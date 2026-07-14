---
family_id: F213
columns:
- du_2022_cater_ctx
- du_2022_cater_full
- du_2022_cater_ss
unit: 语调差分 (无量纲; 两个 [-1,1] 归一化语调之差, 取值约 [-2,2])
formula: "du_2022_cater{track} = du_2022_tone{track} - llm_vote_tone{track}; 正值 → du_2022 词典侧比三家 LLM 共识更正面 (潜在算法迎合)"
producer: news_process/pipeline/panel/runner.py (步骤 8d 算法迎合度, 情形 B 单词典 vs 综合 LLM); 上游 du_2022_tone 由 pipeline/sentiment/tone_words.py 产, llm_vote_tone 由 pipeline/sentiment/tone_llms.py 产; 标签见 pipeline/panel/export.py
upstream:
- 22_tone_words.parquet (du_2022_tone{track})
- 21_tone_llms.parquet (llm_vote_tone{track})
- 40_panel_yearly.parquet
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1016/j.enpol.2023.113917
  type: journal
  authors: Xu, Z., Li, J., Hua, X., & Ren, P.
  year: 2024
  title: "Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry"
  venue: Energy Policy
  vol: 184
  pages_or_artno: 113917
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.18653/v1/d16-1057
  type: wp
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是"算法迎合度"(algorithmic catering) 的一个单词典切面: 以 Du 等人 (2022) 构建的中文金融情感词典对同一批银行金科报道所打出的机器可读语调, 减去三家大语言模型对同一文本的共识语调, 所得差值即 du_2022_cater。其构念直觉是: 词典打分是一套公开、固定、可被撰稿方预先获知的极性规则, 而深层语言模型 (无论是 LLM 还是 BERT) 捕捉的是超越逐词极性的语境语义。当信息发布方知道下游读者中有大量"机器读者"在用词典类工具抓取语调时, 存在一种策略性动机: 堆砌词典正面词、规避词典负面词, 从而在词典口径上显得更乐观, 却未必改变经语境理解后的真实语气。这一差值若系统性为正, 即提示存在朝向词典规则的语言迎合。该构念的开创性证据来自 Cao 等人 (2023) 在算法交易与信息披露语境下的研究: 当机器成为主要读者时, 企业会调整其文本以迎合可被算法识别的模式; 本列把这一"人-机语调楔子"落到银行金科报道的面板测量上, 用词典侧减深层模型侧的方式把楔子显性化。

【方法学与计算】
计算在面板构造阶段 (runner.py 步骤 8d, 情形 B「单词典 vs 综合深层模型」) 完成, 是纯后处理差分, 不额外调用任何付费 API。被减数 du_2022_tone{track} 是 Du 等 (2022) 词典在阶段 22 上算出的净语调 (正面加权词数减负面词数, 再对总极性词数归一化, 落在约 [-1,1]); 其中 du_2022 独有的 political_positive (1,434 词) 以 0.5 权重计入正侧, 即本列被减数采用的是政治词权重 canonical 口径 (polw05)。减数 llm_vote_tone{track} 是三家大模型 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 多数投票得出的共识语调, 亦归一化到同一量纲。两者相减得到无量纲的语调差分, 取值理论区间约 [-2,2], 正值表示 Du 词典比 LLM 共识更正面。三个后缀 _full / _ctx / _ss 分别对应全文轨 (标题 prepend 加正文)、实体窗轨 (标题加银行与金科实体邻近窗口)、同句轨 (标题加银行与金科同句共现窗口), 三轨的被减数与减数均严格逐轨取用, 不跨轨借数。留篇口径遵循 2026-06-29 的 full-only 门控: 一篇报道是否计入"银行金科报道"只由 full 轨的 LLM 判定决定, ctx 与 ss 轨在此基础上是 conditional-on-full 的子集测度。

【文献定位】
在测量方法谱系上, 本列站在"词典法与深层模型法互为参照"的交叉点。词典法一脉自 Du 等 (2022) 发表于 Review of Finance 的中文金融情感词典, 强调语言与领域特异性: 直接移植英文 Loughran-McDonald 词典到中文金融文本会系统性失真, 需本土化重建极性词表并识别政治正面词等中国制度语境特有类别。近年这一脉持续细化, 如 Ma 等 (2025) 构建面向中国境内投资者的细粒度情感词典 CN-FSD, Sun 等 (2025) 将词典知识与中性特征注入预训练语言模型以弥合规则与语义两法, Hamilton 等 (2016) 则从无标注语料自动归纳领域情感词表。深层模型一脉与词典法的语义差恰是本列所要捕捉的信号。Cao 等 (2023) 发表于 Review of Financial Studies 的研究提供了迎合动机的因果证据: 机器读者份额上升会诱发披露文本向算法可识别模式漂移。Xu 等 (2024) 进一步表明官方媒体语调本身对资本市场有价值, 提示语调测量的口径选择 (词典抑或模型) 会实质影响下游推断, 因而以两法之差作为迎合的显性代理具有识别意义。三轨设定属规格稳健性并排: 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified 的 Hansen J。

## VAR: du_2022_cater_full

【变体差分】
本列为全文轨 (_full) 的 du_2022 迎合度。被减数 du_2022_tone_full 在标题 prepend 后的完整正文上计算 Du 等 (2022) 词典净语调, 减数 llm_vote_tone_full 为三家 LLM 在同一全文文本上的共识语调, 两者相减即本列。相对家族内另两轨, full 轨的独特地位在于它是留篇门控的唯一裁决轨 (2026-06-29 full-only 口径): 某篇报道是否被判为一篇"银行金科报道"仅取决于该篇 full 轨的 LLM 判定, 因此 full 轨行宇宙是全集, ctx 与 ss 轨的行宇宙是它的子集。这意味着 full 轨迎合度的分母 (进入年度聚合的报道集) 最完整, 度量噪声相对最低, 通常作为该家族的首要报告轨; ctx 与 ss 则作为 conditional-on-full 的语境收窄稳健性轨。文本通道上 full 轨采用标题加全文正文, 语料覆盖最广, 因而词典侧与模型侧都在信息量最大的文本上打分, 二者之差最能反映撰稿方在整篇文本层面对词典规则的系统性迎合而非局部片段效应。需强调的是, 本列的被减数固定采用 du_2022 政治词权重 canonical 口径 (political_positive 以 0.5 权重计入正侧), 而非政治词权重梯子的 polw00 或 polw10 变体, 因此本列度量的迎合仅在该单一权重取值下定义; 若需检验迎合结论对政治词权重的敏感性, 应另在 du_2022_score_polw 系列上重算, 二者正交不交叉。就识别口径而言, 本列与 du_2022_cater_ctx、du_2022_cater_ss 两轨各自 just-identified 并排、互为稳健性不分主次, 三轨严禁混入同一 over-identified Hansen J 过度识别检验。

## VAR: du_2022_cater_ctx

【变体差分】
本列为实体窗轨 (_ctx) 的 du_2022 迎合度。与 full 轨的唯一差别在文本通道: 被减数 du_2022_tone_ctx 与减数 llm_vote_tone_ctx 都在实体窗文本 content_ctx 上计算, 即标题 prepend 后, 正文只保留银行与金科实体邻近窗口内的句子, 而非整篇。其构念意图是把迎合度的测量收窄到真正谈及目标银行金科业务的语境, 剔除与主题无关的段落对词典计数与模型语义的稀释, 从而更贴近"就该银行金科事项的语气迎合"这一更严格的构念。相对 full 轨, ctx 轨在 full-only 门控下是 conditional-on-full 的稳健性轨: 行宇宙为 full 留篇集的子集, 但 per-track 的词典侧与模型侧仍严格在 ctx 文本上各自计算, 不向 full 借用分子分母。由于窗口收窄, 单篇可用极性词与语境线索变少, 在浅面板 (如 T=2 开发样本) 上该轨方差可能收缩甚至退化, 属预期现象, 生产全样本 (T=18) 下恢复正常。与 full 轨相比, ctx 轨的迎合信号更能排除一种混淆: 撰稿方可能在整篇文本的无关段落里堆砌正面套话拉高词典分, 而在真正涉及银行金科的语境里语气平淡, 这种"边缘迎合"会被 full 轨捕捉却被 ctx 轨过滤掉, 因此 ctx 与 full 两轨迎合度之差本身即可作为迎合发生位置 (整篇 vs 主题句) 的诊断线索。被减数仍固定为 du_2022 政治词权重 0.5 的 canonical 口径。识别定位与 full、ss 轨严格并列: 三轨各自 just-identified、互为稳健性不分主次, 禁混进同一 over-identified 的 Hansen J。

## VAR: du_2022_cater_ss

【变体差分】
本列为同句轨 (_ss) 的 du_2022 迎合度。文本通道最严: 被减数 du_2022_tone_ss 与减数 llm_vote_tone_ss 都在同句共现文本 content_ss 上计算, 即标题 prepend 后, 正文只保留目标银行与金科词在同一句 (±N 句窗, 由 ss_sentence_radius 控制, 默认 1) 内共现的片段。这是三轨中语境最收敛的口径, 意在把迎合度锁定到"银行与金科被同句绑定叙述"时的语气差, 对主题相关性的要求最高。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 优雅回退为全文正文, 并置 ss_is_fallback=True, 与全文共享 n_articles 分母; 若金科 AC 自动机为空则该轨 fallback 标志全 True, 整体优雅降级。在 full-only 门控下, ss 与 ctx 同为 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集的子集, 词典侧与模型侧严格逐轨取数不跨轨借用。因窗口最窄, 该轨在浅面板上更易出现零方差退化, 属预期。ss 轨的价值在于它把迎合度锚定到最不可能被无关文本污染的语境: 只有当银行与金科被撰稿方主动放进同一句叙述时, 该篇才贡献非回退的 ss 语调, 因此该轨上的正向迎合最难用"顺带提及"来解释, 对策略性语言操纵的识别最干净。代价是样本更稀、回退比例更高, 度量噪声相应上升, 故 ss 轨定位为收敛端的稳健性轨而非首要报告轨。被减数同样固定为 du_2022 政治词权重 0.5 的 canonical 口径, 减数为三家 LLM 在同句文本上的共识语调。识别上 ss 与 full、ctx 各自 just-identified 并排、互为稳健性不分主次, 三轨严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. Energy Policy, 184, 113917. https://doi.org/10.1016/j.enpol.2023.113917
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing No. 595-605 [Working Paper]. https://doi.org/10.18653/v1/d16-1057
<!-- rendered-citations:end -->
