---
family_id: F384
columns:
- llm_vote_cont_hw_thr25_sum_ctx
- llm_vote_cont_hw_thr25_sum_full
- llm_vote_cont_hw_thr25_sum_ss
unit: 银行-年内加权求和分, 无量纲 (逐篇连续语调 × 跟风衰减权重 的银行-年内累加, 未除以权重和)
formula: 'llm_vote_cont_hw_thr25_sum_{track} = Σ_i [ llm_vote_cont_{track,i} × herd_weight_{track,i}_thr25 ], i 取该银行-年样本内 llm_vote_score_{track,i} 非缺失的全部文章; herd_weight_{track,i}_thr25 由 stage 24 在相似度阈值 τ=0.25 (敏感性网格 tag=thr25, 对照生产基线 τ=0.35) 下重估, 是"文章与同银行同期其他报道文本相似度越高、可信增量信息越少"的衰减权重 (Peress, 2014, Journal of Finance; Tetlock, 2007, Journal of Finance)'
producer: pipeline\panel\runner.py (步骤 3d 逐篇生成 llm_vote_cont_hw_thr25_{track} = llm_vote_cont_{track} × herd_weight_{track}_thr25) ; pipeline\panel\encode.py (build_aggregation_dict 按 target_bank×year 对该逐篇列取 sum, 得本列)
upstream: [21_tone_llms, 24_herd_decay_processor]
citations:
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: "de Kok, T."
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving Content to Investor Sentiment: The Role of Media in the Stock Market"
  venue: "Journal of Finance"
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.48550/arXiv.2511.15714"
  type: arxiv
  authors: "Kamen, A., & Kamen, Y."
  year: 2025
  title: "Majority rules: LLM ensemble is a winning approach for content categorization"
  venue: "arXiv"
- doi: "10.1111/jofi.12179"
  type: journal
  authors: "Peress, J."
  year: 2014
  title: "The Media and the Diffusion of Information in Financial Markets: Evidence from Newspaper Strikes"
  venue: "Journal of Finance"
  vol: "69"
  issue: "5"
  pages_or_artno: "2007-2043"
- doi: "10.17016/FEDS.2026.020"
  type: wp
  authors: "Hansen, A. L."
  year: 2026
  title: "Validating large language model annotations"
  venue: "Federal Reserve Board FEDS Working Paper"
  vol: "2026-020"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"银行-年内跟风衰减加权连续语调"这一构念在分子端 (加权和) 的原始记账值, 而非最终归一化后的加权均值。其上游素材是 stage 21 三家大模型 (gpt54nano/gemini31/deepseekv4) 对每篇报道的多数投票共识连续语调分 `llm_vote_cont_{track}` (取值区间约 [-1, 1], 值越正表示报道对目标银行的语调越正面, 与离散三分类 `llm_vote_score` 共用同一行有效性, 但保留投票内部的强度信息而非只留符号)。跟风衰减 (herd decay) 权重来自 stage 24: 对每篇报道, 在同一银行同一年份的报道集合内, 用文本相似度衡量它与其余报道的"抄稿/转载/同源通稿"程度, 相似度越高则该篇边际信息增量越低, 赋予的权重就越小, 这一思想呼应 Peress (2014, Journal of Finance) 关于媒体信息扩散的论证——该文以报纸罢工作为自然实验, 发现同一事件被更多独立报道渠道覆盖时价格发现更充分, 反过来意味着高度雷同/彼此复制的报道并不构成独立信息增量, 简单等权累加会系统性放大这类"同源通稿"的权重; 本家族用逐篇相似度衰减来近似修正这一冗余。Tetlock (2007, Journal of Finance) 则是本家族语调测度本身的方法论源头之一, 说明从媒体文本中提炼的悲观度/语调信号具有独立于基本面的定价含量, 为"逐篇语调值得测度并加权累加"这一前提提供文献支撑, 但该文并不讨论重复报道的冗余衰减问题, 二者在本家族中分别对应不同的论证环节, 不应混为一谈。本家族在此基础上再加一层阈值敏感性: 生产口径判定"多相似算跟风"用阈值 τ=0.35, 本列改用更宽松的 τ=0.25 重估同一权重逻辑 (敏感性网格由 `herd_sensitivity_grid` 统一生成, 默认候选 {0.25, 0.30, 0.40, 0.45}), 列名后缀 `_thr25` 即由此而来。列名中的 `_sum` 表明这是分子 (Σ 加权语调), 尚未除以对应的权重之和 (`sum_herd_weight_{track}_thr25`); 面板中真正可解读为"加权平均语调"的是同一 τ 下的比值列 `llm_vote_tone_hw_thr25{track}`/`llm_vote_cont_hw_thr25{track}` (若已计算), 本家族三列本身是这一比值的分子部件, 直接落盘暴露给下游, 便于审计者自行核验分子分母的构造是否一致、或按不同分母口径重新组合。

【方法学与计算】
计算分两步, 均严格逐轨进行, 不跨轨混用。第一步 (runner.py 步骤 3d): 对每篇文章, 取该轨已算好的 `herd_weight_{track}_thr25` (τ=0.25 下的衰减权重, 由 stage 24 输出; 若 stage 24 未产出该 τ 的权重列, 则本列在该轨整体缺失, 优雅跳过而非报错), 与同轨 `llm_vote_cont_{track}` 逐元素相乘, 得到文章级中间列 `llm_vote_cont_hw_thr25_{track}`。第二步 (encode.py build_aggregation_dict): 以 `(target_bank, year)` 为分组键, 对上述文章级列取 `sum` 聚合, 得到本家族三列。聚合口径与 `llm_vote_score` 同一有效性判据配对 (LLM 族为 nullable 缺失敏感型: 某篇报道若三家模型未能给出有效投票, `llm_vote_score`/`llm_vote_cont` 记为缺失, 该篇不进入 Σ; 与此对应的分母列同样只累加"有效篇"的权重, 即 encode-01 修正后的 valid-mask 匹配分母设计, 分子分母同域, 避免把"LLM 未判断"误当作"语调为 0"而系统性把均值拉向 0)。三条列彼此的差异仅在文本轨: `_full` 用标题+正文全文, `_ctx` 用标题+目标银行实体窗口文本, `_ss` 用标题+银行∧金科同句±N 窗口文本 (无共现命中时回退为全文 body, 并标记 `ss_is_fallback=True`, 与 `_ctx` 回退语义镜像); 三者的留篇口径统一以 stage 21 `llm_verified_full` 为准 (full-only 门控, 2026-06-29 起生效), 行宇宙一致, 只是各轨用来加权求和的语调值/权重值取自各自轨道的逐篇结果。

【文献定位】
本家族方法学上落在三条文献线的交汇处: 其一是媒体语调测度对"重复报道稀释边际信息"的敏感性处理, 沿用 Peress (2014) 关于媒体覆盖广度影响信息扩散/价格发现速度的论证框架, 并以 Tetlock (2007) 作为语调测度本身载有定价相关信息这一前提的文献支撑(两文各自对应不同的论证环节, 详见【构念与来源】); 其二是大模型多家投票作为文本分类/情感标注工具的可靠性文献, 本列所依赖的连续语调分正是三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票共识的强度化版本, 呼应 Kamen & Kamen (2025) 关于集成多家大模型投票在内容分类任务上优于单一模型的发现, 也与 de Kok (2025, *Management Science*) 关于在会计与金融文本分析中规范使用生成式大模型 (温度固定为 0、提示词冻结、结果可缓存复现) 的方法论建议一致——本项目 stage 21 的 `temperature=0.0` 与 prompt 字节级冻结正是遵循这一范式; 其三是无金标准场景下大模型标注可信度的验证文献, Hansen (2026, FEDS Working Paper) 讨论了在缺乏人工金标准时如何用一致性统计量 (κ/α 等) 验证大模型标注质量, 与本项目三家 LLM 多数投票共识、并以 Krippendorff's α 与重映射后的 Cohen κ 度量模型间一致性的做法在思路上呼应——需说明的是, 本家族正文其余处出现的"Hansen J"是计量经济学中的过度识别检验统计量, 与 Hansen (2026) 这篇 LLM 标注验证文献是同姓氏巧合、并非同一出处, 两者不可混淆。阈值敏感性网格的设计理念则呼应稳健性推断文献中"结论不应依赖单一自由选定的门槛"的一般性要求, 本列 (τ=0.25) 与生产基线 (τ=0.35) 及网格内其余候选 (0.30/0.40/0.45) 各自独立重估、并排陈列, 供读者判断主结论是否随门槛松紧而漂移。此外须提示: 本项目本机开发态样本仅 T=2 (2017-2018 两年, 110 家银行), 在如此小的银行-年样本内, 同期报道篇数往往很少, 跟风衰减权重所依赖的"同银行同期文本相似度分布"在 τ=0.25/0.35 等不同阈值下容易出现零方差或高度退化的边界情形, 本列在开发态下的读数解读应以此为前提; 生产语料 (T=19, 2007-2025) 报道篇数充分后, 阈值敏感性网格才具备正常的统计辨识力, 二者不可等同看待。

## VAR: llm_vote_cont_hw_thr25_sum_ctx

【变体差分】
本列取三轨中的 `_ctx` 轨: 逐篇 `llm_vote_cont_ctx` 与 `herd_weight_ctx_thr25` 均取自"标题+目标银行实体窗口"文本上跑出的结果, 与全文轨 (`_full`) 及同句共现轨 (`_ss`) 相比, 输入文本更聚焦于银行实体周边语境, 剔除了正文中与目标银行无关的段落对语调判断的稀释/污染。`_ctx` 轨的留篇集合与 `_full` 一致 (full-only 门控口径下, ctx 是 conditional-on-full 的稳健性/测度轨, 行宇宙是 full 留篇集的子集), 但逐篇的语调强度值、以及用于衰减加权的相似度权重, 均在 ctx 文本域内独立计算——即两篇全文近乎重复的报道, 若各自的银行实体窗口文本差异较大, 在 `_ctx` 轨下可能被判定为较低相似度、从而获得比 `_full` 轨更高的权重, 反之亦然。本列与 `_full`/`_ss` 两姊妹列是互为稳健性、各自 just-identified 并排的测度, 不应被混入同一 over-identified 的 Hansen J 设定; 三轨读数若方向一致但幅度不同, 应解读为"实体窗口聚焦"这一构造选择带来的正常测度差异, 而非其中一轨更"正确"。使用者若要核对本列的分母配套, 应取同一 `_ctx` 轨、同一 τ=0.25 标签下的权重和列, 不可误用 `_full` 或基线 τ=0.35 的权重和作除数, 否则会得到既非 full 也非 ctx、既非基线也非敏感性口径的错配比值。本列本身是 Σ 而非均值, 数值随该银行-年 `_ctx` 轨留篇篇数的增减而机械放大或缩小, 不适合直接跨银行或跨年份比较水平; 恰当用法是先除以配套权重和得到加权平均语调, 或在控制了 `_ctx` 轨篇数/权重和之后再做回归。

## VAR: llm_vote_cont_hw_thr25_sum_full

【变体差分】
本列取三轨中的 `_full` 轨, 是三者中文本覆盖面最广的一支: 逐篇 `llm_vote_cont_full` 与 `herd_weight_full_thr25` 均在"标题+正文全文"文本上计算, 未做实体窗口截取或共现句筛选。`_full` 轨同时也是留篇门控的锚定轨——2026-06-29 起, 一篇报道是否计入某银行-年的"银行金科报道"样本, 唯一依据是该篇在 `_full` 轨的 `llm_verified_full == True`, ctx/ss 两轨的行宇宙都是这一集合的子集; 因此本列在三姊妹列中承担"样本口径基准"的角色, 但在测度地位上仍与 ctx/ss 两轨互为稳健性、不分主次, 三者各自 just-identified 并排, 禁止混入同一 over-identified 的 Hansen J 设定。与全家族其余两列相同, 本列同样是 τ=0.25 阈值敏感性网格下的分子加权和, 仅换算权重门槛, 不改变文本轨选取逻辑。由于 `_full` 轨兼具"样本口径基准"与"最宽文本覆盖"两重角色, 该轨下同一批文章的相似度比较涵盖的文本量最大, 抄稿/转载判定相对更容易在长文本中捕捉到共同段落, 因而 τ=0.25 与基线 τ=0.35 之间读数差异的方向与幅度, 在 `_full` 轨上最具解释基准意义, 但这并不意味着 `_full` 轨的敏感性结果比 `_ctx`/`_ss` 轨"更可信"——三轨仍须并排报告、各自作为独立的稳健性证据链, 而不是相互替代或加总。使用者核对本列时, 配套分母是同一 `_full` 轨、同一 τ=0.25 标签下的权重和列, 与生产基线口径 (τ=0.35, 无 `_thr` 后缀) 的对应列不可混用。

## VAR: llm_vote_cont_hw_thr25_sum_ss

【变体差分】
本列取三轨中的 `_ss` 轨: 逐篇 `llm_vote_cont_ss` 与 `herd_weight_ss_thr25` 均在"标题+银行∧金科同句 (±N 句窗口, 默认 N=1) "的最窄文本域上计算, 是三轨中语境最严格的一支, 判据原语要求目标银行实体与金科词在同一句 (或相邻句窗口内) 共同出现。当某篇报道在正文中虽提及目标银行, 却没有银行与金科词同句共现的片段时, `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 该篇在 `_ss` 轨的语调值与权重值退化为与 `_full` 轨同源 (镜像 `_ctx` 轨的回退语义), 但共享同一 `n_articles` 分母口径不变。因此本列在跟风衰减权重的相似度比较上, 对"确有银行金科同句共现"的报道子集给出的是最窄语境下的独立估计, 对回退子集则与 `_full` 轨读数高度重合; 与 `_ctx`/`_full` 两列一样, 本列是 τ=0.25 阈值下 just-identified 并排的稳健性测度分量, 不与另外两轨混入同一识别方程。特别须注意的是, `_ss` 轨的判据主体是"银行∧金科词同句/邻近窗口", 与 stage 13 共现硬过滤的判据 (银行与金科词 ±1 句窗口且允许标题命中) 并非同一原语——前者由 `entity_context.py` 中严格同句的抽取函数产生, 用于三轨文本物化, 后者是文章级去留的硬过滤条件, 两者刻意不复用同一实现, 使用者不应假设两者对同一篇文章给出完全一致的判定。此外, `_ss` 轨在跟风衰减权重上的相似度比较, 是在窄语境文本 (同句窗口, 而非全文) 上进行, 因此哪怕两篇报道全文高度雷同, 只要各自的银行金科同句片段措辞不同, `_ss` 轨仍可能给出与 `_full`/`_ctx` 轨不同的相似度判断与权重, 这是设计上的正常差异而非误差。
<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Peress, J. (2014). The Media and the Diffusion of Information in Financial Markets: Evidence from Newspaper Strikes. Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Hansen, A. L. (2026). Validating large language model annotations. Federal Reserve Board FEDS Working Paper [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
<!-- rendered-citations:end -->
