---
family_id: F148
columns:
- centroid_diff_lda
- centroid_diff_lda_ctx
- centroid_diff_lda_ss
unit: 策略差异度 (无量纲, 主题分布空间到行业质心的距离)
formula: "centroid_diff_lda = 1 - cos(theta_i, theta_bar_{-i}); theta_i = 银行 i 当年报道文本的 LDA 主题占比向量 (probability simplex); theta_bar_{-i} = 当年同业 (peer) 主题占比向量的 leave-one-out 行业质心 (排除银行 i 自身, c_{-i}=(n*c - theta_i)/(n-1)); dist = 主题分布空间内的余弦距离 1-cos(., .)"
producer: news_process/pipeline/features/strategic_diff.py ; news_process/pipeline/panel/export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.1002/smj.3687
  type: journal
  authors: Arts, S., Cassiman, B., & Hou, J.
  year: 2025
  title: "Technology differentiation, product market rivalry, and M&A transactions"
  venue: Strategic Management Journal
  vol: 46
  issue: 4
  pages_or_artno: 837-862
- doi: 10.1002/smj.3586
  type: journal
  authors: Miller, C. D., & Wang, R. D.
  year: 2024
  title: "Product digitization and differentiation strategy change: Evidence from the book publishing industry"
  venue: Strategic Management Journal
  vol: 45
  issue: 7
  pages_or_artno: 1241-1272
- doi: 10.1287/mnsc.2022.4369
  type: journal
  authors: Guzman, J., & Li, A.
  year: 2023
  title: "Measuring founding strategy"
  venue: Management Science
  vol: 69
  issue: 1
  pages_or_artno: 101-118
- doi: 10.1002/smj.2978
  type: journal
  authors: Haans, R. F. J.
  year: 2019
  title: "What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories"
  venue: Strategic Management Journal
  vol: 40
  issue: 1
  pages_or_artno: 3-27
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
new_dois: []
---

## CORE

【构念与来源】
本家族测度的是一家银行在给定年度里被媒体报道所刻画的"战略/主题定位"相对于同业行业整体的偏离程度, 即媒体感知意义上的策略差异度 (strategic differentiation)。构念根植于战略管理与产业组织文献对"差异化"的长期关注: Hoberg & Phillips (2016) 用企业自有披露文本构造文本网络产业与内生产品差异化, 开创了以文本余弦度量企业间相似/差异的范式; Guzman & Li (2023) 进一步把"创始战略"操作化为文本近邻距离; Haans (2019) 从最优区分 (optimal distinctiveness) 视角论证差异化在同质与异质类别中对绩效的非线性含义; Arts, Cassiman & Hou (2025) 与 Miller & Wang (2024) 则把技术/产品差异化的文本测度延伸到并购与数字化情境。本项目沿用这一测量传统, 但把观测文本从企业自有 10-K 披露替换为第三方媒体报道, 因此度量的是"媒体感知差异"而非"自我披露差异", 这是与原始文献最关键的口径差别, 亦是解读时须持续声明的局限。

【方法学与计算】
本家族属"全行业向量法"(industry centroid 法, 方法出处标注为谢佳松 (2025)): 先在语料上训练 LDA 主题模型, 把每篇报道映射为主题占比向量 theta (落在 probability simplex 上, 非负且和为一); 再把同一银行同一年度的报道文本聚合为该银行的年度主题占比向量 theta_i; 然后对该年度同业银行的主题向量求均值得到行业质心, 且刻意采用 leave-one-out 口径——即在为银行 i 计算质心时排除其自身, c_{-i}=(n*c - theta_i)/(n-1), 避免银行 i 的向量既进被减项又进质心而引入约 1/n_t 量级的机械自相关 (源码明确标注: 含自身的均值会系统性抬高与行业越正交的银行的距离, 使 centroid_diff 右尾偏移)。真实距离算子是余弦距离而非泛化的欧氏/任意向量距离: centroid_diff_lda = 1 - cos(theta_i, c_{-i}), 即 1 减去该行年度主题向量与 leave-one-out 行业质心的余弦相似度。距离越大, 说明该行当年被报道所刻画的主题结构越偏离行业中心, 战略/话语定位越独特。因 LDA 主题向量是非负分布, 其余弦相似度落在 [0,1], 故本 LDA 轨的余弦距离值域被约束在非负区间 (与 Embedding 余弦真值域 [-1,1] 的处理不同, 嵌入距离列可达 [0,2]; 本 LDA 轨不做负值地板问题)。centroid_diff_lda 是本家族的 canonical 列, 与同一"全行业向量法"下的 TF-IDF 字符/词级轨 (centroid_diff_tfidf_c/_w) 及嵌入轨 (centroid_diff_emb, 及其 co-primary _lg 孪生 centroid_diff_emb_lg) 并列; 它又与"N-最近邻法"(Guzman & Li 2023 的 strat_diff_n5_lda) 属不同的差异化算子——前者对照行业质心, 后者对照最近的 N 个同业, 两者构念相关但不可互相替代, 稳健性配对时勿错配。

【文献定位】
在测量方法谱系上, LDA 主题分布法与 TF-IDF 词频法、稠密嵌入法互为稳健性: 三者从不同文本表示空间近似同一"战略差异"潜变量, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把 LDA 轨与 TF-IDF 轨或嵌入轨混进同一 over-identified 的 Hansen J 过度识别检验。同理, 本家族的三条文本轨 (full/ctx/ss) 也各自 just-identified 并排, 禁混同一 over-identified Hansen J。就构念区分而言, 本"质心偏离"度量刻画的是横截面上的"离群/独特"程度, 与刻画相邻期主题连续性的文本连贯性变量 (coh_lda 等) 正交——后者比较同一银行相邻年度的主题分布, 而非比较该行与同业的差距。已知局限有二 (源码明确标注): 其一, 原始文献用企业自有披露文本, 本项目用第三方新闻, 测的是媒体感知而非自我披露; 其二, 银行样本每年约五十余家, 远小于 TNIC 数据集的数千家企业, 行业质心由小样本估得, 须留意小样本偏差对质心稳定性的影响。上述两点在把本家族用作战略差异代理变量时应作为稳健性叙事的一部分予以披露。

## VAR: centroid_diff_lda

【变体差分】
本列是家族 canonical 列, 对应 Full 文本轨。Full 轨的输入文本 content_full = 标题 prepend 到全文正文 (stage 14 ctx_materializer 物化, 原始"内容"列不动), 即用整篇报道的全量词面参与 LDA 推断与主题占比聚合。它与家族内另两列在轨道口径上唯一不同: 本列使用最完整的文本上下文, 因而主题向量最"厚"、行业质心估计相对最稳。度量算子为"全行业向量法": 银行年度主题占比向量 theta_i 到当年同业质心 theta_bar 的距离, 值域非负, 越大越偏离行业中心。作为 canonical 轨, 本列是家族的首要测度, ctx 与 ss 两轨降为其规格稳健性轨。与本列同"全行业向量法"但换文本表示的稳健配对是 centroid_diff_tfidf_c (TF-IDF 字符轨) 与 centroid_diff_emb (嵌入轨); 与本列换算子的对照是 strat_diff_n5_lda (LDA 主题分布下的 N=5 最近邻差异度)——务必区分"对照质心"与"对照最近邻"两种差异化定义, 稳健性表格里勿把两者当作同一构念的替代测量。本列与三轨其余两列各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。就阅读该列取值而言: 一家银行若某年被大量报道刻画为聚焦于与同业迥异的主题 (例如集中于某类金融科技创新或某个监管议题), 其 Full 轨主题占比向量便会显著偏离由全部同业均值构成的行业质心, 本列取值随之抬升; 反之若报道话语与同业趋同, 取值向零收敛。因 Full 轨用整篇文本, 主题估计对偶发短讯较不敏感, 故本列相对另两轨更平滑、更适合作为主回归的首要战略差异代理。

## VAR: centroid_diff_lda_ctx

【变体差分】
本列是 canonical 列的 Ctx 文本轨稳健性孪生。与 Full 轨唯一的差分维度在输入文本: content_ctx = 标题 prepend 到"实体窗口"文本, 即只保留围绕目标银行实体一定窗口范围内的正文片段 (stage 14 物化), 而非整篇全文。因此 Ctx 轨的 LDA 主题占比向量刻画的是"与银行实体邻近语境"所呈现的主题结构, 相对 Full 轨过滤掉了报道中与该行关系较远的段落噪声, 更聚焦于实体相关话语。度量算子与 canonical 完全一致——银行年度主题向量到当年同业行业质心的距离, 仅文本轨不同。Ctx 轨定位为 Full 轨的规格稳健性轨: 若主结论只在全量文本下成立而在实体窗口文本下消失 (或反之), 即提示测度对文本范围的敏感性。本列与 Full、Ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J 过度识别检验。其稳健配对仍限于同为 Ctx 轨、同为"全行业向量法"的其它文本表示列 (如 centroid_diff_tfidf_c_ctx、centroid_diff_emb_ctx), 不与 Full 轨或最近邻算子跨轨错配。需要强调的是, Ctx 轨与 Full 轨的差别纯粹来自文本范围而非度量算子: 两轨用同一套 LDA 主题空间与同一质心距离公式, 因此二者之差可被直接解读为"把报道语境收缩到银行实体邻近窗口"对策略差异测度的影响。在实体相关话语与全文话语高度一致时, 本列应与 Full 轨接近; 二者出现系统性背离, 即是测度对上下文范围敏感的信号, 应在稳健性叙事中如实披露。

## VAR: centroid_diff_lda_ss

【变体差分】
本列是 canonical 列的 Ss (same-sentence) 文本轨稳健性孪生, 判据最严。与 Full/Ctx 轨的差分维度在输入文本: content_ss = 标题 prepend 到"银行与金融科技同句共现 ±N 窗"文本 (窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 即只保留目标银行与金科词在同一句 (及相邻窗口) 共现的片段。这使 Ss 轨的 LDA 主题向量最贴近"银行×金融科技"这一交叉议题的话语, 但也最稀疏。Ss 轨严格镜像 Ctx 的回退语义: 当某银行某年不存在银行∧金科同句共现时, content_ss 回退为全文 body, 对应 ss_is_fallback=True (与 Ctx 的 fallback 口径一致), 以避免样本被静默清空; 若 FINTECH_AC=None 则 is_fallback 全 True 优雅降级。度量算子仍是"全行业向量法"——银行年度主题向量到当年同业质心的距离。因 Ss 文本最短, 在浅面板 (如 T=2 开发样本) 上主题向量可能高度稀疏甚至退化, 属预期现象, 生产语料 (T=19) 下方可正常展开。本列与 Full、Ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 稳健配对限于同为 Ss 轨、同为质心算子的其它表示列, 不跨轨、不跨算子错配。三轨由宽到严 (full → ctx → ss) 构成对文本范围的一条规格梯子: 主结论若在最严的 Ss 轨仍稳健, 即表明该战略差异信号确实由银行与金融科技的交叉话语驱动, 而非全文里的无关段落所致; 反之若信号仅存于 Full 轨而在 Ss 轨消失, 则须谨慎解读其构念含义。此为该列相对 canonical 的核心价值所在。

<!-- rendered-citations:begin -->
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Miller, C. D., & Wang, R. D. (2024). Product digitization and differentiation strategy change: Evidence from the book publishing industry. Strategic Management Journal, 45(7), 1241-1272. https://doi.org/10.1002/smj.3586
Guzman, J., & Li, A. (2023). Measuring founding strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
<!-- rendered-citations:end -->
