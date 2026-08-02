---
family_id: F405
columns:
- llm_vote_tone_sum_ctx
- llm_vote_tone_sum_full
- llm_vote_tone_sum_ss
unit: 语调净值加总 (整数计数, 篇级 +1/0/-1 的 bank-year 内求和; 非均值, 无固定量纲上限)
formula: 'llm_vote_tone_sum{track} = sum(llm_vote_score{track}), 其中 llm_vote_score{track} ∈ {+1, 0, -1} 是同一 bank-year 下逐篇文章「三家 LLM (gpt54nano / gemini31 / deepseekv4) 多数投票」得到的篇级净情感标签; 聚合入口 pipeline/panel/encode.py::build_agg_spec, agg[f"llm_vote_tone_sum{track}"] = (f"llm_vote_score{track}", "sum")'
producer: pipeline\panel\encode.py
upstream:
- pipeline/sentiment/tone_llms.py
- pipeline/panel/encode.py
citations:
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for textual analysis? How to use generative LLMs in accounting research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating large language model annotations
  venue: Federal Reserve Board FEDS Working Paper
  vol: '2026-020'
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
- doi: "10.1287/mnsc.2024.08999"
  type: "journal"
  authors: "Burtch, G., McFowland, E., Yang, M., & Adomavicius, G."
  year: 2026
  title: "EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables"
  venue: "Management Science"
  pages_or_artno: "mnsc.2024.08999"
- doi: "10.1007/s42001-025-00388-6"
  type: "journal"
  authors: "Abraham, L., Arnal, C., & Marie, A."
  year: 2025
  title: "Prompt selection matters: enhancing text annotations for social sciences with large language models"
  venue: "Journal of Computational Social Science"
  vol: "8"
  issue: "3"
  pages_or_artno: "73"
new_dois: []
---

## CORE

【构念与来源】
llm_vote_tone_sum 家族衡量的是某银行在给定年度内、经三家大语言模型 (LLM) 独立打分后多数投票产生的篇级净情感标签, 在该 bank-year 样本内的加总值。它的构念起点不是词典打分, 也不是单一模型的连续概率输出, 而是「三家模型各自读同一篇文章、各自给出 +1(正面)/0(中性)/-1(负面) 的离散判断、再取多数一致的结果」这一投票机制产生的篇级共识标签 llm_vote_score。三家模型分别是 gpt54nano (对应 gpt-5.4-nano)、gemini31 (对应 gemini-3.1-flash-lite, 经 OpenLux 中转)、deepseekv4 (对应 deepseek-v4-flash, 直连 api.deepseek.com); 三者独立打分互不共享上下文, 投票聚合发生在 stage 21 情感 LLM 阶段, 产出的 llm_vote_score 是后续所有 llm_vote_* 面板列 (含本家族) 的共同上游。llm_vote_tone_sum 本身在家族体系里属于「计数聚合」而非「均值聚合」的姊妹列: 与其并列存在的 llm_vote_tone (bank-year 均值) 度量的是「平均语调水平」, 而 llm_vote_tone_sum 度量的是「净正面篇数减净负面篇数」的绝对规模——两者在样本篇数不均衡 (例如某银行某年报道量显著多于同侪) 时会给出方向一致但幅度含义不同的信息, 前者做跨银行水平比较更合适, 后者做同一银行跨年度暴露强度比较、或作为需要「总量」而非「强度」的下游回归权重更合适。

【方法学与计算】
计算链路起于 stage 21 (`pipeline/sentiment/tone_llms.py`), 三家 LLM 各自对每篇文章、每个文本轨道输出一个离散标签 (正/中/负), 随后取多数一致规则合成 llm_vote_score{track} ∈ {+1, 0, -1} (三家不一致时退为 0, 即中性/不确定)。该篇级标签经 `pipeline/panel/encode.py::build_agg_spec` 中的聚合规格表以 `(f"llm_vote_score{track}", "sum")` 方式在 bank-year 分组上求和, 得到 llm_vote_tone_sum{track}; dtype 为 int64, 因为求和对象是 {-1,0,1} 的整数标签而非连续分数, 数值范围随该 bank-year 内的有效篇数 (`n_articles_llm_valid{track}`) 扩张, 没有先验的 [-1,1] 上限——这一点是本家族与家族体系里大多数「语调得分」家族 (通常聚合后落在 [-1,1] 区间) 最直观的区别, frontmatter 的 unit 字段特别标注「整数计数, 非均值」正是为了防止使用者把它当作可比水平量误用。
本家族严格遵循全仓「留篇门控 = full-only」口径 (2026-06-29 铁律): 一篇文章是否被计入「该银行金融科技相关报道」的判定只看 full 轨的 `llm_verified_full == True`, ctx/ss 是在该留篇集合子集上的条件测度轨, 并不各自独立决定留篇。三个轨道 (`_full`/`_ctx`/`_ss`) 各自基于同名文本切片独立跑通投票与聚合流水线, full=标题+全文正文, ctx=标题+实体上下文窗口, ss=标题+银行与金科词同句 (±N 句可配) 共现窗口; 三者是并排的「互为稳健性、不分主次」测度, 任何计量设定都不得把三轨同时塞进同一个 over-identified 的 Hansen J 过度识别检验——这不是写作习惯问题, 而是因为三轨文本高度重叠, 混用会人为制造工具变量之间的机械相关, 使过度识别检验的拒绝/不拒绝结论失去经济学含义。_ss 轨的回退语义镜像 _ctx: 当某篇文章不存在银行与金科词的同句共现时, `content_ss` 退化为全文 body 且 `ss_is_fallback` 记为真, 与 `n_articles` 分母共享同一套统计口径, 保证降级不会造成分母口径漂移。

【文献定位】
多数投票聚合的方法学正当性直接对应集成学习/LLM 集成文献的近期发现: Kamen & Kamen (2025) 系统评估了多模型集成用于内容分类任务的表现, 发现多数投票规则相对单模型标注能显著降低标注噪声、提升与人工基准的一致性, 这为本项目选择「三家独立打分 + 多数投票」而非依赖单一供应商模型提供了直接支撑。de Kok (2025, *Management Science*) 系统讨论了如何在会计与金融研究中规范使用生成式 LLM 做文本分析, 强调 temperature=0、prompt 版本冻结与结果缓存等可复现范式——这与本仓库 stage 21 的 `prompt_version='v8-2026-05-17'`、`temperature=0.0` 冻结锚点及 `_llm_cache.db` 确定性可复现设计完全对应, 是本家族计算流程正当性的方法学锚点。Tetlock (2007, *Journal of Finance*) 是文本语调影响资产价格这一实证传统的奠基性工作, 确立了「媒体语调净值」作为可预测收益率与投资者情绪的解释变量这一构念范式, llm_vote_tone_sum 作为该净值构念在 LLM 时代的离散计数化身, 在方法上继承了这条脉络, 但用三家模型投票取代了传统词典计数。Hansen (2026, FEDS WP) 讨论了在缺乏金标准的场景下如何验证 LLM 标注质量, 呼应了本仓库用 Krippendorff's α 与 Cohen's κ 度量三家模型间一致性、并把不一致样本记为中性 (0) 而非强行分类的保守处理策略。 近期文献在若干方向上进一步收紧了本族的定位。Ornstein、Blasingame 与 Truscott (2025) 以 few-shot prompt 在情感分析、文档标度等政治学「文本即数据」任务上做预注册评估, 结论是该做法优于传统有监督学习基线、并以极低成本达到与专家及众包编码员相当 (而非超过) 的水平, 是「LLM 直接产出文本级标签再逐单元聚合」这一测量范式的同族先例, 直接支撑本族 llm_vote_score → bank-year 求和的链路; 其语料为英文政治文本, 且采用单一模型而无三家投票、无面板聚合与三轨切分。Rønningstad 与 Velldal (2024) 评估 LLM 对特定目标实体的情感 (entity-level sentiment) 标注质量并与人工标注对比, 呼应本族「针对目标银行」而非篇章整体的构念界定; 该文目标实体非银行、语料非中文金融新闻, 仅报告标注一致性而不涉及加权分子与面板聚合。Wang、Wang 与 Huang (2025) 以排序投票取代朴素多数票聚合 LLM 的多个候选输出并实证其质量提升, 提示投票规则本身是一处设计自由度而非唯一解; 但其投票单元是同一模型多次采样的候选答案 (self-consistency) 而非跨厂商标签, 本族仍维持朴素多数票, 故该文只作为「多数票非唯一选择」的存在性参照。Kim、Muhn 与 Nikolaev (2024) 向 GPT-4 提供剥离叙事的标准化财务报表以判断未来盈余变动方向, 实证其方向性预测准确率超过人类分析师、与窄训练的 SOTA 机器学习模型相当, 并据其构建的策略取得更高 Sharpe 比率, 是「LLM 离散方向性判断可作为可聚合金融信号」的前沿存在性证明; 边界在于其输入为报表数字而非中文新闻叙事、单位为公司-季度盈余方向而非银行-年语调、单模型而无跨厂商投票, 且其摘要未载自报置信度的使用, 故不得据此为本仓库任何 (label, confidence) → 概率分的映射背书 (本族本就只消费离散标签, 不涉该映射)。就下游使用而言, Burtch、McFowland、Yang 与 Adomavicius (2026) 利用集成学习器内部成员预测之间的差异构造工具变量, 以缓解 ML 生成变量作为回归元时的测量误差偏误, 与本族「多个异构模型对同一篇文章各自打分、成员间存在系统性差异」的结构同构, 提示本族作为 ML 生成变量进入回归时的测量误差是一个已被正视且已有已发表处理路径的问题; 但其集成成员是同一训练流程下的 ML 预测器、成员差异有明确的重采样来源, 而本族成员是三家闭源 LLM, 差异来源不可控亦不可重采样, 其构造 IV 的前提未必成立——本仓库并未实施 EnsembleIV, 该文亦不得被援引为把三家 per-model 列混入同一 over-identified Hansen J 的依据, 后者与桶内各测度各自 just-identified 并排、互为稳健性不分主次的口径铁律直接冲突。最后, Abraham、Arnal 与 Marie (2025) 实证表明 prompt 选择对社科文本标注质量有显著且非平凡的影响, 并给出一套 prompt 选择与评估流程; 本仓库 prompt v8 已字节级冻结并充当缓存键, 刻意不做 prompt 网格 (改 prompt 即全缓存作废), 故该文提示的 prompt 敏感性在本族属未量化的已知局限, 而非已排除的风险, 使用者解读本族数值时应将其计入测量不确定性的来源之一。
## VAR: llm_vote_tone_sum_ctx

【变体差分】
本列是 llm_vote_tone_sum 家族的 ctx (实体上下文) 轨。它复用与 full 轨完全相同的三家 LLM 多数投票机制与求和聚合公式, 唯一差异是喂给三家模型的文本切片不同: full 轨输入标题+全文正文, ctx 轨输入标题+围绕目标实体 (银行/金科关键词) 的上下文窗口截取, 是一个更聚焦、噪声更少但可能损失整体语境的文本变体。留篇门控严格遵循 full-only 铁律——本列的行宇宙 (哪些 bank-year 有值) 由 full 轨的 `llm_verified_full == True` 决定, ctx 轨本身不独立产生留篇判定, 是 conditional-on-full 的测度/稳健性轨, 而非另一套独立样本。ctx 轨与 full 轨、ss 轨三者互为稳健性并排存在, 不分主次, 任何计量模型都不得把三轨同时作为工具变量塞进同一个 over-identified Hansen J 检验; 正确用法是分别在三轨上各自复算核心回归、比较系数符号与显著性是否稳健一致。当某篇文章因缺少可识别实体上下文而无法构造 ctx 切片时, 该篇不参与本轨聚合 (源列缺失由 `valid_agg` 自动过滤), 但不影响 full 轨或 ss 轨各自独立的完整性。使用建议: 若研究问题关心「聚焦实体本身的语调净值总量」而非全文整体语调, ctx 轨比 full 轨更贴近构念; 若做跨年度暴露强度比较, 仍须与同 bank-year 的 `n_articles` 或 `n_articles_llm_valid_ctx` 联合解释, 因为本列是未经篇数标准化的绝对计数。

## VAR: llm_vote_tone_sum_full

【变体差分】
本列是 llm_vote_tone_sum 家族的 full (全文) 轨, 也是三轨中的门控锚——全仓「留篇门控 = full-only」铁律 (2026-06-29) 规定: 一篇文章是否算作「该银行的一篇金融科技相关报道」, 唯一判据是 full 轨的 `llm_verified_full == True`, 与 ctx/ss 两轨的验证结果无关。本列的输入文本是标题+全文正文 (prepend_title 拼接, 原始「内容」列不改动), 三家模型 (gpt54nano/gemini31/deepseekv4) 各自独立读完整文本给出离散标签, 多数投票合成 llm_vote_score_full, 再在 bank-year 上求和得到本列。作为门控锚, full 轨天然拥有三轨中最完整、最不受切片截断影响的行宇宙, ctx 轨与 ss 轨的样本集合都是 full 轨留篇集合的子集 (conditional-on-full), 因此在做「样本量最大化」或「作为主回归设定」的场景下, full 轨通常是首选测度, 但这并不意味着它在识别策略上「优于」ctx/ss——三轨在方法论上仍是并排的互为稳健性关系, 不分主次, 严禁混入同一个 over-identified Hansen J 检验。本列与家族内 `llm_vote_tone_full` (均值) 互补: 前者告诉你「净情感总量有多大」, 后者告诉你「平均情感水平有多正/负」, 两者结合可以区分「该银行报道量大但语调温和」与「报道量小但语调极端」这两种截然不同的情形, 单看其中一列容易得出误导性结论, 建议二者联合报告作为主设定的一部分。

## VAR: llm_vote_tone_sum_ss

【变体差分】
本列是 llm_vote_tone_sum 家族的 ss (同句共现) 轨, 输入文本是标题+银行与金科关键词严格同句 (或按 `config/filtering.yaml::context_window.ss_sentence_radius` 配置的 ±N 句窗口, 默认 N=1) 共现片段, 是三轨中判据最严格、文本粒度最小的一支, 意在剔除「同篇报道里银行与金科话题各说各话、并无真实语义关联」的稀释噪声。计算与聚合逻辑与 full/ctx 两轨完全对称: 三家 LLM 各自对该同句共现片段独立打分, 多数投票得到 llm_vote_score_ss, 按 bank-year 求和得到本列。留篇门控同样遵循 full-only 铁律, 本列样本是 full 轨留篇集合的子集, 不独立扩大或收窄行宇宙。ss 轨有明确的回退语义, 且该回退语义严格镜像 ctx 轨: 当某篇文章不存在银行词与金科词的同句 (或窗口内) 共现时, `content_ss` 优雅退化为全文 body, 对应的 `ss_is_fallback` 标记置真, 该篇仍计入聚合但使用的实际是全文文本而非严格同句片段, 且与 `n_articles` 共享同一分母口径, 不会因回退而产生行数漂移或分母孤儿; 若 `FINTECH_AC` 词典解析失败为 None, 则全部 `*_is_fallback` 置真, 整个 ss 轨优雅降级为等同 full 轨内容。ss 轨与 full/ctx 两轨并排互为稳健性, 是判据最严格的一端, 三者共同构成一个从「宽松 (full)」到「聚焦 (ctx)」再到「严格 (ss)」的稳健性谱系, 但排列顺序本身不构成优先级, 计量应用中三轨系数方向与显著性的一致性才是稳健性论证的核心, 严禁把三轨同时作为工具变量塞入同一个 over-identified Hansen J 检验。

<!-- rendered-citations:begin -->
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Hansen, A. L. (2026). Validating large language model annotations. Federal Reserve Board FEDS Working Paper [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Ornstein, J. T., Blasingame, E. N., & Truscott, J. S. (2025). How to train your stochastic parrot: large language models for political texts. Political Science Research and Methods, 13(2), 264-281. https://doi.org/10.1017/psrm.2024.64
Wang, W., Wang, Y., & Huang, H. (2025). Ranked Voting based Self-Consistency of Large Language Models. Findings of the Association for Computational Linguistics: ACL 2025, 14410-14426. https://doi.org/10.18653/v1/2025.findings-acl.744
Rønningstad, E., Velldal, E., & Øvrelid, L. (2024). A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation. Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII), 133-139. https://doi.org/10.18653/v1/2024.law-1.13
Kim, A., Muhn, M., & Nikolaev, V. (2024). Financial Statement Analysis with Large Language Models. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2407.17866
Burtch, G., McFowland, E., Yang, M., & Adomavicius, G. (2026). EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables. Management Science, mnsc.2024.08999. https://doi.org/10.1287/mnsc.2024.08999
Abraham, L., Arnal, C., & Marie, A. (2025). Prompt selection matters: enhancing text annotations for social sciences with large language models. Journal of Computational Social Science, 8(3), 73. https://doi.org/10.1007/s42001-025-00388-6
<!-- rendered-citations:end -->
</content>
