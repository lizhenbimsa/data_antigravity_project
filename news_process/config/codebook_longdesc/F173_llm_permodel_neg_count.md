---
family_id: F173
columns:
- deepseekv4_neg_count_ctx
- deepseekv4_neg_count_full
- deepseekv4_neg_count_ss
- gemini31_neg_count_ctx
- gemini31_neg_count_full
- gemini31_neg_count_ss
- gpt54nano_neg_count_ctx
- gpt54nano_neg_count_full
- gpt54nano_neg_count_ss
unit: 篇数/计数 (count, 非负整数计数落 double 存储)
formula: "{model}_neg_count_{track} = Σ_{i∈bank-year} 1[ model 对文章 i 在 track 轨的语义判定 = 负面 ∧ 该文经 verified 门控 ]; model ∈ {deepseekv4, gemini31, gpt54nano}, track ∈ {full, ctx, ss}"
producer: news_process/pipeline/sentiment/tone_llms.py (阶段21 单模型文章级情感判定) ; news_process/pipeline/panel/encode.py (bank-year 聚合, groupby.agg sum)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (per-model per-track 文章级情感标签与 verified 标记)
citations:
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.2308/tar-2023-0716
  type: journal
  authors: Bernard, D., Blankespoor, E., de Kok, T., & Toynbee, S.
  year: 2026
  title: "Using GPT to measure business complexity"
  venue: The Accounting Review
  vol: 101
  issue: 3
  pages_or_artno: 67-102
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: "Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy"
  venue: Science Advances
  vol: 10
  issue: 45
  pages_or_artno: eadp1528
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是单一大语言模型 (LLM) 在给定「银行—年度」单元内, 判定为负面语义的银行金科报道篇数, 是阶段21 情感精筛的 per-model 存档计数。构念上它回答一个朴素而关键的问题: 对某家银行在某一年的全部相关报道, 某一家 LLM「数出了多少条负面」。这一裸计数是下游一切负面强度、语调净值、负面占比测度的分子来源, 也是三家模型互为稳健性比对的最细颗粒证据。项目在阶段21 用同一条思维链 (Chain-of-Thought) prompt, 让 gpt-5.4-nano (gpt54nano)、gemini-3.1-flash-lite (gemini31)、deepseek-v4-flash (deepseekv4) 三家模型逐条独立判定每篇报道的真伪与情感, 三家再多数投票合成共识; 而本家族刻意不取共识, 而是把每一家自己的负面判定单独留档, 使研究者能审查厂商间分歧、验证结论不被单一模型的系统性偏好驱动。数据来源为阶段14 物化的三轨文本 content_full / content_ctx / content_ss, 经阶段21 逐模型逐轨判定后, 由 panel encode 层 (encode.py 内 groupby.agg 求和) 在 bank-year 层聚合。命名遵循「模型短名_neg_count_轨道后缀」范式: deepseekv4 直连 api.deepseek.com, gemini31 与 gpt54nano 经 yunwu 路由; 三家均与嵌入模型无关, 换嵌入时本家族零误改。此处「负面计数」区别于词典法 (bian_2021 / du_2022 等) 的规则化正负词加权, 也区别于 BERT 三模型的概率软标签, 是纯 LLM 生成式判定, 三法互为稳健性、不分主次。

【方法学与计算】
计算分两步。第一步在阶段21: 对每篇报道的每一轨文本, 各模型输出结构化的真伪标记与三分类情感 (正面/中性/负面), 温度锁 0.0 以求确定性推理, prompt 版本字节级冻结 (v8-2026-05-17), 命中 LLM 缓存即可离线零成本复现。第二步在 panel encode (encode.py 内 groupby.agg 求和): 对每个 bank-year 单元, 累加该模型该轨判为负面且通过 verified 门控的报道条数。verified 门控与全项目 full-only 留篇口径一致 (2026-06-29): 一篇报道是否算作「一篇银行金科报道」由 full 轨的 llm_verified_full 决定, ctx 与 ss 轨降为 conditional-on-full 的稳健性测度, 其行宇宙是 full 留篇集的子集, 但 per-track 的负面计数各自照算。因此三轨的 neg_count 分母口径并非独立三套留篇集, 而是同一 full 留篇宇宙下的三种文本视角。ss 轨遵循镜像 ctx 的回退语义: 当某篇无银行与金科词同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True, 该篇仍参与计数, 不被静默丢弃。计数落 double 存储但语义为非负整数。极重要的口径约束: 三家模型、三条轨道均为「各自 just-identified 并排、互为稳健性、不分主次」, 严禁把不同模型或不同轨道的 neg_count 混进同一 over-identified 的 Hansen J 过度识别检验 — 这是全项目对多测度并排的铁律, 违反即制造伪过度识别。per-model 独立降级: 若某家模型在某轮缺席 (如 API 不可达), 只掉该模型自身的三列, 不连坐其余两家, 与 co-primary 嵌入的 both-or-neither 强绑定不同。

【文献定位】
把 LLM 当作文本标注器读出情感标签, 近年在会计金融方法学中已从探索走向规范。Gilardi 等 (2023) 在 PNAS 上证明 ChatGPT 在多项文本标注任务上零样本准确率超过众包工人, 为 LLM 替代人工标注提供了首批系统证据; de Kok (2025) 在 Management Science 上给出把生成式 LLM 用于会计文本分析的完整操作规范, 强调温度设零、prompt 冻结与缓存复现三要件, 恰是本项目阶段21 的落地范式。Carlson 与 Burbano (2026) 在 Strategic Management Journal 上进一步系统梳理 LLM 标注在管理学研究中的基础守则与风险警示, 特别指出单一模型可能携带厂商特有的系统性偏好, 因此需要跨模型交叉验证 — 这正是本家族保留 per-model 裸计数而非只留共识的方法学理由。Schoenegger 等 (2024) 在 Science Advances 上显示多个 LLM 的集成预测能力可媲美人类众包, 佐证了多家投票共识的价值, 同时也说明单模型分歧本身是有信息量的稳健性证据。Ludwig 等 (2025) 为 LLM 生成变量进入回归提供了应用计量框架, 提醒生成式测度存在的测量误差需要以并排稳健性而非过度识别来消化。就负面信息本身, Piotroski 等 (2015) 在 Journal of Accounting Research 上记录了中国上市公司政治激励下压制负面信息的现象, 提示中文语境下负面报道的生成与传播受制度约束, 本家族的负面计数应放在这一制度背景中解读。中文金融情感的细粒度 LLM 分析可见 Lan 等 (2025); Bernard 等 (2026) 则示范了以 GPT 抽取企业复杂度这类结构化文本测度进入顶刊的可行路径。

## VAR: deepseekv4_neg_count_ctx

【变体差分】
本列为 DeepSeek-V4 Flash 模型在 ctx (上下文片段) 轨上判定的银行—年度负面报道篇数。模型维度: deepseekv4 是三家投票模型之一, 直连 api.deepseek.com (与经 yunwu 路由的 gemini31、gpt54nano 不同源), 在此列中其负面判定被单独留档而非并入共识。轨道维度: ctx 轨的文本 content_ctx = 标题 prepend + 含目标银行句的 ±窗口片段, 以实体邻近的 proximity 思路截取, 相较 full 轨仅保留银行实体邻近语境, 剔除与目标银行无关的段落, 因而同一篇报道在 ctx 轨的负面判定可能与 full 轨不同 — 语境收窄既可能滤掉噪声也可能丢失全局线索。口径上 ctx 轨为 conditional-on-full 的稳健性测度: 其计数的行宇宙是 full 留篇集的子集 (留篇门控只看 llm_verified_full), 但落在该子集内的每篇报道其 ctx 文本仍独立送 deepseekv4 判定并计数。本列与同家族其余八列 (另两家模型 × 三轨、以及 deepseekv4 的 full/ss 轨) 各自 just-identified 并排、互为稳健性、不分主次, 严禁与它们混入同一 over-identified 的 Hansen J。deepseekv4 缺席时仅本列所在的三列 (ctx/full/ss) 同族降级, 不连坐 gemini31 与 gpt54nano。研究者可用本列与 deepseekv4_neg_count_full 的差异, 度量语境收窄对该模型负面识别的边际影响。需强调本列是裸计数而非占比或净值: 它只回答该模型在该银行—年度数出了多少条负面, 不做任何分母归一; 若要构造负面强度须自行除以对应轨的留篇数。本列的负面判定为生成式思维链结果, 温度锁 0、prompt 版本冻结、命中缓存即可离线零成本复现, 与词典法 (规则化正负词加权) 及 BERT 法 (概率软标签) 的负面计数三法互为稳健性、不分主次。开发期 T=2 小样本上 ctx 轨可能出现零方差, 属预期退化, 生产期 T=18 恢复判别力。

## VAR: deepseekv4_neg_count_full

【变体差分】
本列为 DeepSeek-V4 Flash 模型在 full (全文) 轨上判定的银行—年度负面报道篇数, 是本家族中 deepseekv4 一列的门控基准轨。轨道维度: full 轨文本 content_full = 标题 prepend + 全文正文, 是信息最完整的输入, 也是全项目 full-only 留篇门控 (2026-06-29) 的判定轨 — 一篇报道是否算作银行金科报道, 由 full 轨 verified 结果决定。因此本列的计数分母 (即该 bank-year 参与判定的留篇总数) 是三轨中最本源的一套, ctx 与 ss 轨的计数均寄生于此 full 留篇宇宙。模型维度: deepseekv4 单独留档, 便于与 gemini31_neg_count_full、gpt54nano_neg_count_full 逐一比对同一 full 文本下三家的负面识别分歧, 这种厂商间分歧本身是结论稳健性的直接证据 (Carlson 与 Burbano 2026 强调的跨模型交叉验证)。本列与家族其余八列各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified 的 Hansen J。deepseekv4 独立降级: API 不可达时仅掉 deepseekv4 自身三列。相较词典法与 BERT 法的负面计数, 本列是生成式思维链判定的产物, 温度锁 0、prompt 冻结、缓存命中即可离线复现, 三法互为稳健性。研究者若只用一列做主分析, full 轨因其信息完整与门控基准地位通常是首选, ctx/ss 留作稳健性。本列亦是构造 deepseekv4 负面强度、负面占比等派生测度的分子来源, 其自身为裸计数, 不做分母归一。相较三家共识计数, 本列的价值在于暴露 DeepSeek 单模型的负面识别倾向, 供跨模型一致性检验 (Krippendorff α / Cohen κ) 与跨模型 FWER 稳健性检验消费。开发期 T=2 上因语料稀疏计数可能高度集中于零, 属预期退化, 生产期 T=18 语料充足时恢复正常分布。

## VAR: deepseekv4_neg_count_ss

【变体差分】
本列为 DeepSeek-V4 Flash 模型在 ss (银行与金科同句共现片段) 轨上判定的银行—年度负面报道篇数。轨道维度: ss 轨文本 content_ss = 标题 prepend + 同句内同时含目标银行与金科词的句子 ±窗口, 是三轨中语境最窄、最聚焦「银行做金科」这一交集事件的输入。相较 ctx 轨仅要求出现目标银行句, ss 轨额外要求银行与金科词同句共现, 因而更贴近本研究的核心构念但样本更稀疏。回退语义遵循镜像 ctx 铁律: 当某篇无银行与金科词同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True, 该篇仍以回退文本参与 deepseekv4 判定与计数, 绝不静默丢弃; 当金科 AC 词典为空时 ss_is_fallback 全 True 优雅降级。口径上 ss 亦为 conditional-on-full 稳健性测度, 行宇宙是 full 留篇集子集。模型维度: deepseekv4 单独留档, 可与另两家的 ss 轨负面计数比对厂商分歧。本列与家族其余八列各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J; 尤其 ss 与 full/ctx 三轨禁混同一 Hansen J 是三轨铁律的直接要求。deepseekv4 缺席时仅本列所在三列降级。在开发期 T=2 小样本上, ss 轨因样本稀疏可能出现较多回退与零方差, 属预期退化, 生产期 T=18 恢复正常。本列为裸计数, 不做分母归一, 是 DeepSeek 在最严语境下负面识别的最保守存档。相较 full 与 ctx 轨, ss 轨要求银行与金科词同句共现, 更贴近本研究「银行做金科」的核心构念, 但也因约束最强而最易触发回退; 研究者解读时须结合 ss_is_fallback 比例判断该列计数中真实同句证据与回退证据的构成。本列的负面判定同为温度 0、prompt 冻结、缓存离线可复现的生成式结果, 与词典法、BERT 法三法互为稳健性。

## VAR: gemini31_neg_count_ctx

【变体差分】
本列为 Gemini-3.1-Flash-Lite 模型在 ctx (上下文片段) 轨上判定的银行—年度负面报道篇数。模型维度: gemini31 是三家投票模型之一, 经 yunwu 路由 (与同经 yunwu 的 gpt54nano 同源但不同模型, 与直连的 deepseekv4 异源), 面板列含 gemini31 前缀; 本列把 Gemini 自己的负面判定单独留档, 供审查该厂商相对另两家的系统性倾向。轨道维度: ctx 轨文本 content_ctx = 标题 prepend + 含目标银行句 ±窗口, 语境收窄至银行实体邻近, 相较 gemini31_neg_count_full 剔除无关段落, 同一篇的负面判定可能改变。口径上 ctx 为 conditional-on-full 稳健性测度, 行宇宙是 full 留篇集子集, 留篇门控只看 llm_verified_full。本列与家族其余八列 (另两家 × 三轨, 及 gemini31 的 full/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J。per-model 独立降级: gemini31 缺席仅掉其自身三列, 不连坐 deepseekv4 与 gpt54nano。研究者可用本列与 deepseekv4_neg_count_ctx、gpt54nano_neg_count_ctx 在同一 ctx 文本下三家的差异, 度量厂商间在窄语境下负面识别的一致性 (可配合 Krippendorff α / Cohen κ 一致性检验); 亦可用本列与 gemini31_neg_count_full 的差, 度量语境收窄对 Gemini 负面识别的边际影响。本列是裸计数, 不做分母归一, 是构造 Gemini 负面强度、负面占比等派生测度的分子来源。其负面判定为生成式思维链结果, 温度锁 0、prompt 版本冻结、命中缓存即可离线零成本复现, 与词典法、BERT 法的负面计数三法互为稳健性、不分主次。开发期 T=2 小样本上 ctx 轨计数可能高度集中或零方差, 属预期退化, 生产期 T=18 语料充足时恢复判别力。

## VAR: gemini31_neg_count_full

【变体差分】
本列为 Gemini-3.1-Flash-Lite 模型在 full (全文) 轨上判定的银行—年度负面报道篇数, 是 gemini31 一列的门控基准轨。轨道维度: full 轨文本 content_full = 标题 prepend + 全文正文, 信息最完整, 且是全项目 full-only 留篇门控 (2026-06-29) 的判定轨, 因此本列计数寄生于最本源的 full 留篇宇宙, gemini31 的 ctx/ss 轨计数均以此为行宇宙基准。模型维度: gemini31 经 yunwu 路由, 本列单独留档使研究者能在同一 full 文本下比对三家 (deepseekv4/gemini31/gpt54nano) 的负面识别分歧 — 这种跨厂商分歧是结论稳健性的一线证据, 契合 Carlson 与 Burbano (2026) 与 Schoenegger 等 (2024) 强调的多模型交叉验证与集成价值。本列与家族其余八列各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified 的 Hansen J。per-model 独立降级: gemini31 缺席仅掉自身三列。本列的负面计数是生成式思维链判定 (温度 0、prompt 冻结、缓存可离线复现), 与词典法、BERT 法的负面计数三法互为稳健性、不分主次。在三家共识 (llm_vote_tone) 之外保留本列, 目的正是证明主结论不被 Gemini 单一模型的判定偏好所驱动。本列为裸计数, 不做分母归一, 是 Gemini 在信息最完整 full 文本下负面识别的门控基准存档, 也为跨模型一致性检验 (α / κ) 与跨模型 FWER 稳健性检验提供最细颗粒输入。开发期 T=2 上因语料稀疏计数可能集中于零, 属预期退化, 生产期 T=18 恢复正常分布。研究者若以单模型 full 计数做主轨, 须同时报告另两家的 full 计数以佐证厂商无关性。

## VAR: gemini31_neg_count_ss

【变体差分】
本列为 Gemini-3.1-Flash-Lite 模型在 ss (银行与金科同句共现片段) 轨上判定的银行—年度负面报道篇数。轨道维度: ss 轨文本 content_ss = 标题 prepend + 同句内同时含目标银行与金科词的句 ±窗口, 是三轨中最聚焦「银行做金科」交集事件的输入, 语境最窄、样本最稀疏。回退语义镜像 ctx: 无银行与金科词同句共现时 content_ss 回退全文正文并置 ss_is_fallback=True, 该篇仍以回退文本参与 gemini31 判定与计数; 金科 AC 为空时全 True 优雅降级。口径上 ss 为 conditional-on-full 稳健性测度, 行宇宙是 full 留篇集子集。模型维度: gemini31 经 yunwu 路由, 本列单独留档, 可与 deepseekv4_neg_count_ss、gpt54nano_neg_count_ss 比对三家在最窄语境下的负面识别一致性。本列与家族其余八列各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J, 三轨禁混同一 Hansen J 尤须遵守。per-model 独立降级: gemini31 缺席仅掉自身三列, 不连坐另两家。开发期 T=2 上 ss 轨因样本稀疏、回退比例高, 可能出现零方差或近似退化, 属预期现象, 生产期 T=18 语料充足时恢复正常判别力。研究者可将本列作为对 gemini31_neg_count_full 的最严语境稳健性臂。本列为裸计数, 不做分母归一; 因 ss 轨约束最强、回退最频, 解读时须结合 ss_is_fallback 比例区分真实同句证据与回退证据。其负面判定同为温度 0、prompt 冻结、缓存离线可复现的生成式结果, 与词典法、BERT 法三法互为稳健性、不分主次; 与另两家的 ss 轨计数并排则可检验最窄语境下负面识别的厂商一致性。

## VAR: gpt54nano_neg_count_ctx

【变体差分】
本列为 GPT-5.4-nano 模型在 ctx (上下文片段) 轨上判定的银行—年度负面报道篇数。模型维度: gpt54nano 是三家投票模型之一, 经 yunwu 路由 (与 gemini31 同源不同模型, 与 deepseekv4 异源); 本列把 GPT 自己的负面判定单独留档。轨道维度: ctx 轨文本 content_ctx = 标题 prepend + 含目标银行句 ±窗口, 语境收窄至银行实体邻近, 相较 gpt54nano_neg_count_full 剔除无关段落, 同一篇的负面判定可能改变。口径上 ctx 为 conditional-on-full 稳健性测度, 行宇宙是 full 留篇集子集, 留篇门控只看 llm_verified_full。本列与家族其余八列 (另两家 × 三轨, 及 gpt54nano 的 full/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J。per-model 独立降级: gpt54nano 缺席仅掉自身三列, 不连坐 deepseekv4 与 gemini31。研究者可用本列与另两家 ctx 轨的差异, 度量在窄语境下 GPT 与其余厂商负面识别的一致程度, 并配合跨模型一致性统计 (α / κ) 评估共识可靠性; 亦可用本列与 gpt54nano_neg_count_full 之差度量语境收窄对 GPT 负面识别的边际影响, 与另两家的同类差异对照即揭示语境敏感度是否为厂商共性。本列是裸计数, 不做分母归一, 是构造 GPT 负面强度、负面占比等派生测度的分子来源。其负面判定为生成式思维链结果, 温度锁 0、prompt 版本冻结、命中缓存即可离线零成本复现, 与词典法、BERT 法的负面计数三法互为稳健性、不分主次。开发期 T=2 小样本上 ctx 轨计数可能集中或零方差, 属预期退化, 生产期 T=18 恢复判别力。

## VAR: gpt54nano_neg_count_full

【变体差分】
本列为 GPT-5.4-nano 模型在 full (全文) 轨上判定的银行—年度负面报道篇数, 是 gpt54nano 一列的门控基准轨。轨道维度: full 轨文本 content_full = 标题 prepend + 全文正文, 信息最完整, 且是全项目 full-only 留篇门控 (2026-06-29) 的判定轨, 本列计数寄生于最本源的 full 留篇宇宙, gpt54nano 的 ctx/ss 轨计数均以此为行宇宙基准。模型维度: gpt54nano 经 yunwu 路由, 本列单独留档, 使研究者能在同一 full 文本下比对三家 (deepseekv4/gemini31/gpt54nano) 的负面识别分歧, 该跨厂商分歧是结论稳健性的一线证据 (Gilardi 等 2023 证 LLM 标注可媲美人工, de Kok 2025 给出会计文本 LLM 分析规范)。本列与家族其余八列各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified 的 Hansen J。per-model 独立降级: gpt54nano 缺席仅掉自身三列。本列负面计数为生成式思维链判定 (温度 0、prompt 冻结、缓存离线可复现), 与词典法、BERT 法负面计数三法互为稳健性、不分主次。在三家共识之外保留本列, 意在证明主结论不被 GPT 单一模型的判定偏好驱动, 也为跨模型 FWER 稳健性检验提供最细颗粒输入。本列为裸计数, 不做分母归一, 是 GPT 在信息最完整 full 文本下负面识别的门控基准存档。开发期 T=2 上因语料稀疏计数可能集中于零, 属预期退化, 生产期 T=18 恢复正常分布。研究者若以单模型 full 计数做主轨, 须同时报告 deepseekv4 与 gemini31 的 full 计数以佐证结论的厂商无关性, 这是本项目保留 per-model 存档而非只留共识的根本用意。

## VAR: gpt54nano_neg_count_ss

【变体差分】
本列为 GPT-5.4-nano 模型在 ss (银行与金科同句共现片段) 轨上判定的银行—年度负面报道篇数。轨道维度: ss 轨文本 content_ss = 标题 prepend + 同句内同时含目标银行与金科词的句 ±窗口, 是三轨中最聚焦「银行做金科」交集事件、语境最窄、样本最稀疏的输入。回退语义镜像 ctx: 无银行与金科词同句共现时 content_ss 回退全文正文并置 ss_is_fallback=True, 该篇仍以回退文本参与 gpt54nano 判定与计数, 绝不静默丢弃; 金科 AC 为空时全 True 优雅降级。口径上 ss 为 conditional-on-full 稳健性测度, 行宇宙是 full 留篇集子集, 留篇门控只看 llm_verified_full。模型维度: gpt54nano 经 yunwu 路由, 本列单独留档, 可与 deepseekv4_neg_count_ss、gemini31_neg_count_ss 比对三家在最窄语境下的负面识别一致性。本列与家族其余八列各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J, 三轨禁混同一 Hansen J 尤须遵守。per-model 独立降级: gpt54nano 缺席仅掉自身三列, 不连坐另两家。开发期 T=2 上 ss 轨因样本稀疏、回退比例高可能退化, 属预期, 生产期 T=18 恢复正常; 本列适合作为对 gpt54nano_neg_count_full 的最严语境稳健性臂。本列为裸计数, 不做分母归一; 因 ss 轨约束最强、回退最频, 解读时须结合 ss_is_fallback 比例区分真实同句证据与回退证据。其负面判定同为温度 0、prompt 冻结、缓存离线可复现的生成式结果, 与词典法、BERT 法三法互为稳健性、不分主次; 与另两家的 ss 轨计数并排即可检验最窄语境下 GPT 负面识别与其余厂商的一致程度。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Bernard, D., Blankespoor, E., de Kok, T., & Toynbee, S. (2026). Using GPT to measure business complexity. The Accounting Review, 101(3), 67-102. https://doi.org/10.2308/tar-2023-0716
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
<!-- rendered-citations:end -->
