---
family_id: F383
columns:
- llm_vote_cont_hw_sum_ctx
- llm_vote_cont_hw_sum_full
- llm_vote_cont_hw_sum_ss
unit: 无量纲 (herd-weight 加权连续投票值之银行-年内跨文章求和; 分子, 需除以对应 hw 分母才成为 [-1,1] 区间语调水平)
formula: 'llm_vote_cont_hw_sum{track} = Σ_{i∈(bank,year)} llm_vote_cont{track}_i × herd_weight{track}_i, 其中 llm_vote_cont{track}_i = llm_vote_score{track}_i × llm_agreement_rate{track}_i (三家 LLM 多数投票离散分 {-1,0,1} 乘以三家一致率 ∈[0,1] 的连续化), herd_weight{track}_i 由 stage 24 (herd_decay.py, STAGE_NAME=24_herd_decay_processor) 按 tf-idf 余弦相似度 + 固定阈值 SIMILARITY_THRESHOLD=0.35 (闭边界, config 键 herd_decay.similarity_threshold) 逐篇逐轨判定跟风关系 (相似度≥阈值且按发稿日期排序晚于首发者判为跟风前驱链的跟进稿), 再按其在跟风链中的位置降权, 首发/独家稿权重趋近 1; track ∈ {full, ctx, ss} 三套源列各自独立求和'
producer: pipeline\panel\encode.py (build_aggregation_dict, 聚合口径; herd_weight 源列由 pipeline\sentiment\herd_decay.py / stage 24 (STAGE_NAME='24_herd_decay_processor') 产出)
upstream:
- 21_tone_llms
- 24_herd_decay_processor
citations:
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving Content to Investor Sentiment: The Role of Media in the Stock Market"
  venue: "Journal of Finance"
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.1093/rof/rfab036"
  type: journal
  authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W."
  year: 2022
  title: "Language and Domain Specificity: A Chinese Financial Sentiment Dictionary"
  venue: "Review of Finance"
  vol: "26"
  issue: "3"
  pages_or_artno: "673-719"
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: "de Kok, T."
  year: 2025
  title: "ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
- doi: "10.1093/rfs/hhx055"
  type: journal
  authors: "You, J., Zhang, B., & Zhang, L."
  year: 2018
  title: "Who Captures the Power of the Pen?"
  venue: "The Review of Financial Studies"
  vol: "31"
  issue: "1"
  pages_or_artno: "43-96"
- doi: "10.1609/aaai.v39i18.34120"
  type: "journal"
  authors: "Lyu, Q., Shridhar, K., Malaviya, C., Zhang, L., Elazar, Y., Tandon, N., Apidianaki, M., Sachan, M., & Callison-Burch, C."
  year: 2025
  title: "Calibrating Large Language Models with Sample Consistency"
  venue: "Proceedings of the AAAI Conference on Artificial Intelligence"
  vol: "39"
  issue: "18"
  pages_or_artno: "19260-19268"
- doi: "10.18653/v1/2025.findings-acl.744"
  type: "journal"
  authors: "Wang, W., Wang, Y., & Huang, H."
  year: 2025
  title: "Ranked Voting based Self-Consistency of Large Language Models"
  venue: "Findings of the Association for Computational Linguistics: ACL 2025"
  pages_or_artno: "14410-14426"
new_dois: []
---

## CORE

【构念与来源】
本家族的三个变量 llm_vote_cont_hw_sum_full / _ctx / _ss, 度量的是"银行-年"单元内, 经跟风衰减 (herd decay) 降权后的连续化 LLM 情感投票值之跨文章求和, 是 stage 40 面板导出阶段构造 hw (herd-weight) 加权银行-年语调水平 llm_vote_cont_hw{track} 的分子中间量。它承接两条上游血统: 一是 stage 21 (tone_llms) 产的三家大模型 (gpt-5.4-nano/gpt54nano、gemini-3.1-flash-lite/gemini31 两家走 yunwu、deepseek-v4-flash/deepseekv4 直连 api.deepseek.com) 多数投票情感, 离散分 llm_vote_score ∈ {-1, 0, 1} 与三家一致率 llm_agreement_rate ∈ [0, 1] 相乘得到的连续化情感值 llm_vote_cont (encode.py L301: `llm_vote_cont = llm_vote_score × llm_agreement_rate`, 自然传播 NaN, 一致率越低意味着三家分歧越大, 该篇文章对总体语调的贡献即被自动收缩); 二是 stage 24 (herd_decay.py, STAGE_NAME='24_herd_decay_processor') 按 Tetlock (2007, JF) 提出的"媒体内容对投资者情绪赋能"框架衍生出的跟风衰减权重 herd_weight, 用来刻画同一银行同一年度内, 内容高度相似 (转载/改写/跟风) 的报道相对首发/独家报道应被降权的直觉——若某条负面消息被十家媒体转载, 简单等权求和会机械放大该事件的语调冲击, 而 herd_weight 依据 tf-idf 余弦相似度与固定阈值 SIMILARITY_THRESHOLD=0.35 (闭边界判定) 结合发稿日期先后判定跟风链, 对判定为跟进稿的文章做离散降权, 使得独家、首发的报道对银行-年语调的贡献权重更高——这是一套阈值判定 + 链位置降权的机制, 而非随时间连续衰减的函数。llm_vote_cont_hw_sum{track} 即是把 llm_vote_cont 与 herd_weight 逐篇相乘后在银行-年单元内求和, 是构造 stage 40 最终 hw 加权语调水平变量 llm_vote_cont_hw{track} = llm_vote_cont_hw_sum{track} / hw_denom{track} 的分子部件——分母 hw_denom 由同一银行-年单元内 herd_weight 之和 (sum_herd_weight{track}) 或等效归一化基数给出, 因此本家族三列本身不是最终可解释的语调水平, 而是聚合链条上承前启后的求和中间量, 供审计、复算与稳健性追溯之用。

【方法学与计算】
计算发生在 pipeline\panel\encode.py::build_aggregation_dict 中, 通过 pandas groupby-agg 字典对文章级面板做 (bank, year) 分组求和: 对 track ∈ {full, ctx, ss} 三轨循环, 各自取源列 `llm_vote_cont_hw{track}` (文章级, 由 stage 24 产出的 herd_weight{track} 与 stage 21 衍生的 llm_vote_cont{track} 在文章级预先相乘得到) 做 'sum' 聚合, 写入面板列 `llm_vote_cont_hw_sum{track}`。herd_weight 三轨的取值来源存在版本兼容分支: v3.6.0+ (Edwards 2001 ORM 框架下重构后) schema 下, herd_weight_full / herd_weight_ctx / herd_weight_ss 三列各自独立算出 (真三轨, 因为跟风相似度的判定文本不同——full 轨对比全文, ctx 轨对比实体窗口, ss 轨对比银行∧金科同句窗口, 三种文本相似度矩阵结构不同, 衰减权重自然分化); 若磁盘上只存在 v3.5.x 遗留的单一 herd_weight 列 (未重跑 stage 24 同句轨), 代码会退化为三轨共用同一源列并在日志中显式 WARNING 提示"三轨聚合退化为单源, panel 中 sum_herd_weight_full == sum_herd_weight_ctx == sum_herd_weight_ss (fake 多轨), 如需真三轨需重跑 stage 24"——这一优雅降级避免了整条流水线因缺列崩溃, 但下游消费者 (含论文回归) 若直接假设三轨方差独立须先核对该 WARNING 是否出现。若源列在文章级完全缺失 (例如某次运行未跑 stage 24), 该 agg 键仍注册以维持 schema 稳定, 待 valid_agg 过滤阶段因源列不存在而自动跳过, 使下游面板对应列整体缺席而非以 0 填充 (避免把"未计算"误读为"跟风权重为零")。求和聚合本身对缺失值遵循 pandas 默认语义——文章级 NaN (来自留篇门控 full-only: 未通过 stage 21 三家一致验证的文章其 llm_vote_score 及连带的 llm_vote_cont 直接置 <NA>) 在 groupby sum 中被跳过而非传播为整组 NaN, 因此本列反映的是该银行-年内"可信情感样本"的 herd 加权净和, 分母口径 (sum_herd_weight 抑或 n_articles_llm_valid) 决定了最终归一化后语调的可比性, 须与产出该均值变量的下游逻辑对照才能正确解读。

【文献定位】
把跟风/羊群转载效应纳入媒体语调测度的降权处理, 方法论根源可追至 Tetlock (2007, Journal of Finance) 关于媒体内容如何赋予投资者情绪以经济含义的开创性框架——该文首次系统论证媒体文本的语调对资产价格具有可预测的因果影响, 但也隐含地提出了一个测量论问题: 若同一事件被多家媒体转载报道, 简单等权加总会使"报道数量"而非"信息增量"驱动语调测度, 本项目的 herd_weight 衰减机制正是对这一测量论关切的回应。三家大模型多数投票的情感抽取范式遵循 de Kok (2025, Management Science) 关于会计与金融研究中生成式大语言模型文本分析方法学的规范性建议——特别是 temperature=0.0、prompt 版本冻结、结果可复现缓存的范式在本项目 stage 21 (`prompt_version='v8-2026-05-17'`) 中被严格遵循。中文金融文本情感测度所依赖的语言学与制度背景, 呼应 You, Zhang & Zhang (2018, Review of Financial Studies) 对中国媒体"谁在掌握笔杆子的权力"这一制度约束的实证刻画, 以及 Du et al. (2022, Review of Finance) 关于中文金融情感词典语言/领域特异性的系统研究——尽管本家族用的是 LLM 投票而非词典法, 但两条测度路径 (dict_avg 系列与 llm_vote 系列) 在本项目中互为稳健性并排比对, 共同构成三角验证的情感测度设计。 就 llm_vote_cont{track} = llm_vote_score{track} × llm_agreement_rate{track} 这一连续化构造本身而言, Lyu 等 (2025) 提供了较为直接的方法学依据: 该文系统比较多种置信度来源, 实证表明由多次采样输出之间的一致性 (consistency) 导出的置信度, 在校准性上优于模型自报置信度与 logit 概率, 支持"以一致率而非模型自报分数充当连续置信权重"这一取向。迁移边界须诚实标明: 该文的一致性来自同一模型在正温度下的重复采样, 而本项目 temperature=0.0 且不做重复采样, agreement_rate 来自三家不同厂商模型 (gpt54nano/gemini31/deepseekv4) 的跨模型投票一致率 ∈ [1/3, 1], 属跨模型而非跨采样的一致性, 其校准性质并未被该文覆盖; 该文任务亦为英文推理/QA 基准, 不涉及中文新闻三分类情感, 更未触及本家族的 herd 加权与银行-年求和。多数票这一聚合规则本身同样是设计自由度而非唯一解: Wang、Wang 与 Huang (2025) 以排序投票 (ranked voting) 取代朴素多数票来聚合大模型的多个候选输出, 并实证其聚合质量有所提升, 为本家族上游 llm_vote_score{track} ∈ {-1, 0, 1} 的三家多数票提供了"投票规则可替换"的存在性参照。惟其投票单元是同一模型多次采样得到的候选答案 (self-consistency) 而非跨三家厂商的标签投票, 任务为推理/生成而非三分类情感标注, 聚合亦只到样本级而不涉及本项目的银行-年分组求和与 herd 加权分子; 本项目现行口径仍为朴素多数票, 并未采纳排序投票, 该文在此只作为规则选择空间的旁证, 不构成对本家族聚合方式的背书。
## VAR: llm_vote_cont_hw_sum_ctx

【变体差分】
本列取 ctx (context) 轨: 文章文本口径为"标题 + 实体窗口" (由 stage 14 materialize_ctx 物化的 content_ctx), 即环绕目标银行实体的局部窗口而非全文正文。该轨下的 herd_weight_ctx 衡量的是同银行同年报道在实体窗口局部文本上的相似度衰减, 与 full 轨基于全文正文的相似度判定是两套独立的相似度矩阵——即便同一批文章, 全文层面高度相似 (转载模板套话多) 但实体窗口周边措辞不同的两篇稿件, 在 ctx 轨可能被判定为低相似而不衰减, 在 full 轨则可能被判定为跟风稿而重度衰减, 两轨结果因此结构性分化而非同一数字的重复。llm_vote_cont{track} 分子部分同样取自 ctx 轨下 stage 21 三家 LLM 对 content_ctx 文本的独立投票结果 (三家 LLM 对 full/ctx/ss 三种文本各自单独调用打分, 而非对同一次调用结果重复贴标签)。按照本项目对三轨的一贯定位, ctx 轨与 full、ss 两轨互为稳健性并排 (各自 just-identified), 不设主次高低, 严禁将三轨同时纳入同一个 over-identified 的 Hansen J 检验; 留篇门控 (是否判定为"一篇银行金科报道") 采用 full-only 口径 (2026-06-29 起), 即 ctx 轨的行宇宙是 full 轨留篇集的子集——本列即便按 ctx 轨自身文本计算 herd_weight 与投票值, 参与求和的文章样本边界仍由 full 轨门控圈定, 因此三轨列之间的样本规模严格一致, 差异只体现在源文本与权重取值上。

## VAR: llm_vote_cont_hw_sum_full

【变体差分】
本列取 full 轨: 文章文本口径为"标题 + 全文正文" (原始 内容 列全量), 是三轨中信息量最完整、也是本项目当前留篇门控 (llm_verified_full == True) 直接依赖的主口径。llm_vote_score_full / llm_agreement_rate_full 来自三家 LLM 对全文的独立情感投票, herd_weight_full 衡量的是同银行同年报道在全文层面的文本相似度衰减——由于媒体转载/改写行为通常整篇复制或高度重叠, full 轨的相似度判定最贴近直觉意义上的"这是不是同一条通稿的转载", 因此 full 轨的 herd_weight 分布往往比 ctx/ss 轨呈现更极端的衰减 (大量近乎重复的转载稿被压至接近零权重)。本列虽在数值构造上与 ctx/ss 两轨并列, 但由于 P1 主线 (bank_fintech_tone) 的处理变量 (treatment) `llm_vote_tone_full` 及留篇门控本身均以 full 轨为准, 本列在下游被更频繁地用作构造论文主回归处理变量的原始素材; 但这不意味着本列在稳健性检验设计中享有"主轨"的统计学特权——三轨各自 just-identified 并排、互为稳健性, 仅样本行宇宙的锚定角色属于 full 轨。

需要特别说明的是, full 轨恰好是三轨中受 v3.5.x→v3.6.0 herd_weight schema 迁移影响最直接的一支: 若审计者在盘上核对某次运行的面板发现 sum_herd_weight_full 与 sum_herd_weight_ctx 数值完全相等, 应立即怀疑该次运行未重跑 stage 24 同句轨, herd_weight 退化为单列共用的 legacy 兼容分支, 此时本列虽仍可用但其"跟风衰减仅按全文相似度计算"的构念前提在事实上被三轨共享, 削弱了与 ctx/ss 两列的正交性, 须查 stage 24 日志中的 WARNING 字样以确认。使用本列做进一步换算 (除以 sum_herd_weight_full 或 n_articles_llm_valid_full 得到 herd-weight 加权银行-年语调水平) 时, 应连同分母列一并核对是否存在同一次运行内的 schema 一致性, 避免分子取自真三轨、分母取自 legacy 单轨 (或反之) 造成的口径错配。

## VAR: llm_vote_cont_hw_sum_ss

【变体差分】
本列取 ss (same-sentence) 轨: 文章文本口径为"标题 + 银行∧金科科技词同句 (±N 句窗口, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 共现窗口" (由 stage 14 物化的 content_ss), 是三轨中判定条件最严苛、文本窗口最窄的一支, 用来刻画"银行与金科科技话题在同一句紧邻共现"这一更强的相关性假设下的语调测度。ss 轨的回退语义严格镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现 (未通过更严格的同句判定), 该篇的 content_ss 退化为全文 body 且伴随 ss_is_fallback 标记为真, 此时该篇在 ss 轨的语调计算与 full 轨在事实上趋同, 但仍作为 ss 轨的独立观测参与 herd_weight_ss 与 llm_vote_cont_ss 的计算 (回退不等于剔除样本, 而是共享 n_articles 分母的降级观测)。herd_weight_ss 因此衡量的是在这一更窄、更严苛文本窗口下的跟风相似度衰减, 与 ctx、full 两轨构成结构上独立的第三套权重体系。与另外两轨一致, ss 轨与 full、ctx 互为稳健性并排, 各自 just-identified, 不得混入同一个 over-identified 的 Hansen J 检验; ss 轨的行宇宙同样被 full-only 留篇门控锚定为其子集。

由于同句判定条件比 ctx 轨的实体窗口判定更严, ss 轨的 fallback 比例通常显著高于 ctx 轨——在多数银行-年单元中, 相当一部分文章因不满足银行∧金科同句共现而回退为全文口径, 使得 llm_vote_cont_hw_sum_ss 的数值分布在很多样本点上与 full 轨高度接近, 但两者并非同一构念的重复计算: 凡是未回退 (即真正满足同句共现) 的那部分文章, ss 轨的 herd_weight 与投票值均来自更窄窗口下独立的相似度矩阵与独立的 LLM 调用, 与 full 轨结构性不同。审计或复算本列时, 应结合 ss_is_fallback 标记逐篇核对某一银行-年单元内回退文章占比, 过高的回退比例意味着该单元的 ss 轨测度实际上更接近 full 轨的稀释版本而非严格意义上的同句语调, 这一点在解读 ss 轨稳健性结果时须予以披露。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Lyu, Q., Shridhar, K., Malaviya, C., Zhang, L., Elazar, Y., Tandon, N., Apidianaki, M., Sachan, M., & Callison-Burch, C. (2025). Calibrating Large Language Models with Sample Consistency. Proceedings of the AAAI Conference on Artificial Intelligence, 39(18), 19260-19268. https://doi.org/10.1609/aaai.v39i18.34120
Wang, W., Wang, Y., & Huang, H. (2025). Ranked Voting based Self-Consistency of Large Language Models. Findings of the Association for Computational Linguistics: ACL 2025, 14410-14426. https://doi.org/10.18653/v1/2025.findings-acl.744
<!-- rendered-citations:end -->
