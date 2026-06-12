"""news_process.pipeline.audit.inter_track_kappa — Stage 39a (三维借用计划 v1.37 的 P1)。

在 ``llm_verified_dual_both == True`` 子集上, 对三个创新维度 (locus,
substantiveness, collab_mode) 计算 full 轨与 ctx 轨之间的文章级 Cohen's κ;
输出机器可读 CSV + 论文可用 TeX 到 ``eval_reports/``。

与 Stata 模板 ``20_tableA1_inter_track_kappa.do.tmpl`` 互为镜像。

学术锚点:
  - Cohen (1960) — κ 公式。
  - Landis & Koch (1977) — κ 解释阈值。
  - 预期 κ ∈ [0.50, 0.70] (不是"越高越好"); κ > 0.70 提示双轨冗余;
    κ < 0.30 提示噪声 (Landis & Koch 1977 区间 + 项目内部约定;
    原解释文档随 docs/ 目录于 commit 1698bda5 删除)。
  - Plan v1.37 §4.3.1: bootstrap CI, NaN-aware percentile + 50%
    有限值占比守卫 (R30A-01/R30B-01)。

白话: 同一篇文章我们用两种文本口径 (full=全文, ctx=实体上下文窗口) 各打
一次标签。κ 衡量两套标签的一致程度。太一致 (>0.70) 提示两个口径可能测的
是同一个东西; 太不一致 (<0.30) 提示至少有一轨是噪声。落在中间区间说明
双轨互补、各有信息。注意: 这只是诊断披露 (供论文中讨论), 双轨的去留不由
相关性决定 — 项目立场是 full/ctx 互为稳健性, 高相关 = 对归因窗口稳健。
"""
import os
import warnings

import numpy as np
import pandas as pd

from news_process.core.config import load_config
from news_process.core.logging import setup_logging
from news_process.validation.radius_sensitivity_llm import cohens_kappa_2cat

STAGE_NAME = "39a_inter_track_kappa"

# Plan v1.37 §4.3.1 thresholds (Landis & Koch 1977 区间 + 项目内部约定; 原 docs/ 解释文档已删).
# v3.4.0 §J.4: 第三维度 collab_mode κ ≥ 0.45 (mirrors substantiveness fair-to-moderate
# 标准; Chesbrough 2003 + L&S 2006 SMJ; additive supplementation per Nosek 2018 PNAS).
_THRESHOLDS = {
    'innovation_locus': 0.50,
    'innovation_substantiveness': 0.45,
    'innovation_collab_mode': 0.45,
}


def _compute_kappa_with_bootstrap(y1, y2, n_boot=1000, seed=42):
    """返回 (kappa_point, ci_low, ci_high, n_obs), bootstrap 对 NaN 安全。

    实现遵循 plan v1.37 §4.3.1 步骤 1-5:
      1. n_obs < 3 时短路 → (nan, nan, nan, n_obs)。
      2. 点估计 κ 经 cohens_kappa_2cat(...)['kappa'] (R29C-01 dict 取值)。
      3. Bootstrap 重抽 n_boot 次; 每次重抽追加 ['kappa']。
      4. NaN-aware percentile (R30A-01/R30B-01): 要求 ≥50% 的 κ 为有限值,
         否则返回 (kappa_point, nan, nan, n_obs) + WARN。
      5. 边界: 原始输入某列为常量 → (nan, nan, nan, n_obs)。

    白话: bootstrap 就是"有放回地反复抽自己的样本再算一遍 κ", 用上千次
    结果的 2.5%/97.5% 分位数当置信区间。如果一半以上的重抽算不出有效 κ
    (比如抽到的子样本里某个标签全是同一个值), 区间就不可信, 直接报 NaN。
    """
    y1 = np.asarray(y1)
    y2 = np.asarray(y2)
    n_obs = len(y1)
    if n_obs < 3:
        return (float('nan'), float('nan'), float('nan'), int(n_obs))

    point = cohens_kappa_2cat(y1, y2)
    kappa_point = point['kappa']
    # 原始输入常量列边界 (点估计已是 NaN → 直接返回 NaN 元组)
    if np.isnan(kappa_point):
        return (float('nan'), float('nan'), float('nan'), int(n_obs))

    rng = np.random.default_rng(seed)
    kappas = []
    for _ in range(n_boot):
        idx = rng.choice(n_obs, size=n_obs, replace=True)
        kb = cohens_kappa_2cat(y1[idx], y2[idx])['kappa']
        kappas.append(kb)

    finite = [k for k in kappas if not np.isnan(k)]
    if len(finite) < 0.5 * n_boot:
        warnings.warn(
            f"Bootstrap degenerate: only {len(finite)}/{n_boot} finite κ "
            f"resamples (< 50%); CI bounds returned as NaN.",
            RuntimeWarning,
            stacklevel=2,
        )
        return (float(kappa_point), float('nan'), float('nan'), int(n_obs))

    ci_low = float(np.nanpercentile(kappas, 2.5))
    ci_high = float(np.nanpercentile(kappas, 97.5))
    return (float(kappa_point), ci_low, ci_high, int(n_obs))


def compute_inter_track_kappa(df):
    """返回 7 列 DataFrame: field, kappa_point, ci_95_low,
    ci_95_high, n_obs, threshold, passes_threshold。

    每个创新维度一行 (locus, substantiveness, collab_mode [v3.4.0])。"""
    rows = []
    for field, threshold in _THRESHOLDS.items():
        col_full = f"{field}_full"
        col_ctx = f"{field}_ctx"
        if col_full not in df.columns or col_ctx not in df.columns:
            rows.append({
                'field': field,
                'kappa_point': float('nan'),
                'ci_95_low': float('nan'),
                'ci_95_high': float('nan'),
                'n_obs': 0,
                'threshold': threshold,
                'passes_threshold': False,
            })
            continue
        # 丢弃任一轨为 NaN 的成对行
        sub = df[[col_full, col_ctx]].dropna()
        kp, lo, hi, n = _compute_kappa_with_bootstrap(
            sub[col_full].to_numpy(),
            sub[col_ctx].to_numpy(),
        )
        passes = (not np.isnan(kp)) and (kp >= threshold)
        rows.append({
            'field': field,
            'kappa_point': kp,
            'ci_95_low': lo,
            'ci_95_high': hi,
            'n_obs': n,
            'threshold': threshold,
            'passes_threshold': bool(passes),
        })
    return pd.DataFrame(rows, columns=[
        'field', 'kappa_point', 'ci_95_low', 'ci_95_high',
        'n_obs', 'threshold', 'passes_threshold',
    ])


def _render_tex(table_df, out_path):
    """Booktabs 风格 TeX 表; 满足 plan v1.37 §4.7 验收正则
    (\\toprule / \\midrule / \\bottomrule; 7 列; plan 原文写 2 数据行,
    v3.4.0 增 collab_mode 维度后实际为每维度一行 = 3 行)。"""
    cols = list(table_df.columns)
    n_cols = len(cols)
    lines = [
        "\\begin{tabular}{" + "l" + "r" * (n_cols - 1) + "}",
        "\\toprule",
        " & ".join(cols) + " \\\\",
        "\\midrule",
    ]
    for _, r in table_df.iterrows():
        cells = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                cells.append("NaN" if np.isnan(v) else f"{v:.4f}")
            elif isinstance(v, (bool, np.bool_)):
                cells.append("True" if bool(v) else "False")
            else:
                cells.append(str(v))
        lines.append(" & ".join(cells) + " \\\\")
    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    out_path_str = str(out_path)
    with open(out_path_str, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")


def run_stage(config=None, logger=None):
    """Stage 39a 入口。

    从配置的 output dir 读 ``21_tone_llms.parquet``, 按
    ``llm_verified_dual_both == True`` 过滤, 对全部三个创新维度计算
    轨间 κ, 写 CSV + TeX 到 ``eval_reports/``。
    """
    if config is None:
        config = load_config()
    if logger is None:
        logger = setup_logging(STAGE_NAME, config["paths"]["log_dir"])

    output_dir = config["paths"]["output_dir"]
    input_path = os.path.join(output_dir, "21_tone_llms.parquet")

    if not os.path.exists(input_path):
        logger.warning(f"Input not found: {input_path}; emitting NaN row table.")
        df_subset = pd.DataFrame(columns=[
            'innovation_locus_full', 'innovation_locus_ctx',
            'innovation_substantiveness_full', 'innovation_substantiveness_ctx',
            'innovation_collab_mode_full', 'innovation_collab_mode_ctx',
            'llm_verified_dual_both',
        ])
    else:
        df = pd.read_parquet(input_path)
        if 'llm_verified_dual_both' not in df.columns:
            logger.warning(
                "Column 'llm_verified_dual_both' absent; emitting NaN rows."
            )
            df_subset = df.iloc[0:0]
        else:
            df_subset = df[df['llm_verified_dual_both'] == True].copy()
            if len(df_subset) == 0:
                logger.warning("dual_both subset empty; emitting NaN rows.")

    table = compute_inter_track_kappa(df_subset)

    eval_dir = os.path.join(output_dir, "eval_reports")
    os.makedirs(eval_dir, exist_ok=True)
    csv_path = os.path.join(eval_dir, "inter_track_kappa_table.csv")
    tex_path = os.path.join(eval_dir, "inter_track_kappa_table.tex")

    table.to_csv(csv_path, index=False, encoding='utf-8')
    _render_tex(table, tex_path)

    # 阈值区间告警, 按 plan v1.37 §4.3.1 step 6
    for _, r in table.iterrows():
        k = r['kappa_point']
        if not np.isnan(k) and (k < 0.30 or k > 0.70):
            warnings.warn(
                f"{r['field']} κ={k:.4f} outside expected [0.30, 0.70]; "
                f"<0.30 = one track noise; >0.70 = dual-track redundant.",
                RuntimeWarning,
                stacklevel=2,
            )
            logger.warning(
                f"{r['field']} κ={k:.4f} outside [0.30, 0.70] sentinel range."
            )

    logger.info(f"Wrote {csv_path} + {tex_path} (n_obs={int(table['n_obs'].iloc[0] if len(table) else 0)})")
    return table
