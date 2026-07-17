"""stage 46 stata_export 的 thin shim (plan v14 §9.1)。

v3.2.0 BREAKING: 把 stage 45 panel parquet 转为 Stata .dta + value labels.
实现委托给 news_process.pipeline.panel.stata_export.main()。

详见底层模块 news_process/pipeline/panel/stata_export.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""
import pathlib
import sys

# F-5 (N15, 2026-07-18): sys.path 注入先于包导入 (81/82 同款) — 未 editable install 的
# 裸解释器直跑本 shim 也能解析 news_process 包; 注入必须在 from-import 之前才有效。
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

if __name__ == '__main__':
    from news_process.pipeline.panel.stata_export import main
    main()
