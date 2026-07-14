---
family_id: F186
columns:
- depins_post
unit: 二值时间指示变量 (0/1 dummy, 无量纲)
formula: "depins_post = 1[year >= 2015]; 即样本年份不早于 2015 年记 1, 否则记 0 (《存款保险条例》2015-05-01 全国统一施行断点)"
producer: news_process/pipeline/panel/runner.py (步骤 7g-het 异质性交互段, aggregate_panel 之后于银行-年度面板上机械派生)
upstream:
  - 24_herd_decay.parquet (df_exploded → aggregate_panel 提供 year 列)
  - 40_panel_yearly.parquet (depins_post 与 tone_x_depins_{full,ctx,ss} 一并落盘)
citations:
- doi: 10.1257/jel.20251650
  type: journal
  authors: Baker, A., Callaway, B., Cunningham, S., Goodman-Bacon, A., & Sant'Anna, P. H. C.
  year: 2026
  title: "Difference-in-differences designs: A practitioner's guide"
  venue: Journal of Economic Literature
  vol: 64
  issue: 2
  pages_or_artno: 498-557
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics and Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2022.01.004
  type: journal
  authors: Baker, A. C., Larcker, D. F., & Wang, C. C. Y.
  year: 2022
  title: "How much should we trust staggered difference-in-differences estimates?"
  venue: Journal of Financial Economics
  vol: 144
  issue: 2
  pages_or_artno: 370-395
- doi: 10.1080/1351847x.2020.1805782
  type: journal
  authors: Wang, R., Liu, J., & Luo, H.
  year: 2021
  title: "Fintech development and bank risk taking in China"
  venue: The European Journal of Finance
  vol: 27
  issue: 4-5
  pages_or_artno: 397-418
- doi: 10.1016/j.jeconom.2020.12.001
  type: journal
  authors: Callaway, B., & Sant'Anna, P. H. C.
  year: 2021
  title: "Difference-in-differences with multiple time periods"
  venue: Journal of Econometrics
  vol: 225
  issue: 2
  pages_or_artno: 200-230
- doi: 10.1016/j.jeconom.2021.03.014
  type: journal
  authors: Goodman-Bacon, A.
  year: 2021
  title: "Difference-in-differences with variation in treatment timing"
  venue: Journal of Econometrics
  vol: 225
  issue: 2
  pages_or_artno: 254-277
- doi: 10.1257/aer.20181169
  type: journal
  authors: de Chaisemartin, C., & D'Haultfœuille, X.
  year: 2020
  title: "Two-way fixed effects estimators with heterogeneous treatment effects"
  venue: American Economic Review
  vol: 110
  issue: 9
  pages_or_artno: 2964-2996
- doi: "10.1007/s10693-024-00431-z"
  type: journal
  authors: "Zhou, X., Li, X., Zhou, Y., & Kara, A."
  year: 2024
  title: "Deposit Insurance and Bank Liquidity Creation: Evidence from a Natural Experiment in China"
  venue: "Journal of Financial Services Research"
- doi: "10.1080/00036846.2025.2504204"
  type: journal
  authors: "Moudud-Ul-Huq, S., Hossain, M., Rahman, S., Ullah, H., Adesina, O. O., & Rashid, M."
  year: 2025
  title: "Effects of monetary policy and deposit insurance on financial policy: Does ownership structure matter? Evidence from Chinese banks"
  venue: "Applied Economics"
new_dois:
  - "10.1007/s10693-024-00431-z"
  - "10.1080/00036846.2025.2504204"
---

## CORE

【构念与来源】
depins_post 是一个二值时间指示变量 (0/1 哑变量), 用来标记某个银行-年度观测是否落在中国存款保险制度正式施行之后的时期。构念的制度来源是国务院令第 660 号《存款保险条例》, 该条例于 2015 年 5 月 1 日在全国范围内统一施行, 自此中国从长期以来对银行存款的隐性国家兜底转向显性、有限额 (单一存款人本息合计最高偿付人民币 50 万元) 的存款保险安排。派生规则极为简单透明: 只要样本年份不早于 2015 年 (year >= 2015) 即赋值 1, 否则赋值 0。生产口径见 pipeline/panel/runner.py 步骤 7g-het 异质性交互段, 在 aggregate_panel 把 article×bank 级记录压成银行-年度面板之后, 直接对面板的 year 列做阈值比较 panel['year'] >= 2015 并转 int, 不涉及任何银行侧、省份侧或情感侧信息, 因此它是一条纯粹的日历时间断点列, 对同一年份的所有银行取值恒相同。

【方法学与计算】
需要特别强调的是, depins_post 在本流水线中被刻意设计为时间断点调节项 (temporal breakpoint modulator), 而不是标准的双重差分处理变量。原因写在生产代码注释里: 存款保险是全国统一实施的制度, 不存在受影响组与未受影响组的横截面划分, 也就没有可供 DID 识别的处理/控制分组; 因此它绝不通过 policy_shocks.json 的省份匹配通道实现 (merge_policy_shocks 依赖 panel['bank_province'].isin(provs) 做省份命中, 而"全国"不是任何有效省份名, 强行走该通道只会全部落空)。它的实际用途是作为调节变量进入交互项: 流水线在同一段代码里对三轨情感主测度 llm_vote_tone_{full,ctx,ss} 逐轨乘以 depins_post, 派生出 tone_x_depins_{full,ctx,ss} 三个交互列, 用于检验新闻语调对银行结果的作用是否在存款保险施行前后发生结构性变化 (例如显性存款保险削弱储户对负面新闻的挤兑式反应、从而改变语调传导强度)。这里的三轨 full/ctx/ss 遵循全仓一致的口径: 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨的交互项混进同一个 over-identified 的 Hansen J 过度识别检验; full 轨对应标题 prepend 后的全文正文, ctx 轨为标题加实体窗口, ss 轨为标题加银行与金融科技同句共现窗 (其回退语义镜像 ctx, 无同句共现时退回全文 body)。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入银行金融科技样本只看 full 轨的 llm_verified 结果, ctx/ss 是 conditional-on-full 的从属测度, 因此三条交互列的行宇宙是 full 留篇集的一致子集, 每轨列各自照算而不互相借分母。代码内还带有一条零方差守卫: 当面板年份未跨越 2015 断点时 (盘面 T=2 dev 数据仅含 2017、2018, 两者皆 >= 2015, depins_post 恒为常量 1), tone_x_depins* 退化为 tone×1 无识别力, 会被下游共线性与固定效应吸收, 代码以 WARNING 显式提示以免被误读为可用断点; 生产全量 T=18 (2007–2024) 天然跨越 2015 断点后方差自然恢复, 守卫不再触发。

【文献定位】
depins_post 的构念意义要放在两条文献脉络里理解。第一条是存款保险与银行风险、存款稳定性的制度经济学脉络: Fang et al. (2024) 在《International Review of Economics and Finance》上以中国样本直接研究媒体情绪、存款稳定性与银行系统性风险的联动, 表明媒体语调对存款行为的影响会被存款保险这类制度安排调节, 这正是本变量作为调节项检验语调传导的直接理论依据; Wang et al. (2021) 关于中国金融科技发展与银行风险承担的证据, 则从道德风险与风险承担角度提示显性存款保险可能改变银行与储户的行为均衡, 使得同一制度断点在不同风险环境下具有异质含义。第二条是断点识别方法学脉络: 尽管本变量被定义为时间调节项而非 DID 处理变量, 但凡涉及"施行前后"对比的识别都须警惕近年双重差分文献揭示的陷阱。de Chaisemartin & D'Haultfœuille (2020, AER) 与 Goodman-Bacon (2021) 指出交错处理时点下双向固定效应估计量会因"坏比较组"产生负权重偏误; Callaway & Sant'Anna (2021) 给出多期分组处理下的稳健估计框架; Baker, Larcker & Wang (2022, JFE) 在金融场景中系统展示了交错 DID 的偏误规模; Baker et al. (2026) 发表于《Journal of Economic Literature》的实务指南则汇总了这一整套现代 DID 诊断与估计工具。由于本变量是全国统一时点、无横截面处理分组的纯时间断点, 它在实证中只能进入交互调节而不能独立承担因果识别, 上述方法学文献恰恰解释了为何生产代码要把它与省份级 policy_shocks 严格分开处理——避免把一个日历哑变量误当作可识别的处理时点。此外, Zhou, Li, Zhou, & Kara (2024, Journal of Financial Services Research) 利用中国2015年存款保险制度施行这一自然实验, 检验其对银行流动性创造的因果影响, 为 depins_post 断点的制度背景提供直接的自然实验证据; Moudud-Ul-Huq, Hossain, Rahman, Ullah, Adesina, & Rashid (2025, Applied Economics) 考察货币政策与存款保险制度对中国银行财务政策的联合影响并检验所有权结构的调节作用, 支持将 depins_post 作为调节变量而非独立处理变量的建模选择。

## VAR: depins_post

【变体差分】
本家族为单列家族, depins_post 即家族的 canonical 列, 无三轨后缀、无模型后缀、无阈值或权重梯子变体, 因此它与"家族 canonical"的差分体现在它相对于流水线内其他时间/制度断点哑变量的精确定位, 而非同族兄弟列之间的口径差异。其唯一定义边界是日历阈值 year >= 2015, 对应《存款保险条例》2015-05-01 全国统一施行, 取值粒度是年度 (非月度), 因此 2015 全年被整体归入施行后即使条例在当年 5 月才生效——这是年度面板粒度下的刻意近似, 使用者在解读 2015 年观测时应知晓其为部分年度处理。须与之明确区分的相邻断点列有二: 其一是 stress_period, 定义为 year ∈ {2015, 2018, 2020} (股灾、去杠杆、疫情三个银行业压力年), 是离散的多点压力指示而非单调递增的施行后哑变量, 两者虽在 2015 年重叠取值 1, 但语义完全不同 (stress_period 刻画非对称压力窗口, depins_post 刻画一次性制度切换); 其二是 digital_frontier 及 DCEP/Sandbox 政策冲击列, 后者走 policy_shocks.json 的省份匹配通道并可进入真正的 DID/DDD 结构, 而 depins_post 因全国统一实施刻意不走该通道、只作时间调节。depins_post 本身不进入任何 over-identified Hansen J, 它派生的三条交互项 tone_x_depins_{full,ctx,ss} 遵循三轨铁律各自 just-identified 并排、互为稳健性、不分主次、禁混同一过度识别检验。使用注意: 在样本年份未跨越 2015 断点的子样本 (如 T=2 dev 面板 {2017,2018}) 中该列退化为常量, 交互项零方差无识别力, 生产 T=18 (2007–2024) 跨断点后方差恢复, 解读回归系数前须先确认样本年份确实横跨 2015。

<!-- rendered-citations:begin -->
Baker, A., Callaway, B., Cunningham, S., Goodman-Bacon, A., & Sant'Anna, P. H. C. (2026). Difference-in-differences designs: A practitioner's guide. Journal of Economic Literature, 64(2), 498-557. https://doi.org/10.1257/jel.20251650
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics and Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Baker, A. C., Larcker, D. F., & Wang, C. C. Y. (2022). How much should we trust staggered difference-in-differences estimates?. Journal of Financial Economics, 144(2), 370-395. https://doi.org/10.1016/j.jfineco.2022.01.004
Wang, R., Liu, J., & Luo, H. (2021). Fintech development and bank risk taking in China. The European Journal of Finance, 27(4-5), 397-418. https://doi.org/10.1080/1351847x.2020.1805782
Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. Journal of Econometrics, 225(2), 200-230. https://doi.org/10.1016/j.jeconom.2020.12.001
Goodman-Bacon, A. (2021). Difference-in-differences with variation in treatment timing. Journal of Econometrics, 225(2), 254-277. https://doi.org/10.1016/j.jeconom.2021.03.014
de Chaisemartin, C., & D'Haultfœuille, X. (2020). Two-way fixed effects estimators with heterogeneous treatment effects. American Economic Review, 110(9), 2964-2996. https://doi.org/10.1257/aer.20181169
Zhou, X., Li, X., Zhou, Y., & Kara, A. (2024). Deposit Insurance and Bank Liquidity Creation: Evidence from a Natural Experiment in China. Journal of Financial Services Research. https://doi.org/10.1007/s10693-024-00431-z
Moudud-Ul-Huq, S., Hossain, M., Rahman, S., Ullah, H., Adesina, O. O., & Rashid, M. (2025). Effects of monetary policy and deposit insurance on financial policy: Does ownership structure matter? Evidence from Chinese banks. Applied Economics. https://doi.org/10.1080/00036846.2025.2504204
<!-- rendered-citations:end -->
