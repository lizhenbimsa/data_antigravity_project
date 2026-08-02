# Independent R&D vs. External Collaboration: Open Innovation in Chinese Bank Fintech Strategy

**Paper ID**: `bank_fintech_collab` (P5)
**Status**: M3 skeleton (M0 G0 spec frozen 2026-05-17, manuscript implementation M5/M6)
**Master plan**: B_route_master_plan_v2 (内部规划文档; docs/ 目录已于 commit 1698bda5 整体删除, 无存留副本)

---

## Abstract

Should incumbent banks build fintech capabilities in-house or acquire them from outside? We encode the **organizational source** of Chinese commercial banks' fintech news coverage as a binary attribute — independent in-house R&D versus external collaboration (partnerships, licensing, M&A, strategic investment, open APIs, and industry alliances with fintech firms and tech giants) — and aggregate it to a bank-year external-collaboration news share, `collab_frac`, as the treatment variable, theoretically anchored to Chesbrough's (2003) Open Innovation framework and Laursen & Salter's (2006) search breadth–depth taxonomy. The corpus originates from a pre-filtering census of 18,198,978 media reports across 3,740 outlets (2007–2025); the production target corpus entering the pipeline adopts this full census scope — 18,198,978 media reports (2007–2025, T=19); this corpus then passes through the stage 13 bank–fintech co-occurrence hard filter (the post-filter retained article count is a production statistic; TODO: to be backfilled from the production run), and is aggregated into a bank-year panel of 110 Chinese commercial banks. Article-level classification is produced by majority vote across three large language models (gpt-5.4-nano, gemini-3.1-flash-lite, deepseek-v4-flash) at temperature=0 under a byte-frozen prompt v8, and is bitwise reproducible offline on full cache hits. The primary identification strategy is 2SLS with a same-type leave-one-out peer external-collaboration share instrument (a single confirmatory specification), complemented by a battery of mutually robust, co-equal, each just-identified parallel designs: a generalized Bartik instrument, three text tracks, and cross-vendor per-model classifications.

> TODO: Main result sentence (sign, magnitude, and significance of collab_frac → m_and_a_fintech) to be filled after production regressions.

> TODO: Mechanism and heterogeneity result sentences to be filled after production regressions.

Our contribution is to add the neglected binary dimension of *organizational source* to the fintech innovation literature, and to provide structural evidence of its marginal information content through an orthogonal 2³ = 8-cell saturated decomposition with the substantiveness (P3) and technology-locus (P4) dimensions from the same pipeline.

---

## 1. Introduction

Under digital disruption, incumbent banks face a real and unresolved strategic choice: confronted with fintech competition in technology and business models, should they build capabilities through internal R&D, or source them externally through partnerships, investments, and outright acquisitions (Vives, 2019)? In China this choice is especially acute: large banks have set up fintech subsidiaries and pursued in-house development, while loan facilitation, joint lending, open APIs, and strategic alliances have diffused widely among small and medium-sized banks. The media is a high-frequency information intermediary that records this strategic choice — every report of "Bank X signs a strategic cooperation agreement with fintech firm Y" or "Bank X launches an independently developed core system" is an observable disclosure of the organizational source of that bank's innovation.

Yet the existing empirical fintech-innovation literature characterizes bank innovation almost exclusively along single dimensions — quantity (patent counts, spending), quality (citation weighting), or technological locus — and neglects the **organizational source** of innovation: was it accomplished within the organizational boundary (closed), or across the boundary with external partners (open)? Open innovation theory has long argued that organizational source is a strategic dimension independent of quantity and quality (Chesbrough, 2003; Laursen & Salter, 2006), and Lerner, Seru, Short, & Sun (2024) show with US patent data that the internal versus external attribution of financial innovation output is both measurable and consequential in finance. For the setting of banks' fintech transformation, however, a large-sample, panel-structured, reproducible measure of organizational source is still missing.

We fill this gap with a text-as-data approach (Gentzkow, Kelly, & Taddy, 2019). Starting from a raw-corpus census of 18,198,978 media reports across 3,740 outlets (2007–2025; newspaper-type rows account for 92.93% of all rows), and take this full census as the production target corpus entering the pipeline — 18,198,978 media reports (2007–2025, T=19); this corpus subsequently passes through the stage 13 bank–fintech co-occurrence hard filter (the post-filter retained article count is a production statistic; TODO: to be backfilled from the production run). For every bank-fintech article that passes the verification gate, three large language models independently classify its organizational source under the Chesbrough framework (0 = independent R&D, 1 = external collaboration) and majority-vote to a consensus label, which we aggregate to a bank-year external-collaboration news share, `collab_frac`, for 110 Chinese commercial banks. The entire measurement pipeline runs at temperature=0 with seed=42 under a byte-frozen prompt v8 and is bitwise reproducible offline at zero cost on full cache hits — the measure itself satisfies reproducibility discipline (de Kok, 2025; Hansen & Kazinnik, 2023).

For identification, a bank-year's external-collaboration propensity is plainly endogenous to unobserved strategic preferences and investment opportunities. Our primary strategy is 2SLS with a same-type leave-one-out (LOO) peer external-collaboration share instrument: the average `collab_frac` of other banks of the same type (excluding the focal bank) instruments the focal bank's `collab_frac`. The motivation traces to the peer-effects literature (Manski, 1993; Bramoullé, Djebbari, & Fortin, 2009), the construction is isomorphic to the LOO peer instrument precedent in finance (Leary & Roberts, 2014), and we disclose the exclusion-restriction limitations candidly. The fallback instrument is a generalized Bartik shift-share construction (Borusyak, Hull, & Jaravel, 2025). All robustness ladders — the three text tracks, the three per-model LLM classifications, the two IV engines (LOO and Bartik) plus the lag1 predeterminedness variant — are mutually robust, co-equal parallel designs, each entering its own just-identified regression; they are never pooled into a single over-identified Hansen J test.

> TODO: Results preview paragraph (baseline 2SLS coefficient, economic magnitude, mechanism and heterogeneity summary) to be filled after production regressions.

> TODO: Event-study dynamic evidence sentences (E1 Yu'ebao launch 2013-06-13 / E3 asset-management regulation 2017-04-27 / E4 Ant IPO suspension 2020-11-03) to be filled after production regressions.

The differentiation boundary between this paper and the other papers from the same pipeline is sharp: P5 measures the **binary organizational source** of news announcements — it is not P1's continuous sentiment tone, not P2's attention exposure volume, not P3's substantiveness in the Westphal & Zajac (1994, 1998) sense, and not P4's Gomber technology locus. Organizational source is conceptually orthogonal to substantiveness and locus; crossing the three dimensions yields a 2³ = 8-cell saturated decomposition (§2.4 and Table 6), which serves both as structural evidence for this paper's marginal contribution and as a direct answer to the common concern that multiple papers slice the same corpus.

The remainder of the paper proceeds as follows: §2 develops the theoretical framework and hypotheses; §3 describes the corpus, measurement construction, and identification strategy; §4 reports the main empirical results; §5 presents the robustness architecture; §6 discusses mechanisms and implications; §7 concludes.

---

## 2. Theoretical Framework

### 2.1 Open Innovation (Chesbrough 2003)

Chesbrough's (2003) open innovation framework partitions the innovation process by the direction of knowledge flows into inbound (outside-in: licensing-in, technology acquisitions, joint R&D), outbound (inside-out: licensing-out, spin-offs), and coupled (alliances, co-creation platforms) modes. Its core proposition is that valuable ideas can and should flow across organizational boundaries, and that a purely internal, "closed" R&D paradigm systematically forgoes external opportunities in an environment of increasingly distributed knowledge. Two decades of accumulated evidence broadly support a robust association between openness and innovation performance, while emphasizing boundary conditions — returns depend on absorptive capacity, governance arrangements, and environmental dynamism (the meta-analysis of Zhang, Ma, Liang, & Garrett, 2024). Mapped to the bank-fintech setting: a bank's "external collaboration" announcements (partnerships, licensing, M&A, strategic investment, open APIs, industry alliances) correspond to inbound and coupled modes, while "independent R&D" announcements correspond to the closed internal-R&D path — this is the theoretical foundation of our binary encoding. Dehghani, Brauneis, & Karavidas (2026), studying IP management practices and open innovation across financial institutions, show that this lineage has moved squarely into the financial-institution context.

### 2.2 Search Breadth and Depth (Laursen & Salter 2006)

Laursen & Salter (2006) operationalize a firm's external knowledge-search strategy as breadth (the number of distinct external knowledge sources) and depth (the intensity of reliance on key sources), finding an inverted-U relationship with innovation performance — over-search brings attention dilution and integration costs. The taxonomy supports this paper in two ways. First, measurement: the bank-year external-collaboration news share `collab_frac` can be read as the media image of a bank's annual external-search intensity — a higher share of collaboration coverage indicates innovation activity that relies more on knowledge sources beyond the organizational boundary. Second, theory: the search-and-integration logic predicts that banks with high external-search intensity accumulate more private information about potential targets, partner quality, and integration difficulty — precisely the key inputs into acquisition decisions. Absorptive capacity theory (Cohen & Levinthal, 1990) further implies that prior collaborative experience itself raises the ability to recognize and integrate external knowledge, generating a cumulative path of "collaboration → stronger absorption → deeper collaboration (including M&A)."

### 2.3 Inter-firm R&D Partnerships and Acquisition-Mode Collaboration (Hagedoorn 2002)

Hagedoorn's (2002) systematic account of inter-firm R&D partnerships since 1960 shows that partnering arrangements lie on a continuum from loose contractual forms (joint R&D agreements, licensing) to tight equity-based forms (joint ventures, minority stakes, acquisitions), and that the rise of contractual arrangements in high-tech industries did not displace equity arrangements — the two more often form an escalation ladder in which contractual cooperation serves as the information-gathering and trust-building stage of equity deepening. Recent strategic-management evidence extends this ladder to the acquisition end: Burford, Shipilov, & Furr (2025) show that ecosystem synergies are important drivers of acquisitions — when complementarities between a focal firm and its ecosystem partners rise, acquisition becomes the means of internalizing synergy gains; Chen, Yang, & Wei (2025) show that alliance strategy and technology interdependence jointly shape the growth paths of ventures within ecosystems, with alliance-network position determining the reachability of deeper subsequent ties (including being acquired). The banking implication: banks with a higher external-collaboration propensity are more likely to move up the "cooperation → investment → acquisition" ladder, so their fintech M&A activity should be systematically more active. Bank-fintech M&A itself has become an emerging empirical literature — financial institutions' stock-price responses to fintech-acquisition announcements (Kueschnig & Schertler, 2024), the role of banks' business models in their fintech acquisitions (Alfhaili, Bakoush, & Wolfe, 2025), the link between fintech equity investment and bank innovation (Alfhaili, Bakoush, & Wolfe, 2026), banks' venture/minority-stake investments in fintech firms (Puri, Qian, & Zheng, 2024; evidence adjacent to but distinct from M&A, cited here only as a parallel reference), and the overall landscape of fintech mergers and acquisitions (Zheng & Mao, 2024) — but this literature starts from realized acquisition events and lacks the ex-ante external-collaboration propensity that this paper measures.

### 2.4 Orthogonality to P3 (substantiveness) and P4 (locus)

This paper's organizational-source dimension (independent R&D vs. external collaboration) is conceptually orthogonal to the substantiveness dimension of P3 (substantive vs. symbolic, in the Westphal & Zajac (1994, 1998) lineage) and the technology-locus dimension of P4 (underlying technology vs. application scenario, in the Gomber lineage): an announcement can be substantive and independently developed, or symbolic and externally collaborative — every combination of the three dimensions is meaningful. Crossing the three dimensions yields the complete enumeration of 2³ = 8 cells:

1. **Substantive × Tech × Independent** → genuine internal technological capability building (the internal-tech path, closest to the traditional bank-IT in-house paradigm);
2. **Substantive × Tech × External** → deep technology alliances / technology acquisitions (inbound open innovation acquiring core technology);
3. **Substantive × App × Independent** → internal business digitization (self-built channels and scenario applications);
4. **Substantive × App × External** → ecosystem collaboration (open APIs plus business-side co-creation, the canonical coupled mode);
5. **Symbolic × Tech × Independent** → technology-narrative packaging (claimed in-house core technology without implementation detail);
6. **Symbolic × Tech × External** → sign-and-stop technology cooperation (decoupling, extending Fiss & Zajac 2006);
7. **Symbolic × App × Independent** → marketing-style scenario disclosure (promotional application-side coverage);
8. **Symbolic × App × External** → strategic cooperation signed but not executed (symbolic alliance signaling).

If the organizational-source dimension carries no marginal information beyond P3/P4, then in a regression saturated with the 8-cell indicators, within-(subst, locus) differences across collab cells should be indistinguishable; the saturated decomposition of Table 6 (§4.4) tests exactly this.

### 2.5 Hypothesis Development

**H1 (main hypothesis, single confirmatory specification).** The search-and-integration logic of §2.2 and the alliance-to-acquisition ladder of §2.3 jointly point to the same prediction: banks with a higher external-collaboration propensity accumulate target information, partner trust, and ecosystem-synergy complementarities through alliance and equity channels (Chesbrough, 2003; Burford, Shipilov, & Furr, 2025), lowering the marginal cost and raising the marginal benefit of deepening collaboration into acquisition. Hence:

> **H1**: The bank-year external-collaboration news share (`collab_frac`, full track) has a positive effect on the bank's fintech M&A event count (`m_and_a_fintech`). Primary identification is 2SLS with a same-type peer leave-one-out instrument. This is a theoretical prediction, not an obtained result.

**H2 (risk-cost channel, exploratory secondary).** External collaboration is not costless: it imports third-party operational risk, counterparty credit risk, and regulatory compliance exposure onto the bank's balance sheet — China's tightening of loan-facilitation and joint-lending regulation is precisely the policy response to this exposure. Wu, Shen, Wu, & Shao (2025) provide directionally consistent evidence that bank-fintech strategic cooperation raises bank risk-taking in China; the independent R&D path generates no such third-party exposure. Hence:

> **H2**: `collab_frac` has a negative effect on the bank stability measure `z_score` (higher external collaboration → lower stability / higher risk-taking). Theoretical prediction, not a result.

**H3 (independent R&D path, exploratory secondary).** If the organizational-source coding captures real differences in how innovation is organized, then independence-oriented banks' innovation should land in internal spending and patent output — Lerner, Seru, Short, & Sun (2024) show that internal attribution of financial innovation output is identifiable from patent records. Hence:

> **H3**: The independence-orientation net gap `independent_minus_collab_gap` (= indep_frac − collab_frac) has positive effects on R&D intensity (`r_and_d_intensity`) and fintech patent counts (`patent_fintech_count`). Theoretical prediction, not a result.

**H4 (network-position moderation, testable only on the production T=19 panel).** Banks already occupying brokerage/intermediary positions in the interbank news co-occurrence network have more channels to heterogeneous information and potential targets, so their conversion rate from collaborative experience to acquisitions should be higher. Hence:

> **H4**: The interaction `collab_x_btwn` (= collab_frac × L.bank_between_cent) has a positive effect on `m_and_a_fintech`. This hypothesis requires the production panel. Theoretical prediction, not a result.
>
> TODO: H4 test results to be backfilled from the production panel.

---

## 3. Data and Method

### 3.1 Sample

**Raw-corpus census.** The measurement pipeline starts from a census taken **before** filtering and deduplication (stage 00 raw_census): 183 deduplicated source files containing **18,198,978** media reports spanning 2007-01-01 to 2025-12-31, across **3,740** media outlets (all-type, unfiltered count). Newspaper-type reports — **92.93%** of all rows (16,912,361 rows) — are retained; wire services, magazines, government bulletins, web pages, and other types are dropped row-wise. Exact-unique records number 18,177,370 (a 0.12% duplication rate).

**Filtering chain.** The production target corpus entering the pipeline adopts the full census scope of **18,198,978** media reports (2007–2025, T=19) — note that this is the **pre**-hard-filter intake scope; the newspaper-retention row count (16,912,361 rows) is an intermediate processing statistic and must not be conflated with it. These rows then pass bank-entity recognition and fintech-lexicon matching, and enter the stage 13 co-occurrence hard filter: only articles in which the target bank and at least one fintech term co-occur within a ±1-sentence window are kept (production setting `sentence_radius=1`, with the criterion covering both headline and body, `match_in_title=true`).

> TODO: The post-hard-filter retained article count is a production statistic, to be backfilled from the production-machine rerun.

**Three-track text materialization.** For every retained article the pipeline materializes three parallel text tracks: full (headline + body), ctx (headline + entity context window), and ss (headline + bank∧fintech same-sentence ±1 window). Downstream, the three tracks serve as mutually robust, co-equal measurement scopes (§3.4, §5).

**Panel.** Article-level classifications aggregate into a bank-year panel of **110 Chinese commercial banks** (2007–2025, T=19).

> TODO: Realized production-panel row/column counts and per-variable non-missing observation counts to be backfilled after the production-machine rerun (the spec design target is obs ≥ 3000; the development environment at the time of drafting carried only an early-trial T=2 dataset (retired; the on-disk panel has since been rebuilt at production scale, T=19), which does not constitute a realized measurement).

### 3.2 Measurement: Innovation Collaboration Mode

- LLM ensemble (gpt-5.4-nano + gemini-3.1-flash-lite + deepseek-v4-flash) majority vote
- Prompt v8 (additive supplementation over v7; dedicated git tag `prompt-v8-supplementation-released` not yet created; only `prompt-v7-released` currently exists)
- Binary encoding: 0 = 自主研发 (independent R&D), 1 = 外部协同 (external collaboration)
- Inter-track κ ≥ 0.45 (mirrors the P3 substantiveness fair-to-moderate threshold; threshold defined in `pipeline/audit/inter_track_kappa.py::_THRESHOLDS` per Landis & Koch 1977)

**Article-retention gate (full-only).** Whether an article is judged to be a bank-fintech report — and thereby enters the measurement universe — depends solely on the full-track verification verdict (`llm_verified_full == True`); the ctx and ss tracks are conditional-on-full measurement/robustness tracks: their row universe is a subset of the full retained set, with per-track columns computed as usual but never independently expanding the sample.

**Construction of `collab_frac`.** The article-level binary classification (stage 21, Chesbrough framework: 0 = independent R&D, 1 = external collaboration) is determined independently by each of the three LLMs and majority-voted into a consensus label; the bank-year aggregation (encode.py) takes

$$
\text{collab\_frac}_{it} = \frac{\#\{\text{external-collaboration articles}\}_{it}}{n\_articles\_llm\_valid_{it}},
$$

with the denominator equal to the bank-year count of articles passing the verification gate. The consensus column is not a bare majority vote: upstream it embeds the verification gate, final_v vote-cleaning, and (for the locus dimension) a keyword fallback.

**Determinism and reproducibility.** All LLM calls fix temperature=0.0 and seed=42; prompt v8 is byte-frozen (cache key `prompt_version='v8-2026-05-17'`); the tokenizer is pinned to `jieba==0.42.1`. On full cache hits, the entire classification layer is offline, zero-cost, and bitwise reproducible under `NEWS_PROCESS_LLM_OFFLINE=1`. This design follows the disciplinary norms for generative-LLM text measurement (de Kok, 2025); the three-method parallel and majority-vote design echoes Hansen & Kazinnik's (2023) systematic comparison of GPT-class models, dictionaries, and BERT on central-bank communication (Fedspeak) classification, within the overall text-as-data framework of Gentzkow, Kelly, & Taddy (2019).

**Cross-vendor per-model twins.** Beyond the consensus column, the pipeline materializes per-model classification aggregates for each of the three vendors, `{gpt54nano, gemini31, deepseekv4}_collab_frac_full` (denominator = that model's own verified article count, with `_src` indicator columns). The three per-model arms and the consensus arm are mutually robust and co-equal, each entering its own just-identified regression (§5).

**Measurement validity (commitment, not yet evidence).** This paper commits to the following validity checks, whose evidence status is pending (to be redeemed on the production corpus with human annotation): (i) criterion validity — Cohen κ, Gwet AC1, and Krippendorff α against a 3-coder gold-standard sample (stage 63, Panel G); (ii) inter-track agreement κ (stage 71, threshold κ ≥ 0.45 as above); (iii) NMI against adjacent constructs (stage 72) and discriminant validity |corr| (stage 73, benchmarked against clarity and numeric-intensity measures). Until real human-κ evidence is in hand, we do not claim that the validity of the collab classification has been established.

> TODO: Stage 63/71/72/73 validity panel numbers to be backfilled after production corpus + human annotation.

### 3.3 Outcome Variables

- Primary: `m_and_a_fintech` (fintech M&A event count from Tonghuashun)
- Short-run: `car_5day_window` (5-day market-adjusted CAR, CSI Bank Index (中证银行指数) benchmark)
- Secondary: `r_and_d_intensity` (CSMAR), `patent_fintech_count` (IncoPat), `capex_it`
- Risk-cost channel: `z_score` (bank stability measure, the outcome for H2)

These financial/M&A/patent outcome variables depend on the forthcoming financial-data enrichment layer (M0.5.11) and are currently wired ahead as capture-guarded columns, computable as soon as the financial panel lands — noted here in a single sentence, without affecting the completeness of the measurement layer or the identification design.

`m_and_a_fintech` is a non-negative, skewed, zero-inflated event **count**. Consistent with the paper_spec's `primary_estimator: iv_2sls_peer_loo`, the main report (the sole confirmatory specification) uses linear 2SLS with the LOO peer instrument (§3.4); to address the count nature of the outcome, following Cohn, Liu, & Wardlaw (2022) we report PPML (ppmlhdfe, template `25_collab_ppml`) as a companion count-model robustness check, alongside log(1+x) OLS as a benchmark while disclosing the latter's unit-dependence problem (§5).

### 3.4 Identification

**Baseline fixed effects.** The baseline is a long-panel two-way fixed-effects regression with bank and year effects:

$$
Y_{it} = \beta \cdot \text{collab\_frac}_{it} + X_{it}'\gamma + \alpha_i + \lambda_t + \varepsilon_{it},
$$

where $\alpha_i$ are bank fixed effects, $\lambda_t$ are year fixed effects, and standard errors are clustered at the bank level. Bank FEs absorb time-invariant strategic endowments; year FEs absorb industry-level shocks (regulatory cycles, technology waves).

**Primary identification: same-type peer LOO instrument, 2SLS.** `collab_frac` is endogenous to unobserved bank-level strategic preferences and investment opportunities. The primary identification instruments the focal bank's share with the leave-one-out average external-collaboration share of other banks of the same type (panel column `leave_one_out_peer_collab_iv`):

$$
\text{collab\_frac}_{it} = \pi \cdot \overline{\text{collab\_frac}}^{\,(-i)}_{g(i),t} + X_{it}'\delta + \alpha_i + \lambda_t + \nu_{it} \quad (\text{first stage}),
$$

$$
Y_{it} = \beta^{IV} \cdot \widehat{\text{collab\_frac}}_{it} + X_{it}'\gamma + \alpha_i + \lambda_t + \epsilon_{it} \quad (\text{second stage}),
$$

where $g(i)$ is bank $i$'s type group. Relevance derives from peer strategic diffusion and shared type-level shock exposure (Manski's 1993 reflection problem is precisely the motivation; identification conditions under network structure are given by Bramoullé, Djebbari, & Fortin, 2009); the construction is isomorphic to the LOO peer-instrument precedent in finance (Leary & Roberts, 2014). **Exclusion-restriction limitations are disclosed candidly**: if peer collaboration directly affects the focal bank's acquisition opportunity set (rather than operating only through the focal bank's own collaboration propensity), the exclusion restriction weakens — an acknowledged limitation of LOO peer instruments (disclosed likewise in Leary & Roberts, 2014). We partially mitigate this with the Bartik fallback instrument and clustering-level benchmarks, without claiming full exclusion.

**Fallback instrument: generalized Bartik.** The fallback is a generalized Bartik shift-share construction (panel column `bartik_collab_iv_full`): base-period exposure shares interacted with industry-level collaboration shocks, shifting the identifying assumption to base-share exogeneity (Borusyak, Hull, & Jaravel, 2025). A lag1 variant, `leave_one_out_peer_collab_iv_lag1`, serves as a temporal-predeterminedness benchmark.

**Just-identification discipline (iron rule).** Each of the three text tracks (full/ctx/ss) carries its own LOO-instrument twin (`leave_one_out_peer_collab_iv` and the ctx/ss counterparts), and each track enters its own **just-identified** (one instrument, one endogenous regressor) 2SLS. The three tracks, the two IV engines plus the lag1 variant, and the three per-model arms are mutually robust and co-equal; they are **never pooled into a single over-identified specification for a Hansen J test** — pooling would misinterpret "measurement-scope differences" as an "instrument-validity test."

**Weak-instrument-robust inference.** We report Kleibergen-Paap F statistics; when they fall below Stock-Yogo critical values, inference defers to Anderson-Rubin weak-instrument-robust confidence intervals (appendix table tableA_collab_iv_arci).

**Clustered inference.** The main specification clusters one-way by bank; bank×year two-way clustering and bank_type-level clustering (matching the LOO instrument's group level) serve as robustness; if production-panel cluster sizes are highly heterogeneous, wild cluster bootstrap supplements.

**Event studies.** Dynamic tests around three exogenous industry shocks: E1 (2013-06-13 Yu'ebao launch), E3 (2017-04-27 asset-management regulation), E4 (2020-11-03 Ant IPO suspension), examining differential trajectories of high- vs. low-`collab_frac` banks around each shock and testing parallel pre-trends.

**Confirmatory vs. exploratory declaration.** The paper's sole confirmatory specification is the H1 main specification (collab_frac → m_and_a_fintech, full track, LOO IV, linear 2SLS; PPML is a companion count-model robustness check, not a confirmatory estimator), which receives no multiple-testing correction; heterogeneity and alternative-measure families (H2/H3, subsample splits, weighting variants) are all flagged exploratory, with within-family p-values corrected for FWER via the Romano & Wolf (2005) stepwise method (implementation lineage of List, Shaikh, & Xu, 2019); cross-model family FWER is handled by the pipeline's root-level template (Table A12 Panel C).

---

## 4. Results

> All coefficients, standard errors, and significance levels in this section await production regressions; below is the presentation structure and interpretive scaffolding for each table.

### 4.1 Baseline and Primary Identification (Table 2, M1-M6)

Table 2 presents the main regressions progressively as M1–M6: M1 with `collab_frac` and year FEs only; M2 adds bank FEs (the two-way FE baseline); M3 adds bank-level controls; M4 adds year-level controls; M5 is the LOO IV 2SLS (first stage and KP F reported in the same table); M6 is the PPML count model (Cohn, Liu, & Wardlaw, 2022). Interpretation focuses on: (i) the stability of β from M1→M4 as controls densify (heuristic evidence on the direction of selection bias); (ii) the size of the IV estimate in M5 relative to OLS (gauging the direction of endogeneity); (iii) economic magnitude under the M6 semi-elasticity interpretation.

> TODO: All Table 2 coefficients/SEs/KP F/sample sizes to be backfilled after production regressions.
> TODO: Sign and strength of the first-stage π (peer-diffusion evidence) to be backfilled.

### 4.2 Mechanisms (Table 3)

Table 3 tests the H2/H3 mechanism channels: Panel A uses `z_score` as the outcome (risk-cost channel, predicted negative); Panel B uses `r_and_d_intensity` and `patent_fintech_count` as outcomes with `independent_minus_collab_gap` as the treatment (independent R&D path, predicted positive). If both panels hold, the organizational-source dimension exhibits a forked-path picture: "external collaboration → acquisitions but with a risk cost; independent R&D → internal spending and patents."

> TODO: Table 3 coefficients and significance to be backfilled; the verdict sentence on the mechanisms to be backfilled.

### 4.3 Heterogeneity (Table 4)

Table 4 splits by bank attributes: state-owned vs. not, hub vs. non-hub (news-network position), size, bank type, and era. It additionally tests the H4 interaction `collab_x_btwn` (collaboration × lagged betweenness centrality). All splits are flagged exploratory and receive within-family Romano-Wolf correction.

> TODO: Table 4 split coefficients and RW-corrected p-values to be backfilled; the H4 interaction result awaits the production T=19 panel.

### 4.4 8-Cell Saturated Decomposition (Table 6)

Table 6 runs a regression saturated with the 8-cell indicators of `cell_id_full` (= subst×4 + locus×2 + collab + 1), testing the marginal information content of the organizational-source dimension after controlling P3 substantiveness and P4 locus: if the collab dimension carries no independent information, then within each (subst, locus) pair the collab=0/1 cell coefficients should be indistinguishable. This table is the direct structural test of the orthogonality claim in §2.4.

> TODO: Table 6 cell coefficients and within-pair tests to be backfilled.

---

## 5. Robustness

> Numerical conclusions for every ladder in this section await production regressions. Overarching discipline: all ladders below are **mutually robust, co-equal** parallel designs, each entering its own **just-identified** regression; they are never pooled into a single over-identified Hansen J test.

**(1) Three text tracks.** The treatment is estimated separately on the full (canonical, `collab_frac`) / ctx (`collab_frac_cm`) / ss (`collab_frac_cm_ss`) tracks; the retention gate is full-only, with ctx/ss as conditional-on-full robustness tracks; each track carries its own LOO-instrument twin and enters just-identified in parallel.

> TODO: Three-track coefficient comparison to be backfilled.

**(2) Cross-vendor per-model LLM ladder.** The main specification is re-estimated replacing the consensus treatment with each of the three per-model arms `{gpt54nano, gemini31, deepseekv4}_collab_frac_full`, testing that results are not driven by any single vendor's model; the three arms are co-equal, and cross-model family FWER correction is handled by the root-level Table A12 Panel C (the CLS family). The consensus column is not a bare majority vote (it embeds the verification gate and vote-cleaning steps), so differences between per-model arms and the consensus arm reflect both model disagreement and the contribution of the cleaning steps.

> TODO: Per-model three-arm coefficient comparison and Table A12 Panel C corrected p-values to be backfilled.

**(3) Two IV engines plus the lag1 predeterminedness variant, and weak instruments.** The primary LOO instrument and the generalized Bartik fallback (`bartik_collab_iv_full`) — two engines — run in parallel with the lag1 predeterminedness variant, each just-identified; when KP F is insufficient, inference reads the Anderson-Rubin CI (tableA_collab_iv_arci). (Note: the pipeline-level "three IV engines" term additionally covers a media-outlet house-style exposure engine; P5 carries no outlet instrument column, hence two engines plus a variant here.)

> TODO: Two-engine-plus-lag1 IV comparison and AR CIs to be backfilled.

**(4) Alternative treatment and sign reversal.** The independence-orientation net gap `independent_minus_collab_gap` (Stata binarization `collab_gap ∈ {−1,0,+1}`) serves as a sign-reversal robustness arm: if the main result is driven by external collaboration, the sign should flip under the net-gap treatment.

> TODO: Sign-reversal test to be backfilled.

**(5) Count-outcome estimator ladder.** PPML vs. log(1+x) OLS benchmarks for `m_and_a_fintech` (Cohn, Liu, & Wardlaw, 2022), disclosing the unit-dependence problem of log(1+x).

> TODO: PPML vs. log(1+x) comparison to be backfilled.

**(6) Clustered-inference ladder.** cluster(bank) primary / bank×year two-way / bank_type level, three-tier benchmarks; wild cluster bootstrap supplements under few or heterogeneous clusters.

> TODO: Clustering-ladder SE comparison to be backfilled.

**(7) Subsamples and aggregation weighting.** SOE/hub/size/type/era splits and EW/VW/MW/HW aggregation-weighting families, both flagged exploratory and excluded from the confirmatory family.

> TODO: Subsample and weighting family results to be backfilled.

**(8) Clarity-benchmark robustness (Table A7).** Benchmarks collab results against text-clarity measures (anchored in the readability/clarity literature of the Loughran & McDonald 2011 lineage), ruling out the alternative explanation that collaboration coverage is merely more readable or more boilerplate.

> TODO: Table A7 to be backfilled.

**(9) Romano-Wolf FWER discipline.** The single confirmatory main specification is uncorrected; heterogeneity/alternative-measure families receive within-family stepwise Romano & Wolf (2005) correction (List, Shaikh, & Xu, 2019); the cross-model family is handled by the root-level Table A12 Panel C.

**Negative declaration of inapplicable ladders.** The pipeline's dictionary-ablation variants, political-word weight ladder {0.0, 0.5, 1.0}, rare-word cutoff ladder, three-BERT net_tone, and network construction-criteria ladder belong to the sentiment/dictionary/network measurement families; P5's treatment is an LLM classification, not sentiment or embeddings, so those ladders do not constitute robustness checks for this paper. The pipeline's co-primary dual embedding tracks (Qwen3-Embedding-8B, 4096-dim canonical + text-embedding-3-large, 3072-dim `_lg`, with a Spearman ρ≥0.80 semantic-validity gate) are mentioned only as methodological background when describing the pipeline as a whole and enter none of P5's regressions.

---

## 6. Discussion

**Boundary conditions on the marginal returns to open vs. closed innovation.** If the forked-path picture of §4 holds (external collaboration → acquisitions; independent R&D → internal spending and patents), then the marginal return to open innovation for banks is not unconditionally positive but depends on whether the innovation lands on the business side or the technology side: business-side knowledge (application scenarios, channels, ecosystems) is dispersed among external partners, so the search returns to openness are high; technology-side knowledge (core systems, underlying architecture) carries strong specificity and security/compliance constraints, so the integration returns to closedness are high. This aligns with the boundary conditions emphasized by the Zhang et al. (2024) meta-analysis, and resonates with the contrast between the two theoretically optimal cells — "substantive × tech × independent" and "substantive × app × external" — in the 8-cell decomposition (Table 6).

> TODO: The results-dependent statements in this paragraph to be backfilled after production regressions.

**Risk-cost channel and regulatory implications.** If H2 holds, the acquisition gains of external collaboration come with a stability cost — providing a micro-evidence base for China's tightening of loan-facilitation/joint-lending regulation: the sensible regulatory objective is not to suppress bank-fintech collaboration itself but to price the third-party risk exposure that collaboration imports (directionally consistent evidence in Wu, Shen, Wu, & Shao, 2025; evidence on the real economic gains of fintech credit in Hau et al., 2024 suggests trade-off, not prohibition, is the right frame).

> TODO: Risk-channel magnitudes and refined policy implications to be backfilled.

**Managerial implications.** For bank managers: the organizational-source choice should match the innovation's landing point — prefer open collaboration for ecosystem/business-side innovation (while budgeting third-party risk-management costs), and do not let collaboration substitute for in-house investment on the core-technology side; for banks in network-brokerage positions (H4), the acquisition option value of collaboration channels is higher.

**Limitations.** First, the binary proxy compresses information on partnership intensity, partner type, and collaborative scope (the spectrum nature of Chesbrough/L&S; see the Limitations Statement at the end). Second, identification is observational: the exclusion restriction of the LOO peer instrument is untestable, and the Bartik fallback plus clustering benchmarks only partially mitigate; event studies supply auxiliary dynamic evidence without changing the observational nature. Third, media coverage is itself endogenous — banks with higher coverage propensity may differ systematically, so `collab_frac` measures "covered collaboration propensity." Fourth, annual frequency smooths over within-year strategic dynamics. Fifth, the institutional specificity of the single Chinese market (state-owned bank dominance, strong regulatory cycles) limits extrapolation; cross-country comparative work is the natural extension.

---

## 7. Conclusion

This paper adds the organizational-source dimension to the bank fintech-innovation literature: from Chinese bank-fintech news built on a production target corpus adopting the full census scope of 18,198,978 media reports (2007–2025), we construct a bank-year external-collaboration news share `collab_frac` for 110 Chinese commercial banks via majority vote of three large language models under a byte-frozen prompt at temperature=0, and use same-type peer LOO instrumental-variable 2SLS as the primary identification to test the effects of open-innovation propensity on fintech M&A (H1), risk-taking (H2), and internal innovation output (H3).

> TODO: Main concluding sentences (empirical verdicts on H1–H3) to be backfilled after production regressions.

Theoretically, the paper brings Chesbrough's open innovation, the Laursen-Salter search taxonomy, and the alliance-to-acquisition ladder literature into the bank-fintech setting, and provides a structural test of the dimension's marginal information content via a 2³ = 8-cell saturated decomposition orthogonal to substantiveness (P3) and locus (P4). Methodologically, it demonstrates a deterministic, offline-reproducible, cross-vendor triangulated LLM text-measurement pipeline consistent with the latest disciplinary norms for text-as-data and generative-LLM measurement. For policy, if the risk-cost channel holds, the paper supplies micro-evidence for a regulatory frame that prices collaboration risk rather than prohibiting collaboration.

> TODO: Results-dependent statements in the conclusion to be backfilled after production regressions.

---

## References

- Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2025). The role of banks' business models in their FinTech acquisitions. *Journal of Financial Services Research*. https://doi.org/10.1007/s10693-024-00442-w
- Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. *Journal of International Financial Markets, Institutions and Money*, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
- Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. *Journal of Economic Perspectives*, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
- Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. *Journal of Econometrics*, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
- Burford, N., Shipilov, A., & Furr, N. (2025). Ecosystem synergies as drivers of acquisitions. *Strategic Management Journal*, 46(13), 3218-3251. https://doi.org/10.1002/smj.3729
- Chen, X., Yang, Y., & Wei, J. (2025). How do new ventures thrive in ecosystem venturing: The impacts of alliance strategy and technology interdependence. *Journal of Management Studies*, 62(2), 565-596. https://doi.org/10.1111/joms.13063
- Chesbrough, H. (2003). *Open Innovation: The New Imperative for Creating and Profiting from Technology.* HBS Press.
- Cohen, W. M., & Levinthal, D. A. (1990). Absorptive capacity: A new perspective on learning and innovation. *Administrative Science Quarterly*, 35(1), 128-152.
- Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. *Journal of Financial Economics*, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
- de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. *Management Science*, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
- Dehghani, M. A., Brauneis, A., & Karavidas, D. (2026). Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions. *Technological Forecasting and Social Change*, 226, 124581. https://doi.org/10.1016/j.techfore.2026.124581
- Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. *Academy of Management Journal*, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
- Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. *Journal of Economic Literature*, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
- Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. *Research Policy*, 31(4), 477-492. https://doi.org/10.1016/S0048-7333(01)00120-2
- Hansen, A. L., & Kazinnik, S. (2023). Can ChatGPT decipher Fedspeak? *SSRN Working Paper No. 4399406*. https://doi.org/10.2139/ssrn.4399406
- Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. *The Journal of Finance*, 79(5), 3309-3359. https://doi.org/10.1111/jofi.13384
- Kueschnig, M., & Schertler, A. (2024). Fusing futures: Financial institutions' stock price response to fintech acquisitions. *Finance Research Letters*, 59, 104779. https://doi.org/10.1016/j.frl.2023.104779
- Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159-174. https://doi.org/10.2307/2529310
- Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. *Strategic Management Journal*, 27(2), 131-150. https://doi.org/10.1002/smj.507
- Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? *The Journal of Finance*, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
- Lerner, J., Seru, A., Short, N., & Sun, Y. (2024). Financial innovation in the twenty-first century: Evidence from US patents. *Journal of Political Economy*, 132(5), 1391-1449. https://doi.org/10.1086/727712
- List, J. A., Shaikh, A. M., & Xu, Y. (2019). Multiple hypothesis testing in experimental economics. *Experimental Economics*, 22(4), 773-793. https://doi.org/10.1007/s10683-018-09597-5
- Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance*, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
- Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. *The Review of Economic Studies*, 60(3), 531-542. https://doi.org/10.2307/2298123
- Puri, M., Qian, Y., & Zheng, X. (2024). From competitors to partners: Banks' venture investments in fintech. *NBER Working Paper No. 33297*. https://doi.org/10.3386/w33297
- Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. *Econometrica*, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
- Vives, X. (2019). Digital disruption in banking. *Annual Review of Financial Economics*, 11, 243-272. https://doi.org/10.1146/annurev-financial-100719-120854
- Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. *Applied Economics* (advance online publication). https://doi.org/10.1080/00036846.2025.2536881
- Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. *Journal of Product Innovation Management*, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
- Zheng, H., & Mao, M. Q. (2024). Fintech mergers and acquisitions. *Journal of International Money and Finance*, 143, 103076. https://doi.org/10.1016/j.jimonfin.2024.103076

---

## Limitations Statement (Pre-registration β supplementation)

This paper measures innovation collaboration mode using a binary classification (independent R&D vs. external collaboration) as a discrete proxy for Chesbrough's open innovation spectrum and Laursen & Salter's continuous search breadth–depth dimensions. The binary measure compresses information about partnership intensity, partner type, and collaborative scope, which future research can extend to multi-class formulations (e.g., M&A vs. strategic investment vs. API openness vs. industry alliance).

The prompt template used for LLM classification (prompt v8) is an *additive supplementation* of the pre-registered v7 prompt (anchored at git tag `prompt-v7-released`); v7's verification, sentiment, substantiveness, and locus criteria are preserved verbatim (a purely additive, non-revisionary supplement that leaves all pre-registered criteria untouched, consistent with pre-registration supplementation discipline). The new collaboration mode dimension is to be committed at git tag `prompt-v8-supplementation-released` upon M5 finalization (this tag is not yet created).

**Empirical-status declaration.** This manuscript was drafted on a development machine (early-trial T=2 data only), with no production regression results of any kind; all coefficients, standard errors, and significance levels in §4/§5 are pending-backfill placeholders. The financial/M&A/patent enrichment layer (M0.5.11) is forthcoming, and the corresponding outcome columns are already wired ahead.

**LLM-use disclosure (pointer).** Consistent with the other papers from the same pipeline, this paper's LLM-use disclosure comprises: (i) LLM routing — article-level classification is performed by three models (gpt-5.4-nano and gemini-3.1-flash-lite routed via OpenLux; deepseek-v4-flash via direct connection) at temperature=0.0, seed=42, under byte-frozen prompt v8, aggregated by majority vote; (ii) the article-retention gate is full-only (`llm_verified_full`), with ctx/ss tracks conditional-on-full; (iii) the pipeline's co-primary dual embedding tracks (Qwen3-Embedding-8B canonical + text-embedding-3-large `_lg`) serve only as pipeline background and enter neither P5's treatment nor any of its regressions. Full disclosure text: `papers/_common/AI_DISCLOSURE_TEMPLATES.md`. Platform-migration note: the LLM inference underlying this paper was executed in July 2026 through the pipeline's then-current aggregation proxy; from August 2026 onward the pipeline routes through OpenLux (`https://api.openlux.ai/v1`). Cache keys are formed from the tuple (model name, prompt text, prompt version, temperature) and do not include the endpoint address, so the migration leaves existing inference results bitwise unchanged.
