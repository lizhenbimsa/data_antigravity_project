---
family_id: F499
columns:
- strat_diff_n30_lda
- strat_diff_n30_lda_ctx
- strat_diff_n30_lda_ss
unit: 无量纲距离得分 (Jensen-Shannon 距离均值, base=2 对数, 理论值域 [0,1])
formula: 'strat_diff_n{N}_lda = mean_{j∈KNN_N(i)} sqrt(JSD(θ_i, θ_j)), 其中 θ_i 为文章/银行 i 在 LDA 主题模型下的主题概率分布, KNN_N(i) 为在 JSD 距离矩阵上升序排序取得的 N 个最近同业邻居 (N=30, is_distance=True 路径, 排序度量与最终报告距离为同一矩阵), sqrt(JSD) 为 Jensen-Shannon 距离 (scipy.spatial.distance.jensenshannon, base=2, 即 Jensen-Shannon 散度 (Lin 1991) 的平方根, base=2 对数使上界归一为 1)'
producer: pipeline\features\strategic_diff.py ; pipeline\panel\stata_export.py
upstream: []
citations:
- {doi: "10.1287/mnsc.2022.4369", type: journal, authors: "Guzman, J., & Li, A.", year: 2023, title: "Measuring founding strategy", venue: "Management Science", vol: "69", issue: "1", pages_or_artno: "101-118"}
- {doi: "10.1086/688176", type: journal, authors: "Hoberg, G., & Phillips, G.", year: 2016, title: "Text-based network industries and endogenous product differentiation", venue: "Journal of Political Economy", vol: "124", issue: "5", pages_or_artno: "1423-1465"}
- {doi: "10.1111/jofi.12050", type: journal, authors: "Hoberg, G., Phillips, G., & Prabhala, N.", year: 2014, title: "Product market threats, payouts, and financial flexibility", venue: "The Journal of Finance", vol: "69", issue: "1", pages_or_artno: "293-324"}
- {doi: "10.1002/smj.2978", type: journal, authors: "Haans, R. F. J.", year: 2019, title: "What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories", venue: "Strategic Management Journal", vol: "40", issue: "1", pages_or_artno: "3-27"}
- {doi: "10.1002/smj.3549", type: journal, authors: "Su, J., Gao, X., & Tan, J.", year: 2024, title: "Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment", venue: "Strategic Management Journal", vol: "45", issue: "2", pages_or_artno: "333-361"}
- {doi: "10.1257/jel.20181020", type: journal, authors: "Gentzkow, M., Kelly, B., & Taddy, M.", year: 2019, title: "Text as data", venue: "Journal of Economic Literature", vol: "57", issue: "3", pages_or_artno: "535-574"}
- doi: "10.1287/mnsc.2023.4915"
  title: "Disclosure Similarity and Future Stock Return Comovement"
  authors: "Dyer, T. A., Roulstone, D. T., & Van Buskirk, A."
  year: 2024
  venue: "Management Science"
  type: "journal"
- doi: "10.1016/j.ememar.2025.101309"
  title: "The textual similarity of news content and stock return synchronicity"
  authors: "Huang, R., Chen, X., & Wu, C."
  year: 2025
  venue: "Emerging Markets Review"
  type: "journal"
new_dois:
  - "10.1287/mnsc.2023.4915"
  - "10.1016/j.ememar.2025.101309"
---

## CORE

【构念与来源】
本家族测度企业(样本中的目标银行)在新闻文本所刻画的"战略/业务论述空间"中相对于同业的差异化程度, 方法学上继承 Hoberg & Phillips (2016, Journal of Political Economy) 开创的文本网络产业(TNIC)传统与 Guzman & Li (2023, Management Science) 的"测量创业战略"框架, 将原本基于监管文件(10-K)的文本相似度思想迁移到中文银行/金科新闻语料。producer 为 `pipeline/features/strategic_diff.py`, 面板标签写入见 `pipeline/panel/stata_export.py`。canonical 家族基名 `strat_diff_n{N}` 系列采用 N-最近邻(KNN)范式: 对每篇文章(或每家银行在给定年份的文本聚合)先在某一文本表征空间中定位其向量, 再在同期同业样本中检索 N 个余弦相似度最高的"邻居", 以该文章与其 N 个近邻之间的平均散度/距离刻画其战略论述与同业的偏离程度——距离越大, 说明该银行在新闻叙事中呈现的业务定位/战略语言与同业越不相同, 对应 Haans (2019, Strategic Management Journal) 和 Su, Gao & Tan (2024, Strategic Management Journal) 讨论的"最优区分度"(optimal distinctiveness)构念族在文本维度的经验代理。

本家族 F499 特指该 KNN 差异度指标家族中的 LDA+JSD 方法学分支, 且 N 固定为 30 (即 top-k N 梯子中的一档)。LDA(Latent Dirichlet Allocation, Blei, Ng & Jordan 2003)先将全体文章拟合为一组潜在主题的概率分布, 每篇文章表示为一个主题概率向量 θ_i(和为1的分布, 而非稠密语义嵌入); 随后用 Jensen-Shannon 距离(scipy.spatial.distance.jensenshannon, base=2)度量任意两篇文章主题分布之间的差异, 该量是 Jensen-Shannon 散度(JSD, Lin 1991, IEEE Transactions on Information Theory; Kullback-Leibler 散度的对称化、有界版本)开平方后的度量形式, 底数取 2 使上界归一为 1, 理论值域为 [0,1](若源码遗漏显式 base=2 参数, scipy 默认改用自然对数底, 上界将变为 √ln2≈0.833, 与"值域 [0,1]"的声称不再吻合——本列源码已显式传入 base=2, 不受此隐患影响), 天然适合刻画"分布"而非"点"之间的距离, 与本家族其余 TF-IDF/Embedding 轨(值域同样归一至 [0,1] 区间或经量纲统一处理)在方法论上并列、互为稳健性、不分主次, 不应被解读为互相验证的层级关系。

【方法学与计算】
strat_diff_n30_lda 的计算流程为: ①对该期(年度)全体样本文章的正文/上下文文本拟合(或复用已训练的)LDA 主题模型, 得到每篇文章的主题概率分布 θ, 并据此构建两两文章间的 Jensen-Shannon 距离矩阵(`_build_lda_jsd_matrix`, 对角线置 NaN); ②在该距离矩阵上按 `is_distance=True` 路径对每篇文章的一整行做升序排序, 取距离最小的 N=30 个同期同业邻居——LDA+JSD 轨的近邻检索与最终报告距离共用同一个 JSD 距离矩阵, 不存在独立于 JSD 之外的余弦相似度排序步骤(不同于本家族部分其余方法轨可能采用"相似度矩阵"路径 `is_distance=False`, LDA 轨与 embedding 轨均走距离矩阵直接排序的实现分支); ③对该 30 个近邻的 JSD 距离取均值(并裁剪至 [0,1] 区间)作为该篇文章的 strat_diff_n30_lda; ④文章级指标经 `stata_export.py` 聚合到银行-年面板。金科词注入分词口径(fix inject-fintech-word-lda, 2026-06-21)对本列生效: LDA 训练所用分词器为注入了 1506 个金科词表的独立分词器(`_get_diff_tokenizer`), "金融科技""区块链"等领域复合词被整词保留、不被字符级切分打散, 与本家族 char 轨/embedding 轨的领域感知口径保持一致, 该分词器切换只影响 LDA 与 word 级 TF-IDF 两条轨, 不影响 char 轨与 embedding 轨的字节输出。

top-k N 扩展(fix topk-n-expansion, 2026-07-02)将原本仅有 N=5 的 canonical LDA 差异度列(`strat_diff_n5_lda`)系统扩展为 N∈{10,20,30,40,50} 大邻域孪生集合, 覆盖全部方法(TF-IDF char/word · LDA · Embedding Qwen 主轨 · Embedding text-embedding-3-large 的 `_lg` 对等轨)与全部三个文本轨(full/ctx/ss)。strat_diff_n30_lda 正是该扩展中 N=30 一档在 LDA 方法、full 轨上的实现。不同 N 之间互为稳健性、各自 just-identified 并排、不分主次、禁止混入同一 over-identified Hansen J 或同一回归设定——较小 N(如 5)对局部近邻结构更敏感、噪声更大但更贴近"最相似同业"的语义; 较大 N(如 30、50)对局部噪声更稳健但可能引入跨子类别的稀释效应, 研究者应将不同 N 的估计结果并列报告作为规格曲线的一部分, 而非挑选单一 N 作为"最优"设定。

【文献定位】
本家族的方法学谱系直接对应 Hoberg & Phillips (2016, JPE)提出的文本网络产业分类思想——用文本相似度而非行政行业代码刻画企业间的竞争/战略邻近关系——以及 Guzman & Li (2023, Management Science)将该思路用于测量初创企业战略定位的最近邻方法。构念上呼应 Haans (2019, SMJ)与 Su, Gao & Tan (2024, SMJ)关于企业在同质/异质类别环境下"差异化"绩效效应与"最优区分度"定位策略的组织理论文献, 本指标可视为这类构念在中国银行业新闻文本语境下的经验代理。JSD 作为分布间距离度量的方法论出处为 Lin (1991); LDA 主题模型出处为 Blei, Ng & Jordan (2003)。整体文本-as-data 方法论定位参见 Gentzkow, Kelly & Taddy (2019, Journal of Economic Literature)对文本计量经济学方法的系统综述, 该文亦讨论了主题模型与词袋/嵌入类方法各自的适用边界与解释力权衡, 是本家族在方法选择与稳健性论证上的重要参照。此外, Dyer, Roulstone & Van Buskirk (2024, Management Science) 证明企业间文本披露相似度不仅预测、而且部分驱动了未来股票收益联动, 与本家族基于文本距离刻画企业间(异)同性的方法论直接呼应; Huang, Chen & Wu (2025, Emerging Markets Review) 以中国股票市场新闻文本为对象, 用新闻内容与同业的文本相似度测度信息环境与收益同步性, 方法论与语料场景均与本家族(中文银行/金科新闻文本战略差异度)高度贴近。

## VAR: strat_diff_n30_lda

【变体差分】
本列是 F499 家族在 full 轨(标题+正文全文)上的 canonical 列, 对应文本范围为该篇文章的完整正文文本(经 prepend_title 拼接标题), 不做实体窗口截取, 不做同句共现限定。方法轨固定为 LDA+JSD, 邻域规模固定为 N=30, 属 top-k N 扩展梯子中的一档, 与同方法同轨的 `strat_diff_n5_lda`(canonical 最近邻规模)、`strat_diff_n10_lda`、`strat_diff_n20_lda`、`strat_diff_n40_lda`、`strat_diff_n50_lda` 互为稳健性并排, 不分主次、各自 just-identified、禁止混入同一 over-identified Hansen J。由于本轨文本为全文, 该列在样本覆盖上不受留篇门控之外的额外行级限制——留篇门控本身(2026-06-29 起)以 full 轨的 `llm_verified_full` 判定是否为一篇有效的银行-金科报道, strat_diff 家族的行宇宙继承该门控结果, ctx/ss 轨则是该行宇宙下的条件测度/稳健性轨(conditional-on-full)。值域为 [0,1] 的非负实数(scipy jensenshannon 以 base=2 归一后的上界), 数值越大代表该银行该年度新闻论述在主题分布层面与同业 30 个最近邻的平均偏离程度越大, 即战略/业务定位的文本差异化程度越高。

在实证使用上, 本列适合作为战略差异化的主口径测度参与横截面或面板回归的解释变量或控制变量, 与同族的 TF-IDF char/word 轨、Embedding 主轨(Qwen3-8B)及其 `_lg` 对等轨(text-embedding-3-large)并列报告, 用以说明结论并非某一种文本表征方法的人工产物。由于 LDA 主题分布本身是对语料整体结构的概括性刻画, 相较逐词的 TF-IDF 表征或稠密语义嵌入, 更适合捕捉宏观层面的"话题构成"差异而非细粒度措辞差异, 研究者在解读本列时应注意这一方法学定位差异, 而非将其视为可与其他方法轨简单加总或替代的单一真值。

## VAR: strat_diff_n30_lda_ctx

【变体差分】
本列与 canonical 列的唯一区别是文本轨从 full 切换为 ctx(实体窗口轨): 参与 LDA 拟合与 KNN 检索的文本不是全文, 而是标题+目标银行实体周边窗口文本(`content_ctx`, 由 stage 14 `ctx_materializer` 物化, `prepend_title` 拼接标题)。ctx 轨的设计意图是聚焦于文章中直接围绕目标银行展开论述的局部语境, 剔除与该银行无关的大段正文噪声, 是相对于 full 轨"互为稳健性、不分主次"的并排测度, 而非其子集或替代——full/ctx/ss 三轨铁律要求任何回归设定禁止混用同一 over-identified Hansen J。回退语义: 若某篇文章无法定位到有效的实体窗口(`ctx_is_fallback=True`), 则 `content_ctx` 退化为全文 body, 此时该文章在 ctx 轨上参与 LDA/KNN 计算所用的文本实质与 full 轨相同, 但仍计入 ctx 轨的分母与统计, 不因回退而被剔除样本。留篇门控口径继承 full 轨判定结果(2026-06-29 起 full-only), ctx 轨的行宇宙是 full 轨留篇行的条件子集。N=30、LDA+JSD 方法、金科词注入分词口径与 canonical 列完全一致, 唯一差分维度是文本轨。

由于 ctx 轨聚焦实体窗口局部语境, 相较 full 轨更贴近"该银行在这篇报道中具体被如何论述"的即时语义, 理论上更不易被文章中与银行无关的大段背景/行业综述内容稀释; 但代价是可用文本量整体收缩(尤其在窗口半径较小、原文实体密度低时), 可能引入更大的抽样噪声, 尤其在样本期较短、篇均可用文本量有限时(如本项目本机 dev 数据 T=2 场景)更易出现方差偏大的退化表现。研究者在稳健性检验中应将本列与 full 轨、ss 轨并排报告估计系数与显著性, 而非单独依赖任一轨下结论。

## VAR: strat_diff_n30_lda_ss

【变体差分】
本列与 canonical 列的区别是文本轨切换为 ss(同句共现轨): 参与计算的文本为标题+目标银行与金科关键词严格同句(±N 窗口, 默认半径 1)共现的句子拼接(`content_ss`, 同样在 stage 14 物化、`prepend_title` 拼接标题), 判据比 ctx 轨更严格——要求银行与金科词在同一句子内共同出现, 而非仅在实体窗口范围内邻近。ss 轨与 ctx 轨镜像共享回退语义: 若某篇文章不存在银行∧金科同句共现, 则 `content_ss` 退化为全文 body, `ss_is_fallback=True`, 该文章仍计入 ss 轨的 `n_articles` 分母(与 ctx 轨共享同一回退记账口径), 而不被排除在统计之外。full/ctx/ss 三轨在本列上同样遵循"各自 just-identified 并排、互为稳健性、不分主次、禁止混入同一 over-identified Hansen J"的口径铁律, ss 轨不是 ctx 轨的加强版结论, 二者并列报告即可。方法轨(LDA+JSD)、邻域规模(N=30)、金科词注入分词器与家族其余变体保持一致, 本列区别于 canonical 与 ctx 变体的唯一维度是文本判据的严格程度(全文 vs 实体窗口 vs 严格同句)。

ss 轨代表本家族三轨中文本口径最严格的一档: 只有明确将银行与金科在同一句子内并置论述的段落才被纳入主题分布的估计与近邻检索, 这一口径最贴近"该银行与金融科技存在具体、直接叙事关联"的语义, 但同时也意味着更高的回退发生率(尤其在金科相关词汇分布稀疏的报道中), 需要研究者结合 `ss_is_fallback` 指示列审视样本构成, 避免把大量回退到全文的观测值误当作真实同句证据来解读差异化程度的经济含义。

<!-- rendered-citations:begin -->
Guzman, J., & Li, A. (2023). Measuring founding strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market threats, payouts, and financial flexibility. The Journal of Finance, 69(1), 293-324. https://doi.org/10.1111/jofi.12050
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Su, J., Gao, X., & Tan, J. (2024). Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Dyer, T. A., Roulstone, D. T., & Van Buskirk, A. (2024). Disclosure Similarity and Future Stock Return Comovement. Management Science. https://doi.org/10.1287/mnsc.2023.4915
Huang, R., Chen, X., & Wu, C. (2025). The textual similarity of news content and stock return synchronicity. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2025.101309
<!-- rendered-citations:end -->
</content>
