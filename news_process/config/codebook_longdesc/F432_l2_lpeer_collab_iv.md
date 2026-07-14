---
family_id: F432
columns:
- lpeer_collab_iv_ctx
- lpeer_collab_iv_ctx_lag1
- lpeer_collab_iv_ss
- lpeer_collab_iv_ss_lag1
unit: 工具变量 (与被工具化内生变量 collab_frac_cm 同量纲, [0,1] 占比同尺度)
formula: 'lpeer_collab_iv_{ctx,ss} = 银行 i 在年份 t 的同类型 (bank_type) 同业留一法均值 (leave-one-out mean), 分别以底层内生变量 collab_frac_cm (ctx 轨, 裸列名无 _ctx 后缀) / collab_frac_cm_ss (ss 轨) 为输入: lpeer_collab_iv_ctx_it = mean_{j∈同type(i), j≠i}(collab_frac_cm_jt); lpeer_collab_iv_ss_it = mean_{j∈同type(i), j≠i}(collab_frac_cm_ss_jt)。_lag1 为对应列整体滞后一期 (t-1)。'
producer: pipeline\panel\iv_extensions.py::compute_iv_extensions ; pipeline\panel\stata_export.py (HEURISTIC_LABELS)
upstream:
- collab_frac_cm (ctx/ss 轨底层内生变量, P5 collab 论文面板列)
- bank_type (同业分组键)
citations:
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: 'Identification of endogenous social effects: The reflection problem'
  venue: The Review of Economic Studies
  vol: '60'
  issue: '3'
  pages_or_artno: 531-542
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: Do peer firms affect corporate financial policy?
  venue: The Journal of Finance
  vol: '69'
  issue: '1'
  pages_or_artno: 139-178
- doi: 10.1111/jofi.13384
  type: journal
  authors: Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L.
  year: 2024
  title: FinTech credit and entrepreneurial growth
  venue: The Journal of Finance
  vol: '79'
  issue: '5'
  pages_or_artno: 3309-3359
- doi: 10.1086/727712
  type: journal
  authors: Lerner, J., Seru, A., Short, N., & Sun, Y.
  year: 2024
  title: 'Financial innovation in the twenty-first century: Evidence from US patents'
  venue: Journal of Political Economy
  vol: '132'
  issue: '5'
  pages_or_artno: 1391-1449
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: A practical guide to shift-share instruments
  venue: Journal of Economic Perspectives
  vol: '39'
  issue: '1'
  pages_or_artno: 181-204
- doi: 10.1017/CBO9780511614491.006
  type: book
  authors: Stock, J. H., & Yogo, M.
  year: 2005
  title: Testing for weak instruments in linear IV regression
  venue: 'Identification and Inference for Econometric Models: Essays in Honor of Thomas Rothenberg (D. W. K. Andrews & J. H. Stock, Eds.)'
  pages_or_artno: 80-108
- doi: 10.1146/annurev-economics-080218-025643
  type: journal
  authors: Andrews, I., Stock, J. H., & Sun, L.
  year: 2019
  title: 'Weak instruments in instrumental variables regression: Theory and practice'
  venue: Annual Review of Economics
  vol: '11'
  pages_or_artno: 727-753
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: Text as data
  venue: Journal of Economic Literature
  vol: '57'
  issue: '3'
  pages_or_artno: 535-574
new_dois: []
---

## CORE

【构念与来源】
本家族四列是论文 P5 (bank_fintech_collab, Chesbrough 2003 开放式创新谱系) 内生解释变量 collab_frac_cm (银行—金科协作模式占比, 象征性 vs 实质性协作二分中的 "外部/开放" 一端) 的同业留一法 (leave-one-out, LOO) 工具变量族, 在 ctx (实体窗口) 与 ss (银行∧金科同句共现窗口) 两条稳健轨上各自成对提供 (当期 + 一期滞后), 与全文轨既有的 leave_one_out_peer_collab_iv(_lag1) 三轨并列、互为稳健性。识别逻辑源自银行同业效应文献: Manski (1993) reflection problem 指出, 若直接用同业均值解释银行自身的行为/态度变量, 内生反射性会使系数无法区分内生同侪效应、外生特征相关与共同冲击; Leary & Roberts (2014) 在企业金融政策的同业效应研究中系统化了留一法工具 (排除自身后计算同类型同业均值) 作为处理这一识别难题的标准手段, 该做法此后被广泛移植到银行业文本测度的同业效应研究 (如 Hau et al. 2024, JF, 金融科技信贷的同业扩散)。本族工具变量的构造逻辑是: 银行 i 自身在协作叙事上的选择不可避免地受到"同型同业普遍在做什么"这一外生成分驱动 (行业规范、监管风向、媒体报道范式趋同), 而将 i 自身观测值排除在均值计算之外, 可以阻断由 i 自身特质冲击直接污染其"工具值"这一显而易见的机制性内生性来源, 从而为 collab_frac_cm 的因果效应估计提供一个更贴近外生冲击传导路径的排他性约束候选。

【方法学与计算】
计算发生在面板导出阶段 (`pipeline/panel/iv_extensions.py::compute_iv_extensions`, runner 步骤 8z, 由 `config/panel.yaml::compute_iv_extensions` 开关控制默认启用), 属于「11 论文 IV 补全编排」批量产出的一支。分组键是 `bank_type` (银行类型, 如国有大行/股份制/城商行/农商行等既有分类), 分组内逐年、逐轨计算留一法均值: 对银行 i 在年份 t、ctx 轨, `lpeer_collab_iv_ctx_it = mean_{j∈同type(i), j≠i}(collab_frac_cm_jt)` (底层内生变量为裸列名 `collab_frac_cm`, 本身即代表 ctx 轨测度, 无 `_ctx` 后缀); ss 轨同式代入 `collab_frac_cm_ss`。`_lag1` 列是上述当期列在面板 (bank, year) 结构上整体滞后一期 (t-1 值填入 t 行), 与主线 `leave_one_out_peer_*_iv_lag1` 系列滞后口径一致, 用于满足工具变量在时间维度上先于当期 collab 叙事实现、降低同期性反向因果嫌疑的估计设计需要。命名上采用紧凑前缀 `lpeer_` (而非全称 `leave_one_out_peer_`) 是刻意的工程决定: 三轨 (full/ctx/ss) 逐一附加 `_ctx`/`_ss` 与 `_lag1` 后缀后仍需保持列名 ≤32 字符, 以规避 Stata `.dta` 变量名截断可能造成的隐性歧义 (`_ss` 短于 `_ctx`, 使得 `_ss_lag1` 长度 26 字符低于 `_ctx_lag1` 的 27 字符, 两者均在阈值内)。

本族与 full 轨 `leave_one_out_peer_collab_iv(_lag1)` 是镜像三胞胎而非互相嵌套或加总关系: 三者各自使用同轨底层内生变量 (collab_frac_cm 的 full/ctx/ss 三个版本) 计算, 各自独立 just-identified, 在 2SLS 第一阶段中彼此并排列示, 分别验证 collab_frac_cm 三个文本剪裁窗口下的同业效应工具是否都能通过弱工具诊断、且第二阶段估计方向与显著性是否一致 (三轨互为稳健性、不分主次)。铁律: full/ctx/ss 三轨任意两条 LOO 工具绝不可拼在同一个 2SLS 设定里跑 Hansen J over-identification 检验 — 三者的底层文本剪裁窗口 (full=标题+全文、ctx=标题+实体窗口、ss=标题+银行∧金科同句窗口) 来自同一篇文章, bank_type×year 层面的共同行业冲击会逐字同时污染三轨, 使得 Hansen J 对真实排他性威胁的检验功效趋近于零, 同时因三条工具彼此高度共线而拖累 Kleibergen-Paap rk Wald F 弱工具统计量的表现 (参见 Andrews, Stock & Sun 2019, Annual Review of Economics, 对弱工具与高度相关多工具场景推断的系统综述)。若研究设计确需 over-identification 检验, 应改用跨族工具组合 (例如同业 LOO × Bartik shift-share 工具, 或同业 LOO × 地域 zone-LOO 工具), 这类组合的排他性威胁来源在结构上彼此独立, 各既有 2SLS 模板中已预留对应 overid 诊断列。

弱工具与推断的一般性诊断规范遵循 Stock & Yogo (2005) 的经验法则与 Andrews, Stock & Sun (2019) 对弱工具推断方法的系统综述; 工具构造本身 (留一法排除自身观测) 的形式化处理另可参照 Borusyak, Hull & Jaravel (2025) 对 shift-share 类工具排他性约束的检查清单式讨论, 尽管本族工具并非严格意义上的 shift-share 构造, 但同属"以同组其余单位聚合特征作为外生成分代理"这一大类工具变量设计, 两者在识别假设的检验思路上可相互借鉴。

【文献定位】
本族工具变量的定位是为 P5 (bank_fintech_collab) 论文中"银行—金科协作模式选择如何影响下游经营/创新产出"这一因果问题提供内生性校正手段。Hau et al. (2024, Journal of Finance) 在金融科技信贷扩散的实证设计中采用了类似的同业留一法思路处理银行层面金融科技相关行为变量的内生性, 为本族工具在银行业文本测度语境下的适用性提供了直接的期刊级先例; Lerner, Seru, Short & Sun (2024, Journal of Political Economy) 在金融创新专利研究中同样面临"银行/机构创新叙事选择本身内生于同业环境"的识别挑战, 其处理思路 (以同组其余单位的聚合特征构造工具) 与本族逻辑同源。Manski (1993) 的 reflection problem 框架则是本族方法学合法性的理论基石: 唯有通过留一法排除自身观测, 才能在原则上区分"银行 i 因所属同业普遍协作氛围而协作" (内生同侪效应, 本族工具试图分离出的外生成分) 与"银行 i 自身特质恰好与协作叙事相关" (与工具构造本身无关的混淆项)。

## VAR: lpeer_collab_iv_ctx

【变体差分】
本列是 lpeer_collab_iv 家族在 ctx (实体窗口) 轨上的当期同业留一法工具, 底层内生变量为裸列名 `collab_frac_cm` (由 ctx 轨情感/分类流水线在标题+银行∧金科实体窗口文本上产出的协作模式占比测度; 该列本身即代表 ctx 轨测度, 不带 `_ctx` 后缀, 与 ss 轨对应列 `collab_frac_cm_ss` 命名不对称是源码既定事实, 不宜脑补出一个不存在的 `collab_frac_cm_ctx` 列名)。分组键仍是 `bank_type`, 计算方式与其余三列共享同一留一法均值公式, 差异仅在于底层文本剪裁窗口: ctx 轨排除了正文中与银行/金科实体不直接相关的段落, 保留标题及实体邻近窗口, 用以检验"协作叙事的实体聚焦程度是否影响同业工具的强度与方向"这一稳健性问题。本列与 `leave_one_out_peer_collab_iv` (full 轨) 及 `lpeer_collab_iv_ss` 是并排的 just-identified 工具, 三者互为稳健性、不分主次, 严禁在同一 2SLS 设定中把本列与另两轨工具同时纳入并跑 Hansen J over-identification 检验 (三轨底层文章与 bank_type×year 共同冲击的重叠污染使该检验功效失效, 详见 CORE 节)。本列不含时间滞后处理, 反映的是与被工具化变量同期 (t 期) 的同业协作叙事外生成分。使用本列作为工具变量时, 排他性假设的实质是: 银行 i 自身当期在实体窗口文本中呈现的协作叙事选择, 不应通过除"同业普遍协作氛围"这一渠道之外的其他路径影响其自身当期结果变量 (如 cost-income ratio 变化、并购活动等 P5 下游产出), 这一假设的可信度需要结合弱工具诊断 (第一阶段 F 统计量) 与 Manski (1993) reflection problem 框架逐案例评估, 不同 bank_type 分组内同业数量偏少时尤须警惕留一法均值本身方差过大导致的弱工具问题。

## VAR: lpeer_collab_iv_ctx_lag1

【变体差分】
本列是 `lpeer_collab_iv_ctx` 在面板 (bank, year) 结构上整体滞后一期 (t-1 值填入 t 行) 的版本, 其余构造逻辑 (ctx 轨底层变量裸列名 `collab_frac_cm`、`bank_type` 分组、留一法均值公式) 与当期列完全一致, 唯一差分维度是时间滞后。滞后处理的动机是在 2SLS 设计中进一步降低工具变量与结果变量之间的同期性关联嫌疑 —— 若研究设计要求工具在时间上严格先于被解释的当期结果实现 (例如避免同业协作叙事与当期银行经营产出之间存在未被观测的同期共同冲击), 应优先选用本列而非当期列。与 `leave_one_out_peer_collab_iv_lag1` (full 轨滞后工具) 及 `lpeer_collab_iv_ss_lag1` (ss 轨滞后工具) 同样构成三轨并排的 just-identified 工具集合, 适用同一条"禁混同一 Hansen J"铁律。在实证使用上, 滞后工具通常被视为比当期工具更贴近"排他性约束成立"这一理想情形的选择, 因为 t-1 期的同业协作叙事在时间上严格先于 t 期结果变量的实现, 反向因果 (结果变量影响同期同业叙事) 的渠道被机械阻断; 但代价是滞后带来的样本损失 (面板起始年份无法计算 t-1 值) 以及工具与内生变量当期实现之间可能的相关性衰减, 使用者应在当期列与滞后列之间做稳健性对照, 而非仅报告其中一支。

## VAR: lpeer_collab_iv_ss

【变体差分】
本列是 lpeer_collab_iv 家族在 ss (银行∧金科同句共现) 轨上的当期同业留一法工具, 底层内生变量为 `collab_frac_cm_ss`。ss 轨的文本剪裁判据比 ctx 更严格: 仅当同一句子内同时出现目标银行实体与金科词 (±N 句窗, `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 N=1) 时才计入该轨文本, 若某篇文章不存在这种银行∧金科同句共现, 则该轨回退为镜像 ctx 轨的全文 body (`content_ss` 取全文, `ss_is_fallback` 标记为 True), 回退发生率共享 `n_articles` 分母口径。这一回退语义与 ctx 轨镜像一致, 保证在金科词与银行实体从未同句共现的边界情况下测度仍优雅退化而非产生缺失。本列继承了这一底层设计: `collab_frac_cm_ss` 及以其为输入的留一法工具, 在样本中同句共现稀疏的年份/银行类型组合上, 实际反映的可能更多是回退到全文的协作叙事均值而非严格同句语境下的均值, 使用者在解读本列作为工具变量的排他性强度时应留意这一点。与 full 轨、ctx 轨当期工具三者并排 just-identified、互为稳健性, 铁律同上不赘述。ss 轨的构造逻辑锚点是 Gentzkow, Kelly & Taddy (2019, Journal of Economic Literature) 关于文本作为数据 (text-as-data) 测度设计的方法学综述所强调的窗口/判据选择对下游估计敏感性的一般性原则: 严格同句共现被视为比宽泛实体窗口更"干净"的关联证据, 因而 ss 轨常被定位为 ctx 轨之外更严格的稳健性检验, 而非替代关系; 当 ss 轨工具因样本稀疏 (同句共现率低、回退比例高) 导致弱工具诊断表现不佳时, 应参照 ctx 轨与 full 轨的结果做交叉验证, 而不应单独依赖 ss 轨下结论。

## VAR: lpeer_collab_iv_ss_lag1

【变体差分】
本列是 `lpeer_collab_iv_ss` 的滞后一期版本, 底层变量与分组逻辑与当期 ss 轨列完全一致, 差分维度仅为时间滞后 (t-1 填入 t 行)。列名长度是本列在设计上的一个显式约束点: 采用 `lpeer_` 紧凑前缀而非 `leave_one_out_peer_` 全称, 使得 `_ss_lag1` 缀满后总长度 (26 字符) 严格低于 32 字符上限, 也低于同批 `_ctx_lag1` 版本 (27 字符) —— 这一命名细节被显式记录在 producer 源码注释中, 是为了绕开 Stata `.dta` 变量名 32 字符截断可能引入的命名歧义, 保证下游 Stata 模板可以直接引用完整列名而不必担心截断碰撞。本列与 `leave_one_out_peer_collab_iv_lag1` (full 轨) 及 `lpeer_collab_iv_ctx_lag1` (ctx 轨) 构成三轨并排的滞后工具集合, 适用同一条"各轨各自 just-identified、禁混同一 Hansen J"的识别铁律; 三者中若要做跨族 over-identification 检验, 应改用同业 LOO 工具与 Bartik/地域 zone-LOO 等排他性威胁来源结构独立的跨族工具组合。作为四列中滞后维度与最严格文本判据维度的双重叠加版本, 本列在实际估计中往往样本量最小 (同时受滞后损失首年样本与 ss 轨同句共现稀疏两重约束), 建议仅作为补充稳健性列而非主表首选工具, 且在报告弱工具诊断时应单独列出第一阶段 F 统计量与 Kleibergen-Paap rk Wald F, 不与其余三列的诊断结果混同呈现, 以免读者误判排他性约束在四列间是同等可信的。

<!-- rendered-citations:begin -->
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. The Journal of Finance, 79(5), 3309-3359. https://doi.org/10.1111/jofi.13384
Lerner, J., Seru, A., Short, N., & Sun, Y. (2024). Financial innovation in the twenty-first century: Evidence from US patents. Journal of Political Economy, 132(5), 1391-1449. https://doi.org/10.1086/727712
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Stock, J. H., & Yogo, M. (2005). Testing for weak instruments in linear IV regression. Identification and Inference for Econometric Models: Essays in Honor of Thomas Rothenberg (D. W. K. Andrews & J. H. Stock, Eds.). https://doi.org/10.1017/CBO9780511614491.006
Andrews, I., Stock, J. H., & Sun, L. (2019). Weak instruments in instrumental variables regression: Theory and practice. Annual Review of Economics, 11, 727-753. https://doi.org/10.1146/annurev-economics-080218-025643
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
<!-- rendered-citations:end -->
