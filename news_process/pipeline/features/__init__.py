"""news_process.pipeline.features — Stage 25/26/27: 文章/银行-年特征.

- strategic_diff (25): 与最近邻同业的 TNIC 距离 (Guzman & Li 2023)
- policy_similarity (26): 银行-年文本 vs 权威政策语料的相似度
- benefit_society (27): 双极锚点投影 (Jha et al. 2026)

Stage 25/26/27 为 library-only (历史上无 `__main__`); Phase 2a 计划随
importlib 反射清理一并迁移到本包 (历史规划陈述)。

注: v3.14.0 (2026-06-27, all-API-co-primary) 整体移除本地嵌入稳健轨 text2vec (`_t2v`)
与 bge-m3 (`_bge`); 嵌入改为 gemini (MAIN, 无后缀) ⟂ text-embedding-3-large (`_lg`)
跨厂商对等 co-primary 双轨, 各 producer 内联并列产出 (无后缀 + `_lg`)。
"""
