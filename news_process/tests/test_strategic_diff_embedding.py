from __future__ import annotations

import numpy as np

from news_process.pipeline.features import strategic_diff as sd

# v3.14.0 (all-API-embedding): 本地嵌入模型 (text2vec/_t2v, bge-m3/_bge) 与全部本地
# 推理机器 (encode_local / sentence_transformers 注入) 已彻底移除。嵌入统一走
# _eng.embed_texts(texts, spec) 纯 API 路径 (gemini MAIN 3072 维 + text-embedding-3-large
# _lg 3072 维 co-primary)。本测试改 mock _eng.embed_texts (API 路径), 不再注入 fake
# sentence_transformers。


def _fake_embed(dim: int = 3072):
    """构造一个确定性的 fake embed_texts (API 路径替身)。

    返回每条文本一个 dim 维向量, 前两维携带可断言的确定性信号
    (idx, len(text)), 其余补零 → 不依赖任何在线 API / 本地模型。
    """

    def _embed(texts, spec, **kwargs):
        texts = list(texts)
        out = np.zeros((len(texts), dim), dtype=np.float32)
        for idx, text in enumerate(texts):
            out[idx, 0] = float(idx)
            out[idx, 1] = float(len(text))
        return out

    return _embed


def test_chunk_pooling_uses_api_embed_texts(monkeypatch):
    """MAIN (无后缀, gemini) spec 走 _eng.embed_texts → 3072 维 API 嵌入。"""
    monkeypatch.setattr(
        sd,
        "EMBEDDING_CONFIG",
        {
            "base_url": "https://yunwu.ai/v1",
            "api_key": "fake-key",
            "model": "gemini-embedding-2-preview",
            "text_pipeline_version": "v3-2026-06-27-gemini",
        },
    )
    monkeypatch.setattr(sd._eng, "embed_texts", _fake_embed(dim=3072))

    emb = sd._embed_texts_with_chunk_pooling(["alpha", "beta"], log_prefix="test")

    assert emb is not None
    assert emb.shape == (2, 3072)
    assert np.allclose(emb[:, 0], [0.0, 1.0])


def test_lg_spec_routes_to_text_embedding_3_large(monkeypatch):
    """co-primary _lg spec 经同一 _eng.embed_texts API 路径独立嵌入 (3072 维)。"""
    captured = {}

    def _embed(texts, spec, **kwargs):
        captured["model"] = (spec or {}).get("model")
        return _fake_embed(dim=3072)(texts, spec, **kwargs)

    lg_spec = {
        "base_url": "https://yunwu.ai/v1",
        "api_key": "fake-key",
        "model": "text-embedding-3-large",
        "text_pipeline_version": "v1-2026-06-27-emb3large",
    }
    monkeypatch.setattr(sd._eng, "embed_texts", _embed)

    emb = sd._embed_texts_with_chunk_pooling(
        ["alpha", "beta"], spec=lg_spec, log_prefix="test-lg")

    assert emb is not None
    assert emb.shape == (2, 3072)
    assert captured["model"] == "text-embedding-3-large"
