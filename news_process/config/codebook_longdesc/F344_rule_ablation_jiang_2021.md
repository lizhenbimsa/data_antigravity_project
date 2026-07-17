---
family_id: F344
novelty_exempt_rationale: "该家族是 jiang_2021 词典的语言学规则消融变体 (rule_ablation, producer 为 _RULE_ABLATION_VARIANTS 全 powerset 物化), 非独立新构念, 测度定义依据已在 frontmatter 已引用的母族词典原始文献 (姜富伟等 2021 及 Du et al. 2022 等) 中给出, 无需追加 2023+ 新文献。"
columns:
- jiang_2021_advonly_tone_ctx
- jiang_2021_advonly_tone_full
- jiang_2021_advonly_tone_ss
- jiang_2021_degadv_tone_ctx
- jiang_2021_degadv_tone_full
- jiang_2021_degadv_tone_ss
- jiang_2021_degonly_tone_ctx
- jiang_2021_degonly_tone_full
- jiang_2021_degonly_tone_ss
- jiang_2021_negadv_tone_ctx
- jiang_2021_negadv_tone_full
- jiang_2021_negadv_tone_ss
- jiang_2021_negdeg_tone_ctx
- jiang_2021_negdeg_tone_full
- jiang_2021_negdeg_tone_ss
- jiang_2021_negonly_tone_ctx
- jiang_2021_negonly_tone_full
- jiang_2021_negonly_tone_ss
- jiang_2021_raw_tone_ctx
- jiang_2021_raw_tone_full
- jiang_2021_raw_tone_ss
unit: 语调得分 (连续, 落于闭区间 [-1,1]; bank-year 内逐篇得分取算术平均)
formula: "article: jiang_2021_{variant}_score{track} = (Σ_pos |score(w)| − Σ_neg |score(w)|) / (Σ_pos |score(w)| + Σ_neg |score(w)|) ∈ [-1,1], 其中每个命中词的极性 score(w) 是否被否定翻转 / 是否叠加程度副词放大 / 是否受转折句让步取决于 variant 所启用的语言学规则子集; panel: jiang_2021_{variant}_tone{track} = mean_{a ∈ bank-year 留篇集} jiang_2021_{variant}_score_a{track}"
producer: news_process/pipeline/sentiment/tone_words.py::_RULE_ABLATION_VARIANTS + _analyze_single_article → classify_batch (article 逐规则子集打分) ; news_process/pipeline/panel/encode.py (bank-year 'mean' 聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (jiang_2021_{variant}_score{track} 七变体 × 三轨)
citations:
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
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
- doi: "10.1111/jfir.70063"
  type: "journal"
  authors: "Xiang, L., & Wang, W."
  year: 2026
  title: "Investor sentiment and stock market returns: A comparative analysis of mood, word, and trade"
  venue: "Journal of Financial Research"
  pages_or_artno: "jfir.70063"
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
本家族 21 列度量的是"以姜富伟、孟令超与唐国豪 (2021, 经济学(季刊)) 构建的中文财经情感词典为极性底本, 在启用不同语言学规则子集的条件下计算的银行-年语调均值", 是本项目"词典消融梯度"这条稳健性梯子在 jiang_2021 词典上的完整投影。姜富伟等 (2021) 的原始工作用媒体文本情绪预测股票回报, 其词典专为中文财经语料构建, 是本项目六部并置中文情感词典之一; 本家族关心的不是该词典的极性表本身 (那是词典赋值层的固定输入), 而是词典打分算法中三条独立语言学规则——否定翻转 (遇"不""没有"等否定词时将命中情感词的极性反号)、程度副词放大 (遇"非常""极其"等程度副词时按副词强度系数放大命中词幅值)、转折让步 (遇"但是""然而"等转折连词时对连词前后语段的情感贡献做不对称降权或让步处理)——各自及其两两组合对最终语调分数的边际贡献。三条规则理论上构成 2^3=8 种子集组合 (含全启用的 full 与全不启用的空集), 但项目物化口径只保留 7 个非-full 变体 (canonical 的 full 规则版本, 即同时启用全部三条规则, 落在家族外的 jiang_2021_score/jiang_2021_tone 之下, 不计入本 21 列); 本家族 21 列即这 7 个非-full 变体 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 分别乘以三个文本轨 (full/ctx/ss) 的完全交叉积。这一设计的研究动机是: 中文财经文本的情感极性高度依赖否定、程度、转折三类句法算子对局部褒贬词的调制, 若不做消融, 无法归因整体语调测度对某一条规则的敏感程度; 消融变体正是为回答"哪一条规则在多大程度上驱动了 canonical 语调测度"而生的诊断-稳健性并置轨。

【方法学与计算】
七个变体按其启用的规则子集依次为: raw = 三条规则全部关闭, 是不做任何句法调制的"裸词典命中"基线, 命中词按原始极性幅值直接计入正负两侧, 不翻转、不放大、不让步; negonly = 仅启用否定翻转, 度副词与转折规则关闭; degonly = 仅启用程度副词放大; advonly = 仅启用转折让步; negdeg = 同时启用否定翻转与程度副词放大 (转折关闭); negadv = 同时启用否定翻转与转折让步 (程度副词关闭); degadv = 同时启用程度副词放大与转折让步 (否定关闭)。计算路径与 canonical 全规则版本共享同一状态机骨架: 对每篇文本先用注入态 tone tokenizer 切词, 逐词匹配 jiang_2021 词典命中褒贬词, 在命中词前后局部窗口内扫描是否存在该变体启用的算子 (否定词/程度副词/转折连词), 命中且规则启用则按对应算子调整该词的最终贡献幅值 final, 未启用的规则一律跳过 (等价于该算子不存在)。正负两侧分别对全部命中词的 |final| 求和后作差分归一化, 得到落在闭区间 [-1,1] 的连续得分 (article 层 jiang_2021_{variant}_score{track}), 正值表正面语调、负值表负面语调、零值表零命中或正负完全抵消。三轨 (full/ctx/ss) 各自在自己的文本底料 (content_full / content_ctx / content_ss) 上独立跑同一套七变体消融, 互不借用彼此的命中结果。银行-年层聚合统一取算术平均 (encode 层 'mean' 归约), 分母为该银行-年在 full-only 门控下的留篇报道数 (ctx/ss 轨在 full 留篇集子集上逐轨自算, 不另立行宇宙)。七变体与三轨完全正交交叉、互不嵌套, 消融口径本身不涉及跨规则的可加分解——即 negdeg 不等于 negonly 与 degonly 的简单叠加, 三者只是同一份底稿数据在不同规则开关组合下的独立打分结果, 彼此高度共线 (审计口径 MATH-1 实测 full 与 negonly 一对变体相关系数落在 0.998-0.999 区间, 其余变体两两之间未逐一穷举复核, 但结构上同属对同一份底稿数据施加局部规则开关扰动, 可合理预期同样高度共线), 报相关系数而非把它们并入同一线性可加恒等式。

【文献定位】
本家族坐落于词典法情感测度中"句法算子敏感性"这一细分脉络。姜富伟、孟令超与唐国豪 (2021) 提供了本家族赖以打分的中文财经词典底本, 该词典是本项目并置六部中文金融情感词典之一, 与 Du、Huang、Wermers 与 Wu (2022, Review of Finance) 论证的"中文金融领域专用词典优于英文直译词典"的领域适配主张同源, 二者共同支撑了本项目并置多部中文词典互为稳健性的设计取向。否定翻转规则的方法学依据可追溯至 Pröllochs、Feuerriegel 与 Neumann (2016) 对新闻驱动交易情感分析中否定辖域检测的系统研究, 该文正是本家族 negonly/negdeg/negadv 三个变体所对应句法算子的直接文献先例。转折让步规则则呼应 Taboada、Brooke、Tofiloski、Voll 与 Stede (2011, Computational Linguistics) 对词典法情感分析中语篇结构算子 (含转折连词) 的经典综述, 是 advonly/negadv/degadv 三个变体的方法论依托。词典法作为情感测度三角的一支, 与机器学习法及大语言模型法互为对照: Frankel、Jennings 与 Lee (2022, Management Science) 系统比较了机器学习法与词典法的披露情感测度, 为词典规则消融这类"可解释性优先"路径的存在合理性提供了外部佐证。Tetlock (2007, Journal of Finance) 作为媒体情感测度的奠基性工作, 界定了词典法语调测度在资产定价文献中的解释边界, 是本家族全部变体共享的方法论上游。须重申: 七个规则消融变体各自 just-identified 并排, 互为稳健性、不分主次, 与三文本轨的正交关系镜像项目其余消融梯度 (政治词权重、罕见词频次 cutoff) 的先例, 严禁把不同规则子集或不同文本轨的多列混入同一 over-identified 的 Hansen J 过度识别检验。 晚近前沿从若干侧面为本家族的设计取向提供了补充依据。Oh (2024) 指出情感分析在可解释性上的困难, 明确背书「依赖专家词表的规则法能提供透明性」, 并以资源碎片化与验证缺失为问题意识, 将 15 部原始情感词典与 43 部预处理词典整合入 sentibank 库, 覆盖 7 类体裁与 6 个领域; 这既说明规则/词典法作为可解释的情感测度分支在当代前沿仍被明确背书, 支持本家族保留词典状态机语调轨, 也印证同一情感构念下并存大量异源词典是该领域的既成事实, 与本项目并置六部中文词典的做法同构。其边界须写明: 该文覆盖英文社交媒体等体裁, 不含 jiang_2021 等中文金融词典, 未实现否定/程度/转折三规则状态机, 亦未做任何跨词典整合运算, 故与规则消融稳健性检验无直接关联, 只止于取向层面的佐证。Pokropek (2026) 指出词典法中研究者选定的关键词极少像量表题项那样接受心理测量学检验, 遂提出把单个关键词视为同一潜变量的观测指标, 以词嵌入向量间的中心化余弦相似度矩阵为输入作验证性因子分析, 借以估计载荷与拟合指数、计算信度并检验测量不变性; 这一立场支持本项目不依赖任何单一词表, 而对词表型测度的构造假设作显式检验与披露。须注意指标层级不同: 原文的观测指标是一部词表之内的单个关键词, 整合方式为基于嵌入的 CFA 载荷估计, 语料为社会科学文本, 且未在规则消融的任一臂上分别整合, 不涉及否定/程度/转折三规则。Xiang 与 Wang (2026) 把基于心情、基于文本词与基于交易的三类投资者情绪测度并排比较其对股票收益的解释力, 印证「同一构念的多个测度并排、互为稳健性、不分主次」这一范式在前沿的存在性; 但其并排的是三类异源情绪代理, 而非同一词典内三条语言学规则的 powerset 消融, 且 DV 为股票市场收益、单位为市场/股票-时间, 与本家族的银行-年度面板不同。Iqbal 与 Pfarrer (2025) 证明情感分析在多主体文本中的情感归属上存在系统性测量误差, 提出以共指消解作为解法并经两项研究显示其可降低测量误差, 由此确立「一项具体的语言学处理选择会系统性改变文本测度取值、并构成实质性测量误差来源」这一一般命题, 支持本家族对语言学规则不作默认采纳而显式处理其后果的立场。此条边界须严格声明: 原文的规则是共指消解, 与本家族的否定翻转/程度副词/转折让步非同一规则, 其在本项目中的对应物是 ctx/ss 实体窗口轨而非规则消融族; 且原文取规范性立场, 主张采纳该规则以减少误差 (即存在唯一正确做法), 而本家族令七臂互为稳健性并排、不分主次, 故不得据以视之为 powerset 规则消融设计的同构先例。
## VAR: jiang_2021_advonly_tone_ctx

【变体差分】
本列在规则维度上只启用转折让步规则 (关闭否定翻转与程度副词放大), 在文本维度上取实体窗轨 (ctx), 即逐篇打分算在 content_ctx (标题 prepend + 银行/金融科技实体上下文窗口) 上。转折让步规则的作用是: 当命中词前后出现"但是""然而""不过"等转折连词时, 对连词前后语段的情感贡献做不对称让步处理 (通常降权转折前语段、保留转折后语段的主导地位), 以刻画中文财经文本"先扬后抑"或"先抑后扬"式表述的真实语调走向。本列与 advonly_full/advonly_ss 的唯一差别在文本底料范围, 与家族内其余六个规则变体的差别在于只保留转折算子这一条规则通道; 与 canonical 全规则版本相比, 本列缺失否定翻转与程度副词放大两条调制, 因此对存在否定或程度强化表述但无转折连词的文章, 其得分会系统性偏离全规则版本。留篇门控遵 full-only 铁律, ctx 轨为 conditional-on-full 的子集测度; 规则消融与文本轨两个维度各自 just-identified 并排、互为稳健性不分主次, 禁混入同一 over-identified Hansen J。
由于 ctx 轨的文本底料被裁剪到银行/金融科技实体窗口附近, 转折连词与命中情感词同时落入这一窄窗口的概率天然低于 full 轨, 因此本列相对 raw_ctx (零规则基线) 的边际偏移预计整体偏小、方差也更集中; 但正因窗口聚焦于实体相关语段, 一旦命中转折算子, 其对语调符号的纠偏往往更具针对性、噪声更少, 不会被无关段落的转折表述稀释。本列与 advonly_full、advonly_ss 三者联合构成"仅转折让步"这一条规则通道在三个文本轨上的完整投影, 三者互不借用彼此的命中结果, 各自基于自身轨的 content_ctx/content_full/content_ss 独立跑同一套算子逻辑; 研究者若想单独评估转折算子的文本范围敏感性, 应横向比较这三列而非纵向比较不同规则组合。本列同时也是七变体消融矩阵中"转折维度"一列在 ctx 轨上的锚点, 与 negadv_ctx (否定+转折)、degadv_ctx (程度+转折) 联合可交叉定位转折算子在与其余规则叠加时是否表现稳定 (仅作诊断性比较, 非严格可加分解)。

## VAR: jiang_2021_advonly_tone_full

【变体差分】
本列在规则维度上只启用转折让步规则, 在文本维度上取全文轨 (full), 逐篇打分算在 content_full (标题 prepend + 完整正文) 上, 覆盖报道全部可用文字。full 轨是留篇门控的定义轨: 该篇报道是否计入银行-年行宇宙, 仅由 full 轨的 llm 判定裁决。本列与同规则的 ctx/ss 两列共享同一条转折让步算子实现, 差别只在文本覆盖范围; 与同轨的其余六个规则变体相比, 只保留转折算子, 因此对存在明显否定或程度强化但缺转折连词的报道, 得分不会体现这两类调制的边际贡献。作为七变体中转折维度唯一保留的一支, 本列可与 negonly_full/degonly_full 联合读出三条规则各自对 full 轨语调的独立边际影响; 与 canonical 全规则 jiang_2021_tone_full 的差值可粗略归因为否定与程度两条被关闭规则的联合贡献 (非严格可加分解, 仅作诊断性参照)。
由于 full 轨覆盖报道全部正文, 转折连词 ("但是""然而""不过"等) 在其中出现的绝对频次与相对多样性均高于 ctx/ss 两轨, 因此转折让步算子在 full 轨上的触发率与调制幅度理论上是三轨中最大的一支; advonly_full 相对 raw_full 的偏移量因此可以被视为转折算子边际贡献的"上界式"估计, 而 advonly_ctx/advonly_ss 相应给出更保守的估计, 三者合并阅读能大致刻画转折效应随文本窗口收窄而衰减的模式。本列在银行-年层面的聚合方式与家族其余各列一致, 均取该银行-年留篇集内逐篇 jiang_2021_advonly_score_full 的算术平均, 分母严格是 full 轨自身的留篇篇数, 不与 ctx/ss 轨共享分母、也不因转折规则的开关而改变行宇宙定义 (行宇宙只由 llm_verified_full 门控决定, 与词典规则消融完全正交)。研究者在做规格曲线式稳健性展示时, 通常将 full 轨的七个规则变体并排作为一条完整的敏感性谱系, 本列是这条谱系里转折维度的端点之一。

## VAR: jiang_2021_advonly_tone_ss

【变体差分】
本列在规则维度上只启用转折让步规则, 在文本维度上取同句轨 (ss), 逐篇打分算在 content_ss (标题 prepend + 银行与金融科技词同句 ±N 句半径共现语段, 默认半径 1) 上。回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文正文, 并置 ss_is_fallback=True, 与 ctx_is_fallback 同构、共享 n_articles 分母; 若金融科技 AC 自动机为 None 则全体 *_is_fallback 置真, 优雅降级。由于 ss 轨文本域最窄, 单篇内出现转折连词的概率相应更低, 本列在三轨中通常是转折算子触发频次最低、故与 raw_ss (完全无规则) 的差异最不明显的一支; 留篇仍遵 full-only 门控, ss 轨为 conditional-on-full 子集测度, 与 full/ctx 各自 just-identified 并排、互为稳健性不分主次。
需要特别注意的是, ss 轨回退发生时 (即该篇报道没有银行与金融科技词的同句共现), content_ss 与 content_full 在文本内容上完全一致, 此时 advonly_tone_ss 与 advonly_tone_full 在该篇文章层面的得分理论上应完全相同 (同一段文本、同一套转折让步算子、同一份词典), 仅当 ss_is_fallback=False (确有同句共现窗口) 时两列才会因文本域不同而产生真实差异。这一回退结构意味着 ss 轨相对 full/ctx 两轨的稳健性解释力度依赖于该银行-年样本内 ss_is_fallback 的比例——回退比例越高, ss 轨与 full 轨的重合度越高, 稳健性检验的边际信息量相应越低; 反之回退比例越低, ss 轨提供的是真正聚焦"银行-金科同句语境"下转折算子效应的独立诊断。本列与家族内 raw_ss、negonly_ss、degonly_ss、negdeg_ss、negadv_ss、degadv_ss 六列共享同一份 content_ss 底稿与同一套回退语义, 差异只体现在规则子集的开关组合上。

## VAR: jiang_2021_degadv_tone_ctx

【变体差分】
本列在规则维度上同时启用程度副词放大与转折让步两条规则 (关闭否定翻转), 在文本维度上取实体窗轨 (ctx)。程度副词放大规则的作用是: 命中情感词前若出现"非常""极其""稍微"等程度副词, 按副词对应的强度系数放大或压缩该词的贡献幅值, 刻画中文财经文本中程度状语对情感强弱的调制; 转折让步规则同 advonly 变体所述。本列与 degadv_full/degadv_ss 差别仅在文本底料; 与家族内 negdeg/negadv 两个"双规则"变体相比, 本列缺失否定翻转这一条, 因此对含明确否定表述 (如"未能好转""不算乐观") 的报道, 得分不会体现否定翻转的调制, 可能与直觉语调方向相反。本列与 raw_ctx (零规则)、degonly_ctx (仅程度)、advonly_ctx (仅转折) 联合构成程度-转折两条规则单独及叠加效应的诊断组。留篇遵 full-only 门控, 规则/文本轨两维各自 just-identified 并排、互为稳健性, 禁混入同一 Hansen J。
由于本列的两条启用规则 (程度放大、转折让步) 都只改变幅值大小或语段权重、不涉及符号反号, 而唯一具备符号反号能力的否定翻转规则被关闭, 因此 degadv_ctx 的得分符号方向理论上应与 raw_ctx、degonly_ctx、advonly_ctx 三列高度一致, 四者的主要差异体现在幅值大小而非正负号上; 这与 negdeg_ctx、negadv_ctx、negonly_ctx 三列 (均启用否定翻转、可能与 raw_ctx 符号相反) 形成鲜明对照, 是家族内区分"符号敏感"与"幅值敏感"两类规则组合的一个关键参照点。研究者若关心程度与转折两条规则在实体窗口语境下的联合稳健性, 应以本列相对 raw_ctx 的偏移量作为主要诊断统计量, 并与同名 full/ss 两轨的对应偏移量横向比较文本窗口宽窄对该联合效应量级的调制。

## VAR: jiang_2021_degadv_tone_full

【变体差分】
本列在规则维度上同时启用程度副词放大与转折让步 (关闭否定翻转), 在文本维度上取全文轨 (full), 是留篇门控的定义轨。本列打分覆盖报道全部正文, 命中程度副词与转折连词的概率在三轨中最高, 因此 degadv_full 相对 raw_full 的规则边际贡献通常在三轨中量级最大。与同轨的 negdeg_full、negadv_full 联合读出否定规则单独加入前后两条"双规则"变体的差异, 可粗略定位否定翻转在 full 轨语调测度中的边际重要性 (非严格可加, 仅诊断参照)。与 canonical 全规则 jiang_2021_tone_full 相比, 本列唯一缺失否定翻转规则, 对含否定表述的报道尤易产生方向性偏差, 这正是该变体作为消融诊断存在的意义所在。
本列符号方向理论上与 raw_full、degonly_full、advonly_full 一致 (三者均不含否定翻转), 与之相对的是 negdeg_full、negadv_full、negonly_full 三列 (均含否定翻转、符号可能反向); 这一"符号一致组 vs 符号敏感组"的二分在 full 轨上表现得最充分, 因为 full 轨文本量最大、否定表述出现概率最高, 一旦某篇报道存在"未能好转""不算乐观"这类否定式财经措辞, degadv_full 与含否定翻转的对照列之间的差距就会被放大。本列在七变体消融矩阵中与 degadv_ctx、degadv_ss 共同构成"程度+转折双规则、无否定"这一格在三个文本轨上的完整投影, 三者互不借用彼此的命中结果, 各自基于自身文本轨底稿独立打分, 是评估该规则组合对文本窗口宽窄敏感度的标准比较组。

## VAR: jiang_2021_degadv_tone_ss

【变体差分】
本列在规则维度上同时启用程度副词放大与转折让步 (关闭否定翻转), 在文本维度上取同句轨 (ss), 打分算在 content_ss 上, 回退语义镜像 ctx (无银行∧金科同句共现则回退全文、置 ss_is_fallback=True, 优雅降级见家族 CORE 所述)。由于 ss 轨语境最短, 程度副词与转折连词同时出现在同一命中词局部窗口内的概率在三轨中最低, degadv_ss 相对 raw_ss 的规则边际贡献预计是三轨中最不明显的一支。留篇仍遵 full-only 门控, ss 为 conditional-on-full 子集测度, 与 full/ctx 及其余规则变体各自 just-identified 并排, 互为稳健性不分主次。
与 advonly_ss 相似, 本列在 ss_is_fallback=True 的样本上与 degadv_full 逐篇得分完全一致 (回退语义使 content_ss 退化为 content_full), 只有在存在真实银行-金科同句共现窗口时两列才产生真正的文本域差异; 因此本列作为稳健性检验的边际信息量随该银行-年样本的回退比例升高而递减。degadv_ss 与家族内 raw_ss (零规则基线) 的差值刻画程度放大与转折让步两条规则在同句共现语境下的联合边际贡献, 与 negdeg_ss、negadv_ss、negonly_ss 三列 (均含否定翻转) 对照可判断否定规则是否在该窄语境下扮演更关键的符号决定作用; 三者互为稳健性并排, 不设优先级。

## VAR: jiang_2021_degonly_tone_ctx

【变体差分】
本列在规则维度上只启用程度副词放大规则 (关闭否定翻转与转折让步), 在文本维度上取实体窗轨 (ctx)。本列与家族内 negonly_ctx、advonly_ctx 共同构成三条规则单独启用效应的诊断三元组, 与 raw_ctx (零规则) 对比可单独归因程度副词算子对 ctx 轨语调的边际贡献。程度副词放大只调整幅值大小、不改变命中词的原始极性方向, 因此本列与 raw_ctx 的符号方向理论上高度一致, 差异主要体现在幅值大小而非正负号翻转上, 这与 negonly 变体 (可能翻转符号) 的差异模式在性质上不同。留篇遵 full-only 门控, 与家族内其余变体、其余轨各自 just-identified 并排。
degonly_ctx 作为七变体消融矩阵中"纯程度调制"在 ctx 轨的一格, 其与 raw_ctx 的差值应被解读为程度副词放大算子在实体窗口语境下的净边际效应, 不掺杂否定翻转 (可能反号) 或转折让步 (可能不对称降权) 的干扰; 这使得该差值具有比 negonly_ctx、advonly_ctx 更"纯粹"的可解释性——即完全归因于放大/压缩系数的作用, 而非符号或语段权重的重排。与同规则的 degonly_full、degonly_ss 联合读出程度算子随文本窗口收窄而衰减的模式: 一般预期 full 轨命中程度副词的绝对次数最多、ss 轨最少, 但 ctx 轨聚焦实体相关语段, 其程度副词命中的"信噪比"可能高于 full 轨的全文本命中。三轨互为稳健性并排, 不预设哪一轨的程度效应更具代表性。

## VAR: jiang_2021_degonly_tone_full

【变体差分】
本列在规则维度上只启用程度副词放大规则, 在文本维度上取全文轨 (full), 是留篇门控定义轨。作为七变体中"纯程度调制"一支, 本列与 raw_full 的差值最纯粹地刻画程度副词算子对 full 轨语调幅值的放大效应, 不掺杂否定翻转或转折让步的干扰。与同轨的 negdeg_full (程度+否定)、degadv_full (程度+转折) 联合可交叉验证程度效应在与其余两条规则叠加时是否稳定, 是七变体消融矩阵中承担"程度维度纯效应基准"角色的一列。
由于 full 轨覆盖完整正文, 程度副词 (尤其是"非常""极其""明显""大幅"等财经语料高频修饰词) 命中次数在三轨中最高, degonly_full 相对 raw_full 的幅值放大效应因而在量级上通常最显著, 是评估该规则在没有文本窗口收缩情况下"本征"边际贡献的基准列。若研究者将 degonly_full 与 degonly_ctx、degonly_ss 三列并排比较, 可观察到放大效应量级随文本窗口收窄大致递减的模式, 但该模式并非机械单调 (ctx/ss 轨聚焦实体或共现语段, 命中的程度副词可能语义更集中); 三者仍应作为互为稳健性、不设主次的并排诊断读出, 不应把某一轨视为"更真实"的程度效应估计。

## VAR: jiang_2021_degonly_tone_ss

【变体差分】
本列在规则维度上只启用程度副词放大规则, 在文本维度上取同句轨 (ss), 回退语义镜像 ctx。ss 轨语境最短, 命中程度副词的概率相应较低, degonly_ss 相对 raw_ss 的放大幅度预计在三轨中偏小; 但由于 ss 轨聚焦银行-金科同句共现的核心语段, 命中的程度副词往往语义更集中、噪声更少, 与 full/ctx 两轨的程度效应互为稳健性对照而非相互替代。留篇遵 full-only 门控, 各维度各自 just-identified 并排。
本列在回退发生 (ss_is_fallback=True) 的样本中与 degonly_full 逐篇得分完全一致, 只有存在真实银行-金科同句共现窗口时两列才因文本域不同而分化; 因此本列作为独立稳健性信息源的边际价值取决于该银行-年样本内非回退占比。degonly_ss 相对 raw_ss 的差值刻画程度放大算子在最窄语境下的净边际效应, 与 negonly_ss、advonly_ss 联合构成三条规则单独启用效应在 ss 轨上的完整诊断三元组, 三者各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified 的 Hansen J 过度识别检验。由于 ss 轨的 content_ss 是该家族全部非-raw ss 变体共用的同一份底稿, 家族内比较 degonly_ss 与其余五个规则组合的 ss 变体 (negonly_ss/advonly_ss/negdeg_ss/negadv_ss/degadv_ss) 时可以完全排除文本域差异这一混淆因素, 任何观测到的得分差异都只能归因于规则子集开关本身, 使 ss 轨内部的规则横向比较在方法学上比 full/ctx 两轨对应的横向比较更为"干净"、更不易受文本覆盖范围本身的干扰。

## VAR: jiang_2021_negadv_tone_ctx

【变体差分】
本列在规则维度上同时启用否定翻转与转折让步两条规则 (关闭程度副词放大), 在文本维度上取实体窗轨 (ctx)。否定翻转规则的作用是: 命中情感词前若出现"不""没有""无""未"等否定词, 将该词的极性符号反号计入 (正面词经否定后计入负面侧, 反之亦然), 是三条规则中对最终语调符号方向影响最直接的一条。本列与 negdeg_ctx (否定+程度)、advonly_ctx (仅转折) 联合构成否定规则单独及与转折叠加效应的诊断组。由于同时缺失程度副词放大, 本列对含强程度表述 (如"极为负面""明显改善") 的报道, 其幅值不会被程度算子放大或压缩, 只反映否定与转折两条规则的联合调制。留篇遵 full-only 门控, 与其余变体、其余轨各自 just-identified 并排。
negadv_ctx 是七变体消融矩阵中"否定+转折双规则、无程度"这一格在实体窗轨上的投影, 同时具备符号反号能力 (否定) 与语段权重重排能力 (转折), 但不具备幅值放大/压缩能力 (程度); 这使其与 negdeg_ctx (否定+程度、无转折) 形成互补对照——两者都含否定翻转、理论上符号方向应一致, 但转折让步与程度放大对幅值大小的贡献路径不同, 二者之间的差值可粗略归因转折算子相对程度算子在实体窗口语境下的相对边际贡献差异 (非严格分解, 仅诊断参照)。与 negadv_full、negadv_ss 联合构成同一规则组合在三个文本轨上的完整投影, 三者各自基于自身轨底稿独立打分、互不借用彼此命中结果。

## VAR: jiang_2021_negadv_tone_full

【变体差分】
本列在规则维度上同时启用否定翻转与转折让步 (关闭程度副词放大), 在文本维度上取全文轨 (full), 是留篇门控定义轨。本列与 negonly_full (仅否定)、advonly_full (仅转折) 联合可交叉验证否定与转折两条规则叠加时是否存在超可加或次可加的交互效应 (仅诊断参照, 非严格分解)。与 canonical 全规则 jiang_2021_tone_full 相比, 本列唯一缺失程度副词放大规则, 对含明显程度强化表述的报道其幅值调制不完整, 是识别程度算子边际贡献的关键对照列之一 (与 degonly_full、degadv_full 联合使用)。
由于 full 轨文本量最大, 否定词与转折连词同时出现且各自命中不同情感词的情形在三轨中最为常见, negadv_full 因而是七变体中最能体现"符号反号"与"语段权重重排"两条规则联合作用的一列, 尤其适合用于诊断"先抑后扬且含否定表述"这类复杂财经叙事结构 (如"尽管一季度不良率未见改善, 但下半年拨备计提力度有所加大"这类句式) 对最终语调分数的综合影响。本列与同轨 negonly_full (仅否定)、advonly_full (仅转折) 三者构成的差值组合, 是判断否定与转折两条规则在无程度干扰情况下是否存在超可加或次可加交互效应的标准诊断组, 该判断仅具描述性参照价值, 不构成严格的方差分解。

## VAR: jiang_2021_negadv_tone_ss

【变体差分】
本列在规则维度上同时启用否定翻转与转折让步 (关闭程度副词放大), 在文本维度上取同句轨 (ss), 回退语义镜像 ctx。ss 轨语境收窄至银行-金科同句共现语段, 否定词与转折连词同时命中同一局部窗口的概率在三轨中最低, 本列相对 raw_ss 的规则边际贡献预计是七变体中最保守的估计之一。留篇遵 full-only 门控, 各维度各自 just-identified 并排, 互为稳健性不分主次。
回退发生时 (ss_is_fallback=True) 本列逐篇得分与 negadv_full 完全一致, 仅在存在真实银行-金科同句共现窗口时才因文本域差异而分化, 这一性质对本列与家族内其余六个 ss 变体一体适用, 是理解 ss 轨全部列稳健性边际信息量的共同前提。negadv_ss 与 negonly_ss (仅否定)、advonly_ss (仅转折) 联合构成的诊断组, 在最窄语境下检验否定与转折两条规则联合效应是否随文本窗口收窄而系统性弱化或强化, 这一模式本身也是词典法情感测度对文本颗粒度敏感性的一个侧面证据, 与项目内其余消融梯度 (政治词权重、罕见词频次 cutoff) 的稳健性精神一致。由于 ss 轨的 content_ss 是家族内六个非-raw ss 变体共用的同一份底稿, 比较 negadv_ss 与其余五个规则组合的 ss 变体时可以完全排除文本域差异, 使得该轨内部的规则横向比较不受文本覆盖范围混淆, 这是 ss 轨相对 full/ctx 两轨在方法学上的一个独有优势。

## VAR: jiang_2021_negdeg_tone_ctx

【变体差分】
本列在规则维度上同时启用否定翻转与程度副词放大两条规则 (关闭转折让步), 在文本维度上取实体窗轨 (ctx)。本列与 negonly_ctx (仅否定)、degonly_ctx (仅程度) 联合构成否定与程度两条规则单独及叠加效应的诊断组, 是七变体中唯一同时纳入"符号翻转"与"幅值调制"、但不纳入"语篇让步"的组合。由于缺失转折让步, 本列对存在"先抑后扬"式转折表述的报道, 不会做转折前后语段的不对称降权, 其得分更接近逐句独立打分再累加的朴素口径。留篇遵 full-only 门控, 与其余变体、其余轨各自 just-identified 并排。
negdeg_ctx 同时具备符号反号 (否定) 与幅值调制 (程度) 两种能力, 是七变体中除 canonical 全规则版本外功能最完整的双规则组合之一; 与其对照的 advonly_ctx (仅转折) 缺失这两种能力, 二者的差值近似刻画"否定+程度联合调制"相对"纯转折让步"在实体窗口语境下的净差异, 具有较强的诊断意味。negdeg_ctx 与同规则的 negdeg_full、negdeg_ss 联合构成该双规则组合在三个文本轨上的完整投影, 三者各自基于自身文本轨底稿独立打分、互不借用彼此命中结果, 是评估否定+程度联合效应对文本窗口宽窄敏感度的标准比较组, 也是家族 21 列中距离 canonical 全规则版本"仅一步之遥"(只缺转折) 的三列之一 (另两列为 negdeg_full、negdeg_ss)。

## VAR: jiang_2021_negdeg_tone_full

【变体差分】
本列在规则维度上同时启用否定翻转与程度副词放大 (关闭转折让步), 在文本维度上取全文轨 (full), 是留篇门控定义轨。与 canonical 全规则 jiang_2021_tone_full 相比, 本列唯一缺失转折让步规则, 是识别转折算子边际贡献的关键对照列 (与 advonly_full、degadv_full、negadv_full 联合使用可交叉定位三条规则各自及两两叠加的边际效应)。本列在七变体消融矩阵中承担"否定+程度双规则、无转折"这一格的诊断角色, 与 raw_full 的差值反映否定与程度联合调制、且不受转折让步干扰的净效应。
negdeg_full 是七变体中距离 canonical 全规则 jiang_2021_tone_full 语义最接近的一列 (仅关闭转折让步), 其与 canonical 的差异幅度通常应小于 negonly_full、degonly_full 等单规则变体, 因此可作为"转折算子边际贡献是否可忽略"这一问题的直接检验对象——若 negdeg_full 与 jiang_2021_tone_full 高度重合, 说明转折让步规则对 full 轨语调测度的整体影响有限; 若二者出现系统性偏离, 则说明转折算子在完整正文语境下扮演着不可忽视的调制角色, 这一判断对研究者决定是否需要在稳健性附录中单列转折维度具有指导意义。作为距离 canonical 全规则版本仅一步之遥的三列之一 (另两列为 negdeg_ctx、negdeg_ss), negdeg_full 在稳健性附录中通常与 negdeg_ctx、negdeg_ss 联合展示, 用以判断转折算子的边际贡献量级是否随文本轨窗口宽窄发生系统性变化——若三者相对 canonical 的偏离量级接近, 说明转折算子效应对文本窗口选择不敏感; 若三者偏离量级差异明显, 则说明转折算子效应本身也受文本颗粒度调制, 这一发现对解读家族内含转折让步的其余变体 (advonly/negadv/degadv) 同样具有参照价值。

## VAR: jiang_2021_negdeg_tone_ss

【变体差分】
本列在规则维度上同时启用否定翻转与程度副词放大 (关闭转折让步), 在文本维度上取同句轨 (ss), 回退语义镜像 ctx。ss 轨的短语境使转折连词本就较少出现, 因此 negdeg_ss 相对同轨的 advonly_ss (仅转折) 差异预计比 full/ctx 两轨更小, 但否定与程度两条规则在同句共现语段中命中集中度较高, 二者的联合边际贡献仍具备诊断价值。留篇遵 full-only 门控, 各维度各自 just-identified 并排, 互为稳健性不分主次。
回退语义与家族内其余六个 ss 变体一致: ss_is_fallback=True 时本列逐篇得分与 negdeg_full 完全一致, 仅在存在真实银行-金科同句共现窗口时才因文本域不同而分化。negdeg_ss 作为距离 canonical 全规则版本 (仅缺转折) 最接近的一列在 ss 轨上的投影, 与 negdeg_full、negdeg_ctx 联合可用于判断"转折算子的边际贡献是否随文本窗口收窄而系统性变化"这一问题, 三者互为稳健性并排, 不预设某一轨的答案更具权威性。由于 ss 轨的 content_ss 是家族内六个非-raw ss 变体共用的同一份底稿, negdeg_ss 与其余五列 (negonly_ss/degonly_ss/advonly_ss/negadv_ss/degadv_ss) 的横向比较可以完全排除文本域差异这一混淆因素, 是判断否定与程度两条规则各自及联合边际贡献在同句共现语境下相对量级的一组"干净"对照。

## VAR: jiang_2021_negonly_tone_ctx

【变体差分】
本列在规则维度上只启用否定翻转规则 (关闭程度副词放大与转折让步), 在文本维度上取实体窗轨 (ctx)。本列是七变体中最贴近传统词典法"否定辖域检测"惯例的一支, 方法学依据直接对应 Pröllochs、Feuerriegel 与 Neumann (2016) 对新闻驱动交易情感分析中否定辖域的系统处理。与 raw_ctx (零规则) 对比, 本列纯粹刻画否定翻转算子对 ctx 轨语调符号方向的边际贡献, 是识别"仅靠句法否定检测能纠正多少语调误判"这一问题的核心诊断列。留篇遵 full-only 门控, 与其余变体、其余轨各自 just-identified 并排。
negonly_ctx 与家族内 negdeg_ctx、negadv_ctx 联合构成否定翻转规则在实体窗口语境下"单独启用"与"分别叠加程度/转折"三种情形的完整诊断序列, 三者相对 negonly_ctx 的增量可分别归因程度放大与转折让步在已含否定翻转基础上的边际追加贡献 (非严格可加分解, 仅诊断参照)。由于 ctx 轨聚焦银行/金融科技实体附近文本, 否定词若恰好出现在实体窗口边界之外, 该否定表述可能不会被本列捕捉到, 这是 ctx 轨相对 full 轨在否定翻转维度上一个值得留意的结构性差异, 也是研究者比较 negonly_ctx 与 negonly_full 时应纳入考量的因素之一。

## VAR: jiang_2021_negonly_tone_full

【变体差分】
本列在规则维度上只启用否定翻转规则, 在文本维度上取全文轨 (full), 是留篇门控定义轨, 也是家族内与 stata_export.py 中已具名标签 (jiang_2021_negonly_tone_full: "Jiang2021词典语调(仅否定规则,全文轨)") 直接对应的核心对照列。本列与 canonical 全规则 jiang_2021_tone_full 相比, 缺失程度副词放大与转折让步两条规则, 差值可粗略归因为这两条规则的联合贡献 (非严格可加, 仅诊断参照)。作为纯否定翻转基准, 本列在整个七变体家族中承担"符号方向纠偏"这一最基础规则的边际效应识别角色, 是最贴近国际主流词典法情感分析 (如英文 Loughran-McDonald 传统) 否定处理惯例的中文对照。
negonly_full 的方法学价值在于, 它把否定翻转这一条规则从家族其余全部规则组合中剥离出来单独观察, 使研究者能够在不受程度放大或转折让步干扰的前提下, 纯粹评估"句法否定检测"这一单一机制对中文财经报道整体语调符号方向的纠偏能力; 这一角色与 Pröllochs、Feuerriegel 与 Neumann (2016) 在新闻驱动交易情感分析中系统检验否定辖域检测有效性的研究设计高度呼应——该文正是通过类似的"启用/关闭否定处理"对照设计, 论证了否定辖域检测对新闻情感测度准确性的边际贡献, negonly_full 与 raw_full 的差值可视为该方法论在本项目中文语料上的直接复现。

## VAR: jiang_2021_negonly_tone_ss

【变体差分】
本列在规则维度上只启用否定翻转规则, 在文本维度上取同句轨 (ss), 回退语义镜像 ctx。ss 轨语境收窄至银行-金科同句共现语段, 该语段内否定词命中率如何影响语调符号方向是本列的核心诊断价值所在——由于语境更短、句法结构更单一, 否定辖域检测理论上更精确 (跨句误判否定辖域的风险更低), 因此 negonly_ss 相对 raw_ss 的符号纠偏效应可能比 full/ctx 两轨更清晰。留篇遵 full-only 门控, 各维度各自 just-identified 并排, 互为稳健性不分主次。
回退语义与家族其余六个 ss 变体一致: ss_is_fallback=True 时本列逐篇得分与 negonly_full 完全一致。negonly_ss 与 negonly_full、negonly_ctx 三者联合构成否定翻转规则单独效应在三个文本轨上的完整投影, 是判断"否定辖域检测精度是否随文本窗口收窄而系统性提升"这一方法学问题的核心三元诊断组; 三者各自 just-identified 并排, 互为稳健性不分主次, 严禁把三轨的否定翻转边际效应混入同一 over-identified 的 Hansen J 过度识别检验中联合估计。由于 ss 轨的 content_ss 是家族内六个非-raw ss 变体共用的同一份底稿, negonly_ss 与其余五列 (degonly_ss/advonly_ss/negdeg_ss/negadv_ss/degadv_ss) 的横向比较可以完全排除文本域差异这一混淆因素, 使得 negonly_ss 相对 raw_ss 的偏移量可被纯粹归因于否定翻转算子在最窄语境下的边际贡献, 不掺杂文本覆盖范围的干扰。

## VAR: jiang_2021_raw_tone_ctx

【变体差分】
本列在规则维度上三条规则 (否定翻转、程度副词放大、转折让步) 全部关闭, 是七变体消融矩阵的零规则基线, 在文本维度上取实体窗轨 (ctx)。raw 变体的命中词按原始极性幅值直接计入正负两侧求和归一化, 不做任何句法调制, 等价于"裸词典命中计数式"打分 (只是仍取连续幅值而非纯 0/1 计数)。本列是家族内全部其余六个规则变体的共同对照基准: negonly_ctx、degonly_ctx、advonly_ctx 相对本列的差值分别单独归因三条规则各自的边际贡献, negdeg_ctx、negadv_ctx、degadv_ctx 相对本列的差值则归因对应两条规则的联合贡献。留篇遵 full-only 门控, 与其余轨的 raw 变体各自 just-identified 并排、互为稳健性不分主次。
raw_ctx 在方法学上等价于一个不做任何句法调制的"词典命中计数式"打分器在实体窗口语境下的连续幅值版本, 是判断"句法规则整体是否改变了 ctx 轨语调测度"这一诊断问题的基准端。若 raw_ctx 与含全部三条规则的 canonical ctx 轨版本 (jiang_2021_tone_ctx, 落在家族外) 高度相关且量级接近, 说明句法规则对该轨测度的整体边际影响有限; 若二者出现系统性偏离, 则说明否定、程度、转折三条规则整体上对 ctx 轨语调有实质性调制作用, 值得在稳健性附录中展开逐条规则的贡献分解讨论 (仅诊断参照, 非严格可加分解)。

## VAR: jiang_2021_raw_tone_full

【变体差分】
本列在规则维度上三条规则全部关闭, 在文本维度上取全文轨 (full), 是留篇门控定义轨, 也是七变体消融矩阵中"全文轨零规则基线"这一格。本列与 canonical 全规则 jiang_2021_tone_full 的差值刻画否定、程度、转折三条规则联合启用相对完全不做句法调制时的总体边际贡献, 是判断"句法规则整体是否显著改变了词典法语调测度"这一诊断问题最直接的一列——若 raw_full 与 jiang_2021_tone_full 高度相关且量级接近, 说明 canonical 语调测度对三条句法规则的整体敏感度较低, 反之则说明句法调制对 full 轨测度有实质影响。本列在七变体中与其余六列联合构成完整的规则消融诊断矩阵基准端。
raw_full 作为 full 轨的零规则基线, 是三个文本轨对应基线列 (raw_full/raw_ctx/raw_ss) 中样本量最大、文本覆盖最完整的一支, 通常也是三者中方差最小、统计功效最高的基线, 适合作为主报告中默认展示的"裸词典命中"参照系; ctx/ss 两轨的基线则更适合作为文本窗口敏感性的补充展示。研究者在撰写稳健性附录时, 若只能展示一张规则消融图, 建议以 raw_full 为横轴零点, 纵向排列 negonly_full、degonly_full、advonly_full、negdeg_full、negadv_full、degadv_full 六列相对该基线的偏移量, 直观呈现三条规则各自及两两叠加对 full 轨语调测度的边际贡献谱系。

## VAR: jiang_2021_raw_tone_ss

【变体差分】
本列在规则维度上三条规则全部关闭, 在文本维度上取同句轨 (ss), 回退语义镜像 ctx (无银行∧金科同句共现则回退全文正文, 置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母; AC 自动机为 None 时全体 *_is_fallback 置真优雅降级)。作为 ss 轨的零规则基线, 本列与同轨其余六个规则变体的差值联合归因否定、程度、转折三条规则在"银行-金科同句共现"这一最窄语境下各自及联合的边际贡献; 由于该语境本身语义更集中、句法结构更简单, 三条规则的边际贡献模式可能与 full/ctx 两轨系统性不同, 三轨的 raw 基线本身也互为稳健性对照, 各自 just-identified 并排, 严禁混入同一 over-identified 的 Hansen J。
回退语义与家族其余六个 ss 变体一致: ss_is_fallback=True 时本列逐篇得分与 raw_full 完全一致, 只有存在真实银行-金科同句共现窗口时才因文本域不同而分化。raw_ss 作为 ss 轨的零规则基线, 是 negonly_ss、degonly_ss、advonly_ss、negdeg_ss、negadv_ss、degadv_ss 六列共同的对照基准, 承担与 raw_full、raw_ctx 相同的角色但落在最窄的文本窗口上; 三条基线 (raw_full/raw_ctx/raw_ss) 联合构成本家族规则消融矩阵在文本轨维度上的零点谱系, 是解读全部 21 列相对偏移量时不可或缺的参照系。在 ss_is_fallback=False 的非回退样本中, raw_ss 与 raw_full 因文本域不同而产生真实分化, 此时 raw_ss 相对 raw_full 的差值本身也构成一条独立的诊断信息——它刻画了"聚焦银行-金科同句共现语段"相对"完整正文"在完全不做句法调制前提下对裸词典命中打分的净影响, 这一效应与本家族其余规则消融维度正交, 不应与否定/程度/转折三条规则的边际贡献相混淆。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Oh, N. (2024). Sentibank: A Unified Resource of Sentiment Lexicons and Dictionaries. Proceedings of the International AAAI Conference on Web and Social Media, 18, 2003-2013. https://doi.org/10.1609/icwsm.v18i1.31443
Pokropek, A. (2026). From keyword-based text measures to latent variables: confirmatory factor analysis with word embeddings. EPJ Data Science, 15(1), 51. https://doi.org/10.1140/epjds/s13688-026-00654-1
Xiang, L., & Wang, W. (2026). Investor sentiment and stock market returns: A comparative analysis of mood, word, and trade. Journal of Financial Research, jfir.70063. https://doi.org/10.1111/jfir.70063
Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
<!-- rendered-citations:end -->
