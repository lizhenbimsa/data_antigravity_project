"""news_process.pipeline.preprocess — 阶段 00: 数据摄入、规范化与去重。

Phase 1: ``runner.py`` 暴露 ``main()`` (原 ``00_preprocessing.py`` 正文)。
Phase 2c: 拆分为 ``load.py`` / ``normalize.py`` / ``filter.py`` / ``dedup.py``
及精简 ``runner.py``。
"""
