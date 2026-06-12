"""news_process.pipeline.panel.encode_collab — v3.5.0 D2 cell decomposition + D4 dual-track residual.

Per the v3.5.0 Stage-3 augmentation plan §2.1 / §2.3 (历史方法学文档, 已随 docs/ 目录删除):
    D2 8-cell encoding: cell_id = subst*4 + locus*2 + collab + 1 ∈ {1..8}
        baseline (cell 1) = (0, 0, 0) = 实质性 × 底层技术 × 自主研发
    D4 cross-track residual signals (9 article-level + 18 panel-level frac/count
        + 3 n_articles_{dim}_bothvalid 覆盖披露列, omni 2026-06-11)

锚定文献:
    Angrist & Pischke (2009) Mostly Harmless Econometrics Ch.5 saturated regression (D2)
    Sun & Abraham (2021 JOE 225) cohort decomposition 类比 (D2)
    Loughran & McDonald (2011 JF) tone-vs-context differential 类比借用 (D4)
    Westphal & Zajac (2001 ASQ) decoupling 类比借用 narrative-context layer (D4)

v3.7.0 breaking note: 当 collab_mode 升级到 6-class (multi-class A1), CELL_LABEL_MAP
必须重写为 24 项. Backward-compat: v3.7.0 panel 同时保留 cell_id_v3_5_full + cell_id_v3_7_full,
旧列可在 v3.8.0 deprecate.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Optional

import pandas as pd

logger = logging.getLogger(__name__)

# v3.5.0 D2: 8-cell encoding (baseline=cell 1 三维全 0)
VALID_SUBST = {'实质性', '象征性'}
VALID_LOCUS = {'底层技术', '应用场景'}
VALID_COLLAB = {'自主研发', '外部协同'}

CELL_LABEL_MAP = {
    1: '实质性·底层技术·自主研发',
    2: '实质性·底层技术·外部协同',
    3: '实质性·应用场景·自主研发',
    4: '实质性·应用场景·外部协同',
    5: '象征性·底层技术·自主研发',
    6: '象征性·底层技术·外部协同',
    7: '象征性·应用场景·自主研发',
    8: '象征性·应用场景·外部协同',
}

# v3.5.0 D4: 9 article-level residual signals (3 dim × 3 signal)
DIMS_D4 = [
    ('subst',  'innovation_substantiveness', '实质性',   '象征性'),
    ('locus',  'innovation_locus',           '底层技术', '应用场景'),
    ('collab', 'innovation_collab_mode',     '自主研发', '外部协同'),
]


def _normalize_label(series: pd.Series) -> pd.Series:
    """Pre-normalize LLM label: strip whitespace + 全角空格 + all internal \\s.

    Per plan §2.1.1 F32: defense against trailing space / U+3000 / newline noise
    from stage 21 LLM output. NaN values preserve NaN through .str accessors.
    """
    # fix(omni-g-encode-collab-02, 2026-06-11): pandas 3.0 读 parquet/构造字符串列默认
    # 返回新 `str` dtype, `series.dtype == object` 恒 False → F32 脏标签清洗在生产路径
    # 静默 no-op。gate 放宽为 object 或 string dtype (legacy object / pandas3 str /
    # StringDtype 三者 .str accessor 均可用); 非字符串 dtype (如全 NaN float64) 仍原样返回。
    if series.dtype == object or pd.api.types.is_string_dtype(series):
        return (series.str.strip()
                      .str.replace('　', '', regex=False)
                      .str.replace(r'\s+', '', regex=True))
    return series


def _is_nan(v) -> bool:
    """None 或 float NaN 判定 (sidecar / median 锚点通用小工具)."""
    return v is None or (isinstance(v, float) and v != v)


def _both_valid_mask(full_norm: pd.Series, ctx_norm: pd.Series,
                     baseline: str, contrast: str) -> pd.Series:
    """D4 dim-level both_valid: 两轨归一化标签均为 canonical (baseline/contrast).

    fix(omni-g-encode-collab-02, 2026-06-11): 用 isin 白名单 (与 compute_cell_id 校验
    口径对齐) 取代 notna() — 非 canonical 但非 NaN 的脏标签不再计入 both_valid, 否则
    它只推高 disagree 而打破 invariant (ii) freerider+quietworker == disagree。
    derive_residual_signals 与 aggregate_d4_panel 共用本函数 ⇒ frac 分子/分母同域。
    """
    valid = (baseline, contrast)
    return full_norm.isin(valid) & ctx_norm.isin(valid)


def compute_cell_id(df: pd.DataFrame, track: str) -> pd.Series:
    """Compute article-level cell_id ∈ {1..8} for given track ('full' or 'ctx').

    Returns Int8 nullable Series:
        - Valid value 1..8 when all 3 dims have valid labels (per VALID_* sets, post-normalize)
        - pd.NA when any dim is NaN, dirty label, or column missing

    Per plan §2.1.1 (F27/F28/F32/B-NEW-2/m3):
        - Missing column guard returns all-NA Int8 (no KeyError)
        - Dirty label defense via _normalize_label + isin
        - .where(valid, pd.NA).astype('Int8') universal pandas/numpy compat
    """
    s_col = f'innovation_substantiveness_{track}'
    l_col = f'innovation_locus_{track}'
    c_col = f'innovation_collab_mode_{track}'

    missing = [c for c in (s_col, l_col, c_col) if c not in df.columns]
    if missing:
        logger.warning(
            f"v3.5.0 D2 cell_id_{track}: missing columns {missing}, returning all-NA Int8"
        )
        return pd.Series([pd.NA] * len(df), dtype='Int8', index=df.index)

    s_norm = _normalize_label(df[s_col])
    l_norm = _normalize_label(df[l_col])
    c_norm = _normalize_label(df[c_col])

    valid = (s_norm.isin(VALID_SUBST) &
             l_norm.isin(VALID_LOCUS) &
             c_norm.isin(VALID_COLLAB))

    s_bit = (s_norm == '象征性').astype('int8')
    l_bit = (l_norm == '应用场景').astype('int8')
    c_bit = (c_norm == '外部协同').astype('int8')

    cell = (s_bit * 4 + l_bit * 2 + c_bit + 1).where(valid, pd.NA).astype('Int8')
    return cell


def derive_residual_signals(df: pd.DataFrame) -> list[str]:
    """In-place add 9 article-level D4 residual indicators.

    **WARNING (CR-2)**: This function modifies ``df`` IN-PLACE. If columns
    ``{dim}_disagree`` / ``{dim}_freerider`` / ``{dim}_quietworker`` already exist
    (e.g., function called twice in dev workflow), they are **silently overwritten**.

    Per plan §2.3.2 (F C-NEW-4 invariants i/ii/iii):
        For each dim ∈ {subst, locus, collab}:
            {dim}_disagree    = (full != ctx) ∧ both_valid           [boolean]
            {dim}_freerider   = (full == baseline) ∧ (ctx == contrast) [boolean]
            {dim}_quietworker = (full == contrast) ∧ (ctx == baseline) [boolean]

    Invariants (provable by construction):
        (i)  freerider + quietworker ≤ 1 (mutually exclusive)
        (ii) freerider + quietworker == disagree (definitionally; 由 both_valid 的
             isin 白名单口径保证 — 非 canonical 标签不进 both_valid)
        (iii) NaN propagation: NaN **或非 canonical 脏标签** on either track ⇒
             all three False (not NaN)

    Returns: list of column names added (for downstream panel aggregation registry).
    """
    added_cols: list[str] = []
    for short, base, baseline, contrast in DIMS_D4:
        full_col = f'{base}_full'
        ctx_col = f'{base}_ctx'
        if full_col not in df.columns or ctx_col not in df.columns:
            logger.warning(
                f"v3.5.0 D4: missing track column(s) for {base}, "
                f"skipping {short}_(disagree|freerider|quietworker)"
            )
            continue

        full_norm = _normalize_label(df[full_col])
        ctx_norm = _normalize_label(df[ctx_col])
        # fix(omni-g-encode-collab-02, 2026-06-11): notna() → isin 白名单 (修 invariant ii)
        both_valid = _both_valid_mask(full_norm, ctx_norm, baseline, contrast)

        df[f'{short}_disagree'] = ((full_norm != ctx_norm) & both_valid)
        df[f'{short}_freerider'] = ((full_norm == baseline) & (ctx_norm == contrast))
        df[f'{short}_quietworker'] = ((full_norm == contrast) & (ctx_norm == baseline))
        added_cols.extend([
            f'{short}_disagree', f'{short}_freerider', f'{short}_quietworker'
        ])
    return added_cols


def aggregate_d2_panel(df: pd.DataFrame, panel: pd.DataFrame) -> dict:
    """Aggregate D2 8-cell counts onto bank-year panel.

    Per plan §2.1.2 + F-CR-cell-NA (R6 fix):
        - 8 cell-count columns: n_articles_cell_{1..8}_full
        - 1 NA bucket column: n_articles_cell_NA_full
          (articles 在 cell_id_full = NA, 通常 LLM 对 substantiveness/locus/
           collab_mode 三维之一失败)
        - main identity: ``n_articles >= Σ n_articles_cell_{1..8}_full``
          (逻辑必然性, n_articles 包含 cell_NA bucket; main_fail 仅在 n_articles
          < sum 时 > 0, 那才是真不一致 bug 而非 LLM 部分失败)
        - stricter completeness: ``n_articles == Σ cells_1..8 + n_articles_cell_NA_full``
          (na_bucket_fail > 0 → 上游 race condition)
        - cross identities (vs v3.4.0 _indep/_collab):
            n_articles_indep  >= n_articles_cell_{1,3,5,7}_full
            n_articles_collab >= n_articles_cell_{2,4,6,8}_full

    Returns dict with identity check failure counts (per plan §2.1.2 F27/C-NEW-2
    + R6 F-CR-cell-NA: na_bucket_fail / n_articles_cell_NA_total / na_bucket_pct).
    """
    # CR-3 / CR-4 (CRITICAL fix): 与 production encode.py 对齐 — panel 是 flat
    # DataFrame, target_bank + year 是**列**而非 MultiIndex (参 encode.py:666
    # `panel = df.groupby(['target_bank', 'year']).agg(...).reset_index()`).
    # df 也用 'target_bank' (encode.py:221 注释). 之前用 ['bank', 'year'] 是错误,
    # 单元测试 fixture 与 production 不一致 — 通过 real-data smoke test (CR-20) 发现.
    for required_col in ('target_bank', 'year'):
        if required_col not in panel.columns:
            raise KeyError(
                f"aggregate_d2_panel 要求 panel 含 '{required_col}' 列 "
                f"(production encode.py:666 约定 flat panel with target_bank/year columns); "
                f"got panel.columns starts with {list(panel.columns[:5])}"
            )
        if required_col not in df.columns:
            raise KeyError(
                f"aggregate_d2_panel 要求 df 含 '{required_col}' 列; "
                f"got df.columns starts with {list(df.columns[:5])}"
            )

    if 'cell_id_full' not in df.columns:
        logger.info("  v3.5.0 D2: cell_id_full not in df, skipping panel aggregation")
        # F-52: skip 路径返回 None 而非 0, 避免 "0 = validation passed" 误读
        return {'main_fail': None, 'indep_cross_fail': None, 'collab_cross_fail': None,
                'cell_aggregation_skipped': True,
                'skip_reason': 'cell_id_col_absent'}

    # 边界 F27 (修正): graceful skip 而非 raise — 测试 fixtures / 缺 LLM 列 / 极小 panel 安全
    # 仅当 cell_id_full 全 NA (LLM 输入列缺失或全 dirty label) 时跳过整 D2 panel 派生.
    if df['cell_id_full'].isna().all():
        # F-51 + F-50: 升级为 warning level, 提示 upstream stage 21 数据缺失第三维度
        # 这通常意味 stage 21 未在 v3.4.0+ 重跑 (innovation_collab_mode_* 列缺失).
        # 调用方应检查 cell_aggregation_skipped + skip_reason 而非依赖 main_fail.
        logger.warning(
            "  ⚠ v3.5.0 D2: cell_id_full 全 NA (LLM 输入列缺失或 dirty 全失败); "
            "通常源于 stage 21 未 post-v3.4.0 重跑产出 innovation_collab_mode_* 列. "
            "v3.5.0 D2 主 deliverable (8-cell decomposition) 在此条件下**不可用**. "
            "解决方案: 重跑 stage 21 with prompt v8 (含 collab_mode 维度)."
        )
        return {'main_fail': None, 'indep_cross_fail': None, 'collab_cross_fail': None,
                'cell_aggregation_skipped': True,
                'skip_reason': 'all_na_cell_id'}

    if panel.shape[0] == 0:
        logger.warning("  v3.5.0 D2: panel 空 (0 rows), 跳过 panel 8-cell 聚合")
        return {'main_fail': None, 'indep_cross_fail': None, 'collab_cross_fail': None,
                'cell_aggregation_skipped': True,
                'skip_reason': 'empty_panel'}

    if df.shape[0] < 1000:
        panel.attrs['D2_small_sample_warning'] = True
        logger.info(
            f"  v3.5.0 D2: small sample (df={df.shape[0]} articles < 1000); "
            "panel.attrs['D2_small_sample_warning'] = True; 继续聚合 (production threshold ≥ 100k)"
        )

    # Align groupby results to panel row order via MultiIndex (panel itself stays flat)
    panel_idx = pd.MultiIndex.from_frame(panel[['target_bank', 'year']])

    # F-CR-cell-NA (R6 fix): cell 聚合需与 panel.n_articles 同源 subset 计数。
    # encode.py:573 `n_articles = ('llm_vote_score_full', 'count')` 只数 LLM 总分
    # 非 NaN 的 articles. 直接 `df['cell_id_full'] == cell_id` 会把 LLM 总分失败但
    # cell_id 三维都合法的 articles 也计入 cells → Σ cells > n_articles → 假阳性
    # main_fail (实测 13/87 bank-years). 解决: cell aggregation 限定在与 n_articles
    # 同源 subset 上. 优先用 llm_vote_score_full (encode.py 计算后状态); 退化时复刻
    # encode.py:113-137 完整 invalid_mask 公式 (verified=False ∨ call_failure ∨
    # undefined ∨ sentiment_full 缺失 → invalid).
    if 'llm_vote_score_full' in df.columns:
        df_scored = df[df['llm_vote_score_full'].notna()].copy()
    elif 'llm_sentiment_full' in df.columns:
        invalid = pd.Series(False, index=df.index)
        if 'llm_call_failure_full' in df.columns:
            invalid = invalid | df['llm_call_failure_full'].fillna(0).astype(bool)
        if 'llm_undefined_full' in df.columns:
            invalid = invalid | df['llm_undefined_full'].fillna(0).astype(bool)
        if 'llm_verified_full' in df.columns:
            invalid = invalid | (~df['llm_verified_full'].fillna(False).astype(bool))
        invalid = invalid | df['llm_sentiment_full'].isna()
        df_scored = df[~invalid].copy()
    else:
        # 退化: 上游列全缺失时退回全 df (保留旧语义)
        df_scored = df

    for cell_id in range(1, 9):
        df_cell = df_scored[df_scored['cell_id_full'] == cell_id]
        col = f'n_articles_cell_{cell_id}_full'
        counts = (df_cell.groupby(['target_bank', 'year']).size()
                         .reindex(panel_idx, fill_value=0).astype('Int32'))
        panel[col] = counts.values

    # F-CR-cell-NA: 显式追踪 cell_id_full = NA 的 (LLM-scored) article 数 per (bank, year).
    # 该 bucket = LLM 总分成功 (在 n_articles 中) 但 substantiveness/locus/collab_mode
    # 任一维度失败的 articles. identity: n_articles = Σ cells_1..8 + n_articles_cell_NA_full.
    df_cell_na = df_scored[df_scored['cell_id_full'].isna()]
    na_counts = (df_cell_na.groupby(['target_bank', 'year']).size()
                           .reindex(panel_idx, fill_value=0).astype('Int32'))
    panel['n_articles_cell_NA_full'] = na_counts.values

    # F-CR-cell-NA: identity 改为 "逻辑必然性" 检查 `n_articles >= Σ cells 1..8`,
    # main_fail = 数 of rows where `n_articles < Σ cells` (才是真不一致 bug). 同时新增
    # 严格完整性公式 `n_articles == Σ cells + n_articles_cell_NA_full` 作为 stronger
    # check (na_bucket_fail), 任何时候都应 = 0 — 若不为 0 则上游 LLM 输出有 race condition.
    main_sum = sum(panel[f'n_articles_cell_{i}_full'] for i in range(1, 9))
    # metric-audit 2026-06-02 (encode-02 重构对齐): cells + NA 桶建在 LLM-valid 子集
    # (count 口径), 故恒等式 LHS 须同口径; 重构后 n_articles=物理 size → 用
    # n_articles_llm_valid (旧 panel 缺列回退 n_articles, 其即 count). 否则含 LLM 失败行
    # 的 bank-year 令 size != Σcells+NA → 误报"上游 race condition".
    _nac = 'n_articles_llm_valid' if 'n_articles_llm_valid' in panel.columns else 'n_articles'
    has_news = panel[_nac] > 0
    main_fail = int((panel.loc[has_news, _nac]
                     < main_sum.loc[has_news]).sum())
    na_bucket_fail = int((panel.loc[has_news, _nac]
                          != main_sum.loc[has_news]
                          + panel.loc[has_news, 'n_articles_cell_NA_full']).sum())

    # Cross identities (only if v3.4.0 二元后缀列存在); 改用 ">=" 同 main_fail 一致
    indep_cross_fail = 0
    collab_cross_fail = 0
    if 'n_articles_indep' in panel.columns:
        indep_sum = sum(panel[f'n_articles_cell_{i}_full'] for i in [1, 3, 5, 7])
        has_indep = panel['n_articles_indep'] > 0
        indep_cross_fail = int((panel.loc[has_indep, 'n_articles_indep']
                                < indep_sum.loc[has_indep]).sum())
    if 'n_articles_collab' in panel.columns:
        collab_sum = sum(panel[f'n_articles_cell_{i}_full'] for i in [2, 4, 6, 8])
        has_collab = panel['n_articles_collab'] > 0
        collab_cross_fail = int((panel.loc[has_collab, 'n_articles_collab']
                                 < collab_sum.loc[has_collab]).sum())

    # F-CR-cell-NA: 即便 main_fail / cross_fail 都 = 0, 仍报告 NA bucket 占比 (诊断信息)
    na_total = int(panel['n_articles_cell_NA_full'].sum())
    n_articles_total = int(panel.loc[has_news, _nac].sum())
    na_pct = (na_total / n_articles_total * 100) if n_articles_total > 0 else 0.0

    if main_fail > 0 or indep_cross_fail > 0 or collab_cross_fail > 0:
        logger.warning(
            f"  ✗ cell_id identity 失败 (n_articles < Σ cells 不可能成立): "
            f"main={main_fail}, indep_cross={indep_cross_fail}, "
            f"collab_cross={collab_cross_fail}"
        )
    elif na_bucket_fail > 0:
        logger.warning(
            f"  ⚠ cell_id NA bucket identity 失败 (上游数据 race condition?): "
            f"na_bucket_fail={na_bucket_fail}"
        )
    else:
        # 把 LLM partial failure 的诊断信息从 WARNING 降为 INFO (设计性预期)
        logger.info(
            f"  ✓ cell_id identity 通过 (n_articles_cell_NA_full bucket = "
            f"{na_total}/{n_articles_total} = {na_pct:.1f}% LLM 部分失败 articles)"
        )

    return {
        'main_fail': main_fail,
        'indep_cross_fail': indep_cross_fail,
        'collab_cross_fail': collab_cross_fail,
        'cell_aggregation_skipped': False,
        'na_bucket_fail': na_bucket_fail,
        'n_articles_cell_NA_total': na_total,
        'na_bucket_pct': na_pct,
    }


def aggregate_d4_panel(df: pd.DataFrame, panel: pd.DataFrame,
                       ctx_baseline_path: Optional[str] = None) -> dict:
    """Aggregate D4 residual signals onto bank-year panel.

    Per plan §2.3.3 + §2.3.4 (denominator semantics revised, omni 2026-06-11):
        18 panel columns: {dim}_{signal}_frac + n_articles_{dim}_{signal}
            (3 dim × 3 signal × 2 metric)
        + 3 coverage columns: n_articles_{dim}_bothvalid (论文披露 both_valid 覆盖率)
        *_frac = Σ signal / n_bothvalid — 分母为该维 both_valid (两轨 canonical 标签)
            文章数, 与分子同域; n_bothvalid == 0 → NaN (非假零)。
        Small-sample restriction: n_bothvalid < 5 → *_frac forced to NaN
            (valid 域门; 上游标签列缺失时回退 legacy 物理分母 + n_articles < 5 门)
        ctx coverage adaptive warning + d4_data_quality_flag str column (F6 + C-NEW-3)

    ctx_baseline_path: path to v3_4_0_ctx_coverage_baseline.json (per §9.10).
                       If None or missing, fallback to fixed 0.5 threshold with caveat.

    CR-6 note: coverage check uses `innovation_collab_mode_ctx` as canonical proxy
    (assumed lowest-coverage of 3 ctx dims because Hassan-2019 entity-context
    extraction is most variable on the most-recently-added v3.4.0 dim). For symmetric
    treatment, future versions could average across 3 ctx dims.

    CR-4 (CRITICAL fix): 与 aggregate_d2_panel 同样要求 panel 含 target_bank + year **列**
    (production flat panel, 非 MultiIndex; 参 encode.py:666 约定).
    """
    # CR-4: column invariant (与 aggregate_d2_panel 对称 — flat panel with target_bank/year cols)
    for required_col in ('target_bank', 'year'):
        if required_col not in panel.columns:
            raise KeyError(
                f"aggregate_d4_panel 要求 panel 含 '{required_col}' 列; "
                f"got panel.columns starts with {list(panel.columns[:5])}"
            )
        if required_col not in df.columns:
            raise KeyError(
                f"aggregate_d4_panel 要求 df 含 '{required_col}' 列"
            )

    panel_idx = pd.MultiIndex.from_frame(panel[['target_bank', 'year']])

    residual_frac_cols: list[str] = []
    has_residual = False
    # fix(omni-g-encode-collab-01, 2026-06-11): *_frac 分母改 both_valid 计数 (与分子同域)。
    # derive_residual_signals invariant (iii) 把任一轨缺失/脏标签的文章编为 False (非 NaN),
    # 旧实现 groupby.mean() 的分母=物理文章数 → 缺标签文章被静默计为"不分歧" (系统性下偏),
    # both_valid=0 的组输出假零 0.0。现: frac = Σ signal / n_bothvalid, n_bothvalid < 5
    # (含 ==0) → NaN (small-sample 门同步迁移到 valid 域); 另导出 n_articles_{dim}_bothvalid
    # 供论文披露覆盖率。上游标签列缺失 (无法重建 both_valid) 时回退 legacy 物理分母。
    fallback_frac_cols: list[str] = []
    for short, base, baseline, contrast in DIMS_D4:
        signal_cols = [f'{short}_{s}' for s in ('disagree', 'freerider', 'quietworker')
                       if f'{short}_{s}' in df.columns]
        if not signal_cols:
            continue
        has_residual = True

        full_col = f'{base}_full'
        ctx_col = f'{base}_ctx'
        bv_count = None
        if full_col in df.columns and ctx_col in df.columns:
            # 与 derive_residual_signals 共用 _both_valid_mask ⇒ 分母与分子可达域一致
            bv = _both_valid_mask(_normalize_label(df[full_col]),
                                  _normalize_label(df[ctx_col]),
                                  baseline, contrast)
            bv_count = (bv.groupby([df['target_bank'], df['year']]).sum()
                          .reindex(panel_idx, fill_value=0).astype('Int32'))
            panel[f'n_articles_{short}_bothvalid'] = bv_count.values
        else:
            logger.warning(
                f"  v3.5.0 D4: {base} 双轨源列缺失, {short}_*_frac 回退 legacy 物理分母 "
                "(both_valid 不可重建)"
            )

        for col in signal_cols:
            frac_col = f'{col}_frac'
            count_col = f'n_articles_{col}'
            # Use target_bank (production convention) + reindex to panel_idx for row alignment
            count_series = (df.groupby(['target_bank', 'year'])[col]
                              .sum().reindex(panel_idx, fill_value=0).astype('Int32'))
            panel[count_col] = count_series.values
            if bv_count is not None:
                denom = bv_count.astype('float64')
                # n_bothvalid < 5 (含 ==0 假零) → NaN
                frac_series = (count_series.astype('float64') / denom).where(denom >= 5)
                panel[frac_col] = frac_series.values
            else:
                mean_series = (df.groupby(['target_bank', 'year'])[col]
                                 .mean().reindex(panel_idx))
                panel[frac_col] = mean_series.values
                fallback_frac_cols.append(frac_col)
            residual_frac_cols.append(frac_col)

    if not has_residual:
        logger.info("  v3.5.0 D4: residual signal columns absent, skipping panel aggregation")
        return {'residual_skipped': True}

    # Small-sample restriction (修 m5 + C-NEW-3): 仅 legacy 回退列沿用物理 n_articles 门
    # (both_valid 路径已在上方用 valid 域门 n_bothvalid < 5)
    if fallback_frac_cols:
        small_mask = panel['n_articles'] < 5
        for col in fallback_frac_cols:
            panel.loc[small_mask, col] = pd.NA

    # ctx coverage 自适应警告 (修 C-NEW-3 + F6)
    quality_flag = 'ok'
    ctx_check_col = 'innovation_collab_mode_ctx'
    if ctx_check_col in df.columns:
        current_coverage = float(df[ctx_check_col].notna().mean())
        threshold_low = 0.5  # fallback
        baseline_loaded = False
        if ctx_baseline_path and os.path.exists(ctx_baseline_path):
            try:
                with open(ctx_baseline_path) as f:
                    baseline = json.load(f)
                threshold_low = float(baseline['mean']) - 2.0 * float(baseline['std'])
                baseline_loaded = True
            except (KeyError, ValueError, OSError) as e:
                logger.warning(
                    f"  v3.5.0 D4: failed to load ctx baseline {ctx_baseline_path}: {e}; "
                    "fallback threshold = 0.5"
                )
        if current_coverage < threshold_low:
            quality_flag = 'insufficient'
            logger.warning(
                f"  ⚠ ctx coverage {current_coverage:.2%} < "
                f"{'baseline-2σ' if baseline_loaded else 'fallback'} threshold "
                f"{threshold_low:.2%}; panel.attrs['D4_data_quality'] marked"
            )
            panel.attrs['D4_data_quality'] = 'insufficient_ctx_coverage'

    # F6: str column 持久化到 parquet/.dta, Stata 用户可见
    panel['d4_data_quality_flag'] = quality_flag

    return {
        'residual_skipped': False,
        'd4_data_quality_flag': quality_flag,
        'residual_frac_cols': residual_frac_cols,
    }


def apply_v3_5_0(df: pd.DataFrame, panel: pd.DataFrame,
                 ctx_baseline_path: Optional[str] = None) -> dict:
    """One-shot entry point: apply all v3.5.0 D2 + D4 derivations to df + panel.

    Called by encode.py::aggregate_panel after v3.4.0 collab_mode aggregation block.
    Returns aggregated diagnostics dict for audit log §A.
    """
    # article-level D2
    df['cell_id_full'] = compute_cell_id(df, 'full')
    df['cell_id_ctx'] = compute_cell_id(df, 'ctx')

    # article-level D4
    residual_cols = derive_residual_signals(df)

    # panel-level D2 8-cell + identities
    d2_diag = aggregate_d2_panel(df, panel)

    # panel-level D4 frac/count + d4_data_quality_flag
    d4_diag = aggregate_d4_panel(df, panel, ctx_baseline_path)

    return {
        'v3_5_0_cell_id_added': ['cell_id_full', 'cell_id_ctx'],
        'v3_5_0_residual_articles_added': residual_cols,
        'd2_identity': d2_diag,
        'd4_quality': d4_diag,
    }


# ============================================================================
# v3.5.1 A1 + A3 真双轨补强 (per stage3_v3_5_1 plan v0.3 §2.1.2 + §2.2.2).
# `apply_v3_5_1` 与 `apply_v3_5_0` **并存** (修 C2); v3.6.0 合并方案: 新建
# `apply_supplementation` 统一入口, v3.5.0 entry 保留 deprecation alias 至 v3.7.0.
# ============================================================================


def aggregate_clarity_panel(df: pd.DataFrame, panel: pd.DataFrame,
                            median_amb_d0: Optional[float] = None,
                            median_amb_d0_ctx: Optional[float] = None) -> dict:
    """v3.5.1 A1: 聚合 article 层 clarity 列到 bank-year panel (6 列).

    Per plan v0.3 §2.1.4 公式 (修 H2 + R8-H2 + R9-M3; 分母口径修订 omni 2026-06-11):
        mean_clarity_score_full[b,t] = Σ_valid w_i × clarity_score_full_i / Σ_valid w_i
        mean_frac_definite_full[b,t] = Σ_valid w_i × frac_definite_full_i / Σ_valid w_i
        frac_amb_articles_full[b,t]  = #{i: frac_ambiguous_full_i ≥ median_amb_d0}
                                       / n_clarity_valid_full   (n_clarity_valid ≥ 2 门)
        (同 ctx 双轨; frac_amb 分母 = 该轨 clarity 非缺失文章数, 与分子同域 —
         空文/零 token 文章 (tone_words 显式 NaN) 不再进物理分母造成系统性下偏;
         n_clarity_valid < 2 或 median 为 NaN (全 NaN 轨) → NaN 而非假零)

    Args:
        df: article-level DataFrame (含 clarity_* 双轨 article 列, 来自 stage 22).
        panel: bank-year panel DataFrame (含 target_bank + year).
        median_amb_d0: D0 frozen full 轨全样本中位数 (生产经 apply_v3_5_1 从 sidecar
            冻结值传入); if None, in-sample 计算 (首跑 freeze / 测试).
        median_amb_d0_ctx: D0 frozen ctx 轨中位数, 语义同上 (ctx 轨用自身分布阈值).

    Returns:
        dict: diagnostics + median_amb_d0 / median_amb_d0_ctx actual used.
    """
    for required_col in ('target_bank', 'year'):
        if required_col not in panel.columns or required_col not in df.columns:
            logger.warning(f"v3.5.1 A1: 缺 '{required_col}' 列, clarity panel 聚合跳过")
            return {'v3_5_1_clarity_added': [], 'median_amb_d0': float('nan'),
                    'median_amb_d0_ctx': float('nan')}

    # 检查 article 层 clarity 列存在性 (graceful)
    required_article_cols = [
        'clarity_frac_ambiguous_full', 'clarity_frac_definite_full',
        'clarity_clarity_score_full',
        'clarity_frac_ambiguous_ctx', 'clarity_frac_definite_ctx',
        'clarity_clarity_score_ctx',
    ]
    missing = [c for c in required_article_cols if c not in df.columns]
    if missing:
        logger.info(f"v3.5.1 A1: article 层 clarity 列缺 {missing}, 跳过 panel 聚合 (graceful)")
        return {'v3_5_1_clarity_added': [], 'median_amb_d0': float('nan'),
                'median_amb_d0_ctx': float('nan')}

    # D0 frozen median (修 H2 + R7-H1): 若未给, in-sample 算 (首跑 freeze);
    # 生产由 apply_v3_5_1 从 sidecar JSON 读冻结值传入 (fix(omni-known-open-2, 2026-06-11))
    if median_amb_d0 is None:
        median_amb_d0 = float(df['clarity_frac_ambiguous_full'].dropna().median())
        logger.info(f"v3.5.1 A1: D0 median_amb(full) 实测 = {median_amb_d0:.6f}")
    # fix(encode_collab-01): ctx 轨用 ctx 自身分布的 median 二值化, 不再套用 full 轨阈值
    if median_amb_d0_ctx is None:
        median_amb_d0_ctx = float(df['clarity_frac_ambiguous_ctx'].dropna().median())
        logger.info(f"v3.5.1 A1: D0 median_amb(ctx) 实测 = {median_amb_d0_ctx:.6f}")

    # weight = stage21 media_authority × herd_decay
    # fix(herd-ghost-01): full/ctx 双轨各配自己的 herd 权重 (Edwards 2001 measurement-treatment
    # matching), 不再让 ctx 轨借用 herd_weight_full。herd_weight_ctx 缺失时优雅回退 full。
    def _track_weight(track: str) -> pd.Series:
        wt = pd.Series(1.0, index=df.index)
        if 'media_authority_weight' in df.columns:
            wt = wt * df['media_authority_weight'].fillna(1.0)
        herd_col = f'herd_weight{track}'
        if herd_col in df.columns:
            wt = wt * df[herd_col].fillna(1.0)
        elif 'herd_weight_full' in df.columns:
            wt = wt * df['herd_weight_full'].fillna(1.0)
        return wt
    w_full = _track_weight('_full')
    w_ctx = _track_weight('_ctx')

    added_cols = []
    # 加 weighted columns 给 article level
    # 单次 assign 写入临时列, 避免逐列 insert 触发 pandas PerformanceWarning
    # fix(clarity-weighted-denom, metric-audit 2026-06-10): 加权均值分母须 mask 到各指标
    # valid 集, 否则 clarity 缺失文章的权重仍进物理分母 → Σ_valid(w·x)/Σ_all(w) 系统性下偏
    # (VW/MW/HW 同型未标记兄弟)。各指标(clarity/frac_definite × full/ctx)用自己的 valid 分母。
    df = df.assign(
        _w_clarity_full=df['clarity_clarity_score_full'] * w_full,
        _w_clarity_ctx=df['clarity_clarity_score_ctx'] * w_ctx,
        _w_def_full=df['clarity_frac_definite_full'] * w_full,
        _w_def_ctx=df['clarity_frac_definite_ctx'] * w_ctx,
        _wd_clarity_full=w_full.where(df['clarity_clarity_score_full'].notna()),
        _wd_clarity_ctx=w_ctx.where(df['clarity_clarity_score_ctx'].notna()),
        _wd_def_full=w_full.where(df['clarity_frac_definite_full'].notna()),
        _wd_def_ctx=w_ctx.where(df['clarity_frac_definite_ctx'].notna()),
        _w_full=w_full,
        _w_ctx=w_ctx,
    )

    agg = df.groupby(['target_bank', 'year']).agg(
        _sum_w_clarity_full=('_w_clarity_full', 'sum'),
        _sum_w_clarity_ctx=('_w_clarity_ctx', 'sum'),
        _sum_w_def_full=('_w_def_full', 'sum'),
        _sum_w_def_ctx=('_w_def_ctx', 'sum'),
        _sum_wd_clarity_full=('_wd_clarity_full', 'sum'),
        _sum_wd_clarity_ctx=('_wd_clarity_ctx', 'sum'),
        _sum_wd_def_full=('_wd_def_full', 'sum'),
        _sum_wd_def_ctx=('_wd_def_ctx', 'sum'),
        _sum_w_full=('_w_full', 'sum'),
        _sum_w_ctx=('_w_ctx', 'sum'),
        _n_articles=('_w_full', 'count'),
        # fix(omni-g-encode-collab-03, 2026-06-11): clarity-valid 计数 (count 自动跳 NaN),
        # 作 frac_amb_articles 分母 — 与分子 (s >= median).sum() 只可能数 valid 文章同域
        _n_clar_valid_full=('clarity_frac_ambiguous_full', 'count'),
        _n_clar_valid_ctx=('clarity_frac_ambiguous_ctx', 'count'),
        _n_amb_full=('clarity_frac_ambiguous_full',
                     lambda s: int((s >= median_amb_d0).sum())),
        _n_amb_ctx=('clarity_frac_ambiguous_ctx',
                    lambda s: int((s >= median_amb_d0_ctx).sum())),
    ).reset_index()

    # 派生 panel 列 (各指标用自己 valid-mask 的权重和作分母, 域与分子一致)
    agg['mean_clarity_score_full'] = agg['_sum_w_clarity_full'] / agg['_sum_wd_clarity_full'].replace(0, float('nan'))
    agg['mean_clarity_score_ctx'] = agg['_sum_w_clarity_ctx'] / agg['_sum_wd_clarity_ctx'].replace(0, float('nan'))
    agg['mean_frac_definite_full'] = agg['_sum_w_def_full'] / agg['_sum_wd_def_full'].replace(0, float('nan'))
    agg['mean_frac_definite_ctx'] = agg['_sum_w_def_ctx'] / agg['_sum_wd_def_ctx'].replace(0, float('nan'))

    # fix(omni-g-encode-collab-03, 2026-06-11): frac_amb_articles 分母改 clarity-valid
    # 计数 (刚修的加权均值 valid-mask 分母同型同步, 见 L529 注释理由)。旧分母 _n_articles
    # =物理篇数 → clarity 缺失 (空文/零 token, tone_words.py 显式 NaN) 文章进分母不进
    # 分子的系统性下偏。≥ 2 mask (修 R8-H2) 同步迁移到各轨 valid 计数; median 为 NaN
    # (该轨全 NaN) 时输出 NaN 而非 "s>=NaN 全 False" 的全员假零。
    mask_full = agg['_n_clar_valid_full'] >= 2
    mask_ctx = agg['_n_clar_valid_ctx'] >= 2
    agg['frac_amb_articles_full'] = agg['_n_amb_full'] / agg['_n_clar_valid_full'].where(mask_full)
    agg['frac_amb_articles_ctx'] = agg['_n_amb_ctx'] / agg['_n_clar_valid_ctx'].where(mask_ctx)
    if _is_nan(median_amb_d0):
        agg['frac_amb_articles_full'] = float('nan')
    if _is_nan(median_amb_d0_ctx):
        agg['frac_amb_articles_ctx'] = float('nan')

    out_cols = ['mean_clarity_score_full', 'mean_clarity_score_ctx',
                'mean_frac_definite_full', 'mean_frac_definite_ctx',
                'frac_amb_articles_full', 'frac_amb_articles_ctx']

    # idempotent: 先 drop panel 已有的 out_cols (避免 merge 后 _x/_y 后缀冲突)
    for c in out_cols:
        if c in panel.columns:
            del panel[c]

    # merge 回 panel
    keep = ['target_bank', 'year'] + out_cols
    panel_merged = panel.merge(agg[keep], on=['target_bank', 'year'], how='left')
    for c in out_cols:
        panel[c] = panel_merged[c].values
        added_cols.append(c)

    # cleanup
    for tmp in ('_w_clarity_full', '_w_clarity_ctx', '_w_def_full', '_w_def_ctx',
                '_w_full', '_w_ctx'):
        if tmp in df.columns:
            del df[tmp]

    return {'v3_5_1_clarity_added': added_cols, 'median_amb_d0': median_amb_d0,
            'median_amb_d0_ctx': median_amb_d0_ctx}


def aggregate_num_intensity_panel(df: pd.DataFrame, panel: pd.DataFrame) -> dict:
    """v3.5.1 A3: 聚合 article 层 num_intensity 列到 bank-year panel.

    句级 2 列 (mean_num_intensity_{full,ctx}) + 词级替代版 2 列
    (mean_num_intensity_word_{full,ctx}, §4.3, 2026-06-05 新增) = 共 4 列。
    Per plan v0.3 §2.2.4 公式: weighted mean by stage21 weights (媒体权威×herd)。
    """
    for required_col in ('target_bank', 'year'):
        if required_col not in panel.columns or required_col not in df.columns:
            return {'v3_5_1_num_intensity_added': []}

    if 'num_intensity_full' not in df.columns or 'num_intensity_ctx' not in df.columns:
        logger.info("v3.5.1 A3: num_intensity article 列缺, 跳过 panel 聚合 (graceful)")
        return {'v3_5_1_num_intensity_added': []}

    # fix(herd-ghost-01): full/ctx 双轨各配自己的 herd 权重 (与 clarity 聚合同口径)
    def _track_weight(track: str) -> pd.Series:
        wt = pd.Series(1.0, index=df.index)
        if 'media_authority_weight' in df.columns:
            wt = wt * df['media_authority_weight'].fillna(1.0)
        herd_col = f'herd_weight{track}'
        if herd_col in df.columns:
            wt = wt * df[herd_col].fillna(1.0)
        elif 'herd_weight_full' in df.columns:
            wt = wt * df['herd_weight_full'].fillna(1.0)
        return wt
    w_full = _track_weight('_full')
    w_ctx = _track_weight('_ctx')

    # word-level 替代版 (§4.3) 列是否就位 (graceful: 旧 parquet 无此列时仅聚句级版)
    has_word = ('num_intensity_word_full' in df.columns
                and 'num_intensity_word_ctx' in df.columns)

    # 单次 assign 写入临时列, 避免逐列 insert 触发 pandas PerformanceWarning
    # fix(numint-weighted-denom, metric-audit 2026-06-10): 加权均值分母须 mask 到各指标的
    # valid 集 (num_intensity 非 NaN), 否则空文本(A7 显式 NaN 保护)的权重仍进物理分母 →
    # Σ_valid(w·x)/Σ_all(w) 系统性下偏, 抵消 A7 的 NaN 语义。各指标用自己的 valid-mask 分母。
    assign_kwargs = dict(
        _w_ni_full=df['num_intensity_full'] * w_full,
        _w_ni_ctx=df['num_intensity_ctx'] * w_ctx,
        _wd_ni_full=w_full.where(df['num_intensity_full'].notna()),
        _wd_ni_ctx=w_ctx.where(df['num_intensity_ctx'].notna()),
        _w_full=w_full,
        _w_ctx=w_ctx,
    )
    if has_word:
        # 词级替代版加权分子 (与句级版同权重 w_full/w_ctx, 仅 article 分母从句数→词数)
        assign_kwargs['_w_niw_full'] = df['num_intensity_word_full'] * w_full
        assign_kwargs['_w_niw_ctx'] = df['num_intensity_word_ctx'] * w_ctx
        assign_kwargs['_wd_niw_full'] = w_full.where(df['num_intensity_word_full'].notna())
        assign_kwargs['_wd_niw_ctx'] = w_ctx.where(df['num_intensity_word_ctx'].notna())
    df = df.assign(**assign_kwargs)

    agg_kwargs = dict(
        _sum_w_ni_full=('_w_ni_full', 'sum'),
        _sum_w_ni_ctx=('_w_ni_ctx', 'sum'),
        _sum_wd_ni_full=('_wd_ni_full', 'sum'),
        _sum_wd_ni_ctx=('_wd_ni_ctx', 'sum'),
        _sum_w_full=('_w_full', 'sum'),
        _sum_w_ctx=('_w_ctx', 'sum'),
    )
    if has_word:
        agg_kwargs['_sum_w_niw_full'] = ('_w_niw_full', 'sum')
        agg_kwargs['_sum_w_niw_ctx'] = ('_w_niw_ctx', 'sum')
        agg_kwargs['_sum_wd_niw_full'] = ('_wd_niw_full', 'sum')
        agg_kwargs['_sum_wd_niw_ctx'] = ('_wd_niw_ctx', 'sum')
    agg = df.groupby(['target_bank', 'year']).agg(**agg_kwargs).reset_index()
    # 分母 = 各指标 valid-mask 后的权重和 (域与分子一致)
    swd_ni_full = agg['_sum_wd_ni_full'].replace(0, float('nan'))
    swd_ni_ctx = agg['_sum_wd_ni_ctx'].replace(0, float('nan'))
    agg['mean_num_intensity_full'] = agg['_sum_w_ni_full'] / swd_ni_full
    agg['mean_num_intensity_ctx'] = agg['_sum_w_ni_ctx'] / swd_ni_ctx

    out_cols = ['mean_num_intensity_full', 'mean_num_intensity_ctx']
    if has_word:
        # 兑现 §4.3: 词级数字密度 bank-year 加权均值 (分母词数, 对中文句读 sparse 稳健)
        swd_niw_full = agg['_sum_wd_niw_full'].replace(0, float('nan'))
        swd_niw_ctx = agg['_sum_wd_niw_ctx'].replace(0, float('nan'))
        agg['mean_num_intensity_word_full'] = agg['_sum_w_niw_full'] / swd_niw_full
        agg['mean_num_intensity_word_ctx'] = agg['_sum_w_niw_ctx'] / swd_niw_ctx
        out_cols += ['mean_num_intensity_word_full', 'mean_num_intensity_word_ctx']
    # idempotent: 先 drop panel 已有的 out_cols (避免 merge _x/_y 后缀冲突)
    for c in out_cols:
        if c in panel.columns:
            del panel[c]
    keep = ['target_bank', 'year'] + out_cols
    panel_merged = panel.merge(agg[keep], on=['target_bank', 'year'], how='left')
    for c in out_cols:
        panel[c] = panel_merged[c].values

    for tmp in ('_w_ni_full', '_w_ni_ctx', '_w_niw_full', '_w_niw_ctx', '_w_full', '_w_ctx'):
        if tmp in df.columns:
            del df[tmp]

    return {'v3_5_1_num_intensity_added': out_cols}


def apply_v3_5_1(df: pd.DataFrame, panel: pd.DataFrame,
                 prompt_v8_sha256: Optional[str] = None) -> dict:
    """v3.5.1 A1 + A3 panel 聚合一站入口 (与 apply_v3_5_0 并存, 修 C2).

    顺序: 读 sidecar 冻结 median → A1 clarity → A3 num_intensity → 写 sidecar JSON.

    Sidecar JSON path: ``data/processed/v3_5_1_constants.json`` (修 C1' + R7-H1
    双 anchor: prompt_v8_sha256 + stage21_last_run_timestamp).

    fix(omni-known-open-2, 2026-06-11) frozen-median 接线 (防泄漏机制): clarity 二值化
    阈值 median_amb_d0 / median_amb_d0_ctx 优先读 sidecar 已冻结值传入聚合; sidecar 不
    存在 (或锚值缺失/NaN) 则首跑 in-sample 计算并持久化, 后续跑一律读冻结值 — 阈值不再
    随每次重跑的样本组成漂移 (look-ahead / 全样本中位数泄漏防护, D0 freeze 语义)。

    Args:
        df: article-level DataFrame (含 clarity_* 6 双轨列 + num_intensity 双轨列).
        panel: bank-year panel DataFrame.
        prompt_v8_sha256: optional anchor (写入 sidecar).

    Returns:
        dict: {v3_5_1_clarity_added, v3_5_1_num_intensity_added, median_amb_d0, sidecar_path}.
    """
    import os
    from datetime import datetime, timezone

    sidecar_path = 'data/processed/v3_5_1_constants.json'
    # P0-B (2026-05-25): preserve-if-set — 若 caller 未显式传 prompt_v8_sha256
    # 但已有 sidecar 含非 null SHA, 保留旧值 (避免 stage 21 重跑无声 wipe
    # 已手动锚定的 SHA). 仅当 caller 显式传 SHA 时覆盖.
    # 审计扩展 (2026-05-29): median_amb_d0 同为 "D0 frozen 全样本中位数" 手动锚点
    # (CLAUDE.md 双 anchor); 与 SHA 同理, 当 in-sample 重算得 NaN / 空列表 (文章级
    # clarity 列缺失时早退) 时须保留既有锚值, 否则 run_pipeline_function 每次重跑
    # 都会把受跟踪的 frozen anchor 清成 NaN/空 (见 aggregate_clarity_panel 文档串)。
    # fix(omni-known-open-2, 2026-06-11): sidecar 读移到聚合**之前**, 冻结 median 真正
    # 接线进 aggregate_clarity_panel (此前每次重跑都 in-sample 重算, freeze 名存实亡)。
    existing_sha = None
    existing_median = None
    existing_median_ctx = None
    existing_clarity_cols = None
    existing_ni_cols = None
    if os.path.exists(sidecar_path):
        try:
            with open(sidecar_path, 'r', encoding='utf-8') as _f:
                _prev = json.load(_f)
            existing_sha = _prev.get('prompt_v8_sha256')
            existing_median = _prev.get('median_amb_d0')
            existing_median_ctx = _prev.get('median_amb_d0_ctx')
            existing_clarity_cols = _prev.get('a1_clarity_panel_cols')
            existing_ni_cols = _prev.get('a3_num_intensity_panel_cols')
        except Exception:  # noqa: BLE001
            pass

    # A1 clarity panel 聚合 (D0 frozen median: sidecar 有值用冻结值, 否则首跑 in-sample)
    frozen_median = existing_median if not _is_nan(existing_median) else None
    frozen_median_ctx = existing_median_ctx if not _is_nan(existing_median_ctx) else None
    clarity_diag = aggregate_clarity_panel(df, panel, median_amb_d0=frozen_median,
                                           median_amb_d0_ctx=frozen_median_ctx)

    # A3 num_intensity panel 聚合
    ni_diag = aggregate_num_intensity_panel(df, panel)

    # 写 sidecar JSON (修 C1' 序列化丢失 -> parquet/.dta 不保留 attrs)
    effective_sha = prompt_v8_sha256 if prompt_v8_sha256 is not None else existing_sha

    _recomputed_median = clarity_diag.get('median_amb_d0', float('nan'))
    effective_median = (
        _recomputed_median if not _is_nan(_recomputed_median)
        else (existing_median if not _is_nan(existing_median) else _recomputed_median)
    )
    _recomputed_median_ctx = clarity_diag.get('median_amb_d0_ctx', float('nan'))
    effective_median_ctx = (
        _recomputed_median_ctx if not _is_nan(_recomputed_median_ctx)
        else (existing_median_ctx if not _is_nan(existing_median_ctx)
              else _recomputed_median_ctx)
    )
    _recomputed_clarity = clarity_diag.get('v3_5_1_clarity_added', []) or []
    effective_clarity_cols = _recomputed_clarity or (existing_clarity_cols or [])
    _recomputed_ni = ni_diag.get('v3_5_1_num_intensity_added', []) or []
    effective_ni_cols = _recomputed_ni or (existing_ni_cols or [])
    try:
        os.makedirs(os.path.dirname(sidecar_path), exist_ok=True)
        sidecar = {
            'plan_version': 'v3.5.1',
            'median_amb_d0': effective_median,
            # fix(omni-known-open-2, 2026-06-11): ctx 轨阈值同步冻结 (ctx 用自身分布)
            'median_amb_d0_ctx': effective_median_ctx,
            'prompt_v8_sha256': effective_sha,
            'stage21_last_run_timestamp': datetime.now(timezone.utc).isoformat(),
            'a1_clarity_panel_cols': effective_clarity_cols,
            'a3_num_intensity_panel_cols': effective_ni_cols,
        }
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(sidecar, f, ensure_ascii=False, indent=2)
        logger.info(f"v3.5.1: sidecar JSON 写入 {sidecar_path}")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"v3.5.1: sidecar JSON 写入失败 (graceful): {e}")

    return {
        **clarity_diag,
        **ni_diag,
        'sidecar_path': sidecar_path,
    }


def apply_v3_5_2(df: pd.DataFrame, panel: pd.DataFrame) -> dict:
    """v3.5.2 PR #2/#3 panel-level aggregation for LM 4 subdicts + FLS.

    Closes CLAUDE.md 顶部声明 "Stage 22 _dual_analyze 真集成 LM+FLS → panel +10 列"
    在 panel 层实现 gap: stage 22 article-level 产出 8 LM cols + 2 FLS cols,
    但 encode.py 仅 apply_v3_5_0/v3_5_1, 无对应 v3_5_2 panel-agg → panel-level
    0 cols (O2 sample-run 实测发现).

    Aggregates 10 article-level columns to bank-year panel by simple mean:
        LM 4 subdicts × 2 tracks (full, ctx) = 8 panel cols:
            uncert_frac_{full,ctx} → uncert_frac_{full,ctx}_panel  (mean)
            litig_frac_{full,ctx}  → litig_frac_{full,ctx}_panel  (mean)
            constr_frac_{full,ctx} → constr_frac_{full,ctx}_panel (mean)
            modal_strong_frac_{full,ctx} → modal_strong_frac_{full,ctx}_panel (mean)
        FLS × 2 tracks = 2 panel cols:
            frac_fls_{full,ctx} → frac_fls_{full,ctx}_panel (mean)

    Per stata_export.py L285-290 这 10 panel col 已注册 core_patterns
    (即下游 Stata 已期待这些列存在).

    Args:
        df: article-level DataFrame (含 8 LM + 2 FLS article cols).
        panel: bank-year panel DataFrame (in-place add 10 cols).

    Returns:
        dict: {v3_5_2_lm_added, v3_5_2_fls_added, v3_5_2_skipped_reason}.
    """
    LM_KEYS = ('uncert', 'litig', 'constr', 'modal_strong')
    TRACKS = ('full', 'ctx')

    added_cols: list[str] = []
    skipped_cols: list[str] = []

    # Sanity check upstream columns
    needed = ['target_bank', 'year']
    for col in needed:
        if col not in df.columns:
            return {
                'v3_5_2_lm_added': [],
                'v3_5_2_fls_added': [],
                'v3_5_2_skipped_reason': f"article df 缺 '{col}' 列, 跳过 v3.5.2 panel-agg",
            }

    agg_dict: dict[str, tuple[str, str]] = {}

    # LM 4 subdicts × 2 tracks
    for k in LM_KEYS:
        for track in TRACKS:
            src_col = f'{k}_frac_{track}'
            dst_col = src_col  # 与 stata_export.py core_patterns 一致
            if src_col in df.columns:
                agg_dict[dst_col] = (src_col, 'mean')
                added_cols.append(dst_col)
            else:
                skipped_cols.append(src_col)

    # FLS × 2 tracks
    for track in TRACKS:
        src_col = f'frac_fls_{track}'
        dst_col = src_col
        if src_col in df.columns:
            agg_dict[dst_col] = (src_col, 'mean')
            added_cols.append(dst_col)
        else:
            skipped_cols.append(src_col)

    if not agg_dict:
        return {
            'v3_5_2_lm_added': [],
            'v3_5_2_fls_added': [],
            'v3_5_2_skipped_reason': f"article df 缺所有 LM/FLS 源列 ({skipped_cols[:3]}...), 跳过",
        }

    # Aggregate to bank-year (simple mean of article-level frac)
    agg_panel = (
        df.groupby(['target_bank', 'year'], as_index=False)
        .agg(**agg_dict)
    )

    # Merge into existing panel (append cols on key match)
    # fix(omni-g-encode-collab-04, 2026-06-11): idempotent pre-drop — 镜像 clarity/
    # num_intensity 聚合的同款防护; 否则 panel 已含同名列时 (二次调用/增量重编码)
    # merge 默认 suffixes 产生 *_x/*_y 幻影列双双入 panel, 未后缀陈旧原列保旧值,
    # 下游 stata_export 按精确列名抓到陈旧值。
    for c in added_cols:
        if c in panel.columns:
            del panel[c]
    panel_pre_cols = set(panel.columns)
    merged = panel.merge(agg_panel, on=['target_bank', 'year'], how='left')
    new_cols = [c for c in merged.columns if c not in panel_pre_cols]

    # In-place column add on panel (caller-passed DataFrame)
    for c in new_cols:
        panel[c] = merged[c].values

    lm_added = [c for c in added_cols if any(c.startswith(k) for k in LM_KEYS)]
    fls_added = [c for c in added_cols if 'fls' in c]

    return {
        'v3_5_2_lm_added': lm_added,
        'v3_5_2_fls_added': fls_added,
        'v3_5_2_skipped_reason': None,
    }
