---
family_id: F368
columns:
- llm_models_avg_tone_app_ctx
- llm_models_avg_tone_app_full
- llm_models_avg_tone_app_ss
- llm_models_avg_tone_ctx
- llm_models_avg_tone_ctx_z
- llm_models_avg_tone_full
- llm_models_avg_tone_full_z
- llm_models_avg_tone_hw_ctx
- llm_models_avg_tone_hw_full
- llm_models_avg_tone_hw_ss
- llm_models_avg_tone_mw_ctx
- llm_models_avg_tone_mw_full
- llm_models_avg_tone_mw_ss
- llm_models_avg_tone_ss
- llm_models_avg_tone_ss_z
- llm_models_avg_tone_std_ctx
- llm_models_avg_tone_std_full
- llm_models_avg_tone_std_ss
- llm_models_avg_tone_tech_ctx
- llm_models_avg_tone_tech_full
- llm_models_avg_tone_tech_ss
- llm_models_avg_tone_vw_ctx
- llm_models_avg_tone_vw_full
- llm_models_avg_tone_vw_ss
unit: 语调得分 (连续, 约 [-1,1]; bank-year 聚合后的银行-年度均值)
formula: "llm_models_avg_tone_track = rowmean_over_LLM_MODELS(model_tone_track); model 取值 gpt54nano/gemini31/deepseekv4 三者之一; track 取值 full/ctx/ss 三者之一; 加权变体 vw/mw/hw 以 Σ(w·tone)/Σw 加权聚合再跨模型取行均值; tech/app 为分类维度子样本条件; _std 为跨模型对每家 within-bank-year 语调离散度取行均值; _z 为逐年度截面 (per-year groupby, 仅 n_articles>0 且年内有效样本≥3) 减年均值除年标准差的 Fama-MacBeth 式截面标准化轨 (各年 scale 不同, 分段仿射)"
producer: news_process/pipeline/panel/geography.py::compute_composite_indicators (跨模型行均值综合); news_process/pipeline/panel/encode.py (上游逐模型 bank-year 聚合与加权分母); news_process/pipeline/panel/export.py (Stata 标签)
upstream:
- 21_tone_llms.parquet (三家 LLM 逐篇 {model}_tone{track} 情感码)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 40_panel_yearly.parquet (bank-year 聚合与加权分母)
citations:
- doi: 10.1146/annurev-economics-120925-105620
  type: journal
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2026
  title: "Large language models: An applied econometric framework"
  venue: Annual Review of Economics
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: 105227
- doi: 10.1016/j.mlwa.2023.100508
  type: journal
  authors: Fatouros, G., Soldatos, J., Kouroumali, K., Makridis, G., & Kyriazis, D.
  year: 2023
  title: "Transforming sentiment analysis in the financial domain with ChatGPT"
  venue: Machine Learning with Applications
  vol: 14
  pages_or_artno: 100508
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1111/joes.12370
  type: journal
  authors: Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K.
  year: 2020
  title: "Econometrics meets sentiment: An overview of methodology and applications"
  venue: Journal of Economic Surveys
  vol: 34
  issue: 3
  pages_or_artno: 512-547
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1002/jae.2508
  type: journal
  authors: MacKinnon, J. G., & Webb, M. D.
  year: 2017
  title: "Wild bootstrap inference for wildly different cluster sizes"
  venue: Journal of Applied Econometrics
  vol: 32
  issue: 2
  pages_or_artno: 233-254
- doi: 10.1016/j.jeconom.2024.105727
  type: journal
  authors: Wang, W., & Zhang, Y.
  year: 2024
  title: "Wild bootstrap inference for instrumental variables regressions with weak and few clusters"
  venue: Journal of Econometrics
  vol: 241
  issue: 1
  pages_or_artno: 105727
- doi: "10.1007/s10791-025-09573-7"
  type: journal
  authors: "Chen, W., Liu, W., Zheng, J., & Zhang, X."
  year: 2025
  title: "Leveraging large language model as news sentiment predictor in stock markets: a knowledge-enhanced strategy"
  venue: "Discover Computing"
- doi: "10.1007/978-3-031-97992-7_62"
  title: "Fuzzy Ensemble of Large Language Models for Financial Sentiment Analysis"
  authors: "Stefanova, T., & Georgiev, S."
  year: 2025
  venue: "Lecture Notes in Networks and Systems (Intelligent and Fuzzy Systems)"
  type: "wp"
new_dois:
  - "10.3390/bdcc9100263"
  - "10.1007/s10791-025-09573-7"
  - "10.1007/978-3-031-97992-7_62"
---

## CORE

【构念与来源】
本家族刻画的构念是「多大语言模型集成的银行-年度新闻情感语调」。在 news_process 流水线中, 情感测度以三法并行: 大语言模型 (LLM)、情感词典、微调 BERT。本家族属其中 LLM 一支的均值-ensemble 汇总轨。stage 21 (tone_llms) 对每一篇「银行×金科」报道调用三家彼此独立的商用大模型逐篇打分: gpt-5.4-nano (走 yunwu 路由)、gemini-3.1-flash-lite (走 yunwu 路由)、deepseek-v4-flash (直连 api.deepseek.com)。三家各自产出逐篇语调码 (负面、中性、正面, 映射为约 [-1,1] 的连续语调分), 落列为 gpt54nano_tone、gemini31_tone、deepseekv4_tone 及其三轨后缀。本家族在面板层 (geography.py::compute_composite_indicators) 对这三家逐模型 bank-year 聚合值取跨模型行均值, 得到 llm_models_avg_tone{track}, 即「跨厂商集成语调」。该均值-ensemble 的动机在于降低单一大模型的特异性测量噪声与厂商偏倚: 任一家模型都可能因训练语料、对齐策略、指令跟随差异而在特定题材上系统性偏正或偏负, 而三家算术平均可对这类互不相关的模型级偏差做一阶抵消, 逼近「若干独立标注者共识」的稳健信号。这一集成思路与 Chen 等 (2025) 综述所归纳的 LLM ensemble 范式一脉相承, 也呼应 Gilardi 等 (2023) 关于大模型标注在多次调用/多模型平均后可逼近甚至超过众包标注者一致性的证据。

【构念与来源 (续): 三家大模型的来源与独立性】
三家大模型刻意选自不同厂商、不同架构、不同路由, 以最大化模型级误差的相互独立: gpt-5.4-nano (OpenAI 系, 经 yunwu 中转)、gemini-3.1-flash-lite (Google 系, 经 yunwu 中转)、deepseek-v4-flash (深度求索系, 直连 api.deepseek.com)。三家在预训练语料构成、指令对齐方法、对中文金融语域的适配程度上各不相同, 因此它们对同一篇报道的语调判断偏差在很大程度上互不相关 — 这正是均值-ensemble 得以一阶抵消模型特异性噪声的统计前提。若三家高度同质 (共享同一底座与对齐目标), 均值将退化为单模型且无法降噪; 本项目以跨厂商多样性尽力保证独立性, 并以 per-model 轨、词典轨、BERT 轨三重跨方法互证来暴露任何未被平均消除的共同偏倚。值得强调的是, 情感 LLM 与流水线的嵌入模型完全解耦: stage 21 的三家投票/均值与 co-primary 嵌入 (Qwen3-Embedding-8B 及 text-embedding-3-large) 属两套互不影响的子系统, 换嵌入模型时本家族零误改。

【构念与来源 (续): 与流水线口径的对齐】
本家族的行宇宙与留篇门控严格遵循 2026-06-29 确立的 full-only 口径: 一篇报道是否计入「银行金科报道」样本, 只看该篇的 full 轨大模型判定 (llm_verified_full == True)。因此 llm_models_avg_tone_full 是主轨 canonical, ctx 轨与 ss 轨降为「conditional-on-full」的测度/稳健性轨 — 其行宇宙是 full 留篇集的子集, 但每条轨的分子分母仍按各自轨道独立计算, 不跨轨借分母。三轨文本在 stage 14 (ctx_materializer) 物化: full = 标题 prepend + 全文正文; ctx = 标题 + 实体上下文窗口; ss = 标题 + 银行∧金科同句±N 窗。ss 轨遵循镜像 ctx 的回退公理: 当某篇无「银行∧金科同句共现」时, content_ss 回退为全文正文、ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母口径。这一回退语义确保 ss 轨在稀疏共现的银行-年度不至坍缩为空, 而是优雅退化为一个偏保守的全文测度。这套三轨口径的意义在于把「语境范围」本身当作一个可检验的稳健性维度: full 覆盖全文、ctx 聚焦实体窗口、ss 收紧到同句强共现, 三者对同一构念给出由宽到紧的三重估计, 语调结论若在三轨间一致即获得强稳健性支撑, 若不一致则本身构成关于「语境范围如何影响情感测量」的实质发现。

【方法学与计算 (续): 确定性与可复现锚】
本家族全链条 $0、无网络、逐位可复现。逐篇 LLM 打分虽是付费 API 调用, 但命中冻结的确定性缓存后无需重放: 缓存命中键为 prompt_version='v8-2026-05-17'、temperature=0.0, prompt 构造由 tone_llms.iter_article_track_prompts 单一 SSOT 生成 (生产与审计共用同一构造 → 缓存键一致); 三轨在 _llm_cache.db 中 0 miss 即可设 NEWS_PROCESS_LLM_OFFLINE=1 离线字节级复现, miss 则 raise LLMCacheMissError 而绝不静默付费。面板层的跨模型行均值与 bank-year 聚合是纯 pandas/numpy 运算, 不涉 LLM/嵌入/网络, 因此本家族列在 golden 快照中是确定性锚 (不属 BLAS-FP 非确定的网络列)。冻结锚点还包括 jieba==0.42.1 与 Prompt v8 的字节级冻结, 保证不重跑 stage 21 即可复现历史结果。生产语料全量重处理 (stage 21 全量重跑) 属付费不可逆操作, 须先过 M0 审批门, 并在重生时钉死 PYTHONHASHSEED=0 与全 BLAS 线程为 1。

【方法学与计算】
计算链路分三层。第一层是逐篇打分 (stage 21): 三家 LLM 在冻结的 Prompt v8 (字节级冻结, prompt_version='v8-2026-05-17', temperature=0.0) 下对同一篇三轨文本分别打分, 命中同一确定性缓存键即可离线 $0 复现。第二层是 bank-year 聚合 (encode.py): 对每家模型, 把该银行该年内所有留篇报道的逐篇语调按聚合口径汇总为 {model}_tone{track} — 等权轨取算术均值, 加权轨取 Σ(w·tone)/Σw。第三层是跨模型综合 (geography.py): 对三家的 bank-year 值以 _safe_mean 取行均值, 只对该行实际存在的模型列求平均, 缺列 (如某家模型该轨未落盘) 优雅返回 NaN 而不使阶段崩溃 — 这保证了 per-model 独立降级: 某一家缺席仅拉低该行的有效模型基数, 不像 co-primary 嵌入那样触发 both-or-neither 同置 NaN。等权 canonical 的公式即 llm_models_avg_tone{track} = mean(gpt54nano_tone{track}, gemini31_tone{track}, deepseekv4_tone{track})。加权变体在第二层改换聚合权重: vw (value/salience 加权) 按新闻显著性权重加权, 权重取自 stage 11 news_salience 物化的报道显著性代理 (提及密度、版位、导语、署名等), 概念上对标 Hassan 等 (2019) 的 firm-level 提及计数加权与价值加权文本测度; mw (media-authority 加权) 按媒体权威分层加权 (compute_media_authority_weights), 给权威媒体的报道更高权重; hw (herd 加权) 按 stage 24 herd_decay 产出的羊群/新颖度衰减权重加权, 对重复转载、陈旧信息做折价, 概念上呼应 Tetlock (2007) 及媒体信息新颖性文献对「陈旧新闻」信息含量的折减。tech 与 app 是分类维度条件子样本: 仅在该银行该年被判为「技术型金科」(n_articles_tech) 或「应用型金科」(n_articles_app) 的报道子集上重算集成语调, 用于分辨语调是否随金科叙事类型而异。std 是跨模型对每家 within-bank-year 语调离散度 ({model}_tone_std) 取行均值, 度量的是「同一银行年内报道语调有多分散」而非语调水平本身。_z 是把 canonical 轨做逐年度截面标准化后的版本: standardize_panel_variables 对每个 year 分组 (仅 n_articles>0 且年内有效样本≥3), 在该年度截面内减年均值除年标准差, 各年各自定标 (分段仿射, 各年 scale 不同, 非全样本单一线性变换) — 这是 Fama-MacBeth 式的逐横截面标准化, 目的是剔除年度共同成分、令同一年内不同银行的语调以年内标准差为单位可比, 便于跨测度、跨论文进入回归或森林图。

【文献定位】
本家族坐落于金融文本情感测量的方法学谱系。词典法一脉 (Loughran & McDonald, 2011, 2016; Du 等, 2022 的中文金融情感词典) 强调可复现、可审计但受限于词表覆盖与规则脆性; 机器学习/BERT 一脉 (Huang 等, 2023 的 FinBERT; Frankel 等, 2022 对 ML 与词典法的正面比较) 提升了语境敏感度; 大模型一脉 (Fatouros 等, 2023; Kirtac & Germano, 2024; Lan 等, 2025 的中文细粒度金融情感; Gilardi 等, 2023) 进一步以零样本/少样本指令跟随逼近人类标注。van Atteveldt 等 (2021) 与 Algaba 等 (2020) 从效度与计量整合角度指出: 任何单一自动情感测度都带测量误差, 多方法/多标注者三角互证是提升构念效度的正道。本家族正是这一思想在 LLM 内部的落地 — 三家跨厂商大模型互为独立标注者, 均值-ensemble 是其一阶共识。更具体地, Frankel 等 (2022) 以正面比较表明机器学习情感在预测披露后果上系统性优于词典法, 而 Huang 等 (2023) 的 FinBERT 进一步证明领域预训练能显著提升金融文本情感抽取; 大模型则在此基础上以指令跟随把「无需领域微调即可零样本迁移」推向前沿 (Fatouros 等, 2023 对金融域 ChatGPT 情感的改造; Kirtac & Germano, 2024 将 LLM 情感直接接入交易信号)。在中文金融语域, Lan 等 (2025) 证明大模型可做细粒度 (实体级) 情感分析, Du 等 (2022) 则提供了对照的中文金融情感词典基准。本家族在三家大模型内部取均值, 与这些跨方法基准 (词典均值 dict_avg_tone、BERT 均值 bert_avg) 并列, 构成一个「方法内集成 × 跨方法三角」的双层稳健性结构。至于集成本身的方法论, Chen 等 (2025) 系统综述了 LLM ensemble 的诸种策略 (投票、平均、路由、级联), 本家族采用最透明的算术平均, 兼容后续对投票轨 (llm_vote_tone) 的对照。此外, Chen, Liu, Zheng, & Zhang (2025, Discover Computing) 提出以知识增强策略将大语言模型用作新闻情感预测器, 进一步支持本家族「以大模型对新闻文本逐篇打分、再跨模型集成为语调测度」这一方法学定位的合理性。Stefanova & Georgiev (2025, Lecture Notes in Networks and Systems) 提出对多个大语言模型的输出以模糊逻辑方式集成, 用于金融情感分析, 与本家族三家大模型均值-ensemble 的跨模型集成思路直接呼应。

【识别策略定位】
在识别层面, 本家族的核心纪律是: LLM 三家的 per-model 子测度 (gpt54nano/gemini31/deepseekv4 各自的语调) 与本家族的均值-ensemble, 属「互为稳健性、不分主次」的并排轨; 三轨 (full/ctx/ss)、三套加权 (vw/mw/hw)、两个分类维度 (tech/app) 亦同理。铁律是: 这些并排轨各自 just-identified 并排进入分析, 严禁把它们混进同一个 over-identified 的 Hansen J 过度识别检验 — 因为它们测的是同一构念的高度共线替代, 混入同一 GMM 会人为制造伪过度识别、扭曲 J 统计量。真正的跨模型族错误率控制 (FWER) 由根级模板 27_tableA12_cross_model_fwer 以 Romano & Wolf (2005) 步降式多重检验实现; paper_spec 中的 cross_model 声明是文档性的, 运行时无消费者。作为生成回归元 (generated regressor) 的大模型情感, 其测量误差的计量后果由 Ludwig 等 (2026) 的应用计量框架给出系统刻画 — 集成平均是缓解 (而非消除) 该问题的一种手段。进一步展开, 本家族在识别设计中承担的是「测量稳健性」而非「因果外生性」的角色: 它以并排轨证明「语调结论不由某一测量技术 (投票/均值)、某一模型 (三家之一)、某一语境范围 (三轨)、某一聚合权重 (等权/vw/mw/hw) 驱动」, 但语调本身相对结果变量的内生性 (反向因果、遗漏变量、媒体选择性报道) 须由另一套工具变量设计承接。本项目的 IV 扩展 (iv_extensions.py, runner 步骤 8z) 提供三引擎: 同组 leave-one-out 同伴均值 (剔除自身后同类银行的语调暴露, 阻断自身特异冲击回流)、广义 Bartik (以基期媒体来源份额 × 全国语调变动构造份额-移动工具, 方法学依据见 Goldsmith-Pinkham 等 2020 的 Bartik 工具解剖)、以及媒体来源 house-style 暴露 (以外生的媒体文体倾向作暴露)。本家族任一并排轨都可作为这些 IV 设计的内生自变量, 其测量稳健性与 IV 的外生性识别是两条正交的防线, 不可互相替代 — 前者答「测量对不对」, 后者答「关系是不是因果」。此外, 本家族列在推断层面须与聚类稳健标准误、必要时的 wild bootstrap (MacKinnon & Webb, 2017; 弱工具与少簇情形见 Wang & Zhang, 2024) 配套, 以应对银行-年度面板在 T 短、簇不平衡下的推断偏差; 跨模型/跨方法的族错误率控制则统一交由 Romano & Wolf (2005) 步降法在根级模板 27_tableA12 执行, 而非在本家族内部临时校正。这一「测量稳健性并排 + 外生性 IV + 步降 FWER + wild bootstrap 推断」的四层识别纪律, 是本家族列进入任何主回归时的完整规程。

【与相邻测度的构念区分】
本家族须与三个相邻家族严格区分。其一, 与共识投票轨 llm_vote_tone 区分: llm_vote_tone 是三家「多数投票」共识 (P1 论文的 treatment.primary canonical headline), 走的是离散类别投票再折算; 本家族 llm_models_avg_tone 是三家连续语调分的算术均值-ensemble, 是 headline 的均值型稳健替代, 二者构念同源但聚合算子不同 (投票 vs 均值), 不可混用为同一 headline。其二, 与词典均值 dict_avg_tone、BERT 均值 bert_avg_pos/neg 区分: 那是另两法的 ensemble, 与本家族分属情感三法的不同支, 互为跨方法稳健但不是同一测度。其三, 与逐模型列 (gpt54nano_tone 等) 区分: 后者是集成的构成元, 单独作跨厂商稳健轨; 本家族是其汇总。换嵌入模型对本家族零影响 — 情感 LLM 与嵌入模型完全解耦, stage 21 的三家投票与 Qwen/text-embedding-3-large 嵌入无关。其四, 须与情感三法的另两法集成列区分: dict_avg_tone 是六部中文金融情感词典的跨词典均值, bert_avg_pos/neg/neu 是三分类 BERT 模型的跨模型均值; 它们与本家族分属大模型、词典、BERT 三支, 各自内部集成后再作跨方法三角互证, 但绝非同一测度, 不可并入同一自回归的右手侧, 也不可混进同一 over-identified Hansen J。这一「方法内集成 + 跨方法并排」的双层结构是本项目情感测量稳健性的骨架: 方法内以多模型/多词典平均降特异性噪声, 方法间以三法互证暴露任一方法的系统偏倚, 二者共同支撑「语调结论不由某一测量技术驱动」的论断, 与 van Atteveldt 等 (2021) 倡导的多方法效度三角、Algaba 等 (2020) 的多情感源整合框架一脉相承。正因如此, 本家族在论文中的定位始终是「均值型稳健替代」而非孤立主测度: 它与投票 headline、逐模型轨、词典均值、BERT 均值一同进入稳健性面板, 任一测度单独失真都不足以撼动在多测度间稳定复现的语调结论。其五, 须与本家族内部的离散度轨 (std) 及跨模型分歧构念严格区分: llm_models_avg_tone_std{track} 度量的是「每家模型 within-bank-year 逐篇语调标准差」再跨三家取均值, 即「同一模型眼中年内报道语调有多分散」, 反映的是媒体叙事本身的内部分歧; 这与「三家模型彼此之间对同一银行-年度语调判断的不一致度」(bert_xmodel 型跨模型异质度量所刻画的构念) 是两回事, 前者是标注对象 (报道) 的分歧, 后者是标注者 (模型) 的分歧, 混用会把媒体分歧误读为模型不可靠。其六, 须与情感的水平-强度信息边界对齐: 均值-ensemble 保留连续语调强度 (对离群家敏感但信息完整), 投票 headline 丢弃强度只留类别多数 (对离群家稳健但损失强度), 二者在极化样本上会给出方向一致而量级不同的读数, 论文并排二者正是为了让「强度是否驱动结论」这一问可被独立检验。这些边界共同保证本家族每一列在稳健性面板中占据一个不可被其它列替代的、语义明确的位置, 避免了 variable-farm 式的冗余堆列质疑。

【已知局限与稳健性梯子】
局限有三。其一, 均值-ensemble 假定三家误差近似独立且零均值; 若三家共享同一预训练偏倚 (如对中文官媒正面表述的系统性高估), 平均无法消除该共同成分 — 这正是保留 per-model 轨与词典/BERT 跨方法轨互证的原因。其二, 大模型情感是生成回归元, 直接作自变量会带来测量误差衰减与推断偏差 (Ludwig 等, 2026), 论文层以标准化系数、跨模型稳健性与工具变量扩展缓解。其三, 早期试跑 T=2 面板上 ss/tech/app 等稀疏子样本轨可能零方差或大量 NaN, 属预期退化, 生产 T=19 面板方能充分识别。稳健性梯子由本家族并排轨天然构成: 三轨互证语境敏感度、三套加权互证对显著性/权威/新颖度赋权的敏感度、两分类维度互证叙事类型异质性、_std 轨提供离散度侧信息、_z 轨提供可比标度 — 每条梯子各自 just-identified 并排, 梯子间正交不交叉, 严禁混进同一 over-identified Hansen J。全流程 $0 无网络 (纯 pandas/numpy 面板聚合, 逐位可复现), golden 锚由冻结的 _llm_cache.db 与 Prompt v8 保证。

【已知局限与稳健性梯子 (续): 加权、分类、离散度三类扩展的角色】
本家族在 canonical 之外扩出三类正交变体, 各服务不同的稳健性追问。加权类 (vw/mw/hw) 追问「聚合权重是否驱动结论」: 等权把每篇报道视为等价信号, 而现实中报道在显著性 (vw, 提及密度/版位)、来源权威 (mw, 媒体分层)、新颖性 (hw, 羊群衰减折价重复稿) 上高度异质。三套加权各以一种理论上有依据的权重重聚合, 若语调结论在等权与三加权间稳定, 即排除了「结论由某类报道的机械占比驱动」的质疑; 这一思路直接继承 Hassan 等 (2019) 的价值/提及加权文本测度与 Tetlock (2007) 对陈旧新闻信息折减的洞见。分类维度类 (tech/app) 追问「叙事类型异质性」: 把样本切为技术型与应用型金科两个子样本分别测语调, 检验媒体对「技术故事」与「应用故事」的情感基调是否系统性不同, 与本项目 P3/P4 论文的 substance/locus 维度呼应。离散度类 (std) 追问「语调分歧」: 度量年内报道语调的内部分散度而非水平, 作分歧/不确定性侧信息或调节变量。标准化类 (_z) 则纯为标度对齐, 不改构念。铁律统摄全族: 上述三轨、三加权、两分类、离散度、标准化诸轨, 各自 just-identified 并排、互为稳健性不分主次, 梯子间正交不交叉, 严禁任意组合混进同一 over-identified Hansen J — 因它们是同一构念的高度共线替代, 混入同一 GMM 会伪造过度识别、扭曲 J 统计量。真正的跨模型族 FWER 控制唯一交由根级模板 27_tableA12_cross_model_fwer 以 Romano & Wolf (2005) 步降法执行。

【已知局限与稳健性梯子 (续): 生成回归元与测量误差】
把大模型情感直接放进计量模型作自变量, 本质上是使用「生成回归元」(generated regressor): 语调不是直接观测量, 而是模型对文本的预测输出, 因而携带非零测量误差。Ludwig 等 (2026) 系统刻画了这一情形的计量后果 — 若测量误差与真值负相关 (大模型对极端语调有向中回归的收缩倾向), 直接回归会产生衰减偏差, 使系数向零偏; 若误差与其它协变量相关, 还会污染这些协变量的系数。均值-ensemble 通过对三家独立误差取平均, 缩小了误差方差 (在独立零均值假设下方差约降至单模型的三分之一), 从而缓解 (而非消除) 衰减。论文层进一步以三条防线加固: 其一, 用标准化系数 (_z 轨) 使跨测度可比、便于评估效应量级的稳健性; 其二, 以逐模型、投票、词典、BERT 四重跨方法并排, 任一方法特异的误差都会在互证中暴露; 其三, 以工具变量扩展 (leave-one-out peer、广义 Bartik、媒体来源 house-style 暴露三引擎) 应对语调的潜在内生性。须再次强调本家族与相邻测度的边界: llm_models_avg_tone 是三家连续分的均值, llm_vote_tone 是三家离散类的多数投票 (P1 headline), 二者聚合算子不同、绝不互替为同一 headline; 逐模型列是集成的构成元而非集成本身; 词典/BERT 均值是另两法的集成而非本法。数据溯源方面, 上游报道来自 stage 00 普查确认的去重媒体语料 (生产口径约 1,819 万条媒体报道, 2007–2025, 报纸类占绝对多数), 经 stage 11–13 的银行识别、金科识别、共现硬过滤后进入 stage 21 逐篇打分; 早期试跑面板仅 T=2 (约 220 行) 为试跑规模, 诸多稀疏子样本轨 (ss、tech、app 及其组合) 在此规模下零方差或大量 NaN 属预期退化, 唯生产 T=19 面板方能对全部并排轨充分识别。

## VAR: llm_models_avg_tone_app_ctx

【变体差分】
本列是「应用型金科」分类维度子样本 × ctx 轨的三家 LLM 均值-ensemble 语调。相对家族 canonical (llm_models_avg_tone_full, 全样本、full 轨、等权), 本列有两处差分。其一是分类维度条件: 仅在该银行该年被判为「应用型金科」(application-oriented fintech, 即以金科应用场景/落地为叙事重心) 的报道子集上重算; 该子样本以 n_articles_app 为存在前提, 若该维度计数列缺失则整段不生成 (geography.py 的 if 守卫)。其二是轨道差分: ctx 轨文本 = 标题 prepend + 实体上下文窗口 (content_ctx), 相对 full 轨剔除了与目标实体无邻近关系的正文段落, 更聚焦银行×金科的局部语境。计算上仍是对三家 {model}_tone_app_ctx 取行均值 (_safe_mean, 缺列优雅 NaN、per-model 独立降级)。本列与同族 app_full、app_ss 构成 app 维度的三轨并排, 与 tech 维度三列构成分类维度的正交对照。作为 conditional-on-full 的 ctx 稳健轨, 其行宇宙是 full 留篇集子集, 分子分母严格逐轨、不借 full 分母。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。在早期试跑 T=2 面板上, 该子样本稀疏时可能零方差或大量 NaN, 属预期退化。ctx 轨与 app 维度的叠加使本列在语境与叙事类型两个方向同时收紧: 它只看应用型金科报道、又只取实体上下文窗口, 因此对「银行在普惠/场景金融叙事中被局部提及时的情感基调」最为敏感, 与 app_full 的全文口径互证语境范围对该子样本语调的影响。

## VAR: llm_models_avg_tone_app_full

【变体差分】
本列是「应用型金科」分类维度子样本 × full 轨的三家 LLM 均值-ensemble 语调。相对家族 canonical (全样本 full 轨等权), 唯一差分是分类维度条件: 仅在该银行该年被判为「应用型金科」的报道子集上重算集成语调, 以 n_articles_app 为存在前提。轨道仍是 full (标题 prepend + 全文正文), 与 canonical 同轨、同为主门控口径 (full-only 留篇), 因此本列是「若把样本限定在应用型金科叙事时, 语调水平是否移动」的直接检验。计算为对三家 {model}_tone_app_full 取行均值, _safe_mean 缺列优雅 NaN, per-model 独立降级。本列与 tech_full 构成同轨下两种金科叙事类型的对照: app_full 聚焦金融科技的应用/普惠/场景落地叙事, tech_full 聚焦底层技术/研发叙事; 二者语调差可揭示媒体对「应用故事」与「技术故事」的情感偏好差异, 呼应 Gomber 等的金科分类学与本项目 P3/P4 论文的 substance/locus 维度。作为分类维度稳健轨, 与家族三轨/三加权/std/z 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。作为与 canonical 同轨 (full) 仅差分类维度的一列, 本列最直接地隔离出「应用型金科叙事」这一样本切分对集成语调水平的净效应: 若 app_full 相对 canonical 的全样本语调系统性偏移, 即证明媒体在报道银行的金科应用落地时带有可测量的情感偏向, 而该偏向不被技术型叙事稀释。生产 T=19 面板方能对该子样本充分识别。

## VAR: llm_models_avg_tone_app_ss

【变体差分】
本列是「应用型金科」分类维度子样本 × ss 轨的三家 LLM 均值-ensemble 语调。相对 canonical, 差分为分类维度条件 (仅应用型金科报道子集, 以 n_articles_app 为前提) 叠加 ss 轨道。ss 轨文本 = 标题 + 银行∧金科同句±N 窗 (content_ss); 遵循镜像 ctx 的回退公理: 该篇无「银行∧金科同句共现」时 content_ss 回退全文正文、ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母口径。因此本列在应用型金科且存在同句共现的报道上最为聚焦, 度量的是「银行与金科被同句提及、且叙事偏应用场景时」的集成语调。计算为对三家 {model}_tone_app_ss 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。本列是 app 维度三轨中语境最紧的一条, 与 app_full、app_ctx 并排互证语境敏感度。作为 conditional-on-full 的 ss 稳健轨, 行宇宙为 full 留篇集子集, 分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。早期试跑 T=2 面板上 ss 子样本极稀疏, 大量 NaN 或零方差属预期退化, 须待生产 T=19 面板充分识别。本列在 app 维度三轨中语境与叙事双重最紧, 其相对 app_full 的偏移可视为「把注意力进一步收拢到银行与金科同句共现的应用型报道」所带来的语调变化, 是三轨梯子在应用维度上的最保守估计端。

## VAR: llm_models_avg_tone_ctx

【变体差分】
本列是全样本、等权、ctx 轨的三家 LLM 均值-ensemble 语调, 是家族 canonical (llm_models_avg_tone_full) 的 ctx 轨孪生。唯一差分为轨道: ctx 轨文本 = 标题 prepend + 实体上下文窗口 (content_ctx), 相对 full 轨 (全文正文) 剔除了与银行/金科实体无邻近关系的段落, 只保留实体周边窗口, 因此测的是「聚焦到实体局部语境时」的集成语调。计算为对三家 {model}_tone_ctx 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。在 full-only 门控口径下, 本列是 conditional-on-full 的首要 robustness 轨: 其行宇宙是 full 留篇集子集, 分子分母严格逐轨、不借 full 分母。ctx 轨相对 full 的价值在于, 当一篇长报道仅在局部提及目标银行×金科时, full 轨会把无关正文的语调稀释进来, 而 ctx 轨聚焦实体窗口给出更「就事论事」的情感; 二者语调差本身即一条关于「语境范围如何影响情感测量」的稳健性证据。本列与 llm_models_avg_tone_full、llm_models_avg_tone_ss 构成三轨并排, 各自 just-identified、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J (三轨铁律)。其标准化版本见 llm_models_avg_tone_ctx_z。作为全样本等权的 ctx 轨, 本列是三轨稳健性梯子的「中间松紧度」一端: 比 full 紧 (剔无关正文段落)、比 ss 松 (不要求银行与金科同句), 因此在语境范围连续谱上提供了中点估计, 使 full→ctx→ss 的语调走势可被读作一条关于语境收紧方向的单调 (或非单调) 曲线。

## VAR: llm_models_avg_tone_ctx_z

【变体差分】
本列是 llm_models_avg_tone_ctx 的逐年度截面标准化 (z-score) 版本。计算口径以源码 standardize_panel_variables 为准: 对每个 year 分组, 仅取 n_articles>0 且该年内有效样本≥3 的银行, 在该年度横截面内减年均值、除年标准差 (年标准差近零则跳过), 得到该年内的标准化值; 各年各自定标, 故整体是分段仿射 (piecewise affine) 变换、各年 scale 不同, 而非在全面板样本上做单一均值 0 标准差 1 的线性变换。相对其未标准化母列, 本列不改变构念、不改变模型/轨道/权重, 仅改变标度并顺带剔除年度共同成分 — 这是 Fama-MacBeth 式的逐横截面标准化, 目的是让同一年内不同银行的 ctx 轨集成语调以年内标准差为单位可比, 便于进入回归系数、森林图与跨测度比较, 避免原始语调量纲 (约 [-1,1]) 与其它自变量量纲不一致导致系数难以横向解读。须澄清一个易被误写的性质: 由于逐年定标, 本列并非母列在全样本上的单调线性变换, 因此不保证与 ctx 母列在全样本单变量回归中给出等价的 t 值 — 仅在锁定单一年份的年内截面上, 本列相对母列才是保符号、保秩序的线性重标度。本列属标度稳健轨, 与家族 full_z、ss_z 构成三轨的截面标准化并排。须注意: z 值依赖各年横截面分布, 样本变动 (如换语料、换年窗、年内可用银行数变化) 会移动标准化基准, 故 z 列的绝对数值不跨样本、不跨年可直接比水平, 只在同一年度截面内可比。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。早期试跑 T=2 面板每年可用银行少、方差小, 甚至可能因年内有效样本<3 而整年落 NaN, 标准化后数值高度敏感于个别银行-年度, 生产 T=19 面板方稳定。本列与母列 llm_models_avg_tone_ctx 的分别就是这一逐年重标度: 凡回归需要把 ctx 轨语调与其它逐年标准化协变量置于同一年内标准差刻度上比较边际效应时用本列, 需保留原始约 [-1,1] 语调量纲的语义解读时用母列。

## VAR: llm_models_avg_tone_full

【变体差分】
本列是家族 canonical, 也是本 core 家族的核心列: 全样本、等权、full 轨的三家 LLM 均值-ensemble 语调。它是「跨厂商大模型集成的银行-年度新闻情感」这一构念最正统的落地。轨道为 full = 标题 prepend + 全文正文 (content_full), 与 2026-06-29 确立的 full-only 留篇门控口径完全对齐: 一篇报道是否计入银行金科样本, 只看该篇 full 轨的 llm_verified_full == True, 因此 full 轨是主门控轨, ctx/ss 皆为其 conditional-on-full 子集。计算为对三家 bank-year 聚合值 (gpt54nano_tone_full、gemini31_tone_full、deepseekv4_tone_full) 以 _safe_mean 取行均值; 每家的 bank-year 值是该银行该年内所有留篇报道逐篇 full 轨语调的等权算术均值。_safe_mean 只对实际存在的模型列求平均, 缺列 (某家该轨未落盘) 优雅返回 NaN 而非崩溃, 实现 per-model 独立降级 — 这与 co-primary 嵌入的 both-or-neither 语义刻意不同: 嵌入双轨任一缺则同置 NaN, 而 LLM 均值某家缺仅拉低有效模型基数、其余家仍照算。

本列在构念上区别于两个近邻。其一是 llm_vote_tone_full: 那是三家「多数投票」共识 (P1 论文 treatment.primary 的 canonical headline), 走离散类别投票再折算; 本列是三家连续语调分的算术均值。投票对极端异议稳健但丢弃强度信息, 均值保留强度但对离群家敏感; 二者是同一构念的两种聚合算子, 互为稳健替代, 但绝不可当作同一 headline 混用。CLAUDE.md 的「LLM 三家段」正是点名 llm_models_avg 为均值-ensemble 变体、区别于投票 headline。其二是逐模型列 (gpt54nano_tone_full 等): 那是本列的构成元, 单列作跨厂商稳健轨; 本列是三家的汇总共识。

方法学上, 均值-ensemble 的效度依据来自多标注者/多模型平均逼近人类共识的证据 (Gilardi 等, 2023; Chen 等, 2025 的 LLM ensemble 综述), 以及金融文本大模型情感优于零样本单模型的实证 (Fatouros 等, 2023; Kirtac & Germano, 2024; 中文场景见 Lan 等, 2025)。相对词典法 (Loughran & McDonald, 2016; Du 等, 2022) 与 FinBERT (Huang 等, 2023), 大模型集成在语境敏感度上更强, 但作为生成回归元带来测量误差, 其计量后果由 Ludwig 等 (2026) 系统刻画 — 论文层以标准化系数、跨模型稳健性 (逐模型/投票/词典/BERT 四重互证)、以及 Romano & Wolf (2005) 步降式 FWER 控制 (根级模板 27_tableA12) 加以约束。识别铁律: 本列与逐模型轨、投票轨、词典/BERT 均值轨、三轨、三加权各自 just-identified 并排, 互为稳健性不分主次, 严禁混进同一 over-identified Hansen J (这些是同构念高度共线替代, 混入会伪造过度识别、扭曲 J 检验)。本列的标准化版本为 llm_models_avg_tone_full_z, 分类维度对照见 tech_full/app_full, 加权对照见 vw/mw/hw_full, 离散度侧信息见 std_full。在论文组合中, 本列是 P1 (bank_fintech_tone) 主线的语调 headline 的均值型稳健替代: P1 的 treatment.primary 用投票轨 llm_vote_tone_full, 而本列以均值-ensemble 并排验证「结论不因聚合算子从投票改为均值而变」。作为 core 列, 本列亦是本家族一切加权/分类/标准化变体的参照基准 — 后者皆以「相对等权 full 轨移动了什么」来解读。数值上本列约落在 [-1,1], 负值表示该银行该年金科报道整体偏负面、正值偏正面; bank-year 内的逐篇分先在各家模型内等权平均, 再跨三家取行均值, 故本列对年内报道数敏感 (报道极少的银行-年度均值噪声大, 论文以最小报道数门槛或加权稳健轨缓解)。全流程 $0 无网络、纯面板聚合、逐位可复现, golden 锚由冻结 _llm_cache.db 与 Prompt v8 保证; 换嵌入模型对本列零影响 (情感 LLM 与嵌入完全解耦)。本列亦是全家族命名的 canonical 参照点: 无后缀即等权 full 轨, 一切带 vw/mw/hw/tech/app/std/z 后缀的列都以「相对本列移动了什么」为解读锚。

## VAR: llm_models_avg_tone_full_z

【变体差分】
本列是 core 列 llm_models_avg_tone_full 的逐年度截面标准化 (z-score) 版本。口径以源码 standardize_panel_variables 为准: 对每个 year 分组, 仅取 n_articles>0 且该年内有效样本≥3 的银行, 在年度横截面内减年均值、除年标准差 (年标准差近零跳过), 各年各自定标 — 因此本列是分段仿射变换、各年 scale 不同, 而非在全面板上做单一均值 0 标准差 1 的线性变换。相对其母列, 构念、模型集、轨道、权重全同, 唯一差分是标度: 把约 [-1,1] 的原始语调按各年横截面重标度为年内标准差单位, 并顺带剔除年度共同成分 (Fama-MacBeth 式逐横截面标准化), 便于作为主测度以年内可比系数进入回归与跨测度森林图。须澄清: 因逐年定标, 本列并非母列在全样本上的单调线性变换, 故不保证与 full 母列在全样本单变量回归中给出等价 t 值 — 仅在锁定单一年份的年内截面上, 本列相对母列才是保符号、保秩序的线性重标度。本列常用于需要跨自变量量纲对齐的规格 (如把新闻语调与财务比率、控制变量放在同一逐年标准化标度上比较边际效应)。作为标度稳健轨, 与 ctx_z、ss_z 构成截面标准化三轨并排。须注意 z 值依赖各年横截面分布, 换语料/年窗/年内可用银行数会移动基准, 绝对数值不跨样本、不跨年可直接比水平, 仅同年度截面内可比。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。早期试跑 T=2 面板每年可用银行少、方差小, 甚至可能因年内有效样本<3 而整年落 NaN, 标准化数值对个别银行-年度敏感, 生产 T=19 面板方稳定。由于母列即 core headline (full 轨), 本列是把主测度接入需要标准化标度的规格 (如系数量级横向对比、多测度森林图) 时的首选形式, 与 ctx_z、ss_z 共同保证逐年标准化标度在三轨间口径一致。

## VAR: llm_models_avg_tone_hw_ctx

【变体差分】
本列是 herd 加权 (hw) × ctx 轨的三家 LLM 均值-ensemble 语调。相对 canonical (等权 full 轨), 差分为聚合权重与轨道。hw 加权在 bank-year 聚合层以 stage 24 herd_decay 产出的羊群/新颖度衰减权重加权: 逐篇聚合取 Σ(w_herd·tone)/Σw_herd, 对重复转载、陈旧信息做折价, 保留新颖、原创、领先的报道更高权重。其概念动机是「陈旧新闻信息含量折减」, 呼应 Tetlock (2007) 及媒体信息新颖性文献 — 若干家媒体反复转载同一稿件不应等同于若干条独立信号。轨道为 ctx (标题 + 实体上下文窗口)。计算为对三家 {model}_tone_hw_ctx 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。本列与 hw_full、hw_ss 构成 hw 加权三轨, 与 vw (显著性加权)、mw (媒体权威加权) 构成三套加权的正交对照: vw 问「显著的报道」、mw 问「权威媒体的报道」、hw 问「新颖非重复的报道」各自给出的集成语调是否移动。herd 权重来自 stage 24 herd_decay, 其三轨源列 herd_weight_{full,ctx,ss} 若缺失, encode 层有 legacy 兜底避免三轨源塌陷指向同一列 (F1 修复), 保证本 ctx 轨权重不被 full 权重冒名顶替。作为 conditional-on-full 的 ctx 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。本列在语境宽度 (ctx 窗口) 与新颖度赋权两个方向同时约束, 是 hw 加权三轨中兼顾聚焦与去重的中间松紧读数。

## VAR: llm_models_avg_tone_hw_full

【变体差分】
本列是 herd 加权 (hw) × full 轨的三家 LLM 均值-ensemble 语调。相对 canonical, 唯一差分是聚合权重: 以 stage 24 herd_decay 的羊群/新颖度衰减权重在 bank-year 层加权聚合 Σ(w_herd·tone)/Σw_herd, 对重复转载与陈旧信息折价。轨道仍为 full (与 canonical 同轨、同主门控口径), 因此本列是「若按新颖度而非等权聚合, full 轨集成语调是否移动」的直接检验。计算为对三家 {model}_tone_hw_full 取行均值, _safe_mean 缺列优雅 NaN、per-model 独立降级。hw 的价值在于纠正媒体转载放大效应: 一条被百家转载的旧稿在等权口径下会主导 bank-year 均值, 而 hw 口径把它折价为接近单条信号, 使集成语调更贴近「独立信息事件」的情感重心。这与 Tetlock (2007) 关于陈旧新闻信息含量的洞见一致。本列与 vw_full、mw_full 并排, 三套加权互证赋权敏感度; 与 hw_ctx、hw_ss 并排, 互证语境敏感度。作为加权稳健轨, 与家族三轨/分类维度/std/z 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。herd_weight 的三轨源列若缺失, encode 层有 legacy 兜底防止三轨源指向同一列 (已由 F1 修复), 保证三轨语义不塌陷。在 full-only 门控口径下本列与 canonical 同轨, 因此其相对 canonical 的偏移可被干净地归因于「等权 → 新颖度加权」这一单一变化, 是三套加权中检验转载放大效应最直接的一条 full 轨证据。

## VAR: llm_models_avg_tone_hw_ss

【变体差分】
本列是 herd 加权 (hw) × ss 轨的三家 LLM 均值-ensemble 语调。相对 canonical, 差分为 herd 加权聚合叠加 ss 轨道。hw 权重取自 stage 24 herd_decay 的新颖度衰减权重, 逐篇聚合 Σ(w_herd·tone)/Σw_herd 对重复转载折价。ss 轨文本 = 标题 + 银行∧金科同句±N 窗 (content_ss), 遵循镜像 ctx 的回退公理: 无同句共现时回退全文正文、ss_is_fallback 置 True、共享 n_articles 分母。因此本列是三套加权 × 三轨组合中语境最紧且赋权最重新颖度的一条: 度量「银行与金科被同句提及、且按新颖度折价重复稿后」的集成语调。计算为对三家 {model}_tone_hw_ss 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。本列与 hw_full、hw_ctx 并排互证 herd 加权下的语境敏感度。作为 conditional-on-full 的 ss 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。早期试跑 T=2 面板上 ss 子样本极稀疏, 大量 NaN 或零方差属预期退化, 待生产 T=19 面板充分识别。本列把新颖度折价与同句强共现两重收紧同时施加, 因此在 hw 加权三轨中信息最纯、样本最薄: 它只对「银行与金科同句提及、且非重复转载」的报道计权, 是转载放大与语境宽度双重稳健性检验的交汇点, 提供 hw 加权 × 三轨组合中最保守的一个估计端。

## VAR: llm_models_avg_tone_mw_ctx

【变体差分】
本列是 media-authority 加权 (mw) × ctx 轨的三家 LLM 均值-ensemble 语调。相对 canonical, 差分为聚合权重与轨道。mw 加权按媒体权威分层加权 (compute_media_authority_weights): 依据媒体来源的权威等级赋权, 权威媒体 (如中央级、财经权威) 的报道在 bank-year 聚合中占更高权重, 未评级媒体取默认权重; 逐篇聚合取 Σ(w_auth·tone)/Σw_auth。其概念动机是媒体权威性与信息可信度/市场影响力正相关, 呼应本项目对媒体异质性 (官媒/市场化媒体) 的建模以及金融媒体影响力文献 (Tetlock, 2007 一脉)。轨道为 ctx (标题 + 实体上下文窗口)。计算为对三家 {model}_tone_mw_ctx 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。本列在 export.py 有 Stata 标签 'LLM Avg Tone (Media-Auth Wt, Ctx)'。与 mw_full、mw_ss 构成 mw 三轨, 与 vw、hw 构成三套加权正交对照。媒体权威权重由 compute_media_authority_weights 依 config 媒体分层表赋值, 未评级来源取默认权重, 因此本列相对等权 ctx 轨的偏移直接度量「权威声源在实体上下文语境中的语调是否系统性偏离一般声源」。本列在媒体权威赋权与实体窗口聚焦两个方向同时约束, 是 mw 加权三轨中兼顾声源可信度与语境宽度的中间松紧读数。作为 conditional-on-full 的 ctx 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: llm_models_avg_tone_mw_full

【变体差分】
本列是 media-authority 加权 (mw) × full 轨的三家 LLM 均值-ensemble 语调, 在 export.py 有 Stata 标签 'LLM Avg Tone (Media-Auth Wt, Full)'。相对 canonical, 唯一差分是聚合权重: 按媒体权威分层 (compute_media_authority_weights) 加权, 权威媒体报道占更高权重, 逐篇聚合 Σ(w_auth·tone)/Σw_auth。轨道仍为 full。本列检验「若按媒体权威而非等权聚合, full 轨集成语调是否移动」— 若权威媒体系统性更正面/更负面, mw 口径会相对等权口径偏移, 该偏移本身即媒体权威异质性的证据。计算为对三家 {model}_tone_mw_full 取行均值, _safe_mean 缺列优雅 NaN、per-model 独立降级。mw 与 vw (显著性加权)、hw (新颖度加权) 三者赋权维度正交: mw 问「谁说的」、vw 问「说得多显著」、hw 问「是否新颖非重复」。在中国媒体制度背景下 (官媒与市场化媒体在语调倾向上系统性不同), mw 加权尤其能揭示权威声源的情感基调如何主导银行-年度叙事。作为加权稳健轨, 与家族三轨/分类维度/std/z 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。本列在 export.py 有 Stata 标签 'LLM Avg Tone (Media-Auth Wt, Full)', 与 canonical 同轨仅差权重, 因此是三套加权中检验「谁在说话如何驱动银行金科语调」的最主力 full 轨证据, 尤其在官媒与市场化媒体语调基调分化的中国媒体制度下有实质识别力, 与本项目媒体异质性 (官媒/市场化/深度/日频) 一族的 tone_official/tone_market 等切分互补。

## VAR: llm_models_avg_tone_mw_ss

【变体差分】
本列是 media-authority 加权 (mw) × ss 轨的三家 LLM 均值-ensemble 语调。相对 canonical, 差分为媒体权威加权叠加 ss 轨道。mw 权重按媒体权威分层 (compute_media_authority_weights), 逐篇聚合 Σ(w_auth·tone)/Σw_auth。ss 轨文本 = 标题 + 银行∧金科同句±N 窗 (content_ss), 遵循镜像 ctx 的回退公理: 无同句共现时回退全文正文、ss_is_fallback 置 True、共享 n_articles 分母。因此本列度量「银行与金科被同句提及、且按媒体权威加权后」的集成语调。计算为对三家 {model}_tone_mw_ss 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。本列与 mw_full、mw_ctx 并排互证 mw 加权下的语境敏感度, 与 vw_ss、hw_ss 并排互证同轨下不同赋权维度。作为 conditional-on-full 的 ss 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。早期试跑 T=2 面板上 ss 子样本极稀疏, 大量 NaN 或零方差属预期退化, 待生产 T=19 面板充分识别。本列把媒体权威加权与同句强共现两重条件叠加, 是 mw 加权三轨中样本最薄的一条: 它只对「银行与金科同句提及」的报道按权威分层计权, 交汇了「谁说的」与「多聚焦」两个稳健性问题, 提供 mw 加权 × 三轨组合中最保守的一个估计端; ss 回退语义确保稀疏共现银行-年度不坍缩为空, 而是优雅退化为按权威分层加权的全文估计, 与 mw_full、mw_ctx 并排互证权威赋权在最紧语境下的稳健性。

## VAR: llm_models_avg_tone_ss

【变体差分】
本列是全样本、等权、ss 轨的三家 LLM 均值-ensemble 语调, 是 canonical 的 ss 轨孪生。唯一差分为轨道: ss 轨文本 = 标题 + 银行∧金科同句±N 窗 (content_ss, 窗宽由 config filtering.yaml 的 ss_sentence_radius 控制, 默认 1)。ss 轨遵循镜像 ctx 的回退公理: 该篇无「银行∧金科同句共现」时 content_ss 回退为全文正文、ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母口径; 若上游 FINTECH_AC=None 则 ss_is_fallback 全 True 优雅降级。因此 ss 轨在存在同句共现的报道上最聚焦「银行与金科被同一句子提及」的强共现语境, 是三轨中语境最紧的一条。计算为对三家 {model}_tone_ss 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。在 full-only 门控下, 本列是 conditional-on-full 的稳健轨: 行宇宙是 full 留篇集子集, 分子分母严格逐轨、不借 full 分母。本列与 llm_models_avg_tone_full、llm_models_avg_tone_ctx 构成三轨并排, 各自 just-identified、互为稳健性不分主次, 严禁三轨混进同一 over-identified Hansen J (三轨铁律)。其标准化版本见 llm_models_avg_tone_ss_z。早期试跑 T=2 面板上 ss 轨可能大量回退或零方差, 属预期退化。作为全样本等权的 ss 轨, 本列是三轨稳健性梯子最紧的一端: 当 full→ctx→ss 语调走势在此端出现拐折, 常提示「银行与金科强共现语境」下的情感基调与全文口径不同, 是语境敏感度检验的关键读数点。回退语义确保稀疏共现银行-年度不至坍缩为空, 而是优雅退化为偏保守的全文估计。

## VAR: llm_models_avg_tone_ss_z

【变体差分】
本列是 llm_models_avg_tone_ss 的逐年度截面标准化 (z-score) 版本。口径以源码 standardize_panel_variables 为准: 对每个 year 分组, 仅取 n_articles>0 且该年内有效样本≥3 的银行, 在年度横截面内减年均值、除年标准差 (年标准差近零跳过), 各年各自定标 — 因此本列是分段仿射变换、各年 scale 不同, 而非在全面板上做单一均值 0 标准差 1 的线性变换。相对其母列, 构念、模型集、轨道、权重全同, 唯一差分是标度: 把约 [-1,1] 的原始语调按各年横截面重标度为年内标准差单位, 并顺带剔除年度共同成分 (Fama-MacBeth 式逐横截面标准化), 便于以年内可比系数进入回归与跨测度森林图。须澄清: 因逐年定标, 本列并非母列在全样本上的单调线性变换, 故不保证与 ss 母列在全样本单变量回归中给出等价 t 值 — 仅在锁定单一年份的年内截面上, 本列相对母列才是保符号、保秩序的线性重标度。本列属标度稳健轨, 与 full_z、ctx_z 构成截面标准化三轨并排。须特别注意: ss 轨本身在稀疏共现银行-年度大量回退为全文或缺失, 逐年 z 标准化又要求年内有效样本≥3, 故本列在早期试跑面板上极易整年落 NaN、数值波动大, 换语料/年窗/年内可用银行数会移动标准化基准, 绝对数值不跨样本、不跨年可直接比水平、仅同年度截面内可比。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。生产 T=19 面板方能给出稳定的 ss 逐年标准化标度。本列与母列 llm_models_avg_tone_ss 唯一分别是标度: 需将最紧语境轨语调以年内标准差单位纳入跨测度可比规格时用本列, 需保留原始语调量纲语义时用母列; 因 ss 轨回退与稀疏叠加逐年 z 标准化的样本依赖性, 本列在早期试跑面板上的数值稳定性最弱。

## VAR: llm_models_avg_tone_std_ctx

【变体差分】
本列是 ctx 轨下「跨模型的 within-bank-year 语调离散度均值」, 度量对象与家族其余「语调水平」列根本不同 — 它测的是分散度而非水平。具体地, 每家模型在 bank-year 聚合时除产出均值 {model}_tone_ctx 外, 还产出该银行该年内逐篇 ctx 轨语调的标准差 {model}_tone_std_ctx (衡量年内报道语调有多分歧); 本列对三家的这个 within 离散度取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。因此高值意味着「三家模型都认为该银行该年的报道语调内部高度分化」(有的很正面、有的很负面), 低值意味着语调一致。这一分散度构念与本项目的媒体分歧 (bank_media_disagreement) 论文、以及金融文本情感波动作为不确定性代理的思路相关。相对家族水平列, 本列不进入「语调正负」的处理变量角色, 而作分歧/不确定性侧信息或调节变量。轨道为 ctx (标题 + 实体上下文窗口)。本列与 std_full、std_ss 构成离散度三轨并排, 与家族水平轨正交互补。作为 conditional-on-full 的 ctx 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。年内报道数过少 (如 n=1) 时标准差无定义或为 0, 属预期退化。须强调本列聚合的是「模型内 within-bank-year 逐篇语调标准差」再跨模型取均值, 而非「三家模型之间的分歧」(后者是 bert_xmodel 型跨模型异质度量的构念); 二者不可混淆。

## VAR: llm_models_avg_tone_std_full

【变体差分】
本列是 full 轨下「跨模型的 within-bank-year 语调离散度均值」。相对家族水平 canonical (llm_models_avg_tone_full 测语调正负水平), 本列差分在测度对象: 它是每家模型 within-bank-year 逐篇 full 轨语调标准差 {model}_tone_std_full 的三家行均值, 度量「该银行该年报道语调的内部分散程度」而非水平。计算为 _safe_mean 对三家离散度列取行均值, 缺列优雅 NaN、per-model 独立降级。高值 = 三家模型一致地观察到年内报道语调两极分化 (正负报道并存), 低值 = 报道语调整齐一致。这一构念可作媒体叙事分歧、信息环境不确定性的代理, 与均值水平轨正交: 两家银行可有相同的平均语调却截然不同的语调分散度。轨道为 full (与 canonical 同轨、同主门控口径)。本列与 std_ctx、std_ss 构成离散度三轨。在计量上, std 轨常作调节变量或稳健性侧证据 (如检验语调效应是否随语调分歧放大/衰减), 而非主处理变量。作为离散度稳健轨, 与家族三轨/三加权/分类维度/z 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。年内报道数过少时标准差无定义 (NaN) 或为 0, 属预期退化, 生产 T=19 面板方充分。作为 full 轨的离散度列, 本列是 std 三轨中样本最充分的一条, 常在论文中作为语调分歧的主离散度代理, 与语调水平 canonical (llm_models_avg_tone_full) 配对进入「水平×分歧」的交互或调节规格。

## VAR: llm_models_avg_tone_std_ss

【变体差分】
本列是 ss 轨下「跨模型的 within-bank-year 语调离散度均值」。相对家族水平列, 差分在测度对象 (语调分散度而非水平) 叠加 ss 轨道。它对三家 within-bank-year 逐篇 ss 轨语调标准差 {model}_tone_std_ss 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。ss 轨文本 = 标题 + 银行∧金科同句±N 窗 (content_ss), 遵循镜像 ctx 的回退公理: 无同句共现时回退全文正文、ss_is_fallback 置 True、共享 n_articles 分母。因此本列度量「在银行与金科强共现的报道上, 三家模型观察到的年内语调分散程度」。高值意味强共现语境下报道语调两极分化。本列与 std_full、std_ctx 构成离散度三轨并排, 与家族水平轨正交互补。作为 conditional-on-full 的 ss 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。早期试跑 T=2 面板上 ss 子样本极稀疏, 年内报道常仅一两篇致标准差无定义或为 0, 大量 NaN 属预期退化, 待生产 T=19 面板充分识别。本列是 std 三轨中最紧语境的离散度读数: 它度量「银行与金科强共现的报道内部语调有多分歧」, 与 std_full、std_ctx 并排可揭示语调分歧是否随语境收紧而放大或收敛, 是分歧构念的语境敏感度侧证。年内报道极少时标准差无定义或为 0, 属预期退化。

## VAR: llm_models_avg_tone_tech_ctx

【变体差分】
本列是「技术型金科」分类维度子样本 × ctx 轨的三家 LLM 均值-ensemble 语调。相对 canonical, 差分为分类维度条件叠加 ctx 轨道。技术型金科 (technology-oriented fintech) 指以底层技术/研发/基础设施为叙事重心的报道子集, 以 n_articles_tech 为存在前提, 该维度计数缺失则整段不生成。轨道为 ctx (标题 + 实体上下文窗口, content_ctx)。计算为对三家 {model}_tone_tech_ctx 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。本列与 app_ctx 构成同轨下两种金科叙事类型的对照: tech 聚焦技术/研发故事, app 聚焦应用/场景/普惠故事; 二者语调差揭示媒体对「技术故事」与「应用故事」的情感偏好差异。这一分类维度对照与本项目 P3 (substance)、P4 (locus) 论文的金科叙事分类学相关, 也呼应 Gomber 等的金科分类框架。作为 conditional-on-full 的 ctx 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族三轨/三加权/std/z 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。早期试跑 T=2 面板上该子样本稀疏, 零方差或大量 NaN 属预期退化。本列在语境 (ctx 窗口) 与叙事类型 (技术型金科) 两个方向同时收紧, 对「银行在自研核心系统、AI 风控等技术叙事中被局部提及时的情感基调」最敏感, 与 tech_full 的全文口径互证语境范围对技术型子样本语调的影响。

## VAR: llm_models_avg_tone_tech_full

【变体差分】
本列是「技术型金科」分类维度子样本 × full 轨的三家 LLM 均值-ensemble 语调。相对 canonical (全样本 full 轨等权), 唯一差分是分类维度条件: 仅在被判为「技术型金科」(以底层技术/研发为叙事重心) 的报道子集上重算集成语调, 以 n_articles_tech 为存在前提。轨道仍为 full (与 canonical 同轨、同主门控口径)。计算为对三家 {model}_tone_tech_full 取行均值, _safe_mean 缺列优雅 NaN、per-model 独立降级。本列是「若把样本限定在技术型金科叙事时语调水平是否移动」的直接检验, 与 app_full 构成两种叙事类型的核心对照: 媒体报道银行的技术能力 (如自研核心系统、AI 风控) 与报道其应用落地 (如普惠贷款、场景金融) 时的情感基调可能系统性不同, 该差异对理解银行金科叙事的媒体建构至关重要。作为分类维度稳健轨, 与家族三轨/三加权/std/z 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。生产 T=19 面板方能对该子样本充分识别, 早期试跑 T=2 面板上易零方差或大量 NaN, 属预期退化。作为与 canonical 同轨 (full) 仅差分类维度的一列, 本列最直接地隔离出「技术型金科叙事」样本切分对集成语调水平的净效应, 与 app_full 配对即构成媒体对「技术故事 vs 应用故事」情感基调差异的核心对照读数。

## VAR: llm_models_avg_tone_tech_ss

【变体差分】
本列是「技术型金科」分类维度子样本 × ss 轨的三家 LLM 均值-ensemble 语调。相对 canonical, 差分为分类维度条件 (仅技术型金科报道子集, 以 n_articles_tech 为前提) 叠加 ss 轨道。ss 轨文本 = 标题 + 银行∧金科同句±N 窗 (content_ss), 遵循镜像 ctx 的回退公理: 无同句共现时回退全文正文、ss_is_fallback 置 True、共享 n_articles 分母。因此本列度量「在技术型金科叙事且银行与金科强共现的报道上」的集成语调, 是 tech 维度三轨中语境最紧的一条。计算为对三家 {model}_tone_tech_ss 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。本列与 tech_full、tech_ctx 并排互证技术叙事下的语境敏感度, 与 app_ss 并排互证同轨下叙事类型异质性。作为 conditional-on-full 的 ss 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。早期试跑 T=2 面板上 tech×ss 双重稀疏, 大量 NaN 或零方差属预期退化, 待生产 T=19 面板充分识别。本列是 tech 维度三轨中语境与叙事双重最紧的一条, 其相对 tech_full 的偏移可视为「把注意力进一步收拢到银行与金科同句共现的技术型报道」所带来的语调变化, 是三轨梯子在技术维度上的最保守估计端, 与 app_ss 并排即构成叙事类型异质性在最紧语境下的对照。

## VAR: llm_models_avg_tone_vw_ctx

【变体差分】
本列是 value/salience 加权 (vw) × ctx 轨的三家 LLM 均值-ensemble 语调。相对 canonical (等权 full 轨), 差分为聚合权重与轨道。vw 加权在 bank-year 聚合层按新闻显著性权重加权: 权重取自 stage 11 news_salience 物化的报道显著性代理 (目标银行提及密度 mention_density、版位 front_page、导语、署名等), 逐篇聚合取 Σ(w·tone)/Σw, 给「更显著地报道了目标银行」的报道更高权重。其概念动机对标 Hassan 等 (2019) 以实体提及计数加权文本测度、以及注意力/显著性文献 (Tetlock, 2007 一脉): 一篇仅一笔带过银行的报道不应等同于一篇以该银行为主角的长篇报道。轨道为 ctx (标题 + 实体上下文窗口)。计算为对三家 {model}_tone_vw_ctx 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。本列与 vw_full、vw_ss 构成 vw 三轨, 与 mw (媒体权威加权)、hw (新颖度加权) 构成三套加权正交对照: vw 问「说得多显著」、mw 问「谁说的」、hw 问「是否新颖非重复」。显著性权重取自 stage 11 news_salience 物化的多种代理 (提及密度、版位、导语、署名), 与 mw 的媒体级权威、hw 的产出端新颖度正交, 论文须明写三者区分以防 variable-farm 质疑。本列在显著性赋权与实体窗口聚焦两个方向同时约束, 是 vw 加权三轨中兼顾主角性与语境宽度的中间松紧读数。作为 conditional-on-full 的 ctx 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: llm_models_avg_tone_vw_full

【变体差分】
本列是 value/salience 加权 (vw) × full 轨的三家 LLM 均值-ensemble 语调。相对 canonical, 唯一差分是聚合权重: 按新闻显著性权重 (目标银行提及密度、版位、导语、署名等 stage 11 news_salience 代理) 在 bank-year 层加权聚合 Σ(w·tone)/Σw。轨道仍为 full (与 canonical 同轨、同主门控口径), 因此本列是「若按显著性而非等权聚合, full 轨集成语调是否移动」的直接检验。计算为对三家 {model}_tone_vw_full 取行均值, _safe_mean 缺列优雅 NaN、per-model 独立降级。vw 的价值在于纠正「一篇带过 vs 一篇主角」的等权失真: 以目标银行为主角的显著报道更可能影响利益相关者认知, 显著性加权使集成语调向这类报道倾斜, 概念上呼应 Hassan 等 (2019) 的价值/提及加权与 Sautner 等的实体暴露加权思路。本列与 mw_full、hw_full 并排, 三套加权互证赋权维度敏感度; 与 vw_ctx、vw_ss 并排, 互证语境敏感度。作为加权稳健轨, 与家族三轨/分类维度/std/z 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。本列与 canonical 同轨仅差权重, 因此是三套加权中检验「以银行为主角的显著报道是否主导语调」的最主力 full 轨证据: 若 vw_full 相对等权 canonical 系统性偏移, 即说明语调结论对「谁被显著报道」敏感, 须以此校准对普通与显著报道的解读。全流程 $0 无网络、纯面板聚合、逐位可复现。

## VAR: llm_models_avg_tone_vw_ss

【变体差分】
本列是 value/salience 加权 (vw) × ss 轨的三家 LLM 均值-ensemble 语调。相对 canonical, 差分为显著性加权聚合叠加 ss 轨道。vw 权重取自 stage 11 news_salience 的报道显著性代理 (提及密度、版位、导语、署名), 逐篇聚合 Σ(w·tone)/Σw 给主角性强的报道更高权重。ss 轨文本 = 标题 + 银行∧金科同句±N 窗 (content_ss), 遵循镜像 ctx 的回退公理: 无同句共现时回退全文正文、ss_is_fallback 置 True、共享 n_articles 分母。因此本列度量「银行与金科被同句提及、且按报道显著性加权后」的集成语调, 是三套加权 × 三轨组合中语境紧且赋权重显著性的一条。计算为对三家 {model}_tone_vw_ss 取行均值 (_safe_mean 缺列优雅 NaN、per-model 独立降级)。本列与 vw_full、vw_ctx 并排互证 vw 加权下的语境敏感度, 与 mw_ss、hw_ss 并排互证同轨下不同赋权维度。作为 conditional-on-full 的 ss 稳健轨, 行宇宙为 full 子集、分子分母严格逐轨。与家族其余轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。早期试跑 T=2 面板上 ss 子样本极稀疏, 大量 NaN 或零方差属预期退化, 待生产 T=19 面板充分识别。本列把显著性加权与同句强共现两重条件叠加, 是 vw 加权三轨中样本最薄的一条: 它只对「银行与金科同句提及」的报道按显著性计权, 交汇了「说得多显著」与「多聚焦」两个稳健性问题, 提供三套加权 × 三轨组合中最保守的一个估计。

<!-- rendered-citations:begin -->
Ludwig, J., Mullainathan, S., & Rambachan, A. (2026). Large language models: An applied econometric framework. Annual Review of Economics. https://doi.org/10.1146/annurev-economics-120925-105620
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
Fatouros, G., Soldatos, J., Kouroumali, K., Makridis, G., & Kyriazis, D. (2023). Transforming sentiment analysis in the financial domain with ChatGPT. Machine Learning with Applications, 14, 100508. https://doi.org/10.1016/j.mlwa.2023.100508
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K. (2020). Econometrics meets sentiment: An overview of methodology and applications. Journal of Economic Surveys, 34(3), 512-547. https://doi.org/10.1111/joes.12370
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
MacKinnon, J. G., & Webb, M. D. (2017). Wild bootstrap inference for wildly different cluster sizes. Journal of Applied Econometrics, 32(2), 233-254. https://doi.org/10.1002/jae.2508
Wang, W., & Zhang, Y. (2024). Wild bootstrap inference for instrumental variables regressions with weak and few clusters. Journal of Econometrics, 241(1), 105727. https://doi.org/10.1016/j.jeconom.2024.105727
Chen, W., Liu, W., Zheng, J., & Zhang, X. (2025). Leveraging large language model as news sentiment predictor in stock markets: a knowledge-enhanced strategy. Discover Computing. https://doi.org/10.1007/s10791-025-09573-7
Stefanova, T., & Georgiev, S. (2025). Fuzzy Ensemble of Large Language Models for Financial Sentiment Analysis. Lecture Notes in Networks and Systems (Intelligent and Fuzzy Systems) [Working Paper]. https://doi.org/10.1007/978-3-031-97992-7_62
<!-- rendered-citations:end -->
