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

### R3 (2026-05-15) — v1.2 re-audit

**Findings**: 3 CRITICAL + 17 MAJOR + 3 MINOR (truncated). All addressed in v1.3.

| ID | Severity | Subject | v1.3 fix |
|---|---|---|---|
| R3A-01 / R3B-01 | CRIT | `test_wz_footnote_present` grep string mismatch (footnote vs test had reversed word order) | §5.3.1 footnote closing sentence reworded so `"1 = 象征性 / 应用场景 positive pole"` appears verbatim; test uses 3 independent grep targets. |
| R3C-01 | CRIT | Rater xlsx cell vocab (English) vs LLM/Stata vocab (Chinese) mismatch → Panels E/F silently wrong | §3.3.1 new `RATER_VALUE_TO_CANONICAL_LABEL` map in `manual_validation_schema.py`; new test `test_merge_value_normalization`; coupling test extended to assert both column names AND value vocabularies. |
| R3C-02 / R3A-03 | CRIT | Manuscript paper-draft gate aspirational + scope creep | Gate removed entirely; replaced with §8 process discipline rule. `manuscript_gates.py` dropped. |
| R3A-02 / R3B-02 | MAJ | Fiss & Zajac 2006 cited as ASQ; canonical is AMJ | §2 updated to AMJ with volume/issue/pages. |
| R3A-04 / R3C-12 | MAJ | `pipeline/validation/` is a new subdirectory not matching project layout | Schema module moved to `news_process/validation/manual_validation_schema.py` (peer to llms_evaluation.py). |
| R3B-03 / R3B-04 | MAJ | 41_panel_with_controls propagation mis-attributed to `controls.py::merge_to_panel` (which only touches 51) | §5.4 corrected: 41 propagates via `pipeline/panel/encode.py` downstream merge; 51 via `controls.py::merge_to_panel:568`. |
| R3B-05 | MAJ | §5.3.5/§5.3.6 continuous numbering 1-12 + 13-17 confusing | §5.3.6 renumbered 1-5 independently; §5.5 explicit "12 + 5 = 17". |
| R3B-06 | MAJ | Chicken-and-egg fixture (need pre-refactor golden tex before P0 commit) | §3.3.4 explicit 4-step P0 commit sequence: capture fixture pre-refactor → apply refactor → add tests → commit all together. |
| R3C-03 | MAJ | Bootstrap reproducibility assertion form unspecified | §4.3.6 test 8 specifies `numpy.testing.assert_array_equal` on full 4-tuple. |
| R3C-04 | MAJ | P1 small-n bootstrap edge (n=1, 2) | §4.3.1 short-circuit `n_obs < 3` → NaN tuple; §4.3.6 test 5 `test_kappa_small_n_short_circuit` parametrizes. |
| R3C-05 | MAJ | Fixture-load cwd dependency | §3.3.3 all fixture tests use `Path(__file__).resolve().parent / 'fixtures'`. |
| R3C-06 | MAJ | `test_dag_consistency.py:98` count update split from main P1 commit risks broken revert | §4.3.5 explicit single-commit constraint; §4.6 cross-ref. |
| R3C-07 | MAJ | `pdflatex` smoke compile not in CI matrix | §4.7 replaced with structural Python-`re` assertion (booktabs / column count / row count). |
| R3C-08 | MAJ | Footnote cites convention comment `0=baseline, 1=对照` but not actual .dta value labels | §5.3.1 footnote text expanded to include the value-label strings from `stata_export.py:53-61`; matched by grep target. |
| R3C-09 | MAJ | Git tag `wz-boundary-positive-class-pinned` lacked creation/destruction commands | §5.3.1 + §5.6 added explicit `git tag -a` / `git tag -d` commands. |
| R3C-10 | MAJ | 3-class smoke test only covered P2 path | §5.3.5 test 12 parametrized for P2 + P3 paths. |
| R3C-11 | MAJ | Golden diff scope test assertion form unclear (==/<=) | §5.3.6 test 5 explicit integer equality assertion. |
| R3C-13 | MAJ | Single-rater case (1 cell + 2 NaN) semantics unspecified | §3.3.1 case (3): "exactly 1 → drop"; §3.3.3 test 6 `test_merge_single_rater_dropped`. |
| R3A-05 | MIN | Jaynes 1957 over-cited for binary case | §5.2 notes binary reduces to direct normalization; Jaynes preserved as historical anchor. |
| R3B-07 | MIN | Byte counts verified — no fix | §5.3.4 verified column added. |
| R3C-14 | MIN | Trailer wording strict | §9 explicit: "do not substitute a different model identity". |

**Round 3 verdict**: NOT CLEAN (3 CRITICAL + 17 MAJOR).

**Streak**: 0.

### R4 (2026-05-15) — v1.3 re-audit

**Findings**: 2 CRITICAL + 5 MAJOR + 0 MINOR. Both reviewers asked to suppress MINOR findings (streak rule allows MINOR; only CRITICAL/MAJOR block). Fixes applied via targeted Edits, no full rewrite.

| ID | Sev | Subject | v1.4 fix |
|---|---|---|---|
| R4A-01 | CRIT | wz footnote backticks around `1 = 象征性 / 应用场景 positive pole` broke `grep -F` (R3 fix was incomplete) | §5.3.1 dropped backticks on the two occurrences of `1 = 象征性 / 应用场景` so the verbatim phrase appears unbroken. |
| R4B-02 / R4C-01 | CRIT | `41_panel_with_controls.parquet` has no producer registered; P2 cannot propagate columns to it; `n_added_41 == 8` assertion unreachable | §5.4 + §5.6 mark 41 as orphan; §5.3.6 test 5 changed to `n_added_41 == 0`. Verified via `grep -rn "41_panel_with_controls" pipeline/ core/`: only writer is `generate_golden_snapshot.py` (snapshot tool), not pipeline. |
| R4A-02 | MAJ | RATER_VALUE_TO_CANONICAL_LABEL lacked whitespace/case handling | §3.3.1 added `normalize_rater_value()` helper with `.strip()` + case-folded lookup; test 7 parametrized to cover capitalization + trailing space + typo (→ None). |
| R4B-01 | MAJ | Smoke test 12 P3-path expected `(None, 0.5) → P3`; actual is P2 (verified by running `compute_prob_score(None, 0.5)` → `{...prob_source: "P2"}`) | §5.3.5 test 12 changed to `(None, 0.0) → P3` (correct P3-trigger requires c == 0). |
| R4C-02 | MAJ | `test_positive_class_encoding_assertion` only covered subst | §5.3.6 test 4 parametrized for both substantiveness and locus dimensions. |
| R4C-03 | MAJ | §4.7 said "booktabs" but enumerated `\hline` (incompatible with booktabs) | §4.7 now requires `\toprule`/`\midrule`/`\bottomrule`; replaces `\hline` token. |
| R4C-04 | MAJ | Synthetic xlsx generator determinism unspecified | §3.3.4 added explicit determinism contract: `default_rng(seed=42)`, sort columns, byte-identical reproduction; regen rule for future amendments. |

**Round 4 verdict**: NOT CLEAN (2 CRITICAL + 5 MAJOR).

**Streak**: 0.

### R5 (2026-05-15) — v1.4 re-audit

**Findings**: 0 CRITICAL + 4 MAJOR + 0 MINOR. All fixes applied as targeted Edits.

| ID | Sev | Subject | v1.5 fix |
|---|---|---|---|
| R5A-01 | MAJ | Stale cross-ref §5.3.1 "(test, §5.3.5)" but test lives in §5.3.6 | §5.3.1 corrected both occurrences to "§5.3.6 item 1". |
| R5C-01 | MAJ | normalize_rater_value lacks pd.isna early-return + bool/int auto-type policy | §3.3.1 rewrote function spec with explicit pd.isna check, non-string-type return-None policy, and silent-vs-WARN distinction; §3.3.3 test 7 parametrize extended with True/1/np.nan/pd.NA/"" cases. |
| R5C-02 | MAJ | openpyxl xlsx not byte-identical across versions (ZIP timestamps + cell metadata variance) | §3.3.4 weakened contract from "byte-identical xlsx" to "byte-identical DataFrame hash via pd.util.hash_pandas_object" stored in sidecar `.sha` file. |
| R5C-03 | MAJ | Orphan 41-file cleanup policy not stated | §5.4 NOTE block adds explicit "OUT OF SCOPE / deferred" sentence for the cleanup task. |

**Round 5 verdict**: NOT CLEAN (0 CRITICAL + 4 MAJOR).

**Streak**: 0.

### R6 (2026-05-15) — v1.5 re-audit

**Findings**: 1 CRITICAL + 3 MAJOR + 0 MINOR. (Reviewer A: NO_FINDINGS. Reviewer B: NO_FINDINGS. Reviewer C: all 4 findings.)

| ID | Sev | Subject | v1.6 fix |
|---|---|---|---|
| R6C-01 | CRIT | §5.4 closing ``` after NOTE block buries OUT OF SCOPE prose inside fenced code block (markdown renders prose as plain code) | Closed fence after `codebook.xlsx, .dta export`; promoted NOTE block + OUT OF SCOPE paragraph to regular markdown prose. |
| R6C-02 | MAJ | `test_dag_consistency.py:95-100` has 4 hardcoded "12" references (docstring L96, comment L97, assert L98, error f-string L99); v1.5 only listed L98 | §4.3.5 enumerated all 4 atomic edits required. |
| R6C-03 | MAJ | `pd.util.hash_pandas_object` value drifts across pandas minor versions (1.x vs 2.x; even 2.2 vs 2.3) | §3.3.4 strengthened: sidecar `.sha` records pandas + numpy versions; mismatch → pytest.skip with regenerate instructions; hash mismatch under matching versions → fail. |
| R6C-04 | MAJ | "Panel D's `\end{tabular}`" ambiguous (multiple `\end{tabular}` per file) | §3.3.3 test 11 rewrote with precise byte-offset rule: first `\end{tabular}` after first `Panel D` line. |

**Round 6 verdict**: NOT CLEAN (1 CRITICAL + 3 MAJOR).

**Streak**: 0.

### R7 (2026-05-15) — v1.6 re-audit

**Findings**: 1 CRITICAL + 2 MAJOR + 0 MINOR. (Reviewer A: NO_FINDINGS. Reviewer B: NO_FINDINGS. Reviewer C: 3 findings — all anticipated edge cases from the audit prompt's explicit pre-emptive probes.)

| ID | Sev | Subject | v1.7 fix |
|---|---|---|---|
| R7C-01 | CRIT | Synthetic fixture lacks bias-diagnostic gold → pre-refactor golden `.tex` may have no "Panel D" line → byte-offset truncation crashes | §3.3.3 test 11 rewrote rule conditionally: if "Panel D" absent, truncate at first `\end{tabular}`; offset captured in sidecar `.offset` file. Added test 16 `test_golden_tex_has_no_panel_D_branch`. |
| R7C-02 | MAJ | `.sha` sidecar absence not handled (FileNotFoundError on first-time run) | §3.3.4 step 6 added: missing `.sha` auto-generates from existing xlsx; generator idempotent. Added test 17 `test_sha_missing_is_auto_generated`. |
| R7C-03 | MAJ | Hardcoded "12" in `test_validation_stage_count` lacks future-proof guard | §4.3.5 added `test_no_orphan_twelve_in_validation_count` (tokenize-based); cross-listed in §3.3.3 item 18; added as P1 test 10. |

Test count delta updated: P0 = 17 (was 15; +2 for tests 16-17); P1 = 10 (was 9; +1 for test 10); P2 unchanged at 17. Total 44; baseline 1197.

**Round 7 verdict**: NOT CLEAN (1 CRITICAL + 2 MAJOR).

**Streak**: 0.

### R8 (2026-05-15) — v1.7 re-audit

**Findings**: 2 CRITICAL + 2 MAJOR + 0 MINOR. (Reviewer A: NO_FINDINGS. Reviewer B: 3 findings. Reviewer C: 1 finding.)

| ID | Sev | Subject | v1.8 fix |
|---|---|---|---|
| R8B-01 / R8B-02 | CRIT (paired) | Tokenize-guard test cross-listed in both §3.3.3 item 18 (P0) and §4.3.6 item 10 (P1) → ambiguous double-count → numeric gate uncertain (1196 vs 1197) | Removed §3.3.3 item 18 from P0 enumeration (replaced with a note clarifying P1 owns it). §4.3.6 retains item 10 with explicit "lives in test_dag_consistency.py NOT test_39a_*". Authoritative count: P0 = 17, P1 = 10 (9 in test_39a + 1 in test_dag_consistency), P2 = 17; sum 44; target 1197 unchanged. |
| R8B-03 | MAJ | §3.7 stale "15 new tests" (P0 was 15 in v1.6, now 17 in v1.7) | §3.7 updated to "All 17 new tests pass". |
| R8C-01 | MAJ | §4.5 stale "(9 tests)" — should reflect 10 total | §4.5 updated to "(9 tests in this file; the 10th P1 test lives in tests/integration/test_dag_consistency.py)". |

**Round 8 verdict**: NOT CLEAN (2 CRITICAL + 2 MAJOR).

**Streak**: 0.

### R9 (2026-05-15) — v1.8 re-audit

**Findings**: 0 CRITICAL + 1 MAJOR + 0 MINOR. (Reviewer A: NO_FINDINGS. Reviewer B: NO_FINDINGS. Reviewer C: 1 MAJOR.)

| ID | Sev | Subject | v1.9 fix |
|---|---|---|---|
| R9C-01 | MAJ | §4.3.5 stale cross-reference to "§3.3.3 item 18" — item 18 was removed in R8B-01 fix | §4.3.5 cross-ref updated to "trailing paragraph of §3.3.3, after item 17". |

**Round 9 verdict**: NOT CLEAN (0 CRITICAL + 1 MAJOR).

**Streak**: 0.

### R10 (2026-05-15) — v1.9 re-audit

**Findings**: 0 CRITICAL + 0 MAJOR + 0 MINOR. All three reviewers returned NO_FINDINGS.

**Round 10 verdict**: **CLEAN**.

**Streak**: **1 / 7**.

### R11 (2026-05-15) — v1.9 re-audit

**Findings**: 0 CRITICAL + 0 MAJOR + 0 MINOR. All three reviewers returned NO_FINDINGS.

**Round 11 verdict**: **CLEAN**.

**Streak**: **2 / 7**.

### R12 (2026-05-15) — v1.9 re-audit (streak break)

**Findings**: 0 CRITICAL + 3 MAJOR + 0 MINOR. (Reviewer A: NO_FINDINGS. Reviewer B: 1 MAJOR. Reviewer C: 2 MAJOR — both labeled as R12C-01 by separate agent instances.)

| ID | Sev | Subject | v1.10 fix |
|---|---|---|---|
| R12B-01 | MAJ | tokenize-NUMBER-only guard misses STRING/COMMENT/FSTRING tokens; 3 of 4 hardcoded "12" sites slip past | §4.3.5 rewrote guard body using `re.findall(r'\b12\b', src)` to catch all token classes; word-boundary avoids `122` false positives. |
| R12C-01 (first instance) | MAJ | §5.4 / §5.6 attribution: "via merge_to_panel" misleads — merge_to_panel:568 only adds nf_* aggregates, not the new prob_score cols; actual propagation is via pd.read_parquet at controls.py:261 then preserved through the left-join | §5.4 + §5.6 reworded: "inherited via pd.read_parquet at controls.py:261; preserved through merge_to_panel left-join at controls.py:568". |
| R12C-01 (second instance) | MAJ | §3.3.3 test 11 truncation rule vacuous: pre-refactor has only ONE `\end{tabular}`; both R7C-01 branches resolve to same byte position; post-refactor appending E/F before that single end-tag breaks the comparison | §3.3.3 + §3.3.4 + §3.3.2 introduce a **structural constraint**: Panels E/F MUST live in a SEPARATE `tabular` block. Sidecar offset file withdrawn. Test 11 rewritten as direct cut-at-first-`\end{tabular}` + meta-line filter equality. Test 16 replaced with `test_panels_E_F_in_separate_tabular` enforcing the constraint. |

**Round 12 verdict**: NOT CLEAN (3 MAJOR).

**Streak**: **0 / 7** (reset).

### R13 (2026-05-15) — v1.10 re-audit

**Findings**: 1 CRITICAL + 0 MAJOR + 0 MINOR. (Reviewer A: NO_FINDINGS. Reviewer B: NO_FINDINGS. Reviewer C: 1 CRITICAL.)

| ID | Sev | Subject | v1.11 fix |
|---|---|---|---|
| R13C-01 | CRIT | Synthetic fixture covers innovation R-columns only; pre-refactor `llms_evaluation.py::main()` early-returns at L989-991 when verification gold is absent. The production `32_news_llms_human_samples.xlsx` is NOT in the repo; step 1 of §3.3.4 commit sequence cannot produce the golden TeX deterministically on a clean checkout | §3.3.4 added `news_llms_human_samples_synthetic.xlsx` as a REQUIRED second fixture with ≥1 verification + sentiment gold row; updated step 1 to load both fixtures via env-var/CLI; §3.3.3 test 17 parametrized over both fixtures for `.sha` auto-generation. |

**Round 13 verdict**: NOT CLEAN (1 CRITICAL).

**Streak**: **0 / 7** (reset).

### R14 (2026-05-15) — v1.11 re-audit

**Findings**: 2 CRITICAL + 1 MAJOR + 0 MINOR. (R14A: 1 CRITICAL refuting R13C-01 premise. R14B: 1 CRITICAL — no override mechanism in pre-refactor code. R14C: 1 MAJOR — bare `controls.py` path ambiguous.)

| ID | Sev | Subject | v1.12 fix |
|---|---|---|---|
| R14A-01 | CRIT | R13C-01's premise was wrong: `llms_evaluation.py::main()` has 3 `_generate_demo_data()` fallback branches at L898/L913/L966 with `np.random.RandomState(42)`-seeded 200 rows. The L989-991 early-return is unreachable on clean checkout. v1.11's dual-fixture mandate is unmotivated and introduces a methodological hazard (synthetic vs demo distribution mismatch). | §3.3.4 v1.11 dual-fixture mandate REVERTED. Single fixture (manual_validation) restored. Step 1 documented as relying on `_generate_demo_data()` fallback. R13C-01 entry above superseded. |
| R14B-01 | CRIT | Even if dual-fixture were desired, pre-refactor `main()` has no argparse/env-var/CLI override mechanism; step 1 cannot execute without code change | Moot — v1.12 reverts the override requirement entirely. |
| R14C-01 | MAJ | §5.4 / §5.6 bare `controls.py:261/568` is ambiguous; surrounding context (encode.py, codebook.py, etc.) lives in `pipeline/panel/`, but actual file is at `pipeline/falsification/controls.py`. Invocation site is `pipeline/panel/runner.py:1171`. | §5.4 + §5.6 updated to `pipeline/falsification/controls.py:261/568`; invocation site `pipeline/panel/runner.py:1171` noted. |

§3.3.3 test 17 reverted to single-fixture parametrization.

**Round 14 verdict**: NOT CLEAN (2 CRITICAL + 1 MAJOR).

**Streak**: **0 / 7** (reset).

### R15 (2026-05-15) — v1.12 re-audit

**Findings**: 1 CRITICAL + 1 MAJOR + 0 MINOR. (R15A: 1 CRITICAL — wrong filename + wrong reachable branch. R15B: 1 MAJOR — wrong invocation file. R15C: NO_FINDINGS.)

| ID | Sev | Subject | v1.13 fix |
|---|---|---|---|
| R15A-01 | CRIT | (a) Plan used `32_news_llms_human_samples.xlsx` but config has `32_human_samples.xlsx` (paths.yaml:56); (b) the file is PRESENT in repo (empty gold cells), so step 1's reachable demo-fallback branch is L966 (empty-gold), NOT L898 (file-absent) | All occurrences of `32_news_llms_human_samples.xlsx` replaced with `32_human_samples.xlsx` (replace_all). Step 1 now cites L966 as the actual reachable branch; L898 and L913 noted as alternative converging paths. |
| R15B-01 | MAJ | §5.4 / §5.6 cited `pipeline/panel/runner.py:1171` as invocation site of merge_to_panel; `grep -rn "merge_to_panel" pipeline/` shows it is only called at `pipeline/falsification/controls.py:1171` (inside `run_falsification`, between `aggregate_non_fintech` at L1170 and `export_results` at L1173) | §5.4 + §5.6 corrected to cite `pipeline/falsification/controls.py:1171` as invocation site; explicitly noted "NOT pipeline/panel/runner.py" to prevent regression. |

**Round 15 verdict**: NOT CLEAN (1 CRITICAL + 1 MAJOR).

**Streak**: **0 / 7** (reset).

**Trend note**: R12→R15 illustrates a pattern: when one finding is fixed, the fix itself introduces a downstream attribution issue (R12→R14 path qualifier; R14→R15 invocation site). This is normal during convergence on a long plan; the trend remains downward in severity and count.

### R16 (2026-05-15) — v1.13 re-audit

**Findings**: 1 CRITICAL + 0 MAJOR + 0 MINOR. (R16A: NO_FINDINGS. R16B: 1 CRITICAL — function name. R16C: NO_FINDINGS.)

| ID | Sev | Subject | v1.14 fix |
|---|---|---|---|
| R16B-01 | CRIT | R15B-01 fix introduced wrong function name `run_falsification` — no such function exists in `pipeline/falsification/controls.py`; the actual containing function at L1152 is `main()` | Both §5.4 + §5.6 occurrences of "inside run_falsification" replaced with "inside main() (controls.py:1152)" via replace_all. |

**Round 16 verdict**: NOT CLEAN (1 CRITICAL).

**Streak**: **0 / 7** (reset).

**Trend note**: R16 continues the R12→R15 attribution-chain pattern. The fix for R15 (invocation file) introduced a wrong function name; R16 fix closes that. Each layer reduces ambiguity slightly. Expected to converge cleanly once attribution-chain stabilizes.

### R17 (2026-05-15) — v1.14 re-audit

**Findings**: 1 CRITICAL + 1 MAJOR + 0 MINOR + 1 REJECTED. (R17A: 1 CRITICAL R17A-02; 1 REJECTED R17A-01. R17B: 1 MAJOR. R17C: NO_FINDINGS.)

| ID | Sev | Subject | v1.15 fix |
|---|---|---|---|
| R17A-02 | CRIT | `_aggregate_track` stores per-model substantiveness/locus *confidences* in `per_model_parsed` at L887-898, but the *labels* are only appended to flat `innov_loci` / `innov_substs` lists — so per-model `compute_prob_score_binary(label, conf, positive_class)` cannot be evaluated. Plan §5.3.1 lacked the prerequisite parsing-block extension. | §5.3.1 split into Step A (extend parsing block to store `{short}_innovation_locus` and `{short}_innovation_substantiveness` per-model labels in `per_model_parsed`) and Step B (binary prob_score computation). Added P2 test 13 `test_per_model_innovation_labels_stored`; P2 delta 17 → 18; §8 sum 44 → 45; target 1197 → 1198. |
| R17B-01 | MAJ | R16B-01 fix's replace_all missed §5.6 line 669 because identifier was wrapped in backticks; "inside `run_falsification`" remained | Direct Edit replaced the remaining occurrence to "inside `main()` (`controls.py:1152`)". |
| R17A-01 | REJ | Reviewer claimed test_dag_consistency.py "12" sites are at L94-L97 (off-by-2 vs plan's L96-L99) | REJECTED after `Read tests/integration/test_dag_consistency.py:93-100`: actual lines are L96 docstring, L97 comment, L98 assert, L99 f-string — matching the plan. Reviewer miscounted blank lines. |

**Round 17 verdict**: NOT CLEAN (1 CRITICAL + 1 MAJOR).

**Streak**: **0 / 7** (reset).

**Trend note**: R13→R14 illustrates the value of independent fresh-context reviewers — R13C reviewer asserted demo-fallback didn't exist without checking; R14A reviewer caught the gap. The plan is more robust after v1.12 because the demo-mode fallback is now explicitly documented as part of step 1's reachability proof.

**Trend note**: R12 spike is genuine — 2 R10-R11 reviewers (different agents) missed both R12 findings. The plan documents real-world `merge_to_panel` semantics inaccurately, and the offset-file rule from R7 was tested against a hypothetical 2-tabular pre-refactor that the actual code does not produce. v1.10 fixes are structural (refactor must emit 2 tabulars, guard must regex), not bookkeeping.

**Trend**: R1 (7C+13M) → R2 (2C+12M) → R3 (3C+17M) → R4 (2C+5M) → R5 (0C+4M) → R6 (1C+3M) → R7 (1C+2M) → R8 (2C+2M) → R9 (0C+1M). Findings narrowing to single-item bookkeeping nits. 2 of 3 reviewers found NO_FINDINGS at R9; if v1.9 closes the cross-ref, R10 should clear.

