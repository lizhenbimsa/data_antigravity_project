---
family_id: F438
columns:
- mean_num_intensity_word_ctx
- mean_num_intensity_word_full
- mean_num_intensity_word_ss
unit: 数字 token 每词 (无量纲比率, digits per word; 分子分母口径不对称, 理论上可 > 1)
formula: "mean_num_intensity_word_{track} = Σ_i (w_i · num_intensity_word_i) / Σ_i w_i[valid]; num_intensity_word = n_numeric / max(n_words, 1); w_i = media_authority_weight × herd_weight{track}"
producer: pipeline/sentiment/numerical_intensity.py::compute_num_intensity_word (文章级) ; pipeline/panel/encode_collab.py::aggregate_num_intensity_panel (bank-year 加权聚合) ; pipeline/panel/export.py (Stata 标签)
upstream:
  - 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
  - 22_tone stage (num_intensity_word_{full,ctx,ss} 文章级列)
citations:
- doi: 10.1111/jbfa.70056
  type: journal
  authors: Taraj, I., & Wahlström, R. R.
  year: 2026
  title: "Narratives contextualizing numeric disclosures: Insights from earnings calls"
  venue: Journal of Business Finance & Accounting
  vol: 53
  issue: 3
  pages_or_artno: 1263-1286
- doi: 10.1111/1475-679X.70058
  type: journal
  authors: Levy, B.
  year: 2026
  title: "Caution ahead: Numerical reasoning and look-ahead bias in AI models"
  venue: Journal of Accounting Research
  vol: 64
  issue: 3
  pages_or_artno: 1139-1188
- doi: 10.1016/j.jcorpfin.2025.102813
  type: journal
  authors: Campbell, J. L., Zheng, X., & Zhou, D.
  year: 2025
  title: "Number of numbers: Does a greater proportion of quantitative textual disclosure reduce information risk?"
  venue: Journal of Corporate Finance
  vol: 94
  pages_or_artno: 102813
- doi: 10.1111/1467-8551.12853
  type: journal
  authors: Cai, W., Shi, W., & Jiang, F.
  year: 2025
  title: "Cheap talk? Strategy disclosure intensity, corporate risk-taking and financial performance"
  venue: British Journal of Management
  vol: 36
  issue: 1
  pages_or_artno: 361-382
- doi: 10.1287/mnsc.2024.05417
  type: journal
  authors: Siano, F.
  year: 2025
  title: "The news in earnings announcement disclosures: Capturing word context using LLM methods"
  venue: Management Science
  vol: 71
  issue: 11
  pages_or_artno: 9831-9855
- doi: 10.1057/s41599-025-06094-y
  type: journal
  authors: Lesmy, D., Muchnik, L., & Mugerman, Y.
  year: 2025
  title: "Lost in the fog: Growing complexity in financial reporting — A comparative study"
  venue: Humanities and Social Sciences Communications
  vol: 12
  pages_or_artno: 848
- doi: 10.1103/rxxz-lk3n
  type: journal
  authors: Rosillo-Rodes, P., San Miguel, M., & Sánchez, D.
  year: 2025
  title: "Entropy and type-token ratio in gigaword corpora"
  venue: Physical Review Research
  vol: 7
  issue: 3
  pages_or_artno: 033054
- doi: 10.48550/arXiv.2511.17866
  type: arxiv
  authors: Hartley, E.
  year: 2025
  title: "Narratives to numbers: Large language models and economic policy uncertainty"
  venue: arXiv
  pages_or_artno: 2511.17866
- doi: 10.48550/arXiv.2511.04935
  type: arxiv
  authors: Isler, C.
  year: 2025
  title: "Words matter: Forecasting economic downside risks with corporate textual data"
  venue: arXiv
  pages_or_artno: 2511.04935
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1177/0261927X09351676
  type: journal
  authors: Tausczik, Y. R., & Pennebaker, J. W.
  year: 2010
  title: "The psychological meaning of words: LIWC and computerized text analysis methods"
  venue: Journal of Language and Social Psychology
  vol: 29
  issue: 1
  pages_or_artno: 24-54
- doi: 10.1111/j.1540-6261.2008.01362.x
  type: journal
  authors: Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S.
  year: 2008
  title: "More than words: Quantifying language to measure firms' fundamentals"
  venue: The Journal of Finance
  vol: 63
  issue: 3
  pages_or_artno: 1437-1467
- doi: 10.3115/1119250.1119269
  type: journal
  authors: Sproat, R., & Emerson, T.
  year: 2003
  title: "The first international Chinese word segmentation bakeoff"
  venue: Proceedings of the Second SIGHAN Workshop on Chinese Language Processing
  pages_or_artno: 133-143
- doi: "10.1016/j.frl.2025.107917"
  title: "Decoding CSR report: How report readability and tone influence M&A target and acquirer likelihood"
  authors: "Li, Y."
  year: 2025
  venue: "Finance Research Letters"
  type: "journal"
- doi: "10.1057/s41599-024-04169-w"
  title: "Are risk disclosures in financial reports informative? A text mining-based perspective"
  authors: "Zhu, X., Li, J., & Wang, Y."
  year: 2024
  venue: "Humanities and Social Sciences Communications"
  type: "journal"
new_dois:
  - "10.1016/j.frl.2025.107917"
  - "10.1057/s41599-024-04169-w"
---

## CORE

【构念与来源】
本家族刻画银行-年面板上一家目标银行相关新闻报道的数值披露强度 (numerical intensity) 的词级口径, 即报道正文中阿拉伯数字 token 占词汇总量的相对密度。其构念动机来自会计与金融文本分析对定量披露 (quantitative disclosure) 的长期关注: 一篇报道中数字越密, 通常意味着传递的硬信息 (hard information) 越多、可核验的定量事实越丰富, 而非停留在定性的、模糊的叙事层面。构念锚定 Davis 与 Tama-Sweet (2012) 关于管理层在不同披露渠道 (盈余新闻稿 vs. 管理层讨论与分析) 中语言使用差异的研究, 其把数字密度视为披露"实" (substance) 与"虚" (rhetoric) 之别的一个可操作化代理; 需要郑重声明的是, 该文并未给出与本实现逐字一致的封闭公式, 因此本家族采用的 n_numeric / 篇幅 公式是项目自定义的操作化, 构念归属 Davis 与 Tama-Sweet (2012) 而公式归属本项目 — 生产源码 docstring 中曾误注的 Hales, Kuang 与 Venkataraman (2011) 数值强度公式一处已于 2026-06-05 引文勘误中撤销 (经核该文主题为生动/苍白语言对投资者判断的影响, 不定义数值强度)。近年一批研究进一步支撑了"数字密度"作为独立信息构念的价值: Campbell, Zheng 与 Zhou (2025) 直接以"数字的数量" (number of numbers) 度量定量文本披露占比, 并检验其是否降低信息风险; Taraj 与 Wahlström (2026) 考察盈余电话会议中数字披露的叙事语境; Hartley (2025) 与 Isler (2025) 则从大语言模型与下行风险预测的角度探讨文本中数字与叙事的相互作用。这些工作共同界定了本家族的构念坐标: 它测量的是"报道有多少定量事实密度", 而非语调正负、也非文本可读性或情绪强度。

本家族的三个成员 mean_num_intensity_word_full / _ctx / _ss 分别对应三条文本轨 (full = 标题 prepend + 全文正文; ctx = 标题 + 银行实体上下文窗口; ss = 标题 + 银行与金融科技词同句共现窗口), 是同一构念在三种文本取材范围下的并排测度。三轨互为稳健性、不分主次, 各自 just-identified 并排进入各自的识别式, 严禁把三轨列混进同一条 over-identified 的 Hansen J 过度识别检验 (此为 CLAUDE.md 三轨铁律)。ss 轨的回退语义严格镜像 ctx: 当某报道不存在银行与金融科技同句共现时, content_ss 优雅回退为全文 body 且 ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母口径; 当上游 FINTECH_AC 为 None 时 ss 相关列整体优雅降级为 NaN 而非静默填零。数据来源上, 文章级三轨文本在 stage 14 (ctx_materializer) 物化, 词级数字密度在数值强度阶段 (stage 22 族) 逐轨计算, 银行-年加权聚合在 stage 40 面板导出的 encode_collab 环节完成。

为什么要专门保留一个词级口径而非仅句级口径, 值得从构念效度角度展开。数值披露强度的核心诉求是"每单位篇幅承载多少定量事实", 而"单位篇幅"的选择直接决定测度对文本结构的敏感性。以句子为分母是英文披露文献 (如 Tetlock, Saar-Tsechansky 与 Macskassy 2008 对语言量化的传统) 的默认习惯, 因为英文句读边界清晰、句长分布相对稳定。但中文新闻的句读习惯与英文差异显著: 一个中文长句往往用逗号串联多个分句, 直到语义完整才落句号, 因而句号密度远低于英文, 句级分母会系统性偏低, 从而人为放大数字密度、并把测度对写作风格 (爱用长句还是短句) 的敏感性引入本应只反映内容的指标。词级口径以 jieba 分词得到的词数为分母, 分词粒度对长短句风格不敏感, 从而把"内容密度"与"句读风格"这两个混杂维度解耦。这正是本家族与句级家族并排存在的方法学理由 — 二者不是冗余, 而是对同一构念的两种归一化假设的显式对照。用大白话说: 句级版问"平均每句话里有几个数字", 词级版问"平均每一百个词里有几个数字"; 中文里前者容易被"爱写长句"的媒体拉高, 后者更公平。这一区分并非纯理论: 中国财经媒体行文风格差异极大 (党报偏长句政论体、都市报偏短句消息体、网媒偏碎片化), 若只用句级口径, 测得的"数字密度"会混入媒体行文风格这一与银行定量披露无关的混杂因素; 词级口径通过更细的归一化粒度削弱了这一混杂, 使跨媒体、跨年度的数字密度更具可比性。也正因此, 项目把句级与词级两条口径都物化并要求实证中并排报告, 而非以其中一条替代另一条。

【方法学与计算】
词级数字密度的计算分文章级与面板聚合两层。文章级函数 compute_num_intensity_word(content) 返回 n_numeric / max(n_words, 1): 分子 n_numeric 是文本经保守版中文数词转阿拉伯数字 (_cn2arab) 归一化后, 由数字 token 正则 (_DIGIT_TOKEN_RE, 含可选小数、百分号、万/亿单位字符) 匹配到的数字 token 数; 分母 n_words 是原文经 jieba 分词后剔除纯空白、纯标点、纯数字 token (复用 lm_non_sentiment 的 _LMFLS_NONWORD_RE 过滤正则, 与 clarity / pos_ratio / frac_uncert 的分母同口径) 后的词汇总数。空文本、单字符文本以及由 pandas astype(str) 产生的字符串化 NaN 哨兵 ("nan"/"None"/"<NA>"/"NaT" 等) 一律返回 NaN 而非 0.0, 以保证缺失沿聚合链正确传播、不系统性压低银行-年均值。分子分母口径刻意不对称 — 分子计入数字 token 而分母恰恰排除了纯数字 token — 因此对数字极密的文本, 该比值理论上可以大于 1, 它是 [0, +∞) ∪ NaN 的密度而非 [0, 1] 的比率, 这一点在论文与本 codebook 均须写明以免误读。

分子的中文数词归一化是本测度的关键工程环节。_cn2arab 把"两千万"→"20000000"、"三亿五千万"→"350000000"、"百分之三十"→"30%"等整体转为单一 token, 而对不定数 ("几千"/"数十亿"/"上百万") 保守地不计为 token。历史上 cn2arab 曾存在大规模误转 (单字"一"占分子约四分之一, 功能词与固定搭配如"进一步"/"之一"/"一带一路"、政治专名如"十九大"/"十三五"被误转为数字), 经 2026-06-11 omni 审计与一系列守卫修复 (序数"第N"守卫、单字块数量语境门控、党代会/规划名专名守卫、malformed 数词守卫、后缀不定数守卫) 后, 单字数字仅在具备量词/单位白名单或前置数量修饰的数量语境下计入。为吞吐考虑, 句级与词级两版共享一次 _cn2arab 转换 (_num_intensity_both), 逐位等价于分别调用, 保留两个独立公开函数供单测。

面板聚合在 encode_collab.aggregate_num_intensity_panel 完成, 采用与语调、清晰度聚合一致的媒体权威×羊群衰减加权口径。对每条报道 i、每条轨 track, 权重 w_i = media_authority_weight × herd_weight{track} (缺 herd 列时回退 herd_weight_full, 再缺则退化为 1.0)。银行-年加权均值 = Σ_i(w_i · num_intensity_word_i) / Σ_i w_i, 其中分母只累加该指标 valid-mask (即 num_intensity_word 非 NaN) 之后的权重, 使分子分母的样本域严格一致、不因缺失篇被稀释; 当有效权重和为 0 时分母被 replace(0, NaN) 置空以产出 NaN 而非除零。full/ctx 恒算, ss 词级列仅当上游 num_intensity_word_ss 就位时聚合 (旧 parquet 无 ss 时优雅跳过), 三轨各配自己的 herd 权重 (fix herd-ghost-01)。加权口径的选择本身也是一条稳健性轴: media_authority_weight 依据媒体来源的权威性 (党报/央媒/都市报/网媒等) 对报道赋权, herd_weight{track} 则对同一事件被多家媒体扎堆转载的羊群式重复报道做衰减, 避免少数被大量转载的事件在银行-年均值中占据不成比例的权重。valid-mask 加权的精细之处在于: 分母不是简单的报道计数, 而是"该指标非缺失篇的权重和", 因此当某银行-年下部分报道文本为空、cn2arab 后无有效词、或轨列缺失导致 num_intensity_word 为 NaN 时, 这些篇既不进分子也不进分母, 均值只由真正可算的报道决定, 从根本上杜绝了 NaN→0 的静默污染 (这一污染曾在 2026-05-27 的 R1-R5 审计中被识别并修复)。

关于确定性与可复现性须特别强调: 本家族全链不依赖任何 LLM 或嵌入 API, 仅依赖 jieba==0.42.1 冻结词典与纯 Python 的 cn2arab/正则计数, 因此在 golden 复现体系下是逐位可复现的确定性列 — 换嵌入模型、换 LLM 厂商对本家族零影响 (本家族与情感 LLM 三家投票、co-primary 双轨嵌入均无关)。这一确定性正是它在大语言模型时代作为定量披露基线测度的价值所在: 当 Siano (2025)、Levy (2026)、Hartley (2025) 等新方法用 LLM 捕捉词语语境或数值推理时, 一个透明、可审计、零随机性的数字密度基线能作为对照锚点, 检验更复杂方法是否真的带来增量。

从计算流程的端到端视角再复述一遍数据谱系, 有助于使用者定位每一步的口径来源。原始新闻语料经 stage 00 预处理、stage 11/12 银行与金融科技实体识别、stage 13 共现硬过滤 (只保留目标银行与至少一个金科词邻近共现的报道) 后, 在 stage 14 由 ctx_materializer 物化出 content_full / content_ctx / content_ss 三条真实文本列 (标题一律 prepend 到正文之前, 原始"内容"列不动); 数值强度阶段对三条文本列各独立调用 compute_num_intensity 与 compute_num_intensity_word (二者经 _num_intensity_both 共享一次 cn2arab 转换以省算力), 产出 num_intensity_word_{full,ctx,ss} 六列 (句级词级各三轨) 的文章级值; 最终在 stage 40 面板导出时由 encode_collab.aggregate_num_intensity_panel 把文章级词级值按媒体权威×羊群衰减权重聚合到 (target_bank, year) 粒度, 并在 export.py 打上 Stata 标签 "Num Intensity per-Word (Full/Ctx)"。整条链路无任何 LLM/嵌入调用, 是纯确定性文本计量。需要提醒的是, stage 13 的共现硬过滤已在样本框层面保证进入面板的报道都与目标银行及金融科技存在邻近共现, 因此本家族测得的数字密度是"金融科技相关的银行报道"这一特定语料上的密度, 而非银行全部报道的密度 — 这一样本框限定对解释系数至关重要: 它刻画的是当媒体在金融科技语境下谈论某银行时, 报道有多依赖定量事实。此外, 文章级中间列 (num_intensity_word_{full,ctx,ss}) 仅服务于面板聚合, 面板落盘的是银行-年粒度的加权均值列, 使用者在计量分析中直接消费的是后者。

【文献定位】
本家族坐落于计算文本分析中"定量披露密度"这一支。与语调/情绪测度族 (Tetlock, Saar-Tsechansky 与 Macskassy 2008; García, Hu 与 Rohrer 2023) 相比, 数值强度不判断文本的正负色彩, 而只计数其定量事实密度, 两者正交; 与词权重/内容分析法 (Jegadeesh 与 Wu 2013 的 word power) 相比, 本测度不做监督式词权重学习, 而是一个无监督的、可解释的密度比。与文本复杂度/可读性族 (Lesmy, Muchnik 与 Mugerman 2025; Rosillo-Rodes, San Miguel 与 Sánchez 2025 的 type-token ratio) 相比, 数字密度是内容维度而非语言难度维度, 尽管二者都以词级归一化为分母而在方法学上相邻。披露强度构念在近期公司金融研究中被独立检验 (Cai, Shi 与 Jiang 2025 关于策略披露强度与风险承担; Campbell, Zheng 与 Zhou 2025 关于数字比例与信息风险), 而大语言模型时代的文本-数字交互 (Siano 2025 对盈余披露词语语境的 LLM 捕捉; Levy 2026 对 AI 模型数值推理与前视偏差的警示; Hartley 2025) 进一步凸显了保留一个透明、确定性、可复现的数字密度基线测度的价值 — 本家族正是这样一个不依赖任何 LLM、逐位可复现的定量基线。进一步地, 数字密度与文本可读性/复杂度在方法学上相邻却在构念上正交: Lesmy, Muchnik 与 Mugerman (2025) 记录了财务报告复杂度的时序上升, Rosillo-Rodes, San Miguel 与 Sánchez (2025) 以 type-token ratio (亦是词级归一化) 刻画语料多样性, 二者都提醒我们词级分母的选择会影响测度的可比性 — 而本家族恰以词级归一化 (Sproat 与 Emerson 2003 所奠定的中文分词框架下的 jieba 词数) 为分母, 与这一支共享方法学地基但测量的是数字内容而非词汇多样性。在中文语境的特殊性上, Tausczik 与 Pennebaker (2010) 的 LIWC 传统提示词类计数 (功能词、数量词等) 的心理与信息含义, 而中文分词的歧义使得词级计数本身需要一个冻结、可复现的分词标准, 这正是项目钉死 jieba 版本的原因。该文用 BERT 深度学习方法度量企业社会责任报告的文本复杂度与语调, 检验其对并购目标/收购方可能性的影响, 与本家族共享"文本定量密度/复杂度作为披露实质性代理"的方法学地基, 引用格式作者 Li (2025, Finance Research Letters)。该文用文本挖掘方法检验金融报告风险披露的具体性与信息含量, 以次贷危机为真实风险事件验证披露语言从模糊到具体的变化, 与本家族"数字密度刻画硬信息含量"的构念动机相呼应, 引用格式作者 Zhu, Li 与 Wang (2024, Humanities and Social Sciences Communications)。

【识别策略定位】
在计量识别中, mean_num_intensity_word 主要充当文本"实质性/硬信息含量"的处理变量或稳健性协变量, 而非结果变量。它与句级版 mean_num_intensity (以句子数为分母) 构成对"归一化分母选择"的稳健性对: 中文新闻句号使用比英文 sparse (长句多逗号), 句级分母系统性偏低、放大数字密度; 词级版改以 jieba 词数为分母规避中英文句读差异。两种分母口径互为稳健性、不分主次, 纪律上不以二者相关系数高低取舍, 而是各自独立进入各自回归、各自 just-identified 并排, 严禁把句级列与词级列混进同一条 over-identified Hansen J。此外三轨 (full/ctx/ss) 亦是识别层面的规格稳健性并排轨, 同样禁混同一过度识别式。留篇门控与 n_articles 分母遵循 full-only 口径 (2026-06-29): 一篇报道是否计入某银行-年样本, 由 full 轨的 LLM verified 判定决定, ctx/ss 降为 conditional-on-full 的测度轨, 因此三轨面板列共享同一 full 留篇集为行宇宙, 各轨 per-track 分子分母照各自轨算。

【与相邻测度的构念区分】
须与三类相邻测度严格区分, 这一区分对避免在同一识别式中把高度共线的测度当作独立工具至关重要。其一, 与句级 mean_num_intensity 只差分母 (词数 vs 句数), 共享同一分子 n_numeric 与同一 _cn2arab 计数, 误差同源, 是分母口径稳健性对而非独立构念。其二, 与文章长度族 (avg_word_count / ln_word_count / avg_han_count) 区分: 后者是篇幅绝对量, 本测度是数字相对密度, 分母虽同为词级但语义不同。其三, 与稀有词比 (avg_rare_word)、硬字比 (avg_hard_char)、名词化比 (avg_nominalization)、功能词比 (avg_function_word) 等复杂度/风格族区分: 那些测度语言难度或修辞风格, 本测度只测定量内容密度。已知一处口径纪律: 因分母排除纯数字 token 而分子计数字 token, 数字极密文本比值可 > 1, 不可误当 [0,1] 比率解释。

【已知局限与稳健性梯子】
本测度存在若干已披露局限。其一, cn2arab 保守转换虽经多重守卫仍非零误转, 但误差同等影响句级/词级两版分子, 不构成词级版独有缺陷。其二, jieba 冻结词典 (jieba==0.42.1) 的分词粒度直接决定分母 n_words, 中文分词的固有歧义 (Sproat 与 Emerson 2003 所论的分词 bakeoff 难题) 会给分母带来系统性但确定性的口径, 换分词器即改口径, 故 jieba 版本作为冻结锚点不可轻动。其三, 不定数被保守剔除会低估某些定性数量表达的信息量。稳健性梯子由三条正交轴构成且各轴禁混同一 Hansen J: 分母口径轴 (句级 vs 词级) 已由本家族与 F 句级家族并排承担; 文本取材轴 (full/ctx/ss 三轨) 由本家族三成员并排承担; 加权口径轴 (媒体权威×羊群衰减 vs 等权) 由聚合层参数承担。三轴互为稳健性、不分主次、各自 just-identified 并排, 共同证明主结论不被任一单一操作化选择所驱动。其四, 开发期 T=2 小样本 (盘上约 220 行, 110 家银行×2 年) 下, 窗口较窄的 ctx/ss 轨词级列可能出现方差退化甚至逼近零方差, 属预期的样本规模退化而非代码缺陷, 生产期 T=19 全量语料 (2007–2025) 下恢复正常; 使用者在 dev 快照上不应据此退化下任何实质性结论。其五, 须再次强调 [0, +∞) 而非 [0,1] 的取值域: 由于分子计入数字 token 而词级分母恰恰排除了纯数字 token, 数字极密的短文本 (如纯数据披露) 的比值可以超过 1, 论文与稳健性表在描述统计与分布检查时须避免误将 > 1 的观测当作异常裁剪。综上, 本核心家族提供的是一个在中文金融新闻语境下经过工程加固 (cn2arab 多重守卫)、口径同构 (与 clarity/pos_ratio 共享词级分母过滤)、确定性可复现 (无 LLM/嵌入)、且在多条正交稳健性轴上并排布防的定量披露密度基线测度。

## VAR: mean_num_intensity_word_ctx

【变体差分】
本列为 ctx 轨的词级数字密度: 文本取材范围 = content_ctx (标题 prepend + 银行实体上下文窗口, 即以目标银行提及为中心的句子窗口, 剔除与银行无关的段落)。与 canonical 的 full 轨相比, ctx 轨只在银行被提及的邻近语境内计数数字 token 与词数, 因此测量的是"围绕该银行的报道语境里数字有多密", 而非整篇 (可能大段与该银行无关) 的数字密度。计算公式、分子分母口径 (n_numeric / max(n_words,1))、cn2arab 归一化、jieba 词级分母过滤、NaN 哨兵拦截、媒体权威×羊群衰减加权聚合均与 full 轨逐字一致, 唯一差别是输入文本轨。ctx 轨在识别上与 full/ss 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨列混进同一条 over-identified Hansen J 过度识别检验。留篇口径遵循 full-only (2026-06-29): 本列作为 conditional-on-full 的测度轨, 行宇宙 = full 轨 LLM verified 留篇集, 但 per-track 分子分母 (数字 token、jieba 词数、有效权重和) 一律按 ctx 轨自身文本重算, 不借 full 轨分母。ctx 与 ss 共享 n_articles 分母口径。因窗口截取, ctx 轨的词级分母通常远小于 full 轨, 在报道极短或银行仅一处提及时该列方差可能退化, 属预期而非缺陷。ctx 轨的实证价值在于剔除报道中与目标银行无关的段落所带来的稀释: 一篇同时谈及多家机构的综合报道, full 轨会把无关段落的数字一并计入, 而 ctx 轨只保留银行邻近语境, 从而更精确地反映"关于该银行的定量披露密度"。与 canonical full 轨相比, 本列是首要的规格稳健性并排臂, 检验主结论是否对"整篇 vs 银行语境"这一取材范围选择敏感。同样地, 本列也与句级 mean_num_intensity_ctx 构成分母口径 (词级 vs 句级) 的稳健性对, 二者互为稳健性、不分主次, 各自独立进入回归, 严禁混入同一 over-identified Hansen J。

## VAR: mean_num_intensity_word_full

【变体差分】
本列为家族 canonical 兼 core 列 (Table A9 真双轨 co-equal 第二臂, spec tA9 dual_track, 2026-07-10 签核扩围), 对应 full 轨: 文本取材 = content_full = 标题 prepend + 全文正文, 即在整篇报道 (含标题第 0 句) 上计数阿拉伯数字 token 与 jieba 词数。它是本家族三轨中取材最全、方差最稳、行覆盖最广的一条, 因而被选为核心列: 生产口径上留篇门控本身即由 full 轨的 LLM verified 判定驱动 (full-only 口径, 2026-06-29), full 轨天然与留篇集同域, 无 conditional-on-full 的子集收缩问题, 使其成为最适合作为主处理变量/主稳健性协变量的轨。作为词级口径, 本列与句级 canonical mean_num_intensity_full 构成"归一化分母选择"的双臂稳健性对: 二者共享同一分子 n_numeric (同一 _cn2arab + _DIGIT_TOKEN_RE 计数), 仅分母不同 (词数 vs 句数); 词级分母规避了中文新闻句号 sparse (长句多逗号) 导致句级分母系统性偏低、放大数字密度的问题, 对中文句读差异更稳健。二者互为稳健性、不分主次, 纪律上不以相关系数取舍, 各自独立进入回归、各自 just-identified 并排, 严禁把词级列与句级列混进同一条 over-identified Hansen J。作为 Table A9 双轨 co-equal 的第二臂, 本列与其对应的第一臂 (句级) 是并排的等价稳健性测度而非主从关系, 二者均须报告、任一不得被另一顶替。计算细节: 分子 n_numeric 经保守中文数词转阿拉伯数字后由数字 token 正则匹配, 不定数保守剔除, 政治专名/序数/功能词经守卫防误转; 分母 n_words 为 jieba 分词剔纯标点/纯数字/纯空白 token 后的词汇数; 空/单字符/字符串化 NaN 哨兵返回 NaN 沿链传播; 银行-年聚合为媒体权威×herd_weight_full 加权均值, 分母仅累加 valid-mask 后权重, 有效权重和为 0 时置 NaN。因分母排除纯数字 token 而分子计数字, 数字极密文本本列可 > 1, 属 [0, +∞) ∪ NaN 密度而非 [0,1] 比率。本列在三轨 (full/ctx/ss) 中与 ctx/ss 互为规格稳健性并排轨, 同样严禁三轨混入同一过度识别式; 构念上须与文章长度族 (绝对篇幅)、复杂度族 (语言难度)、语调族 (情绪正负) 严格区分 — 本列只测定量内容密度这一维。作为核心列, 本列在实证中最典型的角色是刻画围绕某银行的媒体报道整体上有多"实" (数字驱动的硬信息) 而非有多"虚" (定性叙事), 可作为处理变量进入信息含量、融资成本、投资等结果方程, 也可作为稳健性协变量控制报道的定量密度差异。相较 ctx/ss 两条窗口截取轨, full 轨取材最全, 银行-年下的有效篇数最多、加权分母最厚, 因而估计方差最小、跨年可比性最好, 这也是它被签核为 core 而非 ctx/ss 的实证理由。使用者须牢记两条纪律: 其一, 本列与句级 mean_num_intensity_full 是分母口径的双臂, 报告时二者并列而非择一; 其二, 本列大于 1 的观测并非异常值 (源于分子计数字 token 而分母排除纯数字 token 的口径不对称), 不应在数据清洗时被当作错误裁剪。其三, 本列作为不依赖 LLM 与嵌入的确定性列, 在 golden 复现体系下逐位可复现, 换情感 LLM 厂商或换嵌入模型对它零影响, 因而适合作为跨版本、跨方法对照时稳定不变的定量披露锚点。其四, 作为 core 列, 本列的 Stata 变量标签为 "Num Intensity per-Word (Full)", 在导出的最宽 dta 中与句级、ctx/ss 各轨并列存放, 供复现包按分母口径与文本轨两个维度做规格曲线式的稳健性展开。

## VAR: mean_num_intensity_word_ss

【变体差分】
本列为 ss 轨 (同句共现轨) 的词级数字密度: 文本取材 = content_ss = 标题 prepend + 银行实体与金融科技词同句共现窗口 (银行∧金科同句 ±N 句窗, N 由 config filtering.yaml context_window.ss_sentence_radius 控制, 默认 1)。与 ctx 轨相比, ss 轨的取材更严格 — 不仅要求银行被提及, 还要求银行与金融科技词在同一句 (或近邻窗口) 内共现, 因此测量的是"在银行与金科同句谈及的语境里数字有多密"。ss 轨严格平价 ctx (plan §④/§7.3-A1 仅情感/文本测度族得 _ss), 回退语义镜像 ctx: 当某报道无银行∧金科同句共现时, content_ss 优雅回退为全文 body 且 ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母口径; 当上游 FINTECH_AC 为 None 时 ss 相关列整体降级为 NaN 而非静默填零。计算公式、cn2arab 分子、jieba 词级分母、NaN 哨兵拦截、媒体权威×herd_weight_ss 加权聚合均与 full/ctx 逐字一致, 唯一差别是输入文本轨与 ss 专属 herd 权重。ss 词级列的聚合是条件性的: 仅当上游 num_intensity_word_ss 就位时才产出, 旧 parquet 无 ss 时优雅跳过 (has_word_ss 守卫)。ss 轨与 full/ctx 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨列混进同一条 over-identified Hansen J。留篇口径遵循 full-only: 本列为 conditional-on-full 测度轨, 行宇宙 = full 留篇集, per-track 分子分母按 ss 轨自身文本重算。因同句共现窗口最窄, ss 轨词级分母通常最小, 在开发期 T=2 小样本或回退篇占比高时该列方差可能退化 (甚至逼近全 NaN/零方差), 属预期退化, 生产期 T=19 全量语料下恢复正常。

<!-- rendered-citations:begin -->
Taraj, I., & Wahlström, R. R. (2026). Narratives contextualizing numeric disclosures: Insights from earnings calls. Journal of Business Finance & Accounting, 53(3), 1263-1286. https://doi.org/10.1111/jbfa.70056
Levy, B. (2026). Caution ahead: Numerical reasoning and look-ahead bias in AI models. Journal of Accounting Research, 64(3), 1139-1188. https://doi.org/10.1111/1475-679X.70058
Campbell, J. L., Zheng, X., & Zhou, D. (2025). Number of numbers: Does a greater proportion of quantitative textual disclosure reduce information risk? Journal of Corporate Finance, 94, 102813. https://doi.org/10.1016/j.jcorpfin.2025.102813
Cai, W., Shi, W., & Jiang, F. (2025). Cheap talk? Strategy disclosure intensity, corporate risk-taking and financial performance. British Journal of Management, 36(1), 361-382. https://doi.org/10.1111/1467-8551.12853
Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417
Lesmy, D., Muchnik, L., & Mugerman, Y. (2025). Lost in the fog: Growing complexity in financial reporting — A comparative study. Humanities and Social Sciences Communications, 12, 848. https://doi.org/10.1057/s41599-025-06094-y
Rosillo-Rodes, P., San Miguel, M., & Sánchez, D. (2025). Entropy and type-token ratio in gigaword corpora. Physical Review Research, 7(3), 13868. https://doi.org/10.1103/rxxz-lk3n
Hartley, E. (2025). Narratives to numbers: Large language models and economic policy uncertainty. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.17866
Isler, C. (2025). Words matter: Forecasting economic downside risks with corporate textual data. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.04935
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Tausczik, Y. R., & Pennebaker, J. W. (2010). The psychological meaning of words: LIWC and computerized text analysis methods. Journal of Language and Social Psychology, 29(1), 24-54. https://doi.org/10.1177/0261927X09351676
Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More than words: Quantifying language to measure firms' fundamentals. The Journal of Finance, 63(3), 1437-1467. https://doi.org/10.1111/j.1540-6261.2008.01362.x
Sproat, R., & Emerson, T. (2003). The first international Chinese word segmentation bakeoff. Proceedings of the Second SIGHAN Workshop on Chinese Language Processing, 133-143. https://doi.org/10.3115/1119250.1119269
Li, Y. (2025). Decoding CSR report: How report readability and tone influence M&A target and acquirer likelihood. Finance Research Letters. https://doi.org/10.1016/j.frl.2025.107917
Zhu, X., Li, J., & Wang, Y. (2024). Are risk disclosures in financial reports informative? A text mining-based perspective. Humanities and Social Sciences Communications. https://doi.org/10.1057/s41599-024-04169-w
<!-- rendered-citations:end -->
