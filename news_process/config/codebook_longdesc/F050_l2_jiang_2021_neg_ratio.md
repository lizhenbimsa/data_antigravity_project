---
family_id: F050
columns:
- avg_jiang_2021_neg_ratio_ctx
- avg_jiang_2021_neg_ratio_full
- avg_jiang_2021_neg_ratio_ss
unit: 比率/占比 (proportion, 无量纲 ∈ [0,1]; 篇级 = 负面词 token 数 / word-token 数, 面板级 = 银行-年内篇级比率的等权均值)
formula: "avg_jiang_2021_neg_ratio_<trk> = mean_articles(jiang_2021_neg_ratio_<trk>), trk ∈ {full, ctx, ss}; 篇级 jiang_2021_neg_ratio = neg_count / n_word_tokens, neg_count = jiang_2021 词典命中且语言学规则处理后 final < 0 的 token 数 (含 21 个 positive∩negative 跨类重叠词两侧计数), n_word_tokens = 剔除纯标点/纯数字 token 后的有效词 token 数; 空文本/零分母/词典缺失 → NaN"
producer: news_process/pipeline/sentiment/tone_words.py::_analyze_single_article (篇级, stage 22) ; news_process/pipeline/panel/encode.py::build_aggregation_dict Section M (银行-年 mean 聚合, stage 40)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (jiang_2021_neg_ratio_full / _ctx / _ss)
- config/tone_dicts.json (jiang_2021 词表, SSOT)
citations:
- doi: 10.1007/s10479-025-06567-y
  type: journal
  authors: "Anastasiou, D., Katsafados, A., & Tzomakas, C."
  year: 2026
  title: "Banks' stock price crash risk prediction with textual analysis: A machine learning approach"
  venue: Annals of Operations Research
  vol: 357
  issue: 1
  pages_or_artno: 89-111
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: "Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y."
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: Advance online publication
- doi: 10.1108/JED-06-2025-0296
  type: journal
  authors: "Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B."
  year: 2025
  title: "Investor negativity derived from news shapes firm distress dynamics under bounded rationality"
  venue: Journal of Economics and Development
  vol: 27
  issue: 4
  pages_or_artno: 309-321
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: "Punetha, N., & Jain, G."
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: Article 20
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: "Ma, Y., Zhang, T., & Zhang, P."
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: "Sun, Y., Yuan, H., & Xu, F."
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: "100148"
- doi: 10.48550/arXiv.2506.19958
  type: arxiv
  authors: "Valdenegro, D., Yan, J., Dai, D., & Rahal, C."
  year: 2025
  title: "RobustiPy: An efficient next generation multiversal library with model selection, averaging, resampling, and explainable artificial intelligence"
  venue: arXiv
- doi: 10.1080/00036846.2025.2536881
  type: journal
  authors: "Wu, M., Shen, L., Wu, T., & Shao, Y."
  year: 2025
  title: "Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China"
  venue: Applied Economics
  pages_or_artno: Advance online publication
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: "姜富伟, 孟令超, 唐国豪"
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: "经济学(季刊)"
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1016/j.jfineco.2018.10.001
  type: journal
  authors: "Jiang, F., Lee, J., Martin, X., & Zhou, G."
  year: 2019
  title: "Manager sentiment and stock returns"
  venue: Journal of Financial Economics
  vol: 132
  issue: 1
  pages_or_artno: 126-149
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: "Pröllochs, N., Feuerriegel, S., & Neumann, D."
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: 10.1111/jofi.12027
  type: journal
  authors: "Garcia, D."
  year: 2013
  title: "Sentiment during recessions"
  venue: The Journal of Finance
  vol: 68
  issue: 3
  pages_or_artno: 1267-1300
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
new_dois:
- 10.1111/jofi.12027
- 10.1111/j.1540-6261.2010.01625.x
---

## CORE

【构念与来源】
本家族三列 avg_jiang_2021_neg_ratio_full、avg_jiang_2021_neg_ratio_ctx 与 avg_jiang_2021_neg_ratio_ss 测量同一构念在三条文本轨道上的平行实现: 一家银行在一个日历年内的媒体报道中, 命中姜富伟等 (2021) 中文金融情感词典负面词表的词汇占全部有效词汇的比例, 先逐篇计算、再在银行-年单元内取等权算术均值。它是负面媒体暴露强度的词典法密度测度: 分子只数负面词, 分母是文本有效词量; 与把正负两侧轧差再归一化的净语调分值相比, 本家族刻意放弃极性对冲, 只保留负面一侧的信息。这一正负分离的设计有明确的文献依据: Loughran 与 McDonald (2011) 在金融文本分析的奠基性工作中证明, 领域定制的负面词表所承载的信息含量远高于正面词表, 正面用语因惯常的礼貌性与宣传性表达而信噪比偏低; Garcia (2013) 进一步证明新闻情绪的资产定价含义在经济衰退期高度不对称, 把正面与负面词频作为两个独立协变量分别进入回归, 能避免净指标把两侧信号相互抵消后掩蔽真实效应。本家族正是该传统在中文银行新闻语料上的单词典实现。词表来源上, 姜富伟等 (2021) 发表于经济学 (季刊) 的中文金融情感词典以 Loughran-McDonald 英文词典为蓝本翻译并本土化扩充, 正面词表三千一百九十四条、负面词表五千六百二十一条, 原始发布中两类不跨类去重; 该文用这部词典构造媒体文本情绪指标并证明其对中国股票回报的可预测性, 是中文金融文本词典法研究的核心锚点之一。在本仓库六部词典体系中 jiang_2021 排第一部, 与 yao_2021、bian_2021、du_2022、you_2018 以及 Loughran-McDonald 中文主译本并列, 六部词典各自产出同构的负面密度列, 构成跨词典稳健性梯子。数据来源为经过预处理、银行实体识别、金融科技词共现硬过滤后的银行与金融科技交集新闻语料; 篇级词典打分在 stage 22 完成, 银行-年聚合在 stage 40 面板导出完成, 全链路零 API 成本、确定性可复现, 唯一确定性锚为冻结的分词器版本与冻结的词表文件, 与需要付费大模型的情感轨在成本与可复现口径上完全不同。

【方法学与计算】
篇级计算链路如下。上游 stage 14 物化三条文本轨道: content_full 为标题前置拼接全文正文; content_ctx 为标题前置拼接目标银行实体上下文窗口文本; content_ss 为标题前置拼接银行与金融科技词同句共现句及其前后邻句窗口。stage 22 对每篇文章的每条轨道用独立的 tone 分词器执行一次 jieba 分词, 分词结果由六部词典共享, 保证跨词典可比。对 jiang_2021 词典, 引擎以逐 token 状态机施加三条语言学规则: 否定词在其后两个分词单元的窗口内翻转情感词极性; 程度副词按六级权重体系对随后的情感词幅度做最高三倍的缩放; 转折连词之后的情感词幅度乘一点五加权, 句末标点重置全部句法状态, 修饰效应不跨句传播。每个命中词典的 token 得到规则处理后的最终得分, 最终得分为负者计入负面词数。这里有一个对本家族构念极为关键的结构性事实: 程度副词与转折加权的乘数恒为正, 不可能改变符号, 因此负面词计数在构造上只对否定规则敏感, 对程度与转折两条幅度规则完全不敏感; 换言之, 本家族是否定校正后的负面词计数密度, 比裸词频更接近语义真值, 又不掺入幅度加权带来的研究者自由度。词典中同时出现在正负两侧的二十一个跨类重叠词按项目决策保留并两侧同计, 即同一 token 同时计入正面与负面计数, 使净语调拉向中性而不武断选边, 本列的分子因此把这类词按一票计入负面侧。须与无词典前缀的并集口径明确区分: 本家族的分子取自单一 jiang_2021 词典的负面计数, 而无前缀的 neg_ratio 分子取自六词典固定并集词表的负面计数, 二者虽共享同一 word-token 分母与同一状态机, 计数所用的词表却不同一; 本家族服务于跨词典异质性梯子的单臂, 并集口径服务于全样本共用同一测量工具的共识测度。分母为该篇该轨的有效词 token 数, 剔除纯标点与纯数字 token, 与本仓库 LM 与 FLS 族比率的分母修复采用同一正则口径, 避免标点密度的逐篇差异造成非常数稀释。篇级取值保留六位小数; 空文本、分词后无有效 token、或词典加载缺失时, 篇级值为缺失值而非零, 缺测与真零严格区分。面板层由 encode 模块聚合字典的 Section M 注册, 对银行-年单元内全部留存文章的篇级比率取等权算术均值, 缺失篇按均值聚合惯例跳过、不进入分子分母; 上游列整列缺席时聚合入口自动跳过, 不抛错。同一注册块并排产出正面孪生列 avg_jiang_2021_pos_ratio, 两者共享分母与规则口径, 相对结构进一步充当词典法媒体分歧类下游测度的词级输入。行宇宙口径遵循全仓 full-only 留篇门控: 一篇文章是否计入银行-年单元只由 full 轨的大模型验证结论决定, ctx 与 ss 轨是该留篇集合上的条件测度, 行宇宙为 full 留篇集的子集, 三轨共享同一篇数分母语境。ss 轨回退语义镜像 ctx 轨: 当一篇文章不存在银行与金融科技词的同句共现时, content_ss 回退为全文正文并置回退旗标; 金融科技词表不可用时全部旗标置真, 优雅降级而非报错。变量标签由面板导出层批量注入, 属泛型推断标签而非人工精修标签。分词器版本冻结在 jieba 0.42.1, 与 Prompt 冻结锚共同保证跨机跨期字节级可复现。

【文献定位】
本家族在文献谱系中的位置可从四条线索刻画。第一条是负面词表主导传统: Loughran 与 McDonald (2011) 确立领域定制负面词表在披露文本中的信息优先地位, Garcia (2013) 确立正负词频分离进入回归的计量惯例, 姜富伟等 (2021) 把这一传统移植到中文金融媒体语料并给出回报可预测性证据, 三者共同构成本家族单词典负面密度设计的直接依据。第二条是否定处理线索: 对词典法最经典的批评是无法处理诸如不良贷款率并未上升这类否定语境下的负面词误计, Pröllochs, Feuerriegel 与 Neumann (2016) 证明否定作用域检测能实质改进新闻驱动交易的决策支持, Punetha 与 Jain (2025) 给出无监督数学框架处理否定的最新进展; 本家族的否定窗口翻转规则正是对这条批评的工程化回应, 且如前述, 负面计数在构造上恰好只吸收否定校正这一条规则, 使方法论辩护可以聚焦。第三条是中文词典生态线索: Ma, Zhang 与 Zhang (2025) 构建面向中国境内投资者的细粒度中文情感词典并展示其应用价值, 说明中文金融情感词典生态仍在快速演化, 单一词典的词表选择是真实存在的研究者自由度, 这正是本仓库同时物化六部词典平行列族的动机; Sun, Yuan 与 Xu (2025) 展示词典知识可注入预训练语言模型以改进金融情感分析, 说明词典法与神经方法是互补而非替代关系, 对应本仓库词典轨、大模型轨与 BERT 轨三方法并行的架构。第四条是负面文本信息的经济后果线索: Jiang, Lee, Martin 与 Zhou (2019) 证明由词典法聚合的经理人情绪指数对股票回报具有稳健预测力, 确立篇级词典分值聚合为主体级指数的方法论先例, 与本家族篇级比率聚合为银行-年均值的做法同构; Pham, Huynh, Nguyen 与 Luu (2025) 证明源自新闻的投资者负面情绪在有限理性框架下塑造企业困境动态, 直接支持负面侧单独成列的经济学意义; Anastasiou, Katsafados 与 Tzomakas (2026) 用银行文本做股价崩盘风险的机器学习预测, 说明银行负面文本信号对审慎结果变量的预测价值; Li 等 (2026) 从文本风险披露中恢复金融网络结构与关联性, 说明负面与风险文本测度可进一步充当网络与传染分析的输入, 呼应本仓库把负面比率喂入行业负面冲击与媒体分歧等下游构件的用法。应用域上, Wu, Shen, Wu 与 Shao (2025) 关于银行与金融科技公司战略合作影响银行风险承担的证据, 界定了本语料银行与金融科技交集报道的经济学语境: 本家族测量的正是这一语境下负面叙事的浓度。

【识别策略定位】
在识别链条中, 本家族属于处理变量侧的文本测度而非结果变量, 定位是描述性证据与条件相关证据的构件, 不单独主张因果识别。之所以不主张独立因果识别, 根源在于媒体报道的内生性: 新闻负面叙事的浓度既反映也回应银行自身的基本面与风险状况, 报道量与语调同银行经营处境之间存在同时性与反射关系, 因此把负面密度直接当作外生冲击会混淆信息环境的度量与被度量的经济状态; 本家族的定位因此是刻画信息环境、构造条件相关证据, 而非制造准实验变异。它在论文组合中的典型用法有三类。其一, 作为净语调主测度的机制拆解伴随变量: 当某篇论文的净语调系数显著时, 用负面密度与正面密度两列分别替换净语调重估, 可回答效应究竟由负面一侧还是正面一侧驱动, 这正是 Garcia (2013) 式正负分离在回归设计上的落地; 而 Garcia (2013) 关于新闻情绪的定价含义在衰退期显著放大的不对称发现进一步提示, 负面侧密度在银行承压时段可能承载更强的边际信息, 单列负面密度使这一时变异质性可被直接检验。其二, 作为媒体分歧类测度的词级输入: 银行-年内正负两侧比率的相对结构是词典法分歧指标的原材料, 本家族与其正面孪生列在聚合注册处的定位即词级分歧输入, 分歧构件消费的是两侧密度的相对关系而非任一单侧的绝对水平。其三, 作为跨方法三角验证的词典臂: 与大模型三家投票轨、BERT 三模型概率轨的负面占比族并排, 检验负面媒体暴露这一构念是否对测量方法敏感, 词典法的透明可审计性在此轨中充当神经方法的外部对照。识别增强依赖面板结构与工具变量扩展: 银行与年份双向固定效应吸收银行个体水平的时不变差异与全样本共同的年度冲击; 三类工具变量各自提供不同来源的准外生变异 — 同组留一均值利用同类银行媒体暴露的共同成分而剔除自身、广义 Bartik 用行业层份额与时间冲击的交互构造预测暴露、媒体来源风格暴露用各报道来源固有的语调倾向构造与个体基本面正交的暴露, 三者各自 just-identified 单独进入各自的两阶段最小二乘。行宇宙口径亦影响识别样本: 一篇文章是否计入银行-年单元只由 full 轨的大模型验证结论决定, 本家族三轨共享这同一 full-only 留篇集, ctx 与 ss 轨是该集合上的条件测度、其行宇宙为 full 留篇集的子集。需要反复强调的口径铁律是: 三条文本轨道、六部词典、跨方法各梯子的每一个成员都各自 just-identified 并排进入各自的回归, 互为稳健性、不分主次, 严禁把同族多个变体混进同一个 over-identified 的 Hansen J 检验; 同构念高相关测度堆进同一组矩条件, 既无识别增益, 又会使过度识别检验的拒绝无从归因于任一具体变体, 这一铁律对本家族三轨同样无条件适用。

【与相邻测度的构念区分】
本家族与仓库内多个近邻列族测的不是同一构念, 使用与解读时须严格区分。与 jiang_2021_tone 净语调族的区别是密度对净值: 净语调是规则加权后正负轧差再自归一化的有界分值, 其分母是命中词加权幅度绝对值之和, 无命中词时为中性零; 本家族分母是全文有效词量, 保留篇幅信息, 前者回答倾向多偏负, 后者回答负面词浓度多高。两者在长文淡负与短文浓负的情形下会给出方向相反的排序: 一篇万字长篇里散布少量强负面词, 净语调可能显著为负而负面密度极低; 一篇短讯通篇负面词, 负面密度很高而净语调因缺乏正面对冲仅中度为负 — 因此两列不可互相替代, 应各自成轨。与 jiang_2021_negonly_tone 等规则消融族的区别是作用面: 消融族作用于净语调分值, 通过开关否定、程度、转折三条规则的全 powerset 检验语调对语言学规则组合的敏感性; 比率族只物化全规则口径一个版本, 且如前述其负面计数在构造上仅吸收否定规则、对幅度规则天然不敏感, 本身即近似仅否定语义, 无须另设消融臂, 这也是本家族不随规则消融梯度衍生多个变体的原因。与无词典前缀的 avg_neg_ratio 的区别是词表口径: 后者的计数基是六部词典的固定并集词表, 全样本共用同一测量工具, 兑现固定词表构念; 本家族是 jiang_2021 单词典口径, 服务于跨词典梯子中的单臂, 二者虽共享同一 word-token 分母与同一状态机, 分子所用的词表并不同一, 在下游用法上分别对应共识测度与词典异质性测度, 不可互换。与词级 IDF 加权的 jiang_2021_idf_tone 及其价值、幅度、调和加权变体的区别是词权口径: 那一族用逆文档频率压低高频词的权重以抑制常见词噪声, 与本家族的等权计数互为稳健性、不分主次; 本家族刻意保持每个命中词一票的最简等权口径以便解释与审计。与 jiang_2021_neg_count 计数族的区别是测量层级: 计数族数的是被该词典判为负面篇的文章篇数, 单位是篇, 分母语境是银行-年篇数; 本家族数的是词, 篇内密度先行、篇间等权, 对篇内负面信息的强弱分辨率更高。与 msent 计数族的区别是规则口径: msent 按原始词典极性零规则计数, 不好中的好会被计为正面; 本家族按否定校正后的最终极性计数。与 BERT 概率轨的极端负面占比族的区别在测量机制: 那是神经分类器概率阈值口径, 阈值语义随模型而异、跨模型不可比水平; 本家族是透明可审计的词表匹配, 任何一次计数都可回溯到具体词条与具体规则触发。最后, avg_jiang_2021_pos_ratio 是本家族的正面孪生, 两者共享分母与规则口径, 建议成对进入描述统计与回归以保持极性对称、避免单侧选择性报告。

【已知局限与稳健性梯子】
本家族的已知局限与对应的稳健性安排如下。词表覆盖域局限: jiang_2021 词表脱胎于面向公司披露语域的英文 Loughran-McDonald 词典, 经翻译并本土化扩充后应用于新闻语域 — 原始发布的正面表三千三百三十八条、负面表五千八百九十条, 类内去重后为三千一百九十四条与五千六百二十一条、类间刻意不去重, 负面表规模约为正面表的一点七六倍, 这一负面偏重的结构本身即呼应 Loughran 与 McDonald (2011) 负面词信息优先的发现; 但媒体特有的口语化与修辞性负面表达仍可能欠覆盖。对策是六部词典的平行列族, 其中 yao_2021 含社交媒体子表、du_2022 含政治语域扩充词, 六部词典各自产出同构的负面密度列, 跨词典系数方向一致性是本家族最主要的稳健性证据; Ma, Zhang 与 Zhang (2025) 所代表的新一代中文细粒度词典也提示词表选择是持续存在且仍在演化的研究者自由度, 这正是仓库同时物化多部词典而非独尊一部的动机。分词依赖局限: 中文比率的分子与分母都建立在 jieba 分词之上, 分词错误会直接进入测度; 仓库以冻结的分词器版本锚定跨机跨期可复现性, 但无法消除分词器本身的系统性偏差, 跨方法并排的大模型轨与 BERT 轨不依赖显式的词表分词, 恰好构成对这一风险的外部校验。规则启发式局限: 否定窗口取其后两个分词单元是启发式选择, 超窗否定、双重否定与反讽不被捕获, 跨类重叠的二十一个词按项目决策两侧同计而非择一, 也是一处显式的测量选择; 由于比率对程度与转折两条幅度规则天然不敏感, 这一局限集中于否定一条规则, 与语调侧的规则消融梯子的证据互补。等权聚合局限: 篇级等权均值不区分媒体权威度与传播量, 一篇小报短讯与一篇权威长篇权重相同; 语调列族另设有媒体加权臂可作参照, 比率族刻意保持最简等权口径以便解释, 加权敏感性应在语调侧检验后外推。样本深度局限: 早期试跑环境仅为两年的迷你面板, 年内篇数稀薄时篇级均值方差偏大, 生产环境十九年全量语料下自然缓解; 任何面板实测的分布特征一律以引擎注入的动态统计段为准, 本文不手填数字。规格空间局限: 词典选择、轨道选择、聚合方式共同张成一个不小的规格空间, 处理哲学遵循多重宇宙分析思路 — 把每个规格物化为独立列、在论文层做规格并排而非规格挑选, 从源头消除抽屉问题, Valdenegro 等 (2025) 的规格曲线与模型平均工具族正是这一思路的当代工程化表达。最后重申口径铁律: full、ctx、ss 三轨各自 just-identified 并排, 六词典各臂并排, 词典法与大模型法、BERT 法并排, 一律互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 本家族属词典法非嵌入测度, 依 carve-out 口径不存在 _lg 孪生列, 与嵌入模型更换零耦合。

## VAR: avg_jiang_2021_neg_ratio_ctx

【变体差分】
本列是家族的实体窗口轨稳健性臂, tier 为 standard, 与 canonical 全文轨的唯一差分是测量文本域: 篇级输入为 content_ctx, 即标题前置拼接目标银行实体上下文窗口文本, 词典、语言学规则、跨类重叠词处理、word-token 分母与六位小数取整口径同 canonical 逐字节一致。设该轨的动机是归因降噪: 银行新闻常见多主体长篇综述, 全文轨会把同篇中论及其他银行或宏观环境的负面段落一并计入目标银行的负面密度, 实体窗口轨把测量域收窄到目标银行实体附近, 负面词与目标银行的归因链条更短、属性错配噪声更小, 代价是文本量收缩后单篇估计的抽样方差增大。行宇宙口径遵循 full-only 留篇门控: 一篇文章是否留存只看 full 轨的大模型验证结论, 本列是该留篇集上的条件测度, 即行宇宙为 full 留篇集子集、逐轨列照算。当一篇文章无法构造实体窗口时按回退语义使用全文正文并置回退旗标, 回退篇上本列与全文轨机械收敛属预期而非发现, 解读时应结合回退旗标占比。使用口径遵守家族铁律: ctx 轨与 full、ss 轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 本列不充当主测度, 其价值在于检验全文轨结论对归因口径收紧是否定性稳健。

## VAR: avg_jiang_2021_neg_ratio_full

【变体差分】
本列是家族 canonical 主列, tier 为 core, 签核依据为词典负面成分占比在 Loughran-McDonald 分解成分族中的代表地位: 在跨词典梯子中 jiang_2021 列于六部词典之首, 其负面词表规模在六部中最大, 且姜富伟等 (2021) 的中文媒体语料验证使其成为与本仓库新闻语域最贴合的单词典负面密度代表, 故本列被选为该构念进入 core 深度文档的锚点列。轨道语义上, full 轨的篇级输入为 content_full, 即标题前置拼接全文正文: 标题是中文财经报道情绪信号最浓缩的位置, 前置拼接使其进入分子分母而无须独立标题轨; 全文正文保证覆盖面最大、无回退问题, 本轨不存在回退旗标, 是三轨中唯一文本域天然完整的轨道。门控语义上, 本列具有三轨中独有的自洽性: 全仓 full-only 留篇门控本身即以 full 轨的大模型验证结论定义行宇宙, 因此本列是门控轨与测量轨重合的列, 其分母语境与家族篇数口径同源, ctx 与 ss 列则是同一留篇集上的条件测度, 其行宇宙为 full 留篇集的子集。计算口径上, 篇级值为 jiang_2021 词典命中且否定校正后最终得分为负的 token 数除以剔除纯标点纯数字后的有效词 token 数, 二十一个跨类重叠词两侧同计, 银行-年内等权均值聚合, 缺测为缺失值而非零; 分子取自单一 jiang_2021 词典的负面计数, 与无前缀并集口径的 avg_neg_ratio 虽共用同一 word-token 分母却用不同词表计数, 二者不可互相替换。解释口径上, 本列取值为词汇密度, 理论值域为零到一, 实际取值贴近零端且右偏, 系数的原始单位含义是负面词密度提高一个单位对应的结果变化, 该单位对应全篇皆负面词的极端情形, 故原始系数尺度不宜直接口语化解读, 实证报告建议以标准化系数为主、原始系数为辅, 并与正面孪生列 avg_jiang_2021_pos_ratio 成对呈现以保持极性对称、避免单侧选择性报告。构造敏感性上, 本列的负面计数在构造上只吸收否定翻转一条规则, 对程度副词与转折两条幅度规则完全不敏感 (二者的乘数恒为正、永不改变符号), 因此本列近似否定校正后的负面词计数密度, 无须另设规则消融臂; 二十一个跨类重叠词按项目决策两侧同计, 使这类正负兼具的词条在本列分子中按一票计入负面侧, 对应决策口径把净语调拉向中性而非武断选边。下游用法上, 本列是词级媒体分歧测度的直接输入, 也是净语调机制拆解中负面侧的承担者: 当 jiang_2021_tone 净语调系数显著时, 用本列与其正面孪生列分别替换重估, 即可回答效应由负面侧还是正面侧驱动。样本深度上, 早期试跑环境仅两年迷你面板, 银行-年内篇数稀薄时篇级等权均值的抽样方差偏大, 生产环境十九年全量语料下自然缓解; 任何本列的面板实测分布特征一律以引擎注入的动态统计段为准, 本文不手填数字。可复现口径上, 本列全链路零 API 成本、纯 CPU 确定性计算, 确定性锚为冻结的 jieba 分词器版本与冻结的 jiang_2021 词表文件, 换嵌入模型、换情感大模型对本列均零影响。使用铁律与家族一致: 本列与 ctx、ss 两列各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 与其余五部词典的同构负面密度列亦并排不混, 跨词典方向一致性由论文层规格并排呈现; 本列属词典法非嵌入测度, 依 carve-out 口径无 _lg 孪生列。

## VAR: avg_jiang_2021_neg_ratio_ss

【变体差分】
本列是家族的同句共现轨稳健性臂, tier 为 standard, 归因口径在三轨中最严: 篇级输入为 content_ss, 即标题前置拼接银行与金融科技词在同一句内共现的句子及其前后邻句窗口, 窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制、默认为一句; 该键与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同的配置键, 前者定义 ss 轨文本域、后者定义留行判据, 不可混淆。设该轨的动机是把负面密度测量钉死在银行与金融科技议题直接交汇的最小语义单元上, 排除同篇中与金融科技无关的银行负面叙事, 使本列逼近银行金融科技叙事本身的负面浓度这一更窄构念。回退语义镜像 ctx 轨: 当一篇文章不存在银行与金融科技词的同句共现时, content_ss 回退为全文正文并将回退旗标置真, 与家族共享篇数分母; 金融科技词表不可用时全部旗标置真、优雅降级。回退占比越高, 本列与全文轨的机械收敛越强, 解读时须结合回退旗标占比区分测度收敛与构念收敛。词典、规则与分母口径同 canonical 逐字节一致, 行宇宙为 full-only 留篇集子集。使用铁律同家族: ss 轨与 full、ctx 轨各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. Journal of Economics and Development, 27(4), 309-321. https://doi.org/10.1108/JED-06-2025-0296
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Valdenegro, D., Yan, J., Dai, D., & Rahal, C. (2025). RobustiPy: An efficient next generation multiversal library with model selection, averaging, resampling, and explainable artificial intelligence. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.19958
Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. Applied Economics, Advance online publication. https://doi.org/10.1080/00036846.2025.2536881
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Jiang, F., Lee, J., Martin, X., & Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Garcia, D. (2013). Sentiment during recessions. The Journal of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
