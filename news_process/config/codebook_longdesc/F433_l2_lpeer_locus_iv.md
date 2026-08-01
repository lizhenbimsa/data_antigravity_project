---
family_id: F433
novelty_exempt_rationale: "F433 是 P4 主线 full 轨工具变量家族 leave_one_out_peer_locus_iv 在 ctx/ss 两条文本剪裁轨上的镜像补全变体(命名/构造/分组逻辑与主家族完全一致,仅内生变量所依赖的文本剪裁窗口不同),其测度定义与识别策略依据(Manski反射问题、Leary & Roberts同业LOO工具、Bartik/shift-share诊断框架)已在母族/主线家族引文中给出,属技术变体而非独立新构念,无需单独追加新颖文献。"
columns:
- lpeer_locus_iv_ctx
- lpeer_locus_iv_ctx_lag1
- lpeer_locus_iv_ss
- lpeer_locus_iv_ss_lag1
unit: 工具变量 (与被工具化内生变量 tech_frac_lc / tech_frac_ls 同量纲, 取值区间 [0,1] 的比例型 leave-one-out 均值)
formula: 银行 i 年 t 的工具值 = 同 bank_type 分组内所有同型同业 j≠i 该年 tech_frac_{lc,ls} 的简单均值 (leave-one-out, 排除 i 自身), 即标准 Bartik/同侪 LOO 构造 mean_{j∈g(i), j≠i} tech_frac_track(j,t); lag1 后缀取 t-1 年该 LOO 均值一阶滞后
producer: pipeline\panel\iv_extensions.py::compute_iv_extensions (步骤 8z) ; pipeline\panel\stata_export.py::HEURISTIC_LABELS
upstream:
- 40_panel_export_main (面板已含 tech_frac_lc / tech_frac_ls 逐行列)
citations:
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
- doi: "10.1257/aer.20181047"
  type: journal
  authors: "Goldsmith-Pinkham, P., Sorkin, I., & Swift, H."
  year: 2020
  title: "Bartik Instruments: What, When, Why, and How"
  venue: "American Economic Review"
  vol: "110"
  issue: "8"
  pages_or_artno: "2586-2624"
- doi: "10.1007/s11573-017-0852-x"
  type: journal
  authors: "Gomber, P., Koch, J.-A., & Siering, M."
  year: 2017
  title: "Digital Finance and FinTech: Current Research and Future Research Directions"
  venue: "Journal of Business Economics"
  vol: "87"
  issue: "5"
  pages_or_artno: "537-580"
- doi: "10.1093/restud/rdab030"
  type: journal
  authors: "Borusyak, K., Hull, P., & Jaravel, X."
  year: 2022
  title: "Quasi-Experimental Shift-Share Research Designs"
  venue: "The Review of Economic Studies"
  vol: "89"
  issue: "1"
  pages_or_artno: "181-213"
- doi: "10.1016/j.jfineco.2026.104274"
  type: "journal"
  authors: "Avramov, D., Ge, S., Li, S., & Linton, O."
  year: 2026
  title: "Dual peer effects and cross-stock predictability"
  venue: "Journal of Financial Economics"
  vol: "180"
  pages_or_artno: "104274"
- doi: "10.1016/j.pacfin.2025.102878"
  type: "journal"
  authors: "Ding, J., Huang, J., & Ding, A."
  year: 2025
  title: "The peer effects of corporate social responsibility in China: A pre-registered study"
  venue: "Pacific-Basin Finance Journal"
  vol: "94"
  pages_or_artno: "102878"
new_dois: []
---

## CORE

【构念与来源】
F433 属 P4 (bank_fintech_locus, Gomber 谱系) 识别策略工具变量族, 是同业 leave-one-out (LOO) 均值工具 leave_one_out_peer_locus_iv 家族在 ctx / ss 两条文本剪裁轨上的镜像补全。被工具化的内生解释变量是「创新落点」(innovation locus) 测度 tech_frac_lc / tech_frac_ls — 即银行年度报道中被 LLM 判定落在「底层技术/研发端」而非「应用端」的报道占比 (`n_articles_tech / n_articles_llm_valid`, 分类目标标签「底层技术」), 分别取自 ctx 轨 (标题+实体窗口剪裁文本) 与 ss 轨 (标题+银行∧金科同句共现窗口剪裁文本) 的三家 LLM 共识分类。四列均产自 `iv_extensions.py::compute_iv_extensions` 步骤 8z, 与 P4 主线 full 轨工具 `leave_one_out_peer_locus_iv`(_lag1) 严格镜像, 前缀改用紧凑 `lpeer_` 以规避 stata_export 32 字符截断歧义 (`_ss_lag1`=26 字符 < `_ctx_lag1`=27 字符, 两者均安全落在阈值内)。
构造逻辑遵循 Manski (1993) 反射问题的经典化解路径: 银行 i 自身的创新落点报道占比不能直接作银行媒体形象/合作模式等下游结果的工具, 因为同一媒体环境冲击 (行业景气、监管周期、金科热点轮动) 会同时驱动 i 与其结果变量, 违反排他性。同业 LOO 均值 (排除 i 自身, 仅取同 bank_type 分组内其余银行当年 tech_frac 均值) 切断了这条直接路径: 银行 i 自身特质性新闻不进入工具, 工具只反映「同型同业整体在报道叙事上的技术落点分布」, 该分布经由 Leary & Roberts (2014) 论证的同侪影响渠道 (媒体/分析师/监管对同类机构的叙事联动) 间接作用于银行 i 的媒体呈现, 而与银行 i 自身特质冲击正交 (在标准可交换性假设下)。这一 LOO 构造与 Bartik/shift-share 工具同属一个大家族 (Goldsmith-Pinkham, Sorkin & Swift 2020; Borusyak, Hull & Jaravel 2022 的份额-位移分解逻辑), 但此处「份额」退化为等权同侪均值而非地理/行业暴露份额, 是该谱系里最简约的版本。

【方法学与计算】
计算口径: 对每个 (bank_type, year) 分组, 取组内除银行 i 外全部银行的 tech_frac_track(j,t) 算术均值, 赋给银行 i 作为该年该轨工具值; `_lag1` 列在此基础上做逐银行按年份排序后的一阶滞后 (t-1 年工具值对齐到 t 年观测), 用于时间错位的稳健性设定或作滞后工具规避同期性担忧。ctx 轨与 ss 轨内生变量来源不同: `lpeer_locus_iv_ctx(_lag1)` 工具化 `tech_frac_lc` (ctx 轨, 标题+实体窗口剪裁文本上判定的「底层技术/研发端」报道占比), `lpeer_locus_iv_ss(_lag1)` 工具化 `tech_frac_ls` (ss 轨, 标题+银行∧金科同句共现窗口剪裁文本上判定的「底层技术/研发端」报道占比); 两轨与 P4 主线 full 轨工具 (工具化 full 轨 `tech_frac`/`innovation_locus_full` 衍生比例) 各自独立配对同轨内生变量, 不存在跨轨混用。ss 回退语义镜像 ctx: 若某文章无银行∧金科同句共现, `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 该回退是文章级剪裁口径, 传导至面板级 `tech_frac_ls` 的分子分母仍按 ss 轨自身口径统计, 不借用 ctx/full 分母, 因此本工具族在 ss 轨稀薄样本 (早期试跑 T=2 盘小样本尤甚) 下方差可能偏大, 属预期退化而非缺陷。
识别用法上, 三轨 (full/ctx/ss) 各自的 LOO 工具与其同轨内生变量构成【各自 just-identified、并排陈列】的三套 IV 设定, 是"互为稳健性、不分主次"的关系: 研究者应逐轨单独估计 2SLS/GMM 并比较系数符号与显著性的稳定性, 而不是把 full/ctx/ss 三轨 LOO 工具堆进同一个 over-identified 模型跑 Hansen J 检验。三轨剪裁窗口 (full=标题+全文, ctx=标题+实体窗口, ss=标题+银行金科同句窗口) 本质上是对同一批文章的三种不同截取方式, bank_type×year 层面的共同媒体冲击会以几乎相同的方式逐字污染三轨, 这使得任何两轨工具之间存在结构性近共线, 塞进同一 over-id 检验既无法为真正的外生性威胁提供有效功效, 反而会拖垮 Kleibergen-Paap rk Wald F 统计量、误导弱工具诊断的读数, 这与 Borusyak, Hull & Jaravel (2022) 对 shift-share 工具在共享暴露结构下诊断失真的告诫是同一类问题的不同表现形式。若确需做真正的 over-identification 检验, 正确路径是跨族组合 (例如把本 LOO 工具与结构完全不同的 Bartik 工具或 zone-LOO 工具搭配), 详见各 P4 2SLS 模板已内置的跨族 overid 列。
面板落点上, 四列均是 bank-year 层观测 (行数与 40_panel_yearly 主键一致), 缺失规则跟随所工具化内生变量的缺失规则: 若某 (bank_type, year) 分组内除自身外无其他银行有该轨有效 tech_frac 观测 (极端小样本分组, 如早期试跑 T=2 盘部分银行型别样本稀疏), LOO 均值退化为 NaN 而非虚假填 0, 避免向 2SLS 第一阶段引入系统性偏误; `_lag1` 列额外因缺 t-1 年观测 (面板首年) 而产生结构性缺失, 属滞后构造的固有特性。

【文献定位】
本工具族方法论谱系直接承袭 Manski (1993, The Review of Economic Studies) 对内生同侪效应识别问题 (「反射问题」) 的经典表述: 个体结果、个体特质与群体均值三者共线导致的不可分离性, 只能借助排他性工具或结构假设打破。Leary & Roberts (2014, The Journal of Finance) 将这一逻辑应用于公司金融情境, 用同业 LOO 均值工具企业政策的同侪效应, 是本工具族在应用层面最直接的先例, 本族沿用其"排除自身、取同组均值"的构造范式。Goldsmith-Pinkham, Sorkin & Swift (2020, American Economic Review) 与 Borusyak, Hull & Jaravel (2022, The Review of Economic Studies) 提供了 Bartik/shift-share 工具族的现代识别框架与诊断标准 (份额外生性、暴露异质性的可检验含义), 本族虽在构造上更简约 (等权同侪均值而非份额加权位移), 但共享"用群体层面的结构性变异隔离个体内生冲击"的核心思想, 引用二者是为了在识别策略讨论中把本工具明确定位为该谱系的简化特例, 并借用其诊断建议 (第一阶段 F 统计量、工具相关性的组间异质性检验)。内生变量的实质构念 — 创新落点二分 (技术研发端 vs 应用端) — 源自 Gomber, Koch & Siering (2017, Journal of Business Economics) 对数字金融/金融科技研究方向的分类框架, 该文是 P4 论文 (bank_fintech_locus) 构念定义的直接出处, 本工具族的存在意义正是为该构念提供 ctx/ss 双轨的因果识别配套。 同侪暴露测度族在近年的前沿存续亦可为本族定位提供参照: Avramov、Ge、Li 与 Linton (2026) 在 Journal of Financial Economics 构造股票间的同侪连接矩阵并度量同侪特征向自身的溢出, 属典型的「以 (加权) 同侪均值作为暴露变量」设定, 与本族在同 bank_type 分组内取等权 leave-one-out 均值同属一个测度族, 可作该族在顶级金融期刊的最新应用存在性证明; 但其同侪连接基于股票收益/特征的经济联系, 被加权的量是收益或特征、DV 是横截面收益的可预测性, 与本族按 bank_type×year 分组、被平均量为 tech_frac_lc / tech_frac_ls、层级为银行-年的设定在单位与对象上均不同, 该文亦未讨论把同侪均值转用作工具变量的合法性, 故只锚定测度族而非本族的识别论证。Ding、Huang 与 Ding (2025) 则以预注册设计考察中国语境下企业社会责任的同侪效应, 用 OLS 验证假设并辅以工具变量法缓解内生性威胁, 提出市场竞争与制度压力两条机制, 为「同侪暴露变量 + IV 缓解反射性与内生性」这一识别范式在中国情境下的可信性提供了近期参考; 惟该文同侪暴露变量的具体构造 (分组维度、是否为组内 leave-one-out 均值) 与其工具的具体形式均未在可得摘要中披露, 故此处只锚定该识别范式的存在与可信性, 不得据以主张其与本族 mean_(j∈g(i), j≠i) 的构造同形, 其被平均的是 CSR 表现而非 LLM 判定的技术落点报道占比, 亦未设本族 lag1 一阶滞后臂那样的时间错位设定。
## VAR: lpeer_locus_iv_ctx

【变体差分】
本列工具化 ctx 轨内生变量 `tech_frac_lc` (标题+实体窗口剪裁文本上判定的「底层技术/研发端」创新落点占比), 是与主线 full 轨 `leave_one_out_peer_locus_iv` 结构完全一致的镜像工具, 差异只在于内生变量所依赖的文章剪裁窗口: ctx 轨仅保留标题与目标实体 (银行/金科词) 周边窗口文本, 剔除全文中与银行-金科关系无关的段落, 因此该轨判定的"落点"更聚焦于文章明确提及银行与金科技术交集的局部语境, 相比 full 轨(标题+全文)对无关段落噪声的稀释更小, 判定噪声理论上更低但样本覆盖 (含 `ctx_is_fallback` 触发的降级) 略窄于 full 轨。作为工具变量, `lpeer_locus_iv_ctx` 与同期 ctx 轨内生变量配对使用, 属于 P4 三轨识别设定中的一支, 与 full 轨、ss 轨工具各自 just-identified 并排, 三者互为稳健性、不分主次, 不得混入同一 over-identified 模型联合估计或跑 Hansen J — 三轨对同批文章的不同剪裁窗口共享 bank_type×year 层面的媒体冲击, 强行拼装只会拖垮弱工具诊断而非提供有效的过度识别信息。计算时严格排除银行自身 (leave-one-out), 分组键为 bank_type×year: 若某年某 bank_type 分组内除自身外无其他银行留有 ctx 轨有效 `tech_frac_lc` 观测, 该行本列即置为缺失而非人为填零, 以避免向下游第一阶段回归引入系统性偏误。使用者若需在 P4 复现包内比较 full/ctx 两轨第一阶段强度, 应分别单独跑弱工具 F 检验, 而非直接堆叠系数。

## VAR: lpeer_locus_iv_ctx_lag1

【变体差分】
在 `lpeer_locus_iv_ctx` 基础上取逐银行按年份序列的一阶滞后 (t-1 年工具值对齐 t 年观测), 用于需要工具与内生变量、结果变量之间保持时间错位的设定 (例如规避同期媒体冲击同时驱动工具与结果的担忧, 或作为额外的过度识别稳健性检验的候选工具, 但仍需遵守【禁止跨轨混入同一 Hansen J】的家族铁律, 只应与其他滞后一期或同期的 ctx 轨变量配对, 不得与 full 轨/ss 轨的同期或滞后工具混装进单一 over-identified 模型)。构造上仍是同 bank_type×year 分组、排除自身的 leave-one-out 均值, 唯一区别是取值对齐到面板行的年份索引减一; 面板首年因无 t-1 观测而产生结构性缺失, 该缺失是滞后构造的固有属性而非数据质量问题, 使用该列做 2SLS 前须先用 `xtset` 确认面板年份连续、避免非连续年份下滞后错位。早期试跑 T=2 盘上该列的有效值仅覆盖面板第二年, 生产 T=19 全量语料上该列覆盖率将随面板深度显著提升, 属预期的该盘退化而非实现缺陷。在识别策略叙事中, 滞后一期工具常被用作"预先确定" (predetermined) 工具的稳健性佐证: 若同期工具与滞后工具在第一阶段与结构方程中给出方向一致的估计, 有助于缓解审稿人对同期性/反向因果的质疑, 但这属于同一 ctx 轨内部的稳健性组合, 不改变四列各自 just-identified 并排的基本地位。

## VAR: lpeer_locus_iv_ss

【变体差分】
本列工具化 ss 轨内生变量 `tech_frac_ls` (标题+银行∧金科词同句共现窗口剪裁文本上判定的「底层技术/研发端」创新落点占比), 是 ctx 轨镜像工具在更严格剪裁口径下的对应版本。ss 轨要求银行实体与金科关键词在同一句 (±N 句窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 内共现才纳入该窗口, 若某文章无此类同句共现, 则 `content_ss` 回退为全文 body 且标记 `ss_is_fallback=True` (回退语义镜像 ctx 轨的降级规则: 无共现不等于剔除文章, 而是退化为等同 full 轨的宽窗口, 同时保留标记供下游区分); 该回退发生在文章级, 传导至本工具的面板级构造时, 面板分母 `n_articles_llm_valid_ss` 已自洽包含回退文章, 工具本身不额外处理回退标记, 只对 ss 轨 `tech_frac_ls` 做同 bank_type×year 分组内的 leave-one-out 均值, 计算规则与 ctx/full 轨完全一致, 仅内生变量来源轨不同。作为 P4 三轨识别设定的第三支, 与 full/ctx 轨工具并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验, 也不应把 ss 轨工具单独当作"更严谨因而优先"的主工具 — 三轨在识别策略上地位平等, 差异只在文本剪裁窗口的宽严。因 ss 轨判据比 ctx 更严 (同句 vs 实体窗口), 小样本 (如早期试跑 T=2 盘) 下该列及其滞后列比 ctx 轨更容易出现同组内有效同业过少导致的 LOO 均值缺失, 属预期的判据收紧代价而非缺陷, 在生产 T=19 全量语料上该缺失率预期显著收窄。

## VAR: lpeer_locus_iv_ss_lag1

【变体差分】
在 `lpeer_locus_iv_ss` 基础上取一阶滞后 (t-1 年对齐 t 年), 与 `lpeer_locus_iv_ctx_lag1` 是同一构造逻辑在 ss 轨上的镜像: 同 bank_type×year 分组、排除自身的 leave-one-out 均值先算出逐年工具值, 再按银行分组做年份序列一阶滞后, 面板首年同样因无 t-1 观测而结构性缺失。四列中本列字符长度最短 (`_ss_lag1` 后缀 26 字符, 短于 `_ctx_lag1` 的 27 字符), 这是命名前缀刻意收窄为 `lpeer_` (而非主线 `leave_one_out_peer_`) 的直接动因之一, 目的是把 ctx/ss 两轨全部滞后列名压在 Stata 32 字符变量名硬上限之内, 避免 stata_export 阶段因截断产生的列名歧义 (两个不同变量截断后若恰好撞名, 会在 .dta 导出时静默覆盖其中一列, 该风险正是本紧凑前缀存在的直接原因)。使用时须与 ss 轨滞后一期的内生变量/结果变量配对, 且仍受【禁止跨轨混入同一 Hansen J】家族铁律约束; 因叠加了 ss 判据收紧与滞后缺失双重收窄, 本列在四列中预期缺失率最高, 小样本面板 (如早期试跑 T=2 盘) 上应对第一阶段强度做单独检验后再决定是否采用。与 `lpeer_locus_iv_ctx_lag1` 的关系是横向并列而非纵向替代: 二者分别锚定 ctx/ss 两种剪裁窗口下的滞后同侪工具, 论文正文若同时报告两轨滞后结果, 应作为并列稳健性表格呈现, 而不应在同一回归式内同时纳入两者充当过度识别工具组合, 理由同样是三轨/两轨底层共享同一批文章的媒体冲击结构, 拼装无法提供有效的额外识别信息。

<!-- rendered-citations:begin -->
Manski, C. F. (1993). Identification of Endogenous Social Effects: The Reflection Problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Leary, M. T., & Roberts, M. R. (2014). Do Peer Firms Affect Corporate Financial Policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik Instruments: What, When, Why, and How. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital Finance and FinTech: Current Research and Future Research Directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-Experimental Shift-Share Research Designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Avramov, D., Ge, S., Li, S., & Linton, O. (2026). Dual peer effects and cross-stock predictability. Journal of Financial Economics, 180, 104274. https://doi.org/10.1016/j.jfineco.2026.104274
Ding, J., Huang, J., & Ding, A. (2025). The peer effects of corporate social responsibility in China: A pre-registered study. Pacific-Basin Finance Journal, 94, 102878. https://doi.org/10.1016/j.pacfin.2025.102878
<!-- rendered-citations:end -->
</content>
</invoke>
