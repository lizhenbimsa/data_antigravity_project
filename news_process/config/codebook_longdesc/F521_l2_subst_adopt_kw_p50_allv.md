---
family_id: F521
columns:
- subst_adopt_kw_p50_allv
- subst_adopt_kw_p50_allv_ctx
- subst_adopt_kw_p50_allv_ss
unit: 无量纲比例 (bank-year 内已测量文章中落入"实质采纳"象限的占比, 值域 [0,1], 未测量年份=NaN)
formula: 'groupby(target_bank, year) 上 mean( 1{fintech_distinct_keywords{_trk} >= 年度P50(该轨词频) AND policy_cosine_sim_allv{_trk} >= 年度P50(该轨相似度)} ), 仅对词频与相似度双双非缺失的文章计入指示与分母; _classify_policy_quadrants() 产出'
producer: pipeline\panel\runner.py (`_classify_policy_quadrants` 逐篇四象限分类器 + 7h 步骤四象限占比聚合循环); pipeline\panel\export.py (STATA_LABELS 标签映射, 不改变数值)
upstream:
- 15_fintech_intensity (fintech_distinct_keywords 词频; policy_cosine_sim_allv 全语料静态政策锚点相似度)
- 24_herd_decay_processor (`_filter_to_verified_universe` semi-join, 决定进入四象限分类的文章全集)
citations:
- doi: "10.2307/2393295"
  type: journal
  authors: "Westphal, J. D., & Zajac, E. J."
  year: 1994
  title: "Substance and Symbolism in CEOs' Long-Term Incentive Plans"
  venue: "Administrative Science Quarterly"
  vol: "39"
  issue: "3"
  pages_or_artno: "367-390"
- doi: "10.5465/amj.2006.23478255"
  type: journal
  authors: "Fiss, P. C., & Zajac, E. J."
  year: 2006
  title: "The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling"
  venue: "Academy of Management Journal"
  vol: "49"
  issue: "6"
  pages_or_artno: "1173-1193"
- doi: "10.1287/orsc.2014.0949"
  type: journal
  authors: "Kim, E.-H., & Lyon, T. P."
  year: 2015
  title: "Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure"
  venue: "Organization Science"
  vol: "26"
  issue: "3"
  pages_or_artno: "705-723"
- doi: "10.1287/mnsc.2024.07420"
  type: journal
  authors: "Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C."
  year: 2026
  title: "\"Glossy Green\" Banks: The Disconnect Between Environmental Disclosures and Lending Activities"
  venue: "Management Science"
  pages_or_artno: "advance online publication"
- doi: "10.1111/joms.13043"
  type: "journal"
  authors: "Athanasopoulou, A., Marti, E., Risi, D., & Schlindwein, E."
  year: 2025
  title: "How Companies Restrain Means–Ends Decoupling: A Comparative Case Study of CSR Implementation"
  venue: "Journal of Management Studies"
  vol: "62"
  issue: "1"
  pages_or_artno: "214-245"
- doi: "10.1016/j.frl.2024.105265"
  type: "journal"
  authors: "Huang, J., & Ma, L."
  year: 2024
  title: "Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105265"
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
本家族衡量银行金融科技新闻报道中"实质性采纳" (substantive adoption) 相对于"象征性/隐性采纳" (token/hidden adoption) 的相对占比, 构念源自组织理论中"实质与象征" (substance vs. symbolism) 的经典二分——企业对外沟通/制度实践既可以是名实相符的实质性行动, 也可以是名不副实的象征性姿态或反过来做而不说的"闷声干大事" (Westphal & Zajac, 1994, *Administrative Science Quarterly*; Fiss & Zajac, 2006, *Academy of Management Journal*)。落到银行金融科技报道的语境: 一篇报道若既高频提及金融科技关键词、又与官方金融科技政策文本高度语义对齐, 判定其处于"实质采纳" (Substantive) 象限——高谈阔论且言之有物; 若词频高但政策对齐低, 判定"Token" (蹭热点/表面化提及, 缺乏与政策议程的实质呼应); 若词频低但政策对齐高, 判定"Hidden" (低调但方向正确, 悄悄落地); 两者皆低则为不相关象限 (未纳入本三列, 仅在四象限内部作为剩余类别隐含存在)。该"言有物/言无物"二分与漂绿/漂洗文献中"言辞与实践脱钩" (decoupling) 的构念高度同源 (Kim & Lyon, 2015; Giannetti, Jasova, Loumioti & Mendicino, 2026, *Management Science*), 本家族可视为其在银行金融科技情境下的镜像应用: 用"关键词密度 × 政策语义对齐度"这一可计算的双变量交叉分类, 替代人工判读的实质/象征标签。
本家族三列共享完全相同的构造逻辑与相同的锚点变体 (`_allv` 全语料静态政策锚点), 唯一差异是文本轨道 (full / ctx / ss), 详见各 VAR 节。三轨"各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J"——不应把三轨占比同时塞进单一工具变量方程的超识别检验, 而应各自独立汇报, 互相印证结论的稳健性。

【方法学与计算】
核心分类原语是 `_classify_policy_quadrants(df_align, sim_col, freq_col, pct)` (`pipeline/panel/runner.py`): 对给定轨道, 在年度截面内分别取词频列与相似度列的第 `pct` 百分位数 (本家族固定 P50, 即年度中位数) 作为该年的双阈值; 逐篇文章同时比较词频、相似度是否各自不低于当年阈值, 得到 Token/Hidden/Substantive 三个 0/1 指示 (float dtype)。三个指示互斥 (定义上一篇文章至多落入其一)。分类前置了严格的"未测量=NaN"掩码 (`measured = sim_col.notna() & freq_col.notna()`): 只要该文章的词频或相似度任一缺失 (例如上游 stage 15 三条优雅早退路径写出全 NaN 相似度), 三个指示同置 NaN, 既不误记 False 也不误记 0, 避免"零测量伪装成低词频/低对齐"污染分位数阈值与后续均值。此掩码修复了历史实现 `NaN >= threshold → False` 的静默误分类缺陷 (源码注释 `fix(omni-g-runner-03/g-runner-11, 2026-06-11)`)。
文章级三指示按 `(target_bank, year)` 分组取 `mean`——pandas `mean` 默认跳过 NaN, 因此面板层的占比分母是该 bank-year 内已测量 (词频与相似度双双非缺失) 的文章数, 而非该 bank-year 全部报道数; 若某 bank-year 全部文章均未测量, 面板输出为 NaN (不回填 0, 避免污染 TWFE 系数, 源码注释援引 Allison 2001 §3 关于"未测量≠零"的告诫)。这与家族三列共同的分母口径完全一致, 三列之间可直接横向比较占比水平。
纳入四象限分类循环的文章全集, 先经 `_filter_to_verified_universe` 与 stage 24 (`24_herd_decay_processor`) 做 `(docid, target_bank)` 键的 semi-join 过滤——这一步把分类限定在通过 LLM 情感/相关性核验 (verified) 的文章域内, 与本项目"留篇门控 = full-only" (2026-06-29) 的口径一致: 是否判定"一篇银行金科报道"只看 `llm_verified_full`, ctx/ss 轨在此基础上是 conditional-on-full 的测度轨——即 ctx/ss 象限占比的行宇宙是 full 轨留篇集合的子集, per-track 分类值仍各自独立计算。
`_allv` 是锚点变体标记, 对应相似度分子列 `policy_cosine_sim_allv{_trk}`, 与不带 `_allv` 后缀的"vintage 主轨" `policy_cosine_sim{_trk}` 构成一对稳健性孪生: vintage 主轨的政策锚点向量随年份滚动更新 (逐年用截至当年的政策文本构造锚点), `_allv` 锚点则用全语料 (全部年份汇总) 一次性构造静态锚点, 不随年份变化。二者衡量的是同一构念 (文章与官方金融科技政策议程的语义相似度) 在"锚点是否允许时变"这一构造选择上的两种口径, 互为稳健性, 不分主次, 禁止混入同一 over-identified 方程。词频侧 (`fintech_distinct_keywords`) 与锚点选择无关, 不随 `_allv` 变化, 只随文本轨道 (full/ctx/ss) 变化——即 `_allv` 只改变相似度阈值的构造方式, 不改变词频阈值。

【文献定位】
"实质 vs. 象征"的行为区分脉络可追溯到 Westphal & Zajac (1994, *Administrative Science Quarterly*) 关于 CEO 长期激励计划"言行是否一致"的经典研究, 以及 Westphal & Zajac (1998) 对公司治理改革中股东反应与实际治理变革脱钩的进一步刻画; Fiss & Zajac (2006, *Academy of Management Journal*) 将其发展为"象征性管理"(symbolic management) 的一般理论, 强调组织可通过话语框架 (framing) 与实践脱钩 (decoupling) 应对制度压力而无需真正改变行为。本家族把该二分具体化为可计算的双变量 (词频 × 语义相似度) 阈值交叉, 方法学上呼应文本量化研究中"言辞不必然反映实质行动"的一般提醒 (Kim & Lyon, 2015, *Organization Science*, 提出漂绿/漂棕不对称框架); 银行业情境下的对应实证参见 Giannetti、Jasova、Loumioti & Mendicino (2026, *Management Science*) 关于银行环境信息披露与实际放贷行为脱钩的"光鲜绿色"发现——本家族的 Token 象限 (高词频、低政策对齐) 即结构上对应此类"言过其实"的脱钩情形, 而 Hidden 象限对应相反方向的"言不及义但实至名归"。 在该二分的当代延伸上, Athanasopoulou、Marti、Risi 与 Schlindwein (2025) 以比较案例研究考察企业如何抑制 means-ends decoupling, 即形式采纳在何种条件下能真正转化为实质结果, 恰为本族 Substantive 象限 (词频与政策相似度双双不低于年度中位) 的构念合法性提供顶刊管理学依据; 惟该文为定性比较案例、场域为 CSR 实施, 既无量化指标亦无阈值切分与面板结构, 故只锚定"双高格即脱耦被抑制"的构念解释, 不能视为本族 P50 判据或 bank-year 聚合口径的方法学来源。同域应用上, Huang 与 Ma (2024) 在中国情境中以金融科技发展为解释变量, 检验其对企业实质性绿色创新与象征性绿色创新的差异化影响, 表明"实质 vs. 象征"二分在金融科技议题下已有直接的实证与中文语用先例; 但其实质/象征由专利类型 (发明 vs. 实用新型/外观) 客观划分, 主体为非金融上市公司, 金融科技是解释变量而非被报道的议题本身, 与本族由新闻文本词频与政策相似度交叉判定、主体为银行的口径不同, 不可据以外推本族的阈值选择。Zhang、Hou、Li 与 Li (2024) 研究 ESG 评级如何推动企业创新结构自象征性向实质性迁移, 把象征性占比当作可随外部监督变化的结构性比例来处理, 这一"以构成比而非绝对水平为分析对象"的取向, 与本族把 Substantive 象限占比 (而非金科提及的绝对量) 作为结构性被解释量的设计逻辑一致; 其比例基于专利结构数据、主体为 A 股非金融企业、驱动因素为 ESG 评级, 且未使用任何文本判定器, 故仅锚定象征/实质构成比这一构念, 不涉及本族的词频与相似度测度口径。
## VAR: subst_adopt_kw_p50_allv

【变体差分】
本列是家族的基准 (base) 轨道, 对应文本轨 full (标题+正文全文, 无轨道后缀)。词频分子取 `fintech_distinct_keywords` (stage 15 在全文上统计的去重金融科技关键词命中数, 是 kw 轨——即基于关键词表 Aho-Corasick 命中计数的词频代理, 与另一条未落在本家族的 int 轨 `fintech_intensity_score` 相区分); 相似度分子取全语料静态锚点 `policy_cosine_sim_allv` (无轨道后缀), 即用全部年份汇总构造的一次性静态政策向量, 在 full 文本上计算的余弦相似度。年度分位阈值固定 P50 (中位数), 即以"当年词频中位数以上"与"当年政策相似度中位数以上"两条件的合取判定为 Substantive 象限。
需要特别说明与另外两个非本家族但同一循环产出的姊妹列的边界: `token_adopt_kw_p50_allv` 衡量高词频低对齐 (蹭热点未落地), `hidden_adopt_kw_p50_allv` 衡量低词频高对齐 (低调落地), 二者与本列互斥且共用同一对年度阈值——三者的和 (加上未纳入任何象限的"不相关"剩余类别) 才构成该 bank-year 已测量文章的全集占比分解。本列单独看是"言之有物"型报道在已测量报道中的占比, 数值越高说明该银行在该年度的金融科技相关报道中, 高关键词密度的报道也倾向于与官方政策议程语义高度贴合, 可解读为该银行金融科技传播在词频与政策取向两个维度上的一致性/协同性更强。
分母口径与家族一致: 仅计入该 bank-year 内词频与相似度双双非缺失 (即真正参与过 stage 15 关键词统计与政策相似度打分) 的已核验 (verified, 经 stage 24 semi-join full-only 门控) full 轨文章; 未测量的 bank-year 输出 NaN, 不得与真实零占比混淆。作为不带轨道后缀的基准列, 它是三轨中样本量最大、覆盖度最完整的一支 (ctx/ss 轨依赖对应轨道的词频/相似度列存在, 存在优雅降级)。

## VAR: subst_adopt_kw_p50_allv_ctx

【变体差分】
本列对应文本轨 ctx (标题 + 目标银行实体窗口截取文本, 而非全文), 与基准列的唯一系统差异是词频分子与相似度分子均切换为该轨道的同轨变体: 相似度分子为 `policy_cosine_sim_allv_ctx` (在 ctx 文本上用同一枚全语料静态锚点计算的余弦相似度); 词频分子优先取 `fintech_distinct_keywords_ctx` (若该同轨词频列存在于对齐数据中), 若不存在则优雅回退复用 full 轨词频列 `fintech_distinct_keywords` 并在日志中披露 ("词频列无同轨变体 [track-agnostic], 复用 full")——这是因为关键词去重计数在实现上属于对某些轨道而言的 track-agnostic 元数据, 不总是每条轨道都独立重算, 与情感三轨 (LLM/词典/BERT) 逐轨独立扫描的口径不同, 写手/使用者在解读 ctx 轨与 full 轨差异幅度时应留意这一潜在的词频侧共享。
年度分位阈值口径 (P50, 年度截面重新计算) 与"仅双双非缺失方可分类, 否则三指示同 NaN"的掩码规则与基准列完全一致, 分母同为该 bank-year 内已测量 (ctx 轨词频/相似度双非缺失) 且经 verified 域过滤的文章数。ctx 轨聚焦于银行实体周边窗口的局部语境, 相对 full 轨剔除了与目标银行、金融科技均无直接关联的大段无关正文, 理论上能降低"长文章因整体词频基数大而被稀释判断"的噪声, 是构念测量的稳健性检验轨, 而非替代基准列的"更优"版本——三轨遵循"互为稳健性、不分主次"的既定口径, 结论应以三轨结果一致或方向一致作为支撑, 不应仅依赖单一轨道。
需注意 ctx 轨的样本宇宙是 full 轨留篇集合的子集 (2026-06-29 起留篇门控收紧为 full-only: 是否构成"一篇银行金科报道"仅由 `llm_verified_full` 判定, ctx/ss 轨在此留篇集合基础上才计算各自的象限指示), 因此本列覆盖的 bank-year 观测数原则上不多于基准列, 且当某 bank-year 的 ctx 轨词频或相似度列本身缺失 (旧 schema 或该轨完全未产出) 时, 运行时日志会记录"跳过 Track"并使该 bank-year 在本列上留空/NaN, 而非静默填零。

## VAR: subst_adopt_kw_p50_allv_ss

【变体差分】
本列对应文本轨 ss (标题 + 目标银行与金融科技关键词严格同句共现窗口截取文本), 与 ctx 轨镜像但窗口更严格: 相似度分子为 `policy_cosine_sim_allv_ss` (同一枚全语料静态锚点在 ss 文本上的余弦相似度), 词频分子优先取 `fintech_distinct_keywords_ss` (若同轨词频列存在), 缺失时同样优雅回退复用 full 轨词频列并披露日志, 与 ctx 轨的降级机制完全对称。
ss 轨的回退语义镜像 ctx 轨的既定口径: 当某篇文章不存在银行与金融科技词在同一句内共现时, 该篇的 `content_ss` 在 stage 14 物化阶段即回退为全文 body (`ss_is_fallback=True`, 与 ctx 共享 `n_articles` 分母的既定契约), 因此本列在 ss 文本上计算得到的词频/相似度, 对相当比例的文章而言实际上是在退化为 full 文本上算出的; 若上游 fintech 关键词自动机 (`FINTECH_AC`) 为 None (词典缺失等极端场景), 则 `*_is_fallback` 会全体为 True, 本列此时近似退化为 full 轨的重复度量, 属已知的优雅降级路径而非缺陷。
分位阈值 (P50, 年度截面) 与掩码规则同家族其余两列: 仅词频与相似度双非缺失方参与分类, 分母为该 bank-year 内已测量且经 verified 域 (full-only 门控) 过滤的 ss 轨文章数。作为三轨中窗口最严格、语境最纯净但也最容易触发回退的一支, ss 轨的信息含量在"银行-金融科技强共现"样本充分的年份最具区分度, 在共现稀疏的 bank-year 则更依赖回退机制而使其行为趋近 full 轨；解读时应结合 `ss_is_fallback` 相关诊断列, 并将本列与 full/ctx 两列的结果并列汇报, 而非单独作为定论依据, 遵循三轨"各自 just-identified 并排、互为稳健性、禁止混入同一 over-identified 方程"的既定铁律。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C. (2026). "Glossy Green" Banks: The Disconnect Between Environmental Disclosures and Lending Activities. Management Science, advance online publication. https://doi.org/10.1287/mnsc.2024.07420
Athanasopoulou, A., Marti, E., Risi, D., & Schlindwein, E. (2025). How Companies Restrain Means–Ends Decoupling: A Comparative Case Study of CSR Implementation. Journal of Management Studies, 62(1), 214-245. https://doi.org/10.1111/joms.13043
Huang, J., & Ma, L. (2024). Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation. Finance Research Letters, 63, 105265. https://doi.org/10.1016/j.frl.2024.105265
Zhang, Z., Hou, Y., Li, Z., & Li, M. (2024). From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure. Finance Research Letters, 63, 105401. https://doi.org/10.1016/j.frl.2024.105401
<!-- rendered-citations:end -->
