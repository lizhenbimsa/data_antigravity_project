---
family_id: F395
columns:
- llm_vote_score_hw_thr45_sum_ctx
- llm_vote_score_hw_thr45_sum_full
- llm_vote_score_hw_thr45_sum_ss
unit: 无量纲加权得分之和 (银行-年层面, 由篇级 {-1,0,+1} 语调票乘以跟风衰减权重后逐篇求和; 本身非比率, 需再除以有效篇加权和才得语调均值)
formula: 'llm_vote_score_hw_thr45_sum{track} = Σ_i∈(target_bank,year) [ llm_vote_score{track}_i × herd_weight{track}_thr45_i ], track ∈ {full, ctx, ss}; 其中 herd_weight{track}_thr45_i 由 stage 24 (pipeline/sentiment/herd_decay.py) 在相似度阈值 τ=0.45 (而非生产基线 τ=0.35) 下, 对与文章 i 同银行同轨文本相似度 ≥ τ 的"跟风稿"做衰减降权后得到; llm_vote_score{track}_i ∈ {-1, 0, +1} 为三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票语调; 本列是 pipeline/panel/encode.py::build_aggregation_dict 里 agg[f"llm_vote_score_hw_{tag}_sum{track}"] = (f"llm_vote_score_hw_{tag}{track}", "sum") 的分子中间列 (tag="thr45"), 面板下游再除以配套分母列 sum_wd_hw_thr45_llm{track} 得到最终比率 llm_vote_tone_hw_thr45{track}'
producer: pipeline\panel\encode.py::build_aggregation_dict (加权求和聚合定义) ; pipeline\panel\runner.py (步骤 3d, 逐篇预计算 llm_vote_score_hw_thr45{track} 与配套 valid-mask 权重列) ; pipeline\sentiment\herd_decay.py (stage 24, 在 τ=0.45 下产出 herd_weight{track}_thr45 篇级权重) ; core\config.py::herd_sensitivity_grid (τ 网格与 tag 编码单一事实源)
upstream: [21_tone_llms, 24_herd_decay]
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving Content to Investor Sentiment: The Role of Media in the Stock Market"
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A.; Kamen, Y.
  year: 2025
  title: 'Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization'
  venue: arXiv
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating Large Language Model Annotations
  venue: Federal Reserve Board FEDS Working Paper
  pages_or_artno: '2026-020'
new_dois: []
---

## CORE

【构念与来源】
本家族属于"跟风衰减加权语调"(herd-decay-weighted tone) 测度族在阈值敏感性维度上的一个具体取值分支: τ=0.45。管道对银行报道做语调加权聚合时, 面对的问题是同一篇原创报道常被多家媒体转发或改写转载, 若不加处理直接对篇级语调取算术平均, 会让被大量转发的稿件在银行-年语调均值里获得远超其信息含量的权重, 造成系统性的"跟风偏误"(herding bias)。这一构念直接呼应 Tetlock (2007) 对媒体报道与股票收益关系的经典发现: 媒体文本的信息含量与其独立性密切相关, 高度雷同、彼此转发的报道不构成独立信息增量。管道的应对方式是: 先在 stage 24 (`pipeline/sentiment/herd_decay.py`) 对同一银行同一文本轨 (full/ctx/ss) 内的文章两两计算文本相似度, 对相似度超过某一阈值 τ 的"疑似跟风稿"按其相似程度做衰减降权 (权重随相似度升高而单调下降, 而非简单丢弃), 得到篇级权重列 `herd_weight{track}` (基线 τ=0.35) 及其阈值敏感性网格变体 `herd_weight{track}_thr{NN}`。随后在 `pipeline/panel/encode.py` 的面板聚合阶段, 用这一权重对篇级 LLM 投票语调 `llm_vote_score{track}` 做加权求和, 构成本列 `llm_vote_score_hw_thr45_sum{track}`。本列的直接上游是 stage 21 (`21_tone_llms`, 产出三家 LLM 多数投票的篇级语调票 `llm_vote_score{track}` ∈ {-1, 0, +1}) 与 stage 24 (`24_herd_decay`, 产出阈值敏感性权重 `herd_weight{track}_thr45`), 两者在 `pipeline/panel/runner.py` 步骤 3d 里逐篇相乘并预计算为 `llm_vote_score_hw_thr45{track}` 列, 再由 `encode.py::build_aggregation_dict` 按 (target_bank, year) 分组求和产出本列。

【方法学与计算】
本列是"分子中间列", 而非最终可直接解读的语调水平: 它是银行-年层面对全部有效篇加权语调票的求和 Σ (票 × 权重), 单位随文章篇数与权重尺度而变, 不做归一化。要得到可比的"加权平均语调"水平, 面板下游还需用配套的"有效权重和"分母列 (`sum_wd_hw_thr45_llm{track}`, 即仅对 LLM 判定有效的篇目求权重和, 采用 valid-mask 匹配分母以避免分子分母域不一致导致语调系统性向 0 收缩, 详见 `encode.py::_build_llm_valid_masked_weights` 的 fix(encode-01) 注记) 相除, 才生成最终比率列 `llm_vote_tone_hw_thr45{track}`。本列因此更适合作为审计校验、二次自定义聚合或稳健性诊断的原材料, 一般回归表格径直消费的是除法之后的比率列。阈值 τ=0.45 是 `herd_detection.sensitivity_thresholds` (默认网格 [0.25, 0.30, 0.40, 0.45], SSOT=`core/config.py::herd_sensitivity_grid`) 中比生产基线 τ=0.35 更宽松的一档: τ 越大, 判定为"跟风稿"所需的文本相似度门槛越高, 也就是说被降权的文章越少, 整体加权结果越接近未加权的算术平均语调。τ=0.45 与 τ=0.25/0.30/0.40 各自独立预计算、并排陈列, 共同构成"换一个抄稿判定门槛, 结论是否还成立"的稳健性证据链, 彼此互为稳健性、不分主次, 不存在哪一档阈值是"更正确"的先验判断; 生产基线 τ=0.35 对应的是不带 `_thrNN` 后缀的 `llm_vote_score_hw_sum{track}` 及其比率列 `llm_vote_tone_hw{track}`, 是回归表格的默认主测度, τ=0.45 及同族其余阈值列是围绕该主测度做的规格稳健性检验分支。

【文献定位】
跟风衰减降权的构念根植于媒体信息经济学对"重复报道≠独立信息"的长期关注: Tetlock (2007, Journal of Finance) 论证媒体文本对股价的影响力与其信息独立性直接相关, 是本族权重设计在直觉与实证动机上的锚点; 更晚近地, 文本相似度聚类/降权在识别转载、洗稿、通稿分发等现象上已成为处理大规模新闻语料的标准前处理步骤, 目的是避免少数源头事件被自动写手或转载渠道放大后, 在下游面板统计量里获得不成比例的权重。本列所属的三家 LLM 多数投票语调测度本身 (`llm_vote_score`) 的方法学定位遵循近年金融文本分析文献里对大语言模型标注可靠性的系统评估: de Kok (2025, Management Science) 系统讨论了在会计与金融文本分析研究中使用生成式大语言模型的规范做法, 特别是 temperature=0、prompt 版本冻结、结果缓存等确定性保证手段, 与本管道 stage 21 的 prompt v8 字节级冻结、`temperature=0.0`、`_llm_cache.db` 可复现锚点的设计高度吻合; Kamen & Kamen (2025, arXiv) 专门论证了在内容分类任务上采用多模型多数投票 (majority-rules ensemble) 相较单模型标注的稳健性优势, 直接对应本列所依赖的 `llm_vote_score` 三家投票共识构造; Hansen (2026, FEDS Working Paper) 讨论了在缺乏人工金标准时如何验证 LLM 标注质量, 呼应本项目 Krippendorff's α / Cohen's κ 跨模型一致性 gate 的设计初衷。三者共同为"LLM 投票语调 × 跟风衰减权重 × 阈值敏感性网格"这一复合测度提供了方法学依据: 投票共识环节保证标注稳健, 加权求和环节保证信息独立性, 阈值敏感性网格环节保证结论不依赖单一超参数选择。

## VAR: llm_vote_score_hw_thr45_sum_full

【变体差分】
本列的轨道后缀为 `_full`, 表示相似度聚类判定所用的比较文本、以及所加权求和的语调票, 均取自"标题+全文正文"轨 (full track, stage 14 `content_full`)。full 轨是留篇门控的唯一依据轨 (2026-06-29 起 `llm_verified_full == True` 决定一篇报道是否计入"一篇银行金科报道"), 因此 `llm_vote_score_full` 的行宇宙即为面板的基准行宇宙; 本列作为 full 轨上的 τ=0.45 加权求和分子, 是三轨中样本量最完整、覆盖面最广的一支。full 轨的跟风聚类是在全文层面比较文本相似度, 因此更容易捕捉到大段落级别的雷同转载 (例如整篇通稿被多家媒体原文转发), 但也因为正文信息量更大, 词面上的巧合相似度相对更低, 在同一 τ 取值下判定为"跟风稿"的比例通常与 ctx/ss 轨不同, 三轨结果不可直接相加或相互替代解读。full 轨与 ctx/ss 轨在本族内各自独立预计算、各自 just-identified 并排陈列, 互为稳健性、不分主次, 禁止把三轨权重或求和列混入同一 over-identified Hansen J 设定; 与阈值维度 (τ∈{0.25,0.30,0.40,0.45} 与基线 0.35) 同理正交, 不设跨轨或跨阈值的联合矩条件。就阅读顺序而言, 本列是回归分析里最常被溯源核对的一支: 由于 full-only 门控意味着 `n_articles`、`fintech_share`、`attention_pct` 等一系列篇数派生统计量全部以 full 轨的留篇集合为准, 当研究者怀疑某一银行-年的加权语调结果异常 (例如极端偏正或偏负), 优先核查的正是本列与配套分母列 `sum_wd_hw_thr45_llm_full` 是否存在个别巨量转载事件驱动整体求和; τ=0.45 相较基线 0.35 更宽松, 若在该宽松阈值下加权求和结果与基线列 `llm_vote_score_hw_sum_full` 高度接近, 说明跟风降权对 full 轨主结论的敏感性较低, 是稳健性表格里常见的诊断读数之一。

## VAR: llm_vote_score_hw_thr45_sum_ctx

【变体差分】
本列的轨道后缀为 `_ctx`, 表示相似度聚类判定所用的比较文本、以及所加权求和的语调票, 均取自"标题+实体窗口"轨 (ctx track, stage 14 `content_ctx`, `prepend_title` 拼接)。ctx 轨在 2026-06-29 full-only 门控切换后降级为"conditional-on-full"的测度/稳健性轨: 其行宇宙是 full 轨留篇集合的子集, 即先由 `llm_verified_full` 判定一篇文章是否计入样本, 再在该子集内逐轨各自计算 ctx 口径下的相似度聚类、跟风权重与语调加权求和, 而非独立门控。若某篇文章因实体窗口缺失或提取失败落入 `ctx_is_fallback` (回退为全文 body), 该篇仍参与聚合但其 ctx 轨文本实质上退化为 full 轨内容, 这是 ctx 轨优雅降级语义的一部分, 不改变本列的求和口径。ctx 轨与 full/ss 轨各自独立预计算 herd_weight 与加权求和列, 互为稳健性并排陈列、不分主次, 严禁混入同一 over-identified Hansen J; 亦与阈值敏感性维度 (τ=0.25/0.30/0.40/0.45) 正交, 两个梯子不交叉合并。相较 full 轨, ctx 轨比较的文本更短、更聚焦于银行实体周边窗口, 在同一 τ=0.45 取值下, 文本相似度分布与降权比例通常与 full 轨系统性不同, 因此本列与 `_full` 后缀同名列不可直接比较数值水平, 只能在各自轨道内部沿阈值网格做纵向稳健性比较。使用本列时应留意其分母口径: 匹配的有效权重和分母列同样限定在 ctx 轨且已按 `llm_vote_score_ctx` 是否有效做过掩码, 分子分母同域, 避免出现因样本缺失而系统性向零收缩的偏误。

## VAR: llm_vote_score_hw_thr45_sum_ss

【变体差分】
本列的轨道后缀为 `_ss`, 表示相似度聚类判定所用的比较文本、以及所加权求和的语调票, 均取自"标题+银行∧金科同句±N窗"轨 (ss track, `context_window.ss_sentence_radius`, 默认窗口半径 1)。ss 轨的回退语义镜像 ctx 轨: 当一篇文章不存在银行与金科词同句 (或窗口内) 共现时, `content_ss` 回退为全文 body、`ss_is_fallback` 置 True, 与 ctx 轨共享同一套"缺同句证据即退化为全文"的优雅降级逻辑, `FINTECH_AC=None` 时 `*_is_fallback` 全部置 True 亦对 ss 轨等同生效。ss 轨同样在 full-only 门控切换后是 conditional-on-full 的稳健性轨, 行宇宙为 full 轨留篇集合的子集, 在该子集内独立完成相似度聚类、τ=0.45 跟风降权与语调加权求和三步, 不借用 full 或 ctx 轨的分母或权重。ss 轨的比较文本通常是三轨中最短、最聚焦于银行-金科共现语境的窗口文本, 相似度聚类在窄窗口下更容易因词面高度重合 (同一实体名+同一金科词) 而系统性偏高, 这意味着同一 τ=0.45 取值在 ss 轨判定为跟风稿的比例, 相较 full/ctx 轨可能明显不同, 数值绝对水平不可跨轨比较。ss 轨与 full/ctx 轨各自独立预计算、并排互为稳健性不分主次, 严禁混入同一 over-identified Hansen J, 亦与阈值敏感性梯子 (τ 网格) 正交不交叉; 三轨×多阈值的完整组合共同构成本测度族"跟风判定不依赖单一文本窗口口径、也不依赖单一相似度门槛"的双重稳健性证据。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kamen, A.; Kamen, Y. (2025). Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Hansen, A. L. (2026). Validating Large Language Model Annotations. Federal Reserve Board FEDS Working Paper No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
<!-- rendered-citations:end -->
