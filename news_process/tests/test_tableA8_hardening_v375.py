"""v3.7.5 Table A8 hardening — render-level regression tests (Item 3 + Item 4 fixes).

Covers:
  - Item 4: strategic_diff no-op guard (title_applicable) + retitle away from "sentiment".
  - F2: every reghdfe gated on MAIN_DV/MAIN_TREAT existence.
  - F5: dynamic, scoped esttab (no crash when a panel is skipped) + dynamic mtitles.
  - Item 3 / D3: llm_peer Panel A disclosed as firm-tone OLS reduced-form (not 2SLS).
  - Item 3 / D4: brokerage genuine 2SLS title robustness (Panel F).
  - Spec integrity: llm_peer treatment/iv pointers reconciled; phantom _loo column gone.
  - F7: collab template patched on disk but not buildable.
  - F8: v3.7.3 lineage + Heston/Loughran header invariant preserved (test_paper_spec_tA8_filled).
"""
from pathlib import Path

import pytest
import yaml

from news_process.papers._common import derivative_replication as dr

_TDIR = Path(dr.__file__).resolve().parent / "stata_templates"
_PAPERS_DIR = Path(dr.__file__).resolve().parents[1]

# All 9 hardened templates (root + 7 paper copies + bs), raw text.
_ALL_TEMPLATES = sorted(_TDIR.glob("**/25_tableA8_title_robustness.do.tmpl")) + [
    _TDIR / "benefit_society" / "26_bs_title_robustness.do.tmpl"
]

# Renderable via derivative_replication (subset in _DERIVATIVE_PAPER_IDS).
_RENDERABLE = {
    "bank_fintech_attention": "25_tableA8_title_robustness.do.tmpl",
    "bank_fintech_substance": "25_tableA8_title_robustness.do.tmpl",
    "bank_fintech_locus": "25_tableA8_title_robustness.do.tmpl",
    "brokerage_network": "25_tableA8_title_robustness.do.tmpl",
    "llm_peer": "25_tableA8_title_robustness.do.tmpl",
    "strategic_diff": "25_tableA8_title_robustness.do.tmpl",
    "benefit_society": "26_bs_title_robustness.do.tmpl",
}


def _render(pid: str, fn: str) -> str:
    content = (_TDIR / pid / fn).read_text(encoding="utf-8")
    return dr._substitute(content, dr.get_paper_defaults(pid))  # fail-fast on residue


def test_all_nine_templates_have_hardening_markers():
    assert len(_ALL_TEMPLATES) == 9
    for p in _ALL_TEMPLATES:
        c = p.read_text(encoding="utf-8")
        assert "v3.7.5 Table A8 hardening" in c, p
        assert "local title_applicable" in c, p
        assert "local has_dv" in c and "local has_treat" in c, p
        assert "no estimable panel for" in c, f"{p}: dynamic-esttab stub branch missing"
        assert "mtitles(`a8_titles')" in c, f"{p}: dynamic mtitles missing"
        assert 'mtitles("Title-only"' not in c, f"{p}: static mtitles remains"
        # F8: header lineage invariant relied on by test_paper_spec_tA8_filled.py
        assert "v3.7.3" in c and ("Heston" in c or "Loughran" in c), f"{p}: header invariant"


@pytest.mark.parametrize("pid,fn", sorted(_RENDERABLE.items()))
def test_renderable_templates_are_placeholder_clean(pid, fn):
    rendered = _render(pid, fn)  # raises ValueError on any unsubstituted {{...}}
    assert "{{" not in rendered and "}}" not in rendered


def test_item4_strategic_diff_noop_guarded_and_retitled():
    r = _render("strategic_diff", "25_tableA8_title_robustness.do.tmpl")
    # MAIN_TREAT = strat_diff_n5 has no _full/_ctx suffix -> title_var resolves to itself,
    # so title_applicable compares title_var against "strat_diff_n5" (will be false at runtime).
    assert '!= "strat_diff_n5")' in r
    assert "Sub-sample / Environment Robustness" in r
    assert "TEXT-DISTINCTNESS" in r


def test_item3_llm_peer_discloses_ols_reduced_form():
    r = _render("llm_peer", "25_tableA8_title_robustness.do.tmpl")
    assert "OLS reduced-form" in r  # Panel A interim disclosure


def test_tier2_llm_peer_panel_g_genuine_2sls():
    r = _render("llm_peer", "25_tableA8_title_robustness.do.tmpl")
    assert "Panel G" in r and "GENUINE 2SLS" in r
    assert "llm_vote_tone_title = llm_peer_tone_iv_title" in r
    assert "ivreghdfe" in r and "ivreg2" in r  # T=2-robust fallback
    assert "activates on next production encode" in r  # self-activating disclosure


def test_tier2_llm_peer_iv_title_column_wired():
    import inspect

    from news_process.pipeline.panel import llm_peer_iv

    src = inspect.getsource(llm_peer_iv.compute_llm_peer_iv)
    assert "title_tone_col" in src
    # title IV aggregated over the SAME peer_mask as the full IV (faithful by construction)
    assert "llm_peer_tone_iv_title_" in src
    assert "('llm_peer_tone_iv_title', 'llm_peer_tone_iv_title_80')" in src


def test_item3_d4_brokerage_genuine_iv_title():
    r = _render("brokerage_network", "25_tableA8_title_robustness.do.tmpl")
    assert "ivreghdfe" in r
    assert "ivreg2" in r  # T=2-robust fallback (HDFE IV degenerates at T=2)
    assert "peer_tone_lag1_title = peer_tone_2nd_lag1_title" in r
    assert "m_iv_title" in r
    assert '"IV-title (2SLS)"' in r
    assert "{{" not in r  # placeholder-clean (incl. {{CLUSTER_VAR}})


def test_llm_peer_spec_integrity_fixed():
    spec_path = _PAPERS_DIR / "llm_peer" / "paper_spec.yaml"
    raw = spec_path.read_text(encoding="utf-8")
    spec = yaml.safe_load(raw)
    # treatment.primary now names the endogenous 2nd-stage regressor (was the instrument).
    assert spec["treatment"]["primary"] == "llm_vote_tone_full"
    # iv.primary now names the real instrument (was the phantom _loo column).
    assert spec["identification"]["iv"]["primary"] == "llm_peer_tone_iv_full"
    assert spec["identification"]["iv"]["fallback"] == "llm_peer_tone_iv_full_75"
    # phantom _loo column no longer used as an ACTIVE pointer (it may remain only in an
    # explanatory comment documenting why it was wrong).
    active_values = [
        spec["treatment"]["primary"],
        *spec["treatment"]["alternative"],
        spec["identification"]["iv"]["primary"],
        spec["identification"]["iv"]["fallback"],
    ]
    assert not any("llm_peer_tone_loo" in str(v) for v in active_values)


def test_f7_collab_template_patched_but_not_buildable():
    assert "bank_fintech_collab" not in dr._DERIVATIVE_PAPER_IDS
    c = (_TDIR / "bank_fintech_collab" / "25_tableA8_title_robustness.do.tmpl").read_text(
        encoding="utf-8"
    )
    assert "v3.7.5 Table A8 hardening" in c  # patched on disk for consistency
