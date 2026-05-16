"""Unit tests for papers/benefit_society/dimension_analysis.py.

Coverage targets:
- Dimension index slicing aligns with Stage 27 anchor labels
- Direction vector computation produces unit-norm vectors
- Projection cosine similarity stays in [-1, 1]
- Bank-year aggregation matches equal-weighted mean per Jha 2026 Eq. 2
- Anchor import tolerates Stage 27 module signature
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def dim_module():
    from news_process.papers.benefit_society import dimension_analysis as dim
    return dim


def test_dimension_indices_cover_all_anchors(dim_module):
    """All 10 anchor indices must appear exactly once across 4 dimensions."""
    all_indices = []
    for indices in dim_module.DIMENSION_INDICES.values():
        all_indices.extend(indices)
    assert sorted(all_indices) == list(range(10)), \
        f"Dimension indices do not partition [0,10): {sorted(all_indices)}"
    assert len(set(all_indices)) == 10, "Dimension indices overlap"


def test_dimension_labels_match_indices(dim_module):
    """Every dimension in DIMENSION_INDICES must have a label."""
    for dim_name in dim_module.DIMENSION_INDICES:
        assert dim_name in dim_module.DIMENSION_LABELS, \
            f"Missing label for {dim_name}"


def test_import_anchors_returns_lists(dim_module):
    """_import_anchors must return parallel pos/neg lists of length 10."""
    pos, neg = dim_module._import_anchors()
    assert isinstance(pos, list)
    assert isinstance(neg, list)
    assert len(pos) == len(neg) == 10


def test_project_texts_by_dimension_cosine_range(dim_module):
    """Projection scores must be cosine similarities in [-1, 1]."""
    rng = np.random.default_rng(42)
    text_emb = rng.standard_normal((20, 128)).astype(np.float32)

    # Build unit-norm fake directions
    directions = {}
    for dim_name in dim_module.DIMENSION_INDICES:
        d = rng.standard_normal(128).astype(np.float32)
        directions[dim_name] = d / np.linalg.norm(d)

    scores = dim_module.project_texts_by_dimension(text_emb, directions)
    assert set(scores) == set(directions)
    for dim_name, vec in scores.items():
        assert vec.shape == (20,), f"{dim_name}: shape mismatch"
        assert np.all(vec >= -1.0001), f"{dim_name}: <-1 violation"
        assert np.all(vec <= 1.0001), f"{dim_name}: >+1 violation"


def test_project_texts_zero_norm_handled(dim_module):
    """Zero-norm text embeddings must not cause division by zero."""
    text_emb = np.zeros((3, 64), dtype=np.float32)
    direction = np.ones(64, dtype=np.float32) / np.sqrt(64)
    scores = dim_module.project_texts_by_dimension(
        text_emb, {"core_op": direction}
    )
    assert scores["core_op"].shape == (3,)
    assert np.all(np.isfinite(scores["core_op"]))


def test_aggregate_to_bank_year_equal_weighted_mean(dim_module):
    """Aggregation must match equal-weighted mean (Jha 2026 Eq. 2)."""
    # Build a fake exploded DataFrame with 2 banks × 2 years × 3 articles each
    df_exp = pd.DataFrame({
        "target_bank": ["A"] * 6 + ["B"] * 6,
        "year": [2017, 2017, 2017, 2018, 2018, 2018] * 2,
    })
    text_emb = np.array([
        [1, 0], [1, 0], [1, 0],
        [0, 1], [0, 1], [0, 1],
        [-1, 0], [-1, 0], [-1, 0],
        [0, -1], [0, -1], [0, -1],
    ], dtype=np.float32)

    direction = np.array([1.0, 0.0], dtype=np.float32)
    directions = {"core_op": direction}

    panel = dim_module.aggregate_to_bank_year(df_exp, text_emb, directions)

    panel_a_2017 = panel[(panel["target_bank"] == "A") & (panel["year"] == 2017)]
    panel_b_2017 = panel[(panel["target_bank"] == "B") & (panel["year"] == 2017)]
    assert abs(panel_a_2017["benefit_core_op"].iloc[0] - 1.0) < 1e-5
    assert abs(panel_b_2017["benefit_core_op"].iloc[0] - (-1.0)) < 1e-5


def test_aggregate_length_mismatch_raises(dim_module):
    df_exp = pd.DataFrame({"target_bank": ["A"], "year": [2017]})
    text_emb = np.array([[1, 0], [0, 1]], dtype=np.float32)
    with pytest.raises(ValueError, match="length mismatch"):
        dim_module.aggregate_to_bank_year(
            df_exp, text_emb, {"core_op": np.array([1.0, 0.0])}
        )


def test_compute_direction_vectors_anchor_mismatch_raises(dim_module):
    with pytest.raises(ValueError, match="Anchor count mismatch"):
        dim_module.compute_direction_vectors(
            ["a", "b", "c"], ["x", "y"], cache_db_path="/nonexistent"
        )


def test_compute_direction_vectors_missing_cache_raises(dim_module, tmp_path):
    """Missing LLM cache must produce a clear RuntimeError."""
    pos = ["p1"] * 10
    neg = ["n1"] * 10
    cache_path = tmp_path / "missing.db"
    with pytest.raises(RuntimeError, match="LLM cache not found"):
        dim_module.compute_direction_vectors(
            pos, neg, cache_db_path=str(cache_path)
        )


def test_get_anchor_embeddings_uses_cache(dim_module, tmp_path, monkeypatch):
    """Anchor embedding retrieval must hit LLMCache, not call API."""
    from news_process.core.caching import LLMCache

    cache_path = tmp_path / "fake.db"
    with LLMCache(str(cache_path)) as cache:
        for i, anchor in enumerate(["a1", "a2", "a3"]):
            vec = [float(i + 1), 0.0, 0.0]
            cache.put("test-model", anchor, json.dumps(vec), prompt_version="v0")

    emb = dim_module._get_anchor_embeddings(
        ["a1", "a2", "a3"],
        cache_db_path=str(cache_path),
        model_id="test-model",
        prompt_version="v0",
    )
    assert emb.shape == (3, 3)
    assert np.allclose(emb[:, 0], [1.0, 2.0, 3.0])
