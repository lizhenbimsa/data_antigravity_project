---
family_id: LB008
columns:
- company_bank_loanw_panel
- cw_X_t_loanw
- ce_X_t_loanw
unit: 与媒体主面板同引擎同列名, 权重来自披露授信上限(MaxLoan), 量纲随各自源列 X 而定
formula: "权重 w(company,bank,year) = 该公司该年对该银行的披露授信上限(MaxLoan), 银团贷款按 1/k 等分给 k 家成员银行; cw/ce 通式与媒体主面板一致, 差异仅在权重来源"
producer: company_listed_bank/pipeline/03_build_altweight_panels.py (scheme=loan 分支)
upstream:
- _company_bank_altweights_loan.parquet (贷款关系强度长表)
- news_process 40_panel_yearly.parquet (被加权源列 X 取值来源)
citations:
- doi: 10.1111/j.1540-6261.1994.tb04418.x
  type: journal
  authors: Petersen, M. A., & Rajan, R. G.
  year: 1994
  title: "The benefits of lending relationships: Evidence from small business data"
  venue: The Journal of Finance
  vol: 49
  issue: 1
  pages_or_artno: 3-37
- doi: 10.1086/296668
  type: journal
  authors: Berger, A. N., & Udell, G. F.
  year: 1995
  title: "Relationship lending and lines of credit in small firm finance"
  venue: The Journal of Business
  vol: 68
  issue: 3
  pages_or_artno: 351-381
- doi: 10.1016/j.jfi.2021.100923
  type: journal
  authors: Banerjee, R. N., Gambacorta, L., & Sette, E.
  year: 2021
  title: "The real effects of relationship lending"
  venue: Journal of Financial Intermediation
  vol: 48
  issue: ""
  pages_or_artno: "100923"
- doi: 10.1016/j.jfi.2024.101101
  type: journal
  authors: Kutzbach, M. J., & Pogach, J.
  year: 2024
  title: "Financial technology and relationship lending: Complements or substitutes?"
  venue: Journal of Financial Intermediation
  vol: 59
  issue: ""
  pages_or_artno: "101101"
---

## CORE

本家族覆盖贷款权面板 company_bank_loanw_panel 的构造逻辑与口径披露, 是七替代权面板中与关系借贷经典命题联系最直接的一支。权重来源于公司对银行的披露授信上限, 而非实际提款余额, 这一选择的动机是授信上限相对稳定, 可视为一种存续暴露的恒额代理, 而实际余额随企业资金需求逐月波动, 不适合作为年度关系强度的稳定测度; 但使用者须清楚意识到授信上限与信贷存量是两个不同构念, 恒额代理天然带有测量误差。

数据存在两处系统性局限须显式披露。其一是左截断: 二零零七年之前签约存续的授信记录不可观测, 这意味着面板早期的贷款权在方法论上偏向低估长期关系深度, 建议对早期年份做敏感性检验时以约二零一零年起为稳健窗口。其二是银团贷款处理: 当一笔授信由多家银行组成的银团联合提供时, 本项目按成员数量等分权重给每家银行, 这一简化处理在银团结构信息不完整时属于保守近似, 完整的领头行与跟贷行差异化权重留待后续版本引入。贷款关系构造关系强度权重的做法, 其理论根据可追溯到关系借贷文献的奠基性发现, 即银行与企业之间建立的紧密借贷联系能够缓解信息不对称并提升企业融资可得性, 这一命题此后被大量拓展研究反复验证, 包括对信贷额度与关系深度交互效应的考察, 以及对关系借贷在信贷收缩期真实经济效应的识别。近年的研究进一步关注金融科技对传统关系借贷模式的替代或互补效应, 这一新兴文献脉络提醒使用者, 贷款权面板衡量的是传统银企借贷关系的强度, 在金融科技渗透率较高的样本区间内, 该测度捕捉到的经济含义可能随时间发生结构性漂移, 解读跨年度趋势时应对此保持警觉。

贷款权在七替代权面板体系中的相对位置也值得单独说明。相较于以媒体共现为权重的主面板, 贷款权提供的是一种基于硬性财务契约事实而非公开报道的关系强度代理, 二者的信息来源性质截然不同: 媒体共现权重反映的是外部可观测的信息传播强度, 可能受到企业与银行双方公关策略、媒体资源禀赋等因素影响, 而贷款权则反映的是双方之间实际存在的合同约束关系, 二者理论上应当正相关但不必然重合, 一家公司完全可能与某银行有着密集的媒体报道但并无实质授信往来, 反之亦然。正因如此, 若某一实证结论在以媒体共现为权重与以授信规模为权重两种设定下均保持稳健, 则该结论对权重来源的具体假设不敏感, 稳健性证据强度显著提升; 若结论仅在媒体共现权重下成立而在贷款权下消失, 则需要审慎考虑该结论是否更多反映的是媒体关注度本身的效应, 而非真实的银企经济关系效应, 这一权重来源交叉验证的思路正是本项目设计七替代权面板体系的核心动机。授信上限数据本身的披露频率与详细程度在样本期内也存在制度性演进, 早期年份的披露规范相对宽松, 部分中小公司可能仅披露授信总额而不区分具体银行, 这类记录在权重构造中天然缺失, 该缺失模式与语料宇宙边界局限一样, 不属于随机缺失, 使用者在做跨年度比较时应结合披露规范演进背景审慎解读。

<!-- rendered-citations:begin -->
Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending relationships: Evidence from small business data. The Journal of Finance, 49(1), 3-37. https://doi.org/10.1111/j.1540-6261.1994.tb04418.x
Berger, A. N., & Udell, G. F. (1995). Relationship lending and lines of credit in small firm finance. The Journal of Business, 68(3), 351-381. https://doi.org/10.1086/296668
Banerjee, R. N., Gambacorta, L., & Sette, E. (2021). The real effects of relationship lending. Journal of Financial Intermediation, 48, 100923. https://doi.org/10.1016/j.jfi.2021.100923
Kutzbach, M. J., & Pogach, J. (2024). Financial technology and relationship lending: Complements or substitutes?. Journal of Financial Intermediation, 59, 101101. https://doi.org/10.1016/j.jfi.2024.101101
<!-- rendered-citations:end -->
