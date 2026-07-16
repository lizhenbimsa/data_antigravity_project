---
family_id: F315
columns:
- frac_fls_ctx
- frac_fls_full
- frac_fls_ss
unit: "比例 (proportion, 无量纲, 值域 [0, 1]; FLS 前瞻句数占全部句数之比)"
formula: "文章级 frac_fls_{trk} = n_fls_sentences / n_sentences, trk ∈ {full, ctx, ss}; 句 s 判为 FLS 当且仅当 ∃w∈s: w∈D_future 且 ∃t∈s: t∈D_time (双门控; jieba 精确 token 匹配, ≥3 字标记加性 substring 补漏); 空文本或 n_sentences=0 → NaN; panel 列 = 文章级同名列按 bank-year 简单均值聚合 (dst=src 同名直聚合, 非 avg_ 前缀范式)"
producer: "news_process/pipeline/sentiment/forward_looking.py::compute_fls_for_text (句级双门判定); news_process/pipeline/sentiment/tone_words.py::_dual_analyze (stage 22 三轨逐篇调用); news_process/pipeline/panel/encode_collab.py::apply_v3_5_2 (bank-year 同名 mean 聚合)"
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨物化文本 + ss_is_fallback)
- 22_tone_words.parquet (文章级 frac_fls_{full,ctx,ss})
- config/tone_dicts.json::forward_looking_statements (双门控词表 SSOT, v0.1.6 future 68 + time 53)
citations:
- doi: 10.3390/jrfm19060391
  type: journal
  authors: "Wu, Y."
  year: 2026
  title: "Forward-looking disclosure with and without time frames: Determinants, market responses, and implications"
  venue: "Journal of Risk and Financial Management"
  vol: 19
  issue: 6
  pages_or_artno: "Article 391"
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: 10.1142/S1094406025500064
  type: journal
  authors: "Liu, T., Zhang, J., & Wu, J."
  year: 2026
  title: "Forward-looking statements in annual reports and firms' financing constraints: A machine learning approach"
  venue: "The International Journal of Accounting"
  vol: 61
  issue: 1
  pages_or_artno: "Article 2550006"
- doi: 10.1016/j.irfa.2024.103484
  type: journal
  authors: "Abedin, M. Z., Goldstein, M. A., Huang, Q., & Zeng, H."
  year: 2024
  title: "Forward-looking disclosure effects on stock liquidity in China: Evidence from MD&A text analysis"
  venue: "International Review of Financial Analysis"
  vol: 95
  pages_or_artno: "Article 103484"
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2020
  title: "Textual analysis in finance"
  venue: "Annual Review of Financial Economics"
  vol: 12
  issue: 1
  pages_or_artno: "357-375"
- doi: 10.1257/jel.20181020
  type: journal
  authors: "Gentzkow, M., Kelly, B., & Taddy, M."
  year: 2019
  title: "Text as data"
  venue: "Journal of Economic Literature"
  vol: 57
  issue: 3
  pages_or_artno: "535-574"
- doi: 10.1016/j.jacceco.2017.11.008
  type: journal
  authors: "Bozanic, Z., Roulstone, D. T., & Van Buskirk, A."
  year: 2018
  title: "Management earnings forecasts and other forward-looking statements"
  venue: "Journal of Accounting and Economics"
  vol: 65
  issue: 1
  pages_or_artno: "1-20"
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: "Journal of Accounting Research"
  vol: 54
  issue: 4
  pages_or_artno: "1187-1230"
- doi: 10.1287/mnsc.2014.1921
  type: journal
  authors: "Muslu, V., Radhakrishnan, S., Subramanyam, K. R., & Lim, D."
  year: 2015
  title: "Forward-looking MD&A disclosures and the information environment"
  venue: "Management Science"
  vol: 61
  issue: 5
  pages_or_artno: "931-948"
- doi: 10.1111/j.1475-679X.2010.00396.x
  type: journal
  authors: "Brown, S. V., & Tucker, J. W."
  year: 2011
  title: "Large-sample evidence on firms' year-over-year MD&A modifications"
  venue: "Journal of Accounting Research"
  vol: 49
  issue: 2
  pages_or_artno: "309-346"
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: "The Journal of Finance"
  vol: 66
  issue: 1
  pages_or_artno: "35-65"
- doi: 10.1111/j.1475-679X.2010.00382.x
  type: journal
  authors: "Li, F."
  year: 2010
  title: "The information content of forward-looking statements in corporate filings: A naïve Bayesian machine learning approach"
  venue: "Journal of Accounting Research"
  vol: 48
  issue: 5
  pages_or_artno: "1049-1102"
- doi: 10.3115/1119250.1119269
  type: journal
  authors: "Sproat, R., & Emerson, T."
  year: 2003
  title: "The first international Chinese word segmentation bakeoff"
  venue: "Proceedings of the Second SIGHAN Workshop on Chinese Language Processing"
  pages_or_artno: "133-143"
- doi: "10.1002/isaf.1549"
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  venue: "Intelligent Systems in Accounting, Finance and Management"
  type: "journal"
- doi: "10.1111/jbfa.70010"
  title: "Forward-Looking Statements and Investor Trading"
  authors: "Chen, J.-C., Jain, P. K., & Silveri, S. (Dino)"
  year: 2025
  venue: "Journal of Business Finance & Accounting"
  type: "journal"
- doi: "10.1016/j.heliyon.2023.e15329"
  title: "Forward looking statement, investor sentiment and stock liquidity"
  authors: "Li, C., Yan, Y., Liu, X., Wan, S., Xu, Y., & Lin, H."
  year: 2023
  venue: "Heliyon"
  type: "journal"
new_dois:
  - "10.3390/bdcc9100263"
  - "10.1002/isaf.1549"
  - "10.1111/jbfa.70010"
  - "10.1016/j.heliyon.2023.e15329"
---

## CORE

【构念与来源】
本家族测量的构念是媒体报道文本的前瞻取向强度 (forward-looking statement intensity, 下称 FLS 强度), 即一篇关于目标银行与金融科技的新闻报道中, 前瞻性陈述句占全部句子的比例。前瞻性陈述指那些谈论未来计划、预期、目标、展望而非既成事实的句子, 例如宣布某银行计划未来三年将数字化投入翻番, 或预计明年上线新的线上信贷平台。这一构念源自会计与金融文本分析文献中的经典命题: 披露文本的时间取向本身携带独立于语气正负的信息含量。Li (2010) 用朴素贝叶斯机器学习方法在公司年报中识别前瞻性句子, 发现前瞻陈述的语气对公司未来盈利具有预测力且市场对其反应不足, 奠定了以句子为单位、以比例为汇总统计量的 FLS 测度范式, 本家族的分子分母结构正是该范式的同型移植。Bozanic, Roulstone 与 Van Buskirk (2018) 进一步把管理层盈余预测放回更广的前瞻陈述语境, 系统刻画了前瞻句的数量属性与时间跨度属性如何影响其信息含量, 为本家族坚持句级判定而非全文词频的设计提供了直接依据。Muslu, Radhakrishnan, Subramanyam 与 Lim (2015) 则证明基于关键词规则识别的 MD&A 前瞻披露能够改善公司信息环境, 说明词表规则法与机器学习法在该构念上是可互换的操作化路径, 词表法凭借完全可复现与零推断成本的优势更适合本项目 约 1,819 万篇量级的生产语料。与上述文献以公司自愿披露为对象不同, 本家族把 FLS 测度移植到第三方媒体报道: 报道银行金融科技活动时前瞻句占比高, 意味着媒体叙事聚焦于该银行的战略布局与未来承诺而非已落地的经营结果, 这一区分对识别银行金融科技转型的事前预期渠道与事后确认渠道至关重要。数据来源上, 本家族消费 stage 14 物化的三轨文本 (content_full 与 content_ctx 与 content_ss), 在 stage 22 词典情感阶段逐篇计算, 最终经 panel 构建步骤聚合为银行-年面板列, 全程确定性纯 CPU 计算, 不涉及任何 LLM 或嵌入调用, 零 API 成本。

【方法学与计算】
判定规则采用句子级双门控: 一个句子被判为 FLS, 当且仅当该句同时含有至少一个未来动作词 (D_future, 如将、拟、预计、计划、有望、力争、致力于、展望) 与至少一个未来时间标记 (D_time, 如未来、明年、下季、三年内、中长期、下一阶段)。双门结构对中文语料有特殊的语言学必要性: 中文动词没有屈折形态的时态标记, 英文文献可以借助 will 与 shall 等助动词或动词将来时形态识别前瞻句, 中文的未来指向只能通过词汇手段表达, 而单个未来动作词 (如计划、预计) 在中文里同时承担名词与动词功能且常出现在回顾性语境 (如报道去年制定的计划的执行情况), 仅凭单门误报率高; 要求未来时间标记同句共现相当于给动作词加上一个显性的时间锚, 把判定收敛到真正谈论未来的句子上。这是把 Li (2010) 的英文 FLS 判定思想向中文语法特点做的适配性重构, 而非词表的简单翻译。双门控词表当前版本 v0.1.6 含 future 词 68 个加 time 词 53 个共 121 词, 已从模块内联 frozenset 外置到 config/tone_dicts.json 顶层条目 forward_looking_statements 作为单一事实源, 模块 import 时一次性加载为模块级 frozenset; 文件或条目缺失时静默降级为空集, 此时双门永不触发, 非空文本的 frac_fls 恒为零、空文本为缺失值, 该降级仅为防御性设计, 因 tone_dicts.json 是项目核心必备文件。词表准入受 G-A2.1 门控约束: 词表规模不低于一百词, 且在五百句人工标注上精确率不低于零点八; v0.1.5 到 v0.1.6 的修订删除了十个非未来指向词 (进行体动词、裸时距、当期词), 变更披露见词表条目的元数据, 词表成员由专项测试锁定。计算流程为: 先用中文分句器 cn_split_sentence 把文本切成句子序列, 分母 n_sentences 即句子总数; 对每句用 jieba 分词得到 token 集合, 与两个词表 frozenset 求交判定两门; 分子 n_fls_sentences 为双门同时命中的句数; 比值即 frac_fls, 值域零到一; 空文本或分句结果为零句时返回缺失值而非零, 以区分无内容与有内容但无前瞻两种状态。匹配层有两处经审计加固的细节。其一是 P-038 修复: 早期实现用子串匹配, 单字词如望、将会误命中希望、绝望、瞭望、将其等非前瞻语境, 修复后改为 jieba 精确 token 匹配, 依赖 jieba 分词器单例缓存, 每句约零点一毫秒。其二是长标记补漏: jieba 默认词典常把多字标记切碎, 例如下一财年被切为三段、中长期目标被切为两段, 成分若不在词表则整词漏判, 因此对长度不低于三字的词表词追加原句字面子串匹配作为补充; 该补充是纯加性的, 只会把门控置真不会取消任何 token 命中, 而一字与二字短词仍仅走精确分词匹配以保持 P-038 建立的精度, 句内空格统一剥除以兼容含空格的时间表达。分词依赖 jieba 0.42.1 冻结锚点, 保证跨机器逐位可复现; Sproat 与 Emerson (2003) 组织的首届中文分词评测早已表明分词方案差异会系统性影响下游词元匹配, 冻结分词器版本正是对这一测量学风险的工程回应。三轨调用发生在 stage 22 的逐篇分析函数内, 对 content_full 与 content_ctx 与 content_ss 各调用一次同一个 track-agnostic 的计算函数, 轨道差异完全由输入文本驱动, 判定逻辑三轨逐字节一致。面板聚合在 panel 构建的 encode_collab 步骤完成: 按银行-年分组对文章级列取简单均值, 输出列与文章级源列同名 (dst 等于 src, 无前缀改写, 刻意区别于 avg_ 前缀范式), 与下游 Stata 模板和 codebook 的既有列名契约一致; 聚合的文章宇宙遵循全流水线的 full-only 留篇门控口径 (2026-06-29): 一篇文章是否计入银行金融科技报道宇宙只由 full 轨的 LLM 验证结论决定, ctx 与 ss 轨列在该宇宙上条件计算。计算的确定性保障有三层: 词表层由外置单一事实源与成员锁定测试保证任何修订都显式留痕; 分词层由 jieba 0.42.1 版本冻结保证同一文本在任何机器任何时点切出同一 token 序列; 数值层分子分母均为整数计数, 比值无浮点累加次序问题, 因此本家族不在 BLAS 浮点漂移的非确定列清单内, golden 对照可做逐位复现。缺失值语义需要特别说明: 空文本与零句文本返回缺失值而非零, 这一选择把没有可判定内容与有内容但无前瞻严格区分开, 面板均值聚合时缺失文章自动退出分子分母, 不会把无内容文章稀释为伪低前瞻。

【文献定位】
本家族在方法谱系上位于词典规则法与机器学习法两条 FLS 操作化路径的词典端。Li (2010) 是机器学习端的奠基, Muslu 等 (2015) 是关键词规则端的代表, 二者对同一构念给出了收敛的实证结论, 支持路径选择主要是成本与可复现性的权衡而非效度分歧。Loughran 与 McDonald (2011) 确立的领域专用词典原则 (通用词典移植到财务语境会产生系统性误分类) 是本家族自建中文双门控词表而非翻译英文 FLS 词表的直接理由; 其后续综述 Loughran 与 McDonald (2016) 与 Loughran 与 McDonald (2020) 反复强调词典法的透明性与可审计性优势, 并把测量误差的来源分解为词表覆盖与语境歧义两类, 本家族的双门设计与长标记补漏分别针对这两类误差。Gentzkow, Kelly 与 Taddy (2019) 的文本即数据框架把词典测度视为高维文本到低维统计量的映射, 提醒任何单一映射都应配备并排的替代规格, 这正是本项目为 FLS 配置单门稳健臂与三轨并排的方法论出处。近期文献把 FLS 测度推进到中文语料与更细的属性维度: Abedin, Goldstein, Huang 与 Zeng (2024) 用中国上市公司 MD&A 文本证明前瞻披露强度影响股票流动性且其效应被可读性与语气调节, 为中文语境下 FLS 构念的市场后果提供了直接实证; Liu, Zhang 与 Wu (2026) 用机器学习方法测度中国年报前瞻陈述并发现其缓解融资约束, 说明中文 FLS 强度与实体经济结果相连; Wu (2026) 区分带时间框架与不带时间框架的前瞻披露并发现二者的决定因素与市场反应系统不同, 该区分与本家族双门对单门的设计几乎一一对应: 双门 canonical 恰好捕捉带时间框架的前瞻句, 单门臂则纳入无时间框架的弱前瞻句。Brown 与 Tucker (2011) 对 MD&A 逐年修改幅度的大样本测度则从披露动态角度补充了背景: 前瞻文本是披露中信息增量最集中也最易模板化的部分, 这提示 FLS 比例应与本管线的套话比率、陈旧度等文本再利用测度联合解读而非孤立使用。Todd, Bowden 与 Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融文本情感分析文献并展望未来方向, 呼应本家族把词典规则法前瞻句测度置于文本即数据方法谱系中的定位。Chen, Jain 与 Silveri (2025, Journal of Business Finance & Accounting) 用10-K/10-Q文本分析发现前瞻性陈述与投资者交易成本降低相关,主要通过降低做市商库存成本实现。Li, Yan, Liu, Wan, Xu 与 Lin (2023, Heliyon) 以中国A股上市公司为样本发现前瞻性信息披露水平越高股票流动性越好,投资者情绪是其中的传导机制。

【识别策略定位】
在本项目多论文组合的识别框架中, frac_fls 家族不承担任何论文的主处理变量 (treatment headline) 角色, 而是三重身份的辅助测度。第一重是叙事属性控制变量: P1 至 P5 主线的处理变量多为 full 轨情感与属性变量, 媒体对银行金融科技的报道语气与报道的时间取向天然相关 (战略宣示类报道往往同时更正面也更前瞻), 在回归中加入 frac_fls 可以把语气效应从前瞻叙事效应中剥离, 缓解把预期驱动误认为情感驱动的混淆。第二重是机制与异质性切割变量: 按银行-年的 FLS 强度高低分组, 可以检验金融科技报道效应是经由事前预期渠道 (前瞻叙事改变投资者与同业对该银行转型的预期) 还是事后确认渠道 (落地成果报道改变基本面评估) 传导, Muslu 等 (2015) 关于前瞻披露改善信息环境的结论为预期渠道提供了先验。第三重是安慰剂与效度佐证: 前瞻句占比是纯语言形式测度, 不依赖 LLM 判断, 其与 LLM 情感测度的低相关是两族测度各自构念效度的旁证。此外在事件研究与动态设定中, 银行-年 FLS 均值的时间路径本身有解释价值: 若某银行的金融科技报道在处理事件前以前瞻叙事为主、事件后转向落地叙事, 该转折点为平行趋势诊断与预期效应 (anticipation effect) 的排查提供了文本侧证据, Bozanic 等 (2018) 关于前瞻陈述时间跨度属性的分析正是这类解读的理论支点。因为分子分母都来自确定性词表匹配, 该家族列在工具变量设定中也天然满足可复现性要求, 但项目不将其用作工具, 因为媒体前瞻叙事与银行不可观测的战略冲击存在明显的排他性约束疑虑。使用时须遵守本项目铁律: 三轨 full 与 ctx 与 ss 各自 just-identified 并排、互为稳健性不分主次, 禁止把多轨同时塞进同一个 over-identified 的 Hansen J 检验; 双门 canonical 与单门 fonly 稳健臂同理二臂并排, 禁混同一 Hansen J。

【与相邻测度的构念区分】
本家族与管线内多个词典族测度共享 stage 22 的计算基础设施, 但构念边界清晰。与六部情感词典的语气分值 (如 du_2022 族) 的区别是维度正交: 语气测量正负极性, FLS 测量时间取向, 一篇报道可以同时高度正面且完全回顾性, 也可以负面而前瞻 (如预警某银行未来风险)。与 LM 非情感六子集 (不确定、诉讼、约束、强弱情态、复杂度) 的区别最需要澄清: 强情态词族 (如必将、承诺) 与弱情态词族 (如可能、或许) 在英文文献中常被当作前瞻性的代理, 但情态测量的是承诺强度与确定性程度, 不要求未来时间指向; 本家族双门控显式要求未来动作词与未来时间标记同句共现, 排除了对当期或过去事项的情态表达, 构念上更窄也更纯。与 clarity 三轨 (明确词对模糊词) 的区别是清晰度测量表述的可验证性而非时间取向。与套话比率 (boilerplate) 的关系是潜在负相关的两个独立构念: 模板化文本往往缺少具体前瞻承诺, 但二者的测量原语完全不同 (n-gram 重复对句级词表门控)。与数字强度、罕见词比率等形式测度的区别同理。家族内部, frac_fls 是双门 canonical, 单门臂 frac_fls_fonly (仅要求 future 词, 不要求 time 词) 属于另一个独立家族, 逐句蕴含关系保证单门是双门的超集, 单门减双门恰为 Wu (2026) 意义上无时间框架的弱前瞻句占比; 该差值本身不物化为列, 是刻意的设计克制, 防止派生列组合爆炸。所有这些相邻测度族之间同样只做并排稳健性对照, 不做跨族联合过度识别。

【已知局限与稳健性梯子】
第一, 领域迁移局限: 奠基文献 Li (2010) 与 Bozanic 等 (2018) 的对象是公司自愿披露 (年报与盈余预测), 而本家族的对象是第三方媒体报道, 媒体转述管理层前瞻表态时可能改写时间表达 (把三年内改写为中期), 双门中的时间门对此类改写敏感; 缓解手段是时间词表刻意收录了未来、中长期、下一阶段等媒体惯用的模糊时间标记。第二, 词表法固有的召回率局限: 双门控是精度优先的研究者选择, 500 句人工标注精确率不低于零点八的准入门控只约束精度不约束召回, 隐含前瞻句 (无显性标记的语用前瞻, 如反问句式的展望) 会被漏判; 对应的稳健性梯子是单门 fonly 臂, 其放宽时间门后逐句蕴含地覆盖更多弱前瞻句, 主结论若在双门与单门两臂间稳定, 则不被门控松紧这一自由度驱动, 二臂互为稳健性不分主次、各自 just-identified 并排、禁混同一 over-identified Hansen J。第三, 分词依赖: jieba 对新出现的金融科技复合词的切分不可预期, 长标记子串补漏只覆盖词表内的长词, 不能挽救词表外的表达; jieba 版本已冻结在 0.42.1, 保证该误差在时间维度上恒定, 不会因依赖升级产生跨年份的系统漂移。第四, 分母敏感性: 短文本句数少, 单句判定翻转即引起比例大幅跳动, ctx 与 ss 轨因文本更短对此更敏感; 面板层按银行-年取均值天然平滑了这一噪声, 且三轨并排本身构成对分母口径的稳健性检验。第五, 聚合口径: 面板列是文章级比例的简单均值, 未按文章长度加权, 长短文章在银行-年层面等权; 这与本管线全部词典族 frac 列的聚合口径一致, 是刻意的族内一致性选择而非疏漏。第六, 静默降级风险: 词表加载失败降级为空集时 frac_fls 恒零而非报错, 依赖 tone_dicts.json 作为核心必备文件的项目级保障与词表成员锁定测试兜底。整个家族无阈值、无权重、无滞后参数, 研究者自由度集中在词表成员与门控结构两处, 前者由外置单一事实源加成员锁定测试实现全量可审计, 后者由双门对单门的二臂并排设计吸收; 这使得本家族的规格曲线维度天然有限, 报告稳健性时只需覆盖三轨乘二臂共六个并排规格即可穷尽全部合理的操作化空间, 无需再做额外的参数扫描。

## VAR: frac_fls_full

【变体差分】
本列是家族三轨中的 full 轨, 亦是唯一 core 列: FLS 双门 canonical 测度的主轨落点。文本口径为 content_full, 即 stage 14 物化的标题前置加全文正文 (prepend_title 机制, 标题作为文本第零句参与分句与门控扫描, 原始内容列不动), 不做任何实体窗口裁剪, 因此分母句数在三轨中最大, 单句判定翻转对比例的扰动最小, 是统计上最稳定的一轨。选择 full 轨作为 core 的理由与全管线的口径决策同构: 自 2026-06-29 起留篇门控为 full-only, 一篇文章是否计入银行金融科技报道宇宙只由 full 轨的 LLM 验证结论决定, 各论文主轨处理变量也已切换为 full 轨, 因此与主处理变量同轨的 full 轨 FLS 是回归设定中语义最对齐的叙事属性控制, 把它并入含 llm_vote_tone_full 等主变量的方程时不引入跨轨口径错配。构念上本列回答的问题是: 就这篇报道的完整文本而言, 有多大比例的句子在谈论目标银行的未来而非现在与过去。相对家族内另两列的精确差分为: 其一, 输入文本无窗口约束, 覆盖报道中与目标银行不直接相邻的背景段落与行业展望段落, 因此本列度量的是整篇报道的前瞻氛围, 而 ctx 与 ss 轨度量的是银行实体邻域的前瞻密度, 三者的构念重心不同而互补; 其二, 本列不存在回退语义, content_full 对每篇留存文章恒有定义, 缺失值只来自空文本或零句这一数据边界, 而 ss 轨的取值可能来自回退后的全文; 其三, 本列是双门 canonical, 与单门稳健臂 frac_fls_fonly_full 构成二臂对照, 双门要求未来动作词与未来时间标记同句共现, 单门仅要求前者, 单门逐句蕴含地是双门的超集, 二臂互为稳健性不分主次、各自 just-identified 并排、禁混进同一 over-identified Hansen J。面板层本列由文章级同名列按银行-年简单均值聚合, 列名与文章级源列相同, 无前缀改写。标题前置机制对本列有一个值得注意的解读含义: 新闻标题是编辑对报道主旨的浓缩, 战略宣示类报道的标题本身往往就是一个前瞻句 (如某银行拟三年投入百亿建设数字银行), 标题作为第零句参与分句与门控后, 这类报道即使正文以背景铺陈为主, 本列也能捕捉到其前瞻主旨; 反之短讯类报道句数少, 标题单句的判定结果对比例影响权重更大, 解读短文章占比高的银行或年份子样本时应意识到这一分母效应, 必要时以文章长度分组做异质性核查。本列无阈值、权重、滞后参数, 全部计算为确定性词表匹配, 依赖 jieba 0.42.1 冻结与词表 v0.1.6 外置单一事实源, 跨机器逐位可复现, 亦不在 BLAS 浮点漂移的非确定列清单内。作为 core 列, 本列在跨论文回归设定中的推荐用法是与主处理变量同方程作叙事属性控制, 或作分组切割变量检验预期渠道; 若研究者需要报告 FLS 自身系数的跨规格稳定性, 应把 ctx 轨、ss 轨与 fonly 单门臂的平行估计并排呈现于稳健性表, 每个规格各自 just-identified, 而非合并为联合矩条件。与 ctx 及 ss 轨并用时须遵守三轨铁律: 各自 just-identified 并排、互为稳健性不分主次, 禁把多轨塞进同一 over-identified Hansen J。

## VAR: frac_fls_ctx

【变体差分】
本列是家族的 ctx 轨: 输入文本为 content_ctx, 即 stage 14 物化的标题前置加目标银行实体窗口文本, 只保留目标银行实体提及附近窗口内的句子, 裁掉与该银行不直接相邻的背景与他行段落。因此本列度量的构念重心从整篇报道的前瞻氛围收窄为目标银行叙事邻域的前瞻密度, 回答的问题是: 报道在直接谈论这家银行的那部分文本里, 有多大比例的句子指向未来。相对 canonical 的 full 轨, 差分有三点。其一, 分母是 ctx 文本的句数, 系统性小于 full 轨, 短分母使比例对单句翻转更敏感, 面板层银行-年均值聚合部分平滑该噪声。其二, 多主体长文中 full 轨会把针对他行或行业整体的前瞻句计入分子, ctx 轨通过实体窗口裁剪削弱这类归属噪声, 当报道同时覆盖多家银行时 ctx 轨对目标银行的前瞻叙事归属更干净。其三, 本列行宇宙遵循 full-only 留篇门控口径 (2026-06-29): 文章是否留篇只看 full 轨验证结论, ctx 轨在该宇宙上条件计算 (conditional-on-full), 本列是条件测度轨而非独立留篇轨。句级双门判定逻辑、词表、匹配细节与 full 轨逐字节一致, 差异完全由输入文本驱动。使用铁律: 本列与 full 及 ss 轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与单门臂 frac_fls_fonly_ctx 的二臂对照同理并排不混。

## VAR: frac_fls_ss

【变体差分】
本列是家族的 ss 轨: 输入文本为 content_ss, 即 stage 14 物化的标题前置加银行与金融科技词同句共现句及其前后各一句的窗口文本 (窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认一句; 该键与 stage 13 共现硬过滤的 sentence_radius 是两个不同键)。本列因此是三轨中窗口最严的一轨, 度量的是银行与金融科技话题交汇处的前瞻密度, 回答的问题是: 恰好在把这家银行与金融科技放在同一句谈论的那部分文本里, 前瞻句占多大比例, 构念上最贴近银行金融科技战略叙事本身的时间取向。回退语义镜像 ctx 轨的物化约定: 当一篇文章不存在银行与金科词的同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置真, 共享同一 n_articles 分母, 回退行上本列取值实质等价于在全文上计算; 上游金科词典不可用 (FINTECH_AC 为空) 时全部行回退置真, 属优雅降级而非报错。因此解读本列时应意识到其取值混合了严格同句窗与回退全文两种文本口径, 回退占比越高本列越向 full 轨收敛。行宇宙同样遵循 full-only 留篇门控 (2026-06-29), ss 轨为 conditional-on-full 条件测度轨。分母为 ss 文本句数, 三轨中最小, 单句翻转扰动最大, 依赖面板均值聚合平滑。判定逻辑与词表与另两轨逐字节一致。使用铁律: 与 full 及 ctx 轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与单门臂 frac_fls_fonly_ss 的对照亦二臂并排不混。

<!-- rendered-citations:begin -->
Wu, Y. (2026). Forward-looking disclosure with and without time frames: Determinants, market responses, and implications. Journal of Risk and Financial Management, 19(6), Article 391. https://doi.org/10.3390/jrfm19060391
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Liu, T., Zhang, J., & Wu, J. (2026). Forward-looking statements in annual reports and firms' financing constraints: A machine learning approach. The International Journal of Accounting, 61(1), Article 2550006. https://doi.org/10.1142/S1094406025500064
Abedin, M. Z., Goldstein, M. A., Huang, Q., & Zeng, H. (2024). Forward-looking disclosure effects on stock liquidity in China: Evidence from MD&A text analysis. International Review of Financial Analysis, 95, Article 103484. https://doi.org/10.1016/j.irfa.2024.103484
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Bozanic, Z., Roulstone, D. T., & Van Buskirk, A. (2018). Management earnings forecasts and other forward-looking statements. Journal of Accounting and Economics, 65(1), 1-20. https://doi.org/10.1016/j.jacceco.2017.11.008
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Muslu, V., Radhakrishnan, S., Subramanyam, K. R., & Lim, D. (2015). Forward-looking MD&A disclosures and the information environment. Management Science, 61(5), 931-948. https://doi.org/10.1287/mnsc.2014.1921
Brown, S. V., & Tucker, J. W. (2011). Large-sample evidence on firms' year-over-year MD&A modifications. Journal of Accounting Research, 49(2), 309-346. https://doi.org/10.1111/j.1475-679X.2010.00396.x
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Li, F. (2010). The information content of forward-looking statements in corporate filings: A naïve Bayesian machine learning approach. Journal of Accounting Research, 48(5), 1049-1102. https://doi.org/10.1111/j.1475-679X.2010.00382.x
Sproat, R., & Emerson, T. (2003). The first international Chinese word segmentation bakeoff. Proceedings of the Second SIGHAN Workshop on Chinese Language Processing, 133-143. https://doi.org/10.3115/1119250.1119269
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
Chen, J.-C., Jain, P. K., & Silveri, S. (Dino). (2025). Forward-Looking Statements and Investor Trading. Journal of Business Finance & Accounting. https://doi.org/10.1111/jbfa.70010
Li, C., Yan, Y., Liu, X., Wan, S., Xu, Y., & Lin, H. (2023). Forward looking statement, investor sentiment and stock liquidity. Heliyon. https://doi.org/10.1016/j.heliyon.2023.e15329
<!-- rendered-citations:end -->
