# P0.1 Audit Memo — Per-Paper `.do` Script Methodology Inventory

Captured 2026-05-15 from reading the existing `papers_assets/<paper>/do/*.do` files
end-to-end (excluding `bank_fintech_tone/do/falsification_template.do.tmpl` — that
is the 1016-line **template** which is the production target form for P1
parameterization, not a regular `.do`).

## 1. Shared conventions (all 4 derivative papers + main)

| Convention | Value |
|---|---|
| Panel data path (default) | `../../../data/processed/40_panel_yearly.dta` |
| Output dir (default) | `../output` (created via `capture mkdir`) |
| Panel ID variable | `target_bank` → `encode … gen(bank_id)` → `xtset bank_id year` |
| Default FE | `absorb(bank_id year)` (two-way) |
| Estimator (reduced form) | `reghdfe` (ssc install reghdfe) |
| Estimator (IV) | `ivreghdfe` (ssc install ivreghdfe) |
| Cluster level | `bank_id` (most papers) or `prov_id` (brokerage_network) |
| Tables tool | `esttab` / `estout` |
| User-fillable globals | `$panel_dta`, `$out_dir`, `$controls`, sometimes Y |

## 2. Per-paper signatures

### 2.1 benefit_society — `token_hidden_regression.do` (187 lines)

**Methodology**: 4-layer regression architecture (Distel 2026 + Westphal-Zajac 2001 + Jha-Liu-Manela 2026)

| Layer | Models | Specification |
|---|---|---|
| 1 Main | m1 (sim), m2 (interact) | `reghdfe ROA article_sim_mean $controls, absorb(bank_id year) vce(cluster bank_id)` |
| 2 Mechanism | m3-m5 (token/hidden/subst P50) | `reghdfe {CAR\|ROA} {token_adopt_kw_p50\|hidden_adopt_kw_p50\|subst_adopt_kw_p50} $controls, ...` |
| 3 Robustness | m6-m8 (P25/P75/INT) | `reghdfe ROA token_adopt_kw_p{25,75} hidden_adopt_kw_p{25,75} $controls, ...` |
| 4 Attitude | m9-m12 (benefit Full/Ctx/Frac) | `reghdfe ROA benefit_mean_{full\|ctx} ...` |

**Default DV**: ROA (m1-m12), CAR (m3 only)
**Main DV variants in robustness**: ROA / CAR (no Z_score in this .do)
**Controls suggestion**: `ln_news_coverage media_breadth n_articles`
**Cluster**: `bank_id`
**Output**: `token_hidden_results.tex` (single combined esttab)

### 2.2 brokerage_network — `network_causal.do` (345 lines)

**Methodology**: Bramoullé-2009 Network 2SLS + Manski-1993 reflection + DCEP/Sandbox heterogeneity

| Section | Models | Specification |
|---|---|---|
| A1 OLS baseline | `ols_baseline` | `reghdfe Y peer_tone_lag1_full $controls, absorb(bank_id year) vce(cluster prov_id)` |
| A2 Net 2SLS | `iv_net2sls` | `ivreghdfe Y (peer_tone_lag1_full = peer_tone_2nd_lag1_full) $controls, absorb(bank_id year) cluster(prov_id) ffirst` |
| B DCEP × centrality | b1 (Btw), b2 (Constraint), b3 (Brokerage) | `reghdfe Y dcep_x_L_<cent> dcep_post L_bank_<cent> $controls, ...` |
| C Sandbox × centrality | c1, c2, c3 | same as B, replacing dcep → sandbox |
| D Ctx robustness | `iv_ctx` | `ivreghdfe Y (peer_tone_lag1_ctx = peer_tone_2nd_lag1_ctx) ...` |

**Default DV**: Y (placeholder, user-fillable); commentary mentions ROA, NPL_ratio, Z_score
**Endogenous**: peer_tone_lag1_full (1st-order peer spillover)
**IV**: peer_tone_2nd_lag1_full (2nd-order, Bramoullé exclusion via intransitive triads)
**Centrality vars** (lagged 1 period): L_bank_between, L_bank_constraint, L_brokerage
**Treatment**: dcep_post, sandbox_post
**Controls suggestion**: `ln_news_coverage media_hhi bank_scale_ord`
**Cluster**: `prov_id` (province-level, Cameron-Miller 2015 rationale)
**Output**: `$out_dir/network_causal.tex` + screen `esttab`

### 2.3 strategic_diff — `strategic_differentiation.do` (268) + `text_coherence.do` (119)

#### 2.3.1 strategic_differentiation.do — Guzman-Li 2023 + Hoberg-Phillips 2016

| Section | Models | Specification |
|---|---|---|
| Descriptives | `sum`, `pwcorr` | strat_diff_n* / strat_sim_max / strat_fluidity |
| 3 Baseline | m1, m2 (+ fluidity), m3 (+ sim_max + fluidity) | `reghdfe Y strat_diff_n5 [strat_fluidity] [strat_sim_max] $controls, ...` |
| 4 N sensitivity | n3-n7 | `foreach n of numlist 3/7 { reghdfe Y strat_diff_n`n' $controls, ... }` |
| 5 Method robustness | ra (jieba), rb (LDA), rc (Embedding) | `reghdfe Y strat_diff_n5_{w\|lda\|emb} $controls, ...` |
| 6 SOE heterogeneity | (no eststo) | `reghdfe Y strat_diff_n5 strat_x_soe is_soe $controls, ...` |
| 7 Bartik IV | (no eststo) | `ivreghdfe Y (llm_vote_tone_full = bartik_type_iv_full) strat_diff_n5 strat_fluidity $controls, ...` |
| 8 Centroid (谢佳松 2025) | cd1, cd_{tfidf_c, tfidf_w, lda, emb} | `reghdfe Y centroid_diff_<method> $controls, ...` |
| 9 Full vs Ctx | nn_full/nn_ctx, cd_full/cd_ctx, horse_race | both tracks side by side |
| 10 Authority policy | auth_{tfidf_c, tfidf_w, lda, emb}_f | `reghdfe Y auth_sim_<method>_full $controls, ...` |

#### 2.3.2 text_coherence.do — 欧阳-胡 2024 + Hoberg-Phillips 2016

| Section | Models | Specification |
|---|---|---|
| Baseline | coh1 | `reghdfe Y coh_tfidf_c_full $controls, ...` |
| Mechanism | coh2 (tone × coh) | `reghdfe Y llm_vote_tone_full coh_tfidf_c_full tone_x_coh_full $controls, ...` |
| Method robust | coh_{tfidf_c, tfidf_w, lda, emb}_full | 4-method side-by-side |
| Ctx robustness | coh_ctx | `reghdfe Y coh_tfidf_c_ctx $controls, ...` |
| SOE het | (no eststo) | `reghdfe Y coh_tfidf_c_full coh_x_soe is_soe $controls, ...` |

**Default DV (both .do)**: Y (placeholder)
**Main RHS variables**: strat_diff_n5, strat_fluidity, coh_tfidf_c_full
**Controls suggestion**: `ln_news_coverage media_hhi bank_scale_ord`
**Cluster**: `bank_id`
**Heterogeneity var**: `is_soe`
**Bartik IV**: `bartik_type_iv_full` → `llm_vote_tone_full`

### 2.4 llm_peer — NO existing `.do` (only `.gitkeep`)

**Methodology to design** (Cao-Li-Wang-Zhao 2025): LLM-generated peer competition IV

**Variables available** (from `papers/llm_peer/__init__.py` + `tables.py`):
- `llm_peer_tone_iv_full` — primary IV (LLM peer leave-one-out tone)
- `llm_peer_coverage_iv` — coverage-weighted variant
- `llm_peer_count` — # LLM-identified peers
- `peer_compete_idx` — competition intensity
- `llm_peer_tone_iv_full_{70,75,80,85,90}` — cutoff sensitivity

**Designed methodology for P1 main_regression.do.tmpl**:
1. OLS baseline: `reghdfe ROA llm_vote_tone_full $controls, absorb(bank_id year) vce(cluster bank_id)`
2. Main IV 2SLS: `ivreghdfe ROA (llm_vote_tone_full = llm_peer_tone_iv_full) $controls, absorb(bank_id year) cluster(bank_id) ffirst`
3. Cutoff sensitivity: 5 specs (cutoff 70/75/80/85/90)
4. Coverage-IV robustness: substitute `llm_peer_coverage_iv`
5. Peer competition index control: add `peer_compete_idx`
6. SOE heterogeneity: `is_soe` interaction
7. Ctx-track robustness: replace `_full` → `_ctx`

## 3. Cross-paper consistency observations

| Dimension | Consistent across all 4 derivatives | Outlier |
|---|---|---|
| Cluster level | `bank_id` (3 papers) | brokerage_network uses `prov_id` |
| FE | `bank_id year` (all 4) | — |
| Default DV | `ROA` (project convention) | strategic_diff uses placeholder Y |
| Controls suggestion | `ln_news_coverage` + paper-specific | benefit_society uses `media_breadth` instead of `media_hhi` |
| Het var | `is_soe` (3 papers) | benefit_society does not have explicit het section |
| Bartik IV | `bartik_type_iv_full` | only strategic_diff explicitly uses it |
| Path prelude | identical 8-line Phase 4a block | — |

## 4. P1 parameterization recommendation

Given the 4 papers share ~70% of structure, **Scheme A** (extend `_KNOWN_PLACEHOLDERS`) is viable.
Three tiers of placeholders required:

### Tier 1 — universal (already exist in main)
`{{PROJECT_ROOT}}`, `{{MAIN_LOCUS_TRACK}}`, `{{MAIN_SUBST_TRACK}}`, `{{MAIN_SENT_TRACK}}`

### Tier 2 — paper-level (new in P1)
`{{PAPER_ID}}`, `{{MAIN_DV}}`, `{{CONTROLS}}`, `{{CLUSTER_VAR}}`, `{{HET_VAR}}`

### Tier 3 — paper-specific (new in P1, sparse per paper)
- benefit_society: `{{ATTITUDE_VAR}}` = `benefit_mean_full`
- brokerage_network: `{{MAIN_ENDOG}}` = `peer_tone_lag1_full`, `{{MAIN_IV}}` = `peer_tone_2nd_lag1_full`
- strategic_diff: `{{MAIN_DIFF_VAR}}` = `strat_diff_n5`, `{{BARTIK_IV}}` = `bartik_type_iv_full`
- llm_peer: `{{LLM_PEER_IV}}` = `llm_peer_tone_iv_full`, `{{COMPETE_IDX}}` = `peer_compete_idx`

## 5. Risks identified

1. **strategic_diff Y is unfilled** — user-side global `Y` is a placeholder, not concrete. P1 templates need `{{MAIN_DV}}` default = `ROA` with override path.
2. **benefit_society uses CAR for short-term, ROA for long-term** — single MAIN_DV insufficient; need `{{ROBUSTNESS_DV}}` or split mechanism table.
3. **brokerage_network cluster = prov_id, not bank_id** — generic template's `vce(cluster bank_id)` will silently produce wrong SE. Must templatize.
4. **llm_peer has zero prior `.do`** — designed methodology in §2.4 is novel; needs separate validation against Cao 2025 RAS replication code (not currently in repo).
5. **Existing 14 templates were written for main paper's locus/subst/sent triad** — derivative papers don't have this 3D spec; need to make those placeholders optional or paper-conditional.

## 6. Output stata path inside .do

All existing .do files write to `$out_dir` (default `../output`), which under our new layout
maps to `papers_assets/<paper>/output/`. With P0.2's `output/{tables,figures,logs}` subdir
contract, the existing .do files would put `.tex` directly in `output/` root, not in
`output/tables/`. **Decision for P1**: new templates should write to `$out_dir/tables/` and
`$out_dir/figures/` respectively, updating the prelude block:

```stata
if "$tables_dir" == "" { global tables_dir "$out_dir/tables"; capture mkdir "$tables_dir" }
if "$figures_dir" == "" { global figures_dir "$out_dir/figures"; capture mkdir "$figures_dir" }
```

Existing .do files left untouched per P-plan §10 invariant.
