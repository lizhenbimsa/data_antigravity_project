---
family_id: F179
columns:
- deepseekv4_score_w_sum_ctx
- deepseekv4_score_w_sum_full
- deepseekv4_score_w_sum_ss
- gemini31_score_w_sum_ctx
- gemini31_score_w_sum_full
- gemini31_score_w_sum_ss
- gpt54nano_score_w_sum_ctx
- gpt54nano_score_w_sum_full
- gpt54nano_score_w_sum_ss
unit: 无量纲 value-weighted 语调分子和 (每篇离散语调分 ∈ {-1,0,+1} 乘提及密度权重后在 bank-year 内求和)
formula: "{short}_score_w_sum{track} = Σ_{篇 ∈ bank-year} {short}_score{track} × mention_density; {short}_score ∈ {-1,0,+1} 为单一 LLM 模型该轨判定; 下游 {short}_tone_vw{track} = {short}_score_w_sum{track} / _llm_denom('vw', short, track) (per-model LLM 走 valid-mask 加权分母 _wd_*, 向零衰减修复; 非裸 sum_mention_density —— 后者仅用于词典/BERT 列)"
producer: news_process/pipeline/panel/runner.py (步骤 3b VW 加权列预计算) ; news_process/pipeline/panel/encode.py (bank-year 'sum' 聚合)
upstream:
- 21_tone_llms.parquet (三家 LLM 逐篇三轨 {short}_score{track})
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss + mention_density 源)
citations:
- doi: 10.1146/annurev-economics-120925-105620
  type: journal
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2026
  title: "Large language models: An applied econometric framework"
  venue: Annual Review of Economics
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
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
- doi: "10.1111/1911-3846.12832"
  title: "FinBERT: A Large Language Model for Extracting Information from Financial Text"
  authors: "Huang, A. H., Wang, H., & Yang, Y."
  year: 2023
  venue: "Contemporary Accounting Research"
  type: "journal"
- doi: "10.1016/j.frl.2024.105227"
  title: "Sentiment trading with large language models"
  authors: "Kirtac, K., & Germano, G."
  year: 2024
  venue: "Finance Research Letters"
  type: "journal"
new_dois:
  - "10.1111/1911-3846.12832"
  - "10.1016/j.frl.2024.105227"
---

## CORE

【构念与来源】
本家族刻画的是「单一大语言模型 (LLM) 逐篇语调判定, 经提及密度加权后在 bank-year 内求得的价值加权分子和」。它是流水线情感三角验证体系里 LLM 一脉的 per-model 中间聚合量: 每一列锁定三家投票模型中的某一家 (gpt54nano = GPT-5.4-nano、gemini31 = Gemini-3.1-flash-lite、deepseekv4 = DeepSeek-V4-Flash) 在某一文本轨 (full/ctx/ss) 上的判定, 把该家对一家银行当年每篇相关报道给出的离散语调分 (取值为负面 −1、中性 0、正面 +1) 乘以该篇的提及密度权重, 再在 bank-year 单元内累加。它不是最终测度, 而是价值加权语调 (下游 {short}_tone_vw) 的分子: 该分子除以同一 bank-year 内的加权分母即得以曝光强度为权的加权平均语调。须精确区分分母口径: per-model LLM 列的 {short}_tone_vw 走 valid-mask 加权分母 (encode 内 _llm_denom 的 'vw' 支路取 _wd_* 权重和, 即向零衰减修复后只累加该模型自身判定有效篇的提及密度权重), 而非裸的全篇提及密度权重之和 sum_mention_density —— 后者仅用于词典轨与 BERT 轨的对应归一列。把分子单独物化为面板列, 目的在于让研究者可以自选分母 (物理篇数、valid-mask 篇数或权重和), 并在稳健性表中直接检视加权前的累积极性, 而不被归一化掩盖。

【方法学与计算】
计算链路分两级。文章级: 阶段 21 tone_llms 对每篇报道以全文 (_full)、实体上下文窗 (_ctx)、银行与金融科技同句共现窗 (_ss) 三种输入分别请求三家模型, 每家独立返回真伪精筛与情感判定, 落为逐篇逐轨的 {short}_score{track} ∈ {−1,0,+1}。随后在面板 runner 步骤 3b, 以每篇的 mention_density (目标银行提及密度, 曝光强度代理) 为权 w, 逐篇构造加权列 {short}_score_w{track} = {short}_score{track} × w。银行-年级: encode 阶段对该加权列按 bank-year 做 'sum' 聚合, 得 {short}_score_w_sum{track}。零新闻的 bank-year 单元按「空集求和 = 0」契约填 0 而非缺失, 与 sum_mention_density 等兄弟权重和列口径一致。提及密度加权借鉴 Hassan et al. (2019) 的公司层暴露测量思想: 一篇高强度提及目标主体的报道, 对该主体当年舆论基调的贡献应大于一带而过的提及, 因此以提及密度而非等权累加更贴合曝光的经济学含义。三家模型的逐篇判定共用同一冻结 Prompt (v8 字节级冻结)、temperature=0 确定性推理与统一缓存键, 确保可复现 (de Kok, 2025 所倡导的 temperature=0 / prompt 冻结 / 缓存范式)。留篇门控采用 full-only 口径: 一篇是否算作「银行金融科技报道」只由 full 轨 verified 判定, ctx/ss 降为 conditional-on-full 的稳健性轨, per-model 各列在此留篇宇宙内各自计算。

【文献定位】
本家族坐落在「以大模型做金融文本标注」这一近年迅速成熟的方法脉络上。Gilardi et al. (2023) 在 PNAS 上证明零样本 ChatGPT 在多项文本标注任务上的准确率与一致性可超过众包标注者, 为以 LLM 替代人工情感标注提供了效度背书; de Kok (2025) 在 Management Science 上系统梳理了在会计与金融研究中稳健使用生成式 LLM 的工程规范 (确定性温度、提示冻结、结果缓存), 正是本流水线 per-model 判定可复现性的方法论依据。Ludwig, Mullainathan, & Rambachan (2026) 在 Annual Review of Economics 上提出把 LLM 输出视作带测量误差的生成变量并纳入计量框架, 呼应了本家族「保留 per-model 分子、显式暴露测量异质性」的设计取向。与词典法、监督式 BERT 并置, LLM 一脉构成 Frankel, Jennings, & Lee (2022) 所论「机器学习 vs 词典法」情感测量的第三角: 本项目刻意保留三家模型各自的 per-model 子测度, 使 gpt54nano / gemini31 / deepseekv4 互为跨厂商稳健性, 不分主次。价值加权的经济学基础见 Hassan et al. (2019) 的暴露测量与 Tetlock (2007) 关于媒体语调对市场影响的经典证据; 中文金融文本的领域特异性则由 Du et al. (2022) 在 Review of Finance 上论证, 提示中文语料的情感判定须对领域词与政治语境敏感, 这也是本项目在词典轨之外并置多家 LLM 的原因之一。铁律: 三家 per-model 子测度、三条文本轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把它们混进同一 over-identified 的 Hansen J 检验 (跨模型联合识别会伪造过度识别自由度)。真正的跨模型族级 FWER 校正走根级 rwolf 模板, 而非在结构方程里堆叠工具。Huang, Wang, & Yang (2023, Contemporary Accounting Research) 提出面向金融文本的领域适配大模型 FinBERT, 为本家族多 LLM 并置判定语调的方法论提供金融文本大模型基准参照; Kirtac & Germano (2024, Finance Research Letters) 系统比较多种大语言模型与词典法在近百万篇金融新闻上的情感判定与交易表现, 支持本家族以多家 LLM 互为稳健性并置构念的正当性。

## VAR: deepseekv4_score_w_sum_ctx

【变体差分】
本列锁定 DeepSeek-V4-Flash (直连 api.deepseek.com, 与走 OpenLux 路由的另两家在网络端点与厂商上均不同源) 在实体上下文轨 (_ctx) 上的价值加权语调分子和。ctx 轨输入为「标题 prepend + 含目标银行句的 ±窗口片段」, 即 Hassan et al. (2019) 意义下的邻近上下文: 相较 full 轨, 它剔除了与目标银行无关的远端正文, 使语调判定聚焦于银行被直接谈及的语境, 从而降低远端无关段落引入的判定噪声。该列在 full-only 留篇门控下计算: 行宇宙为 full 轨 verified 留篇集, ctx 轨判定被降为 conditional-on-full 的稳健性测度, per-column 照算但不参与「是否算一篇报道」的门控。它与本家族 full/ss 两轨、与 gemini31/gpt54nano 两家的对应 ctx 列互为稳健性、各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。差分维度可概括为: 模型 = DeepSeek 一家 (第一家跨厂商视角), 轨道 = ctx (中等严格语境), 门控 = conditional-on-full。分子语义: 逐篇 DeepSeek 判定 ∈ {−1,0,+1} 乘该篇提及密度权重后在 bank-year 内求和; 零新闻单元按空集求和契约填 0; 下游除以 valid-mask 加权分母 (_llm_denom 的 'vw' 支路取 _wd_* 权重和, 非裸 sum_mention_density) 即得价值加权平均语调 deepseekv4_tone_vw_ctx, 分子单列的价值在于允许研究者自选分母并检视归一化前的累积极性。使用提示: 本列是 per-model 稳健性存档量而非主报告测度, 主报告以三家多数投票的共识语调为 headline; 在稳健性表中把三家 ctx 分子并列, 可直观展示 DeepSeek 一家在中等语境轨上的判定是否与共识及另两家系统性偏离, 从而回应「结论是否由某一厂商模型驱动」的审稿质疑。该列与词典轨、监督式 BERT 轨的同构念测度并置时, 亦须遵守各自 just-identified 并排、不混入同一 over-identified Hansen J 的口径。

## VAR: deepseekv4_score_w_sum_full

【变体差分】
本列为 DeepSeek-V4-Flash 在全文轨 (_full) 上的价值加权语调分子和。full 轨输入为「标题 prepend + 全文正文」, 是留篇门控的判定轨 (full-only 口径, 2026-06-29): 一篇是否算作银行金融科技报道只看 full 轨 verified 判定, 因此 full 轨的 per-model 分子直接对应留篇宇宙本身, 而非其子集, 这是它与同家族 ctx/ss 两轨在行宇宙上的根本差别。相较 ctx/ss, full 保留完整正文语境, 覆盖面最广, 但代价是可能纳入与目标银行关系较弱的段落, 使加权极性对篇内主题漂移更敏感; 三轨并置正是为了让研究者观察语境宽窄对结论的影响。差分维度: 模型 = DeepSeek 一家, 轨道 = full (最宽语境、门控判定轨), 权重 = 提及密度。该列与 deepseekv4 的 ctx/ss 两轨、与 gemini31/gpt54nano 的 full 列共同构成跨模型 × 跨轨稳健性矩阵, 各自 just-identified、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; 跨模型的族级多重检验校正另由根级 rwolf 模板承担。计算同家族链路: 阶段 21 逐篇 DeepSeek 判定 × mention_density 生成 deepseekv4_score_w_full, 再于 encode 阶段按 bank-year 做 'sum' 聚合; 零新闻单元填 0 而非缺失, 与 sum_mention_density 等兄弟权重和列口径一致。使用提示: 因 full 轨既是门控判定轨又是覆盖最广的语境轨, 本列通常是三轨中方差最充分、最适合作跨模型对照基准的一列; 研究者若要比较 DeepSeek 与 Gemini、GPT 的判定倾向, 优先在 full 轨上对齐, 再以 ctx/ss 作语境窄化的稳健性验证。须强调本列是价值加权分子而非归一化语调, 直接跨 bank-year 比较其绝对水平会混入曝光强度差异, 正确用法是配合 sum_mention_density 或 valid-mask 分母归一后再作横向比较。

## VAR: deepseekv4_score_w_sum_ss

【变体差分】
本列为 DeepSeek-V4-Flash 在银行与金融科技同句共现轨 (_ss) 上的价值加权语调分子和。ss 轨输入为「标题 prepend + 同句内同时含目标银行∧金融科技词的句 ±窗口」, 是三轨中语境最严的一轨, 只在银行与金科被直接并置陈述时才取该句语境作判定, 因而衡量的是「银行数字化 / 金融科技叙事」这一特定语义子空间里 DeepSeek 给出的加权极性。回退语义须特别注意: 当某篇无银行∧金科同句共现时, ss 镜像 ctx 的回退逻辑, content_ss 退回全文正文并置 ss_is_fallback=True (与 ctx/full 共享 n_articles 分母), 而当 FINTECH_AC 为空时整批 *_is_fallback 全置 True 优雅降级, 绝不静默清空。差分维度: 模型 = DeepSeek 一家, 轨道 = ss (最严同句共现语境 + 回退), 门控 = conditional-on-full。因语境最严, 该列在早期试跑期短面板 (T=2) 上可能因共现稀疏而近零方差, 属预期退化, 生产期 T=19 语料充足后恢复正常方差。它与 deepseekv4 的 full/ctx 两轨、与另两家 ss 列互为稳健性、各自 just-identified 并排, 禁混同一 over-identified Hansen J。分子构造同家族: 逐篇 ss 判定 ∈ {−1,0,+1} × mention_density 于 bank-year 'sum' 聚合, 下游除以 valid-mask 加权分母 (_wd_* 权重和, per-model LLM 专用, 非裸 sum_mention_density) 得 deepseekv4_tone_vw_ss。使用提示: ss 轨的价值在于把语义锁定在银行与金融科技被同句并置的陈述上, 因此本列比 full/ctx 更能捕捉「针对银行数字化举措本身」的舆论极性, 适合作构念效度的窄化稳健性检验; 但因回退机制的存在, 当共现稀疏时相当比例的 bank-year 实际退回全文语境, 使用者解读时须结合 ss_is_fallback 占比判断该轨在特定样本上的有效锐度, 避免把回退主导的结果误读为同句共现信号。

## VAR: gemini31_score_w_sum_ctx

【变体差分】
本列锁定 Gemini-3.1-flash-lite (经 OpenLux 路由) 在实体上下文轨 (_ctx) 上的价值加权语调分子和。与同家族 deepseekv4/gpt54nano 的 ctx 列相比, 唯一差分在于判定模型是 Google 系的 Gemini 一家, 用以提供独立于 DeepSeek 与 GPT 的第三方厂商视角: 三家模型对同一批 ctx 片段各自给出 ∈ {−1,0,+1} 判定, 列间差异纯粹反映模型间标注异质性 (不同预训练语料、对齐策略与中文金融语义把握的差别), 而非语料或轨道差异, 这正是跨厂商三角验证的设计初衷。ctx 轨输入为标题 prepend + 目标银行句 ±窗口, 在 full-only 留篇门控下作 conditional-on-full 稳健性轨计算, 行宇宙为 full 轨 verified 留篇集。差分维度: 模型 = Gemini 一家, 轨道 = ctx, 门控 = conditional-on-full。该列与 gemini31 的 full/ss 两轨、与另两家同轨列并排为跨模型稳健性, 各自 just-identified、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。分子: 逐篇 Gemini 判定 × mention_density 于 bank-year 'sum' 聚合, 零新闻单元填 0; 下游归一为价值加权平均语调 gemini31_tone_vw_ctx, 模型间一致性另由 Krippendorff α / Cohen κ 评估而非在本分子列上直接比较水平。使用提示: Gemini 作为 Google 系模型, 其对齐策略与中文金融语义把握与 OpenAI 系 GPT、DeepSeek 系模型存在系统差异, 因此本列在跨模型稳健性表中承担独立的第三方厂商锚点作用; 若三家 ctx 分子归一后语调方向一致, 则跨厂商三角验证成立, 主结论的模型稳健性得到支撑, 反之则须在稳健性叙事中披露分歧来源。本列不进入任何以另两家为工具的联合结构方程。

## VAR: gemini31_score_w_sum_full

【变体差分】
本列为 Gemini-3.1-flash-lite 在全文轨 (_full) 上的价值加权语调分子和, 是 Gemini 一家在留篇判定轨上的累积加权极性。full 轨为 full-only 门控的判定轨, 故该列对应完整留篇宇宙而非子集, 这是它与 gemini31 的 ctx/ss 两轨在行宇宙上的本质区别。相较 ctx/ss, full 纳入完整正文语境, 覆盖最广。差分维度: 模型 = Gemini 一家, 轨道 = full (门控判定轨), 权重 = 提及密度。该列与 gemini31 的 ctx/ss 两轨、与 deepseekv4/gpt54nano 的 full 列共同构成跨模型 × 跨轨稳健性矩阵。设置三家模型 per-model 并排 (而不仅报共识投票结果) 的用意, 是让主结论不被任一厂商的标注习惯驱动, 呼应 Gilardi et al. (2023) 关于 LLM 标注效度可比甚至优于众包的证据、de Kok (2025) 关于生成式 LLM 在会计金融研究中稳健使用规范的梳理, 以及 Ludwig et al. (2026) 把 LLM 输出视作带测量误差生成变量的计量框架; 一致性由跨模型 Krippendorff α / Cohen κ 另行评估, 而非在本分子列上直接比较水平。铁律: 各家 / 各轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。计算: 逐篇 Gemini 判定 × mention_density 于 bank-year 求和, 零新闻单元填 0。使用提示: full 轨 Gemini 分子是跨模型对照中方差最充分的 Gemini 列, 优先在此与另两家 full 分子对齐比较判定倾向; 因是价值加权分子, 跨 bank-year 直接比绝对水平会混入曝光强度差异, 须配合分母归一后再横向比较, 且解读时应记住它衡量的是留篇宇宙全集而非任何子集。

## VAR: gemini31_score_w_sum_ss

【变体差分】
本列为 Gemini-3.1-flash-lite 在银行∧金融科技同句共现轨 (_ss) 上的价值加权语调分子和。ss 为最严语境轨: 仅取同句同时含目标银行与金科词的句 ±窗口作输入; 无共现时镜像 ctx 的回退语义, content_ss 退回全文正文并置 ss_is_fallback=True (共享 n_articles 分母), FINTECH_AC 为空时整批优雅降级。因此该列衡量的是「银行与金融科技被直接同句并置陈述时」Gemini 给出的加权极性, 语义比 full/ctx 更锐利、更贴近银行数字化叙事这一子空间, 但可用样本更薄。差分维度: 模型 = Gemini 一家, 轨道 = ss (最严同句共现 + 回退), 门控 = conditional-on-full。早期试跑 T=2 上因共现稀疏可能近零方差 (预期退化, 生产 T=19 恢复), 使用者在短面板稳健性表中应对此有预期而不误判为缺陷。它与 gemini31 的 full/ctx 两轨、与另两家 ss 列互为稳健性、各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。分子构造同家族链路: 逐篇 ss 判定 ∈ {−1,0,+1} × mention_density 于 bank-year 'sum' 聚合, 下游除以 valid-mask 加权分母 (_wd_* 权重和, per-model LLM 专用, 非裸 sum_mention_density) 得 gemini31_tone_vw_ss。使用提示: 本列把 Gemini 的判定锁定在银行与金融科技同句并置的最锐语境上, 适合作构念效度窄化检验的第三方厂商锚点; 但须结合 ss_is_fallback 占比判断该轨在具体样本上有多少 bank-year 实际退回全文语境, 以免把回退主导的结果误读为同句共现的纯净信号, 短面板上尤须审慎。

## VAR: gpt54nano_score_w_sum_ctx

【变体差分】
本列锁定 GPT-5.4-nano (经 OpenLux 路由) 在实体上下文轨 (_ctx) 上的价值加权语调分子和。差分在于判定模型为 OpenAI 系的 GPT-5.4-nano, 提供区别于 DeepSeek 与 Gemini 的第三家跨厂商稳健性视角: 三家在同一批 ctx 片段上各自独立标注 ∈ {−1,0,+1}, 列间差异纯为模型间标注异质性。ctx 轨输入为标题 prepend + 目标银行句 ±窗口 (Hassan 2019 式邻近上下文), 剔除远端无关正文使判定聚焦银行语境; 在 full-only 门控下作 conditional-on-full 稳健性轨计算, 行宇宙为 full 轨 verified 留篇集。差分维度: 模型 = GPT 一家, 轨道 = ctx, 门控 = conditional-on-full。该列与 gpt54nano 的 full/ss 两轨、与 deepseekv4/gemini31 的 ctx 列并排为跨模型稳健性矩阵。铁律: 各家 / 各轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 真正的跨模型族级多重检验校正走根级 rwolf 模板, 不在结构方程内堆叠工具以伪造过度识别自由度。分子: 逐篇 GPT 判定 × mention_density 于 bank-year 'sum' 聚合, 零新闻单元填 0, 下游归一为 gpt54nano_tone_vw_ctx。使用提示: GPT-5.4-nano 作为 OpenAI 系模型, 在跨模型稳健性表中与 DeepSeek、Gemini 并列构成三方厂商锚点; 本列是 per-model 稳健性存档量而非主报告 headline, 主报告以三家共识投票语调为准, 本列的作用是让审稿人直观检视 GPT 一家在中等语境轨上的判定是否与共识及另两家系统偏离, 从而支撑或质疑结论的模型稳健性。

## VAR: gpt54nano_score_w_sum_full

【变体差分】
本列为 GPT-5.4-nano 在全文轨 (_full) 上的价值加权语调分子和, 是 GPT 一家在留篇判定轨上的累积加权极性。full 轨为 full-only 门控判定轨, 该列对应完整留篇宇宙而非子集, 这是它与 gpt54nano 的 ctx/ss 两轨在行宇宙上的本质差别。相较 ctx/ss, full 覆盖完整正文语境, 覆盖面最广但对篇内主题漂移更敏感。差分维度: 模型 = GPT 一家, 轨道 = full (门控判定轨), 权重 = 提及密度。该列与 gpt54nano 的 ctx/ss 两轨、与 deepseekv4/gemini31 的 full 列共同构成跨模型 × 跨轨稳健性矩阵。设置三家 per-model 并排 (而非仅报共识投票) 意在证明主结论不被任一厂商标注习惯驱动, 呼应 Gilardi et al. (2023) 与 de Kok (2025) 关于 LLM 标注效度与可复现规范的方法论共识, 以及 Ludwig et al. (2026) 把 LLM 输出作带测量误差生成变量的框架; 中文金融语料的领域特异性 (Du et al., 2022) 进一步说明并置多家 LLM 交叉验证的必要。铁律: 各家各轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。计算: 逐篇 GPT 判定 × mention_density 于 bank-year 求和, 零新闻单元按空集求和契约填 0。使用提示: full 轨 GPT 分子是三轨中方差最充分的 GPT 列, 最适合作跨模型对照的对齐基准; 因是价值加权分子而非归一化语调, 跨 bank-year 直接比绝对水平会混入曝光强度差异, 正确用法是配合 sum_mention_density 或 valid-mask 分母归一后再横向比较, 且须记住本列对应留篇宇宙全集。

## VAR: gpt54nano_score_w_sum_ss

【变体差分】
本列为 GPT-5.4-nano 在银行∧金融科技同句共现轨 (_ss) 上的价值加权语调分子和。ss 为最严语境轨: 仅取同句并置目标银行与金科词的句 ±窗口作输入, 衡量「银行与金融科技被直接同句陈述」时 GPT 给出的加权极性, 语义最贴近银行数字化 / 金融科技叙事子空间; 无共现时镜像 ctx 回退全文正文并置 ss_is_fallback=True (共享 n_articles 分母), FINTECH_AC 为空时整批 *_is_fallback 全置 True 优雅降级, 绝不静默清空。差分维度: 模型 = GPT 一家, 轨道 = ss (最严同句共现 + 回退), 门控 = conditional-on-full。早期试跑 T=2 上因共现稀疏可能近零方差 (预期退化, 生产 T=19 恢复), 短面板稳健性表中应对此有预期。它与 gpt54nano 的 full/ctx 两轨、与另两家 ss 列互为稳健性、各自 just-identified 并排, 严禁混入同一 over-identified Hansen J。分子构造同家族: 逐篇 ss 判定 ∈ {−1,0,+1} × mention_density 于 bank-year 'sum' 聚合, 下游除以 valid-mask 加权分母 (_wd_* 权重和, per-model LLM 专用, 非裸 sum_mention_density) 得 gpt54nano_tone_vw_ss。使用提示: 本列把 GPT 的判定锁定在银行与金融科技同句并置的最锐语境上, 语义最贴近银行数字化叙事子空间, 适合作构念效度的窄化第三方厂商稳健性检验; 解读时须结合 ss_is_fallback 占比判断有多少 bank-year 实际退回全文语境, 避免把回退主导的结果误读为同句共现的纯净信号。它与本家族其余八列、与词典轨及监督式 BERT 轨的同构念测度均属规格稳健性并排, 各自 just-identified, 严禁并入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Ludwig, J., Mullainathan, S., & Rambachan, A. (2026). Large language models: An applied econometric framework. Annual Review of Economics. https://doi.org/10.1146/annurev-economics-120925-105620
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A Large Language Model for Extracting Information from Financial Text. Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.12832
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters. https://doi.org/10.1016/j.frl.2024.105227
<!-- rendered-citations:end -->
