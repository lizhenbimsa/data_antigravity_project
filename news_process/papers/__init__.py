"""news_process.papers — 多论文代码外壳 (Phase 3).

每个论文子包包含 analysis.py / figures.py / tables.py 三件套, 声明其所需
pipeline 阶段与后处理逻辑 (历史上设想的 per-paper dag.py 未落地, 阶段调度
统一走 ``core/dag.py``)。非代码研究产物 (do/, outputs/, drafts/) 单独放在
项目顶层 ``papers_assets/`` 目录下, 保持可导入的 Python 包干净。
"""
