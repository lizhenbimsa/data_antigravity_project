---
family_id: F303
columns:
- fin_sent_zh_tone_entropy_ctx
- fin_sent_zh_tone_entropy_full
- fin_sent_zh_tone_entropy_ss
- finbert2_tone_entropy_ctx
- finbert2_tone_entropy_full
- finbert2_tone_entropy_ss
- finbert_cn_tone_entropy_ctx
- finbert_cn_tone_entropy_full
- finbert_cn_tone_entropy_ss
unit: 归一化香农熵 (无量纲, 值域 [0,1]; 文章级熵在 bank-year 格内取均值)
formula: "{b}_tone_entropy{trk} = mean_{bank-year}(H_i); H_i = -Σ_k p_{ik}·ln(p_{ik}) / ln(K_b); K_b = 3 (finbert_cn / fin_sent_zh, 类 = 正面/负面/中性) 或 2 (finbert2, 显式只读 正面/负面 两概率列); p=0 项按极限记 0, 参与类任一概率 NaN 则整篇 H_i 置 NaN"
producer: news_process/pipeline/panel/bert_distribution.py::compute_article_distribution_cols (文章级 _ent_{b}{trk} 中间列) + iter_agg_entries ('mean' 聚合条目, 经 pipeline/panel/encode.py::build_aggregation_dict 消费); 概率列上游 = pipeline/sentiment/tone_berts.py (stage 23)
upstream:
- 23_bert_tone.parquet ({b}_正面/{b}_负面/{b}_中性 三轨概率列)
- 14_materialize_ctx.parquet (content_ctx / content_ss 三轨文本物化)
citations:
- doi: 10.1145/3711896.3737219
  type: journal
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)
  pages_or_artno: 5117-5128
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: 10.1016/j.gfj.2025.101126
  type: journal
  authors: Garcia, J.
  year: 2025
  title: "Beyond the headlines: Sentiment divergence and financial distress"
  venue: Global Finance Journal
  vol: 66
  pages_or_artno: "101126"
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: "100148"
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
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
- doi: 10.1017/S0022109017000187
  type: journal
  authors: Ertugrul, M., Lei, J., Qiu, J., & Wan, C.
  year: 2017
  title: "Annual report readability, tone ambiguity, and the cost of borrowing"
  venue: Journal of Financial and Quantitative Analysis
  vol: 52
  issue: 2
  pages_or_artno: 811-836
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1016/j.irfa.2014.02.006
  type: journal
  authors: Kearney, C., & Liu, S.
  year: 2014
  title: "Textual sentiment in finance: A survey of methods and models"
  venue: International Review of Financial Analysis
  vol: 33
  pages_or_artno: 171-185
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2008.01314.x
  type: journal
  authors: Epstein, L. G., & Schneider, M.
  year: 2008
  title: "Ambiguity, information quality, and asset pricing"
  venue: The Journal of Finance
  vol: 63
  issue: 1
  pages_or_artno: 197-228
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.3390/e27121234"
  type: journal
  authors: "Peng, C.-Y."
  year: 2025
  title: "Information-Processing Entropy and Heterogeneous Sentiment Reaction Windows: Evidence from S&P 500 Stocks"
  venue: "Entropy"
  one_sentence_zh: "该文用归一化香农熵刻画金融文本情感信息处理的不确定性并与市场对不同情感强度的异质反应窗口关联,与本家族用归一化熵测量BERT逐篇语调判断犹豫度的构造思路直接同源。"
- doi: "10.3390/info14070420"
  type: journal
  authors: "Holm, A. N., Wright, D., & Augenstein, I."
  year: 2023
  title: "Revisiting Softmax for Uncertainty Approximation in Text Classification"
  venue: "Information"
  one_sentence_zh: "该文系统评估以softmax输出(含归一化熵)近似文本分类不确定性的可靠性与局限,为本家族用归一化香农熵刻画BERT分类器逐篇判断犹豫度的做法提供方法论层面的校准依据与局限提示。"
- doi: "10.3389/frai.2025.1609097"
  type: journal
  authors: "Herrera-Poyatos, D., Peláez-González, C., Zuheros, C., Herrera-Poyatos, A., Tejedor, V., Herrera, F., & Montes, R."
  year: 2025
  title: "An overview of model uncertainty and variability in LLM-based sentiment analysis: challenges, mitigation strategies, and the role of explainability"
  venue: "Frontiers in Artificial Intelligence"
  one_sentence_zh: "该综述系统梳理LLM情感分析中基于熵的不确定性估计方法及其与语义一致性、模型置信度校准的关系,呼应本家族用归一化熵量化情感分类器逐篇判断模糊度的构念。"
new_dois:
- "10.3390/bdcc9100263"
- 10.1111/j.1540-6261.2008.01314.x
- "10.3390/e27121234"
- "10.3390/info14070420"
- "10.3389/frai.2025.1609097"
---

## CORE

【构念与来源】
本家族九列测量的构念是「语调模糊度」(tone ambiguity), 即金融情感分类器在逐篇新闻上表现出的判断犹豫程度, 属于文本情感测度体系里的二阶矩信息, 与「语调水平」(一阶矩, 正面还是负面) 是两个正交的维度。直觉上, 一篇报道如果被模型以接近确定的把握判为正面或负面, 说明其语气清晰、信息含义明确; 如果三类概率被摊得很平, 说明这篇报道语气含混、正负信号交织, 模型「读不准」。把这种逐篇的读不准程度在银行乘年份的格内取平均, 得到的就是该银行该年度媒体报道整体的语调模糊度水平。构念的经济学动机来自模糊性与信息质量的资产定价文献: Epstein 与 Schneider (2008) 证明当信号质量本身不确定时, 投资者对含混信息的反应是非对称的, 坏消息被放大而好消息被打折, 因此信息的「可读性/清晰度」维度独立于其方向本身进入定价; Carlin, Longstaff 与 Matoba (2014) 进一步用市场分歧的直接测度证明分歧上升伴随超额收益与波动率的系统性变化, 说明二阶矩信息有独立定价含义。在公司金融一侧, Ertugrul, Lei, Qiu 与 Wan (2017) 用年报语调模糊度直接预测借款成本, 发现语气含混的披露对应更高的贷款利差与更严的契约条款, 这与本项目银行融资成本结局变量的研究设计形成同构映照。Garcia (2025) 则表明不同情感信号源之间的分歧程度能预测财务困境, 提示「情感测度不一致本身即是信号」。需要强调, 上述文献是本构念的动机锚点而非构造出处, 本家族的具体构造公式完全由本仓库 bert_distribution 模块给出, 见下节。数据来源上, 本家族是 stage 23 三个中文金融 BERT 模型已落盘概率列的零成本纯后处理: stage 23 (tone_berts) 对每篇通过银行×金融科技共现硬过滤 (stage 13) 的新闻, 用 finbert_cn、fin_sent_zh、finbert2 三个模型各自输出逐类 softmax 概率; 本家族在 panel 构建期把这些概率转换为归一化香农熵, 不重跑任何推理、不新增任何 API 或 GPU 成本。它是 BERT 分布形状五族扩展 (熵、极端负面占比、净语调偏度、跨模型分歧、年内动态) 中的第一族, 也是该扩展的 canonical 代表列所在族, 三个 full 轨列被列为 core 层级。

【方法学与计算】
文章级公式为 H_i = 负的 Σ_k p_ik 乘 ln(p_ik), 再除以 ln(K_b) 归一化, 其中 p_ik 是模型 b 对文章 i 输出的第 k 类概率, K_b 是该模型的类数: finbert_cn 与 fin_sent_zh 为三分类 (正面/负面/中性), K 取三; finbert2 为二分类 (正面/负面), K 取二。除以 ln(K_b) 使不同类数模型的熵都落在零到一的闭区间: 零对应模型把全部概率押在单一类上 (完全确定), 一对应概率完全均匀 (最大犹豫)。概率为零的项按数学极限记零 (p 趋于零时 p 乘 ln p 趋于零)。实现层面有四个承重细节。第一, finbert2 的熵显式只读正面与负面两列: 其中性概率列在 stage 23 是刻意写成全 NaN 的占位列 (为保持三模型列 schema 对齐), 如果按「列存在即参与」的朴素逻辑取三列, finbert2 的熵会被全 NaN 中性列静默清零, 因此代码按 three_class 成员资格显式决定读几列。第二, 真三分类模型若缺失中性列, 该 (模型, 轨道) 的熵键直接不产出, 严禁静默降级为二分类: 因为三分类模型的正负概率之和小于一, 只用两列算出的「熵」会越过归一化上界一, 值域与构念双双破坏, 终审时曾用构造样例实测确认此风险, 故 fail-silent 被封死为「键不产」的合法缺席语义。第三, NaN 处理走「先算后掩码」: 参与类中任一概率为 NaN 的文章, 其熵整体置 NaN, 且实现刻意绕开 np.where(p 大于零, p 乘 ln p, 零) 这类会把 NaN 静默映射为零的反模式 (NaN 与零比较恒为假), 先在非缺失掩码内累加各项, 最后按行级有效性掩码统一置 NaN。第四, per-(模型, 轨道) 独立降级: 某模型某轨的正/负概率列任一缺席 (典型如 finbert2 因本地模型目录未配置被优雅跳过), 该组合的全部键不出现在返回字典中, 只掉自身族、不连坐其他模型, 与共现主嵌入双轨 both-or-neither 的连坐语义刻意不同。聚合层面, 文章级中间列 _ent_{b}{trk} 经聚合声明器以算术均值聚合到 bank-year 格, 即面板列等于该银行该年所有概率非缺文章熵的简单平均; 中间列本身由 runner 在诊断日志之前单点删除, 绝不落入文章级 parquet, 面板列是其唯一持久化形态。上游概率的生成口径继承 stage 23 全部工程细节: 超长文本按滑动窗口切片 (窗口间半幅重叠), 各窗 logits 以置信度加权池化聚合成整篇概率, 高置信窗口权重更大; 三轨文本 (full/ctx/ss) 由 stage 14 物化并统一前置标题, 三个模型各自独立分词分窗。推理失败与空文本各有哨兵, 对应概率为 NaN, 自然被本家族的行级掩码排除出分子分母。本家族属非嵌入测度, 依 carve-out 口径不设 _lg 孪生列。

为什么选熵而不是其他不确定性刻画, 也是一个需要交代的口径选择。候选方案至少有三种: 最大类概率的补 (一减去最大概率)、前两大类概率之差 (margin)、以及香农熵。前两者只用到概率分布的一到两个点, 对第三类概率的信息完全不敏感; 香农熵利用整个分布, 对「概率质量摊得有多平」给出全序刻画, 且不引入任何自由阈值参数, 与本仓库「测度先行、阈值进梯子」的总体设计一致 (对比之下, 极端负面占比族就是带阈值的测度, 所以那一族配了三阈值梯子, 而本族无需)。归一化除以 ln(K_b) 而不是统一除以 ln 三, 是把「各模型在自身类空间内的相对犹豫度」对齐到共同值域的最小干预方案; 它刻意不试图跨模型对齐分布形状, 因为那需要对概率做显式校准, 而校准参数本身样本依赖, 会破坏逐篇局部可复现性 (同样的取舍逻辑也出现在跨模型分歧族: 逐篇局部确定的标签异质性是 canonical, 样本依赖的 z 标准化离散是稳健轨)。白话地讲, 这一族列回答的问题是: 这家银行这一年的金融科技相关报道, 在人工智能情绪识别器读来, 语气是黑白分明还是模棱两可。它不关心说的是好话坏话, 只关心话说得干脆不干脆; 话说得越含糊, 投资者与储户从媒体获得的信息质量越低, 按模糊厌恶定价理论, 这本身就会影响融资成本与存款行为的敏感度。还有一点值得指出: 熵用的是概率而非离散标签, 这使它比「标签是否为中性」的哑变量口径信息更细, 一篇被判为正面但概率仅略高于其余两类的文章, 在标签口径下与斩钉截铁的正面报道不可区分, 在熵口径下则清晰分层; 这也是分布形状五族整体的立足点, 即已付费算出的概率分布里还有大量未被均值消费的形状信息。

【文献定位】
本家族在方法论谱系上处于金融文本情感测度「三角互证」框架的 BERT 一角的二阶矩延伸。词典法源头是 Loughran 与 McDonald (2011) 对通用情感词表在财务语境下系统性误判的批判与领域专用词表的建立, 其后 Loughran 与 McDonald (2016) 与 Kearney 与 Liu (2014) 的两篇综述确立了「测度方法本身是研究设计选择」的自觉; Tetlock (2007) 是媒体语调进入资产定价实证的原点。机器学习一侧, Frankel, Jennings 与 Lee (2022) 系统比较机器学习与词典法对披露情感的捕捉能力, 证明监督学习在样本外解释力上占优但可解释性受损, 这正是本项目坚持词典、LLM、BERT 三法并行互证而非单法独断的文献依据; Todd, Bowden 与 Moshfeghi (2024) 的最新综述把「从词袋到上下文嵌入」的迁移明确为该领域的主线。BERT 谱系内, Huang, Wang 与 Yang (2023) 的 FinBERT 证明金融语料预训练模型在情感与前瞻性信息抽取上全面超越词典与传统机器学习; 本家族用到的 finbert2 对应 Xu 等 (2025) 提出的中文金融专用双向编码器, 其在中文金融文本分类与检索基准上系统超越通用大模型, 是「小型专用编码器在部署场景仍有位置」论点的代表作。中文语境的特殊性由 Du, Huang, Wermers 与 Wu (2022) 确立: 中文金融情感词汇与通用中文、英文金融词汇均有系统差异, 语言与领域双重特异性要求测度工具本地化, 这同样适用于 BERT 模型的选择 (本家族三模型均为中文金融专用或中文金融微调)。Lan 等 (2025) 与 Sun, Yuan 与 Xu (2025) 代表中文金融情感的当前前沿: 前者做实体级细粒度情感, 后者把词典知识与中性特征注入预训练模型, 两者共同说明「中性/含混类的处理」是中文金融情感的活跃难点, 而本家族的熵恰是对中性与含混维度的直接量化。银行媒体情感的中国证据由 Fang, Wang, Wang 与 Yuan (2024) 提供: 媒体情感经存款稳定性渠道影响银行系统性风险, 为本项目银行×年媒体测度进入银行风险回归的设定提供了同域先例。另有 Peng (2025, Entropy) 用归一化香农熵刻画金融文本情感信息处理的不确定性, 并将其与市场对不同情感强度的异质反应窗口相关联, 与本家族用归一化熵测量 BERT 逐篇语调判断犹豫度的构造思路直接同源, 为熵测度在金融情感语境下的适用性提供了独立于本仓库方法论的外部印证。Holm, Wright 与 Augenstein (2023, Information) 系统评估以 softmax 输出 (含归一化熵) 近似文本分类不确定性的可靠性与局限, 为本家族用归一化香农熵刻画 BERT 分类器逐篇判断犹豫度的做法提供方法论层面的校准依据与局限提示。Herrera-Poyatos 等 (2025, Frontiers in Artificial Intelligence) 系统梳理 LLM 情感分析中基于熵的不确定性估计方法及其与语义一致性、模型置信度校准的关系, 呼应本家族用归一化熵量化情感分类器逐篇判断模糊度的构念。

【识别策略定位】
本家族在识别设计中的角色是辅助性二阶矩测度与稳健性维度, 不是任何一篇论文的 treatment 主变量。主线论文的处理变量是语调水平类测度 (如 LLM 三家投票共识语调), 熵族的用途有三: 其一, 作为调节变量或机制变量进入异质性分析, 检验「语调效应是否在语气清晰的报道年份更强」这类信息质量交互假说, 对应 Epstein 与 Schneider (2008) 的非对称反应机制; 其二, 作为控制变量吸收语调测量误差的系统分量, 因为模型犹豫度高的格其语调均值的测量噪声机械地更大; 其三, 作为测度体系完备性的展示列进入描述性统计与附表。计量口径上须严守本仓库梯子铁律: 本家族横跨两条正交梯子, 即 per-model 三模型 (finbert_cn / fin_sent_zh / finbert2) 与三轨 (full / ctx / ss), 两条梯子上的每一个变体各自 just-identified 并排、互为稳健性、不分主次, 严禁把任意两个变体混进同一个 over-identified 的 Hansen J 检验; 该铁律与三轨、co-primary 双轨嵌入、政治词权重梯度、词典消融梯度诸族完全同款。跨模型比较另有一条水平比较禁令: finbert2 是二分类模型, 其熵在逐篇层面恒等于净语调绝对值的严格单调递减变换 (详见其 VAR 节), 与三分类模型「模糊度」构念不可比, 因此任何跨模型的比较只能比各自回归的标准化系数, 严禁直接比较熵的水平或占比的水平。行宇宙口径与全仓一致: 留篇门控为 full-only (二零二六年六月二十九日口径), 即一篇文章是否进入面板聚合宇宙只由 full 轨的 LLM 验证决定, ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集; 熵族三轨列的分母是各自轨内概率非缺的文章数, 不借用其他轨的分母。多重检验口径上, 本家族不进入跨模型 FWER 模板: 该模板 (逐步降压多重检验) 只覆盖对同一构念的可替换 headline 测量, 而熵族属于「规格稳健性并排」而非「同构念替代测量」, 与网络判据敏感性、词典消融梯度同款处理, 即在附表并排报告各变体的点估计与常规推断, 不做族内联合检验; 该分类沿用网络判据敏感性与词典消融梯度的既有先例口径。另须说明聚合形态的刻意从简: 熵族的聚合声明器只登记简单平均一种聚合, 不设市值加权、媒体权威加权、羊群加权臂 (per-model 语调族有这三臂), 熵作为辅助二阶矩测度, 其加权变体的信息增量不足以抵偿列空间膨胀。

【与相邻测度的构念区分】
熵族与同为 stage 23 后代的相邻列族有清晰的构念分工, 逐一区分如下。与 {b}_net_tone (逐篇正面概率减负面概率的格内均值) 的区别是一阶矩对二阶矩: net_tone 回答「说的是好话还是坏话」, 熵回答「话说得清楚不清楚」, 三分类模型上两者不存在函数关系, 一篇高熵文章可以有任意方向的温和净语调。与 {b}_pos_std / {b}_tone_std 类离散度列的区别是「篇内」对「篇间」: std 类测量同一格内不同文章之间语调的分散程度 (报道口径不一致), 熵测量单篇文章内部概率分布的弥散程度 (单篇语气含混), 一个格完全可以篇间高度一致而篇内普遍含混, 反之亦然。与跨模型分歧双轨 bert_xmodel_lblhet / bert_xmodel_disp 的区别是「模型内」对「模型间」: 跨模型族测量三个模型对同一篇文章的判断互相吵不吵架, 熵测量单个模型自己有多犹豫, 前者的信息源是模型间训练语料与架构差异, 后者的信息源是文本自身的含混性, 两者共同构成「测量不确定性」的互补分解。与极端负面占比 {b}_xneg_frac 族的区别是尾部对整体形状: xneg 只看负面概率是否越过高阈值, 是方向性的尾部计数; 熵对三类对称、无方向。与净语调偏度 {b}_net_tone_skew 的区别是篇内分布对格内分布的第三矩: 偏度族在格内文章间算净语调的原始偏度, 与熵的篇内视角不同层。最后, 与 LLM 法的语调及词典法的语调族相比, 本家族属于 BERT 方法臂, 三法互为独立路线, 依三角互证框架并排使用 (Frankel 等 2022; Kearney 与 Liu 2014), 任何单法内的梯子变体不与他法变体混入同一过度识别检验。

【已知局限与稳健性梯子】
第一, 熵测量的是模型的输出置信度分布而非文本模糊性的直接真值: softmax 概率未经显式校准, 系统性过自信或欠自信会平移熵的水平, 但只要校准偏差在模型内时间不变, bank-year 面板中的组内变异仍有效识别相对模糊度变化; 这也是水平比较禁令的另一重依据。第二, K 归一化只对齐了值域, 没有对齐分布形状: 二分类的熵与三分类的熵在相同「犹豫程度」下取值分布不同, finbert2 的熵更是净语调绝对值的确定性变换, 「模糊度」构念仅在三分类模型上为主解释, finbert2 列的角色是形式对齐的伴随列。第三, 超长文本的置信度加权窗口池化会让整篇概率偏向高置信窗口, 从而机械压低长文的熵; 该口径对三模型一致, 且长度本身可由控制变量吸收。第四, 熵对报道体裁敏感: 转述式、罗列式的中性通稿天然高熵, 深度评论天然低熵, 体裁构成的年际漂移会进入熵的时间变异, 解释时应与套话比率、staleness 类文本特征列联读。稳健性梯子方面, 本家族自身提供两条正交梯子 (三模型、三轨), 使用者应将主结论在梯子的每个变体上重跑并报告标准化系数的符号与显著性稳定性, 每个变体各自 just-identified 并排, 禁混同一 Hansen J; per-model 独立降级保证任一模型缺席时其余变体照常可用。与熵族联读的外围稳健性由分布形状五族的其余四族提供: 若熵的效应在极端负面占比、偏度、跨模型分歧上有同向印证, 则「信息质量」解释增强; 若仅熵独动, 则应警惕体裁混杂。生产环境注意: 本家族是纯后处理, 任何对 stage 23 概率列的重生 (换模型、改窗口参数) 都会机械传导到本族全部九列, 复现时须以 stage 23 的冻结口径为锚。

## VAR: fin_sent_zh_tone_entropy_ctx

【变体差分】
本列是 fin_sent_zh 模型归一化熵的 ctx 轨变体, tier 为 standard。与家族 canonical (同模型 full 轨) 的唯一差分在文本口径: ctx 轨文本 = 前置标题 + content_ctx, 后者是 stage 14 物化的「目标银行实体窗口」文本, 即只保留围绕目标银行名出现位置的邻近句窗, 剔除与该银行无关的段落。因此本列测量的是「与目标银行直接相关的那部分文本」的语气含混度, 排除了同篇文章里其他主体报道带来的语调噪声; 代价是文本更短, 概率估计的有效证据更少, 熵的抽样噪声更大, 且实体窗口截断可能切断跨句的语义脉络使模型更犹豫, 造成熵的水平系统性偏移。行宇宙口径: 留篇门控为 full-only, 本列的行宇宙是 full 留篇集的子集, 分母为 ctx 轨概率非缺的文章数, 属 conditional-on-full 测度轨。角色定位: 与 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁与任何其他轨或其他模型的变体混进同一 over-identified Hansen J; 当 full 轨结论在本列复现时, 可排除「效应由文章中与银行无关的段落驱动」的替代解释。缺失语义与家族一致: 该轨概率任一为 NaN 的文章整篇熵置 NaN 退出分子分母, 格级零覆盖为合法 NaN 缺席禁零填充。因文本截短导致的熵水平位移在模型内近似时间不变, 组内识别不受影响, 但本列与 full 轨的水平差不可直接解释为「无关段落的模糊度贡献」, 两轨文本长度差异本身即混杂。

## VAR: fin_sent_zh_tone_entropy_full

【变体差分】
本列是家族三个 canonical 代表列之一, tier 为 core: 模型 = fin_sent_zh, 轨道 = full, 是该模型熵测度的主形态。模型口径: fin_sent_zh 对应 HuggingFace 公开模型 bardsai/finance-sentiment-zh-base, 是在金融短语库类语料上微调的中文金融情感三分类器, 输出正面/负面/中性三类 softmax 概率, 故本列的 K 取三, 熵 = 负的三类概率各自 p 乘 ln p 之和除以 ln 三, 值域零到一: 零表示模型把概率完全押在单一类 (语气斩钉截铁), 一表示三类概率均匀 (完全读不出倾向)。三分类结构使本列是家族内「模糊度」构念解释最干净的列之一: 中性类的存在让「明确的中性」(高中性概率、低熵) 与「含混不清」(三类摊平、高熵) 可分, 这正是 Sun, Yuan 与 Xu (2025) 强调中性特征处理价值的实证体现。轨道口径: full 轨文本 = 前置标题 + 全文正文, 是信息最完整、证据最充分的文本形态, 概率估计的抽样噪声最小; full 同时是留篇门控轨 (full-only 口径), 本列行宇宙 = 全部留篇文章中该模型 full 轨概率非缺者, 是家族内分母最大、覆盖最全的列。聚合 = 格内文章熵的简单平均。与家族 canonical 的差分: 本列自身即 canonical 之一 (家族内三个模型的 full 轨并列为 core, BERT 法无 ensemble headline, 三模型 co-equal 互为稳健、不分主次)。与同模型 ctx / ss 列的关系: 本列是两者的基准轨, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J。与另两个模型 full 列的关系: per-model 梯子上的并排变体, 跨模型只比标准化系数不比水平。降级语义: fin_sent_zh 是 HF 公开模型, strict 模式下非预期加载失败会 fail-loud, 不同于 finbert2 的优雅跳过; 本列在正常生产运行中恒在场。缺失语义分两层: 文章层面, 空文本与推理失败各有哨兵 (窗口计数为零或负一), 对应概率为 NaN, 该篇熵置 NaN 并自动退出格内分子分母; 格层面, 某银行某年 full 轨概率非缺文章数为零时本列该格为 NaN, 属合法缺席而非零值, 下游回归不得以零填充。与同模型一阶矩列的联读关系: 本列与 fin_sent_zh 的净语调列在三分类下无函数关系, 二者的组内相关是实证问题而非机械恒等, 这一点与 finbert2 形成对照 (后者两列在逐篇层面是确定性变换); 因此在同模型内把「语调水平」与「语调模糊度」同时放入回归在本列上是合法设定, 在 finbert2 上则是共线陷阱。训练语料口径的提醒: 该模型的微调语料以金融短语与公告文本为主, 与本项目的新闻语料存在域差, 域差在模型内时间不变, 组内识别不受影响, 但解释熵的绝对水平时不应赋予校准意义。使用建议: 需要单列代表「BERT 语调模糊度」构念时优先取本列或 finbert_cn 的 full 轨 (两者同为三分类、训练语料互相独立, 互为最干净的跨模型印证对), 并以另一者做跨模型稳健性印证; 报告时依水平比较禁令只呈现标准化系数的符号与显著性对照, 不并列原始水平; 若需进一步压尾部替代解释, 与同模型的极端负面占比列及净语调偏度列联读。相对于标签口径的额外说明: 本列消费的是概率分布而非 argmax 标签, 与同模型标签频数类列相比对「勉强判正」与「确定判正」可分, 信息含量严格更细。

## VAR: fin_sent_zh_tone_entropy_ss

【变体差分】
本列是 fin_sent_zh 模型归一化熵的 ss 轨变体, tier 为 standard。与家族 canonical (同模型 full 轨) 的差分在文本口径: ss 轨文本 = 前置标题 + content_ss, 后者是「银行与金融科技词严格同句共现」的句窗文本 (同句命中位置正负一句的窗口, 半径由过滤配置给定), 是三轨中语义靶向最窄、与银行×金融科技构念绑定最紧的口径。本列测量的是「直接谈论该银行金融科技业务的那几句话」的语气含混度, 最大限度剔除文章其余部分的语调污染; 代价是文本极短, 熵的抽样噪声在三轨中最大。回退语义须严格按仓库口径理解: 当一篇留篇文章内不存在银行与金融科技词的同句共现时, content_ss 回退为全文正文且 ss_is_fallback 标记为真, 回退行与非回退行共享同一分母, 因此本列在高回退率的格上向 full 轨机械收敛, 解读 ss 与 full 的差异时应联读回退率。行宇宙为 full 留篇集的子集 (full-only 门控), 分母 = ss 轨概率非缺文章数。本列的证据价值在于构念纯度: 若语调模糊度效应在本列上保持, 说明含混性确实发生在银行金融科技论述本身, 而非文章其他话题段落; 若仅 full 轨显著而本列消失且回退率不高, 应怀疑效应来自泛银行报道的语气而非金融科技专属论述。本列与 full、ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: finbert2_tone_entropy_ctx

【变体差分】
本列是 finbert2 模型归一化熵的 ctx 轨变体, tier 为 standard, 差分维度有二: 模型与轨道。模型侧: finbert2 是本项目经环境变量指向的本地私有二分类中文金融 BERT (谱系对应 Xu 等 2025 的金融专用编码器路线), 只输出正面/负面两类概率, K 取二, 其熵显式只读正负两列 (中性列为全 NaN 占位, 不参与), 且逐篇恒等于净语调绝对值的严格单调递减变换, 「模糊度」构念解释弱于三分类模型, 水平不可与 finbert_cn / fin_sent_zh 的熵直接比较, 只比标准化系数。降级语义: 模型目录未配置或路径无效时整个 finbert2 列族优雅缺席, 仅掉自身族不连坐他模型 (per-model 独立降级)。轨道侧: ctx 轨文本 = 前置标题 + 目标银行实体窗口文本, 测量与该银行直接相关文本段的判断犹豫度, 行宇宙为 full 留篇集子集 (full-only 门控), 分母为 ctx 轨概率非缺篇数。使用警示与同模型 full 列同款且不因换轨而放松: 严禁与同模型净语调类列同回归 (逐篇确定性变换的共线陷阱), 跨模型禁比水平只比标准化系数; 本列的实际角色是 per-model 与三轨两条梯子交点上的对齐臂, 使梯子在全部九个组合上机械同式闭合。本列与同模型 full / ss 轨及另两模型的对应列均互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: finbert2_tone_entropy_full

【变体差分】
本列是家族三个 core 代表列之一: 模型 = finbert2, 轨道 = full。模型口径是本列全部特殊性的来源。finbert2 是项目经 FINBERT2_MODEL_DIR 环境变量解析的本地私有微调模型, 谱系上对应 Xu 等 (2025) 提出的中文金融专用双向编码器 FinBERT2 路线, 即在通用大模型时代仍以小型领域编码器承担金融文本分类的部署角色; 与另两个模型的关键差异是它只做二分类 (负面/正面), 无中性类。由此产生三个必须写明的口径后果。其一, K 取二: 熵 = 负的正负两类概率各自 p 乘 ln p 之和除以 ln 二, 即伯努利熵, 值域仍是零到一。其二, 实现上显式只读正负两列: stage 23 为保持三模型 schema 对齐给 finbert2 补写了全 NaN 的中性占位列, 若按「列在场即参与」的逻辑取三列, 全 NaN 会把本列静默清零, 代码以 three_class 成员资格显式排除之。其三, 构念警示 (家族最重要的警示之一): 二分类概率和恒为一, 设正类概率为 p, 逐篇净语调 nt = 二 p 减一, 熵 = H((一加 nt) 除以二), 是净语调绝对值的严格单调递减函数, 逐篇 Spearman 相关恒为负一; 换言之本列在逐篇层面不携带独立于「语调强度」的新信息, 「模糊度」解释仅在三分类模型上成立, 本列的角色是家族形式完备性与跨模型梯子的对齐臂, 严禁与三分类模型比较熵的水平, 跨模型只比各自回归的标准化系数。轨道口径: full 轨 = 前置标题 + 全文正文, 留篇门控轨 (full-only), 行宇宙为全部留篇文章中 finbert2 概率非缺者。降级语义: 模型目录未配置时本列连同整个 finbert2 列族优雅缺席, 仅掉自身族 (per-model 独立降级, 镜像 stage 23 的 graceful skip), 不影响另两模型任何列; 这也意味着复现包在无该私有模型的机器上跑出的面板将合法缺失本列, 复现文档须按缺席而非错误对待。既然逐篇不携带独立信息, 为何仍保留本列而不是直接删去, 有三点理由值得写明。第一, 梯子完备性: per-model 梯子的价值在于「同一构念表达式对三个模型机械同式计算」, 若对二分类模型改用别的表达式, 梯子就不再是纯粹的模型替换而混入了公式替换, 稳健性论证被污染。第二, 格内聚合后的非恒等: 逐篇的单调变换经过格内平均后, 本列与同模型净语调绝对值的格均值不再是彼此的确定函数 (均值不与非线性变换交换), 面板层面本列仍有边际变异, 只是解释须回到「语调强度的凹变换均值」而非模糊度。第三, 私有模型的部署证据价值: finbert2 是三模型中唯一的项目本地私有微调模型, 它的在场使 BERT 臂不完全依赖公开权重的第三方托管稳定性。使用警示汇总: 严禁在同一回归内同时放入本列与同模型净语调类列 (逐篇共线陷阱); 严禁与三分类模型比较熵水平或占比水平; 报告时只呈现标准化系数; 论文正文若引用本列, 须随文披露其与净语调绝对值的恒等变换关系, 避免审稿人将其误读为独立的模糊度证据。本列与同模型 ctx / ss 及另两模型 full 列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: finbert2_tone_entropy_ss

【变体差分】
本列是 finbert2 模型归一化熵的 ss 轨变体, tier 为 standard, 差分同样落在模型与轨道两个维度。模型侧与同模型 full 列完全一致: 二分类伯努利熵 (K 取二, 显式只读正负两列, 全 NaN 中性占位列不参与), 逐篇恒等于净语调绝对值的严格单调递减变换, 模糊度构念解释弱, 跨模型禁比水平只比标准化系数; 模型目录未配置时整族优雅缺席, per-model 独立降级。轨道侧: ss 轨文本 = 前置标题 + 银行与金融科技词严格同句共现的句窗文本, 是三轨中构念靶向最窄的口径, 测量「直接谈论该银行金融科技业务的句子」上模型的判断犹豫; 回退语义与全仓一致, 无同句共现的文章其 content_ss 回退为全文正文并标记 ss_is_fallback 为真, 回退行与非回退行共享分母, 高回退率格上本列向同模型 full 列机械收敛。行宇宙为 full 留篇集子集 (full-only 门控), 分母 = ss 轨概率非缺篇数。与同模型其余轨相同, 本列严禁与 finbert2 净语调类列同回归 (共线陷阱), 跨模型禁比水平; 其角色是两条梯子交点上的对齐臂, 保证 per-model 梯子在最窄文本口径上同样机械闭合。本列与同模型 full / ctx 轨及另两模型 ss 列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: finbert_cn_tone_entropy_ctx

【变体差分】
本列是 finbert_cn 模型归一化熵的 ctx 轨变体, tier 为 standard。模型口径: finbert_cn 对应 HuggingFace 公开模型 yiyanghkust/finbert-tone-chinese, 中文金融语调三分类器 (正面/负面/中性), K 取三, 谱系上属 Huang, Wang 与 Yang (2023) FinBERT 路线的中文迁移, 三分类结构使其熵具备完整的模糊度构念解释 (明确中性与含混不清可分)。轨道差分: ctx 轨文本 = 前置标题 + 目标银行实体窗口文本, 本列测量与目标银行直接相关文本段上该模型的判断犹豫度, 剔除同篇其他主体段落的语调噪声, 代价是文本变短、熵的抽样噪声变大且窗口截断可能系统性抬升犹豫水平。行宇宙口径: full-only 留篇门控下, 本列行宇宙为 full 留篇集子集, 分母 = ctx 轨概率非缺文章数, 属 conditional-on-full 测度轨。缺失语义: 该轨概率任一 NaN 的文章熵置 NaN 退出分子分母, 格级零覆盖为合法 NaN 缺席禁零填充。证据价值: 本列与 fin_sent_zh 的 ctx 列构成实体窗口口径上同为三分类的对称印证对, 若 full 轨的模糊度效应在两者上同时保持, 「效应由无关段落驱动」与「效应由单一模型伪影驱动」两个替代解释可同时排除。本列与同模型 full / ss 轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J; 与另两模型 ctx 列构成 per-model 梯子的并排变体, 跨模型只比标准化系数。

## VAR: finbert_cn_tone_entropy_full

【变体差分】
本列是家族三个 core 代表列之一: 模型 = finbert_cn, 轨道 = full。模型口径: finbert_cn 对应 HuggingFace 公开模型 yiyanghkust/finbert-tone-chinese, 是在中文金融语料上训练的语调三分类器, 输出正面/负面/中性三类 softmax 概率, K 取三, 熵 = 负的三类概率各自 p 乘 ln p 之和除以 ln 三, 值域零到一。该模型在谱系上是 Huang, Wang 与 Yang (2023) 确立的「金融语料预训练 BERT 全面超越词典与传统机器学习」路线在中文的直接落地, 与 Du 等 (2022) 论证的中文金融文本语言与领域双重特异性相配套: 用中文金融专训模型而非通用中文模型或英文金融模型翻译, 是本项目 BERT 臂的口径选择。在三模型中, finbert_cn 是社区使用最广、下游引用最密的中文金融语调分类器, 其行为特征在公开基准上有较充分的外部记录, 这降低了「单一模型私有怪癖」进入测度的风险, 也使本列适合充当家族对外报告时的首选展示列。三分类结构下本列的模糊度构念解释完整: 高中性概率低熵对应「明确的中性报道」, 三类摊平高熵对应「语气含混、正负交织」, 两态在二分类模型上不可分而在本列可分, 这是本列与 finbert2 对应列最本质的构念差异。轨道口径: full 轨 = 前置标题 + 全文正文, 证据最充分、概率估计噪声最小; full 是留篇门控轨 (full-only 口径, 二零二六年六月二十九日), 本列行宇宙 = 全部留篇文章中该模型概率非缺者, 分母覆盖为家族内最大之列。聚合 = 格内文章熵简单平均, 超长文本的整篇概率由置信度加权窗口池化给出 (高置信窗口权重更大, 对长文有机械压低熵的方向性影响, 三模型口径一致)。降级语义: HF 公开模型, strict 模式非预期加载失败 fail-loud, 正常生产恒在场; 文章级缺失 (空文本或推理失败哨兵) 对应熵 NaN 并退出格内分子分母, 格级零覆盖为合法 NaN 缺席, 禁零填充。与同模型其余分布形状族的联读: finbert_cn 的极端负面占比族捕捉方向性尾部、净语调偏度族捕捉格内第三矩、本列捕捉篇内二阶弥散, 三者对同一模型概率输出做互补分解, 若一项结论获得其余两项同向印证则信息质量解释显著增强。与 fin_sent_zh 对应列的关系是家族内最有证据价值的一对: 两模型同为三分类、训练语料与微调路线互相独立, 对同一篇文章的犹豫度判断若系统一致, 说明高熵是文本自身属性而非单一模型的校准伪影; 若系统分歧, 则分歧本身进入跨模型分歧族的测量范围。因此实务顺序建议是先在本列与 fin_sent_zh 的 full 列上做对称印证, 再以 finbert2 对齐臂补全梯子。本列与 fin_sent_zh 的 full 列互为最对称的跨模型印证对, 两者加 finbert2 对齐臂构成 per-model 梯子; 与同模型 ctx / ss 构成三轨梯子; 全部变体各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J, 跨模型禁比水平只比标准化系数。同模型内本列与净语调列无机械函数关系, 允许同回归共存 (对照 finbert2 的共线禁令), 但两列联合进入时应对语调水平做中心化以缓解交互项共线。

## VAR: finbert_cn_tone_entropy_ss

【变体差分】
本列是 finbert_cn 模型归一化熵的 ss 轨变体, tier 为 standard。模型口径与同模型 full 列一致: yiyanghkust/finbert-tone-chinese 三分类器, K 取三, 模糊度构念解释完整。轨道差分: ss 轨文本 = 前置标题 + 银行与金融科技词严格同句共现的句窗文本 (同句命中位置正负一句窗口), 三轨中语义靶向最窄, 本列测量「直接谈论该银行金融科技业务的句子」上该模型的判断犹豫度, 是熵测度与银行×金融科技构念绑定最紧的形态; 代价是文本最短、抽样噪声最大。回退语义严格按仓库口径: 无银行与金融科技词同句共现的留篇文章, 其 content_ss 回退为全文正文且 ss_is_fallback 置真, 回退行与非回退行共享同一分母, 高回退率格上本列向同模型 full 列机械收敛, 解读三轨差异须联读回退率指示列。行宇宙为 full 留篇集子集 (full-only 门控), 分母 = ss 轨概率非缺文章数。证据价值: 三分类结构加最窄文本口径使本列成为「银行金融科技论述本身是否含混」这一问题解释最直接的列; 与 fin_sent_zh 的 ss 列做同为三分类的对称印证可进一步排除单模型伪影。本列与同模型 full / ctx 轨及另两模型 ss 列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), 5117-5128. https://doi.org/10.1145/3711896.3737219
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. Global Finance Journal, 66, 101126. https://doi.org/10.1016/j.gfj.2025.101126
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Ertugrul, M., Lei, J., Qiu, J., & Wan, C. (2017). Annual report readability, tone ambiguity, and the cost of borrowing. Journal of Financial and Quantitative Analysis, 52(2), 811-836. https://doi.org/10.1017/S0022109017000187
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Kearney, C., & Liu, S. (2014). Textual sentiment in finance: A survey of methods and models. International Review of Financial Analysis, 33, 171-185. https://doi.org/10.1016/j.irfa.2014.02.006
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Epstein, L. G., & Schneider, M. (2008). Ambiguity, information quality, and asset pricing. The Journal of Finance, 63(1), 197-228. https://doi.org/10.1111/j.1540-6261.2008.01314.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Peng, C.-Y. (2025). Information-Processing Entropy and Heterogeneous Sentiment Reaction Windows: Evidence from S&P 500 Stocks. Entropy. https://doi.org/10.3390/e27121234
Holm, A. N., Wright, D., & Augenstein, I. (2023). Revisiting Softmax for Uncertainty Approximation in Text Classification. Information. https://doi.org/10.3390/info14070420
Herrera-Poyatos, D., Peláez-González, C., Zuheros, C., Herrera-Poyatos, A., Tejedor, V., Herrera, F., & Montes, R. (2025). An overview of model uncertainty and variability in LLM-based sentiment analysis: challenges, mitigation strategies, and the role of explainability. Frontiers in Artificial Intelligence. https://doi.org/10.3389/frai.2025.1609097
<!-- rendered-citations:end -->
