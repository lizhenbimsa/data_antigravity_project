"""papers/benefit_society/dimension_analysis.py 的单元测试。

覆盖目标:
- 维度索引切片与 Stage 27 anchor 标签对齐
- 方向向量计算产出单位范数 (unit-norm) 向量
- 投影余弦相似度保持在 [-1, 1] 区间
- bank-year 聚合与等权均值一致 (Jha 2026 Eq. 2)
- anchor 导入兼容 Stage 27 模块签名
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
    """全部 10 个 anchor 索引必须在 4 个维度间恰好各出现一次。"""
    all_indices = []
    for indices in dim_module.DIMENSION_INDICES.values():
        all_indices.extend(indices)
    assert sorted(all_indices) == list(range(10)), \
        f"Dimension indices do not partition [0,10): {sorted(all_indices)}"
    assert len(set(all_indices)) == 10, "Dimension indices overlap"


def test_dimension_labels_match_indices(dim_module):
    """DIMENSION_INDICES 中的每个维度都必须有对应标签。"""
    for dim_name in dim_module.DIMENSION_INDICES:
        assert dim_name in dim_module.DIMENSION_LABELS, \
            f"Missing label for {dim_name}"


def test_import_anchors_returns_lists(dim_module):
    """_import_anchors 必须返回长度均为 10 的平行 pos/neg 列表。"""
    pos, neg = dim_module._import_anchors()
    assert isinstance(pos, list)
    assert isinstance(neg, list)
    assert len(pos) == len(neg) == 10


def test_project_texts_by_dimension_cosine_range(dim_module):
    """投影分数必须是落在 [-1, 1] 内的余弦相似度。"""
    rng = np.random.default_rng(42)
    text_emb = rng.standard_normal((20, 128)).astype(np.float32)

    # 构造单位范数的伪方向向量
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
    """零范数文本 embedding 不得导致除零。"""
    text_emb = np.zeros((3, 64), dtype=np.float32)
    direction = np.ones(64, dtype=np.float32) / np.sqrt(64)
    scores = dim_module.project_texts_by_dimension(
        text_emb, {"core_op": direction}
    )
    assert scores["core_op"].shape == (3,)
    assert np.all(np.isfinite(scores["core_op"]))


def test_aggregate_to_bank_year_equal_weighted_mean(dim_module):
    """聚合结果必须等于等权均值 (Jha 2026 Eq. 2)。"""
    # 构造伪 exploded DataFrame: 2 银行 × 2 年 × 各 3 篇文章
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
    """LLM 缓存缺失时必须抛出清晰的 RuntimeError。"""
    pos = ["p1"] * 10
    neg = ["n1"] * 10
    cache_path = tmp_path / "missing.db"
    with pytest.raises(RuntimeError, match="LLM cache not found"):
        dim_module.compute_direction_vectors(
            pos, neg, cache_db_path=str(cache_path)
        )


def test_get_anchor_embeddings_uses_cache(dim_module, tmp_path, monkeypatch):
    """anchor embedding 检索必须命中 LLMCache, 而非调用 API。"""
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
