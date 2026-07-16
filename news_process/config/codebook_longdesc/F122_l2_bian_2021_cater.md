---
family_id: F122
columns:
- bian_2021_cater_ctx
- bian_2021_cater_full
- bian_2021_cater_ss
unit: 迎合度差分得分 (无量纲; 词典语调 减 LLM 共识语调, 值域随两个被减数各自的 [-1,1] 归一化区间落在 [-2,2])
formula: "bian_2021_cater{track} = bian_2021_tone{track} - llm_vote_tone{track}; track in {_full,_ctx,_ss}"
producer: news_process/pipeline/panel/runner.py (步骤 8d 算法迎合度 algo_cater, L2432-L2477)
novelty_exempt_rationale: "该家族 (bian_2021_cater_*) 是词典语调与LLM共识语调之差的算法迎合度衍生测度 (producer algo_cater, 步骤8d), 正文明确'该构念不是一个独立的情感测度,而是两个异源情感测度之差', 其学术依据已由被减数 bian_2021_tone (Bian et al. 2021 词典) 与 llm_vote_tone 各自的母族文献支撑, 属衍生/差分变体家族, 非独立新构念, 无需单独追新2023+文献。"
upstream:
- 22_tone_words.parquet (bian_2021_tone{track}, Bian2021 词典逐篇极性聚合)
- 21_tone_llms.parquet (llm_vote_tone{track}, 三家 LLM 多数投票共识语调)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本)
citations:
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
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
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
new_dois: []
---

## CORE

【构念与来源】
本家族三列 bian_2021_cater_full / bian_2021_cater_ctx / bian_2021_cater_ss 度量的是同一个构念: 以卞氏中文金融情感词典 (Bian et al. 2021) 逐篇计算的银行金科报道语调, 相对于三家大语言模型多数投票共识语调之间的系统性差值, 我们称之为"算法迎合度差分" (algorithmic catering divergence)。其经济学含义在于: 当以固定词典穷举关键词的方式度量报道语调, 与以深层语义理解模型度量的语调之间出现稳定偏离时, 这一偏离既可能来自词典对语境反讽、否定嵌套、程度修饰的机械不敏感, 也可能来自信息生产者 (媒体或被报道银行) 有意堆砌词典可捕捉的正面套话以"迎合"机器化文本打分器的行为倾向。正值表示卞氏词典判读比 LLM 共识更正面, 即报道在词典可见的表层用词上比其深层语义所支持的更乐观, 这正是文献中所关切的"对着正在倾听的机器说话"式披露策略的可观测痕迹。该构念不是一个独立的情感测度, 而是两个异源情感测度之差, 因此它天然继承被减数 bian_2021_tone 与 llm_vote_tone 各自的口径与缺失语义。

数据来源上, 被减项 bian_2021_tone 来自 stage 22 词典情感阶段: 卞氏词典是一部面向会计与金融文本、以中文语料训练的极性词表, 在本项目内以 tone_dicts.json 为单一事实源加载, 逐篇按正负词计数并经否定翻转、程度副词、转折三条语言学规则调制后归一化为 [-1,1] 区间的篇级极性, 再在银行年层聚合。减项 llm_vote_tone 来自 stage 21 情感 LLM 阶段, 是 gpt54nano、gemini31、deepseekv4 三家模型对同一篇报道情感三分类投票后的多数共识, 亦归一化至同一区间。两者相减即得本家族列。

【方法学与计算】
计算实现位于 pipeline/panel/runner.py 步骤 8d "算法迎合度"全展开块。对每一轨 track ∈ {_full, _ctx, _ss}, 若银行年面板中同时存在 bian_2021_tone{track} 与 llm_vote_tone{track} 两列, 引擎执行逐元素相减 panel[bian_2021_cater{track}] = panel[bian_2021_tone{track}] - panel[llm_vote_tone{track}], 不做任何再归一化、缩尾或标准化。这是一个纯后处理派生, 不新增任何 LLM 或词典调用, 因此对冻结缓存零成本、对 golden 锚点字节安全。缺失语义随被减数传导: 任一被减项为 NaN 则差值为 NaN, 不做零填充, 这与本项目对"零覆盖银行年不得伪装成中性 0"的一贯红线一致。

三轨口径必须显式说明。full 轨文本为标题 prepend 后的全文正文, ctx 轨为标题加银行与金科实体窗, ss 轨为标题加银行与金科同句共现窗; 三轨文本在 stage 14 物化。按 2026-06-29 起生效的 full-only 留篇门控, 一篇报道是否计入银行金科报道宇宙只由 full 轨的 LLM 判定决定, ctx 与 ss 轨降为条件于 full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集。因此本家族三列的 full 轨是首要测度, ctx 与 ss 两轨是并排的规格稳健性轨。三轨遵循本项目铁律: full / ctx / ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混进同一个 over-identified 的 Hansen J 过度识别检验。ss 轨的回退语义镜像 ctx: 当某篇无银行金科同句共现时其 ss 文本退化为全文, is_fallback 置真, 分母口径与 ctx 共享。在本机 T=2 开发面板上 ctx 与 ss 轨常出现零方差退化属预期, 生产 T=19 语料上恢复正常。

【文献定位】
算法迎合度这一构念的方法学根基是"词典法与深层模型法对同一文本给出系统性不同语调"这一被反复记录的经验事实。Frankel、Jennings 与 Lee (2022) 在对披露文本情感的机器学习法与词典法的正面比较中指出, 两类方法捕捉的语调维度并不重合, 且其分歧本身携带增量信息, 这为把"词典减模型"之差作为一个独立可分析对象提供了直接依据。van Atteveldt、van der Velden 与 Boukes (2021) 通过将人工标注、众包编码、词典法与机器学习算法并置比较, 系统刻画了词典法相对于语义模型在效度上的结构性偏差, 说明本家族的差分并非纯噪声而是有构念含义的信号。在词典本体的合法性上, Barbaglia 等 (2025) 论证了基于词表的经济文本情感度量在可解释性与可复现性上的独立价值, 而 Du 等 (2022) 与 Bian 等 (2021) 则分别提供了中文金融领域词典的领域特定性证据与本家族所用卞氏词典的构造来源, 支撑以卞氏词典而非通用英文词表作被减项的选择。综合而言, 本家族把词典与 LLM 两条已被文献确立为"互为稳健、各有偏差"的测度之差, 转化为一个对媒体披露策略敏感的可观测指标。

## VAR: bian_2021_cater_full

【变体差分】
本列是卞氏词典算法迎合度的 full 轨实例, 也是本家族的首要测度轨。其精确语义为 bian_2021_cater_full = bian_2021_tone_full - llm_vote_tone_full: 被减项取 full 轨 (标题 prepend 后的全文正文) 上的卞氏词典篇级极性银行年聚合, 减项取 full 轨上三家 LLM 多数投票共识语调。选择 full 轨作首要测度直接源于 2026-06-29 起生效的 full-only 留篇门控: 银行金科报道宇宙的成篇判定只看 full 轨 LLM 判定, 因此 full 轨的分母是完整留篇集, 而非任何子集, 数值最稳定、样本最全。本列与家族内 ctx、ss 两列的唯一区别就在文本轨: 三者共享同一相减公式与同一对被减数命名模式, 仅文本范围 (全文 vs 实体窗 vs 同句窗) 不同, 由此形成 full / ctx / ss 三条并排的规格稳健性轨。三轨须遵循铁律: 各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified 的 Hansen J。本列不做再归一化, 缺失随被减数传导为 NaN 而非零填充。需要提示的是, 本列与同族的 bian_2021_cater_b_full 是两个不同减项的迎合度: 本列减的是 LLM 共识, cater_b 减的是 BERT 综合极性, 两者不可混用于同一识别式。同理, 本列亦区别于综合词典迎合度 algo_cater_full (被减项为六部词典均值 dict_avg_tone 而非单一卞氏词典, 减项仍为 LLM 三家共识) 与逐模型迎合度 cater_gpt54nano_full 等。须特别澄清: 逐模型迎合度 cater_gpt54nano_full 与本列在被减项和减项两处均不同, 而非仅减项不同——其被减项亦为六部词典均值 dict_avg_tone (非卞氏单一词典 bian_2021_tone), 减项则为单家 LLM 的语调 (非三家多数投票共识); 因此不可把 cater_gpt54nano 视作"本列换单模型减项"的直接变体, 两者被减数基准不同, 分属词典整体口径与单词典口径两条互不重合的迎合度族。本列刻意把被减项锁定为卞氏单一词典 bian_2021_tone、减项锁定为 LLM 三家共识 llm_vote_tone, 用以隔离"卞氏词典这一部特定中文金融词表相对深层语义模型的系统偏离", 而非词典整体或单模型口径的偏离。这一命名精确性对下游把本列作单词典迎合度稳健性臂使用时至关重要。

## VAR: bian_2021_cater_ctx

【变体差分】
本列是卞氏词典算法迎合度的 ctx 轨实例, 定位为条件于 full 的规格稳健性轨。其语义为 bian_2021_cater_ctx = bian_2021_tone_ctx - llm_vote_tone_ctx: 两个被减数均取 ctx 轨, 即标题 prepend 后仅保留银行与金科实体上下文窗口 (content_ctx) 的文本上计算的卞氏词典极性与 LLM 共识语调之差。相对本家族 full 轨, 本列的唯一差分维度是文本范围收窄至实体窗而非全文: 这一收窄意在剥离与银行金科无关的语料, 检验迎合度信号是否稳健于"只看实体近邻语境"的更严口径。按 full-only 门控, ctx 轨的行宇宙是 full 留篇集的子集, 因此本列是 conditional-on-full 的测度而非独立成篇判据; 其 per-track 分母按 ctx 轨自身口径计算, 不借用 full 轨分母。本列与 full、ss 两列互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁三轨混入同一 over-identified 的 Hansen J 过度识别检验。缺失语义与家族一致: 任一被减项为 NaN 则本列为 NaN, 不做零填充以免零覆盖银行年被伪装成中性迎合度 0。在本机 T=2 开发样本上 ctx 轨常呈零方差退化, 属预期, 生产 T=19 语料恢复正常方差。本列与同族 bian_2021_cater_b_ctx 亦须区分: 后者减项为 BERT 综合极性而非 LLM 共识, 两条迎合度轨互为稳健、各自 just-identified 并排, 不得混入同一过度识别检验。把实体窗与全文轨并排比较可诊断迎合度信号是否由与银行金科无关的旁支语料驱动: 若 ctx 轨迎合度显著弱于 full 轨, 则提示表层套话主要堆积在报道的非核心段落而非实体近邻语境, 这一对比本身即是本列作为稳健性轨的诊断价值所在。

## VAR: bian_2021_cater_ss

【变体差分】
本列是卞氏词典算法迎合度的 ss (同句) 轨实例, 是三轨中口径最严的规格稳健性轨。其语义为 bian_2021_cater_ss = bian_2021_tone_ss - llm_vote_tone_ss: 两个被减数均在 ss 轨文本 (content_ss, 标题 prepend 后仅保留银行与金科在同一句内共现的句窗) 上计算。相对家族 full 与 ctx 两轨, 本列的差分维度是把文本进一步收窄至"银行与金科同句"这一最严共现判据, 用以检验迎合度是否在只保留强共现语境时依然成立。ss 轨的回退语义镜像 ctx: 当某篇报道不存在银行与金科同句共现时, 其 ss 文本优雅退化为全文正文, 对应的 is_fallback 标记置真, 且分母口径与 ctx 轨共享。按 full-only 留篇门控, 本列同样是 conditional-on-full 的测度轨, 行宇宙为 full 留篇集子集, per-track 分母按 ss 轨自身计算。本列与 full、ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified 的 Hansen J。缺失随被减数传导为 NaN 不零填。因同句窗最窄, 本列在本机 T=2 开发面板上出现零方差或大量回退退化最为常见, 均属预期, 需以生产 T=19 语料为准评估其信号。本列与同族 bian_2021_cater_b_ss 的区别仍在减项 (LLM 共识 vs BERT 综合极性), 两轨互为稳健不分主次。ss 轨是三轨中对"银行金科强共现语境下是否仍存在词典对深层模型的系统迎合"这一最严命题的检验: 当回退比例过高时本列大量取值等于对应 full 轨值 (因文本退化为全文), 使用者须结合 is_fallback 分母甄别真同句信号与回退污染, 不可把回退主导的 ss 轨迎合度直接等同于同句语境结论。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
<!-- rendered-citations:end -->
