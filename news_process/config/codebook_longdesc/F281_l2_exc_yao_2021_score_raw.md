---
family_id: F281
columns:
- exc_yao_2021_score_raw_ctx
- exc_yao_2021_score_raw_full
- exc_yao_2021_score_raw_ss
unit: 情感倾向得分 (无量纲, 逐篇自归一化后取 bank-year 均值, 值域 [-1, 1])
formula: "exc_yao_2021_score_raw{track} = mean over {i in (target_bank, year) : _is_ceased_media_i == 0} of yao_2021_score_raw{track}_i; 其中逐篇 yao_2021_score_raw = Σ(final_score) / Σ|final_score| ∈ [-1, +1] (final_score 为姚加权(2021)词典逐词命中的带符号极性贡献, 正词为正、负词为负), 且**不施加任何语言学规则** (L0: 否定翻转 off / 程度加权 off / 转折增强 off); 在 L0 下 final_score 退化为逐词固有极性权重, 该式与 (Σpos-Σneg)/(Σpos+Σneg) 数学等价, 采用源码规范表述"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性 exc_* 动态发现循环); 文章级 yao_2021_score_raw{track} 由 news_process/pipeline/sentiment/tone_words.py::_analyze_single_article 在 _RULE_ABLATION_VARIANTS 循环内对 'raw' (L0 全关) 变体调用规则引擎产出
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_words_tone.parquet (yao_2021_score_raw_full / _ctx / _ss + _is_ceased_media)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1111/jofi.13498
  type: journal
  authors: Derrien, F., Krüger, P., Landier, A., & Yao, T.
  year: 2025
  title: "ESG news, future cash flows, and firm value"
  venue: Journal of Finance
  vol: 80
  issue: 6
  pages_or_artno: 3499-3554
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
本家族测度一条"停刊稳健性口径下"的词典情感得分: 以姚加权等 (2021) 金融领域中文情绪词典为词表, 在零语言学规则的基线 (raw, L0) 下逐篇算出情感极性得分, 再仅对未被判定为疑似退出覆盖 (停刊代理) 的媒体所发报道取 bank-year 均值。列名由三段语义正交拼成: exc 前缀 = 剔除疑似停刊媒体后的稳健性口径 (exclude ceased-media); yao_2021 = 词典身份; score_raw = 规则消融梯度的 L0 零规则基线变体。三段各自回答一个独立问题 —— 用哪批媒体 (exc)、用哪本词典 (yao_2021)、施加多少语言学规则 (raw), 三者不可混淆。

【构念与来源】数据来源有两层。文章级源列 yao_2021_score_raw{track} 由词典情感阶段 (stage 22, tone_words) 产出: 姚加权等 (2021) 词典按"年报"与"社交媒体"两个语境子表合并为 positive (约 3844 词) 与 negative (约 2074 词) 两张极性表, 跨表去重、不跨极性去重; 逐词命中按其极性取带符号贡献 final_score (正词为正、负词为负), 逐篇累加后按源码规范表述归一化: normalized_score = Σ(final_score) / Σ|final_score| ∈ [−1, 1] (与 (Σpos − Σneg) / (Σpos + Σneg) 数学等价, 后者是等值的白话拆分表述)。该归一化口径对政治词权重梯度 (du_2022 独有, 本词典不适用) 与 both_sided_words 等特殊处理是通用的: 无论词的极性判定是否经过特殊加权, 最终都汇入同一 final_score 再统一归一化, 不存在脱离该式的例外通道。所谓 raw (L0) 是规则消融梯度 (rule-ablation ladder, SSOT = tone_words._RULE_ABLATION_VARIANTS) 的最底一级: 否定翻转、程度六级加权、转折增强三条状态机规则全部关闭, 即把每个命中词按其固有极性等权累加, 不因"不"、"没有"等否定词翻号, 不因"大幅"、"略微"等程度副词缩放, 不因"但是"、"然而"等转折连词加权。全规则版本 (T,T,T) 对应家族外的 canonical yao_2021_score, raw 是它的零规则对照臂。

【构念与来源】exc 这一层是幸存者偏差 (survivorship bias) 的稳健性设计。地方报纸退出本地覆盖会让样本内的情感信号系统性地向存活媒体倾斜, 污染以媒体来源结构为工具的识别。产出侧因此先跑停刊代理检测 (detect_defacto_cessation): 用覆盖间隔阈值把"疑似已退出本地覆盖"的媒体标为 _is_ceased_media==1, 再在 bank-year 聚合时只对 _is_ceased_media==0 的存活媒体报道求 yao_2021_score_raw{track} 的均值, 得到本家族三列。与之并列的 canonical 口径 (全媒体) 是主测度, exc 口径是稳健性对照; 二者互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

【方法学与计算】逐篇 raw 得分自归一化 (分母 Σpos+Σneg 随命中词集变化), 因此跨规则级的相邻级差不是"某条规则的纯贡献", 只作 ablation 稳健性对照; 披露时须报四级相关系数与逐级变号占比, 论文口径表述为"主结论定性不变"。bank-year 聚合是对存活媒体子集的简单等权均值, 无篇幅加权。计数零填契约不适用于本族: exc_*tone/score 属情感类, 对零存活报道的 bank-year 保持 NaN (不零填), 与兄弟计数列 n_articles_exc (Σ over ∅ = 0, 零填并恢复整型) 的填充语义刻意不同。三轨 full/ctx/ss 逐轨独立计算, 缺轨优雅跳过 (graceful skip), 不借用其它轨的分母。留篇门控为 full-only (2026-06-29): 是否判为"一篇银行金科报道"只看 full 轨的 LLM 判定, ctx/ss 降为 conditional-on-full 的稳健性轨, 但本词典族各轨的极性得分仍逐轨照算。

【文献定位】词典法情感测度的方法论根基, Taboada 等 (2011) 系统论证了词典法 (lexicon-based) 相对机器学习的可复现、可移植与领域稳健优势, 并把否定处理与程度加强 (intensification) 明确为词典法的核心增强步骤 —— 这正是本族 raw 变体所刻意关闭的三条规则, 使 raw 成为衡量"规则增强究竟带来多少边际改变"的零点参照。Frankel 等 (2022, Management Science) 在披露文本上直接对撞机器学习与词典法, 发现两类方法在多数应用中高度相关, 支持把词典法作为可审计、低成本的主力测度之一。中文金融语境的词典构建, Du 等 (2022, Review of Finance) 强调语言与领域特异性 (language and domain specificity), 论证通用英文词典迁移到中文金融文本会系统失真, 这是本项目选用中文本土金融词典 (姚加权等 2021、Du 等 2022、卞等 2021 等) 并列互证的直接依据。Ma 等 (2025) 进一步构建面向中国国内投资者的细粒度中文情绪词典, Barbaglia 等 (2025) 给出经济文本的词典法情感范式, 两者共同表明词典法在近年仍是可信的基准测度。测度效度上, van Atteveldt 等 (2021) 用人工标注、众包、词典法与机器学习四路对撞, 提示词典法在极性判别上的系统性偏差需靠多词典/多方法互证来缓释 —— 本项目以六部词典 × 规则消融梯度 × exc 稳健性口径并列, 正是对该效度关切的工程回应。Derrien 等 (2025, Journal of Finance) 则从新闻信息如何经由未来现金流预期进入公司价值这一角度, 佐证媒体报道情感的经济含义, 支撑本族作为 bank-year 面板情感自变量的外部效度。

## VAR: exc_yao_2021_score_raw_ctx

【变体差分】
本列取 ctx 轨: 文本单元 = 标题 prepend + 实体上下文窗口 (content_ctx), 即围绕目标银行实体命中位置的窗口文本, 而非整篇正文。相对同族 full 列, ctx 把词典命中限定在银行实体邻近语域, 剔除与银行无关的段落噪声, 是三轨中"聚焦实体、牺牲上下文完整性"的一端。相对 ss 列, ctx 的窗口以实体窗口 (entity window) 为界, 不要求银行与金融科技在同一句共现, 语域比 ss 宽。本列同时继承 exc 口径 (仅存活媒体) 与 raw 口径 (L0 零规则): 因此它是"实体窗口文本 × 停刊稳健样本 × 无语言学规则"三重限定下的姚加权 (2021) 词典极性得分的 bank-year 均值。留篇门控为 full-only: 行宇宙由 full 轨留篇集决定, ctx 为 conditional-on-full 的稳健性/测度轨, 本列在该行宇宙上逐轨独立聚合, 不借 full 分母。三轨 full/ctx/ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 与 full/ss 混进同一 over-identified Hansen J。在开发期 T=2 的浅面板上, ctx 轨可能因存活媒体子集样本稀薄而出现零方差或 NaN, 属预期退化, 生产期 T=18 恢复正常; 分析时须与 full 轨相关系数、逐级变号占比一并披露, 口径表述"定性不变"。使用本列时应注意两层嵌套限定同时生效带来的样本收缩: exc 层先剔去疑似停刊媒体的报道, ctx 层再把剩余报道的文本窗口收窄到实体邻近语域, 两层筛选叠加后逐篇有效命中词数往往显著少于 full 轨, 使得原始极性得分对个别高权重词的敏感度上升, 这是词典法情感测度的共有特征而非本列独有缺陷。在稳健性附表中, 建议把本列与同族 exc_yao_2021_score_full/ss 及不做停刊剔除的 canonical yao_2021_score_ctx 并列汇报, 以同时展示"文本窗口收紧"与"样本存活性收紧"两条独立维度各自的边际影响, 且两条维度在识别策略上互不替代、不可合并为单一交互项写入同一过识别方程。

## VAR: exc_yao_2021_score_raw_full

【变体差分】
本列取 full 轨: 文本单元 = 标题 prepend + 全文正文 (content_full), 是三轨中信息最完整的一端, 也是留篇门控的判定轨 (full-only, 2026-06-29) —— 一篇报道是否计入"银行金融科技报道"的行宇宙, 只看 full 轨的 LLM 判定。相对 ctx/ss, full 不做实体窗口或同句共现裁剪, 覆盖全篇的词典命中, 因而分母 (命中词数) 最大、逐篇得分方差通常最稳, 是本族在实证中作为词典情感自变量时的首要轨。本列继承 exc 口径 (仅对 _is_ceased_media==0 的存活媒体聚合) 与 raw 口径 (L0 零规则: 否定翻转/程度加权/转折增强全关): 因此它衡量的是"全文文本 × 停刊稳健样本 × 无语言学规则"下姚加权 (2021) 词典极性得分的 bank-year 均值, 是同族 canonical (全媒体) 得分的幸存者偏差稳健性对照。与 canonical 全媒体口径互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。与规则消融梯度的其它级 (negonly/degonly/advonly/negdeg/negadv/degadv 及全规则 canonical) 亦互为稳健性: raw 是零点参照, 用于报四级相关与变号占比、佐证"规则增强不改变主结论定性方向"。本列不受计数零填契约影响, 对零存活报道的 bank-year 保持 NaN。作为三轨中的默认引用轨, 本列在实证使用中通常兼任两个角色: 一是词典法情感的幸存者偏差稳健性检验 (与全媒体 canonical 全文轨对照, 若系数符号与显著性一致, 支持结论不由停刊媒体的极端报道驱动); 二是规则消融梯度的零点参照 (与同族 negonly/degonly/advonly/negdeg/negadv/degadv/canonical 全规则版本逐级对照, 若相关系数随规则加码单调上升且逐级变号占比很低, 支持"语言学规则增强只改变量纲、不改变方向"的论证)。两种对照分属不同维度 (媒体存活性 vs. 语言学规则), 在回归设计上应分别以独立稳健性附表呈现, 不应合并进同一工具变量方程的过识别检验, 以免把两类互不隶属的稳健性来源误当作单一构念的多重测度。

## VAR: exc_yao_2021_score_raw_ss

【变体差分】
本列取 ss 轨: 文本单元 = 标题 prepend + 银行与金融科技同句共现窗口 (content_ss), 即只保留目标银行与金融科技词在同一句 (±N 句窗, 默认半径 1) 共现的最窄语域。ss 是三轨中限定最严的一端, 语义上镜像 ctx 但把"实体窗口"收紧为"银行∧金科严格同句共现"。回退语义 (镜像 ctx): 当某篇无银行∧金科同句共现时, content_ss 回退为全文 body, 且 ss_is_fallback 置 True 并共享 n_articles 分母; 若金融科技自动机 FINTECH_AC=None 则 *_is_fallback 全置 True 优雅降级。本列同时继承 exc 口径 (仅存活媒体) 与 raw 口径 (L0 零规则), 因此是"同句共现文本 × 停刊稳健样本 × 无语言学规则"下姚加权 (2021) 词典极性得分的 bank-year 均值。留篇门控为 full-only: ss 为 conditional-on-full 稳健性轨, 行宇宙 = full 留篇集子集, 逐轨独立聚合不借 full 分母。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁 ss 与 full/ctx 混进同一 over-identified Hansen J。在 T=2 浅面板上, ss 因同句共现命中稀薄叠加存活媒体子集, 极易呈零方差或 NaN, 属预期退化, 生产 T=18 恢复; 披露须与 full 轨相关及变号占比并列, 口径"定性不变"。三重限定 (同句共现 × 存活媒体 × 零规则) 叠加后, 本列是本家族中样本损耗最严重的一列: 先经金融科技自动机与银行实体位置的同句共现判定筛出窄语域文本, 再经停刊代理检测剔去疑似退出覆盖的媒体, 最后在零语言学规则下计算极性, 三层筛选逐层收缩有效样本量, 因此在生产期 T=18 的分析中也应预期其标准误系统性大于 full/ctx 两轨。尽管样本量最小, 该列的构念纯度最高: 它把"银行与金融科技话题在同一句被共同谈及"这一最严格的相关性判据与"排除退出覆盖媒体的偏差污染"两个独立稳健性维度叠加在一起, 适合在稳健性附表中作为"最保守口径下结论是否仍然成立"的压力测试, 而非作为主回归的默认自变量。若该列在 T=18 全量语料下方差仍偏低, 应优先怀疑同句共现判据本身对本行业文本过严, 而非误判为管道缺陷。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Derrien, F., Krüger, P., Landier, A., & Yao, T. (2025). ESG news, future cash flows, and firm value. Journal of Finance, 80(6), 3499-3554. https://doi.org/10.1111/jofi.13498
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
