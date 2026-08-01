---
family_id: F172
columns:
- deepseekv4_cont_w_sum_ctx
- deepseekv4_cont_w_sum_full
- deepseekv4_cont_w_sum_ss
- gemini31_cont_w_sum_ctx
- gemini31_cont_w_sum_full
- gemini31_cont_w_sum_ss
- gpt54nano_cont_w_sum_ctx
- gpt54nano_cont_w_sum_full
- gpt54nano_cont_w_sum_ss
unit: 提及密度加权的连续语调和 (无量纲; 价值加权分子, 未归一化)
formula: "{short}_cont_w_sum{track} = Σ_articles ( {short}_cont{track} × mention_density ); 其中 {short}_cont{track} = {short}_score{track} × {short}_sentiment_confidence{track}, {short}_score ∈ {-1,0,+1} 由 verified 门控清票; short ∈ {gpt54nano, gemini31, deepseekv4}"
producer: news_process/pipeline/panel/runner.py (步骤 3b 提及密度加权列预计算) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (F 段 sum 聚合) ; news_process/pipeline/panel/encode.py::encode_sentiment ({short}_cont 构造)
upstream:
- 21_tone_llms.parquet ({short}_sentiment / {short}_sentiment_confidence / {short}_verified 三轨)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_export_main (mention_density 价值权重)
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
- doi: 10.1287/mnsc.2024.05417
  type: journal
  authors: Siano, F.
  year: 2025
  title: "The news in earnings announcement disclosures: Capturing word context using LLM methods"
  venue: Management Science
  vol: 71
  issue: 11
  pages_or_artno: 9831-9855
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
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: "Majority rules: LLM ensemble is a winning approach for content categorization"
  venue: arXiv
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
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
本家族刻画的是"单一大模型给出的连续语调, 经提及密度价值加权后, 在银行-年层面加总得到的分子量"。它是情感三角验证 (LLM/词典/BERT) 中 LLM 一支的逐模型 (per-model) 价值加权连续测度的中间产物, 由三家彼此独立的大语言模型 gpt-5.4-nano (gpt54nano)、gemini-3.1-flash-lite (gemini31) 与 deepseek-v4-flash (deepseekv4) 分别产出, 并各自在全文 (full)、实体上下文 (ctx)、银行与金科同句共现 (ss) 三条文本轨道上重复计算。构念的源头是阶段 21 (tone_llms) 对每条银行金科报道的逐模型判定: 每家模型独立返回该报道的情感方向 (正/中/负) 与一个自报置信度, 二者相乘即得文章级连续语调 {short}_cont{track}, 相比离散的三值 {short}_score, 它把"模型有多确信"这一强度信息保留下来, 使强信号报道对银行-年聚合的贡献大于模棱两可的报道。价值加权环节 (runner 步骤 3b) 再以 mention_density (目标银行在报道中的提及密度) 为权重乘入, 使"多次、密集提及目标银行"的报道获得更高权重, 呼应 Hassan et al. (2019) 以提及强度构造企业层暴露测度的价值加权范式。最后在 encode 的 F 段以 groupby-sum 把逐篇加权连续语调加总到银行-年, 得到本家族的九个 _cont_w_sum 列。它是价值加权均值 (_cont_vw / _tone_vw) 的分子, 分母为同银行-年的 Σ mention_density; 本家族只落分子和, 供下游按需归一化并做稳健性对照。

【方法学与计算】
计算链路分三步严格衔接。第一步 (阶段 21): 各模型对三轨文本分别请求, 经 verified 门控清票——某模型对某报道判定为"非真银行金科报道"或返回无效时, 该模型该篇的 score 与 cont 置为缺失 (NA), 不参与加总, 从而使分子只累积该模型自身确认为有效的报道。第二步 (runner 3b): 对存在 mention_density 的样本, 逐篇计算 {short}_cont_w{track} = {short}_cont{track} × mention_density, 缺失权重按 0 填充。第三步 (encode F 段): 以银行-年为组做 sum 聚合得 {short}_cont_w_sum{track}, 零报道银行-年为空集求和恒为 0, 与 sum_mention_density 等兄弟列口径一致。留篇门控采 full-only 口径 (2026-06-29): 一篇报道是否计入"银行金科报道"宇宙只看 full 轨 verified, ctx 与 ss 轨降为 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的加权连续和仍逐轨独立累计。ss 轨语义镜像 ctx: 报道无银行与金科同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True。三家模型互为稳健性、不分主次, 各自 just-identified 并排; 三轨同理。铁律: 三家模型、三条轨道各自独立进入并排规格, 严禁把不同模型或不同轨道的加权连续和混进同一 over-identified 的 Hansen J 检验, 否则会把跨厂商测量差异与跨轨文本差异误当作过度识别约束。逐模型独立降级: 某家模型 (如 deepseekv4) 整体缺席时只掉该模型自身族, 不牵连另两家 (区别于 co-primary 嵌入的 both-or-neither)。

【文献定位】
本家族站在"用大模型做金融文本情感标注"的方法学脉络上。de Kok (2025) 在 Management Science 系统论证了生成式大模型做文本分析时 temperature=0、prompt 冻结、缓存复现的规范范式, 正是本项目阶段 21 确定性锚点的方法依据; Siano (2025) 同刊证明大模型能捕捉传统词典忽略的词语上下文, 支持以 LLM 连续语调补充词典法。Frankel, Jennings & Lee (2022) 比较机器学习与词典法情感, 为把 LLM 一支与词典、BERT 并列作三角验证提供计量对照基础。Carlson & Burbano (2026) 在 Strategic Management Journal 给出用 LLM 标注管理学数据的操作指南与风险警示, 直接支撑逐模型并排、交叉验证而非单模型独裁的设计。多模型多数投票与集成的稳健性由 Kamen & Kamen (2025) 的内容分类集成研究佐证。价值加权环节以 Hassan et al. (2019) 的提及强度暴露测度为范式源头, 而以媒体语调聚合影响资产定价的经典证据则见 Tetlock (2007)。中文金融场景的逐实体细粒度 LLM 情感可行性由 Lan et al. (2025) 提供直接支撑。这些文献共同界定了本家族的构念效度边界: 它是逐厂商、逐轨、价值加权的连续语调分子, 作互为稳健性的规格对照, 而非单一权威测度。

## VAR: deepseekv4_cont_w_sum_full

【变体差分】
本列是 deepseek-v4-flash (deepseekv4) 单一模型在 full 全文轨上的提及密度加权连续语调银行-年加总。相对家族其余八列的三处精确差分: 模型 = deepseekv4 (直连 api.deepseek.com, 与走 yunwu 网关的 gpt54nano/gemini31 是不同厂商不同端点, 供应商归属勘误见 export 注释, 原误标 Grok-4.1 已更正为 DeepSeek V4 Flash); 轨道 = full (content_full = 标题 prepend + 全文正文), 是 full-only 留篇门控的判定轨, 决定该报道是否计入银行金科报道宇宙; 权重 = mention_density 价值加权, 内容 = deepseekv4 自身 score×confidence 的连续语调, verified 门控只清 deepseekv4 自己的票。它与 gpt54nano_cont_w_sum_full、gemini31_cont_w_sum_full 三家 full 轨列互为稳健性、不分主次, 各自 just-identified 并排, 严禁三家混入同一 over-identified Hansen J; deepseekv4 整体缺席时仅本族三列降级, 不牵连另两家。作为价值加权均值的分子, 归一化需除以同银行-年 sum_mention_density。full 轨是本列相对 ctx/ss 稳健轨的首要测度轨。用大白话说, 这个数字回答的是"这家银行这一年里, 被多次提及的报道所携带的、由深度求索模型判断的语调强度, 加在一起有多大"; 因为保留的是加总而非均值, 它同时编码了报道数量、提及密度与语调强度三重信息, 直接除以提及密度总和才还原成可比的加权平均语调。之所以逐模型单独保留而不只留三家共识, 是因为不同厂商模型对中文金融语料的判读风格存在系统差异, 把深度求索这一支单列出来, 才能在稳健性检验中检验主结论是否被某一家模型的判读习惯所驱动。在实证使用上, 本列既可作分子构造加权语调进入回归, 也可作模型间一致性诊断的原始材料, 但绝不与另两家或另两轨拼进同一过度识别检验。

## VAR: deepseekv4_cont_w_sum_ctx

【变体差分】
本列在 deepseekv4 模型、mention_density 价值加权口径上与 deepseekv4_cont_w_sum_full 完全一致, 唯一差分是文本轨道 = ctx (实体上下文轨)。ctx 轨的 content_ctx = 标题 prepend + 含目标银行句的 ±窗口片段 (Hassan 2019 proximity 邻近口径), 只把目标银行出现处附近的语句喂给模型, 剔除全文中与目标银行无关的段落噪声。在 full-only 门控下, ctx 轨降为 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集, 但 deepseekv4 对 ctx 文本的逐篇连续语调仍独立请求、独立 verified 清票、独立按 mention_density 加权后逐轨累加, 不借用 full 轨的分子或分母。它与同模型的 full/ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。与另两家模型的 ctx 轨列 (gpt54nano/gemini31) 同为逐厂商并排稳健测度。早期试跑 T=2 短面板上 ctx 轨可能因样本稀薄退化, 属预期现象, 生产期 T=19 恢复正常。归一化除以同银行-年 sum_mention_density。用大白话说, 本列把每篇报道里"目标银行出现的那句话及其前后窗口"单独抽出来交给深度求索模型判读, 再按提及密度加权加总, 因此它比全文轨更贴近"报道究竟怎么评价这家银行", 而少受全文里无关段落的干扰。它与全文轨的差别正是稳健性证据的来源: 若把上下文噪声剔除后结论依旧, 说明主效应并非全文里旁枝末节的语调所拼凑。因此本列在稳健性表里与同模型全文轨、同句轨并排出现, 各自跑一遍主回归, 三轨结论一致才算稳。它绝不与另两轨或另两家模型拼进同一过度识别的 Hansen J。

## VAR: deepseekv4_cont_w_sum_ss

【变体差分】
本列在 deepseekv4 模型、mention_density 价值加权口径上与家族同模型两列一致, 差分是文本轨道 = ss (银行与金科同句共现轨)。ss 轨的 content_ss = 标题 prepend + 同一句内同时含目标银行与金科词的句 ±窗口, 是三轨中信息最聚焦、最严格的口径, 专门捕捉"银行做金科"这一构念的同句共现语义。回退语义镜像 ctx: 当报道不存在银行与金科同句共现时, content_ss 优雅回退为全文正文并置 ss_is_fallback=True, 与 ctx 的 content_full 回退同构, 共享 n_articles 分母口径。在 full-only 门控下 ss 同为 conditional-on-full 稳健轨, deepseekv4 对 ss 文本逐篇独立请求、独立 verified 清票、独立按提及密度加权累加。它与同模型 full/ctx 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。与 gpt54nano/gemini31 的 ss 轨列同为逐厂商并排。因同句共现约束严苛, 早期试跑期短面板上 ss 轨常大幅回退或退化, 生产期方显区分度。归一化除以同银行-年 sum_mention_density。用大白话说, 本列只认"同一句话里既提到这家银行又提到金融科技词"的那种报道, 是三条轨道里门槛最高、最贴近本项目核心构念的一档: 它衡量的不是泛泛的银行语调, 而是专门针对"这家银行做金融科技"这件事、由深度求索模型判读的语调。正因为门槛高, 很多报道不满足同句共现而回退到全文, 所以本列在小样本上常与全文轨趋同; 但在生产期大语料上, 它能把"银行涉足金科"这一窄构念的语调与银行的一般性报道语调区分开, 从而作为最保守的一档稳健性对照, 检验主结论是否真由银行金科构念而非泛泛的媒体情绪所驱动。

## VAR: gemini31_cont_w_sum_full

【变体差分】
本列是 gemini-3.1-flash-lite (gemini31) 单一模型在 full 全文轨上的提及密度加权连续语调银行-年加总。差分三处: 模型 = gemini31 (经 yunwu 网关调用, 与直连 deepseek 的 deepseekv4、同走 yunwu 的 gpt54nano 并列为交叉厂商三角验证的一支); 轨道 = full (标题 prepend + 全文, full-only 留篇门控判定轨); 权重 = mention_density 价值加权, 内容 = gemini31 自身 score×confidence 连续语调, verified 门控只清 gemini31 自己的票。它与 deepseekv4_cont_w_sum_full、gpt54nano_cont_w_sum_full 三家互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; gemini31 缺席仅本族三列降级。相较三家均值集成 (llm_models_avg) 或多数投票共识 (llm_vote), 本列是逐厂商 co-equal 稳健测度, 用以证明主结论不由单一厂商模型驱动。作为价值加权均值分子, 归一化除以 sum_mention_density; full 轨为其相对 ctx/ss 的首要测度轨。用大白话说, 本列衡量的是"这家银行这一年里, 被密集提及的报道所携带的、由谷歌 Gemini 模型判断的语调强度加总量", 因保留加总而非均值, 它同时编码报道数量、提及密度与语调强度三重信息。之所以把 Gemini 这一支单列, 是因为它与直连的深度求索、同走网关的 gpt 模型出自不同厂商、训练语料与对齐方式各异, 对同一篇中文金融报道的语调判读可能系统性偏乐观或偏审慎; 单列出来才能检验主结论是否被某一家模型的判读偏好放大。在实证使用上, 本列与另两家全文轨列并排各跑一遍主回归, 系数方向与显著性一致方证跨厂商稳健, 但三家绝不拼进同一过度识别检验。

## VAR: gemini31_cont_w_sum_ctx

【变体差分】
本列在 gemini31 模型、价值加权口径上与 gemini31_cont_w_sum_full 一致, 差分为文本轨道 = ctx 实体上下文轨。content_ctx = 标题 prepend + 目标银行句 ±窗口, 依 Hassan (2019) 邻近口径只保留目标银行邻近语句, 抑制全文无关段落噪声。full-only 门控下 ctx 为 conditional-on-full 稳健轨, 行宇宙是 full 留篇子集, gemini31 对 ctx 文本独立请求、独立 verified 清票、独立按 mention_density 加权后逐轨累加, 不借 full 轨分子分母。它与同模型 full/ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与另两家模型 ctx 轨列同为逐厂商并排稳健测度。gemini31 独立降级不牵连 deepseekv4/gpt54nano。早期试跑期短面板 ctx 轨可能退化属预期。归一化除以同银行-年 sum_mention_density。本列价值在于同时切换厂商 (gemini31) 与轨道 (ctx) 两维, 与 full 轨、其余两家共同构成规格稳健性网格。用大白话说, 本列把每篇报道里目标银行出现处附近的语句抽出来单独交给谷歌 Gemini 模型判读, 再按提及密度加权加总, 因此它比全文轨更聚焦于"报道怎么评价这家银行", 少受全文无关段落干扰。它与同模型全文轨的差异, 正是检验"上下文噪声是否驱动结论"的稳健性证据: 剔除无关段落后结论不变, 说明主效应并非旁枝末节的语调所拼凑。早期试跑期短面板上样本稀薄可能使 ctx 轨退化, 属预期, 生产期大语料方显区分度。它绝不与另两轨或另两家模型拼进同一过度识别的 Hansen J。

## VAR: gemini31_cont_w_sum_ss

【变体差分】
本列在 gemini31 模型、价值加权口径上与家族同模型两列一致, 差分为文本轨道 = ss 银行金科同句共现轨。content_ss = 标题 prepend + 银行与金科同句 ±窗口, 是三轨中最聚焦的口径, 捕捉银行涉足金科的同句共现语义; 无共现时优雅回退全文正文并置 ss_is_fallback=True, 回退语义镜像 ctx, 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 稳健轨, gemini31 对 ss 文本独立请求、独立 verified 清票、独立按提及密度加权累加。它与同模型 full/ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与 deepseekv4/gpt54nano 的 ss 列同为逐厂商并排。gemini31 缺席仅本族降级。因同句共现约束严苛, 早期试跑期短面板上 ss 轨常回退或退化, 生产期方显区分度。归一化除以同银行-年 sum_mention_density。本列同时以最严文本轨道与 gemini31 厂商切换, 为主结论提供最保守的规格对照。用大白话说, 本列只认"同一句话里既提到这家银行又提到金融科技词"的报道, 是三条轨道里门槛最高的一档, 衡量的不是泛泛的银行语调, 而是专门针对"这家银行做金融科技"这件事、由谷歌 Gemini 模型判读的语调。门槛高使许多报道回退全文, 故小样本上常与全文轨趋同; 生产期大语料上它能把银行金科窄构念的语调与一般性报道语调区分开, 作为最保守的稳健性对照, 检验主结论是否真由银行金科构念驱动。它与另两家的同句轨、同模型的另两轨并排各自跑主回归, 结论一致方证稳健, 绝不拼进同一过度识别检验。

## VAR: gpt54nano_cont_w_sum_full

【变体差分】
本列是 gpt-5.4-nano (gpt54nano) 单一模型在 full 全文轨上的提及密度加权连续语调银行-年加总。差分三处: 模型 = gpt54nano (经 yunwu 网关调用); 轨道 = full (标题 prepend + 全文, full-only 留篇门控判定轨); 权重 = mention_density 价值加权, 内容 = gpt54nano 自身 score×confidence 连续语调, verified 门控只清 gpt54nano 自己的票。它与 deepseekv4_cont_w_sum_full、gemini31_cont_w_sum_full 三家互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; gpt54nano 缺席仅本族三列降级, 不牵连另两家。相较三家均值集成与多数投票共识, 本列是逐厂商 co-equal 稳健测度, 用以佐证主结论不依赖单一厂商模型。作为价值加权均值分子, 归一化除以同银行-年 sum_mention_density; full 轨为其相对 ctx/ss 稳健轨的首要测度轨。gpt54nano 与另两家采同一冻结 prompt v8、同一 temperature=0 确定性口径, 保证跨厂商差异只来自模型本身而非请求设置。用大白话说, 本列衡量"这家银行这一年里被密集提及的报道所携带的、由 GPT 模型判断的语调强度加总量", 加总而非均值使其同时编码报道数量、提及密度与语调强度。之所以把 GPT 这一支单列, 是因为三家模型出自不同厂商, 对同一篇中文金融报道可能系统性偏乐观或偏审慎; 单列才能检验主结论是否被某家模型的判读偏好放大。因三家共用同一冻结提示词与零温度, 命中缓存即可离线零成本逐字节复现, 跨厂商差异被干净地隔离为模型本身之别。本列与另两家全文轨并排各跑主回归, 系数一致方证稳健, 三家绝不拼进同一过度识别检验。

## VAR: gpt54nano_cont_w_sum_ctx

【变体差分】
本列在 gpt54nano 模型、价值加权口径上与 gpt54nano_cont_w_sum_full 一致, 差分为文本轨道 = ctx 实体上下文轨。content_ctx = 标题 prepend + 目标银行句 ±窗口 (Hassan 2019 邻近口径), 只保留目标银行邻近语句以抑制全文无关噪声。full-only 门控下 ctx 为 conditional-on-full 稳健轨, 行宇宙是 full 留篇子集, gpt54nano 对 ctx 文本独立请求、独立 verified 清票、独立按 mention_density 加权后逐轨累加, 不借 full 轨分子分母。它与同模型 full/ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与另两家模型 ctx 轨列同为逐厂商并排稳健测度。gpt54nano 独立降级不牵连 deepseekv4/gemini31。早期试跑期短面板 ctx 轨可能退化属预期, 生产期 T=19 恢复。归一化除以同银行-年 sum_mention_density。本列同时切换厂商 (gpt54nano) 与轨道 (ctx), 与其余八列共同织成模型×轨道的规格稳健性网格。用大白话说, 本列把每篇报道里目标银行出现处附近的语句单独交给 GPT 模型判读, 再按提及密度加权加总, 因此比全文轨更聚焦于"报道怎么评价这家银行", 少受全文无关段落干扰。它与同模型全文轨的差异, 正是检验上下文噪声是否驱动结论的稳健性证据: 剔除无关段落后结论不变, 说明主效应并非旁枝末节的语调所拼凑。早期试跑期短面板样本稀薄可能使 ctx 轨退化, 属预期, 生产期大语料方显区分度。它绝不与另两轨或另两家模型拼进同一过度识别的 Hansen J。

## VAR: gpt54nano_cont_w_sum_ss

【变体差分】
本列在 gpt54nano 模型、价值加权口径上与家族同模型两列一致, 差分为文本轨道 = ss 银行金科同句共现轨。content_ss = 标题 prepend + 银行与金科同句 ±窗口, 是三轨中最严格聚焦的口径, 专捕银行涉足金科的同句共现语义; 无共现时优雅回退全文正文并置 ss_is_fallback=True, 回退语义镜像 ctx, 共享 n_articles 分母口径。full-only 门控下 ss 为 conditional-on-full 稳健轨, gpt54nano 对 ss 文本独立请求、独立 verified 清票、独立按提及密度加权累加。它与同模型 full/ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与 deepseekv4/gemini31 的 ss 列同为逐厂商并排。gpt54nano 缺席仅本族降级。因同句共现约束严苛, 早期试跑期短面板 ss 轨常大幅回退或退化, 生产期方显区分度。归一化除以同银行-年 sum_mention_density。本列以最严文本轨道叠加 gpt54nano 厂商切换, 为主结论提供最保守的一档规格对照。用大白话说, 本列只认"同一句话里既提到这家银行又提到金融科技词"的报道, 是三条轨道里门槛最高的一档, 衡量的不是泛泛的银行语调, 而是专门针对"这家银行做金融科技"这件事、由 GPT 模型判读的语调。门槛高使许多报道回退全文, 故小样本上常与全文轨趋同; 生产期大语料上它能把银行金科窄构念的语调与一般性报道语调区分开, 作为最保守的稳健性对照, 检验主结论是否真由银行金科构念驱动。它与另两家的同句轨、同模型的另两轨并排各自跑主回归, 结论一致方证稳健, 绝不拼进同一过度识别检验。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
