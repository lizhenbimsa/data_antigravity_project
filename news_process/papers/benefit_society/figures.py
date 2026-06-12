"""news_process.papers.benefit_society.figures — 经营效益态度论文图表.

Phase 3d 最小可用集: 占位 ``plot_benefit_distribution()``。
具体图表方案在论文修订过程中扩展。
"""

from __future__ import annotations

from pathlib import Path

from news_process.papers._common import (
    COLORBLIND_PALETTE,
    FIGSIZE_SINGLE,
    PaperConfig,
    apply_publication_style,
    get_paper_config,
    load_panel,
)


def plot_benefit_distribution(paper_config: PaperConfig | None = None,
                              *, filename: str = 'fig1_benefit_distribution.pdf'
                              ) -> Path:
    """绘制 ``benefit_mean_full`` 在 Bank-Year 维度的分布。"""
    import matplotlib.pyplot as plt

    pc = paper_config or get_paper_config('benefit_society')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['benefit_mean_full'])
    series = panel['benefit_mean_full'].dropna()

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[1],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.set_xlabel('Benefit-Operations Attitude Mean (Full)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Distribution of bank-year benefit attitude')

    out = pc.output_dir / filename
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_main_coefplot(paper_config: PaperConfig | None = None,
                       *, filename: str = 'fig2_main_coefplot.pdf') -> Path:
    """Figure 2: 主效应系数图 (读 Table 2 esttab CSV)."""
    from news_process.papers._common.paper_figures_ext import coefplot_from_esttab_df
    from news_process.papers.benefit_society.tables import build_table2_main

    pc = paper_config or get_paper_config('benefit_society')
    df = build_table2_main(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    return coefplot_from_esttab_df(
        df,
        variables=[v for v in ['benefit_mean_full', 'article_sim_mean',
                               'fintech_intensity_mean'] if v in df.index],
        output_path=out,
        title='Main Effects — benefit_society',
        xlabel='Coefficient (95% CI)',
    )


def plot_mechanism_forest(paper_config: PaperConfig | None = None,
                          *, filename: str = 'fig3_mechanism_forest.pdf') -> Path:
    """Figure 3: Token/Hidden/Subst 机制森林图 (读 Table 3 esttab CSV)."""
    from news_process.papers._common.paper_figures_ext import forest_plot_from_esttab_df
    from news_process.papers.benefit_society.tables import build_table3_mechanism

    pc = paper_config or get_paper_config('benefit_society')
    df = build_table3_mechanism(pc)
    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    # 取行索引中第一个存在的机制变量
    var = next((v for v in ['token_adopt_kw_p50', 'hidden_adopt_kw_p50',
                            'subst_adopt_kw_p50', 'benefit_mean_full']
                if v in df.index), None)
    if var is None:
        raise KeyError("No recognized mechanism variable in df.index")
    return forest_plot_from_esttab_df(
        df, variable=var, output_path=out,
        title='Mechanism: Token / Hidden / Subst — benefit_society',
    )


def plot_benefit_distribution_with_subsampling_ci(
    paper_config: PaperConfig | None = None,
    *,
    filename: str = 'fig1_benefit_distribution_with_ci.pdf',
    block_size: int = 2,
    n_subsamples: int = 1000,
    seed: int = 42,
) -> Path:
    """Figure 1 with cluster block bootstrap 95% CI overlay (C1).

    fix(omni-g-papers-misc-10, 2026-06-11) 方法标签更正: 旧图注/标题宣称
    Politis-Romano (1994) subsampling, 但 stats_helpers 实现自始是
    with-replacement 块自助 (Carlstein/Künsch block bootstrap)。现 (a) 图注/
    标题改为 cluster block bootstrap; (b) 改按 ``target_bank`` 整簇重采样
    (cluster bootstrap over banks), 替代位置切片块 — 位置块在 dropna 移位 /
    全量 T=18 不平衡面板下会跨银行, 不再 preserve within-bank dependence。
    注: J-L-M 2026 Figure 2 caption 的 "subsampling" 措辞不再照搬, 以实现为准。

    ``block_size`` 仅在面板缺 target_bank 列的 positional fallback 下生效。
    """
    import matplotlib.pyplot as plt

    from news_process.papers._common.stats_helpers import cluster_block_bootstrap_ci

    pc = paper_config or get_paper_config('benefit_society')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id,
                       project_config=pc.config,
                       columns=['benefit_mean_full', 'target_bank'])
    valid = panel.dropna(subset=['benefit_mean_full'])
    series = valid['benefit_mean_full'].values
    if 'target_bank' in valid.columns and valid['target_bank'].notna().any():
        # cluster bootstrap over banks (块=同一银行的全部 bank-year 观测)
        mean, lo, hi = cluster_block_bootstrap_ci(
            series, cluster_id=valid['target_bank'].values,
            n_resamples=n_subsamples, seed=seed,
        )
    else:  # positional fallback (面板异常缺 target_bank 时)
        mean, lo, hi = cluster_block_bootstrap_ci(
            series, block_size=block_size, n_resamples=n_subsamples, seed=seed,
        )

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    ax.hist(series, bins=40, color=COLORBLIND_PALETTE[1],
            alpha=0.85, edgecolor='white', linewidth=0.4)
    ax.axvline(mean, color=COLORBLIND_PALETTE[3], linestyle='-', linewidth=1.5,
               label=f'Mean = {mean:.3f}')
    ax.axvspan(lo, hi, color=COLORBLIND_PALETTE[3], alpha=0.15,
               label=f'95% cluster block-bootstrap CI = [{lo:.3f}, {hi:.3f}]')
    ax.set_xlabel('Benefit-Operations Attitude Mean (Full)')
    ax.set_ylabel('Bank-Year frequency')
    ax.set_title('Distribution with cluster block bootstrap 95% CI')
    ax.legend(loc='best', fontsize=8, frameon=False)

    out = pc.output_dir / filename
    fig.savefig(out)
    plt.close(fig)
    return out


def plot_placebo_comparison(
    paper_config: PaperConfig | None = None,
    *,
    filename: str = 'figA2_placebo_comparison.pdf',
) -> Path:
    """Figure A2: Placebo β 与 main β 对照条形图 (S1 可视化证据).

    按 V2.0 plan §3 P3.3: 5 个 placebo β + 1 个 main β 条形图, 每根条标注
    |β_placebo / β_main| 比率。验收 (AC-S1) 目检标准: placebo 条高
    应 ≤ main 条高的 30%。

    白话: placebo (安慰剂) 检验 = 把处理变量换成"理论上不该有效果"的
    业务线指标再跑一遍回归; 如果安慰剂的系数远小于主回归 (比率<0.3),
    说明主结果不是数据里随便什么变量都能跑出来的假象。

    fix(omni-gapfill-11, 2026-06-12): parse_esttab_csv 单元格是 Coefficient
    namedtuple — 旧 ``float(coef_row[c])`` 必 TypeError (pd.notna 对 namedtuple
    返回 True 不挡)。现 (a) 复用 paper_figures_ext._to_value_se 提取 value;
    (b) 系数行选取跳过 footer stats 行 (N/r2 等); (c) 补 docstring 承诺的
    |β_placebo/β_main| 比率标注 (首列约定为 Main, 见 23_tableA10 模板 mlabels)。
    """
    import math

    import matplotlib.pyplot as plt

    from news_process.papers._common.paper_figures_ext import _to_value_se
    from news_process.papers._common.stata_postprocess import _KNOWN_STATS
    from news_process.papers.benefit_society.tables import build_table_a10_placebo

    pc = paper_config or get_paper_config('benefit_society')
    pc.output_dir.mkdir(parents=True, exist_ok=True)

    try:
        df = build_table_a10_placebo(pc)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Placebo table CSV missing (run Stata 23_tableA10_*.do first): {e}"
        ) from e

    # 取第一行系数行 (通常是投影均值变量), 跳过表尾统计行 (N / r2 / ...)。
    coef_vars = [ix for ix in df.index if ix not in _KNOWN_STATS]
    if not coef_vars:
        raise ValueError("Placebo CSV empty (no coefficient rows)")
    coef_row = df.loc[coef_vars[0]]

    apply_publication_style()
    fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
    cols = list(coef_row.index)
    raw_values = [_to_value_se(coef_row[c])[0] for c in cols]
    values = [v if math.isfinite(v) else 0.0 for v in raw_values]
    colors = [COLORBLIND_PALETTE[0]] + [COLORBLIND_PALETTE[2]] * (len(cols) - 1)

    ax.bar(range(len(cols)), values, color=colors, alpha=0.85,
           edgecolor='white', linewidth=0.5)
    # |β_placebo / β_main| 比率标注 (AC-S1: 预期 < 0.3)
    main_beta = values[0]
    if main_beta != 0.0:
        for i, v in enumerate(values[1:], start=1):
            ratio = abs(v / main_beta)
            ax.annotate(f'{ratio:.2f}', xy=(i, v), xytext=(0, 4),
                        textcoords='offset points', ha='center', fontsize=7,
                        color=COLORBLIND_PALETTE[3])
        ax.annotate('labels: |β_placebo/β_main| (AC-S1 < 0.3)',
                    xy=(0.99, 0.02), xycoords='axes fraction',
                    ha='right', fontsize=7, color='gray')
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=30, ha='right', fontsize=8)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.set_ylabel('β coefficient')
    ax.set_title('Placebo vs Main: business-line robustness (S1, J-L-M §4.2)')

    out = pc.output_dir / 'figures' / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out)
    plt.close(fig)
    return out


__all__ = [
    'plot_benefit_distribution',
    'plot_main_coefplot',
    'plot_mechanism_forest',
    # V2.0 J-L-M 对齐 (Round 9)
    'plot_benefit_distribution_with_subsampling_ci',
    'plot_placebo_comparison',
]
