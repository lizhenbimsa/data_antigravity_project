---
family_id: F025
columns:
- avg_agreement_rate_ctx
- avg_agreement_rate_full
- avg_agreement_rate_ss
unit: 比例 (proportion, [0,1] 内连续取值; bank-year 均值, 无量纲)
formula: "avg_agreement_rate{trk} = bank-year mean(_agree_valid{trk}), _agree_valid{trk} = llm_agreement_rate{trk} 仅保留 llm_vote_score{trk} 非缺行 (valid-vote 域掩码, 掩码列缺席回退 raw 列); 文章级 llm_agreement_rate{trk} = #(有效验证票 == final_v) / n_valid_votes, final_v = majority_vote_bool 严格多数 (>50%), n_valid_votes = 0 时取 0.0 并置 call_failure=1; trk ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/sentiment/tone_llms.py::_aggregate_track (文章级 agree_rate_v) ; news_process/pipeline/panel/encode.py::encode_sentiment (_agree_valid 掩码) + build_aggregation_dict (bank-year mean 聚合)
upstream:
- 15_fintech_intensity.parquet
- 21_tone_llms.parquet
citations:
- doi: 10.1177/00131644251380540
  type: journal
  authors: Almehrizi, R. S.
  year: 2026
  title: "Coefficient Lambda for interrater agreement among multiple raters: Correction for category prevalence"
  venue: Educational and Psychological Measurement
  vol: 86
  issue: 2
  pages_or_artno: 287-319
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.3758/s13428-025-02746-8
  type: journal
  authors: Moons, F., & Vandervieren, E.
  year: 2025
  title: "Measuring agreement among several raters classifying subjects into one or more (hierarchical) categories: A generalization of Fleiss' kappa"
  venue: Behavior Research Methods
  vol: 57
  issue: 10
  pages_or_artno: Article 287
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: 65
  issue: 4
  pages_or_artno: 1373-1403
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: "How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk"
  venue: Journal of Banking & Finance
  vol: 164
  pages_or_artno: Article 107191
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: "Measuring news sentiment"
  venue: Journal of Econometrics
  vol: 228
  issue: 2
  pages_or_artno: 221-243
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  pages_or_artno: Article 102776
- doi: 10.1037/met0000412
  type: journal
  authors: van Oest, R., & Girard, J. M.
  year: 2021
  title: "Weighting schemes and incomplete data: A generalized Bayesian framework for chance-corrected interrater agreement"
  venue: Psychological Methods
  pages_or_artno: Advance online publication
- doi: 10.1348/000711006x126600
  type: journal
  authors: Gwet, K. L.
  year: 2008
  title: "Computing inter-rater reliability and its variance in the presence of high agreement"
  venue: British Journal of Mathematical and Statistical Psychology
  vol: 61
  issue: 1
  pages_or_artno: 29-48
- doi: 10.1016/0895-4356(90)90158-l
  type: journal
  authors: Feinstein, A. R., & Cicchetti, D. V.
  year: 1990
  title: "High agreement but low Kappa: I. The problems of two paradoxes"
  venue: Journal of Clinical Epidemiology
  vol: 43
  issue: 6
  pages_or_artno: 543-549
- doi: 10.1037/h0031619
  type: journal
  authors: Fleiss, J. L.
  year: 1971
  title: "Measuring nominal scale agreement among many raters"
  venue: Psychological Bulletin
  vol: 76
  issue: 5
  pages_or_artno: 378-382
new_dois:
- 10.1073/pnas.2305016120
- 10.1016/j.jeconom.2020.07.053
---

## CORE

【构念与来源】
本家族三列度量的是银行-年份 (bank-year) 层面上, 三家大语言模型对同一篇候选新闻的验证判定投票的一致率均值, 也即媒体报道逐篇分类环节的评分员间信度 (inter-rater reliability) 在面板层的原始一致率 (raw percent agreement) 表达。流水线 stage 21 (tone_llms) 是全链唯一核心付费阶段: 它让三个跨厂商、相互独立部署的商用大模型 (gpt-5.4-nano 与 gemini-3.1-flash-lite 两家经 yunwu 网关调用, deepseek-v4-flash 直连官方端点; 阵容动态读自 config/sentiment.yaml, 不硬编码) 各自通读同一篇文章, 首先各投一张验证票, 回答一个门控问题: 这篇报道是否确实在讲目标银行与金融科技之间的关系。三张验证票经严格多数决裁定该篇的最终 verified 判定; 文章级中间量记录的就是与最终判定同向的有效票在全部有效票中的占比。stage 40 面板聚合再把这一文章级比率按银行-年份取均值, 得到本家族的三列面板变量。构念上, 这是 Fleiss (1971) 开创的多评分员名义尺度一致性度量传统在大模型标注范式下的直接移植: 把三个异构厂商的模型视为三位互相独立的编码员, 用它们对同一材料收敛与否来度量分类测度本身的可靠性。这一移植在近年的方法学文献中已获正式承认与规范化: Gilardi, Alizadeh 与 Kubli (2023) 证明大模型在政治与社会文本标注任务上可以超越众包标注员, 并以标注者间一致性作为核心质量证据; Carlson 与 Burbano (2026) 则为管理学与战略研究使用大模型标注数据给出基础性指南, 其中明确要求研究者汇报模型间一致性并披露多模型交叉验证的设计细节。在本项目的证据体系中, 该家族承担的是效度叙事职能: core 列 avg_agreement_rate_full 是论文正文汇报模型间一致性的 headline 列 (2026-07-10 签核扩围, 类别六扩围第一项), 用以向审稿人证明作为主处理变量的媒体语调测度并非某一家模型的私有判断, 而是三家跨厂商模型可复核、可分解、可离线复现的收敛结论。数据来源链条为: stage 15 (fintech_intensity) 产出的 15_fintech_intensity.parquet 提供候选文章全集与三轨文本底稿 (三轨文本 content_full、content_ctx、content_ss 由更上游的 stage 14 ctx_materializer 物化并沿链路传递, 标题以 prepend 方式并入各轨文本, 原始内容列不动; 勿因 legacy 配置键名 output_14_fintech_intensity 误判该 parquet 归属 stage 14 — 重编号后配置键未随之更名, 产出归属以 core/schemas.py 输出登记为准); stage 21 对每篇文章按三轨分别调用三家模型, 轨道级聚合函数逐轨产出文章级一致率并写入 21_tone_llms.parquet; stage 40 的 panel/encode 层完成域掩码与 bank-year 均值聚合。整条链路在提示词第八版字节级冻结、温度参数取零的确定性推理、以及以 _llm_cache.db 为锚的响应缓存三重保障下, 缓存全命中时可在离线守卫下零成本、字节级复现 — 这意味着本家族汇报的一致率不含任何采样随机性, 是纯粹的模型间横截面异质性度量, 与自一致性文献中"同一模型多路径采样再投票"的纵向一致性构念判然有别。

【方法学与计算】
文章级分子分母的精确口径如下。对某一轨道, 三家模型的原始响应先经解析守卫过滤: 调用失败、空响应、JSON 不可解析、或缺失验证键的响应一律按"模型缺席"处理 — 缺席模型既不投赞成票也不充当反对票, 完全退出分子与分母 (2026-06-11 修复批 omni-g-tonellms-01/08 的核心贡献; 此前解析失败曾被静默编码为拒绝票, 会同时污染有效票计数、一致率本身、以及下游以一致率为权重的连续测度与高置信子样本的准入判定)。凡成功解析的模型各得一张布尔验证票, 有效票数记为 n_valid_votes。最终判定由严格多数决裁定: 赞成票必须严格超过有效票数的一半才判通过, 两票中一票赞成不构成多数 (工程实现见 majority_vote_bool, 其源码注明该共识机制移植自多路径采样取多数投票的自一致性推理范式)。文章级一致率等于与最终判定同向的有效票数除以有效票数 (源码 agree_rate_v = agree_v_count / n_valid_votes); 有效票数为零 (三家全部缺席) 时取零值并同时置 call_failure 指示为一, 供下游显式掩码剔除。由于分母至多为三, 该比率是粗粒度离散量: 三票齐时只能落在三分之二或一 (严格多数决保证最终判定至少获得两票支持); 恰有一家缺席时落在二分之一或一; 仅一家有效时恒为一; 全缺席退化为零。这一支撑集特性直接决定了下游高置信子样本阈值的取法。姊妹列的区分必须写明: 同批产出的情感票一致率 (列名多一个 s 中缀) 是另一个质量维度 — 它只在通过验证的模型子集上统计情感方向票与最终情感多数决一致的占比, 无有效情感票时取 NaN 而非零, 属自编码域; 本家族无 s 中缀, 度量的是"是否银行金科报道"这一门控判定本身的收敛度。两列并排构成两个正交质量维度, 面板层分别聚合, 不可混同。面板聚合口径经过一次重要的域对齐修复 (2026-06-11, omni-g-encode-02): encode 层先构造 valid-vote 域掩码列 (_agree_valid{track} = llm_agreement_rate{track}.where(llm_vote_score{track} 非缺)), 把文章级一致率仅保留在该轨情感投票分值非缺的行上 — 即只有该轨验证通过、情感非未定、调用未整体失败的文章才进入均值; 聚合字典优先取掩码列做 bank-year 均值, 掩码列缺席时才回退未掩码的物理域列 llm_agreement_rate{track}。修复动机在于域错位: 旧实现把验证失败、未定与调用失败文章的一致率也计入均值, 而该列要伴随解释的语调测度只建立在有效票文章上, 于是验证失败率高的银行的一致率被无效票机械拉低, 质量诊断信号与被诊断对象不同域。修复后本列与模型自报置信度的宏均值列同口径、与被伴随的语调测度同域。行宇宙与留篇门控方面, stage 21 落盘的分析文件已按 full-only 口径 (2026-06-29 用户决策) 完成留篇: 一篇文章是否算作银行金融科技报道, 只看全文轨验证判定是否为真; ctx 与 ss 两轨降为 conditional-on-full 的测度与稳健性轨, 其行宇宙是全文轨留篇集的子集, 各轨列在该子集上照常计算。因此本家族三列的聚合底座都是全文轨通过验证的文章集合, 这对解释各轨一致率的分布形态有实质影响。下游消费者有三类。其一, 连续编码通道: 每轨的连续语调分值等于离散投票分值乘以该轨一致率 (encode 的 vote_cont = score × agree_rate, 自然传播 NaN), 把一致率用作情感分值的连续衰减权重 — 学理依据是 Shapiro, Sudhof 与 Wilson (2022) 关于新闻情感测度噪声导致回归系数衰减偏误的分析, 一致率低即测量噪声大, 乘法降权等价于对低可靠观测的软剔除。其二, 洗稿率方法 F 高置信度子样本以文章级一致率不低于三分之二为准入门槛, 实现取三分之二减去一个极小浮点余量的下界 — 历史上硬编码的 0.67 曾把唯一的多数票档 (数值上略小于 0.67) 整类静默排除, 使高置信子样本退化为全票一致子样本, 与声明构念不符, 2026-06-11 修复。其三, panel runner 主入口把全文轨文章级一致率列 (llm_agreement_rate_full) 列为硬依赖输入, 缺文件或缺该列即终止退出 — 该列因此是面板构造的结构性锚点之一。此外 stage 21 的运行日志按轨输出模型间一致性诊断 (含均值与全票一致占比两个口径), 并明示其判读语义: 一致率是三家大模型评分员的评分员间信度替代量, 某轨显著低于其他轨说明该轨边界样本更多、语义更模糊, 解释该轨回归时须相应谨慎。

【文献定位】
方法学谱系上, 本测度属于多评分员一致性文献中最古老、也最透明的一支: 原始一致率。Fleiss (1971) 为多评分员、名义尺度的一致性度量奠定经典框架, 其后的方法学演进主要围绕机会一致校正展开: Feinstein 与 Cicchetti (1990) 系统刻画了"高一致率、低卡帕"的两个悖论, 指出类别边际分布极端时机会校正系数会系统性背离直觉; Gwet (2008) 针对高一致场景给出更稳健的校正系数及其方差估计; Moons 与 Vandervieren (2025) 把 Fleiss 框架推广到多标签与层级类别情形; Almehrizi (2026) 针对类别流行率失衡提出带流行率校正的 Lambda 系数; van Oest 与 Girard (2021) 则在广义贝叶斯框架下统一处理加权方案与缺失数据 — 最后这一支与本测度"模型缺席不入分母"的处理直接相关: 缺席即缺失设计, 分母随缺席收缩, 不同文章的一致率建立在不同的评分员阵容上, 恰是该文献所讨论的不完整数据场景。本项目刻意选择在面板列层面保留未经机会校正的原始一致率, 而把机会校正指标 (Krippendorff 的阿尔法与 Cohen 的卡帕) 放在验证阶段作全局标量报告, 理由有二: 第一, 原始一致率逐篇有定义, 可直接聚合为 bank-year 协变量并进入连续权重通道, 而阿尔法与卡帕是样本级统计量, 不具备逐篇分解性; 第二, 在验证判定这种两类、且留篇后阳性占比结构性偏高的场景, 机会校正系数恰好落入 Feinstein-Cicchetti 悖论的高发区, 原始一致率反而是对读者更诚实的汇报口径 — 项目采取两者并用、互为解释的双轨汇报策略, 面板列供回归与加权, 校正标量供效度总评。应用谱系上, 大模型即标注员的文献为本测度提供了直接先例与规范要求: Gilardi, Alizadeh 与 Kubli (2023) 以标注一致性作为大模型标注质量的核心证据; Carlson 与 Burbano (2026) 进一步警告, 多个大模型之间的一致不能自动等同于正确, 因为不同厂商模型共享相近的训练语料与对齐范式, 误差可能正相关, 故一致性汇报必须与人工金标准对照并行。金融文本测度文献中, Shapiro, Sudhof 与 Wilson (2022) 把测量噪声与回归衰减偏误正式联系起来, 构成一致率作衰减权重与高置信子样本切分的学理基础; Bingler 等 (2022) 与 Bingler 等 (2024) 在气候披露的分类器测度中示范了"分类质量决定推断质量"的验证范式, 其从分类器输出到经济后果的证据链结构与本项目从逐篇判定到面板语调的链条同构; Gutknecht (2025) 代表媒体报道基础测度进入公司金融风险回归的近期实践, 提示媒体基础变量的可信度必须以测量质量证据佐证; Li 与 Luan (2025) 的新闻分歧测度则与本族构成有用的构念对照, 详见构念区分一节。

【识别策略定位】
本家族三列不是处理变量 (treatment), 也不是结果变量 (outcome/DV), 而是测量质量诊断协变量 (measurement-quality diagnostic covariate), 在识别体系中承担三种边界清晰、互不越界的辅助角色, 逐一写明其在识别链上的确切位置与不可逾越的边界。第一, 效度叙事 (validity narrative): 论文正文以 core 列 avg_agreement_rate_full 的分布特征证明主处理变量 — 例如 P1 的全文轨大模型投票语调 llm_vote_tone_full — 建立在三家跨厂商、独立部署模型的收敛判定之上, 而非任一单模型的私有输出; 这一用途属测量效度证据链 (measurement validity chain) 的一环, 与结构参数的识别无涉, 因此本列不进入任何回归的右手边, 只在效度小节以描述统计与分布图形式出现。其正当性根植于本测度的确定性可复现属性: 提示词第八版字节冻结、温度取零、以 _llm_cache.db 为锚的缓存全命中下, 一致率不含任何采样随机性, 是纯粹的模型间横截面异质性度量, 因而作效度证据时不会把采样噪声误读为模型分歧 — 这一点把它与自一致性 (self-consistency) 文献中"同一模型多路径采样再投票"的纵向一致性构念划清界限, 后者的一致率随采样温度与路径数波动, 不具备本测度的字节级可复现性。第二, 衰减校正 (attenuation correction): 一致率经连续编码通道以乘法权重形式内嵌进连续语调测度 (encode 的 vote_cont = llm_vote_score × llm_agreement_rate, 自然传播 NaN), 使低可靠观测在构造测度时即自动降权; 学理依据是经典测量误差 (classical measurement error) 使回归系数向零衰减的偏误 — 当自变量含加性噪声时 OLS 斜率被系统性压向零, Shapiro, Sudhof 与 Wilson (2022) 在新闻情感测度语境下正式刻画了这一衰减机制, 一致率低即测量噪声大, 乘法降权在效果上等价于对低信噪比观测的软剔除 (soft-trimming)。须严格区分的是: 这一用途改变的是测度的构造方式 (measure construction), 而非任何识别假设 (identification assumption) 本身 — 权重内嵌在自变量定义里, 不引入新的排除性约束, 论文中因此披露为测度构造细节而非识别策略, 不得表述为工具变量或断点等识别设计。第三, 样本切分 (sample split): 高置信度子样本以文章级一致率阈值构造稳健性臂 (洗稿率方法 F, 准入门槛为一致率不低于三分之二, 工程实现取三分之二减一个极小浮点余量 HC_AGREEMENT_THRESHOLD = 2/3 − 1e−9 的下界, 使三票中两票赞成的唯一多数票档按声明纳入, 修历史硬编码 0.67 把该档整类静默排除、令高置信子样本退化为全票一致子样本之弊, 该阈值的构念锚点亦是 Shapiro 等 2022), 检验主结论是否被低一致率的边界样本驱动; 此用途下一致率扮演样本定义变量 (sample-defining variable), 而非模型内的解释变量。坏控制警示 (bad-control warning) 是本节的承重约束, 必须显式写明: 一致率由报道文本的语义清晰度 (semantic clarity) 决定, 而语义模糊的报道可能系统性地更多出现在业务复杂、处于战略转型期或陷入舆论争议的银行身上 — 即一致率与银行基本面 (bank fundamentals) 可能内生相关。把它直接放进回归右手边作控制变量有引入坏控制 (bad control) 之风险: 一致率处于"报道语义清晰度"这一潜在中介的因果下游, 又可能与银行基本面共变, 条件于它可能打开虚假路径、扭曲主效应估计 (潜在对撞子/处理后变量偏误); 项目口径因此严格界定为只用于效度叙事、衰减加权与子样本切分三种用途, 绝不作右手边控制变量, 亦不作被解释变量。结构性锚点 (structural anchor) 地位补充: 全文轨的文章级源列 llm_agreement_rate_full 被 panel runner 主入口列为硬依赖输入 (与 target_bank、llm_sentiment_full、日期等并列), 缺文件或缺该列即 sys.exit(1) 终止, 本列因此不仅承担叙事职能, 更是 stage 24/45 面板构造链的结构性输入之一, 其缺失会连锁中断整条面板生成。轨道维度铁律必须复述: full、ctx、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J — 该铁律同样约束本家族, 三列分别伴随各自轨道的语调测度进入各自的规格, 不得把多轨一致率同时塞进一条矩条件链 (moment-condition set), 也不得以三轨一致率互相加权合成单一指标后再进回归。

【与相邻测度的构念区分】
与情感票一致率族 (列名带 s 中缀, avg_agreement_rate_s{track}) 的区分: 本族数的是验证票 (这是不是银行金科报道) 的收敛, s 族数的是情感方向票在验证通过子集上的收敛; 前者度量门控判定 (gate decision) 的可靠性, 后者度量语调方向 (tone polarity) 的可靠性, 两者是两个正交的信度维度。空票语义与聚合口径亦不同: 本族三家全缺席时取零并配调用失败指示列 call_failure, 面板聚合依赖显式 valid-vote 域掩码 _agree_valid{track}; s 族无有效情感票时取 NaN (自编码域, self-encoded domain), 面板层直接对 llm_agreement_rate_s{track} 求均值、不需掩码。两列并排构成两个层级不同的信度维度, 不可混同或相加。与模型自报置信度宏均值列 (avg_llm_conf{track}) 的区分: 置信度是各模型对自身判断的主观概率自评 (self-assessment), 一致率是模型之间的客观交叉验证 (peer-assessment); 前者可能被单一模型的系统性过度自信 (overconfidence) 抬高 — 一个总是自报高置信的模型会单方面拉高该列, 却对判定是否正确不提供任何独立证据, 后者对任何单模型的自评偏倚天然免疫, 因为它只统计模型间的收敛而不读取任何模型的自我评分; 二者是自评与互评两个正交维度, 在同一 valid-vote 域上并排汇报 (2026-06-11 域对齐修复后二者同口径), 互为补充不可替代。与连续加权语调测度 (llm_vote_cont{track} 及其各类加权变体) 的区分: 一致率是这些连续测度的构造输入 (作为乘法权重), 而非它们的输出 — vote_cont = score × agree_rate 中, 一致率扮演权重角色, 乘积才是被加权后的语调分; 把一致率与这些加权语调分混为一谈是范畴错误, 前者是信度度量、后者是被信度调制后的语调度量, 逻辑上前者先于后者。与有效票数、验证票数两个计数列 (n_valid_votes{track} / n_verifying_votes{track}) 的区分: 计数列刻画投票阵容 (rater panel) 的规模与构成, 是一致率的分母与分子素材, 未做比率归一, 一致率是它们的归一化商; 计数列供下游按绝对阵容规模掩码 (例如只保留三家全到齐的文章), 与本族的比率口径职能不同。与验证阶段的 Krippendorff 阿尔法与 Cohen 卡帕 (tone_validation 全局标量) 的区分: 后者是机会校正 (chance-corrected) 的样本级标量, 用于跨模型一致性的验收闸, 不落面板列 (卡帕计算前须把缺标哨兵 −1 重映射为非负码, 避免与负面标签的负值编码冲突); 本族是未经机会校正、逐篇可分解 (per-article decomposable)、可聚合为 bank-year 协变量的原始一致率; 两套指标构念互补而层级不同, 校正标量供全局效度总评、原始一致率供逐篇加权与截面回归, 项目刻意两者并用、互为解释。与 BERT 侧跨模型标签异质度、分歧度两列 (bert_xmodel_lblhet / bert_xmodel_disp) 的区分: 那是三个 BERT 模型情感标签的跨模型分歧测度, 符号方向与本族相反 (高值等于分歧大而非一致大), 属 BERT 方法族的平行质量维度; 大模型法与 BERT 法两法各自 just-identified 并排、互为稳健性, 禁混同一 over-identified Hansen J。与新闻基础的投资者分歧一类经济测度 (如 Li 与 Luan 2025 的 news-based investor disagreement) 的区分最须防混淆: 那是市场参与者对同一信息解读的分歧, 是有资产定价 (asset-pricing) 含义的经济构念, 其分歧本身进入收益预测模型; 本族是标注工具 (annotation tool) 对同一文本判定的分歧, 是纯测量构念 (measurement construct), 不具任何资产定价含义; 二者名近而实远, 论文写作中不得互为代理, 亦不得把本族的低一致率解读为市场分歧。与洗稿式文本相似度测度 (herd_decay 族) 的区分: 后者度量的是跨文章的内容复制转抄程度 (article-to-article textual duplication), 是内容层面的相似度; 本族度量的是同一篇文章上评分员间判定的收敛度 (within-article rater convergence); 前者的"相似"发生在文本之间, 后者的"一致"发生在评分员之间, 层级完全不同, 不可互换。

【已知局限与稳健性梯子】
局限一, 粒度粗 (coarse granularity): 分母至多为三, 文章级比率的支撑集 (support set) 在三票齐时仅落 {2/3, 1}、恰一家缺席时仅 {1/2, 1}、仅一家有效时恒为 1、全缺席退化为 0, 高度离散; bank-year 均值的边际变化主要由留篇文章构成的变化驱动, 不宜对其水平差做精细解读, 更不宜标准化后当作连续正态变量建模; 其恰当角色是分布位置的证据与阈值切分的原料, 而非精细的连续回归自变量。局限二, 无机会校正 (no chance correction): 原始一致率在类别流行率 (category prevalence) 失衡时系统性偏高 — Feinstein 与 Cicchetti (1990) 刻画的"高一致率、低卡帕"两个悖论正发生在边际分布极端的场景, Almehrizi (2026) 的流行率校正 Lambda 系数与 Gwet (2008) 的高一致稳健系数均是对此的修正; 留篇后的全文轨阳性占比结构性偏高, 一致率高企部分是构造使然 (constructional) 而非全然反映模型可靠; 项目以验证阶段的阿尔法与卡帕、以及人工盲标双编码 (double-coding) 协议作互补证据, 面板列与校正标量双轨并用。局限三, 评分员非独立 (non-independent raters): 三家模型共享互联网规模的训练语料与相近的指令对齐 (instruction alignment) 范式, 判定误差可能正相关 (positively correlated errors), 一致不等于正确 (Carlson 与 Burbano 2026 的核心警告); 缓解手段是人工标注金标准 (human gold standard) 对照, 而不是加入更多同质模型 — 后者只会放大共享偏倚而虚增一致率。局限四, 缺席导致的不完整设计 (incomplete design from absence): 模型缺席使分母收缩, 不同文章的一致率建立在不同阵容上, 恰是 van Oest 与 Girard (2021) 广义贝叶斯框架所讨论的缺失数据 (incomplete/missing data) 场景; 调用失败指示列 call_failure 与有效票数列 n_valid_votes 供下游显式控制阵容异质性, 使分析者能区分"三家一致"与"仅一家在场故恒为一"这两种表面等值实则信度悬殊的情形。局限五, 选择效应 (selection effect): full-only 留篇 (2026-06-29 用户决策) 使全文轨行宇宙条件于最终判定为真, 该轨一致率分布右移且被截断在多数票档 (2/3) 之上, 三票齐时只能落 2/3 或 1; 解释其截面与时序变异时须记住这是条件于通过门控 (conditional-on-gate-pass) 的一致率, 回答的不是"模型是否同意留下这篇", 而是"在已留篇的文章上反对票残留的密度", 而非无条件测度。局限六, 早期试跑盘面退化 (dev-sample degradation): T=2 样本上各列统计属小样本退化, 一切水平与方差结论以生产全量 T=19 语料为准 (真实语料 约 1,819 万条媒体报道、2007–2025)。稳健性梯子按维度展开, 各维彼此正交、不交叉组合, 以避免规格爆炸 (specification explosion) 并保持每一臂的可解释性: 轨道维为 full、ctx、ss 三轨, 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J, 其中 ss 轨回退语义镜像 ctx — 无银行与金科同句共现时该轨文本取全文正文并置回退指示 ss_is_fallback 为真, 与其他轨共享文章数分母; 质量维为 s 中缀情感票一致率并排的第二信度维度; 阈值维为高置信子样本的三分之二准入臂 (2/3 − 1e−9 下界); 方法维为大模型三家逐模型存档列与 BERT 三模型平行质量族, 各法、各家、各模型均各自 just-identified 并排; 校正维为机会校正标量 (阿尔法/卡帕) 验收闸与人工盲标双编码的双口径。以上各维共同构成本族的规格稳健性体系, 但铁律不变: 任一梯子内的各臂不得混进同一 over-identified Hansen J, 亦不得跨维交叉相乘以免规格爆炸。

## VAR: avg_agreement_rate_ctx

【变体差分】
本列是家族在 ctx 轨 (实体上下文轨) 上的实现: 文章级一致率的计算材料是标题 prepend 加实体窗口文本 (content_ctx, stage 14 的 ctx_materializer 物化), 即只保留目标银行实体附近的上下文片段, 三家模型对这一压缩后的文本独立作出验证判定再行投票。与 canonical 的全文轨列相比, 差分维度是文本窗口而非模型、阈值或权重: ctx 文本更短、更聚焦于实体近旁语境, 剔除了与目标银行无关的段落噪声, 但也可能截掉分散在全文各处的佐证信息, 因此其验证判定的边界样本占比通常更高, 一致率的轨间落差本身就是文本窗口对判定难度影响的直接证据。行宇宙口径须写明: 依 full-only 留篇门控 (2026-06-29 用户决策), 本列的聚合底座仍是全文轨验证通过的文章集合, ctx 轨自身的验证判定不参与留篇决定, 本列因此是 conditional-on-full 的测度与稳健性轨; 在该行宇宙内, ctx 轨验证判定可以为假, 面板聚合经 valid-vote 域掩码 (_agree_valid_ctx) 只纳入 ctx 轨投票分值非缺的文章, ctx 轨与全文轨的大模型判定成功率相互独立, 掩码域不借用全文轨。逐轨自洽的口径纪律在同一 encode 文件中有旁证先例: 同轨的大模型分类占比列族曾因分母错用全文轨有效篇数出现轨道不对称除法、比率越界的历史缺陷并已修复 — 但须明辨, 那一越界情节发生在分类占比族, 不发生在本族; 本族自身的历史修复是域对齐 (2026-06-11, 见 CORE 方法学节): 旧实现把验证失败与调用失败文章的一致率计入均值, 属域错位拉低均值, 无任何越界情节, 两桩修复同属逐轨口径纪律却是两个不同缺陷, 不可混同归因。用途上本列伴随 ctx 轨语调测度进入 ctx 规格, 与全文轨列互为稳健性、不分主次, 两轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 亦不得与全文轨、同句轨一致率互相加权合成单一指标后再进回归。

## VAR: avg_agreement_rate_full

【变体差分】
本列是家族的 canonical headline 与全家族唯一 core 列, tier 升格依据为类别六扩围第一项 (2026-07-10 签核): 大模型三家一致率的全文轨版本被指定为论文正文效度叙事的汇报列, 模型间一致性在正文以本列为口径展开。差分语义分四层。第一层, 文本窗口: 计算材料是标题 prepend 加全文正文 (content_full), 三家模型面对的是信息最完整的版本, 判定所依据的证据集是三轨中的超集, 因此本列度量的是"给足信息时三家模型是否仍然收敛", 是三轨中对模型能力差异最敏感、对文本截断噪声最不敏感的一轨, 这正是它承担正文效度叙事的原因。作为 canonical headline, 本列还是全族唯一在缓存全命中下可经 NEWS_PROCESS_LLM_OFFLINE=1 离线零成本、字节级复现的效度证据 — 正文汇报的模型间一致性因此不含任何采样随机性, 审稿人可离线独立复核, 这一确定性属性是把它选作正文汇报列而非其余两轨的额外理由。第二层, 行宇宙的自门控特性: 留篇门控本身就定义在本轨 — 只有全文轨验证判定为真的文章才进入分析文件, 于是本列聚合域内每篇文章的最终判定均为真, 三票齐时文章级一致率只能落在三分之二 (两票赞成一票反对) 或一 (全票一致) 两档, 分布被结构性截断在多数票档之上; 解释本列的截面与时序变异时必须记住这一条件化语义: 它回答的不是"模型是否同意留下这篇文章", 而是"在已留篇的文章上, 反对票残留的密度有多高", 换言之是留篇集内部由弱多数篇 (三分之二档) 与全票篇 (一档) 混合比例决定的位置量, 弱多数篇占比越高本列越低。因三票齐时该文章级分布仅两点支撑 (2/3 与 1), 本列水平的经济解读须格外克制, 不宜标准化后当作连续正态变量建模, 其恰当读法是"留篇集内部全票一致篇的相对密度"这一位置指标。第三层, 下游结构地位, 本轨在三轨中承重最实: 其一, panel runner 主入口把本轨的文章级源列 llm_agreement_rate_full 与 target_bank、llm_sentiment_full、日期等并列为硬依赖, 缺文件或缺该列即 sys.exit(1) 终止, 本列因此是 stage 24/45 面板构造链的结构性锚点; 其二, 全文轨连续语调编码以本轨文章级源作乘法衰减权重 (vote_cont = score × agree_rate), 与 P1 主处理变量同轨同域伴随, 学理依据是 Shapiro, Sudhof 与 Wilson (2022) 的测量噪声衰减偏误分析, 一致率低即噪声大、乘法降权即对低可靠观测软剔除; 其三, 洗稿率方法 F 高置信子样本的主轨准入以本轨一致率不低于三分之二为门槛 (实现取三分之二减一个极小浮点余量的下界, 使唯一的多数票档按声明纳入, 修历史硬编码 0.67 把该档整类静默排除之弊), Shapiro 等 (2022) 亦是该高置信构念的源码级锚点; 其四, stage 21 运行日志的模型间一致性诊断以本轨为第一汇报位, 均值与全票一致占比两个口径并列输出。第四层, 与非 core 两列的关系: ctx 与 ss 列是本列在更窄文本窗口下的平行测度, 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 本列的 core 地位是汇报职能上的 (正文叙事与验收闸挂钩), 不是计量地位上的主从关系, 三轨在回归体系中的证据权重对等, 不得因本列为 core 就把它凌驾于另两轨之上或将三轨一致率合成单一指标。使用警示重申: 本列不作回归右手边控制 (报道语义模糊度可能与银行基本面相关, 且处于报道语义清晰度这一潜在中介的因果下游, 条件于它有坏控制乃至对撞子偏误之风险), 其正当用途严格限于效度叙事、衰减加权与高置信子样本切分三种, 越出此三用途即属误用; 尤须防止的误用是把本列的高低直接解读为"银行媒体形象好坏"或"市场分歧大小" — 它度量的只是三家标注模型对门控判定的收敛度, 与语调方向、与市场解读分歧均无构念对应。

## VAR: avg_agreement_rate_ss

【变体差分】
本列是家族在 ss 轨 (同句共现轨) 上的实现: 文章级一致率的计算材料是标题 prepend 加"目标银行与金融科技词在同一句内共现"的句窗片段 (content_ss, 窗口半径由 config/filtering.yaml 的 ss_sentence_radius 控制, 默认正负一句; 该键与 stage 13 共现硬过滤的 sentence_radius 是两个不同配置键, 不可混同), 判定采用不对称口径 — 银行侧经否定与短名过滤, 金融科技侧用裸 AC 自动机词表匹配。这是三轨中文本最窄、语义密度最高的一轨, 模型只看到银行与金科直接同句交汇的证据核, 验证判定因此最严苛, 一致率反映的是"证据最浓缩时三家模型的收敛度"。回退语义必须按铁律写明: 当整篇文章不存在银行与金科的同句共现时, 本轨文本回退为全文正文, 同时回退指示列 ss_is_fallback 置真, 该回退镜像 ctx 轨的回退设计, 且与其他轨共享文章数分母, 不单独收缩行宇宙; 回退行上本轨文本与全文轨实质重合, 其一致率天然趋同于全文轨, 解释本列时应结合回退占比理解两轨落差的真实来源。行宇宙口径与 ctx 列相同: full-only 留篇门控下本列是 conditional-on-full 的稳健性轨, 聚合经 valid-vote 域掩码 (_agree_valid_ss) 只纳入 ss 轨投票分值非缺的文章, 判定成功率与其他轨独立、掩码域不互借。本列伴随 ss 轨语调测度进入 ss 规格, 与 full、ctx 两列互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 亦不得与另两轨一致率加权合成后再进回归。

<!-- rendered-citations:begin -->
Almehrizi, R. S. (2026). Coefficient Lambda for interrater agreement among multiple raters: Correction for category prevalence. Educational and Psychological Measurement, 86(2), 287-319. https://doi.org/10.1177/00131644251380540
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Moons, F., & Vandervieren, E. (2025). Measuring agreement among several raters classifying subjects into one or more (hierarchical) categories: A generalization of Fleiss' kappa. Behavior Research Methods, 57(10), Article 287. https://doi.org/10.3758/s13428-025-02746-8
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, Article 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, Article 102776. https://doi.org/10.1016/j.frl.2022.102776
van Oest, R., & Girard, J. M. (2021). Weighting schemes and incomplete data: A generalized Bayesian framework for chance-corrected interrater agreement. Psychological Methods, Advance online publication. https://doi.org/10.1037/met0000412
Gwet, K. L. (2008). Computing inter-rater reliability and its variance in the presence of high agreement. British Journal of Mathematical and Statistical Psychology, 61(1), 29-48. https://doi.org/10.1348/000711006x126600
Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low Kappa: I. The problems of two paradoxes. Journal of Clinical Epidemiology, 43(6), 543-549. https://doi.org/10.1016/0895-4356(90)90158-l
Fleiss, J. L. (1971). Measuring nominal scale agreement among many raters. Psychological Bulletin, 76(5), 378-382. https://doi.org/10.1037/h0031619
<!-- rendered-citations:end -->
