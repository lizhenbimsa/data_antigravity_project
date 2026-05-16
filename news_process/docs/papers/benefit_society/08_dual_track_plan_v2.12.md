# benefit_society Full Dual-Track Plan v2.12 (Audit-Frozen)

> **Status**: Frozen 2026-05-16 after 14 audit rounds (59 findings).
> See [07_audit_log.md](./07_audit_log.md) for finding-by-finding ledger.

## 0. Scope summary

Bring `benefit_society` derivative paper from Phase 0 scaffolding (commit 23564a6) to **full v3.2.0 dual-track compliance** matching the conventions used by main paper `bank_fintech_tone`:

- Article-level + bank-year-level inter-track agreement (Tier-A appendix Table A1)
- Main spec dual-track switch sensitivity (Table A2 — 2-spec specialized for benefit_society, not 8-spec from main paper)
- Coefplot dual-track visual (Figure 2)
- Mechanism / shrinkage / dimension extended to ctx track
- PAP v1.0-final with H3 three-tuple test (mean + pos_frac + neg_frac), wild cluster bootstrap inference

## 1. Decision register (审计员断定)

| DP | Decision | Rationale |
|---|---|---|
| DP-1 | DV = ROA (main) + CAR (robustness) | CBIRC public, no Wind license |
| DP-2 | Table 2 = M1-M6 single-track progressive | Aligns with main paper convention |
| DP-3 | `_common` templates copied + specialized per paper | Avoids main paper pollution |
| DP-4 | Data source = CBIRC + annual reports | No external license |
| DP-5 | OSF registration deferred to user manual trigger | Out of automation scope |
| DP-6 | Version bump = v3.2.1 (patch) | semver-aligned |
| DP-7 | Cohort = 84 banks "as-observed" (drop "non-listed SME" qualifier from PAP RQ) | Avoid 30h re-cohort cost |
| DP-8 | Cohort locked via `data/raw/cohort/benefit_society_84banks.csv` manifest | Prevents stage 00 drift |
| DP-9 | Add `is_listed` dummy + 2-way heterogeneity (`is_listed × bank_type`) | Partial narrative rescue |
| DP-10 | Golden snapshot regenerated once; both papers must pass post-regen | Avoid dual-baseline complexity |
| DP-11 | Audit terminates on 5 consecutive perfect rounds | Achieved at R14 |

## 2. Phase breakdown (execution order)

Concrete implementation phases A–J as tracked in TodoWrite. Each phase ends with a self-audit step. The plan v2.12 is implemented via this automation pass (2026-05-16).

| Phase | Files touched | Self-audit trigger |
|---|---|---|
| A | `news_process/docs/papers/benefit_society/07*.md`, `08*.md` | Doc lint |
| B | `news_process/docs/papers/benefit_society/06_pap_draft.md` | PAP cross-link check |
| C | `news_process/data/raw/cohort/benefit_society_84banks.csv` | Manifest unique key |
| D | `news_process/papers/_common/derivative_replication.py`, `stata_runner.py` | `pytest test_derivative_replication.py` |
| E | `news_process/papers/_common/stata_templates/benefit_society/{11,13,14,17,18}_*.do.tmpl`, new `00_install_packages.do.tmpl` | Template placeholder regression |
| F | `news_process/papers/_common/stata_templates/benefit_society/{20_tableA1_*,21_tableA2_*,31_figure2_*,17b_table8b_*}.do.tmpl` | Instantiate dry-run |
| G | `news_process/papers/benefit_society/{dimension_analysis,shrinkage}.py`, `news_process/pipeline/features/benefit_society.py` | Function-level unit tests |
| H | `news_process/papers/benefit_society/{tables,figures,analysis}.py`, `00_master.do.tmpl`, `README.md` | Loader smoke test |
| I | `news_process/tests/test_dual_track_*.py` (5 new), `pytest` baseline | Full test suite |
| J | 7-round self-audit | Convergence to perfect |

## 3. Phase-J audit termination

The execution-time audit (Phase J) re-uses the methodology from R1–R14 plan-time audit but on **delivered artifacts**:

- Round J1: code-quality + ruff
- Round J2: pytest fast-marker subset
- Round J3: integration tests
- Round J4: stata template instantiation dry-run
- Round J5: PAP cross-link + bibliography
- Round J6: golden snapshot reproducibility
- Round J7: final consistency sweep

Terminate on 7 consecutive zero-issue rounds OR exhaust budget at 15 rounds, whichever first.

## 4. Out-of-scope (followup)

- F-V2-B1 b-path / c-path cohort re-sampling (would need stage 00 re-run)
- F-R6-H1 anchor re-generation if leakage confirmed (PAP §9 disclosure path chosen instead)
- Wind-license-dependent NCD spread DV (DP-1.a abandoned)
- OSF actual DOI registration (user manual step)
- `.gitignore` followup F-R12-L1
- Pre-existing 8 long-named columns latent bug (F-V2-L4) — independent issue

## 5. Test-baseline contract

- Pre-execution baseline: **1506 tests collected** (CLAUDE.md notes 1153 passed + 6 skipped).
- Post-execution target: baseline ± new dual-track tests; **0 main-paper regressions**.
- Acceptance gate: `pytest news_process/tests/ -m "fast or integration"` exits 0.

## 6. Synthetic data declaration

P0.2 financial ETL **cannot fetch real CBIRC data inside the automation environment**. A clearly-marked synthetic placeholder dataset (`data/raw/financial/CBIRC_2017_2018_PLACEHOLDER.xlsx`) is generated with reasonable distributional priors (ROA ~ N(0.01, 0.005), CAR ~ N(0.12, 0.02)) so the pipeline can be instantiated and tested end-to-end. **The user MUST replace this file with actual CBIRC data before any results are quoted in the paper.**
