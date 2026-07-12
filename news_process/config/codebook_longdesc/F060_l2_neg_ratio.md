---
family_id: F060
columns:
- avg_neg_ratio_ctx
- avg_neg_ratio_full
- avg_neg_ratio_ss
- avg_neg_ratio_std_ctx
- avg_neg_ratio_std_full
- avg_neg_ratio_std_ss
unit: 比率/占比 (无量纲, 文章级 ∈ [0,1]; 银行-年 avg 为文章级均值, std 为文章间样本标准差)
formula: "文章级 neg_ratio{track} = union_neg_count / n_word_tokens (n_word_tokens=0 → NaN); 面板 avg_neg_ratio{track} = mean_i(neg_ratio{track}); avg_neg_ratio_std{track} = std_i(neg_ratio{track}) (ddof=1, 银行-年内文章间样本标准差)"
producer: news_process/pipeline/sentiment/tone_words.py::_compute_sentiment_with_rules (文章级, 经 _analyze_single_article / classify_batch 批处理) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (银行-年聚合)
upstream:
- 21_tone_llms.parquet (content_full/content_ctx/content_ss)
- 22_tone_words.parquet (neg_ratio_full/neg_ratio_ctx/neg_ratio_ss)
- 40_panel_yearly.parquet
citations:
- doi: 10.1007/s10479-025-06567-y
  type: journal
  authors: Anastasiou, D., Katsafados, A., & Tzomakas, C.
  year: 2026
  title: "Banks' stock price crash risk prediction with textual analysis: A machine learning approach"
  venue: Annals of Operations Research
  vol: 357
  issue: 1
  pages_or_artno: 89-111
- doi: 10.1108/JED-06-2025-0296
  type: journal
  authors: Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B.
  year: 2025
  title: "Investor negativity derived from news shapes firm distress dynamics under bounded rationality"
  venue: Journal of Economics and Development
  vol: 27
  issue: 4
  pages_or_artno: 309-321
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: Article 20
- doi: 10.1093/qje/qjx045
  type: journal
  authors: Hansen, S., McMahon, M., & Prat, A.
  year: 2018
  title: "Transparency and deliberation within the FOMC: A computational linguistics approach"
  venue: Quarterly Journal of Economics
  vol: 133
  issue: 2
  pages_or_artno: 801-870
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  issue: ""
  pages_or_artno: 67-75
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: Journal of Finance
  vol: 67
  issue: 2
  pages_or_artno: 561-598
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一家银行在某一年度的新闻报道中"负面用词的密度", 即报道文本里被固定金融情感词典判为负面的词条相对文本用词总量的占比。构念根源是金融文本分析的一条基本主张: 净情感 (正减负) 会因正负极性在同一分母上相互对冲而掩蔽信息, 因而将负面词频作为独立协变量单独度量, 比只看净值更能保留"坏消息含量"这一维度的变异。负面词密度是媒体语气 (media tone) 与坏消息披露强度的直接文本代理, 在银行金融科技叙事中承担"舆论压力/声誉风险信号"的角色。构念的经济含义有坚实文献支撑: 媒体对企业的负面倾向会独立影响其估值与融资 (Gurun & Butler 2012), 而在中国制度环境下, 负面信息的生成与抑制本身受政治激励约束 (Piotroski, Wong & Zhang 2015), 这使得"报道中还剩多少负面用词"成为一个既有测量意义又有识别意义的量。数据来源是本项目 stage 22 词典法情感阶段: 上游读入 stage 21 经 LLM 语义精筛确认的银行金融科技报道 (content_full/content_ctx/content_ss 三轨文本), 在词条层扫描后聚合到银行-年面板。

【方法学与计算】
文章级 neg_ratio 的分子 = 固定 union 词典判定的负面词计数 (union_neg_count), 分母 = 该文本的实词 token 数 (n_word_tokens, 排除纯标点与纯数字), 分母为零时取 NaN, 结果四舍五入到 6 位。这里的"固定 union 词典"是本项目 2026-06-11 的关键测度纠正: pos_ratio/neg_ratio/msent_score 的计数基从旧的"逐篇匹配数最多的词典" (best-dict, 会让测量工具随观测漂移) 改为六部中文金融情感词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 / loughran_mcdonald_zh_2026) 并集后、对跨类重叠词以极性多数票消解、平票剔除而成的单一全样本词表, 兑现 Tetlock (2007)、Garcia (2013)、Henry (2008) 所要求的"固定词表"构念——同一把尺子量所有观测。词条扫描叠加三条语言学规则: 否定词在窗口内翻转极性、程度副词六级放大或缩小强度、转折连词后权重提升。面板聚合在 encode 层按银行-年分组: avg_neg_ratio{track} 取组内文章级 neg_ratio 的均值, avg_neg_ratio_std{track} 取组内文章间的样本标准差 (pandas std, ddof=1)——须强调 std 后缀是"银行-年内跨文章离散度", 度量该行当年不同报道在负面密度上的分歧程度, 并非把均值做 z 标准化, 两者语义正交不可混淆。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科报道宇宙, 只看 full 轨的 LLM 判定; ctx/ss 轨降为 conditional-on-full 的子集测度, 各轨 per-track 分子分母严格逐轨自洽。

【文献定位】
负面词频作为文本情感的独立维度, 上承 Garcia (2013) 将正负面词分离为独立协变量、Loughran & McDonald (2011) 的固定词表方法学传统; 计量文本测度的规范做法与可复现性可锚 Hansen, McMahon & Prat (2018) 在 FOMC 语料上的计算语言学框架。否定处理是负面词密度可信度的命门, 因为漏判否定会把"并非坏消息"误计为负面, 本项目的否定翻转窗口与 Pröllochs, Feuerriegel & Neumann (2016) 的否定作用域检测、Punetha & Jain (2025) 的否定处理数学方法同属一脉。构念的下游价值在近期银行文本研究中持续得到印证: Anastasiou, Katsafados & Tzomakas (2026) 用文本分析预测银行股价崩盘风险, Pham 等 (2025) 论证由新闻派生的投资者负面情绪对企业困境动态的塑造作用, 均说明"报道负面密度"是银行风险与舆论研究的有效前置变量。三轨 (full/ctx/ss) 与 avg 主测度、std 离散度测度之间: 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同轨的同名列混进同一 over-identified Hansen J; avg 与 std 度量的是均值水平与年内分歧两个不同构念, 应各自入回归右手侧而非并列进同一识别式。

## VAR: avg_neg_ratio_full

【变体差分】
本列是 full 轨的负面词密度均值, 也是本家族语义上的 canonical/主轨。full 轨文本 = 标题 prepend 后拼接全文正文 (content_full), 覆盖整篇报道的全部用词, 故其 neg_ratio 反映的是"整篇报道层面的负面用词占比", 是坏消息含量最全景的口径。作为主轨, full 承担留篇门控职责: 银行-年的报道计数 (n_articles) 与该行是否被判为一篇银行金科报道, 均以 full 轨的 LLM 判定为准, 因此本列的分母文章集就是该行当年 full 留篇宇宙, 与 ctx/ss 的 conditional-on-full 子集口径相区别。计算上, 先对每篇 full 文本按固定 union 词典扫描得文章级 neg_ratio_full = union 负面词计数 / 实词 token 数, 再在银行-年分组取均值 (mean)。该列与同轨的 avg_neg_ratio_std_full 构成"水平-离散"配对: 前者答"平均有多负", 后者答"各报道之间负面程度是否分歧"。与另两轨的对应列 avg_neg_ratio_ctx / avg_neg_ratio_ss 互为稳健性、不分主次: 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。full 轨因用词最全, 通常分母最大、单篇极值被稀释, 数值相对平稳, 适合作为基准规格的主变量。分子的固定 union 词典与三条语言学规则 (否定翻转、程度副词六级、转折增强) 保证了跨银行、跨年度用同一把尺子度量负面用词, 使本列在面板固定效应回归中具有可比的水平含义; 当研究关心的是"这家银行的报道整体有多负"时, 本列是首选主轨口径。

## VAR: avg_neg_ratio_ctx

【变体差分】
本列是 ctx (context) 轨的负面词密度均值。ctx 轨文本 = 标题 prepend 后拼接"银行实体上下文窗口"内的正文片段 (content_ctx), 即只保留围绕目标银行实体出现处的邻近文字, 而非整篇正文。其构念意图是把负面用词的度量收敛到"与该银行直接相关的语境", 降低同篇报道里与本行无关段落的噪声干扰, 因此相较 full 轨它是一个更聚焦、更贴近实体的稳健性口径。计算链路与 full 同构: 每篇 content_ctx 按固定 union 词典扫描得文章级 neg_ratio_ctx = union 负面词计数 / 实词 token 数, 银行-年内取均值。留篇口径为 conditional-on-full: 是否算一篇银行金科报道仍由 full 轨门控决定, ctx 只在该 full 留篇子集上按自身轨文本重算负面密度, 分子分母严格逐轨自洽, 不借用 full 轨的分母。与 avg_neg_ratio_full / avg_neg_ratio_ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨同名列混进同一 over-identified Hansen J。当实体窗口内文本较短时, 单篇负面密度的分母偏小、方差偏大, 使用时应结合同轨 std 列判断年内稳定性。相对 full 主轨, 本列的价值在于抑制"整篇报道里与本行无关的负面语段"造成的虚高: 例如一篇同时报道多家银行风险事件的文章, full 轨会把他行的负面用词一并计入本行分子, 而 ctx 轨仅保留围绕本行实体的邻近文字, 从而给出更贴近本行的负面密度估计, 因此它承担实体聚焦稳健性检验的角色。

## VAR: avg_neg_ratio_ss

【变体差分】
本列是 ss (same-sentence) 轨的负面词密度均值。ss 轨文本 = 标题 prepend 后拼接"银行与金融科技词同句共现的句子及其 ±N 句窗口" (content_ss, 句半径由 config 的 ss_sentence_radius 控制, 默认 1), 是三轨中语境最窄、最贴近"银行∧金科共现"焦点的口径, 意在度量真正围绕银行金融科技话题那几句里的负面用词占比。其回退语义镜像 ctx: 当一篇报道不存在银行与金科的同句共现时, content_ss 优雅降级为全文正文、ss_is_fallback 置 True, 与 ctx 无实体命中时的回退处理同构, 保证无共现文章不被静默丢弃而是以全文兜底并共享 n_articles 分母。计算上每篇 content_ss 按固定 union 词典扫描得 neg_ratio_ss, 银行-年内取均值。留篇仍为 full-only 门控下的 conditional-on-full 子集, ss 只在 full 留篇集上按自身轨文本重算, 分子分母逐轨自洽。与 avg_neg_ratio_full / avg_neg_ratio_ctx 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。ss 轨在开发期短面板上因共现句稀疏可能退化, 应以生产语料口径解读。三轨中 ss 语境最窄, 其负面密度最能反映"银行金融科技这一话题本身在报道里被以多负的措辞讨论", 剔除了报道中其他主题段落的干扰, 因此它是与研究焦点最对齐的稳健性口径; 但也正因窗口窄、分母小, 加之回退到全文的比例会随共现稀疏而上升, 本列在解读时须同时参考 ss_is_fallback 占比与年内报道数, 避免把兜底文本的负面密度误当作焦点语境的度量。

## VAR: avg_neg_ratio_std_full

【变体差分】
本列是 full 轨负面词密度在银行-年内跨文章的样本标准差 (pandas std, 默认 ddof=1), 度量该行当年不同报道在负面用词占比上的离散/分歧程度, 而非负面水平本身。须严格区分: 后缀 std 指"文章间标准差"这一二阶离散测度, 绝不是把 avg_neg_ratio_full 做 z-score 标准化——它与均值列 avg_neg_ratio_full 构成正交的"水平-离散"配对, 一个答"平均有多负", 另一个答"各报道之间负面程度是否一致"。构念价值在于捕捉媒体报道内部的情感异质性: 高 std 意味着该行当年的报道在正负基调上分裂 (例如同期既有正面宣传又有负面事件曝光), 低 std 意味着口径趋同, 这一维度对研究信息环境的分歧、报道冲突或叙事不确定性尤为有用。计算基与 avg 同源, 均建立在 full 轨文章级 neg_ratio_full 之上, 只是聚合算子由 mean 换成 std, 留篇同为 full 门控。当银行-年内有效文章数过少 (例如仅一篇) 时, 样本标准差不可估或极不稳定, 会返回 NaN 或高噪声值, 使用时须配合报道计数解读。作为 std 家族的主轨口径, 本列建立在 full 全文文本上, 覆盖整篇报道的负面用词分布, 因而其离散度既包含真实的报道基调分歧, 也天然稀释了单篇短文本的抽样噪声, 相对 ctx/ss 两轨的 std 更稳。研究媒体信息环境的分歧、报道内部冲突或叙事不确定性时, 本列可作为年内情感异质性的基准代理, 与均值列 avg_neg_ratio_full 一并进入回归可同时刻画"平均负面水平"与"负面基调是否分裂"两个独立维度。与 std_ctx / std_ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

## VAR: avg_neg_ratio_std_ctx

【变体差分】
本列是 ctx 轨负面词密度在银行-年内跨文章的样本标准差 (ddof=1), 与 avg_neg_ratio_std_full 语义同构, 差别仅在计算基是 ctx 轨的文章级 neg_ratio_ctx——即先把负面密度收敛到银行实体上下文窗口内再算年内离散度。因此本列度量的是"聚焦于该银行相关语境后, 各报道之间负面用词占比的分歧程度", 剔除了整篇报道中与本行无关段落对离散度的干扰, 是 std_full 的实体聚焦稳健性口径。同样须与均值列 avg_neg_ratio_ctx 区分: std 是文章间二阶离散测度, 不是均值的 z 标准化, 二者正交配对分别刻画年内水平与年内分歧。留篇遵循 full-only 门控下的 conditional-on-full 子集, ctx 只在 full 留篇集上按自身轨文本重算 neg_ratio_ctx 后取标准差, 分子分母逐轨自洽, 不借用 full 分母。由于 ctx 窗口文本较短, 单篇 neg_ratio_ctx 的抽样波动本就偏大, 其年内标准差会同时含"真实报道分歧"与"短文本测量噪声"两部分, 解读时应审慎, 并结合样本量。本列的定位是 std_full 的实体聚焦稳健性变体: 当研究者担心整篇报道中他行相关的负面段落会污染年内离散度估计时, 可改用本列, 因为它先把度量收敛到本行实体上下文再算文章间标准差, 使离散度更集中于"关于本行的报道基调是否一致"这一构念。与 std_full / std_ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

## VAR: avg_neg_ratio_std_ss

【变体差分】
本列是 ss 轨负面词密度在银行-年内跨文章的样本标准差 (ddof=1), 计算基为 ss 轨文章级 neg_ratio_ss, 即在"银行与金融科技同句共现句 ±N 窗口"这一最窄语境上先算每篇负面密度、再取银行-年内文章间标准差。它度量的是聚焦到银行金科共现焦点后, 各报道之间负面用词占比的分歧程度, 是 std 家族里语境最贴近研究话题的离散度口径。回退语义仍镜像 ctx: 无银行∧金科同句共现的报道以全文正文兜底 (ss_is_fallback=True) 并共享 n_articles 分母, 因此本列的离散度在共现稀疏的银行-年上会受回退文本比例影响, 须结合 fallback 占比解读。与均值列 avg_neg_ratio_ss 的区分同前: std 是文章间二阶离散测度, 非均值的 z 标准化, 两者正交。留篇为 full-only 门控下的 conditional-on-full 子集, ss 只在 full 留篇集上重算 neg_ratio_ss 后取标准差, 逐轨自洽。在开发期短面板 (T 小、共现句稀疏) 上, ss 轨的年内标准差极易因有效篇数不足而退化为 NaN 或高噪声, 属预期现象, 应以生产语料规模为准解读。本列的定位是把年内负面基调分歧收敛到"银行金融科技共现焦点"上的最窄语境稳健性口径: 当研究者关心的是围绕金科话题的报道措辞是否内部分裂 (例如同期既有正面合作宣传又有负面风险质疑) 时, 本列比 std_full/std_ctx 更贴近该焦点, 但代价是共现稀疏时回退到全文的比例上升、有效篇数下降, 离散度估计的可信度随之走低, 须结合 ss_is_fallback 占比审慎解读。与 std_full / std_ctx 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. Journal of Economics and Development, 27(4), 309-321. https://doi.org/10.1108/JED-06-2025-0296
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
<!-- rendered-citations:end -->
