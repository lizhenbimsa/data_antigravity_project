"""news_process.validation — 稳健性 / 校验阶段实现包。

当前状态 (Phase 7b 迁移已完成)
----------------------------------------------
Phase 7b 迁移已完成: 各校验阶段的权威实现体 (canonical body) 现位于
本包内 (如 ``decay_sensitivity.py``, ``radius_sensitivity.py``,
``threshold.py``, ``tone_validation.py``, ``media_diversity.py``,
``dedup_threshold.py``, ``entity_masking.py``, ``prompt_sensitivity.py``
等)。每个模块顶部均带有
"本模块由原 root script ... 迁入 (Phase 7b)" 的迁移说明。

项目根目录下对应的 ``NN_*.py`` 文件是薄 ``importlib`` shim, 仅委托到
本包内的模块; 校验流水线经 ``run_pipeline_validation.py`` 消费
``news_process.core.dag.STAGES_VALIDATION`` 来发现它们。

注意
-----
1. ``import news_process.validation`` 立即可解析; 各模块可直接导入
   (如 ``python -m news_process.validation.media_diversity``)。
2. 本目录是一个契约标记 (contract marker) — 对它的改动局限在单一
   子树内, 不波及项目根目录。
"""
