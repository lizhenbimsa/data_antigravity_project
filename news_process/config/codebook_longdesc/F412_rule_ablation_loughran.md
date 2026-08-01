---
family_id: F412
novelty_exempt_rationale: "该家族是 loughran 词典语调测度在否定/程度副词/转折三条语言学规则 powerset 上的消融变体家族 (rule_ablation_ 前缀), 测度定义依据已在母族 Loughran & McDonald (2011/2016) 词典原始文献中给出, 非独立新构念, 无需追加新文献。"
columns:
- loughran_advonly_tone_ctx
- loughran_advonly_tone_full
- loughran_advonly_tone_ss
- loughran_degadv_tone_ctx
- loughran_degadv_tone_full
- loughran_degadv_tone_ss
- loughran_degonly_tone_ctx
- loughran_degonly_tone_full
- loughran_degonly_tone_ss
- loughran_negadv_tone_ctx
- loughran_negadv_tone_full
- loughran_negadv_tone_ss
- loughran_negdeg_tone_ctx
- loughran_negdeg_tone_full
- loughran_negdeg_tone_ss
- loughran_negonly_tone_ctx
- loughran_negonly_tone_full
- loughran_negonly_tone_ss
- loughran_raw_tone_ctx
- loughran_raw_tone_full
- loughran_raw_tone_ss
unit: 语调得分 (连续, 理论域约 [-1,1]; 文章级状态机打分后按 bank-year 取均值聚合)
formula: 状态机遍历分词序列, 对命中 loughran (Loughran & McDonald 2011 中文主译本) 正/负词条按启用的语言学规则子集(否定翻转 neg / 程度副词 deg / 转折 adv 的 powerset 七臂之一)调整符号或权重后累加, 以 Σ|final| 自归一化得到单篇 [-1,1] 语调, 再按 bank×year 取算术均值
producer: pipeline\sentiment\tone_words.py（文章级状态机打分与消融变体物化） ; pipeline\panel\encode.py（RULE_ABLATION_SUFFIXES 谱驱动 bank-year 聚合, {dict}_{suffix}_tone{track} 面板列生成, 第88-92/774-792行） ; pipeline\panel\export.py（该列族 Stata 变量标签映射, 第655-670行）
upstream: []
citations:
- doi: "10.1111/j.1540-6261.2010.01625.x"
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: "The Journal of Finance"
  vol: "66"
  issue: "1"
  pages_or_artno: "35-65"
- doi: "10.1111/1475-679X.12123"
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: "Journal of Accounting Research"
  vol: "54"
  issue: "4"
  pages_or_artno: "1187-1230"
- doi: "10.1162/COLI_a_00049"
  type: journal
  authors: "Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M."
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: "Computational Linguistics"
  vol: "37"
  issue: "2"
  pages_or_artno: "267-307"
- doi: "10.1016/j.dss.2016.05.009"
  type: journal
  authors: "Pröllochs, N., Feuerriegel, S., & Neumann, D."
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: "Decision Support Systems"
  vol: "88"
  pages_or_artno: "67-75"
- doi: "10.1287/mnsc.2021.4156"
  type: journal
  authors: "Frankel, R., Jennings, J., & Lee, J."
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: "Management Science"
  vol: "68"
  issue: "7"
  pages_or_artno: "5514-5532"
- doi: "10.1111/ecin.13264"
  type: journal
  authors: "Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E."
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: "Economic Inquiry"
  vol: "63"
  issue: "1"
  pages_or_artno: "125-143"
- doi: "10.1057/s41267-025-00798-8"
  type: "journal"
  authors: "Pinto, J., & Siano, F."
  year: 2025
  title: "Beyond words: the challenge of measuring financial text across borders"
  venue: "Journal of International Business Studies"
  vol: "56"
  issue: "7"
  pages_or_artno: "921-936"
- doi: "10.1609/icwsm.v18i1.31443"
  type: "journal"
  authors: "Oh, N."
  year: 2024
  title: "Sentibank: A Unified Resource of Sentiment Lexicons and Dictionaries"
  venue: "Proceedings of the International AAAI Conference on Web and Social Media"
  vol: "18"
  pages_or_artno: "2003-2013"
- doi: "10.1140/epjds/s13688-026-00654-1"
  type: "journal"
  authors: "Pokropek, A."
  year: 2026
  title: "From keyword-based text measures to latent variables: confirmatory factor analysis with word embeddings"
  venue: "EPJ Data Science"
  vol: "15"
  issue: "1"
  pages_or_artno: "51"
- doi: "10.1177/10944281251334777"
  type: "journal"
  authors: "Iqbal, F., & Pfarrer, M. D."
  year: 2025
  title: "Using Coreference Resolution to Mitigate Measurement Error in Text Analysis"
  venue: "Organizational Research Methods"
  pages_or_artno: "10944281251334777"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的构念是: 一套建立在 Loughran & McDonald (2011) 「当负债不算负债」词典学传统之上的中文金融语调测度, 在剥离/保留三条语言学规则的七种子集组合下, 逐句状态机重新打分所得到的消融族。词源是 config/tone_dicts.json 内登记的 loughran_mcdonald_zh_2026 词典 — 该词典是 L&M(2011) JF 原版英文正负极性词表在中文金融报道语境下的主译本, 正面词条 1,295 个、负面词条 3,729 个, 另含 5 类非极性词类(不确定性/诉讼/受限/强弱模态等, 本家族不消费)。这一词典与本仓库另外 5 部词典(jiang_2021/yao_2021/bian_2021/du_2022/you_2018)并列构成 6 词典打分矩阵, 但本家族只聚焦 loughran 一部词典在规则维度上的敏感性, 不做跨词典比较(跨词典比较属另一族群)。构念定位上, loughran 词典因其在英文文献中的规范地位(会计与金融文本分析的事实标准起点, Loughran & McDonald 2016 综述系统总结了其适用边界与常见误用), 被选作"规则消融"这一稳健性练习的载体: 词典本身固定不变, 变的是打分时是否启用否定翻转/程度副词/转折三条语言学规则, 借此拆解"词典选择"与"规则设计"两个独立自由度对语调测度的贡献, 防止读者把某个具体数值结果误归因于词典本身而非规则设定。

【方法学与计算】
打分引擎是逐句/逐词状态机(见 pipeline\sentiment\tone_words.py), 对每篇文章的分词序列扫描, 命中词典正/负词条时先记下基础极性(+1/-1), 随后按当前变体启用的规则集合依次应用调整: 否定翻转规则(neg)在命中词前若干 token 窗口内检测否定词, 命中则将该词极性反号(把"不好"从负面词"好"的否定还原为负面, 或把"不差"从负面词翻正); 程度副词规则(deg)在命中词前检测强度副词(如"极其""略微"), 对该词的贡献施加放大或缩小的权重乘子, 而非改变符号; 转折规则(adv)检测句内转折连词(如"但是""然而"), 对转折之后的分句给予不同权重(生产口径下调转折前半句权重, 强调转折后语义), 体现"但是"后面才是说话人真实态度的语用学共识。七个非-full 变体对应三条规则的幂集去掉全启用(loughran_tone/loughran_full, 即三规则全开的 canonical 主测度, 不在本家族内, 属另一 canonical 列)与全不启用两个端点中的后者被本家族收录为 raw(三规则全关, 只做裸词典计数打分)以及五个中间组合: negonly(仅开否定)/degonly(仅开程度副词)/advonly(仅开转折)/negdeg(开否定+程度副词)/negadv(开否定+转折)/degadv(开程度副词+转折)。每个变体独立完成一次全语料状态机重跑, 单篇最终语调以 Σ|final| 做自归一化处理, 即把所有命中词经规则调整后的正负贡献分别求和, 再除以全部贡献绝对值之和, 得到落在 [-1,1] 区间、对词数多寡不敏感的比例化语调值; 这一自归一化设计使得不同变体之间、不同长度文章之间的语调分值具有跨观测可比性。文章级打分完成后, 在 pipeline\panel\export.py 中按 bank×year 分组取算术均值聚合成面板列, 聚合前不做温莎化或截尾(截尾发生在下游描述统计/回归稳健性检验环节, 非本家族产出阶段职责)。

【文献定位】
本家族的方法学谱系直接承袭 Loughran & McDonald (2011, The Journal of Finance) 的词典打分范式 — 该文首次系统证明通用情感词典(Harvard-IV)在金融文本上大量误判, 提出金融领域专属正负词表, 是文本分析在会计与金融研究中确立方法论地位的奠基文献, 亦是本 codebook 顶刊锚点; 其后续综述(Loughran & McDonald, 2016, Journal of Accounting Research)系统盘点了词典法在会计金融文献中的应用谱系与常见方法学陷阱, 为本家族"规则消融需要披露、不能默认单一规则设定"的设计动机提供直接依据。规则层面, 否定翻转与转折处理的必要性呼应词典法综述 Taboada et al. (2011, Computational Linguistics) 对"上下文调整词(contextual valence shifters)"——包括否定词、强化/弱化词、转折连词——系统性影响词汇情感极性判断这一发现的中文场景落地; negonly 臂的设计动机直接对应 Pröllochs, Feuerriegel & Neumann (2016, Decision Support Systems) 关于否定作用域检测对新闻驱动交易信号质量的可观测影响。方法论正当性上, Frankel, Jennings & Lee (2022, Management Science) 对比机器学习与词典法两条路径测得的信息含量差异, 提示词典法内部的规则设定选择(而非仅词典或机器学习二选一)本身即构成一个值得系统披露的自由度, 这正是本家族存在的方法学理由; 更晚近的 Barbaglia, Consoli, Manzan, Tiozzo Pezzoli & Tosetti (2025, Economic Inquiry) 对经济文本词典法的系统评估进一步确认, 词典法的规则组件(而非仅词表本身)对最终情感分数的方差贡献不可忽视, 支持本家族"三规则全 powerset 物化并披露"而非仅报告单一"最优"规则组合的设计立场。

按照仓库当前状态铁律, 本家族的三条正交自由度须严格分层理解: 其一是三轨自由度(full/ctx/ss), 三者对应不同文本窗口(全文/实体上下文窗口/银行∧金科同句窗口), 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定; 其二是留篇门控口径, 2026-06-29 起门控判定统一改为仅看 full 轨 llm_verified_full, ctx/ss 是 conditional-on-full 的测度轨, 行宇宙是 full 留篇集合的子集; 其三是回退语义, 当某篇文章不存在银行∧金科同句共现时 content_ss 回退为全文 body 且 ss_is_fallback 置 True(镜像 content_ctx 回退语义, 分母 n_articles 共享)。本家族的七规则消融维度与三轨维度、与家族外的政治词权重梯度(du_2022 专属)完全正交、互不交叉, 词典消融梯度内部各变体之间也是各自独立的 just-identified 并排关系, 不构成任何联合过识别设定; 使用者若要检验某一具体语言学规则(如否定处理)对语调测度稳健性的边际贡献, 应固定轨道比较七个规则变体的差异, 而不应把七变体×三轨的 21 列一并塞入单一回归右手方作为工具变量集合。 晚近前沿在若干侧面补强了上述分层。首先, 本家族所用词表是 Loughran & McDonald (2011) 的中文主译本, 这一把美国基准词表移出本国语境的动作本身即是一项应被披露的测度风险: Pinto 与 Siano (2025) 以 85 个国家、200,960 份财报电话会记录 (文本本身即英文) 为语料, 把美国基准词表直接套用其上, 发现情感与收益的关联在非美国公司弱约 30%, 且定谳主因是文化距离而非语言 (语言特征仅作文化价值的工具变量); 其含义是 L&M 式美国基准词表一旦移出美国语境, 即使文本仍是英文, 信号强度亦系统性衰减, 那么把该词表移入中国语境 (既跨文化、又另加中文翻译) 风险只会更大, 这正是本项目既保留 loughran 译本轨、又并置多部本土中文词典与多个规则臂的动机之一。该条须按限定口径引用: 原文全文无词表翻译、亦无非英语语料, 语料为财报电话会记录而非中文金融新闻, 讨论对象是美国基准词表移出本国语境后的信号衰减, 并未涉及否定/程度/转折规则子集的消融设计, 亦无银行-年度聚合层级。其次, Oh (2024) 指出情感分析在可解释性上的困难并明确背书「依赖专家词表的规则法能提供透明性」, 同时以资源碎片化与验证缺失为问题意识, 把 15 部原始情感词典与 43 部预处理词典整合入 sentibank 库 (覆盖 7 类体裁、6 个领域), 说明规则/词典法作为可解释测度分支在当代前沿仍被背书, 支持本家族保留词典状态机语调轨; 但其覆盖为英文社交媒体等体裁, 不含本项目所用中文金融词典, 未实现三规则状态机, 亦未主张「不同词典给出不同极性故须并排使用」, 故仅止于取向层面的佐证, 与规则消融稳健性检验无直接关联。第三, Pokropek (2026) 指出词典法中研究者选定的关键词极少像量表题项那样接受心理测量学检验 (罕有报告信度、评估内部结构或检验测量不变性), 遂提出把单个关键词视为同一潜变量的观测指标、以词嵌入的中心化余弦相似度矩阵为输入作验证性因子分析, 借以估计载荷与拟合指数、计算信度并检验不变性; 这一心理测量学立场与本家族「规则设定不能默认、须全 powerset 物化并披露」的动机同向。须注意指标层级不同: 原文的观测指标是一部词表之内的单个关键词, 整合方式为基于嵌入的 CFA 载荷估计, 语料为社会科学文本, 且未在规则消融的任一臂上分别整合, 不涉及否定/程度/转折规则。最后, Iqbal 与 Pfarrer (2025) 证明情感分析在多主体文本中的情感归属上存在系统性测量误差, 并以共指消解作为解法、经两项研究显示可降低测量误差, 由此确立「一项具体的语言学处理选择会系统性改变文本测度取值、并构成实质性测量误差来源」这一一般命题, 支持本家族对规则不作默认采纳而显式披露其后果。其边界须严格声明: 原文规则是共指消解 (实体指代还原), 与本家族三规则非同一规则, 其在本项目中的对应物是 ctx/ss 实体窗口轨而非规则消融族; 且原文取规范性立场、主张采纳该规则以减少误差, 而本家族令七臂 just-identified 并排、互为稳健性不分主次, 故不得据以视之为 powerset 规则消融设计的同构先例。
## VAR: loughran_advonly_tone_ctx

【变体差分】
本列在 loughran 词典打分中仅启用转折规则(adv), 否定翻转与程度副词规则均关闭, 文本轨道为 ctx(标题 + 实体上下文窗口, 由 stage 14 ctx_materializer 物化的 content_ctx, 遵循 prepend_title 拼接约定)。与 canonical 三规则全开的 loughran_tone_ctx 相比, 本列只捕捉"转折连词导致的分句权重再分配"这一单一机制的净效应, 不含否定翻转带来的符号反转、也不含程度副词带来的强度加权; 因此本列语调值与 canonical 值之间的差异, 可被干净地归因于否定/程度两条规则在 ctx 轨的边际贡献之和。作为规则消融七臂之一, 本列与 loughran_advonly_tone_full/loughran_advonly_tone_ss 构成同一规则设定下的三轨并排, 互为稳健性、不分主次, 亦与另外六个规则变体(raw/negonly/degonly/negdeg/negadv/degadv)在 ctx 轨内互为稳健性并排, 全部 just-identified, 不得混入同一 over-identified Hansen J。行宇宙遵循 full-only 留篇门控: 只有 llm_verified_full 为真的文章才计入聚合分母, ctx 轨作为 full 留篇集合的子集条件测度存在; 若该文章不含实体上下文窗口的有效抽取, content_ctx 回退为全文, 对应 ctx_is_fallback 置真, 参与本列打分时不做特殊剔除, 而是与非回退观测一并计入均值(回退比例可作为该家族数据质量披露项)。转折规则的触发依赖实体上下文窗口内是否完整保留了转折连词及其前后分句, 若窗口截断恰好落在转折连词处, 该规则可能无法完整识别分句边界, 这是 ctx 轨相较 full 轨在解读本列时应额外考虑的窗口效应, 建议与 loughran_advonly_tone_full 做差值对照以估计窗口截断对转折规则触发率的具体影响幅度, 而非直接假定二者应高度一致。

## VAR: loughran_advonly_tone_full

【变体差分】
本列在 loughran 词典打分中仅启用转折规则(adv), 否定翻转与程度副词规则关闭, 文本轨道为 full(标题 + 全文正文, 三轨中信息覆盖面最广、不依赖实体窗口抽取质量的基准轨)。作为 full 轨在七规则消融矩阵中的一格, 本列与同规则设定的 loughran_advonly_tone_ctx / loughran_advonly_tone_ss 并列, 三轨互为稳健性、不分主次; 同时本列与 loughran_raw_tone_full / loughran_negonly_tone_full / loughran_degonly_tone_full / loughran_negdeg_tone_full / loughran_negadv_tone_full / loughran_degadv_tone_full 在 full 轨内部构成七臂并排, 分别单独承载"仅转折""三规则全关""仅否定"等语言学假设, 均 just-identified, 不应混入同一过识别设定。留篇门控判定本身即以 full 轨 llm_verified_full 为准, 因此本列的行宇宙即门控判定所依据的核心集合, 不存在回退语义问题(full 轨不设 is_fallback 标记, 因为全文本身即是回退的目标状态)。本列的方法学意义在于: 若某研究结论在开启转折规则、关闭其余两条规则的设定下依然成立, 则说明该结论对"是否处理转折连词"这一具体建模选择不敏感, 是稳健性论证链条中的一个具体证据点, 而非独立的主张。由于本轨是三轨中信息覆盖面最广、不受实体窗口抽取误差影响的基准轨, 本列亦是判断"转折规则的边际贡献是否受窗口截断放大或缩小"这一问题的对照锚点: 将本列与 loughran_advonly_tone_ctx / loughran_advonly_tone_ss 的差值和 canonical 三轨对应差值相比较, 若差值幅度接近, 说明转折规则的触发对文本窗口宽窄不敏感; 若 ctx/ss 轨差值明显偏离本列, 则提示窗口截断确实系统性地改变了转折连词的可检测性, 应在稳健性附录中一并披露该窗口效应, 而非默认三轨结果可直接互换解读。

## VAR: loughran_advonly_tone_ss

【变体差分】
本列在 loughran 词典打分中仅启用转折规则(adv), 文本轨道为 ss(标题 + 银行∧金科同句±N窗口, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认半径为 1)。ss 轨相较 ctx 轨窗口更窄、语境更聚焦于银行与金融科技词汇同句共现的局部语义, 因此本列捕捉的是"转折规则在高度局部化文本窗口内"对语调分值的边际影响, 与 full/ctx 两轨的对应列构成三轨并排稳健性证据, 互为稳健性不分主次, 且与本轨内另六个规则消融变体(raw/negonly/degonly/negdeg/negadv/degadv 的 _ss 版本)just-identified 并排。回退语义严格镜像 ctx 轨: 若某篇文章不存在银行∧金科词汇同句共现(即 stage 13 共现硬过滤保留但无法在句级别定位同句窗口的边界情形, 或该文章未通过更细粒度的句级判定), content_ss 回退为全文 body, ss_is_fallback 置真, 与 ctx_is_fallback 共享 n_articles 分母口径, 不因回退而单独调整聚合权重。留篇门控仍以 full 轨为准, ss 轨是 full 留篇集合的条件测度子集。本列在实证使用上应被理解为"三条语言学规则中只保留转折处理"这一假设在最严格局部语境下是否依然稳健的证据点, 与家族内其余 20 列共同构成完整的规则×轨道敏感性网格。因转折连词往往跨句连接前后两个分句而 ss 轨窗口最窄, 本列受窗口截断的影响预期在七个规则消融变体的 ss 版本中最为显著, 建议将本列与 loughran_advonly_tone_ctx / loughran_advonly_tone_full 的差值联合报告, 以清晰区分"转折规则本身的边际贡献"与"窗口宽度对该规则可及性的截断效应"两种不同来源的数值差异, 避免读者把窗口效应误认成规则语言学假设本身的失效。

## VAR: loughran_degadv_tone_ctx

【变体差分】
本列同时启用程度副词规则(deg)与转折规则(adv), 否定翻转规则(neg)关闭, 文本轨道为 ctx。与仅单规则的 advonly/degonly 相比, 本列刻画的是"强度加权"与"转折分句再权重"两条机制的联合效应, 但排除否定翻转带来的符号反转, 因此本列与 canonical loughran_tone_ctx 之间的差异可归因于否定规则单独的边际贡献。作为七臂消融矩阵中"两规则组合"三格之一(negdeg/negadv/degadv), 本列与 loughran_degadv_tone_full / loughran_degadv_tone_ss 构成三轨并排, 亦与 ctx 轨内其余六变体 just-identified 并排, 互为稳健性、不分主次, 不得混入同一 over-identified Hansen J。行宇宙遵循 full-only 门控, ctx 轨的回退语义(无实体上下文窗口时回退全文、ctx_is_fallback 置真)与本家族其余 ctx 列一致, 不做特殊处理。本列的诊断价值在于: 当研究者怀疑某一发现主要由否定翻转规则驱动时, 本列(关闭否定、保留另两条规则)与 negdeg/negadv(保留否定、关闭另一条)的对比可以直接分离否定规则的边际贡献大小。此外, 由于程度副词与转折规则都不改变词条基础符号(只调整幅度或分句权重), 本列语调值的正负方向预期与 raw_tone_ctx 高度一致, 主要差异体现在幅度上而非方向翻转上; 若观测到本列与 raw_tone_ctx 出现方向性分歧, 应优先怀疑打分引擎实现或分词边界识别存在异常, 而非归因于程度/转折两条规则本身的正常语言学调整效应, 这是使用本列做数据质量诊断时的一条实用经验法则。

## VAR: loughran_degadv_tone_full

【变体差分】
本列同时启用程度副词规则与转折规则, 关闭否定翻转规则, 文本轨道为 full。作为 full 轨七臂矩阵中的一格, 本列与同规则设定的 _ctx/_ss 版本三轨并排互为稳健性, 亦与 full 轨内其余六变体(raw/negonly/degonly/negadv/negdeg/advonly)just-identified 并排, 全部不分主次、禁混入同一过识别设定。留篇门控直接以本轨 llm_verified_full 为准, 不存在回退语义。本列在方法论叙事中承担"排除否定规则单独效应"的角色: 若某研究结论在 canonical(三规则全开)与本列(缺否定)之间数值方向一致、幅度相近, 则说明否定翻转规则对结论的贡献有限, 反之则提示否定处理是驱动结论的关键建模选择, 需要在稳健性附录中专门讨论。该列与 negdeg_tone_full(保留否定、关闭转折)、negadv_tone_full(保留否定、关闭程度副词)共同构成完整的"缺一验证"矩阵, 便于逐条规则的边际贡献核算, 但三者之间彼此并列, 不构成任何联立方程或工具变量层级关系。作为 full 轨基准, 本列亦是 loughran_degadv_tone_ctx 与 loughran_degadv_tone_ss 做窗口效应对照的锚点: 由于转折规则对窗口宽窄较为敏感而程度副词规则相对不敏感, 三轨对应列之间的差异预期主要来自转折规则触发率随窗口收窄而下降, 建议在解读三轨差异时将该效应与"否定规则单独边际贡献"两条解释路径分开讨论, 避免混淆规则本身失效与窗口截断两种截然不同的成因。

## VAR: loughran_degadv_tone_ss

【变体差分】
本列同时启用程度副词与转折规则, 关闭否定翻转规则, 文本轨道为 ss。ss 轨窗口最窄、语境最聚焦于银行∧金科同句共现, 本列反映的是这两条规则组合在最局部化文本上的联合效应, 与 full/ctx 两轨对应列构成三轨并排、互为稳健性不分主次。回退语义严格镜像 ctx(镜像先例, 无同句共现则回退全文、ss_is_fallback 置真, 分母口径与 ctx_is_fallback 共享), 留篇门控以 full 轨为准。该列与本轨内 negdeg_tone_ss/negadv_tone_ss/advonly_tone_ss/degonly_tone_ss/negonly_tone_ss/raw_tone_ss 共同构成 ss 轨完整的七臂并排矩阵, 均 just-identified, 不与其他轨道或家族外测度混入同一过识别设定。使用建议: 由于 ss 轨样本天然更依赖同句共现是否成立(回退比例通常高于 ctx), 在解读本列与 canonical 差异时应同时报告该轨的回退比例, 避免把"窗口过窄导致回退占比高"误读为"规则设定本身导致的测度偏移"。此外, 转折规则依赖跨句语境(转折连词往往连接前后两个分句), 在 ss 轨±1 句默认半径下, 若转折连词恰好落在窗口边界之外, 该规则实际不会触发, 使本列在很多观测上退化为等价于纯裸计数打分; 这一现象不是测度偏差, 而是窗口设计本身决定的规则可及性约束, 建议在稳健性附录中以窗口半径作为额外的敏感性维度加以说明, 并结合回退比例与转折规则实际触发率两项诊断指标联合披露, 以帮助读者正确理解 ss 轨消融结果的适用边界。程度副词规则相较转折规则受窗口宽度影响更小, 因为强度副词通常紧邻其修饰的词条出现在同一分句内, 不易被窗口半径截断, 因此本列相较纯 advonly_tone_ss 更能稳定复现 full/ctx 两轨的方向性结论。

## VAR: loughran_degonly_tone_ctx

【变体差分】
本列仅启用程度副词规则(deg), 否定翻转与转折规则均关闭, 文本轨道为 ctx。相较 canonical, 本列只保留"强度副词对命中词权重的放大/缩小"这一单一机制, 不含否定翻转的符号反转、也不含转折规则的分句再权重, 因此本列与 canonical 之间的差异可归因于否定规则与转折规则两者边际贡献之和(与 advonly 互补对照)。本列作为七臂矩阵中单规则三格之一(negonly/degonly/advonly), 与 loughran_degonly_tone_full / loughran_degonly_tone_ss 构成三轨并排, 亦与 ctx 轨内其余六变体 just-identified 并排, 互为稳健性不分主次。行宇宙与回退语义与本家族其余 ctx 列一致(full-only 门控, 无实体窗口时回退全文)。程度副词规则本身语义较为"温和"(只调幅度不调符号), 因此本列与 raw(三规则全关)之间的数值差异通常小于 negonly/advonly 与 raw 的差异, 这是解读该列时应有的先验预期, 便于快速判断规则设定对语调测度的敏感程度量级。另一方面, 由于程度副词在实体上下文窗口内出现的位置通常紧邻其修饰的极性词(强度副词一般直接前置于被修饰词, 罕见跨句甚至跨长距离修饰), 该规则相较转折规则受 ctx 窗口截断的影响更小, 触发率预期更接近 full 轨对应列; 因此在评估"哪条规则对窗口宽度最不敏感"这一元问题时, degonly 系三轨列(本列与其 full/ss 对应列)通常是最稳定的参照组, 可优先作为窗口效应研究的基准。

## VAR: loughran_degonly_tone_full

【变体差分】
本列仅启用程度副词规则, 文本轨道为 full。作为 full 轨七臂矩阵一格, 与同规则设定的 _ctx/_ss 版本三轨并排互为稳健性, 与 full 轨内其余六变体 just-identified 并排。留篇门控以本轨 llm_verified_full 直接判定, 无回退语义问题。本列与 raw_tone_full 的差值即"仅开启程度副词规则"对全文轨语调分值的净贡献, 是规则敏感性核算矩阵中最基础的构造块之一; 结合 negonly_tone_full 与 advonly_tone_full 的对应差值, 三者理论上应大致可加(在词典打分状态机不存在规则间强交互效应的前提下)近似还原 canonical 与 raw 之间的总差异, 但由于状态机内部规则应用存在窗口重叠与优先级顺序(实际实现按代码内规则应用顺序逐条叠加, 非严格可加分解), 不应假定三者精确可加, 而应将其作为方向性、量级性的诊断依据看待, 不作为精确分解公式使用。本列作为 full 轨基准, 亦是 loughran_degonly_tone_ctx 与 loughran_degonly_tone_ss 做窗口效应对照时的锚点参照: 三者若数值高度一致, 说明程度副词规则的触发对文本窗口宽窄不敏感(因强度副词一般紧邻其修饰词, 罕见被窗口截断); 若三者出现系统性偏离, 则应结合各轨回退比例与命中词数分布进一步排查, 而不宜简单归因为规则本身的不稳定。

## VAR: loughran_degonly_tone_ss

【变体差分】
本列仅启用程度副词规则, 文本轨道为 ss。作为 ss 轨七臂矩阵一格, 与 full/ctx 两轨对应列构成三轨并排互为稳健性、不分主次, 回退语义镜像 ctx(无同句共现回退全文、ss_is_fallback 置真), 留篇门控以 full 轨为准。由于 ss 轨文本窗口最窄, 单篇内命中程度副词的绝对次数通常显著少于 full/ctx 两轨, 该列在早期试跑 T=2 开发规模等小样本场景下更容易出现方差较低甚至局部退化的情形, 属该窗口设计下的预期表现而非缺陷; 在生产全量语料(T=19, 约 1,819 万条量级)下样本量充足, 该退化风险大幅降低。本列与本轨内 raw_tone_ss 的差值构成程度副词规则在最局部化语境下的边际贡献估计, 是规则×轨道完整敏感性网格中的一格, 与其余各格互为稳健性并排, 不构成任何层级依赖关系。由于强度副词一般紧邻其修饰的极性词、罕见跨句出现, 该规则在 ss 轨极窄窗口内的可及性预期高于转折规则, 本列与 loughran_degonly_tone_ctx / loughran_degonly_tone_full 的相关性预期在七个非-full 变体的三轨对照中相对稳定, 可作为评估"规则语义局部性 vs 窗口宽度"这一交互命题的一组自然对照, 供研究者判断具体语言学规则是否适合在极窄窗口下继续使用。

## VAR: loughran_negadv_tone_ctx

【变体差分】
本列同时启用否定翻转规则(neg)与转折规则(adv), 程度副词规则(deg)关闭, 文本轨道为 ctx。与仅单规则变体相比, 本列刻画否定翻转与转折分句再权重两条机制的联合效应, 排除强度加权机制, 因此与 canonical 的差异可归因于程度副词规则单独的边际贡献。作为两规则组合三格之一, 本列与 loughran_negadv_tone_full / loughran_negadv_tone_ss 构成三轨并排, 与 ctx 轨内其余六变体 just-identified 并排, 互为稳健性不分主次。留篇门控与回退语义与本家族其余 ctx 列一致。由于否定翻转是三条规则中语义强度最大的一条(能直接反转词条符号, 而非仅调整幅度), 本列与 raw 之间的数值差异预期通常大于纯 degonly 或纯 advonly 与 raw 的差异, 这一先验有助于快速判断某一具体文章的语调测度对否定处理是否高度敏感, 尤其在包含大量否定句式的报道(如"未能达标""不构成重大不利影响"等金融文本常见句式)中效应更为显著。由于否定翻转规则受窗口截断影响较小、转折规则受影响较大, 本列相较 loughran_degadv_tone_ctx(否定关闭、转折保留)预期更稳定地复现 full 轨对应结论; 与 loughran_negadv_tone_full / loughran_negadv_tone_ss 的三轨对比, 可用于分离"窗口宽度对转折规则可及性的截断效应"这一成分, 是七臂矩阵中兼具诊断否定与转折两条规则边际贡献的复合型证据点。

## VAR: loughran_negadv_tone_full

【变体差分】
本列同时启用否定翻转与转折规则, 关闭程度副词规则, 文本轨道为 full。作为 full 轨两规则组合一格, 与同规则设定的 _ctx/_ss 版本构成三轨并排互为稳健性, 与 full 轨内其余六变体 just-identified 并排。留篇门控以本轨为准判定, 无回退语义。本列与 negdeg_tone_full(保留否定、关闭转折)、degadv_tone_full(关闭否定、保留转折+程度)构成一组互补对照, 三者两两对比可分离出否定/转折/程度三条规则在全文轨上的两两交互模式(注意: 状态机实现下规则应用存在顺序依赖, 交互效应不是简单可加, 但两两对照仍能提供方向性证据)。本列在 canonical(三规则全开)与 negdeg(缺转折)之间的相对位置, 是判断"转折处理是否对全文轨语调测度产生额外边际信息增量"的直接诊断依据, 尤其适用于财经报道中常见的"业绩承压, 但管理层维持全年指引不变"这类先抑后扬句式的语调捕捉能力评估。作为 full 轨基准, 本列亦是 loughran_negadv_tone_ctx 与 loughran_negadv_tone_ss 做窗口效应对照的参照锚点: 因转折规则易受窗口截断影响而否定翻转规则相对稳定, 三轨差异预期主要来自转折规则触发率随窗口收窄而系统性下降, 而非否定规则本身在不同轨道上表现不一致, 解读三轨结果分歧时应优先考察转折连词是否落在窗口边界之外这一具体机制。

## VAR: loughran_negadv_tone_ss

【变体差分】
本列同时启用否定翻转与转折规则, 关闭程度副词规则, 文本轨道为 ss。作为 ss 轨两规则组合一格, 与 full/ctx 两轨对应列构成三轨并排互为稳健性, 回退语义镜像 ctx(无同句共现回退全文、ss_is_fallback 置真), 留篇门控以 full 轨为准。由于 ss 轨窗口聚焦银行∧金科同句共现, 转折连词若恰好出现在窗口边界外(例如转折发生在窗口半径 N 之外的相邻句), 该规则在 ss 轨的实际触发率可能显著低于 full/ctx 两轨, 造成本列数值更贴近 negonly_tone_ss 而非预期的"否定+转折"联合效应, 这是解读 ss 轨规则消融列时需要留意的窗口截断效应, 应结合窗口半径参数(ss_sentence_radius)一并披露, 而非直接类比 full/ctx 轨的规则触发行为。本列与本轨内其余六变体 just-identified 并排, 互为稳健性不分主次。相较之下, 否定翻转规则受窗口截断影响较小(否定词通常紧邻其修饰词, 罕见落在窗口边界外), 因此本列在数值上更贴近 negonly_tone_ss 而非贴近保留完整转折效应的 canonical, 这一"退化倾向"本身即是一条有用的诊断信息: 若研究者观测到 ss 轨的 negadv 列与 negonly 列高度相近, 可据此推断该样本中转折句式恰好集中出现在窗口半径覆盖不到的相邻句, 而非否定或转折规则实现存在缺陷。

## VAR: loughran_negdeg_tone_ctx

【变体差分】
本列同时启用否定翻转规则与程度副词规则, 转折规则(adv)关闭, 文本轨道为 ctx。本列刻画的是否定符号反转与强度加权两条机制的联合效应, 排除转折分句再权重机制, 与 canonical 的差异可归因于转折规则单独的边际贡献。作为两规则组合三格之一, 本列与 loughran_negdeg_tone_full / loughran_negdeg_tone_ss 构成三轨并排, 与 ctx 轨内其余六变体 just-identified 并排, 互为稳健性不分主次, 留篇门控与回退语义与本家族其余 ctx 列一致。因否定+程度两条规则组合覆盖了绝大多数中文金融语调判断中最常见的语言学修饰(否定句式与强度副词几乎在每篇报道中都会出现, 而转折句式相对少见), 本列在数值上通常最接近 canonical(三规则全开)的表现, 是七个非-full 变体中与主测度相关性预期最高的一格, 可作为"转折规则是否可被安全省略"这一简化建模假设的直接检验对象。本列与 loughran_negdeg_tone_full / loughran_negdeg_tone_ss 构成同规则设定的三轨并排, 互为稳健性不分主次; 由于否定与程度两条规则本身受窗口截断影响都相对有限(均依赖局部而非跨句语境), 三轨对应列之间的数值差异预期显著小于涉及转折规则(adv)的其余变体在三轨间的差异, 这一"跨轨稳定性梯度"本身可作为快速判断某一具体规则是否对文本窗口宽度敏感的经验法则, 供后续窗口设计选择参考。

## VAR: loughran_negdeg_tone_full

【变体差分】
本列同时启用否定翻转与程度副词规则, 关闭转折规则, 文本轨道为 full。作为 full 轨两规则组合一格, 与同规则设定的 _ctx/_ss 版本构成三轨并排互为稳健性, 与 full 轨内其余六变体 just-identified 并排。留篇门控以本轨直接判定, 无回退语义。由于本列覆盖否定与程度两条最常见的语言学修饰规则, 其与 canonical loughran_tone_full 之间的相关系数预期在七个非-full 变体中最高, 若实证发现本列与 canonical 出现较大分歧, 应优先怀疑该样本中转折句式占比异常偏高(例如报道大量使用"尽管…但是…"结构描述银行业绩), 而非默认归因于打分引擎实现问题。本列亦是 negdeg 系三轨中的 full 基准, 供 ctx/ss 对应列做窗口效应对照时的锚点参照。因否定与程度副词两条规则受窗口截断影响都较小, 本列与 loughran_negdeg_tone_ctx / loughran_negdeg_tone_ss 预期数值高度一致, 三者之间的偏离若出现, 应优先怀疑分词或窗口边界识别环节存在异常, 而非默认归因于规则设定在不同轨道上表现不一致; 这一跨轨高一致性预期也使本列成为检验"消融口径实现是否跨轨一致"这一底层数据质量问题的天然回归检验点。

## VAR: loughran_negdeg_tone_ss

【变体差分】
本列同时启用否定翻转与程度副词规则, 关闭转折规则, 文本轨道为 ss。作为 ss 轨两规则组合一格, 与 full/ctx 两轨对应列构成三轨并排互为稳健性, 回退语义镜像 ctx(无同句共现回退全文、ss_is_fallback 置真), 留篇门控以 full 轨为准。因 ss 轨窗口本身已高度聚焦于银行与金融科技词汇的同句语境, 否定与程度副词规则在该窗口内的触发率相对稳定(不像转折规则那样依赖跨句语境), 本列预期是 ss 轨七个变体中数值上最贴近 canonical loughran_tone_ss 的一格, 可作为 ss 轨"省略转折规则是否可接受"这一简化假设的经验依据, 与 full/ctx 对应结论做跨轨比对时应留意 ss 轨样本量与回退比例对该结论稳健性的潜在影响。本列与 loughran_negdeg_tone_ctx / loughran_negdeg_tone_full 构成三轨并排, 互为稳健性不分主次; 由于否定与程度两条规则触发均不依赖跨句语境, 即便 ss 轨窗口极窄, 该两条规则的可及性预期仍与 full/ctx 两轨基本一致, 故本列是七个非-full 变体的 ss 版本中受窗口收窄影响最小、跨轨一致性最强的一格, 适合作为评估 ss 轨整体测度质量的稳定性基准。若研究者需要在 ss 轨这一最严格窗口设定下检验语调测度对语言学规则设计的敏感性, 本列与 canonical loughran_tone_ss(三规则全开)之间数值差异中不涉及的部分即可视为转折规则贡献的上界估计, 是分离转折规则单独效应时最经济的参照列, 无需额外构造中间变体即可获得该项分解。

## VAR: loughran_negonly_tone_ctx

【变体差分】
本列仅启用否定翻转规则(neg), 程度副词与转折规则均关闭, 文本轨道为 ctx。作为七臂矩阵中语义强度最大的单规则变体, 本列与 raw_tone_ctx 的差值即否定翻转规则在 ctx 轨的独立边际贡献, 预期是三条单规则变体(negonly/degonly/advonly)中与 raw 差异幅度最大的一格, 因为否定翻转直接反转词条符号而非仅调整幅度。该结论呼应文献中否定处理对情感极性判断具有一阶重要性的一致发现(参见 Pröllochs, Feuerriegel & Neumann 2016 关于新闻文本否定作用域检测对交易信号质量的直接影响)。本列与 loughran_negonly_tone_full / loughran_negonly_tone_ss 构成三轨并排, 与 ctx 轨内其余六变体 just-identified 并排, 互为稳健性不分主次, 留篇门控与回退语义与本家族其余 ctx 列一致。由于否定词与被否定极性词之间的距离通常较短(否定副词一般紧邻其修饰的动词或形容词, 罕见跨句), 该规则在 ctx 窗口内的触发率预期与 full 轨接近, 受窗口截断的影响相对有限, 因此本列可作为衡量"窗口宽窄是否系统性改变某条规则可及性"这一问题时较为稳定的对照组, 与转折规则(advonly 系列, 受窗口截断影响更明显)形成鲜明对比。

## VAR: loughran_negonly_tone_full

【变体差分】
本列仅启用否定翻转规则, 文本轨道为 full。作为 full 轨语义强度最大的单规则变体, 本列与 raw_tone_full 的差值构成否定规则边际贡献的全文轨基准估计, 与 negonly_tone_ctx / negonly_tone_ss 构成三轨并排互为稳健性。留篇门控以本轨直接判定, 无回退语义。在中文金融报道语境下, 否定句式(如"未""不""未能""无法"等)出现频率高且往往直接决定句子的实际情感取向(例如"不良贷款率未见明显改善"中的"未见"直接反转"改善"一词的正面极性), 因此本列在实证解读中通常被视为规则消融七臂里方向性信息含量最高的单规则变体, 与 canonical 三规则全开版本的相关性预期高于 degonly/advonly 两个单规则变体, 但仍应作为独立的稳健性证据点使用, 不应替代 canonical 作为主测度。作为 full 轨基准, 本列亦是 loughran_negonly_tone_ctx 与 loughran_negonly_tone_ss 做窗口效应对照的锚点: 由于否定翻转规则受窗口截断影响相对较小(否定词通常紧邻其修饰词), 三轨对应列预期数值高度一致, 若观测到系统性偏离应优先排查分词或窗口边界识别环节, 而非默认归因于规则本身在不同轨道上的表现差异。

## VAR: loughran_negonly_tone_ss

【变体差分】
本列仅启用否定翻转规则, 文本轨道为 ss。作为 ss 轨语义强度最大的单规则变体, 与 full/ctx 两轨对应列构成三轨并排互为稳健性, 回退语义镜像 ctx(无同句共现回退全文、ss_is_fallback 置真), 留篇门控以 full 轨为准。由于 ss 轨文本窗口窄, 否定词与被否定词之间的距离通常也更短(同句或相邻句内), 否定翻转规则的检测窗口更容易完整覆盖否定关系, 触发的可靠性预期高于转折规则(转折连词可能跨句出现在窗口半径之外); 因此本列在 ss 轨七变体中与 canonical loughran_tone_ss 的方向一致性预期较强, 是判断"否定处理规则在最局部化语境下是否依然可靠触发"的关键诊断列。本列与 loughran_negonly_tone_ctx / loughran_negonly_tone_full 构成同规则设定的三轨并排, 互为稳健性不分主次; 由于否定翻转规则相对转折规则受窗口截断影响更小, 该三轨对应列预期是七个规则消融变体中跨轨一致性最强的一组之一(仅次于 negdeg 系), 若观测到 ss 轨与 full/ctx 两轨出现明显方向性分歧, 应优先排查该样本是否存在异常长的否定作用域跨句结构, 而非默认归因于规则本身失效。

## VAR: loughran_raw_tone_ctx

【变体差分】
本列是七臂消融矩阵中的裸词典基线: 否定翻转、程度副词、转折三条语言学规则全部关闭, 仅依据 loughran 词典正负词条的命中次数做未经任何上下文调整的加总打分, 再做 Σ|final| 自归一化, 文本轨道为 ctx。本列是解读其余六个规则变体的锚点参照 — 任何单规则或双规则变体与本列的差值, 即该规则组合在 ctx 轨的净边际贡献, 是规则敏感性核算矩阵的基准原点。本列与 loughran_raw_tone_full / loughran_raw_tone_ss 构成三轨并排, 与 ctx 轨内其余六变体 just-identified 并排, 互为稳健性不分主次, 留篇门控与回退语义与本家族其余 ctx 列一致。裸词典打分对应词典法文献中最朴素的"词袋(bag-of-words)计数"设定, 未考虑上下文调整词(contextual valence shifters)的影响, 是 Taboada et al. (2011) 综述中明确指出准确率通常低于经上下文调整版本的基线设定, 因此本列预期在方向准确性上弱于其余六个规则变体, 但作为消融基准仍具有不可替代的诊断价值。本列与 loughran_raw_tone_full / loughran_raw_tone_ss 构成三轨并排互为稳健性不分主次; 由于裸计数打分不涉及任何上下文调整规则, 其对文本窗口宽窄的敏感性完全来自命中词条数量随窗口收窄而减少这一纯统计效应, 不涉及任何语言学规则的窗口截断问题, 因此本列的三轨差异是最"干净"的窗口宽度效应对照组, 可作为分离"窗口效应对词条覆盖量的影响"与"窗口效应对具体语言学规则可及性的影响"两个不同成因的基准分离点。

## VAR: loughran_raw_tone_full

【变体差分】
本列是裸词典基线在 full 轨的版本: 三条语言学规则全关, 仅按词典命中次数加总后自归一化打分。作为 full 轨消融矩阵的基准原点, 本列与 canonical loughran_tone_full(三规则全开)之间的总差值, 理论上等于否定/程度/转折三条规则在 full 轨的联合边际贡献(注意规则间存在应用顺序依赖, 不必然可加分解为三个单规则贡献之和); 本列与 raw_tone_ctx / raw_tone_ss 构成三轨并排互为稳健性, 留篇门控以本轨直接判定、无回退语义。本列在实证使用中的核心功能是充当"规则设定是否重要"这一元问题的对照组: 若某研究结论在 raw 与 canonical 之间数值方向、显著性均高度一致, 则说明该结论对语言学规则设计选择整体不敏感, 是最强的稳健性证据之一; 反之若二者出现分歧, 则需要在论文正文明确披露规则设定对结论的驱动作用, 并优先以 canonical(三规则全开)作为解释力更强的主测度报告结果。本列与 loughran_raw_tone_ctx / loughran_raw_tone_ss 构成三轨并排互为稳健性不分主次, 是全部七个规则消融变体在三轨维度上共同的基准原点; 由于 full 轨信息覆盖面最广, 本列的样本量与词条命中密度预期在三轨中最高, 因而也是三轨中方差最小、最适合作为跨轨窗口效应研究出发点的一格。

## VAR: loughran_raw_tone_ss

【变体差分】
本列是裸词典基线在 ss 轨的版本: 三条语言学规则全关, 仅按银行∧金科同句窗口内词典命中次数加总打分。作为 ss 轨消融矩阵的基准原点, 与 raw_tone_full / raw_tone_ctx 构成三轨并排互为稳健性不分主次, 回退语义镜像 ctx(无同句共现回退全文、ss_is_fallback 置真), 留篇门控以 full 轨为准。由于 ss 轨窗口窄、单篇内词典命中的绝对次数通常较少, 裸计数打分(不做任何上下文调整)在该轨面临的稀疏性挑战比 full/ctx 两轨更突出, 少数词条的极性判断误差对最终自归一化语调值的相对影响也更大, 这是解读 raw_tone_ss 时应额外留意的测度噪声来源; 在小样本开发环境(早期试跑 T=2)下该列尤其容易呈现较低方差甚至局部退化, 属窗口设计下的预期表现, 生产全量语料(T=19)下退化风险显著降低。本列是 ss 轨全部规则消融列的共同基准参照点, 与 loughran_raw_tone_ctx / loughran_raw_tone_full 构成三轨并排互为稳健性不分主次, 三者共同构成七臂矩阵最基础的基准原点行, 供其余六个规则变体在各自轨道内计算规则边际贡献时统一参照。研究者若希望评估"在最严格的银行∧金科同句窗口下, 完全不做语言学调整的裸词典打分是否已足够可用", 本列即是该问题的直接经验证据: 将本列与 canonical loughran_tone_ss 做相关性检验, 若二者高度相关, 说明在 ss 轨这一局部化窗口内三条语言学规则的边际增量有限, 裸计数已能较好近似经规则调整后的语调; 若相关性明显低于 full/ctx 两轨对应的 raw-canonical 相关性, 则提示 ss 轨窗口的局部性放大了语言学规则调整的必要性, 值得在稳健性附录中专门说明。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Pinto, J., & Siano, F. (2025). Beyond words: the challenge of measuring financial text across borders. Journal of International Business Studies, 56(7), 921-936. https://doi.org/10.1057/s41267-025-00798-8
Oh, N. (2024). Sentibank: A Unified Resource of Sentiment Lexicons and Dictionaries. Proceedings of the International AAAI Conference on Web and Social Media, 18, 2003-2013. https://doi.org/10.1609/icwsm.v18i1.31443
Pokropek, A. (2026). From keyword-based text measures to latent variables: confirmatory factor analysis with word embeddings. EPJ Data Science, 15(1), 51. https://doi.org/10.1140/epjds/s13688-026-00654-1
Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
<!-- rendered-citations:end -->
