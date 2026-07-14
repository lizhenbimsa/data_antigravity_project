---
family_id: F608
columns:
- washing_ratio_fin_sent_zh
- washing_ratio_fin_sent_zh_ctx
- washing_ratio_fin_sent_zh_ss
unit: 比率/占比 (proportion, [0,1]; 分子分母皆为文章计数, 空分母时输出 NaN)
formula: washing_ratio_fin_sent_zh{track} = count(fin_sent_zh{track} 判正面 且 innovation_substantiveness_full=象征性) / count(fin_sent_zh{track} 判正面 且 innovation_substantiveness 已测量[象征性∨实质性])
producer: pipeline\panel\runner.py (方法 E2 篇章级标记 washing_cols 构造, 步骤 7h 聚合); pipeline\panel\export.py (Stata 标签装配)
upstream: [is_positive_fin_sent_zh_full, is_positive_fin_sent_zh_ctx, is_positive_fin_sent_zh_ss, innovation_substantiveness_full]
citations:
- {doi: "10.1016/j.frl.2022.102776", type: journal, authors: "Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.", year: 2022, title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures", venue: "Finance Research Letters", vol: "47", issue: "Part B", pages_or_artno: "102776"}
- {doi: "10.1111/jofi.13412", type: journal, authors: "Duchin, R., Gao, J., & Xu, Q.", year: 2025, title: "Sustainability or greenwashing: Evidence from the asset market for industrial pollution", venue: "The Journal of Finance", vol: "80", issue: "2", pages_or_artno: "699-754"}
- {doi: "10.1016/j.pacfin.2024.102600", type: journal, authors: "Fan, X., Tang, Z., Huang, W., & Yang, K.", year: 2025, title: "Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective", venue: "Pacific-Basin Finance Journal", vol: "89", pages_or_artno: "102600"}
- {doi: "10.1111/eufm.12509", type: journal, authors: "Gorovaia, N., & Makrominas, M.", year: 2024, title: "Identifying greenwashing in corporate-social responsibility reports using natural-language processing", venue: "European Financial Management", vol: "31", issue: "1", pages_or_artno: "427-462"}
- {doi: "10.1007/978-3-030-32381-3_16", type: book, authors: "Sun, C., Qiu, X., Xu, Y., & Huang, X.", year: 2019, title: "How to fine-tune BERT for text classification?", venue: "Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science", vol: "11856", pages_or_artno: "194-206"}
- {doi: "10.1007/s00521-024-10603-6", type: journal, authors: "Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.", year: 2025, title: "Chinese fine-grained financial sentiment analysis with large language models", venue: "Neural Computing and Applications", vol: "37", issue: "30", pages_or_artno: "24883-24892"}
new_dois: []
---

## CORE

【构念与来源】
washing_ratio_fin_sent_zh 一族衡量的是"洗稿"(washing / cherry-picking) 现象在单一 BERT 情感模型 fin_sent_zh 判正面的报道子样本中的占比: 一篇报道被 fin_sent_zh 模型判为情感正面, 但同时被 LLM 三家投票的 innovation_substantiveness_full 判为"象征性"(symbolic, 即空洞姿态性表述, 无可验证的具体举措/数据/时间表支撑) 而非"实质性"(substantive)。这是 pipeline 洗稿率大家族里方法 E2 (单 BERT argmax 标签) 的产物, 与方法 E (BERT 三模型均值投票, 见 washing_ratio_bert)、方法 A/A2 (LLM 多数投票 / 逐 LLM)、方法 D/D2 (词典均值 / 单词典) 并列, 但分子分母判正面所用的引擎换成了单一 BERT 模型 fin_sent_zh 的 argmax 输出, 而非 LLM 或词典。构念直接对应 Bingler, Kraus, Leippold & Webersinke (2022, Finance Research Letters) 提出的"cheap talk"检验思路: 若一家银行/金科相关报道频繁呈现"正面语气 + 无实质内容"的组合, 该报道更可能是公关式姿态宣示而非可验证的业务进展披露, 这与企业传播文献中"漂绿"(greenwashing) 概念——即用积极修辞掩盖缺乏实质支撑的行为——同构, 只是这里的"绿"换成了"金融科技创新"话题。分子计数条件是"fin_sent_zh{track} 判正面 且 innovation_substantiveness_full=象征性"两个指示变量的逻辑与, 分母不是简单的"全部正面报道数", 而是"正面 且 实质性测量已完成(即 innovation_substantiveness_full 落在象征性或实质性两类之一, 排除测量失败/拒绝的 NaN)"的同域计数——这是 2026-06-11 的一处已知修正(fix omni-g-runner-10/g-runner-14)。修正之前, 分母数的是"全部正面文章"(不论 LLM 是否成功判出象征性/实质性), 分子却只在 LLM 判出结果时才计数; 当 LLM 分类失败率系统性上升时, 分子端因测量失败而丢失的正面报道不会同步从分母剔除, 造成洗稿率被人为稀释、系统性下偏——分类失败越多, 观测到的"洗稿"占比反而看起来越低, 这是一个纯粹的度量假象而非真实的行为变化。现行实现引入 `_svd_*` (substantiveness-valid denominator) 篇章级同域掩码, 确保分子与分母共享"实质性判定已完成"这同一测量前提, 从根子上排除了分类失败率漂移对分母的污染。
【方法学与计算】
计算流程分两步: 第一步在 pipeline\panel\runner.py 步骤 7h 之前, 逐轨(full/ctx/ss) 构造两个篇章级 0/1 标记列 `_is_pos_symb{track}`(该文正面 且 象征性) 与 `_svd_pos{track}`(该文正面 且 实质性已测量, 无论最终判为象征性或实质性), 二者均对 `is_positive_fin_sent_zh{track}` 先做 `fillna(0)` 再与布尔条件相与, 保证 nullable Int8 的 NaN(代表模型未能判出/平局/拒绝) 不会被误当作"判正面"参与计数。第二步在面板聚合阶段(步骤 7h), 按 bank-year 分组对上述两个篇章级标记求和, 再相除得到本家族三列。分母的实质性掩码 `_subst_measured` 取自 `innovation_substantiveness_full.isin(_SUBST_VALID_LABELS)`——⚠ 注意该判定固定读 `_full` 轨(全文轨), 不随本列的 track 后缀切换, 因为 innovation_substantiveness 分类本身在 v3.2.0 后即以 `_full` 作为唯一主规格(bare 版本已删除), 三轨情感判正面才是本族真正切换轨道的对象。fin_sent_zh 是 BERT_MODELS 常量表中三个中文金融情感 BERT 之一(与 finbert_cn、finbert2 并列), 其"判正面"依据该模型对文章的 argmax 三分类(正/负/中性)标签是否落在正面类, 这与 LLM 三家投票或六部词典均值是完全独立的判正面引擎——三条洗稿率生产线(LLM/词典/BERT)彼此不共享判正面的底层信号来源, 仅共享"象征性 vs 实质性"这同一 LLM 分类结果作为分子侧的鉴别维度。当分母为 0(某 bank-year 内没有任何"fin_sent_zh 判正面 且实质性已测量"的文章)时, 本列按标准比率处理惯例输出 NaN, 不做 0/0 强填零处理, 避免把"无可比较样本"误读为"零洗稿"。
【文献定位】
"洗稿率"这一构念的方法学祖源是 Bingler, Kraus, Leippold & Webersinke (2022, Finance Research Letters) 用 ClimateBert 检验企业气候披露"言辞多于实质"(cheap talk) 的框架, 本族将同一逻辑迁移到银行金融科技报道语境, 并把"言辞是否落空"的鉴别标签由气候披露具体举措换成了本项目 LLM 三家投票产出的 innovation_substantiveness 分类。国际漂绿计量文献亦提供了并行方法学参照: Duchin, Gao & Xu (2025, *The Journal of Finance*) 用资产市场交易数据识别工业污染企业的漂绿/真实可持续行为分野, 验证了"言行不一致"可通过外部可验证信号(资产处置、报道内容)系统性识别, 为本族"正面语气—象征性内容不一致"的构念提供了跨行业的方法学正当性; Fan, Tang, Huang & Yang (2025, *Pacific-Basin Finance Journal*) 基于多主体视角研究中国资本市场股权集中度与企业漂绿的关系, 提供了中国资本市场语境下漂绿测度的最新参照; Gorovaia & Makrominas (2024, *European Financial Management*) 用自然语言处理方法从企业社会责任报告中识别漂绿, 与本族"从文本正面情感与实质性标签的错配中提取洗稿信号"方法论同源。fin_sent_zh 作为中文金融领域预训练 BERT 分类器的微调应用范式, 参照 Sun, Qiu, Xu & Huang (2019, *CCL*) 关于 BERT 文本分类微调的方法学基础; Lan, Wu, Xu, Feng & Zhang (2025, *Neural Computing and Applications*) 进一步展示了中文细粒度金融情感分析在大语言模型时代的最新实践, 与本项目 BERT/LLM 双轨并列的情感测度设计理念相呼应。

## VAR: washing_ratio_fin_sent_zh

【变体差分】
本列是家族 canonical(无轨道后缀) 变体, 判正面引擎固定为 `_full`(标题+正文全文) 轨的 fin_sent_zh BERT 模型输出, 即分子分母的"判正面"条件均取 `is_positive_fin_sent_zh_full`。它与三轨设计中的另外两条(_ctx/_ss) 互为稳健性、不分主次: 各自 just-identified 并排使用, 严禁把三轨洗稿率同时塞进同一个 over-identified 的 Hansen J 过度识别检验里联合估计——这会人为制造工具冗余并破坏三轨"各自独立回归"的稳健性设计初衷。全文轨的特点是判正面依据整篇报道(不裁剪、不限定实体窗口)的语气, 覆盖面最宽但也最容易被与目标银行/金科话题无关的段落情感稀释; 这也是本族三轨里样本量最大、噪声也相对最大的一条。分母侧 `innovation_substantiveness_full` 恒定读全文轨(与本列判正面轨一致, 天然对齐无需跨轨换算), 分子/分母掩码构造严格遵循 CORE 节所述的 `_svd_*` 同域计数修正, 即分母只数"象征性∨实质性已判出"的正面文章, 不数 LLM 分类失败的正面文章, 从而避免分类失败率系统性推高/推低表观洗稿率。作为方法 E2(单 BERT 模型), 本列与家族对应的方法 E 变体(BERT 三模型均值投票, 见 washing_ratio_bert 家族)在数值上通常正相关但绝非恒等: E2 只依赖 fin_sent_zh 单模型的 argmax 三分类判定, 不引入 finbert_cn、finbert2 两个并列 BERT 模型的投票信息, 因此在三模型判断存在分歧的报道上, 本列与均值版本会出现方向性差异。这种差异不是缺陷, 而是"各 BERT 模型互为稳健性、不分主次"设计的直接体现——本项目刻意保留每个 BERT 模型的单模型洗稿率, 而非只发布均值版本, 目的是让下游研究者能够检验结论是否依赖某一个特定预训练模型的判断偏好。使用本列时应把它当作 fin_sent_zh 视角下的洗稿率观测, 与同族 finbert_cn、finbert2 版本(若存在) 及 LLM/词典版本并排比较, 而不是把它当作唯一权威口径。

## VAR: washing_ratio_fin_sent_zh_ctx

【变体差分】
本列判正面引擎切换为 `_ctx`(标题+实体窗口) 轨的 fin_sent_zh BERT 输出, 即分子分母的"判正面"条件取 `is_positive_fin_sent_zh_ctx`, 而分母的实质性掩码仍固定读 `innovation_substantiveness_full`(与上一条同理, 全家族该分类本身不随判正面轨切换)。ctx 轨把判正面的文本输入收窄到银行/金科实体周边窗口, 相比全文轨(canonical 列) 更聚焦于报道中直接涉及目标实体的语句语气, 理论上能降低无关段落对情感判断的稀释噪声, 但样本覆盖面随之收窄(实体窗口抽取失败或过短的文章会退化)。本列与 canonical(_full) 及 _ss 轨三者严格并排、互为稳健性: 若某银行-年度洗稿率在全文轨与 ctx 轨方向一致, 结论的稳健性增强; 若二者出现方向性分歧, 应报告分歧而非强行调和, 三轨绝不可混入同一个过度识别 Hansen J 联合估计。ctx 轨的实体窗口抽取依赖上游 stage 14 `ctx_materializer` 物化的 `content_ctx` 列(标题 prepend + 实体窗口正文), 与 stage 13 共现硬过滤(要求目标银行与 ≥1 金科词在 ±1 句窗口内邻近共现, 并允许标题匹配) 是两道独立但衔接的判据: 前者决定文章能否进入面板样本, 后者决定判正面时具体读哪一段窗口文本。因此 ctx 轨洗稿率的样本 universe 与 canonical(_full) 轨完全一致(留篇门控固定为 full-only, 2026-06-29 起 stage 21 是否判为"一篇银行金科报道"只看 `llm_verified_full`), 二者差异只来自"判正面时模型看到的文本范围不同", 而非样本构成不同, 这是解读三轨差异时须牢记的口径前提。

## VAR: washing_ratio_fin_sent_zh_ss

【变体差分】
本列判正面引擎切换为 `_ss`(标题+银行∧金科同句窗口, ±N 句半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 轨的 fin_sent_zh BERT 输出, 分子分母判正面条件取 `is_positive_fin_sent_zh_ss`, 分母实质性掩码同样固定读全文轨 `innovation_substantiveness_full`。ss 轨的回退语义镜像 ctx 轨: 当一篇报道内不存在银行与金科词的同句共现时, `content_ss` 退化为全文 body(等同 canonical 输入), 并由共享的 `ss_is_fallback` 标记该行属于回退状态, 分母口径(`n_articles`) 与 ctx 轨共享同一套后备计数逻辑, 不因回退而产生额外的孤儿列或分母口径漂移。ss 轨是三轨中判据最严格的一条——只在银行与金科话题真正同句紧邻出现的语境里判断情感正负, 理论上最能剥离"报道提到银行, 也提到金科, 但两者话题彼此无关"的伪共现噪声, 是判定"洗稿"是否发生在银行与金科真正同框叙事中的最精炼观测窗口。与 canonical(_full)、_ctx 两轨同属并排稳健性设计, 三者各自 just-identified, 禁止混入同一 over-identified Hansen J 联合估计; 若 fintech_intensity 判定金科 AC 词典为空(FINTECH_AC=None), 则全部 `*_is_fallback` 优雅降级为 True, 本列随之退化为等同全文轨的观测。ss 轨是三轨中对"银行与金科话题真正相关叙事"最挑剔的一条: 它把判正面所依据的文本严格限定在同句共现窗口内, 意味着即使一篇报道整体语气正面(canonical 轨会捕捉到), 只要银行与金科词从未在同一句话里相邻出现, ss 轨判正面所看的文本片段就仍是全文回退版本而非任何被裁剪的窗口——回退语义本身保证了分母(`n_articles`) 的分母口径不会因窗口抽取失败而产生额外缺失行, 这与 ctx 轨共享同一套"共享分母、镜像回退"的设计约定。使用者在解读 _ss 与 _full/_ctx 三者差异时应留意: 差异既可能来自"同句叙事下情感判断确实不同", 也可能来自"回退触发比例本身在不同银行-年度间的分布差异"——后者是样本构成层面的差异, 前者才是构念层面的差异, 两者混淆会导致对"洗稿"程度的误判, 建议同时参考 `ss_is_fallback` 占比作为解读本列时的辅助诊断信息。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47(Part B), 102776. https://doi.org/10.1016/j.frl.2022.102776
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance, 80(2), 699-754. https://doi.org/10.1111/jofi.13412
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Sun, C., Qiu, X., Xu, Y., & Huang, X. (2019). How to fine-tune BERT for text classification?. Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science. https://doi.org/10.1007/978-3-030-32381-3_16
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
<!-- rendered-citations:end -->
