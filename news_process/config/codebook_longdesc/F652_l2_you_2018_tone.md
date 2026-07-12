---
family_id: F652
columns:
- you_2018_tone_app_ctx
- you_2018_tone_app_full
- you_2018_tone_app_ss
- you_2018_tone_ctx
- you_2018_tone_full
- you_2018_tone_hw_ctx
- you_2018_tone_hw_full
- you_2018_tone_hw_ss
- you_2018_tone_mw_ctx
- you_2018_tone_mw_full
- you_2018_tone_mw_ss
- you_2018_tone_ss
- you_2018_tone_std_ctx
- you_2018_tone_std_full
- you_2018_tone_std_ss
- you_2018_tone_tech_ctx
- you_2018_tone_tech_full
- you_2018_tone_tech_ss
- you_2018_tone_vw_ctx
- you_2018_tone_vw_full
- you_2018_tone_vw_ss
unit: 语调得分 (无量纲, 文章级归一化后落 [-1,+1]; bank-year 聚合为加权均值, _std 变体为组内标准差)
formula: "article you_2018_score = Σ(final_score)/Σ|final_score| ∈ [-1,+1] (含否定翻转/程度副词≤×3.0/转折×1.5 规则); panel you_2018_tone{w}{track} = Σ(weight·score)/Σ(weight) over bank-year 全留篇集; weight ∈ {等权(无后缀), 版位显著_vw, 媒体权威_mw, 羊群衰减_hw}; _std = 组内 sd(score); _tech/_app = innovation_locus 子集条件均值"
producer: news_process/pipeline/panel/encode.py::aggregate_panel (article 层 news_process/pipeline/sentiment/tone_words.py::classify_batch → _analyze_single_article → _compute_sentiment_with_rules)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (you_2018_score{track})
- 24_herd_decay_processor.parquet (herd_weight{track}, _hw 分母)
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
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
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
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
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
本家族度量的是银行金融科技新闻在文章层被 You et al. (2018) 中文金融情感词典判定的语调极性, 再按银行年聚合而成的连续测度。构念上它回答的问题是: 在某一银行某一年被媒体报道的金融科技相关叙事, 整体上偏正面(利好、进取、成效)还是偏负面(风险、亏损、监管收紧)。之所以以 You et al. (2018) 为命名锚, 是因为该文 "Who Captures the Power of the Pen?" 系统构建并验证了适配中国媒体语境的中文金融情感词表, 并揭示了官方媒体与市场化媒体在报道语气上的系统差异——这一"笔的权力"分布差异, 正是本家族后续引入媒体权威加权轨(见下)的直接理论来源。词典法情感测度在会计与金融文本分析中已是主流范式之一, Loughran & McDonald (2011) 奠定了以领域专用词表替代通用心理学词表的方法论转向, Loughran & McDonald (2016) 的综述进一步确立了词典法与统计学习法并置、互为验证的实证规范。本项目对中文语料的处理, 在词表选择上不依赖单一来源, 而是把 You et al. (2018) 与 Du et al. (2022)、以及其他若干中文金融词典并列为一组"六词典"消融梯度, 使任一词表的构造偏差不至于单独驱动主结论。

【数据来源】
文章层输入来自三轨物化产物 14_materialize_ctx.parquet 的 content_full / content_ctx / content_ss 三列, 经 stage 22 词典打分落 22_tone_words.parquet 的 you_2018_score{track} 列; 媒体权威加权所需的媒体级权重在 encode 层由 compute_media_authority_weights 计算, 羊群衰减加权所需的 herd_weight{track} 来自 stage 24; 最终 bank-year 聚合在 encode.py::aggregate_panel 完成并落 40_panel_yearly.parquet。语料的银行年宇宙遵循 full-only 留篇门控(2026-06-29 口径): 一篇报道是否计入"银行金融科技报道", 只由 llm_verified_full == True 判定; 因此本家族所有列的行宇宙都是 full 留篇集, ctx / ss 轨是在该宇宙内的 conditional-on-full 测度, 而非各自独立的留篇集。

【方法学与计算】
文章层的 you_2018_score 采用归一化极性公式: normalized_score = Σ(final_score) / Σ|final_score|, 取值落于 [-1, +1]。其中 final_score 是逐命中词的带符号权重, 在裸词典极性基础上叠加三条语言学规则——否定翻转(前置否定词把极性取反)、程度副词放大(最高可达 ×3.0)、转折结构调节(×1.5); 分母取带符号权重的绝对值之和而非裸匹配词数, 使得同一词若同时命中正负两表(跨类重叠词)对分子净贡献为零、对分母贡献两倍绝对值, 从而把该词的语调温和地拉向中性而不武断剔除。这一"全规则"口径是本家族的语调基线; 与之正交的 negonly(仅否定、去程度与转折)消融属于另一家族, 不在本家族列内。银行年聚合则按加权均值 Σ(weight·score)/Σ(weight) 展开, 权重方案区分四种: 等权(无权重后缀, 每篇计一)、版位显著加权 _vw(按报道版面位置与导语显著度赋权, 呼应显要报道对市场影响更大的直觉)、媒体权威加权 _mw(按媒体来源权威度赋权, 直接落地 You et al. (2018) 官媒与市场化媒体"笔的权力"不等的发现)、羊群衰减加权 _hw(按 stage 24 羊群衰减权重赋权, 压低同质化跟风报道的重复计入)。此外 _std 变体不是均值而是银行年组内文章语调的样本标准差, 度量的是叙事语气的离散/分歧程度而非水平; _tech 与 _app 则是把文章按创新落点(innovation_locus)划分为"底层技术"与"应用场景"两个子集后分别取条件均值, 呼应 Gomber et al. (2018) 对金融科技底层设施创新与应用场景创新的构念分野。

【三轨文本架构】
本家族的三轨(full/ctx/ss)对应三种文本判定域, 均在 stage 14 ctx_materializer 物化为独立文本列并置回退标记。full 轨(content_full)= 标题 prepend 后拼接全文正文, 信息量最大但也最易混入与目标银行无关的语气噪声; ctx 轨(content_ctx)= 标题 prepend 后拼接目标实体上下文窗, 把语气判定聚焦到银行等实体附近的语境, 提升语气归因精度; ss 轨(content_ss)= 标题 prepend 后拼接"银行与金融科技词同句±N 窗"(半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 最贴近"针对该银行金融科技活动"的语气。三轨判定的银行侧口径为否定加短名过滤, 金融科技侧为裸 AC 词表匹配。留篇门控为 full-only(2026-06-29): 一篇是否算银行金融科技报道只由 llm_verified_full == True 决定, 故 full 轨定义整个家族的行宇宙, ctx / ss 降为该宇宙内的 conditional-on-full 测度轨与稳健性轨, per-track 列仍按各自轨道分子分母独立计算, 绝不借用 full 轨分母。ss 轨回退语义镜像 ctx: 当某篇不存在银行与金融科技词的同句共现时, content_ss 优雅回退为全文正文并置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母, 绝不静默清空; 若金融科技 AC 词表为空则回退标记全 True 优雅降级。三轨文本域宽窄不同, 是判定域这一维度上的规格稳健性并排, 而非同一测度的冗余副本。

【文献定位】
在测量学谱系上, 本家族属于词典/词表法一支, 与统计学习法(如 FinBERT 家族)和大模型投票法(stage 21 三家 LLM)构成三方互证的测量三角。Frankel et al. (2022) 与 van Atteveldt et al. (2021) 均实证指出词典法在披露文本与新闻文本上的信度与外部效度需以人工标注和机器学习法交叉校验, 本项目正是以此为据把词典轨、BERT 轨、LLM 轨并置而非单选; 词典法的独特价值在于它完全透明、可逐词复算、零 API 成本且确定性可复现, 因而适合充当昂贵 LLM 轨语气的确定性对照基准。Algaba et al. (2020) 对"情感计量学"方法论的综述, 为把多词典、多加权、多轨道视为一组规格稳健性并排提供了方法论支撑, 其核心主张是任何单一情感测度都携带构造选择的自由度, 唯有把这些自由度显式展开为并排的稳健性梯子才能证明主结论不被某一构造选择驱动。中文语境下, Du et al. (2022) 论证了金融情感词表的语言与领域专用性——英文金融词表直译到中文会系统性误判, 因为金融正负面表达在中文里高度依赖领域惯用语与政治语境; Ma et al. (2025) 进一步给出细粒度中文投资者情感词典 CN-FSD, 二者共同说明中文金融情感测度不宜照搬英文词表, 也印证本项目采用多部中文词表并排消融的必要性; 而 Barbaglia et al. (2025) 对经济文本的词典法给出跨语言的方法学范式, 说明词典法在经济新闻这一具体文本类型上仍具竞争力。媒体语气与资产定价的因果链条则可追溯至 Tetlock (2007) 关于媒体悲观语气预测股市短期下行与随后回归的经典发现, 该文奠定了"媒体语气是可定价信息"的实证传统; Holzman et al. (2023) 关于媒体情感需按媒体权威度加权方能反映市场纪律作用的证据, 正是本家族 _mw 轨的直接锚。银行×年语气聚合的操作口径参照 Marchetti et al. (2025) 对意大利银行融资条件媒体语气的银行年度聚合实践, 该文示范了如何把文章级语气按银行年折叠为可进入面板回归的暴露度量。语言学规则(否定翻转/程度副词/转折)的处理则依据 Taboada et al. (2011) 的词典法规则体系, 该文系统论证了否定、程度、转折三类语境算子对词典法情感准确度的边际贡献。金融科技创新的底层技术与应用场景两分, 落点判定依据 Gomber et al. (2018) 对金融科技创新力量的构念框架。

【识别策略定位】
本家族在识别框架中通常充当处理变量(treatment)一侧的媒体叙事测度, 而非结果变量。canonical 列 you_2018_tone_full 与主线 P1 论文(bank_fintech_tone)共享的 llm_vote_tone_full 属于同一构念"银行金融科技报道语气"的不同测量实现, 二者互为构念替代测量; 词典轨的价值在于它是完全透明、可复算、零 API 成本的确定性测度, 可作为 LLM 轨语气的稳健性对照。由于本项目内所有情感测度都嵌入 IV 扩展框架(同组 LOO 均值、广义 Bartik、媒体来源 house-style 暴露三引擎), 本家族的各轨语气可作为被工具化的内生媒体叙事: 同组同侪的语气均值提供 leave-one-out 工具, 银行金融科技暴露的广义 Bartik 分解提供份额-冲击工具, 媒体来源的固有语气风格提供 house-style 暴露工具, 三条工具各自 just-identified 地为语气回归提供外生变异。须强调的是, 本家族的语气水平列(等权与三加权轨)度量的是媒体如何评价银行金融科技活动, 而非银行金融科技活动本身的强度或成效——后者由 fintech_intensity、attention、substance/locus/collab 等家族分别度量; 因此在因果链上, 本家族语气常被建模为银行金融科技暴露对某个财务或市场结果(如 funding_cost)传导的媒体中介渠道, 而非结果本身。这一定位决定了它在稳健性梯子里的角色: 语气水平的多重构造(词典/加权/轨道/落点)是对同一处理变量的多重测量, 用以证明处理效应不被语气测量口径驱动。须进一步区分处理变量与结果变量两套体系: 本家族语气属处理变量(treatment)一侧, 主线 P1 论文 bank_fintech_tone 的结果变量(如 funding_cost 等外部财务哨兵列)另行构造, 二者在因果图上分居箭头两端, 绝不可把语气水平当作被解释的成效结局。同侪同组的语气均值提供 leave-one-out 工具时, 须满足排他性约束——同组银行的媒体语气仅通过本行媒体叙事这一渠道影响本行结果, 而不经由其他直接渠道; 广义 Bartik 分解则把银行金融科技暴露拆为份额与冲击两部分, 以行业级冲击的外生性支撑识别; 媒体来源 house-style 暴露工具利用某银行报道所依赖的媒体组合的固有语气风格。三条工具各自 just-identified, 严禁把互为稳健性的多轨语气叠进同一 over-identified 的工具集合, 否则 Hansen J 过度识别检验将检验一个由构造自由度人为制造的伪约束。词典轨在此框架中的独特价值是它不依赖任何在线服务、逐位可复现, 因而可作为昂贵 LLM 语气工具化结果的确定性对照——若两种测量范式下的 IV 系数方向一致, 则识别结论不被语气测量范式驱动。

【与相邻测度的构念区分】
须与三类相邻测度严格区分。其一, 与 you_2018 的 clarity/definite/ambiguous 家族区分: 后者来自 You et al. (2018) Panel C/D 的"确定性/模糊性"词表, 度量的是叙事的确定程度而非情感极性, 二者共用命名锚但构念正交。其二, 与其他五部词典的同名 tone 列(jiang_2021 / yao_2021 / bian_2021 / du_2022 等)区分: 它们是六词典消融梯度中的平行臂, 词表不同、极性判定不同, 互为稳健性而非可加。其三, 与 negonly 规则消融变体区分: 本家族列均为全语言学规则口径(否定翻转 + 程度副词 + 转折三规则齐备), 不含仅否定的规则退化臂 you_2018_negonly_tone, 后者属规则消融梯度的另一家族。其四, 与 LLM 投票语气 llm_vote_tone 及 BERT 净语气区分: 三者是同一构念的三种测量范式(词典/大模型/微调分类器), 互为方法学稳健性对照, 数值口径与信息来源迥异, 不可相互替代或求和。其五, 与银行侧的 fintech_intensity、attention 等强度/关注度家族区分: 本家族度量语气的正负极性(评价方向), 强度家族度量报道的多寡与篇幅(评价体量), 二者构念正交, 可同时进入模型。

【加权方案的构造细节与互补性】
四种加权聚合并非任意堆叠, 而是分别针对语气归因的三类不同"谁的声音更重要"问题。等权(无后缀)假设每篇报道对市场的语气影响相同, 是最保守的基线, 但会让一稿多发的跟风报道与独家深度报道等量齐观。版位显著加权 _vw 回答"这篇放得多显要": 权重取版面位置与导语显著度(版位=物理显著, 导语=文本显著), 因为显要报道更可能进入投资者视野, 与 Tetlock (2007) 显著媒体语气影响市场的逻辑一致。媒体权威加权 _mw 回答"哪家媒体在说": 权重取媒体来源的机构权威度, 由 compute_media_authority_weights 归一化到均值 1 附近, 直接落地 You et al. (2018) 官媒与市场化媒体"笔的权力"不等的发现, 也与 Holzman et al. (2023) 权威媒体情感更具市场纪律作用的证据相容。羊群衰减加权 _hw 回答"这篇是独立信息还是跟风重复": 权重取 stage 24 羊群衰减权重, 对高度同质、扎堆转载的报道给予折减, 使语气聚合更接近独立信息含量加权而非发文条数加权; 其分母按三轨独立取 sum_herd_weight, ss 轨分母可能因 stage 24 未跑同句轨而缺失, 由 hw_denom_by_track 兜底。三种加权维度(报道显著度、媒体权威度、信息冗余度)彼此正交: 一篇小报头条、一篇权威大报内页短讯、一篇被十家转载的通稿, 在三种加权下会得到系统不同的相对权重, 因此三轨联合验证能刻画语气结论对"谁的声音更重要"这一假设的敏感度。

【离散度量与落点子集的构造细节】
_std 变体把聚合算子由加权均值改为银行年组内文章语气分数的样本标准差, 度量的不是语气水平而是语气分歧: 高 _std 表示同一银行同一年的金融科技报道语气众说纷纭、市场缺乏共识, 低 _std 表示叙事高度一致。该二阶矩测度与一阶矩的水平列构念正交, 可同时进入模型而不冗余, 并直接服务于本项目"高覆盖 + 高波动 = 高叙事暴露"的金融科技暴露度构造(fintech_exposure = ln_coverage × tone_std)。_tech 与 _app 则把文章按创新落点(innovation_locus_full)切分为"底层技术"与"应用场景"两个子集后分别取条件均值, 落点判定统一取自 full 轨, 分母分别为 n_articles_tech 与 n_articles_app; 两子集之和一般不等于全样本, 因存在落点未判定或不属二分类的文章。该切分呼应 Gomber et al. (2018) 对金融科技创新的两分——底层技术设施创新与应用场景创新在商业逻辑、监管敏感度、市场反应上不同, 分别度量语气能揭示"是哪一类金融科技活动"驱动了银行年语气。

【已知局限与稳健性梯子】
本家族天然是一组多维度稳健性梯子的乘积: 六词典维度 × 四加权方案(等权/vw/mw/hw)加一个离散度量(std)加两个落点子集(tech/app) × 三轨(full/ctx/ss)。铁律是: 这些维度上的每一列都各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨道、不同加权、不同词典的语气列混进同一 over-identified Hansen J 过度识别检验——混用会人为制造并不存在的过度识别约束, 破坏工具变量的正当性。真正的族内多重检验校正应交由根级 rwolf / 跨模型 FWER 模板处理, 其方法学依据是 Romano & Wolf (2005) 的逐步多重检验框架。已知局限包括: 词典法对讽刺、隐含语气、否定嵌套深层结构不敏感(Taboada et al. (2011) 已述), 中文分词(jieba 0.42.1 冻结)对新兴金融科技术语的切分误差, 以及在 T=2 开发样本上 _std / ss 轨可能因组内篇数不足而退化为常数或缺失(生产 T=18 语料上恢复正常)。ss 轨的回退语义镜像 ctx 轨: 当某篇不存在银行与金融科技词的同句共现时, content_ss 回退为全文正文并置回退标记, 与 ctx 共享 n_articles 分母, 属优雅降级而非缺失。词典法本身还有几处已知的构造敏感性须在解读时留意: 其一, 归一化分母取带符号权重绝对值之和而非裸词数, 使跨类重叠词(同时命中正负两表)对分子净贡献为零、对分母贡献两倍绝对值, 从而温和拉中性而非武断剔除, 这一设计虽稳健却可能在重叠词密集的文本上系统性压低语气绝对值。其二, 程度副词最高放大 ×3.0、转折结构 ×1.5 的规则系数取自 Taboada et al. (2011) 的经验校准而非中文语料重新估计, 属研究者选择, 与之正交的规则消融梯度(negonly 等)在另一家族里验证主结论不被规则系数驱动。其三, 媒体权威权重与羊群衰减权重均在特定口径下归一化到均值 1 附近, 权重构造本身携带假设, 故四加权方案(等权/vw/mw/hw)并排本就是对"谁的声音更重要"这一假设的敏感性检验。这些敏感性并不构成对本家族的否定, 恰是把构造自由度显式展开为并排稳健性梯子的动机所在——正如 Algaba et al. (2020) 与 Frankel et al. (2022) 所强调, 单一情感测度的可信度须由多测度、多范式的交叉一致性支撑, 而非由某一构造选择的内在优越性支撑。最后须重申测量三角的互证逻辑: 词典轨、BERT 轨、LLM 三家投票轨是同一"银行金融科技报道语气"构念的三种测量范式, 各自 just-identified 并排、互为方法学稳健性, 数值口径与信息来源迥异, 既不可相互替代也不可求和进同一 over-identified Hansen J; 三者一致方能证明结论不被测量范式驱动, 三者分歧则定位出测量口径敏感的边际样本。

## VAR: you_2018_tone_full

【变体差分】
本列是家族 canonical 核心列(tier=core), 是理解其余二十列差分的参照原点。它取 full 轨: 文章文本 = 标题 prepend 后拼接全文正文(content_full), 覆盖整篇报道而非实体窗口或同句窗口, 因此在三轨中信息量最大、噪声也最高。它取等权聚合: 银行年内每篇留篇文章的 you_2018_score_full 计一份权重, 均值即本列, 不按版位、媒体权威或羊群衰减重加权, 也不做子集切分。它取全语言学规则口径: 文章分数已在 stage 22 叠加否定翻转、程度副词(≤×3.0)、转折(×1.5)三规则并归一化到 [-1,+1]。相对于 ctx / ss 轨, 本列以全文为判定域, 是留篇门控的判定轨——full-only 门控(2026-06-29)下, 一篇是否算银行金融科技报道只看 full 轨的 LLM 核验, 故 full 轨定义了整个家族的行宇宙, ctx / ss 只在此宇宙内做 conditional 测度。相对于 _vw / _mw / _hw, 本列是它们退化为均匀权重时的特例, 即当所有权重相等时四者数值收敛; 三种加权轨是本列的稳健性伴随而非替代。相对于 _std, 本列度量语气水平(一阶矩), _std 度量语气分歧(二阶矩), 二者构念正交。相对于 _tech / _app, 本列在全部留篇文章上聚合, 不按创新落点切分。作为词典法 canonical, 本列与主线 P1 的 LLM 投票语气 llm_vote_tone_full 互为同构念替代测量, 是零成本、确定性、可完全复算的对照轨: 只要冻结词表(tone_dicts.json 为 SSOT)与 jieba 0.42.1 分词版本不变, 本列在任意机器上逐位可复现, 不依赖任何在线服务, 这使它在稳健性梯子里承担"当 LLM 语气与词典语气一致时, 结论不被测量范式驱动"的验证职责。数值解读上, 本列取值落于 [-1,+1]: 趋近 +1 表示该银行该年金融科技报道整体高度正面(利好、进取、成效导向), 趋近 -1 表示整体负面(风险、亏损、监管收紧导向), 趋近 0 表示正负相抵或叙事中性; 因分母取带符号权重绝对值之和, 该值天然自归一化, 与报道篇数无关, 故不同银行年间可直接比较语气水平而不受报道体量干扰。文章级分数在 stage 22 由 classify_batch 逐批调度、per-row 经 _analyze_single_article 落到 _compute_sentiment_with_rules 打分产出, 其中程度副词最高放大 ×3.0、转折结构 ×1.5、前置否定翻转极性, 跨类重叠词(同时命中正负两表, you_2018 词表内约 5 词)对分子净贡献为零、对分母贡献两倍绝对值, 从而温和拉中性而非武断剔除。铁律重申: 本列与家族内其余加权/轨道/词典臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; 混用会把互为稳健的多重测量误当作多个独立矩条件, 人为制造过度识别约束并使 Hansen J 检验失去意义。族内多重检验交由根级 rwolf 与跨模型 FWER 模板按 Romano & Wolf (2005) 逐步法校正, 该框架在控制族错误率的同时保留检验功效。本列的语言学规则、归一化分母口径、以及跨类重叠词拉中性处理, 均与 You et al. (2018) 词表及 Taboada et al. (2011) 规则体系一致, 而其作为 bank-year 媒体语气聚合的操作口径参照 Marchetti et al. (2025) 与 Holzman et al. (2023); 与 clarity 家族(You et al. (2018) Panel C/D 确定性/模糊性词表)构念正交, 后者度量叙事确定程度而非情感极性, 二者共用命名锚但不可混用。作为 tier=core 列, 本列是家族对外的默认语气暴露度量, 也是论文正文表格里报道 you_2018 词典轨系数时的首选列; 其余二十列在正文之外的稳健性附录里以并排臂形式出现, 用来展示主系数在轨道、加权、落点、离散算子四个维度上的稳定性。数值上再补一层解读: 由于分母自归一化, 本列与报道篇数无关, 因此它刻画的是"平均一篇报道的语气倾向"而非"语气的累积体量"; 若研究者关心语气的总暴露量, 应把本列与覆盖度家族(如 ln_coverage)相乘构造交互暴露, 而非直接用本列充当体量代理。

## VAR: you_2018_tone_ctx

【变体差分】
本列取 ctx 轨、等权聚合、全语言学规则, 与 canonical you_2018_tone_full 的唯一差分在文本判定域。ctx 轨的文章文本 = 标题 prepend 后拼接实体上下文窗口(content_ctx), 即只保留银行等目标实体附近的语境窗, 而非整篇正文。其构念动机是: 当一篇报道涉及多个主体或多个话题时, 全文语气可能被与目标银行无关的段落污染, 实体窗口聚焦能提升语气归因的精确度, 代价是可能丢失窗口外的补充语气信息。因此本列是 full 轨的首要稳健性对照轨: 若主结论在全文语气与实体窗口语气上一致, 则语气归因不受判定域宽窄驱动。行宇宙仍是 full 留篇集(full-only 门控), 本列是该宇宙内的 conditional-on-full 测度, 逐轨算分母 n_articles 亦以此为准。相对 ss 轨, ctx 窗口比同句窗口更宽(实体上下文窗 vs 银行与金融科技同句共现窗)。铁律: full / ctx / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。词表、规则、归一化口径与 canonical 完全一致, 仅文本域不同; 方法学锚同 You et al. (2018) 与 Algaba et al. (2020)。数值解读上本列同样落于 [-1,+1] 且因分母自归一化与报道篇数无关, 可与 full 轨直接比较语气水平: 若某银行年 ctx 语气显著高于 full 语气, 说明全文里与目标银行无关段落把整体语气拖低, 实体窗口聚焦后语气更正面, 这类系统性差异本身即是判定域敏感性的直接证据。ctx 轨作为 full 的首要稳健性对照轨, 在正文主系数报告之外的稳健性附录里承担"语气归因是否被判定域宽窄驱动"的验证职责。

## VAR: you_2018_tone_ss

【变体差分】
本列取 ss 轨(same-sentence)、等权聚合、全语言学规则, 与 canonical 差分同样只在文本判定域, 但比 ctx 更严格。ss 轨的文章文本 = 标题 prepend 后拼接"银行与金融科技词同句±N 窗"的文本(content_ss, 半径由 config/filtering.yaml 的 ss_sentence_radius 控制, 默认 1)。其构念是把语气判定收窄到银行与金融科技真正同句共现的语境, 力求捕捉"针对该银行金融科技活动本身"的语气而非泛泛的银行报道语气。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金融科技词的同句共现时, content_ss 优雅回退为全文正文并置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母, 绝不静默清空。因此本列是最贴近"金融科技专属语气"的轨, 也是三轨中最易在稀疏语料上退化的轨——开发 T=2 样本上 ss 轨可能因同句共现篇数不足而近零方差或缺失, 生产 T=18 恢复。行宇宙仍是 full 留篇集(full-only 门控)。铁律: 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。词表与规则口径同 canonical。数值解读上本列落于 [-1,+1] 且与报道篇数无关, 但其有效样本是三轨中最小的——只有真正存在银行与金融科技同句共现的报道才进入非回退计算, 因此本列语气对"针对该银行金融科技活动本身"的评价最敏感, 也最贴近处理变量的构念内核。当本列与 ctx、full 轨语气方向一致时, 说明语气结论稳健于判定域从全文到实体窗再到同句窗的逐级收窄; 当三轨方向分歧时, 本列定位出"泛银行报道语气"与"金融科技专属语气"不一致的边际银行年, 这类分歧样本正是判定域敏感性最强的观测。ss 轨在正文之外承担最严判定域的稳健性验证职责。

## VAR: you_2018_tone_vw_full

【变体差分】
本列在 canonical you_2018_tone_full 基础上把等权聚合替换为版位显著加权(vw = value/visibility weighting), 轨道仍为 full。聚合公式由简单均值改为 Σ(weight·score)/Σ(weight), 权重取文章的版面位置与导语显著度(版位=物理显著、导语=文本显著), 使刊于显要版面、进入导语的报道对银行年语气贡献更大, 弱化边栏、内页短讯的影响。构念动机是: 显要报道更可能被读者与市场注意到, 其语气对预期与定价的影响权重应更高, 这与 Tetlock (2007) 关于显著媒体语气影响市场的证据一致。相对 canonical(等权)本列是加权稳健性伴随轨: 当版位权重退化为均匀时二者收敛。相对 _mw(媒体权威加权)本列按单篇报道的物理/文本显著度加权, 而非按媒体来源的机构权威度加权, 两者正交——一篇小报的头条 vs 权威大报的内页短讯, vw 与 mw 会给出相反的加权方向。相对 _hw(羊群衰减)本列不针对报道的同质化跟风做折减。行宇宙为 full 留篇集。铁律: vw / mw / hw / 等权四种加权各自 just-identified 并排、互为稳健性、不分主次, 严禁四臂混进同一 over-identified Hansen J。权重实现细节: 版位显著度由报道所处版面位置(头版/要闻版/内页/边栏)与是否进入导语两分量合成, 归一化后进入 Σ(weight·score)/Σ(weight) 的加权均值。相对 canonical 本列在正文主系数之外承担"语气结论是否被报道显著度分布驱动"的稳健性验证——若显要报道系统性偏正面或偏负面, 等权与 vw 加权会给出方向不同的银行年语气, 这类差异即揭示语气水平对市场注意力分布假设的敏感度。开发 T=2 样本上因版位元数据稀疏, 加权后有效权重集中于少数报道, 可能放大单篇影响, 生产 T=18 语料上分布趋于平滑。

## VAR: you_2018_tone_vw_ctx

【变体差分】
本列 = 版位显著加权 × ctx 轨, 相对 you_2018_tone_vw_full 的差分在文本域(ctx 实体上下文窗而非全文), 相对 you_2018_tone_ctx 的差分在聚合权重(版位显著加权而非等权)。它同时叠加两个正交维度: 判定域收窄到实体窗口以提升语气归因精度, 权重偏向显要报道以贴近市场注意力分布。因此本列服务于交叉稳健性检验——验证主结论既不被判定域宽窄驱动, 也不被报道显著度加权驱动。行宇宙为 full 留篇集, 本列在其上做 conditional-on-full 的加权聚合。铁律: 三轨与四加权方案各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 轨与 vw 加权任意组合混进同一 over-identified Hansen J。权重定义、词表、语言学规则均与家族一致, 仅文本域与权重方案的组合不同; 方法学参照 Tetlock (2007) 显著媒体语气与 Algaba et al. (2020) 规格稳健性并排框架。本列是"判定域收窄"与"显著度加权"两个正交维度的乘积交叉臂, 其存在的意义正是同时扰动两个自由度以检验交互稳健性: 若主结论在等权全文、等权实体窗、显著加权全文、显著加权实体窗四个组合上一致, 则语气归因既不被判定域也不被显著度加权驱动。数值上本列落于 [-1,+1], 分母为 ctx 轨版位权重之和 sum_vw_weight_ctx, 与报道篇数无关。开发 T=2 上双维度收窄使有效样本更稀, 系数方差偏大, 生产 T=18 恢复稳定, 解读时应以生产语料为准而非以开发样本的退化值下结论。

## VAR: you_2018_tone_vw_ss

【变体差分】
本列 = 版位显著加权 × ss 轨(same-sentence)。相对 you_2018_tone_vw_full 差分在文本域收窄到银行与金融科技同句共现窗, 相对 you_2018_tone_ss 差分在权重由等权改为版位显著加权。它是三轨中最严判定域与显著度加权的组合, 度量"金融科技专属语境下、且以显要报道为主导"的银行年语气。ss 轨回退语义镜像 ctx: 无同句共现的文章回退为全文正文并置 ss_is_fallback, 共享 n_articles 分母, 优雅降级不清空。开发 T=2 上本列易退化(同句共现篇数少 × 加权后有效样本更稀), 生产 T=18 恢复。行宇宙为 full 留篇集。铁律: 三轨与四加权各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。词表与规则口径同 canonical, 仅"最严文本域 × 显著度加权"组合区别于家族其余列。数值上本列落于 [-1,+1], 分母为 ss 轨版位权重之和, 回退篇不参与同句判定但按回退语义仍以全文正文进入语气计算并共享 n_articles 分母。作为家族里判定域最严且加权维度取报道显著度的角落组合, 本列在稳健性附录里承担"金融科技专属语境下、以显要报道为主导时语气结论是否依旧成立"的验证; 它与 mw_ss、hw_ss 三列在同一 ss 判定域上以不同加权维度并排, 三者各自 just-identified、互为稳健性, 严禁三加权臂在 ss 轨内混进同一 over-identified Hansen J。

## VAR: you_2018_tone_mw_full

【变体差分】
本列在 full 轨上把等权聚合替换为媒体权威加权(mw = media-authority weighting)。聚合公式为 Σ(weight·score)/Σ(weight), 权重取自 encode 层 compute_media_authority_weights 计算的媒体来源权威度(归一化到均值 1 附近), 分母为 sum_media_authority_weight。构念动机直接源自 You et al. (2018) "笔的权力"发现: 官方媒体与市场化媒体在语气与市场影响力上系统不等, 因此按媒体机构权威度加权能刻画"更有分量的笔"所主导的语气。这一加权还与 Holzman et al. (2023) 关于媒体情感需按权威度加权方能反映市场纪律作用的证据一致。相对 canonical(等权)本列是加权稳健性伴随轨。相对 _vw(版位显著加权)本列按媒体机构层的权威度加权, 而非按单篇报道的版面/导语显著度加权——二者正交: 前者刻画"哪家媒体在说", 后者刻画"这篇放得多显要"。相对 _hw 本列不做同质化跟风折减。行宇宙为 full 留篇集。铁律: 四加权方案各自 just-identified 并排、互为稳健性、不分主次, 严禁四臂混进同一 over-identified Hansen J。权重实现细节: 媒体权威度在媒体机构层判定(而非报道层), 由 compute_media_authority_weights 依据媒体的行政层级、发行规模、专业财经属性等综合赋权并归一化到均值 1 附近, 因此同一媒体的所有报道共享同一权威权重。相对 _vw(报道层显著度)本列在机构层加权, 二者正交: 一篇市场化小报的头条在 vw 下权重高、在 mw 下权重低, 一篇权威大报的内页短讯则相反。本列在稳健性附录里承担"语气结论是否由权威媒体主导"的验证, 直接落地 You et al. (2018) "笔的权力"官媒/市场化不等的核心发现, 并与 Holzman et al. (2023) 权威媒体情感更具市场纪律作用的证据相容。

## VAR: you_2018_tone_mw_ctx

【变体差分】
本列 = 媒体权威加权 × ctx 轨, 相对 you_2018_tone_mw_full 差分在文本域(实体上下文窗而非全文), 相对 you_2018_tone_ctx 差分在聚合权重(媒体权威加权而非等权)。它交叉验证语气归因既不被判定域宽窄驱动, 也不被媒体来源权威度加权驱动。构念上, ctx 窗口收敛语气归因到目标银行语境, mw 权重把"权威媒体的语气"抬升, 二者组合刻画"权威媒体在贴近银行的语境里说了什么"。行宇宙为 full 留篇集, 本列在其上做 conditional-on-full 的媒体权威加权聚合。铁律: 三轨与四加权各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 轨与 mw 加权组合混进同一 over-identified Hansen J。权重口径同 You et al. (2018) 与 Holzman et al. (2023) 的权威加权动机, 词表与规则同家族。数值上本列落于 [-1,+1], 分母为 ctx 轨媒体权威权重之和 sum_media_authority_weight_ctx, 与报道篇数无关。本列是"判定域收窄到实体窗"与"机构权威加权"两个正交维度的交叉臂, 在稳健性附录里检验语气归因既不被判定域宽窄也不被媒体权威分层驱动。当本列与 mw_full 方向一致时说明权威媒体语气结论稳健于判定域收窄; 当二者分歧时定位出权威媒体在全文与实体窗里语气不一致的边际银行年, 这类样本往往是权威媒体报道涉多主体、语气归因易被窗外段落干扰的观测。开发 T=2 上权威权重因媒体来源覆盖不全可能偏斜, 生产 T=18 趋稳。

## VAR: you_2018_tone_mw_ss

【变体差分】
本列 = 媒体权威加权 × ss 轨。相对 you_2018_tone_mw_full 差分在文本域收窄到银行与金融科技同句共现窗, 相对 you_2018_tone_ss 差分在权重由等权改为媒体权威加权。它度量"权威媒体在金融科技专属语境下"对银行的语气, 是"最严判定域 × 机构权威加权"的组合。ss 轨回退语义镜像 ctx: 无同句共现回退全文正文并置 ss_is_fallback、共享 n_articles 分母、优雅降级。开发 T=2 易退化, 生产 T=18 恢复。行宇宙为 full 留篇集。铁律: 三轨与四加权各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。方法学锚同 You et al. (2018) 权威分层与 Marchetti et al. (2025) 银行年语气聚合。数值上本列落于 [-1,+1], 分母为 ss 轨媒体权威权重之和, 与报道篇数无关。作为家族里判定域最严且加权维度取媒体机构权威的角落组合, 本列度量"权威媒体在金融科技专属语境下对该银行的语气", 是最贴近"有分量的笔如何评价该银行金融科技活动"这一构念的列; 它与 vw_ss、hw_ss 在同一 ss 判定域上以三种不同加权维度并排, 各自 just-identified、互为稳健性。开发 T=2 上"同句共现 × 权威权重非零"双重稀疏使本列退化最甚, 常近零方差或缺失, 生产 T=18 语料上恢复正常, 解读时不应以开发样本的退化值下结论。铁律: 严禁三轨与四加权任意组合混进同一 over-identified Hansen J。

## VAR: you_2018_tone_hw_full

【变体差分】
本列在 full 轨上把等权聚合替换为羊群衰减加权(hw = herd weighting)。聚合公式为 Σ(weight·score)/Σ(weight), 权重取自 stage 24 herd_decay_processor 产出的 herd_weight_full, 分母为 sum_herd_weight_full。构念动机是: 同一事件常被多家媒体近乎同质地转载跟风, 简单等权会让"一稿多发"的重复语气被过度计入, 羊群衰减权重对高度同质、扎堆出现的报道给予折减, 使银行年语气更接近"独立信息含量加权"而非"发文条数加权"。相对 canonical(等权)本列压低跟风报道的贡献。相对 _vw(显著度)与 _mw(媒体权威)本列的加权维度是报道之间的信息冗余度, 而非单篇显著度或媒体机构权威度, 三者正交。hw 加权按三轨独立取分母(full/ctx/ss 各自 sum_herd_weight), 本列取 full 轨分母。行宇宙为 full 留篇集。铁律: 四加权方案各自 just-identified 并排、互为稳健性、不分主次, 严禁四臂混进同一 over-identified Hansen J。权重实现细节: 羊群衰减权重来自 stage 24 herd_decay_processor, 依据报道在时间与内容上的扎堆程度对同质转载给予指数式折减, 使一个事件被十家近乎同质转载时的语气不至于被重复计入十次。相对 _vw(报道显著度)与 _mw(媒体权威)本列的加权维度是报道之间的信息冗余度, 三者两两正交, 分别回答"这篇放得多显要""哪家媒体在说""这篇是独立信息还是跟风重复"。本列在稳健性附录里承担"语气结论是否被一稿多发的跟风报道人为放大"的验证; 若折减跟风后语气水平大幅移动, 说明原等权聚合被同质转载主导, 这本身即是重要的信息环境事实。分母为 full 轨 sum_herd_weight_full。

## VAR: you_2018_tone_hw_ctx

【变体差分】
本列 = 羊群衰减加权 × ctx 轨, 相对 you_2018_tone_hw_full 差分在文本域(实体上下文窗而非全文), 相对 you_2018_tone_ctx 差分在聚合权重(羊群衰减加权而非等权)。hw 加权按三轨独立取分母, 本列取 ctx 轨的 sum_herd_weight_ctx。它交叉验证语气归因既不被判定域宽窄驱动, 也不被报道同质化冗余度驱动——把跟风稿折减后, 实体窗口语气是否仍稳健。行宇宙为 full 留篇集, 本列在其上做 conditional-on-full 的羊群衰减加权聚合。铁律: 三轨与四加权各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 轨与 hw 加权组合混进同一 over-identified Hansen J。词表与规则同家族, 仅权重来源(stage 24 herd_weight)与文本域组合区别。数值上本列落于 [-1,+1], 分母为 ctx 轨羊群衰减权重之和 sum_herd_weight_ctx, 按三轨独立取分母而绝不借用 full 轨分母。本列是"判定域收窄到实体窗"与"信息冗余度折减"两个正交维度的交叉臂, 检验语气归因既不被判定域宽窄也不被同质转载冗余驱动。当本列与 hw_full 方向一致时说明折减跟风后的语气结论稳健于判定域收窄; 当二者分歧时定位出跟风报道在全文与实体窗里语气归因不一致的样本。开发 T=2 上 herd_weight 因时间跨度短(仅两年)难以充分刻画扎堆衰减, 权重接近等权, 本列与 ctx 等权列数值相近属预期, 生产 T=18 语料上衰减结构显现后二者拉开差距。

## VAR: you_2018_tone_hw_ss

【变体差分】
本列 = 羊群衰减加权 × ss 轨。相对 you_2018_tone_hw_full 差分在文本域收窄到银行与金融科技同句共现窗, 相对 you_2018_tone_ss 差分在权重由等权改为羊群衰减加权。它度量"折减跟风冗余后、金融科技专属语境下"的银行年语气, 是"最严判定域 × 信息冗余度加权"的组合。hw 分母按三轨独立, 本列取 ss 轨 sum_herd_weight_ss, 而 ss 分母可能因 stage 24 未跑同句轨而缺失, 由 hw_denom_by_track 兜底。ss 轨回退语义镜像 ctx: 无同句共现回退全文正文并置 ss_is_fallback、共享 n_articles 分母、优雅降级。开发 T=2 易退化, 生产 T=18 恢复。行宇宙为 full 留篇集。铁律: 三轨与四加权各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。数值上本列落于 [-1,+1], 分母为 ss 轨羊群衰减权重之和; 当 stage 24 未跑同句轨导致 sum_herd_weight_ss 缺失时, 由 hw_denom_by_track 兜底避免除零崩溃。作为家族里判定域最严且加权维度取信息冗余度的角落组合, 本列度量"折减跟风冗余后、金融科技专属语境下"的银行年语气, 与 vw_ss、mw_ss 在同一 ss 判定域上以三种加权维度并排, 各自 just-identified、互为稳健性。开发 T=2 上"同句共现稀疏 × herd 衰减未充分刻画"双重退化使本列信息量最低, 生产 T=18 恢复, 解读须以生产语料为准。

## VAR: you_2018_tone_std_full

【变体差分】
本列在 full 轨上把聚合算子由均值改为银行年组内文章 you_2018_score_full 的样本标准差(std)。它度量的不是语气水平(一阶矩)而是语气分歧/离散(二阶矩): 同一银行同一年被媒体报道的金融科技语气是高度一致还是众说纷纭。构念上高 _std 意味着叙事分裂、市场对该银行金融科技活动缺乏共识, 可用于刻画信息环境的不确定性或分歧度, 这与本项目把 tone_std 用作"高覆盖 + 高波动 = 高叙事暴露"的金融科技暴露度构造(fintech_exposure = ln_coverage × tone_std)相衔接。相对 canonical you_2018_tone_full(水平)本列构念正交, 二者可同时进入模型而不冗余。相对 _vw / _mw / _hw(仍是加权水平)本列是唯一的离散度量, 不涉加权分母。计算上需组内至少两篇文章方有定义, 单篇或零篇的银行年该列为 NaN——开发 T=2 样本上大量银行年因组内篇数不足而缺失, 生产 T=18 恢复。行宇宙为 full 留篇集。铁律: 水平各轨与离散度量各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。数值解读上本列非负(标准差), 取值随组内语气分数的分散程度增大而增大, 无上界意义上的固定标度, 跨银行年比较时应关注相对高低而非绝对水平。计算口径为样本标准差(ddof=1), 需组内至少两篇有效文章方有定义, 单篇或零篇的银行年该列为 NaN。本列直接服务于金融科技叙事暴露度构造 fintech_exposure = ln_coverage × tone_std——高覆盖叠加高语气波动被解读为高叙事暴露, 因为此时该银行金融科技活动既被密集报道又引发语气分歧, 信息环境的不确定性最高。

## VAR: you_2018_tone_std_ctx

【变体差分】
本列 = 语气离散度(std)× ctx 轨, 相对 you_2018_tone_std_full 差分在文本域(实体上下文窗而非全文), 相对 you_2018_tone_ctx 差分在聚合算子(组内标准差而非均值)。它度量在实体上下文窗判定域下的银行年语气分歧程度。构念动机与 _std_full 一致(叙事分歧/信息不确定性), 但判定域收窄到目标银行语境, 排除窗外话题对语气方差的干扰, 从而更精确地刻画"针对该银行"的语气分歧。计算上需组内至少两篇有效文章方有定义。行宇宙为 full 留篇集, 本列在其上做 conditional-on-full 的组内离散度量。开发 T=2 上因样本稀疏易缺失, 生产 T=18 恢复。铁律: 三轨与水平/离散算子各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 轨语气方差与其余臂混进同一 over-identified Hansen J。词表与规则口径同家族, 仅"实体窗判定域 × 组内标准差"组合区别于其余列。数值上本列非负, 度量的是实体上下文窗判定域下银行年语气的组内分散程度: 相对 std_full, 本列排除了全文里窗外话题对语气方差的贡献, 因此更精确地刻画"针对该银行"的语气分歧, 而非泛银行报道的语气分歧。二者方向一致说明分歧结论稳健于判定域收窄, 分歧则揭示窗外话题是语气方差的重要来源。开发 T=2 上组内篇数常不足两篇, 本列大量缺失, 生产 T=18 恢复。铁律: 三轨与水平/离散算子各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 轨语气方差与其余臂混进同一 over-identified Hansen J。

## VAR: you_2018_tone_std_ss

【变体差分】
本列 = 语气离散度(std)× ss 轨(same-sentence)。相对 you_2018_tone_std_full 差分在文本域收窄到银行与金融科技同句共现窗, 相对 you_2018_tone_ss 差分在算子由均值改为组内标准差。它度量"金融科技专属语境下"银行年语气的分歧程度, 是三轨中最严判定域与离散算子的组合。ss 轨回退语义镜像 ctx: 无同句共现回退全文正文并置 ss_is_fallback、共享 n_articles 分母、优雅降级。因需组内至少两篇有效文章方有定义, 而 ss 轨同句共现本就稀疏, 本列在开发 T=2 上退化最甚(常近零方差或全 NaN), 生产 T=18 恢复。行宇宙为 full 留篇集。铁律: 三轨与水平/离散算子各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。词表与规则同家族。数值上本列非负, 度量金融科技专属语境下银行年语气的组内分散程度, 是三轨离散度量里判定域最严的一列。因需同时满足"同句共现"且"组内至少两篇有效文章", 本列在开发 T=2 上退化最甚, 常近零方差或全 NaN, 生产 T=18 语料上恢复, 解读时切不可把开发样本的退化常数误读为"语气高度一致"。当本列与 std_full、std_ctx 三轨方向一致时说明语气分歧结论稳健于判定域逐级收窄, 分歧则定位出金融科技专属语境与泛银行语境分歧度不一致的边际银行年。ss 轨回退语义镜像 ctx: 无同句共现回退全文正文并置 ss_is_fallback、共享 n_articles 分母、优雅降级不清空。

## VAR: you_2018_tone_tech_full

【变体差分】
本列在 full 轨上把聚合域限定为创新落点(innovation_locus_full)== "底层技术"的文章子集, 在该子集上取等权语气均值。它不是新的加权方案, 而是按金融科技创新的构念分野切分后条件均值——只统计涉及底层技术设施(如支付清算底层、区块链、云计算、数据基础设施)创新的报道语气。构念动机来自 Gomber et al. (2018) 对金融科技创新的两分: 底层技术创新与应用场景创新在商业逻辑、监管敏感度、市场反应上不同, 因此对二者分别度量语气能揭示"是哪一类金融科技活动"驱动了银行年语气。相对 canonical you_2018_tone_full(全部留篇文章)本列是其"底层技术"条件子样本, 分母为 n_articles_tech。相对 _app 子集本列是互补的另一半落点。相对 _vw / _mw / _hw / _std 本列的差分维度是文章子集划分而非加权或算子。开发 T=2 上若该银行年无底层技术类报道则子集为空、本列缺失。行宇宙为 full 留篇集。铁律: 落点子集与其余加权/轨道臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。数值上本列落于 [-1,+1], 分母为该银行年落点判为底层技术的文章数 n_articles_tech, 与报道篇数无关。落点判据 innovation_locus_full 统一取自 full 轨的创新落点判定, 以保证同一篇文章在 tech/app/全样本三种聚合域里落点归属一致, 不因语气取轨不同而漂移。本列与 _app_full 覆盖互补落点半区, 二者之和一般不等于全样本 canonical——因存在落点未判定或不属底层技术/应用场景二分类的文章, 这部分文章进入 canonical 但不进入任一子集。本列在稳健性附录里承担"是否底层技术类金融科技活动驱动了银行年语气"的机制拆解职责, 构念分野依据 Gomber et al. (2018)。

## VAR: you_2018_tone_tech_ctx

【变体差分】
本列 = "底层技术"落点子集 × ctx 轨, 相对 you_2018_tone_tech_full 差分在文本域(实体上下文窗而非全文), 相对 you_2018_tone_ctx 差分在聚合域(仅底层技术类文章而非全部留篇)。子集划分仍按 innovation_locus_full == "底层技术"(落点判据取自 full 轨的创新落点判定), 但语气分数取 ctx 轨。它度量在实体上下文窗判定域下、涉底层技术创新报道的银行年语气, 交叉验证"底层技术语气"结论既不被判定域驱动也不被全文噪声驱动。分母为 n_articles_tech。行宇宙为 full 留篇集, 本列在其上做 conditional-on-full 的子集条件均值。铁律: 三轨与落点子集各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 轨与 tech 子集组合混进同一 over-identified Hansen J。构念分野依据 Gomber et al. (2018), 词表与规则同家族。数值上本列落于 [-1,+1], 分母同为 n_articles_tech(落点判据取 full 轨), 语气分数取 ctx 轨。本列是"底层技术落点子集"与"实体窗判定域"两个正交维度的交叉臂, 检验"底层技术语气"结论既不被落点外报道也不被全文噪声驱动。当本列与 tech_full 方向一致时说明底层技术语气稳健于判定域收窄; 分歧则揭示全文里非目标银行段落对底层技术语气归因的干扰。开发 T=2 上若某银行年无底层技术类报道则子集为空、本列缺失, 生产 T=18 语料上覆盖改善。铁律: 三轨与落点子集各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 轨与 tech 子集组合混进同一 over-identified Hansen J。

## VAR: you_2018_tone_tech_ss

【变体差分】
本列 = "底层技术"落点子集 × ss 轨(same-sentence)。相对 you_2018_tone_tech_full 差分在文本域收窄到银行与金融科技同句共现窗, 相对 you_2018_tone_ss 差分在聚合域仅限底层技术类文章。它度量"金融科技底层技术专属语境下"的银行年语气, 是"最严判定域 × 底层技术落点"的组合。子集划分按 innovation_locus_full == "底层技术", 语气取 ss 轨。ss 轨回退语义镜像 ctx: 无同句共现回退全文正文并置 ss_is_fallback、共享 n_articles 分母、优雅降级。因需同时满足"底层技术落点"且"同句共现", 双重稀疏使本列在开发 T=2 上退化最甚, 生产 T=18 恢复。行宇宙为 full 留篇集。铁律: 三轨与落点子集各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。数值上本列落于 [-1,+1], 分母同为 n_articles_tech(落点判据取 full 轨), 语气分数取 ss 轨。作为"底层技术落点 × 最严同句判定域"的角落组合, 本列度量金融科技底层技术专属语境下的银行年语气, 因需同时满足"底层技术落点"且"同句共现"双重条件, 在开发 T=2 上退化最甚, 生产 T=18 恢复。ss 轨回退语义镜像 ctx: 无同句共现回退全文正文并置 ss_is_fallback、共享 n_articles 分母、优雅降级不清空。与 app_ss 互补覆盖两落点半区, 与 clarity 家族(确定性/模糊性词表)构念正交, 后者度量叙事确定程度而非情感极性。

## VAR: you_2018_tone_app_full

【变体差分】
本列在 full 轨上把聚合域限定为创新落点(innovation_locus_full)== "应用场景"的文章子集, 在该子集上取等权语气均值, 是 _tech 子集的互补另一半。它只统计涉及金融科技应用场景(如面向 C 端/B 端的信贷、理财、保险、支付应用等落地场景)创新的报道语气。构念动机同样来自 Gomber et al. (2018) 的创新两分: 应用场景创新更贴近终端市场与用户体验, 其语气可能与底层技术创新语气系统不同。相对 canonical you_2018_tone_full(全部留篇)本列是其"应用场景"条件子样本, 分母为 n_articles_app。相对 _tech 子集本列覆盖互补的落点半区; 两子集之和一般不等于全样本, 因存在落点未判定或非二分类的文章。相对 _vw / _mw / _hw / _std 本列的差分维度是文章子集划分而非加权或算子。开发 T=2 上若该银行年无应用场景类报道则本列缺失。行宇宙为 full 留篇集。铁律: 落点子集与其余加权/轨道臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。数值上本列落于 [-1,+1], 分母为该银行年落点判为应用场景的文章数 n_articles_app, 与报道篇数无关。落点判据 innovation_locus_full 统一取自 full 轨以保证跨聚合域落点归属一致。本列与 _tech_full 覆盖互补落点半区, 二者之和一般不等于全样本 canonical, 因存在落点未判定或非二分类的文章只进 canonical 不进任一子集。构念上应用场景创新更贴近终端市场与用户体验, 其语气可能与偏基础设施、偏监管敏感的底层技术创新语气系统不同, 因此 tech 与 app 两列并排能揭示"是哪一类金融科技活动"驱动银行年语气, 构念分野依据 Gomber et al. (2018)。本列在稳健性附录里承担应用场景侧的机制拆解职责。

## VAR: you_2018_tone_app_ctx

【变体差分】
本列 = "应用场景"落点子集 × ctx 轨, 相对 you_2018_tone_app_full 差分在文本域(实体上下文窗而非全文), 相对 you_2018_tone_ctx 差分在聚合域(仅应用场景类文章而非全部留篇)。子集划分按 innovation_locus_full == "应用场景"(落点判据取自 full 轨), 语气分数取 ctx 轨。它度量在实体上下文窗判定域下、涉应用场景创新报道的银行年语气, 交叉验证"应用场景语气"结论既不被判定域驱动也不被全文噪声驱动。分母为 n_articles_app。行宇宙为 full 留篇集, 本列在其上做 conditional-on-full 的子集条件均值。铁律: 三轨与落点子集各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 轨与 app 子集组合混进同一 over-identified Hansen J。构念分野依据 Gomber et al. (2018), 词表与语言学规则口径同家族其余列。数值上本列落于 [-1,+1], 分母同为 n_articles_app(落点判据取 full 轨), 语气分数取 ctx 轨。本列是"应用场景落点子集"与"实体窗判定域"两个正交维度的交叉臂, 检验"应用场景语气"结论既不被落点外报道也不被全文噪声驱动。当本列与 app_full 方向一致时说明应用场景语气稳健于判定域收窄; 分歧则揭示全文里非目标银行段落对应用场景语气归因的干扰。开发 T=2 上若某银行年无应用场景类报道则子集为空、本列缺失, 生产 T=18 覆盖改善。铁律: 三轨与落点子集各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 轨与 app 子集组合混进同一 over-identified Hansen J。

## VAR: you_2018_tone_app_ss

【变体差分】
本列 = "应用场景"落点子集 × ss 轨(same-sentence)。相对 you_2018_tone_app_full 差分在文本域收窄到银行与金融科技同句共现窗, 相对 you_2018_tone_ss 差分在聚合域仅限应用场景类文章。它度量"金融科技应用场景专属语境下"的银行年语气, 是"最严判定域 × 应用场景落点"的组合。子集划分按 innovation_locus_full == "应用场景", 语气取 ss 轨。ss 轨回退语义镜像 ctx: 无同句共现回退全文正文并置 ss_is_fallback、共享 n_articles 分母、优雅降级。因需同时满足"应用场景落点"且"同句共现", 双重稀疏使本列在开发 T=2 上退化甚, 生产 T=18 恢复。行宇宙为 full 留篇集。铁律: 三轨与落点子集各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。与 _tech_ss 互补, 与 clarity 家族构念正交。数值上本列落于 [-1,+1], 分母同为 n_articles_app(落点判据取 full 轨), 语气分数取 ss 轨。作为"应用场景落点 × 最严同句判定域"的角落组合, 本列度量金融科技应用场景专属语境下的银行年语气, 因需同时满足"应用场景落点"且"同句共现"双重条件, 在开发 T=2 上退化甚, 生产 T=18 恢复, 解读须以生产语料为准而非以开发样本退化值下结论。ss 轨回退语义镜像 ctx: 无同句共现回退全文正文并置 ss_is_fallback、共享 n_articles 分母、优雅降级不清空。clarity 家族源自 You et al. (2018) Panel C/D 的确定性/模糊性词表, 度量叙事确定程度而非情感极性, 与本列共用命名锚但构念正交、不可混用。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K. (2020). Econometrics meets sentiment: An overview of methodology and applications. Journal of Economic Surveys, 34(3), 512-547. https://doi.org/10.1111/joes.12370
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
<!-- rendered-citations:end -->
