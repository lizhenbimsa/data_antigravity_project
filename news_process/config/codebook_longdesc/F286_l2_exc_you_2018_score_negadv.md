---
family_id: F286
columns:
- exc_you_2018_score_negadv_ctx
- exc_you_2018_score_negadv_full
- exc_you_2018_score_negadv_ss
unit: 情感倾向分值 (无量纲, Σ|base| 幅度归一化, 值域约束于 [-1, 1])
formula: "exc_you_2018_score_negadv_{track} = mean_{i ∈ (bank,year), _is_ceased_media_i = 0} you_2018_score_negadv_{track},i; 其中文章级 you_2018_score_negadv = Σ signed_final / Σ|base|, 以 you_2018 词典逐 token 计分, 规则组合 = 否定翻转 ON + 程度副词 OFF + 转折增益 ON (= 全规则 − degree)"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (文章级源列 news_process/pipeline/sentiment/tone_words.py::_analyze_single_article, 经 _RULE_ABLATION_VARIANTS 消融循环调用 _compute_sentiment_with_rules)
upstream:
- 22_tone_words.parquet (you_2018_score_negadv_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_yearly.parquet (target_bank × year 骨架 + _is_ceased_media 标记)
citations:
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
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: "10.1111/ecin.13264"
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  authors: "Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E."
  year: 2024
  venue: "Economic Inquiry"
  type: "journal"
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
- doi: "10.1177/10944281251334777"
  type: "journal"
  authors: "Iqbal, F., & Pfarrer, M. D."
  year: 2025
  title: "Using Coreference Resolution to Mitigate Measurement Error in Text Analysis"
  venue: "Organizational Research Methods"
  pages_or_artno: "10944281251334777"
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
new_dois:
  - "10.1111/ecin.13264"
---

## CORE

【构念与来源】
本家族度量的是"剔除疑似退出覆盖媒体后、以 you_2018 词典否定加转折规则计得的银行年度报道语调"。它由两条彼此独立的构念叠合而成: 其一是情感词典测度本身 —— 以命名与词表溯源自 You, Zhang & Zhang (2018) 的中文金融情感词表 (项目内代号 you_2018) 对每篇银行金融科技报道逐 token 计分, 得到文章级极性分值; 其二是样本稳健性口径 —— 在把该文章级分值聚合到银行年度面板时, 只纳入"存活媒体"发布的报道, 把疑似退出本地话题覆盖的媒体来源保守剔出, 列名前缀 exc_ 即 exclude ceased media 之意。两者相乘, 使本列既保留 you_2018 词典法的语言学计分口径, 又对媒体退出所引入的幸存者偏差 (survivorship bias) 做敏感性检验。You, Zhang & Zhang (2018) 在 Review of Financial Studies 上实证了"谁掌握了媒体之笔"这一媒体俘获问题, 揭示媒体报道的情感倾向并非中性中介, 而是可被利益方左右的信号; 本项目以其研究脉络为命名锚, 取用对应的中文金融极性词表构造词典测度, 使语调不再只是词频统计, 而承载媒体信号可被塑造这一制度背景。这一构念区分极为重要: 语调测度捕捉的是报道的极性方向与强度, 而非报道是否被操纵; 后者须借助媒体退出、来源异质性等外生变异识别, 本家族的 exc_ 聚合口径正是朝这一方向的一次稳健性探针。

【方法学与计算】
文章级源列 you_2018_score_negadv 由 tone_words.py 的 _analyze_single_article 产出: 该函数对每篇报道分词后, 在 _RULE_ABLATION_VARIANTS 消融变体谱上逐一调用计分内核 _compute_sentiment_with_rules, 以后缀 negadv 对应的规则开关组合物化本列。计分内核对分词后的 token 序列扫描 you_2018 词表, 命中词取其基础极性 base, 再按三条可开关的语言学规则修饰: 否定翻转 (否定词在同句窗口内出现则翻转其后情感词极性)、程度副词 (程度词按六级权重缩放情感强度, 最高约三倍)、转折增益 (转折连词后的分句情感权重上调 ADVERSATIVE_BOOST 倍, 体现"末尾效应"下作者真实立场)。三条规则的作用域均限定为从句级, 遇句末标点即重置转折、否定、程度状态, 学术依据为 Ding, Liu & Yu (2008) 的从句级转折作用域。本家族对应的规则组合后缀为 negadv, 即否定翻转 ON、程度副词 OFF、转折增益 ON —— 等价于在全规则基线上单独关掉程度副词一维 (full 减 degree)。最终分值以幅度口径归一化, 即 signed_final 之和除以 base 绝对值之和, 分子分母同含转折权重, 故恒约束于 [-1, 1] 的无量纲极性。聚合环节在 attention_media.py 的 compute_media_heterogeneity 中: 先依据媒体在语料中的覆盖跨度识别疑似退出媒体集, 逐篇打上 _is_ceased_media 标记; 随后对 _is_ceased_media 等于 0 的存活报道, 按 target_bank 与 year 分组取文章级分值的算术平均, 落成本列。分组为空 (该银行年度无存活媒体报道) 时本列按情感类契约保持 NaN, 绝不零填。留篇门控沿用 full-only 口径 (2026-06-29): 一篇报道是否计入银行金融科技样本仅由 full 轨 LLM 判定, ctx 与 ss 轨为 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, per-track 分值照各轨文本独立计算。

【文献定位】
情感词典法在金融文本分析中源远流长, 中文场景尤须领域专用词表。You, Zhang & Zhang (2018) 是本家族情感构念的命名与词表来源, 也是本家族的顶刊锚: 其对媒体报道情感可被利益方俘获的实证, 为"语调即制度化信号"提供了理论根基。Du et al. (2022) 在 Review of Finance 上系统论证语言与领域专用性对中文金融情感测度的重要性, 并交付了同项目并行的 du_2022 词典, 印证领域专用词表相对通用词表的增益, 亦是本项目多词典互为稳健性设计的直接依据。方法学对照方面, Frankel, Jennings & Lee (2022) 在 Management Science 上比较机器学习与词典法在披露情感测度上的表现, 是本项目以词典法、BERT、LLM 三法互为稳健性的先例, 提醒词典法虽透明可审但须与学习法交叉验证。语言学规则一侧, Taboada et al. (2011) 系统梳理了词典法中否定、程度副词与转折等 valence-shifter 的处理方式, 正是本家族规则消融梯度 (含 negadv 这一去程度、保否定与转折的组合) 的方法学出处。Barbaglia, Consoli, Manzan, Tiozzo Pezzoli & Tosetti (2024, Economic Inquiry) 提出面向经济文本的词典法情感测度框架, 处理否定与修饰词对经济概念极性的作用, 与本家族否定翻转加转折规则消融口径直接相关。本家族三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨或多套规则消融变体混进同一 over-identified 的 Hansen J 检验; 规则消融梯度各变体高度共线 (与全规则版相关系数近 0.99), 仅作定性不变的稳健性对照, 不主张某一规则组合更优, 也不可将 full 与 negadv 之差解读为程度副词规则的纯因果贡献 (audit MATH-1: 非可加分解)。 近期方法学证据可为本家族的两个具体环节再作补强。Naldi 与 Petroni (2023) 以人工构造测试集专门评估词典法情感工具的否定检测与处理能力, 实证发现各工具在该环节表现差异显著; 这一证据落在 negadv 档位保留否定翻转的一侧, 说明否定并非可默认信赖的既成处理, 而是词典法内部可被单独测量、单独失效的模块, 因而其开/关须成为独立报告的一臂。迁移边界在于, 原文为英文通用领域的工具评测、以否定检测准确率为度量, 本项目不评测任何一臂的否定检测准确率, 而是把该规则的开/关作为中文金融新闻语调面板测度的并排稳健性臂; 其发表于 2023 年, 非 2024 年后前沿。Iqbal 与 Pfarrer (2025) 在 Organizational Research Methods 上以共指消解为例, 经两项研究证明一项具体的语言学处理选择会系统性改变文本测度取值并构成实质性测量误差来源, 支持本家族显式呈现规则后果而不默认采纳的立场; 惟原文规则是实体指代还原 (在本项目对应 ctx/ss 实体窗口轨而非本族), 与否定/程度/转折三规则非同一项, 且其取规范性取向、主张采纳该规则以减少误差, 与本项目七臂互为稳健性并排、不设主次的取向不同, 故不得据以视为 powerset 规则消融设计的同构先例。就 exc_ 前缀的样本裁剪而言, Cziraki 与 Gider (2024) 以报纸停刊为冲击, 实证报道供给退出会改变本地股票交易行为, 为「剔除 _is_ceased_media 判定为 1 的媒体后再作银行-年度聚合」提供现实动机: 媒体退出是真实且具经济后果的样本组成变化。其停刊判定取自外部事件数据并用作识别冲击, 而本项目 ceased_set 由 detect_defacto_cessation 自语料内部推断 (confirmed ∪ suspected), 系保守代理而非严格停刊事实, 用途仅限稳健性子样本; 该文为工作论文, 尚未经同行评审。
## VAR: exc_you_2018_score_negadv_ctx

【变体差分】
本列取实体上下文轨 (ctx)。文本口径为标题 prepend 后的银行实体窗文本 (content_ctx) —— 即在物化阶段 14 由 ctx_materializer 抽取焦点银行提及周边窗口、并前置标题所得的截断文本, 而非整篇正文。相较 full 轨, ctx 轨把计分素材收缩到与目标银行直接邻近的语句, 意在剥离与该银行无关段落的噪声, 检验语调测度对"实体近场文本"是否稳健。规则组合与家族一致 (否定翻转 ON、程度副词 OFF、转折增益 ON, 即 negadv), 词典为 you_2018, 归一化为 Σ signed_final / Σ|base|; 聚合仍只纳入 _is_ceased_media 等于 0 的存活媒体报道, 按 target_bank 与 year 取均值, 空组保持 NaN。轨道定位上, ctx 为 conditional-on-full 轨: 其行宇宙是 full 轨留篇集的子集, 是否计入银行金融科技样本由 full 轨门控裁定, ctx 只在被留篇的报道上按 content_ctx 独立计分。本 ctx 轨与同家族的 full、ss 轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified 的 Hansen J 检验; 它与规则消融其余六变体、政治词权重梯度彼此正交, 不得交叉组合以免列数爆炸。实证解读上, ctx 轨相对 full 轨的系统性差异, 反映"实体近场语调"与"全篇语调"的口径落差: 若一篇报道整体基调偏正但银行邻近语句偏负, ctx 轨会更贴近后者。剔除疑似退出媒体这一样本口径亦逐轨独立施加, ctx 轨的存活媒体子集与 full 轨同源于 _is_ceased_media 标记, 但各轨在被留篇报道上按各自文本独立计分, 分母互不借用。

## VAR: exc_you_2018_score_negadv_full

【变体差分】
本列取全文轨 (full), 是三轨中的门控基准轨。文本口径为标题 prepend 后的整篇正文 (content_full), 即在原始报道正文前置标题所得的完整文本, 计分素材覆盖全篇而非实体窗或同句窗。full 轨承担留篇门控职责 (2026-06-29 full-only 口径): 一篇报道是否被判定为"银行金融科技报道"并计入样本, 仅由 full 轨的 LLM 判定决定; ctx 与 ss 两轨的行宇宙均是 full 留篇集的子集。规则组合为 negadv (否定翻转 ON、程度副词 OFF、转折增益 ON, 等价于全规则减去程度副词一维), 词典为 you_2018, 分值以 Σ signed_final / Σ|base| 归一化至 [-1, 1]; 聚合时只对 _is_ceased_media 等于 0 的存活媒体报道按 target_bank 与 year 取算术平均, 空组保持 NaN 不零填。相较 ctx 收窄到实体近场、ss 收窄到银行金科同句共现, full 轨保留最完整的语义上下文, 是语调测度的信息量上界参照。本 full 轨与 ctx、ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified 的 Hansen J; 与政治词权重三臂、规则消融其余变体正交不交叉。实证意义上, full 轨承担双重角色: 既是留篇门控的唯一裁定轨, 又是语调测度信息量的上界参照; 当 ctx、ss 因文本收窄而在早期试跑期短面板上出现零方差退化时, full 轨仍能提供稳定的基准分值。本列与不剔除媒体的常规聚合列之差, 恰好隔离出媒体退出对银行年度语调的净影响, 是"幸存者偏差是否驱动主结论"这一诘问的直接答复列。

## VAR: exc_you_2018_score_negadv_ss

【变体差分】
本列取同句共现轨 (ss), 是三轨中口径最严的一轨。文本口径为标题 prepend 后、银行与金融科技词在同一句子 (可含前后 N 句窗, 默认半径 1) 共现的语句拼接 (content_ss)。回退语义镜像 ctx: 当某报道不存在银行与金融科技的同句共现时, content_ss 优雅回退为整篇正文, 并置 ss_is_fallback 为真, 与 ctx 轨的回退契约同构; 当金融科技 AC 自动机为空时该轨 fallback 全部为真, 整体优雅降级。规则组合与家族一致 (否定翻转 ON、程度副词 OFF、转折增益 ON, 即 negadv), 词典 you_2018, 归一化 Σ signed_final / Σ|base|; 聚合只纳入 _is_ceased_media 等于 0 的存活媒体报道, 按 target_bank 与 year 取均值, 空组保持 NaN。轨道定位上 ss 同为 conditional-on-full 轨, 行宇宙是 full 留篇集子集, 留篇裁定权归 full 轨, ss 只在留篇报道上按 content_ss 独立计分。本 ss 轨与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified 的 Hansen J 检验; 与政治词权重梯度及规则消融其余变体正交不交叉。实证解读上, ss 轨把计分素材压缩到银行与金融科技真正同句共现的语境, 因而最贴近"银行金融科技关联叙事"这一核心构念, 但也最易受回退稀释: 在同句共现稀疏的语料或短面板上, 大量报道走整篇正文回退, 使 ss 轨向 full 轨收敛。故本列在稳健性梯子中定位为口径最严的一端, 与 full 的最宽端、ctx 的中间端构成语义粒度的三点谱。剔除疑似退出媒体的样本口径逐轨独立施加, ss 轨的存活媒体子集与其余两轨同源于 _is_ceased_media 标记, 分母不跨轨借用, 空组一律保持 NaN 而非零填, 以免把"无存活报道"误读为"零语调"。

<!-- rendered-citations:begin -->
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2024). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry. https://doi.org/10.1111/ecin.13264
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
