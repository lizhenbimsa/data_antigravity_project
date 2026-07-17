---
family_id: F102
columns:
- bartik_fintech_lc_share_app
- bartik_fintech_lc_share_tech
unit: 基期类别份额 (base-period category share, 无量纲比例, 银行内跨两类别归一化和为一)
formula: "bartik_fintech_lc_share_c = (基期窗口内该银行归入 fintech 类别 c 的报道注意力) / (基期窗口内该银行两类别报道注意力之和); c ∈ {tech, app}, 类别归属由 innovation_locus_ctx 轨判定 (lc = locus-ctx); 该基期份额是 shift-share (Bartik) 工具变量的 share 分量, 与全国层面各类别的时序冲击 (shift) 交互后生成 bartik_fintech_lc_iv_{full,ctx}"
producer: news_process/pipeline/panel/iv_did.py::compute_bartik_iv_fintech (runner.py 仅 import 并调用; 列标签在 pipeline/panel/export.py)
upstream:
- 21_tone_llms.parquet (innovation_locus_ctx 类别判定, LLM 分类产出)
- 40_panel_yearly.parquet (银行-年注意力聚合与基期窗口切片)
citations:
- doi: 10.1016/j.jfineco.2024.103950
  type: journal
  authors: Babina, T., Bahaj, S., Buchak, G., De Marco, F., Foulis, A., Gornall, W., Mazzola, F., & Yu, T.
  year: 2025
  title: "Customer data access and fintech entry: Early evidence from open banking"
  venue: Journal of Financial Economics
  vol: 169
  pages_or_artno: 103950
- doi: 10.1016/j.jfineco.2024.103957
  type: journal
  authors: Vives, X., & Ye, Z.
  year: 2025
  title: "Information technology and lender competition"
  venue: Journal of Financial Economics
  vol: 163
  pages_or_artno: 103957
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.1093/rfs/hhy130
  type: journal
  authors: Chen, M. A., Wu, Q., & Yang, B.
  year: 2019
  title: "How valuable is FinTech innovation?"
  venue: Review of Financial Studies
  vol: 32
  issue: 5
  pages_or_artno: 2062-2106
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: Journal of Business Economics
  vol: 87
  issue: 5
  pages_or_artno: 537-580
- doi: "10.1257/jep.20231370"
  type: journal
  authors: "Borusyak, K., Hull, P., & Jaravel, X."
  year: 2025
  title: "A Practical Guide to Shift-Share Instruments"
  venue: "Journal of Economic Perspectives"
- doi: "10.1017/s0022109023000698"
  type: journal
  authors: "Chu, Y., & Wei, J."
  year: 2023
  title: "Fintech Lending and Credit Market Competition"
  venue: "Journal of Financial and Quantitative Analysis"
- doi: "10.1016/j.intfin.2026.102306"
  title: "Investing in fintech equity and bank innovation"
  authors: "Alfhaili, F. A., Bakoush, M., & Wolfe, S."
  year: 2026
  venue: "Journal of International Financial Markets, Institutions and Money"
  type: "journal"
- doi: "10.1016/j.jfs.2024.101230"
  title: "The role of banks' technology adoption in credit markets during the pandemic"
  authors: "Branzoli, N., Rainone, E., & Supino, I."
  year: 2024
  venue: "Journal of Financial Stability"
  type: "journal"
new_dois:
  - "10.1257/jep.20231370"
  - "10.1017/s0022109023000698"
  - "10.1016/j.intfin.2026.102306"
  - "10.1016/j.jfs.2024.101230"
---

## CORE

【构念与来源】
本家族刻画的是 shift-share (Bartik) 工具变量构造中的 share 分量, 即每家银行在基期窗口内金融科技报道注意力沿"金融科技类别"维度的份额分布。金融科技类别维度按创新落点 (innovation locus) 二分为技术类 (Technology) 与应用类 (Application) 两类: 技术类指报道所涉金融科技创新的落点在底层技术能力本身 (如算法、数据基础设施、模型), 应用类指创新落点在面向业务与客户的场景应用 (如支付、信贷、财富管理界面)。这一二分承袭 Gomber, Koch 与 Siering (2017) 对数字金融研究谱系的落点式梳理, 以及 Gomber, Kauffman, Parker 与 Weber (2018) 对金融科技创新—颠覆—转型三重力量的结构化区分。家族键名中的 lc 表示类别归属由 innovation_locus_ctx 轨 (ctx 轨落点判定) 给出, 与之孪生的另一套 lf (locus-full, 由 innovation_locus_full 轨判定) 在导出层并列存在, 两套构成互为稳健性、不分主次的并排轨: 各自 just-identified 单独进入其自身的 2SLS 识别式, 严禁把 lc 与 lf 两套 share 混进同一 over-identified Hansen J 过度识别检验 (与三轨 full/ctx/ss 及 co-primary 双轨嵌入的铁律同源)。

【方法学与计算】
shift-share 工具的一般形式为: 银行层暴露 = Σ_c (基期份额_bc × 全国冲击_ct)。本家族提供的正是其中的基期份额_bc 这一横截面权重: 对给定银行 b, 在基期窗口 (t0, 生产口径为面板首期或指定的预处理基期切片) 内统计其被归入技术类与应用类的金融科技报道注意力, 再以两类之和为分母做银行内归一化, 得到 bartik_fintech_lc_share_tech 与 bartik_fintech_lc_share_app 两列; 二者在同一银行内互补, 理论上相加为一 (当两类注意力皆非缺失时)。这套基期份额此后与全国层面各类别的时序增长冲击交互, 生成同族的工具列 bartik_fintech_lc_iv_full 与 bartik_fintech_lc_iv_ctx (工具列后缀 full/ctx 指冲击侧的情感/注意力轨, 与 share 侧的 locus 轨是两个独立后缀轴, 不可混淆)。之所以采用基期份额而非同期份额, 是 Bartik 设计外生性的要害: 份额锁定在处理前的基期以隔断反向因果, 使横截面暴露的差异不被同期结果污染。银行的报道注意力口径与全流程一致遵循 full-only 留篇门控 (2026-06-29): 一篇报道是否计入银行金融科技注意力总量由 llm_verified_full 判定, ctx/ss 在此仅作条件化于 full 的测度轨; 因此 lc share 的分母虽由 locus-ctx 轨给出类别切分, 其纳入的报道宇宙仍是 full 门控留篇集的子集。

【文献定位】
在识别方法层面, 本家族的推断有效性以 Adão, Kolesár 与 Morales (2019) 对 shift-share 设计的理论与推断框架为规范锚: 该文指出份额型 Bartik 工具的标准误须考虑同暴露单元间的相关结构, 否则会系统性低估, 这一警示直接约束下游 2SLS 的方差估计口径。在构念的经济内涵层面, 金融科技创新的可度量性与其价值含义由 Chen, Wu 与 Yang (2019) 在顶级金融学证据中确立, 支撑了以报道注意力沿创新落点分布来刻画银行金融科技暴露的合理性。类别二分的理论来源前已述及 Gomber 等 (2017, 2018) 的落点谱系。就工具所服务的实证问题——银行金融科技暴露如何影响其竞争与信贷行为——近期证据如 Vives 与 Ye (2025) 关于信息技术与放贷者竞争、Babina 等 (2025) 关于开放银行下客户数据可得性与金融科技进入的研究, 说明技术侧与应用侧暴露对银行的作用机制可能异质, 这正是保留 tech/app 两类分维份额、而非仅用合并暴露的动机所在。需强调本家族两列本身是工具的构造中间量 (基期权重), 不是结果变量, 其解读须置于 shift-share 识别链条整体之中。就 shift-share 工具的推断规范而言, Borusyak, Hull 与 Jaravel (2025, Journal of Economic Perspectives) 系统梳理了两条并行的识别路径 (多外生冲击 vs 外生份额) 及其配套的推断实践指南, 为本家族基期份额分量的识别有效性与标准误口径提供了最新方法学规范; 就工具所服务的竞争传导机制而言, Chu 与 Wei (2023, Journal of Financial and Quantitative Analysis) 用竞争模型刻画金融科技借贷者与传统银行在信息与技术上的差异化竞争, 为本家族按技术类/应用类二分刻画银行金融科技暴露的异质传导路径提供了理论与实证支撑。银行对金融科技股权投资的研究发现, 当标的属于面向客户的 fin-native (支付/信贷) 而非底层技术的 tech-native (数据分析/监管科技) 时, 对银行创新能力的提升效应更强, 为技术类/应用类二分的异质传导路径提供了2026年新证据 (Alfhaili, Bakoush, & Wolfe, 2026, Journal of International Financial Markets, Institutions and Money)。利用银行IT支出异质性度量技术采纳程度并考察其对信贷扩张的因果作用, 为本家族以银行金融科技报道注意力度量技术类暴露的实证策略提供了方法参照 (Branzoli, Rainone, & Supino, 2024, Journal of Financial Stability)。

## VAR: bartik_fintech_lc_share_app

【变体差分】
本列是应用类 (Application) 基期份额: 在基期窗口内, 该银行金融科技报道中被 innovation_locus_ctx 轨判定为创新落点在业务/客户应用场景 (支付、信贷投放界面、财富管理、场景化金融服务等) 的注意力, 除以该银行技术类与应用类注意力之和。相对家族 canonical 语义, 本列的差分维度有三: 其一是类别轴取"应用"侧 (与同族 tech 列互补, 同一银行内两列理论上相加为一, 当两类皆非缺失时); 其二是落点判定轨为 locus-ctx (lc), 即类别归属来自 innovation_locus_ctx 而非孪生的 innovation_locus_full (lf 套), lc 与 lf 两套互为稳健性、不分主次, 各自 just-identified 单独进其 2SLS 识别式, 严禁把 lc 与 lf 的 share 混进同一 over-identified Hansen J; 其三是本列属 share 分量 (基期横截面权重), 与同族 iv 列 (share 与全国冲击交互后的最终工具) 分工不同, 不可互相替代。应用侧暴露的经济含义偏向面向客户的金融科技扩张, 与技术侧 (底层能力) 的传导路径可能异质, 故须与 tech 列并保而非合并。基期份额的处理前锁定是其外生性要害: 应用类份额固定在基期切片, 隔断同期银行绩效对暴露度量的反向污染, 使横截面暴露差异可作为工具的合法 share 权重。报道纳入宇宙仍受 full-only 留篇门控约束, 分母只统计 full 门控留篇集内、经 locus-ctx 归入两类的注意力。

## VAR: bartik_fintech_lc_share_tech

【变体差分】
本列是技术类 (Technology) 基期份额: 在基期窗口内, 该银行金融科技报道中被 innovation_locus_ctx 轨判定为创新落点在底层技术能力 (算法、大数据与数据基础设施、人工智能模型、分布式账本等技术层) 的注意力, 除以该银行技术类与应用类注意力之和。相对家族 canonical 语义, 本列差分维度与同族 app 列镜像对称、方向相反: 其一是类别轴取"技术"侧 (与 app 列互补, 同一银行内两列理论上相加为一, 当两类皆非缺失时); 其二是落点判定轨同为 locus-ctx (lc), 类别归属来自 innovation_locus_ctx 而非孪生 lf 套, lc 与 lf 互为稳健性、不分主次, 各自 just-identified 并排单独进 2SLS, 严禁把两套 share 混进同一 over-identified Hansen J; 其三是本列同属 share 分量 (基期横截面权重), 服务于与全国技术类冲击交互生成同族 iv 列, 不与 iv 列互替。技术侧暴露刻画银行对金融科技底层能力构建的报道显著度, 其对成本、竞争与信贷的传导路径, 依 Vives 与 Ye (2025) 及 Babina 等 (2025) 的证据, 可能不同于应用侧, 这构成保留双类分维份额的实证动机。基期锁定与 full-only 门控口径与 app 列一致: 技术类份额固定在处理前基期切片以保外生性, 分母只纳入 full 留篇集内经 locus-ctx 归为两类的报道注意力。

<!-- rendered-citations:begin -->
Babina, T., Bahaj, S., Buchak, G., De Marco, F., Foulis, A., Gornall, W., Mazzola, F., & Yu, T. (2025). Customer data access and fintech entry: Early evidence from open banking. Journal of Financial Economics, 169, 103950. https://doi.org/10.1016/j.jfineco.2024.103950
Vives, X., & Ye, Z. (2025). Information technology and lender competition. Journal of Financial Economics, 163, 103957. https://doi.org/10.1016/j.jfineco.2024.103957
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Chen, M. A., Wu, Q., & Yang, B. (2019). How valuable is FinTech innovation? Review of Financial Studies, 32(5), 2062-2106. https://doi.org/10.1093/rfs/hhy130
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Borusyak, K., Hull, P., & Jaravel, X. (2025). A Practical Guide to Shift-Share Instruments. Journal of Economic Perspectives. https://doi.org/10.1257/jep.20231370
Chu, Y., & Wei, J. (2023). Fintech Lending and Credit Market Competition. Journal of Financial and Quantitative Analysis. https://doi.org/10.1017/s0022109023000698
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. Journal of International Financial Markets, Institutions and Money. https://doi.org/10.1016/j.intfin.2026.102306
Branzoli, N., Rainone, E., & Supino, I. (2024). The role of banks' technology adoption in credit markets during the pandemic. Journal of Financial Stability. https://doi.org/10.1016/j.jfs.2024.101230
<!-- rendered-citations:end -->
