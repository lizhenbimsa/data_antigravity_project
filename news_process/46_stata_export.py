"""stage 46 stata_export 的 thin shim (plan v14 §9.1)。

v3.2.0 BREAKING: 把 stage 45 panel parquet 转为 Stata .dta + value labels.
实现委托给 news_process.pipeline.panel.stata_export.main()。

详见底层模块 news_process/pipeline/panel/stata_export.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""
from news_process.pipeline.panel.stata_export import main

if __name__ == '__main__':
    main()
