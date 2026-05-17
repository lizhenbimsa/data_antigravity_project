# Westphal-Zajac Framework Boundary Justification

> 论文 Methodology Section 必备段落 (per W3 顶刊审稿警告). 解释
> 为什么 Westphal & Zajac (1994, 1998) 框架从原文 CEO compensation
> context 延伸到 fintech innovation reporting 是 theoretically
> justifiable.

## 1. Original Context of the W&Z Framework

Westphal and Zajac (1994, ASQ) developed the substantive-vs-symbolic
distinction in the specific context of CEO long-term incentive plans
(LTIPs). Their empirical setting was 570 of the largest U.S.
corporations across 1972–1990. Their core theoretical contribution
was the **decoupling** insight: firms may **adopt** LTIPs symbolically
to signal alignment with shareholder interests while **not
substantively using** them — i.e., the formal policy and the actual
operational practice are decoupled.

Westphal and Zajac (1998, ASQ) extended this framework to corporate
governance reforms more broadly, showing that symbolic LTIP adoption
**deters substantive governance reforms** that would actually
constrain CEO power. The 1998 paper established the framework's
applicability beyond compensation contracts to any organizational
practice serving institutional legitimacy.

Fiss and Zajac (2006, AMJ) further generalized the framework to
**strategic change communications**. They demonstrated that firms use
specific framing language to (a) match divergent stakeholder
preferences, (b) decouple espoused strategic change from actual
implementation, and (c) generate positive market responses to
institutionally appropriate framing. This generalization is the most
direct theoretical bridge to our fintech context: it shows that the
substantive-symbolic distinction applies to **communicative acts
about strategic initiatives**, not only to compensation policies.

## 2. Why W&Z Applies to Fintech Innovation Reporting

We argue the substantive-symbolic distinction applies to bank
fintech news on three theoretically grounded reasons:

### 2.1 Same Underlying Institutional Pressures

Banks face institutional pressure to demonstrate digital
transformation — from regulators (PBoC's "smart finance" initiatives,
CBIRC fintech guidelines), peer institutions (mimetic isomorphism),
and capital markets (fintech valuation premiums). These pressures
**parallel the institutional pressures** Westphal and Zajac (1994)
identified for CEO compensation: signaling alignment with
stakeholder expectations.

### 2.2 Same Decoupling Mechanism

Banks publicly announcing fintech initiatives face the same
decoupling temptation: announcing AI/blockchain/cloud initiatives
**without commensurate substantive resource commitment** generates
the same legitimacy benefits as symbolically adopting LTIPs without
substantively using them. Westphal and Zajac (1998) directly establish
this in their 1998 ASQ paper: symbolic LTIP adoptions generated
significant positive stockholder reactions and deterred substantive
governance reforms, even when the plans were not actually implemented
(`announcement-implementation decoupling`). Fiss and Zajac (2006)
extend this insight to communicative acts about strategic change more
broadly, showing that strategically framed announcements about
strategic change generate positive market responses irrespective of
implementation depth. Both mechanisms apply directly to news-mediated
fintech announcements.

### 2.3 Empirical Plausibility in Bank-Fintech Domain

The fintech revolution literature, summarized by Gomber et al. (2018),
characterizes the disruption of financial services through entry of
specialized fintech firms and incumbents' responsive innovation. While
Gomber et al. do not directly invoke the substantive-symbolic
distinction, their characterization of incumbent banks facing
institutional pressure to demonstrate digital transformation creates
the structural conditions under which symbolic adoption is predicted
by W&Z (1994) theory. The applicability of the substantive-symbolic
distinction to this domain is therefore a theoretically motivated
extension, to be empirically validated through our news classification
and the planned manual validation study (Section 3.5 of the
methodology section).

## 3. Boundary Conditions Considered

We acknowledge four boundary conditions that distinguish our
context from W&Z's original setting:

| W&Z (1994) original | This paper |
|---|---|
| Annual filings (10-K, proxy) | News articles |
| Single-event observation (LTIP adoption) | Recurring narrative content |
| Direct firm communication | Third-party media reporting |
| **Multivariate regression** (570 firms × 18 years) | **Per-article LLM classification** (qualitative coding) |

The fourth boundary deserves explicit attention: W&Z (1994) tests
substantive-vs-symbolic decoupling econometrically by regressing
implementation indicators on adoption indicators with firm and time
controls. Our setting differs in that we **classify** individual
articles as substantive or symbolic via LLM, then aggregate at the
bank-year panel level for downstream econometric use. The per-article
classification step inherits W&Z's conceptual distinction but not
their regression framework. This is a methodological adaptation rather
than a framework redefinition; the published examples of similar
adaptation include Loughran and McDonald (2011), who similarly adapt
Harvard psychological dictionaries to financial text classification
contexts.

These boundary differences do not invalidate the framework; rather
they refine its application:

- **Narrative recurrence**: News-mediated symbolic actions occur
  through repeated announcement-without-action patterns, observable
  in cross-temporal patterns that single-event compensation studies
  cannot capture.
- **Third-party reporting**: News coverage may **amplify** the
  symbolic-vs-substantive distinction because journalists serve as
  informed intermediaries who often pick up on the gap between
  announced strategy and operational reality (Tetlock, 2007, JF).
- **Operationalization adapted**: We operationalize "substantive"
  with five specific verifiable features (real resource commitment,
  capability building, business impact, alignment with operations,
  traceability), and "symbolic" with five mechanisms (slogan
  without specifics, PR packaging, trend following, ritualistic
  reannouncement, espousal-implementation decoupling). These
  domain-adapted criteria are pre-registered in `unified_cot.txt v7`
  and committed at git tag `prompt-v7-released`.

**Footnote (added with P2 commit, tag `wz-boundary-positive-class-pinned`).**
For quantitative downstream econometrics, the binary `prob_score`
columns (`avg_subst_prob_score_*`, `avg_locus_prob_score_*`)
anchor the 1 = 象征性 / 应用场景 positive pole. The encoding is
consistent with `stata_export.py:40-50`
(`SUBSTANTIVENESS_ENCODING = {实质性: 0, 象征性: 1}`;
`LOCUS_ENCODING = {底层技术: 0, 应用场景: 1}`; comment `0 = baseline, 1 = 对照`)
and with the Stata value labels at `stata_export.py:53-61`
(`0: 实质性 (Substantive) / 1: 象征性 (Symbolic)`;
`0: 底层技术 (Technology) / 1: 应用场景 (Application)`). This
positive_class assignment is a downstream econometric encoding;
it does NOT alter the pre-registered classification rules in
`unified_cot.txt v7` (tag `prompt-v7-released`). All panel
regressions consuming these columns are anchored to the
1 = 象征性 / 应用场景 positive pole.

## §4 v3.4.0 Pre-registration β supplementation 声明 (2026-05-17)

**触发事件**: 本研究在 v3.3.0 → v3.4.0 BREAKING 升级中新增第三个创新维度 `innovation_collab_mode` ∈ {自主研发, 外部协同}，锚定 Chesbrough (2003) Open Innovation + Laursen & Salter (2006 SMJ 27:131-150) framework。

**Pre-registration adjustment 性质**: 根据 Nosek et al. (2018, PNAS 115(11):2600-2606) "The preregistration revolution" 第 4 节关于 pre-registration adjustment 的 "additive vs revisionary" 区分:

- **additive (additive supplementation)**: 添加新的、独立的、不修改已注册元素的内容 → 允许，不构成 pre-registration violation。
- **revisionary**: 修改已注册的判定规则 / 操作化定义 / outcome → 等同于 protocol breach，需重新注册。

本研究采用 **β additive supplementation** 路径:

1. **v7 的 5 个 substantive features + 5 个 symbolic mechanisms (per §3 above) 完全保留，字符级不变** (`unified_cot.txt v7` git tag `prompt-v7-released`)。
2. **v7 的 innovation_locus 判定规则 (Gomber 2018 JMIS technology vs application) 完全保留**。
3. **新增 innovation_collab_mode 第三维度** 作为并行 (parallel)、概念正交的判定，不修改任何 v7 已注册元素。
4. **新 git tag `prompt-v8-supplementation-released`** 锚定 v3.4.0 baseline。`prompt-v7-released` tag **永不删除**，保留作为 v7 subset 的历史 baseline (v8 是 v7 严格超集)。

**正交性论证**: 三维度 (substantiveness × locus × collab_mode) 构成 2³ = 8 cross-tab cells，每 cell 在概念上独立可识别 (详见 `innovation_collab_mode_framework.md` §2)。collab_mode 与 substantiveness 的正交性: 自主研发可以是象征性 (e.g., 内部研发声明但无落地)，外部协同也可以是实质性 (e.g., 真实并购 fintech)。collab_mode 与 locus 的正交性: 自主研发 + 底层技术 / 自主研发 + 应用场景 / 外部协同 + 底层技术 / 外部协同 + 应用场景 4 种组合均有真实案例。

**审稿应对**: P1-P4 论文的 limitations 段需追加 1 段标准声明:

> "Innovation collaboration mode (Chesbrough 2003) was added to the prompt schema in a v8 release subsequent to the v7 pre-registration (committed at `prompt-v7-released`). Per Nosek et al. (2018) classification of pre-registration adjustments, the v8 update constitutes an *additive supplementation* (not a revision): the v7 verification, sentiment, substantiveness, and locus criteria are preserved verbatim, character-for-character. The new collab_mode field is parallel to and conceptually orthogonal to the v7 dimensions. The v8 baseline is independently anchored at git tag `prompt-v8-supplementation-released`."

**测试 gate**: `tests/integration/test_prompt_version_wired.py::test_production_prompts_have_version_header` 已拦截"未更新版本号"; bump v7→v8 通过该 gate。Cache schema (`core/caching.py` SCHEMA_VERSION=v1) 包含 prompt_version 维度，v8 prompt 自动 cache silent miss，强制重新调 API (零污染历史 v7 标注)。

**长期约束**: 任何未来对 v7 已 pre-registered 元素的修改 (substantiveness / locus 判定规则、5 个 substantive features、5 个 symbolic mechanisms) 都构成 revisionary breach，须 (a) 创建新的 pre-registration commit，(b) 在所有下游论文 limitations 中显式声明，(c) 不可声称与 v7 baseline 可比。`prompt-v7-released` tag 不可删除。

---

## 5. Anticipated Reviewer Questions and Responses

**Q1**: Why not use a more domain-specific framework (e.g., a
fintech-specific "substantive innovation" measure)?

**A1**: Three reasons: (a) The fintech literature has not yet
developed a measurement framework with the methodological rigor of
W&Z. (b) Using a widely cited published framework provides external
validity and methodological transparency. (c) Pre-registering W&Z
criteria avoids post-hoc judgment calls that would compromise
replicability.

**Q2**: Are these definitions consistent with the management
literature's understanding of symbolic action?

**A2**: Yes. Our operationalization aligns with the institutional
theory literature on **organizational hypocrisy** (Brunsson, 2002),
**decoupling** (Meyer & Rowan, 1977; Bromley & Powell, 2012), and
**symbolic management** (Fiss & Zajac, 2006). The five "symbolic"
features we identify map directly to mechanisms documented in
these literatures.

**Q3**: How do you know LLMs faithfully apply the W&Z framework?

**A3**: We provide three layers of evidence: (a) prompt sensitivity
analysis showing variant-invariant classification at PABAK ≥ 0.90
(see methodology Section 3.4); (b) explicit chain-of-thought
rationale recorded for each classification, enabling post-hoc
inspection; (c) planned multi-rater manual validation study (n =
248, Section 3.5) to establish κ-vs-human benchmarks.

## 5. References

Bromley, P., & Powell, W. W. (2012). From smoke and mirrors to walking the talk: Decoupling in the contemporary world. *The Academy of Management Annals*, *6*(1), 483–530.

Brunsson, N. (2002). *The organization of hypocrisy: Talk, decisions, and actions in organizations* (2nd ed.). Copenhagen Business School Press.

Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. *Academy of Management Journal*, *49*(6), 1173–1193.

Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. *Journal of Management Information Systems*, *35*(1), 220–265.

Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance*, *66*(1), 35–65. https://doi.org/10.1111/j.1540-6261.2010.01625.x

Meyer, J. W., & Rowan, B. (1977). Institutionalized organizations: Formal structure as myth and ceremony. *American Journal of Sociology*, *83*(2), 340–363.

Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. *The Journal of Finance*, *62*(3), 1139–1168.

Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. *Administrative Science Quarterly*, *39*(3), 367–390.

Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. *Administrative Science Quarterly*, *43*(1), 127–153.
