from __future__ import annotations

import sys
import types

import numpy as np

from news_process.pipeline.panel import network_spillover as ns


class _FakeSentenceTransformer:
    def __init__(self, model_id):
        self.model_id = model_id

    def encode(self, texts, batch_size=32, show_progress_bar=False):
        return np.asarray(
            [[float(idx), float(len(text))] for idx, text in enumerate(texts)],
            dtype=np.float32,
        )


def test_embedding_peer_texts_uses_local_config_before_api(monkeypatch):
    fake_module = types.SimpleNamespace(SentenceTransformer=_FakeSentenceTransformer)
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)
    monkeypatch.setattr(
        ns,
        "EMBEDDING_CONFIG",
        {
            "base_url": "local",
            "api_key": "local",
            "model": "fake-local-model",
            "batch_size": 8,
        },
    )
    monkeypatch.setattr(ns, "_LOCAL_EMBEDDING_MODEL", None)

    async def _api_should_not_be_used(*args, **kwargs):
        raise AssertionError("local embedding config should not call HTTP API")

    monkeypatch.setattr(ns, "_get_embeddings_api", _api_should_not_be_used)

    emb = ns._embed_peer_texts(["alpha", "beta"], year=2020)

    assert emb is not None
    assert emb.shape == (2, 2)
    assert np.allclose(emb[:, 0], [0.0, 1.0])
