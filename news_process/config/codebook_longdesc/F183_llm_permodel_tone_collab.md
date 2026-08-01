---
family_id: F183
columns:
- deepseekv4_tone_collab_ctx
- deepseekv4_tone_collab_full
- deepseekv4_tone_collab_ss
- gemini31_tone_collab_ctx
- gemini31_tone_collab_full
- gemini31_tone_collab_ss
- gpt54nano_tone_collab_ctx
- gpt54nano_tone_collab_full
- gpt54nano_tone_collab_ss
unit: 语调得分 (连续, 约 [-1, 1]; bank-year 组内单模型篇均)
formula: "{short}_tone_collab{track} = mean_over_articles( {short}_score{track} | innovation_collab_mode_full == '外部协同' ), 按 (target_bank, year) 分组; short ∈ {deepseekv4, gemini31, gpt54nano}, track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/encode.py (innovation_collab_mode 分组聚合块, cm_agg)
upstream:
- 21_tone_llms.parquet ({short}_score{track} 单模型文章级语调; innovation_collab_mode_full 共识分类标签)
- 40_panel_yearly.parquet (encode.py bank-year 聚合)
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
  venue: Finance and Economics Discussion Series (Federal Reserve Board)
  pages_or_artno: 2026-020
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
  pages_or_artno: 2412.07031
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: "Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis"
  venue: Journal of Product Innovation Management
  vol: 41
  issue: 4
  pages_or_artno: 793-815
- doi: 10.1111/jofi.13384
  type: journal
  authors: Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L.
  year: 2024
  title: "FinTech credit and entrepreneurial growth"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3309-3359
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"外部协同"这一开放式创新报道子群内, 单个大语言模型给出的情感语调。其构念根植于 Chesbrough (2003) 的开放式创新框架与 Laursen and Salter (2006) 关于外部搜寻广度的经典命题: 银行推进金融科技既可以走自主研发的封闭路径, 也可以通过与外部金融科技企业结盟、合资、股权投资、平台开放等方式协同创新。第五条主线论文 (bank_fintech_collab, 内部代号 P5) 关心的正是媒体报道在描述这类"外部协同"事件时所携带的情感倾向: 当一家银行的金融科技进展被描述为向外借力、开放合作时, 报道语调究竟偏乐观还是偏审慎, 这一子群语调是 P5 处理变量与稳健性叙事的构成要素。与之对照的自主研发子群 (_indep) 及二者之差 tone_gap_indep_collab 共同构成该主线的核心测度。

数据来源上, 每一列都建立在阶段 21 (tone_llms) 的两类产出之上。其一是三家大语言模型逐篇、逐轨给出的文章级情感得分 {short}_score{track}: gpt54nano 为 GPT-5.4-nano (经 yunwu 路由), gemini31 为 Gemini-3.1-flash-lite (经 yunwu 路由), deepseekv4 为 DeepSeek-V4-flash (直连 api.deepseek.com)。其二是三家投票合成的开放式创新模式共识分类标签 innovation_collab_mode_full, 取值域为"自主研发"与"外部协同"两类。本家族列取"外部协同"这一子群, 在该子群内对某一指定模型的逐篇语调按 (target_bank, year) 求组内均值, 落成 bank-year 面板列。命名遵循 {short}_tone_collab{track} 模式, 其中 collab 后缀专指外部协同子群, 而 short 指明该语调来自哪一家厂商的模型。

【方法学与计算】
计算链路在 encode.py 的 innovation_collab_mode 分组聚合块内一次完成。首先以共识分类标签把文章语料切成子集: df_cm = 满足 innovation_collab_mode_full == '外部协同' 的全部文章行。须特别强调一处口径: 子群成员资格恒由全文轨 (_full) 的共识分类标签界定, 与本家族 full-only 留篇门控口径 (2026-06-29) 一致; 三条轨道并不各自重新分类, 换轨只切换语调的度量通道而不改变被计入的文章集合。在该固定子集上, 对每一模型 short 与每一轨道 track, 取源列 {short}_score{track} 按银行-年度分组求均值, 写成 {short}_tone_collab{track}。ss 与 ctx 源列若在上游缺失, 则以 if-in-columns 守卫逐源跳过, 不借用 full 轨分母, 属优雅降级。语调取值继承单篇 LLM 得分的量纲, 约落在 [-1, 1], 正值表示该子群报道整体偏正面。方法学层面, 以生成式模型逐篇标注金融文本、并以 temperature=0 冻结、prompt 冻结、缓存复现的范式, 与 de Kok (2025)、Lan et al. (2025) 所倡导的可复现标注流程一致; 逐篇请求、跨厂商多模型交叉验证的设计则呼应 Ludwig et al. (2025) 对语言模型作为测量工具的计量学审视。

【文献定位】
本家族的方法学定位落在三条相互交织的文献脉络上。第一, 开放式创新的构念与"外部协同 vs 自主研发"的二分, 直接承自 Chesbrough (2003) 与 Laursen and Salter (2006), 并以 Zhang et al. (2024) 发表于 Journal of Product Innovation Management 的二十年元分析作为该二分近期最完整的实证综述锚点, 确认外部协同度是开放式创新绩效的稳健前因与后果维度。第二, 以大语言模型对文本做研究级标注的效度与风险, 由 Carlson and Burbano (2026) 发表于 Strategic Management Journal 的管理学标注指南系统梳理, 提示了逐模型标注的偏差来源与稳健性检验要求; Hansen (2026) 进一步给出无金标准时以 κ/α 一致性验证 LLM 标注的设计。第三, 金融文本情感的 LLM 度量本身, 由 de Kok (2025)、Lan et al. (2025) 面向中文细粒度金融情感的工作提供直接方法对照, 而 Hau et al. (2024) 发表于 The Journal of Finance 对金融科技信贷的研究为银行-金融科技协同这一实体对象提供了经济学背景。本家族三家模型的逐列并排, 正是把 Carlson and Burbano (2026) 所要求的跨标注器稳健性检验落成可审计的面板列。

## VAR: deepseekv4_tone_collab_full

【变体差分】
本列 = DeepSeek-V4-flash (deepseekv4, 直连 api.deepseek.com) 在外部协同子群内的全文轨语调。差分坐标有三: 模型 = deepseekv4, 子群 = 外部协同 (innovation_collab_mode_full == '外部协同'), 轨道 = _full。度量通道取全文轨得分 deepseekv4_score_full, 即以"标题 prepend + 全文正文"为输入所得的单篇情感, 按银行-年度求子群组内均值。子群成员资格由全文轨共识分类界定, 全文轨语调与该分类同轨, 故本列在三轨中口径最一致, 是本模型该子群语调的基准臂。它与同子群的共识列 llm_vote_tone_collab_full 属"逐模型稳健性臂 vs 三家共识 headline"的关系: 共识列是 canonical, 本列是 deepseekv4 单厂商测度。与同家族 gemini31/gpt54nano 的对应列互为稳健性、不分主次, 三家各自 just-identified 并排, 严禁把三家混进同一 over-identified Hansen J。用途上, 本列既可作 P5 外部协同语调的跨厂商稳健性检验分子, 也可与 _indep 侧同模型列作差, 复算单厂商口径下的自主-协同语调差距。须注意本列分母是"外部协同子群篇数"而非全部留篇, 与非分子群的 deepseekv4_tone_full 分母口径不同: 后者对全部 LLM 有效篇求均, 前者只在被判为外部协同的子集内求均, 两者不可混用。deepseekv4 为直连 api.deepseek.com 的第三家投票模型, 其逐篇得分同样受 prompt v8 冻结与缓存命中键约束, 三轨全命中即可在 NEWS_PROCESS_LLM_OFFLINE=1 下零字节复现, 保证本列的跨-run 可复现性。作为共识分类之外的单厂商语调, 本列不参与共识票的合成, 仅作稳健性并排轨存档。

## VAR: deepseekv4_tone_collab_ctx

【变体差分】
本列 = DeepSeek-V4-flash 在外部协同子群内的上下文轨 (_ctx) 语调。差分仅在度量通道: 源列改为 deepseekv4_score_ctx, 即以"标题 + 含目标银行句 ±窗口"的上下文片段为输入所得单篇情感 (Hassan et al. proximity 思路)。关键区别在于, 子群成员资格仍由全文轨共识分类 innovation_collab_mode_full 界定, 换轨只替换语调的度量输入而不重新划分文章集合; 因此本列与 deepseekv4_tone_collab_full 在同一批文章上比较"全文语调"与"实体邻近语调"的差异, 是对语调是否被正文远处噪声稀释的敏感性检验。ctx 轨作为 full 轨的首要稳健性对照轨, 与 full/ss 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。与其他两家模型的 _ctx 列同理并排。在早期试跑 T=2 的盘上, 外部协同子群逐格样本极小, 本列可能大面积缺格, 属预期退化, 生产 T=19 语料下方具信息量。ctx 轨的经济含义在于剔除正文远端与目标银行无关的段落: 一篇长篇报道可能只在中段提及某银行的对外合作, 全文轨语调会被其余无关正文稀释, 而实体邻近截取使语调更贴合"关于该银行外部协同"的局部叙事。因此本列与 deepseekv4_tone_collab_full 之差, 可视为语调对文本聚焦程度的敏感度, 是判断全文轨结论是否被无关正文噪声污染的直接诊断。本列同样受 prompt 冻结与缓存键约束, 缓存三轨全命中即可离线零字节复现。

## VAR: deepseekv4_tone_collab_ss

【变体差分】
本列 = DeepSeek-V4-flash 在外部协同子群内的同句共现轨 (_ss) 语调。度量通道取 deepseekv4_score_ss, 输入为"标题 + 同句内同时含目标银行∧金科词的句 ±窗口"片段; 无此类同句共现时, content_ss 镜像 ctx 回退全文 body 且 ss_is_fallback=True, 语调随之退化为全文口径。子群成员资格与前两列完全一致, 仍由全文轨共识分类 innovation_collab_mode_full 界定, 只切换语调度量输入。本列是三轨中信息最聚焦的稳健性轨: 它逼近"银行与金融科技被同句提及时"这一最窄语境下的报道语调, 用以检验外部协同语调是否对语境窗口的收窄稳健。ss 与 ctx/full 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。因 ss 回退语义镜像 ctx, 在大量文章无同句共现时本列会向全文口径靠拢, 解读时须结合 ss_is_fallback 占比。与 gemini31/gpt54nano 的 _ss 列跨厂商并排, 供逐模型稳健性检验。ss 轨的构念价值在于最大程度排除"银行与金融科技被分别提及但语义无关"的假共现: 只有当二者落在同一句 ±窗口内, 报道才最可能真正在陈述该银行的对外协同事件, 此时的情感语调对外部协同这一构念的效度最高。因此本列常被用作三轨中效度最高但样本最稀的稳健性锚: 若全文轨与同句轨语调在符号与量级上一致, 则外部协同语调结论最为可信。逐模型独立降级意味着 deepseekv4 该轨源列缺失只掉本模型本轨, 不触发 both-or-neither 的双列同置 NaN。

## VAR: gemini31_tone_collab_full

【变体差分】
本列 = Gemini-3.1-flash-lite (gemini31, 经 yunwu 路由) 在外部协同子群内的全文轨语调。差分坐标: 模型 = gemini31, 子群 = 外部协同, 轨道 = _full。度量通道取全文轨得分 gemini31_score_full, 按银行-年度求子群组内均值。子群成员资格由全文轨共识分类界定, 与语调同轨, 故本列为 gemini31 该子群语调的基准臂。它相对同子群共识 headline llm_vote_tone_collab_full 是 Google 系单厂商稳健性臂; 与 deepseekv4/gpt54nano 的同轨对应列互为稳健性、不分主次, 三家各自 just-identified 并排, 严禁三家混进同一 over-identified Hansen J。跨厂商并排的价值在于: 若外部协同语调结论仅由某一家模型驱动, 三列并排回归即可暴露; Carlson and Burbano (2026) 正是把这种跨标注器一致性作为 LLM 标注可信度的必要检验。本列亦可与 gemini31 的 _indep 列作差, 复算单厂商口径的自主-协同语调差距。gemini31 经 yunwu 路由, 与 gpt54nano 同源但为不同厂商模型, 二者与直连的 deepseekv4 构成"两路由源、三厂商"的交叉验证结构; 若外部协同语调结论仅在某一路由或某一厂商成立, 三列并排即暴露。本列语调继承 gemini31 单篇得分的尺度, 该尺度可能与另两家存在系统性偏移, 因此在跨模型汇总时应先做 z 标准化, 只比标准化后的回归系数, 不比原始语调水平。本列不参与共识票合成, 仅作 Google 系单厂商稳健性并排轨。

## VAR: gemini31_tone_collab_ctx

【变体差分】
本列 = Gemini-3.1-flash-lite 在外部协同子群内的上下文轨语调。度量通道取 gemini31_score_ctx (标题 + 含目标银行句 ±窗口)。与 gemini31_tone_collab_full 相比, 唯一差分是语调度量输入换为上下文片段, 而被计入的文章集合仍由全文轨共识分类 innovation_collab_mode_full 固定不变, 因此本列检验 gemini31 的外部协同语调是否对"实体邻近截取"稳健。ctx 轨是 full 轨的首要稳健性对照轨, 与 full/ss 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与 deepseekv4/gpt54nano 的 _ctx 列跨厂商并排。gemini31 的两分类/连续得分尺度与另两家可能存在系统性偏移, 故在跨模型比较水平时须先标准化, 只比标准化系数而非原始语调水平。早期试跑盘 T=2 下子群逐格样本稀薄, 本列缺格属预期退化。ctx 轨对 gemini31 的意义与对其余两家一致: 以含目标银行句 ±窗口的邻近片段替代全文, 剔除正文远端与该银行外部协同无关的段落, 使语调更贴合局部叙事。本列与 gemini31_tone_collab_full 之差, 度量了 Google 系模型的外部协同语调对文本聚焦程度的敏感度; 若两者一致, 则该模型全文语调未被无关正文稀释。本列受 prompt v8 冻结与缓存键约束, 三轨全命中即可离线零字节复现; 逐模型独立降级保证 gemini31 该轨源列缺失只掉本模型本轨, 不触发另两家或另两轨的连坐缺失。

## VAR: gemini31_tone_collab_ss

【变体差分】
本列 = Gemini-3.1-flash-lite 在外部协同子群内的同句共现轨语调。度量通道取 gemini31_score_ss (标题 + 银行∧金科同句 ±窗口; 无共现则镜像 ctx 回退全文, ss_is_fallback=True)。子群成员资格仍由全文轨共识分类界定, 只切换语调度量输入。本列是 gemini31 在最窄语境下的外部协同语调稳健性轨, 用以检验语调结论是否对语境窗口收窄至同句稳健。ss 与 ctx/full 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与 deepseekv4/gpt54nano 的 _ss 列跨厂商并排。因 ss 回退语义镜像 ctx, 在无同句共现文章占比高时本列语调向全文口径回归, 解读须结合回退比例。逐模型独立降级: 若 gemini31 某轨源列缺失, 仅本模型该轨缺席, 不牵连另两家 (非 co-primary 嵌入的 both-or-neither 口径)。ss 轨对 gemini31 的构念价值在于把语境收窄到银行与金融科技词同句共现的最小窗口, 从而最大程度排除二者被分别提及却语义无关的假共现, 使外部协同语调的构念效度最高。因此本列是 Google 系模型三轨中效度最高、样本最稀的稳健性锚: 若 gemini31 的全文轨与同句轨语调在符号与量级上一致, 则其外部协同语调结论最为可信。在无同句共现文章占比高的银行-年度, 本列会因 ss 回退而向全文口径靠拢, 解读须结合 ss_is_fallback 占比。本列受 prompt 冻结与缓存键约束, 缓存三轨全命中即可离线零字节复现。

## VAR: gpt54nano_tone_collab_full

【变体差分】
本列 = GPT-5.4-nano (gpt54nano, 经 yunwu 路由) 在外部协同子群内的全文轨语调。差分坐标: 模型 = gpt54nano, 子群 = 外部协同, 轨道 = _full。度量通道取 gpt54nano_score_full, 按银行-年度求子群组内均值; 子群成员资格由全文轨共识分类界定, 与语调同轨, 是 gpt54nano 该子群语调的基准臂。相对同子群共识 headline llm_vote_tone_collab_full, 本列是 OpenAI 系单厂商稳健性臂; 与 deepseekv4/gemini31 的同轨对应列互为稳健性、不分主次, 三家各自 just-identified 并排, 严禁三家混进同一 over-identified Hansen J。三家逐列并排把 de Kok (2025)、Ludwig et al. (2025) 所强调的"LLM 测量须暴露模型选择敏感性"落成可审计面板。本列可作 P5 外部协同语调跨厂商稳健性检验分子, 亦可与 gpt54nano 的 _indep 列作差, 复算单厂商口径自主-协同语调差距。gpt54nano 经 yunwu 路由, 与 gemini31 同一路由源但为不同厂商模型, 与直连 api.deepseek.com 的 deepseekv4 一道构成两路由源、三厂商的交叉验证结构。本列分母是外部协同子群篇数而非全部留篇, 与非分子群的 gpt54nano_tone_full 分母口径不同, 二者不可混用。本列语调继承 gpt54nano 单篇得分尺度, 该尺度可能与另两家存在系统性偏移, 跨模型汇总须先 z 标准化只比标准化系数。本列受 prompt v8 冻结与缓存命中键约束, 三轨全命中即可在离线守卫下零字节复现; 作为 OpenAI 系单厂商语调, 本列不参与共识票合成, 仅作稳健性并排轨存档。

## VAR: gpt54nano_tone_collab_ctx

【变体差分】
本列 = GPT-5.4-nano 在外部协同子群内的上下文轨语调。度量通道取 gpt54nano_score_ctx (标题 + 含目标银行句 ±窗口)。与 gpt54nano_tone_collab_full 的唯一差分是语调度量输入换为上下文片段, 被计入文章集合仍由全文轨共识分类 innovation_collab_mode_full 固定, 因此本列检验 gpt54nano 外部协同语调对实体邻近截取的稳健性。ctx 是 full 的首要稳健性对照轨, 与 full/ss 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与 deepseekv4/gemini31 的 _ctx 列跨厂商并排。跨模型比较水平前须标准化, 只比标准化系数。早期试跑盘 T=2 外部协同子群逐格样本极小, 本列缺格属预期退化, 生产 T=19 语料下方有稳定分布。本列的诊断意义与 deepseekv4_tone_collab_ctx 平行: 它衡量 gpt54nano 的外部协同语调在把输入从全文收窄到实体邻近片段后是否漂移。若 gpt54nano_tone_collab_full 与 gpt54nano_tone_collab_ctx 差异显著, 说明该模型的全文语调受正文远端无关段落影响较大, 需以 ctx 轨作为更聚焦的稳健性对照。本列受 prompt v8 冻结与缓存命中键约束, 三轨全命中即可离线零字节复现; 逐模型独立降级保证 gpt54nano 该轨源列缺失不牵连另两家。须再次强调, ctx 轨只切换语调度量输入, 被计入的文章集合仍由全文轨共识分类 innovation_collab_mode_full 固定, 与本家族 full-only 门控口径一致, 因此本列与全文轨在完全相同的一批外部协同文章上比较全文语调与邻近语调的差异, 是干净的同集合对照。跨模型比较水平前须先标准化, 只比标准化后的回归系数。

## VAR: gpt54nano_tone_collab_ss

【变体差分】
本列 = GPT-5.4-nano 在外部协同子群内的同句共现轨语调。度量通道取 gpt54nano_score_ss (标题 + 银行∧金科同句 ±窗口; 无共现则镜像 ctx 回退全文, ss_is_fallback=True)。子群成员资格仍由全文轨共识分类界定, 只切换语调度量输入。本列是 gpt54nano 在最窄同句语境下的外部协同语调稳健性轨。ss 与 ctx/full 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与 deepseekv4/gemini31 的 _ss 列跨厂商并排。因 ss 回退语义镜像 ctx, 无同句共现文章占比高时本列语调向全文口径回归。逐模型独立降级: gpt54nano 某轨源列缺失仅本模型该轨缺席, 不牵连另两家。三家 × 三轨共九列合力回答同一问题——外部协同报道语调的结论是否稳健于模型厂商与语境窗口的选择, 这正是 Carlson and Burbano (2026) 与 Hansen (2026) 所要求的跨标注器一致性审计的面板化实现。就 gpt54nano 的同句轨而言, 它把语境收窄到银行与金融科技词同句共现的最小窗口, 排除二者被分别提及却语义无关的假共现, 使外部协同语调的构念效度在 OpenAI 系模型上达到最高。因此本列虽样本最稀, 却是三轨中效度最高的稳健性锚: 若 gpt54nano 的全文轨与同句轨语调符号量级一致, 则该模型外部协同语调结论最可信。在无同句共现文章占比高的银行-年度, 本列会因 ss 回退镜像 ctx 而向全文口径靠拢, 解读须结合 ss_is_fallback 占比。本列受 prompt 冻结与缓存键约束, 缓存三轨全命中即可离线零字节复现。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Hansen, A. L. (2026). Validating large language model annotations. Finance and Economics Discussion Series (Federal Reserve Board) No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. The Journal of Finance, 79(5), 3309-3359. https://doi.org/10.1111/jofi.13384
<!-- rendered-citations:end -->
