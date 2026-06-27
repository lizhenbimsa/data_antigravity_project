"""news_process.pipeline.text — 文本/上下文物化与嵌入工具.

包内模块:
    ctx_materializer:  stage 13 content_full/content_ctx/content_ss 列物化, 供
                       stage 14/15 三轨化 (full/ctx/ss) 使用
                       (Plan E v3.6.0 P4 A1; v3.8.0 起各轨均 prepend 标题;
                       v3.9.0 新增第三轨 content_ss = 标题 + 含"目标银行∧金科词"
                       同句 ±N 句窗, 无共现→镜像 ctx 回退全文, flag ss_is_fallback).
    embedding_engine:  co-primary 双 API 嵌入统一引擎 (v3.14.0: gemini 无后缀 ⟂
                       text-embedding-3-large `_lg`, 跨厂商对等; 零本地模型, 穿透 LLMCache).
    article_sbert:     stage 25 article-level SBERT embeddings 持久化 (v3.14.0 双轨 API
                       dual-emit: emb_{full,ctx,ss} + `_lg`; D 组前置).
    article_staleness: stage 26 article-level staleness 双指标 (surface MinHash 非嵌入,
                       无 `_lg`; semantic Faiss 双轨 semantic_staleness + `_lg`).
"""
