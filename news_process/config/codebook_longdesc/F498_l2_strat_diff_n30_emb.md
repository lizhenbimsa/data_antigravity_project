---
family_id: F498
columns:
- strat_diff_n30_emb
- strat_diff_n30_emb_ctx
- strat_diff_n30_emb_lg
- strat_diff_n30_emb_lg_ctx
- strat_diff_n30_emb_lg_ss
- strat_diff_n30_emb_ss
unit: 无量纲 (0-2 区间, 余弦距离均值; 1 减余弦相似度)
formula: 'Ŝ_i(bank,year) = 1 - mean(cos_sim(e_i, e_j)) for j in top-N nearest peer BANKS of bank i (within the same year cross-section, ~54-118 banks/year), where e_i is the embedding of bank i''s year-aggregated news document (_aggregate_bank_year_texts); N=30. Bank-year is already the unit of observation — no separate article-level-to-bank-year aggregation step exists.'
producer: pipeline\features\strategic_diff.py (面板标签装配于 pipeline\panel\stata_export.py)
upstream:
- 14_materialize_ctx
- 21_tone_llms
citations:
- doi: 10.1287/mnsc.2022.4369
  type: journal
  authors: Guzman, J., & Li, A.
  year: 2023
  title: Measuring founding strategy
  venue: Management Science
  vol: '69'
  issue: '1'
  pages_or_artno: 101-118
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: Text-based network industries and endogenous product differentiation
  venue: Journal of Political Economy
  vol: '124'
  issue: '5'
  pages_or_artno: 1423-1465
- doi: 10.1002/smj.2978
  type: journal
  authors: Haans, R. F. J.
  year: 2019
  title: What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories
  venue: Strategic Management Journal
  vol: '40'
  issue: '1'
  pages_or_artno: 3-27
- doi: 10.1002/smj.3549
  type: journal
  authors: Su, J., Gao, X., & Tan, J.
  year: 2024
  title: Positioning for optimal distinctiveness; How firms manage competitive and institutional pressures under dynamic and complex environment
  venue: Strategic Management Journal
  vol: '45'
  issue: '2'
  pages_or_artno: 333-361
- doi: 10.1086/715162
  type: journal
  authors: Rodriguez, P. L., & Spirling, A.
  year: 2022
  title: 'Word embeddings: What works, what doesn''t, and how to tell the difference for applied research'
  venue: The Journal of Politics
  vol: '84'
  issue: '1'
  pages_or_artno: 101-115
- doi: 10.18653/v1/D19-1410
  type: wp
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: 'Sentence-BERT: Sentence embeddings using Siamese BERT-networks'
  venue: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing
  pages_or_artno: 3980-3990
- doi: "10.1016/j.jfineco.2025.104007"
  title: "Global Business Networks"
  authors: "Breitung, C., & Müller, S."
  year: 2025
  venue: "Journal of Financial Economics"
  type: "journal"
- doi: "10.1371/journal.pone.0284567"
  title: "Identify novel elements of knowledge with word embedding"
  authors: "Yin, D., Wu, Z., Yokota, K., Matsumoto, K., & Shibayama, S."
  year: 2023
  venue: "PLOS ONE"
  type: "journal"
new_dois:
  - "10.1016/j.jfineco.2025.104007"
  - "10.1371/journal.pone.0284567"
---

## CORE

【构念与来源】
strat_diff_n30_emb 家族测度的是一家银行当年在媒体报道语义空间中, 相对同一年度截面内与其最相近的 N=30 家同业银行的"战略/内容距离"——直觉上, 一家银行当年金融科技报道的语义内容若与最相似的 30 家同业银行高度雷同, 说明该行在媒体叙事层面呈现出"泯然众人"的低区分度; 若显著偏离最相似的同业银行, 则说明该行的媒体呈现具有更高的文本独特性 (textual distinctiveness)。分析单元是银行-年份, 不是单篇文章: 计算前先把同一 (银行, 年份) 下的全部报道文本拼接聚合为一份"企业-年"文档, 最近邻检索与均值距离均在"银行-年份文档"之间两两进行, 而不是在文章之间进行。这一构念直接承袭文本战略计量学中"以文本相似度代理战略/产品定位相似度"的传统, 其经典范式是 Hoberg 与 Phillips 基于 10-K 产品描述文本余弦相似度构造的 TNIC (text-based network industry classification) 及其衍生的产品市场差异化测度 (Hoberg & Phillips, 2016)——他们证明企业间产品文本的成对余弦相似度可以内生地划分产业边界并度量产品差异化程度, 优于静态 SIC/NAICS 行业代码, 而 TNIC 本身的分析单元正是"企业-年度"聚合文档 (10-K 年报), 并非企业内部逐篇披露段落。本家族将同一逻辑从企业自述文本 (10-K) 迁移到第三方媒体报道文本, 用银行年度聚合报道的句向量嵌入代替产品描述向量, 用"银行-年份最近邻均值距离"代替"成对相似度矩阵", 是该范式在中文金融科技新闻语料上的应用变体。
更直接的方法学血缘是 Guzman 与 Li (2023) 提出的"测量创业战略"框架: 他们用文本嵌入的最近邻距离衡量新创企业商业计划书相对于同行的战略独特性, 距离越大代表该企业选择了越"拥挤度低"的战略定位; 本测度将同一"最近邻距离即战略区分度"的核心逻辑套用到银行金融科技报道语料上——不再是企业自述商业计划, 而是媒体对银行金融科技活动的第三方叙事聚合成的年度文档, 距离度量的对象是"某银行的年度报道画像与其语义最近的 N 家同业银行年度报道画像"。因此 strat_diff_n30_emb 更准确的解读是"媒体叙事层面的银行间战略新颖度/差异化程度", 而非直接的产品市场战略测度; 它捕捉的是银行金融科技报道整体画像在同业语义空间里被淹没在"标准叙事模板"中的程度——数值越低, 说明该行全年报道内容与市场上大量同质化的同业报道 (例如例行的"XX银行上线XX金融科技产品"套话式报道) 高度雷同; 数值越高, 说明该行的金融科技报道叙事相对同业更为独特、罕见或前沿。
该家族在 codebook 分类体系中标记为 l2 (第二层派生指标, 由句向量嵌入进一步计算得到银行间文本距离), kind 标注为 "inferred:战略差异|Stage 25"——即该指标不是原始情感/属性打分, 而是在嵌入向量已知的前提下推断出的结构性文本距离测度。⚠ 口径澄清: 本家族的嵌入调用并不复用 25_article_sbert 阶段产出的逐文章句向量; producer (pipeline/features/strategic_diff.py) 在把同 (银行,年份) 全部报道聚合为单一年度文档后, 独立调用统一嵌入引擎 (embedding_engine._eng.embed_texts) 对聚合文档重新编码, 与 stage 25 的逐文章嵌入产出互不读取、互不复用; 25_article_sbert 服务的是 stage 26 语义 staleness 测度这一条完全独立的下游, 与本家族无数据依赖关系。本家族真正依赖的上游是 14_materialize_ctx (提供 content_full/content_ctx/content_ss 三轨聚合原料文本) 与 21_tone_llms (提供 full-only 留篇门控标志 llm_verified_full, 决定哪些文章可进入年度聚合文档)。

【方法学与计算】
计算流程分三步, 全部在 pipeline/features/strategic_diff.py 一个模块内完成, 分析单元自始至终是"银行-年份", 从不产出文章级中间分数。第一步 (_aggregate_bank_year_texts): 对每个 (target_bank, year) 组合, 把该行宇宙内 (full-only 留篇门控确定, 即仅 llm_verified_full=True 的文章参与) 的全部报道文本 (标题+正文, full/ctx/ss 三轨各自独立取材) 拼接为单一"企业-年"文档, 同 (bank,year) 内逐字重复全文先去重, 使一年内几十甚至上百篇报道压缩为一份年度文本画像。第二步 (_build_embedding_sim_matrix→_embed_texts_with_chunk_pooling): 对同一年度截面内全部银行 (通常约 54~118 家, 随年份样本覆盖而变) 的年度聚合文档逐一调用嵌入引擎编码为定长稠密向量, 主轨用 Qwen/Qwen3-Embedding-8B (硅基流动 API, 4096 维), 对偶 co-primary 轨用 text-embedding-3-large (OpenAI/yunwu, 3072 维, 列名带 `_lg` 中缀), 超长文档走 token 级分段+均值池化。第三步 (_compute_nn_scores): 对该年度截面内每家银行 i, 计算其与同年内所有其余银行 j 的嵌入余弦相似度 cos_sim(e_i, e_j), 取相似度最高的 N=30 家银行作为银行 i 的"最近邻同业集合", 再对这 30 个相似度值取均值, 用 1 减去该均值得到 Ŝ_i = strat_diff_n30 = 1 - mean(cos_sim_top30_banks); 该值本身已是 bank-year 层面的观测, 无需再按银行-年份分组聚合这一额外步骤。该值落在大致 [0, 2] 区间 (余弦相似度理论范围 [-1, 1], 1 减之后落在 [0, 2]), 但因新闻文本嵌入的相似度经验分布高度集中在正值区间, 实际观测值通常远小于该理论上界, 越接近 0 表示该行报道画像与最相近的 30 家同业高度雷同, 越大表示越独特。若该年度截面内可比银行数不足 N+1 家 (|peers| < N), 该 (bank, year) 的 strat_diff_n30 优雅降级为 NaN, 而非静默用更小的 k 顶替 (避免制造虚假的 N 敏感性稳健)。
top-k N 是一个可调超参数——邻域窗口选得太窄 (N 很小, 如 N=5) 对个别偶然高相似的同业过于敏感, 方差大; 选得太宽 (N 很大, 如 N=50, 且同年可比银行池通常仅 ~54~118 家) 则把语义上并不真正相关的同业也纳入均值, 稀释了区分信号、向"当年全体同业平均相似度"收敛甚至趋同于 centroid 构念。producer 源码实际构造的完整 N 梯子是 N∈{3,4,5,6,7}∪{10,20,30,40,50} 共十档 (基准 N=5 加稳健档 3/4/6/7, 再加大邻域档 10/20/30/40/50), 但只有 N∈{5,10,20,30,40,50} 六档被落地为独立 codebook 列族 (对应家族 strat_diff_full/strat_diff_n5_emb 至 strat_diff_n50_emb 系列); N∈{3,4,6,7} 四档存在于源码常量与面板列中但未各自成族编目, 使用时应留意源码侧的敏感性覆盖范围比本 codebook 六档列族更宽。本家族对应 N=30 这一档, 是六档列族中位偏上的一个稳健档位——邻域既不至于因样本量过小而噪声过大, 也不至于因样本量过大而把区分信号平均掉。⚠ 铁律: N 取值梯子内各档 (n5/n10/n20/n30/n40/n50, 含源码内未独立编目的 n3/n4/n6/n7) 各自 just-identified 并排, 互为稳健性、不分主次, 不存在哪一档是"更优"或"官方"取值, 报告结果时应展示跨 N 的稳健性而非单挑一档, 严禁把多档 N 混入同一 over-identified Hansen J 式的联合矩估计。
本家族同时承载三条正交的稳健性维度, 三者两两独立、互不纠缠: 其一是文本轨道 full/ctx/ss——full 轨用标题+全文正文编码, ctx 轨用标题+银行/金融科技实体窗口文本编码, ss 轨用标题+银行∧金融科技同句 (±N 句窗) 文本编码; 三轨各自独立计算最近邻集合与均值距离, 各自 just-identified 并排、互为稳健性不分主次, 三轨严禁混入同一 over-identified Hansen J。其二是嵌入引擎 co-primary 双轨——canonical 无后缀轨用 Qwen/Qwen3-Embedding-8B (4096 维, 硅基流动), `_lg` 中缀轨用 text-embedding-3-large (3072 维, OpenAI/yunwu); 两条嵌入轨严格 parity (列名双射 both-or-neither, 任一嵌入 API 调用失败则同族两列同置缺失, 不产生单边孤儿列), 二者同为主测度、互为稳健性、严格 just-identified 并排, 同样禁止混入同一 Hansen J。其三是前述 top-k N 梯子。三条维度组合穷举即产生本家族及其姊妹家族的全部列名 (轨道后缀 × 嵌入后缀 × N 值), strat_diff_n30_emb 系列六列正是"N=30 固定, 遍历三轨 × 两嵌入引擎"的六个格点。
关于留篇门控口径: 参与最近邻计算的文章全集口径是 full-only——stage 21 情感 LLM 只依据 full 轨 llm_verified_full 标志判定"是否为一篇有效的银行-金融科技报道", ctx/ss 轨的最近邻计算复用同一行宇宙 (full 留篇集的子集), 而非各轨独立扩样, 这与 CLAUDE.md 中"留篇门控 = full-only" (2026-06-29 切换) 的口径完全一致。ss 轨的回退语义镜像 ctx 轨: 若某篇报道找不到银行与金融科技词在同一句 (±N 句窗) 共现, 则该篇的 content_ss 退化为全文 body (与 content_full 相同), 并置 ss_is_fallback=True, 在此情形下该篇的 ss 轨嵌入与 full 轨高度相关, 是设计内的优雅降级而非缺陷。

【文献定位】
本家族最直接的方法学出处是 Guzman 与 Li (2023) 发表于顶刊 Management Science 的《Measuring Founding Strategy》, 该文首次系统性地用文本嵌入空间中的最近邻距离测量企业战略的差异化/独特性程度, 并证明这一文本距离测度能够预测企业存续与融资结果, 是本仓库 strat_diff_n{N}_emb 全系列命名与构造逻辑的直接出处 (见 producer 源码注释 "strat_diff_n{N} 最近邻距离出处")。第二支重要文献是 Hoberg 与 Phillips (2016) 发表于顶刊 Journal of Political Economy 的《Text-Based Network Industries and Endogenous Product Differentiation》, 该文奠定了"用文本余弦相似度矩阵内生刻画产品/战略差异化边界"的方法论范式, 是本测度将"最近邻距离"应用于媒体文本场景的更早期理论根基, 也是 TNIC 文本产业分类的方法起点。第三支是组织理论中"最优区分度" (optimal distinctiveness) 文献: Haans (2019) 发表于顶刊 Strategic Management Journal 的研究指出, 企业在同质化程度不同的品类中, 差异化对绩效的边际效应并非线性单调, 而是存在"过犹不及"的非线性关系——这一发现提示在使用 strat_diff 类测度做后续回归分析时, 应审慎考虑其与绩效结果的非线性/倒 U 型关系, 而非默认"差异化越高越好"的单调假设。Su, Gao 与 Tan (2024, Strategic Management Journal) 进一步在动态复杂环境下讨论企业如何在竞争压力与制度压力之间为最优区分度定位, 为解释银行在金融科技报道中的差异化选择提供了制度理论视角。文本嵌入模型本身的方法学有效性参考 Reimers 与 Gurevych (2019) 的 Sentence-BERT 工作 (句向量嵌入的标准范式) 以及 Rodriguez 与 Spirling (2022) 关于词/句嵌入在应用社会科学研究中"何时可靠、何时不可靠"的方法论评估, 二者共同支撑了本仓库选用句向量余弦相似度而非词袋/TF-IDF 作为最近邻距离底层度量的合理性。此外, Breitung 与 Müller (2025, Journal of Financial Economics) 该文用文本嵌入构造全球企业相似度网络, 延续 Hoberg 与 Phillips 文本相似度范式并扩展到跨国、嵌入向量层面, 与本家族用银行年度报道嵌入构造同业最近邻距离的方法学直接呼应。Yin、Wu、Yokota、Matsumoto 与 Shibayama (2023, PLOS ONE) 该文用词嵌入空间中的新颖元素识别衡量科学文献的新颖度, 为本家族以嵌入最近邻距离度量银行报道叙事独特性/新颖度提供了跨领域的方法学参照。

## VAR: strat_diff_n30_emb

【变体差分】
本列是家族 canonical 基准格点: 文本轨道 = full (标题+全文正文), 嵌入引擎 = 主轨 Qwen/Qwen3-Embedding-8B (硅基流动, 4096 维), 邻域宽度 N = 30。计算时先把每家银行当年通过 full-only 留篇门控的全部报道拼接为一份年度聚合文档, 再在同一年度截面的全体银行 (通常约 54~118 家) 中检索该行年度文档余弦相似度最高的 30 家同业银行年度文档, 取 1 减这 30 个相似度值的均值作为该行当年的战略差异分——该值本身即为 bank-year 观测, 不涉及"文章级打分后再聚合"这一并不存在的步骤。full 轨的输入文本是标题拼接全文正文, 未经任何实体窗口或同句共现的裁剪, 因此该列反映的是"银行年度报道整体画像"相对于同年最相近 30 家同业的语义距离, 既包含围绕银行金融科技活动的核心叙事, 也包含背景介绍、行业综述等外围段落, 距离信号相对更"粗", 但样本覆盖面最完整、不受任何窗口回退语义的影响。该列是本文若报告单一 strat_diff_n30 数值时的默认参照点, 但按照本家族"梯子内各档并排、互为稳健性"的铁律, 它并不因此获得优先解释地位, 使用时应与 ctx/ss 轨及 `_lg` 嵌入轨对照报告, 也应与 N∈{5,10,20,40,50} 其余档位对照报告以展示结果对邻域宽度选择的稳健性, 严禁在同一 over-identified 联合估计中把该列与其余五个姊妹格点同时作为解释变量混入。

## VAR: strat_diff_n30_emb_ctx

【变体差分】
本列与 canonical 列的唯一差分维度是文本轨道: 由 full 换为 ctx (标题+银行/金融科技实体窗口文本), 嵌入引擎与 N=30 邻域宽度保持不变 (仍为 Qwen/Qwen3-Embedding-8B 主轨)。ctx 轨的年度聚合文档由更聚焦于实体上下文窗口的文本拼接而成 (仍是先按银行-年份聚合再在同年银行截面内做最近邻检索), 相比 full 轨排除了报道中与银行、金融科技活动无直接关联的段落 (如宏观背景、行业综述性文字), 因此该列度量的差异化更贴近"围绕银行-金融科技实体本身的年度叙事独特性", 而非整篇文章通篇内容聚合后的独特性。ctx 轨的文本在 stage 14 物化时以 prepend_title 方式拼接标题与实体窗口片段, 与 full/ss 两轨共享同一句向量嵌入引擎与同一套"先聚合银行-年文档、再在银行截面内求最近邻"的计算流程 (仅输入文本不同), 因此三轨之间的差异纯粹来自文本裁剪范围, 不掺杂模型或超参数差异。ctx 与 full、ss 三轨严格并排、互为稳健性不分主次, 禁止将三轨同时纳入同一 over-identified 联合估计。该列所依赖的行宇宙仍是 full-only 留篇门控确定的文章集合 (conditional-on-full), 即只有在 full 轨被判定为有效银行金融科技报道的文章才参与 ctx 轨年度聚合文档的构建与后续最近邻计算, 与主线口径完全一致, 不因切换文本轨道而扩大或缩小样本行宇宙。

## VAR: strat_diff_n30_emb_lg

【变体差分】
本列与 canonical 列的唯一差分维度是嵌入引擎: 由主轨 Qwen/Qwen3-Embedding-8B (4096 维, 硅基流动) 换为跨厂商 co-primary 对偶轨 text-embedding-3-large (3072 维, OpenAI/yunwu), 文本轨道仍为 full, N 仍为 30, 分析单元仍是"银行-年份聚合文档"而非单篇文章。两条嵌入引擎产出的向量空间维度不同、来自不同厂商的训练语料与目标函数, 最近邻检索与均值距离的计算逻辑完全相同 (均在同年银行截面内两两比较年度聚合文档), 唯一差异是底层句向量的来源模型, 二者严格 parity: 若某银行-年份的年度聚合文档在任一引擎调用失败, 则该 (银行,年份) 在两条嵌入轨对应的 strat_diff 全族列同步置缺失, 不产生单边孤儿列, 这一 both-or-neither 守卫由 producer 侧的 `_MAIN_ANCHOR_KEYS`/`_lg` 派生循环保证。`_lg` 轨与无后缀主轨同为 co-primary 主测度、互为稳健性、不分主次, 二者各自 just-identified 并排, 严禁混入同一 over-identified Hansen J 联合矩估计。该列用于验证"银行媒体报道战略差异化"这一构念的结论是否对具体嵌入模型的选择保持稳健, 而非检验主轨的"正确性"——两条轨严格对等, 任何一方都不天然优先于另一方, 结果解读应报告二者是否给出方向一致、显著性相近的结论。由于两家厂商模型的训练语料、分词与向量维度均不同, 二者构造出的语义空间几何结构存在系统性差异, 最近邻集合的具体成员 (即某银行在两条轨下"最相似的 30 家同业"名单) 也可能不完全重合, 但若"银行报道叙事独特性"这一构念是真实且稳健的, 则两条轨的战略差异分在银行-年份层面的排序应保持大致一致; 若二者出现方向性背离, 应优先怀疑测度对嵌入模型选择的敏感性而非急于否定构念本身。

## VAR: strat_diff_n30_emb_lg_ctx

【变体差分】
本列同时叠加两个差分维度: 嵌入引擎换为 `_lg` co-primary 轨 (text-embedding-3-large), 文本轨道换为 ctx (标题+实体窗口), N 邻域宽度仍为 30。它是"跨厂商嵌入稳健性"与"文本轨道稳健性"两条正交维度的交叉格点, 用于同时检验"围绕银行-金融科技实体的叙事独特性"这一构念在不同嵌入模型下是否给出一致的排序结论。三轨 (full/ctx/ss) 与两嵌入引擎 (主轨/_lg) 两个维度彼此正交、互不纠缠——切换文本轨道不改变嵌入模型, 切换嵌入模型也不改变文本裁剪范围, 二者可以自由组合而不产生耦合偏误。该列作为二者交叉产物同样严格遵守两条各自的 just-identified 并排铁律, 不得与其余格点混入同一 Hansen J 联合估计; 行宇宙 (银行-年份格点集合) 同样是 full-only 门控下的 conditional-on-full 子集, 即仅覆盖 full 轨判定为有效留篇的报道所构成的年度聚合文档, ctx 轨自身不额外扩样也不因换用 `_lg` 嵌入而改变样本边界, 与前述 both-or-neither 缺失值同步守卫共同保证该列与其余五个格点在样本口径上完全可比。在实证使用上, 该列常与 canonical 主轨的 ctx 格点 (strat_diff_n30_emb_ctx) 一并报告, 用以说明"围绕银行金融科技实体的叙事独特性"这一结论既不依赖具体嵌入厂商、也不依赖是否纳入实体窗口以外的背景文字, 是本家族六个格点中稳健性含量最高、但样本行宇宙与其余格点完全一致的一档。

## VAR: strat_diff_n30_emb_lg_ss

【变体差分】
本列的三个差分维度组合为: 嵌入引擎 = `_lg` co-primary 轨 (text-embedding-3-large), 文本轨道 = ss (标题+银行∧金融科技同句 ±N 句窗), N 邻域宽度 = 30。ss 轨的构造判据比 ctx 轨更严格——要求银行与金融科技词在同一句 (或按 `config/filtering.yaml::context_window.ss_sentence_radius` 指定半径的邻近句) 内共现才纳入 ss 轨文本, 因此 ss 轨反映的是最贴近"银行与金融科技活动直接被同句提及"这一最窄语境下的叙事独特性, 相较 ctx 轨的实体窗口, ss 轨进一步剔除了同一实体窗口内但并非同句提及的过渡性描述文字。若某篇文章不存在这种同句共现, 则该篇 content_ss 回退为全文 body (镜像 ctx 轨回退语义, 共享同一 n_articles 分母), 对应 ss_is_fallback 标志置真, 此时该篇在纳入年度聚合文档后, ss 轨与 full 轨的年度文档嵌入高度相关属预期设计而非异常, 不应误判为该 (银行,年份) 最近邻检索失效。该列作为"最严格判据 × 跨厂商嵌入"交叉格点, 与其余格点同样严格并排、互为稳健性, 不参与同一 Hansen J, 使用时应同时对照 canonical 主轨的 ss 格点与 ctx/full 两条相邻轨道以判断结论对判据严格程度和嵌入模型的双重稳健性。该列是本家族六格点中文本裁剪最窄、嵌入引擎又切换为跨厂商对偶轨的极端组合, 若该格点与其余五个格点在银行-年份排序上表现出高度一致的方向性, 则可视为"叙事独特性"构念在最苛刻的双重稳健性检验下依然成立的有力证据; 反之若仅在该格点出现异常, 应优先排查是否为同句共现样本量过小导致的统计噪声, 而非直接归因于构念失效。

## VAR: strat_diff_n30_emb_ss

【变体差分】
本列与 canonical 列的差分维度是文本轨道: 由 full 换为 ss (标题+银行∧金融科技同句 ±N 句窗), 嵌入引擎仍为主轨 Qwen/Qwen3-Embedding-8B, N 仍为 30。相较 ctx 轨, ss 轨的判据更为严苛 (要求同句而非仅实体窗口共现), 因此该列捕捉的是报道中银行与金融科技被直接绑定叙述的那部分文本片段相对于同期语料最近邻的语义独特性, 是三轨中"最贴近具体共现语境"的一档, 也是对无关背景段落过滤最彻底的一档, 理论上能最大程度剥离与银行金融科技活动无关的套话式文字对最近邻检索的干扰。ss 轨严格遵循镜像 ctx 的回退语义: 无同句共现时退化为全文并标记 ss_is_fallback=True, 共享同一 n_articles 分母, 不产生额外样本损耗, 也不因回退而人为压低或抬高该篇的战略差异分。该列与 full/ctx 轨、以及与 `_lg` 嵌入轨的对应格点各自 just-identified 并排, 互为稳健性不分主次, 严禁混入同一 over-identified Hansen J 联合估计; 与 canonical 列相比, 二者共享同一嵌入模型与同一 N=30 邻域宽度, 唯一差异是输入文本的裁剪范围, 是判断"叙事独特性结论是否依赖于文本窗口选择"的关键对照格点。该列还应与 `_lg` 嵌入轨对应的 ss 格点 (strat_diff_n30_emb_lg_ss) 联合报告, 以区分文本窗口效应与嵌入模型效应两条正交来源; 若二者在同一判据下方向一致, 则说明所观测到的战略差异化模式源自银行报道内容本身的语义结构, 而非某一具体嵌入模型的偶然产物。

<!-- rendered-citations:begin -->
Guzman, J., & Li, A. (2023). Measuring founding strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Su, J., Gao, X., & Tan, J. (2024). Positioning for optimal distinctiveness; How firms manage competitive and institutional pressures under dynamic and complex environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Rodriguez, P. L., & Spirling, A. (2022). Word embeddings: What works, what doesn't, and how to tell the difference for applied research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing No. 3980-3990 [Working Paper]. https://doi.org/10.18653/v1/D19-1410
Breitung, C., & Müller, S. (2025). Global Business Networks. Journal of Financial Economics. https://doi.org/10.1016/j.jfineco.2025.104007
Yin, D., Wu, Z., Yokota, K., Matsumoto, K., & Shibayama, S. (2023). Identify novel elements of knowledge with word embedding. PLOS ONE. https://doi.org/10.1371/journal.pone.0284567
<!-- rendered-citations:end -->
