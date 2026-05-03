"""news_process.pipeline.features — Stages 25/26/27/30: article-level features.

- strategic_diff (25): TNIC distance to nearest peers (Guzman & Li 2023)
- policy_similarity (26): firm-year vs authoritative policy corpus
- benefit_society (27): bipolar anchor projection (Jha et al. 2026)
- text2vec_robust (30): local-embedding dual-track robustness

Stages 25/26/27 are library-only (no `__main__` historically); Phase 2a will
migrate them to this package alongside the importlib reflection purge.
Stage 30 has its own `__main__`; Phase 1 already shims it here.
"""
