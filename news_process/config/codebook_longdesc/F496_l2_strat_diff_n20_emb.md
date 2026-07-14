---
family_id: F496
columns:
- strat_diff_n20_emb
- strat_diff_n20_emb_ctx
- strat_diff_n20_emb_lg
- strat_diff_n20_emb_lg_ctx
- strat_diff_n20_emb_lg_ss
- strat_diff_n20_emb_ss
unit: 无量纲距离得分, 取值范围 [0,2] (1 减去余弦相似度; 0=与最近 20 家同业新闻文本几乎重合, 2=方向完全相反)
formula: 'Ŝ_i = (1/20) · Σ_{j∈J_i^20} δ_ij, δ_ij = 1 − cos(v_i, v_j); v_i 为银行 i 当年金融科技新闻文档的稠密语义嵌入向量 (Qwen/Qwen3-Embedding-8B 或 text-embedding-3-large), J_i^20 为按 δ_ij 升序取的 20 家最近同业银行'
producer: pipeline\features\strategic_diff.py::compute_strategic_differentiation
upstream:
- 14_materialize_ctx (content_ctx/content_ss 三轨文本物化)
- 25_article_sbert (Qwen/Qwen3-Embedding-8B 主轨 + text-embedding-3-large _lg 双轨嵌入引擎)
- pipeline\panel\stata_export.py (面板列标签与 co-primary 标注)
citations:
- doi: "10.1287/mnsc.2022.4369"
  type: journal
  authors: "Guzman, J., & Li, A."
  year: 2023
  title: "Measuring Founding Strategy"
  venue: "Management Science"
  vol: "69"
  issue: "1"
  pages_or_artno: "101-118"
- doi: "10.1086/688176"
  type: journal
  authors: "Hoberg, G., & Phillips, G."
  year: 2016
  title: "Text-Based Network Industries and Endogenous Product Differentiation"
  venue: "Journal of Political Economy"
  vol: "124"
  issue: "5"
  pages_or_artno: "1423-1465"
- doi: "10.1002/smj.3687"
  type: journal
  authors: "Arts, S., Cassiman, B., & Hou, J."
  year: 2025
  title: "Technology Differentiation, Product Market Rivalry, and M&A Transactions"
  venue: "Strategic Management Journal"
  vol: "46"
  issue: "4"
  pages_or_artno: "837-862"
- doi: "10.1002/smj.2978"
  type: journal
  authors: "Haans, R. F. J."
  year: 2019
  title: "What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories"
  venue: "Strategic Management Journal"
  vol: "40"
  issue: "1"
  pages_or_artno: "3-27"
- doi: "10.1086/715162"
  type: journal
  authors: "Rodriguez, P. L., & Spirling, A."
  year: 2022
  title: "Word Embeddings: What Works, What Doesn't, and How to Tell the Difference for Applied Research"
  venue: "The Journal of Politics"
  vol: "84"
  issue: "1"
  pages_or_artno: "101-115"
- doi: "10.1145/3589335.3651526"
  type: journal
  authors: "Steck, H., Ekanadham, C., & Kallus, N."
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: "Companion Proceedings of the ACM Web Conference 2024"
  pages_or_artno: "887-890"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行 i 在给定年度的金融科技战略"独特性"或"拥挤度": 把该行当年全部金融科技报道聚合为一份"企业产品/战略描述"代理文档, 在稠密语义嵌入空间中量出它与市场上最像它的一批同业银行的平均语义距离。距离越大, 说明该行当年报道所呈现的金融科技叙事在语义上越"独树一帜"、越少与同业重叠; 距离越小, 说明该行的金融科技战略措辞与一批近邻同业高度雷同, 处于战略生态位拥挤地带。这一构念严格映射 Guzman & Li (2023, Management Science) 提出的"从相似度到创立战略"框架: 用文本相似度矩阵度量企业间的战略邻近性, 再把每家企业的相似度聚合为一个标量差异度指数。计算流程与 Hoberg & Phillips (2016, Journal of Political Economy) 逐年重建文本相似度网络的做法一致 — 相似度矩阵不跨年份汇总, 而是逐年在当年可比的银行集合内重新计算, 避免跨期语料结构漂移混入横截面比较。

本家族命名中的 "n20" 指最近邻聚合窗口 N=20, 是家族 `l2_strat_diff` 之下 top-k N 梯子 (`_TOPK_NN = {10,20,30,40,50}`) 中的一档。producer 论文推荐的基准值是 N=5 (`strat_diff_n5_emb` 系列, 属另一家族), N=20 与梯子上其余 N 值一样, 是"换一个近邻数量看结果是否稳健"的敏感性检验臂, 与 N=5 基准及梯子上其余各档互为稳健性、不分主次, 不构成谁是"更优"设定的主张。之所以要有这样一条梯子, 是因为最近邻聚合数 N 本身是研究者自由度: N 太小 (如 3) 对个别年份的语料噪音敏感, N 太大则把远端、不太可比的同业也纳入"邻居"集合, 稀释差异度信号的辨识力; 通过在 N∈{3,4,5,6,7,10,20,30,40,50} 上重复计算并观察系数符号/显著性是否稳定, 可以证明主结论不依赖于这一具体窗口宽度的取值。

大白话讲: 假设某银行今年的金融科技报道读起来"很像"另外二十家银行今年的报道 (讲的都是移动支付、开放银行接口这些差不多的东西, 用词、话题结构也接近), 那么这个银行的差异度得分就会很低, 说明它在做的事情跟一大片同业没什么区别; 反过来如果它的报道内容跟市场上大多数同业都不太像, 找不到很多"长得像"的邻居, 差异度得分就会偏高, 说明它走的是相对独特的金融科技路线。

【方法学与计算】
计算分五步。第一步, 按 (银行, 年度) 聚合该行当年全部金融科技新闻文本, 形成一份"企业产品描述"代理文档 (三轨口径见下)。第二步, 对同一年度内全部银行的代理文档, 用嵌入模型逐一编码为稠密向量; 本家族对应两个 co-primary 嵌入引擎的其中一个: canonical 无后缀轨用 `Qwen/Qwen3-Embedding-8B` (硅基流动 API, 4096 维), `_lg` 后缀轨用 `text-embedding-3-large` (OpenAI/yunwu API, 3072 维)。第三步, 计算银行两两之间的成对距离 δ_ij = 1 − cos(v_i, v_j), 得到当年 (在制片可比银行集合内逐年重建, 不跨年汇总) 的距离矩阵; 距离取值范围 [0,2] (cos 相似度 ∈ [−1,1] 的仿射变换), 0 表示两份文档方向完全一致、2 表示方向完全相反。第四步, 对每家银行 i, 按 δ_ij 升序取距离最近的 20 家同业银行组成邻居集合 J_i^20, 计算算术平均 Ŝ_i = (1/20)·Σ_{j∈J_i^20} δ_ij, 即为 `strat_diff_n20_emb` 系的原始面板值。第五步, 面板导出层 (`stata_export.py`) 为每一列打上 "co-primary: Qwen/Qwen3-Embedding-8B" 或对等的 _lg 标注, 供下游识别其嵌入来源。

三轨扩展方面: full 轨聚合银行当年全部金融科技报道正文 (标题+正文 prepend, 无 `_full` 后缀的裸命名, 遵循 producer 命名约定 n5_emb/sim_max_emb/centroid_diff_emb 一族的历史习惯); ctx 轨 (`_ctx` 后缀) 改用 stage 14 物化的实体窗口文本 `content_ctx` 重新聚合并重新计算整套距离矩阵与最近邻聚合; ss 轨 (`_ss` 后缀) 改用银行∧金科同句共现窗口文本 `content_ss`, 镜像 ctx 轨的回退语义 — 若某文章无银行与金科词的同句共现, `content_ss` 退化为全文 body 且 `ss_is_fallback=True`, 与 stage 21 情感三轨共享同一套回退口径, 不是本家族独有设计。三轨 (full/ctx/ss) 各自基于独立的文本聚合与独立的距离矩阵重建, 互为稳健性、不分主次, 禁止把三轨的估计混进同一 over-identified Hansen J。

co-primary 双轨方面: 无后缀 (Qwen) 与 `_lg` (text-embedding-3-large) 是两条并排的主测度, 严格 parity — 若某银行-年度在某一嵌入引擎上取不到向量 (API 缺失/离线未命中缓存), 该轨同族全部列同时置 NaN, 不出现只有一条轨降级、另一条轨保留数值的单边孤儿情形。两条嵌入轨各自独立地跑完整的 N-最近邻聚合流程 (各自的余弦距离矩阵、各自的近邻集合选取), 互为稳健性、不分主次, 不得把两条嵌入轨的估计量混入同一个过度识别 (over-identified) 的 Hansen J 检验; 二者应各自 just-identified 并排呈现。

留篇门控口径 (2026-06-29 起): 是否算作"一篇有效的银行-金融科技报道"纳入聚合文档只看 stage 21 的 `llm_verified_full == True` (full-only 门控); ctx/ss 轨的行宇宙是 full 轨留篇集合的子集, 在这个共同子集内各轨分别聚合各自的文本并计算距离, 而非各轨各自独立筛选留篇标准。

【文献定位】
本家族的核心构念与聚合公式直接取自 Guzman & Li (2023, Management Science) "Measuring Founding Strategy" 提出的最近邻相似度聚合法, 该文用企业公开文本表述之间的成对相似度矩阵、聚合至每家企业最近的若干竞争者, 构造出可用于横截面比较的"战略差异度"标量指标, 本家族的 Ŝ_i=(1/N)Σδ_ij 公式与该文 Section 3 的构造方式一一对应, 仅将标的从"创立战略文本"替换为"银行金融科技新闻叙事"。逐年重建相似度网络 (不跨期汇总、避免语料结构漂移混入横截面比较) 的做法参照 Hoberg & Phillips (2016, Journal of Political Economy) 在文本网络产业分类构造中确立的方法学规范, 该文是文本相似度用于刻画企业间竞争生态位/产品市场差异化的经典出处。战略距离度量与企业绩效、竞争压力之间关系的理论定位参照 Haans (2019, Strategic Management Journal) 关于"差异化的价值取决于同质/异质类别情境"的发现, 以及 Arts, Cassiman & Hou (2025, Strategic Management Journal) 关于技术差异化与产品市场竞争强度关系的近期证据, 二者共同支持"文本语义距离是可解释的战略生态位测度"这一构念定位。嵌入模型作为文本相似度测度工具本身的方法学有效性与局限, 参照 Rodriguez & Spirling (2022, The Journal of Politics) 对词向量在应用研究中"何时可信、如何判别可信"的系统性讨论, 以及 Steck, Ekanadham & Kallus (2024) 对余弦相似度作为嵌入空间距离度量的适用边界的近期方法论提醒 — 后者提示余弦距离在不同嵌入模型/不同训练目标下的可比性并非理所当然, 这也是本家族坚持 canonical 与 `_lg` 两条 co-primary 嵌入轨并排互证、而非相互替代的方法论理由之一。

## VAR: strat_diff_n20_emb

【变体差分】
本列是家族在 full 轨、canonical 嵌入引擎 (Qwen/Qwen3-Embedding-8B, 硅基流动) 上的基准形态: 聚合银行当年全部金融科技新闻正文 (标题+全文 prepend, 无 fallback 概念, 因为 full 轨不依赖实体窗口或同句共现判据), 用 Qwen 嵌入向量计算全行业成对余弦距离矩阵, 对每行取距离最近的 20 家同业银行取平均, 得到 Ŝ_i。它是 N=20 敏感性梯子上与 N=5 基准最贴近的一档 (相对 N=30/40/50 邻居窗口更窄), 与同梯子其余 N 值 (10/30/40/50, 以及 canonical 基准 N=5 属另一家族 `strat_diff_n5_emb`) 互为稳健性并排、不分主次, 也与其 `_lg`/ctx/ss 变体互为稳健性并排、不分主次。

行宇宙受 full-only 留篇门控约束 (2026-06-29 起): 是否算作"一篇有效的银行-金融科技报道"纳入当年聚合文档, 只看 stage 21 的 `llm_verified_full == True`, ctx/ss 轨的行宇宙均是这一 full 集合的子集。计算上, 每年度内所有满足留篇条件的银行会被同时纳入当年的成对距离矩阵, 银行数不足 21 家 (含自身) 的年度理论上仍可正常计算 (取全部可用同业作为邻居集合, 但样本极小年份取值会更不稳定, 解读时应留意分母覆盖度); 距离矩阵逐年重建, 不跨年拼接, 因此同一银行在不同年度的 `strat_diff_n20_emb` 之间不构成同一向量空间内的可比时间序列, 只能在同一年度横截面内比较大小或做面板固定效应回归时依赖年份固定效应吸收跨年不可比部分。数值方向: 越大代表当年金融科技叙事在语义上越独树一帜 (与市场上最像的 20 家同业仍有较大距离), 越接近 0 代表叙事高度趋同、处于战略生态位拥挤地带。

## VAR: strat_diff_n20_emb_ctx

【变体差分】
在 `strat_diff_n20_emb` 的 canonical Qwen 嵌入引擎基础上, 唯一差分维度是文本聚合口径由 full 轨改为 ctx 轨: 每篇纳入聚合的报道不取全文, 而取 stage 14 物化的 `content_ctx` (标题+实体窗口文本), 据此重新聚合银行当年文档、重新计算距离矩阵与 20-最近邻平均。与 full 轨相比, ctx 轨的每份"企业代理文档"更短、更聚焦于银行与金融科技实体周边的措辞, 理论上应降低无关背景段落 (如宏观经济评论、领导讲话套话) 对文本相似度的稀释效应, 使距离度量更贴近"银行在报什么金融科技动作", 而非"这篇报道整体行文风格像不像"。

ctx 轨与 full/ss 轨各自独立聚合、各自独立计算成对余弦距离矩阵与最近邻集合, 三轨并排互为稳健性、不分主次, 禁止把三轨的估计混入同一 over-identified Hansen J。行宇宙是 full 轨留篇集合的子集 (conditional-on-full, 2026-06-29 起的口径), 分母/文档集合不向 full 轨借用插补, 仅共享"哪些文章算数"这一留篇集合本身; 对于集合内某些文章, `content_ctx` 的具体切分依赖 stage 14 的实体窗口抽取逻辑, 与银行∧金科同句共现判据 (对应 ss 轨) 是不同的抽取口径, 不应混淆。若某银行-年度在 ctx 轨上因样本极小导致近邻集合覆盖不足, 数值波动性会高于 full 轨, 属预期的稳健性检验特征而非缺陷。

## VAR: strat_diff_n20_emb_lg

【变体差分】
在 full 轨文本聚合口径不变的前提下, 唯一差分维度是嵌入引擎由 canonical Qwen/Qwen3-Embedding-8B (4096 维, 硅基流动 API) 切换为 co-primary 对偶 text-embedding-3-large (3072 维, OpenAI/yunwu API)。距离矩阵构造、20-最近邻选取与算术平均聚合公式与 canonical 轨完全一致, 唯一差别在于喂入余弦距离计算的向量来自不同厂商、不同维度、不同训练目标的嵌入模型。这一差分维度存在的意义是回应"任何单一嵌入模型都可能引入自身的训练语料偏差或几何各向异性 (anisotropy), 使文本相似度的绝对水平或排序受模型选择本身驱动"这一方法学关切 — 通过在两个跨厂商、跨维度的嵌入空间中各自独立重跑同一套最近邻聚合流程, 若两条轨给出方向一致、量级相近的银行排序, 则可以排除"结果是某个具体嵌入模型的训练伪影"这一解释。

本列与 `strat_diff_n20_emb` 严格 parity: 二者共用同一份 full 轨聚合文档, 仅嵌入向量来源不同; 若某银行-年度在 text-embedding-3-large 端无法取到向量 (API 调用失败, 或离线模式 `NEWS_PROCESS_LLM_OFFLINE=1` 下缓存未命中触发 raise), 本列与同一 `_lg` 族的其余列 (`centroid_diff_emb_lg`/`coh_emb_lg`/`strat_diff_lg_full` 等) 同时置 NaN, 不允许出现"只有本列缺失、同族其余 `_lg` 列仍有值"的单边孤儿情形。两条嵌入轨 (canonical/`_lg`) 各自 just-identified 并排、互为稳健性、不分主次, 禁止把二者的估计混进同一 over-identified Hansen J 检验。

## VAR: strat_diff_n20_emb_lg_ctx

【变体差分】
本列同时叠加两个差分维度: 嵌入引擎为 co-primary 对偶 `_lg` (text-embedding-3-large, 3072 维) 而非 canonical Qwen/Qwen3-Embedding-8B (4096 维), 文本聚合口径为 ctx 轨 (`content_ctx`, 标题+实体窗口文本) 而非 full 轨。计算流程上, 先按 stage 14 物化的实体窗口逻辑重新组装每家银行当年的代理文档, 再用 text-embedding-3-large 编码为向量, 最后重新计算成对余弦距离矩阵、取 20-最近邻算术平均, 与其余各格的 20-最近邻聚合公式在数学形式上完全一致, 差别只体现在输入端 (文本口径+嵌入模型) 的两处替换。

本列是"co-primary 嵌入双轨 (canonical/`_lg`) × 三轨文本 (full/ctx/ss)"这一 2×3 交叉网格中的一格, 与其余 5 个交叉格 (`strat_diff_n20_emb`[full×canonical]、`strat_diff_n20_emb_ctx`[ctx×canonical]、`strat_diff_n20_emb_ss`[ss×canonical]、`strat_diff_n20_emb_lg`[full×_lg]、`strat_diff_n20_emb_lg_ss`[ss×_lg]) 各自独立计算、并排互为稳健性, 不分主次, 均不得混入同一 over-identified Hansen J。行宇宙仍受 full-only 留篇门控约束 (2026-06-29 起), 是 full 轨留篇集合的 conditional-on-full 子集, 而非 ctx 轨自身独立定义的留篇标准; 该列继承 `_lg` 系的 both-or-neither 降级规则, 缺失时与同族其余 `_lg` 列同步置 NaN。

需要特别提示的是, 本列同时叠加了两条独立的稳健性梯子 (文本判据梯子与嵌入引擎梯子), 因此解读时切勿把它当作某个"更精细/更权威"的最终版本 — 它只是敏感性检验矩阵里的一个格点, 目的是证明主结论 (若成立) 在文本抽取口径与嵌入模型两个维度上都不脆弱。若某研究只报告本列而略去 `strat_diff_n20_emb_ctx`(同判据、canonical 嵌入) 或 `strat_diff_n20_emb_lg`(同嵌入、full 判据) 中的任何一个, 会破坏"并排呈现、不挑最漂亮结果"的稳健性叙事完整性。

## VAR: strat_diff_n20_emb_lg_ss

【变体差分】
本列叠加两个差分维度: 嵌入引擎为 `_lg` (text-embedding-3-large, 3072 维), 文本聚合口径为 ss 轨 (`content_ss`, 标题+银行∧金科同句共现窗口, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句)。ss 轨相较 ctx 轨判据更严: ctx 轨取的是实体出现附近的窗口, ss 轨要求银行实体与金融科技词在同一句 (或同句±1 句内) 共同出现才计入该句, 是三轨中文本粒度最细、上下文最贴合"银行在谈论金融科技"这一具体动作的一档。

ss 轨的回退语义镜像 ctx 轨: 若某篇报道全篇不存在银行与金融科技词的同句共现 (例如报道整体在谈金融科技但银行名与金科词从未同句出现), 则该篇的 `content_ss` 退化为全文 body 且 `ss_is_fallback=True`, 与 stage 21 情感三轨、stage 15/16 等其余消费 `content_ss` 的下游模块共享同一份回退口径与同一份 `n_articles` 分母, 而非本家族独立定义的回退规则; `FINTECH_AC=None` (金科词典缺失) 时该轨 `*_is_fallback` 全体退化为 True。本列与 `strat_diff_n20_emb_ss` (同为 ss 轨、canonical 嵌入) 互为稳健性并排、不分主次; 与 `strat_diff_n20_emb_lg`(full×_lg)、`strat_diff_n20_emb_lg_ctx`(ctx×_lg) 同理并排、不分主次, 三者连同 canonical 侧对应三轨共同构成 2×3 网格, 均禁止混入同一 over-identified Hansen J, 且遵循 `_lg` 系 both-or-neither 降级规则。

在三条文本判据轨中, ss 轨对语料的要求最苛刻: 它不仅要求文章命中银行实体与金融科技词, 还要求二者出现在彼此的同一句 (或半径±1 句) 之内, 这比 ctx 轨"实体附近窗口"的宽松判据严格得多。因此本列 (ss×_lg) 在小样本银行-年度组合上比 `strat_diff_n20_emb_lg_ctx`(ctx×_lg) 更容易触发大比例 fallback 退化为全文聚合, 此时其数值行为会趋近于 full×_lg 格点 (即 `strat_diff_n20_emb_lg`)。这一现象是回退语义的自然结果, 不是本列计算逻辑的缺陷, 但在跨列比较时应结合 `ss_is_fallback` 覆盖率一并解读, 避免把 fallback 主导的样本误判为"ss 判据本身产生了差异化信号"。

## VAR: strat_diff_n20_emb_ss

【变体差分】
在 canonical Qwen/Qwen3-Embedding-8B 嵌入引擎基础上, 唯一差分维度是文本聚合口径切到 ss 轨: 聚合银行当年报道中的 `content_ss` (标题+银行∧金科同句共现窗口文本), 而非全文或实体窗口。未发生银行∧金科同句共现的文章, 其 `content_ss` 按镜像 ctx 轨的回退规则退化为全文 body 并标记 `ss_is_fallback=True`, 与 stage 21 情感三轨共享同一份 `n_articles` 分母口径, 不是本家族单独定义的回退逻辑。

距离矩阵构造 (逐年重建成对余弦距离) 与 20-最近邻算术平均聚合流程与 full/ctx 轨在数学形式上完全一致, 仅输入文档的抽取判据不同: full 轨不做任何窗口裁剪, ctx 轨按实体窗口裁剪, ss 轨按银行∧金科同句共现 (更严的判据) 裁剪, 三者互不借用彼此的文本, 也互不借用彼此的距离矩阵。本列与 canonical 侧的 full/ctx 轨、以及 `_lg` 对偶轨的对应三轨各自并排、互为稳健性、不分主次, 均不得混入同一 over-identified Hansen J; 行宇宙同样是 full 轨留篇集合 (`llm_verified_full == True`) 的 conditional-on-full 子集, 而非 ss 轨自身独立定义的留篇标准。ss 轨因判据最严, 在报道量较小的银行-年度上比 ctx 轨更容易触发 fallback, 解读该列取值时应结合 `ss_is_fallback` 的覆盖比例。

本列与 `strat_diff_n20_emb_lg_ss`(同判据、`_lg` 嵌入) 构成"同判据、双嵌入引擎"的对偶对, 二者应并排呈现、互相印证, 不应只报告其一; 与 `strat_diff_n20_emb`(full×canonical)、`strat_diff_n20_emb_ctx`(ctx×canonical) 构成"同嵌入引擎、三判据"的梯子, 三者也应并排呈现。若某年度银行样本量偏小 (如本项目本机 dev 环境 T=2 的极小样本), ss 轨的 fallback 触发比例可能显著高于生产语料规模下的预期水平, 此时该列的近邻聚合样本会明显偏向"退化为全文"的银行, 数值的区分度会相应下降, 这属于小样本下的预期退化现象, 不代表生产规模 (T=18, 完整语料) 下同一测度的实际表现。

<!-- rendered-citations:begin -->
Guzman, J., & Li, A. (2023). Measuring Founding Strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Arts, S., Cassiman, B., & Hou, J. (2025). Technology Differentiation, Product Market Rivalry, and M&A Transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Haans, R. F. J. (2019). What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Rodriguez, P. L., & Spirling, A. (2022). Word Embeddings: What Works, What Doesn't, and How to Tell the Difference for Applied Research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
<!-- rendered-citations:end -->
</content>
