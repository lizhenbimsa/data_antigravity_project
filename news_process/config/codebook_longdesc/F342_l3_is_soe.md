---
family_id: F342
columns:
- is_soe
unit: 二值哑变量 (0/1, 无量纲)
formula: 'is_soe = 1{bank_type == "soe"}; 若面板缺失 bank_type 列则 is_soe 恒置 0 并写 WARNING 日志'
producer: pipeline\panel\runner.py (步骤 7g-het 异质性分析交互项预计算区块)
upstream:
- bank_type (由步骤 7e compute_bartik_iv() 生成的银行类型分类列)
citations:
- doi: 10.48550/arXiv.2605.29188
  type: arxiv
  authors: Gong, T., & Sun, S.
  year: 2026
  title: 'Slogans or stance? A label-light diagnostic for entrepreneurial-discourse
    measurement on Chinese SOE speeches'
  venue: arXiv
- doi: 10.1086/261354
  type: journal
  authors: Demsetz, H., & Lehn, K.
  year: 1985
  title: 'The structure of corporate ownership: Causes and consequences'
  venue: Journal of Political Economy
  vol: '93'
  issue: '6'
  pages_or_artno: 1155-1177
- doi: 10.1016/j.chieco.2023.101973
  type: journal
  authors: Choi, H., Kim, J. H., Suh, J., & Yu, S.
  year: 2023
  title: Ownership concentration and financial policy of China's listed firms
  venue: China Economic Review
  vol: '79'
  pages_or_artno: Article 101973
- doi: "10.1093/wber/lhaf024"
  type: "journal"
  authors: "Betts, C. M., & Cao, Y."
  year: 2025
  title: "How Does State Ownership Affect Firm Innovation? Evidence from Chinese Manufacturing Firms"
  venue: "The World Bank Economic Review"
  pages_or_artno: "lhaf024"
new_dois:
- 10.1086/261354
- 10.1016/j.chieco.2023.101973
---

## CORE

【构念与来源】
is_soe 是银行年度面板里的一个二值哑变量, 记录目标银行在给定观测年是否属于国有(state-owned enterprise, SOE)控制类别: 银行分类为国有(bank_type == "soe")时取 1, 否则取 0。该列不是从新闻文本或情感测度衍生的行为变量, 而是一个静态的银行所有制身份标签, 直接由上游步骤 7e (compute_bartik_iv, 生成 bank_type 分类列) 传导而来, 在步骤 7g-het (异质性分析交互项预计算) 中一次性物化。producer 源码里紧邻的注释块明确了引入本列的学理动机: 交互项模型要同时保留主效应 (constituent terms) 才不会让交互系数产生偏误, 这是计量方法论中处理交互效应模型规范的通行共识, 要求任何形如 A×B 的交互项回归都必须同时纳入 A 与 B 各自的主效应, 否则交互系数的估计与解读会失去基准可比性。is_soe 因此首先是作为交互项的主效应 (constituent term) 而非独立解释变量被构造出来的: 一旦研究者要检验"新闻情感对银行结果变量的影响是否因所有制类型而异"(如 llm_vote_tone_full × is_soe), 就必须让 is_soe 本身作为主效应同时进入回归, 否则交互系数的识别会受到污染。
【方法学与计算】
计算逻辑极简且确定性: 若面板已含 bank_type 列(该列取值集合含 'soe' 与其余类别, 由步骤 7e 的银行分类逻辑赋值), 则 is_soe 通过布尔比较 (panel['bank_type'] == 'soe') 转 int 一次性向量化生成; 若 bank_type 因任何上游原因缺失(如某次调试性子集运行未跑到步骤 7e), producer 走保护性分支, 记录 WARNING 日志并将 is_soe 全体置 0, 而不是中断整条流水线。这是一个刻意的"优雅降级而非静默污染"设计: 降级会在日志里留痕(`bank_type 不存在, is_soe 设为 0`), 使用者据此可判断该次运行中 is_soe 是否具备真实区分力, 避免误把全零列当成"全样本非国有"的实质结论。is_soe 不涉及任何三轨(full/ctx/ss)或 co-primary 嵌入维度——它是与文本测度架构完全正交的银行属性静态标签, 逐年不变（同一银行跨年度的所有制身份在样本窗口内通常保持稳定, 除非发生股权结构性变更并被上游 bank_type 分类逻辑捕捉到), 因此不适用"各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J"这一套多轨/多模型铁律——它只有一列、一个口径, 没有平行的稳健性变体。
【文献定位】
本列在计量框架中扮演的角色是经典的所有制结构异质性调节变量(moderator), 其学理谱系可追溯到公司治理文献对"谁控制企业、控制权结构如何影响企业行为与绩效"的长期研究传统。Demsetz & Lehn (1985, Journal of Political Economy) 研究的是美国企业股权集中度的决定因素与后果, 与本列"国有/非国有"这一中国情境下的所有制身份分类并非同一构念——该文不涉及国有企业分类, 这里仅取其"控制权结构并非随机分布而是内生于企业所处的治理环境, 因而不应被当作任意分组"这一更一般化的方法论洞见作为类比性参照, 提示读者对待 is_soe 这类粗粒度所有制标签时也需留意其内生性, 而非将其直接等同于该文的实证发现。就中国银行业情境而言, 国有控股与非国有控股银行在信贷配置动机、政策性负担、风险偏好与对外部媒体关注的反应模式上存在系统性差异, 这正是 is_soe 被设计为异质性交互项主效应的实证动机——Choi, Kim, Suh & Yu (2023, China Economic Review) 提供了中国上市公司情境下"股权集中度→企业融资/负债政策"的直接证据, 印证所有制/控制权变量在中国企业金融决策研究中的核心调节地位。Gong & Sun (2026, arXiv 预印本) 则从方法学角度讨论了中国国有企业话语(SOE speeches)测度中"口号 vs. 立场"的诊断问题, 提醒研究者在处理涉及国企身份的文本/标签变量时需警惕表面合规话语与实质立场的错配, 这一提醒对本列的下游使用(尤其是把 is_soe 与情感/态度类文本测度做交互时)具有直接的方法学参照价值: 不应简单假设国有银行的新闻语调差异必然反映真实的经营立场差异, 而应结合具体交互设定审慎解读系数。 在"中国情境下国有产权是否构成实质性的异质性维度"这一前提上, Betts 与 Cao (2025) 以中国制造业企业为样本, 以国有/非国有的产权二分作为核心自变量, 识别国有产权对企业创新行为的影响, 为 is_soe 这类粗粒度产权哑变量作为调节轴承载真实的结构性差异(而非任意分组)提供了近期实证依据。迁移边界须明确标出: 该文样本为制造业企业而非商业银行, 其国有企业界定标准与本列依赖上游 bank_type 列判定(缺失时恒置 0 并记 WARNING)的二分口径并不一致; 其 DV 为企业创新, 全文未涉及媒体语调或任何文本测度, 因而对 llm_vote_tone_full × is_soe 一类交互设定仅提供"产权分组有意义"的一般性支持, 并不支撑语调 × 产权的任何具体机制主张, 引用时不得据此推断国有银行的新闻语调差异必然对应经营行为差异。
## VAR: is_soe

【变体差分】
本家族目前仅含 is_soe 这一列, tier 标记为 standard, 不存在同一家族内的平行变体(无阈值梯子、无 per-model 分支、无三轨镜像), 因此本节的"差分语义"聚焦于该列自身的边界条件与解读注意事项, 而非与家族内其他列的对比。首先, is_soe 的取值口径是二元且互斥的: bank_type == 'soe' 记 1, 其余一切非国有分类(包括但不限于股份制商业银行、城商行、农商行、外资银行等 bank_type 分类结果) 一律记 0, 也就是说 is_soe 不区分"国有独资"与"国有相对控股"等更细粒度的国有化程度, 是一个粗粒度的二分类哑变量而非连续的国有持股比例测度; 若下游研究需要国有化程度的连续测度, 应寻找面板中是否有更细的股权比例列, 而不能把 is_soe 当作连续变量的替代。其次, is_soe 的构造严格依赖上游 bank_type 列的可得性与正确性: bank_type 由步骤 7e 的 Bartik IV 构造流程副产, 若该步骤因数据缺失或配置问题未能正确分类某些银行, is_soe 会继承这一分类误差, 而不是独立重新判定所有制身份; 使用者在解读涉及 is_soe 的异质性分析结果前, 应先确认同批次面板日志中步骤 7e/7g-het 的分类分布(SOE=N 条 vs 非SOE=M 条)是否符合先验认知, 避免因上游分类失败导致 is_soe 退化为全零列而把"无异质性"误读为"国有属性不重要"这一实质性结论。第三, 本列在设计上主要不是被当作独立的解释变量或控制变量使用, 而是作为与其他核心解释变量(如银行金科报道情感、覆盖强度分组等)构造交互项时的主效应(constituent term)伴随进入回归; 因此在任何包含 is_soe × X 交互项的回归设定中, 应始终同时保留 is_soe 与 X 各自的主效应系数, 这是交互效应模型规范的基本要求, 也是本列被单独物化(而非仅在交互项构造时临时计算)的直接原因——单独持久化 is_soe 使得下游多个 paper 模块能复用同一份口径一致的所有制标签, 而不必各自重新从原始银行名单反推所有制类型, 从而保证跨 paper 模块间"国有 vs 非国有"这一分类边界的一致性。需特别澄清的是, is_soe 在下游的真实复用场景与"异质性交互项 HET_VAR"是两个不同的模板变量、不可混为一谈: benefit_society 的 13_table4_heterogeneity.do.tmpl 模板里 {{HET_VAR}} 占位符实际硬编码为 is_listed (是否上市这一维度), is_soe 并未作为该模板的 HET_VAR 被传入, 也从未在 benefit_society 异质性分析中充当过交互项主效应的候选; is_soe 真正被复用的场景是同一 paper 目录下 27_tableA14_subsample_composition.do.tmpl 里的所有制子样本构成表——该模板按 is_soe==1 与 is_soe==0 切分子样本, 报告国有/非国有两类银行各自的样本构成与描述性统计, 属于子样本切分(subsample split)机制而非交互项异质性(heterogeneity interaction)机制。两者虽然都服务于"按所有制维度审视结果是否稳健"这一广义研究问题, 但在计量实现上分属不同模板、不同占位符、不同统计逻辑, 使用者若把 is_soe 误当作可以直接替换进 {{HET_VAR}} 占位符的交互异质性候选变量, 会与 benefit_society 主线模板的实际硬编码脱节。

<!-- rendered-citations:begin -->
Gong, T., & Sun, S. (2026). Slogans or stance? A label-light diagnostic for entrepreneurial-discourse measurement on Chinese SOE speeches. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2605.29188
Demsetz, H., & Lehn, K. (1985). The structure of corporate ownership: Causes and consequences. Journal of Political Economy, 93(6), 1155-1177. https://doi.org/10.1086/261354
Choi, H., Kim, J. H., Suh, J., & Yu, S. (2023). Ownership concentration and financial policy of China's listed firms. China Economic Review, 79, Article 101973. https://doi.org/10.1016/j.chieco.2023.101973
Betts, C. M., & Cao, Y. (2025). How Does State Ownership Affect Firm Innovation? Evidence from Chinese Manufacturing Firms. The World Bank Economic Review, lhaf024. https://doi.org/10.1093/wber/lhaf024
<!-- rendered-citations:end -->
