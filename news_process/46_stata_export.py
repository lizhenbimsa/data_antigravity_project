"""Thin shim for stage 46 stata_export (plan v14 §9.1).

v3.2.0 BREAKING: 把 stage 45 panel parquet 转为 Stata .dta + value labels.
Delegates to news_process.pipeline.panel.stata_export.main().
"""
from news_process.pipeline.panel.stata_export import main

if __name__ == '__main__':
    main()
