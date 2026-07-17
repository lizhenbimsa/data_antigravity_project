---
family_id: F181
columns:
- deepseekv4_tech_frac_ctx
- deepseekv4_tech_frac_full
- deepseekv4_tech_frac_ss
- gemini31_tech_frac_ctx
- gemini31_tech_frac_full
- gemini31_tech_frac_ss
- gpt54nano_tech_frac_ctx
- gpt54nano_tech_frac_full
- gpt54nano_tech_frac_ss
unit: 比率/占比 (proportion, 取值域 [0,1]; 单一 LLM 模型层面的技术定位篇数占比)
formula: "model_tech_frac_track = (该模型在该轨判为技术定位类的篇数) / (该模型在该轨的 verified 篇数); model 取值 gpt54nano/gemini31/deepseekv4 三者之一, track 取值 full/ctx/ss 三者之一"
producer: news_process/pipeline/sentiment/tone_llms.py (阶段21 三家逐条分类) ; news_process/pipeline/panel/encode.py (encode 层聚合 LLM_CLASS_SPEC)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet
- 40_panel_yearly.parquet
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
- doi: 10.1177/00491241251325243
  type: journal
  authors: Chae, Y., & Davidson, T.
  year: 2026
  title: "Large language models for text classification: From zero-shot learning to instruction-tuning"
  venue: Sociological Methods & Research
  vol: 55
  issue: 2
  pages_or_artno: 501-567
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv
- doi: 10.1177/08944393241286471
  type: journal
  authors: Törnberg, P.
  year: 2024
  title: "Large language models outperform expert coders and supervised classifiers at annotating political social media messages"
  venue: Social Science Computer Review
  vol: 43
  issue: 6
  pages_or_artno: 1181-1195
- doi: 10.1093/rfs/hhy130
  type: journal
  authors: Chen, M. A., Wu, Q., & Yang, B.
  year: 2019
  title: "How valuable is FinTech innovation?"
  venue: Review of Financial Studies
  vol: 32
  issue: 5
  pages_or_artno: 2062-2106
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的构念是"银行金融科技活动的技术定位强度" (technology locus), 即在一家银行的年度媒体报道中, 有多大比例的银行金科报道被判定为核心议题落在技术层面 (自建或引入数字技术、系统、基础设施、算法能力) 而非落在业务、渠道或监管层面。这一"定位" (locus) 维度直接承接 Gomber et al. (2018) 对金融科技革命所作的力量分解: 他们把金科的冲击拆为创新的技术侧 (what technology) 与业务功能侧 (which financial service function), 强调同一笔金科事件, 究竟主要发生在"技术能力"这一环还是"金融功能"这一环, 是理解其价值与竞争后果的关键分野。本项目据此把每篇银行金科报道映射到一个离散的定位类别, 并在银行-年层面聚合为技术定位占比 tech_frac, 作为衡量该银行金科叙事"技术含量"的年度面板测度。tech_frac 服务于 P4 (bank_fintech_locus) 论文线, 与实质性维度 (substance, sub_frac) 和协作维度 (collaboration, collab_frac) 并列构成 LLM 分类三维度族。

【方法学与计算】
计算分两阶段。第一阶段在 pipeline/sentiment/tone_llms.py (阶段21) 完成: 每篇被留篇的银行金科报道, 由三家大模型 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 逐条独立地在同一条思维链提示 (prompt v8, temperature=0) 内, 除真伪与情感外, 一并输出该篇的定位判定 (技术 / 业务 / 其他)。第二阶段在 pipeline/panel/encode.py 的 encode 层完成聚合: 由 SSOT 三元映射 encode.LLM_CLASS_SPEC 把文章级基名 (locus) 锁定到面板 metric (tech_frac)、分子目标类 (技术定位类) 与解析键; 该映射是文章命名域与面板命名域之间唯一的互锁点, 两域之间没有任何字符串变换可直接相互推导, 故任何改名都必须同步该映射。分母是"该模型自身在该轨的 verified 篇数" —— 即以该模型自身的真伪判定为准清票后仍留存的篇数, 而非三家共识分母; 这样每一列 {model}_tech_frac_{track} 都是一台完全自洽、可独立复算的仪器, 分子分母同源同轨, 不跨模型也不跨轨借分母。

留篇口径遵循 full-only 门控 (2026-06-29): 是否算作"一篇银行金科报道"这件事只看 full 轨的 llm_verified_full == True; ctx 轨与 ss 轨在此基础上降为 conditional-on-full 的稳健性轨, 其行宇宙是 full 留篇集合的子集, 但 per-track 的分子分母仍按各自轨的判定独立计算。ss 轨的文本回退语义镜像 ctx: 当某篇不存在银行与金科词同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True。文章级中间列 ({short}_{dim}{track}) 属不门控审计存档, 供逐轨对照; 真正进入面板并受 verified 门控的口径在 encode 层收口, 由 {short}_tech_frac_src 指示列标注其分母来源篇数。

本家族横跨两个稳健性维度: 三家模型 (跨厂商) 与三条文本轨 (full/ctx/ss)。铁律是, 三家模型各自 just-identified 并排、三条轨各自 just-identified 并排, 它们互为稳健性、不分主次, 严禁把不同模型或不同轨的 tech_frac 混进同一个 over-identified 的 Hansen J 检验; 跨模型一致性由根级 FWER 模板 27_tableA12 Panel C (CLS 族) 统一承接, 而非在单个回归内混装。per-model 独立降级: 若某家模型整体缺席, 只掉该模型自身的三列, 不连坐其余两家 —— 这与 co-primary 嵌入双轨的 both-or-neither 严格互斥语义不同。

【文献定位】
构念根系在 Gomber et al. (2018) 的金科力量分解, 以及 Chen et al. (2019) 关于金科创新价值的实证: 后者在《Review of Financial Studies》上以专利文本区分金科创新的技术类型, 论证不同技术定位的创新对企业价值的异质贡献, 为"以技术定位为面板测度"提供了直接的经济学正当性。测量方法学层面, 本家族采用大模型作零样本/少样本标注器, 其效度与规范由 Chae & Davidson (2026)、Törnberg (2024) 与 Carlson & Burbano (2026) 共同支撑: Törnberg (2024) 证明大模型在标注任务上可超越专家编码者与监督式分类器; Chae & Davidson (2026) 系统比较零样本到指令微调的文本分类范式; Carlson & Burbano (2026) 在《Strategic Management Journal》上给出管理学研究中以 LLM 标注数据的基础指引与警示 (提示冻结、温度控制、多标注者一致性、缓存复现), 本项目 temperature=0 + prompt v8 字节冻结 + 磁盘缓存的确定性范式即与之对齐。Ludwig et al. (2025) 进一步把大模型标注纳入应用计量框架, 提示以 LLM 生成变量作回归自变量时的测量误差与去偏考量, 是本家族"三家并排、不混 Hansen J"设计的方法学依据之一。

## VAR: deepseekv4_tech_frac_full

【变体差分】
本列是 DeepSeek-V4 Flash 单一模型在 full 轨上的技术定位占比。差分坐标有三: 模型=deepseekv4 (直连 api.deepseek.com, 与走 yunwu 的另两家不同源)、轨道=full (content_full = 标题 prepend + 全文正文)、聚合口径=该模型自身 verified 分母。full 轨是留篇门控的判定轨 (llm_verified_full), 因此本列的分母即该模型在留篇集合上判为真的篇数, 分子是其中被 deepseekv4 判为技术定位类的篇数。与家族内其余八列的关系是"互为稳健性、不分主次": 本列与 gemini31_tech_frac_full、gpt54nano_tech_frac_full 构成同轨跨厂商三胞胎, 用于检验技术定位测度是否被某一厂商的标注习惯所驱动; 与 deepseekv4_tech_frac_ctx、deepseekv4_tech_frac_ss 构成同模型跨轨三胞胎, 用于检验测度是否被输入文本范围所驱动。三家模型各自 just-identified 并排, 严禁把本列与另两家的同名列混进同一 over-identified Hansen J; 跨模型一致性走 27_tableA12 Panel C。作为 P4 locus 线的一条 treatment 稳健性轨, 本列在 deepseekv4 缺席时随该模型族整体降级, 不连坐 gemini31/gpt54nano。需强调, 技术定位类的判据由 encode.LLM_CLASS_SPEC 的分子目标类与解析键锁定, 共识列不是文章级裸多数票, 而是经 verified 门控与 final_v 清票后的结果; 本列作为单一模型的 per-model 存档进入面板, 与共识列在语义上刻意区分, 供 Table A5 跨模型 β 标准化对照使用。以本列估计的技术含量偏高或偏低, 应在与另两家同名列并置后再作解读, 单列水平值 (proportion) 因各家判读门槛不同而不具跨模型可比性, 只有标准化后的回归系数方可跨模型比较。

## VAR: deepseekv4_tech_frac_ctx

【变体差分】
本列是 DeepSeek-V4 Flash 在 ctx 轨上的技术定位占比。差分坐标: 模型=deepseekv4、轨道=ctx (content_ctx = 标题 prepend + 含目标银行句的 ±窗口片段)。相对同模型的 full 轨, ctx 轨把大模型的判读视野收窄到围绕目标银行实体的邻近上下文, 属 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集合的子集, 但 verified 判定与技术定位判定均按 ctx 轨文本独立重算, 分母是 deepseekv4 在 ctx 轨的自有 verified 篇数, 不借 full 轨分母。该轨回答的问题是: 当只让模型看"银行出现处附近的话", 银行金科叙事的技术含量估计是否稳健。本列与 gemini31_tech_frac_ctx、gpt54nano_tech_frac_ctx 同轨跨厂商互为稳健性, 与 deepseekv4 的 full/ss 两列同模型跨轨互为稳健性; 三家模型、三条轨各自 just-identified 并排, 不分主次, 严禁混进同一 over-identified Hansen J。dev T=2 语料上 ctx 轨可能因样本稀薄出现退化取值, 属预期, 生产 T=19 恢复正常。相较 full 轨, ctx 轨的价值在于隔离"篇章其余部分的干扰": 若一篇报道主体讲监管而仅顺带提及某银行的技术升级, full 轨可能仍把整篇的定位判读拉向业务或监管, 而 ctx 轨把视野钉在银行实体附近, 更贴近"这家银行在这篇报道里的技术定位"这一目标构念。因此 ctx 与 full 的差异本身即是一种测量误差诊断: 两轨结论一致说明定位测度对文本范围不敏感, 分歧则提示需在稳健性叙事中披露。本列的分母指示列 deepseekv4_tech_frac_src 标注 ctx 轨自有 verified 篇数, 供审计复算。

## VAR: deepseekv4_tech_frac_ss

【变体差分】
本列是 DeepSeek-V4 Flash 在 ss 轨 (银行∧金科同句共现窗) 上的技术定位占比。差分坐标: 模型=deepseekv4、轨道=ss (content_ss = 标题 prepend + 同句内同时含目标银行与金科词的句子 ±窗口)。ss 是三轨中判读视野最窄、信噪比要求最高的一轨, 只保留银行主体与金融科技概念真正同句共现的语境, 供最严格的三角验证使用。回退语义镜像 ctx: 当某篇不存在银行与金科同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True, 与 ctx 的回退机制对称。本列分母是 deepseekv4 在 ss 轨的自有 verified 篇数, 分子是其中判为技术定位类的篇数, 严格逐轨、不借 full 或 ctx 分母。本列与 gemini31_tech_frac_ss、gpt54nano_tech_frac_ss 同轨跨厂商互为稳健性, 与 deepseekv4 的 full/ctx 两列同模型跨轨互为稳健性; 三家、三轨各自 just-identified 并排, 不分主次, 严禁混进同一 over-identified Hansen J, 跨模型一致性走 27_tableA12 Panel C。ss 轨是三轨中对"银行确实与金科概念发生实质关联"要求最强的一轨, 因此它在识别上最接近纯净的处理构念, 但代价是有效样本最稀、回退比例最高; 当 ss_is_fallback=True 的篇章占比升高时, 本列实际趋近于 deepseekv4 的全文判读, 需结合 ss 回退率一并解读。dev T=2 语料上 ss 轨常因共现篇稀薄而退化, 属预期, 生产 T=19 恢复。本列与同模型 full/ctx 两列的梯度, 呈现的是"文本视野从全文逐步收窄到同句共现"时技术定位估计的位移, 三轨并置即构成对 deepseekv4 单一模型内部的稳健性谱系, 与跨厂商谱系正交、不交叉。

## VAR: gemini31_tech_frac_full

【变体差分】
本列是 Gemini-3.1-flash-lite 单一模型在 full 轨上的技术定位占比。差分坐标: 模型=gemini31 (经 yunwu 路由)、轨道=full。作为 full 轨留篇门控下的稳健性轨, 分母是 gemini31 自身在留篇集合上判为真的篇数, 分子是其中被 gemini31 判为技术定位类的篇数; 分子分母同源同轨, 不与另两家共享分母。本列的存在意义在于把"技术定位占比"这一测度从任一单一厂商的标注偏好中解耦: gemini31 与 gpt54nano、deepseekv4 在同一 prompt v8、同一 temperature=0 下对同一批 full 轨文本独立判读, 三列若结论一致则说明测度不被厂商驱动。本列与 deepseekv4_tech_frac_full、gpt54nano_tech_frac_full 同轨跨厂商互为稳健性, 与 gemini31 的 ctx/ss 两列同模型跨轨互为稳健性; 三家模型、三条轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把本列与其余同名列混进同一 over-identified Hansen J。gemini31 缺席时只掉本模型族三列, 不连坐其余两家 (per-model 独立降级)。gemini31 与 deepseekv4 分属不同厂商、不同训练语料与对齐策略, 故本列相对 deepseekv4_tech_frac_full 的差异, 承载的正是"标注器身份"这一维度的稳健性检验: 若两列在银行-年面板上高度一致, 则技术定位测度可视为对具体大模型不敏感的稳定构念。本列水平值仅在 gemini31 内部可比, 跨模型比较须先经 z-score 标准化后比回归系数, 不比原始占比。作为 P4 locus 线的 treatment 稳健性轨之一, 本列与三维度族的另两维 (sub_frac 实质性、collab_frac 协作) 正交, 各自度量金科叙事的不同侧面, 不相互替代。

## VAR: gemini31_tech_frac_ctx

【变体差分】
本列是 Gemini-3.1-flash-lite 在 ctx 轨上的技术定位占比。差分坐标: 模型=gemini31、轨道=ctx (标题 prepend + 目标银行句 ±窗口)。相对同模型 full 轨, 本列把 gemini31 的判读视野收窄到银行实体邻近上下文, 属 conditional-on-full 的稳健性轨: 行宇宙是 full 留篇子集, 但 verified 与技术定位判定按 ctx 轨文本独立重算, 分母为 gemini31 在 ctx 轨自有 verified 篇数。它回答的是"只看银行出现处附近, gemini31 估计的技术含量是否稳健"。本列与 deepseekv4_tech_frac_ctx、gpt54nano_tech_frac_ctx 同轨跨厂商互为稳健性, 与 gemini31 的 full/ss 两列同模型跨轨互为稳健性; 三家、三轨各自 just-identified 并排, 不分主次, 严禁混进同一 over-identified Hansen J, 跨模型一致性走 27_tableA12 Panel C。dev T=2 上 ctx 轨可能退化, 属预期, 生产 T=19 正常。ctx 轨对 gemini31 而言尤其重要, 因为不同厂商的模型对"篇章整体语境"的权衡各异: 有的模型倾向被开篇导语主导, 有的更均衡地整合全文; 把视野统一收窄到银行实体附近, 可在一定程度上抹平这种厂商级的阅读风格差异, 使 ctx 轨的跨厂商三胞胎比 full 轨更可能收敛。本列分母指示列 gemini31_tech_frac_src 标注 ctx 轨自有 verified 篇数, 与 full/ss 轨的同名指示列分立, 保证逐轨复算的可审计性; 本列与同模型 full/ss 两列共同构成 gemini31 的三轨稳健性谱系, 与跨厂商谱系正交。

## VAR: gemini31_tech_frac_ss

【变体差分】
本列是 Gemini-3.1-flash-lite 在 ss 轨上的技术定位占比。差分坐标: 模型=gemini31、轨道=ss (标题 prepend + 银行∧金科同句共现窗)。ss 是判读视野最窄的一轨, 只在银行主体与金科概念真正同句共现的语境内取样, 供最严格三角验证。回退语义镜像 ctx: 无同句共现时 content_ss 回退全文正文并置 ss_is_fallback=True。本列分母是 gemini31 在 ss 轨自有 verified 篇数, 分子是其中判技术定位类篇数, 严格逐轨不借 full/ctx 分母。本列与 deepseekv4_tech_frac_ss、gpt54nano_tech_frac_ss 同轨跨厂商互为稳健性, 与 gemini31 的 full/ctx 两列同模型跨轨互为稳健性; 三家、三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。ss 轨对 gemini31 的判读施加了最强的语境约束, 只在银行与金科词真正同句共现处取样, 因此它剔除了大量"银行与金科在同篇但不同段落各说各话"的弱关联噪声, 识别上最接近纯净处理; 代价是有效样本最稀、ss_is_fallback 回退比例最高, 当回退占比升高时本列趋近 gemini31 的全文判读, 须结合回退率解读。本列水平值仅 gemini31 内部可比, 跨模型比较经 z-score 标准化后比系数。本列与同模型 full/ctx 两列构成 gemini31 三轨稳健性谱系, 呈现文本视野收窄时技术定位估计的位移, 与跨厂商谱系正交、不交叉; dev T=2 上 ss 轨常退化属预期, 生产 T=19 恢复。

## VAR: gpt54nano_tech_frac_full

【变体差分】
本列是 GPT-5.4-nano 单一模型在 full 轨上的技术定位占比。差分坐标: 模型=gpt54nano (经 yunwu 路由)、轨道=full。作为 full 轨留篇门控下的稳健性轨, 分母是 gpt54nano 自身在留篇集合上判为真的篇数, 分子是其中被 gpt54nano 判为技术定位类的篇数; 分子分母同源同轨, 不与另两家共享分母。本列与 deepseekv4_tech_frac_full、gemini31_tech_frac_full 同轨跨厂商互为稳健性, 用于把技术定位测度从任一厂商标注习惯中解耦; 与 gpt54nano 的 ctx/ss 两列同模型跨轨互为稳健性, 用于把测度从输入文本范围中解耦。三家模型、三条轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把本列与其余同名列混进同一 over-identified Hansen J, 跨模型一致性由 27_tableA12 Panel C (CLS 族) 统一承接。作为 P4 locus 线的 treatment 稳健性轨之一, 本列在 gpt54nano 缺席时随本模型族整体降级, 不连坐 gemini31/deepseekv4 (per-model 独立降级)。gpt54nano 作为 OpenAI 系轻量模型, 与 gemini31 (Google 系)、deepseekv4 (DeepSeek 系) 分属三家不同厂商, 三列同轨并置即构成对"标注器身份"的完整跨厂商稳健性检验; 本列相对另两家同名列的分歧, 是判断技术定位测度是否被单一厂商标注偏好驱动的直接证据。本列水平值仅 gpt54nano 内部可比, 跨模型比较须先 z-score 标准化后比回归系数, 不比原始占比 (proportion) 水平。作为 P4 locus 线的 treatment 稳健性轨之一, 本列与三维度族的实质性 (sub_frac)、协作 (collab_frac) 两维正交, 各度量金科叙事的不同侧面, 不相互替代; 其分母指示列 gpt54nano_tech_frac_src 标注 full 轨自有 verified 篇数, 供审计复算。

## VAR: gpt54nano_tech_frac_ctx

【变体差分】
本列是 GPT-5.4-nano 在 ctx 轨上的技术定位占比。差分坐标: 模型=gpt54nano、轨道=ctx (标题 prepend + 目标银行句 ±窗口)。相对同模型 full 轨, 本列把 gpt54nano 的判读视野收窄到银行实体邻近上下文, 属 conditional-on-full 的稳健性轨: 行宇宙是 full 留篇子集, 但 verified 与技术定位判定按 ctx 轨文本独立重算, 分母为 gpt54nano 在 ctx 轨自有 verified 篇数, 不借 full 轨分母。它回答的是"只让模型看银行出现处附近的话, gpt54nano 估计的技术含量是否稳健"。本列与 deepseekv4_tech_frac_ctx、gemini31_tech_frac_ctx 同轨跨厂商互为稳健性, 与 gpt54nano 的 full/ss 两列同模型跨轨互为稳健性; 三家、三轨各自 just-identified 并排, 不分主次, 严禁混进同一 over-identified Hansen J。dev T=2 上 ctx 轨可能因样本稀薄退化, 属预期, 生产 T=19 恢复正常。ctx 轨相对 full 轨的意义在于隔离篇章其余部分的干扰: 当一篇报道主线并非某银行的技术议题、而只是顺带提及时, full 轨的整篇判读可能被主线拉偏, ctx 轨则把 gpt54nano 的视野钉在银行实体附近, 更贴近"这家银行在这篇报道里的技术定位"。因此 ctx 与 full 的分歧本身即是测量误差诊断: 两轨一致说明测度对文本范围稳健, 分歧则须在稳健性叙事中披露。本列分母指示列 gpt54nano_tech_frac_src 标注 ctx 轨自有 verified 篇数, 与 full/ss 同名指示列分立; 本列与同模型 full/ss 两列构成 gpt54nano 三轨稳健性谱系, 与跨厂商谱系正交、不交叉。

## VAR: gpt54nano_tech_frac_ss

【变体差分】
本列是 GPT-5.4-nano 在 ss 轨上的技术定位占比。差分坐标: 模型=gpt54nano、轨道=ss (标题 prepend + 银行∧金科同句共现窗)。ss 是三轨中信噪比要求最高的一轨, 只在银行主体与金科概念真正同句共现的语境内取样, 供最严格三角验证使用。回退语义镜像 ctx: 无同句共现时 content_ss 回退为全文正文并置 ss_is_fallback=True。本列分母是 gpt54nano 在 ss 轨自有 verified 篇数, 分子是其中被判为技术定位类的篇数, 严格逐轨、不借 full 或 ctx 分母。本列与 deepseekv4_tech_frac_ss、gemini31_tech_frac_ss 同轨跨厂商互为稳健性, 与 gpt54nano 的 full/ctx 两列同模型跨轨互为稳健性; 三家模型、三条轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把本列与其余同名列混进同一 over-identified Hansen J, 跨模型一致性走 27_tableA12 Panel C。gpt54nano 缺席时随本模型族整体降级, 不连坐 gemini31/deepseekv4。ss 轨对 gpt54nano 施加最强语境约束, 只在银行与金科词真正同句共现处取样, 剔除同篇不同段的弱关联噪声, 识别上最接近纯净处理构念; 代价是有效样本最稀、ss_is_fallback 回退比例最高, 当回退占比升高时本列趋近 gpt54nano 的全文判读, 须结合回退率解读。本列水平值仅 gpt54nano 内部可比, 跨模型比较经 z-score 标准化后比系数。本列与同模型 full/ctx 两列共同构成 gpt54nano 三轨稳健性谱系, 呈现文本视野从全文收窄到同句共现时技术定位估计的位移, 与跨厂商谱系正交、不交叉; dev T=2 上 ss 轨常退化属预期, 生产 T=19 恢复正常。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Chae, Y., & Davidson, T. (2026). Large language models for text classification: From zero-shot learning to instruction-tuning. Sociological Methods & Research, 55(2), 501-567. https://doi.org/10.1177/00491241251325243
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Törnberg, P. (2024). Large language models outperform expert coders and supervised classifiers at annotating political social media messages. Social Science Computer Review, 43(6), 1181-1195. https://doi.org/10.1177/08944393241286471
Chen, M. A., Wu, Q., & Yang, B. (2019). How valuable is FinTech innovation? Review of Financial Studies, 32(5), 2062-2106. https://doi.org/10.1093/rfs/hhy130
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
<!-- rendered-citations:end -->
