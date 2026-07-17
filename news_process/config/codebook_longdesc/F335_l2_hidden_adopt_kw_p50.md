---
family_id: F335
columns:
- hidden_adopt_kw_p50
- hidden_adopt_kw_p50_ctx
- hidden_adopt_kw_p50_ss
unit: 银行-年占比 (0-1 区间比例, 分母=当年已测量篇数)
formula: 'per-article 指示 _is_hidden = 1{freq_col < year_quantile(freq_col, p=0.50)} AND 1{sim_col >= year_quantile(sim_col, p=0.50)}, 其中 freq_col=fintech_distinct_keywords(kw 轨), sim_col=policy_cosine_sim(full 轨); bank-year 面板列 = groupby(target_bank, year) 对 _is_hidden 取 mean (NaN 跳过, 分母=sim/freq 双双非缺测的篇数)'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (步骤7h 网络族循环内联) ; 面板标签见 pipeline\panel\export.py
upstream:
- fintech_distinct_keywords (stage 12 news_fintech, Aho-Corasick 去重关键词计数)
- policy_cosine_sim (stage 16 article_policy_alignment, 文章-政策文本嵌入余弦相似度)
citations:
- doi: "10.1017/S0022109023000662"
  type: journal
  authors: "Kwan, A., Lin, C., Pursiainen, V., & Tai, M."
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: "Journal of Financial and Quantitative Analysis"
  vol: "59"
  issue: "6"
  pages_or_artno: "2618-2646"
- doi: "10.1073/pnas.2203150119"
  type: journal
  authors: "Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al."
  year: 2022
  title: "Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty"
  venue: "Proceedings of the National Academy of Sciences"
  vol: "119"
  issue: "44"
  pages_or_artno: "e2203150119"
- doi: "10.1111/ecin.12992"
  type: journal
  authors: "Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., et al."
  year: 2021
  title: "The influence of hidden researcher decisions in applied microeconomics"
  venue: "Economic Inquiry"
  vol: "59"
  issue: "3"
  pages_or_artno: "944-960"
- doi: "10.1016/j.frl.2026.109668"
  type: "journal"
  authors: "Chen, M., Zhang, Z., & Liu, Y."
  year: 2026
  title: "Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China"
  venue: "Finance Research Letters"
  vol: "95"
  pages_or_artno: "109668"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是银行金融科技新闻报道里的一种特定错位模式——"言行不一"的反面, 即"闷声干大事": 一篇报道里金融科技关键词提及很少 (词频低), 但报道内容与官方金融科技政策文本的语义相似度却很高 (政策对齐高)。这与常见的"蹭热点/洗科技"式报道 (关键词堆砌但内容空洞、与政策脱节) 恰好相反, 故命名为 Hidden Adoption (隐性采纳)。构念来自 runner.py 步骤7h 网络族循环中的"四象限政策对齐"分类器 `_classify_policy_quadrants`, 与同一四象限体系下的 Token Adoption (词频高但对齐低, 洗科技) 和 Substantive Adoption (词频高且对齐高, 言行一致) 互为镜像/互补测度, 三者加上 Irrelevant (词频低且对齐低) 象限共同穷尽样本空间。四象限的设计思路直接对应本项目在源码注释里给出的白话比喻: 纵轴是"关键词多不多", 横轴是"跟政策像不像", 每篇报道被放进四个格子之一, 再按 (银行, 年) 汇总占比。这一分类逻辑呼应了创新与技术采纳文献里对"仪式性/表征性采纳"与"实质性采纳"的区分传统 (锦上添花式的话语层面追随 vs. 真实的行为/资源投入层面追随), 具体到金融科技语境, Hidden Adoption 象限捕捉的是那些不刻意使用"金融科技""数字化转型"等热词、却在业务实质上贴近官方政策导向的报道——可能对应银行低调推进但未大肆宣传的金融科技布局, 也可能是媒体报道口径本身偏朴素但内容扎实。
本家族仅含 kw 词频轨 (Track A) 在 P50 (中位数) 分位阈值下的 Hidden 象限占比及其 full/ctx/ss 三个文本轨道孪生列; 家族命名中的 "kw" 明确区分于并行存在的 int 词频轨 (Track B, 使用 TF-IDF×SIF 加权的 `fintech_intensity_score` 而非去重关键词计数), 两条词频轨互为稳健性, 不应混同; "p50" 明确区分于并行存在的 P25/P75 稳健性分位阈值变体, 三个分位数同样互为稳健性并排, 不分主次。

【方法学与计算】
分类器逐篇作业, 分两步: 第一步确定当年 (year) 分位数阈值——词频列与相似度列各自按年份分组取 0.50 分位数 (`groupby('year').transform(lambda x: x.quantile(0.5))`), 即阈值是年度内生的 (每年单独算中位数, 而非跨全部年份池化一个全局阈值), 这样可以吸收词频/相似度水平本身随年份的漂移 (例如政策文本库逐年扩充导致相似度整体抬升)。第二步逐篇比较: 若该篇词频 < 当年词频中位数 且 该篇相似度 >= 当年相似度中位数, 记为 Hidden=1, 否则记为 Hidden=0 (与此并行还同时算出 Token/Subst 两个互斥指示, 但本家族只暴露 Hidden)。缺测处理是本测度的一处关键设计: 只有当 sim 列与 freq 列在该篇文章上同时非缺测 (notna) 时才参与分类, 任一方缺测则该篇的三个象限指示全部记 NaN——这是 2026-06-11 的一处修复 (fix omni-g-runner-03/g-runner-11), 修复前的旧实现把 `NaN >= 阈值` 静默判为 False, 会把 stage 15/16 因优雅早退而产出全 NaN 的 `policy_cosine_sim` 错误地当作"低相似度"处理, 导致大量高词频文章被误判入 Token 象限; 修复后未测量文章不再污染任何象限, 而是在 (银行, 年) 聚合阶段被 `groupby().mean()` 自动跳过, 即面板占比列的分母是该银行当年"已测量篇数" (sim 与 freq 都非缺测的文章数), 而非该银行当年全部报道篇数。若某银行某年全部报道的 sim 或 freq 都缺测, 则该 bank-year 的占比直接输出 NaN (真实"未测量"语义, 而非人为填 0)——这一点在 2026 年 v6/F3 修复中被专门强调: token_adopt/hidden_adopt/subst_adopt/article_sim_*/fintech_intensity_mean 这类"率/均值/相似度"型指标绝不做 `fillna(0.0)`, 强填零会在双向固定效应回归里污染系数估计 (参照 Allison 2001 关于面板数据缺失值处理的经典告诫)。
词频侧 (kw 轨的分子来源) 用的是 stage 12 `fintech_distinct_keywords`: Aho-Corasick 自动机在文章文本里扫描金融科技关键词库后得到的去重关键词命中数, 是一个"词汇丰富度"式计数, 而非简单的词频总和; 相似度侧用的是 stage 16 `policy_cosine_sim`: 文章文本嵌入向量与官方金融科技政策文本嵌入向量之间的余弦相似度, 度量的是语义层面的政策贴合程度而非字面关键词重合。两者在概念上正交——一个测"说了多少金融科技相关的话", 一个测"说的话在多大程度上贴近官方政策精神"——四象限交叉正是利用这种正交性来区分言辞层面与实质层面的采纳信号。

【文献定位】
这一构念设计与创新扩散/技术采纳研究长期关注的"表征性合规 vs. 实质性合规"张力一脉相承: 组织可能在话语/符号层面追随某项创新或制度压力而未必伴随实质行为改变, 反之亦可能存在低调但真实的采纳行为未被话语充分反映, 这正是当代文本挖掘方法论文献日益关注的"隐藏的不确定性"问题的一个具体化——即便测量流程 (关键词计数、语义相似度) 表面客观, 分类阈值 (本处为中位数分割) 与轨道 (kw vs int, full/ctx/ss) 的选择仍是研究者自由度的来源, Breznau et al. (2022, *PNAS*) 的多团队重复分析研究表明, 即使面对同一数据和假设, 不同研究者因隐藏的分析选择差异会得出系统性不同结论, 这也是本项目坚持将 P25/P50/P75、kw/int、full/ctx/ss 等多条并排轨道全部产出为独立稳健性列、而非折叠为单一"最优"口径的方法论依据。类似地, Huntington-Klein et al. (2021, *Economic Inquiry*) 系统记录了应用微观经济学研究中"隐藏的研究者决策" (如变量构造的分箱/阈值选择) 对复现结果的实质性影响, 直接呼应本家族刻意保留分位阈值梯度 (25/50/75) 作为并排稳健性检验而非单点估计的设计初衷。在金融科技/银行业数字化采纳的具体应用场景, Kwan, Lin, Pursiainen & Tai (2024, *Journal of Financial and Quantitative Analysis*) 对银行数字能力的压力测试研究提供了"话语层面的数字化宣称"与"实质数字能力储备"可能脱钩的实证背景, 支持了本项目区分 Token/Hidden/Substantive 三种采纳模式的构念效度动机。

三轨 (full/ctx/ss) 铁律: 本家族的 full/ctx/ss 三个文本轨道各自独立 just-identified, 互为稳健性检验、不分主次, 三轨结果不应被合并进同一 over-identified 的 Hansen J 过度识别检验框架。full 轨使用文章全文与全文政策相似度; ctx 轨使用银行实体上下文窗口文本及其对应相似度 `policy_cosine_sim_ctx`; ss 轨使用银行∧金科同句共现窗口文本及其对应相似度 `policy_cosine_sim_ss` (ss 回退语义镜像 ctx: 当某篇文章不存在银行∧金科同句共现时, 该篇的 ss 轨文本回退为全文, 对应的 `_is_fallback` 指示置 True, 与全文轨共享分母口径)。需特别注意: kw 轨的词频列 `fintech_distinct_keywords` 是 track-agnostic 的元数据 (AC 关键词扫描本身不区分 full/ctx/ss 窗口), 故当构造 ctx/ss 轨的 Hidden 占比时, 相似度侧换轨 (`policy_cosine_sim_ctx`/`_ss`) 而词频侧优先寻找同轨变体、若不存在则退化复用 full 轨的 `fintech_distinct_keywords` 列 (源码注释称"复用 full 列并披露")——这意味着本家族的 ctx/ss 两列在词频维度上实际上与 full 轨共享同一分子来源, 差异完全来自相似度分母侧的文本窗口切换, 这是解读三列差异时必须明确的口径细节, 而非笼统认为"三轨各自独立测量"。此外本测度与留篇门控 (2026-06-29 起 stage 21 是否计为"一篇银行金科报道" 仅看 full 轨 `llm_verified_full`) 相关但不同源——四象限分类使用的是 stage 15/16 的 `policy_cosine_sim`/词频列而非 stage 21 情感 LLM 投票结果, 门控口径不直接约束本家族的行宇宙, 但下游面板聚合仍继承 `_filter_to_verified_universe` 的 verified 域 semi-join。 更贴近 Hidden 象限本身的近期证据来自 Chen、Zhang 与 Liu (2026): 该文在中国语境下专门刻画企业创新披露中的"多行动少言说 (more action-less talk)"沉默型态, 即实质投入不低而文本声量偏低的一格, 并检验其与商业信用融资的关系, 为"低声量高实质"作为一种独立可测的采纳型态提供了 2026 年的存在性证据, 呼应本家族把"词频低于当年中位数 且 政策相似度不低于当年中位数"单列为 Hidden、而非归入采纳缺失的构念判断。迁移边界须明确: 该文的观察层级为上市公司-年, 其"沉默"由企业年报披露文本与专利/研发投入之间的落差界定, 属言—行的外部对照; 本家族两维则均取自新闻文本 (AC 去重关键词计数 vs 政策余弦相似度), 判据为双分位交叉, 且该文既无 full/ctx/ss 三轨设计, 亦无 P25/P50/P75 阈值梯子, 故只能锚定 Hidden 构念的可测性, 不能作为本家族分位判据与聚合口径的出处。
## VAR: hidden_adopt_kw_p50

【变体差分】
本列是家族的 canonical (基准) 变体: 词频轨=kw (`fintech_distinct_keywords`, AC 去重关键词计数), 分位阈值=P50 (年度内生中位数分割), 文本轨=full (无 `_ctx`/`_ss` 后缀, 使用文章全文与全文政策相似度 `policy_cosine_sim`)。取值为该银行当年被判入 Hidden 象限 (当年词频中位数以下 且 当年相似度中位数以上) 的报道占该银行当年"已测量篇数" (sim 与 kw 词频均非缺测) 的比例, 值域 [0, 1], 未测量年份为 NaN 而非 0。该列与并排的 `hidden_adopt_int_p50` (int 词频轨稳健性)、`hidden_adopt_kw_p25`/`hidden_adopt_kw_p75` (分位阈值稳健性) 互为稳健性检验, 各自 just-identified, 不应混入同一过度识别框架; 也与同一四象限体系下互斥的 `token_adopt_kw_p50`/`subst_adopt_kw_p50` 构成完整的构念区分——三者在同一 (银行, 年, 阈值) 组合下按定义互斥 (逐篇只能落入一个象限), 但三个占比列并非严格互补加总为 1 (因为还存在第四象限 Irrelevant 未单独产出面板列, 且分母仅限已测量篇数)。该列在 `papers/_common/derivative_replication.py::benefit_society` 配置块中被指定为 `MECHANISM_HIDDEN` 占位符, 与 `MECHANISM_TOKEN`(token_adopt_kw_p50)、`MECHANISM_SUBST`(subst_adopt_kw_p50) 三者并列构成该 paper 复现包中的机制检验组, 用于检验"隐性金融科技采纳"作为经营效益态度 (`benefit_mean_full` 等) 与实质业务变化之间可能存在的中介/机制渠道——即银行低调采纳金融科技 (少提及关键词但内容贴近政策) 的报道占比是否与经营效益的正面态度存在系统性关联, 区别于单纯"话语层面追风"(Token 象限) 的关联模式。由于四象限阈值按年度内生计算, 该列的解读须结合样本期内政策文本库与关键词库本身的演化——若某年政策文本大量扩充导致相似度整体抬升, 当年的相似度中位数阈值也会相应上移, 使得"高于当年中位数"这一判定标准并非跨年份绝对可比, 这是使用年度内生分位阈值 (而非全样本池化阈值) 的方法学取舍: 优点是自动吸收年度水平漂移, 代价是跨年份占比差异不能被简单解读为"绝对隐性采纳程度"的变化, 更适合用于同年横截面银行间比较或作为面板固定效应回归中的相对排序信号。

## VAR: hidden_adopt_kw_p50_ctx

【变体差分】
与 canonical 列的唯一差异在相似度分母侧: 本列使用 `policy_cosine_sim_ctx` (银行实体上下文窗口文本与政策文本的余弦相似度) 而非全文相似度 `policy_cosine_sim`; 分位阈值仍按年度内生方式在 ctx 轨相似度自身分布上重新计算 P50 (与 full 轨阈值不共用同一数值, 各轨阈值独立按各自年度分布求出)。词频侧因 kw 轨词频列 `fintech_distinct_keywords` 为 track-agnostic 元数据、不存在 `_ctx` 变体, 故本列的分子词频端仍复用与 canonical 列相同的全文关键词计数, 并非词频与相似度同步换轨——这是解读本列时最容易误判的一点: 本列度量的是"全文词频筛选 + 上下文窗口语义对齐筛选"的交叉, 而非纯粹的"ctx 轨内部"四象限。该列与 canonical (full) 及 `_ss` 列互为稳健性检验, 三轨各自 just-identified 并排, 禁止混入同一 over-identified Hansen J 框架; 当上游 stage 16 未产出 `policy_cosine_sim_ctx` 列时 (旧 schema), 本列在生成时被优雅跳过 (对应面板输出为全 NaN 或缺列, 视 schema 版本而定)。本列的经济含义可理解为"银行实体周边语境是否贴近政策精神, 而不看该篇报道整体金融科技话语密度是否稀薄"——由于 ctx 窗口聚焦在银行实体出现附近的文本片段, 相似度计算天然带有更强的实体针对性 (排除了与该银行不直接相关的政策式套话段落对相似度的稀释或拉高), 因此本列相对 full 轨列更适合用作"该银行本身是否被聚焦于政策相关语境"的稳健性检验, 而不是对整篇报道主题的泛化判断。与 full 轨列相比, 本列在同一 (银行, 年) 上的取值可能系统性偏离, 因为 ctx 窗口相似度的年度分布形态 (均值、方差) 通常与全文相似度不同, 年度中位数阈值也随之不同, 故不能简单假设两列在同一银行同一年应当接近或应存在单调对应关系。

## VAR: hidden_adopt_kw_p50_ss

【变体差分】
与 canonical 列的差异同样限于相似度分母侧: 本列使用 `policy_cosine_sim_ss` (银行实体与金融科技词汇同句共现窗口文本与政策文本的余弦相似度), 是三轨中窗口最窄、语境最紧凑的一支, 年度 P50 阈值同样在 ss 轨相似度自身分布上独立计算。ss 轨遵循镜像 ctx 的回退语义: 当某篇报道不存在银行与金科关键词的同句共现时, 该篇的 ss 文本回退为全文, 对应 `policy_cosine_sim_ss` 的 `_is_fallback` 指示为 True, 分母口径与全文轨共享; 词频侧同样因 kw 轨 track-agnostic 特性而复用全文的 `fintech_distinct_keywords` 计数, 不存在独立的 ss 词频变体。该列与 full/ctx 两列互为稳健性检验, 三者各自 just-identified 并排, 不分主次, 禁止混入同一 over-identified Hansen J 框架; 当上游 `policy_cosine_sim_ss` 列缺失时 (旧 schema 或 ss 轨未上线), 本列生成同样优雅跳过。由于 ss 窗口要求银行与金融科技关键词严格同句共现, 满足该条件的报道天然是"实质谈及" (而非仅在标题或不相关段落各自提及) 银行与金融科技的子样本, 因此在此子样本上仍呈现"关键词计数低但语义相似度高"的 Hidden 象限模式, 其证据强度理论上强于 full 轨 (因为已经排除了银行与金融科技话题完全不相关、仅偶然同篇出现的噪声报道); 但代价是回退机制导致相当比例的报道 (无同句共现) 落回全文文本, 使得实际参与"严格同句"判定的有效样本量小于 full/ctx 两轨, 在小样本银行-年格子上 Hidden 占比的抽样噪声会更大, 解读时应结合该银行当年的 `n_articles`(留篇门控下的已验证报道量) 综合判断估计稳定性, 而非孤立看占比数值本身。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. Proceedings of the National Academy of Sciences, 119(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., et al. (2021). The influence of hidden researcher decisions in applied microeconomics. Economic Inquiry, 59(3), 944-960. https://doi.org/10.1111/ecin.12992
Chen, M., Zhang, Z., & Liu, Y. (2026). Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China. Finance Research Letters, 95, 109668. https://doi.org/10.1016/j.frl.2026.109668
<!-- rendered-citations:end -->
