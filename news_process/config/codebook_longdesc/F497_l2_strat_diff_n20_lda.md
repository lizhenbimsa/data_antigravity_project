---
family_id: F497
columns:
- strat_diff_n20_lda
- strat_diff_n20_lda_ctx
- strat_diff_n20_lda_ss
unit: 无量纲得分 (Jensen-Shannon 散度距离, 理论值域 [0,1])
formula: 'strat_diff_n20_lda_i = mean_{j∈N20(i)} JSD(θ_i, θ_j), 其中 θ_i 是文章/银行-年文本经 LDA 主题模型估得的主题概率分布, N20(i) 是以 LDA 主题分布余弦相似度 (或等价距离) 排序取出的 20 个最近邻同业, JSD 为 Jensen-Shannon 散度 (Lin 1991 定义, 底数 2 对数下上界为 1)'
producer: pipeline\features\strategic_diff.py ; pipeline\panel\stata_export.py
upstream: []
citations:
- doi: "10.1287/mnsc.2022.4369"
  type: journal
  authors: "Guzman, J., & Li, A."
  year: 2023
  title: "Measuring founding strategy"
  venue: "Management Science"
  vol: "69"
  issue: "1"
  pages_or_artno: "101-118"
- doi: "10.1086/688176"
  type: journal
  authors: "Hoberg, G., & Phillips, G."
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: "Journal of Political Economy"
  vol: "124"
  issue: "5"
  pages_or_artno: "1423-1465"
- doi: "10.1002/smj.2978"
  type: journal
  authors: "Haans, R. F. J."
  year: 2019
  title: "What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories"
  venue: "Strategic Management Journal"
  vol: "40"
  issue: "1"
  pages_or_artno: "3-27"
- doi: "10.1002/smj.3549"
  type: journal
  authors: "Su, J., Gao, X., & Tan, J."
  year: 2024
  title: "Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment"
  venue: "Strategic Management Journal"
  vol: "45"
  issue: "2"
  pages_or_artno: "333-361"
- doi: "10.1111/jofi.12050"
  type: journal
  authors: "Hoberg, G., Phillips, G., & Prabhala, N."
  year: 2014
  title: "Product market threats, payouts, and financial flexibility"
  venue: "The Journal of Finance"
  vol: "69"
  issue: "1"
  pages_or_artno: "293-324"
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
本家族衡量单篇银行-金科报道 (及其汇总到银行-年层面的对应量) 在主题语义空间中与同期"最相似的 20 篇同业报道"之间的差异程度, 是 strat_diff 战略差异度大家族 (pipeline\features\strategic_diff.py) 内 LDA+JSD 方法分支的 N=20 大邻域取值。家族构念直接承继 Guzman & Li (2023, Management Science) 的"测度创业策略"思路——用文本相似度定义同业邻域、用邻域内平均距离刻画一家机构的策略独特性——并把 Hoberg & Phillips (2016, Journal of Political Economy) 基于文本的产业内生分类范式从"文档-余弦相似度"泛化到"主题分布-JSD 距离"这一条平行的方法学分支。canonical 口径 strat_diff_n5_lda 取 N=5 的近邻窗口作为主设定; 本家族三列是 2026-07-02 top-k N 扩展 (fix topk-n-expansion) 中新增的 N=20 大邻域孪生, 与 N=5 canonical 以及 N∈{10,30,40,50} 的其余邻域宽度、TF-IDF(char/word)/Embedding(Qwen/large) 等其余四种底层表征方法各自并排, 互为稳健性、不分主次, 禁止混进同一个 over-identified 的 Hansen J 检验 (三轨/co-primary 嵌入/梯子铁律, 见 CLAUDE.md「当前状态铁律」)。

【方法学与计算】
计算分两步。第一步用 LDA (Latent Dirichlet Allocation, Blei, Ng, & Jordan 2003 提出的经典生成式主题模型) 对语料 (按 full/ctx/ss 各自独立的分词、见下) 估计固定数量的隐主题, 得到每篇文本在主题空间上的概率分布 θ (各分量非负且和为 1, 是一个合法的离散概率分布)。第二步对每篇文章, 在同一时间窗口/可比同业集合内, 按主题分布距离找出最近的 20 篇同业报道 (N20 邻域), 逐对计算 Jensen-Shannon 散度 JSD(θ_i, θ_j) —— JSD 是 KL 散度的对称化、有界化版本 (Lin 1991), 定义为 JSD(P,Q) = ½KL(P‖M) + ½KL(Q‖M), M=(P+Q)/2, 底数取 2 时上界为 1、下界为 0 (完全相同分布) —— 再对 20 个 JSD 值取均值, 得到该文章 (进而汇总到银行-年) 的战略差异度分数。JSD 相比原始 KL 散度的优势是对称、恒有界、且允许两分布支撑集不完全重合时仍良定义, 适合作为跨文档比较的距离度量。

分词口径上, 家族沿用 2026-06-21 起对全部 word 级 TF-IDF 列 (*_w) 与全部 LDA 列 (*_lda) 生效的口径变更 (fix inject-fintech-word-lda): 分词器改用注入了 607 个金科词表的独立分词器 (`_get_diff_tokenizer`), 使"金融科技""区块链"等领域复合词作为整词保留, 不被通用分词器拆碎, 与 char 轨 (char_wb n-gram) 及 embedding 轨的领域感知程度对齐; 该口径变更不影响 char 轨与 embedding 轨的字节输出。值域上, TF-IDF/LDA 轨的底层向量都是非负分布, JSD 距离本身理论值域 [0,1] (2026-06-11 值域口径修复 fix(omni-g-strategic-02/03) 明确了这一点, 与嵌入余弦轨的 [-1,1]/[0,2] 值域是两套不同的度量空间, 不可跨方法直接比较数值大小, 只能比较标准化后的回归系数)。

三列对应家族的三条文本轨: 无后缀列使用 full 轨 (标题+全文正文物化文本, stage 14 `content_full`); `_ctx` 后缀使用 ctx 轨 (标题+银行/金科实体窗口物化文本 `content_ctx`); `_ss` 后缀使用 ss 轨 (标题+银行∧金科同句±N窗物化文本 `content_ss`, 默认半径 1 句, 键 `config/filtering.yaml::context_window.ss_sentence_radius`)。三轨在 stage 14 `ctx_materializer` 统一物化, 是并列的稳健性/测度轨而非主次关系: full 轨是留篇门控口径 (2026-06-29 起 stage 21 是否判定为"一篇银行金科报道"只看 `llm_verified_full`), ctx/ss 轨是 conditional-on-full 的稳健性测度, 行宇宙是 full 留篇集的子集, 但每条轨各自独立计算 LDA 主题分布与 JSD 距离, 不借用彼此的分母或中间量。ss 轨在没有银行∧金科词同句共现时回退语义镜像 ctx 轨: `content_ss` 退化为全文 body, 对应 `ss_is_fallback=True`, 与 ctx/full 共享 `n_articles` 分母, 不产生单边孤儿行。三轨之间同样构成"各自 just-identified 并排、互为稳健性、禁止混入同一 over-identified Hansen J"的关系, 与 N-邻域梯子的铁律相互正交、不交叉叠加。

【文献定位】
本家族的"用文本相似度定义同业邻域、以邻域内平均距离刻画策略独特/趋同程度"这一整体设计, 方法学谱系上溯到 Hoberg & Phillips (2016, Journal of Political Economy) 基于 10-K 文本余弦相似度构造的文本网络产业分类 (TNIC), 以及同一作者组在 Hoberg, Phillips, & Prabhala (2014, The Journal of Finance) 中给出的产品市场流动性 (fluidity) 指标——后者衡量竞争环境的动态变化程度, 与本家族衡量单个主体相对同业的静态差异程度构成互补视角。直接的测度设计范式取自 Guzman & Li (2023, Management Science) 的"测度创业策略": 该文用文本相似度构造同业邻域、以邻域内平均距离作为策略独特性指标, 本家族在方法上完全平行, 仅将底层表征从其原始设定换成 LDA 主题分布 + JSD 距离这一条概率分布距离分支 (与家族内 TF-IDF 余弦、Embedding 余弦等其余分支互为稳健性)。在组织理论侧, Haans (2019, Strategic Management Journal) 与 Su, Gao, & Tan (2024, Strategic Management Journal) 关于"最优独特性" (optimal distinctiveness) 的讨论, 为"差异度既非越高越好也非越低越好, 存在同业趋同压力与差异化收益的权衡"这一构念解释提供了理论支点, 是解读本家族回归系数符号时应参照的理论背景, 而非该指标的测度方法来源。 在邻域界定这一环节上, Shen、Zhang、Zhong 与 Lu (2025) 提供了近年的直接支撑: 该文在中国某天使投资平台的 3266 份商业计划书上, 分别计算同一创业企业相对在位企业与相对同台同类创业企业的独特性, 发现两个参照物下的独特性对投资人评价的作用方向不同且互相调节, 由此证明"独特性相对于谁而言"的参照集界定会实质改变构念的经济含义, 锚定本族把 N=20 同业邻域视为须显式披露与检验的设计选择、而非中性技术细节这一立场。迁移边界须诚实标明: 该文的参照集由平台类别与投资人视角离散界定, 非本族在连续文本向量空间中的近邻检索; 层级为创业企业而非银行-年度, 语料为商业计划书而非第三方媒体报道; 且该文并未变动参照集的规模宽窄, 故不构成 N∈{5,10,20,30,40,50} 邻域宽度并排稳健性梯子的必要性论证, 亦未使用 LDA 主题分布或 JSD 距离——本条只锚"参照集须被显式界定与检验"这一设计前提, 不锚本族的表征分支与距离核。
## VAR: strat_diff_n20_lda

【变体差分】
本列是 full 轨 (无 `_ctx`/`_ss` 后缀), 使用标题+全文正文物化文本 (`content_full`) 作为 LDA 主题分布估计的输入语料, 是留篇门控口径的直接对应轨——stage 21 判定"是否为一篇有效的银行金科报道"仅依据 full 轨的 `llm_verified_full`, 因此本列所覆盖的行宇宙是家族三轨中的基准全集, ctx/ss 两轨是其子集上的条件稳健性测度。方法分支固定为 LDA 主题分布 + Jensen-Shannon 散度 (与家族内 TF-IDF char/word 轨、Embedding Qwen/large 轨并排, 互为稳健性)。邻域宽度固定为 N=20, 即近邻数量取每篇文章语义空间中最相似的 20 篇同业报道, 属 2026-07-02 top-k N 扩展新增的大邻域档位之一, 与 canonical N=5 及 N∈{10,30,40,50} 各档位各自独立计算、并排呈现, 用于检验战略差异度结论对"多大的同业比较窗口"这一构造判据是否稳健, 不构成任何一档对其余各档的替代或包含关系。

由于 full 轨语料未经实体窗口或共现句筛窄, 语料长度分布与主题异质性通常大于 ctx/ss 两轨, 相应地本列的 LDA 主题分布往往更平滑、峰度更低, JSD 距离的横截面方差在直觉上也应更大——这是 full 轨"信息量更全但噪声也更多"这一权衡在本方法分支下的具体体现, 解读回归系数时应留意此差异不代表测度错误, 而是三轨各自刻意保留的构造判据分歧。分词器沿用注入 607 金科词表的领域感知分词器, 保证"金融科技""区块链"等复合词整词参与主题估计, 不因通用分词拆碎而稀释领域主题的可辨识度。N=20 档相对 canonical N=5 档纳入更多同业作为比较基准, 距离均值通常更趋向于同业整体分布的中心, 对单一异常近邻的敏感度更低, 属于"更平滑但更粗"的稳健性设定, 二者差异本身即是研究者应披露的规格曲线信息之一, 不应择一而弃另一。

## VAR: strat_diff_n20_lda_ctx

【变体差分】
本列与 canonical `strat_diff_n20_lda`(full 轨) 及 `strat_diff_n5_lda` 等同族列的唯一系统性差异是文本轨: 本列使用 ctx 轨物化文本 `content_ctx` (标题+银行/金科实体窗口) 作为 LDA 主题分布估计的输入语料, 而非全文正文。ctx 轨行宇宙是 full 轨留篇集的子集 (2026-06-29 起门控只看 full), 属"conditional-on-full"的稳健性/测度轨, 用以检验战略差异度结论是否对"截取实体附近窗口 vs 使用全文"这一文本抽取判据敏感。若某篇文章在实体窗口截取后 `ctx_is_fallback=True` (即缺乏可定位的实体窗口而退化为全文), 该行仍按 ctx 轨自身的分母正常纳入本列计算, 不借用 full 轨的中间量。方法分支 (LDA+JSD) 与邻域宽度 (N=20) 与 canonical 一致, 仅文本轨不同; 与 full 轨、ss 轨各自 just-identified 并排, 互为稳健性、不分主次, 三轨结果不应被混入同一 over-identified 的 Hansen J 检验。

ctx 轨的构造意图是剔除文章中与银行/金科实体无关的背景段落 (如无关的宏观经济评论、其他企业动态), 让 LDA 估计的主题分布更集中反映实体周边的语义内容, 理论上应比 full 轨得到更"尖锐"、主题集中度更高的分布, 使 JSD 距离对策略差异的刻画更聚焦但也更容易受窗口截取误差影响 (例如实体识别漏检导致窗口过窄、丢失关键上下文)。本列与 full 轨、ss 轨在同一 N=20 邻域宽度下的差异, 提供了"文本抽取粒度"这一独立于"邻域宽度梯子"和"底层表征方法梯子"的第三个正交稳健性维度: 三个维度两两不交叉叠加, 各自的稳健性结论应分别陈述, 不应合并成单一的联合检验。若 full 轨与 ctx 轨在符号和显著性上高度一致, 可视为战略差异度构念对文本抽取粒度不敏感的证据; 若二者出现系统性偏离, 则需结合 fallback 比例等辅助诊断列进一步排查是实体识别质量问题还是构念本身的粒度依赖。

## VAR: strat_diff_n20_lda_ss

【变体差分】
本列与 canonical `strat_diff_n20_lda`(full 轨) 及 `_ctx` 轨的唯一系统性差异同样是文本轨: 本列使用 ss 轨物化文本 `content_ss` (标题+银行∧金科在同一句 ±1 句窗口内共现的片段) 作为 LDA 主题分布估计的输入语料, 是三轨中窗口最窄、判据最严的一条。ss 轨回退语义镜像 ctx 轨: 当某篇文章内不存在银行词与金科词的同句共现时, `content_ss` 退化为全文 body, 对应标记列 `ss_is_fallback=True`, 与 full/ctx 轨共享同一个 `n_articles` 分母, 不因回退而产生单边孤儿行或分母口径漂移。行宇宙同样是 full 轨留篇集的子集 (full-only 门控), 用以检验战略差异度结论在"最贴近银行-金科共现语境的极窄文本窗口"下是否依然成立, 是三轨中判据最严格、对文本噪声最不敏感但样本覆盖可能因回退而最依赖 fallback 标记的一条稳健性轨。方法分支 (LDA+JSD) 与邻域宽度 (N=20) 与家族其余两列一致; 三轨 (full/ctx/ss) 各自 just-identified 并排, 互为稳健性、不分主次, 不得混入同一 over-identified 的 Hansen J 检验。

ss 轨是三轨中构造判据最严的一条: 只有银行词与金科词落在同一句 (±1 句窗口, `context_window.ss_sentence_radius` 键控) 内的片段才计入语料, 相比 ctx 轨的整段实体窗口更窄, 目的是把 LDA 主题分布的估计语料收窄到"银行与金科业务真正被同时论及"的最小语义单元, 从而最大程度剔除同篇报道中与银行-金科关系无关的段落噪声。但正因窗口极窄, 当一篇文章缺乏同句共现时触发的回退 (`ss_is_fallback=True`, 退化为全文 body) 比例通常高于 ctx 轨的回退比例, 分析时应结合该 fallback 标记列检查本列在低共现密度子样本中的估计稳定性, 避免把"回退样本占比过高导致的均值拉平"误读为"策略差异度本身不显著"。ss 轨与 ctx 轨、full 轨的差异构成文本抽取粒度这一独立稳健性维度上的极端设定, 三者共同构成从"全文"到"实体窗口"再到"同句共现"依次收窄的判据序列, 序列内部不设主次, 结果一致则增强构念效度、不一致则提示需进一步的机制性诊断而非简单取舍。

<!-- rendered-citations:begin -->
Guzman, J., & Li, A. (2023). Measuring founding strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Su, J., Gao, X., & Tan, J. (2024). Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market threats, payouts, and financial flexibility. The Journal of Finance, 69(1), 293-324. https://doi.org/10.1111/jofi.12050
Shen, R., Zhang, H., Zhong, W., & Lu, J. (2025). Distinctiveness from whom? Evaluation of startups' distinctiveness from multiple referents in angel investment platforms. Strategic Entrepreneurship Journal, 19(1), 171-195. https://doi.org/10.1002/sej.1521
<!-- rendered-citations:end -->
</content>
