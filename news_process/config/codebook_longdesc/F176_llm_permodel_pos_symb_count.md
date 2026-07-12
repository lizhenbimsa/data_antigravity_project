---
family_id: F176
columns:
- deepseekv4_pos_symb_count_ctx
- deepseekv4_pos_symb_count_full
- deepseekv4_pos_symb_count_ss
- gemini31_pos_symb_count_ctx
- gemini31_pos_symb_count_full
- gemini31_pos_symb_count_ss
- gpt54nano_pos_symb_count_ctx
- gpt54nano_pos_symb_count_full
- gpt54nano_pos_symb_count_ss
unit: 篇数 (bank-year 计数, 非负整数)
formula: "{llm}_pos_symb_count{track} = Σ_articles [ (({llm}_score{track} > 0)) ∧ (innovation_substantiveness_full == '象征性') ]; 逐篇指示 _is_{llm}_pos_symb{track} 由 runner 构造, encode 按 bank-year sum 聚合"
producer: news_process/pipeline/panel/runner.py (逐篇 _is_{llm}_pos_symb 指示) ; news_process/pipeline/panel/encode.py (bank-year sum 聚合)
upstream:
- 21_tone_llms.parquet ({llm}_score{track} 单模型三轨语调分, innovation_substantiveness_full 实质/象征分类)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
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
  venue: FEDS Working Paper No. 2026-020
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
- doi: 10.2139/ssrn.4412788
  type: wp
  authors: Lopez-Lira, A., & Tang, Y.
  year: 2023
  title: "Can ChatGPT forecast stock price movements? Return predictability and large language models"
  venue: SSRN Working Paper No. 4412788
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  pages_or_artno: 102776
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: "The symbolic management of stockholders: Corporate governance reforms and shareholder reactions"
  venue: Administrative Science Quarterly
  vol: 43
  issue: 1
  pages_or_artno: 127-153
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"正面且象征性"的银行金融科技报道在银行-年层面的计数, 且这一计数按三家大模型 (deepseekv4、gemini31、gpt54nano) 各自单独统计, 再按三条文本轨 (full / ctx / ss) 各自单独统计, 共九列。所谓"象征性", 沿用 Westphal 与 Zajac (1998) 在公司治理研究中确立的实质-象征二元框架: 一篇报道若只在话语层面宣示某种金融科技姿态、却缺乏可核验的落地内容 (投入、系统上线、产品交付、组织变革), 即被判为象征性 (decoupling / cheap talk); 反之若有实体证据支撑则判为实质性。把"象征性"与"正面语调"两个条件相乘, 得到的正是"银行在媒体上被正面报道、但报道内容偏空谈"的那一类篇章, 它是下游"洗稿率 / 象征化占比"这一构念 (Bingler 等 2022 意义上的 cheap talk 与 cherry-picking) 的分子来源。白话说: 这九个数就是"一家银行这一年里, 被某个模型判成'又正面、又是空谈'的新闻有几篇"。

【方法学与计算】
逐篇指示列 _is_{llm}_pos_symb{track} 在 pipeline/panel/runner.py 的洗稿率块中构造, 其正面条件取单模型三轨语调分 {llm}_score{track} 严格大于零 (per-model 分值为 nullable 整型, 缺席/平局/拒绝的 NaN 经 fillna(0) 折为非正, 恒不入分子); 其象征条件取文章级 innovation_substantiveness_full 是否等于"象征性"。此处有一处承重口径: 象征-实质判定固定取 full 轨 (innovation_substantiveness_full), 三条轨的差异只体现在正面语调这一半的门, 象征这一半的门三轨共用同一 full 分类, 不随轨切换; 因此 ctx 与 ss 列并非在 ctx/ss 文本上重判象征性, 而是"用 ctx/ss 轨的正面判定 × full 轨的象征判定"的乘积。构造好的逐篇 0/1 指示进入 pipeline/panel/encode.py 洗稿率聚合块 (代码 K 段), 以 bank-year 求和 (sum) 得到本家族九列的面板计数。计数落在留篇门控 (full-only, 2026-06-29) 界定的宇宙内: 是否算作一篇银行金融科技报道只看 llm_verified_full, ctx 与 ss 是 conditional-on-full 的子集轨, 因此三轨计数天然满足 ss ⊆ ctx 语料范围 ⊆ full 留篇集这一嵌套关系 (per-track 分子照各轨语调分独立计)。三家模型的路由各不相同: deepseekv4 为 DeepSeek-V4 Flash, 直连 api.deepseek.com; gemini31 为 gemini-3.1-flash-lite、gpt54nano 为 gpt-5.4-nano, 两家经 yunwu 网关。三家在 temperature=0、prompt v8 冻结下确定性推理, 缓存命中即可零成本复现。

【文献定位】
本家族坐落在"用大模型对金融文本做标注、并把标注计数进面板"这一新兴测量传统上。Loughran 与 McDonald (2016) 系统综述了会计金融中的文本分析测度, 确立了正负极性计数类指标的规范; 而把生成式大模型直接当作标注器的可行性与陷阱, de Kok (2025) 在 Management Science 上给出了操作指南 (temperature=0、prompt 冻结、缓存范式), 与本流水线的确定性锚点一致。将同一构念交由多家模型各自标注、以此做交叉验证与稳健性, 是 Carlson 与 Burbano (2026) 与 Hansen (2026) 反复强调的做法 — 单一模型的标注可能带有厂商特异的系统偏差, 故三家 per-model 计数并排呈现。象征-实质这一被计数的属性本身源自 Westphal 与 Zajac (1998) 的象征性管理理论, 并在气候披露语境下被 Bingler 等 (2022) 复活为 cheap talk 的机器度量; Lan 等 (2025) 与 Lopez-Lira、Tang (2023) 则分别提供了中文金融细粒度情感与大模型金融文本分析的可复现证据, 支撑正面语调这一半门的构造效度。⚠ 铁律: 三家模型各自 just-identified 并排、三条轨各自 just-identified 并排, 彼此互为稳健性、不分主次, 严禁把不同模型或不同轨的计数混进同一 over-identified 的 Hansen J 检验。

## VAR: deepseekv4_pos_symb_count_ctx

【变体差分】
本列取 DeepSeek-V4 Flash (deepseekv4, 直连 api.deepseek.com) 在 ctx 轨的正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ctx 轨文本 content_ctx = 标题 prepend + 含目标银行句的上下文窗口 (银行实体邻近片段, 对应 Hassan 2019 式 proximity 口径), 相较 full 轨剔除了与目标银行无关的段落, 因此正面语调门 deepseekv4_score_ctx > 0 是在"聚焦银行的窄语境"上判定的; 而象征这一半仍取 innovation_substantiveness_full (象征判定不随轨切换, 全轨共用 full 分类)。与同族 deepseekv4_pos_symb_count_full 的差异纯在正面门的文本轨: ctx 因语料更窄, 计数一般不超过 full 列。与另外两家模型 (gemini31 / gpt54nano) 的同轨列并排构成跨厂商稳健性: 三家 per-model 计数各自 just-identified, 互为稳健性不分主次, 禁混同一 over-identified Hansen J。本列落在 full-only 留篇门控界定的宇宙内, ctx 为 conditional-on-full 子集轨, 缺 deepseekv4_score_ctx 时该篇不入分子 (NaN 折非正), 不借 full 分值填补。

在下游用法上, 本列充当"正面且象征"的分子, 与同域分母 _svd_deepseekv4_pos_ctx (正面且实质性已测量的篇数) 相除即得该模型 ctx 轨的象征化占比 (洗稿率); 该分母刻意只数 innovation_substantiveness 判出结果的篇, 以免象征-实质分类失败越多、占比被系统性稀释下偏。需强调这是 Loughran 与 McDonald (2016) 式的计数型测度而非可加分解: 三家模型的计数高度共线但各自反映厂商特异的正面阈与实质判读, 因此本列只作跨模型稳健性的一条腿, 报告时与其它模型/轨并排呈现相关而不并入同一结构式。ctx 轨相较 full 剔除了无关段落, 更贴近 Bingler 等 (2022) cheap talk 度量对"聚焦目标主体"的语境要求。

## VAR: deepseekv4_pos_symb_count_full

【变体差分】
本列取 DeepSeek-V4 Flash (deepseekv4) 在 full 轨的正面判定与 full 轨的象征判定相乘后的 bank-year 计数, 是本家族中 deepseekv4 一支的基准轨。full 轨文本 content_full = 标题 prepend + 全文正文, 是留篇门控 (2026-06-29, full-only) 的判定轨: 一篇报道是否算银行金融科技报道以 llm_verified_full 为准, 故本列的行宇宙即 full 留篇集本身, 而非其子集。正面门 deepseekv4_score_full > 0 在完整正文上判定, 象征门取 innovation_substantiveness_full, 两半同轨、语义最自洽, 是三轨中信息最全、噪声也最全的一轨。相较 ctx / ss 两轨, 本列计数通常最大 (语料最宽)。与 gemini31_pos_symb_count_full、gpt54nano_pos_symb_count_full 并排即跨厂商 per-model 稳健性梯子, 三家各自 just-identified、互为稳健性不分主次, 禁混同一 over-identified Hansen J。deepseekv4_score_full 缺席 (模型未返回/平局/拒绝) 时经 fillna(0) 折为非正, 该篇不计入分子。

作为基准轨, 本列的下游分母是同域的 _svd_deepseekv4_pos_full (正面且实质性已测量), 两者相除得 DeepSeek 一支 full 轨的洗稿率。DeepSeek-V4 Flash 独立于 yunwu 端点直连 api.deepseek.com, 其确定性由 temperature=0 与 prompt v8 冻结、缓存命中共同保证, 缓存三轨零 miss 时可离线零成本复现, 符合 de Kok (2025) 对生成式标注可复现性的操作要求。把象征-实质属性交由大模型判读、再以计数进面板, 其效度依赖标注一致性; Carlson 与 Burbano (2026)、Hansen (2026) 均主张以多模型交叉核验降低单一标注器的系统偏差, 这正是本家族保留三家 per-model 并排的方法学理由。本列与另两家的 full 列共同构成跨模型稳健性梯子的基准轨对照。

## VAR: deepseekv4_pos_symb_count_ss

【变体差分】
本列取 DeepSeek-V4 Flash (deepseekv4) 在 ss 轨的正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ss 轨文本 content_ss = 标题 prepend + 同句内同时含目标银行∧金融科技词的句子及其 ±窗口 (银行与金科同句共现片段), 是三轨中语境最严的一轨; 当某篇不存在银行∧金科同句共现时, ss 镜像 ctx 的回退语义、退回全文 body 并置 ss_is_fallback=True (与 ctx 回退口径一致)。因此本列正面门 deepseekv4_score_ss > 0 是在"银行与金科真正同句"的最窄语料上判定的, 象征门仍取 innovation_substantiveness_full。与同族 full / ctx 列的差异纯在正面门的文本轨: ss 语料最窄, 计数一般最小; 回退篇则等价 ctx/全文口径。三轨互为稳健性、各自 just-identified, 禁混同一 over-identified Hansen J; 本列亦落在 full-only 留篇宇宙内, 为 conditional-on-full 子集轨。deepseekv4_score_ss 缺席折非正不入分子。

ss 轨的构造意图是把语境收到"银行与金融科技真正同句"的最严口径, 以此检验象征化占比是否对语境窗口的选择稳健: 若结论在 full、ctx、ss 三轨一致, 则不由某一特定语境切法驱动。回退语义须留意 — 无同句共现的篇被退回全文 body 并标记 ss_is_fallback=True, 这类篇在正面门上等价 full 口径, 故 ss 计数并非严格小于 ctx。下游以 _svd_deepseekv4_pos_ss 为同域分母得该轨洗稿率。三轨互为稳健性、各自 just-identified 并排, 严禁把不同轨的计数混进同一 over-identified Hansen J; 象征这一半固定取 full 分类, 故 ss 列不在 ss 文本上重判象征性, 仅以 ss 轨正面判定与 full 象征判定相乘。

## VAR: gemini31_pos_symb_count_ctx

【变体差分】
本列取 gemini-3.1-flash-lite (gemini31, 经 yunwu 网关) 在 ctx 轨的正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ctx 轨 content_ctx = 标题 prepend + 目标银行句上下文窗口, 正面门 gemini31_score_ctx > 0 在聚焦银行的窄语境上判定, 象征门取 innovation_substantiveness_full (全轨共用 full 象征分类, 不随轨切换)。与 gemini31_pos_symb_count_full 的差异纯在正面门文本轨 (ctx 语料更窄, 计数一般不超过 full); 与 deepseekv4 / gpt54nano 的同轨列并排构成跨厂商 per-model 稳健性。gemini31 与 gpt54nano 同经 yunwu 路由、但为不同厂商不同模型, deepseekv4 则直连独立端点; 三家各自 just-identified、互为稳健性不分主次, 禁混同一 over-identified Hansen J。本列落在 full-only 留篇宇宙内, ctx 为 conditional-on-full 子集轨, gemini31_score_ctx 缺席经 fillna(0) 折非正、该篇不入分子, 不借他轨分值填补。象征这一半固定取 full 轨, 故 ctx 列并非在 ctx 文本上重判象征性。

gemini31 的正面阈判定基于其厂商特有的对齐与训练语料, 相较另两家可能给出系统性偏移的计数; 这正是跨模型并排要暴露的稳健性维度, 而非需要抹平的噪声。下游以同域分母 _svd_gemini31_pos_ctx (正面且实质性已测量) 相除得该模型 ctx 轨洗稿率。本列亦服务于跨模型一致性诊断 (如逐模型 κ / α 一致性与跨模型 FWER 稳健性), 其中三家 per-model 计数作为同一象征化构念的替代测量并排, 而不并入同一结构式估计。ctx 语料聚焦目标银行, 更贴合 Bingler 等 (2022) 对 cheap talk 度量语境的要求, 与 full 轨形成语境宽窄的对照臂。

## VAR: gemini31_pos_symb_count_full

【变体差分】
本列取 gemini-3.1-flash-lite (gemini31, 经 yunwu) 在 full 轨的正面判定与 full 轨的象征判定相乘后的 bank-year 计数, 是 gemini31 一支的基准轨。full 轨 content_full = 标题 prepend + 全文正文, 与留篇门控同轨 (full-only, 2026-06-29), 故本列行宇宙即 full 留篇集。正面门 gemini31_score_full > 0 在完整正文上判定, 象征门取 innovation_substantiveness_full, 两半同轨、语义最自洽, 三轨中信息最全。相较 ctx / ss 两轨语料更宽, 计数通常最大。与 deepseekv4_pos_symb_count_full、gpt54nano_pos_symb_count_full 并排即跨厂商 per-model 稳健性梯子, 三家各自 just-identified、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。gemini31 因厂商与训练语料不同于另两家, 其正面阈判定与 innovation_substantiveness_full 的组合可能给出与它家系统性偏移的计数, 这正是跨模型并排要暴露的稳健性维度。gemini31_score_full 缺席经 fillna(0) 折非正、不计入分子。

作为 gemini31 一支的基准轨, 本列下游以同域分母 _svd_gemini31_pos_full 相除得该模型 full 轨洗稿率。gemini31 经 yunwu 网关调用 gemini-3.1-flash-lite, 与 gpt54nano 共用路由但分属不同厂商不同模型, 因此二者计数的差异反映的是模型本身而非网关。把象征-实质属性交由大模型判读再计数进面板, 其构造效度依赖标注一致性与可复现性: 本流水线以 temperature=0、prompt v8 冻结、缓存命中锚定确定性, 符合 de Kok (2025) 与 Lopez-Lira、Tang (2023) 对生成式标注的可复现要求。本列与 deepseekv4、gpt54nano 的 full 列并排, 是跨模型稳健性梯子的基准轨对照, 三家各自 just-identified、互为稳健性不分主次。

## VAR: gemini31_pos_symb_count_ss

【变体差分】
本列取 gemini-3.1-flash-lite (gemini31, 经 yunwu) 在 ss 轨的正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ss 轨 content_ss = 标题 prepend + 银行∧金科同句共现片段及 ±窗口, 是语境最严的一轨; 无同句共现时镜像 ctx 回退全文 body 并置 ss_is_fallback=True。正面门 gemini31_score_ss > 0 在最窄语料上判定, 象征门仍取 innovation_substantiveness_full。与同族 gemini31 的 full / ctx 列差异纯在正面门文本轨: ss 语料最窄、计数一般最小, 回退篇等价 ctx/全文口径。与 deepseekv4 / gpt54nano 的同轨 ss 列并排为跨厂商稳健性。三轨与三家模型两个维度均"各自 just-identified 并排、互为稳健性不分主次", 禁混同一 over-identified Hansen J。本列落在 full-only 留篇宇宙内, 为 conditional-on-full 子集轨; gemini31_score_ss 缺席经 fillna(0) 折非正、不入分子; 象征这一半固定取 full 轨, 故 ss 列不在 ss 文本上重判象征性, 仅用 ss 轨正面判定与 full 象征判定相乘。

ss 轨把语境收到银行与金融科技同句共现的最严口径, 用以检验 gemini31 一支的象征化占比是否对语境窗口稳健。回退篇 (无同句共现) 退回全文 body 并置 ss_is_fallback=True, 正面门在这些篇上等价 full 口径, 故 ss 计数不必严格小于 ctx。下游以同域分母 _svd_gemini31_pos_ss 相除得该模型 ss 轨洗稿率。三轨与三家模型两维度均"各自 just-identified 并排、互为稳健性不分主次", 严禁把不同轨或不同模型的计数混进同一 over-identified Hansen J; 象征这一半固定取 full 分类保证三轨象征判据一致, 只让正面语调这一半随轨变化, 使三轨差异可干净归因于正面判定的语境宽窄。

## VAR: gpt54nano_pos_symb_count_ctx

【变体差分】
本列取 gpt-5.4-nano (gpt54nano, 经 yunwu 网关) 在 ctx 轨的正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ctx 轨 content_ctx = 标题 prepend + 目标银行句上下文窗口, 正面门 gpt54nano_score_ctx > 0 在聚焦银行的窄语境上判定, 象征门取 innovation_substantiveness_full (全轨共用 full 象征分类)。与 gpt54nano_pos_symb_count_full 的差异纯在正面门文本轨 (ctx 语料更窄, 计数一般不超过 full); 与 deepseekv4 / gemini31 的同轨列并排构成跨厂商 per-model 稳健性。gpt54nano 与 gemini31 虽同走 yunwu 路由, 但分属不同厂商的不同模型, 三家 per-model 计数各自 just-identified、互为稳健性不分主次, 禁混同一 over-identified Hansen J。本列落在 full-only 留篇宇宙内, ctx 为 conditional-on-full 子集轨; gpt54nano_score_ctx 缺席经 fillna(0) 折非正、该篇不入分子, 不借他轨分值填补; 象征这一半固定取 full 轨, 故本列不在 ctx 文本上重判象征性。

gpt54nano 作为轻量 nano 级模型, 其正面阈判定相较大模型可能更保守或更宽松, 因而与另两家的同轨计数产生系统偏移; 这一偏移正是跨模型稳健性要暴露而非抹平的信息。下游以同域分母 _svd_gpt54nano_pos_ctx (正面且实质性已测量) 相除得该模型 ctx 轨洗稿率, 分母只数象征-实质判出结果的篇以防分类失败稀释占比。三家 per-model 计数作为同一象征化构念的替代测量并排, 服务于跨模型一致性诊断与稳健性, 相关而不并入同一结构式。ctx 语料聚焦目标银行, 相较 full 剔除无关段落, 与 full 轨形成语境宽窄的对照臂, 贴合 Bingler 等 (2022) cheap talk 度量对语境的要求。

## VAR: gpt54nano_pos_symb_count_full

【变体差分】
本列取 gpt-5.4-nano (gpt54nano, 经 yunwu) 在 full 轨的正面判定与 full 轨的象征判定相乘后的 bank-year 计数, 是 gpt54nano 一支的基准轨。full 轨 content_full = 标题 prepend + 全文正文, 与留篇门控同轨 (full-only, 2026-06-29), 本列行宇宙即 full 留篇集。正面门 gpt54nano_score_full > 0 在完整正文上判定, 象征门取 innovation_substantiveness_full, 两半同轨、语义最自洽, 三轨中信息最全、计数通常最大。与 deepseekv4_pos_symb_count_full、gemini31_pos_symb_count_full 并排即跨厂商 per-model 稳健性梯子, 三家各自 just-identified、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。gpt54nano 作为轻量 nano 级模型, 其正面阈判定与 innovation_substantiveness_full 的组合相较大模型可能有系统偏移, 正是跨模型并排要暴露的维度。gpt54nano_score_full 缺席 (未返回/平局/拒绝) 经 fillna(0) 折非正, 不计入分子。

作为 gpt54nano 一支的基准轨, 本列下游以同域分母 _svd_gpt54nano_pos_full 相除得该模型 full 轨洗稿率。gpt54nano 经 yunwu 网关调用 gpt-5.4-nano, 确定性由 temperature=0、prompt v8 冻结与缓存命中共同保证, 缓存三轨零 miss 时可离线零成本复现。把象征-实质属性交由大模型判读再计数进面板, 效度依赖标注一致性; Carlson 与 Burbano (2026)、Hansen (2026) 主张以多模型交叉核验降低单一标注器的系统偏差, 支撑本家族保留三家 per-model 并排的设计。本列与 deepseekv4、gemini31 的 full 列共同构成跨模型稳健性梯子的基准轨对照, 三家各自 just-identified、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: gpt54nano_pos_symb_count_ss

【变体差分】
本列取 gpt-5.4-nano (gpt54nano, 经 yunwu) 在 ss 轨的正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ss 轨 content_ss = 标题 prepend + 银行∧金科同句共现片段及 ±窗口, 是语境最严的一轨; 无同句共现时镜像 ctx 回退全文 body 并置 ss_is_fallback=True。正面门 gpt54nano_score_ss > 0 在最窄语料上判定, 象征门仍取 innovation_substantiveness_full。与同族 gpt54nano 的 full / ctx 列差异纯在正面门文本轨: ss 语料最窄、计数一般最小, 回退篇等价 ctx/全文口径。与 deepseekv4 / gemini31 的同轨 ss 列并排为跨厂商稳健性。三轨与三家模型两维度均"各自 just-identified 并排、互为稳健性不分主次", 禁混同一 over-identified Hansen J。本列落在 full-only 留篇宇宙内, 为 conditional-on-full 子集轨; gpt54nano_score_ss 缺席经 fillna(0) 折非正、不入分子; 象征这一半固定取 full 轨, 故 ss 列不在 ss 文本上重判象征性, 仅用 ss 轨正面判定与 full 象征判定相乘得计数。

ss 轨把语境收到银行与金融科技同句共现的最严口径, 用以检验 gpt54nano 一支的象征化占比是否对语境窗口稳健。回退篇 (无同句共现) 退回全文 body 并置 ss_is_fallback=True, 正面门在这些篇上等价 full 口径, 故 ss 计数不必严格小于 ctx。下游以同域分母 _svd_gpt54nano_pos_ss 相除得该模型 ss 轨洗稿率。三轨与三家模型两维度均"各自 just-identified 并排、互为稳健性不分主次", 严禁把不同轨或不同模型的计数混进同一 over-identified Hansen J。象征这一半固定取 full 分类保证三轨象征判据一致, 只让正面语调这一半随轨变化, 使三轨差异可干净归因于正面判定的语境宽窄, 便于把象征化占比对语境口径的稳健性判读得清清楚楚。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Hansen, A. L. (2026). Validating large language model annotations. FEDS Working Paper No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. SSRN Working Paper No. 4412788 [Working Paper]. https://doi.org/10.2139/ssrn.4412788
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
<!-- rendered-citations:end -->
