---
family_id: F366
columns:
- llm_models_avg_cont_app_ctx
- llm_models_avg_cont_app_full
- llm_models_avg_cont_app_ss
- llm_models_avg_cont_ctx
- llm_models_avg_cont_ctx_z
- llm_models_avg_cont_full
- llm_models_avg_cont_full_z
- llm_models_avg_cont_ss
- llm_models_avg_cont_ss_z
- llm_models_avg_cont_tech_ctx
- llm_models_avg_cont_tech_full
- llm_models_avg_cont_tech_ss
unit: 无量纲连续情感分 (值域 [-1, +1]; _z 变体为年度截面标准化后的标准差单位)
formula: "llm_models_avg_cont{track} = mean_{s∈LLM_MODELS}( {s}_cont_mean{track} ); 其中 {s}_cont_mean{track} = 银行-年内对逐篇 {s}_cont{track} 取均值, {s}_cont ∈ [-1,+1] = g(三分类标签, sentiment_confidence) 依 Törnberg (2023) 置信加权映射; LLM_MODELS = {gpt54nano, gemini31, deepseekv4}"
producer: pipeline\panel\geography.py (步骤 7 综合指标; 逐模型 _cont_mean 聚合在 pipeline\panel\encode.py::build_aggregation_dict)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet ({s}_cont{track} 逐篇置信加权连续分 + 三分类标签 + locus tech/app 分类列)
- 40_panel_yearly.parquet (encode 聚合出的 {s}_cont_mean{track} 逐模型银行-年均值)
citations:
- doi: 10.1146/annurev-economics-120925-105620
  type: journal
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2026
  title: "Large language models: An applied econometric framework"
  venue: Annual Review of Economics
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: "Majority rules: LLM ensemble is a winning approach for content categorization"
  venue: arXiv
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1016/j.pacfin.2024.102632
  type: journal
  authors: Chiu, I.-C., & Hung, M.-W.
  year: 2025
  title: "Finance-specific large language models: Advancing sentiment analysis and return prediction with LLaMA 2"
  venue: Pacific-Basin Finance Journal
  vol: 90
  pages_or_artno: 102632
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: 105227
- doi: 10.52202/075280-3000
  type: journal
  authors: Egami, N., Hinck, M., Stewart, B., & Wei, H.
  year: 2023
  title: "Using imperfect surrogates for downstream inference: Design-based supervised learning for social science applications of large language models"
  venue: Advances in Neural Information Processing Systems 36
  pages_or_artno: 68589-68601
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1016/j.mlwa.2023.100508
  type: journal
  authors: Fatouros, G., Soldatos, J., Kouroumali, K., Makridis, G., & Kyriazis, D.
  year: 2023
  title: "Transforming sentiment analysis in the financial domain with ChatGPT"
  venue: Machine Learning with Applications
  vol: 14
  pages_or_artno: 100508
- doi: 10.2139/ssrn.4412788
  type: wp
  authors: Lopez-Lira, A., & Tang, Y.
  year: 2023
  title: "Can ChatGPT forecast stock price movements? Return predictability and large language models"
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
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the FinTech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
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
本家族刻画的是「同一批银行报道, 交由三家异构大语言模型独立打分, 再把三家的连续情感读数横向取算术平均」所得到的跨厂商 ensemble 连续情感测度。它的落点是 canonical 列 llm_models_avg_cont_full, 值域理论上限定在负一到正一之间, 越接近正一表示银行在金融科技语境下被媒体叙述得越正面, 越接近负一越负面, 零附近为中性或多空相抵。这里的核心词是「连续」(cont, continuous): 与本项目主线的离散投票语气 llm_vote_tone 不同, 连续分并非把三分类标签直接算术化, 而是先在单篇层面把「三分类标签乘以模型自报的情感置信度 sentiment_confidence」映射为一条落在负一到正一区间的实数刻度, 使得「高置信度的正面」与「低置信度的正面」不再被压成同一个加号, 从而保留了语气强度这一维信息。逐篇连续分记为某模型的 cont 列, 银行-年内先在单模型内部对全部留篇取均值得到该模型的 cont_mean, 再由本家族把三家的 cont_mean 横向平均, 得到不依赖任一单一厂商的综合连续情感。这一逐篇「标签乘置信度到区间分」的映射思路承袭 Törnberg (2023) 对大模型口头置信度转连续指标的做法, 也呼应了金融文本计量长期强调「情感不只有方向、还有强度」的传统。为什么值得单列一条连续测度而非只保留离散投票? 因为在银行金科这一政策敏感、表述克制的中文媒体语域里, 大量报道并非非黑即白, 而是「谨慎乐观」「有所保留」这类中间态; 离散三分类会把这些中间态强行归入正、中、负三格, 抹平强度信息, 而连续分借置信度把「弱正面」与「强正面」区分开来, 使得同为正面基调的两个银行-年不再等同。对以情感为处理变量的实证而言, 这一强度维往往正是识别所需的横截面变异来源。用大白话说: 离散投票回答「这篇是好话还是坏话」, 连续分进一步回答「好到什么程度、模型有多确信」, 本家族则把三个不同来路的大模型对后一问的回答做了一次公平的平均。

数据来源沿三段链路成形。第一段是文本轨的物化: stage 14 ctx_materializer 把标题 prepend 进正文后, 分别产出 content_full (标题加全文正文)、content_ctx (标题加银行实体窗口)、content_ss (标题加银行与金科同句共现窗口) 三条平行文本列, 让下游同一套打分逻辑能在三种输入粒度上各跑一遍。第二段是 stage 21 tone_llms 的逐篇打分: 三家大模型 gpt54nano、gemini31、deepseekv4 各自对每条文本轨输出三分类标签、情感置信度以及由二者合成的连续分 cont; 三家里 gpt54nano 与 gemini31 经 yunwu 网关调用, deepseekv4 直连 api.deepseek.com, 三家同为一等打分器、互不主从。第三段是面板聚合与综合: encode.build_aggregation_dict 在银行-年层把每家的逐篇 cont 聚成 cont_mean (mean 聚合) 与 cont_sum (sum 聚合); geography.py 步骤 7 再以 _safe_mean 把三家的 cont_mean 横向平均, 落成 llm_models_avg_cont 家族。_safe_mean 的语义是「只对当前存在的源列取行均值, 全缺则整列返回缺失」, 因此当某家某轨的源列尚未落盘 (例如 ss 轨在开发样本上未跑满) 时, 本家族不会崩、而是优雅降级为可用子集的均值或缺失, 这与三轨互为稳健、缺轨不连坐的工程纪律一致。

【方法学与计算】
计算可分三层复述。最内层是逐篇连续分: 对文本轨 track 与模型 s, 该模型给出三分类标签与 sentiment_confidence, 二者按 Törnberg (2023) 的置信加权规则合成为一条落在负一到正一的实数 cont。这一步的关键设计约束是「离散与连续同子集」: 连续因变量与离散因变量必须建立在同一批观测上, 当整篇被多数模型判为非金融科技报道时, 离散主 DV 与连续 DV 同步缺失, 不让少数模型的判定单方面泄入面板; 极罕见的「已验证却零可解析票」态下会出现离散置中性、连续置缺失的轻微不同子集, 属诚实置缺、可接受。这一「同子集」纪律不是可有可无的实现细节, 而是保证连续综合分与离散综合分能被并排解读为「同一批银行报道的两种标度」的前提: 若二者观测集不同, 则它们的差异会被观测选择混入, 无法归因于标度差异, 稳健性对照将失效。逐篇连续分落在负一到正一的对称区间, 也使得银行-年均值天然可读作「净情感强度」, 零点对应多空相抵或普遍中性, 与词典法的归一化语气分、BERT 的正负概率差在量纲直觉上互通, 便于三支度量在同一图表上并列。中间层是单模型银行-年聚合: 对每家 s, cont_mean 是银行-年内对全部逐篇 cont 取算术均值, 分母口径与留篇门控一致 (留篇是否成立由 full-only 口径裁定, 见下)。最外层即本家族的横向综合: llm_models_avg_cont 对三家的 cont_mean 取等权算术平均, 不做厂商加权、不做置信再加权, 保证「三家一票、地位对等」。派生的 _z 变体在此之上叠一层年度截面标准化 (Fama 与 MacBeth 一九七三年提出的按年做横截面标准化范式), 即在每个年度内对该连续综合列做去均值除以年内标准差, 使不同年度、不同量纲基线的读数可比, 便于回归中直接读系数的标准差弹性。派生的 _app 与 _tech 变体则在打分之外叠一层「locus 分类条件化」: 只对被判为「应用场景」(app) 或「底层技术」(tech) 的报道子集聚合并综合, 用来分辨媒体对金融科技「用在哪」与「底层是什么」两类叙事的情感差异, 这一 tech 与 app 的二分承 Gomber 等 (2018) 对金融科技创新的技术层与应用层划分。

留篇门控采用 full-only 口径 (二零二六年六月二十九日确立): 一篇报道是否被计入「银行金科报道」全宇宙, 只看其 full 轨是否通过验证, ctx 与 ss 轨降为「以 full 留篇为条件」的测度轨与稳健轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的连续分仍按各自轨的逐篇读数照算。因此 full 轨的 llm_models_avg_cont_full 是留篇宇宙的一等定义列, ctx 与 ss 轨是条件其上的稳健性刻画。ss 轨的回退语义镜像 ctx: 当某银行某年在同句层无银行与金科的共现时, 相应文本轨回退到全文, 使 ss 轨在共现稀疏时不至整片缺失。这三条文本轨、以及三家模型, 在方法学上一律「各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同轨或不同厂商的 cont 混进同一个 over-identified 的 Hansen J 过度识别检验」——这是本仓贯穿三轨、co-primary 双轨嵌入、各类梯子与 per-model 族的统一识别纪律。

须再强调三家厂商的对等性。gpt54nano、gemini31、deepseekv4 分属不同预训练语料、不同对齐策略与不同提示敏感性的三条技术路线, 把它们的连续读数等权平均, 目的正是稀释任一单一厂商的系统性偏置——某家可能对政策性正面表述过度乐观、某家可能对风险词过度警觉, 等权集成在一阶意义上互相抵消这些方向性偏置, 得到比任一单家更稳的构念读数。这与仅换一个模型「重跑一遍」有本质区别: 集成不是复制, 而是把三份带独立噪声的读数做方差缩减。也正因如此, 三家的 per-vendor 子测度 (各自的 cont_mean) 被保留为可单独调用的稳健轨, 而非在集成后丢弃; 当论文需要展示「主结论不依赖某一特定厂商」时, 可把三家子测度分别代入同一回归, 观察系数符号与显著性是否一致, 这正是 per-model 稳健性梯的用法, 与把三家塞进一条过度识别方程截然不同。

【文献定位】
本家族坐落在「以大模型做金融文本情感、并以连续刻度承载强度」这一近年迅速成形的方法学脉络上。用大模型替代或补充人工与词典标注, 已有较系统的证据: Gilardi、Alizadeh 与 Kubli (2023) 在通用文本标注任务上证明大模型可超过众包工人的一致性与准确度, Fatouros 等 (2023) 与 Lopez-Lira 与 Tang (2023) 分别在金融领域情感分析与股价方向预测上展示了大模型读数的信息含量, Kirtac 与 Germano (2024) 进一步把大模型情感直接接入交易信号, Chiu 与 Hung (2025) 则以金融专用大模型改进情感与收益预测, Lan 等 (2025) 面向中文金融文本给出细粒度实体级情感的大模型方案, 与本项目的中文银行金科语料高度同构。把这些单模型读数横向集成为 ensemble, 有其独立方法学依据: Chen 等 (2025) 系统综述了多大模型集成的收益与设计空间, Kamen 与 Kamen (2025) 论证了多模型「多数规则」式集成在内容归类上的稳健优势; 本家族取三家等权平均正是这一集成思想在「连续读数」上的落地, 用以稀释任一单一厂商的系统性偏置与提示敏感性。方法学的审慎面由两支文献锚定: Ludwig、Mullainathan 与 Rambachan (2026) 的应用计量框架, 以及 Egami 等 (2023) 关于「以不完美代理做下游推断」的设计化监督学习, 共同提醒把大模型读数当作生成的回归变量时须正视测量误差与偏置传导——这正是本项目坚持三家并排、三轨并排而非单点采信、并把跨模型一致性单列检验的原因。回到金融文本计量的母题, 本家族与词典法、监督式机器学习互为并行度量: Loughran 与 McDonald (2016) 综述了会计金融文本分析的谱系, Frankel、Jennings 与 Lee (2022) 直接比较了机器学习与词典法在披露情感上的分歧, Tetlock (2007) 则奠定了「媒体情感对市场有实质影响」的经验基石; 本家族的连续综合分, 意在为这一谱系补上一条不依赖固定词表、且保留强度维度的大模型连续测度。相较词典法固定词表在跨语域迁移时的失配 (中文金融文本尤甚, 故本项目另配 Du 等 (2022) 的中文金融情感词典作词典臂), 大模型读数以少样本乃至零样本的语境理解见长, 对反讽、否定嵌套、程度修饰等词典法难以捕捉的语言现象更鲁棒; 但其代价是可复现性依赖提示与温度的冻结、以及潜在的训练数据污染与前瞻偏置, 故本项目以冻结提示版本、温度置零、并把逐次读数落缓存的方式锁定确定性。把大模型作情感测量而非直接因果读数, 也呼应了 Frankel 等 (2022) 对机器学习与词典法分歧来源的剖析: 两类方法的差异本身携带信息, 不应简单择一, 而应作为测量稳健性的并行证据。本家族因此不谋求取代词典法或 BERT, 而是与之构成金融文本情感测量的方法三角, 三腿各自 just-identified 并排、禁混同一 over-identified Hansen J。

【识别策略定位】
在识别上, 本家族的核心角色是 P1 主线 (bank_fintech_tone) 情感处理变量的一条并行测量轨, 与离散投票主轨 llm_vote_tone 互为稳健性: 前者保留强度、后者稳健于置信噪声, 二者对同一构念给出可交叉验证的读数。三家模型的 per-vendor 子测度、三条文本轨、以及连续综合与离散综合, 都是「同一构念的替代测量」而非「同一方程的多重工具」: 严禁把 llm_models_avg_cont 的 full/ctx/ss 三轨或三家厂商拼进同一个过度识别的 Hansen J; 跨模型的真正联合检验只走根级的跨模型 FWER 模板 (以 Romano 与 Wolf (2005) 的逐步多重检验控制族错误率), 而非把替代测量塞进一条工具变量方程冒充过度识别。_z 变体的年度截面标准化服务于跨年可比与系数解读, 不改变识别内核。_app 与 _tech 的 locus 条件化则服务于机制辨析 (P4 位置分类), 用「技术层情感减应用层情感」的差距刻画媒体叙事重心, 而非作为独立的外生冲击。需要点明的是, 本家族多为「生成的回归变量」: 大模型读数带测量误差, 直接当作解释变量会把误差传导进系数与标准误。本项目对此的一贯处理不是寄望单点读数无偏, 而是以三家并排稀释厂商偏置、以三轨并排稀释文本切分偏置、以连续对离散并排稀释标度偏置, 并在真正需要跨模型联合推断时走根级的跨模型 FWER 模板, 以 Romano 与 Wolf (2005) 的逐步多重检验在族层控制错误率——这与把多份替代测量塞进一条工具变量方程冒充过度识别是两回事, 后者会因替代测量高度共线而使 Hansen J 失去检验力, 是本仓明令禁止的做法。

【与相邻测度的构念区分】
须与三组相邻列严格区分。其一, 与 llm_models_avg_tone 家族: 后者是三家离散语气标签的横向平均 (方向为主), 本家族是三家连续置信加权分的横向平均 (方向加强度); 二者在极端高置信样本上趋同, 在中低置信样本上系统性分叉, 故不可互相替代、也不可并入同一过度识别式。其二, 与 llm_vote_cont / llm_vote_tone: 投票族是先在单篇层把三家「投票合一」再聚合, 本家族是先各家独立聚合再横向平均, 二者的聚合次序不同 (先投票后平均 对 先平均后综合), 在三家分歧大的银行-年上读数不同, 分别承载「共识口径」与「等权集成口径」两种稳健性。其三, 与 dict_avg_cont 类词典综合或 bert_avg 类 BERT 综合: 那些是另两支度量三角 (词典法、编码器式监督模型) 的横向平均, 与本家族的大模型连续分互为方法三角的三条腿, 各自 just-identified 并排、禁混同一 Hansen J。

【已知局限与稳健性梯子】
局限有三层。第一是置信度映射的模型依赖: sentiment_confidence 的标定在三家厂商间并不天然可比, 等权平均只是一阶稳健化, 未做置信再校准; 因此水平值的跨模型直接比较须谨慎, 回归中优先读标准化后的系数 (故有 _z 轨)。第二是留篇门控与子集依赖: full-only 口径下 ctx/ss 轨为条件测度, 在共现稀疏的银行-年上 ss 轨回退全文, 读数与 full 轨趋同, 其增量信息随语料密度变化, 开发样本 (T=2) 上尤其可能退化, 生产样本 (T=18) 才充分展开。第三是生成回归变量的测量误差传导, 已由三家并排、跨模型 FWER、以及与词典法与 BERT 的方法三角共同缓释。对应的稳健性梯子包括: 三条文本轨 (full/ctx/ss) 互为输入粒度稳健, 三家厂商 (gpt54nano/gemini31/deepseekv4) 互为模型稳健, 连续综合与离散综合互为标度稳健, _app 与 _tech 的 locus 条件化提供机制稳健; 所有梯级一律各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J。

再补一层跨模型一致性的稳健证据链。三家厂商等权平均只是一阶方差缩减, 它并不自证「三家读的是同一构念」; 为此本项目在综合分之外单列跨模型一致性检验 (以名义标度的 Krippendorff α 与两两 Cohen κ 度量三家标签级吻合度), 只有在一致性达可接受水平时, 等权集成才被解读为「稳的构念读数」而非「三份不相干噪声的平均」。这一「先验一致性、后集成读数」的次序, 与把替代测量塞进过度识别方程的做法正相反: 前者用一致性证明可集成、再以集成缩方差, 后者妄图用共线的替代测量撑起过度识别自由度而必然失败。须再次强调, 跨模型的联合统计推断只在根级跨模型 FWER 模板里发生, 以 Romano 与 Wolf (2005) 的逐步多重检验在族层控制错误率, 而非在任一条回归方程内以 Hansen J 冒充; 这正是「各家 just-identified 并排、禁混同一 over-identified Hansen J」纪律在本连续综合族上的具体落地。就生成回归变量的偏置传导而言, Ludwig、Mullainathan 与 Rambachan (2026) 的应用计量框架与 Egami 等 (2023) 的设计化监督学习共同给出了审慎口径: 大模型读数作为不完美代理进入下游推断时, 其测量误差既可能衰减系数、也可能因与处理相关而引入方向性偏置, 故本项目不寄望单点无偏, 而以三家并排、三轨并排、连续对离散并排三重稀释, 并把标准化后的 _z 轨作为跨样本回归的首选读数。

最后就确定性与可复现补一句: 大模型读数天然有随机性隐忧, 本项目以冻结提示版本、温度置零、并把三家逐次读数落地缓存的方式锁定确定性, 使得在缓存全命中时可离线零字节复现同一批 cont, 进而复现本家族的每一列; 缓存未命中才会触发付费在线调用。因此本家族虽以大模型为源, 却与词典法、BERT 一样具备逐位可复现的工程锚, 这也是它能被当作正式面板变量、进入论文主表与稳健性表的前提。综上, 本家族给出的是一条「跨厂商等权集成、保留强度、可复现、且与词典法与 BERT 构成方法三角」的大模型连续情感测度, 其 canonical 落点 llm_models_avg_cont_full 是 P1 主线情感处理变量的连续测量主轨。

## VAR: llm_models_avg_cont_app_ctx

【变体差分】
本列是 canonical llm_models_avg_cont_full 的两维叠加变体: 其一切到 ctx 文本轨 (标题 prepend 加银行实体上下文窗口, 而非全文), 其二叠加 locus 分类条件化, 只对被判为「应用场景」(app) 类的报道子集聚合并做三家横向平均。也就是说, 分母不再是该银行-年的全部留篇, 而是其中 locus 被判为应用场景、且在 ctx 轨上产出有效连续分的那部分报道; 分子是三家模型在该子集上的 cont_mean 的等权算术平均。与 tech 变体互补, 二者相减即得媒体对金融科技「用在哪 (应用)」与「底层是什么 (技术)」两类叙事的情感落差 (Gomber 等 (2018) 的技术层与应用层二分)。ctx 轨在 full-only 门控下为条件测度轨: 其行宇宙是 full 留篇集的子集, per-track 连续读数按 ctx 文本各自照算。本列与 app_full、app_ss 三轨互为稳健性、各自 just-identified 并排, 与 tech 系列以及无 locus 后缀的基列一律不分主次, 严禁把不同轨、不同 locus 或不同厂商的读数混进同一个 over-identified 的 Hansen J 过度识别检验。app 子集在开发样本上篇数稀薄, 该列可能大面积缺失或近零方差, 属 T=2 预期退化, 生产样本方充分展开。实现上本列经 _safe_mean 对三家 app 场景 ctx 轨 cont_mean 取行均值, 某家源列缺席时优雅降级为可用子集均值; 逐篇连续分依 Törnberg (2023) 由标签与置信度合成。相较 app_full, 本列把注意力从全文收敛到银行实体窗口, 在长文多主题的应用场景报道上与 app_full 读数可系统性分叉, 二者互为输入粒度稳健。因 app 与 ctx 双重条件, 分母收窄两次, 水平值的横截面比较须结合篇数辅列谨慎解读。

## VAR: llm_models_avg_cont_app_full

【变体差分】
本列相对 canonical 的差分仅在 locus 一维: 文本轨仍是 full (标题 prepend 加全文正文), 与 canonical 同轨, 但把聚合子集限定为 locus 被判为「应用场景」(app) 的报道。因此它是「应用场景叙事的全文轨连续情感综合」: 银行-年内, 先在每家模型上对应用场景类留篇的逐篇 cont 取均值得 cont_mean, 再对三家 cont_mean 等权横向平均。与 canonical llm_models_avg_cont_full 相比, 分子分母都收窄到应用场景子集, 故读数刻画的是媒体在谈金融科技「应用与场景落地」时的情感基调, 而非全部金科报道的综合情感。它与 tech_full 构成一对方向相反的机制探针 (应用层减技术层即位置情感差距, 服务 P4 locus 机制), 与 app_ctx、app_ss 构成该 locus 下的三文本轨稳健梯。full 轨在 full-only 门控下为留篇宇宙的一等轨。本列与其余轨、其余 locus、其余厂商一律互为稳健性、不分主次, 禁混同一 over-identified Hansen J。应用场景子集篇数在开发样本上偏薄, 缺失或低方差属预期退化。实现上本列经 _safe_mean 对三家 app 场景 full 轨 cont_mean 取行均值, 逐篇连续分依 Törnberg (2023) 由标签与置信度合成, 单模型均值由 encode 层 mean 聚合。因它与 canonical 同为 full 轨、仅在 locus 上收窄, 二者之差恰好隔离出「应用场景叙事相对全部金科叙事的情感偏移」, 是解读媒体是否对金融科技落地场景更宽容或更苛刻的直接抓手; 与 app_ctx、app_ss 并置又构成同一 locus 下的输入粒度稳健梯。

## VAR: llm_models_avg_cont_app_ss

【变体差分】
本列是 app (应用场景) locus 条件化在 ss 文本轨上的落点。ss 轨 = 标题 prepend 加「银行与金科同句共现」窗口, 是三轨里语境最紧的一条, 只截取银行与金融科技词在同一句子里相邻共现的片段作为打分输入。本列因此刻画的是「在银行与金科被同句并置、且该报道被判为应用场景类的语境下, 三家大模型连续情感的等权综合」。ss 轨的回退语义镜像 ctx: 当某银行某年无同句共现时, ss 文本回退到全文正文, 相应读数向 full 轨趋近, 故 ss 轨的增量信息在共现稀疏时收窄。它在 full-only 门控下为条件测度轨, 行宇宙为 full 留篇集之子集, per-track 连续分按 ss 文本各自照算。与 app_full、app_ctx 三轨互为稳健性、各自 just-identified 并排; 与 tech_ss 互为机制对照。所有轨、locus 与厂商一律不分主次, 严禁混进同一 over-identified Hansen J。ss 且 app 双重条件化后子集极薄, 开发样本 (T=2) 上大面积缺失或零方差属预期退化, 生产样本方有意义。计算实现上, 本列由 geography 步骤 7 的 _safe_mean 对三家的 app 场景 ss 轨 cont_mean 取行均值, 某家源列未落盘时优雅降级为可用子集均值而非崩溃; 逐篇连续分仍依 Törnberg (2023) 由三分类标签与置信度合成, 单模型均值由 encode 层 mean 聚合。读数解读时须记住 ss 轨的回退主导会压缩其与 full 轨的差异, 故本列的增量价值集中在同句共现密集、且应用场景叙事丰沛的银行-年上。

## VAR: llm_models_avg_cont_ctx

【变体差分】
本列是 canonical 的纯文本轨切换变体: 不叠 locus 条件, 只把输入文本从 full (全文) 换到 ctx (标题 prepend 加银行实体上下文窗口)。也就是说, 银行-年内对全部 ctx 轨留篇, 三家模型各自算 cont_mean, 再等权横向平均。它与 canonical llm_models_avg_cont_full 度量同一构念 (跨厂商综合连续情感), 差别只在打分所见的文本粒度: ctx 轨把注意力收敛到银行实体附近的语境, 剔除与银行无关的段落噪声, 因此在长文、多主题报道上与 full 轨读数可系统性分叉, 二者互为输入粒度稳健。在 full-only 门控下 ctx 轨为条件测度轨: 是否留篇仍由 full 轨裁定, ctx 轨的行宇宙为 full 留篇集之子集, 但 per-track 连续分按 ctx 文本照算。本列与 full、ss 三轨互为稳健性、各自 just-identified 并排, 严禁把三轨读数混进同一 over-identified 的 Hansen J。派生的 _z 后缀 (ctx_z) 为本列的年度截面标准化版本, app_ctx 与 tech_ctx 为本列叠 locus 条件的机制探针。三家厂商在本轨内亦各自并排、不分主次。实现上本列经 _safe_mean 对三家 ctx 轨 cont_mean 取行均值, 某家源列未落盘时优雅降级; 逐篇连续分依 Törnberg (2023) 由三分类标签与置信度合成, 单模型均值由 encode 层 mean 聚合。ctx 轨的实体窗口设计意在剔除银行无关段落的情感噪声, 因此在报道以银行为配角、主体另有他物的长文上, 它相对 full 轨更贴近「关于该银行本身」的情感, 是 full 轨主读数之外一条语义更聚焦的稳健轨。

## VAR: llm_models_avg_cont_ctx_z

【变体差分】
本列是 llm_models_avg_cont_ctx 的年度截面标准化 (z-score) 版本, 差分只在标准化这一层, 底层构念、文本轨 (ctx)、模型集 (三家)、locus 条件 (无) 全与 ctx 基列一致。标准化按 Fama 与 MacBeth (一九七三) 的横截面范式在每个年度内独立执行: 对给定年份, 取该年内所有银行的 ctx 连续综合读数, 减去年内均值、除以年内标准差, 得到以年内标准差为单位的无量纲得分。其作用是消除不同年度间的整体情感基线漂移与量纲差异, 使跨年可比、并让回归系数可直接读作「银行连续情感每变动一个年内标准差」的弹性。它不改变构念内核, 只做尺度重整, 因此与未标准化的 ctx 基列一一对应、承载相同信息但不同尺度。dtype 为 double 以承标准化后的精度。本列仅是 ctx 轨的尺度稳健化, 与 full_z、ss_z 三轨的标准化列互为稳健性、各自 just-identified 并排, 严禁把三轨的标准化读数混进同一 over-identified 的 Hansen J。年内样本过少时 (如某年仅少数银行) 标准差不稳, 开发样本上 z 值须谨慎解读。之所以为 ctx 轨单列标准化版本而非只标准化 full 轨, 是因为三轨互为稳健性、须在同一尺度基线上并排比较系数; 若只对部分轨标准化, 跨轨系数将不可比。本列因此是 ctx 轨进入回归的推荐形态, 与 full_z、ss_z 共同构成三轨在标准差尺度上的稳健梯, 各轨各自 just-identified 并排、禁混同一 over-identified Hansen J。

## VAR: llm_models_avg_cont_full

【变体差分】
本列是本家族的 canonical 核心列, 也是二零二六年七月十日签核扩围纳入 core 的锚点。它的完整语义是「full 文本轨、不叠 locus 条件、三家大模型连续情感读数的等权横向综合」: 银行-年内, 对每篇 full 轨留篇 (标题 prepend 加全文正文) 由三家模型各自输出置信加权连续分 cont, 每家先在银行-年内对逐篇 cont 取均值得 cont_mean, 再由本列对三家 cont_mean 做等权算术平均, 落成一条值域负一到正一的综合连续情感。它是留篇宇宙的一等定义轨: full-only 门控 (二零二六年六月二十九日) 下, 一篇是否算「银行金科报道」全看其 full 轨是否通过验证, 因此 full 轨的分母即留篇全宇宙, ctx 与 ss 轨则是条件其上的子集测度。本列与离散投票主轨 llm_vote_tone 互为稳健性: 前者保留由 sentiment_confidence 承载的语气强度维、后者稳健于置信噪声, 二者对 P1 主线情感处理变量给出可交叉验证的双读数。

与相邻列的构念区分须点清。相对 llm_models_avg_tone_full (三家离散语气的横向平均), 本列的分子是连续置信加权分而非离散标签, 在中低置信样本上系统性分叉, 二者不可互替、亦不可并入同一过度识别式。相对 llm_vote_cont_full (先在单篇把三家投票合一再聚合的连续分), 本列是先各家独立聚合再横向综合, 聚合次序相反 (先平均后综合 对 先投票后聚合), 在三家分歧大的银行-年上读数不同, 分别承载「等权集成」与「共识」两种口径。相对 dict_avg 与 bert_avg 类综合, 本列是方法三角里「大模型连续分」这条腿, 与词典法、BERT 编码器式监督分互为并行度量。派生 full_z 为本列的年度截面标准化版本, app_full 与 tech_full 为本列叠 locus 条件的机制探针。

方法学上, 逐篇 cont 依 Törnberg (2023) 由三分类标签与置信度合成, 单模型 cont_mean 由 encode 层 mean 聚合, 三家横向平均由 geography 步骤 7 的 _safe_mean 完成——_safe_mean 只对现存源列取行均值, 某家源列未落盘时优雅降级而非崩溃。识别纪律上, 本列的 full/ctx/ss 三轨、三家厂商 (gpt54nano/gemini31/deepseekv4)、连续与离散标度, 都是「同一构念的替代测量」而非「同一方程的多重工具」: 严禁把三轨或三厂商读数拼进同一个 over-identified 的 Hansen J; 跨模型的真正联合检验只走根级跨模型 FWER 模板 (以 Romano 与 Wolf (2005) 逐步多重检验控制族错误率)。已知局限包括置信度标定的跨厂商不可比 (故回归优先读标准化系数)、生成回归变量的测量误差传导 (由三家并排与方法三角缓释)、以及开发样本 T=2 下的稀薄退化 (生产 T=18 方充分)。稳健性梯子由三文本轨、三厂商、连续对离散、locus 条件化四条构成, 各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J。

在数据契约层面还须记两点。其一, 命名口径: 无 locus 后缀、无加权后缀的 llm_models_avg_cont_full 即为等权集成的 canonical, 不带任何隐含加权; 与之并行还有 cont_sum 系列 (三家 cont_sum 的横向平均, 即分子口径, 供加权指标使用), 二者构念不同——本列是均值口径 (强度), cont_sum 是总量口径。其二, 缺列语义: 因 _safe_mean 只对现存源列取行均值, 当某家厂商某年因限流或离线缓存未命中而未产出该轨 cont 时, 本列会以剩余可用厂商的均值填充而非崩溃, 这一优雅降级保证管道稳定, 但也意味着极端情形下本列可能只代表两家甚至一家的读数; 生产运行须核对三家的 cont 源列均已落盘, 以免把降级读数误当满配集成。据此, 本列在论文中作为 P1 情感处理变量的连续测量主轨呈现时, 通常与其标准化版本 full_z 搭配, 并以离散投票主轨 llm_vote_tone 作交叉验证的伴随读数。

就文献坐标而言, 本列所在的「大模型连续情感」方法脉络已有较系统的经验支撑: Gilardi、Alizadeh 与 Kubli (2023) 证明大模型在文本标注上可超越众包一致性, Fatouros 等 (2023) 与 Lopez-Lira 与 Tang (2023) 分别在金融情感与股价方向预测上验证了大模型读数的信息含量, Kirtac 与 Germano (2024) 进一步把大模型情感接入交易信号, Chiu 与 Hung (2025) 以金融专用大模型改进情感与收益预测, Lan 等 (2025) 面向中文金融文本给出实体级细粒度方案 (与本项目中文银行金科语料同构); 把这些单模型读数横向集成的方法学依据则来自 Chen 等 (2025) 对多大模型集成的系统综述与 Kamen 与 Kamen (2025) 对「多数规则」式集成稳健优势的论证。本列取三家等权平均正是这一集成思想在连续读数上的落地。回到金融文本情感测量的谱系, 本列与词典法 (Loughran 与 McDonald (2016) 综述)、监督式机器学习 (Frankel、Jennings 与 Lee (2022) 对机器学习与词典法分歧的剖析) 构成方法三角, 而 Tetlock (2007) 奠定了「媒体情感对市场有实质影响」的经验母题——本列的连续综合分意在为这一谱系补上一条不依赖固定词表、且保留由 sentiment_confidence 承载的强度维的大模型测度。须再次点明识别纪律: 本列与词典综合、BERT 综合三腿各自 just-identified 并排、互为稳健性不分主次, 严禁并入同一 over-identified 的 Hansen J。

## VAR: llm_models_avg_cont_full_z

【变体差分】
本列是核心列 llm_models_avg_cont_full 的年度截面标准化 (z-score) 版本, 差分仅在标准化这一层, 构念、full 文本轨、三家模型集、无 locus 条件均与 full 基列完全一致。标准化按 Fama 与 MacBeth (一九七三) 横截面范式逐年执行: 每个年度内对该年全部银行的 full 连续综合读数去均值、除以年内标准差, 得到以年内标准差为单位的无量纲得分, 消除年度间情感基线漂移, 使跨年可比且回归系数可直读为标准差弹性。因 canonical 列的水平值受置信度标定的跨厂商不可比影响, 本 _z 列在跨年、跨样本回归中往往是更宜直接采信的读数, 是核心列在识别与解读上的首选标准化轨。它不改变构念内核, 只做尺度重整, 与 full 基列一一对应。dtype 为 double 承标准化精度。本列与 ctx_z、ss_z 三轨标准化列互为稳健性、各自 just-identified 并排, 严禁把三轨标准化读数混进同一 over-identified 的 Hansen J。年内银行数过少时标准差不稳 (开发样本尤甚), z 值须谨慎解读。它与 ctx_z、ss_z 三轨标准化列须在同一尺度基线上并排, 才能让跨轨系数可比; 这也是三轨各自单列标准化而非共用一条的原因。实现上标准化在 geography 步骤 7b 的白名单 (_STANDARDIZE_COLS) 内执行, llm_models_avg_cont 基名被显式纳入该白名单, 三轨齐备时逐年去均值除年内标准差。本列因此是核心构念进入 P1 主线回归的推荐形态。

## VAR: llm_models_avg_cont_ss

【变体差分】
本列是 canonical 的纯文本轨切换变体, 不叠 locus 条件, 把输入文本换到 ss 轨——标题 prepend 加「银行与金科同句共现」窗口, 是三轨中语境最紧的一条, 只取银行与金融科技词在同一句子内相邻共现的片段供三家模型打分, 各家算 cont_mean 后等权横向平均。它与 canonical 度量同一构念, 差别在打分所见的文本粒度收到句级共现: 相较 full (全文) 与 ctx (实体窗口), ss 轨最大程度剔除银行与金科无直接语义关联的段落, 读数最贴近「银行确被与金融科技并置谈论时」的情感。ss 轨回退语义镜像 ctx: 无同句共现的银行-年, ss 文本回退全文正文, 读数向 full 趋近, 故其增量信息随共现密度变化。在 full-only 门控下 ss 轨为条件测度轨, 行宇宙为 full 留篇集之子集, per-track 连续分按 ss 文本照算。本列与 full、ctx 三轨互为稳健性、各自 just-identified 并排, 严禁把三轨读数混进同一 over-identified 的 Hansen J。派生 ss_z 为其年度截面标准化版本, app_ss 与 tech_ss 为其叠 locus 条件的机制探针。开发样本上同句共现稀疏, 本列可能大面积回退或低方差, 属预期退化。实现上本列经 _safe_mean 对三家 ss 轨 cont_mean 取行均值, 某家源列未落盘时优雅降级; 逐篇连续分依 Törnberg (2023) 由三分类标签与置信度合成。ss 轨的价值在于它逼近「银行与金融科技被直接并置谈论」这一最狭义语境, 因此当研究关心的是媒体对银行金科关联本身的情感 (而非泛泛的银行报道情感) 时, 本列是三轨里语义指向最精的一条稳健读数。

## VAR: llm_models_avg_cont_ss_z

【变体差分】
本列是 llm_models_avg_cont_ss 的年度截面标准化 (z-score) 版本, 差分只在标准化层, 底层构念、ss 文本轨、三家模型集、无 locus 条件全与 ss 基列一致。标准化按 Fama 与 MacBeth (一九七三) 横截面范式逐年执行: 每个年度内对该年全部银行的 ss 连续综合读数去均值、除以年内标准差, 得到以年内标准差为单位的无量纲得分, 消除年度间基线漂移使跨年可比, 并让回归系数可直读作标准差弹性。它不改构念内核, 只做尺度重整, 与 ss 基列一一对应, dtype 为 double 承标准化精度。因 ss 轨在共现稀疏时向 full 回退, 本 _z 列在开发样本上更易受回退主导而方差压缩, 解读须结合共现密度。本列与 full_z、ctx_z 三轨标准化列互为稳健性、各自 just-identified 并排, 严禁把三轨标准化读数混进同一 over-identified 的 Hansen J。年内银行数过少时标准差不稳, z 值须谨慎。实现上标准化在 geography 步骤 7b 白名单 (_STANDARDIZE_COLS) 内执行, ss 轨的 llm_models_avg_cont 基名被显式纳入, 三轨齐备时逐年去均值除年内标准差, ss 源列缺席时该轨标准化优雅跳过。之所以为 ss 轨单列标准化版本而非只标准化 full 轨, 是因为三轨互为稳健性、须在同一标准差尺度基线上并排比较系数; 只标准化部分轨会使跨轨系数不可比。本列因此是 ss 轨进入 P1 主线回归的推荐形态, 与 full_z、ctx_z 共同构成三轨在标准差尺度上的稳健梯, 解读时须结合同句共现密度与年内有效银行数两个辅助口径, 避免把回退主导的低方差误读为情感趋同。

## VAR: llm_models_avg_cont_tech_ctx

【变体差分】
本列是 canonical 的两维叠加变体: 文本轨切到 ctx (标题 prepend 加银行实体上下文窗口), 并叠加 locus 分类条件化, 只对被判为「底层技术」(tech) 类的报道子集聚合并做三家横向平均。分母是该银行-年内 locus 被判为底层技术、且在 ctx 轨产出有效连续分的报道; 分子是三家模型在该子集上 cont_mean 的等权平均。它刻画的是媒体谈论金融科技「底层技术是什么」(如系统、算法、基础设施) 时的情感基调, 与 app_ctx (应用场景) 构成一对方向相反的机制探针, 二者相减即技术层减应用层的位置情感差距 (承 Gomber 等 (2018) 技术层与应用层二分, 服务 P4 locus 机制)。ctx 轨在 full-only 门控下为条件测度轨, 行宇宙为 full 留篇集之子集, per-track 连续分按 ctx 文本照算。本列与 tech_full、tech_ss 三轨互为稳健性、各自 just-identified 并排, 与 app 系列及无 locus 基列一律不分主次, 严禁把不同轨、不同 locus 或不同厂商读数混进同一 over-identified 的 Hansen J。tech 子集在开发样本上篇数稀薄, 缺失或近零方差属预期退化。实现上本列经 _safe_mean 对三家 tech 底层技术 ctx 轨 cont_mean 取行均值, 某家源列缺席时优雅降级为可用子集均值; 逐篇连续分依 Törnberg (2023) 由标签与置信度合成。相较 tech_full, 本列把打分视野从全文收敛到银行实体窗口, 在以银行为配角的技术类长文上与 tech_full 读数可分叉, 二者互为输入粒度稳健; 因 tech 与 ctx 双重条件, 分母收窄两次, 水平值横截面比较须结合篇数辅列谨慎。

## VAR: llm_models_avg_cont_tech_full

【变体差分】
本列相对 canonical 的差分仅在 locus 一维: 文本轨仍是 full (标题 prepend 加全文正文), 与 canonical 同轨, 但聚合子集限定为 locus 被判为「底层技术」(tech) 的报道。它是「底层技术叙事的全文轨连续情感综合」: 银行-年内先在每家模型上对底层技术类留篇的逐篇 cont 取均值得 cont_mean, 再对三家 cont_mean 等权横向平均。与 canonical llm_models_avg_cont_full 相比, 分子分母都收窄到底层技术子集, 读数刻画媒体在谈金融科技底层技术 (系统、算法、数据基础设施) 时的情感基调, 而非全部金科报道的综合情感。它与 app_full 构成一对方向相反的机制探针 (技术层减应用层即位置情感差距, 服务 P4 locus 机制), 与 tech_ctx、tech_ss 构成该 locus 下的三文本轨稳健梯。full 轨在 full-only 门控下为留篇宇宙的一等轨, tech 条件化后为其子集测度。本列与其余轨、其余 locus、其余厂商一律互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J。底层技术子集篇数在开发样本上偏薄, 缺失或低方差属预期退化, 生产样本方充分展开。实现上本列经 _safe_mean 对三家 tech 底层技术 full 轨 cont_mean 取行均值, 逐篇连续分依 Törnberg (2023) 由标签与置信度合成, 单模型均值由 encode 层 mean 聚合。它与 canonical 同为 full 轨、仅在 locus 上收窄至底层技术, 二者之差恰好隔离出「技术层叙事相对全部金科叙事的情感偏移」; 再与 app_full 相减即得技术层减应用层的位置情感差距, 是 P4 locus 机制辨析里方向最明确的一条探针。

## VAR: llm_models_avg_cont_tech_ss

【变体差分】
本列是 tech (底层技术) locus 条件化在 ss 文本轨上的落点。ss 轨 = 标题 prepend 加「银行与金科同句共现」窗口, 只截取银行与金融科技词同句相邻共现的片段供三家模型打分。本列因此刻画「在银行与金科被同句并置、且该报道被判为底层技术类的语境下, 三家大模型连续情感的等权综合」——语境最紧且机制指向最专的一条: 既锁定同句共现、又锁定底层技术叙事。ss 轨回退语义镜像 ctx: 无同句共现的银行-年, ss 文本回退全文正文, 读数向 full 趋近, 增量信息随共现密度收窄。它在 full-only 门控下为条件测度轨, 行宇宙为 full 留篇集之子集, per-track 连续分按 ss 文本照算。与 tech_full、tech_ctx 三轨互为稳健性、各自 just-identified 并排; 与 app_ss 互为机制对照 (技术层对应用层)。所有轨、locus 与厂商一律不分主次, 严禁混进同一 over-identified 的 Hansen J。ss 且 tech 双重条件化后子集极薄, 开发样本 (T=2) 上大面积缺失或零方差属预期退化, 生产样本方有意义。实现上本列经 _safe_mean 对三家 tech 底层技术 ss 轨 cont_mean 取行均值, 某家源列缺席时优雅降级为可用子集均值; 逐篇连续分依 Törnberg (2023) 由三分类标签与置信度合成, 单模型均值由 encode 层 mean 聚合。由于同时锁定同句共现与底层技术叙事, 本列的分母是三轨与两 locus 的交集里最狭窄的一格, 因此它承载的信息最专、但样本最薄, 宜作为机制稳健性的补充证据而非主读数; 当研究关心「银行与金科底层技术被直接并置谈论时的情感」这一最精语义时, 它是不可替代的一条。

<!-- rendered-citations:begin -->

<!-- rendered-citations:end -->
