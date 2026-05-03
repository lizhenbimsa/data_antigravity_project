"""news_process.pipeline.filtering — Stages 11/12/14/15: domain filtering.

- bank_news (11): bank-name keyword filter
- fintech_news (12): fintech keyword filter (full + selected outputs)
- intensity (14): TF-IDF + SIF intensity scoring
- policy_alignment (15): article-level policy semantic alignment
  (NOTE: 15 has importlib reflection of 41 -> deferred to Phase 2a migration)
"""
