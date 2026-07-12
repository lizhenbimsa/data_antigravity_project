---
family_id: F139
columns:
- cater_deepseekv4_ctx
- cater_deepseekv4_full
- cater_deepseekv4_ss
unit: 情感差值 (无量纲; 综合词典 tone 与 deepseekv4 LLM tone 均归一化到 [-1,1] 同尺度后的算术差)
formula: "cater_deepseekv4{track} = dict_avg_tone{track} - deepseekv4_tone{track}; track ∈ {_full,_ctx,_ss}"
producer: news_process/pipeline/panel/runner.py (step 8d 算法迎合度) ; news_process/pipeline/panel/export.py (标签)
upstream:
- 21_tone_llms.parquet (deepseekv4_tone{track})
- 22_tone_words.parquet (dict_avg_tone{track})
- 24_herd_decay.parquet (df_exploded, aggregate_panel 聚合到 bank-year)
citations:
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
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
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是同一批银行金融科技报道在两种情感抽取范式下的系统性偏离, 即所谓算法迎合度 (algorithmic catering) 的一个具体切面。分子端的 dict_avg_tone 是六部中文金融情感词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran) 的平均语调, 属于透明、可复算、规则驱动的浅层测度; 减项端的 deepseekv4_tone 则是第三家大语言模型 deepseek-v4-flash (直连 api.deepseek.com, 与走云雾中转的 gpt54nano、gemini31 两家异源) 对同一文本三分类投票折算出的语调分。两者相减得到 cater_deepseekv4, 正值意味着词典读出的情感比深层语言模型更正面, 负值则相反。这一差被解读为一种潜在的信息操纵或表达策略信号: 当一家银行有动机让基于词表的自动化舆情系统读到更漂亮的语调时, 它可能在措辞上堆砌词典命中的正面词, 而这种表层修饰未必能骗过理解上下文、否定与转折的语言模型, 于是词典分与模型分之间出现可观测的楔子。构念的理论根基来自 Cao 等 (2023) 关于"当机器在听时如何说话"的发现: 企业在意识到机器读者 (量化投资者、算法舆情) 存在后, 会系统性调整披露措辞以迎合机器可读性, 而这种迎合在浅层与深层文本模型之间留下可度量的落差。

【方法学与计算】
计算发生在面板总装阶段 (runner.py 步骤 8d, 算法迎合度全展开块), 属零额外调用的纯后处理: 上游 stage 21 已产出 deepseekv4 逐篇三分类结果并在 aggregate_panel 聚合为 bank-year 的 deepseekv4_tone, stage 22 已产出六词典语调并聚合为 dict_avg_tone, 本家族只做逐轨逐行的减法 cater_deepseekv4{track} = dict_avg_tone{track} − deepseekv4_tone{track}。两个被减量都事先归一化到 [-1,1] 的可比尺度, 因此差值本身无量纲, 理论取值区间为 [-2,2], 但实际分布集中在零附近。本家族属"综合词典 vs 单深层模型"的 C 型迎合度, 与"综合词典 vs 综合 LLM 投票"的 algo_cater、"单词典 vs 综合模型"的 {dict}_cater、"综合词典 vs 单 BERT"的 cater_{bert} 并列, 它们各自锁定迎合信号的一个正交切面。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否计入银行金融科技样本、进而进入任何轨的分母, 只由 full 轨的 LLM 验证结果决定; ctx 与 ss 轨是 conditional-on-full 的稳健性测度, 其行宇宙是 full 留篇集的子集。零覆盖的 bank-year (无有效报道) 在同族缺失语义下应输出 NaN 而非伪零, 避免把"没数据"误当成"词典与模型完全一致"。

【文献定位】
方法学谱系上, 本家族站在词典法与机器学习法长期并存、互为参照的传统之上。Loughran 和 McDonald (2011) 奠定了金融文本词典法的规范, 指出通用情感词表在金融语境下的系统性偏误, 催生了领域专用词典; 而 Frankel、Jennings 和 Lee (2022) 在顶刊上直接比较机器学习与词典方法抽取披露情感的差异, 论证两类范式各有系统性倾向、不可相互替代, 为"以两者之差作为独立信号"提供了直接依据。深层测度一侧, Huang、Wang 和 Yang (2023) 的 FinBERT 与本项目 deepseekv4 同属能建模上下文、否定与语义的深层语言模型, 其抽取的情感与词典命中在机制上不同源。de Kok (2025) 进一步系统评估了生成式大语言模型用于会计文本分析的可靠性与偏误边界, 提示 LLM 端读数并非无噪声的真值, 因此 cater 差应被理解为两条各有测量误差的测度之间的相对楔子, 而非"模型对、词典错"的校正量。四家/两范式各自 just-identified 并排、互为稳健性、不分主次, 严禁把词典分与不同 LLM 或 BERT 的模型分混进同一 over-identified Hansen J 工具集。

## VAR: cater_deepseekv4_full

【变体差分】
本列为 full 轨变体, 是本家族的门控基准轨。full 文本 = 标题 prepend 后拼接全文正文 (content_full), 覆盖整篇报道的完整语义面, 因此它同时是留篇门控的唯一判定轨: 一篇报道是否算作银行金融科技样本、进而其 dict_avg_tone_full 与 deepseekv4_tone_full 是否进入 bank-year 聚合, 完全由 full 轨的 llm_verified_full 决定 (full-only 口径, 2026-06-29)。数值上, cater_deepseekv4_full = dict_avg_tone_full − deepseekv4_tone_full, 即六词典平均语调 (在全文范围内命中并归一化) 减去 deepseek-v4-flash 对全文三分类投票折算的语调。与同族 cater_gpt54nano_full、cater_gemini31_full 相比, 本列只换减项模型为第三家 deepseekv4 (直连 api.deepseek.com, 异源于云雾中转的另两家), 词典分子端完全一致; 三家 per-model 迎合度各自 just-identified 并排、互为稳健性、不分主次, 严禁三家模型分同进一个 over-identified Hansen J。与本家族 ctx/ss 两轨相比, 差异仅在文本窗口: full 用整篇, 信息最全但也最易被与银行金融科技无关的段落稀释。per-model 独立降级: 若 deepseekv4 该轨缺席, 仅本列族置 NaN, 不牵连 gpt54nano/gemini31 或 BERT 迎合度列, 这与 co-primary 双轨嵌入的 both-or-neither 语义截然不同。因 full 是门控轨, 三轨中通常唯本列在生产语料上有最完整的非缺失覆盖。正值方向的解读须谨慎: full 轨读的是整篇报道, 词典命中的正面词可能来自与银行无关的宏观背景段落, 使 dict_avg_tone_full 偏高, 从而抬升本列的迎合读数; 而 deepseekv4 因能建模上下文与否定, 对同段的语调判定往往更保守。因此本列的正值既可能反映真实的表达迎合, 也可能夹带全文范围内无关正面语料的噪声, 论文使用时应把 ctx/ss 两条更窄窗口轨作为并列稳健性对照, 三者读数一致时迎合信号才稳固。

## VAR: cater_deepseekv4_ctx

【变体差分】
本列为 ctx 轨变体。ctx 文本 = 标题 prepend 后拼接实体上下文窗口 (content_ctx), 即只保留围绕目标银行实体提及的邻近窗口, 而非整篇正文, 意在剥离与该银行无关的段落噪声, 让情感读数更聚焦于报道对这家银行的具体表述。数值上 cater_deepseekv4_ctx = dict_avg_tone_ctx − deepseekv4_tone_ctx, 分子与减项均在同一 ctx 窗口文本上计算, 严格逐轨对齐, 绝不借用 full 轨的分子或分母。本列相对 full 轨的唯一差分是文本窗口收窄, 相对 ss 轨的差分是窗口口径更宽 (实体窗口 vs 银行金融科技同句窗); 相对同族其它模型列 (cater_gpt54nano_ctx、cater_gemini31_ctx) 的唯一差分仍是减项模型换为 deepseekv4。ctx 轨在 full-only 门控下是 conditional-on-full 的稳健性测度: 其行宇宙是 full 留篇集的子集, 只对已被 full 轨判为银行金融科技样本的 bank-year 逐轨另算 ctx 读数。三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨读数混进同一 over-identified Hansen J。per-model 独立降级同 full 轨: deepseekv4 该轨缺席只置本列 NaN。在 T=2 开发盘上, ctx 窗口在极短面板上可能出现零方差或大量退化, 属预期现象, 生产 T=18 语料上恢复正常判别力。相对 full 轨, ctx 轨把无关段落剥离后, 词典分子端不再被报道中与银行无涉的正面宏观语料抬高, 因此本列与其 full 孪生的差异恰恰承载了"迎合信号是否稳健于窗口收窄"的稳健性信息: 若 full 轨读出的正向迎合在 ctx 轨消失, 提示该迎合更可能来自全文噪声而非针对该银行的表达策略。deepseekv4 作为第三家异源模型 (直连 api.deepseek.com), 与云雾中转的 gpt54nano、gemini31 在提示、温度与缓存键上共享同一构造口径, 保证 per-model 迎合度的跨厂商可比性; 本列的减项换成 deepseekv4 后, 与 cater_gpt54nano_ctx、cater_gemini31_ctx 构成同一 ctx 轨上的三家厂商稳健梯子。

## VAR: cater_deepseekv4_ss

【变体差分】
本列为 ss 轨变体, 三轨中窗口最窄。ss 文本 = 标题 prepend 后拼接"银行与金融科技同句共现"窗口 (content_ss), 即只保留目标银行名与金融科技词在同一句子 (±N 句半径, config filtering.yaml 的 ss_sentence_radius 默认 1) 内同现的片段, 口径最严, 意在把情感读数锁定在真正把这家银行与金融科技绑在一起谈论的语句上。数值上 cater_deepseekv4_ss = dict_avg_tone_ss − deepseekv4_tone_ss, 分子与减项均在同一 ss 窗口文本上严格逐轨计算。ss 轨的关键差分在其回退语义 (镜像 ctx): 当某报道不存在银行与金融科技的同句共现时, content_ss 回退为全文正文 body, 并置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母; 若 FINTECH_AC 词表为空则 ss_is_fallback 全 True 优雅降级。因此本列在无同句共现的报道上实际读的是全文语调差, 应结合 fallback 标记解读, 不可当成纯同句测度。相对同族 cater_gpt54nano_ss、cater_gemini31_ss 的唯一差分仍是减项模型换为第三家 deepseekv4。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; per-model 独立降级只影响本列族。在 T=2 开发盘上 ss 轨常因同句共现稀少而大量走回退或呈零方差退化, 属预期, 生产 T=18 语料上具判别力。ss 轨是三轨中最能定位"银行与金融科技共同被谈论时的表达迎合"的口径: 当报道确有同句共现且非回退时, 本列捕捉的是词典与 deepseekv4 在这一最相关语句集上的语调楔子, 理论上信噪比最高; 但因回退机制的存在, 实际非缺失值里混有相当比例的全文回退读数, 使用者须联合 ss_is_fallback 标记做子样本切分, 单独考察真同句共现子集与回退子集, 才能把纯同句迎合信号与全文迎合信号分离。就与相邻测度的区分而言, 本列与同句口径的 algo_cater_ss (综合词典 vs 综合 LLM 投票) 的差别在减项: 后者用三家投票共识, 本列只用 deepseekv4 单模型, 因此本列额外承载单一厂商模型特异性的信息, 二者不可相互替代。

<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
