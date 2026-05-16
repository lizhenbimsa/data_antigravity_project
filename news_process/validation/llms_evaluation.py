"""
news_process.validation.llms_evaluation — 阶段33：新闻分类模型评估

迁移说明 (Phase 7b)：
    本模块由原 root script ``33_news_llms_evaluation.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.llms_evaluation``

=======================================================

功能：
    根据国际顶级期刊标准，对新闻分类系统进行全面的性能评估。

    评估内容：
      1. 编码者间一致性 (Inter-Coder Reliability)
         - Cohen's Kappa（2 名编码者）
         - Krippendorff's Alpha（多编码者扩展）
      2. 分类器性能评估
         - Precision / Recall / F1-Score
         - 混淆矩阵（含可视化）
         - McNemar 检验（比较规则分类器 vs LLM 分类器）
      3. 误分类系统相关性诊断 (Carlson & Burbano 2026)
      4. 输出 LaTeX 格式表格（可直接嵌入论文）

    学术依据：
      - Loughran, T. & McDonald, B. (2011). "When Is a Liability Not a Liability?
        Textual Analysis, Dictionaries, and 10-Ks." Journal of Finance, 66(1), 35-65.
      - Krippendorff, K. (2018). Content Analysis: An Introduction to Its
        Methodology (4th ed.). Sage. Threshold: Krippendorff's Alpha >= 0.80.
        (Cohen's Kappa >= 0.80 threshold: Landis & Koch 1977, Biometrics 33(1):159-174)
      - Tetlock, P., Saar-Tsechansky, M., & Macskassy, S. (2008). "More Than Words:
        Quantifying Language to Measure Firms' Fundamentals." JF, 63(3), 1437-1467.
      - Carlson, N. A. & Burbano, V. C. (2026). "The Use of LLMs to Annotate Data
        in Management Research." Strategic Management Journal, 47(3), 699-725.

输入：
    阶段 32 输出的人工验证 Excel 文件（已填写编码者判定）

输出：
    评估报告（日志 + CSV + PNG 图表 + LaTeX 表格）
"""

import json
import os
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/llms_evaluation.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import log_stage_summary, setup_logging
from news_process.core.plotting import configure_matplotlib_chinese_fonts

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "33_news_llms_evaluation"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# ============================================================================
# 2. 统计指标计算函数
# ============================================================================

def compute_cohens_kappa(rater1: np.ndarray, rater2: np.ndarray) -> dict:
    """计算 Cohen's Kappa 编码者间一致性系数（支持多分类）。

    基于混淆矩阵方法，自动适配任意数量的类别。当输入为二分类 (0/1)
    时，结果与旧版完全一致；当输入为三分类 (0/1/2) 或更多类别时，
    expected_agreement 正确累加所有类别的边际概率乘积。

    数学公式 (Cohen 1960, Educational and Psychological Measurement):
        p_o = Σ_k n_{kk} / N           (观察一致率：对角线之和 / 总数)
        p_e = Σ_k (n_{k·} × n_{·k}) / N²  (随机一致率：行和 × 列和之积)
        κ   = (p_o - p_e) / (1 - p_e)

    Args:
        rater1: 编码者 A 的判定数组（整型，支持任意类别值）。
        rater2: 编码者 B 的判定数组（整型，支持任意类别值）。

    Returns:
        dict: 包含 kappa, observed_agreement, expected_agreement, n_samples 的字典。
    """
    rater1 = np.asarray(rater1)
    rater2 = np.asarray(rater2)
    assert len(rater1) == len(rater2), "两个编码者的样本数必须一致"
    n = len(rater1)

    if n == 0:
        return {'kappa': 0.0, 'observed_agreement': 0.0,
                'expected_agreement': 0.0, 'n_samples': 0}

    # 自动发现所有类别（合并两个编码者的标签集）
    categories = sorted(set(np.concatenate([rater1, rater2])))
    cat_idx = {c: i for i, c in enumerate(categories)}
    k = len(categories)

    # 构建 k×k 混淆矩阵
    confusion = np.zeros((k, k), dtype=int)
    for a, b in zip(rater1, rater2):
        confusion[cat_idx[a], cat_idx[b]] += 1

    # 观察一致率 p_o = 对角线之和 / N
    observed_agreement = float(np.trace(confusion)) / n

    # 随机一致率 p_e = Σ_k (行和_k × 列和_k) / N²
    row_sums = confusion.sum(axis=1)   # 编码者 A 各类别频次
    col_sums = confusion.sum(axis=0)   # 编码者 B 各类别频次
    expected_agreement = float((row_sums * col_sums).sum()) / (n * n)

    # Kappa
    if expected_agreement == 1.0:
        kappa = 1.0
    else:
        kappa = (observed_agreement - expected_agreement) / (1 - expected_agreement)

    return {
        'kappa': round(kappa, 4),
        'observed_agreement': round(observed_agreement, 4),
        'expected_agreement': round(expected_agreement, 4),
        'n_samples': n,
    }


def compute_krippendorffs_alpha(ratings_matrix: np.ndarray) -> float:
    """计算 Krippendorff's Alpha（支持多编码者）。

    采用名义尺度 (nominal) 的计算方式。

    Args:
        ratings_matrix: 形状 (n_coders, n_items)，
                        值为类别标签（int），-1 表示缺失。

    Returns:
        float: Krippendorff's Alpha 值。
    """
    n_coders, n_items = ratings_matrix.shape
    valid_mask = ratings_matrix >= 0  # 非缺失标记

    # 收集所有非缺失的类别值
    all_values = set()
    for c in range(n_coders):
        for i in range(n_items):
            if valid_mask[c, i]:
                all_values.add(int(ratings_matrix[c, i]))

    if len(all_values) <= 1:
        return 1.0  # 只有一个类别则完全一致

    # 计算观察的不一致度 D_o
    D_o = 0.0
    n_pairable = 0
    for i in range(n_items):
        coders_for_item = []
        for c in range(n_coders):
            if valid_mask[c, i]:
                coders_for_item.append(int(ratings_matrix[c, i]))
        m_u = len(coders_for_item)
        if m_u < 2:
            continue
        n_pairable += m_u
        # 在该 item 上，所有编码者对的不一致度
        counter = Counter(coders_for_item)
        for v1 in all_values:
            for v2 in all_values:
                if v1 != v2:
                    D_o += float(counter.get(v1, 0) * counter.get(v2, 0)) / float(m_u - 1)

    if n_pairable == 0:
        return 0.0

    D_o /= n_pairable

    # 计算期望的不一致度 D_e
    total_counter = Counter()
    for c in range(n_coders):
        for i in range(n_items):
            if valid_mask[c, i]:
                val = int(ratings_matrix[c, i])
                total_counter[val] = total_counter.get(val, 0) + 1
    n_total = sum(int(x) for x in total_counter.values())

    D_e = 0.0
    for v1 in all_values:
        for v2 in all_values:
            if v1 != v2:
                D_e += float(total_counter.get(v1, 0) * total_counter.get(v2, 0))
    D_e /= float(n_total * (n_total - 1))

    if D_e == 0:
        return 1.0

    alpha = 1.0 - D_o / D_e
    return round(alpha, 4)


def compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, labels: list = None) -> dict:
    """计算分类器的 Precision / Recall / F1 / 准确率。支持二分类和多分类。

    Args:
        y_true: 真实标签（人工黄金标准）。
        y_pred: 预测标签（分类器输出）。
        labels: 类别列表。如果提供，则按指定的类别计算多分类指标（包括混淆矩阵）。

    Returns:
        dict: 包含宏平均、加权平均、以及每个类别的精确率、召回率、F1和混淆矩阵等。
    """
    try:
        from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
    except ImportError:
        logger.error("缺少 scikit-learn 依赖，请运行: pip install scikit-learn")
        raise ImportError("scikit-learn 未安装，无法执行评估指标计算。请运行: pip install scikit-learn")
    
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    
    # 提取唯一标签，如果未提供 labels
    if labels is None:
        labels = np.unique(np.concatenate([y_true, y_pred]))

    acc = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    metrics = {
        'accuracy': round(float(acc), 4),
        'confusion_matrix': cm.tolist(),
        'labels': labels.tolist() if hasattr(labels, 'tolist') else list(labels),
        'total': len(y_true)
    }

    # 使用 macro (各类别算术平均) 和 weighted (基于支持度加权平均) 分别计算
    for avg_method in ['macro', 'weighted']:
        prec, rec, f1, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=labels, average=avg_method, zero_division=0
        )
        metrics[avg_method] = {
            'precision': round(float(prec), 4),
            'recall': round(float(rec), 4),
            'f1': round(float(f1), 4)
        }
        
    # 计算每个类别的独立指标
    prec_arr, rec_arr, f1_arr, support_arr = precision_recall_fscore_support(
        y_true, y_pred, labels=labels, average=None, zero_division=0
    )
    
    metrics['per_class'] = {}
    for i, label in enumerate(labels):
        metrics['per_class'][str(label)] = {
            'precision': round(float(prec_arr[i]), 4),
            'recall': round(float(rec_arr[i]), 4),
            'f1': round(float(f1_arr[i]), 4),
            'support': int(support_arr[i])
        }

    return metrics


def compute_mcnemar_test(y_true: np.ndarray,
                         y_pred_a: np.ndarray,
                         y_pred_b: np.ndarray) -> dict:
    """McNemar 检验：比较两个分类器性能的统计显著性。

    基于两个分类器在同一样本上的错误模式差异。

    Args:
        y_true:  真实标签。
        y_pred_a: 分类器 A 的预测。
        y_pred_b: 分类器 B 的预测。

    Returns:
        dict: 包含 chi2_statistic, p_value, significant(bool) 的字典。
    """
    correct_a = (y_pred_a == y_true)
    correct_b = (y_pred_b == y_true)

    # b: A 对 B 错的个数, c: A 错 B 对的个数
    b = int(np.sum(correct_a & ~correct_b))
    c = int(np.sum(~correct_a & correct_b))

    if (b + c) == 0:
        return {'chi2_statistic': 0.0, 'p_value': 1.0, 'significant': False,
                'b_count': b, 'c_count': c}

    # McNemar 统计量（带连续性校正）
    chi2_stat = (abs(b - c) - 1) ** 2 / (b + c)

    # chi2(df=1) 的 p 值近似——使用 scipy 不一定可用，手动近似
    # 对 df=1 的卡方分布：p ≈ erfc(sqrt(chi2/2)) (正态近似)
    # 精确做法：使用正则化不完全 Gamma 函数
    try:
        from scipy.stats import chi2 as chi2_dist
        p_value = float(chi2_dist.sf(chi2_stat, df=1))
    except ImportError:
        # 正态近似回退
        import math
        z = math.sqrt(chi2_stat)
        p_value = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))

    return {
        'chi2_statistic': round(chi2_stat, 4),
        'p_value': round(p_value, 6),
        'significant': p_value < 0.05,
        'b_count': b,
        'c_count': c,
    }


# ============================================================================
# 3. 可视化函数
# ============================================================================

def save_confusion_matrix_plot(metrics: dict, classifier_name: str,
                               output_path: str, logger_inst):
    """保存混淆矩阵为 PNG 图片。

    Args:
        metrics:         compute_classification_metrics 的返回值。
        classifier_name: 分类器名称（用于标题）。
        output_path:     PNG 文件保存路径。
        logger_inst:     日志记录器。
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        configure_matplotlib_chinese_fonts()

        cm = np.array(metrics['confusion_matrix'])
        labels = metrics['labels']
        n_classes = len(labels)

        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(cm, cmap='Blues', interpolation='nearest')

        # 标注数值
        for i in range(n_classes):
            for j in range(n_classes):
                color = 'white' if cm[i, j] > cm.max() / 2 else 'black'
                ax.text(j, i, f'{cm[i, j]}',
                        ha='center', va='center', color=color, fontsize=16)

        ax.set_xticks(range(n_classes))
        ax.set_yticks(range(n_classes))
        
        # 兼容二分类标签和多分类标签
        labels_str_set = set(str(l) for l in labels)
        if labels_str_set == {'0', '1'}:
            # 统一转 str 做索引查找，避免 int/str 类型不匹配
            labels_as_str = [str(l) for l in labels]
            idx_0 = labels_as_str.index('0')
            idx_1 = labels_as_str.index('1')
            xticklabels = [''] * 2
            xticklabels[idx_0] = '预测: 否 (0)'
            xticklabels[idx_1] = '预测: 是 (1)'
            yticklabels = [''] * 2
            yticklabels[idx_0] = '实际: 否 (0)'
            yticklabels[idx_1] = '实际: 是 (1)'
            ax.set_xticklabels(xticklabels)
            ax.set_yticklabels(yticklabels)
        else:
            ax.set_xticklabels([f'预测: {l}' for l in labels])
            ax.set_yticklabels([f'实际: {l}' for l in labels])
            
        ax.set_xlabel('预测标签', fontsize=12)
        ax.set_ylabel('真实标签', fontsize=12)
        
        # 提取 macro f1 做标题
        macro_prec = metrics.get('macro', {}).get('precision', 0.0)
        macro_rec = metrics.get('macro', {}).get('recall', 0.0)
        macro_f1 = metrics.get('macro', {}).get('f1', 0.0)
        
        ax.set_title(f'{classifier_name} (Macro Avg)\n'
                     f'Precision={macro_prec:.3f}  '
                     f'Recall={macro_rec:.3f}  '
                     f'F1={macro_f1:.3f}', fontsize=11)

        fig.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        logger_inst.info(f"混淆矩阵图已保存: {output_path}")

    except ImportError:
        logger_inst.warning("matplotlib 不可用，跳过混淆矩阵图绘制")
    except Exception as e:
        logger_inst.warning(f"绘制混淆矩阵图失败: {e}")


# ============================================================================
# 4. LaTeX 格式输出
# ============================================================================

def generate_latex_table(results: dict, output_path: str, logger_inst):
    """生成 LaTeX 格式的评估结果表格，分任务输出。

    Args:
        results:     包含各项测试指标的字典。
        output_path: .tex 文件保存路径。
        logger_inst: 日志记录器。
    """
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Validation and Sentiment Performance Evaluation}",
        r"\label{tab:dual_task_classification_eval}",
        r"\begin{tabular}{lcccc}",
        r"\hline",
        r"Task/Classifier & Precision & Recall & F1-Score & Accuracy \\",
        r"\hline",
    ]

    # 添加 Verification 评估结果
    lines.append(r"\multicolumn{5}{l}{\textbf{Panel A: Verification Task (Binary)}} \\")
    for name, metrics in results.get('classifier_metrics', {}).get('verification', {}).items():
        macro = metrics.get('macro', {})
        lines.append(
            f"  {name} & {macro.get('precision', 0):.3f} & "
            f"{macro.get('recall', 0):.3f} & {macro.get('f1', 0):.3f} & "
            f"{metrics.get('accuracy', 0):.3f} \\\\"
        )
        
    lines.append(r"\hline")

    # 添加 Sentiment 评估结果
    lines.append(r"\multicolumn{5}{l}{\textbf{Panel B: Sentiment Task (Three-class, Macro Avg)}} \\")
    for name, metrics in results.get('classifier_metrics', {}).get('sentiment', {}).items():
        macro = metrics.get('macro', {})
        lines.append(
            f"  {name} & {macro.get('precision', 0):.3f} & "
            f"{macro.get('recall', 0):.3f} & {macro.get('f1', 0):.3f} & "
            f"{metrics.get('accuracy', 0):.3f} \\\\"
        )

    lines.append(r"\hline")

    # Panel C: 情感任务逐类别 Recall（cf. FinBERT Table 1 Panel A）
    sentiment_metrics = results.get('classifier_metrics', {}).get('sentiment', {})
    if sentiment_metrics:
        lines.append(r"\multicolumn{5}{l}{\textbf{Panel C: Sentiment Per-class Recall}} \\")
        lines.append(r"\hline")
        # 表头改为: Classifier & 正面 Recall & 中性 Recall & 负面 Recall & Support \\
        lines.append(r"Classifier & Pos.~Recall & Neu.~Recall & Neg.~Recall & Total \\")
        lines.append(r"\hline")
        for name, metrics in sentiment_metrics.items():
            pc = metrics.get('per_class', {})
            pos_r = pc.get('正面', pc.get('positive', {})).get('recall', 0) if isinstance(pc.get('正面', pc.get('positive', {})), dict) else 0
            neu_r = pc.get('中性', pc.get('neutral', {})).get('recall', 0) if isinstance(pc.get('中性', pc.get('neutral', {})), dict) else 0
            neg_r = pc.get('负面', pc.get('negative', {})).get('recall', 0) if isinstance(pc.get('负面', pc.get('negative', {})), dict) else 0
            total = metrics.get('total', 0)
            lines.append(
                f"  {name} & {pos_r:.3f} & {neu_r:.3f} & {neg_r:.3f} & {total} \\\\"
            )

    # Panel D: 误分类系统相关性诊断 (Carlson & Burbano 2026)
    bias_full = results.get('misclassification_bias_full', {})
    bias_tests = bias_full.get('tests', []) if isinstance(bias_full, dict) else []
    non_skipped = [t for t in bias_tests if not t.get('skipped', True)]
    if non_skipped:
        lines.append(r"\hline")
        lines.append(r"\multicolumn{5}{l}{\textbf{Panel D: Misclassification Bias Diagnostic}} \\")
        lines.append(r"\hline")
        lines.append(r"Variable & Grp A Mean & Grp B Mean & Statistic & p-value \\")
        lines.append(r"\hline")
        for t in non_skipped:
            ma = f"{t['mean_a']:.4f}" if t.get('mean_a') is not None else 'N/A'
            mb = f"{t['mean_b']:.4f}" if t.get('mean_b') is not None else 'N/A'
            st = f"{t['statistic']:.4f}" if t.get('statistic') is not None else 'N/A'
            pv = f"{t['p_value']:.4f}" if t.get('p_value') is not None else 'N/A'
            vn = t.get('var', '').replace('_', r'\_')
            lines.append(f"  {vn} & {ma} & {mb} & {st} & {pv} \\\\")

    lines.extend([
        r"\hline",
        r"\end{tabular}",
    ])

    # Plan v1.37 P0 §3.3.2 + R12C-01 + R21A-01: Panels E (substantiveness)
    # + F (locus) in a SEPARATE \begin{tabular}...\end{tabular} block.
    # Per R21A-01 pending-case reconciliation, Panel E/F subheaders are
    # ALWAYS present; only data rows differ between populated and pending.
    pending_reason = results.get('innovation_pending_reason')
    lines.extend([
        "",
        r"\bigskip",
        r"\begin{tabular}{lcccc}",
        r"\hline",
        r"\multicolumn{5}{l}{\textbf{Panel E: Innovation Substantiveness (binary, W\&Z 1994/1998 ASQ)}} \\",
        r"\hline",
    ])
    subst_metrics = results.get('classifier_metrics', {}).get('innovation_substantiveness', {})
    if pending_reason or not subst_metrics:
        reason_text = pending_reason or 'n=0'
        lines.append(rf"\multicolumn{{5}}{{l}}{{manual validation pending --- {reason_text}}} \\")
    else:
        for name, metrics in subst_metrics.items():
            macro = metrics.get('macro', {})
            lines.append(
                rf"  {name} & {macro.get('precision', 0):.3f} & "
                rf"{macro.get('recall', 0):.3f} & {macro.get('f1', 0):.3f} & "
                rf"{metrics.get('accuracy', 0):.3f} \\"
            )
    lines.extend([
        r"\hline",
        r"\multicolumn{5}{l}{\textbf{Panel F: Innovation Locus (binary, Gomber 2018 JMIS)}} \\",
        r"\hline",
    ])
    locus_metrics = results.get('classifier_metrics', {}).get('innovation_locus', {})
    if pending_reason or not locus_metrics:
        reason_text = pending_reason or 'n=0'
        lines.append(rf"\multicolumn{{5}}{{l}}{{manual validation pending --- {reason_text}}} \\")
    else:
        for name, metrics in locus_metrics.items():
            macro = metrics.get('macro', {})
            lines.append(
                rf"  {name} & {macro.get('precision', 0):.3f} & "
                rf"{macro.get('recall', 0):.3f} & {macro.get('f1', 0):.3f} & "
                rf"{metrics.get('accuracy', 0):.3f} \\"
            )
    lines.extend([
        r"\hline",
        r"\end{tabular}",
    ])

    # 编码者间一致性注脚 (Verification)
    icr_v = results.get('inter_coder_reliability', {}).get('verification', {})
    if icr_v:
        kappa_info = icr_v.get('cohens_kappa', {})
        alpha = icr_v.get('krippendorffs_alpha', 'N/A')
        lines.append(r"\begin{tablenotes}[flushleft]\footnotesize")
        lines.append(rf"  \item Verification ICR: Cohen's $\kappa$ = {kappa_info.get('kappa', 'N/A')}, Krippendorff's $\alpha$ = {alpha}")
        
        icr_s = results.get('inter_coder_reliability', {}).get('sentiment', {})
        if icr_s:
            kappa_info_s = icr_s.get('cohens_kappa', {})
            alpha_s = icr_s.get('krippendorffs_alpha', 'N/A')
            lines.append(rf"  \item Sentiment ICR: Cohen's $\kappa$ = {kappa_info_s.get('kappa', 'N/A')}, Krippendorff's $\alpha$ = {alpha_s}")
            
        lines.append(r"\end{tablenotes}")

    lines.append(r"\end{table}")

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        logger_inst.info(f"LaTeX 表格已保存: {output_path}")
    except Exception as e:
        logger_inst.warning(f"保存 LaTeX 表格失败: {e}")


# ============================================================================
# 4b. 误分类系统相关性诊断 (Carlson & Burbano 2026, SMJ)
# ============================================================================

SENTIMENT_MAP_DIAG = {'正面': 1, '中性': 0, '负面': -1}


def _safe_ttest(group_a, group_b, label_a, label_b, var_name, logger_inst):
    """安全执行 Welch's t-test，处理所有边界情况。

    边界情况处理:
      - 任一组样本量 < 2 → skipped
      - scipy 未安装 → skipped
      - 方差均为 0 → skipped (scipy 会抛 warning)
    """
    n_a = int(np.sum(~np.isnan(group_a))) if len(group_a) > 0 else 0
    n_b = int(np.sum(~np.isnan(group_b))) if len(group_b) > 0 else 0
    result = {
        'var': var_name, 'test': 'welch_t',
        'group_a': label_a, 'n_a': n_a,
        'mean_a': round(float(np.nanmean(group_a)), 4) if n_a > 0 else None,
        'group_b': label_b, 'n_b': n_b,
        'mean_b': round(float(np.nanmean(group_b)), 4) if n_b > 0 else None,
        'statistic': None, 'p_value': None, 'significant': None,
        'skipped': False, 'skip_reason': None,
    }
    if n_a < 2 or n_b < 2:
        result['skipped'] = True
        result['skip_reason'] = f'样本量不足 (n_a={n_a}, n_b={n_b}，至少需要 2)'
        if logger_inst:
            logger_inst.info(f"    {var_name}: 跳过 — {result['skip_reason']}")
        return result
    try:
        from scipy.stats import ttest_ind
        stat, p = ttest_ind(group_a, group_b, equal_var=False, nan_policy='omit')
        result['statistic'] = round(float(stat), 4)
        result['p_value'] = round(float(p), 6)
        result['significant'] = bool(p < 0.05)
    except ImportError:
        result['skipped'] = True
        result['skip_reason'] = 'scipy 未安装'
    except Exception as e:
        result['skipped'] = True
        result['skip_reason'] = str(e)
    if logger_inst and not result['skipped']:
        diff = (result['mean_a'] or 0) - (result['mean_b'] or 0)
        sig = '显著' if result['significant'] else '不显著'
        logger_inst.info(
            f"    {var_name}: {label_a}均值={result['mean_a']}(n={n_a}), "
            f"{label_b}均值={result['mean_b']}(n={n_b}), "
            f"差值={diff:+.4f}, t={result['statistic']}, p={result['p_value']} {sig}"
        )
    return result


def _safe_kstest(group_a, group_b, label_a, label_b, var_name, logger_inst):
    """安全执行 Kolmogorov-Smirnov 双样本检验。"""
    n_a = int(np.sum(~np.isnan(group_a))) if len(group_a) > 0 else 0
    n_b = int(np.sum(~np.isnan(group_b))) if len(group_b) > 0 else 0
    result = {
        'var': var_name, 'test': 'ks_2samp',
        'group_a': label_a, 'n_a': n_a, 'mean_a': None,
        'group_b': label_b, 'n_b': n_b, 'mean_b': None,
        'statistic': None, 'p_value': None, 'significant': None,
        'skipped': False, 'skip_reason': None,
    }
    if n_a < 1 or n_b < 1:
        result['skipped'] = True
        result['skip_reason'] = f'样本量不足 (n_a={n_a}, n_b={n_b})'
        if logger_inst:
            logger_inst.info(f"    {var_name} KS: 跳过 — {result['skip_reason']}")
        return result
    try:
        from scipy.stats import ks_2samp
        stat, p = ks_2samp(group_a[~np.isnan(group_a)], group_b[~np.isnan(group_b)])
        result['statistic'] = round(float(stat), 4)
        result['p_value'] = round(float(p), 6)
        result['significant'] = bool(p < 0.05)
    except ImportError:
        result['skipped'] = True
        result['skip_reason'] = 'scipy 未安装'
    except Exception as e:
        result['skipped'] = True
        result['skip_reason'] = str(e)
    if logger_inst and not result['skipped']:
        sig = '显著' if result['significant'] else '不显著'
        logger_inst.info(
            f"    {var_name} KS: D={result['statistic']}, p={result['p_value']} {sig}"
        )
    return result


def _evaluate_innovation_panels(results: dict, output_dir: str, logger_inst) -> None:
    """Plan v1.37 P0 §3.3.1: populate Panel E (substantiveness) + Panel F (locus).

    Reads manual_validation_samples.xlsx (3-rater R1/R2/R3 stage3a/3b cols),
    merges via majority-vote into single gold column, joins to LLM predictions
    from 21_tone_llms.parquet, computes per-model + aggregate classification
    metrics. Sets results['innovation_pending_reason'] to one of:
      None (data available), 'file not present', 'schema mismatch', 'n=0'.

    Outputs (when gold data present):
      - eval_reports/cm_innovation_{substantiveness,locus}_llm_{full,ctx}.png
      - eval_reports/per_model_innovation_{substantiveness,locus}_comparison.csv
    """
    from news_process.core.config import load_config
    from news_process.validation.manual_validation_schema import (
        R_COLUMNS_BY_RATER,
        merge_three_rater_majority,
    )

    config = load_config()
    output_dir_cfg = config.get('paths', {}).get('output_dir', output_dir)
    mv_path = os.path.join(output_dir_cfg, 'manual_validation_samples.xlsx')

    # Reachability check 1: file absent
    if not os.path.exists(mv_path):
        results['innovation_pending_reason'] = 'file not present'
        logger_inst.info(
            f"  manual_validation_samples.xlsx absent at {mv_path}; "
            f"Panels E/F → pending."
        )
        return

    # Load xlsx
    try:
        xl = pd.ExcelFile(mv_path)
        sheet = xl.sheet_names[0]
        df_mv = pd.read_excel(xl, sheet_name=sheet)
    except Exception as exc:
        results['innovation_pending_reason'] = 'file not present'
        logger_inst.warning(
            f"  failed to read manual_validation_samples.xlsx: {exc}; pending."
        )
        return

    # Reachability check 2: schema mismatch
    all_r_cols = R_COLUMNS_BY_RATER['substantiveness'] + R_COLUMNS_BY_RATER['locus']
    missing = [c for c in all_r_cols if c not in df_mv.columns]
    if missing:
        results['innovation_pending_reason'] = 'schema mismatch'
        logger_inst.warning(
            f"  manual_validation_samples.xlsx missing R-columns: {missing}; "
            f"Panels E/F → pending (schema mismatch)."
        )
        return

    # Merge raters → gold (per-row majority vote on 3 raters)
    df_mv = df_mv.copy()
    df_mv['gold_substantiveness'] = df_mv.apply(
        lambda r: merge_three_rater_majority(r, R_COLUMNS_BY_RATER['substantiveness']),
        axis=1,
    )
    df_mv['gold_locus'] = df_mv.apply(
        lambda r: merge_three_rater_majority(r, R_COLUMNS_BY_RATER['locus']),
        axis=1,
    )

    n_gold_subst = df_mv['gold_substantiveness'].notna().sum()
    n_gold_locus = df_mv['gold_locus'].notna().sum()

    # Reachability check 3: all R-cells NaN
    if n_gold_subst == 0 and n_gold_locus == 0:
        results['innovation_pending_reason'] = 'n=0'
        logger_inst.warning(
            f"  manual_validation_samples.xlsx present but all R-cells NaN; "
            f"Panels E/F → pending (n=0)."
        )
        return

    # Join with 21_tone_llms predictions
    llms_path = os.path.join(output_dir_cfg, '21_tone_llms.parquet')
    if not os.path.exists(llms_path):
        results['innovation_pending_reason'] = 'file not present'
        logger_inst.warning(
            f"  21_tone_llms.parquet absent at {llms_path}; Panels E/F → pending."
        )
        return
    df_pred = pd.read_parquet(llms_path)

    # Determine join key: prefer docid (production). If absent in either df,
    # mark schema mismatch and bail (positional/orig_index fallback would
    # require careful column-name disambiguation; deferred).
    # Rα3-01 fix: unconditional return when no usable key (previously dead-coded).
    if 'docid' not in df_mv.columns or 'docid' not in df_pred.columns:
        logger_inst.warning(
            "  no shared docid join key between manual_validation_samples.xlsx "
            "and 21_tone_llms.parquet; Panels E/F → pending (schema mismatch)."
        )
        results['innovation_pending_reason'] = 'schema mismatch'
        return
    join_key = 'docid'

    # Deduplicate join key (R2C-04 + plan §3.3.3 test 14)
    df_mv = df_mv.drop_duplicates(subset=[join_key], keep='first')
    df_pred = df_pred.drop_duplicates(subset=[join_key], keep='first')

    df_joined = df_mv.merge(df_pred, on=join_key, how='inner', suffixes=('_mv', ''))

    # Evaluate each innovation dim + each track
    for task_name, gold_col, pred_template, class_labels in [
        ('innovation_substantiveness', 'gold_substantiveness',
         'innovation_substantiveness{track}', ['实质性', '象征性']),
        ('innovation_locus', 'gold_locus',
         'innovation_locus{track}', ['底层技术', '应用场景']),
    ]:
        for track in ['_full', '_ctx']:
            pred_col = pred_template.format(track=track)
            if pred_col not in df_joined.columns:
                logger_inst.info(f"  pred col {pred_col} absent; skip.")
                continue
            mask = df_joined[gold_col].notna() & df_joined[pred_col].notna()
            if mask.sum() < 2:
                logger_inst.info(
                    f"  {task_name}{track}: only {mask.sum()} paired rows; "
                    f"skip metrics."
                )
                continue
            y_true = df_joined.loc[mask, gold_col].astype(str).to_numpy()
            y_pred = df_joined.loc[mask, pred_col].astype(str).to_numpy()
            metrics = compute_classification_metrics(y_true, y_pred, labels=class_labels)
            results['classifier_metrics'][task_name][f'LLM ({track})'] = metrics
            try:
                save_confusion_matrix_plot(
                    metrics,
                    f"LLM {task_name}{track}",
                    os.path.join(output_dir, f'cm_{task_name}_llm{track}.png'),
                    logger_inst,
                )
            except Exception as exc:
                logger_inst.warning(f"  cm plot {task_name}{track} failed: {exc}")
        # Per-model comparison CSV
        rows = []
        for k, m in results['classifier_metrics'][task_name].items():
            rows.append({
                '模型': k,
                'Precision': m.get('macro', {}).get('precision', float('nan')),
                'Recall': m.get('macro', {}).get('recall', float('nan')),
                'F1-Score': m.get('macro', {}).get('f1', float('nan')),
                'Accuracy': m.get('accuracy', float('nan')),
            })
        if rows:
            comp_df = pd.DataFrame(rows)
            comp_path = os.path.join(output_dir, f'per_model_{task_name}_comparison.csv')
            comp_df.to_csv(comp_path, index=False, encoding='utf-8-sig')
            logger_inst.info(f"  {task_name} per-model CSV: {comp_path}")

    logger_inst.info(
        f"  Panels E/F populated: n_gold_subst={n_gold_subst}, n_gold_locus={n_gold_locus}"
    )


def diagnose_misclassification_bias(
    df_verify: pd.DataFrame,
    gold_ver_col: str,
    track: str = '_full',
    logger_inst=None,
    output_dir: str = None,
) -> dict:
    """第一阶段误分类 vs 下游变量系统相关性诊断。

    学术依据:
      Carlson, N. A. & Burbano, V. C. (2026). "The Use of LLMs to Annotate
      Data in Management Research: Foundational Guidelines and Warnings."
      Strategic Management Journal, 47(3), 699-725.

      核心论点 (Figure 1): "greater accuracy in the first stage does not
      necessarily translate to better recovery of the 'true' effect if the
      direction of error is correlated with the second-stage dependent variable."

    检验项:
      T1: FP vs TP 情感分数 (t-test)     — 检测 FP 是否偏正面
      T2: FN vs TN 情感分数 (t-test)     — 检测 FN 是否偏负面
      T3: FP vs TP 情感分数 (KS)         — 分布形状差异
      T4: FN vs TN 情感分数 (KS)         — 分布形状差异
      T5: 误分类 vs 正确 文本长度 (t-test) — 长度偏差
      T6: 误分类 vs 正确 置信度 (t-test)   — 置信度校准

    Args:
        df_verify:    金标准验证样本 DataFrame。
        gold_ver_col: 黄金标准验证列名（如 '最终_验证'）。
        track:        轨道后缀（'_full' 或 '_ctx'）。
        logger_inst:  日志记录器（可选）。
        output_dir:   CSV 输出目录（可选）。

    Returns:
        dict: 包含四象限计数、检验结果列表和总体结论。
    """
    ver_col = f'llm_verified{track}'
    sent_col = f'llm_sentiment{track}'
    lg = logger_inst

    diag = {'track': track, 'tests': [], 'quadrant_counts': {}, 'conclusion': ''}

    # ── 安全检查 ──
    if gold_ver_col not in df_verify.columns or ver_col not in df_verify.columns:
        if lg:
            lg.warning(f"  [{track}] 缺少必要列 ({gold_ver_col} 或 {ver_col})，跳过诊断")
        diag['conclusion'] = '缺少必要列，诊断跳过'
        return diag

    if lg:
        lg.info(f"  [{track}] 开始诊断: 金标准列='{gold_ver_col}', 预测列='{ver_col}', 样本数={len(df_verify)}")

    df = df_verify.copy()
    df['_gold'] = pd.to_numeric(df[gold_ver_col], errors='coerce').fillna(0).astype(int)
    # 处理 bool / str / int 混合类型
    _pred_raw = df[ver_col].fillna(False)
    if _pred_raw.dtype == object:
        df['_pred'] = _pred_raw.map(
            lambda x: 1 if str(x).strip().lower() in ('true', '1', 'yes') else 0
        ).astype(int)
        if lg:
            lg.info(f"  [{track}] 预测列类型: object (str)，已映射为 0/1")
    else:
        df['_pred'] = _pred_raw.astype(int)
        if lg:
            lg.info(f"  [{track}] 预测列类型: {_pred_raw.dtype}")

    # ── 四象限 ──
    tp = (df['_gold'] == 1) & (df['_pred'] == 1)
    fp = (df['_gold'] == 0) & (df['_pred'] == 1)
    fn = (df['_gold'] == 1) & (df['_pred'] == 0)
    tn = (df['_gold'] == 0) & (df['_pred'] == 0)
    n_tp, n_fp, n_fn, n_tn = int(tp.sum()), int(fp.sum()), int(fn.sum()), int(tn.sum())
    diag['quadrant_counts'] = {'TP': n_tp, 'FP': n_fp, 'FN': n_fn, 'TN': n_tn}
    n_total = n_tp + n_fp + n_fn + n_tn
    n_wrong = n_fp + n_fn
    n_correct = n_tp + n_tn
    if lg:
        lg.info(f"  [{track}] 混淆矩阵四象限:")
        lg.info(f"  [{track}]   True Positive  (TP) = {n_tp:>4d}  (gold=1, pred=1: 正确保留)")
        lg.info(f"  [{track}]   False Positive (FP) = {n_fp:>4d}  (gold=0, pred=1: 应排除却保留)")
        lg.info(f"  [{track}]   False Negative (FN) = {n_fn:>4d}  (gold=1, pred=0: 应保留却排除)")
        lg.info(f"  [{track}]   True Negative  (TN) = {n_tn:>4d}  (gold=0, pred=0: 正确排除)")
        lg.info(f"  [{track}]   总计={n_total}, 误分类={n_wrong} ({n_wrong/max(n_total,1)*100:.1f}%), 正确={n_correct} ({n_correct/max(n_total,1)*100:.1f}%)")

    # ── 构建下游代理变量 ──
    if lg:
        lg.info(f"  [{track}] 构建下游代理变量...")

    # (a) 情感数值: 正面→+1, 中性→0, 负面→-1
    if sent_col in df.columns:
        df['_sent'] = df[sent_col].map(SENTIMENT_MAP_DIAG).astype(float)
        sent_dist = df['_sent'].value_counts().to_dict()
        if lg:
            lg.info(f"  [{track}]   (a) 情感分数 '{sent_col}': 映射 {{正面:+1, 中性:0, 负面:-1}}, 分布={sent_dist}")
    else:
        df['_sent'] = 0.0
        if lg:
            lg.info(f"  [{track}]   (a) 情感列 '{sent_col}' 不存在，默认全部为 0.0")

    # (b) 文本长度
    if '内容' in df.columns:
        df['_len'] = df['内容'].astype(str).str.len().astype(float)
        if lg:
            lg.info(f"  [{track}]   (b) 文本长度: min={df['_len'].min():.0f}, median={df['_len'].median():.0f}, max={df['_len'].max():.0f} 字符")
    else:
        df['_len'] = np.nan
        if lg:
            lg.info(f"  [{track}]   (b) '内容'列不存在，文本长度设为 NaN")

    # (c) 验证置信度均值（逐模型置信度列的平均）
    try:
        cfg = load_config()
        models = cfg.get('tone_llm_processing', {}).get('models', [])
    except Exception:
        models = []
    conf_cols = [f"{m.get('short_name', '')}_verification_confidence{track}"
                 for m in models if m.get('short_name', '')]
    conf_cols = [c for c in conf_cols if c in df.columns]
    df['_conf'] = df[conf_cols].mean(axis=1) if conf_cols else np.nan
    if lg:
        if conf_cols:
            lg.info(f"  [{track}]   (c) 验证置信度: 聚合 {len(conf_cols)} 个模型列均值, mean={df['_conf'].mean():.4f}")
        else:
            lg.info(f"  [{track}]   (c) 无可用验证置信度列 (模型数={len(models)})")

    if lg:
        lg.info(f"  [{track}] ── 开始 6 项统计检验 (Carlson & Burbano 2026, SMJ) ──")

    # ── T1: FP vs TP 情感偏差 ──
    if lg:
        lg.info(f"  [{track}] --- T1: FP vs TP 情感分数 (Welch's t-test) ---")
        lg.info(f"  [{track}]     目的: 检测被错误保留的非相关文章(FP)是否情感偏正面")
    diag['tests'].append(_safe_ttest(
        df.loc[fp, '_sent'].values, df.loc[tp, '_sent'].values,
        'FP', 'TP', f'情感分数{track}', lg))

    # ── T2: FN vs TN 情感偏差 ──
    if lg:
        lg.info(f"  [{track}] --- T2: FN vs TN 情感分数 (Welch's t-test) ---")
        lg.info(f"  [{track}]     目的: 检测被错误排除的相关文章(FN)是否情感偏负面")
    diag['tests'].append(_safe_ttest(
        df.loc[fn, '_sent'].values, df.loc[tn, '_sent'].values,
        'FN', 'TN', f'情感分数{track}', lg))

    # ── T3: FP vs TP 情感分布 (KS) ──
    if lg:
        lg.info(f"  [{track}] --- T3: FP vs TP 情感分布 (Kolmogorov-Smirnov) ---")
        lg.info(f"  [{track}]     目的: 检测 FP 与 TP 的情感分布形状是否存在差异")
    diag['tests'].append(_safe_kstest(
        df.loc[fp, '_sent'].values, df.loc[tp, '_sent'].values,
        'FP', 'TP', f'情感分布{track}', lg))

    # ── T4: FN vs TN 情感分布 (KS) ──
    if lg:
        lg.info(f"  [{track}] --- T4: FN vs TN 情感分布 (Kolmogorov-Smirnov) ---")
        lg.info(f"  [{track}]     目的: 检测 FN 与 TN 的情感分布形状是否存在差异")
    diag['tests'].append(_safe_kstest(
        df.loc[fn, '_sent'].values, df.loc[tn, '_sent'].values,
        'FN', 'TN', f'情感分布{track}', lg))

    # ── T5: 误分类 vs 正确 文本长度 ──
    wrong = fp | fn
    correct = tp | tn
    if lg:
        lg.info(f"  [{track}] --- T5: 误分类 vs 正确 文本长度 (Welch's t-test) ---")
        lg.info(f"  [{track}]     目的: 检测文本长度是否影响分类准确性")
    diag['tests'].append(_safe_ttest(
        df.loc[wrong, '_len'].values, df.loc[correct, '_len'].values,
        '误分类', '正确', f'文本长度{track}', lg))

    # ── T6: 误分类 vs 正确 验证置信度 ──
    if lg:
        lg.info(f"  [{track}] --- T6: 误分类 vs 正确 验证置信度 (Welch's t-test) ---")
        lg.info(f"  [{track}]     目的: 检测模型置信度是否能有效区分正确与错误分类")
    if conf_cols:
        diag['tests'].append(_safe_ttest(
            df.loc[wrong, '_conf'].values, df.loc[correct, '_conf'].values,
            '误分类', '正确', f'验证置信度{track}', lg))
    else:
        skip_entry = {
            'var': f'验证置信度{track}', 'test': 'welch_t',
            'group_a': '误分类', 'n_a': 0, 'mean_a': None,
            'group_b': '正确', 'n_b': 0, 'mean_b': None,
            'statistic': None, 'p_value': None, 'significant': None,
            'skipped': True, 'skip_reason': '无可用的验证置信度列',
        }
        diag['tests'].append(skip_entry)
        if lg:
            lg.info(f"    验证置信度: 跳过 — 无可用的验证置信度列")

    # ── 汇总结论 ──
    n_total_tests = len(diag['tests'])
    n_skipped = sum(1 for t in diag['tests'] if t.get('skipped', True))
    n_executed = n_total_tests - n_skipped
    sig_tests = [t for t in diag['tests']
                 if not t.get('skipped', True) and t.get('significant', False)]
    nonsig_tests = [t for t in diag['tests']
                    if not t.get('skipped', True) and not t.get('significant', False)]

    if lg:
        lg.info(f"  [{track}] ── 检验汇总 ──")
        lg.info(f"  [{track}]   总检验数: {n_total_tests}, 成功执行: {n_executed}, 跳过: {n_skipped}")
        lg.info(f"  [{track}]   显著(p<0.05): {len(sig_tests)}, 不显著: {len(nonsig_tests)}")
        if sig_tests:
            for t in sig_tests:
                lg.info(f"  [{track}]   {t['var']}: p={t.get('p_value','N/A')} (显著)")
        if nonsig_tests:
            for t in nonsig_tests:
                lg.info(f"  [{track}]   ✓  {t['var']}: p={t.get('p_value','N/A')}")

    if sig_tests:
        sig_names = [t['var'] for t in sig_tests]
        diag['conclusion'] = (
            f"发现 {len(sig_tests)}/{n_executed} 项显著系统相关: {sig_names}。"
            f"建议在论文 Robustness Check 中报告 (Carlson & Burbano 2026, SMJ)。"
        )
    else:
        diag['conclusion'] = (
            f"✓ {n_executed}/{n_executed} 项检验均不显著(p>0.05)，"
            f"未发现误分类与下游变量的系统相关，第一阶段筛选无方向性偏差证据。"
        )
    if lg:
        lg.info(f"  [{track}] 最终结论: {diag['conclusion']}")

    # ── 输出 CSV ──
    if output_dir:
        try:
            rows = []
            for t in diag['tests']:
                rows.append({
                    'track': track, 'variable': t.get('var', ''),
                    'test': t.get('test', ''),
                    'group_a': t.get('group_a', ''), 'n_a': t.get('n_a', ''),
                    'mean_a': t.get('mean_a', ''),
                    'group_b': t.get('group_b', ''), 'n_b': t.get('n_b', ''),
                    'mean_b': t.get('mean_b', ''),
                    'statistic': t.get('statistic', ''), 'p_value': t.get('p_value', ''),
                    'significant': t.get('significant', ''),
                    'skipped': t.get('skipped', False),
                    'skip_reason': t.get('skip_reason', ''),
                })
            csv_path = os.path.join(output_dir, f'misclassification_bias_diag{track}.csv')
            pd.DataFrame(rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
            if lg:
                lg.info(f"  [{track}] 诊断 CSV 已保存: {csv_path}")
        except Exception as e:
            if lg:
                lg.warning(f"  [{track}] 保存诊断 CSV 失败: {e}")

    return diag


# ============================================================================
# 5. 主函数
# ============================================================================

def main():
    """分类有效性评估主入口。

    .. todo:: v3.0-split (Plan-r3 P1-7 锚点, god function)

        本函数是 stage 33 的 monolithic 主流程, 内部 5 个职责紧耦合:
        1. 加载 verify + tone_llms parquet (含 schema 守护)
        2. compute_metrics -- precision/recall/F1 矩阵计算
        3. diagnose_misclassification_bias (本文件子函数)
        4. diagnose_confidence_calibration (validation/tone_validation.py)
        5. 报告渲染 + 多格式导出 (csv/markdown/json)

        v3.0 拆分: 每个职责独立函数 + 一个薄 main 编排器.
    """
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # 定义输入输出路径
    verify_path = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG['filenames'].get('output_32_human_sample', '32_news_llms_human_samples.xlsx')
    )
    output_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
    os.makedirs(output_dir, exist_ok=True)

    # ======================================================================
    # Step 1: 加载人工验证数据
    # ======================================================================
    if not os.path.exists(verify_path):
        logger.info(
            f"人工验证文件未找到: {verify_path}\n"
            f"  → 将生成模拟验证数据用于评估框架测试。\n"
            f"  → 请在人工编码完成后重新运行此脚本。"
        )
        # 生成模拟数据以验证框架正确性
        df_verify = _generate_demo_data()
        demo_mode = True
    else:
        logger.info(f"正在从 {verify_path} 加载人工验证数据...")
        try:
            # 优先读取"验证数据" sheet；若不存在则读取第一个 sheet
            xl = pd.ExcelFile(verify_path)
            sheet_name = '验证数据' if '验证数据' in xl.sheet_names else xl.sheet_names[0]
            if sheet_name != '验证数据':
                logger.info(f"  未找到 '验证数据' sheet，改用: '{sheet_name}'")
            df_verify = pd.read_excel(xl, sheet_name=sheet_name)
            demo_mode = False
        except Exception as e:
            logger.error(f"加载人工验证文件失败: {e}")
            logger.info("将使用模拟数据继续...")
            df_verify = _generate_demo_data()
            demo_mode = True

    logger.info(f"验证样本数: {len(df_verify):,} ({'模拟数据' if demo_mode else '真实数据'})")

    # ======================================================================
    # Step 2: 数据预处理——提取验证标签与情感标签
    # ======================================================================
    # 验证判定列
    coder_a_ver = '编码者A_验证'
    coder_b_ver = '编码者B_验证'
    final_ver = '最终_验证'

    # 情感判定列
    coder_a_sen = '编码者A_情感'
    coder_b_sen = '编码者B_情感'
    final_sen = '最终_情感'

    # 清理验证列（转 int）
    for col in [coder_a_ver, coder_b_ver, final_ver]:
        if col in df_verify.columns:
            df_verify[col] = pd.to_numeric(df_verify[col], errors='coerce')
            
    # 清理情感列（去除首尾空格）
    for col in [coder_a_sen, coder_b_sen, final_sen]:
        if col in df_verify.columns:
            df_verify[col] = df_verify[col].astype(str).str.strip()
            df_verify.loc[df_verify[col] == 'nan', col] = np.nan

    # 验证判定具备有效一致性样本的条件
    has_both_ver = (
        df_verify[coder_a_ver].notna() & df_verify[coder_b_ver].notna()
    ) if coder_a_ver in df_verify.columns and coder_b_ver in df_verify.columns else pd.Series(False, index=df_verify.index)
    
    has_both_sen = (
        df_verify[coder_a_sen].notna() & df_verify[coder_b_sen].notna()
    ) if coder_a_sen in df_verify.columns and coder_b_sen in df_verify.columns else pd.Series(False, index=df_verify.index)

    n_both_ver = int(has_both_ver.sum())
    n_both_sen = int(has_both_sen.sum())
    logger.info(f"两位编码者均有【验证】判定的样本数: {n_both_ver}")
    logger.info(f"两位编码者均有【情感】判定的样本数: {n_both_sen}")

    # 先将 gold_sen_col 初始化为 None，防止后续分支遗漏赋值导致 UnboundLocalError
    gold_sen_col = None

    # 黄金标准（验证）
    if final_ver in df_verify.columns and df_verify[final_ver].notna().sum() > 0:
        gold_ver_col = final_ver
    elif coder_a_ver in df_verify.columns and df_verify[coder_a_ver].notna().sum() > 0:
        gold_ver_col = coder_a_ver
    else:
        logger.info("验证黄金标准缺失，切换至模拟模式")
        df_verify = _generate_demo_data()
        demo_mode = True
        has_both_ver = df_verify['编码者A_验证'].notna() & df_verify['编码者B_验证'].notna()
        n_both_ver = int(has_both_ver.sum())
        gold_ver_col = '最终_验证'
        gold_sen_col = '最终_情感'

    # 黄金标准（情感）：demo_mode 时若 else 分支已赋值则跳过；否则从真实数据中判断
    if demo_mode and gold_sen_col is None:
        # demo_mode=True 但是 else 分支未执行（模拟数据列存在），直接指向模拟情感列
        gold_sen_col = '最终_情感'
    elif not demo_mode:
        if final_sen in df_verify.columns and df_verify[final_sen].notna().sum() > 0:
            gold_sen_col = final_sen
        elif coder_a_sen in df_verify.columns and df_verify[coder_a_sen].notna().sum() > 0:
            gold_sen_col = coder_a_sen
        else:
            gold_sen_col = None

    has_gold_ver = df_verify[gold_ver_col].notna()
    n_gold_ver = int(has_gold_ver.sum())
    logger.info(f"有【验证】黄金标准的样本数: {n_gold_ver}")

    if n_gold_ver == 0:
        logger.error("黄金标准样本数为 0，无法评估。请先完成人工编码。")
        return

    results = {
        'demo_mode': demo_mode,
        'n_samples': len(df_verify),
        'n_gold_ver': n_gold_ver,
        'inter_coder_reliability': {
            'verification': {},
            'sentiment': {}
            # Plan v1.37 P0 §3.3.2 R27B-02: ICR stays at 2 keys.
            # 32_human_samples.xlsx uses 2-rater (coder_A/coder_B) suited
            # to Cohen κ. manual_validation_samples.xlsx uses 3-rater
            # majority-voted into a single gold column (per-rater data
            # merged away). Innovation reliability is reported separately
            # via the manual-validation-study-plan κ/α workstream.
        },
        'classifier_metrics': {
            'verification': {},
            'sentiment': {},
            # Plan v1.37 P0 §3.3.2: 4-task extension for Panels E (substantiveness) + F (locus).
            'innovation_substantiveness': {},
            'innovation_locus': {},
        },
        'mcnemar_test': {},
        # Plan v1.37 P0 §3.3.1 pending semantics
        'innovation_pending_reason': None,
    }

    # ======================================================================
    # Step 3: 编码者间一致性 (ICR)
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    编码者间一致性分析 (ICR)    ===")
    logger.info("=" * 70)

    # 3.1 验证任务 ICR
    if n_both_ver > 0:
        df_both = df_verify[has_both_ver]
        rater1 = df_both['编码者A_验证'].astype(int).values
        rater2 = df_both['编码者B_验证'].astype(int).values

        kappa_result = compute_cohens_kappa(rater1, rater2)
        results['inter_coder_reliability']['verification'].update({'cohens_kappa': kappa_result})
        logger.info(f"[验证] Cohen's Kappa: {kappa_result['kappa']:.4f}")

        # Krippendorff's Alpha
        ratings_matrix = np.stack([rater1, rater2], axis=0)
        alpha = compute_krippendorffs_alpha(ratings_matrix)
        results['inter_coder_reliability']['verification'].update({'krippendorffs_alpha': alpha})
        logger.info(f"[验证] Krippendorff's Alpha: {alpha:.4f}")

    # 3.2 情感任务 ICR (需要将字符串映射为 int，剔除空值)
    if demo_mode or n_both_sen > 0:
        if demo_mode:
            df_both_sen = df_verify.copy()
        else:
            df_both_sen = df_verify[has_both_sen].copy()
        
        # 定义映射：正面:2, 中性:1, 负面:0
        sen_map = {'正面': 2, '中性': 1, '负面': 0}
        
        rater1_sen = df_both_sen['编码者A_情感'].map(sen_map).fillna(-1).astype(int).values
        rater2_sen = df_both_sen['编码者B_情感'].map(sen_map).fillna(-1).astype(int).values
        
        # 过滤掉映射失败的记录 (-1)
        valid_mask_sen = (rater1_sen >= 0) & (rater2_sen >= 0)
        rater1_sen_valid = rater1_sen[valid_mask_sen]
        rater2_sen_valid = rater2_sen[valid_mask_sen]
        
        if len(rater1_sen_valid) > 0:
            kappa_result_sen = compute_cohens_kappa(rater1_sen_valid, rater2_sen_valid)
            results['inter_coder_reliability']['sentiment'].update({'cohens_kappa': kappa_result_sen})
            logger.info(f"[情感] Cohen's Kappa: {kappa_result_sen['kappa']:.4f}")

            ratings_matrix_sen = np.stack([rater1_sen_valid, rater2_sen_valid], axis=0)
            alpha_sen = compute_krippendorffs_alpha(ratings_matrix_sen)
            results['inter_coder_reliability']['sentiment'].update({'krippendorffs_alpha': alpha_sen})
            logger.info(f"[情感] Krippendorff's Alpha: {alpha_sen:.4f}")

    # ======================================================================
    # Step 4: 分类器性能评估
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    分类器性能评估    ===")
    logger.info("=" * 70)

    # 4.1 === 验证任务评估 ===
    logger.info(">>> 评估任务一：真伪验证")
    df_eval_ver = df_verify[has_gold_ver].copy()
    y_gold_ver = df_eval_ver[gold_ver_col].astype(int).values

    # 规则分类器（全是候选集，故全部预测为 1）
    y_pred_rule = np.ones(len(y_gold_ver), dtype=int)
    rule_metrics = compute_classification_metrics(y_gold_ver, y_pred_rule, labels=[0, 1])
    results['classifier_metrics']['verification'].update({'规则分类器 (Rule-Based)': rule_metrics})

    logger.info("  规则分类器:")
    logger.info(f"    Macro F1:  {rule_metrics['macro']['f1']:.4f}")
    logger.info(f"    Accuracy:  {rule_metrics['accuracy']:.4f}")

    # LLM 分类器（双轨对比）
    y_pred_llm_tracks = {}
    for track in ['_full', '_ctx']:
        ver_col = f'llm_verified{track}'
        if ver_col in df_eval_ver.columns:
            y_pred_llm = df_eval_ver[ver_col].fillna(False).astype(int).values
            y_pred_llm_tracks[track] = y_pred_llm
            llm_metrics = compute_classification_metrics(y_gold_ver, y_pred_llm, labels=[0, 1])
            results['classifier_metrics']['verification'][f'LLM 验证 ({track})'] = llm_metrics

            logger.info(f"  LLM 语义精筛 [{track}]:")
            logger.info(f"    Macro Precision: {llm_metrics['macro']['precision']:.4f}")
            logger.info(f"    Macro Recall:    {llm_metrics['macro']['recall']:.4f}")
            logger.info(f"    Macro F1:  {llm_metrics['macro']['f1']:.4f}")
            logger.info(f"    Accuracy:  {llm_metrics['accuracy']:.4f}")

            save_confusion_matrix_plot(
                llm_metrics, f'LLM 语义精筛验证 {track}',
                os.path.join(output_dir, f'cm_verification_llm{track}.png'), logger
            )

    # McNemar: 规则 vs LLM_full
    if '_full' in y_pred_llm_tracks:
        mcnemar = compute_mcnemar_test(y_gold_ver, y_pred_rule, y_pred_llm_tracks['_full'])
        results['mcnemar_rule_vs_llm_full'] = mcnemar
        logger.info(f"  McNemar (规则 vs LLM_full) p值: {mcnemar['p_value']:.6f}  {'显著' if mcnemar['significant'] else '不显著'}")

    # McNemar: full vs ctx
    if '_full' in y_pred_llm_tracks and '_ctx' in y_pred_llm_tracks:
        mcnemar_fc = compute_mcnemar_test(y_gold_ver, y_pred_llm_tracks['_full'], y_pred_llm_tracks['_ctx'])
        results['mcnemar_full_vs_ctx'] = mcnemar_fc
        logger.info(f"  McNemar (full vs ctx) p值: {mcnemar_fc['p_value']:.6f}  {'显著' if mcnemar_fc['significant'] else '不显著'}")
        
    # 4.1b === 各 LLM 模型独立验证评估 ===
    logger.info(">>> 评估各 LLM 模型独立验证性能")
    llm_config = CONFIG.get('tone_llm_processing', {})
    model_list = llm_config.get('models', [])
    per_model_ver_results = {}
    
    for m in model_list:
        short = m.get('short_name', '')
        for track in ['_full', '_ctx']:
            col_name = f"{short}_verified{track}"
            if col_name in df_eval_ver.columns:
                y_pred_model = df_eval_ver[col_name].fillna(False)
                if y_pred_model.dtype == object:
                    y_pred_model = y_pred_model.map(
                        lambda x: 1 if str(x).strip().lower() in ('true', '1', 'yes') else 0
                    ).astype(int).values
                else:
                    y_pred_model = y_pred_model.astype(int).values
                
                model_metrics = compute_classification_metrics(y_gold_ver, y_pred_model, labels=[0, 1])
                per_model_ver_results[f"{short}{track}"] = model_metrics
                results['classifier_metrics']['verification'][f"{short}{track} (独立)"] = model_metrics
                
                logger.info(f"  {short}{track} 独立验证:")
                logger.info(f"    Precision: {model_metrics['macro']['precision']:.4f}")
                logger.info(f"    Recall:    {model_metrics['macro']['recall']:.4f}")
                logger.info(f"    F1:        {model_metrics['macro']['f1']:.4f}")
                logger.info(f"    Accuracy:  {model_metrics['accuracy']:.4f}")
            else:
                logger.info(f"  {short}{track}: 列 {col_name} 不存在，跳过")
    
    if per_model_ver_results:
        comparison_rows = []
        for model_name, metrics in per_model_ver_results.items():
            comparison_rows.append({
                '模型': model_name,
                'Precision': metrics['macro']['precision'],
                'Recall': metrics['macro']['recall'],
                'F1-Score': metrics['macro']['f1'],
                'Accuracy': metrics['accuracy'],
            })
        comp_df = pd.DataFrame(comparison_rows)
        comp_path = os.path.join(output_dir, 'per_model_verification_comparison.csv')
        comp_df.to_csv(comp_path, index=False, encoding='utf-8-sig')
        logger.info(f"  模型间验证对比 CSV 已保存: {comp_path}")

    # 4.2 === 情感任务评估 ===
    logger.info(">>> 评估任务二：情感分类")
    if gold_sen_col is not None:
        has_gold_sen = df_verify[gold_sen_col].notna() & (df_verify[gold_sen_col] != '')
        df_eval_sen = df_verify[has_gold_sen].copy()
        y_gold_sen = df_eval_sen[gold_sen_col].values
        
        labels_sen = ['正面', '中性', '负面']
        
        # LLM 情感评估（双轨对比）
        for track in ['_full', '_ctx']:
            sen_col = f'llm_sentiment{track}'
            if sen_col in df_eval_sen.columns:
                y_pred_llm_sen = df_eval_sen[sen_col].fillna('中性').astype(str).values
                y_pred_llm_sen = np.where(np.isin(y_pred_llm_sen, labels_sen), y_pred_llm_sen, '中性')
                
                llm_sen_metrics = compute_classification_metrics(y_gold_sen, y_pred_llm_sen, labels=labels_sen)
                results['classifier_metrics']['sentiment'][f'LLM 情感分析 ({track})'] = llm_sen_metrics
                
                logger.info(f"  LLM 情感分析 [{track}]:")
                logger.info(f"    Macro Precision: {llm_sen_metrics['macro']['precision']:.4f}")
                logger.info(f"    Macro Recall:    {llm_sen_metrics['macro']['recall']:.4f}")
                logger.info(f"    Macro F1:  {llm_sen_metrics['macro']['f1']:.4f}")
                logger.info(f"    Accuracy:  {llm_sen_metrics['accuracy']:.4f}")
                # 逐类别 Recall（cf. FinBERT Table 1 Panel A: Per-class Recall）
                per_class = llm_sen_metrics.get('per_class', {})
                if per_class:
                    logger.info(f"    --- 逐类别指标 (Per-class) ---")
                    for cls_label in labels_sen:
                        cls_m = per_class.get(str(cls_label), {})
                        support = cls_m.get('support', 0)
                        logger.info(
                            f"    {cls_label:　<3s}: "
                            f"Precision={cls_m.get('precision', 0):.4f}  "
                            f"Recall={cls_m.get('recall', 0):.4f}  "
                            f"F1={cls_m.get('f1', 0):.4f}  "
                            f"(n={support})"
                        )
                
                save_confusion_matrix_plot(
                    llm_sen_metrics, f'LLM 情感分析 {track}',
                    os.path.join(output_dir, f'cm_sentiment_llm{track}.png'), logger
                )
        
        # 4.2b === 各 LLM 模型独立情感评估 ===
        logger.info(">>> 评估各 LLM 模型独立情感性能")
        per_model_sen_results = {}
        for m_cfg in model_list:
            short = m_cfg.get('short_name', '')
            for track in ['_full', '_ctx']:
                col_name = f"{short}_sentiment{track}"
                if col_name in df_eval_sen.columns:
                    y_pred_model_sen = df_eval_sen[col_name].fillna('中性').astype(str).values
                    y_pred_model_sen = np.where(np.isin(y_pred_model_sen, labels_sen), y_pred_model_sen, '中性')
                    model_sen_metrics = compute_classification_metrics(y_gold_sen, y_pred_model_sen, labels=labels_sen)
                    per_model_sen_results[f"{short}{track}"] = model_sen_metrics
                    results['classifier_metrics']['sentiment'][f"{short}{track} (独立)"] = model_sen_metrics
                    logger.info(f"  {short}{track} 独立情感:")
                    logger.info(f"    Precision: {model_sen_metrics['macro']['precision']:.4f}")
                    logger.info(f"    Recall:    {model_sen_metrics['macro']['recall']:.4f}")
                    logger.info(f"    F1:        {model_sen_metrics['macro']['f1']:.4f}")
                    logger.info(f"    Accuracy:  {model_sen_metrics['accuracy']:.4f}")
                    # 逐类别指标
                    per_class_m = model_sen_metrics.get('per_class', {})
                    if per_class_m:
                        for cls_label in labels_sen:
                            cls_m = per_class_m.get(str(cls_label), {})
                            logger.info(
                                f"      {cls_label}: "
                                f"P={cls_m.get('precision', 0):.4f} "
                                f"R={cls_m.get('recall', 0):.4f} "
                                f"F1={cls_m.get('f1', 0):.4f} "
                                f"(n={cls_m.get('support', 0)})"
                            )
                else:
                    logger.info(f"  {short}{track}: 列 {col_name} 不存在，跳过")
        
        if per_model_sen_results:
            sen_comparison_rows = []
            for model_name, metrics in per_model_sen_results.items():
                sen_comparison_rows.append({
                    '模型': model_name,
                    'Precision': metrics['macro']['precision'],
                    'Recall': metrics['macro']['recall'],
                    'F1-Score': metrics['macro']['f1'],
                    'Accuracy': metrics['accuracy'],
                })
            sen_comp_df = pd.DataFrame(sen_comparison_rows)
            sen_comp_path = os.path.join(output_dir, 'per_model_sentiment_comparison.csv')
            sen_comp_df.to_csv(sen_comp_path, index=False, encoding='utf-8-sig')
            logger.info(f"  模型间情感对比 CSV 已保存: {sen_comp_path}")
    else:
        logger.info("  未找到有效的情感分类黄金标准。")

    # ======================================================================
    # Step 4c: Plan v1.37 P0 §3.3.1 — Panels E (substantiveness) + F (locus)
    # Innovation-dimension classifier metrics from manual_validation_samples.xlsx.
    # Code path lands regardless of annotation state; pending footnote used
    # when xlsx absent / schema mismatch / all cells NaN.
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    Step 4c: Panels E/F (innovation dimensions)    ===")
    logger.info("=" * 70)
    _evaluate_innovation_panels(results, output_dir, logger)

    # ======================================================================
    # Step 4b: 误分类系统相关性诊断 (Carlson & Burbano 2026, SMJ 47(3))
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    Step 4b: 误分类系统相关性诊断    ===")
    logger.info("===    Carlson & Burbano (2026, Strategic Management Journal, 47(3), 699-725)    ===")
    logger.info("===    检验第一阶段筛选的误分类方向是否与下游情感变量系统相关    ===")
    logger.info("=" * 70)
    for track in ['_full', '_ctx']:
        ver_col_diag = f'llm_verified{track}'
        if ver_col_diag in df_eval_ver.columns:
            bias_diag = diagnose_misclassification_bias(
                df_verify=df_eval_ver,
                gold_ver_col=gold_ver_col,
                track=track,
                logger_inst=logger,
                output_dir=output_dir,
            )
            results[f'misclassification_bias{track}'] = bias_diag
        else:
            logger.info(f"  [{track}] 列 {ver_col_diag} 不存在，跳过诊断")

    # ======================================================================
    # Step 5: 生成报告
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    生成评估报告    ===")
    logger.info("=" * 70)

    # 保存 JSON 结果
    json_path = os.path.join(output_dir, 'classification_eval_results.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"JSON 结果已保存: {json_path}")

    # 生成 LaTeX 表格
    latex_path = os.path.join(output_dir, 'classification_eval_table.tex')
    generate_latex_table(results, latex_path, logger)

    # 生成 CSV 汇总
    csv_rows = []
    
    # 汇总验证分类器
    for name, m in results.get('classifier_metrics', {}).get('verification', {}).items():
        macro = m.get('macro', {})
        csv_rows.append({
            '任务': '验证',
            '分类器': name,
            'Macro Precision': macro.get('precision', 0),
            'Macro Recall': macro.get('recall', 0),
            'Macro F1-Score': macro.get('f1', 0),
            'Accuracy': m.get('accuracy', 0)
        })
        
    # 汇总情感分类器（含逐类别 Recall）
    for name, m in results.get('classifier_metrics', {}).get('sentiment', {}).items():
        macro = m.get('macro', {})
        pc = m.get('per_class', {})
        row = {
            '任务': '情感',
            '分类器': name,
            'Macro Precision': macro.get('precision', 0),
            'Macro Recall': macro.get('recall', 0),
            'Macro F1-Score': macro.get('f1', 0),
            'Accuracy': m.get('accuracy', 0),
        }
        # 逐类别指标（Recall 为核心，附 Precision 和 F1）
        for cls_label in ['正面', '中性', '负面']:
            cls_m = pc.get(str(cls_label), {})
            row[f'{cls_label}_Precision'] = cls_m.get('precision', '')
            row[f'{cls_label}_Recall'] = cls_m.get('recall', '')
            row[f'{cls_label}_F1'] = cls_m.get('f1', '')
            row[f'{cls_label}_Support'] = cls_m.get('support', '')
        csv_rows.append(row)
        
    if csv_rows:
        csv_path = os.path.join(output_dir, 'classification_eval_summary.csv')
        pd.DataFrame(csv_rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"CSV 汇总已保存: {csv_path}")

    # ======================================================================
    # G-10: 人工验证标准化报告 (论文方法论章节所需)
    # 学术依据: Carlson & Burbano (2026, SMJ §3.4):
    #   "Authors should report: (1) sample size, (2) inter-coder reliability
    #    metrics with confidence intervals, (3) coding protocol details."
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    G-10: 标准化人工验证报告 (论文方法论章节)    ===")
    logger.info("=" * 70)

    std_report = {
        '数据模式': '模拟数据' if demo_mode else '真实数据',
        '验证样本总量 (N)': len(df_verify),
        '有效验证样本 (n_gold_ver)': n_gold_ver,
    }

    # 提取 κ 和 α
    icr_ver = results.get('inter_coder_reliability', {}).get('verification', {})
    if icr_ver:
        kappa_ver = icr_ver.get('cohens_kappa', {})
        alpha_ver = icr_ver.get('krippendorffs_alpha', None)
        std_report['验证任务_Cohens_κ'] = kappa_ver.get('kappa', 'N/A')
        std_report['验证任务_Krippendorffs_α'] = alpha_ver
        std_report['验证任务_observed_agreement'] = kappa_ver.get('observed_agreement', 'N/A')
        std_report['验证任务_n_samples'] = kappa_ver.get('n_samples', 'N/A')

        # κ 的近似 95% CI: κ ± 1.96 × SE(κ)
        # SE(κ) ≈ sqrt(p_o × (1 - p_o) / (n × (1 - p_e)²))
        kappa_val = kappa_ver.get('kappa', 0)
        p_o = kappa_ver.get('observed_agreement', 0)
        p_e = kappa_ver.get('expected_agreement', 0)
        n_s = kappa_ver.get('n_samples', 0)
        if n_s > 0 and p_e < 1:
            import math
            se_kappa = math.sqrt(p_o * (1 - p_o) / (n_s * (1 - p_e) ** 2))
            ci_low = round(kappa_val - 1.96 * se_kappa, 4)
            ci_high = round(kappa_val + 1.96 * se_kappa, 4)
            std_report['验证任务_κ_95%CI'] = f"[{ci_low}, {ci_high}]"
            logger.info(f"  验证任务: κ = {kappa_val:.4f}, 95% CI = [{ci_low:.4f}, {ci_high:.4f}]")
            logger.info(f"  验证任务: α = {alpha_ver}, N = {n_s}")

    icr_sen = results.get('inter_coder_reliability', {}).get('sentiment', {})
    if icr_sen:
        kappa_sen = icr_sen.get('cohens_kappa', {})
        alpha_sen = icr_sen.get('krippendorffs_alpha', None)
        std_report['情感任务_Cohens_κ'] = kappa_sen.get('kappa', 'N/A')
        std_report['情感任务_Krippendorffs_α'] = alpha_sen
        std_report['情感任务_n_samples'] = kappa_sen.get('n_samples', 'N/A')

        kappa_val_s = kappa_sen.get('kappa', 0)
        p_o_s = kappa_sen.get('observed_agreement', 0)
        p_e_s = kappa_sen.get('expected_agreement', 0)
        n_s_s = kappa_sen.get('n_samples', 0)
        if n_s_s > 0 and p_e_s < 1:
            se_s = math.sqrt(p_o_s * (1 - p_o_s) / (n_s_s * (1 - p_e_s) ** 2))
            ci_low_s = round(kappa_val_s - 1.96 * se_s, 4)
            ci_high_s = round(kappa_val_s + 1.96 * se_s, 4)
            std_report['情感任务_κ_95%CI'] = f"[{ci_low_s}, {ci_high_s}]"
            logger.info(f"  情感任务: κ = {kappa_val_s:.4f}, 95% CI = [{ci_low_s:.4f}, {ci_high_s:.4f}]")
            logger.info(f"  情感任务: α = {alpha_sen}, N = {n_s_s}")

    # 输出标准化报告 CSV
    std_report_path = os.path.join(output_dir, 'validation_standard_report.csv')
    pd.DataFrame([std_report]).to_csv(std_report_path, index=False, encoding='utf-8-sig')
    logger.info(f"  标准化验证报告: {std_report_path}")

    # 论文引用建议
    logger.info("")
    logger.info("  ── 论文方法论章节建议表述 ──")
    logger.info(f"  \"We randomly sampled {std_report.get('验证样本总量 (N)', 'N')} articles")
    logger.info(f"   for manual validation. Two independent coders evaluated each article")
    logger.info(f"   following a standardized protocol (Carlson & Burbano, 2026, SMJ).")
    if icr_ver:
        logger.info(f"   Inter-coder reliability for the verification task was")
        logger.info(f"   κ = {std_report.get('验证任务_Cohens_κ', 'N/A')} "
                    f"{std_report.get('验证任务_κ_95%CI', '')}, "
                    f"α = {std_report.get('验证任务_Krippendorffs_α', 'N/A')}.\"")

    results['standardized_validation_report'] = std_report

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=len(df_verify), output_rows=n_gold_ver)
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


# ============================================================================
# 6. 模拟数据生成（人工验证完成前的框架测试用）
# ============================================================================

def _generate_demo_data(n=200) -> pd.DataFrame:
    """生成包含验证和情感双重任务的模拟数据（含各模型独立列）。"""
    rng = np.random.RandomState(42)

    # 【任务一模拟】
    gold_ver = rng.binomial(1, 0.7, n)
    coder_a_ver = np.where(rng.binomial(1, 0.10, n), 1 - gold_ver, gold_ver)
    coder_b_ver = np.where(rng.binomial(1, 0.12, n), 1 - gold_ver, gold_ver)
    llm_verified = np.where(rng.binomial(1, 0.15, n), 1 - gold_ver, gold_ver).astype(bool)

    # 【任务二模拟】
    labels = ['正面', '中性', '负面']
    gold_sen_idx = rng.choice([0, 1, 2], size=n, p=[0.4, 0.4, 0.2])
    gold_sen = np.array(labels)[gold_sen_idx]
    
    # 构建包含错误的多分类偏移（如果 noise发生，在另两个标签中随机抽）
    noise_a_sen = rng.binomial(1, 0.10, n)
    coder_a_sen = []
    for i in range(n):
        if noise_a_sen[i]:
            coder_a_sen.append(rng.choice([x for x in labels if x != gold_sen[i]]))
        else:
            coder_a_sen.append(gold_sen[i])
            
    noise_b_sen = rng.binomial(1, 0.12, n)
    coder_b_sen = []
    for i in range(n):
        if noise_b_sen[i]:
            coder_b_sen.append(rng.choice([x for x in labels if x != gold_sen[i]]))
        else:
            coder_b_sen.append(gold_sen[i])

    noise_llm_sen = rng.binomial(1, 0.15, n)
    llm_sentiment = []
    for i in range(n):
        if noise_llm_sen[i]:
            llm_sentiment.append(rng.choice([x for x in labels if x != gold_sen[i]]))
        else:
            llm_sentiment.append(gold_sen[i])

    df = pd.DataFrame({
        '样本编号': range(1, n + 1),
        '标题': [f'模拟新闻标题_{i}' for i in range(1, n + 1)],
        '内容': [f'模拟新闻内容_{i}' for i in range(1, n + 1)],
        
        'llm_verified_full': llm_verified,
        'llm_verified_ctx': llm_verified,
        'llm_sentiment_full': llm_sentiment,
        'llm_sentiment_ctx': llm_sentiment,
        
        '编码者A_验证': coder_a_ver,
        '编码者A_情感': coder_a_sen,
        '编码者A_理由': '',
        
        '编码者B_验证': coder_b_ver,
        '编码者B_情感': coder_b_sen,
        '编码者B_理由': '',
        
        '最终_验证': gold_ver,
        '最终_情感': gold_sen,
        '裁定备注': '',
    })

    # 生成各模型独立列的模拟数据（双轨）
    try:
        config = load_config()
        model_list = config.get('tone_llm_processing', {}).get('models', [])
    except Exception:
        model_list = []
    
    for m in model_list:
        short = m.get('short_name', '')
        if not short:
            continue
        for track in ['_full', '_ctx']:
            # 各模型独立验证：以不同噪声率模拟（10%-20%）
            noise_rate = rng.uniform(0.10, 0.20)
            model_ver = np.where(rng.binomial(1, noise_rate, n), 1 - gold_ver, gold_ver).astype(bool)
            df[f'{short}_verified{track}'] = model_ver
            # 各模型独立情感
            model_sen = []
            noise_model = rng.binomial(1, noise_rate, n)
            for i in range(n):
                if noise_model[i]:
                    model_sen.append(rng.choice([x for x in labels if x != gold_sen[i]]))
                else:
                    model_sen.append(gold_sen[i])
            df[f'{short}_sentiment{track}'] = model_sen
            # 各模型置信度
            df[f'{short}_verification_confidence{track}'] = rng.uniform(0.6, 1.0, n).round(2)
            df[f'{short}_sentiment_confidence{track}'] = rng.uniform(0.5, 1.0, n).round(2)

    # 补充更真实的内容长度（供误分类诊断 T5 使用）
    df['内容'] = [
        '模' * rng.randint(200, 3000) for _ in range(n)
    ]

    return df


if __name__ == "__main__":
    main()
