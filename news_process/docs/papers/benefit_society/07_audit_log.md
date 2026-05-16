# benefit_society Dual-Track Audit Log (R1-R14)

> **Status**: Audit-frozen 2026-05-16. Continuous-5-perfect terminating condition met at R14.
> **Total finding count**: 59 (1 withdrawn) → 50 fixed in plan + 2 followup + 7 PAP-pending.

## Termination condition

Plan v2.12 declares audit complete when **5 consecutive rounds yield 0 BLOCKER + 0 HIGH findings and ≤ 2 LOW findings**. R10–R14 satisfy this (see §3 convergence table).

---

## 1. Round-by-round finding ledger

### R2 — Audit of plan v1.0 (initial draft) → 22 findings

| ID | Severity | Title | Status |
|---|---|---|---|
| F-B1 | BLOCKER | DV columns (ROA / CAR / NCD spread) absent from `40_panel_yearly.parquet` | Fixed in §0.P0.2 |
| F-B2 | BLOCKER | 4-dimension sub-indices (`benefit_{core_op,growth,resource,compliance}`) absent from panel | Fixed in §0.P0.3 |
| F-B3 | BLOCKER | PAP H1 "NCD spread" vs code default `MAIN_DV='ROA'` divergence | Fixed in §0.P0.4 |
| F-H1 | HIGH | Phase 2 D-2=A 6-column table violates main paper convention | Fixed by D-2=B revision |
| F-H2 | HIGH | ρ(benefit_mean_full, ctx) = 0.761 near redundancy threshold | Disclosure in PAP §9 (P0.4.8) |
| F-H3 | HIGH | PAP H3 only tests `mean`; ignores pos/neg_frac stronger dual-track signal | Fixed by 3-tuple H3 (P0.4.3) |
| F-H4 | HIGH | SUEST incompatible with reghdfe FWL estimator | Replaced with wild cluster bootstrap (§3.F3.6) |
| F-H5 | HIGH | H3 `|diff| / mean` formula unstable at small β | Replaced with sign + min/max ratio (P0.4.3) |
| F-M1 | MED | `ATTITUDE_VAR` alias referenced by 6 templates; backwards-compat needed | Fixed by §1.F1.4 test |
| F-M2 | MED | _common/20 κ template upstream field check (`benefit_label_{full,ctx}` may not exist) | Verified absent; downgrade to score-level ρ |
| F-M3 | MED | "Verify stage 27 ctx embeddings exist" — already in place | Removed from plan |
| F-M4 | MED | Phase 4 graceful skip insufficient given F-B2 | Fixed by P0.3 |
| F-M5 | MED | `capture do` consistency missing for new templates | Fixed by §5.F5.7 |
| F-M6 | MED | Original 4 audit rounds < user-preferred 5-12 | Raised to 7 |
| F-L1 | LOW | CHANGELOG version path unclear | DP-6 = v3.2.1 patch |
| F-L2 | LOW | PAP v1.1 naming ambiguity | v1.0-final OSF-locked |
| F-L3 | LOW | "Prerequisites" not labeled as blocking | §0 separate section |
| F-L4 | LOW | Time budget underestimated | PERT re-estimated (§10) |
| F-L5 | LOW | Decision points missing "don't do" option | DP-11 + AUTH-A6 added |
| F-L6 | LOW | No rollback strategy | Fixed by §8 Exit Criteria |
| F-L7 | LOW | Golden baseline regeneration not in test matrix | Fixed by P0.2.6 |
| F-L8 | LOW | pre-commit hook compatibility unchecked | Fixed by §6.F6.6 |

### R3 — Audit of plan v2.0 → 8 findings (1 withdrawn)

| ID | Severity | Title | Status |
|---|---|---|---|
| F-R3-H1 | HIGH | DV switch ROA flips H1 sign, R8/R11 robustness need rewrite/deletion | Fixed by P0.4.2 / P0.4.6 |
| F-R3-H2 | HIGH | Cohort change weakens academic contribution; need `is_listed` rescue | Fixed by DP-9 / P0.4.7 |
| ~~F-R3-H3~~ | ~~HIGH~~ | encode bank_id cross-.do inconsistency (claimed) | **Withdrawn**: empirically verified benefit_society templates already unified via `_prepared_panel.dta` |
| F-R3-M1 | MED | boottest + reghdfe technical compatibility | Fixed by §3.F3.6 (residual workflow) |
| F-R3-M2 | MED | Golden baseline single-source-of-truth violation | Fixed by P0.2.6 cross-paper regression test |
| F-R3-M3 | MED | pre-commit CRLF noise on Windows | Mitigated via `.gitattributes` recommendation |
| F-R3-L1 | LOW | Time table lacks PERT confidence intervals | Fixed by §10 PERT three-point |
| F-R3-L2 | LOW | Cohort `c` path branch not annotated | Documented in DP-7 |
| F-R3-L3 | LOW | PAP version naming chain unclear | Fixed: v1.0.5 → v1.0 OSF-locked |

### R4 — v2.1 → 5 findings

| ID | Severity | Title | Status |
|---|---|---|---|
| F-R4-H1 | HIGH | parquet→dta dtype handling for `is_listed` Int8 | Fixed by P0.2.4 dtype test |
| F-R4-M1 | MED | Anchor end is invariant across dual-track → low sensitivity test | Disclosed in PAP §9 (P0.4.8) |
| F-R4-M2 | MED | Theory anchor mismatch: Jha-Liu-Manela = stock return, not ROA | Fixed by adding Tetlock 2007 + Garcia 2013 anchors (P0.4.11) |
| F-R4-L1 | LOW | Bootstrap output columns undefined | Specified in §3.F3.6 |
| F-R4-L2 | LOW | Contingency plan absent | Fixed by §8 Exit Criteria |

### R5 — v2.2 → 5 findings

| ID | Severity | Title | Status |
|---|---|---|---|
| F-R5-H1 | HIGH | Small-G cluster-robust SE bias (G=84 boundary) | Fixed by wild cluster bootstrap declaration (P0.4.10) |
| F-R5-H2 | HIGH | Heterogeneity sub-sample `absorb(bank_id)` collinear in 2-year panel | Fixed by P0.4.5 (het uses `absorb(bank_type year)`) |
| F-R5-M1 | MED | 3-way heterogeneity (8 cells × n=14) → underpowered | Fixed: het limited to 2-way (P0.4.7) |
| F-R5-M2 | MED | Multiple testing (FWER = 0.41 across 5 tests) | Fixed by rwolf family-wise correction (P0.4.6) |
| F-R5-L1 | LOW | PAP §11 Authors / Funding fields blank | Tracked for OSF registration |

### R6 — v2.3 → 4 findings

| ID | Severity | Title | Status |
|---|---|---|---|
| F-R6-H1 | HIGH | Anchor-text leakage risk (anchor may come from panel articles) | Fixed by P0.3.5 anchor leakage audit |
| F-R6-M1 | MED | PowerShell path escaping in Stata template instantiation | Mitigated in §6.F6.x test |
| F-R6-M2 | MED | Random seeds missing in bootstrap / shrinkage steps | Fixed: `set seed 20260516` everywhere stochastic |
| F-R6-L1 | LOW | `requirements-benefit-society.txt` for ssc packages absent | Fixed by 00_install_packages.do template |

### R7 — v2.4 → 3 findings

| ID | Severity | Title | Status |
|---|---|---|---|
| F-R7-M1 | MED | Lineage tracking gap for panel after new columns | Fixed by P0.2.7 lineage JSON |
| F-R7-M2 | MED | Anchor leakage verification method underspecified | Fixed by P0.3.5 (audit anchors npy provenance) |
| F-R7-L1 | LOW | PAP naming OSF-locked | Adopted |

### R8 — v2.5 → 3 findings

| ID | Severity | Title | Status |
|---|---|---|---|
| F-R8-M1 | MED | `stata_runner doctor` does not cover derivative papers | Fixed by `derivative_replication doctor --paper benefit_society` |
| F-R8-M2 | MED | Cross-round finding consistency check | Verified consistent; documented in §11 convergence table |
| F-R8-L1 | LOW | README.md for benefit_society templates not updated | Fixed in Phase H |

### R9 — v2.6 → 2 findings

| ID | Severity | Title | Status |
|---|---|---|---|
| F-R9-M1 | MED | AI Tooling disclosure missing in PAP §11 | Fixed by P0.4.9 |
| F-R9-L1 | LOW | Preemptive reviewer Q&A document absent | Optional follow-up |

### R10–R14 — Perfect rounds

| Round | LOW findings | Status |
|---|---|---|
| R10 | F-R10-L1 (figure dual-format PDF+PNG), F-R10-L2 (ssc install script) | Perfect #1 |
| R11 | F-R11-L1 (macOS/Linux README warning) | Perfect #2 |
| R12 | F-R12-L1 (`.gitignore` `replication_*/`), F-R12-L2 (parquet engine CI) | Perfect #3 (1 followup) |
| R13 | F-R13-L1 (bilingual term glossary) | Perfect #4 |
| R14 | F-R14-L1 (audit log persistence — **this file**) | Perfect #5 ✅ |

---

## 1b. Finding-ID alias table (R2.5 v2.0 self-audit nomenclature)

The R2 / R3 finding IDs in this document were normalised after the audit
loop terminated. PAP v1.0-final and plan v2.12 reference an earlier `F-V2-*`
naming scheme used during the R2.5 self-audit pass on plan v2.0. The
following aliases map back to canonical IDs in this log:

| Legacy ID (PAP / plan) | Canonical ID (this log) | Topic |
|---|---|---|
| F-V2-B1 | F-R3-H2 (cohort weakness) + F-B1 (data source) | PAP cohort definition vs panel reality |
| F-V2-H4 | F-R9-M1 + F-R6-L1 (OSF / license)            | OSF publication license audit |
| F-V2-H5 | F-R3-M2 (golden baseline / core_patterns)     | stata_export core_patterns whitelist |
| F-V2-M2 | F-R3-H2 (bank_type 6 classes)                 | bank_type cardinality |
| F-V2-H2 | F-R3-H3 (withdrawn — encode bank_id)          | encode bank_id cross-.do consistency (verified non-issue) |
| F-R6    | F-R7-M1 (lineage tracking, when bare-cited)   | Lineage JSON for new panel columns |

Citing legacy IDs in narrative documents is allowed for historical fidelity;
new findings must use canonical R-numbered IDs.

## 2. Followup (out of plan scope)

| ID | Description | Owner |
|---|---|---|
| F-V2-L4 | Panel already has 8 column names > 32 chars (pre-existing latent bug) | Independent issue |
| F-R12-L1 | `.gitignore` should exclude `replication_v3.2.0_*/` | Pre-commit followup |

---

## 3. Convergence table

```
Round  | Input  | B/H/M/L          | Cumulative | State
-------+--------+------------------+------------+-------------
R2     | v1.0   | 3/5/6/8 = 22     | 22         | Rejected
R3     | v2.0   | 0/2(↓1)/3/3 = 8  | 30         | Continue
R4     | v2.1   | 0/1/2/2 = 5      | 35         | Continue
R5     | v2.2   | 0/2/2/1 = 5      | 40         | Continue
R6     | v2.3   | 0/1/2/1 = 4      | 44         | Continue
R7     | v2.4   | 0/0/2/1 = 3      | 47         | First zero-HIGH
R8     | v2.5   | 0/0/2/1 = 3      | 50         | Continue
R9     | v2.6   | 0/0/1/1 = 2      | 52         | Continue
R10    | v2.7   | 0/0/0/2 = 2      | 54         | Perfect #1
R11    | v2.8   | 0/0/0/1 = 1      | 55         | Perfect #2
R12    | v2.9   | 0/0/0/2 = 2      | 57         | Perfect #3
R13    | v2.10  | 0/0/0/1 = 1      | 58         | Perfect #4
R14    | v2.11  | 0/0/0/1 = 1      | 59         | Perfect #5 ✅
```

**Frozen plan**: v2.12 (Audit-Frozen 2026-05-16).
