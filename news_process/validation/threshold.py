"""
news_process.validation.threshold — 阶段31：分类阈值敏感性分析

迁移说明 (Phase 7b)：
    本模块由原 root script ``60_bank_fintech_threshold.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.threshold``

==========================================================

功能：
    对银行新闻分类和金融科技新闻分类的核心阈值参数进行系统性敏感性分析，
    以验证当前阈值选择的稳健性并确定最优阈值区间。

    分析内容：
      1. 银行新闻分类阈值
         - min_name_occurrences: 网格搜索 1~10
         - 在不同阈值下统计分类数量变化
         - 若有人工验证数据，计算 Precision/Recall/F1 曲线
      2. 金融科技新闻分类阈值
         - min_distinct_keywords: 网格搜索 1~10
         - 在不同阈值下统计分类数量变化
         - 若有人工验证数据，计算 Precision/Recall/F1 曲线
      3. 输出
         - 阈值-样本量变化表（CSV + LaTeX）
         - Precision-Recall 权衡曲线（PNG，若有验证数据）
         - 最优阈值建议

    学术依据：
      - Loughran & McDonald (2011): 分类系统的关键参数应做敏感性分析
      - Gentzkow et al. (2019): 文本分析的全部人为选择（如阈值）须报告稳健性

输入：
    阶段 00 的 Parquet 文件以及银行名称/金融科技关键词配置文件

输出：
    敏感性分析报告（CSV + PNG + LaTeX）

注意：
    本脚本独立于主分类流程，不修改任何中间数据文件。
    它读取阶段 00 的原始输出，用不同阈值"模拟"阶段 11/12，
    从而评估阈值对最终样本量的影响。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 60_bank_fintech_threshold.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**位置与角色**: 验证流水线诊断阶段, 不修改任何主链中间数据。shim (60_bank_fintech_threshold.py) 仅 `sys.path` 注入后 `from news_process.validation.threshold import main; main()`。

**输入**: `data/processed/00_preprocessing.parquet` (CONFIG['filenames']['output_00_preprocessing']; 人民日报+Wisers 全量预处理语料), 取 `内容`/`标题` 两列。为提速做抽样: `sample_n = min(sample_max=10000, max(1000, int(总行数×sample_fraction=0.10)))`, `random_state=42`; 抽样量 ≥ 总行数时改全量。

**处理步骤**:
1. 银行分类阈值扫描 — 复用与 stage 11 完全一致的匹配逻辑 (`core/text/ahocorasick.analyze_bank_matches`, 含否定模式 `negation_ac` + 短名歧义消解 `short_name_exclusions` + `context_window`)。先 `_precompute_bank_matches` 一次遍历预计算每篇 upper/lower/title 命中计数, 再对 `min_name_occurrences ∈ threshold_range (默认 1..10)` 网格用 `simulate_bank_classification_from_precomputed` 快速过滤。
2. 金融科技分类阈值扫描 — `_precompute_fintech_matches` (Aho-Corasick `fintech_ac.iter` 上/下半区+标题命中) + `simulate_fintech_classification_vectorized` 对 `min_distinct_keywords ∈ 1..10` 网格过滤。

**关键算法/公式**: 银行判正 = `total (=total_with_title) >= threshold` 且 (`cond_a`: upper>=min_upper 且 lower>=min_lower; 或 `cond_b`: 标题命中 且 正文 (upper+lower)>=min_upper)。注意 fix(omni-extra-threshold-condb, 2026-06-11): cond_b 比较基数从含标题的 total_with_title 改为正文 (upper+lower), 对齐生产 analyze_bank_matches; 前置 `total>=threshold` 仍用 total_with_title (与生产 meets_occurrence 一致, 勿改)。每个阈值算 count / ratio(%) / estimated_total (=int(count/sample_n×total_rows) 按抽样比例外推全量) / is_current。'拐点'建议 = `np.argmin(相邻 count 差分 diffs)` 找样本量下降最剧烈点 (报告 diffs argmin 的右侧阈值)。

**输出列/产物**: CSV 列 = threshold / count / ratio / estimated_total / is_current; 另出双面板 (Panel A 银行 / Panel B 金科, 含 Δ Count) LaTeX 表 + 双子图 PNG (左=样本量柱状, 右=保留率曲线)。

**外部依赖**: 无 LLM/Embedding/BERT; 仅 matplotlib (缺失则 ImportError 捕获后跳图)、pyahocorasick (经 core/text/ahocorasick)。无超时配置 (StageSpec 未设 timeout), 无 _llm_cache.db 锚点。确定性: 抽样 seed 固定=42, 算法纯计数, 完全确定。

**学术依据 (模块 docstring)**: Loughran & McDonald (2011, JF) 阈值稳健性范式; Gentzkow, Kelly & Taddy (2019, JEL) 文本分析人为选择须报告稳健性。

■ 白话说明

**这一步在做什么**: 想象你用'文章里出现某银行名字几次'来判定'这是不是这家银行的新闻'。'几次'这个门槛是人为定的 (现在银行用2次、金融科技新闻用2个不同关键词)。这一步就是把门槛从1一直试到10, 每个门槛下数一数还剩多少篇新闻被判为'是', 画成曲线。

**为什么需要它**: 审稿人会问'你为什么挑2而不是1或3? 是不是凑出来的好看结果?'。这一步用证据回答: 如果门槛在2附近上下挪一点, 入选新闻数几乎不变 (处在平坦区), 就说明结论稳, 不是挑出来的; 如果一挪就剧烈变化, 就得谨慎。

**对面板和论文的影响**: 它本身不改任何数据, 只生成附录里的稳健性表格和图。它影响的是'可信度'而非数字 — 让最终银行-年度面板里'哪些新闻算数'这个最底层的过滤决策站得住脚。门槛选得稳, 后续所有情感、注意力指标的样本基础就稳; 选得不稳, 整篇论文的样本都可能被质疑。
========================================================================
"""

import os
import platform
import sys
import time

import numpy as np
import pandas as pd

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/threshold.py 出发, 上溯 2 层抵达项目父目录)
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
from news_process.core.plotting import configure_matplotlib_chinese_fonts
from news_process.core.text.ahocorasick import (
    analyze_bank_matches,
    load_bank_names,
    load_exclusion_patterns,
    load_fintech_dict,
)

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "60_bank_fintech_threshold"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# ── 经核验参考文献 (逐字照抄 APA-7 + DOI; 仅运行期日志用, DOI 见 pool.json) ──
# 把模块 docstring 已声明的方法学锚点 emit 进 .log, 让阈值敏感性扫描自证依据,
# 而非仅停留在源码注释 (镜像 pipeline/panel/geography.py 的 📖 运行期引文范式)。
_REFERENCES = {
    # 白话: "文本分类里所有人为选定的门槛 (如出现几次算数) 都必须做稳健性并报告" —
    # 这正是本阶段把 min_name_occurrences / min_distinct_keywords 从 1 扫到 10 的依据。
    "gentzkow_text_as_data": (
        "Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. "
        "Journal of Economic Literature, 57(3), 535-574. "
        "https://doi.org/10.1257/jel.20181020"
    ),
    # 白话: 用"词典关键词计数过门槛"来判定文本类别的经典范式 (10-K 文本分析) —
    # 金融科技轨用 1506 词金科词典数 distinct 命中过阈, 与此同源。
    "loughran_mcdonald_dict": (
        "Loughran, T., & McDonald, B. (2011). When is a liability not a "
        "liability? Textual analysis, dictionaries, and 10-Ks. The Journal "
        "of Finance, 66(1), 35-65. "
        "https://doi.org/10.1111/j.1540-6261.2010.01625.x"
    ),
}


# ============================================================================
# 2. 银行名称匹配核心逻辑（委托至 utils.aho_corasick 共享模块）
# ============================================================================
# 现已使用与 11_news_bank.py 完全一致的匹配逻辑（含否定模式排除和短名歧义消解）


def _precompute_bank_matches(df: pd.DataFrame,
                              bank_ac,
                              banks_list: list,
                              split_ratio: float,
                              negation_ac=None,
                              short_name_exclusions: dict = None,
                              context_window: int = 5) -> list[dict]:
    """预计算每篇文章的银行匹配数据（一次遍历）。

    使用 utils.aho_corasick.analyze_bank_matches 进行完整匹配（含否定模式），
    再对不同阈值在预计算结果上快速过滤。
    """
    article_matches = []
    contents = df['内容'].fillna('').astype(str).tolist()
    titles = df['标题'].fillna('').astype(str).tolist()
    for text, title in zip(contents, titles):
        result = analyze_bank_matches(
            content=text,
            title=title,
            bank_ac=bank_ac,
            banks_list=banks_list,
            split_ratio=split_ratio,
            negation_ac=negation_ac,
            short_name_exclusions=short_name_exclusions,
            context_window=context_window,
            min_name_occurrences=1,  # 设为最小值，允许后续阈值搜索
            min_upper=1,
            min_lower=0,
        )

        bank_counts = {}
        for bank_info in result['matched_banks']:
            bank_name = bank_info['bank_name']
            bank_counts[bank_name] = {
                'total': bank_info['total_with_title'],
                'upper': bank_info['upper_count'],
                'lower': bank_info['lower_count'],
                'title': 1 if bank_info['in_title'] else 0,
            }

        article_matches.append({'bank_counts': bank_counts})

    return article_matches


def simulate_bank_classification_from_precomputed(article_matches: list,
                                                   min_upper: int,
                                                   min_lower: int,
                                                   threshold: int) -> int:
    """对预计算的银行匹配数据进行阈值过滤，返回分类为正的数量。

    fix(omni-extra-threshold-condb, 2026-06-11): 路径 B (cond_b) 的比较基数由
    total_with_title 改为正文 total (upper+lower), 对齐生产 analyze_bank_matches。
    """
    count = 0
    for m in article_matches:
        for bank_name, counts in m['bank_counts'].items():
            if counts['total'] >= threshold:
                cond_a = counts['upper'] >= min_upper and counts['lower'] >= min_lower
                # fix(omni-extra-threshold-condb, 2026-06-11): 路径 B 对齐生产逻辑
                # analyze_bank_matches (core/text/ahocorasick.py:414-417) — 比较基数
                # 用 **正文** total (upper+lower), 而非含标题的 total_with_title。
                # 旧实现 counts['total'] (= total_with_title) 使标题-only 提及
                # (正文 0 次) 也能踩线达标, 敏感性网格低阈值端正例数虚高。
                # 前置条件 counts['total'] >= threshold 仍用 total_with_title,
                # 与生产 meets_occurrence 口径一致, 勿一并改动。
                cond_b = (counts['title'] > 0
                          and (counts['upper'] + counts['lower']) >= min_upper)
                if cond_a or cond_b:
                    count += 1
                    break
    return count


# ============================================================================
# 3. 金融科技关键词匹配核心逻辑（委托至 utils.aho_corasick 共享模块）
# ============================================================================

def _precompute_fintech_matches(df: pd.DataFrame,
                                  ac_automaton,
                                  split_ratio: float) -> list:
    """预计算每篇文章的金融科技关键词匹配数据（一次遍历）。"""
    article_matches = []
    contents = df['内容'].fillna('').astype(str).tolist()
    titles = df['标题'].fillna('').astype(str).tolist()
    for text, title in zip(contents, titles):

        if not text and not title:
            article_matches.append({
                'distinct_count': 0, 'upper_total': 0,
                'lower_total': 0, 'grand_total': 0, 'any_in_title': False
            })
            continue

        mid = int(len(text) * split_ratio)
        # fix(log-reaudit-2026-06-20 #1): 单遍扫【全文】后按匹配【起始位置】归入 upper/lower,
        # 取代旧的物理切片 (text[:mid] / text[mid:] 各扫一遍) —— 旧法会漏掉横跨 mid 的关键词
        # (在 upper_text 被截断、在 lower_text 又起始于切点之后), 与生产 analyze_fintech_matches
        # 已修复的 omni-g-entity-07/11 "跨切分点关键词无声丢失" 同源。单遍全文扫无边界丢失。
        kw_stats = {}
        for end_pos, kw in ac_automaton.iter(text):
            kw_stats.setdefault(kw, {'upper': 0, 'lower': 0, 'in_title': False})
            start_pos = end_pos - len(kw) + 1
            if start_pos < mid:
                kw_stats[kw]['upper'] += 1
            else:
                kw_stats[kw]['lower'] += 1
        if title:
            for end_pos, kw in ac_automaton.iter(title):
                kw_stats.setdefault(kw, {'upper': 0, 'lower': 0, 'in_title': False})
                kw_stats[kw]['in_title'] = True

        grand_upper = sum(s['upper'] for s in kw_stats.values())
        grand_lower = sum(s['lower'] for s in kw_stats.values())
        any_in_title = any(s['in_title'] for s in kw_stats.values())
        distinct = sum(1 for kw, s in kw_stats.items()
                       if (s['upper'] + s['lower'] > 0) or s['in_title'])

        article_matches.append({
            'distinct_count': distinct,
            'upper_total': grand_upper,
            'lower_total': grand_lower,
            'grand_total': grand_upper + grand_lower,
            'any_in_title': any_in_title,
        })

    return article_matches


def simulate_fintech_classification_vectorized(article_matches: list,
                                                min_upper: int,
                                                min_lower: int,
                                                threshold: int) -> int:
    """对预计算的匹配数据进行阈值过滤（向量化），返回分类为正的数量。

    分类逻辑与 12_news_fintech.py 保持一致：
      ① 前置条件：distinct_count >= threshold
      ② 分布条件（满足任一）：上下半各达标，或标题有且全文合计达标

    Args:
        article_matches: _precompute_fintech_matches 的返回值。
        min_upper:       上半区最低出现次数。
        min_lower:       下半区最低出现次数。
        threshold:       min_distinct_keywords 阈值。

    Returns:
        int: 被分类为金融科技新闻的文章数。
    """
    count = 0
    for m in article_matches:
        if m['distinct_count'] >= threshold:
            cond_a = m['upper_total'] >= min_upper and m['lower_total'] >= min_lower
            cond_b = m['any_in_title'] and m['grand_total'] >= min_upper
            if cond_a or cond_b:
                count += 1
    return count


# ============================================================================
# 4. Precision-Recall 曲线绘制
# ============================================================================

def _plot_threshold_sensitivity(threshold_results: list, param_name: str,
                                classifier_name: str, output_path: str,
                                logger_inst):
    """绘制阈值敏感性分析图。

    Args:
        threshold_results: [{threshold, count, ratio, ...}, ...]
        param_name:        参数名称。
        classifier_name:   分类器名称。
        output_path:       PNG 文件路径。
        logger_inst:       日志记录器。
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        configure_matplotlib_chinese_fonts()

        thresholds = [r['threshold'] for r in threshold_results]
        counts = [r['count'] for r in threshold_results]
        ratios = [r['ratio'] for r in threshold_results]

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # 左图：样本量变化
        ax1.bar(thresholds, counts, color='steelblue', alpha=0.8, edgecolor='navy')
        ax1.set_xlabel(param_name, fontsize=12)
        ax1.set_ylabel("分类为正的样本数", fontsize=12)
        ax1.set_title(f"{classifier_name}：阈值 vs 样本量", fontsize=13)
        ax1.set_xticks(thresholds)
        for i, (t, c) in enumerate(zip(thresholds, counts)):
            ax1.text(t, c + max(counts) * 0.02, f'{c:,}',
                     ha='center', va='bottom', fontsize=8)

        # 右图：保留率变化
        ax2.plot(thresholds, ratios, 'o-', color='darkorange', linewidth=2,
                 markersize=6)
        ax2.set_xlabel(param_name, fontsize=12)
        ax2.set_ylabel("保留率 (%)", fontsize=12)
        ax2.set_title(f"{classifier_name}：阈值 vs 保留率", fontsize=13)
        ax2.set_xticks(thresholds)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)

        fig.suptitle(f"阈值敏感性分析 — {classifier_name}", fontsize=14,
                     fontweight='bold', y=1.02)
        fig.tight_layout()
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        logger_inst.info(f"阈值敏感性图已保存: {output_path}")

    except ImportError:
        logger_inst.warning("matplotlib 不可用，跳过图表绘制")
    except Exception as e:
        logger_inst.warning(f"绘制阈值敏感性图失败: {e}")


def _plot_pr_curve(threshold_results: list, param_name: str,
                   classifier_name: str, output_path: str, logger_inst):
    """若结果中包含 precision/recall，绘制 PR 曲线。"""
    has_pr = all('precision' in r and 'recall' in r for r in threshold_results)
    if not has_pr:
        return

    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        configure_matplotlib_chinese_fonts()

        thresholds = [r['threshold'] for r in threshold_results]
        precisions = [r['precision'] for r in threshold_results]
        recalls = [r['recall'] for r in threshold_results]
        f1s = [r.get('f1', 0) for r in threshold_results]

        fig, ax = plt.subplots(figsize=(8, 6))

        ax.plot(thresholds, precisions, 's-', color='steelblue',
                linewidth=2, markersize=6, label='Precision')
        ax.plot(thresholds, recalls, 'o-', color='darkorange',
                linewidth=2, markersize=6, label='Recall')
        ax.plot(thresholds, f1s, '^-', color='forestgreen',
                linewidth=2, markersize=6, label='F1-Score')

        # 标记最优 F1
        best_idx = np.argmax(f1s)
        ax.axvline(x=thresholds[best_idx], color='red', linestyle='--', alpha=0.5)
        ax.annotate(f'Best F1={f1s[best_idx]:.3f}\n{param_name}={thresholds[best_idx]}',
                    xy=(thresholds[best_idx], f1s[best_idx]),
                    xytext=(thresholds[best_idx] + 0.5, f1s[best_idx] - 0.1),
                    arrowprops=dict(arrowstyle='->', color='red'),
                    fontsize=10, color='red')

        ax.set_xlabel(param_name, fontsize=12)
        ax.set_ylabel("Score", fontsize=12)
        ax.set_title(f"Precision-Recall 权衡曲线 — {classifier_name}", fontsize=13)
        ax.set_xticks(thresholds)
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)

        fig.tight_layout()
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        logger_inst.info(f"PR 曲线图已保存: {output_path}")

    except ImportError:
        logger_inst.warning("matplotlib 不可用，跳过 PR 曲线绘制")
    except Exception as e:
        logger_inst.warning(f"绘制 PR 曲线失败: {e}")


# ============================================================================
# 5. LaTeX 输出
# ============================================================================

def generate_sensitivity_latex(bank_results: list, fintech_results: list,
                                output_path: str, logger_inst):
    """生成敏感性分析的 LaTeX 表格。"""
    lines = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Classification Threshold Sensitivity Analysis}",
        r"\label{tab:threshold_sensitivity}",
        "",
        r"% Panel A: Bank News Classification",
        r"\begin{subtable}{\textwidth}",
        r"\centering",
        r"\caption{Panel A: Bank News Classification (min\_name\_occurrences)}",
        r"\begin{tabular}{crrr}",
        r"\hline",
        r"Threshold & Classified Positive & Retention Rate (\%) & $\Delta$ Count \\",
        r"\hline",
    ]

    prev_count = None
    for r in bank_results:
        delta = f"{r['count'] - prev_count:+,}" if prev_count is not None else "--"
        lines.append(
            f"  {r['threshold']} & {r['count']:,} & {r['ratio']:.1f} & {delta} \\\\"
        )
        prev_count = r['count']

    lines.extend([
        r"\hline",
        r"\end{tabular}",
        r"\end{subtable}",
        "",
        r"\\[12pt]",
        "",
        r"% Panel B: FinTech News Classification",
        r"\begin{subtable}{\textwidth}",
        r"\centering",
        r"\caption{Panel B: FinTech News Classification (min\_distinct\_keywords)}",
        r"\begin{tabular}{crrr}",
        r"\hline",
        r"Threshold & Classified Positive & Retention Rate (\%) & $\Delta$ Count \\",
        r"\hline",
    ])

    prev_count = None
    for r in fintech_results:
        delta = f"{r['count'] - prev_count:+,}" if prev_count is not None else "--"
        lines.append(
            f"  {r['threshold']} & {r['count']:,} & {r['ratio']:.1f} & {delta} \\\\"
        )
        prev_count = r['count']

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
# 6. 主函数
# ============================================================================

def main():
    """Stage 31 阈值敏感性分析主入口 (Plan-r3 P3-16 docstring 补齐)。

    在 ``min_name_occurrences`` (银行新闻分类) 与 ``min_distinct_keywords``
    (金融科技新闻分类) 两个核心阈值参数上做 1~10 的网格搜索, 输出每个阈值
    组合下的最终样本量, 评估当前生产配置的稳健性。

    输入:
        ``data/processed/00_preprocessing.parquet`` (人民日报 + Wisers 全量)
    输出 (均位于 ``data/processed/eval_reports/``):
        ``threshold_sensitivity_bank.csv`` / ``threshold_sensitivity_fintech.csv``
        ``sensitivity_bank_threshold.png`` / ``sensitivity_fintech_threshold.png``
        ``threshold_sensitivity_table.tex``

    学术依据: Loughran & McDonald (2011, JF) 阈值稳健性范式;
              Gentzkow, Kelly & Taddy (2019, JEL) 文本分析人为选择须报告稳健性.
    """
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段说明书 (仿 39c 黄金范式)。
    logger.info("=" * 72)
    logger.info("阶段 60: 银行×金科分类阈值敏感性 (Loughran-McDonald 2011 / GKT 2019 稳健性范式)")
    logger.info("=" * 72)
    logger.info("【功能】把银行分类阈值 min_name_occurrences 与金科分类阈值 min_distinct_keywords")
    logger.info("        各从 1 扫到 10, 统计每个阈值下被判为正例的文章数/保留率, 验证当前生产")
    logger.info("        阈值(银行=2、金科=2, 见 config/filtering.yaml min_name_occurrences/min_distinct_keywords)是否站得住脚 (产稳健性附录表/图, 不改任何主链数据)。")
    logger.info("【方法】银行轨复用与 stage 11 完全一致的 Aho-Corasick 匹配逻辑(analyze_bank_matches, 含否定模式+短名歧义消解);")
    logger.info("        金科轨为本 stage 独立实现(单遍全文扫+按起始位置切 upper/lower, fix 已消除横跨切点关键词丢失),")
    logger.info("        与 stage 12 analyze_fintech_matches 口径高度一致但非逐字复刻(边缘可能 ±1 篇分歧, 见 docstring);")
    logger.info("        银行判正 = total(含标题)>=阈值 且 (上下半各达标 或 标题命中且正文计数达标);")
    logger.info("        金科判正 = distinct_count>=阈值 且 (上下半各达标 或 标题命中且全文计数达标)。")
    logger.info("        为提速取 min(10000, max(1000, 10%)) 行抽样 (即下限 1000、上限封顶 1 万行;")
    logger.info("        random_state=42); 全量场景实抽 <=1 万行 (约 0.06%), 按抽样比例外推全量。")
    logger.info("【判读】最理想是当前阈值落在'平台区'(±1 微调时正例数几乎不变=稳健, 非凑结果);")
    logger.info("        相邻阈值 |Δ正例数| 降幅最大处(np.argmin diffs, 即 diff 最负处)= '拐点/陡降区',")
    logger.info("        离当前阈值越远越好 (注: 正例数随阈值单调非增, diffs<=0, argmin 取最负=绝对降幅最大)。")
    logger.info("【文献】分类关键参数须做敏感性分析 + 文本分析全部人为选择 (如阈值) 须报告稳健性:")
    logger.info("  · Loughran, T., & McDonald, B. (2011). When is a liability not a liability? "
                "Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. "
                "https://doi.org/10.1111/j.1540-6261.2010.01625.x")
    logger.info("  · Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. "
                "Journal of Economic Literature, 57(3), 535-574. "
                "https://doi.org/10.1257/jel.20181020")
    logger.info("【确定性】纯 CPU 计数, 无 LLM/Embedding/BERT; 抽样 seed 固定=42 → 逐位可复现。")
    logger.info("=" * 72)

    # ① 🧭 项目 / 环境信息 (运行环境指纹 — tone_words.py 黄金范式; 仅日志, golden-safe)。
    # 整块 try/except 兜底: 任何 env-probe 异常都不得拖垮验证阶段。
    try:
        _ver = CONFIG.get('project', {}).get('version', 'v3.15.0')
        logger.info("【环境】项目 = news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) "
                    f"| 版本 {_ver}")
        logger.info(
            f"        Python {sys.version.split()[0]} @ {sys.executable}"
        )
        logger.info(
            f"        平台 {platform.platform()} | CPU {os.cpu_count()} 核 | PID {os.getpid()}"
        )
        logger.info(
            f"        run_id={os.environ.get('NEWS_PROCESS_RUN_ID', '(未设)')} "
            "| 成本 $0 (纯本地 CPU, 无付费 API / 无网络)"
        )
        logger.info(f"        模块 = {os.path.abspath(__file__)}")
        logger.info(f"        工作目录 = {os.getcwd()}")
        logger.info("=" * 72)
    except Exception as _e:  # pragma: no cover - env banner 仅日志
        logger.warning(f"[环境] banner 输出异常, 跳过(不影响产物): {_e}")

    # 使用抽样进行快速分析——取 min(10000, max(1000, 10%)) 行 (下限 1000, 上限封顶 1 万)
    sample_frac = CONFIG.get('threshold_sensitivity', {}).get('sample_fraction', 0.10)
    sample_max = CONFIG.get('threshold_sensitivity', {}).get('sample_max', 10000)
    threshold_range = CONFIG.get('threshold_sensitivity', {}).get('threshold_range', list(range(1, 11)))

    output_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
    os.makedirs(output_dir, exist_ok=True)

    # ======================================================================
    # Step 1: 加载阶段00输出数据
    # ======================================================================
    input_file = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG['filenames']['output_00_preprocessing']
    )

    if not os.path.exists(input_file):
        logger.error(f"阶段00输出文件未找到: {input_file}")
        logger.info("请先运行 00_preprocessing.py")
        return

    logger.info(f"正在加载数据: {input_file}")
    df = pd.read_parquet(input_file)
    total_rows = len(df)
    logger.info(f"总样本量: {total_rows:,}")

    # [io_provenance] 输入 parquet 的 schema 出处: 列数 + 两个被消费文本字段
    # (内容/标题) 的非空占比, 确认 stage-00 预处理输出的文本字段在模拟分类前已填充。
    # 纯日志诊断 (try/except 内, 结果只喂 logger 不参与任何下游计算)。
    try:
        _ncols = df.shape[1]
        _content_nonnull = df['内容'].notna().mean() if '内容' in df.columns else float('nan')
        _title_nonnull = df['标题'].notna().mean() if '标题' in df.columns else float('nan')
        logger.info(
            f"  [输入溯源] 列数={_ncols:,}; 文本字段非空占比: "
            f"内容={pct4(_content_nonnull)}, 标题={pct4(_title_nonnull)}"
        )
    except Exception as _e:  # noqa: BLE001 — 诊断兜底, 不可影响主流程
        logger.debug(f"输入 schema 溯源诊断跳过: {_e}")

    # 抽样加速（保留全量结果比例计算的参考点）
    sample_n = min(sample_max, max(1000, int(total_rows * sample_frac)))
    if sample_n < total_rows:
        df_sample = df.sample(n=sample_n, random_state=42)
        logger.info(f"使用 {sample_n:,} 条抽样进行分析（占比 {pct4(sample_n/total_rows)}）")
    else:
        df_sample = df
        logger.info("使用全量数据进行分析")

    log_memory_usage(logger, "数据加载完成")

    # ======================================================================
    # Step 2: 银行新闻分类阈值敏感性
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    银行新闻分类阈值敏感性分析    ===")
    logger.info("=" * 70)

    bank_params = CONFIG.get('bank_news_classification', {})
    bank_names_file = CONFIG['paths']['bank_names_file']
    split_ratio = bank_params.get('split_ratio', 0.5)
    min_upper = bank_params.get('min_occurrences_upper', 1)
    min_lower = bank_params.get('min_occurrences_lower', 1)
    current_threshold = bank_params.get('min_name_occurrences', 2)

    # [runtime_params] 回显驱动 cond_a/cond_b 的上/下半区分布门控参数, 让审稿人能精确
    # 复现阈值网格背后的分布条件 (split_ratio = 上/下半区切分比例; min_upper/min_lower =
    # 各半区最低命中次数)。仅 headline min_name_occurrences 入日志会丢失这三个支撑参数。
    logger.info(
        f"  分布条件参数: split_ratio={sig4(split_ratio)} (上/下半区切分比例), "
        f"min_occurrences_upper={min_upper:,}, min_occurrences_lower={min_lower:,}, "
        f"当前 min_name_occurrences={current_threshold:,}"
    )
    # 白话: 阈值这种"人为选定的门槛"必须做敏感性并报告, 否则审稿人会质疑是凑结果。
    logger.info(f"  📖 文本分类阈值稳健性: {_REFERENCES['gentzkow_text_as_data']}")

    banks_list, bank_ac, _ = load_bank_names(bank_names_file)
    logger.info(f"已加载 {len(banks_list)} 家银行名称信息")

    # 加载否定模式（确保阈值分析与主分类使用一致的排除逻辑）
    _excl_file = CONFIG['paths'].get(
        'bank_name_exclusions_file',
        os.path.join(os.path.dirname(bank_names_file), 'bank_name_exclusions.json')
    )
    negation_ac, short_name_exclusions, context_window = load_exclusion_patterns(_excl_file)

    # v2: 预计算所有文章的银行匹配数据（一次遍历，含否定模式排除）
    logger.info("正在预计算银行匹配数据（含否定模式排除）...")
    t_precompute = time.time()
    bank_article_matches = _precompute_bank_matches(
        df_sample, bank_ac, banks_list, split_ratio,
        negation_ac=negation_ac,
        short_name_exclusions=short_name_exclusions,
        context_window=context_window,
    )
    logger.info(f"银行匹配预计算完成，耗时 {sig4(time.time() - t_precompute)}s")

    # [result_distribution] 阈值网格只报"过门槛后"计数, 这里刻画"过门槛前"的原始信号密度:
    # 每篇文章命中最强的那家银行的 total(含标题) 命中次数分布。它解释了为何 1~10 的网格
    # 是有信息量的 (信号集中在低位 → 阈值在 2 附近能有效区分)。纯诊断, 复用已算 locals。
    try:
        _bm = np.array(
            [max((_c['total'] for _c in _m['bank_counts'].values()), default=0)
             for _m in bank_article_matches],
            dtype=float,
        )
        if _bm.size:
            logger.info(
                f"  [信号密度·银行] 每文最大银行 total(含标题) 命中分布 (n={_bm.size:,}): "
                f"均值={sig4(_bm.mean())}, 中位数={sig4(np.median(_bm))}, "
                f"Q25={sig4(np.percentile(_bm, 25))}, Q75={sig4(np.percentile(_bm, 75))}, "
                f"最大={int(_bm.max()):,}; 无银行命中占比={pct4(float((_bm == 0).mean()))}"
            )
    except Exception as _e:  # noqa: BLE001 — 诊断兜底, 不可影响主流程
        logger.debug(f"银行信号密度分布诊断跳过: {_e}")

    bank_results = []
    for threshold in threshold_range:
        t_start = time.time()
        n_positive = simulate_bank_classification_from_precomputed(
            bank_article_matches, min_upper, min_lower, threshold
        )
        elapsed = time.time() - t_start
        ratio = n_positive / len(df_sample) * 100 if len(df_sample) > 0 else 0

        result = {
            'threshold': threshold,
            'count': n_positive,
            'ratio': round(ratio, 2),
            'estimated_total': int(n_positive / len(df_sample) * total_rows) if len(df_sample) > 0 else 0,
            'is_current': threshold == current_threshold,
        }
        bank_results.append(result)

        marker = " ← 当前阈值" if threshold == current_threshold else ""
        logger.info(
            f"  min_name_occurrences={threshold}: "
            f"正例={n_positive:,} ({pct4(ratio, fraction=False)}), "
            f"估计全量={result['estimated_total']:,}, "
            f"耗时={sig4(elapsed)}s{marker}"
        )

    # ======================================================================
    # Step 3: 金融科技新闻分类阈值敏感性
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    金融科技新闻分类阈值敏感性分析    ===")
    logger.info("=" * 70)

    fintech_params = CONFIG.get('fintech_news_classification', {})
    fintech_dict_file = CONFIG['paths']['fintech_dict_file']
    ft_split_ratio = fintech_params.get('split_ratio', 0.5)
    ft_min_upper = fintech_params.get('min_occurrences_upper', 1)
    ft_min_lower = fintech_params.get('min_occurrences_lower', 1)
    ft_current_threshold = fintech_params.get('min_distinct_keywords', 2)

    # [runtime_params] 回显驱动 cond_a/cond_b 的上/下半区分布门控参数 (与银行轨对称),
    # 让审稿人能精确复现 min_distinct_keywords 网格背后的分布条件。
    logger.info(
        f"  分布条件参数: split_ratio={sig4(ft_split_ratio)} (上/下半区切分比例), "
        f"min_occurrences_upper={ft_min_upper:,}, min_occurrences_lower={ft_min_lower:,}, "
        f"当前 min_distinct_keywords={ft_current_threshold:,}"
    )
    # 白话: 金科轨用"金融科技词典里命中几个不同关键词"过门槛来判类, 是词典计数分类范式。
    logger.info(f"  📖 词典计数文本分类: {_REFERENCES['loughran_mcdonald_dict']}")

    keywords_list, fintech_ac = load_fintech_dict(fintech_dict_file)
    logger.info(f"已加载 {len(keywords_list)} 个金融科技关键词")

    # 预计算所有文章的匹配数据（仅遍历一次）
    logger.info("预计算文章关键词匹配数据...")
    fintech_matches = _precompute_fintech_matches(df_sample, fintech_ac, ft_split_ratio)
    logger.info(f"预计算完成，共 {len(fintech_matches)} 篇文章")

    # [result_distribution] 阈值网格在 distinct_count 上切割; 这里刻画"过门槛前"的原始信号:
    # 每文不同金科关键词命中数 (distinct_count) 分布 + 零命中文章占比, 给审稿人交代为何
    # min_distinct_keywords 网格有区分力。纯诊断, 复用已算 fintech_matches。
    try:
        _dc = np.array([_m['distinct_count'] for _m in fintech_matches], dtype=float)
        if _dc.size:
            logger.info(
                f"  [信号密度·金科] distinct_count 分布 (n={_dc.size:,}): "
                f"均值={sig4(_dc.mean())}, 中位数={sig4(np.median(_dc))}, "
                f"Q25={sig4(np.percentile(_dc, 25))}, Q75={sig4(np.percentile(_dc, 75))}, "
                f"最大={int(_dc.max()):,}; 零命中占比={pct4(float((_dc == 0).mean()))}"
            )
    except Exception as _e:  # noqa: BLE001 — 诊断兜底, 不可影响主流程
        logger.debug(f"金科信号密度分布诊断跳过: {_e}")

    fintech_results = []
    for threshold in threshold_range:
        t_start = time.time()
        n_positive = simulate_fintech_classification_vectorized(
            fintech_matches, ft_min_upper, ft_min_lower, threshold
        )
        elapsed = time.time() - t_start
        ratio = n_positive / len(df_sample) * 100 if len(df_sample) > 0 else 0

        result = {
            'threshold': threshold,
            'count': n_positive,
            'ratio': round(ratio, 2),
            'estimated_total': int(n_positive / len(df_sample) * total_rows) if len(df_sample) > 0 else 0,
            'is_current': threshold == ft_current_threshold,
        }
        fintech_results.append(result)

        marker = " ← 当前阈值" if threshold == ft_current_threshold else ""
        logger.info(
            f"  min_distinct_keywords={threshold}: "
            f"正例={n_positive:,} ({pct4(ratio, fraction=False)}), "
            f"估计全量={result['estimated_total']:,}, "
            f"耗时={sig4(elapsed)}s{marker}"
        )

    # ======================================================================
    # Step 4: 输出报告
    # ======================================================================
    logger.info("=" * 70)
    logger.info("===    生成分析报告    ===")
    logger.info("=" * 70)

    # CSV 报告
    bank_df = pd.DataFrame(bank_results)
    bank_csv = os.path.join(output_dir, 'threshold_sensitivity_bank.csv')
    bank_df.to_csv(bank_csv, index=False, encoding='utf-8-sig')
    logger.info(f"银行分类阈值分析: {bank_csv}")

    fintech_df = pd.DataFrame(fintech_results)
    fintech_csv = os.path.join(output_dir, 'threshold_sensitivity_fintech.csv')
    fintech_df.to_csv(fintech_csv, index=False, encoding='utf-8-sig')
    logger.info(f"金融科技分类阈值分析: {fintech_csv}")

    # 可视化
    _plot_threshold_sensitivity(
        bank_results, 'min_name_occurrences', '银行新闻分类',
        os.path.join(output_dir, 'sensitivity_bank_threshold.png'), logger
    )
    _plot_threshold_sensitivity(
        fintech_results, 'min_distinct_keywords', '金融科技新闻分类',
        os.path.join(output_dir, 'sensitivity_fintech_threshold.png'), logger
    )

    # LaTeX 表格
    generate_sensitivity_latex(
        bank_results, fintech_results,
        os.path.join(output_dir, 'threshold_sensitivity_table.tex'), logger
    )

    # 最优阈值建议
    logger.info("-" * 70)
    logger.info("=== 阈值建议摘要 ===")
    logger.info(f"银行新闻分类当前阈值: min_name_occurrences = {current_threshold}")
    logger.info(f"金融科技新闻分类当前阈值: min_distinct_keywords = {ft_current_threshold}")

    # 找到"拐点"：保留率下降速率最大的阈值
    if len(bank_results) >= 2:
        diffs = [bank_results[i+1]['count'] - bank_results[i]['count']
                 for i in range(len(bank_results) - 1)]
        max_drop_idx = np.argmin(diffs)
        logger.info(
            f"银行分类建议：阈值={bank_results[max_drop_idx+1]['threshold']} "
            f"处样本量下降最剧烈 (Δ={diffs[max_drop_idx]:+,})"
        )

    if len(fintech_results) >= 2:
        diffs = [fintech_results[i+1]['count'] - fintech_results[i]['count']
                 for i in range(len(fintech_results) - 1)]
        max_drop_idx = np.argmin(diffs)
        logger.info(
            f"金融科技分类建议：阈值={fintech_results[max_drop_idx+1]['threshold']} "
            f"处样本量下降最剧烈 (Δ={diffs[max_drop_idx]:+,})"
        )

    # ======================================================================
    # 结果分析 — 写入日志, 让 <stage>.log 自带"当前阈值稳不稳"的判读 (仿 39c)。
    # 仅服务于日志的局部计算, 不回写 df / 任何产物 (golden-safe)。
    # ======================================================================
    def _platform_verdict(results: list, cur_thr: int):
        """检查 cur_thr 是否落在'平台区'(±1 微调时正例数几乎不变=稳健)。

        返回 (cur_count, cur_ratio, 相对左右邻居的最大百分比波动, 文字判读)。
        纯日志用, 不修改任何产物。
        """
        by_thr = {r['threshold']: r for r in results}
        cur = by_thr.get(cur_thr)
        if cur is None or cur['count'] == 0:
            return (cur['count'] if cur else 0,
                    cur['ratio'] if cur else 0.0, None, '当前阈值不在网格内或正例为 0')
        neighbors = [by_thr[t] for t in (cur_thr - 1, cur_thr + 1) if t in by_thr]
        if not neighbors:
            return cur['count'], cur['ratio'], None, '无相邻阈值可比 (网格端点)'
        max_pct = max(abs(n['count'] - cur['count']) / cur['count'] * 100
                      for n in neighbors)
        if max_pct < 5.0:
            verdict = (f'平台区 (±1 仅 {pct4(max_pct, fraction=False)} 波动 <5% '
                       '→ 阈值稳健, 非凑结果)')
        elif max_pct < 15.0:
            verdict = (f'缓坡区 (±1 波动 {pct4(max_pct, fraction=False)} '
                       '→ 尚可, 建议附录披露敏感性)')
        else:
            verdict = (f'陡降区 (±1 波动 {pct4(max_pct, fraction=False)} ≥15% '
                       '→ 不利, 微调即显著改变样本, 须谨慎)')
        return cur['count'], cur['ratio'], max_pct, verdict

    # crash-guard: 结果分析块整体 try/except, 任何诊断异常都不得拖垮阶段
    # (本块已在 CSV/PNG/LaTeX 写盘之后, 但仍兜底以防 division/索引异常)。
    try:
        logger.info("-" * 72)
        logger.info(
            f"【结果分析】阈值网格 {threshold_range[0]}~{threshold_range[-1]}, "
            f"抽样 {len(df_sample):,} 篇 (银行名 {len(banks_list)} 家 / 金科词 {len(keywords_list)} 个):"
        )

        b_cnt, b_ratio, b_pct, b_verdict = _platform_verdict(
            bank_results, current_threshold)
        logger.info(
            f"  · 银行分类 @当前阈值={current_threshold}: 正例={b_cnt:,} ({pct4(b_ratio, fraction=False)}), "
            f"估计全量={next((r['estimated_total'] for r in bank_results if r['threshold'] == current_threshold), 0):,}"
        )
        logger.info(
            f"    判读 (±1 最大波动 {pct4(b_pct, fraction=False)}): {b_verdict}"
            if b_pct is not None else f"    判读: {b_verdict}"
        )

        f_cnt, f_ratio, f_pct, f_verdict = _platform_verdict(
            fintech_results, ft_current_threshold)
        logger.info(
            f"  · 金科分类 @当前阈值={ft_current_threshold}: 正例={f_cnt:,} ({pct4(f_ratio, fraction=False)}), "
            f"估计全量={next((r['estimated_total'] for r in fintech_results if r['threshold'] == ft_current_threshold), 0):,}"
        )
        logger.info(
            f"    判读 (±1 最大波动 {pct4(f_pct, fraction=False)}): {f_verdict}"
            if f_pct is not None else f"    判读: {f_verdict}"
        )

        # 全网格单调性自检 (阈值越高正例应越少; 反单调=逻辑异常, loud 提示)。
        b_counts = [r['count'] for r in bank_results]
        f_counts = [r['count'] for r in fintech_results]
        b_mono = all(b_counts[i] >= b_counts[i + 1] for i in range(len(b_counts) - 1))
        f_mono = all(f_counts[i] >= f_counts[i + 1] for i in range(len(f_counts) - 1))
        logger.info(
            f"  · 单调性自检: 银行 {'✓ 单调非增 (符合预期)' if b_mono else '✗ 出现反单调 (异常, 须排查)'}, "
            f"金科 {'✓ 单调非增 (符合预期)' if f_mono else '✗ 出现反单调 (异常, 须排查)'}"
        )

        # 全网格保留率跨度描述性摘要 (max→min/均值/中位, 全 sig4; 仅日志, golden-safe)。
        b_ratios = [r['ratio'] for r in bank_results]
        f_ratios = [r['ratio'] for r in fintech_results]
        if b_ratios:
            logger.info(
                f"  · 银行保留率跨度 (阈值 {threshold_range[0]}~{threshold_range[-1]}): "
                f"max={pct4(max(b_ratios), fraction=False)} → min={pct4(min(b_ratios), fraction=False)}, "
                f"均值={pct4(float(np.mean(b_ratios)), fraction=False)}, "
                f"中位={pct4(float(np.median(b_ratios)), fraction=False)}, "
                f"标准差={pct4(float(np.std(b_ratios)), fraction=False)}"
            )
        if f_ratios:
            logger.info(
                f"  · 金科保留率跨度 (阈值 {threshold_range[0]}~{threshold_range[-1]}): "
                f"max={pct4(max(f_ratios), fraction=False)} → min={pct4(min(f_ratios), fraction=False)}, "
                f"均值={pct4(float(np.mean(f_ratios)), fraction=False)}, "
                f"中位={pct4(float(np.median(f_ratios)), fraction=False)}, "
                f"标准差={pct4(float(np.std(f_ratios)), fraction=False)}"
            )

        # 优雅降级 / 边界警告。
        if b_cnt == 0:
            logger.warning("  ⚠ 银行分类在当前阈值正例为 0 — 检查银行名词典/否定模式是否加载成功")
        if f_cnt == 0:
            logger.warning("  ⚠ 金科分类在当前阈值正例为 0 — 检查金科关键词词典 (fintech_dict) 是否加载成功")
        if len(keywords_list) == 0:
            logger.warning("  ⚠ 金科关键词词典为空 → 金科网格全 0, 敏感性结论无效 (优雅降级, 须补词典)")

        # 小样本警告 (盘面抽样 / T=2)。
        if sample_n < total_rows:
            logger.info(
                f"  ⚠ 本次为抽样分析 ({sample_n:,}/{total_rows:,}={pct4(sample_n / total_rows)}), "
                "全量比率以外推值为参考; 阈值平台/陡降判读以 约1,819万/T=19 全量实测为准, 当前仅验证管道正确性。"
            )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # ======================================================================
    # 📖 方法论依据 — 关键词词典/文本度量构造法的近期顶刊同源文献 (仅日志, golden-safe)。
    # 阈值稳健性范式本身由顶部 banner 的 Loughran-McDonald (2011) / GKT (2019) 锚定;
    # 此处补充"种子词/二元组关键词命中 → firm-level / 主题级文本度量"这一底层构造法
    # (本阶段银行名 + 金科词 Aho-Corasick 命中计数 = 该范式的离散计数实例) 的核验前沿。
    # ======================================================================
    logger.info("=" * 72)
    logger.info("📖 方法论依据 (本阶段关键词命中分类 + 阈值稳健性所锚定的核验文献):")
    logger.info(
        "  · Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & "
        "Tahoun, A. (2025). The diffusion of new technologies. The Quarterly "
        "Journal of Economics, 140(2), 1299-1365. https://doi.org/10.1093/qje/qjaf002"
    )
    logger.info("    (白话: 用文本 bigram 识别新兴技术并追踪扩散; 本阶段以金科关键词命中"
                "作技术关注强度判据, 同源词表构造法。)")
    logger.info(
        "  · Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). "
        "Firm-level climate change exposure. The Journal of Finance, 78(3), "
        "1449-1498. https://doi.org/10.1111/jofi.13219"
    )
    logger.info("    (白话: 机器学习发现关键词 + 二元组命中构 firm-level 关注度, 是关键词"
                "词表构建的标准模板; 本阶段金科/银行词典命中计数与之同范式。)")
    logger.info(
        "  · Wu, D. (A.). (2024). Text-based measure of supply chain risk "
        "exposure. Management Science, 70(7), 4781-4801. "
        "https://doi.org/10.1287/mnsc.2023.4927"
    )
    logger.info("    (白话: 种子词嵌入 + 词袋构 firm-level 文本暴露并以波动率验证; 本阶段对"
                "'命中几次才算正例'的阈值敏感性即此类文本度量的稳健性检验。)")
    logger.info("=" * 72)

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=len(df_sample),
                      extra_info={'分析模式': '抽样分析' if sample_n < total_rows else '全量分析',
                                  '抽样量': f'{len(df_sample):,}'})
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
