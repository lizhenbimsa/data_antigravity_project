"""v3.7.5 — Harden the 9 Table A8 _title-robustness templates (Item 4 + F2/F5 fixes).

Applies three defensive changes, idempotently, to every `25_tableA8_title_robustness.do.tmpl`
(root + 7 paper copies) and `26_bs_title_robustness.do.tmpl`:

  (a) `title_applicable` guard — false when MAIN_TREAT lacks a _full/_ctx suffix, so the
      subinstr no-op (title_var == MAIN_TREAT, e.g. strategic_diff strat_diff_n5) no longer
      produces a degenerate Panel A/B that silently re-runs the main regression.
  (b) `has_dv` / `has_treat` — gate every reghdfe (A/B/C/D/E) on MAIN_DV / MAIN_TREAT
      existence, so absent columns (the live derivative-paper panel lacks ROA + most main
      treatments) no longer r(111)-abort at Panel C *before* esttab.
  (c) `a8_models` / `a8_titles` — dynamic, scoped esttab (only the 3 A/B/C estimates; never
      the Panel D/E models) + an else-branch that writes a stub .tex so a fully-skipped table
      never crashes the .do chain.

Idempotent: skips any file already containing the 'v3.7.5' marker.
Fail-fast: asserts each anchor string is present before replacing.

Run:  python scripts/migrate/v3_7_5_harden_tableA8.py
"""
from __future__ import annotations

from pathlib import Path

MARKER = "v3.7.5 Table A8 hardening"

_TEMPLATES_DIR = (
    Path(__file__).resolve().parents[2] / "papers" / "_common" / "stata_templates"
)

# 8 files using m_* estimate names (root + 7 paper copies).
_M_GROUP = [
    _TEMPLATES_DIR / "25_tableA8_title_robustness.do.tmpl",  # root (P1)
    _TEMPLATES_DIR / "bank_fintech_attention" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "bank_fintech_substance" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "bank_fintech_locus" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "bank_fintech_collab" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "brokerage_network" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "llm_peer" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "strategic_diff" / "25_tableA8_title_robustness.do.tmpl",
]
_BS_FILE = _TEMPLATES_DIR / "benefit_society" / "26_bs_title_robustness.do.tmpl"

# ---- shared building blocks --------------------------------------------------

_GUARD_BLOCK = """local title_var = subinstr("`title_var'", "_full", "_title", .)

* ==== v3.7.5 Table A8 hardening (Item 4 no-op fix + F2 reghdfe gating + F5 dynamic esttab) ====
* (a) title_applicable=0 when MAIN_TREAT lacks a _full/_ctx suffix (subinstr no-op -> title_var==MAIN_TREAT);
*     prevents the degenerate Panel A/B that silently re-runs the main regression (e.g. strategic_diff strat_diff_n5).
* (b) has_dv/has_treat gate every reghdfe so an absent MAIN_DV/MAIN_TREAT does not r(111)-abort the .do.
* (c) a8_models/a8_titles drive a dynamic, scoped esttab (3 A/B/C estimates only) so a skipped panel never crashes the table.
local title_applicable = ("`title_var'" != "{{MAIN_TREAT}}")
if !`title_applicable' display "  [WARN] {{MAIN_TREAT}} has no _full/_ctx suffix; no genuine _title variant -> Panels A/B N/A."
capture confirm variable {{MAIN_DV}}
local has_dv = (_rc == 0)
capture confirm variable {{MAIN_TREAT}}
local has_treat = (_rc == 0)
local a8_models ""
local a8_titles \"\""""

# Note: the trailing `local a8_titles ""` is written with escaped quotes only for the
# Python literal; on disk it is plain `local a8_titles ""`.
_GUARD_BLOCK = _GUARD_BLOCK.replace('local a8_titles ""', 'local a8_titles ""')


def _stub_esttab(open_line: str, tex_name: str) -> tuple[str, str]:
    """Return (old, new) that wraps an `esttab <models> ///` opener in an
    if-empty-stub / else-esttab-dynamic-list guard."""
    new = (
        'if "`a8_models\'" == "" {\n'
        '    display "  [WARN] Table A8: no estimable panel for {{PAPER_ID}}; writing stub .tex."\n'
        f'    file open _a8stub using "$tables_dir/{tex_name}", write replace\n'
        '    file write _a8stub "% Table A8 N/A for {{PAPER_ID}}: no usable _title panel (MAIN cols or _title variant absent)." _n\n'
        '    file close _a8stub\n'
        '}\n'
        "else esttab `a8_models' ///"
    )
    return open_line, new


def _m_group_repls() -> list[tuple[str, str]]:
    return [
        # (a)(b)(c) guard block — anchored on the (unique) 2nd subinstr line.
        ('local title_var = subinstr("`title_var\'", "_full", "_title", .)', _GUARD_BLOCK),
        # Panel A/B gate (root: 2 occurrences, both gated; copies: 1).
        (
            "capture confirm variable `title_var'\nif !_rc {",
            "capture confirm variable `title_var'\nif `title_applicable' & `has_dv' & `has_treat' & !_rc {",
        ),
        # a8_models/a8_titles accumulation after each of the 3 rendered estimates.
        (
            "    eststo m_title_only\n",
            '    eststo m_title_only\n    local a8_models "`a8_models\' m_title_only"\n    local a8_titles `"`a8_titles\' "Title-only""\'\n',
        ),
        (
            "    eststo m_main_plus_title\n",
            '    eststo m_main_plus_title\n    local a8_models "`a8_models\' m_main_plus_title"\n    local a8_titles `"`a8_titles\' "Main+Title""\'\n',
        ),
        (
            "    eststo m_with_gap\n",
            '    eststo m_with_gap\n    local a8_models "`a8_models\' m_with_gap"\n    local a8_titles `"`a8_titles\' "+Gap control""\'\n',
        ),
        # Panel C / D / E reghdfe gating on MAIN existence.
        (
            "capture confirm variable tone_gap_title_full\nif !_rc {",
            "capture confirm variable tone_gap_title_full\nif `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "capture confirm variable frac_title_mentions_fintech\nif !_rc {",
            "capture confirm variable frac_title_mentions_fintech\nif `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "capture confirm variable frac_title_long\nif !_rc {",
            "capture confirm variable frac_title_long\nif `has_dv' & `has_treat' & !_rc {",
        ),
        # Dynamic, scoped esttab + stub.
        _stub_esttab(
            "esttab m_title_only m_main_plus_title m_with_gap ///",
            "tableA8_title_robustness.tex",
        ),
        # Dynamic mtitles (parallel to a8_models -> correct labels even for partial tables).
        (
            '    mtitles("Title-only" "Main+Title" "+Gap control") ///',
            "    mtitles(`a8_titles') ///",
        ),
    ]


def _bs_repls() -> list[tuple[str, str]]:
    return [
        ('local title_var = subinstr("`title_var\'", "_full", "_title", .)', _GUARD_BLOCK),
        (
            "capture confirm variable `title_var'\nif !_rc {",
            "capture confirm variable `title_var'\nif `title_applicable' & `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "    eststo bs_m_title_only\n",
            '    eststo bs_m_title_only\n    local a8_models "`a8_models\' bs_m_title_only"\n    local a8_titles `"`a8_titles\' "Title-only""\'\n',
        ),
        (
            "    eststo bs_m_main_plus_title\n",
            '    eststo bs_m_main_plus_title\n    local a8_models "`a8_models\' bs_m_main_plus_title"\n    local a8_titles `"`a8_titles\' "Main+Title""\'\n',
        ),
        (
            "    eststo bs_m_with_gap\n",
            '    eststo bs_m_with_gap\n    local a8_models "`a8_models\' bs_m_with_gap"\n    local a8_titles `"`a8_titles\' "+Gap control""\'\n',
        ),
        (
            "capture confirm variable tone_gap_title_full\nif !_rc {",
            "capture confirm variable tone_gap_title_full\nif `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "capture confirm variable frac_title_mentions_fintech\nif !_rc {",
            "capture confirm variable frac_title_mentions_fintech\nif `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "capture confirm variable frac_title_long\nif !_rc {",
            "capture confirm variable frac_title_long\nif `has_dv' & `has_treat' & !_rc {",
        ),
        _stub_esttab(
            "esttab bs_m_title_only bs_m_main_plus_title bs_m_with_gap ///",
            "bs_title_robustness.tex",
        ),
        (
            '    mtitles("Title-only" "Main+Title" "+Gap control") ///',
            "    mtitles(`a8_titles') ///",
        ),
    ]


def _apply(path: Path, repls: list[tuple[str, str]]) -> str:
    content = path.read_text(encoding="utf-8")
    if MARKER in content:
        return "skip (already hardened)"
    for old, new in repls:
        if old not in content:
            raise AssertionError(f"{path.name}: anchor not found:\n---\n{old}\n---")
        content = content.replace(old, new)
    # post-conditions
    assert MARKER in content, f"{path.name}: marker not written"
    assert "a8_models" in content and "a8_titles" in content
    assert 'mtitles("Title-only"' not in content, f"{path.name}: static mtitles remains"
    path.write_text(content, encoding="utf-8")
    return "hardened"


def main() -> None:
    results = []
    for p in _M_GROUP:
        results.append((p, _apply(p, _m_group_repls())))
    results.append((_BS_FILE, _apply(_BS_FILE, _bs_repls())))
    for p, status in results:
        rel = p.relative_to(_TEMPLATES_DIR.parents[2])
        print(f"  [{status:>22}] {rel}")
    n_done = sum(1 for _, s in results if s == "hardened")
    print(f"\nv3.7.5 Table A8 hardening: {n_done} hardened, {len(results) - n_done} skipped.")


if __name__ == "__main__":
    main()
