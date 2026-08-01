---
family_id: F002
columns:
- algo_cater_b_ctx
- algo_cater_b_full
- algo_cater_b_ss
unit: 无量纲情感差值 (词典侧减深层模型侧, 取值区间随两侧归一化口径落在约 [-2, 2])
formula: "algo_cater_b{track} = dict_avg_tone{track} - (bert_avg_pos{track} - bert_avg_neg{track}); track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/runner.py (8d 算法迎合度全展开) ; news_process/pipeline/panel/export.py (Stata 变量标签)
upstream:
- 22_tone_words.parquet (dict_avg_tone{track})
- 23_tone_berts.parquet (bert_avg_pos{track}, bert_avg_neg{track})
- 40_panel_yearly.parquet
citations:
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1146/annurev-economics-082222-074352
  type: journal
  authors: Ash, E., & Hansen, S.
  year: 2023
  title: "Text algorithms in economics"
  venue: Annual Review of Economics
  vol: 15
  pages_or_artno: 659-688
- doi: 10.1007/s13278-024-01270-5
  type: journal
  authors: Khan, M. H., Hasan, A. B., & Anupam, A.
  year: 2024
  title: "Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms"
  venue: Social Network Analysis and Mining
  vol: 14
  issue: 1
  pages_or_artno: 110
- doi: 10.2307/2346806
  type: journal
  authors: Dawid, A. P., & Skene, A. M.
  year: 1979
  title: "Maximum likelihood estimation of observer error-rates using the EM algorithm"
  venue: Journal of the Royal Statistical Society Series C (Applied Statistics)
  vol: 28
  issue: 1
  pages_or_artno: 20-28
- doi: "10.2139/ssrn.5153587"
  type: "wp"
  authors: "Bose, I., Hu, N., Liang, P., & Yang, X."
  year: 2025
  title: "Can Larger Language Models Always Perform Better? A Comparison of GPT, FinBERT, and Dictionaries in Evaluating Management Sentiment"
  venue: "SSRN"
  pages_or_artno: "5153587"
- doi: "10.1145/3677052.3698675"
  type: "journal"
  authors: "Kim, W., Spörer, J., Lee, C. L., & Handschuh, S."
  year: 2024
  title: "Is Small Really Beautiful for Central Bank Communication? Evaluating Language Models for Finance: Llama-3-70B, GPT-4, FinBERT-FOMC, FinBERT, and VADER"
  venue: "Proceedings of the 5th ACM International Conference on AI in Finance"
  pages_or_artno: "626-633"
- doi: "10.1007/s00521-024-10495-6"
  type: "journal"
  authors: "Lee, J., Stevens, N., & Han, S. C."
  year: 2025
  title: "Large Language Models in Finance (FinLLMs)"
  venue: "Neural Computing and Applications"
  vol: "37"
  issue: "30"
  pages_or_artno: "24853-24867"
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
本家族刻画"算法迎合"(algorithmic catering) 的词典—深层模型分歧版本, 具体为综合词典情感与综合 BERT 情感之差 algo_cater_b。构念动机来自一个稳健的经验事实: 面向机器阅读者 (监管文本挖掘器、量化情绪因子、舆情打分引擎) 的信息发布者, 有动机把措辞刻意调向词表可捕捉的正面词, 从而在浅层词典打分上显得更乐观, 而这种表层修辞并不一定被理解上下文与句法的深层语言模型采信。于是同一篇银行金融科技报道, 用固定金融情感词典打出的语气分, 会系统性地高于用微调中文金融 BERT 打出的语气分; 二者之差即为迎合度的可观测代理。取正值时, 词典侧比 BERT 侧更正面, 提示报道含较多"迎合词表"的表层褒义修辞; 取负值时, 深层模型读出的正面性反而更高, 提示词典漏读了语境化的正面语义。本家族与姊妹家族 algo_cater (词典对 LLM) 构念同源、深层模型侧不同: algo_cater 以三家投票 LLM 情感为深层基准, 本家族 algo_cater_b 以三模型平均 BERT 情感为深层基准, 二者是同一迎合构念下互为稳健性、不分主次的两条并排测度轨, 不得混入同一 over-identified Hansen J。

【方法学与计算】
计算在面板构建 runner 的算法迎合度全展开步骤 (8d) 内完成, 是纯面板列相减的后处理, 不新增任何 LLM 或嵌入调用。逐轨公式为 algo_cater_b{track} = dict_avg_tone{track} − (bert_avg_pos{track} − bert_avg_neg{track})。其中词典侧 dict_avg_tone 是六部金融情感词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran) 归一化语气分的银行—年聚合均值, 在全部语言学规则 (否定翻转、程度副词、转折) 下计算; 深层模型侧以三模型平均 BERT 的正面概率均值减负面概率均值构造带符号净语气 (bert_avg_pos − bert_avg_neg), 落在 [-1, 1]。两侧口径不同故差值无严格封闭上下界, 但实证落在约 [-2, 2]。缺失语义与同族 disag、log_sent 对齐: 上游任一侧列缺席则该轨迎合度不产出, 对无文章的银行—年行输出 NaN 而非 0, 避免把"无报道"误当"零迎合"进入回归 (对齐 Heckman 1979、Allison 2001 的缺失处理红线)。三条文本轨 full、ctx、ss 各自独立走同一公式: full 为标题 prepend 加全文正文, ctx 为标题加实体上下文窗口, ss 为标题加银行与金融科技同句共现窗口。ss 回退语义镜像 ctx: 当某银行—年无银行与金融科技同句共现时, content_ss 退化为全文正文、ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母。留篇门控为 full-only 口径 (2026-06-29): 一篇报道是否算"银行金融科技报道"只看 full 轨 LLM 判定, ctx 与 ss 是 conditional-on-full 的行宇宙子集测度。三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

【文献定位】
方法学根基在于词典法与机器学习法情感测度的系统性分歧本身即是可分析信号。van Atteveldt 等 (2021) 直接比较人工标注、众包、词典与机器学习算法四类情感测度, 记录了词典法相对深层模型在效度上的可复现落差, 为把二者之差解读为构念性偏离而非纯噪声提供了外部依据。Ash 与 Hansen (2023) 综述了文本算法在经济学中的应用谱系, 明确区分基于词表的浅层计数法与基于表征学习的深层模型, 支持本家族以两类方法的读数差作为发布者行为代理。Khan 等 (2024) 以银行股为对象比较先进机器与深度学习算法在社媒情绪上的表现, 佐证深层模型在金融文本上对语境化情感的捕捉优势, 即本差值负项一侧的合理性来源。Dawid 与 Skene (1979) 关于多观察者误差率的极大似然估计, 为把多模型读数聚合成综合基准 (三模型平均 BERT、六词典平均) 时的一致性与偏差分解提供经典统计学参照。 晚近的模型评测文献为本家族两端的口径选择提供了更贴近的外部依据。Bose、Hu、Liang 与 Yang (2025) 把 GPT、FinBERT 与情感词典三类方法置于同一批管理层文本上头对头比较, 报告三者对语调判读的系统性不一致, 直接支撑本家族"词典侧减深层模型侧"之差非零并非抽样噪声; 但该文语料为英文管理层沟通文本, 模型侧为 GPT 与 FinBERT 而非本项目的三部中文金融 BERT, 词典侧亦为英文词表, 分析层级是文档级方法比较而非银行—年聚合, 且系尚未经期刊同行评议的工作论文, 故仅可作分歧存在性的定性依据。Kim、Spörer、Lee 与 Handschuh (2024) 在同一批中央银行沟通语料上并排评测 VADER 词典、FinBERT 与 FinBERT-FOMC 及 GPT-4、Llama-3-70B, 给出"模型规模更大不必然与词典或小模型读数一致"的评测证据, 佐证本家族以 BERT 净语气作深层基准具有可辨识性; 其语料为美联储 FOMC 英文文本, 词典臂为通用情感词典 VADER 而非本项目六部中文金融词典, 评价目标是对齐人工标签的分类准确率, 与本家族的有向差值面板列口径不同, 且为会议论文。Lee、Stevens 与 Han (2025) 综述金融领域语言模型自 FinBERT 类判别式模型至生成式 FinLLM 的技术谱系, 可为本家族与姊妹家族 algo_cater 的深层基准分野 (BERT 族与 LLM 族并非同一测度族) 提供谱系层面的定位; 该文系综述而非原创实证, 不含任何测度比较结果, 覆盖以英文金融 NLP 为主且未评测 finbert_cn、fin_sent_zh、finbert2, 亦无词典对照臂与面板层级, 故引用严格限于技术谱系定位, 不得据以推导任何数值口径。Wang、Wong 与 Zhang (2026) 在中国语境下把两类媒体文本的语调并置, 以其中一方识别另一方的乐观偏差, 其"两个同构念语调测度相减、把有向差解读为一方系统性偏离"的做法与本家族同型; 惟差值轴不同——该文比较的是媒体来源之间的偏差, 本家族比较的是同一篇文本上词典法与深层模型法之间的方法层偏差, 且其语料为国有媒体与社交媒体而非银行金融科技报道, 层级为公司或事件层, 亦无 BERT 口径, 系工作论文, 故只作差值构造形态的同型参照。
## VAR: algo_cater_b_ctx

【变体差分】
本列是 algo_cater_b 家族的 ctx 上下文窗口轨。文本口径为标题 prepend 加实体上下文窗口 content_ctx: 只保留围绕目标银行实体的邻近文本窗, 剔除与目标银行无关的段落, 相对 full 轨收窄了语料范围, 意在过滤远端无关叙事对词典—BERT 分歧的稀释。计算公式与家族一致, dict_avg_tone_ctx 减 (bert_avg_pos_ctx − bert_avg_neg_ctx), 分子分母严格逐轨取 ctx 列, 不借用 full 轨的读数或分母。该轨在留篇门控 full-only 口径下为 conditional-on-full 子集测度: 行宇宙是 full 轨留篇集的子集, per-track 列照算。与 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。在早期试跑 T=2 面板上, 若某银行—年 ctx 侧任一上游列缺席则本列输出 NaN, 与同族 disag、log_sent 的缺失语义一致; 生产 T=19 面板上本轨应正常取值。ctx 轨作为主结果对文本范围敏感性的检验臂: 若迎合度在 full 与 ctx 上同号同量级, 说明结论不由远端无关文本驱动; 若两轨背离, 则提示迎合修辞集中在实体窗口之外的段落, 本身即是可报告的构念性发现。需强调 ctx 的实体窗口判据与 ss 的同句共现判据是两套不同口径的裁剪, 前者围绕目标银行实体扩窗, 后者要求银行与金融科技词严格同句共现, 二者不得互相复用或视作同义。ctx 侧深层基准仍为三模型平均 BERT 的净语气 (正面概率均值减负面概率均值), 词典侧仍为六词典在全部语言学规则下的归一化语气均值, 两侧口径与 full 轨完全一致, 唯文本范围收窄; 因此 full 与 ctx 之差纯粹归因于文本裁剪而非测度口径变化, 使本轨成为干净的文本范围稳健性检验。

## VAR: algo_cater_b_full

【变体差分】
本列是 algo_cater_b 家族的 full 全文轨, 是三轨中文本范围最宽的一条。文本口径为标题 prepend 加全文正文 content_full: 标题作为第 0 句拼入正文, 原始内容列不改动, 覆盖整篇报道而不做实体或同句裁剪。计算公式为 dict_avg_tone_full 减 (bert_avg_pos_full − bert_avg_neg_full), 严格取 full 轨列。在 full-only 留篇门控口径下 (2026-06-29), full 轨承担"是否算一篇银行金融科技报道"的判定基准, 因此 full 轨的行宇宙即为家族的母集, ctx 与 ss 轨是其 conditional-on-full 子集。就构念可解释性而言, full 轨给出发布者在整篇文本层面的词典—深层模型分歧, 是迎合度最直接、覆盖最完整的读数, 通常作为首要报告轨; ctx 与 ss 作为收窄文本范围的稳健性并排轨。与另两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。缺失处理同家族: 无文章行输出 NaN 而非 0, 避免零迎合与无报道混淆。就与姊妹家族 algo_cater 的区分而言, 本 full 列以三模型平均 BERT 为深层基准, algo_cater 的对应列以三家投票 LLM 为深层基准; 二者构念同源、深层模型侧不同, 是同一迎合构念下互为稳健性的并排轨, 不得混入同一 over-identified Hansen J。BERT 侧与 LLM 侧各自独立降级: 某一深层模型缺席只影响自身族的迎合列, 不牵连另一族, 这与 co-primary 嵌入双轨的 both-or-neither 严格 parity 不同。full 轨读数在实证上通常方差最充分, 因其覆盖整篇文本, 词典与深层模型均有最完整的语料可打分, 故迎合度的银行—年异质性在 full 轨上最易识别。

## VAR: algo_cater_b_ss

【变体差分】
本列是 algo_cater_b 家族的 ss 同句共现轨, 文本范围最窄。文本口径为标题 prepend 加银行与金融科技同句共现窗口 content_ss: 仅保留目标银行与金融科技词在同一句子及其上下 N 句半径 (由 filtering 配置 ss_sentence_radius 控制, 默认 1) 内共现的文本, 意在把迎合度锁定到银行确实谈及金融科技的语句上, 排除银行与金融科技在文中各说各话的伪共现。计算公式为 dict_avg_tone_ss 减 (bert_avg_pos_ss − bert_avg_neg_ss), 严格逐轨取 ss 列, 不借 full 或 ctx 分母。ss 回退语义镜像 ctx: 当某银行—年无银行与金融科技同句共现时, content_ss 退化为全文正文、ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母, 属优雅降级而非丢行。在 full-only 门控下本轨为 conditional-on-full 子集测度。与 full、ctx 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。在早期试跑 T=2 面板上 ss 轨因共现稀疏可能大面积回退或零方差, 属预期退化; 生产 T=19 语料上本轨提供最贴近共现语句的迎合度读数。缺失处理同家族, 无文章行输出 NaN。ss 的同句共现判据由 filtering 配置的 ss_sentence_radius 键控制 (默认 1), 与 stage 13 共现硬过滤所用的 cooccurrence_filter.sentence_radius 是两个不同的配置键, 语义亦不同: 前者用于物化 ss 文本轨的语句半径, 后者用于上游丢行的硬过滤判据, 二者不得互相复用。判定的不对称口径为银行侧带否定与短名过滤、金融科技侧为裸词表匹配。就构念区分而言, ss 轨把迎合度收敛到银行确实谈及金融科技的语句, 使读数最贴近"银行—金融科技"这一研究焦点, 但代价是共现稀疏时大面积回退、有效样本收缩, 故只作稳健性并排轨而非首要报告轨; full 轨仍是首要轨, ctx 与 ss 为收窄文本范围的两条互补稳健性轨。三者与 algo_cater 的 LLM 深层基准族正交, 各自 just-identified, 禁混同一 Hansen J。

<!-- rendered-citations:begin -->
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Ash, E., & Hansen, S. (2023). Text algorithms in economics. Annual Review of Economics, 15, 659-688. https://doi.org/10.1146/annurev-economics-082222-074352
Khan, M. H., Hasan, A. B., & Anupam, A. (2024). Social media-based implosion of Silicon Valley Bank and its domino effect on bank stock indices: Evidence from advanced machine and deep learning algorithms. Social Network Analysis and Mining, 14(1), 110. https://doi.org/10.1007/s13278-024-01270-5
Dawid, A. P., & Skene, A. M. (1979). Maximum likelihood estimation of observer error-rates using the EM algorithm. Journal of the Royal Statistical Society Series C (Applied Statistics), 28(1), 20-28. https://doi.org/10.2307/2346806
Bose, I., Hu, N., Liang, P., & Yang, X. (2025). Can Larger Language Models Always Perform Better? A Comparison of GPT, FinBERT, and Dictionaries in Evaluating Management Sentiment. SSRN No. 5153587 [Working Paper]. https://doi.org/10.2139/ssrn.5153587
Kim, W., Spörer, J., Lee, C. L., & Handschuh, S. (2024). Is Small Really Beautiful for Central Bank Communication? Evaluating Language Models for Finance: Llama-3-70B, GPT-4, FinBERT-FOMC, FinBERT, and VADER. Proceedings of the 5th ACM International Conference on AI in Finance, 626-633. https://doi.org/10.1145/3677052.3698675
Lee, J., Stevens, N., & Han, S. C. (2025). Large Language Models in Finance (FinLLMs). Neural Computing and Applications, 37(30), 24853-24867. https://doi.org/10.1007/s00521-024-10495-6
Wang, Y., Wong, T., & Zhang, T. (2026). Does Social Media Identify the Optimistic Bias of State-Controlled Media? Evidence from China. SSRN Electronic Journal No. 6143029 [Working Paper]. https://doi.org/10.2139/ssrn.6143029
<!-- rendered-citations:end -->
