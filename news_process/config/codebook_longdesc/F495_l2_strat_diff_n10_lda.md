---
family_id: F495
columns:
- strat_diff_n10_lda
- strat_diff_n10_lda_ctx
- strat_diff_n10_lda_ss
unit: 无量纲主题分布距离得分 (JSD 平方根, 值域 [0,1])
formula: 'strat_diff_n10_lda_i = mean_{j∈KNN10(i)} sqrt(JSD(θ_i, θ_j)); KNN10 = 对银行 i 与所有其他银行 LDA 主题分布 θ 两两计算 Jensen-Shannon 距离矩阵后升序排列取距离最小的 10 家同业 (非余弦相似度)'
producer: pipeline\features\strategic_diff.py ; pipeline\panel\stata_export.py
upstream: []
citations:
- doi: 10.1086/688176
  type: journal
  authors: "Hoberg, G., & Phillips, G."
  year: 2016
  title: "Text-Based Network Industries and Endogenous Product Differentiation"
  venue: Journal of Political Economy
  vol: '124'
  issue: '5'
  pages_or_artno: 1423-1465
- doi: 10.1287/mnsc.2022.4369
  type: journal
  authors: "Guzman, J., & Li, A."
  year: 2023
  title: "Measuring Founding Strategy"
  venue: Management Science
  vol: '69'
  issue: '1'
  pages_or_artno: 101-118
- doi: 10.1002/smj.2978
  type: journal
  authors: "Haans, R. F. J."
  year: 2019
  title: "What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories"
  venue: Strategic Management Journal
  vol: '40'
  issue: '1'
  pages_or_artno: 3-27
- doi: 10.1002/smj.3549
  type: journal
  authors: "Su, J., Gao, X., & Tan, J."
  year: 2024
  title: "Positioning for Optimal Distinctiveness, How Firms Manage Competitive and Institutional Pressures under Dynamic and Complex Environment"
  venue: Strategic Management Journal
  vol: '45'
  issue: '2'
  pages_or_artno: 333-361
new_dois: []
---

## CORE

【构念与来源】
本家族衡量银行在给定年度媒体报道文本所呈现的战略主题结构与其"最相似同业圈"之间的偏离程度, 用以刻画银行战略定位的独特性 (strategic distinctiveness/differentiation)。构念直接承袭文本产品市场差异度传统: Hoberg & Phillips (2016, Journal of Political Economy) 用 10-K 文本余弦相似度构造企业间文本网络产业, 证明企业在该网络中的相对位置刻画真实的产品市场竞争关系而非静态行业代码; Guzman & Li (2023, Management Science) 进一步把"与最近邻的平均文本距离"用作创业战略测度的操作化范式, 是本列 N-近邻 (KNN) 构造思路的直接来源。本项目把该范式移植到中文银行业媒体报道语料: 不看企业自身披露文本 (10-K/年报), 而看外部媒体对银行金融科技相关战略动作的报道文本, 用同一套 N-近邻差异度逻辑衡量"报道所呈现的银行战略主题与同业有多不同"。家族键 `l2_strat_diff_n10_lda` 中 `n10` 是 top-k 近邻数扩展 (canonical N=5 之外的大邻域孪生, 2026-07-02 fix topk-n-expansion 落地, N∈{10,20,30,40,50}), `lda` 是五种底层表征方法之一 (另四种为 TF-IDF char 轨/TF-IDF word 轨/Qwen3 嵌入轨/text-embedding-3-large `_lg` 轨) 中的 Latent Dirichlet Allocation 主题分布法, 距离核为 Jensen-Shannon Divergence (JSD) 而非余弦。

【方法学与计算】
计算分两步。第一步, 对每篇报道文本 (按轨道 full/ctx/ss 分别取原始 `content_full`/`content_ctx`/`content_ss`, prepend_title 已内嵌标题) 用注入 1506 金科词的领域感知分词器切词 (`_get_diff_tokenizer`, 自 2026-06-21 起金融科技/区块链等领域复合词整词保留, fix inject-fintech-word-lda 口径统一), 训练/推断出一个固定维度的 LDA 主题分布 θ (每篇文章一个概率单纯形向量, 维度=主题数 K, 各分量非负且和为 1)。第二步, 按银行 × 年度聚合出该银行当期报道的 LDA 主题分布质心 θ_i, 与样本中所有其他银行的质心两两计算 Jensen-Shannon 距离 (JSD 的平方根, 满足三角不等式, 是 Shannon 熵意义下两个概率分布"可分辨程度"的标准度量, Lin 1991 首次证明其为可用作距离的散度), 取与 θ_i 最近的 N=10 家同业 (KNN10), 对这 10 个 JSD 距离取算术平均, 得到 `strat_diff_n10_lda`。JSD 距离的值域天然落在 [0,1] (以 log 底 2 归一化时上界为 1), 与 TF-IDF/Embedding 轨的距离值域刻度不同 (TF-IDF/LDA 轨 ∈ [0,1]; Embedding 轨因原始余弦真值域为 [-1,1], 对应距离列 ∈ [0,2], 2026-06-11 fix omni-g-strategic-02/03 之前曾被错误 clip 到 [0,1] 造成值域删失, 现已修正) — 跨方法比较绝对水平无意义, 只应比较标准化系数或方向。数值越大, 说明该银行当期报道所呈现的主题结构与其 10 个最相似同业相比仍然偏离 (即便是"最相似的一批"也谈不上雷同), 是战略独特性/差异化定位的代理; 数值越小, 说明该银行的媒体呈现战略与同业高度趋同 (可能因业务模式高度模仿或行业整体叙事同质化)。
N-近邻梯子的引入动机是稳健性: 单一固定 N (如 canonical N=5) 的近邻集合在小样本行业分区或年度截面较薄时对个别极端邻居敏感, top-k 扩展 (N∈{10,20,30,40,50}) 让研究者观察差异度指标是否随近邻圈扩大而单调收缩、以及在何种 N 下结论仍然稳健。`strat_diff_n10_lda` 是这一梯子里 N=10 的一档, 与 N=5 (canonical) 及 N∈{20,30,40,50} 的其余各档并排、互为稳健性、不分主次——不应把不同 N 值的列同时放进同一个过度识别 (over-identified) 的 Hansen J 检验框架, 每个 N 各自构成一个 just-identified 的稳健性平行宇宙。三个文本轨道 (full/ctx/ss) 同理各自 just-identified 并排, full=全文本 (标题+正文全文), ctx=标题+银行/金科实体窗口, ss=标题+银行∧金科同句±N 窗 (config/filtering.yaml::context_window.ss_sentence_radius, 默认 1); 三轨间同样禁止混入同一 Hansen J。ss 轨的回退语义镜像 ctx 轨: 若某银行-年度文章集合中不存在银行与金科词同句共现的文章, 则该文章 `content_ss` 退化为全文 body, `ss_is_fallback=True`, 参与聚合但共享全文 `n_articles` 分母; 若 `FINTECH_AC=None` (金科词典未加载), 全体 `*_is_fallback` 置 True 优雅降级, 不静默清空数据。留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否计入"银行金科报道"样本只看 `llm_verified_full == True`, ctx/ss 轨是在该 full-only 行宇宙子集上的 conditional-on-full 测度/稳健性轨。产出列由 `pipeline/features/strategic_diff.py` 计算 (~125 基础列 + top-k N 扩展净增约 75 列), 经 `pipeline/panel/stata_export.py` 打标签导出面板/dta。

【文献定位】
本家族方法学谱系有三条主线交汇。第一条是文本产品市场竞争与战略独特性: Hoberg & Phillips (2016, Journal of Political Economy) 建立"文本相似度网络刻画真实竞争关系"的范式, 是本族最近邻思路的方法论源头; Haans (2019, Strategic Management Journal) 论证"差异化的价值取决于所处类别是同质还是异质环境", 提醒差异度指标的经济含义并非单调"越大越好", 而须结合行业竞争结构解读; Su, Gao & Tan (2024, Strategic Management Journal) 进一步讨论企业在动态复杂环境下如何为"最优独特性" (optimal distinctiveness) 定位, 呼应本族数值不宜脱离行业情境孤立解读的方法论提醒。第二条主线是把这套文本距离范式操作化为可重复的战略测度构造流程: Guzman & Li (2023, Management Science) 的"与最近邻平均文本距离"测度框架被本族直接借鉴为 N-近邻均值算法本身。第三条是 LDA 主题模型与 JSD 距离的技术基础 (Blei, Ng & Jordan 2003 提出 LDA; Lin 1991 建立 JSD 作为可度量距离的数学性质), 二者共同构成本列区别于 TF-IDF/Embedding 各轨的"主题分布视角"表征选择——LDA 把文本压缩为低维、可解释的主题占比向量, 距离核选 JSD 而非余弦, 是因为主题分布是概率单纯形对象, JSD 比欧式/余弦距离更契合概率分布间"信息可分辨度"的语义。

## VAR: strat_diff_n10_lda

【变体差分】
本列是家族 canonical 的全文 (full) 轨: 文本输入取 `content_full` (标题 + 正文全文, prepend_title), 分词器为注入 1506 金科词的领域感知分词器, LDA 主题分布质心两两 JSD 距离, 对每家银行取与之最近的 N=10 家同业 (KNN10) 距离均值。它与同家族的 `_ctx`/`_ss` 两轨在文本窗口范围上互斥并排 (full 用全文、ctx 用实体窗口、ss 用银行∧金科同句窗口), 三者互为稳健性、不分主次, 禁止混进同一 Hansen J; 与非本家族的 `strat_diff_n5_lda` (canonical N=5) 及 `strat_diff_n{20,30,40,50}_lda` 系列在 top-k 近邻数上并排, 同样各自 just-identified、禁止混入同一 Hansen J。留篇门控为 full-only, 本列所在的样本行宇宙即门控本身依据的行宇宙 (无需 conditional-on-full 的额外收缩)。
在方法族内, 本列还与同轨的 TF-IDF char/word 两法 (`strat_diff_n10`/`strat_diff_n10_w`) 及 Qwen3/`_lg` 两嵌入法 (`strat_diff_n10_emb`/`strat_diff_n10_lg`) 并排, 五种表征方法各有取舍: TF-IDF 轨对高频词表面用词敏感, LDA 轨压缩到主题占比层面对同义改写更稳健但依赖主题数 K 的先验设定, Embedding 轨捕捉稠密语义但值域刻度与前两者不同 ([0,2] 而非 [0,1])。研究者报告本列结果时应同时给出至少一种非 LDA 轨作为交叉验证, 而不是把 LDA 单轨的显著性当作最终结论; 五法之间同样各自 just-identified 并排, 不构成同一 over-identified 系统的多重工具变量。数值层面, N 越大意味着近邻圈越宽, 个别极端邻居 (例如某年报道量极少或业务转型剧烈的银行) 对均值的拉动被稀释, 因此 `strat_diff_n10_lda` 相对 canonical N=5 通常呈现更平滑、方差更小的截面分布, 若两档 N 下的回归系数方向一致但显著性随 N 增大而减弱, 应解读为"结论对近邻圈宽窄敏感", 而非其中一档单独失败。

## VAR: strat_diff_n10_lda_ctx

【变体差分】
本列相对 canonical 全文轨的差分维度是文本窗口: 输入取 `content_ctx` (标题 + 银行/金科实体窗口, stage 14 `ctx_materializer` 物化), 其余计算链路 (领域感知分词器、LDA 质心、JSD 距离、N=10 近邻均值) 与 `strat_diff_n10_lda` 完全一致。ctx 轨与 full 轨、ss 轨互为稳健性并排, 不分主次; 作为 conditional-on-full 测度轨, 其行宇宙是 full-only 留篇门控之后的子集, 逐轨单独计算 (不借用其他轨道的分母或缺失值填补)。当某银行-年度报道文本中缺乏可用的实体窗口内容时, 该篇不参与 ctx 轨聚合 (与 ss 轨"退化为全文"的回退语义不同——ctx 轨本身无镜像回退规则, 缺失即缺失, 不臆造替代文本)。
ctx 轨的经济含义是把观测窗口从"整篇报道在讲什么"收窄到"报道里紧贴银行/金科实体的那部分文字在讲什么", 目的是压低与银行战略无关的行文噪声 (背景介绍、记者评论、无关业务段落) 对 LDA 主题分布估计的稀释效应。理论上, 若某银行的报道存在大量与战略定位无关的套话或背景铺垫, full 轨的主题质心会被这些噪声段落拉向行业通用主题, 使 `strat_diff_n10_lda` 系统性偏小 (看起来比实际更"趋同"); ctx 轨通过只截取实体窗口文字, 更贴近银行自身战略叙事的核心内容, 理论上应放大真实的战略异质性。因此若 ctx 轨的差异度均值显著高于 full 轨, 与"套话稀释"假说一致, 是该假说的间接支持证据而非因果证明; 报告结果时应把 ctx 轨明确定位为 conditional-on-full 的稳健性检验, 不作为独立的因果识别变量使用。

## VAR: strat_diff_n10_lda_ss

【变体差分】
本列相对 canonical 全文轨的差分维度同样是文本窗口, 但取值更严格: 输入取 `content_ss` (标题 + 银行∧金科同句 ±N 窗, 默认窗口半径 1 句, `config/filtering.yaml::context_window.ss_sentence_radius`), 其余计算链路与 `strat_diff_n10_lda`/`strat_diff_n10_lda_ctx` 一致。ss 轨的回退语义镜像 ctx 轨的"缺失退化"精神但具体实现不同: 若某篇文章不存在银行与金科词同句共现, `content_ss` 退化为该篇全文 body 而非留空, 并置位 `ss_is_fallback=True`, 该篇仍参与聚合、共享全文 `n_articles` 分母 (与 ctx 轨"缺失即不参与"不同); 若 `FINTECH_AC=None`, 全体 `*_is_fallback` 置 True, 全轨优雅降级为等效全文轨而非崩溃。ss 轨与 full/ctx 两轨互为稳健性并排, 不分主次, 禁止混进同一 Hansen J; 作为最严格的判据轨 (要求银行与金科词严格同句共现), 其在信噪比与样本量之间的权衡与 ctx 轨 (实体窗口, 较宽松) 相对——两者都是 conditional-on-full 的稳健性检验, 数值差异应解读为文本窗口宽严带来的测量口径差异, 而非其中一轨"更对"。
需特别注意 ss 轨的回退比例 (`ss_is_fallback` 为 True 的篇数占比) 是解读本列时的必查诊断量: 若某银行-年度绝大多数报道都缺乏银行∧金科词的严格同句共现, 该银行当期的 `strat_diff_n10_lda_ss` 实质上是退化为(近似)全文轨的产物, 与真正满足同句判据的银行样本在测量精度上不可等量齐观, 不应不加区分地放入同一回归方程直接比较系数大小。ss 轨判据的严格性来自 stage 13 共现硬过滤与 stage 14 物化的共同约束——只有句子层面同时命中银行实体与金科词典 (裸 AC 1506 词) 才计入窗口, 银行侧另叠加否定词与短名过滤以降低误匹配。这一严格性的代价是可用文本量比 ctx 轨更小, 换来的收益是主题分布估计更聚焦于"银行与金科科技话题直接同句出现"的叙事片段, 理论上应比 ctx 轨进一步放大战略趋同/差异化的信号强度, 但估计方差也随之增大, 是三轨里样本效率最低、语义纯度最高的一档。

<!-- rendered-citations:begin -->
Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Guzman, J., & Li, A. (2023). Measuring Founding Strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Haans, R. F. J. (2019). What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Su, J., Gao, X., & Tan, J. (2024). Positioning for Optimal Distinctiveness, How Firms Manage Competitive and Institutional Pressures under Dynamic and Complex Environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
<!-- rendered-citations:end -->
</content>
