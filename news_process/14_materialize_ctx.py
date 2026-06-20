"""14_materialize_ctx.py — stage 14 thin shim (Plan E P4 A1, v3.6.0).

物化 content_ctx 列, 供 stage 15/16 双轨化使用。
所有逻辑见 news_process/pipeline/text/ctx_materializer.py。

详见底层模块 pipeline/text/ctx_materializer.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""
from news_process.pipeline.text.ctx_materializer import main

if __name__ == "__main__":
    main()
