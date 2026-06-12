"""news_process.pipeline.falsification — Stage 51 证伪检验 (falsification test)。

Phase 2c 把 ``51_falsification_test.py`` 的函数体迁到本包的 ``controls.py``;
项目根目录的同名文件保留为 thin CLI shim。

Phase 4c (2026-05-04) 进一步把内嵌的 Stata 回归模板抽到
``papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl``,
``controls.py`` 因此大幅瘦身。

Phase 4c 同时显式*取消*了原计划的 Phase 2c-2 helper 拆分子任务:
``controls.py`` 内的 ``build_non_fintech`` / ``aggregate_non_fintech`` /
``merge_to_panel`` 是证伪检验专用函数 (不是跨论文 helper), 搬到
``pipeline/panel/falsification_helpers.py`` 并不会提高复用性。
因此 ``controls.py`` 仍是 stage 51 全部逻辑的唯一归属地。

白话: "证伪检验"是论文的反向自检 — 故意拿"不该有效应"的对照组
(非金融科技新闻) 跑同样的回归, 如果对照组也跑出显著效应, 说明主结果
可能是假象。本包就是干这件事的代码。
"""
