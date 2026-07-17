---
family_id: F615
columns:
- washing_ratio_loughran
- washing_ratio_loughran_ctx
- washing_ratio_loughran_ss
unit: 比率/占比 (proportion, 定义域 [0,1]; 分母为空时该行记为缺失, 不强制填 0)
formula: 'washing_ratio_loughran{track} = count(loughran_score{track} > 0 且 innovation_substantiveness_full == "象征性") / count(loughran_score{track} > 0 且 innovation_substantiveness_full ∈ {"象征性","实质性"} 已测量)'
producer: pipeline\panel\runner.py (步骤 7h 篇章级标记 + 聚合) ; pipeline\panel\export.py (列标签注入)
upstream:
- loughran_score_full
- loughran_score_ctx
- loughran_score_ss
- innovation_substantiveness_full
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: 'Textual analysis in accounting and finance: A survey'
  venue: Journal of Accounting Research
  vol: '54'
  issue: '4'
  pages_or_artno: 1187-1230
- doi: 10.1017/S0022109023000716
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2024
  title: Measuring firm complexity
  venue: Journal of Financial and Quantitative Analysis
  vol: '59'
  issue: '6'
  pages_or_artno: 2487-2514
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.1016/j.frl.2026.109684
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: 'AI washing: Strategic disclosure and backlash'
  venue: Finance Research Letters
  vol: '95'
  issue: ''
  pages_or_artno: '109684'
- doi: "10.1016/j.frl.2024.105401"
  type: "journal"
  authors: "Zhang, Z., Hou, Y., Li, Z., & Li, M."
  year: 2024
  title: "From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105401"
new_dois: []
---

## CORE

【构念与来源】
washing_ratio_loughran 族衡量的是"言辞正面但内容空心"的洗稿式报道在某银行—年报道流中所占的比例, 是家族 washing_ratio 系列 (方法 D2, 单词典口径) 在 Loughran-McDonald (以下简称 L&M) 词典轨上的具体实现。该测度的构念来源于 Westphal & Zajac (1998, Administrative Science Quarterly) 对企业"象征性采纳"(symbolic adoption) 与"实质性采纳"(substantive adoption) 的区分——企业可以只在言辞和公告层面模仿某项创新(如金融科技合作), 而不在组织内部真正落实。本 pipeline 把这一区分平移到银行—金科关系的新闻文本上: 一篇报道若同时满足"用 L&M 词典打出正面语气分数"(loughran_score{track} > 0)与 LLM 判定为"象征性"(而非"实质性"), 则计入分子; 分母是同一词典分数为正、且实质性/象征性标签已被成功测出的报道总数。washing_ratio_loughran{track} 越高, 说明该银行—年围绕金科的正面报道里, 缺乏实质业务内容支撑的"表演式"报道占比越大。这与文献中的"漂绿"(greenwashing)/"洗白"(washing)概念同构: Song, Hou, Ouyang & Hao (2026, Finance Research Letters) 讨论的 AI washing——企业在披露中夸大 AI/科技投入而缺乏实质行动引发市场反噬——与银行—金科语境下的"washing"高度平行, 都是"言辞—行动"落差的量化尝试。

【方法学与计算】
计算链条分两层。第一层是 L&M 词典打分: loughran_score{track} 由 stage 22 dict-sentiment 引擎在 Loughran & McDonald (2011, The Journal of Finance) 建立的金融领域正负面词典上运行规则消融口径(否定翻转/程度副词/转折三条语言学规则的 canonical 全规则版, 非消融变体)得到, 是一个连续打分, 大于 0 视为该篇报道语气偏正面(该词典是六本词典之一, 属于家族"词典消融梯度"中 6 词典×3 轨×多消融变体矩阵的一格; washing_ratio_loughran 只取 canonical 全规则、无消融后缀的那一格)。第二层是象征性/实质性标签: innovation_substantiveness_full 由 stage 21 三家 LLM (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 在 full 轨(标题+全文正文)上共同判定, 取值"象征性"或"实质性"(或未测出); 该标签口径固定用 _full 轨, 不随本列自身的 full/ctx/ss 轨道切换——因为象征性判断依赖报道整体叙事完整度, 切到窄窗口(ctx/ss)容易因上下文缺失而误判, 故沿用留篇门控(2026-06-29 起口径)所对齐的 full-only 判定基准。分子分母同域构造是本族的关键工程细节(fix omni-g-runner-10, 2026-06-11 修正): 若直接以"L&M 正面 ∧ 象征性"为分子、以"L&M 正面"全体为分母, 则当 LLM 未能测出某些报道的实质性标签时(网络失败、格式解析失败等), 这些报道只会拖累分母、不会进入分子, 导致 washing_ratio 被系统性低估——分类失败率越高, 假象上的"洗稿率"越低, 这与真实洗稿程度无关, 纯属测量伪影。为消除这一伪影, 分母被限定为"L&M 正面 ∧ 实质性标签已成功测出(象征性或实质性二选一)"的同域计数, 与分子共享同一"标签有效"前提, 这样分类失败率的变化不再机械地驱动比率漂移。三条后缀 _full/_ctx/_ss 对应 stage 14 物化的三条文本轨: full=标题+正文全文, ctx=标题+银行/金科实体窗口, ss=标题+银行∧金科同句(±1 句半径, 见 config/filtering.yaml::context_window.ss_sentence_radius)共现窗口; 三轨仅体现在 loughran_score{track} 这一侧(词典打分随文本窗口变化), 实质性标签侧固定 full。ss 轨遵循与 ctx 轨相同的回退语义: 若某篇报道不存在银行∧金科同句共现, 则 content_ss 退化为全文正文, ss_is_fallback 标记为真, washing_ratio_loughran_ss 在此类回退行上与 washing_ratio_loughran(full 轨的 loughran_score 分数)高度重合但并非恒等(因为分母的实质性标签测量成功与否与轨道无关, 但正面判定阈值 loughran_score{track}>0 仍按各自轨的打分实际计算)。

【文献定位】
本族测度站在两条文献线的交叉点上。其一是文本情感词典法本身: Loughran & McDonald (2011, The Journal of Finance) 首次证明通用情感词典(如 Harvard-IV)套用在金融文本上会系统性误判, 由此构建了面向 10-K 文本的领域专属词典, 成为会计与金融文本分析领域事实标准之一; Loughran & McDonald (2016, Journal of Accounting Research)的综述进一步梳理了文本分析方法在会计与金融研究中的应用边界和陷阱, 为本族"词典打分仅是构念的一个代理、须与语言学规则消融和多词典并排稳健性检验搭配使用"的设计取向提供依据; Loughran & McDonald (2024, Journal of Financial and Quantitative Analysis) 关于测量企业文本复杂度的近期工作, 延续了同一方法论传统, 佐证词典法在测度构念(而非仅统计词频)上的持续生命力。其二是象征性—实质性区分与漂绿/洗稿文献: Song, Hou, Ouyang & Hao (2026, Finance Research Letters) 讨论的 AI washing 现象——企业在言辞层面夸大技术投入而无实质行动支撑, 一旦被市场识破会引发股价反噬——与本族测度试图捕捉的"言辞正面但内容空心"的银行—金科报道高度呼应; Gorovaia & Makrominas (2024, European Financial Management) 用自然语言处理方法在企业社会责任报告中识别漂绿信号, 提供了将词典/NLP 判定与"言辞—行动"落差检测相结合的方法学参照, 是本族"词典打分 + LLM 象征性标签"双层构造思路的直接方法学先例。washing_ratio_loughran 是家族 washing_ratio 系列(方法 A=LLM 多数投票版、A2=单 LLM 版、D=6 词典均值版、D2=单词典版、E/E2=BERT 版、F=高置信度子样本版)在 D2·L&M 词典这一格上的具体实现, 与同族其余方法互为稳健性、不分主次, 目的是验证"洗稿率"这一构念不因情感测量所用的具体方法(LLM/词典/BERT)而系统性改变结论。三轨(full/ctx/ss)之间同样是并排的稳健性关系: 三者各自 just-identified, 互为稳健性检验, 绝不应混入同一个 over-identified 的 Hansen J 检验框架; ss 轨的回退语义严格镜像 ctx 轨(无共现即退化为全文、标记 is_fallback), 二者共享同一分母口径 n_articles。 象征占比作为结构性比例而非绝对水平的处理方式, 亦见于近期绿色创新文献: Zhang、Hou、Li 与 Li (2024) 研究 ESG 评级如何推动企业创新结构从象征性向实质性迁移, 把「象征性占比」当作可随外部监督变化的结构比例来分析, 与本族取「正面 ∧ 象征性」计数除以「正面 ∧ 实质性已测」计数的分母同域设计逻辑一致; 但其比例基于专利结构数据, 主体为中国 A 股非金融企业, 驱动因素为 ESG 评级, 且全文未使用任何文本判定器, 因此该文仅锚定象征占比这一构念层设计, 不对本族所用的 L&M 词典口径本身提供佐证。
## VAR: washing_ratio_loughran

【变体差分】
本列是 washing_ratio_loughran 族的 full 轨、亦是家族 canonical 基准列。轨道口径: loughran_score_full 由标题+全文正文(stage 14 物化的 content_full)驱动 L&M 词典打分, 不做实体窗口截断, 词典能看到报道全部正文信息, 因此正面判定 loughran_score_full > 0 的样本量通常是三轨中最大的一个(不受实体窗口/同句共现筛选影响), 分母也相应最宽。分子侧的实质性标签 innovation_substantiveness_full 本身就在 full 轨上测出, 与本列的文本窗口天然对齐, 不存在轨道错配问题——这是三条轨道中唯一"词典打分轨"与"标签测定轨"完全同源的一列, 因而在解释力上通常被视为该族的主口径参照点, 但按家族铁律, 它与 _ctx/_ss 两列仍是并排稳健性关系而非层级主次关系, 三者共同验证"银行—金科洗稿式报道占比"这一构念不因文本窗口选取而系统性漂移。留篇门控(2026-06-29 起)以 llm_verified_full 为准, 即本列所在的行宇宙就是"确认为银行—金科报道"的 full 判定集合, ctx/ss 两列是在该集合子集上的条件测度(conditional-on-full), 不构成独立的留篇口径。由于分子分母同域构造(fix omni-g-runner-10)的存在, 本列对 LLM 实质性分类失败率的敏感度最低——因为分母限定为标签已成功测出的正面报道, 分类失败不会像旧口径那样机械压低比率; 但当某银行—年报道量本就很小、且大量报道 L&M 词典打分恰好为 0 或负时, 分母可能趋近于 0, 此时该行按约定记为缺失而非强制填 0, 使用时须核对分母样本量再解读比率数值, 避免小样本导致的极端比率误导结论。

## VAR: washing_ratio_loughran_ctx

【变体差分】
本列使用 ctx 轨(标题+银行/金科实体窗口物化文本 content_ctx, stage 14 ctx_materializer 产出)计算 loughran_score_ctx, 分子分母判定逻辑与 canonical 列完全相同(正面∧象征性 / 正面∧已测标签), 唯一差异是词典打分所依赖的文本窗口被收窄到实体邻近区域, 排除了报道中与银行—金科关系无直接语义关联的段落。这意味着 ctx 轨的 L&M 正面判定更聚焦于"围绕银行与金科实体本身"的措辞语气, 理论上能过滤掉因文章其他部分(如宏观经济评论、行业综述段落)带来的语气噪声, 但也可能因窗口过窄而丢失部分能佐证"实质性"或"象征性"的上下文线索——不过后者由固定 full 轨的实质性标签兜底, 不受 ctx 窗口收窄影响。本列与 canonical 列(full)、_ss 列共享同一"实质性标签已测出"分母同域构造(fix omni-g-runner-10), 三者互为稳健性并排, 分子分母行宇宙均为 full-only 留篇门控下的子集, 分母 n_articles 定义在三轨间共享。ctx 轨没有 ss 轨那样的"回退到全文"机制——若实体窗口物化失败或窗口内文本为空, content_ctx 会退回全文正文并标记 ctx_is_fallback, 与 ss 轨回退机制在设计上完全并行, 但在洗稿率语境下二者的实际触发条件不同: ctx 依赖实体识别成功率, ss 依赖银行与金科关键词是否同句共现, 后者的回退触发频率通常显著高于前者, 因此本列与 _ss 列的样本组成(有效窗口 vs 回退全文)存在系统性差异, 解读时不应把 ctx 与 ss 的比率差异简单归因于"窗口紧窄程度", 还须考虑各自回退比例的不同。

## VAR: washing_ratio_loughran_ss

【变体差分】
本列使用 ss 轨(标题+银行∧金科同句共现窗口物化文本 content_ss, 句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 ±1 句)计算 loughran_score_ss。判定逻辑与另两列一致, 差异同样只体现在词典打分的文本窗口: ss 轨要求银行与金科关键词在同一句(或半径窗口内)出现才纳入正文, 是三轨中最严格的窗口口径。ss 回退语义严格镜像 ctx 轨: 若某篇报道不存在满足条件的同句共现, content_ss 退化为全文正文, ss_is_fallback 标记为真, 此时该行的 loughran_score_ss 实际上等价于在全文上打分(与 canonical full 列的输入文本一致, 但分母仍按 ss 轨自身的正面判定阈值独立计算, 不与 full 轨分母合并)。分母共享 n_articles 口径, 不因回退而重新定义样本总量。与另外两轨相同, 分子的实质性标签固定取自 innovation_substantiveness_full, 不随本列窗口收紧而改变来源轨道。ss 轨作为三轨中信息密度最集中、噪声最少但样本覆盖(非回退比例)最窄的一支, 是该族稳健性检验中对"语义强相关性"要求最高的一格, 与 full、ctx 两列并排、互为稳健性, 禁止三者混入同一 over-identified 回归识别框架。由于 ss 轨的回退触发条件(无银行∧金科同句共现)比 ctx 轨的回退条件(实体识别失败)宽松得多, 本列在实践中回退到全文的样本占比通常明显高于 ctx 轨, 这意味着一个不小的样本子集上 washing_ratio_loughran_ss 与 washing_ratio_loughran(full 轨)在词典打分输入文本上是等价的, 二者的比率差异主要来自未回退部分——即银行与金科确实同句出现的那批报道——上的语气与分母构成差异。对研究者而言, ss 轨的价值在于当银行与金科被同句提及时, 措辞语气更可能直接反映二者关系的实质而非泛泛提及, 是三轨中对"洗稿"构念在语义上最贴近的一支, 但样本覆盖窄意味着标准误通常更大, 须结合 full/ctx 两轨联合解读, 不宜单独作为唯一证据。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2024). Measuring firm complexity. Journal of Financial and Quantitative Analysis, 59(6), 2487-2514. https://doi.org/10.1017/S0022109023000716
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, 109684. https://doi.org/10.1016/j.frl.2026.109684
Zhang, Z., Hou, Y., Li, Z., & Li, M. (2024). From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure. Finance Research Letters, 63, 105401. https://doi.org/10.1016/j.frl.2024.105401
<!-- rendered-citations:end -->
