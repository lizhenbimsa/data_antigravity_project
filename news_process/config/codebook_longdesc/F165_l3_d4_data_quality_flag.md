---
family_id: F165
columns:
- d4_data_quality_flag
unit: 分类字符串标志 (无量纲; 取值域 {ok, insufficient}, 刻意以可读字符串落盘不做 byte 编码)
formula: "d4_data_quality_flag = 'ok' if global_ctx_coverage(innovation_collab_mode_ctx) >= threshold_low else 'insufficient' (单一全局标量, 对整个 df 算一次 notna().mean() 后广播到面板每一行); threshold_low = baseline['mean'] - 2.0*baseline['std'] (从 v3_4_0_ctx_coverage_baseline.json 的 mean/std 派生, 非直接取 json 记录值), 基线文件缺失时回退固定 0.5"
producer: pipeline\panel\encode_collab.py::aggregate_d4_panel ; 取值映射与落盘 pipeline\panel\stata_export.py
upstream:
- "21_tone_llms.parquet (full/ctx 属性标签: substantiveness / locus / collab_mode)"
- 14_materialize_ctx.parquet (content_ctx — ctx 轨文本供属性标注)
- config/v3_4_0_ctx_coverage_baseline.json (ctx 覆盖率基线阈值)
citations:
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1080/19312458.2023.2285765
  type: journal
  authors: Birkenmaier, L., Lechner, C. M., & Wagner, C.
  year: 2024
  title: "The search for solid ground in text as data: A systematic review of validation practices and practical recommendations for validation"
  venue: Communication Methods and Measures
  vol: 18
  issue: 3
  pages_or_artno: 249-277
- doi: 10.1037/met0000412
  type: journal
  authors: van Oest, R., & Girard, J. M.
  year: 2021
  title: "Weighting schemes and incomplete data: A generalized Bayesian framework for chance-corrected interrater agreement"
  venue: Psychological Methods
- doi: 10.1093/pan/mps028
  type: journal
  authors: Grimmer, J., & Stewart, B. M.
  year: 2013
  title: "Text as data: The promise and pitfalls of automatic content analysis methods for political texts"
  venue: Political Analysis
  vol: 21
  issue: 3
  pages_or_artno: 267-297
- doi: 10.1080/19312450709336664
  type: journal
  authors: Hayes, A. F., & Krippendorff, K.
  year: 2007
  title: "Answering the call for a standard reliability measure for coding data"
  venue: Communication Methods and Measures
  vol: 1
  issue: 1
  pages_or_artno: 77-89
- doi: 10.1016/S0304-4076(01)00072-0
  type: journal
  authors: Croushore, D., & Stark, T.
  year: 2001
  title: "A real-time data set for macroeconomists"
  venue: Journal of Econometrics
  vol: 105
  issue: 1
  pages_or_artno: 111-130
- doi: "10.1177/08944393241286471"
  type: "journal"
  authors: "Törnberg, P."
  year: 2024
  title: "Large Language Models Outperform Expert Coders and Supervised Classifiers at Annotating Political Social Media Messages"
  venue: "Social Science Computer Review"
- doi: "10.63317/4oh42vhxfvci"
  title: "Large Language Models as Financial Data Annotators: A Study on Effectiveness and Efficiency"
  authors: "Aguda, T. D., Siddagangappa, S., Kochkina, E., Kaur, S., Wang, D., & Smiley, C."
  year: 2024
  venue: "Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)"
  type: "wp"
- doi: "10.3390/bdcc9020033"
  title: "Large Language Models as Kuwaiti Annotators"
  authors: "Alostad, H."
  year: 2025
  venue: "Big Data and Cognitive Computing"
  type: "journal"
new_dois:
  - "10.1177/08944393241286471"
  - "10.63317/4oh42vhxfvci"
  - "10.3390/bdcc9020033"
---

## CORE

【构念与来源】
d4_data_quality_flag 是一枚分类字符串"数据质量标志"，取值域刻意收敛为二元集合 ok 与 insufficient，用来对整个 bank-year 面板中所谓"D4 残差信号"列块的可信度做一次全局裁决并给出一句话结论。必须先钉死一条粒度事实以免误读：它并非逐行体检出来的、行与行可以取不同值的列，而是一枚单一全局标量——产出函数在整个 df 上把 ctx 覆盖率算一次（对 innovation_collab_mode_ctx 列取 notna().mean()），拿这一个数与阈值比出 ok 或 insufficient，再把这同一个字符串广播赋给面板的每一行。因此在任何一次落盘里，本列要么整列全 ok、要么整列全 insufficient，绝不会出现同一批次内部分行 ok 部分行 insufficient 的情形。它本身不是任何计量回归里的处理变量或被解释变量，而是伴随 D4 列块一同落盘的、面向整份数据集的元数据护栏：告诉下游 Stata 使用者，这一批银行-年度观测下、由大语言模型属性标注驱动的"言行不一/口径分歧"占比列，是否整体建立在足够的 ctx 标注覆盖之上，从而这份 D4 残差信号是否整体值得信任。D4 列块的构念根系在于"同一篇金融科技报道，用两套抽取口径（full 全文轨与 ctx 实体上下文轨）各自打出的三维属性标签是否发生分歧"。这三维属性分别是：实质性对象征性（substantiveness）、底层技术对应用场景（locus）、自主研发对外部协同（collab_mode）。当同一篇文章在 full 与 ctx 两个口径下被判为不同类别时，即记为一次"残差信号"；把这些残差信号在银行-年度层面聚合，就得到形如 dim 信号 frac 的分歧占比列，共 18 列（3 维度 × 3 信号 × 2 度量），另附 3 个 both_valid 覆盖计数列。这套残差信号的分母有一条硬约束：只数"两套口径都给出合法标签"的文章（both_valid），因为分歧只可能定义在这类文章上；若把全部物理文章数当分母，未标注文章会被静默当作"无分歧"，把分歧率系统性向下压偏。d4_data_quality_flag 正是为这条分母约束保驾：它在聚合层判断 ctx 轨的标签覆盖率是否达标，达标记 ok，不达标记 insufficient。产出函数为 pipeline\panel\encode_collab.py 内的 aggregate_d4_panel，字符串取值映射与最终 dta 落盘由 pipeline\panel\stata_export.py 承接。

【方法学与计算】
该标志的判定核心是 ctx 覆盖率与一条基线阈值的比较。覆盖率检查刻意选用 innovation_collab_mode_ctx 列作为 canonical 代理（源码 CR-6 注记）：在三个 ctx 维度中，collab_mode 是 v3.4.0 最新加入、Hassan 式实体上下文抽取波动最大者，被假定为覆盖最低维，取它作代理即取"最坏情形"守门，从严不从宽。阈值来源分两路，且须说清阈值是派生量而非直接取值：若磁盘上存在 v3_4_0_ctx_coverage_baseline.json，则读取其中记录的 mean 与 std 两个字段，按 threshold_low = mean 减去二倍 std 现算出一条低位阈值（日志亦以 baseline 减二倍 sigma 字样标注），即以历史基线的均值向下两个标准差处作为覆盖率的合格下界，而非把 json 里某个字段的值直接拿来当阈值；若基线文件缺失或路径为空，则优雅回退到固定 0.5 阈值并在日志注明 caveat，绝不静默失守。全局覆盖率不低于该阈值记 ok，低于阈值记 insufficient。与此正交，D4 残差列本身还叠了一道小样本门：某维 both_valid 文章数不足 5 篇时，对应分歧占比列强制置 NaN（valid 域门，非假零）；上游标签列缺失时回退 legacy 物理分母加 n_articles 小于 5 门。两道守卫方向一致——都是"证据太薄就明确记缺失或标不可信，而非把噪声伪装成信号"。工程细节上，这一列刻意以可读字符串原样落盘而不做 byte 编码——源码在 stata_export.py 里对它只声明了一个 D4_DATA_QUALITY_FLAG_VALUES 取值常量元组，并不对它施加任何 .map 类别编码，故也不存在针对本列的取值映射步骤——好让 Stata 使用者直接肉眼看到 ok 与 insufficient 取值。须澄清一处易混：邻近的 substantiveness/locus/collab_mode 类别列走的 _map_categorical_failloud fail-loud 守卫（对账 notna-before 与 isna-after、未登记类别直接 raise）服务的是那些列的 byte 0/1 编码，与本列无关；本列既不做 byte 编码也就无所谓该守卫。由于本列是整份数据集级的单一标量而非逐行取值，其 Stata 端典型用法 keep if d4_data_quality_flag == "ok" 的语义相应是一记"全局开关"：当本批数据被判 ok 时该句保留全部行、被判 insufficient 时该句剔除全部行，它并不能在同一批次内选择性地滤掉部分覆盖不可信的行（因为不存在行间差异）；使用者应把它理解为"这份 D4 面板整体是否可用"的门闩，而非行级筛子。还须澄清一条轨道口径：D4 残差只比 full 与 ctx 两套属性口径，ss 是纯情感轨不产属性标签，因此本族有意只走 full/ctx 两路、不产 ss 分支（源码 no-ss-track 注记）。也正因如此，d4_data_quality_flag 是一枚 track-agnostic 的元数据质量标志，而非 co-primary 双轨或三轨中的某条测度轨——它不进任何回归右手端，谈不上与其它轨"互为稳健性"，更不涉及把多轨混进同一 over-identified Hansen J 的禁忌；它的角色是在这些测度轨被消费之前，先把样本框划出可信子集。凡下游用 D4 列做的三轨或梯子稳健性检验，仍须遵守各口径各自 just-identified 并排、禁混同一 over-identified Hansen J 的项目铁律，而本标志恰是保证那些检验建立在干净样本上的前置闸。

【文献定位】
本列所服务的方法学问题——如何评估由大语言模型自动标注得到的类别数据的可信度、并在覆盖不足时明确标记而非掩盖——正处在近年"文本即数据"效度研究的核心。Carlson 与 Burbano (2026) 在管理学顶刊系统给出用大语言模型标注研究数据的基础准则与警示，强调标注覆盖率与一致性须被显式披露、低覆盖单元须被识别隔离，正是 d4_data_quality_flag 以 ok/insufficient 二分做覆盖守门的直接依据。Birkenmaier、Lechner 与 Wagner (2024) 对文本即数据的效度验证实践做系统综述，呼吁把"测度是否建立在充分证据之上"作为可复核的验证环节，本标志即把这一环节物化为可被 Stata 直接筛选的列。Grimmer 与 Stewart (2013) 早年即警示自动内容分析方法的前景与陷阱，指出无差别地信任机器标注会引入系统偏误，与本设计"证据太薄就记不可信"的保守立场一脉相承。van Oest 与 Girard (2021) 针对不完整数据下的机遇校正评分者一致性给出加权框架，其"缺失不可被当作一致"的思想与本族 both_valid 分母、小样本置 NaN 的分母约束同构。Hayes 与 Krippendorff (2007) 关于编码数据标准信度测度的经典工作，为把 full/ctx 两口径分歧解读为信度残差提供了度量学根基。Croushore 与 Stark (2001) 从宏观实时数据集角度提示"数据本身有质量维度、须随附 vintage 与可信度记录"，把数据质量标志作为分析对象的一等公民对待，与本列作为伴生质量护栏的定位互为呼应。Törnberg (2024, Social Science Computer Review) 实证比较大语言模型标注与专家人工编码及监督分类器在政治社交媒体文本上的表现与一致性，为本列以标注覆盖率作为数据质量裁决依据提供了当代经验证据。Aguda 等 (2024, LREC-COLING 2024) 比较三种大语言模型(GPT-4/PaLM 2/MPT Instruct)在金融文档关系抽取标注任务上相对专家与众包标注者的有效性与效率，并提出可信度指标筛出需专家复核的产出，为本列以标注覆盖率作为数据质量裁决依据提供了当代金融领域的经验证据。Alostad (2025, Big Data and Cognitive Computing) 评估11种大语言模型在科威特方言立场检测标注任务上的表现差异，揭示不同标注口径与模型间标签覆盖/一致性的系统性波动，呼应本列以ctx覆盖率作最坏情形代理来守门的保守设计思路。综合来看，d4_data_quality_flag 不是可有可无的旁注，而是把上述效度文献的规范建议落到工程实处的一枚硬护栏。

## VAR: d4_data_quality_flag

【变体差分】
本族仅此一列，它即家族 canonical，无三轨后缀、无模型后缀、无阈值梯子孪生列，因此差分语义须从"它相对整条 D4 列块的独特角色"来界定，而非相对某个兄弟变体。第一重差分：数据类型与落盘形态独特。它是全族唯一刻意以可读字符串（str）原样落盘、不做 byte 值标签编码的列，保留字面 ok 与 insufficient，目的是让 Stata 使用者无需查 value label 即可肉眼判读。此处须避免一处过陈述：同批设计里的 substantiveness/locus/collab_mode 类别列确实定义了 0/1 byte 编码与 value label 机制，但在当前 bank-year 面板落盘语境下这套编码并不触发——那些文章级 str 列在 encode 聚合阶段已被消费掉、面板里并不含它们，故 encode_categorical_columns 对本面板恒为 no-op、返回空 value_labels；因此说"同批类别列均走 byte 编码"仅在机制层为真、在本面板落盘时并不发生。相形之下本列是真正落到面板每一行的字符串。第二重差分：取值域二元且语义是"整份数据集级的元数据裁决"而非"逐行内容测度"。它取值只有 ok 与 insufficient 两种，分别对应全局 ctx 标签覆盖率达标与不达标；这不是对某篇报道内容属性的测量，更不是对每一行银行-年度分别体检，而是对整份 D4 残差面板可信度的一次全局裁决后广播到每一行，故落盘时整列同值。正因如此它不进回归右手端、不参与任何 Hansen J 或稳健性并排，是 track-agnostic 的样本框护栏；对应的 keep if d4_data_quality_flag == "ok" 是全有或全无的全局开关，而非行级筛子。第三重差分：判定用 canonical 代理列。覆盖率检查刻意只看 innovation_collab_mode_ctx 一列作最坏情形代理（CR-6），而非对三个 ctx 维度取平均——这使本标志在守门上偏保守，宁可对边界行记 insufficient。第四重差分：阈值来源双路可回退。优先读 v3_4_0_ctx_coverage_baseline.json 的自适应基线，缺失则回退固定 0.5 并注明 caveat，两路都 fail-loud、绝不静默失守。第五重差分：滞后与轨道维度上均为空——它无滞后版本、无 full/ctx/ss 分轨版本（D4 本族有意只走 full/ctx 两路且 ss 不产属性标签），因此不存在 _ctx/_ss/_lag1 之类的孪生列。理解本列的关键是记住它的裁决方向与粒度：insufficient 不是"某行数据错了"，而是"本批 D4 残差占比整体建立在过薄的 ctx 标注证据上，请整体审慎或剔除"——它是全局标量而非行级判定，与 both_valid 分母约束、小样本置 NaN 门共同构成同一道"证据不足即明记不可信"的保守防线。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Birkenmaier, L., Lechner, C. M., & Wagner, C. (2024). The search for solid ground in text as data: A systematic review of validation practices and practical recommendations for validation. Communication Methods and Measures, 18(3), 249-277. https://doi.org/10.1080/19312458.2023.2285765
van Oest, R., & Girard, J. M. (2021). Weighting schemes and incomplete data: A generalized Bayesian framework for chance-corrected interrater agreement. Psychological Methods. https://doi.org/10.1037/met0000412
Grimmer, J., & Stewart, B. M. (2013). Text as data: The promise and pitfalls of automatic content analysis methods for political texts. Political Analysis, 21(3), 267-297. https://doi.org/10.1093/pan/mps028
Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. Communication Methods and Measures, 1(1), 77-89. https://doi.org/10.1080/19312450709336664
Croushore, D., & Stark, T. (2001). A real-time data set for macroeconomists. Journal of Econometrics, 105(1), 111-130. https://doi.org/10.1016/S0304-4076(01)00072-0
Törnberg, P. (2024). Large Language Models Outperform Expert Coders and Supervised Classifiers at Annotating Political Social Media Messages. Social Science Computer Review. https://doi.org/10.1177/08944393241286471
Aguda, T. D., Siddagangappa, S., Kochkina, E., Kaur, S., Wang, D., & Smiley, C. (2024). Large Language Models as Financial Data Annotators: A Study on Effectiveness and Efficiency. Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024) [Working Paper]. https://doi.org/10.63317/4oh42vhxfvci
Alostad, H. (2025). Large Language Models as Kuwaiti Annotators. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9020033
<!-- rendered-citations:end -->
