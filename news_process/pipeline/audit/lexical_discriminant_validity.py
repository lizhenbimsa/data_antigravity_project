"""news_process.pipeline.audit.lexical_discriminant_validity — Stage 39d (v3.5.1).

A1/A3 vs LLM substance 的 discriminant validity 检验 — 3 × 3 矩阵:
    T1 = LLM substance vote (现有 avg_subst_prob_score_full)
    T2 = A1 clarity (新 mean_clarity_score_full)
    T3 = A3 num_intensity (新 mean_num_intensity_full)

锚定文献:
    - Henseler, Ringle, Sarstedt (2015) JAMS 43: 115-135 — HTMT
    - Fornell & Larcker (1981) JMR 18(1): 39-50 — AVE / φ² discriminant
    - Bagozzi & Yi (1988) JAMS 16: 74-94 — 构念效度框架
    - Cohen (1960) EPM 20(1): 37-46 — κ for nominal agreement
    - Cronbach (1951) Psychometrika 16(3): 297-334 — α reliability

实施状态 (per plan v0.3 §2.3, 8 项中 7 已实施, 第 4 项 R8-H1 mask 在 v3.7.2 推迟):
    1. Algorithm path: main() 一次性 pd.read_parquet 读全表入内存, 逐对 indicator
       在内存计算 cross-correlation (面板仅约 9000 bank-year, 内存无压力, 无 OOM).
       注: 计划中的 "pairwise on-disk" OOM 缓解设计 (R7-H3/R8-H3) 从未实现,
       因实测面板规模远小于 OOM 阈值.
    2. Permutation seed = **42** (与 pipeline/audit/inter_track_kappa.py 的
       _compute_kappa_with_bootstrap (seed=42) 一致, 修 R9-H3).
    3. HTMT 双 cutoff (修 R4-M2): strict < 0.85 / lenient < 0.90.
    4. ctx-fallback HTMT mask (R8-H1 audit anchor): 文档锁定但**当前未在 39d 内实施**.
       实测 fallback 率 10.43% (v3.7.2 R4-1 测于 disk 14_news_with_ctx.parquet, 1170 行).
       公共信号 `ctx_is_fallback` (article) + `frac_ctx_fallback` (panel) 已由 v3.7.2
       全管道延伸暴露; 39d 是 validation-only stage (EXPECTED_NO_OUTPUT, 不进 paper main
       analysis), 在此实施 mask 的 ROI 远低于 panel 列推广, 因此本 stage 推迟实施.
       论文层若需 R8-H1 等价 robustness, 直接在 Stata 用
       ``if frac_ctx_fallback < 0.30`` 或 ``if n_articles_for_ctx_independence >= 5``.
    5. Cronbach α **across all 3 indicators** (修 R9-M2): 而非 within track (within
       single-item 数学退化).
    6. Cohen κ 方向锁定 (修 M2'): 象征性 (1) ↔ clarity_score < median (1); 预期正 κ.
    7. n_articles(b,t) ≥ 2 mask (修 R8-H2).
    8. Panel HTMT 适用性 disclosure (修 R9-M1): paper §3.4 加 "cross-sectional HTMT
       applied to panel as conservative diagnostic per Henseler 2015 footnote 11".

白话: 我们有三把"尺子"量银行新闻 — LLM 判的实质性 (T1)、词典算的表述
清晰度 (T2)、数字密集度 (T3)。判别效度检验回答: 这三把尺子是不是真的在
量三件不同的事? HTMT 看任意两把尺子的相关有多高 (低于 0.85/0.90 才算
"各量各的"); Cronbach α 看把三者合成一个量表是否内部一致; Cohen κ 专门
看"象征性"标签与"表述含糊"是否如理论预期正相关。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 73_lexical_discriminant_validity.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 读 `40_panel_yearly.parquet`(银行-年度面板)。每轨用 3 个指标列(单 indicator 构念): T1=LLM 实质性概率 `avg_subst_prob_score_{full,ctx,ss}`、T2=词典清晰度 `mean_clarity_score_*`、T3=数字密集度 `mean_num_intensity_*`。

**处理步骤**(`main` → 三轨循环 `run_discriminant_validity`):
- 样本 mask: 优先 `n_articles_llm_valid ≥ 2`(该列缺失时回退 n_articles_col, 默认 'n_articles'), 与 39e 同口径(修 R8-H2); mask 后 <10 obs → status=insufficient_obs 跳过。
- `compute_htmt`: 单 indicator 退化为 HTMT_ij=|corr(T_i,T_j)|(`_safe_corrcoef` Pearson r, 缺值/方差 0 → NaN)。
- `compute_ave_and_phi_squared`: 单 item AVE=1.0, φ²_ij=r²(Fornell-Larcker 1981)。
- `compute_cronbach_alpha_across_indicators`: 跨 3 个 item α=(k/(k−1))(1−Σσ²_i/σ²_total)(跨全部 indicator 而非 within track, 避单 item 退化)。
- `compute_cohen_kappa_substance_vs_clarity`: 二分化(substance≥0.5→象征性 1; clarity<median→含糊 1), 方向锁定预期正 κ; mask.sum()<4 或常量轴守卫(任一二分轴无变异 → 显式 NaN, 避 vacuous κ=0)。
- `compute_spearman_substance_clarity`: 同报 Spearman ρ 避二分化丢信息。
- `compute_permutation_null`: 每对 indicator 打乱 1000 次(seed=42, np.random.default_rng)取 |corr| 的 p95/p99/mean/std。

**关键算法/公式**: Henseler-Ringle-Sarstedt(2015) HTMT 双 cutoff(strict<0.85 / lenient<0.90, 三档 verdict strict_pass/lenient_pass/fail/nan); Cohen(1960) κ; Cronbach(1951) α; Fornell-Larcker(1981) √AVE>max(φ)。注: docstring 标 "算法路径 pairwise on-disk"(为 R7-H3/R8-H3 OOM 设计), 实际 main 一次性 read_parquet 全表入内存逐对计算(面板仅约 9000 bank-year, 内存无压力)。

**输出**: report dict 落两份: parquet(每个非 dict 标量一行 metric/value, 统一 str 化避 pyarrow ArrowTypeError)+ JSON(全报告含 htmt/htmt_verdict/ave_phi_squared/cronbach_alpha_across/cohen_kappa_substance_clarity/spearman/permutation_null/permutation_seed)。

**外部依赖/超时/确定性**: 纯 numpy/pandas, 无 sklearn/LLM/Embedding/_llm_cache.db; permutation seed=42 保证确定性; DAG timeout=900(15 分钟, 实际 N≈9000 bank-year 单线程<1 分钟)。

**DAG 位置**: 验证阶段 39d(STAGES_VALIDATION), 上游=stage 40 panel(及上游 14/15 物化的 clarity/num_intensity 列), 与 39e(LM 子词典 8 维 HTMT)互补, 服务论文 §3.4 判别效度披露。注: R8-H1 ctx-fallback HTMT mask 文档锁定但本 stage 推迟实施(validation-only ROI 低), 论文层若需可在 Stata 用 frac_ctx_fallback<0.30 等价处理。

■ 白话说明

**这一步在做什么**: 我们有三把不同的"尺子"量同一批银行新闻——LLM 判的"实质性"(讲的是真创新还是装样子)、词典算的"表述清晰度"(话说得清不清楚)、"数字密集度"(文章里堆了多少数据)。这一步像检查"这三把尺子量的是不是三件不同的事": 它算任意两把尺子读数的相关高不高(低于 0.85/0.90 才算各量各的), 还专门检查理论预期——"装样子"的报道是不是真的更"含糊"。

**为什么需要它**: 一篇严谨的论文不能让人觉得"你这几个文本指标其实在重复量同一个东西"。这一步用判别效度检验给出统计证据: 三把尺子相关都够低、且能合成一个内部一致的量表, 就证明它们是独立有效的测度, 论文可以放心分别使用。

**对最终面板/论文的影响**: 它不改主回归用的面板列(只产摘要表和 JSON), 但它支撑论文方法学部分"我们的清晰度、数字密集度指标和 LLM 实质性判断是可区分的有效构念"这一关键声明。如果检验发现两把尺子高度重叠, 论文就要重新考虑是否同时用、或在稳健性里披露这个重叠。
========================================================================
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

STAGE_NAME = "73_lexical_discriminant_validity"

# v3.5.1 frozen at D0
HTMT_CUTOFF_STRICT = 0.85
HTMT_CUTOFF_LENIENT = 0.90
PERMUTATION_SEED = 42  # 与 inter_track_kappa.py:41 一致 (修 R9-H3)
N_PERMUTATIONS_DEFAULT = 1000

# 三轨判别效度的 3 指标列名 (T1 substance / T2 clarity / T3 num_intensity)。
# full = 主 spec (run_discriminant_validity 默认参数, 向后兼容旧测试契约);
# ctx / ss = 镜像并列轨 (main() 额外各写一份 track-suffixed 输出)。
# ss = 银行+金科同句共现轨 (suffix _ss): 机械 _full→_ss swap, 列尚未物化时
# run_discriminant_validity 内部 missing-columns 守卫优雅跳过 (status=missing_columns)。
INDICATORS_FULL = {
    'substance_col': 'avg_subst_prob_score_full',
    'clarity_col': 'mean_clarity_score_full',
    'num_intensity_col': 'mean_num_intensity_full',
}
INDICATORS_CTX = {k: v.replace('_full', '_ctx') for k, v in INDICATORS_FULL.items()}
INDICATORS_SS = {k: v.replace('_full', '_ss') for k, v in INDICATORS_FULL.items()}

# WS-B (F6/F-R2): locus/collab 判别效度的焦点 indicator 列名。
# ⚠ 硬编码命名例外 (third-track-ss/fintech-dims 两次踩坑): locus/collab 的
#   ctx/ss 列名非机械 _full→_ctx/_ss swap, 禁 .replace 派生。
#   对照轴 clarity/num_intensity 三维共用 (沿用 INDICATORS_*)。
# direction=None → 无理论符号锚, 跳定向 κ, 只报无向 |corr| (见 run_discriminant_validity)。
LOCUS_INDICATORS = {
    '_full': {'substance_col': 'tech_frac',    'clarity_col': 'mean_clarity_score_full',
              'num_intensity_col': 'mean_num_intensity_full'},
    '_ctx':  {'substance_col': 'tech_frac_lc', 'clarity_col': 'mean_clarity_score_ctx',
              'num_intensity_col': 'mean_num_intensity_ctx'},
    '_ss':   {'substance_col': 'tech_frac_ls', 'clarity_col': 'mean_clarity_score_ss',
              'num_intensity_col': 'mean_num_intensity_ss'},
}
COLLAB_INDICATORS = {
    '_full': {'substance_col': 'collab_frac',       'clarity_col': 'mean_clarity_score_full',
              'num_intensity_col': 'mean_num_intensity_full'},
    '_ctx':  {'substance_col': 'collab_frac_cm',    'clarity_col': 'mean_clarity_score_ctx',
              'num_intensity_col': 'mean_num_intensity_ctx'},
    '_ss':   {'substance_col': 'collab_frac_cm_ss', 'clarity_col': 'mean_clarity_score_ss',
              'num_intensity_col': 'mean_num_intensity_ss'},
}

# WS-B (F11): 三创新维彼此的 panel 列名 (跨构念 heterotrait-monomethod 块)。
# ⚠ 硬编码命名例外, 禁 .replace 派生。substance=prob 均值 / locus·collab=frac 份额
#   (口径异质, |corr| 不可与对照轴块横向比较, 见 compute_heterotrait_monomethod 披露)。
INNOVATION_DIM_COLS = {
    '_full': {'substance': 'avg_subst_prob_score_full', 'locus': 'tech_frac',    'collab': 'collab_frac'},
    '_ctx':  {'substance': 'avg_subst_prob_score_ctx',  'locus': 'tech_frac_lc', 'collab': 'collab_frac_cm'},
    '_ss':   {'substance': 'avg_subst_prob_score_ss',   'locus': 'tech_frac_ls', 'collab': 'collab_frac_cm_ss'},
}


def compute_heterotrait_monomethod(panel: pd.DataFrame, cols: dict,
                                   min_n: int = 10) -> dict:
    """三创新维彼此的跨构念 heterotrait-monomethod 裸相关块 (Campbell-Fiske 1959 概念锚)。

    WS-B (F11): 对 (substance×locus) / (substance×collab) / (locus×collab) 三对
    panel 列两两 |Pearson r|。⚠ 非 heteromethod 判别效度——三 frac/prob 列共享
    stage21 LLM 单次调用方法方差, 低 |corr| 仅弱"非冗余"旁证; 承重判别证据是
    stage 72 NMI。口径异质 (substance=prob 均值 vs locus/collab=frac 份额) 已披露。

    Args:
        panel: bank-year panel.
        cols: {'substance': col, 'locus': col, 'collab': col} (某轨, 命名例外硬编码)。
        min_n: 公共有限观测 < min_n → 该对标 insufficient_obs (与 F20 一致)。

    Returns:
        dict: {pair: {abs_corr|status, n_obs}} + method/披露串。
    """
    pairs = [('substance', 'locus'), ('substance', 'collab'), ('locus', 'collab')]
    out = {
        'method': 'heterotrait-monomethod |corr| (Campbell-Fiske 1959 概念锚, 非 heteromethod)',
        'disclosure': ('三 frac/prob 列共享 stage21 LLM 单次调用方法方差 → 低 |corr| 仅弱'
                       '非冗余旁证; 承重判别证据见 stage 72 NMI。口径异质 (substance=prob '
                       '均值 vs locus/collab=frac 份额), |corr| 不可与对照轴块横向比较。'),
        'pairs': {},
    }
    for a, b in pairs:
        key = f'{a}_x_{b}'
        ca, cb = cols.get(a), cols.get(b)
        if ca not in panel.columns or cb not in panel.columns:
            out['pairs'][key] = {'status': 'missing_column',
                                 'missing': [c for c in (ca, cb) if c not in panel.columns]}
            continue
        arr_a = pd.to_numeric(panel[ca], errors='coerce').to_numpy(dtype=float)
        arr_b = pd.to_numeric(panel[cb], errors='coerce').to_numpy(dtype=float)
        n_common = int((np.isfinite(arr_a) & np.isfinite(arr_b)).sum())
        if n_common < min_n:
            out['pairs'][key] = {'status': 'insufficient_obs', 'n_obs': n_common}
            continue
        r = _safe_corrcoef(arr_a, arr_b)
        out['pairs'][key] = {'abs_corr': abs(r) if not np.isnan(r) else float('nan'),
                             'n_obs': n_common}
    return out


def _safe_corrcoef(a: np.ndarray, b: np.ndarray) -> float:
    """安全 Pearson r: 缺值 / 方差 0 → NaN."""
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 2:
        return float('nan')
    a, b = a[mask], b[mask]
    if a.std() == 0 or b.std() == 0:
        return float('nan')
    return float(np.corrcoef(a, b)[0, 1])


def compute_htmt(indicators: dict[str, np.ndarray]) -> dict[str, float]:
    """3 × 3 HTMT matrix (Henseler 2015 JAMS).

    HTMT 公式: 对每对 construct (i, j):
        HTMT_ij = mean(|cross-correlations between items of i and j|)
                / sqrt(mean(|within-correlations of i|) × mean(|within-correlations of j|))

    本项目 simplification: 每 construct 仅 1 indicator (T1/T2/T3 各 1), HTMT 退化为:
        HTMT_ij = |corr(T_i, T_j)|  (within-corr 退化为 1)

    Args:
        indicators: dict[str, np.ndarray] of 3 panel-level vectors aligned.

    Returns:
        dict: {('T1','T2'): float, ('T1','T3'): float, ('T2','T3'): float}
              所有 pairwise HTMT 值 ∈ [0, 1].
    """
    keys = list(indicators.keys())
    result = {}
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k_i, k_j = keys[i], keys[j]
            r = _safe_corrcoef(indicators[k_i], indicators[k_j])
            result[f'htmt_{k_i}_{k_j}'] = abs(r) if not np.isnan(r) else float('nan')
    return result


def compute_ave_and_phi_squared(indicators: dict[str, np.ndarray]) -> dict[str, float]:
    """AVE / φ² (Fornell-Larcker 1981 JMR).

    单 indicator 退化: AVE = 1; φ² = corr²;
    Fornell-Larcker criterion: √AVE > max(φ) across pairs.

    Returns:
        dict: AVE_i for each + phi_ij² for each pair.
    """
    keys = list(indicators.keys())
    result = {f'ave_{k}': 1.0 for k in keys}  # single-item AVE = 1.0
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k_i, k_j = keys[i], keys[j]
            r = _safe_corrcoef(indicators[k_i], indicators[k_j])
            result[f'phi2_{k_i}_{k_j}'] = r * r if not np.isnan(r) else float('nan')
    return result


def compute_cronbach_alpha_across_indicators(indicators: dict[str, np.ndarray]) -> float:
    """跨全部 indicator 的 Cronbach α (修 R9-M2)。

    标准公式 (k 个 item):
        α = (k / (k-1)) × (1 - Σ σ²_i / σ²_total)

    Args:
        indicators: 含 ≥ 2 个 indicator 的 dict (每个是 panel 向量)。

    Returns:
        Cronbach α ∈ [0, 1]。
    """
    arr = np.column_stack([v for v in indicators.values()])
    arr = arr[~np.isnan(arr).any(axis=1)]  # 按行取完整观测 (任一列缺值整行剔除)
    k = arr.shape[1]
    if k < 2 or arr.shape[0] < 2:
        return float('nan')
    item_var_sum = arr.var(axis=0, ddof=1).sum()
    total_var = arr.sum(axis=1).var(ddof=1)
    if total_var <= 0:
        return float('nan')
    return float((k / (k - 1)) * (1 - item_var_sum / total_var))


def compute_cohen_kappa_substance_vs_clarity(
        substance: np.ndarray,
        clarity: np.ndarray,
        clarity_median: Optional[float] = None) -> dict[str, float]:
    """LLM substance 与二分化 clarity 之间的 Cohen κ (1960 EPM)。

    方向锁定 (修 M2'): 象征性 (1) ↔ clarity_score < median (1); 预期正 κ.

    Args:
        substance: LLM substance 概率的 panel 向量 (0=实质性, 1=象征性)。
        clarity: clarity_score 的 panel 向量 (连续值)。
        clarity_median: D0 冻结的 median; None 时样本内计算。

    Returns:
        dict: {kappa, n_obs, median_used}。
    """
    s = np.asarray(substance, dtype=float)
    c = np.asarray(clarity, dtype=float)
    mask = np.isfinite(s) & np.isfinite(c)
    if mask.sum() < 4:
        return {'kappa': float('nan'), 'n_obs': int(mask.sum()),
                'median_used': float('nan')}
    s, c = s[mask], c[mask]

    # Dichotomize: substance ≥ 0.5 → 1 (象征性);
    #              clarity < median → 1 (含糊, 与象征性配对); 修 M2' 方向锁定.
    if clarity_median is None:
        clarity_median = float(np.median(c))
    s_bin = (s >= 0.5).astype(int)
    c_bin = (c < clarity_median).astype(int)

    # P1 修复 (metric-audit 2026-06-02): 常量轴守卫. 若任一二分轴无变异 (全 0 / 全 1
    # — 真实数据上 substance 概率经 n_articles≥2 mask 后恒 < 0.5 → s_bin 全 0),
    # Cohen κ 数学上未定义却会退化为貌似合法的 0.0 (p_o == p_e), 被误读为"零一致".
    # 显式返回 NaN, 避免 vacuous κ=0 进报告.
    if s_bin.min() == s_bin.max() or c_bin.min() == c_bin.max():
        return {'kappa': float('nan'), 'n_obs': len(s_bin),
                'median_used': clarity_median}

    # Cohen κ
    n = len(s_bin)
    p_o = float((s_bin == c_bin).mean())  # 观测一致率
    p_s = float((s_bin == 1).mean())
    p_c = float((c_bin == 1).mean())
    p_e = p_s * p_c + (1 - p_s) * (1 - p_c)  # 随机碰巧一致的期望率
    if p_e >= 1.0:
        return {'kappa': float('nan'), 'n_obs': n, 'median_used': clarity_median}
    kappa = (p_o - p_e) / (1 - p_e)
    return {'kappa': float(kappa), 'n_obs': n, 'median_used': clarity_median}


def compute_spearman_substance_clarity(
        substance: np.ndarray, clarity: np.ndarray) -> float:
    """Spearman ρ (修 R4-m3) 同时报, 避免 dichotomize 损失信息."""
    s = pd.Series(substance)
    c = pd.Series(clarity)
    return float(s.corr(c, method='spearman'))


def compute_permutation_null(
        indicators: dict[str, np.ndarray],
        n_permutations: int = N_PERMUTATIONS_DEFAULT,
        seed: int = PERMUTATION_SEED) -> dict[str, dict[str, float]]:
    """Permutation null distribution for HTMT (修 R9-H3 seed=42).

    对每对 indicator 做 N 次 shuffle, 计算 null HTMT; 返回 95% percentile 作 cutoff.

    Returns:
        dict: {(pair): {p95, p99, mean, std}}
    """
    rng = np.random.default_rng(seed)
    keys = list(indicators.keys())
    null_results = {}
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            k_i, k_j = keys[i], keys[j]
            arr_i = np.asarray(indicators[k_i], dtype=float)
            arr_j = np.asarray(indicators[k_j], dtype=float)
            mask = np.isfinite(arr_i) & np.isfinite(arr_j)
            if mask.sum() < 10:
                null_results[f'null_{k_i}_{k_j}'] = {
                    'p95': float('nan'), 'p99': float('nan'),
                    'mean': float('nan'), 'std': float('nan'),
                }
                continue
            arr_i, arr_j = arr_i[mask], arr_j[mask]
            null_htmts = np.empty(n_permutations)
            for k in range(n_permutations):
                shuffled = rng.permutation(arr_j)
                r = np.corrcoef(arr_i, shuffled)[0, 1]
                null_htmts[k] = abs(r) if not np.isnan(r) else 0.0
            null_results[f'null_{k_i}_{k_j}'] = {
                'p95': float(np.percentile(null_htmts, 95)),
                'p99': float(np.percentile(null_htmts, 99)),
                'mean': float(null_htmts.mean()),
                'std': float(null_htmts.std()),
            }
    return null_results


def run_discriminant_validity(
        panel: pd.DataFrame,
        substance_col: str = 'avg_subst_prob_score_full',
        clarity_col: str = 'mean_clarity_score_full',
        num_intensity_col: str = 'mean_num_intensity_full',
        n_articles_col: str = 'n_articles',
        min_n_articles: int = 2,
        focal_label: str = 'T1_substance',
        direction: Optional[str] = 'positive') -> dict:
    """主入口: 对 bank-year panel 跑完整 discriminant validity 检验.

    WS-B (F6/R-P1-2/R6-P2-3/P2-4): 泛化为可对任一创新维 (substance/locus/collab)
    跑判别效度旁证。focal_col (=substance_col 形参, 复用) vs 词汇对照轴 clarity /
    num_intensity 的裸相关 + permutation null。
      - substance (direction='positive'): 有 W&Z 理论符号锚 → 报定向 Cohen κ;
        返回键 cohen_kappa_substance_clarity / spearman_substance_clarity (M7 冻结)。
      - locus/collab (direction=None): 无方向判别假设 → 跳过 κ, 只报无向
        |corr| (abs_corr_focal_clarity) + spearman_focal_clarity。
    ⚠ 判别效度承重证据是 stage 72 NMI; 此处 73 裸相关仅弱"非冗余"旁证。

    Args:
        panel: bank-year panel DataFrame.
        substance_col / clarity_col / num_intensity_col: 焦点 + 对照轴列名.
        n_articles_col: n_articles 列名 (用于 ≥ 2 mask, 修 R8-H2).
        min_n_articles: 最小 article 数 cell (修 R8-H2).
        focal_label: 焦点 indicator 的 T1 键名 (substance/locus/collab 区分).
        direction: 'positive' → 有理论符号锚, 报定向 κ; None → 跳 κ 只报 |corr|.

    Returns:
        dict: 完整 discriminant validity report.
    """
    required_cols = [substance_col, clarity_col, num_intensity_col]
    missing = [c for c in required_cols if c not in panel.columns]
    if missing:
        logger.warning(f"v3.5.1 73: 缺列 {missing}, graceful skip (R4)")
        return {'status': 'missing_columns', 'missing': missing,
                'focal_label': focal_label}

    # 修 R8-H2: n_articles ≥ 2 mask
    # metric-audit 2026-06-02: 判别效度 metric (substance/clarity) 建立在 LLM-valid
    # 文章上, mask 应用 LLM-valid 计数; encode-02 重构后 n_articles=物理篇数,
    # 故优先 n_articles_llm_valid (重生 panel 后存在), 旧冻结 panel 缺列则回退 n_articles.
    _mask_col = ('n_articles_llm_valid'
                 if 'n_articles_llm_valid' in panel.columns else n_articles_col)
    if _mask_col in panel.columns:
        mask = panel[_mask_col] >= min_n_articles
        panel = panel.loc[mask].copy()
        logger.info(f"v3.5.1 39d: {_mask_col} ≥ {min_n_articles} mask 后 {len(panel)} obs")

    if len(panel) < 10:
        return {'status': 'insufficient_obs', 'n_obs': len(panel),
                'focal_label': focal_label}

    indicators = {
        focal_label: panel[substance_col].to_numpy(),
        'T2_clarity': panel[clarity_col].to_numpy(),
        'T3_num_intensity': panel[num_intensity_col].to_numpy(),
    }

    htmt = compute_htmt(indicators)
    ave_phi = compute_ave_and_phi_squared(indicators)
    cronbach = compute_cronbach_alpha_across_indicators(indicators)
    null_dist = compute_permutation_null(indicators, seed=PERMUTATION_SEED)

    # HTMT 双 cutoff 解读 (修 R4-M2)
    htmt_verdict = {}
    for k, v in htmt.items():
        if np.isnan(v):
            htmt_verdict[k] = 'nan'
        elif v < HTMT_CUTOFF_STRICT:
            htmt_verdict[k] = 'strict_pass'
        elif v < HTMT_CUTOFF_LENIENT:
            htmt_verdict[k] = 'lenient_pass'
        else:
            htmt_verdict[k] = 'fail'

    report = {
        'status': 'ok',
        'n_obs': len(panel),
        'focal_label': focal_label,
        'htmt': htmt,
        'htmt_cutoff_strict': HTMT_CUTOFF_STRICT,
        'htmt_cutoff_lenient': HTMT_CUTOFF_LENIENT,
        'htmt_verdict': htmt_verdict,
        'ave_phi_squared': ave_phi,
        'cronbach_alpha_across': cronbach,
        'permutation_null': null_dist,
        'permutation_seed': PERMUTATION_SEED,
        'min_n_articles_mask': min_n_articles,
    }
    # WS-B/R6-P2-4: substance 有理论符号锚 → 定向 κ + 旧键名冻结;
    # locus/collab (direction=None) → 跳 κ, 只报无向 |corr| + spearman。
    spearman_fc = compute_spearman_substance_clarity(
        indicators[focal_label], indicators['T2_clarity'])
    if direction is not None:
        report['cohen_kappa_substance_clarity'] = (
            compute_cohen_kappa_substance_vs_clarity(
                indicators[focal_label], indicators['T2_clarity']))
        report['spearman_substance_clarity'] = spearman_fc
    else:
        report['abs_corr_focal_clarity'] = htmt.get(
            f'htmt_{focal_label}_T2_clarity', float('nan'))
        report['spearman_focal_clarity'] = spearman_fc
    return report


def _write_track_report(report: dict, out_dir: Path, suffix: str) -> None:
    """写单轨 39d 产物 (parquet 摘要 + JSON htmt 矩阵)。

    full 轨保留 canonical 文件名 (``73_lexical_discriminant.parquet`` /
    ``73_htmt_matrix.json``, 向后兼容旧测试/下游); ctx / ss 轨用 track-suffixed
    名 (``73_lexical_discriminant_{ctx,ss}.parquet`` 等)。
    """
    name_pq = ('73_lexical_discriminant.parquet' if suffix == 'full'
               else f'73_lexical_discriminant_{suffix}.parquet')
    name_js = ('73_htmt_matrix.json' if suffix == 'full'
               else f'73_htmt_matrix_{suffix}.json')

    # 输出 1: parquet (主表)
    # quality-hardening Round 40 (2026-05-27): value 列旧实现是 int/float/str
    # 混合 (e.g. n_obs=int + status='ok' str), pyarrow 无法推导 object 类型 →
    # ArrowTypeError. 改 unifies to str: parquet 是 audit 摘要, 数值/字符串都
    # 当 metric 文本看, 不破坏向后兼容 (无下游 reader; grep 全仓 0 个).
    df_out = pd.DataFrame([{
        'metric': k,
        'value': str(v),
    } for k, v in report.items() if not isinstance(v, dict)])
    df_out.to_parquet(out_dir / name_pq, index=False)

    # 输出 2: JSON htmt matrix
    with open(out_dir / name_js, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    # 日志数值统一 4 位有效数字 (项目规范 2026-06-24; sig4/pct4 单一事实源)。
    from news_process.core.logging import sig4
    alpha_val = report.get('cronbach_alpha_across')
    alpha_str = sig4(alpha_val) if isinstance(alpha_val, (int, float)) else 'N/A'
    kappa_val = report.get('cohen_kappa_substance_clarity', {}).get('kappa', float('nan'))
    kappa_str = sig4(kappa_val) if isinstance(kappa_val, (int, float)) else 'N/A'
    logger.info(f"v3.5.1 stage 39d [{suffix}] 完成: HTMT verdict={report.get('htmt_verdict')}, "
                f"α_across={alpha_str}, κ_subst_clarity={kappa_str}")

    # 结果分析 — 写入日志: 逐对 HTMT vs null + α / κ / ρ 人话判读。
    htmt = report.get('htmt', {})
    verdict = report.get('htmt_verdict', {})
    null = report.get('permutation_null', {})
    logger.info(f"  [{suffix}] 结果分析 (n_obs={report.get('n_obs')}; HTMT 越低越好, <0.85 strict_pass):")
    _pairs = (
        ('htmt_T1_substance_T2_clarity', 'null_T1_substance_T2_clarity', '实质性 × 清晰度'),
        ('htmt_T1_substance_T3_num_intensity', 'null_T1_substance_T3_num_intensity', '实质性 × 数字密集'),
        ('htmt_T2_clarity_T3_num_intensity', 'null_T2_clarity_T3_num_intensity', '清晰度 × 数字密集'),
    )
    for hk, nk, label in _pairs:
        hv = htmt.get(hk, float('nan'))
        p95 = null.get(nk, {}).get('p95', float('nan'))
        logger.info(f"    {label}: HTMT={sig4(hv)} (null_p95={sig4(p95)}) → {verdict.get(hk, 'nan')}")
    _all_pass = bool(verdict) and all(v == 'strict_pass' for v in verdict.values())
    logger.info("    HTMT 总判读: " + ("三对全部 strict_pass → 三指标判别有效, 各量各的"
                                       if _all_pass else "存在未通过对 (见上)"))
    logger.info(f"    Cronbach α_across = {alpha_str} (越低越好: 证明三者非单一量表、不冗余)")
    if isinstance(kappa_val, (int, float)) and np.isnan(kappa_val):
        logger.info("    Cohen κ = nan (常量轴守卫: mask 后 substance 二分轴退化为常量, "
                    "κ 数学未定义, 显式置 NaN 避免假的 κ=0)")
    else:
        logger.info(f"    Cohen κ (象征性↔含糊) = {kappa_str} (方向锁定, 预期正)")
    spear = report.get('spearman_substance_clarity', float('nan'))
    logger.info(f"    Spearman ρ (实质性 vs 清晰度) = {sig4(spear)}")


def main():
    """Stage 39d 入口。三轨 (full / ctx / ss) 各跑一次判别效度并写产物。

    full = 主 spec (canonical 输出名, 向后兼容); ctx / ss = 镜像并列轨, 列尚未
    物化时 run_discriminant_validity 返回 status=missing_columns → 该轨优雅跳过。
    """
    import os
    import platform
    import sys
    import time

    from news_process.core.config import load_config
    from news_process.core.logging import setup_logging, sig4
    config = load_config()
    # 接入项目统一日志: 写 <log_dir>/73_lexical_discriminant_validity.log。
    # 此前本阶段仅 getLogger(__name__) 无 FileHandler, 虽产出 parquet/json 却不落
    # <stage>.log (与 39a/39e 等同族 audit 阶段不一致); 现对齐 setup_logging 约定。
    global logger
    logger = setup_logging(STAGE_NAME, config['paths'].get('log_dir', 'logs'))

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39e)。
    logger.info("=" * 72)
    logger.info("阶段 39d: 文本指标判别效度 (HTMT + AVE + Cronbach α + Cohen κ; v3.5.1)")
    logger.info("=" * 72)
    logger.info("【功能】检验 T1=LLM实质性 / T2=词典清晰度 / T3=数字密集度 三把文本尺子是否各量各的")
    logger.info("        (论文 §3.4 判别效度披露; 三轨 full/ctx/ss 各跑一次)。")
    logger.info("【方法】HTMT=两两 |corr| (双 cutoff strict<0.85 / lenient<0.90, 越低越好);")
    logger.info("        φ²=共享方差; Cronbach α 跨 3 指标 (此处越低越好=非单一量表/不冗余);")
    logger.info("        Cohen κ 验'象征性↔含糊'方向; permutation null 1000 次 (seed=42) 为参照。")

    _t0 = time.time()
    # fix(stage-input-config-wiring, 2026-06-25): panel 名经 config 单一真值解析
    # (output_40_panel_yearly; 键存在值=默认 → golden-safe), 替代硬编码字面量。
    panel_path = os.path.join(config['paths']['output_dir'], config.get('filenames', {}).get('output_40_panel_yearly', '40_panel_yearly.parquet'))
    out_dir = Path(config['paths']['output_dir'])

    # ① 🧭 项目 / 环境信息 + ③ ⚙ 运行配置 (日志富集 2026-06-24, 仿 tone_words.py 金标准)。
    # 纯日志, 不改任何产物 / schema / 控制流 (golden-safe)。验证阶段 EXPECTED_NO_OUTPUT
    # 仅产摘要 parquet/JSON, 不进 paper main analysis; 纯 numpy/pandas, 无 LLM/嵌入/网络 ($0)。
    try:
        logger.info("")
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (文本指标判别效度; STAGES_VALIDATION 39d; 三轨 full/ctx/ss)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板; v3.11.1)")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "纯 CPU / 无 LLM·嵌入·网络·_llm_cache.db ($0; seed 锁定确定性可复现)")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入面板: {panel_path}")
        logger.info(f"     · 输出目录: {out_dir} (full 轨 canonical: 73_lexical_discriminant.parquet "
                    "+ 73_htmt_matrix.json; ctx/ss 轨 track-suffixed)")

        logger.info("  ⚙ 运行配置 (v3.5.1 冻结常量, 模块顶部单一事实源)")
        logger.info(f"     · HTMT 双 cutoff: strict<{sig4(HTMT_CUTOFF_STRICT)} / lenient<{sig4(HTMT_CUTOFF_LENIENT)} "
                    "(Henseler-Ringle-Sarstedt 2015 HTMT; 越低越判别有效)")
        logger.info(f"     · permutation: N={N_PERMUTATIONS_DEFAULT:,d} 次 | seed={PERMUTATION_SEED} "
                    "(与 inter_track_kappa.py 一致, 确定性参照分布)")
        logger.info("     · 样本 mask: n_articles_llm_valid≥2 (缺列回退 n_articles; 与 39e 同口径); "
                    "mask 后 <10 obs → 跳过")
        logger.info("     · 焦点轴: T1=LLM实质性 (substance/locus/collab) | 对照轴: T2=清晰度 T3=数字密集度")
        logger.info("     · 方法: 单 indicator 构念 → HTMT 退化为 |Pearson r|; AVE=1.0; "
                    "φ²=r² (Fornell-Larcker 1981); Cronbach α 跨 3 指标; Cohen κ 方向锁定 (象征性↔含糊)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置信息打印失败 (不影响处理): {e}")

    # 📖 方法论依据 (纯日志, golden-safe): 本阶段判别效度/构念效度锚点的 APA-7 全引 + DOI。
    # 仅引用经 Crossref 核验注册表中的条目, 逐字照抄 (绝不臆造 DOI); 8 个锚点
    # (HTMT/AVE/α/MTMM/CFA/κ + 现代信度 Krippendorff α + stage72 NMI chance-校正)
    # 均经 Crossref 核验并附可访问 DOI 链接 (后两条 2024 期刊, 偏近期方法学)。
    try:
        logger.info("")
        logger.info("  📖 方法论依据 (构念/判别效度锚点; APA-7 全引 + 已核验 DOI 链接)")
        logger.info("     · Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). A new criterion "
                    "for assessing discriminant validity in variance-based structural equation "
                    "modeling. Journal of the Academy of Marketing Science, 43(1), 115-135. "
                    "https://doi.org/10.1007/s11747-014-0403-8  [HTMT 双 cutoff 判别效度准则]")
        logger.info("     · Fornell, C., & Larcker, D. F. (1981). Evaluating structural equation "
                    "models with unobservable variables and measurement error. Journal of "
                    "Marketing Research, 18(1), 39-50. https://doi.org/10.2307/3151312  "
                    "[AVE / φ² 判别效度]")
        logger.info("     · Cronbach, L. J. (1951). Coefficient alpha and the internal structure "
                    "of tests. Psychometrika, 16(3), 297-334. "
                    "https://doi.org/10.1007/BF02310555  [α 内部一致性信度]")
        logger.info("     · Campbell, D. T., & Fiske, D. W. (1959). Convergent and discriminant "
                    "validation by the multitrait-multimethod matrix. Psychological Bulletin, "
                    "56(2), 81-105. https://doi.org/10.1037/h0046016  [MTMM 异质特质-单方法锚]")
        logger.info("     · Bagozzi, R. P., & Yi, Y. (1988). On the evaluation of structural "
                    "equation models. Journal of the Academy of Marketing Science, 16(1), 74-94. "
                    "https://doi.org/10.1007/BF02723327  [CFA 构念效度框架]")
        logger.info("     · Cohen, J. (1960). A coefficient of agreement for nominal scales. "
                    "Educational and Psychological Measurement, 20(1), 37-46. "
                    "https://doi.org/10.1177/001316446002000104  [κ for nominal agreement]")
        logger.info("     · Marzi, G., Balzano, M., & Marchiori, D. (2024). K-Alpha "
                    "Calculator–Krippendorff's Alpha Calculator: A user-friendly tool for "
                    "computing Krippendorff's Alpha inter-rater reliability coefficient. "
                    "MethodsX, 12, 102545. https://doi.org/10.1016/j.mex.2023.102545  "
                    "[Krippendorff α 现代 inter-coder 信度锚, 补充本阶段 Cronbach α / Cohen κ]")
        logger.info("     · Mahmoudi, A., & Jemielniak, D. (2024). Proof of biased behavior of "
                    "Normalized Mutual Information. Scientific Reports, 14(1), Article 9021. "
                    "https://doi.org/10.1038/s41598-024-59073-9  [NMI 有偏(偏好更多簇) → "
                    "承重判别证据 stage 72 NMI 比较分区须 chance 校正之锚]")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  方法论依据打印失败 (不影响处理): {e}")

    if not os.path.exists(panel_path):
        logger.warning(f"v3.5.1 39d: panel 缺 ({panel_path}), graceful skip")
        return

    panel = pd.read_parquet(panel_path)

    # substance 三轨各跑一次 (有 W&Z 理论符号锚 → 定向 κ; INDICATORS_SS 列缺失优雅跳过)
    for suffix, cols in (
        ('full', INDICATORS_FULL),
        ('ctx', INDICATORS_CTX),
        ('ss', INDICATORS_SS),
    ):
        report = run_discriminant_validity(panel, **cols)
        # graceful skip 路径: run_discriminant_validity 在缺列 / 样本不足时
        # 返回 {'status': ..., ...} 而非完整 metric 字典. 此时不写文件 + 简短日志.
        if isinstance(report, dict) and report.get('status') in ('missing_columns', 'insufficient_obs'):
            logger.info(f"v3.5.1 stage 73 [substance/{suffix}] 跳过: {report}")
            continue
        _write_track_report(report, out_dir, suffix)

    # WS-B: locus / collab 三轨各跑一次 (无理论符号锚 → direction=None, 跳定向 κ,
    # 只报无向 |corr|)。承重判别证据是 stage 72 NMI; 此处仅弱"非冗余"旁证。
    # 命名例外列名硬编码在 LOCUS/COLLAB_INDICATORS (禁 .replace 派生)。
    for dim, ind_map, flabel in (
        ('locus', LOCUS_INDICATORS, 'T1_locus'),
        ('collab', COLLAB_INDICATORS, 'T1_collab'),
    ):
        for track, cols in ind_map.items():
            suffix = track.lstrip('_')
            report = run_discriminant_validity(
                panel, **cols, focal_label=flabel, direction=None)
            if isinstance(report, dict) and report.get('status') in (
                    'missing_columns', 'insufficient_obs'):
                logger.info(f"v3.5.1 stage 73 [{dim}/{suffix}] 跳过: {report}")
                continue
            # dim-suffixed 产物 (73_discriminant_{dim}_{track})
            name_js = f'73_discriminant_{dim}_{suffix}.json'
            with open(out_dir / name_js, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            logger.info(
                f"v3.5.1 stage 73 [{dim}/{suffix}] 完成 (无向 |corr| 旁证, 无定向 κ): "
                f"HTMT verdict={report.get('htmt_verdict')}, "
                f"abs_corr_focal_clarity={sig4(report.get('abs_corr_focal_clarity'))}")

    # WS-B (F11): 三创新维彼此跨构念 heterotrait-monomethod 块 (三轨各一份)。
    # 弱"非冗余"旁证 (承重判别证据是 stage 72 NMI); 命名例外硬编码。
    for track, dim_cols in INNOVATION_DIM_COLS.items():
        suffix = track.lstrip('_')
        hm = compute_heterotrait_monomethod(panel, dim_cols)
        with open(out_dir / f'73_heterotrait_monomethod_{suffix}.json',
                  'w', encoding='utf-8') as f:
            json.dump(hm, f, ensure_ascii=False, indent=2, default=str)
        # abs_corr 为 float → sig4 渲染 (4 位有效数字); 缺该对时回退 status 字符串原样保留。
        _hm_disp = {
            k: (sig4(v['abs_corr']) if 'abs_corr' in v else v.get('status'))
            for k, v in hm['pairs'].items()
        }
        logger.info(f"v3.5.1 stage 73 [跨构念/{suffix}] heterotrait-monomethod: {_hm_disp}")

    logger.info("⚠ 盘面 T=2 小样本 (mask 后约数十个 bank-year), 结果仅验证管道正确性, 非全量生产结论。")

    # ⑥ ⏱ 阶段计时 (墙钟; 纯日志)。
    try:
        logger.info(f"  ⏱ 阶段总耗时 (读盘+三轨判别效度+locus/collab+heterotrait+写盘): "
                    f"{sig4(time.time() - _t0)} 秒")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  计时打印失败 (不影响处理): {e}")


if __name__ == '__main__':
    main()
