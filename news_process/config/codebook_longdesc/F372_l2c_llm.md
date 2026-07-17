---
family_id: F372
columns:
- llm_peer_n_effective
- llm_peer_queried
unit: 计数 (llm_peer_n_effective=同行家数; llm_peer_queried=0/1 指示)
formula: 'llm_peer_n_effective = |{p ∈ LLM_Peer_Set(bank) : p ∈ 面板样本框 ∧ p 在 t-1 期经文章级 leave-out (剔除与焦点银行 exclude_bank 共提的文章后) 仍有效可取 tone}|; llm_peer_queried = 1{该 bank-year (year=t, 同年口径) 的 LLM 同行识别调用发起且响应可解析}, 与识别出的同行集合是否为空无关, 且与决定同行 tone IV/n_effective 的 lag_year=t-1 查询是两个独立事件'
producer: pipeline\panel\llm_peer_iv.py
upstream: []
citations:
- {doi: "10.1007/s11142-025-09892-6", type: journal, authors: "Cao, Y., Chen, L., Tucker, J. W., & Wan, C.", year: 2025, title: "Can Generative AI Help Identify Peer Firms?", venue: "Review of Accounting Studies", vol: "30", issue: "4", pages_or_artno: "3344-3386"}
- {doi: "10.1086/688176", type: journal, authors: "Hoberg, G., & Phillips, G.", year: 2016, title: "Text-Based Network Industries and Endogenous Product Differentiation", venue: "Journal of Political Economy", vol: "124", issue: "5", pages_or_artno: "1423-1465"}
- {doi: "10.2307/2298123", type: journal, authors: "Manski, C. F.", year: 1993, title: "Identification of Endogenous Social Effects: The Reflection Problem", venue: "The Review of Economic Studies", vol: "60", issue: "3", pages_or_artno: "531-542"}
- {doi: "10.1111/jofi.12094", type: journal, authors: "Leary, M. T., & Roberts, M. R.", year: 2014, title: "Do Peer Firms Affect Corporate Financial Policy?", venue: "The Journal of Finance", vol: "69", issue: "1", pages_or_artno: "139-178"}
- {doi: "10.1016/j.jeconom.2008.12.021", type: journal, authors: "Bramoullé, Y., Djebbari, H., & Fortin, B.", year: 2009, title: "Identification of Peer Effects through Social Networks", venue: "Journal of Econometrics", vol: "150", issue: "1", pages_or_artno: "41-55"}
- doi: "10.2478/bsrj-2026-0010"
  title: "AI-Driven Peer Company Identification: A Semantic Text-Similarity Approach Beyond Traditional Industry Classification Systems"
  authors: "Jagrič, T., & Herman, A."
  year: 2026
  venue: "Business Systems Research Journal, 17(1), 204-222"
  type: "journal"
new_dois:
  - "10.2478/bsrj-2026-0010"
---

## CORE

【构念与来源】
本家族 F372 的两列 (llm_peer_n_effective、llm_peer_queried) 是 producer `pipeline/panel/llm_peer_iv.py` 内围绕核心工具变量 llm_peer_tone_iv_{full,ctx,ss} 的两枚诊断/披露列, 不是同行情感度量本身, 而是刻画"该同行 IV 均值实际是由多少家、以及在哪些 bank-year 上算出来的"的元数据。上游流程分两步: 第一步由 LLM (与 stage 21 情感三家投票同源的调用范式, 但用途不同——此处任务是"识别产品市场竞争同行"而非情感打分) 对每家焦点银行发起一次结构化查询, 参照 Hoberg & Phillips (2016) 提出的 TNIC (text-based network industry classification) 方法学惯例, 取"最接近的 10 家同行"为识别上限; 第二步用识别出的同行集合与银行面板样本框求交集, 并对每个同行取其 t-1 期 (滞后一期) 的 tone 度量做等权均值, 构成核心 IV `llm_peer_tone_iv_full/ctx/ss`。llm_peer_n_effective 与 llm_peer_queried 分别刻画这条构造链路第二步 (交集后的有效基数) 与第一步 (调用是否成功) 的两个断点, 是审计该 IV 有效性、识别该 IV 缺失/退化原因的必需元数据, 而非用于回归 RHS 的处理变量或结果变量。
【方法学与计算】
llm_peer_n_effective 的计算路径是: LLM 返回的原始同行候选集合 (未做面板过滤, 对应诊断列 llm_peer_count 的口径) 先与面板样本框做交集 (仅保留在册且在样本期内的银行), 再对每个候选同行检验其 t-1 期是否存在可用的 tone 观测 (缺失/停牌/未进入样本的同行被剔除), 剩余数量即为该 bank-year 实际进入 tone IV 均值分母的同行家数, 是一个 double 类型的计数值 (允许出现 0, 表示查证成功但无面板内可用同行, 此时对应的 tone IV 应为缺失或退化)。llm_peer_queried 则是更上游的一个 0/1 指示列 (int64): 1 表示该 bank-year 的 LLM 同行识别调用已发起且响应被成功解析 (无论解析出的同行集合是否为空); 0 表示调用未发起或响应无法解析, 即该 bank-year 从未真正"被查证过"。这一区分刻意把"查证后确认零同行"与"根本未查证"两种截然不同的缺失机制分离开来 (producer 注释标注为 fix omni-g-llm-peer-07), 因为二者对下游 IV 缺失应如何处理、是否可信有本质区别: 前者是信息 (该银行在 LLM 识别的产品市场同行网络中确无可用同行), 后者是数据缺口 (需要重新查证或做缺失机制分析), 二者混同会污染任何基于"零同行"样本的稳健性检验。
两列的存在服务于同一识别策略的透明度要求: llm_peer_tone_iv 作为工具变量, 其排除约束依赖"同行 t-1 期特质报道冲击只经同行渠道影响焦点银行 t 期结果"这一假设, 而这一假设的可信度直接取决于同行集合的构造质量与覆盖广度——若某类银行系统性地查证失败 (llm_peer_queried=0 占比高) 或系统性地面板内同行稀少 (llm_peer_n_effective 系统性偏低), 则 IV 的弱工具风险与选择性缺失风险都会上升, 必须在第一阶段 F-统计量与工具相关性诊断之外单独披露。llm_peer_n_effective 与另一诊断列 llm_peer_count (计入全部归一化同行, 含不在面板内者) 是不同有效域: 前者是 tone IV 均值分母的真实基数, 后者是 LLM 原始识别广度, 二者之差刻画了"面板覆盖损耗"。
【文献定位】
同行工具变量的构造范式承袭 Leary & Roberts (2014) 关于同行公司财务政策外溢的研究传统; 该文献本身也讨论了同行结果均值型 IV 在排除约束上的局限 (同行结果本身可能与焦点公司共同暴露于相同冲击), 本 producer 通过滞后一期 + 文章级 leave-out (剔除与焦点银行同篇报道的贡献) 缓解这一机械相关, 但 Leary & Roberts (2014) 与 Manski (1993) 关于反射问题 (reflection problem) 的经典论证提醒: 剩余识别假设仍需在论文正文中明确披露, 而非隐含默认成立。同行集合的识别方法论借鉴 Hoberg & Phillips (2016) 的文本网络产业分类思路——用文本信息 (此处为 LLM 对新闻/公开信息的语义推断) 而非传统行业代码来刻画产品市场竞争关系, 并沿用其"10 家最近同行"的实践惯例作为候选集合规模上限; Cao et al. (2025) 进一步证实生成式 LLM 在识别同行公司方面具有与传统文本网络方法相当的效度, 为本 producer 用 LLM 而非规则式匹配来构造同行集合提供了方法学背书。Bramoullé, Djebbari & Fortin (2009) 关于网络中同行效应识别的结构性条件 (网络结构差异性、非传递闭包) 也为审视本工具变量的可识别性提供了理论参照——llm_peer_n_effective 的跨行截面变异, 本质上就是这类识别条件在本数据集中的经验体现。该文提出基于 BERT 语义文本相似度、超越传统 NACE/NAICS 行业代码的 AI 驱动同行公司识别方法, 与本家族 llm_peer_n_effective/llm_peer_queried 所依赖的 LLM 同行识别构造思路互为印证, 引用格式 Jagrič & Herman (2026, Business Systems Research Journal)。

## VAR: llm_peer_n_effective

【变体差分】
llm_peer_n_effective 与家族内另一列 llm_peer_queried 的核心差分在于计量层级: 前者是数量型诊断 (double, 可为 0、也可能因浮点存储惯例而非严格整数), 度量"实际进入核心工具变量 llm_peer_tone_iv_full/ctx/ss 均值计算的面板内同行家数"; 它与另一非本家族诊断列 llm_peer_count (计入 LLM 识别出的全部归一化同行, 不论是否在面板样本框内) 的口径差异是本列的关键区分点——llm_peer_n_effective 是 llm_peer_count 经过面板样本框过滤 (剔除不在册银行) 与滞后一期可用性过滤 (剔除 t-1 期 tone 缺失的同行) 之后的子集计数, 二者之差直接量化了"面板覆盖损耗"。这一损耗的来源可能是: 同行银行未纳入本项目银行面板样本框 (如小型城商行/农商行覆盖不全)、或同行虽在册但该同行在 t-1 期恰好缺失 tone 观测 (如该同行当年报道量为零导致情感度量本身缺失)。对使用者而言, llm_peer_n_effective 是判断 tone IV 弱工具风险的第一道筛子: 当该值系统性偏低 (如全样本均值远小于 TNIC 惯例上限 10) 或呈现与焦点银行特征 (如银行类型、地域) 相关的系统性变异模式时, 意味着工具变量的有效样本基数薄弱, 第一阶段 F 统计量的解读需格外谨慎, 也应作为稳健性检验中按 llm_peer_n_effective 分组或加权的依据。需要强调, llm_peer_n_effective 不区分三轨 full/ctx/ss (同行识别与面板过滤过程与文本轨道无关, 是同行网络结构本身的属性), 但下游 tone IV 均值 (llm_peer_tone_iv_full/ctx/ss) 是逐轨分别用该同行集合上各自轨道的 tone 计算的, 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J 检验; llm_peer_n_effective 本身作为同行集合基数, 在三轨间是共享的单一诊断值, 不随轨道变化。

## VAR: llm_peer_queried

【变体差分】
llm_peer_queried 与 llm_peer_n_effective 的差分在于其刻画的是构造链路更上游的一个二值断点: 它只回答"该 bank-year 的 LLM 同行识别调用是否发起且响应被成功解析"这一问题, 完全不涉及解析出的同行集合规模或是否落入面板框内。取值 1 表示调用成功且可解析 (此时该 bank-year 的同行集合状态是确定的, 可能为非空集合、也可能是查证后确认的空集合); 取值 0 表示调用未发起 (如超出预算/未触发) 或响应无法解析 (如 LLM 返回格式错误、API 超时等), 此时该 bank-year 的同行状态是真正未知的。这一区分 (producer 注释 fix omni-g-llm-peer-07) 的必要性在于: 若不做此区分, 使用者面对 llm_peer_n_effective=0 的观测将无法判断这是"查证后确认无面板内同行" (真实的零, 一种有信息量的观测) 还是"根本没有查过" (数据缺口, 应视为缺失而非零), 两者若混同处理, 会使任何基于"同行数为零"样本的子样本分析或稳健性检验产生系统性偏误——例如若将未查证 (queried=0) 的观测误当作真实零同行 (n_effective=0) 纳入 IV 第一阶段回归, 会人为压低工具相关性并引入选择性偏误。因此规范用法是: 仅在 llm_peer_queried=1 的子样本上解读 llm_peer_n_effective 的取值 (含其为 0 的情形) 为有效信息; llm_peer_queried=0 的观测应作为独立的缺失类别处理, 并在描述性统计与稳健性附录中单独披露其占比与是否与银行特征相关 (是否存在非随机缺失), 以支持 tone IV 排除约束假设的可信度评估。与 llm_peer_n_effective 相同, llm_peer_queried 是不分三轨的单一诊断列 (LLM 同行识别调用本身在 producer 中按 bank-year 发起一次, 不随 full/ctx/ss 文本轨道重复); 但使用者须警惕一个容易混淆的时序错配——llm_peer_queried 报告的是该行自身年份 year=t 的查询是否成功解析 (producer 注释明确标注为"同年口径"), 而同一行上的 llm_peer_tone_iv_full/ctx/ss、llm_peer_count、llm_peer_n_effective 三者的取值全部构造自 lag_year=t-1 的查询结果 (滞后一期同行 tone), 即真正决定该行 tone IV/n_effective 是否可算的"查证"事件发生在 t-1 年, 而非 t 年。因此"若某行 llm_peer_queried=0, 则该行 tone IV 三轨缺失"这一蕴含关系并不成立: 该行 llm_peer_queried=0 只说明 year=t 的查询未成功, 与该行 t-1 期的查询状态是两个独立事件; 真正决定该行 IV/n_effective 是否缺失的, 是 bank 在 year=t-1 那一 bank-year 的查询是否成功 (即面板中 year=t-1 那一行的 llm_peer_queried 取值, 而非本行的取值)。规范用法是: 若要交叉核验某行 tone IV 缺失的成因, 应回查该 bank 在 lag_year=t-1 对应行的 llm_peer_queried 状态, 而不能直接读本行的 llm_peer_queried; 同一 bank 相邻两行 (t-1 与 t) 的 llm_peer_queried 之间不存在必然递推或蕴含关系, 二者是两次独立发起的 LLM 调用。

<!-- rendered-citations:begin -->
Cao, Y., Chen, L., Tucker, J. W., & Wan, C. (2025). Can Generative AI Help Identify Peer Firms? Review of Accounting Studies, 30(4), 3344-3386. https://doi.org/10.1007/s11142-025-09892-6
Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Manski, C. F. (1993). Identification of Endogenous Social Effects: The Reflection Problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Leary, M. T., & Roberts, M. R. (2014). Do Peer Firms Affect Corporate Financial Policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of Peer Effects through Social Networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Jagrič, T., & Herman, A. (2026). AI-Driven Peer Company Identification: A Semantic Text-Similarity Approach Beyond Traditional Industry Classification Systems. Business Systems Research Journal, 17(1), 204-222. https://doi.org/10.2478/bsrj-2026-0010
<!-- rendered-citations:end -->
