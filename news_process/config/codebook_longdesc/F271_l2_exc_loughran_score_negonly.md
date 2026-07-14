---
family_id: F271
columns:
- exc_loughran_score_negonly_ctx
- exc_loughran_score_negonly_full
- exc_loughran_score_negonly_ss
unit: 无量纲情感得分 (自归一化, 值域约 [-1, 1]; bank-year 层面为存活媒体子集上的算术均值)
formula: "exc_loughran_score_negonly_{trk} = mean_文章所属媒体的 _is_ceased_media 取 0 (即非疑似退出媒体) ( loughran_score_negonly_{trk} ); 其中文章级 loughran_score_negonly 由 _compute_sentiment_with_rules(apply_negation=True, apply_degree=False, apply_adversative=False) 产出, 是逐 token 状态机施加否定翻转规则 (关闭程度副词与转折) 后的自归一化幅度加权得分 self-normalized Σ(final)/Σ|final| ∈ [-1,1] (含 HowNet 六级权重体系与词典权重), 并非正负词计数比值; 计数比值口径对应的是同阶段另一列 msent_negonly = (neg-pos)/(pos+neg), 与本列口径不同不可混用"
producer: news_process/pipeline/panel/attention_media.py
upstream:
- 22_tone_words.parquet (loughran_score_negonly_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_export_main (attention_media 停刊代理检测 _is_ceased_media)
citations:
- doi: 10.1017/S0022109023000716
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2024
  title: "Measuring firm complexity"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2487-2514
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
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  issue: ""
  pages_or_artno: 67-75
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
new_dois: []
---

## CORE

【构念与来源】
本家族三列 exc_loughran_score_negonly_{full,ctx,ss} 是一族停刊稳健性 (publication-cessation robustness) 情感度量: 在 bank-year 层面, 对目标银行相关报道计算 Loughran-McDonald (2011) 情感词典中文主译版的语调得分, 但只保留否定翻转这一条语言学消融规则 (negonly 变体), 并且在聚合成银行-年均值时剔除疑似退出媒体覆盖的报纸来源。三个后缀对应三条文本轨道: full (标题 prepend 全文正文)、ctx (标题加实体上下文窗)、ss (标题加银行与金科同句共现窗)。这一族度量的构念定位不是新的情感信号, 而是主情感测度在两个正交扰动维度上的稳健性并排臂: 一是媒体存活性扰动 (exc_ 前缀, 剔除疑似停刊媒体后再聚合), 二是词典解析规则扰动 (negonly, 关闭程度副词与转折规则只留否定翻转)。它服务于系数稳定性检验, 回答"若主情感结果由存活媒体的幸存者偏差、或由某一条语言学解析规则驱动, 结论是否被推翻"。

数据来源上, 文章级底料 loughran_score_negonly_{trk} 由 stage 22 词典情感阶段 (22_tone_words.parquet) 产出。loughran 是本项目六部中文金融情感词典中的第六部, 是 Loughran & McDonald (2011) 发表于 The Journal of Finance 的英文金融词典的中文主译移植, 列前缀别名 loughran 由 tone_words.DICT_COLUMN_ALIAS 与 encode.DICT_NAMES 锁定权威。exc_ 前缀的聚合与停刊剔除逻辑落在 pipeline/panel/attention_media.py: 该模块先由 detect_defacto_cessation 检测隐性停刊, 得到文章级哨兵 _is_ceased_media, 再对存活子集 (df_alive = df[_is_ceased_media==0]) 按目标银行与年份分组取均值, 通过动态发现遍历 _SCORE_PATTERNS 匹配到 loughran_score_ 前缀的各消融变体列, 逐列生成 exc_ 前缀的稳健性副本。停刊在本实现中是"话题覆盖退出"(topic coverage exit) 的保守代理, 而非经证实的报纸停刊, 因此下游一律解读为"疑似退出覆盖媒体"口径的保守剔除, 不可在论文中表述为严格停刊。

【方法学与计算】
文章级 loughran_score_negonly 并非正负词计数比值, 而是逐 token 状态机在开启否定翻转、关闭程度副词与转折两条规则的设定下, 对每个匹配词施加否定窗口翻号后得到的幅度加权得分, 再自归一化为 Σ(final)/Σ|final|, 落在约 [-1, 1] 区间; 其中权重体系含 HowNet 六级强度与词典自带权重, 而非单纯计数。与其口径不同的是同阶段另一跨词典计数列 msent_negonly = (neg-pos)/(pos+neg), 二者分子分母定义、量纲均不同, 不可混淆或互代。negonly 是词典消融梯度全 powerset 物化的七个非-full 变体之一; 消融梯度对否定翻转、程度副词、转折三条语言学规则做全组合, negonly 单独打开否定翻转、关闭其余两条, 用以隔离否定处理对语调符号的边际贡献。各消融变体自归一化、非可加分解, 相互间高度共线, 因此按审计口径报相关性而非并入同一线性分解式。bank-year 聚合环节, exc_ 变体只在存活媒体子集上求算术均值, 与主聚合 (含全部媒体) 并排, 二者差分即媒体存活性对情感读数的敏感度。零文章的 bank-year 在 left-join 后保持 NaN (情感类按契约不零填, 与计数类 n_articles_exc 的 Σ over ∅ = 0 零填契约刻意区分)。

三轨、negonly 消融变体、以及"含全部媒体 vs 剔停刊"两个媒体口径, 都是各自 just-identified 并排的稳健性臂: 它们互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J 过度识别检验 (混轨/混消融变体/混媒体口径进同一 GMM 会伪造正交矩)。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科报道宇宙只由 full 轨的 LLM 判定决定, ctx 与 ss 降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 词典得分仍逐轨独立计算。ss 轨的回退语义镜像 ctx: 当某文章无银行与金科同句共现时, content_ss 退回全文正文, ss_is_fallback 记 True。

【文献定位】
词典法情感测度的方法论基石是 Loughran & McDonald (2011), 该文在 The Journal of Finance 上论证通用心理学词典 (如 Harvard-IV) 在金融文本上系统误判, 提出领域专用金融词表, 本项目 loughran 前缀正是其中文移植。Loughran & McDonald (2016) 在 Journal of Accounting Research 的综述进一步指出词典构造与解析规则选择 (含否定、加权) 会实质影响读数, 为本族的规则消融敏感性提供直接依据。Loughran & McDonald (2024) 在 Journal of Financial and Quantitative Analysis 延续这一测量学传统, 说明文本派生指标须对构造选择做透明的稳健性披露。否定处理这一具体环节, Pröllochs 等 (2016) 在 Decision Support Systems 上以新闻驱动交易为背景系统检验了否定范围检测对情感极性的影响, 正是 negonly 臂隔离否定规则的文献支撑。词典法与机器学习法的相对效度与互为稳健地位, Frankel 等 (2022) 在 Management Science 上做了系统比较, 支持本项目三方法 (LLM/词典/BERT) 各自并排、互不从属的稳健性设计; van Atteveldt 等 (2021) 则从人工标注、众包、词典、机器学习四路对比给出效度基准。中文金融语境的领域特异性由 Du 等 (2022) 在 Review of Finance 上确立, 提示英文词典移植须警惕跨语言语义漂移, 这也是本项目并列六部中文词典而非单一移植的动因。

## VAR: exc_loughran_score_negonly_ctx

【变体差分】
本列取 ctx 轨。ctx 轨的文本单元是标题 prepend 加实体上下文窗 content_ctx, 即围绕目标银行实体命中位置截取的上下文窗口 (而非全文), 意在把语调统计聚焦到与目标银行邻近的语句, 抑制长篇报道中与该银行无关段落的稀释。相对家族三轨, 本列与 full 列的差别纯在文本轨道: 词典 (loughran)、消融变体 (negonly, 仅否定翻转)、聚合口径 (剔疑似停刊媒体后 bank-year 均值) 三者与 full 列完全一致, 唯一变量是喂入词典打分的文本范围由全文正文收窄为实体上下文窗。在 full-only 留篇门控下, ctx 是 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集, per-track 得分照逐轨独立计算, 不回借 full 轨分母。本列与 full、ss 两列互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。在盘上 T=2 开发样本中, ctx 轨窗口较窄、共现事件稀疏, 可能出现较 full 更多的零方差或缺失格, 属预期退化, 生产 T=18 语料正常。停刊剔除维度与消融维度在本列上与其它两轨同口径叠加, 使其成为"实体窗文本 × 存活媒体 × 仅否定规则"三重扰动交点上的一枚稳健性读数。解释上, 本列与含全部媒体的 ctx 主聚合之差, 度量疑似退出覆盖媒体对实体窗口径语调读数的边际拉动; 而本列与 full 列之差, 度量把文本范围从全文收窄到实体上下文窗对语调的影响。两项差分均应作为并排稳健性证据陈述, 而不作为主结果替换, 也不与其它轨道或消融变体合成单一过度识别矩。

## VAR: exc_loughran_score_negonly_full

【变体差分】
本列取 full 轨, 是本家族在留篇门控意义上的基准轨。full 轨文本单元为 content_full, 即标题 prepend 后拼接全文正文, 是覆盖面最广的文本口径。相对 ctx 与 ss 两列, 本列的唯一差别在文本轨道: 词典选用 loughran 中文主译版、消融变体固定为 negonly (只施加否定翻转规则, 关闭程度副词与转折)、聚合口径固定为剔除疑似停刊媒体后的 bank-year 均值, 这三项与另外两轨逐字一致, 变量仅为喂词典的文本由实体窗/同句窗放宽到全文正文。按 full-only 门控 (2026-06-29), 一篇报道是否计入银行金科报道宇宙只看 full 轨 LLM 判定, 因此 full 轨的行宇宙是三轨中的母集, ctx/ss 为其子集; 但本列本身仍是纯词典打分的稳健性度量, 不承担门控职责。本列与 ctx、ss 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混入同一 over-identified Hansen J。因文本范围最宽, 本列相对 ctx/ss 通常方差更充分、缺失更少, 是三轨中最稳定的稳健性锚; 它与含全部媒体的主聚合列之差, 直接度量疑似停刊媒体退出对全文口径语调读数的边际影响。同样地, 本列与 ctx、ss 两列之差, 度量文本范围由全文收窄到实体窗或同句窗对语调读数的影响。须强调的是, negonly 只是词典消融梯度七个非-full 变体之一, 本列的否定翻转臂应与家族内程度副词、转折等其它规则臂并排解读, 用以证明主情感结论不被任一单条语言学解析规则驱动; 各消融臂高度共线, 审计口径报相关性而非并入同一线性分解, 更不得与三轨或两媒体口径合成单一 over-identified 检验。

## VAR: exc_loughran_score_negonly_ss

【变体差分】
本列取 ss 轨 (sentence-scope 同句共现窗)。ss 轨文本单元 content_ss 是标题 prepend 加银行与金科同句共现窗, 即只保留目标银行与金融科技词在同一句 (含 ±N 句半径, 默认半径 1) 共现的语句, 是三轨中语义约束最紧的口径, 意在把语调统计限定到银行与金科主题真正交汇的语境。相对 full 与 ctx, 本列唯一差别仍是文本轨道: loughran 词典、negonly 消融变体 (仅否定翻转)、剔停刊媒体后 bank-year 均值三项与另两轨一致。ss 轨的回退语义镜像 ctx: 当某文章不存在银行与金科同句共现时, content_ss 优雅退回全文正文并置 ss_is_fallback 为 True, 与 ctx 共享 n_articles 分母; 若金科 AC 自动机为 None 则全篇回退, 整轨优雅降级。在 full-only 门控下, ss 是 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集, per-track 得分逐轨独立计算不回借 full 分母。本列与 full、ctx 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。因约束最紧, 盘上 T=2 开发样本中本列零方差或缺失格最多属预期退化, 生产 T=18 正常。语义定位上, 本列是三轨中信噪最纯、但覆盖最稀疏的一枚稳健性读数: 当主结果在 full 轨稳健时, 若 ss 轨在有效格上给出同向系数, 即为构念真在银行与金科交汇语境内成立的强证据; 反之若 ss 轨大面积退化, 则应回退到 full 轨为主的解释而不强解读 ss 的零方差格。本列与含全部媒体的 ss 主聚合之差度量疑似停刊媒体退出对同句窗口径的边际影响, 属并排稳健性证据, 不与其它轨道或消融变体合成单一过度识别矩。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2024). Measuring firm complexity. Journal of Financial and Quantitative Analysis, 59(6), 2487-2514. https://doi.org/10.1017/S0022109023000716
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
