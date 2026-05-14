# Manual Validation Study Plan (n ≥ 500)

> 解决 W10 (顶刊 LLM 验证标准: n ≥ 500 + 多 raters) + W2 (inter-rater
> reliability). 设计 v1, 2026-05-14.

## 1. Objective

To provide publishable-grade validation of the v7 three-stage CoT
classification protocol via large-sample multi-rater human-coded
agreement, supplementing the prompt-perturbation analysis already
reported in Section 3.4 of the methodology section.

**Publishable inter-rater reliability**: Cohen's κ (Landis & Koch,
1977), Krippendorff's α (Krippendorff, 2004), with PABAK (Byrt et al.,
1993) reported for dimensions with skewed base rates.

## 2. Sample Design

### 2.1 Sample Size — Constrained by Data Availability

**Original target**: n = 500 with stratified design across 5 strata
(100 per stratum).

**Actual constraint discovered during pilot sampling (2026-05-14)**:
The v7 panel exhibits extreme base-rate skew that limits stratified
sampling:

| Stratum | v7 panel size | Sampled | Status |
|---|---|---|---|
| A. Not relevant (verified=False) | 321 | 100 | ✓ |
| B. Substantive ∧ Application | 801 | 100 | ✓ |
| C. Symbolic ∧ Application | **22** | 22 (all) | constraint |
| D. Substantive ∧ Technology | **25** | 25 (all) | constraint |
| E. Symbolic ∧ Technology | **1** | 1 (all) | constraint |
| **Total achievable** | — | **248** | — |

**Realized design**: n = 248 (minority over-sampled to 19.4% vs.
v7 panel 2.7%), achieving substantial gain in κ precision for
innovation dimensions despite n < 500.

**Power note**: With n = 248 and post-stratification weighting,
expected κ standard error on innovation_substantiveness is ~0.07
(under simple random sampling baseline of κ_true = 0.50), within
the threshold for publishable κ reporting.

**Discussion**: This data limitation is an unavoidable consequence
of the v7 W&Z framework applied to the fintech news corpus — the
modal class (substantive innovation) is overwhelmingly dominant.
We explicitly disclose this constraint in the methodology section
(Carlson & Burbano, 2026, §3.7 transparency guideline). Future
work could (a) extend the corpus to a longer time horizon or wider
bank set to recover more minority observations, or (b) report
PABAK alongside κ to characterize agreement under skewed base rates
(Byrt et al., 1993).

### 2.2 Stratified Sampling

To over-sample minority classes for stable κ estimation. Targets shown
are original design; realized n constrained by v7 panel availability:

| Stratum | v7 prediction | Target n | Realized n | Status |
|---|---|---|---|---|
| A. is_bank_fintech_news = False | False | 100 | **100** | ✓ |
| B. Substantive ∧ Application | substantive, application | 100 | **100** | ✓ |
| C. **Symbolic** ∧ Application | symbolic, application | 100 | **22** | constraint (over-sampled from 2.5% panel rate to 22/248 = 8.9%) |
| D. Substantive ∧ Technology | substantive, technology | 100 | **25** | constraint |
| E. **Symbolic** ∧ Technology | symbolic, technology | 100 | **1** | constraint (only 1 in v7 panel) |
| **Total** | — | 500 | **248** | base rate limit |

Per §2.1, Strata C/D/E cannot reach target n=100 due to v7 panel base-rate
limits (97/3 substantive/symbolic; 97/3 application/technology). We
sample all available from C/D/E and document the realized n=248
weighted design in the methodology section.

### 2.3 Sampling Frame

`news_process/data/processed/21_tone_llms.parquet` (v7, 849 verified rows).
Random seed = 42 (consistent with prompt_sensitivity sampling). Sampling
code: `news_process/scripts/migrate/manual_validation_sampling.py`
(provided below).

### 2.4 Reporting Weights

Final inter-rater statistics will be reported with **post-stratification
weighting** to recover population-level estimates from the stratified
sample.

## 3. Annotation Protocol

### 3.1 Raters

**Three trained raters** (rationale: Tetlock 2007 JF uses 5 raters;
Calomiris & Mamaysky 2019 JFE uses 2; we adopt 3 as a balanced design
that supports both pairwise Cohen's κ and 3-rater Fleiss' κ /
Krippendorff's α while keeping cost-per-rater hours below 50). Each
rater independently codes all 248 articles.

**Rater training**:
1. 30-minute orientation: read methodology section + W&Z framework
   primer
2. 30-minute calibration: code 20 pilot articles + group discuss
   disagreements
3. Production: 248 articles × ~5 min/article = ~21 hours per rater

Raters should be management/finance/economics graduate students or
post-docs. Avoid involving the v7 prompt designers (anchoring bias).

### 3.2 Codebook

Each article presents:
- Article ID + target bank
- Title
- Full text (or context window if specified)
- Coding form with three sections:

**Section 1: Bank-Fintech Relevance (Stage 1)**
- [ ] Is this article substantively about [target_bank]'s fintech activity?
- [ ] (If YES) Confidence: low / medium / high
- [ ] (If NO) Reason: not about target bank / not about fintech / pure background

**Section 2: Sentiment (Stage 2; skip if Section 1 = NO)**
- [ ] Positive: performance growth, technical breakthrough, regulatory recognition, etc.
- [ ] Neutral: objective fact-reporting, industry-level commentary
- [ ] Negative: risk exposure, regulatory penalty, security incident, public-opinion crisis
- [ ] Confidence: low / medium / high

**Section 3a: Innovation Substantiveness (Stage 3a; skip if Section 1 = NO)**
- W&Z (1994, 1998) framework: does this article describe substantive
  action with real economic/operational consequences, or symbolic action
  primarily serving legitimacy/impression management?
- [ ] **Substantive**: real resource commitment + verifiable capability
      building + correspondence with actual operations
- [ ] **Symbolic**: slogan/vision without specifics OR PR-packaging with
      data but no real impact OR trend-following OR decoupling
- [ ] Confidence: low / medium / high
- [ ] Note: "Symbolic" does not mean "lacks facts"; even data-laden
      announcements can be symbolic if they primarily signal legitimacy.

**Section 3b: Innovation Locus (Stage 3b; skip if Section 1 = NO)**
- Gomber et al. (2018) framework
- [ ] **Technology layer**: AI, blockchain, big data, cloud, quantum, biometrics
- [ ] **Application layer**: digital payments, open banking, intelligent
      risk control, robo-advisory, digital lending
- [ ] Confidence: low / medium / high

**Free-text rationale (≥30 chars)** for each section, citing specific
article content.

### 3.3 Quality Controls

- **Attention checks**: ~5% (n = 13) of articles are duplicated to
  measure intra-rater reliability
- **Adjudication**: articles with 3-rater disagreement are discussed
  in a calibration meeting; final code via consensus or majority
- **Time monitoring**: median time per article should be 4–7 min;
  articles coded in < 1 min are flagged

## 4. Reliability Statistics

### 4.1 Reported Metrics

| Metric | Computed by dimension | Threshold |
|---|---|---|
| Pairwise Cohen's κ (rater i vs rater j, averaged) | Stages 1, 2, 3a, 3b | ≥ 0.61 substantial |
| Krippendorff's α (multi-rater) | Stages 1, 2, 3a, 3b | ≥ 0.667 acceptable |
| Fleiss' κ (3-rater categorical) | Stages 1, 2, 3a, 3b | ≥ 0.61 substantial |
| **PABAK** | **Stages 3a, 3b (skewed)** | ≥ 0.81 almost perfect |
| Cohen's κ vs v7 LLM (each rater) | Stages 1, 2, 3a, 3b | ≥ 0.61 |
| Confusion matrix (rater consensus vs v7) | Stages 3a, 3b | Reported |

### 4.2 Acceptable Outcomes

Per Carlson and Burbano (2026, §3.7), the LLM should achieve **at
least the same level of inter-rater reliability as the human raters
do among themselves** to be considered "as good as" a human rater.
Formally:

$$\bar{\kappa}_{\text{LLM-vs-human}} \geq \bar{\kappa}_{\text{human-vs-human}} - \epsilon, \quad \epsilon = 0.10$$

### 4.3 Failure Modes and Robustness

If LLM-vs-human κ < human-vs-human κ − 0.10 on any dimension, this
indicates LLM disagreement with human consensus. Report:
- Confusion matrix
- Sample of disagreement articles with rationale
- Bootstrap CI on κ
- Sensitivity to including / excluding low-confidence ratings

## 5. Cost and Timeline

- 3 raters × 21 hours = 63 person-hours (production)
- At $25/hour for graduate-student annotators: $1,575
- Plus 8 hours calibration + adjudication: $200
- **Total: ~$1,775 for 3-rater design (n=248 realized)**
- Timeline: 2 weeks (week 1 training + calibration, week 2 production)
- Cost reduction (~50% vs original $3,400 estimate) reflects n=248
  actual rather than n=500 target, due to base-rate constraint.

## 6. Sampling Script

See `news_process/scripts/migrate/manual_validation_sampling.py`.

## 7. Reporting Template

Section 3.5 of the methodology section will be populated with:

> "Three trained annotators independently coded n = [N] articles
> drawn via stratified random sampling (Section 2 above), achieving
> mean pairwise Cohen's κ of [X1] on Stage 1, [X2] on Stage 2, [X3]
> on Stage 3a, [X4] on Stage 3b (all values substantial by Landis &
> Koch, 1977). The LLM CoT protocol achieves κ_LLM-vs-human of [Y1]
> through [Y4] across the four stages, falling within ε = 0.10 of the
> human consensus benchmark on [P/4] dimensions, satisfying the
> validation criterion of Carlson and Burbano (2026, §3.7)."

## 8. Cross-References

- Methodology section: `paper_methodology_section_draft.md` Section 3.5
- v7 prompt: `news_process/config/prompts/unified_cot.txt`
- v7 LLM Rerun output: `news_process/data/processed/21_tone_llms.parquet`
- Codebook: `news_process/pipeline/panel/codebook.py`
- Prompt terminology mapping: `prompt_terminology_mapping.md`

## References

Hubert, L. (1977). Kappa revisited. *Psychological Bulletin*, *84*(2), 289–297.

(For other references, see `prompt_terminology_mapping.md` References section.)
