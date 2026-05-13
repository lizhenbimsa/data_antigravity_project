from __future__ import annotations

import sys
import types

import numpy as np

from news_process.pipeline.features import benefit_society as bs


class _FakeSentenceTransformer:
    def __init__(self, model_id):
        self.model_id = model_id

    def encode(self, texts, batch_size=32, show_progress_bar=False):
        return np.asarray(
            [[float(idx), float(len(text))] for idx, text in enumerate(texts)],
            dtype=np.float32,
        )


def test_local_embedding_config_uses_sentence_transformers(monkeypatch):
    fake_module = types.SimpleNamespace(SentenceTransformer=_FakeSentenceTransformer)
    monkeypatch.setitem(sys.modules, "sentence_transformers", fake_module)
    monkeypatch.setattr(
        bs,
        "EMBEDDING_CONFIG",
        {
            "base_url": "local",
            "api_key": "local",
            "model": "fake-local-model",
            "batch_size": 8,
        },
    )
    monkeypatch.setattr(bs, "_LOCAL_EMBEDDING_MODEL", None)

    async def _api_should_not_be_used(*args, **kwargs):
        raise AssertionError("local embedding config should not call HTTP API")

    monkeypatch.setattr(bs, "_get_embeddings_api", _api_should_not_be_used)

    emb = bs._get_embeddings(["alpha", "beta"], [1, 1], log_prefix="test")

    assert emb.shape == (2, 2)
    assert np.allclose(emb[:, 0], [0.0, 1.0])
