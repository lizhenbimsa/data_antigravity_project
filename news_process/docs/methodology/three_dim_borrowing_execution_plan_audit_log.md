# Three-Dimension Borrowing Execution Plan — Audit Log

> **Convergence rule**: at least 7 consecutive clean rounds (no CRITICAL,
> no MAJOR findings) required to terminate the audit cycle. Each round
> consists of 3 parallel reviewer perspectives plus an aggregation
> step that records findings, applies fixes, and increments the
> consecutive-clean counter.
>
> **Severity definitions**:
> - **CRITICAL**: methodological error, contradiction with existing
>   `docs/methodology/` documents, breaking change not declared,
>   pre-registration violated.
> - **MAJOR**: false claim about file path / function name / column /
>   line number; missing dependency declaration; un-falsifiable
>   acceptance criterion; uncovered edge case in test plan; risk with
>   no rollback path.
> - **MINOR**: prose / phrasing / citation style / typo / link
>   formatting / non-essential ambiguity. Does NOT block convergence.

## Round numbering

| Field | Meaning |
|---|---|
| `R#` | round number |
| `Reviewer A` | methodological-rigor reviewer (frameworks, doc consistency, pre-registration) |
| `Reviewer B` | engineering-feasibility reviewer (file paths, function names, columns, tests, golden baseline) |
| `Reviewer C` | completeness / cross-doc consistency reviewer (CLAUDE.md, internal P0/P1/P2 dependency, edge cases, rollback) |
| `Findings` | per-reviewer list, severity-tagged |
| `Fixes` | per-finding fix summary |
| `Clean?` | round verdict (yes/no) |
| `Streak` | consecutive-clean counter |

## Rounds

<!-- Rounds appended below as the audit cycle progresses. -->

### R1 (2026-05-15) — initial audit against v1.0

**Reviewers**: A (methodological rigor), B (engineering feasibility), C (completeness).

**Findings summary**: 7 CRITICAL, 13 MAJOR, 15 MINOR.

#### CRITICAL findings

| ID | Description | Fix in v1.1 |
|---|---|---|
| R1A-01 | Platt 1999 citation misapplied — formula is naive map, not learned sigmoid scaling | §5.2 replaced Platt 1999 with Jaynes 1957 + Törnberg 2024 (same anchors as 3-class function); §2 added explicit "citations NOT inherited" note for Platt and Bingler. |
| R1A-02 | Stage number 47 already used as sub-step inside panel orchestrator | Renumbered to `39a` (validation block 31-39 convention; alphabetic suffix per existing 32a/38a/38b precedent). |
| R1A-03 | P0 acceptance contradicts reality (manual annotation pending) | §3.7 split into "code-path acceptance" (achievable now) + "data-path acceptance" (deferred); §2 made the dependency explicit. |
| R1B-01 | `tests/test_llms_evaluation.py` does not exist; actual is `test_33_evaluation.py` and `test_panels_A_to_D` is new (not existing regression) | §3.3.2 corrected target file; §3.3.3 added new `classification_eval_table_A_to_D_golden.tex` fixture creation as in-scope work. |
| R1B-02 | `cohens_kappa_2cat` has no bootstrap CI | §4.3.1 spec now explicitly implements bootstrap on top of the point function via `numpy.random.default_rng(seed=42)`. |
| R1C-01 | positive_class encoding inverted from existing Stata convention | §5.3.1 flipped positive_class to `象征性` / `应用场景` to align with Stata `1=对照` encoding; added explicit citation of `stata_export.py:40-50`; §5.3.6 added assertion test. |
| R1C-02 | P0 secretly depends on rater unblocking despite "independent" claim | §2, §3.6, §3.7, §7 made the data-path dependency explicit; §3.3.3 added synthetic fixture so code path tests deterministically. |

#### MAJOR findings

| ID | Description | Fix in v1.1 |
|---|---|---|
| R1A-04 | positive_class methodological asymmetry not pre-registered | §5.3.1 now declares this is an encoding choice (downstream of LLM labels), NOT a prompt-semantic change; §9 records pre-registration integrity check; one-paragraph footnote added to `wz_framework_boundary_justification.md` (committed with P2). |
| R1A-05 | 4-state prob_source schema conflates label + mapping branch | §5.3.1 simplified to 2 states `P2_BIN` / `P3_BIN`, parallel to existing `P2` / `P3` convention. |
| R1B-03, R1C-08 | Test count arithmetic inconsistent (1161 vs 1168) | §3.5, §4.5, §5.5, §8 all normalized to cumulative delta from baseline: 1153 + 9 + 6 + 13 = 1181 (revised totals after Test plan rework). |
| R1B-04, R1C-07 | "byte-for-byte unchanged" assertion vague | §3.7, §3.3.2 changed to filtered structural diff with explicit regex for metadata lines. |
| R1B-05 | Golden snapshot command path inconsistent | §5.3.7, §10 standardized on `"F:/Anaconda3/python.exe" news_process/scripts/migrate/generate_golden_snapshot.py`. |
| R1B-06 | Golden diff scope mis-described ("+8 column entries" only) | §5.6 rewrote diff scope as +8 entries in 3 dicts + 2 scalar field changes + no other-stage diff; §5.3.6 added explicit assertion test. |
| R1B-07 | Stage filename in `EXPECTED_NO_OUTPUT_STAGES` missing `.py` suffix | §4.3.4 corrected to `"39a_inter_track_kappa.py"`. |
| R1C-03 | Order independence claim overstated | §7 rewrote independence/reversibility section with precise per-work-item conditions. |
| R1C-04 | Rater tie test misformulated for binary labels | §3.3.1, §3.3.2 reformulated tie semantics (3-way ties impossible for binary; only missing-rater 1-1 ties exist); 5 new tests cover the realistic edge cases. |
| R1C-05 | P1 missing empty-subset and constant-column tests | §4.3.5 added `test_kappa_empty_subset` and `test_kappa_constant_column`. |
| R1C-06 | P2 missing all-NaN and invalid positive_class tests | §5.3.5 added `test_all_none_aggregation` and `test_mismatched_positive_class`. |
| R1C-09 | P1 acceptance "whatever they are" un-falsifiable | §4.7 rewrote with concrete pass/fail conditions: 2 rows, 7 columns, value-set membership. |
| R1C-10 | New YAML config key not declared | §3.3.1 and §9 hardcode column names; removes YAML key requirement entirely. |

#### MINOR findings (informational; not blocking convergence)

| ID | Description | Fix in v1.1 |
|---|---|---|
| R1A-06 | Bingler 2022 inherited but unused | §2 "Citations NOT inherited" subsection explicitly drops Bingler from anchor list. |
| R1A-07 | Bootstrap not propagated to P0 | §3.2, §3.3.1 added bootstrap CI invocation when `n_gold < 100`. |
| R1B-08 | L995-1003 off by 2 | §3.3.1 corrected to L993-1004. |
| R1B-09 | `_rationale` column existence not acknowledged | §3.3.1 added explicit note that `_rationale` columns exist but are not consumed. |
| R1B-11 | §9 contradicted §3.6 on YAML keys | Resolved via R1C-10 fix (no new YAML keys). |
| R1B-13 | Stata labels not enumerated | §5.3.4 now enumerates all 8 labels with character counts. |
| R1B-14 | Empty-xlsx edge-case test missing | §3.3.2 added `test_panels_E_F_pending_when_empty` and `test_panels_E_F_pending_when_file_absent`. |
| R1B-15 | Ruff not enumerated for new files | §3.5, §4.5, §5.5 all enumerated. |
| R1C-11 | Tie reasoning citation wrong though conclusion correct | §6 corrected to "Binary label + 3 raters → 2-1 or 3-0 splits only; 3-way ties mathematically impossible". |
| R1C-12 | Sibling doc co-existence informational | No fix needed. |

**Round 1 verdict**: NOT CLEAN (7 CRITICAL + 13 MAJOR).

**Streak**: 0.

### R2 (2026-05-15) — v1.1 re-audit

**Reviewers**: A (rigor), B (engineering), C (completeness).

**Findings summary**: 2 CRITICAL + 12 MAJOR + 6 MINOR.

#### CRITICAL
| ID | Description | Fix in v1.2 |
|---|---|---|
| R2C-01 | `test_dag_consistency.py:98` hard-asserts `STAGES_VALIDATION` count == 12; P1's stage addition makes it 13, breaks CI | §4.3.5 new sub-section: P1 commit updates the constant to 13. §4.3.3 specifies `_VALIDATION_PREDS['inter_track_kappa']` module-scope predicate for `test_predicate_identity_module_scope`. |
| R2B-02 | Stata `STATA_VAR_LABEL_MAXLEN = 80` enforced on **UTF-8 bytes** not chars; plan said "chars"; em-dash is 3 bytes | §5.3.4 rewrote the table with explicit Chars + Bytes columns; cited `validate_stata_compat` at `stata_export.py:268-269`. All 8 byte counts ≤ 80. |

#### MAJOR
| ID | Description | Fix in v1.2 |
|---|---|---|
| R2A-02 / R2C-03 | wz footnote not yet written; pre-registration claim un-verifiable | §5.3.1 now embeds the verbatim footnote text; §5.7 + new test `test_wz_footnote_present` makes presence grep-falsifiable; new git tag `wz-boundary-positive-class-pinned`. |
| R2A-03 | Bootstrap threshold n<100 not aligned with source (n<50 in `inter_track_agreement_interpretation.md §7`) | §3.2 + §3.3.1 changed to `bootstrap_when_n_below=50`; §4.2 explicitly distinguishes P1's always-bootstrap as a separate intentional choice. |
| R2A-04 | No paper-draft gate to prevent shipping with pending Panels E/F | §8 added "Paper-draft gate" subsection with `PENDING_INNOVATION_PANELS` CI marker and `papers/_common/manuscript_gates.py`. |
| R2B-01 | tone_llms.py main reference "L1190-1395" misleading (function header is L1050) | §5.3.1 corrected to L1050 with prose anchor. |
| R2B-03 / R2B-04 | Golden snapshot diff scope wrong: covers 4 parquets (21/40/41/51), not just 40; 21 gains 4 article-level cols | §5.6 rewrote with full per-parquet diff enumeration; §5.3.6 `test_golden_baseline_diff_scope` updated. |
| R2B-05 | stata_export.py L113-114 / L177 anchor refs misidentified (they point at existing entries, not insertion landmarks) | §5.3.4 corrected to `HEURISTIC_LABELS` at L108-124 and `assign_core_columns::core_patterns` at L162-200. |
| R2C-02 | R-column hardcoded names lack coupling test with the emitter | §3.3.2 new module `news_process/pipeline/validation/manual_validation_schema.py` holds the constant; §3.3.3 test 13 `test_r_column_schema_coupling` enforces emitter alignment. |
| R2C-04 | 3 missing P0 edge cases (wrong cols, fallback join, duplicate docid) | §3.3.3 added 3 tests (items 10-12). |
| R2C-05 | 2 missing P1 tests (bootstrap reproducibility; missing dual-both column) | §4.3.6 added 2 tests (items 7-8). |
| R2C-06 | 3 missing P2 tests (confidence clamp ±, 3-class non-regression smoke) | §5.3.5 added 3 tests (items 10-12); §5.3.1 specified input-domain validation. |
| R2A-01 | §5.2 derivation logically inverted (LLM emits `P(predicted_label)=c`, not `P(positive_class)=c`) | §5.2 rewrote derivation: the constraint is on predicted_label, positive_class assignment is a downstream relabeling. |

#### MINOR
| ID | Fix |
|---|---|
| R2A-05 | §2 + §5.2 added Cover & Thomas (2006) §2 as binary-entropy companion citation. |
| R2A-06 | §5.3.1 added concrete consumer ground (`papers/bank_fintech_tone/analysis.py`). |
| R2B-06 | §3.3.4 noted xlsx-fixture precedent. |
| R2C-07 | §7 added two verified-grep evidence footnotes. |
| R2C-08 | §8 replaced constant 1181 with formulaic `count == 1153 + Σ(deltas)`. |
| R2C-12 | Sibling docs presence reconfirmed (informational). |

**Round 2 verdict**: NOT CLEAN (2 CRITICAL + 12 MAJOR).

**Streak**: 0.

