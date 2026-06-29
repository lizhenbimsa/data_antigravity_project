"""news_process.pipeline.sentiment.numerical_intensity — v3.5.1 A3 真三轨 (full/ctx/ss) 数字密度.

锚定文献 (2026-06-05 引文勘误; 2026-06-24 Crossref 核验):
    - 数值披露强度构念 (numerical intensity = 数字 token / 篇幅):
      Davis, A. K., & Tama-Sweet, I. (2012). Managers' use of language across
      alternative disclosure outlets: Earnings press releases versus MD&A.
      Contemporary Accounting Research, 29(3), 804-837.
      https://doi.org/10.1111/j.1911-3846.2011.01125.x
    - ⚠ 原注 "Hales, Kuang & Venkataraman (2011) CAR 28(1):305-339 — numerical
      intensity Eq.(1)" 经 web 核对有误: 该文实为 Journal of Accounting Research
      49(1):223-255, 主题是 vivid/pallid 语言对投资者判断的影响, 并未定义 numerical
      intensity。故数字密度构念不归该文; 本实现公式 n_numeric_tokens / total_sentences
      为项目自定义操作化, 精确公式锚点待最终确认。

设计要点 (per stage3_v3_5_1 plan v0.3 §2.2):
    1. 真三轨 (修 R3-C2; v3.9.0 +ss): `enrich_with_num_intensity_dual_track` 对
       content_full / content_ctx / content_ss **各独立调用** compute_num_intensity
       一次; 与项目现有 _dual_analyze 三轨契约 (full + ctx + ss) 一致.
       (`compute_num_intensity` / `compute_num_intensity_word` 本身 track-agnostic,
       第三轨 ss = 同句共现轨 = content_ss; 缺列优雅跳过, 镜像 ctx 守卫.)
    2. cn2arab 5 标准样例锁定 (修 H1, frozen at D0):
        - "两千万" → "20000000" (1 token)
        - "三亿五千万" → "350000000" (1 token, 不拆 3 + 5)
        - "1.5 亿" → "150000000" (1 token)
        - "百分之三十" → "30%" (1 token)
        - "30 万亿元" → "30000000000000元" (1 token)
        - 不定数 ("几千" / "数十亿" / "上百万") **不计为 token** (保守, 修 R7-M2)
    3. 句子切分用 lookahead/behind 排除小数点 (修 M1'):
       (?<! digit) [。！？.!?] (?! digit) ; 不计分号 (与 LM 2011 JF 一致).
    4. 空文本 / 单字符 → pd.NA (修 R8-M1).
    5. ctx 残半句已被 entity_context 完整句号过滤 (修 R3-H3).
    6. **decision (D-1.4)**: 不引入 PyPI cn2an 包; 自实现 ~50 行保守版本以避免
       requirements.lock 增量.

中文 sentence 分母与英文不直接可比 disclosure (paper §3.4, 修 R7-M1):
   中文新闻句号使用比英文 sparse (长句 + 逗号), num_intensity 分母系统性偏低.
   word-level 替代版 (n_numeric / jieba 词数) 已实现 — compute_num_intensity_word,
   产出 num_intensity_word_{full,ctx,ss} (2026-06-05; v3.9.0 +ss, 兑现 paper §4.3 承诺;
   对"归一化分母选择"互为稳健性).
"""
from __future__ import annotations

import logging
import re
import time
from typing import Optional

import jieba
import pandas as pd

# 日志富集 (2026-06-24): 非整数数字一律 4 位有效数字 (项目规范单一事实源)。
# 仅服务 logger.* 输出, 不参与任何产物计算 (golden-safe)。
from news_process.core.logging import pct4, sig4

# fix(omni-g-numlex word-denominator, 2026-06-11): 复用 lm_non_sentiment 的
# word-token 过滤正则 (单一事实源), 让 _count_word_tokens 与 lmfls-01 修复后的
# frac_* / clarity / pos_ratio 分母同口径 (排除纯标点/纯数字 token)。
from news_process.pipeline.sentiment.lm_non_sentiment import _LMFLS_NONWORD_RE

logger = logging.getLogger(__name__)

# v3.5.1 A3 公式锁定 (frozen at D0):
# 句子分割正则 (lookahead/behind 排除小数点, 修 M1')
# fix(omni-g-numlex-02, 2026-06-11): digit-guard 仅限半角句点 '.' (小数点保护本意) —
# 旧正则把 (?<!\d)/(?!\d) 一并套在全角 。！？ 上, 而全角句号永远不是小数点, 致句尾
# 数字 ("…达120。") / 句首数字 ("。2017年…", 新闻极常见) 的真句界被丢弃 (实测全语料
# 丢 6.4% 全角句末符, 63.6% 文章受影响), 且 cn2arab 转换会新造 digit-相邻句号放大漏计
# → 分母偏小且与分子正相关 → num_intensity 系统性上偏。全角 。！？ 与半角 !? 不再守卫。
_SENTENCE_END_RE = re.compile(r'[。！？!?]|(?<!\d)\.(?!\d)')

# 数字 token 正则
_DIGIT_TOKEN_RE = re.compile(r'\d+(?:\.\d+)?[%％]?')

# 中文数字基本映射
_CN_DIGIT_MAP = {
    '零': 0, '一': 1, '二': 2, '两': 2, '三': 3, '四': 4,
    '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
}
_CN_UNIT_MAP = {'十': 10, '百': 100, '千': 1000, '万': 10000, '亿': 100000000}

# 不定数: 保守策略**不计**为数字 token (修 R7-M2)
_CN_INDEFINITE_QUANTIFIERS = frozenset({'几', '数', '若干', '些', '多', '余'})

# 连续中文数字 / 量词块的正则; 后续逐块 cn2arab
_CN_NUMBER_BLOCK_RE = re.compile(
    r'(?:百分之)?[零一二两三四五六七八九十百千万亿]+'
)

# 百分之 prefix
_PERCENT_PREFIX_RE = re.compile(r'百分之([零一二两三四五六七八九十百千万亿]+)')

# fix(omni-g-numlex-01/-08, 2026-06-11): 单字中文数字块的数量语境门控。
# 旧行为对任意上下文单字数字无条件 cn2arab → 实测 (盘上 1170 篇 content_full)
# 42.3% 分子来自该类转换 (单字 '一' 即 25.1%), 94.5% 文章受影响, 压倒性为功能词/
# 固定搭配 (进一步/一起/统一/之一/一系列/一带一路/一方面 等), 系统性污染构念。
# 修复: 单字块仅在数量语境计入 —
#   (a) 后接量词/单位白名单 _SINGLE_CN_UNIT_AFTER (一笔/五家/三人/十年), 或
#   (b) 前置数量修饰守卫 _SINGLE_CN_QUANT_BEFORE (约三/达九/共五);
# 且前字命中功能词黑名单 _SINGLE_CN_PREV_BLACKLIST 时**强制不计** (黑名单优先于
# 白名单, 防 '统一个人账户'/'这一年'/'同一家' 类 '一'+白名单字的边缘误计)。
# 黑名单构成: 之/统/进 = 组级裁决点名 (之一/统一/进一步); 这/同/唯 = 指示/同一性
# 前缀 (这一×222 是审计实测 top 噪声源, 同一/唯一 同构非定量)。
# 白话: "进一步""统一""之一"里的"一"根本不是数字, 老版本却把它们都数成
# 数字 token, 数字密度被大幅灌水。现在的规则是: 孤零零的一个中文数字,
# 只有当它看起来真在"数东西"时才算数 —— 比如后面跟着量词 (五"家"银行、
# 一"笔"贷款), 或前面有"约/达/共"这类修饰; 而前面是"之/统/进"等字时
# 一票否决, 绝不算数。
_SINGLE_CN_UNIT_AFTER = frozenset(
    '个家只笔元名人项次倍户张件款单期批轮宗股份成年月日天周季亩吨克米'
)
_SINGLE_CN_QUANT_BEFORE = frozenset('约近逾超达共仅')
_SINGLE_CN_PREV_BLACKLIST = frozenset('之统进这同唯')

# fix(omni-g-numlex-01/-08, 2026-06-11): 政治专名守卫 — '十九大' (党代会序数) 不是
# 定量披露, 块后紧跟 '大' 且块命中党代会序数集时不转 ('十九大'→'19大' 是实测误转;
# '十三五' 类规划名由 _cn_number_to_arabic 的相邻纯数字 malformed 守卫覆盖)。
_PARTY_CONGRESS_BLOCKS = frozenset({'十六', '十七', '十八', '十九', '二十', '二十一'})

# fix(omni-g-numlex-07, 2026-06-11): 后缀不定数字符 — 块后紧跟 多/余/来/几 时整体为
# 不定数 ('三十多万'/'二十余家'/'十来个'/'百分之三十几'), 按 R7-M2 既定策略不计。
# 旧实现的不定数守卫仅对块内字符生效, 后缀形式中不定字符在块外 → 守卫被旁路。
_INDEFINITE_SUFFIX_CHARS = frozenset('多余来几')


def _cn_number_to_arabic(cn_str: str) -> Optional[int]:
    """单一连续中文数字串 → 整数 (~50 行 自实现, 不依赖 cn2an).

    支持: "两千" / "三亿五千万" / "百分之三十" prefix.
    不支持: 不定数 ("几千" / "数十亿") → 返回 None.
    不支持: 纯单位组合 ("万亿" / "万" 单独) → 返回 None (避免误转 "万亿" 为 100010000).

    Args:
        cn_str: 仅含中文数字字符的字符串.

    Returns:
        int 或 None (若含不定数 / 解析失败 / 纯单位).
    """
    if not cn_str:
        return None
    # 不定数排除 (修 R7-M2)
    if any(c in _CN_INDEFINITE_QUANTIFIERS for c in cn_str):
        return None
    # 纯单位组合排除 (修 v3.5.1 实测 bug): "万亿" / "万" / "亿" 单独不是数字
    # 必须至少含一个 pure digit 字符 (零一二两三四五六七八九).
    _pure_digits = frozenset({'零', '一', '二', '两', '三', '四', '五', '六', '七', '八', '九'})
    if not any(c in _pure_digits for c in cn_str):
        return None

    # fix(omni-g-numlex-01/-08, 2026-06-11): malformed 数词守卫 ×2 —
    # (a) 相邻两个非零纯数字字符 = 非规范数词 (规范中文数词数字间必有单位:
    #     三十五/三百五十; '零' 是合法占位符如 '一百零五' 故豁免)。命中者为专名/
    #     枚举 ('十三五' 旧实现还错算成 15, '一二三'), 一律不转。
    # (b) 前导单位字 (百/千/万/亿) = 非规范数词开头 ('万一' 旧实现误算 10001;
    #     规范数词不以这些单位起头, '十三' 类 '十' 起头合法故豁免)。
    _nonzero_digits = frozenset({'一', '二', '两', '三', '四', '五', '六', '七', '八', '九'})
    for _a, _b in zip(cn_str, cn_str[1:]):
        if _a in _nonzero_digits and _b in _nonzero_digits:
            return None
    if cn_str[0] in ('百', '千', '万', '亿'):
        return None

    # P-042 修复 (v3.7.1): "万亿" 复合单位 = 10^12 (万 × 亿). 旧实现把它当
    # 两个独立单位累加 (total = X*1e4 + 1*1e8), 对 "两万亿" 给出 100020000
    # 而非真值 2*10^12 (差 20000×). 预处理: "X万亿" → "X·10^12 + 后缀".
    if '万亿' in cn_str:
        idx = cn_str.index('万亿')
        prefix_str = cn_str[:idx]
        suffix_str = cn_str[idx + 2:]
        prefix_val = _cn_number_to_arabic(prefix_str) if prefix_str else 1
        if prefix_val is None:
            prefix_val = 1
        suffix_val = _cn_number_to_arabic(suffix_str) if suffix_str else 0
        if suffix_val is None:
            suffix_val = 0
        return prefix_val * 10**12 + suffix_val

    total = 0
    section = 0  # 当前 section (累计 < 万)
    number = 0   # 当前数字 (累计 < 十)

    for ch in cn_str:
        if ch in _CN_DIGIT_MAP and ch not in ('十', '百', '千', '万', '亿'):
            number = _CN_DIGIT_MAP[ch]
        elif ch == '十':
            # "十" 单独出现时表示 10; 否则作 unit
            section += (number or 1) * 10
            number = 0
        elif ch in _CN_UNIT_MAP:
            unit = _CN_UNIT_MAP[ch]
            if unit >= 10000:
                # 万 / 亿: flush section 到 total
                section += number
                total += (section or 1) * unit
                section = 0
                number = 0
            else:  # 百 / 千
                section += (number or 1) * unit
                number = 0
        else:
            # 未知字符, 跳过
            continue

    section += number
    total += section
    return total if total > 0 else None


def _cn2arab(text: str) -> str:
    """中文数字 → 阿拉伯字符串 (~50 行 自实现).

    锁定 5 标准样例 (frozen at D0, 修 H1):
        - "两千万" → "20000000"
        - "三亿五千万" → "350000000"
        - "1.5 亿" → 1.5×100000000 = 150000000 (注: 阿拉伯数字 + 单位字符)
        - "百分之三十" → "30%"
        - "30 万亿元" → "30000000000000元"
    不定数 ("几千" / "数十亿" / "上百万") 保留原文不转 → 不计为数字 token.

    Args:
        text: 任意中文文本.

    Returns:
        str: 中文数字字符串被替换为阿拉伯数字; 其他字符不变.
    """
    if not isinstance(text, str) or not text.strip():
        return text

    # 1. 处理 "百分之 X" → "X%"
    def _percent_replace(match: re.Match) -> str:
        cn_num = match.group(1)
        # fix(omni-g-numlex-07, 2026-06-11): '百分之三十几' 类后缀不定数整体不计
        # (旧实现转出 '30%几' 计 1 token, 旁路 R7-M2 不定数策略)。
        end = match.end()
        if end < len(match.string) and match.string[end] in _INDEFINITE_SUFFIX_CHARS:
            return match.group(0)
        arab = _cn_number_to_arabic(cn_num)
        if arab is None:
            return match.group(0)
        return f"{arab}%"

    text = _PERCENT_PREFIX_RE.sub(_percent_replace, text)

    # 2. 处理一般中文数字块
    def _replace_block(match: re.Match) -> str:
        cn_str = match.group(0)
        start, end = match.start(), match.end()
        s = match.string
        prev_ch = s[start - 1] if start > 0 else ''
        next_ch = s[end] if end < len(s) else ''
        # fix(numintensity-02): 序数词 "第N" 不是定量信息 (如 "第三季度"/"第十八届"),
        # 不转阿拉伯数字, 避免产生假定量 token 污染 num_intensity 计数。
        if prev_ch == '第':
            return cn_str
        # fix(omni-g-numlex-07, 2026-06-11): 后缀不定数 ('三十多万'/'二十余家'/'十来个')
        # — 不定字符 多/余/来/几 在块外, 旧块内守卫被旁路; 按 R7-M2 整体不计。
        if next_ch in _INDEFINITE_SUFFIX_CHARS:
            return cn_str
        # fix(omni-g-numlex-01/-08, 2026-06-11): 党代会专名 ('十九大'→曾误转 '19大')。
        if next_ch == '大' and cn_str in _PARTY_CONGRESS_BLOCKS:
            return cn_str
        # fix(omni-g-numlex-01/-08, 2026-06-11): 单字块数量语境门控 (见常量注释) —
        # 功能词黑名单优先; 否则须 后接量词/单位白名单 或 前置数量修饰守卫。
        if len(cn_str) == 1:
            if prev_ch in _SINGLE_CN_PREV_BLACKLIST:
                return cn_str
            if (next_ch not in _SINGLE_CN_UNIT_AFTER
                    and prev_ch not in _SINGLE_CN_QUANT_BEFORE):
                return cn_str
        arab = _cn_number_to_arabic(cn_str)
        if arab is None:
            return cn_str
        return str(arab)

    text = _CN_NUMBER_BLOCK_RE.sub(_replace_block, text)

    # 3. 处理 "1.5 亿" / "30 万亿" 类阿拉伯数字 + 中文单位
    # 后处理: 阿拉伯小数 + 万亿 / 亿 / 万 单位
    def _arab_with_unit(match: re.Match) -> str:
        num_str, unit = match.group(1), match.group(2)
        try:
            num = float(num_str)
            unit_val = {'万亿': 1e12, '亿': 1e8, '万': 1e4}[unit]
            result = int(num * unit_val) if (num * unit_val).is_integer() else num * unit_val
            return f"{result}{'元' if False else ''}"  # 单位被吃掉,数字纳入
        except (ValueError, KeyError):
            return match.group(0)

    text = re.sub(r'(\d+(?:\.\d+)?)\s*(万亿|亿|万)(?!元)?', _arab_with_unit, text)

    return text


def _count_numerical_tokens(text: str) -> tuple[int, int]:
    """返回 (n_numeric_tokens, n_sentences).

    Args:
        text: 已经 cn2arab 转换后的文本.

    Returns:
        tuple: (数字 token 数, 句子数; 至少为 1 以避免分母 0).
    """
    if not isinstance(text, str) or not text.strip():
        return (0, 1)

    # n_numeric = 阿拉伯数字 token 数 (含可选小数 + 百分号 + 万/亿单位字符)
    n_numeric = len(_DIGIT_TOKEN_RE.findall(text))

    # n_sentences = 句号 / 问号 / 感叹号; lookahead/behind 排除小数点 (修 M1')
    n_sentences = len(_SENTENCE_END_RE.findall(text))
    if n_sentences == 0:
        n_sentences = 1  # 整段文本视为 1 句

    return (n_numeric, n_sentences)


def compute_num_intensity(content: str) -> float:
    """对**单一文本**计算 numerical intensity (数值披露强度; 公式 n_numeric/n_sentences
    为项目自定义操作化, 构念锚 Davis & Tama-Sweet 2012 CAR, 见模块 docstring 引文勘误).

    Args:
        content: 任意单一文本 (典型为 content_full 或 content_ctx).

    Returns:
        float: n_numeric / n_sentences; 空/单字符文本 → float('nan').

    R1-R5 audit fix A7 (2026-05-27):
        修 silent NaN→0 propagation. 下游 enrich_with_num_intensity_dual_track (三轨,
        full/ctx/ss) 用 ``df[col].astype(str).apply(...)`` 调用时, pandas 把 ``NaN/None`` 转成
        字符串 ``'nan'`` / ``'None'`` / ``'<NA>'`` (长度 ≥ 3, 通过 isinstance(str)
        与 strip 检查), 返回 0.0 而非 NaN, 让 panel mean_num_intensity_* 系统性
        偏低 (R4-A8 实测). 本 fix 在 isinstance check 后**显式拦截字符串化 NaN
        哨兵值**, 返回 float('nan') 保证 NaN propagate 到 panel 聚合层.

        cn2arab 误转修复史 (fix(omni-g-numlex-01/-08, 2026-06-11) 改写本段披露):
        旧版此处声称误转仅 "影响 5-15 article/1170 ≈ 1%" 且 deferred 到 v3.7.5 —
        该量化经 2026-06-11 omni 审计证实**失真约两个数量级**: 盘上 1170 篇实测
        42.3% 分子 token 来自 cn2arab 转换 (单字 '一' 即占分子 25.1%), 94.5% 文章
        受影响, 压倒性为功能词/固定搭配 (进一步/之一/统一/一系列/一带一路 等) 与
        政治专名 ('十九大'→'19大'/'十三五'→错值 15/'万一'→错值 10001)。已修复:
        序数 '第N' 守卫 (numintensity-02) + 单字块数量语境门控 + 党代会/规划名
        专名守卫 + malformed 数词守卫 + 后缀不定数守卫 (g-numlex-07), 见 _cn2arab
        与 _replace_block 内 fix 注释。修后单字数字仅在数量语境 (后接量词/单位
        白名单或前置数量修饰) 计入。
    """
    if not isinstance(content, str) or not content.strip():
        return float('nan')

    # 拦截 pandas astype(str) 产生的字符串化 NaN 哨兵值 (R1-R5 audit fix A7)
    # NB: 这些是字符串字面值, isinstance(str) 与 strip() 都过, 必须显式检测.
    if content.strip() in ('nan', 'NaN', 'None', '<NA>', 'NaT'):
        return float('nan')

    # cn2arab 后计数
    text_arabic = _cn2arab(content)
    n_num, n_sent = _count_numerical_tokens(text_arabic)
    return round(n_num / max(n_sent, 1), 6)


def _count_word_tokens(content: str) -> int:
    """返回 jieba 分词后 word-token 数 (= 文章词级长度; 排除纯标点/纯数字 token).

    fix(omni-g-numlex word-denominator, 2026-06-11): 加 ``_LMFLS_NONWORD_RE``
    同口径过滤。旧实现仅剔空白、含标点/纯数字 token (盘上实测占 ~19%, 逐篇
    13%-26% 非常数), 而 lm_non_sentiment (lmfls-01) / tone_words clarity 与
    pos_ratio (omni-g-tonewords-01) 的分母均已是 word-token 口径 — 旧 docstring
    声称的 "与 frac_uncert / clarity 可横向比较" 已失真。修后三处分母重新同构。

    口径披露: 分母排除纯数字 token 而 num_intensity_word 分子计数字 token →
    数字极密文本理论上比值可 > 1 (非 [0,1] 比率, codebook/论文须写明)。
    """
    if not isinstance(content, str) or not content.strip():
        return 0
    return sum(
        1 for t in jieba.cut(content)
        if t.strip() and not _LMFLS_NONWORD_RE.fullmatch(t.strip())
    )


def compute_num_intensity_word(content: str) -> float:
    """word-level 数字密度: n_numeric / n_words (兑现本模块 §4.3 承诺).

    动机: 主测度 ``compute_num_intensity`` 以**句子数**为分母 (句级口径), 但中文新闻
    句号比英文 sparse (长句 + 逗号), 句级分母系统性偏低、放大数字密度 (见模块 docstring
    §3.4)。本 word-level 版改以 **jieba 词数**为分母, 规避中英文句读差异, 作为对
    "归一化分母选择"互为稳健性的替代版 (句级 vs 词级两种分母口径纪律: 不以相关性取舍,
    两种口径各自进回归)。

    与句级版**共享分子** n_numeric (同一 _cn2arab + _DIGIT_TOKEN_RE 计数), 仅分母不同
    → 误差同源、不引入新偏差。已知 cn2arab 修饰词误转 (序数/不定数, 见 compute_num_intensity
    docstring) 同等影响两版分子, 不构成 word 版独有缺陷。

    Args:
        content: 任意单一文本 (典型为 content_full 或 content_ctx)。

    Returns:
        float: n_numeric / max(n_words, 1); 空/单字符/字符串化 NaN 哨兵 → float('nan')。
    """
    if not isinstance(content, str) or not content.strip():
        return float('nan')
    # 拦截 pandas astype(str) 产生的字符串化 NaN 哨兵 (与 compute_num_intensity 同款保护,
    # 防 'nan'/'<NA>' 被当正常文本算出 0.0 污染 panel 聚合)
    if content.strip() in ('nan', 'NaN', 'None', '<NA>', 'NaT'):
        return float('nan')

    # 分子: cn2arab 后阿拉伯数字 token 数 (与句级版同源; 注: 此处独立再算一次 cn2arab,
    # 17M 全量下若成吞吐瓶颈可与句级版合并为单 pass, 当前保持独立函数以便单测)
    text_arabic = _cn2arab(content)
    n_num, _ = _count_numerical_tokens(text_arabic)
    # 分母: 原文 jieba 词数 (词级文章长度)
    n_words = _count_word_tokens(content)
    return round(n_num / max(n_words, 1), 6)


def _num_intensity_both(content: str) -> tuple[float, float]:
    """共享一次 _cn2arab pass 计算 (句级, 词级) num_intensity, 逐位等价于分别调用
    compute_num_intensity / compute_num_intensity_word (perf(accel-numint-01) —
    消去同文本对 _cn2arab 的重复转换)。两个独立公开函数保留供单测, 语义不变。
    """
    if not isinstance(content, str) or not content.strip():
        return (float('nan'), float('nan'))
    if content.strip() in ('nan', 'NaN', 'None', '<NA>', 'NaT'):
        return (float('nan'), float('nan'))
    text_arabic = _cn2arab(content)           # 单次转换, 句级/词级共享分子 n_num
    n_num, n_sent = _count_numerical_tokens(text_arabic)
    sent_intensity = round(n_num / max(n_sent, 1), 6)
    n_words = _count_word_tokens(content)
    word_intensity = round(n_num / max(n_words, 1), 6)
    return (sent_intensity, word_intensity)


def enrich_with_num_intensity_dual_track(df: pd.DataFrame,
                                         full_col: str = 'content_full',
                                         ctx_col: str = 'content_ctx',
                                         ss_col: str = 'content_ss') -> pd.DataFrame:
    """真三轨 post-processor: 对 content_full / content_ctx / content_ss 各调用一次 compute_num_intensity.

    与项目现有 _dual_analyze 三轨契约 (full + ctx + ss) 一致 (per plan v0.3 §2.2.3 修 R3-C2 + H4;
    v3.9.0 加 ss = 银行+金科同句共现轨).

    Args:
        df: 含 full_col + ctx_col (+ 可选 ss_col) 列的 DataFrame (典型来自 stage 22 batch 处理后).
        full_col: 全文列名 (默认 'content_full'; 含标题, 与 ctx 对称; 缺列回退裸 '内容').
        ctx_col: 上下文列名 (默认 'content_ctx').
        ss_col: 同句共现列名 (默认 'content_ss', stage 13 物化; 缺列优雅跳过 ss 轨, 镜像 ctx 守卫).

    Returns:
        pd.DataFrame: 加 ``num_intensity_{full,ctx}`` (句级口径) +
        ``num_intensity_word_{full,ctx}`` (词级替代版, §4.3); 若 ss_col 在列, 再加
        ``num_intensity_ss`` + ``num_intensity_word_ss`` (共 4 或 6 列)。
    """
    if df is None or len(df) == 0:
        return df

    # ── 子步骤 banner (called-by-runner helper; 复用上游 stage22 日志句柄, 不打 ENV/CONFIG 块) ──
    # 富集铁律: 仅 logger.* + 纯日志局部变量, 不改任何写盘值/schema/控制流 (golden-safe)。
    _t0 = time.time()
    try:
        logger.info("─" * 64)
        logger.info("【数字密度子步骤】numerical intensity 三轨富集 (full / ctx / ss)")
        logger.info("  · 功能: 数值披露强度 = 数字 token / 归一化分母 (句级 + 词级两口径)")
        logger.info(f"  · 输入: {len(df):,d} 行 article-level DataFrame; 模块 = "
                    "pipeline.sentiment.numerical_intensity (called-by-runner helper, 纯 CPU/$0)")
        # 方法论依据 (参考文献信息): 数值披露强度构念锚。
        # ✓ 构念锚 Davis & Tama-Sweet (2012) CAR 29(3):804-837 已经 Crossref 核验 (2026-06-24),
        #   DOI=10.1111/j.1911-3846.2011.01125.x; 故现 emit 完整核验引文含 DOI (在经核验注册表内)。
        #   模块 docstring 仍记录早期 Hales-Kuang-Venkataraman 引文勘误 + 精确公式锚待最终确认。
        logger.info("  · 方法论: 数值披露强度 (numerical disclosure intensity) 构念出处 "
                    "Davis, A. K., & Tama-Sweet, I. (2012). Managers' use of language across "
                    "alternative disclosure outlets: Earnings press releases versus MD&A. "
                    "Contemporary Accounting Research, 29(3), 804-837. "
                    "https://doi.org/10.1111/j.1911-3846.2011.01125.x "
                    "(构念锚, 已 Crossref 核验); 本实现公式 n_numeric / n_sentences "
                    "(句级) 与 n_numeric / jieba 词数 (词级) 为项目自定义操作化, 互为分母稳健性。")
        logger.info("  · 白话: 一篇报道里出现多少『具体数字』(经中文数字→阿拉伯转换 + 不定数/序数/"
                    "功能词守卫), 除以句子数或词数得到数字密度; 数字越密通常硬信息含量越高。")
        # ── 📖 方法论依据 (Crossref 三道核验注册表内文献; 仅 logger.* 输出, golden-safe) ──
        # 构念锚 Davis & Tama-Sweet (2012) 已在上方 banner emit; 下列为"数字占文本比例 →
        # 信息风险/信息含量"操作化与因果验证的近期顶刊文献, 锚定本模块 num_intensity 测度。
        logger.info("  · 📖 方法论依据 (本模块 num_intensity = 数字 token / 归一化分母, 测度文献锚):")
        logger.info("     [1] Campbell, J. L., Zheng, X., & Zhou, D. (2025). Number of numbers: "
                    "Does a greater proportion of quantitative textual disclosure reduce information "
                    "risk? Journal of Corporate Finance, 94, 102813. "
                    "https://doi.org/10.1016/j.jcorpfin.2025.102813")
        logger.info("         (白话: 把『数字占文本的比例』直接作信息量度量并做因果检验, "
                    "正是本模块 num_intensity 的近期顶刊操作化母本。)")
        logger.info("     [2] Gietzmann, M., Grossetti, F., & Lewis, C. M. (2026). Investor "
                    "distraction and multi-dimensional financial narrative. Review of Accounting "
                    "Studies, 31(1), 334-373. https://doi.org/10.1007/s11142-026-09950-7")
        logger.info("         (白话: 把数字密度/可读性/套话当成多维叙事特征联合度量并关联投资者注意力, "
                    "支撑数字密度作为独立叙事维度入面板。)")
        logger.info("     [3] Zhu, X., Li, J., & Wang, Y. (2024). Are risk disclosures in financial "
                    "reports informative? A text mining-based perspective. Humanities and Social "
                    "Sciences Communications, 11(1), 1653. https://doi.org/10.1057/s41599-024-04169-w")
        logger.info("         (白话: 用文本挖掘评披露的具体性/信息含量, 与本模块『数字越多越具体硬信息越足』"
                    "同一测度逻辑。)")
        logger.info("     [4] Taraj, I., & Wahlström, R. R. (2026). Narratives contextualizing numeric "
                    "disclosures: Insights from earnings calls. Journal of Business Finance & Accounting, "
                    "53(3), 1263-1286. https://doi.org/10.1111/jbfa.70056")
        logger.info("         (白话: 数字披露须与叙事窗口联动解读 — 数字密度必须放进句/段粒度的语境里看, "
                    "正是本模块 full/ctx/ss 三轨 (全文 / 银行邻近句 / 银行∧金科同句) 设计的理论依据。)")
        logger.info("     [5] Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained "
                    "financial sentiment analysis with large language models. Neural Computing and "
                    "Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6")
        logger.info("         (白话: 中文金融文本细粒度处理的近期实证 — 作为本模块在中文金融语料上做词级 "
                    "(jieba) 与句级多粒度数字密度测度的领域旁证 (domain-adjacent), 而非分词算法本身的依据。)")
    except Exception as _e_banner:  # 日志块绝不许崩阶段
        logger.warning(f"num_intensity 子步骤 banner 渲染失败 (已跳过, 不影响产物): {_e_banner}")

    df = df.copy()
    # 防御: full_col 缺失 (旧 schema 未物化 content_full) 时回退裸 '内容'。
    # dual-track 一致性修 (2026-06-08): 默认 full_col 已由历史地雷 '内容'(裸正文无标题)
    # 改为 'content_full'(含标题), 与 ctx_col='content_ctx' 同为含标题轨 → 任何用默认调用
    # 的 caller 不再让 num_intensity_full 成为唯一不含标题的 *_full 指标 (病根A 模式)。
    # 与项目其余 tone_words 站点 'content_full 缺列回退裸内容' 范式一致。
    if full_col not in df.columns:
        _fallback = '内容' if '内容' in df.columns else None
        if _fallback is not None:
            logger.warning(f"num_intensity: '{full_col}' 缺失, full 轨回退用 '{_fallback}'")
            full_col = _fallback
    # 防御: 若 ctx_col 缺失, 回退用 full_col
    if ctx_col not in df.columns:
        logger.warning(f"v3.5.1 A3: '{ctx_col}' 缺失, ctx 轨回退用 '{full_col}'")
        df[ctx_col] = df[full_col]

    # perf(accel-numint-01): 每轨共享一次 _cn2arab pass — 原对每轨分别 apply
    # compute_num_intensity 与 compute_num_intensity_word, 各算一遍 _cn2arab (同文本
    # 重复转换); 改 _num_intensity_both 单 pass 返回 (句级, 词级), 逐位等价。
    _both_full = [_num_intensity_both(c) for c in df[full_col].astype(str)]
    _both_ctx = [_num_intensity_both(c) for c in df[ctx_col].astype(str)]
    # 句级 (主测度): n_numeric / n_sentences
    df['num_intensity_full'] = [t[0] for t in _both_full]
    df['num_intensity_ctx'] = [t[0] for t in _both_ctx]
    # 词级 (替代版, 兑现 §4.3; 对中文句读 sparse 稳健): n_numeric / jieba 词数
    df['num_intensity_word_full'] = [t[1] for t in _both_full]
    df['num_intensity_word_ctx'] = [t[1] for t in _both_ctx]

    # 第三轨 ss (银行+金科同句共现轨, v3.9.0): content_ss 由 stage 13 物化, 缺列优雅跳过
    # (镜像上方 ctx 守卫范式; 回退=镜像 ctx→全文 body 已由 stage 13 处理, 此处仅按列存在与否门控)。
    if ss_col in df.columns:
        _both_ss = [_num_intensity_both(c) for c in df[ss_col].astype(str)]
        df['num_intensity_ss'] = [t[0] for t in _both_ss]
        df['num_intensity_word_ss'] = [t[1] for t in _both_ss]
    else:
        logger.info(f"num_intensity: '{ss_col}' 缺失, ss 轨 (同句共现) 跳过 (镜像 ctx 守卫优雅降级)")

    # ── 输入/输出列血缘 (io provenance; 仅 logger.* 读 df.columns 成员关系, 无行为改动) ──
    # 富集铁律: 纯 provenance, 不改任何写盘值/schema/控制流 (golden-safe)。
    # 白话: 把"每条轨实际读了哪一列原始文本 + 这一步写出了哪几列数字密度"如实记进日志,
    # 复现/审计时一眼可见 full/ctx 是否触发了回退、ss 轨是否因缺列被跳过。
    try:
        _ss_present = ss_col in df.columns
        _ss_in = ss_col if _ss_present else f"{ss_col}|缺列跳过"
        logger.info(f"  · 输入列血缘 (各轨实读物理文本列): full←{full_col} / "
                    f"ctx←{ctx_col} / ss←{_ss_in}")
        _out_cols = ['num_intensity_full', 'num_intensity_ctx',
                     'num_intensity_word_full', 'num_intensity_word_ctx']
        if _ss_present:
            _out_cols += ['num_intensity_ss', 'num_intensity_word_ss']
        logger.info(f"  · 输出列清单 ({len(_out_cols)} 列, 句级 + 词级两口径): "
                    f"{', '.join(_out_cols)}")
    except Exception as _e_prov:  # 血缘块绝不许崩阶段
        logger.warning(f"num_intensity 输入/输出血缘渲染失败 (已跳过, 不影响产物): {_e_prov}")

    # ── 关键指标解读 (运行结果信息): 对**真实算出的**列逐轨给阈值判读 (sig4/pct4) ──
    # 仅读取已写入的列, 不改任何值; 全块 try/except 保护, 失败仅 warning 不崩阶段。
    try:
        _n = len(df)
        logger.info("  · 结果解读 (数字一律 4 位有效数字):")
        # 句级 + 词级两口径 × (full/ctx[/ss]) 逐列: 非空率 + 均值 + 标准差
        _intensity_cols = [
            ('num_intensity_full', '句级·full'),
            ('num_intensity_ctx', '句级·ctx'),
            ('num_intensity_ss', '句级·ss'),
            ('num_intensity_word_full', '词级·full'),
            ('num_intensity_word_ctx', '词级·ctx'),
            ('num_intensity_word_ss', '词级·ss'),
        ]
        for _col, _label in _intensity_cols:
            if _col not in df.columns:
                continue
            _s = pd.to_numeric(df[_col], errors='coerce')
            _notna = int(_s.notna().sum())
            _rate = (_notna / _n) if _n else 0.0
            # 非空率判读: 空/单字符文本 → NaN 是设计行为, 但全语料 NaN 率应低
            _verdict = ("好" if _rate >= 0.90 else "临界" if _rate >= 0.70 else "偏低(空/单字文本多?)")
            _mean = float(_s.mean()) if _notna else float('nan')
            _std = float(_s.std()) if _notna > 1 else float('nan')
            logger.info(
                f"     - {_label} ({_col}): 非空 {_notna:,d}/{_n:,d} = "
                f"{pct4(_rate)} [{_verdict}]; 均值={sig4(_mean)} 标准差={sig4(_std)}"
            )
            # 分布分位 (result_distribution): num_intensity = 数字 token / 归一化分母 比率,
            # 重度右偏 (多数文章数字稀疏、少数数字极密) → 仅 均值±标准差 会误导; 补 中位数 +
            # 四分位 (p25/p75) + 极值给出右偏全貌。纯读 _s (已 coerce), 值/schema 不变 (golden-safe)。
            if _notna:
                _median = float(_s.median())
                _p25 = float(_s.quantile(0.25))
                _p75 = float(_s.quantile(0.75))
                _vmin = float(_s.min())
                _vmax = float(_s.max())
                logger.info(
                    f"         分布 (右偏稳健画像): 中位数={sig4(_median)} "
                    f"p25={sig4(_p25)} p75={sig4(_p75)} 极值=[{sig4(_vmin)}, {sig4(_vmax)}]"
                )
            # 词级越界自检 (result_distribution): word 版分母排除纯数字 token、分子仍计数字
            # token → 数字极密文本理论上比值可 > 1 (非 [0,1] 比率, 见 _count_word_tokens
            # docstring "口径披露")。此处用真实数据量化这一文档化的 caveat (>1.0 占比),
            # log-only 取证 — 既不裁剪也不改任何值, 只把"理论可越界"落成"实测越界率"。
            if _col.startswith('num_intensity_word') and _notna:
                _gt1 = int((_s > 1.0).sum())
                _gt1_rate = (_gt1 / _notna) if _notna else 0.0
                logger.info(
                    f"         词级 >1.0 越界占比 (非 [0,1] 比率, codebook/论文已披露): "
                    f"{_gt1:,d}/{_notna:,d} = {pct4(_gt1_rate)}"
                )
        # 三轨独立性自检: full vs ctx 句级数字密度相关 (过高 → ctx 窗口未带来增量信号)
        if {'num_intensity_full', 'num_intensity_ctx'}.issubset(df.columns):
            _ff = pd.to_numeric(df['num_intensity_full'], errors='coerce')
            _cc = pd.to_numeric(df['num_intensity_ctx'], errors='coerce')
            _both = _ff.notna() & _cc.notna()
            if int(_both.sum()) >= 3 and _ff[_both].std() > 0 and _cc[_both].std() > 0:
                _corr = float(_ff[_both].corr(_cc[_both]))
                _corr_verdict = (
                    "ctx 近乎复制 full(共线高)" if abs(_corr) >= 0.95
                    else "两轨高度相关" if abs(_corr) >= 0.80
                    else "两轨独立信号成立"
                )
                logger.info(
                    f"     - 三轨独立性: corr(句级 full, ctx) = {sig4(_corr)} "
                    f"[{_corr_verdict}] (n={int(_both.sum()):,d} 双非空)"
                )
        logger.info(f"  · ⏱ 数字密度三轨富集墙钟耗时: {sig4(time.time() - _t0)} 秒")
        logger.info("─" * 64)
    except Exception as _e_result:  # 结果解读块绝不许崩阶段
        logger.warning(f"num_intensity 结果解读块渲染失败 (已跳过, 不影响产物): {_e_result}")

    return df
