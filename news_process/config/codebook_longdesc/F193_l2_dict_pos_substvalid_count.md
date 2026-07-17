---
family_id: F193
novelty_exempt_rationale: "该家族(dict_pos_substvalid_count)正文明确自陈'并非独立构念度量,而是洗稿率(方法D词典均值臂)除法中被刻意收窄的同域分母',是 dict_pos_count 的技术性排除/有效性收窄变体(substvalid = 实质性属性可测同域筛选),其测度定义学术依据已在母族词典文献(Loughran & McDonald 2011; Du et al. 2022; Bian et al. 2021等)及洗稿率上位构念文献中给出,非独立新构念,故豁免新颖度追新引文要求。"
columns:
- dict_pos_substvalid_count_ctx
- dict_pos_substvalid_count_full
- dict_pos_substvalid_count_ss
unit: 篇数/计数 (count, 银行-年整数计数)
formula: "dict_pos_substvalid_count{track} = Σ_articles ( 1[ mean_d dict_d_score{track} > 0 ] ∧ 1[ innovation_substantiveness_full ∈ {实质性, 象征性} ] ); 篇章级指示 _svd_dict_pos{track} 经 _pool_svd_substvalid_counts 按 target_bank×year 求和"
producer: pipeline\panel\runner.py::build_panel (_svd_dict_pos 构造) + _pool_svd_substvalid_counts (bank-year 聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (六词典 {jiang_2021,yao_2021,bian_2021,du_2022,you_2018,loughran}_score{track})
- 21_tone_llms.parquet (innovation_substantiveness_full)
citations:
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
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: "10.1016/j.frl.2024.105265"
  type: "journal"
  authors: "Huang, J., & Ma, L."
  year: 2024
  title: "Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105265"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 (dict_pos_substvalid_count_full / _ctx / _ss) 度量的是"词典口径的实质性有效正面篇数": 在某一银行-年内, 有多少篇涉该银行金融科技的报道, 既被六词典平均口径判为正面情感, 又同时被大语言模型成功判定了创新实质性属性 (即 innovation_substantiveness 落入 实质性 或 象征性 二值之一, 而非缺测/平局/拒答)。它并不是一个独立的构念度量, 而是"洗稿率" (washing ratio, 方法 D 词典均值臂) 除法中被刻意收窄的同域分母。要理解它, 须先理解上位的脱耦 (decoupling) 与象征性管理 (symbolic management) 构念: 一家银行在新闻话语里表达的对金融科技的正面姿态, 可以是有实质投入支撑的 (实质性), 也可以是纯粹话术包装、缺乏配套行动的 (象征性)。Westphal 与 Zajac 系列研究奠定了这一"实质与象征"的二分传统, 而将其操作化为文本可测量的比率, 需要一个干净的分母: 洗稿率 = 正面且象征性的篇数 ÷ 正面篇数。这里的关键陷阱在于分母该数哪些"正面篇"。

【方法学与计算】
朴素做法是把分母取为全部词典判正的篇数 (物理分母)。但洗稿率的分子 (正面 ∧ 象征性) 隐含要求该篇的实质性属性已被 LLM 成功测量: 若某篇报道 LLM 未能判出实质性/象征性 (返回 nan), 它进不了分子, 那它也不应留在分母里 — 否则分类失败越多, 分母越被稀释放大, 洗稿率被机械地压低, 制造出"洗稿越少"的假象, 而这只是测量缺失的伪影, 不是事实。因此本项引入同域 (subst-valid) 分母: 篇章级指示 _svd_dict_pos{track} 仅在"六词典平均分 > 0" 且 "innovation_substantiveness_full ∈ {实质性, 象征性}"两条件同时成立时置 1, 再由 _pool_svd_substvalid_counts 按 target_bank×year 求和, 得到本家族三列。分子分母遂严格同域, 除法 (_svd_denom → _safe_ratio) 只在这批"既判正又判了实质性"的篇上进行; 旧 schema 缺本列时回退物理分母 (dict_pos_count) 作向后兼容。词典均值口径的"dict"指六部中文金融情感词典 {jiang_2021, yao_2021, bian_2021, du_2022, you_2018, loughran} 逐篇 score 的算术平均, 平均分为正即计入正面 — 这与逐词典单独臂 (方法 D2, 各 {d}_pos_substvalid_count) 互补而不重复。须强调一处不对称口径: 词典正面性 (mean_d score > 0) 是逐轨计算 (full/ctx/ss 各读自身文本轨的 score), 而实质性测量门 innovation_substantiveness_full 恒取 full 轨、三列共享, 与项目 2026-06-29 起确立的 full-only 留篇门控一致 — 一篇报道是否算"一篇银行金科报道"、其实质性属性只以 full 轨判定为准, ctx/ss 降为 conditional-on-full 的稳健性/测度轨。故三列的差异纯粹来自词典正面性分量所读的文本轨不同, 实质性门是共享常量。

【文献定位】
词典法情感测度的方法论基石是 Loughran 与 McDonald (2011) 对 10-K 文本的分析, 他们指出通用情感词典移植到金融语域会系统性误判 (如"liability"在会计语境非负面), 由此确立领域专用词典的必要性 — 本项六词典中的中文金融情感词典 (Du 等 2022; Bian 等 2021) 正是这一传统在中文语料上的延续, Du 等 (2022) 更系统论证了语言与领域双重专用性对中文金融文本测度的增量效度。词典法与机器学习/LLM 法孰优的争论由 Frankel、Jennings 与 Lee (2022) 在 Management Science 上作了对照检验, 他们发现两类方法在披露情感测量上互有短长、宜互为稳健性而非单选一家 — 这直接支撑本项目将词典均值臂 (方法 D) 与 LLM 投票臂、BERT 均值臂并列为多方法洗稿率的做法。van Atteveldt、van der Velden 与 Boukes (2021) 则以人工标注为金标准, 比较了词典、众包与机器学习三类情感分析的效度, 提示词典法在细粒度判别上的局限, 这也正是本项目不单靠词典正面性、而额外叠加 LLM 实质性门以收窄分母的动因。须重申三轨铁律: full/ctx/ss 三列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 词典均值臂与逐词典臂、LLM 臂、BERT 臂之间亦是并排稳健性关系, 同样禁混同一过度识别检验。 至于本家族分子分母共用的「实质性 vs 象征性」二分, Huang 与 Ma (2024) 在同一议题域内提供了直接对应: 该文以金融科技发展为解释变量, 检验其对企业实质性绿色创新与象征性绿色创新的差异化影响, 表明这一二分在中国情境、且恰在金融科技议题下已是可操作的分析范畴, 与本项目 innovation_substantiveness 的二值标签在构念与中文表述上直接呼应。迁移边界须写明: 原文的实质/象征由专利类型 (发明专利 vs 实用新型、外观设计) 客观划分, 主体为非金融上市公司, 金融科技居于解释变量位置; 本项目的实质/象征则由 LLM 对新闻文本判定而非取自专利数据, 主体为商业银行, 金融科技本身即被报道的议题。原文亦未构造任何比率型 washing 指标, 故它只锚定该二分作为构念的正当性, 不锚定本家族以 LLM 判定成功与否来收窄同域分母的设计。
## VAR: dict_pos_substvalid_count_full

【变体差分】
本列为 full 轨: 词典正面性判据读取 full 轨文本 (标题 prepend + 全文正文) 上算出的六词典平均分 — 即 mean_d(du_2022_score_full, jiang_2021_score_full, ...) > 0 时该篇计正面。full 轨是三轨中信息量最全的一轨, 也是本家族的 canonical 参照: 因为实质性测量门 innovation_substantiveness_full 本就取自 full 轨, 故 full 列是唯一"词典正面性分量与实质性门分量同轨"的一列, 二者在同一文本证据面上判定, 无跨轨错配。在项目的 full-only 留篇门控口径下 (2026-06-29), 一篇报道是否算入银行金科报道宇宙、以及其实质性属性, 均以 full 轨为权威判据; ctx/ss 两列的行宇宙是 full 留篇集的子集/条件轨。因此 full 列的计数天然是三列里最"稠密"的一列 (词典判正门槛在全文口径下更易触发, 且实质性门与之同轨), 在下游洗稿率方法 D 中充当分母时数值最稳、最少因跨轨文本差异引入噪声。使用者若需一个不受窗口截断影响的、口径最一致的实质性有效正面篇数, 应以本 full 列为首选; ctx/ss 列则作为对文本窗口收窄敏感性的稳健性对照。本列与逐词典的 {d}_pos_substvalid_count_full 系列 (方法 D2) 构念相同但聚合层级不同: 本列先对六词典逐篇取平均再判正, 逐词典列则各词典独立判正, 二者不可相互替代。三轨各自 just-identified 并排、禁混同一 over-identified Hansen J。

## VAR: dict_pos_substvalid_count_ctx

【变体差分】
本列为 ctx 轨: 词典正面性判据改读 ctx 轨文本上算出的六词典平均分, 即 mean_d({d}_score_ctx) > 0 才计该篇为正面。ctx (context) 轨的文本是"标题 + 目标银行实体上下文窗口" (prepend_title 后, 取银行实体出现处的邻近句窗), 相较 full 全文正文, 它剔除了与目标银行无关的段落, 聚焦于围绕该银行的语境。因此本列相对 full 列的差异纯粹在词典正面性分量: 同一批文章, 在 ctx 收窄文本上重算词典平均分, 正负号可能翻转, 使某些在全文口径下判正的篇不再判正 (或反之), 从而计数与 full 列不同。须特别注意口径不对称: 尽管词典正面性在 ctx 轨上重算, 实质性测量门仍恒取 innovation_substantiveness_full (full 轨, 三列共享), 不随本轨切换 — 这与 full-only 留篇门控一致, ctx 列在此语义下是 conditional-on-full 的测度/稳健性轨, 而非独立门控轨。ctx 列的价值在于检验实质性有效正面篇数对"是否只看银行相关语境"的敏感性: 若主结论在 full 与 ctx 两口径下一致, 说明词典正面信号不是由与银行无关的泛正面报道段落驱动的。本列与 full、ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。ctx 列同样区别于逐词典的 {d}_pos_substvalid_count_ctx (方法 D2): 本列是六词典均值判正, 逐词典列是单词典判正。

## VAR: dict_pos_substvalid_count_ss

【变体差分】
本列为 ss 轨 (银行∧金科同句轨): 词典正面性判据读取 ss 轨文本上算出的六词典平均分, 即 mean_d({d}_score_ss) > 0 才计该篇正面。ss (same-sentence) 轨文本是"标题 + 目标银行与金融科技词在同一句 ± N 窗共现"的最严收窄轨 (窗半径由 config filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语义最聚焦、文本最短的一轨, 只保留银行与金科真正同句共现的证据面。因此本列相对 full/ctx 列, 在词典正面性分量上收窄最甚: 只有银行与金科同句语境里的词汇进入词典打分, 泛化的正面表述被排除, 计数通常最稀疏。ss 轨的回退语义镜像 ctx 轨: 当某篇无银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置 True (与 ctx 的 fallback 机制对称)。与另两轨一致, 实质性测量门仍恒取 innovation_substantiveness_full, 三列共享该 full 轨常量门, 本列在 full-only 留篇门控下为 conditional-on-full 的测度/稳健性轨。ss 列的价值在于提供对"银行与金科关系必须紧邻共现"这一最严判据的敏感性检验: 若实质性有效正面篇数在 ss 极窄口径下仍支撑主结论, 则该正面信号确凿地锚定在银行-金科的直接关联叙事上, 而非松散的同文共现。本列与 full、ctx 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 亦区别于逐词典的 {d}_pos_substvalid_count_ss (方法 D2 单词典臂)。

<!-- rendered-citations:begin -->
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Huang, J., & Ma, L. (2024). Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation. Finance Research Letters, 63, 105265. https://doi.org/10.1016/j.frl.2024.105265
<!-- rendered-citations:end -->
