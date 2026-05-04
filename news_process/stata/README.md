# `news_process/stata/` — Migrated to `papers_assets/<paper>/do/` (Phase 4a)

This directory previously held 5 Stata `.do` scripts that were used across
multiple research papers.  As of Phase 4a (2026-05-04), each `.do` file has
been migrated to the appropriate paper's asset directory and updated with
the standard path prelude (`global panel_dta`, `global out_dir`).

## Migration mapping

| Original path                              | New path                                                          |
|--------------------------------------------|-------------------------------------------------------------------|
| `stata/50_robustness_text2vec_stata.do`    | `papers_assets/bank_fintech_tone/do/50_robustness_text2vec_stata.do` |
| `stata/network_causal.do`                  | `papers_assets/brokerage_network/do/network_causal.do`            |
| `stata/strategic_differentiation.do`       | `papers_assets/strategic_diff/do/strategic_differentiation.do`    |
| `stata/text_coherence.do`                  | `papers_assets/strategic_diff/do/text_coherence.do`               |
| `stata/token_hidden_regression.do`         | `papers_assets/benefit_society/do/token_hidden_regression.do`     |

## Path correction

All 5 `.do` files referenced one of two stale paths:
- `output/40_panel_yearly.dta` (the actual file lived at `data/processed/40_panel_yearly.dta`)
- `output/40_panel_data.dta` (a file that has never existed — likely a planning leftover)

Phase 4a normalises both to `$panel_dta`, defaulting to
`../../../data/processed/40_panel_yearly.dta` (3 levels up from
`papers_assets/<paper>/do/` to `news_process/`, then into `data/processed/`).

`output/<x>.tex` references are likewise normalised to `$out_dir/<x>.tex`,
defaulting to `../output/` so each paper's outputs land in
`papers_assets/<paper>/output/`.

## Why this directory is preserved (not deleted)

Empty directories are invisible to git, so this README is the marker that
allows the migration history to remain discoverable from the project root
without `git log` archaeology.  Once Phase 5 (or a follow-up cleanup)
confirms no external scripts/notebooks reference `news_process/stata/`,
this entire directory can be removed.
