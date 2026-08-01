---
family_id: F159
columns:
- collab_disagree_frac
- collab_frac
- collab_freerider_frac
- collab_quietworker_frac
unit: 比率/占比 (proportion, [0,1], bank-year 层无量纲)
formula: "collab_frac = n_articles_collab / n_articles_llm_valid (full 轨共识 innovation_collab_mode_full=='外部协同' 且 llm_vote_score_full 非缺失的篇数 / full 轨 LLM 判定有效留篇数; 分母为 0 置 NaN); collab_<X>_frac (X ∈ disagree, freerider, quietworker) = n_articles_collab_<X> / n_articles_collab_bothvalid (both_valid = full 与 ctx 归一化标签均 ∈ 白名单 [自主研发, 外部协同]; n_bothvalid < 5 强制 NaN; 源列缺失回退物理分母 + n_articles < 5 门)"
producer: news_process/pipeline/panel/encode.py (innovation_collab_mode 聚合块 → indep_frac/collab_frac) ; news_process/pipeline/panel/encode_collab.py::derive_residual_signals + aggregate_d4_panel (D4 残差三列)
upstream:
- 15_fintech_intensity.parquet (stage 21 输入)
- 21_tone_llms.parquet (innovation_collab_mode_full / innovation_collab_mode_ctx 三家共识列)
citations:
- doi: 10.1016/j.techfore.2026.124581
  type: journal
  authors: Dehghani, M. A., Brauneis, A., & Karavidas, D.
  year: 2026
  title: "Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions"
  venue: Technological Forecasting and Social Change
  vol: 226
  pages_or_artno: "124581"
- doi: "10.3390/jrfm18100587"
  type: "journal"
  authors: "Gigante, G., Galotta, L., & Scarlini, F."
  year: 2025
  title: "Market Reactions to Fintech M&A: Evidence from Event Study Analysis of Financial Institutions"
  venue: "Journal of Risk and Financial Management"
- doi: 10.1016/j.intfin.2026.102306
  type: journal
  authors: Alfhaili, F. A., Bakoush, M., & Wolfe, S.
  year: 2026
  title: "Investing in fintech equity and bank innovation"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 108
  pages_or_artno: "102306"
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.1007/s10693-024-00442-w
  type: journal
  authors: Alfhaili, F. A., Bakoush, M., & Wolfe, S.
  year: 2025
  title: "The role of banks' business models in their FinTech acquisitions"
  venue: Journal of Financial Services Research
- doi: 10.1002/smj.3729
  type: journal
  authors: Burford, N., Shipilov, A., & Furr, N.
  year: 2025
  title: "Ecosystem synergies as drivers of acquisitions"
  venue: Strategic Management Journal
  vol: 46
  issue: 13
  pages_or_artno: 3218-3251
- doi: 10.1111/joms.13063
  type: journal
  authors: Chen, X., Yang, Y., & Wei, J.
  year: 2025
  title: "How do new ventures thrive in ecosystem venturing: The impacts of alliance strategy and technology interdependence"
  venue: Journal of Management Studies
  vol: 62
  issue: 2
  pages_or_artno: 565-596
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1080/00036846.2025.2536881
  type: journal
  authors: Wu, M., Shen, L., Wu, T., & Shao, Y.
  year: 2025
  title: "Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China"
  venue: Applied Economics
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1016/j.frl.2023.104779
  type: journal
  authors: Kueschnig, M., & Schertler, A.
  year: 2024
  title: "Fusing futures: Financial institutions' stock price response to fintech acquisitions"
  venue: Finance Research Letters
  vol: 59
  pages_or_artno: "104779"
- doi: 10.3386/w33297
  type: wp
  authors: Puri, M., Qian, Y., & Zheng, X.
  year: 2024
  title: "From competitors to partners: Banks' venture investments in fintech"
  venue: NBER Working Paper No. 33297
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: "Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis"
  venue: Journal of Product Innovation Management
  vol: 41
  issue: 4
  pages_or_artno: 793-815
- doi: 10.1016/j.jimonfin.2024.103076
  type: journal
  authors: Zheng, H., & Mao, M. Q.
  year: 2024
  title: "Fintech mergers and acquisitions"
  venue: Journal of International Money and Finance
  vol: 143
  pages_or_artno: "103076"
- doi: 10.1086/727712
  type: journal
  authors: Lerner, J., Seru, A., Short, N., & Sun, Y.
  year: 2024
  title: "Financial innovation in the twenty-first century: Evidence from US patents"
  venue: Journal of Political Economy
  vol: 132
  issue: 5
  pages_or_artno: 1391-1449
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 529-551
- doi: 10.1613/jair.1.12752
  type: journal
  authors: Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M.
  year: 2021
  title: "Learning from disagreement: A survey"
  venue: Journal of Artificial Intelligence Research
  vol: 72
  pages_or_artno: 1385-1470
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1146/annurev-financial-100719-120854
  type: journal
  authors: Vives, X.
  year: 2019
  title: "Digital disruption in banking"
  venue: Annual Review of Financial Economics
  vol: 11
  pages_or_artno: 243-272
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: "Bramoullé, Y., Djebbari, H., & Fortin, B."
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: "Disagreement and the stock market"
  venue: Journal of Economic Perspectives
  vol: 21
  issue: 2
  pages_or_artno: 109-128
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: "The symbolic management of strategic change: Sensegiving via framing and decoupling"
  venue: Academy of Management Journal
  vol: 49
  issue: 6
  pages_or_artno: 1173-1193
- doi: 10.1002/smj.507
  type: journal
  authors: Laursen, K., & Salter, A.
  year: 2006
  title: "Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms"
  venue: Strategic Management Journal
  vol: 27
  issue: 2
  pages_or_artno: 131-150
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: 10.1016/S0048-7333(01)00120-2
  type: journal
  authors: Hagedoorn, J.
  year: 2002
  title: "Inter-firm R&D partnerships: An overview of major trends and patterns since 1960"
  venue: Research Policy
  vol: 31
  issue: 4
  pages_or_artno: 477-492
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.2307/2529310
  type: journal
  authors: Landis, J. R., & Koch, G. G.
  year: 1977
  title: "The measurement of observer agreement for categorical data"
  venue: Biometrics
  vol: 33
  issue: 1
  pages_or_artno: 159-174
- doi: 10.1037/h0026256
  type: journal
  authors: Cohen, J.
  year: 1968
  title: "Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit"
  venue: Psychological Bulletin
  vol: 70
  issue: 4
  pages_or_artno: 213-220
- doi: "10.1016/j.ribaf.2025.102993"
  title: "Competition or cooperation? Disentangling the Bank-FinTech interaction through a hybrid literature review"
  authors: "Costa, D., Querci, F., & Santulli, R."
  year: 2025
  venue: "Research in International Business and Finance"
  type: "journal"
- doi: "10.1108/ijbm-02-2023-0071"
  title: "Enhancing online visibility through strategic alliances: the case of bank-FinTech relationships"
  authors: "Cosma, S., & Pennetta, D."
  year: 2024
  venue: "International Journal of Bank Marketing"
  type: "journal"
new_dois:
- "10.3390/jrfm18100587"
- "10.1016/j.ribaf.2025.102993"
- "10.1108/ijbm-02-2023-0071"
---

## CORE

该文用事件研究法考察2008-2024年90起银行、资管与投行收购金融科技公司交易的短期市场反应及其交易层面与公司层面驱动因素, 为银行外部协同(并购路径)构念提供最新实证锚点。

【构念与来源】
本家族度量的核心构念是银行金融科技创新的协同模式 (collaboration mode), 即媒体报道所呈现的某项银行金科创新到底是银行在组织边界内自主研发完成, 还是通过与外部机构 (金融科技公司, 互联网平台, 科研院所等) 协同合作完成。构念源头是 Chesbrough 于 2003 年提出的开放式创新框架: 有价值的创意既可以来自企业内部也可以来自外部, 企业获取技术能力存在内部研发与外部获取两条基本路径, 两条路径在治理结构, 知识产权归属, 吸收能力要求与信息披露激励上系统性不同。该框架二十余年的实证积累已由 Zhang 等 (2024) 的元分析系统整理, 确认外部开放度与创新产出之间稳健但有条件的正向关系; 更早的奠基性操作化见 Laursen 与 Salter (2006) 对外部搜索广度与深度的度量以及 Hagedoorn (2002) 对企业间研发伙伴关系长期趋势的记录。落到银行业语境, Vives (2019) 指出数字化冲击迫使传统银行在自建技术栈与借力金融科技生态之间作出战略选择; 近年的实证文献分别度量了这一选择的各种外部协同形态: 银行对金融科技公司的风险投资与股权投资 (Puri 等 2024; Alfhaili 等 2026), 金融科技并购及其市场反应 (Alfhaili 等 2025; Kueschnig 与 Schertler 2024; Zheng 与 Mao 2024), 银行与金科公司的战略合作协议 (Wu 等 2025, 中国样本), 以及更一般的生态联盟战略 (Chen 等 2025; Burford 等 2025)。本家族与上述基于交易事件或专利归属 (Lerner 等 2024 用专利受让人区分金融创新的内部产出与外部来源) 的度量互补: 它以媒体新闻文本为原始数据 (Gentzkow 等 2019 意义上的 text-as-data 范式), 用大语言模型逐篇判读报道叙事中呈现的协同模式 (de Kok 2025 系统讨论了生成式大模型在财务会计文本分析中的方法学定位), 因此能覆盖未形成正式交易记录的合作叙事, 也天然携带媒体如何呈现银行创新来源的话语维度。家族含四列: canonical 主列 collab_frac 度量协同模式构念水平 (bank-year 内外部协同报道占比), 其余三列 collab_disagree_frac, collab_freerider_frac, collab_quietworker_frac 是 v3.5.0 D4 跨文本口径残差族, 度量同一篇文章在全文口径与实体近邻上下文口径下协同标签的一致性结构, 兼具测量诊断与言行解耦信号两重身份。用白话说, 这一族变量回答的问题是: 在媒体眼中, 这家银行搞金融科技靠的是自己的技术团队还是靠外面找伙伴, 以及同一篇报道从整体读和贴着这家银行的名字附近读, 给出的答案是否一致。前一个问题由主列回答, 后一个问题由三条残差列回答。之所以值得从媒体叙事而非仅从交易记录度量协同模式, 是因为叙事先于交易且覆盖面更广: 许多合作以框架协议, 联合实验室, 试点项目等形态见诸报端却不进入并购或股权数据库; 同时叙事本身构成银行对外的战略信号发布, 其与近距离事实的偏离正是象征性管理理论 (Fiss 与 Zajac 2006) 关心的对象, 这为残差族提供了独立于测量误差解释的构念空间。

【方法学与计算】
测量链路分文章级判读与面板级聚合两段。文章级判读在 stage 21 (tone_llms) 完成: 三家供应商锁定的大语言模型 (gpt-5.4-nano, gemini-3.1-flash-lite, deepseek-v4-flash) 在字节级冻结的 v8 提示词与温度取零的确定性设置下, 对每篇候选文章独立给出协同模式二分类标签, 标签空间恰为自主研发与外部协同两值; 随后按分类多数决聚合为共识列 innovation_collab_mode_full (以及 ctx, ss 两个文本口径的对应列), 平局或空票时保守降级为自主研发 (等价于均匀先验下的最大后验保守取值), 三家全部失败时该篇该维度置缺失。所有标签进入下游前经统一归一化 (剥首尾空白, 全角空格与内部空白字符), 归一化后不落在两值白名单内的脏标签不计入任何聚合并触发日志告警。留篇门控执行 full-only 口径 (2026-06-29 用户决策): 一篇文章是否进入面板聚合宇宙只看全文轨 llm_verified_full 是否为真, ctx 与 ss 是 conditional-on-full 的条件测度与稳健性轨, 不参与留篇决定。面板级聚合在 encode.py 的 innovation_collab_mode 聚合块完成: 先按 full 轨共识标签把留篇文章分为自主研发与外部协同两组, n_articles_collab 计外部协同组内 llm_vote_score_full 非缺失的篇数, 然后 collab_frac 等于 n_articles_collab 除以 n_articles_llm_valid (该 bank-year 内 full 轨大模型判定有效的留篇总数), 分母为零时置缺失而非假零。代码同时执行分割恒等式校验: n_articles_llm_valid 大于等于自主研发篇数与外部协同篇数之和, 差额恰为协同维度缺标的文章, 由八格分解的 cell_NA 桶列兜底跟踪, 这保证 collab_frac 与 indep_frac 之和以一为上界但不必然等于一。D4 残差三列的链路在 encode_collab.py: derive_residual_signals 先在文章级构造三个布尔信号, 其定义域是 both_valid 掩码, 即同一篇文章的 full 口径与 ctx 口径归一化标签均落在两值白名单内; collab_disagree 为两口径标签不一致且 both_valid, collab_freerider 为 full 口径判自主研发而 ctx 口径判外部协同, collab_quietworker 为反向组合, 由构造可证三条不变量: freerider 与 quietworker 互斥, 二者之和恒等于 disagree, 任一口径缺失或脏标签时三信号一律为假而非缺失。aggregate_d4_panel 随后把信号计数聚合到 bank-year, 占比列分母采用与分子同域的 n_articles_collab_bothvalid 而非物理文章总数 (若以物理总数为分母, 缺标文章会被静默记为无分歧, 系统性下压分歧率); both_valid 篇数小于五的格子占比强制置缺失以抑制小样噪声; 仅当上游标签源列整列缺失, 无法重建 both_valid 时才回退物理分母并改用总篇数小于五的门。聚合层还对 ctx 口径覆盖率做基线两倍标准差的自适应告警, 结果以 d4_data_quality_flag 字符串列持久化进面板供论文披露。D4 残差有意只比较 full 与 ctx 两个属性口径而不产 ss 残差, 但其真实理由不是 ss 轨缺属性标签: stage 21 同样对 ss 口径写回协同属性列 innovation_collab_mode_ss, 面板层亦产 ss 口径的对角协同占比列 collab_frac_cm_ss, ss 属性标签客观存在。D4 只取 full 与 ctx 的实际口径依据是八格 cell_id 分解在 encode.py 中仅对 full 与 ctx 两口径展开 (八格由 full 与 ctx 两个二值属性维交叉而成, ss 不进入该交叉表), 残差信号定义域是 full 与 ctx 的 both_valid 掩码, 因此三条残差臂只可能落在 full 对 ctx 这一对口径上, 与设计口径自洽。

再往上游追一层, 进入 stage 21 的文章宇宙本身由两道前置工序界定。其一是 stage 13 共现硬过滤: 只有目标银行与至少一个金融科技词在句窗邻近共现的文章才被保留, 判定采用生产口径的正负一句窗口且标题参与匹配, 这保证协同标签判读的对象确属银行金科关联报道而非泛金融新闻。其二是 stage 14 文本口径物化: 全文口径为标题前置拼接正文全文, 实体近邻上下文口径为标题前置拼接目标银行实体周边窗口文本, 同句共现口径为标题前置拼接银行与金科词严格同句的片段 (无同句共现时按镜像 ctx 的回退语义退回全文正文并以回退旗标记录)。D4 残差比较的正是前两个口径下协同标签的一致性, 因此其构念含义可以精确表述为: 全文尺度叙事与实体近距离叙事对创新来源归属的呈现是否一致。可复现性方面, 全部大模型调用经由逐篇逐轨逐模型的持久化缓存落盘, 缓存键包含模型名, 提示词文本, 提示词版本与温度, 温度取零下同一输入的输出字节级确定; 缓存全命中时整条判读链路可在离线守卫下零成本逐字节复现, 这使本家族满足 de Kok (2025) 对生成式模型文本测度提出的可审计与可复现要求。面板落盘还有一处刻意的不对称语义须知: 计数列 (n_articles_collab 及各残差计数列) 在无对应文章的格子填零并取整数类型, 而全部占比列在零新闻或分母无效的格子一律保持缺失, 缺失与真实零占比在下游回归中不可互换。

【识别策略定位】
collab_frac 是 P5 论文 (bank_fintech_collab) paper_spec 中 treatment 的主列, 即正文级主处理变量: 研究设计把媒体叙事层面的外部协同倾向作为银行开放式创新姿态的可观测代理, 检验其对银行后续真实协同行为 (结局变量为金融科技并购哨兵列, 财务面板接入时构造) 与经营后果的预测力, 呼应 Puri 等 (2024) 从竞争者到伙伴的关系演化命题与 Alfhaili 等 (2025) 银行商业模式决定金科收购倾向的发现。须先明确处理变量与结局变量是两套独立空间: 本列只承担处理侧, 结局侧的并购哨兵列在财务面板到位前是占位, 二者不可互换角色, 也不可把本列同时放进同一方程的两侧构造机械相关。内生性威胁在此设定下有三条具体来路: 其一是联立性, 已经启动外部合作谈判的银行更可能主动向媒体释放协同叙事, 报道与行为互为因果; 其二是遗漏变量, 银行的数字化雄心, 高管更替或监管窗口指导可能同时驱动协同叙事与经营后果; 其三是反射问题, 同业银行的协同姿态互相影响, 直接把同组均值放进回归会遭遇 Manski (1993) 指出的内生与外生效应不可分难题。识别层面, 该列接入项目统一的 IV 扩展三引擎生成的工具变量列族与对应的两阶段最小二乘模板, 三引擎分别针对上述三条威胁: 同组 leave-one-out 均值引擎以剔除自身后的同组同业均值为工具, 其排除性依赖网络局部结构提供的排他变异, 逻辑上承接 Bramoullé 等 (2009) 用网络拓扑破解反射问题的识别路线; 广义 Bartik 暴露引擎把年度层面的行业协同叙事冲击按银行的事前暴露份额分摊, 识别假设可以在份额外生或冲击外生两条路线之间选择并分别论证, 相应的诊断与陷阱清单遵循 Borusyak 等 (2025) 对 shift-share 工具的操作指引, 例如须报告有效样本集中度并警惕暴露份额本身与结局趋势相关的违例; 媒体来源 house-style 暴露引擎利用不同媒体在协同话题上的稳定风格差异乘以银行的事前媒体构成, 排除性要求媒体风格只经由报道叙事而不直接作用于银行经营。三引擎各自单独入方程, 每条 IV 规格 just-identified, 这是刻意的设计而非省事: 把三类工具堆进同一方程做过度识别检验, 等于假设三条排除性同时成立且残差同质, 一旦其中一条工具弱或违例, Hansen J 的拒绝无法归因, 反而制造虚假的联合有效性外观。固定效应结构上, 主规格吸收银行与年份两维固定效应, 银行维吸收规模与所有制等时不变曝光差异, 年份维吸收金融科技政策周期与行业叙事潮汐, 识别变异因此来自银行内跨年的协同叙事变动。稳健性层面, 协同维度经 LLM_CLASS_SPEC 三元映射接入 per-model 跨厂商梯子: 共识列 collab_frac 是 canonical headline, 三家模型各自的同名占比列是 co-equal 的跨厂商稳健臂, 互为稳健性, 不分主次; 跨模型多重假设的族错误率控制不依赖声明式文档, 而由根级 rwolf 模板 (27 号表 A12 的分类维度面板) 按 Romano 与 Wolf (2005) 的逐步降压程序执行; 跨模型并表比较时各臂系数一律先经标准化再报告, 以消除各模型原始方差量纲差异对量级解读的干扰。此处必须复述项目口径铁律: 共识列与三家 per-model 列, full 与 ctx 与 ss 三轨, 以及本家族 canonical 列与 D4 残差诊断列, 全部是各自 just-identified 的并排规格, 互为稳健性, 不分主次, 严禁把任意两条臂混进同一个 over-identified 的 Hansen J 检验; 它们共享测量对象但不构成同一矩条件系统的多工具。

【与相邻测度的构念区分】
与 indep_frac 的关系是同一分类的两个类别占比, 分母同为 n_articles_llm_valid, 但因协同维度缺标篇的存在二者之和小于等于一, 不能把其中一列当作另一列的线性恒等变换使用。与 collab_frac_cm 及 collab_frac_cm_ss 的区分是文本口径: 后两者是 ctx 与 ss 口径的对角轨 (ctx 分子配 ctx 分母, ss 分子配 ss 分母), 属 conditional-on-full 稳健轨, 主列恒为 full 口径的 collab_frac。与 sub_frac 及 tech_frac 的区分是构念维度: 三者同属 LLM 分类维度三元组, 分别对应实质性对象征性, 底层技术对应用场景, 自主研发对外部协同, 三个维度在八格 cell_id 分解中各占一位, 协同维是最低位。与 tone_gap_indep_collab 的区分是度量类型: 后者是自主研发组与外部协同组的大模型投票情感均值之差 (带最小五篇守门), 度量的是情感纯度差距而非构念占比。与 llm_agreement_rate 族的区分是分歧主体: 该族度量三家模型之间的判读分歧, 而本家族 D4 三残差度量的是同一共识标签跨全文与实体近邻两个文本取材口径的分歧, 前者是评审者间信度问题 (Uma 等 2021 综述意义上的标注分歧), 后者是叙事结构问题; 两类分歧可以同时存在于同一篇文章且互不蕴含, 模型间高度一致的标签仍可跨口径翻转, 反之亦然。与金融学分歧文献里的投资者分歧构念 (Carlin 等 2014 的机构预测离散度, Li 与 Luan 2025 的新闻分歧) 的区分是分歧的承载主体与定价含义: 那一支度量的是市场参与者对同一资产的信念离散并检验其风险溢价含义, 本家族 disagree 列度量的是同一文本内部两个取材尺度对事实归类的不一致, 它先是测量结构量, 只有叠加解耦理论解释后才升格为行为信号, 引用该支文献是为论证叙事分歧可携带信息这一前提, 而非宣称二者同构。与曝光类度量 (n_articles, fintech_share, attention 族) 的区分是条件结构: 曝光类回答该银行被报道了多少, 本家族回答的是在被报道且被判定为银行金科关联报道的条件下, 叙事把创新来源归到哪边, 因此本家族全部占比列都是 conditional-on-coverage 量, 银行间曝光深度差异已被分母吸收, 但条件化也意味着零覆盖格子是缺失而非零, 样本进入本身可能有选择。与 IV 扩展引擎产出的 leave-one-out 同组协同均值列的区分是角色: 后者是为识别而造的工具变量, 度量对象是同业而非本行, 只应出现在第一阶段与工具位, 绝不可当作本行协同倾向的替代测度直接解读。最后, 与基于交易事件的协同度量 (并购公告, 股权投资记录) 的区分是数据生成过程: 本家族捕捉媒体叙事中的协同呈现, 涵盖未落地为交易的合作意向与框架协议, 也因此携带媒体选择与框架化偏差, 这既是局限也是 D4 残差族得以存在的构念空间。

【文献定位】
本家族在三支文献的交汇处。第一支是开放式创新与联盟战略文献: Zhang 等 (2024) 的元分析框架确立了外部开放度的前因后果谱系, Chen 等 (2025) 与 Burford 等 (2025) 把联盟与生态协同和技术互依, 并购动因连接起来, Dehghani 等 (2026) 则直接考察金融机构知识产权管理实践中的开放式创新模式, 为协同维度在金融科技语境下的效度提供最新锚点。Costa, Querci 与 Santulli (2025, Research in International Business and Finance) 通过混合式文献综述系统梳理银行与金融科技公司互动中的竞争与合作两条路径, 为本家族协同模式构念的产业背景提供最新文献定位; Cosma 与 Pennetta (2024, International Journal of Bank Marketing) 以意大利金融科技公司样本考察股权型与合约型银行战略联盟对其线上可见度的差异化效应, 为外部协同的具体治理形式 (股权对合约) 提供实证锚点。第二支是银行金科互动的金融经济学实证: Puri 等 (2024), Alfhaili 等 (2025, 2026), Kueschnig 与 Schertler (2024), Zheng 与 Mao (2024) 与 Wu 等 (2025) 分别覆盖股权投资, 收购, 战略合作三类外部协同形态及其风险与绩效后果, Lerner 等 (2024) 提供金融创新专利归属的长时段证据, 本家族把这些交易层构念前移到媒体叙事层。第三支是文本测度方法学: Gentzkow 等 (2019) 确立文本即数据的一般框架, de Kok (2025) 讨论生成式大模型作为文本标注引擎的可复现性要求 (温度取零, 提示词冻结, 逐篇缓存正是本管线的实现), Uma 等 (2021) 为多标注者分歧的建模提供分类学。D4 残差族另有专属理论锚: Fiss 与 Zajac (2006) 的象征性管理与解耦理论预言组织对外话语与贴近行动的信息可以系统性分离, freerider 与 quietworker 两列正是该解耦构念在协同维度上的方向化操作化; 而 disagree 列与新闻文本分歧度量文献相通, Hong 与 Stein (2007) 给出分歧作为资产定价基本要素的理论综述, Li 与 Luan (2025) 证明基于新闻的投资者分歧度量携带定价信息, 支持把叙事层分歧本身当作研究变量而非纯测量噪声。

【已知局限与稳健性梯子】
第一, 媒体选择偏差: 进入语料的是被报道的创新而非创新总体, 大银行与话题性合作被系统性过度代表; 以大模型有效篇数为分母的占比构造部分中和了规模性曝光差异, 但报道议题结构漂移仍可能与银行特征相关, 论文侧以银行与年份固定效应及媒体来源暴露工具变量缓解。第二, 大模型判读的测量误差非经典且可能跨厂商相关: 三家模型若共享训练语料或提示词敏感性, 其误差不独立, 多数决共识只能压缩独立噪声而压不掉共同偏误; 应对是 per-model 跨厂商梯子 (三家各自 just-identified 并排, 互为稳健性, 不分主次, 禁混同一 over-identified Hansen J), 人工盲标双编码协议与跨模型一致性系数, 以及 Romano 与 Wolf (2005) 式族错误率控制。一致性系数的报告口径本身有陷阱: 项目采用名义且缺标感知的 Krippendorff alpha 以容纳不同模型标签空间的类目数差异, 另报 Cohen 系列 kappa 时必须先把缺标哨兵码重映射为非负码, 否则负值哨兵与负面类目冲突会污染系数; 系数量级的解读参照 Landis 与 Koch (1977) 的惯例区间但只作描述性基准, 不作为通过与否的机械阈值, 加权处理有序分歧的方案见 Cohen (1968) 传统, 本维度为二值名义标签故不加权。第三, 平局保守降级方向性: 平局归自主研发使 collab_frac 在边际上偏向低估外部协同占比, 属保守偏误, 方向可知且在跨模型臂间同构。与之相邻的构念压缩局限: 二值标签空间对混合形态报道 (同一篇既述自研投入又述外部签约) 强制单标签, 判读将取叙事主线, 该强制在构念上等价于把连续的开放度压缩为二分, 与 Laursen 与 Salter (2006) 连续广度深度度量相比损失了强度信息, 论文解释系数时应以叙事主线占比而非开放度水平措辞。另须提示占比变量的计量性质: 分子是小计数, 分母亦有限, 占比在小分母格子呈粗粒化跳变 (五篇分母下只能取六个值), 对数或比率变换在零附近的问题与 Cohn 等 (2022) 对计数类结局的告诫同源, 处理侧使用时以线性规格加固定效应为主, 避免对占比做非线性变换后再解释边际效应。第四, D4 残差的分母覆盖依赖 ctx 口径实体上下文抽取质量, both_valid 覆盖率不足时占比虽经最小五篇守门与质量旗标披露, 仍应在解释时对照 n_articles_collab_bothvalid 列报告覆盖率。第五, 早期试跑盘小样退化: 极小年份深度下大量格子触发最小样本门置缺失属预期行为, 不构成生产口径下的推断依据。第五之外还有一处口径细节: ctx 口径的实体窗口截断可能遗漏远离银行名称但语义相关的协同描述, 使 ctx 标签在长篇多主体报道中相对全文标签更保守, 这一机制性差异意味着 D4 残差不可全部归因于叙事解耦, 解释时应与覆盖率披露并读。第六, 构念边界: 协同标签判读的是报道叙事呈现而非法律意义上的合作关系, freerider 与 quietworker 的言行解耦解释 (Fiss 与 Zajac 2006) 应表述为疑似信号而非行为指控; 同理, 主列的高协同占比也不等于合作规模或投入强度, 它是篇数占比而非金额加权量, 与 Zheng 与 Mao (2024) 等交易金额口径的度量在解释上应互补而非互替。梯子全景: 本家族的稳健性结构包括共识对三家 per-model 的厂商梯子, full 对 ctx 对 ss 的文本口径轨 (D4 残差有意仅 full 对 ctx), canonical 占比对 D4 残差诊断的测度族并排; 以上每一维度均为规格稳健性并排, 各臂各自 just-identified, 互为稳健性不分主次, 严禁混入同一 over-identified Hansen J, 亦刻意不做各梯子维度之间的交叉展开以避免规格组合爆炸。

## VAR: collab_disagree_frac

【变体差分】
本列是家族 D4 残差族的总量臂, 区别于 canonical 列 collab_frac 之处在于它不度量构念水平而度量跨文本口径的标签分歧率: 某 bank-year 内, 全文口径 (innovation_collab_mode_full) 与实体近邻上下文口径 (innovation_collab_mode_ctx) 的协同标签均合法且互不一致的文章篇数, 除以两口径均给出合法标签的文章篇数 (n_articles_collab_bothvalid)。分母刻意取 both_valid 域而非物理篇数, 保证分子分母同域, 缺标文章不被静默记为无分歧; both_valid 篇数小于五的格子强制置缺失, 仅在上游标签源列整列缺失时回退物理分母并沿用总篇数小于五的门。由构造恒等式, 本列恰等于 collab_freerider_frac 与 collab_quietworker_frac 之和 (同分母), 是两方向臂的无方向汇总。解释上有两重身份: 其一是测量诊断, 分歧率高的银行年份提示协同标签对文本取材口径敏感, 应在稳健性检验中对照两口径结果 (与三家模型间分歧的 llm_agreement_rate 族严格区分, 那是评审者间信度, 本列是口径间一致性, 概念上对应 Uma 等 (2021) 综述的标注分歧建模传统); 其二是实质信号, 叙事层分歧本身可以携带信息, 新闻分歧度量的定价含义见 Hong 与 Stein (2007) 的理论框架与 Li 与 Luan (2025) 的最新实证。使用口径: 本列与家族 canonical 列及两方向臂各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。伴生计数列 n_articles_collab_disagree 与覆盖列 n_articles_collab_bothvalid 供论文披露分母覆盖率, 数据质量旗标见 d4_data_quality_flag。

## VAR: collab_frac

【变体差分】
本列是家族 canonical 主列, tier 为 core, 亦是 P5 论文 bank_fintech_collab 在 paper_spec 中登记的 treatment 主列 (正文级主处理变量)。精确语义: 对某银行某年份, 分子为 full 轨三家大模型共识标签 innovation_collab_mode_full 等于外部协同且 full 轨投票分非缺失的留篇篇数 (n_articles_collab), 分母为该 bank-year 内 full 轨大模型判定有效的留篇总数 (n_articles_llm_valid), 分母为零时整格置缺失而非假零。文章宇宙由 full-only 留篇门控确定 (2026-06-29 口径, 只看 llm_verified_full), 故本列与同分母的 indep_frac, sub_frac, tech_frac 等分类占比在同一行宇宙上可比。轨道语义: 无后缀即 full 轨, 是三口径中的 canonical; ctx 与 ss 口径的对应物是 collab_frac_cm 与 collab_frac_cm_ss (各自以本口径有效篇数为分母的对角构造), 属 conditional-on-full 稳健轨, 三口径各自 just-identified 并排, 互为稳健性不分主次, 禁混同一 over-identified Hansen J。模型语义: 本列聚合的是三家多数决共识, 平局或空票保守降级为自主研发 (均匀先验最大后验), 因此本列对外部协同占比构成保守方向的边际低估; 三家各自的 per-model 同名占比列经 LLM_CLASS_SPEC 映射并排产出, 与本列 co-equal 互为稳健性, 跨厂商多重检验的族错误率由根级 rwolf 模板按 Romano 与 Wolf (2005) 程序控制, 同样禁与本列混入同一 Hansen J。构念指向: 取值越高表示该银行该年份的媒体叙事越倾向把其金科创新呈现为外部协同 (股权投资, 并购, 战略合作, 联盟等开放式创新路径, 实证锚点见 Puri 等 (2024), Alfhaili 等 (2025, 2026), Zheng 与 Mao (2024), Wu 等 (2025)), 越低则越倾向自主研发叙事; 与 indep_frac 之和以一为上界, 差额为协同维度缺标篇占比, 由八格分解的缺标桶列跟踪, 使用时不得把两列互为恒等补集。识别用法上本列接入 IV 扩展三引擎的工具列族与两阶段最小二乘模板; 跨模型比较回归中系数应经标准化后再并表报告, 以消除各臂原始方差差异。阈值与滞后: 本列无阈值参数与滞后结构, 分母守门仅为分母大于零; 与 D4 残差三列的最小五篇守门口径不同, 不可混用。伴生列语义: 计数列 n_articles_collab 在无协同报道的格子填零并取整数, 而本列在分母为零的格子保持缺失, 零占比与缺失在回归中严格区分; 同分组还并排产出协同组的情感伴生列 (共识投票情感均值, 概率分均值及三家逐模型情感均值, 覆盖三个文本口径), 以及协同维度置信度均值列, 它们度量协同报道的语气与判读确信度, 与本列的占比构念正交, 不可混同。数据链路口径: 本列的行宇宙由 stage 13 银行金科邻近共现硬过滤与 full-only 留篇门控两道闸共同决定, 因此其分母语义是被判定为真实银行金科报道的有效篇数, 而非该银行全部新闻; 判读输出经逐篇持久化缓存, 温度取零下字节级可复现。白话解读: 这个数越接近一, 说明媒体报道里这家银行该年的金融科技动作越多被描述为找外部伙伴一起干 (投资, 收购, 签约, 结盟), 越接近零则越多被描述为自己研发; 论文用它作为银行开放式创新姿态的代理去预测后续真实的对外协同行为与经营后果。跨模型报告口径: 与三家 per-model 臂并表时系数一律先标准化再比较, 显著性经跨模型族错误率程序校正后报告; 各 per-model 臂的分母是该模型自身判定有效的篇数而非共识分母, 各家分母互不相同, 故臂间占比水平不可直接相减解读, 只可比较标准化后的回归系数方向与量级。工具位口径: 本列对应的工具变量列族 (同组剔己均值, 广义 Bartik 暴露, 媒体来源风格暴露) 是识别用途的伴生列, 只进第一阶段, 不是本列的替代测度; 每条 IV 规格恰好识别, 三工具禁堆入同一方程。生产与开发口径差: 早期试跑盘年份深度极小, 大量格子因分母守门置缺失属预期退化, 本列的推断口径以生产全量语料为准。

## VAR: collab_freerider_frac

【变体差分】
本列是 D4 残差族的方向臂之一, 区别于总量臂 collab_disagree_frac 之处在于锁定分歧的特定方向: 分子只计全文口径标签为自主研发 (协同维基线类) 而实体近邻上下文口径标签为外部协同 (对照类) 的文章, 即全文整体叙事把创新呈现为银行自主研发, 但贴近目标银行实体的窗口文本却指向外部协同。分母与总量臂完全相同 (n_articles_collab_bothvalid, both_valid 域, 最小五篇守门, 源列缺失回退物理分母), 且与 collab_quietworker_frac 在文章级互斥, 二者之和恒等于 disagree 臂。命名沿袭实质性维度的言行隐喻 (freerider 原指全文宣称实质而近实体上下文呈现象征的说一套做一套形态), 在协同维度上的直译标签为说而不做; 其理论依据是 Fiss 与 Zajac (2006) 的象征性管理与解耦框架: 组织面向公众的话语框架与贴近具体行动的信息可以系统性脱节, 方向化的口径错位正是解耦的文本痕迹。解释时应表述为疑似解耦信号而非行为认定: 口径错位也可能源于实体上下文抽取窗口截断或大模型对局部语境的判读误差, 故本列兼具测量诊断功能, 使用时应对照 both_valid 覆盖列与质量旗标。口径铁律: 本列与总量臂, 反向臂及家族 canonical 列各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J; D4 残差有意仅比较 full 与 ctx 两口径, 其理由不是 ss 缺属性标签 (stage 21 亦写回 innovation_collab_mode_ss, 面板层亦产 collab_frac_cm_ss), 而是八格 cell_id 分解在 encode.py 中仅对 full 与 ctx 两个二值属性维展开, 残差信号定义域限于 full 对 ctx 的 both_valid 掩码, 故无 ss 对应残差。

## VAR: collab_quietworker_frac

【变体差分】
本列是 D4 残差族与 collab_freerider_frac 严格对称的反方向臂: 分子只计全文口径标签为外部协同 (对照类) 而实体近邻上下文口径标签为自主研发 (基线类) 的文章, 即全文整体叙事把创新呈现为外部协同, 而贴近目标银行实体的窗口文本却呈现自主研发。分母, 守门与回退逻辑与另两条残差臂逐字相同 (n_articles_collab_bothvalid 分母, both_valid 篇数小于五置缺失, 源列缺失回退物理分母加总篇数小于五门), 与 freerider 臂在文章级互斥且两臂之和恒等于 disagree 臂, 三条不变量由构造保证。命名同样沿袭实质性维度隐喻 (quietworker 原指全文低调而近实体上下文呈现实质的做而不说形态), 协同维度上的直译标签为做而不说。构念上, 本列捕捉与 freerider 臂相反方向的叙事解耦: 报道整体强调合作生态框架, 但落到该银行自身的近距离描述却是自建与内部研发, 这类形态在联盟话语盛行而实际技术互依有限的情形下尤其可能出现 (生态联盟叙事与实际技术互依关系的张力见 Chen 等 (2025) 与 Burford 等 (2025) 的讨论), 其解耦解释框架同样锚定 Fiss 与 Zajac (2006)。与 freerider 臂合并使用时只应作为 disagree 的方向分解描述性报告, 或各自单独进入回归; 口径铁律与家族其余列一致: 各臂各自 just-identified 并排, 互为稳健性不分主次, 严禁混入同一 over-identified Hansen J, 且不与三轨或 per-model 梯子做交叉展开。

<!-- rendered-citations:begin -->
Dehghani, M. A., Brauneis, A., & Karavidas, D. (2026). Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions. Technological Forecasting and Social Change, 226, 124581. https://doi.org/10.1016/j.techfore.2026.124581
Gigante, G., Galotta, L., & Scarlini, F. (2025). Market Reactions to Fintech M&A: Evidence from Event Study Analysis of Financial Institutions. Journal of Risk and Financial Management. https://doi.org/10.3390/jrfm18100587
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. Journal of International Financial Markets, Institutions and Money, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2025). The role of banks' business models in their FinTech acquisitions. Journal of Financial Services Research. https://doi.org/10.1007/s10693-024-00442-w
Burford, N., Shipilov, A., & Furr, N. (2025). Ecosystem synergies as drivers of acquisitions. Strategic Management Journal, 46(13), 3218-3251. https://doi.org/10.1002/smj.3729
Chen, X., Yang, Y., & Wei, J. (2025). How do new ventures thrive in ecosystem venturing: The impacts of alliance strategy and technology interdependence. Journal of Management Studies, 62(2), 565-596. https://doi.org/10.1111/joms.13063
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. Applied Economics. https://doi.org/10.1080/00036846.2025.2536881
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kueschnig, M., & Schertler, A. (2024). Fusing futures: Financial institutions' stock price response to fintech acquisitions. Finance Research Letters, 59, 104779. https://doi.org/10.1016/j.frl.2023.104779
Puri, M., Qian, Y., & Zheng, X. (2024). From competitors to partners: Banks' venture investments in fintech. NBER Working Paper No. 33297 [Working Paper]. https://doi.org/10.3386/w33297
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Zheng, H., & Mao, M. Q. (2024). Fintech mergers and acquisitions. Journal of International Money and Finance, 143, 103076. https://doi.org/10.1016/j.jimonfin.2024.103076
Lerner, J., Seru, A., Short, N., & Sun, Y. (2024). Financial innovation in the twenty-first century: Evidence from US patents. Journal of Political Economy, 132(5), 1391-1449. https://doi.org/10.1086/727712
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M. (2021). Learning from disagreement: A survey. Journal of Artificial Intelligence Research, 72, 1385-1470. https://doi.org/10.1613/jair.1.12752
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Vives, X. (2019). Digital disruption in banking. Annual Review of Financial Economics, 11, 243-272. https://doi.org/10.1146/annurev-financial-100719-120854
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131-150. https://doi.org/10.1002/smj.507
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. Research Policy, 31(4), 477-492. https://doi.org/10.1016/S0048-7333(01)00120-2
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310
Cohen, J. (1968). Weighted kappa: Nominal scale agreement provision for scaled disagreement or partial credit. Psychological Bulletin, 70(4), 213-220. https://doi.org/10.1037/h0026256
Costa, D., Querci, F., & Santulli, R. (2025). Competition or cooperation? Disentangling the Bank-FinTech interaction through a hybrid literature review. Research in International Business and Finance. https://doi.org/10.1016/j.ribaf.2025.102993
Cosma, S., & Pennetta, D. (2024). Enhancing online visibility through strategic alliances: the case of bank-FinTech relationships. International Journal of Bank Marketing. https://doi.org/10.1108/ijbm-02-2023-0071
<!-- rendered-citations:end -->
