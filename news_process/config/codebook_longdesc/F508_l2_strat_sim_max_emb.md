---
family_id: F508
columns:
- strat_sim_max_emb
- strat_sim_max_emb_ctx
- strat_sim_max_emb_lg
- strat_sim_max_emb_lg_ctx
- strat_sim_max_emb_lg_ss
- strat_sim_max_emb_ss
unit: 余弦相似度 [-1,1]
formula: 'strat_sim_max_emb = max_{j∈peer(i,t)} cos(v_i, v_j), 其中 v_i 为银行 i 在年 t 的语义向量: 先将该行-年全部合格文章的文本样本拼接 (join) 为单一长字符串 agg_text, 再整体交由嵌入引擎编码得到 v_i (超长文本走朴素分段 chunking + Mean Pooling, 而非逐篇先编码再对多个文章向量取均值), peer(i,t) 为同年可比同行集合; 六列在此式基础上按「文本轨」(full/ctx/ss) 与「嵌入引擎」(Qwen3-Embedding-8B 主轨 / text-embedding-3-large `_lg` 轨) 两个维度做笛卡尔展开取值。'
producer: pipeline\features\strategic_diff.py ; pipeline\panel\stata_export.py
upstream:
- 25_article_sbert
- 14_materialize_ctx
citations:
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
- doi: 10.1002/smj.3687
  type: journal
  authors: Arts, S., Cassiman, B., & Hou, J.
  year: 2025
  title: Technology differentiation, product market rivalry, and M&A transactions
  venue: Strategic Management Journal
  vol: '46'
  issue: '4'
  pages_or_artno: 837-862
- doi: 10.1111/jofi.12050
  type: journal
  authors: Hoberg, G., Phillips, G., & Prabhala, N.
  year: 2014
  title: Product market threats, payouts, and financial flexibility
  venue: The Journal of Finance
- doi: 10.18653/v1/D19-1410
  type: journal
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: 'Sentence-BERT: Sentence embeddings using Siamese BERT-networks'
  venue: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)
  pages_or_artno: 3980-3990
- doi: 10.1145/3589335.3651526
  type: journal
  authors: Steck, H., Ekanadham, C., & Kallus, N.
  year: 2024
  title: Is cosine-similarity of embeddings really about similarity?
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
new_dois: []
---

## CORE

【构念与来源】
本家族测度的构念是「银行 i 在报道语义空间中与其可比同行的最大相似度」, 即战略趋同度 (strategic similarity) 的镜像互补量: 相似度越高, 说明该行当年被媒体描述的业务/战略叙事越接近某一具体同行, 缺乏独树一帜的文本特征; 相似度越低, 说明其战略叙事在同行集合中更具辨识度。该构念脱胎于文本产业分类与产品市场差异化文献的核心洞见 (Hoberg & Phillips 传承的 TNIC 方法论谱系): 企业对自身业务的公开文本描述蕴含真实的战略定位信息, 可用作难以直接观测的产品/市场战略距离的代理变量。本项目将该逻辑从企业年报的自我描述迁移到第三方媒体对银行的报道文本, 前提假设是: 媒体报道虽非银行自陈, 但在样本量充足时其语义质心能够近似反映该行在公众叙事中的战略画像, 这与 Haans (2019) 关于"在同质化竞争环境中差异性如何影响绩效"的最优显著性 (optimal distinctiveness) 框架、以及 Su, Gao & Tan (2024) 关于企业如何在竞争与制度压力下管理定位差异化的研究一脉相承——二者均以文本/类别相似度刻度企业的战略位置, 而非依赖财务报表科目。本族与同一 producer 输出的距离族 `strat_diff_n5_emb` 系列构念互补但不等价: 距离族衡量与 N 个最近邻的平均/加权差异, 反映局部竞争强度; 本族的"取最大值"操作刻意聚焦单一最相似同行, 捕捉的是"与哪个具体对手撞叙事"这一极值信息, 二者在计量模型中不应替换使用, 而应视为对同一潜在构念的两种互补切面。

【方法学与计算】
计算管线起点是 producer `strategic_diff.py::_aggregate_bank_year_texts`: 依轨道取全文/实体窗口/银行∧金科同句窗口后的文章样本, 先按银行-年分组把该组内全部合格文章的文本样本逐篇拼接 (`' '.join`) 为单一长字符串 agg_text (而非先逐篇编码为句向量再对多个文章级向量取算术平均); 每个银行-年恰产生一条 agg_text。该 agg_text 再整体交给 `_embed_texts_with_chunk_pooling` 编码得到该行-年的语义向量 v_i: 若 agg_text 超过嵌入引擎单次可处理的 token 上限, 内部走朴素分段 (naive chunking) 切成若干片段分别编码后做 Mean Pooling 合并为一个向量, 这一分段发生在"已拼接的单一长文本"内部, 与"先逐篇文章各自编码、再对多个文章级向量取均值"是两种不同机制——前者是对同一长字符串的机械切分, 后者才会保留逐篇文章的独立语义边界, 本族测度采用的是前者。对每个焦点银行-年 (i,t), 在同年样本内枚举其余全部银行 j≠i 作为潜在同行, 计算向量间的余弦相似度 cos(v_i, v_j) (`_build_embedding_sim_matrix`), 取其最大值作为 `strat_sim_max_emb`。因为该向量来自嵌入模型的稠密表征而非非负词频/主题分布, 该相似度的真实值域是 [-1, 1] (与 TF-IDF/LDA 轨的 [0,1] 值域不同, 后者向量非负故余弦不会取负); 若历史实现曾将嵌入轨相似度强行截断到 [0,1], 属于值域删失, 会把负相关的语义关系错误地地板到零, 当前口径已按真实值域 [-1,1] 记录, 计算/使用该列时不应再假设非负。本族六列由两个正交维度的笛卡尔积构成: 第一维是文本轨 (full 全文标题+正文 / ctx 标题+实体窗口 / ss 标题+银行∧金科同句±N窗口), 第二维是嵌入引擎 (无 `_lg` 后缀 = 硅基流动 Qwen/Qwen3-Embedding-8B, 4096 维, canonical 无后缀主轨; `_lg` 后缀 = OpenAI/yunwu text-embedding-3-large, 3072 维)。两条嵌入轨线是 co-primary 关系: 二者同为主测度、互为稳健性、严格 parity (任一引擎对某行嵌入失败为 None, 同族两列同步置 NaN, 不产生单边孤儿列)。三条文本轨与两条嵌入轨各自 just-identified 并排排列, 互为稳健性、不分主次, 严禁在同一 over-identified 的 Hansen J 检验中把不同轨/不同引擎的列混作多重工具变量同时使用——这是本项目对涉及三轨文本与 co-primary 双嵌入所有测度族的统一铁律。ss 轨若焦点文章内不存在银行与金科词的同句共现, 回退为使用全文 body 文本 (镜像 ctx 轨回退语义), 相应地该行-年质心的样本构成会偏向"回退产生的全文文本"而非"严格同句窗口文本", 用户在解读 ss 轨数值时应结合 `ss_is_fallback` 标记综合判断, 而非假定 ss 轨恒为严格窗口。留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否计入"该行-年有效银行金科报道"样本, 判据只看 full 轨的 LLM 验证结果 (`llm_verified_full`); ctx/ss 轨的质心样本因此是 full 留篇集合的子集, 三轨行宇宙一致, 只是每轨各自用自己的文本内容重新编码质心, 这保证了三轨在样本层面可比、差异只来自文本窗口本身。

【文献定位】
本族方法论的直接学理祖先是 Hoberg, Phillips & Prabhala (2014) 提出的以文本相似度度量产品市场竞争流动性的框架, 该文用 10-K 文本相似度构造企业间竞争强度的连续测度, 本族沿用其"取相似度构造同行竞争强度代理变量"的基本逻辑, 但将底层表征从稀疏词袋/TF-IDF 换为稠密句向量嵌入, 顺应了近年文本-as-数据方法从词频统计向语境化嵌入迁移的趋势。Haans (2019) 与 Su, Gao & Tan (2024) 两篇 Strategic Management Journal 论文为"相似度—差异化—绩效"关系提供了理论支撑, 说明战略相似度本身即是具有独立解释力的构念, 而非仅是竞争强度的副产品; Arts, Cassiman & Hou (2025) 则展示了技术差异化测度在并购/产品市场竞争情境下的应用范式, 佐证了本族"取同行集合极值相似度"这一构造思路在战略管理实证文献中具有先例。底层句向量编码方法学参照 Reimers & Gurevych (2019) 提出的 Sentence-BERT 框架 (孪生网络句嵌入训练范式), 本项目虽未直接调用 SBERT 权重, 但沿用其"用余弦相似度比较句/文档级稠密向量"的评估惯例。需要特别提示的方法论陷阱是 Steck, Ekanadham & Kallus (2024) 指出的"嵌入余弦相似度未必真实反映语义相似度"问题——不同嵌入模型的向量几何结构、归一化方式、训练目标都会系统性影响余弦相似度的数值分布与可比性, 这正是本族坚持 Qwen 与 `_lg` 两条 co-primary 引擎并排稳健、而非只信任单一嵌入模型点估计的方法论理由: 若结果仅在一条引擎轨上显著而在另一条上消失, 应优先怀疑测度层面的嵌入模型伪影, 而非急于下战略叙事层面的实质性结论。

## VAR: strat_sim_max_emb

【变体差分】
本列是家族的 canonical 无后缀基准列: 文本轨 = full (标题+全文正文), 嵌入引擎 = Qwen/Qwen3-Embedding-8B (硅基流动, 4096 维) 主轨。producer 侧对该基名刻意采用裸命名惯例 (无 `_full` 后缀), 这是 `strategic_diff.py` 内 N-最近邻差异度 (`strat_diff_n5_emb`)、最大相似度 (本列)、质心距离 (`centroid_diff_emb`) 三个子族共享的统一命名约定, 与家族内其余五列均带轨道和/或引擎后缀的模式相区分, 使用时不应误读为"无轨道信息"或视为遗漏后缀的笔误。该列的质心样本来自 full-only 留篇门控 (2026-06-29 起生效) 下的全部合格银行金科报道正文: 一篇文章能否计入 (i,t) 的质心均值样本, 只由该篇 full 轨的 LLM 三家投票验证结果 (`llm_verified_full`) 决定, 与 ctx/ss 轨各自的判定无关, 这保证了本列在样本层面覆盖最完整、噪声来源最单一。由于该列同时是文本轨的 full 端点与嵌入引擎的 Qwen 端点, 它在六列矩阵中处于"双重基准"位置: 既是 ctx/ss 两条文本轨稳健性对照的锚点, 也是 `_lg` 引擎稳健性对照的锚点, 是下游 paper 模块 (如 `strategic_diff` 自身处理变量族与识别策略章节) 默认优先引用的一支, 但这不意味着其在统计意义上比其余五列更"正确"——六列之间是并排稳健性关系, 并非层级关系。命名上需要留意, 家族内其余五列的后缀顺序是"引擎标记在前、轨道标记在后" (如 `_lg_ctx` 而非 `_ctx_lg`), 这与 `stata_export.py` 内 `_lg` 派生循环的生成顺序一致, 使用批量正则匹配列名时应遵循该固定顺序, 不宜假设两个后缀可以任意换位。

## VAR: strat_sim_max_emb_ctx

【变体差分】
与 canonical 列的差分维度仅在文本轨一个维度: 本列质心向量改用 ctx 轨文本 (标题+围绕目标银行/金科实体的窗口片段, 由 stage 14 `ctx_materializer` 物化 `content_ctx` 列, prepend_title 拼接) 编码, 嵌入引擎仍是 Qwen/Qwen3-Embedding-8B 主轨, 未变。ctx 轨的窗口裁剪去除了正文中与银行-金科关系无直接关联的段落 (例如同一篇报道中与本次报道主题无关的其他业务段落), 理论上能降低无关内容对质心方向的稀释噪声、提升相似度测度对"该行金科相关叙事"本身的聚焦度, 但代价是每篇文章参与质心计算的文本量变小, 对样本量本就稀疏的行-年组合 (如小型城商行早期年份) 更敏感, 极端情况下质心方向可能被少数几篇文章主导。本列与 canonical 列 (full 轨) 构成 just-identified 并排的三轨稳健性对照之一, 二者数值差异若持续较大, 通常提示该行-年报道中"全文整体基调"与"聚焦实体窗口内容"存在系统性偏离 (例如全文中金科叙事只占一小部分篇幅), 而非测度本身出错; 依照项目铁律, 该列不应与 canonical 列在同一个 over-identified Hansen J 检验中同时作为工具变量混用。使用建议上, 若研究者关心的是"银行在实体相关叙事层面与哪个同行最相似"这一更精确的问题 (例如比较两行的金科业务定位是否趋同), 本列比 canonical 全文列更贴切; 若关心的是"银行整体媒体形象层面的最大相似同行", 则 canonical 列更合适, 两者服务于不同的研究问题层次, 不存在绝对优劣。

## VAR: strat_sim_max_emb_lg

【变体差分】
与 canonical 列的差分维度仅在嵌入引擎一个维度: 文本轨仍是 full, 但质心向量改用 text-embedding-3-large (OpenAI/yunwu 端点, 3072 维) 编码后再求余弦相似度, 而非 Qwen/Qwen3-Embedding-8B (4096 维)。该列与 canonical 列共同构成 co-primary 双轨中的 `_lg` 一侧, 二者严格 parity: 若某行-年在 Qwen 轨嵌入失败 (值缺失), `_lg` 轨对应值同步置 NaN, 反之亦然, 项目内不允许出现只有一侧有值的孤儿观测, 这一 both-or-neither 约束由 producer 与 `stata_export.py` 的标签/派生逻辑共同保证。两条引擎轨互为验证而非彼此的稳健性附庸: 3072 维与 4096 维向量空间的几何结构、训练目标、归一化方式均不同, Steck, Ekanadham & Kallus (2024) 指出嵌入余弦相似度未必忠实反映语义相似度这一方法论警示在此尤为相关——若某个基于本族测度的战略结论只在 Qwen 轨或只在 `_lg` 轨上显著, 应视为对该结论稳健性的警示信号, 提示结论可能对具体嵌入模型的几何伪影敏感, 而非确认信号。从治理角度看, 两条引擎轨分属两套完全独立的 API 供应链 (Qwen 走硅基流动 `https://api.siliconflow.cn/v1`, `_lg` 走 OpenAI/yunwu 端点), 这既是稳健性设计, 也是供应链风险对冲: 任一供应商出现服务中断、模型更新或计费策略变化, 都不会导致本族测度整体失效, 仅相应一侧的列受影响, 且 both-or-neither 守卫会保证受影响观测同步置缺, 不会产生半侧数据污染下游回归的风险。

## VAR: strat_sim_max_emb_lg_ctx

【变体差分】
本列在两个维度上同时偏离 canonical 列: 文本轨为 ctx (非 full), 嵌入引擎为 `_lg` text-embedding-3-large (非 Qwen 主轨, 3072 维)。它是 `strat_sim_max_emb_ctx` 在嵌入引擎维度上的 co-primary 对照 (同文本轨, 换引擎), 也是 `strat_sim_max_emb_lg` 在文本轨维度上的三轨对照 (同引擎, 换文本轨); 换言之该列同时承载"文本窗口收窄"与"嵌入引擎切换"两条独立的稳健性检验路径, 解读时应分别与这两个相邻列逐一比较、定位差异来源, 而不宜脱离其余五列孤立解读单一数值。与 ctx 轨其余各列一致, 该列的质心样本行宇宙仍受 full-only 留篇门控约束 (只是文本内容与嵌入引擎不同), 保证六列之间样本层面严格可比、差异只来自"用什么文本""用什么引擎"这两个正交选择, 而不来自样本构成本身的漂移。在实证使用上, 本列适合用作"双重最严格设定"下的稳健性检验: 既用最聚焦的实体窗口文本排除无关段落噪声, 又用非主流 (相对项目 canonical 而言) 嵌入引擎排除单一供应商模型伪影, 若某个基于 canonical 列得到的结论在本列上依然成立, 说明该结论对文本窗口选择与嵌入引擎选择的联合扰动均不敏感, 是六列中稳健性证据强度最高的单一对照点之一。

## VAR: strat_sim_max_emb_lg_ss

【变体差分】
文本轨为 ss (标题+银行∧金科同句±N窗口, 窗口半径见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1, 与 stage 13 `cooccurrence_filter.sentence_radius` 是完全不同的两个配置键, 不可混用), 嵌入引擎为 `_lg` text-embedding-3-large。ss 轨判定口径较 ctx 更严格 (要求银行与金科词在同一句内共现, 而非仅在窗口范围内出现), 若焦点行-年内某篇报道不满足该条件, 该篇在 ss 轨质心计算中回退为使用全文 body 文本, 并共享 `n_articles` 分母, 由 `ss_is_fallback` 标记该回退状态; 回退发生率高的行-年应谨慎解读本列数值与 canonical full 轨的差异, 因为此时二者实际输入文本的重合度会显著上升, 差异会被人为压缩而非反映真实的窗口收窄效应。本列与 `strat_sim_max_emb_ss` 构成 ss 轨内部的 co-primary 引擎对照 (同文本轨, 换引擎), 也是 `strat_sim_max_emb_lg_ctx` 在文本轨维度上的对照 (同引擎, 换文本轨从 ctx 到 ss)。因为 ss 判据 (银行∧金科同句) 比 ctx 判据 (实体窗口) 更严格, 满足条件的样本量通常更小、回退比例通常更高, 本列作为"最严格文本窗口 + 非主流嵌入引擎"的组合, 在数据稀疏的行-年格 (尤其是早期年份或报道量本就不多的中小银行) 上出现缺失或数值不稳定的概率也相应更高, 解读结论前应先核对该行-年在 ss 轨的有效文章数与回退比例, 避免把样本稀疏导致的极端值误读为真实的战略趋同/差异化信号。

## VAR: strat_sim_max_emb_ss

【变体差分】
文本轨为 ss, 嵌入引擎为 Qwen/Qwen3-Embedding-8B 主轨 (与 canonical 列共享引擎, 仅文本轨从 full 切到 ss)。该列是三条文本轨 (full/ctx/ss) 在 Qwen 主轨侧的最后一支, 与 `strat_sim_max_emb`、`strat_sim_max_emb_ctx` 共同构成 just-identified 并排的三轨稳健性组合, 三者互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。回退语义同 `strat_sim_max_emb_lg_ss` 一节所述 (镜像 ctx 轨, 无银行∧金科同句共现时以全文 body 兜底、共享 `n_articles` 分母), 使用时建议结合该行-年样本内 `ss_is_fallback` 的比例判断本列数值是在多大程度上反映严格同句窗口叙事, 还是实质上退化为接近 full 轨的全文叙事; 回退比例越低, 本列相对 canonical 列的边际信息量越大。相较 `strat_sim_max_emb_lg_ss` (同文本轨换引擎), 本列因使用与 canonical 相同的 Qwen 主轨, 在生产环境中通常拥有更长的缓存播种历史与更稳定的服务可用性, 因此在样本覆盖率上一般不劣于 `_lg` 对照, 二者数值上的系统性偏离更适合归因于引擎几何差异而非采样噪声。作为 Qwen 主轨内部的第三条文本轨, 本列与 `strat_sim_max_emb`(full)、`strat_sim_max_emb_ctx`(ctx) 一起构成完整的三轨并排矩阵, 三者共享同一嵌入引擎因而不存在引擎维度的混杂, 任何三者之间的数值差异都可以纯粹归因于文本窗口构造方式的不同, 这使得该三元组是研究"文本窗口选择本身对语义相似度测度的边际影响"这一方法论问题的干净对照组, 也是本家族用于回应"结果是否对文本窗口裁剪方式敏感"这类审稿质疑的首选证据链。

<!-- rendered-citations:begin -->
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Su, J., Gao, X., & Tan, J. (2024). Positioning for optimal distinctiveness; How firms manage competitive and institutional pressures under dynamic and complex environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market threats, payouts, and financial flexibility. The Journal of Finance. https://doi.org/10.1111/jofi.12050
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), 3980-3990. https://doi.org/10.18653/v1/D19-1410
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity? Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
<!-- rendered-citations:end -->
