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
import json
import time
import logging
from typing import Any
import pandas as pd
import numpy as np
from collections import Counter
from joblib import Parallel, delayed
import psutil
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


# ============================================================================
# 5. 单篇文章分析
# ============================================================================

# 全局词典变量（延迟加载，在 main() 中初始化）
ALL_DICTIONARIES = None

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
        return result

    # 对每个词典计算情感
    best_detail: list[dict[str, Any]] = []
    best_matched_count: int = 0

    for dict_name, sentiment_dict in ALL_DICTIONARIES:
        if not sentiment_dict:
            result[f'{dict_name}_score'] = 0.0
            result[f'{dict_name}_label'] = '中性'
            continue

        raw_score, norm_score, pos_cnt, neg_cnt, matched = \
            _compute_sentiment_with_rules(tokens, sentiment_dict)

        result[f'{dict_name}_score'] = round(norm_score, 4)
        result[f'{dict_name}_label'] = _score_to_label(norm_score)

        # 记录匹配词最多的词典的详情（用于最终输出）
        if len(matched) > best_matched_count:
            best_matched_count = len(matched)
            best_detail = matched

    # 仅保留 Top-20 匹配词（按绝对影响力降序）
    top_detail = sorted(best_detail, key=lambda x: abs(x['final']), reverse=True)[:20]
    result['sentiment_details'] = json.dumps(top_detail, ensure_ascii=False) if top_detail else ''

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
    global ALL_DICTIONARIES
    
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

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
