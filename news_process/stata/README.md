# `news_process/stata/` — Stata 变量标注脚本流水线 (含 Phase 4a 跨论文 .do 迁移历史)

This directory serves two purposes:
(a) it hosts the **active variable-labelling pipeline** — `00_load_panel_data.do` …
`15_label_complete.do` plus the orchestrator `99_master.do` — which loads
`data/processed/40_panel_yearly.dta` and applies all variable labels, saving
`40_panel_yearly_labeled.dta`;
(b) it records the **Phase 4a (2026-05-04) migration** of 5 earlier `.do`
scripts to per-paper asset directories (mapping table below). Phase 4a 之后
(commit 19341bcd) 本目录被重新用于存放变量标注脚本, 因此现在非空。Those 5
migrated files were each updated with the standard path prelude
(`global panel_dta`, `global out_dir`).

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

## Current contents — active variable-labelling pipeline (do NOT delete)

This directory is NOT empty.  Beyond the migration history above, it now hosts
a live Stata variable-labelling pipeline that runs against
`data/processed/40_panel_yearly.dta`:

- `00_load_panel_data.do` — loads the panel `.dta`.
- `01_label_variables.do` … `15_label_complete.do` — 15 sequential label
  scripts (LLM/dict/BERT sentiment, text features, media, geography, Bartik
  IV/DID, network, strategic, benefit/token, washing/disagreement, etc.).
- `99_master.do` — master orchestrator that runs the label scripts in order
  and saves the labelled panel.

Because the directory holds this live pipeline, it must NOT be deleted; the
earlier "this entire directory can be removed" guidance applied only to the
pre-refill state and is no longer valid.
