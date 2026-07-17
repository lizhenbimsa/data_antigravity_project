---
family_id: F394
columns:
- llm_vote_score_hw_thr40_sum_ctx
- llm_vote_score_hw_thr40_sum_full
- llm_vote_score_hw_thr40_sum_ss
unit: 无量纲加权得分之和 (银行-年层面, HW 分子, 待与对应 herd_weight 分母相除方得阈值敏感性 HW 语调比率)
formula: llm_vote_score_hw_thr40_sum{track} = groupby(target_bank, year).sum(llm_vote_score_hw_thr40{track}); 其中文章级 llm_vote_score_hw_thr40{track} = llm_vote_score{track} × herd_weight{track}_thr40, herd_weight{track}_thr40 为 stage 24 在相似度阈值 τ=0.40 (而非生产基线 τ=0.35) 下重算的跟风衰减权重
producer: pipeline\panel\encode.py::build_aggregation_dict (F5b 阈值敏感性 HW 聚合段, 消费 herd_sensitivity_grid 生成的 τ 网格与 tag) ; pipeline\panel\runner.py (步骤 3d, 生成文章级 llm_vote_score_hw_{tag}{track} 加权列) ; 上游 pipeline\sentiment\herd_decay.py (stage 24, 产 herd_weight{track}_thr40) ; core\config.py::herd_sensitivity_grid (τ 网格与列名 tag 单一事实源)
upstream:
- 21_tone_llms.parquet (llm_vote_score{track})
- 24_herd_decay.parquet (herd_weight{track}_thr40, herd_sensitivity_grid 分支)
citations:
- doi: "10.48550/arXiv.2511.15714"
  type: arxiv
  authors: "Kamen, A., & Kamen, Y."
  year: 2025
  title: "Majority rules: LLM ensemble is a winning approach for content categorization"
  venue: "arXiv"
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: "de Kok, T."
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
- doi: "10.1007/s00521-024-10603-6"
  type: journal
  authors: "Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y."
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: "Neural Computing and Applications"
  vol: "37"
  issue: "30"
  pages_or_artno: "24883-24892"
- doi: "10.1111/j.1468-0262.2005.00615.x"
  type: journal
  authors: "Romano, J. P., & Wolf, M."
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: "Econometrica"
  vol: "73"
  issue: "4"
  pages_or_artno: "1237-1282"
- doi: "10.1111/j.1540-6261.2010.01625.x"
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: "Journal of Finance"
  vol: "66"
  issue: "1"
  pages_or_artno: "35-65"
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
本家族的三列 (ctx/full/ss) 是银行-年面板层面 "LLM 投票语调 × 跟风衰减权重" 加权和的一个稳健性分支, 归属阈值敏感性网格族。它衡量的不是语调水平本身, 而是把每篇文章的 LLM 投票语调得分 (llm_vote_score, 三家大模型 gpt54nano/gemini31/deepseekv4 多数投票得到的离散/连续折衷分数, 归属 stage 21) 按"这篇报道有多像抄稿跟风"打折后, 在给定银行-年内累加得到的分子。折扣权重来自 stage 24 的跟风衰减处理: 若一篇报道与同银行同期其他报道的文本相似度 (余弦相似度) 超过某判定门槛, 就被视为"抄稿/跟风", 权重随相似度上升而衰减到接近 0; 反之独立成文的报道权重接近 1。生产口径的判定门槛是 τ=0.35 (config/sentiment.yaml::herd_detection.similarity_threshold, 研究者自由选定的参数, 无先验文献定值), 对应的基线列是不带阈值后缀的 herd_weight{track}/llm_vote_score_hw_sum{track}。本家族的 "thr40" 后缀表示: 把这个自由参数从 0.35 换成 0.40 (门槛更松, 判定"跟风"更严格 — 只有相似度更高的一小撮报道才会被打折, 因此同一批文章在 τ=0.40 下平均权重通常不低于 τ=0.35 下的权重), 重新走一遍相同的衰减公式和相同的加权求和逻辑, 产出一套平行的分子列。它与基线列、以及 config 里另外三个网格点 (τ∈{0.25, 0.30, 0.45}) 共同构成一把"换一个抄稿判定门槛"的敏感性梯子, 五个分支各自独立、平行存在, 目的是向读者证明: 银行-年层面的 LLM 加权语调结论不是靠 0.35 这一个具体取值堆出来的, 换成更松或更紧的判定标准, 加权语调的量级和符号仍然稳定。

【方法学与计算】
计算分两层, 分层归属不同 stage。第一层在 stage 24 (herd_decay.py) 完成: 对同一目标银行、同一时间窗口内的文章两两计算文本相似度 (基于既有的语义或词面表示), 凡相似度 ≥ τ 的报道对被记为"跟风对", 每篇文章的最终权重是一个随其与"最近的高相似同类报道"距离单调递减的衰减函数, 值域压缩在 [0, 1] 区间 (不是简单的 0/1 二值剔除, 而是连续衰减, 抄得越像权重越接近 0, 完全原创权重接近 1)。这一层对 τ=0.40 单独重算一遍, 产出文章级列 herd_weight{track}_thr40, 与基线 herd_weight{track} 是两条完全平行、互不覆盖的列。第二层在 runner.py 步骤 3d 与 encode.py 的聚合阶段完成: 先把文章级 llm_vote_score{track} 与 herd_weight{track}_thr40 逐行相乘得到 llm_vote_score_hw_thr40{track}, 再在 encode.py::build_aggregation_dict 的 F5b 段内, 按 (target_bank, year) 分组对这一乘积列求和, 得到本家族三列。needs 强调的是: 本家族只是"分子和", 它本身不是一个可以直接拿来读数的"平均语调"指标 —— 下游 Stata 面板/模板会再拿它去除以对应的 sum_wd_hw_thr40_llm{track} (有效样本加权分母, 只数 LLM 判断有效的文章), 相除后才得到可解释的 llm_vote_tone_hw_thr40{track} 加权平均语调。之所以把分子单独落一列而不是直接落比率列, 是为了保留可加性 (方便跨截面再聚合、方便审计每个环节), 也是全部 HW/MW/VW 加权族在本项目里的统一做法。三个 τ∈{0.25,0.30,0.40,0.45} 网格分支与基线 0.35 的口径、公式、聚合方式完全同构, 唯一差异是喂入衰减函数的判定门槛数值; 网格本身由 core/config.py::herd_sensitivity_grid 统一生成并做粒度校验 (仅接受 0.01 粒度、开区间 (0,1) 内的数值, 越界或非法项跳过并告警, 与基线重合的门槛自动去重不重复生成列), 是本梯子列名 tag (thr25/thr30/thr40/thr45) 与全部下游消费方共享的唯一事实源。

【文献定位】
把 LLM 多家模型的判断汇聚为一个共识分数再加权聚合, 呼应大模型集成投票 (LLM ensemble) 优于单一模型的稳健性证据: Kamen & Kamen (2025) 系统比较了多数投票式集成在内容分类任务上相对单模型的胜率优势, 支持本项目用三家 (gpt54nano/gemini31/deepseekv4) 多数投票而非单家模型作为语调测度主轨的设计选择。把大模型判断落地为可复现的结构化面板列, 依赖冻结 prompt、零温度采样与结果缓存的方法学纪律, de Kok (2025, *Management Science*) 系统梳理了会计与金融研究中使用生成式大模型做文本标注时, temperature=0、prompt 版本冻结、结果可复现缓存这一套范式的必要性与陷阱, 与本项目 stage 21 的 prompt v8 字节级冻结、`_llm_cache.db` 离线可复现锚点直接对应。中文金融文本情感的细粒度大模型标注也已有本土化验证: Lan 等 (2025, *Neural Computing and Applications*) 针对中文金融文本构建细粒度情感标注体系并用大模型实现实体级情感抽取, 佐证在中文语境下用大模型判读语调是可行且有文献先例的技术路线。而"要不要相信一个自由选定的判定门槛"这一稳健性诉求, 在计量文献中有更早的方法学根基: Romano & Wolf (2005, *Econometrica*) 提出的逐步式多重检验框架正是为"同一构念下用多个候选设定重复检验、又要控制整体假发现率"这一类问题提供的形式化工具, 本项目虽未把阈值敏感性网格直接接入 rwolf 式的联合检验 (网格本身走的是并排稳健性叙事而非联合 FWER 表), 但其"多设定并排、不以单一自由参数定论"的精神与该文一致。最后, 语调测度本身作为文本分析在金融研究中的合法性, 溯源自 Loughran & McDonald (2011, *Journal of Finance*) 对基于词典/规则的文本情感测度构造与验证方法的奠基性工作 —— 本项目虽然主测度改用大模型判读, 但"给定一个可复现的规则/模型, 把文本转成可加总的数值语调, 再按权重聚合到面板层面"这一整体范式仍与该文一脉相承。

需要特别强调项目内部的口径铁律: full/ctx/ss 三轨在下方各自成列, 是各自独立、just-identified 并排的稳健性口径, 互为稳健性、不分主次, 严禁把三轨的任何组合混进同一个 over-identified 的 Hansen J 过度识别检验里 (这是三轨架构与 co-primary 双轨嵌入共用的项目级铁律)。同理, τ=0.40 与基线 τ=0.35 及网格其余分支 (0.25/0.30/0.45) 也是各自 just-identified 的并排稳健性分支, 不构成一组可以联合过度识别的工具集。此外, n_articles/留篇门控口径遵循 2026-06-29 起生效的 full-only 铁律: 是否判定某银行-年内某篇报道"算数" (即纳入分母), 只看 full 轨的 llm_verified_full 是否为真; ctx/ss 两轨的样本行宇宙是 full 留篇集合的子集, 在此子集内各自按 ctx/ss 口径独立计算权重和加权和, 不借用彼此的分母, 也不倒过来影响 full 轨的留篇判定。 在分子所依赖的"LLM 标签→面板聚合"一环上, 尚有数项前沿工作可补足本族的方法学定位。Ornstein、Blasingame 与 Truscott (2025) 以 few-shot prompt 在情感分析、文档标度等政治学文本即数据任务上做预注册评估, 证明该路径优于传统有监督学习基线、并以极低成本达到与专家及众包编码员相当 (comparable, 非超过) 的水平, 是"直接用大模型产出文本级标签再逐单元聚合"这一测量范式在社会科学内的同族先例, 与上文 Loughran & McDonald (2011) 所代表的词典范式恰构成同一谱系的两端; 其语料为英文政治文本、单模型而非三家投票, 无跟风加权与 bank-year 聚合。Wang、Wang 与 Huang (2025) 以排序投票 (ranked voting) 取代朴素多数票来聚合大模型的多个候选输出并实证聚合质量提升, 说明本族分子 llm_vote_score 所用的多数票规则本身即是一重设计自由度, 与 τ 门槛一样属于研究者选择而非文献定值; 惟其投票单元是同一模型多次采样的候选答案 (self-consistency) 而非跨三家厂商的标签票, 任务为推理生成而非三分类情感, 本项目仍维持朴素多数票、未采纳排序投票, 该维度目前未构成一条并排的稳健性梯子。Rønningstad 与 Velldal (2024) 评估大模型对特定目标实体的情感 (entity-level / targeted sentiment) 标注质量并与人工标注对比, 直接对应本族"针对目标银行"而非篇章整体的语调构念; 其语料为挪威语/英语通用新闻、目标实体非银行, 采用单一 GPT 模型且只报告标注一致性, 不做面板聚合与加权分子构造。Kim、Muhn 与 Nikolaev (2024) 向 GPT-4 提供剥离叙事的标准化财务报表令其判断企业未来盈余的变动方向, 实证其方向性预测超过人类分析师、与窄训练的 SOTA 机器学习模型相当, 并据以构建出更高 Sharpe 比率与 alpha 的策略, 是"令大模型作离散方向性判断、再把该判断聚合为可用金融信号"在金融领域的前沿存在性证明; 其输入为报表数字而非中文新闻叙事, 单位为公司-季度盈余方向而非银行-年语调, 且为单模型无跨厂商投票。四文均只锚定分子的离散标签一环, 对 τ=0.40 这一跟风判定门槛及整条阈值梯子不构成依据。
## VAR: llm_vote_score_hw_thr40_sum_ctx

【变体差分】
本列是 ctx 轨的 HW 阈值敏感性分子和, 即 llm_vote_score_hw_thr40_sum{track} 公式中 track=_ctx 的实现。ctx 轨的文章级底层文本是"标题 + 实体窗口" (围绕目标银行/金科实体截取的上下文片段, 而非全文), 对应的 llm_vote_score_ctx 与 herd_weight_ctx_thr40 均基于这一截取文本计算: 前者是三家大模型在 ctx 文本上给出的投票语调, 后者是在 ctx 文本表示空间内, 以 τ=0.40 作为跟风判定门槛重算的衰减权重 (与 full 轨、ss 轨各自独立计算, 不共享相似度矩阵)。当某篇文章不存在可截取的实体窗口 (即 ctx_is_fallback=True) 时, 该文章的 ctx 轨退化为使用全文 body 兜底, 相应的语调与权重也随之退化为全文口径下的取值, 这一回退不改变分母口径 (仍与 full 轨共享 n_articles, 但 ctx 轨的具体加权求和只在留篇门控通过的样本子集上进行)。ctx 轨与 full 轨、ss 轨在本项目里是并排的稳健性测量口径而非互相替代关系: full 轨捕捉整篇报道的语调, ctx 轨聚焦"围绕目标实体"的局部语境语调, 二者数值有系统性差异 (ctx 通常语调更聚焦、噪声更小但样本可用性受实体窗口截取成功率制约) 完全在预期之内, 不应被解读为测量误差。使用者若需要把 τ=0.40 门槛下的 ctx 轨加权语调落到可解释的比率, 需要另行除以对应的 sum_wd_hw_thr40_llm_ctx (有效样本加权分母), 本列本身只提供分子。

## VAR: llm_vote_score_hw_thr40_sum_full

【变体差分】
本列是 full 轨的 HW 阈值敏感性分子和, 即公式中 track=_full 的实现, 是本项目留篇门控与 P1 主处理变量共同锚定的口径。full 轨的底层文本是"标题 + 全文正文" (无截取), llm_vote_score_full 是三家大模型基于完整报道给出的投票语调, herd_weight_full_thr40 是在全文文本表示空间内、以 τ=0.40 为跟风判定门槛重算的衰减权重。按 2026-06-29 生效的 full-only 留篇门控铁律, 一篇报道是否被算作"一篇有效的银行-金科报道"、进而是否纳入本列所在银行-年的求和范围, 判定依据只看 llm_verified_full 是否为真; ctx/ss 两轨的样本行宇宙是本轨留篇集合的子集。也正因如此, full 轨的加权和是三轨里样本覆盖最完整、口径最贴近"整篇报道综合语调"的一支, 项目主线论文 (P1 bank_fintech_tone) 的核心处理变量 llm_vote_tone_full 及其阈值敏感性稳健表所引用的分支, 均以本轨 (以及基线 τ=0.35 下的对应列) 为主要参照, 但这并不意味着本列本身在三轨间"更优"或应被优先看待 —— 三轨仍是互为稳健性、不分主次的并排设计, full 轨只是恰好承担了留篇门控锚点这一额外角色。数值上, 本列理应是三轨中样本覆盖 (求和所涉文章数) 最大或至少不小于 ctx/ss 两轨的一支, 因为后两轨的行宇宙是本轨的子集。

## VAR: llm_vote_score_hw_thr40_sum_ss

【变体差分】
本列是 ss 轨的 HW 阈值敏感性分子和, 即公式中 track=_ss 的实现。ss 轨的底层文本是"标题 + 目标银行与金科词严格同句共现窗口" (较 ctx 轨的实体窗口更窄, 要求银行实体与金科词在同一句内共同出现, 句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认半径 1), 对应的 llm_vote_score_ss 与 herd_weight_ss_thr40 均基于这一更紧的同句文本计算。ss 轨的回退语义镜像 ctx 轨: 当某篇文章不存在银行与金科词的同句共现时 (ss_is_fallback=True), 该文章的 ss 轨退化为使用全文 body 兜底, 语调与权重相应退化为全文口径下的取值, 分母仍与 full 轨共享 n_articles, 但求和范围仍受 full-only 留篇门控约束, 只在门控通过的子集内进行。由于同句共现的判定条件比 ctx 轨的实体窗口更严格, ss 轨通常是三轨中触发回退 (fallback) 比例相对最高、"真实"同句样本占比相对最低的一支, 这是该轨设计上刻意收紧构念 (只测"同一句话里银行和金科词放在一起讨论"这种最紧密的共现关系) 的自然结果, 不构成数据质量问题。ss 轨与 ctx 轨、full 轨三者在阈值敏感性梯子 (τ=0.40) 下各自独立走完整套衰减与加权求和流程, 互不借用彼此的相似度矩阵或权重, 是并排、互为稳健性、不分主次的稳健性分支之一。

<!-- rendered-citations:begin -->
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Ornstein, J. T., Blasingame, E. N., & Truscott, J. S. (2025). How to train your stochastic parrot: large language models for political texts. Political Science Research and Methods, 13(2), 264-281. https://doi.org/10.1017/psrm.2024.64
Wang, W., Wang, Y., & Huang, H. (2025). Ranked Voting based Self-Consistency of Large Language Models. Findings of the Association for Computational Linguistics: ACL 2025, 14410-14426. https://doi.org/10.18653/v1/2025.findings-acl.744
Rønningstad, E., Velldal, E., & Øvrelid, L. (2024). A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation. Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII), 133-139. https://doi.org/10.18653/v1/2024.law-1.13
Kim, A., Muhn, M., & Nikolaev, V. (2024). Financial Statement Analysis with Large Language Models. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2407.17866
<!-- rendered-citations:end -->
