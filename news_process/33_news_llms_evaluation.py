"""
33_news_llms_evaluation.py — 阶段33：新闻分类模型评估
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
      3. 输出 LaTeX 格式表格（可直接嵌入论文）

    学术依据：
      - Loughran & McDonald (2011, Journal of Finance)
      - Krippendorff (2018): Cohen's Kappa ≥ 0.80
      - Tetlock et al. (2008, Journal of Finance)

输入：
    阶段 03c 输出的人工验证 Excel 文件（已填写编码者判定）

输出：
    评估报告（日志 + CSV + PNG 图表 + LaTeX 表格）
"""

import os
import sys
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
STAGE_NAME = "33_news_llms_evaluation"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


# ============================================================================
# 2. 统计指标计算函数
# ============================================================================

def compute_cohens_kappa(rater1: np.ndarray, rater2: np.ndarray) -> dict:
    """计算 Cohen's Kappa 编码者间一致性系数。

    Args:
        rater1: 编码者 A 的判定数组（0/1 整型）。
        rater2: 编码者 B 的判定数组（0/1 整型）。

    Returns:
        dict: 包含 kappa, observed_agreement, expected_agreement 的字典。
    """
    assert len(rater1) == len(rater2), "两个编码者的样本数必须一致"
    n = len(rater1)

    # 观察一致率
    observed_agreement = np.sum(rater1 == rater2) / n

    # 随机一致率
    p1_yes = np.sum(rater1 == 1) / n
    p1_no = np.sum(rater1 == 0) / n
    p2_yes = np.sum(rater2 == 1) / n
    p2_no = np.sum(rater2 == 0) / n
    expected_agreement = p1_yes * p2_yes + p1_no * p2_no

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
        from sklearn.metrics import precision_recall_fscore_support, accuracy_score, confusion_matrix
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
        if set(labels) == {0, 1} or set(labels) == {'0', '1'}:
            # Ensure label 0 corresponds to the first element and 1 to the second
            idx_0 = labels.index(0) if 0 in labels else labels.index('0')
            idx_1 = labels.index(1) if 1 in labels else labels.index('1')
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
    lines.append(r"\multicolumn{5}{l}{\textbf{Panel B: Sentiment Task (Three-class)}} \\")
    for name, metrics in results.get('classifier_metrics', {}).get('sentiment', {}).items():
        macro = metrics.get('macro', {})
        lines.append(
            f"  {name} & {macro.get('precision', 0):.3f} & "
            f"{macro.get('recall', 0):.3f} & {macro.get('f1', 0):.3f} & "
            f"{metrics.get('accuracy', 0):.3f} \\\\"
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
# 5. 主函数
# ============================================================================

def main():
    """分类有效性评估主入口。"""
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
        logger.warning(
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
        logger.warning("验证黄金标准缺失，切换至模拟模式")
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
        },
        'classifier_metrics': {
            'verification': {},
            'sentiment': {}
        },
        'mcnemar_test': {},
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

    # LLM 分类器
    if 'llm_verified' in df_eval_ver.columns:
        y_pred_llm = df_eval_ver['llm_verified'].fillna(False).astype(int).values
        llm_metrics = compute_classification_metrics(y_gold_ver, y_pred_llm, labels=[0, 1])
        results['classifier_metrics']['verification'].update({'LLM 验证 (LLM-Verified)': llm_metrics})

        logger.info("  LLM 语义精筛:")
        logger.info(f"    Macro Precision: {llm_metrics['macro']['precision']:.4f}")
        logger.info(f"    Macro Recall:    {llm_metrics['macro']['recall']:.4f}")
        logger.info(f"    Macro F1:  {llm_metrics['macro']['f1']:.4f}")
        logger.info(f"    Accuracy:  {llm_metrics['accuracy']:.4f}")

        save_confusion_matrix_plot(
            llm_metrics, 'LLM 语义精筛验证',
            os.path.join(output_dir, 'cm_verification_llm.png'), logger
        )

        mcnemar = compute_mcnemar_test(y_gold_ver, y_pred_rule, y_pred_llm)
        results.update({'mcnemar_test': mcnemar})
        logger.info(f"  McNemar p值: {mcnemar['p_value']:.6f}  {'显著' if mcnemar['significant'] else '不显著'}")
        
    # 4.1b === 各 LLM 模型独立验证评估 ===
    logger.info(">>> 评估各 LLM 模型独立验证性能")
    llm_config = CONFIG.get('tone_llm_processing', {})
    model_list = llm_config.get('models', [])
    per_model_ver_results = {}
    
    for m in model_list:
        short = m.get('short_name', '')
        col_name = f"{short}_verified"
        if col_name in df_eval_ver.columns:
            y_pred_model = df_eval_ver[col_name].fillna(False)
            if y_pred_model.dtype == object:
                y_pred_model = y_pred_model.map(
                    lambda x: 1 if str(x).strip().lower() in ('true', '1', 'yes') else 0
                ).astype(int).values
            else:
                y_pred_model = y_pred_model.astype(int).values
            
            model_metrics = compute_classification_metrics(y_gold_ver, y_pred_model, labels=[0, 1])
            per_model_ver_results[short] = model_metrics
            results['classifier_metrics']['verification'][f"{short} (独立)"] = model_metrics
            
            logger.info(f"  {short} 独立验证:")
            logger.info(f"    Precision: {model_metrics['macro']['precision']:.4f}")
            logger.info(f"    Recall:    {model_metrics['macro']['recall']:.4f}")
            logger.info(f"    F1:        {model_metrics['macro']['f1']:.4f}")
            logger.info(f"    Accuracy:  {model_metrics['accuracy']:.4f}")
        else:
            logger.info(f"  {short}: 列 {col_name} 不存在，跳过")
    
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
        
        # LLM 情感评估
        if 'llm_sentiment' in df_eval_sen.columns:
            y_pred_llm_sen = df_eval_sen['llm_sentiment'].fillna('中性').astype(str).values
            # 补齐未见过的分类到中性以防万一
            y_pred_llm_sen = np.where(np.isin(y_pred_llm_sen, labels_sen), y_pred_llm_sen, '中性')
            
            llm_sen_metrics = compute_classification_metrics(y_gold_sen, y_pred_llm_sen, labels=labels_sen)
            results['classifier_metrics']['sentiment'].update({'LLM 情感分析 (LLM-Tone)': llm_sen_metrics})
            
            logger.info("  LLM 情感分析:")
            logger.info(f"    Macro Precision: {llm_sen_metrics['macro']['precision']:.4f}")
            logger.info(f"    Macro Recall:    {llm_sen_metrics['macro']['recall']:.4f}")
            logger.info(f"    Macro F1:  {llm_sen_metrics['macro']['f1']:.4f}")
            logger.info(f"    Accuracy:  {llm_sen_metrics['accuracy']:.4f}")
            
            save_confusion_matrix_plot(
                llm_sen_metrics, 'LLM 情感分析',
                os.path.join(output_dir, 'cm_sentiment_llm.png'), logger
            )
        
        # 4.2b === 各 LLM 模型独立情感评估 ===
        logger.info(">>> 评估各 LLM 模型独立情感性能")
        per_model_sen_results = {}
        for m_cfg in model_list:
            short = m_cfg.get('short_name', '')
            col_name = f"{short}_sentiment"
            if col_name in df_eval_sen.columns:
                y_pred_model_sen = df_eval_sen[col_name].fillna('中性').astype(str).values
                y_pred_model_sen = np.where(np.isin(y_pred_model_sen, labels_sen), y_pred_model_sen, '中性')
                model_sen_metrics = compute_classification_metrics(y_gold_sen, y_pred_model_sen, labels=labels_sen)
                per_model_sen_results[short] = model_sen_metrics
                results['classifier_metrics']['sentiment'][f"{short} (独立)"] = model_sen_metrics
                logger.info(f"  {short} 独立情感:")
                logger.info(f"    Precision: {model_sen_metrics['macro']['precision']:.4f}")
                logger.info(f"    Recall:    {model_sen_metrics['macro']['recall']:.4f}")
                logger.info(f"    F1:        {model_sen_metrics['macro']['f1']:.4f}")
                logger.info(f"    Accuracy:  {model_sen_metrics['accuracy']:.4f}")
            else:
                logger.info(f"  {short}: 列 {col_name} 不存在，跳过")
        
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
        
    # 汇总情感分类器
    for name, m in results.get('classifier_metrics', {}).get('sentiment', {}).items():
        macro = m.get('macro', {})
        csv_rows.append({
            '任务': '情感',
            '分类器': name,
            'Macro Precision': macro.get('precision', 0),
            'Macro Recall': macro.get('recall', 0),
            'Macro F1-Score': macro.get('f1', 0),
            'Accuracy': m.get('accuracy', 0)
        })
        
    if csv_rows:
        csv_path = os.path.join(output_dir, 'classification_eval_summary.csv')
        pd.DataFrame(csv_rows).to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"CSV 汇总已保存: {csv_path}")

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
        
        'llm_verified': llm_verified,
        'llm_sentiment': llm_sentiment,
        
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

    # 生成各模型独立列的模拟数据（用于 P1-5 各模型独立评估）
    try:
        config = load_config()
        model_list = config.get('tone_llm_processing', {}).get('models', [])
    except Exception:
        model_list = []
    
    for m in model_list:
        short = m.get('short_name', '')
        if not short:
            continue
        # 各模型独立验证：以不同噪声率模拟（10%-20%）
        noise_rate = rng.uniform(0.10, 0.20)
        model_ver = np.where(rng.binomial(1, noise_rate, n), 1 - gold_ver, gold_ver).astype(bool)
        df[f'{short}_verified'] = model_ver
        # 各模型独立情感
        model_sen = []
        noise_model = rng.binomial(1, noise_rate, n)
        for i in range(n):
            if noise_model[i]:
                model_sen.append(rng.choice([x for x in labels if x != gold_sen[i]]))
            else:
                model_sen.append(gold_sen[i])
        df[f'{short}_sentiment'] = model_sen
        # 各模型置信度
        df[f'{short}_verification_confidence'] = rng.uniform(0.6, 1.0, n).round(2)
        df[f'{short}_sentiment_confidence'] = rng.uniform(0.5, 1.0, n).round(2)

    return df


if __name__ == "__main__":
    main()
