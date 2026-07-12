---
family_id: F121
columns:
- bian_2021_cater_b_ctx
- bian_2021_cater_b_full
- bian_2021_cater_b_ss
unit: 无量纲语调差值 (词典语调减 BERT 净语调; 理论域约 [-2, 2], 实测集中于 0 附近)
formula: "bian_2021_cater_b{track} = bian_2021_tone{track} - (bert_avg_pos{track} - bert_avg_neg{track}); track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/runner.py (步骤 8d, algo_cater 计算块); 标签在 news_process/pipeline/panel/export.py 与 news_process/pipeline/panel/stata_export.py
upstream:
- 22_tone_words.parquet (bian_2021_tone)
- 23_tone_berts.parquet (bert_avg_pos / bert_avg_neg)
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
new_dois: []
---

## CORE

【构念与来源】
本家族三列 bian_2021_cater_b_{full,ctx,ss} 度量的是同一篇 (聚合到银行-年后) 银行金融科技报道在两套完全异构的情感刻画之间的系统性落差: 一端是基于 Bian 等 (2021) 中文财经情感词典的逐词计数语调, 另一端是基于两家三分类中文金融 BERT (finbert_cn、fin_sent_zh) 聚合的深层净语调 (二分类 finbert2 因类空间不一致被排除在该聚合之外, 详见方法学与计算节)。差值取词典语调减去 BERT 净语调, 正值意味着词典读到的情绪比深层模型更为正面, 负值反之。之所以把这一落差单列为一个测度而非视作噪声, 是因为它承载一个可解释的构念: 当文本撰写方 (银行公关口径、财经记者、监管通稿) 有动机去 "取悦" 某一类下游读取器时, 会出现只对词法层面友好、却在语义/语境层面并不友好 (或相反) 的表达。这类因读取器而异的措辞调整, 学界称为算法迎合 (algorithmic catering), 其核心可观测量正是词典测度与机器学习测度之间的差值。词尾 _b 标识本族对齐的深层锚是 BERT 集成 (对照本仓另有对齐 LLM 集成的无 _b 姊妹族 bian_2021_cater), 两族测度互不替代: 一个捕捉词典对机器学习判别式模型的落差, 一个捕捉词典对生成式大模型的落差。

【方法学与计算】
计算在面板装配阶段 (runner.py 步骤 8d, algo_cater 计算块) 一次性展开, 属零额外 API 调用的纯后处理列。逐轨公式为 bian_2021_cater_b{track} 等于 bian_2021_tone{track} 减去 (bert_avg_pos{track} 减 bert_avg_neg{track})。其中 bian_2021_tone 来自 stage 22 词典语调 (Bian 词典正负词计数经否定翻转、程度副词、转折三条语言学规则调制后自归一化的极性分), bert_avg_pos 与 bert_avg_neg 来自 stage 23 中文金融 BERT 逐篇正负类概率的银行-年均值, 其差即 BERT 净语调, 理论域 [-1,1]。需要精确说明其成员组成: bert_avg_pos/neg 只在两家三分类中文金融 BERT (finbert_cn、fin_sent_zh) 上取均值, 二分类模型 finbert2 被刻意排除在这一聚合之外 (源码 geography.py 的 _BERT3 只纳入落在 THREE_CLASS_MODELS 中的模型)。排除的理由是类空间一致性: finbert2 仅输出正负两类、其正负概率恒和为一, 若把它并入 pos/neg 均值会把本应归入中性的概率质量重归一进正负两侧, 导致 bert_avg_pos 系统性上偏、且 bert_avg_pos/neu/neg 三者不再构成概率单纯形 (盘上实测三类和一度冲到 1.33), 故聚合域统一收敛到三分类族以使 pos+neu+neg≈1 的恒等式成立。finbert2 并非丢弃, 而是以其逐模型列 (finbert2_pos/neg 及各权重变体, 以及本仓 cater_finbert2 逐模型稳健轨) 单独保留为二分类稳健轨。两端分别落在约 [-1,1] 区间, 故差值理论域约 [-2,2], 但在真实语料上二者高度同向, 差值实测集中于 0 附近, 尾部才承载迎合信号。任一端在某银行-年缺列 (如 BERT 集成因模型缺席而无净语调、或该轨无词典命中) 时, 该轨差值置 NaN, 不做单边外推。三轨 full/ctx/ss 分别以三套文本载荷 (full 为标题拼正文全文; ctx 为标题拼实体窗口; ss 为标题拼银行与金科同句正负窗) 独立计算, 词典端与 BERT 端在每一轨内严格同轨相减, 不跨轨借用。ss 轨遵循镜像 ctx 的回退语义: 当某篇不存在银行与金融科技的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真, 与 ctx 共享分母口径。留篇门控为 full-only (2026-06-29 口径): 一篇报道是否计入银行金科报道全集只看 llm_verified_full 是否为真, ctx 与 ss 因而是 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 但每轨的差值列照各自轨的文本独立计算。

【文献定位】
本测度的方法学正当性首先落在词典法与机器学习法孰优孰劣、以及二者分歧本身是否携带信息这一议题上。Frankel 等 (2022) 在 Management Science 上系统比较了披露文本上的机器学习情感与词典情感, 论证两类方法在同一语料上给出的语调排序会系统性分歧, 且分歧并非纯噪声而与文本特征相关 —— 这正是把 "词典减深层模型" 显式物化为一个测度的直接依据。Bian 等 (2021) 构造的中文财经情感词典是本族词典端的命名来源, 其相对于英文 Loughran-McDonald 体系在中文会计金融文本上的域特异性优势, 与 Du 等 (2022) 在 Review of Finance 上关于中文财经情感词典语言与领域特异性的论证互为支撑, 共同说明选用本土词典而非直译词表的必要。van Atteveldt 等 (2021) 以人工标注为金标准同台比较词典法、众包与机器学习法, 揭示词典法与机器学习法各自的系统性偏差方向不同, 为本测度差值的符号解释提供了外部效度参照。Barbaglia 等 (2025) 与 Taboada 等 (2011) 则从经济文本与通用文本两侧夯实了基于词典的极性计算流程本身的规范性。需要强调, 本族三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified 的 Hansen J 过度识别检验; 同理 _b (对 BERT) 与无 _b (对 LLM) 两族、以及三家 BERT 各自的子测度, 亦是各自 just-identified 的并排稳健性轨, 不得混入同一过度识别式。

## VAR: bian_2021_cater_b_ctx

【变体差分】
本列是家族 ctx 轨变体, 文本载荷为实体窗口轨: content_ctx 在 stage 14 物化为标题 prepend 加实体上下文窗口 (围绕目标银行与金融科技实体的邻近句窗), 而非全文。差分口径为 bian_2021_cater_b_ctx 等于 bian_2021_tone_ctx 减去 (bert_avg_pos_ctx 减 bert_avg_neg_ctx), 词典端与 BERT 端均取 ctx 轨读数, 严格同轨相减, 绝不借用 full 轨或 ss 轨的任何一端。相对于 full 轨, ctx 轨把注意力收窄到银行与金科实体的语境邻域, 因而更能剔除通稿中与主体无关的背景性正负面措辞, 使得词典与 BERT 的分歧更纯粹地反映围绕主体的迎合性表达。在 full-only 留篇口径下, ctx 是 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集, 是否计为一篇银行金科报道仍由 llm_verified_full 决定, 本列仅在该子集上按 ctx 文本重算差值。ctx 轨与 full、ss 两轨互为稳健性、各自 just-identified 并排, 严禁三轨混入同一 over-identified Hansen J 过度识别检验。当 ctx 轨某银行-年词典端或 BERT 端任一缺列时该轨差值置 NaN, 不单边外推。需要额外区分的是, 本列的 BERT 端取的是两家三分类中文金融 BERT (finbert_cn、fin_sent_zh) 在 ctx 文本上正负类概率的聚合均值净语调 (二分类 finbert2 因会把中性质量重归一进正负两侧致 pos 上偏而被排除在该聚合之外, finbert2 仅在逐模型 cater_finbert2 稳健轨单独出现), 而非任一单模型读数, 因而本列度量的是词典对三分类判别式深层聚合的落差, 与对齐生成式 LLM 聚合的姊妹列 bian_2021_cater_ctx 度量不同的深层锚, 二者是并排稳健性轨而非替代关系。相较全文 full 轨, ctx 轨在实体窗口内往往剔除了大量与主体无关的宏观背景措辞, 使得词典与 BERT 分歧的绝对幅度通常收窄, 但也因此更集中于围绕银行金科主体本身的迎合性表达信号, 这是 ctx 轨作为语境收窄稳健性对照的方法学价值所在。

## VAR: bian_2021_cater_b_full

【变体差分】
本列是家族 full 轨变体, 也是三轨中承载留篇门控的基准轨。文本载荷为全文轨: content_full 在 stage 14 物化为标题 prepend 加正文全文。差分口径为 bian_2021_cater_b_full 等于 bian_2021_tone_full 减去 (bert_avg_pos_full 减 bert_avg_neg_full), 两端均取 full 轨读数同轨相减。full 轨的特殊地位在于 (2026-06-29 全仓口径): 一篇报道是否计入银行金科报道全集, 唯一由 llm_verified_full 是否为真判定, 因此 full 轨是留篇集的定义轨, ctx 与 ss 轨的行宇宙都是本轨留篇集的子集。就迎合构念而言, full 轨捕捉的是整篇报道层面词典语调与 BERT 净语调的落差, 相较 ctx/ss 更接近读者实际接触的完整文本, 因而是主叙事轨; ctx 与 ss 提供收窄语境后的稳健性对照。full、ctx、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 过度识别检验。本列与对齐 LLM 聚合的姊妹列 bian_2021_cater_full 度量不同的深层锚 (三分类 BERT 判别式 对 LLM 生成式), 二者亦为并排稳健性轨而非替代。任一端在某银行-年缺列时该轨差值置 NaN。就构念解读而言, full 轨差值取正意味着 Bian 词典在整篇文本上读到的情绪比两家三分类 BERT (finbert_cn、fin_sent_zh) 聚合的净语调更为正面 (二分类 finbert2 因类空间不一致不进入 bert_avg_pos/neg 聚合, 仅作逐模型稳健轨), 这一符号可对应词法层面友好而语义层面并不同等友好的措辞策略; 取负则反之。由于 full 轨承载留篇门控且贴近读者接触的完整文本, 本列通常作为迎合构念的主报告轨, 而 ctx 与 ss 轨给出语境逐级收窄后的稳健性对照, 三者符号一致性本身即可用于判断迎合信号是全篇性的还是仅集中于主体邻域。

## VAR: bian_2021_cater_b_ss

【变体差分】
本列是家族 ss 轨 (同句轨) 变体, 文本载荷最窄: content_ss 在 stage 14 物化为标题 prepend 加银行与金融科技同句共现的正负句窗 (半径由配置 ss_sentence_radius 控制, 默认 1)。差分口径为 bian_2021_cater_b_ss 等于 bian_2021_tone_ss 减去 (bert_avg_pos_ss 减 bert_avg_neg_ss), 两端均取 ss 轨读数同轨相减, 不借 full 或 ctx。ss 轨遵循镜像 ctx 的回退语义: 当某篇不存在银行与金科的同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置真, 并与 ctx 共享 n_articles 分母口径; 若 FINTECH_AC 为空导致无法判定, 则 ss_is_fallback 全真优雅降级。就迎合构念而言, ss 轨把词典与 BERT 的分歧压缩到银行与金科真正同句共现的最小语境, 因而对 "仅在主体紧邻处做措辞迎合" 这一细粒度模式最敏感, 是三轨中语境最严的稳健性轨。在 full-only 留篇口径下 ss 同为 conditional-on-full 轨, 行宇宙是 full 留篇集的子集。ss、ctx、full 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J 过度识别检验。任一端某银行-年缺列时该轨差值置 NaN, 不单边外推。与 ctx/full 两轨一致, 本列 BERT 端取两家三分类中文金融 BERT (finbert_cn、fin_sent_zh) 聚合的 ss 轨净语调 (二分类 finbert2 因会致 pos 系统上偏而被排除在 bert_avg_pos/neg 聚合外, 仅在逐模型 cater_finbert2 稳健轨单独出现), 词典端取 Bian 词典 ss 轨语调, 严格同轨相减, 度量的仍是词典对三分类判别式深层聚合的落差; 对齐 LLM 聚合的姊妹列 bian_2021_cater_ss 是并排稳健性轨而非替代。由于回退机制的存在, 在同句共现稀疏的银行-年上 ss 轨的有效非回退样本可能显著少于 full 轨, 这一样本依赖性是 ss 轨作为最严语境稳健性对照时须在结果叙事中披露的已知局限; 但正因其只在银行与金科真正同句处取信号, ss 轨对最贴近主体的细粒度迎合模式最为敏感, 与 full、ctx 两轨共同构成语境由宽到窄的三级稳健性梯子。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
