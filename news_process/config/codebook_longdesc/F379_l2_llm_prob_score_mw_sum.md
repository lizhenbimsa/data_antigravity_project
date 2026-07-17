---
family_id: F379
columns:
- llm_prob_score_mw_sum_ctx
- llm_prob_score_mw_sum_full
- llm_prob_score_mw_sum_ss
unit: 媒体权威性加权的 Logit-to-Score 共识概率语调银行-年累加和 (无量纲, 未除权分子)
formula: 'llm_prob_score_mw_sum{track} = Σ_{a∈bank-year} [ llm_prob_score_a × media_authority_weight_a ]; 其中 llm_prob_score_a = compute_prob_score(sentiment_label_a, confidence_a) = P(正面)_a − P(负面)_a ∈ [-1,+1] 由三家 LLM 多数决共识标签 (llm_vote) 与共识置信度按 Logit-to-Score 概率映射得到 (主类概率取 confidence_a, 剩余概率按最大熵原理在非主类间均分 (1-confidence_a)/2); media_authority_weight_a 为该篇报道所属媒体来源的权威性权重 (runner 步骤 3c, 缺失回退 1.0); {track}∈{_full,_ctx,_ss}。本列是未归一化分子, 对应归一化度量需除以同轨掩码媒体权威权重和 sum_wd_mw_prob{track} (仅计入 llm_prob_score 非缺失文章的权重, 缺列回退物理和 sum_media_authority_weight{track})'
producer: 'news_process/pipeline/sentiment/tone_llms.py::compute_prob_score (阶段 21, Logit-to-Score 概率映射计算); news_process/pipeline/panel/runner.py (步骤 3c: llm_prob_score × media_authority_weight → llm_prob_score_mw, 并经 _build_llm_valid_masked_weights 建配套掩码分母 _wd_mw_prob{track}); news_process/pipeline/panel/encode.py::_build_panel_aggregations (groupby sum → llm_prob_score_mw_sum{track})'
upstream:
- 21_tone_llms.parquet (三家 LLM 多数决共识 sentiment/confidence/verified 三轨)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
- runner 步骤 3c media_authority_weight (媒体权威性权重)
citations:
- doi: 10.48550/arXiv.2412.07031
  type: wp
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: NBER Working Paper No. 33344
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: "105227"
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.2139/ssrn.4412788
  type: wp
  authors: Lopez-Lira, A., & Tang, Y.
  year: 2023
  title: "Can ChatGPT forecast stock price movements? Return predictability and large language models"
  venue: SSRN Working Paper
- doi: "10.48550/arxiv.2207.05221"
  type: "arxiv"
  authors: "Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., ... Kaplan, J."
  year: 2022
  title: "Language Models (Mostly) Know What They Know"
  venue: "arXiv"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"多数决共识"语调经 Logit-to-Score 概率映射后, 再按媒体权威性加权的银行-年累加和, 即最终归一化度量的未除权分子。列名骨架为 llm_prob_score_mw_sum{track}, {track} 取 full、ctx、ss 三条文本轨, 三列即三轨的笛卡尔积; 与 F170 等家族的 {short}_cont_mw_sum 不同, 本家族不区分单一模型, 而是取三家 LLM (GPT-5.4-nano、Gemini-3.1-flash-lite、DeepSeek-V4-flash) 多数决之后的共识标签 llm_vote 及其共识置信度作为唯一输入, 因而是"稳健性检验"轨而非跨厂商三角验证轨: 目的是提供一种独立于逐词典/逐模型离散极性编码的替代连续化路径。构念上, llm_prob_score 由 tone_llms.compute_prob_score 实现, 其学理依据是 Ludwig、Mullainathan 与 Rambachan (2025) 提出的把 LLM 分类输出纳入应用计量框架、系统处理其作为测量工具时的统计性质的方法论路径, 以及 Kirtac 与 Germano (2024, 《Finance Research Letters》) 关于以 LLM 连续化情感分数替代离散极性标签用于市场应用的实证论证: 二分类或三分类的离散极性标签会人为压缩语调强度信息, 使得两篇同判"负面"但确信程度悬殊的报道在下游回归中被等同对待, 而本家族的 Logit-to-Score 映射通过把模型自报的置信度嵌入映射函数, 保留了这一强度维度。具体映射规则是: 令共识标签的主类概率等于共识置信度 confidence, 其余两类的概率按最大熵原理在非主类间均分 (1-confidence)/2 (信息熵最大化原理下, 在已知主类概率约束下的唯一无偏解), 再取正面类概率减负面类概率, 得到 llm_prob_score = P(正面) − P(负面) ∈ [-1, +1]。mw 指媒体权威性加权 (media-authority weighted): 每篇报道的 llm_prob_score 再乘以其所属媒体来源的权威性权重, 让权威大报的连续语调在银行-年汇总中获得更高话语权, 这一处理呼应 Fang 与 Peress (2009) 以及 Tetlock (2007) 记录的媒体覆盖显著性对资本市场定价的非对称影响, 亦是本项目 VW (提及密度)/MW (媒体权威)/HW (跟风衰减) 三套加权族对全测度族的统一施加惯例之一。sum 指该银行-年内所有留篇报道上述加权连续语调的算术累加, 是一个尚未除以权重总和的分子而非可直接横向比较的均值。

【方法学与计算】
计算链路分三级严格上溯。第一级在阶段 21 (tone_llms) 得到三家 LLM 逐篇逐轨的独立情感标签与自报置信度, 再由 majority_vote_categorical 汇总为共识标签 llm_vote (multi-model consensus, 而非任一单模型), 并给出共识置信度; 第二级由 compute_prob_score 把共识标签与共识置信度映射为 llm_prob_score ∈ [-1,+1] (主类概率=confidence, 其余两类均分 (1-confidence)/2, 取正面概率减负面概率)。须提示的是, compute_prob_score 的输出是"序数代理变量" (ordinal proxy) 而非经过校准的真实概率: verbalized confidence 已知存在系统性过度自信倾向, 保序性基本成立但绝对水平不宜直接解读为频率概率, 这一局限在阶段 21 源码注释中明确声明并沿袭到本家族。第三级由 runner 步骤 3c 施加媒体权威性权重: llm_prob_score_mw{track} = llm_prob_score{track} × media_authority_weight (权重缺失回退 1.0), 再经 encode.py 的面板聚合按银行-年 groupby 求和得到本家族 llm_prob_score_mw_sum{track}。与 F170 系列的连续语调分子一致, 本家族本身也是未归一化分子: 对应的、面板已物化的归一化度量并非直接由本列除以物理权重和, 而是须除以同轨的 valid-mask 掩码媒体权威权重和 sum_wd_mw_prob{track} (由 _build_llm_valid_masked_weights 在 encode-01 修复中建立, 仅累计 llm_prob_score 非缺失文章的权重, 缺该掩码列时才回退物理和 sum_media_authority_weight{track}); 这一 valid-mask 设计的动机是防止把"共识置信度或标签缺失"的文章在分母端计入满权重, 从而系统性把加权语调压向 0。共识标签本身的产生要求三家模型至少形成多数, 若三家彻底分歧或空票, llm_vote 及其下游 llm_prob_score 按 undefined/conservative 策略处理为缺失, 该篇不进入本列分子也不进入掩码分母, 自然沿 NaN 语义传播。留篇门控遵循 2026-06-29 起的 full-only 口径: 一篇报道是否算作"一篇银行金科报道"只看 llm_verified_full, 三轨共享同一 full 留篇集所定义的行宇宙, ctx 与 ss 是 conditional-on-full 的子集测度, 各轨照常独立计算; ss 轨在无银行与金科同句共现时镜像 ctx 回退到全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母口径, 缺 content_ss 列时进一步优雅回退 content_full。⚠ 铁律: full、ctx、ss 三条文本轨各自 just-identified 并排, 互为稳健性不分主次, 严禁把不同轨混进同一 over-identified 的 Hansen J 过度识别检验; 本家族的"共识 Logit-to-Score"与 F170 等家族的"逐模型连续语调"亦是两条互不可加合并、并排比较的稳健性路径, 不应在同一设定内混用。

【文献定位】
本家族方法学上坐落于"把 LLM 离散分类输出转成连续强度指标"这一新兴脉络。Ludwig、Mullainathan 与 Rambachan (2025) 提出的把 LLM 输出作为测量工具纳入应用计量框架的路径, 是本家族把共识标签与置信度映射为连续 Logit-to-Score 的方法学来源; Kirtac 与 Germano (2024) 发表于《Finance Research Letters》的 LLM 情感交易研究, 为"连续型语调优于离散极性标签"这一构念选择提供了实证支撑, 也是本项目在词典/BERT/LLM 三种情感测度手段中始终并置连续化分支的共同引用锚点之一。Gilardi、Alizadeh 与 Kubli (2023) 在《美国科学院院刊》(PNAS) 的顶刊证据表明 ChatGPT 类模型在文本标注任务上可超越众包工人, 为以 LLM 自报置信度作为标注确信度的序数代理变量提供了效度基础, 支撑本家族把 verbalized confidence 纳入概率映射而非弃之不用。de Kok (2025) 关于生成式 LLM 用于会计研究的操作规范讨论了 temperature=0 与 prompt 冻结等可复现性实践, 与本项目阶段 21 的确定性缓存架构一致, 说明本家族的共识置信度输入本身具备跨-run 可复现的方法学基础。Lopez-Lira 与 Tang (2023) 关于 ChatGPT 预测股价走势的早期实证, 则从应用侧印证了 LLM 连续化情感指标 (而非纯离散标签) 在金融市场预测力上的增量价值, 呼应本家族作为主离散语调族之外一条独立稳健性轨的定位。 在"LLM 自报置信度可当作概率量"这一前提上, 更早的 Kadavath 等 (2022) 提供了奠基性证据: 该文系统研究语言模型能否自评其答案的正确性, 证明较大模型在格式恰当的多选/判断题上校准良好, 报告了性能、校准与规模效应, 并据此提出先给答案再自评 P(True) 的自评范式, 另研究了无需特定候选答案的 P(IK) 预测, 为本家族把共识置信度送入 compute_prob_score 得到 P(正面)−P(负面) 连续分、再作媒体权威性加权求和提供了一般性支持。其迁移边界须明确: 该文并非本家族做法的方法出处 — 原文自评经由专门的 P(True)/P(IK) 探针与 logit 读数, 本项目 confidence 则取自 prompt 结构化输出字段 (verbalized confidence 一线); 其模型代次为 2022 年的内部模型, 与本项目三家生产模型不可比; 原文亦只到"自评概率具备校准性"为止, 并未提出把剩余概率 (1−confidence) 在非主类间按最大熵均分再作差的映射, 该映射与其后的 media_authority_weight 加权求和均属研究者选择, 非原文成果。
## VAR: llm_prob_score_mw_sum_ctx

【变体差分】
本列是共识 Logit-to-Score 概率语调在 ctx (上下文片段) 轨上的媒体权威性加权银行-年累加和。文本轨维度上, ctx 轨输入 content_ctx, 即标题 prepend 后再取含目标银行别名命中句前后各配置窗口 (context_window.sentence_radius, 默认 1 句) 扩展合并的实体邻近片段, 短文本退化为字符级窗口; 相对 full 轨, ctx 轨压缩了与银行实体无关的段落噪声, 使三家模型的共识判定更集中于目标银行周边语境, 因此 llm_prob_score_ctx 反映的是"实体邻近语境下"的共识置信映射语调而非整篇总体印象。该轨的共识标签与置信度仍来自三家 LLM 在 ctx 轨的独立判定经多数决汇总, 若三家在该轨的判定彻底分歧, 本篇的 ctx 轨共识及其下游 llm_prob_score_ctx 置缺失, 与 full/ss 两轨的共识结果相互独立 (逐轨独立多数决, 非跨轨共享)。作为未归一化分子, 本列须除以同轨掩码权重和 sum_wd_mw_prob_ctx (仅计入 llm_prob_score_ctx 非缺失文章的媒体权威权重, 缺该掩码列时回退物理和 sum_media_authority_weight_ctx) 方可得到可横向比较的加权均值; 单独读取本列绝对量意义有限, 银行覆盖篇数越多、分子累加值天然越大。留篇门控仍是 full-only, 本列在 full 留篇子集上按 conditional-on-full 口径逐轨计算, 度量的是"已判为银行金科报道的样本中, 三家共识在实体邻近语境下的概率映射语调加权总量"。⚠ 铁律: 本列与 full、ss 两轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified Hansen J; 亦不应与 F170 等逐模型连续语调家族的对应轨合并入同一过度识别设定。

## VAR: llm_prob_score_mw_sum_full

【变体差分】
本列是共识 Logit-to-Score 概率语调在 full (全文) 轨上的媒体权威性加权银行-年累加和, 是三条轨中的 canonical 留篇轨。文本轨维度上, full 轨输入 content_full 为标题 prepend 后拼接的整篇正文, 信息最全、噪声也最高, 并且是全项目留篇门控的判定基准: 一篇报道是否算作银行金科报道完全取决于 llm_verified_full 是否为真, 因而 full 轨既定义行宇宙又充当自身的一条度量轨。本列的共识标签与置信度取自三家 LLM 在 full 轨的独立判定经多数决汇总, 再经 compute_prob_score 映射为 llm_prob_score_full ∈ [-1,+1], 乘媒体权威性权重后银行-年求和得本列。作为未归一化分子, 若需可比较的加权均值须除以同轨掩码权重和 sum_wd_mw_prob_full (仅计入 llm_prob_score_full 非缺失文章的权重, 缺列回退物理和 sum_media_authority_weight_full)。相对 ctx 与 ss 两条更聚焦语境的稳健性轨, full 轨语义最宽, 最贴近"整篇报道对该银行金科议题的总体共识语调倾向", 也因覆盖最全的样本而通常拥有最少的因判据过严导致的缺失或回退。与 F170 系列的 {short}_cont_mw_sum_full (逐模型连续语调) 相比, 本列的差异在于输入不是任一单模型的自身标签与置信度, 而是三家多数决之后的共识标签与共识置信度, 二者互为方法学上独立的稳健性路径, 均不应互相替代或合并入同一识别设定。⚠ 铁律: full、ctx、ss 三轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。本列为未归一化分子, 供审计追溯分子分母是否配对生成及支撑替代归一化方案, 一般不单独直接进主回归。

## VAR: llm_prob_score_mw_sum_ss

【变体差分】
本列是共识 Logit-to-Score 概率语调在 ss (银行与金科同句共现) 轨上的媒体权威性加权银行-年累加和, 是三轨中判据最严的一条。文本轨维度上, ss 轨输入 content_ss, 即标题 prepend 后仅保留同一句内同时出现目标银行别名与金科词的句子并按窗口扩展合并的最严片段, 用以隔离出银行与金融科技被真正并置讨论的语境; 其回退语义镜像 ctx: 当整篇无银行与金科同句共现时, content_ss 回退为全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母口径, 缺 content_ss 列时进一步优雅回退 content_full。本列的共识标签与置信度来自三家 LLM 在 ss 轨的独立判定经多数决汇总, 再映射为 llm_prob_score_ss, 乘媒体权威性权重后银行-年求和得本列; 作为未归一化分子, 须除以同轨掩码权重和 sum_wd_mw_prob_ss (仅计入 llm_prob_score_ss 非缺失文章的权重, 缺列回退物理和 sum_media_authority_weight_ss) 方可得到可横向比较的加权均值。留篇门控仍是 full-only, 本列是 conditional-on-full 的最严子集测度, 度量的是"最贴近研究构念的银行金科同句共现语境下, 三家共识的概率映射语调加权总量"。因判据最严, 开发期 T=2 小样本上该轨容易出现较多回退与零方差退化, 属预期行为, 生产期长面板 (T=19) 恢复正常; 解释本列时应结合 ss_is_fallback 占比判断该轨真正体现同句共现语境的程度, 避免误读为 ctx 的近似替代。⚠ 铁律: ss 与 full、ctx 两轨各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified Hansen J; 亦不应与逐模型连续语调家族 (F170 等) 的对应轨合并比较水平。

<!-- rendered-citations:begin -->
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. NBER Working Paper No. 33344 [Working Paper]. https://doi.org/10.48550/arXiv.2412.07031
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.4412788
Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., ... Kaplan, J. (2022). Language Models (Mostly) Know What They Know. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2207.05221
<!-- rendered-citations:end -->
