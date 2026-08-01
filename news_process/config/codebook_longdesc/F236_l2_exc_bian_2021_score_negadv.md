---
family_id: F236
novelty_exempt_rationale: "exc_ 停刊剔除 × negadv 规则消融的双重稳健性变体家族, 测度定义依据母族 bian_2021 词典及其规则消融/停刊代理设计, 非独立新构念, 不需要独立追新文献。"
columns:
- exc_bian_2021_score_negadv_ctx
- exc_bian_2021_score_negadv_full
- exc_bian_2021_score_negadv_ss
unit: 情感倾向分值 (无量纲, self-normalized 至 [-1, +1])
formula: "文章级 bian_2021_score_negadv = Σ(final)/Σ|final| (final = base × negation × adversative, 停用 degree 副词缩放); 面板级 exc_bian_2021_score_negadv{track} = 剔除疑似退出覆盖媒体后, bank-year 内文章级得分的算术均值"
producer: news_process/pipeline/panel/attention_media.py::(停刊稳健性聚合, C.4 动态发现 exc_* 列); 上游文章级得分 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores (_RULE_ABLATION_VARIANTS 'negadv')
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (bian_2021_score_negadv_full / _ctx / _ss)
- 21_tone_llms.parquet (媒体来源列 用于停刊代理检测)
- 42_cessation_report.xlsx (ceased_all = confirmed ∪ suspected 退出覆盖媒体集)
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
- doi: "10.1093/llc/fqae013"
  type: "journal"
  authors: "Venglařová, K., & Matlach, V."
  year: 2024
  title: "Beyond content: discriminatory power of function words in text type classification"
  venue: "Digital Scholarship in the Humanities"
  vol: "39"
  issue: "2"
  pages_or_artno: "765-789"
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是一条稳健性专用的词典法情感语调: 在把"疑似退出本地覆盖的媒体"保守剔出样本之后, 用 Bian et al. (2021) 编纂的中文金融情感词典对每篇银行金科报道打分, 并在 negadv (否定 + 转折, 停用程度副词) 这一条规则消融组合下取值, 最后按银行-年做算术平均得到面板列。它回答的问题不是"银行的情感语调有多正/多负"这一主构念本身, 而是"当我把可能因报纸停刊或退出话题覆盖而产生的样本选择性剔除掉、并且只保留否定翻转与转折加权两条语言学规则时, 主语调结论是否依然成立"。因此本家族的三列全部是 standard 稳健性轨, 不承担任何 paper 的 primary treatment 角色, 存在的意义是给主词典语调提供一个"样本口径 × 规则口径"双重扰动下的旁证。

构念的三层来源需要逐层说清。第一层是底层词典: bian_2021 指 Bian, Jia, Li 与 Yan (2021) 在 Loughran 与 McDonald 英文金融词表基础上做中文本土化扩充得到的情感词典 (正面 1,107 词 / 负面 1,488 词), 项目内以 tone_dicts.json 为唯一事实源加载, 跨类重叠词按用户 2026-06-24 决策做两侧并计数。第二层是规则消融维度: 文章级打分核心是状态机 _compute_sentiment_with_rules, 它可开关三条中文语言学规则——否定词在 NEGATION_WINDOW=2 个分词单元内翻转极性、程度副词按 HowNet 六级体系缩放幅度、转折连词 (但是/然而 等) 之后的情感按 ADVERSATIVE_BOOST=1.5 加权 (因作者真实立场常落在转折之后, 句末标点重置作用域, 该从句级作用域处理延续 Taboada et al. (2011) 提出的 lexicon-based 效价转移规则谱系)。negadv 变体的开关组合是 apply_negation=True、apply_degree=False、apply_adversative=True, 即在 full (三规则全开) 基础上关掉程度副词缩放这一条, 语义上等于"full 减去 degree"。第三层是样本口径: exc 前缀表示"剔疑似停刊媒体"——面板聚合前先经 detect_defacto_cessation 识别在样本期内不再出现的媒体来源作为停刊代理 (cessation proxy), 把 confirmed ∪ suspected 合集里的媒体所发文章整体剔除, 只对存活媒体子集求均值。

【方法学与计算】
计算分两级。文章级 (stage 22, tone_words.compute_dict_scores 内 _RULE_ABLATION_VARIANTS 循环) 先对三轨文本各自分词, 在 negadv 规则组合下逐 token 施加否定翻转与转折加权, 每命中一个情感词得到一个带号的 final 值, 全篇归一化得 bian_2021_score_negadv{track} = Σ(final) / Σ|final| ∈ [-1, +1]。该分母是幅度和 Σ|final| 而非裸匹配词数, 且每个消融变体各自 self-normalize, 因此相邻消融级差并非"某规则的纯贡献", 只作 ablation 对照 (audit MATH-1: 消融变体间高度共线, corr 常达 0.99 量级, 披露报 corr 而非并入同一分解式)。面板级 (stage 40, attention_media.py 停刊稳健性 C.4 段) 先由 _is_ceased_media 标记文章所属媒体是否属退出覆盖集, 取 df_alive = 非停刊子集, 对匹配 _SCORE_PATTERNS 的每个文章级得分列 (含 bian_2021_score_ 前缀) 做 bank-year groupby-mean, 输出列名机械前缀 exc_, 即 exc_bian_2021_score_negadv{track}。停刊代理口径须保守解读为"疑似退出覆盖媒体", 不可在论文中表述为严格出版停刊 (NPPA 交叉验证仅改报告标签, 不改剔除集)。此列属情感类, 零文章 bank-year 保持 NaN (不同于计数类 n_articles_exc 的零填契约), 勿连带零填。

【文献定位】
方法学上本家族坐落在词典法金融情感测量与其稳健性设计的交叉点。Bian et al. (2021) 提供底层中文词表; Du et al. (2022) 在 Review of Finance 论证中文金融文本的语言与领域特异性, 说明为何需要本土化词典而非直接移植英文词表, 是本家族选用中文专用词典的直接依据。转折与否定这类效价转移规则的语言学处理谱系可追溯到 Taboada et al. (2011) 在 Computational Linguistics 提出的 lexicon-based 效价转移方法, negadv 变体保留转折加权、停用程度缩放正是对该谱系中单条规则贡献的敏感性检验。Barbaglia et al. (2025) 的经济文本 lexicon-based 情感分析进一步支持在计量研究中以透明可复现的词典法作为主测度或旁证。方法互证层面, Frankel, Jennings 与 Lee (2022) 在 Management Science 系统比较词典法与机器学习法的披露情感测量, 为本项目"LLM 三家投票为共识 headline、词典法与 BERT 各自并排互为稳健"的多方法设计提供先例; van Atteveldt, van der Velden 与 Boukes (2021) 则从效度角度比较人工标注、众包、词典与机器学习, 提示词典法在特定语域下的适用边界。据此, exc × negadv × 三轨构成的稳健性列并非独立信号, 而是与主词典语调、LLM 语调、BERT 语调各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同规则消融变体或不同样本口径混进同一 over-identified Hansen J 的过度识别检验。三轨 (full/ctx/ss) 亦遵同一铁律: full=标题 prepend 全文正文, ctx=标题+实体窗口, ss=标题+银行与金科同句共现窗 (ss 无共现时回退镜像 ctx/全文, 与 full-only 留篇门控口径一致), 三轨禁混同一 over-identified Hansen J。 补充的近期方法学证据进一步锚定本族所激活的两条规则与其样本口径。Naldi 与 Petroni (2023) 提出一套基于人工构造测试集的评测方法, 专门度量词典法情感工具对否定的检测与处理能力, 并实证发现各工具在该模块上的表现差异显著; 这为把否定翻转视作词典状态机内可被单独测量、单独失效的模块, 进而单列为一条可独立开关的消融臂, 提供了最贴近的方法学依据。迁移边界须诚实交代: 该文是英文通用领域 (非金融) 的工具评测, 指标为否定检测准确率, 而本族并不评测否定检测是否正确, 只把否定规则的开/关作为银行-年度面板测度的一条稳健性臂, 语料亦为中文金融新闻。转折通道值得与情感词极性分开单列这一构念前提, 由 Venglařová 与 Matlach (2024) 侧面补强: 该文实证显示连词一类功能词在文本类型判别上携带独立于内容词的信息量; 但原文任务为文本类型分类, 并不区分转折连词与其他功能词类, 语料非中文金融新闻, 亦不涉及本族的效价放大与银行-年度聚合, 故仅作构念层旁证, 不构成本族转折加权具体做法的依据。exc_ 口径的现实动机则由 Cziraki 与 Gider (2024) 补充: 该工作论文以报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 说明媒体退出是真实且有经济后果的样本组成变化。惟须注明, 原文的停刊判定取自外部事件数据并被用于识别冲击, 而本族 ceased_set 是自语料内部推断的疑似退出覆盖保守代理 (confirmed ∪ suspected), 并非严格停刊事实, 用途仅限稳健性子样本; 该文为工作论文, 未经同行评审。
## VAR: exc_bian_2021_score_negadv_ctx

【变体差分】
本列在家族三层口径之上, 轨道维度取 ctx (context/实体窗口轨)。ctx 文本 = 标题 prepend + 围绕目标银行与金科实体的上下文窗口 (在 stage 14 ctx_materializer 物化 content_ctx), 相对 full 轨剔除了与银行金科无关的段落, 使词典打分更聚焦于报道中真正谈及目标主体的语句, 降低无关正负面词对语调的稀释。其余三处口径与家族一致: 底层 bian_2021 中文金融词典、negadv 规则组合 (否定翻转 + 转折加权, 停用程度副词缩放, 等于 full 减 degree)、exc 样本口径 (面板聚合前剔除疑似退出覆盖媒体, 仅对存活媒体子集求 bank-year 均值)。取值 self-normalized 至 [-1, +1], 情感类零文章格保持 NaN。相对家族 canonical (full 轨) 差分点仅在文本范围: ctx 是主词典语调在稳健性谱中的 conditional-on-full 测度轨, 行宇宙为 full 留篇集的子集, per-track 列照算。与 full/ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。ctx 轨在早期试跑 T=2 语料上因窗口收窄可能出现方差退化, 属预期现象, 生产 T=19 恢复正常。需要提醒的是, ctx 与 full 的差别只在文本切分范围, 底层词典、negadv 规则开关与 exc 停刊剔除三者完全相同, 因此本列与同名 full 列的相关性通常很高, 它的增量价值在于回答"若把语调测量限定在真正谈及银行金科的上下文窗口内, 主结论是否仍成立"这一样本敏感性问题, 而非提供一个方向可能相反的独立信号。读者不应把 ctx 与 full 的微小数值差异解读为实质性分歧, 而应把二者一致视为稳健性得到满足的证据。

## VAR: exc_bian_2021_score_negadv_full

【变体差分】
本列轨道维度取 full (全文轨), 是家族在轨道意义上的 canonical 位置。full 文本 = 标题 prepend + 完整正文 body (原始内容列不动, 标题改 prepend 而非独立 title 轨, title 独立轨已于 v3.8.0 移除), 词典打分覆盖整篇报道全部句子。相对 ctx/ss 两轨, full 不做实体窗口或同句共现的文本裁剪, 因此纳入最多的情感词, 但也可能纳入与目标银行金科无关段落的正负面信号。其余三处口径与家族一致: bian_2021 中文金融词典、negadv 规则 (否定 + 转折, 停用程度, 等价 full 三规则减 degree 缩放这一条)、exc 样本口径 (面板聚合仅对非疑似退出覆盖媒体子集求 bank-year 均值)。取值 self-normalized 至 [-1, +1], 情感类零文章格保持 NaN。full 轨是 2026-06-29 起留篇门控与主轨切换所锚定的轨道 (留篇门控 = full-only, 只看 full 轨是否判为一篇银行金科报道), 但就本稳健性家族而言 full 仅是三轨之一, 与 ctx/ss 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。需强调 negadv 与主列 (三规则全开的 bian_2021 语调) 在实测中高度共线, 本列意义在于证明主语调对"是否施加程度副词缩放"这条规则不敏感, 而非提供独立于主语调的新信息。之所以要在 full 轨上同时叠加 exc 停刊剔除与 negadv 规则消融两层扰动, 是因为单独任何一层都只能排除一种质疑: 只做 exc 无法回应"结论是否被程度副词加权规则驱动", 只做 negadv 又无法回应"结论是否被可能退出覆盖的媒体样本选择性驱动", 二者叠加才能同时封堵样本口径与规则口径两条批评路径。因此本列在稳健性谱系中处于"最全文本范围 × 最保守样本 × 去程度规则"的交叉格, 是主词典语调最直接的对照参照臂。

## VAR: exc_bian_2021_score_negadv_ss

【变体差分】
本列轨道维度取 ss (同句共现轨)。ss 文本 = 标题 prepend + 目标银行与金科词在同一句子内共现的句子及其 ±N 句窗 (半径由 config filtering.yaml context_window.ss_sentence_radius 控制, 默认 1; 与 stage 13 cooccurrence_filter.sentence_radius 是两个不同键), 是三轨中语境最严的一轨, 只保留银行与金科真正被同句谈及的语句, 最大限度排除偶然共现造成的语调污染。回退语义镜像 ctx: 当全篇无银行与金科同句共现时, content_ss 回退为全文 body、ss_is_fallback=True, 共享 n_articles 分母; 若 FINTECH_AC=None 则 ss_is_fallback 全 True 优雅降级。其余三处口径与家族一致: bian_2021 中文金融词典、negadv 规则组合 (否定翻转 + 转折加权, 停用程度副词缩放)、exc 样本口径 (面板聚合仅对疑似退出覆盖媒体之外的存活媒体子集求 bank-year 均值)。取值 self-normalized 至 [-1, +1], 情感类零文章格保持 NaN。ss 是 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集。与 full/ctx 两轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。早期试跑 T=2 上 ss 轨因同句共现样本稀薄常出现零方差或大量回退, 属预期退化, 生产 T=19 恢复正常语境区分度。ss 与 ctx 的关键区别在于共现判据的严格程度: ctx 只要求实体落入上下文窗口, ss 则要求银行与金科在同一句子内共现, 因而 ss 的语境纯度最高但可用样本最少, 回退率也最高。正因回退机制存在, ss 轨的取值在多数 bank-year 上会与 ctx 或 full 趋同 (回退即镜像上位轨文本), 这是设计使然而非缺陷——回退保证了 ss 轨永远有定义、不产生单边孤儿列, 与 co-primary 双轨 both-or-neither 的优雅降级精神一致。综合看, ss 是三轨中语境约束最强的稳健性对照臂, 用于回答"即使把语调测量收紧到最严的同句共现范围, 主结论是否依然成立"。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Venglařová, K., & Matlach, V. (2024). Beyond content: discriminatory power of function words in text type classification. Digital Scholarship in the Humanities, 39(2), 765-789. https://doi.org/10.1093/llc/fqae013
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
