"""14_materialize_ctx.py — stage 14 thin shim (Plan E P4 A1, v3.6.0).

物化 content_full / content_ctx / content_ss 列, 供下游三轨化 (full/ctx/ss) 使用。
所有逻辑见 news_process/pipeline/text/ctx_materializer.py。

详见底层模块 pipeline/text/ctx_materializer.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""
import pathlib
import sys

# F-5 (N15, 2026-07-18): sys.path 注入先于包导入 (81/82 同款) — 未 editable install 的
# 裸解释器直跑本 shim 也能解析 news_process 包; 注入必须在 from-import 之前才有效。
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    from news_process.pipeline.text.ctx_materializer import main
    main()
