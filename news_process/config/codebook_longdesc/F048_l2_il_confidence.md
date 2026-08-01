---
family_id: F048
columns:
- avg_il_confidence_ctx
- avg_il_confidence_full
- avg_il_confidence_ss
unit: 分类置信度均值 (无量纲, 逐篇取值域 [0, 1] 后按银行-年求算术平均)
formula: "article: innovation_locus_confidence{track} = mean_over_models_with_nonNone_locus_label({short}_innovation_locus_confidence); panel: avg_il_confidence{track} = mean_over_bank_year(innovation_locus_confidence{track}); track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/encode.py::aggregate_panel (il 短名三轨 groupby mean, encode.py:1662-1678; 逐篇上游 news_process/pipeline/sentiment/tone_llms.py::_avg_innovation_confidence)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (innovation_locus_confidence_full / _ctx / _ss)
citations:
- doi: 10.1016/j.intfin.2026.102325
  type: journal
  authors: Chen, K., Granville, B., & Matousek, R.
  year: 2026
  title: "Decoding central bank communications with large language models"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 109
  pages_or_artno: 102325
- doi: 10.1016/j.econlet.2025.112803
  type: journal
  authors: Aksoy-Yurdagul, D., Buchner, A., & Zareei, A.
  year: 2026
  title: "The persistence of news sentiment: Implications for return predictability"
  venue: Economics Letters
  vol: 260
  pages_or_artno: 112803
- doi: 10.1002/jae.3095
  type: journal
  authors: Bodilsen, S. T., & Lunde, A.
  year: 2025
  title: "Exploiting news analytics for volatility forecasting"
  venue: Journal of Applied Econometrics
  vol: 40
  issue: 1
  pages_or_artno: 18-36
- doi: 10.1007/s13278-024-01270-5
  type: journal
  authors: Khan, M. H., Hasan, A. B., & Anupam, A.
  year: 2024
  title: "Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms"
  venue: Social Network Analysis and Mining
  vol: 14
  issue: 1
  pages_or_artno: 110
- doi: 10.1002/047174882X
  type: book
  authors: Cover, T. M., & Thomas, J. A.
  year: 2006
  title: "Elements of information theory (2nd ed.)"
  venue: Wiley-Interscience
- doi: 10.1002/smj.3586
  type: journal
  authors: Miller, C. D., & Wang, R. D.
  year: 2024
  title: "Product digitization and differentiation strategy change: Evidence from the book publishing industry"
  venue: Strategic Management Journal
  vol: 45
  issue: 7
  pages_or_artno: 1241-1272
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是「创新位置 (innovation locus) 分类置信度」在银行-年层面的均值, 记为 avg_il_confidence。这里的「创新位置」是本项目自定义的离散分类构念, 承袭金融科技研究中常见的「底层技术 (technology) 对应用场景 (application)」两分视角: 一篇涉及目标银行与金融科技的报道, 究竟是在讲「底层技术」(如分布式账本、云计算、人工智能内核) 还是在讲「应用场景」(如支付、信贷、财富管理的落地), 构成 innovation_locus 这一离散分类构念。该技术-应用两分是本测度框架的分析性设定, 与 innovation_substantiveness (实质性) 及 innovation_collab_mode (协作模式) 两维度正交并列, 三者共同由阶段 21 的多模型 LLM 判定。avg_il_confidence 不是该分类的标签本身 (标签比例族另有 tech_frac 等列承载), 而是分类器对自身判定的把握程度, 即「信号强度」维度。它回答的是一个正交于「判成什么类」的问题: 模型对该篇报道落在哪一层「有多确定」。把握程度高, 说明报道文本对技术-应用归属提供了清晰、非歧义的线索; 把握程度低, 说明报道语义模糊、技术与应用交织或线索稀薄。因此本家族本质上是一个逐篇分类质量/文本清晰度的代理, 而非情感或态度测度, 也不进入任何极性 (正负面) 语义空间。

【方法学与计算】
计算链路分两级。逐篇一级: 在阶段 21 (tone_llms) 中, 三家 LLM (gpt54nano、gemini31、deepseekv4) 各自对报道给出 innovation_locus 标签及其自报的 verbalized confidence (语言化置信度) ∈ [0, 1]; 逐篇的 innovation_locus_confidence{track} 由 _avg_innovation_confidence 计算, 取那些「该维度标签非 None (即落入 canonical 接受集)」的模型所报置信度的算术均值, 并进一步剔除数值 ≤ 0 的项, 无有效项时置 0.0。这一「聚合域与标签聚合域对齐」的口径是刻意的: 若某模型判该维度为 false/标签为 null 却仍 emit 一个置信度数字, 该数字不得混入均值, 否则分子 (标签投票) 与信号强度将来自不同的模型子集。银行-年二级: 在 encode.py 的面板聚合中, 对每一 (target_bank, year) 组内的逐篇 innovation_locus_confidence{track} 求算术平均, 落为 avg_il_confidence{track}。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否被计入银行金科报道宇宙, 只看 full 轨的 llm_verified_full 判定; ctx 与 ss 轨降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 置信度列仍逐轨独立计算。零新闻的银行-年格保持 NaN, 与其它比例/均值类列一致。

【文献定位】
本测度植根于两条文献脉络。其一是大语言模型对金融文本的分类与其可信度评估: Chen、Granville 与 Matousek (2026) 展示了 LLM 在解码央行沟通这类高度专业金融文本上的判别能力与不确定性刻画, 为「以 LLM 自报置信度作为分类质量代理」提供了直接方法学背书。其二是新闻文本信号的构造与聚合传统: Bodilsen 与 Lunde (2025) 论证了新闻分析信号在波动率预测中的增量价值, Aksoy-Yurdagul、Buchner 与 Zareei (2026) 则揭示新闻情感信号具有跨期持续性并影响收益可预测性 — 二者共同说明由逐篇文本派生、再按实体-时间聚合的信号 (本家族正属此类) 在资产定价与银行研究中是可操作的构念。Khan、Hasan 与 Anupam (2024) 对硅谷银行事件的机器/深度学习分类研究进一步印证: 在银行语境下, 文本分类器的置信/概率输出本身携带可用于下游的信息。就「创新位置」这一技术-应用两分构念的实质合法性而言, Miller 与 Wang (2024) 在顶刊层面论证了产品数字化 (即底层技术向应用形态的迁移) 会系统性重塑企业的差异化战略, 为「区分一篇报道落在底层技术层还是应用场景层」这一分类维度提供了战略管理文献的构念背书 — 技术与应用不是同义反复, 而是承载不同战略含义的两个可分离层面。最后, 把「置信度」理解为「不确定性的减少量」这一视角可回溯至 Cover 与 Thomas (2006) 的信息论框架: 高置信度对应低条件熵、清晰的类别归属, 低置信度对应高熵、语义含混, 从而将本测度与文本清晰度/可读性研究的构念空间对接。

## VAR: avg_il_confidence_full

【变体差分】
本列为 full 轨。full 轨的文本来源是「标题 prepend + 全文正文」(content_full), 由阶段 14 (ctx_materializer) 物化, 覆盖报道的完整语义信息。full 轨在本三轨体系中具有 canonical 与门控双重地位: 留篇门控 (full-only, 2026-06-29) 仅以 llm_verified_full 判定报道是否进入银行金科报道宇宙, 因此 avg_il_confidence_full 的银行-年行宇宙即为留篇集本身, 而非其子集。逐篇上游列 innovation_locus_confidence_full 在最完整的文本证据上计算, 三家 LLM 可读到标题与全部正文, 通常能获得最充分的技术-应用归属线索, 故本列相对 ctx/ss 轨往往覆盖更多有效篇、置信度基础更厚实。需强调本列是「信号强度」而非「标签」: 一篇被高置信度归入应用场景的报道, 与另一篇被同等置信度归入底层技术的报道, 在本列上贡献相同, 因为本列只累加分类器对自身判定的把握度, 不承载技术-应用的方向信息; 方向信息由 tech_frac 等比例族独立承载, 二者构念正交, 不可互替。同理, 本列高不等于该银行金科创新活跃, 只表示涉该银行的报道在技术-应用归属上文本线索清晰、语义低歧义。本列与 avg_il_confidence_ctx、avg_il_confidence_ss 构成三轨规格稳健性: 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁将三轨列混入同一 over-identified 的 Hansen J 过度识别检验; 三轨应各自进入独立的自回归/识别式, 以证主结论不被单一文本窗口口径驱动。零新闻银行-年格保持 NaN。

## VAR: avg_il_confidence_ctx

【变体差分】
本列为 ctx 轨。ctx 轨的文本来源是「标题 prepend + 实体上下文窗口」(content_ctx): 仅保留目标银行实体附近的语义窗口, 而非全文, 由阶段 14 物化。相较 full 轨, ctx 轨主动裁剪掉与目标银行实体距离较远的段落, 目的是压制无关噪声、把分类判据聚焦到确实围绕该银行展开的叙事上; 代价是可能丢弃分散在正文别处的技术-应用线索, 从而使部分报道的 innovation_locus 归属线索变稀、逐篇置信度承压。作为门控口径下的 conditional-on-full 测度轨, ctx 轨的银行-年行宇宙是 full 留篇集的子集, 但 innovation_locus_confidence_ctx 仍逐轨独立由 _avg_innovation_confidence 在 ctx 文本上计算, 分母不借用 full 轨。本列相对 canonical 的 full 轨是首要稳健性轨: 它检验「把证据窗口收紧到实体上下文」是否改变分类把握度的银行-年画像。其识别价值在于隔离一种潜在混淆: 若 full 轨的高置信度部分来自与目标银行无关的、但技术-应用主题鲜明的旁支段落, 那么裁剪到实体窗口后置信度应显著回落; 若 ctx 与 full 画像接近, 则说明分类线索确实锚定在围绕该银行的叙事上, 主结论更稳健。逐篇 innovation_locus_confidence_ctx 仍遵循 _avg_innovation_confidence 的对齐口径 — 仅纳入该维度标签非 None 的模型所报置信度, 剔除非正值, 无有效项置 0.0。本列与 full/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。零新闻或该轨无有效篇的银行-年格保持 NaN。

## VAR: avg_il_confidence_ss

【变体差分】
本列为 ss 轨 (same-sentence, 同句共现轨)。ss 轨的文本来源是「标题 prepend + 银行与金融科技同句共现的 ±N 句窗口」(content_ss, 窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语义窗口最紧的一轨, 只保留目标银行与金融科技词在同一句 (及其邻句) 同现的最强证据片段。ss 轨的回退语义镜像 ctx: 当报道中不存在银行与金融科技的同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母口径; 若上游金融科技 AC 词典缺失 (FINTECH_AC=None), 则整轨 *_is_fallback 全 True 优雅降级。因此 avg_il_confidence_ss 在最严格的共现证据下刻画分类把握度: 命中同句共现的报道通常技术-应用主题最聚焦、置信度可能更高, 而大量回退篇则使本轨向 full 轨口径靠拢。本列同为 conditional-on-full 稳健性轨, 银行-年行宇宙为留篇集子集, innovation_locus_confidence_ss 逐轨独立计算不借 full 分母。本列与 full/ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。与 ctx 轨检验「实体邻近性」不同, ss 轨进一步检验「银行与金融科技是否在同一语义单元内被共同提及」这一更强的相关性判据: 只有当技术-应用讨论确实与目标银行同句绑定时, 才被视为最纯净的分类证据; 大量回退篇的存在则天然把本轨拉回 full 轨口径, 使 ss 成为「最严格判据」与「全文兜底」之间的连续谱。逐篇 innovation_locus_confidence_ss 同样遵循标签对齐的置信度均值口径, 逐轨独立计算。早期试跑 T=2 小样本上, ss 轨因回退比例与共现稀疏可能出现较多 NaN 或退化取值, 属预期现象, 生产期 T=19 恢复正常。

<!-- rendered-citations:begin -->
Chen, K., Granville, B., & Matousek, R. (2026). Decoding central bank communications with large language models. Journal of International Financial Markets, Institutions and Money, 109, 102325. https://doi.org/10.1016/j.intfin.2026.102325
Aksoy-Yurdagul, D., Buchner, A., & Zareei, A. (2026). The persistence of news sentiment: Implications for return predictability. Economics Letters, 260, 112803. https://doi.org/10.1016/j.econlet.2025.112803
Bodilsen, S. T., & Lunde, A. (2025). Exploiting news analytics for volatility forecasting. Journal of Applied Econometrics, 40(1), 18-36. https://doi.org/10.1002/jae.3095
Khan, M. H., Hasan, A. B., & Anupam, A. (2024). Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms. Social Network Analysis and Mining, 14(1), 110. https://doi.org/10.1007/s13278-024-01270-5
Cover, T. M., & Thomas, J. A. (2006). Elements of information theory (2nd ed.). Wiley-Interscience. https://doi.org/10.1002/047174882X
Miller, C. D., & Wang, R. D. (2024). Product digitization and differentiation strategy change: Evidence from the book publishing industry. Strategic Management Journal, 45(7), 1241-1272. https://doi.org/10.1002/smj.3586
<!-- rendered-citations:end -->
