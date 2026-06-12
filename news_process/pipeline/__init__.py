"""news_process.pipeline — 主线: 原始新闻 -> 银行-年面板.

子包: preprocess, filtering, text, sentiment, features, panel,
falsification, audit, llm_archive。各阶段 runner 位于对应子包内,
暴露 ``main()`` 入口, 供根目录 thin shim (如 ``00_preprocessing.py``)
与编排器 ``run_pipeline_function.py`` 共同调用。
"""
