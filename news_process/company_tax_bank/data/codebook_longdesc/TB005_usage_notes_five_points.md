---
family_id: TB005
novelty_exempt_rationale: "该家族是使用注意事项五要点的规范披露, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- cw_X_t_usage_note
- cluster_bank_undefined
- ppml_recommendation
- three_track_no_monotone
- weight_endogeneity_note
unit: 无量纲 (使用规范说明段, 非独立数值列)
formula: "exposure-robust SE 建议 + cluster(bank)未定义警示 + PPML/ln(1+x)计数列建模建议 + 三轨禁单调断言 + 权重内生性对照臂说明, 五条并列, 不构成单一公式"
producer: company_tax_bank/pipeline/02_build_cooc_panel.py (codebook §③ 使用要点段生成分支)
upstream:
- company_tax_bank_cooc_panel.dta/parquet (企业乘年主面板, 使用规范的适用对象)
- _company_tax_bank_altweights_branch_city.parquet / _branch_county.parquet (权重内生性对照臂来源)
citations:
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: The Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.3982/ECTA19367
  type: journal
  authors: Borusyak, K., & Hull, P.
  year: 2023
  title: "Nonrandom exposure to exogenous shocks"
  venue: Econometrica
  vol: 91
  issue: 6
  pages_or_artno: 2155-2185
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
---

## VAR

本条目独立完整复述税调企业银企共现面板供分析端遵循的五条使用规范, 五条彼此独立、并列生效, 共同回应加权测度构造中最容易被误用的五个环节。第一条是推断层面的规范: cw 系列加权测度在结构上是共现份额乘银行侧测度的份额加权设计, 与经典的份额加权工具变量识别结构高度同构, 这意味着共享同一家银行冲击的不同企业之间的估计残差天然相关, 常规按企业维度聚类计算标准误会低估真实的抽样不确定性, 必须改用对暴露结构稳健的标准误估计方法, 这一诊断直接建立在份额加权设计理论与推断文献的系统论证之上, 该文献明确指出份额加权估计量的有效推断需要专门处理由共享冲击引入的横截面相关性, 而非简单套用聚类稳健标准误的常规做法。

第二条规范纠正一个常见的误用倾向, 即在企业层面的回归中对银行维度做聚类调整。由于本面板的行键是企业乘年, 每一行的加权测度值已经把多家银行的贡献混合进单一数值, 银行这一维度在企业层面数据里不再是可清晰界定的聚类单元, 若确需按银行维度聚类, 必须回到 pair 长表重构成企业乘银行乘年的长表结构再行操作, 直接在企业层面数据上声明按银行聚类在统计意义上是无定义的操作。第三条是计数列的建模建议: 共现篇数类列右偏且大量取值集中在零, 直接使用普通最小二乘法拟合原始计数值容易导致估计偏误, 建议采用对数变换或泊松伪极大似然方法, 这类建模选择在稀疏计数数据的经济学应用中已相当成熟。第四条是关于三条文本轨的断言纪律: 全文轨、上下文轨与严格同句轨三者互为稳健性、不分主次, 彼此之间不存在单调包含关系, 任何形式的轨间大小比较断言均属误用。第五条针对权重内生性, 提醒媒体共现权重与被加权测度可能同源自报道行为本身这一共源反射通道, 城市网点权与县域网点权正是为对冲这一风险而设的独立对照臂, 份额加权工具变量识别逻辑的系统梳理同样指出, 份额来源的外生性假设需要单独检验而不能默认成立, 非随机暴露问题的理论刻画进一步表明, 暴露结构本身若存在系统性选择, 会直接污染基于份额加权设计得到的因果解释, 论文写作端应预先声明主口径权重, 禁止在多个权重版本之间择优挑选表现更好的结果单独报告。

五条规范之所以要在同一条目内并列呈现而非分散到各自所属的家族长文中, 是因为它们共同刻画的是"面板整体使用姿态"而非某一具体列的构造细节, 使用者在着手建模之前通读这五条, 能够一次性排除掉最容易出现的五类方法论陷阱, 从而把注意力集中在真正具有研究价值的实质性问题上。值得特别指出的是, 第一条与第五条虽然分别聚焦推断层面与识别层面, 但二者在根源上共享同一个结构性事实, 即所有 cw/ce 系列加权测度本质上都是份额加权设计的具体实例, 份额加权设计理论文献反复强调, 这类设计天然带来的推断挑战与识别挑战往往不是彼此独立的两个问题, 而是同一套底层数学结构在不同分析环节的两种表现形式, 处理其中一个而忽视另一个, 很可能只是把方法论风险从统计显著性检验环节转移到了因果解读环节, 并未真正化解风险本身。份额加权工具变量识别的系统性综述进一步指出, 研究者在实际应用中应当对暴露结构与推断结构做联合诊断, 而不能割裂处理, 这正是本条目坚持五条规范并列呈现、互相印证的方法论初衷。

<!-- rendered-citations:begin -->
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. The Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Borusyak, K., & Hull, P. (2023). Nonrandom exposure to exogenous shocks. Econometrica, 91(6), 2155-2185. https://doi.org/10.3982/ECTA19367
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
<!-- rendered-citations:end -->
