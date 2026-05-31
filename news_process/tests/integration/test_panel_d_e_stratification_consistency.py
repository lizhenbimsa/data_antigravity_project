"""Integration tests for Panel D/E stratification consistency in the 9 Table A8
templates.

v3.7.6 (2026-05-31): the Panel D/E stratification contract was CORRECTED (audit
follow-up, user-authorized). These tests now pin the FIXED behaviour:
  - Panel E splits on the bank-year MEDIAN of frac_title_long (was a fixed 0.5
    cut that contradicted the documented "bank-year median" design);
  - Panel D + Panel E conditions exclude missing-frac rows via `!missing(...)`
    (Stata otherwise treats missing as +inf and silently includes them);
  - the Panel D/E stratified estimates are EXPORTED to a separate table
    `tableA8_panelDE_strat.tex` (they were eststo-only / never tabulated before).
Earlier v3.7.4 versions of these tests pinned the as-shipped (buggy) behaviour;
they were updated here together with the fix in
scripts/migrate/v3_7_6_export_panelDE.py.
"""
from pathlib import Path

_TDIR = Path(__file__).resolve().parents[1].parent / "papers" / "_common" / "stata_templates"

_TEMPLATES = sorted(_TDIR.glob("**/25_tableA8_title_robustness.do.tmpl")) + [
    _TDIR / "benefit_society" / "26_bs_title_robustness.do.tmpl"
]


def _read(p):
    return p.read_text(encoding="utf-8")


def _panel_d_block(c: str) -> str:
    # From the Panel D section header to the Panel E section header. Both panels
    # are preceded by a unique "* Panel X (v3.7.4)" comment banner.
    return c.split("* Panel D (v3.7.4)")[1].split("* Panel E (v3.7.4)")[0]


def _panel_e_block(c: str) -> str:
    # Panel E runs from its banner to the next panel/export marker.
    after_e = c.split("* Panel E (v3.7.4)")[1]
    for stop in ("* Panel F", "v3.7.6 Panel D/E export", 'if "`a8_models'):
        after_e = after_e.split(stop)[0]
    return after_e


def test_all_templates_have_panel_d():
    for p in _TEMPLATES:
        c = _read(p)
        assert "Panel D (v3.7.4)" in c, p
        assert "frac_title_mentions_fintech" in c, p


def test_panel_d_threshold_above_below_partition():
    """Panel D uses tau in {0.3,0.5,0.7} with an above/below partition."""
    for p in _TEMPLATES:
        c = _read(p)
        assert "foreach tau in 0.3 0.5 0.7" in c, p
        assert "frac_title_mentions_fintech > `tau'" in c, p
        assert "frac_title_mentions_fintech <= `tau'" in c, p


def test_panel_e_uses_bank_year_median_not_fixed_half():
    """v3.7.6 fix: Panel E splits on the computed bank-year median of
    frac_title_long, NOT a fixed 0.5 cut (which contradicted the documented
    'bank-year median' design)."""
    for p in _TEMPLATES:
        c = _read(p)
        assert "summarize frac_title_long" in c, p
        assert "local med_ftl = r(p50)" in c, p
        assert "frac_title_long > `med_ftl'" in c, p
        # the old fixed-0.5 cut must be gone
        assert "frac_title_long > 0.5" not in c, p
        assert "frac_title_long <= 0.5" not in c, p


def test_panel_d_missing_guard_excludes_nan():
    """v3.7.6 fix: Panel D conditions exclude missing-frac rows (Stata treats
    missing as +inf, otherwise silently included in the > tau arm)."""
    for p in _TEMPLATES:
        pd_block = _panel_d_block(_read(p))
        assert "!missing(frac_title_mentions_fintech)" in pd_block, p


def test_panel_e_missing_guard_excludes_nan():
    """v3.7.6 fix: Panel E conditions exclude missing-frac rows."""
    for p in _TEMPLATES:
        pe_block = _panel_e_block(_read(p))
        assert "!missing(frac_title_long)" in pe_block, p


def test_panel_de_estimates_are_exported():
    """v3.7.6 fix: the stratified Panel D/E estimates are written to a separate
    table (previously eststo-only and never tabulated)."""
    for p in _TEMPLATES:
        c = _read(p)
        assert "local de_models" in c, p
        assert "tableA8_panelDE_strat.tex" in c, p
        # all four stratified arms accumulate into de_models
        assert c.count('local de_models "`de_models\'') == 4, p
