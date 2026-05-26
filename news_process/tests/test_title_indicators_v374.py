"""tests/test_title_indicators_v374.py — v3.7.4 unit tests for L3 + lint.

Covers:
  - core/text/title_indicators.py (P3.0 shared lib, EP-B3)
  - pipeline/text/ctx_materializer._add_title_indicators (P3.1)
  - pipeline/panel/encode.build_aggregation_dict v3.7.4 keys (P3.1.5)
  - papers/_common/paper_spec_schema (P3.6.a)
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from news_process.core.text.title_indicators import (  # noqa: E402
    compute_title_length_bucket,
    compute_title_mentions_fintech,
    detect_bank_alias_in_title,
    detect_title_sentiment_word,
)

# --- P3.0 shared lib tests ---

class TestTitleIndicatorsLib:
    def test_mentions_fintech_positive(self):
        assert compute_title_mentions_fintech("工行加码区块链", ["区块链", "AI"]) is True

    def test_mentions_fintech_negative(self):
        assert compute_title_mentions_fintech("工行Q3净利增5%", ["区块链", "AI"]) is False

    def test_mentions_fintech_empty_inputs(self):
        assert compute_title_mentions_fintech("", ["区块链"]) is False
        assert compute_title_mentions_fintech("工行", []) is False

    def test_length_bucket_below_median(self):
        assert compute_title_length_bucket("短标题", 20) == 0

    def test_length_bucket_above_median(self):
        assert compute_title_length_bucket("X" * 50, 20) == 1

    def test_sentiment_word_positive(self):
        assert detect_title_sentiment_word("工行净利上涨") is True

    def test_sentiment_word_negative(self):
        assert detect_title_sentiment_word("某行年报发布") is False

    def test_bank_alias_strip_suffix(self):
        assert detect_bank_alias_in_title("工商银行新规", "工商银行股份有限公司") is True


# --- P3.6.a paper_spec_schema tests ---

class TestPaperSpecSchema:
    def test_valid_ref_pattern(self):
        from news_process.papers._common.paper_spec_schema import (
            is_valid_audit_response_ref,
        )
        good = ("docs/methodology/title_track_as_robustness.md"
                "#5-audit-response-template-for-peer-review")
        assert is_valid_audit_response_ref(good) is True

    def test_invalid_ref_pattern(self):
        from news_process.papers._common.paper_spec_schema import (
            is_valid_audit_response_ref,
        )
        bad = "random_url.txt"
        assert is_valid_audit_response_ref(bad) is False

    def test_validate_paper_spec_with_valid_fields(self):
        from news_process.papers._common.paper_spec_schema import validate_paper_spec
        spec = {
            "tables": {
                "tA8": {
                    "title_robustness": {
                        "audit_response_ref": (
                            "docs/methodology/title_track_as_robustness.md"
                            "#5-audit-response-template-for-peer-review"
                        ),
                        "panel_d_caveat": "ok",
                        "panel_e_caveat": "ok",
                    }
                }
            }
        }
        errs = validate_paper_spec(spec)
        assert errs == []

    def test_validate_paper_spec_with_bad_ref(self):
        from news_process.papers._common.paper_spec_schema import validate_paper_spec
        spec = {
            "tables": {
                "tA8": {
                    "title_robustness": {"audit_response_ref": "/wrong/path"}
                }
            }
        }
        errs = validate_paper_spec(spec)
        assert len(errs) == 1

    def test_validate_paper_spec_benefit_society_alt_key(self):
        from news_process.papers._common.paper_spec_schema import validate_paper_spec
        spec = {
            "title_robustness_table": {
                "audit_response_ref": (
                    "docs/methodology/title_track_as_robustness.md"
                    "#5-audit-response-template-for-peer-review"
                ),
            }
        }
        assert validate_paper_spec(spec) == []


# --- P3.1.5 panel encode aggregation key tests ---

class TestPanelAggregation:
    def test_v374_keys_present_when_article_cols_exist(self):
        from news_process.pipeline.panel.encode import build_aggregation_dict
        df = pd.DataFrame({
            "title_mentions_fintech": [True, False, True],
            "title_length_bucket": [0, 1, 1],
            "ctx_is_fallback": [True, False, False],
            "llm_vote_score_full": [0.1, 0.2, 0.3],
        })
        agg = build_aggregation_dict(df)
        assert "frac_title_mentions_fintech" in agg
        assert "frac_title_long" in agg

    def test_v374_keys_absent_when_article_cols_missing(self):
        from news_process.pipeline.panel.encode import build_aggregation_dict
        df = pd.DataFrame({"llm_vote_score_full": [0.1, 0.2]})
        agg = build_aggregation_dict(df)
        assert "frac_title_mentions_fintech" not in agg
        assert "frac_title_long" not in agg


# --- Real paper_spec.yaml validation (uses real files after P3.6.b patcher) ---

@pytest.mark.integration
class TestRealPaperSpecYaml:
    @pytest.mark.parametrize("paper_id", [
        "bank_fintech_tone", "bank_fintech_attention", "bank_fintech_substance",
        "bank_fintech_locus", "bank_fintech_collab", "brokerage_network",
        "llm_peer", "strategic_diff", "benefit_society",
    ])
    def test_real_spec_has_v374_fields(self, paper_id):
        try:
            from ruamel.yaml import YAML
            yaml = YAML()
        except ImportError:
            import yaml as _y
            yaml = _y

        spec_path = (_ROOT / "news_process" / "papers" / paper_id /
                     "paper_spec.yaml")
        if not spec_path.exists():
            pytest.skip(f"paper_spec.yaml not found: {spec_path}")

        with spec_path.open("r", encoding="utf-8") as f:
            spec = yaml.load(f) if hasattr(yaml, "load") else yaml.safe_load(f)

        if paper_id == "benefit_society":
            parent = spec.get("title_robustness_table", {})
        else:
            parent = (spec.get("tables", {}) or {}).get("tA8", {}) or {}
            parent = parent.get("title_robustness", {}) or {}

        assert "audit_response_ref" in parent, f"{paper_id}: audit_response_ref missing"
        assert "panel_d_caveat" in parent, f"{paper_id}: panel_d_caveat missing"
        assert "panel_e_caveat" in parent, f"{paper_id}: panel_e_caveat missing"
