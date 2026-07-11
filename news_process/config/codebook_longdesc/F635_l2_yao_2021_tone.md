---
family_id: F635
columns:
- yao_2021_tone_app_ctx
- yao_2021_tone_app_full
- yao_2021_tone_app_ss
- yao_2021_tone_ctx
- yao_2021_tone_full
- yao_2021_tone_hw_ctx
- yao_2021_tone_hw_full
- yao_2021_tone_hw_ss
- yao_2021_tone_mw_ctx
- yao_2021_tone_mw_full
- yao_2021_tone_mw_ss
- yao_2021_tone_ss
- yao_2021_tone_std_ctx
- yao_2021_tone_std_full
- yao_2021_tone_std_ss
- yao_2021_tone_tech_ctx
- yao_2021_tone_tech_full
- yao_2021_tone_tech_ss
- yao_2021_tone_vw_ctx
- yao_2021_tone_vw_full
- yao_2021_tone_vw_ss
unit: 语调得分 (无量纲, 归一化 ∈ [-1,1]; 聚合后为 bank-year 均值/加权均值/离散度)
formula: "yao_2021_tone{track} = mean_over_articles(yao_2021_score{track}); 文章级 yao_2021_score = Σ(final_score)/Σ|final_score| ∈ [-1,1], final_score = base × degree × negation × adversative; 加权变体 {vw,mw,hw} = Σ(w_j·score_j)/Σ(w_j); std 变体 = bank-year 横截面 SD; {tech,app} = 条件均值 mean(yao_2021_score{track} | innovation_locus ∈ {底层技术, 应用场景})"
producer: news_process/pipeline/panel/encode.py::aggregate_panel (base/std/vw/mw/hw/tech/app 面板聚合); 文章级分数 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (yao_2021_score_{full,ctx,ss})
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
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1111/joes.12370
  type: journal
  authors: Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K.
  year: 2020
  title: "Econometrics meets sentiment: An overview of methodology and applications"
  venue: Journal of Economic Surveys
  vol: 34
  issue: 3
  pages_or_artno: 512-547
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1145/1341531.1341561
  type: book
  authors: Ding, X., Liu, B., & Yu, P. S.
  year: 2008
  title: "A holistic lexicon-based approach to opinion mining"
  venue: "Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08)"
  pages_or_artno: 231-240
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是同一 bank-year 单元内, 以「姚加权等 (2021) 金融领域中文情绪词典」(下称 yao_2021 词典) 为极性判据算出的新闻语调 (tone), 即某银行在某一年度被媒体报道时, 正面用词与负面用词的净倾向, 以及围绕这一净倾向派生的若干加权均值、横截面离散度与创新落点子样本变体。这里的「语调」不是抽象情绪, 而是一个可回归的连续标量: 报道整体越偏正面褒扬, 值越接近 +1; 越偏负面质疑, 值越接近 -1; 中性或正负相抵则趋近 0。需要提醒的是, 在本项目的实证语料上, 名义双极 [-1,1] 的分布实为单极偏正 (favorability/optimism 口径) —— 媒体对银行金科报道整体偏正向, 因此该测度更宜解读为「褒扬强度」而非对称的褒贬轴, 面板诊断对 tone 均值是否为正设有研判提示。yao_2021 词典是六部并行的中文金融情感词典之一, 与 loughran (Loughran-McDonald 2011 主译第六部)、jiang_2021、bian_2021、du_2022、you_2018 一同在项目 stage 22 (tone_words) 被并列应用, 词条与极性权重的单一事实源是 config/tone_dicts.json, 而非各词典原始发布的散料文件。之所以同时上六部词典而非只取一部, 是因为词典法本身是一种「测量工具」而非「真值」: 盘上实证显示逐篇最优词典会在观测间漂移 (以逐篇匹配数计, yao 约 51%、du 约 41% 的篇章各自胜出), 说明没有哪一部词典对全部报道普适地最优。把六部词典各自算出的 tone 并排为互为稳健性的平行测量, 是防止主结论被单一词典的构念偏差、词表覆盖缺口或语域漂移所驱动的必要设计。yao_2021 家族在这一并排结构里承担「一部独立词典」的角色, 其 canonical 列 yao_2021_tone_full 是本家族 21 列的核心测度, 其余 20 列都是它在文本轨、加权方案、汇总统计量与子样本维度上的规格变体。本家族的最终对象是银行金融科技舆论环境: 银行既是金融科技的采纳者也是被颠覆者, 媒体对其金科战略的语调构成一种外部信息环境与声誉纪律, 这一构念定位与下方文献脉络一致。

【方法学与计算】
计算分两层。第一层是文章级打分 (stage 22, tone_words.py::compute_dict_scores): 对每篇报道按 jieba 分词 (版本冻结于 0.42.1 以保确定性) 后, 命中 yao_2021 词典的 token 取其 base 极性权重, 再逐 token 施加三条语言学规则乘子 —— 否定翻转 (negation, 遇否定词将该词极性取反)、程度副词放大 (degree, 依副词强度施乘子, 最高约 3.0 倍)、转折增强 (adversative, 转折连词后的语调被适度放大)。逐 token 累加得 final_score 后, 文章归一化语调 = Σ(final_score) / Σ|final_score|, 值域严格落在 [-1, +1]。归一化分母取绝对值之和而非裸匹配词数 (pos_count+neg_count), 使程度与转折规则既进分子又进分母, 从而避免分母被规则乘子系统性放大而把语调虚拉向中性 —— 这是相对旧实现 (分母为裸词数) 的关键修正。对同时被判正负的混合极性词, 其对分子的净贡献为 0 (正负 final 相抵)、对分母贡献 2|final|, 因此把该词的语调拉向中性而非武断剔除, 体现对该词典个体净语调「不武断选边」的设计取向。第二层是 bank-year 聚合 (stage 40, encode.py::aggregate_panel): 遵循先分后合范式 (Tetlock 等 2008) —— 先对每篇报道各自算分, 再对每个 (银行, 年度) 单元内的文章级 yao_2021_score 求汇总量; 这一顺序至关重要, 因为 mean(a/b) ≠ mean(a)/mean(b) (Jensen 不等式), 若先聚合原始计数再算比率会引入系统性偏差。汇总量按变体分岔: canonical/base 列取等权算术均值; std 变体取单元内横截面标准差 (度量分歧度而非水平); vw/mw/hw 三个加权变体取 Σ(权重×分数)/Σ(权重) 的加权均值, 权重分别为提及密度、媒体权威、跟风衰减; tech/app 两个子样本变体取按文章级 innovation_locus 条件筛选后的均值。文章级分数不落最终面板, 仅 bank-year 聚合列进 .dta。三轨文本 (full/ctx/ss) 在 stage 14 (ctx_materializer) 物化, 词典打分对三轨各扫一遍, 故每个变体都有三轨孪生列。

【文献定位】
本家族方法学根植于金融文本分析的词典法传统。Loughran & McDonald (2011) 确立了领域专用词典相对通用词典 (如 Harvard General Inquirer) 在金融语料上的必要性 —— 通用词典里许多「负面」词在金融语境实为中性, 直接套用会系统性误判; 其后续综述 Loughran & McDonald (2016) 进一步系统梳理了词典法的适用边界、常见陷阱与稳健性建议。Tetlock (2007) 是媒体语调影响资产定价的开创性证据, 奠定了「把报道语调聚合为可回归的连续变量」这一范式, 也是本项目把 tone 聚合到 bank-year 的直接思想来源。中文金融语域的专用词典建设由 Du 等 (2022) 在 Review of Finance 上的中文金融情感词典、Bian 等 (2021) 的 Loughran-McDonald 中文扩展词典、以及 Ma 等 (2025) 的细粒度投资者情绪词典 CN-FSD 等推进; yao_2021 属于同一本土化谱系的一部词典, 与它们互为稳健、可交叉验证。词典法的三条语言学规则 (否定、程度、转折) 在方法学上有 Ding 等 (2008) 的整体式 (holistic) 词典观点与 Taboada 等 (2011) 系统的 lexicon-based 情感计算作锚点, 二者论证了规则修饰对提升词典法效度的作用。方法学综述层面, Algaba 等 (2020) 的 sentometrics 框架把词典聚合、加权与稳健性并入统一的计量经济视角, 为本家族的多加权、多轨设计提供了总纲。效度校准层面, van Atteveldt 等 (2021) 以人工标注、众包编码为参照系, 比较了词典法、机器学习各自的效度边界; Frankel 等 (2022) 直接对比机器学习与词典法在披露语调上的表现 —— 二者共同论证了「不把单一方法当真值、而以多方法互为稳健」的必要性, 正是本项目「六词典并排 + LLM/BERT 并排」设计的直接先例。Barbaglia 等 (2025) 则提供了经济文本 lexicon-based 语调抽取的近期方法参照, 说明词典法在大规模经济文本上仍具竞争力。

【识别策略定位】
在下游计量中, yao_2021 家族的角色是「同一潜在构念 (媒体对银行金科报道的语调) 的一部独立测量」, 而非某个独立的经济机制。canonical 列 yao_2021_tone_full 可作处理变量或稳健性列进入 bank-year 面板固定效应回归 (银行与年度双向固定效应), 度量语调对下游银行财务、投资或声誉结局的关联。识别纪律有二, 二者互相独立且都是硬约束。其一, 六部词典 (yao/du/jiang/bian/you/loughran) 各自算出的 tone 是对同一潜在语调的平行测量, 它们各自 just-identified 并排、互为稳健性、不分主次; 严禁把不同词典的 tone 混进同一 over-identified 的 Hansen J 过度识别检验 —— 因为它们对同一文本高度共线 (逐篇胜出词典漂移即是共线的直接证据), 并非相互独立的外生矩条件, 混入会使 J 统计量丧失应有的过度识别含义, 得出虚假的「工具有效」结论。其二, 家族内部的三轨 (full/ctx/ss)、三种加权 (vw/mw/hw)、两种落点子样本 (tech/app) 亦各自构成规格稳健性并排臂, 同样禁止混入同一 over-identified Hansen J; 它们的唯一用途是证明主结论不被文本切片口径、加权方案或子样本选择所驱动, 而非提供额外的识别性矩条件。三个加权变体分别承接三条独立的加权理论脉络: vw 承 Hassan 等 (2019) 的提及密度加权、mw 承 Holzman 等 (2023) 的媒体权威加权、hw 承 Tetlock (2011) 的跟风衰减加权; 三者对「哪些报道更该被重视」给出不同但都有理论依据的答案, 因此互为稳健。落点子样本 tech/app 承 Gomber 等 (2018) 的金融科技创新框架, 切分底层技术层与应用场景层的舆论。跨这些规格臂的多重检验若需汇报族错误率, 应参照 Romano & Wolf (2005) 的逐步多重检验框架, 由根级跨模型/跨规格 rwolf 模板统一处置, 而非在单个回归里堆矩条件。

【与相邻测度的构念区分】
yao_2021 家族须与三类相邻测度严格区分, 以免在稳健性表里被误当作独立证据或误混识别检验。第一, 与其他五部词典 tone 家族 (du_2022 / jiang_2021 / bian_2021 / you_2018 / loughran) 的区别仅在极性词表来源不同, 计算管线 (分词、三规则、归一化) 与聚合口径 (先分后合、六变体、三轨) 完全一致; 因此它们互为稳健性而非互为对照真值, 六部同向变动是词典法内部一致性的体现, 而非六个独立发现。第二, 与情感 LLM 三家投票 tone (llm_vote_tone 族, gpt54nano/gemini31/deepseekv4 多数投票) 及 BERT 三模型 tone (finbert_cn/fin_sent_zh/finbert2) 的区别在于打分机理根本不同 —— 词典法是可解释、可复算的计数—规则法, LLM/BERT 是不可逐词追溯的语义模型法; 三法各自 just-identified 并排、互为稳健、不分主次, 严禁混入同一 over-identified Hansen J; 词典 tone 与 LLM/BERT tone 的一致度本身是效度证据, 但不能当作叠加的矩条件。第三, 与 du_2022 特有的政治词权重梯度 (polw00/05/10)、以及规则消融梯度 (negonly 等纯计数、规则约简变体) 是正交维度: 本 F635 家族全部 21 列均在完整语言学规则、无政治权重特判下计算, 刻意不展开权重或规则的消融, 以避免与三轨、六变体相乘导致列数组合爆炸。相应地, yao_2021 词典的 negonly (纯计数、规则约简) 变体归属另一命名域与另一家族, 不在本 21 列内; 若在稳健性叙事里同时引用 yao_2021_tone 与 yao_2021_negonly_tone, 须明确二者是规则维度的并排臂而非独立机制。

【已知局限与稳健性梯子】
局限有五, 使用时须如实披露。其一, 中文金融词典的极性词表在互联网金融/金融科技这一新兴、快速演化的语域上覆盖率有限, 新造词、行业黑话、英文缩写可能漏判, 这既是词典法的固有短板, 也是并排六部词典并进一步以 LLM/BERT 交叉验证的根本动因。其二, 归一化语调把情绪强度压缩进 [-1,1], 对极端情绪与温和情绪的区分度弱于连续概率法, 更适合刻画方向而非幅度。其三, tech/app 落点子样本依赖 LLM 对 innovation_locus 的分类, 当分类置信度偏低时子样本 tone 噪声较大, 使用前须结合面板列 avg_category_confidence 诊断 (置信度低于 0.5 的单元被标记, 慎用维度切分)。其四, 加权变体 (vw/mw/hw) 的分母 (权重之和) 在稀疏 bank-year 单元上可能为 0, 已由 replace(0, NaN) 守卫避免除零, 但会使这些单元的加权 tone 缺失。其五, std 变体在单篇或零篇的 bank-year 上标准差无定义, 取 NaN, 在 T 较小的开发样本上退化尤为常见。稳健性梯子沿三条正交轴铺开: (a) 文本轨 full / ctx / ss —— 分别为标题加全文、标题加实体上下文窗、标题加银行金科同句共现窗, 检验语调是否对文本语境的逐级收窄稳健; ss 轨在无同句共现时优雅回退为全文正文并置 ss_is_fallback (回退语义镜像 ctx 轨, 以 CLAUDE.md 铁律为准)。(b) 加权方案 equal / vw / mw / hw —— 检验语调是否对『放大高提及报道、权威媒体、抑制跟风扎堆报道』等不同加权稳健。(c) 落点子样本 tech / app —— 按 Gomber 等 (2018) 的底层技术 vs 应用场景切分, 检验技术层与应用层的舆论温差。三轴各臂一律 just-identified 并排、互为稳健、不分主次, 严禁混同一 over-identified Hansen J。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否算作「银行金科报道」只看 full 轨的 LLM 验证 (llm_verified_full == True), ctx 与 ss 轨降为 conditional-on-full 的稳健性测度, 其行宇宙是 full 留篇集的子集, 因此三轨的样本量与缺失模式不同, 解读跨轨差异时须记住这一门控不对称。

## VAR: yao_2021_tone_app_ctx

【变体差分】
本列是 yao_2021 家族在「应用场景 (app) 子样本 × ctx 轨」交叉下的语调。app 子样本指按文章级 innovation_locus 分类落在「应用场景」一类的报道 (对应 Gomber 等 2018 金融科技创新框架中面向业务应用层、而非底层技术层的创新落点)。本列取值 = mean(yao_2021_score_ctx | innovation_locus == "应用场景"), 即仅在应用场景类报道内、用 ctx 轨文本算出的 yao_2021 词典语调的 bank-year 均值。ctx 轨文本 = 标题 prepend 后的实体上下文窗口 (银行/金科实体附近 ±N 句), 相对 full 轨收窄至实体语境, 用于检验语调是否对无关段落的稀释稳健。该列与同为应用场景子样本的 app_full、app_ss 构成三轨稳健性并排, 又与技术层子样本 tech_ctx 构成落点对照 (二者之差近似应用层减技术层的舆论温差, 但本列不做差分, 差分由 tone_gap 系列列承担)。当某 bank-year 在应用场景子样本下无报道时取 NaN。本列与家族其余各列各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ctx 轨采 conditional-on-full 口径, 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_app_full

【变体差分】
本列是「应用场景 (app) 子样本 × full 轨」交叉下的 yao_2021 语调。取值 = mean(yao_2021_score_full | innovation_locus == "应用场景"), 即把某 bank-year 内被 LLM 判为面向应用场景层创新的报道筛出, 用 full 轨文本 (标题 prepend 加全文正文) 算 yao_2021 词典语调后求均值。full 轨是本项目的 canonical 文本轨, 也是留篇门控 (full-only, 2026-06-29) 的唯一判据轨, 因此本列在应用场景子样本内是水平最完整、样本最全的语调测度, 相对 app_ctx/app_ss 更贴近「该银行该年度应用层报道的整体口碑」。与 tech_full 并列时, 两列覆盖 Gomber 等 (2018) 框架下应用场景 vs 底层技术两个互斥落点, 是本家族对创新落点异质性的直接切分; 但两列仅作规格稳健并排, 严禁把 app 与 tech 两个子样本 tone 混进同一 over-identified Hansen J。当应用场景子样本为空时取 NaN。本列亦与其他五部词典的同口径 app_full 列互为稳健性、不分主次。

## VAR: yao_2021_tone_app_ss

【变体差分】
本列是「应用场景 (app) 子样本 × ss 轨」交叉下的 yao_2021 语调, 取值 = mean(yao_2021_score_ss | innovation_locus == "应用场景")。ss 轨 (same-sentence) 是三轨中语境最窄的一轨: 文本仅取银行实体与金融科技词在同一句内共现的 ±N 句窗 (标题 prepend)。当某篇报道不存在银行与金科的同句共现时, ss 轨优雅回退 —— content_ss 退化为全文正文、ss_is_fallback 置 True, 该回退语义严格镜像 ctx 轨的回退口径 (以 CLAUDE.md 铁律为准)。因此本列度量的是「应用场景类报道里, 银行与金科强共现语境下」的 yao_2021 语调, 是三轨中对『银行—金科直接关联』这一构念最纯净、也最易受回退与稀疏性影响的一轨, 通常作首要稳健性轨而非主轨。本列与 app_full、app_ctx 三轨并排, 各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; ss 轨同为 conditional-on-full, 行宇宙是 full 留篇集子集。应用场景子样本为空时取 NaN。

## VAR: yao_2021_tone_ctx

【变体差分】
本列是 yao_2021 家族 canonical (等权、全样本) 语调的 ctx 轨版本, 取值 = mean(yao_2021_score_ctx), 即对某 bank-year 内全部留篇报道、用 ctx 轨文本算出的 yao_2021 词典语调求等权算术均值。它与核心列 yao_2021_tone_full 的唯一差别是文本轨: ctx 轨 = 标题 prepend 后的实体上下文窗口 (银行/金科实体附近 ±N 句), 相对 full 轨 (标题加全文) 收窄至实体周边语境, 剔除了与银行金科无关的段落噪声。本列不做加权 (区别于 vw/mw/hw)、不做离散度 (区别于 std)、不做落点切分 (区别于 tech/app), 是最贴近「该银行该年度媒体口碑均值」的实体聚焦版测度。作为 canonical 的实体窗轨, 它是 full 轨的首要稳健性对照, 检验语调水平是否对文本从全文收窄到实体窗稳健。本列与 full、ss 三轨并排, 各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ctx 轨采 conditional-on-full 口径 (留篇门控 full-only), 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_full

【变体差分】
本列是整个 F635 家族的核心 (core) 列, 也是 yao_2021 词典语调的 canonical 定义: 取值 = mean(yao_2021_score_full), 即对某 bank-year 内全部 full-only 留篇报道, 用 full 轨文本 (标题 prepend 加全文正文) 算出的 yao_2021 词典归一化语调, 再取等权算术均值。它相对家族其余 20 列的差分是「无任何修饰」的基准形态: 文本轨取最完整的 full 轨、聚合取等权均值 (非 vw/mw/hw 加权)、汇总取水平均值 (非 std 离散度)、样本取全体留篇 (非 tech/app 落点子样本)。之所以以 full 轨作 canonical, 是因为 full 轨是本项目留篇门控的唯一判据轨 (full-only 口径, 2026-06-29): 一篇报道是否计为「银行金科报道」只看 llm_verified_full == True, 因此 full 轨行宇宙最完整、样本框最稳定, 天然适合作主测度; ctx 与 ss 轨则降为 conditional-on-full 的稳健性测度, 其行宇宙是本列留篇集的子集。文章级 yao_2021_score_full 的构造是: 分词后命中 yao_2021 词典的 token 取 base 极性, 施加否定翻转、程度副词放大、转折增强三条语言学规则得 final_score, 再按 Σ(final_score)/Σ|final_score| 归一化到 [-1,1]; bank-year 聚合遵循先分后合范式 (Tetlock 等 2008), 逐篇算分后再对篇求均值, 避免 Jensen 不等式下 mean(a/b)≠mean(a)/mean(b) 的偏差。在识别层面, 本列是 yao_2021 词典对「媒体对银行金科报道的语调」这一潜在构念的一部独立测量, 可作处理变量或稳健性列进入 bank-year 面板固定效应回归; 作处理变量时, 通常搭配银行、年度双向固定效应与银行层面聚类稳健标准误, 以吸收银行不随时间变的异质性与共同年度冲击。关键纪律: 本列须与其他五部词典 (du_2022 / jiang_2021 / bian_2021 / you_2018 / loughran) 的同名 canonical tone、以及情感 LLM 三家投票 tone、BERT 三模型 tone 并排为互为稳健性、不分主次的平行测量; 六部词典对同一文本高度共线 (逐篇最优词典在 yao 约 51%、du 约 41% 间漂移即是共线的直接证据), 因此严禁把它们混进同一 over-identified 的 Hansen J 过度识别检验 —— 它们不构成相互独立的外生矩条件, 混入会使 J 检验结论失真。本列亦是整个家族三轴稳健性梯子 (三轨 full/ctx/ss、三加权 vw/mw/hw、两落点 tech/app) 的原点: 其余 20 个带后缀列都以本列为差分参照, 即「本列 + 某一维度的偏离」。留篇门控层面须再次强调 full-only 口径: 本列的行宇宙是全部 llm_verified_full == True 的留篇集, 是三轨中最完整的样本框, 而 ctx/ss 轨的对应列只在本列留篇集的子集上定义, 因此本列在样本代表性上优于任何非 full 轨或子样本列, 这也是选它作核心的原因之一。方法学锚点见 Loughran & McDonald (2011, 2016) 的金融词典法奠基与综述、Tetlock (2007) 的媒体语调—资产定价范式, 以及 Du 等 (2022)、Bian 等 (2021)、Ma 等 (2025) 的中文金融情感词典本土化建设脉络; 词典法语言学规则的方法学依据见 Ding 等 (2008)、Taboada 等 (2011); 多方法互为稳健、不以单一方法为真值的设计先例见 Frankel 等 (2022) 与 van Atteveldt 等 (2021); 跨规格多重检验的族错误率纪律见 Romano & Wolf (2005)。

## VAR: yao_2021_tone_hw_ctx

【变体差分】
本列是 yao_2021 语调的「跟风衰减加权 (hw, herd-decay weighted) × ctx 轨」变体, 取值 = Σ(herd_weight_j × yao_2021_score_ctx_j) / Σ(herd_weight_j), 其中权重 herd_weight 由 stage 24 (herd_decay) 按报道的时间聚集度赋值 —— 同一事件短时间内被大量跟风转载的后发报道被降权, 以抑制羊群式重复报道对语调均值的过度影响 (方法学锚点 Tetlock 2011 的媒体跟风衰减)。相对 canonical ctx 列的等权均值, 本列改用跟风衰减权重的加权均值, 检验语调水平是否对『把扎堆跟风报道压权』这一处理稳健。分母按轨独立取 sum_herd_weight_ctx (三轨各用自身权重和, 避免跨轨错配), 权重和为 0 时置 NaN。本列与 hw_full、hw_ss 三轨并排, 又与 equal/vw/mw 三种加权方案并排, 各臂各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。ctx 轨采 conditional-on-full 口径, 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_hw_full

【变体差分】
本列是「跟风衰减加权 (hw) × full 轨」变体, 取值 = Σ(herd_weight_j × yao_2021_score_full_j) / Σ(herd_weight_j), 分母取 full 轨自身的 sum_herd_weight_full。herd_weight 对短时间内密集跟风转载的后发报道降权, 使语调均值更反映独立信息源而非重复噪声 (Tetlock 2011 的跟风衰减脉络)。在 full 轨 (canonical 文本轨、留篇门控判据轨) 上, 本列是 hw 加权方案下样本最完整的语调测度, 与 canonical 的等权 yao_2021_tone_full 直接对照, 检验主结论是否对『扎堆报道降权』稳健。它同时与 vw_full (提及密度加权)、mw_full (媒体权威加权) 构成三种独立加权理论的并排臂 —— 三者分别对应 Hassan 等 (2019)、Holzman 等 (2023)、Tetlock (2011) 三条脉络, 各自 just-identified、互为稳健、不分主次, 严禁混进同一 over-identified Hansen J。权重和为 0 的稀疏 bank-year 置 NaN。本列亦与其他五部词典的同口径 hw_full 列互为稳健性。

## VAR: yao_2021_tone_hw_ss

【变体差分】
本列是「跟风衰减加权 (hw) × ss 轨」变体, 取值 = Σ(herd_weight_j × yao_2021_score_ss_j) / Σ(herd_weight_j), 分母取 ss 轨的 sum_herd_weight_ss。ss 轨文本仅取银行与金科同句共现的 ±N 句窗 (标题 prepend), 无同句共现时优雅回退为全文正文并置 ss_is_fallback (镜像 ctx 回退语义)。本列在最窄的银行—金科强共现语境上叠加跟风衰减加权, 度量的是「压低扎堆报道后、银行金科直接关联语境内」的 yao_2021 语调, 是三轨 × 三加权网格里语境最纯、也最易受回退与稀疏性影响的一格。当 stage 24 未产出 ss 轨权重列时, ss hw 分母退化为全 NaN, 本列随之 NaN, 属预期降级而非缺陷 (per-track 独立降级, 不连坐 full/ctx)。本列与 hw_full、hw_ctx 三轨并排、又与 equal/vw/mw 加权并排, 各臂各自 just-identified、互为稳健、不分主次, 禁混同一 over-identified Hansen J; ss 轨同为 conditional-on-full, 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_mw_ctx

【变体差分】
本列是 yao_2021 语调的「媒体权威加权 (mw, media-authority weighted) × ctx 轨」变体, 取值 = Σ(media_authority_weight_j × yao_2021_score_ctx_j) / Σ(media_authority_weight_j), 分母取 sum_media_authority_weight。权重 media_authority_weight 按报道所属媒体来源的权威性/影响力赋值 (方法学锚点 Holzman 等 2023, 论证权威媒体的语调更具定价与纪律作用), 使高权威媒体的语调在 bank-year 均值里占更大份额。相对 canonical ctx 列的等权均值, 本列检验语调水平是否对『按媒体权威加权』稳健 —— 若主结论仅由大量低权威转载驱动, 加权后会显著改变。ctx 轨文本收窄至银行/金科实体上下文窗。本列与 mw_full、mw_ss 三轨并排、又与 equal/vw/hw 加权方案并排, 各臂各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。权重和为 0 时置 NaN; ctx 轨采 conditional-on-full 口径, 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_mw_full

【变体差分】
本列是「媒体权威加权 (mw) × full 轨」变体, 取值 = Σ(media_authority_weight_j × yao_2021_score_full_j) / Σ(media_authority_weight_j)。权重按媒体来源权威性赋值 (Holzman 等 2023): 权威媒体的报道语调更可能被市场认真定价并对银行形成外部纪律, 故给予更高份额。在 full 轨 (canonical、留篇门控判据轨) 上, 本列是 mw 加权方案下样本最完整的语调测度, 与等权 yao_2021_tone_full 直接对照, 检验主结论是否对『放大权威媒体语调』稳健。它与 vw_full (提及密度加权, Hassan 等 2019)、hw_full (跟风衰减加权, Tetlock 2011) 一并构成三条独立加权理论的并排臂, 各自 just-identified、互为稳健、不分主次, 严禁混进同一 over-identified Hansen J。权重和为 0 的稀疏 bank-year 置 NaN。本列亦与其他五部词典的同口径 mw_full 列互为稳健性、不分主次。

## VAR: yao_2021_tone_mw_ss

【变体差分】
本列是「媒体权威加权 (mw) × ss 轨」变体, 取值 = Σ(media_authority_weight_j × yao_2021_score_ss_j) / Σ(media_authority_weight_j)。ss 轨文本仅取银行与金科同句共现的 ±N 句窗 (标题 prepend), 无同句共现时回退为全文正文并置 ss_is_fallback (镜像 ctx 回退)。本列在最窄的银行—金科强共现语境上叠加媒体权威加权 (Holzman 等 2023), 度量「按权威加权后、银行金科直接关联语境内」的 yao_2021 语调, 是三轨 × 三加权网格里语境最纯的一格之一。它是首要稳健性轨而非主轨: ss 轨对同句共现的稀疏性与回退最敏感, 在 T 较小的开发样本上易退化。本列与 mw_full、mw_ctx 三轨并排、又与 equal/vw/hw 加权并排, 各臂各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; ss 轨同为 conditional-on-full, 行宇宙是 full 留篇集子集。权重和为 0 时置 NaN。

## VAR: yao_2021_tone_ss

【变体差分】
本列是 yao_2021 家族 canonical (等权、全样本) 语调的 ss 轨版本, 取值 = mean(yao_2021_score_ss), 即对某 bank-year 内全部留篇报道、用 ss 轨文本算出的 yao_2021 词典语调求等权均值。它与核心列 yao_2021_tone_full 的唯一差别是文本轨: ss (same-sentence) 轨仅取银行实体与金融科技词在同一句内共现的 ±N 句窗 (标题 prepend), 是三轨中语境最窄、对「银行—金科直接关联」这一构念最纯净的一轨。当某篇报道不存在银行与金科同句共现时, ss 轨优雅回退 —— content_ss 退化为全文正文、ss_is_fallback 置 True, 该回退语义严格镜像 ctx 轨的回退口径 (以 CLAUDE.md 铁律为准), 并与全文轨共享 n_articles 分母。因此本列度量的是『银行与金科强共现语境下』该银行该年度的 yao_2021 语调, 通常作 canonical 的首要稳健性轨而非主轨。本列不加权、不取离散度、不做落点切分, 是 ss 轨的基准形态。它与 full、ctx 三轨并排, 各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ss 轨采 conditional-on-full 口径 (留篇门控 full-only), 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_std_ctx

【变体差分】
本列是 yao_2021 语调的「离散度 (std) × ctx 轨」变体, 取值 = std(yao_2021_score_ctx), 即某 bank-year 内各篇报道 ctx 轨 yao_2021 语调的横截面标准差, 而非水平均值。它度量的构念与 canonical 完全不同: canonical (yao_2021_tone_ctx) 是该银行该年度媒体口碑的中心趋势, 本 std 列则是口碑的分歧度/异质度 —— std 越大, 说明当年不同报道对该银行金科的评价越两极分化。这类离散度测度常作媒体分歧 (media disagreement) 的代理, 与语调水平正交, 可同时进入回归而不冗余。本列在 ctx 轨 (实体上下文窗) 上计算, 与 std_full、std_ss 三轨并排。单篇或零篇的 bank-year 无法定义标准差, 取 NaN。本列与家族水平类列 (canonical/vw/mw/hw/tech/app) 各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ctx 轨采 conditional-on-full 口径, 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_std_full

【变体差分】
本列是「离散度 (std) × full 轨」变体, 取值 = std(yao_2021_score_full), 即某 bank-year 内各篇报道 full 轨 yao_2021 语调的横截面标准差。它与核心列 yao_2021_tone_full 度量的是互补而非同一的构念: 后者是媒体语调的水平 (中心趋势), 本列是语调的离散度 (分歧度)。在 full 轨 (canonical、留篇门控判据轨) 上, 本列是 std 方案样本最完整的分歧度测度, 可作『媒体对该银行金科评价是否两极』的代理变量, 与水平 tone 正交, 二者可同进回归。经济含义上, 高语调离散度可能反映该银行金科战略的不确定性或争议性, 是水平语调之外的独立信息维度。单篇或零篇 bank-year 标准差无定义, 取 NaN。本列与家族全部水平类列、以及其他五部词典的同口径 std_full 列各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: yao_2021_tone_std_ss

【变体差分】
本列是「离散度 (std) × ss 轨」变体, 取值 = std(yao_2021_score_ss), 即某 bank-year 内各篇报道 ss 轨 yao_2021 语调的横截面标准差。ss 轨文本仅取银行与金科同句共现的 ±N 句窗 (标题 prepend), 无同句共现时回退为全文正文并置 ss_is_fallback (镜像 ctx 回退)。本列度量的是『银行—金科强共现语境下』媒体语调的分歧度, 而非水平; 它是三轨 × 离散度网格里语境最纯、也最易受同句共现稀疏性影响的一格 —— 当 bank-year 内合格 (非回退) 篇数不足两篇时标准差无定义、取 NaN, 在 T 较小的开发样本上退化尤为常见, 属预期而非缺陷。本列与 std_full、std_ctx 三轨并排, 各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ss 轨采 conditional-on-full 口径, 行宇宙是 full 留篇集子集。它与家族水平类列度量互补的分歧度构念, 二者正交不冗余。

## VAR: yao_2021_tone_tech_ctx

【变体差分】
本列是 yao_2021 语调的「底层技术 (tech) 子样本 × ctx 轨」变体, 取值 = mean(yao_2021_score_ctx | innovation_locus == "底层技术")。tech 子样本指按文章级 innovation_locus 分类落在「底层技术」一类的报道 —— 对应 Gomber 等 (2018) 金融科技创新框架中面向底层技术层 (而非应用场景层) 的创新落点。本列度量的是「仅在底层技术类报道内、用 ctx 轨文本」算出的 yao_2021 语调均值, 是家族对创新落点异质性的切分之一。它与同轨的 app_ctx (应用场景子样本) 构成落点对照, 二者之差近似技术层减应用层的舆论温差, 但本列不做差分 (差分由 tone_gap 系列承担)。ctx 轨文本收窄至银行/金科实体上下文窗。当某 bank-year 在底层技术子样本下无报道时取 NaN。本列与 tech_full、tech_ss 三轨并排, 又与 app 子样本并排, 各臂各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ctx 轨采 conditional-on-full 口径, 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_tech_full

【变体差分】
本列是「底层技术 (tech) 子样本 × full 轨」变体, 取值 = mean(yao_2021_score_full | innovation_locus == "底层技术"), 即把某 bank-year 内被 LLM 判为面向底层技术层创新的报道筛出, 用 full 轨文本算 yao_2021 词典语调后求均值。full 轨是 canonical 文本轨与留篇门控判据轨, 因此本列在底层技术子样本内水平最完整、样本最全, 贴近「该银行该年度技术层报道的整体口碑」。与 app_full 并列时, 两列覆盖 Gomber 等 (2018) 框架下底层技术 vs 应用场景两个互斥落点, 是家族对创新落点异质性的直接切分; 二者之差 (由 tone_gap_tech_app 承担, 附 min(n_tech,n_app)≥5 的混杂防御) 反映技术层与应用层的舆论温差。但 tech 与 app 两个子样本 tone 仅作规格稳健并排, 严禁混进同一 over-identified Hansen J。底层技术子样本为空时取 NaN。本列亦与其他五部词典的同口径 tech_full 列互为稳健性、不分主次; tech/app 子样本分类依赖 LLM 的 innovation_locus 判定, 分类置信度偏低时子样本 tone 噪声较大, 使用时须结合 avg_category_confidence 诊断。

## VAR: yao_2021_tone_tech_ss

【变体差分】
本列是「底层技术 (tech) 子样本 × ss 轨」变体, 取值 = mean(yao_2021_score_ss | innovation_locus == "底层技术")。ss 轨文本仅取银行与金科同句共现的 ±N 句窗 (标题 prepend), 无同句共现时回退为全文正文并置 ss_is_fallback (镜像 ctx 回退语义)。本列度量「底层技术类报道里、银行与金科强共现语境下」的 yao_2021 语调, 是家族三轨 × 落点子样本网格里语境最纯、也最受同句共现稀疏性与 LLM 落点分类噪声双重影响的一格 —— 在底层技术子样本下同时要求同句共现的 bank-year 往往篇数很少, 空样本取 NaN 属常见的预期退化。它与同轨的 app_ss 构成落点对照。本列与 tech_full、tech_ctx 三轨并排, 又与 app 子样本并排, 各臂各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ss 轨采 conditional-on-full 口径, 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_vw_ctx

【变体差分】
本列是 yao_2021 语调的「提及密度加权 (vw, value/mention-density weighted) × ctx 轨」变体, 取值 = Σ(mention_density_j × yao_2021_score_ctx_j) / Σ(mention_density_j), 分母取 sum_mention_density。权重 mention_density 按报道对该银行的提及密度 (提及次数/篇幅) 赋值, 使密集提及该银行的报道在语调均值里占更大份额 (方法学锚点 Hassan 等 2019 的提及密度加权度量法)。相对 canonical ctx 列的等权均值, 本列检验语调水平是否对『按提及密度加权』稳健 —— 顺带提及与深度报道被赋予不同份额。ctx 轨文本收窄至银行/金科实体上下文窗。本列与 vw_full、vw_ss 三轨并排, 又与 equal/mw/hw 加权方案并排, 各臂各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。分母 (提及密度和) 为 0 时置 NaN; ctx 轨采 conditional-on-full 口径, 行宇宙是 full 留篇集子集。

## VAR: yao_2021_tone_vw_full

【变体差分】
本列是「提及密度加权 (vw) × full 轨」变体, 取值 = Σ(mention_density_j × yao_2021_score_full_j) / Σ(mention_density_j), 分母取 sum_mention_density。权重按报道对该银行的提及密度赋值 (Hassan 等 2019 的 firm-level 提及密度加权): 深度、密集提及该银行的报道对其口碑的信息含量更高, 故给予更大份额。在 full 轨 (canonical、留篇门控判据轨) 上, 本列是 vw 加权方案下样本最完整的语调测度, 与等权 yao_2021_tone_full 直接对照, 检验主结论是否对『放大高提及密度报道』稳健。它与 mw_full (媒体权威加权, Holzman 等 2023)、hw_full (跟风衰减加权, Tetlock 2011) 一并构成三条独立加权理论的并排臂, 各自 just-identified、互为稳健、不分主次, 严禁混进同一 over-identified Hansen J。提及密度和为 0 的稀疏 bank-year 置 NaN。本列亦与其他五部词典的同口径 vw_full 列互为稳健性、不分主次。

## VAR: yao_2021_tone_vw_ss

【变体差分】
本列是「提及密度加权 (vw) × ss 轨」变体, 取值 = Σ(mention_density_j × yao_2021_score_ss_j) / Σ(mention_density_j), 分母取 sum_mention_density。ss 轨文本仅取银行与金科同句共现的 ±N 句窗 (标题 prepend), 无同句共现时回退为全文正文并置 ss_is_fallback (镜像 ctx 回退语义)。本列在最窄的银行—金科强共现语境上叠加提及密度加权 (Hassan 等 2019), 度量「按提及密度加权后、银行金科直接关联语境内」的 yao_2021 语调, 是三轨 × 三加权网格里语境最纯、也最受同句共现稀疏性影响的一格之一, 通常作首要稳健性轨而非主轨。本列与 vw_full、vw_ctx 三轨并排, 又与 equal/mw/hw 加权方案并排, 各臂各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ss 轨采 conditional-on-full 口径, 行宇宙是 full 留篇集子集。提及密度和为 0 时置 NaN。

<!-- rendered-citations:begin -->

<!-- rendered-citations:end -->
