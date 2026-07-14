---
family_id: F502
columns:
- strat_diff_n50_emb
- strat_diff_n50_emb_ctx
- strat_diff_n50_emb_lg
- strat_diff_n50_emb_lg_ctx
- strat_diff_n50_emb_lg_ss
- strat_diff_n50_emb_ss
unit: 无量纲差异度得分 (文本余弦距离均值), 值域 [0,2]
formula: 'Ŝ_i = (1/N) Σ_{j∈J_i^N} δ_ij, δ_ij = 1 − cos(v_i, v_j); N=50, J_i^N = 银行 i 在语义嵌入空间中相似度最高的 50 家同行 (Guzman & Li 2023 §3 公式, N-最近邻大邻域敏感性臂)'
producer: pipeline\features\strategic_diff.py (`_compute_nn_scores` + `_build_embedding_sim_matrix`); 面板标签映射见 pipeline\panel\stata_export.py
upstream:
- 14_materialize_ctx.parquet (`content_ctx`/`content_ss` 三轨文本物化, 银行-年度聚合文本经模块内 `_embed_texts_with_chunk_pooling` 直接调用 `EMBEDDING_CONFIG`/`_LARGE_SPEC` 嵌入 API 现算, 非消费 stage 25 产物)
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
new_dois: []
---

## CORE

【构念与来源】
本家族测度银行在新闻文本语义空间中的"战略差异度"(strategic distinctiveness), 直接实现 Guzman & Li (2023, Management Science) 在创业战略测量文献中提出的从相似度到差异度的转换规则, 并把其应用场景从"公司注册文件文本"迁移到"银行金科新闻报道文本"。核心直觉: 一家银行的新闻报道内容若与同行高度雷同(同质化叙事、同样的产品口径、同样的合作模式描述), 则其在嵌入空间里离最近的同行很近, 差异度低; 反之若该行的报道内容呈现出独特的战略叙事(独有的产品创新表述、独特的合作对象、差异化的数字化路径), 则与同行的语义距离更大, 差异度高。这一构念呼应 Hoberg & Phillips (2016, JPE) 文本网络产业分类的核心思想——企业间的文本相似度可作为产品市场定位相似度的可观测代理——但本家族把分析单位从"公司年度产品描述文本(10-K)"换成"银行年度金科相关新闻报道文本", 用第三方媒体叙事而非企业自我披露来刻画战略定位, 从而部分规避自我披露的策略性美化偏误, 同时引入媒体报道选择性/记者措辞风格的新噪声源(须与 outlet house-style IV 等稳健性工具配合解读)。

本家族属于家族 `l2_strat_diff` 的 top-k N 扩展支族: 家族基准 canonical 列是 N=5 最近邻(`strat_diff_n5_emb` 及其三轨/双嵌入孪生), 对应 Guzman & Li (2023) 论文原文推荐的基准邻域半径; 2026-07-02 的 top-k N 扩展(fix topk-n-expansion)在此基础上追加 N∈{10,20,30,40,50} 五个更大邻域半径的敏感性臂, 本家族 F502 即 N=50(最大邻域)一档, 是这一敏感性梯子里覆盖同行范围最广的一档——把"最近的50家同行"而非"最近的5家同行"纳入平均, 检验差异度测度是否对邻域大小的选择敏感, 抑或在放大邻域窗口后依然保持稳定的排序与量级。

【方法学与计算】
计算流程分三步。第一步, 为每个"银行 × 年度"单元, 从其全部三轨新闻文本(full/ctx/ss, 见下)聚合出一个代表性语义嵌入向量; 该嵌入向量并非取自 stage 25 `article_sbert` 的句子级产物, 而是本模块(`strategic_diff.py`)在 14_materialize_ctx 聚合出的银行-年度文本之上, 经 `_embed_texts_with_chunk_pooling` 直接调用嵌入 API 现算得到——主轨模型为硅基流动 API 的 `Qwen/Qwen3-Embedding-8B`(4096 维, `EMBEDDING_CONFIG` 配置), co-primary 对偶轨模型为 OpenAI/yunwu 的 `text-embedding-3-large`(3072 维, `_LARGE_SPEC` 配置, 家族列名带 `_lg` 后缀); 二者与 stage 25 句子级嵌入是模型选型上的姊妹关系, 但不存在消费/被消费的产物依赖。第二步, 以银行-年度为节点、跨节点计算成对余弦相似度矩阵(对角线设为 NaN, 排除自比), 相似度截断到嵌入余弦的真值域 [-1, 1](而非误伤的 [0, 1], 这一点在 2026-06-11 修复中被专门校正, 因为原先的 [0,1] 截断会把嵌入空间真实存在的负余弦值错误地下限到 0, 人为压低差异度上限)。第三步, 对每个银行-年度节点, 在相似度矩阵中按降序取相似度最高的 N=50 个"同行"(J_i^{50}), 计算每对的文本距离 δ_ij = 1 − cos(v_i, v_j), 再对这 50 个距离取算术平均, 得到该银行-年度的差异度得分 Ŝ_i = (1/50) Σ δ_ij。若某银行-年度在给定年份的可比同行数不足 50 家(|peers| < 50), 则该格直接置为缺失(NaN), 而非静默地用"能凑到的同行数"降级计算——这是 2026-06-11 (fix omni-g-strategic-05) 专门修复的一个隐蔽问题: 早期实现里 k=min(N, |peers|) 的静默降级会让 n3..n7 这样的小 N 档在低覆盖年份塌缩成同一个值, 制造出虚假的"N 敏感性稳健"假象; 现在的实现严格要求同行数达标才出值, 覆盖不足即诚实报缺失。由于差异度定义为 1 减余弦相似度且相似度真值域是 [-1, 1], 距离的理论值域相应扩展为 [0, 2](与家族基准 N=5 档及 TF-IDF/LDA 等值域 [0,1] 的其他方法档不同, 是本嵌入类专属的值域扩张; 详见各 VAR 节的值域说明)。

【文献定位】
本家族方法论直接来自 Guzman & Li (2023), 该文用美国企业注册文件的文本相似度构造"创业战略"测度, 核心公式即本家族逐字复刻的 Ŝ_i = (1/N) Σ δ_ij; 本项目把这一测量框架从企业注册文本迁移到银行金科新闻文本, 应用场景不同但转换规则严格对应。构念定位上呼应 Hoberg & Phillips (2016) 开创的文本产业分类范式(TNIC), 二者共享"文本相似度→产品市场/战略定位相似度"的核心识别逻辑, 但 Hoberg & Phillips 用于构造产业分类边界, 本家族用于构造连续型差异度得分。N 值敏感性检验的必要性还可参考 Rodriguez & Spirling (2022, The Journal of Politics) 对应用研究中词嵌入测度有效性的系统讨论——该文指出嵌入模型的具体规格选择(训练语料、维度、相似度截断规则等)会实质影响下游测度的数值稳定性, 因而任何基于嵌入相似度构造的连续测度都应报告对关键规格选择的敏感性证据; 本家族的 N∈{5,10,20,30,40,50} 邻域梯子正是把"改变邻域范围、检验结论是否稳健"这一设计思路落到文本嵌入空间里的具体实现, 与 co-primary 双嵌入引擎、三轨文本梯子共同构成本家族的规格稳健性证据链。研究者在把本家族差异度得分接入结果方程时, 还应留意 Haans(2019, Strategic Management Journal)对"独特性—绩效"关系的提醒: 该文发现文本/属性距离度量的距离-绩效关系并非单调线性, 而是随所处品类的同质/异质程度不同而呈现形态各异的曲线(在高度同质化的品类里适度差异化可能提升绩效, 在本就高度异质化的品类里同样的差异度增量则可能不再有边际效应, 甚至转为负向), 因此在下游回归里对本家族差异度得分(不论 N=5 还是本档 N=50)贸然只设线性项, 有可能掩盖真实存在的非线性/门槛效应; 建议至少以二次项或分档哑变量做形态敏感性检验, 这与本家族既有的 N 值邻域梯子、三轨梯子、双嵌入梯子共同构成对结论稳健性的多重交叉验证。

【口径铁律复述】本家族列同时横跨两条正交梯子: (1) top-k N 邻域梯子(N∈{5,10,20,30,40,50}, F502 固定 N=50 档), (2) 三轨文本梯子(full/ctx/ss)与 co-primary 双轨嵌入梯子(Qwen 主轨/`_lg` text-embedding-3-large 对偶轨)。full/ctx/ss 三轨各自独立成文、就地识别(just-identified)并排, 互为稳健性检验、不分主次, 禁止把三轨证据混入同一个 over-identified Hansen J 检验; Qwen 主轨与 `_lg` 对偶轨同为 co-primary 主测度、互为稳健性, 严格 parity(任一嵌入引擎调用失败或返回形状异常, 同族无后缀列与 `_lg` 列一并置 NaN, 不出现单边孤儿列), 同样禁止混入同一 Hansen J。N=50 与 N∈{5,10,20,30,40} 等其余邻域档也是并排的敏感性臂, 不存在"哪个 N 更权威"的主次关系——研究者应把 N=50 结果与家族 canonical N=5 结果对照报告, 只要方向与显著性在整个 N 梯子上保持稳定, 即构成对"邻域半径选择不驱动结论"的稳健性证据。此外, full 轨遵循 2026-06-29 起生效的留篇门控口径: 是否判定为"一篇银行金科报道"只看 `llm_verified_full`, ctx/ss 轨的行宇宙是 full 留篇集合的子集, 各轨的分子分母均逐轨独立计算, 不借用彼此的分母。

## VAR: strat_diff_n50_emb

【变体差分】
本列是家族在 Qwen 主嵌入轨(`Qwen/Qwen3-Embedding-8B`, 硅基流动 API, 4096 维)上的 full 轨(标题+正文全文)N=50 最近邻差异度得分, 是本家族六列中的锚点列, 也是家族标签体系里带 `(co-primary: Qwen/Qwen3-Embedding-8B)` 对称标注的基准档。计算时以 full 轨文本嵌入构造相似度矩阵, 对每个银行-年度取相似度最高的 50 家同行, 平均其文本距离 δ=1−cos。值域为理论上的 [0, 2](因嵌入余弦可为负, 截断边界是 [-1, 1] 而非 TF-IDF 类方法的 [0, 1])。与家族 canonical 列 `strat_diff_n5_emb`(N=5)相比, 本列把可比同行数从 5 家扩大到 50 家, 平滑效果更强——单个极端相似或极端相异的同行个案对得分的边际影响被摊薄, 得分更接近"该行整体在同行谱系中的平均位置", 但同时也更容易在同行池本身不足 50 家的年份(尤其是样本银行数较少或早期年份)因覆盖不足而整体置为缺失, 这一置缺规则(|peers|<N 直接 NaN, 而非静默取 min(N,|peers|) 降级)是 2026-06-11 修复的隐蔽偏误, 目的是防止小同行池年份出现虚假的"N 敏感性稳健"假象。

在生产环境 T=18(2007-2024)的全量样本下, 早期年份(数据覆盖尚薄的样本初期)出现同行数不足 50 家而置缺的概率显著高于晚期年份, 这意味着 N=50 档的面板在时间维度上并非均匀覆盖——研究者在解读 N=50 档回归结果时应留意样本期是否因缺失而系统性地向晚期年份倾斜, 并与 N=5/N=10 等对该问题不敏感的小邻域档对照, 判断结论是否受这一非随机缺失模式驱动。本机 dev 样本(T=2, 2017-2018, 110 家银行)因跨期只有两年、同行池规模有限, N=50 档大概率整体或大面积置缺, 这一空值模式是预期的规模退化而非代码缺陷, 待生产语料机全量重跑后方能观察 N=50 档的真实覆盖率与数值分布。full 轨与 ctx/ss 轨、Qwen 与 `_lg` 均是并排稳健性臂, 不分主次, 不得混入同一 Hansen J。

## VAR: strat_diff_n50_emb_ctx

【变体差分】
本列与 `strat_diff_n50_emb` 共享 N=50、Qwen 主嵌入引擎, 唯一差分维度是文本轨从 full 切换到 ctx(标题+实体窗口文本, `content_ctx`, 由 stage 14 `ctx_materializer` 物化, 标题经 `prepend_title` 拼接在窗口文本前)。ctx 轨聚焦银行/金科实体周边的窗口文本而非全文, 用意是过滤掉与银行战略定位无关的报道噪声段落(如通稿套话、无关事件铺垫、与实体不直接相关的行业综述段落), 让相似度矩阵更集中反映与目标实体直接相关的叙事内容, 理论上应比 full 轨对无关噪声更稳健, 但代价是可用文本量缩水, 单篇报道对嵌入向量的边际影响相对放大。行宇宙是 full 轨留篇集合的子集(2026-06-29 起生效的 full-only 门控口径——是否判定为"一篇银行金科报道"只看 `llm_verified_full`, ctx 轨降级为 conditional-on-full 的测度/稳健性轨), 若某银行-年度无可用 ctx 窗口文本, 依 stage 14 回退语义按全文 body 兜底并标记 `content_ctx_is_fallback`, 此时该银行-年度在 ctx 轨与 full 轨的嵌入输入实质趋同, 二者差异主要来自后续 N-最近邻聚合时相似度矩阵里其他同行节点是否也发生回退。

由于 N=50 已经是大邻域档, ctx 轨相对 full 轨在样本覆盖上的收缩(fintech_share/attention_pct 等口径收缩效应, 参见 CLAUDE.md「全量17M/T18」与「full-only门控」相关记录)会叠加同行池不足 50 家的置缺规则, 使 `strat_diff_n50_emb_ctx` 成为家族六列中理论上覆盖率最低的一档之一。研究者若观察到 ctx 轨 N=50 档大面积缺失, 应先核对是否为 ctx 窗口文本本身覆盖不足所致, 再核对是否叠加了 N=50 同行池不足的双重收缩, 两者叠加是预期的规模效应而非产生偏误的信号。本列与 full 轨、ss 轨、`_lg` 对偶轨均属并排稳健性臂, 互不构成主次关系, 不得混入同一 over-identified Hansen J。

## VAR: strat_diff_n50_emb_lg

【变体差分】
本列在 N=50、full 轨的基础上, 把嵌入引擎从 Qwen 主轨切换为 co-primary 对偶轨 `text-embedding-3-large`(OpenAI/yunwu API, 3072 维), 是跨厂商 embedding 模型的稳健性验证列, 与 `strat_diff_n50_emb` 同为主测度、互为稳健性、地位对等, 并非"稳健性检验"这一从属措辞所暗示的主次关系——家族标签体系刻意禁止使用"robust/robustness check"这类暗示从属地位的措辞, 而统一标注为对称的 co-primary 关系。计算流程与主轨严格并行(同一份 full 轨文本、同一套 N-最近邻聚合逻辑 `_compute_nn_scores`、同一套 sim_bounds=(-1,1) 截断规则), 唯独嵌入向量来源不同(`_build_embedding_sim_matrix` 以 `_LARGE_SPEC` 配置指向 text-embedding-3-large API 端点)。严格保持 both-or-neither parity: 若 Qwen 主轨或 `_lg` 对偶轨任一嵌入引擎调用失败/返回形状异常, 该银行-年度在两条轨上的 N=50 得分同时置为 NaN, 不会出现只有一边有值的单边孤儿, 这一 parity 守卫由本模块的 `_embed_texts_with_chunk_pooling`/`_build_embedding_sim_matrix` 在现算嵌入时统一执行(与 stage 25 `article_sbert` 各自独立现算, 非共享同一产物)。

由于两款嵌入模型的向量几何(维度、训练语料、归一化方式)不同, `strat_diff_n50_emb` 与 `strat_diff_n50_emb_lg` 的绝对水平不可直接比较——即便二者理论值域都是 [0,2], 具体分布的均值与方差会因模型不同而系统性偏移。研究者应比较两者标准化(z-score)后的效应方向与显著性模式是否一致, 以此判断结论是否依赖特定厂商的嵌入选择, 这正是引入 co-primary 双轨架构(而非仅用单一嵌入模型)的核心动机: 用两个训练语料、参数规模、厂商都不同的商用嵌入模型分别独立估计同一构念, 若结论在两者上都成立, 则可排除"结论只是某个特定嵌入模型的训练偏差产物"这一威胁。

## VAR: strat_diff_n50_emb_lg_ctx

【变体差分】
本列同时叠加两个差分维度: 文本轨=ctx(实体窗口文本)、嵌入引擎=`_lg` co-primary 对偶轨(text-embedding-3-large)。它是 `strat_diff_n50_emb_ctx` 的跨厂商嵌入孪生列, 也是 `strat_diff_n50_emb_lg` 的 ctx 轨孪生列, 处在三轨梯子与双嵌入梯子的交叉格, 是家族六列中信息密度最"窄"的一档——文本量因 ctx 窗口收窄, 邻域范围又因 N=50 放到最大, 两个方向的选择叠加在一起。ctx 轨行宇宙同样是 full 轨留篇集合的子集(full-only 门控), 缺失窗口文本时依镜像语义回退到全文并标记 `content_ctx_is_fallback`; `_lg` 嵌入引擎失败时与 Qwen 主轨同族同轨的 ctx 档一并置 NaN(both-or-neither parity 在 ctx 轨与 full 轨遵循同一套守卫逻辑, 不因轨道切换而放松)。

与家族内其余五列一样, N=50、轨道(full/ctx/ss)、嵌入引擎(Qwen/_lg)三个维度各自独立、就地识别、互为稳健性, 不存在跨维度的加权合成或主次排序; 报告时应与 canonical `strat_diff_n5_emb` 及本列的同轨 Qwen 版本 `strat_diff_n50_emb_ctx`、同引擎 full 轨版本 `strat_diff_n50_emb_lg` 并列对照, 而非单独作为独立结论依据。由于该格叠加了两重收缩因素, 在样本覆盖较薄的年份或早期语料段, 本列出现整体缺失的概率在家族六列中相对较高, 这是预期的规模退化现象, 生产语料机全量重跑(T=18)后覆盖率应显著改善。

## VAR: strat_diff_n50_emb_lg_ss

【变体差分】
本列文本轨=ss(银行∧金科同句共现窗口, `content_ss`), 嵌入引擎=`_lg` co-primary 对偶轨(text-embedding-3-large)。ss 轨的判定口径比 ctx 更严格——要求目标银行实体与金科词汇出现在同一句(±N 句窗口由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1), 而非仅在同一篇报道的宽松实体窗口内; 因此 ss 轨捕捉的是"报道直接把该行与金科话题放在同一叙述单元里"的更强共现信号, 对战略定位叙事的刻画更聚焦, 理论上噪声更小, 但样本覆盖通常比 ctx 更稀疏(能满足严格同句共现的文章篇数天然少于满足宽松实体窗口的篇数)。ss 轨回退语义镜像 ctx 轨: 若某银行-年度没有满足严格同句共现条件的文本, `content_ss` 回退为全文 body, 并以 `content_ss_is_fallback=True` 标记(与 ctx 轨共享同一套 `n_articles` 分母口径, 二者对称降级但不互相借用彼此的行宇宙)。

需特别注意, ss 轨这里的"同句共现"判据(entity_context 模块的逐句共现原语)与 stage 13 `cooccurrence_filter` 的整篇文章级"银行∧金科邻近共现"硬过滤判据是两套不同口径——前者决定 ss 轨文本内容本身的取材范围, 后者决定文章是否进入本项目样本池; 两套判据均基于 `sentence_radius`/窗口半径概念, 但不可混用或互相替代。本列与家族内 `strat_diff_n50_emb_ss`(Qwen 主轨同轨版本)、`strat_diff_n50_emb_lg`(ctx 换 full)、`strat_diff_n50_emb_lg_ctx`(ss 换 ctx)均互为稳健性并排, 各自 just-identified, 禁止混入同一 over-identified Hansen J。

## VAR: strat_diff_n50_emb_ss

【变体差分】
本列是 Qwen 主嵌入轨在 ss 轨(银行∧金科严格同句共现窗口)上的 N=50 差异度得分, 是 `strat_diff_n50_emb`(full 轨)与 `strat_diff_n50_emb_ctx`(实体窗口轨)之外的第三条文本轨稳健性臂, 也是 `strat_diff_n50_emb_lg_ss` 的同轨 Qwen 版本孪生。ss 轨判定原语与 stage 13 共现硬过滤的"整篇文章级"共现判据不同——ss 轨是逐句级的严格同句共现(`entity_context` 模块的同句判据, 扫描单位含标题的第 0 句), 这一区分在项目铁律中被明确标注为"判据后缀 ≠ 三轨文本后缀"的两套不同口径, 不可混淆: 文章能否进入样本池由 stage 13 的整篇邻近共现判据决定, 而 `content_ss` 具体截取哪些句子由本列所用的严格同句判据决定。

行宇宙同样受 full-only 留篇门控约束(2026-06-29 起生效), 是 full 轨留篇集合的子集; 覆盖不足 50 家同行的银行-年度置 NaN, 与家族内其余五列遵循同一置缺规则(2026-06-11 修复的 |peers|<N→NaN 硬性口径)。由于 ss 轨样本天然比 ctx/full 稀疏, 叠加 N=50 大邻域要求同行数达标, 本列在样本覆盖偏薄的年份或银行数较少的子样本中出现整体缺失的风险相对较高, 应与 N=5/N=10 等小邻域档对照解读缺失模式是否合理。本列与家族内 full/ctx 轨及 `_lg` 对偶轨均为并排、互为稳健性、不分主次的稳健性梯子成员, 报告时应联合呈现而非孤立解读。

<!-- rendered-citations:begin -->
Guzman, J., & Li, A. (2023). Measuring Founding Strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Haans, R. F. J. (2019). What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Rodriguez, P. L., & Spirling, A. (2022). Word Embeddings: What Works, What Doesn't, and How to Tell the Difference for Applied Research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162
<!-- rendered-citations:end -->
