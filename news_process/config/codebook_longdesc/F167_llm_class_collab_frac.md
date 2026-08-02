---
family_id: F167
columns:
- deepseekv4_collab_frac_ctx
- deepseekv4_collab_frac_full
- deepseekv4_collab_frac_ss
- gemini31_collab_frac_ctx
- gemini31_collab_frac_full
- gemini31_collab_frac_ss
- gpt54nano_collab_frac_ctx
- gpt54nano_collab_frac_full
- gpt54nano_collab_frac_ss
unit: 占比 (proportion, 无量纲, 值域 [0,1]; 单一 LLM 模型判为"外部协同"的篇数 / 该模型 verified 篇数)
formula: "{short}_collab_frac{track} = bank-year 内 mean({short}_collab_frac_src{track}); 其中 src = 1 若该模型 verified 且 innovation_collab_mode == '外部协同', 0 若 verified 但非该类, NA 若未 verified — groupby mean 恰等于 (该模型判为外部协同篇数)/(该模型 verified 篇数)"
producer: news_process/pipeline/panel/encode.py::encode_sentiment (per-model 门控指示列 {short}_collab_frac_src{track}) + build_aggregation_dict (bank-year mean 聚合); 上游 news_process/pipeline/sentiment/tone_llms.py (stage 21 per-model 分类存档列 {short}_collab{track})
upstream:
- 21_tone_llms.parquet (per-model innovation_collab_mode 判定 + verified 标记, 三轨)
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
- doi: 10.1177/08944393241286471
  type: journal
  authors: Törnberg, P.
  year: 2024
  title: "Large language models outperform expert coders and supervised classifiers at annotating political social media messages"
  venue: Social Science Computer Review
  vol: 43
  issue: 6
  pages_or_artno: 1181-1195
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: "Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis"
  venue: Journal of Product Innovation Management
  vol: 41
  issue: 4
  pages_or_artno: 793-815
- doi: 10.1086/727712
  type: journal
  authors: Lerner, J., Seru, A., Short, N., & Sun, Y.
  year: 2024
  title: "Financial innovation in the twenty-first century: Evidence from US patents"
  venue: Journal of Political Economy
  vol: 132
  issue: 5
  pages_or_artno: 1391-1449
- doi: 10.1002/smj.507
  type: journal
  authors: Laursen, K., & Salter, A.
  year: 2006
  title: "Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms"
  venue: Strategic Management Journal
  vol: 27
  issue: 2
  pages_or_artno: 131-150
- doi: 10.1016/S0048-7333(01)00120-2
  type: journal
  authors: Hagedoorn, J.
  year: 2002
  title: "Inter-firm R&D partnerships: An overview of major trends and patterns since 1960"
  venue: Research Policy
  vol: 31
  issue: 4
  pages_or_artno: 477-492
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
new_dois: []
---

## CORE

【构念与来源】
本家族 9 列度量的是"外部协同"这一创新模式维度在单一 LLM 模型判定口径下的银行-年占比, 是主线论文 P5 (bank_fintech_collab, 理论锚定 Chesbrough 开放式创新) 处理变量的跨厂商稳健臂。构念上, 每篇银行金融科技报道被大模型沿三个正交的分类维度贴标, 其中"创新协同模式" (innovation_collab_mode) 维把报道刻画的银行创新路径二分为"自主研发"与"外部协同"两类: 前者指银行依靠自有团队、内部研发资源推进金融科技; 后者指银行通过与外部金融科技企业结盟、合资、股权投资、并购、平台开放或联合实验室等方式吸纳外部创新能力。外部协同占比越高, 越贴合 Chesbrough 提出的开放式创新范式, 即企业主动跨越组织边界、以内外部知识流入流出并举的方式获取创新绩效。该构念的学理根系可上溯到企业间研发合作与联盟研究传统, 也与吸收能力、开放度对创新绩效的解释框架一脉相承。数据来源是 stage 21 (tone_llms) 对每篇报道逐模型、逐轨请求得到的分类结果: gpt54nano、gemini31、deepseekv4 三家模型各自独立给出 innovation_collab_mode 标签, 未先做多数投票折叠。共识列 collab_frac 是 canonical headline, 但其构造并非对三家原始存档标签直接取裸多数票——须先经 per-model verified 门控与 final_v 清票, 再在合法票面上聚合共识; 本家族 9 列则把共识拆回三家 per-model 子测度, 供跨厂商三角验证。

【方法学与计算】
计算分两层。文章级 (stage 21) 每家模型对每篇报道输出 innovation_collab_mode 存档标签; 该存档列本身不做 verified 门控, 保留原始输出以备审计。面板级门控在 encode 层一次完成: encode_sentiment 为每家模型每条轨构造门控指示列 {short}_collab_frac_src{track}, 取值规则为——该模型 verified 为真且其协同模式标签等于目标类"外部协同"记 1, verified 为真但标签非该类记 0, 该模型未 verified 记缺失 NA。随后 build_aggregation_dict 在 bank-year 上对该指示列取 mean; 由于 mean 跳过 NA, 其结果恰等于 (该模型判为外部协同的篇数)/(该模型 verified 篇数)。分母是该模型自身的 verified 篇数, 即 per-model 版的 n_articles_llm_valid, 而非共识口径的分母——这保证分子分母同源、占比落在 [0,1]。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否算"银行金融科技报道"只看 llm_verified_full; ctx 与 ss 轨降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但 per-model verified 掩码与分母按各轨自身计数, 不跨轨借用。三家 per-model 子测度与共识 collab_frac、以及三轨 full/ctx/ss、政治词权重梯度、co-primary 双轨嵌入遵循同一条铁律: 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同模型或不同轨的同名占比混进同一个 over-identified 的 Hansen J 过度识别检验; 跨模型的族级 FWER 校正另由根级 rwolf 模板承担, 不在本族内部做。三家模型是 SSOT (encode.LLM_MODELS) 的成员, 任一家在生产中缺席只连坐掉自身族列, 属 per-model 独立降级, 并非 co-primary 嵌入那种 both-or-neither 的双列同置。

【文献定位】
方法学上, 以生成式大模型替代人工编码做文本标注的效度与操作规范, 近年已有系统论述: Carlson 与 Burbano (2026) 在管理学研究情境下给出用 LLM 标注数据的基础准则与警示, 强调多模型交叉、温度冻结与可复现缓存是可信标注的前提, 直接支撑本项目"三家模型逐条投票 + prompt 字节冻结 + temperature=0"的设计。de Kok (2025) 针对会计研究说明如何用生成式 LLM 做文本分析并把温度设零、缓存复用以保确定性; Törnberg (2024) 实证显示大模型在标注任务上可超过专家编码员与监督式分类器。把多家大模型的独立判定聚合为共识, 其方法根据在于多模型集成 (Chen 等, 2025) 对单模型判定习惯偏差的抵消: 需注意本项目的共识 collab_frac 并非对三家原始存档标签直接取裸多数票, 而是先施加 per-model verified 门控与 final_v 清票, 再在合法票面上聚合, 故共识列的构造严于教科书式多数投票——本家族 9 列则是把该共识拆回三家 per-model 子测度作跨厂商三角验证。构念侧, 外部协同/开放式创新的测量传统由 Laursen 与 Salter (2006) 对开放度的开创性刻画、Hagedoorn (2002) 对企业间研发合作长期趋势的梳理, 以及 Zhang 等 (2024) 对二十年开放式创新的框架与元分析共同奠定; 金融创新本身的专利证据由 Lerner 等 (2024) 提供。本族把这些构念放进逐厂商可比的占比测度, 使"银行走外部协同路线"的媒体信号得以跨模型三角验证。

## VAR: deepseekv4_collab_frac_full

【变体差分】
本列取 DeepSeek-V4 Flash 单一模型、full 轨的外部协同占比。模型侧: deepseekv4 是 stage 21 三家投票模型之一, 直连 api.deepseek.com (与走 OpenLux 的 gpt54nano、gemini31 不同源), 供应商归属为深度求索 DeepSeek V4 Flash, 历史上曾被误标为 Grok, 现已勘误。本列只用该家自身的判定与自身的 verified 掩码, 不掺入另外两家。轨道侧: full 轨输入为 content_full = 标题 prepend + 全文正文, 是留篇门控的判定轨 (full-only 口径), 也是三轨中信息最完整、分母通常最大的一轨; 分子为该模型在 full 轨 verified 且判为"外部协同"的篇数, 分母为该模型 full 轨 verified 篇数。相对家族 canonical (共识 collab_frac, 经 verified 门控与 final_v 清票后再多数投票聚合, 非裸多数票), 本列刻意不折叠投票, 保留单厂商视角作跨厂商稳健臂。与同族 gpt54nano、gemini31 的 full 列 co-equal, 各自 just-identified 并排、互为稳健性、不分主次, 严禁三家同名占比混进同一 over-identified Hansen J。DeepSeek 在生产缺席时仅连坐本族 deepseekv4 三列, 属 per-model 独立降级, 与 co-primary 嵌入那种 both-or-neither 双列同置不同。实证解读上, 本列的量纲是纯占比: 值为 1 表示该银行该年被 DeepSeek 判定为有效的银行金融科技报道全部落在外部协同一侧, 值为 0 表示全部落在自主研发一侧, 中间值表示两条创新路径在媒体报道中的相对权重。由于协同模式维度允许缺标残差 (个别报道 verified 但两类标签都未贴上), 互补两类——collab (外部协同, 本列度量) 与 indep (自主研发)——的占比之和可能小于 1, 差额即该模型未能给出协同模式标签的那部分, 属正确语义而非缺陷; 注意 indep 与"自主研发"是同一类, 二者并非彼此残差。跨模型对读时, 若三家 full 列在同一银行-年给出一致的高外部协同占比, 则该处理信号的可信度显著提升, 这正是三角验证的用途; 若三家分歧较大, 则提示该银行的协同叙事在媒体文本中本身模糊。作为稳健性臂, 本列不进入主回归的核心 RHS, 而是与共识 collab_frac 并排检验主结论是否被单一厂商的判定习惯驱动。

## VAR: deepseekv4_collab_frac_ctx

【变体差分】
本列取 DeepSeek-V4 Flash 单一模型、ctx 轨的外部协同占比。轨道侧: ctx 轨输入为 content_ctx = 标题 prepend + 含目标银行句的 ±窗口上下文片段 (实体邻近, Hassan 式 proximity), 聚焦银行实体周边语境而非全文, 故对泛泛提及但未紧扣银行的协同信号更保守。按 full-only 口径, ctx 是 conditional-on-full 的测度轨: 其行宇宙为 full 留篇集子集, 但 verified 掩码与分母 (该模型 ctx 轨 verified 篇数, 对应 n_articles_llm_valid_ctx 的 per-model 版) 按 ctx 轨自身计数, 绝不借用 full 轨分母——否则会出现轨道不对称除法使占比越界。模型侧同 deepseekv4_collab_frac_full, 单厂商、直连 api.deepseek.com、不折叠投票。相对 full 列, 本列的差分仅在输入文本轨 (ctx vs full), 二者互为稳健性、不分主次, 严禁与 full/ss 同名占比混进同一 over-identified Hansen J。在早期试跑 T=2 样本上 ctx 轨可能出现零方差退化, 属预期, 生产 T=19 恢复正常。因 ctx 轨把语境收窄到银行实体周边, 分母 (该模型 ctx 轨 verified 篇数) 通常小于 full 轨, 故本列相对 full 列往往更"离散"、噪声更高, 但也更少受与银行无关的泛金科段落污染, 二者恰构成一对信息完整度与语境精度的权衡。解读时应把本列视作 full 列的语境敏感性对照: 若外部协同占比在收窄语境后依然稳健, 说明协同信号确实系于银行本身而非报道中其他主体。作为 DeepSeek 单厂商的 ctx 视角, 本列与 gpt54nano、gemini31 的 ctx 列跨厂商互证, 三家一致方增强处理变量效度; 与本族 deepseekv4 的 full/ss 列则是同厂商跨轨互证。所有并排关系一律 just-identified, 不做过度识别合并。

## VAR: deepseekv4_collab_frac_ss

【变体差分】
本列取 DeepSeek-V4 Flash 单一模型、ss 轨的外部协同占比。轨道侧: ss 轨输入为 content_ss = 标题 prepend + 同一句内同时出现"目标银行"与"金融科技词"的句子的 ±窗口, 是三轨中语义最严的一轨, 要求银行与金科在同句共现, 最贴近"这家银行确实在谈金融科技协同"的强信号。ss 的回退语义镜像 ctx: 当某篇报道无银行与金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置真, 并共享 n_articles 分母口径; 若上游金科 AC 自动机为空则 ss_is_fallback 全真, 优雅降级。按 full-only 口径, ss 为 conditional-on-full 测度轨, verified 掩码与分母 (该模型 ss 轨 verified 篇数, 对应 n_articles_llm_valid_ss 的 per-model 版) 按 ss 轨自身计数。模型侧同 deepseekv4 其余两列, 单厂商、不折叠投票。相对 full/ctx 列, 差分仅在文本轨 (ss 同句共现口径), 三轨互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。开发样本早期试跑 T=2 上 ss 轨常零方差退化, 属预期。由于 ss 轨要求银行与金科同句共现这一最严判据, 未回退的 ss 分子对应的是媒体明确把该银行与金融科技绑定叙述的报道, 因而本列在三轨中最贴近"银行确实公开走外部协同路线"的强证据口径; 但也正因判据严格, 大量报道触发回退, 使本列在实际语料中的有效方差更依赖生产规模。解读上, 本列适合与 deepseekv4 的 full/ctx 列做梯度对读: 若外部协同占比沿 full→ctx→ss 逐轨收窄仍保持方向一致, 说明协同信号在从宽到严的语义过滤下稳健。作为 DeepSeek 单厂商的最严轨视角, 本列与另两家 ss 列跨厂商互证。

## VAR: gemini31_collab_frac_full

【变体差分】
本列取 Gemini-3.1 Flash-Lite 单一模型、full 轨的外部协同占比。模型侧: gemini31 是 stage 21 三家投票模型之一, 经 OpenLux 网关调用 (与同走 OpenLux 的 gpt54nano 同源、与直连的 deepseekv4 异源), 供应商为 Google Gemini 系。本列只用 gemini31 自家的判定与 verified 掩码, 不掺另外两家, 用作 P5 外部协同处理变量的又一跨厂商视角。轨道侧: full 轨输入 content_full = 标题 prepend + 全文正文, 是留篇门控判定轨; 分子为该模型 full 轨 verified 且判"外部协同"篇数, 分母为该模型 full 轨 verified 篇数。相对家族 canonical 共识 collab_frac (经 verified 门控与 final_v 清票后再多数投票聚合, 非裸多数票折叠), 本列保留单厂商视角。与 deepseekv4、gpt54nano 的 full 列 co-equal, 各自 just-identified 并排、互为稳健性、不分主次, 严禁三家同名占比同进一个 over-identified Hansen J; 三家共识与 per-model 的关系镜像三轨与政治词权重梯度。gemini31 生产缺席仅连坐本族 gemini31 三列, per-model 独立降级。实证上, Gemini 系模型的判定习惯可能与 GPT、DeepSeek 存在系统性差异 (如对"战略合作"措辞的敏感度), 保留本列正是为了让这类厂商特异性暴露于稳健性对读, 而非被多数投票掩盖。值为 1 表示该银行该年 Gemini 判定的全部有效银行金科报道均落外部协同侧, 值为 0 表示全落自主研发侧; 互补两类 collab (外部协同) 与 indep (自主研发) 的占比之和可能因缺标残差小于 1, 属正确语义 (indep 即自主研发, 非另一残差类)。本列不进主回归核心 RHS, 而与共识 collab_frac 并排检验 P5 处理信号是否稳健于厂商选择。跨读时, 若 gemini31 与 gpt54nano、deepseekv4 的 full 列在同一银行-年高度一致, 处理变量的构念效度即获三角支撑。

## VAR: gemini31_collab_frac_ctx

【变体差分】
本列取 Gemini-3.1 Flash-Lite 单一模型、ctx 轨的外部协同占比。轨道侧: ctx 轨输入 content_ctx = 标题 prepend + 含目标银行句 ±窗口的实体邻近上下文, 相较 full 更聚焦银行周边语境, 对未紧贴银行的泛协同表述更保守。按 full-only 口径, ctx 为 conditional-on-full 测度轨, 行宇宙是 full 留篇集子集, 但 verified 掩码与分母按 ctx 轨自身计数 (per-model 版 n_articles_llm_valid_ctx), 不借 full 分母以免轨道不对称除法致占比越界。模型侧同 gemini31 其余两列: 经 OpenLux 调用、单厂商、不折叠投票。相对 gemini31_collab_frac_full, 差分仅在文本轨 (ctx vs full); 相对 deepseekv4/gpt54nano 的 ctx 列, 差分在模型厂商。全部 co-equal、互为稳健性、不分主次, 严禁与同名 full/ss 或跨厂商同名占比混进同一 over-identified Hansen J。开发样本早期试跑 T=2 上 ctx 轨可能零方差退化, 生产 T=19 正常。因语境收窄至银行实体周边, 本列分母通常小于 gemini31 的 full 轨, 相对更离散但更少受无关金科段落污染, 适合作 gemini31_collab_frac_full 的语境敏感性对照: 若外部协同占比在收窄语境后依然稳健, 说明该 Gemini 判定的协同信号确系于银行本身。本列既与 gemini31 的 full/ss 列做同厂商跨轨互证, 又与 deepseekv4、gpt54nano 的 ctx 列做同轨跨厂商互证, 两条互证方向正交, 共同支撑 P5 外部协同处理变量的稳健性叙事。本列作为稳健性臂不进主回归核心 RHS, 而与共识 collab_frac 并排, 用以证明主结论不被单一厂商在收窄语境下的判定习惯所驱动。

## VAR: gemini31_collab_frac_ss

【变体差分】
本列取 Gemini-3.1 Flash-Lite 单一模型、ss 轨的外部协同占比。轨道侧: ss 轨输入 content_ss = 标题 prepend + 银行与金科同句共现句 ±窗口, 是语义最严的一轨, 要求银行与金融科技词在同一句里共现, 最能锁定"该银行确在谈金科协同"的强信号; 无同句共现时回退全文 body 并置 ss_is_fallback 为真, 镜像 ctx 回退语义、共享 n_articles 分母口径。按 full-only 口径, ss 为 conditional-on-full 测度轨, verified 掩码与分母 (per-model 版 n_articles_llm_valid_ss) 按 ss 轨自身计数。模型侧同 gemini31 其余两列: 经 OpenLux 网关、单厂商、不折叠投票。相对 gemini31 的 full/ctx 列, 差分仅在文本轨 (ss 同句共现口径); 相对 deepseekv4/gpt54nano 的 ss 列, 差分在厂商。三轨与三厂商全部 co-equal、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。开发样本早期试跑 T=2 上 ss 轨常零方差退化, 属预期。作为 Gemini 单厂商在最严同句共现判据下的视角, 本列的未回退分子对应媒体明确把该银行与金融科技并置叙述的报道, 是三轨中最贴近强证据口径的一轨, 但因判据严格触发大量回退, 有效方差更依赖生产语料规模。解读时宜与 gemini31 的 full/ctx 列做 full→ctx→ss 梯度对读: 方向沿由宽到严的语义过滤保持一致, 则协同信号稳健。与 deepseekv4、gpt54nano 的 ss 列跨厂商互证时, 三家一致方增强处理变量在最严口径下的效度。

## VAR: gpt54nano_collab_frac_full

【变体差分】
本列取 GPT-5.4-nano 单一模型、full 轨的外部协同占比。模型侧: gpt54nano 是 stage 21 三家投票模型之一, 经 OpenLux 网关调用 (与 gemini31 同源、与直连的 deepseekv4 异源), 供应商为 OpenAI GPT-5 系轻量档。本列只用 gpt54nano 自家判定与 verified 掩码, 作 P5 外部协同处理变量的第三个跨厂商视角。轨道侧: full 轨输入 content_full = 标题 prepend + 全文正文, 是留篇门控判定轨; 分子为该模型 full 轨 verified 且判"外部协同"篇数, 分母为该模型 full 轨 verified 篇数。相对家族 canonical 共识 collab_frac (经 verified 门控与 final_v 清票后再多数投票聚合, 非裸多数票), 本列保留单厂商视角。与 deepseekv4、gemini31 的 full 列 co-equal, 各自 just-identified 并排、互为稳健性、不分主次, 严禁三家同名占比混进同一 over-identified Hansen J; 跨模型族级 FWER 由根级 rwolf 模板承担而非本族内部。gpt54nano 生产缺席仅连坐本族 gpt54nano 三列, per-model 独立降级。实证上, GPT 系轻量档模型的判定习惯自成一系, 保留本列使其厂商特异性暴露于稳健性对读而非被投票折叠掩盖。值为 1 表示该银行该年 GPT 判定的全部有效银行金科报道均落外部协同侧, 值为 0 表示全落自主研发侧; 互补两类 collab (外部协同) 与 indep (自主研发) 的占比之和可能因缺标残差小于 1, 属正确语义 (indep 即自主研发, 非另一残差类)。本列不进主回归核心 RHS, 而与共识 collab_frac 并排, 检验 P5 处理信号是否稳健于厂商选择。若 gpt54nano 与 gemini31、deepseekv4 的 full 列在同一银行-年高度一致, 则外部协同处理变量的构念效度获三家三角支撑, 这也是 stage 21 采用三家逐条投票而非单模型的根本理由。

## VAR: gpt54nano_collab_frac_ctx

【变体差分】
本列取 GPT-5.4-nano 单一模型、ctx 轨的外部协同占比。轨道侧: ctx 轨输入 content_ctx = 标题 prepend + 含目标银行句 ±窗口的实体邻近上下文, 相较 full 更聚焦银行周边语境, 对未紧扣银行的泛协同表述更保守。按 full-only 口径, ctx 为 conditional-on-full 测度轨, 行宇宙是 full 留篇集子集, 但 verified 掩码与分母按 ctx 轨自身计数 (per-model 版 n_articles_llm_valid_ctx), 不借 full 分母以免轨道不对称除法致占比越界。模型侧同 gpt54nano 其余两列: 经 OpenLux 网关、单厂商、不折叠投票。相对 gpt54nano_collab_frac_full, 差分仅在文本轨 (ctx vs full); 相对 deepseekv4/gemini31 的 ctx 列, 差分在厂商。全部 co-equal、互为稳健性、不分主次, 严禁与同名 full/ss 或跨厂商同名占比混进同一 over-identified Hansen J。开发样本早期试跑 T=2 上 ctx 轨可能零方差退化, 生产 T=19 正常。因语境收窄至银行实体周边, 本列分母通常小于 gpt54nano 的 full 轨, 相对更离散但更少受与银行无关的泛金科段落污染, 适合作 gpt54nano_collab_frac_full 的语境敏感性对照: 外部协同占比在收窄语境后仍稳健, 则说明该 GPT 判定的协同信号确系于银行本身。本列既与 gpt54nano 的 full/ss 列做同厂商跨轨互证, 又与 deepseekv4、gemini31 的 ctx 列做同轨跨厂商互证, 两条互证方向正交, 共同支撑 P5 外部协同处理变量的稳健性叙事。本列作为稳健性臂不进主回归核心 RHS, 而与共识 collab_frac 并排, 用以证明主结论不被单一厂商在收窄语境下的判定习惯所驱动。

## VAR: gpt54nano_collab_frac_ss

【变体差分】
本列取 GPT-5.4-nano 单一模型、ss 轨的外部协同占比。轨道侧: ss 轨输入 content_ss = 标题 prepend + 银行与金科同句共现句 ±窗口, 是三轨中语义最严的一轨, 要求银行与金融科技词在同一句里共现, 最能锁定"该银行确在谈金科协同"的强信号; 无同句共现时回退全文 body 并置 ss_is_fallback 为真, 镜像 ctx 回退语义、共享 n_articles 分母口径; 上游金科 AC 自动机为空则 ss_is_fallback 全真优雅降级。按 full-only 口径, ss 为 conditional-on-full 测度轨, verified 掩码与分母 (per-model 版 n_articles_llm_valid_ss) 按 ss 轨自身计数。模型侧同 gpt54nano 其余两列: 经 OpenLux 网关、单厂商、不折叠投票。相对 gpt54nano 的 full/ctx 列, 差分仅在文本轨; 相对 deepseekv4/gemini31 的 ss 列, 差分在厂商。三轨与三厂商全部 co-equal、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。开发样本早期试跑 T=2 上 ss 轨常零方差退化, 属预期。作为 GPT 单厂商在最严同句共现判据下的视角, 本列未回退的分子对应媒体明确把该银行与金融科技并置叙述的报道, 是三轨中最贴近强证据口径的一轨, 但因判据严格触发大量回退, 有效方差更依赖生产语料规模。解读时宜与 gpt54nano 的 full/ctx 列做 full→ctx→ss 梯度对读: 方向沿由宽到严的语义过滤保持一致, 则协同信号稳健。本列与 deepseekv4、gemini31 的 ss 列跨厂商互证, 三家一致方增强处理变量在最严口径下的效度, 共同服务于 P5 开放式创新处理变量的三角验证。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Törnberg, P. (2024). Large language models outperform expert coders and supervised classifiers at annotating political social media messages. Social Science Computer Review, 43(6), 1181-1195. https://doi.org/10.1177/08944393241286471
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Lerner, J., Seru, A., Short, N., & Sun, Y. (2024). Financial innovation in the twenty-first century: Evidence from US patents. Journal of Political Economy, 132(5), 1391-1449. https://doi.org/10.1086/727712
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131-150. https://doi.org/10.1002/smj.507
Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. Research Policy, 31(4), 477-492. https://doi.org/10.1016/S0048-7333(01)00120-2
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
<!-- rendered-citations:end -->
