---
family_id: F442
columns:
- modal_weak_frac_ctx
- modal_weak_frac_full
- modal_weak_frac_ss
unit: 比率/占比 (proportion, [0,1]; 弱势模态词命中数 / 该轨分词后总词数)
formula: 'modal_weak_frac_{trk} = count(tokens_{trk} ∩ weak_modal_dict) / n_tokens_{trk} ; weak_modal_dict 取自 config/tone_dicts.json::loughran_mcdonald_zh_2026 的 weak_modal 类别 (55 词, jieba==0.42.1 分词)'
producer: pipeline\sentiment\lm_non_sentiment.py ; pipeline\sentiment\tone_words.py (三轨调用集成点) ; pipeline\audit\lm_discriminant_validity.py (stage 39e 判别效度审计)
upstream: []
citations:
- {doi: "10.1111/j.1540-6261.2010.01625.x", type: journal, authors: "Loughran, T., & McDonald, B.", year: 2011, title: "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks", venue: "The Journal of Finance", vol: "66", issue: "1", pages_or_artno: "35-65"}
- {doi: "10.1111/1475-679X.12123", type: journal, authors: "Loughran, T., & McDonald, B.", year: 2016, title: "Textual Analysis in Accounting and Finance: A Survey", venue: "Journal of Accounting Research", vol: "54", issue: "4", pages_or_artno: "1187-1230"}
- {doi: "10.1111/1911-3846.12825", type: journal, authors: "Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.", year: 2023, title: "Textual Analysis in Accounting: What's Next?", venue: "Contemporary Accounting Research", vol: "40", issue: "2", pages_or_artno: "765-805"}
- {doi: "10.1007/s11747-014-0403-8", type: journal, authors: "Henseler, J., Ringle, C. M., & Sarstedt, M.", year: 2015, title: "A New Criterion for Assessing Discriminant Validity in Variance-Based Structural Equation Modeling", venue: "Journal of the Academy of Marketing Science", vol: "43", issue: "1", pages_or_artno: "115-135"}
- {doi: "10.1007/BF02310555", type: journal, authors: "Cronbach, L. J.", year: 1951, title: "Coefficient Alpha and the Internal Structure of Tests", venue: "Psychometrika", vol: "16", issue: "3", pages_or_artno: "297-334"}
- {doi: "10.1177/001316446002000104", type: journal, authors: "Cohen, J.", year: 1960, title: "A Coefficient of Agreement for Nominal Scales", venue: "Educational and Psychological Measurement", vol: "20", issue: "1", pages_or_artno: "37-46"}
- doi: "10.1111/fire.70002"
  title: "Tone Distance: Managerial Tone Divergence and Market Reaction to Earnings Announcements"
  authors: "Angelo, B., Johnston, M., Singh, A., & Wan, Y. Q."
  year: 2025
  venue: "Financial Review"
  type: "journal"
new_dois:
  - "10.1111/fire.70002"
---

## CORE

【构念与来源】
modal_weak_frac 家族衡量一篇报道 (逐轨: 标题+正文全文 full / 标题+实体窗口 ctx / 标题+银行∧金科同句共现窗 ss) 中"弱势情态动词"类词汇的出现密度, 是 Loughran & McDonald (2011, Journal of Finance) 面向 10-K 文本分析所构建的六类非情感词典体系中的一支。原始 L&M 词典区分 strong modal (如"必然""一定会") 与 weak modal (如"可能""或许""大概")——前者传递高确定性主张, 后者传递含蓄、留有余地的措辞。管理层或信息中介在陈述前景不明或存在下行风险的事项时, 倾向于系统性地增用弱势情态词以规避断言性责任; 这一"语言对冲" (hedging) 现象在会计与金融文本分析文献中被反复证实与股价/盈余不确定性存在系统关联。本家族把该构念迁移到中文财经新闻语料: 词典来源不是研究者自建的中文 stub, 而是 `config/tone_dicts.json::loughran_mcdonald_zh_2026` 项目下 weak_modal 类别的 55 个词条——该类别与 uncertainty(392)/litigious(913)/constraining(174)/strong_modal(54)/complexity(129) 共同构成 1,717 词的 L&M 情感主译全本非极性子集, 经项目内部 325-agent 审计的全本翻译产出, 于 v3.10.0 (2026-06-18) 替代此前 314 词、标记 AWAITING_EXPERT_AUDIT 的手工 stub `lm_non_sentiment`——该 stub 已按用户指令彻底废弃并从 tone_dicts.json 移除。这是一次有意的测度变更而非行为保持型重构: 词表体量与来源均改变, 数值不与旧 stub 版本可比。

【方法学与计算】
计算路径复用项目 v3.5.1 起建立的 A1 词典型文本分析基础设施: `_compute_clarity_for_text` / `_dual_analyze` 提供三轨分词与词频统计骨架。只读模块 `lm_non_sentiment.py::_compute_lm_non_sentiment_for_text` 是一个 track-agnostic 的纯函数——它只接收一段已就绪的文本、返回该文本上 6 个 L&M 子集各自的命中计数与占比, 本身不感知 full/ctx/ss 的轨道划分; 但真正被生产路径三轨调用的不是该只读模块的函数本身, 而是 `pipeline/sentiment/tone_words.py` 文件内部自带的同语义包装 `_compute_lm_non_sentiment_for_text_tone_tok` (该函数 docstring 明确声明"与只读模块 `lm_non_sentiment._compute_lm_non_sentiment_for_text` 逐项同语义", 即物理上是两个分处不同文件的独立实现、语义等价但非同一函数对象)。真正的三轨语义由调用方 `pipeline/sentiment/tone_words.py::_dual_analyze` 决定: 该函数对 `content_full`/`content_ctx`/`content_ss` 三段文本分别各调用一次 `_compute_lm_non_sentiment_for_text_tone_tok`, 把返回的 6 项结果 (含 modal_weak) 分别落入对应轨的 dict, 因而"第三轨 (ss) 由调用方用 content_ss 文本驱动, 本模块无需改动"——ss 与 ctx 共享同一套下游消费与回退语义, 镜像 ctx 的处理路径。分母 n_tokens 是该轨该篇文章 jieba (==0.42.1, 冻结版本以保证 golden 逐位可复现) 分词后的总词数 (非字符数、非句数), 命中判据是精确词表匹配 (非子串/模糊匹配), weak_modal 词表本身不做否定翻转/程度副词/转折规则的语言学消融——这一规则消融梯度 (`_RULE_ABLATION_VARIANTS`) 只施加于情感极性词典 (tone_words 的 6 词典 × 3 轨 × 7 变体), 不适用于本家族这类非极性描述性词频测度。

三轨口径必须与项目铁律对齐: full=标题+正文全文, ctx=标题+实体识别窗口, ss=标题+银行∧金科同句共现窗口 (`config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1)。ss 轨的回退语义严格镜像 ctx: 当一篇文章不存在银行∧金科同句共现时, `content_ss` 退化为全文 body、`ss_is_fallback` 标记为 True, 与 ctx 共享同一 `n_articles` 分母口径, 因而 modal_weak_frac_ss 在回退样本上实质上退化为对全文本的度量, 不是零值或缺失。三轨彼此是互为稳健性、不分主次的并排测度——full 是留篇门控口径 (2026-06-29 起 stage 21 是否判定"一篇银行金科报道"只看 `llm_verified_full`), ctx/ss 是 conditional-on-full 的稳健性轨, 三者各自 just-identified, 禁止在同一 over-identified Hansen J 设定中混用三轨列作为过度识别工具变量或联合矩条件——这是与嵌入双轨、政治词权重梯度、词典消融梯度共享的一条项目级识别铁律, 目的是避免研究者无意间把"同一构念的三种测量方式"错误地当成三个独立识别来源。

【文献定位】
L&M (2011, Journal of Finance) 首次系统证明基于词典的文本情感/确定性测度能捕捉 10-K 文件中传统金融词典 (如 Harvard-IV) 无法捕捉到的会计语境特异信号, 弱势情态词是其六类非情感词典之一, 用以刻画措辞的确定性程度而非情感极性。Loughran & McDonald (2016, Journal of Accounting Research) 的综述进一步系统梳理了文本分析方法在会计与金融研究中的扩散路径与方法学陷阱, 为跨语料 (含本项目的中文财经新闻迁移) 词典复用提供了方法论正当性依据。Bochkay, Brown, Leone & Tucker (2023, Contemporary Accounting Research) 综述了会计文本分析的前沿方向, 呼应本项目在 L&M 词典基础上叠加 LLM 三家投票、BERT 三模型等多方法互证架构的设计取向——词典法 (含本家族) 与机器学习法在本项目中定位为互为稳健性、不设主次的并排测度体系, 而非相互替代。本家族的下游判别效度审计 (`lm_discriminant_validity.py`, stage 39e) 采用 Henseler, Ringle & Sarstedt (2015, Journal of the Academy of Marketing Science) 提出的 HTMT (Heterotrait-Monotrait ratio) 准则, 对 8 维构念 (L&M 6 子集 + clarity_score + num_intensity) 两两计算异质-同质比, 双门槛 0.85 (strict) / 0.90 (lenient), 目的是验证 modal_weak_frac 等 6 个 L&M 子集彼此之间、以及与项目内已建立的清晰度/数字密集度测度之间不存在系统性构念重叠 (即测的不是同一件事)。审计另辅以 Cronbach (1951, Psychometrika) 的 α 系数评估各子词典内部一致性, 以及 Cohen (1960, Educational and Psychological Measurement) 的 κ 系数用于跨维度类别一致性诊断的方法学参照。审计输出按 full/ctx/ss 三轨各写一份 8×8 HTMT 矩阵与 1,000 次重复 (seed=42) 置换零分布 CSV, 落于 `eval_reports/74_lm_htmt_matrix_{full,ctx,ss}.csv` 与 `eval_reports/74_lm_permutation_{full,ctx,ss}.csv`, ss 轨在相关列缺失时优雅跳过而不中断整体审计流程。Angelo, Johnston, Singh & Wan (2025, Financial Review) 提出管理层语气分歧度测度并检验其与盈余公告市场反应的关联, 呼应本家族用弱势模态词密度刻画报道措辞确定性/含蓄程度这一构念取向。

白话: 这组指标数的是一篇报道里"可能""或许""大概"这类"说话留余地"的词占了多大比例。记者或消息源在拿不准的事情上往往会不自觉地多用这类词, 所以这个比例某种程度上反映了报道语气的确定性高低, 跟正面/负面的情感判断是两回事。同一篇文章按标题+全文、标题+实体附近、标题+银行和金科词同句出现这三种不同的"取文范围"各算一遍, 三个数字谁也不比谁更权威, 都是彼此印证的稳健性检验, 不能把它们混在一起当作三个独立的证据来源使用。

## VAR: modal_weak_frac_ctx

【变体差分】
ctx 轨: 取文范围为"标题 + 实体识别窗口" (`content_ctx`, stage 14 `ctx_materializer` 物化, prepend_title), 而非全文正文。相对 full 轨, ctx 轨把弱势模态词的搜索空间收窄到目标银行/金科实体周边的语境窗口, 剔除了文章中与银行-金科关系无关段落 (如背景铺垫、无关业务介绍) 的弱势模态词干扰, 因而更贴近"报道在直接谈及银行-金科关系时措辞确定性如何"这一更精细的构念; 代价是分母 (该轨词数) 更小, 单个词命中对比例的边际影响更大, 方差通常高于 full 轨。当一篇文章的实体窗口抽取失败或退化 (`*_is_fallback` 标记) 时, ctx 轨与其余 ctx 族列共享同一套回退处理, 计算函数本身 track-agnostic、不因轨道而改变判据逻辑, 差异完全来自上游喂入的文本内容。留篇门控 (2026-06-29 起) 以 full 轨的 LLM 验证结果为准, modal_weak_frac_ctx 的行样本因而是 full 留篇集的子集测度, 不单独扩展样本范围。作为 full 的互为稳健性并排轨, 不应与 full/ss 轨列一并塞入同一 over-identified 设定。在判别效度审计 (`lm_discriminant_validity.py`, stage 39e) 中, ctx 轨的 8×8 HTMT 矩阵单独落盘为 `eval_reports/74_lm_htmt_matrix_ctx.csv`, 与 full/ss 轨互不混算, 目的是分别验证"实体窗口语境下"的 6 个 L&M 子集彼此及与 clarity/num_intensity 是否构念独立, 不因取文范围收窄而人为抬高构念间相关性。实践上, 当一篇报道谈及某银行与某金科平台的合作/风险事项集中在文章局部段落时, ctx 轨相比 full 轨更能捕捉"该局部段落"本身的措辞确定性, 例如报道主体多为客观陈述但涉及双方合作前景的一两句话使用了"可能""预计"等弱势模态词——这类局部信号在 full 轨会被全文其余段落的词量稀释, 在 ctx 轨则不会。

## VAR: modal_weak_frac_full

【变体差分】
full 轨: 取文范围为"标题 + 正文全文" (`content_full`, 项目三轨架构中的默认/留篇门控口径), 是本家族的 canonical 测度——2026-06-29 起 stage 21 是否判定"一篇银行金科报道"仅看 `llm_verified_full == True`, 因而 modal_weak_frac_full 对应的行样本即为该留篇门控下的全集, ctx/ss 均是以此为行样本子集的稳健性轨。相对 ctx/ss, full 轨的分母 (全文词数) 最大, 弱势模态词命中数的绝对规模也通常最大, 因此单篇文章层面的比例估计方差最小、最不受个别词命中的边际扰动影响, 是本家族在后续判别效度审计 (`lm_discriminant_validity.py`) 与面板汇总统计中作为默认参照轨呈现的版本; 但这一"默认呈现"地位不改变项目铁律——三轨彼此仍是互为稳健性、不分主次的并排测度, full 轨不构成对 ctx/ss 轨的统计意义上的优先级。判别效度审计 (`lm_discriminant_validity.py`, stage 39e) 对 full 轨单独产出 `eval_reports/74_lm_htmt_matrix_full.csv` 与对应 1,000 次置换零分布 CSV, 验证 modal_weak_frac_full 与同轨 uncert_frac_full/litig_frac_full/constr_frac_full/modal_strong_frac_full/complexity_frac_full 六者两两 HTMT < 0.85, 且与 full 轨 clarity_score/num_intensity 亦保持判别效度。由于 full 轨样本量最大 (对应留篇门控全集, 不受实体窗口或同句共现判据收窄), 该轨的 HTMT 估计与置换检验统计功效通常最高, 是判断"弱势模态词密度"是否真的独立于强势模态词密度、不确定性密度等相邻构念的首要参照, 但仍需与 ctx/ss 轨联合解读方能得出稳健结论, 单一轨的显著性不足以单独支撑构念有效性判定。

## VAR: modal_weak_frac_ss

【变体差分】
ss 轨: 取文范围为"标题 + 银行∧金科同句共现窗口" (`content_ss`, `config/filtering.yaml::context_window.ss_sentence_radius` 默认半径 1 句), 判据比 ctx 轨更严格——要求银行实体与金科词在同一句 (或窗口内相邻句) 中出现, 而非仅在实体识别窗口内邻近。ss 轨的回退语义严格镜像 ctx: 当一篇文章不存在满足条件的银行∧金科同句共现时, `content_ss` 退化为全文 body、`ss_is_fallback` 置 True, 与 ctx 共享同一 `n_articles` 分母口径; 这意味着在回退发生的样本上, modal_weak_frac_ss 的数值来源实质上等同于 full 轨对同一文章的测度, 而非缺失值或零值——解读该列时须结合 `ss_is_fallback` 标记, 否则会把"退化为全文"误读为"该文章弱势模态词密度天然更高/更低"。当 `FINTECH_AC` (金科关键词自动机) 为 None 时, `*_is_fallback` 全部置 True, 全体样本优雅降级为对全文的测度。ss 轨是三轨中判据最严、样本内部方差潜在最大的一支, 用于在"直接同句提及"这一最窄语境下检验弱势模态词密度结论的稳健性, 与 full/ctx 轨并排、不构成同一识别设定内可混用的独立工具。判别效度审计 (`lm_discriminant_validity.py`, stage 39e) 对 ss 轨单独产出 `eval_reports/74_lm_htmt_matrix_ss.csv` 及对应置换零分布, 但明确注明"ss = 银行+金科同句共现轨, 列缺失时该轨优雅跳过", 即当上游 `content_ss` 相关列因该批次样本中银行-金科同句共现极少而未能产出稳定统计量时, 审计不会强行插补或报错中断, 而是跳过该轨的 HTMT 计算, 仅对 full/ctx 两轨出具判别效度结论。这一设计反映了 ss 轨判据严格带来的固有权衡: 判据越窄, 语境信号越纯粹 (直接锁定银行与金科词共现的那一句话的措辞确定性), 但样本覆盖与统计稳定性的代价也越大, 尤其在 T=2 的开发期小样本上表现为大量回退 (`ss_is_fallback=True`), 生产期全量语料 (T=18) 上覆盖度预期显著改善。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2016). Textual Analysis in Accounting and Finance: A Survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual Analysis in Accounting: What's Next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). A New Criterion for Assessing Discriminant Validity in Variance-Based Structural Equation Modeling. Journal of the Academy of Marketing Science, 43(1), 115-135. https://doi.org/10.1007/s11747-014-0403-8
Cronbach, L. J. (1951). Coefficient Alpha and the Internal Structure of Tests. Psychometrika, 16(3), 297-334. https://doi.org/10.1007/BF02310555
Cohen, J. (1960). A Coefficient of Agreement for Nominal Scales. Educational and Psychological Measurement, 20(1), 37-46. https://doi.org/10.1177/001316446002000104
Angelo, B., Johnston, M., Singh, A., & Wan, Y. Q. (2025). Tone Distance: Managerial Tone Divergence and Market Reaction to Earnings Announcements. Financial Review. https://doi.org/10.1111/fire.70002
<!-- rendered-citations:end -->
