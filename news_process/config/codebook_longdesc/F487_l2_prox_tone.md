---
family_id: F487
columns:
- prox_100km_tone_ctx
- prox_100km_tone_full
- prox_100km_tone_ss
- prox_150km_tone_ctx
- prox_150km_tone_full
- prox_150km_tone_ss
- prox_200km_tone_ctx
- prox_200km_tone_full
- prox_200km_tone_ss
- prox_50km_tone_ctx
- prox_50km_tone_full
- prox_50km_tone_ss
unit: LLM 投票语调分数 (llm_vote_score, 三分类映射为 {-1, 0, +1} 后的圈内文章均值, 连续值域 [-1,1]; bank-year 粒度, 无进一步跨年聚合)
formula: 'prox_{d}km_tone{track} = mean(llm_vote_score{track}[within_{d}km]), track ∈ {_full, _ctx, _ss}, d ∈ {50,100,150,200}; within_{d}km 定义为该 bank-year 全部可地理编码文章中 haversine 距离 dist_km ≤ d 的子集; n_geocoded=0 (该 bank-year 全部媒体无法地理编码) 时全空 NaN; n_geocoded>0 但圈内 (within) 该轨 llm_vote_score 全 NA 时按设计取 NaN (非缺失哨兵)'
producer: pipeline\panel\geography.py::compute_geo_proximity_buffers (buf_results[key][f'{prefix}_tone{_track}'] 赋值段, 约 L1379-L1402)
upstream: [21_tone_llms (llm_vote_score_full/_ctx/_ss 三家 LLM 多数投票共识分), 40_panel_export_main (地理编码 haversine 距离 _dist_km + 圈内子集 within)]
citations:
- {doi: "10.2308/TAR-2020-0104", type: journal, authors: "Holzman, E. R., Miller, B. P., & Twedt, B. J.", year: 2023, title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements", venue: "The Accounting Review", vol: "98", issue: "7", pages_or_artno: "315-345"}
- {doi: "10.1016/j.iref.2024.01.067", type: journal, authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.", year: 2024, title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China", venue: "International Review of Economics & Finance", vol: "91", pages_or_artno: "1150-1172"}
- {doi: "10.1016/j.eap.2024.08.019", type: journal, authors: "Guo, L., Zhu, H., Zhang, C., Liu, Y., & Yang, C.", year: 2024, title: "Does improved credit access promote pollution reduction? The role of bank proximity", venue: "Economic Analysis and Policy", vol: "84", pages_or_artno: "78-97"}
- {doi: "10.1002/ijfe.2791", type: journal, authors: "Ahmad, M., & Law, S. H.", year: 2024, title: "Financial development, institutions, and economic growth nexus: A spatial econometrics analysis using geographical and institutional proximities", venue: "International Journal of Finance & Economics", vol: "29", issue: "3", pages_or_artno: "2699-2721"}
- {doi: "10.1080/0034340052000320887", type: journal, authors: "Boschma, R.", year: 2005, title: "Proximity and innovation: A critical assessment", venue: "Regional Studies", vol: "39", issue: "1", pages_or_artno: "61-74"}
new_dois: []
---

## CORE

【构念与来源】
本家族 F487 (`prox_{d}km_tone_{full,ctx,ss}`, d∈{50,100,150,200} 公里) 度量的是"银行地理邻近圈内媒体报道的平均语调"——把 F483 (占比/正负比例) 与 F485/F486 (圈内文章数/媒体数) 度量的"有多少报道"这一强度维度, 换成"这些报道说了什么"这一方向维度。构念动机源于媒体地理学与银行挤兑传染文献的共识: 媒体离报道对象(银行分支机构、总部注册地)物理距离越近, 记者越可能获得一手信息源(本地分支员工、本地客户、本地监管接触), 报道的信息密度与准确度也倾向更高(Holzman, Miller & Twedt, 2023, *The Accounting Review*, 论证媒体情感对盈余公告有纪律约束作用, 隐含前提即媒体信息生产的地理嵌入性); 反之地理遥远的媒体转载/编译成本更低而核实成本更高, 语调更易受全国性叙事或同业传染带动而非本地基本面驱动。这一"接近性驱动信息质量"的直觉在中国语境下尤其相关: 银行分支网络高度依赖属地监管与属地信贷业务, 本地媒体的语调波动更贴近该银行分支所在地区的真实经营状况变化(如 Fang, Wang, Wang & Yuan, 2024, *International Review of Economics & Finance*, 就发现中国银行的媒体情感与存款稳定性、系统性风险直接相关, 且该效应在信息不对称更高的样本中更强)。F487 因此提供了一个"给定报道强度后, 报道基调是正是负"的补充测度, 与 F483 的强度/占比测度正交但互补——F483 回答"邻近圈内报道了多少条正面/负面新闻", F487 回答"邻近圈内所有报道综合起来平均是正是负"。

家族构念上属于地理邻近性(proximity)文献与文本情感测量文献的交叉产物。地理邻近性一支可追溯到区域经济学对"接近性—知识溢出"关系的系统性梳理(Boschma, 2005, *Regional Studies*, 提出接近性除地理维度外还有认知、组织、社会、制度四维, 本家族仅刻画其中地理维度, 其余维度未纳入构念, 属于刻意的范围限定而非遗漏); 空间计量在金融发展—制度—增长关系中的应用(Ahmad & Law, 2024, *International Journal of Finance & Economics*)进一步确认了"地理距离作为信息摩擦代理变量"在金融文本/制度分析中的合法性。这为把"媒体—银行地理距离"当作调节文本情感生产质量的外生结构变量提供了方法论支撑。

【方法学与计算】
公式层面, F487 的计算完全依托 F483/F485/F486 共享的地理定位与分箱基础设施(`pipeline/panel/geography.py::compute_geo_proximity_buffers`), 差异仅在最后一步取的聚合统计量不同: F483/F486 数点数(count/占比), F487 取均值(mean of tone)。具体步骤: ① 对该 bank-year 下每篇可关联到目标银行的报道, 用报道所属媒体(`媒体(中文)`列)的地理坐标与目标银行注册地/分支地坐标算 haversine 大圆距离 `_dist_km`; 无法解析媒体地理位置的文章 `_dist_km` 记 NaN 且不计入任何下游分母(`n_geocoded` = 该 bank-year 内 `_dist_km` 非空的文章数, 是本家族与 F483/F485/F486 共享的统一分母口径, 2026-06-10 metric-audit 修复过"分子圈内、分母误用未过滤全量"的口径不一致); ② 对四个半径阈值 d∈{50,100,150,200} 公里各自筛出 `within_{d}km = {_dist_km ≤ d}` 子集(阈值越大子集越宽, 存在 `prox_50km ⊆ prox_100km ⊆ prox_150km ⊆ prox_200km` 的拓扑单调性, 该单调性在源码里有专门断言守卫); ③ 在每个 within 子集上, 对三条文本轨道各自的 `llm_vote_score{track}` (stage 21 三家 LLM `gpt54nano`/`gemini31`/`deepseekv4` 多数投票共识分, 已由 encode 层映射为 {-1,0,+1} 三分类连续编码, 属于文章级测度而非本家族现算)取算术均值, 得到 `prox_{d}km_tone{track}`。

两处边界语义在 producer 源码中被明确刻意区分(而非同一"缺失"笼统处理), 写手须精确复述: 其一, `n_geocoded == 0`(该 bank-year 全部关联媒体都无法地理编码)时, 半径圈"内部有没有报道"这件事本身是未知而非确知为零, 因此该 bank-year 的全部 `prox_*` 系列列(含本家族 tone)统一填 NaN, 与 F483 的 `is_local`/`n_articles` 语义对齐(2026-06-11 omni-g-geography-02 修复曾把这种"未知"误记成"确知为0"的自相矛盾编码, 现已改正); 其二, 即便 `n_geocoded > 0` 且圈内确有文章(`n_within > 0`), 若圈内文章在该轨道上的 `llm_vote_score{track}` 全部为空值(该轨情感测量本身因故未产出, 如 ctx/ss 轨道罕见地无有效上下文窗口), 对应的 `prox_{d}km_tone{track}` 同样取 NaN——这是"分母存在但被测度对象本身缺席"造成的 NaN, 与前一种"分母整体未知"的 NaN 来源不同但表现相同, 下游使用时若要区分二者需联合读取 `prox_{d}km_n_articles`(F485)辅助判断。计算实现上还有一处 dtype 细节值得记录: 文章级 `llm_vote_score`/`is_positive`/`is_negative` 在 encode 层是 nullable `Int8`(NA 表示测量失败或投票平局), 若圈内该轨全部为 NA, pandas 的 `.mean()` 在 nullable 类型上返回 `pd.NA` 而非 `np.nan`, 混入结果字典后会把整列错误推断为 object dtype; 源码为此在聚合前显式 `.astype('float64')` 做类型归一, 确保无论圈内命中情况如何, 输出列恒为 float64 且缺失哨兵统一为 `np.nan`, 不会因这一实现细节污染下游 Stata 导出或统计推断。

三条轨道 full/ctx/ss 是本项目情感测量的标准三分法, 在 F487 语境下遵循与其余情感族完全一致的口径: full = 标题+全文正文, ctx = 标题+目标银行实体窗口, ss = 标题+银行∧金科同句±N窗(N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认1句); 三轨在 stage 21 情感 LLM 阶段各自独立产出 `llm_vote_score{track}`, F487 对每条轨道分别在圈内取均值, 得到三条并排、互不派生的地理邻近语调测度。ss 轨道遵循全项目统一的回退语义: 若某篇文章不存在银行∧金科同句共现, 其 `content_ss` 回退为全文 body 且 `ss_is_fallback=True`(镜像 ctx 轨道的回退设计, 分母共享 `n_articles`), 该回退发生在 stage 14 文本物化层, F487 本身不重复实现回退逻辑, 只是被动继承已回退文本上算出的 `llm_vote_score_ss`。三轨语调之间各自 just-identified 并排、互为稳健性、不分主次, 三者度量的是同一构念(邻近圈内平均语调)在不同文本窗口口径下的三次独立估计, 不应在同一 over-identified Hansen J 统计量中混用, 也不应把某一轨简单当作另一轨的"更精确版本"来替代——full 轨捕获文章通篇基调, ctx 轨聚焦银行实体窗口附近的措辞, ss 轨进一步收窄到银行与金科词汇同句出现处的措辞, 三者信息集不同, 差异本身就是稳健性检验的对象而非噪声。

【文献定位】
F487 与银行挤兑/存款稳定性研究中"媒体情感的地理异质性"文献直接对话: Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 发现中国银行的媒体情感显著预测存款稳定性与系统性风险, 且效应强度随信息环境异质而变——F487 用地理距离对这一"信息环境异质性"做出一个可操作化的连续分箱刻画, 提供了比全国平均语调更精细的空间粒度。Holzman, Miller & Twedt (2023, *The Accounting Review*) 关于媒体情感对盈余公告的纪律约束效应说明"语调"这一构念本身在公司/银行治理研究中有独立的解释力, 不能简单被"报道数量"或"报道占比"(F483)替代, 这正是本家族与 F483/F485/F486 分工的理论依据。Ahmad & Law (2024) 的空间计量应用与 Boschma (2005) 的接近性维度理论共同支撑了"地理距离阈值分箱"这一操作化选择的合理性——用离散半径圈(50/100/150/200公里)而非连续距离核, 是在计算成本与解释直观性之间的取舍, 四个阈值构成一个粗粒度的距离衰减梯子, 与文献中常见的距离衰减(distance decay)设定思路一致, 允许研究者观察语调—距离关系是否随半径扩大而单调稀释。Guo, Zhu, Zhang, Liu & Yang (2024, *Economic Analysis and Policy*) 关于银行邻近性与信贷可及性/污染治理的研究进一步佐证了"银行—地理对象距离"作为一个有实质经济含义的结构变量, 在中国金融地理学语境下已有先例, 而非本项目独创的度量口径。

## VAR: prox_50km_tone_full

【变体差分】
50 公里半径圈内(该项目四档半径梯子中最窄的一档, 约等同"同城/邻近区县"尺度)全部文章 full 轨(标题+正文全文)`llm_vote_score_full` 的均值。作为最窄半径, 该列样本量(`prox_50km_n_articles`, 见家族 F485)在多数 bank-year 上预期最小, 因而方差最大、对个别极端文章最敏感, 是"最本地化但最不稳健"的一端; 在距离衰减梯子四档中处于起点, 常被用作论文正文主设定(若研究假设强调本地信息优势)或稳健性梯子的一端锚点。full 轨意味着该均值综合了文章通篇(含背景铺垫、行业综述等与银行本身弱相关段落)的语调, 相比 ctx/ss 更"粗"但覆盖信息更全, 是三轨中最不容易漏掉边缘相关信息、但也最容易被无关段落稀释语调信号的一条。构念上, 50 公里圈 + full 轨的组合最贴近"本地记者写的完整报道读起来是正面还是负面"这一直觉问法, 适合作为距离衰减分析(观察语调系数随半径 50→200 公里如何变化)的内圈锚点, 与 200 公里外圈端点对照可以检验"地理邻近性—报道语调"关系是否随距离单调衰减; 若该列与 100/150/200 公里同轨语调高度相关, 说明本地信息优势在语调维度上的边际贡献有限, 是论文正文应披露的反面证据而非需要隐藏的null结果。使用时须留意: 该列继承 F483/F485/F486 共享的 `n_geocoded==0` 全空规则, 与圈内文章存在但该轨 `llm_vote_score_full` 全 NA 的情形共享同一 NaN 哨兵, 不可与"确知圈内无报道"混淆, 建议联合 `prox_50km_n_articles` 一并读取以判定 NaN 来源。

## VAR: prox_50km_tone_ctx

【变体差分】
50 公里半径圈内文章 ctx 轨(标题+目标银行实体窗口)`llm_vote_score_ctx` 的均值。与同半径 full 轨共享同一批圈内文章集合(`within_50km` 由地理距离而非文本轨道决定, 轨道差异只体现在情感测量本身用哪段文本), 差异仅在于情感打分所依据的文本窗口更聚焦于银行实体周边语境, 剔除了与该银行关联较弱的通篇背景内容, 理论上比 full 轨更贴近"媒体究竟怎么评价这家银行"而非"这篇报道整体氛围如何"。在最窄的 50 公里半径下, ctx 轨的这一"去噪"作用尤为重要: 本地报道往往夹杂大量与该银行无直接关系的区域经济背景描述(如地方 GDP、招商引资综述), full 轨的整篇均值容易被这类中性甚至无关内容拉向 0, 而 ctx 轨聚焦实体窗口后更能捕捉记者对该银行本身的真实评价倾向。该列与 `prox_50km_tone_full` 的差值本身就是一个有信息量的诊断量: 若二者系统性偏离, 说明本地报道中"通篇氛围"与"针对该银行的具体措辞"存在结构性分歧, 值得在稳健性附录中单独讨论。ctx 轨与 full 轨、ss 轨三者各自 just-identified 并排、互为稳健性, 不应在同一回归设定或同一 over-identified Hansen J 统计量中把三者同时当作对同一构念的多重工具变量混用。

## VAR: prox_50km_tone_ss

【变体差分】
50 公里半径圈内文章 ss 轨(标题+银行∧金科同句±1句窗)`llm_vote_score_ss` 的均值。ss 轨进一步收窄到银行实体与金科关键词同句共现处的措辞, 是三轨中文本窗口最窄、语调判定最贴近"银行—金科关系"具体措辞的一档; 若某篇文章无银行∧金科同句共现, 其底层 `content_ss` 已在 stage 14 回退为全文(`ss_is_fallback=True`, 与 ctx 轨回退语义镜像), 本列被动继承该回退结果, 不改变圈内文章数(F485 系列)本身。50 公里最窄半径叠加 ss 最窄文本窗口, 使该列在三轨×四阈值 12 列矩阵中处于"双重最窄"的角, 样本效应与测量噪声均预期最突出, 解读时须格外留意小样本 bank-year 的极端值——若某 bank-year 圈内仅一两篇文章满足银行∧金科同句共现条件, 该均值本质上退化为单篇文章打分, 不宜过度解读为"稳健的邻近语调估计"。对于以银行金融科技为研究主题的论文(P1 `bank_fintech_tone`), 该列相比 full/ctx 轨更直接地刻画了"本地媒体对该银行金融科技相关举措的具体措辞是正面还是负面", 是最贴近核心构念但样本效率最低的一档, 通常适合作为附录中的补充稳健性证据而非正文主设定。

## VAR: prox_100km_tone_full

【变体差分】
100 公里半径圈(距离衰减梯子第二档, 约等同"跨市但同省"尺度)内文章 full 轨 `llm_vote_score_full` 均值。相对 50 公里档, 圈内文章数(F485)通常增多, 语调均值的样本波动性相应下降, 是四档半径中承上启下的一档, 常作为"本地—非本地"分界的稳健性参照。100 公里已能覆盖多数省份内相邻地级市之间的媒体覆盖, 因而该列所刻画的"邻近性"开始从"同城信息优势"过渡到"省域信息网络", 在解释力上介于 50 公里档(强本地性)与 150/200 公里档(弱本地性)之间。研究者若观察到语调系数从 50→100 公里档小幅衰减但仍显著, 可将其解读为地理邻近性效应在省域尺度内依然存在但强度递减, 是距离衰减梯子上一个自然的检验点。计算口径与其余三档 full 轨完全一致, 唯一差分维度是圈内筛选阈值 `_dist_km ≤ 100`; 分母仍是该 bank-year 全部可地理编码文章数 `n_geocoded`(与半径无关的固定量), 分子随半径扩大而单调不减, 因此 `prox_100km_n_articles ≥ prox_50km_n_articles` 恒成立(拓扑单调性断言由源码显式守卫), 但对应的语调均值不必然单调, 因为新纳入的 50-100 公里环带文章语调可正可负。若某 bank-year 该环带内新增文章语调与 50 公里圈内已有文章语调方向相反, 会拉动 `prox_100km_tone_full` 偏离 `prox_50km_tone_full`, 这一偏离本身即是判断"报道语调是否随距离系统性变化"的直接经验证据, 而非测量误差。

## VAR: prox_100km_tone_ctx

【变体差分】
100 公里半径圈内文章 ctx 轨(标题+银行实体窗口)`llm_vote_score_ctx` 均值。同 50km_tone_ctx 的轨道语义, 差异仅在纳入圈内的地理半径放宽到 100 公里, 圈内文章集合随之扩大, 语调估计的样本基础更宽但地理"本地性"假设相应弱化。由于圈内文章数增多, 该列相比 50km_tone_ctx 更不易受单篇极端文章左右, 适合在需要兼顾样本量与本地性两端权衡时作为折中设定; 与同半径 full 轨的差值同样可用于诊断"通篇氛围 vs 实体窗口措辞"是否存在系统性分歧, 逻辑与 50 公里档一致但样本更稳。ctx 轨在实体窗口内测量语调, 理论上比 full 轨更少受报道中大段行业背景、宏观政策综述等与目标银行本身无直接关联段落的稀释, 100 公里档下这一去噪优势与更大的样本量叠加, 使该列成为 ctx 轨稳健性梯子中信噪比相对较优的一档; 与 `prox_100km_tone_full`、`prox_100km_tone_ss` 三者应各自单独进入回归设定并排比较, 不应加权合并或互为工具变量, 三者共同构成同一半径下"文本窗口口径梯子"的并排稳健性证据。100 公里档 ctx 轨相较 50 公里档在样本量与本地性纯度之间取得了一个更均衡的位置, 是研究者若只能报告一档 ctx 轨稳健性证据时的常见折中选择。

## VAR: prox_100km_tone_ss

【变体差分】
100 公里半径圈内文章 ss 轨(标题+银行∧金科同句±1句窗)`llm_vote_score_ss` 均值。同 50km_tone_ss 的窄文本窗口语义与回退语义(`ss_is_fallback` 镜像 ctx), 半径放宽到 100 公里后圈内符合银行∧金科同句共现条件的文章数(该条件本身与半径无关, 只是分母集合随半径扩大而扩大)通常增多, 相比 50km 档更不易因个别极端文章失真。该列在"银行—金科同句共现"这一严格判据下天然样本偏小, 100 公里档相比 50 公里档提供的样本量缓解虽有限但仍是正向的, 论文中若同时报告 50km 与 100km 两档 ss 轨系数方向一致, 可作为该 ss 轨测度不受半径选择驱动的一个佐证。需注意 ss 轨的窄判据(银行实体与金科关键词须在同一句±1句窗内共现)独立于地理半径起作用, 即便 100 公里圈内文章总数(对照 full 轨的 `prox_100km_n_articles`)相当可观, 满足 ss 判据的子集仍可能只有个位数, 此时该列的 `llm_vote_score_ss` 均值本质上由极少数文章主导, 是三轨×四阈值矩阵中最需要联合 F485/F486 系列文章数与媒体数辅助判断估计可靠性的一档之一。研究者在使用该列做正式推断前, 建议先核查对应的 `prox_100km_n_articles`(F485)量级, 若圈内满足 ss 判据的文章数长期个位数, 该列更适合仅作定性佐证而非纳入正式回归系数解读。

## VAR: prox_150km_tone_full

【变体差分】
150 公里半径圈(距离衰减梯子第三档)内文章 full 轨 `llm_vote_score_full` 均值。该档进一步放宽地理邻近假设, 覆盖范围可能已跨省辐射至相邻省份地级市, "本地信息优势"的理论解释力相对 50/100 公里档减弱, 更多起到距离衰减趋势线上承接第二档与第四档的中继作用。在四档半径的距离衰减曲线绘制中, 150 公里档是判断衰减模式(线性衰减 vs 在某一阈值后骤然平坦)的关键中间点: 若语调系数从 100→150 公里已趋于平坦并与 200 公里档接近, 提示邻近性效应的"有效半径"大致在 100-150 公里量级, 是论文正文可以直接引用的经验发现。该列与其余三档 full 轨共享完全相同的分母口径(该 bank-year 全部可地理编码文章数 `n_geocoded`)与相同的圈内子集单调嵌套关系(`within_100km ⊆ within_150km ⊆ within_200km`), 唯一变化维度是筛选阈值本身, 便于研究者在同一张图上呈现语调系数随半径连续变化的形状, 而不必担心不同半径档之间因分母口径不一致产生的可比性问题。150 公里档 full 轨在四档半径中处于"中偏宽"的位置, 若论文正文以 100 公里档作主设定, 该列常被用作紧邻的上侧稳健性检验, 用以说明结果不因半径的微小调整而发生方向性反转。

## VAR: prox_150km_tone_ctx

【变体差分】
150 公里半径圈内文章 ctx 轨 `llm_vote_score_ctx` 均值。轨道语义同前述各 ctx 列(标题+银行实体窗口测量口径不变), 唯一差分维度是地理半径放宽到 150 公里, 圈内文章集合相应扩大。作为 ctx 轨稳健性梯子的第三档, 该列与 50/100 公里档共同构成一条完整的衰减序列, 便于在同一张系数图中呈现 ctx 轨语调—距离关系的整体形状, 而不依赖单一半径设定的选择性结果; 与该半径下的 full 轨、ss 轨并排比较可同时观察"半径扩大"与"文本窗口收窄/放宽"两个独立维度对语调估计的影响, 二者互不纠缠——半径变化只改变纳入哪些文章, 文本窗口变化只改变对同一文章打分时依据哪段文字, 两个维度的差分在本家族与相邻家族(F483/F485/F486)中被刻意保持正交, 不应在同一回归设定中把二者混为一谈或相互替代。150 公里档 ctx 轨的圈内文章集合已显著宽于 50 公里档, 但仍严格窄于 200 公里档, 在距离衰减图上位于曲线中段, 是判断 ctx 轨语调—距离关系是否呈现平滑衰减还是存在拐点的重要观测点。若研究者绘制 ctx 轨四档语调系数随半径变化的曲线, 该列作为中间点承担着判断曲线形状(近似线性 vs 存在明显拐点)的枢纽作用, 缺失该档会使 50→200 公里的跳跃解读失去中间过渡证据。

## VAR: prox_150km_tone_ss

【变体差分】
150 公里半径圈内文章 ss 轨 `llm_vote_score_ss` 均值。轨道语义同前述各 ss 列(标题+银行∧金科同句窗测量口径、回退语义均不变), 半径放宽到 150 公里后圈内符合同句共现条件的文章分母随之扩大, 是三轨×四阈值矩阵中样本基础较宽的一档。相比 50/100 公里档, 该列的小样本问题有所缓解, 更适合作为 ss 轨稳健性检验中样本量与本地性权衡较优的一个设定, 但仍不及 full/ctx 轨在同半径下的样本量, 解读时仍需结合 F485 系列的圈内文章数辅助判断估计精度。150 公里档 ss 轨与 50/100 公里档 ss 轨共同构成 ss 轨内部完整的四档序列(与 200 公里档合计四档), 四者相互印证方向一致时可显著加强"银行—金科关系措辞语调受地理邻近性调节"这一论断的可信度, 是 ss 轨稳健性附录中不可或缺的一环, 单独一档不足以支撑该论断, 论文披露应以四档并列图表形式呈现而非选择性挑选。该列在样本量与地理邻近性纯度之间处于 ss 轨四档序列的中段位置, 既非样本最稀疏的 50 公里档、也非邻近性构念效度最弱的 200 公里档, 常被选作 ss 轨附录表格中除主设定外的首选补充证据。

## VAR: prox_200km_tone_full

【变体差分】
200 公里半径圈(该项目距离衰减梯子最宽的一档, 约等同"跨省辐射"尺度)内文章 full 轨 `llm_vote_score_full` 均值。作为四档中最宽的半径, 该列圈内文章数(F485)预期最大, 语调估计样本基础最稳, 但"地理邻近—信息优势"的构念解释力也最弱, 更接近于一个宽松的区域性语调而非严格意义上的本地语调; 在距离衰减分析中常作为"外圈基准"与 50 公里"内圈"对比, 若二者语调系数相近甚至不显著弱化, 提示地理邻近性对语调本身的调节作用有限。该列也因样本量最大而最不受个别极端文章驱动, 若研究者担心小半径档因样本稀疏产生的测量噪声主导结果, 可将 200 公里档 full 轨作为一个"信噪比最优但邻近性假设最弱"的稳健性参照, 与 50 公里档"邻近性假设最强但噪声最大"的组合形成完整的偏差—方差权衡叙事。研究者在稳健性附录中通常会把 `prox_50km_tone_full` 与 `prox_200km_tone_full` 并列呈现作为距离衰减梯子的两端锚点, 若二者系数符号相同、量级接近, 则说明地理邻近性对报道语调的调节作用较弱, 该发现本身对论文的贡献不亚于一个显著的正向发现, 不应因不显著而被舍弃不报告。

## VAR: prox_200km_tone_ctx

【变体差分】
200 公里半径圈内文章 ctx 轨 `llm_vote_score_ctx` 均值。轨道语义同前述各 ctx 列, 半径为四档中最宽, 圈内文章集合最大, 是 ctx 轨稳健性梯子的外圈端点。与 `prox_50km_tone_ctx` 构成 ctx 轨内部完整的距离衰减对照组, 二者系数差异(若存在)可归因于地理邻近性本身而非文本窗口口径变化, 因为轨道选择在四档半径间保持恒定, 唯一变化的是圈内文章的地理筛选范围。200 公里档 ctx 轨在四档中样本基础最宽, 是 ctx 轨稳健性梯子中最不受个别文章驱动、但地理"邻近性"构念效度最弱的一档, 常与 50 公里档 ctx 轨并列呈现作为该轨内部完整距离衰减曲线的两端参照, 供审稿人一眼判断结果是否敏感于半径阈值的具体取值。与该半径下的 full 轨、ss 轨并排理解: 三者共享同一圈内文章地理筛选集合, 仅在情感打分依据的文本窗口上不同, 三轨系数若方向一致而量级有别, 说明地理邻近性效应在不同文本粒度上表现稳定, 是较强的稳健性证据; 若三轨方向出现分歧, 则提示该效应可能集中于特定文本窗口(如仅在实体窗口措辞中显著而通篇氛围中不显著), 本身也是值得在论文中讨论的细粒度发现, 而非需要回避的矛盾结果。

## VAR: prox_200km_tone_ss

【变体差分】
200 公里半径圈内文章 ss 轨 `llm_vote_score_ss` 均值。轨道语义同前述各 ss 列(含 `ss_is_fallback` 回退镜像 ctx 的设计), 半径为四档中最宽, 是本家族 12 列矩阵中 ss 轨稳健性梯子的外圈端点, 与 `prox_50km_tone_ss`(内圈端点)构成 ss 轨内部的距离衰减对照组。200 公里档下 ss 轨的样本量相对其余三档 ss 列最大, 缓解了 ss 轨本身因"银行∧金科同句共现"判据严格而普遍存在的小样本问题, 但对应的地理邻近性构念效度也最弱; 若论文核心假设依赖 ss 轨捕获的"银行—金科具体措辞语调", 该列可作为在牺牲部分邻近性纯度换取估计精度后的补充证据, 不应替代 50/100 公里档作为主设定。200 公里档 ss 轨与 150 公里档 ss 轨、100 公里档 ss 轨、50 公里档 ss 轨四者合计构成本家族 ss 轨内部完整的四档距离衰减梯子, 四者各自 just-identified 并排, 互为稳健性、不分主次, 论文披露时应统一以图表形式呈现四档系数及置信区间, 而非仅挑选其中支持假设的一档单独报告, 后者构成选择性报告风险, 与本项目其余梯子式测度(词典规则消融、政治词权重、罕见词频次 cutoff)一致遵循全梯子披露原则。作为 ss 轨样本量最大的一档, 该列在四档中信噪比相对最优, 常与 50 公里档 ss 轨(样本最小但邻近性假设最强)成对呈现, 用以说明 ss 轨内部的偏差—方差权衡边界。

<!-- rendered-citations:begin -->
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Guo, L., Zhu, H., Zhang, C., Liu, Y., & Yang, C. (2024). Does improved credit access promote pollution reduction? The role of bank proximity. Economic Analysis and Policy, 84, 78-97. https://doi.org/10.1016/j.eap.2024.08.019
Ahmad, M., & Law, S. H. (2024). Financial development, institutions, and economic growth nexus: A spatial econometrics analysis using geographical and institutional proximities. International Journal of Finance & Economics, 29(3), 2699-2721. https://doi.org/10.1002/ijfe.2791
Boschma, R. (2005). Proximity and innovation: A critical assessment. Regional Studies, 39(1), 61-74. https://doi.org/10.1080/0034340052000320887
<!-- rendered-citations:end -->
