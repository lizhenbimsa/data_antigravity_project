# Three-Dimension Borrowing Execution Plan

> **Status**: v1.15 (post-Round-17 audit; 1 CRITICAL + 1 MAJOR fixes applied; 1 finding rejected as wrong)
> **Scope**: Code-only changes; no manual annotation, no infra changes, no model retraining.
> **Authoring date**: 2026-05-15
> **Baseline**: news_process v3.2.0, pytest baseline 1153 passed / 6 skipped / 0 failed.

## 0. Document Purpose

After v3.2.0, three asymmetries remain between how `sentiment`,
`innovation_substantiveness`, and `innovation_locus` are processed.
This plan addresses each via one independent work item (P0, P1, P2).
All other candidates are explicitly ruled out (§2).

The three asymmetries:

1. **`llms_evaluation.py`** evaluates only verification + sentiment
   ([L993-1004](../../validation/llms_evaluation.py#L993-L1004)).
2. **Inter-track κ** has a Stata template
   [20_tableA1_inter_track_kappa.do.tmpl](../../papers/_common/stata_templates/20_tableA1_inter_track_kappa.do.tmpl)
   but no Python stage; no `.csv` / `.tex` in `eval_reports/`.
3. **Probability scoring** ([compute_prob_score](../../pipeline/sentiment/tone_llms.py#L680))
   is 3-class only; binary dims have no continuous prob_score column.

## 1. Context Anchors

- Project root: `f:\WiseSearch\data_antigravity_project\`.
- Python interpreter: `F:\Anaconda3\python.exe` (memory `python_interpreter`).
- Package: `news_process/`; CLAUDE.md governs conventions.
- Sibling methodology docs (`news_process/docs/methodology/`):
  `stage3_dual_track_plan_v3.2.0.md`,
  `inter_track_agreement_interpretation.md`,
  `manual_validation_study_plan.md`,
  `wz_framework_boundary_justification.md`,
  `calibration_plan_v5.1.md`,
  `prompt_terminology_mapping.md`,
  `paper_methodology_section_draft.md`,
  `v3_2_0_release_readiness.md`.
- Existing git tag `prompt-v7-released` (pre-registration anchor for
  `unified_cot.txt v7`); verified by `git tag -l prompt-v7-released`.

## 2. Scope

### In scope

- **P0**: Extend [llms_evaluation.py](../../validation/llms_evaluation.py)
  to cover 4 tasks (verification + sentiment + substantiveness + locus).
  Code-path lands regardless of annotation state; Panels E/F display
  "manual validation pending (n=0)" footnote until rater coordination
  unblocks the data path.
- **P1**: New stage `39a_inter_track_kappa.py` computing inter-track
  Cohen's κ for innovation dimensions with bootstrap CI; emits
  `inter_track_kappa_table.csv` + `.tex` to `eval_reports/`.
- **P2**: New `compute_prob_score_binary` alongside `compute_prob_score`;
  produces binary `prob_score ∈ [0, 1]` for substantiveness and locus
  at article + bank-year levels.

### Out of scope (with reason)

| Item | Reason |
|---|---|
| Substantiveness lexicon classifier | Violates W&Z "象征性 ≠ 缺乏事实陈述" ([unified_cot.txt:51-53](../../config/prompts/unified_cot.txt#L51-L53)); breaks pre-registration. |
| Locus BERT fine-tune | Minority class has 1 sample ([manual_validation_study_plan.md:34](manual_validation_study_plan.md#L34)). |
| Tie-strategy sensitivity | Binary + 3 raters → 2-1 or 3-0 only; 3-way ties impossible. |
| Locus title-only track | Engineering cost dominates value. |
| Calibration unblock / rater coordination | External resource. |
| Stage 33 LLM-vs-human for innovation | Code path covered by P0; data path waits on rater coordination. |
| Manuscript paper-draft gate | No existing manuscript build pipeline in the repo; would be aspirational. Instead, §8 documents the guideline: paper drafts MUST NOT cite Panels E/F by content until data-path acceptance holds. This is a process discipline rule, not enforced by CI. (Round-3 finding R3A-03/R3C-02; gate removed.) |
| New sentiment dictionary work | Out of charter. |

### Academic anchors actually invoked by P0/P1/P2

- Cohen (1960) — κ formula (P0, P1).
- Krippendorff (2004) — α formula (P0).
- Landis & Koch (1977) — κ thresholds (P0, P1).
- Westphal & Zajac (1994, 1998 ASQ) — substantive vs symbolic; positive-class encoding (P2).
- Fiss & Zajac (2006, **Academy of Management Journal**, 49(6), 1173–1193) — decoupling generalization (cited via `wz_framework_boundary_justification.md:165`).
- Gomber et al. (2018 JMIS) — technology vs business function locus.
- Cover & Thomas (2006) *Elements of Information Theory* §2 — binary entropy / Bernoulli (P2).
- Jaynes (1957) — maximum entropy framing (noted; the binary case trivially reduces to direct normalization, see §5.2).
- Törnberg (2024) — LLM verbalized confidence → continuous indicator (P2).
- Shapiro, Sudhof & Wilson (2022 J.Econometrics) — continuous LHS in finance (P2).

### Citations explicitly NOT inherited

- Bingler 2022 FRL — used in `stage3_dual_track_plan_v3.2.0.md`.
- Platt 1999 — used in `calibration_plan_v5.1.md` (learned sigmoid); P2's max-entropy map is closed-form.
- De Kok 2025 — requires neutral class for 3-class softmax.

## 3. Work Item P0 — Extend llms_evaluation.py to 4 tasks

### 3.1 Goal

Extend [llms_evaluation.py::main()](../../validation/llms_evaluation.py#L863)
to emit Panels A–F (was A–D); add `cm_*.png` and
`per_model_*_comparison.csv` for substantiveness and locus.

### 3.2 Academic Reference

- Cohen (1960); Krippendorff (2004) — applied unchanged to innovation dims.
- Bootstrap CI for small-n κ: per [inter_track_agreement_interpretation.md §7](inter_track_agreement_interpretation.md#L80-L86),
  threshold `n < 50`. P0 emits bootstrap 95% CI when `n_gold < 50` for innovation panels.

### 3.3 File Changes

#### 3.3.1 `news_process/validation/manual_validation_schema.py` (new)

Schema module placed alongside `llms_evaluation.py` in the existing
`news_process/validation/` package (NOT under `pipeline/validation/`
which would be a new subdirectory with a name-collision risk — Round-3
finding R3A-04/R3C-12).

```python
# news_process/validation/manual_validation_schema.py
"""Single source of truth for manual_validation_samples.xlsx schema."""

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

# Rater cells may be in English ("substantive" / "symbolic" /
# "technology" / "application") per emitter
# scripts/migrate/manual_validation_sampling.py L130-144; LLM predictions
# and Stata encoding use Chinese. Normalize to Chinese before κ /
# confusion-matrix computation. (Round-3 R3C-01; Round-4 R4A-02
# adds whitespace + case-insensitive handling for English keys.)
_RATER_VALUE_TO_CANONICAL_LABEL_RAW = {
    'substantive': '实质性',
    'symbolic':    '象征性',
    'technology':  '底层技术',
    'application': '应用场景',
    # Already-Chinese cells pass through unchanged
    '实质性': '实质性',
    '象征性': '象征性',
    '底层技术': '底层技术',
    '应用场景': '应用场景',
}

def normalize_rater_value(raw):
    """Normalize a rater cell value to canonical Chinese label or None.

    Rules (Round-5 R5C-01 hardening):
      - None / pandas.isna(raw) / empty string → None (silent; no WARN).
      - Bool / int / float that survives isna() → None (silent; cells
        must be strings; non-string types from openpyxl auto-typing
        are explicit missing data).
      - Strings are .strip()'d; English keys are case-folded via
        .lower() before lookup; Chinese keys (CJK code points unaffected
        by case folding) match directly after .strip().
      - Unknown strings (e.g., typos like 'subtantive') → None + WARN log.
    """
    import pandas as pd
    # Early return for None / NaN-like values (pd.isna handles float nan,
    # np.nan, pd.NA, pd.NaT uniformly).
    try:
        if raw is None or pd.isna(raw):
            return None
    except (TypeError, ValueError):
        pass  # pd.isna raises on some custom types; fall through
    # Non-string types from openpyxl auto-typing (bool/int/float) → None silently.
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s:
        return None
    # Try direct match (Chinese pass-through), then case-folded (English)
    hit = (_RATER_VALUE_TO_CANONICAL_LABEL_RAW.get(s)
           or _RATER_VALUE_TO_CANONICAL_LABEL_RAW.get(s.lower()))
    if hit is None:
        # Unknown string — log WARN once per process via logger
        pass  # actual logger.warning() call in implementation
    return hit
```

#### 3.3.2 `news_process/validation/llms_evaluation.py`

- **Generalize results dict** at L993-1004 to 4 task keys
  (`verification`, `sentiment`, `innovation_substantiveness`,
  `innovation_locus`). Task-driven loop.
- **Gold sources**:
  - Verification + sentiment: `32_human_samples.xlsx` (existing).
  - Innovation: `manual_validation_samples.xlsx` per columns in
    `manual_validation_schema.R_COLUMNS_BY_RATER`. The `_rationale`
    columns exist but are NOT consumed.
- **Pending semantics**:
  - File absent → Panels E/F with footnote "manual validation pending — file not present".
  - File present, all R-cells NaN → "manual validation pending — n=0".
  - File present, R-columns missing/misnamed → "manual validation pending — schema mismatch".
- **`_merge_manual_validation_raters(df_mv)` helper**, per row:
  1. Collect 3 substantiveness cells; **normalize each via `normalize_rater_value()`** (handles whitespace, case, Chinese pass-through; Round-3 R3C-01 + Round-4 R4A-02); drop None.
  2. If 0 remain → skip from gold.
  3. If exactly 1 remains → drop (insufficient inter-rater confirmation; Round-3 R3C-13).
  4. If ≥ 2 remain and ≥ 2 agree → row kept with that label.
  5. If exactly 2 remain and disagree (1-1 tie with missing 3rd) → drop.
  Same for locus. Output columns: `gold_substantiveness`, `gold_locus`.
- **`_evaluate_classification_task(...)`** parameterized by `task_name`,
  `gold_col`, `pred_col_template`, `per_model_col_template`,
  `class_labels`, `output_dir`, `bootstrap_when_n_below=50`. Factor out
  the current verification (L1068-1155) and sentiment (L1162-1247)
  blocks. CLI behavior preserved.
- **`generate_latex_table()`** (L404-505): extend to Panels E (substantiveness) + F (locus). **Structural constraint (Round-12 R12C-01)**: Panels E/F MUST be emitted in a SEPARATE `\begin{tabular}` / `\end{tabular}` block, immediately after the existing Panels A-D block. This makes "first `\end{tabular}` in file" a stable truncation anchor for `test_panels_A_to_D_structural_equality` (§3.3.3 item 11). Pending case emits a single "manual validation pending" row inside the second `tabular`.
- **Join logic**: prefer `docid` (production), fallback to `orig_index` (manual_validation xlsx). If neither resolves uniquely, raise with a clear message.

#### 3.3.3 `news_process/tests/test_33_evaluation.py` (extend existing)

Existing tests must continue to pass. **Fixture loading** in every new
test uses `Path(__file__).resolve().parent / 'fixtures' / '<name>.xlsx'`
to be cwd-independent (Round-3 R3C-05).

1. `test_merge_majority_3_agree`
2. `test_merge_majority_2_of_3`
3. `test_merge_2_agree_1_missing`
4. `test_merge_1_1_tie_with_missing` (1-1 tie + NaN 3rd → drop)
5. `test_merge_all_missing` (3 NaN → drop)
6. `test_merge_single_rater_dropped` (1 cell + 2 NaN → drop; Round-3 R3C-13)
7. `test_merge_value_normalization` — parametrize over `"substantive"`, `"Substantive"`, `" SUBSTANTIVE "`, `"象征性 "`, `"subtantive"` (typo → None), `True` (bool from openpyxl auto-type → None), `1` (int → None), `np.nan` (numpy NaN → None), `pd.NA` (pandas NA → None), `""` (empty → None); assert normalization rules per §3.3.1 (Round-3 R3C-01 + Round-4 R4A-02 + Round-5 R5C-01). Each non-string / NaN case must return None WITHOUT emitting WARN (only typo strings WARN).
8. `test_panels_E_F_present_with_gold` — synthetic xlsx 30 valid rows; assert `Panel E`/`Panel F` (non-pending) in TeX + cm PNG + per_model CSV
9. `test_panels_E_F_pending_when_empty` — 30 rows all R-cells NaN
10. `test_panels_E_F_pending_when_file_absent`
11. `test_panels_A_to_D_structural_equality` — Round-6 R6C-04 + Round-7 R7C-01 + Round-12 R12C-01 (truncation-rule revision): the pre-refactor `.tex` produced by `generate_latex_table` contains exactly ONE `\end{tabular}` (since all panels live inside a single `tabular` block). The previous byte-offset truncation rules collapse to the same byte position and provide no protection — the post-refactor will append Panels E/F BEFORE that single `\end{tabular}`, so any byte-offset truncation either (a) truncates BEFORE E/F in the post file, swallowing the new content, OR (b) truncates AT/AFTER `\end{tabular}` in both files, producing a non-empty filtered diff. **Structural constraint instead**: the P0 refactor MUST place Panels E/F in a SEPARATE `tabular` environment (a new `\begin{tabular}` / `\end{tabular}` block immediately after the existing one). This makes "first `\end{tabular}` in file" a stable anchor that occurs only once in the pre-refactor and remains the boundary between Panels A-D (1st block) and Panels E-F (2nd block) in the post-refactor.

    With the structural constraint in place, the test is:
    ```python
    def test_panels_A_to_D_structural_equality():
        pre = Path(fixtures / "classification_eval_table_A_to_D_golden.tex").read_text("utf-8")
        post = Path(eval_reports / "classification_eval_table.tex").read_text("utf-8")
        cut = lambda s: s[: s.find(r"\end{tabular}") + len(r"\end{tabular}")]
        meta = re.compile(r"^(?:% Generated:|% Timestamp:|% Run-ID:).*$", re.MULTILINE)
        assert meta.sub("", cut(pre)) == meta.sub("", cut(post))
    ```
    Sidecar offset file is no longer needed (R7C-01 rule withdrawn); test 16 (`test_golden_tex_has_no_panel_D_branch`) is replaced with `test_panels_E_F_in_separate_tabular` (R12C-01) that asserts the post-refactor TeX has exactly TWO `\begin{tabular}` blocks and the second one contains the literal `Panel E`.
12. `test_xlsx_with_wrong_columns_emits_pending` — pending footnote, no raise
13. `test_join_falls_back_to_orig_index`
14. `test_duplicate_docid_dedupe_with_warn` — dedupe keep-first; WARN logged
15. `test_r_column_schema_coupling` — import both `R_COLUMNS_BY_RATER` and `manual_validation_sampling.py`; assert column-name lists and value-vocabulary mappings match (Round-3 R3C-01 closure)
16. `test_panels_E_F_in_separate_tabular` (Round-12 R12C-01; replaces R7C-01's offset-file approach which was found vacuous): assert the post-refactor `classification_eval_table.tex` contains exactly TWO `\begin{tabular}` blocks; the first contains literals `Panel A` / `Panel B` / `Panel C` (and `Panel D` if bias-diagnostic gold present); the second contains literal `Panel E` (always) and `Panel F` (always). This enforces the structural-constraint that makes the truncation rule in test 11 valid.
17. `test_sha_missing_is_auto_generated` (Round-7 R7C-02; Round-14 R14A-01 reverts dual-fixture extension) — single fixture `manual_validation_samples_synthetic.xlsx`: delete the `.sha` sidecar; invoke the fixture-loading helper; assert the `.sha` is regenerated from the existing xlsx (re-read + re-hash); existing xlsx is NOT modified.

Note (Round-8 R8B-01 disambiguation): the tokenize-guard `test_no_orphan_twelve_in_validation_count` is P1-owned and lives in `tests/integration/test_dag_consistency.py`; it is enumerated as item 10 in §4.3.6 only. It is NOT counted in P0's +17 delta. See §4.3.5 for the function body.

**P0 test delta: +17 (P0 total 17; was 15 in v1.6, +2 for new tests 16-17 per Round-7 R7C-01/R7C-02).**

#### 3.3.4 Test fixtures and chicken-and-egg capture (Round-3 R3B-06)

`news_process/tests/fixtures/`:
- `manual_validation_samples_synthetic.xlsx`: 30 valid + 30 empty rows.

> **R14A-01 / R14B-01 update (revised in v1.13 per R15A-01 reachability path)**: v1.11 introduced a second synthetic fixture `news_llms_human_samples_synthetic.xlsx` to "unblock" pre-refactor capture of Panels A-D. Round-14 reverted that mandate after finding `llms_evaluation.py::main()` has THREE `_generate_demo_data()` fallback branches at L898 (file absent), L913 (read exception), and L966 (empty gold columns), each deterministically synthesizing 200 rows via `np.random.RandomState(42)`. **Round 15 R15A-01 refined the reachability claim**: the configured filename is `32_human_samples.xlsx` (paths.yaml:56), the file IS present in the repo's `data/processed/` (3.18 MB, 1000 rows) with empty gold annotation columns, so the L898 file-absent branch is NOT the reachable path on a clean checkout — instead, L966 (empty-gold branch) fires after the file loads successfully. The functional outcome is identical (all three branches converge to the same `np.random.RandomState(42)`-seeded data) but the documented reachability path in v1.13 cites L966 as the actual branch. The single `manual_validation_samples_synthetic.xlsx` (for innovation R-columns / Panels E/F) remains the only required new fixture.
- `_make_manual_validation_synthetic.py`: generator script. **Determinism contract (Round-4 R4C-04 + Round-5 R5C-02 weakening + Round-6 R6C-03 version-pinning)**: uses `numpy.random.default_rng(seed=42)` and sorts columns alphabetically before write. Openpyxl xlsx output is NOT byte-identical across openpyxl 3.x minor versions (ZIP timestamps + cell metadata variance — verified industry-known). The contract is therefore weakened from "byte-identical xlsx" to **"byte-identical post-read DataFrame hash under pinned pandas/numpy versions"**:
  1. After generation, immediately `pd.read_excel(...)` to reload.
  2. Compute `pd.util.hash_pandas_object(df, index=False).sum()`.
  3. Store a sidecar text file `tests/fixtures/manual_validation_samples_synthetic.sha` containing 3 lines:
     - `hash=<integer>`
     - `pandas=<pandas.__version__ at capture>`
     - `numpy=<numpy.__version__ at capture>`
  4. The fixture-loading test reads the .sha file, then **asserts the runtime pandas+numpy versions match** the captured values. Mismatch emits `pytest.skip(...)` with instructions to regenerate (NOT a fail — version drift is not a code error).
  5. Hash mismatch under matching versions IS a fail (genuine determinism break).
  6. **Missing `.sha` handling (Round-7 R7C-02)**: if the `.sha` file is absent (first-time test run, or after `git clean`), the fixture-loading helper auto-invokes the generator's hash step (re-read existing xlsx + re-hash + write `.sha`); the existing xlsx is NOT modified. Generator is idempotent: a second invocation without xlsx changes produces a byte-identical `.sha`. `test_sha_missing_is_auto_generated` (§3.3.3 item 17) covers this.
  
  Re-running the generator on a clean checkout with matching pandas/numpy versions MUST reproduce the same DataFrame hash. The xlsx itself is a regeneration artifact (committed for convenience, but the `.sha` file is the authoritative determinism anchor). If a future P0 amendment regenerates the fixture, `classification_eval_table_A_to_D_golden.tex` MUST also be re-captured at that point against the pre-refactor `llms_evaluation.py` (extending §3.3.4 commit sequence).
- `classification_eval_table_A_to_D_golden.tex`: pre-refactor snapshot. Round-12 R12C-01: sidecar `.offset` file is NOT needed (the offset-file rule was found vacuous when pre-refactor has only one `\end{tabular}`). Truncation uses the first `\end{tabular}` and the post-refactor structural constraint (Panels E/F in a separate `tabular` block).

**P0 commit sequence** (single commit, atomic; Round-14 R14A-01 / R14B-01 simplification):
1. Capture pre-refactor golden TeX. The configured filename per `config/paths.yaml:56` is `output_32_human_sample: 32_human_samples.xlsx` (NOT `32_news_llms_human_samples.xlsx` despite the variable name in the code). The file is **present** in `data/processed/` (3.18 MB, 1000 rows) but with all gold annotation columns empty (per memory `calibration_plan_v5_1_frozen`, Day 0 G1 FAIL). On a clean checkout running pre-refactor `main()`, the reachability path is: L891 `os.path.exists(verify_path) == True` (file is present) → load succeeds at L908 → L960-967 detects all-empty gold columns → L966 `df_verify = _generate_demo_data()` activates demo mode with 200 deterministic rows (`np.random.RandomState(42)`-seeded). This populates Panels A-D in the pre-refactor TeX. Inject `manual_validation_samples_synthetic.xlsx` for innovation R-columns. Capture output `classification_eval_table.tex` → `tests/fixtures/classification_eval_table_A_to_D_golden.tex`. (No code change to pre-refactor `main()` required; all three demo-fallback branches at L898/L913/L966 produce byte-identical synthesized data via `np.random.RandomState(42)`; the reachable branch under current repo state is L966.)
2. Apply the P0 refactor to `llms_evaluation.py`.
3. Add the new tests in `test_33_evaluation.py` (fixture loading uses `Path(__file__).resolve().parent / 'fixtures'`).
4. Commit all files together (manual_validation_samples_synthetic.xlsx + its `.sha` sidecar + golden TeX + refactor + new tests + schema module).

Note: Panels A-D in the golden TeX reflect the demo-data distribution at np.random.RandomState(42); the post-refactor must also run via demo-mode (or the same fixture state) to produce a byte-comparable Panels A-D region. The post-refactor `_evaluate_classification_task` MUST preserve demo-mode semantics for verification + sentiment tasks unchanged.

### 3.4 Data Flow

```
manual_validation_samples.xlsx (R1/R2/R3 cells, possibly English)
  → _merge_manual_validation_raters (normalize → Chinese; majority vote)
  → gold_substantiveness / gold_locus
21_tone_llms.parquet
  → df_pred (innovation_*_{full,ctx}; already Chinese)
join on docid (preferred) or orig_index (fallback)
  → df_eval_innov
  → _evaluate_classification_task × 2 (bootstrap CI when n_gold < 50)
  → cm_*.png, per_model_*.csv, classification_eval_table.tex Panel E/F
```

### 3.5 Test Plan

- `"F:/Anaconda3/python.exe" -m pytest news_process/tests/test_33_evaluation.py -v`.
- `"F:/Anaconda3/python.exe" -m pytest`. Falsifiable: `count == 1153 + Σ(deltas)` (R2C-08 formula).
- Lint: ruff on touched / new files.

### 3.6 Risks and Rollback

| Risk | Mitigation |
|---|---|
| Refactor breaks Panels A–D | `test_panels_A_to_D_structural_equality`. |
| xlsx absent / pending | Pending footnote; never raise. |
| R-column / value drift | `test_r_column_schema_coupling` enforces both names and value vocab. |
| Bootstrap non-determinism | `numpy.random.default_rng(seed=42)`. |
| `docid` duplicates | `test_duplicate_docid_dedupe_with_warn`. |
| `docid` absent | Fallback to `orig_index`; `test_join_falls_back_to_orig_index`. |
| Fixture loads via wrong cwd | `Path(__file__)` resolution. |

Rollback: `git revert <commit>`. The P0 commit creates 3 new files
(`manual_validation_schema.py`, fixture xlsx + generator,
golden tex) and edits `llms_evaluation.py`. No other tests import the
new schema module yet, so removal is safe.

### 3.7 Acceptance Criteria

**Code-path** (achievable now):
- All 17 new tests pass (`pytest tests/test_33_evaluation.py`).
- `pytest` collected count satisfies the formula gate.
- `classification_eval_table.tex` contains `"Panel E"` and `"Panel F"`.
- Filtered diff pre/post is empty.
- `ruff check` clean.

**Data-path** (deferred):
- `cm_innovation_substantiveness_llm_{full,ctx}.png`, `cm_innovation_locus_llm_{full,ctx}.png` non-empty.
- `per_model_innovation_substantiveness_comparison.csv`, `per_model_innovation_locus_comparison.csv` ≥ 1 data row.
- Panels E/F populated (not pending).

## 4. Work Item P1 — Inter-track κ Python audit stage

### 4.1 Goal

Python counterpart of
[20_tableA1_inter_track_kappa.do.tmpl](../../papers/_common/stata_templates/20_tableA1_inter_track_kappa.do.tmpl).
Stage number `39a` (validation block 31-39; alphabetic suffix per
existing 32a/38a/38b precedent).

### 4.2 Academic Reference

- Landis & Koch (1977); Cohen (1960).
- [inter_track_agreement_interpretation.md §2](inter_track_agreement_interpretation.md#L14-L21):
  κ ∈ [0.50, 0.70] expected; κ > 0.70 redundant; κ < 0.30 noise.
- P1 always-bootstrap policy: distinct from P0's `n < 50` conditional.
  Bootstrap cost negligible at stage scope; uniform output schema simpler for paper Table A1.

### 4.3 File Changes

#### 4.3.1 `news_process/pipeline/audit/inter_track_kappa.py` (new)

- `_compute_kappa_with_bootstrap(y1, y2, n_boot=1000, seed=42)`:
  1. **Short-circuit small n** (Round-3 R3C-04): if `n_obs < 3` → `(nan, nan, nan, n_obs)` immediately; do NOT bootstrap.
  2. Call [cohens_kappa_2cat](../../validation/radius_sensitivity_llm.py#L54) for point κ.
  3. Bootstrap via `rng = numpy.random.default_rng(seed)` for `n_obs ≥ 3`; resample indices with replacement n_boot times.
  4. Return `(kappa_point, np.percentile(kappas, 2.5), np.percentile(kappas, 97.5), n_obs)`.
  5. Edge: one column constant → `(nan, nan, nan, n_obs)`.
- `compute_inter_track_kappa(df)` → DataFrame[7 cols]: `field`, `kappa_point`, `ci_95_low`, `ci_95_high`, `n_obs`, `threshold`, `passes_threshold` (`kappa_point >= threshold`; NaN → False).
- `run_stage(config, logger)`:
  1. Read `21_tone_llms.parquet`.
  2. If `llm_verified_dual_both` column absent → WARN + emit NaN rows.
  3. Filter on True; if empty → WARN + NaN rows.
  4. Compute, write CSV + TeX (booktabs).
  5. RuntimeWarning if κ outside [0.30, 0.70].

#### 4.3.2 `news_process/39a_inter_track_kappa.py` (new thin shim, ≤30 lines)

#### 4.3.3 `news_process/core/dag.py`

- New `StageSpec` in `STAGES_VALIDATION`: name `"阶段39a: Inter-track Cohen's κ for innovation dimensions"`, script `"39a_inter_track_kappa.py"`, `group="validation"`, `kind="audit"`, `enabled_when=_VALIDATION_PREDS['inter_track_kappa']` (module-scope callable; identity-stable for `test_predicate_identity_module_scope` at `tests/integration/test_dag_consistency.py:122-126`).
- New entry in `_VALIDATION_PREDS` dict.

#### 4.3.4 `news_process/core/schemas.py`

- Add `"39a_inter_track_kappa.py"` to `EXPECTED_NO_OUTPUT_STAGES` (L147-161). `.py` suffix per existing convention.

#### 4.3.5 `news_process/tests/integration/test_dag_consistency.py`

- The `test_validation_stage_count` function at L95-100 has **four coupled hardcoded references to "12"** (Round-6 R6C-02). The P1 commit MUST update all four atomically:
  - L96 docstring: `(12)` → `(13)`.
  - L97 enumeration comment: append `+ 39a`; update sum `= 12` → `= 13`.
  - L98 assertion: `== 12` → `== 13`.
  - L99 f-string error message: `expected 12` → `expected 13`.
- All four lines MUST be in the same commit as the new stage registration; never a separate fix-up commit (Round-3 R3C-06). This is enforced by a single Edit pass during P1 implementation.
- **Future-proofing guard (Round-7 R7C-03 + Round-12 R12B-01 token-coverage fix)**: P1 also adds a new test `test_no_orphan_twelve_in_validation_count` to the same file (P1 owns the addition; disambiguation note for P0 review awareness lives at the trailing paragraph of §3.3.3, after item 17). The original tokenize-NUMBER-only scan missed STRING / COMMENT / FSTRING token contents, where 3 of the 4 hardcoded "12" refs actually live (docstring L96, comment L97, f-string L99). The corrected guard uses a `\b12\b` word-boundary regex over the full source string to catch all four sites without false positives on `122` etc.:
  ```python
  def test_no_orphan_twelve_in_validation_count():
      """Guards against future maintainers leaving stale `12` references.

      Uses \\b12\\b word-boundary regex across the entire function source
      (covers docstring, comments, f-strings, and numeric tokens).
      """
      import inspect, re
      src = inspect.getsource(test_validation_stage_count)
      hits = re.findall(r"\b12\b", src)
      assert hits == [], (
          f"Stale '12' references in test_validation_stage_count: "
          f"{len(hits)} hit(s). Expected only '13' after P1 lands. "
          f"Locations to check: docstring (L96), enumeration comment (L97), "
          f"assertion (L98), error f-string (L99)."
      )
  ```
  Catches any future hardcoded `12` reference inside the function regardless of token class (avoids false positives on `122`, `123` via `\b` word boundary).

#### 4.3.6 `news_process/tests/test_39a_inter_track_kappa.py` (new)

1. `test_kappa_full_agreement` — 100 rows; κ=1.0.
2. `test_kappa_moderate_agreement` — 100 rows ≈ 20% disagree; κ ∈ [0.50, 0.70].
3. `test_kappa_empty_subset` — 0 rows.
4. `test_kappa_constant_column`.
5. `test_kappa_small_n_short_circuit` (Round-3 R3C-04) — parametrize n ∈ {1, 2}; both return `(nan, nan, nan, n)` without invoking bootstrap.
6. `test_outputs_emitted`.
7. `test_dag_registration` — `"39a_inter_track_kappa.py"` in `EXPECTED_NO_OUTPUT_STAGES`; `len(STAGES_VALIDATION) == 13`.
8. `test_kappa_bootstrap_reproducibility` (Round-3 R3C-03) — call `_compute_kappa_with_bootstrap` twice on identical inputs; assert via `numpy.testing.assert_array_equal` on the full 4-tuple `(kappa_point, ci_low, ci_high, n_obs)`.
9. `test_missing_dual_both_column` — emit NaN row + WARN; no raise.

P1 also adds **one additional test in a different file** (`tests/integration/test_dag_consistency.py`):

10. `test_no_orphan_twelve_in_validation_count` (Round-7 R7C-03) — tokenize-based guard against future `12` literals in `test_validation_stage_count` source; function body specified at §4.3.5. Location: `tests/integration/test_dag_consistency.py` (NOT `tests/test_39a_inter_track_kappa.py`).

**P1 test delta: +10 total (9 in test_39a_inter_track_kappa.py + 1 in test_dag_consistency.py; was 9 in v1.6, +1 for new test 10 per Round-7 R7C-03).**

### 4.4 Data Flow

```
21_tone_llms.parquet
  → df[df.llm_verified_dual_both == True]  (or NaN fallback)
  → compute_inter_track_kappa
  → eval_reports/inter_track_kappa_table.csv + .tex
```

### 4.5 Test Plan

- `pytest news_process/tests/test_39a_inter_track_kappa.py -v` (9 tests in this file; the 10th P1 test lives in `tests/integration/test_dag_consistency.py`).
- `pytest news_process/tests/integration/test_dag_consistency.py -v` (count = 13).
- `pytest` formula gate.
- Lint: ruff on new files.

### 4.6 Risks and Rollback

| Risk | Mitigation |
|---|---|
| Bootstrap non-determinism | seed=42; `test_kappa_bootstrap_reproducibility`. |
| Constant column / empty / small n | Tests 3, 4, 5. |
| Missing dual-both column | Test 9. |
| Stage in wrong DAG list / suffix wrong | Test 7. |
| `test_dag_consistency.py` count drift | P1 commit is single atomic commit including the L98 update (Round-3 R3C-06). |

Rollback: `git revert <commit>` (atomic) reverts shim + pipeline module + dag.py + schemas.py + test_dag_consistency.py L98. Stata template `20_tableA1_inter_track_kappa.do.tmpl` reads `21_tone_llms.dta` directly; does NOT depend on Python CSV. Verified: `grep -F "eval_reports/inter_track_kappa" news_process/papers/` returns no hits.

### 4.7 Acceptance Criteria

- `"F:/Anaconda3/python.exe" news_process/39a_inter_track_kappa.py` exits 0; produces both files.
- CSV has 2 data rows, 7 columns; `threshold ∈ {0.45, 0.50}`; `passes_threshold ∈ {True, False}`.
- **TeX structural assertion** (replaces pdflatex; Round-3 R3C-07 + Round-4 R4C-03 booktabs correction): Python-`re` checks confirm: `\begin{tabular}` and `\end{tabular}` present; `\toprule`, `\midrule`, `\bottomrule` present (booktabs convention; NOT `\hline`); column count derived from `\begin{tabular}{...}` brace == 7; data-row count between `\midrule` and `\bottomrule` == 2.
- `test_dag_consistency.py` green after L98 update.

## 5. Work Item P2 — Binary prob_score for innovation dimensions

### 5.1 Goal

Article-level `avg_subst_prob_score_{full,ctx}`,
`avg_locus_prob_score_{full,ctx}` (4 cols) and panel-level same +
`_std_*` (8 cols total at panel level).

### 5.2 Academic Reference

- Cover & Thomas (2006) §2 — Bernoulli / binary entropy.
- Jaynes (1957) — historical max-entropy framing; for the binary case
  the derivation reduces to direct normalization (single linear
  constraint pins the remaining mass), preserved for notational
  parallelism with the 3-class function. (Round-3 R3A-05.)
- **Derivation**: LLM emits predicted label `ℓ ∈ {0, 1}` with verbalized
  confidence `c` (interpretation `P(ℓ|x) = c`). Normalization gives
  `P(¬ℓ|x) = 1 − c`. Downstream relabeling: `prob_score := P(positive_class|x)`,
  equal to `c` if `ℓ == positive_class`, else `1 − c`. The
  positive_class assignment is downstream econometric encoding only;
  it does NOT alter the pre-registered LLM judgment.
- Törnberg (2024) — LLM verbalized confidence → continuous indicator.
- Shapiro, Sudhof & Wilson (2022 J.Econometrics) — continuous LHS in
  finance.
- Platt 1999 NOT used here. De Kok 2025 NOT applicable.

### 5.3 File Changes

#### 5.3.1 `news_process/pipeline/sentiment/tone_llms.py`

- **New function** `compute_prob_score_binary(label, confidence, positive_class)` placed adjacent to existing `compute_prob_score` at [L680](../../pipeline/sentiment/tone_llms.py#L680). Returns `{prob_score, prob_source}` with `prob_source ∈ {"P2_BIN", "P3_BIN"}`.

  **Input domain validation** (Round-3 R3C-06):
  - `label is None` or `confidence is None`: `(NaN, "P3_BIN")`.
  - `label` not in valid binary labels: `(NaN, "P3_BIN")`.
  - `confidence` outside `[0, 1]` (e.g., 1.0001 from rounding): `(NaN, "P3_BIN")`.
  - `confidence == 0`: one-hot fallback (`label == positive_class` → 1.0; else → 0.0), `"P3_BIN"`.
  - `label == positive_class` and `0 < confidence ≤ 1`: `(confidence, "P2_BIN")`.
  - `label != positive_class` and `0 < confidence ≤ 1`: `(1 − confidence, "P2_BIN")`.

- **Positive-class choice — Stata-encoding-consistent**:
  - Substantiveness: `positive_class = "象征性"`.
  - Locus: `positive_class = "应用场景"`.

  Rationale: `stata_export.py:40-50` declares
  `SUBSTANTIVENESS_ENCODING = {实质性: 0, 象征性: 1}` and
  `LOCUS_ENCODING = {底层技术: 0, 应用场景: 1}` with comment
  `0 = baseline, 1 = 对照`. The value labels at
  `stata_export.py:53-61` are
  `0: 底层技术 (Technology)` / `1: 应用场景 (Application)` and
  `0: 实质性 (Substantive)` / `1: 象征性 (Symbolic)`.
  Choosing positive_class `象征性` / `应用场景` aligns
  `prob_score = 1 ↔ encoded byte = 1` for both substantiveness and
  locus, preserving downstream regression sign conventions. Concrete
  downstream consumer: `papers/bank_fintech_tone/analysis.py` uses
  these dimensions as regressors.

  This is downstream encoding only; `unified_cot.txt v7` (tag
  `prompt-v7-released`) is unchanged.

- **`wz_framework_boundary_justification.md` footnote — verbatim text** (Round-3 R3A-01/R3B-01 grep-target alignment):

  P2 commit appends the following paragraph at the end of §3 of
  `wz_framework_boundary_justification.md`:

  > **Footnote (added with P2 commit, tag `wz-boundary-positive-class-pinned`).**
  > For quantitative downstream econometrics, the binary `prob_score`
  > columns (`avg_subst_prob_score_*`, `avg_locus_prob_score_*`)
  > anchor the 1 = 象征性 / 应用场景 positive pole. The encoding is
  > consistent with `stata_export.py:40-50`
  > (`SUBSTANTIVENESS_ENCODING = {实质性: 0, 象征性: 1}`;
  > `LOCUS_ENCODING = {底层技术: 0, 应用场景: 1}`; comment `0 = baseline, 1 = 对照`)
  > and with the Stata value labels at `stata_export.py:53-61`
  > (`0: 实质性 (Substantive) / 1: 象征性 (Symbolic)`;
  > `0: 底层技术 (Technology) / 1: 应用场景 (Application)`). This
  > positive_class assignment is a downstream econometric encoding;
  > it does NOT alter the pre-registered classification rules in
  > `unified_cot.txt v7` (tag `prompt-v7-released`). All panel
  > regressions consuming these columns are anchored to the
  > 1 = 象征性 / 应用场景 positive pole.

  **Grep-falsifiable assertions** (test `test_wz_footnote_present`, §5.3.6 item 1):
  - `grep -F "1 = 象征性 / 应用场景 positive pole"` matches ≥ 1 line (the closing sentence).
  - `grep -F "0: 实质性 (Substantive) / 1: 象征性 (Symbolic)"` matches ≥ 1 line.
  - `grep -F "0: 底层技术 (Technology) / 1: 应用场景 (Application)"` matches ≥ 1 line.

  All three strings appear verbatim in the footnote above (Round-3 R3A-01/R3B-01 fix: closing sentence reworded so "positive pole" trails the literal phrase).

- **Git tag command** (Round-3 R3C-09): immediately after pushing the P2 commit, the P2 author runs:
  ```bash
  git tag -a wz-boundary-positive-class-pinned <P2-commit-sha> -m 'Pin positive_class=象征性/应用场景 to Stata encoding'
  git push origin wz-boundary-positive-class-pinned
  ```
  Rollback step in §5.6 specifies the destructive tag-delete commands.

- **`_aggregate_track`** ([L773-940](../../pipeline/sentiment/tone_llms.py#L773-L940)) — two-step extension (Round-17 R17A-02):

  **Step A — store per-model innovation labels in `per_model_parsed`**: the existing parsing block at L868-885 appends valid locus labels to flat `innov_loci` and valid substantiveness labels to flat `innov_substs` lists but does NOT store per-model identity for those labels. Per-model *confidences* are stored at L887-898 as `{short}_innovation_substantiveness_confidence` / `{short}_innovation_locus_confidence`; the matching labels are not. P2 extends the parsing block to also write:
  - `per_model_parsed[f"{short}_innovation_locus"] = part` (canonical `底层技术` / `应用场景`, set inside the L874 acceptance branch) or `None` (else branch).
  - `per_model_parsed[f"{short}_innovation_substantiveness"] = tt_str` (set inside the L883 acceptance branch) or `None` (else).

  **Step B — compute per-model binary prob_score**: using the (label, confidence) pairs stored in Step A and `compute_prob_score_binary`, with positive_class `"象征性"` for substantiveness and `"应用场景"` for locus. NaN-safe `np.nanmean` across non-NaN per-model scores. Returns new fields `avg_subst_prob_score`, `avg_locus_prob_score`; if all per-model values are NaN, return NaN. P2 test 13 `test_per_model_innovation_labels_stored` (§5.3.5) enforces Step A's contract.

- **`main`** at [L1050](../../pipeline/sentiment/tone_llms.py#L1050): write 4 new article-level columns to the dataframe in the existing per-track collection block below `_aggregate_track` invocation.

#### 5.3.2 `news_process/pipeline/panel/encode.py`

- Extend bank-year aggregation at [L582-583](../../pipeline/panel/encode.py#L582-L583): emit 8 new panel columns (means + `_std`). `np.nanmean` and `np.nanstd(ddof=1)`. Zero-article cells NaN per [L1105](../../pipeline/panel/encode.py#L1105).

#### 5.3.3 `news_process/pipeline/panel/codebook.py`

- Add 8 `VariableMetadata` entries following [L305](../../pipeline/panel/codebook.py#L305). Formula text cites `compute_prob_score_binary` and the chosen `positive_class`.

#### 5.3.4 `news_process/pipeline/panel/stata_export.py`

- Add 8 entries to `HEURISTIC_LABELS` dict (insertion point after [L124](../../pipeline/panel/stata_export.py#L124), within the function `build_variable_labels` defined at L108).
- Add 8 column-name patterns to `core_patterns` in `assign_core_columns` ([L162-200](../../pipeline/panel/stata_export.py#L162-L200)) so they are tagged "core" under the 2048-var IC cap.
- `validate_stata_compat` ([L268-269](../../pipeline/panel/stata_export.py#L268-L269)) enforces `len(label.encode('utf-8')) ≤ 80` (BYTES per [L37](../../pipeline/panel/stata_export.py#L37)).

**Proposed labels** (em-dash U+2014 = 3 UTF-8 bytes; all bytes ≤ 80):

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

Byte counts verified empirically (Round 3 confirmation: `len(s.encode('utf-8'))` matches the table).

#### 5.3.5 `news_process/tests/test_compute_prob_score_binary.py` (new, items 1-12)

1. `test_positive_label_positive_class`: `("象征性", 1.0, "象征性") → (1.0, "P2_BIN")`.
2. `test_negative_label_positive_class`: `("实质性", 1.0, "象征性") → (0.0, "P2_BIN")`.
3. `test_mid_confidence_positive`: `("象征性", 0.5, "象征性") → (0.5, "P2_BIN")`.
4. `test_none_label`: `(None, 0.7, "象征性") → (NaN, "P3_BIN")`.
5. `test_invalid_label`: `("invalid", 0.7, "象征性") → (NaN, "P3_BIN")`.
6. `test_zero_confidence_positive`: `("象征性", 0.0, "象征性") → (1.0, "P3_BIN")`.
7. `test_zero_confidence_negative`: `("实质性", 0.0, "象征性") → (0.0, "P3_BIN")`.
8. `test_all_none_aggregation`: 5 (None, NaN, "象征性") tuples; `np.nanmean` → NaN, no error.
9. `test_mismatched_positive_class`: positive_class `"不存在"` → every input NaN.
10. `test_confidence_clamp_above_one`: `("象征性", 1.0001, "象征性") → (NaN, "P3_BIN")`.
11. `test_confidence_clamp_below_zero`: `("象征性", -0.0001, "象征性") → (NaN, "P3_BIN")`.
12. `test_three_class_compute_prob_score_unchanged_smoke` — **parametrized** for both P2 and P3 paths (Round-3 R3C-10 + Round-4 R4B-01 correction): for `("正面", 0.7)` assert P2 output `{prob_pos: 0.7, prob_neu: pytest.approx(0.15), prob_neg: pytest.approx(0.15), prob_score: 0.55, prob_source: "P2"}`; for `(None, 0.0)` assert P3 output `{prob_pos: 0.0, prob_neu: 1.0, prob_neg: 0.0, prob_score: 0.0, prob_source: "P3"}` (verified via `compute_prob_score(None, 0.0)` returning P3 because `c == 0` triggers the else-branch at tone_llms.py:757; `(None, 0.5)` is the wrong P3-trigger because c>0 → P2 with neutral cls).
13. `test_per_model_innovation_labels_stored` (Round-17 R17A-02): construct a mock `_aggregate_track` invocation with 3 models each returning JSON containing valid `innovation_locus` + `innovation_substantiveness` labels; assert the returned `per_model_parsed` dict contains both `{short}_innovation_locus` and `{short}_innovation_substantiveness` keys for each of the 3 models (6 new keys total); assert their values match the model-emitted labels (NOT the majority-voted aggregate). This enforces the parsing-block extension specified in §5.3.1 Step A.

#### 5.3.6 `news_process/tests/test_panel_binary_prob_columns.py` (new, items 1-5)

1. `test_wz_footnote_present` (Round-3 R3A-01/R3B-01/R3C-08): three independent `grep -F` checks on `wz_framework_boundary_justification.md` for the three verbatim strings enumerated in §5.3.1.
2. `test_eight_new_columns_present`: 8 new columns in `40_panel_yearly.parquet`.
3. `test_zero_article_bank_year_nan`: zero-article cell → all 8 NaN.
4. `test_positive_class_encoding_assertion` — **parametrized for both dims** (Round-4 R4C-02): case (a) `("象征性", 1.0)` for substantiveness → `avg_subst_prob_score_full == 1.0`; case (b) `("应用场景", 1.0)` for locus → `avg_locus_prob_score_full == 1.0`. Both sign-flip guards.
5. `test_golden_baseline_diff_scope` (Round-3 R3C-11 + Round-4 R4B-02/R4C-01): **exact integer equality** assertion: `n_added_21 == 4 and n_added_40 == 8 and n_added_51 == 8 and n_added_41 == 0 and other_stages_diff == 0`. Rationale: `41_panel_with_controls.parquet` exists in `data/processed/` (255 KB) and in `golden_panel_v0.json`, but has NO producer registered in `core/schemas.py::OUTPUT_REGISTRY` and no `to_parquet` / `save_dataset` writer for that filename anywhere in `news_process/pipeline/` (verified at v1.4 authoring). It is an orphan artifact from a defunct stage; P2 cannot propagate columns into it because no code rewrites it. The test asserts the 41 file is unchanged (count 0).

**P2 test delta: +18 (13 + 5; P2 total 18; was 17 in v1.14, +1 for test 13 `test_per_model_innovation_labels_stored` per Round-17 R17A-02).**

#### 5.3.7 `news_process/tests/fixtures/golden_panel_v0.json`

Regenerate via
`"F:/Anaconda3/python.exe" news_process/scripts/migrate/generate_golden_snapshot.py`.
Commit alongside P2 code changes.

### 5.4 Data Flow

```
LLM JSON per article × model
  → compute_prob_score_binary × 2 dims per model (positive_class 象征性 / 应用场景)
  → per-model prob_score (P2_BIN / P3_BIN)
  → np.nanmean → article-level avg_*_prob_score per track
  → 21_tone_llms.parquet: +4 article-level columns
  → encode.py bank-year np.nanmean + np.nanstd:
  → 40_panel_yearly.parquet: +8 panel columns
  → 51_panel_with_controls.parquet: +8 cols (inherited via pd.read_parquet at pipeline/falsification/controls.py:261; preserved through merge_to_panel left-join at pipeline/falsification/controls.py:568 — the merge itself only adds nf_* aggregates, but it does not strip upstream columns. Invocation site: pipeline/falsification/controls.py:1171 inside main() (controls.py:1152), between aggregate_non_fintech and export_results — NOT pipeline/panel/runner.py per R15B-01 correction)
  → codebook.xlsx, .dta export
```

**NOTE on 41_panel_with_controls.parquet** (Round-4 R4B-02/R4C-01 +
Round-5 R5C-03 + Round-6 R6C-01 fence-extraction): This file exists in
`data/processed/` as a stale artifact from a defunct stage; no current
pipeline code writes to it. The `golden_panel_v0.json` entry is
preserved for snapshot completeness but no propagation occurs. See
test 5 in §5.3.6 for the explicit `n_added_41 == 0` assertion.

**Orphan cleanup is OUT OF SCOPE** for P0/P1/P2 (removing the entry at
`scripts/migrate/generate_golden_snapshot.py:52` and the corresponding
key from `golden_panel_v0.json` is an unrelated pipeline-hygiene task;
folding it into this plan would conflate the golden diff scope). A
follow-up cleanup ticket should be tracked separately and is explicitly
deferred here.

### 5.5 Test Plan

- `pytest tests/test_compute_prob_score_binary.py -v` (12 tests).
- `pytest tests/test_panel_binary_prob_columns.py -v` (5 tests).
- `pytest tests/test_prob_score.py -v` (existing 3-class non-regression).
- `pytest tests/integration/test_panel_reproducibility.py -v`.
- `pytest` formula gate.
- Lint: ruff on touched / new files.

### 5.6 Risks and Rollback

| Risk | Mitigation |
|---|---|
| Golden diff affects unrelated stages | Test `test_golden_baseline_diff_scope` asserts exact integer counts per affected stage. |
| Positive-class encoding flipped silently | Test `test_positive_class_encoding_assertion`; verbatim footnote + 3-grep coupling test. |
| 3-class `compute_prob_score` regressed | Parametrized smoke test 12 covers both P2 and P3 paths; existing `tests/test_prob_score.py` must remain green. |
| All-NaN aggregation crashes | Test 8. |
| Out-of-domain confidence | Tests 10, 11. |
| Git tag references stale commit on revert | Rollback adds explicit tag-delete commands; see below. |

**Expected golden-snapshot diff scope**:
- `21_tone_llms.parquet`: +4 article-level entries.
- `40_panel_yearly.parquet`: +8 bank-year entries.
- `51_panel_with_controls.parquet`: +8 entries (inherited via `pd.read_parquet` at `pipeline/falsification/controls.py:261`; preserved through `merge_to_panel` left-join at `pipeline/falsification/controls.py:568`; invocation site `pipeline/falsification/controls.py:1171` inside `main()` (`controls.py:1152`) — NOT `pipeline/panel/runner.py:1171` per Round-15 R15B-01 correction; Round-12 R12C-01 attribution + Round-14 R14C-01 path qualifier + Round-15 R15B-01 invocation-site).
- `41_panel_with_controls.parquet`: NO change (orphan; no producer per Round-4 R4B-02/R4C-01).
- All other stages: no diff.

`test_golden_baseline_diff_scope` asserts these as exact integer equalities (Round-3 R3C-11).

**Rollback** (atomic): `git revert <commit>` reverts the code, the wz footnote, and the regenerated `tests/fixtures/golden_panel_v0.json`. Tag teardown (P2 author authorized; CLAUDE.md "destructive ops" rule applies):
```bash
git tag -d wz-boundary-positive-class-pinned
git push --delete origin wz-boundary-positive-class-pinned
```
Forward compatibility: extra columns are ignored by old code paths. P0 does NOT depend on P2.

At v1.3 authoring, `grep -rE 'avg_(subst|locus)_prob_score_' news_process/ papers/` returns 0 hits outside this plan and the audit log; no downstream artifact references the new columns yet.

### 5.7 Acceptance Criteria

- 8 new panel columns + 4 article-level columns present.
- `codebook.xlsx` documents all 8 with `positive_class` in formula text.
- `.dta` export includes all 8 with byte-valid labels per the §5.3.4 table.
- All 17 new tests pass.
- `tests/test_prob_score.py` remains green.
- `compute_prob_score` source unchanged (verified by `git diff` against the function).
- `wz_framework_boundary_justification.md` contains the 3 verbatim grep targets.
- Git tag `wz-boundary-positive-class-pinned` exists locally and pushed to origin.

## 6. Items NOT done

Enumerated in §2. The manuscript paper-draft gate (Round-2 R2A-04) is
removed in v1.3 (Round-3 R3A-03/R3C-02 scope creep): the discipline
rule "no paper drafts cite Panels E/F by content until data-path
acceptance" is documented in §8 as a process guideline, not an enforced
CI gate.

## 7. Execution sequence and dependencies

```
P1 (inter-track κ stage)  ← no schema change, smallest blast radius
    ↓
P2 (binary prob_score)    ← golden baseline regenerated; +12 cols (4 article + 8 panel × multiple propagation)
    ↓
P0 (eval 4-task refactor) ← largest refactor; isolated to validation/
```

**Independence vs reversibility — precise statements**:

- **P1**: fully reversible at any time. Stata template `20_tableA1_inter_track_kappa.do.tmpl` is self-contained.
- **P2**: reversible while no downstream artifact references the new columns. At v1.3 authoring, `grep -rE 'avg_(subst|locus)_prob_score_' news_process/ papers/` returns zero hits outside this plan and the audit log. Once a paper draft or replication pack cites these columns, P2 revert requires updating that artifact AND the destructive tag teardown.
- **P0**: fully reversible at any time.

All three are independent of `calibration_plan_v5.1` G1 unblock for code landing.

## 8. End-to-end acceptance

**Numeric gate** (formula): `pytest` collected count satisfies
`count == 1153 + Σ(delta_P0, delta_P1, delta_P2)` per declared deltas
(§3.5 = 17, §4.5 = 10, §5.5 = 18; sum 45; target 1198 after v1.15).
The gate is the formula, not the constant. The v1.15 increment from
44 → 45 reflects the new P2 test 13 (`test_per_model_innovation_labels_stored`)
added by Round-17 R17A-02.

**File-existence gates** (all 3 commits in):

`news_process/data/processed/eval_reports/`:
- Code-path: `inter_track_kappa_table.csv`, `.tex`; `classification_eval_table.tex` with `Panel E` + `Panel F` literals.
- Data-path (deferred): `cm_innovation_substantiveness_llm_{full,ctx}.png`, `cm_innovation_locus_llm_{full,ctx}.png`, `per_model_innovation_substantiveness_comparison.csv`, `per_model_innovation_locus_comparison.csv`, populated Panels E/F.

`news_process/data/processed/`:
- `40_panel_yearly.parquet`: 8 new columns.
- `codebook.xlsx`: 8 new VariableMetadata entries.
- `*.dta`: 8 new vars with byte-valid labels.

**Paper-draft discipline rule** (replaces former gate; Round-3 R3A-03/R3C-02): Paper drafts cite Panels E/F by content (numbers, conclusions) ONLY after data-path acceptance holds. This is a discipline rule enforced through review of paper PRs, NOT an automated CI gate. The original aspirational `manuscript_gates.py` is dropped.

## 9. Out-of-band requirements satisfied

- **Git commit protocol**: each work item a separate commit, HEREDOC body, trailer exactly `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` (Round-3 R3C-14; do not substitute a different model identity).
- **Shim invariant**: only `39a_inter_track_kappa.py` adds a shim; ≤30 lines.
- **DAG consistency**: P1 registers in `STAGES_VALIDATION` + `EXPECTED_NO_OUTPUT_STAGES` (with `.py` suffix) + `test_dag_consistency.py:98` count update (atomic single commit).
- **Config-split conformance**: NO new YAML keys. Schema constants in `news_process/validation/manual_validation_schema.py` (same package as `llms_evaluation.py`; Round-3 R3A-04/R3C-12 location fix).
- **Ruff conformance**: lint commands per §3.5, §4.5, §5.5.
- **Pre-registration integrity**: P2 positive_class is downstream encoding only. `unified_cot.txt v7` (tag `prompt-v7-released`) unchanged. Verbatim footnote committed to `wz_framework_boundary_justification.md`; falsifiable by 3 grep targets in test 1 of §5.3.6. Tag `wz-boundary-positive-class-pinned` created post-P2-commit.

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

(None as of v1.3.)

## 12. Audit history

See [three_dim_borrowing_execution_plan_audit_log.md](three_dim_borrowing_execution_plan_audit_log.md).
