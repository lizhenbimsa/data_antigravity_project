"""news_process.pipeline.sentiment.numerical_intensity — v3.5.1 A3 真双轨数字密度.

锚定文献:
    - Hales, Kuang & Venkataraman (2011) CAR 28(1): 305-339
      "Who Believes the Hype? An Experimental Examination of How Language Affects
       Investor Judgments" — numerical intensity Eq.(1):
       n_numeric_tokens / total_sentences
    - Davis & Tama-Sweet (2012) CAR 29(3): 804-837 (补强)

设计要点 (per stage3_v3_5_1 plan v0.3 §2.2):
    1. 真双轨 (修 R3-C2): `enrich_with_num_intensity_dual_track` 对 content_full
       和 content_ctx **各独立调用** compute_num_intensity 一次; 与项目现有
       _dual_analyze 三轨契约一致.
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

中文 sentence 分母与英文 Hales 2011 不直接可比 disclosure (paper §3.4, 修 R7-M1):
   中文新闻句号使用比英文 sparse (长句 + 逗号), num_intensity 分母系统性偏低.
   同时报 word-level 替代版 (paper §4.3).
"""
from __future__ import annotations

import logging
import re
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# v3.5.1 A3 公式锁定 (frozen at D0):
# 句子分割正则 (lookahead/behind 排除小数点, 修 M1')
_SENTENCE_END_RE = re.compile(r'(?<!\d)[。！？.!?](?!\d)')

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
        arab = _cn_number_to_arabic(cn_num)
        if arab is None:
            return match.group(0)
        return f"{arab}%"

    text = _PERCENT_PREFIX_RE.sub(_percent_replace, text)

    # 2. 处理一般中文数字块
    def _replace_block(match: re.Match) -> str:
        cn_str = match.group(0)
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
    """对**单一文本**计算 numerical intensity (Hales 2011 CAR Eq.1).

    Args:
        content: 任意单一文本 (典型为 content_full 或 content_ctx).

    Returns:
        float: n_numeric / n_sentences; 空/单字符文本 → float('nan').
    """
    if not isinstance(content, str) or not content.strip():
        return float('nan')

    # cn2arab 后计数
    text_arabic = _cn2arab(content)
    n_num, n_sent = _count_numerical_tokens(text_arabic)
    return round(n_num / max(n_sent, 1), 6)


def enrich_with_num_intensity_dual_track(df: pd.DataFrame,
                                         full_col: str = '内容',
                                         ctx_col: str = 'content_ctx') -> pd.DataFrame:
    """真双轨 post-processor: 对 content_full + content_ctx 各调用一次 compute_num_intensity.

    与项目现有 _dual_analyze 三轨契约一致 (per plan v0.3 §2.2.3 修 R3-C2 + H4).

    Args:
        df: 含 full_col + ctx_col 列的 DataFrame (典型来自 stage 22 batch 处理后).
        full_col: 全文列名 (默认 '内容').
        ctx_col: 上下文列名 (默认 'content_ctx').

    Returns:
        pd.DataFrame: 加 ``num_intensity_full`` + ``num_intensity_ctx`` 两列.
    """
    if df is None or len(df) == 0:
        return df

    df = df.copy()
    # 防御: 若 ctx_col 缺失, 回退用 full_col
    if ctx_col not in df.columns:
        logger.warning(f"v3.5.1 A3: '{ctx_col}' 缺失, ctx 轨回退用 '{full_col}'")
        df[ctx_col] = df[full_col]

    df['num_intensity_full'] = df[full_col].astype(str).apply(compute_num_intensity)
    df['num_intensity_ctx'] = df[ctx_col].astype(str).apply(compute_num_intensity)

    return df
