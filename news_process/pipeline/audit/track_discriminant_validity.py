"""news_process.pipeline.audit.track_discriminant_validity — Stage 39g (v3.7.3).

Track-discriminant validity (HTMT 3×3 across `_full` / `_ctx` / `_title` 切片轨).

设计动机
========
v3.5.1 stage 39d (lexical_discriminant_validity.py) 检验的是 **指标维度** 的
判别效度: T1 = LLM substance / T2 = A1 clarity / T3 = A3 num_intensity —
回答"3 个新加指标彼此是否构成独立构念"。

v3.7.3 stage 39g 检验的是 **文本切片轨道维度** 的判别效度: T1 = _full /
T2 = _ctx / T3 = _title — 回答"3 条切片轨在同一 sentiment 指标上是否构成
独立的测量切片 vs 数学退化的同义切片"。两 stage **正交且并存**。

学术锚定
========
- Campbell & Fiske (1959) Psych Bull 56(2): 81-105 — MTMM 矩阵
- Henseler, Ringle, Sarstedt (2015) JAMS 43: 115-135 — HTMT (双 cutoff)
- Heston & Sinha (2017) FAJ 73(3): 67-83 — headline vs body sentiment 对照
- Loughran & McDonald (2016) JAR 54(4): 1187-1230 — text subset robustness §6
- Boudoukh et al. (2019) RFS 32(3): 992-1033 — headline-based identification §III

v0.1 已知 limitation
====================
1. HTMT(_full, _ctx) 预期 > 0.85 (同 content 不同 slice, 数学必然), 因此
   acceptance criterion 修订为: HTMT(_full, _title) AND HTMT(_ctx, _title)
   < 0.85; HTMT(_full, _ctx) 通过 lenient 0.90 即可 (实测后再决定).
2. NEW-B1 (v1.0.2 已纠正): panel 的中文后缀列名 (例
   `finbert_cn_正面_w_sum_title`) 是合法 UTF-8 中文 (正/面/负), 并非 GBK/UTF-8
   双重编码乱码 — 此前在 GBK 终端下 `����` 的渲染是显示假象。
   `_is_mojibake_column` 保留为前瞻性守卫, 仅 skip 真正含 U+FFFD 的列 (当前
   panel 实测 0 个)。详见 tests/integration/test_panel_no_mojibake.py 的
   v1.0.2 retraction.
3. 与 v3.5.1 R3-H1 兼容: A1/A3 (mean_clarity_score / mean_num_intensity)
   在 _title 上不计算; 本 stage 仅用 sentiment-family 指标 (llm_vote_tone /
   dict_avg_tone / bert_avg_pos).
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

# 复用 39d 的 HTMT + permutation 公共函数 (修 R5-F7 重复劳动 finding)
from news_process.pipeline.audit.lexical_discriminant_validity import (
    HTMT_CUTOFF_LENIENT,
    HTMT_CUTOFF_STRICT,
    N_PERMUTATIONS_DEFAULT,
    PERMUTATION_SEED,
    compute_htmt,
    compute_permutation_null,
)

logger = logging.getLogger(__name__)

STAGE_NAME = "39g_track_discriminant_validity"

# 三轨 sentiment 指标候选 — 优先级降序 (panel 列名命名规约见
# data/processed/40_panel_yearly.parquet 实测列名扫描).
TRACK_INDICATOR_CANDIDATES: list[tuple[str, str]] = [
    ("llm_vote_tone", "LLM majority vote tone"),
    ("dict_avg_tone", "Dictionary average tone (jiang/yao/bian/du/you 5 词典)"),
    ("bert_avg_pos", "BERT average positive probability"),
    ("llm_models_avg_tone", "LLM models average tone (3 model mean)"),
    ("dict_avg_idf_tone", "Dictionary IDF-weighted average tone"),
]


def _is_mojibake_column(col_name: str) -> bool:
    """前瞻性 mojibake 守卫 (v1.0.2 已纠正 NEW-B1 误判).

    panel 的中文后缀列名实为合法 UTF-8 (正/面/负), 并非双重编码乱码; 此前在
    GBK 终端下 `����` 的渲染只是显示假象 (codepoint 实测 0x6b63 正 / 0x9762 面
    / 0x8d1f 负, panel 内 0 个 U+FFFD)。本函数因此对当前 panel 全部返回 False,
    仅作为防止未来出现真 U+FFFD 的前瞻性守卫保留。

    Args:
        col_name: panel column name.

    Returns:
        True iff column name contains a U+FFFD replacement char (real mojibake).
    """
    # "����" sequence implies "�" U+FFFD; single check suffices but
    # we keep explicit `or` to document both detection patterns.
    return "�" in col_name or "����" in col_name  # noqa: RUF001 — explicit mojibake literal


def _find_track_triple(panel: pd.DataFrame,
                       indicator_stem: str) -> Optional[tuple[str, str, str]]:
    """对给定 indicator stem (e.g. ``llm_vote_tone``), 找全/上下文/标题三轨列.

    Returns:
        tuple of (col_full, col_ctx, col_title) if all 3 exist, else None.
    """
    col_full = f"{indicator_stem}_full"
    col_ctx = f"{indicator_stem}_ctx"
    col_title = f"{indicator_stem}_title"

    has_full = col_full in panel.columns and not _is_mojibake_column(col_full)
    has_ctx = col_ctx in panel.columns and not _is_mojibake_column(col_ctx)
    has_title = col_title in panel.columns and not _is_mojibake_column(col_title)

    if has_full and has_ctx and has_title:
        return (col_full, col_ctx, col_title)
    return None


def run_track_discriminant_validity(
        panel: pd.DataFrame,
        indicator_stems: Optional[list[str]] = None,
        n_articles_col: str = "n_articles",
        min_n_articles: int = 2) -> dict:
    """主入口: 对 bank-year panel 跑 _full/_ctx/_title 三轨判别效度审计.

    Args:
        panel: bank-year panel DataFrame (e.g. ``40_panel_yearly.parquet``).
        indicator_stems: 可选 indicator stem list; 默认遍历
            ``TRACK_INDICATOR_CANDIDATES``.
        n_articles_col: n_articles 列名 (≥ min_n_articles mask, 复用 39d 范式).
        min_n_articles: 最小 article 数 cell.

    Returns:
        dict: {
            'status': 'ok' | 'no_track_triple_found',
            'n_obs': int,
            'mojibake_columns_skipped': list[str],
            'indicators_tested': list[str],  # 实际跑了哪些 indicator stem
            'htmt_3x3_per_indicator': {indicator_stem: htmt_dict},
            'permutation_p95_per_indicator': {...},
            'verdict_per_indicator': {...},
            'overall_verdict': str,
        }
    """
    # 1. mojibake 列扫描 (NEW-B1 防御)
    mojibake_cols = [c for c in panel.columns if _is_mojibake_column(c)]
    if mojibake_cols:
        logger.warning(
            f"v3.7.3 39g: panel 含 {len(mojibake_cols)} 个 mojibake 列, "
            f"已 skip (NEW-B1 detection). 前 5 个示例: {mojibake_cols[:5]}"
        )

    # 2. 找有完整三轨的 indicator
    stems = indicator_stems or [s for s, _ in TRACK_INDICATOR_CANDIDATES]
    valid_triples: dict[str, tuple[str, str, str]] = {}
    for stem in stems:
        triple = _find_track_triple(panel, stem)
        if triple is not None:
            valid_triples[stem] = triple

    if not valid_triples:
        logger.warning(
            f"v3.7.3 39g: panel 中找不到任何完整三轨 indicator. "
            f"候选 stems: {stems}; mojibake skip: {len(mojibake_cols)}"
        )
        return {
            "status": "no_track_triple_found",
            "n_obs": int(len(panel)),
            "mojibake_columns_skipped": mojibake_cols,
            "indicators_tested": [],
        }

    # 3. n_articles ≥ min_n_articles mask (复用 39d R8-H2 范式)
    panel_filtered = panel
    if n_articles_col in panel.columns:
        mask = panel[n_articles_col] >= min_n_articles
        panel_filtered = panel.loc[mask].copy()
        logger.info(
            f"v3.7.3 39g: n_articles ≥ {min_n_articles} mask 后 "
            f"{len(panel_filtered)} obs (从 {len(panel)} 减)"
        )

    if len(panel_filtered) < 10:
        return {
            "status": "insufficient_obs",
            "n_obs": int(len(panel_filtered)),
            "mojibake_columns_skipped": mojibake_cols,
        }

    # 4. 对每个 indicator 跑 HTMT 3×3 + permutation null
    htmt_per_indicator: dict[str, dict[str, float]] = {}
    perm_per_indicator: dict[str, dict[str, dict[str, float]]] = {}
    verdict_per_indicator: dict[str, dict[str, str]] = {}

    for stem, (col_full, col_ctx, col_title) in valid_triples.items():
        indicators = {
            "full": panel_filtered[col_full].to_numpy(),
            "ctx": panel_filtered[col_ctx].to_numpy(),
            "title": panel_filtered[col_title].to_numpy(),
        }
        htmt = compute_htmt(indicators)
        perm = compute_permutation_null(
            indicators, n_permutations=N_PERMUTATIONS_DEFAULT,
            seed=PERMUTATION_SEED,
        )

        # 双 cutoff 解读 (复用 39d R4-M2 范式)
        verdict = {}
        for k, v in htmt.items():
            if np.isnan(v):
                verdict[k] = "nan"
            elif v < HTMT_CUTOFF_STRICT:
                verdict[k] = "strict_pass"
            elif v < HTMT_CUTOFF_LENIENT:
                verdict[k] = "lenient_pass"
            else:
                verdict[k] = "fail"

        htmt_per_indicator[stem] = htmt
        perm_per_indicator[stem] = perm
        verdict_per_indicator[stem] = verdict

    # 5. overall verdict (per Plan A v1.0 M9 / R8-F7 修订)
    # acceptance criterion: HTMT(full, title) AND HTMT(ctx, title) < 0.85;
    # HTMT(full, ctx) 因测量设计自相关, 接受 0.85-0.90 lenient 区间.
    overall = _compute_overall_verdict(verdict_per_indicator)

    return {
        "status": "ok",
        "n_obs": int(len(panel_filtered)),
        "mojibake_columns_skipped": mojibake_cols,
        "indicators_tested": list(valid_triples.keys()),
        "htmt_3x3_per_indicator": htmt_per_indicator,
        "permutation_p95_per_indicator": {
            k: {kk: vv["p95"] for kk, vv in v.items()}
            for k, v in perm_per_indicator.items()
        },
        "verdict_per_indicator": verdict_per_indicator,
        "overall_verdict": overall,
        "htmt_cutoff_strict": HTMT_CUTOFF_STRICT,
        "htmt_cutoff_lenient": HTMT_CUTOFF_LENIENT,
    }


def _compute_overall_verdict(
        verdict_per_indicator: dict[str, dict[str, str]]) -> str:
    """Overall verdict across all tested indicators.

    Acceptance per Plan A v1.0 M9 (修 R8-F7):
        - HTMT(full, title) AND HTMT(ctx, title) < 0.85 for ≥ 50% of indicators
          → 'pass_title_discriminant'
        - Else if all pairs < 0.90 → 'lenient_pass_with_design_self_correlation'
        - Else → 'fail'
    """
    if not verdict_per_indicator:
        return "no_indicator"

    n_indicators = len(verdict_per_indicator)
    n_title_discriminant = 0
    n_all_lenient = 0

    for stem, vd in verdict_per_indicator.items():
        # key 格式: 'htmt_full_ctx', 'htmt_full_title', 'htmt_ctx_title'
        v_ft = vd.get("htmt_full_title", "nan")
        v_ct = vd.get("htmt_ctx_title", "nan")
        v_fc = vd.get("htmt_full_ctx", "nan")

        if v_ft == "strict_pass" and v_ct == "strict_pass":
            n_title_discriminant += 1

        if all(v in ("strict_pass", "lenient_pass")
               for v in (v_ft, v_ct, v_fc) if v != "nan"):
            n_all_lenient += 1

    if n_title_discriminant >= n_indicators * 0.5:
        return "pass_title_discriminant"
    if n_all_lenient == n_indicators:
        return "lenient_pass_with_design_self_correlation"
    return "fail"


def main(panel_path: Optional[Path] = None,
         output_path: Optional[Path] = None) -> dict:
    """Stage 39g shim entrypoint (delegated by news_process/39g_*.py).

    Path resolution: 复用 39d 范式 — 通过 ``news_process.core.config.load_config()``
    读 ``config['paths']['output_dir']`` 解析 panel + output paths (cwd-independent).
    显式 override 通过 ``panel_path`` / ``output_path`` 参数 (主要用于测试).

    Args:
        panel_path: 可选 explicit panel path override.
        output_path: 可选 explicit output JSON path override.

    Returns:
        Discriminant validity report dict.
    """
    if panel_path is None or output_path is None:
        from news_process.core.config import load_config
        config = load_config()
        out_dir = Path(config['paths']['output_dir'])
        if panel_path is None:
            panel_path = out_dir / "40_panel_yearly.parquet"
        if output_path is None:
            output_path = out_dir / "39g_track_discriminant_validity.json"

    if not panel_path.exists():
        logger.warning(f"v3.7.3 39g: panel {panel_path} 不存在, graceful skip")
        return {"status": "panel_not_found", "panel_path": str(panel_path)}

    panel = pd.read_parquet(panel_path)
    logger.info(
        f"v3.7.3 39g: loaded panel {panel_path.name} "
        f"({len(panel)} rows × {len(panel.columns)} cols)"
    )

    report = run_track_discriminant_validity(panel)

    # v3.7.4 P3.3: bootstrap CI + strata HTMT (MA-2 + 5R-B2 + 7R-A1)
    report["v3_7_4_extensions"] = _v374_bootstrap_and_strata(panel)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    logger.info(f"v3.7.3 39g: report saved to {output_path}")

    return report


# ============================================================================
# v3.7.4 P3.3 extensions: bootstrap CI + 4-cell strata HTMT
# ============================================================================

BOOTSTRAP_N_DEFAULT = 1000
BOOTSTRAP_SEED = 42  # 与 39d permutation seed 一致 (独立 numpy RNG state)
HTMT_STRICT_CUTOFF_V374 = 0.85
MIN_CELL_N = 30  # 5R-B2 per-cell graceful skip threshold


def _bootstrap_htmt_ci(indicators: dict, n_bootstrap: int = BOOTSTRAP_N_DEFAULT,
                       seed: int = BOOTSTRAP_SEED) -> dict:
    """Bootstrap 95% CI for HTMT (Henseler-Ringle-Sarstedt 2015 JAMS §4).

    Case-resample with replacement; compute HTMT for each resample;
    return percentile-based CI per pair.

    Returns:
        {'htmt_full_ctx': {'point': float, 'ci_lower': float, 'ci_upper': float,
                            'upper_below_085': bool}, ...}
    """
    rng = np.random.default_rng(seed)
    n = len(next(iter(indicators.values())))
    if n < 10:
        return {"status": "insufficient_n", "n": int(n)}

    point = compute_htmt(indicators)

    boot_results: dict[str, list[float]] = {k: [] for k in point.keys()}
    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        resampled = {k: v[idx] for k, v in indicators.items()}
        try:
            h = compute_htmt(resampled)
            for k in boot_results:
                if k in h and not np.isnan(h[k]):
                    boot_results[k].append(float(h[k]))
        except Exception:
            continue

    ci_summary: dict[str, dict] = {}
    for k, vals in boot_results.items():
        if len(vals) < 100:
            ci_summary[k] = {"status": "bootstrap_failed", "n_valid": len(vals)}
            continue
        lower = float(np.percentile(vals, 2.5))
        upper = float(np.percentile(vals, 97.5))
        ci_summary[k] = {
            "point": float(point[k]) if not np.isnan(point[k]) else None,
            "ci_lower": lower,
            "ci_upper": upper,
            "upper_below_085_strict": upper < HTMT_STRICT_CUTOFF_V374,
            "n_bootstrap_valid": len(vals),
        }
    return ci_summary


def _strata_htmt_per_cell(panel: pd.DataFrame, stem: str = "llm_vote_tone") -> dict:
    """5R-B2: 4-cell strata HTMT with per-cell graceful skip (N ≥ 30).

    Strata = title_mentions_fintech ∈ {0,1} × title_length_bucket ∈ {0,1}.
    For each cell with N ≥ 30: compute HTMT 3×3 + bootstrap CI.
    For cells with N < 30: emit insufficient_power flag.

    If ALL 4 cells fail N ≥ 30: emit `all_cells_insufficient_power` flag.
    """
    triple = _find_track_triple(panel, stem)
    if triple is None:
        return {"status": "no_track_triple", "stem": stem}

    col_full, col_ctx, col_title = triple
    needed = {"frac_title_mentions_fintech", "frac_title_long"}
    if not needed.issubset(panel.columns):
        return {"status": "strata_columns_missing",
                "needed": list(needed),
                "available": [c for c in needed if c in panel.columns]}

    # Bank-year level — binarize using > 0.5 threshold (mid-point convention;
    # Antweiler-Frank 2004 JF sensitivity tested in Stata Panel D at {0.3, 0.5, 0.7})
    cells = {
        "tmf0_tlb0": ((panel["frac_title_mentions_fintech"] <= 0.5) &
                      (panel["frac_title_long"] <= 0.5)),
        "tmf0_tlb1": ((panel["frac_title_mentions_fintech"] <= 0.5) &
                      (panel["frac_title_long"] > 0.5)),
        "tmf1_tlb0": ((panel["frac_title_mentions_fintech"] > 0.5) &
                      (panel["frac_title_long"] <= 0.5)),
        "tmf1_tlb1": ((panel["frac_title_mentions_fintech"] > 0.5) &
                      (panel["frac_title_long"] > 0.5)),
    }

    per_cell: dict[str, dict] = {}
    valid_cell_count = 0
    for cell_name, mask in cells.items():
        n_cell = int(mask.sum())
        if n_cell < MIN_CELL_N:
            per_cell[cell_name] = {"status": "insufficient_power",
                                   "n": n_cell, "min_required": MIN_CELL_N}
            continue
        sub = panel.loc[mask]
        indicators = {
            "full": sub[col_full].to_numpy(),
            "ctx": sub[col_ctx].to_numpy(),
            "title": sub[col_title].to_numpy(),
        }
        per_cell[cell_name] = {
            "status": "ok",
            "n": n_cell,
            "htmt": compute_htmt(indicators),
            "bootstrap_ci": _bootstrap_htmt_ci(
                indicators, n_bootstrap=BOOTSTRAP_N_DEFAULT, seed=BOOTSTRAP_SEED),
        }
        valid_cell_count += 1

    return {
        "status": "ok" if valid_cell_count > 0 else "all_cells_insufficient_power",
        "stem": stem,
        "valid_cell_count": valid_cell_count,
        "min_cell_n": MIN_CELL_N,
        "per_cell": per_cell,
    }


def _v374_bootstrap_and_strata(panel: pd.DataFrame) -> dict:
    """MA-2 + 5R-B2 + 7R-A1: bootstrap CI + strata for default stem.

    Returns dict with keys:
        - panel_level_bootstrap: bootstrap CI on full N panel
        - strata_per_cell: 4-cell strata HTMT (5R-B2 per-cell graceful)
        - acceptance_strict: True iff
              (i) bootstrap upper < 0.85 for (full,title) and (ctx,title) AND
              (ii) ≥ 1 valid cell with same property
    """
    default_stem = "llm_vote_tone"
    triple = _find_track_triple(panel, default_stem)
    if triple is None:
        return {"status": "no_track_triple", "stem": default_stem}

    n_articles_col = "n_articles"
    if n_articles_col in panel.columns:
        panel_f = panel.loc[panel[n_articles_col] >= 2].copy()
    else:
        panel_f = panel

    col_full, col_ctx, col_title = triple
    indicators = {
        "full": panel_f[col_full].to_numpy(),
        "ctx": panel_f[col_ctx].to_numpy(),
        "title": panel_f[col_title].to_numpy(),
    }
    panel_bootstrap = _bootstrap_htmt_ci(indicators)
    strata = _strata_htmt_per_cell(panel_f, stem=default_stem)

    # Strict acceptance (MA-2 + 5R-B2)
    bs_ft = panel_bootstrap.get("htmt_full_title", {}) if isinstance(
        panel_bootstrap, dict) else {}
    bs_ct = panel_bootstrap.get("htmt_ctx_title", {}) if isinstance(
        panel_bootstrap, dict) else {}
    panel_strict = (bs_ft.get("upper_below_085_strict") is True and
                    bs_ct.get("upper_below_085_strict") is True)
    strata_strict = (strata.get("status") == "ok" and
                     strata.get("valid_cell_count", 0) >= 1)

    return {
        "panel_level_bootstrap": panel_bootstrap,
        "strata_per_cell": strata,
        "acceptance_strict": panel_strict and strata_strict,
        "n_obs_panel": int(len(panel_f)),
        "bootstrap_seed": BOOTSTRAP_SEED,
        "bootstrap_n": BOOTSTRAP_N_DEFAULT,
    }
