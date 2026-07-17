---
family_id: F501
columns:
- strat_diff_n40_lda
- strat_diff_n40_lda_ctx
- strat_diff_n40_lda_ss
unit: 无量纲距离得分, 值域 [0,1] (Jensen-Shannon 距离, base=2 时天然落在 [0,1], 非负向量/概率分布轨的通用值域口径)
formula: 'strat_diff_n{N}_lda = mean_{j∈N40NN(i)} JSD_dist(θ_i, θ_j), 其中 θ_i 为文章 i 的 LDA 主题分布向量 (topic-count 维单纯形), N40NN(i) 为按 JSD 距离升序取的 40 个"最近邻"同业文章 (top-k N 梯子 N=40 分量), JSD_dist 为 scipy jensenshannon(base=2) 计算的 Jensen-Shannon 距离 (即 Jensen-Shannon 散度的平方根, sqrt(JSD), 一个满足三角不等式的度量, Lin 1991 / Endres & Schindelin 2003)'
producer: pipeline\features\strategic_diff.py ; pipeline\panel\stata_export.py
upstream: []
citations:
- {doi: "10.1287/mnsc.2022.4369", type: journal, authors: "Guzman, J., & Li, A.", year: 2023, title: "Measuring Founding Strategy", venue: "Management Science", vol: "69", issue: "1", pages_or_artno: "101-118"}
- {doi: "10.1086/688176", type: journal, authors: "Hoberg, G., & Phillips, G.", year: 2016, title: "Text-Based Network Industries and Endogenous Product Differentiation", venue: "Journal of Political Economy", vol: "124", issue: "5", pages_or_artno: "1423-1465"}
- {doi: "10.1002/smj.3549", type: journal, authors: "Su, J., Gao, X., & Tan, J.", year: 2024, title: "Positioning for Optimal Distinctiveness: How Firms Manage Competitive and Institutional Pressures under Dynamic and Complex Environment", venue: "Strategic Management Journal", vol: "45", issue: "2", pages_or_artno: "333-361"}
- {doi: "10.1002/smj.2978", type: journal, authors: "Haans, R. F. J.", year: 2019, title: "What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories", venue: "Strategic Management Journal", vol: "40", issue: "1", pages_or_artno: "3-27"}
- {doi: "10.1257/jel.20181020", type: journal, authors: "Gentzkow, M., Kelly, B., & Taddy, M.", year: 2019, title: "Text as Data", venue: "Journal of Economic Literature", vol: "57", issue: "3", pages_or_artno: "535-574"}
- doi: "10.1111/1467-8551.12857"
  type: "journal"
  authors: "Kang, J., & Kang, Y."
  year: 2025
  title: "Capital Market Scrutiny and Strategic Distinctiveness of the Firm: Evidence from a Natural Experiment"
  venue: "British Journal of Management"
  vol: "36"
  issue: "1"
  pages_or_artno: "461-476"
- doi: "10.1002/sej.1521"
  type: "journal"
  authors: "Shen, R., Zhang, H., Zhong, W., & Lu, J."
  year: 2025
  title: "Distinctiveness from whom? Evaluation of startups' distinctiveness from multiple referents in angel investment platforms"
  venue: "Strategic Entrepreneurship Journal"
  vol: "19"
  issue: "1"
  pages_or_artno: "171-195"
new_dois: []
---

## CORE

【构念与来源】
strat_diff_n40_lda 系列度量的是"一篇银行金科报道在主题语义空间中相对同业的差异化程度", 属于 F501 家族"战略差异度 (strategic differentiation)"的 LDA 主题分布轨、top-k N=40 大邻域分量。构念直接承接文本战略度量文献: Hoberg & Phillips (2016) 用文本余弦相似度构造 TNIC 行业分类与产品差异度, Guzman & Li (2023) 用创业公司自我描述文本的 N-最近邻余弦距离刻画"创业战略的独特性", 本产出把同一"N-最近邻文本距离"范式迁移到中文银行金科新闻语料, 用以刻画银行在媒体呈现的金科战略叙事上与同业的疏离程度 (越大越"与众不同"、越小越"随大流"/趋同)。与家族内的字符级/词级 TF-IDF 轨、句向量 Embedding 轨并列, LDA 轨是三种文本表征方法之一, 走的是"先降维到主题分布单纯形、再用信息论散度量距离"的路线, 而非直接在高维稀疏或稠密向量空间量余弦/欧氏距离; 三种方法互为稳健性检验, 不设主次。
【方法学与计算】
计算分两步。第一步用银行金科语料训练的 LDA (Latent Dirichlet Allocation, Blei, Ng & Jordan 2003) 主题模型, 把每篇文章的分词文本 (口径见下)映射为一个固定维度的主题概率分布 θ_i (单纯形上的向量, 各分量非负且和为 1)。第二步对每篇文章 i, 在同期同业文章池中按 Jensen-Shannon 距离升序检索出"最近邻"集合 N{N}NN(i), 本列取 N=40 (top-k N 扩展梯子的一个分量, 2026-07-02 上线), 再对该 40 篇最近邻取距离均值作为 strat_diff_n40_lda 的取值。这里的距离度量精确对应源码调用 scipy.spatial.distance.jensenshannon(θ_i, θ_j, base=2): 该函数返回的不是 Jensen-Shannon 散度 JSD(P,Q) 本身, 而是其平方根 sqrt(JSD(P,Q)), 即 Jensen-Shannon *距离* (Jensen-Shannon divergence 是 KL 散度的对称化、有界化版本, 满足 JSD(P,Q)=JSD(Q,P)∈[0, ln2]; 对该量取平方根得到的 Jensen-Shannon distance 才满足三角不等式, 是一个真正的度量)。以 base=2 计算时, JSD(P,Q) 的自然上界是 1 (log2 底), 故其平方根 sqrt(JSD(P,Q)) 天然落在 [0,1] 区间——这是 base=2 参数直接导致的值域收窄, 而非对 JSD 散度做了额外的"归一化"变换; 本文档统一使用"JSD 距离/Jensen-Shannon distance"指称该量, 与源码注释"# sqrt(JSD) ∈ [0,1]"保持精确一致, 避免与"JSD 散度∈[0, ln2] 后归一化"这一在数学上不成立的表述混淆。数值越大表示该文章的主题分布与同业最近的 40 篇越不像, 即"差异化程度"越高。分词口径上, 自 2026-06-21 起全部 LDA 列改用注入 1506 个金科词的独立分词器 (_get_diff_tokenizer), "金融科技""区块链"等领域复合词整词保留不被切碎, 与字符轨 (char_wb) 及嵌入轨的领域感知口径对齐, 三者可比。
top-k N 是本家族的核心梯子: 除历史基线 N∈{3,4,5,6,7} 外, 2026-07-02 起为 TF-IDF (char/word)、LDA、两条 co-primary 嵌入 (Qwen3-8B 主轨 与 text-embedding-3-large 的 _lg 对等轨) 五种方法各加装 N∈{10,20,30,40,50} 的大邻域孪生列, 与既有 N=5 (或 N∈{3..7}) 互为稳健性、不分主次 — 邻域越大, 度量越接近"与整个行业均值的差异", 邻域越小越接近"与最相似同侪的差异", 二者刻画的是同一构念在不同局部/全局尺度下的表现, 不存在谁更优的排序, 论文层面禁止把不同 N 的列混进同一 over-identified 设定 (如同一 Hansen J 检验) 联合使用, 只能各自 just-identified 并排报告或作稳健性附表。strat_diff_n40_lda 即该梯子里 N=40 的 LDA 分量, 是偏"大邻域/接近行业均值"一端的差异度量。
本列同时挂在家族的三轨扩展下 (full/ctx/ss), 无后缀的 strat_diff_n40_lda 是 full 轨 (标题+全文正文), 另两个同名列分别是 ctx 与 ss 轨的孪生 (见下方 VAR 节)。三轨遵循项目"留篇门控=full-only" (2026-06-29) 与三轨行宇宙口径: 留篇/是否计入的判定只看 full 轨的 LLM 验证结果, ctx/ss 是 conditional-on-full 的测度/稳健性轨, 各自在自身文本口径上独立计算 LDA 主题分布与最近邻检索, 三轨同样各自 just-identified 并排, 互为稳健性, 禁止混入同一 over-identified Hansen J。
【文献定位】
LDA 主题模型本身出自 Blei, Ng & Jordan (2003) 的经典无监督文本建模框架; N-最近邻文本距离度量企业/文章"独特性"的做法直接对应 Guzman & Li (2023, Management Science) 对创业公司自我描述文本的处理, 以及 Hoberg & Phillips (2016, Journal of Political Economy) 对 10-K 产品描述文本构造行业分类与差异度的经典设计, 本产出的 top-k N 梯子正是这一文献传统里"检索半径敏感性"问题的直接回应。战略差异化/最优显著性 (optimal distinctiveness) 的组织理论根基参见 Haans (2019, Strategic Management Journal) 关于异质与同质品类下差异化收益的分析, 以及 Su, Gao & Tan (2024, Strategic Management Journal) 关于企业在动态复杂环境下如何权衡竞争压力与制度压力定位差异化程度的研究, 二者共同支撑"差异化程度对绩效的影响并非单调"这一构念背景, 提醒使用者 strat_diff_n40_lda 是一个方向中性的距离测度, 本身不隐含"越大越好"的价值判断。方法论上, JSD 度量分布距离与文本数据计量经济学处理的一般性讨论见 Gentzkow, Kelly & Taddy (2019, Journal of Economic Literature) 对"文本作为数据"的方法综述, 该文特别强调不同文本表征 (词袋/主题模型/嵌入) 各有偏误结构, 支持本家族"多方法并列互证"而非单一方法定论的设计取向。 在当代实证前沿上, Kang 与 Kang (2025) 以自然实验识别外部资本市场审视压力对企业战略独特性的因果影响, 证明「企业相对同业的战略偏离度」是一个可被外生冲击移动、具有实质经济内容的构念, 为本族差异度得分提供构念存在性的近期佐证; 惟该文的独特性建立在财务比率向量相对行业均值的标准化距离之上, 单位为美国公司-年, 既非文本相似度, 更无 LDA 主题分布或 Jensen-Shannon 距离, 故本条只锚构念、不锚算子。参照集的界定则由 Shen、Zhang、Zhong 与 Lu (2025) 从反面提示: 该文在中国某天使投资平台的 3266 份商业计划书上, 把同一创业企业分别相对在位企业与同台同类创业企业计算独特性, 发现两个参照物下独特性对投资人评价的作用方向不同且互相调节, 说明「独特性相对于谁而言」会实质改变该得分的经济含义, 因而本族以 40 个最近邻界定参照集的做法须被显式披露并接受检验。其迁移边界须诚实标明: 该文参照集由平台类别与投资人视角离散给定, 非本族在主题单纯形上按 JSD 距离检索的连续空间 kNN; 层级为创业企业而非银行-年度; 原文未使用主题分布或 JSD 距离, 亦未变动参照集的规模宽窄, 故不构成本族 top-k N 邻域梯子的直接依据 — 该梯子各档仍按互为稳健性、不分主次、各自 just-identified 的并排口径解读, 严禁混入同一 over-identified Hansen J 检验。
## VAR: strat_diff_n40_lda

【变体差分】
本列是 full 轨 (标题+正文全文) 上的 LDA 主题分布 top-k N=40 最近邻 JSD 差异度, 家族内三轨中的 canonical/无后缀成员, 也是 top-k N 梯子里 N=40 这一"较大邻域"分量。计算文本为 content_full (prepend_title 后的标题+正文), LDA 主题分布 θ_i 与最近邻检索池均限定在同期同业 full 轨文章集合内; 是否计入该文章参与最近邻池, 遵循 full-only 留篇门控 (仅 llm_verified_full == True 的文章计入), 与 ctx/ss 两轨的行宇宙 (conditional-on-full 子集) 保持一致对齐, 便于逐轨比较同一批文章在不同文本口径下的差异度是否稳健。N=40 相对家族内的默认 N=5 邻域大得多, 度量更接近"该文章相对整个同业主题分布均值"的偏离, 而非"相对最相似同侪"的偏离; 与同梯子的 n10/n20/n30/n50 五个大邻域分量及历史 N∈{3..7} 小邻域分量之间不设优先级, 均为互为稳健性的并排测度, 不得混入同一 over-identified 联合估计。使用时若要与其它同梯子分量 (如 strat_diff_n5_lda、strat_diff_n50_lda) 联合报告, 应作为独立的稳健性附表列, 而非同一回归设定里的多重内生工具变量, 否则会触犯家族口径铁律里对 over-identified Hansen J 检验的禁用条款。作为家族内 LDA 方法轨的一员, 本列与同名的 TF-IDF 字符/词轨、Embedding 双主轨列 (strat_diff_n40_emb 及其 _lg 孪生) 并列存在, 三种文本表征方法各自独立训练/检索, 互不复用中间结果, 仅在最终研究设计层面互证。

## VAR: strat_diff_n40_lda_ctx

【变体差分】
本列与 strat_diff_n40_lda 共享 LDA 主题模型与 N=40、JSD 距离的计算逻辑, 唯一差分维度是文本口径切到 ctx 轨: content_ctx (标题+实体窗口, 即银行/金科实体附近的截取文本, 而非全文), LDA 主题分布与最近邻检索池均在 ctx 轨文本集合内独立计算, 不与 full 轨共享词袋/主题矩阵或最近邻结果。行宇宙上, ctx 轨遵循 full-only 门控派生的 conditional-on-full 口径: 只统计 full 轨已判定为"银行金科报道"的文章子集, 在其之上用各自的 ctx 文本重算 LDA 与最近邻距离; 若某文章无有效的银行∧金科实体窗口 (即无法定位实体邻近文本), 该文章的 content_ctx 按项目回退语义退化为全文 body 且 ctx_is_fallback 置 True, 仍参与计算但需知悉其文本口径已退化为等同 full。ctx 轨与 full 轨、ss 轨互为稳健性并排关系, 不分主次, 也不与 full 轨/ss 轨混入同一 over-identified Hansen J; 与 full 轨的差异反映的是"聚焦实体邻近语境"与"通篇语境"两种文本截取策略下差异化测度是否一致, 而非孰优孰劣。由于 ctx 文本本身比 full 文本更短、更集中于实体周边表述, 训练同一份 LDA 主题模型时主题分布 θ_i 的方差结构与 full 轨可能不同, 使用者比较 strat_diff_n40_lda 与 strat_diff_n40_lda_ctx 的绝对水平差异时应留意这一文本长度效应, 更稳妥的做法是比较两轨内部的排序/相对位置而非跨轨直接比数值大小。N=40 大邻域设定在 ctx 轨上同样成立, 与该轨的 n10/n20/n30/n50/n5 分量并列, 不设主次。

## VAR: strat_diff_n40_lda_ss

【变体差分】
本列与前两列共享 LDA 建模与 N=40/JSD 差异度计算逻辑, 差分维度是文本口径切到 ss 轨: content_ss (标题+银行∧金科同句共现窗口, 判据为项目 config/filtering.yaml::context_window.ss_sentence_radius 默认±1句), 是三轨中口径最窄、要求最严的一支——只取银行实体与金科词同一句 (或半径窗口内) 共现的文本片段参与 LDA 建模与最近邻检索。ss 轨回退语义镜像 ctx 轨: 若文章不存在银行∧金科同句共现, content_ss 退化为全文 body 且 ss_is_fallback 置 True, 与 ctx_is_fallback 共享同一 n_articles 分母口径, 计算逻辑上不因回退而单独剔除该文章。行宇宙同样是 full-only 门控派生的 conditional-on-full 子集, 与 strat_diff_n40_lda / strat_diff_n40_lda_ctx 三者并排、互为稳健性, 禁止混入同一 over-identified Hansen J。三轨横向比较可以揭示: 当把主题分布计算严格限定在银行与金科词紧邻共现的窄窗口时 (ss), 差异化测度是否仍与全文 (full)、实体宽窗 (ctx) 两轨给出一致的排序结论, 是本家族稳健性叙事的重要组成部分, 而非替代关系。由于 ss 轨的可用文本片段通常比 ctx 轨更短 (严格同句共现, 而非实体窗口), 回退比例 (ss_is_fallback=True 的占比) 通常不低于 ctx 轨, 使用者在解读 strat_diff_n40_lda_ss 时应结合回退占比判断该轨在具体样本上的信息量是否充分; N=40 的大邻域设定在这一较窄文本口径下同样与 n10/n20/n30/n50/n5 等分量并排, 互为稳健性, 不设主次, 也不因样本量或回退比例差异而改变家族内"禁止混入同一 over-identified Hansen J"的铁律。

<!-- rendered-citations:begin -->
Guzman, J., & Li, A. (2023). Measuring Founding Strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Su, J., Gao, X., & Tan, J. (2024). Positioning for Optimal Distinctiveness: How Firms Manage Competitive and Institutional Pressures under Dynamic and Complex Environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Haans, R. F. J. (2019). What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as Data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Kang, J., & Kang, Y. (2025). Capital Market Scrutiny and Strategic Distinctiveness of the Firm: Evidence from a Natural Experiment. British Journal of Management, 36(1), 461-476. https://doi.org/10.1111/1467-8551.12857
Shen, R., Zhang, H., Zhong, W., & Lu, J. (2025). Distinctiveness from whom? Evaluation of startups' distinctiveness from multiple referents in angel investment platforms. Strategic Entrepreneurship Journal, 19(1), 171-195. https://doi.org/10.1002/sej.1521
<!-- rendered-citations:end -->
