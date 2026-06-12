"""news_process.pipeline.text — 文本/上下文物化与嵌入工具.

包内模块:
    ctx_materializer:  stage 13 content_full/content_ctx 列物化, 供 stage 14/15
                       双轨化使用 (Plan E v3.6.0 P4 A1; v3.8.0 起两轨均 prepend 标题).
    embedding_engine:  双模型嵌入统一引擎 (主轨 API + _t2v 本地稳健轨, 穿透 LLMCache).
    article_sbert:     stage 30a article-level SBERT embeddings 持久化 (D 组前置).
    article_staleness: stage 18 article-level staleness 双指标
                       (surface MinHash + semantic Faiss).
"""
