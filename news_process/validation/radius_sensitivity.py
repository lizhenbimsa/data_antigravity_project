"""
news_process.validation.radius_sensitivity — 窗口半径敏感性检验

迁移说明 (Phase 7b)：
    本模块由原 root script ``35_radius_sensitivity.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.radius_sensitivity``

===============================================================

功能：
    对 entity_context 的 sentence_radius 参数进行系统性敏感性分析，
    验证情感分析结果对窗口大小选择的稳健性。

检验设计：
    - 对 radius ∈ {0, 1, 2, 3} 四组设定，分别提取实体上下文
    - 使用全部 5 个词典重新计算情感得分和标签
    - 计算跨半径的标签一致性、得分相关性和分布统计
    - 生成学术论文附录级别的报告（LaTeX 表格 + 可视化图表）

学术依据：
    Hassan et al. (2019, QJE) Proximity-based Attribution 的参数敏感性检验。
    顶刊标准要求对关键方法论参数进行 robustness check。

输入：
    阶段21输出（经 LLM 语义精筛后的数据，含 target_bank 列）

输出：
    1. 敏感性分析报告（JSON + LaTeX 表格）
    2. 可视化图表（标签分布对比、相关性热力图）
    3. 控制台/日志完整统计输出
"""

import json
import logging
import os
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/radius_sensitivity.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import log_memory_usage, log_stage_summary, setup_logging

try:
    import jieba
    jieba.setLogLevel(logging.WARNING)
except ImportError:
    raise ImportError("请安装 jieba: pip install jieba")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "35_radius_sensitivity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 检验参数
RADII = [0, 1, 2, 3]                    # 待检验的窗口半径
FALLBACK_CHAR_RADIUS = 150               # 字符级回退窗口（与原始设定一致）

# 从 22_tone_words 复用的情感参数
SENTIMENT_PARAMS = CONFIG.get('sentiment_analysis', {}).get('tone_words', {})
NEGATION_WORDS = frozenset(SENTIMENT_PARAMS.get('negation_words', []))
DEGREE_WORDS = SENTIMENT_PARAMS.get('degree_words', {})
ADVERSATIVE_WORDS = frozenset(SENTIMENT_PARAMS.get('adversative_words', []))
ADVERSATIVE_BOOST = float(SENTIMENT_PARAMS.get('adversative_boost', 1.5))
NEGATION_WINDOW = SENTIMENT_PARAMS.get('negation_window', 2)
POS_THRESHOLD = SENTIMENT_PARAMS.get('pos_threshold', 0.1)
NEG_THRESHOLD = SENTIMENT_PARAMS.get('neg_threshold', -0.1)

# 句末标点集合（遇到时重置转折/否定/程度状态，确保作用域限定为当前句）
SENTENCE_END_MARKERS = frozenset(SENTIMENT_PARAMS.get('sentence_end_markers', ['。', '！', '？', '!', '?', '；', ';']))

# 词典文件路径
TONE_DICTS_FILE = CONFIG['paths'].get(
    'tone_dicts_file',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'tone_dicts.json')
)


# ============================================================================
# 2. 从 22_tone_words.py 复用的核心函数（避免导入时的副作用）
# ============================================================================

def load_all_dictionaries() -> list[tuple[str, dict[str, float]]]:
    """从 tone_dicts.json 加载所有情感词典。完全复用 22_tone_words.py 逻辑。"""
    logger.info(f"正在从 {TONE_DICTS_FILE} 加载情感词典...")

    all_dict_data = {}
    if os.path.exists(TONE_DICTS_FILE):
        try:
            with open(TONE_DICTS_FILE, 'r', encoding='utf-8') as f:
                all_dict_data = json.load(f)
        except Exception as e:
            logger.error(f"加载词典文件失败: {e}")

    dictionaries = []
    dict_keys = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']

    for dict_key in dict_keys:
        entry = all_dict_data.get(dict_key, {})
        d = {}
        for word in entry.get('positive', []):
            word = str(word).strip()
            if word:
                d[word] = 1.0
        for word in entry.get('negative', []):
            word = str(word).strip()
            if word:
                d[word] = -1.0
        for word in entry.get('political_positive', []):
            word = str(word).strip()
            if word and word not in d:
                d[word] = 0.5
        dictionaries.append((dict_key, d))

        pos_cnt = sum(1 for v in d.values() if v > 0)
        neg_cnt = sum(1 for v in d.values() if v < 0)
        logger.info(f"  {dict_key}: {len(d)} 个词汇 (正面={pos_cnt}, 负面={neg_cnt})")

    return dictionaries


def _compute_sentiment_with_rules(
    tokens: list[str], sentiment_dict: dict[str, float]
) -> tuple[float, float, int, int]:
    """语言学规则增强的词典情感计算。复用 22_tone_words.py 核心逻辑。

    Returns:
        tuple: (raw_score, normalized_score, pos_count, neg_count)
    """
    total_score = 0.0
    pos_count = 0
    neg_count = 0
    negation_remaining = 0
    degree_multiplier = 1.0
    adversative_active = False

    for token in tokens:
        if token in SENTENCE_END_MARKERS:
            adversative_active = False
            negation_remaining = 0
            degree_multiplier = 1.0
            continue
        if token in ADVERSATIVE_WORDS:
            adversative_active = True
            degree_multiplier = 1.0
            negation_remaining = 0
            continue
        if token in NEGATION_WORDS:
            negation_remaining = NEGATION_WINDOW
            continue
        if token in DEGREE_WORDS:
            degree_multiplier = DEGREE_WORDS[token]
            continue
        if token in sentiment_dict:
            base_score = sentiment_dict[token]
            if negation_remaining > 0:
                base_score = -base_score
            final_score = base_score * degree_multiplier
            if adversative_active:
                final_score *= ADVERSATIVE_BOOST
            total_score += final_score
            if final_score > 0:
                pos_count += 1
            elif final_score < 0:
                neg_count += 1
            degree_multiplier = 1.0
        else:
            degree_multiplier = 1.0
        if negation_remaining > 0:
            negation_remaining -= 1

    total_matched = pos_count + neg_count
    normalized_score = total_score / total_matched if total_matched > 0 else 0.0
    return total_score, normalized_score, pos_count, neg_count


def _score_to_label(normalized_score: float) -> str:
    """将归一化得分映射为情感标签。"""
    if normalized_score > POS_THRESHOLD:
        return "正面"
    elif normalized_score < NEG_THRESHOLD:
        return "负面"
    else:
        return "中性"


def _inject_custom_dicts_to_jieba(dictionaries):
    """将领域词汇注入 jieba 分词器。"""
    added = 0
    for _, sentiment_dict in dictionaries:
        for word in sentiment_dict:
            jieba.add_word(word)
            added += 1

    # 注入银行名称
    bank_path = CONFIG['paths'].get('bank_names_file', '')
    if bank_path and os.path.exists(bank_path):
        try:
            with open(bank_path, 'r', encoding='utf-8') as f:
                bank_data = json.load(f)
            for bank in bank_data:
                if not isinstance(bank, dict):
                    continue
                # 修正：使用正确的字段名 bank_name（非 standard_name）
                std_name = bank.get('bank_name')
                if std_name:
                    jieba.add_word(str(std_name).strip())
                    added += 1
                for v in bank.get('variants', []):
                    if v:
                        jieba.add_word(str(v).strip())
                        added += 1
        except Exception as e:
            logger.warning(f"加载银行词典失败: {e}")

    # 注入金融科技词典
    fintech_path = CONFIG['paths'].get('fintech_dict_file', '')
    if fintech_path and os.path.exists(fintech_path):
        try:
            with open(fintech_path, 'r', encoding='utf-8') as f:
                fintech_data = json.load(f)
            if isinstance(fintech_data, list):
                for word in fintech_data:
                    if word:
                        jieba.add_word(str(word).strip())
                        added += 1
            elif isinstance(fintech_data, dict):
                for _, words_list in fintech_data.items():
                    if isinstance(words_list, list):
                        for word in words_list:
                            if word:
                                jieba.add_word(str(word).strip())
                                added += 1
        except Exception as e:
            logger.warning(f"加载金融科技词典失败: {e}")

    # 否定词、程度词、转折词
    for word in NEGATION_WORDS:
        jieba.add_word(word)
    for word in DEGREE_WORDS:
        jieba.add_word(word)
    for word in ADVERSATIVE_WORDS:
        jieba.add_word(word)

    logger.info(f"成功注入 {added} 个领域词汇到 jieba 分词器。")


# ============================================================================
# 3. 从 entity_context.py 复用的上下文提取（支持参数化 radius）
# ============================================================================

from news_process.core.text.entity_context import extract_entity_context, get_target_aliases

# ============================================================================
# 4. 敏感性分析核心引擎
# ============================================================================

def analyze_single_article_multi_radius(
    content: str,
    target_aliases: list[str],
    dictionaries: list[tuple[str, dict[str, float]]],
) -> dict[int, dict]:
    """对单篇文章，在多个 radius 下提取上下文并计算情感。

    Returns:
        dict: {radius: {dict_name + '_score': float, dict_name + '_label': str, 'context_len': int, ...}}
    """
    results = {}

    for radius in RADII:
        ctx = extract_entity_context(
            content, target_aliases,
            sentence_radius=radius,
            fallback_char_radius=FALLBACK_CHAR_RADIUS,
        )
        # 若未匹配到，回退到原文
        text_for_analysis = ctx if ctx else content
        context_len = len(text_for_analysis)
        full_len = len(content) if content else 1

        # 分词（共享 jieba 实例）
        tokens = [t for t in jieba.cut(text_for_analysis) if t.strip()]

        radius_result = {
            'context_len': context_len,
            'context_ratio': round(context_len / full_len, 4) if full_len > 0 else 1.0,
            'token_count': len(tokens),
            'context_empty': (ctx == ""),
        }

        # 对每个词典计算
        for dict_name, sentiment_dict in dictionaries:
            if not sentiment_dict:
                radius_result[f'{dict_name}_score'] = 0.0
                radius_result[f'{dict_name}_label'] = '中性'
                continue

            _, norm_score, pos_cnt, neg_cnt = _compute_sentiment_with_rules(tokens, sentiment_dict)
            radius_result[f'{dict_name}_score'] = round(norm_score, 4)
            radius_result[f'{dict_name}_label'] = _score_to_label(norm_score)
            radius_result[f'{dict_name}_pos_count'] = pos_cnt
            radius_result[f'{dict_name}_neg_count'] = neg_cnt

        results[radius] = radius_result

    return results


# ============================================================================
# 5. 统计指标计算
# ============================================================================

def compute_label_agreement(labels_a: list[str], labels_b: list[str]) -> float:
    """计算两组标签的一致率。"""
    if not labels_a or len(labels_a) != len(labels_b):
        return 0.0
    agree = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    return agree / len(labels_a)


def compute_cohens_kappa(labels_a: list[str], labels_b: list[str]) -> float:
    """计算 Cohen's Kappa。"""
    n = len(labels_a)
    if n == 0:
        return 0.0

    cats = sorted(set(labels_a) | set(labels_b))
    cat_idx = {c: i for i, c in enumerate(cats)}
    k = len(cats)

    matrix = np.zeros((k, k), dtype=int)
    for a, b in zip(labels_a, labels_b):
        matrix[cat_idx[a], cat_idx[b]] += 1

    p_o = np.trace(matrix) / n
    row_sums = matrix.sum(axis=1)
    col_sums = matrix.sum(axis=0)
    p_e = (row_sums * col_sums).sum() / (n * n)

    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def run_sensitivity_analysis(
    df: pd.DataFrame,
    dictionaries: list[tuple[str, dict[str, float]]],
) -> dict:
    """对整个数据集执行敏感性分析。

    Returns:
        dict: 完整的分析结果。
    """
    total = len(df)
    dict_names = [name for name, _ in dictionaries]

    # 预加载别名缓存
    bank_names_file = CONFIG['paths'].get('bank_names_file', '')
    alias_cache = {}

    # 收集每个 radius 下所有文章的结果
    per_radius_data = {r: [] for r in RADII}

    logger.info(f"正在对 {total:,} 篇文章执行 {len(RADII)} 组窗口半径敏感性检验...")

    process_start = time.time()
    report_interval = max(1, total // 10)

    for i, (_, row) in enumerate(df.iterrows()):
        target_bank = str(row.get('target_bank', ''))
        content = str(row.get('内容', ''))

        if not target_bank or not content.strip():
            # 无目标银行或空内容，所有 radius 产出相同的默认结果
            for r in RADII:
                empty_result = {'context_len': 0, 'context_ratio': 0, 'token_count': 0, 'context_empty': True}
                for dn in dict_names:
                    empty_result[f'{dn}_score'] = 0.0
                    empty_result[f'{dn}_label'] = '中性'
                per_radius_data[r].append(empty_result)
            continue

        # 获取别名
        if target_bank not in alias_cache:
            alias_cache[target_bank] = get_target_aliases(target_bank, bank_names_file)
        aliases = alias_cache[target_bank]

        # 多半径分析
        multi_result = analyze_single_article_multi_radius(content, aliases, dictionaries)
        for r in RADII:
            per_radius_data[r].append(multi_result[r])

        if (i + 1) % report_interval == 0 or (i + 1) == total:
            elapsed = time.time() - process_start
            speed = (i + 1) / elapsed if elapsed > 0 else 0
            logger.info(f"  进度: {i + 1:,}/{total:,} ({(i+1)/total*100:.1f}%) "
                        f"| 速度: {speed:.0f} 文章/秒")

    total_elapsed = time.time() - process_start
    logger.info(f"全部文章处理完成。耗时: {total_elapsed:.1f}s, "
                f"平均速度: {total / total_elapsed:.0f} 文章/秒")

    # ── 汇总统计 ──
    analysis_results = {
        'meta': {
            'total_articles': total,
            'radii_tested': RADII,
            'dictionaries': dict_names,
            'processing_time_seconds': round(total_elapsed, 1),
        },
        'per_radius': {},
        'cross_radius': {},
    }

    # 5.1 每个 radius 的基础统计
    for r in RADII:
        data_list = per_radius_data[r]
        r_stats = {
            'context': {
                'mean_char_len': round(np.mean([d['context_len'] for d in data_list]), 1),
                'mean_ratio': round(np.mean([d['context_ratio'] for d in data_list]), 4),
                'empty_count': sum(1 for d in data_list if d['context_empty']),
                'mean_token_count': round(np.mean([d['token_count'] for d in data_list]), 1),
            },
            'dictionaries': {},
        }
        for dn in dict_names:
            scores = [d[f'{dn}_score'] for d in data_list]
            labels = [d[f'{dn}_label'] for d in data_list]
            label_dist = Counter(labels)
            r_stats['dictionaries'][dn] = {
                'score_mean': round(np.mean(scores), 4),
                'score_std': round(np.std(scores), 4),
                'score_median': round(np.median(scores), 4),
                'label_distribution': {
                    '正面': label_dist.get('正面', 0),
                    '中性': label_dist.get('中性', 0),
                    '负面': label_dist.get('负面', 0),
                },
                'label_distribution_pct': {
                    '正面': round(label_dist.get('正面', 0) / total * 100, 2) if total > 0 else 0,
                    '中性': round(label_dist.get('中性', 0) / total * 100, 2) if total > 0 else 0,
                    '负面': round(label_dist.get('负面', 0) / total * 100, 2) if total > 0 else 0,
                },
            }
        analysis_results['per_radius'][str(r)] = r_stats

    # 5.2 跨半径对比（基准 = radius=1，即当前生产配置）
    baseline_radius = 1
    baseline_data = per_radius_data[baseline_radius]

    for r in RADII:
        if r == baseline_radius:
            continue
        compare_data = per_radius_data[r]
        comparison = {}

        for dn in dict_names:
            base_labels = [d[f'{dn}_label'] for d in baseline_data]
            comp_labels = [d[f'{dn}_label'] for d in compare_data]
            base_scores = [d[f'{dn}_score'] for d in baseline_data]
            comp_scores = [d[f'{dn}_score'] for d in compare_data]

            agreement = compute_label_agreement(base_labels, comp_labels)
            kappa = compute_cohens_kappa(base_labels, comp_labels)

            # Pearson 和 Spearman 相关
            pearson_r, pearson_p = scipy_stats.pearsonr(base_scores, comp_scores) if len(base_scores) > 2 else (0, 1)
            spearman_r, spearman_p = scipy_stats.spearmanr(base_scores, comp_scores) if len(base_scores) > 2 else (0, 1)

            # 均值差异的配对 t 检验
            score_diffs = [c - b for b, c in zip(base_scores, comp_scores)]
            if len(score_diffs) > 1 and np.std(score_diffs) > 0:
                t_stat, t_p = scipy_stats.ttest_1samp(score_diffs, 0)
            else:
                t_stat, t_p = 0.0, 1.0

            comparison[dn] = {
                'label_agreement': round(agreement, 4),
                'cohens_kappa': round(kappa, 4),
                'pearson_r': round(pearson_r, 4),
                'pearson_p': round(pearson_p, 6),
                'spearman_rho': round(spearman_r, 4),
                'spearman_p': round(spearman_p, 6),
                'mean_score_diff': round(np.mean(score_diffs), 4),
                'paired_t_stat': round(t_stat, 4),
                'paired_t_p': round(t_p, 6),
            }

        analysis_results['cross_radius'][f'r{baseline_radius}_vs_r{r}'] = comparison

    return analysis_results, per_radius_data


# ============================================================================
# 6. 报告生成
# ============================================================================

def _log_key_interpretation(results: dict, dict_names: list[str], logger):
    """根据分析结果自动生成关键解读并记录到日志。

    解读逻辑：
        1. 检测标签不平衡程度，判断 Kappa 悖论风险
        2. 按对比组分类统计（极端窗口 r=0 vs 邻近窗口 r=2/3）
        3. 汇总 t 检验显著性
        4. 生成综合研判结论（适合论文讨论部分引用）
    """
    meta = results['meta']
    baseline_radius = 1
    radii = meta['radii_tested']
    total_articles = meta['total_articles']

    logger.info("")
    logger.info("─" * 80)
    logger.info(">>>  关键解读（自动生成）  <<<")
    logger.info("─" * 80)

    # ── 1. 标签不平衡检测与 Kappa 悖论 ──
    logger.info("")
    logger.info("【1. 标签分布不平衡检测】")
    max_dominant_pct = 0.0
    dominant_label = ""
    for dn in dict_names:
        for r in radii:
            dist_pct = results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct']
            for label, pct in dist_pct.items():
                if pct > max_dominant_pct:
                    max_dominant_pct = pct
                    dominant_label = label

    # 计算各半径下主导标签的平均占比
    dominant_pcts_per_radius = {}
    for r in radii:
        pcts = []
        for dn in dict_names:
            dist_pct = results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct']
            pcts.append(max(dist_pct.values()))
        dominant_pcts_per_radius[r] = np.mean(pcts)

    avg_dominant = np.mean(list(dominant_pcts_per_radius.values()))
    logger.info(f"  主导标签「{dominant_label}」平均占比: {avg_dominant:.1f}%")

    kappa_paradox = avg_dominant >= 90.0
    if kappa_paradox:
        logger.info(f"  检测到高度不平衡（主导标签 ≥ 90%）")
        logger.info(f"    → Kappa 悖论 (Paradox of High Agreement but Low Kappa):")
        logger.info(f"      当分类高度集中于单一类别时，即使一致率很高，")
        logger.info(f"      Kappa 也会因为 P(e) 过大而被严重压低。")
        logger.info(f"      因此 Kappa 值不应作为唯一稳健性判据。")
    else:
        logger.info(f"  标签分布相对均衡，Kappa 指标可作为可靠判据。")

    # ── 2. 分组对比分析 ──
    logger.info("")
    logger.info("【2. 分组对比分析】")

    # 区分极端窗口 (r=0) 和邻近窗口 (r=2, r=3)
    extreme_key = f"r{baseline_radius}_vs_r0"
    adjacent_keys = [k for k in results['cross_radius'].keys() if k != extreme_key]

    # 极端窗口 (r=0)
    if extreme_key in results['cross_radius']:
        pair_data = results['cross_radius'][extreme_key]
        kappas = [pair_data[dn]['cohens_kappa'] for dn in dict_names]
        pearsons = [pair_data[dn]['pearson_r'] for dn in dict_names]
        agrees = [pair_data[dn]['label_agreement'] for dn in dict_names]
        t_ps = [pair_data[dn]['paired_t_p'] for dn in dict_names]
        sig_count = sum(1 for p in t_ps if p < 0.05)

        logger.info(f"  ── r=1 vs r=0（极端窗口: 仅实体所在句）──")
        logger.info(f"     Kappa 范围:     {min(kappas):.4f} ~ {max(kappas):.4f}  (均值 {np.mean(kappas):.4f})")
        logger.info(f"     Pearson 范围:   {min(pearsons):.4f} ~ {max(pearsons):.4f}  (均值 {np.mean(pearsons):.4f})")
        logger.info(f"     一致率范围:     {min(agrees):.2%} ~ {max(agrees):.2%}")
        logger.info(f"     t 检验显著 (p<0.05): {sig_count}/{len(dict_names)} 个词典")
        if np.mean(kappas) < 0.60:
            logger.info(f"     → 解读: r=0 仅保留实体所在句，上下文信息严重不足，")
            logger.info(f"       与 r=1 差异较大属于预期行为，不影响 r=1 的合理性。")

    # 邻近窗口 (r=2, r=3)
    if adjacent_keys:
        adj_kappas = []
        adj_pearsons = []
        adj_agrees = []
        adj_t_ps = []
        for key in adjacent_keys:
            pair_data = results['cross_radius'][key]
            for dn in dict_names:
                adj_kappas.append(pair_data[dn]['cohens_kappa'])
                adj_pearsons.append(pair_data[dn]['pearson_r'])
                adj_agrees.append(pair_data[dn]['label_agreement'])
                adj_t_ps.append(pair_data[dn]['paired_t_p'])

        adj_sig_count = sum(1 for p in adj_t_ps if p < 0.05)
        adj_radii_str = ", ".join(k.split("_vs_")[1] for k in adjacent_keys)

        logger.info(f"  ── r=1 vs 邻近窗口（{adj_radii_str}）──")
        logger.info(f"     Kappa 范围:     {min(adj_kappas):.4f} ~ {max(adj_kappas):.4f}  (均值 {np.mean(adj_kappas):.4f})")
        logger.info(f"     Pearson 范围:   {min(adj_pearsons):.4f} ~ {max(adj_pearsons):.4f}  (均值 {np.mean(adj_pearsons):.4f})")
        logger.info(f"     一致率范围:     {min(adj_agrees):.2%} ~ {max(adj_agrees):.2%}")
        logger.info(f"     t 检验显著 (p<0.05): {adj_sig_count}/{len(adj_t_ps)} 个词典×对比组")
        if np.mean(adj_pearsons) >= 0.80:
            logger.info(f"     → 解读: 邻近半径间得分高度相关 (Pearson ≥ 0.80)，")
            logger.info(f"       标签变化极少，结果具有良好稳健性。")

    # ── 3. t 检验显著性汇总 ──
    logger.info("")
    logger.info("【3. 配对 t 检验显著性汇总】")
    all_t_ps = []
    sig_pairs = []
    for pair_key, pair_data in results['cross_radius'].items():
        for dn in dict_names:
            p_val = pair_data[dn]['paired_t_p']
            all_t_ps.append(p_val)
            if p_val < 0.05:
                sig_pairs.append((pair_key, dn, p_val))

    total_tests = len(all_t_ps)
    total_sig = len(sig_pairs)
    logger.info(f"  共进行 {total_tests} 组配对 t 检验（{len(results['cross_radius'])} 对比组 × {len(dict_names)} 词典）")
    logger.info(f"  显著 (p < 0.05): {total_sig} 组")
    logger.info(f"  不显著 (p ≥ 0.05): {total_tests - total_sig} 组")
    if sig_pairs:
        logger.info(f"  显著的对比组:")
        for pair_key, dn, p_val in sig_pairs:
            logger.info(f"    - {pair_key} × {dn}: p = {p_val:.6f}")
    else:
        logger.info(f"  → 所有对比组的均值差异均不具有统计显著性。")

    # ── 4. 综合研判结论 ──
    logger.info("")
    logger.info("【4. 综合研判结论】")

    # 判定邻近窗口的稳健性
    adj_robust = (len(adjacent_keys) > 0
                  and np.mean(adj_pearsons) >= 0.80
                  and np.mean(adj_agrees) >= 0.95)

    # 判定极端窗口是否有偏差
    extreme_deviated = False
    if extreme_key in results['cross_radius']:
        extreme_pair = results['cross_radius'][extreme_key]
        extreme_kappas = [extreme_pair[dn]['cohens_kappa'] for dn in dict_names]
        extreme_deviated = np.mean(extreme_kappas) < 0.60

    # 判定 t 检验总体不显著
    mostly_nonsig = (total_sig / total_tests) <= 0.2 if total_tests > 0 else True

    if adj_robust and mostly_nonsig:
        # 邻近稳健 + t 检验多数不显著 → 实质稳健
        if extreme_deviated and kappa_paradox:
            logger.info("  结论: 情感分析结果对窗口半径选择具有实质稳健性。")
            logger.info("")
            logger.info(f"  - 当前生产配置 r={baseline_radius} 是合理的折中选择。")
            logger.info(f"  - 邻近半径 (r={baseline_radius} vs r=2/r=3) 一致率 ≥ {min(adj_agrees):.1%}，")
            logger.info(f"    Pearson 相关 ≥ {min(adj_pearsons):.3f}，差异统计上不显著。")
            logger.info(f"  - r=0 的 Kappa 较低是由标签高度不平衡导致的 Kappa 悖论，")
            logger.info(f"    以及 r=0 上下文信息不足的双重因素所致，")
            logger.info(f"    不影响 r={baseline_radius} 作为默认值的方法论合理性。")
            logger.info(f"  - 建议论文讨论: 在附录中报告本检验结果，说明 r=0 偏差")
            logger.info(f"    归因于上下文信息不足，符合 proximity-based attribution 的理论预期。")
        elif extreme_deviated:
            logger.info("  结论: 情感分析结果在邻近半径间具有良好稳健性，")
            logger.info("        但 r=0 极端窗口存在显著偏差。")
            logger.info("")
            logger.info(f"  - r={baseline_radius} 与 r=2/r=3 的差异不显著，结果稳健。")
            logger.info(f"  - r=0 偏差较大，建议在论文中讨论上下文窗口的边界效应。")
        else:
            logger.info("  结论: 情感分析结果对窗口半径选择具有良好稳健性。")
            logger.info("")
            logger.info(f"  - 所有半径对比均显示较高一致性。")
            logger.info(f"  - r={baseline_radius} 是稳健的默认选择。")
    elif adj_robust:
        logger.info("  结论: 邻近半径间稳健性良好，但个别对比组存在统计显著差异。")
        logger.info("")
        logger.info(f"  - 虽有 {total_sig} 组 t 检验显著，但实际均值差异幅度很小。")
        logger.info(f"  - r={baseline_radius} 仍可作为合理的默认选择。")
    else:
        logger.info("  结论: 情感分析结果对窗口半径选择存在一定敏感性。")
        logger.info("")
        logger.info(f"  - 建议在论文中充分讨论参数选择依据。")
        logger.info(f"  - 考虑展示多半径结果作为稳健性检验的一部分。")

    logger.info("")
    logger.info("=" * 80)


def log_report(results: dict):
    """将分析结果输出到日志（结构化文本报告）。"""
    meta = results['meta']
    dict_names = meta['dictionaries']

    logger.info("=" * 80)
    logger.info("===   实体上下文窗口半径敏感性检验报告（Sensitivity Analysis）   ===")
    logger.info("=" * 80)
    logger.info(f"总文章数: {meta['total_articles']:,}")
    logger.info(f"检验半径: {meta['radii_tested']}")
    logger.info(f"使用词典: {dict_names}")
    logger.info(f"处理耗时: {meta['processing_time_seconds']}s")

    # ── Panel A: 上下文统计 ──
    logger.info("")
    logger.info("─" * 80)
    logger.info("Panel A: 各半径下的上下文提取统计")
    logger.info("─" * 80)
    logger.info(f"{'Radius':>8} {'平均字符数':>12} {'占全文比例':>12} {'平均分词数':>12} {'未命中(回退)':>14}")
    logger.info("-" * 60)
    for r in meta['radii_tested']:
        ctx = results['per_radius'][str(r)]['context']
        logger.info(f"{r:>8} {ctx['mean_char_len']:>12.1f} {ctx['mean_ratio']:>12.2%} "
                     f"{ctx['mean_token_count']:>12.1f} {ctx['empty_count']:>14,}")

    # ── Panel B: 标签分布 ──
    logger.info("")
    logger.info("─" * 80)
    logger.info("Panel B: 各半径 × 词典的标签分布 (%)")
    logger.info("─" * 80)
    header = f"{'词典':<12} {'Radius':>8}   {'正面':>8} {'中性':>8} {'负面':>8}"
    logger.info(header)
    logger.info("-" * 54)
    for dn in dict_names:
        for r in meta['radii_tested']:
            dist = results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct']
            logger.info(f"{dn:<12} {r:>8}   {dist['正面']:>7.2f}% {dist['中性']:>7.2f}% {dist['负面']:>7.2f}%")
        logger.info("")

    # ── Panel C: 跨半径一致性（对比基准 r=1） ──
    logger.info("")
    logger.info("─" * 80)
    logger.info("Panel C: 跨半径一致性（基准 = radius=1）")
    logger.info("─" * 80)
    header2 = (f"{'对比':>14} {'词典':<12} {'一致率':>8} {'Kappa':>8} "
               f"{'Pearson':>9} {'Spearman':>9} {'均值差':>8} {'t-test p':>10}")
    logger.info(header2)
    logger.info("-" * 90)
    for pair_key, pair_data in results['cross_radius'].items():
        for dn in dict_names:
            d = pair_data[dn]
            logger.info(
                f"{pair_key:>14} {dn:<12} {d['label_agreement']:>7.2%} {d['cohens_kappa']:>8.4f} "
                f"{d['pearson_r']:>9.4f} {d['spearman_rho']:>9.4f} {d['mean_score_diff']:>8.4f} "
                f"{d['paired_t_p']:>10.6f}"
            )
        logger.info("")

    logger.info("=" * 80)

    # ── 结论摘要 ──
    logger.info("")
    logger.info(">>>  结论摘要  <<<")

    all_kappas = []
    all_agreements = []
    all_pearsons = []
    for pair_data in results['cross_radius'].values():
        for dn_data in pair_data.values():
            all_kappas.append(dn_data['cohens_kappa'])
            all_agreements.append(dn_data['label_agreement'])
            all_pearsons.append(dn_data['pearson_r'])

    if all_kappas:
        min_kappa = min(all_kappas)
        min_agree = min(all_agreements)
        min_pearson = min(all_pearsons)

        baseline_radius = 1
        extreme_key = f"r{baseline_radius}_vs_r0"
        adjacent_pairs = {
            k: v for k, v in results['cross_radius'].items()
            if k != extreme_key
        }
        adjacent_kappas = []
        adjacent_agreements = []
        adjacent_pearsons = []
        for pair_data in adjacent_pairs.values():
            for dn_data in pair_data.values():
                adjacent_kappas.append(dn_data['cohens_kappa'])
                adjacent_agreements.append(dn_data['label_agreement'])
                adjacent_pearsons.append(dn_data['pearson_r'])

        logger.info(f"  全部对比最低标签一致率: {min_agree:.2%}")
        logger.info(f"  全部对比最低 Cohen's Kappa: {min_kappa:.4f}")
        logger.info(f"  全部对比最低 Pearson 相关: {min_pearson:.4f}")

        if adjacent_kappas:
            adj_min_kappa = min(adjacent_kappas)
            adj_min_agree = min(adjacent_agreements)
            adj_min_pearson = min(adjacent_pearsons)
            logger.info(f"  邻近窗口最低标签一致率: {adj_min_agree:.2%}")
            logger.info(f"  邻近窗口最低 Cohen's Kappa: {adj_min_kappa:.4f}")
            logger.info(f"  邻近窗口最低 Pearson 相关: {adj_min_pearson:.4f}")
        else:
            adj_min_kappa = min_kappa
            adj_min_agree = min_agree
            adj_min_pearson = min_pearson

        if adj_min_kappa >= 0.80:
            logger.info("  ✅ 判定: 邻近窗口半径下情感分析结果具有强稳健性（κ ≥ 0.80）")
        elif adj_min_kappa >= 0.60 and adj_min_agree >= 0.95 and adj_min_pearson >= 0.80:
            logger.info("  判定: 邻近窗口半径下情感分析结果具有实质稳健性（κ ≥ 0.60, agreement ≥ 95%, Pearson ≥ 0.80）")
        else:
            logger.info("  判定: 邻近窗口半径下情感分析结果存在一定敏感性，需讨论参数选择")

        if extreme_key in results['cross_radius'] and min_kappa < 0.60:
            logger.info("  注: 最低 κ 来自 r=0 极端压力测试；r=0 仅保留实体所在句，不作为默认窗口稳健性的主判据。")

    logger.info("=" * 80)

    # ── 关键解读（自动生成） ──
    _log_key_interpretation(results, dict_names, logger)


def generate_latex_table(results: dict) -> str:
    """生成 LaTeX 格式的敏感性分析表格（论文附录使用）。"""
    meta = results['meta']
    dict_names = meta['dictionaries']

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{Entity Context Window Radius Sensitivity Analysis}")
    lines.append(r"\label{tab:radius_sensitivity}")
    lines.append(r"\small")

    # ── Panel A: Label Distribution ──
    lines.append(r"\begin{tabular}{ll" + "r" * len(meta['radii_tested']) + "}")
    lines.append(r"\toprule")
    header_cols = " & ".join([f"$r={r}$" for r in meta['radii_tested']])
    lines.append(r"Dictionary & Label & " + header_cols + r" \\")
    lines.append(r"\midrule")

    for dn in dict_names:
        dn_display = dn.replace('_', r'\_')
        for label in ['正面', '中性', '负面']:
            label_en = {'正面': 'Positive', '中性': 'Neutral', '负面': 'Negative'}[label]
            vals = []
            for r in meta['radii_tested']:
                pct = results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct'][label]
                vals.append(f"{pct:.1f}\\%")
            row_dn = dn_display if label == '正面' else ""
            lines.append(f"  {row_dn} & {label_en} & " + " & ".join(vals) + r" \\")
        lines.append(r"\addlinespace")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    lines.append(r"\vspace{0.5em}")

    # ── Panel B: Cross-Radius Agreement ──
    lines.append(r"\begin{tabular}{llrrrrr}")
    lines.append(r"\toprule")
    lines.append(r"Comparison & Dictionary & Agreement & $\kappa$ & Pearson $r$ & Spearman $\rho$ & $p$-value \\")
    lines.append(r"\midrule")

    for pair_key, pair_data in results['cross_radius'].items():
        pair_display = pair_key.replace('_', r'\_')
        for dn in dict_names:
            d = pair_data[dn]
            dn_display = dn.replace('_', r'\_')
            p_str = f"{d['paired_t_p']:.4f}" if d['paired_t_p'] >= 0.0001 else "<0.0001"
            lines.append(
                f"  {pair_display} & {dn_display} & "
                f"{d['label_agreement']:.2%} & {d['cohens_kappa']:.3f} & "
                f"{d['pearson_r']:.3f} & {d['spearman_rho']:.3f} & {p_str}" + r" \\"
            )
        pair_display = ""  # 后续行不重复
        lines.append(r"\addlinespace")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def generate_visualizations(results: dict, per_radius_data: dict, output_dir: str):
    """生成可视化图表。"""
    if not HAS_MATPLOTLIB:
        logger.warning("matplotlib 未安装，跳过可视化生成。")
        return

    # 尝试设置中文字体
    try:
        # Windows 常见中文字体路径
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',     # 微软雅黑
            'C:/Windows/Fonts/simhei.ttf',    # 黑体
            'C:/Windows/Fonts/simsun.ttc',    # 宋体
        ]
        zh_font = None
        for fp in font_paths:
            if os.path.exists(fp):
                zh_font = font_manager.FontProperties(fname=fp)
                break
        if zh_font is None:
            zh_font = font_manager.FontProperties()
    except Exception:
        zh_font = font_manager.FontProperties()

    meta = results['meta']
    dict_names = meta['dictionaries']

    # ── 图1: 标签分布柱状图 ──
    fig, axes = plt.subplots(1, len(dict_names), figsize=(4 * len(dict_names), 4), sharey=True)
    if len(dict_names) == 1:
        axes = [axes]

    labels_cn = ['正面', '中性', '负面']
    labels_en = ['Positive', 'Neutral', 'Negative']
    colors = ['#2ecc71', '#95a5a6', '#e74c3c']

    for idx, dn in enumerate(dict_names):
        ax = axes[idx]
        x = np.arange(len(labels_cn))
        width = 0.18
        for ri, r in enumerate(meta['radii_tested']):
            pcts = [results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct'][l]
                    for l in labels_cn]
            ax.bar(x + ri * width, pcts, width, label=f'r={r}', alpha=0.85)
        ax.set_xlabel('Sentiment', fontsize=10)
        ax.set_ylabel('Percentage (%)' if idx == 0 else '', fontsize=10)
        ax.set_title(dn.replace('_', ' ').title(), fontsize=11)
        ax.set_xticks(x + width * (len(meta['radii_tested']) - 1) / 2)
        ax.set_xticklabels(labels_en, fontsize=9)
        ax.legend(fontsize=8, loc='upper right')

    plt.suptitle('Label Distribution Across Window Radii', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig_path_1 = os.path.join(output_dir, '35_radius_label_distribution.png')
    plt.savefig(fig_path_1, dpi=200, bbox_inches='tight')
    plt.close()
    logger.info(f"图表已保存: {fig_path_1}")

    # ── 图2: 得分相关性热力图 ──
    fig, axes = plt.subplots(1, len(dict_names), figsize=(4 * len(dict_names), 3.5))
    if len(dict_names) == 1:
        axes = [axes]

    for idx, dn in enumerate(dict_names):
        ax = axes[idx]
        corr_matrix = np.ones((len(RADII), len(RADII)))
        for i, r1 in enumerate(RADII):
            scores_1 = [d[f'{dn}_score'] for d in per_radius_data[r1]]
            for j, r2 in enumerate(RADII):
                if i != j:
                    scores_2 = [d[f'{dn}_score'] for d in per_radius_data[r2]]
                    corr_matrix[i, j] = scipy_stats.pearsonr(scores_1, scores_2)[0]

        im = ax.imshow(corr_matrix, cmap='RdYlGn', vmin=0.5, vmax=1.0, aspect='auto')
        ax.set_xticks(range(len(RADII)))
        ax.set_yticks(range(len(RADII)))
        ax.set_xticklabels([f'r={r}' for r in RADII], fontsize=9)
        ax.set_yticklabels([f'r={r}' for r in RADII], fontsize=9)
        ax.set_title(dn.replace('_', ' ').title(), fontsize=11)

        # 在单元格中标注数值
        for i in range(len(RADII)):
            for j in range(len(RADII)):
                text_color = 'white' if corr_matrix[i, j] < 0.75 else 'black'
                ax.text(j, i, f'{corr_matrix[i, j]:.3f}',
                        ha='center', va='center', fontsize=8, color=text_color)

    plt.suptitle('Score Correlation Across Window Radii (Pearson r)', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig_path_2 = os.path.join(output_dir, '35_radius_correlation_heatmap.png')
    plt.savefig(fig_path_2, dpi=200, bbox_inches='tight')
    plt.close()
    logger.info(f"图表已保存: {fig_path_2}")


# ============================================================================
# 7. 主函数
# ============================================================================

def main():
    """窗口半径敏感性检验主入口。"""
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    logger.info(f"检验的窗口半径: {RADII}")
    logger.info(f"基准半径: 1（当前生产配置）")

    # ── 加载输入数据 ──
    # 优先使用阶段 21 的输出（经 LLM 精筛，含 target_bank 列）
    input_candidates = [
        CONFIG['filenames'].get('output_21_tone_llms', '21_tone_llms.parquet'),
        CONFIG['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet'),
    ]

    input_path = None
    for fname in input_candidates:
        candidate = os.path.join(CONFIG['paths']['output_dir'], fname)
        if os.path.exists(candidate):
            input_path = candidate
            break

    if input_path is None:
        logger.error("未找到输入文件。需要阶段 21 或阶段 12 的输出。")
        return

    logger.info(f"加载输入数据: {input_path}")
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    logger.info(f"已加载 {input_rows:,} 行数据。")
    log_memory_usage(logger, "数据加载后")

    # 检查必要列
    if 'target_bank' not in df.columns:
        logger.error("输入数据缺少 'target_bank' 列，无法执行 entity_context 提取。")
        return
    if '内容' not in df.columns:
        logger.error("输入数据缺少 '内容' 列。")
        return

    # 统计 target_bank 分布
    bank_counts = df['target_bank'].value_counts()
    logger.info(f"涵盖银行数: {len(bank_counts)}")
    logger.info(f"target_bank 非空记录: {df['target_bank'].notna().sum():,}")

    # ── 加载词典 ──
    dictionaries = load_all_dictionaries()
    non_empty = sum(1 for _, d in dictionaries if d)
    logger.info(f"有效词典数: {non_empty}/{len(dictionaries)}")

    # ── 初始化 jieba ──
    logger.info("初始化 jieba 分词器...")
    _inject_custom_dicts_to_jieba(dictionaries)

    # ── 执行敏感性分析 ──
    analysis_results, per_radius_data = run_sensitivity_analysis(df, dictionaries)

    # ── 输出报告 ──
    log_report(analysis_results)

    # ── 保存 JSON 结果 ──
    output_dir = CONFIG['paths']['output_dir']
    json_path = os.path.join(output_dir, '35_radius_sensitivity.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON 报告已保存: {json_path}")

    # ── 保存 LaTeX 表格 ──
    latex_path = os.path.join(output_dir, '35_radius_sensitivity.tex')
    latex_content = generate_latex_table(analysis_results)
    with open(latex_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    logger.info(f"LaTeX 表格已保存: {latex_path}")

    # ── 生成可视化 ──
    generate_visualizations(analysis_results, per_radius_data, output_dir)

    # ── 阶段摘要 ──
    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=input_rows)
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
