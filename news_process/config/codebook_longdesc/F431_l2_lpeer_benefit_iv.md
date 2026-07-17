---
family_id: F431
columns:
- lpeer_benefit_iv_ctx
- lpeer_benefit_iv_ctx_lag1
- lpeer_benefit_iv_ss
- lpeer_benefit_iv_ss_lag1
unit: 工具变量 (与被工具化内生变量 benefit_mean_ctx / benefit_mean_ss 同量纲, 取值范围随构念嵌入余弦相似度映射, 近似 [-1,1])
formula: 银行 i 年份 t 的 lpeer_benefit_iv_{trk} = 同类型同业 (bank_type 相同、排除 i 自身) 该年份 benefit_mean_{trk} 的留一法 (leave-one-out) 均值; _lag1 后缀取该序列滞后一年 (t-1) 取值; trk ∈ {ctx, ss}
producer: pipeline\panel\iv_extensions.py ; pipeline\panel\stata_export.py
upstream:
- benefit_mean_ctx
- benefit_mean_ss
- bank_type
citations:
- doi: "10.1093/qje/qjz021"
  type: journal
  authors: "Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A."
  year: 2019
  title: "Firm-Level Political Risk: Measurement and Effects"
  venue: "Quarterly Journal of Economics"
  vol: "134"
  issue: "4"
  pages_or_artno: "2135-2202"
- doi: "10.1257/aer.20181047"
  type: journal
  authors: "Goldsmith-Pinkham, P., Sorkin, I., & Swift, H."
  year: 2020
  title: "Bartik Instruments: What, When, Why, and How"
  venue: "American Economic Review"
  vol: "110"
  issue: "8"
  pages_or_artno: "2586-2624"
- doi: "10.2307/2298123"
  type: journal
  authors: "Manski, C. F."
  year: 1993
  title: "Identification of Endogenous Social Effects: The Reflection Problem"
  venue: "The Review of Economic Studies"
  vol: "60"
  issue: "3"
  pages_or_artno: "531-542"
- doi: "10.1111/jofi.12094"
  type: journal
  authors: "Leary, M. T., & Roberts, M. R."
  year: 2014
  title: "Do Peer Firms Affect Corporate Financial Policy?"
  venue: "The Journal of Finance"
  vol: "69"
  issue: "1"
  pages_or_artno: "139-178"
- doi: "10.1086/728743"
  type: journal
  authors: "Gabaix, X., & Koijen, R. S. J."
  year: 2024
  title: "Granular Instrumental Variables"
  venue: "Journal of Political Economy"
  vol: "132"
  issue: "7"
  pages_or_artno: "2274-2303"
- doi: "10.1093/rfs/hhaf012"
  type: journal
  authors: "Jha, M., Liu, H., & Manela, A."
  year: 2026
  title: "Does Finance Benefit Society? A Language Embedding Approach"
  venue: "Review of Financial Studies"
  vol: "39"
  issue: "5"
  pages_or_artno: "1227-1266"
- doi: "10.1257/jep.20231370"
  type: journal
  authors: "Borusyak, K., Hull, P., & Jaravel, X."
  year: 2025
  title: "A Practical Guide to Shift-Share Instruments"
  venue: "Journal of Economic Perspectives"
  vol: "39"
  issue: "1"
  pages_or_artno: "181-204"
- doi: "10.1111/roiw.12674"
  type: journal
  authors: "Girshina, A., Mathä, T. Y., & Ziegelmeyer, M."
  year: 2024
  title: "Peer Effects in Stock Market Participation: Evidence from Immigration"
  venue: "Review of Income and Wealth"
- doi: "10.1080/15140326.2024.2375682"
  type: journal
  authors: "Zaighum, I., Aman, A., & Abd Karim, M. Z."
  year: 2024
  title: "Peer effects, industry concentration and capital structure: evidence from emerging market economies"
  venue: "Journal of Applied Economics"
new_dois:
  - "10.1111/roiw.12674"
  - "10.1080/15140326.2024.2375682"
---

## CORE

【构念与来源】
本家族 4 列构成 benefit_society 衍生论文识别策略中「同业留一法 (leave-one-out, LOO) 工具变量」族在实体窗口轨 (ctx) 与银行金科同句轨 (ss) 上的镜像补全。产出于 40_panel_export_main 步骤 8z「IV 扩展族」(`pipeline\panel\iv_extensions.py`), 与 full 轨既有 `leave_one_out_peer_benefit_iv(_lag1)` 一一对应, 前缀由 `leave_one_out_peer_` 紧凑为 `lpeer_`, 以保证含 `_lag1` 后缀的最长列名不超过 Stata 32 字符变量名上限, 避免 `stata_export` 截断歧义。构念内核是「用同类型同业的受益态度均值 (排除该银行自身), 作为该银行自身受益态度的工具」——经典的 Bartik/shift-share 精神变体, 借鉴 Hassan et al. (2019, QJE) 在企业层面用同业同期政治风险度量构造工具变量的做法, 以及 Goldsmith-Pinkham, Sorkin & Swift (2020, AER) 对 Bartik 类工具识别假设的系统刻画。内生变量是各轨 `benefit_mean_{ctx,ss}` —— 银行金科新闻文本经语言嵌入投影到「金融是否有益于社会」构念方向上的逐篇得分之银行-年均值 (jha2026benefit 语言嵌入路径, Jha, Liu & Manela 2026, RFS)。工具本身不进入结果方程, 只用于第一阶段预测内生变量的外生变动部分。

【方法学与计算】
计算原语是「同 bank_type 分组内的留一法均值」: 对银行 i、年份 t、轨道 trk, 先取同一 bank_type (银行业务/所有制类型分类, 定义于面板上游实体匹配字典) 下、同一年份 t 的全部银行样本的 `benefit_mean_{trk}`, 排除 i 自身后取算术均值, 得到 `lpeer_benefit_iv_{trk}`。`_lag1` 变体是该序列在时间维度上整体后移一年, 即银行 i 年份 t 的 `lpeer_benefit_iv_{trk}_lag1` 取值等于同一银行同一轨道年份 t-1 的 `lpeer_benefit_iv_{trk}` 取值 (面板内按 bank_id 排序后的一阶滞后算子, 首年份对应缺失), 与因果推断中「用过去期同业均值预测当期内生变量」的时序错位设计一致, 削弱同期共同冲击 (common shock) 对排他性约束的直接威胁。ctx 轨的内生变量来源是实体窗口文本 (`content_ctx`, 标题+目标银行实体前后窗口) 计算的 `benefit_mean_ctx`; ss 轨来源是银行∧金科词同句共现窗口文本 (`content_ss`) 计算的 `benefit_mean_ss` —— 无银行∧金科同句共现时 `content_ss` 按项目铁律回退为全文 body (`ss_is_fallback=True`, 镜像 ctx 轨回退语义, 共享 `n_articles` 分母)。与 full 轨的 `leave_one_out_peer_benefit_iv` 相比, ctx/ss 两轨在「同一构念、不同文本剪裁窗口」维度上并排补全, 三轨对应同一篇文章的三种裁剪方式 (full=标题+全文, ctx=标题+实体窗口, ss=标题+银行∧金科同句窗口), 而非三个独立构念。项目口径明确: 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把 full/ctx/ss 任意两轨 LOO 拼成一对工具跑同一个 over-identified Hansen J —— 三者共享同一篇文章的 bank_type×year 共同冲击, 逐字同污染各轨, 使 Hansen J 对真实排他性威胁的检验功效趋近于零, 且近共线还会拖累弱工具诊断 (Kleibergen-Paap rk Wald F 统计量)。若确需做过度识别检验, 应跨族组合工具 (例如 LOO × Bartik、LOO × zone-LOO), 而非跨轨组合同族工具。这一处理呼应 Manski (1993, Review of Economic Studies) 对「反射问题」(reflection problem) 的经典刻画: 同业均值类工具本质上是用群体特征预测个体特征, 需要额外的排他性论证 (工具只通过「同业整体受益态度基调」这一渠道影响该银行受益态度, 而非通过共同宏观/行业冲击的直接传导), 也呼应 Leary & Roberts (2014, Journal of Finance) 在同业效应识别中对留一法工具构造的应用范式——留一法排除自身避免了机械的部分-整体相关性 (mechanical part-whole correlation), 是这类工具构造的标准做法。滞后一期设计进一步呼应 Gabaix & Koijen (2024, Journal of Political Economy) 关于颗粒工具变量 (granular instrumental variables) 在排他性约束上对时序结构的强调——用滞后期变量作为工具, 可以部分缓解同期反向因果与同期共同冲击对排他性的直接威胁, 但不能完全消除, 仍需结合弱工具检验、Hansen J (跨族) 等诊断共同使用。

【文献定位】
本家族方法学谱系上承 Bartik/shift-share 工具变量与同业留一法 (peer leave-one-out) 两条相互交织的识别策略脉络。Bartik 一脉的规范性论述见 Goldsmith-Pinkham, Sorkin & Swift (2020, American Economic Review), 该文系统拆解 Bartik 工具的识别假设为「shift 外生」与「share 外生」两种等价刻画, 为本家族工具构造的排他性论证提供方法论基准。留一法同业工具的应用先例见 Hassan et al. (2019, Quarterly Journal of Economics) 的企业层面政治风险度量, 以及 Leary & Roberts (2014, The Journal of Finance) 对同业公司财务政策溢出效应的识别。反射问题的理论根基见 Manski (1993, The Review of Economic Studies), 该文首次系统区分内生效应 (endogenous effect)、外生效应 (contextual/exogenous effect) 与关联效应 (correlated effect) 三类同群效应混淆来源, 是留一法工具设计动机的理论出发点。内生变量本身的构念来源见 Jha, Liu & Manela (2026, Review of Financial Studies) 提出的语言嵌入 (language embedding) 方法, 将「金融是否有益于社会」这一抽象构念投影为文本方向向量, 用逐篇余弦相似度打分。工具的近期拓展参见 Gabaix & Koijen (2024, Journal of Political Economy) 的颗粒工具变量框架, 以及 Borusyak, Hull & Jaravel (2025, Journal of Economic Perspectives) 对 shift-share 工具实践检查表的系统梳理 (共现权重×银行测度的排他性讨论)。本家族与家族内 full 轨 `leave_one_out_peer_benefit_iv(_lag1)`、以及跨论文的 `zone_leave1out_benefit_iv(_ctx/_ss)` (按 bank_zone 跨省分组的姊妹工具族) 共同构成 benefit_society 衍生论文的完整识别策略工具箱, 供 2SLS 模板选配。此外, Girshina, Mathä & Ziegelmeyer (2024, Review of Income and Wealth) 利用移民背景下的同侪构成变化识别同侪效应对股市参与决策的因果影响, 方法论上采用留一法工具变量思路; Zaighum, Aman & Abd Karim (2024, Journal of Applied Economics) 以新兴市场企业为样本, 考察同行业同侪均值对个体企业资本结构决策的影响及行业集中度的调节作用, 呼应本测度的同业留一法均值构造思路。

## VAR: lpeer_benefit_iv_ctx

【变体差分】
本列是 `lpeer_benefit_iv` 族在 ctx 轨 (实体窗口文本) 的当期取值: 银行 i 年份 t 的取值 = 同 bank_type 分组、同年份 t、排除 i 自身后, 其余银行 `benefit_mean_ctx` 的算术均值。内生变量来源 `benefit_mean_ctx` 计算自 `content_ctx` (标题+目标银行实体前后窗口文本), 与 full 轨全文剪裁窗口不同, 捕捉「聚焦目标银行本身语境」下的受益态度基调, 相对全文剪裁能过滤掉与目标银行本身无直接关联的段落噪声, 是三轨 (full/ctx/ss) 稳健性并排中的一员。本列与家族内 `lpeer_benefit_iv_ss` 的差异在于文本剪裁半径不同 (实体窗口 vs 银行∧金科同句窗口), 两者是互为稳健性、不分主次的并排测度, 均对应各自轨道的当期 (未滞后) 留一法工具; 与本家族内 `lpeer_benefit_iv_ctx_lag1` 的差异纯为时间维度——后者是本列序列的滞后一期版本。使用本列做第一阶段回归时, 应仅与 ctx 轨内生变量 (`benefit_mean_ctx` 及其面板下游列) 配对, 不应与 full 或 ss 轨的 LOO 工具混入同一 over-identified 检验。分组变量 bank_type 取自实体匹配字典的银行业务/所有制类型分类, 留一法排除自身是为了避免结果方程与工具变量之间的机械部分-整体相关性 (若不排除自身, 银行 i 自己的观测会同时出现在内生变量与工具两侧, 制造纯算术意义上的正相关, 与真实的同业溢出效应混淆), 这一处理与 Leary & Roberts (2014, Journal of Finance) 在同业公司财务政策溢出效应研究中的留一法工具构造范式一致。计算原语内置硬编码门槛 min_peers=2: 排除 i 自身后, 若同 bank_type、同年份 t 内剩余有效同业观测数 < 2 (即单一同业甚至零同业, 不构成一个「组均值」), 则该银行该年份该轨道的取值直接置为缺失 (NaN), 而非退化为单一同业取值或全样本均值——这是刻意设计, 避免用退化样本冒充组均值。因此当同 bank_type 分组内当年样本银行数量过少 (逼近或低于 min_peers 门槛) 时, 不只是留一法均值方差偏大, 更直接的后果是样本缺失率上升, 二者叠加共同构成弱工具问题的潜在来源, 需结合弱工具诊断统计量与缺失率一并判断该轨道工具是否可用。

## VAR: lpeer_benefit_iv_ctx_lag1

【变体差分】
本列是 `lpeer_benefit_iv_ctx` 序列的滞后一期版本: 银行 i 年份 t 的取值 = 该银行同一 ctx 轨在年份 t-1 的 `lpeer_benefit_iv_ctx` 取值 (面板按 bank_id 分组、按年份排序后的一阶滞后算子; 样本首年份因无 t-1 观测而取值缺失)。滞后设计的识别学动机是把「同期同业均值」替换为「前一期同业均值」作为工具, 降低同期共同冲击 (如行业性政策、宏观金融环境突变) 同时驱动工具与结果方程误差项、从而威胁排他性约束的风险——工具变量文献中用滞后同群变量规避同期反向因果与共同冲击是标准做法, 但代价是可能引入序列相关下的弱工具问题, 须结合 Kleibergen-Paap 弱工具诊断使用。与家族内 `lpeer_benefit_iv_ctx` 的差异纯粹是时间维度的滞后算子, 构念、轨道 (ctx 实体窗口)、分组口径 (同 bank_type 留一法) 完全一致; 与 `lpeer_benefit_iv_ss_lag1` 的差异是文本剪裁轨道不同 (实体窗口 vs 银行金科同句窗口), 两者各自 just-identified、互为稳健性并排, 不应混入同一 Hansen J 检验。滞后处理对应 Gabaix & Koijen (2024, Journal of Political Economy) 颗粒工具变量框架中对时序结构排他性的强调: 用滞后期同业均值而非同期均值构造工具, 可以缓解「本期宏观/行业冲击同时推动银行 i 自身受益态度与其同业受益态度」这一共同冲击渠道对排他性约束的直接威胁, 但无法完全排除跨期持续性冲击 (如某项监管政策连续两年发酵) 的残余污染, 实证使用时仍需结合弱工具诊断 (Kleibergen-Paap rk Wald F) 与工具相关性检验联合判断该滞后工具在 ctx 轨上的可用性, 不能仅凭滞后设计本身默认排他性成立。

## VAR: lpeer_benefit_iv_ss

【变体差分】
本列是 `lpeer_benefit_iv` 族在 ss 轨 (银行∧金科词同句共现窗口文本) 的当期取值: 银行 i 年份 t 的取值 = 同 bank_type 分组、同年份 t、排除 i 自身后, 其余银行 `benefit_mean_ss` 的算术均值。内生变量来源 `benefit_mean_ss` 计算自 `content_ss` (标题+目标银行与金科词在同一句内共现的窗口文本, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句), 捕捉「银行与金融科技被同句直接提及」这一更严格语境下的受益态度基调。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, 则 `content_ss` 按项目铁律退化为全文 body 兜底 (`ss_is_fallback=True`), 与 `n_articles` 共享分母, 不会造成该文章在 ss 轨上的样本流失, 只是语境窗口退化为全文粒度。本列与 `lpeer_benefit_iv_ctx` 差异在剪裁窗口宽严不同 (同句共现窗口更严格、更聚焦「银行-金科」议题本身的措辞), 两者是互为稳健性、不分主次的并排测度, 不构成互相嵌套或替代关系。使用本列做工具变量时应仅与 ss 轨内生变量配对做第一阶段, 避免与 full/ctx 轨的 LOO 工具混入同一过度识别检验。ss 轨同句共现窗口相较 ctx 实体窗口更聚焦「银行与金科被同一句话直接并列提及」的措辞, 排除了同篇文章中与银行金科议题无直接关联段落的稀释效应, 与 ctx 轨的 Hassan et al. (2019, QJE) 实体邻近窗口谱系并列, 而非互相嵌套或替代——两条剪裁窗口都服务于同一个「压缩内生变量测量噪声、进而压缩留一法工具的传导噪声」目标, 但作用力度不同: 窗口越窄, 单篇文章信号越集中于「银行-金科」议题本身, 但可用信号量也越稀薄。同句窗口更小意味着单篇文章贡献的信号更稀疏, 依赖回退兜底 (`ss_is_fallback`) 的比例通常高于 ctx 轨, 在解读该轨道留一法均值的方差与弱工具诊断结果时应结合回退占比一并评估。

## VAR: lpeer_benefit_iv_ss_lag1

【变体差分】
本列是 `lpeer_benefit_iv_ss` 序列的滞后一期版本: 银行 i 年份 t 的取值 = 该银行同一 ss 轨在年份 t-1 的 `lpeer_benefit_iv_ss` 取值 (面板一阶滞后算子, 样本首年份取值缺失)。与 `lpeer_benefit_iv_ctx_lag1` 完全对称, 差异仅在于所依赖的内生变量来源轨道不同 (ss 银行∧金科同句共现窗口 vs ctx 实体窗口), 时序滞后的识别学动机 (削弱同期共同冲击对排他性约束的直接威胁) 与后者一致。四列在家族内部构成一个 2×2 结构: {ctx, ss} 两条剪裁轨道 × {当期, 滞后一期} 两种时序处理, 每个单元各自对应一个 just-identified 工具, 互为稳健性并排选配进各自轨道匹配的 2SLS 模板, 不应跨单元混用或合并进同一 over-identified 检验。滞后一期设计对 ss 轨尤其重要: 由于 ss 轨内生变量依赖更严格的同句共现窗口、单篇文章信号更稀疏, 同期波动更容易受当年个别热点事件驱动, 用 t-1 期同业均值作为工具能在一定程度上把「当期同业热点冲击」从工具中剥离, 降低其与结果方程当期误差项相关的风险, 但对应代价是该轨道工具的时序滞后可能进一步放大方差 (稀疏信号 + 滞后), 弱工具诊断在 ss_lag1 单元上格外关键, 建议与 zone_leave1out_benefit_iv_ss (按 bank_zone 跨省分组、无滞后的姊妹工具) 联合比较作为稳健性交叉验证, 但两者仍应各自 just-identified、不合并进同一过度识别检验。

<!-- rendered-citations:begin -->
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik Instruments: What, When, Why, and How. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Manski, C. F. (1993). Identification of Endogenous Social Effects: The Reflection Problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Leary, M. T., & Roberts, M. R. (2014). Do Peer Firms Affect Corporate Financial Policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Gabaix, X., & Koijen, R. S. J. (2024). Granular Instrumental Variables. Journal of Political Economy, 132(7), 2274-2303. https://doi.org/10.1086/728743
Jha, M., Liu, H., & Manela, A. (2026). Does Finance Benefit Society? A Language Embedding Approach. Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Borusyak, K., Hull, P., & Jaravel, X. (2025). A Practical Guide to Shift-Share Instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Girshina, A., Mathä, T. Y., & Ziegelmeyer, M. (2024). Peer Effects in Stock Market Participation: Evidence from Immigration. Review of Income and Wealth. https://doi.org/10.1111/roiw.12674
Zaighum, I., Aman, A., & Abd Karim, M. Z. (2024). Peer effects, industry concentration and capital structure: evidence from emerging market economies. Journal of Applied Economics. https://doi.org/10.1080/15140326.2024.2375682
<!-- rendered-citations:end -->
