---
family_id: F622
columns:
- yao_2021_cater_ctx
- yao_2021_cater_full
- yao_2021_cater_ss
unit: 语调差分 (无量纲; 两个 [-1,1] 归一化语调之差, 取值约 [-2,2])
formula: "yao_2021_cater{track} = yao_2021_tone{track} - llm_vote_tone{track}; 正值 → yao_2021 词典侧比三家 LLM 共识更正面 (潜在算法迎合)"
producer: news_process/pipeline/panel/runner.py (步骤 8d 算法迎合度, 情形 B 单词典 vs 综合 LLM); 上游 yao_2021_tone 由 pipeline/sentiment/tone_words.py 产, llm_vote_tone 由 pipeline/sentiment/tone_llms.py 产; 标签见 pipeline/panel/export.py / pipeline/panel/stata_export.py
upstream:
- 22_tone_words.parquet (yao_2021_tone{track})
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.18653/v1/d16-1057
  type: wp
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
- doi: "10.2139/ssrn.6143029"
  type: "wp"
  authors: "Wang, Y., Wong, T., & Zhang, T."
  year: 2026
  title: "Does Social Media Identify the Optimistic Bias of State-Controlled Media? Evidence from China"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "6143029"
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是"算法迎合度"(algorithmic catering) 在 Yao (2021) 中文金融情感词典这一单一切面上的表现: 以该词典对同一批银行金科报道所打出的机器可读语调, 减去三家大语言模型 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 对同一文本的多数投票共识语调, 所得差值即 yao_2021_cater。其构念直觉延续本项目其余词典迎合族 (du_2022_cater、jiang_2021_cater、bian_2021_cater、you_2018_cater、loughran_cater) 的共同逻辑: 词典打分依赖一套公开、固定、可被撰稿方预先获知或反推的极性词表与逐词加权规则, 而大语言模型捕捉的是超越逐词极性匹配的语境语义、否定翻转与转折关系。当信息发布方知道下游存在大量"机器读者"依赖词典类工具抓取语调 (监管抓取、量化情报、检索式舆情监测等) 时, 存在一种策略性动机: 堆砌词典正面词、规避词典负面词, 从而在词典口径上显得更乐观, 却未必改变经语境理解后的真实语气立场。若该差值系统性为正, 即提示存在朝向词典规则本身的语言迎合, 而非报道内容真实基调的改善。本列把这一"人-机语调楔子"落到银行金科报道的面板测量上, 以"词典侧减深层模型侧"的方式把楔子显性化, 供后续检验迎合动机是否与银行治理特征、信息环境或监管强度相关。

【方法学与计算】
计算在面板构造阶段 (runner.py 步骤 8d 算法迎合度, 情形 B「单词典 vs 综合深层模型」) 完成, 是纯后处理差分运算, 不额外调用任何付费 LLM 或嵌入 API, 边际成本为零。被减数 yao_2021_tone{track} 是 Yao 词典在阶段 22 (`pipeline/sentiment/tone_words.py`) 上算出的净语调: 依据词典正面/负面词表对分词后的文本计数, 经语言学规则 (否定翻转、程度副词加权、转折句式) 处理后, 对总极性词数归一化, 落在约 [-1,1] 区间; 该计算走的是本项目词典族统一的 canonical 全规则口径 (非消融梯度的某一子集变体)。减数 llm_vote_tone{track} 是三家大模型在阶段 21 (`pipeline/sentiment/tone_llms.py`) 对同一文本的多数投票共识语调, 同样归一化到可比量纲。两者相减得到无量纲的语调差分, 理论取值区间约 [-2,2], 正值表示 Yao 词典比 LLM 共识更正面, 负值反之。三个后缀 _full / _ctx / _ss 分别对应全文轨 (标题 prepend 加完整正文)、实体窗轨 (标题加银行与金科实体邻近窗口)、同句轨 (标题加银行与金科同句共现窗口, ±N 句由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1); 三轨的被减数与减数均严格逐轨取用, 不跨轨借数、不混轨相减。留篇口径遵循 2026-06-29 确立的 full-only 门控: 一篇报道是否计入"一篇银行金科报道"只由 full 轨的 LLM 判定 (`llm_verified_full == True`) 决定, ctx 与 ss 轨在此基础上是 conditional-on-full 的行宇宙子集, 各自的词典侧与模型侧仍按该子集独立聚合, 不借用 full 轨的分子分母。

【文献定位】
在测量方法谱系上, 本列站在"词典法与深层模型法互为参照"的交叉点。词典法一脉的方法学基石是 Du 等 (2022) 发表于 Review of Finance 的中文金融情感词典构建工作: 论文论证了直接移植英文 Loughran-McDonald 词典到中文金融文本会系统性失真, 必须依据中文金融语境本土重建极性词表, 这一方法论同样适用于理解 Yao (2021) 词典的构建逻辑与其局限。近年该谱系持续细化, Ma 等 (2025, Expert Systems with Applications) 构建面向中国境内投资者的细粒度情感词典 CN-FSD, 进一步论证了行业/受众特定词典相对通用词典的增量价值; Sun 等 (2025, Natural Language Processing Journal) 将词典知识与中性特征注入预训练语言模型, 试图弥合规则法与深度语义法之间的鸿沟, 其动机与本列"词典 vs LLM 差分"测度迎合的逻辑高度呼应; Hamilton 等 (2016) 提出从无标注语料自动归纳领域情感词表的方法, 为理解词典类工具的可预测性 (进而可被迎合) 提供了方法论背景。Barbaglia 等 (2025, Economic Inquiry) 系统评估了基于词典的经济文本情感分析方法在宏观与金融场景下的表现与边界, 明确指出词典法对固定规则的依赖是其相对深度模型法的结构性弱点, 这一弱点恰是"迎合"得以发生的制度前提: 撰稿方越能预判词典的判定规则, 就越有空间在不改变实质语气的情况下操纵词典读数。本列的方法论定位即是把这一弱点转译为可观测的面板变量。三轨设定属规格稳健性并排: full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J 过度识别检验。 在差分形态的外部旁证上, Wang、Wong 与 Zhang (2026) 于中国语境下把两类媒体文本的语调并置, 以其中一方识别另一方的乐观偏差, 与本列"取两个同构念语调测度之有向差、并把该差解读为一方的系统性偏离"同型, 旁证了此类有向差在中文媒体文本上可被赋予实质构念内涵。惟其差值轴与本列不同: 原文比较的是媒体来源 A 与来源 B 之间的来源层偏差, 本列比较的是同一篇报道上 yao_2021 词典测度与三家 LLM 共识判读之间的方法层偏差; 其语料为国有媒体与社交媒体文本 (非银行金科共现报道), 层级为公司/事件层而非 bank-year, 无 LLM 三家投票与三轨文本口径, 且属尚未经期刊同行评议的工作论文。因此该文仅作方法形态上的类比参照, 不用于支撑本列的迎合解读本身。
## VAR: yao_2021_cater_full

【变体差分】
本列为全文轨 (_full) 的 yao_2021 迎合度。被减数 yao_2021_tone_full 在标题 prepend 后的完整正文上计算 Yao 词典净语调, 减数 llm_vote_tone_full 为三家 LLM 在同一全文文本上的共识语调, 两者相减即本列。相对家族内另两轨, full 轨的独特地位在于它是留篇门控的唯一裁决轨 (2026-06-29 full-only 口径): 某篇报道是否被判为一篇"银行金科报道"仅取决于该篇 full 轨的 LLM 判定, 因此 full 轨行宇宙是全集, ctx 与 ss 轨的行宇宙是它的严格子集。这意味着 full 轨迎合度的分母 (进入年度聚合的报道集) 最完整、覆盖面最广, 度量在样本量意义上噪声相对最低, 通常作为该家族的首要报告轨。文本通道上 full 轨采用标题加全文正文, 语料信息量最大, 因而词典侧与模型侧都在最完整的文本上打分, 二者之差最能反映撰稿方在整篇文本层面对词典规则的系统性迎合, 而非局部片段的偶发效应。需强调的是, 本列的词典侧固定取 yao_2021 词典的 canonical 全规则语调 (否定翻转+程度副词+转折规则齐全), 并非词典消融梯度 (raw/negonly/degonly/advonly 等) 中的某一子集变体, 二者正交不交叉, 不应混用。就识别口径而言, 本列与 yao_2021_cater_ctx、yao_2021_cater_ss 两轨各自 just-identified 并排、互为稳健性不分主次, 三轨严禁混入同一 over-identified Hansen J 过度识别检验。

## VAR: yao_2021_cater_ctx

【变体差分】
本列为实体窗轨 (_ctx) 的 yao_2021 迎合度。与 full 轨的唯一差别在文本通道: 被减数 yao_2021_tone_ctx 与减数 llm_vote_tone_ctx 都在实体窗文本 content_ctx 上计算, 即标题 prepend 后, 正文只保留银行与金科实体邻近窗口内的句子, 而非整篇正文。其构念意图是把迎合度的测量收窄到真正谈及目标银行金科业务的语境, 剔除与该主题无关的段落对词典计数与模型语义判断的稀释, 从而更贴近"就该银行金科事项的语气迎合"这一更严格的构念。相对 full 轨, ctx 轨在 full-only 门控下是 conditional-on-full 的稳健性轨: 行宇宙为 full 留篇集的子集, 但被减数与减数仍严格在 ctx 文本上各自计算, 不向 full 轨借用分子或分母。由于窗口收窄, 单篇可用的极性词与语境线索相应变少, 在浅面板 (如早期试跑 T=2 样本) 上该轨方差可能收缩甚至退化为零, 属预期现象, 生产全样本 (T=19) 下应恢复正常变异。相对 full 轨, ctx 轨的迎合信号能排除一种混淆: 撰稿方可能在整篇文本的无关段落里堆砌正面套话拉高词典分, 而在真正涉及银行金科的语境里语气平淡, 这类"边缘迎合"会被 full 轨捕捉却被 ctx 轨过滤掉, 因此 ctx 与 full 两轨迎合度读数之差本身即可作为迎合发生位置 (整篇泛化 vs 主题句聚焦) 的诊断线索。词典侧同样固定取 yao_2021 canonical 全规则语调。识别定位与 full、ss 轨严格并列: 三轨各自 just-identified、互为稳健性不分主次, 禁混进同一 over-identified 的 Hansen J。

## VAR: yao_2021_cater_ss

【变体差分】
本列为同句轨 (_ss) 的 yao_2021 迎合度。文本通道在三轨中最严: 被减数 yao_2021_tone_ss 与减数 llm_vote_tone_ss 都在同句共现文本 content_ss 上计算, 即标题 prepend 后, 正文只保留目标银行与金科词在同一句 (±N 句窗, 由 `ss_sentence_radius` 控制, 默认 1) 内共现的片段。这是三轨中语境最收敛的口径, 意在把迎合度锁定到"银行与金科被同句绑定叙述"时的语气差, 对主题相关性的要求最高。ss 轨的回退语义严格镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 优雅回退为全文正文, 并置 ss_is_fallback=True, 与全文共享 n_articles 分母; 若金科自动机 (FINTECH_AC) 为空则该轨 fallback 标志全部为 True, 整体优雅降级而非崩溃。在 full-only 门控下, ss 与 ctx 同为 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集的子集, 词典侧与模型侧严格逐轨取数、不跨轨借用。因窗口最窄, 该轨在浅面板上更易出现零方差退化, 属预期而非缺陷。ss 轨的价值在于它把迎合度锚定到最不可能被无关文本污染的语境: 只有当银行与金科被撰稿方主动放进同一句叙述时, 该篇才贡献非回退的 ss 语调, 因此该轨上呈现的正向迎合最难以"顺带提及、语境无关"来解释, 对策略性语言操纵的识别相对最干净; 代价是有效样本更稀、回退比例更高, 度量噪声相应上升, 故 ss 轨定位为语境收敛端的稳健性轨而非首要报告轨。词典侧同样固定取 yao_2021 canonical 全规则语调, 减数为三家 LLM 在同句文本上的共识语调。识别上 ss 与 full、ctx 各自 just-identified 并排、互为稳健性不分主次, 三轨严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing No. 595-605 [Working Paper]. https://doi.org/10.18653/v1/d16-1057
Wang, Y., Wong, T., & Zhang, T. (2026). Does Social Media Identify the Optimistic Bias of State-Controlled Media? Evidence from China. SSRN Electronic Journal No. 6143029 [Working Paper]. https://doi.org/10.2139/ssrn.6143029
<!-- rendered-citations:end -->
