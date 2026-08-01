---
family_id: F288
novelty_exempt_rationale: "exc_ 前缀停刊剔除稳健性变体, 叠加于 you_2018 词典 negonly 消融变体之上, 属衍生/消融/排除双重技术变体家族, 测度定义依据母族 you_2018 词典文献 (You et al. 2018) 与消融梯度设计, 非独立新构念, 不需追新 2023+ 文献。"
columns:
- exc_you_2018_score_negonly_ctx
- exc_you_2018_score_negonly_full
- exc_you_2018_score_negonly_ss
unit: 无量纲情感得分 (自归一化, 值域约 [-1, 1]; bank-year 层面为存活媒体子集上的算术均值)
formula: "exc_you_2018_score_negonly_{trk} = mean_文章所属媒体的 _is_ceased_media 取 0 (即非疑似退出媒体) ( you_2018_score_negonly_{trk} ); 其中文章级 you_2018_score_negonly = Σ(final_score) / Σ|final_score|, final_score = base_score(词典权重) × negation_flip, 仅施加否定翻转 (negation-flip) 一条语言学规则, 关闭程度副词与转折规则; 此为幅度加权自归一化口径, 区别于同家族之外裸计数口径的 msent_negonly"
producer: news_process/pipeline/panel/attention_media.py
upstream:
- 22_tone_words.parquet (you_2018_score_negonly_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_export_main (attention_media 停刊代理检测 _is_ceased_media)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
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
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
- doi: "10.18653/v1/2025.emnlp-main.1088"
  type: "journal"
  authors: "Kim, J., Koo, S., & Lim, H."
  year: 2025
  title: "Semantic Inversion, Identical Replies: Revisiting Negation Blindness in Large Language Models"
  venue: "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing"
  pages_or_artno: "21445-21482"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 exc_you_2018_score_negonly_{full,ctx,ss} 是一族停刊稳健性 (publication-cessation robustness) 情感度量: 在 bank-year 层面, 对目标银行相关报道计算 You 等 (2018) 中文金融情感词典的语调得分, 但只保留否定翻转这一条语言学消融规则 (negonly 变体), 并且在聚合成银行-年均值时剔除疑似退出媒体覆盖的报纸来源。三个后缀对应三条文本轨道: full 轨为标题 prepend 后拼接全文正文, ctx 轨为标题加实体上下文窗, ss 轨为标题加银行与金科同句共现窗。这族度量的构念定位不是引入新的情感信号, 而是把主情感测度放到两个正交扰动维度上的稳健性并排臂: 一是媒体存活性扰动, 由 exc_ 前缀实现, 剔除疑似停刊媒体后再聚合; 二是词典解析规则扰动, 由 negonly 变体实现, 关闭程度副词与转折规则而只留否定翻转。它服务于系数稳定性检验, 回答一个具体的证伪问题: 若主情感结果实际由存活媒体的幸存者偏差驱动, 或由某一条语言学解析规则驱动, 主结论是否被推翻。

词典来源上, you_2018 是本项目六部中文金融情感词典之一, 出自 You 等 (2018) 发表于 The Review of Financial Studies 的媒体报道研究 "Who captures the power of the pen?"。该词典在本实现中激活其 Panel C (definite, 明确极性) 与 Panel D (ambiguous, 模糊极性) 两组词表, 由 tone_words 的加载器读入 tone_dicts.json 的 you_2018 键并对正负跨类重叠词按 Loughran-McDonald 惯例做净化 (you_2018 存在 5 个 positive∩negative 跨类重叠词, 含高文档命中率的"打破", 予以剔除或降权处理)。词典别名 you_2018 由 tone_words.DICT_COLUMN_ALIAS 与 encode.DICT_NAMES 逐字锁定为权威, 二者须 byte-for-byte 一致, 否则下游聚合循环找不到列而静默全 NaN。

文章级底料 you_2018_score_negonly_{trk} 由 stage 22 词典情感阶段 (22_tone_words.parquet) 产出; exc_ 前缀的聚合与停刊剔除逻辑落在 pipeline/panel/attention_media.py。该模块先由停刊检测得到文章级哨兵 _is_ceased_media, 再对存活子集 (剔除 _is_ceased_media==1 的报道) 按目标银行与年份分组取均值, 通过动态发现遍历得分列前缀匹配到 you_2018_score_ 的各消融变体, 逐列生成 exc_ 前缀的稳健性副本。须强调停刊在本实现中是"话题覆盖退出" (topic coverage exit) 的保守代理, 而非经证实的报纸停刊, 因此下游一律解读为"疑似退出覆盖媒体"口径的保守剔除, 论文中不可表述为严格停刊。零文章的 bank-year 在 left-join 后保持 NaN, 情感类按契约不做零填, 与计数类 n_articles_exc 的空集求和为 0 的零填契约刻意区分。

【方法学与计算】
文章级 you_2018_score_negonly 采用幅度加权的自归一化形式, 而非裸词计数差商: 逐词命中先取词典权重 base_score (因词而异, 非固定 ±1), 再乘以否定翻转系数 negation_flip 得到 final_score, 归一化得分 = Σ(final_score) / Σ|final_score|, 分子分母都是逐词权重加权和而非命中计数, 得分落在约 [-1, 1] 区间。须明确区分本项目中同时存在的另一族计数口径变体 msent_negonly, 其定义为 (neg−pos)/(pos+neg) 式的裸计数差商, 与本列所属的 score_ 幅度加权口径是两套不同公式、分属不同列族, 不可混淆或互相替代解读。negonly 是词典消融梯度全 powerset 物化的七个非-full 变体之一; 消融梯度对否定翻转、程度副词、转折三条语言学规则做全组合, negonly 单独打开否定翻转、关闭其余两条, 用以隔离否定处理对语调符号的边际贡献。实现上, 当程度副词规则关闭时否定命中仍以固定倍率 1.0 计入 (不放大), 转折规则关闭时也不放大, 但从句边界的 scoping 与全规则共享, 使从句边界在两种打分变体间抵消, 不污染 negonly 的纯否定语义。各消融变体自归一化、非可加分解, 相互间高度共线 (审计口径 corr 常在 0.99 量级), 因此按审计约定报相关性而非并入同一线性分解式。bank-year 聚合环节, exc_ 变体只在存活媒体子集上求算术均值, 与含全部媒体的主聚合并排, 二者差分即媒体存活性对情感读数的敏感度。

三轨、negonly 消融变体、以及"含全部媒体 vs 剔停刊"两个媒体口径, 都是各自 just-identified 并排的稳健性臂: 它们互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J 过度识别检验, 因为混轨、混消融变体或混媒体口径进同一 GMM 会伪造正交矩。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科报道宇宙只由 full 轨的 LLM 判定决定, ctx 与 ss 降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 词典得分仍逐轨独立计算, 不回借 full 轨分母。ss 轨的回退语义镜像 ctx: 当某文章无银行与金科同句共现时, content_ss 优雅退回全文正文, ss_is_fallback 记 True, 并与 ctx 共享 n_articles 分母; 若金科自动机为 None 则全篇回退, 整轨优雅降级。

【文献定位】
本族的词典与构念直接源自 You 等 (2018) 发表于 The Review of Financial Studies 的研究, 该文考察媒体报道对企业信息环境的影响, 并构建了用于中文财经文本的极性词表 (Panel C 明确词与 Panel D 模糊词), 是 you_2018 前缀的权威出处, 也为"媒体语调作为可度量信号"这一构念提供了顶刊层级的理论与测量基础。词典法情感测度对构造选择 (含否定、加权、程度处理) 的敏感性由词典法方法学文献反复强调, Barbaglia 等 (2025) 在 Economic Inquiry 上系统论证词典法在经济文本上的可行性与其对词表与规则设定的依赖, 为本族的规则消融敏感性提供直接依据。否定处理这一具体环节, Pröllochs 等 (2016) 在 Decision Support Systems 上以新闻驱动交易为背景系统检验了否定范围检测对情感极性的影响, 正是 negonly 臂隔离否定规则的文献支撑。词典法与机器学习法的相对效度与互为稳健地位, Frankel 等 (2022) 在 Management Science 上做了系统比较, 支持本项目三方法 (LLM/词典/BERT) 各自并排、互不从属的稳健性设计; van Atteveldt 等 (2021) 则从人工标注、众包、词典、机器学习四路对比给出效度基准。中文金融语境的领域特异性由 Du 等 (2022) 在 Review of Finance 上确立, 提示情感词典须警惕跨语言与跨领域语义漂移, 这也是本项目并列六部中文词典而非依赖单一词表的动因。 晚近文献进一步把否定处理单列为词典法内部可独立测量的模块。Naldi 与 Petroni (2023) 提出一套基于人工构造测试集的方法, 专门度量词典法情感工具对否定的检测与处理能力, 实证发现各工具在这一环节表现差异显著; 这是本族把否定翻转从三条语言学规则中单独抽出、构成 negonly 臂的最贴近方法学依据——否定处理确是词典法内部可被单独测量、亦可单独失效的模块。迁移边界在于: 原文是英文通用领域 (非金融) 词典工具的否定检测准确率评测, 而本族并不评测否定检测的准确率, 只把否定规则的开与关作为面板语调测度的一条并排稳健性臂, 语料亦为中文金融新闻。构念层面, Kim、Koo 与 Lim (2025) 提出并验证「查询否定盲区」: 当模型对肯定式查询的知识掌握准确时, 对语义被否定翻转的同一查询仍产出相同或近似回答, 其以 complexity 与 constrainedness 两准则设计的四项任务给出系统性证据, 表明否定在当代 NLP 系统中仍是一条独立且尚未解决的语义处理轴, 由此为把否定单列为可独立开关、独立报告的一条规则提供背景动机。此条须严格按降级口径引用: 该文为英文 NLP 基准评测, 对象是生成式大语言模型的知识问答与逻辑推理, 不涉及情感或语调测度, 不涉及词典与状态机, 亦不涉及中文否定词表; 本族的否定翻转是状态机内对否定辖域内命中词的确定性改号, 其「是否被正确处理」并不构成问题, negonly 臂检验的仅是该规则对结论的影响。故本文只作构念层背景, 词典法否定处理的直接证据仍以 Naldi 与 Petroni (2023) 与 Pröllochs 等 (2016) 为准。
## VAR: exc_you_2018_score_negonly_ctx

【变体差分】
本列取 ctx 轨。ctx 轨的文本单元是标题 prepend 加实体上下文窗 content_ctx, 即围绕目标银行实体命中位置截取的上下文窗口而非全文, 意在把语调统计聚焦到与目标银行邻近的语句, 抑制长篇报道中与该银行无关段落对情感读数的稀释。相对家族三轨, 本列与 full 列的差别纯在文本轨道: 词典 (you_2018)、消融变体 (negonly, 仅否定翻转)、聚合口径 (剔疑似停刊媒体后的 bank-year 均值) 三者与 full 列完全一致, 唯一变量是喂入词典打分的文本范围由全文正文收窄为实体上下文窗。在 full-only 留篇门控下, ctx 是 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集, per-track 得分照逐轨独立计算, 不回借 full 轨分母。本列与 full、ss 两列互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。在早期试跑盘上 T=2 样本中, ctx 轨窗口较窄、共现事件稀疏, 可能出现较 full 更多的零方差或缺失格, 属预期退化, 生产 T=19 语料正常。停刊剔除维度与消融维度在本列上与其它两轨同口径叠加, 使其成为"实体窗文本 × 存活媒体 × 仅否定规则"三重扰动交点上的一枚稳健性读数。解释上, 本列与含全部媒体的 ctx 主聚合之差, 度量疑似退出覆盖媒体对实体窗口径语调读数的边际拉动; 而本列与 full 列之差, 度量把文本范围从全文收窄到实体上下文窗对语调的影响。两项差分均应作为并排稳健性证据陈述, 而不作为主结果替换, 也不与其它轨道或消融变体合成单一过度识别矩。

## VAR: exc_you_2018_score_negonly_full

【变体差分】
本列取 full 轨, 是本家族在留篇门控意义上的基准轨。full 轨文本单元为 content_full, 即标题 prepend 后拼接全文正文, 是覆盖面最广的文本口径。相对 ctx 与 ss 两列, 本列的唯一差别在文本轨道: 词典选用 you_2018 中文金融情感词表、消融变体固定为 negonly (只施加否定翻转规则, 关闭程度副词与转折)、聚合口径固定为剔除疑似停刊媒体后的 bank-year 均值, 这三项与另外两轨逐字一致, 变量仅为喂词典的文本由实体窗或同句窗放宽到全文正文。按 full-only 门控 (2026-06-29), 一篇报道是否计入银行金科报道宇宙只看 full 轨 LLM 判定, 因此 full 轨的行宇宙是三轨中的母集, ctx/ss 为其子集; 但本列本身仍是纯词典打分的稳健性度量, 不承担门控职责。本列与 ctx、ss 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混入同一 over-identified Hansen J。因文本范围最宽, 本列相对 ctx/ss 通常方差更充分、缺失更少, 是三轨中最稳定的稳健性锚; 它与含全部媒体的主聚合列之差, 直接度量疑似停刊媒体退出对全文口径语调读数的边际影响。同样地, 本列与 ctx、ss 两列之差, 度量文本范围由全文收窄到实体窗或同句窗对语调读数的影响。须强调的是, negonly 只是词典消融梯度七个非-full 变体之一, 本列的否定翻转臂应与家族内程度副词、转折等其它规则臂并排解读, 用以证明主情感结论不被任一单条语言学解析规则驱动; 各消融臂高度共线, 审计口径报相关性而非并入同一线性分解, 更不得与三轨或两媒体口径合成单一 over-identified 检验。

## VAR: exc_you_2018_score_negonly_ss

【变体差分】
本列取 ss 轨 (sentence-scope 同句共现窗)。ss 轨文本单元 content_ss 是标题 prepend 加银行与金科同句共现窗, 即只保留目标银行与金融科技词在同一句 (含 ±N 句半径, 默认半径 1) 共现的语句, 是三轨中语义约束最紧的口径, 意在把语调统计限定到银行与金科主题真正交汇的语境。相对 full 与 ctx, 本列唯一差别仍是文本轨道: you_2018 词典、negonly 消融变体 (仅否定翻转)、剔停刊媒体后 bank-year 均值三项与另两轨一致。ss 轨的回退语义镜像 ctx: 当某文章不存在银行与金科同句共现时, content_ss 优雅退回全文正文并置 ss_is_fallback 为 True, 与 ctx 共享 n_articles 分母; 若金科自动机为 None 则全篇回退, 整轨优雅降级。在 full-only 门控下, ss 是 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集, per-track 得分逐轨独立计算不回借 full 分母。本列与 full、ctx 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。因约束最紧, 早期试跑盘上 T=2 样本中本列零方差或缺失格最多属预期退化, 生产 T=19 正常。语义定位上, 本列是三轨中信噪最纯、但覆盖最稀疏的一枚稳健性读数: 当主结果在 full 轨稳健时, 若 ss 轨在有效格上给出同向系数, 即为构念真在银行与金科交汇语境内成立的强证据; 反之若 ss 轨大面积退化, 则应回退到 full 轨为主的解释而不强解读 ss 的零方差格。本列与含全部媒体的 ss 主聚合之差度量疑似停刊媒体退出对同句窗口径的边际影响, 属并排稳健性证据, 不与其它轨道或消融变体合成单一过度识别矩。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Kim, J., Koo, S., & Lim, H. (2025). Semantic Inversion, Identical Replies: Revisiting Negation Blindness in Large Language Models. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 21445-21482. https://doi.org/10.18653/v1/2025.emnlp-main.1088
<!-- rendered-citations:end -->
