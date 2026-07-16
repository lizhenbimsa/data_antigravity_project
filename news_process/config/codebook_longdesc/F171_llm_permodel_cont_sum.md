---
family_id: F171
columns:
- deepseekv4_cont_sum_ctx
- deepseekv4_cont_sum_full
- deepseekv4_cont_sum_ss
- gemini31_cont_sum_ctx
- gemini31_cont_sum_full
- gemini31_cont_sum_ss
- gpt54nano_cont_sum_ctx
- gpt54nano_cont_sum_full
- gpt54nano_cont_sum_ss
unit: 无量纲 (置信度加权有符号语调之 bank-year 总和; 外延口径, 随覆盖量放大)
formula: "{short}_cont{track} = {short}_score{track} × {short}_sentiment_confidence{track}; {short}_score ∈ {-1,0,+1} (verified 门控后), confidence ∈ [0,1]; {short}_cont_sum{track} = Σ_{该 bank-year 全部文章} {short}_cont{track} (groupby sum)"
producer: news_process/pipeline/panel/encode.py::encode_sentiment (文章级 {short}_cont) + build_aggregation_dict (bank-year sum)
upstream:
- 21_tone_llms.parquet ({short}_sentiment / {short}_sentiment_confidence / {short}_verified 三轨)
- 40_panel_yearly.parquet (bank-year 聚合)
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
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1287/mnsc.2024.05417
  type: journal
  authors: Siano, F.
  year: 2025
  title: "The news in earnings announcement disclosures: Capturing word context using LLM methods"
  venue: Management Science
  vol: 71
  issue: 11
  pages_or_artno: 9831-9855
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.2139/ssrn.4412788
  type: wp
  authors: Lopez-Lira, A., & Tang, Y.
  year: 2023
  title: "Can ChatGPT forecast stock price movements? Return predictability and large language models"
  venue: SSRN Working Paper
new_dois: []
---

## CORE

【构念与来源】
本家族刻画单一大语言模型 (LLM) 对一家银行在某一年度全部涉金融科技报道所给出的「置信度加权有符号语调」的年度总和 (continuous-sum, 简写 cont_sum)。构念的原子是文章级连续得分 {short}_cont{track}: 在 stage 21 统一语义精筛与情感判定环节, 每家 LLM 对每篇报道独立输出一个三分类情感标签 (正/中/负) 与一个自评置信度; encode 层先把标签经 SENTIMENT_MAP 映射为有符号整数 (正=+1、中=0、负=−1), 再乘以该模型对该篇的置信度 (取值区间 0 到 1), 得到一个落在闭区间负一到正一的连续量。该连续量既保留了语调的方向 (符号), 又以置信度作幅度调制 — 模型越笃定, 绝对值越接近极端; 模型越犹疑, 绝对值越向零收缩。cont_sum 则是把这一连续量在同一 bank-year 内对该行当年全部留篇文章逐篇相加得到的总和。它是外延 (extensive-margin) 口径的度量: 数值随该行当年报道数量与语调强度共同放大, 因此与同族的 cont_mean (内涵均值) 互补而非等价 — 前者答「这家银行今年被媒体以多强的净正/净负笃定度总体覆盖」, 后者答「平均每篇的笃定净语调多高」。三家模型 (gpt54nano、gemini31、deepseekv4) 各产一列, 三种文本轨 (full、ctx、ss) 各产一列, 3×3 共九列。数据来源为 stage 21 逐模型逐轨的原始判定 (情感标签 + 置信度 + verified 精筛旗标), 上游经 stage 14 ctx_materializer 物化的三轨文本喂入, 下游在 stage 40 面板导出时按 bank-year 分组求和。

【方法学与计算】
计算分两步。第一步在文章级: 对每家模型, 先按该模型自身的 verified 精筛旗标门控 — 若该模型对该篇判为未通过精筛, 则其得分置为缺失, 不进入连续量; 通过者则以有符号得分乘自评置信度成连续量。此处「per-model 独立降级」是关键设计: 三家模型各用自己的 verified 与 confidence, 一家缺席只掉自己这一族, 绝不牵连另两家 (区别于 co-primary 嵌入的 both-or-neither 联锁)。第二步在 bank-year 级: 用 groupby 对该行当年全部文章的连续量求和 (聚合算子 sum, 非 mean), 缺失值按 pandas 缺失语义自然跳过。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否算作该行当年的「银行金融科技报道」只由 llm_verified_full 判定, ctx 轨与 ss 轨是 conditional-on-full 的子集测度, 其行宇宙是 full 留篇集的子集, 各轨的 per-track 列在此子集上照算。置信度加权借鉴人工内容分析中以标注者把握度调制信号强度的传统, 使高把握判定获得更大权重、低把握判定被自动衰减, 从而在不额外训练的前提下逼近一种软标签期望。三家模型的推理温度均钉为零以获确定性输出, prompt 版本字节级冻结, 判定结果落缓存, 使该族在离线复现时可零字节复刻。⚠ 铁律: 三家模型互为稳健性、不分主次, 三条文本轨亦互为稳健性、不分主次, 各自 just-identified 并排即可, 严禁把不同模型或不同轨的 cont_sum 混进同一条 over-identified Hansen J 过度识别方程 — 跨模型的真 FWER 校正由根级 rwolf 模板统一承担, 而非在单一工具变量方程内混装。

【文献定位】
把 LLM 直接当作文本标注器并将其输出作为下游计量变量, 这一做法的效度与规范近年在顶刊被系统检视。Gilardi et al. (2023) 在 PNAS 证明 ChatGPT 在多项文本标注任务上零样本一致性与准确率超过众包工人, 为「以 LLM 替代人工标注」奠定经验基础; de Kok (2025) 在 Management Science 给出会计研究使用生成式 LLM 做文本分析的操作范式, 明确温度取零、prompt 冻结与缓存三要件, 正是本族确定性复现锚的直接依据; Siano (2025) 同刊展示 LLM 方法相较词袋能捕捉盈余公告披露中的词语语境, 印证连续语调优于纯计数。管理学侧, Carlson & Burbano (2026) 在 Strategic Management Journal 系统梳理以 LLM 标注研究数据的基础守则与警示 (验证子样本、报告一致性、警惕幻觉与污染), 本族逐模型 verified 门控与多模型并排即回应其规范。计量嵌入层面, Ludwig, Mullainathan & Rambachan (2025) 提出把 LLM 输出接入回归的应用计量框架, 提示测量误差与内生选择须显式处理, 支撑本族以外延总和与内涵均值双口径并置; 多模型集成的价值由 Chen et al. (2025) 的 LLM ensemble 综述与本族逐模型稳健性并排一脉相承。中文金融语境的适配则由 Lan et al. (2025) 的中文细粒度金融情感 LLM 研究背书, Lopez-Lira & Tang (2023) 进一步验证 LLM 情感对金融序列的预测含量并确立温度零的确定性推理惯例。

## VAR: deepseekv4_cont_sum_ctx

【变体差分】
本列锁定 deepseekv4 模型 × ctx 文本轨的置信度加权有符号语调年度总和。模型维: deepseekv4 是 DeepSeek V4 Flash, 直连 api.deepseek.com, 是三家中唯一不经云雾 (yunwu) 聚合端点、直连原厂 API 的模型, 与走云雾聚合端点的另两家 (gemini31、gpt54nano) 在调用链路上分属两个独立源, 因而其潜在的服务端限流、批处理与版本迭代节奏均与另两家解耦, 这一异源性本身即构成对「结论是否被单一供应商链路特质驱动」的一重稳健性检验。其得分、置信度与 verified 精筛均取自该家自身输出, 与 gemini31、gpt54nano 互为稳健性、不分主次。轨道维: ctx = content_ctx = 标题 prepend 后接含目标银行句的正负 N 句窗口 (实体邻近上下文), 相较 full 轨舍弃了与目标银行无关的段落, 使语调判定聚焦于银行相关语境, 从而在保留银行相关叙述的同时压低无关段落带来的语调噪声。聚合维: 本列为 sum 聚合, 是外延口径, 随该行当年 ctx 轨留篇量放大, 与 deepseekv4_cont_mean_ctx (内涵均值) 互补。此外, 本列是未叠加媒体权威权重、羊群衰减权重与投票加权的裸置信度加权总和, 即 deepseekv4_cont_w_sum_ctx、deepseekv4_cont_hw_sum_ctx 等加权变体的参照臂; 数值为正表示该行当年 ctx 语境下被净正面且笃定地覆盖, 为负则净负面, 绝对值随覆盖量与语调极端度共同抬升。与三家共识的 llm_vote_cont_sum_ctx 不同, 本列不经多数投票合成, 直接暴露 DeepSeek 单厂商视角, 供跨模型分歧诊断与稳健性对照。门控上, 文章是否留篇仍由 full-only 口径 (llm_verified_full) 决定, ctx 轨为其 conditional-on-full 子集, deepseekv4 自身 verified 未过的篇其得分置缺失不入总和。⚠ 铁律: 本列与同族另八列各自 just-identified 并排, 禁与其它模型或其它轨混入同一 over-identified Hansen J。

## VAR: deepseekv4_cont_sum_full

【变体差分】
本列锁定 deepseekv4 模型 × full 文本轨。模型维同 deepseekv4 家族: DeepSeek V4 Flash 直连 api.deepseek.com, 逐条并发独立判定, 温度钉零、prompt 冻结、判定落缓存, 是与另两家互为稳健性的三角验证一员, per-model 独立降级 (deepseekv4 缺席只掉本族, 不牵连 gemini31 与 gpt54nano)。轨道维: full = content_full = 标题 prepend 后接完整正文, 是信息量最全、也是留篇门控的权威轨 — 一篇报道是否算该行当年金融科技报道的判据 llm_verified_full 正落在此轨 (full-only 门控, 2026-06-29)。因此本列的行宇宙是母集, ctx 与 ss 轨均为其子集; 在稳健性表中 full 轨常作首要测量, ctx/ss 作稳健臂。聚合维仍为 bank-year sum, 外延口径, 随全文轨留篇量与逐篇置信度加权语调共同放大, 与 deepseekv4_cont_mean_full 内涵均值互补作双口径并置 (呼应 Ludwig et al. 2025 对测量口径显式化的建议)。本列亦是 deepseekv4_cont_w_sum_full、deepseekv4_cont_hw_sum_full、deepseekv4_cont_mw_sum_full 等媒体权威/羊群衰减/投票加权变体的裸参照臂: 若结论在这些加权臂上成立而在裸总和上不成立, 即提示效应由权重构造而非语调本身驱动。数值为正表示该行当年被 DeepSeek 判为净正面且高把握覆盖, 为负则净负面, 绝对值反映当年报道体量与语调笃定度的联合强度; 与三家共识 llm_vote_cont_sum_full 相比, 本列保留单厂商原始信号, 未经多数投票折叠。⚠ 铁律: 本列与同族另八列各自 just-identified 并排, 三家三轨严禁混进同一 over-identified Hansen J。

## VAR: deepseekv4_cont_sum_ss

【变体差分】
本列锁定 deepseekv4 模型 × ss (银行金融科技同句共现) 文本轨。模型维同上, 取 DeepSeek V4 Flash 自身输出。轨道维: ss = content_ss = 标题 prepend 后接同一句内同时含目标银行词与金融科技词的句之正负 N 句窗口 (config filtering.yaml ss_sentence_radius, 默认 1), 是三轨中语境最收敛、信噪最纯的输入, 专门捕捉「银行与金融科技被同句提及」的强共现语调。回退语义须复述准: 若该篇无任何银行与金融科技同句共现, content_ss 镜像 ctx 逻辑回退为全文正文 body, 并置 ss_is_fallback=True, 与母族共享 n_articles 分母; 若金融科技 AC 自动机为空则该篇 ss 全 True 优雅降级。聚合维为 bank-year sum, 外延口径, 与 deepseekv4_cont_mean_ss 内涵均值互补, 并作 deepseekv4_cont_w_sum_ss 等加权变体的裸参照臂。在开发期 T=2 小样本上 ss 轨因同句共现稀疏可能出现零方差退化属预期, 生产期 T=19 恢复正常。ss 轨的价值在于把语调判定限缩到银行与金融科技被真正放在同一句讨论的强共现语境, 是三轨中最贴近本研究「银行金融科技」构念的收敛测度, 相较 ctx 进一步排除了银行出现但与金融科技无关的段落噪声。门控仍守 full-only: 留篇由 llm_verified_full 定, ss 为 conditional-on-full 子集, deepseekv4 自身 verified 未过者置缺失, per-model 独立降级不牵连另两家。⚠ 铁律: 本列与同族另八列各自 just-identified 并排, 三家三轨严禁混进同一 over-identified Hansen J。

## VAR: gemini31_cont_sum_ctx

【变体差分】
本列锁定 gemini31 模型 × ctx 文本轨。模型维: gemini31 是 gemini-3.1-flash-lite, 经云雾 (yunwu) 聚合端点调用, 与直连的 deepseekv4 不同源、与同走云雾的 gpt54nano 不同模型, 其得分、置信度、verified 均取自该家自身输出, 与另两家 co-equal 互为稳健性、不分主次。轨道维: ctx = content_ctx = 标题 prepend 后接含目标银行句的正负 N 句窗口 (实体邻近上下文), 相较 full 聚焦银行相关语境、相较 ss 又更宽 (只要求银行出现, 不要求金融科技同句)。聚合维为 bank-year sum 外延口径, 随该行当年 ctx 轨留篇量放大, 与 gemini31_cont_mean_ctx 内涵均值互补, 并作 gemini31_cont_w_sum_ctx、gemini31_cont_hw_sum_ctx 等加权变体的裸参照臂。数值为正表示该行当年 ctx 语境下被 Gemini 判为净正面且高把握覆盖, 为负则净负面, 绝对值随覆盖量与语调极端度联合抬升。与三家共识 llm_vote_cont_sum_ctx 不同, 本列不经多数投票折叠, 直接暴露 Google 系模型的单厂商视角, 供跨模型分歧诊断。三家单模型 cont_sum 之间的年内符号一致性与离散度可用于评估语调测量的跨厂商稳健程度, 分歧越小则主结论越不依赖某一家模型的特质。门控守 full-only: 留篇由 llm_verified_full 决定, ctx 为 conditional-on-full 子集, gemini31 自身 verified 未过的篇得分置缺失不入总和, per-model 独立降级 (gemini31 若整体缺席只掉本族)。⚠ 铁律: 本列与同族另八列各自 just-identified 并排, 三家三轨严禁混进同一 over-identified Hansen J; 跨模型一致性由 Krippendorff α 与 Cohen κ 报告, 跨模型 FWER 由根级 rwolf 模板承担, 不在单方程内混装。

## VAR: gemini31_cont_sum_full

【变体差分】
本列锁定 gemini31 模型 × full 文本轨。模型维: gemini-3.1-flash-lite 经云雾聚合端点调用, 温度钉零、prompt 字节冻结、判定落缓存以保确定性复现, 与 deepseekv4、gpt54nano 三角互证、不分主次, per-model 独立降级。轨道维: full = content_full = 标题 prepend 后接完整正文, 信息量最全, 亦是全局留篇门控的权威轨 (llm_verified_full 落此轨, full-only 口径 2026-06-29), 故本列行宇宙为母集, ctx 与 ss 轨为其子集; 稳健性叙事中 full 常任首要测量, ctx/ss 作稳健臂。聚合维为 bank-year sum 外延口径, 随全文轨留篇量与逐篇置信度加权净语调共同放大, 与 gemini31_cont_mean_full 内涵均值构成双口径 (外延答总体覆盖强度, 内涵答平均笃定净语调)。此列适合作单模型稳健性检验的 full 轨主锚, 用以对照三家共识与另两家单模型 cont_sum。本列同时是 gemini31_cont_w_sum_full、gemini31_cont_hw_sum_full、gemini31_cont_mw_sum_full 等加权总和的裸参照臂: 加权臂在其上叠加媒体权威度、羊群衰减或投票同意率权重, 而本列不施加任何外生权重, 仅以模型自评置信度调制幅度, 从而隔离出「语调本身」与「权重构造」两类信号来源。数值为正代表 Gemini 对该行当年整体给出净正面且笃定的语调, 绝对值反映报道体量与语调强度的联合规模。⚠ 铁律: 本列与同族另八列各自 just-identified 并排, 三家三轨严禁混进同一 over-identified Hansen J。

## VAR: gemini31_cont_sum_ss

【变体差分】
本列锁定 gemini31 模型 × ss (银行金融科技同句共现) 文本轨。模型维同 gemini31 家族: gemini-3.1-flash-lite 走云雾端点, 取该家自身得分、置信度与 verified。轨道维: ss = content_ss = 标题 prepend 后接银行词与金融科技词同句共现之正负 N 句窗口 (默认半径 1 句), 三轨中语境最收敛、专捕强共现语调。回退语义: 无同句共现时 content_ss 镜像 ctx 回退全文 body 并置 ss_is_fallback=True、共享 n_articles 分母; 金融科技 AC 为空时该篇 ss 全 True 优雅降级。聚合维为 bank-year sum 外延口径, 与 gemini31_cont_mean_ss 内涵均值互补, 并作 gemini31_cont_w_sum_ss 等加权变体的裸参照臂。开发期 T=2 上 ss 轨因同句共现稀疏可能零方差退化属预期, 生产期 T=19 恢复。ss 轨把 Gemini 的语调判定限缩到银行与金融科技同句强共现语境, 是三轨中最贴近本研究核心构念的收敛测度, 相较 ctx 进一步剔除银行出现但与金融科技无关的段落噪声, 因而信噪最纯但也最易受共现稀疏影响。数值为正代表当年该行在同句共现语境下被 Gemini 判为净正面且高把握覆盖, 绝对值随共现报道体量与语调极端度联合抬升。门控守 full-only: 留篇由 llm_verified_full 定, ss 为 conditional-on-full 子集, gemini31 自身 verified 未过者置缺失, per-model 独立降级不牵连另两家。⚠ 铁律: 本列与同族另八列各自 just-identified 并排, 三家三轨严禁混进同一 over-identified Hansen J。

## VAR: gpt54nano_cont_sum_ctx

【变体差分】
本列锁定 gpt54nano 模型 × ctx 文本轨。模型维: gpt54nano 是 gpt-5.4-nano, 经云雾 (yunwu) 聚合端点调用 (与同走云雾的 gemini31 不同模型、与直连的 deepseekv4 不同源), 其得分、置信度、verified 取自该家自身输出, 与另两家 co-equal 互为稳健性、不分主次。轨道维: ctx = content_ctx = 标题 prepend 后接含目标银行句的正负 N 句窗口 (实体邻近上下文), 聚焦银行相关语境, 较 full 更窄、较 ss 更宽。聚合维为 bank-year sum 外延口径, 随该行当年 ctx 轨留篇量放大, 与 gpt54nano_cont_mean_ctx 内涵均值互补。门控守 full-only: 留篇由 llm_verified_full 决定, ctx 为 conditional-on-full 子集, gpt54nano 自身 verified 未过篇置缺失不入总和, per-model 独立降级 (gpt54nano 缺席只掉本族)。此列常与 deepseekv4_cont_sum_ctx、gemini31_cont_sum_ctx 三家并列于同一稳健性表列作跨厂商稳健对照。本列亦是 gpt54nano_cont_w_sum_ctx、gpt54nano_cont_hw_sum_ctx 等加权变体的裸参照臂, 未叠加任何外生权重, 仅以模型自评置信度调制幅度; 数值为正表示该行当年 ctx 语境下被 OpenAI 系模型判为净正面且高把握覆盖, 为负则净负面, 绝对值随覆盖量与语调极端度联合抬升, 供跨模型分歧诊断。本列与 deepseekv4、gemini31 的同轨 cont_sum 之间的符号一致性与离散度, 可量化 ctx 语境下语调测量的跨厂商稳健程度, 分歧越小越表明结论不依赖单一厂商模型的特质。⚠ 铁律: 本列与同族另八列各自 just-identified 并排, 三家三轨严禁混进同一 over-identified Hansen J。

## VAR: gpt54nano_cont_sum_full

【变体差分】
本列锁定 gpt54nano 模型 × full 文本轨。模型维: gpt-5.4-nano 经云雾聚合端点调用, 温度钉零、prompt 冻结、判定落缓存, 与 deepseekv4、gemini31 三角互证、不分主次, per-model 独立降级。轨道维: full = content_full = 标题 prepend 后接完整正文, 信息量最全, 亦是全局留篇门控权威轨 (llm_verified_full 落此轨, full-only 口径 2026-06-29), 故本列行宇宙为母集, ctx 与 ss 轨为其子集; full 轨在稳健性叙事中常任首要测量。聚合维为 bank-year sum 外延口径, 随全文轨留篇量与逐篇置信度加权净语调共同放大, 与 gpt54nano_cont_mean_full 内涵均值构成双口径并置。作为三家中 OpenAI 系单模型的 full 轨 cont_sum, 本列是检验主结论是否被单一厂商模型驱动的关键稳健锚之一 (呼应 Carlson & Burbano 2026 多模型交叉验证守则)。本列同时是 gpt54nano_cont_w_sum_full、gpt54nano_cont_hw_sum_full、gpt54nano_cont_mw_sum_full 等加权总和的裸参照臂: 加权臂叠加媒体权威度、羊群衰减或投票同意率权重, 而本列仅以模型自评置信度调制幅度、不施外生权重, 从而隔离语调本身与权重构造两类信号。数值为正代表 gpt-5.4-nano 对该行当年整体给出净正面且笃定语调, 绝对值反映报道体量与语调强度联合规模。作为单厂商原始信号, 本列未经三家多数投票折叠, 与共识 llm_vote_cont_sum_full 并置可诊断 OpenAI 系模型相对共识的系统性偏移。⚠ 铁律: 本列与同族另八列各自 just-identified 并排, 三家三轨严禁混进同一 over-identified Hansen J。

## VAR: gpt54nano_cont_sum_ss

【变体差分】
本列锁定 gpt54nano 模型 × ss (银行金融科技同句共现) 文本轨。模型维同 gpt54nano 家族: gpt-5.4-nano 走云雾端点, 取该家自身得分、置信度与 verified。轨道维: ss = content_ss = 标题 prepend 后接银行词与金融科技词同句共现之正负 N 句窗口 (默认半径 1 句), 三轨中语境最收敛、专捕强共现语调, 信噪最纯。回退语义须准: 无同句共现时 content_ss 镜像 ctx 回退全文 body 并置 ss_is_fallback=True、共享 n_articles 分母; 金融科技 AC 自动机为空时该篇 ss 全 True 优雅降级。聚合维为 bank-year sum 外延口径, 与 gpt54nano_cont_mean_ss 内涵均值互补, 并作 gpt54nano_cont_w_sum_ss 等加权变体的裸参照臂。开发期 T=2 上 ss 轨因同句共现稀疏可能零方差退化属预期, 生产期 T=19 恢复正常。ss 轨把 gpt-5.4-nano 的语调判定限缩到银行与金融科技同句强共现语境, 是三轨中最贴近本研究核心构念的收敛测度, 相较 ctx 进一步剔除银行出现但与金融科技无关的段落噪声, 信噪最纯但最易受共现稀疏影响。数值为正代表当年被净正面且高把握覆盖, 绝对值随覆盖量与语调极端度联合抬升。门控守 full-only: 留篇由 llm_verified_full 定, ss 为 conditional-on-full 子集, gpt54nano 自身 verified 未过者置缺失, per-model 独立降级不牵连另两家。⚠ 铁律: 本列与同族另八列各自 just-identified 并排, 三家三轨严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.4412788
<!-- rendered-citations:end -->
