# Execution Plan — Table A8 Title-Track Fixes: Item 3 (llm_peer estimator) & Item 4 (strategic_diff no-op)

> Status: **v2.0 (2026-05-31)** — rewritten after a 4-lens adversarial audit of v1.0
> (6 P0 + 11 P1 findings). v1.0 verdict was NEEDS REWORK; this version bakes in
> findings F1–F15. Authored after live code + data verification.
> Scope: two confirmed defects in the `_title` Tier-B robustness track (Table A8).
> Constraints: disk-freeze discipline, $0 incremental LLM, golden-snapshot
> discipline, Stata 19+ only, shims frozen (logic in `pipeline/` / `papers/`).

> **v1.0 → v2.0 correction log (audit-driven):**
> - **Item 3 was mis-framed.** The actual 2SLS (`llm_peer/11_table2_main_iv_2sls.do.tmpl:51`)
>   is `ivreghdfe ROA (llm_vote_tone_full = llm_peer_tone_iv_full)`: `llm_vote_tone_full`
>   is the **endogenous regressor of interest**, `llm_peer_tone_iv_full` is its
>   **instrument**. So the template's `MAIN_TREAT=llm_vote_tone_full` is the
>   economically-correct variable. Item 3 is **"right variable, OLS not 2SLS"**,
>   NOT "wrong variable." (F3)
> - `llm_peer_tone_loo_*` (spec `iv.primary`) is a **phantom column** built nowhere. (F3)
> - There is **no DAG stage 48**; `compute_llm_peer_iv` is inline step 7h-llmpeer in
>   `pipeline/panel/runner.py:1260`. (F3)
> - The 9 templates are **structurally divergent**; the v1.0 "edit root + append-only
>   propagation" mechanism cannot work. (F1)
> - On the live panel the first crash is at **Panel C's reghdfe** (MAIN_TREAT/ROA
>   absent), BEFORE esttab. (F2)
> - Fully-clean Panel-A coverage is **1 of 9** (P1 only), not 2. (F4)
> - brokerage's genuine **IV-title is a free $0 win** (both columns already exist). (F10)

---

## 0. Verified root causes (evidence, not assertion)

Confirmed against live code and `data/processed/40_panel_yearly.parquet`
(174×1997, mtime 2026-05-30 22:52).

### Item 4 — `strategic_diff`: degenerate no-op (the more dangerous, simplest to fix)

- Template derives the title variant by suffix substitution
  (`25_tableA8_title_robustness.do.tmpl:37-38`):
  `subinstr(MAIN_TREAT,"_ctx","_title")` then `subinstr(...,"_full","_title")`.
- `strategic_diff` main treatment = `strat_diff_n5` (`paper_spec.yaml:28`;
  `derivative_replication.py:138`) — **no `_full`/`_ctx` suffix** → both `subinstr`
  are no-ops → `title_var == strat_diff_n5 == MAIN_TREAT`.
- `strat_diff_n5` exists on the panel; `strat_diff_n5_title` does **not** (no
  `strat_diff*_title` column exists).
- Consequence: Panel A's `capture confirm variable` guard **passes** → Panel A
  silently runs `reghdfe ROA strat_diff_n5 ...` = the **main regression**,
  mislabeled as title robustness. Panel B regresses the same var twice.
- **Stata-19 behavior (F11):** this does NOT error — `reghdfe DV M M` → "omitted
  for collinearity" (rc=0); `test M = M` → "constraint dropped" (rc=0, r(p)=.).
  So it produces a *plausible-but-meaningless* panel — worse than a clean skip.

### Item 3 — `llm_peer`: title robustness uses OLS, not the paper's 2SLS (CORRECTED framing)

- **Actual headline identification** (`llm_peer/11_table2_main_iv_2sls.do.tmpl:51`):
  `ivreghdfe ROA_w (llm_vote_tone_full = llm_peer_tone_iv_full)` + controls + FE.
  - **Endogenous regressor (coefficient = the paper's headline causal estimate):**
    `llm_vote_tone_full` (the bank's own LLM-vote tone).
  - **Excluded instrument:** `llm_peer_tone_iv_full` (leave-one-out mean of peers'
    `llm_vote_tone_full`; peers identified by LLM, Cao et al. 2025 RAS).
- Table A8 `MAIN_TREAT = llm_vote_tone_full` (`derivative_replication.py:155`) →
  `title_var = llm_vote_tone_title` (exists) → Panel A = `reghdfe ROA
  llm_vote_tone_title` = **the correct variable, but OLS** (drops the IV).
- **Defect (corrected):** estimator mismatch (OLS vs the paper's 2SLS), *not*
  "wrong variable." This is the **same class as brokerage** (OLS-on-endogenous
  title var).
- **Two separate spec-integrity bugs surfaced:**
  - `paper_spec.yaml:27 treatment.primary = llm_peer_tone_iv_full` **mislabels the
    instrument as the treatment** (the true 2nd-stage regressor is
    `llm_vote_tone_full`).
  - `paper_spec.yaml:39 iv.primary = llm_peer_tone_loo_full` is a **phantom** —
    `llm_peer_tone_loo_*` is built nowhere (`llm_peer_iv.py` emits only
    `llm_peer_tone_iv_full` + cutoff variants; 0 panel matches for `*_loo*`).

### Adjacent facts that shape scope (all verified live)

| Fact | Evidence | Implication |
|---|---|---|
| P1 uses the **root** template, `MAIN_TREAT=llm_vote_tone_ctx` | `stata_runner.py:241` | `title_var=llm_vote_tone_title ≠ MAIN_TREAT`, exists → item-4 guard safe; P1 is the **only fully-clean** Panel A (OLS main + OLS title) |
| brokerage main = `peer_tone_lag1_full` (endogenous), IV = `peer_tone_2nd_lag1_full` | `derivative_replication.py:114-122`; `brokerage/11_table2:31` | Panel A runs OLS on `peer_tone_lag1_title`; **both** `peer_tone_lag1_title` AND `peer_tone_2nd_lag1_title` exist on panel → a genuine **$0 IV-title is buildable NOW** |
| On the live panel, **ROA + all 4 absent-paper MAIN_TREATs are missing** | Stata run of `46_panel_yearly_full.dta`: ROA, attention_index_full, innovation_substantiveness_full, locus_layer_full, innovation_collab_mode_full all absent | Panel C reghdfe (references `{{MAIN_TREAT}}`/`{{MAIN_DV}}`, gated only on `tone_gap_title_full`:80) **r(111)-crashes before esttab** for those papers |
| `esttab name1 name2 name3` errors r(111) if any name unstored | verified live | dynamic esttab needed — but **secondary** to the Panel-C crash |
| All 7 derivative + bs masters call `capture do 25_*.do`; only root/P1 uses plain `do` | grep of `00_master.do.tmpl` | master.do **does not abort** for skip-papers; the `.tex` is simply not written. The "master breaks" rationale in v1.0 was wrong (F12) |
| `bank_fintech_collab` is **NOT** in `_DERIVATIVE_PAPER_IDS` (7 IDs) | `derivative_replication.py:42-60` | collab template is patched on disk but **cannot be instantiated/smoke-tested**; verification covers only attention/substance/locus (F7) |
| 8 copies of `25_tableA8` (root 8246 B; 7 paper copies ~5.2–5.8 KB) + `26_bs` | glob + byte-diff | **structurally divergent**: root has separate Panel A & B blocks; the 7 copies + bs **merge** A+B into one `if !_rc` block, with per-paper addnotes, `$data_dir` fallback, and bs uses `bs_m_*` estimate names (F1, F6) |
| Live panel already has `frac_title_mentions_fintech` / `frac_title_long` / `tone_gap_title_full` (~117–118 non-null) | column scan | Panels C/D/E now **run** (not "graceful-skip"); docs (`title_track_as_robustness.md §7.3`) are stale (F15) |

---

## 1. Scope and non-goals

**In scope**
- (S1) Item 4: stop `strategic_diff` emitting a degenerate Panel A/B; clean N/A.
- (S2) Generalize: `title_applicable` guard for any suffix-less `MAIN_TREAT`
  (currently only `strategic_diff`) **plus** gate every reghdfe (A/B/**C**/D/E) on
  `MAIN_TREAT`/`MAIN_DV` existence so absent-column papers don't r(111)-crash, **plus**
  dynamic `esttab` (scoped to the 3 A/B/C estimates).
- (S3) Item 3 Tier-1 (no panel change): (a) build brokerage's **genuine IV-title**
  ($0, columns exist); (b) make llm_peer's Panel A honest about OLS-vs-2SLS
  (retitle/caveat or unwire); (c) **fix the two spec-integrity bugs**.
- (S4) Item 3 Tier-2 (deferred, panel-gated, $0-LLM-conditional): build
  `llm_peer_tone_iv_title` (LOO mean of `llm_vote_tone_title` over the cached peer
  map) → a true 2SLS title robustness for llm_peer.

**Non-goals**
- No production panel re-run in Tier-1.
- No new LLM API calls anywhere.
- No fix to the broader "derivative-paper main columns absent from the live panel"
  state (that is the production-run's job; here we only make the templates
  crash-safe and honest).

---

## 2. Item 4 + generic template hardening (do first; cheapest, highest safety)

### 2.1 Three interdependent Stata-level changes (MUST ship together — F11)

**(a) `title_applicable` guard.** After the two `subinstr` lines:
```stata
local title_applicable = ("`title_var'" != "{{MAIN_TREAT}}")
if !`title_applicable' display "  [WARN] {{MAIN_TREAT}} has no _full/_ctx suffix; no _title variant -> Panels A/B N/A."
```
Gate Panel A and **Panel B** on `` `title_applicable' & !_rc `` (v1.0 gated only A — F11/stata).

**(b) Gate every reghdfe on MAIN_TREAT/MAIN_DV existence (NEW — fixes F2).**
Wrap Panel C (and A/B/D/E) so they only run when the regressors exist:
```stata
capture confirm variable {{MAIN_DV}}
local has_dv = !_rc
capture confirm variable {{MAIN_TREAT}}
local has_treat = !_rc
```
and require `` `has_dv' & `has_treat' `` on Panels C/D/E (which reference
`{{MAIN_DV}}`/`{{MAIN_TREAT}}`). Without this, attention/substance/locus
r(111)-crash at Panel C **before** esttab on the current panel.

**(c) Dynamic, scoped `esttab` (F5).** Accumulate ONLY the three rendered
estimates — never the Panel D/E models (which are intentionally not tabulated):
```stata
* append after each of the THREE renders only:
*   Panel A -> local a8_models "`a8_models' m_title_only"
*   Panel B -> local a8_models "`a8_models' m_main_plus_title"
*   Panel C -> local a8_models "`a8_models' m_with_gap"
if "`a8_models'" != "" {
    esttab `a8_models' using "$tables_dir/tableA8_title_robustness.tex", ...
}
else {
    display "  [WARN] Table A8: no estimable panel; writing stub .tex for LaTeX \input."
    file open _stub using "$tables_dir/tableA8_title_robustness.tex", write replace
    file write _stub "% Table A8 N/A for {{PAPER_ID}}." _n
    file close _stub
}
```
> Rationale clarified (F12): the `if "\`a8_models'" != ""` guard prevents the
> **Stata-chain** r(111); the `.tex` stub is only for a downstream LaTeX `\input`
> (Stata/master never reads the `.tex`; derivative masters use `capture do` and do
> not abort anyway). Keep `mtitles` = the existing 3 titles so layout is unchanged.

### 2.2 Files & propagation mechanism (REWRITTEN — F1, F6)

The 9 templates are **structurally divergent**, so v1.0's "edit root + append-only
propagation" is invalid. Required approach:
- **Per-file in-place block edits** (not whole-file copy). Two structural variants:
  - **Root** (`25_tableA8...tmpl`, used by P1): separate Panel A (50-58) + Panel B
    (64-74) blocks.
  - **7 paper copies + `26_bs`**: merged Panel A+B in one `if !_rc {...}` block,
    per-paper addnotes, `$data_dir` fallback `../data`, and **`26_bs` uses
    `bs_m_title_only/bs_m_main_plus_title/bs_m_with_gap`** + `bs_title_robustness.tex`.
- Either (a) hand-edit all 9 files with copy-specific anchors, or (b) write a
  **new structure-aware** migration script that branches on root-vs-merged layout,
  inserts (a)/(b) guards after `subinstr`, gates each reghdfe, and rewrites each
  file's own `esttab` line **preserving** per-paper estimate-name prefixes
  (`bs_m_*`), addnotes, `.tex` targets. The cited `v3_7_4_append_panel_de.py` is
  append-only and is **not** a usable model for this.
- **Preserve header invariant (F8):** lines 1-17 (`'v3.7.3'` lineage string +
  Heston/Loughran anchor) MUST survive — `test_paper_spec_tA8_filled.py:137-143`
  asserts them in every template.

### 2.3 Decision D1 (see §5): keep tA8 wired for strategic_diff (clean N/A for A/B;
C/D/E retitled — see F-academic) vs unwire. **Recommendation: keep wired + clean
N/A for A/B, and RETITLE the table** away from "Headline-Only **Sentiment**
Robustness" because `strat_diff_n5` is a text-**distinctness** measure, not
sentiment; Panels C/D/E for it are generic environment/sub-sample robustness, not
sentiment-robustness-of-the-main-treatment (academic auditor).

### 2.4 Tests (fast, no Stata)
- `test_stata_templates.py` (or a new `test_tableA8_render.py`): assert each
  instantiated copy contains the `title_applicable` guard, the per-reghdfe
  `has_dv`/`has_treat` gating, and the `if "\`a8_models'" != ""` block; assert
  `a8_models` references exactly the 3 A/B/C names (`bs_m_*` for bs).
- Assert strategic_diff render's `title_var` resolves to `strat_diff_n5` and that
  **no** `eststo m_title_only` / `test strat_diff_n5 = strat_diff_n5` line is
  reachable (suppression test, not just guard-presence — F-completeness).
- Assert all 9 templates retain `'v3.7.3'` + Heston/Loughran (F8).
- `test_derivative_replication.py`: packages still instantiate placeholder-clean.

### 2.5 Verification (manual, local StataNow 19.5/MP — outside CI)
- Build a **fixture panel that includes ROA + the paper's MAIN_TREAT** (the live
  panel lacks them; F2), then run strategic_diff + attention/substance/locus
  `25_*.do` end-to-end. Confirm: no Panel-C r(111) crash; A/B emit N/A or skip;
  stub `.tex` written; `master.do` (capture do) completes.
- **collab is excluded** from end-to-end verification (not buildable — F7).

---

## 3. Item 3 fix — `llm_peer` + brokerage (CORRECTED)

### 3.1 Tier-1 — now, NO panel change

**(a) brokerage — genuine IV-title, FREE $0 win (F10).** Both
`peer_tone_lag1_title` and its instrument `peer_tone_2nd_lag1_title` exist on the
panel. Add a paper-specific `brokerage_network/25b_tableA8_iv_title.do.tmpl`:
`ivreghdfe {{MAIN_DV}} (peer_tone_lag1_title = peer_tone_2nd_lag1_title) $bank_controls,
absorb(...) cluster(prov_id)`. This is a *causal* title robustness, no panel change.

**(b) llm_peer — honesty fix.** Its instrument's title variant
(`llm_peer_tone_iv_title`) does **not** exist, so a true 2SLS title is not
buildable now (→ Tier-2). For the interim, Panel A's `reghdfe ROA
llm_vote_tone_title` tests the **correct** endogenous variable but as **OLS**.
Decision D3 (see §5):
- **1a' (disclose):** keep the OLS Panel A but (i) **retitle/move** it out of
  "Headline-Only Sentiment Robustness" into an explicit "firm-tone headline
  (OLS reduced-form) supplementary", and (ii) caveat that the IV (2SLS) title
  robustness is deferred (Tier-2). The variable is correct, so this is more
  defensible than v1.0 assumed — BUT a bare caveat under the existing title is
  the weakest option (academic auditor F9); the **retitle** is required.
- **1b' (unwire/N/A):** set `llm_peer` `tables.tA8.template: null` until Tier-2.
- **Recommendation: 1a' with retitle** (the OLS reduced-form on the right variable
  carries real interim information; the estimator gap is disclosed).

**(c) Fix spec-integrity bugs (F3).** In `papers/llm_peer/paper_spec.yaml`:
reconcile `treatment.primary` (currently names the instrument
`llm_peer_tone_iv_full`; the true 2nd-stage regressor is `llm_vote_tone_full`) and
`iv.primary` (currently the phantom `llm_peer_tone_loo_full`; the real instrument is
`llm_peer_tone_iv_full`). This is a dangling-pointer reproducibility bug
independent of Table A8 and should be fixed regardless.

**Tier-1 tests:** extend `test_paper_spec_tA8_filled.py` for the llm_peer
retitle/caveat keys and the corrected spec fields; add a brokerage IV-title
render test.

### 3.2 Tier-2 — deferred, panel-gated, $0-LLM-conditional (REWRITTEN — F3, F13)

Goal: a genuine 2SLS title robustness for llm_peer.
1. **`pipeline/panel/llm_peer_iv.py`**: add a second pass that reuses the **cached
   peer map** (served from `_llm_cache.db` via `LLMCache`, keyed on
   `PEER_PROMPT_VERSION='v1-2026-05-13'`) and averages `llm_vote_tone_title`
   (t−1, leave-one-out) → emit **one** new column `llm_peer_tone_iv_title`. There is
   **no `_loo` column** (phantom); do not build one. The 2SLS becomes
   `(llm_vote_tone_title = llm_peer_tone_iv_title)`.
2. **No "stage 48"**: `compute_llm_peer_iv` is **inline step 7h-llmpeer** in
   `pipeline/panel/runner.py:1260` — not a DAG stage, no shim, no
   `OUTPUT_REGISTRY` entry. The new column surfaces only via a **full panel encode
   re-run** (the build path that writes `40_panel_yearly.parquet`), which triggers
   **golden-snapshot regen** and is M0-gated. Update `stata_export.py` core/aux
   patterns for the new column (lands in aux; core stays ≤2048).
3. **New template** `llm_peer/25b_tableA8_iv_title.do.tmpl`: `ivreghdfe {{MAIN_DV}}
   (llm_vote_tone_title = llm_peer_tone_iv_title) $bank_controls, ...`.
4. **$0-LLM is real but conditional**: holds only if `_llm_cache.db` is preserved
   and `PEER_PROMPT_VERSION` unchanged (peer identification served from cache, tone
   averaging is pure pandas). Note `_save/_load_peer_cache` in `llm_peer_iv.py` are
   dead code; the live cache is `LLMCache`.
5. **Count-test bump (F14)**: any new `25b_*.tmpl` breaks hardcoded counts —
   `test_papers_b_route.py` (104), `test_stata_replication_matrix.py:42`,
   `test_stata_templates.py:294-296`. Bump them as part of Tier-2.

---

## 4. Sequencing, dependencies, rollback

```
Step 1 (Item 4 + generic hardening): per-file in-place edits to 9 templates
        (title_applicable guard + per-reghdfe MAIN gating + scoped dynamic esttab)
        → fast tests.  [no panel change, no LLM]
Step 2 (Item 3 Tier-1): brokerage IV-title template ($0, columns exist)
        + llm_peer retitle/caveat + llm_peer spec-integrity fix → fast tests.
Step 3 (docs): sync title_track_as_robustness.md (§7.3 D/E now RUN, not skip),
        report v2.6, CLAUDE.md coverage → "1 of 9 fully clean".
Step 4 (Tier-2, DEFERRED, M0-gated): llm_peer_tone_iv_title in runner step 7h
        + 2SLS template + panel encode re-run + golden regen + count-test bump.
```
- Steps 1–3 non-breaking, $0, no panel change → one PR.
- Step 4 gated, lands with the next production batch.
- **Rollback**: Steps 1–3 are template/spec/doc text only → `git revert` the PR; no
  data artifact changes, no golden rollback.

---

## 5. Open decisions (require user input before execution)

| ID | Decision | Options | Recommendation |
|---|---|---|---|
| **D1** | strategic_diff Item-4 | (a) keep tA8 wired, A/B clean-N/A, **retitle** C/D/E as generic robustness; (b) unwire | **(a)** — keeps valid generic Panels; retitle removes the "sentiment" misframe |
| **D2** | Item-3 timing | (a) Tier-1 now (brokerage IV-title + llm_peer disclose + spec fix) + Tier-2 deferred; (b) Tier-1 only | **(a)** |
| **D3** | llm_peer Tier-1 form | (a') keep OLS Panel A but **retitle** as firm-tone OLS reduced-form supplementary + disclose IV deferred; (b') unwire/N/A | **(a')** — variable is correct; disclose the estimator gap |
| **D4** | brokerage | (a) build genuine IV-title NOW ($0, columns exist); (b) caveat only | **(a)** — it is a free causal title robustness |

---

## 6. Effort & risk (revised up from v1.0)

| Item | Effort | Risk | LLM | Panel change |
|---|---|---|---|---|
| Item 4 + generic hardening (9 per-file edits + structure-aware migration + tests) | ~1–1.5 day | Low-Med (must not clobber per-paper esttab/addnotes; Panel-C gating new) | $0 | none |
| Item 3 Tier-1 (brokerage IV-title + llm_peer retitle + spec fix) | ~0.5 day | Low | $0 | none |
| Docs sync | ~0.25 day | Low | $0 | none |
| Item 3 Tier-2 (llm_peer IV-title) | ~2-3 day + **gated panel re-run + golden regen** | Med | $0* (*cache + prompt-version frozen) | yes (additive col) |

---

## 7. Acceptance criteria (Steps 1–3)

1. strategic_diff `25_*.do` no longer runs a `strat_diff_n5` regression labeled as
   title robustness; emits N/A; table retitled away from "sentiment".
2. attention/substance/locus `25_*.do` no longer r(111)-crash at **Panel C** or
   esttab when MAIN_TREAT/ROA are absent (verified on a fixture panel that includes
   them, plus the absent case). collab excluded (not buildable).
3. brokerage `25b_*.do` runs a genuine `ivreghdfe (peer_tone_lag1_title =
   peer_tone_2nd_lag1_title)` IV-title.
4. llm_peer Panel A retitled as a firm-tone OLS reduced-form supplementary +
   caveat; llm_peer `paper_spec.yaml` `treatment.primary`/`iv.primary`
   reconciled with the implemented identification.
5. Coverage statement reads **"1 of 9 fully clean (P1); brokerage + llm_peer =
   right variable but OLS-not-2SLS (brokerage now upgraded to IV-title); 5 skip; 1
   no-op (strategic_diff); collab deferred."**
6. All 9 templates retain `'v3.7.3'` + Heston/Loughran header; all fast tests green.
7. Docs corrected: Panel D/E **run** (columns present), not "graceful-skip until
   re-run".
8. No golden-snapshot regen (no panel column change in Steps 1–3).

---

## 8. Residual risk (unverifiable without a live Stata/MP run or production re-run)

All column-presence, template-structure, DAG, and spec facts were verified
statically and against the live parquet, but **Stata was not executed by the
plan author**. Open until a StataNow 19.5/MP run on a fixture panel **containing
MAIN_TREAT+MAIN_DV+ROA**: (1) the guard + per-reghdfe gating + scoped esttab emit
the stub and complete through `master.do` for strategic_diff and an absent-column
paper; (2) no remaining unguarded reghdfe (Panel D/E) r(111)-crashes on sparse
strata; (3) exact `esttab`/`mtitles` rendering. **Tier-2's $0-LLM** is unverifiable
until a gated encode confirms `_llm_cache.db` integrity + frozen `PEER_PROMPT_VERSION`
reproduce the peer map with zero API calls and that `llm_peer_tone_iv_title`
(expected sparse, like the ~19-row `llm_peer_tone_iv_full`) yields a non-degenerate
2SLS. The **brokerage IV-title (F10)** is the only Tier-2-class item buildable and
verifiable now without a panel re-run.
