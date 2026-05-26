"""tests/test_paper_spec_tA8_filled.py — v3.7.3 Plan A v1.0.

校验 v3.7.3 升级的 9 篇 paper_spec.yaml 中 tA8 / title_robustness_table
字段填充正确 + 引用的 Stata .do.tmpl 文件实际存在.

测试覆盖 (12 tests):
    1. 8 paper (P1-P5 + brokerage + llm_peer + strategic) 的 tA8.template
       字段值 == '25_tableA8_title_robustness'
    2. benefit_society tA8.template 保持原值 '19_bs_num_intensity_robustness'
       (R3-H1 兼容: A3 不被覆盖)
    3. benefit_society 含新字段 title_robustness_table.template
       == '26_bs_title_robustness'
    4-12. 引用的 Stata .do.tmpl 文件均实际存在 (主线根 P1 + 7 子目录 + bs)
"""
from __future__ import annotations

from pathlib import Path

import pytest

yaml = pytest.importorskip("yaml", reason="PyYAML required for paper_spec read")

# Repo paper_spec.yaml 8 + 1 covered by Plan A v1.0
PAPERS_TA8_FILLED = [
    "bank_fintech_tone",
    "bank_fintech_attention",
    "bank_fintech_substance",
    "bank_fintech_locus",
    "bank_fintech_collab",
    "brokerage_network",
    "llm_peer",
    "strategic_diff",
]

PAPER_BENEFIT_SOCIETY = "benefit_society"

# Stata template paths (relative to news_process/papers/_common/stata_templates/)
EXPECTED_TEMPLATE_PATHS = {
    "bank_fintech_tone": "25_tableA8_title_robustness.do.tmpl",  # 主线根目录
    "bank_fintech_attention": "bank_fintech_attention/25_tableA8_title_robustness.do.tmpl",
    "bank_fintech_substance": "bank_fintech_substance/25_tableA8_title_robustness.do.tmpl",
    "bank_fintech_locus": "bank_fintech_locus/25_tableA8_title_robustness.do.tmpl",
    "bank_fintech_collab": "bank_fintech_collab/25_tableA8_title_robustness.do.tmpl",
    "brokerage_network": "brokerage_network/25_tableA8_title_robustness.do.tmpl",
    "llm_peer": "llm_peer/25_tableA8_title_robustness.do.tmpl",
    "strategic_diff": "strategic_diff/25_tableA8_title_robustness.do.tmpl",
    "benefit_society": "benefit_society/26_bs_title_robustness.do.tmpl",
}

# 仓库根 → news_process/papers/
def _papers_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "papers"


def _templates_dir() -> Path:
    return _papers_dir() / "_common" / "stata_templates"


def _load_paper_spec(paper_id: str) -> dict:
    spec_path = _papers_dir() / paper_id / "paper_spec.yaml"
    if not spec_path.exists():
        pytest.skip(f"paper_spec.yaml missing for {paper_id}: {spec_path}")
    with open(spec_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ===========================================================================
# Test 1-8: 8 papers' tA8.template == '25_tableA8_title_robustness'
# ===========================================================================

@pytest.mark.parametrize("paper_id", PAPERS_TA8_FILLED)
def test_paper_tA8_template_filled(paper_id):
    """每篇 paper 的 tables.tA8.template 字段填入 25_tableA8_title_robustness."""
    spec = _load_paper_spec(paper_id)
    tables = spec.get("tables", {})
    tA8 = tables.get("tA8")
    assert tA8 is not None, f"{paper_id}: tables.tA8 missing"
    assert isinstance(tA8, dict), f"{paper_id}: tables.tA8 not a dict"
    assert tA8.get("template") == "25_tableA8_title_robustness", (
        f"{paper_id}: tA8.template = {tA8.get('template')!r}, "
        f"expected '25_tableA8_title_robustness'"
    )
    # Sanity: title_robustness sub-key present with anchor citation
    tr = tA8.get("title_robustness", {})
    assert "anchor" in tr, f"{paper_id}: tA8.title_robustness.anchor missing"
    assert "Heston" in tr["anchor"] or "Loughran" in tr["anchor"], (
        f"{paper_id}: anchor citation incomplete: {tr['anchor']!r}"
    )


# ===========================================================================
# Test 9: benefit_society tA8 preserves v3.5.1 A3 num_intensity
# ===========================================================================

def test_benefit_society_tA8_preserves_a3_num_intensity():
    """benefit_society 的 tA8 保持 v3.5.1 A3 占用; R3-H1 兼容不覆盖."""
    spec = _load_paper_spec(PAPER_BENEFIT_SOCIETY)
    tA8 = spec.get("tables", {}).get("tA8")
    assert tA8 is not None
    assert tA8.get("template") == "19_bs_num_intensity_robustness", (
        f"benefit_society: tA8.template should preserve A3 num_intensity, "
        f"got {tA8.get('template')!r}"
    )


# ===========================================================================
# Test 10: benefit_society uses paper-specific extension for title robustness
# ===========================================================================

def test_benefit_society_title_robustness_extension():
    """benefit_society uses title_robustness_table extension (v1.0.1)."""
    spec = _load_paper_spec(PAPER_BENEFIT_SOCIETY)
    ext = spec.get("title_robustness_table")
    assert ext is not None, (
        "benefit_society: title_robustness_table extension key missing "
        "(should be added because tA8 is already occupied by A3 num_intensity)"
    )
    assert ext.get("template") == "26_bs_title_robustness"
    tr = ext.get("title_robustness", {})
    assert "Heston" in tr.get("anchor", "")


# ===========================================================================
# Test 11: 9 referenced .do.tmpl files exist on disk
# ===========================================================================

@pytest.mark.parametrize("paper_id,template_rel_path",
                         list(EXPECTED_TEMPLATE_PATHS.items()))
def test_referenced_stata_template_exists(paper_id, template_rel_path):
    """Stata .do.tmpl 文件实际存在 (paper_spec 引用不为 dangling pointer)."""
    full_path = _templates_dir() / template_rel_path
    assert full_path.exists(), (
        f"{paper_id} references {template_rel_path} but file does not exist "
        f"at {full_path}"
    )
    # Sanity: template content includes the v3.7.3 marker
    content = full_path.read_text(encoding="utf-8")
    assert "v3.7.3" in content, (
        f"{template_rel_path}: missing v3.7.3 marker in template content"
    )
    assert "Heston" in content or "Loughran" in content, (
        f"{template_rel_path}: missing top-journal anchor citation"
    )


# ===========================================================================
# Test 12: R3-H1 compatibility marker in 9 paper specs
# ===========================================================================

@pytest.mark.parametrize("paper_id", PAPERS_TA8_FILLED)
def test_r3_h1_compatible_flag(paper_id):
    """All 8 tA8-filled specs must mark r3_h1_compatible: true (A1/A3 not on _title)."""
    spec = _load_paper_spec(paper_id)
    tA8 = spec.get("tables", {}).get("tA8", {})
    tr = tA8.get("title_robustness", {})
    assert tr.get("r3_h1_compatible") is True, (
        f"{paper_id}: tA8.title_robustness.r3_h1_compatible must be True "
        f"(maintains v3.5.1 R3-H1 A1/A3 exclusion)"
    )
