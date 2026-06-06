"""news_process.pipeline.sentiment.lexical_complexity — 词汇/句法复杂度 $0 测度族.

2026-06-05 新增 (顶刊文本测度缺口报告批 #2–#6)。一篇文章做**单次** jieba.posseg
词性标注 pass, 派生 6 个互补的"披露质量/可读性"测度, 全部 $0 (jieba 0.42.1 冻结,
无付费 LLM、无新 PyPI 依赖、不触 M0 门、不动 Prompt v8), 真双轨 (_full/_ctx)。

测度与锚点:
  1. rare_word_ratio   低频词率   — You & Zhang (2009) RAS; Gentzkow-Kelly-Taddy
                                     (2019) JEL §2.2 (TF-IDF/词频). 词汇难度维, 补
                                     CPW/TTR 未覆盖的"术语稀有度"。
  2. hard_char_ratio   难字率     — Dale & Chall (1948) familiar-word 思路的中文落地;
                                     丘心颖等 (2016)《经济学(季刊)》15(4):1483-1506.
                                     即英文 Fog "%complex words" 的中文等价 (中文无音节)。
  3. nominalization_ratio 名词化率 — Bonsall-Leone-Miller-Rennekamp (2017) JAE Bog
                                     Index 句法成分之一 (动词憋成抽象名词→官腔/难读)。
  4. function_word_ratio 功能词比率 — LIWC Analytic 维的中文近似 (虚词占比高≈低分析性)。
  5. specificity_index 硬信息密度 — Hope, Hu & Lu (2016) RAS 21(4):1005-1045. 报道
                                     具名实体+数字占比 (reframe: 是"报道"硬信息密度,
                                     非 10-K 自我披露 specificity)。
  6. within_doc_redundancy 文档内冗余 — Dyer-Lang-Stice-Lawrence (2017) JAE; Cazier &
                                     Pfeiffer (2016). 篇内自重复 (与 staleness/herd 的
                                     "跨文章重复"正交: 篇内 vs 篇间)。

诚实限定 (写入论文须披露):
  - jieba.posseg 走 词典+HMM, nr/ns/nt 实体边界与歧义精度低于专用 NER, 属"粗近似/
    上界噪声估计", 措辞应为"以 jieba 词性近似硬信息类别", 勿声称等同 Stanford NER。
  - hard_char 的"常用字集"由 jieba 0.42.1 冻结词典词频派生 (可复现 $0 代理); 官方
    《通用规范汉字表》一级字 3500 可作未来 drop-in 替换 (见 _common_char_set)。
  - within_doc_redundancy 用字符 3-gram 自重复比; 中文新闻篇幅中位 ~800 字、常无段落
    标记, 篇内信号弱于 10-K, 全量下宜另出 bank-year pooled 版互为稳健 (本模块仅篇级)。
  - rare_word 阈值 (RARE_WORD_PERCENTILE=20) 确定性派生, 但低频侧巨量 tie 致实测覆盖约
    57% distinct 词 (非紧致 20% 尾部), 实为"非高频词率"; spec/论文须如实表述。
  - nominalization: f[0]=='n' 亦匹配 nr/ns/nt/nz 专名词性, 故"姓+性/化/度/型/制"型人名
    (如 jieba 把 '赵性' 误标 nr) 会被计入 → 小幅高估, 属上界噪声 (与下方"粗近似"披露一致;
    收紧排除专名会同时漏掉被 jieba 误标 nr 的真名词化如 '安全性', 取舍后选保留 recall)。
"""
from __future__ import annotations

import functools
import re

import jieba
import jieba.posseg as pseg

# ── 常量 (spec 固定) ─────────────────────────────────────────────────────────
# 低频词阈值: jieba 冻结词典正词频分布的第 P 百分位 (确定性、可复现)。
# ⚠ 因低频侧巨量并列 (freq=2 约 4 万词、freq=3 约 16 万词), 第 20 百分位 cutoff 实测=3.0,
# 用 <= 谓词会把 freq<=3 的词全计入 → rare_word_ratio 实际覆盖约 57% distinct 词 (含
# OOV freq=0 升至约 70%), 即度量"非高频词率"而非紧致的最稀有 20% 尾部。论文/spec 须如实
# 表述, 勿声称"低频 20% 阈值" (审核 2026-06-05 P2)。
RARE_WORD_PERCENTILE = 20
# 常用字覆盖率: 累计到该比例的字频质量定义"常用字" (越大常用字集越大、难字率越低)
COMMON_CHAR_COVERAGE = 0.995
# 难字率分母最小 Han 字数 (过短文本难字率不稳, 低于此返回 nan)
_MIN_HAN_CHARS = 5

# 名词化后缀 (动词/形容词 → 抽象名词: 数字化/安全性/合规度/中心型/股份制)
_NOMINAL_SUFFIX = frozenset({'性', '化', '度', '型', '制'})
# 名词化词性: vn(名动词) / an(名形词)
_NOMINAL_FLAGS = frozenset({'vn', 'an'})

# 功能词词性前缀 (LIWC function words 的中文映射): u 助词 / p 介词 / c 连词 / r 代词 /
# y 语气词 / e 叹词. 不含 d 副词 (副词偏内容, 保守排除)。
_FUNCTION_FLAG_PREFIXES = ('u', 'p', 'c', 'r', 'y', 'e')

# 具名实体词性 (硬信息): nr 人名 / ns 地名 / nt 机构 / nz 其他专名
_ENTITY_FLAGS = frozenset({'nr', 'ns', 'nt', 'nz'})

# 逆接/转折连词【独立词表】—— 刻意不复用 config/sentiment.yaml 的 adversative_words
# (那张表驱动情感 boost; 复用会让本 RHS 与情感轨机械同源、污染度量纯度, 见缺口报告 G5)。
# 锚: Ding-Liu-Yu (2008) WSDM; 徐巍-姚振晔-陈冬华 (2021)《会计研究》(3):28-44 (副词连词占比)。
_ADVERSATIVE_WORDS = frozenset({
    '但', '但是', '然而', '却', '可是', '不过', '尽管', '虽然', '虽',
    '反而', '相反', '只是', '反倒', '岂料', '殊不知', '竟然', '不料',
    '尽管如此', '话虽如此', '即便', '即使', '纵然', '哪怕',
})

_PUNCT_FLAG = 'x'  # jieba.posseg 标点/未知词性


@functools.lru_cache(maxsize=1)
def _common_char_set() -> frozenset[str]:
    """从 jieba 0.42.1 冻结词典词频派生"常用字"集 (可复现 $0 代理).

    做法: 遍历 jieba.dt.FREQ 所有词条, 把词频累加到其每个汉字上得到字频; 按字频降序
    累计到 COMMON_CHAR_COVERAGE 比例的汉字即"常用字"。jieba 词典冻结 → 结果确定性。

    未来可替换为官方《通用规范汉字表》一级字 3500 (drop-in, 改本函数返回值即可)。
    """
    jieba.initialize()  # 确保 FREQ 已加载 (惰性; 已加载则 O(1))
    char_freq: dict[str, int] = {}
    for word, freq in jieba.dt.FREQ.items():
        if not freq:
            continue
        for ch in word:
            if '一' <= ch <= '鿿':  # CJK 统一表意文字
                char_freq[ch] = char_freq.get(ch, 0) + freq
    if not char_freq:
        return frozenset()
    total = sum(char_freq.values())
    common: set[str] = set()
    cum = 0
    for ch, f in sorted(char_freq.items(), key=lambda kv: kv[1], reverse=True):
        common.add(ch)
        cum += f
        if cum / total >= COMMON_CHAR_COVERAGE:
            break
    return frozenset(common)


@functools.lru_cache(maxsize=1)
def _rare_word_cutoff() -> float:
    """低频词频率阈值 = jieba 冻结词典正词频的第 RARE_WORD_PERCENTILE 百分位.

    词 w 视为"低频/难词" iff jieba.dt.FREQ.get(w, 0) <= cutoff (OOV freq=0 → 低频)。
    ⚠ 见上方 RARE_WORD_PERCENTILE 注释: 低频侧巨量 tie 使实测 cutoff=3.0、覆盖约 57%
    distinct 词; 该指标实为"非高频词率", 论文表述勿声称紧致 20% 尾部 (审核 2026-06-05 P2)。
    """
    jieba.initialize()
    freqs = sorted(f for f in jieba.dt.FREQ.values() if f and f > 0)
    if not freqs:
        return 0.0
    idx = max(0, min(len(freqs) - 1, int(len(freqs) * RARE_WORD_PERCENTILE / 100)))
    return float(freqs[idx])


def _safe_div(num: float, den: float) -> float:
    """分母 > 0 时返回比值 (round 6), 否则 nan (避免 0 分母伪 0)。"""
    return round(num / den, 6) if den > 0 else float('nan')


def _empty_result() -> dict[str, float]:
    """空/无效文本的统一返回 (所有键 → nan, 保证跨行 dict 结构一致)。"""
    return {
        'rare_word_ratio': float('nan'),
        'hard_char_ratio': float('nan'),
        'nominalization_ratio': float('nan'),
        'function_word_ratio': float('nan'),
        'specificity_index': float('nan'),
        'within_doc_redundancy': float('nan'),
        'adversative_ratio': float('nan'),
        'n_words_real': float('nan'),
    }


# 模块导出的指标键 (供 tone_words new_metric_cols 登记 + encode 聚合引用)
LEXICAL_COMPLEXITY_KEYS = (
    'rare_word_ratio', 'hard_char_ratio', 'nominalization_ratio',
    'function_word_ratio', 'specificity_index', 'within_doc_redundancy',
    'adversative_ratio',
)

# 词级文章长度原始计数 (非比率): mean 聚合后由 geography 做 ln 变换得 ln_word_count
# (Li 2008 JAE 真 MLENGTH 词口径, 补 avg_article_length 的字符口径; 批 #7)。
WORD_COUNT_KEY = 'n_words_real'


def _char_trigram_redundancy(content: str) -> float:
    """篇内冗余 = 1 − (唯一字符3-gram数 / 全部字符3-gram数)。

    越高 = 重复 3-gram 越多 = 越啰嗦/套话/复读。短文本 (<3 字) → nan。
    用字符 3-gram 而非 gzip: 避免短文本压缩头部开销主导, 更可解释。
    """
    s = re.sub(r'\s+', '', content)
    if len(s) < 3:
        return float('nan')
    grams = [s[i:i + 3] for i in range(len(s) - 2)]
    total = len(grams)
    uniq = len(set(grams))
    return round(1.0 - uniq / total, 6) if total > 0 else float('nan')


def compute_lexical_complexity(content: str) -> dict[str, float]:
    """对单一文本计算 6+1 个词汇/句法复杂度测度 (单次 posseg pass)。

    Args:
        content: 任意单一文本 (典型 content_full 或 content_ctx)。

    Returns:
        dict: LEXICAL_COMPLEXITY_KEYS 各键 → float (无效/空文本 → nan)。
    """
    if not isinstance(content, str) or not content.strip():
        return _empty_result()
    # 拦截 pandas astype(str) 字符串化 NaN 哨兵 (与 numerical_intensity 同款保护)
    if content.strip() in ('nan', 'NaN', 'None', '<NA>', 'NaT'):
        return _empty_result()

    # ── 单次词性标注 pass (posseg 比 jieba.cut 慢 ~2-3x, 是新测度的必要成本) ──
    pairs = [(w, f) for w, f in pseg.cut(content) if w.strip()]
    real_pairs = [(w, f) for w, f in pairs if f != _PUNCT_FLAG]
    n_real = len(real_pairs)
    if n_real == 0:
        return _empty_result()

    cutoff = _rare_word_cutoff()
    common_chars = _common_char_set()
    freq = jieba.dt.FREQ

    n_rare = 0          # 低频/难词数
    n_nominal = 0       # 名词化 token 数
    n_function = 0      # 功能词 token 数
    n_entity = 0        # 具名实体 + 数词 token 数 (specificity 分子)
    n_adversative = 0   # 逆接连词 token 数
    for w, f in real_pairs:
        # 1) rare_word: 词频 <= cutoff (OOV freq=0 也命中)
        if freq.get(w, 0) <= cutoff:
            n_rare += 1
        # 3) nominalization: vn/an 词性 或 名词且以名词化后缀结尾
        if f in _NOMINAL_FLAGS or (f and f[0] == 'n' and w[-1] in _NOMINAL_SUFFIX):
            n_nominal += 1
        # 4) function word: u/p/c/r/y/e 词性前缀
        if f and f[0] in _FUNCTION_FLAG_PREFIXES:
            n_function += 1
        # 5) specificity: 具名实体 (nr/ns/nt/nz) 或 数词 (m/mq)
        if f in _ENTITY_FLAGS or (f and f[0] == 'm'):
            n_entity += 1
        # 7) adversative: 命中独立逆接词表
        if w in _ADVERSATIVE_WORDS:
            n_adversative += 1

    # 2) hard_char: 非常用 Han 字 / 全部 Han 字
    han = [ch for ch in content if '一' <= ch <= '鿿']
    n_han = len(han)
    if n_han >= _MIN_HAN_CHARS:
        n_hard = sum(1 for ch in han if ch not in common_chars)
        hard_char_ratio = round(n_hard / n_han, 6)
    else:
        hard_char_ratio = float('nan')

    return {
        'rare_word_ratio': _safe_div(n_rare, n_real),
        'hard_char_ratio': hard_char_ratio,
        'nominalization_ratio': _safe_div(n_nominal, n_real),
        'function_word_ratio': _safe_div(n_function, n_real),
        'specificity_index': _safe_div(n_entity, n_real),
        'within_doc_redundancy': _char_trigram_redundancy(content),
        'adversative_ratio': _safe_div(n_adversative, n_real),
        'n_words_real': float(n_real),  # 词级文章长度 (批 #7, 供 ln_word_count)
    }
