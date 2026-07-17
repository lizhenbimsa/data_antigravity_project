---
family_id: F332
columns:
- hidden_adopt_int_p75_allv
- hidden_adopt_int_p75_allv_ctx
- hidden_adopt_int_p75_allv_ss
unit: 无量纲指示比例 (bank-year 层面 [0,1] 区间的已测量篇均值; 逐篇底层为 0/1/NaN 指示)
formula: 'bank-year 层面 mean(hidden_t), 其中逐篇 hidden_t = 1{article_sim_t >= year_p75(article_sim) AND fintech_intensity_t < year_p75(fintech_intensity)}（即高相似度且低强度），仅在 sim/freq 双双非缺失 (measured) 的文章上取值, 否则为 NaN 并被 groupby(mean) 自动跳过分母'
producer: pipeline\panel\runner.py::_classify_policy_quadrants ; pipeline\panel\runner.py::_filter_to_verified_universe ; pipeline\panel\export.py (HEURISTIC_LABELS 映射)
upstream: [article_sim_mean, fintech_intensity_mean, docid, target_bank, year]
citations:
- doi: "10.1002/smj.821"
  type: journal
  authors: "Adner, R., & Kapoor, R."
  year: 2010
  title: "Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations"
  venue: "Strategic Management Journal"
  vol: "31"
  issue: "3"
  pages_or_artno: "306-333"
- doi: "10.1007/s10994-021-05946-3"
  type: journal
  authors: "Hüllermeier, E., & Waegeman, W."
  year: 2021
  title: "Aleatoric and epistemic uncertainty in machine learning: An introduction to concepts and methods"
  venue: "Machine Learning"
  vol: "110"
  issue: "3"
  pages_or_artno: "457-506"
- doi: "10.1016/j.econmod.2023.106445"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, F., & Zhao, Y."
  year: 2023
  title: "Bank fintech, liquidity creation, and risk-taking: Evidence from China"
  venue: "Economic Modelling"
  vol: "127"
  pages_or_artno: "106445"
- doi: "10.1016/j.iref.2021.03.009"
  type: journal
  authors: "Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J."
  year: 2021
  title: "Does fintech innovation improve bank efficiency? Evidence from China's banking industry"
  venue: "International Review of Economics & Finance"
  vol: "74"
  pages_or_artno: "468-483"
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
本家族刻画银行金融科技"隐性/低调采纳" (hidden adoption) 的强度轨 (Track B, int) 四象限分类之一, 在 bank-year 面板层面输出象限落位的年内占比。四象限框架把每篇报道同时投影到两个连续测度: 政策-文本余弦相似度 (`article_sim_mean`, 源自 stage 15/16 article_policy_alignment 的语义相似度, 对齐 Distel 等 2026 的政策文本相似框架) 与金融科技提及强度 (`fintech_intensity_mean`, stage 15 fintech_intensity 的连续词频/密度型测度)。按年度分别取两者的 75 分位阈值 (P75), 逐篇按"高/低相似度 × 高/低强度"落入四象限之一: token (高强度、低相似度, 即高调提及但语义空洞的"标签化"采纳)、hidden (低强度、高相似度, 即语义上与金融科技政策高度贴合但提及频次不显著的"低调/隐性"采纳)、subst (高强度、高相似度, 高调且语义贴合的"实质性"采纳)、以及未落入前述任一高位组合的基准组 (两者皆低)。hidden_adopt_int_p75_allv 度量的正是 hidden 象限: 银行报道文本在语义层面已经与金融科技政策议题高度趋同, 但报道中金融科技相关措辞的出现密度并不突出——这类文章更接近"业务实质已转向金融科技、但对外传播刻意低调或尚未形成高频话语标签"的采纳模式, 与高调宣传型 (token) 及言行合一型 (subst) 形成互斥对照。该构念呼应技术采纳与组织传播研究中"实质性 vs. 象征性"(substantive vs. symbolic) 采纳区分的传统 (可追溯 Westphal 等对公司治理实践"解耦" decoupling 的经典观察), 在金融科技语境下用于甄别银行是否存在"做而不说"的隐性数字化转型信号。

【方法学与计算】
底层 producer 为 `pipeline/panel/runner.py::_classify_policy_quadrants`, 输入为 bank-year 聚合前的文章级对齐表 `df_align` (含 `article_sim_mean` 与 `fintech_intensity_mean` 两连续列)。计算分两步: 第一步年度分位阈值——对每一 `year` 分组分别取 `article_sim_mean`/`fintech_intensity_mean` 的 P75 分位数 (`groupby('year').transform(quantile)`), 阈值随年度浮动而非全样本固定分位, 使象限划分对跨年报道基调/媒体覆盖率漂移保持相对稳健。第二步逐篇分类——仅对 sim 与 freq 双双非缺失 (`measured = sim.notna() & freq.notna()`) 的文章赋 0/1 指示, `hidden = (~high_freq & high_sim)`; 未测量的文章指示值设为 NaN 而非静默 0, 因此在后续 groupby('mean') 聚合到 bank-year 时会被自动跳过, 分母仅为该年内实际完成语义/强度双重测量的文章数, 不含因 stage 15 三条优雅早退路径 (无嵌入模型/无 policy 语料/API 失败) 导致测量缺失的文章——这一处理直接对应 runner.py 内注明的 fix(omni-g-runner-03/g-runner-11, 2026-06-11) 修复, 避免把测量失败误判为"低相似度"从而人为抬高 token 象限占比、压低 hidden 象限占比。在 `_classify_policy_quadrants` 之前, `df_align` 已无条件经过 `_filter_to_verified_universe` 的 semi-join 收敛: 该函数把输入域从 stage 15 规则预筛候选集收敛到 stage 21 LLM 语义精筛后判定为真阳性的 LLM-verified 集合 (与 stage 24 herd_decay 输出按 `docid`/`target_bank` 键内连接), 从根本上避免整个四象限族 (含本列) 与政策对齐均值、金融科技强度均值等下游测度共享一个不一致的聚合域而制造虚假的 bank-year "幽灵行"——但这一收敛对 vintage 主轨与 `_allv` 孪生轨完全等同生效, 并非 `allv` 后缀特有的语义。真正与 `allv` 后缀绑定的是另一件独立的工程决策: `pipeline/filtering/policy_alignment.py::all_vintage_companion_enabled` (2026-06-21 默认开启) 控制的"全年份锚点稳健孪生"——`article_sim_mean` 主轨用逐年度 vintage-aware 政策锚点 (仅纳入截至该年已发布的政策文本) 计算 `policy_cosine_sim`, 而 `_allv` (all-vintage) 孪生轨则用全语料 (所有年份, 含未来政策文本) 拼接的静态锚点重算同一套 `policy_cosine_sim_allv`, 二者共用完全一致的下游嵌入/池化/余弦/四象限构造方法, 仅锚点选取窗口不同。`hidden_adopt_int_p75_allv` 即在 `_anchor_variants` 循环 (runner.py L2024 起) 的 `_allv` 分支下, 以 `article_sim_mean_allv` 替换 `article_sim_mean` 作为相似度输入重新执行同一象限分类, 用于检验 hidden 象限归类是否对"政策锚点是否含未来信息"这一构造选择敏感。⚠ `_allv` 含未来政策文本, 仅作 anchor-robustness 对照, 绝不替换 vintage 主轨, 两者应并排报告、禁混进同一 over-identified 检验。

【文献定位】
象限式采纳分类的构念传统上溯至组织理论对"实质性响应 vs. 象征性遵从"的区分。这里借用 Adner 与 Kapoor (2010) 关于技术互补性/结构性相互依赖影响企业绩效的框架作一类比性参照: 该文原本讨论的是创新生态系统内互补资产结构是否对齐对绩效的影响, 并非直接针对文本分类方法论, 但其"结构维度与强度维度可以相互独立、不必收敛为单一连续量表"的分析取向, 支持本族把 hidden/token/subst 处理为并列象限而非单一线性量表两端的建模选择, 使用时应明确这是借用式的方法论类比而非该文献的直接结论。政策文本相似度测度中"缺失 vs. 低值"的严格区分处理, 亦借鉴 Hüllermeier 与 Waegeman (2021) 在机器学习文献中对 aleatoric (随机/数据层面) 与 epistemic (认知/模型层面) 不确定性来源的经典区分——该文献本身聚焦机器学习不确定性量化方法论综述, 并非专门讨论文本测度缺失值处理, 本族仅借用其"缺失≠已测但取值偏低"的概念区分逻辑, 落地为"未测量"(aleatoric 式缺失, 赋 NaN) 与"低值"(epistemic 式已测量但落入低分位) 的严格区分处理——即缺失值一律 NaN、绝不用零填充冒充"低相似度"测量结果, 这一处理准则贯穿本项目 `runner.py` 全部四象限族与情感缺失族。中国银行业金融科技语境下的文本情感/披露测度传统另见 Fang 等 (2023, Economic Modelling) 对银行金融科技与风险承担的文本化度量、以及 Lee 等 (2021, International Review of Economics & Finance) 对金融科技创新与银行效率关系的实证框架, 二者均以银行报道/披露文本的强度化测度为自变量构造起点, 与本族"强度轨 (int)"的方法论定位一致。 政策文本相似度这一测度族的近期方法学进展, 可参 Chen、Wen、Deng、Chen 与 Ma (2026): 该文以政府文件文本为基础构造政策扩散强度的文本驱动测度, 与本族 sim 维所依托的 policy_cosine_sim 及其 `_allv` 孪生同属「用政策文本相似度/强度刻画政策对齐程度」的方法族, 为该测度路径提供 2026 年的方法学存在性锚点。迁移边界须明确: 该文测量的是政策文件彼此之间的扩散强度 (政府—政府层级), 本项目则是新闻报道文本对政策锚点的余弦相似度 (媒体—政策层级); 该文不做二值象限分类, 不设年度分位阈值, 亦无 vintage 逐年滚动锚点与 `_allv` 全年份静态锚点的对照设计, 故仅可作测度族层面的方法学参照, 不构成对本族象限判据或 anchor-robustness 孪生设计的直接背书。
## VAR: hidden_adopt_int_p75_allv

【变体差分】
本列为家族 canonical/无轨道后缀变体, 底层文本轨道为 full (标题+正文全文), 对应文章级 `fintech_intensity_mean` 在全文文本上计算得到, 而相似度输入 `article_sim_mean_allv` 则来自 `all_vintage_companion_enabled` (2026-06-21 默认开启) 控制的全年份静态锚点孪生轨——与用逐年度 vintage-aware 锚点 (仅纳入截至该年已发布政策文本) 计算的主轨 `article_sim_mean` 相对, `_allv` 锚点改用全语料 (所有年份, 含未来政策文本) 拼接的静态锚点重算同一套余弦, 下游嵌入/池化/四象限构造方法与主轨完全一致, 仅锚点选取窗口不同, 是 anchor-robustness 对照而非 LLM 验证域收敛的标记 (LLM-verified 域收敛由 `_filter_to_verified_universe` 在两个锚点分支之前统一施加, 对 vintage 主轨与 `_allv` 孪生轨同等生效, 与 `allv` 后缀无关)。⚠ `_allv` 含未来政策文本, 仅作稳健性对照, 绝不替换 vintage 主轨 (无 `_allv` 后缀的家族 `hidden_adopt_int_p75` 同名主轨列), 二者应并排报告、禁混进同一 over-identified 检验。按 CLAUDE.md 三轨铁律, full/ctx/ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定——本列与 `_ctx`/`_ss` 两个同族变体应作为并列稳健性检验对照报告, 而非视为主/辅关系。留篇门控采用 full-only 口径 (2026-06-29 起): 是否计入"一篇有效银行金科报道"由 `llm_verified_full == True` 判定, ctx/ss 两轨的行宇宙是该 full 留篇集的子集, 因此本列 (full 轨) 的已测量篇均分母天然等于该 bank-year 的完整留篇集合, 不存在因轨道降级而缩小的分母问题。本列与 `hidden_adopt_kw_p75` (Track A, 关键词命中计数版) 构成方法学对照: kw 轨用离散关键词命中频次代替连续强度测度 `fintech_intensity_mean` 作为 x 轴, int 轨 (本列所属) 则用连续强度分数, 两者对同一"高调 vs 低调"象限划分提供不同粒度的稳健性互证, 同样应并排报告而非相互替代。此外本列还与同一强度轨内的另外两个百分位阈值变体 `hidden_adopt_int_p25`/`hidden_adopt_int_p50` 构成阈值梯子: P75 属较严格的高分位判据 (要求相似度落入年度最高四分之一区间才判定为"高相似"), 相较 P50/P25 更保守, 三者在解读上同属并列稳健性检验而非取代关系, 阈值越高, hidden 象限内文章的政策语义贴合度证据越强但样本占比越小, 呈现出典型的严格度—覆盖率权衡, 报告时建议同时展示不同分位口径下的结果以说明结论对阈值选择的敏感性。本列输出值域为 [0,1] 的 bank-year 层面占比 (已测量文章中落入 hidden 象限的比例), 而非文章计数; 当某 bank-year 内当年所有报道均未通过 sim/freq 双重测量 (例如 stage 15 因缺少嵌入模型或政策语料而全年早退) 时, 该 bank-year 的本列取值为 NaN 而非 0, 与全项目"无可测量样本即缺失、绝不用零冒充"的一致性契约对齐。

## VAR: hidden_adopt_int_p75_allv_ctx

【变体差分】
本列文本轨道为 ctx (标题+目标银行实体窗口), 底层 `article_sim_mean`/`fintech_intensity_mean` 在 stage 14 物化的 `content_ctx` (标题+实体窗口文本, 无同名独立轨即为窗口截断正文而非全文) 上重新独立计算, 而非对 full 轨结果做任何变换或截断——ctx 轨是围绕目标银行实体窗口的独立测度重算, 用于检验政策相似度/强度信号是否集中在与银行主体直接相关的语境窗口内, 从而排除全文中与银行主体无关的政策类段落对 hidden 象限归类的稀释或污染。行宇宙口径: 由于留篇门控已切换为 full-only, ctx 轨的行宇宙是 full 留篇集的子集 (conditional-on-full), 本列在计算 bank-year 均值时的分母仍为该年内已测量 (sim/freq 双双非缺失) 的 ctx 轨文章数, 与 full 轨分母独立, 二者不应直接相除或合并解读。ctx 轨若遇 `content_ctx_is_fallback` 标记为真的文章 (即无法定位有效实体窗口而回退为全文), 该文章在 ctx 轨上的相似度/强度计算实质退化为全文口径, 但该回退标记不影响本象限指示列本身的 0/1/NaN 赋值逻辑, 仅影响文本输入的信息密度。本列与 `hidden_adopt_int_p75_allv`(full 轨) 及 `hidden_adopt_int_p75_allv_ss`(ss 轨) 三者各自 just-identified 并排, 互为稳健性检验、不分主次, 报告时应同时列出三轨结果而非挑选单轨作为唯一依据, 亦不得将三轨系数混入同一 over-identified 工具变量设定共同估计。

## VAR: hidden_adopt_int_p75_allv_ss

【变体差分】
本列文本轨道为 ss (标题+银行∧金融科技同句共现窗口, 句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句), 是三轨中窗口最窄、语境最精炼的一支: 仅取银行主体与金融科技词汇在同一句 (或相邻半径内) 共现的文本片段计算 `article_sim_mean`/`fintech_intensity_mean`, 从而把"隐性采纳"象限的判定收窄到"银行与金融科技话题被作者放在同一叙述单元内讨论"的最强共现证据上——若某篇报道整体语义上贴合金融科技政策 (drives full/ctx 轨落入 hidden), 但银行主体与金融科技词汇从未在同句内直接共现, 则该文章在 ss 轨上更可能触发回退语义: 按 CLAUDE.md 铁律, ss 轨回退镜像 ctx 轨——当某篇文章不存在银行∧金融科技同句共现时, `content_ss` 退化为全文 body 且 `ss_is_fallback=True` (与 full 轨共享 `n_articles` 分母), 本象限指示列在该回退情形下仍按退化后的全文文本重新计算 sim/freq 并正常参与 0/1/NaN 分类, 不会因回退而被强制置为缺失。ss 轨与 full/ctx 两轨同属并列稳健性设计, 三者行宇宙均以 full-only 留篇门控为上界子集, 各自年度 P75 阈值、各自已测量分母独立核算, 解读时须明确标注所引用的具体轨道后缀, 禁止跨轨道加总或在同一识别设定内联合使用三轨系数。

<!-- rendered-citations:begin -->
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
Hüllermeier, E., & Waegeman, W. (2021). Aleatoric and epistemic uncertainty in machine learning: An introduction to concepts and methods. Machine Learning, 110(3), 457-506. https://doi.org/10.1007/s10994-021-05946-3
Fang, Y., Wang, Q., Wang, F., & Zhao, Y. (2023). Bank fintech, liquidity creation, and risk-taking: Evidence from China. Economic Modelling, 127, 106445. https://doi.org/10.1016/j.econmod.2023.106445
Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J. (2021). Does fintech innovation improve bank efficiency? Evidence from China's banking industry. International Review of Economics & Finance, 74, 468-483. https://doi.org/10.1016/j.iref.2021.03.009
Chen, J., Wen, J., Deng, Y., Chen, M., & Ma, F. (2026). Measuring policy diffusion intensity: A text-driven analysis of government documents. Information Processing & Management, 63(2), 104383. https://doi.org/10.1016/j.ipm.2025.104383
<!-- rendered-citations:end -->
