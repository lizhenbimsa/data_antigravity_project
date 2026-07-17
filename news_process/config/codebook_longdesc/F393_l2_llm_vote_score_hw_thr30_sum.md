---
family_id: F393
columns:
- llm_vote_score_hw_thr30_sum_ctx
- llm_vote_score_hw_thr30_sum_full
- llm_vote_score_hw_thr30_sum_ss
unit: 无量纲加权得分之和 (银行-年内文章级离散投票语调 × 跟风衰减权重 的求和; 非比率, 未除以权重和)
formula: 'llm_vote_score_hw_thr30_sum{track} = Σ_i∈(bank,year) [ llm_vote_score{track}_i × herd_weight{track}_i(τ=0.30) ], 其中 llm_vote_score∈{-1,0,1} 为三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票离散语调 (Int8, 无效行传播为 <NA>)、herd_weight(τ=0.30) 为 stage 24 在相似度阈值 τ=0.30 下算出的跟风衰减权重 (与银行-年内文章互文相似度挂钩, 越像"抄稿"权重越低); 求和聚合发生在 pipeline/panel/encode.py 的 build_aggregation_dict (agg[f"llm_vote_score_hw_{tag}_sum{track}"]=(f"llm_vote_score_hw_{tag}{track}","sum")), 分子来源列由 pipeline/panel/runner.py 步骤 3d-2 预乘 (sens_cols[f"llm_vote_score_hw_thr30{track}"]=df[f"llm_vote_score{track}"]*hw_t)。'
producer: pipeline\panel\encode.py ; pipeline\panel\runner.py ; pipeline\sentiment\herd_decay.py ; core\config.py::herd_sensitivity_grid
upstream:
- 21_tone_llms
- 24_herd_decay_processor
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization'
  venue: arXiv
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and Domain Specificity: A Chinese Financial Sentiment Dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: "10.1017/psrm.2024.64"
  type: "journal"
  authors: "Ornstein, J. T., Blasingame, E. N., & Truscott, J. S."
  year: 2025
  title: "How to train your stochastic parrot: large language models for political texts"
  venue: "Political Science Research and Methods"
  vol: "13"
  issue: "2"
  pages_or_artno: "264-281"
- doi: "10.18653/v1/2025.findings-acl.744"
  type: "journal"
  authors: "Wang, W., Wang, Y., & Huang, H."
  year: 2025
  title: "Ranked Voting based Self-Consistency of Large Language Models"
  venue: "Findings of the Association for Computational Linguistics: ACL 2025"
  pages_or_artno: "14410-14426"
- doi: "10.18653/v1/2024.law-1.13"
  type: "journal"
  authors: "Rønningstad, E., Velldal, E., & Øvrelid, L."
  year: 2024
  title: "A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation"
  venue: "Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII)"
  pages_or_artno: "133-139"
- doi: "10.48550/arxiv.2407.17866"
  type: "arxiv"
  authors: "Kim, A., Muhn, M., & Nikolaev, V."
  year: 2024
  title: "Financial Statement Analysis with Large Language Models"
  venue: "arXiv"
new_dois: []
---

## CORE

【构念与来源】
本家族的三个列 (`llm_vote_score_hw_thr30_sum_full` / `_ctx` / `_ss`) 度量的是"某银行在某年度全部相关报道中, 经跟风衰减折算后的离散投票语调加权和" —— 一个未除以权重和的原始累加量, 而非可直接读作"平均语调"的比率。它坐落在情感三法之首的 LLM 投票法内部, 与相邻的 `llm_vote_cont_hw_thr{NN}_sum{track}` 族 (F386/F387 等) 是同一敏感性网格上的姊妹族, 但分子取的是三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票产出的离散语调 `llm_vote_score{track}∈{-1,0,1}`, 而非再乘以三家一致度 `llm_agreement_rate{track}` 得到的连续版本 `llm_vote_cont{track}`。换句话说, "score" 支线只在乎多数票落在正/负/中性哪一档, 不区分"三家全票一致的强判断"与"两票对一票的弱判断"; "cont" 支线才把一致度纳入权重打折。二者互为稳健性的一组构念平行分支——若主结论在离散 score 与连续 cont 两支上均稳健, 说明结论不依赖是否纳入投票分歧程度这一建模选择。求和的第二个乘数是 stage 24 (herd_decay_processor) 在阈值敏感性网格里 τ=0.30 一档算出的跟风衰减权重 `herd_weight{track}_thr30`。白话讲: 一家银行一年若有 10 篇相关报道, 每篇先按三家 LLM 多数投票打出一个 -1/0/1 的语调分 (不打折, 不管三家吵得多凶), 再看这篇报道和同一银行-年内其它报道有多像通稿——如果相似度超过 0.30 这一 (相对宽松/易触发) 门槛, 这篇报道对本年度语调的贡献就被压低; 把 10 篇折算后的分数直接加起来, 就是这个 "sum" 列的值。它本身不是最终用于回归的语调指标——真正进回归的是同名 "tone" 比率列 `llm_vote_tone_hw_thr30{track}` (该 sum 列除以对应的加权分母 `sum_wd_hw_thr30_llm{track}`, 分母走 LLM 族专用的 valid-mask 口径以避免向零系统性衰减)——但这个 sum 列作为分子中间量本身入面板, 供审计、诊断加权和的规模/覆盖度, 也供研究者自行按替代分母重构比率。

跟风衰减权重的构念动机是: 中国财经新闻生态里存在大量转载/通稿现象 (同一篇通稿被多家媒体几乎逐字转发), 若不加处理地把这些高度重复的报道各自计一票, 会让"多家媒体一致唱多/唱空"这个表面信号实为"一篇通稿被复制了 N 次"的假象, 系统性放大某些银行-年的语调极性并制造伪聚集。跟风衰减机制 (stage 24) 通过篇章间文本相似度判定一篇报道与同一银行-年窗口内其它报道的"抄稿"程度, 相似度越高、权重越低, 从而把重复转载对语调聚合的贡献做衰减而非简单计数。这一逻辑呼应 Tetlock (2007) 关于媒体语调作为投资者情绪代理指标须警惕"同质化噪音"膨胀统计显著性的告诫, 也与财经文本分析文献里"文本样本非独立" (转载/联合署名/通稿) 是语调测度的常见污染源这一共识一致。τ=0.30 相对生产基线 τ=0.35 更宽松地判定"相似即抄稿"(阈值更低意味着更容易触发降权), 因此在其它条件相同时, 同一批文章在 τ=0.30 档下的加权和整体上更容易被压低, 这正是敏感性网格设计的目的——覆盖"判定门槛偏松"与"判定门槛偏紧"两端, 用以检验主回归结论不被 0.35 这一具体取值单独驱动。

【方法学与计算】
计算链条分三段, 严格分布在三处 producer 代码里。第一段在 stage 21 (LLM 投票): 三家 LLM 各自对文章-轨给出情感标签, 经多数投票产出 `llm_sentiment{track}` 与一致度 `llm_agreement_rate{track}`, 再由 `encode.py` 的 SENTIMENT_MAP 把标签映射为离散 `llm_vote_score{track}∈{-1,0,1}` (Int8, 无效行传播为 `<NA>`)。第二段在 stage 24 (herd_decay_processor): 除生产口径 τ=0.35 (`herd_detection.similarity_threshold`) 外, 按 `herd_detection.sensitivity_thresholds` (默认 `[0.25, 0.30, 0.40, 0.45]`) 网格额外产出逐 τ 的 `herd_weight{track}_thr{NN}` 列 (SSOT = `core.config.herd_sensitivity_grid`, 列名后缀规则 `thr{round(τ*100):02d}`, 0.30 → `thr30`); τ 越小意味着判定"抄稿"的门槛越紧 (文章间只需较低相似度即触发降权), 权重整体更偏离 1 (更接近强衰减); τ=0.30 是网格中仅次于最紧 τ=0.25 的第二紧档位。第三段在 `pipeline/panel/runner.py` 步骤 3d-2 (阈值敏感性 HW 加权列预计算): 对每个 τ 档、每条轨道, 用 `herd_weight{track}_thr30.fillna(1.0)` (缺权重优雅回退为 1, 即不衰减) 逐篇相乘 `llm_vote_score{track} × hw_t` 得到文章级 `llm_vote_score_hw_thr30{track}`, 随后在 `pipeline/panel/encode.py` 的聚合字典里对每个银行-年做 `groupby(...).agg('sum')`, 落成本家族的 `llm_vote_score_hw_thr30_sum{track}` 面板列。该求和是"物理域求和" (Σ over 全部有效文章), 与之配套的分母诊断列是 `sum_herd_weight{track}_thr30` (权重本身求和) 与 LLM 族专用的 valid-mask 分母 `sum_wd_hw_thr30_llm{track}` (仅累加"LLM 有效判断"的那些文章的权重, 修正 encode-01 缺陷——若用物理分母除, 会把"LLM 未给出判断"的文章按语调 0 计入分母, 系统性把加权语调拉向 0); 面板内真正拿来做回归 DV 的比率列 `llm_vote_tone_hw_thr30{track}` = `llm_vote_score_hw_thr30_sum{track} / sum_wd_hw_thr30_llm{track}` 的匹配版本, 不是简单除以 `sum_herd_weight`。理解这一点很重要: 本家族三列作为分子中间量, 天然会随"该银行-年报道量"与"跟风衰减压低程度"两个因素共同波动, 不能脱离分母单独解释为"平均语调水平"。

【文献定位】
LLM 多数投票 (三厂商 gpt54nano/gemini31/deepseekv4 独立打标签取共识) 的设计呼应 Kamen & Kamen (2025) 关于集成多个 LLM 标注器可显著降低单一模型系统性偏差、提升内容分类稳健性的发现; de Kok (2025, *Management Science*) 系统讨论了生成式 LLM 用于会计/金融文本分析时 temperature=0、prompt 版本冻结、结果可复现等方法论要求, 本项目 stage 21 的 prompt v8 字节级冻结缓存架构与之一致。跟风衰减对"重复/转载文本膨胀语调信号"的警惕呼应 Tetlock (2007, *Journal of Finance*) 关于媒体文本作为市场情绪代理指标须处理样本非独立性的经典论述。中文财经情感测度这一底层任务的方法论谱系参照 Du, Huang, Wermers & Wu (2022, *Review of Finance*) 关于中文金融情感词典构建的领域特定性讨论 (该文亦是本项目 `tone_words` 词典/政治词权重族的核心方法学锚点, 二者在"中文财经文本情感如何被系统性度量"这一更宏观构念上与本 LLM 投票族互为方法学三角验证的一支)。

τ=0.30 只是敏感性网格中的一档, 与 τ∈{0.25, 0.40, 0.45} 及生产基线 τ=0.35 (对应无 `_thrNN` 后缀的 canonical `llm_vote_score_hw_sum{track}` 家族) 共同构成一条"跟风判定门槛松紧梯子"; 依据 CLAUDE.md「当前状态铁律」的梯子铁律, 该网格内各档 (含基线) 各自 just-identified 并排、互为稳健性、不分主次, 用于证明主回归结论不依赖 0.35 这一具体相似度门槛的取值, 严禁把不同 τ 档的加权测度同时塞进同一个 over-identified 的 Hansen J 检验。三条轨道 (full/ctx/ss) 同理各自 just-identified 并排、互为稳健性、不分主次: full=标题+全文, ctx=标题+银行实体窗口, ss=标题+银行∧金科同句±N窗; 三轨与阈值梯子是两条相互独立、不交叉的稳健性维度, 而"score 支线 vs cont 支线"(是否纳入三家一致度打折) 则是第三条相互独立的稳健性维度。留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否被判定为"有效的银行-金科报道"只看 `llm_verified_full`, ctx/ss 轨的行宇宙是 full 留篇集合的子集, 分轨各自算量; ss 轨若一篇文章内不存在银行与金科词的同句共现, 依镜像 ctx 的回退语义, `content_ss` 退化为全文 body 且 `ss_is_fallback=True`, 该篇仍计入 `n_articles` 分母、但其 ss 轨情感度量与 full 轨在数值上趋同 (因文本来源相同)。 在"逐篇取 LLM 标签、再按银行-年聚合"这一测量链路本身的方法学谱系上, 本族尚可锚定至几项近年前沿工作。Ornstein、Blasingame 与 Truscott (2025) 以 few-shot prompt 在情感分析、文档标度、主题建模等政治学文本即数据任务上做预注册评估, 结论是该做法优于传统有监督学习基线, 并以极低成本达到与专家及众包编码员相当 (而非超过) 的水平, 是本族分子"文章级 LLM 标签 → 分组求和"链路在社会科学中的同族先例; 其语料为英文政治文本、采用单一模型而非三家投票, 亦无跟风衰减加权、bank-year 面板聚合与三轨切分, 迁移时须作此保留。Wang、Wang 与 Huang (2025) 以排序投票 (ranked voting) 替代朴素多数票来聚合 LLM 的多个候选输出并实证其聚合质量提升, 提示本族分子所依赖的多数票并非唯一可选规则、投票规则本身即一重设计自由度; 但其投票单元是同一模型多次采样得到的候选答案 (self-consistency), 而非跨三家厂商的标签票, 任务为推理生成而非三分类情感, 本项目仍维持朴素多数票、未采纳排序投票。Rønningstad 与 Velldal (2024) 评估 LLM 对特定目标实体的情感 (entity-level sentiment) 标注质量并与人工标注对比, 与本族"针对目标银行而非篇章整体"的语调构念直接同族; 其语料为挪威语/英语通用新闻与评论、目标实体非银行, 采用单一 GPT 模型且仅报告标注一致性, 不涉及跟风衰减权重与银行-年求和。Kim、Muhn 与 Nikolaev (2024) 向 GPT-4 提供刻意剥离叙事与行业信息的标准化财务报表, 令其判断企业未来盈余的变动方向, 实证其方向性预测准确率超过人类分析师、与窄训练的 SOTA 机器学习模型相当, 并据以构建出更高 Sharpe 比率的策略, 为"令 LLM 作离散方向性判断、再把该判断当作可聚合的金融信号"提供了金融领域的前沿存在性证明; 其输入为报表数字而非中文新闻叙事, 单位为公司-季度盈余方向而非银行-年语调, 且为单模型无跨厂商投票, 与本族仅在范式层面同族。需要说明的是, 上述四文均只锚定本族分子的"离散标签"一环, 对 τ 门槛下的跟风衰减权重与阈值梯子不构成任何依据 — 后者的动机依旧由 Tetlock (2007) 一线承担, 门槛取值本身是研究者选择。
## VAR: llm_vote_score_hw_thr30_sum_ctx

【变体差分】
本列是家族在 ctx 轨 (标题 + 银行实体上下文窗口) 上的实现: 求和的分子文章级来源是 `llm_vote_score_ctx` (三家 LLM 在 ctx 轨文本上独立打标签、多数投票后的离散编码, 不折算一致度), 权重来源是 stage 24 在 ctx 轨文本上、τ=0.30 门槛下算出的 `herd_weight_ctx_thr30` (与 full 轨的跟风判定是独立计算的一条相似度矩阵——ctx 轨文本更短、聚焦银行实体窗口, 两篇报道在 ctx 轨下的相似度不必然等于其在 full 轨下的相似度, 因此 ctx 轨的"抄稿"判定与衰减权重是 full 轨的一份独立稳健性复核, 不是 full 轨权重的重新标注)。该列的行宇宙遵循 2026-06-29 起的 full-only 留篇门控: 一篇文章是否计入求和取决于其 `llm_verified_full` 是否为真, ctx 轨仅在 full 轨判定该篇有效的前提下才纳入 ctx 轨自身的语调与权重计算, 因此 ctx 轨的样本行宇宙是 full 留篇集合的子集, 度量本身 (语调值、跟风相似度) 仍完全基于 ctx 轨自身的文本与三家 LLM 独立判断算出、不借用 full 轨的数值。与本家族的 `_full`/`_ss` 两个同胞列相比, ctx 轨、τ=0.30 门槛下的这一列在跟风衰减铁律下与二者各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨或跨 τ 档混入同一个 over-identified Hansen J 检验框架; 同一轨道下, 本列与 cont 支线的 `llm_vote_cont_hw_thr30_ctx` 亦各自 just-identified 并排、不混入同一检验。若某银行-年在 ctx 轨完全没有可用的 herd_weight 权重列 (旧 schema 单轨 legacy 退化场景), 该列在 runner.py 步骤 3d-2 中会因源列缺失而被整体跳过, 相应银行-年在该列上呈缺失而非置零。

## VAR: llm_vote_score_hw_thr30_sum_full

【变体差分】
本列是家族在 full 轨 (标题 + 全文正文, 三轨中样本覆盖最广、也是 P1 主线论文 treatment 变量 `llm_vote_tone_full` 所在轨道) 上的实现, 是三个同胞列里唯一直接对应该论文主处理变量所在轨道口径的一支。求和分子是 `llm_vote_score_full` (三家 LLM 多数投票的离散语调, 不含一致度折算), 权重是 stage 24 在 full 轨文本 (完整正文) 上、τ=0.30 门槛下算出的 `herd_weight_full_thr30`。full 轨也是留篇门控本身的判定轨道: 2026-06-29 起, 一篇报道是否被算作"一篇银行-金科相关报道"完全由 `llm_verified_full == True` 决定, 因此本列 (及其分母诊断列 `sum_wd_hw_thr30_llm_full`) 的行宇宙即是该银行-年全体留篇文章的直接求和, 不存在"借用其它轨道判定再筛子集"的问题——ctx/ss 两个同胞列反而是以本列的判定结果为门控前提。需要强调: 本列本身是 τ=0.30 敏感性梯子上的一档, 与生产基线口径 τ=0.35 对应的 canonical 列 `llm_vote_score_hw_sum_full` (无 `_thrNN` 后缀) 不是同一构念的两种写法, 而是"同一构念、不同跟风判定松紧度"下各自独立算出的稳健性复核档位; 依梯子铁律, τ=0.30 档与 τ∈{0.25,0.35(基线),0.40,0.45} 其余各档各自 just-identified 并排、互为稳健性、不分主次, 用于证明主回归结论 (尤其涉及 P1 论文 `llm_vote_tone_full` 或其 HW 加权稳健性版本的结论) 不依赖 0.35 这一具体相似度阈值取值, 禁止把不同 τ 档的加权测度同时纳入同一个 over-identified Hansen J 检验矩阵; 与本列同轨的 cont 支线 `llm_vote_cont_hw_thr30_full` 亦是独立的第三条稳健性维度, 二者不应合并进同一识别方程。

## VAR: llm_vote_score_hw_thr30_sum_ss

【变体差分】
本列是家族在 ss 轨 (标题 + 银行∧金科同句±N窗, 三轨中判定条件最严格) 上的实现: 求和分子是 `llm_vote_score_ss` (三家 LLM 在 ss 轨文本上独立打标签、多数投票后的离散编码), 权重是 stage 24 在 ss 轨文本上、τ=0.30 门槛下算出的 `herd_weight_ss_thr30`。ss 轨的回退语义严格镜像 ctx 轨: 若一篇文章不存在银行与金科关键词的同句 (或 ±N 句窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 共现, `content_ss` 退化为全文 body 且 `ss_is_fallback=True`, 该篇仍计入分母、但其 ss 轨情感/跟风判定实质上是在与 full 轨相同的文本上重新独立跑一遍 LLM 与相似度计算——因此回退状态下的 ss 轨语调与跟风权重在数值上会趋近于 full 轨、但不是同一份计算结果的复制, 三家 LLM 与相似度矩阵仍各自独立求值。行宇宙同样遵循 full-only 留篇门控 (只有 `llm_verified_full` 为真的银行-年报道才纳入 ss 轨求和), 与 ctx 轨互为同一门控约束下的姊妹稳健轨, 二者行宇宙相同 (均为 full 留篇集合的子集) 但各自度量值 (语调与跟风相似度) 独立算出, 互不借用彼此数值。与 `_full`/`_ctx` 两列一样, 本列作为 τ=0.30 敏感性梯子上 ss 轨的一档, 与其余 τ 档、以及 ss 轨自身在 canonical τ=0.35 基线下的 `llm_vote_score_hw_sum_ss` 各自 just-identified 并排、互为稳健性、不分主次, 三轨 × 敏感性梯子 × score/cont 支线三个维度相互正交、不交叉, 均不得混入同一个 over-identified Hansen J 检验。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kamen, A., & Kamen, Y. (2025). Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Ornstein, J. T., Blasingame, E. N., & Truscott, J. S. (2025). How to train your stochastic parrot: large language models for political texts. Political Science Research and Methods, 13(2), 264-281. https://doi.org/10.1017/psrm.2024.64
Wang, W., Wang, Y., & Huang, H. (2025). Ranked Voting based Self-Consistency of Large Language Models. Findings of the Association for Computational Linguistics: ACL 2025, 14410-14426. https://doi.org/10.18653/v1/2025.findings-acl.744
Rønningstad, E., Velldal, E., & Øvrelid, L. (2024). A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation. Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII), 133-139. https://doi.org/10.18653/v1/2024.law-1.13
Kim, A., Muhn, M., & Nikolaev, V. (2024). Financial Statement Analysis with Large Language Models. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2407.17866
<!-- rendered-citations:end -->
