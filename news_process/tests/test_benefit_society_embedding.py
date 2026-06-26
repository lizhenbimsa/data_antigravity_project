from __future__ import annotations

import sys
import types

import numpy as np

from news_process.pipeline.features import benefit_society as bs


class _FakeSentenceTransformer:
    def __init__(self, model_id, device=None):
        self.model_id = model_id
        self.device = device

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
    # W13 (2026-06-26): 删除对 _LOCAL_EMBEDDING_MODEL / _get_embeddings_api (已删死符号) 的
    # monkeypatch。本地 EMBEDDING_CONFIG 下 _get_embeddings 经 _eng.embed_texts → encode_local
    # → (fake) sentence_transformers, 不走任何 API → 无需再 patch 死的 API 函数。

    emb = bs._get_embeddings(["alpha", "beta"], [1, 1], log_prefix="test")

    assert emb.shape == (2, 2)
    assert np.allclose(emb[:, 0], [0.0, 1.0])
