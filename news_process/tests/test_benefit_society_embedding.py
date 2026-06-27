from __future__ import annotations

import numpy as np

from news_process.pipeline.features import benefit_society as bs

# v3.14.0 (all-API-embedding): 本地嵌入模型与本地推理机器已彻底移除。
# _get_embeddings 现统一经 _eng.embed_texts(texts, spec) 纯 API 路径 (gemini MAIN
# 3072 维 / text-embedding-3-large _lg 3072 维 co-primary)。本测试 mock _eng.embed_texts
# (API 路径), 不再注入 fake sentence_transformers。


def _fake_embed(dim: int = 3072):
    def _embed(texts, spec, **kwargs):
        texts = list(texts)
        out = np.zeros((len(texts), dim), dtype=np.float32)
        for idx, text in enumerate(texts):
            out[idx, 0] = float(idx)
            out[idx, 1] = float(len(text))
        return out

    return _embed


def test_get_embeddings_uses_api_embed_texts(monkeypatch):
    """MAIN (无后缀, gemini) spec 走 _eng.embed_texts → 3072 维 API 嵌入。"""
    monkeypatch.setattr(
        bs,
        "EMBEDDING_CONFIG",
        {
            "base_url": "https://yunwu.ai/v1",
            "api_key": "fake-key",
            "model": "gemini-embedding-2-preview",
            "text_pipeline_version": "v3-2026-06-27-gemini",
        },
    )
    monkeypatch.setattr(bs._eng, "embed_texts", _fake_embed(dim=3072))

    emb = bs._get_embeddings(["alpha", "beta"], [1, 1], log_prefix="test")

    assert emb is not None
    assert emb.shape == (2, 3072)
    assert np.allclose(emb[:, 0], [0.0, 1.0])


def test_get_embeddings_lg_spec_routes_to_large(monkeypatch):
    """co-primary _lg spec 经同一 _eng.embed_texts API 路径 (3072 维), 失败软降级 None。"""
    captured = {}

    def _embed(texts, spec, **kwargs):
        captured["model"] = (spec or {}).get("model")
        return _fake_embed(dim=3072)(texts, spec, **kwargs)

    monkeypatch.setattr(bs._eng, "embed_texts", _embed)
    lg_spec = {
        "base_url": "https://yunwu.ai/v1",
        "api_key": "fake-key",
        "model": "text-embedding-3-large",
        "text_pipeline_version": "v1-2026-06-27-emb3large",
    }

    emb = bs._get_embeddings(
        ["alpha", "beta"], [1, 1], spec=lg_spec, log_prefix="test-lg")

    assert emb is not None
    assert emb.shape == (2, 3072)
    assert captured["model"] == "text-embedding-3-large"


def test_get_embeddings_lg_spec_soft_degrades_on_failure(monkeypatch):
    """_lg twin (非 MAIN canonical) API 致命错 → 软降级 None (其轨列 NaN, 不炸 stage)。"""
    def _boom(texts, spec, **kwargs):
        raise RuntimeError("simulated API failure")

    monkeypatch.setattr(bs._eng, "embed_texts", _boom)
    lg_spec = {
        "base_url": "https://yunwu.ai/v1",
        "api_key": "fake-key",
        "model": "text-embedding-3-large",
        "text_pipeline_version": "v1-2026-06-27-emb3large",
    }

    emb = bs._get_embeddings(
        ["alpha", "beta"], [1, 1], spec=lg_spec, log_prefix="test-lg")

    assert emb is None
