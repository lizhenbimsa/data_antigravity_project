---
family_id: TB011
novelty_exempt_rationale: "该家族是县域网点权(branch_countyw)构造与缺键语义定义披露, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- company_tax_bank_branch_countyw_panel
- county_key_ok
- rel_n_banks
unit: cw_X_t/ce_X_t 通式, 权重=(城市,区县)复合层存续网点数, 量纲随各自源列 X 而定
formula: "w(company,bank,year)=企业注册地(城市,区县)复合键内当年该银行存续网点数; county_key_ok=1 表复合键有效(含(i)退化键), =0 表直筒子/复合键无匹配/境外缺键, 该子集县权全缺失NaN且不回退城市层"
producer: company_tax_bank/pipeline/03_build_altweight_panels.py (scheme=branch_county 分支)
upstream:
- config/银行业金融机构基本信息表.dta (603,907行商业数据权源, 区县字段来源)
- _company_tax_bank_altweights_branch_county.parquet (县域层网点关系强度长表)
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
- doi: 10.1016/j.jfi.2024.101101
  type: journal
  authors: Kutzbach, M. J., & Pogach, J.
  year: 2024
  title: "Financial technology and relationship lending: Complements or substitutes?"
  venue: Journal of Financial Intermediation
  vol: 59
  issue: ""
  pages_or_artno: "101101"
- doi: 10.1086/296668
  type: journal
  authors: Berger, A. N., & Udell, G. F.
  year: 1995
  title: "Relationship lending and lines of credit in small firm finance"
  venue: The Journal of Business
  vol: 68
  issue: 3
  pages_or_artno: 351-381
- doi: 10.1257/app.20170543
  type: journal
  authors: Nguyen, H.-L. Q.
  year: 2019
  title: "Are credit markets still local? Evidence from bank branch closings"
  venue: "American Economic Journal: Applied Economics"
  vol: 11
  issue: 1
  pages_or_artno: 1-32
---

## VAR

县域网点权面板是双替代权体系中粒度更细的一支, 空间单元由城市与区县两级字段联合构成复合键, 权重来源同为存续网点数量, 但统计范围收窄到企业注册地所在区县而非整个城市, 理论上应当比城市层权重具有更强的集中度与更精细的经济关系刻画能力。然而这一细化在实践中带来了本项目最尖锐的缺失语义问题: 权源表的区县字段与税调企业名录的区县字段并非在任何情形下都能对齐, 一部分企业的区县信息因权源表本身记录粒度不足或税调名单批次质量问题而无法参与复合键匹配, 由此产生的县权缺失在数值形态上与"该企业周边确实没有任何银行网点"这种真实的零暴露完全相同, 二者若不加区分, 会让使用者误把技术性缺键当作经济意义上的真零, 从而得出错误的构念解读。

为解决这一识别难题, 本项目专门引入 county_key_ok 这一仅存在于县权面板的标识列, 用以显式区分复合键是否有效: 取值为一代表企业存在可用于匹配的有效复合键, 包括一类特殊的退化键情形, 即部分省或自治区直辖县级市因行政区划本身缺少更细层级, 复合键被构造为退化态直接等同城市层键; 取值为零则涵盖三类不可匹配情形, 分别是区县字段记为占位符的直筒子式企业、复合键在权源表中确实找不到对应记录的企业, 以及区县信息本身空缺的境外或异常记录。这一缺失数据处理逻辑与关联档案分析的方法论框架高度契合, 该框架系统论证了跨源关联数据中缺失模式往往并非随机产生, 而是与数据源本身的记录粒度、行政区划变更等结构性因素相关联, 必须通过专门的标识机制加以区分, 而非简单假设缺失等价于零。本项目刻意选择不将县权缺失回退到城市层填补, 这一设计决策的根据在于, 回退操作会让县域权在数值上直接复制城市权的取值, 从而破坏两个权重版本互为独立稳健性对照的前提, 削弱双替代权设计本应提供的额外识别力, 这一取舍与金融科技渗透背景下重新审视传统关系借贷地理暴露测度构念边界的研究思路是一致的, 即测度构念的精细化应当以不牺牲测度间的独立性为前提。

从使用者操作层面看, county_key_ok 这一标识列的正确使用姿态是先按该列的取值把样本一分为二, 再分别在两个子样本内解读县域网点权的经济含义: 在标识为一的子样本内, 县域权是比城市权更细粒度、理论上信息量更丰富的暴露测度, 适合作为主口径参与回归分析; 在标识为零的子样本内, 县域权列本身取值为缺失而非零, 任何试图将其当作数值参与建模的做法都会引入系统性偏误, 正确的处理方式是要么将该子样本从依赖县域权的分析中剔除, 要么明确改用城市权作为该子样本的替代口径并在论文中如实说明这一切换。这一"先按标识列分层再分别建模"的操作纪律, 与关联档案分析框架强调的"缺失模式本身应当被建模而非被忽略"的方法论立场高度一致, 也与金融科技渗透背景下重新审视关系借贷地理暴露测度构念边界的研究思路相呼应, 该研究提醒后续使用者, 地理暴露类测度的构念有效性高度依赖于底层行政区划匹配的完整性, 匹配缺口若被静默处理为零, 会直接扭曲后续基于该测度展开的实证推断方向。

县域粒度细化本身的构念价值在银行地理研究的顶刊证据中有直接支撑: Nguyen 于 2019 年利用银行网点关闭事件的准实验设计证明, 即便在信息技术高度发达的当代, 信贷市场在很大程度上仍然是地方性的, 网点在地与否对周边小企业信贷供给有实质影响且影响随距离迅速衰减, 这说明以更细的空间单元刻画企业与银行网点的地理暴露并非精度上的锦上添花, 而是贴近信贷供给真实作用半径的必要细化, 也正因如此, 县权缺失语义的严谨处理才值得本条目如此篇幅的专门披露。

<!-- rendered-citations:begin -->
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
Kutzbach, M. J., & Pogach, J. (2024). Financial technology and relationship lending: Complements or substitutes?. Journal of Financial Intermediation, 59, 101101. https://doi.org/10.1016/j.jfi.2024.101101
Berger, A. N., & Udell, G. F. (1995). Relationship lending and lines of credit in small firm finance. The Journal of Business, 68(3), 351-381. https://doi.org/10.1086/296668
Nguyen, H.-L. Q. (2019). Are credit markets still local? Evidence from bank branch closings. American Economic Journal: Applied Economics, 11(1), 1-32. https://doi.org/10.1257/app.20170543
<!-- rendered-citations:end -->
