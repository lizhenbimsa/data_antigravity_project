---
family_id: F610
columns:
- washing_ratio_finbert_cn
- washing_ratio_finbert_cn_ctx
- washing_ratio_finbert_cn_ss
unit: 比率 (proportion, [0,1]; 分子分母均为文章计数, 无量纲)
formula: washing_ratio_finbert_cn{track} = count(finbert_cn 判正面{track} ∧ innovation_substantiveness_full=='象征性') / count(finbert_cn 判正面{track} ∧ 实质性测量已完成), 其中 track ∈ {full, ctx, ss}; 分母口径为方法 E2 专属列 `_svd_finbert_cn_pos{track}`(面板列 `finbert_cn_pos_substvalid_count{track}`), 与方法 A 的 `_svd_pos{track}` 是同一设计模式下各自独立的并列列(非同一列复用), 只数实质性/象征性已被 LLM 判出的文章, 未测量文章既不入分子也不入分母
producer: pipeline\panel\runner.py (方法 E2 单 BERT 洗稿率标记构造, 步骤 7h 聚合); pipeline\panel\export.py (Stata 标签/列注册)
upstream: [23_tone_berts, 16_article_policy_alignment, 21_tone_llms]
citations:
- doi: "10.1111/1911-3846.12832"
  type: journal
  authors: "Huang, A. H., Wang, H., & Yang, Y."
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.2307/2393593"
  type: journal
  authors: "Westphal, J. D., & Zajac, E. J."
  year: 1998
  title: "The symbolic management of stockholders: Corporate governance reforms and shareholder reactions"
  venue: "Administrative Science Quarterly"
  vol: "43"
  issue: "1"
  pages_or_artno: "127-153"
- doi: "10.2307/2393295"
  type: journal
  authors: "Westphal, J. D., & Zajac, E. J."
  year: 1994
  title: "Substance and symbolism in CEOs' long-term incentive plans"
  venue: "Administrative Science Quarterly"
  vol: "39"
  issue: "3"
  pages_or_artno: "367-390"
- doi: "10.1016/j.pacfin.2024.102600"
  type: journal
  authors: "Fan, X., Tang, Z., Huang, W., & Yang, K."
  year: 2025
  title: "Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective"
  venue: "Pacific-Basin Finance Journal"
  vol: "89"
  pages_or_artno: "102600"
- doi: "10.1038/s41598-025-29621-y"
  type: "journal"
  authors: "Li, Y., Li, J., Zheng, Y., Zheng, G., & Wu, C."
  year: 2025
  title: "Machine learning detection of manipulative environmental disclosures in corporate reports"
  venue: "Scientific Reports"
  vol: "15"
  issue: "1"
  pages_or_artno: "45011"
new_dois: []
---

## CORE

【构念与来源】
洗稿率 (washing ratio) 测度的是"新闻语气表面正面, 但内容缺乏实质性创新支撑"这一现象在样本文章中的占比, 学术根子来自 Westphal & Zajac (1994, 1998) 关于公司治理改革中"象征性采纳"(symbolic adoption) 与"实质性采纳"(substantive adoption) 的区分——正面语气对应"看起来在做", 象征性分类对应"实际未必真做", 二者叠加即"言辞与实质脱节"的量化捕捉思路。本仓库把这一构念搬到银行-金科新闻语境: 一篇报道若被情感模型判为"正面", 但同一篇文章又被 stage 16 (`article_policy_alignment`) 的 LLM 判为"象征性"(即仅描述战略意图/口号式合作, 无具体产品/技术/投入等可验证实质内容), 就构成一次"洗稿"式正面表述——媒体在渲染积极形象, 但缺乏可核实的实质支撑。`l2_washing_ratio_finbert_cn` 家族是洗稿率测度矩阵里的方法 E2 分支: 用单个 BERT 情感模型 `finbert_cn` (而非 LLM 多数投票或词典) 的 argmax 分类结果作为"正面"判据的来源, 与家族内其余 per-model BERT 洗稿率家族 (`finbert2`/`fin_sent_zh`) 并列, 也与 LLM 投票版 `washing_ratio`(方法 A)、词典均值版 `washing_ratio_dict`(方法 D)、BERT 三模型均值版 `washing_ratio_bert`(方法 E) 平行存在, 互为稳健性、不分主次。白话讲: 就是"finbert_cn 这个模型看着挺正面, 但仔细一看内容全是空话套话"的文章, 占"finbert_cn 判为正面且实质性已被判定清楚"的文章的比例——比例越高, 说明按这个模型的判断标准, 该银行-年度的正面报道里"注水"越多。

【方法学与计算】
计算分两层。第一层在篇章级 (producer `pipeline\panel\runner.py`): 对每篇文章、每条轨道 track ∈ {full, ctx, ss}, 取 finbert_cn 在该轨道上的三分类判定 (来自 stage 23 `tone_berts`, 该模型对 `content_{track}` 文本 argmax 出的正/负/中性标签), 记为该轨的 `is_positive{track}` 指示; 同时取 stage 16 输出的 `innovation_substantiveness_full` 分类结果 (取值"实质性"/"象征性"/其他), 记 `_is_symb`、`_subst_measured`(是否被成功判出实质性/象征性、非缺失非拒答)。构造两个篇章级 0/1 标记: 分子标记 = (finbert_cn 判正面{track}) ∧ (象征性); 分母标记 = (finbert_cn 判正面{track}) ∧ (实质性已测量)。第二层在面板级 (步骤 7h 聚合): 按 银行-年度 对上述两个标记求和, 相除得到本列。分母同域约束是本测度区别于朴素实现的关键设计: 早期版本分母用"全部正面文章数", 但若 finbert_cn 判正面而 stage 16 LLM 未能判出实质性/象征性 (分类失败、拒答或平局), 该文章进不了分子却仍计入朴素分母, 导致分类失败率越高、洗稿率被系统性低估的假象 (与 encode-01 类修正同族, 详见 producer 注释 fix(omni-g-runner-10/g-runner-14)); 修正后分母只数"实质性判定成功"的同域样本, 让洗稿率反映的是真实的"正面-但-空洞"占比而非测量噪音。当分母 (同域正面且已测样本数) 为 0 时该银行-年度取值缺失 (NaN), 不做 0/0 强填。

【文献定位】
本测度的构念来源锚定治理研究中的"象征性 vs 实质性行动"区分, 直接源自 Westphal & Zajac (1994, *Administrative Science Quarterly*) 关于长期激励计划采纳的实证发现——公司常常在制度压力下采纳看似合规的治理安排, 但执行层面并无实质约束力, 后续 Westphal & Zajac (1998, *Administrative Science Quarterly*) 进一步把这一逻辑延伸到股东沟通的象征管理: 上市公司管理层可以通过话术选择性地向股东传达"变革已发生"的印象, 而不必真正改变治理结构。本测度把这一"言辞-行动"脱节的识别逻辑迁移到银行-金科合作报道语境: 用情感模型的"正面"判定对应媒体话术层面的印象管理, 用 stage 16 的"象征性"分类对应内容层面缺乏可验证实质, 二者交集即为一次"洗稿"记录。本 F610 家族作为 per-model 稳健性分支, 其模型来源锚定于顶刊 Huang, Wang & Yang (2023, *Contemporary Accounting Research*) 提出的 FinBERT 架构族及其金融文本适配范式——finbert_cn 是该范式在中文金融语料上的落地实现, 与家族内另两个 BERT 模型 (finbert2、fin_sent_zh) 构成三模型互证矩阵而非层级关系。三轨设计 (full/ctx/ss) 遵照本仓库既定口径: full=标题+正文全文, ctx=标题+银行/金科实体窗口, ss=标题+银行∧金科同句±N窗 (回退语义镜像 ctx: 若某篇文章不存在银行∧金科同句共现, 则 `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 共享 `n_articles` 分母, 缺列优雅降级)。三轨、per-model (finbert_cn/finbert2/fin_sent_zh)、以及洗稿率的多方法族 (A/A2/B/D/D2/E/E2/F) 均各自 just-identified 并排, 互为稳健性、不分主次, 严禁在同一 over-identified Hansen J 设定中混用同族多个变体作为并列工具/协变量——每条轨道、每个模型各进独立回归设定。 在"披露操纵可由分类器在大规模文本上自动测量"这一存在性前提上, Li、Li、Zheng、Zheng 与 Wu (2025) 以监督式机器学习分类器检测企业报告中的操纵性环境披露, 表明"文本宣称与实质不符"这一构念具备端到端的自动识别可行性, 与本家族在文本判定器之上构造洗稿率的总体思路相邻。此处须严格自限: 该文分类器直接以"是否操纵"为标签端到端训练, 观测单位为企业报告, 语料为英文企业自述文本与环境议题; 而本家族的 finbert_cn 并不判定操纵, 仅承担情感极性判定 (正面/中性/负面), 象征-实质标签另由 stage 16 的 LLM 提供, 二者交叉后方在银行-年层聚合为比率。两者并非同一方法族, 该文不构成本家族判定器口径的方法学依据, 亦无证据表明其分类器属预训练语言模型范式, 因此引用仅止于构念可测性层面的相邻佐证, 不得据以为 finbert_cn 的架构或训练范式背书。
## VAR: washing_ratio_finbert_cn

【变体差分】
这是 F610 家族的 full 轨 canonical 列, 即分子分母的"正面"判据全部来自 `content_full`(标题+正文全文) 上 finbert_cn 的 argmax 分类结果, 象征性判据仍固定用 `innovation_substantiveness_full`(stage 16 实质性分类本身在上游同时产出 full/ctx/ss 三轨独立列 `innovation_substantiveness_{full,ctx,ss}`, 供其它消费方——如 4-way 洗稿变体、`_sc` 类列——按轨选用; 但本 F610 洗稿率家族在设计上刻意只锚定 full 轨实质性判据, 三条洗稿率轨共享同一份 full 轨象征性标签, 不随"正面"判据的轨道切换而切换)。该列与家族内 `_ctx`/`_ss` 两个变体的唯一差异在于"正面"判据所依赖的文本窗口不同, 分母的实质性测量口径三轨完全一致。作为三轨中样本覆盖最完整的一支 (full 轨不存在共现回退问题, 不涉及 ctx/ss 那种"无共现窗口则回退全文"的降级路径), 该列通常被视为洗稿率测度矩阵里样本量最大、噪音最小的基准分支, 但按本仓库口径它与 ctx/ss 轨互为稳健性并列, 不构成"主"测度层级, 三者在任何回归设定里都应各自单独进入、不得叠加为同一工具集。列值域 [0,1] 或缺失 (分母同域样本为 0 时, 即当年该行银行既无 finbert_cn 判正面且实质性已测的文章)。使用该列做实证解释时须留意其与家族内 finbert2/fin_sent_zh 两个 per-model 洗稿率家族的关系: 三者共享完全相同的分子构造逻辑 (正面 ∧ 象征性) 与分母同域约束逻辑, 唯一差异是"正面"标签的来源模型不同, 因此三个 per-model 家族之间的差异反映的是不同 BERT 情感分类器在同一批文章上的判定分歧, 而非测度定义本身的分歧; 研究者若关心洗稿率结论对具体情感分类模型的敏感度, 应把 finbert_cn/finbert2/fin_sent_zh 三支 full 轨版本并列汇报, 而非取其一作为唯一依据。

## VAR: washing_ratio_finbert_cn_ctx

【变体差分】
ctx 轨版本: "正面"判据改由 finbert_cn 在 `content_ctx`(标题+银行/金科实体窗口截取文本) 上的分类结果给出, 分母的实质性测量口径 (`innovation_substantiveness_full`) 与 full 轨相同、不随轨道切换。ctx 轨聚焦实体邻近上下文而非全文, 用于检验"洗稿"判定是否对文本截取范围敏感——若一篇文章全文语气正面但实体邻近段落语气中性/负面 (反之亦然), full 与 ctx 两轨的分子标记可能不一致, 二者差异本身即是一种文本粒度稳健性信号。ctx 轨依赖 stage 14 `ctx_materializer` 物化的 `content_ctx` 列, 若上游实体窗口截取失败或该文章无可用窗口, 依 stage 14 既定回退语义处理 (非本列独有逻辑)。本列与 `washing_ratio_finbert_cn` 及 `washing_ratio_finbert_cn_ss` 各自 just-identified 并排, 互为稳健性, 禁止混入同一 over-identified 设定联合估计。从构念角度看, ctx 轨的价值在于剥离与银行-金科合作议题无关的正文段落干扰: 一篇长报道全文语气可能被无关段落 (如宏观经济评论、行业综述) 拉高或拉低, 而实体窗口截取只保留银行/金科关键词邻近的语句, 因此 ctx 轨的"正面"判定理论上更贴近文章真正谈及银行-金科合作时的语气, 而 full 轨则更接近整篇报道的总体基调。两轨分子标记不一致的文章 (即 full 与 ctx 对同一篇文章给出不同的"正面"判定) 恰恰是检验测度稳健性的关键样本, 若洗稿率结论在 full/ctx 两轨间大幅摇摆, 说明该结论对文本截取窗口高度敏感, 须在论文稳健性附录中并列汇报两轨结果并讨论差异来源, 而不能只选取对结论更有利的一轨作为正式陈述。分母 (`_subst_measured`) 不随 ctx 切换, 这一设计保证了跨轨比较时唯一变动的自变量是"正面"判据的文本来源, 不会因分母口径不同而引入额外混淆。

## VAR: washing_ratio_finbert_cn_ss

【变体差分】
ss 轨版本: "正面"判据改由 finbert_cn 在 `content_ss`(标题+银行∧金科同句±N窗, 窗口半径见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认1) 上的分类结果给出, 分母的实质性测量口径仍固定为 `innovation_substantiveness_full`。ss 轨回退语义镜像 ctx: 若一篇文章不存在银行与金科关键词同句 (或同句±N窗内) 共现, `content_ss` 退化为全文 body, 对应 `ss_is_fallback=True`, 此时该篇文章在 ss 轨的"正面"判定实质上等同于 full 轨判定, 但仍计入 ss 轨样本、共享 `n_articles` 分母, 不做单独剔除。ss 轨是三轨中文本窗口最窄、判据最严格的一支——只在银行与金科议题被同一句话直接绑定报道时才采用局部窗口文本, 因此对"洗稿"判定的敏感度理论上更贴近"标题党式" 强关联描述与实质内容脱节的场景: 当一篇文章标题或某一句同时点名银行与金科关键词、语气积极, 但全文对该合作的具体实质缺乏展开时, ss 轨最容易捕捉到这种"强绑定-弱实质"的洗稿模式。由于同句共现在样本中相对稀疏, ss 轨的 `ss_is_fallback=True` 比例通常高于 ctx 轨依赖回退的比例, 意味着相当一部分文章在 ss 轨上实际是用 full 轨文本参与判定, 这是设计既定的优雅降级而非缺陷, 但也意味着 ss 轨与 full 轨的分子标记重合度天然较高, 二者差异主要集中在确实存在同句共现的那部分文章上。研究者比较三轨结果时应留意这一结构性重合, 不宜把 ss 轨与 full 轨的高度一致简单解读为"洗稿率对文本窗口不敏感", 而应聚焦真正触发窗口截取 (`ss_is_fallback=False`) 的子样本做差异检验。本列与 full/ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J, 亦不应与 finbert2/fin_sent_zh 两个平行 per-model 家族的 ss 轨列混合作为同一联立方程组的多重工具变量。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Li, Y., Li, J., Zheng, Y., Zheng, G., & Wu, C. (2025). Machine learning detection of manipulative environmental disclosures in corporate reports. Scientific Reports, 15(1), 45011. https://doi.org/10.1038/s41598-025-29621-y
<!-- rendered-citations:end -->
