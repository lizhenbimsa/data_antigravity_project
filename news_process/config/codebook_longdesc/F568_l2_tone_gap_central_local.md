---
family_id: F568
columns:
- tone_gap_central_local_ctx
- tone_gap_central_local_full
- tone_gap_central_local_ss
unit: 语调缺口 (连续, 两组均值之差; 理论域约 [-2,2], 实践中绝大多数样本落在 [-1,1] 附近; bank-year 面板)
formula: 'tone_gap_central_local{track} = tone_central_media{track} - tone_local_media{track};
  其中 tone_central_media{track} = mean(llm_vote_score{track} | _is_central==1) 按 (target_bank, year) 分组,
  tone_local_media{track} = mean(llm_vote_score{track} | _is_central==0) 按 (target_bank, year) 分组;
  _is_central = 媒体(中文) ∈ CENTRAL (中央级媒体名单; 地方级 = 该名单外的补集, 非独立维护名单)。track ∈ {_full, _ctx, _ss}, 源列 llm_vote_score{track} 缺失时该轨整族优雅跳过。'
producer: pipeline\panel\attention_media.py::compute_media_heterogeneity_features (维度④, L1309-1332) ; pipeline\panel\export.py (dta 标签映射)
upstream:
- 21_tone_llms.parquet::llm_vote_score_full / llm_vote_score_ctx / llm_vote_score_ss
- config/media_classification.json (键 central_media, 中央级媒体名单; 地方级为其补集, 非独立名单)
citations:
- doi: "10.1093/rfs/hhx055"
  type: journal
  authors: "You, J., Zhang, B., & Zhang, L."
  year: 2018
  title: "Who Captures the Power of the Pen?"
  venue: "Review of Financial Studies"
  vol: "31"
  issue: "1"
  pages_or_artno: "43-96"
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China"
  venue: "International Review of Economics & Finance"
  vol: "91"
  pages_or_artno: "1150-1172"
- doi: "10.2308/TAR-2020-0104"
  type: journal
  authors: "Holzman, E. R., Miller, B. P., & Twedt, B. J."
  year: 2023
  title: "Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements"
  venue: "The Accounting Review"
  vol: "98"
  issue: "7"
  pages_or_artno: "315-345"
- doi: "10.1016/j.ememar.2024.101234"
  type: journal
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  title: "Does Official Media Sentiment Matter for the Stock Market? Evidence from China"
  venue: "Emerging Markets Review"
  vol: "64"
  pages_or_artno: "101234"
- doi: "10.1371/journal.pone.0315137"
  type: "journal"
  authors: "Ananyev, M., & Volkova, E."
  year: 2024
  title: "Media ownership and ideological slant: Evidence from Australian newspaper mergers"
  venue: "PLOS ONE"
  vol: "19"
  issue: "12"
  pages_or_artno: "e0315137"
- doi: "10.1287/orsc.2022.17237"
  type: "journal"
  authors: "Dewan, Y., Simons, T., & Wernicke, G."
  year: 2024
  title: "The Ideological Imperative: Corporate Social Responsibility and News Media Coverage of Firms"
  venue: "Organization Science"
  vol: "35"
  issue: "5"
  pages_or_artno: "1930-1955"
- doi: "10.1016/j.irfa.2023.102761"
  type: "journal"
  authors: "Isakin, M., & Pu, X."
  year: 2023
  title: "Dispersion in news sentiment and corporate bond returns"
  venue: "International Review of Financial Analysis"
  vol: "89"
  pages_or_artno: "102761"
new_dois: []
---

## CORE

【构念与来源】
tone_gap_central_local 族衡量同一银行同一年度内, 中央级媒体报道语调与地方级媒体报道语调之间的系统性缺口, 是 Stage 40 面板导出模块 `attention_media.py` 中"媒体异质性"五维分类体系 (财经 vs 综合 vs 其他 / 中央 vs 地方 / 官方 vs 非官方) 里第④维度的产物。行政层级二分基于媒体主管归属: `_is_central` 判据取 `媒体(中文)` 列是否落入 `config/media_classification.json::central_media` 名单 (人民日报、新华社、中央电视台等中央级党政机关或全国性权威媒体); 该判据只显式维护"中央级"这一个名单, 地方级 (省市级党报/都市报/地方广电) 并非另一份独立名单, 而是"不在中央级名单内"的补集 (`_is_central==0`), 二者在数据结构上是名单-补集关系而非两份对等维护的名单。构念动机来自媒体政治经济学文献对"层级捕获"(hierarchical capture) 的关注: 中央级媒体承担更强的政治宣传与舆论引导职能, 报道语调更可能受宏观维稳/政策基调影响而系统性偏离地方级媒体的市场化报道语调; 反之地方级媒体贴近属地企业利益关系, 可能因关联寻租或地方保护而呈现另一种偏差方向。该缺口列因此不预设符号方向, 是纯粹的描述性异质性诊断量, 供研究者检验"谁在为银行说好话/坏话"这一层级维度的媒体捕获假说, 并作为 P1 (bank_fintech_tone) 与衍生论文 (bank_media_disagreement, brokerage_network) 稳健性附录中媒体来源异质性分解的组成部分。

【方法学与计算】
计算发生在 bank-year 面板聚合层, 不在文章级留痕: 先以 `(target_bank, year)` 分组、按 `_is_central` 取子集分别求 `llm_vote_score{track}` 均值, 得到 `tone_central_media{track}` 与 `tone_local_media{track}` 两个中间列并各自 merge 回面板, 再逐行相减得到 `tone_gap_central_local{track} = tone_central_media{track} - tone_local_media{track}`。正值表示该银行当年中央级媒体报道语调更正面 (相对地方级); 负值反之。源列 `llm_vote_score{track}` 是 stage 21 三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票共识的连续打分版本, 与离散版 `llm_vote_tone{track}` 同源但保留了投票强度信息, 属于本项目情感 LLM 轨的下游二次聚合而非独立测度。三轨 (full/ctx/ss) 各自独立完成上述分组-求均值-相减流程, 任一轨源列在文章级数据中不存在时 (例如 ctx/ss 物化列缺失), 该轨整族 (`tone_central_media{track}`/`tone_local_media{track}`/`tone_gap_central_local{track}`) 直接跳过, 不借用其他轨的数值填补, 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J 设定。`_ss` 轨的回退语义镜像 `_ctx`: 当某篇文章不存在银行与金科词的同句共现时, 其 `content_ss` 退化为全文正文 (`ss_is_fallback=True`), 但该文章是否计入分组均值仍由 stage 21 的留篇门控决定 —— 留篇判定统一以 `llm_verified_full==True` 为准 (full-only 门控, 2026-06-29 起), ctx/ss 轨的样本行集合是 full 轨留篇集合的子集, 分组均值分母 (该银行-年-层级下的可用文章数) 随轨道而系统性缩小, 三轨数值不可直接比较绝对水平, 只可比较符号与相对结构。若某银行-年组合内某一层级 (中央或地方) 无任何报道, 对应 `tone_central_media{track}` 或 `tone_local_media{track}` 为缺失, 缺口列相应记为缺失 (NaN), 属预期的稀疏退化而非计算错误, 在 T=2 (2017-2018) 开发样本上尤为常见。

【文献定位】
媒体在公司治理与信息中介中的政治属性差异是媒体经济学与公司金融交叉领域的核心议题。You, Zhang & Zhang (2018, *Review of Financial Studies*) 的经典发现是官方媒体的负面报道并不能有效约束高管更替, 而市场化媒体的负面报道则具有显著的治理效应, 揭示了媒体所有制/政治关联对报道信息含量与市场反应传导路径的系统性调节作用, 是本项目维度⑤ (官方 vs 非官方) 的直接理论依据, 也为维度④ (中央 vs 地方) 提供了平行的层级捕获逻辑——中央级媒体在层级序列中往往与官方媒体高度重叠但并非同一构念, 二者是本项目正交设计的两个维度。Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 在中国银行业情境下直接考察媒体情感对存款稳定性与系统性风险的影响, 是本族最贴近的中国银行-媒体情感同域实证锚点, 其研究设计同样依赖银行-年层面的媒体语调分组聚合。Holzman, Miller & Twedt (2023, *The Accounting Review*) 揭示媒体情感在盈余公告发布窗口对市场反应具有约束效应, 为"媒体语调差异如何影响信息治理"提供跨市场证据, 支撑本族缺口测度作为媒体异质性诊断工具的一般性。此外, Xu, Hua & Zhang (2025, *Emerging Markets Review*) 在中国资本市场情境下直接检验"官方媒体"(official media) 情感是否对股票市场定价具有独立解释力, 其官方 vs 非官方媒体的行政属性二分设计与本族中央级 vs 地方级的层级二分在构念上高度贴近 (同属媒体行政隶属维度的异质性检验, 而非泛化到央行等货币当局自身沟通文本的情感构念), 为本项目将中央级媒体语调单独分离并与地方级比较的操作化取向提供了最直接的同构念实证参照。 晚近三条证据从不同侧面收紧了本族的成立前提。Ananyev 与 Volkova (2024) 利用 2016-2019 年三起澳大利亚报业并购, 以逾三千万篇报道的语言构建 slant 测度、以合成双重差分识别媒体所有权变更对报纸政治 slant 的因果影响, 为「按媒体归属/控制权分层、并预期分层之间的语调存在系统性缺口」这一前提提供了准实验层面的证据; 但其所有权维度是私人资本集中度, 而非中国的中央/地方行政层级隶属, slant 以政治意识形态量表度量, 与本族 LLM 投票的银行金科报道语调不是同一构念, 层级为报纸-时期亦无银行-年面板, 故只锚定分层-缺口这一设计前提。Dewan、Simons 与 Wernicke (2024) 实证考察企业 CSR 行为如何影响新闻媒体对该企业的报道及其报道倾向, 发现这一映射受媒体自身意识形态的调节, 支撑本族「媒体并非中性传声筒、来源属性会系统性移动报道倾向, 因而缺口的期望值不必为零」这一理论前提; 该文情境为美国媒体与美国企业, 观测的是报道量/倾向作为结果变量, 既不区分行政层级, 也不构造任何缺口型统计量, 因此只锚定前提而不锚定本族公式。Isakin 与 Pu (2023) 把同一发行主体同期多篇新闻之间的情感离散度作为独立可定价构念加以度量与检验 (美国公司债、债券-月层级、英文新闻数据库情感), 是 tone_gap 族「同一主体报道内部的语调不一致本身携带信息, 而非只有语调水平携带信息」这一一般前提的方法学近亲; 但原文的离散度是全部报道上的跨文章统计离散, 与本族先按来源层级划成互补两组、再取组均值之差 (between-group contrast) 并非同一统计量, 原文亦不做任何媒体来源属性分层, 且发表年为 2023, 不属 2024 年以来的前沿区间。上述三条与三轨口径正交: 本族 full/ctx/ss 三轨仍各自 just-identified 并排, 互为稳健性、不分主次, 不因新增锚点而改变禁混同一 over-identified Hansen J 的设定。
## VAR: tone_gap_central_local_ctx

【变体差分】
本列取 ctx (实体窗口) 轨: 分组均值所依赖的源列是 `llm_vote_score_ctx`, 即 stage 21 情感 LLM 在"标题+实体窗口"文本 (`content_ctx`, stage 14 `ctx_materializer` 物化) 上打分的多数投票共识度。与 `_full` 轨相比, ctx 轨聚焦银行/金科实体周边的局部语境, 剔除了全文中与目标银行无关的段落噪声, 因而在同一中央/地方层级分组内, ctx 轨的语调均值通常方差更小、对文章主题漂移更不敏感; 但其样本行集合仍受 full-only 留篇门控约束 (只统计 `llm_verified_full==True` 的文章), 且当某篇文章缺少可物化的实体窗口时按上游规则处理, 不与 `_full`/`_ss` 轨混同。ctx 轨与 full/ss 两轨各自 just-identified 并排, 是同一构念下的互为稳健性测量, 不设主次关系, 三轨数值差异应解释为文本抽取窗口不同带来的测量口径差异, 而非层级捕获效应本身的强弱变化。

由于 `_is_central` 判据完全独立于文本抽取轨道 (只依赖 `媒体(中文)` 列的名单归属, 不依赖任何轨道的正文内容), 三轨在"哪些文章属于中央级/地方级"的行政分类上是完全一致的, 差异只体现在分组均值计算时使用哪一份语调打分。这意味着 ctx 轨与 full 轨、ss 轨在样本行的层级归属上是对齐的, 唯一的自由度是同一批文章在不同文本窗口下被 LLM 打出的语调分数不同, 因此 ctx 轨与 full 轨之间的差值可以被解读为"聚焦实体窗口是否系统性改变了对某一层级媒体语调的判断", 而非层级构成本身的变化。使用者在解读该列时应注意, ctx 轨样本量小于 full 轨 (受制于实体窗口是否可物化), 在银行-年组合样本稀疏的开发环境 (T=2) 下, 某一层级 (尤其是样本天然更少的中央级) 缺行导致整列 NaN 的概率高于 full 轨, 属预期的稀疏退化而非计算错误, 生产语料 T=19 全量下该退化率将显著降低。

## VAR: tone_gap_central_local_full

【变体差分】
本列取 full (全文) 轨, 是本家族的 canonical 基准: 分组均值依赖的源列是 `llm_vote_score_full`, 即三家 LLM 在"标题+完整正文"文本上打分的多数投票共识度, 覆盖信息量最完整, 也是 P1 (bank_fintech_tone) 主处理变量 `llm_vote_tone_full` 所在轨道的直接映射对象, 留篇门控 (`llm_verified_full==True`) 本身就定义在这一轨上, 因此 full 轨的样本行集合是三轨中最完整的一支 (ctx/ss 均是其子集)。`export.py` 中该列的 dta 标签为 "Tone Gap: Central - Local (Full)", 与同族 `tone_gap_fin_other_full`/`tone_gap_comp_other_full`/`tone_gap_fin_comp_full` 并列构成媒体异质性缺口列的 Full 轨道子集。使用者若只需单一口径的中央-地方媒体语调缺口, 应以本列为首选参照, 但仍需在稳健性表中报告 ctx/ss 两轨作为互为稳健性并排检验, 不应将三轨强行并入同一过度识别设定。

full 轨的另一层特殊性在于其样本行集合本身定义了留篇门控的边界: `llm_verified_full==True` 是判断"某篇报道是否真的构成一篇有效的银行金科报道"的唯一判据, 因此 full 轨在中央/地方两个子分组下的可用文章数在三轨中最多, 中央级样本天然稀疏 (相对地方级媒体报道数量) 导致的缺失概率在 full 轨下最低。研究者在跨银行、跨年份比较该缺口列的绝对水平时, 应同时报告分组样本量 (中央级篇数与地方级篇数), 避免把"某银行中央级报道仅 1-2 篇导致均值不稳定"误读为真实的层级捕获效应差异; 该注意事项对三轨均适用, 但在样本量最大的 full 轨下相对最不敏感。

## VAR: tone_gap_central_local_ss

【变体差分】
本列取 ss (银行∧金科同句) 轨: 分组均值依赖的源列是 `llm_vote_score_ss`, 该轨的底层文本 `content_ss` 要求目标银行与金科关键词在同一句内共现 (半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1); 若某篇文章不满足该同句共现条件, 其 `content_ss` 按镜像 ctx 的回退语义退化为全文正文, 并置 `ss_is_fallback=True`, 但该文章能否进入本列的分组均值计算仍取决于是否通过 full-only 留篇门控, 与是否触发 ss 回退无关。ss 轨聚焦银行与金科业务在文本层面最紧密关联的语境切片, 是三轨中窗口最窄、对"该文章是否真的在谈论银行金科业务"这一构念最挑剔的一支, 因而样本量通常小于 ctx 轨, 在 T=2 稀疏开发样本上尤易出现某银行-年组合下中央或地方一侧缺行导致整列 NaN 的情形。ss 轨与 full/ctx 两轨同样各自 just-identified 并排, 互为稳健性、不分主次, 三者一律禁止混入同一 over-identified Hansen J 设定。

从构念严格性角度看, ss 轨可视为三轨中对"该文章是否真的在同时谈论目标银行与金融科技业务"这一前提要求最苛刻的一支: full 轨只要求文章整体与银行相关 (经 stage 13 共现硬过滤), ctx 轨要求实体窗口可物化, 而 ss 轨要求银行与金科关键词在同一句内共现, 三者构成一条构念严格性递增的谱系。因此 ss 轨的中央/地方语调缺口更适合被解读为"在银行与金科业务紧密交织的叙事片段中, 中央级与地方级媒体语调是否存在系统性差异", 而非泛化到该银行的全部报道语境。由于 ss 轨样本行是 full 轨留篇集合与同句共现条件的双重交集, 其分组样本量在三轨中通常最小, 使用者在解读该列的极端值或符号翻转时应格外谨慎核对分组样本量, 避免将小样本噪声误读为层级捕获强度的真实变化; 该列与 ctx/full 两轨的差异应始终作为规格稳健性并排报告, 不设主次、不建立跨轨加权合成指标。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen? Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Xu, Z., Hua, X., & Zhang, T. (2025). Does Official Media Sentiment Matter for the Stock Market? Evidence from China. Emerging Markets Review, 64, 101234. https://doi.org/10.1016/j.ememar.2024.101234
Ananyev, M., & Volkova, E. (2024). Media ownership and ideological slant: Evidence from Australian newspaper mergers. PLOS ONE, 19(12), e0315137. https://doi.org/10.1371/journal.pone.0315137
Dewan, Y., Simons, T., & Wernicke, G. (2024). The Ideological Imperative: Corporate Social Responsibility and News Media Coverage of Firms. Organization Science, 35(5), 1930-1955. https://doi.org/10.1287/orsc.2022.17237
Isakin, M., & Pu, X. (2023). Dispersion in news sentiment and corporate bond returns. International Review of Financial Analysis, 89, 102761. https://doi.org/10.1016/j.irfa.2023.102761
<!-- rendered-citations:end -->
