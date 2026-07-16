---
family_id: F117
columns:
- bert_pos_substvalid_count_ctx
- bert_pos_substvalid_count_full
- bert_pos_substvalid_count_ss
unit: 篇数/计数 (count, 非负整数)
formula: "bert_pos_substvalid_count{track} = Σ_{i∈bank-year} 1[BERT_argmax_majority(i,{track})=正面] · 1[innovation_substantiveness_full(i) ∈ {实质性, 象征性}]; 作洗稿率 washing_ratio_bert{track} = _safe_ratio(bert_pos_symb_count{track}, ·) 的同域分母"
producer: news_process/pipeline/panel/runner.py (篇章级 _svd_bert_pos{track}=_bert_pos&_subst_measured 在主 panel 循环内构造; _pool_svd_substvalid_counts 仅做 bank-year 求和聚合)
upstream:
- 21_tone_llms.parquet (innovation_substantiveness_full 实质性/象征性 分类)
- 23_tone_berts.parquet (逐模型 BERT 正面/负面 概率)
- 40_panel_yearly.parquet (bank-year 聚合底座)
citations:
- doi: 10.1287/mnsc.2024.07420
  type: journal
  authors: Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C.
  year: 2026
  title: '"Glossy green" banks: The disconnect between environmental disclosures and lending activities'
  venue: Management Science
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: "Sustainability or greenwashing: Evidence from the asset market for industrial pollution"
  venue: Journal of Finance
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  pages_or_artno: 102776
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H., & Lyon, T. P.
  year: 2015
  title: "Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure"
  venue: Organization Science
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: "The symbolic management of stockholders: Corporate governance reforms and shareholder reactions"
  venue: Administrative Science Quarterly
  vol: 43
  issue: 1
  pages_or_artno: 127-153
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
- doi: "10.1111/eufm.12509"
  title: "Identifying greenwashing in corporate-social responsibility reports using natural-language processing"
  authors: "Gorovaia, N., & Makrominas, M."
  year: 2024
  venue: "European Financial Management"
  type: "journal"
- doi: "10.1002/csr.70722"
  title: "Symbolic Versus Substantive ESG Practices: A Systematic Review and Integrative Framework"
  authors: "Ștefănescu, C. A., & Suciu, A. L."
  year: 2026
  venue: "Corporate Social Responsibility and Environmental Management"
  type: "journal"
new_dois:
  - "10.1111/eufm.12509"
  - "10.1002/csr.70722"
---

## CORE

【构念与来源】
本家族三列 bert_pos_substvalid_count{track} 是「实质—象征脱耦」(substantive-symbolic decoupling) 洗稿率测度族里 BERT 均值方法 (方法 E) 的同域分母 (same-domain denominator), 记录每个 银行—年 单元内「被 BERT 集成判为正面语调、且其创新实质性属性已被成功测量」的报道篇数。它本身不是一个可直接解读的经济量, 而是一个为洗稿率除法量身构造的分母骨架: 洗稿率 washing_ratio_bert{track} = 正面且象征性的报道数 (bert_pos_symb_count{track}) 除以本列。构念根系可上溯到 Westphal 与 Zajac (1998) 在《Administrative Science Quarterly》确立的实质管理与象征管理二分——企业既可以做出实质性的治理/战略改变, 也可以仅采取象征性姿态以安抚受众而不改变实际做法; 二者在对外话语上可以同样正面, 却在实际行动上南辕北辙。把这一二分搬到银行金融科技报道语境: 一篇对某银行金科动作正面报道的新闻, 既可能对应实打实的技术投入与业务落地 (实质性), 也可能只是口号式、造势式的表态 (象征性)。象征性正面报道占「实质性可判定的正面报道」的比例, 即洗稿率, 度量的正是这种「说得好听但未必做实」的脱耦倾向, 与近年绿色洗白 (greenwashing)、廉价表态 (cheap talk) 文献同构。

【方法学与计算】
分子分母的域必须严格对齐, 这是本列存在的唯一理由。篇章级指示 _svd_bert_pos{track} = 1[BERT 集成 argmax 多数票判为正面 (该轨)] ∧ 1[innovation_substantiveness_full ∈ {实质性, 象征性}]; 即要求这篇报道既被判正面, 又在实质性维度上「有判定结果」(非缺测)。BERT 侧采用三模型集成的逐模型 argmax 标签多数票 (占比 > 0.5 判正面, 尺度不变, 规避跨模型概率标度差污染), 三模型为 finbert_cn / fin_sent_zh / finbert2。实质性侧取 innovation_substantiveness_full 的取值落入 {实质性, 象征性} 两类有效标签集; 若 LLM 未能判出实质性 (NaN→astype(str)→'nan'), 该篇既进不了象征性分子, 也不应计入分母。这一「同域」修正 (fix omni-g-runner-10/14) 修补了旧实现的系统性偏误: 旧分母数全部正面文章, 当实质性分类失败率上升时, 有效分子被稀释, 洗稿率被虚假地压低。篇章级指示由 _pool_svd_substvalid_counts 在 银行×年 上求和聚合为本列, 命中 balance_panel 的计数零填规则 (零新闻 银行—年 → 0), 除法经 _safe_ratio 在分母为 0 时安全返 NaN; 旧 schema 缺本列时 _svd_denom 回退物理分母 bert_pos_count{track}。需要强调: 实质性/象征性标签固定取 full 轨 (v3.2.0 起裸 innovation_substantiveness 退役、以 _full 为 main spec), 因此三列的轨道差异只由 BERT 正面判定的轨道驱动, 而非象征性判定的轨道。

【文献定位】
测度方法学锚定在金融文本的 BERT 情感抽取与洗白实证两条脉络。Huang、Wang 与 Yang (2023) 在《Contemporary Accounting Research》提出的 FinBERT 证明了 transformer 语言模型在金融文本情感抽取上系统优于词典法, 是本族 BERT 均值方法采用集成 transformer 判正面的直接依据; Bochkay 等 (2023) 同刊综述系统梳理了会计文本分析的下一步方向, 为多测度并置提供方法学框架。洗白/脱耦实证方面, Bingler 等 (2022) 用 ClimateBert 识别气候披露中的「廉价表态与摘樱桃」, 与本族「象征性正面 ÷ 实质性可判正面」的构造几乎逐字对应; Giannetti 等 (2026, 《Management Science》) 记录了「亮绿」银行环境披露与实际放贷活动的脱节, Duchin、Gao 与 Xu (2025, 《Journal of Finance》) 从工业污染资产市场提供了区分真可持续与洗白的证据, Kim 与 Lyon (2015, 《Organization Science》) 则给出洗绿与「洗棕」双向夸大/过度谦逊的对称刻画——三者共同支撑「正面话语与实质行动可脱耦」这一识别前提。Loughran 与 McDonald (2011, 《Journal of Finance》) 关于文本情感测量的经典口径, 提醒极性计数须谨防语域错配, 正是本列坚持同域分母的方法论根据。Gorovaia 与 Makrominas (2024, European Financial Management) 用自然语言处理从企业社会责任报告中提取文本特征, 识别披露与实际行为脱耦的洗白倾向, 与本族象征性/实质性 BERT 分母构造的方法学定位高度契合; Ștefănescu 与 Suciu (2026, Corporate Social Responsibility and Environmental Management) 系统综述并整合象征性与实质性 ESG 实践的理论框架, 为本族「实质—象征脱耦」构念提供最新的跨学科文献锚点。铁律: 本族三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; BERT 三模型亦各自 just-identified 并排、per-model 独立降级; 留篇门控为 full-only (2026-06-29), full 轨为 canonical 主轨, ctx/ss 降为 conditional-on-full 的测度/稳健轨。

## VAR: bert_pos_substvalid_count_full

【变体差分】
full 轨变体, 是本族 canonical 主轨, 也是留篇门控 (full-only, 2026-06-29) 判定「一篇银行金科报道」所依据的轨道。文本口径 = 标题 prepend + 全文正文 (content_full), BERT 集成的正面 argmax 多数票在整篇 (标题+正文) 上评估。分母指示 = 1[BERT 集成正面 (full 轨)] ∧ 1[innovation_substantiveness_full 已测量]; 由于实质性标签本就固定取 full 轨, 本列是三列中唯一分子侧 (BERT 轨) 与分母侧 (实质性轨) 完全同轨的变体, 语义上最干净。作为分母, 它与 bert_pos_symb_count_full 配对生成 washing_ratio_bert_full——本族洗稿率的规范 (canonical) 主测度。三列之间就轨道口径互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。生产规模 T=19 下正常出值; dev T=2 上因样本极浅可能出现零覆盖 银行—年 → 0 → 除法 NaN, 属预期退化而非缺陷。本列与 F118 (bert_pos_symb_count, 分子) 是同一洗稿率除式的分母/分子对手方, 二者必须同域读取, 不可交叉借用异轨或异方法的计数。需特别区分本列与词典法方法 D2 的同名分母 (如 loughran_pos_substvalid_count) 及单模型 BERT 方法 E2 的 per-model 分母 (F300 族): 本列的正面判定来自三个 BERT 模型的集成多数票而非任一单模型, 亦非词典打分正负号, 故与那些分母虽命名同构却口径不可互换。同理, 本列不同于 LLM 投票方法 A 的 pos_substvalid_count (F477), 后者正面侧来自情感 LLM 三家投票共识, 而非 BERT。三条测度线 (LLM / 词典 / BERT) 就正面判定来源互为稳健性、各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: bert_pos_substvalid_count_ctx

【变体差分】
ctx 轨变体, 属 conditional-on-full 的测度/稳健轨。文本口径 = 标题 prepend + 实体窗口 (content_ctx, 银行/金科实体邻近窗内的正文片段), BERT 集成的正面 argmax 多数票在该窗口文本上评估, 因此与 full 轨相比, 正面判定基于更聚焦、更短的上下文。关键差分: 分母指示的 BERT 正面侧取 ctx 轨, 但实质性掩码仍固定取 innovation_substantiveness_full (v3.2.0 起以 _full 为 main spec), 故本列是「ctx 轨正面 ∧ full 轨实质性可判」的交叉口径——分子/分母的轨道不完全同轨, 这是本列区别于 full 变体的精确语义。与 bert_pos_symb_count_ctx 配对生成 washing_ratio_bert_ctx, 作为 full 轨洗稿率的轨道稳健性对照。ctx 与 full/ss 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 行宇宙为 full 留篇集的子集, per-track 计数照算。这一「BERT 正面取 ctx 轨、实质性取 full 轨」的交叉设计是刻意的: 实质性维度是篇章级、话题级的语义属性, 在实体窗口截断后判定基础不稳, 故 v3.2.0 起统一钉在 full 轨以保口径稳定; 而正面语调对上下文窗口敏感, 恰是三轨稳健性检验要暴露的自由度。因此本列度量的是「在更聚焦的实体上下文里仍被判正面、且整篇实质性可判」的报道数, 与 full 变体的差异纯由 BERT 正面轨道贡献。dev T=2 上上下文更窄可能进一步压低有效计数, 出现零方差/零覆盖退化属预期; 生产 T=19 下 ctx 与 full 应呈可辨识但高度相关的分化。

## VAR: bert_pos_substvalid_count_ss

【变体差分】
ss 轨变体, 属 conditional-on-full 的测度/稳健轨, 口径最严。文本 = 标题 prepend + 「银行 ∧ 金科同句 ±N 窗」(content_ss, N 由 config context_window.ss_sentence_radius 定, 默认 1); BERT 集成正面 argmax 多数票在该同句共现窗上评估。回退语义镜像 ctx: 当某篇不存在银行 ∧ 金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True (共享 n_articles 分母), FINTECH_AC=None 时 *_is_fallback 全 True 优雅降级。差分同 ctx: 正面侧取 ss 轨, 实质性掩码仍固定取 innovation_substantiveness_full, 故本列 = 「ss 轨正面 ∧ full 轨实质性可判」的最窄交叉口径。与 bert_pos_symb_count_ss 配对生成 washing_ratio_bert_ss, 作为洗稿率对同句共现约束的稳健性轨。ss 与 full/ctx 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。ss 轨的语义定位是回答「即便把证据面收窄到银行与金科在同一句子里同时出现的最强共现约束, 正面语调是否依然成立」——它是三轨中对「银行—金科关联真实存在」这一前提设防最严的稳健性轨。与 ctx 一样, 分母的实质性掩码仍固定取 full 轨, 故本列 = ss 轨正面 ∧ full 轨实质性可判, 差分纯由 BERT 正面轨道贡献; 但相比 ctx 的实体邻近窗, ss 的同句约束更硬, 落入分母的报道更少、更精。需注意 ss 的 sentence_radius 键与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同配置键, 不可混用。dev T=2 上同句共现约束极紧, 有效计数常趋零、ss 与 ctx 可能退化重合, 属预期; 生产 T=19 正常分化。

<!-- rendered-citations:begin -->
Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C. (2026). "Glossy green" banks: The disconnect between environmental disclosures and lending activities. Management Science. https://doi.org/10.1287/mnsc.2024.07420
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. Journal of Finance. https://doi.org/10.1111/jofi.13412
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure. Organization Science. https://doi.org/10.1287/orsc.2014.0949
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management. https://doi.org/10.1111/eufm.12509
Ștefănescu, C. A., & Suciu, A. L. (2026). Symbolic Versus Substantive ESG Practices: A Systematic Review and Integrative Framework. Corporate Social Responsibility and Environmental Management. https://doi.org/10.1002/csr.70722
<!-- rendered-citations:end -->
