"""news_process.pipeline.features — Stages 25/26/27: article-level features.

- strategic_diff (25): TNIC distance to nearest peers (Guzman & Li 2023)
- policy_similarity (26): firm-year vs authoritative policy corpus
- benefit_society (27): bipolar anchor projection (Jha et al. 2026)

Stages 25/26/27 are library-only (no `__main__` historically); Phase 2a will
migrate them to this package alongside the importlib reflection purge.

注: 原 text2vec_robust (stage 30 / 30_robustness_text2vec) 已于 2026-05-29
双模型重构时退役; _t2v 稳健 twin 列现由 stage 15 (policy_alignment) + stage 25
(strategic_diff) 主流程内联产出 (见 core/dag.py:307-312 退役注释)。
"""
