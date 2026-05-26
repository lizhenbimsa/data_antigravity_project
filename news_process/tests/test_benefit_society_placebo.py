"""Tests for benefit_society_placebo (S1 business-line placebo).

V2.0 J-L-M robustness alignment plan §3 Phase 1 P1.9 (S1 portion).
Pure-Python tests; no sentence_transformers / no LLM API dependency.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.features.benefit_society_placebo import (
    compute_placebo_projection,
    filter_articles_by_keywords,
    load_placebo_keywords,
)

# ============================================================================
# load_placebo_keywords
# ============================================================================


class TestLoadKeywords:
    def test_default_yaml_loads_4_business_lines_plus_1_neutral(self) -> None:
        bl, nb, meta = load_placebo_keywords()
        assert len(bl) == 4
        assert len(nb) == 1
        assert meta["n_business_lines"] == 4
        assert meta["n_neutral_baselines"] == 1

    def test_business_lines_are_canonical(self) -> None:
        bl, _, _ = load_placebo_keywords()
        expected_keys = {
            "housing_loans",
            "credit_cards",
            "intermediate_business",
            "branch_channel",
        }
        assert set(bl.keys()) == expected_keys

    def test_each_business_line_has_keywords(self) -> None:
        bl, nb, _ = load_placebo_keywords()
        for k, kws in bl.items():
            assert len(kws) >= 5, f"Business line {k} has too few keywords"
        for k, kws in nb.items():
            assert len(kws) >= 5, f"Neutral {k} has too few keywords"

    def test_sha256_stable(self) -> None:
        _, _, meta = load_placebo_keywords()
        sha = meta["yaml_sha256"]
        assert isinstance(sha, str)
        assert len(sha) == 64

    def test_missing_yaml_raises(self, tmp_path) -> None:
        with pytest.raises(FileNotFoundError):
            load_placebo_keywords(tmp_path / "nonexistent.yaml")

    def test_invalid_business_line_count_raises(self, tmp_path) -> None:
        bad = tmp_path / "bad.yaml"
        bad.write_text(
            "schema_version: '1.0'\n"
            "business_lines:\n"
            "  only_one:\n"
            "    keywords: ['x']\n"
            "neutral_baseline:\n"
            "  baseline:\n"
            "    keywords: ['y']\n",
            encoding="utf-8",
        )
        with pytest.raises(ValueError, match="4 business lines"):
            load_placebo_keywords(bad)


# ============================================================================
# filter_articles_by_keywords
# ============================================================================


class TestFilterArticles:
    def test_single_keyword_matches_in_title(self) -> None:
        df = pd.DataFrame(
            {
                "标题": ["银行房贷新政", "科技转型", "信用卡发行"],
                "内容": ["...", "...", "..."],
            }
        )
        mask = filter_articles_by_keywords(df, ["房贷"])
        assert mask.tolist() == [True, False, False]

    def test_keyword_in_content_matches(self) -> None:
        df = pd.DataFrame(
            {
                "标题": ["银行新闻", "其他", "通用"],
                "内容": ["首套房贷利率下调", "信用卡分期优惠", "无关内容"],
            }
        )
        mask = filter_articles_by_keywords(df, ["房贷"])
        assert mask.tolist() == [True, False, False]

    def test_multiple_keywords_any_match(self) -> None:
        df = pd.DataFrame(
            {
                "标题": ["按揭贷款", "信用卡分期", "存款新规"],
                "内容": ["...", "...", "..."],
            }
        )
        mask = filter_articles_by_keywords(df, ["按揭", "信用卡"])
        assert mask.tolist() == [True, True, False]

    def test_empty_keywords_returns_all_false(self) -> None:
        df = pd.DataFrame({"标题": ["x", "y"], "内容": ["a", "b"]})
        mask = filter_articles_by_keywords(df, [])
        assert mask.tolist() == [False, False]

    def test_nan_columns_handled(self) -> None:
        # Row 0: title=NaN, content="按揭" → matched via content
        # Row 1: title="房贷新政", content=NaN → "按揭" not in either → not matched
        # Row 2: title="按揭利率", content="..." → matched via title
        df = pd.DataFrame(
            {
                "标题": [np.nan, "房贷新政", "按揭利率"],
                "内容": ["按揭", np.nan, "..."],
            }
        )
        mask = filter_articles_by_keywords(df, ["按揭"])
        assert mask.tolist() == [True, False, True]

    def test_missing_columns_default_to_empty(self) -> None:
        df = pd.DataFrame({"标题": ["按揭贷款"]})  # 内容 col missing
        mask = filter_articles_by_keywords(df, ["按揭"])
        assert mask.tolist() == [True]


# ============================================================================
# compute_placebo_projection
# ============================================================================


class TestComputePlaceboProjection:
    def _make_data(self):
        df = pd.DataFrame(
            {
                "target_bank": ["bank_a", "bank_a", "bank_b", "bank_b"],
                "year": [2017, 2018, 2017, 2018],
                "标题": ["房贷新政", "信用卡分期", "网点改造", "其他新闻"],
                "内容": ["...", "...", "...", "..."],
            }
        )
        text_embeddings = np.array(
            [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [0.5, 0.5, 0.0],
            ],
            dtype=np.float32,
        )
        direction = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        return df, text_embeddings, direction

    def test_single_keyword_placebo_aggregates(self) -> None:
        df, emb, direction = self._make_data()
        keyword_sets = {"housing": ["房贷"]}
        panel, matches = compute_placebo_projection(df, emb, direction, keyword_sets)
        assert matches["housing"] == 1
        assert "benefit_placebo_housing_mean" in panel.columns
        # row 0 matched (cosine emb[0] @ direction = 1.0), only at (bank_a, 2017)
        row = panel[
            (panel["target_bank"] == "bank_a") & (panel["year"] == 2017)
        ].iloc[0]
        assert row["benefit_placebo_housing_mean"] == pytest.approx(1.0, abs=1e-5)

    def test_multiple_placebos_all_aggregated(self) -> None:
        df, emb, direction = self._make_data()
        keyword_sets = {
            "housing": ["房贷"],
            "cards": ["信用卡"],
            "branch": ["网点"],
        }
        panel, matches = compute_placebo_projection(df, emb, direction, keyword_sets)
        assert matches == {"housing": 1, "cards": 1, "branch": 1}
        for key in keyword_sets:
            assert f"benefit_placebo_{key}_mean" in panel.columns

    def test_no_match_yields_warning_but_no_crash(self) -> None:
        df, emb, direction = self._make_data()
        keyword_sets = {"empty": ["完全不存在的词组"]}
        panel, matches = compute_placebo_projection(df, emb, direction, keyword_sets)
        assert matches["empty"] == 0
        # Column exists but all-NaN (no rows aggregated)
        assert "benefit_placebo_empty_mean" not in panel.columns or panel[
            "benefit_placebo_empty_mean"
        ].isna().all()

    def test_length_mismatch_raises(self) -> None:
        df = pd.DataFrame({"target_bank": ["a"], "year": [2017], "标题": ["x"], "内容": ["y"]})
        emb = np.zeros((3, 8))  # length mismatch
        direction = np.zeros(8)
        with pytest.raises(ValueError, match="length mismatch"):
            compute_placebo_projection(df, emb, direction, {"x": ["k"]})

    def test_zero_norm_embeddings_handled(self) -> None:
        df, emb, direction = self._make_data()
        emb[2] = 0.0  # zero-norm row
        keyword_sets = {"branch": ["网点"]}
        panel, matches = compute_placebo_projection(df, emb, direction, keyword_sets)
        # row 2 matched 网点 with zero embedding → cosine = 0
        assert matches["branch"] == 1
        row = panel[
            (panel["target_bank"] == "bank_b") & (panel["year"] == 2017)
        ].iloc[0]
        assert row["benefit_placebo_branch_mean"] == pytest.approx(0.0, abs=1e-5)


# ============================================================================
# CLI smoke (validate-only)
# ============================================================================


class TestCLIValidate:
    def test_validate_only_exits_clean(self) -> None:
        from news_process.pipeline.features import benefit_society_placebo

        rc = benefit_society_placebo.main(["--validate-only"])
        assert rc == 0

    # quality-hardening Round 32 (2026-05-27): benefit_society_placebo 93.33%→100%
    # missing 73 / 77 / 81 (config schema errors) + 273-277 (CLI no-validate path)

    def test_main_default_run_returns_zero_with_warning(self, caplog) -> None:
        """main() 无 --validate-only → warning + return 0 (lines 273-277)."""
        import logging

        from news_process.pipeline.features import benefit_society_placebo

        caplog.set_level(
            logging.WARNING,
            logger='news_process.pipeline.features.benefit_society_placebo',
        )
        rc = benefit_society_placebo.main([])
        assert rc == 0


class TestLoadConfigSchemaErrors:
    """load_placebo_keywords YAML schema 校验."""

    def test_business_line_empty_keywords_raises(self, tmp_path):
        """business_line keywords 为空 → ValueError (line 73)."""
        import yaml
        bad_yaml = tmp_path / 'bad.yaml'
        bad_yaml.write_text(yaml.dump({
            'business_lines': {
                'auto': {'keywords': ['汽车']},
                'real_estate': {'keywords': []},  # 空 keywords → raise
                'food': {'keywords': ['食品']},
                'energy': {'keywords': ['能源']},
            },
            'neutral_baseline': {'baseline_a': {'keywords': ['基线词']}},
        }), encoding='utf-8')
        with pytest.raises(ValueError, match="no keywords"):
            load_placebo_keywords(yaml_path=bad_yaml)

    def test_neutral_baseline_count_not_one_raises(self, tmp_path):
        """neutral_baseline 不是 1 个 → ValueError (line 77)."""
        import yaml
        bad_yaml = tmp_path / 'bad.yaml'
        bad_yaml.write_text(yaml.dump({
            'business_lines': {
                'auto': {'keywords': ['汽车']},
                'real_estate': {'keywords': ['房地产']},
                'food': {'keywords': ['食品']},
                'energy': {'keywords': ['能源']},
            },
            'neutral_baseline': {
                'baseline_a': {'keywords': ['基线词']},
                'baseline_b': {'keywords': ['另一基线']},  # 2 个 → raise
            },
        }), encoding='utf-8')
        with pytest.raises(ValueError, match="Expected 1 neutral baseline"):
            load_placebo_keywords(yaml_path=bad_yaml)

    def test_neutral_baseline_empty_keywords_raises(self, tmp_path):
        """neutral_baseline keywords 为空 → ValueError (line 81)."""
        import yaml
        bad_yaml = tmp_path / 'bad.yaml'
        bad_yaml.write_text(yaml.dump({
            'business_lines': {
                'auto': {'keywords': ['汽车']},
                'real_estate': {'keywords': ['房地产']},
                'food': {'keywords': ['食品']},
                'energy': {'keywords': ['能源']},
            },
            'neutral_baseline': {'baseline_a': {'keywords': []}},  # 空
        }), encoding='utf-8')
        with pytest.raises(ValueError, match="no keywords"):
            load_placebo_keywords(yaml_path=bad_yaml)
