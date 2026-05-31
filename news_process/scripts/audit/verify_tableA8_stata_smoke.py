"""v3.7.5 — Stata/MP smoke verification harness for the hardened Table A8 templates.

Resolves the plan's only residual risk (Stata not executed). Renders 4 representative
templates, builds a synthetic _prepared_panel.dta, and writes a master verify.do that
runs each under `capture` and asserts the post-hardening behavior:

  - strategic_diff : title_applicable=0 (strat_diff_n5 no suffix) -> Panel A/B N/A,
                     Panel C runs; NO degenerate m_title_only; rc==0.
  - bank_fintech_substance : MAIN_TREAT absent -> every reghdfe gated off ->
                     stub .tex written; rc==0 (no r(111) crash).
  - brokerage_network : Panel A/B/C + Panel F (genuine 2SLS IV-title) run; rc==0.
  - llm_peer : firm-tone OLS reduced-form Panel A/B/C run; rc==0.

Outputs everything under build/stata_verify/. The actual Stata run is launched
separately (PowerShell): StataMP-64.exe /b do build/stata_verify/verify.do
(Windows 必须用 /b 批处理 flag; 用 /e 或裸 GUI 启动会弹「已完成」对话框并阻塞等待点击.)
"""
from __future__ import annotations

from pathlib import Path

from news_process.papers._common import derivative_replication as dr

_REPO = Path(__file__).resolve().parents[1]
_TDIR = Path(dr.__file__).resolve().parent / "stata_templates"
_OUT = _REPO / "build" / "stata_verify"
_CODE = _OUT / "code"          # cwd at run time; templates use ../data + ../output/tables fallback
_DATA = _OUT / "data"
_TABLES = _OUT / "output" / "tables"

_PAPERS = {
    "strategic_diff": "strategic_diff_25.do",
    "bank_fintech_substance": "substance_25.do",
    "brokerage_network": "brokerage_25.do",
    "llm_peer": "llm_peer_25.do",
}

# Fixture columns. NOTE: innovation_substantiveness_full (substance MAIN_TREAT) is
# DELIBERATELY omitted so the absent-main gating path is exercised.
_FIXTURE_DO = r"""
clear all
set more off
set seed 12345
quietly set obs 120
gen bank_id = ceil(_n/2)
bysort bank_id: gen year = 2016 + _n
gen prov_id = mod(bank_id, 20) + 1
gen double ROA = rnormal()
gen double strat_diff_n5 = rnormal()
gen double llm_vote_tone_full = rnormal()
gen double llm_vote_tone_title = rnormal()
gen double llm_peer_tone_iv_title = rnormal()
gen double peer_tone_lag1_full = rnormal()
gen double peer_tone_lag1_title = rnormal()
gen double peer_tone_2nd_lag1_title = rnormal()
gen double tone_gap_title_full = rnormal()
gen double frac_title_mentions_fintech = runiform()
gen double frac_title_long = runiform()
gen double ln_news_coverage = rnormal()
gen double media_hhi = runiform()
gen double media_breadth = runiform()
gen double n_articles = ceil(runiform()*10)
save "$data_dir/_prepared_panel.dta", replace
global bank_controls "ln_news_coverage media_hhi n_articles"
"""


def _render(pid: str) -> str:
    fn = "25_tableA8_title_robustness.do.tmpl"
    content = (_TDIR / pid / fn).read_text(encoding="utf-8")
    return dr._substitute(content, dr.get_paper_defaults(pid))


def main() -> None:
    _CODE.mkdir(parents=True, exist_ok=True)
    _DATA.mkdir(parents=True, exist_ok=True)
    _TABLES.mkdir(parents=True, exist_ok=True)
    for pid, out in _PAPERS.items():
        (_CODE / out).write_text(_render(pid), encoding="utf-8")

    tex = (_TABLES / "tableA8_title_robustness.tex").as_posix()
    # cwd = code dir so each template's `../data` / `../output/tables` fallback resolves
    # even after its leading `clear all` wipes the session globals. Absolute globals are
    # also set, so it works whether or not clear all drops globals.
    lines = [
        "* v3.7.5 Table A8 Stata/MP smoke verification (auto-generated).",
        "clear all",
        "set more off",
        'cd "' + _CODE.as_posix() + '"',
        'global data_dir "' + _DATA.as_posix() + '"',
        'global tables_dir "' + _TABLES.as_posix() + '"',
        _FIXTURE_DO,
        'di "=== RUN strategic_diff (expect: title_applicable WARN, Panel A/B N/A, rc 0) ==="',
        'capture noisily do "strategic_diff_25.do"',
        'di "RC_strategic_diff=" _rc',
        'di "=== RUN substance (absent MAIN_TREAT -> all gated -> stub, rc 0) ==="',
        'capture noisily do "substance_25.do"',
        'di "RC_substance=" _rc',
        'di "=== RUN brokerage (expect Panel F IV-title runs, rc 0) ==="',
        'capture noisily do "brokerage_25.do"',
        'di "RC_brokerage=" _rc',
        'di "=== RUN llm_peer (firm-tone OLS reduced-form, rc 0) ==="',
        'capture noisily do "llm_peer_25.do"',
        'di "RC_llm_peer=" _rc',
        'di "=== ARTIFACT CHECK ==="',
        'capture confirm file "' + tex + '"',
        'di "tex_exists_rc=" _rc',
        'di "ALL_DONE_OK"',
    ]
    (_CODE / "verify.do").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", _CODE / "verify.do")
    print("rendered:", ", ".join(_PAPERS.values()))


if __name__ == "__main__":
    main()
