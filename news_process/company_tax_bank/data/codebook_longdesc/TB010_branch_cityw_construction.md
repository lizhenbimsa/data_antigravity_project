---
family_id: TB010
novelty_exempt_rationale: "该家族是城市网点权(branch_cityw)构造定义披露, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- company_tax_bank_branch_cityw_panel
- rel_n_banks
- rel_hhi
unit: cw_X_t/ce_X_t 通式, 权重=城市层存续网点数, 量纲随各自源列 X 而定
formula: "w(company,bank,year)=企业注册地所在城市当年该银行存续网点数 (ApprovalDate≤t ∧ 非退出 ∧ 非失控); cw/ce 通式与媒体主面板一致, 权重来源换为城市层网点存量"
producer: company_tax_bank/pipeline/03_build_altweight_panels.py (scheme=branch_city 分支)
upstream:
- config/银行业金融机构基本信息表.dta (603,907行商业数据权源, 经BankCanon规范化)
- _company_tax_bank_altweights_branch_city.parquet (城市层网点关系强度长表)
citations:
- doi: 10.1086/296668
  type: journal
  authors: Berger, A. N., & Udell, G. F.
  year: 1995
  title: "Relationship lending and lines of credit in small firm finance"
  venue: The Journal of Business
  vol: 68
  issue: 3
  pages_or_artno: 351-381
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
---

## VAR

城市网点权面板是双替代权体系中粒度较粗的一支, 以企业注册地所在城市为空间单元, 统计该市当年处于存续状态的每家银行网点数量作为权重来源。存续状态的判定采用三重条件的交集: 该网点的批复设立日期须早于或等于当年年末, 且尚未因主动退出而在当年之前完成退出手续, 且尚未因经营失控被监管注销, 三个条件同时满足才计入当年存量, 这一存续窗口的判定方式确保网点权重反映的是当年年末的真实供给存量而非累积开设数量, 后者会随时间单调增长, 无法反映银行网点的进入退出动态。构造这一权重的根本动机与贷款权面板一致, 均是为了给媒体共现权提供一个基于真实经济关系而非报道行为本身的对照臂, 关系借贷经典研究揭示银行与企业之间地理与业务上的紧密联系能够缓解信息不对称并提升信贷可得性, 银行网点的物理存在正是这种紧密联系最直观可观测的代理指标之一。

由于城市这一空间单元覆盖范围较宽, 绝大多数地级市内同时存续多家银行的多个网点, 城市层网点权重集中度测度整体偏低, 这意味着以城市网点权为权重构造出的加权测度更接近城市层面银行业整体构成的均值, 而非某一家或某几家银行的专属暴露, 企业固定效应控制后, 该权重能够识别的变异主要来自网点的进入与退出而非截面层面的银行选择, 分析端在解释系数时应对这一构念性质保持清醒, 尤其要警惕城市固定效应与企业固定效应联合纳入模型时可能出现的共线性问题。近年关于关系借贷真实经济效应的实证研究进一步表明, 银行地理网络的密度变化本身即可作为识别银行信贷供给冲击的合法工具, 这类研究的识别逻辑与本权重面板构造网点存量作为暴露代理的思路高度一致, 为城市网点权作为媒体共现权的稳健性对照臂提供了额外的方法论支持。城市网点权与其粒度更细的县域对应版本共享同一权源数据表, 二者是同一权重来源的空间粒度梯子, 论文写作端须在两者之间预先声明主口径层级。

城市网点权在实际应用中还承担着一项常被忽视的功能, 即为媒体共现权提供一个"下界锚点"式的对照参照系: 若某一企业与某家银行的媒体共现权重明显高于该银行在企业所在城市的网点权重份额, 这一背离本身即可能构成值得进一步追问的信号, 提示该企业与该银行之间的媒体关注度可能受到共现权重之外的因素驱动, 例如企业自身的新闻曝光策略或该银行在特定时期的公关活动强度, 而非单纯反映真实的地理与业务关联紧密程度。这一"背离即信号"的解读逻辑并非本项目独创, 而是与关系借贷真实经济效应研究中利用银行网点密度变化识别信贷供给冲击的识别策略同源, 该策略的核心洞见在于, 银行物理存在的变化提供了一个相对外生于企业自身行为的暴露基准, 任何显著偏离这一基准的测度都值得被单独标注并纳入稳健性讨论, 而不应被默认视为噪声一并忽略。城市网点权因其粒度较粗, 在提供这一基准功能时天然比县域网点权更稳定, 波动性更低, 这也是双替代权体系保留城市这一粗粒度层级而非只保留更细粒度县域层级的另一重考虑。

<!-- rendered-citations:begin -->
Berger, A. N., & Udell, G. F. (1995). Relationship lending and lines of credit in small firm finance. The Journal of Business, 68(3), 351-381. https://doi.org/10.1086/296668
Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending relationships: Evidence from small business data. The Journal of Finance, 49(1), 3-37. https://doi.org/10.1111/j.1540-6261.1994.tb04418.x
Banerjee, R. N., Gambacorta, L., & Sette, E. (2021). The real effects of relationship lending. Journal of Financial Intermediation, 48, 100923. https://doi.org/10.1016/j.jfi.2021.100923
<!-- rendered-citations:end -->
