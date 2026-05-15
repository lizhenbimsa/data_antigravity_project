# Three-Dimension Borrowing Execution Plan

> **Status**: v1.2 (post-Round-2 audit; 2 CRITICAL + 12 MAJOR fixes applied)
> **Scope**: Code-only changes; no manual annotation, no infra changes, no model retraining.
> **Authoring date**: 2026-05-15
> **Baseline**: news_process v3.2.0, pytest baseline 1153 passed / 6 skipped / 0 failed.

## 0. Document Purpose

This plan addresses three concrete asymmetries between how `sentiment`,
`innovation_substantiveness`, and `innovation_locus` are processed
**after** v3.2.0 dual-track work. v3.2.0 already unified the prompt
(unified_cot.txt v7), dual-track architecture (`_full` / `_ctx`), per-model
per-dimension confidence, and majority-vote framework across the three
dimensions. Three asymmetries remain:

1. **`llms_evaluation.py`** evaluates only `verification` and `sentiment`
   tasks ([L993-1004](../../validation/llms_evaluation.py#L993-L1004)).
2. **Inter-track κ** has Stata template
   [20_tableA1_inter_track_kappa.do.tmpl](../../papers/_common/stata_templates/20_tableA1_inter_track_kappa.do.tmpl)
   but no Python pipeline stage; no `.csv` / `.tex` produced in
   `eval_reports/`.
3. **Probability scoring** via `compute_prob_score`
   ([tone_llms.py:680](../../pipeline/sentiment/tone_llms.py#L680)) only
   handles the 3-class sentiment case; binary dimensions have no
   `prob_score` continuous LHS column.

This plan addresses these three via three work items (P0, P1, P2). All
other candidates are explicitly ruled out (§6).

## 1. Context Anchors

- Project root: `f:\WiseSearch\data_antigravity_project\`.
- Python interpreter (memory `python_interpreter`): `F:\Anaconda3\python.exe`.
- Pipeline package: `news_process/`; CLAUDE.md governs conventions.
- Sibling methodology docs (`news_process/docs/methodology/`):
  `stage3_dual_track_plan_v3.2.0.md`,
  `inter_track_agreement_interpretation.md`,
  `manual_validation_study_plan.md`,
  `wz_framework_boundary_justification.md`,
  `calibration_plan_v5.1.md`,
  `prompt_terminology_mapping.md`,
  `paper_methodology_section_draft.md`,
  `v3_2_0_release_readiness.md`.

## 2. Scope

### In scope

- **P0**: Extend [llms_evaluation.py](../../validation/llms_evaluation.py)
  to cover four classification tasks (verification + sentiment +
  substantiveness + locus). Code path lands regardless of annotation
  state; Panels E/F display "manual validation pending (n=0)" footnote
  until rater coordination unblocks the data path.
- **P1**: New stage `39a_inter_track_kappa.py` computing inter-track
  Cohen's κ for innovation dimensions with bootstrap CI; emits
  `inter_track_kappa_table.csv` + `.tex` to `eval_reports/`. Mirrors
  Stata template `20_tableA1_inter_track_kappa.do.tmpl`.
- **P2**: New `compute_prob_score_binary` alongside `compute_prob_score`;
  produces binary `prob_score ∈ [0, 1]` for substantiveness and locus
  at article + bank-year levels.

### Out of scope (with reason)

| Item | Reason |
|---|---|
| Substantiveness lexicon classifier | Violates W&Z "象征性 ≠ 缺乏事实陈述" ([unified_cot.txt:51-53](../../config/prompts/unified_cot.txt#L51-L53)); breaks pre-registration. |
| Locus BERT fine-tune | Minority class has 1 sample ([manual_validation_study_plan.md:34](manual_validation_study_plan.md#L34)). |
| Tie-strategy sensitivity | Binary label + 3 raters → 2-1 or 3-0 only; 3-way ties impossible. |
| Locus title-only track | Engineering cost dominates value. |
| Calibration unblock | External resource (human raters); see [calibration_plan_v5.1.md](calibration_plan_v5.1.md). |
| Stage 33 LLM-vs-human for innovation | Code path covered by P0; data path waits on rater coordination. |
| New sentiment dictionary work | Out of charter; P0/P1/P2 target innovation asymmetries. |

### Academic anchors actually invoked by P0/P1/P2

- Cohen (1960) — κ formula (P0, P1).
- Krippendorff (2004) — α formula (P0).
- Landis & Koch (1977) — κ interpretation thresholds (P0, P1).
- Westphal & Zajac (1994, 1998 ASQ) — substantive vs symbolic; positive-class encoding choice (P2).
- Fiss & Zajac (2006 ASQ) — decoupling generalization (cited via `wz_framework_boundary_justification.md`).
- Gomber et al. (2018 JMIS) — technology vs business function locus (all three).
- Jaynes (1957) — maximum entropy principle; binary case follows trivially as Bernoulli entropy (Cover & Thomas 2006 §2) (P2).
- Törnberg (2024) — LLM verbalized confidence → continuous indicator (P2).
- Shapiro, Sudhof & Wilson (2022 J.Econometrics) — continuous LHS in finance (P2).

### Citations explicitly NOT inherited

- Bingler et al. (2022 FRL) — used in `stage3_dual_track_plan_v3.2.0.md` for sentiment ∧ substantiveness 4-way count; NOT relevant to this plan.
- Platt (1999) — used in `calibration_plan_v5.1.md` for sigmoid calibration with learned A, B; this plan applies a closed-form max-entropy map (no learned parameters), so Platt is NOT applicable here. Calibration is a downstream consumer of P2's raw output.
- De Kok (2025) — requires neutral class for 3-class softmax; innovation dims are binary.

## 3. Work Item P0 — Extend llms_evaluation.py to 4 tasks

### 3.1 Goal

[llms_evaluation.py::main()](../../validation/llms_evaluation.py#L863)
currently emits Panels A–D. After P0 it emits Panels A–F covering
verification + sentiment + innovation_substantiveness + innovation_locus,
with parallel `cm_*.png` and `per_model_*_comparison.csv` outputs. Code
path lands regardless of annotation state.

### 3.2 Academic Reference

- Cohen (1960) for κ; Krippendorff (2004) for α — same metrics applied
  to innovation dimensions unchanged.
- Bootstrap CI for small-n κ: per
  [inter_track_agreement_interpretation.md §7](inter_track_agreement_interpretation.md#L80-L86)
  ("n < 50 时 κ 置信区间宽阔，不要单点报告，需 bootstrap CI"), P0 emits
  bootstrap 95% CI when `n_gold < 50` for innovation panels. Threshold
  aligns with source.
- (P1 §4.3.1 uses always-bootstrap deliberately: stage-level audit costs
  negligibly; uniform schema simpler for paper Table A1.)

### 3.3 File Changes

#### 3.3.1 `news_process/validation/llms_evaluation.py`

- **Generalize results dict** at L993-1004 to four task keys
  (`verification`, `sentiment`, `innovation_substantiveness`,
  `innovation_locus`). Task-driven loop, not hard-coded branches.
- **Gold-label sources**:
  - Verification + sentiment: `32_news_llms_human_samples.xlsx` (existing).
  - Innovation: `manual_validation_samples.xlsx` columns
    `R{1,2,3}_stage3a_substantiveness`, `R{1,2,3}_stage3a_conf`,
    `R{1,2,3}_stage3b_locus`, `R{1,2,3}_stage3b_conf`. The
    `_rationale` columns exist in the xlsx but are NOT consumed.
- **Hardcoded schema** lives in a single source-of-truth constant
  `R_COLUMNS_BY_RATER` placed in
  `news_process/pipeline/validation/manual_validation_schema.py`
  (new module). Both `_merge_manual_validation_raters` and a coupling
  test import this constant. The emitter
  [manual_validation_sampling.py:130-144](../../scripts/migrate/manual_validation_sampling.py#L130-L144)
  is asserted to emit the same names.
- **Pending semantics**:
  - File absent → emit Panels E/F with footnote "manual validation pending — file not present".
  - File present, all R-columns NaN → footnote "manual validation pending — n=0 fully-annotated rows".
  - File present, R-columns missing or misnamed → footnote "manual validation pending — schema mismatch".
- **`_merge_manual_validation_raters(df_mv)` helper**: per row:
  1. Collect 3 substantiveness cells; drop NaN.
  2. If 0 remain → skip row from substantiveness gold.
  3. If ≥ 2 remain and ≥ 2 agree → row kept with that label.
  4. If 2 remain disagreeing (1-1 with missing 3rd) → row dropped (tie).
  Same for locus. Output columns: `gold_substantiveness`, `gold_locus`.
- **`_evaluate_classification_task(...)` function** parameterized by
  task_name, gold_col, pred_col_template, per_model_col_template,
  class_labels, output_dir, `bootstrap_when_n_below=50`. Bodies of the
  current verification (L1068-1155) and sentiment (L1162-1247) blocks
  factor into this single function. CLI behavior preserved.
- **`generate_latex_table()`** (L404-505): extend to Panel E
  (substantiveness) + Panel F (locus). When gold absent, Panels emit
  a single "manual validation pending" row.
- **Join logic**: prefer `docid` (production schema), fall back to
  `orig_index` (manual_validation xlsx schema). If neither key resolves
  uniquely, raise with clear error message.

#### 3.3.2 `news_process/pipeline/validation/manual_validation_schema.py` (new)

- Single-source constant:
  ```python
  R_COLUMNS_BY_RATER = {
      'substantiveness': [
          'R1_stage3a_substantiveness',
          'R2_stage3a_substantiveness',
          'R3_stage3a_substantiveness',
      ],
      'locus': [
          'R1_stage3b_locus',
          'R2_stage3b_locus',
          'R3_stage3b_locus',
      ],
  }
  ```
- Imported by `llms_evaluation.py` AND by the coupling test in §3.3.3.

#### 3.3.3 `news_process/tests/test_33_evaluation.py` (extend existing file)

The existing file currently tests `diagnose_misclassification_bias`
only. P0 adds the following new tests; existing tests must continue
to pass.

1. `test_merge_majority_3_agree`: 3 raters all agree → row kept.
2. `test_merge_majority_2_of_3`: 2 agree, 1 disagrees → row kept.
3. `test_merge_2_agree_1_missing`: 2 agree, 1 NaN → row kept.
4. `test_merge_1_1_tie_with_missing`: 1 substantive, 1 symbolic, 1 NaN → row dropped.
5. `test_merge_all_missing`: 3 NaN → row dropped.
6. `test_panels_E_F_present_with_gold`: synthetic xlsx with 30 valid rows; assert PNG, CSV, and `Panel E`/`Panel F` (non-pending) in TeX.
7. `test_panels_E_F_pending_when_empty`: synthetic xlsx with 30 rows but all R-columns NaN; assert pending footnote in Panels E/F.
8. `test_panels_E_F_pending_when_file_absent`: no xlsx; assert pending footnote; main does not raise.
9. `test_panels_A_to_D_structural_equality`: pre/post structural diff via regex filter `^% Generated:|^% Timestamp:|^% Run-ID:` plus additions after Panel D's `\end{tabular}`; remaining diff empty. Fixture: `tests/fixtures/classification_eval_table_A_to_D_golden.tex`, created during P0 authoring.
10. `test_xlsx_with_wrong_columns_emits_pending` (R2C-04): xlsx exists but missing R-columns → pending footnote, no raise.
11. `test_join_falls_back_to_orig_index` (R2C-04): 21_tone_llms.parquet lacks `docid` → join on `orig_index` succeeds.
12. `test_duplicate_docid_raises` (R2C-04): synthetic xlsx with 2 rows sharing `docid` → deterministic dedupe (keep first) with WARN log.
13. `test_r_column_schema_coupling` (R2C-02): import `R_COLUMNS_BY_RATER` and `manual_validation_sampling.py`; assert the sampling script's emitted columns match the constant.

**P0 test delta: +13 (count 1153 → 1166 after P0).**

#### 3.3.4 Test fixtures

- `news_process/tests/fixtures/manual_validation_samples_synthetic.xlsx`:
  30 valid + 30 empty rows. Built by
  `news_process/tests/fixtures/_make_manual_validation_synthetic.py`
  (also committed). Convention note: this is the first xlsx fixture in
  `tests/fixtures/`; reused by R2B-06 precedent allowance.
- `news_process/tests/fixtures/classification_eval_table_A_to_D_golden.tex`:
  snapshot of pre-refactor Panel A–D output for structural-diff test.

### 3.4 Data Flow

```
manual_validation_samples.xlsx (n=248, R1/R2/R3 columns)
  → _merge_manual_validation_raters → gold_substantiveness / gold_locus
21_tone_llms.parquet
  → df_pred (innovation_*_full, _ctx)
join on docid (preferred) or orig_index (fallback)
  → df_eval_innov
  → _evaluate_classification_task × 2, with bootstrap CI when n_gold < 50
  → results.classifier_metrics.{innovation_substantiveness, innovation_locus}
  → cm_*.png, per_model_*.csv, classification_eval_table.tex Panel E/F
```

### 3.5 Test Plan

- `"F:/Anaconda3/python.exe" -m pytest news_process/tests/test_33_evaluation.py -v` — existing + 13 new.
- `"F:/Anaconda3/python.exe" -m pytest`. Test count: `assert collected == 1153 + Σ(P0=13, P1=8, P2=17) = 1191` (per work-item deltas declared in §3.5/§4.5/§5.5).
- No golden-baseline regeneration needed (no panel schema changes).
- Lint: `ruff check news_process/validation/llms_evaluation.py
  news_process/pipeline/validation/manual_validation_schema.py
  news_process/tests/test_33_evaluation.py
  news_process/tests/fixtures/_make_manual_validation_synthetic.py`.

### 3.6 Risks and Rollback

| Risk | Mitigation |
|---|---|
| Refactor breaks Panels A–D | `test_panels_A_to_D_structural_equality` regression. |
| `manual_validation_samples.xlsx` absent in CI | Pending footnote; never raise. |
| R-column schema drift | `R_COLUMNS_BY_RATER` single-source constant; `test_r_column_schema_coupling` enforces emitter alignment. |
| Bootstrap non-determinism | `numpy.random.default_rng(seed=42)`. |
| `docid` join key duplicates | `test_duplicate_docid_raises`; dedupe-with-warn semantics specified. |
| `docid` absent entirely | Falls back to `orig_index`; `test_join_falls_back_to_orig_index`. |

Rollback: `git revert <commit>`; no schema migration.

### 3.7 Acceptance Criteria

**Code-path acceptance** (achievable now):
- `pytest news_process/tests/test_33_evaluation.py -v` reports all tests pass.
- `pytest` collected count satisfies `count - 1153 == Σ(deltas)`.
- `classification_eval_table.tex` contains literal `"Panel E"` and `"Panel F"` (pending or populated).
- Filtered diff of pre/post `classification_eval_table.tex` (regex `^% Generated:|^% Timestamp:|^% Run-ID:` removed, additions after Panel D's `\end{tabular}` ignored) is empty.
- `ruff check` clean on touched / new files.

**Data-path acceptance** (deferred to rater unblocking):
- `eval_reports/cm_innovation_substantiveness_llm_{full,ctx}.png` non-empty.
- `eval_reports/cm_innovation_locus_llm_{full,ctx}.png` non-empty.
- `per_model_innovation_substantiveness_comparison.csv` and `per_model_innovation_locus_comparison.csv` exist with ≥ 1 data row.
- Panels E/F in TeX populated (not pending).

## 4. Work Item P1 — Inter-track κ Python audit stage

### 4.1 Goal

Implement Python counterpart of
[20_tableA1_inter_track_kappa.do.tmpl](../../papers/_common/stata_templates/20_tableA1_inter_track_kappa.do.tmpl).
Compute article-level Cohen's κ for `innovation_locus_full` vs
`innovation_locus_ctx` and for `innovation_substantiveness_full` vs
`innovation_substantiveness_ctx` on `llm_verified_dual_both == True`
subset; emit `inter_track_kappa_table.csv` + `.tex` to `eval_reports/`.
Stage number `39a` (validation block 31-39; alphabetic suffix per
existing 32a/38a/38b precedent).

### 4.2 Academic Reference

- Landis & Koch (1977) — κ interpretation thresholds.
- Cohen (1960) — κ formula.
- [inter_track_agreement_interpretation.md §2](inter_track_agreement_interpretation.md#L14-L21):
  κ ∈ [0.50, 0.70] is the **expected** range (not "higher is better");
  κ > 0.70 flags redundant dual-track; κ < 0.30 flags one track as noise.
- P1 always-bootstrap policy: bootstrap cost negligible at stage scope;
  uniform output schema simpler for paper Table A1. Distinct from P0's
  n<50 conditional bootstrap.

### 4.3 File Changes

#### 4.3.1 `news_process/pipeline/audit/inter_track_kappa.py` (new)

- `_compute_kappa_with_bootstrap(y1, y2, n_boot=1000, seed=42)`:
  1. Call [cohens_kappa_2cat](../../validation/radius_sensitivity_llm.py#L54)
     for the point κ (returns `{kappa, observed_agreement, expected_agreement, n}`; no bootstrap upstream).
  2. Bootstrap implemented here via `rng = numpy.random.default_rng(seed)`;
     resample indices with replacement n_boot times; collect κ values.
  3. Return `(kappa_point, np.percentile(kappas, 2.5), np.percentile(kappas, 97.5), n_obs)`.
  4. Edge cases: n_obs == 0 → `(nan, nan, nan, 0)`; one column constant → `(nan, nan, nan, n_obs)`.
- `compute_inter_track_kappa(df) -> pd.DataFrame`: 7 columns:
  `field`, `kappa_point`, `ci_95_low`, `ci_95_high`, `n_obs`, `threshold`,
  `passes_threshold` (kappa_point ≥ threshold; NaN κ → False).
  Computes for `innovation_locus` (threshold 0.50) and
  `innovation_substantiveness` (threshold 0.45).
- `run_stage(config, logger)`:
  1. Load `21_tone_llms.parquet`.
  2. If column `llm_verified_dual_both` is absent → log WARN, emit CSV
     with NaN rows; do not raise.
  3. Filter on `llm_verified_dual_both == True`; if empty → emit NaN rows + WARN.
  4. Call `compute_inter_track_kappa`.
  5. Write CSV + TeX (booktabs).
  6. Per-field threshold check; RuntimeWarning if κ outside [0.30, 0.70].

#### 4.3.2 `news_process/39a_inter_track_kappa.py` (new thin shim)

- ≤ 30 lines (shim invariant).
- Imports `news_process.pipeline.audit.inter_track_kappa.run_stage`.

#### 4.3.3 `news_process/core/dag.py`

- Register new `StageSpec` in `STAGES_VALIDATION`:
  ```
  name="阶段39a: Inter-track Cohen's κ for innovation dimensions"
  script="39a_inter_track_kappa.py"
  group="validation", kind="audit"
  enabled_when=_VALIDATION_PREDS['inter_track_kappa']
  ```
- Add `_VALIDATION_PREDS['inter_track_kappa']` (module-scope callable
  identity for `test_predicate_identity_module_scope` per
  `tests/integration/test_dag_consistency.py:122-126`).

#### 4.3.4 `news_process/core/schemas.py`

- Add `"39a_inter_track_kappa.py"` to `EXPECTED_NO_OUTPUT_STAGES`
  (L147-161). The `.py` suffix matches existing convention.

#### 4.3.5 `news_process/tests/integration/test_dag_consistency.py`

- Line 98 hard-asserts `len(core_dag.STAGES_VALIDATION) == 12`. P1 must
  update this constant to `13`. (R2C-01 fix.) This is the only test
  edit P1 requires.

#### 4.3.6 `news_process/tests/test_39a_inter_track_kappa.py` (new)

1. `test_kappa_full_agreement`: 100 rows all `_full == _ctx` → κ=1.0.
2. `test_kappa_moderate_agreement`: 100 rows ≈ 20% disagree → κ ∈ [0.50, 0.70].
3. `test_kappa_empty_subset`: 0 rows → `(nan, nan, nan, 0)`; CSV NaN; no raise.
4. `test_kappa_constant_column`: 100 rows `_full` all `'应用场景'` → NaN; passes_threshold False.
5. `test_outputs_emitted`: `run_stage` writes both `.csv` and `.tex` to tmp_path; non-empty.
6. `test_dag_registration`: assert `"39a_inter_track_kappa.py"` in `EXPECTED_NO_OUTPUT_STAGES` and `STAGES_VALIDATION` (length now 13).
7. `test_kappa_bootstrap_reproducibility` (R2C-05): call `_compute_kappa_with_bootstrap` twice; `(kappa_point, ci_low, ci_high)` exactly equal.
8. `test_missing_dual_both_column` (R2C-05): parquet lacks `llm_verified_dual_both` → emit NaN row + WARN; no raise.

**P1 test delta: +8 (count 1166 → 1174 after P1).**

### 4.4 Data Flow

```
21_tone_llms.parquet
  → df[df.llm_verified_dual_both == True] (or NaN-row fallback)
  → compute_inter_track_kappa
  → DataFrame[7 cols]
  → eval_reports/inter_track_kappa_table.csv
  → eval_reports/inter_track_kappa_table.tex
```

### 4.5 Test Plan

- `"F:/Anaconda3/python.exe" -m pytest news_process/tests/test_39a_inter_track_kappa.py -v` (8 tests).
- `"F:/Anaconda3/python.exe" -m pytest news_process/tests/integration/test_dag_consistency.py -v` (updated count).
- `"F:/Anaconda3/python.exe" -m pytest`.
- Lint: `ruff check news_process/pipeline/audit/inter_track_kappa.py
  news_process/39a_inter_track_kappa.py
  news_process/tests/test_39a_inter_track_kappa.py`.

### 4.6 Risks and Rollback

| Risk | Mitigation |
|---|---|
| Bootstrap non-determinism | `numpy.random.default_rng(seed=42)`; `test_kappa_bootstrap_reproducibility`. |
| Constant column / empty subset | `test_kappa_constant_column`, `test_kappa_empty_subset`. |
| Missing dual-both column | `test_missing_dual_both_column`. |
| Stage in wrong DAG list | `test_dag_registration`. |
| Filename suffix mismatch | Asserted as exact string. |
| `test_dag_consistency.py` STAGES_VALIDATION count regression | P1 commit includes the L98 constant update; new count 13. |

Rollback: `git revert <commit>` reverts shim, pipeline module, dag.py,
schemas.py, test_dag_consistency.py count change. Stata template
`20_tableA1_inter_track_kappa.do.tmpl` reads `21_tone_llms.dta` directly
and does NOT depend on the Python stage's CSV output (verified at v1.2
authoring: `grep -F "eval_reports/inter_track_kappa" news_process/papers/`
returns no hits), so P1 revert is template-safe.

### 4.7 Acceptance Criteria

- `"F:/Anaconda3/python.exe" news_process/39a_inter_track_kappa.py` exits 0; produces both files.
- CSV has 2 data rows (innovation_locus, innovation_substantiveness), 7 columns each per §4.3.1.
- `threshold ∈ {0.45, 0.50}`; `passes_threshold ∈ {True, False}`.
- TeX passes `pdflatex` smoke compile in the Robustness Appendix wrapper.
- `test_dag_consistency.py` green (STAGES_VALIDATION count = 13 after P1).

## 5. Work Item P2 — Binary prob_score for innovation dimensions

### 5.1 Goal

Add `prob_score ∈ [0, 1]` for `innovation_substantiveness` and
`innovation_locus` at article + bank-year levels. Article-level:
`avg_subst_prob_score_{full,ctx}`, `avg_locus_prob_score_{full,ctx}`.
Panel-level: same names + `_std_*` standard deviation columns.

### 5.2 Academic Reference

- Jaynes (1957). *Physical Review* 106(4) 620-630 — maximum-entropy
  principle. The 3-class case is in
  [compute_prob_score docstring](../../pipeline/sentiment/tone_llms.py#L699-L703).
  The binary analogue is the standard Bernoulli entropy in Cover &
  Thomas (2006) *Elements of Information Theory* §2.
- **Derivation (corrected per R2A-01)**: the LLM emits a predicted
  label `ℓ ∈ {0, 1}` with verbalized confidence `c` (interpretation:
  `P(ℓ | x) = c`). Under the constraint `P(ℓ | x) = c`, the max-entropy
  distribution over a 2-element alphabet is `P(ℓ) = c, P(not ℓ) = 1 − c`.
  We then **relabel** to a fixed positive_class for downstream
  econometrics: `prob_score := P(positive_class | x)`, which equals `c`
  if `ℓ == positive_class` and `1 − c` otherwise. The positive_class
  assignment is a downstream econometric encoding; it does NOT alter
  the LLM's pre-registered judgment rule.
- Törnberg (2024). arXiv:2307.13106 — methodological framework for
  building continuous indicators from LLM verbalized confidence.
- Shapiro, Sudhof & Wilson (2022 J.Econometrics) — continuous LHS
  necessity in finance/econometrics; same anchor as
  [tone_llms.py:694-697](../../pipeline/sentiment/tone_llms.py#L694-L697).
- Platt (1999) NOT used here (no learned sigmoid); reserved for
  `calibration_plan_v5.1.md` downstream consumer.
- De Kok (2025) NOT applicable (requires neutral class for 3-class
  softmax).

### 5.3 File Changes

#### 5.3.1 `news_process/pipeline/sentiment/tone_llms.py`

- **New function `compute_prob_score_binary(label, confidence, positive_class)`**
  placed adjacent to existing `compute_prob_score` at
  [L680](../../pipeline/sentiment/tone_llms.py#L680). Returns
  `{prob_score, prob_source}` with `prob_source ∈ {"P2_BIN", "P3_BIN"}`.

  **Input domain validation** (R2C-06):
  - `confidence` clamped to `[0, 1]` (values outside this range due to
    floating-point or JSON parsing fall back to `P3_BIN` and the clamped
    bound).
  - `label` must be in the valid binary label set; else `prob_source = "P3_BIN"`, `prob_score = NaN`.

  **Behavior**:
  - `label is None` or `confidence is None`: `(NaN, "P3_BIN")`.
  - `label` not in valid binary labels: `(NaN, "P3_BIN")`.
  - `confidence` outside `[0, 1]` (e.g., 1.0001 or -0.0001 from rounding error): clamp to `[0, 1]`, return `(NaN, "P3_BIN")`.
  - `confidence == 0`: one-hot fallback (label == positive_class → 1.0; else → 0.0), `prob_source = "P3_BIN"`.
  - `label == positive_class` and `0 < confidence ≤ 1`: `(confidence, "P2_BIN")`.
  - `label != positive_class` and `0 < confidence ≤ 1`: `(1.0 - confidence, "P2_BIN")`.

  `prob_source` is exactly two states `{P2_BIN, P3_BIN}`, parallel to
  existing `{P2, P3}` for the 3-class function. The codes describe the
  mapping branch (max-entropy vs one-hot/missing), NOT the predicted
  label (which is in the categorical columns).

- **Positive-class choice — Stata-encoding-consistent**:
  - Substantiveness: `positive_class = "象征性"`.
  - Locus: `positive_class = "应用场景"`.

  Rationale: `stata_export.py` defines
  [SUBSTANTIVENESS_ENCODING](../../pipeline/panel/stata_export.py#L40-L50)
  as `{实质性: 0, 象征性: 1}` and
  [LOCUS_ENCODING](../../pipeline/panel/stata_export.py#L40-L50)
  as `{底层技术: 0, 应用场景: 1}` (`0=baseline, 1=对照`). Choosing
  positive_class = `象征性` / `应用场景` aligns
  `prob_score = 1 ↔ encoded byte = 1 ↔ "对照" pole`, preserving sign
  conventions across all downstream regressions (concrete consumer:
  `papers/bank_fintech_tone/analysis.py` uses
  `innovation_substantiveness_*` and `innovation_locus_*` columns as
  regressors; per R2A-06 a paper-level regression spec referencing
  `avg_subst_prob_score_*` as continuous LHS will be added in the same
  P2 commit's `papers/bank_fintech_tone/tables.py` extension once the
  column is available).

  This is an encoding choice (downstream of LLM labels), NOT a prompt
  change. unified_cot.txt v7 pre-registered judgment is preserved.

- **`wz_framework_boundary_justification.md` footnote — exact text
  (R2A-02, R2C-03)**:

  P2 commit appends the following verbatim paragraph at the end of §3
  of `wz_framework_boundary_justification.md`:

  > **Footnote (added 2026-05-XX with P2 commit)**. For quantitative
  > downstream econometrics, the binary `prob_score` columns
  > (`avg_subst_prob_score_*`, `avg_locus_prob_score_*`) adopt the
  > positive pole `1 = 象征性 / 应用场景`, consistent with the existing
  > Stata value-label encoding declared in `stata_export.py:40-50`
  > (`SUBSTANTIVENESS_ENCODING = {实质性: 0, 象征性: 1}`;
  > `LOCUS_ENCODING = {底层技术: 0, 应用场景: 1}`; `0 = baseline,
  > 1 = 对照`). This is an encoding choice downstream of LLM judgment;
  > it does NOT alter the pre-registered classification rules in
  > `unified_cot.txt v7` (git tag `prompt-v7-released`). Sign
  > conventions in all panel regressions consuming these columns are
  > anchored to the `1 = 象征性 / 应用场景` pole.

  The footnote's presence is asserted by `test_wz_footnote_present`
  (§5.3.5 item 13). The wording is committed verbatim; any future
  change requires updating both the doc and the test in the same
  commit. P2 commit creates a new git tag `wz-boundary-positive-class-pinned`
  referencing the footnote-augmented file.

- **`_aggregate_track`** ([L773-940](../../pipeline/sentiment/tone_llms.py#L773-L940)):
  add per-model binary prob_score computation for substantiveness
  (positive_class `"象征性"`) and locus (positive_class `"应用场景"`).
  NaN-safe mean via `np.nanmean` across non-NaN per-model scores.
  Returns 2 new fields: `avg_subst_prob_score`, `avg_locus_prob_score`.

- **`main` function** at
  [L1050](../../pipeline/sentiment/tone_llms.py#L1050) (function
  header; column-writing code lives within main's body, below
  `_aggregate_track` invocation per existing pattern): writes 4 new
  article-level columns to the dataframe:
  `avg_subst_prob_score_full`, `avg_subst_prob_score_ctx`,
  `avg_locus_prob_score_full`, `avg_locus_prob_score_ctx`.

#### 5.3.2 `news_process/pipeline/panel/encode.py`

- Extend bank-year aggregation pattern at
  [L582-583](../../pipeline/panel/encode.py#L582-L583): emit 8 new
  panel columns:
  - `avg_subst_prob_score_full`, `avg_subst_prob_score_full_std`
  - `avg_subst_prob_score_ctx`, `avg_subst_prob_score_ctx_std`
  - `avg_locus_prob_score_full`, `avg_locus_prob_score_full_std`
  - `avg_locus_prob_score_ctx`, `avg_locus_prob_score_ctx_std`
- Aggregation: `np.nanmean` (mean), `np.nanstd(ddof=1)` (std).
- NaN propagation: zero-article bank-year cells remain NaN (consistent
  with [L1105](../../pipeline/panel/encode.py#L1105)).

#### 5.3.3 `news_process/pipeline/panel/codebook.py`

- Add 8 `VariableMetadata` entries following the pattern at
  [L305](../../pipeline/panel/codebook.py#L305). Formula text cites
  `compute_prob_score_binary` and includes the chosen `positive_class`
  per dimension.

#### 5.3.4 `news_process/pipeline/panel/stata_export.py`

- Add 8 entries to `HEURISTIC_LABELS` dict in `build_variable_labels`
  ([L108-124](../../pipeline/panel/stata_export.py#L108-L124)), after
  L124, before the closing brace.
- Add 8 column-name patterns to `core_patterns` whitelist in
  `assign_core_columns`
  ([L162-200](../../pipeline/panel/stata_export.py#L162-L200)), so they
  are tagged "core" (not "aux") under the Stata IC 2048-var cap.
- Validation: `validate_stata_compat`
  ([L268-269](../../pipeline/panel/stata_export.py#L268-L269)) enforces
  `len(label.encode('utf-8')) ≤ STATA_VAR_LABEL_MAXLEN = 80` (BYTES,
  not chars per
  [L37](../../pipeline/panel/stata_export.py#L37)).

  **Proposed labels with UTF-8 byte lengths** (em-dash `—` U+2014 = 3
  bytes):

  | Column | Label | Chars | Bytes |
  |---|---|---|---|
  | `avg_subst_prob_score_full` | `Avg Subst P_BIN (full-track) — 1=symbolic, max-ent map` | 54 | 56 |
  | `avg_subst_prob_score_full_std` | `Std Subst P_BIN (full-track, bank-year SD)` | 42 | 42 |
  | `avg_subst_prob_score_ctx` | `Avg Subst P_BIN (ctx-track) — 1=symbolic, max-ent map` | 53 | 55 |
  | `avg_subst_prob_score_ctx_std` | `Std Subst P_BIN (ctx-track, bank-year SD)` | 41 | 41 |
  | `avg_locus_prob_score_full` | `Avg Locus P_BIN (full-track) — 1=application, max-ent map` | 57 | 59 |
  | `avg_locus_prob_score_full_std` | `Std Locus P_BIN (full-track, bank-year SD)` | 42 | 42 |
  | `avg_locus_prob_score_ctx` | `Avg Locus P_BIN (ctx-track) — 1=application, max-ent map` | 56 | 58 |
  | `avg_locus_prob_score_ctx_std` | `Std Locus P_BIN (ctx-track, bank-year SD)` | 41 | 41 |

  All UTF-8 byte counts ≤ 80; satisfies Stata IC limit per validator.

#### 5.3.5 `news_process/tests/test_compute_prob_score_binary.py` (new)

1. `test_positive_label_positive_class`: `("象征性", 1.0, "象征性") == {prob_score: 1.0, prob_source: "P2_BIN"}`.
2. `test_negative_label_positive_class`: `("实质性", 1.0, "象征性") == {prob_score: 0.0, prob_source: "P2_BIN"}`.
3. `test_mid_confidence_positive`: `("象征性", 0.5, "象征性") == {prob_score: 0.5, prob_source: "P2_BIN"}`.
4. `test_none_label`: `(None, 0.7, "象征性") == {prob_score: NaN, prob_source: "P3_BIN"}`.
5. `test_invalid_label`: `("invalid", 0.7, "象征性") == {prob_score: NaN, prob_source: "P3_BIN"}`.
6. `test_zero_confidence_positive`: `("象征性", 0.0, "象征性") == {prob_score: 1.0, prob_source: "P3_BIN"}`.
7. `test_zero_confidence_negative`: `("实质性", 0.0, "象征性") == {prob_score: 0.0, prob_source: "P3_BIN"}`.
8. `test_all_none_aggregation`: 5 (None, NaN, "象征性") tuples; `np.nanmean` returns NaN, no division-by-zero.
9. `test_mismatched_positive_class`: positive_class `"不存在"` (no matching label); every input yields NaN.
10. `test_confidence_clamp_above_one` (R2C-06): `("象征性", 1.0001, "象征性") → (NaN, "P3_BIN")` (out-of-domain).
11. `test_confidence_clamp_below_zero` (R2C-06): `("象征性", -0.0001, "象征性") → (NaN, "P3_BIN")`.
12. `test_three_class_compute_prob_score_unchanged_smoke` (R2C-06): import `compute_prob_score`; assert `compute_prob_score("正面", 0.7) == {'prob_pos': 0.7, 'prob_neu': 0.15, 'prob_neg': 0.15, 'prob_score': 0.55, 'prob_source': 'P2'}` (1-line guard against accidental edits to the 3-class function).

#### 5.3.6 `news_process/tests/test_panel_binary_prob_columns.py` (new)

13. `test_wz_footnote_present` (R2C-03): `grep -F "1 = 象征性 / 应用场景 positive pole"` on `wz_framework_boundary_justification.md` matches at least one line (assertion in pytest).
14. `test_eight_new_columns_present`: integration with mocked `21_tone_llms.parquet`; 8 new column names appear in `40_panel_yearly.parquet`.
15. `test_zero_article_bank_year_nan`: zero-article bank-year cell → all 8 columns NaN.
16. `test_positive_class_encoding_assertion`: synthetic article with label `"象征性"`, confidence 1.0 → `avg_subst_prob_score_full == 1.0`.
17. `test_golden_baseline_diff_scope`: regenerate golden snapshot; assert diff scope (see §5.6 for enumeration).

**P2 test delta: +17 (count 1174 → 1191 after P2).**

#### 5.3.7 `news_process/tests/fixtures/golden_panel_v0.json`

Regenerate via
`"F:/Anaconda3/python.exe" news_process/scripts/migrate/generate_golden_snapshot.py`
(consistent with §10). Commit alongside code changes.

### 5.4 Data Flow

```
LLM JSON per article × model
  → per-model label + confidence (subst, locus)
  → compute_prob_score_binary × 2 per model (positive_class 象征性 / 应用场景)
  → per-model binary prob_score (P2_BIN / P3_BIN)
  → np.nanmean across models → avg_*_prob_score per track
  → article-level columns in 21_tone_llms.parquet (4 new)
  → bank-year np.nanmean + np.nanstd in encode.py
  → 8 new panel columns in 40_panel_yearly.parquet
  → propagated via left join into 41_panel_with_controls.parquet and 51_panel_with_controls.parquet
  → codebook.xlsx, .dta export
```

### 5.5 Test Plan

- `pytest news_process/tests/test_compute_prob_score_binary.py -v` (12 tests).
- `pytest news_process/tests/test_panel_binary_prob_columns.py -v` (5 tests).
- `pytest news_process/tests/test_prob_score.py -v` (existing 3-class non-regression; must remain green).
- `pytest news_process/tests/integration/test_panel_reproducibility.py -v`.
- `pytest`.
- Lint: `ruff check news_process/pipeline/sentiment/tone_llms.py
  news_process/pipeline/panel/encode.py news_process/pipeline/panel/codebook.py
  news_process/pipeline/panel/stata_export.py news_process/tests/test_compute_prob_score_binary.py
  news_process/tests/test_panel_binary_prob_columns.py`.

### 5.6 Risks and Rollback

| Risk | Mitigation |
|---|---|
| Golden baseline diff affects unrelated stages | `test_golden_baseline_diff_scope` asserts the expected diff (see below). |
| Positive-class flipped silently | `test_positive_class_encoding_assertion`; codebook formula text; verbatim footnote in wz doc; `test_wz_footnote_present`. |
| 3-class `compute_prob_score` regressed | `test_three_class_compute_prob_score_unchanged_smoke` + existing `tests/test_prob_score.py`. |
| All-NaN aggregation crashes | `test_all_none_aggregation`. |
| Out-of-domain confidence (1.0001 etc.) | `test_confidence_clamp_*` (R2C-06). |

**Expected golden-snapshot diff scope** (R2B-03, R2B-04):

Golden snapshot covers stages emitting parquets (per
`scripts/migrate/generate_golden_snapshot.py`). The 8/4 new columns
propagate as follows:

- `21_tone_llms.parquet`: +4 article-level entries (`avg_subst_prob_score_full`, `avg_subst_prob_score_ctx`, `avg_locus_prob_score_full`, `avg_locus_prob_score_ctx`) in `columns_order`, `dtypes`, `column_hashes`; `n_columns` and `size_bytes` scalars updated.
- `40_panel_yearly.parquet`: +8 bank-year entries in same fields.
- `41_panel_with_controls.parquet`: +8 entries (via left join in `pipeline/falsification/controls.py::merge_to_panel`).
- `51_panel_with_controls.parquet`: +8 entries (same propagation).
- All other stages: no diff.

`test_golden_baseline_diff_scope` asserts this exact pattern: 4 affected stages with the column counts above; all other stages unchanged.

**Rollback**: `git revert <commit>`; revert
`tests/fixtures/golden_panel_v0.json` and the wz footnote. Forward
compatibility: extra columns are ignored by old code paths. P0 does
NOT depend on P2's columns (P0 only touches `validation/llms_evaluation.py`),
so P2 revert is safe after P0 lands.

Cross-commit verification (recorded at v1.2 authoring): `grep -rE
'avg_(subst|locus)_prob_score_' news_process/ papers/` returned zero
hits outside this plan and the audit log; no downstream artifact
references the new columns yet.

### 5.7 Acceptance Criteria

- 8 new columns appear in `40_panel_yearly.parquet`; +4 in `21_tone_llms.parquet`; propagated into 41/51.
- `codebook.xlsx` documents all 8 with formulas including `positive_class`.
- `.dta` export includes all 8 with valid Stata variable labels (UTF-8 byte length ≤ 80; verified by `validate_stata_compat`).
- All 17 new tests pass.
- `tests/test_prob_score.py` remains green (3-class function unchanged).
- `compute_prob_score` source unchanged.
- `wz_framework_boundary_justification.md` contains the verbatim footnote (grep-falsifiable per `test_wz_footnote_present`).

## 6. Items explicitly NOT done

Already enumerated in §2 with reasons; consolidated here for quick
reference. See §2 for reasons.

## 7. Execution sequence and dependencies

```
P1 (inter-track κ stage)  ← no schema change, smallest blast radius
    ↓
P2 (binary prob_score)    ← golden baseline regenerated; schema +12 cols (4 article + 8 panel + propagation)
    ↓
P0 (eval 4-task refactor) ← largest refactor; isolated to validation/
```

**Independence vs reversibility — precise statements**:

- **P1**: fully reversible at any time independent of P0, P2. Stata template `20_tableA1_inter_track_kappa.do.tmpl` reads `21_tone_llms.dta` directly, NOT `eval_reports/inter_track_kappa_table.csv`, so P1 revert leaves the Stata template self-contained. (Verified by `grep -F "eval_reports/inter_track_kappa" news_process/papers/` returning no hits at v1.2 authoring.)
- **P2**: reversible while no downstream artifact references the new columns. At v1.2 authoring, `grep -rE 'avg_(subst|locus)_prob_score_' news_process/ papers/` returns zero hits outside this plan and the audit log. Once a paper draft / Stata replication pack cites these columns, P2 revert additionally requires updating that artifact. P0 does NOT reference these columns; P0 landing does not change P2 revert cost.
- **P0**: fully reversible at any time. The four parquets affected by P2 (21/40/41/51) are unaffected by P0 (P0 only edits `validation/llms_evaluation.py`).

All three are independent of `calibration_plan_v5.1` G1 unblock for
code landing. P0's **data-path acceptance** (populated Panels E/F) is
the only piece dependent on rater coordination.

## 8. End-to-end acceptance

**Numeric gate** (R2C-08 falsifiable formula):

`pytest` collected test count satisfies `count == 1153 +
delta_P0 + delta_P1 + delta_P2`, where the per-work-item deltas are
declared at §3.5 (13), §4.5 (8), §5.5 (17). At v1.2 the target is
1191; the gate is the formula, not the constant — if any per-work-item
delta changes, the total updates automatically.

**File-existence gates** (post all three commits):

`news_process/data/processed/eval_reports/`:
- `cm_innovation_substantiveness_llm_{full,ctx}.png` (data-path; pending until raters unblock)
- `cm_innovation_locus_llm_{full,ctx}.png` (data-path)
- `per_model_innovation_substantiveness_comparison.csv` (data-path)
- `per_model_innovation_locus_comparison.csv` (data-path)
- `inter_track_kappa_table.csv` (code-path)
- `inter_track_kappa_table.tex` (code-path)
- `classification_eval_table.tex` with Panels A–F (Panels E/F pending until raters unblock)

`news_process/data/processed/40_panel_yearly.parquet`: 8 new columns.
`news_process/data/processed/codebook.xlsx`: 8 new VariableMetadata entries.
`news_process/data/processed/*.dta`: 8 new variables with byte-valid labels.

**Paper-draft gate** (R2A-04):

Any manuscript Section / table that cites Panels E/F by content (not
just by name) requires `test_panels_E_F_pending_when_empty` to be
inactive — i.e., data-path acceptance must hold. A CI marker
`PENDING_INNOVATION_PANELS` is emitted by `llms_evaluation.py` when
Panels E/F are pending; manuscript builds that reference Panel E/F
must detect this marker and refuse to compile. The detection logic
lives in `papers/_common/manuscript_gates.py` (added with P0;
≤30 lines).

## 9. Out-of-band requirements satisfied

- **Git commit protocol**: each work item a separate commit, HEREDOC body, `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer (per CLAUDE.md §Critical Constraints).
- **Shim invariant**: only `39a_inter_track_kappa.py` (P1) adds a new shim; ≤30 lines.
- **DAG consistency**: P1 registers in `STAGES_VALIDATION` and adds `"39a_inter_track_kappa.py"` (`.py` suffix) to `EXPECTED_NO_OUTPUT_STAGES`; P1 also updates `test_dag_consistency.py` L98 STAGES_VALIDATION count to 13. Predicate identity satisfied via `_VALIDATION_PREDS['inter_track_kappa']` module-scope callable.
- **Config-split conformance**: NO new YAML keys added by any work item. Schema constants hardcoded in `news_process/pipeline/validation/manual_validation_schema.py` (P0) as a single source of truth.
- **Ruff conformance**: lint commands per §3.5, §4.5, §5.5.
- **Pre-registration integrity**: P2's positive_class choice is downstream econometric encoding only. unified_cot.txt v7 pre-registered judgment is preserved. Verbatim footnote committed to `wz_framework_boundary_justification.md` per §5.3.1; grep-falsifiable by `test_wz_footnote_present`. New git tag `wz-boundary-positive-class-pinned` referenced.

## 10. Verification commands

```bash
# Repository root: f:\WiseSearch\data_antigravity_project\

# P0
"F:/Anaconda3/python.exe" -m pytest news_process/tests/test_33_evaluation.py -v
"F:/Anaconda3/python.exe" -m news_process.validation.llms_evaluation

# P1
"F:/Anaconda3/python.exe" -m pytest news_process/tests/test_39a_inter_track_kappa.py -v
"F:/Anaconda3/python.exe" -m pytest news_process/tests/integration/test_dag_consistency.py -v
"F:/Anaconda3/python.exe" news_process/39a_inter_track_kappa.py

# P2
"F:/Anaconda3/python.exe" -m pytest news_process/tests/test_compute_prob_score_binary.py -v
"F:/Anaconda3/python.exe" -m pytest news_process/tests/test_panel_binary_prob_columns.py -v
"F:/Anaconda3/python.exe" -m pytest news_process/tests/test_prob_score.py -v
"F:/Anaconda3/python.exe" -m pytest news_process/tests/integration/test_panel_reproducibility.py -v
"F:/Anaconda3/python.exe" news_process/scripts/migrate/generate_golden_snapshot.py

# Full regression
"F:/Anaconda3/python.exe" -m pytest
```

## 11. Open items

(None as of v1.2; Round 2 audit findings all addressed in this revision.)

## 12. Audit history

See [three_dim_borrowing_execution_plan_audit_log.md](three_dim_borrowing_execution_plan_audit_log.md).
