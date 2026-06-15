"""news_process.pipeline.audit.lm_discriminant_validity — stage 39e.

v3.5.2 PR #4 — LM 4 子词典与 v3.5.1 lexical clarity / numerical intensity
的 panel-level 判别效度 (Discriminant Validity) 测试.

学术依据
--------
Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). A new criterion for
assessing discriminant validity in variance-based structural equation
modeling. Journal of the Academy of Marketing Science, 43(1), 115-135.
→ HTMT (Heterotrait-Monotrait ratio) 双 cutoff: 0.85 strict / 0.90 lenient

Cohen, J. (1960). A coefficient of agreement for nominal scales.
Educational and Psychological Measurement, 20(1), 37-46.

Cronbach, L. J. (1951). Coefficient alpha and the internal structure of
tests. Psychometrika, 16(3), 297-334.

测试指标对
----------
本 stage 测试 6 维构念间的判别效度:
    1. uncert_frac (LM uncertainty)
    2. litig_frac (LM litigious)
    3. constr_frac (LM constraining)
    4. modal_strong_frac (LM modal_strong)
    5. clarity_score (v3.5.1 A1)
    6. num_intensity (v3.5.1 A3)

预期: 6×6 HTMT 矩阵中 LM 4 子集互相 HTMT < 0.85, 且与 clarity / num_intensity
HTMT < 0.85 (判别效度通过).

输入 / 输出
-----------
输入: ``data/processed/40_panel_yearly.parquet`` (含 v3.5.1 + v3.5.2 全部列)
输出 (按 full / ctx / ss 三轨各写一份):
    ``eval_reports/39e_lm_htmt_matrix_{ctx,full,ss}.csv``   6×6 HTMT 矩阵
    ``eval_reports/39e_lm_permutation_{ctx,full,ss}.csv``   1000-rep permutation null (seed=42)
    (仅产上述 CSV — 与 core/schemas.py 登记的契约一致; 不单独落盘 Cohen κ /
     Cronbach α CSV, 亦不产 parquet; ss = 银行+金科同句共现轨, 列缺失时该轨优雅跳过)

实现状态
--------
``main()`` 与 ``permutation_null`` 已由 PR #14 集成完成 (非 stub): 依赖 v3.5.2
PR #3 (lm_non_sentiment) 输出的 panel 列存在; G-A1.2 准入门控
(panel HTMT < 0.85) 在该集成中验证。

白话: LM 词典给文本打了 4 类标签 (不确定性/诉讼/约束/强情态), 我们又造了
清晰度和数字密集度两个测度。这一步检查这 6 个测度两两相关是否都低于
0.85 — 低才说明它们各测各的、没有重复造轮子; 否则要请专家复核。
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
import pandas as pd

# sys.path 注入 (保证从任意 cwd 直跑本文件时可 import news_process 包)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "39e_lm_discriminant_validity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 6 个 indicator 列 (三轨各一组; main spec 用 _ctx 与 P1 v3.6.0 G3 对齐)
INDICATORS_CTX = [
    'uncert_frac_ctx',
    'litig_frac_ctx',
    'constr_frac_ctx',
    'modal_strong_frac_ctx',
    'mean_clarity_score_ctx',
    'mean_num_intensity_ctx',
]
INDICATORS_FULL = [
    'uncert_frac_full',
    'litig_frac_full',
    'constr_frac_full',
    'modal_strong_frac_full',
    'mean_clarity_score_full',
    'mean_num_intensity_full',
]
# 第三轨 ss = 银行+金科同句共现轨 (suffix _ss): 机械 _full→_ss swap (继承同 6 维度);
# ss 列尚未物化时下游 compute_htmt_matrix 缺列优雅跳过 (present < 2 → 空矩阵)。
INDICATORS_SS = [c.replace('_full', '_ss') for c in INDICATORS_FULL]

HTMT_STRICT = 0.85
HTMT_LENIENT = 0.90

# fix(omni-g-audit-family-05, 2026-06-11): 与 39d (lexical_discriminant_validity
# run_discriminant_validity min_n_articles=2, 修 R8-H2) 统一样本过滤口径.
MIN_N_ARTICLES = 2


def _apply_llm_valid_mask(panel: pd.DataFrame,
                          min_n_articles: int = MIN_N_ARTICLES) -> pd.DataFrame:
    """对 panel 施加 n_articles_llm_valid ≥ min_n_articles mask (与 39d 同口径).

    fix(omni-g-audit-family-05, 2026-06-11): 39d 与 39e 测同一对构念
    (clarity / num_intensity), 旧 39e 完全不 mask — 单篇文章 bank-year 的噪声
    测度进入 HTMT, 两份判别效度报告在不同样本上互不可比, 且 G-A1.2 门控
    (max HTMT < 0.85) 的判定样本与 39d 论文口径脱节. 现复用 39d 的过滤:
    优先 ``n_articles_llm_valid`` (判别效度测度建立在 LLM-valid 文章上),
    旧冻结 panel 缺该列则回退 ``n_articles``; 两列均缺 → 不过滤 (graceful).
    """
    mask_col = ('n_articles_llm_valid'
                if 'n_articles_llm_valid' in panel.columns else 'n_articles')
    if mask_col not in panel.columns:
        logger.warning(
            f"  39e mask: panel 缺 n_articles_llm_valid / n_articles 列, "
            f"不过滤 (与 39d 口径对齐失败, 结果与 39d 不可比)")
        return panel
    masked = panel.loc[panel[mask_col] >= min_n_articles].copy()
    logger.info(f"  39e: {mask_col} ≥ {min_n_articles} mask 后 {len(masked)} obs "
                f"(原 {len(panel)}; 与 39d R8-H2 口径统一)")
    return masked


def _offdiag_max(corr: pd.DataFrame) -> float:
    """对称矩阵的非对角最大值 (P0 修复 metric-audit 2026-06-02; CoW 安全).

    pandas 3.0 Copy-on-Write 下 DataFrame.values / corr().abs().values 返回**只读**
    数组, 此前 `np.fill_diagonal(df.values, np.nan)` 抛
    ``ValueError: assignment destination is read-only`` → stage 39e (默认启用的
    validation stage) 运行期崩溃. 改为在可写副本上置对角为 NaN 后取 nanmax,
    语义与旧 ``fill_diagonal + df.max().max()`` 完全一致 (off-diagonal 最大值).
    """
    arr = corr.to_numpy(copy=True)
    np.fill_diagonal(arr, np.nan)
    return float(np.nanmax(arr))


def compute_htmt_matrix(panel: pd.DataFrame, indicators: list[str]) -> pd.DataFrame:
    """k×k HTMT 矩阵 (Henseler et al. 2015 JAMS).

    HTMT(i, j) = corr(indicator_i, indicator_j) / sqrt(rel_i × rel_j),
    其中 rel_i 用 Cronbach α 估单维 reliability. 因 LM 子集 single-item,
    退化为 single-indicator HTMT = |corr(i, j)| / sqrt(1 × 1) = |corr|.

    Note:
        v3.5.1 stage 39d 已实现 multi-indicator HTMT 完整版; stage 39e 因
        LM 4 子集为 single-item, 用 abs(Pearson r) 作为 HTMT 简化估计.
        与 39d 互补不冲突.
    """
    present = [c for c in indicators if c in panel.columns]
    if len(present) < 2:
        logger.warning(f"  indicators 列不足 2 列存在 ({present}); HTMT 跳过")
        return pd.DataFrame()
    corr = panel[present].corr().abs()
    return corr


def compute_cronbach_alpha(panel: pd.DataFrame, indicators: list[str]) -> float:
    """跨 6 个 indicator 的 Cronbach α (Cronbach 1951)。"""
    present = [c for c in indicators if c in panel.columns]
    if len(present) < 2:
        return float('nan')
    sub = panel[present].dropna()
    k = len(present)
    if len(sub) < 2:
        return float('nan')
    var_items = sub.var(axis=0).sum()
    var_total = sub.sum(axis=1).var()
    if var_total == 0:
        return float('nan')
    return (k / (k - 1)) * (1 - var_items / var_total)


def permutation_null(panel: pd.DataFrame, indicators: list[str],
                     n_perm: int = 1000, seed: int = 42) -> pd.DataFrame:
    """HTMT 的 permutation null 分布 (按列随机洗牌)。

    实现仿 stage 39c::permutation_null: 对每个 indicator 列独立随机置换 n_perm 次,
    统计 HTMT 上限的 null 分布 (当前为串行循环, 非 n_jobs 并行)。

    fix(omni-g-audit-family-05, 2026-06-11) 两处口径修正:
    (a) 旧实现对含 NaN 的全样本列直接 ``rng.permutation`` — NaN 随值一起洗牌,
        破坏列间缺失对齐 → null 的有效 pairwise n 缩水, |corr| null 分布偏宽
        (p95 偏高, 方向保守但口径失准). 现观测与置换统一在 listwise-complete
        子样本上进行 (缺失模式固定, 观测/null 同域).
    (b) 披露: 行置换假设观测行独立, 未处理面板 bank 聚类 (within-bank 序列
        相关下 null 可能偏窄) — 写入输出 ``note`` 字段.
    """
    rng = np.random.default_rng(seed)
    present = [c for c in indicators if c in panel.columns]
    if len(present) < 2:
        return pd.DataFrame()
    # fix(omni-g-audit-family-05): listwise-complete 子样本 — 观测与 null 同域
    sub = panel[present].dropna()
    if len(sub) < 4:
        logger.warning(
            f"  permutation_null: listwise-complete 样本不足 ({len(sub)} 行 < 4); 跳过")
        return pd.DataFrame()
    # 观测 HTMT 上限 (对角置 NaN 后取全矩阵最大值), 作为下方 permutation null 的对比基准.
    obs_htmt = compute_htmt_matrix(sub, present)
    if obs_htmt.empty:
        return pd.DataFrame()
    obs_max = _offdiag_max(obs_htmt)  # P0 修复: CoW 安全 (不写只读 .values)
    # Layer 8.1 (v2.3-followup-v2 第 17 轮 user-request): perm 100 stub → n_perm reps.
    # 与 stage 39c/39d v3.5.0/v3.5.1 1000-rep 基线对齐 (Henseler-Ringle-
    # Sarstedt 2015 JAMS 建议 ≥ 500; 项目 stage 39d 用 1000 seed=42).
    perm_max = []
    for _ in range(n_perm):
        shuffled = sub.apply(lambda c: rng.permutation(c.values))
        h = shuffled.corr().abs()
        perm_max.append(_offdiag_max(h))  # P0 修复: CoW 安全
    p_emp = float((np.array(perm_max) >= obs_max).mean())
    return pd.DataFrame([{
        'obs_htmt_max': obs_max,  # P0 修复: off-diag max (obs_htmt 不再 in-place 改)
        'perm_htmt_max_mean': float(np.mean(perm_max)),
        'perm_htmt_max_p95': float(np.percentile(perm_max, 95)),
        'p_empirical': p_emp,
        'n_perm': len(perm_max),
        'n_listwise': int(len(sub)),
        'note': (f'{n_perm} reps (与 stage 39d 1000-rep 基线对齐); seed={seed}; '
                 f'obs 与 null 同 listwise-complete 域 (n={len(sub)}); '
                 f'披露: 行置换未处理面板 bank 聚类 (within-bank 相关下 null 或偏窄)'),
    }])


def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段 39e: LM Non-Sentiment 判别效度 (v3.5.2 PR #4)")
    logger.info("=" * 60)

    output_dir = CONFIG['paths']['output_dir']
    eval_dir = os.path.join(output_dir, '..', 'eval_reports')
    os.makedirs(eval_dir, exist_ok=True)

    panel_path = os.path.join(output_dir, '40_panel_yearly.parquet')
    if not os.path.exists(panel_path):
        logger.error(f"  panel 未找到: {panel_path}; 跳过 39e")
        sys.exit(0)

    panel = pd.read_parquet(panel_path)
    logger.info(f"  panel: {len(panel)} 行 × {len(panel.columns)} 列")

    # fix(omni-g-audit-family-05, 2026-06-11): 与 39d 统一 n_articles_llm_valid ≥ 2
    # 样本过滤 (HTMT / Cronbach α / permutation 全部在同一过滤后样本上计算)
    panel = _apply_llm_valid_mask(panel)

    # 三轨各跑一次 (full / ctx / ss; 与 v3.5.1 stage 39d 对齐)
    # ss = 银行+金科同句共现轨; INDICATORS_SS 列尚未物化时 compute_htmt_matrix
    # 内部 present < 2 → 返回空矩阵, 本轮 continue 优雅跳过 (镜像 ctx/full 缺列守卫)。
    for suffix, indicators in (
        ('ctx', INDICATORS_CTX),
        ('full', INDICATORS_FULL),
        ('ss', INDICATORS_SS),
    ):
        logger.info(f"  ── 轨道 {suffix} ──")
        htmt = compute_htmt_matrix(panel, indicators)
        if htmt.empty:
            logger.warning(f"  {suffix}: HTMT 跳过 (indicator 列缺失)")
            continue
        htmt_path = os.path.join(eval_dir, f'39e_lm_htmt_matrix_{suffix}.csv')
        htmt.to_csv(htmt_path)
        logger.info(f"    HTMT matrix → {htmt_path}")

        alpha = compute_cronbach_alpha(panel, indicators)
        logger.info(f"    Cronbach α = {alpha:.4f}")

        perm = permutation_null(panel, indicators)
        if not perm.empty:
            perm_path = os.path.join(eval_dir, f'39e_lm_permutation_{suffix}.csv')
            perm.to_csv(perm_path, index=False)
            logger.info(f"    Permutation → {perm_path}")

        # G-A1.2 准入门控判定
        max_htmt = _offdiag_max(htmt)  # P0 修复: CoW 安全
        logger.info(
            f"    G-A1.2 判定: max HTMT = {max_htmt:.4f} "
            f"({'PASS' if max_htmt < HTMT_STRICT else 'FAIL (need expert audit)'})"
        )

    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")


if __name__ == '__main__':
    main()
