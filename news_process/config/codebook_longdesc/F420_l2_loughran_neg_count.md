---
family_id: F420
columns:
- loughran_neg_count_ctx
- loughran_neg_count_full
- loughran_neg_count_ss
unit: 篇数/计数 (count)
formula: 'loughran_neg_count_{trk} = 逐篇统计 content_{trk} 中命中 loughran_mcdonald_zh_2026 词典 negative 集合 (3,729 词) 的词条出现次数之和 (含否定翻转后的极性判定, 不做长度归一化)'
producer: pipeline\sentiment\tone_words.py ; pipeline\panel\stata_export.py
upstream: []
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: 'Textual analysis in accounting and finance: A survey'
  venue: Journal of Accounting Research
  vol: '54'
  issue: '4'
  pages_or_artno: 1187-1230
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: A new Chinese financial sentiment dictionary for textual analysis in accounting and finance
  venue: SSRN Working Paper
  vol: ''
  issue: ''
  pages_or_artno: ''
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: 'Negation scope detection in sentiment analysis: Decision support for news-driven trading'
  venue: Decision Support Systems
  vol: '88'
  issue: ''
  pages_or_artno: 67-75
- doi: "10.1017/s0022109023000716"
  title: "Measuring Firm Complexity"
  authors: "Loughran, T., & McDonald, B."
  year: 2024
  venue: "Journal of Financial and Quantitative Analysis"
  type: "journal"
- doi: "10.3390/bdcc9100263"
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  venue: "Big Data and Cognitive Computing"
  type: "journal"
new_dois:
  - "10.1017/s0022109023000716"
  - "10.3390/bdcc9100263"
---

## CORE

【构念与来源】
loughran_neg_count 家族记录每篇报道中命中 Loughran & McDonald 中文主译词典 (config/tone_dicts.json 中 loughran_mcdonald_zh_2026, 内部列前缀别名 loughran) negative 类目的词条出现次数, 是本项目六部情感词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 / loughran_mcdonald_zh_2026) 中唯一直接源自英文金融文本分析基准 Loughran & McDonald (2011) 「When is a liability not a liability」的中文主译本。原始英文 L&M 2011 词典因基于 10-K 年报语料构建、剔除了通用情感词典 (如 Harvard-IV) 中大量在财务语境下并非负面的「假负面」词 (如 tax、cost、crude 等中性财务术语被通用词典误判为负面), 成为会计与金融文本分析领域引用最广的行业专属情感测度基准 (Loughran & McDonald, 2016)。本家族的中文译本延续该「行业专属而非通用情感词典」的构念定位, negative 类目收录 3,729 词, 显著大于 positive 类目的 1,295 词 — 这一不对称在 L&M 系列词典中是稳定特征, 反映负面财务/风险披露语言在词汇层面比正面语言更丰富、更具区分度的经验规律。三个 loughran_neg_count 列 (`_full`/`_ctx`/`_ss`) 是同一计数口径在三个不同扫描文本轨道上的并行实现, 三轨互为稳健性、不分主次、各自 just-identified, 严禁在同一 over-identified 设定 (如 Hansen J 检验) 中混用三轨列作为过度识别工具变量集合。

【方法学与计算】
producer 位于 pipeline/sentiment/tone_words.py, 属 stage 22 (`22_tone_words`) 词典情感打分模块。计算口径: 对每篇报道的三条扫描文本 (content_full/content_ctx/content_ss, 均由 stage 14 `ctx_materializer` 物化并已 prepend_title) 分词 (jieba==0.42.1 冻结版本以保证 golden 可复现), 逐词查表命中 loughran 词典的 negative 集合即计数加一, 汇总得到该篇该轨的 negative 词条出现总次数, 即 loughran_neg_count_{trk}。计数版本 (neg_count) 与语调版本 (loughran_tone/loughran_negonly_tone, 位于 stata_export.py 面板标签常量表) 是并列而非嵌套的两类衍生列: neg_count 是原始出现次数的加总 (未做否定翻转、未做正负相抵), 用于刻画负面词汇的绝对暴露强度; tone 类列则在此基础上应用否定翻转/程度副词/转折三条语言学规则并做正负相抵, 服务于净语调构念。词典消歧口径 (2026-06-24 用户决策「保留并两侧计数」): loughran 词典原始 positive∩negative 跨类重叠词 61 个, 经消歧 38 词已归单侧、余 23 词因语义不可约简而保留两侧计数, 即该 23 词命中时同时计入 pos 与 neg 两个计数通道, 对净语调构念呈中性拉力, 但对本家族的 neg_count 而言仍如实计入负面出现次数 (不做武断单侧取舍)。三轨扫描文本口径分别为: full=标题+正文全文; ctx=标题+目标银行实体上下文窗口 (无银行∧金科同句共现要求); ss=标题+银行∧金科词同句±N窗口 (N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认1)。ss 轨在文章不存在银行∧金科同句共现时执行回退语义 (镜像 ctx 轨回退口径): content_ss 退化为全文 body, 对应 ss_is_fallback 标记为 True, 分母 n_articles 与 ctx 轨共享同一套统计口径, 不因回退而产生额外分母漂移。留篇门控 (2026-06-29 起) 采用 full-only 口径: 一篇报道是否被认定为「一篇银行金科报道」仅取决于 llm_verified_full 是否为 True; ctx/ss 两轨的 loughran_neg_count 列是 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集, 但每轨内部的计数值仍按各自轨道的扫描文本独立计算, 不借用 full 轨的计数结果。

【文献定位】
L&M (2011, Journal of Finance) 是本家族方法学的直接源头: 该文系统论证了通用情感词典 (如 Harvard-IV Psychosocial Dictionary) 应用于 10-K 年报文本时存在系统性误判, 约有四分之三被通用词典标记为负面的词汇在财务披露语境下实际语义中性或正面, 由此构建了专门面向财务文本的正/负/不确定/诉讼/强弱模态等类目词典, 该词典及其后续更新版本已成为会计与金融领域文本分析的事实标准 (Loughran & McDonald, 2016, Journal of Accounting Research, 该文系统综述文本分析方法在会计金融领域的应用现状与方法学陷阱, 明确肯定行业专属词典相对通用情感词典的优势)。本项目使用的中文主译本 (loughran_mcdonald_zh_2026) 是对该英文词典的本土化翻译与适配, 与另一部本土原创的中文金融情感词典 Bian et al. (2021) 形成方法学对照: 前者路径是「英文行业词典翻译本土化」, 后者路径是「基于中文语料原创构建」, 两者在本项目六部词典矩阵中并列为固定 union 词典的组成部分, 服务于跨方法稳健性检验而非相互替代。计数版本 (neg_count) 与否定处理相关的方法学考量参见 Pröllochs, Feuerriegel & Neumann (2016, Decision Support Systems), 该文专门研究否定范围检测 (negation scope detection) 对情感分析结果的影响, 对应本项目 loughran_negonly_tone 消融臂 (仅应用否定翻转规则) 的方法学依据; neg_count 列本身不涉及否定翻转, 是三条语言学规则消融梯度的基线原始计数, 与 tone_words.py 中「三规则全 powerset 消融」体系 (raw/negonly/degonly/advonly 等 7 变体) 处于同一模块但服务不同构念层。Loughran & McDonald (2024, 期刊 Journal of Financial and Quantitative Analysis) 在 Loughran & McDonald 方法学传统下, 用词典化文本分析方法从 10-K 年报构建企业复杂度测度, 延续行业专属词典优于通用情感词典的构念定位。Chuang, He & Hu (2025, 期刊 Big Data and Cognitive Computing) 构建中文财经新闻情感标注语料并比较词典法与语言模型法在中文财经文本负面情感识别上的表现, 为本项目中文词典口径提供跨语言对照证据。

## VAR: loughran_neg_count_ctx

【变体差分】
本列在扫描文本轨道上取 ctx 轨: content_ctx = 标题 + 目标银行实体上下文窗口 (由 stage 14 `ctx_materializer` 物化), 不要求银行与金科词在同一句内共现, 窗口范围围绕已识别的目标银行实体展开, 相较 full 轨大幅缩短扫描文本长度、更聚焦于银行主体周边语境。留篇门控为 full-only (2026-06-29 起口径), 即该列的行宇宙由 llm_verified_full 决定是否留篇, ctx 轨本身不参与是否留篇的判定, 仅在留篇集合内部提供本轨的负面词汇计数作为 conditional-on-full 的稳健性测度; 换言之 ctx 轨是「行宇宙继承自 full 轨、但计数值独立于 full 轨重新扫描」的并行测度, 不存在借用 full 轨扫描结果再截断的捷径实现。ctx 轨与 full 轨、ss 轨三者互为稳健性、不分主次、各自 just-identified, 差异主要体现窗口收窄对负面词汇捕获密度的影响方向: 窗口越窄, 越可能捕获与目标银行直接相关的负面语言 (如监管处罚、坏账、诉讼等紧贴主体陈述), 但也可能因窗口外的负面陈述 (如宏观风险背景铺垫、行业整体负面评价) 被截断而使计数相对 full 轨偏低, 该方向性差异本身即为跨轨对照提供了实质信息, 而非单纯的噪声。三轨计数值理论上不应作为同一识别策略下的多重工具变量同时投入 Hansen J 过度识别检验, 使用者若需构造工具变量, 应在三轨中择一作为 just-identified 设定, 其余两轨留作独立的稳健性复核, 不得混合拼接为单一 over-identified 矩。词典查表逻辑 (loughran negative 集合命中计数、23 个跨类重叠词两侧计入) 与 full 轨完全一致, 差异仅在于喂入分词器的原始文本范围不同。

## VAR: loughran_neg_count_full

【变体差分】
本列在扫描文本轨道上取 full 轨: content_full = 标题 + 正文全文, 是三轨中信息覆盖最完整、词汇样本量最大的一轨, 亦是留篇门控 (llm_verified_full, 2026-06-29 起 full-only 口径) 的判定依据轨道, 决定整个 loughran_neg_count 家族三列共享的行宇宙范围: 一篇报道只要 llm_verified_full 为 True 即进入面板, 无论其 ctx/ss 轨是否触发回退语义。作为默认无窗口截断的基线扫描口径, full 轨的计数值通常是三轨中绝对值最大者 (扫描文本最长, 覆盖标题与正文全部段落), 在跨文章比较负面词汇绝对暴露强度时具有最完整的语料覆盖, 常被面板层聚合与标准化处理 (如按篇数、按词数或按句数归一化生成负面词密度指标) 用作基线参照, 也是词典消融梯度 (raw/negonly/degonly/advonly 等语言学规则 powerset) 与政治词权重敏感性检验等衍生测度默认锚定的扫描轨道。但 full 轨与 ctx/ss 两轨在方法学地位上仍是并排稳健性关系而非「主测度—附属测度」的从属关系: 三轨各自独立扫描、各自 just-identified, 差异反映扫描范围收窄程度不同, 而非精度高低之别。三轨严禁混入同一 over-identified Hansen J 设定, 亦不应在同一回归设定中同时以三轨计数作为并列解释变量, 应各自单独进入自身设定并互证结论稳健性。

## VAR: loughran_neg_count_ss

【变体差分】
本列在扫描文本轨道上取 ss 轨: content_ss = 标题 + 银行∧金科词同句 (±N 句窗口, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认1) 共现片段, 是三轨中判据最严格、扫描文本最短的一轨, 专门捕获银行主体与金融科技词汇在语义上紧密关联 (同句邻近) 语境下的负面词汇密度, 相较 ctx 轨的「实体窗口」判据更进一步收紧到「同句」判据, 理论上应最能反映「该篇报道确实在谈论银行与金科业务的交集」这一语境下的负面语言强度。当某篇报道不存在银行∧金科同句共现时, 该列执行回退语义 (镜像 ctx 轨回退口径, 二者共享同一套回退设计原则): content_ss 退化为全文 body, 对应 ss_is_fallback 标记为 True, 此时该篇的 loughran_neg_count_ss 实质上退化为对全文的计数, 与 loughran_neg_count_full 数值上可能完全重合, 分母 n_articles 的统计口径不因回退而产生额外漂移。使用者在解读该列时须结合 ss_is_fallback 标记区分「真正同句捕获」(判据最严格, 样本量较小) 与「回退全文捕获」(判据退化为无约束, 样本量与 full 轨一致) 两类观测, 不应将全部观测一视同仁地当作严格同句判据下的计数看待, 否则会低估该列在真实同句样本中的判据强度。ss 轨与 full/ctx 两轨同样互为稳健性、不分主次、各自 just-identified, 留篇门控仍为 full-only 口径 (llm_verified_full 判定), ss 轨行宇宙是 full 轨留篇集合的子集, 三轨严禁混入同一 over-identified Hansen J 设定。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Loughran, T., & McDonald, B. (2024). Measuring Firm Complexity. Journal of Financial and Quantitative Analysis. https://doi.org/10.1017/s0022109023000716
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
<!-- rendered-citations:end -->
