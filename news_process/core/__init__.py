"""news_process.core — 共享内核 (shared kernel)。

历史: 本包替代了 Phase 0 之前的 ``utils/helpers.py`` mega-module
(Phase 1-3 期间 ``utils/<module>.py`` forward shims 已全部退役, ``utils/``
目录移除; 历史拆分来源见各子模块文件头的 "来源于 utils/..." 注释)。

提供 config loading / logging / parallelism / locking / caching / schemas 等
跨上游模块共享的设施; 各 public utility 的 canonical home 见对应子模块的
module-level docstring。
"""
