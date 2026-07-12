---
family_id: F049
columns:
- avg_iss_confidence_ctx
- avg_iss_confidence_full
- avg_iss_confidence_ss
unit: LLM 自报分类置信度均值 (无量纲, ∈ [0,1]; 0.0 = 该 bank-year 无携带有效实质性标签的模型)
formula: "avg_iss_confidence_{track} = mean_over_articles( mean_over_models_with_nonnull_substantiveness_label( model_innovation_substantiveness_confidence ) ); 行级分子仅纳入被接受标签非 None 且 confidence>0 的模型子集, 无有效项时行级取 0.0"
producer: news_process/pipeline/panel/encode.py (bank-year 聚合); 行级置信度合成 news_process/pipeline/sentiment/tone_llms.py::_avg_innovation_confidence
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (innovation_substantiveness_confidence_{full,ctx,ss})
citations:
- doi: 10.48550/arXiv.2512.10793
  type: arxiv
  authors: Schlee, M., Weisser, C., Kivimäki, T., Mashiku, M., & Saefken, B.
  year: 2025
  title: "LabelFusion: Fusing large language models with transformer encoders for robust financial news classification"
  venue: arXiv
- doi: 10.1002/widm.70019
  type: journal
  authors: Alva Principe, R., Chiarini, N., & Viviani, M.
  year: 2025
  title: "Long document classification in the transformer era: A survey on challenges, advances, and open issues"
  venue: WIREs Data Mining and Knowledge Discovery
  vol: 15
  issue: 2
  pages_or_artno: e70019
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: "How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk"
  venue: Journal of Banking & Finance
  vol: 164
  pages_or_artno: 107191
- doi: 10.18653/v1/2024.naacl-long.366
  type: journal
  authors: Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I.
  year: 2024
  title: "A survey of confidence estimation and calibration in large language models"
  venue: Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics
  pages_or_artno: 6577-6595
- doi: 10.6092/issn.1971-8853/19461
  type: journal
  authors: Törnberg, P.
  year: 2024
  title: "Best practices for text annotation with large language models"
  venue: Sociologica
  vol: 18
  issue: 2
  pages_or_artno: 67-85
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: "The symbolic management of strategic change: Sensegiving via framing and decoupling"
  venue: Academy of Management Journal
  vol: 49
  issue: 6
  pages_or_artno: 1173-1193
new_dois: []
---

## CORE

【构念与来源】
本家族三列刻画的是「实质性创新分类置信度」(innovation substantiveness confidence, 内部短名 iss)在 bank-year 层的均值。所谓「实质性」维度, 沿用 Weick 与 Zbaracki 一系组织传播研究里「实质 (substantive) 对象征 (symbolic)」的二分构念: 一条银行金融科技报道到底是在陈述真实落地的技术投入与业务改造, 还是仅在做象征性的话语包装与声誉管理。该二分正是 P3 (bank_fintech substance, W&Z 谱系) 处理变量所依托的语义基座, 与 Fiss 与 Zajac (2006) 关于「框定与脱耦」的象征性战略管理、以及 Bingler et al. (2024) 关于气候披露中「空谈 (cheap talk)」与真实行动脱节的实证, 属同一条实质对象征的构念脉络。本家族不度量分类结果本身 (那是分类占比列族的职责), 而是度量大语言模型在做出该实质对象征判断时的自报把握程度 — 即模型的 verbalized confidence, 可读作对该 bank-year 报道文本上「实质性信号清晰度」的一个连续代理。

【方法学与计算】
计算分两级。第一级在文章行内合成: stage 21 情感 LLM 对每篇报道就实质性维度独立给出标签与一个 [0,1] 区间的自报置信度; `tone_llms.py::_avg_innovation_confidence` 只把那些「被接受的实质性标签非 None 且 confidence 严格大于 0」的模型的置信度取算术平均, 得到该文章该轨的行级置信度, 无任何有效项时行级取 0.0。此处的聚合域对齐是关键工程约束: prompt 指示模型在判 false 时把标签填 null, 但模型常仍附带一个置信度数值, 若无条件并入均值会使「标签投票的分子」与「伴随置信度的信号强度」来自不同的模型子集, 故显式以「标签非 None」作过滤, 镜像情感侧「sentiment-not-None」语义。第二级在 `encode.py` 内按 (target_bank, year) 对上述行级置信度取 `groupby().mean()`, 对应轨源列缺失时优雅置 NaN。因此单位为无量纲、值域 [0,1] 的置信度均值, 0.0 特指该 bank-year 无携带有效实质性标签的模型, 不可与「低置信度」混读。

【文献定位】
该测度落在「用大语言模型做文本标注并把模型自报置信度当作连续代理」这一近年方法学交汇点上。Geng et al. (2024) 系统综述了大语言模型置信度估计与校准的现状, 明确指出 verbalized confidence 虽倾向过度自信, 但其保序性 (monotonicity) 基本成立, 因而适合作跨文档的相对信号强度而非绝对概率使用 — 这正是本家族把置信度当「信号清晰度」相对代理、而非严格后验概率的依据。Törnberg (2024) 给出大语言模型文本标注的最佳实践, 支撑「多模型独立标注 + 聚合」的产出范式。Alva Principe et al. (2025) 与 Schlee et al. (2025) 分别从长文档分类综述与金融新闻分类的融合模型角度, 佐证在长篇中文财经报道上做实质对象征分类的可行性与噪声来源。三轨 (full/ctx/ss) 是同一置信度构念在不同文本口径下的并列度量, 严格「各自 just-identified 并排、互为稳健性、不分主次」, 禁混进同一 over-identified 的 Hansen J 检验; 是否判定为一篇银行金融科技报道遵循 full-only 留篇门控 (2026-06-29), ctx 与 ss 是 conditional-on-full 的留篇子集上的测度轨。

## VAR: avg_iss_confidence_ctx

【变体差分】
本列是实质性分类置信度均值的实体窗 (ctx) 轨。其文本口径为「标题 prepend + 实体上下文窗口」: 在 stage 14 由 ctx_materializer 物化的 `content_ctx` 上, 大语言模型只面向围绕目标实体的上下文窗口做实质对象征判断, 相较全文轨剥离了远离实体的段落噪声。行级与 bank-year 两级聚合口径与家族 CORE 完全一致 — 逐模型取被接受实质性标签非 None 且置信度大于 0 者的均值, 再按 (target_bank, year) 取文章均值; 对应源列 `innovation_substantiveness_confidence_ctx` 缺失时优雅置 NaN, 行级无有效项取 0.0。该列在留篇口径上属 conditional-on-full: 行宇宙是 full-only 门控留下的报道集的子集, ctx 轨仅在该子集上 per-track 另算, 不改变「一篇报道是否算银行金融科技报道」的判定。ctx 轨与 full、ss 两轨严格互为稳健性、各自 just-identified 并排, 禁三轨混入同一 over-identified Hansen J。相较全文轨, ctx 置信度更能反映模型在「贴近实体的局部文本」上对实质性信号的把握, 是全文轨的稳健性对照而非其从属。需要强调, ctx 轨的实体窗口口径与 stage 13 共现硬过滤的邻近判据并非同一把尺子: 前者是喂给大语言模型判分的文本材料范围, 后者是决定报道去留的过滤判据, 二者共享「实体邻近」直觉但不互相复用原语。在解读上, 当全文轨与实体窗轨的实质性置信度出现系统性背离时, 提示实质对象征的判别信号更多来自远离实体的段落 (全文高、ctx 低) 抑或紧贴实体的表述 (ctx 高、全文低), 这种轨间对照本身即是一种稳健性证据, 而非要在两轨间择一为主。

## VAR: avg_iss_confidence_full

【变体差分】
本列是实质性分类置信度均值的全文 (full) 轨, 也是家族内与 full-only 留篇门控同口径的首要轨。其文本口径为「标题 prepend + 全文正文」: 在 `content_full` 上, 大语言模型对整篇报道做实质对象征判断并自报置信度。全文轨承载了最完整的语境, 也因此可能纳入远离目标实体的段落。行级合成同 CORE — 仅纳入被接受实质性标签非 None 且置信度大于 0 的模型子集取均值, 再在 encode 层按 (target_bank, year) 对文章置信度取均值; 源列 `innovation_substantiveness_confidence_full` 缺失置 NaN, 行级无有效项取 0.0。关键口径: stage 21 判定「一篇银行金融科技报道」只看 full 轨的 llm_verified_full, 故本列所在的 full 留篇集是 ctx/ss 两轨的行宇宙母集, ctx/ss 为其 conditional-on-full 子集测度。full 轨与 ctx、ss 轨严格互为稳健性、不分主次, 各自 just-identified 并排, 禁三轨混入同一 over-identified Hansen J。它是实质性信号清晰度在整篇报道口径下的度量。之所以把 full 轨与门控口径绑定, 是因为「一篇报道算不算银行金融科技报道」这一留篇判定若逐轨各判, 会导致三轨行宇宙互不嵌套、无法在同一 bank-year 面板上并排比较; 统一以 full-only 门控留篇, 再让 ctx/ss 在同一留篇集上各算 per-track 测度, 既保证三轨可比, 又保留了轨间语境宽窄的稳健性对照。因此本列既是首要报告轨, 又充当 ctx/ss 两轨的行宇宙锚, 但在计量识别上仍与另两轨平权 — 首要仅指报告习惯, 不含「主测度」的因果优先性含义。

## VAR: avg_iss_confidence_ss

【变体差分】
本列是实质性分类置信度均值的同句 (ss) 轨。其文本口径为「标题 prepend + 银行与金融科技同句共现的 ±N 句窗口」(窗半径由 config filtering.yaml 的 context_window.ss_sentence_radius 决定, 默认 1): 大语言模型只在银行与金科词同句邻近的最窄语境内做实质对象征判断, 是三轨中语境最紧的一轨。回退语义严格镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, `content_ss` 回退为全文正文、`ss_is_fallback` 置 True, 与 ctx 共享 n_articles 分母, 优雅降级而非置空。行级与 bank-year 聚合口径同 CORE — 逐模型取有效实质性标签者置信度均值再按 (target_bank, year) 取文章均值, 源列 `innovation_substantiveness_confidence_ss` 缺失置 NaN。留篇口径同为 conditional-on-full: 行宇宙是 full-only 门控留篇集的子集。ss 轨与 full、ctx 严格互为稳健性、各自 just-identified 并排, 禁三轨混入同一 over-identified Hansen J。它刻画模型在最紧凑同句语境下对实质性信号的把握, 是三轨中最保守的稳健性对照轨。需注意 ss 轨的同句共现判据 (银行与金科词严格同句) 与 stage 13 硬过滤所用的 ±1 句窗判据是两个不同口径键, 前者用于裁出喂模型的最窄文本、后者用于报道去留, 不可互相复用; 且回退行 (ss_is_fallback=True) 上模型实际看到的是全文正文, 故 ss 轨在同句共现稀疏的样本上会向全文轨收敛, 解读其置信度均值时应结合 fallback 比例。当同句轨置信度稳健地复制全文轨与实体窗轨的结论时, 说明实质对象征的判别信号即便压缩到最窄同句语境仍然清晰, 构成对主结论最严格的稳健性支撑。

<!-- rendered-citations:begin -->
Schlee, M., Weisser, C., Kivimäki, T., Mashiku, M., & Saefken, B. (2025). LabelFusion: Fusing large language models with transformer encoders for robust financial news classification. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2512.10793
Alva Principe, R., Chiarini, N., & Viviani, M. (2025). Long document classification in the transformer era: A survey on challenges, advances, and open issues. WIREs Data Mining and Knowledge Discovery, 15(2), e70019. https://doi.org/10.1002/widm.70019
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration in large language models. Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics, 6577-6595. https://doi.org/10.18653/v1/2024.naacl-long.366
Törnberg, P. (2024). Best practices for text annotation with large language models. Sociologica, 18(2), 67-85. https://doi.org/10.6092/issn.1971-8853/19461
Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
<!-- rendered-citations:end -->
