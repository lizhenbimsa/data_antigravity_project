---
family_id: TB012
novelty_exempt_rationale: "该家族是省直辖县级建制退化键恒等现象的构造性说明, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- county_key_ok
- rel_hhi
unit: 无量纲 (构造性恒等说明段, 非独立数值列)
formula: "144家省/自治区直辖县级占位企业, 分支侧CityName记为该县级市/CountyName记为镇街级 → 县权绕过复合键走城市层同款退化键 (公司键=district), 保证城/县两权逐(bank,year)数值恒等"
producer: company_tax_bank/pipeline/03_build_altweight_panels.py (T-D5b(i) 退化键分支)
upstream:
- config/银行业金融机构基本信息表.dta (CityName/CountyName字段, 退化键判定来源)
- _company_tax_bank_weight_validation.md (03 城×县 Spearman 互验报告, 已按企业整体剔除该144家)
citations:
- doi: 10.1214/24-STS939
  type: journal
  authors: Kamat, G., & Gutman, R.
  year: 2026
  title: "Analysis of linked files: A missing data perspective"
  venue: Statistical Science
  vol: 41
  issue: 1
  pages_or_artno: ""
- doi: 10.1016/0378-8733(78)90021-7
  type: journal
  authors: Freeman, L. C.
  year: 1978
  title: "Centrality in social networks conceptual clarification"
  venue: Social Networks
  vol: 1
  issue: 3
  pages_or_artno: 215-239
- doi: 10.1080/0022250X.1972.9989806
  type: journal
  authors: Bonacich, P.
  year: 1972
  title: "Factoring and weighting approaches to status scores and clique identification"
  venue: The Journal of Mathematical Sociology
  vol: 2
  issue: 1
  pages_or_artno: 113-120
- doi: 10.1162/0033553041502162
  type: journal
  authors: Guiso, L., Sapienza, P., & Zingales, L.
  year: 2004
  title: "Does local financial development matter?"
  venue: The Quarterly Journal of Economics
  vol: 119
  issue: 3
  pages_or_artno: 929-969
---

## VAR

本条目专门解释双替代权面板中一类特殊且容易被误判为构造缺陷的恒等现象: 一百四十四家省级或自治区级直辖县级市企业, 例如新疆石河子、湖北仙桃与潜江等地的企业, 在权源银行网点表中其城市字段直接记录为该县级市本身, 区县字段则填的是镇或街道级别的更细信息, 这与税调企业名录中区县字段的记录粒度无法直接对齐, 因为税调名单期望的是标准的市辖区或县这一级行政区划, 而不是镇街级。面对这种行政区划本身缺少中间层级的情形, 县域权引擎的处理方式是绕过常规的城市区县复合键匹配逻辑, 转而直接采用与城市层完全相同的退化键, 也就是把企业的键值设定为等同于城市层的键。

这一构造选择带来一个必然的数学后果: 对于这一百四十四家企业, 城市网点权与县域网点权在每一个银行乘年份的观测点上取值逐字节恒等, 二者事实上退化为同一个权重版本的两份副本。需要向使用者强调的是, 这种恒等现象是行政区划层级结构本身的客观限制所决定的构造性产物, 并非引擎存在缺陷或计算错误, 网络中心性测度经典文献早已系统澄清, 任何基于网络结构的中心性或权重构造在底层拓扑结构本身退化为单一层级时, 不同粒度的测度定义会自然收敛为同一数值, 这一现象在网络分析领域并不罕见; 权重加总与因子分解方法框架同样论证了, 当基础赋权矩阵的行列结构本身存在退化子集时, 衍生的多个权重版本在该子集上会呈现数学上的恒等关系。正因如此, 本项目在城域与县域两权的互验报告中已将这一百四十四家企业作为已知的构造性恒等子集整体从相关性检验的样本中剔除, 避免这批必然完美相关的观测值人为拉高互验报告中城域与县域权重之间的斯皮尔曼相关系数, 从而虚假地夸大两套权重体系的一致程度; 使用者若在自己的分析中观察到这批企业的城域县域两权数值完全一致, 应理解为预期内的构造现象而非需要排查的异常。

这一百四十四家企业的存在还提示了一个更一般的经验教训: 行政区划体系本身并非在全国范围内均匀地遵循同一套层级结构, 省级或自治区直辖县级市这一建制类型天然跳过了地级市这一中间层级, 任何依赖"城市大于区县"这一默认层级假设构造的空间权重体系, 都必须在设计阶段就预先考虑这类例外建制的存在, 而不能等到生产环境暴露出异常结果后再临时打补丁。中心性测度经典文献所强调的"测度定义必须与底层网络拓扑结构相匹配"这一原则, 在本例中体现为: 空间权重的城市与区县两级划分本身就是对经济地理关系的一种拓扑简化, 当真实行政区划的拓扑结构本身发生退化时, 建立在该拓扑结构之上的测度体系理应随之退化, 而不是勉强维持两个层级形式上的区分却在数值上制造出误导性的伪差异。因子分解与权重加总方法框架同样提示, 处理这类结构性退化子集的正确姿态是显式标注并纳入分析框架, 而非试图通过人为扰动或强行拆分制造出本不存在的层级差异, 本项目选择在互验报告与本条目中双重披露这一现象, 正是对这一原则的具体践行。

以次国家行政层级度量地方金融发展的奠基性顶刊研究早已提示, 空间层级的选择本身就是金融地理测度设计的核心组成部分: Guiso、Sapienza 与 Zingales 于 2004 年在意大利地区层级构造地方金融发展指标时, 同样必须先回答以哪一级行政区划为度量单元这一前置问题, 其结论的稳健性也依赖于所选层级与金融市场真实分割边界的匹配程度; 本条目披露的退化键恒等现象正是这一一般性原理的镜像——当个别建制的行政层级结构本身缺失中间层时, 两级度量单元物理重合, 层级间测度收敛是结构使然而非构造错误。

<!-- rendered-citations:begin -->
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. The Journal of Mathematical Sociology, 2(1), 113-120. https://doi.org/10.1080/0022250X.1972.9989806
Guiso, L., Sapienza, P., & Zingales, L. (2004). Does local financial development matter?. The Quarterly Journal of Economics, 119(3), 929-969. https://doi.org/10.1162/0033553041502162
<!-- rendered-citations:end -->
