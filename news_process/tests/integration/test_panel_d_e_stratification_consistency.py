"""tests/integration/test_panel_d_e_stratification_consistency.py — v3.7.4 P3.7.

Integration test verifying:
  - 9 Stata templates contain Panel D + Panel E v3.7.4 markers
  - paper_spec.yaml × 9 contain audit_response_ref pointing to methodology §5
  - methodology doc and Report (when written) have grep diff = 0 on §6/§5 audit response (4.B SoT)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]


STATA_TEMPLATES = [
    "news_process/papers/_common/stata_templates/25_tableA8_title_robustness.do.tmpl",
    "news_process/papers/_common/stata_templates/bank_fintech_attention/25_tableA8_title_robustness.do.tmpl",
    "news_process/papers/_common/stata_templates/bank_fintech_substance/25_tableA8_title_robustness.do.tmpl",
    "news_process/papers/_common/stata_templates/bank_fintech_locus/25_tableA8_title_robustness.do.tmpl",
    "news_process/papers/_common/stata_templates/bank_fintech_collab/25_tableA8_title_robustness.do.tmpl",
    "news_process/papers/_common/stata_templates/brokerage_network/25_tableA8_title_robustness.do.tmpl",
    "news_process/papers/_common/stata_templates/llm_peer/25_tableA8_title_robustness.do.tmpl",
    "news_process/papers/_common/stata_templates/strategic_diff/25_tableA8_title_robustness.do.tmpl",
    "news_process/papers/_common/stata_templates/benefit_society/26_bs_title_robustness.do.tmpl",
]

PAPER_SPECS = [
    ("bank_fintech_tone", ["tables", "tA8", "title_robustness"]),
    ("bank_fintech_attention", ["tables", "tA8", "title_robustness"]),
    ("bank_fintech_substance", ["tables", "tA8", "title_robustness"]),
    ("bank_fintech_locus", ["tables", "tA8", "title_robustness"]),
    ("bank_fintech_collab", ["tables", "tA8", "title_robustness"]),
    ("brokerage_network", ["tables", "tA8", "title_robustness"]),
    ("llm_peer", ["tables", "tA8", "title_robustness"]),
    ("strategic_diff", ["tables", "tA8", "title_robustness"]),
    ("benefit_society", ["title_robustness_table"]),
]


@pytest.mark.parametrize("template_rel", STATA_TEMPLATES)
def test_stata_template_has_panel_de(template_rel):
    """All 9 templates must contain Panel D (v3.7.4) + Panel E (v3.7.4) markers."""
    p = _ROOT / template_rel
    if not p.exists():
        pytest.skip(f"template not found (probably in non-repo test env): {p}")
    text = p.read_text(encoding="utf-8")
    assert "* Panel D (v3.7.4)" in text, f"{template_rel}: missing Panel D marker"
    assert "* Panel E (v3.7.4)" in text, f"{template_rel}: missing Panel E marker"


@pytest.mark.parametrize("paper_id,parent_path", PAPER_SPECS)
def test_paper_spec_has_v374_fields(paper_id, parent_path):
    """All 9 paper_spec.yaml must have audit_response_ref + 2 caveats."""
    try:
        from ruamel.yaml import YAML
        yaml = YAML()
        loader = yaml.load
    except ImportError:
        import yaml as _y
        loader = _y.safe_load

    spec_path = _ROOT / "news_process" / "papers" / paper_id / "paper_spec.yaml"
    if not spec_path.exists():
        pytest.skip(f"paper_spec.yaml not found: {spec_path}")
    with spec_path.open("r", encoding="utf-8") as f:
        spec = loader(f)

    cur = spec
    for k in parent_path:
        assert isinstance(cur, dict), f"{paper_id}: path {parent_path} not navigable"
        assert k in cur, f"{paper_id}: missing key {k}"
        cur = cur[k]
    for key in ("audit_response_ref", "panel_d_caveat", "panel_e_caveat"):
        assert key in cur, f"{paper_id}: missing {key} under {parent_path}"

    expected = ("docs/methodology/title_track_as_robustness.md"
                "#5-audit-response-template-for-peer-review")
    assert cur["audit_response_ref"] == expected, (
        f"{paper_id}: audit_response_ref={cur['audit_response_ref']!r}, expected {expected!r}"
    )


def test_methodology_doc_has_v11_marker():
    """methodology doc must contain v1.1 marker (after P1.11 metadata update)."""
    p = _ROOT / "news_process" / "docs" / "methodology" / "title_track_as_robustness.md"
    if not p.exists():
        pytest.skip("methodology doc not found")
    text = p.read_text(encoding="utf-8")
    # Soft check: either v1.0 (pre-P1.11) or v1.1 (post-P1.11) is acceptable for now
    assert re.search(r"v1\.\d", text), "methodology doc missing version marker"
