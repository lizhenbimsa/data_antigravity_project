---
family_id: F195
columns:
- digital_frontier
unit: 二值分组哑变量 (0/1, 无量纲)
formula: "digital_frontier_i = 1[ n_articles_{i, base_year} >= median_{g}( n_articles_{base_year} | n_articles>0 ) ]; base_year = min(panel.year); g = bank_type 组内中位数; 基年零覆盖银行 -> 0; 组员资格跨年固定 broadcast"
producer: news_process/pipeline/panel/runner.py::_base_year_median_split (标签 news_process/pipeline/panel/export.py)
upstream:
- 40_panel_yearly.parquet (n_articles, bank_type, year)
citations:
- doi: 10.1002/ijfe.3105
  type: journal
  authors: Liu, J., Chen, S., Su, F., & Liu, J.
  year: 2025
  title: "Digital transformation disclosure and bank loans: An information heterogeneity perspective"
  venue: International Journal of Finance and Economics
  vol: 30
  issue: 4
  pages_or_artno: 4004-4038
- doi: 10.1017/S0022109023000662
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2618-2646
- doi: 10.1080/1540496X.2021.1923477
  type: journal
  authors: Lu, Z., Wu, J., Li, H., & Nguyen, D. K.
  year: 2022
  title: "Local bank, digital financial inclusion and SME financing constraints: Empirical evidence from China"
  venue: Emerging Markets Finance and Trade
  vol: 58
  issue: 6
  pages_or_artno: 1712-1725
- doi: 10.1146/annurev-financial-100719-120854
  type: journal
  authors: Vives, X.
  year: 2019
  title: "Digital disruption in banking"
  venue: Annual Review of Financial Economics
  vol: 11
  issue: 1
  pages_or_artno: 243-272
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: Journal of Business Economics
  vol: 87
  issue: 5
  pages_or_artno: 537-580
new_dois: []
---

## CORE

【构念与来源】
digital_frontier 是一个刻画银行"数字前沿地位"的二值分组哑变量 (0/1, 无量纲), 用于把样本内各家银行事前 (pre-period) 一次性地划分为"高数字前沿组"与"低数字前沿组"两类。其构念意图并非度量某一年内银行的数字化投入强度本身, 而是提供一个在识别层面被冻结的、不随后续年份内生翻转的组员资格 (group membership) 标签, 使其可以充当三重差分 (DDD) 与情感交互项里的调节变量。构念背后的经验直觉是: 在样本期起点即已获得较高媒体报道热度的银行, 通常也是在金融科技、移动支付、数字银行等议题上更活跃、更早被市场与舆论关注的机构; 以基年报道覆盖量作为代理变量, 可以在缺乏逐年细粒度数字化投入面板的条件下, 近似地把"数字先行者"从"数字追随者"中分离出来。这一代理选择与银行数字化文献里以信息披露、数字能力评分或数字普惠指数刻画银行数字前沿地位的做法在精神上一致: Liu, Chen, Su 与 Liu (2025) 以银行数字化转型披露度量其信息环境, Kwan, Lin, Pursiainen 与 Tai (2024) 在新冠冲击下以银行既有数字能力刻画其抗压差异, 二者都强调"数字能力/数字前沿"是一个应当在冲击发生前即已确定 (predetermined) 的银行属性, 而非事后随冲击共同演化的内生量。

【方法学与计算】
本列由 runner.py 内的 _base_year_median_split 辅助函数产出, 计算链路严格遵循"基年固定切分"原则。第一步取面板最早年份 base_year = min(panel['year']) 作为切分基准年; 第二步在基年内取每家银行的新闻报道计数 n_articles, 并只保留基年有正报道覆盖 (n_articles>0) 的银行进入中位数计算; 第三步在 bank_type (银行类型) 组内分别求 n_articles 的中位数, 凡基年报道量大于等于其所属类型组中位数者判为 1 (高数字前沿), 否则判为 0; 第四步把这一在基年确定的 0/1 资格通过 target_bank 主键 broadcast 到该银行的全部年份, 使组员资格跨年恒定; 基年零覆盖或未出现在基年的银行一律回填 0。该实现刻意规避了早期版本按"同年中位数"逐年切分的做法——旧实现下组员资格会随各年内生新闻覆盖量翻转 (历史盘上曾观察到数十家银行的资格逐年翻转), 当该哑变量进入 DDD 交互或情感交互时, 调节变量便与结果变量同期内生, 违反本项目对 Bartik 型工具变量强制的 pre-treatment 固定公理 (Goldsmith-Pinkham 等人 2020 年提出的份额外生性要求), 也偏离 Fang 与 Peress (2009) 对媒体覆盖排序须为 predetermined 的处理。改为基年固定切分后, 该列在识别上被冻结为一个纯事前分组, 只在横截面维度携带变异, 时间维度上对每家银行是常数, 因此其单独系数在含银行固定效应的回归中被吸收, 真正进入结构式的是它与政策冲击、事件后窗的乘积项 dcep_ddd_digfront 与 sandbox_ddd_digfront (Treated × Post × DigFrontier)。

【文献定位】
在数字金融与银行数字化的文献谱系里, digital_frontier 对应的是"银行层面数字前沿异质性"这一调节维度。Vives (2019) 在其对银行业数字颠覆的综述里系统论证了数字技术如何重塑银行竞争格局, 并指出不同银行在面对数字冲击时的响应能力存在结构性分化, 这正是本哑变量试图捕捉的横截面异质性来源。Gomber, Koch 与 Siering (2017) 从数字金融与金融科技的研究议程出发, 勾勒了数字业务范式的多维构成, 为把"报道热度高"解释为"数字业务活跃"提供了构念桥接。Lu, Wu, Li 与 Nguyen (2022) 以中国地方银行的数字普惠金融实践为背景, 说明银行的数字前沿地位与其信贷行为、对中小企业融资约束的缓解能力密切相关, 支持把该分组用作政策效应异质性的调节轴。需要强调的是, 本列是分组代理而非直接测度, 其效度取决于"基年媒体报道热度"与"真实数字能力"之间的相关强度; 稳健性上可与其它事前分组 (如 high_coverage、bank_scale_ord、is_soe) 并列比较, 各分组各自 just-identified 并排、互为稳健性、不分主次, 且禁止混入同一 over-identified 的 Hansen J 检验以避免人为制造过度识别。

## VAR: digital_frontier

【变体差分】
本家族仅含 digital_frontier 单列, 无三轨 (full/ctx/ss) 分身、无 co-primary 双轨嵌入孪生、无梯子 (消融/权重/阈值/判据) 变体、无 per-model 分裂, 因此不存在同族 canonical 与变体的差分关系; 本节说明的是它区别于面板内相邻分组哑变量的精确构造语义。第一, 切分依据是 n_articles (银行-年报道总篇数) 在 bank_type 组内的基年中位数, 而非全样本中位数——组内中位数使切分对不同银行类型的报道基线差异免疫, 避免把"大型国有行天然报道多"混同于"数字前沿"。第二, 时间口径是严格的基年固定 (base_year = min(panel.year)), 组员资格一经确定即跨年 broadcast 恒定, 这与任何"逐年重新切分"的同期内生分组根本不同, 也是它能合法充当 DDD 调节变量的前提。第三, 分子门槛是大于等于组内中位数 (>=med) 而非严格大于, 中位数处的边界银行归入 1 组; 基年零覆盖 (n_articles=0) 或基年缺席的银行一律回填 0, 而非按缺失剔除, 保证该列在全面板无缺失、可直接进入交互乘积。第四, 该列自身在含银行固定效应的设定中因时间不变而被吸收, 其识别贡献只经由 dcep_ddd_digfront 与 sandbox_ddd_digfront 两个三重差分项体现, 分别对应数字货币试点 (DCEP) 与监管沙盒 (Sandbox) 两个政策冲击下"数字前沿组相对非前沿组的额外处理效应"。第五, 若上游 bank_type 列缺失, 生产端会跳过本列构建并记 WARNING 而非静默产出错误分组, 属 fail-loud 设计。相对于同为事前分组的 high_coverage (亦由基年固定切分产出, 但不按 bank_type 分组、直接用全样本 n_articles 中位数), digital_frontier 的组内分层口径使其更贴近"同类型银行内部的数字先行者"这一构念, 二者互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Liu, J., Chen, S., Su, F., & Liu, J. (2025). Digital transformation disclosure and bank loans: An information heterogeneity perspective. International Journal of Finance and Economics, 30(4), 4004-4038. https://doi.org/10.1002/ijfe.3105
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Lu, Z., Wu, J., Li, H., & Nguyen, D. K. (2022). Local bank, digital financial inclusion and SME financing constraints: Empirical evidence from China. Emerging Markets Finance and Trade, 58(6), 1712-1725. https://doi.org/10.1080/1540496X.2021.1923477
Vives, X. (2019). Digital disruption in banking. Annual Review of Financial Economics, 11(1), 243-272. https://doi.org/10.1146/annurev-financial-100719-120854
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
<!-- rendered-citations:end -->
