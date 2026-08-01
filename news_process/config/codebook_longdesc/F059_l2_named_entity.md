---
family_id: F059
columns:
- avg_named_entity_ctx
- avg_named_entity_full
- avg_named_entity_ss
unit: 无量纲比率 (逐篇 = 具名实体 token 数 / 实词 token 数 ∈ [0,1]; 面板列为篇均)
formula: "named_entity_ratio_{trk} = n_named_entity_tokens / n_real_words (逐篇, _safe_div: 实词数>0 才计, 否则 NaN); avg_named_entity_{trk} = mean over full-only 留篇集内该轨非空的 named_entity_ratio_{trk}"
producer: news_process/pipeline/sentiment/lexical_complexity.py (逐篇 named_entity_ratio) ; news_process/pipeline/sentiment/tone_words.py (三轨物化 LEXICAL_COMPLEXITY_KEYS) ; news_process/pipeline/panel/encode.py (篇均聚合) ; news_process/pipeline/panel/stata_export.py (标签)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- 22_tone_words.parquet (逐篇 named_entity_ratio_full/ctx/ss)
- 40_panel_yearly.parquet (银行-年篇均)
citations:
- doi: 10.2139/ssrn.5182756
  type: wp
  authors: Engelberg, J., Manela, A., Mullins, W., & Vulicevic, L.
  year: 2025
  title: "Entity neutering"
  venue: SSRN Working Paper
- doi: 10.48550/arXiv.2412.19140
  type: arxiv
  authors: Zhu, S., He, C., Liu, H., Dong, P., Zhao, H., Yan, Y., Jia, Y., Zan, H., & Peng, M.
  year: 2024
  title: "SILC-EFSA: Self-aware in-context learning correction for entity-level financial sentiment analysis"
  venue: arXiv
- doi: 10.1126/sciadv.abi8021
  type: journal
  authors: Binette, O., & Steorts, R. C.
  year: 2022
  title: "(Almost) all of entity resolution"
  venue: Science Advances
  vol: 8
  issue: 12
  pages_or_artno: eabi8021
- doi: 10.3233/sw-222986
  type: journal
  authors: Sevgili, Ö., Shelmanov, A., Arkhipov, M., Panchenko, A., & Biemann, C.
  year: 2022
  title: "Neural entity linking: A survey of models based on deep learning"
  venue: Semantic Web
  vol: 13
  issue: 3
  pages_or_artno: 527-570
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1007/s11142-016-9371-1
  type: journal
  authors: Hope, O.-K., Hu, D., & Lu, H.
  year: 2016
  title: "The benefits of specific risk-factor disclosures"
  venue: Review of Accounting Studies
  vol: 21
  issue: 4
  pages_or_artno: 1005-1045
- doi: "10.1016/j.jacceco.2023.101635"
  type: "journal"
  authors: "Aghamolla, C., & Smith, K."
  year: 2023
  title: "Strategic complexity in disclosure"
  venue: "Journal of Accounting and Economics"
- doi: "10.1016/j.heliyon.2024.e30053"
  type: "journal"
  authors: "Yang, J., Zhang, T., Tsai, C.-Y., Lu, Y., & Yao, L."
  year: 2024
  title: "Evolution and emerging trends of named entity recognition: Bibliometric analysis from 2000 to 2023"
  venue: "Heliyon"
- doi: "10.1111/1911-3846.12825"
  type: "journal"
  authors: "Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W."
  year: 2022
  title: "Textual Analysis in Accounting: What's Next?"
  venue: "Contemporary Accounting Research"
new_dois:
- 10.1111/1475-679X.12123
- 10.1007/s11142-016-9371-1
- "10.1016/j.jacceco.2023.101635"
- "10.1016/j.heliyon.2024.e30053"
- "10.1111/1911-3846.12825"
---

## CORE

【构念与来源】
本家族度量的是新闻文本的具名实体密度 (named-entity density), 即一篇报道中被识别为具名实体的词元 (机构名、人名、地名、产品/品牌等专有名词) 占其实词总量的比例。构念根源来自会计与金融文本分析中的披露具体性 (disclosure specificity) 传统: Hope, Hu 与 Lu (2016) 在风险因子披露研究中证明, 提及具体的实体与数字使披露更可核验、信息含量更高, 市场对具体披露的反应显著强于泛化措辞。据此, 本项目把披露具体性拆成正交的两面——实体面与数字面。实体面即本家族的具名实体密度, 数字面则由数值披露强度 (num_intensity) 承担, 二者刻意分列以避免把"提到某家金融科技公司"与"给出一个具体金额"混为同一维度。在生产口径上, 具名实体密度是更宽的具体性指数 (specificity_index) 的真子集: specificity_index = (具名实体 + 硬数词) / 实词, 而 named_entity_ratio = 仅具名实体 / 实词。因此本家族列与 specificity 家族在机械上高度相关 (由子集包含关系可推知逐篇相关系数处于中高量级, 具体强度随语料而定, 应以引擎注入的统计段为准而非在正文写死), 属信息量充分的中高相关而非别名; 但正因是子集导致的机械相关, 具名实体密度与 specificity_index 不得同时进入同一回归右手边, 使用时须在文中披露这一子集关系。

【方法学与计算】
逐篇计算落在 lexical_complexity.py: 对分词后的文本, 先剔除停用词与功能词得到实词序列, 再按专有名词判据标注其中的具名实体词元, named_entity_ratio = 具名实体词元数 / 实词词元数。分母由 _safe_div 守护, 只有实词数严格大于零时才返回比值 (round 6 位), 否则返回 NaN, 避免 0 分母伪造出 0 密度; 空文本或无效文本经 _empty_result 统一返回全 NaN, 保证跨行 dict 结构一致。该逐篇键经 LEXICAL_COMPLEXITY_KEYS 自动物化为 named_entity_ratio_full / _ctx / _ss 三个文章级列 (tone_words 三轨), 其中 ss 轨为 v3.9.0 起新增的"银行与金科同句共现"轨。面板层由 encode 把留篇集内每一轨的逐篇比值取篇均, 得到本家族三列 avg_named_entity_full / _ctx / _ss。留篇门控采 full-only 口径 (2026-06-29): 一篇报道是否计入银行-年宇宙, 只由 llm_verified_full 判定; ctx 与 ss 轨降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 篇均仍按各轨自身非空篇数独立计算。三轨文本口径: full = 标题 prepend + 全文正文; ctx = 标题 + 实体窗口; ss = 标题 + 银行与金科同句 ±N 窗; ss 的回退语义镜像 ctx——当某篇不存在银行与金科同句共现时, content_ss 退化为全文 body 且 ss_is_fallback=True, FINTECH_AC 为空时三轨的 *_is_fallback 全 True 优雅降级。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨列混进同一 over-identified Hansen J 检验; 本家族属非嵌入的词法测度, 无 co-primary 的 _lg 孪生列。

【文献定位】
在测量方法学上, 本家族承接 Loughran 与 McDonald (2016) 对会计金融文本分析的系统综述: 该文强调词法层面的可复现测度须公开分词与判据、须与长度等机械混淆量分离核算, 也提醒具体性类指标对分词器与专名边界高度敏感——这正是本项目把具名实体密度与数值强度、与套话率分列并各自披露机械相关的方法学依据。构念的经济学含义则锚在 Hope, Hu 与 Lu (2016): 具体实体披露降低信息不对称、提升披露可核验性, 为把"报道点名了哪些具体主体"当作一条有信息价值的文本维度提供了实证支撑。更下游地, 具名实体的识别、消歧与解析本身是活跃的技术领域: Binette 与 Steorts (2022) 综述实体解析的统计框架, Sevgili 等 (2022) 综述基于深度学习的神经实体链接, Zhu 等 (2024) 针对实体级金融情感给出上下文学习纠错基准, 而 Engelberg 等 (2025) 的实体消隐 (entity neutering) 实验则从反面提示: 抹去具名实体会系统性改变文本承载的信息, 这与本家族把实体密度视作独立信息维度的立场互为印证。需要说明的是, 本项目的具名实体判据是词法启发式而非训练式实体链接, 因此上述链接/解析文献是构念定位与效度参照, 而非本列的实现细节。Aghamolla 与 Smith (2023, Journal of Accounting and Economics) 建立经理人策略性选择披露复杂度的模型, 说明具体与复杂措辞在传递信息与掩饰负面消息之间的权衡, 为本家族把具名实体密度视为披露具体性一维的构念提供了2023年最新的理论支撑。Yang, Zhang, Tsai, Lu 与 Yao (2024, Heliyon) 对2000-2023年具名实体识别研究做文献计量分析, 梳理该技术领域的演进与新兴趋势, 为本家族采用词法启发式具名实体判据提供方法学背景。Bochkay, Brown, Leone 与 Tucker (2022, Contemporary Accounting Research) 系统综述会计学文本分析方法的最新进展与未来方向, 呼应本家族把具名实体密度作为披露具体性可复现文本测度的方法学定位。

## VAR: avg_named_entity_ctx

【变体差分】
本列是具名实体密度的 ctx 轨篇均, 与 avg_named_entity_full、avg_named_entity_ss 共用同一逐篇公式 named_entity_ratio = 具名实体 / 实词, 唯一差别在扫描文本域: ctx 轨的 content_ctx = 标题 prepend + 实体上下文窗口, 即只保留银行/金科实体附近的上下文片段, 而非全文正文。因此本列刻画的是"在与目标实体相关的上下文里, 报道点名具体主体的密度", 相对 full 轨更聚焦、噪声更低, 但样本上受窗口截断影响, 当某篇无可用实体窗口时按 ctx 物化规则处理。在留篇口径上, 本列采 full-only 门控的 conditional-on-full 语义: 行宇宙是 full 留篇集的子集, 但篇均分母用的是本轨自身非空的篇数, 不借用 full 轨分母。ctx 轨与 full、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified Hansen J; 本列为非嵌入词法测度, 无 _lg co-primary 孪生。早期试跑 T=2 语料上, ctx 轨因窗口稀疏可能出现较多缺失或退化, 属预期, 生产 T=19 语料方能充分取值。使用时须记得本列与同轨的 specificity_index_ctx 是子集机械相关, 不得同式并入。经济含义上, ctx 轨回答的是一个更贴近处理机制的问题: 当报道确实在讨论银行与金融科技时, 它是否用具体主体来支撑叙事, 还是停留在泛化的行业措辞。相较 full 轨把导语、背景、无关段落一并纳入, ctx 轨剥离了与目标实体无关的正文噪声, 因而在检验"报道具体性是否随金融科技关注度变化"这类命题时, 常作为 full 轨结论的语境收窄稳健性证据。分词器与专名边界的敏感性在窗口更短的 ctx 轨上会被放大, 单篇比值的方差通常高于 full 轨, 分析时宜以银行-年篇均而非单篇水平解读。

## VAR: avg_named_entity_full

【变体差分】
本列是家族的规范轨 (full) 篇均, 也是三轨中留篇门控的判定轨。逐篇 named_entity_ratio_full 的扫描文本域 content_full = 标题 prepend + 全文正文, 即在整篇报道范围内计具名实体占实词比例, 覆盖面最全、最不受窗口截断影响, 因而是刻画一篇报道整体具体性实体面的首选测度。full-only 留篇口径 (2026-06-29) 的含义在本列最直接: 一篇报道是否计入银行-年面板宇宙, 只看 llm_verified_full 是否为真, 因此本列的篇均分母等于该银行-年内经 full 轨判定留下的报道数中 named_entity_ratio_full 非空者。相对 ctx 与 ss 两条 conditional-on-full 稳健轨, full 轨是并排三轨里的规范测度, 但三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁把 avg_named_entity_full 与 _ctx、_ss 混进同一 over-identified Hansen J。本列为非嵌入词法测度, 无 co-primary 的 _lg 孪生列, 也不参与 both-or-neither 的双轨降级。方法学上须持续披露: named_entity_ratio 是 specificity_index 的真子集 (仅具名实体面, 剔除硬数词面), 二者因子集包含关系在同轨上机械高度相关 (相关强度为中高量级, 精确数值随语料而定, 以引擎注入统计段为准), 故本列与 specificity_index_full 不得同时进入同一回归右手边; 具名实体的数字面正交测度由 num_intensity 家族承担, 两家族刻意分列以避免把"点名主体"与"给出数字"混为一维。作为全篇覆盖的规范轨, 本列在三轨中对分词与专名判据的偶发波动最鲁棒, 单篇比值方差最低, 因而当研究设计需要一条稳定的具体性实体面基线测度时, 应以本列为首选, ctx 与 ss 两轨作为语境收窄方向上的并排稳健性证据分别呈报。

## VAR: avg_named_entity_ss

【变体差分】
本列是具名实体密度的同句共现 (ss) 轨篇均, 为 v3.9.0 起新增的第三轨。逐篇 named_entity_ratio_ss 的扫描文本域 content_ss = 标题 prepend + 银行与金科同句 ±N 窗 (窗半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。因此本列刻画的是"在银行与金融科技被同句提及的最贴近语境内, 报道点名具体主体的密度", 是三轨中语境最紧、判据最严的一条。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 退化为全文 body 且 ss_is_fallback=True (与 n_articles 共享分母口径); 当 FINTECH_AC 为空时, 三轨的 *_is_fallback 全部 True 做优雅降级, 绝不静默清空。留篇口径同样是 full-only 门控下的 conditional-on-full: 行宇宙是 full 留篇集的子集, 篇均分母用本轨自身非空篇数。ss 轨与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified Hansen J; 本列为非嵌入词法测度, 无 _lg co-primary 孪生。早期试跑 T=2 上 ss 轨因同句共现稀疏、回退比例高, 取值可能高度退化甚至接近零方差, 属预期, 须待生产 T=19 语料方能稳定。与同轨 specificity_index_ss 仍是子集机械相关, 不得同式并入。构念上, ss 轨回答的是三轨中最严的一个问题: 在银行与金融科技被压缩到同一句子的最贴近共现语境内, 报道是否仍以具体主体承载信息。这条轨对判据最挑剔, 也最容易因回退而丢失语境信号, 因此它的价值不在于单独作主测度, 而在于当 full 与 ctx 两轨的结论在最严语境下依然成立时, 提供一条方向一致的边界稳健性证据。分析时须结合 ss_is_fallback 的占比一并解读, 回退比例过高的银行-年格点上本列近似退化为全文口径, 不应据此单点推断。

<!-- rendered-citations:begin -->
Engelberg, J., Manela, A., Mullins, W., & Vulicevic, L. (2025). Entity neutering. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5182756
Zhu, S., He, C., Liu, H., Dong, P., Zhao, H., Yan, Y., Jia, Y., Zan, H., & Peng, M. (2024). SILC-EFSA: Self-aware in-context learning correction for entity-level financial sentiment analysis. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.19140
Binette, O., & Steorts, R. C. (2022). (Almost) all of entity resolution. Science Advances, 8(12), eabi8021. https://doi.org/10.1126/sciadv.abi8021
Sevgili, Ö., Shelmanov, A., Arkhipov, M., Panchenko, A., & Biemann, C. (2022). Neural entity linking: A survey of models based on deep learning. Semantic Web, 13(3), 527-570. https://doi.org/10.3233/sw-222986
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Hope, O.-K., Hu, D., & Lu, H. (2016). The benefits of specific risk-factor disclosures. Review of Accounting Studies, 21(4), 1005-1045. https://doi.org/10.1007/s11142-016-9371-1
Aghamolla, C., & Smith, K. (2023). Strategic complexity in disclosure. Journal of Accounting and Economics. https://doi.org/10.1016/j.jacceco.2023.101635
Yang, J., Zhang, T., Tsai, C.-Y., Lu, Y., & Yao, L. (2024). Evolution and emerging trends of named entity recognition: Bibliometric analysis from 2000 to 2023. Heliyon. https://doi.org/10.1016/j.heliyon.2024.e30053
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2022). Textual Analysis in Accounting: What's Next? Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.12825
<!-- rendered-citations:end -->
