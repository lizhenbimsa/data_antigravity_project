---
family_id: F556
columns:
- token_adopt_int_p75_allv
- token_adopt_int_p75_allv_ctx
- token_adopt_int_p75_allv_ss
unit: 二值示性比例 (银行-年内 "Token 采纳" 象限文章占比, 取值 [0,1], 无量纲)
formula: 'mean_over_articles( 1{ fintech_intensity_score_<trk> >= P75_year(fintech_intensity_score_<trk>) AND policy_cosine_sim_allv_<trk> < P75_year(policy_cosine_sim_allv_<trk>) } ), <trk> ∈ {full(无后缀), ctx, ss}; P75 阈值按发文年度分组 (`groupby(year).transform(quantile)`) 逐年、逐轨分别计算 (非全样本固定切点), 双测量 (sim/freq) 有一项缺测该篇即被排除分母外 (NaN, 非计零)'
producer: pipeline\panel\runner.py (象限分类主循环, `_classify_policy_quadrants` 附近; `_anchor_variants`/`_sim_tracks`/`_tracks` 三层循环) ; pipeline\panel\export.py (Stata 变量标签映射, L1404-L1413 一带)
upstream:
- 15_fintech_intensity (fintech_intensity_score 三轨列, 词频侧 Track B "int")
- article_policy_alignment (policy_cosine_sim_allv 全语料静态锚点列, 三轨)
- 21_tone_llms (llm_verified_full 留篇门控, 决定进入 n_articles 分母的文章集合)
citations:
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: Journal of Business Economics
  vol: '87'
  issue: '5'
  pages_or_artno: 537–580
- doi: 10.1002/smj.821
  type: journal
  authors: Adner, R., & Kapoor, R.
  year: 2010
  title: "Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations"
  venue: Strategic Management Journal
  vol: '31'
  issue: '3'
  pages_or_artno: 306–333
- doi: 10.1006/jfin.2000.0282
  type: journal
  authors: Boot, A. W. A.
  year: 2000
  title: "Relationship banking: What do we know?"
  venue: Journal of Financial Intermediation
  vol: '9'
  issue: '1'
  pages_or_artno: 7–25
- doi: 10.1016/j.econmod.2023.106445
  type: journal
  authors: Fang, Y., Wang, Q., Wang, F., & Zhao, Y.
  year: 2023
  title: "Bank fintech, liquidity creation, and risk-taking: Evidence from China"
  venue: Economic Modelling
  vol: '127'
  pages_or_artno: '106445'
- doi: "10.1177/01708406241295505"
  type: "journal"
  authors: "Kaufmann, L., Krlev, G., & Brown, M. (."
  year: 2025
  title: "In Plain Sight: Mechanisms of means–ends decoupling in impact investing"
  venue: "Organization Studies"
  vol: "46"
  issue: "5"
  pages_or_artno: "667-692"
- doi: "10.1016/j.gfj.2026.101305"
  type: "journal"
  authors: "Ge, X., & Luo, Q."
  year: 2026
  title: "Greenwashing in green mutual funds: Symbolic ESG vs. substantive carbon emissions"
  venue: "Global Finance Journal"
  vol: "72"
  pages_or_artno: "101305"
- doi: "10.1016/j.ipm.2025.104383"
  type: "journal"
  authors: "Chen, J., Wen, J., Deng, Y., Chen, M., & Ma, F."
  year: 2026
  title: "Measuring policy diffusion intensity: A text-driven analysis of government documents"
  venue: "Information Processing & Management"
  vol: "63"
  issue: "2"
  pages_or_artno: "104383"
new_dois: []
---

## CORE

【构念与来源】
`token_adopt_int_p75_allv` 系列衡量的是"象征性(symbolic/token)金科采纳"这一制度理论构念在银行-年层面的发生比例, 出自 stage 16 文章级政策对齐/金科强度四象限分类(`policy_cosine_sim` × `fintech_intensity_score`)在面板聚合层的产物(`pipeline/panel/runner.py` 象限分类主循环)。其理论谱系承接组织制度理论中经典的"言行分离/脱耦"(decoupling)框架: 组织可以在话语层面(公开声明、政策对标)与实际行动层面(资源投入、业务落地)之间产生不同步——高调宣称对标监管政策方向, 却未匹配相应的实质性金科业务强度, 即为"仅表态、少落地"的 Token 采纳; 反之亦有"闷声干活、少宣传"的 Hidden 采纳, 以及两头都高的 Substantive(实质)采纳。三者共同构成一个 2×2 象限分类系统的三个非基准格(第四格——两头都低——不计入任何一个 adopt_* 列, 视为"未观测到明显金科政策响应"的基准状态)。`export.py` 注释将该三分类框架标注为源自 Distel et al. (2026), 呼应了银行数字化/金融科技文献中区分"言语承诺"与"实质投入"的一贯关切(如 Gomber, Koch & Siering (2017) 对数字金融/FinTech 研究方向的系统梳理中强调, 银行对金融科技的响应存在从话语层面的战略叙事到真实产品/渠道投入的连续谱, 二者并不总是同步演进)。

本列具体锚定的是"int"(intensity, Track B)词频侧与"allv"(all-vintage, 全语料静态锚点)相似度侧的组合, 且分位阈值取 P75(高位阈值, 即"高强度/高对齐"判据从严, 只有排在同年样本前 25% 的文章才被记为"高")。`token_adopt_int_p75_allv` 对应的是"高强度、低相似度"这一格(`runner.py::_classify_policy_quadrants` 明确定义 `token = high_freq & ~high_sim`, 源码注释直书"洗科技"): 同一篇文章的 `fintech_intensity_score`(基于 Track B 连续型强度打分, 而非 Track A 的去重关键词计数)排在同年样本 P75 以上(即业务强度信号强), 但 `policy_cosine_sim_allv` 未达到同年 P75 分位(即该文章的措辞/主题与当局金科政策话语对齐度不高)——该文章"业务强度信号响, 但对政策话语的调子对得不齐"。这正是 Token 采纳(象征性响应)在本仓库操作化定义下的构念含义: 高实质强度信号 + 低政策话语对齐, 即业务/新闻侧动作看似热闹, 却未见与监管政策方向的紧密贴合, 隐喻"蹭热度而非真正呼应政策"的洗科技(washing)行为。需特别提醒: 与"高相似、低强度"(政策话语调子高但业务强度弱)对应的是 Hidden 象限(`hidden = ~high_freq & high_sim`, 源码注释"闷声干大事"), 不属本家族, 二者构念方向相反, 引用/复述本列定义时不可颠倒。

【方法学与计算】
象限分类的输入是两条独立测量的文章级连续变量: 相似度侧取 `policy_cosine_sim_allv`(及其三轨孪生 `_ctx`/`_ss`), 由文章嵌入与政策文本嵌入的余弦相似度构成, "allv" 后缀标记其锚点为全语料静态口径——即政策参照向量不随发文年份(vintage)滚动更新, 而是用覆盖全部年份的静态锚点计算, 与不带 `_allv` 的"vintage 主轨"(逐年更新政策锚点)构成一对互为稳健性的锚点变体(`runner.py::_anchor_variants` 双循环, 二者共用完全相同的 track × 词频 × 分位三层构造逻辑, 唯一区别是相似度阈值列的基名)。词频侧取 `fintech_intensity_score`(Track B, "int"), 是一个基于金科词表命中强度的连续打分, 与 Track A("kw", 基于 AC 自动机去重关键词计数)是两套独立度量口径, 各自在家族体系中并排产生 `token_adopt_kw_p75` 等镜像列(不属本家族, 但共享同一象限分类算法骨架)。

计算流程为: 对每篇文章分别在其所属 track(full/ctx/ss)内计算 `policy_cosine_sim_allv{_track}` 与 `fintech_intensity_score{_track}` 两列相对同一发文年度内样本(`groupby('year').transform(quantile)`)的 P75 分位阈值, 而后据双列布尔值组合分类。关键的缺测处理原则(修复自早期版本的隐性缺陷, 见 `runner.py` 注释 omni-g-runner-03): 若相似度或强度任一测量缺失(NaN, 多因 stage 15/16 优雅早退——例如政策文本嵌入失败——产生的全 NaN 列), 该篇文章直接被排除出分类分母, 绝不被当作"低于阈值"计零处理。这保证了"高相似度阈值判定失败"与"真实测量结果为低值"不会被混淆, 面板聚合层的 `mean()` 分母始终是"双测量均成功"的篇数子集。银行-年面板值即为该银行该年内落入 Token 象限的文章数 / 双测量成功文章总数, 是一个 [0,1] 区间的比例型指标; 若某银行-年全部文章双测量均失败(如整年 stage 15/16 早退), 该银行-年该列输出 NaN 而非伪零, 与仓库"无数据=未测量"的既定契约(参见其余四象限族 v6/F3 注释)一致。

需特别说明分位阈值的计算范围: P75 阈值是在发文年度内(`df_align.groupby('year')[col].transform(...quantile...)`, 而非全样本合并、也非银行-年双重子样本)分别计算的年度切点, 即同一年份内所有银行的文章共用一把该年的 P75 尺子, 但不同年份的阈值绝对水平会各自独立浮动, 不是跨全部年份统一冻结的固定切点。这一设计使象限分类天然剥离了"整体语料随时间扩容/政策话语随时间演化"导致的年度基线漂移——某年金科报道整体强度普遍抬升(或政策话语整体更趋一致)不会机械地把该年更多/更少文章推过阈值, 每年的"高/低"都是相对当年同侪的相对位置判定, 因此象限分类在跨年份比较上具有可比性; 但阈值仍是在年度截面内计算(而非银行-年内计算), 故不会因某银行某年自身文章数少而产生阈值噪声——阈值稳健性来自"同年全部银行共用一把尺子"而非"全部年份共用一把尺子"。跨版本比较(T=2 dev 语料 vs 生产 T=19 全量语料)时应留意: 语料规模扩容不改变"逐年计算"这一机制本身, 但会改变每年参与分位数计算的文章绝对数量, 小样本年份的分位数估计噪声相对更大。

三轨(full/ctx/ss)与全年份锚点(vintage 主轨 vs `_allv` 静态锚点)在本族内是两条相互独立、正交的稳健性维度: 三轨衡量"用哪部分文本(全文/实体窗口/银行-金科同句窗口)计算相似度与强度", 锚点维度衡量"政策参照向量是否逐年滚动更新"。两个维度各自 just-identified 并排, 互为稳健性、不分主次, 禁止将同一构念的不同轨道或不同锚点变体同时塞入同一个 over-identified Hansen J 检验; ss 轨在无银行∧金科同句共现时镜像 ctx 轨的回退语义, 退化为使用全文 body 并置位 `ss_is_fallback=True`(与 stage 14 物化的三轨文本架构口径一致)。留篇门控采用 full-only 口径(2026-06-29 起): 一篇文章是否被计入 n_articles 分母, 只看其 full 轨的 `llm_verified_full` 判定结果; ctx/ss 轨的象限分类因此是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 轨留篇集合的子集, 而非独立样本。

【文献定位】
Token/Hidden/Substantive 三分类象限的理论根基是组织对外部制度压力的响应存在"言"与"行"两个可分离维度这一制度理论洞见, 银行业金融科技化情境下, Gomber, Koch & Siering (2017, *Journal of Business Economics*) 系统梳理了数字金融/FinTech 研究脉络, 指出传统金融机构对金融科技浪潮的响应既包含战略叙事/公开表态层面, 也包含产品与渠道投入层面的实质行动, 二者演进节奏未必同步, 为区分"话语层"与"行动层"响应提供了文献依据。Adner & Kapoor (2010, *Strategic Management Journal*) 关于创新生态系统中技术互依结构如何影响企业绩效的研究, 进一步支持了"采纳意愿的对外表达"与"采纳的实际技术/资源投入"可被独立测量并产生不同绩效含义这一识别策略前提。Boot (2000, *Journal of Financial Intermediation*) 对关系型银行业的经典综述, 提示银行对外部创新压力的响应模式与其既有关系型业务模式的兼容程度密切相关——这为解释为何部分银行仅在话语层面对标金科政策却迟迟未落地实质投入(Token 象限)提供了制度/战略惰性视角的背景解释。Fang, Wang, Wang & Zhao (2023, *Economic Modelling*) 关于中国银行业金科投入与流动性创造、风险承担关系的实证研究, 与本族测度共享"用连续型强度打分刻画银行金科真实投入水平"的方法论关切, 为 Track B("int")强度打分而非单纯关键词计数的合理性提供了同域实证先例。 上述制度理论谱系在近期文献中获得了更直接的补强。Kaufmann、Krlev 与 Brown (2025) 以影响力投资为田野, 系统刻画了 means-ends decoupling (政策/实践在形式上落地却与目标脱节) 的具体机制, 正是本族 Token 与 Substantive 两格理论区分所依托的脱耦框架的近期组织学表述; 但该文为定性机制研究, 不构造任何数值指标, 更无分位阈值二值化或银行-年聚合, 场域为影响力投资机构而非中国银行业, 其 means-ends 概念与本族「政策余弦 × 金科强度」的操作化仅属理论对应而非同一测量。Ge 与 Luo (2026) 把绿色基金的「象征性 ESG (声明/评级层面)」与「实质性碳排放 (真实结果层面)」分别测量后交叉比对以识别洗绿, 与本列 Token 象限 (强度高、对齐低) 的识别逻辑同构; 其边界在于层级为基金-期, 象征维用 ESG 声明/评级、实质维用组合碳排放, 两维均非文本测度, 亦不用年度分位阈值把双维二值化成 2×2 象限。相似度侧的方法学谱系可参照 Chen、Wen、Deng、Chen 与 Ma (2026): 该文以政府文件文本为基础构造政策扩散强度的文本驱动测度, 与本族 sim 维同属「用政策文本相似度/强度刻画政策对齐程度」的方法族; 但其测的是政府文件之间的扩散强度 (政府—政府层级), 本族则是新闻报道文本对政策锚点的余弦相似度 (媒体—政策层级), 且原文不做二值象限分类、不设年度分位阈值, 也没有全语料静态锚点与逐年滚动锚点相互对照的稳健性设计, 故仅可作为 sim 维的方法学存在性锚点, 不能据以主张其验证过本族的锚点变体对照。
## VAR: token_adopt_int_p75_allv

【变体差分】
本列是 full 轨(标题+正文全文, 无轨道后缀)、`_allv` 全年份静态锚点的 Token 象限比例: `fintech_intensity_score`(无后缀, 全文轨 Track B 强度打分)排在同年样本 P75 以上, 且 `policy_cosine_sim_allv`(无后缀, 全文轨政策相似度)未达同年样本 P75, 二测量均非缺测的文章占该银行-年双测量成功文章总数的比例(强度高、对齐低=洗科技式 Token 采纳, 而非相似度高、强度低——后者是 Hidden 象限, 不属本列)。留篇门控与分母口径均取 full 轨自身的 `llm_verified_full`/双测量成功状态, 是本族三轨中的口径起点, 但不因此获得优先解释力——full/ctx/ss 三轨在本仓库口径中互为稳健性并排陈列, 不分主次。作为三轨之一, 该列与全年份锚点维度(vintage 主轨 `token_adopt_int_p75`, 无 `_allv` 后缀)构成第二条正交稳健性维度; 两条维度共 2×3=6 个变体在数值上会因样本量、锚点更新方式不同而彼此不完全相等, 差异本身即是稳健性证据的一部分, 不应被解读为"哪个更准"。

full 轨相似度与强度均取全文(标题+正文全部句子)计算, 是三轨中信息覆盖最广、噪声也可能最多的一支: 全文既包含与银行金科政策高度相关的核心段落, 也包含与主题无关的背景介绍、免责声明、行情走势等套话性文本(参见家族 boilerplate 比率相关测度), 相似度打分因此可能被稀释, 强度打分也同样受套话文本的分母效应影响。`_allv` 锚点意味着政策参照向量是覆盖 2007–2025 全部年份的静态嵌入, 不随文章发文年份滚动, 因此能剥离"政策文本本身逐年演化"对相似度打分产生的时间趋势性漂移, 使跨年份比较更纯粹地反映银行侧的响应变化而非监管话语本身的语义漂移; 与之相对的 vintage 主轨(无 `_allv` 后缀)则允许政策锚点逐年滚动更新, 更贴合"当期政策语境"但引入了锚点本身的时间序列噪声。两种锚点口径各有取舍, 在本仓库中并排呈现、不设优先级, 使用方应视研究问题对"跨期可比性"与"当期语境贴合度"的相对权重自行取舍并报告两者结果作为稳健性互证。

## VAR: token_adopt_int_p75_allv_ctx

【变体差分】
本列切到 ctx 轨(标题+实体窗口文本)计算相似度与强度: 分类所用列为 `policy_cosine_sim_allv_ctx` 与 `fintech_intensity_score_ctx`(词频侧优先取同轨变体, `runner.py` 明确注释 ctx/ss 轨优先用 `{freq_col}{_sim_sfx}` 同轨列, 缺列才回退 full), P75 阈值同样在 ctx 轨、按发文年度分组独立计算(而非沿用 full 轨阈值), 故 ctx 轨的"高/低"判定边界与 full 轨可能不同。行宇宙受 full-only 留篇门控约束, 是 full 轨留篇集合的子集(2026-06-29 起 ctx 降为 conditional-on-full 稳健性轨, 不再独立门控整篇文章的去留)。ctx 轨的政策相似度窗口更聚焦于银行/金科相关实体周边文本, 理论上更能剥离与政策无关的段落噪声对相似度打分的稀释效应, 是与 full 轨/ss 轨并排、互为稳健性的独立测量, 禁止与其余轨混入同一 over-identified 检验。

具体而言, ctx 轨的文本物化发生在 stage 14(`content_ctx`, `prepend_title` 后再截取围绕目标银行/金科实体的窗口), 相似度与强度打分均在这一更聚焦的窗口文本上重新独立计算, 而非对 full 轨打分做任何裁剪或加权变换——这意味着 ctx 轨与 full 轨即便针对同一篇文章, 相似度与强度数值也可能出现方向性差异(例如某篇文章全文夹杂大量与政策无关的行情快讯, full 轨相似度被拉低而 ctx 轨因聚焦实体窗口反而相似度更高, 二者对该文章是否落入 Token 象限的判定可能不一致)。这种"同一篇文章在不同轨道上被分入不同象限"的现象是设计使然而非缺陷: 它反映了"文章整体基调"与"文章中与目标实体直接相关部分的基调"两种不同但都合理的操作化选择, 二者的不一致程度本身也可作为稳健性诊断的附带信息。窗口半径由 `config/filtering.yaml::context_window` 相关键控制, 与家族口径保持一致。

## VAR: token_adopt_int_p75_allv_ss

【变体差分】
本列切到 ss 轨(银行∧金科同句±N窗, 窗口半径见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认1): 分类所用列为 `policy_cosine_sim_allv_ss` 与 `fintech_intensity_score_ss`, P75 阈值在 ss 轨、按发文年度分组独立计算。ss 轨口径镜像 ctx 轨的回退语义: 若某文章不存在银行与金科词的同句共现, 则该文章的 `content_ss` 回退为全文 body 且 `ss_is_fallback=True`(与 ctx/full 共享 `n_articles` 分母, 而非产生额外的孤儿测量), 使得 ss 轨在无同句共现证据时退化为与 full 轨高度重叠的测量, 但仍保留独立计算的 P75 阈值与独立的双测量缺测排除逻辑。行宇宙同样受 full-only 留篇门控约束, 是 full 轨留篇集合的子集。ss 轨是本族三轨中判据最严格(要求银行与金科词汇同句而非仅同文出现)的一支, 与 full/ctx 两轨并排构成互为稳健性、不分主次的第三条测量, 三者严禁混入同一 over-identified Hansen J 检验。

ss 轨的判据比 ctx 轨更进一步收窄: ctx 只要求实体出现在同一窗口内, ss 则要求银行词与金科词字面上出现在同一个句子中(±N 句半径, 默认 N=1), 是三轨中对"文章确实在同一话语单元内谈论银行与金科关联"这一判据最严格的一支。对于本族象限分类而言, ss 轨的政策相似度与强度打分因此更集中反映"银行与金科紧密共现的那句话及其邻近句"所携带的语义信息, 理论上应比 ctx/full 更少受无关段落污染, 但代价是当同句共现证据稀薄时(尤其在语料样本较小的开发环境下)大量文章触发 fallback, 退化为与 full 轨趋同, 此时 ss 轨相对 ctx/full 的边际信息量下降, 使用方在小样本场景下应留意 `ss_is_fallback` 触发率对该列判别力的影响, 并将其作为解释稳健性结果时的背景说明。

<!-- rendered-citations:begin -->
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537–580. https://doi.org/10.1007/s11573-017-0852-x
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306–333. https://doi.org/10.1002/smj.821
Boot, A. W. A. (2000). Relationship banking: What do we know?. Journal of Financial Intermediation, 9(1), 7–25. https://doi.org/10.1006/jfin.2000.0282
Fang, Y., Wang, Q., Wang, F., & Zhao, Y. (2023). Bank fintech, liquidity creation, and risk-taking: Evidence from China. Economic Modelling, 127, 106445. https://doi.org/10.1016/j.econmod.2023.106445
Kaufmann, L., Krlev, G., & Brown, M. (. (2025). In Plain Sight: Mechanisms of means–ends decoupling in impact investing. Organization Studies, 46(5), 667-692. https://doi.org/10.1177/01708406241295505
Ge, X., & Luo, Q. (2026). Greenwashing in green mutual funds: Symbolic ESG vs. substantive carbon emissions. Global Finance Journal, 72, 101305. https://doi.org/10.1016/j.gfj.2026.101305
Chen, J., Wen, J., Deng, Y., Chen, M., & Ma, F. (2026). Measuring policy diffusion intensity: A text-driven analysis of government documents. Information Processing & Management, 63(2), 104383. https://doi.org/10.1016/j.ipm.2025.104383
<!-- rendered-citations:end -->
