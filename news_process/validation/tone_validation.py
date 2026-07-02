"""
news_process.validation.tone_validation — 阶段34：情感分析三角验证与报告生成

迁移说明 (Phase 7b)：
    本模块由原 root script ``64_tone_validation.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.tone_validation``

=====================================================

功能：
    对三种情感分析方法（词典法/BERT/LLM）进行系统性交叉验证，
    提供情感度量的【收敛效度 / convergent validity】证据（方法间趋同）。
    注 (measurement-validation-audit 2026-06-13): 本阶段为收敛效度，不等于
    【效标效度 / criterion validity】（vs 人工金标准）——后者由人工回读
    evaluate_human_verification 与 stage 33 提供，人工标注未填时为 pending；
    不得仅凭方法间一致性宣称"构念效度达顶刊标准"。

    验证内容：
    ┌────────────────────────────────────────────────────────────┐
    │ 一、内部一致性 (Within-Method Consistency)                   │
    │    1.1 各词典间 Spearman 相关矩阵                            │
    │    1.2 三 BERT 模型间 Spearman 相关矩阵                      │
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
    │ 4.5 LLM 概率诊断 (Chiu & Hung 2025 M3 降级适配)             │
    │    4.5a LLM 类别偏向分析 (chi-square + Jensen-Shannon)       │
    │    4.5b 置信度校准诊断 (ECE / 降级: 描述性统计)               │
    │                                                            │
    │ 五、人工验证样本生成                                         │
    │    5.1 一致样本随机抽取                                      │
    │    5.2 不一致样本过采样随机抽取                              │
    └────────────────────────────────────────────────────────────┘

    学术依据：
      - Loughran & McDonald (2016, JAR 54(4):1187-1230): 多度量方法间的相关性是构建效度的核心证据
      - Cronbach (1951, Psychometrika 16(3):297-334): 内部一致性系数 α ≥ 0.70 可接受
      - Chiu & Hung (2025, PBFJ 90:102632): Dirichlet 不确定性估计揭示 LLM 类别偏向
      - Carlson & Burbano (2026, SMJ 47(3):699-725): LLM 注释应报告 model certainty
      - Guo et al. (2017, ICML): Expected Calibration Error (ECE) 校准诊断

输入：
    阶段 21/22/23 输出的最终 Parquet 文件（包含全部词典/BERT/LLM 列）

输出：
    验证报告（CSV + PNG + LaTeX）+ 人工验证样本 Excel

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 64_tone_validation.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**职责**: 对三种情感方法 (词典法/BERT/LLM) 做系统交叉验证, 提供"方法间趋同"的**收敛效度** (convergent validity) 证据 —— 代码明确声明这不等于"效标效度"(vs 人工金标准), 后者靠人工回读 (evaluate_human_verification) 和 stage 33。

**输入**: `23_bert_tone.parquet` (含逐级累积的全部词典/BERT/LLM 列, config 键 output_23_bert_tone), 回退 `22_words_tone.parquet` (output_22_words_tone); 两者皆缺则 logger.error 并 return。

**处理步骤** (每轨 `_run_validation_for_track`):
1. `discover_sentiment_columns(df, track_suffix)` 按列名后缀自动识别词典 (`*_score{track}`/`*_label{track}`, IDF 词典单独分 words_idf 组防虚高)、BERT (`*_label{track}` + 正面/中性/负面概率列)、LLM (`*_sentiment{track}` + confidence) 三族列。聚合投票列 short_name=='llm' 被剔除出跨方法统计 (否则把成员模型合成票当第 4 个独立模型, 机械抬高一致性)。
2. **内部一致性**: 各族算 Cronbach's α `(k/(k-1))(1-Σσ²ᵢ/σ²ₜ)` + Spearman 相关矩阵 + 热力图。
3. **跨方法一致性**: 词典综合 vs BERT vs LLM 的 Spearman/Pearson; 标签一致率 (完全一致 = nunique==1; 多数一致 = 众数票数 > 方法数/2 的严格多数)。
4. **分层稳健性** `stratified_analysis`: 按新闻长度 (33/66 分位)、年度、词典覆盖率分层, 每层算 α + 观测一致率; 年度 α 序列 ≥5 年做 Spearman 趋势检验 (预警 temporal drift)。
5. **LLM 概率诊断**: 类别偏向 (chi-square + Jensen-Shannon) + 置信度校准 ECE。
6. **人工验证样本生成** `generate_validation_sample`: 一致样本随机抽 n_agree=100 + 分歧样本随机抽 n_disagree=200 (对分歧案例 2:1 过采样, 经 RandomState(seed) 简单 choice — **非几何/邻域加密**, 只是对存在分歧的文章集做无放回随机抽样并放大配额), 附"机器输入文本"列 (content_full/ctx/ss) 与轨道专属编码指南, 写 `09_sentiment_verify{track}.xlsx`。配套 `evaluate_human_verification` 回读端: 对工作台内全部方法列 (词典 6: jiang/yao/bian/du/you/loughran 自 2026-06-18 起 / BERT 3 / LLM 逐模型+多数投票, 约 12, 实际方法数由 discover_sentiment_columns 动态发现) vs 人工判定算 accuracy/macro-P/R/F1 + Cohen κ (复用 stage 33 的 compute_classification_metrics / compute_cohens_kappa, 这是全项目唯一能给词典/BERT 族产出人工指标的路径); 空表 pending 绝不合成, `count_human_annotations` 做 fail-closed 防覆盖守卫 (pending 时清陈旧 CSV, error 时保留)。

**关键公式**: Cronbach α / Spearman ρ / Krippendorff (复用) / Jensen-Shannon 散度 / ECE / Cohen κ。标签数值化: 正面=+1/中性=0/负面=-1, 缺失保 NaN (不 fillna(0) 伪造中性)。

**外部依赖**: pandas/numpy/scipy (spearmanr 等, 有回退) / matplotlib / openpyxl。无 LLM/Embedding API, $0。

**DAG 位置**: 验证支线 stage 34, 上游 = stage 21/22/23 三方法文章级产出; 下游 = 人工回读 (跨阶段闭环到 stage 33 口径)。

■ 白话说明

这一步是"三个裁判交叉验票": 我们用三种完全不同的方法给每篇新闻判情感 —— 一是查情感词典 (数好词坏词), 二是 BERT 神经网络模型, 三是 LLM 大模型。这一步检查三者打分一致不一致。如果三种风马牛不相及的方法都说"这篇是负面", 那这个结论就非常可信; 如果它们经常吵架, 说明情感测量本身不稳。

用到的指标都很直观: Cronbach's α 衡量"几个测量是否在量同一件事"(≥0.7 算可接受), Spearman ρ 衡量两种方法排序是否一致, 还会按新闻长短、按年份分组看一致性稳不稳 (防止 AI 模型"随年代越用越漂")。它还会出一张人工抽查表, 专门多抽"三裁判吵架"的疑难篇 (分歧篇配额是一致篇的两倍) 让人裁决。

关键诚实声明: 三种机器方法互相一致, 只能说"它们彼此趋同"(收敛效度), 不能直接等于"它们都对"(那要跟人工答案比, 叫效标效度) —— 代码里反复强调这一点, 防止论文夸大。对最终面板的影响: 不直接改情感数据, 但它给"我们的情感测量可靠"提供了证据链; 三轨各出一份报告, 让 full/ctx/ss 三个版本的情感测度都各自有可信度背书, 主回归用哪一轨都有据可依。
========================================================================
"""

import json
import os
import re
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/tone_validation.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import (
    log_memory_usage,
    log_stage_summary,
    pct4,
    setup_logging,
    sig4,
)

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "64_tone_validation"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# ============================================================================
# 2. 列名自动发现
# ============================================================================

def discover_sentiment_columns(df: pd.DataFrame, track_suffix: str = '') -> dict:
    """自动发现 DataFrame 中指定轨道的情感分析输出列。

    通过列名后缀模式匹配，自动识别词典法、BERT、LLM 各方法的输出列。

    Args:
        df:           DataFrame
        track_suffix: 轨道后缀，如 '_full' / '_ctx' / '_ss'。为空则匹配无后缀列(向后兼容)。

    Returns:
        dict: {
            'words':     {dict_name: {'score': col, 'label': col}},
            'words_idf': {dict_name: {'score': col, 'label': col}},  # IDF 稳健性组
            'bert':      {short_name: {'label': col, 'probs': {label_name: col}}},
            'llm':       {short_name: {'sentiment': col, 'confidence': col}},
        }

        注 (fix omni-g-val-tone-01, 2026-06-11): 'bert' 组保证不含词典 (等权/IDF)
        与 LLM 名; probs 仅收情感类别概率列 (正面/中性/负面), 不收 zscore 等派生列。
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
    # fix(omni-g-val-tone-01, 2026-06-11): 此前仅排除等权词典名 + LLM 名, 未排除
    # IDF 词典名 (result['words_idf']) → jiang_2021_idf 等 5 个 IDF 词典的
    # *_label 列被误判为 "BERT 模型" (其 *_zscore 列被当作概率列), 结构性污染
    # BERT 组 Cronbach α / 跨方法一致率 / 词典覆盖率分层稳健性 (盘上实测
    # "BERT N Models=8, α=0.894" 实为 3 真 BERT + 5 词典, 纯 BERT α=0.699)。
    words_names = set(result['words'].keys())
    words_idf_names = set(result['words_idf'].keys())
    llm_names = set(result['llm'].keys())
    for col in columns:
        if col.endswith(label_suffix):
            name = col[:-len(label_suffix)]
            if (name in words_names or name in words_idf_names
                    or name in llm_names or '_idf' in name):
                # '_idf' 子串守卫与词典法分支同一判别式 (见上方 words_idf 分组),
                # 防 IDF 列缺 score 对时绕过 words_idf 集合再次泄漏进 BERT 组
                continue
            probs = {}
            for c in columns:
                # 查找同 track 的概率列：{name}_{prob_label}{track_suffix}
                if c.startswith(f'{name}_') and c.endswith(track_suffix) and c != col:
                    # 去除前缀和后缀得到 prob_label
                    prob_label = c[len(f'{name}_'):]
                    if track_suffix:
                        prob_label = prob_label[:-len(track_suffix)]
                    # fix(omni-g-val-tone-01, 2026-06-11): probs 从黑名单收紧为
                    # 情感类别白名单 — 真 BERT 概率列只有 {name}_{正面|中性|负面}
                    # (tone_berts.py 写出格式), zscore / ratio 等派生列不是概率
                    if prob_label in ('正面', '中性', '负面'):
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
    """将情感标签转为数值：正面=+1, 中性=0, 负面=-1。

    audit-fixes 2026-05-29: 未映射/缺失 (LLM 调用失败或未定义) 保留为 NaN, 不再
    silently fillna(0) 当作真实"中性"。否则失败行会作为人造中性观测污染
    Cronbach α / 跨方法 Spearman / 加权共识 (实测 α 0.8156→0.7677 虚高 0.048)。
    下游 compute_cronbachs_alpha 的 dropna()、pandas .corr()、weighted_average_score
    的 mean/加权分支均 NaN-aware, 会正确排除这些行, 与 label 路径
    compute_label_agreement_rate 的 dropna(how='any') 保持同一 n。
    """
    return series.map(SENTIMENT_MAP).astype(float)


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

    # 多数一致 (audit-fixes 2026-05-29): 严格多数 > 列数/2, 不再用 >= (后者把
    # 偶数方法数的 k/2-k/2 平局误判为多数, 且 2 方法时退化为恒等 1.0)。
    mode_counts = valid.apply(lambda row: row.value_counts().iloc[0], axis=1)
    majority_agree = int((mode_counts > n_methods / 2).sum())

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
                                seed: int = 42,
                                track: str = '_full',
                                extra_labels: dict | None = None):
    """生成情感标签人工验证样本。

    抽样策略：
      - 一致样本：所有方法标签一致的文章中随机抽取 n_agree 篇
      - 不一致样本：存在分歧的文章中随机抽取 n_disagree 篇

    fix(omni-g-val-tone-04, 2026-06-11): 编码协议与被验证构念对齐 —
      (a) 调用方按 track 写独立文件 (此前共写同一 xlsx, _ctx 覆盖 _full,
          标注归属轨道不可追溯);
      (b) 编码指南随 track 切换: v3.8.0 起三轨机器输入均为 prepend_title 后
          文本 (full=标题+正文, ctx=标题+实体上下文窗口, ss=标题+银行+金科同句
          共现片段), 旧指南"不受标题影响"指示人类剔除标题信息, 与机器口径
          系统性错位;
      (c) 样本附带被验证轨道的机器输入文本列 (content_full / content_ctx /
          content_ss, 若存在), 让人工阅读与机器消费同一文本。

    Args:
        df:              原始 DataFrame（含标题、内容等）。
        all_labels_df:   各方法标签的 DataFrame。
        vote_labels:     多数投票合成标签。
        output_path:     Excel 输出路径。
        logger_inst:     日志记录器。
        n_agree:         一致样本抽样数。
        n_disagree:      不一致样本抽样数。
        seed:            随机种子。
        track:           被验证轨道 ('_full' / '_ctx' / '_ss'), 决定编码指南口径与
                         机器输入文本列。
        extra_labels:    附加标签列 {列名: pd.Series} — 仅写入工作台供人工
                         比对, 不参与一致/分歧抽样判定。用途 (final-audit F1,
                         2026-06-13): LLM 聚合投票列 (主 spec llm_vote_tone
                         的直接源) 被 omni-02 从 all_labels_df 剔除 (防互比
                         一致性虚高), 但人工验证恰恰最需要验证它 — 经此参数
                         回灌, 聚合票在工作台可被标注并经回读获得人工指标。
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

    # 附加标签列 (不参与一致/分歧判定, 见 docstring extra_labels)
    for extra_name, extra_series in (extra_labels or {}).items():
        sample_df[extra_name] = extra_series.loc[sample_idx]

    # 添加多数投票标签
    sample_df['多数投票标签'] = vote_labels.loc[sample_idx]

    # 添加抽样来源标记
    sample_df['样本类型'] = '一致'
    sample_df.loc[sample_df.index.isin(disagree_sample), '样本类型'] = '分歧'

    # 添加人工编码列
    sample_df['人工判定_情感'] = ''
    sample_df['人工判定_理由'] = ''

    # fix(omni-g-val-tone-04, 2026-06-11): 附上被验证轨道的机器输入文本
    # (prepend_title 后), 让人工标注口径与机器口径一致
    # 三轨映射: _ctx→content_ctx / _ss→content_ss / 其余(_full)→content_full
    track_text_col = {
        '_ctx': 'content_ctx',
        '_ss': 'content_ss',
    }.get(track, 'content_full')
    if track_text_col in sample_df.columns:
        sample_df['机器输入文本'] = sample_df[track_text_col]
    else:
        logger_inst.warning(
            f"  机器输入文本列 '{track_text_col}' 不存在 — 验证样本仅含原始"
            f" 标题/内容 列, 人工口径与机器口径可能存在差异 (需 stage 13 物化)"
        )

    # 保留核心列
    keep_cols = []
    for col in ['标题', '内容', '机器输入文本', '日期', '媒体(中文)']:
        if col in sample_df.columns:
            keep_cols.append(col)

    method_cols = [c for c in sample_df.columns
                   if c.startswith(('词典_', 'BERT_', 'LLM_'))
                   or c in ('多数投票标签', '样本类型',
                            '人工判定_情感', '人工判定_理由')]
    keep_cols.extend(method_cols)

    sample_output = sample_df[keep_cols].copy()

    # fix(omni-g-val-tone-04, 2026-06-11): 编码指南与机器文本口径对齐 —
    # v3.8.0 起 full=标题+正文 / ctx=标题+实体上下文窗口 (均 prepend_title),
    # 三轨扩展: ss=标题+银行+金科同句共现片段 (镜像 ctx 口径, 窗口收窄到同句),
    # 旧指南"不受标题影响"与被验证测度的文本口径系统性错位
    if track == '_ctx':
        track_desc = ('ctx 轨 (上下文窗口): 机器输入 = 标题+目标实体上下文窗口 '
                      '(见"机器输入文本"列), 请基于该窗口文本判断, 勿引入'
                      '窗口外的全文信息')
        coding_note = ('基于"标题+实体上下文窗口"文本(见"机器输入文本"列)的'
                       '整体语调判断, 标题计入判断; 客观报道标为中性')
    elif track == '_ss':
        track_desc = ('ss 轨 (银行+金科同句): 机器输入 = 标题+银行与金科同句共现片段 '
                      '(见"机器输入文本"列), 请基于该同句片段判断, 勿引入'
                      '片段外的全文信息')
        coding_note = ('基于"标题+银行+金科同句共现片段"文本(见"机器输入文本"列)的'
                       '整体语调判断, 标题计入判断; 客观报道标为中性')
    else:
        track_desc = ('full 轨 (全文): 机器输入 = 标题+正文全文 '
                      '(见"机器输入文本"列), 请基于标题+正文判断')
        coding_note = ('基于"标题+正文"整体语调判断, 标题计入判断; '
                       '客观报道标为中性')

    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 编码指南
            guide_data = pd.DataFrame({
                '项目': [
                    '目的',
                    '验证轨道',
                    '情感标签定义',
                    '编码规则',
                    '注意事项',
                    '样本来源说明',
                ],
                '说明': [
                    '对情感分析方法进行人工验证，评估自动化方法的准确性',
                    track_desc,
                    '正面: 积极/利好; 中性: 客观描述; 负面: 消极/风险',
                    '在"人工判定_情感"列填写: 正面/中性/负面; 在"人工判定_理由"列简述原因',
                    coding_note,
                    '"一致"=各方法结果一致的样本; "分歧"=各方法结果不一致的样本',
                ],
            })
            guide_data.to_excel(writer, sheet_name='编码指南', index=False)

            # 验证数据
            sample_output.to_excel(writer, sheet_name='验证数据', index=False)

            # 统计概览
            # fix(final-audit HV-P2-03, 2026-06-13): 生成时点锚点 — 工作台
            # 内的机器标签是本时点快照, 防覆盖守卫生效后上游再迭代时,
            # 回读指标可经此字段追溯其对应的方法版本时点
            overview = pd.DataFrame({
                '统计项': [
                    '总验证样本数',
                    '一致样本数',
                    '分歧样本数',
                    '参与方法数',
                    '生成时间',
                    '源数据行数',
                ],
                '值': [
                    len(sample_output),
                    n_a,
                    n_d,
                    all_labels_df.shape[1] + len(extra_labels or {}),
                    time.strftime('%Y-%m-%d %H:%M:%S'),
                    len(df),
                ],
            })
            overview.to_excel(writer, sheet_name='统计概览', index=False)

        logger_inst.info(f"人工验证样本已保存: {output_path} ({len(sample_output)} 条)")
    except Exception as e:
        logger_inst.warning(f"保存人工验证样本失败: {e}")


# ============================================================================
# 8b. 人工标注回读比对 (human-annot-readback, 2026-06-13)
# ============================================================================
# 此前 09_sentiment_verify{track}.xlsx 只有生成端没有消费端 — 全仓无任何代码
# 读回 '人工判定_情感' 列计算指标, 词典/BERT 族即使标注完成也无比对路径
# (stage 33 评估循环只接 LLM 列)。本节补齐回读端: 对工作台内全部方法标签列
# (词典_*/BERT_*/LLM_*/多数投票标签) vs 人工判定计算 accuracy/macro-P/R/F1 +
# Cohen's κ, 空表优雅 pending (绝不合成数据, 防 demo 假产物覆辙)。
# 白话: 以前考卷只管印出来, 没人负责批改 — 哪怕标注员填完了, 词典和 BERT
# 的得分也算不出来。现在补上"批改"环节: 表填了就出全部方法 (词典 6+BERT 3+LLM, 约 12 种) 的真实成绩单,
# 没填就明确说"待标注", 绝不编造分数。

#: 人工标注样本量低于此阈值时指标仅供参考 (CLT 经验下限)
HUMAN_VERIFY_MIN_N = 30

#: 三分类合法人工标签 (与编码指南/stage 33 评估口径一致)
HUMAN_VERIFY_LABELS = ('正面', '中性', '负面')


def _human_verify_track_note(track: str) -> str:
    """被验证轨道的金标准构念口径说明 (随指标产物落盘, 防论文误读)。

    与 stage 33 (61_human_samples, 全文构念 gold 同评三轨 → ctx/ss 指标为混合
    下界, 见 llms_evaluation.GOLD_CONSTRUCT_DISCLOSURE) 不同: 本工作台自
    omni-g-val-tone-04 起按轨独立抽样, 编码者基于该轨"机器输入文本"判定,
    金标准与机器口径构念对齐 — ctx/ss 轨在此获得真正的窗口级金标准。
    """
    # fix(final-audit HV-P2-02/F2, 2026-06-13): 追加抽样设计 + 编码协议披露 —
    # 指标基于 100一致+200分歧 的选择性抽样 (分歧 oversample), 且 gold 为
    # 单编码者无信度检验, 论文引用时不可当总体准确率/双编码者共识口径
    sampling_note = ('; 抽样=100一致+200分歧(分歧oversample, 选择性样本, '
                     'accuracy 为保守下界不可外推总体, 分层指标见 '
                     'Accuracy_一致/Accuracy_分歧 列); gold=单编码者'
                     '(无编码者间信度, 区别于 stage 33 双编码者共识协议)')
    if track == '_ctx':
        return ('轨道级金标准: 编码者基于"机器输入文本"(标题+实体上下文窗口)判定, '
                '与 ctx 轨机器口径构念对齐, 无全文-窗口构念混淆; 区别于 stage 33 '
                '的 61_human_samples (全文构念 gold, 其 ctx 指标只能解读为混合下界)'
                + sampling_note)
    if track == '_ss':
        return ('轨道级金标准: 编码者基于"机器输入文本"(标题+银行+金科同句共现片段)判定, '
                '与 ss 轨机器口径构念对齐, 无全文-同句构念混淆; 区别于 stage 33 '
                '的 61_human_samples (全文构念 gold, 其 ss 指标只能解读为混合下界)'
                + sampling_note)
    return ('轨道级金标准: 编码者基于"机器输入文本"(标题+正文全文)判定, '
            '与 full 轨机器口径构念对齐' + sampling_note)


def _count_nonempty(series: pd.Series) -> int:
    """计数非空且非 NaN 字面量的单元格。

    ⚠ pandas 3.0 起 astype(str) 保留 NaN (不再字符串化为 'nan') — 必须先
    把缺失置 '' 否则 NaN != '' 为 True, 空单元格被误计 (final-audit 实测)。
    fix(re-audit ATK-P2-01, 2026-06-13): 改 dtype 无关写法 — fillna('') 对
    datetime64 列是静默 no-op (NaT 原样保留→被误计); 先 astype('object')
    再 where 对任意 dtype 都正确置空。'nan'/'none'/'nat' 字面量守卫防
    旧版 pandas 字符串化残留。
    """
    obj = series.astype('object')
    s = obj.where(obj.notna(), '').astype(str).str.strip()
    return int(((s != '') & (~s.str.lower().isin(('nan', 'none', 'nat')))).sum())


def count_human_annotations(verify_path: str) -> int:
    """统计人工验证工作台中"人工动过"的单元格条数 (防覆盖守卫判据)。

    fix(final-audit HV-P1-01/02, 2026-06-13) 守卫语义 = "有人动过这张表
    就不许覆盖", 而非"有合法标签才不许覆盖":
      - 计数口径: 人工判定_情感 + 人工判定_理由 两列的全部非空单元格
        (标注员用错词汇如'积极'/数字编码、或只写了理由, 同样是不可再生
        的人工劳动, 必须受保护);
      - fail-closed: 文件存在但读取失败 (sheet 被改名/文件损坏) 或
        结构异常 (人工判定列全部丢失) 返回 -1 — 读失败≠无标注,
        宁可跳过重生也不冒销毁标注的风险。
    返回: 0=确认空白(允许重生) / >0=有人工痕迹 / -1=读取失败或结构异常。
    白话: 这张表只要有人写过一个字、或者打不开看不清, 都一律不准重印。
    """
    if not os.path.isfile(verify_path):
        return 0
    try:
        verify_df = pd.read_excel(verify_path, sheet_name='验证数据')
    except Exception:
        return -1
    human_cols = [c for c in ('人工判定_情感', '人工判定_理由')
                  if c in verify_df.columns]
    if not human_cols:
        return -1
    return sum(_count_nonempty(verify_df[c]) for c in human_cols)


def evaluate_human_verification(verify_path: str, track: str,
                                output_dir: str, logger_inst) -> dict:
    """回读人工验证工作台, 对全部方法标签列 vs 人工判定计算分类指标。

    覆盖全部情感方法 (词典 6: jiang/yao/bian/du/you/loughran 自 2026-06-18 起 / BERT 3 /
    LLM 逐模型+投票, 约 12, 实际方法数由 discover_sentiment_columns 动态发现) × 本轨道 —
    这是全项目唯一能为词典/BERT 族产出人工验证指标的代码路径 (stage 33
    评估循环只接 LLM 列)。

    指标实现复用 stage 33 单一事实源 (compute_classification_metrics /
    compute_cohens_kappa), 保证与 LLM 族在 61_human_samples 上的口径可比。

    Args:
        verify_path: 工作台路径 (09_sentiment_verify{track}.xlsx)。
        track:       '_full' / '_ctx' / '_ss'。
        output_dir:  指标 CSV 输出目录 (eval_reports/)。
        logger_inst: 注入 logger。

    Returns:
        dict: status ∈ {'ok','insufficient','pending','error'} + 指标明细;
              并入 stage 34 results JSON 的 'human_verification' 键。
              pending/error 时【不写任何指标文件】— 防止空壳/合成产物被
              误引为已完成的人工验证 (2026-05-31 demo 假产物的教训)。
    """
    note = _human_verify_track_note(track)
    result = {'status': 'pending', 'track': track, 'n_annotated': 0,
              'gold_construct_note': note}
    csv_path = os.path.join(output_dir, f'human_verify_metrics{track}.csv')

    def _cleanup_stale_csv(why: str):
        # fix(final-audit T4-01, 2026-06-13): pending (确认无标注) 时不仅
        # 不写新指标, 还要清掉旧指标残留 — 否则"工作台被清空/重生"后陈旧
        # CSV 仍像已完成的人工验证 (与 demo 假产物同型的误引风险)。
        # 刻意不对称 (re-audit T3-02 裁决): error 路径【保留】旧 CSV —
        # error=不可判定 (工作台可能损坏但曾有真实标注), 旧 CSV 可能正是
        # 那批标注的唯一合法指标记录, 删除反而销毁; 状态以 JSON error 为准
        if os.path.isfile(csv_path):
            try:
                os.remove(csv_path)
                logger_inst.warning(
                    f"  已清除陈旧指标文件 ({why}, 防误引): {csv_path}")
            except OSError as e:
                logger_inst.warning(f"  陈旧指标文件清除失败: {e}")

    if not os.path.isfile(verify_path):
        result['reason'] = f'工作台不存在: {verify_path}'
        logger_inst.info(f"  人工标注回读: {result['reason']}")
        _cleanup_stale_csv('工作台不存在')
        return result
    try:
        verify_df = pd.read_excel(verify_path, sheet_name='验证数据')
    except Exception as e:
        result['status'] = 'error'
        result['reason'] = f'工作台读取失败: {e}'
        logger_inst.warning(f"  人工标注回读: {result['reason']}")
        return result
    if '人工判定_情感' not in verify_df.columns:
        result['status'] = 'error'
        result['reason'] = "工作台缺少'人工判定_情感'列"
        logger_inst.warning(f"  人工标注回读: {result['reason']}")
        return result

    labels = list(HUMAN_VERIFY_LABELS)
    gold = verify_df['人工判定_情感'].astype(str).str.strip()
    annotated = gold.isin(labels)
    n_annotated = int(annotated.sum())
    result['n_annotated'] = n_annotated

    # fix(final-audit HV-P1-02, 2026-06-13): 非空但不在词表的人工填写
    # (如'积极'/'1') 显式告警, 不再静默当空表
    n_invalid = _count_nonempty(verify_df['人工判定_情感']) - n_annotated
    result['n_nonempty_invalid'] = n_invalid
    if n_invalid > 0:
        logger_inst.warning(
            f"  [{track}] 发现 {n_invalid} 条非法人工标注值 (不在 "
            f"{'/'.join(labels)} 词表, 不进评估) — 请修正后重跑")

    if n_annotated == 0:
        result['reason'] = ('人工标注未填写 (0 条合法标签) — 编码者填写'
                            '"人工判定_情感"列后重跑 stage 34 即产出'
                            '全部方法×本轨 vs 人工的真实指标')
        logger_inst.info(f"  人工标注回读 [{track}]: {result['reason']}")
        _cleanup_stale_csv('合法标注为 0')
        return result

    # 复用 stage 33 指标实现 (lazy import: 避免 import 期连带其日志初始化)
    from news_process.validation.llms_evaluation import (
        compute_classification_metrics,
        compute_cohens_kappa,
    )

    label_to_int = {lab: i for i, lab in enumerate(labels)}
    # fix(final-audit HV-INFO-03, 2026-06-13): 剔除 pandas 对 Excel 重复表头
    # 自动改名产生的 '列名.1' 镜像列, 防同一方法重复计入。
    # re-audit ATK-INFO-02: 仅当去掉 .N 后缀的基名也在列集合中才视为
    # mangle (真 mangle 必有同名基列), 防误杀含点号的真实方法名 (如 gpt4.1)
    def _is_mangled_dup(col: str) -> bool:
        m = re.search(r'\.\d+$', col)
        return bool(m) and col[:m.start()] in verify_df.columns

    method_cols = [c for c in verify_df.columns
                   if (c.startswith(('词典_', 'BERT_', 'LLM_'))
                       or c == '多数投票标签')
                   and not _is_mangled_dup(c)]

    if not method_cols:
        # fix(final-audit HV-P2-05, 2026-06-13): schema 异常 (无任何方法列)
        # 按 error 处理, 绝不写退化空 CSV 冒充已完成
        result['status'] = 'error'
        result['reason'] = '工作台无任何方法标签列 (词典_/BERT_/LLM_) — schema 异常'
        logger_inst.warning(f"  人工标注回读: {result['reason']}")
        return result

    # 工作台生成时点透传 (final-audit HV-P2-03): 指标对应的是工作台冻结
    # 时点的机器预测快照, 落盘供 staleness 追溯; 旧版工作台无此字段则空
    workbook_ts = ''
    try:
        ov = pd.read_excel(verify_path, sheet_name='统计概览')
        ts_rows = ov[ov['统计项'] == '生成时间']
        if not ts_rows.empty:
            workbook_ts = str(ts_rows['值'].iloc[0])
    except Exception:
        pass

    # 分层掩码 (final-audit HV-P2-02): 一致/分歧 oversample 抽样下, 分层
    # accuracy 是比合并 accuracy 更可解释的量
    stype = (verify_df['样本类型'].astype(str).str.strip()
             if '样本类型' in verify_df.columns else None)

    csv_rows = []
    per_method = {}
    for col in method_cols:
        pred = verify_df[col].astype(str).str.strip()
        valid = annotated & pred.isin(labels)
        n_valid = int(valid.sum())
        if n_valid == 0:
            csv_rows.append({'方法': col, '轨道': track,
                             'n_标注': n_annotated, 'n_有效': 0,
                             '状态': '无有效预测', '口径说明': note})
            continue
        y_true = gold[valid].to_numpy()
        y_pred = pred[valid].to_numpy()
        m = compute_classification_metrics(y_true, y_pred, labels=labels)
        kappa = compute_cohens_kappa(
            np.array([label_to_int[v] for v in y_true]),
            np.array([label_to_int[v] for v in y_pred]))
        # fix(final-audit HV-P2-04): 样本量状态按方法级 n_valid 判定,
        # 不再沿用全表 n_annotated (各方法预测缺失程度不同)
        method_status = ('正常' if n_valid >= HUMAN_VERIFY_MIN_N
                         else f'样本不足(n<{HUMAN_VERIFY_MIN_N}) 仅供参考')
        strat_acc = {}
        if stype is not None:
            for s_name in ('一致', '分歧'):
                s_mask = valid & (stype == s_name)
                n_s = int(s_mask.sum())
                strat_acc[s_name] = (
                    round(float((gold[s_mask] == pred[s_mask]).mean()), 4)
                    if n_s > 0 else '')
        csv_rows.append({
            '方法': col,
            '轨道': track,
            'n_标注': n_annotated,
            'n_有效': n_valid,
            'Coverage': round(n_valid / n_annotated, 4),
            'Accuracy': m['accuracy'],
            'Accuracy_一致': strat_acc.get('一致', ''),
            'Accuracy_分歧': strat_acc.get('分歧', ''),
            'Macro_Precision': m['macro']['precision'],
            'Macro_Recall': m['macro']['recall'],
            'Macro_F1': m['macro']['f1'],
            'Cohens_κ_vs_人工': kappa['kappa'],
            '状态': method_status,
            '工作台生成时间': workbook_ts,
            '口径说明': note,
        })
        per_method[col] = {'n_valid': n_valid,
                           'coverage': round(n_valid / n_annotated, 4),
                           'accuracy': m['accuracy'],
                           'accuracy_by_stratum': strat_acc,
                           'macro': m['macro'],
                           'per_class': m['per_class'],
                           'kappa_vs_human': kappa['kappa'],
                           'status': method_status}
        logger_inst.info(
            f"  [{track}] {col}: Acc={sig4(m['accuracy'])} "
            f"MacroF1={sig4(m['macro']['f1'])} κ={sig4(kappa['kappa'])} "
            f"(n={n_valid:,}/{n_annotated:,})")

    pd.DataFrame(csv_rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
    logger_inst.info(f"  人工验证指标已保存: {csv_path} ({len(per_method)} 个方法)")

    result['status'] = ('ok' if n_annotated >= HUMAN_VERIFY_MIN_N
                        else 'insufficient')
    result['min_n'] = HUMAN_VERIFY_MIN_N
    result['workbook_generated_at'] = workbook_ts
    result['metrics'] = per_method
    result['csv'] = csv_path
    return result


# ============================================================================
# 9. 分层分析
# ============================================================================

def stratified_analysis(df: pd.DataFrame, all_scores_df: pd.DataFrame,
                        all_labels_df: pd.DataFrame, logger_inst,
                        track: str = '_full') -> dict:
    """按新闻长度、时间段和词典覆盖率进行分层一致性分析 (Plan-r3 P3-16 docstring 扩充)。

    分层维度:
        - **新闻长度**: 按分位数 q33/q66 切分为 短/中/长 (非固定字数阈值; 日志标签 <33%/<66%/>66%)
        - **时间段**: 按年度 / 按 DCEP 政策时点前后
        - **词典覆盖率**: 按分位数 q33/q66 切分为 高/中/低 (<33%/33-66%/>66%) + 零覆盖

    每个 strata 内分别计算各方法的 Cronbach α (内部一致性) 与
    full-agreement-rate (未校正的观测一致率)。注 (audit-fixes 2026-05-29):
    本函数并不计算 Cohen κ (chance-corrected) — 修正此前 docstring 误称
    "两两 Cohen Kappa" (全模块无 κ 实现)。

    Args:
        df:              主面板 (含 sentiment_*_score / label 列)
        all_scores_df:   同 df, 但只保留情感分数列, 与 all_labels_df 1:1 对齐
        all_labels_df:   同 df, 只保留 LLM/词典/BERT label 列
        logger_inst:     注入的 logger (避免顶层 logger 多进程串扰)
        track:           '_full' (全文) / '_ctx' (上下文) / '_ss' (银行+金科同句)

    Returns:
        dict: ``{strata_kind: {strata_value: {n_samples, cronbach_alpha,
              full_agreement_rate}}}`` 用于 stage 34 报告渲染 (audit-fixes
              2026-05-29: 修正此前误标的 ``{pair: kappa}`` 返回形状)。
    """
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
                f"α={sig4(alpha)}, 完全一致率={sig4(agreement['full_agreement_rate'])}"
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
                f"α={sig4(alpha)}, 完全一致率={sig4(agreement['full_agreement_rate'])}"
            )

        results['by_year'] = year_results

        # --- 年际一致性趋势检测 ---
        # 方法论依据: 跨时间泛化是深度学习金融情感分析的核心稳健性威胁
        # (详见 Anis, S. (2024). "Fintech Sentiment Analysis Using Deep
        # Learning Approaches: A Survey", IEEE §III Challenge [21])。
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
                        f"  ✓ 年际α完全一致 (n={n_valid:,}年，"
                        f"α={sig4(alpha_arr_sp.mean())}，无变异)"
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
                                f"  年际一致性趋势: α 呈显著下降 "
                                f"(ρ={sig4(rho)}, p={sig4(p_val)}, n={n_valid:,}年)"
                            )
                            logger_inst.warning(
                                f"     解读: 模型可能存在时间漂移(temporal drift)，"
                                f"建议检查近年数据的语义分布变化"
                            )
                        else:
                            logger_inst.info(
                                f"  ✓ 年际一致性趋势: 无显著衰减 "
                                f"(ρ={sig4(rho)}, p={sig4(p_val)}, n={n_valid:,}年)"
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
                            f"mean={sig4(alpha_arr.mean())}, std={sig4(alpha_arr.std())}"
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
                    f"  ℹ️ 年际α描述性统计 (n={n_valid:,}<5，不做推断): "
                    f"mean={sig4(alpha_arr.mean())}, std={sig4(alpha_arr.std())}"
                )
            else:
                trend_result = {
                    'test': 'skipped',
                    'reason': f'有效年份 {n_valid} < 3',
                }

            results['temporal_drift'] = trend_result

    # --- 按 BERT 窗口数分层（单窗口 vs 多窗口） ---
    _nw_col = f'bert_num_windows{track}'
    if _nw_col in df.columns:
        nw = df[_nw_col]
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
                    f"α={sig4(alpha)}, 完全一致率={sig4(agreement['full_agreement_rate'])}"
                )

            results['by_window_count'] = window_results
        else:
            logger_inst.info(f"  {_nw_col} 有效样本不足 40，跳过窗口数分层分析")
    else:
        logger_inst.info(f"  {_nw_col} 列不存在，跳过窗口数分层分析（需先运行阶段 23 落该轨列）")

    # --- 按词典覆盖率分层 ---
    # 方法论依据: lexicon 方法的词汇覆盖率限制是核心挑战
    # (参见: Rizinski, M. et al. (2024). "Sentiment Analysis in Finance:
    # From Transformers Back to eXplainable Lexicons (XLex)", IEEE Access)。
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
                    f"α(BERT+LLM)={sig4(alpha)}, "
                    f"一致率={sig4(agreement['full_agreement_rate'])}"
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
                            f"  覆盖率依赖: Δα={sig4(delta)}，"
                            f"词典法锚点在低覆盖率文章中不可靠"
                        )
                    elif delta < -0.10:
                        logger_inst.warning(
                            f"  覆盖率非单调: Δα={sig4(delta)} (低覆盖 α 反高于高覆盖)，"
                            f"提示覆盖率代理与一致性非单调, 需进一步排查 (非简单'稳健')"
                        )
                    else:
                        logger_inst.info(
                            f"  ✓ BERT+LLM 跨覆盖率稳健 (|Δα|={sig4(abs(delta))}≤0.10)"
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
# 9.5 LLM 概率诊断 (Chiu & Hung 2025 M3 降级适配)
# ============================================================================

# ── 经核验参考文献 (LLM 诊断子族; 逐字照抄 APA-7 + DOI, 仅运行期日志用) ──
# 黄金范式 (mirrors pipeline/panel/geography.py::_GEO_REFERENCES): 让本节诊断的
# logs/64_tone_validation.log 自证方法学锚点 (非仅留注释)。三条 DOI 均经 Crossref/
# DataCite 核验注册表确认 status=match, 各自与所记录的具体方法严格对位:
#   · chiu_hung_2025  = 本节 LLM 类别偏向诊断的奠基思路 (Neutral 偏好 / 类别不确定性)
#   · lin_1991_jsd    = 模型间分布散度所用 Jensen-Shannon 散度 (_compute_jsd) 的原始出处
#   · geng_2024_calib = LLM 自报置信度校准 (ECE) 诊断的当代综述对标
_LLM_DIAG_REFERENCES = {
    "chiu_hung_2025": (
        "Chiu, I.-C., & Hung, M.-W. (2025). Finance-specific large language "
        "models: Advancing sentiment analysis and return prediction with "
        "LLaMA 2. Pacific-Basin Finance Journal, 90, 102632. "
        "https://doi.org/10.1016/j.pacfin.2024.102632"
    ),
    "lin_1991_jsd": (
        "Lin, J. (1991). Divergence measures based on the Shannon entropy. "
        "IEEE Transactions on Information Theory, 37(1), 145–151. "
        "https://doi.org/10.1109/18.61115"
    ),
    "geng_2024_calib": (
        "Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. "
        "(2024). A survey of confidence estimation and calibration in large "
        "language models. In Proceedings of the 2024 Conference of the North "
        "American Chapter of the Association for Computational Linguistics: "
        "Human Language Technologies (Volume 1: Long Papers) (pp. 6577–6595). "
        "Association for Computational Linguistics. "
        "https://doi.org/10.18653/v1/2024.naacl-long.366"
    ),
}


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

    基于 Chiu & Hung (2025, PBFJ) Fig. 2 的 Neutral 偏好诊断思路降级适配。
    项目数据为单次打标，无法复刻原始 Dirichlet 批次更新，改为经验性类别
    比例分析 + 模型间 chi-square 独立性检验 + Jensen-Shannon 散度。

    学术依据：
      - Chiu & Hung (2025, PBFJ): 模型存在系统性 Neutral 偏好倾向
      - Carlson & Burbano (2026, SMJ §4.2): 建议报告 model certainty

    Args:
        df:          当前轨道的 DataFrame。
        llm_cols:    sentiment_cols['llm'] 的值，结构为
                     {short_name: {'sentiment': col, 'confidence': col|None}}。
                     注意：包含投票聚合列 short_name='llm'，需过滤。
        track:       轨道后缀（'_full' / '_ctx' / '_ss'）。
        output_dir:  输出目录（eval_reports/）。
        logger_inst: 日志记录器。

    Returns:
        dict: 诊断结果，包含各模型类别比例、chi-square 结果、JS 散度。
    """
    track_label = {'_full': '全文', '_ctx': '上下文片段', '_ss': '银行+金科同句'}.get(track, track)
    logger_inst.info("=" * 70)
    logger_inst.info(f"===    4.5a LLM 类别偏向诊断 [{track_label}]    ===")
    logger_inst.info("=" * 70)
    # 子步骤方法依据 (called-by 主控的诊断 helper): 类别比例 + 模型间 chi-square 同质性 +
    # Jensen-Shannon 散度。方法源 Chiu & Hung (2025, PBFJ) Fig.2 Neutral 偏好诊断思路 ——
    # 该 DOI 经 Crossref 核验注册表确认 status=match (在 pool 内), 故运行期 emit (修正旧注释
    # "不在注册表→不 emit" 的误判); Carlson & Burbano (2026, SMJ §4.2) 报告 model certainty
    # 已由主控 main() 的方法论块 emit, 此处不重复。判读: JSD>0.1=偏向差异大→多数投票有效,
    # JSD<0.01=高度同质化→投票退化风险。
    # 白话: 多个 LLM 若都偏爱"中性"且彼此判读高度雷同, 多数投票就退化成"一个模型说了算";
    # 故先量化每个模型的类别偏向与模型间分布差异, 作为多数投票有效性的前置体检。
    logger_inst.info(f"  📖 类别偏向诊断方法源: {_LLM_DIAG_REFERENCES['chiu_hung_2025']}")

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
            + ", ".join(f"{cat}={pct4(dist[cat])} ({cnt[cat]:,})" for cat in categories)
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

            # 剔除全零边际（两模型均未观测到的类别列 / 整行为空的模型）：
            # 空类别对同质性检验无信息量，且会令期望频数 E[i,j]=row*col/N 出现
            # 0 元素 → scipy.chi2_contingency 抛 ValueError（如二者负面均为 0）。
            # 剔除后 dof 随有效类别数自动收缩，统计结论不变。
            nonzero_cols = contingency.sum(axis=0) > 0
            nonzero_rows = contingency.sum(axis=1) > 0
            kept_cats = [c for c, keep in zip(categories, nonzero_cols) if keep]
            contingency = contingency[np.ix_(nonzero_rows, nonzero_cols)]
            n_dropped = len(categories) - len(kept_cats)

            # 有效边际不足 2x2 → 两模型在所有共同观测到的类别上完全一致，
            # chi-square 同质性检验无定义（dof=0），记为不显著并跳过以防崩溃。
            if contingency.shape[0] < 2 or contingency.shape[1] < 2:
                logger_inst.info(
                    f"  {m1} vs {m2}: 仅 {len(kept_cats)} 个非空类别"
                    f"（{kept_cats or '无'}），同质性检验无定义，跳过"
                )
                chi2_results.append({
                    'pair': f"{m1} vs {m2}",
                    'chi2': 0.0, 'p_value': 1.0, 'dof': 0, 'significant': False,
                })
                continue

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
            drop_note = f"（剔除 {n_dropped} 个空类别）" if n_dropped else ""
            logger_inst.info(
                f"  {m1} vs {m2}: chi2={sig4(chi2_stat)}, "
                f"p={sig4(p_val)}{sig_mark}, dof={dof:,}{drop_note}"
            )

    # ── 3. 模型间 Jensen-Shannon 散度 ──
    # JSD = 0.5·KLD(P‖M) + 0.5·KLD(Q‖M), M = 0.5·(P+Q) — 对称、有界 [0,1] (log2 底) 的
    # 分布距离, 由 _compute_jsd 直接实现; 原始出处 Lin (1991) 论证基于 Shannon 熵的散度族,
    # 是本节模型间类别分布差异度量的方法学锚点 (squarely-on-method, 非装饰性引用)。
    # 白话: 用一个对称、不会发散到无穷的"分布差异分数"量化两模型的类别判读有多不一样。
    logger_inst.info("  --- 模型间 Jensen-Shannon 散度 ---")
    logger_inst.info(f"  📖 JSD 度量出处: {_LLM_DIAG_REFERENCES['lin_1991_jsd']}")
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
            logger_inst.info(f"  {m1} vs {m2}: JSD={sig4(jsd)} — {interp}")

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

    升级版 (G-02): 实现完整的 Expected Calibration Error (ECE) 和可靠性图。

    ECE 计算策略 (fix omni-g-val-tone-03, 2026-06-11):
      - 若 33 阶段人工金标准数据存在 → 用人工标注作为 ground truth (最高优先级)
      - 否则 → 对每个被评模型用 leave-one-out 共识作伪标准: 其余独立模型的标签
        全部非空且一致时取该共识, 不一致/缺失行剔除。
        此前的 leave-one-in 伪标准 (llm_sentiment{track} 含被评模型自身票) 中
        被评模型自己是共识选票之一, 仅当其余模型一致且都反对它时才判"错" →
        per-bin accuracy 被机械抬高, ECE 对过自信模型系统性低估。

    学术依据：
      - Guo et al. (2017, ICML): ECE = Σ(|B_m|/n) × |acc(B_m) - conf(B_m)|
        其中 B_m 为第 m 个分箱, acc 为实际准确率, conf 为平均置信度
      - Niculescu-Mizil & Caruana (2005, ICML): 可靠性图 (Reliability Diagram)
      - Carlson & Burbano (2026, SMJ): LLM 标注应报告 model certainty

    Args:
        df:          当前轨道的 DataFrame。
        llm_cols:    sentiment_cols['llm'] 的值（含聚合列，需过滤）。
        track:       轨道后缀。
        output_dir:  输出目录。
        logger_inst: 日志记录器。

    Returns:
        dict: 校准诊断结果，含 ECE 值和可靠性图数据。
    """
    track_label = {'_full': '全文', '_ctx': '上下文片段', '_ss': '银行+金科同句'}.get(track, track)
    logger_inst.info("=" * 70)
    logger_inst.info(f"===    4.5b 置信度校准诊断 [{track_label}]    ===")
    logger_inst.info("=" * 70)
    # 子步骤方法依据 (called-by 主控的诊断 helper): 等宽分箱 Expected Calibration Error (ECE)。
    # ECE 公式出处 Guo et al. (2017, ICML, On calibration of modern neural networks) — 不在经核验
    # 注册表, 按铁律不 emit 其 DOI; 但 LLM 自报置信度校准的当代综述 Geng et al. (2024, NAACL)
    # 已经 Crossref 核验 (status=match, 在 pool 内), 作为本诊断的方法对标在运行期 emit。
    # 判读: ECE<0.05=校准良好 / 0.05-0.10=一般 / 0.10-0.15=偏差 / ≥0.15=校准不良。
    # 白话: 检验"模型自称有 90% 把握时, 实际是否约 90% 答对" — 自信度与真实正确率的吻合程度。
    logger_inst.info(f"  📖 LLM 置信度校准综述: {_LLM_DIAG_REFERENCES['geng_2024_calib']}")

    # ── 0. 过滤聚合列 ──
    independent_models = {
        name: info for name, info in llm_cols.items()
        if name != 'llm'
    }
    if not independent_models:
        logger_inst.warning("  无独立 LLM 模型列可用，跳过置信度校准诊断")
        return {}

    N_BINS = 10  # ECE 标准分箱数 (Guo et al. 2017)

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
            f"  [{name}] mean={sig4(stats['mean'])}, "
            f"median={sig4(stats['median'])}, std={sig4(stats['std'])}, "
            f"skew={sig4(stats['skew'])}, n={stats['n']:,}"
        )

    # ── 2. ECE 计算 (G-02 升级) ──
    logger_inst.info("  --- Expected Calibration Error (ECE) ---")
    logger_inst.info(f"  分箱数: {N_BINS} (Guo et al. 2017, ICML)")

    # 确定 ground truth 标签
    # fix(omni-g-val-tone-03, 2026-06-11): 伪标准从 leave-one-in (llm_sentiment{track}
    # = 含被评模型自身票的多数票) 改为 leave-one-out 共识 — 旧口径下被评模型自己
    # 持共识选票, 仅当其余模型一致且都反对它时才判"错", per-bin accuracy 被机械
    # 抬高, ECE 对过自信模型系统性低估。LOO 规则: 其余独立模型标签全部非空且
    # 一致 → 取共识为伪 GT; 否则该行剔除。人工金标准路径保留为最高优先级。
    human_col = f'human_sentiment{track}'
    use_human_gt = (human_col in df.columns
                    and df[human_col].notna().sum() > 100)
    if use_human_gt:
        gt_source = '人工金标准 (Stage 33)'
    else:
        gt_source = ('leave-one-out 共识 (其余独立模型一致取共识, '
                     '排除被评模型自身票; 不一致行剔除)')
    logger_inst.info(f"  Ground Truth 来源: {gt_source}")

    ece_results = {}
    reliability_data = {}

    for name, info in independent_models.items():
        conf_col = info.get('confidence')
        sent_col = info.get('score')  # 模型情感标签列
        if not conf_col or conf_col not in df.columns:
            continue

        # 获取该模型的情感预测标签
        # 查找模型的 sentiment 标签列
        model_sent_col = None
        for candidate in [f'{name}_sentiment{track}', sent_col]:
            if candidate and candidate in df.columns:
                model_sent_col = candidate
                break
        if model_sent_col is None:
            logger_inst.info(f"  [{name}] 无情感标签列，跳过 ECE")
            continue

        # 构建该模型的 ground truth 序列
        if use_human_gt:
            gt_series = df[human_col]
        else:
            # leave-one-out: 仅用其余独立模型的 sentiment 列构建共识
            other_cols = [
                info2.get('sentiment')
                for name2, info2 in independent_models.items()
                if name2 != name
                and info2.get('sentiment') in df.columns
                and info2.get('sentiment') != model_sent_col
            ]
            if not other_cols:
                logger_inst.info(
                    f"  [{name}] 无其余独立模型可构建 leave-one-out 共识，跳过 ECE"
                )
                continue
            others = df[other_cols]
            # 全部非空且唯一值数 == 1 → 一致共识; 否则该行剔除 (NaN)
            unanimous = others.notna().all(axis=1) & (others.nunique(axis=1) == 1)
            gt_series = others.iloc[:, 0].where(unanimous)

        # 构建有效数据掩码
        valid_mask = (
            df[conf_col].notna() &
            df[model_sent_col].notna() &
            gt_series.notna()
        )
        if valid_mask.sum() < 50:
            logger_inst.info(f"  [{name}] 有效观测 < 50，跳过 ECE")
            continue

        confidences = pd.to_numeric(df.loc[valid_mask, conf_col], errors='coerce').values
        predictions = df.loc[valid_mask, model_sent_col].astype(str).values
        ground_truth = gt_series.loc[valid_mask].astype(str).values

        # 计算 ECE (10-bin equal-width binning)
        bin_boundaries = np.linspace(0, 1, N_BINS + 1)
        bin_ece = 0.0
        n_total = len(confidences)
        bin_details = []

        for i in range(N_BINS):
            low, high = bin_boundaries[i], bin_boundaries[i + 1]
            if i == N_BINS - 1:
                in_bin = (confidences >= low) & (confidences <= high)
            else:
                in_bin = (confidences >= low) & (confidences < high)

            bin_size = in_bin.sum()
            if bin_size == 0:
                bin_details.append({
                    'bin': f'{low:.1f}-{high:.1f}',
                    'n': 0, 'avg_conf': 0, 'accuracy': 0, 'gap': 0
                })
                continue

            avg_conf = float(confidences[in_bin].mean())
            accuracy = float((predictions[in_bin] == ground_truth[in_bin]).mean())
            gap = abs(accuracy - avg_conf)
            bin_ece += (bin_size / n_total) * gap

            bin_details.append({
                'bin': f'{low:.1f}-{high:.1f}',
                'n': int(bin_size),
                'avg_conf': round(avg_conf, 4),
                'accuracy': round(accuracy, 4),
                'gap': round(gap, 4),
            })

        ece_value = round(float(bin_ece), 4)
        ece_results[name] = ece_value
        reliability_data[name] = bin_details

        # ECE 解读 (Guo et al. 2017)
        if ece_value < 0.05:
            quality = '✅ 校准良好 (< 0.05)'
        elif ece_value < 0.10:
            quality = '校准一般 (0.05-0.10)'
        elif ece_value < 0.15:
            quality = '校准偏差 (0.10-0.15)'
        else:
            quality = '🔴 校准不良 (≥ 0.15)'

        logger_inst.info(f"  [{name}] ECE = {sig4(ece_value)} {quality}")
        logger_inst.info(f"    Ground Truth: {gt_source}, N = {n_total:,}")

        # 输出分箱详情
        for bd in bin_details:
            if bd['n'] > 0:
                logger_inst.info(
                    f"    Bin {bd['bin']}: n={bd['n']:>5,}, "
                    f"avg_conf={sig4(bd['avg_conf'])}, "
                    f"accuracy={sig4(bd['accuracy'])}, "
                    f"gap={sig4(bd['gap'])}"
                )

    # ── 3. 输出 CSV ──
    csv_rows = []
    for name, s in stats_results.items():
        row = {'模型': name}
        row.update(s)
        if name in ece_results:
            row['ECE'] = ece_results[name]
        csv_rows.append(row)

    csv_path = os.path.join(output_dir, f'llm_calibration{track}.csv')
    if csv_rows:
        pd.DataFrame(csv_rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger_inst.info(f"  置信度校准 CSV: {csv_path}")

    # ── 4. 可靠性图 + 置信度直方图 (升级版) ──
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei',
                                            'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False

        n_models = len(stats_results)
        if n_models > 0:
            # 每个模型: 上方可靠性图 + 下方直方图
            has_ece = len(ece_results) > 0
            n_rows = 2 if has_ece else 1
            fig, axes = plt.subplots(n_rows, n_models,
                                     figsize=(5 * n_models, 4 * n_rows),
                                     squeeze=False)
            plot_idx = 0
            for name, info in independent_models.items():
                conf_col = info.get('confidence')
                if not conf_col or conf_col not in df.columns:
                    continue
                if name not in stats_results:
                    continue
                if plot_idx >= n_models:
                    break

                conf = pd.to_numeric(df[conf_col], errors='coerce').dropna()

                # ── 可靠性图 (Reliability Diagram) ──
                if has_ece and name in reliability_data:
                    ax_rel = axes[0, plot_idx]
                    bins = reliability_data[name]
                    bin_mids = [(i + 0.5) / N_BINS for i in range(N_BINS)]
                    accs = [b['accuracy'] for b in bins]
                    confs_avg = [b['avg_conf'] for b in bins]
                    sizes = [b['n'] for b in bins]

                    # 只画有样本的 bin
                    valid = [i for i, s in enumerate(sizes) if s > 0]
                    if valid:
                        ax_rel.bar([bin_mids[i] for i in valid],
                                   [accs[i] for i in valid],
                                   width=1/N_BINS, alpha=0.6,
                                   color='steelblue', edgecolor='white',
                                   label='Accuracy')
                        ax_rel.plot([0, 1], [0, 1], '--', color='gray',
                                    linewidth=1, label='Perfect calibration')
                    ax_rel.set_xlim(0, 1)
                    ax_rel.set_ylim(0, 1)
                    ax_rel.set_xlabel('Mean Predicted Confidence', fontsize=9)
                    ax_rel.set_ylabel('Fraction of Correct', fontsize=9)
                    ece_val = ece_results.get(name, 0)
                    ax_rel.set_title(f'{name}\nECE = {ece_val:.4f}',
                                     fontsize=10, fontweight='bold')
                    ax_rel.legend(fontsize=7, loc='upper left')

                # ── 置信度直方图 ──
                hist_row = 1 if has_ece else 0
                ax_hist = axes[hist_row, plot_idx]
                ax_hist.hist(conf, bins=20, range=(0, 1), alpha=0.7,
                            color='steelblue', edgecolor='white')
                ax_hist.set_xlabel('置信度', fontsize=10)
                ax_hist.set_ylabel('频次', fontsize=10)
                s = stats_results[name]
                ax_hist.axvline(s['mean'], color='red', linestyle='--',
                               linewidth=1, label=f"mean={s['mean']:.2f}")
                ax_hist.legend(fontsize=8)
                if not has_ece:
                    ax_hist.set_title(f'{name}', fontsize=11, fontweight='bold')

                plot_idx += 1

            title_suffix = ' (with ECE)' if has_ece else ''
            fig.suptitle(f'LLM 置信度校准诊断 [{track_label}]{title_suffix}',
                         fontsize=13, fontweight='bold')
            fig.tight_layout(rect=[0, 0, 1, 0.93])
            png_path = os.path.join(output_dir, f'llm_calibration{track}.png')
            fig.savefig(png_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            logger_inst.info(f"  置信度校准图: {png_path}")
    except ImportError:
        logger_inst.warning("  matplotlib 不可用，跳过校准图绘制")
    except Exception as e:
        logger_inst.warning(f"  绘制校准图失败: {e}")

    # ── 5. 汇总 ──
    mode = 'full_ece' if ece_results else 'descriptive_only'
    result = {
        'stats': stats_results,
        'mode': mode,
    }
    if ece_results:
        result['ece'] = ece_results
        result['ece_bins'] = N_BINS
        result['ground_truth_source'] = gt_source
        result['reliability_data'] = reliability_data
    return result


# ============================================================================
# 10. 主函数
# ============================================================================

def main():
    """情感三角验证主入口（三轨模式 full/ctx/ss）。"""
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} (三轨模式) ---")
    # ── 黄金范式【功能】banner (canonical markers; 详细方法论见下方 📌 段) ──
    logger.info("=" * 72)
    logger.info("阶段 64: 情感验证 (三轨主控) — 词典法/BERT/LLM 三角交叉验证 (Loughran-McDonald 2016 收敛效度)")
    logger.info("=" * 72)
    logger.info(
        "【功能】对三种独立机理的情感测量(查情感词典/BERT 神经网络/LLM 大模型)做系统交叉验证, "
        "为情感度量提供方法间趋同的【收敛效度】证据; 对 _full/_ctx/_ss 三轨各跑一遍完整 6 步并出报告。"
    )
    logger.info(
        "【方法】内部一致性 Cronbach α=(k/(k-1))(1-Σσ²ᵢ/σ²ₜ) + 方法间 Spearman ρ + 标签完全/多数一致率; "
        "LLM 类别偏向(chi-square+JS 散度)与置信度校准(ECE); 并抽样产人工验证工作台(分歧篇 2:1 过采样)。"
    )
    logger.info(
        "【判读】Cronbach α ≥0.70 可接受/≥0.80 良好; Spearman |ρ|≥0.7 强一致; 标签多数一致率 ≥85% 良好。"
        " 三机器方法趋同=收敛效度, 不等于效标效度(vs 人工金标准, 须人工回读/stage 33), 勿夸大。"
    )
    logger.info("【确定性】纯 pandas/numpy/scipy/matplotlib, 无 LLM/Embedding API 调用, $0, 逐位可复现 (抽样 seed=42)。")
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     对三种情感分析方法(词典法/BERT/LLM)进行系统性交叉验证。")
    # fix(measurement-validation-audit 2026-06-13, P1-convergent-vs-criterion): 本阶段
    # 产出的是【收敛效度/convergent validity】证据 (跨方法 Cronbach α / Spearman ρ /
    # 标签一致率 = 方法间趋同), 不等于【效标效度/criterion validity】(vs 人工金标准)。
    # 后者由 evaluate_human_verification (回读 09_sentiment_verify) 与 stage 33 提供,
    # 人工标注未填时恒为 pending。故此处不得单凭方法间一致性宣称"构念效度达顶刊标准"。
    logger.info("     注: 本阶段 = 收敛效度(方法间趋同); 效标效度(vs 人工金标准)由人工")
    logger.info("     回读 (evaluate_human_verification) / stage 33 提供, 未填表时 pending。")
    logger.info("     三轨模式: 全文(_full)、上下文片段(_ctx)和银行+金科同句(_ss)分别执行完整验证。")
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

    # ── 黄金范式【① 项目/环境信息】指纹 (golden-safe; 仅日志, 不入任何产物) ──
    try:
        import platform
        logger.info("=" * 72)
        logger.info("🧭 项目 / 环境信息")
        logger.info("  · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板); 版本 v3.11.1")
        logger.info("  · 阶段: 64 tone_validation (验证支线; thin shim 64_tone_validation.py) — 词典/BERT/LLM 三角交叉验证")
        logger.info(f"  · Python {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"  · 平台: {platform.platform()}; CPU 逻辑核心={os.cpu_count()}; PID={os.getpid()}")
        logger.info(f"  · NEWS_PROCESS_RUN_ID={os.environ.get('NEWS_PROCESS_RUN_ID', '(未设)')}")
        logger.info("  · 确定性/成本: 纯 pandas/numpy/scipy/matplotlib, 无 LLM/Embedding API 调用, $0; 抽样 seed=42 逐位可复现。")
        logger.info(f"  · 模块: {os.path.abspath(__file__)}")
        logger.info(f"  · 工作目录: {os.getcwd()}")
    except Exception as _e_env:
        logger.warning(f"环境信息块打印失败 (不影响阶段): {_e_env}")

    # ── 黄金范式【③ 运行配置】可调参数 + 输入输出路径集中打印 ──
    try:
        _out_dir = CONFIG['paths']['output_dir']
        _log_dir = CONFIG['paths']['log_dir']
        logger.info("=" * 72)
        logger.info("⚙ 运行配置")
        logger.info("  · 验证轨道集: _full(全文) / _ctx(上下文窗口) / _ss(银行+金科同句) — 三轨各跑完整 6 步")
        logger.info(
            f"  · 人工验证抽样: n_agree=100 + n_disagree=200 (分歧案例 2:1 过采样), "
            f"seed=42; 样本量下限 HUMAN_VERIFY_MIN_N={HUMAN_VERIFY_MIN_N:,} (CLT 经验下限)"
        )
        logger.info(f"  · ECE 分箱数 N_BINS=10 (等宽分箱, 见 diagnose_confidence_calibration); 合法人工标签词表={'/'.join(HUMAN_VERIFY_LABELS)}")
        logger.info(
            f"  · 判读阈值: Cronbach α 可接受≥{sig4(0.70)} / 良好≥{sig4(0.80)} / 优秀≥{sig4(0.90)}; "
            f"Spearman 强一致|ρ|≥{sig4(0.70)} / 中等≥{sig4(0.40)}; 标签多数一致率良好≥{pct4(0.85)}"
        )
        logger.info(f"  · 输入键: output_23_bert_tone (回退 output_22_words_tone); 输出目录: {os.path.join(_out_dir, 'eval_reports')}")
        logger.info(f"  · 数据根目录: {_out_dir}; 日志目录: {_log_dir}")
        logger.info("  · 配置来源: config/paths.yaml (路径) + config/sentiment.yaml (上游方法产物); 本阶段无独立 tunable YAML 块")
    except Exception as _e_cfg:
        logger.warning(f"配置块打印失败 (不影响阶段): {_e_cfg}")

    # ── 黄金范式【④ 方法论依据】学术出处 emit 进日志 (含期刊卷(期):页 + DOI 可访问链接) ──
    # 仅引用"经核验参考文献注册表" (VERIFIED_REFERENCES.md, status=match) 中本模块实现的核心构念出处。
    try:
        logger.info("=" * 72)
        logger.info("📖 方法论依据 (核心构念学术出处; 逐字取自经核验参考文献注册表)")
        logger.info(
            "  · 收敛效度(方法间相关性为构建效度核心证据): "
            "Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. "
            "Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123"
        )
        logger.info(
            "  · 词典法(中文银行情感词典构念基础): "
            "胡俊, 李强, 戴嘉诚, & 曾勇. (2024). 基于文本分析的商业银行金融科技测度及赋能效果检验. "
            "中国管理科学, 32(1), 31–41. https://doi.org/10.16381/j.cnki.issn1003-207x.2021.1714"
        )
        logger.info(
            "  · 媒体情感离散度量化(三分类标签数值化 +1/0/-1 的方法学先例): "
            "Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More than words: "
            "Quantifying language to measure firms' fundamentals. The Journal of Finance, 63(3), 1437-1467. "
            "https://doi.org/10.1111/j.1540-6261.2008.01362.x"
        )
        logger.info(
            "  · LLM 作为文本标注器的效度先例(本阶段把 LLM 投票作为与词典/BERT 并列的独立测量轨参与三角验证): "
            "Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for "
            "text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. "
            "https://doi.org/10.1073/pnas.2305016120"
        )
        logger.info(
            "  · LLM 标注的方法学纪律先例(误分类偏置/prompt 敏感性/可复现性, 本阶段对 LLM 轨做偏向+校准诊断的依据): "
            "Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: "
            "Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. "
            "https://doi.org/10.1002/smj.70023"
        )
        logger.info(
            "    (白话: 管理学顶刊给出的 LLM 标注操作指南 — 要警惕系统性误分类与 prompt 敏感性, 故本阶段额外做类别偏向/置信度校准诊断。)"
        )
        logger.info(
            "  · 多评分者一致性(Fleiss κ 的多标签/层级推广, 锚定本阶段跨 N 方法的标签一致率与 Cohen κ 口径): "
            "Moons, F., & Vandervieren, E. (2025). Measuring agreement among several raters classifying subjects "
            "into one or more (hierarchical) categories: A generalization of Fleiss' kappa. Behavior Research Methods, "
            "57(10), Article 287. https://doi.org/10.3758/s13428-025-02746-8"
        )
        logger.info(
            "    (白话: 把经典 Fleiss κ 推广到多评分者/多标签, 为本阶段「全/多数一致率」这类多方法一致性度量提供现代统计依据。)"
        )
        logger.info(
            "  · 收敛/区分效度的奠基范式(多特质-多方法矩阵 MTMM, 本阶段「方法间趋同=收敛效度」的原始构念来源): "
            "Campbell, D. T., & Fiske, D. W. (1959). Convergent and discriminant validation by the "
            "multitrait-multimethod matrix. Psychological Bulletin, 56(2), 81-105. "
            "https://doi.org/10.1037/h0046016"
        )
        logger.info(
            "    (白话: 同一构念用多种独立方法测量、彼此相关即收敛效度——本阶段反复强调的 convergent-vs-criterion 区分正本于此。)"
        )
        logger.info(
            "  · 经济文本词典法情感分析的现代基底(锚定被验证的三轨之一·词典法): "
            "Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). "
            "Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), "
            "125-143. https://doi.org/10.1111/ecin.13264"
        )
        logger.info(
            "  · 多标签分类的 micro/macro/weighted F1 度量学(锚定人工回读端 evaluate_human_verification 的 macro-P/R/F1 口径): "
            "Hinojosa Lee, M. C., Braet, J., & Springael, J. (2024). Performance metrics for multilabel "
            "emotion classification: Comparing micro, macro, and weighted F1-scores. Applied Sciences, "
            "14(21), Article 9863. https://doi.org/10.3390/app14219863"
        )
        logger.info(
            "  · 白话: 用三种机理完全不同的方法(查词典/BERT 神经网络/LLM 大模型)给同一篇新闻判情感, "
            "若彼此趋同则收敛效度强 (但仍≠效标效度=对人工金标准, 须人工回读/stage 33)。"
        )
        # 注: Cronbach (1951, Psychometrika) / Chiu & Hung (2025, PBFJ) / Guo et al. (2017, ICML, ECE)
        # 不在经核验注册表内, 按铁律不 emit DOI, 仅保留代码注释/docstring。
        # (Carlson & Burbano 2026 SMJ 自 2026-06-26 起经 Crossref 三道核验注册表确认 status=match, 已上移至 emit 区。)
    except Exception as _e_ref:
        logger.warning(f"方法论引用块打印失败 (不影响阶段): {_e_ref}")

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
    # Step 2: 三轨三角验证循环
    # ======================================================================
    # 对 _full / _ctx / _ss 三条轨道分别执行完整的三角验证流水线
    _TRACK_LABELS = {
        '_full': '全文',
        '_ctx': '上下文片段',
        '_ss': '银行+金科同句',  # ss 轨人类可读标签 (镜像 ctx 标签 + 同句共现口径)
    }
    _track_elapsed = {}  # 仅服务于日志的 per-轨墙钟计时
    for track in ['_full', '_ctx', '_ss']:
        track_label = _TRACK_LABELS.get(track, track)
        logger.info("\n" + "#" * 70)
        logger.info(f"#####  三角验证轨道: [{track_label}] ({track})  #####")
        logger.info("#" * 70)
        _t_track = time.time()
        _run_validation_for_track(df, track, output_dir, logger, CONFIG)
        _track_elapsed[track] = time.time() - _t_track

    # ── 黄金范式【⑥ 阶段计时】per-轨墙钟 + 总耗时汇总 (仅日志, golden-safe) ──
    try:
        logger.info("=" * 72)
        logger.info("⏱ 阶段计时 (per-轨墙钟)")
        for _tk, _el in _track_elapsed.items():
            logger.info(f"  · 轨道 {_TRACK_LABELS.get(_tk, _tk)} ({_tk}): {sig4(_el)} 秒")
        _total_track = sum(_track_elapsed.values())
        logger.info(f"  · 三轨验证合计: {sig4(_total_track)} 秒; 阶段总墙钟: {sig4(time.time() - stage_start)} 秒")
    except Exception as _e_timing:
        logger.warning(f"计时汇总块打印失败 (不影响阶段): {_e_timing}")

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=len(df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} (三轨模式) ---")


_KAPPA_LABEL_CODE = {'负面': 0, '中性': 1, '正面': 2}  # 非负码 (避 Krippendorff -1 缺标哨兵与负面=-1 冲突)


def compute_cross_model_kappa(df: pd.DataFrame, sentiment_cols: dict, track: str,
                              output_dir: str, logger_inst) -> None:
    """跨模型 chance-corrected 一致性 (2026-07-02, 互为稳健性 Phase 3)。

    LLM 三家 (独立模型, 剔除 'llm' 投票聚合) 一组 + BERT 三模型一组, 各算 Krippendorff α
    (名义尺度, 缺标感知 → 天然容 finbert2 2-vs-3 分类失配, 无需二值化/丢中性) + pairwise
    Cohen κ。复用 llms_evaluation 既有 canonical 函数; 对齐 manuscript.tex (Cohen κ + Krippendorff α)。

    ⚠ 标签重映射**非负码** (负面=0/中性=1/正面=2): compute_krippendorffs_alpha 以 -1 为缺标哨兵,
      与 encode.SENTIMENT_MAP 负面=-1 冲突, 直接传原码会静默把所有负面当缺失丢弃 → α 虚高。
    ⚠ ratings_matrix 形状 = (n_coders, n_items) (raters × items, 非 items × raters)。
    golden-safe (仅产 eval_reports/sentiment_model_kappa{track}.csv, 不改 panel)。
    """
    from news_process.validation.llms_evaluation import (
        compute_cohens_kappa,
        compute_krippendorffs_alpha,
    )

    groups = {
        'LLM': [(n, info['sentiment']) for n, info in sentiment_cols.get('llm', {}).items()
                if n != 'llm'],  # 剔除投票聚合 'llm' — 它是三家的确定性合成, 非独立评分员
        'BERT': [(n, info['label']) for n, info in sentiment_cols.get('bert', {}).items()],
    }
    trk = track.lstrip('_') or 'full'
    rows = []
    for gname, members in groups.items():
        members = [(n, c) for n, c in members if c in df.columns]
        if len(members) < 2:
            logger_inst.info(f"  跨模型 κ [{gname}]: 有效成员 <2, 跳过")
            continue
        # (n_coders, n_items) 非负码矩阵; -1 = 该模型对该文章缺标 (finbert2 无中性=类别子集,
        # 由 Krippendorff 名义尺度天然处理, 非缺标)。
        mat = np.full((len(members), len(df)), -1, dtype=int)
        for j, (_, col) in enumerate(members):
            codes = df[col].map(_KAPPA_LABEL_CODE)
            mat[j, :] = codes.fillna(-1).astype(int).to_numpy()
        n_units = int(((mat >= 0).sum(axis=0) >= 2).sum())
        try:
            alpha = compute_krippendorffs_alpha(mat)
        except Exception as _e:  # noqa: BLE001 — 诊断性
            logger_inst.warning(f"  跨模型 κ [{gname}] Krippendorff 失败: {_e}")
            alpha = float('nan')
        rows.append({'track': trk, 'group': gname, 'metric': 'krippendorff_alpha',
                     'pair': f'{gname} (all {len(members)} models)', 'value': alpha,
                     'n_units': n_units})
        for a in range(len(members)):
            for b in range(a + 1, len(members)):
                m = (mat[a] >= 0) & (mat[b] >= 0)
                if int(m.sum()) < 2:
                    continue
                try:
                    ck = compute_cohens_kappa(mat[a][m], mat[b][m])
                    kv = ck.get('kappa') if isinstance(ck, dict) else ck
                except Exception:  # noqa: BLE001
                    kv = float('nan')
                rows.append({'track': trk, 'group': gname, 'metric': 'cohen_kappa',
                             'pair': f'{members[a][0]} vs {members[b][0]}', 'value': kv,
                             'n_units': int(m.sum())})
    if not rows:
        logger_inst.info("  跨模型 κ: 无可算组 (每组需 ≥2 有效模型), 跳过")
        return
    out_path = os.path.join(output_dir, f'sentiment_model_kappa{track}.csv')
    pd.DataFrame(rows).to_csv(out_path, index=False, encoding='utf-8-sig')
    logger_inst.info(f"  跨模型 κ (Krippendorff α + Cohen κ) 写入 {out_path} ({len(rows)} 行)")


def _run_validation_for_track(df, track, output_dir, logger, CONFIG):
    """对指定轨道执行完整的三角验证流水线 (Plan-r3 P3-16 docstring 扩充)。

    Stage 34 三轨 (full/ctx/ss) 执行的内部主入口. 接到 ``main()`` 的 dispatch,
    对单一 track 跑完 6 步:

        1. discover_sentiment_columns -- 自动发现 LLM/dict/BERT 情感列
        2. 相关/一致性矩阵            -- Spearman/Pearson 相关 + Cronbach α +
           观测一致率 (audit-fixes 2026-05-29: 此前误标 compute_pairwise_kappa /
           Cohen kappa, 实际全模块无 κ 实现)
        3. stratified_analysis        -- 按 length/time/dict-coverage 分层
        4. diagnose_llm_category_bias -- LLM 偏向"中性"等分类偏倚检测
        5. diagnose_confidence_calibration -- 置信度校准 ECE
        6. 输出报告 — ``sentiment_validation_results<track>.json`` /
           ``sentiment_validation_table<track>.tex`` /
           ``sentiment_cross_method<track>.csv`` /
           ``cronbachs_alpha_summary<track>.csv`` +
           人工验证样本 ``09_sentiment_verify<track>.xlsx``

    Args:
        df:         track 已过滤的三轨 panel
        track:      '_full' / '_ctx' / '_ss' (匹配三轨命名约定)
        output_dir: 报告输出目录 (一般 ``data/processed/eval_reports/``)
        logger:     注入 logger
        CONFIG:     已加载的项目 cfg

    Returns:
        None — 副作用是写出上述 ``*<track>.*`` 报告文件 (json/tex/csv/xlsx,
        另含热力图 PNG; 文件名无 ``34_`` 前缀, 见第 6 步清单).
    """
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

    # fix(omni-g-val-tone-02, 2026-06-11): 聚合投票列 short_name=='llm'
    # (llm_sentiment{track} = 3 模型多数票) 不是独立测量 — 计入 Cronbach α /
    # 标签一致率 / 方法级均值 / majority_vote 合成会把成员模型的合成结果当作
    # 第 4 个独立模型, 经典测量理论下机械抬高一致性 (盘上实测 LLM α 0.7677
    # 含投票列 vs 纯 3 模型 0.6933, 0.70 阈值结论翻转)。与
    # diagnose_llm_category_bias / diagnose_confidence_calibration 的过滤
    # 先例对齐, 此处从源头剔除; 聚合列仅作对比基准单独记录于
    # results['llm_aggregate_benchmark']。
    llm_independent = {name: info for name, info in sentiment_cols['llm'].items()
                       if name != 'llm'}
    llm_aggregate_info = sentiment_cols['llm'].get('llm')

    # 跨模型 chance-corrected 一致性 (2026-07-02, 互为稳健性 Phase 3): Krippendorff α + Cohen κ
    # (LLM 三家独立 / BERT 三模型各一组), 对齐 manuscript.tex。golden-safe; 诊断性, 不阻断主验证。
    try:
        compute_cross_model_kappa(df, sentiment_cols, track, output_dir, logger)
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"跨模型 κ 计算跳过 (非致命): {_e}")

    n_words = len(sentiment_cols['words'])
    n_bert = len(sentiment_cols['bert'])
    n_llm = len(llm_independent)
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

    # fix(omni-g-val-tone-02, 2026-06-11): 仅独立模型进入 all_scores/all_labels,
    # 聚合投票列 'llm' 不参与任何跨方法统计
    for short_name, cols_info in llm_independent.items():
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
            # fix(omni-g-val-tone-02): 'llm' 仅列独立模型; 聚合投票列单独披露
            'llm': list(llm_independent.keys()),
            'llm_aggregate_excluded': (['llm'] if llm_aggregate_info else []),
        },
        'within_method': {},
        'cross_method': {},
    }

    # 聚合投票列仅作对比基准单独报告 (不进入 α / 一致率 / 方法均值)
    if llm_aggregate_info is not None:
        agg_col = llm_aggregate_info['sentiment']
        results['llm_aggregate_benchmark'] = {
            'column': agg_col,
            'distribution': {str(k): int(v)
                             for k, v in df[agg_col].value_counts().items()},
            'note': ('聚合投票列 (成员模型多数票), 非独立测量; '
                     '已从 Cronbach α / 一致率 / 方法级均值剔除, 仅作对比基准'),
        }
        logger.info(f"聚合投票列 '{agg_col}' 已从跨方法统计剔除 (仅作对比基准)")

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
        logger.info(f"  Cronbach's Alpha: {sig4(alpha)}")

        spearman = compute_spearman_matrix(words_scores)
        logger.info("  Spearman 相关矩阵:")
        logger.info(f"\n{spearman.to_string()}")
        results['within_method']['words_spearman'] = spearman.to_dict()

        save_correlation_heatmap(
            spearman, 'Spearman 相关矩阵 — 词典法 (内部)',
            os.path.join(output_dir, f'heatmap_within_words{track}.png'), logger
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
            logger.info(f"  IDF Cronbach's Alpha: {sig4(idf_alpha)}")

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
        logger.info(f"  Cronbach's Alpha: {sig4(alpha)}")

        spearman = compute_spearman_matrix(bert_scores)
        logger.info("  Spearman 相关矩阵:")
        logger.info(f"\n{spearman.to_string()}")
        results['within_method']['bert_spearman'] = spearman.to_dict()

        save_correlation_heatmap(
            spearman, 'Spearman 相关矩阵 — BERT (内部)',
            os.path.join(output_dir, f'heatmap_within_bert{track}.png'), logger
        )

    # 3.3 LLM 模型间一致性（如有多个模型）
    if n_llm >= 2:
        logger.info(f"--- LLM: {n_llm} 个模型 ---")
        llm_score_cols = [c for c in all_scores_df.columns if c.startswith('LLM_')]
        llm_scores = all_scores_df[llm_score_cols]

        alpha = compute_cronbachs_alpha(llm_scores)
        within_results['cronbach_alpha']['LLM'] = alpha
        within_results['n_models']['LLM'] = n_llm
        logger.info(f"  Cronbach's Alpha: {sig4(alpha)}")

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
        os.path.join(output_dir, f'heatmap_cross_all{track}.png'), logger
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
            os.path.join(output_dir, f'heatmap_cross_method{track}.png'), logger
        )

    # 4.3 标签一致性
    logger.info("--- 标签一致性分析 ---")
    agreement = compute_label_agreement_rate(all_labels_df)
    cross_results['label_agreement'] = agreement
    results['cross_method']['label_agreement'] = agreement

    logger.info(f"  完全一致率: {sig4(agreement['full_agreement_rate'])} ({pct4(agreement['full_agreement_rate'])})")
    logger.info(f"  多数一致率: {sig4(agreement['majority_agreement_rate'])} ({pct4(agreement['majority_agreement_rate'])})")
    logger.info(f"  参与方法/模型数: {agreement['n_methods']:,}")

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
        pct = count / len(vote_labels)
        logger.info(f"  {label}: {count:,} ({pct4(pct)})")

    # 5.2 加权平均（等权）
    weighted_score = weighted_average_score(all_scores_df)
    logger.info(f"加权平均得分: mean={sig4(weighted_score.mean())}, "
                f"std={sig4(weighted_score.std())}")

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
    # Step 6.5: LLM 概率诊断 (Chiu & Hung 2025 M3 降级适配)
    # ======================================================================
    # fix(omni-g-val-tone-02): n_llm 已剔除聚合列 = 独立模型数; 仍传入完整
    # sentiment_cols['llm'], 函数内部自行过滤聚合列 (defense in depth)
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

    # fix(omni-g-val-tone-04, 2026-06-11): 文件名加 track 后缀 — 此前各轨共写
    # 同一 09_sentiment_verify.xlsx, 后写轨道覆盖前者, 文件内 词典_/BERT_/LLM_
    # 标签列实为后写轨道值但无轨道标识, 人工标注的归属轨道不可追溯
    # (三轨化后 full/ctx/ss 各写独立 09_sentiment_verify{_full,_ctx,_ss}.xlsx)
    verify_path = os.path.join(output_dir, f'09_sentiment_verify{track}.xlsx')
    # 防覆盖守卫 (human-annot-readback, 2026-06-13; final-audit 收紧为
    # fail-closed): 工作台只要有人工痕迹 (含非法词汇/只填理由) 或读取失败
    # (-1, 可能藏有标注), 一律不重生 — 人工填写不可再生, 重抽样即销毁;
    # 仅"确认空白" (=0) 允许刷新
    n_existing = count_human_annotations(verify_path)
    if n_existing < 0:
        logger.error(
            f"工作台存在但读取失败/结构异常 — fail-closed 跳过重生, 以防销毁"
            f"潜在人工标注 (请人工检查 sheet/表头; 确认无人工标注后手动删除"
            f"该文件即可恢复重生): {verify_path}")
    elif n_existing > 0:
        logger.warning(
            f"检测到人工填写痕迹 ({n_existing} 个单元格), 跳过工作台重生以"
            f"保护标注: {verify_path}")
    else:
        # final-audit F1 (2026-06-13): LLM 聚合投票列回灌工作台 — 主 spec
        # llm_vote_tone{track} 的直接源必须可被人工验证; 仅作标注对象列,
        # 不进 all_labels_df (不违反 omni-02 的互比剔除)
        extra_labels = {}
        if llm_aggregate_info and llm_aggregate_info.get('sentiment') in df.columns:
            extra_labels['LLM_投票'] = df[llm_aggregate_info['sentiment']]
        generate_validation_sample(
            df, all_labels_df, vote_labels, verify_path, logger,
            n_agree=100, n_disagree=200, seed=42, track=track,
            extra_labels=extra_labels
        )

    # 回读比对 (human-annot-readback, 2026-06-13): 全项目唯一的
    # 词典/BERT 族人工验证指标产出路径; 空表优雅 pending, 不合成数据
    results['human_verification'] = evaluate_human_verification(
        verify_path, track, output_dir, logger)

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
    # fix(omni-g-val-tone-02): 汇总口径与 LaTeX 'Number of Models' 一致 = 独立模型数
    n_llm = len(llm_independent)
    total_methods = n_words + n_bert + n_llm
    logger.info(f"[{track}] 三角验证完毕: 词典={n_words}, BERT={n_bert}, LLM={n_llm}")

    # ── 黄金范式【结果分析】: 取本轨真实算出的产出指标 + 对照阈值/预期方向给判读 ──
    # 注: 下述变量均为仅服务于日志的局部读取/计算, 绝不回写 df / 不改任何产物 (json/tex/csv/xlsx)。
    _track_label = {'_full': '全文', '_ctx': '上下文片段', '_ss': '银行+金科同句'}.get(track, track)
    _alpha_map = within_results.get('cronbach_alpha', {})
    _agree_full = agreement.get('full_agreement_rate', 0.0)
    _agree_maj = agreement.get('majority_agreement_rate', 0.0)
    _agree_nm = agreement.get('n_methods', 0)
    _spearman_pairs = cross_results.get('spearman_pairs', {})
    _hv = results.get('human_verification', {})
    _hv_status = _hv.get('status', 'pending')
    _hv_n = _hv.get('n_annotated', 0)

    def _alpha_verdict(a):
        # Cronbach (1951): ≥0.90 优秀 / ≥0.80 良好 / ≥0.70 可接受 / <0.70 需改进
        if a >= 0.90:
            return "优秀(≥0.90)"
        if a >= 0.80:
            return "良好(≥0.80)"
        if a >= 0.70:
            return "可接受(≥0.70)"
        return "需改进(<0.70, 内部一致性偏弱)"

    def _rho_verdict(r):
        # Spearman ρ: ≥0.7 强 / 0.4-0.7 中 / <0.4 弱 (按 main() 关键指标解读口径)
        ar = abs(r)
        if ar >= 0.70:
            return "强一致(|ρ|≥0.7)"
        if ar >= 0.40:
            return "中等一致(0.4≤|ρ|<0.7)"
        return "弱一致(|ρ|<0.4, 方法间排序分歧明显)"

    logger.info("-" * 72)
    logger.info(
        f"【结果分析】[{track}={_track_label}] 三角验证(收敛效度)关键产出指标逐项解读 "
        f"(对照阈值/预期方向; 收敛效度≠效标效度):"
    )
    logger.info(
        f"  · 参与三角验证的独立测量数: 词典={n_words} + BERT={n_bert} + LLM(独立模型, "
        f"已剔除聚合投票列)={n_llm} = 合计 {total_methods} (样本 n={len(df):,} 篇)。"
        f"判读: 三族测量来自完全不同机理(查词典/神经网络/大模型), 越多独立测量趋同, 收敛效度越强。"
    )
    # 内部一致性 Cronbach α 逐方法判读
    if _alpha_map:
        for _m, _a in _alpha_map.items():
            try:
                _af = float(_a)
            except (TypeError, ValueError):
                continue
            logger.info(f"  · 内部一致性 Cronbach α [{_m}]: {sig4(_af)} → {_alpha_verdict(_af)}")
    else:
        logger.info(
            "  · 内部一致性 Cronbach α: 本轨无任一方法满足 ≥2 个模型, 未计算 α "
            "(单模型方法无内部一致性可言, 属预期)。"
        )
    # 跨方法 Spearman ρ 逐对判读
    if _spearman_pairs:
        for _pair, _r in _spearman_pairs.items():
            try:
                _rf = float(_r)
            except (TypeError, ValueError):
                continue
            logger.info(f"  · 跨方法 Spearman ρ [{_pair}]: {sig4(_rf)} → {_rho_verdict(_rf)}")
    else:
        logger.info(
            "  · 跨方法 Spearman ρ: 可比较的方法不足 2 族, 未产出成对相关 "
            "(需词典/BERT/LLM 中至少 2 族同时在轨)。"
        )
    # 标签一致率判读 (经验参考 ≥85% 良好)
    logger.info(
        f"  · 标签完全一致率: {sig4(_agree_full)} ({pct4(_agree_full)}) — "
        f"{_agree_nm:,} 个方法/模型对同一篇判出完全相同标签的占比。"
        f"判读: 越高=测量越稳; 完全一致较多数一致更严苛, 中文情感三分类下偏低属正常。"
    )
    _maj_verdict = "良好(≥85%)" if _agree_maj >= 0.85 else (
        "中等(70%-85%)" if _agree_maj >= 0.70 else "偏弱(<70%, 方法间分歧较多)")
    logger.info(
        f"  · 标签多数一致率: {sig4(_agree_maj)} ({pct4(_agree_maj)}) → {_maj_verdict} "
        f"(严格多数 > 方法数/2)。判读: ≥85% 视为方法间一致性良好(经验参考值)。"
    )
    # 合成产物的描述性判读 (仅供解读, 不入产物列以外用途)
    _vote_total = int(vote_dist.sum()) if len(vote_dist) else 0
    _vote_brief = ", ".join(
        f"{_lab}={int(_cnt):,}({pct4(_cnt / _vote_total)})"
        for _lab, _cnt in vote_dist.items()
    ) if _vote_total > 0 else "无"
    _dom_lab = str(vote_dist.idxmax()) if _vote_total > 0 else "无"
    _dom_frac = (vote_dist.max() / _vote_total) if _vote_total > 0 else 0.0
    logger.info(
        f"  · 多数投票情感分布: {_vote_brief}。加权平均(等权)得分: "
        f"mean={sig4(weighted_score.mean())}, std={sig4(weighted_score.std())}。"
        f"判读: 分布若严重偏向单一类别(本轨众数 {_dom_lab} 占 {pct4(_dom_frac)})"
        f"提示测量保守或题材集中, 需结合 LLM 类别偏向诊断(本轨 Step 6.5)一并解读。"
    )
    # 人工验证(效标效度)状态判读
    if _hv_status == 'ok':
        logger.info(
            f"  · 人工验证(效标效度): status=ok, 已回读 {_hv_n} 条人工标注 (≥{HUMAN_VERIFY_MIN_N} "
            f"达标)。判读: 已为词典/BERT/LLM 各方法产出 accuracy/macro-F1/Cohen κ vs 人工金标准, "
            f"是真正的效标效度证据(优于本阶段方法间趋同)。"
        )
    elif _hv_status == 'insufficient':
        logger.info(
            f"  · 人工验证(效标效度): status=insufficient, 仅 {_hv_n} 条标注 (<{HUMAN_VERIFY_MIN_N}); "
            f"指标已算但置信区间过宽, 仅供参考。判读: 需补足人工标注方可作正式效标效度。"
        )
    else:  # pending / error
        logger.info(
            f"  · 人工验证(效标效度): status={_hv_status} (n_annotated={_hv_n})。"
            f"判读: 人工工作台尚未填写(pending)或读取异常(error) → 本轨当前仅有【收敛效度】"
            f"(方法间趋同)证据, 不得据此宣称构念效度达顶刊标准 (披露铁律)。"
        )
    # 优雅降级警告: 某情感方法整族缺列 → 该族未进三角验证
    if n_words == 0:
        logger.warning(
            f"  ⚠ [{track}] 未发现词典法情感列 → 阶段 22 可能未运行或列名后缀不匹配; "
            f"词典族缺席会削弱三角验证的'独立机理'多样性 (优雅降级, 不中断)。"
        )
    if n_bert == 0:
        logger.warning(
            f"  ⚠ [{track}] 未发现 BERT 情感列 → 阶段 23 可能未运行 / FinBERT2 模型缺失而优雅跳过; "
            f"BERT 族缺席同样削弱方法多样性 (优雅降级, 不中断)。"
        )
    if n_llm == 0:
        logger.warning(
            f"  ⚠ [{track}] 未发现 LLM 独立模型情感列 → 阶段 21 可能未运行; "
            f"LLM 族缺席将无法做类别偏向/置信度校准诊断 (优雅降级, 不中断)。"
        )
    # 小样本警告: 盘面 T=2 仅验证管道正确性
    if len(df) < 1000:
        logger.info(
            f"  ⚠ 本轨样本 n={len(df):,} 篇属小样本 (盘面 T=2 / 子样本); 上述 α / ρ / 一致率 "
            f"仅用于验证三角验证管道正确性, 全量结论以 17M / T=18 实测为准。"
        )
    logger.info("-" * 72)


if __name__ == "__main__":
    main()
