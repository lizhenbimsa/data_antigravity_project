---
family_id: F445
columns:
- n_all_articles_j70w10
- n_all_articles_j70w5
- n_all_articles_j75w5
- n_all_articles_j80w10
- n_articles
- n_articles_app
- n_articles_app_lc_ctx
- n_articles_app_ls_ss
- n_articles_cell_1_full
- n_articles_cell_2_full
- n_articles_cell_3_full
- n_articles_cell_4_full
- n_articles_cell_5_full
- n_articles_cell_6_full
- n_articles_cell_7_full
- n_articles_cell_8_full
- n_articles_cell_NA_full
- n_articles_collab
- n_articles_collab_bothvalid
- n_articles_collab_cm_ctx
- n_articles_collab_cm_ss
- n_articles_collab_disagree
- n_articles_collab_freerider
- n_articles_collab_quietworker
- n_articles_exc
- n_articles_for_ctx_independence
- n_articles_for_ss_independence
- n_articles_indep
- n_articles_indep_cm_ctx
- n_articles_indep_cm_ss
- n_articles_locus_bothvalid
- n_articles_locus_disagree
- n_articles_locus_freerider
- n_articles_locus_quietworker
- n_articles_sub
- n_articles_sub_sc_ctx
- n_articles_sub_ss_ss
- n_articles_subst_bothvalid
- n_articles_subst_disagree
- n_articles_subst_freerider
- n_articles_subst_quietworker
- n_articles_symb
- n_articles_symb_sc_ctx
- n_articles_symb_ss_ss
- n_articles_tech
- n_articles_tech_lc_ctx
- n_articles_tech_ls_ss
- n_fintech_articles
- n_ft_articles_j70w10
- n_ft_articles_j70w5
- n_ft_articles_j75w5
- n_ft_articles_j80w10
unit: 篇数 (article count, 非负整数计数)
formula: "n_articles = Σ_{doc ∈ bank-year} 1[llm_verified_full(doc, target_bank) == True] (full-only 留篇门控, 2026-06-29); 各分类/去重变体计数在此留篇脊柱上按其判据子集计数, 分母口径逐族标注"
producer: news_process/pipeline/panel/ (dedup_sensitivity.py 产 j-变体存活计数; encode.py/encode_collab 产分类维度 verified 计数; geography.py/panel 聚合 n_articles 与 n_fintech_articles)
upstream:
- 12_fintech_news_full.parquet
- 13_cooccurrence_filter.parquet
- 14_materialize_ctx.parquet
- 21_tone_llms.parquet
citations:
- doi: 10.1007/s10479-025-06567-y
  type: journal
  authors: Anastasiou, D., Katsafados, A., & Tzomakas, C.
  year: 2026
  title: "Banks' stock price crash risk prediction with textual analysis: A machine learning approach"
  venue: Annals of Operations Research
  vol: 357
  issue: 1
  pages_or_artno: 89-111
- doi: 10.1002/jae.3095
  type: journal
  authors: Bodilsen, S. T., & Lunde, A.
  year: 2025
  title: "Exploiting news analytics for volatility forecasting"
  venue: Journal of Applied Econometrics
  vol: 40
  issue: 1
  pages_or_artno: 18-36
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: 20
- doi: 10.1093/restud/rdad018
  type: journal
  authors: Rambachan, A., & Roth, J.
  year: 2023
  title: "A more credible approach to parallel trends"
  venue: The Review of Economic Studies
  vol: 90
  issue: 5
  pages_or_artno: 2555-2591
- doi: 10.1002/jae.2985
  type: journal
  authors: List, J. A., Shaikh, A. M., & Vayalinkal, A.
  year: 2023
  title: "Multiple testing with covariate adjustment in experimental economics"
  venue: Journal of Applied Econometrics
  vol: 38
  issue: 6
  pages_or_artno: 920-939
- doi: 10.1002/jae.2969
  type: journal
  authors: MacKinnon, J. G., Nielsen, M. Ø., & Webb, M. D.
  year: 2023
  title: "Fast and reliable jackknife and bootstrap methods for cluster-robust inference"
  venue: Journal of Applied Econometrics
  vol: 38
  issue: 5
  pages_or_artno: 671-694
- doi: 10.1016/j.jacceco.2021.101455
  type: journal
  authors: Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y.
  year: 2022
  title: "Meet the press: Survey evidence on financial journalists as information intermediaries"
  venue: Journal of Accounting and Economics
  vol: 73
  issue: 2-3
  pages_or_artno: 101455
- doi: 10.2308/HORIZONS-19-161
  type: journal
  authors: Siano, F., & Wysocki, P.
  year: 2021
  title: "Transfer learning and textual analysis of accounting disclosures: Applying big data methods to small(er) datasets"
  venue: Accounting Horizons
  vol: 35
  issue: 3
  pages_or_artno: 217-244
- doi: 10.1002/jae.2508
  type: journal
  authors: MacKinnon, J. G., & Webb, M. D.
  year: 2017
  title: "Wild bootstrap inference for wildly different cluster sizes"
  venue: Journal of Applied Econometrics
  vol: 32
  issue: 2
  pages_or_artno: 233-254
- doi: 10.1016/j.jacceco.2017.07.002
  type: journal
  authors: Dyer, T., Lang, M., & Stice-Lawrence, L.
  year: 2017
  title: "The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation"
  venue: Journal of Accounting and Economics
  vol: 64
  issue: 2-3
  pages_or_artno: 221-245
- doi: 10.3386/w15851
  type: wp
  authors: Thoma, G., Torrisi, S., Gambardella, A., Guellec, D., Hall, B., & Harhoff, D.
  year: 2010
  title: "Harmonizing and combining large datasets: An application to firm-level patent and accounting data"
  venue: NBER Working Paper No. 15851
  pages_or_artno: w15851
new_dois: []
---

## CORE

【构念与来源】
本家族是 bank-year 面板中一整族"篇数计数"变量的集合, 其共同构念是: 在给定银行-年份单元内, 落入某个界定清晰的报道集合的媒体报道条数。计数本身没有量纲, 是非负整数, 但它在整个 news_process 计量框架里承担三重角色——分母、门控与曝光水平。分母角色指它是几乎所有比率型情感/属性测度的归一化基数 (例如各类 share、pct、intensity 的分母); 门控角色指某些计数为零或过小的单元会被判为"不可测"而置 NaN, 从而防止用极稀疏样本外推; 曝光水平角色指计数自身即是媒体关注度 (attention) 的原始度量, 可作被解释变量或控制变量直接进入回归。家族的锚点核心列是 n_articles, 即该银行-年份内经留篇门控保留的银行-金融科技报道总数; 其余 51 列都是在这一脊柱之上, 沿不同"切法"(分类维度、文本轨道、模型一致性、去重参数) 派生的子计数或替代计数。数据来源上溯到原始中文媒体语料 (stage 00 普查口径 1,819 万条媒体报道、2007–2025、3,740 家来源), 经银行实体识别 (stage 11)、金融科技识别 (stage 12)、共现硬过滤 (stage 13)、三轨文本物化 (stage 14) 与情感/属性 LLM 判定 (stage 21) 层层收敛后, 在面板聚合阶段按 bank-year 分组计数而成。媒体报道作为信息中介对银行的可见度塑造, 与 Call, Emett, Maksymov 和 Sharp (2022) 关于财经记者作为信息中介的调查证据、以及 Bodilsen 和 Lunde (2025) 将新闻分析量用于波动率预测的思路一脉相承——报道"有多少"本身就是一个有经济含义的一阶信号。

【方法学与计算】
计数的方法学关键在于"计入哪些文档"这一集合定义, 而非计数运算本身。全家族统一遵循 2026-06-29 确立的 full-only 留篇门控铁律: 一篇报道是否被判为"一篇银行金融科技报道"只看 full 轨的 LLM 核验结果 llm_verified_full == True; 该门控在 tone_llms 的 df_filtered 与 run_pipeline 的 stage21 skip 兼容判定两处保持副本同步。因此 n_articles 的行宇宙 = full 轨留篇集, 而 ctx 轨与 ss 轨降为 conditional-on-full 的测度轨与稳健性轨——它们的行宇宙是 full 留篇集的子集, per-track 计数照算但绝不反过来扩张留篇集。三轨文本的语义严格遵循 stage 14 物化: full = 标题 prepend + 全文正文; ctx = 标题 + 实体窗口; ss = 标题 + 银行∧金融科技同句±N 窗; ss 轨的回退语义镜像 ctx, 即无同句共现时 content_ss 退化为全文正文且 ss_is_fallback 置真, 与 ctx 共享 n_articles 分母。这一"分母同基"原则贯穿全族: 凡计算某比率 (如 fintech_share), 其分子子计数与分母总计数必须取自同一文档域、同一变体、同一轨道, 不得跨域拼凑。计数运算实现上是标准的 groupby-size / 条件求和, 由面板聚合器 (encode 系列与 geography 聚合) 逐 bank-year 落列; 去重敏感性子族则由 dedup_sensitivity 在已去重产物上叠加更严去重后重新计数。

【文献定位】
计数型媒体测度在文本金融与会计信息披露文献中有长期传统: Dyer, Lang 和 Stice-Lawrence (2017) 以主题模型刻画 10-K 文本演化时, 篇幅/条目数量是其结构化描述的基石; Siano 和 Wysocki (2021) 讨论把大数据文本方法迁移到较小样本时, 反复强调计数分母的稳定性对下游比率估计的决定性影响。就中文金融文本而言, Ma, Zhang 和 Zhang (2025) 构建面向国内投资者的细粒度情感词典、Lan 等 (2025) 用大语言模型做中文细粒度金融实体级情感分析, 均以文档计数为其覆盖度与召回率的报告口径; Anastasiou, Katsafados 和 Tzomakas (2026) 用银行文本做股价崩盘风险预测时, 也把报道数量作为暴露强度的代理。本家族把"计数"从附属统计提升为一等公民测度, 正是承接这一脉络: 报道数量既是关注度构念的直接观测, 也是所有归一化测度得以可比的前提。

【识别策略定位】
在识别策略层面, 本家族的计数变量主要以两种身份进入计量: 其一作为曝光/关注度的处理或控制变量, 其二作为构造比率型处理变量的分母。作为分母时, 计数的测量误差会通过比率传导到系数估计, 因此本项目刻意提供多套并行的计数口径 (分类维度切分、三轨切分、跨文本轨 full-vs-ctx 解耦切分、去重参数切分), 使研究者能检验主结论是否对"如何数报道"这一研究者自由度稳健。须特别澄清: 此处的 full-vs-ctx 解耦切分是同一 LLM 模型在两个文本口径 (全文轨 full 与实体上下文轨 ctx) 上对同一篇报道给出的属性标签是否一致的诊断, 属跨文本轨的说做残差信号, 绝非两个不同 LLM 厂商模型之间的跨模型一致率——后者是另一族 (LLM 三家投票、BERT 三模型) 的关切, 走根级 rwolf 跨模型 FWER 模板, 与本族的跨轨解耦口径正交、不可混同。这与 Rambachan 和 Roth (2023) 对平行趋势可信度的处理哲学相通——把识别所依赖的不可检验假设显式化并做敏感性带; 也与 List, Shaikh 和 Vayalinkal (2023) 在协变量调整下做多重检验校正的立场一致: 当同一构念有多个并行度量时, 推断须为族内多重性负责。特别地, 去重敏感性子族天然对应一个连续的稳健性带, 其推断应配合聚类稳健的自助法 (MacKinnon 和 Webb, 2017; MacKinnon, Nielsen 和 Webb, 2023) 在银行聚类维度上评估。

【与相邻测度的构念区分】
须把本族的"篇数计数"与三类相邻测度严格区分。第一, 计数不是强度 (intensity): intensity 家族对每篇报道赋予 TF-IDF 或语义权重后加总, 是加权量, 而本族是等权计数 (每篇计 1); Salton 与 Buckley 传统的词频加权对 intensity 适用, 对计数不适用。第二, 计数不是情感/属性均值: tone/attention 的比率与均值列以计数为分母, 但计数自身不含情感极性信息, 换情感模型 (LLM 三家投票、BERT 三模型、词典六族) 不改变 full 留篇计数, 只改变落入"正/负/技术/合作"等子集的成员身份。第三, 计数不是嵌入相似度: 与 co-primary 双轨嵌入 (Qwen3-8B 无后缀 4096 维 / text-embedding-3-large 的 _lg 3072 维) 无关, 本族无 _lg 孪生列, 属非嵌入 carve-out。

【已知局限与稳健性梯子】
铁律须复述: 凡本族涉及三轨 (full/ctx/ss)、分类维度并排、模型一致性并排、去重参数梯子的多个计数变体, 它们各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨/不同变体的计数混进同一 over-identified 的 Hansen J 过度识别检验; 每个变体应各自单独进入并排规格, 由规格稳健性 (specification robustness) 而非过度识别统计量来支撑结论。已知局限有三: 一是去重敏感性子族只能向"删得更多"方向扰动, 是"在生产去重之上再施加更严去重"的保守下界, 不等价于从原始语料按低阈值重跑 (keep-greedy 时间窗判重下, 生产小簇里已永久丢弃的文档无法在低阈值大簇里复活), 论文须如实表述为保守扰动而非 from-scratch 重导; 二是去重敏感性存在跨语料盲区, 生产去重在全语料 (银行/非银行分类之前) 上做, 而本子族只在银行新闻子集上重判重, 故"银行稿是某非银行稿的近似副本"这类跨子集近重复看不到, 会系统性低估严格去重本应捕获的剔除量, 这与 Thoma 等 (2010) 讨论跨库记录链接与去重时强调的匹配范围界定问题同源; 三是试跑样本 caveat, 当前盘上 T=2、约 176 个 bank-year, 变体仅追加剔除 1–3% 文章, 与生产锚点的 Pearson 相关接近 1.0 是低剔除率下的预期平凡结果, 绝非充分稳健性证据, 真正的证据须来自把每个变体分母代入主回归后系数符号与显著性的稳定性 (Stata Table A 并列)。情感/分类相关的计数还继承上游判定的局限: 否定处理、程度副词等语言学规则的取舍会影响子集成员身份 (Punetha 和 Jain, 2025), 生产语料 T=19 全量重跑属付费不可逆操作, 须先过 M0 审批门。

【计数域的层层收敛与文档身份】
理解本家族的关键是把"一篇报道"从原始语料到进入某个计数格的收敛链条讲清。原始媒体语料在 stage 00 经普查口径为 1,819 万条报道 (2007–2025、3,740 家来源、报纸类型占约 92.93%), 首先经过预处理与全语料去重; 随后 stage 11 做银行实体识别, 判定某报道是否提及某目标银行 (银行侧判定采用否定过滤 + 短名歧义过滤的严格口径), stage 12 做金融科技识别 (金融科技侧采用裸 AC 607 词表匹配的宽口径), 两侧判定的不对称是有意设计——银行侧要防误挂, 金融科技侧要保召回。stage 13 共现硬过滤在此基础上丢行, 只保留目标银行与至少一个金融科技词邻近共现 (生产口径为正负一句窗、标题加正文匹配) 的报道, 这是一次会真正减少行数的硬收敛, 且带有安全阀 (金融科技 AC 为空时保留全部行并高声告警、保留率过低或零行时以非零码退出, 绝不静默清空)。stage 14 物化三轨文本 (content_full/ctx/ss), 使下游能在三个文本视角上分别计数。stage 21 情感/属性 LLM 判定给出 llm_verified_full 等核验标记, full-only 门控在此锚定留篇集。因此一篇报道要计入 n_articles, 必须依次通过银行识别、金融科技识别、共现过滤、全文轨核验四道关口; 而要计入某个分类子计数 (如实质、技术、合作), 还须额外通过对应属性判定。这条收敛链的每一环都可能引入测量误差, 本家族提供的多套并行计数口径 (去重变体、三轨、模型一致性) 正是为让研究者在各环节上做敏感性检验而设。文档身份的唯一键是 (docid, target_bank) 二元组——同一篇报道若提及多家目标银行, 会对每家银行各计一次, 这一点在读跨银行汇总量时须留意, 与去重敏感性子族经 (docid, target_bank) semi-join 收敛到核验集的口径一致。

【零、缺失与单调性契约】
计数变量的取值语义须与 NaN 契约一并理解, 否则会误读稀疏格。就去重敏感性子族而言, 契约镜像生产锚点的关注度构造: 变体全集内某零金融科技曝光的银行-年份, 其 index/pct 取零表示真零曝光而非缺失; 而某银行-年份在该变体下失去全部银行新闻 (或本就不在 12_full 全集内), 则相应比率取 NaN 表示不可测——零与 NaN 的区分对下游回归的样本纳入至关重要, 把不可测误当真零会系统性拉低估计。单调性不变量是本子族的硬约束: 任一更严变体的存活篇数不超过生产篇数, 因为更严去重只会删得更多不会凭空增稿; 这条不变量可作数据质量的自检哨兵。就分类子计数而言, 交叉分类的八个有效格加兜底格之和须等于可分类的全文留篇总数, 提供另一条完备性自检。就跨文本轨 (full vs ctx) 解耦诊断而言, 双有效计数 (bothvalid, 全文轨与实体上下文轨两路标签均落在 canonical 白名单) 与分歧计数 (disagree, 两轨标签落白名单却不一致) 的相对关系刻画的是同一属性构念在"全文读法"与"实体邻近读法"之间的说做一致性 (D4 跨轨残差信号), 而非跨厂商模型稳健性, 亦非水平信息, 不可与水平计数混入同一识别式。分歧计数进一步按方向拆成 freerider (全文像基线类、上下文却是对照类, 即"说一套做一套"疑似信号) 与 quietworker (反向, 即"做了不说"), 二者互斥且之和恒等于分歧计数, 是构造性完备的方向分解, 而非合作角色象限或角色典型学。这些契约共同保证计数家族在生产 T=19 全量与本机 T=2 试跑之间的行为可预期: T=2 下大量分类格与三轨条件计数为零或退化 (同句共现稀疏、年内变异不足) 属预期, 绝非缺陷, 真实的信息含量要到生产全量才充分展开。作为跨次运行可复现的确定性锚, 计数值不随换情感模型、换嵌入模型 (Google 到阿里 Qwen) 而变, 只有落进子桶的具体篇目会变, 这一性质使计数成为整条流水线金标准复现的基准坐标。

【白话总纲】
用最直白的话把这一整族串起来: 这五十二列全都在回答同一个母问题的不同切法——"这家银行这一年, 被媒体写了多少条?"。最核心的一列 n_articles 数的是全部认下的银行金融科技报道, 是所有占比的分母、也是关注度本身。往下切: 按去重狠不狠切, 得到四个更瘦的分母分子, 用来检验结论会不会因为把重复稿删多删少而翻船; 按报道讲的是啥切, 得到实质、象征、技术、合作、定位、独立这些子桶的条数, 用来算各类占比; 按只看整篇、只看实体周边、还是只看同句切, 得到三条轨的平行计数, 互为稳健性; 按同一个大模型看全文和看实体周边这两种读法判得合不合切 (注意是同一模型的两种文本口径, 不是两个不同大模型), 得到双方都表态、两种读法打架、以及"全文一套上下文另一套 (说一套做一套)"或反过来"做了不说"的诊断条数, 用来看同一个属性换种读法稳不稳。所有这些切法都遵循一条铁律: 各切各的、并排摆着互为稳健性、谁也不比谁主, 绝不能把不同切法的计数硬塞进同一个过度识别检验里。它们既是下游一切比率能不能可靠比较的地基, 也是审稿人追问"你的样本干净吗、你的口径拍脑袋吗"时, 研究者能摊开来的透明账本。媒体报道数量本身就是有经济含义的信号 (Call, Emett, Maksymov 和 Sharp, 2022; Bodilsen 和 Lunde, 2025), 把它数清楚、数出多个口径, 是整条计量链条可信度的第一块砖。

【去重敏感性的方法学诚实声明】
去重敏感性子族 (由 dedup_sensitivity 产出) 承载本家族最需要谨慎表述的方法学立场, 须逐条讲明。其一, 口径诚实: 本模块在已去重产物上叠加更严去重, 其存活集不严格等于在原始语料上直接按该严参数去重的存活集。机理在于时间窗口判重是保留优先 (keep-greedy) 的——簇内按日期升序, 后发文若落在任一已保留文的窗口内即删, 而低阈值下的相似哈希簇是高阈值簇的超集; 某文档可能在生产 0.8 的小簇里被删, 却在原始直算 0.7 的大簇里因锚点更早或超窗反而存活, 而两阶段已永久丢弃它、无法复活。故本结果应表述为"在生产去重之上施加更严扰动的保守下界", 而非"等价于从原始重跑"; 它仍是合法的稳健性探针 (直接回答去重更激进时结论是否稳), 只是不可解释为从头重导。sidecar 落 two_stage_approximation 标记供 Stata 表脚注引用。其二, 跨语料盲区: 生产去重在全语料 (银行/金融科技分类之前) 上做, 本模块只在银行新闻子集上重判重, 故银行新闻与非银行新闻之间的跨子集近似重复看不到, 会系统性低估原始直算严格去重本会捕获的剔除量, 属本模块对关注度构念的有意范围限定, 论文须如实披露。其三, 试跑样本告诫: 当前盘上约 176 个银行-年份、变体仅追加剔除百分之一到三的文章, 与生产锚点的相关接近 1.0 是低剔除率下的预期平凡结果, 非充分稳健性证据; 真正的证据来自把每个变体的分子分母代入主回归后, 系数符号与显著性的稳定性 (配 esttab 并列成 Table A)。这三条诚实声明与稳健推断文献强调的"把不可检验假设显式化并做敏感性带"的精神一致 (Rambachan 和 Roth, 2023), 其推断须配合聚类稳健的自助法在银行聚类维度评估 (MacKinnon 和 Webb, 2017; MacKinnon, Nielsen 和 Webb, 2023)。

【核验域门控与同域不变量】
自 2026-06-13 的面板宇宙一致性审计起, 去重敏感性子族的金融科技分子源与生产锚点的关注度处理保持一致: 经 (docid, target_bank) 半连接收敛到 stage-21 核验集, 使金融科技分子等于核验集与变体存活集之交; 而分母与全集脊柱仍取 12_full 全部银行新闻 (未门控)。须特别提醒: sidecar 的存活文章数与保留占比仍是全 docid 域的去重存活率诊断, 与金融科技分子的"核验交存活"域不同, 勿混读。因生产锚点本身亦已核验门控, 故变体指数与生产指数两侧同域, 满足同域不变量, 相关性比较才有意义。这一域对齐是本子族能作为合法稳健性检验的前提——若分子分母取不同域, 算出的比率会因域漂移而不可解释。理解这一点也有助于读者区分本家族两类看似都叫"存活率/计数"的量: 一类是数据质量层面的去重诊断 (全 docid 域, 回答删了多少稿), 另一类是关注度测度层面的核验计数 (核验交存活域, 回答有多少条进入关注度构造), 二者服务不同目的、不可互相替代。此种对域界定的严谨要求, 与记录链接和跨库去重文献强调匹配域一致性的方法学传统同源 (Thoma 等, 2010)。

## VAR: n_all_articles_j70w10

【变体差分】
本列是去重敏感性子族的"全银行新闻"分母之一, 对应变体参数 j70w10——Jaccard 相似度阈值 0.70 配 10 个工作日的转载判重窗口, 是四个变体中双向最严格 (阈值最低、窗口最长) 的一个: 阈值越低意味着越多文档被判为近似重复而合并, 窗口越长意味着越晚的转载仍会落入某已保留文的判重窗内而被剔除。其计数域为 12_fintech_news_full 的全部银行新闻 (未经 stage-21 verified 门控), 逐 bank-year 统计在该更严去重扰动下存活的报道条数, 是 attention_pct 类比率在该变体下的分母 N_all。相对生产锚点 j80w5 (即无后缀的既有 attention 列本身), 本变体删除更多转载, 故其计数满足单调性不变量 N_all(变体) ≤ N_all(生产)。铁律: 本列与 j70w5、j75w5、j80w10 三个同族分母各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 其正确用法是把各变体分母逐一代入主回归复跑, 检验系数稳健性, 而非以变体间高相关 (T=2 下接近 1.0, 属低剔除率平凡结果) 冒充稳健性证据 (MacKinnon 和 Webb, 2017)。本变体只能向删得更多方向扰动, 是保守下界而非 from-scratch 重导, 且存在银行/非银行跨子集近重复盲区。

用大白话说, 这一列回答的是: 当我们把判定重复的门槛放到最松 (相似度只要七成就算重稿)、把追剔转载的时间窗拉到最长 (十个工作日内的跟风稿都删), 那么这家银行这一年还剩下多少条银行新闻可以当分母。它是四个去重变体里删得最狠的一个下界, 专门用来检验主结论会不会因为去重删得多一点就翻船; 真要下结论, 得把这个更瘦的分母塞回主回归里看系数稳不稳, 而不能拿它和生产口径高度相关就自我安慰。它只对银行新闻子集重新判重, 银行稿与非银行稿之间的跨类近重复它照顾不到, 这一点在数据披露时要老实交代。

## VAR: n_all_articles_j70w5

【变体差分】
本列同属去重敏感性分母族, 变体参数 j70w5——Jaccard 阈值 0.70 配 5 个工作日窗口。与 j70w10 相比, 二者共享最低相似度阈值 0.70 (最激进的合并倾向), 但本列采用较短的 5 工作日转载窗, 因此只在生产锚点相同的 5 日窗口内、以更松的相似度判定去重, 剔除量介于生产锚点与 j70w10 之间: 相似度阈值下调使其比生产 j80w5 删得多, 而窗口不加长使其比 j70w10 删得少。计数域仍为 12_fintech_news_full 全部银行新闻 (未 verified 门控), 逐 bank-year 计存活条数, 作为该变体下 attention 比率的分母 N_all。此列的意义是把"相似度阈值"这一研究者自由度单独拧动一格 (0.80→0.70) 而保持窗口不变, 从而与 j75w5 (0.75×5) 一起构成沿相似度维度的细分梯子。铁律照旧: 与同族三分母各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 使用须代入主回归看系数稳定性 (List, Shaikh 和 Vayalinkal, 2023 的多重检验立场适用于族内并列)。同样受保守下界与跨子集盲区两条局限约束, 试跑 T=2 相关接近 1.0 不构成充分证据。

用大白话说, 这一列是把判重门槛放松到相似度七成、但只在原口径的五天窗内追剔转载后, 剩下多少条银行新闻做分母。它相当于只把相似度这一个旋钮往松拧一格、时间窗保持不动, 因此删掉的稿子比生产口径多、又比十天窗那个变体少, 恰好卡在中间。它和相似度更接近生产口径的七五变体一起, 描出结论对相似度门槛敏不敏感的一条梯子。它同样只在银行新闻子集里重判重, 存在跨类近重复盲区, 试跑样本量小的时候和主口径高度相关是必然的, 不能当稳健性证据。

## VAR: n_all_articles_j75w5

【变体差分】
本列去重敏感性分母, 变体参数 j75w5——Jaccard 阈值 0.75 配 5 个工作日窗口, 是最接近生产锚点 j80w5 的一个扰动: 仅把相似度阈值由 0.80 微降至 0.75 而窗口不变, 属"轻扰动"臂。它与 j70w5 共享 5 工作日窗口, 三者 (j80w5 生产、j75w5、j70w5) 在固定窗口下沿相似度阈值 0.80→0.75→0.70 单调放松, 剔除量单调递增, 存活计数单调递减, 恰好刻画结论对相似度阈值的敏感梯度。计数域为 12_fintech_news_full 全部银行新闻 (未 verified 门控), 逐 bank-year 统计存活条数, 供该变体 attention 比率作分母 N_all。此列在四变体中扰动幅度最小, 因而在低剔除率试跑下与生产锚点相关性最高——这一高相关恰恰印证 T=2 下相关系数不能当稳健性证据的告诫, 真正判据是主回归系数 (MacKinnon, Nielsen 和 Webb, 2023 的聚类稳健自助法用于此处推断)。铁律: 与同族三分母各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 保守下界与跨子集近重复盲区两局限同样适用。

用大白话说, 这一列只把相似度门槛从八成轻轻降到七成半、时间窗不变, 是四个变体里动得最轻的一个, 因此剩下的银行新闻数最接近生产口径。正因为动得轻, 它和主口径算出来的相关性最高——这恰恰提醒我们: 相关性高只是因为几乎没删几条, 不代表结论稳; 真正要看的是把这个分母代进主回归后, 银行金融科技的估计系数还稳不稳。它服务于沿相似度门槛细看敏感性的需要, 与更激进的变体互为参照。

## VAR: n_all_articles_j80w10

【变体差分】
本列去重敏感性分母, 变体参数 j80w10——Jaccard 阈值 0.80 配 10 个工作日窗口。它与生产锚点 j80w5 共享相同的相似度阈值 0.80, 唯一差别是把转载判重窗口由 5 工作日延长到 10 工作日, 因此本列单独拧动"窗口长度"这一自由度而保持相似度不变: 更长的窗口使更晚出现的转载仍被识别为重复并剔除, 故其存活计数低于生产锚点、体现的是对"转载扩散持续多久"这一假设的敏感性。它与 j70w10 共享 10 工作日窗口, 二者在固定长窗下沿相似度 0.80→0.70 放松, 与 5 日窗那一组构成正交的二维 (阈值×窗口) 扰动网格的另一边。计数域为 12_fintech_news_full 全部银行新闻 (未 verified 门控), 逐 bank-year 计存活条数作分母 N_all。铁律: 与同族三分母各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 用法为代入主回归验系数稳健。受保守下界 (只能删得更多) 与跨子集盲区两局限约束, T=2 试跑高相关属预期平凡结果。

用大白话说, 这一列保持相似度门槛不变 (还是八成), 只把追剔转载的时间窗从五天拉长到十天, 专门回答一个问题: 如果我们认为转载会持续更久、把更晚的跟风稿也当重复删掉, 分母会缩多少。它和十天窗、七成门槛那个变体一起构成长窗口这一边, 与五天窗那一组形成门槛乘窗口的二维扰动网格。它删得比生产口径多, 剩下的银行新闻数更少, 用途仍是代入主回归验证结论对转载窗口长度的稳健性。

## VAR: n_articles

【变体差分】
本列是全家族的锚点核心列 (tier=core), 也是整个 bank-year 面板最基础的计数: 在给定银行-年份单元内, 经 full-only 留篇门控 (2026-06-29 铁律) 保留的银行-金融科技报道总条数, 即满足 llm_verified_full == True 的文档去重计数。它是几乎所有比率型情感与属性测度的规范分母, 也是"该 bank-year 是否有可分析样本"的门控信号——计数为零或极小的单元, 其下游比率被置 NaN 或标记为不可测, 以防用稀疏观测外推。它同时是媒体关注度构念的最直接一阶度量, 可作被解释变量 (P2 attention 主线) 或控制变量直接入模。与本族其余 51 列的根本区别在于: n_articles 是未按任何分类维度、模型、去重变体细分的全集计数, 是脊柱本身而非某个切面; 所有 _app/_tech/_sub/_symb/_collab/_locus/_indep/_exc 等分类子计数都是它的子集, 所有 j-变体计数都是它在更严去重下的收缩, 所有 _ctx/_ss 派生都是它在其他轨道上的对偶。轨道上, n_articles 严格定义在 full 轨——留篇门控只认 full 轨核验, ctx 与 ss 轨是 conditional-on-full 的子集测度轨, 其行宇宙是 full 留篇集的子集, per-track 计数照算但绝不反向扩张 full 集。这一 full-only 口径的确立避免了三轨各自留篇导致行宇宙漂移的问题, 使换嵌入模型 (Google→阿里 Qwen)、换情感模型都不改变 n_articles 本身的取值 (只改变落入各情感/属性子集的成员身份), 从而成为跨 run 可复现的确定性锚。构念上须与 n_fintech_articles 区分: 后者是本 bank-year 内被判为金融科技相关的报道数, 是 fintech_share 的分子, 而 n_articles 是覆盖全部留篇的分母基数。数据来源上溯原始媒体语料经 stage 11/12/13/14/21 逐层收敛, 面板聚合阶段按 bank-year groupby 计数落列; 生产全量为 约 1,819 万条过滤后语料、2007–2025、T=19, 当前盘上为 T=2 试跑约 176 个 bank-year。铁律须复述: 凡以 n_articles 及其三轨/去重变体做并排稳健性, 各变体各自 just-identified、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J; 换厂商维度与 full-only 门控带来的 n_articles/fintech_share/attention_pct 收缩均属预期数值副作用而非 bug, manuscript 须披露。计数作为关注度度量的经济含义, 呼应 Call, Emett, Maksymov 和 Sharp (2022) 对财经记者作为信息中介的证据、Bodilsen 和 Lunde (2025) 对新闻分析量的预测性利用, 以及 Anastasiou, Katsafados 和 Tzomakas (2026) 以银行文本量做风险预测的思路: 报道数量本身即是一个有识别力的暴露信号, 而非纯粹的规模控制项。

在识别策略上须再补三点使用规范。其一, 当 n_articles 以曝光/关注度身份直接进入回归 (被解释或控制) 时, 其条数分布在生产语料上高度右偏且跨银行异方差, 故推断应配合银行维度的聚类稳健自助法而非渐近正态近似 (MacKinnon 和 Webb, 2017; MacKinnon, Nielsen 和 Webb, 2023 的快速可靠 jackknife/bootstrap 方法尤适用于簇规模悬殊的银行面板); 当它以分母身份构造比率型处理变量时, 分母的测量误差会经比率非线性传导到系数, 这正是本家族刻意并置去重变体、三轨、模型一致性等多套并行分母的动因——让主结论对"如何数报道"这一研究者自由度接受显式敏感性带的检验, 与 Rambachan 和 Roth (2023) 把识别所依赖的不可检验假设外显化的处理哲学同源, 也与 List, Shaikh 和 Vayalinkal (2023) 在多个并行度量下为族内多重性负责的立场一致。其二, n_articles 作为门控信号时, 其零/极小取值触发下游比率置 NaN 或标记不可测的判定必须与真零曝光严格区分: 该 bank-year 无任何留篇是不可测 (NaN), 而有留篇但无某属性子集成员是真零 (取零值), 二者对样本纳入的后果相反, 混淆会系统性偏移估计。其三, 作为跨 run 确定性锚, n_articles 的取值稳定性使其可充当金标准复现的基准坐标: 换情感模型 (LLM 三家投票、BERT 三模型、词典六族) 或换嵌入模型均不改本列, 只重新分配落入各子桶的成员, 因此任何 run 若 n_articles 漂移即指向留篇门控或上游收敛链的异常, 而非模型替换的正常副作用。这三条使用规范共同确保 n_articles 既能当透明的样本厚度账本, 又不被误用为可混入过度识别检验的多余矩条件。

用大白话说, 这一列就是最朴素的一句话: 这家银行这一年, 我们最终认下了多少条关于它的银行金融科技报道。它是所有占比、均值、强度指标的分母, 也是判断这个银行-年份格子里到底有没有足够料可以分析的开关——料太少的格子, 下游比率会被标成不可测, 免得拿一两条稿子瞎推断。它还直接就是媒体关注度的最原始度量, 报道越多说明这家银行这一年在金融科技话题上越被媒体盯着。它只认全文轨的判定, 换情感模型、换嵌入模型都不会改这个数, 只会改动落进正面、负面、技术、合作这些子桶里的具体是哪几条稿子; 也正因为如此, 它是整条流水线跨次运行都能复现的确定性锚点。换厂商或收紧门控带来的关注度收缩是设计使然, 不是程序出错, 论文里要如实披露。它承载的是最基础也最要紧的一个事实: 样本有多厚, 后续所有归一化测度能不能可靠比较, 都系在这一个数上。

## VAR: n_articles_app

【变体差分】
本列是 attention (关注度) 维度下的有效报道计数——统计该 bank-year 内进入关注度测度构造的报道条数, 是 attention 相关比率 (如 attention_pct/attention_index) 在 full 轨主口径下的分母基数, 与家族锚点 n_articles 的区别在于其计数域限定在 attention 度量所消费的文档子集 (承接 P2 attention 主线的处理域) 而非全部留篇。它遵循 full-only 门控, 即以 full 轨核验为准界定"一篇关注度报道"。作为分母, 它保证 attention 比率的分子分母同基、同域、同轨, 避免跨域拼凑导致的比率失真。其经济含义直接对应媒体对银行的可见度水平, 与 Call, Emett, Maksymov 和 Sharp (2022) 关于财经记者塑造企业可见度的证据一致——报道数量的多寡本身即是一个被市场感知的一阶信号 (Bodilsen 和 Lunde, 2025)。它有两个三轨对偶列 n_articles_app_lc_ctx 与 n_articles_app_ls_ss, 分别在 ctx 轨与 ss 轨给出条件计数; 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。本列本身是 full 轨主口径, 生产 T=19 下才有充分年内变异, T=2 试跑的极小计数只作管线连通性验证, 不承载识别。

用大白话说, 这一列数的是: 进入关注度这套指标计算的报道有几条, 也就是关注度占比和关注度指数的分母。它和全集报道数的区别在于把范围收到关注度度量真正消费的那批稿子上, 保证分子分母同一批口径, 免得比率算歪。报道越多, 说明这家银行这一年在媒体上的可见度越高。它另有上下文轨和同句轨两个孪生列, 三条轨各算各的、互为稳健性、不能塞进同一个过度识别检验。

## VAR: n_articles_app_lc_ctx

【变体差分】
本列是 n_articles_app 的 ctx 轨对偶——在标题 + 实体窗口的上下文轨 (content_ctx) 上, 统计进入关注度测度的有效报道条数。它与 full 轨主口径 n_articles_app 的唯一差别是文本轨道: ctx 轨只保留银行/金融科技实体附近的上下文窗口而非全文, 因而是一条"聚焦实体邻域"的条件计数轨。按 full-only 门控铁律, ctx 轨为 conditional-on-full 的稳健性/测度轨, 其行宇宙是 full 留篇集的子集, per-track 计数照算但不反向扩张留篇集。它与 full 主口径及 ss 轨对偶 n_articles_app_ls_ss 三者各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。ss 轨在无同句共现时回退镜像 ctx 语义, 但本 ctx 轨自身不回退——它就是实体窗口物化的直接产物。此列的价值是提供"若只看实体邻近上下文, 关注度计数是否漂移"的稳健性检验; T=2 试跑下 ctx 轨可能零方差退化属预期, 生产 T=19 正常。它不含情感极性, 换情感/嵌入模型不改变本轨计数, 属非嵌入 carve-out, 无 _lg 孪生。

用大白话说, 这一列是关注度报道数的上下文轨版本: 只截取银行和金融科技词附近那一小段上下文, 而不是整篇, 再数有几条进入关注度计算。它是全文轨主口径的稳健性伴侣, 回答的是若只盯实体周边、关注度报道数会不会漂。它的行范围是全文留篇的子集, 各算各的不反过来扩大留篇集, 也不掺进同一个过度识别检验。试跑样本小时这一轨常常没有方差, 属正常退化。

## VAR: n_articles_app_ls_ss

【变体差分】
本列是 n_articles_app 的 ss 轨对偶——在标题 + 银行∧金融科技同句±N 窗的同句轨 (content_ss) 上统计进入关注度测度的有效报道条数。与 full 主口径的差别在文本轨道: ss 轨要求银行与金融科技词在同一句 (或相邻窗) 内共现, 是三轨中判定最严的一轨, 语义上镜像 ctx 但收窄到句级共现。回退语义须精确复述: 当某报道无银行∧金融科技同句共现时, content_ss 退化为全文正文、ss_is_fallback 置真, 并与 ctx 共享 n_articles 分母; 若 FINTECH_AC 为空则 *_is_fallback 全真优雅降级。按 full-only 门控, ss 轨为 conditional-on-full 子集测度轨, 行宇宙是 full 留篇集的子集。它与 full 主口径及 ctx 轨对偶各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。T=2 试跑下 ss 轨常零方差退化 (同句共现稀疏) 属预期, 生产 T=19 才有充分变异。本列不含情感信息, 属非嵌入 carve-out 无 _lg 孪生, 换模型不改本轨计数。

用大白话说, 这一列是关注度报道数的同句轨版本: 要求银行和金融科技词出现在同一句里才算, 是三条轨里最严的一条。碰到全篇都没有同句共现的稿子, 它会退回按全文来算并打上回退标记, 这一点和上下文轨的处理一致。它是主口径的稳健性伴侣, 各算各的、互为稳健性、不进同一个过度识别检验。同句共现本来就稀疏, 所以小样本下这一轨经常没方差, 要到生产全量才有足够变化。

## VAR: n_articles_cell_1_full

【变体差分】
本列是三维 (三个二值属性维度) 交叉分类中第 1 格在 full 轨的报道计数——统计该 bank-year 内 full 轨留篇集中落入交叉分类第 1 单元格的报道条数。此处的交叉分类由三个各自二取一的属性维度构成: 实质性/象征性 (substantiveness)、底层技术/应用场景 (locus)、自主研发/外部协同 (collab), 三 bit 组合成 2×2×2=8 个有效格 (源码 cell_id = subst×4 + locus×2 + collab + 1 ∈ {1..8}), 第 1 格即 (0,0,0)=实质性·底层技术·自主研发这一三维全基线组合, 故称"二维"是误读, 有效格数 8 正来自 2^3 而非任何两维交叉。它与家族锚点 n_articles 的差别在于把全集按这个三维交叉分类切成互斥的 8 格加一个 NA 兜底格, 本列专计第 1 格; 九个格 (cell_1..8 与 cell_NA) 的计数之和应等于对应 full 轨可分类留篇总数, 构成一个完备且互斥的划分。full 后缀标明其定义在 full 轨 (标题 prepend + 全文正文), 遵循 full-only 门控。这类分格计数用于刻画报道在某属性组合上的分布结构 (类似 Dyer, Lang 和 Stice-Lawrence, 2017 以主题分布描述文本结构的思路), 也是构造格内比率的分母。它作为诊断性/结构性计数, 与并排的 cell_2..8 及 NA 各自 just-identified, 禁混进同一 over-identified Hansen J。T=2 试跑下多数格计数极小或为零属预期稀疏, 生产 T=19 才充分填充。本列不含情感极性, 换模型不改变格归属计数 (格划分由属性判定而非情感模型驱动的部分保持稳定)。

用大白话说, 这一列数的是: 把报道按一张交叉分类表切成八个格子加一个说不清的格子后, 落在第一格里的稿子有几条。它是描述报道在属性组合上怎么分布的一块拼图, 也是这一格内部算占比时的分母。八个有效格加上兜底格的条数应当加起来等于能分类的全文留篇总数。小样本下很多格子是零或个位数, 属正常稀疏, 要到生产全量才填得实。

## VAR: n_articles_cell_2_full

【变体差分】
本列是交叉分类矩阵第 2 格在 full 轨的报道计数, 统计该 bank-year 内 full 轨留篇中落入第 2 单元格的条数。它与第 1 格 n_articles_cell_1_full 的唯一差别是所计的格坐标不同——两列在同一完备互斥划分中各占一格, 语义上互斥不重叠, 合计口径见家族 CORE。full 后缀标明轨道为 full (标题 prepend + 全文正文), 遵循 full-only 门控。作为结构性分格计数, 它刻画报道属性组合分布中第 2 单元的质量, 是格内归一化比率的分母基数, 呼应以离散单元描述文本分布的传统 (Dyer, Lang 和 Stice-Lawrence, 2017)。它与并排的其余八格各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。T=2 试跑下该格计数常为极小值或零属预期稀疏退化, 生产 T=19 才有充分填充与年内变异。本列为纯计数不含情感极性, 属非嵌入 carve-out, 无 _lg 孪生, 换情感/嵌入模型不改变本格计数的属性归属基础。

用大白话说, 这一列数的是交叉分类表里落在第二格的稿子条数, 和第一格只差在坐标不同, 两格互不重叠。它和其余各格一起把报道铺在属性组合的方格上, 好让我们看清这家银行这一年的报道更集中在哪一类。它也是这一格内部比率的分母。小样本下常常是零或极小值, 生产全量才有意义。

## VAR: n_articles_cell_3_full

【变体差分】
本列是交叉分类矩阵第 3 格在 full 轨的报道计数, 统计 full 轨留篇中落入第 3 单元格的条数。与其余各格列的差别仅在格坐标: 九格 (1..8 与 NA) 构成完备互斥划分, 本列专计第 3 格, 与其他格无重叠。full 后缀标明其定义在 full 轨 (标题 prepend + 全文正文), 遵循 full-only 留篇门控。此类分格计数属结构性诊断变量, 用于观察报道在属性组合空间中的分布密度并作格内比率分母, 与主题/属性离散化描述文本结构的方法论一脉相承 (Dyer, Lang 和 Stice-Lawrence, 2017; Siano 和 Wysocki, 2021 强调分母稳定性对下游比率的影响)。它与并排八格各自 just-identified, 严禁混进同一 over-identified Hansen J。T=2 试跑下第 3 格常极稀疏或为零属预期, 生产 T=19 才充分填充。本列纯计数、不含情感极性, 属非嵌入 carve-out 无 _lg 孪生, 换模型不改本格归属计数。作为面板结构描述, 它与情感/属性均值列构念正交, 不可互相替代。

用大白话说, 这一列数的是交叉分类表第三格里的稿子条数, 只是格子坐标和别的格不同, 九个格互斥又完备。它帮我们看报道在属性空间里的疏密, 也当这一格比率的分母。跟情感均值那种列完全是两回事——它只管数数量, 不管稿子说的是好话还是坏话。小样本下多为零, 生产全量才填得起来。

## VAR: n_articles_cell_4_full

【变体差分】
本列是交叉分类矩阵第 4 格在 full 轨的报道计数, 统计 full 轨留篇中落入第 4 单元格的条数。它与其余格列的差别仅在所占格坐标, 九格构成完备互斥划分, 本列专计第 4 格且与他格互斥。full 后缀标明轨道为 full (标题 prepend + 全文正文), 遵循 full-only 门控。作为结构性分格计数, 它度量报道属性组合分布中第 4 单元的规模, 是该格内归一化比率的分母, 承接以离散单元刻画文本结构分布的传统 (Dyer, Lang 和 Stice-Lawrence, 2017)。它与并排八格各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 分格之间是互补的描述性划分而非可并入同一过度识别式的工具集。T=2 试跑下第 4 格计数常为零或极小属预期稀疏退化, 生产 T=19 才具备充分填充与变异。本列为纯计数不含情感极性, 属非嵌入 carve-out, 无 _lg 孪生, 换情感/嵌入模型不改变本格属性归属计数; 它与格内情感均值列构念正交, 不可互替。

用大白话说, 这一列数的是交叉分类表第四格里的稿子条数, 和别的格只差坐标, 彼此不重叠。它是描述报道属性分布的一块拼图, 也是这一格内部比率的分母。它和格子里的情感均值是两码事, 一个数条数、一个算态度, 不能互相替代。小样本下常为零或个位数, 属正常, 生产全量才实。

## VAR: n_articles_cell_5_full

【变体差分】
本列是交叉分类矩阵第 5 格在 full 轨的报道计数, 统计 full 轨留篇中落入第 5 单元格的条数。差别仅在格坐标: 与 cell_1..4、cell_6..8、cell_NA 同处一个完备互斥划分, 本列专计第 5 格。full 后缀标明其在 full 轨 (标题 prepend + 全文正文) 定义, 遵循 full-only 门控。作为结构性分格计数, 它刻画报道属性组合分布第 5 单元的密度, 用作格内比率分母, 呼应文本离散化描述结构的方法论 (Dyer, Lang 和 Stice-Lawrence, 2017; 分母稳定性见 Siano 和 Wysocki, 2021)。它与并排八格各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。T=2 试跑下该格常极稀疏或为零属预期, 生产 T=19 才充分填充与产生年内变异。本列纯计数不含情感极性, 属非嵌入 carve-out, 无 _lg 孪生, 换模型不改本格归属计数。它是面板结构的描述性切面, 与情感/属性均值列构念正交, 二者不可互相替代或并入同一识别式。

用大白话说, 这一列数的是交叉分类表第五格里的稿子条数, 只是坐标不同, 九格互斥完备。它反映报道在这一属性组合上有多密, 也是格内比率的分母。它只数数量、不含态度信息, 换情感模型不影响这个格的归属数。小样本下多为零, 要到生产全量才有实质填充和年际变化。

## VAR: n_articles_cell_6_full

【变体差分】
本列是交叉分类矩阵第 6 格在 full 轨的报道计数, 统计 full 轨留篇中落入第 6 单元格的条数, 与其余格列仅格坐标不同, 九格互斥完备。full 后缀标明轨道为 full (标题 prepend + 全文正文), 遵循 full-only 留篇门控。作为结构性分格计数, 它度量报道属性组合分布第 6 单元的规模并作格内比率分母, 承接以离散单元描述文本分布结构的传统 (Dyer, Lang 和 Stice-Lawrence, 2017)。它与并排八格各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 分格是互补描述性划分而非可合并的过度识别工具集。T=2 试跑下第 6 格计数常为零或极小属预期稀疏退化, 生产 T=19 才具备充分填充。本列为纯计数不含情感极性, 属非嵌入 carve-out, 无 _lg 孪生, 换情感/嵌入模型不改变本格属性归属计数; 与格内情感均值列构念正交不可互替。此列与其余分格联合观察时, 提供报道结构分布的横截面画像, 是 attention 与属性构念之外的第三类描述信息。

用大白话说, 这一列数的是交叉分类表第六格里的稿子条数, 与别的格只差坐标、互不重叠。它是报道属性分布画像的一块, 也是这一格内部比率的分母。把九个格一起看, 就能读出这家银行这一年的报道在属性上是扎堆还是分散。小样本下常为零, 生产全量才填实。

## VAR: n_articles_cell_7_full

【变体差分】
本列是交叉分类矩阵第 7 格在 full 轨的报道计数, 统计 full 轨留篇中落入第 7 单元格的条数, 与其余格列仅格坐标不同, 九格完备互斥。full 后缀标明在 full 轨 (标题 prepend + 全文正文) 定义, 遵循 full-only 门控。作为结构性分格计数, 它刻画报道属性组合分布第 7 单元密度并作格内比率分母, 呼应文本离散化描述结构方法论 (Dyer, Lang 和 Stice-Lawrence, 2017; Siano 和 Wysocki, 2021)。它与并排八格各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。T=2 试跑下第 7 格常极稀疏或为零属预期, 生产 T=19 才充分填充并产生年内变异。本列纯计数不含情感极性, 属非嵌入 carve-out, 无 _lg 孪生, 换模型不改本格归属计数。它是面板结构描述性切面, 与情感/属性均值列构念正交, 不可互相替代或并入同一识别式; 与其余分格并列时构成对报道属性分布的完整横截面刻画, 供研究者审视样本在属性空间中的集中或分散程度。

用大白话说, 这一列数的是交叉分类表第七格里的稿子条数, 坐标不同、互不重叠。它和其余各格拼起来给出报道属性分布的完整横截面画像, 也当这一格比率的分母。它只管数量、不含情感极性, 换模型不改这个格的归属数。小样本下多为零或个位数, 生产全量才有意义。

## VAR: n_articles_cell_8_full

【变体差分】
本列是交叉分类矩阵第 8 格 (最后一个有效格) 在 full 轨的报道计数, 统计 full 轨留篇中落入第 8 单元格的条数, 与其余格列仅格坐标不同; cell_1..8 加 cell_NA 构成完备互斥划分, 本列专计第 8 格。full 后缀标明轨道为 full (标题 prepend + 全文正文), 遵循 full-only 门控。作为结构性分格计数, 它度量报道属性组合分布末格的规模并作格内比率分母, 承接以离散单元描述文本分布的传统 (Dyer, Lang 和 Stice-Lawrence, 2017)。它与并排其余七格及 NA 格各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。T=2 试跑下第 8 格计数常为零或极小属预期稀疏退化, 生产 T=19 才充分填充。本列为纯计数不含情感极性, 属非嵌入 carve-out, 无 _lg 孪生, 换情感/嵌入模型不改本格属性归属计数; 与格内情感均值列构念正交不可互替。作为八格中的最后一格, 它与 cell_NA 一起承担"划分是否完备闭合"的验证功能——八有效格加 NA 之和须等于可分类 full 留篇总数。

用大白话说, 这一列数的是交叉分类表最后一个有效格 (第八格) 里的稿子条数。它和兜底格一起承担一个校验功能: 八个有效格加上兜底格的条数, 应当恰好等于能参与分类的全文留篇总数, 用来确认这张分类表是不是完整闭合的。小样本下常为零或极小, 生产全量才填得起来。

## VAR: n_articles_cell_NA_full

【变体差分】
本列是交叉分类矩阵的未分类兜底格 (NA) 在 full 轨的报道计数——统计该 bank-year 内 full 轨留篇中无法被归入八个有效格中任何一格的报道条数。它与 cell_1..8 的根本差别在于: 后八者是明确落入某属性组合的报道, 而本列是划分的残差桶, 收纳因属性缺失、判定歧义或不适用而未获有效格坐标的文档。它承担完备性闭合功能: cell_1..8 与 cell_NA 之和须等于对应 full 轨可参与划分的留篇总数, 因此本列的取值大小直接反映交叉分类在该 bank-year 的覆盖度——NA 计数越高, 说明可归类的信息越少, 下游格内比率越应审慎解读 (Siano 和 Wysocki, 2021 关于小样本下分母稳定性的告诫在此尤为相关)。full 后缀标明轨道, 遵循 full-only 门控。它与八有效格各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。本列纯计数不含情感极性, 属非嵌入 carve-out, 无 _lg 孪生。T=2 试跑下 NA 格可能占比偏高属稀疏样本预期, 生产 T=19 覆盖度提升。作为诊断变量, 它是判断分格结构是否可信的关键把手。

用大白话说, 这一列数的是: 那些实在归不进八个有效格、被扔进兜底格的稿子有几条。它是分类表的残差桶, 收纳属性缺失、判定模糊或不适用的稿子。这个数越大, 说明这一年能分类的信息越少, 下游那些格内比率就越要小心解读。它是判断分类结构可不可信的关键把手, 和八个有效格加起来须等于可分类留篇总数。

## VAR: n_articles_collab

【变体差分】
本列是合作 (collaboration, P5 主线) 维度下的有效报道计数——统计该 bank-year 内被判定为涉及银行与金融科技合作叙事的报道条数, 是 collab 相关比率 (如 collab_frac) 在 full 轨主口径下的分母基数。它与家族锚点 n_articles 的差别在于把留篇进一步限定到"合作"属性判定为真的子集, 承接 P5 (Chesbrough 开放式创新框架) 的处理域。按 full-only 门控, 以 full 轨核验为准界定合作报道。作为分母, 它保证 collab 比率分子分母同基同域同轨。它有一组三轨对偶列与一组跨文本轨解耦诊断列: n_articles_collab_cm_ctx / _cm_ss (ctx/ss 轨条件计数)、_bothvalid / _disagree / _freerider / _quietworker (D4 跨文本轨 full-vs-ctx 解耦诊断计数, 即同一 LLM 模型在全文轨与实体上下文轨上对合作属性判得是否一致的说做残差信号, 非两个不同厂商模型之间的一致率)。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J; 跨轨解耦诊断亦各自 just-identified。本列不含情感极性, 但其成员身份由 LLM 分类判定决定, 换 LLM 模型会改变落入合作子集的具体文档 (per-model 独立降级), 而 full 留篇总数不变。T=2 试跑下合作报道稀疏属预期, 生产 T=19 充分。

用大白话说, 这一列数的是: 这家银行这一年有几条报道讲的是它和金融科技方合作的事。它是合作类占比的分母, 承接开放式创新那条主线。它另带上下文轨、同句轨两个孪生列, 以及一组衡量同一个大模型看全文和看实体周边这两种读法判得一致不一致的诊断列 (注意是同一模型的两种文本口径打不打架, 不是两个不同大模型比一致)。三条轨、各诊断各算各的, 互为稳健性、不进同一个过度识别检验。换大模型会改动到底是哪几条被算作合作稿, 但全文留篇总数不变。

## VAR: n_articles_collab_bothvalid

【变体差分】
本列是合作维度的跨文本轨 (full vs ctx) 双有效覆盖披露计数——统计该 bank-year 内, 在合作属性判定上全文轨 (full) 与实体上下文轨 (ctx) 两路归一化标签均落在 canonical 白名单 {自主研发, 外部协同} 的报道条数。须强调: 这是同一个 LLM 模型在两个文本口径 (全文 vs 实体邻近上下文) 上都给出可用属性标签的子集, 而非两个不同厂商模型均表态——cell_id 分解只在 full/ctx 两轨进行 (ss 是纯情感轨不产属性标签), 双有效指两轨双双落白名单。它与 n_articles_collab 的差别在于: 后者是合作报道总数, 本列是"两文本轨都给了 canonical 判定"的覆盖子集, 是计算 D4 跨轨分歧率 (disagree/bothvalid) 的有效配对分母, 把说做解耦统计限定在两轨都可比的样本上, 避免用单轨脏标/缺标样本稀释分歧率。源码将本列登记为覆盖披露列。它与 _disagree (两轨均有效但标签相左)、_freerider / _quietworker (分歧的方向分解, 见各自条目) 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J。本列纯计数, 换模型改变落白名单的具体文档 (per-model 独立降级), full 留篇总数不变。T=2 试跑下双有效样本稀疏属预期, 生产 T=19 充分。

用大白话说, 这一列数的是: 在合作这件事上, 同一个大模型分别用"看全文"和"只看实体周边那一段"两种读法都给出了能用的判定 (两种读法都没弃权) 的稿子有几条。注意这是一个模型的两种读法都表态, 不是两个不同大模型都表态。它是算"两种读法打不打架"这个分歧率时的有效配对分母——只有两种读法都表了态的稿子才拿来比一致不一致, 免得用脏标或缺标的稿子把分歧率冲淡。它和分歧列、以及分歧按方向拆出的两个残差列并列, 各算各的, 不塞进同一个过度识别检验。换模型只改动具体是哪几条落进白名单, 全文留篇总数不变。

## VAR: n_articles_collab_cm_ctx

【变体差分】
本列是 n_articles_collab 的 ctx 轨对偶 (后缀 cm_ctx 中 ctx 标明轨道)——在标题 + 实体窗口的上下文轨上统计涉合作叙事的有效报道条数。它与 full 主口径 n_articles_collab 的差别在文本轨道: ctx 轨只保留实体邻近上下文而非全文, 是聚焦实体邻域的条件计数轨。按 full-only 门控铁律, ctx 轨为 conditional-on-full 稳健性/测度轨, 行宇宙是 full 留篇集的子集, per-track 照算不反向扩张。它与 full 主口径及 ss 轨对偶 n_articles_collab_cm_ss 三者各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。此列价值是检验"若只看实体邻近上下文, 合作报道计数是否漂移"。本列成员身份由 LLM 分类在 ctx 轨的判定决定, 换模型改变具体文档 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out, 无 _lg 孪生。T=2 试跑下 ctx 轨合作计数可能零方差退化属预期, 生产 T=19 正常。

用大白话说, 这一列是合作报道数的上下文轨版本: 只看银行和金融科技词附近那一小段上下文, 数有几条算合作稿。它是全文轨主口径的稳健性伴侣, 回答若只盯实体周边、合作报道数会不会漂。它的行范围是全文留篇的子集, 不反过来扩大留篇集, 也不掺进同一个过度识别检验。换大模型会改动具体是哪几条, 但全文留篇总数不变; 小样本下这一轨常没方差, 属正常。

## VAR: n_articles_collab_cm_ss

【变体差分】
本列是 n_articles_collab 的 ss 轨对偶 (后缀 cm_ss 中 ss 标明轨道)——在标题 + 银行∧金融科技同句±N 窗的同句轨上统计涉合作叙事的有效报道条数。它与 full 主口径的差别在文本轨道: ss 轨要求银行与金融科技词句级共现, 是三轨中判定最严的一轨, 语义镜像 ctx 但收窄到同句。回退语义: 无同句共现时 content_ss 退化为全文正文、ss_is_fallback 置真, 与 ctx 共享 n_articles 分母。按 full-only 门控, ss 轨为 conditional-on-full 子集测度轨, 行宇宙是 full 留篇集的子集。它与 full 主口径及 ctx 轨对偶各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。本列成员身份由 LLM 分类在 ss 轨判定决定, 换模型改变具体文档 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out, 无 _lg 孪生。T=2 试跑下 ss 轨合作计数常零方差退化 (同句共现稀疏) 属预期, 生产 T=19 才有充分变异。

用大白话说, 这一列是合作报道数的同句轨版本: 要求银行和金融科技词在同一句里出现才算合作稿, 是三轨里最严的。碰到没有同句共现的稿子, 它退回按全文算并打回退标记, 和上下文轨的处理一致。它是主口径的稳健性伴侣, 各算各的、互为稳健性、不进同一个过度识别检验。同句共现稀疏, 小样本下这一轨经常没方差, 要到生产全量才有足够变化。

## VAR: n_articles_collab_disagree

【变体差分】
本列是合作维度的跨文本轨 (full vs ctx) 分歧诊断计数——统计该 bank-year 内, 同一 LLM 模型的全文轨 (full) 与实体上下文轨 (ctx) 两路均给出 canonical 合作判定但彼此相左 (一轨判自主研发、另一轨判外部协同) 的报道条数, 即源码 disagree = (full != ctx) ∧ both_valid。它是 n_articles_collab_bothvalid 的互补子集: bothvalid 是两轨都落白名单的样本, 本列则是两轨落白名单却不一致的那部分, 两者相除即同一模型在"全文读法"与"实体邻近读法"之间的说做解耦率 (D4 跨轨残差信号), 而非两个厂商模型之间的分歧。它专门量化同一属性在两个文本口径下的不一致——这是 say-do 解耦的直接观测: 全文的整体表态与贴近实体那一小段的局部表态出现落差, 本身即有信息量, 分歧率越高说明该属性对"读多少文本"越敏感。它与 _bothvalid、_freerider、_quietworker 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 它与真正的跨厂商模型 FWER 校正 (走根级 rwolf 模板) 是两回事, 不可混同亦不可并入同一过度识别式。本列纯计数, 换模型改变分歧样本成员身份 (per-model 独立降级)。T=2 试跑下分歧样本稀疏属预期, 生产 T=19 充分。

用大白话说, 这一列数的是: 同一个大模型看全文说一套、只看实体周边那一段又说另一套的稿子有几条 (比如全文看着像自主研发、上下文却更像外部协同)。它是两种读法都表态那批稿子里前后不一致的那部分, 除以双有效数就是"同一模型两种读法的打架率", 也就是说一套做一套的疑似程度。注意这不是两个不同大模型吵架, 而是一个模型换个读法就变卦。这种落差本身就是有用的信号。真正跨不同厂商模型的多重检验校正走根级专门模板, 和这一列不是一回事, 不能塞进同一个过度识别式。

## VAR: n_articles_collab_freerider

【变体差分】
本列是合作维度 D4 跨文本轨解耦的一个方向残差计数 (源码 freerider)——统计该 bank-year 内, 同一 LLM 模型在全文轨 (full) 判为基线类"自主研发"、而在实体上下文轨 (ctx) 判为对照类"外部协同"的报道条数, 即 freerider = (full == 自主研发) ∧ (ctx == 外部协同)。它绝非"参与合作但贡献不对称"之类的合作角色典型学或象限——那是对源码的虚构; freerider 在本项目的确切语义是"说一套做一套"的疑似信号方向之一: 全文口径给出的整体表态与贴近实体那一小段上下文给出的局部表态出现方向性落差。它与 n_articles_collab (合作报道总数) 的差别在于: 后者是水平计数, 本列是分歧计数 (disagree) 按方向拆出的两支之一。它与 _quietworker (相反方向: 全文外部协同、上下文自主研发, 即"做了不说")、_bothvalid、_disagree 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 构造上 freerider + quietworker 恒等于 disagree, 二者互斥, 是分歧的完备方向分解。本列纯计数不含情感极性, 成员身份由 LLM 分类在两轨的判定共同决定, 换模型改变具体文档 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下该方向残差稀疏或为零属预期, 生产 T=19 才充分填充; 与 quietworker 并观可读出跨轨解耦的方向偏斜。

用大白话说, 这一列数的是: 同一个大模型看全文判成"自主研发"、只看实体周边那一段却判成"外部协同"的稿子有几条。它不是什么"搭便车的合作角色"——那是对代码的误读; 它其实是"说一套做一套"疑似信号的一个方向: 整篇的说法和贴着实体那一小段的说法反了向。它和相反方向那一列 (全文外部协同、上下文自主研发, 也就是"做了不说") 配对, 两支加起来正好等于分歧总数, 互不重叠。判定由同一个大模型的两种读法共同决定, 换模型会改动具体是哪几条, 全文留篇总数不变。

## VAR: n_articles_collab_quietworker

【变体差分】
本列是合作维度 D4 跨文本轨解耦的相反方向残差计数 (源码 quietworker)——统计该 bank-year 内, 同一 LLM 模型在全文轨 (full) 判为对照类"外部协同"、而在实体上下文轨 (ctx) 判为基线类"自主研发"的报道条数, 即 quietworker = (full == 外部协同) ∧ (ctx == 自主研发), 与 freerider 方向恰好相反, 是源码白话所谓"做了不说"的疑似信号。须澄清: 它绝非"实质投入但媒体露出少"之类的合作角色典型学——那是对源码的杜撰; quietworker 与 freerider 度量的都是同一个模型两个文本口径 (full vs ctx) 的判定落差方向, 与合作角色、贡献-曝光对称性等构念毫无关系。它与 n_articles_collab 的差别在于: 后者是水平计数, 本列是分歧 (disagree) 按方向拆出的两支之一。它与 _freerider、_bothvalid、_disagree 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 构造上 freerider + quietworker 恒等于 disagree, 二者互斥。本列纯计数不含情感极性, 成员身份由 LLM 分类在两轨的判定共同决定, 换模型改变具体文档 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下该方向残差常稀疏或为零属预期, 生产 T=19 充分。它与合作数量测度构念正交不可互替, 是同一属性跨轨说做一致性的方向观测。

用大白话说, 这一列数的是: 同一个大模型看全文判成"外部协同"、只看实体周边那一段却判成"自主研发"的稿子有几条, 方向和 freerider 那一列正好反过来, 也就是源码说的"做了不说"。它不是什么"默默耕耘的合作角色"——那是对代码的编造; 它和 freerider 一样, 量的都是同一个模型两种读法判得反不反向, 跟合作里谁出力谁露脸没半点关系。它和 freerider 两支加起来正好等于分歧总数, 互不重叠。判定由同一模型的两种读法共同决定, 换模型改动具体篇目、全文留篇总数不变。

## VAR: n_articles_exc

【变体差分】
本列是被排除 (excluded) 报道的计数——统计该 bank-year 内因某排除判据 (如否定过滤、短名歧义过滤、非目标共现等) 而被剔除、未进入有效留篇集的报道条数。它与家族锚点 n_articles 是互补关系: n_articles 是保留下来的有效报道, 本列是被判据挡在门外的报道, 二者相加约等于经初步召回但进入判定的候选总量。它专门量化过滤管线的剔除强度, 是审视留篇门控与共现硬过滤 (stage 13) 严格程度的诊断把手——排除计数偏高说明召回后被判据大量收窄, 关系到样本代表性与潜在选择偏差的评估。判定不对称口径须注意: 银行侧采用否定 + 短名过滤, 金融科技侧采用裸 AC 词表匹配, 因此排除主要发生在银行侧的严格判定。它作为诊断计数各自 just-identified, 不与保留计数并入同一 over-identified Hansen J。本列纯计数不含情感极性, 属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下排除计数依语料而定, 生产 T=19 才反映真实剔除规模。它与 attention/情感测度构念正交, 主要用于数据质量披露与选择偏差讨论 (Siano 和 Wysocki, 2021 强调样本构造透明度)。

用大白话说, 这一列数的是: 这家银行这一年有几条报道被过滤规则挡在门外、没进有效留篇集。它和最终留下来的报道数是一对互补, 加起来大致等于经初筛后进入判定的候选总量。这个数偏高, 说明召回之后被规则大量收窄, 关系到样本代不代表、有没有选择偏差。银行侧判定用了否定和短名过滤, 所以排除主要发生在银行这一侧。它主要用于数据质量披露, 不进主回归的过度识别检验。

## VAR: n_articles_for_ctx_independence

【变体差分】
本列是用于检验 ctx 轨独立性的报道计数分母——统计该 bank-year 内进入"ctx 轨相对 full 轨是否提供独立信息"这一独立性诊断的有效报道条数。它与 n_articles 的差别在于其计数域限定在独立性检验所消费的样本 (即同时具备 full 与 ctx 有效判定、可做轨间比较的文档)。三轨架构下, full 是主留篇轨, ctx/ss 是 conditional-on-full 的稳健性轨, 而"轨间是否真的携带不同信息"需要一个明确的比较样本框, 本列即该框的大小。它作为诊断分母服务于轨间独立性/相关性统计的可靠性评估, 与 n_articles_for_ss_independence (ss 轨对应者) 构成一对。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J; 本列不是把三轨并入一个过度识别式, 恰相反, 它是支撑"三轨须分别 just-identified"这一决策的经验证据分母。本列纯计数不含情感极性, 属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下轨间比较样本稀疏、ctx 轨可能零方差退化属预期, 生产 T=19 才有充分基数评估轨间独立性。

用大白话说, 这一列数的是: 有几条报道能拿来检验上下文轨相对全文轨到底有没有提供新信息。三条轨里全文是主轨, 上下文轨是稳健性伴侣, 但两轨是不是真携带不同信息得有个明确的比较样本框, 这一列就是那个框的大小。它反过来支撑了三轨须各自独立识别这个决策, 而不是把三轨塞进一个过度识别式。小样本下比较样本稀疏、上下文轨常没方差, 属正常。

## VAR: n_articles_for_ss_independence

【变体差分】
本列是用于检验 ss 轨独立性的报道计数分母——统计该 bank-year 内进入"ss 轨相对 full 轨是否提供独立信息"独立性诊断的有效报道条数。它与 n_articles_for_ctx_independence 是并列对偶, 差别仅在所检验的轨道为 ss (标题 + 银行∧金融科技同句±N 窗) 而非 ctx。ss 轨是三轨中判定最严的一轨, 其回退语义镜像 ctx (无同句共现时退化为全文正文), 因此评估 ss 轨独立性时须把回退样本 (ss_is_fallback 为真) 的处理口径讲清, 本列即界定可做 ss-vs-full 比较的有效样本框大小。它作为诊断分母服务于轨间独立性统计的可靠性评估。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J; 本列是支撑"三轨分别 just-identified"决策的经验证据分母而非过度识别工具。本列纯计数不含情感极性, 属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下 ss 轨比较样本常极稀疏 (同句共现稀疏) 属预期, 生产 T=19 才有充分基数评估 ss 轨相对 full 轨的信息独立性。

用大白话说, 这一列数的是: 有几条报道能拿来检验同句轨相对全文轨有没有提供新信息, 是上下文轨那一列的同句版对偶。同句轨最严, 又有全文回退, 所以评估它的独立性时得把回退稿的口径讲清, 这一列就界定了能做同句对全文比较的有效样本框大小。它支撑三轨各自独立识别的决策。同句共现稀疏, 小样本下这个框常常很小, 要到生产全量才够评估。

## VAR: n_articles_indep

【变体差分】
本列是独立 (independent) 报道的计数——统计该 bank-year 内被判定为独立报道 (相对于转载/关联稿而言的原创或独立来源报道) 的条数, 是 indep 相关比率在 full 轨主口径下的分母基数。它与家族锚点 n_articles 的差别在于把留篇进一步限定到"独立性"判定为真的子集。独立报道计数在媒体覆盖研究中用于区分原创信息供给与转载放大——独立来源越多, 该 bank-year 的信息含量越丰富而非同源重复 (与去重敏感性子族的关切互补: 后者剔近似重复, 本列正面刻画独立来源)。它有两个三轨对偶列 n_articles_indep_cm_ctx / _cm_ss。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。按 full-only 门控界定独立报道。本列纯计数, 独立性归属由判定逻辑决定; 属非嵌入 carve-out 无 _lg 孪生。它与 attention 总计数构念相关但不同——n_articles 数全部留篇, 本列只数独立来源。T=2 试跑下独立报道稀疏属预期, 生产 T=19 充分, 呼应财经信息中介独立性对市场感知的影响 (Call, Emett, Maksymov 和 Sharp, 2022)。

用大白话说, 这一列数的是: 这家银行这一年有几条是独立来源的原创报道, 而不是互相转载的同源稿。独立来源越多, 说明这一年关于它的信息越丰富、越不是同一篇稿子反复刷屏。它和去重敏感性那一族正好互补: 那族是把近似重复删掉, 这列是正面数独立来源有多少。它另有上下文轨、同句轨两个孪生列, 三轨各算各的、不进同一个过度识别检验。

## VAR: n_articles_indep_cm_ctx

【变体差分】
本列是 n_articles_indep 的 ctx 轨对偶 (后缀 cm_ctx)——在标题 + 实体窗口的上下文轨上统计独立报道的有效条数。它与 full 主口径 n_articles_indep 的差别在文本轨道: ctx 轨只保留实体邻近上下文而非全文。按 full-only 门控铁律, ctx 轨为 conditional-on-full 稳健性/测度轨, 行宇宙是 full 留篇集的子集, per-track 照算不反向扩张。它与 full 主口径及 ss 轨对偶 n_articles_indep_cm_ss 三者各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。此列价值是检验"若只看实体邻近上下文, 独立报道计数是否漂移"。本列纯计数, 独立性归属由 ctx 轨判定决定; 属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下 ctx 轨独立计数可能零方差退化属预期, 生产 T=19 正常。它与 attention 总计数构念相关但不可互替——数的是 ctx 轨独立来源子集而非全部留篇, 与情感/嵌入测度构念正交。

用大白话说, 这一列是独立报道数的上下文轨版本: 只看实体附近那一小段上下文, 数有几条算独立来源稿。它是全文轨主口径的稳健性伴侣, 回答若只盯实体周边、独立报道数会不会漂。行范围是全文留篇的子集, 不反向扩大留篇集, 也不掺进同一个过度识别检验。小样本下这一轨常没方差, 属正常退化, 生产全量才正常。

## VAR: n_articles_indep_cm_ss

【变体差分】
本列是 n_articles_indep 的 ss 轨对偶 (后缀 cm_ss)——在标题 + 银行∧金融科技同句±N 窗的同句轨上统计独立报道的有效条数。它与 full 主口径的差别在文本轨道: ss 轨要求银行与金融科技词句级共现, 是三轨中判定最严的一轨, 语义镜像 ctx 但收窄到同句。回退语义: 无同句共现时 content_ss 退化为全文正文、ss_is_fallback 置真, 与 ctx 共享 n_articles 分母。按 full-only 门控, ss 轨为 conditional-on-full 子集测度轨, 行宇宙是 full 留篇集的子集。它与 full 主口径及 ctx 轨对偶各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。本列纯计数, 独立性归属由 ss 轨判定决定; 属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下 ss 轨独立计数常零方差退化 (同句共现稀疏) 属预期, 生产 T=19 才有充分变异。它数的是 ss 轨独立来源子集, 与全部留篇计数及情感/嵌入测度构念正交, 不可互替。

用大白话说, 这一列是独立报道数的同句轨版本: 要求银行和金融科技词同句出现才算, 是三轨里最严的一条, 碰到没同句共现就退回按全文算并打回退标记。它是主口径的稳健性伴侣, 各算各的、互为稳健性、不进同一个过度识别检验。同句共现稀疏, 小样本下这一轨常没方差, 要到生产全量才有足够变化。它数的是同句轨里的独立来源子集, 和全部留篇数是两回事。

## VAR: n_articles_locus_bothvalid

【变体差分】
本列是创新位置 (locus, P4 主线, Gomber 框架) 维度的跨文本轨 (full vs ctx) 双有效覆盖披露计数——统计该 bank-year 内, 在 locus 属性判定上全文轨 (full) 与实体上下文轨 (ctx) 两路归一化标签均落在 canonical 白名单 {底层技术, 应用场景} 的报道条数。locus 刻画金融科技创新落在底层技术层还是应用场景层的定位。须强调: 这是同一个 LLM 模型在两个文本口径上都给出可用属性标签的子集, 不是两个不同厂商模型均表态。它与合作维度的 _bothvalid 是平行结构, 差别仅在所诊断的分类维度为 locus 而非 collab。它是计算 locus 维度 D4 跨轨分歧率的有效配对分母, 与 _disagree (两轨均有效但标签相左)、_freerider / _quietworker (分歧的方向分解, 非角色典型) 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 真正跨厂商模型的 FWER 走根级 rwolf 模板, 与本列的跨轨口径不可混同。本列纯计数, 换模型改变落白名单成员身份 (per-model 独立降级)。它是评估 P4 locus 属性在全文口径与实体上下文口径间说做一致性的覆盖分母。T=2 试跑下双有效样本稀疏属预期, 生产 T=19 充分。它与 locus 水平测度构念正交, 专用于跨轨解耦统计而非水平估计。

用大白话说, 这一列数的是: 在创新落在底层技术还是应用场景这件事 (定位) 上, 同一个大模型用"看全文"和"只看实体周边"两种读法都给出能用判定的稿子有几条, 是算这个维度"两种读法打不打架"分歧率的有效配对分母。注意是一个模型的两种读法都表态, 不是两个不同大模型都表态。定位判定本就比二元合作判定更细腻, 所以这个有效配对框尤其要紧。它和分歧列、以及分歧按方向拆出的两支并列, 各算各的, 不塞进同一个过度识别检验。

## VAR: n_articles_locus_disagree

【变体差分】
本列是 locus 维度的跨文本轨 (full vs ctx) 分歧诊断计数——统计该 bank-year 内, 同一 LLM 模型的全文轨 (full) 与实体上下文轨 (ctx) 两路均给出 canonical locus 判定但彼此相左 (一轨判底层技术、另一轨判应用场景) 的报道条数, 即 disagree = (full != ctx) ∧ both_valid。它是 n_articles_locus_bothvalid 的互补子集, 两者相除即同一模型在"全文读法"与"实体邻近读法"之间的 locus 说做解耦率 (D4 跨轨残差), 而非两个厂商模型之间的分歧。它专门量化创新位置属性在两个文本口径下的不一致——底层技术与应用场景的界线本就带梯度, 全文的整体定位与贴近实体那一小段的局部定位出现落差本身即有信息量, 分歧率越高说明该属性对"读多少文本"越敏感。它与 _bothvalid、_freerider、_quietworker 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 真正跨厂商模型的 FWER 校正走根级 rwolf 模板, 与本列不是一回事, 不可并入过度识别式。本列纯计数, 换模型改变分歧样本成员身份 (per-model 独立降级)。T=2 试跑下分歧样本稀疏属预期, 生产 T=19 充分。属非嵌入 carve-out 无 _lg 孪生, 与 locus 水平测度构念正交, 不可互替或并入同一识别式。

用大白话说, 这一列数的是: 同一个大模型看全文把创新定位判成"底层技术"、只看实体周边那一段又判成"应用场景"的稿子有几条 (或反过来), 是两种读法都表态那批稿子里前后不一致的那部分, 除以双有效数就是"同一模型两种读法的打架率"。底层技术和应用场景的界线本就带梯度, 换个读法容易变卦, 分歧率偏高。注意这不是两个不同大模型吵架, 而是一个模型换个读法就变。真正跨不同厂商模型的多重检验校正走根级专门模板, 和这个诊断数不是一回事。

## VAR: n_articles_locus_freerider

【变体差分】
本列是 locus 维度 D4 跨文本轨解耦的一个方向残差计数 (源码 freerider)——统计该 bank-year 内, 同一 LLM 模型在全文轨 (full) 判为基线类"底层技术"、而在实体上下文轨 (ctx) 判为对照类"应用场景"的报道条数, 即 freerider = (full == 底层技术) ∧ (ctx == 应用场景)。须澄清: 它绝非"某种不对称参与"之类的 locus 角色典型学或象限——那是对源码的虚构; freerider 在本项目的确切语义是"说一套做一套"疑似信号的一个方向: 全文口径的整体定位与贴近实体那一小段上下文的局部定位出现方向性落差。它与合作、subst 维度的同名残差列是三个独立分类维度下的平行结构 (须严格区分, 但都是同一 full-vs-ctx 跨轨口径, 非跨模型)。它与 _quietworker (相反方向: 全文应用场景、上下文底层技术)、_bothvalid、_disagree 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 构造上 freerider + quietworker 恒等于 disagree, 二者互斥, 是分歧的完备方向分解。本列纯计数不含情感极性, 成员身份由 LLM 分类在两轨的判定共同决定, 换模型改变具体文档 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下该方向残差稀疏或为零属预期, 生产 T=19 才充分填充; 与 quietworker 并观读出 locus 跨轨解耦的方向偏斜。

用大白话说, 这一列数的是: 同一个大模型看全文把定位判成"底层技术"、只看实体周边那一段却判成"应用场景"的稿子有几条。它不是什么"搭便车的定位角色"——那是对代码的误读; 它其实是"说一套做一套"疑似信号的一个方向: 整篇的定位说法和贴着实体那一小段的定位说法反了向。它和合作、实质维度的同名残差列是三套独立维度下的平行结构, 须分清, 但都是同一个模型两种读法的落差, 不是两个模型比。它和相反方向那一列配对, 两支加起来正好等于分歧总数。换模型改动具体篇目, 全文留篇总数不变。

## VAR: n_articles_locus_quietworker

【变体差分】
本列是 locus 维度 D4 跨文本轨解耦的相反方向残差计数 (源码 quietworker)——统计该 bank-year 内, 同一 LLM 模型在全文轨 (full) 判为对照类"应用场景"、而在实体上下文轨 (ctx) 判为基线类"底层技术"的报道条数, 即 quietworker = (full == 应用场景) ∧ (ctx == 底层技术), 与 freerider 方向恰好相反, 是源码白话所谓"做了不说"的方向。须澄清: 它绝非"实质定位清晰但媒体露出少"之类的角色典型学——那是对源码的杜撰; quietworker 与 freerider 度量的都是同一模型两个文本口径 (full vs ctx) 的 locus 判定落差方向, 与创新位置角色、曝光度等构念无关。它与 n_articles_locus_freerider 差别仅在落差方向, 本列专计相反方向。它与 _freerider、_bothvalid、_disagree 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 构造上 freerider + quietworker 恒等于 disagree, 二者互斥。本列纯计数不含情感极性, 成员身份由 LLM 分类在两轨的判定共同决定, 换模型改变具体文档 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下该方向残差常稀疏或为零属预期, 生产 T=19 充分。它与 locus 水平/数量测度构念正交, 不可互替或并入同一识别式; 与合作、subst 维度的同名列虽都是同一 full-vs-ctx 跨轨口径, 但属三个独立分类维度, 须严格区分。

用大白话说, 这一列数的是: 同一个大模型看全文把定位判成"应用场景"、只看实体周边那一段却判成"底层技术"的稿子有几条, 方向和 freerider 那一列正好反过来, 也就是源码说的"做了不说"。它不是什么"默默耕耘的定位角色"——那是对代码的编造; 它和 freerider 一样, 量的都是同一个模型两种读法判得反不反向, 跟定位叙事里谁露脸没关系。它和 freerider 两支加起来正好等于分歧总数。它和合作、实质维度的同名列须分清, 都是同一模型两种读法的落差, 换模型改动具体篇目、定位总数不变。

## VAR: n_articles_sub

【变体差分】
本列是实质性 (substantive) 维度下的有效报道计数——统计该 bank-year 内被判定为实质性 (相对象征性 symbolic) 金融科技报道的条数, 是 sub 相关比率在 full 轨主口径下的分母基数。它承接 P3 (Westphal 和 Zajac 实质/象征二分框架) 的处理域: 实质性报道指涉及真实资源投入、具体技术落地的叙事, 象征性报道指偏公关姿态、口号式表态的叙事。它与家族锚点 n_articles 的差别在于把留篇限定到实质性判定为真的子集。它有两个三轨对偶列 n_articles_sub_sc_ctx / _ss_ss。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。按 full-only 门控界定实质性报道。本列纯计数, 实质性归属由 LLM 分类判定, 换模型改变子集成员身份 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out 无 _lg 孪生。它与 n_articles_symb (象征性报道计数) 构成一对互补构念, 二者之和约等于可判定实质/象征的报道数, 而非全部留篇。T=2 试跑下实质性报道稀疏属预期, 生产 T=19 充分。

用大白话说, 这一列数的是: 这家银行这一年有几条是实打实讲金融科技落地投入的实质性报道, 而不是喊口号摆姿态的象征性报道。它承接实质对象征那套框架, 是实质类占比的分母, 另有上下文轨、同句轨两个孪生列。它和象征性报道数是一对互补, 两者一比就看出这家银行的金融科技叙事是偏实干还是偏姿态。三轨各算各的、不进同一个过度识别检验; 换模型改动具体篇目、全文留篇总数不变。

## VAR: n_articles_sub_sc_ctx

【变体差分】
本列是 n_articles_sub 的 ctx 轨对偶 (后缀 sc_ctx, ctx 标明轨道)——在标题 + 实体窗口的上下文轨上统计实质性报道的有效条数。它与 full 主口径 n_articles_sub 的差别在文本轨道: ctx 轨只保留实体邻近上下文而非全文。按 full-only 门控铁律, ctx 轨为 conditional-on-full 稳健性/测度轨, 行宇宙是 full 留篇集的子集, per-track 照算不反向扩张。它与 full 主口径及 ss 轨对偶 n_articles_sub_ss_ss 三者各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。此列检验"若只看实体邻近上下文, 实质性报道计数是否漂移"。本列纯计数, 实质性归属由 ctx 轨判定决定, 换模型改变子集成员身份 (per-model 独立降级)。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下 ctx 轨实质计数可能零方差退化属预期, 生产 T=19 正常。它数的是 ctx 轨实质性子集, 与全部留篇计数及象征性对偶列构念相关但不可互替, 与情感/嵌入测度正交。

用大白话说, 这一列是实质性报道数的上下文轨版本: 只看实体附近那一小段上下文, 数有几条算实质性稿。它是全文轨主口径的稳健性伴侣, 回答若只盯实体周边、实质报道数会不会漂。行范围是全文留篇的子集, 不反向扩大留篇集, 也不进同一个过度识别检验。小样本下这一轨常没方差, 属正常退化, 生产全量才正常。

## VAR: n_articles_sub_ss_ss

【变体差分】
本列是 n_articles_sub 的 ss 轨对偶 (后缀 ss_ss, 后一 ss 标明同句轨)——在标题 + 银行∧金融科技同句±N 窗的同句轨上统计实质性报道的有效条数。它与 full 主口径的差别在文本轨道: ss 轨要求银行与金融科技词句级共现, 是三轨中判定最严的一轨, 语义镜像 ctx 但收窄到同句。回退语义: 无同句共现时 content_ss 退化为全文正文、ss_is_fallback 置真, 与 ctx 共享 n_articles 分母。按 full-only 门控, ss 轨为 conditional-on-full 子集测度轨, 行宇宙是 full 留篇集的子集。它与 full 主口径及 ctx 轨对偶各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。本列纯计数, 实质性归属由 ss 轨判定决定, 换模型改变子集成员身份 (per-model 独立降级)。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下 ss 轨实质计数常零方差退化 (同句共现稀疏) 属预期, 生产 T=19 才有充分变异。它数的是 ss 轨实质性子集, 与全部留篇计数及情感/嵌入测度构念正交, 不可互替。

用大白话说, 这一列是实质性报道数的同句轨版本: 要求银行和金融科技词同句出现才算, 是三轨里最严的, 碰到没同句共现就退回按全文算并打回退标记。它是主口径的稳健性伴侣, 各算各的、互为稳健性、不进同一个过度识别检验。同句共现稀疏, 小样本下这一轨常没方差, 要到生产全量才有变化。它数的是同句轨里的实质性子集。

## VAR: n_articles_subst_bothvalid

【变体差分】
本列是实质性 (substantive, 前缀 subst) 维度的跨文本轨 (full vs ctx) 双有效覆盖披露计数——统计该 bank-year 内, 在实质/象征属性判定上全文轨 (full) 与实体上下文轨 (ctx) 两路归一化标签均落在 canonical 白名单 {实质性, 象征性} 的报道条数。须强调: 这是同一个 LLM 模型在两个文本口径上都给出可用属性标签的子集, 不是两个不同厂商模型均表态。它与 n_articles_sub (实质性报道总数) 的差别在于: 后者是水平计数, 本列是"两文本轨都落白名单"的覆盖子集, 是计算 substance 维度 D4 跨轨分歧率的有效配对分母, 服务于跨轨解耦统计而非水平估计。它与合作、locus 维度的同名 _bothvalid 是平行结构, 差别在所诊断维度为 substance。它与 _disagree、_freerider、_quietworker 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 真正跨厂商模型的 FWER 走根级 rwolf 模板, 与本列的跨轨口径不可混同。本列纯计数, 换模型改变落白名单成员身份 (per-model 独立降级)。它是评估 P3 substance 属性在全文口径与实体上下文口径间说做一致性的覆盖分母。T=2 试跑下双有效样本稀疏属预期, 生产 T=19 充分。属非嵌入 carve-out 无 _lg 孪生。

用大白话说, 这一列数的是: 在实质还是象征这件事上, 同一个大模型用"看全文"和"只看实体周边"两种读法都给出能用判定的稿子有几条, 是算这个维度"两种读法打不打架"分歧率的有效配对分母。注意是一个模型的两种读法都表态, 不是两个不同大模型都表态。它和实质报道总数的区别在于——那个是水平数量, 这个是两种读法都落白名单的配对子集, 专门服务跨轨解耦统计。它和分歧列、以及分歧按方向拆出的两支并列, 各算各的, 不塞进同一个过度识别检验。

## VAR: n_articles_subst_disagree

【变体差分】
本列是 substance 维度的跨文本轨 (full vs ctx) 分歧诊断计数——统计该 bank-year 内, 同一 LLM 模型的全文轨 (full) 与实体上下文轨 (ctx) 两路均给出 canonical 判定但彼此相左 (一轨判实质性、另一轨判象征性) 的报道条数, 即 disagree = (full != ctx) ∧ both_valid。它是 n_articles_subst_bothvalid 的互补子集, 两者相除即同一模型在"全文读法"与"实体邻近读法"之间的实质/象征说做解耦率 (D4 跨轨残差), 而非两个厂商模型之间的分歧。它专门量化实质与象征属性在两个文本口径下的不一致——实质与象征的边界带主观性且高度依赖读取多少文本, 全文口径下像实质投入、贴近实体那一小段却像象征表态 (或反之) 的落差本身即是"说一套做一套"的直接观测。它与 _bothvalid、_freerider、_quietworker 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 真正跨厂商模型的 FWER 校正走根级 rwolf 模板, 与本列不是一回事, 不可并入过度识别式。本列纯计数, 换模型改变分歧样本成员身份 (per-model 独立降级)。否定/程度等语言学规则的取舍会影响细粒度实质/象征判定进而影响跨轨落差 (Punetha 和 Jain, 2025)。T=2 试跑下分歧样本稀疏属预期, 生产 T=19 充分。属非嵌入 carve-out 无 _lg 孪生, 与 substance 水平测度构念正交不可互替。

用大白话说, 这一列数的是: 同一个大模型看全文判成"实质性"、只看实体周边那一段又判成"象征性"的稿子有几条 (或反过来), 是两种读法都表态那批稿子里前后不一致的那部分, 除以双有效数就是"同一模型两种读法的打架率"。实质和象征的界线本就主观、又特别看读多少文字, 换个读法容易变卦。注意这不是两个不同大模型吵架, 而是一个模型换个读法就变。真正跨不同厂商模型的多重检验校正走根级专门模板, 和这个诊断数不是一回事。

## VAR: n_articles_subst_freerider

【变体差分】
本列是 substance 维度 D4 跨文本轨解耦的一个方向残差计数 (源码 freerider)——统计该 bank-year 内, 同一 LLM 模型在全文轨 (full) 判为基线类"实质性"、而在实体上下文轨 (ctx) 判为对照类"象征性"的报道条数, 即 freerider = (full == 实质性) ∧ (ctx == 象征性)。须澄清: 它绝非"某种贡献-曝光不对称"之类的 substance 角色典型学或象限——那是对源码的虚构; freerider 在本项目的确切语义是"说一套做一套"疑似信号的一个方向: 全文口径读来像实质投入、贴近实体那一小段上下文却像象征表态。它与合作、locus 维度的同名残差列是三个独立分类维度下的平行结构 (须严格区分, 但都是同一 full-vs-ctx 跨轨口径, 非跨模型)。它与 substance 的 _quietworker (相反方向: 全文象征性、上下文实质性)、_bothvalid、_disagree 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 构造上 freerider + quietworker 恒等于 disagree, 二者互斥, 是分歧的完备方向分解。本列纯计数不含情感极性, 成员身份由 LLM 分类在两轨的判定共同决定, 换模型改变具体文档 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下该方向残差稀疏或为零属预期, 生产 T=19 才充分填充; 与 quietworker 并观读出 substance 跨轨解耦方向偏斜。

用大白话说, 这一列数的是: 同一个大模型看全文把稿子判成"实质性"、只看实体周边那一段却判成"象征性"的稿子有几条。它不是什么"搭便车的实质角色"——那是对代码的误读; 它其实是"说一套做一套"疑似信号的一个方向: 整篇读着像实打实投入、贴着实体那一小段却像喊口号。它和合作、定位维度的同名残差列是三套独立维度下的平行结构, 须分清, 但都是同一个模型两种读法的落差, 不是两个模型比。它和相反方向那一列配对, 两支加起来正好等于分歧总数。换模型改动具体篇目, 全文留篇总数不变。

## VAR: n_articles_subst_quietworker

【变体差分】
本列是 substance 维度 D4 跨文本轨解耦的相反方向残差计数 (源码 quietworker)——统计该 bank-year 内, 同一 LLM 模型在全文轨 (full) 判为对照类"象征性"、而在实体上下文轨 (ctx) 判为基线类"实质性"的报道条数, 即 quietworker = (full == 象征性) ∧ (ctx == 实质性), 与 freerider 方向恰好相反, 是源码白话所谓"做了不说"的方向。须澄清: 它绝非"真实投入但媒体露出少"之类的角色典型学——那是对源码的杜撰; quietworker 与 freerider 度量的都是同一模型两个文本口径 (full vs ctx) 的实质/象征判定落差方向, 与实质叙事角色、贡献-曝光对称性等构念无关。它与 _freerider 差别仅在落差方向, 本列专计相反方向。它与 _freerider、_bothvalid、_disagree 并列, 各自 just-identified, 严禁混进同一 over-identified Hansen J; 构造上 freerider + quietworker 恒等于 disagree, 二者互斥。本列纯计数不含情感极性, 成员身份由 LLM 分类在两轨的判定共同决定, 换模型改变具体文档 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下该方向残差常稀疏或为零属预期, 生产 T=19 充分。它与 substance 水平/数量测度构念正交, 不可互替或并入同一识别式; 与合作、locus 维度的同名列虽都是同一 full-vs-ctx 跨轨口径, 但属三个独立分类维度, 须严格区分。

用大白话说, 这一列数的是: 同一个大模型看全文把稿子判成"象征性"、只看实体周边那一段却判成"实质性"的稿子有几条, 方向和 freerider 那一列正好反过来, 也就是源码说的"做了不说"。它不是什么"默默耕耘的实质角色"——那是对代码的编造; 它和 freerider 一样, 量的都是同一个模型两种读法判得反不反向, 跟实质叙事里谁露脸没关系。它和 freerider 两支加起来正好等于分歧总数。它和合作、定位维度的同名列须分清, 都是同一模型两种读法的落差, 换模型改动具体篇目、实质总数不变。

## VAR: n_articles_symb

【变体差分】
本列是象征性 (symbolic) 维度下的有效报道计数——统计该 bank-year 内被判定为象征性 (相对实质性 substantive) 金融科技报道的条数, 是 symb 相关比率在 full 轨主口径下的分母基数。它是 n_articles_sub (实质性) 的构念对偶, 同属 P3 (Westphal 和 Zajac 实质/象征二分) 框架: 象征性报道指偏公关姿态、口号式表态而缺乏具体资源投入的叙事。它与家族锚点 n_articles 的差别在于把留篇限定到象征性判定为真的子集。它有两个三轨对偶列 n_articles_symb_sc_ctx / _ss_ss。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。按 full-only 门控界定象征性报道。本列纯计数, 象征性归属由 LLM 分类判定, 换模型改变子集成员身份 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out 无 _lg 孪生。它与 n_articles_sub 之和约等于可判定实质/象征的报道数; 二者比值刻画银行金融科技叙事的"实干-姿态"结构, 是 P3 的核心描述量。T=2 试跑下象征性报道稀疏属预期, 生产 T=19 充分。

用大白话说, 这一列数的是: 这家银行这一年有几条是喊口号摆姿态、缺乏具体投入的象征性金融科技报道。它是实质性报道数的对偶, 同属实质对象征那套框架, 是象征类占比的分母, 另有上下文轨、同句轨两个孪生列。它和实质性报道数一比, 就看出这家银行的金融科技叙事到底是干活多还是表态多。三轨各算各的、不进同一个过度识别检验; 换模型改动具体篇目、全文留篇总数不变。

## VAR: n_articles_symb_sc_ctx

【变体差分】
本列是 n_articles_symb 的 ctx 轨对偶 (后缀 sc_ctx)——在标题 + 实体窗口的上下文轨上统计象征性报道的有效条数。它与 full 主口径 n_articles_symb 的差别在文本轨道: ctx 轨只保留实体邻近上下文而非全文。按 full-only 门控铁律, ctx 轨为 conditional-on-full 稳健性/测度轨, 行宇宙是 full 留篇集的子集, per-track 照算不反向扩张。它与 full 主口径及 ss 轨对偶 n_articles_symb_ss_ss 三者各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。此列检验"若只看实体邻近上下文, 象征性报道计数是否漂移"。本列纯计数, 象征性归属由 ctx 轨判定决定, 换模型改变子集成员身份 (per-model 独立降级)。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下 ctx 轨象征计数可能零方差退化属预期, 生产 T=19 正常。它数的是 ctx 轨象征性子集, 与全部留篇计数及实质性对偶列构念相关但不可互替, 与情感/嵌入测度正交。

用大白话说, 这一列是象征性报道数的上下文轨版本: 只看实体附近那一小段上下文, 数有几条算象征性稿。它是全文轨主口径的稳健性伴侣, 回答若只盯实体周边、象征报道数会不会漂。行范围是全文留篇的子集, 不反向扩大留篇集, 也不进同一个过度识别检验。小样本下这一轨常没方差, 属正常退化, 生产全量才正常。

## VAR: n_articles_symb_ss_ss

【变体差分】
本列是 n_articles_symb 的 ss 轨对偶 (后缀 ss_ss, 后一 ss 标明同句轨)——在标题 + 银行∧金融科技同句±N 窗的同句轨上统计象征性报道的有效条数。它与 full 主口径的差别在文本轨道: ss 轨要求银行与金融科技词句级共现, 是三轨中判定最严的一轨, 语义镜像 ctx 但收窄到同句。回退语义: 无同句共现时 content_ss 退化为全文正文、ss_is_fallback 置真, 与 ctx 共享 n_articles 分母。按 full-only 门控, ss 轨为 conditional-on-full 子集测度轨, 行宇宙是 full 留篇集的子集。它与 full 主口径及 ctx 轨对偶各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。本列纯计数, 象征性归属由 ss 轨判定决定, 换模型改变子集成员身份 (per-model 独立降级)。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下 ss 轨象征计数常零方差退化 (同句共现稀疏) 属预期, 生产 T=19 才有充分变异。它数的是 ss 轨象征性子集, 与全部留篇计数及情感/嵌入测度构念正交, 不可互替。

用大白话说, 这一列是象征性报道数的同句轨版本: 要求银行和金融科技词同句出现才算, 是三轨里最严的, 碰到没同句共现就退回按全文算并打回退标记。它是主口径的稳健性伴侣, 各算各的、互为稳健性、不进同一个过度识别检验。同句共现稀疏, 小样本下这一轨常没方差, 要到生产全量才有变化。它数的是同句轨里的象征性子集。

## VAR: n_articles_tech

【变体差分】
本列是技术 (technology) 维度下的有效报道计数——统计该 bank-year 内被判定为技术导向金融科技报道的条数, 是 tech 相关比率在 full 轨主口径下的分母基数。它承接技术属性判定的处理域: 技术性报道指聚焦具体技术 (如区块链、人工智能、云计算等) 落地应用的叙事, 区别于纯业务或姿态性报道。它与家族锚点 n_articles 的差别在于把留篇限定到技术判定为真的子集。它有两个三轨对偶列 n_articles_tech_lc_ctx / _ls_ss。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。按 full-only 门控界定技术报道。本列纯计数, 技术归属由 LLM 分类判定, 换模型改变子集成员身份 (per-model 独立降级), full 留篇总数不变。属非嵌入 carve-out 无 _lg 孪生。技术报道计数刻画银行金融科技叙事的技术含量密度, 与银行文本量作风险/创新暴露代理的思路一致 (Anastasiou, Katsafados 和 Tzomakas, 2026)。T=2 试跑下技术报道稀疏属预期, 生产 T=19 充分。

用大白话说, 这一列数的是: 这家银行这一年有几条报道是真讲具体技术 (区块链、人工智能、云计算之类) 落地的技术型金融科技稿。它刻画这家银行金融科技叙事里的技术含量密度, 是技术类占比的分母, 另有上下文轨、同句轨两个孪生列。三轨各算各的、不进同一个过度识别检验; 换模型改动具体篇目、全文留篇总数不变。报道里的技术含量, 也是把银行文本量当创新暴露代理的一条思路。

## VAR: n_articles_tech_lc_ctx

【变体差分】
本列是 n_articles_tech 的 ctx 轨对偶 (后缀 lc_ctx, ctx 标明轨道)——在标题 + 实体窗口的上下文轨上统计技术导向报道的有效条数。它与 full 主口径 n_articles_tech 的差别在文本轨道: ctx 轨只保留实体邻近上下文而非全文。按 full-only 门控铁律, ctx 轨为 conditional-on-full 稳健性/测度轨, 行宇宙是 full 留篇集的子集, per-track 照算不反向扩张。它与 full 主口径及 ss 轨对偶 n_articles_tech_ls_ss 三者各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。此列检验"若只看实体邻近上下文, 技术报道计数是否漂移"。本列纯计数, 技术归属由 ctx 轨判定决定, 换模型改变子集成员身份 (per-model 独立降级)。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下 ctx 轨技术计数可能零方差退化属预期, 生产 T=19 正常。它数的是 ctx 轨技术性子集, 与全部留篇计数及情感/嵌入测度构念正交, 不可互替。

用大白话说, 这一列是技术型报道数的上下文轨版本: 只看实体附近那一小段上下文, 数有几条算技术稿。它是全文轨主口径的稳健性伴侣, 回答若只盯实体周边、技术报道数会不会漂。行范围是全文留篇的子集, 不反向扩大留篇集, 也不进同一个过度识别检验。小样本下这一轨常没方差, 属正常退化, 生产全量才正常。

## VAR: n_articles_tech_ls_ss

【变体差分】
本列是 n_articles_tech 的 ss 轨对偶 (后缀 ls_ss, ss 标明同句轨)——在标题 + 银行∧金融科技同句±N 窗的同句轨上统计技术导向报道的有效条数。它与 full 主口径的差别在文本轨道: ss 轨要求银行与金融科技词句级共现, 是三轨中判定最严的一轨, 语义镜像 ctx 但收窄到同句。回退语义: 无同句共现时 content_ss 退化为全文正文、ss_is_fallback 置真, 与 ctx 共享 n_articles 分母。按 full-only 门控, ss 轨为 conditional-on-full 子集测度轨, 行宇宙是 full 留篇集的子集。它与 full 主口径及 ctx 轨对偶各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J。本列纯计数, 技术归属由 ss 轨判定决定, 换模型改变子集成员身份 (per-model 独立降级)。属非嵌入 carve-out 无 _lg 孪生。T=2 试跑下 ss 轨技术计数常零方差退化 (同句共现稀疏) 属预期, 生产 T=19 才有充分变异。它数的是 ss 轨技术性子集, 与全部留篇计数及情感/嵌入测度构念正交, 不可互替。

用大白话说, 这一列是技术型报道数的同句轨版本: 要求银行和金融科技词同句出现才算, 是三轨里最严的, 碰到没同句共现就退回按全文算并打回退标记。它是主口径的稳健性伴侣, 各算各的、互为稳健性、不进同一个过度识别检验。同句共现稀疏, 小样本下这一轨常没方差, 要到生产全量才有变化。它数的是同句轨里的技术型子集。

## VAR: n_fintech_articles

【变体差分】
本列是金融科技报道的计数——统计该 bank-year 内被判定为金融科技相关的报道条数, 是 fintech_share 的分子基数。它与家族锚点 n_articles 的差别在于: n_articles 数全部留篇 (银行报道分母基数), 本列只数其中金融科技相关的子集, 二者相除即该行的金融科技新闻占比。分母来源须精确区分 (见项目 fintech_share 分母口径): fintech_share 的分母由 40_article_bank_level 去重 (ft 部分) 与 12_fintech_news_full 减面板后去重 (NF 部分) 合成, 而 12_*_full 是过滤前全量, 不可误判为分母。本列作为分子, 直接度量银行金融科技媒体曝光的绝对规模, 是 P2 attention 主线的原始信号之一, 与以新闻分析量做预测的思路一致 (Bodilsen 和 Lunde, 2025; Anastasiou, Katsafados 和 Tzomakas, 2026)。它遵循 full-only 门控界定金融科技报道。本列纯计数不含情感极性, 金融科技归属由金融科技识别 (stage 12, 金融科技侧裸 AC 607 词匹配) 决定, 而非情感模型, 因此换情感/嵌入模型不改本列。属非嵌入 carve-out 无 _lg 孪生。它与去重敏感性子族的 n_ft_articles_<v> 是同一构念在不同去重变体下的对偶——本列取生产锚点口径, 后者取更严去重变体口径。T=2 试跑下计数稀疏属预期, 生产 T=19 充分。

用大白话说, 这一列数的是: 这家银行这一年被认定为金融科技相关的报道有几条, 是金融科技新闻占比的分子。它和全部留篇报道数的区别在于——那个是分母底盘, 这个只数其中和金融科技沾边的那部分。要特别注意占比的分母不是过滤前的全量, 别把过滤前那份数据误当分母。它由金融科技识别环节决定归属, 换情感模型不影响它。它和去重敏感性那族的金融科技分子是同一构念在不同去重狠度下的对偶, 这一列取的是生产口径。

## VAR: n_ft_articles_j70w10

【变体差分】
本列是去重敏感性子族的"金融科技新闻"分子之一, 变体参数 j70w10 (Jaccard 阈值 0.70 × 10 工作日窗口, 双向最严格)。它与 n_fintech_articles (生产锚点 j80w5 口径的金融科技报道计数) 的差别在于去重口径: 本列在更严去重扰动 (更低相似度阈值 + 更长转载窗) 下重新统计存活的金融科技报道数, 是 attention_pct 类比率在该变体下的分子 N_ft。verified 域门控须精确: 自 2026-06-13 panel-universe-consistency-audit 起, 本子族的金融科技分子源经 (docid, target_bank) semi-join 收敛到 stage-21 verified 集, 故 N_ft = (verified ∩ 变体存活), 与全 docid 域的去重存活率诊断 (sidecar 的 surviving_articles/retained_share) 不同域, 勿混读。它与同变体的分母 n_all_articles_j70w10 (全银行新闻, 未 verified 门控) 相除即该变体 attention_pct。单调性不变量: N_ft(变体) ≤ N_ft(生产)。铁律: 与同族三分子各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 用法为代入主回归验系数稳健 (MacKinnon 和 Webb, 2017)。受保守下界与跨子集近重复盲区两局限约束, T=2 试跑高相关属预期平凡结果。

用大白话说, 这一列数的是: 把去重刀拧到最狠 (相似度七成、十天窗) 之后, 这家银行这一年还剩多少条金融科技报道, 是那个变体下关注度占比的分子。要点是分子这边经过了核验域门控——只数既通过第二十一阶段核验、又在这个更严变体里存活的稿子, 和旁车里那个全口径去重存活率是两码事, 别读串。存活分子一定不超过生产口径。用途是代进主回归验证结论对去重狠度稳不稳, 不能拿试跑高相关自我安慰。

## VAR: n_ft_articles_j70w5

【变体差分】
本列是去重敏感性金融科技分子, 变体参数 j70w5 (Jaccard 阈值 0.70 × 5 工作日窗口)。与 j70w10 共享最低相似度阈值 0.70 但采用较短 5 工作日窗, 故剔除量介于生产锚点与 j70w10 之间。它在更严去重扰动下统计存活的金融科技报道数, 作为该变体 attention_pct 的分子 N_ft。verified 域门控同族: N_ft = (verified ∩ 变体存活), 经 (docid, target_bank) semi-join 收敛到 stage-21 verified 集, 与 sidecar 全 docid 域存活率诊断不同域, 勿混读。它与同变体分母 n_all_articles_j70w5 相除即该变体 attention_pct。此列把"相似度阈值"单独下调一格 (0.80→0.70) 而窗口不变, 与 j75w5 一起构成固定 5 日窗下的相似度梯子。单调性不变量: N_ft(变体) ≤ N_ft(生产)。铁律: 与同族三分子各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 用法为代入主回归验系数稳健 (List, Shaikh 和 Vayalinkal, 2023 的族内多重检验立场适用)。受保守下界与跨子集盲区两局限约束, T=2 试跑高相关属低剔除率预期平凡结果, 非充分稳健性证据。

用大白话说, 这一列数的是: 把相似度门槛松到七成、窗口保持五天之后, 还剩多少条金融科技报道, 是那个变体下占比的分子。删的稿子比生产口径多、又比十天窗那个少, 卡在中间。它同样经核验域门控 (只数核验过又在这个变体里存活的), 和旁车全口径存活率不同域。它和相似度七成半那个变体一起, 描出结论对相似度门槛敏不敏感的一条梯子。存活分子不超过生产口径, 用途是代进主回归验稳健。

## VAR: n_ft_articles_j75w5

【变体差分】
本列是去重敏感性金融科技分子, 变体参数 j75w5 (Jaccard 阈值 0.75 × 5 工作日窗口), 是最接近生产锚点 j80w5 的轻扰动臂——仅把相似度阈值由 0.80 微降至 0.75 而窗口不变。它在该轻扰动去重下统计存活的金融科技报道数, 作为该变体 attention_pct 的分子 N_ft。verified 域门控同族: N_ft = (verified ∩ 变体存活), 经 (docid, target_bank) semi-join 收敛到 stage-21 verified 集, 与 sidecar 全 docid 域存活率诊断不同域, 勿混读。它与同变体分母 n_all_articles_j75w5 相除即该变体 attention_pct。它与 j70w5 及生产 j80w5 在固定 5 日窗下沿相似度 0.80→0.75→0.70 单调放松, 存活分子单调递减。因扰动最小, 试跑下与生产锚点相关性最高——恰印证 T=2 高相关不能当稳健性证据的告诫, 真正判据是主回归系数 (MacKinnon, Nielsen 和 Webb, 2023)。单调性不变量: N_ft(变体) ≤ N_ft(生产)。铁律: 与同族三分子各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J。受保守下界与跨子集近重复盲区两局限约束。

用大白话说, 这一列是四个变体里动得最轻的一个的金融科技分子: 相似度只从八成降到七成半、窗口不变, 因此剩下的金融科技报道数最接近生产口径, 算出来的相关也最高——这恰好提醒我们相关高只是因为几乎没删几条, 不算稳健性证据, 真要看的是把它代进主回归后系数稳不稳。它同样经核验域门控, 和旁车全口径存活率不同域。存活分子不超过生产口径。

## VAR: n_ft_articles_j80w10

【变体差分】
本列是去重敏感性金融科技分子, 变体参数 j80w10 (Jaccard 阈值 0.80 × 10 工作日窗口)。它与生产锚点 j80w5 共享相同相似度阈值 0.80, 唯一差别是把转载判重窗口由 5 工作日延长到 10 工作日, 因此单独拧动"窗口长度"这一自由度而保持相似度不变: 更长窗口使更晚的金融科技转载仍被识别为重复并剔除, 故存活分子低于生产锚点, 体现对"转载扩散持续多久"假设的敏感性。它在该扰动下统计存活的金融科技报道数, 作为该变体 attention_pct 的分子 N_ft。verified 域门控同族: N_ft = (verified ∩ 变体存活), 经 (docid, target_bank) semi-join 收敛到 stage-21 verified 集, 与 sidecar 全 docid 域存活率诊断不同域, 勿混读。它与 j70w10 共享 10 工作日窗, 二者沿相似度放松构成长窗组; 与同变体分母 n_all_articles_j80w10 相除即该变体 attention_pct。单调性不变量: N_ft(变体) ≤ N_ft(生产)。铁律: 与同族三分子各自 just-identified 并排、不分主次, 禁混同一 over-identified Hansen J; 用法为代入主回归验系数稳健。受保守下界与跨子集近重复盲区两局限约束, T=2 试跑高相关属预期平凡结果。

用大白话说, 这一列数的是: 相似度门槛保持八成不变、只把窗口从五天拉到十天之后, 还剩多少条金融科技报道, 专门回答如果认为转载持续更久、把更晚的跟风稿也删掉, 分子会缩多少。它和十天窗七成那个变体构成长窗口这一边。它经核验域门控 (只数核验过又在这个变体里存活的), 和旁车全口径存活率不同域, 别读串。存活分子不超过生产口径, 用途是代进主回归验证结论对转载窗口长度稳不稳。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Bodilsen, S. T., & Lunde, A. (2025). Exploiting news analytics for volatility forecasting. Journal of Applied Econometrics, 40(1), 18-36. https://doi.org/10.1002/jae.3095
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), 20. https://doi.org/10.1007/s13278-025-01416-z
Rambachan, A., & Roth, J. (2023). A more credible approach to parallel trends. The Review of Economic Studies, 90(5), 2555-2591. https://doi.org/10.1093/restud/rdad018
List, J. A., Shaikh, A. M., & Vayalinkal, A. (2023). Multiple testing with covariate adjustment in experimental economics. Journal of Applied Econometrics, 38(6), 920-939. https://doi.org/10.1002/jae.2985
MacKinnon, J. G., Nielsen, M. Ø., & Webb, M. D. (2023). Fast and reliable jackknife and bootstrap methods for cluster-robust inference. Journal of Applied Econometrics, 38(5), 671-694. https://doi.org/10.1002/jae.2969
Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y. (2022). Meet the press: Survey evidence on financial journalists as information intermediaries. Journal of Accounting and Economics, 73(2-3), 101455. https://doi.org/10.1016/j.jacceco.2021.101455
Siano, F., & Wysocki, P. (2021). Transfer learning and textual analysis of accounting disclosures: Applying big data methods to small(er) datasets. Accounting Horizons, 35(3), 217-244. https://doi.org/10.2308/HORIZONS-19-161
MacKinnon, J. G., & Webb, M. D. (2017). Wild bootstrap inference for wildly different cluster sizes. Journal of Applied Econometrics, 32(2), 233-254. https://doi.org/10.1002/jae.2508
Dyer, T., Lang, M., & Stice-Lawrence, L. (2017). The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation. Journal of Accounting and Economics, 64(2-3), 221-245. https://doi.org/10.1016/j.jacceco.2017.07.002
Thoma, G., Torrisi, S., Gambardella, A., Guellec, D., Hall, B., & Harhoff, D. (2010). Harmonizing and combining large datasets: An application to firm-level patent and accounting data. NBER Working Paper No. 15851 No. w15851 [Working Paper]. https://doi.org/10.3386/w15851
<!-- rendered-citations:end -->
