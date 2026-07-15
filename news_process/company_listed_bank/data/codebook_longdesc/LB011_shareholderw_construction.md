---
family_id: LB011
columns:
- company_bank_shareholderw_panel
- cw_X_t_shareholderw
- ce_X_t_shareholderw
unit: 与媒体主面板同引擎同列名, 权重来自持股比例快照(比例, 取值范围[0,1]), 量纲随各自源列 X 而定
formula: "权重 w(company,bank,year) = (公司,年)内最晚可观测报告期快照下银行对公司的持股比例, 同(公司,年)最晚期内同一银行体系(分行加总行)按 canonical 折叠取和"
producer: company_listed_bank/pipeline/03_build_altweight_panels.py (scheme=shareholder 分支)
upstream:
- _company_bank_altweights_shareholder.parquet (股东持股关系强度长表)
- news_process 40_panel_yearly.parquet (被加权源列 X 取值来源)
citations:
- doi: 10.1086/261354
  type: journal
  authors: Demsetz, H., & Lehn, K.
  year: 1985
  title: "The structure of corporate ownership: Causes and consequences"
  venue: Journal of Political Economy
  vol: 93
  issue: 6
  pages_or_artno: 1155-1177
- doi: 10.1111/j.1540-6261.1994.tb04418.x
  type: journal
  authors: Petersen, M. A., & Rajan, R. G.
  year: 1994
  title: "The benefits of lending relationships: Evidence from small business data"
  venue: The Journal of Finance
  vol: 49
  issue: 1
  pages_or_artno: 3-37
- doi: 10.1016/j.jfi.2021.100923
  type: journal
  authors: Banerjee, R. N., Gambacorta, L., & Sette, E.
  year: 2021
  title: "The real effects of relationship lending"
  venue: Journal of Financial Intermediation
  vol: 48
  issue: ""
  pages_or_artno: "100923"
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  issue: ""
  pages_or_artno: 171-202
---

## CORE

本家族覆盖股东权面板 company_bank_shareholderw_panel 的构造逻辑与快照口径, 是七替代权面板中以股权持有而非借贷或人事联结衡量银企关系强度的一支。银行持股企业这一关系类型在公司治理研究中具有特殊地位, 所有权结构的集中或分散程度长期被视为影响公司决策与代理成本的核心变量, 银行作为持股方相较于一般财务投资者往往兼具债权人与股东双重身份, 这种双重身份可能带来独特的监督与信息优势, 也可能带来利益冲突, 股东权面板为量化这一关系强度提供了直接的经验基础。

快照口径的构造存在两点需要显式说明的方法论选择。其一, 权重取自公司当年全部报告期集合中最晚可观测的一期, 而非严格意义上的年末时点, 这一选择的动机是持股数据披露存在时滞, 强行取年末时点可能引入不必要的缺失, 以最晚可观测期作为近似年末快照是数据可得性约束下的合理折中。其二, 同一银行体系下分行与总行的持股记录在同一报告期内会被合并为一条记录取和, 这一处理反映出分支机构持股在实质上属于同一法人实体的合并权益, 折叠加总避免了因报表列示口径差异导致的同一银行关系被重复拆分计数。持股关系数据在样本内呈现出制度性稀疏的特征, 这一稀疏性并非数据缺陷, 而是商业银行相关法律对银行持股非金融企业设有严格限制的直接后果, 现存的持股案例多经历史遗留安排、债转股或个案特批通道产生, 稀疏性反映的是条款解释空间而非样本选取偏误。持股关系作为银企联结强度代理的构念效度, 与关系借贷文献中对信贷额度与股权联结交互效应的考察一脉相承, 也呼应金融网络研究对不同联结类型各自承载独立识别假设这一提醒, 使用者在跨权重版本比较系数时应清醒意识到股东权捕捉的是与贷款权、网点权、人事权均不同的关系维度。

股东权在七替代权谱系中占据一个特殊位置, 因为它是唯一直接反映资本所有权关系而非债权或人事关系的权重臂, 银行作为股东与银行作为债权人对企业行为的影响渠道在公司金融理论中被认为存在本质差异: 股权关系赋予银行更直接的剩余索取权与治理参与权, 银行股东可能通过董事会席位或表决权影响企业重大决策, 而单纯的债权关系则更多依赖契约条款与违约救济机制施加约束, 这一渠道差异意味着股东权与贷款权即便针对同一对公司银行组合, 也可能捕捉到方向相反或强度迥异的经济效应, 不应简单假设二者是同一潜在关系强度的可互换代理。持股比例本身在样本中呈现出高度右偏的分布特征, 绝大多数非零观测集中在较低比例区间, 只有少数历史遗留或特殊安排案例达到显著比例, 这一分布形态提示使用者在做回归分析时应考虑对持股比例做适当的变换处理, 例如取对数或使用分类哑变量, 而非直接以原始比例线性纳入模型, 否则少数极端值可能对回归系数产生不成比例的杠杆影响。此外, 由于商业银行持股非金融企业受到严格的监管限制, 样本内非零持股观测的稀缺性也意味着基于股东权的实证结论天然只能对少数满足特殊持股条件的子样本成立, 使用者在报告基于股东权的发现时应明确声明其外部有效性边界, 不应不加限定地推广到样本中不存在持股关系的绝大多数银企对。

<!-- rendered-citations:begin -->
Demsetz, H., & Lehn, K. (1985). The structure of corporate ownership: Causes and consequences. Journal of Political Economy, 93(6), 1155-1177. https://doi.org/10.1086/261354
Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending relationships: Evidence from small business data. The Journal of Finance, 49(1), 3-37. https://doi.org/10.1111/j.1540-6261.1994.tb04418.x
Banerjee, R. N., Gambacorta, L., & Sette, E. (2021). The real effects of relationship lending. Journal of Financial Intermediation, 48, 100923. https://doi.org/10.1016/j.jfi.2021.100923
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
<!-- rendered-citations:end -->
