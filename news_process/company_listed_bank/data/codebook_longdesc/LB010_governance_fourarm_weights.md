---
family_id: LB010
columns:
- company_bank_boardw_panel
- company_bank_supervisorw_panel
- company_bank_execw_panel
- company_bank_dsgw_panel
unit: 与媒体主面板同引擎同列名, 权重来自人事联结计数, 量纲随各自源列 X 而定
formula: "权重 w(company,bank,year) = 该年度公司与银行之间存在董事/监事/高管/董监高合并四类身份重叠联结的人数(canonical 臂不按在任状态过滤); cw/ce 通式与媒体主面板一致, 差异在权重来源为人事联结而非媒体共现"
producer: company_listed_bank/pipeline/03_build_altweight_panels.py (scheme=board/supervisor/exec/dsg 四分支)
upstream:
- _company_bank_altweights_{board,supervisor,exec,dsg}.parquet (四类人事联结长表)
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
- doi: 10.1086/228631
  type: journal
  authors: Bonacich, P.
  year: 1987
  title: "Power and centrality: A family of measures"
  venue: American Journal of Sociology
  vol: 92
  issue: 5
  pages_or_artno: 1170-1182
---

## CORE

本家族总纲性覆盖四臂治理联结权重面板: 董事权、监事权、高管权与董监高合并权, 四张表与媒体主面板同引擎同列名, 权重来源统一替换为公司与银行之间的人事身份重叠联结计数。四臂之间存在相当程度的重叠, 例如同一人同时担任董事与高管的情形在样本中并不罕见, 因此四臂高度相关但绝非同一构念, 面板设计上刻意让四臂各自独立成表, 严禁将四臂计数直接相加当作单一治理联结总量, 相加会重复计入同一人多重身份带来的联结强度, 造成系统性高估。

人事联结作为银企关系强度代理的构念根据, 可追溯至公司治理文献对所有权与控制权结构如何影响公司决策的经典考察, 该文献确立了股权与人事联结结构是理解公司与外部利益相关方关系强度的重要切入点, 董监高联结正是这一逻辑在银企关系情境下的具体应用: 若公司高管或董事同时在某银行任职或曾任职, 该联结所承载的信息传递与信任基础通常强于纯粹市场化交易关系。四臂权重的构造方式在方法论上借鉴了社会网络分析对行动者中心性与联结强度的量化传统, 该传统区分了基于直接联结数量的度中心性与基于联结在整个网络中传递能力的特征向量式中心性, 本项目当前采用的是较为直观的直接联结计数口径, 尚未引入递归式的网络传播权重, 这是刻意的方法论取舍, 目的是保持权重构造的可解释性与可审计性。canonical 臂对在职状态不做过滤, 即历史上曾经存在过的联结同样计入权重, 而更严格的现任在职稳健臂另在长表提供独立字段, 供需要区分历史沉淀关系与当期活跃关系的使用者选用, 两种口径互为稳健并置而非相互替代。

四臂之间的经济含义差异值得进一步展开。董事联结通常被理解为承载决策监督与战略层面信息交换的渠道, 董事席位赋予的表决权与议事参与权使得联结个体能够较为直接地影响公司重大决策; 监事联结在中国公司治理制度框架下承担的是相对独立的监督职能, 其信息渠道更偏向合规与风险层面而非战略决策层面; 高管联结则更贴近日常经营信息的传递, 高管在企业与银行之间的双重任职往往意味着更频繁的业务往来与更细粒度的经营信息共享; 董监高合并臂将三类身份汇总统计, 提供的是治理联结广度的总量视角, 但正因其合并性质, 使用者若需要区分不同治理联结渠道各自的边际效应, 应优先使用三个分臂而非合并臂作为解释变量。四臂高度相关这一现象背后还隐含一个数据生成机制层面的解释: 具备资源与声誉条件在银行系统内建立多重人事联结的企业, 往往本身就具备更强的关系网络构建能力, 这类企业的董事、监事、高管联结经常同步出现, 而非彼此独立随机分布, 这一共同驱动因素是四臂相关性的重要来源之一, 也提示使用者在解读四臂各自的边际回归系数时, 应意识到系数背后可能混杂了企业本身关系网络构建能力这一未被完全控制的潜在因素, 建议在关键设定中加入企业规模、上市年限等代理变量加以部分缓解。

<!-- rendered-citations:begin -->
Demsetz, H., & Lehn, K. (1985). The structure of corporate ownership: Causes and consequences. Journal of Political Economy, 93(6), 1155-1177. https://doi.org/10.1086/261354
Freeman, L. C. (1978). Centrality in social networks conceptual clarification. Social Networks, 1(3), 215-239. https://doi.org/10.1016/0378-8733(78)90021-7
Bonacich, P. (1972). Factoring and weighting approaches to status scores and clique identification. The Journal of Mathematical Sociology, 2(1), 113-120. https://doi.org/10.1080/0022250X.1972.9989806
Bonacich, P. (1987). Power and centrality: A family of measures. American Journal of Sociology, 92(5), 1170-1182. https://doi.org/10.1086/228631
<!-- rendered-citations:end -->
