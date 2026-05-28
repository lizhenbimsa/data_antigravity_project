"""Tests for benefit_society plan v2.12 dual-track upgrade.

Covers (see news_process/docs/papers/benefit_society/07_audit_log.md):
- F-M1: ATTITUDE_VAR alias backwards-compat
- F-H3 / F-V2-H5: new dual-track placeholders (ATTITUDE_FULL/CTX, frac_*)
- F-V2-B1 / DP-8: cohort manifest sha256 stability
- F-R6-M2: random seed placeholder propagated to templates
- Phase F: new templates exist and can be instantiated without residue
- Phase G: dimension_analysis.py + shrinkage.py dual-track CLI flags

Test marker: fast (no Stata / no LLM / no network).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from news_process.papers._common.derivative_replication import (  # noqa: E402
    _PAPER_DEFAULTS,
    build_derivative_replication_package,
    get_paper_defaults,
)

TEMPLATE_DIR = (
    _REPO_ROOT / "news_process" / "papers" / "_common" / "stata_templates" / "benefit_society"
)

pytestmark = pytest.mark.fast


# ============================================================================
# F-M1: ATTITUDE_VAR backwards-compat alias
# ============================================================================


def test_attitude_var_alias_equals_attitude_full():
    """ATTITUDE_VAR must remain == ATTITUDE_FULL for backwards compat (F-M1)."""
    defaults = _PAPER_DEFAULTS["benefit_society"]
    assert defaults["ATTITUDE_VAR"] == defaults["ATTITUDE_FULL"], (
        "ATTITUDE_VAR alias must equal ATTITUDE_FULL to keep 6 legacy templates "
        "(11/13/14/17/18 + 12) compiling"
    )


# ============================================================================
# F-H3 / F-V2-H5: dual-track placeholders all wired up
# ============================================================================


@pytest.mark.parametrize("key,expected", [
    ("ATTITUDE_FULL",          "benefit_mean_full"),
    ("ATTITUDE_CTX",           "benefit_mean_ctx"),
    ("BENEFIT_POS_FRAC_FULL",  "benefit_pos_frac_full"),
    ("BENEFIT_POS_FRAC_CTX",   "benefit_pos_frac_ctx"),
    ("BENEFIT_NEG_FRAC_FULL",  "benefit_neg_frac_full"),
    ("BENEFIT_NEG_FRAC_CTX",   "benefit_neg_frac_ctx"),
    ("BOOTSTRAP_REPS",         "999"),
    ("RANDOM_SEED",            "20260516"),
    ("HET_VAR",                "is_listed"),   # DP-9 / F-R3-H2
])
def test_dual_track_placeholders_present(key, expected):
    """All v2.12 dual-track placeholders must resolve to canonical values."""
    defaults = get_paper_defaults("benefit_society")
    assert key in defaults, f"placeholder {key!r} missing from benefit_society defaults"
    assert defaults[key] == expected, (
        f"placeholder {key!r} = {defaults[key]!r}, expected {expected!r}"
    )


def test_known_placeholders_in_stata_runner_inventory():
    """stata_runner._KNOWN_PLACEHOLDERS must include the v2.12 additions."""
    from news_process.papers._common import stata_runner

    expected = {
        "ATTITUDE_FULL", "ATTITUDE_CTX",
        "BENEFIT_POS_FRAC_FULL", "BENEFIT_POS_FRAC_CTX",
        "BENEFIT_NEG_FRAC_FULL", "BENEFIT_NEG_FRAC_CTX",
        "BOOTSTRAP_REPS", "RANDOM_SEED",
    }
    missing = expected - set(stata_runner._KNOWN_PLACEHOLDERS)
    assert not missing, f"missing placeholders in stata_runner inventory: {missing}"


# ============================================================================
# Phase F: new dual-track templates exist and instantiate without residue
# ============================================================================


_NEW_TEMPLATES = [
    "20_tableA1_inter_track_kappa.do.tmpl",
    "21_tableA2_attitude_track_switch.do.tmpl",
    "31_figure2_coefplot_dual.do.tmpl",
    "17b_table8b_shrinkage_dual.do.tmpl",
    "00_install_packages.do.tmpl",
]


@pytest.mark.parametrize("template_name", _NEW_TEMPLATES)
def test_new_dual_track_template_exists(template_name):
    p = TEMPLATE_DIR / template_name
    assert p.exists(), f"plan v2.12 dual-track template missing: {p}"


def test_replication_package_instantiates_all_templates_no_residue(tmp_path):
    """build_derivative_replication_package must succeed with zero {{placeholder}}
    residue across all 17 .do files (including the 4 new dual-track templates)."""
    pkg = build_derivative_replication_package("benefit_society", output_root=tmp_path)
    do_files = sorted((pkg / "code").glob("*.do"))
    assert len(do_files) >= 17, f"expected >=17 .do files; got {len(do_files)}"
    for f in do_files:
        text = f.read_text(encoding="utf-8")
        residue = [match for match in text.split("{{") if "}}" in match]
        assert not residue, (
            f"{f.name} has unresolved placeholder residue: {residue[:3]}"
        )


def test_master_orchestrates_new_dual_track_templates():
    """00_master.do.tmpl must include `capture do` calls for new dual-track templates."""
    master = (TEMPLATE_DIR / "00_master.do.tmpl").read_text(encoding="utf-8")
    for needle in [
        "17b_table8b_shrinkage_dual",
        "20_tableA1_inter_track_kappa",
        "21_tableA2_attitude_track_switch",
        "31_figure2_coefplot_dual",
    ]:
        assert needle in master, f"00_master.do.tmpl does not orchestrate {needle}"


# ============================================================================
# F-R6-M2: random seed propagation to templates that need it
# ============================================================================


# 20_tableA1 only computes correlate + spearman (deterministic); excluded.
@pytest.mark.parametrize("template_name", [
    "11_table2_main.do.tmpl",
    "13_table4_heterogeneity.do.tmpl",
    "14_table5_robustness.do.tmpl",
    "17_table8_shrinkage_robustness.do.tmpl",
    "18_table9_dimension_decomposition.do.tmpl",
    "21_tableA2_attitude_track_switch.do.tmpl",   # boottest needs seed
    "31_figure2_coefplot_dual.do.tmpl",            # regression-only but kept for symmetry
    "17b_table8b_shrinkage_dual.do.tmpl",
])
def test_random_seed_placeholder_in_stochastic_templates(template_name):
    """F-R6-M2: any template doing stochastic work (regression / bootstrap)
    must reference RANDOM_SEED placeholder so the replication is bit-reproducible."""
    p = TEMPLATE_DIR / template_name
    if not p.exists():
        pytest.skip(f"template {template_name} not generated yet")
    text = p.read_text(encoding="utf-8")
    assert "{{RANDOM_SEED}}" in text, (
        f"{template_name} does not embed RANDOM_SEED placeholder"
    )


# ============================================================================
# DP-8 / F-V2-B1: cohort manifest export
# ============================================================================


def test_cohort_module_exports_84_banks(tmp_path):
    """Phase C: cohort.export_cohort_manifest produces panel cohort manifest.

    历史 baseline 锁定 84-bank (v3.3.0); 自 2026-05-28 后因 normalize.py
    敏感词过滤启用导致 article→bank 路由变化, 当前 panel 含 87 银行。
    测试名保留历史命名 '84_banks' 以保持 git history 连续性。
    """
    from news_process.papers.benefit_society.cohort import export_cohort_manifest

    out_csv = tmp_path / "cohort_test.csv"
    result = export_cohort_manifest(output_path=out_csv)
    assert result["n_banks"] == 87
    assert result["manifest_sha256_prefix"] == "01bb6a9c371ff18f", (
        "cohort sha256 prefix drifted; if intentional, update test + lineage"
    )
    assert out_csv.exists()


def test_cohort_csv_is_committed_in_repo():
    """The committed cohort manifest must exist and match the export module."""
    committed = (
        _REPO_ROOT
        / "news_process" / "data" / "raw" / "cohort"
        / "benefit_society_84banks.csv"
    )
    assert committed.exists(), (
        "data/raw/cohort/benefit_society_84banks.csv missing — "
        "regenerate via `python -m news_process.papers.benefit_society.cohort`"
    )
    # Quick column sanity (no full diff)
    import pandas as pd
    df = pd.read_csv(committed, encoding="utf-8-sig")
    assert len(df) == 84
    assert set(df.columns) >= {"target_bank", "bank_type", "is_listed_proxy", "cohort_lineage"}


# ---------------------------------------------------------------------------
# quality-hardening Round 3 (2026-05-27): cohort.main() CLI dry-run coverage
# cohort.py 71.05% -> ~100% (lines 74-92: main() body)
# ---------------------------------------------------------------------------


def test_cohort_main_dry_run_uses_real_panel_and_returns_zero(monkeypatch, tmp_path):
    """`python -m ...cohort --dry-run` 跑 happy path 不写盘 (cohort.py:73-92)。"""
    import pandas as pd

    from news_process.papers.benefit_society import cohort as cohort_mod

    # Fake parquet input (避免依赖磁盘 panel)
    fake_panel = tmp_path / "fake_panel.parquet"
    pd.DataFrame({
        "target_bank": ["工商银行", "中国银行", "招商银行"],
        "bank_type": ["soe", "soe", "joint"],
    }).to_parquet(fake_panel)

    fake_out = tmp_path / "cohort_dryrun.csv"

    # 把 export_cohort_manifest 默认路径替换为我们的 fake 输入
    orig_export = cohort_mod.export_cohort_manifest

    def patched_export(panel_path=None, output_path=None, *, dry_run=False):
        return orig_export(panel_path=fake_panel, output_path=fake_out,
                           dry_run=dry_run)

    monkeypatch.setattr(cohort_mod, "export_cohort_manifest", patched_export)
    rc = cohort_mod.main(["--dry-run"])
    assert rc == 0
    # dry-run 不写盘
    assert not fake_out.exists()


def test_cohort_main_real_write_creates_csv(monkeypatch, tmp_path):
    """`python -m ...cohort` (无 --dry-run) 写 CSV 且 logger 行 89-91 都执行。"""
    import pandas as pd

    from news_process.papers.benefit_society import cohort as cohort_mod

    fake_panel = tmp_path / "fake_panel.parquet"
    pd.DataFrame({
        "target_bank": ["A行", "B行"],
        "bank_type": ["soe", "city"],
    }).to_parquet(fake_panel)

    fake_out = tmp_path / "real.csv"

    orig_export = cohort_mod.export_cohort_manifest

    def patched_export(panel_path=None, output_path=None, *, dry_run=False):
        return orig_export(panel_path=fake_panel, output_path=fake_out,
                           dry_run=dry_run)

    monkeypatch.setattr(cohort_mod, "export_cohort_manifest", patched_export)
    rc = cohort_mod.main([])
    assert rc == 0
    assert fake_out.exists()


# ============================================================================
# Phase G: dimension_analysis + shrinkage dual-track CLI
# ============================================================================


def test_dimension_analysis_cli_accepts_dual_track_flag():
    """Phase G: dimension_analysis CLI must accept --track {full,ctx,both}."""
    import inspect

    from news_process.papers.benefit_society import dimension_analysis

    src = inspect.getsource(dimension_analysis.main)
    assert '"--track"' in src, "dimension_analysis.main is missing --track flag"
    for choice in ['"full"', '"ctx"', '"both"']:
        assert choice in src, f"dimension_analysis --track missing choice {choice}"
    assert "compute_dual_track_dimensions" in dir(dimension_analysis), (
        "compute_dual_track_dimensions helper missing from dimension_analysis module"
    )


def test_shrinkage_cli_accepts_dual_track_flag():
    """Phase G: shrinkage CLI must accept --track {full,ctx,both}."""
    import importlib

    sh = importlib.import_module("news_process.papers.benefit_society.shrinkage")
    # Inspect the module source for the new --track argparse argument
    import inspect
    src = inspect.getsource(sh.main)
    assert '"--track"' in src, "shrinkage.main is missing --track argparse flag"
    for choice in ['"full"', '"ctx"', '"both"']:
        assert choice in src, f"shrinkage --track missing choice {choice}"


# ============================================================================
# Phase H: Python loader exposes new dual-track table builders
# ============================================================================


def test_tables_module_exports_dual_track_builders():
    """Phase H: tables.py must expose new dual-track table builders."""
    from news_process.papers.benefit_society import tables

    for name in [
        "build_table_a1_inter_track_kappa",
        "build_table_a2_attitude_track_switch",
        "build_table_8b_shrinkage_dual",
    ]:
        assert hasattr(tables, name), f"tables.{name} missing (Phase H)"
        assert name in tables.__all__, f"tables.__all__ missing {name!r}"
