---
family_id: F054
columns:
- avg_locus_prob_score_ctx
- avg_locus_prob_score_full
- avg_locus_prob_score_ss
- avg_locus_prob_score_std_ctx
- avg_locus_prob_score_std_full
- avg_locus_prob_score_std_ss
unit: 概率 (无量纲, 均值列 ∈ [0, 1]; std 列为同格内标准差, 非负)
formula: "avg_locus_prob_score = mean_over_models( compute_prob_score_binary(label, conf, positive_class=应用场景) ) on innovation_locus, 文章级; 再 mean/std over articles per (target_bank, year)"
producer: news_process/pipeline/sentiment/tone_llms.py::_aggregate_track (文章级概率分数) ; news_process/pipeline/panel/encode.py (bank-year mean/std over articles 聚合) ; news_process/pipeline/panel/codebook.py (VariableMetadata / _PROB_STD_RANGE 元数据, 不做数值聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (innovation_locus 各模型投票 + 置信度)
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.3386/w33344
  type: wp
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: NBER Working Paper No. 33344
- doi: 10.18653/v1/2024.findings-emnlp.432
  type: journal
  authors: Renze, M.
  year: 2024
  title: "The effect of sampling temperature on problem solving in large language models"
  venue: "Findings of the Association for Computational Linguistics: EMNLP 2024"
  pages_or_artno: 7346-7356
- doi: 10.48550/arXiv.2211.02570
  type: arxiv
  authors: Plank, B.
  year: 2022
  title: "The 'problem' of human label variation: On ground truth in data, modeling and evaluation"
  venue: arXiv
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: Journal of Business Economics
  vol: 87
  issue: 5
  pages_or_artno: 537-580
- doi: 10.1287/isre.1100.0322
  type: journal
  authors: Yoo, Y., Henfridsson, O., & Lyytinen, K.
  year: 2010
  title: "The new organizing logic of digital innovation: An agenda for information systems research"
  venue: Information Systems Research
  vol: 21
  issue: 4
  pages_or_artno: 724-735
- doi: 10.1145/1102351.1102430
  type: journal
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: "Proceedings of the 22nd International Conference on Machine Learning (ICML)"
  pages_or_artno: 625-632
- doi: 10.1016/j.spl.2016.02.012
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2016
  title: "Efficient computation of adjusted p-values for resampling-based stepdown multiple testing"
  venue: Statistics & Probability Letters
  vol: 113
  pages_or_artno: 38-40
- doi: "10.1177/08944393241286471"
  type: journal
  authors: "Törnberg, P."
  year: 2024
  title: "Large Language Models Outperform Expert Coders and Supervised Classifiers at Annotating Political Social Media Messages"
  venue: "Social Science Computer Review"
new_dois:
  - "10.1177/08944393241286471"
---

## CORE

【构念与来源】
本家族刻画的是「银行金融科技报道所描述的创新, 在多大程度上落在应用场景一侧而非底层技术一侧」这一构念的连续概率化测度。它的直接理论出处是 Gomber, Koch, & Siering (2017) 提出的数字金融研究立方体, 该框架把金融科技创新沿「技术底座 — 业务功能 — 服务场景」分层, 明确区分了「底层使能技术」与「面向终端的应用场景」两个创新位点 (locus); Yoo, Henfridsson, & Lyytinen (2010) 的分层模块化数字创新逻辑进一步论证了这两个位点在组织与竞争后果上的差异。构念在本项目的落地是一个二分位点判定: 每篇报道所述创新被判为「底层技术」或「应用场景」, 正类 (positive_class) 取「应用场景」。因此得分越高, 表示该银行当年被报道的金融科技创新越偏向应用场景侧 (面向客户的产品/渠道/体验), 越低则越偏向底层技术侧 (核心系统/算法/基础设施)。这是 P4 (bank_fintech_locus, Gomber 线) 论文的处理构念族。

【方法学与计算】
测度自文章级向面板级两级构造。文章级在 stage 21 (tone_llms) 完成: 三家大模型 (gpt54nano / gemini31 / deepseekv4) 各自独立读同一篇报道, 就 innovation_locus 维给出「底层技术 / 应用场景」标签及其置信度。聚合入口是 `_aggregate_track`, 它先解除 verification 与维度判定的耦合 (单模型即便未通过金科验证也保留自身维度判定), 再对通过验证的模型调用 `compute_prob_score_binary(label, conf, positive_class="应用场景")`, 把「离散标签 + 置信度」直接线性重标记为一个连续概率分数 ∈ [0, 1]: 当模型判定的标签恰为正类 (应用场景) 时取该判定的置信度 conf 本身, 否则取 1 − conf, 即把 verbalized confidence 解读为 P(应用场景 | 该篇报道) 的直接估计, 全程不作任何 logit / log-odds 变换。随后对参与的模型取平均, 得到文章级 `avg_locus_prob_score`。这一置信度重标记概率化的方法学动机是概率校准文献 (Niculescu-Mizil & Caruana, 2005): 相比只用硬多数票, 以置信度加权的概率分数保留了判定强度信息, 使弱信号 (低置信) 与强信号 (高置信) 在下游回归中被区别对待。为使概率分数在多次运行间字节可复现, 三家 LLM 的采样温度一律钉为 0.0, 这与 Renze (2024) 关于采样温度影响大模型判定稳定性的实证一致 — 温度归零把随机性从判定链路中移除, 是本项目 golden 可复现锚的前提之一。文章级分数在 stage 40 按 (target_bank, year) 聚合: 取均值得到 `avg_locus_prob_score{track}` (本家族三条无 std 后缀列), 取组内标准差得到 `avg_locus_prob_score_std{track}` (三条 std 列), 后者刻画同一银行同一年内不同报道在位点判定上的离散度。

【文献定位】
把 LLM 作为标注器为管理学/金融学构造变量, 本身是一条正在成型的方法学路径, Carlson & Burbano (2026) 与 Ludwig, Mullainathan, & Rambachan (2025) 分别从操作指南与应用计量框架两个角度给出了使用规范与告警: 前者强调多模型交叉、置信度留痕与降级口径的必要, 后者给出把 LLM 输出当作带测量误差的回归输入时的识别框架。本家族的三家投票 + 置信度概率化 + full-only 留篇门控设计正是对这些告警的直接回应。判定的不可消除分歧被显式建模而非抹平: Plank (2022) 论证了「人类标注本就存在合理变异, 不存在唯一 ground truth」, 这为本家族保留 std 离散度列 (而非只报均值) 提供了构念依据 — 同一银行同年报道在位点上的分散度本身是有信息的信号, 而非纯噪声。需要说明的是, LLM 三家在本项目中互为稳健性: 三家各自的 per-model 子测度并排为「互为稳健性、不分主次」轨, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 本家族报告的是三家平均后的共识概率, 与情感三家投票、三轨文本、co-primary 双轨嵌入遵循同一条铁律。当位点族与其相邻的 subst (实质性) / collab (协作模式) 概率族一并进入多重检验时, 家族级 p 值调整走 Romano & Wolf (2016) 的 stepdown 重抽样方法, 以控制族错误率。Törnberg (2024, Social Science Computer Review) 实证比较大模型标注与专家人工编码、监督分类器在社会媒体文本标签任务上的表现, 为本家族以三家 LLM 置信度概率化替代人工标注 innovation_locus 的方法学选择提供了最新的同行评议依据。

## VAR: avg_locus_prob_score_full

【变体差分】
本列是家族的 canonical 主轨。full 轨文本 = 标题 prepend + 全文正文 (`content_full`), 覆盖整篇报道, 信息量最全。按 2026-06-29 起的 full-only 留篇门控口径, 一篇报道是否算作「一篇银行金科报道」只看 `llm_verified_full == True`, 因此行宇宙 (进入 bank-year 分母的报道集) 由 full 轨界定, ctx/ss 两轨是 conditional-on-full 的子集测度。本列取该银行当年全部 full-留篇报道的文章级 `avg_locus_prob_score` 的算术平均, 值域 ∈ [0, 1], 越接近 1 表示当年被报道创新越偏应用场景侧。作为 P4 处理构念的主测度, 本列是位点回归的首选 headline; 其 ctx/ss 孪生列与本列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。当某银行某年无 full-留篇的金科报道, 或所有模型对该篇 locus 维均降级/缺席时, 本列取缺失 (NaN) 而非伪零, 以免把「无信息」误编码为「偏底层技术」。就选取本列作 headline 的理由而言, full 轨承载最完整的报道语义, 使位点判定不至于因窗口裁剪而遗漏关键的技术/场景信号; 同时留篇门控就锚在 full 轨, 二者口径一致, 避免了「以窄轨门控、以宽轨计值」造成的分母/分子错配。方法学上, 本列的置信度概率化取自三家模型平均, 遵循 Carlson & Burbano (2026) 关于多模型交叉标注以抑制单模型系统性偏误的建议; 温度归零 (Renze, 2024) 则保证同一篇报道在重放时给出字节一致的概率分数, 是本列可复现的前提。使用者应把本列理解为「应用场景侧的连续暴露强度」而非硬分类占比: 它对判定强度敏感, 一篇高置信「应用场景」报道与一篇勉强过线的报道对均值的贡献是有区别的。

## VAR: avg_locus_prob_score_ctx

【变体差分】
本列是 ctx (实体上下文窗) 轨的稳健性孪生。ctx 文本 = 标题 prepend + 银行/金科实体命中位置的上下文窗口 (`content_ctx`), 在 stage 14 物化, 相比 full 轨剔除了与目标实体无邻近关系的段落, 意在削弱长文里离题内容对位点判定的稀释。计算口径与 full 列完全同构: 三家模型对 ctx 文本给出 innovation_locus 判定, 置信度概率化取模型平均得文章级分数, 再按 (target_bank, year) 取均值。关键差分在于本列是 conditional-on-full 测度 — 行宇宙仍是 full 留篇集的子集, 门控由 full 轨界定, 本列只在该子集上 per-track 重算位点概率, 不自立留篇门控。本列与 full/ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。当某篇无有效实体上下文窗时 `content_ctx` 走 fallback (镜像其 is_fallback 语义), 对应文章级分数按缺列跳轨处理而不借 full 轨分母。dev 阶段 T=2 上 ctx 轨可能出现零方差退化, 属预期, 生产 T=18 正常。本列的诊断价值在于与 full 列对照: 若 full 与 ctx 两列的位点水平一致, 说明位点判定稳健于是否裁剪离题段落; 若二者显著背离, 则提示长文中的非实体语境正在系统性地拉动位点判定, 这类背离本身是位点测度可信度的有用信号。需强调 ctx 并非「更好」的轨, 只是「更聚焦」的轨 — 收窄语境同时也会丢失部分交代创新背景的铺陈, 因此项目刻意让 full/ctx/ss 三轨并存而非择一, 三者不分主次地互为稳健性。文本物化端, ctx 的实体命中判定采用银行侧 (否定 + 短名过滤) 与金科侧 (裸 AC 词典) 的不对称口径, 与 full 轨共享同一套 prepend_title 规则, 唯一差异是保留哪些段落进入模型输入, 从而保证 full 与 ctx 的可比性建立在同一标题通道之上。

## VAR: avg_locus_prob_score_ss

【变体差分】
本列是 ss (同句共现窗) 轨的稳健性孪生, 是三轨中信息最窄、最保守的一条。ss 文本 = 标题 prepend + 「银行 ∧ 金科同句 ±N 窗」共现句 (`content_ss`, N 由 filtering.yaml 的 ss_sentence_radius 定, 默认 1), 只保留银行与金融科技在同一句 (及邻句窗) 共现的片段, 意在把位点判定收敛到银行确实与金科并置发生的语境。回退语义镜像 ctx: 当某篇不存在银行 ∧ 金科同句共现时, `content_ss` 回退为全文 body 且 ss_is_fallback=True, 与 ctx 轨共享 `n_articles` 分母口径; 若 FINTECH_AC=None 则 is_fallback 全 True 优雅降级。文章级/面板级计算与 full/ctx 同构 (三家模型概率化取均值, 再 bank-year 取均值)。本列是 conditional-on-full 测度, 行宇宙为 full 留篇集子集, 不自立门控。三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。T=2 上 ss 轨易零方差退化属预期, 生产 T=18 正常。ss 轨在三轨中提供最严格的构念保守性: 它只在银行与金融科技确实同句并置时才据以判定位点, 因此对「报道虽同时提及银行与金科但二者并无实质关联」的伪共现最不敏感, 可作为 full/ctx 结论对语境宽度稳健性的最强检验。代价是信息最窄、回退触发最频繁, 当同句共现稀少时本列大量退回全文, 判定分布向 full 轨收敛, 这一点在解读 ss 与 full 高度相关时须留意 (相关性可能部分由回退共享文本驱动而非独立判定)。项目对 ss 的定位始终是稳健性轨而非主轨, 主 headline 恒为 full 列; 三轨各自 just-identified 并排、不分主次的口径确保任一轨的结论都不被单独提升为因果主张的唯一依据。

## VAR: avg_locus_prob_score_std_full

【变体差分】
本列是 full 轨的组内离散度伴随列, 不是位点水平而是位点判定的分散度。计算 = 对某银行某年全部 full-留篇报道的文章级 `avg_locus_prob_score` 取组内标准差 (std over articles per (target_bank, year)), 值为非负, 落在概率标准差的有界区间内 (由 codebook 的 _PROB_STD_RANGE 约束)。它回答「该行当年被报道的创新在位点上是否众口一致」: 接近 0 表示当年报道高度一致地指向同一位点侧, 偏大表示报道在应用场景与底层技术之间分歧显著。这一离散度列的构念合法性来自 Plank (2022) 关于标注变异本身携带信息的论证 — 分散度不是均值的噪声残渣, 而是可独立进入回归的信号 (如刻画创新叙事的模糊度/争议度)。本列与其 ctx/ss 的 std 孪生列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。单篇报道格 (n=1) 的 std 依 pandas 口径为 NaN (无组内变异可算), 属预期而非缺陷; dev T=2 稀疏格上大量 std 取 NaN 亦属预期退化。就使用而言, 本列可与均值列 (avg_locus_prob_score_full) 配对进入回归以区分「位点水平」与「位点共识」两个独立维度: 两家银行可能有相同的位点均值但迥异的年内分歧, 前者对应「创新叙事一致地偏某侧」, 后者对应「报道莫衷一是」, 二者对下游财务/创新后果的含义并不相同。方法学上, 概率标准差的有界性来自其输入是 [0,1] 概率而非无界打分, 因此本列不会出现重尾, 亦无需 winsorize; 但因分母敏感 (报道少的格 std 极不稳定), 建议在回归中配合报道数控制或对 n 施加下限掩码, 以免小样本格的偶发离散度主导识别。本列与 ctx/ss 的 std 孪生共同构成离散度的三轨稳健性组, 结论不应由任一轨单独驱动。

## VAR: avg_locus_prob_score_std_ctx

【变体差分】
本列是 ctx 轨的组内离散度伴随列, 与 full 的 std 列同构, 差分仅在底层文本轨为 ctx (标题 prepend + 实体上下文窗, `content_ctx`)。计算 = 对该银行当年 ctx 轨文章级 locus 概率取组内标准差, 度量在「只看实体邻近上下文」时报道位点判定的年内分散度。相对 full 的 std, 本列剥离了离题段落对判定的干扰后再看分歧, 因此若 full-std 大而 ctx-std 小, 可提示「分歧主要来自长文里的离题内容而非核心语境」, 是一条有诊断价值的稳健性对照。本列同为 conditional-on-full 测度 (行宇宙 = full 留篇集子集), 缺列/fallback 篇按跳轨处理不借 full 分母。与 full/ss 的 std 孪生互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。单篇格 std=NaN、T=2 稀疏格大量 NaN 与 ctx 轨零方差退化均属预期, 生产 T=18 正常。本列与 full-std 的对照具体化了「分歧来源」的分层诊断: full-std 度量含离题段落时的年内分歧, ctx-std 度量剥离离题后仅看实体语境的分歧, 两者之差可近似归因于长文非核心内容对位点判定的扰动。若研究关注的是「银行金科叙事在核心语境下是否统一」, ctx-std 是比 full-std 更贴合的操作化。与均值列的用法一致, 本列宜与 avg_locus_prob_score_ctx 配对进入模型以分离水平与共识两维。因 ctx 轨报道子集可能小于 full (fallback 篇跳轨), 本列在稀疏格上的 NaN 频率通常高于 full-std, 使用时对有效 n 的掩码尤须谨慎。三条 std 列各自 just-identified 并排、互为稳健性, 禁混进同一 over-identified Hansen J。

## VAR: avg_locus_prob_score_std_ss

【变体差分】
本列是 ss 轨的组内离散度伴随列, 三条 std 列中语境最窄的一条, 差分仅在底层文本轨为 ss (标题 prepend + 银行 ∧ 金科同句共现窗, `content_ss`)。计算 = 对该银行当年 ss 轨文章级 locus 概率取组内标准差, 度量在「只看银行与金科真正并置的同句语境」时位点判定的年内分散度。因 ss 文本最窄, 判定分歧更受共现句本身表述强度驱动; 其回退语义镜像 ctx (无同句共现则退全文 body 且 ss_is_fallback=True, 共享 n_articles 分母)。本列同为 conditional-on-full 测度, 行宇宙为 full 留篇集子集, 不自立门控, 缺列篇跳轨不借 full 分母。与 full/ctx 的 std 孪生列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。单篇格 std=NaN 属 pandas 口径预期; T=2 上 ss 轨零方差/大量 NaN 退化属预期, 生产 T=18 正常。作为三轨离散度组中语境最窄的一条, 本列度量的是「仅在银行与金科真正同句并置的表述里, 年内位点判定的分散度」, 因而对伪共现最不敏感, 可视为位点共识稳健性的最保守检验。须留意 ss 轨的高回退率会让本列在同句共现稀少的银行-年上向 full-std 收敛, 这种收敛部分由共享回退文本驱动而非独立判定, 解读 ss-std 与 full-std 的相关时应扣除这一机制。与均值列一样, 本列宜与 avg_locus_prob_score_ss 配对使用以分离位点水平与共识。方法学与 full/ctx 的 std 列完全同构 (组内标准差、有界非负、单篇格 NaN、小样本格不稳定需 n 掩码)。本列绝非「更权威」的离散度轨, 仅是「更保守」的一条, 主 headline 恒锚 full 轨。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. NBER Working Paper No. 33344 [Working Paper]. https://doi.org/10.3386/w33344
Renze, M. (2024). The effect of sampling temperature on problem solving in large language models. Findings of the Association for Computational Linguistics: EMNLP 2024, 7346-7356. https://doi.org/10.18653/v1/2024.findings-emnlp.432
Plank, B. (2022). The 'problem' of human label variation: On ground truth in data, modeling and evaluation. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2211.02570
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Yoo, Y., Henfridsson, O., & Lyytinen, K. (2010). The new organizing logic of digital innovation: An agenda for information systems research. Information Systems Research, 21(4), 724-735. https://doi.org/10.1287/isre.1100.0322
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML), 625-632. https://doi.org/10.1145/1102351.1102430
Romano, J. P., & Wolf, M. (2016). Efficient computation of adjusted p-values for resampling-based stepdown multiple testing. Statistics & Probability Letters, 113, 38-40. https://doi.org/10.1016/j.spl.2016.02.012
Törnberg, P. (2024). Large Language Models Outperform Expert Coders and Supervised Classifiers at Annotating Political Social Media Messages. Social Science Computer Review. https://doi.org/10.1177/08944393241286471
<!-- rendered-citations:end -->
