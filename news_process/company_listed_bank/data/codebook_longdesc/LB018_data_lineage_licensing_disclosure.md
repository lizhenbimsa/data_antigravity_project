---
family_id: LB018
columns:
- data_provenance_disclosure_conceptual
unit: 概念性说明, 无独立数值量纲
formula: "无公式; 数据谱系披露 = 供应商/库名/表编号/提取日期/过滤条件/许可/第三方获取路径 七字段清单, 生产机回填终值"
producer: company_listed_bank/data/company_bank_cooc_panel_codebook.md 数据谱系节(手工维护, 商业数据库四权源 dta 恒不入库)
upstream:
- company_listed_names.yaml / bank_names.json (随复现包分发的商业派生名单 SSOT)
- 四权源商业数据库 dta (恒不入库, .gitignore 排除)
citations:
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: 2442-2476
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  issue: ""
  pages_or_artno: 171-202
- doi: 10.2308/JFR-2021-003
  type: journal
  authors: Breuer, M.
  year: 2022
  title: "Bartik instruments: An applied introduction"
  venue: Journal of Financial Reporting
  vol: 7
  issue: 1
  pages_or_artno: 49-67
---

## CORE

本家族覆盖本项目数据谱系与再分发许可的披露规范, 是复现包能否被安全共享的关键前置说明。本项目的加权测度族依赖多个商业数据库作为关系强度权重的原始来源, 包括贷款、网点、董监高联结与股东持股四类权源表, 这些商业数据库产品本身受供应商许可条款约束, 不能与本项目的公开代码和衍生面板一并无条件分发, 数据谱系披露表的作用正是以结构化字段的方式记录每一权源表的可追溯来源信息, 供使用者判断自身是否具备相应的访问资格, 以及在何种条件下可以合法获取原始权源数据。

披露表设计了七个结构化字段, 覆盖供应商名称、数据库名称、具体表编号、数据提取日期、所应用的过滤条件、许可类型、以及第三方复现者应循的获取路径, 这一结构化披露的思路与媒体研究文献中长期强调的数据可得性与可复现性声明规范相呼应, 学术研究越来越要求作者在论文附录中明确说明专有数据的获取渠道与限制条件, 而非笼统地声明数据不可公开。为兼顾可复现性与许可合规, 本项目采取了分级降级策略: 商业数据库原始明细表恒不入库, 通过版本控制系统的忽略规则从源头排除; 但派生出的实体匹配所需的公司与银行名称主清单作为较低敏感度的衍生产品随复现包一并分发, 供第三方复现实体识别与共现计算环节; 而更细粒度的行级关系长表则按需申请获取, 需求方须向数据谱系表中登记的原始供应商或本项目维护者单独申请访问权限。这一分级降级路径的设计逻辑, 与金融网络研究中对专有关系数据敏感性的一般性认知一致, 网络暴露测度的构造高度依赖底层关系数据的粒度, 而关系数据本身往往涉及商业机密或个人隐私, 因此披露规范必须在推动学术可复现性与保护数据提供方合法权益之间取得平衡, 供应商、库名、提取日期等字段的终值将在生产语料环境下完整回填。

数据谱系披露表的七字段设计还承担着另一项重要功能, 即为跨版本数据更新提供可追溯的锚点。商业数据库供应商通常会随时间对历史数据做回溯性修订, 包括修正历史披露错误、补充此前缺失的记录, 或因监管口径变化调整历史统计范围, 这类回溯性修订意味着同一权源表在不同提取日期获取的版本之间可能存在细微但非零的差异, 若不记录明确的提取日期, 使用者事后将无法判断某一具体权重数值究竟对应哪一个数据版本, 也无法在发现异常时判断异常究竟源于本项目的处理逻辑还是源于上游数据版本差异, 提取日期字段正是为解决这一版本可追溯性问题而设立。过滤条件字段的作用与之类似, 记录的是本项目在从原始商业数据库表中筛选相关记录时所应用的具体条件, 例如按公司代码范围筛选、按记录状态标志筛选或按最低金额阈值筛选, 这些过滤条件若不显式记录, 第三方复现者即便获得了与本项目相同的原始数据库访问权限, 也可能因为过滤条件理解偏差而重构出与本项目实际使用的样本不完全一致的衍生表, 造成看似相同数据源却得到不同复现结果的困惑。许可类型字段则直接决定了衍生产品的可分发范围, 部分商业数据库许可条款仅允许在授权机构内部使用衍生统计结果而不允许对外公开原始记录级数据, 这类许可限制是本项目坚持四权源商业数据库原始明细表恒不入库这一底线原则的直接法律依据, 而非仅出于审慎考虑的自我限制。

<!-- rendered-citations:begin -->
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Breuer, M. (2022). Bartik instruments: An applied introduction. Journal of Financial Reporting, 7(1), 49-67. https://doi.org/10.2308/JFR-2021-003
<!-- rendered-citations:end -->
