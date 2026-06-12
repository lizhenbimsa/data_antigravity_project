"""news_process.pipeline.panel — Stages 41-48 + monolithic 45 -> bank-year panel.

Phase 1: stage 41-48 与 45 当时仍留在项目根目录 (importlib 反射保持原位加载)。
Phase 2a: 库文件 (41/42/43/44/46/47/48) 迁入本包并重命名; 45 的函数体移入
``runner.py``; 13 处 importlib 反射被原子替换为常规 import。
Phase 2b (originally planned ``runner.py`` <=500 / ``extras.py`` <=700 /
``export.py`` <=300 行拆分) **未执行**; ``runner.py`` 与 ``export.py`` 至今
仍是 monolithic god function, 待 Plan-r3 P1-7 真正落地。
Phase 2c: stage 51 共享的 panel 组装逻辑抽到 ``falsification_helpers.py``
(与 runner.py 物理隔离)。

白话: 这个包负责把每篇文章的各类指标汇总成"每家银行每年一行"的面板表,
再导出给 Stata 跑回归。上面记录的是历史搬家过程: 代码从项目根目录搬进
这个包, 但原计划的"把巨型文件拆小"一步一直没做。
"""
