---
family_id: F149
columns:
- centroid_diff_tfidf_c
- centroid_diff_tfidf_c_ctx
- centroid_diff_tfidf_c_ss
unit: 文本向量距离 (无量纲, ∈ [0,1])
formula: "centroid_diff_tfidf_c = 1 − cos(v_i, c_{-i}); v_i = 银行 i 在 year_t 全部报道拼接后的 char 级 TF-IDF 向量; c_{-i} = (n·c̄ − v_i)/(n−1) 即同年剔除银行 i 自身后的 leave-one-out 行业质心; 三轨 full/ctx/ss 各自独立成 v_i 与 c_{-i}"
producer: pipeline\features\strategic_diff.py ; pipeline\panel\export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_yearly.parquet
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
本家族刻画一家银行在给定年度里, 其被媒体报道所呈现的"战略语义定位"相对于同期全行业平均定位的偏离程度, 即战略差异化 (strategic differentiation / distinctiveness) 的文本代理测度。构念的直觉是: 若一家银行当年的报道内容在词汇构成上与全行业的"共同话语中心"越接近, 则说明它在媒体视野中越随大流、越缺乏可识别的独特定位; 反之, 一家银行的报道若在措辞与议题上系统性地偏离行业质心, 则其被感知的战略差异化程度越高。该构念承接产业组织与战略管理文献中以文本刻画企业异质定位的传统: Hoberg & Phillips (2016) 用企业 10-K 披露文本两两余弦相似度构造基于文本的产业网络与内生产品差异化度量, 奠定了"以文本向量距离度量竞争定位"的方法学基石; Guzman & Li (2023) 进一步把创业企业的自我描述文本嵌入向量空间, 以与同行的近邻距离衡量创始战略的差异化。本项目沿用这一向量空间思路, 但把度量对象从企业自有披露替换为第三方新闻报道, 因此测量的是"媒体感知差异"而非"自我披露差异"——这一替换是构念层面的关键差别, 也是后文局限叙事的核心。

【方法学与计算】
计算分三步。第一步聚合: 对每家银行 i 在 year_t 内命中的全部留篇报道, 将其文本按轨道拼接为一份银行-年度超级文档, 再用字符级 (char_wb) TF-IDF 向量化, 得到银行-年度向量 v_i。家族短名后缀 `_c` 即标记 char 级 (与 jieba 词级的 `_w` 孪生列相对)。这里须精确区分 char 轨与词级轨的向量化口径, 以免误述: 本 char 族走的是 scikit-learn 的 char_wb 字符 n-gram 分析器, 直接在字符层面滑窗切 n-gram 特征, 并不经过词级路径那套注入 1506 金科词的领域感知分词器 (_get_diff_tokenizer); 那套令"金融科技""区块链"等领域复合词整词保留、不被切碎的独立分词器, 自 2026-06-21 起只服务 jieba 词级 (`_w`) 与 LDA (`_lda`) 轨, 而 char (`_c`) 与 embedding 轨在该次改动中输出字节不变, 二者本就不消费该分词器。因此本族对未登录词与领域新词的鲁棒性来自 char n-gram 天然的子词覆盖 (无需切词即可命中"科技""金融"等字面片段), 而非来自领域词表注入——把 char_wb 与 1506 词注入分词器混为一谈是对本轨计算链的误读。第二步质心: 关键在于质心采用 leave-one-out 口径, 即对银行 i 而言, 其对照的"行业质心"是同年剔除银行 i 自身后其余在样银行向量的均值 c_{-i} = (n·c̄ − v_i)/(n−1) (n 为当年在样银行数, c̄ 为含全部银行的整体均值), 而非含自身的算术平均。之所以排除自身, 是因为若把银行 i 自身也计入质心, 则 cos(v_i, 质心) 会内生地包含约 1/n 量级的机械自相关分量, 且对越与行业正交的银行抬升越多, 从而系统性压缩 centroid_diff 的右尾; 源码 fix(omni-g-strategic-10, 2026-06-11) 专门把原含自身的均值口径改为 leave-one-out, 使之与本模块 N-最近邻路径 (对角线置 NaN 排除自身)、fluidity 路径 (other ≠ bank 排除自身) 的既有惯例对齐, 反机械自相关的 leave-one-out 语义是本测度的承重设计而非可替换细节 (当年在样银行数 n<2 时 leave-one-out 质心无定义, 该银行-年度取 NaN)。第三步距离: centroid_diff_tfidf_c 定义为 v_i 与 leave-one-out 质心 c_{-i} 的余弦距离 1 − cos(v_i, c_{-i})。因 TF-IDF 向量元素非负, 余弦相似度落在 [0,1], 故本轨距离亦被约束在 [0,1], 值越大表示该银行报道语义离行业中心越远、被感知的差异化越强 (此值域口径见 strategic_diff.py 的值域说明: TF-IDF/LDA 轨为非负向量/分布 ∈ [0,1]; 与之相对, 嵌入轨因保留负余弦, 其 centroid 距离落在 [0,2], 本 char TF-IDF 族不涉及该扩展值域)。本家族属"全行业向量法"(以个体文本向量对全行业质心的偏离刻画差异化, 承接 Hoberg & Phillips (2016) 以文本向量距离度量竞争定位的传统) 的 char TF-IDF 实现, 与同一 producer 下的 N-最近邻差异度 (Guzman & Li 2023 构念, strat_diff_n{N} 系列) 是并列而非同一的两种差异化算子: 前者比对"个体 vs 行业质心", 后者比对"个体 vs 若干最近同行", 稳健性配对时不可错配。

【文献定位】
差异化-绩效关系的解释需锚定 Haans (2019): 在同质品类里"与众不同"能带来溢价, 而在本就异质的品类里过度差异反而可能损害合法性, 提示 centroid_diff 作为解释变量时其效应方向依赖行业同质度这一情境调节, 而非单调正向。Miller & Wang (2024) 记录了数字化冲击如何驱动在位者的差异化战略变迁, 与本项目研究银行在金融科技冲击下媒体定位漂移的问题高度同构, 支持把逐年 centroid 距离用作"定位随外生冲击演化"的追踪量。Arts, Cassiman & Hou (2025) 则展示技术差异化如何进入产品市场竞争与并购决策的下游后果, 为把本族用作 P5 (M&A) 等下游结果的前置解释变量提供了文献依据。需强调的是, 三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨道的 centroid 距离混入同一个 over-identified 的 Hansen J 过度识别检验; 同理, char (`_c`) 与 jieba 词级 (`_w`)、TF-IDF 与 LDA/嵌入等不同向量化方法之间也是规格稳健性并排关系。本族依赖第三方媒体报道而非企业自有披露, 且银行截面的在样实体数远小于 Hoberg & Phillips (2016) 用全体上市公司 10-K 构造的 TNIC 数据集 (量级约每年数千家), 银行业本身实体总数有限、逐年真正有金科共现报道的在样银行数更少, 使得每年可用于估计行业质心的截面本就单薄; 加之 leave-one-out 质心剔除自身后分母进一步减一, 质心估计的样本抖动相对更大, 解读时应把它视为媒体感知层面的相对定位信号而非精确的战略披露度量。

## VAR: centroid_diff_tfidf_c

【变体差分】
本列是家族 canonical 无后缀列, 对应 full 轨。full 轨的银行-年度超级文档 = 标题 prepend 后的全文正文 (content_full), 即把每篇报道的标题拼接到正文之前再整体纳入 TF-IDF 向量化, 覆盖该银行当年全部留篇报道的完整文本, 因此它是三轨中信息量最大、覆盖面最宽的定位测度。留篇口径与项目 full-only 门控 (2026-06-29) 一致: 一篇报道是否计入银行-年度语料, 只由 full 轨的 llm_verified_full 判定, ctx/ss 轨是在同一 full 留篇集之上的条件性 (conditional-on-full) 测度轨, 故本 full 列的行宇宙是三轨中的母集。就构念而言, 本列回答的问题是: 当把一家银行全年被报道的所有文本整体投影到 char TF-IDF 空间时, 它离全行业报道话语中心有多远。作为 canonical, 它是本族进入回归的首选主轨, 而 `_ctx` / `_ss` 两列是其规格稳健性并排轨——三者各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。char 级 (`_c`) 相对词级 (`_w`) 的差别在于以字符 n-gram 而非 jieba 切词构造特征, 对未登录词与领域新词更鲁棒, 二者亦互为稳健性而非主次。在解释上, 本列取值越大, 说明该银行当年被报道的整体文本在词汇构成上越偏离全行业的共同话语中心, 对应更强的媒体感知战略差异化; 取值趋近 0 则表示其报道措辞与行业均值高度重合、定位随大流。作为家族里覆盖最全、样本抖动相对最小的一轨, 本列在多数下游规格中承担主结果角色, 而把 `_c` 的 char 与 `_w` 的词级实现、以及 TF-IDF 与 LDA/嵌入等替代向量化方法一并视为环绕它的方法学稳健性梯子, 逐一并排检验主结论是否被特定向量化选择所驱动。

## VAR: centroid_diff_tfidf_c_ctx

【变体差分】
本列是 canonical 的 ctx 轨孪生, 唯一差分维度是构造银行-年度超级文档所用的文本来源: 它消费 content_ctx, 即"标题 + 实体上下文窗口"文本, 只保留围绕目标银行实体邻近窗口的片段而非全文, 从而把 TF-IDF 向量与行业质心的比对聚焦到与该银行直接相关的语境, 削弱与银行无关的背景性叙述对定位测度的稀释。ctx 轨的超级文档拼接严格剔除 *_is_fallback 回退行、且不再单独走 title 通道 (标题已在 prepend 阶段内嵌, 再拼即双标题污染), 确保 char TF-IDF 特征不被重复标题扭曲。ctx 轨的质心 c̄ 亦在 ctx 文本空间内独立重算, 不借用 full 轨的向量或质心, 保证同轨内分子分母口径自洽。语义上本列回答: 仅看与该银行实体贴身的报道片段时, 它的媒体定位离行业中心有多远——相对 full 轨更"聚焦实体"、噪声更低但覆盖更窄。本列与 canonical full 列及 `_ss` 列各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J; 它是 full 主轨之上的首要稳健性轨, 用于检验主结论是否被"全文 vs 实体窗"这一文本切割口径所驱动。在 T=2 的本机开发切片上, ctx 轨可能因样本过薄而退化, 属预期现象, 生产 T=18 语料下方为正常。

## VAR: centroid_diff_tfidf_c_ss

【变体差分】
本列是 canonical 的 ss (same-sentence) 轨孪生, 差分维度同样落在文本来源: 它消费 content_ss, 即"标题 + 银行与金科词同句共现 ±N 句窗"文本 (窗口半径由 config 的 ss_sentence_radius 控制, 默认 1), 是三轨中语境约束最严的一轨, 只纳入银行实体与金融科技词在同一句 (及其小邻域) 共现的片段, 因此它度量的是"当银行被置于金融科技语境中被报道时"的差异化定位, 构念上最贴近本项目银行-金科主题。ss 轨的回退语义严格镜像 ctx: 当某银行当年不存在银行∧金科同句共现时, content_ss 优雅回退为全文 body 且 ss_is_fallback 置 True, 与 ctx 共享同一 n_articles 分母口径; 若 FINTECH_AC 为空则 *_is_fallback 全 True 整体降级。超级文档拼接同样剔除 *_is_fallback 行并禁用 title 通道以避免双标题污染, 质心 c̄ 在 ss 文本空间内独立重算。语义上本列回答: 只看金科语境下的报道片段时, 该银行的媒体定位离行业中心有多远。本列与 full (canonical)、`_ctx` 两列各自 just-identified 并排、互为稳健性、不分主次, 三轨禁混同一 over-identified Hansen J。因 ss 轨语境约束最紧, 在 T=2 开发切片上零方差退化尤为常见, 属预期, 生产规模下恢复正常判别力。就构念定位而言, 本列在三轨中信噪权衡最偏向"高特异性、低覆盖"一端: 它牺牲了大量与银行相关但未落在金科同句窗内的文本, 换取对"银行×金融科技"这一核心研究主题的最贴身刻画, 因而当主结论在 full 主轨成立、并在 ctx 与 ss 两条逐步收窄语境的稳健性轨上保持方向一致时, 可较有力地排除结论被宽泛背景叙述或非金科语境噪声驱动的替代解释。反之, 若 ss 轨与 full 轨系统性背离, 则提示该银行的媒体差异化更多来自金科语境之外的一般性报道, 这一诊断价值正是保留 ss 独立轨的意义所在。

<!-- rendered-citations:begin -->
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Miller, C. D., & Wang, R. D. (2024). Product digitization and differentiation strategy change: Evidence from the book publishing industry. Strategic Management Journal, 45(7), 1241-1272. https://doi.org/10.1002/smj.3586
Guzman, J., & Li, A. (2023). Measuring founding strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
<!-- rendered-citations:end -->
