---
family_id: F655
columns:
- zone_leave1out_tone_ctx
- zone_leave1out_tone_full
- zone_leave1out_tone_ss
unit: 语调得分 (连续, 约 [-1,1]; 以 llm_vote_score_{track} 为原子值的经济圈内他行均值, 聚合层级为 bank-year)
formula: 'zone_leave1out_tone_{track}(bank i, year t) = mean_{j∈zone(i), j≠i} llm_vote_score_{track}(j, t), track ∈ {full, ctx, ss}; 排除 bank_zone == "other" (省份未映射经济圈) 的银行不参与聚合, 分组样本量 < min_group_size(默认 3) 时按下游口径优雅置 NaN'
producer: pipeline\panel\iv_did.py::compute_zone_leave1out ; pipeline\panel\export.py (标签挂载)
upstream:
- 21_tone_llms.parquet::llm_vote_score_full
- 21_tone_llms.parquet::llm_vote_score_ctx
- 21_tone_llms.parquet::llm_vote_score_ss
- 40_panel_yearly.parquet::bank_province
- 40_panel_yearly.parquet::target_bank
citations:
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and Domain Specificity: A Chinese Financial Sentiment Dictionary"
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: Measuring News Sentiment
  venue: Journal of Econometrics
  vol: '228'
  issue: '2'
  pages_or_artno: 221-243
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: Media sentiment, deposit stability and bank systemic risk - Evidence from China
  venue: International Review of Economics & Finance
  vol: '91'
  issue: ''
  pages_or_artno: 1150-1172
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: 'Firm-Level Political Risk: Measurement and Effects'
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: "10.2139/ssrn.4787799"
  type: "wp"
  authors: "Ellis, C., & Jaspersen, J. G."
  year: 2024
  title: "Fixed Effects and the \"Leave-Out'' Instrument"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "4787799"
- doi: "10.1162/rest.a.263"
  type: "journal"
  authors: "Frandsen, B., Leslie, E., & McIntyre, S."
  year: 2025
  title: "Cluster Jackknife Instrumental Variables Estimation"
  venue: "Review of Economics and Statistics"
  pages_or_artno: "1-19"
- doi: "10.1257/aeri.20240184"
  type: "journal"
  authors: "Bobrov, A., Kamdar, R., & Ulate, M."
  year: 2025
  title: "Regional Dissent: Do Local Economic Conditions Influence FOMC Votes?"
  venue: "American Economic Review: Insights"
  vol: "7"
  issue: "2"
  pages_or_artno: "268-284"
- doi: "10.3390/econometrics14010005"
  type: "journal"
  authors: "Lee, D. K. C., Xu, W., Shi, J., Wang, Y., & Ding, D."
  year: 2026
  title: "Shock Next Door: Geographic Spillovers in FinTech Lending After Natural Disasters"
  venue: "Econometrics"
  vol: "14"
  issue: "1"
  pages_or_artno: "5"
new_dois: []
---

## CORE

【构念与来源】
zone_leave1out_tone 家族衡量"同一经济圈内其他银行在当年的媒体语调均值", 是为经济圈-年份共同冲击构造的 leave-one-out (LOO) 工具变量族, 产自 `pipeline\panel\iv_did.py::compute_zone_leave1out`, 由 `pipeline\panel\export.py` 挂载标签进入 40 号年度面板。其设计动机直接对标省级 leave-one-out IV: 省级 LOO 以省为分组单位构造同侪均值, 但单省内银行样本量往往过少 (中国多数省份仅有个位数上市/规模化银行分支覆盖), 均值易受个别银行噪声主导, 弱工具风险抬头。经济圈 LOO 用一张跨省经济区域映射表 (`PROVINCE_TO_ZONE`, 硬编码在生产代码中, 覆盖京津冀/长三角/珠三角/成渝/东北/中部/西北/西南/东南/环渤海十个经济圈标签) 把银行总部所在省份折叠进更大的地理-经济单元, 换取更充足的同组样本、以捕捉区域层面共同冲击 (地方金融监管取向、区域宏观景气、跨省媒体网络的地理粘性等) 对语调的系统性拉动, 同时仍然满足工具变量所需的相关性 (同经济圈银行确实共享部分媒体环境与宏观驱动) 与外生性诉求 (个体银行 i 自身的报道被排除出其自身的工具值构造, 避免机械共线)。

leave-one-out 结构是本族的核心识别设计: 对银行 i 在年份 t 的工具值, 只使用"同经济圈、非 i 自身"的其他银行当年语调的均值, 明确排除银行 i 本行的文章参与自身工具构造。这一排除是必要条件, 否则工具值会与银行 i 自身的解释变量 (通常是同期或滞后的语调测度) 机械相关, 破坏工具变量的排他性假设, 使二阶段最小二乘估计退化为伪装成 IV 回归的 OLS。生产代码中还有一处对"伪经济圈"的显式净化: `bank_province` 若未命中 `PROVINCE_TO_ZONE` 映射表 (即省份拼写/口径不在硬编码字典中), 会被 `fillna('other')` 兜底标记为 `'other'`, 而 `'other'` 标签下的文章在聚合前被显式过滤剔除 (`df_z[df_z['_zone'] != 'other']`)。这是因为 `'other'` 并非一个真实存在的地理-经济共同体, 银行之间不共享任何可辨识的区域冲击渠道, 若放任其参与聚合, 会人为拼凑出一个不具经济含义的"虚拟组", 虚报样本覆盖并污染工具的相关性结构; 该处理口径与同一模块内 `compute_bartik_iv` 排除 `'other'` 分组的做法完全对称, 两者共享同一条"伪分组不进入区域层面工具变量"的设计原则。

家族的三个成员列 (`zone_leave1out_tone_full`/`_ctx`/`_ss`) 对应三条彼此独立的文本处理轨道, 消费的原子情感分值来自上游 stage 21 三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票后的 `llm_vote_score_{track}` 列, 而非任一单模型分值, 因此本族工具变量继承了投票共识层面的稳健性, 不受单一厂商模型漂移或偏置的直接支配。三轨文本本身的差分语义 (轨道构造/回退规则) 详见下方 ## VAR: 分节; 三轨之间不构成任何主从关系, 各自在自身文本口径下完成独立的经济圈内 leave-one-out 聚合, 互不借用彼此的分母或分子。

【方法学与计算】
计算分两步。第一步是打标签: 面板层 (bank-year) 依据 `bank_province` 经映射表得到 `bank_zone`; 文章层 (`df_exploded`, 情感与文本处理后被展开到"文章×目标银行"粒度的中间表) 依据 `target_bank` 反查同一张银行-经济圈映射得到每篇文章所属的 `_zone`, 这一步确保文章层与面板层使用完全一致的经济圈口径, 不存在两套地理标签并存的风险。第二步是分组聚合与 leave-one-out 剔除: 对每条 (银行 i, 年份 t) 记录, 在同经济圈同年份的文章子集中, 排除目标银行为 i 自身的文章, 取剩余文章对应的 `llm_vote_score_{track}` 均值作为 `zone_leave1out_tone_{track}(i, t)`; 若该分组样本量小于 `min_group_size` (生产口径默认 3), 或该银行的 `bank_zone` 本身为 `'other'`, 输出置为 NaN, 遵循"宁缺勿凑"的稳健口径, 不用小样本均值冒充可信工具。

三轨中 `_ss` 轨依赖上游 `llm_vote_score_ss` 列; 若该列在特定运行环境下缺失 (例如银行与金科词未曾同句共现导致的结构性稀疏, 或某次流水线运行未启用 ss 轨情感计算), 生产代码会对该轨整体优雅置 NaN, 不中断 `_full`/`_ctx` 两轨的产出, 这一"单轨独立降级、不连坐其余轨"的设计与项目内多处 per-track/per-model 独立降级的口径一致。三轨在经济圈 LOO 聚合前均已各自完成了自身的留篇门控与轨道内成分覆盖判定, 本族只对已产出的原子分值做二次的地理分组均值运算, 不重新触发任何情感判定。

本族属于 IV 扩展体系 (`iv_did.py`, 面板构建 runner 步骤序列的组成部分) 中的经济圈层级工具, 与同模块内的省级 LOO、广义 Bartik 工具、媒体来源 house-style 暴露工具彼此并列, 均服务于同一枚举需求: 为银行-年份语调测度提供多种彼此独立、构造逻辑各异但共同满足"排他性靠地理/结构性共同冲击而非个体银行行为"这一逻辑的候选工具, 供下游 2SLS 模板按识别策略选用或做过度识别检验意义上的横向比较, 而非彼此嵌套叠加进同一条工具方程。

家族名称中的"leave1out"精确指代"留出自身 (leave i out)"这一聚合规则, 而非任何交叉验证或折外样本的统计学习含义; "zone"精确指代经济圈这一介于省级与全国之间的中观地理单元, 与"省级 LOO"工具在粒度上互补而非替代关系: 前者样本更充足但地理粒度更粗, 后者粒度更细但小样本弱工具风险更高, 两者是同一识别问题在不同粒度权衡下的并列解, 供研究者按第一阶段 F 统计量与相关性诊断实证取舍, 亦可同时纳入过度识别检验以交叉验证结论稳健性。

【文献定位】
本族的语调原子值 `llm_vote_score_{track}` 采用大语言模型多数投票范式提取文本情感极性, 方法学谱系上承接文本情感分析从词典法向机器学习/深度学习方法演进的主线; Du, Huang, Wermers & Wu (2022, *Review of Finance*) 构建的中文金融情感词典 (本项目词典轨的直接方法学锚点之一) 系统论证了通用情感词典移植到金融语境、尤其是中文金融语境时的领域特异性失配问题, 为本项目采用 LLM 投票而非纯词典法作为语调测度主轨提供了方法学正当性背景。Shapiro, Sudhof & Wilson (2022, *Journal of Econometrics*) 在新闻情感测度的构造与验证上提供了范式参照, 强调情感测度须在下游预测任务中展现出增量信息含量而非仅在情感标注一致性上自证, 这一思路呼应本族工具变量最终须服务于第一阶段相关性与结构方程外生性的实证检验逻辑。

将同侪 (同经济圈) 语调均值构造为 leave-one-out 工具变量, 方法学脉络上与 Hassan, Hollander, van Lent & Tahoun (2019, *Quarterly Journal of Economics*) 政治风险测度中对同行业/同地区共同冲击的分离思路一脉相承: 该文强调企业层面文本测度中混杂着行业或地区共同成分与企业特质成分, 需要显式的分组结构设计才能将共同冲击从个体信号中分离出来, 为可信的因果识别服务; 本族的经济圈分组正是把这一思路应用到银行地理布局上的具体实现。在中国银行业的具体设定中, Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 直接验证了媒体情感对中国银行系统性风险与存款稳定性的因果关联, 是本族"银行层面媒体语调具有可识别经济后果"这一前提假设的同域实证支持, 也是本族工具变量最终服务的结构方程 (语调对银行经营结果的因果效应) 在中国场景下的直接文献先例。 leave-one-out 算子本身的方法学性质近年亦有直接文献。Ellis 与 Jaspersen (2024) 分析留一同侪均值工具在含固定效应模型中的行为, 指出组内留一均值与固定效应同时进入时估计量会出现机械性偏误, 是本族构造法最贴近的方法学警示; 须注意该文为 SSRN 工作论文而非同行评审终稿, 其推导对象是一般线性面板的留一 IV 估计量性质与模拟, 不涉及媒体或银行数据, 亦未触及本族的 bank-year 层级、中文语调原子值与 min_group_size 守卫, 且本族的 leave1out 列部分仅作同侪暴露控制变量而非 IV, 故按方法学提醒而非现成修正方案引用。Frandsen、Leslie 与 McIntyre (2025) 则从正面提出 cluster jackknife (按簇留出) IV 估计量, 证明其在簇内多工具/多固定效应设定下可消除标准 2SLS 的偏误, 与本族按 (经济圈, 年) 分组留出的思路同族; 该文是纯计量方法论文, 由估计量推导、蒙特卡洛与一个美国司法数据应用构成, 其留出单位是簇 (法官) 而本族留出单位是同经济圈内的单个银行且分组键为地理×年份, 本族仅借其对留一构造的偏误校正逻辑作方法参照, 并未实施 cluster jackknife 估计。

分组前提与同域溢出证据方面, Bobrov、Kamdar 与 Ulate (2025) 检验区域经济状况是否影响按辖区指派的美联储 FOMC 地区联储主席的货币政策投票, 证明「主体所属地理区域的状况会系统性影响其可观测行为」, 为本族按省份/经济圈分组承载真实共同冲击这一前提提供顶刊层面的近期证据; 其主体行为与中国银行的媒体报道语调无任何直接对应, 地理分组是既定的联储辖区而本族需自建经济圈映射, 且该文不做留一均值构造、也未把同组他成员的行为作为解释变量, 故仅锚定「地理分组有实质经济含义」这一前提, 不锚定 leave-one-out 算子本身。Lee、Xu、Shi、Wang 与 Ding (2026) 以印尼最大金融科技放贷平台的贷款级数据 (2021-2023), 用空间滞后灾害暴露 (SLX 型) 估计灾害对相邻未受损省份借贷行为的溢出, 并发现溢出随地理连通性 (陆连 vs 海隔) 大幅变化, 与本族「以空间邻近单元的聚合暴露刻画同侪溢出」逻辑同族; 但该文发表于 MDPI Econometrics, 非本项目优先的顶刊层级, 影响力有限, 仅作金融科技语境下的前沿存在性引用, 其空间邻近以行政邻接界定而非公里缓冲, 溢出对象是金融科技信贷量而非媒体报道语调, 依赖灾害外生冲击设计 (本族无), 亦不涉及本族的经济圈映射规则与 min_group_size 守卫。
## VAR: zone_leave1out_tone_ctx

【变体差分】
`_ctx` 轨的原子情感分值取自上游 `llm_vote_score_ctx`, 消费的底层文本是 stage 14 物化的 `content_ctx` (标题 + 实体窗口, `prepend_title` 拼接), 而非全文正文。该轨与 `_full`/`_ss` 两轨严格并排, 各自在自身文本口径下独立完成经济圈内 leave-one-out 聚合: 三轨各自 just-identified, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验方程。ctx 轨的构造原理是把 LLM 的注意力窗口收窄到围绕目标实体 (银行/金科词) 的局部语境, 相对全文轨滤除了与银行-金科关系无直接关联的段落噪声, 因此其原子分值理论上对报道中"实体相关论调"更敏感, 但同时也放弃了全文轨可能捕捉到的篇章级整体基调信息, 两者互补而非互相替代。

留篇门控口径 (2026-06-29 起) 为 full-only: 一篇文章是否计为"一篇银行金科报道"只由 `llm_verified_full == True` 决定, ctx 轨的行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 但 per-track 的分值仍照各轨自身规则计算, 不借用 full 轨的分值填补 ctx 轨。zone LOO 聚合对 ctx 轨的处理方式与 full/ss 完全对称: 排除银行 i 自身文章, 同经济圈同年份取均值, 样本量不足或经济圈为 `'other'` 时置 NaN, 不存在 ctx 专属的额外聚合规则分支。

在实体窗口收窄这一构造原理下, ctx 轨的经济圈同侪均值刻画的是"同经济圈其他银行在实体相关语境窗口内的语调共识", 更贴近对银行-金科关系本身的定向评价, 相对全文轨可以部分过滤掉与银行经营无关的时政、行业综述性段落对语调的稀释效应。当某银行所属经济圈内多数同侪文章的实体窗口聚焦度不足 (窗口过窄导致可用词汇量骤减) 时, ctx 轨原子分值的方差结构可能与 full 轨产生系统性差异, 这正是三轨并列设计意在捕捉并允许研究者做稳健性比较的差异来源之一, 而非测量误差。

## VAR: zone_leave1out_tone_full

【变体差分】
`_full` 轨是本家族的规范 (canonical) 轨道, 原子分值取自 `llm_vote_score_full`, 消费的底层文本是 stage 14 物化的 `content_full` (标题 + 全文正文 `prepend_title` 拼接), 覆盖信息量最完整。full 轨同时也是留篇门控的唯一判据来源: 一篇文章是否被认定为有效的"银行-金科报道"仅取决于该文章在 full 轨下的 LLM 验证结果 (`llm_verified_full`), ctx 与 ss 两轨的行宇宙均是 full 轨留篇集合的严格子集, 这一点须在 full 轨与两条稳健轨之间的关系表述中被反复强调, 以避免误读为三轨各自独立门控。

尽管 full 轨承担留篇门控角色, 在 zone leave-one-out 聚合这一具体计算步骤上, full 轨与 ctx/ss 两轨地位对等, 各自使用自身轨道产出的 `llm_vote_score_{track}` 做独立的经济圈内均值聚合, 不存在"以 full 轨结果去修正或加权 ctx/ss 轨"的机制。三轨的并列关系应理解为"构念测量的三种互补口径, 各自 just-identified, 互为稳健性、不分主次", 而非层级从属关系; 下游研究者选用哪一轨作为主回归工具、哪些作为稳健性检验, 是识别策略层面的选择, 不由本族 producer 预先设定。

full 轨覆盖信息量最完整, 其经济圈同侪均值也因此最贴近"该经济圈整体媒体环境"这一宽泛构念, 适合作为经济圈共同冲击工具变量的默认首选; 但正因覆盖面宽, full 轨原子分值也更容易掺入与银行-金科主题弱相关的段落内容, 这是其相对 ctx/ss 两条更聚焦轨道的固有权衡, 也是本族提供三条并列轨道、而非仅提供单一 full 轨的根本理由。研究者在实证中若发现 full 轨工具的第一阶段 F 统计量偏弱, 可优先转向 ctx 或 ss 轨做交叉验证, 三者互不隶属。

## VAR: zone_leave1out_tone_ss

【变体差分】
`_ss` 轨的原子情感分值取自 `llm_vote_score_ss`, 消费的底层文本是 stage 14 物化的 `content_ss` (标题 + 银行∧金科同句共现窗口, `sentence_radius` 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句), 是三轨中语境窗口最窄、判定要求最严格的一支, 精确刻画"银行与金科话题在同一句话中被共同提及"时的语调。ss 轨的回退语义严格镜像 ctx 轨: 当一篇文章不存在银行∧金科同句共现时, `content_ss` 回退为全文 body (与 `content_full` 同源), 并置 `ss_is_fallback = True`, 分母 `n_articles` 与 ctx 轨共享同一套回退口径, 不因回退而虚增或虚减有效样本计数; 当上游 `FINTECH_AC` (金科词 Aho-Corasick 匹配器) 为 None 时, `*_is_fallback` 全体置 True, 实现优雅降级而非硬性报错。

本族 zone LOO 聚合层面, `_ss` 轨在上游 `llm_vote_score_ss` 列整体缺失的边界情形下 (例如某次流水线运行未产出 ss 轨情感, 或该轨在特定语料切片下结构性稀疏到无法产出有效分值), 由 `compute_zone_leave1out` 显式优雅降级为整轨置 NaN, 不影响 `_full`/`_ctx` 两轨的正常产出, 三轨各自独立降级、互不连坐。与 ctx 轨相同, ss 轨的留篇行宇宙仍以 full 轨的 `llm_verified_full` 门控为准 (conditional-on-full), ss 轨自身的"同句共现与否"只影响文本内容与分值本身, 不改变该文章是否进入留篇集合的判定权。三轨 (full/ctx/ss) 之间禁止混入同一 over-identified Hansen J 检验方程, 各自 just-identified 并排使用, 互为稳健性、不分主次。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring News Sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk - Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Ellis, C., & Jaspersen, J. G. (2024). Fixed Effects and the "Leave-Out'' Instrument. SSRN Electronic Journal No. 4787799 [Working Paper]. https://doi.org/10.2139/ssrn.4787799
Frandsen, B., Leslie, E., & McIntyre, S. (2025). Cluster Jackknife Instrumental Variables Estimation. Review of Economics and Statistics, 1-19. https://doi.org/10.1162/rest.a.263
Bobrov, A., Kamdar, R., & Ulate, M. (2025). Regional Dissent: Do Local Economic Conditions Influence FOMC Votes? American Economic Review: Insights, 7(2), 268-284. https://doi.org/10.1257/aeri.20240184
Lee, D. K. C., Xu, W., Shi, J., Wang, Y., & Ding, D. (2026). Shock Next Door: Geographic Spillovers in FinTech Lending After Natural Disasters. Econometrics, 14(1), 5. https://doi.org/10.3390/econometrics14010005
<!-- rendered-citations:end -->
