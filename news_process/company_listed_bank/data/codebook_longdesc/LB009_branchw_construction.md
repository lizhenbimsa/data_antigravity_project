---
family_id: LB009
columns:
- company_bank_branchw_panel
- cw_X_t_branchw
- ce_X_t_branchw
unit: 与媒体主面板同引擎同列名, 权重来自城市代理网点数(整数计数), 量纲随各自源列 X 而定
formula: "权重 w(company,bank,year) = 公司注册或办公城市内该银行存续网点数(单城市代理); cw/ce 通式与媒体主面板一致, 差异仅在权重来源为地理邻近而非媒体共现"
producer: company_listed_bank/pipeline/03_build_altweight_panels.py (scheme=branch 分支)
upstream:
- _company_bank_altweights_branch.parquet (网点地理邻近关系强度长表)
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
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1146/annurev-economics-083120-111540
  type: journal
  authors: Jackson, M. O., & Pernoud, A.
  year: 2021
  title: "Systemic risk in financial networks: A survey"
  venue: Annual Review of Economics
  vol: 13
  issue: ""
  pages_or_artno: 171-202
- doi: 10.1086/296668
  type: journal
  authors: Berger, A. N., & Udell, G. F.
  year: 1995
  title: "Relationship lending and lines of credit in small firm finance"
  venue: The Journal of Business
  vol: 68
  issue: 3
  pages_or_artno: 351-381
---

## CORE

本家族覆盖网点权面板 company_bank_branchw_panel 的构造逻辑, 是七替代权面板中以地理邻近而非人事或资金联结衡量银企关系强度的一支。权重取自公司注册或办公所在城市内该银行的存续网点数量, 隐含的经济逻辑是物理网点密度越高, 该银行在当地获取企业软信息、维系日常业务往来的便利程度越高, 这一逻辑与关系借贷文献中强调的软信息传递机制一脉相承, 银行分支网络的地理布局本身即是软信息生产能力的一种可观测代理。

本权重存在两点需要显式说明的构念特征。其一, 权重采用单一城市代理, 对于跨地区多城市经营的公司而言, 单城市口径无法完整刻画公司实际经营版图与银行网点覆盖的重叠关系, 存在结构性失真风险, 且该失真与公司规模正相关, 规模越大的公司跨地区经营概率越高。其二, 网点权在样本内的分布呈现出高度稠密的结构特征, 赫芬达尔集中度指数普遍处于较低区间, 这意味着以网点权加权得到的测度在很大程度上近似于该城市银行体系构成的平均水平, 若回归模型同时纳入公司固定效应与城市固定效应, 网点权能够识别的有效变异将主要来自银行网点的进入与退出这类边际调整, 而非横截面上的城市间差异, 使用者在设定固定效应结构时应对这一共线性风险保持警觉。网点地理布局对企业融资可得性的影响这一命题, 在公司网络效应研究中也有呼应, 相关文献指出企业间乃至企业与关系方之间的空间与网络联结会通过对等效应渠道影响资本结构决策, 网点权本质上提供的正是这样一种基于地理邻近的关系联结测度, 是媒体共现权重之外一种独立的、基于制度性可观测事实构造的稳健性对照。金融网络系统性风险研究进一步提示, 任何网络暴露测度的构造本身都隐含特定的识别假设, 网点权的城市代理设定同样需要在此框架下审慎解读。

网点权与贷款权、股东权等其余权重臂的一个关键区别在于其外生性程度相对更高。银行网点的选址决策通常遵循银行自身的区域扩张战略与监管审批节奏, 在短期内对单个企业的经营状况或媒体形象变化的敏感度较低, 相较于媒体共现权重或贷款授信权重更容易受到企业自身特征的反向影响, 网点权在识别策略上因而具有相对更强的准外生性, 这使得网点权在稳健性检验中往往被赋予更高的说服力, 尤其是在研究者担心权重内生于企业未来结果这一威胁时, 网点权可以作为相对更干净的对照臂。但准外生性并非绝对外生, 银行网点布局仍可能随区域经济发展水平的变化而调整, 若企业所在城市本身正处于经济高速增长阶段, 该城市银行网点扩张与企业自身经营改善可能存在共同驱动因素, 这一混淆路径在实证应用中不可完全排除, 建议使用者在关键识别结论上同时纳入城市层面的经济增长控制变量或城市固定效应加以缓解。此外, 由于网点权原始数据以银行分支机构在各城市的物理存在为基础, 其时间维度上的变化频率明显低于媒体共现或贷款授信这类年度可变数据, 面板中网点权的年际变异主要来自银行网点的新设或撤并这类相对稀疏的事件, 使用者在设计固定效应模型时应留意样本期内网点权的组内变异幅度, 变异过小可能导致相关回归系数的估计精度受限。

<!-- rendered-citations:begin -->
Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending relationships: Evidence from small business data. The Journal of Finance, 49(1), 3-37. https://doi.org/10.1111/j.1540-6261.1994.tb04418.x
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Jackson, M. O., & Pernoud, A. (2021). Systemic risk in financial networks: A survey. Annual Review of Economics, 13, 171-202. https://doi.org/10.1146/annurev-economics-083120-111540
Berger, A. N., & Udell, G. F. (1995). Relationship lending and lines of credit in small firm finance. The Journal of Business, 68(3), 351-381. https://doi.org/10.1086/296668
<!-- rendered-citations:end -->
