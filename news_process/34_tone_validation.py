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
    │ 五、人工验证样本生成                                         │
    │    5.1 一致样本随机抽取                                      │
    │    5.2 不一致样本邻域加密抽取                                │
    └────────────────────────────────────────────────────────────┘

    学术依据：
      - Loughran & McDonald (2016, RFS): 多度量方法间的相关性是构建效度的核心证据
      - Cronbach (1951): 内部一致性系数 α ≥ 0.70 可接受
      - Chen et al. (2023, JFE): 文本度量的构建效度需多方法三角验证

输入：
    阶段 06 的最终 Parquet 文件（包含全部词典/BERT/LLM 列）

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

def discover_sentiment_columns(df: pd.DataFrame) -> dict:
    """自动发现 DataFrame 中的情感分析输出列。

    通过列名后缀模式匹配，自动识别词典法、BERT、LLM 各方法的输出列。

    Returns:
        dict: {
            'words': {dict_name: {'score': col, 'label': col}},
            'bert':  {short_name: {'label': col, 'probs': {label_name: col}}},
            'llm':   {short_name: {'sentiment': col, 'confidence': col}},
        }
    """
    columns = list(df.columns)
    result = {'words': {}, 'bert': {}, 'llm': {}}

    # 词典法列: {name}_score, {name}_label
    score_suffix = '_score'
    label_suffix = '_label'
    sentiment_suffix = '_sentiment'
    confidence_suffix = '_confidence'

    # 词典法：找 _score 列
    for col in columns:
        if col.endswith(score_suffix):
            dict_name = col[:-len(score_suffix)]
            label_col = f'{dict_name}{label_suffix}'
            if label_col in columns:
                result['words'][dict_name] = {
                    'score': col,
                    'label': label_col,
                }

    # LLM 法：找 _sentiment 列
    for col in columns:
        if col.endswith(sentiment_suffix):
            short_name = col[:-len(sentiment_suffix)]
            conf_col = f'{short_name}{confidence_suffix}'
            result['llm'][short_name] = {
                'sentiment': col,
                'confidence': conf_col if conf_col in columns else None,
            }

    # BERT 法：找 _label 列（排除已被词典法识别的；排除 LLM 的）
    words_names = set(result['words'].keys())
    llm_names = set(result['llm'].keys())
    for col in columns:
        if col.endswith(label_suffix):
            name = col[:-len(label_suffix)]
            if name not in words_names and name not in llm_names:
                probs = {}
                for c in columns:
                    if c.startswith(f'{name}_') and c != col:
                        prob_label = c[len(f'{name}_'):]
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
    """计算多方法标签一致率。

    Args:
        labels_df: 各列为分类标签（正面/中性/负面）的 DataFrame。

    Returns:
        dict: 包含完全一致率、多数一致率等指标。
    """
    valid = labels_df.dropna(how='any')
    n = len(valid)
    if n == 0:
        return {'full_agreement_rate': 0.0, 'majority_agreement_rate': 0.0,
                'n_samples': 0}

    full_agree = 0
    majority_agree = 0

    for _, row in valid.iterrows():
        values = row.values
        counter = Counter(values)
        most_common_count = counter.most_common(1)[0][1]
        if most_common_count == len(values):
            full_agree += 1
        if most_common_count >= len(values) / 2:
            majority_agree += 1

    return {
        'full_agreement_rate': round(full_agree / n, 4),
        'majority_agreement_rate': round(majority_agree / n, 4),
        'n_samples': n,
        'n_methods': labels_df.shape[1],
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
                   if c.startswith('方法_') or c in ('多数投票标签', '样本类型',
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
                        all_labels_df: pd.DataFrame, logger_inst) -> dict:
    """按新闻长度和时间段进行分层一致性分析。"""
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

    return results


# ============================================================================
# 10. 主函数
# ============================================================================

def main():
    """情感三角验证主入口。"""
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

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
    # Step 2: 自动发现情感列
    # ======================================================================
    sentiment_cols = discover_sentiment_columns(df)

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
            conf = df[cols_info['confidence']].astype(float).fillna(0.5)
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

    stratified = stratified_analysis(df, all_scores_df, all_labels_df, logger)
    results['stratified'] = stratified

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
    json_path = os.path.join(output_dir, 'sentiment_validation_results.json')

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
    latex_path = os.path.join(output_dir, 'sentiment_validation_table.tex')
    generate_validation_latex(within_results, cross_results, latex_path, logger)

    # CSV 汇总
    csv_rows = []
    for method_pair, rho in cross_results.get('spearman_pairs', {}).items():
        csv_rows.append({'比较': method_pair, 'Spearman ρ': rho})
    if csv_rows:
        csv_path = os.path.join(output_dir, 'sentiment_cross_method.csv')
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
        csv_path = os.path.join(output_dir, 'cronbachs_alpha_summary.csv')
        pd.DataFrame(alpha_rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"Cronbach's Alpha 汇总: {csv_path}")

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=len(df),
                      extra_info={
                          '词典法模型数': n_words,
                          'BERT模型数': n_bert,
                          'LLM模型数': n_llm,
                          '总方法/模型数': total_methods,
                      })
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
