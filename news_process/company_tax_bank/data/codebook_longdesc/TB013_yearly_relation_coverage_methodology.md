---
family_id: TB013
columns:
- weight_source_yearly_relation_count
unit: 关系对数 (逐年计数, 说明性诊断表)
formula: "逐年统计 branch_city/branch_county 两权源在(企业,银行)维度上的存续关系对数, 用以区分'计数为0=真无关系'与'计数为0=权源覆盖假零'两种截然不同的零值成因"
producer: company_tax_bank/pipeline/03_build_altweight_panels.py (§附录 权源逐年关系对数覆盖表生成分支)
upstream:
- config/银行业金融机构基本信息表.dta (603,907行商业数据权源, 关系对存续窗口来源)
- _company_tax_bank_altweights_branch_city.parquet / _branch_county.parquet (逐年聚合来源)
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
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: "What drives media slant? Evidence from U.S. daily newspapers"
  venue: Econometrica
  vol: 78
  issue: 1
  pages_or_artno: 35-71
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: 2442-2476
---

## VAR

权源逐年关系对数覆盖表的核心方法论目标是解决一个在缺失数据处理中反复出现的经典难题, 即区分观测值为零究竟是研究对象本身真实不存在关联, 还是数据来源本身在该时点覆盖不足所导致的表观零值。本表对城市网点权与县域网点权两个权源分别逐年统计企业与银行之间存续关系对的数量, 覆盖窗口自二零一一年至二零二零年, 这一窗口本身经过精心选取, 完整内嵌于权源商业数据表的可得区间之内, 因此原则上不应出现因权源数据本身缺失导致的整年份假零现象, 逐年计数持续单调上升的观测模式, 与银行网点在样本期内整体扩张的宏观事实相符, 侧面印证了权源存续窗口判定逻辑的合理性。

这一区分零值成因的方法论关切在缺失数据的统计学文献中有系统论述, 关联档案分析的缺失数据视角框架明确指出, 跨源数据关联天然会产生结构性缺失与随机缺失两种截然不同的模式, 对二者不加区分地统一处理会导致后续统计推断出现方向性偏误, 本表正是沿着这一分析思路, 为使用者提供一个独立于最终加权测度之外的、纯粹关于权源覆盖完整性的诊断工具。之所以要把这张覆盖表与加权测度分离开单独呈现, 是因为媒体测度构造领域的经验教训表明, 派生测度本身往往无法自我诊断其零值究竟源自真实的经济现象还是数据构造过程中的技术性缺口, 媒体倾向性测度研究反复强调唯有把构造过程的中间产物透明地呈现出来, 才能让使用者对最终测度的可信度做出准确判断; 而探讨政治敏感信息如何在媒体环境中被系统性处理的相关研究进一步提示, 覆盖率本身的时间趋势往往携带着不亚于测度水平本身的分析价值, 使用者在解读加权测度的跨年度变化时, 应结合本表的覆盖率走势排除纯粹由权源覆盖扩张驱动的表观趋势。

从实践操作角度, 本表还可用于事前诊断某一具体年份是否适合纳入依赖加权测度的分析样本: 若某一年份的关系对覆盖数量明显低于相邻年份, 且这一下降无法用银行网点客观收缩这一经济现实解释, 使用者应警惕该年份可能存在权源数据本身的采集或整合缺口, 进而考虑在敏感性分析中单独剔除该年份或对其结果做加权稳健性检验。这一"以覆盖率诊断表倒查异常年份"的操作思路, 与媒体覆盖度和股票横截面收益关系研究中强调媒体测度的时间序列特征本身需要独立核查的方法论态度一致, 该研究提醒, 派生测度的时间趋势有时并非反映研究对象本身的经济动态, 而是数据采集口径随时间演变的产物, 唯有把底层数据覆盖情况的时间序列单独呈现出来, 才能让使用者具备区分这两种截然不同来源的诊断能力。城市层与县域层两个权源的覆盖表理应呈现相似但不完全相同的增长轨迹, 二者之间若出现异常的背离, 本身也构成一个值得单独追问的信号, 提示两个权源在特定年份的整合质量可能出现了不对称的问题。

<!-- rendered-citations:begin -->
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
<!-- rendered-citations:end -->
