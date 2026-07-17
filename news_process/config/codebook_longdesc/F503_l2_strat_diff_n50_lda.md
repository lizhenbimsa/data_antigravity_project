---
family_id: F503
columns:
- strat_diff_n50_lda
- strat_diff_n50_lda_ctx
- strat_diff_n50_lda_ss
unit: 无量纲差异度得分, 值域 [0,1] (LDA 主题分布上 Jensen-Shannon 距离 √JSD 的均值, 非负有界; 注意并非 JSD 散度本身的均值)
formula: 对银行 i 在年份 t 的文本主题分布 θ_i, 在同年份全部同行样本中按 Jensen-Shannon 距离(scipy.spatial.distance.jensenshannon, base=2, 记 d=√JSD) 检索最近的 N=50 个邻居, 取该 N=50 邻居集合上 d 的均值作为 strat_diff_n50_lda (N-最近邻差异度 Ŝ_i); JSD(P‖Q) = 0.5·KL(P‖M) + 0.5·KL(Q‖M), M=0.5(P+Q), 底数取 2 时 JSD∈[0,1]、d=√JSD∈[0,1]; 源码 pipeline/features/strategic_diff.py 中 _build_lda_jsd_matrix 调用 scipy 的 jensenshannon 函数返回的是 JSD 的平方根(即 Jensen-Shannon 距离), 而非 JSD 散度本身, 由 Jensen 不等式 mean(√x) ≠ √mean(x), 落盘的 strat_diff_n50_lda 是"√JSD 距离的均值", 与"JSD 散度的均值"数值上不等同(值域巧合同为 [0,1], 但含义不同)。ctx/ss 后缀分别在实体窗口文本轨、银行∧金科同句共现文本轨上重复同一构造, 主题分布 θ 由同一 LDA 模型在对应轨文本上重新推断得到。
producer: pipeline\features\strategic_diff.py ; pipeline\panel\stata_export.py
upstream:
- 14_materialize_ctx (content_ctx/content_ss 物化)
- 25_article_sbert (co-primary 嵌入族, 与本 LDA 轨并排非上游依赖)
citations:
- doi: "10.1086/688176"
  type: journal
  authors: "Hoberg, G., & Phillips, G."
  year: 2016
  title: "Text-Based Network Industries and Endogenous Product Differentiation"
  venue: "Journal of Political Economy"
  vol: "124"
  issue: "5"
  pages_or_artno: "1423-1465"
- doi: "10.1287/mnsc.2022.4369"
  type: journal
  authors: "Guzman, J., & Li, A."
  year: 2023
  title: "Measuring Founding Strategy"
  venue: "Management Science"
  vol: "69"
  issue: "1"
  pages_or_artno: "101-118"
- doi: "10.1002/smj.2978"
  type: journal
  authors: "Haans, R. F. J."
  year: 2019
  title: "What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories"
  venue: "Strategic Management Journal"
  vol: "40"
  issue: "1"
  pages_or_artno: "3-27"
- doi: "10.1109/18.61115"
  type: journal
  authors: "Lin, J."
  year: 1991
  title: "Divergence Measures Based on the Shannon Entropy"
  venue: "IEEE Transactions on Information Theory"
  vol: "37"
  issue: "1"
  pages_or_artno: "145-151"
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
strat_diff_n50_lda 测度的是"战略距离/战略独特性"(strategic distinctiveness/differentiation) 这一构念在文本空间上的经验代理: 一家银行当年新闻报道所暴露的业务话语(主题分布), 与同年样本中最相似的 N=50 家同行相比, 平均而言有多"不像"。构念根植于产业组织与战略管理文献对"最优独特性"(optimal distinctiveness) 的长期关切——企业既要通过战略差异化获取租金与竞争优势, 又不能偏离行业认知类别太远而丧失合法性(Haans (2019))。本族把这一构念从传统的产品/专利文本移植到银行金融科技新闻报道语料: 文本主题分布替代产品描述或专利分类号, 作为战略定位在语义空间中的坐标。方法学源头有二: 其一是文本网络产业(TNIC)与相似度矩阵方法, 即用文档向量的成对相似度直接刻画企业间的竞争/战略距离, 而非依赖人工产业分类(Hoberg & Phillips (2016)); 其二是"测量创业战略"的最近邻构造思路——对每家企业检索其在语义空间中最近的 N 个邻居, 再用邻居集合上的（不）相似度统计量作为该企业相对独特性的点估计(Guzman & Li (2023))。strat_diff_n50_lda 正是把 Guzman & Li 的最近邻框架, 套用在本项目 stage 25/strategic_diff 模块基于 LDA 主题分布的 JSD 距离上, 并把邻域规模从生产口径默认的 N=5 扩展到 N=50, 形成 top-k N 梯子上的一个大邻域取值点。

【方法学与计算】
计算管线分三步。第一步, 由 pipeline/features/strategic_diff.py 用注入 1506 个金科词的独立分词器(_get_diff_tokenizer)对文本分词(2026-06-21 起 word 级 TF-IDF 与全部 LDA 列统一走该分词器, 领域复合词如"金融科技""区块链"整词保留, 不被切碎, 这一口径与 char 轨、embedding 轨的领域感知处理一致); 第二步, 用一个在样本语料上训练的 LDA 模型把每篇/每行文本映射为一个低维主题概率分布 θ(单纯形上的点, 各分量非负且和为 1); 第三步, 对同一年份内的全部银行样本两两计算 d(θ_i, θ_j)=scipy.spatial.distance.jensenshannon(θ_i, θ_j, base=2)——该 scipy 函数返回的是 JSD 散度的平方根 √JSD, 即 Jensen-Shannon 距离, 而非 JSD 散度本身(源码 _build_lda_jsd_matrix 注释亦明确标注"sqrt(JSD)"), 对银行 i 按 d 升序排列同行, 取前 N=50 个最近邻, 以这 N=50 个 d 值的均值作为 strat_diff_n50_lda。JSD 本身是 KL 散度的对称化、有界化版本(Lin (1991)), √JSD 距离继承了 JSD 的对称、恒有限、以 log2 为底时值域落在 [0,1] 的性质, 且满足三角不等式、是真正的度量(metric), 这正是它比原始 JSD 散度或 KL 散度更适合直接用于最近邻检索排序的原因; 数值越大表示该银行的话语主题分布与其"最相似的一批同行"相比仍然差异越大, 即战略/话语独特性越高, 反之数值越小说明该银行的新闻话语内容与同行高度雷同、缺乏差异化叙事。需特别说明: strat_diff_n50_lda 是"N=50 邻居上 √JSD 距离的均值", 而非"N=50 邻居上 JSD 散度的均值"——由 Jensen 不等式, 对非线性凹函数 √ 取均值再开方与先开方再取均值一般不相等, 两者数值不可互换, 尽管值域都落在 [0,1] 但不构成同一量; 本文档及其余各列一律以此"√JSD 距离均值"口径为准。这一构造与家族内 TF-IDF 轨(char/word)的 N-最近邻差异度共享同一"取最近 N 邻居, 平均距离"框架, 唯一区别是底层文本表征——LDA 主题分布 vs. 词袋向量——不同表征方法互为方法学稳健性检验, 而非彼此替代或分主次。三轨 (full/ctx/ss) 上的取值分别建立在 14_materialize_ctx 物化出的 content_full/content_ctx/content_ss 三份文本上, 各自独立跑一遍分词→LDA 推断→JSD 最近邻这条流水线; full 轨用完整正文(标题+全文 body), ctx 轨用围绕目标银行实体的窗口文本, ss 轨用银行∧金科词同句共现窗口文本(回退语义镜像 ctx: 当某银行-年份样本内无满足"银行∧金科同句共现"的句子时, content_ss 退化为全文 body, 并置 ss_is_fallback=True, 与 ctx 轨共享同一套 n_articles 分母口径)。三轨、以及词典消融/权重/阈值/判据等其它梯子, 在本项目的识别策略里均按"各自 just-identified 并排、互为稳健性、不分主次"处理, 绝不允许把 full/ctx/ss 三条差异度序列同时塞进同一个 over-identified 的 Hansen J 过度识别检验——每条轨道各自作为独立的一次估计并排展示, 用跨轨一致性而非合并识别力度来支撑结论的稳健性。

【文献定位】
本族方法学谱系上承三条脉络: 一是产业组织学界用文本相似度直接构造企业间距离矩阵、绕开人工产业分类的传统, 代表作是 Hoberg & Phillips (2016) 提出的文本网络产业分类(TNIC), 把逐年更新的产品描述文本相似度矩阵作为竞争定位的经验度量; 二是把"最近邻"思想应用到战略/创业异质性测量的近期文献, Guzman & Li (2023) 用创业公司命名文本的最近邻结构度量创始战略的模式化程度与独特性, 是本族 N-最近邻均值构造的直接方法学来源; 三是最优独特性理论传统, Haans (2019) 指出战略独特性对绩效的边际效应依赖于行业内同质/异质竞争格局, 提醒差异度得分本身是中性测度, 其经济含义需结合具体检验假设解读, 不能简单等同"差异度越高越好"或"越低越好"。三者共同构成 strat_diff_n50_lda 及其家族的构念效度基础: 用可复现的文本统计量捕捉战略话语上的相对定位, 同时提醒使用者战略差异化的绩效含义是情境依赖的经验问题而非度量本身自带的方向性判断。 在此三条脉络之上, Shen、Zhang、Zhong 与 Lu (2025) 进一步提示参照集本身的界定并非中性的技术选择: 该文在中国某天使投资平台的 3266 份商业计划书上, 把同一创业企业分别相对在位企业与同台同类创业企业计算独特性, 发现两个参照物下独特性对投资人评价的作用方向不同且互相调节, 从而证明「独特性相对于谁而言」会实质改变该得分的经济含义; 据此, 本族取 N=50 最近邻作为参照集的做法属须被显式披露并接受检验的设计选择, 而非可默认的实现细节。迁移边界须诚实标明: 该文的参照集由平台类别与投资人视角离散界定, 非本族在主题单纯形上按 √JSD 距离检索的连续文本向量空间 kNN; 分析层级为创业企业而非银行-年度; 原文既未提出 kNN 算子, 也未使用 LDA 主题分布或 Jensen-Shannon 距离, 更未变动参照集的规模宽窄, 故不构成本族 top-k N 邻域宽度梯子的直接依据 — 各 N 档仍按互为稳健性、不分主次、各自 just-identified 的并排口径解读, 严禁混入同一 over-identified Hansen J 检验。
## VAR: strat_diff_n50_lda

【变体差分】
本列是家族在 full 轨(标题+完整正文)上的 canonical 取值: content_full 文本先经金科词感知分词, 再由 LDA 主题模型推断得到主题分布 θ, 随后在同年份全部银行样本中按 √JSD 距离(Jensen-Shannon 距离, 而非 JSD 散度本身)升序检索最近的 N=50 个邻居并取该距离值的均值。full 轨是三轨中信息量最完整的一条, 覆盖整篇报道的全部语义信号(不局限于银行实体附近的窗口, 也不要求金科词与银行词同句共现), 因此它捕捉的"战略话语差异度"反映的是银行整体新闻叙事内容层面的相对独特性, 而非仅围绕金融科技话题窗口的局部差异。N=50 是 top-k N 扩展(fix topk-n-expansion, 2026-07-02)引入的大邻域取值, 与生产默认的 N=5(strat_diff_n5_lda)及梯子上的其它取值(N∈{10,20,30,40})互为稳健性并排、不分主次: N 越大, 邻域覆盖的同行范围越广, 均值统计量对局部噪声(个别年份偶然出现的极端相似或极端不相似的少数同行)越不敏感, 但也可能把原本在细分战略群组内确有意义的差异平滑掉; N 越小则相反, 对局部结构更敏感但方差更大。研究者在报告结果时应把 N=50 与 N=5 等其它 N 值上的结果并排陈列作为对同一构念在不同邻域粒度下的稳健性验证, 而非挑选某个 N 作为"正确"设定、弃用其它。本列与家族内同轨的 TF-IDF char/word 版本(strat_diff_n50/strat_diff_n50_w)、以及后续会出现的 embedding 轨版本共享完全相同的"取 N=50 最近邻均值"外层框架, 唯一差异是底层文本表征从主题分布换成了词频/嵌入向量, 三种表征方法各自 just-identified、彼此互证, 不构成同一识别模型下的多重工具。数值上, LDA+JSD 轨与词袋 TF-IDF 轨、稠密 embedding 轨衡量的都是同一构念在不同表征假设下的经验实现, 由于 LDA 主题维度远低于 TF-IDF 词袋维度且经过概率归一化, 该轨对文本长度、罕见词冲击相对更稳健, 但也依赖 LDA 主题数目、迭代收敛质量等超参数选择, 使用者在解读跨年份或跨轨比较时应留意这一模型依赖性, 并优先关注同一设定下的横截面排序而非跨设定的绝对数值可比性。

## VAR: strat_diff_n50_lda_ctx

【变体差分】
本列与家族 canonical(strat_diff_n50_lda) 的唯一系统性差别在于底层文本轨: 本列的主题分布 θ 由 content_ctx(实体窗口文本, 标题+目标银行实体周围窗口内容, 在 14_materialize_ctx 物化)推断得到, 而非 content_full 的完整正文。ctx 轨的设计初衷是把主题推断的输入信号收窄到与目标银行实体直接相关的语境, 剔除文章中与该银行无关的段落(例如同一篇报道同时涉及多家机构或多个话题时的"噪声"内容), 从而让 LDA 主题分布更聚焦于该银行自身的战略/业务叙事, 理论上应能降低无关话题混入造成的主题分布"稀释"。除文本来源不同外, N=50 最近邻检索、√JSD(Jensen-Shannon 距离, 非 JSD 散度本身)计算、金科词感知分词器、以及同年份内的检索范围均与 full 轨完全一致, 因此本列与 canonical 列之间的差异纯粹来自实体窗口截取这一步骤, 不引入任何额外的模型或参数梯子。按本项目铁律, full 与 ctx 两轨互为稳健性、并排看待、不分主次: 若某项检验结论在 full 与 ctx 两轨上方向一致、显著性相近, 则可认为该结论不依赖于是否把无关话题内容纳入主题推断; 若两轨结果出现系统性分歧, 则提示战略差异度的测量对文本窗口选择敏感, 需要在解读时进一步诊断是窗口截取本身的信息损失, 还是无关话题混入 full 轨造成的测量误差。留篇门控口径为 full-only(2026-06-29 起): 一篇报道是否计入"银行-金科"报道集合只看 llm_verified_full 是否为真, ctx 轨的行宇宙是 full 轨留篇集合的条件子集, 该子集内逐轨各自独立计算 N-最近邻差异度, 不存在 ctx 轨单独扩大或收窄留篇范围的情况。禁止将本列与 canonical 列同时作为同一个 over-identified Hansen J 检验中的多重工具变量或多重矩条件, 二者应各自作为独立的估计口径并排报告。

## VAR: strat_diff_n50_lda_ss

【变体差分】
本列同样只在文本轨上区别于 canonical 列: 主题分布 θ 由 content_ss(银行∧金科词同句共现窗口文本)推断得到。ss 轨的构造判据比 ctx 轨更严格——不满足于实体窗口范围内出现相关内容, 而要求目标银行词与金科词在同一句内共同出现, 是三轨中语境约束最紧的一条, 理论上应最能刻画"该银行在金融科技情境下的具体战略话语"这一狭义构念, 代价是可用信息量最小、对稀疏样本(某银行-年份内同句共现句子很少)更敏感。ss 轨的回退语义严格镜像 ctx 轨: 当某银行-年份样本内不存在满足银行∧金科同句共现条件的句子时, content_ss 退化为使用完整正文 body, 并将 ss_is_fallback 标记置为 True; 这一回退与 ctx 轨共享同一套 n_articles 分母口径, 保证降级发生时不会静默地缩小样本或制造虚假的零值。若 FINTECH_AC 词典未加载(None), 则 *_is_fallback 全部置 True, 三轨同时优雅降级为等价于 full 轨的取值, 而不是抛出异常或产生空值。除文本来源与回退规则外, 本列的 N=50 最近邻检索、√JSD(Jensen-Shannon 距离, 非 JSD 散度本身)、分词器与检索年份范围均与家族其它两列完全一致, 不叠加任何额外的判据后缀或阈值梯子(判据后缀如 _win1/_sent 是网络结构指标族的概念, 不适用于本战略差异度族)。三轨(full/ctx/ss)在本族内互为稳健性、各自 just-identified 并排陈列, 严禁混入同一个 over-identified Hansen J 检验;当三轨结果一致时, 增强了"银行层面战略话语差异度"这一构念不依赖具体文本窗口选择的信心, 当三轨出现分歧时, 应结合 ss_is_fallback 占比等辅助诊断列判断分歧是否主要来自回退样本的稀释效应, 而非机械地取三者均值或简单加总来"合并"识别力度。

<!-- rendered-citations:begin -->
Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Guzman, J., & Li, A. (2023). Measuring Founding Strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Haans, R. F. J. (2019). What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Lin, J. (1991). Divergence Measures Based on the Shannon Entropy. IEEE Transactions on Information Theory, 37(1), 145-151. https://doi.org/10.1109/18.61115
Shen, R., Zhang, H., Zhong, W., & Lu, J. (2025). Distinctiveness from whom? Evaluation of startups' distinctiveness from multiple referents in angel investment platforms. Strategic Entrepreneurship Journal, 19(1), 171-195. https://doi.org/10.1002/sej.1521
<!-- rendered-citations:end -->
</content>
</invoke>
