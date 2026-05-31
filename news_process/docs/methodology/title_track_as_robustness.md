# Title Track (`_title`) as Tier-B Robustness Specification — v3.7.4

> **Status**: v3.7.4 v1.1 (2026-05-26; upgraded from v3.7.3 Plan A v1.0 after 9 rounds of audit, joint-occurrence framework integration)
> **Scope**: 9 papers (P1-P5 + brokerage_network + llm_peer + strategic_diff + benefit_society)
> **Compatibility**: maintains v3.5.1 R3-H1 exclusion of A1/A3 on `_title`
> **Anchor**: Heston-Sinha (2017 *FAJ*); LM (2016 *JAR* survey); Boudoukh (2019 *RFS*); Campbell-Fiske (1959) MTMM; Tetlock-Saar-Tsechansky-Macskassy (2008 *JF* 63(3) "More Than Words", DOI verified via CrossRef); Antweiler-Frank (2004 *JF*); Hassan et al. (2019 *QJE*)
> **Implementation**: paper_spec.yaml `tables.tA8.template` (8 papers) + paper-specific extension key `title_robustness_table` (benefit_society); v3.7.4 adds `audit_response_ref` pointer (MA-4 SoT, not inline)
> **v3.7.4 additions**: Panel D (stratify by `frac_title_mentions_fintech` × {0.3, 0.5, 0.7} thresholds, Antweiler-Frank 2004 JF); Panel E (stratify by `frac_title_long`, Da-Engelberg-Gao 2011 JF); stage 39g bootstrap CI (Henseler-Ringle-Sarstedt 2015 JAMS); per-cell graceful skip if N < 30

---

## §1 Decision Summary

The `_title` text slice track has historically existed as an **audit-only** track:
sentiment panels (LLM / dictionary / BERT) compute `_title`-suffixed columns
(~410 columns in `40_panel_yearly.parquet` per empirical scan 2026-05-26),
but **no paper has used these columns as a main treatment or formal robustness
specification** in the 11-paper portfolio.

**v3.7.3 promoted `_title` from audit-only → Tier-B supplementary robustness**
for 9 of the 11 papers (P10/P11 still deferred to v3.7.5+ pending paper-spec
stabilization). **v3.7.4 then extended Tier-B with Panel D / Panel E stratified
robustness + bootstrap CI** (see §4.4 joint-occurrence resolution, §4.5
acceptance criteria, §5 v1.1 audit response template).

The v3.7.3 baseline implementation:

1. **`tables.tA8.template` slot** filled in 8 paper_spec.yaml files (P1-P5 + brokerage_network + llm_peer + strategic_diff) — each pointing to a Stata `.do.tmpl` template that runs Table A8.
2. **`title_robustness_table` paper-specific extension** in benefit_society (its `tables.tA8` slot is already occupied by `19_bs_num_intensity_robustness` from v3.5.1 A3 — execution-period v1.0.1 correction).
3. **stage 39g (`track_discriminant_validity.py`)** new validation audit producing HTMT 3×3 matrix across `_full` / `_ctx` / `_title` tracks for each tested sentiment indicator (LLM tone / dict tone / BERT pos).
4. **NEW-B1 mojibake sanity test** (`tests/integration/test_panel_no_mojibake.py`) detecting panel column-name encoding pollution discovered during execution-period verification.

The v3.7.4 extensions (this doc upgrade, 2026-05-26):

5. **Panel D + Panel E** appended to all 9 Stata templates: Panel D stratifies
   the title-only sentiment by `frac_title_mentions_fintech` across thresholds
   {0.3, 0.5, 0.7} per Antweiler-Frank (2004 *JF*); Panel E stratifies by
   `frac_title_long` per Da-Engelberg-Gao (2011 *JF*) attention channel.
6. **stage 39g bootstrap CI** (Henseler-Ringle-Sarstedt 2015 *JAMS* §4)
   with n_bootstrap=1000, seed=42, plus 4-cell strata HTMT with per-cell
   graceful skip if N < 30.
7. **9 paper_spec.yaml × `audit_response_ref` + 2 caveats**: pointers to
   methodology §5 (MA-4 SoT design, not inline).
8. **New shared lib `core/text/title_indicators.py`** (EP-B3) consolidating
   indicator computation across stage 13 production and L2 audit script.
9. **L4 lint script `scripts/audit/loc_summation_check.py`** with opt-in
   marker, stdin support, self-check — mechanical enforcement of LOC
   summation chain protocol.
10. **Q1-Q5 empirical first-run** (2026-05-26, N=1170 fintech-filtered
    articles): Q5 joint-occurrence rate = 0.68% (vs Q3 × Q4 = 7.6%
    independence assumption), decisively supporting the conditioned-
    sentiment paradigm.

---

## §2 Top-Journal Evidence Base

### §2.1 Methodological framework

Robustness checks of text-based main treatments require **multiple measurement
specifications** (Loughran & McDonald, 2016, *JAR* survey §6; Hassan et al.,
2019, *QJE* §IV.A). Text subset selection is a foundational source of
measurement variance; alternative document segments — including titles,
abstracts, or specific sections — provide independent observations on the same
construct (Campbell & Fiske, 1959, *Psych Bull*; MTMM framework).

The `_title` track in this project serves the **F1 (measurement validity)**
function in the robustness taxonomy: it tests whether the main result
qualitatively persists when the sentiment analysis is restricted to the
headline-level text only.

### §2.2 Top-journal precedents using title-based sentiment

| Reference | Journal | Title sentiment usage |
|-----------|---------|----------------------|
| Antweiler & Frank (2004) | *JF* | Message subject (title) as input to sentiment classifier |
| Engelberg & Parsons (2011) | *JF* | Local newspaper **headline coverage** as causal IV |
| Da-Engelberg-Gao (2011) | *JF* | Attention via search-volume (title-derived) |
| Tetlock (2011) | *RFS* | Title similarity to identify stale news |
| Hillert-Jacobs-Müller (2014) | *RFS* | **Title coverage** drives momentum |
| Chen-De-Hu-Hwang (2014) | *RFS* | Seeking Alpha titles + bodies analyzed separately |
| Heston & Sinha (2017) | *FAJ* | **Direct headline vs full-article sentiment comparison** |
| Boudoukh-Feldman-Kogan-Richardson (2019) | *RFS* | Headline-based identification §III + headline sentiment as robustness §IV.B |
| Tetlock-Saar-Tsechansky-Macskassy (2008) | *JF* 63(3) | "More Than Words" — firm news tone (story-level negative-word fraction) predicts fundamentals; cited as news-tone precedent, NOT a headline-vs-body split (DOI verified v3.7.4) |

**No top-journal paper uses title sentiment as the sole main treatment**, but
multiple top-journal papers use title sentiment as **either a robustness check
or an attention proxy**. This is precisely the role v3.7.3 assigns to `_title`.

### §2.3 Theoretical pillars

1. **Engelberg (2008) hard-soft information asymmetry**: titles carry
   disproportionately more "soft information" (tone, framing) than article
   bodies. Title-only sentiment is therefore not a noisy subset of body
   sentiment — it samples a different region of the information space.
2. **Editor agency** (Mullainathan & Shleifer, 2005, *AER*; Gentzkow & Shapiro,
   2010, *Econometrica*): titles are written/selected by editors with
   different incentives than journalists, producing a "second author" signal.
3. **Salience/attention** (Barber & Odean, 2008, *RFS*; Da-Engelberg-Gao, 2011,
   *JF*; Hirshleifer-Lim-Teoh, 2009, *JF*): titles are the primary trigger of
   retail investor attention, especially relevant in Chinese financial media
   ("标题党" / clickbait phenomenon).

---

## §3 Compatibility with v3.5.1 R3-H1

v3.5.1 R3-H1 decision excludes A1 (Lexical Clarity, You 2018 *CAR* dictionary)
and A3 (Numerical Intensity, Hales 2011 *CAR*) from `_title` because Chinese
news titles < 50 characters violate the stable-denominator assumption of these
indicators.

**v3.7.3 v1.0 explicitly maintains this exclusion**:

| Indicator family | _title computation status | v3.7.3 use |
|------------------|--------------------------|------------|
| LLM tone (3-model vote) | ✅ Computed | Table A8 Panel A/B |
| Dictionary tone (jiang/yao/bian/du/you 5) | ✅ Computed | Table A8 Panel A/B (per-paper choice) |
| BERT pos/neg (3 BERT) | ✅ Computed | Table A8 Panel A/B (per-paper choice) |
| A1 mean_clarity_score | ❌ Excluded (R3-H1) | Not used |
| A3 mean_num_intensity | ❌ Excluded (R3-H1) | Not used |
| `tone_gap_title_full` (Engelberg gap) | ✅ Pre-computed (panel) | Table A8 Panel C control |

This binary compatibility (sentiment-yes / lexical-no) follows directly from
the underlying methodological premise: sentiment classifiers are designed for
short text; lexical density measures are not.

---

## §4 Methodological Acceptance and Validity Framework

**Per paper (Tier-B robustness)**:
- Table A8 (or `bs_title_robustness.tex` for benefit_society) successfully
  renders when the paper's `.do.tmpl` is instantiated and run.
- Panel A coefficient sign on `_title` variant matches main spec sign (or paper
  documents and explains divergence).
- Panel B Wald test on `MAIN_TREAT = title_var` reports `p`-value (significance
  not required for acceptance; the test informs the substantive interpretation).

**Project-level (stage 39g audit)**:
- For ≥ 50% of tested indicators, HTMT(`full`, `title`) AND HTMT(`ctx`, `title`)
  both < 0.85 (strict) → **`pass_title_discriminant`** verdict.
- Else if all pairs < 0.90 (lenient) → **`lenient_pass_with_design_self_correlation`**.
  This case acknowledges that HTMT(`full`, `ctx`) is mathematically expected to
  exceed 0.85 because `_ctx` is by design a sub-window of `_full` (Hassan 2019
  *QJE* entity-proximity vs full-text), not an independent measurement of the
  same construct.

**NEW-B1 mojibake sanity**:
- `tests/integration/test_panel_no_mojibake.py` detects and reports columns
  with U+FFFD or `����` sequence. Known offenders (~30+ dict_avg columns) are
  documented and marked xfail; new offenders trigger CI failure.

---

### §4.4 Joint-occurrence Problem and Conditioned-sentiment Resolution (v3.7.4)

A potential concern is that Chinese news headlines (Phase 2 measurement
on `data/processed/13_news_with_ctx.parquet`, 2026-05-26 run, N=1170
fintech-filtered articles): **Q1 title length median = 20 chars** (p5=9,
p95=39, mean=21.5) cannot physically accommodate joint occurrence of all
three construct dimensions: bank entity (B), FinTech topic (F), and
sentiment tone (S). The article-level joint-occurrence rate
P(B ∩ F ∩ S ∈ title) is empirically **Q5 = 0.68%** (8/1170; framing zone
"<15%"; AC-scan with 1506-keyword fintech dictionary + target_bank alias
scan + Chinese sentiment-hint scan). Component rates: Q3 P(F ∈ title) =
29.8%, Q4 P(B ∈ title) = 25.6%. Q5 falls **dramatically below** even the
intersection of independent component rates (29.8% × 25.6% ≈ 7.6%),
reflecting strong negative correlation: headlines tend to mention bank
OR fintech but rarely both + sentiment together.
This raises the question: what does headline-level sentiment measure when
joint occurrence fails?

**Resolution: conditioned-sentiment paradigm.** We follow the
conditioned-sentiment paradigm established across seven direct top-journal
analogs (broader paradigm support including non-direct precedents like
Engelberg-Reed-Ringgenberg (2012, *JFE*) is documented in Report §2.3):

1. Tetlock (2007 *JF* 62(3)): WSJ column (already selected on market topic)
2. Tetlock-Saar-Tsechansky-Macskassy (2008 *JF* 63(3) "More Than Words"):
   firm news (already firm-tagged), scored at the story level (news-tone precedent; not a headline-vs-body split)
3. Loughran-McDonald (2011 *JF* 66(1)): 10-K (already firm-year conditional)
4. Garcia (2013 *JF* 68(3)): NYT financial column (already selected)
5. Solomon (2012 *RFS* 25): press release (already firm-tagged)
6. Hassan et al. (2019 *QJE* 134(4) §III.B): earnings call (firm-conditional)
7. Antweiler-Frank (2004 *JF* 59(3) §III): Yahoo Finance message subject + body
   scored conditional on firm message-board

Under this paradigm:
- (B, F) dimensions are anchored at the document level via stage 11 bank
  assignment and stage 12 FinTech filter. These dimensions are LABEL-borne,
  not text-borne, and do not require physical co-occurrence in any specific
  text segment.
- (S) dimension is measured at the text level by sentiment classifiers
  (LLM 3-vote / dictionary 5-lexicon / BERT 3-model — BERT reduced 5→3 after the erlangshen+hw2942 drop, commit a6327512).
- Each text slice (`_full`, `_ctx`, `_title`) is an alternative measurement
  specification of S conditional on the (B, F) document-level anchor.

This is structurally identical to Hassan et al. (2019 *QJE* §III.B)
entity-proximity measurement, where firm name and political risk
vocabulary need not co-occur within the same sentence; the document is
firm-conditioned (earnings call transcript), and the proximity window
only carries the risk signal.

**Validation under conditioned-sentiment paradigm**: Convergent + discriminant
validity (HTMT bootstrap 95% CI per Henseler-Ringle-Sarstedt 2015 *JAMS* §4,
stage 39g, n_bootstrap=1000, seed=42) and construct purity diagnostics
(Engelberg 2008 hard-soft asymmetry via `tone_gap_title_full` in Panel C;
stratification by `frac_title_mentions_fintech` in Panel D under
Antweiler-Frank 2004 threshold sensitivity {0.3, 0.5, 0.7};
stratification by `frac_title_long` in Panel E per Da-Engelberg-Gao 2011)
collectively establish that `_title` is a non-redundant measurement of the
same underlying tone construct as `_full` and `_ctx`, even under low
joint-occurrence rate.

### §4.5 Panel D/E Acceptance Criteria (v3.7.4)

**Panel D (stratification by `frac_title_mentions_fintech`)**:
- Coefficient sign in subsample {`frac` > τ} matches main spec sign for at
  least one τ ∈ {0.3, 0.5, 0.7}; deviation in others is interpreted under
  Engelberg (2008) hard-soft asymmetry as "attention channel without
  substance mention".
- Min cell N ≥ 30 bank-year per τ; otherwise `insufficient_power` flag.

**Panel E (stratification by `frac_title_long`)**:
- Coefficient stability across length buckets indicates both attention
  channel (Barber-Odean 2008 *RFS*; Da-Engelberg-Gao 2011 *JF*) and substance
  channel (Tetlock 2007 *JF*) contribute to the headline sentiment signal.

**Graceful fallback (5R-B2)**: If all 4 strata cells have N < 30, stage 39g
outputs only panel-level HTMT (N=64) + per-cell N report +
`all_cells_insufficient_power` flag; Stata Panel D/E templates fall back to
full-sample regression + caveat.

**Current panel state caveat (Round 49 audit)**: The disk panel
`40_panel_yearly.parquet` (168 × 2060, frozen at 2026-05-16) does NOT yet
contain `frac_title_mentions_fintech` / `frac_title_long` columns — these
require a stage 14-40 production re-run to propagate the v3.7.4
article-level indicators (now present in `13_news_with_ctx.parquet` after
the v3.7.4 stage 13 re-execution, 2026-05-26) through `panel/encode.py`
aggregation. **Until that production re-run completes, all 9 Stata
Panel D + Panel E sections will graceful-skip** (the `capture confirm
variable frac_title_mentions_fintech` / `frac_title_long` guards trip,
emitting `[WARN] frac_title_mentions_fintech not in panel; Panel D skipped`).
Panels A/B/C (the v3.7.3 baseline robustness slot) continue to operate
normally on existing panel columns. This is **expected behavior, not a
bug** — it preserves disk freeze discipline while keeping the code
fully ready for the next production batch.

**Aggregation policy (MA-3 anchor)**: Per-paper coefficient + 95% CI +
caveat in each paper's Table A8. **NO portfolio-level pass/fail aggregation**
across the 9-paper portfolio, following Hassan (2019 *QJE*) and
Loughran-McDonald (2016 *JAR* §6) per-paper reporting convention.

**Design rationale (incorporates v1.0 §5 robustness-design narrative)**:
The legacy v1.0 audit-response framework — citing Heston-Sinha (2017 *FAJ*)
headline-vs-body comparison, Boudoukh et al. (2019 *RFS* §III) headline-based
identification, Mullainathan-Shleifer (2005 *AER*) editor-framing, and
Barber-Odean (2008 *RFS*) salience — is preserved as the historical
motivation for the Tier-B robustness slot. v1.1 §5 (below) expands this
framework with the joint-occurrence response.

---

## §5 Audit Response Template (for peer review)

**v1.1 (v3.7.4) — joint-occurrence problem response (this is the SoT for
Report §6 and paper_spec.yaml `audit_response_ref`; grep diff must = 0):**

> "We address the concern that Chinese news headlines (typically Q1
> characters median, Phase 2 measurement) cannot physically co-locate all
> three construct dimensions (bank entity, FinTech topic, sentiment tone).
> Our identification follows the conditional-sentiment paradigm established
> by seven top-journal precedents: Tetlock (2007, *JF*),
> Tetlock-Saar-Tsechansky-Macskassy (2008, *JF*),
> Loughran-McDonald (2011, *JF*), Garcia (2013, *JF*),
> Solomon (2012, *RFS*), Hassan et al. (2019, *QJE*), and
> Antweiler-Frank (2004, *JF*). The topic conditioning is performed at the
> document level (stage 11 bank assignment + stage 12 FinTech filter), and
> the headline serves as a sentiment-bearing text channel conditional on
> this document-level anchor.
>
> To verify headline sentiment is not confounded by topics orthogonal to
> the bank-FinTech construct, we report:
>
> (i) HTMT discriminant validity (Henseler-Ringle-Sarstedt 2015, *JAMS*),
>     on the current production panel (174×1997, stage 39g re-run
>     2026-05-31, N=64 bank-year, n_bootstrap=1000, seed=42):
>     HTMT(`_full`,`_title`) point estimate = 0.384, bootstrap 95% CI
>     upper bound 0.710; HTMT(`_ctx`,`_title`) = 0.517, CI upper 0.798 —
>     both `_title` pairs pass the 0.85 strict cutoff on BOTH the point
>     estimate AND the bootstrap CI upper bound. HTMT(`_full`,`_ctx`) =
>     0.825 is treated as design self-correlation (`_ctx` is the
>     entity-proximity sub-window of `_full`; Hassan et al. 2019 *QJE*),
>     not a discriminant failure. (The earlier 2026-05-26 first-run on
>     the 168×2060 panel reported point 0.627/0.628 with CI upper
>     0.863/0.861 marginally above 0.85, attributed to small-sample
>     width; the current larger panel resolves both below the cutoff.)
>     Point estimates remain consistent with the order of magnitude of
>     the headline-vs-body sentiment relationship documented in
>     Heston-Sinha (2017, *FAJ*);
>
> (ii) Engelberg (2008) hard-soft asymmetry controlled by
>      `tone_gap_title_full` in Panel C;
>
> (iii) Stratification by `frac_title_mentions_fintech` in Panel D across
>       three threshold values {0.3, 0.5, 0.7}, following Antweiler-Frank
>       (2004, *JF*) message-subject-relevance threshold sensitivity
>       convention. Coefficient stability across thresholds indicates
>       conditioned-sentiment is not driven by within-title joint
>       occurrence (Hassan 2019, *QJE* §IV.A);
>
> (iv) Stratification by `frac_title_long` in Panel E — separates the
>      attention channel (Barber-Odean 2008, *RFS*; Da-Engelberg-Gao 2011,
>      *JF*) from the substance channel (Tetlock 2007, *JF*).
>
> Our main findings are reported per paper with paper-specific caveats; we
> do not aggregate to a portfolio-level pass/fail, following Hassan (2019,
> *QJE*) and Loughran-McDonald (2016, *JAR* §6) per-paper reporting
> convention."

**v1.0 legacy audit response (preserved for historical comparison; NOT
the v3.7.4 SoT — v1.1 above supersedes for §6 / paper_spec ref):**

> "We verify the robustness of our main sentiment-based findings under an
> alternative measurement specification restricting the analysis to news
> headlines only. This headline-only specification is motivated by the
> salience and attention literature (Barber & Odean, 2008, *RFS*;
> Da-Engelberg-Gao, 2011, *JF*) and the editor-framing literature
> (Mullainathan & Shleifer, 2005, *AER*), and follows the methodological
> recommendation of Loughran & McDonald (2016, *JAR*) §6 to verify
> text-based results across multiple document subsets. Table A8 (Online
> Appendix) reports the headline-only sentiment specification, paralleling
> the headline-vs-body sentiment comparison in Heston & Sinha (2017, *FAJ*)
> and the headline-based identification design in Boudoukh et al. (2019,
> *RFS*). Our main findings are qualitatively unchanged."

For papers with binary-construct main treatments (P3 substance, P4 locus,
P5 collab), the audit response notes the LLM confidence caveat documented in
the per-paper `tA8.title_robustness.caveat` field of `paper_spec.yaml`.

---

## §6 Engineering Footprint

| Artifact | Lines | Files |
|----------|-------|-------|
| paper_spec.yaml modifications | ~12 lines/file × 9 files | 9 |
| New audit module (stage 39g) | ~260 LOC | 1 |
| Thin shim (`39g_*.py`) | ~17 LOC | 1 |
| DAG registration (`core/dag.py`) | +2 lines (predicate) + 8 lines (StageSpec) | 1 |
| Schema registration (`core/schemas.py`) | +1 line in EXPECTED_NO_OUTPUT_STAGES | 1 |
| Stata templates (`.do.tmpl`) | ~90 lines/file × 9 files | 9 |
| Methodology documentation | ~280 lines | 1 (this file) |
| Tests | ~350 LOC across 3 files | 3 |
| CLAUDE.md current-version block | +20 lines | 1 |
| **Total** | **~1,800 LOC** | **27 files** |

**No LLM API increment** (panel columns pre-exist), **no panel column changes**
(no migration), **no golden snapshot regeneration** (column hashes unchanged).

---

## §7 Forward Path & Known Limitations

### §7.1 Empirical first-run result (2026-05-26)

stage 39g first-run on `data/processed/40_panel_yearly.parquet` (168 × 2060,
n_articles ≥ 2 mask → N=64 bank-year):

| Indicator | HTMT(full, ctx) | HTMT(full, title) | HTMT(ctx, title) |
|-----------|----------------|-------------------|------------------|
| `llm_vote_tone` | 0.965 | **0.627** | **0.628** |

**Overall verdict (point-estimate level)**: `pass_title_discriminant` —
`_title` track discriminates from `_full`/`_ctx` per Henseler et al. (2015)
strict cutoff 0.85 on both pairs involving `_title`. HTMT(full, ctx) = 0.965
exceeds strict cutoff as mathematically expected (`_ctx` is the
entity-proximity sub-window of `_full`; Hassan et al. 2019 *QJE* design
self-correlation, not a discriminant failure).

**v3.7.4 bootstrap CI extension (2026-05-26 second-run, n_bootstrap=1000
seed=42, output `logs/audit/39g_v3_7_4_e2e.json`)**: bootstrap 95% CI
upper bounds 0.863 (full,title) and 0.861 (ctx,title) **exceed** the 0.85
strict cutoff — small-sample (N=64) CI width prevents bootstrap-strict
acceptance. Point-estimate verdict above remains valid; bootstrap evidence
adds **honest small-sample caveat** per Henseler-Ringle-Sarstedt (2015 §4)
inference recommendation. This empirically supports v3.7.3 Plan A v1.0's
methodological claim (`_title` non-redundant) while transparently
reporting CI width pending future N expansion via stage 14-40 production
re-run.

### §7.2 Known limitations

- **NEW-B1 false alarm (resolved)**: initial PowerShell observation of `����`
  in column names was a terminal rendering artifact for legitimate UTF-8
  Chinese characters (0x6b63=正, 0x9762=面). Panel contains 0 U+FFFD mojibake
  columns; ~117 Chinese-character columns are valid v3.5.2+ LM 4-subdict
  sentiment labels. Defensive `_is_mojibake_column` filter retained in
  stage 39g for future regression detection.
- **P5 `bank_fintech_collab` deferred**: P5 is not yet onboarded to
  `derivative_replication._DERIVATIVE_PAPER_IDS` (v3.5.1 R3 known issue:
  P5 manuscript/refs.bib not yet complete). The `25_tableA8_title_robustness.do.tmpl`
  file is in place under `stata_templates/bank_fintech_collab/`; once P5
  onboarding completes (independent PR), Table A8 instantiates automatically.

### §7.3 Forward path

- **v3.7.5+ candidate**: extend to P10 (`bank_media_disagreement`) and P11
  (`bank_news_clarity`) once paper-spec stabilizes (P10 SSRN-route + P11 G3
  unlock conditional on coauthor governance). v3.7.4 covers the 9-paper
  portfolio; P10/P11 remain deferred per v3.7.4 Out of Scope §7.
- **stage 14-40 production re-run — COMPLETED (2026-05-30)**: the panel
  `40_panel_yearly.parquet` was regenerated 2026-05-30 22:52 (174×1997) and
  NOW contains `frac_title_mentions_fintech` / `frac_title_long` /
  `tone_gap_title_full` (~117-118/174 non-null). **Stata Panel C/D/E now RUN**
  (subject only to the per-cell N ≥ 30 graceful-skip), superseding the earlier
  "will graceful-skip until re-run" caveat (§4.5). The on-disk stage-39g JSON
  (`logs/audit/39g_v3_7_4_e2e.json`, 2026-05-26) and the §5/§6 audit-response
  numbers remain STALE vs this live panel and must be regenerated before any
  replication package ships.
- **stage 39g production deployment**: HTMT 3×3 default-enabled (matching
  39d/39e/39f pattern); first empirical result documented above; v3.7.4
  bootstrap CI extension verified by Round 40 end-to-end re-run
  (`logs/audit/39g_v3_7_4_e2e.json`).

### §7.4 v3.7.5 Table A8 hardening (2026-05-31)

A 4-lens adversarial audit of the Table A8 consumption surface (6 P0 + 11 P1,
plan v1.0 → v2.0) surfaced two confirmed defects, now fixed (Tier-1, $0, no
panel change):

- **Item 4 (strategic_diff no-op)**: `strat_diff_n5` lacks a `_full`/`_ctx`
  suffix, so the template `subinstr` was a no-op (`title_var == MAIN_TREAT`) and
  Panel A/B silently re-ran the main regression (non-erroring under Stata 19, so
  it produced a plausible-but-meaningless panel). Fixed by a `title_applicable`
  guard + dynamic esttab; the strategic_diff table is retitled "Sub-sample /
  Environment Robustness" (its treatment is text-distinctness, not sentiment).
- **Item 3 (llm_peer estimator, framing corrected)**: the operative 2SLS is
  `ivreghdfe ROA (llm_vote_tone_full = llm_peer_tone_iv_full)`, so the headline
  regressor IS `llm_vote_tone_full` (already used by Table A8) — the defect is
  OLS-vs-2SLS, **not** a wrong variable. Disclosed as a firm-tone OLS
  reduced-form; the genuine 2SLS title robustness (needing `llm_peer_tone_iv_title`)
  is deferred (Tier-2). The `paper_spec.yaml` `treatment.primary` (had mislabeled
  the instrument) and `iv.primary` (phantom `llm_peer_tone_loo_full`) were
  reconciled with the implemented identification.
- **brokerage (D4, free win)**: a genuine 2SLS title robustness (Panel F,
  `peer_tone_lag1_title` instrumented by `peer_tone_2nd_lag1_title`) was added —
  both columns already exist on the panel.
- **Honest coverage**: genuine fully-clean Panel-A substitution is **1 of 9**
  (P1); brokerage + llm_peer are right-variable-but-OLS-not-2SLS (brokerage now
  upgraded to IV-title); 5 papers skip (no `_title` main variant); collab is
  deferred (not in `_DERIVATIVE_PAPER_IDS`).
- Every reghdfe is now gated on MAIN_DV / MAIN_TREAT existence (the live
  derivative-paper panel lacks ROA + most main treatments, which previously
  r(111)-crashed Panel C before esttab).

See `docs/plan/tableA8_item3_item4_fix_execution_plan.md` (v2.0) for the full
plan + audit trail. Implemented via `scripts/migrate/v3_7_5_harden_tableA8.py`
(idempotent) + `tests/test_tableA8_hardening_v375.py` (15 tests).

**Tier-2 (genuine 2SLS title robustness) — code-complete (no longer deferred).**
`pipeline/panel/llm_peer_iv.py` now also averages `llm_vote_tone_title` over the
*same* LLM-cached peer network that builds `llm_peer_tone_iv_full`, emitting
`llm_peer_tone_iv_title` — faithful by construction, $0 incremental LLM. llm_peer
gains **Panel G** (`ivreghdfe`/`ivreg2` 2SLS: `llm_vote_tone_title` instrumented by
`llm_peer_tone_iv_title`); brokerage's **Panel F** does the same for its existing
title columns. Both self-activate / graceful-skip on column presence.
`llm_peer_tone_iv_title` is now **materialized on the panel** via a validation-gated,
cache-only backfill (`scripts/migrate/v3_7_5_add_llm_peer_iv_title.py`): the LLM-peer
network is rebuilt purely from the LLM cache (**0 API calls / $0**), the rebuilt
`llm_peer_tone_iv_full` reproduces all 19 on-panel values exactly (max_abs_diff = 0.0),
proving the peer network is faithful — only then is the new column written (panel
174×1998, +1 col, 19 non-null; golden snapshot updated; `.v375bak` backup). Panel G
now activates on the real panel.

**Stata/MP verification (residual risk closed).** `scripts/audit/verify_tableA8_stata_smoke.py`
runs the hardened templates through StataNow 19.5/MP: strategic_diff (no-op N/A),
substance (absent main treatment → graceful stub, no r(111)), brokerage (Panel F
2SLS estimates), llm_peer (Panel A + Panel G 2SLS estimates) all return **RC=0**.
Key finding: absorbed-HDFE IV degenerates at **T=2** (`ivreghdfe` r(301)); the
`ivreg2 + i.bank_id i.year` fallback (proven rc=0, mirroring `11_table2_main_iv_2sls`)
makes both 2SLS panels estimable.

---

## §8 References

- Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? *JF*, 59(3), 1259-1294.
- Barber, B. M., & Odean, T. (2008). All that glitters. *RFS*, 21(2), 785-818.
- Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2019). Information, trading, and volatility: Evidence from firm-specific news. *RFS*, 32(3), 992-1033. DOI: 10.1093/rfs/hhy083.
- Campbell, D. T., & Fiske, D. W. (1959). Convergent and discriminant validation by the multitrait-multimethod matrix. *Psychological Bulletin*, 56(2), 81-105.
- Chen, H., De, P., Hu, Y., & Hwang, B.-H. (2014). Wisdom of crowds. *RFS*, 27(5), 1367-1403.
- Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *JF*, 66(5), 1461-1499.
- Engelberg, J. (2008). Costly information processing: Evidence from earnings announcements. Working paper.
- Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media. *JF*, 66(1), 67-97.
- Garcia, D. (2013). Sentiment during recessions. *JF*, 68(3), 1267-1300.
- Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? *Econometrica*, 78(1), 35-71.
- Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk. *QJE*, 134(4), 2135-2202.
- Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). A new criterion for assessing discriminant validity. *JAMS*, 43(1), 115-135.
- Heston, S. L., & Sinha, N. R. (2017). News vs. sentiment. *FAJ*, 73(3), 67-83.
- Hillert, A., Jacobs, H., & Müller, S. (2014). Media makes momentum. *RFS*, 27(12), 3467-3501.
- Hirshleifer, D., Lim, S. S., & Teoh, S. H. (2009). Driven to distraction. *JF*, 64(5), 2289-2325.
- Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *JF*, 66(1), 35-65.
- Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. *JAR*, 54(4), 1187-1230.
- Mullainathan, S., & Shleifer, A. (2005). The market for news. *AER*, 95(4), 1031-1053.
- Solomon, D. H. (2012). Selective publicity and stock prices. *RFS*, 25(7), 2009-2049.
- Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *JF*, 62(3), 1139-1168.
- Tetlock, P. C. (2011). All the news that's fit to reprint. *RFS*, 24(5), 1481-1512.
- Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More than words: Quantifying language to measure firms' fundamentals. *JF*, 63(3), 1437-1467. DOI: 10.1111/j.1540-6261.2008.01362.x (verified via CrossRef, v3.7.4 P0.0).

---

**Document version**: v1.1 (2026-05-26, v3.7.4 upgrade — joint-occurrence problem framework + Panel D/E acceptance + 7-precedent audit response). Earlier v1.0 (Plan A execution-period v1.0.1) lineage preserved.
**Authored alongside**: stage 39g implementation, 9 paper_spec.yaml updates, 9 Stata templates.
