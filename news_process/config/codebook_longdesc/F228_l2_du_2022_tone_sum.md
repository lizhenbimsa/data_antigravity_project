---
family_id: F228
columns:
- du_2022_tone_sum_ctx
- du_2022_tone_sum_full
- du_2022_tone_sum_ss
unit: 语调净得分之和 (无界连续; 量纲 = 银行-年报道篇数 × 单篇 [-1,1] 净语调, 非归一化)
formula: "du_2022_tone_sum{track} = Σ_i du_2022_score_i{track}, i 遍历该银行-年该轨全部有效报道; du_2022_score = Σ_w final_score_w / Σ_w |final_score_w| (全语言学规则 self-normalized 签名加权和, w 遍历命中的情感词); final_score_w = base_score_w × degree_multiplier_w, 含否定翻转 (被否定的正面词其 final_score 翻为负而非计入正侧)、程度副词六级加权 (≤3.0)、转折 ×1.5; 政治正面词以 base_score=0.5 进签名和 (非独立计数相加)"
producer: news_process/pipeline/panel/encode.py (聚合); news_process/pipeline/sentiment/tone_words.py (单篇 du_2022_score)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (du_2022_score{track})
citations:
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1016/j.iref.2024.01.067"
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  venue: "International Review of Economics & Finance"
  type: "journal"
- doi: "10.1002/mde.70100"
  title: "The Textual Tone of Annual Reports and Market Attention: Evidence From Chinese Listed Companies"
  authors: "Li, Y."
  year: 2026
  venue: "Managerial and Decision Economics"
  type: "journal"
new_dois:
  - "10.1016/j.iref.2024.01.067"
  - "10.1002/mde.70100"
---

## CORE

【构念与来源】
本家族测量的是在一个银行-年单元内, 以 Du et al. (2022) 中文金融情感词典 (du_2022) 逐篇计算的净语调得分的算术总和, 即 du_2022_tone_sum。它与家族兄弟测度 du_2022_tone (逐篇净语调的均值) 共享完全相同的单篇打分原语, 唯一区别在聚合算子: 均值把银行-年内的语调压缩为一个不随报道数量放大的强度 (intensive) 量, 而总和保留了报道数量这一外延 (extensive) 维度。因此一家在某年被大量正面报道覆盖的银行, 其总和会显著高于一家仅有零星正面报道的银行, 即使两者的逐篇平均语调相同。这一外延特性使总和天然地把媒体关注的"音量"与"音调"耦合在同一标量里, 契合把银行声誉理解为关注度与情感倾向共同作用的研究视角 (Tetlock, 2007)。单篇原语来自 Du et al. (2022) 发表于 Review of Finance 的中文金融情感词典: 该词典在 Loughran and McDonald (2011) 英文财经词典范式基础上, 针对中文金融文本的领域特异性做了本土化扩充, 并额外区分出一类政治正面词。

【方法学与计算】
单篇打分口径为全语言学规则的 self-normalized 签名加权和, 而非朴素计数比: du_2022_score = Σ_w final_score_w / Σ_w |final_score_w|, w 遍历该篇命中的 du_2022 情感词, final_score_w = base_score_w × degree_multiplier_w。其中三条语言学规则全程生效——否定翻转 (被否定的正面词其 final_score 直接翻为负号, 计入负侧而非正侧计数, apply_negation)、程度副词六级加权 (degree_multiplier ≤ 3.0)、转折关系 ×1.5 (ADVERSATIVE_BOOST)。因此该分数等于签名加权和除以其绝对值和, 天然落在 [-1, 1] 且随每个词的极性、被否定状态、程度修饰与转折位置动态变化; 只有在剥除全部规则的 raw 消融变体下, 它才退化为等价于计数比的形式, canonical du_2022_score 恒为全规则口径。du_2022 的独有设计体现在政治正面词上: 其 political_positive (1,434 词) 依据 Du et al. (2022) 关于政治正面词信号弱于普通正面词的发现, 以 base_score = 0.5 进入上述签名加权和 (即该类命中词贡献 0.5 而非 1.0 的正向分量, 而非在分子上做独立计数相加); 该权重 0.5 是生产口径, 另有政治词权重梯度 (权重 ∈ {0.0, 0.5, 1.0}) 三臂互为稳健性、不分主次、各自 just-identified 并排, 禁混进同一 over-identified Hansen J。词典加载对 positive 与 negative 跨类重叠词按用户 2026-06-24 决策两侧保留, 打分时同时计入 pos/neg 使个体净语调拉向中性而非武断选边。逐篇得分在 stage 22 (tone_words) 产出, 面板聚合在 encode 层以 pandas groupby 的 'sum' 算子完成: du_2022_tone_sum{track} = (du_2022_score{track}, 'sum'), 沿银行-年分组对该轨全部有效报道求和。由于是纯求和, 结果无界, 量纲等于报道篇数乘以单篇 [-1,1] 净语调, 与均值列量纲不可直接比较, 计量应用中须相应选择随规模缩放或做对数/标准化处理。字典法与机器学习/大模型情感抽取互为稳健的三角关系已被 Frankel et al. (2022) 系统评估, 本项目据此把词典 tone 与 LLM 三家投票、BERT 三模型并列为互为稳健的测量臂。

【文献定位】
把媒体语调按主体-时间单元聚合以研究其对金融结果的影响, 是媒体金融学的成熟范式: Tetlock (2007) 以媒体悲观语调预测市场回报, Marchetti et al. (2025) 明确以银行×时间为单元聚合媒体语调刻画银行融资条件, 与本家族的银行-年聚合口径直接对应。度量层面的词典选择争议由 Loughran and McDonald (2011) 奠基——通用情感词典移植到财经语境会系统性误判, 需领域专用词典——Du et al. (2022) 则把这一洞见延伸到中文金融文本并处理了政治词这一中文语境特有的信号衰减问题。方法学上, Frankel et al. (2022) 指出词典法虽较机器学习法在细粒度上有损, 却具备透明、可复现、无训练泄漏的优点, 恰是本项目保留六部词典 tone 作为互为稳健测量臂的依据。总和这一外延聚合算子的价值在于, 它不丢弃报道数量信息, 从而对"关注度放大情感冲击"这类假设保持敏感, 与仅捕捉平均倾向的均值列构成互补而非替代。以中国银行层面媒体情感文本指数为核心变量, 检验负面媒体语调经存款稳定性渠道放大银行系统性风险, 与本家族银行-年媒体语调聚合测度直接呼应, 引用格式 Fang et al. (2024, International Review of Economics & Finance), 不带DOI链接。基于中文年报文本语调测度考察其与市场关注度的关系, 为中文财经文本词典法语调打分与主体-期间聚合提供最新方法学参照, 引用格式 Li (2026, Managerial and Decision Economics), 不带DOI链接。

## VAR: du_2022_tone_sum_full

【变体差分】
本列为 full 轨的 du_2022 净语调总和, 是三轨中的 headline 轨。full 轨文本 = 标题 prepend + 全文正文 (content_full), 即在 stage 14 (ctx_materializer) 把标题拼接到正文前形成的完整报道文本上逐篇计算 du_2022_score_full, 再沿银行-年求和。full 轨对应留篇门控口径 (2026-06-29 full-only): 一篇报道是否计入银行-年的报道宇宙, 只由 llm_verified_full == True 判定, 因此 full 轨的求和分母 (参与求和的报道集) 就是标准的留篇集本身, ctx/ss 轨的行宇宙是该 full 留篇集的子集。相对家族 canonical 的均值列 du_2022_tone_full, 本列的差异仅在聚合算子——用 'sum' 而非 'mean', 保留报道数量的外延维度, 使高关注度银行-年的语调被数量放大。相对同族 ctx/ss 兄弟列, 本列的差异在文本轨道: full 轨用完整正文, 语料最宽、词典命中词数最多, 因而单篇净语调的归一化分母 (命中词 final_score 的绝对值之和 Σ|final_score|) 通常最大、逐篇得分方差最小, 但求和后仍因报道数量差异而在银行-年间高度分散。full/ctx/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。政治正面词权重固定 0.5 (canonical polw05), 语言学规则为全规则口径, 与规则消融梯度、政治词权重梯度均正交不交叉。作为外延聚合量, 本列在计量应用中通常需先随银行-年报道规模缩放或做对数变换, 以免规模最大的银行-年在拟合中主导系数; 这也正是它与不随规模放大的均值列 du_2022_tone_full 互补的地方——均值刻画平均倾向、总和刻画倾向的累积暴露, 两者对"关注度放大情感冲击"假设的敏感度不同, 因此在稳健性叙事中并排而非相互替代。

## VAR: du_2022_tone_sum_ctx

【变体差分】
本列为 ctx (实体窗) 轨的 du_2022 净语调总和。ctx 轨文本 = 标题 prepend + 实体窗口 (content_ctx), 即只截取目标银行实体在正文中出现位置附近的上下文窗口而非全文, 在此较窄文本上逐篇计算 du_2022_score_ctx 再沿银行-年求和。相对 full 轨, ctx 轨把语调计算聚焦到与目标银行直接相关的语境, 剔除了同一篇报道中与该行无关的段落, 从而降低了"整篇泛泛正面但涉及该行部分中性"这类稀释偏差; 代价是命中词数变少、单篇分母变小、逐篇得分更易受个别极性词主导而方差上升。相对家族 canonical 的均值列 du_2022_tone_ctx, 本列同样只在聚合算子上不同 ('sum' 而非 'mean'), 保留报道数量外延信息。ctx 轨行宇宙为 full 留篇集的子集 (conditional-on-full), 是 conditional 测度/稳健性轨而非门控轨——即报道是否留篇仍由 full 轨判定, ctx 轨只在已留篇报道上按窗口重算语调再求和。三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。政治词权重固定 0.5, 全语言学规则。若某银行-年在 ctx 轨无有效命中, 该轨按逐轨口径独立降级, 不借用 full 轨分母。由于 ctx 轨语料较 full 更窄, 其求和结果的绝对量级通常小于 full 轨同名列, 但在语义针对性上更贴近目标银行, 因而当研究关心的是"针对该行本身的媒体语调累积"而非"报道整体氛围"时, ctx 轨总和是更干净的稳健性对照。政治词权重固定 0.5, 与政治词权重梯度、规则消融梯度正交不交叉; 三轨总和列在计量上同样建议随规模缩放后再入模, 以控制外延量纲带来的异方差。

## VAR: du_2022_tone_sum_ss

【变体差分】
本列为 ss (同句) 轨的 du_2022 净语调总和, 是三轨中语境最严格的一轨。ss 轨文本 = 标题 prepend + 银行∧金科同句 ±N 窗 (content_ss, 默认句半径 1), 即仅保留目标银行与金融科技词在同一句 (或 ±1 句窗) 共现的句子, 在这一最窄文本上逐篇算 du_2022_score_ss 再沿银行-年求和。相对 ctx 轨, ss 轨进一步把语调锁定在银行与金科主题直接耦合的语句, 语义针对性最强但语料最稀疏。ss 轨采用镜像 ctx 的回退语义: 当某报道无银行∧金科同句共现时, content_ss 回退为全文 body, ss_is_fallback 置 True, 并与 ctx 轨共享 n_articles 分母; 若 FINTECH_AC 为 None 则 *_is_fallback 全 True 优雅降级。相对家族 canonical 均值列 du_2022_tone_ss, 本列差异仅在 'sum' 聚合算子, 保留报道数量外延维度。ss 轨行宇宙同为 full 留篇集子集 (conditional-on-full), 是稳健性轨而非门控轨。三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。政治词权重固定 0.5, 全语言学规则; 在开发期 T=2 小样本上 ss 轨可能因共现稀疏而退化, 属预期现象, 生产 T=18 语料上恢复正常分散。相对 full/ctx 两轨, ss 轨的求和量级最小、稀疏性最高, 因而在小样本上零值或近零值格点较多; 它捕捉的是银行与金融科技主题在同一语句中被媒体正负面表述的累积暴露, 语义最聚焦于本项目银行-金科议题, 是三轨中构念针对性最强的稳健性臂。政治词权重固定 0.5, 与权重梯度、规则消融梯度正交不交叉; 与均值列 du_2022_tone_ss 互补——后者刻画同句语境下的平均倾向, 本列则叠加了报道数量, 两者在同一 Hansen J 中禁混, 只作并排稳健性对照。

<!-- rendered-citations:begin -->
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.01.067
Li, Y. (2026). The Textual Tone of Annual Reports and Market Attention: Evidence From Chinese Listed Companies. Managerial and Decision Economics. https://doi.org/10.1002/mde.70100
<!-- rendered-citations:end -->
