# Title Track (`_title`) as Tier-B Robustness Specification — v3.7.3

> **Status**: v3.7.3 Plan A v1.0 (2026-05-26)
> **Scope**: 9 papers (P1-P5 + brokerage_network + llm_peer + strategic_diff + benefit_society)
> **Compatibility**: maintains v3.5.1 R3-H1 exclusion of A1/A3 on `_title`
> **Anchor**: Heston-Sinha (2017 *FAJ*); LM (2016 *JAR* survey); Boudoukh (2019 *JFE*); Campbell-Fiske (1959) MTMM
> **Implementation**: paper_spec.yaml `tables.tA8.template` (8 papers) + paper-specific extension key `title_robustness_table` (benefit_society)

---

## §1 Decision Summary

The `_title` text slice track has historically existed as an **audit-only** track:
sentiment panels (LLM / dictionary / BERT) compute `_title`-suffixed columns
(~410 columns in `40_panel_yearly.parquet` per empirical scan 2026-05-26),
but **no paper has used these columns as a main treatment or formal robustness
specification** in the 11-paper portfolio.

**v3.7.3 promotes `_title` from audit-only → Tier-B supplementary robustness**
for 9 of the 11 papers (P10/P11 deferred to v3.7.4 pending paper-spec stabilization).
The promotion is implemented via:

1. **`tables.tA8.template` slot** filled in 8 paper_spec.yaml files (P1-P5 + brokerage_network + llm_peer + strategic_diff) — each pointing to a Stata `.do.tmpl` template that runs Table A8.
2. **`title_robustness_table` paper-specific extension** in benefit_society (its `tables.tA8` slot is already occupied by `19_bs_num_intensity_robustness` from v3.5.1 A3 — execution-period v1.0.1 correction).
3. **stage 39g (`track_discriminant_validity.py`)** new validation audit producing HTMT 3×3 matrix across `_full` / `_ctx` / `_title` tracks for each tested sentiment indicator (LLM tone / dict tone / BERT pos).
4. **NEW-B1 mojibake sanity test** (`tests/integration/test_panel_no_mojibake.py`) detecting panel column-name encoding pollution discovered during execution-period verification.

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
| Boudoukh-Feldman-Kogan-Richardson (2019) | *JFE* | Headline-based identification §III + headline sentiment as robustness §IV.B |
| Bybee-Kelly-Manela-Xiu (2024) | *RFS* | WSJ full-text main; headline subset as robustness |

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
| BERT pos/neg (5 BERT) | ✅ Computed | Table A8 Panel A/B (per-paper choice) |
| A1 mean_clarity_score | ❌ Excluded (R3-H1) | Not used |
| A3 mean_num_intensity | ❌ Excluded (R3-H1) | Not used |
| `tone_gap_title_full` (Engelberg gap) | ✅ Pre-computed (panel) | Table A8 Panel C control |

This binary compatibility (sentiment-yes / lexical-no) follows directly from
the underlying methodological premise: sentiment classifiers are designed for
short text; lexical density measures are not.

---

## §4 Acceptance Criteria

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

## §5 Audit Response Template (for peer review)

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
> *JFE*). Our main findings are qualitatively unchanged. As a supplementary
> diagnostic, we report a joint specification (Main + Title) with a Wald
> test of coefficient equality to assess informational redundancy, and a
> specification adding the title-body sentiment gap (Engelberg, 2008,
> hard-soft asymmetry framework) as a control."

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

**Overall verdict**: `pass_title_discriminant` — `_title` track discriminates
from `_full`/`_ctx` per Henseler et al. (2015) strict cutoff 0.85 on both
pairs involving `_title`. HTMT(full, ctx) = 0.965 exceeds strict cutoff as
mathematically expected (`_ctx` is the entity-proximity sub-window of `_full`;
Hassan et al. 2019 *QJE* design self-correlation, not a discriminant failure).

This empirically supports v3.7.3 Plan A v1.0's methodological claim:
`_title` is a non-redundant measurement specification.

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

- **v3.7.4 candidate**: extend to P10 (`bank_media_disagreement`) and P11
  (`bank_news_clarity`) once paper-spec stabilizes (P10 SSRN-route + P11 G3
  unlock conditional on coauthor governance).
- **stage 39g production deployment**: HTMT 3×3 default-enabled (matching
  39d/39e/39f pattern); first empirical result documented above.

---

## §8 References

- Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? *JF*, 59(3), 1259-1294.
- Barber, B. M., & Odean, T. (2008). All that glitters. *RFS*, 21(2), 785-818.
- Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2019). Information, trading, and volatility. *JFE*, 133(1), 85-104.
- Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and business cycles. *RFS*, forthcoming.
- Campbell, D. T., & Fiske, D. W. (1959). Convergent and discriminant validation by the multitrait-multimethod matrix. *Psychological Bulletin*, 56(2), 81-105.
- Chen, H., De, P., Hu, Y., & Hwang, B.-H. (2014). Wisdom of crowds. *RFS*, 27(5), 1367-1403.
- Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *JF*, 66(5), 1461-1499.
- Engelberg, J. (2008). Costly information processing: Evidence from earnings announcements. Working paper.
- Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media. *JF*, 66(1), 67-97.
- Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? *Econometrica*, 78(1), 35-71.
- Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk. *QJE*, 134(4), 2135-2202.
- Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). A new criterion for assessing discriminant validity. *JAMS*, 43(1), 115-135.
- Heston, S. L., & Sinha, N. R. (2017). News vs. sentiment. *FAJ*, 73(3), 67-83.
- Hillert, A., Jacobs, H., & Müller, S. (2014). Media makes momentum. *RFS*, 27(12), 3467-3501.
- Hirshleifer, D., Lim, S. S., & Teoh, S. H. (2009). Driven to distraction. *JF*, 64(5), 2289-2325.
- Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. *JAR*, 54(4), 1187-1230.
- Mullainathan, S., & Shleifer, A. (2005). The market for news. *AER*, 95(4), 1031-1053.
- Tetlock, P. C. (2011). All the news that's fit to reprint. *RFS*, 24(5), 1481-1512.

---

**Document version**: v1.0 (2026-05-26, plan A execution-period v1.0.1 reflected)
**Authored alongside**: stage 39g implementation, 9 paper_spec.yaml updates, 9 Stata templates.
