"""Tests for benefit_society_audit_combined (P1.6 + 27c thin shim).

V2.0 J-L-M robustness alignment plan §3 Phase 1 P1.9 (P1.6 portion).
Validate-only path tests; full projection requires sentence_transformers
(integration-marked).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.features import benefit_society_audit_combined

# ============================================================================
# CLI validate-only
# ============================================================================


class TestCLIValidate:
    def test_validate_only_exits_clean(self) -> None:
        rc = benefit_society_audit_combined.main(["--validate-only"])
        assert rc == 0

    def test_no_args_warns_and_exits_clean(self) -> None:
        """Without input flags, yaml schemas are validated; CLI exits 0 with warning."""
        rc = benefit_society_audit_combined.main([])
        assert rc == 0


# ============================================================================
# build_audit_panel (mock embedding path) — pure-Python, no sentence_transformers
# ============================================================================


class TestBuildAuditPanelMock:
    def test_length_mismatch_raises(self) -> None:
        df = pd.DataFrame(
            {
                "target_bank": ["a"],
                "year": [2017],
                "标题": ["x"],
                "内容": ["y"],
            }
        )
        emb = np.zeros((3, 8))  # wrong length
        direction = np.zeros(8)
        with pytest.raises(ValueError, match="length mismatch"):
            benefit_society_audit_combined.build_audit_panel(df, emb, direction)


# ============================================================================
# 27c thin shim — script invocation
# ============================================================================


class TestThinShim:
    def test_27c_shim_is_short(self) -> None:
        """Shim ≤30 lines per CLAUDE.md invariant."""
        path = Path(__file__).resolve().parents[1] / "27c_placebo_and_alt_anchor.py"
        # actually news_process root, not tests root — adjust
        shim_path = (
            Path(__file__).resolve().parents[1] / "27c_placebo_and_alt_anchor.py"
        )
        if not shim_path.exists():
            # tests is under news_process/tests/; shim is at news_process/
            shim_path = Path(__file__).resolve().parent.parent / "27c_placebo_and_alt_anchor.py"
        assert shim_path.exists(), f"shim not found: {shim_path}"
        # CLAUDE.md hard cap: ≤30 lines
        with open(shim_path, encoding="utf-8") as f:
            nlines = sum(1 for _ in f)
        assert nlines <= 30, f"27c shim has {nlines} lines > 30 cap"

    def test_27c_shim_imports_main_only(self) -> None:
        """Shim contains exactly one import-and-delegate pattern (no logic)."""
        shim_path = (
            Path(__file__).resolve().parent.parent / "27c_placebo_and_alt_anchor.py"
        )
        text = shim_path.read_text(encoding="utf-8")
        # Must import main from pipeline.features.benefit_society_audit_combined
        assert (
            "from news_process.pipeline.features.benefit_society_audit_combined import main"
            in text
        )
        # Must call sys.exit(main()) under __main__ guard
        assert "sys.exit(main())" in text


# ============================================================================
# write_sidecar_json
# ============================================================================


class TestSidecarJSON:
    def test_sidecar_json_written(self, tmp_path) -> None:
        panel_path = tmp_path / "audit_panel.parquet"
        # Don't actually write parquet; just verify sidecar.json
        meta = {
            "alt_anchor_yaml_sha256": "abc",
            "placebo_keyword_yaml_sha256": "def",
            "placebo_match_counts": {"housing": 100},
        }
        sidecar = benefit_society_audit_combined.write_sidecar_json(panel_path, meta)
        assert sidecar.exists()
        assert sidecar.name == "audit_panel.sidecar.json"
        import json

        loaded = json.loads(sidecar.read_text(encoding="utf-8"))
        assert loaded["alt_anchor_yaml_sha256"] == "abc"
        assert loaded["placebo_match_counts"]["housing"] == 100
