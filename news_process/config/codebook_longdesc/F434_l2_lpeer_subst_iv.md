---
family_id: F434
columns:
- lpeer_subst_iv_ctx
- lpeer_subst_iv_ctx_lag1
- lpeer_subst_iv_ss
- lpeer_subst_iv_ss_lag1
unit: 工具变量取值 (0-1 区间, 与被工具化的内生变量 sub_frac_sc / sub_frac_ss 同量纲, 银行-年层面比例)
formula: 银行 i 年份 t 的工具变量值 = 与 i 同类型 (bank_type, 即国有大行/股份行/城商行/农商行等分组) 的全部其余银行在该年份该文本轨道下的实质性占比份额 (sub_frac_sc 或 sub_frac_ss) 的留一 (leave-one-out) 均值, 即剔除银行 i 自身后对同组同侪取简单平均; _lag1 后缀列在同一构造上整体错后一年 (t-1 期同侪 LOO 均值对应 t 期观测)
producer: pipeline\panel\iv_extensions.py ; pipeline\panel\stata_export.py
upstream:
- sub_frac_sc
- sub_frac_ss
- bank_type
citations:
- doi: "10.1016/j.jbankfin.2024.107191"
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk
  venue: Journal of Banking & Finance
  vol: "164"
  pages_or_artno: "107191"
- doi: "10.1111/jofi.13412"
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: "Sustainability or greenwashing: Evidence from the asset market for industrial pollution"
  venue: The Journal of Finance
- doi: "10.1016/j.jfineco.2021.01.010"
  type: journal
  authors: Flammer, C.
  year: 2021
  title: Corporate green bonds
  venue: Journal of Financial Economics
- doi: "10.2307/2298123"
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
- doi: "10.1257/aer.20181047"
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
- doi: "10.1111/jofi.12094"
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: Do peer firms affect corporate financial policy?
  venue: The Journal of Finance
- doi: "10.2307/2393295"
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: "Substance and symbolism in CEOs' long-term incentive plans"
  venue: Administrative Science Quarterly
- doi: "10.1016/j.ribaf.2022.101873"
  title: "Peer effects in financial economics: A literature survey"
  authors: "Ali-Rind, A., Boubaker, S., & Jarjir, S. L."
  year: 2023
  venue: "Research in International Business and Finance"
  type: "journal"
new_dois:
- "10.1016/j.ribaf.2022.101873"
---

## CORE

【构念与来源】
本家族 F434 (family_key: l2_lpeer_subst_iv) 是 P3 (bank_fintech_substance, W&Z 1998 ASQ 实质-象征区分谱系) 论文识别策略中的同侪留一 (leave-one-out, LOO) 工具变量族, 由 pipeline\panel\iv_extensions.py 的 compute_iv_extensions 在 runner 步骤 8z 统一编排产出, 与 stata_export.py 中的 HEURISTIC_LABELS 字典配对生成 .dta 变量标签。四列均是内生解释变量 sub_frac_sc (ctx 轨"实质性创新占比") 与 sub_frac_ss (ss 轨同名占比) 的工具, 构造思路直接继承 Manski (1993) 反射问题 (reflection problem) 之后计量文献常用的"同类同侪均值"识别路径: 用与本银行处于同一 bank_type 分组 (国有大行/股份行/城商行/农商行等) 的其余全部银行在同一年份、同一文本轨道下的实质性占比均值, 作为本银行自身实质性占比的外生冲击代理, 逻辑上排除自身贡献 (leave-one-out) 以避免机械的自相关污染识别。该思路与 Leary & Roberts (2014) 在公司金融文献中广泛使用的"同行均值工具" (peer-firm mean instrument) 一脉相承: 同类型银行面对相近的监管环境、市场结构与技术采纳节奏, 因而其媒体报道中"实质性创新"话语占比存在共同的组内趋同压力, 这构成排他性约束的经验基础, 但该基础本身依赖组内共同冲击不直接作用于本银行融资成本等结果变量这一可反驳假设, 论文侧须辅以过度识别检验与叙事论证。
【方法学与计算】
构造分两步。第一步取分子构念: sub_frac_sc 是 ctx 轨 (标题+实体窗口文本) 下, 经三家 LLM 多数投票+关键词回退的 innovation_substantiveness 分类结果聚合到银行-年层面的"实质性"篇均占比 (verified 门控分母为该轨自身留篇集); sub_frac_ss 是 ss 轨 (标题+银行∧金科词同句±N窗) 下的镜像同名占比, 回退语义与 ctx 一致 (无同句共现则整篇作 fallback 计入全文 body, ss_is_fallback=True)。第二步在银行-年面板上, 对每个 (bank_type, year) 分组内的全部银行取该轨占比的算术均值, 再对每家银行 i 减去其自身贡献后重新平均, 得到留一均值, 即 lpeer_subst_iv_ctx / lpeer_subst_iv_ss; _lag1 两列在此基础上按面板整体错后一期, 用 t-1 期同侪 LOO 均值解释 t 期内生变量, 进一步削弱同期共同冲击对排他性的直接威胁, 也便于吸收年份固定效应后仍保留识别力。命名上四列均带 lpeer_ 紧凑前缀 (而非各论文既有的 leave_one_out_peer_ 全称), 是因为 ctx/ss 轨镜像扩列后若沿用长前缀会超出 Stata 变量名 32 字符上限产生截断歧义, lpeer_subst_iv_ss_lag1 (22 字符) 与 lpeer_subst_iv_ctx_lag1 (23 字符) 均在安全边界内, stata_export.py 的 HEURISTIC_LABELS 沿用同一命名前缀直接引名而不再另设映射表。
【文献定位】
本族工具变量的识别谱系上溯 Manski (1993) 对同侪效应识别中"反射问题"的经典刻画, 中游经 Leary & Roberts (2014) 在企业融资政策研究中系统化的同行均值工具实践, 亦与 Goldsmith-Pinkham, Sorkin & Swift (2020) 对 Bartik/shift-share 类工具识别假设的形式化讨论互为方法论参照 (本族与同家族并列的 bartik_subst_iv_* 工具是同一内生变量的另一识别策略, 二者构造机制不同、排他性依据不同, 详见后述与相邻测度的构念区分)。构念本身承接 Westphal & Zajac (1994, 1998) 开创、并经本项目 P3 论文延伸到中国银行业金科新闻语境的"实质性 vs 象征性"创新话语二分, sub_frac 的 LLM 分类口径与文本轨道设计参照 Bingler et al. (2024) 在气候信息披露"廉价言辞"(cheap talk) 识别中对实质性语言与言辞性语言的区分方法论, 以及 Duchin, Gao & Xu (2025) 对披露内容与实际行动脱钩现象的实证检验框架; Flammer (2021) 关于企业绿色债券认证与后续环境绩效关系的研究, 为"话语是否兑现为实质行动"这一构念提供了另一路径的外部效度参照。Ali-Rind, Boubaker & Jarjir (2023, Research in International Business and Finance) 系统综述金融经济学中同侪效应的识别策略, 包括留一同侪均值工具与反射问题应对方案, 为本家族以同类型银行留一同侪均值构造工具变量的做法提供最新方法论综述支撑。
四列均为 tier=standard, 不含 core 列, 因此本节不设识别策略定位与已知局限专节 (相关铁律陈述见各 VAR 节尾)。

## VAR: lpeer_subst_iv_ctx

【变体差分】
本列是四列中的当期 ctx 轨基准工具, 分子构念取自 sub_frac_sc, 即"标题+实体窗口"文本轨道 (三轨 full/ctx/ss 之一) 下经留篇门控计算的银行-年"实质性创新"话语占比。构造上对每个 (bank_type, year) 分组, 计算组内除银行 i 之外全部同类型银行该年份 ctx 轨 sub_frac_sc 的算术均值, 赋给银行 i 作为其自身 ctx 轨内生变量的工具, 即当期、无滞后的留一同侪均值。需要明确的是, ctx 轨是围绕目标银行实体附近窗口截取的文本裁剪, 与 full 轨 (标题+全文, 对应既有 leave_one_out_peer_subst_iv) 及 ss 轨 (标题+银行∧金科词同句窗口, 对应本家族的 lpeer_subst_iv_ss) 是同一篇文章的三种不同裁剪口径, 三者虽指向同一构念但因裁剪窗口不同而在数值上存在系统性差异, 不可互相替代或加总。按 CLAUDE.md 铁律与 iv_extensions.py 源码注释 (2026-06-13 四 agent 对抗终审落地) 明确规定: full/ctx/ss 三轨的留一同侪工具各自 just-identified、并排使用, 三者互为稳健性检验、不分主次, 严禁将任意两轨或三轨的工具混入同一个过度识别 (over-identified) 的 Hansen J 检验, 原因是三轨文本源自同一篇原始报道, 银行类型与年份层面的共同冲击会逐字污染各轨, 导致 J 统计量对真实排他性违反的检验功效趋近于零, 同时因三轨工具高度共线还会拖累一阶段 Kleibergen-Paap rk F 统计量的表现 (Parente & Santos Silva 2012 EL 对此类伪过度识别陷阱有系统讨论)。若研究者需要构造真正意义上的过度识别检验, 应采用跨族工具组合 (例如本列的留一同侪工具与同一内生变量的 Bartik 类工具 bartik_subst_iv_ctx 搭配), 而非在三条文本轨道之间做 J 检验。使用该列时应与被工具化的内生变量 sub_frac_sc 保持轨道口径一致, 不应用于工具化 sub_frac (full 轨) 或 sub_frac_ss (ss 轨)。

## VAR: lpeer_subst_iv_ctx_lag1

【变体差分】
本列是 lpeer_subst_iv_ctx 的滞后一期版本, 构造上先按 lpeer_subst_iv_ctx 相同逻辑在面板全体年份上算出留一同侪均值序列, 再对每家银行按其自身时间轴整体错后一年, 使得 t 期观测对应的是 t-1 期同类型同侪 (剔除自身) 在 ctx 轨下的实质性占比均值。滞后处理的经济含义是进一步弱化"同期同类型银行共同暴露于相同宏观或监管冲击"这一潜在排他性违反渠道: 若担心当期同侪均值与当期结果变量 (如融资成本) 之间存在未观测的共同驱动因素, 用上一期同侪信息作为工具可以在时间维度上拉开距离, 代价是识别效力可能因跨期传导衰减而下降, 也会因面板首期缺乏 t-1 观测而产生自然缺失 (早期试跑 T=2 开发集上首年度整列缺失属预期设计, 非缺陷)。与非滞后版本 lpeer_subst_iv_ctx 的关系是互为稳健性的并排设计而非替代关系: 论文侧回归可分别以当期与滞后同侪工具各自单独跑一阶段回归对照系数稳定性, 但同样不得将两者同时塞入同一模型做过度识别检验, 因为二者本质上是同一潜在冲击序列在时间维度上的相邻切片, 相关性机制上并不构成相互独立的排他性来源。本列所工具化的内生变量口径仍限定为 ctx 轨 sub_frac_sc (或其滞后), 与 full 轨、ss 轨的对应滞后工具 (leave_one_out_peer_subst_iv 的滞后版本、lpeer_subst_iv_ss_lag1) 同样构成三轨并排而非混用的关系, 适用同一条 Hansen J 铁律约束。

## VAR: lpeer_subst_iv_ss

【变体差分】
本列是当期 ss 轨的留一同侪工具, 内生变量对应 sub_frac_ss, 即"标题+目标银行与金科关键词同句 (±N 句窗, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认取半径 1) "文本轨道下的实质性创新占比。构造机制与 lpeer_subst_iv_ctx 完全平行: 对每个 (bank_type, year) 分组取除自身外全部同类型银行该年份 ss 轨 sub_frac_ss 的算术均值作为工具。ss 轨在构念上比 ctx 轨更严格, 要求银行实体与金科词汇在同一句内共现才计入非回退样本, 若某篇报道中银行与金科词从未同句出现, 则该篇按回退语义整体计入全文 body 参与统计且标记 ss_is_fallback=True, 这一回退口径镜像 ctx 轨的回退设计, 二者共享同一 n_articles 分母约定, 不存在因回退机制不同而产生的口径落差。ss 轨因窗口更窄, 单篇覆盖的判定样本天然少于 ctx/full 轨, 因而 lpeer_subst_iv_ss 在小样本分组 (如某年度某类型银行数量很少) 下方差可能更大, 使用时应结合分组银行数量做描述性核查。与前述 ctx 轨工具及既有 full 轨工具 leave_one_out_peer_subst_iv 三者同样适用「各自 just-identified 并排、互为稳健性不分主次、禁止混入同一 over-identified Hansen J」的铁律, 三者对应的内生变量分别是 sub_frac (full)、sub_frac_sc (ctx)、sub_frac_ss (ss), 工具与内生变量必须保持轨道口径的一一对应, 不允许用 ss 轨工具去解释 ctx 轨或 full 轨内生变量。

## VAR: lpeer_subst_iv_ss_lag1

【变体差分】
本列是 lpeer_subst_iv_ss 的滞后一期版本, 在 lpeer_subst_iv_ss 逐年留一同侪均值序列基础上, 按银行整体错后一年对齐到面板, 令 t 期观测取 t-1 期同类型同侪 (剔除自身) 在 ss 轨下的实质性占比均值。之所以在紧凑前缀设计下刻意压缩到 lpeer_subst_iv_ss_lag1 这一较短拼写 (22 个字符), 是因为若沿用论文既有 zone_leave1out_benefit_iv 一类的长前缀命名, 叠加 _ss_lag1 后缀极易超出 Stata 变量名 32 字符硬上限而被静默截断, 造成不同轨道列名冲突或歧义, iv_extensions.py 源码注释明确将这一命名收紧列为绕开截断风险的设计考量, stata_export.py 的 HEURISTIC_LABELS 才能对四列分别给出无歧义的独立标签而不必依赖额外映射表。本列与 lpeer_subst_iv_ss 之间同样是互为稳健性的当期/滞后并排关系, 与 lpeer_subst_iv_ctx_lag1、以及既有 full 轨滞后工具共同构成三轨滞后工具组, 三者各自 just-identified、互不替代、禁止混入同一过度识别检验; 若论文需要跨源的真过度识别设计, 应转向与 Bartik 类工具 (bartik_subst_iv_ss) 或分组结构不同的工具 (如按媒体来源 house-style 暴露构造的 outlet 类工具) 搭配, 而非在本族三轨内部或其滞后版本之间寻求过度识别。使用本列时同样须保持与 sub_frac_ss 滞后版本的轨道口径一致, 并在面板首期因缺乏 t-1 观测而产生的缺失应视为设计内预期, 不应作为数据质量问题处理。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Flammer, C. (2021). Corporate green bonds. Journal of Financial Economics. https://doi.org/10.1016/j.jfineco.2021.01.010
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies. https://doi.org/10.2307/2298123
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review. https://doi.org/10.1257/aer.20181047
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? The Journal of Finance. https://doi.org/10.1111/jofi.12094
Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. Administrative Science Quarterly. https://doi.org/10.2307/2393295
Ali-Rind, A., Boubaker, S., & Jarjir, S. L. (2023). Peer effects in financial economics: A literature survey. Research in International Business and Finance. https://doi.org/10.1016/j.ribaf.2022.101873
<!-- rendered-citations:end -->
