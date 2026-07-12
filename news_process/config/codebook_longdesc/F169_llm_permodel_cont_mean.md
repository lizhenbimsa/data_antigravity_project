---
family_id: F169
columns:
- deepseekv4_cont_mean_app_ctx
- deepseekv4_cont_mean_app_full
- deepseekv4_cont_mean_app_ss
- deepseekv4_cont_mean_ctx
- deepseekv4_cont_mean_full
- deepseekv4_cont_mean_ss
- deepseekv4_cont_mean_tech_ctx
- deepseekv4_cont_mean_tech_full
- deepseekv4_cont_mean_tech_ss
- gemini31_cont_mean_app_ctx
- gemini31_cont_mean_app_full
- gemini31_cont_mean_app_ss
- gemini31_cont_mean_ctx
- gemini31_cont_mean_full
- gemini31_cont_mean_ss
- gemini31_cont_mean_tech_ctx
- gemini31_cont_mean_tech_full
- gemini31_cont_mean_tech_ss
- gpt54nano_cont_mean_app_ctx
- gpt54nano_cont_mean_app_full
- gpt54nano_cont_mean_app_ss
- gpt54nano_cont_mean_ctx
- gpt54nano_cont_mean_full
- gpt54nano_cont_mean_ss
- gpt54nano_cont_mean_tech_ctx
- gpt54nano_cont_mean_tech_full
- gpt54nano_cont_mean_tech_ss
unit: 连续情感分均值 (无量纲, 值域 [-1, +1])
formula: "{model}_cont_mean{variant}{track} = mean over retained articles of {model}_cont{track}; {model}_cont = P(正面) - P(负面), 主类概率 = verbalized confidence c, 其余两类 (1-c)/2 (Logit-to-Score); variant ∈ {∅, _app (locus==应用场景), _tech (locus==底层技术)}, locus 判据取自 innovation_locus_full (full-only 单源)"
producer: news_process/pipeline/panel/encode.py::build_aggregation_dict (无后缀 9 列 {model}_cont_mean{track}) ; news_process/pipeline/panel/encode.py::aggregate_panel (18 个 _app/_tech 后缀列, cat_mapping 内联 cat_agg 循环) ; news_process/pipeline/sentiment/tone_llms.py::compute_prob_score (文章级连续分)
upstream:
- 21_tone_llms.parquet (article-level {model}_cont{track}, innovation_locus_full)
- 40_panel_yearly.parquet
citations:
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: "Validating large language model annotations"
  venue: FEDS Working Paper
  pages_or_artno: "2026-020"
- doi: 10.1146/annurev-economics-120925-105620
  type: journal
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2026
  title: "Large language models: An applied econometric framework"
  venue: Annual Review of Economics
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
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
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
本家族刻画的是每一家大语言模型 (LLM) 各自输出的连续情感分在 bank-year 层面的均值, 属于情感三法中 LLM 一支的「逐模型连续测度」轨。与离散多数投票语调 (llm_vote_tone) 不同, 本家族不把三家模型的判定合并为共识, 而是让每一家模型的连续得分独立成列, 从而把「同一构念、三家独立测量」的三角验证结构完整暴露在面板上。所谓连续情感分, 指对某一模型给出的「正面/中性/负面」三分类标签, 结合该模型自报的语气置信度 (verbalized confidence), 经 Logit-to-Score 概率映射折算成一个位于闭区间负一到正一之间的实数: 分数越接近正一表示语气越正面, 越接近负一越负面, 零表示中性或高度不确定。这一构造让原本离散的分类输出获得强度信息, 使得同一篇报道「偏正面且很有把握」与「偏正面但不确定」得以区分, 契合金融计量对连续因变量的需要。三家模型分别为 DeepSeek-V4 Flash (直连 api.deepseek.com)、Gemini-3.1-flash-lite (经 yunwu 路由) 与 GPT-5.4-nano (经 yunwu 路由); 它们是情感 LLM 投票的三名成员, 与嵌入模型、词典法、BERT 三法在测度上彼此无关。文章级连续分列名为 短名加 cont 加轨道后缀, 由阶段 21 tone_llms 产出; bank-year 聚合则在 encode 的聚合字典里以 mean 归并, 得到本家族的 cont_mean 列。

【方法学与计算】
面板聚合遵循 Tetlock (2007) 以来的媒体情感均值化范式: 对某一 bank-year 内被保留的全部报道, 取该模型文章级连续分的算术平均。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否算作「银行金科报道」只看 full 轨的 LLM 语义精筛结果, 因此三轨行宇宙同为 full 留篇集, ctx 与 ss 轨是 conditional-on-full 的稳健性测度, 各轨的 cont 列仍逐轨独立计算。三轨输入的语义为: full 轨取标题拼接全文正文; ctx 轨取标题加含目标银行句的上下文窗口 (Hassan 2019 邻近性); ss 轨取标题加银行与金科词同句共现的窗口, 若某篇无此共现则镜像 ctx 回退为全文正文并置 ss_is_fallback 为真, 与 full 共享篇数分母。本家族除无后缀的全样本变体外, 另设两个按创新落点 (innovation locus) 划分的条件子样变体: app 变体只在 innovation_locus_full 等于「应用场景」的报道内取均值, tech 变体只在等于「底层技术」的报道内取均值。关键口径: 落点判据取自 innovation_locus_full 单一事实源, 属 full-only 分类, 即使 app/tech 变体挂接的是 ctx 或 ss 轨的连续分, 划分子样所用的落点仍由 full 轨判定, 不随情感轨切换。连续分本身由 compute_prob_score 依「主类概率等于自报置信度、其余两类均分剩余概率」的最大熵映射折算 (Jaynes 原理), 数值区间恒在负一到正一之间。逐模型独立降级: 某一模型在某篇缺席时仅使该模型自身族列受影响, 不牵连其余两家, 这与 co-primary 嵌入的 both-or-neither 强绑定截然不同。

【文献定位】
本家族的方法学根基横跨三条脉络。其一是媒体情感与资产定价的经典范式, Tetlock (2007) 发表于 Journal of Finance 的研究奠定了把媒体语气均值化为面板变量、进而解释市场行为的做法, 本家族的 bank-year 均值化正是该范式在银行金科语境下的延续; 与之并列的还有词典法与机器学习法之争, Frankel、Jennings 与 Lee (2022) 在 Management Science 上系统比较了披露情感的机器学习与词典测度, 为本项目情感三法并置提供了方法学正当性。其二是以生成式 LLM 做文本标注与情感抽取的可复现方法学: de Kok (2025) 与 Siano (2025) 均在 Management Science 上讨论了如何在会计与金融研究中规范化地使用生成式 LLM (温度置零、提示词冻结、缓存复现), 直接对应本项目对 prompt 版本与温度的字节级冻结; Gilardi、Alizadeh 与 Kubli (2023) 在 PNAS 上证明 ChatGPT 在文本标注任务上可超越众包工人, 为 LLM 标注的信度背书; Huang、Wang 与 Yang (2023) 的 FinBERT 则代表金融文本领域专用大模型一支, 与本家族通用 LLM 逐模型测度互为参照。其三是把 LLM 输出当作生成回归元 (generated regressor) 的计量框架, Ludwig、Mullainathan 与 Rambachan (2026) 在 Annual Review of Economics 提出了将 LLM 标注纳入计量推断的框架, Hansen (2026) 的 FEDS 工作论文则给出无金标准时以一致性系数验证 LLM 标注的设计; 二者共同支撑本家族逐模型并置、以模型间一致性度量稳健性的做法。铁律: 三家模型、三条轨道、三种落点子样的各连续分均是同一构念的独立测量, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把它们混入同一个 over-identified 的 Hansen J 过度识别检验。

## VAR: deepseekv4_cont_mean_app_ctx

【变体差分】
本列取 DeepSeek-V4 Flash (直连 api.deepseek.com) 一家模型的连续情感分, 在 ctx 轨 (标题加目标银行句上下文窗口, Hassan 2019 邻近性) 上先算文章级连续分, 再在 innovation_locus_full 等于「应用场景」的 app 子样内取 bank-year 均值。在计算机制上, app/tech 两变体与无后缀变体共用同一文章级源列 deepseekv4_cont_ctx, 三者的区别不在源列而在样本子集: app 变体在聚合前先按 innovation_locus_full 等于应用场景过滤出 df_cat 再取 mean, 分母为该子样内有效连续分的篇数; 若该 bank-year 应用场景子样为空则优雅置空而非报错。与同模型离散列 deepseekv4_tone_app_ctx 相比, 后者是三分类标签的计数口径均值, 本列承载 DeepSeek 自报置信度的强度信息, 二者 co-equal、互为稳健不分主次。三处坐标须同时读: 模型 = DeepSeek 单家 (非投票共识); 轨道 = ctx (conditional-on-full 稳健轨, 行宇宙仍为 full 留篇集之子集, 留篇门控恒取 full-only 口径); 落点子样 = app, 其判据 innovation_locus_full 属 full-only 单源, 即便本列挂接 ctx 轨情感, 划分应用场景与底层技术两子样所用的落点仍由 full 轨判定, 不随情感轨切换。连续分本身由标签乘自报置信度经 Logit-to-Score 概率映射折算至负一到正一。本列与同格 tech 变体、无后缀全样本变体, 以及 gemini31/gpt54nano 两家的对应列, 均是同一构念的独立测量, 各自 just-identified 并排、互为稳健、不分主次, 严禁混入同一 over-identified Hansen J。DeepSeek 缺席仅掉自身族列, 不连坐其余两家。

## VAR: deepseekv4_cont_mean_app_full

【变体差分】
本列取 DeepSeek-V4 Flash 单家模型, 在 full 轨 (标题拼接全文正文) 上算文章级连续分, 并在 innovation_locus_full 等于「应用场景」的 app 子样内取 bank-year 均值。本列与无后缀及 tech 变体共用文章级源列 deepseekv4_cont_full, 区别仅在样本子集: 聚合前先按 innovation_locus_full 等于应用场景过滤出 df_cat 再取 mean, 分母为该子样内有效连续分的篇数, 子样为空则优雅置空而非报错。本列供 bank_fintech_tone (P1) 语调分析与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量。该列在规格稳健性并排中仅作 just-identified 单列, 不进入任何过度识别检验。full 轨是留篇门控的判定轨: 一篇报道是否算银行金科报道只看 full 轨的 LLM 语义精筛, 因此本列的行宇宙即该 bank-year 的 full 留篇全集在应用场景落点上的子集, 落点与情感同源于 full, 是三轨中口径最直接的一格。连续分为标签结合 DeepSeek 自报语气置信度经最大熵概率映射折算的负一到正一实数, 强度信息由置信度承载。与 tech 落点子样相比, 本列只纳入被判为「应用场景」类的报道, 度量的是银行在金融科技应用层 (场景落地、产品服务) 相关报道上 DeepSeek 感知到的连续语气; 与无后缀全样本列相比, 本列是落点条件化的稳健切片。本列与 gemini31/gpt54nano 的同格列、与同模型 tech/无后缀变体, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J; DeepSeek 独立降级。

## VAR: deepseekv4_cont_mean_app_ss

【变体差分】
本列取 DeepSeek-V4 Flash 单家模型, 在 ss 轨上算文章级连续分, 并在 innovation_locus_full 等于「应用场景」的 app 子样内取 bank-year 均值。本列与无后缀及 tech 变体共用文章级源列 deepseekv4_cont_ss, 区别仅在样本子集: 聚合前先按 innovation_locus_full 等于应用场景过滤出 df_cat 再取 mean, 分母为该子样内有效连续分篇数, 子样为空则优雅置空而非报错。连续分随三分类标签与 DeepSeek 自报置信度确定性折算, 缓存命中键为 prompt 版本 v8 与温度 0.0, 三轨全命中时可在离线模式下零成本字节级复现。该列在规格稳健性并排中仅作 just-identified 单列。ss 轨输入为标题加银行与金科词同句共现窗口, 属最严格的语义共现轨; 若某篇不存在此种同句共现, 则该篇 ss 文本镜像 ctx 回退为全文正文并置 ss_is_fallback 为真, 与 full 共享篇数分母, 故 ss 轨在共现稀疏时会优雅退化为近似全文口径。留篇门控仍取 full-only, ss 是 conditional-on-full 的稳健轨。落点 app 的判据来自 full-only 的 innovation_locus_full, 即划分应用场景子样所依据的落点由 full 轨判定, 不随 ss 情感轨切换。本列度量的是应用场景类报道中、以银行金科同句语境为锚时 DeepSeek 感知的连续语气均值。与同模型 full/ctx 的 app 变体、与 tech 及无后缀变体, 以及其余两家模型的对应列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J。

## VAR: deepseekv4_cont_mean_ctx

【变体差分】
本列是 DeepSeek-V4 Flash 单家模型在 ctx 轨上的无后缀全样本连续分均值, 即不做落点子样切分、纳入该 bank-year 全部 full 留篇的报道 (但连续分取自 ctx 轨文本)。本无后缀列由 encode 的 build_aggregation_dict 以源列 deepseekv4_cont_ctx 配 mean 归并该 bank-year 全部 full 留篇, 不按落点过滤; valid_agg 按源列存在性守卫, 该模型该轨缺席时优雅置空而非报错。本列供 bank_fintech_tone (P1) 语调分析与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量。ctx 轨输入为标题加含目标银行句的上下文窗口 (Hassan 2019 邻近性), 相较 full 轨的全文, 它把语义焦点收窄到目标银行邻近句, 是 conditional-on-full 的首要稳健轨。无后缀意味着这是本模型 ctx 轨的落点无关基准列, 与 app/tech 两个落点条件化切片形成「全样本对场景/技术子样」的对照。连续分为标签乘 DeepSeek 自报置信度经 Logit-to-Score 映射至负一到正一。本列与同模型 full/ss 无后缀列构成三轨稳健并排, 与 gemini31/gpt54nano 的 ctx 无后缀列构成跨模型三角验证。铁律: 三轨、三家、落点全样本与两子样均是同一构念的独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J; DeepSeek 缺席仅掉自身族。


补充计算细节: 本无后缀列在 build_aggregation_dict 中以 deepseekv4_cont_ctx 为源列、mean 为聚合算子登记, valid_agg 仅在源列存在时纳入该键, 否则整列优雅置空而非抛错; 分母为该 bank-year 内 ctx 轨有效连续分的篇数, 与 full、ss 两轨各自独立计数、互不借用分母。缓存命中键为 prompt 版本 v8 与温度 0.0, ctx 轨全命中时可在离线模式下零成本字节级复现该列。方法学上, 本列延续 Tetlock (2007) 的媒体情感均值化范式, 并作为 Ludwig、Mullainathan 与 Rambachan (2026) 意义上的生成回归元供下游计量消费; 模型间一致性以 Krippendorff α 与 Cohen κ 度量, 本列作为规格稳健性并排中的 just-identified 单列, 不并入任何 over-identified Hansen J 过度识别检验。

## VAR: deepseekv4_cont_mean_full

【变体差分】
本列是 DeepSeek-V4 Flash 单家模型在 full 轨上的无后缀全样本连续分均值, 是本家族中口径最基准的一格: 全文输入 (标题拼接正文)、不做落点切分、纳入该 bank-year 全部 full 留篇。本无后缀列由 build_aggregation_dict 以源列 deepseekv4_cont_full 配 mean 归并该 bank-year 全部 full 留篇, 不做落点过滤; 与同模型离散列 deepseekv4_tone_full co-equal, 后者是三分类标签的计数口径均值, 本列则承载 DeepSeek 自报置信度的强度信息, 二者互为稳健、不分主次。该列在规格稳健性并排中仅作 just-identified 单列, 不进入过度识别检验。full 轨既是留篇门控的判定轨 (是否算银行金科报道只看 full 轨语义精筛), 又是连续分的取值轨, 因此本列的度量对象、行宇宙、落点全部同源于 full, 无任何条件化或跨轨错配。数值为 DeepSeek 三分类标签结合自报语气置信度经最大熵 Logit-to-Score 概率映射折算的负一到正一实数, 正表偏正面、负表偏负面、绝对值表强度。本列是理解本家族其余 26 列的锚: app/tech 是它的落点子样切片, ctx/ss 是它的轨道稳健变体, gemini31/gpt54nano 的同格列是它的跨模型平行测量。铁律: 该基准列与三家、三轨、两子样各列均是同一构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J; DeepSeek 独立降级不连坐。

## VAR: deepseekv4_cont_mean_ss

【变体差分】
本列是 DeepSeek-V4 Flash 单家模型在 ss 轨上的无后缀全样本连续分均值。本无后缀列由 build_aggregation_dict 以源列 deepseekv4_cont_ss 配 mean 归并该 bank-year 全部 full 留篇; valid_agg 按源列存在性守卫, 该轨缺席时优雅置空。数值恒位于负一到正一闭区间, 正偏正面、负偏负面、绝对值表语气强度, bank-year 均值反映该切片内 DeepSeek 的整体语气基调。ss 轨输入为标题加银行与金科词同句共现窗口, 是三轨中语义最严格的一轨; 无同句共现的报道 ss 文本镜像 ctx 回退为全文正文、置 ss_is_fallback 为真并与 full 共享篇数分母, 故本列在共现稀疏时会向全文口径优雅退化。无后缀表示不做落点切分, 纳入该 bank-year 全部 full 留篇 (连续分取自 ss 轨)。留篇门控恒为 full-only, ss 是 conditional-on-full 的稳健轨。本列度量的是以银行金科同句语境为锚时 DeepSeek 感知的连续语气均值, 与 ctx/full 无后缀列并列构成三轨稳健梯度, 与 gemini31/gpt54nano 的 ss 无后缀列构成跨模型三角。铁律: 三轨、三家、落点全样本与两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。


补充计算细节: 本无后缀列在 build_aggregation_dict 中以 deepseekv4_cont_ss 为源列配 mean 归并该 bank-year 全部 full 留篇, 分母为 ss 轨有效连续分篇数, 与 full、ctx 两轨各自独立计数、互不借用分母。ss 轨的回退语义使其在同句共现稀疏时向全文口径优雅退化, 但留篇门控恒取 full-only 口径不受回退影响。本列供 bank_fintech_tone (P1) 语调分析与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入; 与词典法、BERT 三法及 co-primary 嵌入在测度上彼此无关, 换嵌入模型时本列零误改 (嵌入不等于 LLM)。本列作为规格稳健性并排中的 just-identified 单列, 不进入任何 over-identified Hansen J。

## VAR: deepseekv4_cont_mean_tech_ctx

【变体差分】
本列取 DeepSeek-V4 Flash 单家模型, 在 ctx 轨上算文章级连续分, 并在 innovation_locus_full 等于「底层技术」的 tech 子样内取 bank-year 均值。本列与无后缀及 app 变体共用文章级源列 deepseekv4_cont_ctx, 区别仅在样本子集: 先按 innovation_locus_full 等于底层技术过滤出 df_cat 再取 mean, 子样为空则优雅置空。本列属情感 LLM 一支, 与 co-primary 嵌入、词典法、BERT 三法在测度上彼此无关, 换嵌入模型时本列零误改 (嵌入不等于 LLM)。与同格 app 变体镜像对称: app 纳入应用场景类报道, tech 纳入底层技术类报道 (如算法、数据、基础设施等技术落点), 两者的落点判据同取自 full-only 的 innovation_locus_full 单一事实源, 即便本列挂接 ctx 轨情感, 划分技术子样所用的落点仍由 full 轨判定, 不随情感轨切换。ctx 轨输入为标题加目标银行句上下文窗口 (Hassan 2019 邻近性), 属 conditional-on-full 稳健轨, 行宇宙为 full 留篇集之子集。连续分为标签乘 DeepSeek 自报置信度经 Logit-to-Score 折算至负一到正一。本列度量银行在底层技术类报道上、以银行邻近句语境为锚时 DeepSeek 感知的连续语气。与同模型 app/无后缀变体、与其余两家的 tech_ctx 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J。


补充口径细节: app 与 tech 两子样并非穷尽划分, 存在既非应用场景亦非底层技术的报道, 故 tech 子样是全样本的真子集, 无后缀全样本列绝非 app 与 tech 两列之和。本列分母为该 bank-year 内 ctx 轨、底层技术落点上有效连续分的篇数, 子样为空则优雅置空。缓存命中键为 prompt 版本 v8 与温度 0.0, 三轨全命中时可离线零成本字节级复现。本列供 bank_fintech_tone (P1) 与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量, 仅作 just-identified 单列而不进入过度识别检验。

## VAR: deepseekv4_cont_mean_tech_full

【变体差分】
本列取 DeepSeek-V4 Flash 单家模型, 在 full 轨 (标题拼接全文正文) 上算文章级连续分, 并在 innovation_locus_full 等于「底层技术」的 tech 子样内取 bank-year 均值。本列与无后缀及 app 变体共用文章级源列 deepseekv4_cont_full, 区别仅在样本子集 df_cat (按 innovation_locus_full 等于底层技术过滤), 分母为该子样内有效连续分篇数。连续分随标签与 DeepSeek 自报置信度确定性折算, 缓存命中键为 prompt 版本 v8 与温度 0.0, 三轨全命中时可离线零成本字节级复现。full 轨是留篇门控判定轨, 故本列行宇宙为该 bank-year full 留篇全集在底层技术落点上的子集, 落点与情感同源于 full, 是 tech 变体三轨中口径最直接的一格。连续分为 DeepSeek 标签结合自报语气置信度经最大熵 Logit-to-Score 折算的负一到正一实数。与同模型 app_full 相比, 本列只纳入被判为「底层技术」类的报道, 度量的是银行在金融科技技术层 (底层能力建设) 相关报道上 DeepSeek 感知的连续语气均值; 与无后缀 full 全样本列相比, 本列是落点条件化的技术切片。app 与 tech 两子样共同覆盖 Gomber (2018) 意义上的创新落点二分, 二者互补而非嵌套。本列与三家、三轨、app/无后缀各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J; DeepSeek 独立降级。

## VAR: deepseekv4_cont_mean_tech_ss

【变体差分】
本列取 DeepSeek-V4 Flash 单家模型, 在 ss 轨上算文章级连续分, 并在 innovation_locus_full 等于「底层技术」的 tech 子样内取 bank-year 均值。本列与无后缀及 app 变体共用文章级源列 deepseekv4_cont_ss, 区别仅在样本子集 df_cat (按 innovation_locus_full 等于底层技术过滤), 子样为空则优雅置空。本列供 bank_fintech_tone (P1) 与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量。ss 轨输入为标题加银行与金科词同句共现窗口; 无此共现的报道 ss 文本镜像 ctx 回退为全文正文、置 ss_is_fallback 为真并与 full 共享篇数分母。留篇门控恒为 full-only, ss 属 conditional-on-full 稳健轨。落点 tech 判据取自 full-only 的 innovation_locus_full, 划分底层技术子样所依据的落点由 full 轨判定, 不随 ss 情感轨切换。本列度量底层技术类报道中、以银行金科同句语境为锚时 DeepSeek 感知的连续语气均值, 是 tech 变体里语义最严格的一格; 在同句共现稀疏时会随 ss 回退向全文口径退化。与同模型 tech_full/tech_ctx、与 app 及无后缀变体, 以及其余两家的 tech_ss 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。


补充计算细节: 本列以 deepseekv4_cont_ss 为源列, 先按 innovation_locus_full 等于底层技术过滤出 df_cat 再取 mean, 分母为该子样内有效连续分篇数, 与同格 app_ss 变体共用同一源列而仅样本子集不同。ss 轨在同句共现稀疏时随回退向全文口径退化, 但落点划分仍恒由 full 轨的 innovation_locus_full 判定, 不随 ss 情感轨切换。DeepSeek 缺席时仅使自身族列受影响, 与其余两家不连坐, 这与 co-primary 嵌入的 both-or-neither 强绑定截然不同。本列作为规格稳健性并排中的 just-identified 单列, 严禁与 app、无后缀或其余两家的对应列混入同一 over-identified Hansen J。

## VAR: gemini31_cont_mean_app_ctx

【变体差分】
本列取 Gemini-3.1-flash-lite (经 yunwu 路由) 一家模型的连续情感分, 在 ctx 轨 (标题加目标银行句上下文窗口, Hassan 2019 邻近性) 上算文章级连续分, 再在 innovation_locus_full 等于「应用场景」的 app 子样内取 bank-year 均值。本列与无后缀及 tech 变体共用文章级源列 gemini31_cont_ctx, 区别仅在样本子集: 先按 innovation_locus_full 等于应用场景过滤出 df_cat 再取 mean。与同模型离散列 gemini31_tone_app_ctx co-equal, 后者是三分类标签计数口径均值, 本列承载 Gemini 自报置信度的强度信息, 二者互为稳健、不分主次。它与 DeepSeek 的同格列构成跨模型三角验证的第二支: 同一构念、同一 ctx 轨、同一 app 落点子样, 换用不同厂商的独立测量。落点判据 innovation_locus_full 属 full-only 单源, 即便本列挂接 ctx 轨情感, 划分应用场景子样所用落点仍由 full 轨判定, 不随情感轨切换。连续分为 Gemini 三分类标签乘其自报语气置信度经 Logit-to-Score 概率映射折算至负一到正一。本列与同模型 tech/无后缀变体、与 DeepSeek 及 GPT 两家的 app_ctx 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。Gemini 缺席仅掉自身族列, 逐模型独立降级不连坐。


补充计算细节: 本列以 gemini31_cont_ctx 为源列, 聚合前先按 innovation_locus_full 等于应用场景过滤出 df_cat 再取 mean, 分母为该子样内有效连续分篇数, 子样为空则优雅置空。Gemini 经 yunwu 路由请求, 缓存命中键为 prompt 版本 v8 与温度 0.0, ctx 轨全命中时可离线零成本字节级复现。本列供 bank_fintech_tone (P1) 语调分析与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入; Gemini 缺席仅掉自身族列, 逐模型独立降级不连坐其余两家。本列仅作 just-identified 单列, 不进入任何 over-identified Hansen J 过度识别检验。

## VAR: gemini31_cont_mean_app_full

【变体差分】
本列取 Gemini-3.1-flash-lite 单家模型, 在 full 轨 (标题拼接全文正文) 上算文章级连续分, 并在 innovation_locus_full 等于「应用场景」的 app 子样内取 bank-year 均值。app/tech 两变体与无后缀变体共用同一文章级源列 gemini31_cont_full, 区别只在样本子集: app 先按 innovation_locus_full 等于应用场景过滤出 df_cat 再取 mean。须强调 app 与 tech 两子样并非穷尽划分, 存在既非应用场景亦非底层技术的报道, 故两子样是全样本的真子集、两者之并集小于等于无后缀全样本, 无后缀列绝非 app 与 tech 两列之和。full 轨兼为留篇门控判定轨与连续分取值轨, 故本列行宇宙为该 bank-year full 留篇全集在应用场景落点上的子集, 落点与情感同源于 full。连续分为 Gemini 标签结合自报语气置信度经最大熵 Logit-to-Score 折算的负一到正一实数, 强度由置信度承载。本列度量的是银行在金融科技应用层 (场景落地、产品服务) 相关报道上 Gemini 感知的连续语气均值; 与同模型 tech_full 互补覆盖 Gomber (2018) 创新落点二分, 与无后缀 full 全样本列构成落点条件化切片对照。与 DeepSeek/GPT 两家的 app_full 列并列, 为同一 app-full 度量的跨模型独立测量, 支撑模型间一致性的稳健性检验。铁律: 三家、三轨、两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J; Gemini 独立降级。

## VAR: gemini31_cont_mean_app_ss

【变体差分】
本列取 Gemini-3.1-flash-lite 单家模型, 在 ss 轨上算文章级连续分, 并在 innovation_locus_full 等于「应用场景」的 app 子样内取 bank-year 均值。本列与无后缀及 tech 变体共用文章级源列 gemini31_cont_ss, 区别仅在样本子集 df_cat (按 innovation_locus_full 等于应用场景过滤), 子样为空则优雅置空。数值恒位于负一到正一闭区间, 正偏正面、负偏负面、绝对值表语气强度, bank-year 均值反映该切片内 Gemini 的整体语气基调。ss 轨输入为标题加银行与金科词同句共现窗口, 是三轨中语义最严格的一轨; 无此共现的报道 ss 文本镜像 ctx 回退为全文正文、置 ss_is_fallback 为真并与 full 共享篇数分母。留篇门控恒为 full-only, ss 属 conditional-on-full 稳健轨。落点 app 判据取自 full-only 的 innovation_locus_full, 划分应用场景子样所依据的落点由 full 轨判定, 不随 ss 情感轨切换。本列度量的是应用场景类报道中、以银行金科同句语境为锚时 Gemini 感知的连续语气均值; 在共现稀疏时随 ss 回退向全文口径退化。与同模型 app_full/app_ctx、与 tech 及无后缀变体, 以及 DeepSeek/GPT 两家的 app_ss 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。


补充计算细节: 本列以 gemini31_cont_ss 为源列配 mean 归并, 分母为 ss 轨、应用场景落点上有效连续分的篇数, 与同格 app_ctx、app_full 变体共用应用场景子样口径而仅轨道文本不同。ss 轨的回退语义 (无同句共现则镜像 ctx 回退全文正文、置 ss_is_fallback 为真、与 full 共享篇数分母) 使本列在共现稀疏时向全文口径退化。方法学上本列延续 Tetlock (2007) 情感均值化范式并作为生成回归元供下游消费; Gemini 缺席仅掉自身族列, 逐模型独立降级。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gemini31_cont_mean_ctx

【变体差分】
本列是 Gemini-3.1-flash-lite 单家模型在 ctx 轨上的无后缀全样本连续分均值, 即不做落点切分、纳入该 bank-year 全部 full 留篇 (连续分取自 ctx 轨文本)。本无后缀列由 build_aggregation_dict 以源列 gemini31_cont_ctx 配 mean 归并该 bank-year 全部 full 留篇, 不按落点过滤; valid_agg 按源列存在性守卫, 缺席时优雅置空。本列属情感 LLM 一支, 与 co-primary 嵌入、词典法、BERT 三法在测度上彼此无关, 换嵌入模型时本列零误改 (嵌入不等于 LLM)。ctx 轨输入为标题加含目标银行句的上下文窗口 (Hassan 2019 邻近性), 把语义焦点收窄到目标银行邻近句, 是 conditional-on-full 的首要稳健轨。无后缀表示这是本模型 ctx 轨的落点无关基准列, 与 app/tech 两落点子样形成「全样本对场景/技术」的对照。连续分为 Gemini 标签乘其自报置信度经 Logit-to-Score 折算至负一到正一。本列与同模型 full/ss 无后缀列构成三轨稳健并排, 与 DeepSeek/GPT 的 ctx 无后缀列构成跨模型三角验证的三支之一。铁律: 三轨、三家、落点全样本与两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J; Gemini 缺席仅掉自身族。


补充计算细节: 本无后缀列以 gemini31_cont_ctx 为源列、mean 为聚合算子登记, valid_agg 仅在源列存在时纳入该键, 分母为该 bank-year 内 ctx 轨有效连续分篇数, 与 full、ss 两轨各自独立计数、互不借用分母。缓存命中键为 prompt 版本 v8 与温度 0.0, ctx 轨全命中可离线零成本字节级复现。本列供 bank_fintech_tone (P1) 与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量。本列仅作 just-identified 单列, 三轨、三家、落点全样本与两子样各列均是同一构念独立测量, 严禁混入同一 over-identified Hansen J。

## VAR: gemini31_cont_mean_full

【变体差分】
本列是 Gemini-3.1-flash-lite 单家模型在 full 轨上的无后缀全样本连续分均值, 是 Gemini 一支中口径最基准的一格: 全文输入 (标题拼接正文)、不做落点切分、纳入该 bank-year 全部 full 留篇。本无后缀列由 build_aggregation_dict 以源列 gemini31_cont_full 配 mean 归并该 bank-year 全部 full 留篇, 不做落点过滤。连续分随三分类标签与 Gemini 自报置信度确定性折算, 缓存命中键为 prompt 版本 v8 与温度 0.0, 三轨全命中时可在离线模式下零成本字节级复现。full 轨既是留篇门控判定轨又是连续分取值轨, 故度量对象、行宇宙、落点全部同源于 full, 无任何条件化或跨轨错配。数值为 Gemini 三分类标签结合自报语气置信度经最大熵 Logit-to-Score 概率映射折算的负一到正一实数。本列是 DeepSeek 同名基准列的跨模型平行测量, 二者加 GPT 的 full 无后缀列共同构成同一构念、三家独立测量的三角验证核心; app/tech 是本列的落点子样切片, ctx/ss 是本列的轨道稳健变体。铁律: 三家、三轨、两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J; Gemini 独立降级不连坐其余两家。


补充计算细节: 本无后缀 full 列以 gemini31_cont_full 为源列配 mean 归并该 bank-year 全部 full 留篇, 不做落点过滤, 分母为 full 轨有效连续分篇数。与同模型离散列 gemini31_tone_full co-equal, 后者是三分类标签的计数口径均值, 本列承载 Gemini 自报置信度的强度信息, 二者互为稳健、不分主次。full 轨兼为留篇门控判定轨与连续分取值轨, 度量对象、行宇宙、落点全部同源于 full, 无跨轨错配。Gemini 缺席仅掉自身族列, 逐模型独立降级不连坐其余两家。本列仅作 just-identified 单列, 禁混同一 over-identified Hansen J。

## VAR: gemini31_cont_mean_ss

【变体差分】
本列是 Gemini-3.1-flash-lite 单家模型在 ss 轨上的无后缀全样本连续分均值。本无后缀列由 build_aggregation_dict 以源列 gemini31_cont_ss 配 mean 归并该 bank-year 全部 full 留篇; valid_agg 按源列存在性守卫, 该轨缺席时优雅置空。本列供 bank_fintech_tone (P1) 与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量。ss 轨输入为标题加银行与金科词同句共现窗口, 是三轨中语义最严格的一轨; 无同句共现的报道 ss 文本镜像 ctx 回退为全文正文、置 ss_is_fallback 为真并与 full 共享篇数分母, 故本列在共现稀疏时向全文口径优雅退化。无后缀表示不做落点切分, 纳入该 bank-year 全部 full 留篇 (连续分取自 ss 轨)。留篇门控恒为 full-only, ss 属 conditional-on-full 稳健轨。本列度量的是以银行金科同句语境为锚时 Gemini 感知的连续语气均值, 与同模型 ctx/full 无后缀列并列构成三轨稳健梯度, 与 DeepSeek/GPT 的 ss 无后缀列构成跨模型三角。铁律: 三轨、三家、落点全样本与两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。


补充计算细节: 本无后缀 ss 列以 gemini31_cont_ss 为源列配 mean 归并该 bank-year 全部 full 留篇, valid_agg 按源列存在性守卫, 该轨缺席时优雅置空, 分母为 ss 轨有效连续分篇数, 与 full、ctx 两轨各自独立计数。ss 轨的回退语义使本列在同句共现稀疏时向全文口径退化, 但留篇门控恒取 full-only 口径不受回退影响。方法学上本列延续 Tetlock (2007) 情感均值化范式, 并作为 Ludwig、Mullainathan 与 Rambachan (2026) 意义上的生成回归元供下游计量消费。本列仅作 just-identified 单列, 三轨、三家各列均同构念独立测量, 严禁混入同一 over-identified Hansen J。

## VAR: gemini31_cont_mean_tech_ctx

【变体差分】
本列取 Gemini-3.1-flash-lite 单家模型, 在 ctx 轨上算文章级连续分, 并在 innovation_locus_full 等于「底层技术」的 tech 子样内取 bank-year 均值。本列与无后缀及 app 变体共用文章级源列 gemini31_cont_ctx, 区别仅在样本子集 df_cat (按 innovation_locus_full 等于底层技术过滤)。与同模型离散列 gemini31_tone_tech_ctx co-equal, 后者是三分类标签计数口径均值, 本列承载 Gemini 自报置信度的强度信息, 二者互为稳健、不分主次。与同格 app 变体镜像对称: tech 纳入底层技术类报道 (算法、数据、基础设施等技术落点), app 纳入应用场景类报道, 两者落点判据同取自 full-only 的 innovation_locus_full 单一事实源, 即便本列挂接 ctx 轨情感, 划分技术子样所用落点仍由 full 轨判定。ctx 轨输入为标题加目标银行句上下文窗口 (Hassan 2019 邻近性), 属 conditional-on-full 稳健轨。连续分为 Gemini 标签乘自报置信度经 Logit-to-Score 折算至负一到正一。本列度量银行在底层技术类报道上、以银行邻近句语境为锚时 Gemini 感知的连续语气。与同模型 app/无后缀变体、与 DeepSeek/GPT 的 tech_ctx 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J; Gemini 独立降级。


补充计算细节: 本列以 gemini31_cont_ctx 为源列, 先按 innovation_locus_full 等于底层技术过滤出 df_cat 再取 mean, 分母为该子样内有效连续分篇数, 与同格 app_ctx 变体共用同一源列而仅样本子集不同。app 与 tech 两子样非穷尽划分, 无后缀全样本列绝非二者之和。缓存命中键为 prompt 版本 v8 与温度 0.0, 三轨全命中可离线零成本字节级复现。Gemini 缺席仅掉自身族列, 逐模型独立降级不连坐。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J 过度识别检验。

## VAR: gemini31_cont_mean_tech_full

【变体差分】
本列取 Gemini-3.1-flash-lite 单家模型, 在 full 轨 (标题拼接全文正文) 上算文章级连续分, 并在 innovation_locus_full 等于「底层技术」的 tech 子样内取 bank-year 均值。本列与无后缀及 app 变体共用文章级源列 gemini31_cont_full, 区别仅在样本子集 df_cat (按 innovation_locus_full 等于底层技术过滤), 分母为该子样内有效连续分篇数。数值恒位于负一到正一闭区间, 正偏正面、负偏负面、绝对值表语气强度, bank-year 均值反映该切片内 Gemini 的整体语气基调。full 轨为留篇门控判定轨, 故本列行宇宙为该 bank-year full 留篇全集在底层技术落点上的子集, 落点与情感同源于 full, 是 Gemini tech 变体三轨中口径最直接的一格。连续分为 Gemini 标签结合自报语气置信度经最大熵 Logit-to-Score 折算的负一到正一实数。与同模型 app_full 相比, 本列只纳入被判为「底层技术」类的报道, 度量的是银行在金融科技技术层 (底层能力建设) 相关报道上 Gemini 感知的连续语气均值; app 与 tech 两子样共同覆盖 Gomber (2018) 创新落点二分, 互补而非嵌套。与 DeepSeek/GPT 的 tech_full 列并列构成同一 tech-full 度量的跨模型独立测量。铁律: 三家、三轨、两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J。


补充计算细节: 本列以 gemini31_cont_full 为源列, 先按 innovation_locus_full 等于底层技术过滤出 df_cat 再取 mean, 分母为该 bank-year full 留篇全集在底层技术落点上的有效连续分篇数, 子样为空则优雅置空。full 轨兼为留篇门控判定轨与连续分取值轨, 落点与情感同源于 full, 无跨轨错配。缓存命中键为 prompt 版本 v8 与温度 0.0, full 轨全命中可离线零成本字节级复现。本列供 bank_fintech_tone (P1) 与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量; Gemini 缺席仅掉自身族列, 逐模型独立降级不连坐。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gemini31_cont_mean_tech_ss

【变体差分】
本列取 Gemini-3.1-flash-lite 单家模型, 在 ss 轨上算文章级连续分, 并在 innovation_locus_full 等于「底层技术」的 tech 子样内取 bank-year 均值。ss 轨输入为标题加银行与金科词同句共现窗口; 无此共现的报道 ss 文本镜像 ctx 回退为全文正文、置 ss_is_fallback 为真并与 full 共享篇数分母。留篇门控恒为 full-only, ss 属 conditional-on-full 稳健轨。落点 tech 判据取自 full-only 的 innovation_locus_full, 划分底层技术子样所依据的落点由 full 轨判定, 不随 ss 情感轨切换。本列度量底层技术类报道中、以银行金科同句语境为锚时 Gemini 感知的连续语气均值, 是 Gemini tech 变体里语义最严格的一格; 在同句共现稀疏时随 ss 回退向全文口径退化。与同模型 tech_full/tech_ctx、与 app 及无后缀变体, 以及 DeepSeek/GPT 的 tech_ss 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。


补充计算细节: 本列以 gemini31_cont_ss 为源列, 先按 innovation_locus_full 等于底层技术过滤出 df_cat 再取 mean, 分母为该子样内有效连续分篇数, 子样为空则优雅置空, 与同格 tech_full、tech_ctx 变体共用底层技术子样口径而仅轨道文本不同。ss 轨输入为标题加银行与金科词同句共现窗口, 是三轨中语义最严格的一轨, 在共现稀疏时随回退向全文口径退化, 但落点划分仍恒由 full 轨的 innovation_locus_full 判定。本列供 bank_fintech_tone (P1) 与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量; Gemini 缺席仅掉自身族列, 逐模型独立降级。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mean_app_ctx

【变体差分】
本列取 GPT-5.4-nano (经 yunwu 路由) 一家模型的连续情感分, 在 ctx 轨 (标题加目标银行句上下文窗口, Hassan 2019 邻近性) 上算文章级连续分, 再在 innovation_locus_full 等于「应用场景」的 app 子样内取 bank-year 均值。它与 DeepSeek、Gemini 的同格列构成跨模型三角验证的第三支: 同一构念、同一 ctx 轨、同一 app 落点子样, 换用第三家厂商的独立测量。落点判据 innovation_locus_full 属 full-only 单源, 即便本列挂接 ctx 轨情感, 划分应用场景子样所用落点仍由 full 轨判定, 不随情感轨切换。连续分为 GPT 三分类标签乘其自报语气置信度经 Logit-to-Score 概率映射折算至负一到正一。本列与同模型 tech/无后缀变体、与 DeepSeek/Gemini 两家的 app_ctx 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。GPT 缺席仅掉自身族列, 逐模型独立降级不连坐。


补充计算细节: 本列以 gpt54nano_cont_ctx 为源列, 聚合前先按 innovation_locus_full 等于应用场景过滤出 df_cat 再取 mean, 分母为该子样内有效连续分篇数, 子样为空则优雅置空, 与无后缀及 tech 变体共用同一源列而仅样本子集不同。与同模型离散列 gpt54nano_tone_app_ctx co-equal, 后者是三分类标签计数口径均值, 本列承载 GPT 自报置信度的强度信息, 二者互为稳健、不分主次。GPT 经 yunwu 路由请求, 缓存命中键为 prompt 版本 v8 与温度 0.0, ctx 轨全命中可离线零成本字节级复现。ctx 轨属 conditional-on-full 稳健轨, 行宇宙为 full 留篇集之子集; 本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mean_app_full

【变体差分】
本列取 GPT-5.4-nano 单家模型, 在 full 轨 (标题拼接全文正文) 上算文章级连续分, 并在 innovation_locus_full 等于「应用场景」的 app 子样内取 bank-year 均值。full 轨兼为留篇门控判定轨与连续分取值轨, 故本列行宇宙为该 bank-year full 留篇全集在应用场景落点上的子集, 落点与情感同源于 full。连续分为 GPT 标签结合自报语气置信度经最大熵 Logit-to-Score 折算的负一到正一实数。本列度量的是银行在金融科技应用层 (场景落地、产品服务) 相关报道上 GPT 感知的连续语气均值; 与同模型 tech_full 互补覆盖 Gomber (2018) 创新落点二分, 与无后缀 full 全样本列构成落点条件化切片对照。与 DeepSeek/Gemini 两家的 app_full 列并列, 为同一 app-full 度量的跨模型独立测量, 支撑模型间一致性 (Krippendorff α / Cohen κ) 的稳健性检验。铁律: 三家、三轨、两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J; GPT 独立降级。


补充口径细节: app 与 tech 两子样并非穷尽划分, 存在既非应用场景亦非底层技术的报道, 故本列的应用场景子样是全样本的真子集, 无后缀全样本列绝非 app 与 tech 两列之和。本列以 gpt54nano_cont_full 为源列, 分母为该 bank-year full 留篇全集在应用场景落点上的有效连续分篇数。full 轨兼为留篇门控判定轨与连续分取值轨, 落点与情感同源于 full。本列供 bank_fintech_tone (P1) 语调分析作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量; GPT 缺席仅掉自身族列, 逐模型独立降级不连坐。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mean_app_ss

【变体差分】
本列取 GPT-5.4-nano 单家模型, 在 ss 轨上算文章级连续分, 并在 innovation_locus_full 等于「应用场景」的 app 子样内取 bank-year 均值。ss 轨输入为标题加银行与金科词同句共现窗口, 是三轨中语义最严格的一轨; 无此共现的报道 ss 文本镜像 ctx 回退为全文正文、置 ss_is_fallback 为真并与 full 共享篇数分母。留篇门控恒为 full-only, ss 属 conditional-on-full 稳健轨。落点 app 判据取自 full-only 的 innovation_locus_full, 划分应用场景子样所依据的落点由 full 轨判定, 不随 ss 情感轨切换。本列度量的是应用场景类报道中、以银行金科同句语境为锚时 GPT 感知的连续语气均值; 在共现稀疏时随 ss 回退向全文口径退化。与同模型 app_full/app_ctx、与 tech 及无后缀变体, 以及 DeepSeek/Gemini 两家的 app_ss 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。


补充计算细节: 本列以 gpt54nano_cont_ss 为源列, 先按 innovation_locus_full 等于应用场景过滤出 df_cat 再取 mean, 分母为该子样内有效连续分篇数, 子样为空则优雅置空, 与同格 app_full、app_ctx 变体共用应用场景子样口径而仅轨道文本不同。ss 轨的回退语义 (无同句共现则镜像 ctx 回退全文正文、置 ss_is_fallback 为真、与 full 共享篇数分母) 使本列在共现稀疏时向全文口径退化。方法学上本列延续 Tetlock (2007) 情感均值化范式并作为生成回归元供下游消费; GPT 缺席仅掉自身族列, 逐模型独立降级。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mean_ctx

【变体差分】
本列是 GPT-5.4-nano 单家模型在 ctx 轨上的无后缀全样本连续分均值, 即不做落点切分、纳入该 bank-year 全部 full 留篇 (连续分取自 ctx 轨文本)。ctx 轨输入为标题加含目标银行句的上下文窗口 (Hassan 2019 邻近性), 把语义焦点收窄到目标银行邻近句, 是 conditional-on-full 的首要稳健轨。无后缀表示这是本模型 ctx 轨的落点无关基准列, 与 app/tech 两落点子样形成「全样本对场景/技术」的对照。连续分为 GPT 标签乘其自报置信度经 Logit-to-Score 折算至负一到正一。本列与同模型 full/ss 无后缀列构成三轨稳健并排, 与 DeepSeek/Gemini 的 ctx 无后缀列构成跨模型三角验证的三支之一。铁律: 三轨、三家、落点全样本与两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J; GPT 缺席仅掉自身族。


补充计算细节: 本无后缀列以 gpt54nano_cont_ctx 为源列、mean 为聚合算子登记, valid_agg 仅在源列存在时纳入该键, 分母为该 bank-year 内 ctx 轨有效连续分篇数, 与 full、ss 两轨各自独立计数、互不借用分母。缓存命中键为 prompt 版本 v8 与温度 0.0, ctx 轨全命中可离线零成本字节级复现。本列属情感 LLM 一支, 与 co-primary 嵌入、词典法、BERT 三法在测度上彼此无关, 换嵌入模型时本列零误改 (嵌入不等于 LLM)。本列供 bank_fintech_tone (P1) 与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mean_full

【变体差分】
本列是 GPT-5.4-nano 单家模型在 full 轨上的无后缀全样本连续分均值, 是 GPT 一支中口径最基准的一格: 全文输入 (标题拼接正文)、不做落点切分、纳入该 bank-year 全部 full 留篇。full 轨既是留篇门控判定轨又是连续分取值轨, 故度量对象、行宇宙、落点全部同源于 full, 无任何条件化或跨轨错配。数值为 GPT 三分类标签结合自报语气置信度经最大熵 Logit-to-Score 概率映射折算的负一到正一实数。本列是 DeepSeek、Gemini 同名基准列的跨模型平行测量, 三者共同构成同一构念、三家独立测量的三角验证核心; app/tech 是本列的落点子样切片, ctx/ss 是本列的轨道稳健变体。铁律: 三家、三轨、两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J; GPT 独立降级不连坐其余两家。


补充计算细节: 本无后缀 full 列以 gpt54nano_cont_full 为源列配 mean 归并该 bank-year 全部 full 留篇, 不做落点过滤, 分母为 full 轨有效连续分篇数。与同模型离散列 gpt54nano_tone_full co-equal, 后者是三分类标签计数口径均值, 本列承载 GPT 自报置信度的强度信息, 二者互为稳健、不分主次。缓存命中键为 prompt 版本 v8 与温度 0.0, full 轨全命中可离线零成本字节级复现。GPT 缺席仅掉自身族列, 逐模型独立降级不连坐其余两家。本列仅作 just-identified 单列, app/tech 是其落点子样切片, ctx/ss 是其轨道稳健变体, 禁混同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mean_ss

【变体差分】
本列是 GPT-5.4-nano 单家模型在 ss 轨上的无后缀全样本连续分均值。ss 轨输入为标题加银行与金科词同句共现窗口, 是三轨中语义最严格的一轨; 无同句共现的报道 ss 文本镜像 ctx 回退为全文正文、置 ss_is_fallback 为真并与 full 共享篇数分母, 故本列在共现稀疏时向全文口径优雅退化。无后缀表示不做落点切分, 纳入该 bank-year 全部 full 留篇 (连续分取自 ss 轨)。留篇门控恒为 full-only, ss 属 conditional-on-full 稳健轨。本列度量的是以银行金科同句语境为锚时 GPT 感知的连续语气均值, 与同模型 ctx/full 无后缀列并列构成三轨稳健梯度, 与 DeepSeek/Gemini 的 ss 无后缀列构成跨模型三角。铁律: 三轨、三家、落点全样本与两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。


补充计算细节: 本无后缀 ss 列以 gpt54nano_cont_ss 为源列配 mean 归并该 bank-year 全部 full 留篇, valid_agg 按源列存在性守卫, 该轨缺席时优雅置空, 分母为 ss 轨有效连续分篇数, 与 full、ctx 两轨各自独立计数。ss 轨的回退语义使本列在同句共现稀疏时向全文口径退化, 但留篇门控恒取 full-only 口径不受回退影响。方法学上本列延续 Tetlock (2007) 情感均值化范式并作为 Ludwig、Mullainathan 与 Rambachan (2026) 意义上的生成回归元供下游计量消费。GPT 缺席仅掉自身族列, 逐模型独立降级。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mean_tech_ctx

【变体差分】
本列取 GPT-5.4-nano 单家模型, 在 ctx 轨上算文章级连续分, 并在 innovation_locus_full 等于「底层技术」的 tech 子样内取 bank-year 均值。与同格 app 变体镜像对称: tech 纳入底层技术类报道 (算法、数据、基础设施等技术落点), app 纳入应用场景类报道, 两者落点判据同取自 full-only 的 innovation_locus_full 单一事实源, 即便本列挂接 ctx 轨情感, 划分技术子样所用落点仍由 full 轨判定。ctx 轨输入为标题加目标银行句上下文窗口 (Hassan 2019 邻近性), 属 conditional-on-full 稳健轨。连续分为 GPT 标签乘自报置信度经 Logit-to-Score 折算至负一到正一。本列度量银行在底层技术类报道上、以银行邻近句语境为锚时 GPT 感知的连续语气。与同模型 app/无后缀变体、与 DeepSeek/Gemini 的 tech_ctx 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J; GPT 独立降级。


补充计算细节: 本列以 gpt54nano_cont_ctx 为源列, 先按 innovation_locus_full 等于底层技术过滤出 df_cat 再取 mean, 分母为该子样内有效连续分篇数, 子样为空则优雅置空, 与无后缀及 app 变体共用同一源列而仅样本子集不同。app 与 tech 两子样非穷尽划分, 无后缀全样本列绝非二者之和。缓存命中键为 prompt 版本 v8 与温度 0.0, 三轨全命中可离线零成本字节级复现。本列供 bank_fintech_tone (P1) 与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入; GPT 缺席仅掉自身族列, 逐模型独立降级。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mean_tech_full

【变体差分】
本列取 GPT-5.4-nano 单家模型, 在 full 轨 (标题拼接全文正文) 上算文章级连续分, 并在 innovation_locus_full 等于「底层技术」的 tech 子样内取 bank-year 均值。full 轨为留篇门控判定轨, 故本列行宇宙为该 bank-year full 留篇全集在底层技术落点上的子集, 落点与情感同源于 full, 是 GPT tech 变体三轨中口径最直接的一格。连续分为 GPT 标签结合自报语气置信度经最大熵 Logit-to-Score 折算的负一到正一实数。与同模型 app_full 相比, 本列只纳入被判为「底层技术」类的报道, 度量的是银行在金融科技技术层 (底层能力建设) 相关报道上 GPT 感知的连续语气均值; app 与 tech 两子样共同覆盖 Gomber (2018) 创新落点二分, 互补而非嵌套。与 DeepSeek/Gemini 的 tech_full 列并列构成同一 tech-full 度量的跨模型独立测量。铁律: 三家、三轨、两子样各列均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 禁混同一 over-identified Hansen J。


补充计算细节: 本列以 gpt54nano_cont_full 为源列, 先按 innovation_locus_full 等于底层技术过滤出 df_cat 再取 mean, 分母为该 bank-year full 留篇全集在底层技术落点上的有效连续分篇数, 子样为空则优雅置空, 与无后缀及 app_full 变体共用同一源列而仅样本子集不同。app 与 tech 两子样并非穷尽划分, 无后缀全样本列绝非二者之和; 两子样共同覆盖 Gomber (2018) 意义上的创新落点二分, 互补而非嵌套。缓存命中键为 prompt 版本 v8 与温度 0.0, full 轨全命中可离线零成本字节级复现。GPT 缺席仅掉自身族列, 逐模型独立降级不连坐其余两家。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

## VAR: gpt54nano_cont_mean_tech_ss

【变体差分】
本列取 GPT-5.4-nano 单家模型, 在 ss 轨上算文章级连续分, 并在 innovation_locus_full 等于「底层技术」的 tech 子样内取 bank-year 均值。ss 轨输入为标题加银行与金科词同句共现窗口; 无此共现的报道 ss 文本镜像 ctx 回退为全文正文、置 ss_is_fallback 为真并与 full 共享篇数分母。留篇门控恒为 full-only, ss 属 conditional-on-full 稳健轨。落点 tech 判据取自 full-only 的 innovation_locus_full, 划分底层技术子样所依据的落点由 full 轨判定, 不随 ss 情感轨切换。本列度量底层技术类报道中、以银行金科同句语境为锚时 GPT 感知的连续语气均值, 是 GPT tech 变体里语义最严格的一格; 在同句共现稀疏时随 ss 回退向全文口径退化。与同模型 tech_full/tech_ctx、与 app 及无后缀变体, 以及 DeepSeek/Gemini 的 tech_ss 列, 均同构念独立测量, 各自 just-identified 并排、互为稳健不分主次, 严禁混入同一 over-identified Hansen J。

补充计算细节: 本列以 gpt54nano_cont_ss 为源列, 先按 innovation_locus_full 等于底层技术过滤出 df_cat 再取 mean, 分母为该子样内有效连续分篇数, 子样为空则优雅置空, 与同格 tech_full、tech_ctx 变体共用底层技术子样口径而仅轨道文本不同。ss 轨输入为标题加银行与金科词同句共现窗口, 是三轨中语义最严格的一轨, 在共现稀疏时随回退向全文口径退化, 但落点划分仍恒由 full 轨的 innovation_locus_full 判定, 不随 ss 情感轨切换。本列供 bank_fintech_tone (P1) 与创新落点 (P4, Gomber 2018) 异质性作跨模型稳健性输入, 模型间一致性以 Krippendorff α 与 Cohen κ 度量; GPT 缺席仅掉自身族列, 逐模型独立降级不连坐其余两家。本列仅作 just-identified 单列, 严禁混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Hansen, A. L. (2026). Validating large language model annotations. FEDS Working Paper No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Ludwig, J., Mullainathan, S., & Rambachan, A. (2026). Large language models: An applied econometric framework. Annual Review of Economics. https://doi.org/10.1146/annurev-economics-120925-105620
Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
