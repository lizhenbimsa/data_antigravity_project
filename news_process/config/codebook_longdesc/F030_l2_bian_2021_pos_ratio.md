---
family_id: F030
columns:
- avg_bian_2021_pos_ratio_ctx
- avg_bian_2021_pos_ratio_full
- avg_bian_2021_pos_ratio_ss
unit: 比率 (正面词占 word-token 数之比, 无量纲, 值域 [0,1]; 面板层为文章级比率的银行-年算术均值)
formula: "文章级: bian_2021_pos_ratio_trk = pos_cnt_trk / n_word_tokens_trk, trk ∈ {full, ctx, ss}; 分子 = bian_2021 (CFSD) 词典命中且经语言学规则 (否定翻转窗口 2 / 程度副词六级权重 / 转折加权) 处理后 final_score > 0 的 token 数, 分母 = 剔除纯标点/纯数字 token 后的 word-token 数, round 6 位; 空文本/无 word-token/词典缺失 → NaN。面板级: avg_bian_2021_pos_ratio_trk = 银行-年组内文章级比率的算术均值 (pandas mean, skipna), 行宇宙 = llm_verified_full 留篇门控 (full-only, 2026-06-29)"
producer: news_process/pipeline/sentiment/tone_words.py::_analyze_single_article + _compute_sentiment_with_rules (文章级三轨) ; news_process/pipeline/panel/encode.py 单词典 pos_ratio/neg_ratio 聚合段 (面板 avg_ 均值)
upstream:
- "config/tone_dicts.json (bian_2021 词典本体, CFSD 2,595 词: 正面 1,107 / 负面 1,488)"
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本物化)
- 21_tone_llms.parquet (llm_verified_full 留篇门控 + stage 22 输入)
- 22_tone_words.parquet (文章级 bian_2021_pos_ratio 三轨中间列)
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
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: "100148"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: The Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
- doi: 10.1093/qje/qjx045
  type: journal
  authors: Hansen, S., McMahon, M., & Prat, A.
  year: 2018
  title: "Transparency and deliberation within the FOMC: A computational linguistics approach"
  venue: The Quarterly Journal of Economics
  vol: 133
  issue: 2
  pages_or_artno: 801-870
- doi: 10.1086/693096
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2017
  title: "Political bias in corporate news: The role of conglomeration reform in China"
  venue: The Journal of Law and Economics
  vol: 60
  issue: 1
  pages_or_artno: 173-207
- doi: 10.1111/jofi.12027
  type: journal
  authors: Garcia, D.
  year: 2013
  title: "Sentiment during recessions"
  venue: The Journal of Finance
  vol: 68
  issue: 3
  pages_or_artno: 1267-1300
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: "10.1016/j.jfineco.2022.11.006"
  type: journal
  authors: "García, D., Hu, X., & Rohrer, M."
  year: 2023
  title: "The colour of finance words"
  venue: "Journal of Financial Economics"
- doi: "10.1016/j.ribaf.2025.102881"
  type: journal
  authors: "Wei, L., Wei, M., Jing, H., & Jing, Z."
  year: 2025
  title: "Annual report tone and bank risk-taking behavior: Evidence from China"
  venue: "Research in International Business and Finance"
- doi: "10.1002/mde.70100"
  title: "The Textual Tone of Annual Reports and Market Attention: Evidence From Chinese Listed Companies"
  authors: "Li, Y."
  year: 2026
  venue: "Managerial and Decision Economics"
  type: "journal"
- doi: "10.3390/bdcc9100263"
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  venue: "Big Data and Cognitive Computing"
  type: "journal"
new_dois:
- 10.1111/jofi.12027
- 10.1111/j.1540-6261.2010.01625.x
- "10.1016/j.jfineco.2022.11.006"
- "10.1016/j.ribaf.2025.102881"
- "10.1002/mde.70100"
- "10.3390/bdcc9100263"
---

## CORE

【构念与来源】
本家族测量的构念是"目标银行相关新闻报道中的正面语调词密度": 在一篇被判定为银行金融科技报道的新闻文本里, 按 Bian 等 (2021) 中文金融情感词典 (Chinese Financial Sentiment Dictionary, 简称 CFSD) 判定为正面、且经语言学规则修正后最终得分仍为正向的词汇, 占该文全部有效词元的比例。面板层三列 avg_bian_2021_pos_ratio_full、avg_bian_2021_pos_ratio_ctx 与 avg_bian_2021_pos_ratio_ss 分别是这一文章级比率在全文轨、实体窗轨与同句轨三条文本轨道上的银行-年算术均值。构念的方法论出发点是金融文本情感文献中的极性分离原则: Garcia (2013) 在研究衰退期媒体情感对股票收益的预测力时明确指出, 将正面词频与负面词频拆成两个独立协变量, 优于只用一个"正减负"的净情感指标, 因为净指标会把"正负两面都说得很多的争议性报道"与"两面都几乎不提的中性报道"压缩到同一个零点附近, 产生极性对冲掩蔽。本家族正是这一分解的正面分量, 与孪生家族 avg_bian_2021_neg_ratio 的负面分量成对存在: 二者共享分母与规则链、仅分子取向相反, 供下游回归以正负分离形式进入, 也为词级情感分歧指标提供正侧输入。之所以选取"密度"而非"净分"作为该分量的度量, 是因为密度对报道篇幅做了显式归一, 使一篇偶尔出现正面词的长篇报道与一篇通篇褒扬的短讯不会因绝对词数悬殊而错位, 从而保留横截面上银行间正面基调强度的可比性。

词典本体来自 Bian 等 (2021) 面向会计与金融文本分析构建的 CFSD。原始词表以 word 加 sentiment 两列的形式给出 (取值 1 表正面、-1 表负面), 清洗去重后得到 2,595 个唯一词条, 其中正面词 1,107 个、负面词 1,488 个; 项目侧的单一事实源是 config/tone_dicts.json 的 bian_2021 键, 词表字节随仓库版本冻结管理。需要向使用者披露一处年份口径警示: 该词典官方数据仓库命名含 2019 字样, 说明词表初版在 2019 年即已流通, 而项目统一按其工作论文 2021 年 6 月定稿版本命名为 bian_2021 并按 2021 年引注; 引注应以定稿年份为准, 但讨论词表所覆盖的时代范围时须意识到词条遴选所依据的语料可能更早。CFSD 在管道中是六部并排的中文金融情感词典之一, 其余五部为姜富伟等 2021 词典、姚加权等 2021 词典、Du 等 (2022) 含政治正面词的扩充词典、You 等 2018 词典, 以及 Loughran 与 McDonald (2011) 词典的中文主译本; 六部词典同构念、异词表, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把任意两部及以上混进同一条 over-identified 的 Hansen J 检验。CFSD 在这六部中是词条最精简的一部, 其价值不在覆盖广度而在"精选核心情感词"的视角, 与词条更繁的词典形成粒度互补。

【方法学与计算】
计算链路分文章级与面板级两层。文章级在 stage 22 词典情感阶段由 _analyze_single_article 逐篇完成: 输入是 stage 21 输出的报道集合, 全文轨、实体窗轨与同句轨三份文本列已在 stage 14 物化 (标题以 prepend 方式并入正文头部, 三轨共享同一标题通道, 原始"内容"列不被改写; 更上游的 stage 13 共现硬过滤只按银行与金融科技词的邻近共现丢行、不物化任何文本列)。分词采用字节冻结的 jieba 0.42.1, 并使用与全局分词器隔离的独立 tone tokenizer, 使领域词注入不污染其他阶段的切分; 同一文本只切一次、六部词典共享同一分词序列, 整条链路零 API 成本、纯 CPU 且确定性可复现 (确定性锚 = jieba 版本加词典文件字节)。分母 n_word_tokens 采用 word-token 口径: 剔除纯标点与纯数字 token 之后的词元数, 与本仓库对 Loughran-McDonald 词类比率与前瞻性陈述比率的分母修复完全同口径, 对应 Loughran 与 McDonald (2011) 原文"词数占比"的分母定义; 若不剔除标点与数字, 二者在不同文章间的占比波动会构成非常数稀释, 系统性压低并扭曲比率的横截面可比性。

分子 pos_cnt 来自逐 token 状态机 _compute_sentiment_with_rules: 扫描分词序列时维护否定窗口、程度倍率、转折激活三个状态; 遇否定词在其后两个分词单元的窗口内翻转情感词极性 (窗口长度固定为 2), 遇程度副词按六级权重设定倍率, 遇转折连词激活转折加权 (默认放大系数 1.5), 遇句末标点将全部句法状态清零以避免跨句串味 (从句级作用域)。一个 token 命中 bian_2021 词表后, 其 final 得分为词典基础极性经否定翻转、程度缩放与转折放大后的值, final 大于零者计入 pos_cnt、小于零者计入 neg_cnt。由于程度副词与转折加权只缩放幅度而不改变符号, 真正能改变计数归属的只有否定翻转: 词典正面词落入否定窗口会翻成负向而移出 pos_cnt, 词典负面词被否定则翻正计入 pos_cnt, 因此本测度是"规则修正后的正面命中密度", 而非裸词表命中计数, 这与完全零规则的纯计数型指标构成实质差异。

有两点契约值得写明。其一, 管道对部分词典存在的正负跨类重叠词按"保留且两侧同时计数"处理 (对净分贡献为零、对归一化分母贡献两倍幅值, 把该词语调拉向中性而非武断选边剔除); 但 CFSD 本身正负集合的交集为空、无跨类重叠词, 该机制对本家族是空集, 不产生任何计数影响, 使得本家族的正面计数是纯粹的单侧计数。其二, 缺失语义采用 NaN 而非零: 空文本、纯符号文本、分词后无有效 word-token、或词典加载缺失时, 文章级值一律置 NaN, 绝不以零冒充"测得无正面词", 这保证了后续均值聚合不会被伪零系统性拉低。文章级比率按六位小数舍入落盘, 三轨各成一列。面板级在 panel 编码层的单词典 pos_ratio/neg_ratio 聚合段完成: 按银行乘年份分组, 对组内文章级比率取算术均值 (pandas mean, 跳过 NaN), 得 avg_bian_2021_pos_ratio 三轨列。聚合行宇宙遵循 2026-06-29 起生效的 full-only 留篇门控: 一篇报道是否进入银行-年聚合只由全文轨 LLM 复核通过与否决定, 实体窗轨与同句轨作为 conditional-on-full 的测度轨在同一行宇宙内逐轨取值, 不另设独立的留篇判定。面板下游的直接消费者是词级情感分歧指标 (disag_bian_2021 三轨列): 以本列与负面孪生列为输入, 度量正负语调在银行-年内的对冲程度, 分母为正负比率之和、和为零时置 NaN。另一处诊断性消费在面板导出层的距离衰减敏感性检验: bian_2021 与其余五部词典一道进入 uniform 对 inverse 暴露加权的相关性诊断清单, 用于披露衰减权重设定是否影响词典族测度。

【文献定位】
本家族在文献坐标系中位于三条线的交点。第一条是金融文本词典法的主谱系: Loughran 与 McDonald (2011) 确立了领域专用词典相对通用词典的必要性, 指出通用负面词表在财务语境下大量误判, 也定义了"词数占比"这一分母口径, 本家族的 word-token 分母正是其中文实现; Garcia (2013) 确立了正负极性分离的计量形式, 本家族即其正面分量在中文银行新闻语境下的词典实现; Hansen、McMahon 与 Prat (2018) 则代表文本即数据方法在央行与金融机构沟通研究中的规范化, 说明基于透明规则的文本测度在顶级期刊识别设计中的可用性。第二条是中文金融情感词典的本土化谱系: Du 等 (2022) 系统论证了"语言与领域双重特异性", 表明把英文词典机械翻译到中文金融语境会同时丢失语言习惯与领域语义, 必须以中文金融语料重建词表, 这为项目并排使用六部中文词典而非单一译本提供了直接依据; Bian 等 (2021) 的 CFSD 是这一谱系中面向会计与金融文本分析的专门词典, 也即本家族的词表来源; Ma、Zhang 与 Zhang (2025) 构建的面向中国境内投资者的细粒度情感词典代表该谱系的最新进展, 其对词典粒度与应用场景的讨论可作为本家族词表粒度局限的对照; Sun、Yuan 与 Xu (2025) 则展示了词典知识与预训练语言模型融合的混合路线, 呼应本仓库词典轨、LLM 轨与 BERT 轨并行的三法互稳设计。第三条是银行与媒体情感的应用文献: Fang 等 (2024) 用中国银行业语料证明媒体情感影响存款稳定性并传导至系统性风险, 与本面板"银行-年媒体语调"的构念直接同域; Chen、Goldstein、Huang 与 Vashishtha (2022) 表明银行信息环境的透明度实质影响存款人行为, 为"新闻文本的正面强度是银行信息环境的可测维度"提供理论支点; Anastasiou、Katsafados 与 Tzomakas (2026) 以文本特征预测银行股价崩盘风险, 说明银行文本情感分量在风险预测语境下具有独立信息含量。方法效度层面, van Atteveldt、van der Velden 与 Boukes (2021) 对人工标注、众包、词典法与机器学习做系统比较, 提示词典法效度存在天花板, 这正是本家族被定位为稳健性旁证而非 canonical 主测度的文献依据; Li、Mai、Shen 与 Yan (2021) 的机器学习文化测度则从反面说明: 当研究需要可解释、可审计、跨研究者完全可复现的测度时, 固定词表方法仍不可替代。制度语境层面, Piotroski、Wong 与 Zhang (2017) 记录了中国企业新闻的政治性偏差结构, 提示中文财经媒体的正面基调含制度性成分, 解读本列水平值时必须结合固定效应设计。García, Hu 与 Rohrer (2023, Journal of Financial Economics) 用机器学习方法系统精炼与扩充金融情感词典并证明其显著优于传统词典的样本外预测力, 为本家族精选核心情感词表决定测度信噪比的局限讨论提供最新方法论对照。Wei, Wei, Jing 与 Jing (2025, Research in International Business and Finance) 以中国上市银行年报语调测度正面基调与银行风险承担行为的关系, 为本家族银行相关文本正面语调密度的构念在中国银行业语境下提供最新应用文献支点。Li (2026, Managerial and Decision Economics) 以中国上市公司年报文本语调为测度, 检验其与市场关注度之间的关系, 为本家族银行相关文本正面语调密度构念在中国资本市场语境下提供最新应用文献支点。Chuang, He 与 Hu (2025, Big Data and Cognitive Computing) 系统比较词典法与多种词嵌入及语言模型在中文财经新闻情感分类与股价预测中的表现, 为词典法情感测度提供跨方法对照基准。

【识别策略定位】
在识别策略中, 本家族属于语调族处理变量的稳健性层而非 canonical 主轨: 主线论文 (P1, bank_fintech_tone) 的 canonical 处理变量是三家 LLM 多数投票的 llm_vote_tone_full, 词典法六部与 BERT 三模型是与之平行的两条替代方法族, 三方法互为三角验证——词典法以透明、确定性、零边际成本、可逐字节复现的规则测度身份为其提供跨方法旁证; 若 LLM 语调效应在 bian_2021 正面密度上重现同号显著, 则主结论不依赖任一测量技术的独有偏差。项目在此执行严格的并排口径铁律: 三条文本轨各自 just-identified 并排, 六部词典各自 just-identified 并排, 词典法、LLM 法与 BERT 法三法并排, 正面与负面分量成对并排, 全部互为稳健性、不分主次, 严禁把任意两个及以上变体混进同一条 over-identified 的 Hansen J 检验矩条件中——这些变体是同一构念的替代测量而非相互独立的工具变量, 混用会让过度识别检验在机械相关下失去统计含义。落到回归实践, 正确用法是每次以一个变体替换主测度重估全式并报告系数带, 或以正负分量同时进入同一条 OLS 式做极性分解, 而不是把多轨多词典塞进 GMM。

须进一步写明词典族在多重检验校正上的定位: 项目的跨模型 family-wise 校正模板 (根级 27_tableA12 的 rwolf) 只覆盖"同构念替代 headline 测量"的场景, 即 LLM 三家与 BERT 三模型对同一 canonical headline 的平行测量; 词典乘文本轨的密度族属于"规格稳健性并排"性质, 不进入该 rwolf 矩阵, 报告时以逐规格并排表呈现即可, 不设专门的 family-wise 校正模板。这与政治词权重梯度、规则消融梯度的处理一脉相承: 它们都是同一构念的规格自由度探查, 以"定性不变"为叙事目标, 而非彼此独立的假设检验族; 也正因如此, 六词典乘三轨乘正负的整个密度矩阵在论文里以并排稳健性表而非联合检验的形式呈现, 读者据以直接读出主结论对词典与轨道选择的敏感性。

另一处与识别直接相关的口径是行宇宙: 面板聚合遵循 full-only 留篇门控 (2026-06-29 生效), 全文轨 LLM 复核通过的报道构成唯一的银行-年报道集合, 实体窗轨与同句轨是该集合上的 conditional-on-full 测度轨、在同一行宇宙内逐轨取值, 不另设独立的留篇判定; 因此三列之间的差异纯粹来自文本视窗的收窄, 不混入样本构成差异, 三轨对比可被解读为"归因精度梯子"而非样本选择效应。识别读数上, 全文轨作为覆盖最宽口径通常承担正面语境的上界暴露角色: 若某关系在最宽的 full 轨上成立、随 ctx 与 ss 逐步收窄而衰减, 提示正面基调的作用主要来自泛化背景而非银行专属叙述; 反之若收窄轨上不减反增, 则提示正面信号高度聚焦于银行与金融科技议题的直接交汇处——但这一单调性读数只在三轨各自独立入模时才成立, 严禁在过度识别方程内比较三轨系数大小。本家族还作为词级分歧指标的输入间接进入机制分析: disag_bian_2021 三轨列以本列与负面孪生列为对称输入 (分母为正负比率之和、和为零时置 NaN), 故本列的测量质量直接决定分歧构念的可信度; 此外本列进入面板导出层的距离衰减敏感性诊断, 与其余五部词典一道核验 uniform 对 inverse 暴露加权下词典族测度是否稳定, 若两种加权高度相关即说明衰减权重设定不驱动结论。

【与相邻测度的构念区分】
第一, 与孪生列 avg_bian_2021_neg_ratio 的区分是极性方向: 两列共享同一分母 (全篇 word-token 数) 与同一规则链, 仅分子分别取规则修正后 final 为正与为负的命中数, 二者相加不等于总命中率且互不冗余, 按 Garcia (2013) 的分离设计应成对使用、不合成净值。第二, 与跨词典聚合列 avg_pos_ratio 的区分是词表基与聚合孪生: 后者的分子来自六词典固定 union 词表 (并集加极性多数票消解、平票剔除) 的命中计数, 体现固定词表的总量口径、兑现 Tetlock 2007 与 Garcia 2013 的固定词表构念, 且另有 avg_pos_ratio_std 组内离散度孪生; 本列只用 bian_2021 单一词表、是 union 口径的单词典分解臂, 度量该词典独有的词汇视角, 聚合层只有均值、无 _std 孪生 (encode 层对单词典 pos_ratio 仅聚合 mean), 二者是"单词典分量"与"联合词表总量"的关系。第三, 与净语调列 bian_2021_tone 及其源头 bian_2021_score 的区分是量纲与边际类型: 净语调是幅度加权的自归一化净分 (加权得分之代数和除以加权绝对值之和), 值域负一到正一, 度量已命中词内部的净极性方向, 属集约边际; 本列是密度, 分母为全篇有效词元数, 度量正面词相对全文长度的覆盖强度, 属广延边际, 一篇只有两个正面词、无负面词的长文净语调为满分正一而正面密度极低, 两列刻画的是不同物理量。第四, 与计数型 msent_score 的区分是规则层与词表基: msent 用原始词典极性 (base 字段) 零规则计数且基于 union 词表, 本列用规则修正后 final 极性且基于单词典, 两者对含否定的句子 (如"盈利没有改善") 归类相反。第五, 与规则消融梯度、政治词权重梯度、IDF 加权与 Z 标准化族的关系是刻意不交叉: 这些变体只对 score 族物化, pos_ratio 族恒在全规则、等权、原始尺度口径下计算, 不设任何消融或加权孪生列, 以避免列空间组合爆炸; 引用时切勿虚构 bian_2021_pos_ratio_negonly 之类不存在的列名。第六, 与 BERT 判正计数族及 LLM 判正计数族的区分是测量单位: 那些族按篇章分类结果计数 (一篇算一票), 本列按词元计数 (一词算一次), 前者是文档级分类器输出、后者是词级规则输出, 分别位于测量粒度谱的两端; 与 industry 同业冲击族的区分则在主体, 后者以 leave-one-out 口径度量同业其他银行的报道极性暴露, 与本列的自身密度构念正交。

【已知局限与稳健性梯子】
已知局限有七点。一是词表覆盖: CFSD 正面词 1,107 个, 是六部词典中词条最少的一档, 稀疏词表使低命中文章的比率取整粒度偏粗、组内方差被小分子整数化放大; 这既是缺点也是特色——它提供"精选核心情感词"视角, 与大词表词典形成粒度互补, 对策是六词典并排换用其余五部同名密度列检验符号与显著性稳定性。二是二值极性: 词条只有正负两档、无幅度分级, 强弱正面词在分子中同权, 幅度信息只能由 score 族的程度副词机制间接补偿, 也正是 Ma、Zhang 与 Zhang (2025) 细粒度词典所针对的局限。三是正面侧的信噪比劣势: Loughran 与 McDonald (2011) 指出金融披露文本中正面词常被管理层用于粉饰、与后续市场反应的相关弱于负面词, 故正面密度是极性分解中信息含量偏弱的一侧; 本列的价值不在单独承重, 而在按 Garcia (2013) 的分离逻辑充当负面侧的必要正面补集, 并为分歧指标提供正侧输入。四是制度性正面基率: 中文财经媒体存在政治与商业双重来源的正面倾向 (Piotroski、Wong 与 Zhang 2017 的证据), 本列水平值含制度成分, 跨行水平比较须谨慎, 推荐在银行与年份双固定效应内解读组内变异。五是时代漂移: 词表定稿于 2021 年而语料覆盖 2007 至 2024 年, 对后期新词 (如金融科技术语的褒义用法) 覆盖不足会造成后期正面密度的系统性低测, 年份固定效应可吸收共同漂移但吸收不了银行间差异化漂移。六是分词误差与否定近似: jieba 对金融新词与机构名的切分错误会同时污染分子与分母, 版本冻结保证误差确定但不消除误差本身; 固定两词元的否定窗口无法覆盖长距离否定、双重否定与反讽 (van Atteveldt、van der Velden 与 Boukes 2021), 中文口语化的先扬后抑只能由转折加权部分捕捉。七是等权篇均与无守门: 文章级比率虽已对篇幅做密度归一, 但银行-年聚合是篇均等权 (每篇一票、与篇幅无关), 报道量极少的银行-年上单篇极端值即可主导均值, 且本族不设最小篇数守门 (与 industry_neg_shock 的守门口径不同), 回归中应控制报道量或对低篇数单元做敏感性剔除; 报道数量维度由 n_articles 独立承载, 与本列的密度维度正交, 不可将本列水平上升误读为"获得更多正面报道"。针对这些局限, 家族置身于多级正交稳健性梯子: 轨道梯 (全文、实体窗、同句三轨收窄归因范围), 词典梯 (六部词典同构念异词表并排), 词表基梯 (单词典对 union 固定词表), 方法梯 (词典对 LLM 对 BERT 三法), 极性梯 (正负分量成对), 以及下游分歧指标对正负输入的二次校验; 每一级梯子上的变体均各自 just-identified 并排、互为稳健性不分主次, 一律禁混同一 over-identified Hansen J, 梯子间正交不交叉。同句轨的回退语义须按仓库口径复述: 当一篇报道内不存在银行与金融科技词的同句共现时, 同句轨文本回退为全文正文并置 ss_is_fallback 为真, 与实体窗轨的回退设计互为镜像, 共享同一 n_articles 分母; 金融科技自动机缺失时全部回退标记置真并优雅降级, 不会静默清空样本, 这些回退行上同句轨密度与全文轨密度机械趋同属设计内语义、非泄漏, 严格窗口子样本分析应按 fallback 标记切分。开发盘 T 等于 2 的试跑环境下, 同句轨可能整列退化为缺测或零方差、稀疏格上比率取整跳变明显, 均属预期退化, 生产口径以 T 等于 18 全量语料为准。

## VAR: avg_bian_2021_pos_ratio_full

【变体差分】
本列是家族的 canonical 全文轨与唯一 core 列, 入选理由是词典法极性分解族在 canonical 轨上的代表列 (类别六扩围①, 2026-07-10 签核): 在六词典乘三轨乘正负两极的列空间中, 全文轨的 bian_2021 正面分量被选为该子族的核心档案列。差分语义上, 本列与家族内另两列的唯一区别是文本视窗: 分词与规则打分作用于 content_full, 即 prepend 的标题加全部正文, 不做任何以目标银行或金融科技词为锚的截取, 因此它度量的是"整篇报道的正面词密度", 把报道中与目标银行无直接关系的宏观叙事、行业背景、其他机构动态的正面用词一并计入。选择 full 轨作 canonical 有三层理由。第一是与门控口径的自洽: 2026-06-29 起留篇门控为 full-only, 一篇报道是否算"银行金融科技报道"只看 llm_verified_full, 因此全文轨测度的行宇宙与门控判据同轨、分母定义最干净, 本列与该门控在同一文本对象上定义、无跨轨错位; ctx 与 ss 是该留篇集上的 conditional-on-full 收窄轨, 其行宇宙是全文留篇集的子集。第二是与文献的可比性: 英文金融文本文献的词类占比变量 (Loughran 与 McDonald 2011 谱系及 Garcia 2013 的正负分离设计) 均以全文为分母, 全文轨与其构念对齐、便于系数量级对话, 且项目主线 P1 的处理变量 llm_vote_tone_full 亦为全文轨, 本列作其词典法正侧稳健臂时两者口径同轨、不引入轨道混淆。第三是回退中性: 全文轨不存在回退语义, 每篇文章的取值都来自真实全文, 无 fallback 行与非 fallback 行的异质混合, 这使全文轨成为三轨中唯一没有机械趋同污染的口径, 分母也通常最大、单篇比率方差相对最小, 因而在报道量偏低的银行-年上比收窄轨更稳定、更少被极短文本的零一跳变主导。计算细节与家族口径完全一致: 分子为 bian_2021 词表命中且规则修正后 final 仍为正向的词元数 (否定窗口内的正面词被翻出、被否定的负面词被翻入; CFSD 正负集合交集为空, 两侧计数消歧分支对本词典不触发), 分母为剔除纯标点纯数字后的 word-token 数, 文章级六位小数, 银行-年内算术均值 (跳过 NaN), 缺失置 NaN 不冒充零。作为 core 列, 它在论文中的标准角色是: 在以 llm_vote_tone_full 为处理变量的主表之外, 于稳健性附表中以本列及其负面孪生列替换或分解语调测度, 检验"LLM 语调效应是否能被透明词典规则复现", 并为 disag_bian_2021_full 分歧指标提供正侧输入; 与其他五部词典的全文轨正面比率列并排时, 六列各自 just-identified 进入独立回归、互为稳健性、不分主次, 禁混同一 over-identified Hansen J, 词典族属规格稳健性并排、不进入跨模型 rwolf 的 FWER 矩阵。作为极性分解的正面分量, 本列在解读上有一个不能省略的配对约束: 它必须与 avg_bian_2021_neg_ratio_full 联读, 单看正面密度上升无法区分"报道整体更褒扬"与"报道更情绪化 (正负词都增多)"两种情形, 只有把正负两列同时纳入才能识别究竟是基调偏移还是情绪强度上升——这正是密度形式相对净语调形式的信息优势所在, 净语调会把后一种情形压回零点附近而丢失。还须写明正面侧的信噪比定位: 按 Loughran 与 McDonald (2011), 金融披露中的正面词更易被管理层用于粉饰、其信息含量弱于负面词, 故正面密度是极性分解中偏弱的一侧, 本列的价值不在单独承重, 而在充当负面侧的必要正面补集与分歧指标的正侧输入。就识别读数而言, 全文轨作为覆盖最宽口径承担正面语境的上界暴露角色: 若某关系在全文轨成立而随 ctx、ss 收窄衰减, 提示作用来自泛化背景; 若收窄轨上反而增强, 提示正面信号聚焦于银行与金融科技议题的直接交汇处; 该单调性读数只在三轨各自独立入模时成立, 严禁在过度识别方程内比较三轨系数大小。就组内解读而言, 某银行在相邻两年本列取值上升, 应读作"该行相关全文报道中每单位有效词元里判正的核心情感词增多", 而非"该行获得更多正面报道"; 后者是报道数量维度、由 n_articles 承载, 两者正交、分析时不可混淆。本列也进入距离衰减敏感性诊断: 与其余五部词典的全文轨测度一同参与 uniform 对 inverse 暴露加权的相关性核验, 若六部词典在两种加权下高度相关, 则说明词典族测度对衰减权重设定不敏感, 这一诊断是对全文轨测度稳定性的旁证。使用时的两点提示: 其一, 本列水平值受词表规模 (bian_2021 正面词 1,107 个, 在六部中最精简) 与中文媒体正面基率影响, 跨词典比较水平没有意义, 只应比较标准化系数或组内变异; 其二, 本列对报道长度已通过密度化控制, 但极短文本的比率方差天然偏大, 银行-年内的均值聚合部分平滑了这一噪声, 分析报道稀少的银行时仍建议结合报道数量列加权或设置最小篇数门槛。

## VAR: avg_bian_2021_pos_ratio_ctx

【变体差分】
本列是实体窗轨变体, tier 为 standard。与 canonical 全文轨的唯一差分是文本视窗: 打分对象为 content_ctx, 即 prepend 的标题加以目标银行实体提及为锚截取的邻域窗口文本, 度量"目标银行被点名的上下文邻域内"的正面词密度, 把远离银行提及的段落 (宏观评论、其他机构新闻) 从分子分母中同时剔除。相对全文轨, 它以覆盖换归因: 正面词与目标银行的语义关联更可信, 但窗口截取使分母收缩、小分子噪声上升, 且当一篇报道无法抽出有效实体窗口时按镜像回退语义以全文正文兜底并置回退标记, 该篇在本轨上与全文轨取值趋同。行宇宙口径须写明: 本列是 conditional-on-full 测度轨, 是否留篇仍由全文轨门控决定, 本列只在既留篇集合上逐轨取值, 因此它与全文轨列的差异纯粹反映视窗收窄而非样本变化。银行侧实体判定沿用不对称口径: 含否定与短名过滤, 避免"平安""光大"等歧义短名误锚窗口。用法上, 本列与全文轨、同句轨两列构成归因精度梯子, 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 若全文轨效应在本轨复现且幅度相当, 说明结果不由与银行无关的背景正面叙事驱动。本列同时是 disag_bian_2021_ctx 的正侧输入, 亦是六词典实体窗轨正面密度族的 bian 分解臂。

## VAR: avg_bian_2021_pos_ratio_ss

【变体差分】
本列是同句轨变体, tier 为 standard, 是三轨中归因最严的一档。差分语义: 打分对象为 content_ss, 即 prepend 的标题加"目标银行与至少一个金融科技词出现在同一句"的句子及其前后一句的窗口拼接 (窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认一句; 注意该键与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同的配置键, 前者管文本物化、后者管留行过滤, 勿混)。因此本列度量的是"银行与金融科技在句法层面直接绑定的叙事片段"内的正面词密度, 是对"报道正面性是否确实落在银行乘金融科技这一议题交点上"的最强归因检验。回退语义严格镜像实体窗轨: 当整篇报道不存在银行与金融科技词的同句共现时, content_ss 回退为全文正文并置 ss_is_fallback 为真, 与其余轨共享同一 n_articles 分母, 不因回退而丢样本; 金融科技词自动机缺失时全部回退标记置真、整轨优雅降级为全文口径。共现判定采用不对称口径: 银行侧走否定与短名过滤, 金融科技侧为裸自动机词表命中。本列是 conditional-on-full 测度轨, 留篇仍由全文轨门控决定。窗口极窄使分母最小、比率噪声最大, 在报道稀少的银行-年格上波动明显, 解读时应与回退占比信息联用。另须区分两处易混口径: 其一, 本轨的同句判据 (对应严格同句的 extract_bank_fintech_cooccurrence) 与 stage 13 共现硬过滤的 sentence_radius 是两套不同原语、两个不同 config 键, 禁互相复用; 其二, ss 后缀是文本轨后缀, 与网络指标族的 _sent 判据后缀无关。三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。本列同时是 disag_bian_2021_ss 的正侧输入。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. The Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news: The role of conglomeration reform in China. The Journal of Law and Economics, 60(1), 173-207. https://doi.org/10.1086/693096
Garcia, D. (2013). Sentiment during recessions. The Journal of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics. https://doi.org/10.1016/j.jfineco.2022.11.006
Wei, L., Wei, M., Jing, H., & Jing, Z. (2025). Annual report tone and bank risk-taking behavior: Evidence from China. Research in International Business and Finance. https://doi.org/10.1016/j.ribaf.2025.102881
Li, Y. (2026). The Textual Tone of Annual Reports and Market Attention: Evidence From Chinese Listed Companies. Managerial and Decision Economics. https://doi.org/10.1002/mde.70100
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
<!-- rendered-citations:end -->
