---
family_id: F406
columns:
- llm_vote_tone_vw_prob_ctx
- llm_vote_tone_vw_prob_full
- llm_vote_tone_vw_prob_ss
unit: 语调得分 (连续, 理论范围约 [-1,1]; bank-year 面板层面的关注度加权均值)
formula: 'llm_vote_tone_vw_prob{track} = llm_prob_score_w_sum{track} / _llm_denom(''vw'', ''prob'', track, sum_mention_density.replace(0, NaN))；其中 llm_prob_score_w_sum{track} 为该 bank-year 内, 逐篇文章 Logit-to-Score 概率化情感分 × 该篇 mention_density 权重 之和, _llm_denom 对分子分母做 LLM 有效票(valid-mask)口径对齐, track ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\encode.py (聚合公式, w_prob 分子取值 + _llm_denom('vw','prob',track,denom) 三轨归一 L2224-L2226) ; pipeline\panel\export.py (Stata 变量标签映射 L1365-L1366, 仅落 _full/_ctx 显式标签, _ss 由三轨机械派生循环补全)
upstream:
- 21_tone_llms (三家 LLM gpt54nano/gemini31/deepseekv4 逐篇情感投票与 logit 概率化)
- 14_materialize_ctx (content_ctx/content_ss 三轨文本物化)
- 40_panel_export_main (mention_density 关注度权重 / llm_prob_score_w_sum{track} 前置聚合)
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, Paul C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A.; Kamen, Y.
  year: 2025
  title: 'Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization'
  venue: arXiv
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R.; Miller, B. P.; Twedt, B. J.
  year: 2023
  title: 'Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: "10.18653/v1/2023.emnlp-main.330"
  type: "journal"
  authors: "Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C."
  year: 2023
  title: "Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback"
  venue: "Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing"
  pages_or_artno: "5433-5442"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"经关注度加权的 LLM 概率化语调"——一个把三家大语言模型对单篇银行/金科报道的情感投票, 先转换为连续概率分, 再按该篇文章在 bank-year 单元内的关注度(mention_density)加权汇总, 得到的银行-年度层面语调水平。它是 stage 21 三家 LLM (gpt54nano、gemini31、deepseekv4) 逐篇投票口径与 Logit-to-Score 概率映射方法的下游聚合产物, 落盘于 40_panel_export_main。构念定位上, 它属于 P1 (bank_fintech_tone) 论文族"处理变量"体系中 llm_vote_tone 家族的一个价值加权(value-weighted, VW)变体: 与算术平均口径不同, VW 赋予"报道更密集"的银行-年份更大权重, 隐含的经济学假设是媒体语调的市场影响力应随报道关注度放大, 这一权重构造思路直接呼应 Tetlock (2007) 关于媒体情感通过关注渠道影响投资者行为与股价的经典发现——语调本身的信息含量须结合其被市场"看见"的概率来度量, 单纯的等权平均会低估高关注度事件的语调冲击。

【方法学与计算】
计算链条分两段。第一段在 stage 21 完成: 三家 LLM 各自对每篇文章输出情感投票(正/负/中性), encode.py 中通过 Logit-to-Score 映射把离散投票转成 [-1,1] 区间的连续概率化情感分 llm_prob_score, 相比原始三分类多数票, 概率化分数保留了模型置信度的连续信息, 减少了投票边界处的信息损失; 这一"把 LLM 离散判定转成连续可加权分数"的思路与 de Kok (2025) 强调的生成式 LLM 文本分析需在方法论上保证输出可量化、可复现的规范相一致。第二段在面板聚合阶段: encode.py 对每个 bank-year 单元, 先算出 llm_prob_score_w_sum{track} = Σ(该单元内每篇文章的 llm_prob_score{track} × mention_density_该篇), 再除以 _llm_denom('vw', 'prob', track, denom) 得到 VW 均值; 分母 denom = sum_mention_density.replace(0, NaN), 即该单元全部文章的关注度权重之和, 零关注度单元置 NaN 防止除零污染; _llm_denom 进一步对分子分母做"LLM 有效票"(valid-mask)口径对齐, 确保加权平均只在三家 LLM 均给出有效判定的文章子样本上进行, 不把因缺失/解析失败而被跳过的文章计入权重基数, 避免分母虚高稀释语调水平。三轨 (full/ctx/ss) 各自独立走这一完整加权流程, 互不借用彼此的分子或分母, 保证每轨都是一个可独立解释的 just-identified 语调测度。

【文献定位】
本家族站在两条文献脉络的交汇处。一是媒体情感度量与市场反应的经典脉络: Tetlock (2007, Journal of Finance) 建立了"媒体语调是可量化、可预测市场行为的信息载体"这一基础范式, 本家族的关注度加权设计正是对该范式中"语调影响力应与曝光度成正比"这一隐含前提的显式操作化; Holzman, Miller & Twedt (2023, The Accounting Review) 进一步在文本语调聚合中引入权重维度(其研究以媒体权威性为权重, 本家族姊妹测度族 mw 系列即直接对应该权重构造, vw 系列则以关注度/提及密度为权重, 二者构成互补的加权哲学)。二是 LLM 文本标注方法学脉络: de Kok (2025, Management Science) 系统论证了会计与金融研究中使用生成式 LLM 做文本分析时, temperature=0、prompt 冻结与结果可复现是方法论底线, 本项目 stage 21 的 prompt v8 字节级冻结与 temperature=0.0 缓存键设计正是遵循这一规范; Kamen & Kamen (2025) 则专门研究了多 LLM 集成(ensemble)做内容分类时"多数投票"策略的有效性边界, 为本项目采用三家 LLM 独立投票再聚合(而非单一模型输出)的设计提供了方法学支撑——三家模型的投票在概率化之前互为稳健性、不分主次, 聚合口径本身不引入厂商偏向。 在这两条脉络之外, 本族分子所依赖的概率化环节还需要第三条更上游的举证: 把三家模型自报的 confidence 字段当作可加权的概率量, 其正当性由 Tian 等 (2023) 提供。该文在英文事实型 QA 上比较多种置信度获取策略, 发现对经 RLHF 微调的模型, 以自然语言直接索要口头概率所得的置信度, 其校准程度 (以 ECE 度量) 优于读取模型内部的 logit 条件概率, 这正是本仓库在 RLHF 类商用模型上以 prompt 索取 confidence、再经 Logit-to-Score 映射为 llm_prob_score 的实证依据——概率分只有在其本身可被视为校准的情形下, 后续乘以 mention_density 求和才具有「按关注度加权的期望语调」这一解释。迁移边界须如实标明: 该文证据取自 2023 年 GPT-3.5/GPT-4 代次的英文事实问答, 本仓库既未在中文银行×金科新闻语料上复测 ECE, 也未验证该校准优势能否迁移至 deepseekv4 与 gemini31 两家非 OpenAI 模型; 该文更不涉及跨模型投票、关注度加权求和与 bank-year 面板聚合。故其锚定范围仅限于文章级 confidence 的可用性这一环, 不构成对 vw 关注度加权口径或三轨聚合设计的任何背书。
【口径铁律】
本家族三个列构成一组严格并排的三轨测度 llm_vote_tone_vw_prob_full / _ctx / _ss, 分别对应"标题+正文"全文轨、"标题+实体窗口"上下文轨、"标题+银行∧金科同句共现窗口"严格轨。三轨在计量意义上各自 just-identified, 互为稳健性、不分主次, 在任何回归设计中都不得混入同一个 over-identified 的 Hansen J 过度识别检验框架——例如不能把 full/ctx/ss 三个语调测度同时作为同一工具变量方程的多个内生变量或多个矩条件叠加使用, 而应各自单独进入回归或作为彼此独立的稳健性检验分支呈现。样本口径上, 本家族严格遵循 2026-06-29 起生效的 full-only 留篇门控: 一篇报道是否被计入"银行-金科相关报道"样本, 唯一判据是 full 轨的 llm_verified_full == True, ctx/ss 两轨在此基础上属于 conditional-on-full 的测度分支, 其行宇宙是 full 轨留篇集合的子集, 但各轨的分子(llm_prob_score_w_sum{track})与分母(sum_mention_density 对应的 valid-mask 子样本)仍按各轨自身口径独立计算, 不借用 full 轨的中间量。ss 轨的回退语义镜像 ctx 轨: 当某篇文章不存在银行与金科词在同一句内的共现窗口时, content_ss 退化为全文 body, 对应的 ss_is_fallback 标记为 True, 此时该篇文章仍参与 ss 轨的语调计算(而非被剔除), 分母 n_articles 与 ctx 轨共享同一份"是否降级"口径记录, 保证 full/ctx/ss 三轨在样本规模层面具有可比的透明度。

## VAR: llm_vote_tone_vw_prob_ctx

【变体差分】
本列是 F406 家族在"标题+实体窗口"上下文轨(ctx track)上的关注度加权概率化语调测度。区别于 full 轨消费全文正文, ctx 轨的分子来源 llm_prob_score_w_sum_ctx 与分母权重 sum_mention_density 均建立在 content_ctx 文本(标题 prepend 之后, 截取围绕目标银行实体的窗口文本)之上; content_ctx 由 stage 14 (ctx_materializer) 在 stage 21 之前物化, 使得下游 stage 21 三家 LLM 能够对同一篇文章分别在 full 与 ctx 两种文本视角下独立完成情感投票与概率化打分, 二者互不共享中间计算结果。语义上, ctx 轨捕捉的是"聚焦于目标银行实体附近语境"的语调信号, 相比 full 轨可以过滤掉正文中与该银行无直接关联的段落噪声, 在文章较长、话题混杂时尤其能提升语调信号的实体针对性; 但代价是窗口截取本身依赖实体识别与窗口半径参数, 引入了额外的测量误差来源。留篇门控上, ctx 轨的行宇宙严格是 full 轨 llm_verified_full == True 留篇集合的子集(2026-06-29 起 full-only 门控生效), 即一篇文章只有先通过 full 轨的"是否为有效银行-金科报道"判定, 其 ctx 轨的语调分值才会被计入本列的加权聚合分子分母, ctx 轨自身不独立执行留篇判定。加权口径上, 本列的分母 _llm_denom('vw', 'prob', '_ctx', denom) 只统计 ctx 轨自身有效票(三家 LLM 对 ctx 文本均给出有效判定)的文章子样本关注度之和, 不与 full 轨的分母混用, 因此即便同一批文章, full_vw_prob 与 ctx_vw_prob 两列的分母基数在数值上通常并不相等。定位上, ctx 轨与 full 轨、ss 轨构成互为稳健性、不分主次的并排三轨测度, 三者严禁混入同一 over-identified Hansen J 检验; 在实证设计中, ctx 轨常被用作 full 轨主口径 llm_vote_tone_full 家族处理变量的稳健性检验分支, 用以证明主结论不因文本窗口截取方式的选择而系统性改变。

## VAR: llm_vote_tone_vw_prob_full

【变体差分】
本列是 F406 家族的全文轨(full track)测度, 也是家族内三轨中样本留取判据的"锚定轨"——2026-06-29 起生效的 full-only 留篇门控规定, 一篇报道是否被判定为"有效的银行-金科相关报道", 唯一依据是其 full 轨的 llm_verified_full == True 标记, 该判定在 tone_llms.py 的 df_filtered 与 run_pipeline_function.py 的 _stage21_skip_is_compatible 两处副本必须同步维护, 任一处不同步都会导致 skip 判定永久失效、每次重跑都触发付费的 stage 21 全量重算。本列的分子 llm_prob_score_w_sum_full 与分母权重均建立在 content_full 文本(标题 prepend 全文正文, 未做任何窗口截取)之上, 是三轨中信息覆盖面最完整、但也最容易掺入与目标银行无直接关联段落噪声的一支。计算上, 该篇文章的 Logit-to-Score 概率化情感分先由三家 LLM(gpt54nano、gemini31、deepseekv4)分别在 full 文本上完成投票并做 logit 转连续分, 再乘以该篇的 mention_density 关注度权重求和得到 llm_prob_score_w_sum_full, 除以 _llm_denom('vw', 'prob', '_full', sum_mention_density.replace(0, NaN)) 得到本列的 bank-year 加权均值; 分母同样只统计 full 轨自身三家 LLM 均判定有效的文章子样本的关注度总和。构念定位上, full 轨是 P1 (bank_fintech_tone) 论文族处理变量体系 llm_vote_tone 家族的主口径来源之一, 但需注意本 VW-prob 变体本身并非 P1 主回归 treatment(P1 主口径 treatment.primary 是不加权的 llm_vote_tone_full 多数投票共识), 本列是其"按关注度加权 + 概率化连续打分"的双重稳健性延伸——加权维度(VW vs 简单均值 vs MW 媒体权威加权)与打分维度(离散多数票 vs Logit-to-Score 连续概率分)两者叠加, 构成比主口径信息密度更高、但对权重构造假设更敏感的补充测度, 在实证中通常作为主结果的稳健性支柱而非首要报告口径。

## VAR: llm_vote_tone_vw_prob_ss

【变体差分】
本列是 F406 家族在"标题+银行∧金科同句共现窗口"严格轨(ss track, same-sentence)上的关注度加权概率化语调测度, 是三轨中判据最严格的一支。ss 轨要求银行实体词与金科词出现在同一句内(±N 窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1), 只有满足这一同句共现条件的文本片段才被纳入 content_ss, 由 stage 14 与 ctx 轨同步物化。当某篇文章不存在满足条件的同句共现窗口时, ss 轨触发回退语义(镜像 ctx 轨的回退设计): content_ss 退化为全文 body, 对应 ss_is_fallback 标记置 True, 该篇文章并不会因此被剔除出 ss 轨的计算, 而是继续参与 llm_prob_score_w_sum_ss 与分母权重的累加, 只是其语调信号的文本来源实质上等同于 full 轨; n_articles 分母口径与 ctx 轨共享同一套"是否降级"记录方式, 保证跨轨可比性。留篇门控同样服从 full-only 铁律: ss 轨自身不独立判定"是否为有效银行-金科报道", 其行宇宙是 full 轨 llm_verified_full == True 留篇集合的子集; 而"是否存在同句共现窗口"是一个独立于留篇判定的、发生在文本物化阶段的二级过滤维度, 两者不可混淆——前者决定文章是否进入分母基数, 后者只决定该文章的语调打分依据的是严格同句片段还是回退全文。加权与分母口径上, 本列分母 _llm_denom('vw', 'prob', '_ss', denom) 严格只统计 ss 轨三家 LLM 均给出有效判定的文章子样本关注度之和, 与 full、ctx 两轨的分母数值一般不相等, 三者不可相互替代或加总。由于同句共现判据本身对文本长度与句法结构较为敏感, ss 轨在样本量较小(如早期试跑 T=2 环境)时容易出现较高比例的回退触发甚至零方差退化, 这是符合预期的口径特征而非缺陷; 在生产规模 T=19 全量语料上, ss 轨作为三轨中信噪比最高但样本利用率相对更保守的一支, 与 full、ctx 两轨互为稳健性、不分主次并排呈现, 共同构成对 llm_vote_tone_vw_prob 家族语调测度稳健性的三重交叉验证, 三者绝不可混入同一 over-identified Hansen J 检验框架。

<!-- rendered-citations:begin -->
Tetlock, Paul C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Kamen, A.; Kamen, Y. (2025). Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Holzman, E. R.; Miller, B. P.; Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C. (2023). Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 5433-5442. https://doi.org/10.18653/v1/2023.emnlp-main.330
<!-- rendered-citations:end -->
