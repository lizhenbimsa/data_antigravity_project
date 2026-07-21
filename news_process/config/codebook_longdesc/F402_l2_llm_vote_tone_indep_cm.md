---
family_id: F402
columns:
- llm_vote_tone_indep_cm_ctx
- llm_vote_tone_indep_cm_ss
unit: 语调得分 (连续, 约 [-1,1]; 三家 LLM 多数投票语调在"自主研发"分类子集上按 bank-year 聚合的均值)
formula: 'llm_vote_tone_indep_cm_{ctx,ss} = mean_over_articles(llm_vote_tone_{ctx,ss}) restricted to innovation_collab_mode_{ctx,ss} == 自主研发 (对角追加, _aggregate_ctx_diagonal); 分母 n_articles_indep_cm_{ctx,ss} 同批产出, 供 indep_frac_cm_{ctx,ss} 与 tone_gap_indep_collab_cm_{ctx,ss} (min-n>=5 双边守门) 复用'
producer: pipeline\panel\encode.py
upstream:
- 21_tone_llms.parquet (llm_vote_tone_ctx / llm_vote_tone_ss 篇级三家多数投票语调)
- 16_article_policy_alignment.parquet 或等价 collab 分类产出 (innovation_collab_mode_ctx / innovation_collab_mode_ss, 篇级二分类 自主研发/外部协同)
citations:
- doi: 10.1145/3711896.3737219
  type: journal
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: 'FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models'
  venue: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)
  pages_or_artno: 5117-5128
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: 'Firm-Level Political Risk: Measurement and Effects'
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: 'On the Fintech Revolution: Interpreting the Forces of Innovation, Disruption, and Transformation in Financial Services'
  venue: Journal of Management Information Systems
  vol: '35'
  issue: '1'
  pages_or_artno: 220-265
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: "10.1017/psrm.2024.64"
  type: "journal"
  authors: "Ornstein, J. T., Blasingame, E. N., & Truscott, J. S."
  year: 2025
  title: "How to train your stochastic parrot: large language models for political texts"
  venue: "Political Science Research and Methods"
  vol: "13"
  issue: "2"
  pages_or_artno: "264-281"
- doi: "10.18653/v1/2024.law-1.13"
  type: "journal"
  authors: "Rønningstad, E., Velldal, E., & Øvrelid, L."
  year: 2024
  title: "A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation"
  venue: "Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII)"
  pages_or_artno: "133-139"
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
llm_vote_tone_indep_cm 一族衡量的是"当一篇银行∧金科报道被 LLM 判定为描述银行自主研发型创新时, 该篇报道语调三家多数投票的均值"。cm 后缀标记这是 innovation_collab_mode 分类维度 (自主研发 vs 外部协同) 与 llm_vote_tone 语调测度的交叉切片, 是 P5 (collab, provisional) 与 P1 (tone) 两条主线在篇级证据上的对角线拼接; P5 的分类构念本身的理论根据统一归于 Gomber, Kauffman, Parker & Weber (2018) 的金融科技创新形态分类框架 (详见【文献定位】), 本段仅先点出族内两条主线的拼接关系, 不重复其理论出处: 母面板已分别产出 innovation_collab_mode_{ctx,ss} (篇级二分类, 由三家 LLM `{gpt54nano,gemini31,deepseekv4}` 投票裁定该篇报道所写的银行-金科合作事件属于银行自建能力"自主研发"还是引入外部主体"外部协同") 与 llm_vote_tone_{ctx,ss} (篇级语调多数投票共识, 三分类或连续打分聚合到约 [-1,1] 区间)。indep_cm 族不是重新跑一次分类或情感, 而是在既有两批篇级列基础上做条件均值: 先按 innovation_collab_mode == 自主研发 筛出子集, 再对这个子集求 llm_vote_tone 的均值, bank-year 层聚合。姊妹族 collab_cm (未在本家族内, 见并列列 llm_vote_tone_collab_cm_{ctx,ss}) 是同一操作在 外部协同 子集上的镜像, 两者相减且经 min-n>=5 双边质量守门后得到 tone_gap_indep_collab_cm_{ctx,ss}, 用于检验"自主研发型报道"与"外部协同型报道"在语调上是否存在系统性差异 (媒体是否对自建能力叙事更正面, 或反之)。

本家族仅含 _ctx 与 _ss 两条轨, 均属 standard tier, 无 _full 轨在本族出现 (llm_vote_tone_indep_cm 本身在 encode.py 中是 _aggregate_ctx_diagonal 的产物, 该 helper 专为 ctx/ss 实体窗口/同句共现轨设计, 对角追加逻辑不覆盖 full 轨; full 轨的对应机制稳健性口径由未分轨的 collab_frac 系列或 P5 主表其他列承担, 不在本家族重复)。按 CLAUDE.md「三轨 full/ctx/ss…各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J」的铁律, _ctx 与 _ss 两轨在计量设计中应分别进入各自的识别方程作为并排稳健性检验, 不得把二者同时塞进同一个过度识别 Hansen J 检验; 由于本族缺 _full 成员, 使用者若要构造三轨对照表须知晓这是设计使然而非疏漏。 在 LLM 标注链路的方法学坐标上, Ornstein、Blasingame 与 Truscott (2025) 以 few-shot prompt 在情感分析、文档标度、主题建模等政治学文本即数据任务上做预注册评估, 结论是该做法优于传统有监督学习基线, 并以极低成本达到与专家及众包编码员相当 (comparable, 非超过) 的水平, 是本族"先由 LLM 产出篇级标签 (语调与 collab mode)、再按 bank-year 逐单元聚合"这一范式的同族先例; 其语料为英文政治文本、采用单一模型而非三家投票, 也无本族的分类条件切分与 ctx/ss 双轨口径, 故只锚定标签→聚合的链路形态。Rønningstad 与 Velldal (2024) 评估 LLM 对特定目标实体的 entity-level 情感标注质量并与人工标注对比, 与本族条件均值所取的 llm_vote_tone 构念 (针对目标银行而非篇章整体的语调) 同族, 也与 ctx/ss 两轨围绕实体窗口取材的设计相呼应; 但原文语料为挪威语/英语通用新闻与评论、目标实体非银行, 采用单一 GPT 模型, 仅报告标注一致性, 既不做 bank-year 面板聚合, 也不叠加分类条件。Abraham、Arnal 与 Marie (2025) 实证 prompt 选择对社科文本标注质量有显著且非平凡的影响并给出 prompt 选择/评估流程, 提示本族赖以成立的两批篇级 LLM 标签均对 prompt 具敏感性; 本项目 prompt v8 已字节级冻结并作为缓存键, 刻意不遍历 prompt 网格择优, 故这一敏感性对本族属未量化的已知局限, 而非已被排除的风险。
【方法学与计算】
计算发生在 pipeline\panel\encode.py 的面板聚合阶段 (与情感三轨、substantiveness _sc、locus _lc 同一模式), 入口函数是 `_aggregate_ctx_diagonal`, 对 innovation_collab_mode_{ctx,ss} 这一篇级分类列做"对角线追加": 以 (bank, year) 为聚合键, 分别统计"自主研发"子集与"外部协同"子集内 llm_vote_tone 的均值与篇数, 落盘为 llm_vote_tone_indep_cm_{ctx,ss} / llm_vote_tone_collab_cm_{ctx,ss} 及配套的 n_articles_indep_cm_{ctx,ss} / n_articles_collab_cm_{ctx,ss}。n_articles 计数列在聚合后统一 `fillna(0).astype(int)`, 保证空 cell (某银行某年无自主研发类报道) 记为整数 0 而非 NaN, 与 llm_vote_tone_indep_cm 本身允许为 NaN (无篇则语调均值无定义) 形成刻意的不对称: 计数列永不缺失, 语调均值列在样本为空时缺失。

分母口径上有一处历史修正值得写清: 早期版本曾出现"ctx 轨分子配 full 轨分母"的轨道不对称错误 (导致 frac 类指标 > 1), 现已修正为分子分母严格同轨——indep_frac_cm 用 n_articles_indep_cm_ctx / n_articles_llm_valid_ctx, indep_frac_cm_ss 用 n_articles_indep_cm_ss / n_articles_llm_valid_ss, 分母若缺失则整列置 NaN 并记 WARNING 而非静默借用其他轨分母。这一"分母存在性守卫"同时保护了本家族 llm_vote_tone_indep_cm_{ctx,ss} 的下游一致性: llm_vote_tone_indep_cm 与 indep_frac_cm 共享同一批 n_articles_indep_cm 计数, 二者的样本基础永远同源同轨, 不存在语调用 ctx 篇但份额用 ss 篇的口径漂移。tone_gap_indep_collab_cm_{ctx,ss} (本族列的差值稳健性伴生列, 非本家族成员但共享计算路径) 在两侧篇数均 >= 5 时才计算, 否则置 NaN, 这是为防止单篇甚至零篇 cell 产生的伪差距被带入下游机制回归——这条 min-n 守门在 2026-06 一次补丁中被追加到 ctx 轨 (此前 5 个同模式差距列已有该守门, 第 6 个曾遗漏), 本族列虽不直接受此守门约束 (守门作用于差值列而非本族均值列本身), 但理解这一点有助于判断样本量小的 bank-year 单元其 tone_gap 为何可能缺失而 llm_vote_tone_indep_cm 本身仍有值。

llm_vote_tone 输入本身继承 stage 21 的三家 LLM 多数投票机制 (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`), 三家意见分歧时按多数裁决取代单一模型判断, 缓解单模型系统性偏误; 但这一投票只发生在情感维度, 分类维度 (自主研发/外部协同) 的裁决遵循独立的共识规则, 两个维度虽同源于同一批篇级 LLM 调用但各自投票互不干扰, 这也是本家族列命名以 _cm (collab mode) 后缀区别于纯语调族 llm_vote_tone_{ctx,ss} 的原因——后者是全部留篇样本上的语调均值, 不做分类条件切分; 本族则是语调均值在分类维度上的条件展开, 二者构念不同不可互换。

【文献定位】
以 LLM 多数投票缓解单模型偏误的方法学根据近年 LLM 集成研究, Kamen & Kamen (2025) 系统评估了多数投票在内容分类任务中相对单模型的稳健性增益, 支持本项目 stage 21 三家投票裁决 (含分类维度 innovation_collab_mode) 的设计选择——多数投票不仅用于语调三分类, 也用于自主研发/外部协同这一分类维度的裁决, 二者共享同一"集成降低方差"的方法学根据。金融领域中文文本上的 LLM 分类/情感底层技术近年迅速迭代, Xu et al. (2025, KDD '25) 提出的 FinBERT2 属同一技术脉络下的金融专用编码器基座 (本项目 stage 23 BERT 三模型族之一即取材于此脉络), 佐证了 LLM/BERT 系文本测度在金融文本上已成为与传统词典法并行的主流路径, 本家族属于该路径下情感×分类交叉测度的具体实现。

构念本身的理论根据来自 Gomber, Kauffman, Parker & Weber (2018) 对金融科技创新形态的分类框架——自建能力型创新与引入外部主体型创新在组织能力构建与风险敞口上有本质差异, innovation_collab_mode 的二分类正是对这一理论区分的经验测度化; 而将银行创新报道语调按此维度切片, 承接的是媒体报道构念随主体注意力焦点变化的一般思路, 类似 Hassan, Hollander, van Lent & Tahoun (2019, QJE) 在企业层面政治风险测度中"实体邻近窗口内语调条件展开"的方法论——本族的 ctx/ss 两轨本身即取材于该文entity-proximity 窗口的构造思路, 只是在此基础上再叠加一层分类条件。

## VAR: llm_vote_tone_indep_cm_ctx

【变体差分】
本列是 llm_vote_tone_indep_cm 族在 ctx 轨上的实现: 篇级样本限定为 llm_vote_tone_ctx 与 innovation_collab_mode_ctx 均有效的报道, 文本窗口为标题+实体邻近窗口 (config/filtering.yaml::context_window 定义的银行/金科实体前后若干字符窗口, prepend_title 拼接标题), 而非全文正文。ctx 轨的语调判定与分类判定均来自同一批"实体窗口文本"上的 LLM 调用, 与 llm_vote_tone_ss(同族另一列) 使用"银行∧金科同句共现窗口"文本形成对照。留篇门控本身是 full-only 口径 (2026-06-29 起, 一篇报道是否算作"银行金科报道"只看 llm_verified_full), ctx 轨的分类/语调判定作用于 full 留篇集合的子集之上, 是 conditional-on-full 的测度性稳健性轨, 而非独立的行宇宙扩展或收窄。分母 n_articles_indep_cm_ctx / 对照分母 n_articles_llm_valid_ctx 均取自 ctx 轨自身统计, 不借用 full 或 ss 轨分母 (2026-06 修复后的严格同轨口径), 因此 indep_frac_cm_ctx 与 llm_vote_tone_indep_cm_ctx 共享完全一致的样本基础。本列在计量设计上应与 llm_vote_tone_indep_cm_ss 并排作为互为稳健性的两条实体上下文窗口测度, 不应与之混入同一过度识别方程。ctx 轨相对 ss 轨的判据更宽松 (窗口内出现即计入, 不要求同句), 因此在样本量偏小的 bank-year 单元上通常比 ss 轨保留更多留篇观测, 语调均值的方差也相对更稳定; 但这种宽松也意味着窗口内可能夹带与"自主研发"事件本身弱相关的邻近语句, 语调信号的噪声成分理论上略高于同句严格窗口。使用者在解读 llm_vote_tone_indep_cm_ctx 与其 ss 轨对照列的差异时, 应优先归因于判据宽严之别, 而非误判为分类裁决本身不稳定; 二者若方向一致, 说明"自主研发型报道语调"这一构念对实体窗口宽严不敏感, 结论稳健性增强。本列与 indep_frac_cm_ctx、tone_gap_indep_collab_cm_ctx 共享同一批 ctx 轨篇级证据与同轨分母, 三者构成同一"分类×语调"交叉切片在 ctx 轨上的完整测度簇, 解读时应联动查看而非孤立看待单一列的数值。

## VAR: llm_vote_tone_indep_cm_ss

【变体差分】
本列是 llm_vote_tone_indep_cm 族在 ss 轨上的实现, 文本窗口收窄为"目标银行与金科词严格同句共现"(±N 句半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认半径 1, 与 stage 13 共现硬过滤的 sentence_radius 是不同的配置键, 不可混用), 判定原语上银行侧含否定与短名过滤、金科侧为裸 AC 自动机 607 词匹配, 与 ctx 轨的实体邻近窗口判据在算法上不同源。ss 轨遵循"镜像 ctx"的回退语义: 若一篇报道内不存在银行∧金科同句共现, content_ss 退化为全文 body 且 ss_is_fallback 置 True, 该篇在退化状态下参与 innovation_collab_mode_ss / llm_vote_tone_ss 的裁决时使用的实际是全文文本而非严格同句片段, 二者共享同一分母口径 (n_articles, 不因回退而剔除该篇)。本列同样是 conditional-on-full 的稳健性轨 (行宇宙限定于 full 留篇集合子集), 分子分母严格取 ss 轨自身 (n_articles_indep_cm_ss / n_articles_llm_valid_ss), 修复了历史上曾出现的跨轨分母错配问题。ss 轨相对 ctx 轨的判据更严格 (要求真实同句邻近而非窗口宽松包含), 在小样本 bank-year 单元 (如本项目 T=2 开发集) 上更容易出现零篇或极少篇导致的空值或方差退化, 这是判据严格度差异的预期后果而非缺陷; 本列应与 llm_vote_tone_indep_cm_ctx 并排解读为互为稳健性、不分主次的两条同族测度, 二者一致则增强结论可信度, 不一致则提示语调-分类交叉效应对判据边界敏感, 均不构成混入同一过度识别 Hansen J 的依据。

<!-- rendered-citations:begin -->
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), 5117-5128. https://doi.org/10.1145/3711896.3737219
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the Fintech Revolution: Interpreting the Forces of Innovation, Disruption, and Transformation in Financial Services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Ornstein, J. T., Blasingame, E. N., & Truscott, J. S. (2025). How to train your stochastic parrot: large language models for political texts. Political Science Research and Methods, 13(2), 264-281. https://doi.org/10.1017/psrm.2024.64
Rønningstad, E., Velldal, E., & Øvrelid, L. (2024). A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation. Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII), 133-139. https://doi.org/10.18653/v1/2024.law-1.13
Abraham, L., Arnal, C., & Marie, A. (2025). Prompt selection matters: enhancing text annotations for social sciences with large language models. Journal of Computational Social Science, 8(3), 73. https://doi.org/10.1007/s42001-025-00388-6
<!-- rendered-citations:end -->
