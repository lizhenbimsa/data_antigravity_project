---
family_id: F494
columns:
- strat_diff_n10_emb
- strat_diff_n10_emb_ctx
- strat_diff_n10_emb_lg
- strat_diff_n10_emb_lg_ctx
- strat_diff_n10_emb_lg_ss
- strat_diff_n10_emb_ss
unit: 无量纲得分 (0~2 区间的余弦距离均值, 1 减余弦相似度)
formula: 'strat_diff_n{N}_emb_i = 1 - mean_{j in kNN10(i)} cos(v_i, v_j); 先将每家银行当年同轨全部留篇文章嵌入拼接聚合为一条银行-年度"年度总结"向量 v_i (_aggregate_bank_year_texts), 再在同年度同轨全部银行的年度向量之间构建 bank×bank 余弦相似度矩阵, 为银行 i 取同年度其余银行中相似度最高的 top-10 家(不含自身)作为最近邻同行集合 kNN10(i), 该行最终得分为其年度向量与这 10 家最近邻同行向量余弦相似度均值的 1 减; 单元粒度是银行-年度, 并非文章级最近邻聚合'
producer: pipeline\features\strategic_diff.py (数值计算层, 由 25_article_sbert 产出的 emb_full/emb_ctx/emb_ss 与 _lg 孪生嵌入聚合为银行-年度向量后驱动) + pipeline\panel\stata_export.py (标签装配层)
upstream:
- 25_article_sbert
citations:
- {doi: "10.1287/mnsc.2022.4369", type: journal, authors: "Guzman, J., & Li, A.", year: 2023, title: "Measuring Founding Strategy", venue: "Management Science", vol: "69", issue: "1", pages_or_artno: "101-118"}
- {doi: "10.1086/688176", type: journal, authors: "Hoberg, G., & Phillips, G.", year: 2016, title: "Text-Based Network Industries and Endogenous Product Differentiation", venue: "Journal of Political Economy", vol: "124", issue: "5", pages_or_artno: "1423-1465"}
- {doi: "10.1002/smj.2978", type: journal, authors: "Haans, R. F. J.", year: 2019, title: "What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories", venue: "Strategic Management Journal", vol: "40", issue: "1", pages_or_artno: "3-27"}
- {doi: "10.1002/smj.3549", type: journal, authors: "Su, J., Gao, X., & Tan, J.", year: 2024, title: "Positioning for Optimal Distinctiveness: How Firms Manage Competitive and Institutional Pressures under Dynamic and Complex Environment", venue: "Strategic Management Journal", vol: "45", issue: "2", pages_or_artno: "333-361"}
- {doi: "10.1002/smj.3687", type: journal, authors: "Arts, S., Cassiman, B., & Hou, J.", year: 2025, title: "Technology Differentiation, Product Market Rivalry, and M&A Transactions", venue: "Strategic Management Journal", vol: "46", issue: "4", pages_or_artno: "837-862"}
- {doi: "10.1145/3589335.3651526", type: journal, authors: "Steck, H., Ekanadham, C., & Kallus, N.", year: 2024, title: "Is Cosine-Similarity of Embeddings Really about Similarity?", venue: "Companion Proceedings of the ACM Web Conference 2024", pages_or_artno: "887-890"}
new_dois: []
---

## CORE

【构念与来源】
strat_diff_n10_emb 家族测度的是"该银行当年报道所描绘的经营策略, 与同期同轨嵌入空间中其余银行报道相比有多与众不同"——一个文本层面的战略距离(strategic distinctiveness)指标。构念直接承袭 Guzman & Li (2023, Management Science)"用文本向量间的距离刻画创业策略独特性"的做法, 并把它从创业公司描述迁移到银行金融科技报道语境: 若一家银行当年被报道的金融科技相关内容, 在语义嵌入空间里显著偏离同业主流叙事(即与最近邻文章的余弦相似度低), 该行当年即被判定为策略差异化程度更高; 反之若报道内容与同业高度雷同(套话化、跟风式报道扎堆), 差异化得分趋近于零。这一构念与 Hoberg & Phillips (2016, Journal of Political Economy) 经典的文本相似度产业分类思路同源——二者都用"文本向量的成对相似度"代理"经济主体在特征/策略空间中的相对位置", 但 Hoberg & Phillips 面向产品市场竞争关系(TNIC 产业分类), 本测度面向单一银行跨年度的策略叙事独特性, 是同一方法学谱系在不同应用层面的延伸。战略管理文献(Haans 2019; Su, Gao & Tan 2024; Arts, Cassiman & Hou 2025, 均 Strategic Management Journal)进一步表明"差异化"本身是一把双刃剑: 适度独特可带来最优区分度(optimal distinctiveness)红利, 过度偏离同业常规又可能触发合法性质疑或市场认知成本, 因此该测度定位为一个连续的描述性构念, 不预设其对经营绩效的方向性影响, 供后续实证检验中介/调节效应。

【方法学与计算】
计算分两层, 单元粒度是银行-年度而非文章。数值层由 pipeline\features\strategic_diff.py 消费 25_article_sbert 产出的文章级嵌入向量(每篇文章一条 emb_full/emb_ctx/emb_ss 及其 _lg 孪生), 第一步用 _aggregate_bank_year_texts 把每家银行在同一(年度, 轨道)下全部留篇文章的文本/向量聚合拼接为一条"年度总结"表示, 即该行当年报道叙事的一个综合代理, 而非逐篇保留; 第二步在同一年度、同一轨道下, 对全部银行的年度向量构建 bank×bank 余弦相似度矩阵(_build_embedding_sim_matrix), 为银行 i 在同年度其余银行(而非其余文章)中寻找相似度最高的 top-10 家最近邻同行(k=10, 不含自身), 计算银行 i 的年度向量与这 10 家最近邻同行向量的余弦相似度均值, 再用 1 减去该均值得到距离分 strat_diff_n10_emb, 距离越大代表该行当年的报道叙事在同业年度向量空间中越孤立、越不同于其余银行的主流叙事。数值范围理论上落在 [0, 2](余弦相似度 ∈ [-1, 1]), 实务上因新闻文本嵌入普遍呈正相关簇集, 绝大多数观测落在 [0, 1] 区间。标签装配层 pipeline\panel\stata_export.py 只负责给这批列贴 Stata 变量标签(HEURISTIC_LABELS 字典), 不参与数值计算; 6 个后缀的标签均带统一的"(co-primary: Qwen/Qwen3-Embedding-8B)"或其 _lg 替换标注, 严禁使用"robust/robustness check"措辞——因为两条嵌入轨道是对等互证关系而非主辅关系。本列名中的 n10 是 top-k 最近邻同行数梯子的一档: 源码将 N=5 标注为与 Guzman & Li (2023) 原文设计对齐的基准值, N∈{3,4,6,7}∪{10,20,30,40,50} 均为敏感性检验档位, 本列所在的 N=10 属敏感性梯子而非原始设计对照锚点; 生产口径同时物化多档 N, 彼此互为稳健性并排比较, 不存在某一大 N 值优先取代 N=5 基准的排序。N 越大, 最近邻同行池越宽, 距离分对局部离群银行的敏感度越低、越接近"该行报道与全行业年度平均水准"的偏离度; N 越小则越贴近"最相似的一小撮同业"的局部差异化程度, 二者刻画的是同一构念在不同邻域尺度下的表现, 互为稳健性检验, 不分主次。

【文献定位】
本测度的方法学谱系可追溯两条主线。其一是文本相似度度量经济主体相对位置的传统, 由 Hoberg & Phillips (2016) 的产业文本网络分类奠基, 用词袋/TF-IDF 余弦相似度捕捉产品市场层面的可替代性; 本测度将同一"相似度矩阵—最近邻距离"框架应用到银行金融科技报道叙事上, 但改用稠密语义嵌入(dense embedding)而非稀疏词袋表示。其二是嵌入空间中"最近邻距离代理独特性"的直接方法论原型, 由 Guzman & Li (2023, Management Science)在测量创业策略时确立——他们用创业公司自我描述文本嵌入向量距最近邻的距离衡量策略新颖度, 并证明其与后续融资/存活结果相关; strat_diff_n{N}_emb 家族在计算逻辑上直接对齐这一设计(仅将"公司自述"换成"银行被报道内容", "策略新颖度"换成"报道叙事差异化"), 是同一测度范式在中国银行业金融科技情境下的复刻与延伸。战略管理学文献(Haans 2019; Su et al. 2024; Arts et al. 2025)提供了"最优区分度"理论背景, 说明差异化得分本身并非单调"越高越好", 为后续论文在使用该测度做回归时提供理论锚点(建议同时检验线性与二次项设定)。此外, Steck, Ekanadham & Kallus (2024) 就"余弦相似度是否真正度量语义相似性"给出方法学警示, 指出学习到的嵌入空间中余弦相似度可能受向量范数、训练目标等因素扭曲, 因此本测度定位为构念的一种可操作化近似, 而非无争议的黄金标准; 这也是本仓库坚持 Qwen3-Embedding-8B 与 text-embedding-3-large 两条 co-primary 嵌入轨道并行、互相校验的方法学动机之一, 而非仅为覆盖厂商风险。

## VAR: strat_diff_n10_emb

【变体差分】
本列是 strat_diff_n10_emb 家族在 full 轨、Qwen3-Embedding-8B 主嵌入模型、N=10 最近邻同行梯子下的裸名基准列(无 _full 后缀, 遵循本仓库 n5_emb/sim_max_emb/centroid_diff_emb 系列的 full 轨命名惯例)。计算输入是 25_article_sbert 阶段对 content_full(标题+全文正文)编码得到的 emb_full 向量; 留篇门控遵循 full-only 口径(2026-06-29 起生效)——即某篇文章是否计入其所属银行当年的策略叙事样本, 只看 llm_verified_full 是否为真, 与 ctx/ss 轨道无关。留篇之后, _aggregate_bank_year_texts 把该银行当年全部留篇文章的 emb_full 聚合为一条银行-年度向量, 再在同年度全部银行的年度向量之间取 top-10 最近邻同行、求相似度均值再取 1 减, 得到本列的银行-年度距离分; 单元粒度自始至终是"银行-年度", 并非逐篇文章距离分的均值汇总。该列与家族内 _ctx / _ss 两个后缀互为稳健性并排, 与 _lg 系列互为 co-primary 并排, 二者均不构成"更优先"的主轨——本列只是六个变体中的一个基准锚点, 三轨与两嵌入模型共八种组合(N10 层面为 3 轨 × 2 引擎 = 6 列)在识别策略上必须各自 just-identified 单独进入回归, 严禁在同一 over-identified 的 Hansen J 检验里把不同轨道或不同嵌入引擎的列混合当作多重工具变量使用。使用建议: 若研究问题只需一个"稳态基准"报告列, 本列可作为 full 轨主引擎的默认参照; 但需明确 N=10 属敏感性梯子档位, 源码内与 Guzman & Li (2023) 原始设计对齐的基准值是 N=5(strat_diff_n5_emb, 不在本家族之内), 本列与 N∈{20,30,40,50} 各档共享同一 full 轨 + 主引擎设定, 互为最近邻数敏感性梯子上的并排档位, 不互为优先级关系。

## VAR: strat_diff_n10_emb_ctx

【变体差分】
本列与 canonical 基准列的差分维度是文本轨道: 输入嵌入为 emb_ctx, 即 25_article_sbert 对 content_ctx(标题+实体窗口文本, 由 stage 14 ctx_materializer 物化)编码得到的向量, 而非全文正文。ctx 轨道聚焦银行与金融科技实体附近的局部语境, 相较 full 轨道去除了与银行金融科技叙事无关的正文段落噪声, 理论上能让"策略差异化"信号更聚焦于实体相关表述本身、减少长文噪声段落对最近邻距离的稀释。留篇门控仍是 full-only(该文章是否计入样本由 llm_verified_full 判定), ctx 只影响嵌入向量的文本来源, 不影响样本行进入与否; 换言之 full 轨与 ctx 轨面对的是完全相同的文章行集合, 差异纯粹来自"编码哪一段文本"这一测量选择, 这正是本仓库把 ctx 定位为"conditional-on-full"稳健测度轨而非独立样本口径的原因。本列与 full 轨、ss 轨的三份是互为稳健性、不分主次的并排关系, 禁止混入同一 over-identified Hansen J 检验。嵌入模型仍是 Qwen3-Embedding-8B(co-primary 主轨), 与本列命名对应的 _lg 孪生列 strat_diff_n10_emb_lg_ctx 是同一文本轨道下的跨厂商对等复现, 二者互证不分主次; N=10 近邻梯子在此轨道上与 N∈{20,30,40,50} 各档同样构成敏感性并排组。相较 full 轨样本更容易受实体识别边界效应影响: 若某银行当年多数留篇文章的实体窗口截取过窄, ctx 文本可能只剩零星词汇, 聚合出的银行-年度 ctx 向量可能在同年度同行相似度矩阵中偏离主流簇集, 造成该行距离分虚高, 这也是本仓库将 ctx 定位为"稳健性核验轨"而非替代 full 轨的原因之一——任何仅在 ctx 轨显著、full 轨不显著的结果都应审慎解读为测量伪影而非真实效应。

## VAR: strat_diff_n10_emb_lg

【变体差分】
本列与 canonical 基准列的差分维度是嵌入引擎: 底层向量来自 text-embedding-3-large(OpenAI/OpenLux 端点, 3072 维), 而非 Qwen3-Embedding-8B(硅基流动端点, 4096 维)。两条嵌入轨道是本仓库自 v3.15.0 起确立的 co-primary 双轨架构——彼此互为主测度、互为稳健性检验、严格 parity(列名双射, both-or-neither 缺失规则: 任一引擎 embed 失败为 None, 则该家族两条轨道同族列同置缺失, 不产生单边孤儿观测), 而非"主轨/稳健轨"的主次关系。这一 both-or-neither 守卫在本列上意味着: 若某银行-年度单元下有文章因 Qwen 端点限流或超时导致 embed 失败进而无法聚合出该行的年度向量, strat_diff_n10_emb 与 strat_diff_n10_emb_lg 会同步置缺失, 不会出现"主引擎有值、_lg 引擎缺失"的单边孤儿列, 反之亦然。文本来源仍是 content_full, 留篇门控仍是 full-only, 银行-年度向量聚合(_aggregate_bank_year_texts)与随后的 top-10 最近邻同行检索均限定在同一(年度, 轨道, 引擎)的银行集合内、不跨引擎混算相似度矩阵, N=10 最近邻同行数设定与 canonical 列一致。使用本列做实证时应将其与无 _lg 后缀的 strat_diff_n10_emb 并排报告(如稳健性表的双栏对照), 而非将两者同时作为同一回归方程里的多重工具变量或叠加控制变量混入同一 Hansen J 检验; 二者数值量级可能因维度(3072 vs 4096)与训练目标差异而不完全等价, 比较时应关注方向与显著性的一致性而非绝对水平。

## VAR: strat_diff_n10_emb_lg_ctx

【变体差分】
本列同时叠加两个差分维度: 嵌入引擎切换为 text-embedding-3-large(_lg co-primary 轨), 文本轨道切换为 ctx(标题+实体窗口, content_ctx)。它是 strat_diff_n10_emb_ctx 在跨厂商嵌入下的对等复现, 也是 strat_diff_n10_emb_lg 在实体窗口文本上的对等复现——三轨 × 双引擎 = 六列矩阵中的一格。留篇门控依旧 full-only, 与全部同族列共享同一批留篇文章行集合, 差异只体现在编码输入文本与嵌入模型两个正交维度上; both-or-neither 缺失规则仍适用, 即该 ctx 文本若在 _lg 引擎侧 embed 失败, 无 _lg 后缀的 strat_diff_n10_emb_ctx 同一观测也会同步置缺失, 反之亦然, 保证两条 co-primary 轨道在样本口径上严格对齐、不产生单边孤儿。N=10 近邻梯子保持不变, 与 N∈{20,30,40,50} 的其余档位互为稳健性并排, 不构成优先排序。该列与家族内其余五列的关系遵循同一条铁律: 三轨(full/ctx/ss)与两引擎(主轨/_lg)各自正交、各自 just-identified, 严禁在同一 over-identified Hansen J 里混用; 在稳健性表中报告该列时, 建议同栏并列 strat_diff_n10_emb_ctx 作为跨厂商对照, 而非单独展示。本列所处的四象限位置(_lg 引擎 × ctx 轨道)在解读上应同时满足两条独立铁律: 与 strat_diff_n10_emb_ctx 比较用于判断"结果是否对嵌入厂商稳健", 与 strat_diff_n10_emb_lg 比较用于判断"结果是否对文本窗口选择稳健", 两条比较相互独立、互不替代, 不能因一条比较通过就省略另一条。

## VAR: strat_diff_n10_emb_lg_ss

【变体差分】
本列叠加嵌入引擎为 text-embedding-3-large、文本轨道为 ss(同句共现窗口)。ss 轨道的构造原语是"标题+银行∧金融科技词同句共现窗口(默认 ±1 句半径, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制)", 镜像 ctx 轨道的回退语义: 若某篇文章内不存在银行与金融科技词的同句共现, content_ss 回退为全文 body、并将 ss_is_fallback 标记为 True, 此时该文章在 ss 轨道上的嵌入实质上退化为对全文的编码, 与 ctx 轨道回退到全文正文的处理完全对称、共享同一个 n_articles 分母口径。留篇门控依旧只看 llm_verified_full, ss 轨的回退与否不影响该文章是否计入分母, 只影响该文章嵌入向量所依据的文本窗口宽窄。本列是 ss 轨道 + _lg 引擎的组合格, 与 strat_diff_n10_emb_ss(同轨道、主嵌入引擎)互为 co-primary 并排、与 strat_diff_n10_emb_lg_ctx(同引擎、不同轨道)互为三轨并排, 两个维度都不设主次, 均须各自 just-identified 进入模型, 不得混入同一 over-identified Hansen J。both-or-neither 缺失规则同样适用于本列与 strat_diff_n10_emb_ss 之间: 任一引擎在该 ss 文本单元上 embed 失败, 两条轨道同步置缺失。使用时应留意 ss 轨道在回退占比偏高的银行-年度单元上实质与 full/ctx 高度重合, 解读差异化系数时宜结合回退率一并披露。本列相较无 _lg 后缀的 ss 轨同伴, 提供的是"文本窗口最窄 + 嵌入引擎切换"两重稳健性叠加, 在样本量本就因同句共现要求而偏小的 ss 轨道上, 跨引擎一致性检验的说服力尤为重要——若 Qwen 与 text-embedding-3-large 两条 co-primary 轨道在 ss 窗口下方向一致, 可在一定程度上排除结果是单一嵌入模型训练目标或向量范数偏差所致的伪相关。

## VAR: strat_diff_n10_emb_ss

【变体差分】
本列使用主嵌入引擎 Qwen3-Embedding-8B, 文本轨道为 ss(标题+银行∧金融科技同句共现窗口, content_ss)。与 ctx 轨道的判定不对称口径一致——ss 轨道的共现窗口构造同样遵循银行侧"否定+短名过滤"、金融科技侧"裸 AC 自动机 607 词表"的不对称判据; 当同句共现缺失时, content_ss 回退为全文 body 并置 ss_is_fallback=True, 与 ctx 轨的回退语义完全镜像, 共享同一个 n_articles 分母口径。留篇门控为 full-only, 本列的样本行集合与 full/ctx 轨道完全一致, 只是嵌入编码所依据的文本窗口更窄(理想情形下仅覆盖银行与金融科技词紧邻同现的句子), 理论上能让策略差异化信号进一步聚焦到银行与金融科技实体真正共同出现的叙事片段, 代价是回退样本占比上升时该轨道退化为准 full 轨的重复测度。本列与 strat_diff_n10_emb(full 轨主引擎)、strat_diff_n10_emb_ctx(ctx 轨主引擎)构成三轨主引擎并排组, 与 strat_diff_n10_emb_lg_ss(同轨道 _lg 引擎)构成 co-primary 双轨并排组, 两组维度正交, 均须各自 just-identified, 严禁混入同一 over-identified Hansen J。本列在方法学上是家族内与 Guzman & Li (2023) 原始"策略嵌入距离"构念语义最贴近实体共现要求的一档: 由于 ss 轨道只在银行与金融科技词真正同句出现时才采用局部窗口文本, 未回退的观测其嵌入向量应最能反映"该行金融科技相关叙事的独特表述方式", 而回退观测则退化为准 full 轨测度; 建议在稳健性分析中报告未回退子样本上的系数, 作为对全样本估计的补充核验, 但不应据此重新定义样本口径(留篇门控始终是 full-only, 不因 ss 轨回退与否而改变分母)。

<!-- rendered-citations:begin -->
Guzman, J., & Li, A. (2023). Measuring Founding Strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Haans, R. F. J. (2019). What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Su, J., Gao, X., & Tan, J. (2024). Positioning for Optimal Distinctiveness: How Firms Manage Competitive and Institutional Pressures under Dynamic and Complex Environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Arts, S., Cassiman, B., & Hou, J. (2025). Technology Differentiation, Product Market Rivalry, and M&A Transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is Cosine-Similarity of Embeddings Really about Similarity? Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
<!-- rendered-citations:end -->
