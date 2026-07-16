---
family_id: F047
columns:
- avg_icm_confidence_ctx
- avg_icm_confidence_full
- avg_icm_confidence_ss
unit: 无量纲置信度均值 (∈ [0, 1], 银行-年内逐篇平均)
formula: "avg_icm_confidence{track} = mean_over_(target_bank, year) of innovation_collab_mode_confidence{track}; track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/encode.py::build_panel (三轨 innovation 维度 avg confidence 聚合块)
upstream:
- 21_tone_llms.parquet (innovation_collab_mode_confidence_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.18653/v1/2024.naacl-long.366
  type: journal
  authors: Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I.
  year: 2024
  title: "A survey of confidence estimation and calibration in large language models"
  venue: "Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)"
  pages_or_artno: 6577-6595
- doi: 10.3758/s13428-010-0044-x
  type: journal
  authors: Wright, D. B., & Herrington, J. A.
  year: 2011
  title: "Problematic standard errors and confidence intervals for skewness and kurtosis"
  venue: Behavior Research Methods
  vol: 43
  issue: 1
  pages_or_artno: 8-17
- doi: 10.1145/1102351.1102430
  type: journal
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: "Proceedings of the 22nd International Conference on Machine Learning (ICML)"
  pages_or_artno: 625-632
- doi: 10.1002/smj.507
  type: journal
  authors: Laursen, K., & Salter, A.
  year: 2006
  title: "Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms"
  venue: Strategic Management Journal
  vol: 27
  issue: 2
  pages_or_artno: 131-150
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行-年层面「创新协同模式 (innovation collaboration mode) 分类的平均置信度」。短名 icm 是 innovation_collab_mode 的缩写, 指的是 stage 21 情感与属性 LLM 在给每一篇银行金科报道打「自主研发 vs 外部协同」这一创新协同模式二元标签时, 自报的分类把握度。三家 LLM (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 逐篇给出该维度的标签与置信度, 多模型聚合后得到文章级 innovation_collab_mode_confidence{track}, 再由面板聚合器在 (target_bank, year) 分组内取算术均值, 落成 avg_icm_confidence{track}。取值为无量纲实数, 落在 0 到 1 区间, 数值越高表示该银行当年被报道的金科创新在「自主 / 协同」这一构念轴上越容易被模型清晰判别, 数值偏低则意味着该年报道在协同模式上语义模糊、模型犹豫。构念的实体来源是 Chesbrough (2003) 的开放式创新框架: 企业创新可沿「封闭 (自主研发)」与「开放 (借助外部伙伴、生态、并购、平台) 」两极展开; 金融科技领域的银行既有自建实验室、独立开发的路径, 也有与第三方支付、云厂商、科技公司共建的协同路径, 该二元轴正是刻画这一战略选择的直接测度。Laursen & Salter (2006) 在开放式创新的实证脉络里进一步论证, 企业创新可沿「开放度 (openness)」这一连续谱系展开, 依赖外部伙伴、渠道与知识来源的广度与深度构成与纯自主研发相对的战略维度, 为本家族「自主研发 vs 外部协同」这一分类轴提供了顶刊层面的构念规范依据。置信度本身并非战略方向 (方向由 collab_frac 等占比列承载), 而是「方向信号的清晰程度」这一元测度。

【方法学与计算】
计算链路分两段。第一段在 stage 21 (tone_llms): 对每篇报道, 三家 LLM 各自在 collab 维度上返回一个标签 (「自主研发」或「外部协同」) 与一个自报置信度。文章级置信度的聚合口径 (源码 _avg_innovation_confidence) 与标签投票域严格对齐: 只把该维度标签非 None (即被 canonical 标签集接受) 的模型所报置信度纳入, 且仅计入其中严格大于零的正置信度, 取算术均值; 当无任何模型给出有效标签与正置信度时置 0.0。此对齐修正了历史上「模型判 false、标签为 null 却仍 emit 置信度数值」的行污染均值的缺陷 —— 分子 (标签投票) 与伴随置信度 (信号强度) 必须来自同一模型子集。需强调, 该置信度均值本身不引入关键词分类器回退: 关键词回退与 (None, 0.0) 的优雅降级只发生在 collab 标签 / 占比链路的逐篇解析环节 (决定标签取值), 与本置信度均值的计算相互独立、不参与其分子分母。多模型逐篇聚合后写出 innovation_collab_mode_confidence{track}。第二段在 encode.py 的 build_panel: 按 (target_bank, year) 对该文章级列做 groupby-mean, 得到 avg_icm_confidence{track}; 源列缺失时优雅置 NaN, 与相邻 substantiveness (iss) / locus (il) 两维度的三轨聚合块共用同一机械范式。分母口径遵循全项目 full-only 留篇门控 (2026-06-29): 一篇报道是否算作「银行金科报道」只看 llm_verified_full 为真, ctx 与 ss 轨为 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的置信度均值仍在各自轨上逐列独立计算。ss 轨的文本回退语义镜像 ctx: 当某篇无银行与金科同句共现时, content_ss 回退为全文正文并置 ss_is_fallback 为真。三轨 (full / ctx / ss) 是各自 just-identified 的并排测度、互为稳健性、不分主次, 铁律是禁混进同一 over-identified Hansen J。

【文献定位】
avg_icm_confidence 的方法学落点是「LLM 自报置信度的度量与解释」这一当代议题。Geng et al. (2024) 对大语言模型置信度估计与校准做了系统综述, 指出模型自报置信度与真实正确率之间常存在系统性偏差 (过自信居多), 因而把 LLM 置信度当作信号使用时需以校准视角审慎解读——这正是本家族只把该均值当作「判别清晰度」代理、而非绝对概率真值的依据。Niculescu-Mizil & Caruana (2005) 从监督学习角度论证了不同分类器在输出「良好概率」上的差异, 为「原始模型分数需经校准才逼近真实频率」提供了经典证据, 支持我们对逐篇置信度做保守解读、以跨模型聚合平滑单模型偏置。Wright & Herrington (2011) 具体论证了偏度、峰度这类高阶矩的标准误与置信区间在常规正态理论假定下存在系统性问题、覆盖率失真; 落到本家族, 当稳健性诊断需要考察银行-年置信度分布的形状 (偏度、尾部, 而非仅点均值) 时, 该文直接告诫不可对其高阶矩天真套用标准正态区间, 须改用自助或专门修正法 —— 这是把置信度均值进一步用于分布层面推断时的具体高阶矩约束, 而非仅对点估计的泛泛提醒。在构念侧, 本家族所判别的「自主研发 vs 外部协同」轴根植于开放式创新研究传统, Laursen & Salter (2006) 以英国制造业企业的实证证据刻画了创新开放度这一战略谱系, 说明企业对外部协同来源的依赖广度与深度是可观测、可分类的战略选择, 从而为本置信度元测度所度量的「协同模式判别清晰度」锚定了顶刊层面的构念合法性——置信度高低正对应该战略轴上信号是否清晰可辨。综合看, 本家族在方法学上定位为「协同模式分类的信号强度元测度」, 与情感语调、创新占比等实体测度构念正交, 服务于稳健性与信号可信度诊断。

## VAR: avg_icm_confidence_ctx

【变体差分】
本列是 ctx 轨变体: 源文章级列 innovation_collab_mode_confidence_ctx 来自「标题 prepend + 实体上下文窗口」文本轨 (content_ctx), 即只保留银行与金科实体邻近窗口内的语境, 再交给 stage 21 三家 LLM 做协同模式判别并取多模型置信度均值, 最后在 (target_bank, year) 内取算术均值。相对家族 canonical (full 轨) 的差分维度是文本轨道: ctx 把判别语境收窄到实体窗口, 剔除全文中与银行金科无关的段落, 因而当报道主体明确聚焦某银行的具体协同 / 自研举措时, ctx 轨置信度往往比 full 更锐利; 而当窗口过窄丢失了协同关系的关键语境时, 也可能反而降低置信度。轨道口径上, ctx 是 conditional-on-full 的测度轨与稳健性轨: 其行宇宙是 full 留篇集 (llm_verified_full 为真) 的子集, 分母不与 full 混用, per-track 独立聚合。本列与 full / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 铁律是禁混进同一 over-identified Hansen J; 源列缺失时优雅置 NaN, 零新闻行按比例类保持 NaN 而非填零。在开发期 T=2 小样本上, ctx 轨可能出现覆盖稀疏导致的退化, 属预期现象, 生产期 T=19 语料上恢复正常。作为协同模式分类的信号强度元测度, 本列与 collab_frac 等协同占比列构念正交: 前者度量模型在「自主 vs 协同」轴上判得多清楚, 后者度量协同报道的占比多高, 二者不可互相替代, 也不可合并进同一识别方程。跨模型层面, 逐篇置信度由三家 LLM 聚合而来, 用意在于以多厂商平滑单一模型的过自信偏置; 与情感语调的跨模型稳健性梯子一样, 各家各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: avg_icm_confidence_full

【变体差分】
本列是 full 轨变体, 即家族 canonical 轨。源文章级列 innovation_collab_mode_confidence_full 来自「标题 prepend + 全文正文」文本轨 (content_full), 覆盖整篇报道的完整语义, 交给 stage 21 三家 LLM 判别「自主研发 vs 外部协同」并取多模型置信度均值, 再在 (target_bank, year) 内取算术均值落盘。相对 ctx / ss 两轨, full 轨的差分维度是文本范围最全: 它不裁剪语境, 因而当协同模式的判别线索散布在报道多个段落时, full 轨能整合全篇证据, 通常给出最稳定的判别置信度。轨道地位上, full 轨承载全项目 full-only 留篇门控 (2026-06-29) 的分母基准: 一篇是否算「银行金科报道」由 llm_verified_full 单独裁定, 因而 full 轨的行宇宙即留篇集本身, ctx / ss 两轨是其子集上的 conditional 测度。本列与 ctx / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 铁律是禁混进同一 over-identified Hansen J。作为协同模式分类的信号强度元测度, 本列与 collab_frac 等实体占比列构念正交: 前者刻画「模型判得多清楚」, 后者刻画「协同占比多高」, 二者不可互相替代, 也不可并入同一 over-identified Hansen J。作为最全语境轨, full 轨在解读上须结合 Geng et al. (2024) 关于 LLM 自报置信度常系统性过自信的告诫: 本列的均值只当作协同模式判别清晰度的相对代理, 不作绝对概率真值使用, 跨模型聚合与保守解读是其可信度保障。源列缺失优雅置 NaN, 零新闻行按比例类保持 NaN 而非填零; 在 T=2 开发期上覆盖稀疏可致退化, 生产期 T=19 语料恢复正常。

## VAR: avg_icm_confidence_ss

【变体差分】
本列是 ss 轨变体: 源文章级列 innovation_collab_mode_confidence_ss 来自「标题 prepend + 银行与金科同句 ±N 窗」文本轨 (content_ss), 即只在银行与金科实体严格同句共现的最窄语境上做协同模式判别, 再取多模型置信度均值并在 (target_bank, year) 内取算术均值。相对 full / ctx 两轨, ss 轨差分维度是判别语境最紧: 只有当银行与金科词落在同一句 (可扩 ±N 句半径, 见 config filtering 的 ss_sentence_radius) 时才纳入证据, 因而 ss 轨对「银行确实在做金科协同 / 自研」这一强共现信号最敏感, 但也最易因语境过窄而丢失判别线索。ss 轨的文本回退语义镜像 ctx: 当某篇无银行与金科同句共现时, content_ss 回退为全文正文并置 ss_is_fallback 为真, 与 ctx 的回退处理对称, 分母共享 n_articles 口径。轨道口径上 ss 是 conditional-on-full 的测度轨与稳健性轨, 行宇宙是 full 留篇集子集, per-track 独立聚合不与 full / ctx 混分母。本列与 full / ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 铁律是禁混进同一 over-identified Hansen J。在 T=2 开发期上 ss 轨可能出现零方差或高缺失退化, 属预期, 生产期 T=19 恢复; 源列缺失优雅置 NaN, 零新闻行保持 NaN。作为协同模式分类的信号强度元测度, 本列与 collab_frac 等协同占比列构念正交, 度量的是判别清晰度而非协同强度, 二者不可互相替代, 也不可并入同一识别方程。ss 轨的强共现口径使其成为 full 轨的严格稳健性对照: 当结论在最窄同句语境上仍稳健时, 说明协同模式判别不依赖于宽语境噪声; 当 ss 与 full 分歧时, 分歧本身即诊断信号, 提示协同线索是否高度依赖跨句语境。

<!-- rendered-citations:begin -->
Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration in large language models. Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), 6577-6595. https://doi.org/10.18653/v1/2024.naacl-long.366
Wright, D. B., & Herrington, J. A. (2011). Problematic standard errors and confidence intervals for skewness and kurtosis. Behavior Research Methods, 43(1), 8-17. https://doi.org/10.3758/s13428-010-0044-x
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML), 625-632. https://doi.org/10.1145/1102351.1102430
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131-150. https://doi.org/10.1002/smj.507
<!-- rendered-citations:end -->
