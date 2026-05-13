from __future__ import annotations

import sys
import types

import numpy as np

from news_process.pipeline.features import strategic_diff as sd


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
        sd,
        "EMBEDDING_CONFIG",
        {
            "base_url": "local",
            "api_key": "local",
            "model": "fake-local-model",
            "batch_size": 8,
        },
    )
    monkeypatch.setattr(sd, "_LOCAL_EMBEDDING_MODEL", None)

    emb = sd._embed_texts_with_chunk_pooling(["alpha", "beta"], log_prefix="test")

    assert emb.shape == (2, 2)
    assert np.allclose(emb[:, 0], [0.0, 1.0])
