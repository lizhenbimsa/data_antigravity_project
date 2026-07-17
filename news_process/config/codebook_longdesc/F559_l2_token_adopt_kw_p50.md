---
family_id: F559
columns:
- token_adopt_kw_p50
- token_adopt_kw_p50_ctx
- token_adopt_kw_p50_ss
unit: 比例 (银行-年内被判定为"象征性采纳"文章占已测量文章数之比, 取值域 [0,1], 未测量年份为 NaN 而非 0)
formula: 逐篇二值指示 = 1{词频(fintech_distinct_keywords) >= 年度P50分位 且 policy_cosine_sim < 年度P50分位}, 仅对 sim 与 freq 均 notna 的文章判定 (否则该文章指示=NaN); token_adopt_kw_p50 = 该指示在 (target_bank, year) 分组内的 mean (NaN 自动跳过, 分母=该银行-年已测量篇数)
producer: pipeline\panel\runner.py::_classify_policy_quadrants + 步骤7h 四象限聚合循环 (L1978-2100 附近); 面板列标签见 pipeline\panel\export.py::STATA_LABELS; 下游消费见 papers\_common\derivative_replication.py::MECHANISM_TOKEN (benefit_society 稳健性机制变量)
upstream:
- 16_article_policy_alignment (policy_cosine_sim / policy_cosine_sim_ctx / policy_cosine_sim_ss, Distel et al. 2026 政策对齐余弦相似度)
- 12_news_fintech (fintech_distinct_keywords, AC 自动机去重关键词计数)
- 24_herd_decay_processor (下游面板汇入前的行宇宙裁剪)
citations:
- doi: "10.1017/S0022109023000662"
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: Journal of Financial and Quantitative Analysis
  vol: "59"
  issue: "6"
  pages_or_artno: "2618-2646"
- doi: "10.1080/09296171003643098"
  type: journal
  authors: Covington, M. A., & McFall, J. D.
  year: 2010
  title: "Cutting the Gordian knot: The moving-average type-token ratio (MATTR)"
  venue: Journal of Quantitative Linguistics
  vol: "17"
  issue: "2"
  pages_or_artno: "94-100"
- doi: "10.1016/j.rmal.2024.100168"
  type: journal
  authors: Bestgen, Y.
  year: 2025
  title: "Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons"
  venue: Research Methods in Applied Linguistics
  vol: "4"
  issue: "1"
  pages_or_artno: "100168"
- doi: "10.1016/j.frl.2024.105401"
  type: "journal"
  authors: "Zhang, Z., Hou, Y., Li, Z., & Li, M."
  year: 2024
  title: "From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105401"
- doi: "10.1016/j.pacfin.2024.102493"
  type: "journal"
  authors: "Liu, Y., Wang, J., Wen, F., & Wu, C."
  year: 2024
  title: "Corporate responses to systemic risk: Talk and action"
  venue: "Pacific-Basin Finance Journal"
  vol: "87"
  pages_or_artno: "102493"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是一家银行在某一年度的新闻报道中, 有多大比例落入"象征性金融科技采纳"(token / symbolic fintech adoption) 这一象限。它源自组织理论对"言行是否一致"的经典区分: 企业可能大量使用金融科技相关词汇进行传播 (言), 却未必真正在业务与政策取向上贴近既定的金融科技/普惠金融政策方向 (行)。为了把这种言行错位量化到文章层面并汇总到银行-年面板, 流水线在步骤 7h (`pipeline/panel/runner.py::_classify_policy_quadrants`) 构造了一个逐篇二维分类: 纵轴是"词频轨"(某篇报道里金融科技关键词出现的丰富程度), 横轴是"对齐轨"(该篇报道文本与官方金融科技/数字普惠金融政策文本之间的余弦相似度, 产自 stage 16 `article_policy_alignment`, 方法学谱系可追溯到 Hassan et al. 传统的文本-政策对齐范式, 在本项目 codebook 中标注为 Distel et al. 2026)。两轴各自按年度分位数二值化后, 组合出四个格子: 高词频×高对齐 = 实质性采纳 (substantive, `subst_adopt_*`), 高词频×低对齐 = 象征性采纳 (token, 即本家族), 低词频×高对齐 = 隐性采纳 (hidden, `hidden_adopt_*`), 低词频×低对齐 = 不相关。本家族 `token_adopt_kw_p50` 及其 `_ctx`/`_ss` 孪生列取的是"词频≥中位数且对齐<中位数"这一格, 白话讲就是"新闻里金融科技词堆得多、但内容跟政策文件对不上号"——一种可能反映"蹭热点/洗科技"(fintech-washing) 而非真实业务转型的报道模式。

【方法学与计算】
计算分两层。第一层是逐篇二值指示: 对每篇文章, 先在同一年度内 (`groupby('year').transform`) 分别对相似度列 `policy_cosine_sim*` 与词频列 `fintech_distinct_keywords*` 取分位数阈值 (P=25/50/75 三档, 本家族取 P50 中位数, 与项目内 10 余处"中位数分割"惯例一致), 再判定该篇是否满足"词频≥阈值 且 相似度<阈值"。这一指示的定义域被显式限制在 sim 与 freq 均非缺失的文章上 (`measured = sim.notna() & freq.notna()`); 若两者任一缺失 (例如 stage 15/16 因数据不足优雅早退写出全 NaN 相似度), 该篇的指示值为 NaN 而不是被误判为 False——这是 2026-06-11 的一次修复 (`omni-g-runner-03`/`g-runner-11`), 旧实现会把"未测量"静默计成"低对齐", 系统性地把测量失败的文章错误灌入 Token 象限。第二层是银行-年聚合: 用 `groupby(['target_bank','year']).agg(mean)` 对逐篇指示取均值, pandas 的 mean 对 NaN 天然跳过, 因此该占比的分母是该银行-年"已测量"的文章数, 而不是全部报道数; 若某银行-年所有文章均未测量, 面板输出为 NaN——这与项目 v6/F3 修复的"无数据=未测量, 不得强填 0"契约保持一致 (强填 0 会在双向固定效应回归中系统性压低系数, 参见 Allison 2001 的缺失值处理讨论)。
本家族三列共享同一构造逻辑, 差别仅在于对齐相似度取自哪条文本轨: full/ctx/ss。这是本项目"三轨"架构的标准应用——full/ctx/ss 三条文本轨在方法论上各自独立成立、互为稳健性检验、不分主次, 严禁把三轨系数混进同一个 over-identified 的 Hansen J 过度识别检验; 它们应当各自 just-identified 并排呈现, 让读者看到结论是否对文本窗口选择稳健。需要特别指出的是: 本家族的"词频轨"(kw, 即 `fintech_distinct_keywords`) 是一个 track-agnostic 的元数据列 (AC 自动机在全文范围内去重计数, 本身并无 ctx/ss 变体), 因此在构造 `_ctx`/`_ss` 孪生列时, 词频侧仍复用 full 轨的 `fintech_distinct_keywords`, 只有相似度侧切换为对应轨的 `policy_cosine_sim_ctx`/`policy_cosine_sim_ss`——这是刻意的非对称设计并在源码注释中明确披露, 不是遗漏。此外, kw 是"Track A"路径 (与之并列的 Track B 是 `int`, 即 `fintech_intensity_score` TF-IDF×SIF 加权强度, 对应家族 `token_adopt_int_p50`), 两条词频轨之间同样互为稳健性、不分主次。

【文献定位】
本家族所刻画的"言行不一致的技术采纳/传播"现象, 在银行数字化转型与金融科技压力测试的实证文献中有稳固的方法学根基。Kwan, Lin, Pursiainen & Tai (2024, *Journal of Financial and Quantitative Analysis*) 以 COVID-19 冲击为准自然实验, 检验银行"数字能力"的异质性及其对经营韧性的实质影响, 揭示了银行数字化的对外呈现 (报道/披露) 与其真实运营能力之间可能存在的落差, 为本家族"报道热度高但政策对齐低"的象限划分提供了实证参照系: 若某银行大量新闻报道堆砌金融科技词汇却与官方政策文本疏离, 这与该文献所强调的"披露/传播 vs 真实能力"张力属于同一构念族。词频度量本身的方法学 (关键词计数/词汇多样性的稳健测量) 呼应 Covington & McFall (2010, *Journal of Quantitative Linguistics*) 提出的 moving-average type-token ratio 及其后续评估 (Bestgen 2025), 二者共同支撑本项目对"词频丰富度"这一维度的合理性——即高频出现某类关键词本身并不等价于内容的实质相关性, 需要与独立的语义对齐测度联合判定才能区分符号性与实质性两种传播模式。分位数二值化 (P25/P50/P75) 的稳健性检验设计, 亦与项目内其余梯子式测度 (词典消融、政治词权重、阈值梯子) 遵循同一原则: 中位数为机制检验基准, 上下分位数互为并排的稳健性检验, 不作为对主结果的加权修正。 在此基础上, 近年两支实证工作可为本家族的构念边界提供进一步参照。Zhang、Hou、Li 与 Li (2024) 研究 ESG 评级如何推动企业绿色创新结构由象征性向实质性迁移, 把"象征性占比"作为可随外部监督变化的结构性比例 (而非绝对水平) 来处理, 这与本家族把象征性采纳表述为"已测量文章内的占比"(分母限定为相似度与词频均非缺失的报道) 而非计数水平的设计取向同源; 但迁移边界须诚实交代: 该文的比例基于专利结构数据, 主体为中国 A 股非金融企业, 驱动因素为 ESG 评级, 且全文未使用任何文本判定器, 因此它仅锚定"象征占比"这一构念形态, 并不为本家族"词频 × 政策对齐"的判定口径本身提供证据。Liu、Wang、Wen 与 Wu (2024) 则将企业对系统性风险的回应拆为 talk (文本表述强度) 与 action (实际举措) 两条可分别测量的维度并检验二者关系, 与本桶用"词频高低 × 政策对齐高低"划分 token/hidden 象限属同一"言—行两维并置"的测度族; 其边界在于原文为企业层面的系统性风险回应而非银行金融科技采纳, talk 取自披露文本、action 取自财务与公司行为代理, 而本家族两维同源于新闻文本 (词频 vs 政策余弦), 且不含年度分位阈值梯子与 bank-year 篇均占比聚合, 故该文只支撑"两维并置"的构造思路, 不能替本家族具体的阈值化与聚合口径背书。
## VAR: token_adopt_kw_p50

【变体差分】
本列是家族的 full 轨 canonical 变体, 即分类判定所用的两个输入列均取自全文文本对应的度量: 相似度用 `policy_cosine_sim` (stage 16 在文章全文/标题拼接文本上计算的政策对齐余弦相似度), 词频用 `fintech_distinct_keywords` (AC 自动机在全文范围内识别的去重金融科技关键词计数, 本身即为 track-agnostic 度量, 无需区分轨道)。分位阈值取 P50 (年度中位数), 是 Track A (kw 词频) × P50 × full 轨的机制检验基准组合, 论文正文回归通常以此列作为"象征性采纳"倾向的主要机制变量 (参见 `papers/_common/derivative_replication.py::MECHANISM_TOKEN` 在 benefit_society 论文模块中的稳健性机制检验用途)。行宇宙口径遵循项目 2026-06-29 起确立的留篇门控铁律: 是否构成"一篇银行-金科报道"的判定以 `llm_verified_full == True` 为准, full 轨即为该门控原生对应的测度轨, ctx/ss 是在 full 留篇集合子集上的条件测度。取值范围 [0,1], 分母为该银行-年 sim 与 freq 同时非缺失的文章数; 若某银行-年因 stage 15/16 优雅早退导致相似度全 NaN, 该银行-年本列输出为 NaN 而非 0, 需在下游回归中显式处理缺失而非当作零值处理。
本列与家族内另外两个 P25/P75 分位阈值列 (`token_adopt_kw_p25`/`token_adopt_kw_p75`, 属独立家族但共享同一构造函数) 互为稳健性并排, P50 是研究者选定的主机制检验分位 (与项目内十余处中位数分割惯例一致), P25/P75 用于检验"象征性采纳"占比是否对分位阈值的具体取值敏感; 三者应各自 just-identified 汇报, 不应合并进同一超定 (over-identified) 检验框架。与之并列的 Track B (`token_adopt_int_p50`, 词频侧改用 TF-IDF×SIF 加权的 `fintech_intensity_score`) 是另一条互为稳健性的词频度量路径, 用以排除本列结论仅是"关键词计数"这一特定操作化选择的产物。此外, 若面板中存在 `_allv` 后缀孪生列 (如 `token_adopt_kw_p50_allv`), 那是相似度阈值改用全语料静态锚点 (`policy_cosine_sim_allv`) 而非逐年 vintage 锚点的稳健性变体, 与本列 (vintage 主轨) 同样互为并排, 不构成本列的替代或修正。

## VAR: token_adopt_kw_p50_ctx

【变体差分】
本列与 canonical 列的唯一差别在相似度输入: 用 `policy_cosine_sim_ctx` (在标题+实体窗口拼接文本 `content_ctx` 上计算的政策对齐相似度) 替换 `policy_cosine_sim`; 词频侧仍沿用 track-agnostic 的 `fintech_distinct_keywords` (full 轨全文关键词计数), 这是源码显式披露的非对称设计, 不是漏做 ctx 词频。P50 阈值同样按年度在 ctx 相似度列上独立重新计算 (与 full 轨阈值数值不同), 因此本列与 canonical 列并非简单的行级子集关系, 而是基于不同相似度分布重新分档后的独立分类结果。按本项目三轨铁律, ctx 与 full/ss 三者互为稳健性检验、各自 just-identified 并排比较, 不应混入同一个 over-identified 的 Hansen J 检验框架, 也不构成对 full 轨系数的加权修正; 若 `policy_cosine_sim_ctx` 在某次面板重建中缺失 (旧 schema 或 stage 16 未产出该轨), 该 ctx 孪生列在聚合循环中会被优雅跳过, 面板中不出现该列而非静默填零。
ctx 轨的构念定位是: 用一个比全文更聚焦、比同句共现更宽松的中间窗口 (标题+实体窗口) 去检验"象征性采纳"占比是否稳健于文本纳入范围的选择。若某银行大量报道在全文层面词频高、政策对齐低 (即 full 轨判为 token), 但把文本收窄到银行实体附近窗口后对齐度回升 (ctx 轨判为 substantive 或 hidden), 则提示 full 轨的低对齐可能是被文章中与该银行无关的段落 (例如泛泛的行业综述) 稀释所致, 而非该银行自身报道确实"言行不一"; 反之若三轨结论一致, 则象征性采纳的判定更为稳健。这一比较逻辑与本项目"双轨/三轨互为稳健性、不以相关性高低决定取舍"的一贯原则相符——两轨即便高度相关也仍应分别进入各自的回归设定, 不得合并为一个跨轨的联合矩条件。

## VAR: token_adopt_kw_p50_ss

【变体差分】
本列的相似度输入进一步收窄为 `policy_cosine_sim_ss`, 即在"银行实体与金融科技词汇同句共现"窗口文本 `content_ss` 上计算的政策对齐相似度, 是三轨中判定条件最严格的一支。其文本回退语义严格镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, `content_ss` 退化为全文 body 且 `ss_is_fallback=True`, 此时该篇纳入的仍是与 full 轨相近的宽口径文本而非空值, 分母 `n_articles` 与 ctx 轨共享同一套定义。词频侧与 ctx 列一样复用 track-agnostic 的 `fintech_distinct_keywords` (full 轨计数), 只有相似度侧切轨; P50 阈值按年度在 ss 相似度分布上独立计算。ss 轨判定条件最贴近"银行与金融科技在同一句话里被提及"的强共现场景, 更适合作为 full/ctx 结果的加严稳健性检验, 用以排查"象征性采纳"占比是否被宽松的实体窗口口径 (ctx) 或全文口径 (full) 夸大或压缩; 三轨结论方向一致则增强象征性传播现象的可信度, 方向不一致则提示结论对文本窗口选择敏感, 需在稳健性讨论中并列披露而非取其一舍其二。若 `policy_cosine_sim_ss` 缺失 (ss 轨未上线的旧 schema), 该列同样被聚合循环优雅跳过。
需要提醒的是, ss 轨的"回退到全文"并非稀有事件的极端边角情形, 而是同句共现判据本身较为苛刻时的常态路径: 只有当扫描文本中银行实体与金融科技词汇落在同一句 (或按 `config/filtering.yaml::context_window.ss_sentence_radius` 设定的窗口半径, 默认1句) 内才触发严格同句提取, 否则回退为全文, 因此 ss 轨相似度分布在回退比例较高的语料中会与 full 轨呈现一定的重叠, 这是设计使然而非缺陷。读者在解读 `token_adopt_kw_p50_ss` 与 `token_adopt_kw_p50` 的差异时, 应结合该银行-年的 `ss_is_fallback` 比例一并考察: 回退比例高的银行-年, 两列数值天然更接近; 回退比例低 (即真实存在大量同句共现文章) 的银行-年, 两列差异才更能反映"象征性传播"判定对文本窗口收紧程度的敏感性。三判据/三轨之间保持并排、互不加权合并, 是本项目稳健性叙事的统一惯例, 也适用于本列与其余两列的比较。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type-token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94-100. https://doi.org/10.1080/09296171003643098
Bestgen, Y. (2025). Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons. Research Methods in Applied Linguistics, 4(1), 100168. https://doi.org/10.1016/j.rmal.2024.100168
Zhang, Z., Hou, Y., Li, Z., & Li, M. (2024). From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure. Finance Research Letters, 63, 105401. https://doi.org/10.1016/j.frl.2024.105401
Liu, Y., Wang, J., Wen, F., & Wu, C. (2024). Corporate responses to systemic risk: Talk and action. Pacific-Basin Finance Journal, 87, 102493. https://doi.org/10.1016/j.pacfin.2024.102493
<!-- rendered-citations:end -->
