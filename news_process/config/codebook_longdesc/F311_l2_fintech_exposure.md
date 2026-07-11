---
family_id: F311
columns:
- fintech_exposure_ctx
- fintech_exposure_ctx_z
- fintech_exposure_full
- fintech_exposure_full_z
- fintech_exposure_ss
- fintech_exposure_ss_z
unit: "无量纲复合指标 (对数覆盖强度 × 年内情感标准差的乘积; _z 后缀列为年度截面 z-score, 单位 = 年内截面标准差)"
formula: "fintech_exposure{track} = ln_news_coverage × llm_vote_tone_std{track}, 其中 ln_news_coverage = ln(1 + n_articles), llm_vote_tone_std{track} = std(llm_vote_score{track}) 按银行-年分组 (pandas 样本标准差 ddof=1); track ∈ {_full, _ctx, _ss}; 零新闻行 (n_articles = 0) 置 NaN。_z 列 = 逐年度截面 (x − μ_year) / σ_year, 仅 n_articles > 0 行参与, 年内有效观测 < 3 或 σ_year < 1e-10 的年份跳过"
producer: "news_process/pipeline/panel/geography.py (Fintech Exposure 复合指标块, 三轨循环 L363-389; _z 列由同文件 standardize_panel_variables 白名单 _STANDARDIZE_COLS 之 fintech_exposure_{t} 模板经 _expand_track_templates 展开产出)"
upstream:
- 21_tone_llms.parquet (llm_vote_score{track} 文章级三家多数投票分值 → encode.py 聚合为 llm_vote_tone_std{track})
- 40_panel_yearly.parquet 中间态 (n_articles → ln_news_coverage = np.log1p(n_articles), encode.py; llm_vote_tone_std{track}, encode.py 聚合字典)
citations:
- doi: 10.1080/00036846.2025.2476213
  type: journal
  authors: Zhang, X., & Li, Z.
  year: 2026
  title: "FinTech and branch network expansion: Evidence from China's banking industry"
  venue: Applied Economics
  vol: 58
  issue: 12
  pages_or_artno: 2321-2336
- doi: 10.1016/j.intfin.2026.102306
  type: journal
  authors: Alfhaili, F. A., Bakoush, M., & Wolfe, S.
  year: 2026
  title: "Investing in fintech equity and bank innovation"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 108
  pages_or_artno: "102306"
- doi: 10.1002/ijfe.3105
  type: journal
  authors: Liu, J., Chen, S., Su, F., & Liu, J.
  year: 2025
  title: "Digital transformation disclosure and bank loans: An information heterogeneity perspective"
  venue: International Journal of Finance & Economics
  vol: 30
  issue: 4
  pages_or_artno: 4004-4038
- doi: 10.1016/j.jfineco.2024.103950
  type: journal
  authors: Babina, T., Bahaj, S., Buchak, G., De Marco, F., Foulis, A., Gornall, W., Mazzola, F., & Yu, T.
  year: 2025
  title: "Customer data access and fintech entry: Early evidence from open banking"
  venue: Journal of Financial Economics
  vol: 169
  pages_or_artno: "103950"
- doi: 10.1080/00036846.2025.2536881
  type: journal
  authors: Wu, M., Shen, L., Wu, T., & Shao, Y.
  year: 2025
  title: "Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China"
  venue: Applied Economics
- doi: 10.1080/1351847X.2025.2468481
  type: journal
  authors: Li, T., Stasinakis, C., Yeo, W. M., & Da Silva Fernandes, F.
  year: 2025
  title: "Fintech, financial development and banking efficiency: Evidence from Chinese commercial banks"
  venue: The European Journal of Finance
  vol: 31
  issue: 10
  pages_or_artno: 1245-1295
- doi: 10.2139/ssrn.4323093
  type: wp
  authors: Dim, C., Sangiorgi, F., & Vilkov, G.
  year: 2023
  title: "Media narratives and price informativeness"
  venue: SSRN Working Paper No. 4323093
- doi: 10.1017/S0022109023000662
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2618-2646
- doi: 10.1016/j.intfin.2024.102002
  type: journal
  authors: Koranteng, B., & You, K.
  year: 2024
  title: "Fintech and financial stability: Evidence from spatial analysis for 25 countries"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 93
  pages_or_artno: "102002"
- doi: 10.1016/j.jimonfin.2024.103076
  type: journal
  authors: Zheng, H., & Mao, M. Q.
  year: 2024
  title: "Fintech mergers and acquisitions"
  venue: Journal of International Money and Finance
  vol: 143
  pages_or_artno: "103076"
- doi: 10.1016/j.econmod.2023.106445
  type: journal
  authors: Fang, Y., Wang, Q., Wang, F., & Zhao, Y.
  year: 2023
  title: "Bank fintech, liquidity creation, and risk-taking: Evidence from China"
  venue: Economic Modelling
  vol: 127
  pages_or_artno: "106445"
- doi: 10.1016/j.iref.2021.03.009
  type: journal
  authors: Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J.
  year: 2021
  title: "Does fintech innovation improve bank efficiency? Evidence from China's banking industry"
  venue: International Review of Economics & Finance
  vol: 74
  pages_or_artno: 468-483
- doi: 10.1080/1351847x.2020.1805782
  type: journal
  authors: Wang, R., Liu, J., & Luo, H.
  year: 2021
  title: "Fintech development and bank risk taking in China"
  venue: The European Journal of Finance
  vol: 27
  issue: 4-5
  pages_or_artno: 397-418
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: The Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1016/j.jfs.2020.100836
  type: journal
  authors: Boot, A., Hoffmann, P., Laeven, L., & Ratnovski, L.
  year: 2021
  title: "Fintech: What's old, what's new?"
  venue: Journal of Financial Stability
  vol: 53
  pages_or_artno: "100836"
- doi: 10.1016/j.jfi.2019.100833
  type: journal
  authors: Thakor, A. V.
  year: 2020
  title: "Fintech and banking: What do we know?"
  venue: Journal of Financial Intermediation
  vol: 41
  pages_or_artno: "100833"
- doi: 10.1016/j.pacfin.2020.101398
  type: journal
  authors: Cheng, M., & Qu, Y.
  year: 2020
  title: "Does bank FinTech reduce credit risk? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 63
  pages_or_artno: "101398"
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: Journal of Business Economics
  vol: 87
  issue: 5
  pages_or_artno: 537-580
new_dois:
- 10.2139/ssrn.4323093
---

## CORE

【构念与来源】

本家族测度的构念是银行层面的金融科技叙事暴露度 (fintech narrative exposure): 一家银行在给定年度内, 既被媒体高强度地置于金融科技叙事之中, 又面对情感基调高度分歧的报道流时, 其经营环境所承受的叙事性信息冲击强度。构念的直接学理出处是 Dim, Sangiorgi 与 Vilkov (2023) 的媒体叙事与价格信息含量研究: 该文第三式将资产层面的叙事暴露定义为资产收益对各条叙事注意力冲击的敏感度绝对值与该叙事注意力时间序列波动率的加权乘积和, 即敏感度捕捉"这项资产被卷入该叙事的深度", 波动率捕捉"该叙事本身翻腾的剧烈程度", 两者相乘才构成有效的叙事暴露。本项目把这一资产定价语境下的构念迁移到中国银行业新闻面板: 以银行-年新闻覆盖强度的对数变换类比原文的敏感度绝对值分量, 度量该银行嵌入金融科技媒体叙事的信息暴露深度; 以该银行当年金融科技报道情感的横截面离散度类比原文的叙事注意力波动率分量, 度量围绕该银行的叙事基调有多不安定; 两者的乘积构成复合暴露指标。乘积形式的经济含义是清晰的: 只有"报道多"且"报道口径分歧大"同时成立, 银行才真正处于高叙事暴露状态; 报道再多但口径高度一致 (标准差趋零), 或者口径再乱但只有寥寥数篇, 暴露度都会被另一个乘数压低。这一交互结构区别于单独使用覆盖量或情感水平的传统媒体测度, 是本家族的核心识别性特征。

数据来源上, 本家族坐落于 news_process 银行-年面板的下游合成层。原始输入是中国银行与金融科技主题新闻语料 (生产口径约一千七百万条, 2007 至 2024 年, T=18; 开发盘上为 T=2 试跑切片), 经预处理、银行实体识别、金融科技词表匹配、共现硬过滤与三轨文本物化后, 由第 21 阶段的三家大模型情感投票 (gpt54nano 与 gemini31 经 yunwu 路由、deepseekv4 直连) 给出逐篇情感分值, 再在银行-年单元聚合为投票均值与投票标准差。本家族消费的两个直接上游量均在聚合层生成: 其一是新闻覆盖强度的对数 ln(1 + n_articles), 其中 n_articles 是该银行当年通过 full 轨留篇门控的金融科技相关报道篇数; 其二是逐轨的年内逐篇投票分值样本标准差。复合指标本身在面板地理与合成阶段 (geography 模块) 计算, 六列全部落入年度面板并导出至 Stata 数据集, 出口标签为 Fintech Exposure (Cov*Std) 及其 Z 化版本。

【方法学与计算】

计算公式为: 某银行 i 在年份 t、轨道 k 上的 fintech_exposure 等于 ln_news_coverage 乘以 llm_vote_tone_std 的第 k 轨版本。第一乘数 ln_news_coverage 定义为 ln(1 + n_articles), 由聚合引擎以 np.log1p 直接从留篇计数变换而来; 注意它是 track-agnostic 标量, 不随三轨分裂 — 分母性质的"这家银行今年被报道了多少篇"只有一个答案, 因为留篇门控自 2026-06-29 起统一为 full-only 口径: 一篇文章是否算作银行金融科技报道, 只看 llm_verified_full 是否为真, ctx 与 ss 轨是留篇集之上的 conditional-on-full 测度轨, 不拥有独立的行宇宙。第二乘数 llm_vote_tone_std 是逐轨量: 对该银行当年全部留篇文章, 取其第 k 轨的三家模型多数投票情感分值 (取值离散于负一、零、正一), 按银行-年分组计算 pandas 样本标准差 (ddof=1)。由样本标准差的定义可知, 该乘数要求年内至少两篇有效文章才非缺失, 单篇银行-年的标准差为 NaN, 从而复合指标同为 NaN — 这是刻意的保守设计, 单篇无从谈"叙事分歧"。

生产代码的健壮性语义值得逐条写明。第一, 零新闻行处理: 计算前先构造 has_news 掩码 (n_articles 大于零), 覆盖乘数经 where 变换在零新闻行置 NaN, 与面板全部情感变量的 NaN 语义保持一致 — 零新闻不是零暴露, 而是不可观测。第二, 缺列优雅跳过: 若某轨的投票标准差列未落盘 (例如 ss 轨情感在某些上游配置下未产出) 或 ln_news_coverage 缺席, 该轨复合列整列填 NaN 并写出响亮的 warning 日志, 绝不静默省略列, 保证面板 schema 稳定。第三, 生产日志携带自动判读: 每轨计算后记录非空观测的均值与标准差, 并按横截面离散度给出三档判读 (全空即该轨不可用、离散度近零即区分度弱、存在横截面变异即可作叙事暴露代理), 供日志审计快速定位小样本退化。第四, 全部新列经单次 concat 合并入面板, 避免逐列赋值造成的 DataFrame 碎片化。

三个 _z 后缀列由同模块的年度截面标准化函数产出, 方法学锚点是 Fama-MacBeth 式两阶段回归对截面变量可比性的要求。fintech_exposure 三轨模板位于标准化白名单, 经轨道模板展开进入候选集; 执行时仅处理有新闻覆盖的银行-年, 对每个年度截面分别计算均值与标准差并作 z 变换, 年内有效观测少于三个的年份直接跳过, 截面标准差小于十的负十次方 (数值零方差) 的年份亦跳过, 原始列原样保留、标准化列以 _z 后缀新增。此外还有两道入口守卫: 整列非空观测少于十个的候选列被判入观测不足而整体跳过; 上游列若为 nullable 扩展 dtype 则先统一归一为 float64 再运算, 保证 z 分数对上游 dtype 不敏感。经 z 化后, 回归系数可直接解读为"叙事暴露每变动一个年内截面标准差, 因变量变动 β 个单位", 消除了不同年份媒体总量漂移对系数量纲的污染 — 这一点在 2007 至 2024 的长面板上尤为重要, 因为中国金融科技报道总量在此期间发生了数量级增长。

覆盖乘数取对数变换而非原始篇数, 有两层理由。其一是注意力的边际递减: 媒体报道对信息环境的增量贡献随篇数增加而递减, 第十篇与第十一篇报道的差别远小于第一篇与第二篇, 对数形式把这一凹性内生地编码进指标; 其二是分布形态: 银行-年报道篇数呈重尾分布, 头部大银行的篇数可高出中位数若干个数量级, 不取对数则复合指标的横截面变异几乎完全被篇数极值主导, 分歧乘数的信息被淹没, 对数化后两个乘数的变异贡献才处于可比量级。加一后取对数 (log1p) 是为兼容零篇数行的数值定义, 尽管这些行随后已被 has_news 掩码置 NaN, 变换本身不在零点发散仍是数值卫生的要求。

与原文公式的差异也须如实交代: Dim, Sangiorgi 与 Vilkov (2023) 的原式在多条叙事上加权求和并以波动率总和归一, 本项目只针对金融科技单一叙事族, 故无跨叙事归一化分母; 原文的敏感度是资产收益对叙事冲击的回归系数绝对值, 本项目以对数覆盖强度作代理, 属于概念类比而非逐项复刻。生产源码注释对这一"概念迁移"性质有明确声明, 论文写作引用时应表述为 conceptually adapted from 而非 following。

【文献定位】

本家族在三支文献的交汇处。第一支是媒体叙事与文本测度文献。Dim, Sangiorgi 与 Vilkov (2023) 证明媒体叙事暴露度对价格信息含量有独立解释力, 是本指标的构念母体; 更广义地, Li, Mai, Shen 与 Yan (2021) 以机器学习从文本构造公司文化测度的范式, 确立了"从大规模非结构化文本提炼企业层面连续变量"的方法论合法性, 本项目以大模型投票替代其词嵌入种子词扩展, 属同一测度传统的工具升级。第二支是银行金融科技的实证文献, 特别是中国场景: Cheng 与 Qu (2020) 以年报文本词频构造银行金融科技指数并考察信用风险, 是中国银行金融科技文本测度的早期标杆; Lee, Li, Yu 与 Zhao (2021) 考察金融科技创新对银行效率的影响; Fang, Wang, Wang 与 Zhao (2023) 研究银行金融科技对流动性创造与风险承担的作用; Wang, Liu 与 Luo (2021) 从行业层面金融科技发展考察银行风险承担; Li, Stasinakis, Yeo 与 Da Silva Fernandes (2025) 综合文本挖掘构造金融科技测度检验中国商业银行效率; Zhang 与 Li (2026) 考察金融科技对银行网点扩张的影响; Wu, Shen, Wu 与 Shao (2025) 检验银企金融科技战略合作与银行风险承担的关系。这批文献的共同局限是暴露测度多取自银行自身披露 (年报、专利、合作公告), 度量的是银行的主动数字化投入; 本家族以外部媒体报道的覆盖与分歧刻画银行"被叙事"的被动暴露, 与主动投入型指标构成互补的测量视角, Liu, Chen, Su 与 Liu (2025) 关于数字化转型披露的信息异质性影响银行贷款的证据, 恰好说明市场对同一数字化信号的解读分歧本身携带定价信息, 为"分歧作为暴露分量"的设计提供了间接支持。第三支是金融科技与银行业结构的综述与前沿: Thakor (2020) 与 Boot, Hoffmann, Laeven 与 Ratnovski (2021) 的综述框定了金融科技冲击银行中介功能的理论边界; Gomber, Koch 与 Siering (2017) 给出数字金融研究的领域图谱; Kwan, Lin, Pursiainen 与 Tai (2024) 以招聘广告文本度量银行数字化能力并利用疫情作压力测试, 展示了非披露型文本代理在识别中的价值; Babina 等 (2025) 研究开放银行数据准入与金融科技进入; Zheng 与 Mao (2024) 与 Alfhaili, Bakoush 与 Wolfe (2026) 分别考察金融科技并购与股权投资, 说明银行对金融科技叙事的应对是可观测的真实决策; Koranteng 与 You (2024) 的跨国空间分析则把金融科技与金融稳定的关联推到系统层面。本家族为这支文献补充了一个此前缺失的解释变量: 媒体叙事层面的金融科技暴露强度。

【识别策略定位】

在回归体系中, 本家族定位为处理变量侧的连续暴露测度或调节变量, 而非结果变量。典型用法有三: 其一, 作为核心解释变量进入银行结果方程 (风险承担、效率、投融资决策), 检验叙事暴露的边际效应, 此时推荐使用 _z 列以获得截面标准差单位的系数解读; 其二, 作为调节变量与情感水平变量交乘, 检验"高暴露状态下情感冲击是否被放大"; 其三, 作为异质性分组变量, 按暴露度高低分样本检验主效应的条件性。须明确的识别限度是: 本指标本身不携带外生变异, 覆盖强度与情感分歧都可能与银行不可观测基本面同时决定, 单独回归只能给出条件相关而非因果效应; 管道内配套的三引擎工具变量族 (同组留一均值、广义 Bartik、媒体来源风格暴露) 才是因果主张的承重结构, 本家族在其中扮演被解释的内生处理变量或描述性暴露背景的角色。规格设定的实务建议: 固定效应至少纳入银行与年份双向, 以吸收银行恒常媒体关注度与年度叙事总量漂移; 标准误按银行聚类, 面板另备注册地省市列可作地理聚类稳健性; 因分歧乘数在少篇银行-年上测量误差大且误差与篇数负相关, 系数存在向零衰减的可能, 报告时宜辅以按篇数分层的子样本估计。

口径铁律必须复述: 本家族横跨三轨 (full、ctx、ss), 三轨各自 just-identified 并排进入各自的回归规格, 互为稳健性、不分主次, 严禁把三轨版本混入同一 over-identified 方程做 Hansen J 过度识别检验 — 三轨共享同一语料与同一留篇集, 其矩条件不是相互独立的工具, 混用会产生机械性的过度识别假象。同理, 原始列与 _z 列是同一信息的两种量纲, 只能择一进入给定规格, 并排呈现时属于规格稳健性而非独立证据。留篇门控与分母口径须与 full-only 铁律一致: n_articles 及由之派生的 ln_news_coverage 均以 llm_verified_full 单一门控计数, ctx 与 ss 轨不改变行宇宙。

【与相邻测度的构念区分】

面板中与本家族构念相邻但不可混同的测度有六类, 逐一划界如下。与 ln_news_coverage 及其 z 化版本的区别: 后者是纯注意力量, 只回答"报道多不多", 不含情感信息; 本家族在其上乘入分歧维度, 二者在回归中同时出现时, 本家族系数应解读为给定覆盖强度后分歧的增量贡献, 且须警惕机械共线。与 llm_vote_tone 家族的区别: 情感均值度量基调的水平与方向, 本家族的第二乘数是同年逐篇分值的标准差, 度量的是离散而非方向 — 一个当年均值为零的银行, 可能是全部报道中性 (标准差零, 低暴露), 也可能是正负报道对半开 (标准差最大, 高暴露), 本家族区分这两种状态而均值不能。与 tone_volatility 的区别: 后者是三年滚动窗口上银行-年情感均值序列的时间序列标准差, 度量跨年基调不稳; 本家族的分歧分量是单一年度内跨文章的横截面标准差, 度量同期口径分裂, 时间结构完全不同。与 fintech_share、attention_pct 等占比类注意力测度的区别: 占比刻画金融科技话题在该银行全部报道中的相对显著度, 不含分歧维度。与 concern_score 的区别: 该指标同为覆盖乘以情感的复合结构, 但其情感分量是负偏比率的水平量, 构念是"担忧强度", 与本家族"分歧强度"正交。与 fintech_intensity 嵌入测度的区别: 后者以语义嵌入度量文本内容与金融科技构念的语义贴近度, 属内容维; 本家族属反应维, 度量媒体对该内容的评价离散。

【已知局限与稳健性梯子】

已知局限有五。第一, 样本量敏感: 标准差乘数要求年内至少两篇, 少篇银行-年的标准差本身噪声极大, 小银行的暴露度估计精度系统性低于大银行, 建议稳健性检验中按篇数设阈值截尾或以篇数加权。第二, 投票分值离散于三点支撑集, 标准差的取值范围与分布形态受离散化约束, 跨银行比较水平时应意识到这不是连续情感的标准差; 词典与 BERT 连续分值的对应标准差列 (各词典 tone_std、各 BERT 模型分布形状族) 构成天然的测量替代梯子。第三, 覆盖乘数 track-agnostic 而分歧乘数逐轨, 因此三轨复合指标间的差异完全由分歧乘数驱动, 解读跨轨差异时不可归因于覆盖差异。第四, ss 轨的回退语义随上游继承: 无银行与金融科技同句共现的文章, 其 ss 轨文本回退为全文正文 (镜像 ctx 回退公理, 回退行以 ss_is_fallback 标记, 与 full 共享 n_articles 分母), 故 ss 轨标准差在高回退率银行-年上向 full 轨收敛, 属预期行为而非缺陷。第五, 乘积形式与对数变换是研究者选择, 未做跨叙事归一化; 对函数形式的敏感性可用两乘数分别进入回归并加交乘项的展开式规格作检验。开发环境 T=2 切片上, 部分年份截面观测不足导致 _z 列大面积跳过、少篇银行标准差缺失, 均为预期退化, 生产 T=18 面板不受此限。稳健性梯子汇总: 三轨并排 (full canonical、ctx 与 ss 条件轨)、原始与 z 化两量纲、情感引擎替代 (三家大模型逐家 tone_std、六词典、三 BERT 模型的对应离散测度), 每一级各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。

## VAR: fintech_exposure_full

【变体差分】

本列是家族 canonical 列 (tier=core, 2026-07-10 类别六扩围签核), 轨道为 full 轨: 分歧乘数取 llm_vote_tone_std_full, 即逐篇"标题 prepend 加全文正文"文本上三家大模型多数投票分值的银行-年样本标准差。full 轨在三轨体系中的特殊地位有三重来源, 决定了本列作 canonical 的合理性。第一, 门控地位: 自 2026-06-29 full-only 留篇门控口径生效后, 一篇文章是否计入银行金融科技报道宇宙只由 llm_verified_full 决定, full 轨是唯一定义行宇宙的轨道, 其余两轨是该宇宙之上的条件测度; 因此本列的两个乘数在口径上最自洽 — 覆盖乘数 ln_news_coverage 数的正是 full 轨门控通过的篇数, 分歧乘数也在同一批文章的 full 轨分值上计算, 分子分母宇宙完全重合。第二, 信息完整性: full 轨情感基于文章全部内容判定, 不受实体窗口或同句共现截取带来的上下文丢失影响, 其逐篇分值的横截面离散最接近"媒体对该银行金融科技叙事的整体评价分歧"这一目标构念; ctx 与 ss 轨的截取在提升银行针对性的同时也引入截取噪声, 故按测量目标的贴合度排序, full 居首。第三, 体系一致性: 面板主线论文族的处理变量主轨均已切换为 full 轨 (如主线情感处理变量 llm_vote_tone_full), 本列与之同轨, 保证同一回归内处理变量与暴露调节变量的文本口径一致, 避免跨轨交乘的解释歧义。计算细节与家族公式完全一致: 零新闻行 NaN、单篇银行-年因样本标准差未定义而 NaN、缺列时整列 NaN 加响亮告警。与本列相对, ctx 与 ss 版本是并排稳健性轨, 三者各自 just-identified 进入各自规格, 互为稳健性、不分主次, 禁混入同一 over-identified Hansen J; 与 fintech_exposure_full_z 的关系是同一信息的量纲变换, 择一入模。论文表格中若只报告一列, 应报告本列或其 z 化版本, 并在稳健性附表并排呈现 ctx 与 ss 轨结果。

数值解读的两个典型端点情形值得写明。高值端: 某银行当年被大量报道且正负评价并存 (例如既有金融科技合作落地的正面报道又有技术风险事件的负面报道), 两个乘数同时高企, 本列取全样本高位 — 这正是构念意义上"深陷分歧叙事"的银行-年, 也是叙事暴露最可能传导到融资成本、估值与监管注意力的状态。低值端有两条路径, 经济含义不同却在指标上等价: 报道多但口径高度一致 (标准差近零, 常见于大行的程式化正面报道), 或报道极少 (对数覆盖近零); 若研究设计需要区分这两种低暴露, 应将两个乘数拆开检验。缺失端: 零新闻行与单篇行均为 NaN 而非零, 回归样本因此天然剔除无新闻银行-年, 与面板情感变量的样本选择口径一致, 无需额外处理但须在样本描述中说明。测量替代梯子上, 本列的分歧乘数取三家模型多数投票的分值标准差; 面板同时落有三家模型各自的逐家分值标准差 (逐家 tone_std 列族) 与六词典、三 BERT 模型的对应离散测度, 以其替换分歧乘数可构造本列的引擎替代变体, 各替代各自 just-identified 并排、互为稳健性不分主次, 同受禁混 Hansen J 铁律约束。开发 T=2 切片上本列非空行稀少且横截面离散度可能近零 (生产日志的自动判读会给出区分度弱的警示), 属预期退化; 生产 T=18 面板上, 十八个年度截面与百余家银行足以支撑本列作为连续处理变量的识别功率。

## VAR: fintech_exposure_ctx

【变体差分】

本列与 canonical 列 (fintech_exposure_full) 的唯一差分是分歧乘数的轨道: 取 llm_vote_tone_std_ctx, 即逐篇 ctx 轨文本 (标题 prepend 加目标银行实体上下文窗口) 上三家模型投票分值的银行-年样本标准差; 覆盖乘数 ln_news_coverage 为 track-agnostic 标量, 与 full 版完全同值。因此本列与 canonical 的全部数值差异都来自"实体窗口截取是否改变逐篇情感判定的横截面离散"。ctx 轨的测量意图是剔除同篇文章中与目标银行无关段落的情感污染 — 一篇同时评论多家银行的行业综述, full 轨分值混入了对其他银行的褒贬, ctx 轨只看目标银行邻近文本, 银行针对性更强; 代价是窗口截取可能丢失影响整体基调的上下文。行宇宙口径须注意: ctx 是 conditional-on-full 测度轨, 其行集合是 full-only 门控留篇集的子集, 本列不拥有独立的留篇判定; 若上游 ctx 轨情感列未落盘, 本列整列 NaN 并记录告警而非静默缺列。使用定位: 本列是 canonical 的并排稳健性轨, 与 full、ss 版本各自 just-identified 进入各自回归, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 主结论若在 full 轨成立而 ctx 轨翻转, 提示效应可能由非目标银行内容驱动, 是重要的诊断信号而非简单的稳健性失败。

## VAR: fintech_exposure_ctx_z

【变体差分】

本列是 fintech_exposure_ctx 的年度截面标准化版本, 与原始列的唯一差分是量纲变换: 在每个年度截面内, 对有新闻覆盖 (n_articles 大于零) 的银行-年子样本计算该年均值与标准差, 作 z 变换 (减均值除标准差)。守卫条件全部继承标准化引擎: 年内有效观测少于三个的年份整年跳过 (该年 z 值 NaN), 年截面标准差小于十的负十次方视为零方差跳过, 整列非空观测少于十个则该列整体不进入标准化, 零新闻行保持 NaN, 原始列不被覆盖。标准化的方法学动机是 Fama-MacBeth 式截面可比性: 金融科技媒体报道总量在样本期内数量级增长, 原始暴露度的量纲随年份漂移, 直接入池回归时系数被高覆盖年份主导; z 化后每年截面归一至零均值单位方差, 系数可读作"暴露每高一个当年截面标准差, 因变量变动 β 单位", 跨年可比。使用注意有二: 其一, 本列与原始 ctx 列是同一信息的两种量纲, 在同一规格中只能择一, 并排报告属规格稳健性; 其二, 本列继承 ctx 轨的全部轨道语义 (conditional-on-full 行宇宙、实体窗口截取), 与 full_z、ss_z 并排时同样适用三轨铁律 — 各自 just-identified、互为稳健性不分主次、禁混同一 over-identified Hansen J。开发 T=2 切片上因年截面观测稀薄, 本列大面积 NaN 属预期退化。

## VAR: fintech_exposure_full_z

【变体差分】

本列是 canonical 列 fintech_exposure_full 的年度截面标准化版本, 差分维度是量纲而非轨道: 分歧乘数仍为 full 轨投票标准差, 数值经逐年截面 z 变换 (对 n_articles 大于零的银行-年, 减去当年截面均值、除以当年截面标准差)。跳过守卫与家族公式一致: 年内有效观测不足三个、年截面数值零方差、整列非空不足十个这三种情形分别导致该年或该列不产 z 值; 原始列保留, 本列以 _z 后缀新增。作为 canonical 的 z 化形态, 本列是回归表中最推荐的入模版本: 主线论文的处理变量与控制变量多以标准化形态进入 (面板另有 llm_vote_tone_full_z 等同构 z 列), 本列与之量纲对齐, 系数直接可比, 且"一个截面标准差的叙事暴露变化"是比原始乘积单位远更可解释的效应语言。须注意三点: 第一, z 变换是逐年截面操作, 保留截面内排序但抹平跨年水平差异, 若研究问题本身关心暴露度的时间序列增长 (如金融科技叙事的整体升温), 应使用原始列而非本列; 第二, 本列与原始 full 列择一入模, 并排属规格稳健性; 第三, 与 ctx_z、ss_z 构成三轨 z 化并排, 各自 just-identified、互为稳健性不分主次, 禁混同一 over-identified Hansen J。Stata 出口标签为 Fintech Exposure Z (Full)。

## VAR: fintech_exposure_ss

【变体差分】

本列与 canonical 列的差分维度是轨道: 分歧乘数取 llm_vote_tone_std_ss, 即逐篇 ss 轨文本上投票分值的银行-年样本标准差; 覆盖乘数与其余两轨同值 (track-agnostic)。ss 轨是三轨中银行针对性最强的一轨: 其文本由标题加"目标银行与金融科技词在同一句及其前后 N 句窗口内共现"的句段构成 (窗口半径由 context_window.ss_sentence_radius 配置, 默认一句; 该键与 stage 13 共现硬过滤的 sentence_radius 是两个不同键), 情感判定聚焦于银行与金融科技被同一句法单元直接关联的最强证据文本。回退语义是本列解读的承重点, 以 CLAUDE.md 口径为准: 当一篇留篇文章内不存在银行与金融科技的同句共现时, 其 content_ss 回退为全文正文 (镜像 ctx 回退公理), 该行 ss_is_fallback 置真, 且与 full 轨共享 n_articles 分母; 上游金融科技词表不可用的极端情形下全部行回退, 属优雅降级而非报错。因此在同句共现稀疏的银行-年, 本列的分歧乘数向 full 轨收敛, 观察到 ss 与 full 数值接近时应先检查回退率再下结论。本列同为 conditional-on-full 测度轨, 行宇宙是 full-only 门控留篇集的子集; 上游 ss 轨情感列未落盘时整列 NaN 加告警 (生产代码对 ss 缺列与 ctx 缺列采用同一优雅跳过口径)。使用定位: 与 full、ctx 版本各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。

## VAR: fintech_exposure_ss_z

【变体差分】

本列是 fintech_exposure_ss 的年度截面标准化版本, 差分由两个维度叠加而成: 轨道上继承 ss 轨全部语义 (同句共现窗口文本、无共现回退全文正文并以 ss_is_fallback 标记、与 full 共享 n_articles 分母、conditional-on-full 行宇宙), 量纲上经逐年截面 z 变换 — 对当年有新闻覆盖的银行-年子样本减截面均值除截面标准差, 年内有效观测少于三个或截面零方差的年份跳过, 整列非空不足十个则不标准化, 零新闻行保持 NaN, 原始 ss 列不被覆盖。本列的独特价值在于: ss 轨原始值的截面分布受当年同句共现密度与回退率的影响, 不同年份间水平不可直接比较, z 化在很大程度上吸收了这类年份效应, 使 ss 轨暴露度可以与 full_z、ctx_z 在同一效应语言下并排呈现 ("一个截面标准差"的统一单位)。解读时仍须携带 ss 轨的回退警示: 高回退率年份的本列数值本质上是 full 轨信息的 z 化, 跨轨差异证据的强度应结合回退率报告。使用铁律与家族一致: 本列与原始 ss 列择一入模; 与 full_z、ctx_z 三轨 z 化并排时, 各自 just-identified、互为稳健性不分主次, 禁混入同一 over-identified Hansen J。开发 T=2 切片上本列与其余 z 列同样大面积 NaN, 属截面观测稀薄的预期退化, 生产 T=18 面板正常。

<!-- rendered-citations:begin -->
Zhang, X., & Li, Z. (2026). FinTech and branch network expansion: Evidence from China's banking industry. Applied Economics, 58(12), 2321-2336. https://doi.org/10.1080/00036846.2025.2476213
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. Journal of International Financial Markets, Institutions and Money, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
Liu, J., Chen, S., Su, F., & Liu, J. (2025). Digital transformation disclosure and bank loans: An information heterogeneity perspective. International Journal of Finance & Economics, 30(4), 4004-4038. https://doi.org/10.1002/ijfe.3105
Babina, T., Bahaj, S., Buchak, G., De Marco, F., Foulis, A., Gornall, W., Mazzola, F., & Yu, T. (2025). Customer data access and fintech entry: Early evidence from open banking. Journal of Financial Economics, 169, 103950. https://doi.org/10.1016/j.jfineco.2024.103950
Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. Applied Economics. https://doi.org/10.1080/00036846.2025.2536881
Li, T., Stasinakis, C., Yeo, W. M., & Da Silva Fernandes, F. (2025). Fintech, financial development and banking efficiency: Evidence from Chinese commercial banks. The European Journal of Finance, 31(10), 1245-1295. https://doi.org/10.1080/1351847X.2025.2468481
Dim, C., Sangiorgi, F., & Vilkov, G. (2023). Media narratives and price informativeness. SSRN Working Paper No. 4323093 [Working Paper]. https://doi.org/10.2139/ssrn.4323093
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Koranteng, B., & You, K. (2024). Fintech and financial stability: Evidence from spatial analysis for 25 countries. Journal of International Financial Markets, Institutions and Money, 93, 102002. https://doi.org/10.1016/j.intfin.2024.102002
Zheng, H., & Mao, M. Q. (2024). Fintech mergers and acquisitions. Journal of International Money and Finance, 143, 103076. https://doi.org/10.1016/j.jimonfin.2024.103076
Fang, Y., Wang, Q., Wang, F., & Zhao, Y. (2023). Bank fintech, liquidity creation, and risk-taking: Evidence from China. Economic Modelling, 127, 106445. https://doi.org/10.1016/j.econmod.2023.106445
Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J. (2021). Does fintech innovation improve bank efficiency? Evidence from China's banking industry. International Review of Economics & Finance, 74, 468-483. https://doi.org/10.1016/j.iref.2021.03.009
Wang, R., Liu, J., & Luo, H. (2021). Fintech development and bank risk taking in China. The European Journal of Finance, 27(4-5), 397-418. https://doi.org/10.1080/1351847x.2020.1805782
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Boot, A., Hoffmann, P., Laeven, L., & Ratnovski, L. (2021). Fintech: What's old, what's new?. Journal of Financial Stability, 53, 100836. https://doi.org/10.1016/j.jfs.2020.100836
Thakor, A. V. (2020). Fintech and banking: What do we know?. Journal of Financial Intermediation, 41, 100833. https://doi.org/10.1016/j.jfi.2019.100833
Cheng, M., & Qu, Y. (2020). Does bank FinTech reduce credit risk? Evidence from China. Pacific-Basin Finance Journal, 63, 101398. https://doi.org/10.1016/j.pacfin.2020.101398
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
<!-- rendered-citations:end -->
