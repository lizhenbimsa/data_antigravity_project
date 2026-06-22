"""news_process.pipeline.features — Stage 25/26/27: 文章/银行-年特征.

- strategic_diff (25): 与最近邻同业的 TNIC 距离 (Guzman & Li 2023)
- policy_similarity (26): 银行-年文本 vs 权威政策语料的相似度
- benefit_society (27): 双极锚点投影 (Jha et al. 2026)

Stage 25/26/27 为 library-only (历史上无 `__main__`); Phase 2a 计划随
importlib 反射清理一并迁移到本包 (历史规划陈述)。

注: 原 text2vec_robust (stage 30 / 30_robustness_text2vec) 已于 2026-05-29
双模型重构时退役; _t2v 稳健 twin 列现由 stage 15 (policy_alignment) + stage 25
(strategic_diff) 主流程内联产出 (见 core/dag.py:264-272 退役注释)。
"""
