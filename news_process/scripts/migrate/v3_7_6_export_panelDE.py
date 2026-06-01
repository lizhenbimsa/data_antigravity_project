"""scripts/migrate/v3_7_6_export_panelDE.py — Table A8 Panel D/E export + true
median + missing-guards (audit follow-up, 2026-05-31). [OBSOLETE — 历史/已废]

⚠ 已废 (标题情感轨 + Table A8 已删): 本脚本的 9 个 Table A8 标题稳健性模板已在 remove-title-track
改造中全部删除; 注入代码引用的列 frac_title_mentions_fintech / frac_title_long 已取消; docstring
声称保持 green 的两个测试文件 tests/test_tableA8_hardening_v375.py 与 test_paper_spec_tA8_filled.py
亦均已删除。该脚本若再运行将对全部目标报 [MISS] / 测试已不存在。仅作历史留存。下方为历史描述。

Runs AFTER v3.7.5 hardening (title_applicable guard + dynamic a8_models esttab +
brokerage Panel F + llm_peer disclosure). It is strictly ADDITIVE to that work:
it never edits the a8_models accumulation, the A/B/C/F esttab, the mtitles, the
stub branch, or any v3.7.5 marker — so the 13 tests in
tests/test_tableA8_hardening_v375.py and the 40 in test_paper_spec_tA8_filled.py
remain green.

Closes the three remaining Panel D/E defects the v3.7.5 plan explicitly deferred:

  DEFECT 1 (dead export, highest severity): each template `eststo`s 4 Panel D/E
  stratified models but esttab exports only `a8_models` (A/B/C[/F]). The D/E
  estimates reach NO reader. Fix: accumulate them into a SEPARATE `de_models`
  local and write a skip-safe stratification table `tableA8_panelDE_strat.tex`,
  inserted immediately before the `if "`a8_models'" == ""` export guard.

  DEFECT 2 (Panel E fixed-0.5 vs documented "median"): Panel E is documented as
  an above/below "bank-year median" split but coded as a fixed 0.5 cut. Fix:
  summarize -> `local med_ftl = r(p50)` -> compare against the median. (Done
  correctly: r(p50) is captured into a local BEFORE the next `count` clears r().)

  DEFECT 3 (Stata +inf missing inclusion): `if frac > tau` / `> 0.5` silently
  include missing-frac rows (Stata treats missing as +inf). Fix: add
  `& !missing(...)` to every Panel D/E count + reghdfe condition.

Anchors are byte-identical across all 9 templates (verified: Panel-D block hash
uniform; Panel-E block uniform). Each replacement asserts an exact expected count,
so any anchor drift raises instead of silently no-op'ing.

Idempotent: skips a template already carrying the v3.7.6 marker.

Run:  F:\\Anaconda3\\python.exe scripts/migrate/v3_7_6_export_panelDE.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TPL = ROOT / "papers" / "_common" / "stata_templates"
MARKER = "v3.7.6 Panel D/E export"

TEMPLATES = [
    TPL / "25_tableA8_title_robustness.do.tmpl",
    TPL / "bank_fintech_attention" / "25_tableA8_title_robustness.do.tmpl",
    TPL / "bank_fintech_substance" / "25_tableA8_title_robustness.do.tmpl",
    TPL / "bank_fintech_locus" / "25_tableA8_title_robustness.do.tmpl",
    TPL / "bank_fintech_collab" / "25_tableA8_title_robustness.do.tmpl",
    TPL / "brokerage_network" / "25_tableA8_title_robustness.do.tmpl",
    TPL / "llm_peer" / "25_tableA8_title_robustness.do.tmpl",
    TPL / "strategic_diff" / "25_tableA8_title_robustness.do.tmpl",
    TPL / "benefit_society" / "26_bs_title_robustness.do.tmpl",
]

# (old, new, expected_count) — every count asserted per file.
REPL = [
    # ---- de_models declaration: piggy-back on the universal a8_titles="" line ----
    ('local a8_titles ""\n',
     'local a8_titles ""\n'
     '* v3.7.6: separate accumulator for Panel D/E stratified models (own table)\n'
     'local de_models ""\n',
     1),

    # ---- Panel D: missing-guards on the two counts ----
    ("    quietly count if frac_title_mentions_fintech > `tau'\n",
     "    quietly count if frac_title_mentions_fintech > `tau' "
     "& !missing(frac_title_mentions_fintech)\n",
     1),
    ("    quietly count if frac_title_mentions_fintech <= `tau'\n",
     "    quietly count if frac_title_mentions_fintech <= `tau' "
     "& !missing(frac_title_mentions_fintech)\n",
     1),
    # ---- Panel D: missing-guards on reghdfe if + de_models accumulation ----
    ("            if frac_title_mentions_fintech > `tau', ///\n",
     "            if frac_title_mentions_fintech > `tau' "
     "& !missing(frac_title_mentions_fintech), ///\n",
     1),
    ("        eststo m_panelD_above_`thr_str'\n",
     "        eststo m_panelD_above_`thr_str'\n"
     "        local de_models \"`de_models' m_panelD_above_`thr_str'\"\n",
     1),
    ("            if frac_title_mentions_fintech <= `tau', ///\n",
     "            if frac_title_mentions_fintech <= `tau' "
     "& !missing(frac_title_mentions_fintech), ///\n",
     1),
    ("        eststo m_panelD_below_`thr_str'\n",
     "        eststo m_panelD_below_`thr_str'\n"
     "        local de_models \"`de_models' m_panelD_below_`thr_str'\"\n",
     1),

    # ---- Panel E: true bank-year median split (replaces fixed 0.5) ----
    ("    quietly count if frac_title_long > 0.5\n"
     "    local n_long = r(N)\n"
     "    quietly count if frac_title_long <= 0.5\n"
     "    local n_short = r(N)\n",
     "    quietly summarize frac_title_long if !missing(frac_title_long), detail\n"
     "    local med_ftl = r(p50)\n"
     "    quietly count if frac_title_long > `med_ftl' & !missing(frac_title_long)\n"
     "    local n_long = r(N)\n"
     "    quietly count if frac_title_long <= `med_ftl' & !missing(frac_title_long)\n"
     "    local n_short = r(N)\n",
     1),
    ("            if frac_title_long > 0.5, ///\n",
     "            if frac_title_long > `med_ftl' & !missing(frac_title_long), ///\n",
     1),
    ("        eststo m_panelE_long\n",
     "        eststo m_panelE_long\n"
     "        local de_models \"`de_models' m_panelE_long\"\n",
     1),
    ("            if frac_title_long <= 0.5, ///\n",
     "            if frac_title_long <= `med_ftl' & !missing(frac_title_long), ///\n",
     1),
    ("        eststo m_panelE_short\n",
     "        eststo m_panelE_short\n"
     "        local de_models \"`de_models' m_panelE_short\"\n",
     1),
]

# D/E export block, inserted immediately before the A/B/C export guard (unique).
EXPORT_ANCHOR = 'if "`a8_models\'" == "" {'
EXPORT_BLOCK = (
    "* ==== v3.7.6 Panel D/E export ====\n"
    "* The Panel D/E stratified models were eststo-only (never tabulated) before\n"
    "* v3.7.6. Write them to a SEPARATE skip-safe table so the subsample columns\n"
    "* are not conflated with the A/B/C substitution columns.\n"
    'if "`de_models\'" != "" {\n'
    "    esttab `de_models' ///\n"
    '        using "$tables_dir/tableA8_panelDE_strat.tex", ///\n'
    "        se star(* 0.10 ** 0.05 *** 0.01) replace ///\n"
    '        title("Table A8 (Panel D/E): Stratified Headline Robustness — {{PAPER_ID}}") ///\n'
    "        nonotes ///\n"
    '        addnote("Panel D: subsample by frac_title_mentions_fintech vs tau in {0.3,0.5,0.7} " ///\n'
    '                "(Antweiler-Frank 2004 JF subject-relevance threshold sensitivity). " ///\n'
    '                "Panel E: above/below bank-year MEDIAN frac_title_long " ///\n'
    '                "(attention-channel motivation, Da-Engelberg-Gao 2011 JF). " ///\n'
    '                "Per-cell N>=30 graceful skip; rows with missing frac excluded.")\n'
    '    display "  [done] Panel D/E stratified table: $tables_dir/tableA8_panelDE_strat.tex"\n'
    "}\n"
    'else display "  [WARN] Panel D/E: no subsample cell with N>=30; stratified table skipped."\n'
    "\n"
)


def patch(text: str) -> tuple[str, bool]:
    if MARKER in text:
        return text, False
    for old, new, exp in REPL:
        got = text.count(old)
        if got != exp:
            raise AssertionError(
                f"anchor count {got} != {exp} for: {old[:70]!r}")
        text = text.replace(old, new)
    if text.count(EXPORT_ANCHOR) != 1:
        raise AssertionError(f"export anchor count {text.count(EXPORT_ANCHOR)} != 1")
    text = text.replace(EXPORT_ANCHOR, EXPORT_BLOCK + EXPORT_ANCHOR, 1)
    return text, True


def main() -> None:
    print("=== v3.7.6 Panel D/E export + true-median + missing-guards ===")
    changed = 0
    for p in TEMPLATES:
        if not p.exists():
            print(f"  MISSING: {p}")
            continue
        raw = p.read_text(encoding="utf-8")
        new, did = patch(raw)
        if did:
            p.write_text(new, encoding="utf-8", newline="")
            changed += 1
            print(f"  [CHG] {p.relative_to(ROOT)}")
        else:
            print(f"  [ . ] {p.relative_to(ROOT)} (already v3.7.6)")
    print(f"\nSUMMARY: {changed}/{len(TEMPLATES)} templates patched.")


if __name__ == "__main__":
    main()
