---
family_id: F119
columns:
- bert_xmodel_disp_ctx
- bert_xmodel_disp_full
- bert_xmodel_disp_ss
- bert_xmodel_lblhet_ctx
- bert_xmodel_lblhet_full
- bert_xmodel_lblhet_ss
unit: "lblhet = 两两符号不一致模型对占比 (无量纲, [0,1]); disp = z 标准化净语调的跨模型样本标准差 (z 分数 SD, [0,+inf))"
formula: "bert_xmodel_lblhet = mean_articles[ #{(a,b): sign(nt_a) != sign(nt_b)} / #pairs ], nt_b = P_b(正面) - P_b(负面), sign(0) 与 ±1 记不一致、0 与 0 记一致, 逐篇可用模型 <2 → NaN; bert_xmodel_disp = mean_articles[ SD_ddof1(z_b) ], z_b = (nt_b - mu_b) / sigma_b 按 模型×轨 在本次 run 文章宇宙估计 (ddof=1), sigma=0 或全 NaN 模型退出"
producer: news_process/pipeline/panel/bert_distribution.py::compute_xmodel_dispersion (文章级中间列 _lblhet_art / _xmd_art) + iter_agg_entries (bank-year mean 聚合, encode 消费); 变量元数据挂载 pipeline/panel/codebook.py
upstream:
- 23_tone_berts.parquet (三 BERT 模型的正面/负面概率列, 三轨各一套)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本, 经 stage 23 打分后间接进入)
citations:
- doi: 10.1111/fire.70030
  type: journal
  authors: Frijns, B., Indriawan, I., Tourani-Rad, A., & Zhang, H.
  year: 2026
  title: "Analyst forecast dispersion and market quality surrounding the FOMC announcement"
  venue: Financial Review
  vol: 61
  issue: 2
  pages_or_artno: 513-531
- doi: "10.2139/ssrn.5199096"
  type: "wp"
  authors: "Lefort, B., Benhamou, E., Ohana, J.-J., Guez, B., Saltiel, D., & Jacquot, T."
  year: 2025
  title: "Examining Independence in Ensemble Sentiment Analysis: A Study on the Limits of Large Language Models Using the Condorcet Jury Theorem"
  venue: "SSRN Working Paper"
- doi: 10.1145/3711896.3737219
  type: journal
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)
  pages_or_artno: 5117-5128
- doi: 10.48550/arXiv.2512.10793
  type: arxiv
  authors: Schlee, M., Weisser, C., Kivimäki, T., Mashiku, M., & Saefken, B.
  year: 2025
  title: "LabelFusion: Fusing large language models with transformer encoders for robust financial news classification"
  venue: arXiv
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: 103870
- doi: 10.48550/arXiv.2406.18403
  type: arxiv
  authors: Bavaresco, A., Bernardi, R., Bertolazzi, L., Elliott, D., Fernández, R., Gatt, A., Ghaleb, E., Giulianelli, M., Hanna, M., Koller, A., Martins, A. F. T., Mondorf, P., Neplenbroek, V., Pezzelle, S., Plank, B., Schlangen, D., Suglia, A., Surikuchi, A. K., Takmaz, E., & Testoni, A.
  year: 2024
  title: "LLMs instead of human judges? A large scale empirical study across 20 NLP evaluation tasks"
  venue: arXiv
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
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
- doi: 10.1111/ecin.12992
  type: journal
  authors: Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y.
  year: 2021
  title: "The influence of hidden researcher decisions in applied microeconomics"
  venue: Economic Inquiry
  vol: 59
  issue: 3
  pages_or_artno: 944-960
- doi: 10.24963/ijcai.2020/622
  type: journal
  authors: Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J.
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20)
  pages_or_artno: 4513-4519
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: The Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
- doi: 10.18653/v1/N19-1423
  type: journal
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT)
  pages_or_artno: 4171-4186
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
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: 10.1111/0022-1082.00490
  type: journal
  authors: Diether, K. B., Malloy, C. J., & Scherbina, A.
  year: 2002
  title: "Differences of opinion and the cross section of stock returns"
  venue: The Journal of Finance
  vol: 57
  issue: 5
  pages_or_artno: 2113-2141
- doi: "10.3389/frai.2025.1609097"
  type: journal
  authors: "Herrera-Poyatos, D., Peláez-González, C., Zuheros, C., Herrera-Poyatos, A., Tejedor, V., Herrera, F., & Montes, R."
  year: 2025
  title: "An overview of model uncertainty and variability in LLM-based sentiment analysis: challenges, mitigation strategies, and the role of explainability"
  venue: "Frontiers in Artificial Intelligence"
- doi: "10.1002/isaf.1549"
  type: journal
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: "Intelligent Systems in Accounting, Finance and Management"
new_dois:
- 10.1111/jofi.12852
- 10.1111/0022-1082.00490
- "10.3389/frai.2025.1609097"
- "10.2139/ssrn.5199096"
- "10.1002/isaf.1549"
---

## CORE

该文实证检验多个大语言模型/金融情感分类器(如FinBERT、DistilRoBERTa、GPT-4)在集成投票中的独立性假设是否成立,发现孔多塞陪审团定理的独立性前提并不适用,模型间判读存在系统性相关的分歧,与本文跨模型判读分歧构念直接呼应。

【构念与来源】
本家族度量的构念是同一篇银行金融科技报道在多个独立 BERT 情感分类器之间引起的判读分歧, 即文本本身对机器分类器而言的判读难度或情感模糊度。直觉上, 一篇立场鲜明、措辞清晰的报道, 无论交给哪一个训练充分的中文金融情感模型, 都应得到方向一致的判定; 而一篇夹叙夹议、正负信息混杂、或者语用上高度依赖上下文的报道, 不同模型给出的正负判定就容易互相冲突。把这种逐篇的跨模型冲突程度在银行年层面取均值, 得到的就是该银行该年度媒体报道语料的平均判读难度, 它既是一个测量质量诊断量, 也是一个可以独立进入回归的文本属性测度。家族由两支孪生测度乘以三条文本轨道构成六列: 标签基的符号不一致占比 bert_xmodel_lblhet 与连续幅度的 z 标准化跨模型标准差 bert_xmodel_disp, 各自有无后缀的 full 轨、_ctx 轨与 _ss 轨变体。canonical 定音在 bert_xmodel_lblhet 的 full 轨列, disp 是其连续幅度版的稳健孪生轨, 双轨互为稳健性、不分主次。数据来源是流水线 stage 23 三个 BERT 情感模型对每篇文章逐轨输出的正面与负面概率列: 两个三分类中文金融情感模型与一个私有微调的二分类模型, 三个模型的成员资格由单一事实源常量集中声明, 本家族的计算模块以参数注入方式接收模型清单, 不反向依赖聚合层。值得强调的是, 本家族属于二〇二六年七月落地的 BERT 分布形状五族扩展中的跨模型双轨一族: 整个五族都是对 stage 23 已落盘概率列的零成本纯后处理, 不新增任何模型推断调用, 不触碰付费 LLM 缓存, 也不改动上游任何一列既有输出。构念上, 本测度与金融学中广为研究的意见分歧构念存在直接类比: 分析师盈利预测的横截面分散度被用作投资者意见分歧的代理并被证明与横截面收益相关 (Diether, Malloy 与 Scherbina, 2002), 社交媒体投资者之间的观点分歧被证明能预测异常交易量 (Cookson 与 Niessner, 2020)。但必须写明的是, 本列的构造是本项目自行定义的, 与上述文献只是构念层面的直接类比, 标准化与聚合方案均不同, 不可表述为按某某方法计算; 更根本的差别在于, 上述文献度量的是人类主体之间的意见分歧, 本家族度量的是机器分类器之间对同一文本的判读分歧, 分歧的主体从投资者换成了模型, 承载的解释也从信念异质性变成了文本模糊度与测量不确定性。

【方法学与计算】
计算分文章级与面板级两步。文章级由 compute_xmodel_dispersion 完成: 对每条轨道, 先为每个可用模型构造逐篇净语调, 即该模型该轨的正面概率减负面概率, 值域负一到正一; 某模型该轨的正面或负面概率列任一缺席, 则该模型退出该轨 (per-model 独立降级, 镜像 finbert2 优雅跳过语义); 某轨可用模型列不足两个, 则该轨双列整体不产, 属合法缺席而非报错。canonical 的 lblhet 中间列取符号化后的两两模型对比较: 对每一对可用模型, 若二者净语调符号不同则记一次不一致, 分母是该篇实际可比的模型对数, 商即该篇的符号不一致占比。符号判定有两条定音规则: 其一, 净语调恰为零 (finbert2 概率重归一后正负各半在真实数据中可达) 与正负一记为不一致, 零与零记为一致; 其二, 刻意不设任何净语调死区, 靠近零点的符号翻转噪声被承认为标签基测度的固有属性而非待修的缺陷, 理由是任何死区宽度都是一个新增的研究者自由度, 而隐藏的研究者决策本身就是应用微观计量可复现性的重要威胁来源 (Huntington-Klein 等, 2021)。逐篇可用模型不足两个时该篇双列均记缺失, 不做任何填补。稳健孪生轨 disp 的中间列则先把每个模型的净语调按模型乘轨道在本次运行的全部文章宇宙上做 z 标准化 (均值与标准差按样本标准差自由度修正一计算, 标准差为零或全缺失的模型退出该轨), 再对每篇文章取跨模型 z 分数的样本标准差 (同样自由度修正一), 非缺模型不足两个的行记缺失。z 标准化的动机是三个模型的原始净语调方差量纲不同 (二分类与三分类的概率几何天然不同), 直接取原始净语调的跨模型标准差会被方差最大的模型主导; 代价是 z 参数取自本次运行的文章宇宙, 带样本依赖与前视性, 逐篇数值不可局部复现, 这正是 disp 被降为稳健轨而由逐篇局部确定、不依赖任何全样本统计量的 lblhet 出任 canonical 的裁决理由。面板级聚合是简单的银行年均值: 两支文章级中间列各自按银行年取算术平均, 得到六个面板列。文章级中间列属于内部生命周期管理对象, 由 runner 在诊断日志之前按声明全集与实际列交集单点删除, 绝不落入文章级 parquet, 因此外部只见面板列。数值上, lblhet 的逐篇支撑在三模型可用时为零、三分之一、三分之二、一四点, 在仅两模型可用时退化为零一两点, 面板均值混合两种支撑, 这一逐篇口径混合 (源自模型全局缺席或逐篇推断失败) 属已记账的测量特征而非缺陷。全族无嵌入 _lg 孪生列: 本家族基于 BERT 分类概率而非 API 嵌入向量, 属非嵌入 carve-out, 与 co-primary 双轨嵌入的列名双射守卫无关。聚合权重口径还有两点须申明。其一, 银行年均值是逐篇等权而非按篇幅或曝光加权, 构念是语料的平均判读难度而非曝光加权的舆论环境, 篇数少的银行年格子均值方差大, 回归中应以报道量类变量作控制或按其加权稳健性重估。其二, 分母是该银行年中间列非缺失的文章数, 它随可用模型构成变化而非恒等于留篇总数: 某篇三模型全部推断失败则该篇对本家族不贡献分母, 但仍计入 n_articles 类计数列, 两个分母口径不可混同。确定性口径上, lblhet 全链只含比较与计数运算, 不经过任何 BLAS 线性代数路径, 不属于本仓已记账的浮点非确定网络列清单, golden 复现按逐位一致要求; disp 含均值与标准差归约, 在固定线程钉一的重生环境下同样逐位可复现, 但跨语料宇宙不可复现的样本依赖性质如前所述。

【文献定位】
本家族站在三条文献脉络的交汇处。第一条是预训练语言模型在金融文本情感测量中的谱系: 双向 Transformer 预训练范式由 Devlin 等 (2019) 确立, 金融领域适配的 FinBERT 系模型随后出现 (Liu 等, 2020), 会计与金融学界的系统评估表明微调后的 FinBERT 在金融文本情感分类上稳定超越词典法与传统机器学习 (Huang, Wang 与 Yang, 2023), 中文金融场景的第二代专用编码器进一步缩小了与通用大模型的部署差距 (Xu 等, 2025)。本项目 stage 23 并行运行三个此谱系内的模型, 正是为了不把测量命运押在任何单一模型上。第二条是测量方法比较与测量误差文献: 词典法的领域适配问题由 Loughran 与 McDonald (2011) 确立为金融文本分析的基本教训, 其综述 (Loughran 与 McDonald, 2016) 与后续会计文本分析综述 (Bochkay 等, 2023) 都反复强调不同测量方法在同一构念上产生系统性分歧; Frankel, Jennings 与 Lee (2022) 直接量化了机器学习测度与词典测度的信息含量差异; 中文语境的领域专用词典 (Du 等, 2022) 是本项目词典轨的锚。在这一脉络里, 本家族把方法间分歧本身从需要在稳健性附录里被动检查的麻烦, 升格为一个显式落盘、可进回归的一等测度。第三条是意见分歧与信息质量文献: 除前述 Diether, Malloy 与 Scherbina (2002) 和 Cookson 与 Niessner (2020) 外, 社交媒体文本信号的信息含量分解 (Cookson, Lu, Mullins 与 Niessner, 2024) 与分析师预测分散度对市场质量的含义 (Frijns 等, 2026) 都表明分歧类测度承载着水平类测度无法替代的信息。方法学上还有一条新兴的旁支直接支持跨模型分歧的诊断价值: 大规模实证研究系统比较了大语言模型与人类评审在数十项自然语言评估任务上的一致性 (Bavaresco 等, 2024), 而把大语言模型输出与 Transformer 编码器融合以获得更稳健金融新闻分类的工作 (Schlee 等, 2025) 则说明模型间分歧正是融合增益的来源; 媒体语调影响投资者行为这一整个测量事业的前提动机则可追溯至 Tetlock (2007)。此外, Herrera-Poyatos 等 (2025, Frontiers in Artificial Intelligence) 的综述系统梳理了基于大语言模型的情感分析中模型间不确定性与输出变异性的成因与缓解策略, 与本家族把跨模型判读分歧本身作为一等可测量构念的思路直接呼应。Todd, Bowden 与 Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融文本情感分析文献并指出方法间与模型间分歧、测量比较是未来研究方向之一, 为本家族把跨模型判读分歧作为一等测度的定位提供综述层支撑。

【识别策略定位】
本家族在识别体系中的定位是测量诊断量与规格稳健性并排成员, 明确不是任何 per-model 梯子的成员, 也不是任何论文的主处理变量。第一种用法是测量质量诊断: 经典测量误差使系数向零衰减, 跨模型判读分歧高的银行年格子正是情感测度测量误差大的格子, 把样本按本列高低分层重估主回归, 若主效应在低分歧子样本中更强, 则与衰减偏误的方向预测一致, 构成对测量误差解释的间接检验。第二种用法是调节变量或控制变量: 在以任一 BERT 情感测度为处理变量的规格中加入本列或其交互项, 检验结论是否被高模糊度语料驱动。第三种用法是作为文本模糊度这一构念本身的代理进入描述性与机制分析。计量口径上有三条铁律必须复述。其一, lblhet 与 disp 双轨互为稳健性、不分主次, 各自 just-identified 并排进各自的回归, 禁止把双轨同时塞进同一个 over-identified 的 Hansen J 检验; 同理, full、_ctx、_ss 三轨也各自 just-identified 并排, 禁混同一 Hansen J; 这一口径与本仓 co-primary 双轨嵌入、词典消融梯度、政治词权重梯子的处理完全同构。其二, 本家族属规格稳健性并排族, 不进入跨模型 FWER 模板: 根级 rwolf 多重检验模板只覆盖同一构念的替代 headline 测量 (Romano 与 Wolf, 2005 意义上的正式数据窥探控制), 而本家族与逐模型净语调是不同构念, 不适用该模板。其三, 若涉及跨模型系数比较, 须按 Table A5 口径用标准化系数, 因为二分类与三分类模型的原始净语调方差不同, 原始系数不可比。留篇门控口径与全仓一致: 一篇文章是否算作银行金融科技报道只看 full 轨的 LLM 验证标志 (二〇二六年六月二十九日 full-only 口径), _ctx 与 _ss 是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集。此外还须申明本家族在因果链条中的位置: 它不是处理变量的候选, 因为跨模型分歧由模型集合与文本共同决定, 对银行结果变量不存在可辩护的排除约束; 它也不宜作工具变量, 因为分歧与情感水平的测量误差机械相关, 恰好违反工具外生性。其正当角色被刻意限定在诊断、调节与描述三类, 任何把本列升格为主处理或工具的用法均属口径违规。与财务结果变量对接时, 由于外部财务面板尚在接入过程中, 相关回归设计以哨兵列占位, 本家族在该阶段的实际用途以测量诊断为先。

【与相邻测度的构念区分】
本家族最容易与四类相邻测度混淆, 须逐一划界。第一, 与逐模型的跨文章分歧测度 disag 系列区分: 后者是 Antweiler-Frank 式构造, 度量同一个模型在同一银行年的不同文章之间正负判定的离散程度, 分歧发生在文章之间; 本家族度量同一篇文章在不同模型之间的判读分歧, 分歧发生在模型之间。前者混合了真实事件面的意见环境异质性与报道选择, 后者在固定文本的条件下把分歧完全归因于分类器判读, 二者在构念上正交。第二, 与逐模型的归一化熵区分: 熵度量单一模型对单一文章输出概率分布的内部不确定性, 是模型内、篇内的模糊度; 本家族是模型间、篇内的模糊度。一个模型可以对错误答案高度自信 (低熵) 而与其他模型冲突 (高 lblhet), 两测度捕捉的失效模式不同; 且二分类模型的熵是净语调绝对值的严格单调递减变换, 跨模型不可比, 而本家族天然定义在模型对上, 不存在该退化。第三, 与 stage 21 的 LLM 三家投票体系区分: 那是三家不同厂商生成式大模型的多数投票共识与 per-model 并排, 属另一条测量方法臂, 与本家族的三个 BERT 判别式分类器在模型来源、成本结构与缓存体系上完全无关, 换嵌入或换 LLM 供应商时本家族零改动。第四, 与验证侧的模型间一致性统计量区分: tone_validation 层的 Krippendorff alpha 与 Cohen kappa 是对全语料汇总的单个一致性系数, 服务于测量效度报告; 本家族是逐篇计算、逐银行年聚合的面板变量, 服务于回归分析, 二者是同一现象在验证域与分析域的两种投影, 不可互相替代。还有第五条边界值得点明: 与词典法之间的方法间分歧不属本家族管辖。词典轨与 BERT 轨的测度差异反映的是方法论范式之差 (词袋计数对语境化表征), 其比较已由测量方法比较文献的框架承接 (Frankel, Jennings 与 Lee, 2022); 本家族刻意把模型宇宙限定在同一方法论范式内的三个判别式编码器, 使分歧的解释收敛到文本模糊度本身, 而不被范式差异污染。若未来引入跨范式分歧测度, 应另立家族而非扩充本族列集。

【已知局限与稳健性梯子】
第一, 标签基的固有噪声: 净语调在零点附近的微小扰动即可翻转符号, lblhet 对近零文章的分歧判定带机械噪声; 项目裁决刻意不设死区, 把该噪声记账为测度固有属性, 使用者若担心可用 disp 轨交叉验证, 因为 z 分数标准差对近零扰动是连续响应。第二, disp 的样本依赖: 其 z 参数取自本次运行的文章宇宙, 属前视变换, 逐篇值不可脱离全样本复现, 亦随语料扩容漂移, 故永远只作稳健轨, 不得升格 canonical。第三, 模型宇宙的时变构成: finbert2 依赖本地私有模型目录, 未配置时优雅跳过, 该缺席使部分运行的分母从三模型三对退化为两模型一对, 逐篇支撑点集改变; 这一混合已在元数据记账, 跨运行比较须核对模型宇宙一致。第四, 二分类与三分类的概率几何差异: finbert2 的中性概率质量被重归一到正负两类, 其符号判定天然比三分类模型更极化, lblhet 的模型对之间因此不是可交换的; 这不影响均值作为总体判读难度代理的解释, 但禁止对单个模型对占比做水平解读。第五, 开发环境退化: 本机 dev 语料仅两年份小样本, 三轨中 _ctx 与 _ss 的文章数远小于 full, 分歧占比在小分母下方差大, 属预期退化, 生产 T 十八年语料下正常。第六, 构念效度的边界: 本家族把跨模型分歧解释为文本模糊度, 隐含假设是三个模型的误差近似独立; 若三模型共享训练语料偏差或架构性盲区, 它们可能对某类文本一致地判错而本列显示零分歧, 即一致不等于正确, 本列度量的是判读的可靠性而非效度, 效度须由人工标注盲标双文件协议与验证侧一致性统计在测量验证层另行背书, 本列不承担该职能。稳健性梯子的完整展开是双测度乘三轨共六列的并排矩阵: 任一主结论若只在单一格子成立而在其余格子系统性反号, 即触发测量而非机制的怀疑; 六列各自 just-identified, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J, 亦不与词典轨、LLM 轨的分歧类测度交叉构造联合工具。梯子之外的两点补充也须记账。其一, 面板深度对推断的约束: 分歧类测度的年内变异部分来自语料构成的年际漂移 (报道主题、媒体来源结构随年份变化), 银行固定效应无法吸收该来源, 建议在含年份固定效应的规格下解释, 并对聚类稳健标准误的簇数保持警觉。其二, 与人工标注的锚定关系: 盲标双文件协议提供的人类金标可用于外部效度抽检 — 抽取本列取值极端的文章子集, 核对人工标注者之间的一致性是否同样恶化; 若机器分歧高的文章人类一致性并不低, 提示分歧源于模型盲区而非文本本身, 该抽检是本列构念效度最直接的可证伪检验, 留待生产语料阶段执行。

## VAR: bert_xmodel_disp_ctx

【变体差分】
本列是跨模型分歧连续幅度测度 disp 在 _ctx 实体窗口轨上的变体, 相对家族 canonical 列 bert_xmodel_lblhet_full 有两重差分。测度差分: 不数符号翻转, 而是先把三个 BERT 模型各自的逐篇净语调按模型乘 _ctx 轨在本次运行文章宇宙上 z 标准化 (自由度修正一), 再取每篇跨模型 z 分数的样本标准差, 银行年均值即本列; 它对靠近零点的判读摇摆给出连续响应, 是 lblhet 标签基噪声的交叉验证轨, 双轨互为稳健性、不分主次。轨道差分: 输入概率来自 stage 23 对 content_ctx 的打分, 该文本是标题 prepend 加目标银行实体邻近窗口的拼接, 剔除了与目标银行无关的段落, 因此本列度量的是聚焦银行相关语境后的跨模型判读分歧, 排除了文章其余部分噪声文本引起的模型分歧。行宇宙遵守 full-only 留篇门控口径: 是否留篇只看 full 轨 LLM 验证, _ctx 是 conditional-on-full 的测度轨。局限与 canonical 相同处从略, 特有一点是 z 参数按轨独立估计, _ctx 轨的标准化基准与 full 轨不同, 两轨数值水平不可直接相减比较, 只可各自进回归后比较标准化系数的符号与量级。另一特有细节是分母口径: 银行年均值的分母为本列文章级中间值非缺失的篇数, 在 _ctx 轨可用模型构成与 full 轨可能不同的格子里, 本列分母与 disp_full 的分母不必然一致, 跨轨比较解释时须意识到二者宇宙的细微错位。本列与其余五列各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。

## VAR: bert_xmodel_disp_full

【变体差分】
本列是 disp 测度在 full 全文轨上的变体, 与家族 canonical 列 bert_xmodel_lblhet_full 同轨异测度, 是其最直接的连续幅度孪生: 二者共享同一批文章、同一组模型净语调输入, 唯一差别是把两两符号比较换成 z 标准化后的跨模型样本标准差 (模型内 z 参数按 full 轨文章宇宙估计, 自由度修正一; 跨模型标准差同样自由度修正一; 标准差为零或全缺失的模型退出, 非缺模型不足两个的篇记缺失)。构念上本列回答的问题是模型间分歧有多大而非是否过符号线, 因此对 canonical 的两个已知噪声源均免疫: 近零净语调的符号翻转在本列只造成小幅连续变化; 逐篇支撑点离散化 (三分之一步长) 在本列不存在。代价是样本依赖: z 参数取本次运行文章宇宙, 带前视性且随语料构成漂移, 逐篇值不可局部复现, 这正是本列被裁为稳健轨而非 canonical 的唯一理由, 语料冻结的复现包内该差异不构成实际威胁。全文轨语义: 输入为标题 prepend 加完整正文的 content_full, 留篇门控即以本轨为准。使用建议是与 canonical 成对报告: 主表报 lblhet_full, 附表以本列重估同一规格, 二者互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bert_xmodel_disp_ss

【变体差分】
本列是 disp 测度在 _ss 同句共现轨上的变体, 差分维度与 disp_ctx 平行但文本口径更严: content_ss 取标题 prepend 加银行与金融科技词在同一句 (加减一句窗口, 由过滤配置的 ss 句半径键控制) 共现的句子集, 是三轨中语境最聚焦、平均文本最短的一轨。须完整复述 ss 回退语义: 当一篇文章不存在银行与金融科技词的同句共现时, content_ss 回退为全文正文且回退标志置真, 该轨镜像 _ctx 的回退框架并共享 n_articles 分母; 因此本列在回退占比高的银行年格子里向 full 轨测度收敛, 解释时应连同回退率一起读。测度构造与其余 disp 列相同: 按模型乘 _ss 轨估计 z 参数 (自由度修正一) 后取逐篇跨模型 z 分数样本标准差, 银行年均值落盘。短文本对 BERT 分类是更高难度的输入, 概率输出更接近判别边界, 跨模型分歧的基线水平天然高于 full 轨, 故本列水平不可与其他轨直接比较, 只作同规格重估的稳健臂。行宇宙为 full-only 留篇集子集 (conditional-on-full)。dev 小样本下本轨文章数最少、方差最大, 属预期退化。使用上本列最有信息量的场景是与回退率联合分层: 在回退率低的银行年格子里, 本列度量的才是真正同句语境的判读分歧; 在回退率高的格子里其与 disp_full 的差异主要是宇宙构成噪声, 不宜过度解读。本列与家族其余列各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。

## VAR: bert_xmodel_lblhet_ctx

【变体差分】
本列是家族 canonical 测度 lblhet (两两符号不一致模型对占比) 在 _ctx 实体窗口轨上的变体, 与 canonical 列 bert_xmodel_lblhet_full 的唯一差分是文本轨道: 输入概率来自 stage 23 对 content_ctx 的打分, 该文本为标题 prepend 加目标银行实体邻近窗口拼接, 裁掉了与目标银行无直接关联的正文段落。构念含义随之收窄: full 轨的跨模型分歧可能部分来自文章中与银行无关的杂质文本 (例如同篇报道兼述其他行业), 本列把判读对象限定在银行相关语境, 若一银行年的 lblhet_ctx 明显低于 lblhet_full, 提示 full 轨分歧主要由语境外文本驱动而非银行相关表述本身模糊。计算细节与 canonical 逐条相同: 逐篇取可用模型净语调符号的两两比较, 零与正负一记不一致、零与零记一致, 不设死区, 可用模型不足两个的篇记缺失, 该轨可用模型列不足两个则整列不产; 银行年均值落盘。本列逐篇局部确定、不依赖任何全样本统计量, 与 disp_ctx 构成该轨的确定性与连续性孪生对。行宇宙遵守 full-only 留篇门控, _ctx 为 conditional-on-full 测度轨。dev 小样本下 _ctx 轨文章数少、占比噪声大属预期退化。本列与家族其余列各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。

## VAR: bert_xmodel_lblhet_full

【变体差分】
本列是全家族的 canonical 列与 core 列, 其余五列的差分语义均以本列为参照系定义, 故本节写清它被定音为 canonical 的完整理由链与精确口径。轨道语义: full 轨, 输入为 stage 23 三个 BERT 模型对 content_full (标题 prepend 加完整正文, 原始内容列不动, 由 stage 14 物化) 的正面与负面概率列; full 轨同时是全仓留篇门控轨, 一篇文章是否计入银行金融科技报道宇宙只看 full 轨 LLM 验证标志 (二〇二六年六月二十九日 full-only 口径), 因此本列的文章宇宙即家族三轨中的最大宇宙, _ctx 与 _ss 轨行宇宙是其子集。测度语义: 逐篇先取每个可用模型的净语调 (正面概率减负面概率), 再对全部可用模型对做符号比较, 不一致对数除以总对数即该篇的标签异质度, 银行年算术平均落盘; 符号定音规则为零与正负一记不一致、零与零记一致, 且刻意不设近零死区。canonical 裁决的理由链有三环。第一环是逐篇局部确定性: 本列每篇的值只依赖该篇自身的模型输出, 不依赖任何跨文章统计量, 语料扩容、子样本切分、复现重放均不改变已有篇的值; 孪生轨 disp 的 z 参数取本次运行文章宇宙, 带前视性与样本依赖, 不满足这一确定性要求, 这是二者主从定音的唯一分水岭。第二环是解释的直接性: 占比支撑在零一区间且以模型对为自然单位, 系数解释为分歧占比每上升一个百分点的边际关联, 比 z 分数标准差的单位更贴近审稿人直觉。第三环是对模型方差异质性的免疫: 符号比较天然不受各模型净语调方差量纲差异影响, 无须标准化即跨模型可比, 而这正是 disp 必须引入样本依赖 z 变换的原因。本列的两个已记账测量特征须在使用时申明: 其一, 逐篇支撑是离散混合的, 三模型在场时为四点 (零、三分之一、三分之二、一), 仅两模型在场时为两点 (零、一), 混合源自 finbert2 全局缺席或逐篇推断失败, 面板均值平滑了该离散性但子样本内的支撑结构可能不同; 其二, 近零净语调的符号翻转噪声属标签基固有, 项目裁决不设死区以免引入隐藏研究者自由度, 交叉验证责任交给同轨 disp 孪生列。定位申明: 本列是测量诊断测度, 非任何 per-model 梯子成员, 不进入跨模型 FWER 模板 (该模板只覆盖同构念替代 headline 测量); 与 disp_full 及 _ctx、_ss 轨变体互为稳健性、不分主次, 六列各自 just-identified 并排, 禁混同一 over-identified Hansen J; 涉及跨模型系数比较一律按标准化系数口径。聚合为逐篇等权均值, 分母是本列中间值非缺失的篇数而非留篇总数, 回归建议以报道量类变量作控制以吸收小分母格子的机械方差。与验证侧的整体一致性系数 (Krippendorff alpha 与 Cohen kappa) 的关系是同一现象的面板投影与汇总投影, 全局一致性高不排除个别银行年格子的本列取值高, 二者互不替代。无 _lg 孪生列 (非嵌入 carve-out), 换嵌入模型或更换 LLM 供应商时本列零改动, 仅当 stage 23 的 BERT 模型清单变化时本列宇宙才随之变化。最后一点是复现口径: 本列全链只含符号比较与计数, 不经任何线性代数库路径, 不在浮点非确定列清单内, 受控重生环境下按逐位一致验收, 这使它同时充当五族扩展中零漂移验证的天然探针列。

## VAR: bert_xmodel_lblhet_ss

【变体差分】
本列是 canonical 测度 lblhet 在 _ss 同句共现轨上的变体, 与 canonical 列 bert_xmodel_lblhet_full 的差分维度是文本轨道, 且是三轨中口径最严的一条: content_ss 取标题 prepend 加银行与金融科技词同句 (加减一句窗口) 共现句集, 度量的是在银行与金融科技被同时谈论的最小语境单元上, 三个 BERT 模型的符号判定有多不一致。构念上这是对银行金融科技关联表述本身模糊度的最尖锐探针: 若分歧在 full 轨高而在本列低, 说明模糊来自文章其他部分; 反之若本列仍高, 则模糊内生于关联表述本身。必须完整申明 ss 回退语义: 无银行与金融科技同句共现的文章, content_ss 回退为全文正文且回退标志置真 (镜像 _ctx 回退框架, 共享 n_articles 分母), 金融科技词自动机不可用时回退标志全真优雅降级; 回退占比高的格子里本列向 full 轨收敛, 解读须伴随回退率。计算规则与 canonical 完全一致: 两两符号比较、零与正负一记不一致、无死区、逐篇可用模型不足两个记缺失、银行年均值落盘; 逐篇局部确定, 与 disp_ss 构成该轨确定性与连续性孪生对。短句集输入下模型概率更贴近判别边界, 本列基线分歧水平天然偏高, 禁与其他轨比水平, 只比同规格标准化系数。行宇宙为 full-only 留篇集子集 (conditional-on-full); dev 小样本退化同 _ctx 轨。本列与家族其余列各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Frijns, B., Indriawan, I., Tourani-Rad, A., & Zhang, H. (2026). Analyst forecast dispersion and market quality surrounding the FOMC announcement. Financial Review, 61(2), 513-531. https://doi.org/10.1111/fire.70030
Lefort, B., Benhamou, E., Ohana, J.-J., Guez, B., Saltiel, D., & Jacquot, T. (2025). Examining Independence in Ensemble Sentiment Analysis: A Study on the Limits of Large Language Models Using the Condorcet Jury Theorem. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5199096
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), 5117-5128. https://doi.org/10.1145/3711896.3737219
Schlee, M., Weisser, C., Kivimäki, T., Mashiku, M., & Saefken, B. (2025). LabelFusion: Fusing large language models with transformer encoders for robust financial news classification. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2512.10793
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Bavaresco, A., Bernardi, R., Bertolazzi, L., Elliott, D., Fernández, R., Gatt, A., Ghaleb, E., Giulianelli, M., Hanna, M., Koller, A., Martins, A. F. T., Mondorf, P., Neplenbroek, V., Pezzelle, S., Plank, B., Schlangen, D., Suglia, A., Surikuchi, A. K., Takmaz, E., & Testoni, A. (2024). LLMs instead of human judges? A large scale empirical study across 20 NLP evaluation tasks. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2406.18403
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y. (2021). The influence of hidden researcher decisions in applied microeconomics. Economic Inquiry, 59(3), 944-960. https://doi.org/10.1111/ecin.12992
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20), 4513-4519. https://doi.org/10.24963/ijcai.2020/622
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. The Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT), 4171-4186. https://doi.org/10.18653/v1/N19-1423
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Diether, K. B., Malloy, C. J., & Scherbina, A. (2002). Differences of opinion and the cross section of stock returns. The Journal of Finance, 57(5), 2113-2141. https://doi.org/10.1111/0022-1082.00490
Herrera-Poyatos, D., Peláez-González, C., Zuheros, C., Herrera-Poyatos, A., Tejedor, V., Herrera, F., & Montes, R. (2025). An overview of model uncertainty and variability in LLM-based sentiment analysis: challenges, mitigation strategies, and the role of explainability. Frontiers in Artificial Intelligence. https://doi.org/10.3389/frai.2025.1609097
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
<!-- rendered-citations:end -->
