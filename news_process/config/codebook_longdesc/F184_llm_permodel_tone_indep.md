---
family_id: F184
columns:
- deepseekv4_tone_indep_ctx
- deepseekv4_tone_indep_full
- deepseekv4_tone_indep_ss
- gemini31_tone_indep_ctx
- gemini31_tone_indep_full
- gemini31_tone_indep_ss
- gpt54nano_tone_indep_ctx
- gpt54nano_tone_indep_full
- gpt54nano_tone_indep_ss
unit: 语调得分 (连续, 约 [-1,1]; 自主研发子样本内单一模型逐篇语调的 bank-year 算术均值)
formula: "per-model 自主研发子样本语调: 单一 LLM 模型 m ∈ {deepseekv4, gemini31, gpt54nano} 的文章级语调得分 m_score_track (track ∈ {full, ctx, ss}), 在 innovation_collab_mode_full == '自主研发' 的文章子样本上按 target_bank×year 取算术均值; 子样本划分键为 full 轨分类 (三轨共用同一 full 划分), 分母 = 该 bank-year 自主研发篇数 n_articles_indep"
producer: news_process/pipeline/panel/encode.py ; news_process/pipeline/sentiment/tone_llms.py ; news_process/pipeline/panel/export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (逐篇 m_score_track + innovation_collab_mode_full 协同模式分类)
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
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: "Validating large language model annotations"
  venue: FEDS Working Paper No. 2026-020, Federal Reserve Board
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv (NBER Working Paper No. 33344)
- doi: 10.48550/arXiv.2509.08825
  type: arxiv
  authors: Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D.
  year: 2025
  title: "Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation"
  venue: arXiv
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: 105227
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是「单一大语言模型在『自主研发』协同模式子样本上给出的银行涉金融科技报道语调」这一 per-model × 子样本测度族。后缀 indep 并非「模型各自独立、互不折叠」之意, 而是指 P5 开放式创新协同模式维度里的『自主研发 (independent, 独立/内部研发)』子样本, 与对偶后缀 collab (『外部协同』) 一一成对; 也就是说, 每一列先把文章按其被 LLM 分类出的创新协同模式二分 (自主研发 vs 外部协同), 再只在『自主研发』这一半文章上聚合该模型的逐篇语调。前缀 (deepseekv4 = DeepSeek V4 Flash, 直连 api.deepseek.com; gemini31 = Gemini 3.1 Flash Lite, 走 yunwu; gpt54nano = GPT-5.4-nano, 走 yunwu) 才承载「per-model 单一厂商」的身份, 每列由三家中的某一家单独给出, 不经跨家投票合成。构念的经济学意涵是: 当一家银行在某年被媒体报道为「以自主/内部方式推进金融科技」时, 这批报道所承载的情绪极性 (正面—中性—负面)。语调越高表示这半报道整体越正面, 越低越负面, 数值近似落在负一到正一之间, bank-year 层面取该模型在自主研发子样本上逐篇语调的算术均值。协同模式二分借鉴开放式创新框架 (Chesbrough 2003; Laursen 与 Salter 2006), 属 P5 Chesbrough 维度; 数据上游为 stage 14 物化的三轨文本 (content_full / content_ctx / content_ss) 与 stage 21 tone_llms 逐篇输出的语调得分及 innovation_collab_mode_full 协同模式分类。

【方法学与计算】
计算链路起点是 stage 21 的统一 LLM 语义精筛与情感分析模块 tone_llms: 用同一条思维链 Prompt (Chain-of-Thought) 在单次请求内同时获取「真伪判定」「情感判定」与创新属性 (含协同模式) 等输出, 每条新闻对三家模型分别独立请求, 由信号量控制并发。温度参数钉死为零 (temperature=0.0) 以逼近确定性推理, Prompt 版本冻结为 v8 且字节级锁定, 请求—响应经本地磁盘缓存 (_llm_cache.db) 持久化, 缓存命中键含 prompt_version 与 temperature, 因而三轨全部命中时可离线零成本逐字节复现。真正把文章级得分聚合为 bank-year 面板列的环节在 encode.py: 该模块先按 innovation_collab_mode_full 把文章划成『自主研发』与『外部协同』两个子样本 (划分键取 full 轨分类, 故 ctx/ss 语调列亦在同一 full 划分出的自主研发子样本上聚合), 对『自主研发』子样本执行 groupby(target_bank, year).agg, 把每家模型每轨的逐篇得分 m_score_track 取均值, 落成 m_tone_indep_track 列, 分母是该 bank-year 自主研发篇数 n_articles_indep (由 llm_vote_score_full 计数得到), 而非「该模型自身 verified 篇数」。export.py 在此链路里只负责把这些列名映射成人类可读的 Stata 变量标签, 不做数值聚合。全流程仍受 2026-06-29 起生效的 full-only 留篇口径约束: 一篇报道是否被计入「银行金融科技报道」宇宙只看 full 轨验证结果, ctx 与 ss 两轨降为 conditional-on-full 条件测度轨, 其行宇宙是 full 留篇集子集; 在此之上再叠加自主研发子样本这一维度切分。

【文献定位】
本族的两条方法学支柱——「以 LLM 逐篇标注文本情感」与「按创新协同模式对文章分层」——均有系统文献支撑。Carlson 与 Burbano (2026) 在 Strategic Management Journal 上给出管理研究中使用 LLM 标注数据的基础性操作规范与风险警示, 明确指出单一模型标注须辅以可复现的温度、Prompt 与缓存冻结, 并对模型间分歧保持透明, 这正是本族保留三家独立前缀列、并按子样本细分的方法学依据。Gilardi、Alizadeh 与 Kubli (2023) 在 PNAS 上实证表明 ChatGPT 在多类文本标注任务上的准确率与一致性超过众包工人, 为以 LLM 同时充当情感标注器与协同模式分类器提供了效度背书。de Kok (2025) 在 Management Science 上系统梳理了生成式 LLM 用于会计文本分析的规范范式, 特别强调温度置零、Prompt 冻结与结果缓存以保障可复现性, 与本族的确定性推理锚点完全一致。Holzman、Miller 与 Twedt (2023) 在 The Accounting Review 上以媒体情绪度量刻画报道语调对市场的规训作用, 提供了「媒体 tone」构念的金融学落点。方法学审慎面上, Hansen (2026) 讨论无金标准时如何用 κ 与 α 一致性设计验证 LLM 标注; Ludwig、Mullainathan 与 Rambachan (2025) 提出把 LLM 输出纳入计量框架的应用范式; Baumann 等 (2025) 量化了 LLM 文本标注的隐藏风险 (LLM hacking); Chen 等 (2025) 综述了多模型集成方法。这些文献共同支撑「三家 per-model 独立并列、互为稳健性」的取舍。金融文本情感的下游价值可参考 Kirtac 与 Germano (2024) 关于 LLM 情感交易信号的证据。铁律上, 三家 per-model 前缀各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同模型的列混进同一 over-identified 的 Hansen J 过度识别检验; 三轨 full/ctx/ss 亦各自 just-identified 并排、禁混同一 over-identified Hansen J; 真正的跨模型族错误率控制走根级 rwolf 模板, 而非塞进同一工具变量集。per-model 独立降级同样成立: 某一家模型缺席时只掉它自己的自主研发三列, 不牵连另两家, 与 co-primary 嵌入双轨的 both-or-neither 语义截然不同。自主研发 (indep) 与外部协同 (collab) 是同一协同模式维度的对偶两臂, 各自刻画不同创新语境下的媒体情绪, 并非相互替代的稳健性梯子。

## VAR: deepseekv4_tone_indep_full

【变体差分】
本列 = DeepSeek V4 Flash 单一模型在 full 轨上、且限于『自主研发』协同模式子样本的语调, bank-year 聚合均值。后缀 indep 指自主研发 (内部/独立研发) 子样本, 与对偶列 deepseekv4_tone_collab_full (外部协同子样本) 成对: 本列只在被分类为『自主研发』的文章上聚合, 分母 = 该 bank-year 自主研发篇数 n_articles_indep, 而非该模型全样本或其 verified 篇数。模型身份上, deepseekv4 是三家中唯一直连 api.deepseek.com 的一家 (另两家 gemini31 与 gpt54nano 均走 yunwu 网关), 供应商为 DeepSeek 而非 xAI (历史上曾被误标 Grok, 已勘误)。轨道身份上, full 轨输入文本 content_full = 标题 prepend + 全文正文, 模型读到的是整篇报道的完整语料。full 轨在本族中地位特殊: 依 2026-06-29 full-only 留篇门控, 一篇报道是否算入「银行金融科技报道」宇宙只由 full 轨 verified 判定决定; 且自主研发/外部协同的子样本划分键正是 full 轨分类 innovation_collab_mode_full, 故本列是「full 轨语调 × full 轨子样本划分」双 full 对齐。该列与同族 gemini31_tone_indep_full、gpt54nano_tone_indep_full 构成同一 full 轨、同一自主研发子样本上的跨厂商三家并排, 三者互为稳健性、不分主次、各自 just-identified, 严禁混进同一 over-identified Hansen J; 每列只报 DeepSeek 一家在该子样本上的判定, 用于检验主结论是否被任一单一厂商模型驱动。计算细节上, DeepSeek 在同一条思维链 Prompt 内一并给出真伪、情感与创新协同模式, 温度置零、Prompt 冻结 v8 字节级锁定, 请求响应经本地缓存持久化, 三轨全命中时可离线零成本复现。因 DeepSeek 直连独立端点、与另两家网关不同源, 其列在网络与配额层面亦与 yunwu 两家解耦, 单家端点故障只影响本模型的自主研发三列而不牵连另两家, 正是 per-model 独立降级的落点。方法学上保留三家独立前缀列, 呼应 Carlson 与 Burbano (2026) 对模型间分歧保持透明的操作规范, 也为 Krippendorff α 与 Cohen κ 度量跨模型一致性提供原料。

## VAR: deepseekv4_tone_indep_ctx

【变体差分】
本列 = DeepSeek V4 Flash 在 ctx 轨上、限于『自主研发』子样本的语调, bank-year 聚合均值; 对偶列为 deepseekv4_tone_collab_ctx (外部协同子样本)。轨道差分: ctx 轨输入 content_ctx = 标题 prepend + 含目标银行句的 ±窗口上下文片段 (实体邻近窗口, 借鉴 Hassan 2019 的 proximity 思路), 相较 full 轨只保留与目标银行邻近的语料, 剔除无关段落, 逼近「针对该银行的」情绪而非整篇报道的泛泛基调。子样本口径: 自主研发/外部协同划分键取 full 轨分类 innovation_collab_mode_full, 故本列虽读 ctx 语料却在与 full 相同的自主研发子样本上聚合; 叠加 full-only 门控, ctx 轨本身为 conditional-on-full 条件测度轨, 行宇宙是 full 留篇集子集, 分母为该子样本的自主研发篇数。该列与 deepseekv4_tone_indep_full、deepseekv4_tone_indep_ss 构成同一模型、同一自主研发子样本的三轨并排, 三轨互为稳健性、不分主次、各自 just-identified, 严禁混进同一 over-identified Hansen J; 与另两家同轨 ctx 列则构成跨厂商三家并排, 同样禁混。ctx 轨回答「把语料收窄到银行邻近上下文后情绪方向是否稳健」的测量口径敏感性问题。若 full 与 ctx 两轨语调在 DeepSeek 上高度一致, 说明自主研发报道基调本就集中于银行相关段落; 若背离, 提示正文含大量与该行无关的情绪噪声, ctx 收窄恰好将其过滤。与同轨 gemini31_tone_indep_ctx、gpt54nano_tone_indep_ctx 并读, 可分辨「轨道收窄」与「厂商差异」两个正交来源。早期试跑 T=2 小样本上 ctx 轨可能退化甚至方差塌缩, 属预期, 生产期 T=19 语料充分后恢复正常。per-model 独立降级下 DeepSeek 缺席只掉本模型的自主研发三列, 不牵连另两家。

## VAR: deepseekv4_tone_indep_ss

【变体差分】
本列 = DeepSeek V4 Flash 在 ss 轨 (同句共现轨) 上、限于『自主研发』子样本的语调, bank-year 聚合均值; 对偶列为 deepseekv4_tone_collab_ss (外部协同子样本)。轨道差分: ss 轨输入 content_ss = 标题 prepend + 同一句内同时出现「目标银行 ∧ 金融科技词」的句子 ±窗口片段, 是三轨中语料最严格、最聚焦银行—金科关联语境的一轨。回退语义镜像 ctx: 当报道内无银行与金科同句共现时, content_ss 回退全文正文并置 ss_is_fallback=True, 与 ctx 降级逻辑一致, 共享 n_articles 分母; 金科自动机为空时 ss_is_fallback 全置 True 优雅降级。子样本口径: 自主研发/外部协同划分键仍取 full 轨分类 innovation_collab_mode_full, 故本列在与 full 相同的自主研发子样本上聚合, 分母为该子样本自主研发篇数; 叠加 full-only 门控, ss 轨为 conditional-on-full 条件测度轨。该列与 deepseekv4 另两轨、以及另两家同轨 ss 列分别构成三轨并排与跨厂商并排, 均互为稳健性、不分主次、各自 just-identified, 严禁混进同一 over-identified Hansen J。ss 轨回答「只看银行与金科真正同句关联语境时情绪方向是否依然成立」的最严判据稳健性。相较 ctx 轨仅要求含目标银行句, ss 轨额外要求同句内共现金科词, 语料更稀、回退率更高, 是三轨中对「银行—金科关联情绪」最精准也最保守的度量。三轨并读时, DeepSeek 的 full、ctx、ss 三列同向则该行自主研发报道基调稳健; 若 ss 轨与另两轨背离, 提示涉金科语境情绪与整篇基调不同。与另两家同轨 ss 列并读, 可把厂商差异从判据差异中分离。早期试跑 T=2 上 ss 轨可能高度退化甚至零方差, 属预期; 生产语料 T=19 恢复常态。per-model 独立降级下 DeepSeek 缺席只掉本模型的自主研发三列, 不牵连另两家。

## VAR: gemini31_tone_indep_full

【变体差分】
本列 = Gemini 3.1 Flash Lite 单一模型在 full 轨上、限于『自主研发』子样本的语调, bank-year 聚合均值; 对偶列为 gemini31_tone_collab_full (外部协同子样本), 分母 = 该 bank-year 自主研发篇数 n_articles_indep 而非 Gemini 的 verified 篇数。模型身份: gemini31 是 Google 的 Gemini 3.1 Flash Lite, 经 yunwu 网关调用 (与同走 yunwu 的 gpt54nano 同源、与直连 DeepSeek 的 deepseekv4 异源)。轨道身份: full 轨输入 content_full = 标题 prepend + 全文正文, 既是 full-only 留篇门控主轨, 又是自主研发/外部协同子样本划分键 innovation_collab_mode_full 的来源轨, 故本列语调与子样本划分双 full 对齐。该列与 deepseekv4_tone_indep_full、gpt54nano_tone_indep_full 构成 full 轨、自主研发子样本上的跨厂商三家并排, 三者互为稳健性、不分主次、各自 just-identified, 严禁混进同一 over-identified Hansen J; 本列只报 Gemini 一家在该子样本上的判定, 不经三家投票。保留本列的意义在于, 若主结论仅在 Gemini 上成立而在另两家上翻转, 即暴露单一厂商模型驱动的脆弱性, 三家独立前缀列构成厂商级稳健性交叉验证。计算细节上, Gemini 与另两家共用同一条思维链 Prompt、同一 v8 冻结版本、同一温度置零口径与同一本地缓存, 三家在完全对齐的输入与解码设定下判定, 差异只来自模型本身而非提示或采样配置。方法学上 Gemini 列既是 Gilardi 等 (2023) 所论 LLM 标注效度的又一实例, 也是对 de Kok (2025) 可复现范式 (温度置零、Prompt 冻结、结果缓存) 的直接落地。因 Gemini 走 yunwu 网关、与同源 GPT 共享端点、与直连 DeepSeek 异源, 网关侧配额或故障会同时影响 Gemini 与 GPT 两家而不涉 DeepSeek, 但列级降级仍按 per-model 独立执行, 缺席只掉 Gemini 自身自主研发三列。

## VAR: gemini31_tone_indep_ctx

【变体差分】
本列 = Gemini 3.1 Flash Lite 在 ctx 轨上、限于『自主研发』子样本的语调, bank-year 聚合均值; 对偶列为 gemini31_tone_collab_ctx (外部协同子样本)。轨道差分: ctx 轨输入 content_ctx = 标题 prepend + 目标银行句 ±窗口的实体邻近上下文, 剔除与目标银行无关的段落, 逼近针对该行的情绪。子样本与门控口径: 自主研发/外部协同划分键取 full 轨分类 innovation_collab_mode_full, 故本列在与 full 相同的自主研发子样本上聚合, 分母为该子样本自主研发篇数; 叠加 full-only, ctx 轨为 conditional-on-full 条件测度轨, 行宇宙是 full 留篇集子集。该列与 gemini31 另两轨构成三轨并排, 与另两家同轨 ctx 列构成跨厂商并排, 均互为稳健性、不分主次、各自 just-identified, 严禁混进同一 over-identified Hansen J。ctx 轨回答把语料收窄到银行邻近上下文后 Gemini 情绪判定是否稳健的口径敏感性问题。与同轨 deepseekv4_tone_indep_ctx、gpt54nano_tone_indep_ctx 并读, 可分辨「轨道差异」与「厂商差异」两个正交来源。若 Gemini 的 full 与 ctx 两列高度一致, 说明自主研发报道基调集中于银行相关段落; 若背离, 提示正文含大量与该行无关的情绪, ctx 收窄将其滤除。ctx 轨与 full、ss 共同构成 Gemini 的三轨稳健性组; 三轨同向则该行基调稳健。早期试跑 T=2 小样本上 ctx 轨可能退化甚至方差塌缩, 属预期, 生产期 T=19 语料充分后恢复正常; per-model 独立降级下 Gemini 缺席只掉本模型的自主研发三列, 不牵连 DeepSeek 与 GPT。

## VAR: gemini31_tone_indep_ss

【变体差分】
本列 = Gemini 3.1 Flash Lite 在 ss 轨 (同句共现轨) 上、限于『自主研发』子样本的语调, bank-year 聚合均值; 对偶列为 gemini31_tone_collab_ss (外部协同子样本)。轨道差分: ss 轨输入 content_ss = 标题 prepend + 银行与金科词同句共现句 ±窗口, 语料最严格。回退语义镜像 ctx: 无银行金科同句共现时 content_ss 回退全文正文并置 ss_is_fallback=True, 共享 n_articles 分母; 金科自动机为空时 ss_is_fallback 全置 True 优雅降级。子样本与门控口径: 自主研发/外部协同划分键取 full 轨分类 innovation_collab_mode_full, 故本列在与 full 相同的自主研发子样本上聚合, 分母为该子样本自主研发篇数; 叠加 full-only, ss 轨为 conditional-on-full 条件测度轨。该列与 gemini31 另两轨、以及另两家同轨 ss 列分别构成三轨并排与跨厂商并排, 均互为稳健性、不分主次、各自 just-identified, 严禁混进同一 over-identified Hansen J。ss 轨回答「只看银行与金科真正同句关联语境时 Gemini 情绪方向是否成立」的最严判据稳健性。相较 ctx 轨仅要求含目标银行句, ss 轨额外要求同句内共现金科词, 语料更稀、回退率更高, 是三轨中对涉金科情绪最精准也最保守的度量。三轨并读时, Gemini 的 full、ctx、ss 三列同向则该行自主研发报道基调稳健; 若 ss 轨与另两轨背离, 提示涉金科语境情绪与整篇基调不同。与另两家同轨 ss 列并读, 可把厂商差异从判据差异中分离检验。早期试跑 T=2 上 ss 轨可能零方差退化, 属预期; 生产 T=19 恢复常态。per-model 独立降级下 Gemini 缺席只掉本模型的自主研发三列, 不牵连 DeepSeek 与 GPT。

## VAR: gpt54nano_tone_indep_full

【变体差分】
本列 = GPT-5.4-nano 单一模型在 full 轨上、限于『自主研发』子样本的语调, bank-year 聚合均值; 对偶列为 gpt54nano_tone_collab_full (外部协同子样本), 分母 = 该 bank-year 自主研发篇数 n_articles_indep 而非 GPT 的 verified 篇数。模型身份: gpt54nano 是 OpenAI 系的 GPT-5.4-nano, 经 yunwu 网关调用 (与 gemini31 同源、与直连 DeepSeek 的 deepseekv4 异源)。轨道身份: full 轨输入 content_full = 标题 prepend + 全文正文, 既是 full-only 留篇门控主轨, 又是自主研发/外部协同子样本划分键 innovation_collab_mode_full 的来源轨, 故本列语调与子样本划分双 full 对齐。该列与 deepseekv4_tone_indep_full、gemini31_tone_indep_full 构成 full 轨、自主研发子样本上的跨厂商三家并排, 互为稳健性、不分主次、各自 just-identified, 严禁混进同一 over-identified Hansen J; 本列只报 GPT 一家在该子样本上的判定。保留本列的意义在于把 OpenAI 系模型的独立判定单独暴露出来, 与另两家交叉验证, 确保主结论不被任一单一厂商模型驱动。三家独立前缀列并读, 亦可经 κ 与 Krippendorff α 度量模型间一致性, 呼应 Hansen (2026) 无金标准时以一致性验证 LLM 标注的方法学建议。计算细节上, GPT 与另两家共用同一条思维链 Prompt、同一 v8 冻结版本、同一温度置零口径与同一本地缓存, 三家在完全对齐的输入与解码设定下判定, 差异只来自模型本身。因 GPT 走 yunwu 网关、与 Gemini 同源、与直连 DeepSeek 异源, 端点层面 GPT 与 Gemini 共享配额, 但列级降级仍严格 per-model 独立, 缺席只掉 GPT 自身自主研发三列。方法学上, 三家来自 OpenAI、Google、DeepSeek 三个不同厂商与训练体系, 彼此判定相关性越低, 三家一致时的共识越可信, 这正是 Chen 等 (2025) 所论多模型集成价值的具体体现。

## VAR: gpt54nano_tone_indep_ctx

【变体差分】
本列 = GPT-5.4-nano 在 ctx 轨上、限于『自主研发』子样本的语调, bank-year 聚合均值; 对偶列为 gpt54nano_tone_collab_ctx (外部协同子样本)。轨道差分: ctx 轨输入 content_ctx = 标题 prepend + 目标银行句 ±窗口的实体邻近上下文, 剔除无关段落, 逼近针对该行的情绪。子样本与门控口径: 自主研发/外部协同划分键取 full 轨分类 innovation_collab_mode_full, 故本列在与 full 相同的自主研发子样本上聚合, 分母为该子样本自主研发篇数; 叠加 full-only, ctx 轨为 conditional-on-full 条件测度轨, 行宇宙为 full 留篇集子集。该列与 gpt54nano 另两轨构成三轨并排, 与另两家同轨 ctx 列构成跨厂商并排, 均互为稳健性、不分主次、各自 just-identified, 严禁混进同一 over-identified Hansen J。ctx 轨回答把语料收窄到银行邻近上下文后 GPT 情绪判定是否稳健的口径敏感性问题。与同轨 deepseekv4_tone_indep_ctx、gemini31_tone_indep_ctx 并读, 可把轨道敏感性与厂商敏感性两条正交稳健性维度分离检验。若 GPT 的 full 与 ctx 两列高度一致, 说明自主研发报道基调集中于银行相关段落; 若背离, 提示正文含大量与该行无关的情绪, ctx 收窄将其滤除。ctx 轨与 full、ss 共同构成 GPT 的三轨稳健性组; 三轨同向则该行基调稳健, 背离则须逐轨排查语料收窄带来的情绪偏移来源。早期试跑 T=2 小样本上 ctx 轨可能退化甚至方差塌缩, 属预期, 生产期 T=19 语料充分后恢复正常; per-model 独立降级下 GPT 缺席只掉本模型的自主研发三列, 不牵连 DeepSeek 与 Gemini。

## VAR: gpt54nano_tone_indep_ss

【变体差分】
本列 = GPT-5.4-nano 在 ss 轨 (同句共现轨) 上、限于『自主研发』子样本的语调, bank-year 聚合均值; 对偶列为 gpt54nano_tone_collab_ss (外部协同子样本)。轨道差分: ss 轨输入 content_ss = 标题 prepend + 银行与金科词同句共现句 ±窗口, 是三轨中语料最严格、最聚焦银行—金科关联语境的一轨。回退语义镜像 ctx: 无银行金科同句共现时 content_ss 回退全文正文并置 ss_is_fallback=True, 共享 n_articles 分母; 金科自动机为空时 ss_is_fallback 全置 True 优雅降级。子样本与门控口径: 自主研发/外部协同划分键取 full 轨分类 innovation_collab_mode_full, 故本列在与 full 相同的自主研发子样本上聚合, 分母为该子样本自主研发篇数; 叠加 full-only, ss 轨为 conditional-on-full 条件测度轨。该列与 gpt54nano 另两轨、以及另两家同轨 ss 列分别构成三轨并排与跨厂商并排, 均互为稳健性、不分主次、各自 just-identified, 严禁混进同一 over-identified Hansen J。ss 轨回答「只看银行与金科真正同句关联语境时 GPT 情绪方向是否成立」的最严判据稳健性。相较 ctx 轨仅要求含目标银行句, ss 轨额外要求同句内共现金科词, 语料更稀、回退率更高, 是三轨中对涉金科情绪最精准也最保守的度量。三轨并读时, GPT 的 full、ctx、ss 三列同向则该行自主研发基调稳健; 若 ss 轨与另两轨背离, 提示涉金科语境情绪与整篇基调不同。与另两家同轨 ss 列并读, 可把厂商差异从判据差异中分离。早期试跑 T=2 上 ss 轨可能零方差退化, 属预期; 生产 T=19 恢复常态; per-model 独立降级下 GPT 缺席只掉本模型的自主研发三列。至此三家 × 三轨九列构成完整的「per-model × 自主研发子样本」语调矩阵, 均与对偶的 collab 外部协同子样本列成对; 三家各自 just-identified 并排、互为稳健性、不分主次, 三轨亦然, 严禁混进同一 over-identified Hansen J, 供跨厂商与跨轨道双向稳健性交叉验证。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Hansen, A. L. (2026). Validating large language model annotations. FEDS Working Paper No. 2026-020, Federal Reserve Board [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv (NBER Working Paper No. 33344) [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D. (2025). Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2509.08825
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
<!-- rendered-citations:end -->
