"""scripts/migrate/v3_7_4_append_panel_de.py — v3.7.4 P3.4 + P3.5 propagator. [OBSOLETE — 历史/已废]

⚠ 已废 (标题情感轨已删): 本脚本的 9 个目标模板 (8 × 25_tableA8_title_robustness.do.tmpl +
benefit_society × 26_bs_title_robustness.do.tmpl) 已在 remove-title-track 改造中全部删除;
注入的 Panel D/E 代码块引用的列 frac_title_mentions_fintech / frac_title_long 亦已取消
(encode.py 三轨循环收为 [_full, _ctx])。该脚本若再运行将对全部 9 个目标报 [MISS]。仅作历史留存,
请勿当作活体迁移工具。下方为历史描述。

One-shot migration: append Panel D + Panel E sections to each of 9 Stata
templates (8 paper × `25_tableA8_title_robustness.do.tmpl` + benefit_society
× `26_bs_title_robustness.do.tmpl`).

Idempotent: skips templates that already contain `*Panel D:` and `*Panel E:`
markers.

Run:
    python F:/Anaconda3/python.exe scripts/migrate/v3_7_4_append_panel_de.py

The Panel D template stratifies the main treatment by
`frac_title_mentions_fintech` at three Antweiler-Frank (2004 JF) sensitivity
thresholds {0.3, 0.5, 0.7}.

The Panel E template stratifies by `frac_title_long` (above/below bank-year
median title length, per Da-Engelberg-Gao 2011 JF attention channel).
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent.parent
_TEMPLATES_ROOT = _PROJECT_ROOT / "papers" / "_common" / "stata_templates"

# 9 target templates (8 paper × 25_tableA8 + benefit_society × 26_bs)
TARGETS: list[Path] = [
    _TEMPLATES_ROOT / "25_tableA8_title_robustness.do.tmpl",  # P1 main
    _TEMPLATES_ROOT / "bank_fintech_attention/25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_ROOT / "bank_fintech_substance/25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_ROOT / "bank_fintech_locus/25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_ROOT / "bank_fintech_collab/25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_ROOT / "brokerage_network/25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_ROOT / "llm_peer/25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_ROOT / "strategic_diff/25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_ROOT / "benefit_society/26_bs_title_robustness.do.tmpl",
]


PANEL_D_BLOCK = r"""
* ---------------------------------------------------------------------------
* Panel D (v3.7.4): stratify by frac_title_mentions_fintech across 3 thresholds
* {0.3, 0.5, 0.7} — Antweiler-Frank (2004) JF 59(3) subject-relevance
* threshold sensitivity convention. Hassan et al. (2019) QJE §IV.A
* sub-window analysis. Per-cell graceful skip if N < 30.
* ---------------------------------------------------------------------------
capture confirm variable frac_title_mentions_fintech
if !_rc {
    foreach tau in 0.3 0.5 0.7 {
        local thr_str = subinstr("`tau'", ".", "p", .)
        quietly count if frac_title_mentions_fintech > `tau'
        local n_above = r(N)
        quietly count if frac_title_mentions_fintech <= `tau'
        local n_below = r(N)
        display "  Panel D τ=`tau': N above=`n_above', N below=`n_below'"
        if `n_above' >= 30 {
            reghdfe {{MAIN_DV}} {{MAIN_TREAT}} $bank_controls ///
                if frac_title_mentions_fintech > `tau', ///
                absorb(bank_id year) vce(cluster bank_id year)
            eststo m_panelD_above_`thr_str'
        }
        else {
            display "    [WARN] Panel D τ=`tau' above: N=`n_above' < 30, skip"
        }
        if `n_below' >= 30 {
            reghdfe {{MAIN_DV}} {{MAIN_TREAT}} $bank_controls ///
                if frac_title_mentions_fintech <= `tau', ///
                absorb(bank_id year) vce(cluster bank_id year)
            eststo m_panelD_below_`thr_str'
        }
        else {
            display "    [WARN] Panel D τ=`tau' below: N=`n_below' < 30, skip"
        }
    }
}
else {
    display "  [WARN] frac_title_mentions_fintech not in panel; Panel D skipped"
}
"""

PANEL_E_BLOCK = r"""
* ---------------------------------------------------------------------------
* Panel E (v3.7.4): stratify by frac_title_long (bank-year median title length)
* Anchor: Da-Engelberg-Gao (2011) JF 66(5) attention-channel separation
* (short titles → attention channel; long titles → substance channel);
* Tetlock (2007) JF 62(3) length-based information content.
* Per-cell graceful skip if N < 30.
* ---------------------------------------------------------------------------
capture confirm variable frac_title_long
if !_rc {
    quietly count if frac_title_long > 0.5
    local n_long = r(N)
    quietly count if frac_title_long <= 0.5
    local n_short = r(N)
    display "  Panel E: N long-title=`n_long', N short-title=`n_short'"
    if `n_long' >= 30 {
        reghdfe {{MAIN_DV}} {{MAIN_TREAT}} $bank_controls ///
            if frac_title_long > 0.5, ///
            absorb(bank_id year) vce(cluster bank_id year)
        eststo m_panelE_long
    }
    else {
        display "    [WARN] Panel E long: N=`n_long' < 30, skip"
    }
    if `n_short' >= 30 {
        reghdfe {{MAIN_DV}} {{MAIN_TREAT}} $bank_controls ///
            if frac_title_long <= 0.5, ///
            absorb(bank_id year) vce(cluster bank_id year)
        eststo m_panelE_short
    }
    else {
        display "    [WARN] Panel E short: N=`n_short' < 30, skip"
    }
}
else {
    display "  [WARN] frac_title_long not in panel; Panel E skipped"
}
"""


def append_to_template(template_path: Path) -> str:
    """Append Panel D + Panel E blocks to a Stata template. Idempotent.

    Returns a status string: '[APPENDED] ...', '[SKIP idempotent] ...', or '[MISS] ...'.
    """
    if not template_path.exists():
        return f"[MISS] {template_path.name}"
    content = template_path.read_text(encoding="utf-8")
    if "* Panel D (v3.7.4)" in content and "* Panel E (v3.7.4)" in content:
        return f"[SKIP idempotent] {template_path.name}"

    # Insert before the final `esttab` block (per existing convention)
    # If `esttab` is found, insert before; otherwise append at end.
    marker = "esttab "
    insert_block = PANEL_D_BLOCK + PANEL_E_BLOCK
    if marker in content:
        idx = content.find(marker)
        # Walk back to start of line
        line_start = content.rfind("\n", 0, idx) + 1
        new_content = content[:line_start] + insert_block + "\n" + content[line_start:]
    else:
        new_content = content + insert_block

    template_path.write_text(new_content, encoding="utf-8")
    return f"[APPENDED] {template_path.name}"


def main() -> int:
    """Walk TARGETS and append Panel D + Panel E blocks. Returns 0 on success."""
    print(f"v3.7.4 Panel D + E propagator: walking {len(TARGETS)} templates")
    print(f"Templates root: {_TEMPLATES_ROOT}")
    print("-" * 60)
    for tpl in TARGETS:
        rel = tpl.relative_to(_PROJECT_ROOT)
        result = append_to_template(tpl)
        print(f"  {result} ({rel})")
    print("-" * 60)
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
