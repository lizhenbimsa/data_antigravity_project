---
family_id: F177
columns:
- deepseekv4_score_hw_sum_ctx
- deepseekv4_score_hw_sum_full
- deepseekv4_score_hw_sum_ss
- gemini31_score_hw_sum_ctx
- gemini31_score_hw_sum_full
- gemini31_score_hw_sum_ss
- gpt54nano_score_hw_sum_ctx
- gpt54nano_score_hw_sum_full
- gpt54nano_score_hw_sum_ss
unit: 无量纲加权分值之和 (herd-weighted 离散语调得分的 bank-year 求和; 下游除以同轨 herd 权重和得均值语调)
formula: "{short}_score_hw_sum{track} = Σ_{a ∈ bank-year} {short}_score{track}_a × herd_weight{track}_a; 其中 {short}_score ∈ {+1, 0, -1} 为单一 LLM 的离散签名语调票, herd_weight 来自 stage 24 herd_decay 处理器; {short} ∈ {gpt54nano, gemini31, deepseekv4}, track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/runner.py (逐文章 {short}_score_hw 加权列) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (bank-year sum)
upstream:
- 21_tone_llms.parquet (逐模型离散语调票 {short}_score{track})
- 24_herd_decay_processor.parquet (三轨 herd_weight{track})
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: "Validating large language model annotations"
  venue: FEDS Working Paper
  pages_or_artno: No. 2026-020
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv
- doi: 10.1073/pnas.2308950121
  type: journal
  authors: Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J.
  year: 2024
  title: "GPT is an effective tool for multilingual psychological text analysis"
  venue: Proceedings of the National Academy of Sciences
  vol: 121
  issue: 34
  pages_or_artno: e2308950121
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
  pages_or_artno: No. 4412788
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"单一大语言模型 (LLM) 对某银行-年内每篇银行金融科技报道所给出的离散语调票, 经跟风衰减权重加权后在该银行-年上求和所得的分子量"。九个列由三家彼此独立的商用大模型 (gpt54nano 即 gpt-5.4-nano、gemini31 即 gemini-3.1-flash-lite、deepseekv4 即 deepseek-v4-flash) 与三条文本轨道 (full、ctx、ss) 交叉笛卡尔积而成, 每列均为一个 bank-year 级的加权求和量, 而非最终的均值语调。它是下游"逐模型跟风加权语调" (下游列名形如 {short}_tone_hw{track}) 的分子: 均值语调等于本分子除以同轨的跟风权重有效样本和。之所以把分子单独物化落列, 是为了让面板层能以严格逐轨、逐模型的分母重构任意加权口径, 而不必回到文章级重算, 同时保证跨口径 (等权 / 提及密度权 VW / 媒体权威权 MW / 跟风权 HW) 之间的分子彼此独立、可审计。

【方法学与计算】
计算分两步。第一步在 stage 21 (tone_llms) 完成: 每篇报道以 full、ctx、ss 三种文本形态分别提交给三家模型, 每家模型经同一条思维链 Prompt 同时输出"真伪判定"与"情感判定", 情感判定被离散映射为签名语调票 {short}_score{track} ∈ {+1, 0, −1} (正面记 +1、中性记 0、负面记 −1)。三家模型逐条并发独立请求, 互不参照。第二步在面板构建阶段 (runner.py) 把每篇报道的该模型签名票乘以同轨的跟风衰减权重 herd_weight{track} 得到文章级加权列 {short}_score_hw{track}, 随后 encode.py 的聚合字典把它按 (target_bank, year) 求和, 落为本家族列。跟风衰减权重来自 stage 24 herd_decay 处理器, 用以对同一事件被多家媒体扎堆转载的"羊群式"报道降权, 抑制信息重复计数。权重为三轨独立构造 (herd_weight_full / herd_weight_ctx / herd_weight_ss), 因此本家族的加权分子亦严格逐轨, 不跨轨借权重。

【文献定位】
本家族的方法学根基在于"以大模型充当文本标注器"的可靠性证据链。Gilardi et al. (2023) 在 PNAS 上证明 ChatGPT 在多项文本标注任务上超越众包工人, Rathje et al. (2024) 进一步证实 GPT 类模型在多语种心理文本分析上的有效性, 二者共同支撑了以中文银行报道语调作为标注对象的可行性。de Kok (2025) 在 Management Science 上系统梳理了在会计研究中使用生成式大模型做文本分析的规范, 特别强调 temperature=0、Prompt 冻结与结果缓存以保证可复现性——这正是本项目 stage 21 的确定性锚点做法。Hansen (2026) 提出在缺乏金标准时以 κ / α 一致性验证大模型标注的设计, Ludwig et al. (2025) 给出把大模型输出嵌入计量框架的形式化处理。多模型并置的思想则呼应 Chen et al. (2025) 关于大模型集成的综述: 三家模型互为稳健性、不分主次。在金融文本语调测量的更长脉络上, Tetlock (2007) 奠定了媒体语调进入资产定价的经验范式, Lopez-Lira & Tang (2023) 与 Huang et al. (2023, FinBERT) 则分别代表生成式与判别式两条机器语调测量路线。⚠ 铁律: 三家模型 (gpt54nano / gemini31 / deepseekv4) 以及三条文本轨道 (full / ctx / ss) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把跨模型或跨轨的分子混进同一条 over-identified 的 Hansen J 检验; 每家模型、每条轨道各自单独进入自回归或 2SLS, 作为稳健性并排展示。

## VAR: deepseekv4_score_hw_sum_ctx

【变体差分】
本列 = DeepSeek-V4-Flash (deepseekv4) 在 ctx 轨上的跟风加权签名语调票之 bank-year 求和。模型维度: deepseekv4 特指 deepseek-v4-flash, 由 config/sentiment.yaml::models 单一事实源定义, 直连 api.deepseek.com (与 gpt54nano / gemini31 经 OpenLux 网关路由不同源), 是三家投票中唯一独立厂商端点; 历史上曾被误标为 "Grok-4.1", 已于 2026-06-11 勘误为 DeepSeek。轨道维度: ctx 轨的输入文本 content_ctx = 标题 prepend + 含目标银行句的 ±窗口上下文片段 (Hassan et al. 2019 邻近性思想), 相较 full 轨聚焦于银行实体周边语境, 削弱全文中与目标银行无关段落的干扰。加权维度: 逐文章的 deepseekv4_score_ctx ∈ {+1, 0, −1} 乘 herd_weight_ctx 后在银行-年上求和, 权重严格取 ctx 轨自身构造的跟风衰减权重, 不借 full 轨权重。本列是分子, 下游 deepseekv4_tone_hw_ctx 由本列除以 ctx 轨跟风权重有效样本和得到。作为加权口径族的一员, 本列与等权语调、提及密度加权 (VW, deepseekv4_score_w_sum_ctx)、媒体权威加权 (MW, deepseekv4_score_mw_sum_ctx) 等分子并列物化, 各加权口径的分子彼此正交、互不干扰, 便于面板层以统一除法框架重构任意加权均值而无需回到文章级重算。本家族采用 per-model 独立降级策略: 若 deepseekv4 端点在某次运行中缺席, 仅其自身族列置空, 不牵连 gemini31 / gpt54nano, 亦非 co-primary 嵌入那种 both-or-neither 的连坐。缓存确定性上, stage 21 以 prompt v8 字节级冻结加 temperature=0 为锚, 三轨全命中缓存时可离线零字节复现本列。⚠ 铁律: 本列作为 deepseekv4 单模型 × ctx 单轨的稳健性并排项, 与其它两模型、其它两轨各自 just-identified 并排, 严禁与它们混入同一 over-identified Hansen J。

## VAR: deepseekv4_score_hw_sum_full

【变体差分】
本列 = DeepSeek-V4-Flash (deepseekv4) 在 full 轨上的跟风加权签名语调票之 bank-year 求和, 是本家族在留篇门控口径下最贴近"主"测量的轨道。模型维度同 deepseekv4 家族: deepseek-v4-flash 直连 api.deepseek.com, 独立于经 OpenLux 路由的另两家。轨道维度: full 轨输入 content_full = 标题 prepend + 全文正文, 覆盖报道全文信息, 是留篇门控 (2026-06-29 full-only 口径) 的判定基准轨——一篇报道是否被计为"银行金科报道"只看 full 轨的 llm_verified_full, 因此 full 轨的行宇宙即银行-年留篇集本身, ctx / ss 轨为其 conditional-on-full 的子集测度。加权维度: 逐文章 deepseekv4_score_full × herd_weight_full 在银行-年上求和; full 轨权重亦独立构造。本列为分子, 下游 deepseekv4_tone_hw_full 由本列除以 full 轨跟风权重有效样本和。作为加权口径族的一员, 本列与等权语调、提及密度加权 (VW, deepseekv4_score_w_sum_full)、媒体权威加权 (MW, deepseekv4_score_mw_sum_full) 等分子并列物化, 各加权口径的分子彼此正交、互不干扰, 便于面板层以统一除法框架重构任意加权均值而无需回到文章级重算。本家族采用 per-model 独立降级策略: 若 deepseekv4 端点缺席, 仅掉自身族列, 不牵连另两家, 亦非 co-primary 嵌入的 both-or-neither 连坐。缓存确定性上, stage 21 以 prompt v8 字节级冻结加 temperature=0 为确定性锚, 三轨全命中缓存时可离线零字节复现, 保证跨运行 golden 可复现。⚠ 铁律: 本列作为 deepseekv4 单模型 × full 单轨稳健性并排项, 与另两家模型、另两条轨各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; DeepSeek 的厂商与端点独立性正是三角交叉验证 (triangulation) 的价值所在。

## VAR: deepseekv4_score_hw_sum_ss

【变体差分】
本列 = DeepSeek-V4-Flash (deepseekv4) 在 ss 轨上的跟风加权签名语调票之 bank-year 求和。模型维度同上: deepseek-v4-flash 直连独立端点。轨道维度: ss (same-sentence) 轨输入 content_ss = 标题 prepend + 同句内同时含"目标银行 ∧ 金科词"的句子的 ±窗口片段, 是三轨中语义最严格的银行金科共现片段, 由 stage 14 ctx_materializer 物化 (stage 13 仅上游共现硬过滤、不物化文本列); 当某报道不存在银行与金科词的同句共现时, ss 轨镜像 ctx 的回退语义、退回全文 body 并置 ss_is_fallback=True。加权维度: 逐文章 deepseekv4_score_ss × herd_weight_ss 在银行-年上求和, 权重取 ss 轨自身跟风衰减权重。本列是分子, 下游 deepseekv4_tone_hw_ss 由本列除以 ss 轨跟风权重有效样本和。因 ss 轨在早期试跑 T=2 语料上共现稀疏、常大面积回退, 其数值分布与 full / ctx 可显著不同, 属预期的语料退化而非缺陷。作为加权口径族的一员, 本列与等权语调、提及密度加权 (VW, deepseekv4_score_w_sum_ss)、媒体权威加权 (MW, deepseekv4_score_mw_sum_ss) 等分子并列物化, 各加权口径的分子彼此正交、互不干扰, 便于面板层统一重构加权均值而无需回文章级重算。本家族采用 per-model 独立降级策略: deepseekv4 缺席仅掉自身族列, 不牵连另两家。缓存确定性上, stage 21 以 prompt v8 冻结加 temperature=0 为锚, 三轨全命中缓存时离线零字节可复现。⚠ 铁律: 本列作为 deepseekv4 单模型 × ss 单轨稳健性并排项, 与另两模型、另两轨各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。

## VAR: gemini31_score_hw_sum_ctx

【变体差分】
本列 = Gemini-3.1-Flash-Lite (gemini31) 在 ctx 轨上的跟风加权签名语调票之 bank-year 求和。模型维度: gemini31 特指 gemini-3.1-flash-lite, 经 OpenLux 网关路由 (与 gpt54nano 同源网关、与 deepseekv4 的直连端点不同源), 是三家投票中的 Google 系模型, 在跨厂商三角验证中代表与 OpenAI 系、DeepSeek 系并列的第三个独立信号源。轨道维度: ctx 轨 content_ctx = 标题 prepend + 含目标银行句的 ±窗口上下文, 聚焦银行实体邻近语境。加权维度: 逐文章 gemini31_score_ctx ∈ {+1, 0, −1} × herd_weight_ctx 在银行-年上求和, 权重严格取 ctx 轨跟风衰减权重, 不跨轨借权。本列为分子, 下游 gemini31_tone_hw_ctx 由本列除以 ctx 轨跟风权重有效样本和。跨模型一致性 (与 gpt54nano、deepseekv4 同轨列的 Krippendorff α / Cohen κ) 是评估三家标注收敛度的稳健性证据。作为加权口径族的一员, 本列与等权语调、提及密度加权 (VW, gemini31_score_w_sum_ctx)、媒体权威加权 (MW, gemini31_score_mw_sum_ctx) 等分子并列物化, 各口径分子彼此正交、互不干扰, 便于面板层以统一除法框架重构任意加权均值。本家族采用 per-model 独立降级: gemini31 缺席仅掉自身族列, 不牵连 gpt54nano / deepseekv4, 亦非 co-primary 嵌入的 both-or-neither 连坐。缓存确定性上, stage 21 以 prompt v8 冻结加 temperature=0 为锚, 三轨全命中缓存时可离线零字节复现本列。⚠ 铁律: 本列作为 gemini31 单模型 × ctx 单轨稳健性并排项, 与另两模型、另两轨各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。

## VAR: gemini31_score_hw_sum_full

【变体差分】
本列 = Gemini-3.1-Flash-Lite (gemini31) 在 full 轨上的跟风加权签名语调票之 bank-year 求和。模型维度同 gemini31 家族: gemini-3.1-flash-lite 经 OpenLux 路由, 代表 Google 系独立信号。轨道维度: full 轨 content_full = 标题 prepend + 全文正文, 是留篇门控的判定基准轨 (full-only 口径, 2026-06-29): 报道是否计为银行金科报道只看 full 轨验证结果, 故 full 轨行宇宙即银行-年留篇集本身。加权维度: 逐文章 gemini31_score_full × herd_weight_full 在银行-年上求和, full 轨权重独立构造。本列为分子, 下游 gemini31_tone_hw_full 由本列除以 full 轨跟风权重有效样本和。相较 gpt54nano_score_hw_sum_full 与 deepseekv4_score_hw_sum_full, 本列仅在模型厂商上不同, 三者构成同一 full 轨上的跨厂商稳健性梯队, 用于检验主结论不被单一大模型的系统性标注偏差驱动。作为加权口径族的一员, 本列与等权语调、提及密度加权 (VW, gemini31_score_w_sum_full)、媒体权威加权 (MW, gemini31_score_mw_sum_full) 等分子并列物化, 各口径分子彼此正交、互不干扰, 便于面板层统一重构加权均值而无需回文章级重算。本家族采用 per-model 独立降级: gemini31 缺席仅掉自身族列, 不牵连另两家, 亦非 co-primary 嵌入的 both-or-neither 连坐。缓存确定性上, stage 21 以 prompt v8 字节级冻结加 temperature=0 为确定性锚, 三轨全命中缓存时离线零字节可复现。⚠ 铁律: 本列作为 gemini31 单模型 × full 单轨稳健性并排项, 与另两模型、另两轨各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。

## VAR: gemini31_score_hw_sum_ss

【变体差分】
本列 = Gemini-3.1-Flash-Lite (gemini31) 在 ss 轨上的跟风加权签名语调票之 bank-year 求和。模型维度同上: gemini-3.1-flash-lite 经 OpenLux 路由的 Google 系独立信号。轨道维度: ss 轨 content_ss = 标题 prepend + 同句内同时含"目标银行 ∧ 金科词"的句子 ±窗口片段, 是语义最严格的银行金科共现轨, 由 stage 14 ctx_materializer 物化 (stage 13 仅上游共现硬过滤、不物化文本列); 无同句共现时镜像 ctx 回退语义、退回全文 body 并置 ss_is_fallback=True (与 full / ctx 共享 n_articles 分母)。加权维度: 逐文章 gemini31_score_ss × herd_weight_ss 在银行-年上求和, 权重取 ss 轨自身跟风衰减权重。本列是分子, 下游 gemini31_tone_hw_ss 由本列除以 ss 轨跟风权重有效样本和。ss 轨在开发期语料上因共现稀疏而多回退, 数值可退化, 属预期; 生产期 T=19 全量语料上共现覆盖显著改善。作为加权口径族的一员, 本列与等权语调、提及密度加权 (VW, gemini31_score_w_sum_ss)、媒体权威加权 (MW, gemini31_score_mw_sum_ss) 等分子并列物化, 各口径分子彼此正交、互不干扰, 便于面板层统一重构加权均值。本家族采用 per-model 独立降级: gemini31 缺席仅掉自身族列, 不牵连另两家, 亦非嵌入双轨的 both-or-neither 连坐。缓存确定性上, stage 21 以 prompt v8 字节级冻结加 temperature=0 为确定性锚, 三轨全命中缓存时离线零字节可稳定复现本列, 保证跨运行可复现。⚠ 铁律: 本列作为 gemini31 单模型 × ss 单轨稳健性并排项, 与另两模型、另两轨各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_score_hw_sum_ctx

【变体差分】
本列 = GPT-5.4-nano (gpt54nano) 在 ctx 轨上的跟风加权签名语调票之 bank-year 求和。模型维度: gpt54nano 特指 gpt-5.4-nano, 经 OpenLux 网关路由, 是三家投票中的 OpenAI 系模型, 代表与 Google 系 (gemini31)、DeepSeek 系 (deepseekv4) 并列的第三个独立厂商信号。轨道维度: ctx 轨 content_ctx = 标题 prepend + 含目标银行句的 ±窗口上下文, 聚焦银行实体邻近语境, 相较 full 轨削弱无关段落干扰、相较 ss 轨保留更宽的语境。加权维度: 逐文章 gpt54nano_score_ctx ∈ {+1, 0, −1} × herd_weight_ctx 在银行-年上求和, 权重严格取 ctx 轨跟风衰减权重。本列为分子, 下游 gpt54nano_tone_hw_ctx 由本列除以 ctx 轨跟风权重有效样本和。本列与 gemini31、deepseekv4 的同名 ctx 列构成 ctx 轨上的跨厂商稳健性梯队。作为加权口径族的一员, 本列与等权语调、提及密度加权 (VW, gpt54nano_score_w_sum_ctx)、媒体权威加权 (MW, gpt54nano_score_mw_sum_ctx) 等分子并列物化, 各口径分子彼此正交、互不干扰, 便于面板层以统一除法框架重构任意加权均值而无需回文章级重算。本家族采用 per-model 独立降级: gpt54nano 缺席仅掉自身族列, 不牵连 gemini31 / deepseekv4, 亦非 co-primary 嵌入的 both-or-neither 连坐。缓存确定性上, stage 21 以 prompt v8 字节级冻结加 temperature=0 为确定性锚, 三轨全命中缓存时离线零字节可稳定复现本列, 保证跨运行可复现。⚠ 铁律: 本列作为 gpt54nano 单模型 × ctx 单轨稳健性并排项, 与另两模型、另两轨各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_score_hw_sum_full

【变体差分】
本列 = GPT-5.4-nano (gpt54nano) 在 full 轨上的跟风加权签名语调票之 bank-year 求和, 是本家族 OpenAI 系模型在留篇门控基准轨上的分子。模型维度: gpt-5.4-nano 经 OpenLux 路由。轨道维度: full 轨 content_full = 标题 prepend + 全文正文, 是 full-only 留篇门控 (2026-06-29) 的判定基准——报道是否计入银行-年留篇集只看 full 轨验证结果, ctx / ss 轨为其 conditional-on-full 子集。加权维度: 逐文章 gpt54nano_score_full × herd_weight_full 在银行-年上求和, full 轨权重独立构造。本列为分子, 下游 gpt54nano_tone_hw_full 由本列除以 full 轨跟风权重有效样本和。本列与 gemini31_score_hw_sum_full、deepseekv4_score_hw_sum_full 三者仅厂商不同、轨道与加权口径全同, 构成 full 轨跨厂商三角验证的核心并排组, 用以证明主语调结论不被任一单一大模型的标注习性驱动。作为加权口径族的一员, 本列与等权语调、提及密度加权 (VW, gpt54nano_score_w_sum_full)、媒体权威加权 (MW, gpt54nano_score_mw_sum_full) 等分子并列物化, 各口径分子彼此正交、互不干扰, 便于面板层统一重构加权均值。本家族采用 per-model 独立降级: gpt54nano 缺席仅掉自身族列, 不牵连另两家, 亦非 co-primary 嵌入的 both-or-neither 连坐。缓存确定性上, stage 21 以 prompt v8 字节级冻结加 temperature=0 为确定性锚, 三轨全命中缓存时离线零字节可复现, 保证 golden 跨运行可复现。⚠ 铁律: 本列作为 gpt54nano 单模型 × full 单轨稳健性并排项, 与另两模型、另两轨各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_score_hw_sum_ss

【变体差分】
本列 = GPT-5.4-nano (gpt54nano) 在 ss 轨上的跟风加权签名语调票之 bank-year 求和。模型维度: gpt-5.4-nano 经 OpenLux 路由的 OpenAI 系独立信号。轨道维度: ss 轨 content_ss = 标题 prepend + 同句内同时含"目标银行 ∧ 金科词"的句子 ±窗口片段, 是三轨中银行金科共现语义最严格者, 由 stage 14 ctx_materializer 物化 (stage 13 仅上游共现硬过滤、不物化文本列); 无同句共现时镜像 ctx 回退语义、退回全文 body 并置 ss_is_fallback=True。加权维度: 逐文章 gpt54nano_score_ss × herd_weight_ss 在银行-年上求和, 权重取 ss 轨自身跟风衰减权重, 严格逐轨不借 full 权。本列是分子, 下游 gpt54nano_tone_hw_ss 由本列除以 ss 轨跟风权重有效样本和。ss 轨在早期试跑 T=2 语料上共现稀疏、大面积回退致数值退化, 属预期而非缺陷; 生产全量语料上共现更充分。作为加权口径族的一员, 本列与等权语调、提及密度加权 (VW, gpt54nano_score_w_sum_ss)、媒体权威加权 (MW, gpt54nano_score_mw_sum_ss) 等分子并列物化, 各口径分子彼此正交、互不干扰, 便于面板层统一重构加权均值而无需回文章级重算。本家族采用 per-model 独立降级: gpt54nano 缺席仅掉自身族列, 不牵连另两家。缓存确定性上, stage 21 以 prompt v8 冻结加 temperature=0 为锚, 三轨全命中缓存时离线零字节可复现本列。⚠ 铁律: 本列作为 gpt54nano 单模型 × ss 单轨稳健性并排项, 与另两模型、另两轨各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Hansen, A. L. (2026). Validating large language model annotations. FEDS Working Paper No. No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J. (2024). GPT is an effective tool for multilingual psychological text analysis. Proceedings of the National Academy of Sciences, 121(34), e2308950121. https://doi.org/10.1073/pnas.2308950121
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. SSRN Working Paper No. No. 4412788 [Working Paper]. https://doi.org/10.2139/ssrn.4412788
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
