"""
34_tone_validation.py — 阶段34：情感分析三角验证与报告生成
=====================================================

功能：
    对三种情感分析方法（词典法/BERT/LLM）进行系统性交叉验证，
    以确保情感度量的构建效度符合国际顶级期刊标准。

    验证内容：
    ┌────────────────────────────────────────────────────────────┐
    │ 一、内部一致性 (Within-Method Consistency)                   │
    │    1.1 五词典间 Spearman 相关矩阵                            │
    │    1.2 五 BERT 模型间 Spearman 相关矩阵                      │
    │    1.3 Cronbach's Alpha 内部一致性系数                       │
    │                                                            │
    │ 二、跨方法一致性 (Cross-Method Consistency)                  │
    │    2.1 词典法综合 vs BERT 综合 vs LLM 综合                   │
    │        → Spearman / Pearson 相关系数                        │
    │    2.2 标签一致性（多数投票对比）                              │
    │    2.3 全方法 × 全模型的交叉相关热力图                        │
    │                                                            │
    │ 三、合成策略与投票机制                                       │
    │    3.1 多数投票法 (Majority Voting)                         │
    │    3.2 加权平均法 (Weighted Average)                        │
    │                                                            │
    │ 四、分层稳健性分析                                           │
    │    4.1 按新闻长度分层                                        │
    │    4.2 按时间段分层                                          │
    │                                                            │
    │ 4.5 LLM 概率诊断 (Chiu & Hung 2024 M3 降级适配)             │
    │    4.5a LLM 类别偏向分析 (chi-square + Jensen-Shannon)       │
    │    4.5b 置信度校准诊断 (ECE / 降级: 描述性统计)               │
    │                                                            │
    │ 五、人工验证样本生成                                         │
    │    5.1 一致样本随机抽取                                      │
    │    5.2 不一致样本邻域加密抽取                                │
    └────────────────────────────────────────────────────────────┘

    学术依据：
      - Loughran & McDonald (2016, JAR 54(4):1187-1230): 多度量方法间的相关性是构建效度的核心证据
      - Cronbach (1951, Psychometrika 16(3):297-334): 内部一致性系数 α ≥ 0.70 可接受
      - Chiu & Hung (2024, IRFA): Dirichlet 不确定性估计揭示 LLM 类别偏向
      - Carlson & Burbano (2026, SMJ 47(3):699-725): LLM 注释应报告 model certainty
      - Guo et al. (2017, ICML): Expected Calibration Error (ECE) 校准诊断

输入：
    阶段 21/22/23 输出的最终 Parquet 文件（包含全部词典/BERT/LLM 列）

输出：
    验证报告（CSV + PNG + LaTeX）+ 人工验证样本 Excel
"""

import os
import time
import json
import numpy as np
import pandas as pd
from collections import Counter
from utils.helpers import load_config, setup_logging, log_memory_usage, log_stage_summary

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "34_tone_validation"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# ============================================================================
# 2. 列名自动发现
# ============================================================================

def discover_sentiment_columns(df: pd.DataFrame, track_suffix: str = '') -> dict:
    """自动发现 DataFrame 中指定轨道的情感分析输出列。

    通过列名后缀模式匹配，自动识别词典法、BERT、LLM 各方法的输出列。

    Args:
        df:           DataFrame
        track_suffix: 轨道后缀，如 '_full' 或 '_ctx'。为空则匹配无后缀列(向后兼容)。

    Returns:
        dict: {
            'words': {dict_name: {'score': col, 'label': col}},
            'bert':  {short_name: {'label': col, 'probs': {label_name: col}}},
            'llm':   {short_name: {'sentiment': col, 'confidence': col}},
        }
    """
    columns = list(df.columns)
    result = {'words': {}, 'bert': {}, 'llm': {}}

    # 词典法列: {name}_score{track_suffix}, {name}_label{track_suffix}
    score_suffix = f'_score{track_suffix}'
    label_suffix = f'_label{track_suffix}'
    sentiment_suffix = f'_sentiment{track_suffix}'
    confidence_suffix = f'_confidence{track_suffix}'

    # 词典法：找 _score{track_suffix} 列，区分等权 vs IDF
    result['words_idf'] = {}  # IDF 加权词典（稳健性检验，独立分组）

    for col in columns:
        if col.endswith(score_suffix):
            dict_name = col[:-len(score_suffix)]
            label_col = f'{dict_name}{label_suffix}'
            if label_col in columns:
                if '_idf' in dict_name:
                    # IDF 列 → 单独分组（不与等权混入 Cronbach's α）
                    result['words_idf'][dict_name] = {
                        'score': col,
                        'label': label_col,
                    }
                else:
                    result['words'][dict_name] = {
                        'score': col,
                        'label': label_col,
                    }

    # LLM 法：找 _sentiment{track_suffix} 列
    for col in columns:
        if col.endswith(sentiment_suffix):
            short_name = col[:-len(sentiment_suffix)]
            # 置信度列查找：21_tone_llms.py 输出格式为
            # {short}_sentiment_confidence{track}，优先匹配此模式；
            # 回退到 {short}_confidence{track} 以兼容历史数据
            conf_col_primary = f'{short_name}_sentiment{confidence_suffix}'
            conf_col_fallback = f'{short_name}{confidence_suffix}'
            if conf_col_primary in columns:
                conf_col = conf_col_primary
            elif conf_col_fallback in columns:
                conf_col = conf_col_fallback
            else:
                conf_col = None
            result['llm'][short_name] = {
                'sentiment': col,
                'confidence': conf_col,
            }

    # BERT 法：找 _label{track_suffix} 列（排除已被词典法识别的；排除 LLM 的）
    words_names = set(result['words'].keys())
    llm_names = set(result['llm'].keys())
    for col in columns:
        if col.endswith(label_suffix):
            name = col[:-len(label_suffix)]
            if name not in words_names and name not in llm_names:
                probs = {}
                for c in columns:
                    # 查找同 track 的概率列：{name}_{prob_label}{track_suffix}
                    if c.startswith(f'{name}_') and c.endswith(track_suffix) and c != col:
                        # 去除前缀和后缀得到 prob_label
                        prob_label = c[len(f'{name}_'):]
                        if track_suffix:
                            prob_label = prob_label[:-len(track_suffix)]
                        if prob_label not in ('label', 'score', 'sentiment', 'confidence'):
                            probs[prob_label] = c
                result['bert'][name] = {
                    'label': col,
                    'probs': probs,
                }

    return result


# ============================================================================
# 3. 标签数值化
# ============================================================================

SENTIMENT_MAP = {'正面': 1, '中性': 0, '负面': -1}
SENTIMENT_MAP_REVERSE = {1: '正面', 0: '中性', -1: '负面'}


def label_to_numeric(series: pd.Series) -> pd.Series:
    """将情感标签转为数值：正面=+1, 中性=0, 负面=-1。"""
    return series.map(SENTIMENT_MAP).fillna(0).astype(float)


# ============================================================================
# 4. 统计指标计算
# ============================================================================

def compute_spearman_matrix(df_numeric: pd.DataFrame) -> pd.DataFrame:
    """计算 Spearman 秩相关矩阵。

    使用 pandas 内置 `DataFrame.corr(method='spearman')` 计算，
    正确处理并列排名（ties），比手写简化公式更精确。

    Args:
        df_numeric: 各列为数值型的 DataFrame。

    Returns:
        pd.DataFrame: 对称相关矩阵。
    """
    return df_numeric.corr(method='spearman').round(4)


def compute_pearson_matrix(df_numeric: pd.DataFrame) -> pd.DataFrame:
    """计算 Pearson 相关矩阵。"""
    return df_numeric.corr(method='pearson').round(4)


def compute_cronbachs_alpha(df_numeric: pd.DataFrame) -> float:
    """计算 Cronbach's Alpha 内部一致性系数。

    Args:
        df_numeric: 各列为数值型的 DataFrame（每列一个方法/模型的得分）。

    Returns:
        float: Cronbach's Alpha 值。
    """
    df_clean = df_numeric.dropna()
    if len(df_clean) < 10 or df_clean.shape[1] < 2:
        return np.nan

    k = df_clean.shape[1]
    item_vars = df_clean.var(axis=0, ddof=1)
    total_var = df_clean.sum(axis=1).var(ddof=1)

    if total_var == 0:
        return 1.0

    alpha = (k / (k - 1)) * (1 - item_vars.sum() / total_var)
    return round(alpha, 4)


def compute_label_agreement_rate(labels_df: pd.DataFrame) -> dict:
    """计算多方法标签一致率（向量化实现）。

    Args:
        labels_df: 各列为分类标签（正面/中性/负面）的 DataFrame。

    Returns:
        dict: 包含完全一致率、多数一致率等指标。
    """
    valid = labels_df.dropna(how='any')
    n = len(valid)
    if n == 0:
        return {'full_agreement_rate': 0.0, 'majority_agreement_rate': 0.0,
                'n_samples': 0, 'n_methods': 0}

    n_methods = valid.shape[1]

    # 向量化：利用 nunique(axis=1) 判断完全一致（所有值相同 → nunique == 1）
    nunique_per_row = valid.nunique(axis=1)
    full_agree = int((nunique_per_row == 1).sum())

    # 多数一致：每行最高频标签的频次 >= 列数 / 2
    mode_counts = valid.apply(lambda row: row.value_counts().iloc[0], axis=1)
    majority_agree = int((mode_counts >= n_methods / 2).sum())

    return {
        'full_agreement_rate': round(full_agree / n, 4),
        'majority_agreement_rate': round(majority_agree / n, 4),
        'n_samples': n,
        'n_methods': n_methods,
    }


# ============================================================================
# 5. 可视化函数
# ============================================================================

def save_correlation_heatmap(corr_matrix: pd.DataFrame, title: str,
                              output_path: str, logger_inst):
    """保存相关系数矩阵热力图。"""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        # 设置中文字体支持
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei',
                                            'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        n = len(corr_matrix)
        fig_size = max(8, n * 0.8 + 2)
        fig, ax = plt.subplots(figsize=(fig_size, fig_size * 0.85))

        data = corr_matrix.values
        im = ax.imshow(data, cmap='RdYlBu_r', vmin=-1, vmax=1,
                       interpolation='nearest')

        # 标注数值
        for i in range(n):
            for j in range(n):
                val = data[i, j]
                if not np.isnan(val):
                    color = 'white' if abs(val) > 0.5 else 'black'
                    ax.text(j, i, f'{val:.2f}',
                            ha='center', va='center', color=color, fontsize=8)

        labels = corr_matrix.columns.tolist()
        ax.set_xticks(range(n))
        ax.set_yticks(range(n))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        ax.set_yticklabels(labels, fontsize=9)
        ax.set_title(title, fontsize=13, fontweight='bold', pad=15)

        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        logger_inst.info(f"热力图已保存: {output_path}")

    except ImportError:
        logger_inst.warning("matplotlib 不可用，跳过热力图绘制")
    except Exception as e:
        logger_inst.warning(f"绘制热力图失败: {e}")


# ============================================================================
# 6. LaTeX 输出
# ============================================================================

def generate_validation_latex(within_results: dict, cross_results: dict,
                               output_path: str, logger_inst):
    """生成情感验证报告的 LaTeX 表格。"""
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Sentiment Analysis Triangulation Validation}",
        r"\label{tab:sentiment_validation}",
        "",
        r"% Panel A: Within-Method Consistency",
        r"\begin{subtable}{\textwidth}",
        r"\centering",
        r"\caption{Panel A: Internal Consistency (Cronbach's $\alpha$)}",
        r"\begin{tabular}{lcc}",
        r"\hline",
        r"Method & Number of Models & Cronbach's $\alpha$ \\",
        r"\hline",
    ]

    for method_name, alpha in within_results.get('cronbach_alpha', {}).items():
        n_models = within_results.get('n_models', {}).get(method_name, '?')
        alpha_str = f"{alpha:.3f}" if not np.isnan(alpha) else "N/A"
        lines.append(f"  {method_name} & {n_models} & {alpha_str} \\\\")

    lines.extend([
        r"\hline",
        r"\end{tabular}",
        r"\end{subtable}",
        "",
        r"\\[12pt]",
        "",
        r"% Panel B: Cross-Method Consistency",
        r"\begin{subtable}{\textwidth}",
        r"\centering",
        r"\caption{Panel B: Cross-Method Agreement}",
        r"\begin{tabular}{lcc}",
        r"\hline",
        r"Metric & Value & N \\",
        r"\hline",
    ])

    agreement = cross_results.get('label_agreement', {})
    lines.append(
        f"  Full Agreement Rate & "
        f"{agreement.get('full_agreement_rate', 0):.3f} & "
        f"{agreement.get('n_samples', 0)} \\\\"
    )
    lines.append(
        f"  Majority Agreement Rate & "
        f"{agreement.get('majority_agreement_rate', 0):.3f} & "
        f"{agreement.get('n_samples', 0)} \\\\"
    )

    for pair, rho in cross_results.get('spearman_pairs', {}).items():
        lines.append(f"  Spearman ($\\rho$): {pair} & {rho:.3f} & -- \\\\")

    lines.extend([
        r"\hline",
        r"\end{tabular}",
        r"\end{subtable}",
        r"\end{table}",
    ])

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        logger_inst.info(f"LaTeX 表格已保存: {output_path}")
    except Exception as e:
        logger_inst.warning(f"保存 LaTeX 表格失败: {e}")


# ============================================================================
# 7. 合成策略
# ============================================================================

def majority_vote(labels_df: pd.DataFrame) -> pd.Series:
    """多数投票法合成情感标签。

    如果票数相同，按优先级 中性 > 负面 > 正面 选取（保守策略）。

    Args:
        labels_df: 各列为分类标签的 DataFrame。

    Returns:
        pd.Series: 合成后的标签。
    """
    def _vote(row):
        values = row.dropna().tolist()
        if not values:
            return '中性'
        counter = Counter(values)
        max_count = counter.most_common(1)[0][1]
        # 票数最多的标签（如有并列，按保守优先级）
        candidates = [k for k, v in counter.items() if v == max_count]
        for pref in ['中性', '负面', '正面']:
            if pref in candidates:
                return pref
        return candidates[0]

    return labels_df.apply(_vote, axis=1)


def weighted_average_score(scores_df: pd.DataFrame,
                           weights: dict = None) -> pd.Series:
    """加权平均法合成情感得分。

    Args:
        scores_df: 各列为连续得分的 DataFrame。
        weights:   {列名: 权重} 字典，若为 None 则等权。

    Returns:
        pd.Series: 合成后的加权得分。
    """
    if weights is None:
        return scores_df.mean(axis=1)

    total_weight = sum(weights.get(col, 1.0) for col in scores_df.columns)
    weighted_sum = sum(
        scores_df[col] * weights.get(col, 1.0)
        for col in scores_df.columns
    )
    return weighted_sum / total_weight


# ============================================================================
# 8. 人工验证样本生成
# ============================================================================

def generate_validation_sample(df: pd.DataFrame,
                                all_labels_df: pd.DataFrame,
                                vote_labels: pd.Series,
                                output_path: str,
                                logger_inst,
                                n_agree: int = 100,
                                n_disagree: int = 200,
                                seed: int = 42):
    """生成情感标签人工验证样本。

    抽样策略：
      - 一致样本：所有方法标签一致的文章中随机抽取 n_agree 篇
      - 不一致样本：存在分歧的文章中随机抽取 n_disagree 篇

    Args:
        df:              原始 DataFrame（含标题、内容等）。
        all_labels_df:   各方法标签的 DataFrame。
        vote_labels:     多数投票合成标签。
        output_path:     Excel 输出路径。
        logger_inst:     日志记录器。
        n_agree:         一致样本抽样数。
        n_disagree:      不一致样本抽样数。
        seed:            随机种子。
    """
    valid = all_labels_df.dropna(how='any')
    if valid.empty:
        logger_inst.warning("无有效标签数据，跳过人工验证样本生成")
        return

    # 判断是否完全一致
    is_agree = valid.apply(lambda row: len(set(row.values)) == 1, axis=1)
    agree_idx = valid[is_agree].index
    disagree_idx = valid[~is_agree].index

    logger_inst.info(f"完全一致样本数: {len(agree_idx):,}")
    logger_inst.info(f"存在分歧样本数: {len(disagree_idx):,}")

    rng = np.random.RandomState(seed)

    # 抽样
    n_a = min(n_agree, len(agree_idx))
    n_d = min(n_disagree, len(disagree_idx))

    if n_a > 0:
        agree_sample = rng.choice(agree_idx, size=n_a, replace=False)
    else:
        agree_sample = np.array([], dtype=int)

    if n_d > 0:
        disagree_sample = rng.choice(disagree_idx, size=n_d, replace=False)
    else:
        disagree_sample = np.array([], dtype=int)

    sample_idx = np.concatenate([agree_sample, disagree_sample])

    # 构建输出 DataFrame
    sample_df = df.loc[sample_idx].copy()

    # 添加各方法标签列
    for col in all_labels_df.columns:
        sample_df[col] = all_labels_df.loc[sample_idx, col]

    # 添加多数投票标签
    sample_df['多数投票标签'] = vote_labels.loc[sample_idx]

    # 添加抽样来源标记
    sample_df['样本类型'] = '一致'
    sample_df.loc[sample_df.index.isin(disagree_sample), '样本类型'] = '分歧'

    # 添加人工编码列
    sample_df['人工判定_情感'] = ''
    sample_df['人工判定_理由'] = ''

    # 保留核心列
    keep_cols = []
    for col in ['标题', '内容', '日期', '媒体(中文)']:
        if col in sample_df.columns:
            keep_cols.append(col)

    method_cols = [c for c in sample_df.columns
                   if c.startswith(('词典_', 'BERT_', 'LLM_'))
                   or c in ('多数投票标签', '样本类型',
                            '人工判定_情感', '人工判定_理由')]
    keep_cols.extend(method_cols)

    sample_output = sample_df[keep_cols].copy()

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 编码指南
            guide_data = pd.DataFrame({
                '项目': [
                    '目的',
                    '情感标签定义',
                    '编码规则',
                    '注意事项',
                    '样本来源说明',
                ],
                '说明': [
                    '对情感分析方法进行人工验证，评估自动化方法的准确性',
                    '正面: 积极/利好; 中性: 客观描述; 负面: 消极/风险',
                    '在"人工判定_情感"列填写: 正面/中性/负面; 在"人工判定_理由"列简述原因',
                    '基于文章整体语调判断，不受标题影响; 客观报道标为中性',
                    '"一致"=各方法结果一致的样本; "分歧"=各方法结果不一致的样本',
                ],
            })
            guide_data.to_excel(writer, sheet_name='编码指南', index=False)

            # 验证数据
            sample_output.to_excel(writer, sheet_name='验证数据', index=False)

            # 统计概览
            overview = pd.DataFrame({
                '统计项': [
                    '总验证样本数',
                    '一致样本数',
                    '分歧样本数',
                    '参与方法数',
                ],
                '值': [
                    len(sample_output),
                    n_a,
                    n_d,
                    all_labels_df.shape[1],
                ],
            })
            overview.to_excel(writer, sheet_name='统计概览', index=False)

        logger_inst.info(f"人工验证样本已保存: {output_path} ({len(sample_output)} 条)")
    except Exception as e:
        logger_inst.warning(f"保存人工验证样本失败: {e}")


# ============================================================================
# 9. 分层分析
# ============================================================================

def stratified_analysis(df: pd.DataFrame, all_scores_df: pd.DataFrame,
                        all_labels_df: pd.DataFrame, logger_inst,
                        track: str = '_full') -> dict:
    """按新闻长度、时间段和词典覆盖率进行分层一致性分析。"""
    results = {}

    # --- 按新闻长度分层 ---
    if '内容' in df.columns:
        df_temp = df.copy()
        df_temp['text_len'] = df_temp['内容'].astype(str).str.len()
        q33 = df_temp['text_len'].quantile(0.33)
        q66 = df_temp['text_len'].quantile(0.66)

        length_groups = {
            '短文本 (<33%)': df_temp['text_len'] <= q33,
            '中文本 (33-66%)': (df_temp['text_len'] > q33) & (df_temp['text_len'] <= q66),
            '长文本 (>66%)': df_temp['text_len'] > q66,
        }

        length_results = {}
        for group_name, mask in length_groups.items():
            group_scores = all_scores_df.loc[mask]
            if len(group_scores) < 20:
                continue

            alpha = compute_cronbachs_alpha(group_scores)
            group_labels = all_labels_df.loc[mask]
            agreement = compute_label_agreement_rate(group_labels)

            length_results[group_name] = {
                'n_samples': int(mask.sum()),
                'cronbach_alpha': alpha,
                'full_agreement_rate': agreement['full_agreement_rate'],
            }
            logger_inst.info(
                f"  分层[{group_name}]: n={int(mask.sum()):,}, "
                f"α={alpha:.3f}, 完全一致率={agreement['full_agreement_rate']:.3f}"
            )

        results['by_text_length'] = length_results

    # --- 按时间段分层 ---
    date_col = None
    for c in ['日期', 'date', 'Date']:
        if c in df.columns:
            date_col = c
            break

    if date_col:
        df_temp = df.copy()
        df_temp['_date'] = pd.to_datetime(df_temp[date_col], errors='coerce')
        df_temp['_year'] = df_temp['_date'].dt.year

        year_results = {}
        for year in sorted(df_temp['_year'].dropna().unique()):
            mask = df_temp['_year'] == year
            group_scores = all_scores_df.loc[mask]
            if len(group_scores) < 20:
                continue

            alpha = compute_cronbachs_alpha(group_scores)
            group_labels = all_labels_df.loc[mask]
            agreement = compute_label_agreement_rate(group_labels)

            year_results[str(int(year))] = {
                'n_samples': int(mask.sum()),
                'cronbach_alpha': alpha,
                'full_agreement_rate': agreement['full_agreement_rate'],
            }
            logger_inst.info(
                f"  分层[{int(year)}年]: n={int(mask.sum()):,}, "
                f"α={alpha:.3f}, 完全一致率={agreement['full_agreement_rate']:.3f}"
            )

        results['by_year'] = year_results

        # --- 年际一致性趋势检测 (Anis et al. 2024, §III Challenge [21]) ---
        # 论文依据: 跨时间泛化是深度学习金融情感分析的核心稳健性威胁。
        # 通过检测 Cronbach's α 的年际变化趋势，预警模型时间漂移。
        if len(year_results) >= 3:
            years_sorted = sorted(year_results.keys(), key=int)
            alphas = [year_results[y]['cronbach_alpha'] for y in years_sorted]
            years_int = [int(y) for y in years_sorted]

            valid_pairs = [(y, a) for y, a in zip(years_int, alphas)
                           if not np.isnan(a)]
            n_valid = len(valid_pairs)

            if n_valid >= 5:
                # 统计功效充足: 执行 Spearman 秩相关趋势检验
                valid_years = [v[0] for v in valid_pairs]
                valid_alphas = [v[1] for v in valid_pairs]

                # 防御: 常数输入检测 (std==0 时 spearmanr 返回 NaN
                # 并触发 ConstantInputWarning，需提前拦截)
                alpha_arr_sp = np.array(valid_alphas)
                if alpha_arr_sp.std() == 0:
                    trend_result = {
                        'test': 'descriptive_only',
                        'reason': f'所有 {n_valid} 年的 α 完全相同，无变异',
                        'alpha_mean': round(float(alpha_arr_sp.mean()), 4),
                        'alpha_std': 0.0,
                        'alpha_range': [round(float(alpha_arr_sp.min()), 4),
                                        round(float(alpha_arr_sp.max()), 4)],
                        'n_years': n_valid,
                    }
                    logger_inst.info(
                        f"  ✓ 年际α完全一致 (n={n_valid}年，"
                        f"α={alpha_arr_sp.mean():.3f}，无变异)"
                    )
                else:
                    try:
                        from scipy.stats import spearmanr
                        rho, p_val = spearmanr(valid_years, valid_alphas)
                        trend_result = {
                            'test': 'spearman_trend',
                            'spearman_rho': round(rho, 4),
                            'p_value': round(p_val, 4),
                            'trend': 'declining' if rho < 0 else 'stable_or_improving',
                            'significant': p_val < 0.05,
                            'n_years': n_valid,
                        }
                        if p_val < 0.05 and rho < 0:
                            logger_inst.warning(
                                f"  ⚠️ 年际一致性趋势: α 呈显著下降 "
                                f"(ρ={rho:.3f}, p={p_val:.3f}, n={n_valid}年)"
                            )
                            logger_inst.warning(
                                f"     解读: 模型可能存在时间漂移(temporal drift)，"
                                f"建议检查近年数据的语义分布变化"
                            )
                        else:
                            logger_inst.info(
                                f"  ✓ 年际一致性趋势: 无显著衰减 "
                                f"(ρ={rho:.3f}, p={p_val:.3f}, n={n_valid}年)"
                            )
                    except ImportError:
                        alpha_arr = np.array(valid_alphas)
                        trend_result = {
                            'test': 'descriptive_only',
                            'reason': 'scipy 不可用',
                            'alpha_mean': round(float(alpha_arr.mean()), 4),
                            'alpha_std': round(float(alpha_arr.std()), 4),
                            'alpha_range': [round(float(alpha_arr.min()), 4),
                                            round(float(alpha_arr.max()), 4)],
                            'n_years': n_valid,
                        }
                        logger_inst.info(
                            f"  ℹ️ 年际α描述性统计 (scipy不可用): "
                            f"mean={alpha_arr.mean():.3f}, std={alpha_arr.std():.3f}"
                        )
            elif n_valid >= 3:
                # 统计功效不足: 仅输出描述性统计
                alpha_arr = np.array([v[1] for v in valid_pairs])
                trend_result = {
                    'test': 'descriptive_only',
                    'reason': f'有效年份仅 {n_valid} 年 (<5)，功效不足',
                    'alpha_mean': round(float(alpha_arr.mean()), 4),
                    'alpha_std': round(float(alpha_arr.std()), 4),
                    'alpha_range': [round(float(alpha_arr.min()), 4),
                                    round(float(alpha_arr.max()), 4)],
                    'n_years': n_valid,
                }
                logger_inst.info(
                    f"  ℹ️ 年际α描述性统计 (n={n_valid}<5，不做推断): "
                    f"mean={alpha_arr.mean():.3f}, std={alpha_arr.std():.3f}"
                )
            else:
                trend_result = {
                    'test': 'skipped',
                    'reason': f'有效年份 {n_valid} < 3',
                }

            results['temporal_drift'] = trend_result

    # --- 按 BERT 窗口数分层（单窗口 vs 多窗口） ---
    if 'bert_num_windows' in df.columns:
        nw = df['bert_num_windows']
        # 排除未推理的文章 (num_windows=0)
        valid_mask = nw > 0
        if valid_mask.sum() >= 40:  # 两组各至少需要 20 篇
            window_groups = {
                '单窗口 (=1)': valid_mask & (nw == 1),
                '多窗口 (>1)': valid_mask & (nw > 1),
            }

            window_results = {}
            for group_name, mask in window_groups.items():
                group_scores = all_scores_df.loc[mask]
                if len(group_scores) < 20:
                    continue

                alpha = compute_cronbachs_alpha(group_scores)
                group_labels = all_labels_df.loc[mask]
                agreement = compute_label_agreement_rate(group_labels)

                window_results[group_name] = {
                    'n_samples': int(mask.sum()),
                    'cronbach_alpha': alpha,
                    'full_agreement_rate': agreement['full_agreement_rate'],
                }
                logger_inst.info(
                    f"  分层[{group_name}]: n={int(mask.sum()):,}, "
                    f"α={alpha:.3f}, 完全一致率={agreement['full_agreement_rate']:.3f}"
                )

            results['by_window_count'] = window_results
        else:
            logger_inst.info("  bert_num_windows 有效样本不足 40，跳过窗口数分层分析")
    else:
        logger_inst.info("  bert_num_windows 列不存在，跳过窗口数分层分析（需先运行阶段 23）")

    # --- 按词典覆盖率分层 (Rizinski et al. 2024 [22], XLex 方法论) ---
    # 论文依据: lexicon 方法的词汇覆盖率限制是核心挑战。
    # 覆盖率代理: pos_ratio + neg_ratio (22_tone_words.py L751-759)
    # 该比率 = 情感词频次 / 总 token 数，直接反映词汇覆盖密度。
    # 注意: 不使用 |score| 之和 (score 是归一化强度，非覆盖率)。
    pos_ratio_col = f'pos_ratio{track}'
    neg_ratio_col = f'neg_ratio{track}'

    if pos_ratio_col in df.columns and neg_ratio_col in df.columns:
        coverage = df[pos_ratio_col].fillna(0) + df[neg_ratio_col].fillna(0)
        has_coverage = coverage > 0

        if has_coverage.sum() >= 60:
            q33 = coverage[has_coverage].quantile(0.33)
            q66 = coverage[has_coverage].quantile(0.66)

            coverage_groups = {
                '低覆盖率 (<33%)': has_coverage & (coverage <= q33),
                '中覆盖率 (33-66%)': has_coverage & (coverage > q33) & (coverage <= q66),
                '高覆盖率 (>66%)': has_coverage & (coverage > q66),
            }

            coverage_results = {}
            non_words_score_cols = [c for c in all_scores_df.columns
                                    if not c.startswith('词典_')]
            non_words_label_cols = [c for c in all_labels_df.columns
                                    if not c.startswith('词典_')]

            for group_name, mask in coverage_groups.items():
                if mask.sum() < 20:
                    continue
                group_scores = all_scores_df.loc[mask, non_words_score_cols]
                alpha = compute_cronbachs_alpha(group_scores)
                group_labels = all_labels_df.loc[mask, non_words_label_cols]
                agreement = compute_label_agreement_rate(group_labels)

                coverage_results[group_name] = {
                    'n_samples': int(mask.sum()),
                    'cronbach_alpha_bert_llm': alpha,
                    'full_agreement_rate_bert_llm': agreement['full_agreement_rate'],
                }
                logger_inst.info(
                    f"  分层[{group_name}]: n={int(mask.sum()):,}, "
                    f"α(BERT+LLM)={alpha:.3f}, "
                    f"一致率={agreement['full_agreement_rate']:.3f}"
                )

            results['by_dict_coverage'] = coverage_results

            # 自动解读: 低 vs 高覆盖率组的 α 差异
            low = coverage_results.get('低覆盖率 (<33%)', {})
            high = coverage_results.get('高覆盖率 (>66%)', {})
            if low and high:
                alpha_low = low.get('cronbach_alpha_bert_llm', np.nan)
                alpha_high = high.get('cronbach_alpha_bert_llm', np.nan)
                if not np.isnan(alpha_low) and not np.isnan(alpha_high):
                    delta = alpha_high - alpha_low
                    if delta > 0.10:
                        logger_inst.warning(
                            f"  ⚠️ 覆盖率依赖: Δα={delta:+.3f}，"
                            f"词典法锚点在低覆盖率文章中不可靠"
                        )
                    else:
                        logger_inst.info(
                            f"  ✓ BERT+LLM 在低覆盖率文章中仍稳健 "
                            f"(Δα={delta:+.3f})"
                        )
        else:
            logger_inst.info(
                f"  覆盖率分层: 有效样本不足60 ({has_coverage.sum()})"
            )
    else:
        logger_inst.info(
            f"  pos_ratio/neg_ratio 列不存在，跳过覆盖率分层"
        )

    return results


# ============================================================================
# 9.5 LLM 概率诊断 (Chiu & Hung 2024 M3 降级适配)
# ============================================================================

def _compute_jsd(p: np.ndarray, q: np.ndarray) -> float:
    """计算 Jensen-Shannon 散度（以 bit 为单位）。

    JSD(P||Q) = 0.5 * KLD(P||M) + 0.5 * KLD(Q||M)，其中 M = 0.5*(P+Q)。
    自动处理零概率（加 1e-12 平滑），避免 log(0)。

    Args:
        p: 概率分布向量（需归一化）。
        q: 概率分布向量（需归一化）。

    Returns:
        float: JSD 值，范围 [0, 1]（以 log2 计算时上界为 1）。
    """
    eps = 1e-12
    p = np.asarray(p, dtype=float) + eps
    q = np.asarray(q, dtype=float) + eps
    p = p / p.sum()
    q = q / q.sum()
    m = 0.5 * (p + q)
    kld_pm = float(np.sum(p * np.log2(p / m)))
    kld_qm = float(np.sum(q * np.log2(q / m)))
    return round(0.5 * kld_pm + 0.5 * kld_qm, 6)


def _chi2_contingency_manual(observed: np.ndarray) -> tuple:
    """手动计算 chi-square 独立性检验（scipy 不可用时的回退实现）。

    Args:
        observed: 列联表（r x c numpy 数组）。

    Returns:
        tuple: (chi2_statistic, p_value_approx, dof)
               p 值为近似值（使用 chi-square CDF 的正态近似）。
    """
    observed = np.asarray(observed, dtype=float)
    row_sums = observed.sum(axis=1)
    col_sums = observed.sum(axis=0)
    total = observed.sum()
    if total == 0:
        return 0.0, 1.0, 0
    expected = np.outer(row_sums, col_sums) / total
    # 避免除零
    mask = expected > 0
    chi2 = float(np.sum((observed[mask] - expected[mask]) ** 2 / expected[mask]))
    dof = (observed.shape[0] - 1) * (observed.shape[1] - 1)
    if dof <= 0:
        return chi2, 1.0, dof
    # Wilson-Hilferty 正态近似
    z = ((chi2 / dof) ** (1.0 / 3) - (1 - 2.0 / (9 * dof))) / (2.0 / (9 * dof)) ** 0.5
    # 标准正态 CDF 近似 (Abramowitz & Stegun)
    if z > 8:
        p_val = 0.0
    elif z < -8:
        p_val = 1.0
    else:
        t = 1.0 / (1.0 + 0.2316419 * abs(z))
        d = 0.3989422804014327  # 1/sqrt(2*pi)
        poly = t * (0.319381530 + t * (-0.356563782 + t * (
            1.781477937 + t * (-1.821255978 + t * 1.330274429))))
        cdf = 1.0 - d * np.exp(-0.5 * z * z) * poly if z > 0 else d * np.exp(-0.5 * z * z) * poly
        p_val = 1.0 - cdf
    return chi2, max(0.0, min(1.0, p_val)), dof


def diagnose_llm_category_bias(df: pd.DataFrame, llm_cols: dict,
                                track: str, output_dir: str,
                                logger_inst) -> dict:
    """诊断各 LLM 模型的系统性类别偏向及模型间独立性。

    基于 Chiu & Hung (2024, IRFA) Fig. 2 的 Neutral 偏好诊断思路降级适配。
    项目数据为单次打标，无法复刻原始 Dirichlet 批次更新，改为经验性类别
    比例分析 + 模型间 chi-square 独立性检验 + Jensen-Shannon 散度。

    学术依据：
      - Chiu & Hung (2024): 模型存在系统性 Neutral 偏好倾向
      - Carlson & Burbano (2026, SMJ §4.2): 建议报告 model certainty

    Args:
        df:          当前轨道的 DataFrame。
        llm_cols:    sentiment_cols['llm'] 的值，结构为
                     {short_name: {'sentiment': col, 'confidence': col|None}}。
                     注意：包含投票聚合列 short_name='llm'，需过滤。
        track:       轨道后缀（'_full' 或 '_ctx'）。
        output_dir:  输出目录（eval_reports/）。
        logger_inst: 日志记录器。

    Returns:
        dict: 诊断结果，包含各模型类别比例、chi-square 结果、JS 散度。
    """
    track_label = '全文' if track == '_full' else '上下文片段'
    logger_inst.info("=" * 70)
    logger_inst.info(f"===    4.5a LLM 类别偏向诊断 [{track_label}]    ===")
    logger_inst.info("=" * 70)

    # ── 0. 过滤聚合列，仅保留独立模型 ──
    independent_models = {
        name: info for name, info in llm_cols.items()
        if name != 'llm'  # 排除多数投票聚合列
    }
    n_models = len(independent_models)
    if n_models < 1:
        logger_inst.warning("  无独立 LLM 模型列可用，跳过类别偏向诊断")
        return {}

    logger_inst.info(f"  独立模型数: {n_models} ({list(independent_models.keys())})")

    # ── 1. 各模型类别分布 ──
    categories = ['正面', '中性', '负面']
    distributions = {}  # name -> {cat: proportion}
    counts_raw = {}     # name -> {cat: count}
    model_names = []

    for name, info in independent_models.items():
        sent_col = info['sentiment']
        if sent_col not in df.columns:
            logger_inst.warning(f"  列 '{sent_col}' 不存在，跳过模型 {name}")
            continue
        model_names.append(name)
        vc = df[sent_col].value_counts()
        total = vc.sum()
        dist = {}
        cnt = {}
        for cat in categories:
            c = int(vc.get(cat, 0))
            cnt[cat] = c
            dist[cat] = round(c / max(total, 1), 4)
        distributions[name] = dist
        counts_raw[name] = cnt
        logger_inst.info(
            f"  [{name}] 类别分布: "
            + ", ".join(f"{cat}={dist[cat]:.1%} ({cnt[cat]})" for cat in categories)
        )

    if len(model_names) < 2:
        logger_inst.info("  独立模型不足 2 个，跳过两两比较")
        return {'distributions': distributions}

    # ── 2. 模型间 chi-square 同质性检验（两两） ──
    # 注：2×3 列联表检验两模型的边际分类分布是否相同（homogeneity test），
    # 而非同一样本上两变量的独立性。两种检验公式和统计量完全相同。
    logger_inst.info("  --- 模型间类别分布同质性检验 ---")
    try:
        from scipy.stats import chi2_contingency
        _use_scipy = True
    except ImportError:
        _use_scipy = False
        logger_inst.info("  scipy 不可用，使用手动 chi-square 实现")

    chi2_results = []
    for i in range(len(model_names)):
        for j in range(i + 1, len(model_names)):
            m1, m2 = model_names[i], model_names[j]
            # 构建 2 x len(categories) 列联表
            row1 = [counts_raw[m1].get(cat, 0) for cat in categories]
            row2 = [counts_raw[m2].get(cat, 0) for cat in categories]
            contingency = np.array([row1, row2])

            if _use_scipy:
                chi2_stat, p_val, dof, _ = chi2_contingency(contingency)
            else:
                chi2_stat, p_val, dof = _chi2_contingency_manual(contingency)

            chi2_results.append({
                'pair': f"{m1} vs {m2}",
                'chi2': round(chi2_stat, 4),
                'p_value': round(p_val, 6),
                'dof': dof,
                'significant': p_val < 0.05,
            })
            sig_mark = '*' if p_val < 0.05 else ''
            logger_inst.info(
                f"  {m1} vs {m2}: chi2={chi2_stat:.2f}, "
                f"p={p_val:.4f}{sig_mark}, dof={dof}"
            )

    # ── 3. 模型间 Jensen-Shannon 散度 ──
    logger_inst.info("  --- 模型间 Jensen-Shannon 散度 ---")
    js_results = []
    for i in range(len(model_names)):
        for j in range(i + 1, len(model_names)):
            m1, m2 = model_names[i], model_names[j]
            p = np.array([distributions[m1].get(cat, 0) for cat in categories])
            q = np.array([distributions[m2].get(cat, 0) for cat in categories])
            jsd = _compute_jsd(p, q)
            js_results.append({'pair': f"{m1} vs {m2}", 'jsd': jsd})

            if jsd > 0.1:
                interp = '偏向差异大（多数投票有效性正面证据）'
            elif jsd < 0.01:
                interp = '高度同质化（多数投票退化风险）'
            else:
                interp = '偏向差异适中'
            logger_inst.info(f"  {m1} vs {m2}: JSD={jsd:.4f} — {interp}")

    # ── 4. 输出 CSV ──
    csv_rows = []
    for name in model_names:
        row = {'模型': name}
        row.update({f'比例_{cat}': distributions[name][cat] for cat in categories})
        csv_rows.append(row)
    # 追加检验结果
    for cr in chi2_results:
        csv_rows.append({
            '模型': cr['pair'],
            'chi2': cr['chi2'],
            'p_value': cr['p_value'],
            'significant': cr['significant'],
        })
    for jr in js_results:
        csv_rows.append({'模型': jr['pair'], 'JSD': jr['jsd']})

    csv_path = os.path.join(output_dir, f'llm_bias_diagnostic{track}.csv')
    pd.DataFrame(csv_rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
    logger_inst.info(f"  类别偏向诊断 CSV: {csv_path}")

    # ── 5. 输出 PNG ──
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei',
                                            'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        x = np.arange(len(categories))
        width = 0.8 / max(len(model_names), 1)
        fig, ax = plt.subplots(figsize=(8, 5))

        for idx, name in enumerate(model_names):
            vals = [distributions[name].get(cat, 0) for cat in categories]
            offset = (idx - (len(model_names) - 1) / 2) * width
            bars = ax.bar(x + offset, vals, width * 0.9, label=name, alpha=0.85)
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f'{v:.1%}', ha='center', va='bottom', fontsize=8)

        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=11)
        ax.set_ylabel('比例', fontsize=11)
        ax.set_title(f'LLM 模型类别分布对比 [{track_label}]', fontsize=13, fontweight='bold')
        ax.legend(fontsize=9)
        ax.set_ylim(0, 1.0)
        fig.tight_layout()

        png_path = os.path.join(output_dir, f'llm_bias_diagnostic{track}.png')
        fig.savefig(png_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        logger_inst.info(f"  类别偏向诊断图: {png_path}")
    except ImportError:
        logger_inst.warning("  matplotlib 不可用，跳过类别偏向柱状图")
    except Exception as e:
        logger_inst.warning(f"  绘制类别偏向图失败: {e}")

    return {
        'distributions': distributions,
        'chi2_tests': chi2_results,
        'js_divergences': js_results,
    }


def diagnose_confidence_calibration(df: pd.DataFrame, llm_cols: dict,
                                     track: str, output_dir: str,
                                     logger_inst) -> dict:
    """检查 LLM 模型自报告置信度是否校准良好。

    当 33 阶段人工金标准数据存在时，计算 Expected Calibration Error (ECE)
    并绘制可靠性图。否则降级为仅输出置信度分布描述性统计。

    学术依据：
      - Guo et al. (2017, ICML): ECE < 0.05 校准良好
      - Niculescu-Mizil & Caruana (2005, ICML): 可靠性图

    Args:
        df:          当前轨道的 DataFrame。
        llm_cols:    sentiment_cols['llm'] 的值（含聚合列，需过滤）。
        track:       轨道后缀。
        output_dir:  输出目录。
        logger_inst: 日志记录器。

    Returns:
        dict: 校准诊断结果。
    """
    track_label = '全文' if track == '_full' else '上下文片段'
    logger_inst.info("=" * 70)
    logger_inst.info(f"===    4.5b 置信度校准诊断 [{track_label}]    ===")
    logger_inst.info("=" * 70)

    # ── 0. 过滤聚合列 ──
    independent_models = {
        name: info for name, info in llm_cols.items()
        if name != 'llm'
    }
    if not independent_models:
        logger_inst.warning("  无独立 LLM 模型列可用，跳过置信度校准诊断")
        return {}

    # ── 1. 置信度描述性统计（始终执行） ──
    logger_inst.info("  --- 置信度分布描述性统计 ---")
    stats_results = {}

    for name, info in independent_models.items():
        conf_col = info.get('confidence')
        if not conf_col or conf_col not in df.columns:
            logger_inst.info(f"  [{name}] 无置信度列，跳过")
            continue

        conf = pd.to_numeric(df[conf_col], errors='coerce').dropna()
        if len(conf) == 0:
            logger_inst.info(f"  [{name}] 置信度列全为空值，跳过")
            continue

        stats = {
            'mean': round(float(conf.mean()), 4),
            'median': round(float(conf.median()), 4),
            'std': round(float(conf.std()), 4),
            'min': round(float(conf.min()), 4),
            'max': round(float(conf.max()), 4),
            'n': len(conf),
        }
        # skew: 手动计算避免 scipy 依赖
        if stats['std'] > 0:
            stats['skew'] = round(float((((conf - conf.mean()) / conf.std()) ** 3).mean()), 4)
        else:
            stats['skew'] = 0.0

        stats_results[name] = stats
        logger_inst.info(
            f"  [{name}] mean={stats['mean']:.3f}, "
            f"median={stats['median']:.3f}, std={stats['std']:.3f}, "
            f"skew={stats['skew']:.3f}, n={stats['n']}"
        )

    # ── 2. 输出 CSV（描述性统计，始终生成） ──
    csv_rows = []
    for name, s in stats_results.items():
        row = {'模型': name}
        row.update(s)
        csv_rows.append(row)

    csv_path = os.path.join(output_dir, f'llm_calibration{track}.csv')
    if csv_rows:
        pd.DataFrame(csv_rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger_inst.info(f"  置信度校准 CSV: {csv_path}")

    # ── 3. 置信度直方图（降级模式，始终绘制） ──
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei',
                                            'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        n_plots = len(stats_results)
        if n_plots > 0:
            fig, axes = plt.subplots(1, n_plots, figsize=(5 * n_plots, 4),
                                     squeeze=False)
            plot_idx = 0
            for name, info in independent_models.items():
                conf_col = info.get('confidence')
                if not conf_col or conf_col not in df.columns:
                    continue
                if name not in stats_results:
                    continue
                if plot_idx >= n_plots:
                    break
                ax = axes[0, plot_idx]
                conf = pd.to_numeric(df[conf_col], errors='coerce').dropna()
                ax.hist(conf, bins=20, range=(0, 1), alpha=0.7,
                        color='steelblue', edgecolor='white')
                ax.set_title(f'{name}', fontsize=11, fontweight='bold')
                ax.set_xlabel('置信度', fontsize=10)
                ax.set_ylabel('频次', fontsize=10)
                s = stats_results[name]
                ax.axvline(s['mean'], color='red', linestyle='--', linewidth=1,
                           label=f"mean={s['mean']:.2f}")
                ax.legend(fontsize=8)
                plot_idx += 1

            fig.suptitle(f'LLM 置信度分布 [{track_label}]', fontsize=13,
                         fontweight='bold')
            fig.tight_layout(rect=[0, 0, 1, 0.93])
            png_path = os.path.join(output_dir, f'llm_calibration{track}.png')
            fig.savefig(png_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            logger_inst.info(f"  置信度分布图: {png_path}")
    except ImportError:
        logger_inst.warning("  matplotlib 不可用，跳过置信度直方图")
    except Exception as e:
        logger_inst.warning(f"  绘制置信度直方图失败: {e}")

    return {
        'stats': stats_results,
        'mode': 'descriptive_only',
    }


# ============================================================================
# 10. 主函数
# ============================================================================

def main():
    """情感三角验证主入口（双轨模式）。"""
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} (双轨模式) ---")
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     对三种情感分析方法(词典法/BERT/LLM)进行系统性交叉验证,")
    logger.info("     以确保情感度量的构建效度(Construct Validity)符合顶级期刊标准。")
    logger.info("     双轨模式: 全文(_full)和上下文片段(_ctx)分别执行完整验证。")
    logger.info("")
    logger.info("  📖 方法论依据")
    logger.info("     · Loughran & McDonald (2016, JAR 54(4):1187-1230):")
    logger.info("       多度量方法间的相关性是构建效度的核心证据")
    logger.info("     · Cronbach (1951, Psychometrika 16(3):297-334):")
    logger.info("       内部一致性系数 α 的计算与解释标准")
    logger.info("")
    logger.info("  📊 关键指标解读")
    logger.info("     · Cronbach's Alpha: ≥0.90(优秀), ≥0.80(良好), ≥0.70(可接受), <0.70(需改进)")
    logger.info("     · Spearman ρ ≥ 0.7: 方法间一致性强; 0.4-0.7: 中等; <0.4: 弱")
    logger.info("     · 跨方法标签一致性: ≥85% 视为方法间一致性良好 (经验参考值)")
    logger.info("")

    output_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
    os.makedirs(output_dir, exist_ok=True)

    # ======================================================================
    # Step 1: 加载情感分析数据
    # ======================================================================
    # 串联流程中，阶段 22 的输出已包含全部词典/BERT/LLM 列（逐级累积），
    # 因此直接加载最终产出物即可，无需三文件合并。
    primary_key = 'output_23_bert_tone'
    primary_file = CONFIG['filenames'].get(primary_key, '')
    primary_path = os.path.join(CONFIG['paths']['output_dir'], primary_file)

    if not os.path.isfile(primary_path):
        # 退回到词典法输出
        primary_key = 'output_22_words_tone'
        primary_file = CONFIG['filenames'].get(primary_key, '')
        primary_path = os.path.join(CONFIG['paths']['output_dir'], primary_file)

    if not os.path.isfile(primary_path):
        logger.error("未找到任何情感分析阶段的输出文件，请先运行阶段 22/23")
        return

    logger.info(f"加载数据源 [{primary_key}]: {primary_path}")
    df = pd.read_parquet(primary_path)
    logger.info(f"行数: {len(df):,}，列数: {len(df.columns)}")
    log_memory_usage(logger, "数据加载完成")

    # ======================================================================
    # Step 2: 双轨三角验证循环
    # ======================================================================
    # 对 _full 和 _ctx 两条轨道分别执行完整的三角验证流水线
    for track in ['_full', '_ctx']:
        track_label = '全文' if track == '_full' else '上下文片段'
        logger.info("\n" + "#" * 70)
        logger.info(f"#####  三角验证轨道: [{track_label}] ({track})  #####")
        logger.info("#" * 70)
        _run_validation_for_track(df, track, output_dir, logger, CONFIG)

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=len(df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} (双轨模式) ---")


def _run_validation_for_track(df, track, output_dir, logger, CONFIG):
    """对指定轨道执行完整的三角验证流水线。"""
    # ======================================================================
    # Step 2: 自动发现情感列
    # ======================================================================
    sentiment_cols = discover_sentiment_columns(df, track_suffix=track)

    logger.info("=" * 70)
    logger.info("===    已发现的情感分析列    ===")
    logger.info("=" * 70)
    logger.info(f"词典法: {list(sentiment_cols['words'].keys()) or '未发现'}")
    logger.info(f"BERT:   {list(sentiment_cols['bert'].keys()) or '未发现'}")
    logger.info(f"LLM:    {list(sentiment_cols['llm'].keys()) or '未发现'}")

    # 列存在性校验
    if not sentiment_cols['words']:
        logger.warning("未发现词典法情感列 → 请确认阶段 22 已正确运行")
    if not sentiment_cols['bert']:
        logger.warning("未发现 BERT 情感列 → 请确认阶段 23 已正确运行")
    if not sentiment_cols['llm']:
        logger.warning("未发现 LLM 情感列 → 请确认阶段 21 已正确运行")

    n_words = len(sentiment_cols['words'])
    n_bert = len(sentiment_cols['bert'])
    n_llm = len(sentiment_cols['llm'])
    total_methods = n_words + n_bert + n_llm

    if total_methods < 2:
        logger.error(f"至少需要 2 种方法/模型才能进行三角验证（当前: {total_methods}）")
        return

    # 收集所有数值得分和标签
    all_scores = {}  # name -> pd.Series (数值型)
    all_labels = {}  # name -> pd.Series (标签型)

    for dict_name, cols_info in sentiment_cols['words'].items():
        all_scores[f'词典_{dict_name}'] = df[cols_info['score']].astype(float)
        all_labels[f'词典_{dict_name}'] = df[cols_info['label']]

    for short_name, cols_info in sentiment_cols['bert'].items():
        all_labels[f'BERT_{short_name}'] = df[cols_info['label']]
        # 尝试用概率差值作为数值得分
        probs = cols_info.get('probs', {})
        if '正面' in probs and '负面' in probs:
            pos_probs = df[probs['正面']].astype(float)
            neg_probs = df[probs['负面']].astype(float)
            all_scores[f'BERT_{short_name}'] = pos_probs - neg_probs
        elif len(probs) > 0:
            # 用标签数值化作为分数
            all_scores[f'BERT_{short_name}'] = label_to_numeric(df[cols_info['label']])

    for short_name, cols_info in sentiment_cols['llm'].items():
        all_labels[f'LLM_{short_name}'] = df[cols_info['sentiment']]
        # 用标签×置信度作为连续得分
        if cols_info.get('confidence'):
            numeric = label_to_numeric(df[cols_info['sentiment']])
            conf = pd.to_numeric(df[cols_info['confidence']], errors='coerce').fillna(0.5)
            all_scores[f'LLM_{short_name}'] = numeric * conf
        else:
            all_scores[f'LLM_{short_name}'] = label_to_numeric(
                df[cols_info['sentiment']]
            )

    all_scores_df = pd.DataFrame(all_scores)
    all_labels_df = pd.DataFrame(all_labels)

    logger.info(f"共构建 {len(all_scores)} 个数值得分列, {len(all_labels)} 个标签列")

    results = {
        'n_samples': len(df),
        'methods_detected': {
            'words': list(sentiment_cols['words'].keys()),
            'bert': list(sentiment_cols['bert'].keys()),
            'llm': list(sentiment_cols['llm'].keys()),
        },
        'within_method': {},
        'cross_method': {},
    }

    # ======================================================================
    # Step 3: 内部一致性分析（Within-Method）
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    一、内部一致性分析 (Within-Method)    ===")
    logger.info("=" * 70)

    within_results = {'cronbach_alpha': {}, 'n_models': {}}

    # 3.1 词典间一致性
    if n_words >= 2:
        logger.info(f"--- 词典法: {n_words} 个词典 ---")
        words_score_cols = [c for c in all_scores_df.columns if c.startswith('词典_')]
        words_scores = all_scores_df[words_score_cols]

        alpha = compute_cronbachs_alpha(words_scores)
        within_results['cronbach_alpha']['Dictionary'] = alpha
        within_results['n_models']['Dictionary'] = n_words
        logger.info(f"  Cronbach's Alpha: {alpha:.4f}")

        spearman = compute_spearman_matrix(words_scores)
        logger.info("  Spearman 相关矩阵:")
        logger.info(f"\n{spearman.to_string()}")
        results['within_method']['words_spearman'] = spearman.to_dict()

        save_correlation_heatmap(
            spearman, 'Spearman 相关矩阵 — 词典法 (内部)',
            os.path.join(output_dir, 'heatmap_within_words.png'), logger
        )

    # 3.1b IDF 词典法内部一致性（稳健性检验，独立报告）
    # IDF 与等权是同源数据的不同加权，非独立观测，
    # 混入同一 Cronbach's α 会虚假膨胀。因此单独报告。
    # 注意：使用局部变量，不修改共享的 all_scores/all_scores_df，
    #       防止下游跨方法分析被 IDF 列污染。
    n_words_idf = len(sentiment_cols.get('words_idf', {}))
    if n_words_idf >= 2:
        logger.info(f"--- 词典法 IDF (稳健性检验): {n_words_idf} 个词典 ---")
        idf_scores_dict = {}
        for dict_name, cols_info in sentiment_cols['words_idf'].items():
            idf_scores_dict[f'词典_{dict_name}'] = df[cols_info['score']].astype(float)

        idf_scores = pd.DataFrame(idf_scores_dict)
        if len(idf_scores.columns) >= 2:
            idf_alpha = compute_cronbachs_alpha(idf_scores)
            within_results['cronbach_alpha']['Dictionary_IDF'] = idf_alpha
            within_results['n_models']['Dictionary_IDF'] = n_words_idf
            logger.info(f"  IDF Cronbach's Alpha: {idf_alpha:.4f}")

            idf_spearman = compute_spearman_matrix(idf_scores)
            logger.info("  IDF Spearman 相关矩阵:")
            logger.info(f"\n{idf_spearman.to_string()}")
            results['within_method']['words_idf_spearman'] = idf_spearman.to_dict()

    # 3.2 BERT 模型间一致性
    if n_bert >= 2:
        logger.info(f"--- BERT: {n_bert} 个模型 ---")
        bert_score_cols = [c for c in all_scores_df.columns if c.startswith('BERT_')]
        bert_scores = all_scores_df[bert_score_cols]

        alpha = compute_cronbachs_alpha(bert_scores)
        within_results['cronbach_alpha']['BERT'] = alpha
        within_results['n_models']['BERT'] = n_bert
        logger.info(f"  Cronbach's Alpha: {alpha:.4f}")

        spearman = compute_spearman_matrix(bert_scores)
        logger.info("  Spearman 相关矩阵:")
        logger.info(f"\n{spearman.to_string()}")
        results['within_method']['bert_spearman'] = spearman.to_dict()

        save_correlation_heatmap(
            spearman, 'Spearman 相关矩阵 — BERT (内部)',
            os.path.join(output_dir, 'heatmap_within_bert.png'), logger
        )

    # 3.3 LLM 模型间一致性（如有多个模型）
    if n_llm >= 2:
        logger.info(f"--- LLM: {n_llm} 个模型 ---")
        llm_score_cols = [c for c in all_scores_df.columns if c.startswith('LLM_')]
        llm_scores = all_scores_df[llm_score_cols]

        alpha = compute_cronbachs_alpha(llm_scores)
        within_results['cronbach_alpha']['LLM'] = alpha
        within_results['n_models']['LLM'] = n_llm
        logger.info(f"  Cronbach's Alpha: {alpha:.4f}")

    results['within_method']['cronbach_alpha'] = within_results['cronbach_alpha']

    # ======================================================================
    # Step 4: 跨方法一致性分析（Cross-Method）
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    二、跨方法一致性分析 (Cross-Method)    ===")
    logger.info("=" * 70)

    cross_results = {}

    # 4.1 全量相关矩阵
    logger.info("--- 全量 Spearman 相关矩阵 ---")
    full_spearman = compute_spearman_matrix(all_scores_df)
    logger.info(f"\n{full_spearman.to_string()}")
    results['cross_method']['full_spearman'] = full_spearman.to_dict()

    save_correlation_heatmap(
        full_spearman, 'Spearman 相关矩阵 — 全部方法 × 全部模型',
        os.path.join(output_dir, 'heatmap_cross_all.png'), logger
    )

    # 4.2 方法级聚合对比
    logger.info("--- 方法级聚合对比 ---")
    method_agg = {}

    words_cols = [c for c in all_scores_df.columns if c.startswith('词典_')]
    bert_cols = [c for c in all_scores_df.columns if c.startswith('BERT_')]
    llm_cols = [c for c in all_scores_df.columns if c.startswith('LLM_')]

    if words_cols:
        method_agg['词典法'] = all_scores_df[words_cols].mean(axis=1)
    if bert_cols:
        method_agg['BERT'] = all_scores_df[bert_cols].mean(axis=1)
    if llm_cols:
        method_agg['LLM'] = all_scores_df[llm_cols].mean(axis=1)

    if len(method_agg) >= 2:
        method_agg_df = pd.DataFrame(method_agg)
        method_spearman = compute_spearman_matrix(method_agg_df)
        method_pearson = compute_pearson_matrix(method_agg_df)

        logger.info("方法级 Spearman:")
        logger.info(f"\n{method_spearman.to_string()}")
        logger.info("方法级 Pearson:")
        logger.info(f"\n{method_pearson.to_string()}")

        results['cross_method']['method_spearman'] = method_spearman.to_dict()
        results['cross_method']['method_pearson'] = method_pearson.to_dict()

        # 提取成对相关用于 LaTeX
        spearman_pairs = {}
        for i, c1 in enumerate(method_spearman.columns):
            for j, c2 in enumerate(method_spearman.columns):
                if i < j:
                    spearman_pairs[f'{c1} vs {c2}'] = method_spearman.iloc[i, j]
        cross_results['spearman_pairs'] = spearman_pairs

        save_correlation_heatmap(
            method_spearman, 'Spearman 相关矩阵 — 方法级聚合',
            os.path.join(output_dir, 'heatmap_cross_method.png'), logger
        )

    # 4.3 标签一致性
    logger.info("--- 标签一致性分析 ---")
    agreement = compute_label_agreement_rate(all_labels_df)
    cross_results['label_agreement'] = agreement
    results['cross_method']['label_agreement'] = agreement

    logger.info(f"  完全一致率: {agreement['full_agreement_rate']:.4f}")
    logger.info(f"  多数一致率: {agreement['majority_agreement_rate']:.4f}")
    logger.info(f"  参与方法/模型数: {agreement['n_methods']}")

    # ======================================================================
    # Step 5: 合成策略
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    三、合成策略    ===")
    logger.info("=" * 70)

    # 5.1 多数投票
    vote_labels = majority_vote(all_labels_df)
    vote_dist = vote_labels.value_counts()
    logger.info("多数投票情感分布:")
    for label, count in vote_dist.items():
        pct = count / len(vote_labels) * 100
        logger.info(f"  {label}: {count:,} ({pct:.1f}%)")

    # 5.2 加权平均（等权）
    weighted_score = weighted_average_score(all_scores_df)
    logger.info(f"加权平均得分: mean={weighted_score.mean():.4f}, "
                f"std={weighted_score.std():.4f}")

    # 保存合成结果到 DataFrame
    df['consensus_vote_label'] = vote_labels.values
    df['consensus_weighted_score'] = weighted_score.values

    results['synthesis'] = {
        'vote_distribution': vote_dist.to_dict(),
        'weighted_score_mean': round(float(weighted_score.mean()), 4),
        'weighted_score_std': round(float(weighted_score.std()), 4),
    }

    # ======================================================================
    # Step 6: 分层稳健性分析
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    四、分层稳健性分析    ===")
    logger.info("=" * 70)

    stratified = stratified_analysis(df, all_scores_df, all_labels_df, logger, track=track)
    results['stratified'] = stratified

    # ======================================================================
    # Step 6.5: LLM 概率诊断 (Chiu & Hung 2024 M3 降级适配)
    # ======================================================================
    # n_llm 包含聚合列 'llm'（= 独立模型数 + 1），此处仅做粗筛；
    # 函数内部过滤聚合列后会自行检查独立模型数 >= 2，不足则跳过两两比较
    if n_llm >= 2:
        bias_diag = diagnose_llm_category_bias(
            df, sentiment_cols['llm'], track, output_dir, logger
        )
        results['llm_bias_diagnostic'] = bias_diag

        calib_diag = diagnose_confidence_calibration(
            df, sentiment_cols['llm'], track, output_dir, logger
        )
        results['llm_calibration'] = calib_diag

    # ======================================================================
    # Step 7: 人工验证样本生成
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    五、人工验证样本生成    ===")
    logger.info("=" * 70)

    verify_path = os.path.join(output_dir, '09_sentiment_verify.xlsx')
    generate_validation_sample(
        df, all_labels_df, vote_labels, verify_path, logger,
        n_agree=100, n_disagree=200, seed=42
    )

    # ======================================================================
    # Step 8: 生成全部报告
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    生成验证报告    ===")
    logger.info("=" * 70)

    # JSON 结果（将 numpy 类型转换为原生 Python 类型）
    json_path = os.path.join(output_dir, f'sentiment_validation_results{track}.json')

    def _json_serializable(obj):
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Series):
            return obj.tolist()
        return str(obj)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=_json_serializable)
    logger.info(f"JSON 结果已保存: {json_path}")

    # LaTeX 表格
    latex_path = os.path.join(output_dir, f'sentiment_validation_table{track}.tex')
    generate_validation_latex(within_results, cross_results, latex_path, logger)

    # CSV 汇总
    csv_rows = []
    for method_pair, rho in cross_results.get('spearman_pairs', {}).items():
        csv_rows.append({'比较': method_pair, 'Spearman ρ': rho})
    if csv_rows:
        csv_path = os.path.join(output_dir, f'sentiment_cross_method{track}.csv')
        pd.DataFrame(csv_rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"跨方法对比 CSV: {csv_path}")

    # Cronbach's Alpha 汇总
    alpha_rows = []
    for method_name, alpha in within_results.get('cronbach_alpha', {}).items():
        alpha_rows.append({
            '方法': method_name,
            'N Models': within_results['n_models'].get(method_name, '?'),
            "Cronbach's Alpha": alpha,
        })
    if alpha_rows:
        csv_path = os.path.join(output_dir, f'cronbachs_alpha_summary{track}.csv')
        pd.DataFrame(alpha_rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"Cronbach's Alpha 汇总: {csv_path}")

    n_words = len(sentiment_cols['words'])
    n_bert = len(sentiment_cols['bert'])
    n_llm = len(sentiment_cols['llm'])
    total_methods = n_words + n_bert + n_llm
    logger.info(f"[{track}] 三角验证完毕: 词典={n_words}, BERT={n_bert}, LLM={n_llm}")


if __name__ == "__main__":
    main()
