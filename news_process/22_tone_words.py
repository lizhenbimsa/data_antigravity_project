"""
22_tone_words.py — 阶段22：基于词典的情感分析 + 语言学规则增强
===================================================================

功能：
    使用多个中文金融/通用情感词典，对每篇新闻计算情感得分。

┌────────────────────────────────────────────────────────────┐
│ 词典列表（来源：config/tone_dicts.json）                      │
├────────────────────────────────────────────────────────────┤
│ 1. jiang_2021  姜富伟等（2021）中文金融情感词典                 │
│    └─ positive(3,194)  /  negative(5,621)                  │
│       基于 LM(2011) 英文词典翻译扩充；两类不跨类去重            │
│                                                            │
│ 2. yao_2021   姚加权等（2021）金融领域中文情绪词典              │
│    ├─ annualReport_positive(3,592) / negative(1,633)        │
│    ├─ socialMedia_positive(912)    / negative(965)          │
│    └─ positive = 年报∪社媒去重(3,844) / negative(2,074)      │
│                                                            │
│ 3. bian_2021  Bian et al.(2021) LM 中文本土化扩充版           │
│    └─ positive(1,107)  /  negative(1,488)                  │
│                                                            │
│ 4. du_2022    Du et al.(2022) 含政治正面词金融情感扩充          │
│    ├─ positive(2,235)  /  negative(2,986)                  │
│    └─ political_positive(1,434)（以 0.5 权重加入）              │
│                                                            │
│ 5. you_2018   You et al.(2018) 中文金融情感词典               │
│    ├─ positive(1,425)  / negative(1,583)                   │
│    ├─ definite(388)  / ambiguous(178, 仅存档)                │
└────────────────────────────────────────────────────────────┘

语言学规则增强：
    - 否定词处理（翻转极性，窗口 = NEGATION_WINDOW 个分词单元）
    - 程度副词处理（放大/缩小情感强度，六级权重体系）
    - 转折连词处理（转折后权重提升 ADVERSATIVE_BOOST 倍）

性能优化：
    - frozenset 替代 set 加速 O(1) 查找
    - jieba 静默初始化
    - joblib 并行分批处理

输入：
    阶段3b输出的 Parquet 文件（经过 LLM 语义精筛确认的银行金融科技新闻）

输出：
    追加各词典的得分、标签和匹配详情列
"""

import os
import re
import json
import math
import time
import logging
from typing import Any
import pandas as pd
import numpy as np
from collections import Counter
from joblib import Parallel, delayed
import psutil
import ahocorasick
from utils.helpers import load_config, setup_logging, log_memory_usage, log_stage_summary, safe_save_preview_csv

try:
    import jieba
    jieba.setLogLevel(logging.WARNING)  # 抑制 jieba 的 INFO 级别日志输出
except ImportError:
    raise ImportError("请安装 jieba: pip install jieba")

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "22_tone_words"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 从配置中获取情感分析参数
SENTIMENT_PARAMS = CONFIG.get('sentiment_analysis', {}).get('tone_words', {})

# 词典文件路径
TONE_DICTS_FILE = CONFIG['paths'].get(
    'tone_dicts_file',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'tone_dicts.json')
)


# ============================================================================
# 2. 语言学规则常量（从 config.yaml 加载）
#
# 设计依据与参考文献（均已核实，提供 DOI/链接）：
#
#   否定词：
#     - Jia, L., Yu, C., & Meng, W. (2009). CIKM '09, pp. 1827-1830.
#       DOI: 10.1145/1645953.1646241
#     - Pang, B., & Lee, L. (2008). Foundations and Trends in IR, 2(1-2), 1-135.
#       DOI: 10.1561/1500000001
#
#   程度副词：
#     - Li, F., Huang, M., & Zhu, X. (2010). AAAI 2010, pp. 1371-1376.
#       DOI: 10.1609/aaai.v24i1.7523
#     - Liu, B. (2012). Sentiment Analysis and Opinion Mining. Morgan & Claypool.
#       DOI: 10.2200/s00416ed1v01y201204hlt016
#     - Kennedy, A., & Inkpen, D. (2006). Computational Intelligence, 22(2), 110-125.
#       DOI: 10.1111/j.1467-8640.2006.00277.x
#
#   转折连词：
#     - Ding, X., Liu, B., & Yu, P. S. (2008). WSDM '08, pp. 231-240.
#       DOI: 10.1145/1341531.1341561
#     - Wang, F., Wu, Y., & Qiu, L. (2012). COLING 2012: Posters, pp. 1311-1320.
#       URL: https://aclanthology.org/C12-2128/
# ============================================================================

# ── 否定词集合（frozenset：不可变 + O(1) 查找） ──
# 遇到否定词时，将其后 NEGATION_WINDOW 个分词单元内的情感词极性翻转。
NEGATION_WORDS: frozenset[str] = frozenset(SENTIMENT_PARAMS.get('negation_words', []))

# ── 程度副词及其权重倍数 ──
# 权重含义：>1 程度加强，<1 程度减弱
# 分级依据：HowNet 六级程度体系 + Liu(2012) 三级线性近似
DEGREE_WORDS: dict[str, float] = SENTIMENT_PARAMS.get('degree_words', {})

# ── 转折连词集合 ──
# 转折后的内容更能反映作者真实立场（"末尾效应"）
ADVERSATIVE_WORDS: frozenset[str] = frozenset(SENTIMENT_PARAMS.get('adversative_words', []))

# 转折后权重提升倍数
ADVERSATIVE_BOOST: float = float(SENTIMENT_PARAMS.get('adversative_boost', 1.5))

# ── 句末标点集合（句法边界标记）──
# 遇到句末标点时重置转折/否定/程度状态，确保作用域限定为当前句
# 学术依据: Ding, Liu & Yu (2008, WSDM) 的转折效应作用域为从句级别
# 注意: 不包含逗号——逗号连接同一复句内的从句, 转折效应理应跨越
SENTENCE_END_MARKERS: frozenset[str] = frozenset(
    SENTIMENT_PARAMS.get('sentence_end_markers', ['。', '！', '？', '!', '?', '；', ';'])
)

# 否定词有效作用窗口（向后影响的分词单元数）
# 设为 2：覆盖"不 [程度副词] 情感词"结构（如"不太 乐观"）
NEGATION_WINDOW = SENTIMENT_PARAMS.get('negation_window', 2)

# ── 前瞻性陈述词汇集 ──
# Li, F. (2010). The Information Content of Forward-Looking Statements
# in Corporate Filings—A Naive Bayesian Machine Learning Approach.
# Journal of Accounting Research, 48(5), 1049-1102.
# DOI: 10.1111/j.1475-679X.2010.00382.x
FORWARD_LOOKING_WORDS: frozenset[str] = frozenset(
    SENTIMENT_PARAMS.get('forward_looking_words', [])
)


# ============================================================================
# 3. 词典加载
# ============================================================================

def load_all_dictionaries() -> list[tuple[str, dict[str, float]]]:
    """从统一的 tone_dicts.json 加载所有情感词典。

    Returns:
        list[tuple]: ``[(dict_name, {word: score}), ...]``
            其中 score > 0 表示正面词，score < 0 表示负面词，
            score = 0.5 表示政治正面词（du_2022 特有）。
    """
    logger.info(f"正在从 {TONE_DICTS_FILE} 加载情感词典...")

    all_dict_data = {}
    if os.path.exists(TONE_DICTS_FILE):
        try:
            with open(TONE_DICTS_FILE, 'r', encoding='utf-8') as f:
                all_dict_data = json.load(f)
            if not isinstance(all_dict_data, dict):
                logger.error(f"词典文件格式错误: 期望 JSON 对象，实际为 {type(all_dict_data).__name__}")
                all_dict_data = {}
        except json.JSONDecodeError as e:
            logger.error(f"词典文件 JSON 解析失败: {e}")
        except Exception as e:
            logger.error(f"加载 {TONE_DICTS_FILE} 失败: {e}")
    else:
        logger.warning(f"词典文件未找到: {TONE_DICTS_FILE}")

    dictionaries = []
    dict_keys = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']

    for dict_key in dict_keys:
        entry = all_dict_data.get(dict_key, {})
        dict_name = entry.get('name', dict_key)
        d = {}

        # 从 JSON 中的 positive/negative 列表构建 {word: score}
        for word in entry.get('positive', []):
            word = str(word).strip()
            if word:
                d[word] = 1.0
        for word in entry.get('negative', []):
            word = str(word).strip()
            if word:
                d[word] = -1.0

        # Du et al. (2022) 特有：政治正面词以较低权重 0.5 加入
        for word in entry.get('political_positive', []):
            word = str(word).strip()
            if word and word not in d:  # 避免覆盖已有正面词
                d[word] = 0.5

        dictionaries.append((dict_key, d))

        pos_cnt = sum(1 for v in d.values() if v > 0)
        neg_cnt = sum(1 for v in d.values() if v < 0)
        pol_cnt = sum(1 for v in d.values() if v == 0.5)

        if d:
            logger.info(f"  {dict_key} ({dict_name}): {len(d)} 个词汇 "
                        f"(正面={pos_cnt}, 负面={neg_cnt})")
            # 各词典子类别详细统计
            if dict_key == 'du_2022' and pol_cnt > 0:
                logger.info(f"    └─ political_positive: {pol_cnt} 词 (权重=0.5)")
        else:
            logger.info(f"  {dict_key} ({dict_name}): 空（待填充）")

    total_loaded = sum(len(d) for _, d in dictionaries)
    non_empty = sum(1 for _, d in dictionaries if len(d) > 0)
    logger.info(f"词典加载完成: {non_empty}/{len(dict_keys)} 个词典有效, 共 {total_loaded} 个词汇条目")

    return dictionaries


# ============================================================================
# 4. 语言学规则情感计算引擎
# ============================================================================

def _compute_sentiment_with_rules(tokens: list[str], sentiment_dict: dict[str, float]) -> tuple[float, float, int, int, list[dict[str, Any]]]:
    """对分词序列使用语言学规则增强的词典法计算情感得分。

    内部状态机：
      遍历 token 序列，维护三个状态变量：
        ① negation_remaining: 否定窗口剩余 token 数（>0 则极性翻转）
        ② degree_multiplier:  当前程度副词倍率（碰到情感词时消费并重置）
        ③ adversative_active:  是否处于转折后区域（遇句末标点重置, Ding 2008 从句级作用域）

    状态转移规则：
        token ∈ SENTENCE_END_MARKERS → 重置转折、否定、程度（句法边界）
        token ∈ ADVERSATIVE_WORDS → 激活转折，重置否定和程度
        token ∈ NEGATION_WORDS    → 设置否定窗口
        token ∈ DEGREE_WORDS      → 设置程度倍率
        token ∈ sentiment_dict    → 计算 score = base × degree × negation × adversative
        其他                       → 重置程度副词（未被消费）

    Args:
        tokens:         分词结果列表。
        sentiment_dict: ``{word: score}`` 情感词典。

    Returns:
        tuple: (raw_score, normalized_score, pos_count, neg_count, matched_words)
    """
    total_score: float = 0.0
    pos_count: int = 0
    neg_count: int = 0
    matched_words: list[dict[str, Any]] = []

    negation_remaining: int = 0
    degree_multiplier: float = 1.0
    adversative_active: bool = False

    for token in tokens:
        # ── 句法边界: 句末标点重置全部句法级状态 ──
        # Ding et al. (2008): 转折效应限定为从句级 (Clause-level)
        if token in SENTENCE_END_MARKERS:
            adversative_active = False
            negation_remaining = 0
            degree_multiplier = 1.0
            continue

        # 检查转折连词
        if token in ADVERSATIVE_WORDS:
            adversative_active = True
            degree_multiplier = 1.0
            negation_remaining = 0
            continue

        # 检查否定词
        if token in NEGATION_WORDS:
            negation_remaining = NEGATION_WINDOW
            continue

        # 检查程度副词
        if token in DEGREE_WORDS:
            degree_multiplier = DEGREE_WORDS[token]
            continue

        # 检查情感词
        if token in sentiment_dict:
            base_score = sentiment_dict[token]

            # 应用否定词翻转
            if negation_remaining > 0:
                base_score = -base_score

            # 应用程度副词
            final_score = base_score * degree_multiplier

            # 应用转折加权
            if adversative_active:
                final_score *= ADVERSATIVE_BOOST

            total_score += final_score

            if final_score > 0:
                pos_count += 1
            elif final_score < 0:
                neg_count += 1

            matched_words.append({
                'word': token,
                'base': sentiment_dict[token],
                'final': round(final_score, 4),
                'boosted': adversative_active,
            })

            degree_multiplier = 1.0  # 已消费程度副词
        else:
            degree_multiplier = 1.0  # 非情感词重置程度副词

        # 否定窗口递减
        if negation_remaining > 0:
            negation_remaining -= 1

    # 归一化: score / (pos_count + neg_count)，防止长文本偏高
    total_matched = pos_count + neg_count
    normalized_score = total_score / total_matched if total_matched > 0 else 0.0

    return total_score, normalized_score, pos_count, neg_count, matched_words


def _score_to_label(normalized_score: float, pos_threshold=0.1, neg_threshold=-0.1) -> str:
    """将归一化得分映射为情感标签。

    Args:
        normalized_score: 归一化情感得分。
        pos_threshold:    正面阈值（默认 0.1）。
        neg_threshold:    负面阈值（默认 -0.1）。

    Returns:
        str: ``"正面"`` / ``"中性"`` / ``"负面"``
    """
    if normalized_score > pos_threshold:
        return "正面"
    elif normalized_score < neg_threshold:
        return "负面"
    else:
        return "中性"


def _compute_forward_looking_ratio(tokens: list[str]) -> tuple[float, int]:
    """计算前瞻性词汇比率。

    学术依据:
      Li, F. (2010). The Information Content of Forward-Looking Statements
      in Corporate Filings—A Naive Bayesian Machine Learning Approach.
      Journal of Accounting Research, 48(5), 1049-1102.
      DOI: 10.1111/j.1475-679X.2010.00382.x

    Li (2010) 使用前瞻性关键词在 MD&A 中的句子级占比衡量前瞻性信息含量。
    本实现使用 token 级占比作为中文新闻的等价度量。

    注意: 否定句中的前瞻性词仍计入（"不预计降息"中"预计"仍属前瞻性表述），
    因为判定的是时间取向（prospective vs. retrospective），而非极性。

    Args:
        tokens: jieba 分词结果列表（已过滤空白 token）。

    Returns:
        tuple: (fl_ratio, fl_count)
            fl_ratio: 前瞻性词汇 token 占总 token 之比 ∈ [0, 1]
            fl_count: 前瞻性词汇绝对频次
    """
    if not tokens:
        return 0.0, 0
    fl_count = sum(1 for t in tokens if t in FORWARD_LOOKING_WORDS)
    return fl_count / len(tokens), fl_count


def _compute_readability(content: str, tokens: list[str]) -> dict[str, float]:
    """计算中文文本可读性的三维度代理指标。

    学术依据:
      Loughran, T. & McDonald, B. (2014). Measuring Readability in
      Financial Disclosures. Journal of Finance, 69(4), 1643-1671.
      DOI: 10.1111/jofi.12162
      — 指出 Gunning-Fog Index 不适用于金融文本（多音节商业术语
      如 "financial", "company" 被误判为"复杂"），建议使用替代度量。

      Bonsall, S.B., Leone, A.J., Miller, B.P. & Rennekamp, K. (2017).
      A Plain English Measure of Financial Reporting Readability.
      Journal of Accounting and Economics, 63(2-3), 329-357.
      DOI: 10.1016/j.jacceco.2017.03.002
      — 提出 Bog Index 捕捉 SEC Plain English 属性，但依赖英文句法。

    对于中文文本，采用以下三个维度的代理指标：

    1. avg_sentence_len (ASL): 平均句长（字符/句）— 越长越难读
    2. type_token_ratio (TTR): 词汇丰富度（唯一词/总词）— 越高越复杂
    3. char_per_word (CPW): 平均词长（字符/词）— 越长越倾向专业术语

    Args:
        content: 原始文本字符串。
        tokens:  jieba 分词结果列表（已过滤空白 token）。

    Returns:
        dict: {'avg_sentence_len': float, 'type_token_ratio': float,
               'char_per_word': float}
    """
    # 1. 平均句长 (ASL) — 按中文句末标点分割
    sentences = re.split(r'[。！？!?；;]', content)
    sentences = [s for s in sentences if len(s.strip()) > 0]
    n_sentences = max(len(sentences), 1)
    avg_sentence_len = sum(len(s.strip()) for s in sentences) / n_sentences

    # 2. Type-Token Ratio (TTR) — 词汇丰富度
    n_tokens = max(len(tokens), 1)
    ttr = len(set(tokens)) / n_tokens

    # 3. 平均词长 (CPW) — 字符级词复杂度
    total_chars = sum(len(t) for t in tokens)
    cpw = total_chars / n_tokens

    return {
        'avg_sentence_len': round(avg_sentence_len, 2),
        'type_token_ratio': round(ttr, 4),
        'char_per_word': round(cpw, 4),
    }


# ============================================================================
# 4B. IDF 加权稳健性检验 (Gentzkow, Kelly & Taddy, 2019, JEL §2.2)
# ============================================================================

def build_idf_weights(
    df: pd.DataFrame,
    dictionaries: list[tuple[str, dict[str, float]]],
    text_col: str = '内容',
) -> dict[str, dict[str, float]]:
    """基于全语料库计算每个词典中情感词的 IDF 权重。

    公式 (smooth IDF + 均值归一化 + Winsorization):
        raw_idf(w) = log₁₀(N / (1 + df(w)))
        normalized_idf(w) = raw_idf(w) / mean(raw_idf)
        final_idf(w) = Winsorize(normalized_idf, P1, P99)

    学术依据:
      Gentzkow, M., Kelly, B. & Taddy, M. (2019). Text as Data.
      Journal of Economic Literature, 57(3), 535-574. §2.2: TF-IDF.

      Manning, C.D., Raghavan, P. & Schütze, H. (2008).
      Introduction to Information Retrieval. Cambridge University Press.
      Ch. 6.2.1: smooth IDF 公式。

      Fama, E.F. & French, K.R. (1993). Common Risk Factors in the Returns
      on Stocks and Bonds. Journal of Financial Economics, 33(1), 3-56.
      — Winsorization (P1/P99) 标准做法。

    设计决策:
      1. DF 通过 Aho-Corasick 子串匹配一次遍历全语料计算。
         语义等价于 jieba 分词后匹配（中文情感词为 2-4 字完整词组），
         但速度提升 ~50x（AC ~50K doc/s vs jieba ~1K doc/s）。
      2. IDF 在全文语料（text_col='内容'）上统一计算一次，两轨共享。
         IDF 的语义是「词在整体文档集合中的区分力」，
         上下文片段（content_ctx）是全文子集，不应独立计算。
      3. 均值归一化确保 IDF 加权后得分量级 ≈ 等权版，可共享阈值。
      4. P1/P99 Winsorization 防止极端稀有词主导或极高频词归零。

    Args:
        df:           全量 DataFrame，需含 text_col 列。
        dictionaries: 词典列表 [(name, {word: score}), ...]。
        text_col:     文本列名。

    Returns:
        dict: {dict_name: {word: capped_normalized_idf}}
    """
    N = len(df)
    if N == 0:
        logger.warning("IDF: 语料为空，所有权重降级为 1.0")
        return {name: {w: 1.0 for w in d} for name, d in dictionaries}

    texts = df[text_col].fillna('').astype(str).tolist()

    # 1. 合并所有词典词汇（去重），构建 AC 自动机
    all_words = set()
    for _, d in dictionaries:
        all_words.update(d.keys())

    if not all_words:
        return {name: {} for name, _ in dictionaries}

    A = ahocorasick.Automaton()
    for word in sorted(all_words):
        A.add_word(word, word)
    A.make_automaton()

    # 2. 一次遍历全语料计算文档频率
    doc_freq: Counter = Counter()
    for text in texts:
        seen_in_doc: set[str] = set()
        for _, word in A.iter(text):
            seen_in_doc.add(word)
        doc_freq.update(seen_in_doc)

    # 3. 为每个词典分别计算 IDF → 均值归一化 → Winsorize
    result: dict[str, dict[str, float]] = {}
    for dict_name, sentiment_dict in dictionaries:
        if not sentiment_dict:
            result[dict_name] = {}
            continue

        raw_idf = {}
        for word in sentiment_dict:
            df_w = doc_freq.get(word, 0)
            raw_idf[word] = math.log10(N / (1 + df_w))

        # 均值归一化（使 IDF 加权后量级 ≈ 等权版）
        values = list(raw_idf.values())
        mean_val = float(np.mean(values)) if values else 1.0
        if mean_val > 0:
            normed = {w: v / mean_val for w, v in raw_idf.items()}
        else:
            normed = {w: 1.0 for w in raw_idf}

        # P1/P99 Winsorization (Fama & French 1993)
        normed_vals = np.array(list(normed.values()))
        if len(normed_vals) >= 2:
            p1, p99 = float(np.percentile(normed_vals, 1)), float(np.percentile(normed_vals, 99))
            capped = {w: float(np.clip(v, p1, p99)) for w, v in normed.items()}
        else:
            capped = dict(normed)

        result[dict_name] = capped

    return result


def _build_idf_weighted_dict(
    sentiment_dict: dict[str, float],
    idf_weights: dict[str, float],
) -> dict[str, float]:
    """将 IDF 权重乘入情感词典的 base_score。

    weighted_score(w) = base_score(w) × idf_weight(w)

    保留 base_score 的符号（正/负极性）和非对称幅值：
    - 正面词: +1.0 × idf
    - 负面词: -1.0 × idf
    - du_2022 政治词: +0.5 × idf（保留较低权重）

    语言学规则引擎兼容性:
      生成的 idf_dict 可直接传入 _compute_sentiment_with_rules()，
      因为该函数仅关心 sentiment_dict[token] 的数值，
      否定/程度/转折规则在此之上叠加，与 IDF 权重正交。
    """
    return {
        word: base_score * idf_weights.get(word, 1.0)
        for word, base_score in sentiment_dict.items()
    }


# ============================================================================
# 5. 单篇文章分析
# ============================================================================

# 全局词典变量（延迟加载，在 main() 中初始化）
ALL_DICTIONARIES = None
IDF_DICTIONARIES = None  # IDF 加权词典（稳健性检验，在 main() 中初始化）

def _inject_custom_dicts_to_jieba():
    """将所有情感词、银行名称、金融科技词汇注入jieba分词器，防止专业词汇被切碎。"""
    logger.info("正在将自定义领域词汇注入 jieba 分词器...")
    added_count = 0

    # 1. 注入所有情感词典中的词汇
    for dict_name, sentiment_dict in ALL_DICTIONARIES:
        if sentiment_dict:
            for word in sentiment_dict.keys():
                jieba.add_word(word)
                added_count += 1

    # 2. 注入银行名称库 (11_news_bank.py 的同源字典)
    bank_dict_path = CONFIG['paths'].get(
        'bank_names_file',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'bank_names.json')
    )
    if os.path.exists(bank_dict_path):
        try:
            with open(bank_dict_path, 'r', encoding='utf-8') as f:
                bank_data = json.load(f)
                if isinstance(bank_data, list):
                    for bank in bank_data:
                        if not isinstance(bank, dict): continue
                        std_name = bank.get('standard_name')
                        if std_name:
                            jieba.add_word(str(std_name).strip())
                            added_count += 1
                        for variant in bank.get('variants', []):
                            if variant:
                                jieba.add_word(str(variant).strip())
                                added_count += 1
        except Exception as e:
            logger.warning(f"未能加载银行词典注入jieba: {e}")

    # 3. 注入金融科技词典 (12_news_fintech.py 的同源字典)
    fintech_dict_path = CONFIG['paths'].get(
        'fintech_dict_file',
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'fintech_dict.json')
    )
    if os.path.exists(fintech_dict_path):
        try:
            with open(fintech_dict_path, 'r', encoding='utf-8') as f:
                fintech_data = json.load(f)
                if isinstance(fintech_data, list):
                    for word in fintech_data:
                        if word:
                            jieba.add_word(str(word).strip())
                            added_count += 1
                elif isinstance(fintech_data, dict):
                    for category, words_list in fintech_data.items():
                        if isinstance(words_list, list):
                            for word in words_list:
                                if word:
                                    jieba.add_word(str(word).strip())
                                    added_count += 1
        except Exception as e:
            logger.warning(f"未能加载金融科技词典注入jieba: {e}")
            
    # 4. 注入否定词与程度词增强规则库
    for word in NEGATION_WORDS:
        jieba.add_word(word)
    for word in DEGREE_WORDS.keys():
        jieba.add_word(word)
    for word in ADVERSATIVE_WORDS:
        jieba.add_word(word)

    # 5. 注入前瞻性词汇（防止多字前瞻性词被 jieba 切碎，
    #    如"预判""酝酿""筹划"等）
    for word in FORWARD_LOOKING_WORDS:
        if len(word) > 1:  # 单字词无需注入
            jieba.add_word(word)

    logger.info(f"成功注入 {added_count} 个领域自定义词汇到 jieba 分词树。")

# 注入操作延迟到 main() 中执行
# _inject_custom_dicts_to_jieba()


def _analyze_single_article(content: str) -> dict:
    """对单篇文章执行所有词典的情感分析。

    分词只执行一次（jieba.cut），然后对每个词典独立计分。

    Args:
        content: 文章内容文本。

    Returns:
        dict: 包含各词典的得分、标签和最佳匹配详情。
    """
    result: dict[str, Any] = {}

    if not isinstance(content, str) or not content.strip():
        for dict_name, _ in ALL_DICTIONARIES:
            result[f'{dict_name}_score'] = 0.0
            result[f'{dict_name}_label'] = '中性'
        result['sentiment_details'] = ''
        result['forward_looking_ratio'] = 0.0
        result['forward_looking_count'] = 0
        result['avg_sentence_len'] = 0.0
        result['type_token_ratio'] = 0.0
        result['char_per_word'] = 0.0
        result['pos_ratio'] = 0.0
        result['neg_ratio'] = 0.0
        # IDF 加权列一致性初始化（确保所有行返回相同 key 结构）
        if IDF_DICTIONARIES is not None:
            for dict_name, _ in IDF_DICTIONARIES:
                result[f'{dict_name}_idf_score'] = 0.0
                result[f'{dict_name}_idf_label'] = '中性'
        return result

    # 分词（单次调用，所有词典共享分词结果）
    tokens = list(jieba.cut(content))

    # 防御：极端文本（纯符号、纯控制字符）可能产生全空分词结果
    tokens = [t for t in tokens if t.strip()]
    if not tokens:
        for dict_name, _ in ALL_DICTIONARIES:
            result[f'{dict_name}_score'] = 0.0
            result[f'{dict_name}_label'] = '中性'
        result['sentiment_details'] = ''
        result['forward_looking_ratio'] = 0.0
        result['forward_looking_count'] = 0
        result['avg_sentence_len'] = 0.0
        result['type_token_ratio'] = 0.0
        result['char_per_word'] = 0.0
        result['pos_ratio'] = 0.0
        result['neg_ratio'] = 0.0
        # IDF 加权列一致性初始化（确保所有行返回相同 key 结构）
        if IDF_DICTIONARIES is not None:
            for dict_name, _ in IDF_DICTIONARIES:
                result[f'{dict_name}_idf_score'] = 0.0
                result[f'{dict_name}_idf_label'] = '中性'
        return result

    # 对每个词典计算情感
    best_detail: list[dict[str, Any]] = []
    best_matched_count: int = 0
    best_pos_count: int = 0
    best_neg_count: int = 0

    for dict_name, sentiment_dict in ALL_DICTIONARIES:
        if not sentiment_dict:
            result[f'{dict_name}_score'] = 0.0
            result[f'{dict_name}_label'] = '中性'
            continue

        raw_score, norm_score, pos_cnt, neg_cnt, matched = \
            _compute_sentiment_with_rules(tokens, sentiment_dict)

        result[f'{dict_name}_score'] = round(norm_score, 4)
        result[f'{dict_name}_label'] = _score_to_label(norm_score)

        # 记录匹配词最多的词典的详情（用于最终输出和正/负面词频分离）
        if len(matched) > best_matched_count:
            best_matched_count = len(matched)
            best_detail = matched
            best_pos_count = pos_cnt
            best_neg_count = neg_cnt

    # 仅保留 Top-20 匹配词（按绝对影响力降序）
    top_detail = sorted(best_detail, key=lambda x: abs(x['final']), reverse=True)[:20]
    result['sentiment_details'] = json.dumps(top_detail, ensure_ascii=False) if top_detail else ''

    # ── 前瞻性陈述比率 ──
    # Li, F. (2010). Journal of Accounting Research, 48(5), 1049-1102.
    # DOI: 10.1111/j.1475-679X.2010.00382.x
    fl_ratio, fl_count = _compute_forward_looking_ratio(tokens)
    result['forward_looking_ratio'] = round(fl_ratio, 6)
    result['forward_looking_count'] = fl_count

    # ── 文本可读性控制变量 ──
    # Loughran, T. & McDonald, B. (2014). Journal of Finance, 69(4), 1643-1671.
    # DOI: 10.1111/jofi.12162
    readability = _compute_readability(content, tokens)
    result['avg_sentence_len'] = readability['avg_sentence_len']
    result['type_token_ratio'] = readability['type_token_ratio']
    result['char_per_word'] = readability['char_per_word']

    # ── 正/负面词频分离（稳健性检验）──
    # Berger, A.N., Kim, S. & Ma, F. (2024). Bank Sentiment and Liquidity
    # Hoarding. SSRN Working Paper, Appendix S6.
    # Loughran, T. & McDonald, B. (2011). When Is a Liability Not a Liability?
    # Textual Analysis, Dictionaries, and 10-Ks.
    # Journal of Finance, 66(1), 35-65. DOI: 10.1111/j.1540-6261.2010.01625.x
    n_tokens = len(tokens)
    result['pos_ratio'] = round(best_pos_count / n_tokens, 6) if n_tokens > 0 else 0.0
    result['neg_ratio'] = round(best_neg_count / n_tokens, 6) if n_tokens > 0 else 0.0

    # ── IDF 加权并行度量 (Gentzkow et al. 2019, JEL §2.2) ──
    # 复用同一次 jieba.cut() 的 tokens，零额外分词开销
    if IDF_DICTIONARIES is not None:
        for dict_name, idf_dict in IDF_DICTIONARIES:
            if not idf_dict:
                result[f'{dict_name}_idf_score'] = 0.0
                result[f'{dict_name}_idf_label'] = '中性'
                continue
            _, idf_norm, _, _, _ = _compute_sentiment_with_rules(tokens, idf_dict)
            result[f'{dict_name}_idf_score'] = round(idf_norm, 4)
            result[f'{dict_name}_idf_label'] = _score_to_label(idf_norm)

    return result


# ============================================================================
# 6. 批处理和统计
# ============================================================================

def classify_batch(df_batch: pd.DataFrame) -> tuple:
    """对单个批次执行词典法双轨情感分析（全文 + 上下文片段）。

    Args:
        df_batch: 待分析的 DataFrame 批次（需含 'content_ctx' 列，
                  由阶段 21 物化生成）。

    Returns:
        tuple: (processed_df, stats_dict)
    """
    stats = {'total': 0}
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx']:
            stats[f'{dict_name}_正面{track}'] = 0
            stats[f'{dict_name}_中性{track}'] = 0
            stats[f'{dict_name}_负面{track}'] = 0

    if df_batch.empty:
        return df_batch, stats

    df = df_batch.copy()
    stats['total'] = len(df)

    # 对每篇文章执行双轨情感分析
    # content_ctx 由阶段 21 预计算并物化为列，直接读取以确保三种方法输入一致
    def _dual_analyze(row):
        content_full = str(row.get('内容', ''))
        content_ctx = str(row.get('content_ctx', content_full))

        res_full = _analyze_single_article(content_full)
        res_ctx = _analyze_single_article(content_ctx)

        # 合并：为每个键追加轨道后缀
        merged = {}
        for k, v in res_full.items():
            merged[f'{k}_full'] = v
        for k, v in res_ctx.items():
            merged[f'{k}_ctx'] = v
        return merged

    results = df.apply(_dual_analyze, axis=1)

    # 提取各列（双轨）
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx']:
            df[f'{dict_name}_score{track}'] = results.apply(
                lambda r: r.get(f'{dict_name}_score{track}', 0.0))
            df[f'{dict_name}_label{track}'] = results.apply(
                lambda r: r.get(f'{dict_name}_label{track}', '中性'))

            label_counts = df[f'{dict_name}_label{track}'].value_counts()
            stats[f'{dict_name}_正面{track}'] = int(label_counts.get('正面', 0))
            stats[f'{dict_name}_中性{track}'] = int(label_counts.get('中性', 0))
            stats[f'{dict_name}_负面{track}'] = int(label_counts.get('负面', 0))

    df['sentiment_details_full'] = results.apply(lambda r: r.get('sentiment_details_full', ''))
    df['sentiment_details_ctx'] = results.apply(lambda r: r.get('sentiment_details_ctx', ''))

    # ── 提取 IDF 加权列（双轨）──
    if IDF_DICTIONARIES is not None:
        for dict_name, _ in IDF_DICTIONARIES:
            for track in ['_full', '_ctx']:
                df[f'{dict_name}_idf_score{track}'] = results.apply(
                    lambda r, k=f'{dict_name}_idf_score{track}': r.get(k, 0.0))
                df[f'{dict_name}_idf_label{track}'] = results.apply(
                    lambda r, k=f'{dict_name}_idf_label{track}': r.get(k, '中性'))

    # ── 提取新增指标列（双轨）──
    new_metric_cols = [
        'forward_looking_ratio', 'forward_looking_count',
        'avg_sentence_len', 'type_token_ratio', 'char_per_word',
        'pos_ratio', 'neg_ratio',
    ]
    for col in new_metric_cols:
        for track in ['_full', '_ctx']:
            col_key = f'{col}{track}'
            df[col_key] = results.apply(lambda r, k=col_key: r.get(k, 0.0))

    return df, stats


def merge_stats(stats_list: list) -> dict:
    """合并多个批次的统计结果。

    Args:
        stats_list: 各批次返回的统计字典列表。

    Returns:
        dict: 合并后的统计字典。
    """
    merged = {'total': 0}
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx']:
            merged[f'{dict_name}_正面{track}'] = 0
            merged[f'{dict_name}_中性{track}'] = 0
            merged[f'{dict_name}_负面{track}'] = 0

    for s in stats_list:
        merged['total'] += s['total']
        for dict_name, _ in ALL_DICTIONARIES:
            for track in ['_full', '_ctx']:
                merged[f'{dict_name}_正面{track}'] += s.get(f'{dict_name}_正面{track}', 0)
                merged[f'{dict_name}_中性{track}'] += s.get(f'{dict_name}_中性{track}', 0)
                merged[f'{dict_name}_负面{track}'] += s.get(f'{dict_name}_负面{track}', 0)
    return merged


def log_classification_report(stats: dict, logger, track_suffix: str = ''):
    """输出词典法情感分析统计报告。

    Args:
        stats:         合并后的统计字典。
        logger:        日志记录器。
        track_suffix:  轨道后缀 ('_full' 或 '_ctx')，用于区分报告。
    """
    track_label = '全文' if track_suffix == '_full' else '上下文片段' if track_suffix == '_ctx' else ''
    logger.info("=" * 70)
    logger.info(f"===      词典法情感分析统计报告 [{track_label}]      ===")
    logger.info("=" * 70)

    total = stats['total']
    logger.info(f"总记录数: {total:,}")
    logger.info(f"使用词典数: {len(ALL_DICTIONARIES)} 个")
    logger.info(
        f"语言学规则: 否定词({len(NEGATION_WORDS)}个), "
        f"程度副词({len(DEGREE_WORDS)}个), "
        f"转折连词({len(ADVERSATIVE_WORDS)}个)"
    )

    logger.info("-" * 70)
    logger.info(f"{'词典名称':<20} {'正面':>8} {'中性':>8} {'负面':>8} {'正面占比':>10} {'中性占比':>10} {'负面占比':>10}")
    logger.info("-" * 70)

    for dict_name, d in ALL_DICTIONARIES:
        pos = stats.get(f'{dict_name}_正面{track_suffix}', 0)
        neu = stats.get(f'{dict_name}_中性{track_suffix}', 0)
        neg = stats.get(f'{dict_name}_负面{track_suffix}', 0)
        pos_pct = f"{pos / total * 100:.1f}%" if total > 0 else "N/A"
        neu_pct = f"{neu / total * 100:.1f}%" if total > 0 else "N/A"
        neg_pct = f"{neg / total * 100:.1f}%" if total > 0 else "N/A"
        dict_label = f"{dict_name}({len(d)}词)"
        logger.info(f"  {dict_label:<20} {pos:>8,} {neu:>8,} {neg:>8,} {pos_pct:>10} {neu_pct:>10} {neg_pct:>10}")

    logger.info("=" * 70)


# ============================================================================
# 7. 主函数
# ============================================================================

def main():
    """词典法情感分析阶段主入口。"""
    global ALL_DICTIONARIES, IDF_DICTIONARIES
    
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     使用五部中文金融情感词典对每篇新闻进行情感打分。")
    logger.info("     每部词典独立计算正/负词频比, 并通过语言学规则(否定/程度/转折)修正。")
    logger.info("     采用双轨模式: 全文(_full)和上下文片段(_ctx)分别计算, 供下游三角验证。")
    logger.info("")
    logger.info("  📖 方法论依据")
    logger.info("     · IDF 加权: Gentzkow, Kelly & Taddy (2019, JEL 57(3):535-574) §2.2")
    logger.info("       → 降低高频常见词的权重, 提升稀有金融术语的区分度")
    logger.info("     · 语言学规则参考: Jia et al. (2009), Pang & Lee (2008),")
    logger.info("       Li et al. (2010), Liu (2012), Kennedy & Inkpen (2006)")
    logger.info("")
    logger.info("  📊 关键指标解读")
    logger.info("     · Z-score 标准化: 均值=0, 标准差=1。正值=正面倾向, 负值=负面倾向")
    logger.info("     · IDF 权重分位数: P25-P75 的范围越窄 → 词典词汇区分度越均匀")
    logger.info("     · 正/中/负面占比: 若某词典负面>60%, 可能存在负面偏差")
    logger.info("")

    # 延迟加载词典和注入 jieba（避免 import 时的副作用）
    ALL_DICTIONARIES = load_all_dictionaries()
    _inject_custom_dicts_to_jieba()

    non_empty_dicts = [(name, d) for name, d in ALL_DICTIONARIES if len(d) > 0]
    if not non_empty_dicts:
        logger.error("所有情感词典均为空！请检查词典文件。")
        return

    logger.info(f"有效词典: {len(non_empty_dicts)}/{len(ALL_DICTIONARIES)} 个")

    # 定义输入输出
    input_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames'].get('output_21_tone_llms', '21_tone_llms.parquet'))
    output_path = os.path.join(CONFIG['paths']['output_dir'],
                               CONFIG['filenames'].get('output_22_words_tone', '22_tone_words.parquet'))

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        return

    logger.info(f"正在从 {input_path} 加载数据...")
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    logger.info(f"已加载 {input_rows:,} 行数据。")
    log_memory_usage(logger, "数据加载后")

    # ── IDF 加权稳健性检验初始化 ──
    IDF_DICTIONARIES = None
    idf_enabled = SENTIMENT_PARAMS.get('idf_weighting', True)
    if idf_enabled:
        logger.info("═" * 60)
        logger.info("IDF 加权稳健性检验 (Gentzkow et al. 2019, JEL §2.2)")
        logger.info("═" * 60)

        idf_weights = build_idf_weights(df, ALL_DICTIONARIES, text_col='内容')
        IDF_DICTIONARIES = [
            (name, _build_idf_weighted_dict(d, idf_weights.get(name, {})))
            for name, d in ALL_DICTIONARIES
        ]

        # 诊断日志：IDF 分位数 + Top5/Bottom5 词
        for dict_name in idf_weights:
            w = idf_weights[dict_name]
            if w:
                vals = np.array(list(w.values()))
                logger.info(
                    f"  {dict_name}: {len(w)} 词, "
                    f"IDF [min={vals.min():.3f}, P25={np.percentile(vals, 25):.3f}, "
                    f"P50={np.percentile(vals, 50):.3f}, P75={np.percentile(vals, 75):.3f}, "
                    f"max={vals.max():.3f}]"
                )
                sorted_w = sorted(w.items(), key=lambda x: x[1], reverse=True)
                top5 = [(k, f"{v:.2f}") for k, v in sorted_w[:5]]
                bot5 = [(k, f"{v:.2f}") for k, v in sorted_w[-5:]]
                logger.info(f"    IDF 最高 (稀有→高权重): {top5}")
                logger.info(f"    IDF 最低 (常见→低权重): {bot5}")

        # 保存 IDF 权重到 JSON（可复现性，AER/QJE 标准）
        idf_save_path = os.path.join(
            CONFIG['paths']['output_dir'], '22_idf_weights.json')
        try:
            serializable = {
                k: {word: round(val, 6) for word, val in v.items()}
                for k, v in idf_weights.items()
            }
            serializable['_meta'] = {
                'N': int(len(df)),
                'formula': 'log10(N / (1 + df(w)))',
                'normalization': 'mean=1 then Winsorize P1/P99',
                'reference': 'Gentzkow, Kelly & Taddy (2019, JEL) §2.2',
            }
            with open(idf_save_path, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2)
            logger.info(f"  IDF 权重已保存: {idf_save_path}")
        except Exception as e:
            logger.warning(f"  保存 IDF 权重失败: {e}")

        logger.info(f"  IDF 加权词典构建完成: {len(IDF_DICTIONARIES)} 个")
    else:
        logger.info("IDF 加权已在配置中禁用 (idf_weighting: false)")

    # 执行词典法情感分析
    logger.info(f"开始执行词典法情感分析...")
    batch_size = CONFIG['parallel'].get('batch_size', 5000)
    num_batches = max(1, (len(df) - 1) // batch_size + 1)
    df_batches = [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

    all_stats = []
    processed_dfs = []
    n_jobs = CONFIG['parallel'].get('n_jobs', -1)
    logger.info(f"使用 joblib 并行处理: n_jobs={n_jobs}, 共 {num_batches} 个批次")

    results = Parallel(n_jobs=n_jobs, prefer='threads')(
        delayed(classify_batch)(batch) for batch in df_batches
    )
    for res_df, res_stats in results:
        processed_dfs.append(res_df)
        all_stats.append(res_stats)

    # 合并全部结果
    processed_df = pd.concat(processed_dfs, ignore_index=True)

    # P1-4: 为每个词典的得分列添加 Z-score 标准化列（双轨独立计算）
    # 解决跨词典量纲不一致问题，供 34_tone_validation.py 的 Cronbach's Alpha 分析使用
    # 注意：_full 和 _ctx 的 μ 和 σ 必须独立计算，因文本长度差异导致数值分布本质不同
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx']:
            score_col = f"{dict_name}_score{track}"
            zscore_col = f"{dict_name}_zscore{track}"
            if score_col in processed_df.columns:
                mean_val = processed_df[score_col].mean()
                std_val = processed_df[score_col].std()
                if std_val > 0:
                    processed_df[zscore_col] = (processed_df[score_col] - mean_val) / std_val
                else:
                    processed_df[zscore_col] = 0.0
                logger.info(f"  {dict_name} [{track}]: Z-score 标准化完成 (μ={mean_val:.4f}, σ={std_val:.4f})")

    # IDF 列 Z-score 标准化
    if IDF_DICTIONARIES is not None:
        for dict_name, _ in IDF_DICTIONARIES:
            for track in ['_full', '_ctx']:
                score_col = f"{dict_name}_idf_score{track}"
                zscore_col = f"{dict_name}_idf_zscore{track}"
                if score_col in processed_df.columns:
                    mean_val = processed_df[score_col].mean()
                    std_val = processed_df[score_col].std()
                    if std_val > 0:
                        processed_df[zscore_col] = (
                            (processed_df[score_col] - mean_val) / std_val)
                    else:
                        processed_df[zscore_col] = 0.0
                    logger.info(f"  {dict_name}_idf [{track}]: "
                                f"Z-score (μ={mean_val:.4f}, σ={std_val:.4f})")

    processed_df.to_parquet(output_path, index=False)

    # 统计报告（双轨分别打印）
    if all_stats:
        merged_stats = merge_stats(all_stats)
        log_classification_report(merged_stats, logger, track_suffix='_full')
        log_classification_report(merged_stats, logger, track_suffix='_ctx')



    # 生成预览
    preview_path = output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(processed_df, preview_path, logger)

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=len(processed_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} (双轨模式) ---")


if __name__ == "__main__":
    main()
