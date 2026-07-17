---
family_id: F485
columns:
- prox_100km_n_articles
- prox_150km_n_articles
- prox_200km_n_articles
- prox_50km_n_articles
unit: 篇 (计数, bank-year 级)
formula: 'prox_{d}km_n_articles = 该 bank-year 内、报道媒体地理坐标与目标银行总部坐标球面距离 (Haversine)
  ≤ d 公里的可地理编码文章篇数; 分子分母同口径限定在"可地理编码"文章集合内 (媒体城市/省份能定位到坐标的文章), 该 bank-year
  全部文章不可地理编码时该列填 NaN (非 0)。'
producer: pipeline/panel/geography.py::compute_geo_proximity_buffers (步骤 12 四梯度地理距离缓冲)
upstream:
- 00_preprocessing (媒体侧 城市/国家地区省份 原始列)
- config/paths.yaml::city_coordinates_file (城市坐标字典)
- config/paths.yaml::province_capital_map_file (省会回退映射)
- config/paths.yaml::bank_addresses_file (银行总部地址→城市)
- 40_panel_export_main (target_bank × year 行索引)
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/j.1540-6261.2010.01626.x
  type: journal
  authors: Engelberg, J. E., & Parsons, C. A.
  year: 2011
  title: The causal impact of media in financial markets
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 67-97
- doi: 10.1016/j.eap.2024.08.019
  type: journal
  authors: Guo, L., Zhu, H., Zhang, C., Liu, Y., & Yang, C.
  year: 2024
  title: Does improved credit access promote pollution reduction? The role of bank
    proximity
  venue: Economic Analysis and Policy
  vol: '84'
  pages_or_artno: 78-97
- doi: 10.1002/ijfe.2791
  type: journal
  authors: Ahmad, M., & Law, S. H.
  year: 2024
  title: 'Financial development, institutions, and economic growth nexus: A spatial
    econometrics analysis using geographical and institutional proximities'
  venue: International Journal of Finance & Economics
  vol: '29'
  issue: '3'
  pages_or_artno: 2699-2721
- doi: 10.1111/0022-1082.00181
  type: journal
  authors: Coval, J. D., & Moskowitz, T. J.
  year: 1999
  title: 'Home bias at home: Local equity preference in domestic portfolios'
  venue: The Journal of Finance
  vol: '54'
  issue: '6'
  pages_or_artno: 2045-2073
- doi: "10.1080/24694452.2025.2564220"
  type: "journal"
  authors: "Kong, I., & Purves, R. S."
  year: 2026
  title: "Analyzing Geographic Bias of Newspaper Articles Reporting Global Climate Disasters"
  venue: "Annals of the American Association of Geographers"
  vol: "116"
  issue: "2"
  pages_or_artno: "270-288"
---

## CORE

【构念与来源】
`l2_prox_n_articles` 家族 (`prox_50km_n_articles` / `prox_100km_n_articles` / `prox_150km_n_articles` / `prox_200km_n_articles`) 是四梯度地理距离缓冲 (geo-proximity buffer) 计数族的分子列, 度量"以银行总部为圆心、半径 d 公里的圆内, 有多少篇可地理编码的报道"。构念定位是本地媒体注意力 (local media attention) 的规模侧量: 一家银行若被总部近旁的媒体大量报道, 说明该行嵌入本地信息环境的强度高, 这与银行本地关系网络、区域市场声誉建构、以及本地投资者/储户信息获取渠道直接相关。产生该家族的模块是 `pipeline/panel/geography.py::compute_geo_proximity_buffers` (步骤 12 "四梯度地理距离缓冲"), 与家族 F483 (`prox_{d}km_frac`, 占比)、F484 (`prox_{d}km_is_local`, 二值)、F486 (`prox_{d}km_n_media`, 媒体来源数)、F487 (`prox_{d}km_tone/pos_frac/neg_frac`, 情感三轨) 同源同批产出, 六个子家族共用同一次逐 bank-year 距离计算, 仅取用的汇总函数不同 (计数 vs 占比 vs 均值)。

【方法学与计算】
计算分三步。第一步坐标解析: 对每篇文章的媒体侧地理字段 (`城市` 列, 缺失时退到 `国家地区/省份` 列) 做三级坐标查找 — Level 1 精确匹配城市坐标字典; Level 2 清洗字符串 (去"市"/"地区"等后缀噪声) 后再匹配; Level 3 若仍未命中, 退化到该省份的省会坐标 (`province_capital_map_file`)。银行总部坐标同样通过 `bank_addresses_file` 解析城市后查坐标字典, 三级查找失败 (Level 1/2/3 均未命中) 的银行整个 bank-year 被跳过 (不产出任何 `prox_*` 列, 而非填 0)。第二步距离计算: 用 Haversine 球面距离公式 (地球半径取 6371km) 逐篇计算媒体坐标与银行总部坐标的大圆距离, 得到 `_dist_km` 列; 媒体侧三级查找也失败的文章距离记为缺失 (不可地理编码)。第三步阈值计数: 对 `_DISTANCE_THRESHOLDS_KM = (50, 100, 150, 200)` 四个半径依次筛选 `_dist_km ≤ d` 的文章子集, 取子集行数即为 `prox_{d}km_n_articles`。分母口径要点 (2026-06-10 metric-audit 修复 prox-frac-denominator 同批对齐): 该 bank-year 内全部文章都不可地理编码时 (`n_geocoded == 0`), 四个 `n_articles` 列统一填 `NaN` 而非 0 — "圈内有无报道"在此时是未知而非确知为零, 与占比家族 F483 (`prox_*_frac`) 及二值家族 F484 (`prox_*_is_local`) 的 NaN 语义严格对齐, 避免下游把"未知"误读为"确知无报道"的系统性向下偏差。四个阈值列彼此存在拓扑单调约束 (`prox_50km_n_articles ≤ prox_100km_n_articles ≤ prox_150km_n_articles ≤ prox_200km_n_articles`), 该约束由半径嵌套的几何定义直接保证 (更大半径的圆必然包含更小半径圆的全部文章), 经逐行核对 `compute_geo_proximity_buffers` 源码, 该函数对本家族四列本身并无显式的单调断言或告警代码, 该约束是"筛选逻辑必然导出"的隐式性质而非产出后被程序主动校验的性质; geography.py 内唯一存在的显式拓扑单调 warning (非 assert) 属于同文件另一函数 `compute_regional_imitation_pressure` 产出的 `ai_reg_{d}km` 区域模仿压力族, 与本家族变量名不同、口径不同, 不应混同援引。本族计数与情感三轨 (full/ctx/ss) 无关, 是 track-agnostic 单轨列 — 圆内文章数不区分该文章走哪条文本轨道分析, 与家族 F487 (`prox_*_tone_full/_ctx/_ss` 等三轨情感聚合) 是同一批圈选文章上的不同统计量, 不构成三轨梯子, 不适用"各自 just-identified 并排、禁混同一 Hansen J"的三轨/co-primary 铁律 (那是情感测量维度的正交梯子, 本族是几何计数维度)。

【文献定位】
多距离阈值缓冲方法论的经典锚点是 Gurun & Butler (2012, *The Journal of Finance*) 与 Engelberg & Parsons (2011, *The Journal of Finance*): 前者证明本地媒体对本地上市公司存在系统性正面偏向 (local media slant), 后者证明媒体报道对金融市场存在因果冲击, 且冲击强度随媒体与标的公司地理接近度衰减, 两文均采用以标的公司为圆心、多个同心圆半径分层统计媒体覆盖的设计, 是本家族"50/100/150/200km 四梯度圆"设计的直接方法学来源。地理距离与球面几何计算沿用 Coval & Moskowitz (1999) 度量本地权益偏好 (home bias) 时确立的精确距离计算传统。近期文献进一步把"地理邻近度—金融行为"构念延展到银行/信贷场景: Guo, Zhu, Zhang, Liu & Yang (2024, *Economic Analysis and Policy*) 证明银行网点地理邻近度 (bank proximity) 影响信贷可得性进而影响企业污染治理行为, 与本族"以银行总部为圆心度量媒体报道密度"共享"物理距离作为信息/资源摩擦代理变量"的识别逻辑; Ahmad & Law (2024, *International Journal of Finance & Economics*) 用空间计量方法同时纳入地理邻近度与制度邻近度检验金融发展—经济增长关系, 佐证地理距离在金融地理学中作为多层次邻近度构念之一的通用性。这些文献共同支持本族的核心解释假设: 报道数量随地理距离衰减反映的是本地信息生产与传播成本梯度, 而非报道内容 (语调) 本身的系统差异 (后者由 F487 家族单独测度)。 在"先给新闻报道打上地理坐标、再在坐标空间上统计覆盖度"这一分析范式上, Kong 与 Purves (2026) 提供了前沿存在性证明: 该文对报纸文章检测地名并赋予地理坐标后, 量化报道在空间上的不均衡覆盖 (地理偏倚), 并考察地名粒度与要素类型对分析结论的影响, 与本族先地理编码、再对可地理编码报道作距离缓冲计数的口径同源。迁移边界须诚实标注: 其语料固定为五家英国报纸、主题是全球气候灾害而非银行金融科技, 分析单位是"报道—事件发生地"的国别覆盖偏倚, 而非本族"媒体所在地—银行总部"的双坐标距离; 原文亦无 bank-year 面板聚合, 也无本族全部报道不可地理编码时置 NaN 的哨兵口径, 属地理学期刊而非金融计量文献, 故仅在范式可行性层面提供支撑, 不构成四梯度阈值取值的依据。
## VAR: prox_50km_n_articles

【变体差分】
本列是四梯度中最内层的半径 (50 公里), 圈选的是与银行总部处于同城或近郊范围内的媒体报道。50km 半径下, 圈内文章通常绝大部分来自银行总部所在城市本身的都市报/晚报等本地化媒体, 因此该列最贴近"严格意义上的本地媒体覆盖", 受省会插补 (`prox_geo_imputed_frac`) 的干扰在四档中相对最敏感: 一家总部设在省会城市的银行, 凡遇到无法精确定位到具体地级市、只能退化到省会坐标的媒体报道, 都会被计入 50km 圈 (因为省会坐标与银行坐标重合或距离压至 ≈0), 造成该列对省会银行系统性偏高; 而非省会银行的报道即便实际发自邻近地级市, 若该地级市坐标缺失也只能退化到省会, 又会被系统性排除出 50km 圈。这一不对称性是 producer 文档 (geography.py 步骤 12 docstring) 明确记录的插补水分来源, 稳健性检验中应同时报告剔除高插补 bank-year 后的 50km 列估计, 或直接改用 100km/150km 更宽半径作平行设计。50km 与其余三档共享同一份逐 bank-year 距离计算与"全不可地理编码则填 NaN"的缺失口径, 唯一差分维度是筛选阈值 `d=50`, 不涉及情感轨道或权重梯子, 四档半径彼此是同一构念沿距离维度的单调嵌套刻度, 而非互为稳健性的并排梯子——更宽半径天然包含更窄半径的全部文章, 二者不构成可独立识别的正交设计, 使用时应视研究问题选定单一半径为主设计, 其余半径作距离敏感性展示而非 over-identified 联合估计。

## VAR: prox_100km_n_articles

【变体差分】
本列半径 100 公里, 是四梯度中的第二档, 通常覆盖银行总部所在城市及其邻近地级市/都市圈范围。相较 50km, 100km 半径纳入的媒体来源更多元, 省会插补造成的系统偏差相对缓和 (省会与非省会城市间的典型地理距离多落在 100–300km 区间, 100km 半径下仍会有一部分插补噪声, 但不像 50km 那样几乎完全被插补效应主导)。100km 是四档中常被作为"区域性媒体覆盖"操作化定义的折中选择, 兼顾了"本地"构念的紧致性与样本量的可估计性 (50km 圈在中小城市总部银行样本中圈内文章数可能极稀疏、方差大)。与 `prox_50km_n_articles` 同理, 该列与情感三轨、词典消融、政治词权重等梯子均无交集, 是 track-agnostic 单轨几何计数, 计算分母口径 (可地理编码文章集合) 与缺失填法 (全不可编码则 NaN) 与其余三档完全一致, 唯一差分维度是阈值 `d=100`。在四档半径的单调嵌套关系下, `prox_100km_n_articles ≥ prox_50km_n_articles` 恒成立 (该关系由半径嵌套的几何定义直接保证, producer 对本列并无显式断言/告警代码主动核实此性质, 是筛选逻辑必然导出的隐式性质), 因此该列常被用作 50km 列样本量不足时的替代主设计, 或与 50km/150km/200km 一并报告作为"结果对半径选择的敏感性"图表, 而非作为与 50km 并列的独立稳健性检验轨。

## VAR: prox_150km_n_articles

【变体差分】
本列半径 150 公里, 是四梯度的第三档, 在多数省份已能覆盖省内主要地级市乃至部分邻省城市, 圈内文章数通常显著多于 50km/100km 两档, 样本稀疏性问题进一步缓解, 但相应地"本地"构念的紧致性被稀释——150km 圈内已包含相当比例原本不构成"同城/近邻"直觉的媒体, 更接近"省域媒体覆盖"而非"本地媒体覆盖"。省会插补效应在该档下影响趋弱: 由于 150km 半径本身已足够宽, 即便某些媒体因坐标缺失被错误地放置到省会而非其真实城市, 只要真实城市本就落在 150km 邻域内 (省内城市间距离多数不超过 150–200km), 插补造成的"计入/排除"误判概率下降, 但对省域面积特别大的省份 (如新疆、西藏、内蒙古) 该效应依然可观, 不能一概而论为已消除。150km 与其余三档共享同一距离计算流水线、同一缺失填法与同一 track-agnostic 属性, 差分维度仅在阈值取值。该列在四档半径谱系中承担"宽口径"一端的角色, 常与 200km 一起用于检验窄口径 (50km/100km) 下的结果是否对半径选择的具体取值敏感, 即距离阈值敏感性分析中的高半径锚点。

## VAR: prox_200km_n_articles

【变体差分】
本列半径 200 公里, 是四梯度中最宽的一档, 在多数情形下已覆盖银行总部所在省份的绝大部分区域甚至跨省邻接地级市, 圈内文章数在四档中通常最多、方差最小, 样本稀疏性问题基本消解, 但"本地媒体"这一构念在该半径下已相当程度上退化为"区域媒体"甚至局部逼近"全国性媒体在该区域的报道", 与 Gurun & Butler (2012) / Engelberg & Parsons (2011) 原始设计中"本地"应体现地理紧致性的初衷渐行渐远, 使用该列作主要解释变量时需在论文中明确其构念含义已从"本地"漂移为"区域"。省会插补效应在该档下影响最弱 (200km 半径几乎必然把插补坐标与真实坐标都圈入同一集合), 因此 `prox_200km_n_articles` 相对 50km/100km 列对 `prox_geo_imputed_frac` 披露的插补噪声最不敏感, 常被用作检验窄半径结果是否受插补水分驱动的对照锚点——若某一发现在 50km 显著、在 200km 依然同向显著, 可部分排除该发现完全由省会插补人为制造。与其余三档相同, 该列是 track-agnostic 单轨几何计数, 缺失填法、分母口径与产出批次完全一致, 差分维度仅在阈值 `d=200`, 且四档半径构成单调嵌套 (`prox_50km_n_articles ≤ prox_100km_n_articles ≤ prox_150km_n_articles ≤ prox_200km_n_articles`), 报告结果时应作为半径选择的敏感性谱系而非可并列汇报的独立稳健性检验。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Guo, L., Zhu, H., Zhang, C., Liu, Y., & Yang, C. (2024). Does improved credit access promote pollution reduction? The role of bank proximity. Economic Analysis and Policy, 84, 78-97. https://doi.org/10.1016/j.eap.2024.08.019
Ahmad, M., & Law, S. H. (2024). Financial development, institutions, and economic growth nexus: A spatial econometrics analysis using geographical and institutional proximities. International Journal of Finance & Economics, 29(3), 2699-2721. https://doi.org/10.1002/ijfe.2791
Coval, J. D., & Moskowitz, T. J. (1999). Home bias at home: Local equity preference in domestic portfolios. The Journal of Finance, 54(6), 2045-2073. https://doi.org/10.1111/0022-1082.00181
Kong, I., & Purves, R. S. (2026). Analyzing Geographic Bias of Newspaper Articles Reporting Global Climate Disasters. Annals of the American Association of Geographers, 116(2), 270-288. https://doi.org/10.1080/24694452.2025.2564220
<!-- rendered-citations:end -->
