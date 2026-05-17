"""13_materialize_ctx.py — stage 13 thin shim (Plan E P4 A1, v3.6.0).

物化 content_ctx 列, 供 stage 14/15 双轨化使用。
所有逻辑见 news_process/pipeline/text/ctx_materializer.py。
"""
from news_process.pipeline.text.ctx_materializer import main

if __name__ == "__main__":
    main()
