---
family_id: F068
columns:
- avg_specificity_ctx
- avg_specificity_full
- avg_specificity_ss
unit: token 占比 (无量纲, 值域 [0,1] ∪ NaN)
formula: "avg_specificity_{track} = bank-year mean of article-level specificity_index; specificity_index = (nr+ns+nt+nz 具名实体 token + m 硬数词 token) / n_real 实词 token 数 (剔除标点及未知词性 _PUNCT_FLAG='x' 后的分词 token 数); 逐轨 track ∈ {full, ctx, ss} 用各轨文本 content_{track} 各调用一次"
producer: news_process/pipeline/sentiment/lexical_complexity.py::compute_lexical_complexity ; news_process/pipeline/panel/encode.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (lexical_complexity per-track 派生)
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1007/s11142-016-9371-1
  type: journal
  authors: Hope, O.-K., Hu, D., & Lu, H.
  year: 2016
  title: "The benefits of specific risk-factor disclosures"
  venue: Review of Accounting Studies
  vol: 21
  issue: 4
  pages_or_artno: 1005-1045
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
- doi: "10.1177/14648849241262204"
  type: "journal"
  authors: "Thäsler-Kordonouri, S., Thurman, N., Schwertberger, U., & Stalph, F."
  year: 2025
  title: "Too many numbers and worse word choice: Why readers find data-driven news articles produced with automation harder to understand"
  venue: "Journalism"
  vol: "26"
  issue: "9"
  pages_or_artno: "1878-1898"
new_dois:
- 10.1007/s11142-016-9371-1
---

## CORE

【构念与来源】
本家族刻画"报道硬信息密度"(specificity / hard-information density), 即一篇银行金融科技新闻里具名实体与数字所占的词汇比重。构念直接锚定 Hope, Hu 和 Lu (2016) 在披露文本研究中提出的 specificity 思想: 一段文本越是充斥可核验的硬信息 (谁、在哪、哪家机构、多少金额), 其信息含量与可验证性越高; 反之充满抽象、模糊、不可核验措辞的文本, 其"软性"程度更高。原始文献处理的是上市公司 10-K 风险因子披露的自我陈述具体性, 本项目将其 reframe 为"媒体报道的硬信息密度"—— 度量对象不是银行自我披露, 而是第三方媒体报道正文, 因此措辞上刻意避免声称等同于监管披露 specificity, 仅作为报道文本质量维度的一个 $0 代理测度。

【方法学与计算】
文章级 specificity_index 在 lexical_complexity 模块内, 对每篇文本做单次 jieba.posseg (0.42.1 冻结词典) 词性标注 pass, 分子 = 具名实体类词性 token 数 (nr 人名 / ns 地名 / nt 机构名 / nz 其他专名) 加硬数词 token (m, 且过 _is_hard_m_token 排除一些/许多/若干/几X/数X 等模糊量词) 之和, 分母 = n_real 实词 token 数 —— 即对该文分词后剔除标点及未知词性 (_PUNCT_FLAG='x') 得到的实词 token 数, 而非包含标点在内的全部 token 数, 故本占比是 over 实词分母而非 over 原始切分总数, 得一个位于 [0,1] 的 token 占比。compute_lexical_complexity 本身 track-agnostic: 输入单一文本、返回 per-text 字典; 三轨 (full/ctx/ss) 的 per-track 循环由调用方 tone_words 用各轨物化文本 content_full / content_ctx / content_ss 各驱动一次。文章级 specificity_index 落盘于 22_tone_words 派生后, 面板列则由 encode 聚合层 (pipeline/panel/encode.py, 对 specificity_index{track} 取 mean 聚合) 对留篇集内文章逐轨取 bank-year 均值得到 (codebook 只产 codebook 描述与标签、geography 只做 ln 等下游变换, 均不承担本列的均值聚合), 单位与值域为 token 占比 [0,1] ∪ NaN (该银行-年在某轨无有效文章时置 NaN)。诚实限定须写入论文: jieba.posseg 走词典加 HMM, 其 nr/ns/nt 实体边界与歧义判定精度低于专用 NER, 故本测度是"以词性近似硬信息类别"的粗近似 / 上界噪声估计, 不应声称等同 Stanford NER 等专用命名实体识别; 数词 m 的口径亦受分词切分影响。

【文献定位】
specificity 的信息经济学根基可上溯至 Spärck Jones (1972) 对"术语特异性"(term specificity) 的统计诠释 —— 越稀有、越具体的词项携带越高的检索区分度 (IDF 思想), 与本测度"具名实体与数字承载硬信息"的直觉同源。会计与金融文本分析文献中, Hope, Hu 和 Lu (2016) 系统论证了披露具体性 (specific risk-factor disclosures) 对市场信息效率的正向价值, 是本构念的主锚。将文本测度落地于中文金融语料时, 词典与领域特异性问题尤为关键: Du 等 (2022) 在《Review of Finance》上构建中文金融情感词典时明确指出, 语言与领域特异性 (language and domain specificity) 决定了英文文本工具不能简单移植到中文金融语境, 本家族对 jieba 词性近似口径及其精度限定的坦诚披露正是对这一警示的呼应。三轨口径遵循 CLAUDE.md 铁律: full/ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J; 且非嵌入族测度无 co-primary 双轨嵌入的 _lg 孪生。留篇门控采 full-only 口径 (2026-06-29): 一篇是否计入"银行金融科技报道"仅看 llm_verified_full == True, ctx/ss 降为 conditional-on-full 的测度轨, 行宇宙为 full 留篇集的子集, per-track 列在各自轨照算。 在新闻文体一侧, Thäsler-Kordonouri、Thurman、Schwertberger 与 Stalph (2025) 以 3135 名读者的在线问卷实验与因子分析, 抽取出影响读者评价的五类文章构成维度, 其中"数字特征 (numeric features)"与"用词选择"两类与本族构念指向一致, 并据此建议后编辑时减少数字数量、解释读者不易理解的词; 该文为"数字密度是新闻文本中可被识别的构成性属性"提供了同域 (新闻) 的动机来源, 但须标明三重边界。其一, 原文测量的是读者对上述维度的主观感知评分 (survey experiment 加因子分析), 并未计算数词占比等文本统计量, 故不得据本文声称本族数字密度测度的实现先例; 其二, 原文语料为英语/德语的自动化数据新闻, 结果变量为读者理解度, 无机构—年聚合层级; 其三, 原文结论方向 (数字越多越难懂) 与本族把具体性读作硬信息密度的正向诠释并不等同, 且本族分子除过 _is_hard_m_token 过滤的硬数词外还含 nr/ns/nt/nz 具名实体 token、分母为实词数, 与原文的数字感知口径不同。因此该文在本族只作动机与构念张力的旁证, 不承担对 specificity_index 测度效度的背书。
## VAR: avg_specificity_full

【变体差分】
本列是 full 轨: 文本 = content_full, 即标题 prepend 到全文正文后的完整文章文本 (标题第 0 句 + body)。full 轨是本家族的 headline / canonical 轨, 也是 full-only 留篇门控 (2026-06-29) 直接作用的轨 —— 一篇文章是否计入某银行-年的报道宇宙, 仅由 llm_verified_full == True 判定, 故 avg_specificity_full 的 bank-year 分母是最完整的留篇集。相对 ctx/ss 两轨, full 轨覆盖全文所有句子, 具名实体与数词的采样面最广, 通常也最稳定, 受同句共现回退语义影响最小。与 ctx/ss 的差分仅在文本范围: 本轨不做实体窗口或同句裁剪, 度量整篇报道的硬信息密度。三轨定位铁律: avg_specificity_full 与 avg_specificity_ctx、avg_specificity_ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 本轨作为主测度进入回归时, 另两轨作规格稳健性对照, 不得同式并入。方法学上须重申: full 轨 specificity 分子的具名实体 (nr/ns/nt/nz) 与数词 (m) 由单次 jieba.posseg pass 派生, 对全文所有句子统一切词标注, 因而本轨对篇内不同段落的实体密度差异不敏感, 报告的是整篇平均硬信息浓度。在共现回退问题上 full 轨天然免疫 —— 它本就取全文, 不存在 ss/ctx 那样的窗口裁剪与回退分支, 故 avg_specificity_full 在低共现银行-年上的数值最稳健、最不受 *_is_fallback 结构影响, 这也是把它设为家族 canonical 与 full-only 留篇门控载体轨的实证理由。

## VAR: avg_specificity_ctx

【变体差分】
本列是 ctx 轨: 文本 = content_ctx, 即标题 prepend 加"实体上下文窗口" —— 只保留围绕目标银行实体出现位置的局部文本窗口, 而非整篇正文。相较 full 轨, ctx 轨把度量对象收敛到与目标银行邻近的语句范围, 意在剔除报道中与该银行无关的段落对硬信息密度的稀释或污染; 其代价是文本更短、采样面更窄, 具名实体与数词的占比估计方差更大。在留篇门控上, ctx 轨为 conditional-on-full 的测度轨: 其行宇宙是 full 留篇集的子集, 一篇是否留篇仍由 full 轨的 llm_verified_full 决定, ctx 列只在该子集上逐轨计算 per-track 均值, 不独立开门。三轨铁律照旧: avg_specificity_ctx 与 full、ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。本轨作为 full 轨的首要稳健性对照存在, 用于检验硬信息密度结论是否被"全文 vs 银行邻近窗口"的文本范围选择所驱动。需要强调 ctx 的实体窗口口径与 stage 13 共现硬过滤是两个不同层级: stage 13 在上游按银行与金科邻近共现决定文章去留, 而 ctx 轨是在留篇之后于 stage 14 物化的 content_ctx 文本列上度量硬信息密度, 二者判据原语与作用对象均不重叠, 不得互相复用。由于 ctx 文本较 full 短, specificity 占比的分母更小, 单篇内一两个专名或数词的进出对占比的杠杆更大, 故本轨在文章稀少或篇幅极短的银行-年上方差偏大, 解读时宜与 full 轨并置对照, 而非孤立采信。

## VAR: avg_specificity_ss

【变体差分】
本列是 ss 轨: 文本 = content_ss, 即标题 prepend 加"银行与金融科技同句共现窗口" —— 只保留目标银行与金融科技词在同一句 (±N 句半径, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 内共现的局部文本。ss 轨是三轨中语义最聚焦的轨, 度量的是银行与金科议题真正交汇处的报道硬信息密度。其关键差分在于回退语义 (镜像 ctx): 当一篇文章不存在银行与金科的同句共现时, content_ss 优雅回退为全文 body, 且 ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母口径; 当 FINTECH_AC 为 None 时 *_is_fallback 全 True, 整轨优雅降级。因此在共现稀疏的银行-年, ss 轨会有相当比例的文章走 body 回退, 其数值向 full 轨趋近, 解读时须结合 ss_is_fallback 占比。留篇门控同为 conditional-on-full: 行宇宙是 full 留篇集子集, 留篇判定只看 full 轨。三轨铁律: avg_specificity_ss 与 full、ctx 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。须注意 ss 的同句共现窗口 (ss_sentence_radius) 与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个独立 config 键, 判据口径亦不同: ss 轨的物化判据严格锚定银行与金科同句 (extract_bank_fintech_cooccurrence), 与 stage 13 的邻近共现原语 (has_bank_fintech_cooccurrence_within_radius) 不可互相复用。作为三轨中语义最窄的轨, ss 在共现密集的银行-年提供最聚焦的硬信息密度信号, 但在共现稀疏处大量回退至全文 body 后其区分度趋于退化 (向 full 轨收敛), 因此它更适合作规格稳健性对照而非独立主测度; 论文报告须一并披露该银行-年的 ss_is_fallback 占比以正确解读数值。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hope, O.-K., Hu, D., & Lu, H. (2016). The benefits of specific risk-factor disclosures. Review of Accounting Studies, 21(4), 1005-1045. https://doi.org/10.1007/s11142-016-9371-1
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Thäsler-Kordonouri, S., Thurman, N., Schwertberger, U., & Stalph, F. (2025). Too many numbers and worse word choice: Why readers find data-driven news articles produced with automation harder to understand. Journalism, 26(9), 1878-1898. https://doi.org/10.1177/14648849241262204
<!-- rendered-citations:end -->
