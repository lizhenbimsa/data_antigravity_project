from __future__ import annotations

import numpy as np

from news_process.pipeline.panel import network_spillover as ns

# v3.14.0 (all-API-embedding): 本地嵌入模型与本地推理机器已彻底移除。
# _embed_peer_texts 现统一经 _eng.embed_texts(texts, spec) 纯 API 路径 (gemini MAIN
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


def test_embed_peer_texts_uses_api_embed_texts(monkeypatch):
    """MAIN (无后缀, gemini) spec 走 _eng.embed_texts → 3072 维 API 嵌入。"""
    monkeypatch.setattr(
        ns,
        "EMBEDDING_CONFIG",
        {
            "base_url": "https://yunwu.ai/v1",
            "api_key": "fake-key",
            "model": "gemini-embedding-2-preview",
            "text_pipeline_version": "v3-2026-06-27-gemini",
        },
    )
    monkeypatch.setattr(ns._eng, "embed_texts", _fake_embed(dim=3072))

    emb = ns._embed_peer_texts(["alpha", "beta"], year=2020)

    assert emb is not None
    assert emb.shape == (2, 3072)
    assert np.allclose(emb[:, 0], [0.0, 1.0])


def test_embed_peer_texts_lg_spec_routes_to_large(monkeypatch):
    """co-primary _lg spec 经同一 _eng.embed_texts API 路径 (3072 维)。"""
    captured = {}

    def _embed(texts, spec, **kwargs):
        captured["model"] = (spec or {}).get("model")
        return _fake_embed(dim=3072)(texts, spec, **kwargs)

    monkeypatch.setattr(ns._eng, "embed_texts", _embed)
    lg_spec = {
        "base_url": "https://yunwu.ai/v1",
        "api_key": "fake-key",
        "model": "text-embedding-3-large",
        "text_pipeline_version": "v1-2026-06-27-emb3large",
    }

    emb = ns._embed_peer_texts(["alpha", "beta"], year=2020, spec=lg_spec)

    assert emb is not None
    assert emb.shape == (2, 3072)
    assert captured["model"] == "text-embedding-3-large"


def test_embed_peer_texts_none_on_api_failure(monkeypatch):
    """API 路径异常 → _embed_peer_texts 优雅返回 None (轨列置 NaN, 不炸 stage)。"""
    def _boom(texts, spec, **kwargs):
        raise RuntimeError("simulated API failure")

    monkeypatch.setattr(ns._eng, "embed_texts", _boom)

    emb = ns._embed_peer_texts(["alpha", "beta"], year=2020)

    assert emb is None
