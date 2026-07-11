---
family_id: F037
columns:
- avg_du_2022_neg_ratio_ctx
- avg_du_2022_neg_ratio_full
- avg_du_2022_neg_ratio_ss
unit: 比率 (proportion, [0,1]; 银行-年内篇章级 du_2022 负面词占比的算术均值, 无量纲)
formula: "篇章级 du_2022_neg_ratio{trk} = neg_count_du2022{trk} / n_word_tokens{trk}, trk ∈ {_full,_ctx,_ss}; neg_count = 语言学规则状态机中 final_score < 0 的匹配词次 (否定翻转后按最终符号归类, 跨类重叠词两侧计数), n_word_tokens = 剔除纯标点/纯数字 token 后的词数 (_LMFLS_NONWORD_RE 口径), round 6; n_word_tokens = 0 或词典缺失 → NaN。面板级 avg_du_2022_neg_ratio{trk} = 银行-年格内篇章级比率的算术均值 (pandas mean, NaN 跳过; 行宇宙 = full-only 留篇集)"
producer: news_process/pipeline/sentiment/tone_words.py::_analyze_single_article + _compute_sentiment_with_rules (篇章级三轨) ; news_process/pipeline/panel/encode.py::build_aggregation_dict Section M → aggregate_panel (bank-year 均值聚合) ; news_process/pipeline/panel/stata_export.py (Stata 标签层)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本 + *_is_fallback 指示列)
- 22_tone_words.parquet (篇章级 du_2022_neg_ratio_{full,ctx,ss})
- 40_panel_yearly.parquet (本家族三列落盘)
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
- doi: 10.1108/JED-06-2025-0296
  type: journal
  authors: Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B.
  year: 2025
  title: "Investor negativity derived from news shapes firm distress dynamics under bounded rationality"
  venue: Journal of Economics and Development
  vol: 27
  issue: 4
  pages_or_artno: 309-321
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: Article 20
- doi: 10.48550/arXiv.2506.19958
  type: arxiv
  authors: Valdenegro, D., Yan, J., Dai, D., & Rahal, C.
  year: 2025
  title: "RobustiPy: An efficient next generation multiversal library with model selection, averaging, resampling, and explainable artificial intelligence"
  venue: arXiv
- doi: 10.1287/mnsc.2023.03556
  type: journal
  authors: Fišar, M., Greiner, B., Huber, C., Katok, E., Ozkes, A. I., & the Management Science Reproducibility Collaboration
  year: 2024
  title: "Reproducibility in Management Science"
  venue: Management Science
  vol: 70
  issue: 3
  pages_or_artno: 1343-1356
- doi: 10.1016/j.enpol.2023.113917
  type: journal
  authors: Xu, Z., Li, J., Hua, X., & Ren, P.
  year: 2024
  title: "Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry"
  venue: Energy Policy
  vol: 184
  pages_or_artno: Article 113917
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.iref.2021.03.009
  type: journal
  authors: Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J.
  year: 2021
  title: "Does fintech innovation improve bank efficiency? Evidence from China's banking industry"
  venue: International Review of Economics & Finance
  vol: 74
  pages_or_artno: 468-483
- doi: 10.18653/v1/d16-1057
  type: journal
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
new_dois: []
---

## CORE

【构念与来源】本家族测度的构念是银行金融科技新闻报道的负面词汇密度: 对进入面板的每一篇目标银行金融科技报道, 用 du_2022 中文金融情感词典在分词序列上逐词匹配, 统计经语言学规则判定后落在负面一侧的情感词词次, 除以该篇剔除纯标点与纯数字之后的有效词数, 得到篇章级负面词占比 du_2022_neg_ratio, 再在银行-年格内取算术均值, 落盘为面板列 avg_du_2022_neg_ratio 的三轨形态。构念内核是媒体文本情感文献里的经典做法, 即把负面词频占比作为一个独立测度单列, 而不是只报告正负两侧轧差后的净语调。这一分离设计的动机在于极性对冲的掩蔽问题: 一篇同时高密度出现增长叙事与风险叙事的报道, 其净语调可能接近零, 但它的负面词汇裸暴露强度与一篇平淡的中性通稿完全不在同一量级; 若下游只保留净语调列, 就无法区分这两种信息环境, 更无法构造任何需要正负两侧独立信息的派生指标。负面单侧密度刻画的是报道中风险、亏损、违约、处罚、下滑、纠纷这类负向语汇对读者注意力的冲击面, 它与银行风险感知、融资成本、监管关注等结果变量的关联在概念上比净语调更直接: 净语调是一个方向量, 而负面密度是一个强度量, 二者回答的是不同的经济学问题。近期文献对负面文本测度的构念效度有直接印证: Pham 等 (2025) 以源自新闻的投资者负面性作为独立解释变量, 证明其在有限理性条件下塑造企业困境动态; Anastasiou 等 (2026) 把银行文本的负面信息特征输入机器学习模型, 显示其对银行股价崩盘风险有可观的预测力, 说明单侧负向文本信号本身即携带正语调所不能替代的定价含义。词典来源上, du_2022 取自 Du 等 (2022) 发表于 Review of Finance 的中文金融情感词典研究, 该文的核心论证是语言特定性与领域特定性对金融文本测度不可或缺: 直接翻译英文词典会错配中文的构词方式与惯用搭配, 借用通用中文情感词表则会错配金融语域特有的极性分布, 因此必须用本土金融语料构建并校准的领域词典。项目按 config/tone_dicts.json 收录其正面词 2,235 条、负面词 2,986 条, 另含政治正面词 1,434 条; 政治正面词以 0.5 权重计入正侧得分, 但本家族只消费负面一侧的匹配计数, 且计数按符号而非幅度归类, 故该权重设定并不进入本家族的分子 (详见方法学节与相邻测度区分节)。领域词典优于通用词表的方法论依据可上溯到 Hamilton 等 (2016) 的领域情感词典归纳研究: 同一词项在不同语域下情感极性会系统性漂移, 只有在领域内归纳或校准过的词表才能保住测度效度。中文金融场景下这一议题至今未收敛, Ma 等 (2025) 面向中国本土投资者构建的细粒度情感词典表明中文金融词表仍在持续迭代竞争, 这正是本管道并行维护六部词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018 与 L&M 词典中文主译本) 而非独尊一部的根本原因: du_2022 只是六部之一, 六部词典的同名负面比率列互为稳健性、不分主次。中国语境下媒体语调的资本市场信息含量亦有专门证据, Xu 等 (2024) 检验了政府控制媒体的语调对中国新能源行业资本市场的价值, 佐证了在中国新闻语料上度量情感极性具有实证意义。本项目的应用场景是中国银行业的金融科技转型叙事, Lee 等 (2021) 提供了金融科技创新影响中国银行效率的行业背景证据; 语料为按共现口径过滤后的银行×金融科技新闻 (生产全量约一千七百万条, 覆盖 2007 至 2024 年, T=18)。

【方法学与计算】计算链路分篇章与面板两层, 分别位于 stage 22 词典情感阶段与 stage 40 面板聚合阶段, 全程零 API 成本、纯本地确定性计算。上游文本准备: 原始新闻先经 stage 13 共现硬过滤 (只保留目标银行与至少一个金融科技词在 ±1 句窗口内邻近共现的文章), 再由 stage 14 (ctx_materializer) 物化三轨文本列, 即 content_full (标题 prepend 于正文之前的全文轨)、content_ctx (标题加目标银行实体窗口的实体窗轨)、content_ss (标题加银行与金融科技词严格同句 ±N 句窗的同句轨, 窗宽由 config/filtering.yaml 的 ss_sentence_radius 控制, 默认 1); 原始内容列不被改写, 三轨各配 *_is_fallback 指示列。篇章层计算: tone_words 对每轨文本独立执行同一套流程, 先用项目独立的 tone tokenizer (jieba, 版本 0.42.1 冻结锚点; 领域词注入走独立实例, 不污染全局分词器) 对该轨文本切词一次, 六部词典共享这份分词结果; 随后对 du_2022 调用 _compute_sentiment_with_rules 状态机遍历 token 序列。状态机维护三个句法级状态变量: 否定窗口剩余长度、程度副词倍率、转折激活位; 句末标点重置全部状态, 保证修饰效果不跨句串味。命中词典的 token 计算最终得分 final_score, 等于词典基础分经否定翻转、程度倍率、转折增强三条规则依次作用后的值, 并按 final_score 的最终符号计入 pos_count 或 neg_count。这是本测度最要紧的口径细节: 负面计数按规则处理后的最终符号而非词典原始极性归类, 于是被否定翻转的正面词会计入负面一侧 (如否定词紧邻的乐观类词), 被翻转的负面词则计入正面一侧 (如不存在风险这类否定性安抚表述中的风险)。否定作用域的处理精度对负面测度尤其关键, 因为金融新闻大量使用未出现重大损失、不存在违约风险之类的否定性缓和句式, 不做翻转会系统性高估负面密度; 否定范围检测对新闻驱动决策的价值在 Pröllochs 等 (2016) 有专门论证, 而否定处理至今仍是情感分析的开放难题 (Punetha 与 Jain 2025)。跨类重叠词 (即同一词典中正负两侧同时收录的词) 按 2026-06-24 的用户决策两侧计数, 同时进入 pos_count 与 neg_count, 把该词的语调拉向中性而不武断选边; du_2022 本身无跨类重叠词, 该机制对本家族是防御性一致口径, 保证六部词典走同一状态机分支。分母方面, n_word_tokens 取剔除纯标点与纯数字 token 之后的词数, 复用 lm_non_sentiment 模块的非词正则 (_LMFLS_NONWORD_RE), 与 LM 及 FLS 分母修复同口径; 盘上实测纯标点数字 token 约占全 token 的两成且逐篇波动非常数, 不剔除会引入随文体漂移的稀释噪声。篇章级比率等于 neg_count 除以 n_word_tokens, 四舍五入至 6 位小数; 纯符号文本 (n_word_tokens 为 0) 或词典加载缺失时置 NaN 而非 0, 严格保持不可测与测得为零两种语义的区分。面板层聚合: encode.py 的聚合注册表 build_aggregation_dict 的 Section M 对三轨逐一注册 avg_du_2022_neg_ratio 等于银行-年格内篇章级比率的算术均值, pandas mean 自动跳过 NaN, 整格皆 NaN 则面板格为 NaN; 均值为等权口径, 不做媒体权威度或媒体层级加权 (加权族走 vw/mw/hw 等独立列, 与本家族并排)。进入聚合的文章宇宙遵循 full-only 留篇门控 (2026-06-29 口径): 一篇文章是否被判为银行金融科技报道只看 llm_verified_full 为真这一个门; ctx 与 ss 轨是 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 各轨列在该宇宙上照常独立计算, 三轨共享 n_articles 分母口径。_ss 的回退语义镜像 _ctx: 文中不存在银行与金融科技词的严格同句共现时, content_ss 回退为全文 body 并置 ss_is_fallback 为真; 金融科技自动机不可用时全体回退标志置真, 优雅降级而绝不静默丢行。下游消费: 本家族三列与孪生的 avg_du_2022_pos_ratio 三轨一起, 作为词级情感分歧指标 disag_du_2022 的直接输入, 分歧公式为一减去正负差除以正负和的平方再开方, 值域零到一, 零代表全正或全负的完全一致, 一代表正负相等的最大分歧; 负面占比在其中承担分歧公式的负侧臂, 这正是正负分离设计的直接兑现, 因为净语调列无法还原分歧所需的两侧独立信息。

【文献定位】本测度在方法谱系上处于两条线的交点: 词典法负面词频传统与中文金融领域词典建设。前者的构念是用固定词表统计负面词占比并把正负两侧作为独立协变量, 是金融文本分析的奠基性做法, 其当代延续包括 Pham 等 (2025) 直接以新闻负面性为独立回归变量研究企业困境动态, 以及 Anastasiou 等 (2026) 把银行文本负面特征作为崩盘风险预测的输入特征。后者的领域特定性论证由 Du 等 (2022) 在中文金融语境系统完成, 与 Hamilton 等 (2016) 提出的从无标注语料归纳领域情感词典的方法论一脉相承; Ma 等 (2025) 的投资者细粒度词典与 Xu 等 (2024) 的政府媒体语调证据共同说明, 中文金融文本测度是一个活跃且远未收敛的领域, 任何单一词典的特异性, 包括词表规模、收词语料、极性标注惯例、更新年代, 都可能以不可观测的方式进入下游估计。因此本管道的设计立场不是挑选最优词典, 而是把六部词典的负面比率并排物化为同名列族, 让词典选择本身成为可遍历、可报告的规格维度; du_2022 列的独特价值在于其词表出自经同行评议的顶级金融学期刊、构建过程有完整方法学披露, 且是六部中唯一显式建模政治话语的词典, 与中国银行业新闻中浓厚的政策叙事高度适配。

【识别策略定位】在项目的多论文识别框架里, 本家族不充当任何一篇论文的 headline treatment, 而承担贯穿全部论文的横向稳健性角色, 须先厘清它与主线处理变量的分工。P1 至 P5 主线的处理变量清一色是模型法的 full 轨情感或属性列 (P1 的处理变量是三家 LLM 多数投票的 llm_vote_tone_full), 论文正文的因果叙事、事件研究图、系数表主报告口径全部落在模型轨; 词典法负面密度不进入任何一条主回归的核心自变量位置, 而是在稳健性小节以并排臂身份出场。据此本家族承担三类明确角色。其一, 词典法负面侧的透明稳健性测度: 当 LLM 语调因黑箱性、提示词敏感性、训练数据污染或厂商切换 (Google 至阿里 Qwen) 被审稿人质疑时, du_2022 负面密度提供一条逐词可审计、给定语料与环境种子后字节级可复现、与任何大模型权重完全无关的平行证据链; 它与模型法的 LLM 轨、BERT 轨在方法维上构成三法互证的三角, 三法各自 just-identified 并排、互为稳健性、不分主次, 严禁把词典轨与模型轨混进同一个 over-identified 方程去跑 Hansen J 过度识别检验。三法之所以不可合并, 根源在于它们是同一潜在情感构念的三种操作化, 彼此高度相关却完全不满足工具变量意义上的排除约束: 任何一法都不能被论证为仅通过另一法这条唯一通道影响结果变量, 混入同一 Hansen J 只会制造机械化的过度识别拒绝, 或因高共线性而虚假通过的伪检验, 二者都不构成有效推断。其二, 情感分歧指标 disag_du_2022 的构造输入 (见方法学节): 分歧构念在数学上要求正负两侧的计数各自独立保全, 本家族是该词典负侧的唯一供给列, 若下游只保留净语调, 分歧公式所需的两侧独立信息将不可还原, 这是正负分离设计最直接的兑现。其三, 与孪生列 avg_du_2022_pos_ratio 配对支持正负不对称机制检验: 媒体效应与文本定价文献的一个稳健发现是负面文本对风险定价、崩盘风险、融资成本一类结果的边际效应系统性强于同等强度的正面文本, 该不对称本身即机制证据, 而识别它必须让正负两侧密度以独立协变量身份并排进入同一回归的右端 (此处两列是同一构念的两个正交侧面而非替代测量, 不触犯禁混铁律), Anastasiou 等 (2026) 对银行文本负面特征预测股价崩盘风险、Pham 等 (2025) 以新闻负面性独立塑造企业困境动态, 均印证负面单侧信号携带正语调不可替代的定价含义。使用口径与全仓铁律一致: 六部词典的同名负面比率列构成第一个规格维, full、ctx、ss 三轨构成第二个规格维, 词典法内部的规则消融梯度与政治词权重梯子构成第三个规格维, 每一维内各臂一律各自 just-identified 并排、互为稳健性、不分主次、禁混同一 over-identified Hansen J; 跨臂只做系数方向与显著性的定性一致陈述, 系数量级比较须先做 z-score 标准化, 因各词典词表规模不同导致比率列的原始方差在标度上不可直接比较。多重比较层面须区分两类族: 词典族的跨列检验属于规格稳健性并排, 不进入 rwolf 的 FWER 模板; 该模板按项目口径只覆盖同构念替代 headline 测量的跨模型族 (真 FWER 走根级跨模型模板), 词典轨的规格稳健性并排与之正交, 混入会错配多重检验的族定义。这套并排而非合并、预先物化而非事后拼装的设计哲学与可复现性运动的诊断一脉相承: Fišar 等 (2024) 对管理科学的大规模再现检验表明结论对操作化选择的敏感性是系统性而非偶发的风险; Valdenegro 等 (2025) 的多重宇宙分析框架主张把整个规格空间显式物化、整体报告而非择优汇报。本管道正是以列族形式把词典乘轨道乘规则的规格空间预先落盘到面板, 审稿人无须触碰文本管道即可在 Stata 侧直接遍历全部臂, 把规格选择从隐藏的研究者自由度转为可审计的公开维度。

【与相邻测度的构念区分】与本家族同源或同名易混的相邻列须逐一划界, 每一处区分都对应一个具体的下游误用风险。第一, du_2022_tone 族 (面板上的 du_2022_tone_full 等) 是净语调: 状态机加权得分经幅度和归一化后的净值, 值域负一到正一, 正负贡献在分子相互对冲、分母是加权幅度和; 本家族是负面单侧密度, 值域零到一, 两侧不对冲, 分母是有效词数。一个是方向测度 (报道整体偏正还是偏负), 一个是强度测度 (负面语汇裸暴露有多密), 二者回答不同经济学问题, 构念不可互替; 尤其在增长叙事与风险叙事同时高密度出现的报道里, 净语调趋近零而负面密度很高, 两列会给出截然不同的信息环境刻画, 这正是把负面单侧单列而非只留净语调的核心动因。第二, du_2022_neg_count 族是银行-年内被该词典判为负面标签的篇数计数, 属篇章标签层的计数聚合: 它问有多少篇负面报道, 本家族问报道里负面词有多密, 分子 (篇数对词次) 与分母 (无对有效词数) 语义均不同, 且篇数计数对报道长度不敏感而密度对长度敏感, 二者在长文占比高的媒体环境下会显著背离。第三, 无词典前缀的 avg_neg_ratio 走六词典固定 union 词典口径, 计数基是全样本统一的并集词表: 该口径的构念是固定词表下的综合负面密度, 跨类重叠词以正一负一的平衡双票喂入 union, 极性 margin 守恒使 union 比率对重叠消歧改动逐位不变; 本家族是单词典 du_2022 口径, 刻意保留该词典的收词特异性 (词表规模、收词语料、极性标注惯例、更新年代) 供稳健性比对, 两者是综合与分解的关系, 谁都不能替代谁。第四, 政治词权重梯子 du_2022_score_polw00、polw05、polw10 只物化得分列而非比率列: 政治正面词 (1,434 词) 恒在正侧, 0.5 权重只缩放幅度不改符号, 常规情形不进 neg_count; 唯一间接通道是否定翻转把被否定的政治正面词送入负侧计数, 但负面计数按最终符号归类、与权重取值无关, 因此本家族刻意不设 polw 变体, 三权重梯子对本列数值零影响 (三权重仍各自 just-identified 并排、禁混同一 over-identified Hansen J, 只是与本列正交)。第五, 规则消融梯度 du_2022_score_raw、negonly、degonly 等同样只物化得分列, 本家族的负面计数恒在全语言学规则状态机 (否定翻转、程度倍率、转折增强骨架全开) 下产生, 无消融孪生列; 若要评估否定规则对结论的贡献, 应走 du_2022_negonly_tone 得分列做对照, 而非在本比率列上做任何再加工。第六, BERT 概率列与 LLM 计数列是模型法的负面测度, 与词典法的本列构成方法三角, 三法各自 just-identified 并排, 禁混同一 Hansen J。第七, 网络溢出族 industry_neg_shock 内部的负面比率是 LLM 口径 (LLM 负面篇数除以 LLM 有效篇数), 与本家族的词级词典比率同名异源、异分母, 引用时勿混。第八, 孪生列 avg_du_2022_pos_ratio 是同状态机、同分母、同聚合的正面单侧密度, 与本家族配对使用而非替代; 二者之和不等于一, 因为绝大多数词既非正面词也非负面词, 分子只覆盖命中词典的少数 token, 两列相加仍远小于一。以上八条中, 前三条 (tone 对 count 对 ratio、篇数对词次、union 对单词典) 是构念层的分解, 后五条 (权重、消融、方法、网络、孪生) 是口径层的分流, 共同保证本列在 Stata 侧被引用时不与任何异源列混淆。

【已知局限与稳健性梯子】局限一, 分词依赖: 分子的词典匹配与分母的有效词数都建立在 jieba 0.42.1 的切分之上, 分词器版本是项目的冻结锚点, 任何升级都会同时移动六词典的全部比率列; 这是刻意接受的测量工具固定化, 用可解释性与字节级可复现换取分词稳定性, 与 Fišar 等 (2024) 强调的计算可复现规范一致, 代价是分词边界误差 (未登录词、金融科技新词的切分歧义) 会同时污染分子的匹配与分母的词数。局限二, 否定与作用域启发式: 否定窗口是固定 token 窗加句末重置的启发式而非句法树解析, 双重否定、反问、引语归属、跨句指代等复杂修辞会漏判或误翻, 对评论型、社论型文体的负面密度存在系统性测量误差; 否定处理至今是情感分析的开放难题 (Punetha 与 Jain 2025 综述了否定处理的持续挑战, Pröllochs 等 2016 专门论证了新闻驱动交易中否定范围检测的价值), 项目以规则消融梯子把否定规则的边际贡献显式化, 供审稿人在得分列上做敏感性核查。局限三, 词典覆盖时效: du_2022 负面词表基于其构建期语料, 对金融科技领域后起的新词、监管术语的贬义惯用法、平台经济负面事件的新表述覆盖滞后, 低覆盖篇章的比率信噪比更低; 该风险由六词典并排与 union 口径列共同对冲, 中文金融词表本身仍在持续迭代竞争 (Ma 等 2025 面向本土投资者构建的细粒度词典即为新一轮迭代), 这正是本管道并行维护六部词典而非独尊一部的根本理由。局限四, 长度稀释: 密度测度对分母高度敏感, 长文的主题稀释会机械压低比率, 一篇万字长报道即便负面基调浓厚, 其负面词占全文有效词数的比率仍可能低于一篇短讯; 三轨设计正是梯子式应对, ctx 轨把文本收窄到目标银行实体邻域、ss 轨进一步收窄到银行金科同句邻域, 逐级剔除与目标银行无关的正文噪声, 使归因随轨道收紧而趋纯。局限五, 等权聚合: 银行-年均值对格内每篇报道等权, 头部权威媒体与长尾小媒体的一篇报道贡献相同, 不反映媒体影响力差异; 媒体加权族列 (vw、mw、hw 等) 与本家族并排, 供加权敏感性检验, 本列的等权口径正是加权族的参照臂。局限六, 开发环境退化: 本机 dev 语料仅两个年度 (T=2), 年格内篇数极少时均值方差偏大、ctx 与 ss 轨可能因同句共现稀疏而整格 NaN, 均属预期退化而非缺陷, 生产 T=18 语料 (2007 至 2024, 约一千七百万条) 下测度正常。稳健性梯子汇总为四个正交维度: 轨道维 (full、ctx、ss 三轨, 归因由宽到严)、词典维 (六部词典同名列族, 收词口径互异)、方法维 (词典、LLM、BERT 三法, 生成机制互异)、口径维 (单词典对 union、比率对计数对净语调、等权对加权)。每一维内各臂互为稳健性、不分主次、各自 just-identified 并排, 严禁跨臂混进同一 over-identified Hansen J; 主结论以 full 轨为 headline 叙事口径, 其余各臂只做定性方向不变的稳健性陈述, 绝不声称任何一臂在测度上更优。本列在这套梯子里的定位是: 方法维上作为词典法的透明锚点, 轨道维上以 full 为 canonical, 与全部旁系臂共同把情感测量的研究者自由度压成一张可公开遍历的规格网格。

## VAR: avg_du_2022_neg_ratio_ctx

【变体差分】实体窗轨变体: 篇章级比率在 content_ctx 上计算, 即标题 prepend 加目标银行实体窗口文本, 由 stage 14 物化。与家族 canonical 的 full 轨相比, 分子分母的计数域从整篇正文收窄到目标银行提及点周边的窗口拼接文本, 于是测到的构念从报道整体的负面密度变为归属于目标银行邻域的负面密度: 一篇主体在讨论行业乱象、仅在结尾一句提及目标银行的报道, full 轨会把全文的负面词都算进来, ctx 轨只统计银行提及点附近的负面语汇, 归因更紧。银行侧实体判定采用不对称口径, 含否定与短名过滤, 防止歧义短名与被否定提及虚增窗口。行宇宙上, ctx 轨是 conditional-on-full 的测度轨: 文章是否留篇只由 full-only 门控 (llm_verified_full 为真) 决定, ctx 列在该留篇集子集上照常计算, 不设独立门控; 无法提取实体窗口的文章按回退口径处理并由 ctx_is_fallback 指示, 回退行的比率退化为全文口径。分母仍是该轨文本自身剔除纯标点数字后的词数, 不借用 full 轨分母; 空窗文本置 NaN。用途上本列与 full、ss 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 其独立价值在于对长文稀释偏误的免疫性更强, 当 full 轨结果被质疑由与银行无关的正文噪声驱动时, ctx 轨提供归因收紧后的平行证据。本列同时是 disag_du_2022_ctx 分歧指标的负侧输入, 与同轨的 avg_du_2022_pos_ratio_ctx 配对进入分歧公式。

## VAR: avg_du_2022_neg_ratio_full

【变体差分】全文轨, 本家族的 canonical 列与 core 列 (签核口径: 类别6-扩围①, 词典 du_2022 负面成分占比的 canonical full 形态, L&M 式正负分解成分)。篇章级比率在 content_full 上计算, 即标题 prepend 于正文之前的全文文本; 标题进入计数域是刻意设计, 因为中文财经新闻的负面定调高度集中于标题, 独立标题轨已于 v3.8.0 删除并改为 prepend 口径。作为 canonical 轨, 本列承担三重身份。第一, 家族 headline: 六词典对照、三法互证、论文正文叙事一律以 full 轨为主报告口径, ctx 与 ss 轨作定性不变的稳健性陈述; 这与全仓留篇门控的 full-only 口径同构, 文章宇宙本身就由 llm_verified_full 单门定义, full 轨是唯一其计数域与留篇判定域完全对齐的轨道, 不存在轨间宇宙错位问题。第二, disag_du_2022_full 分歧指标的负侧输入, 与 avg_du_2022_pos_ratio_full 配对进入分歧公式; 由于 full 轨覆盖全文, 其正负两侧的计数基最大, 分歧指标在三轨中统计噪声最小。第三, 正负不对称机制检验的负侧臂: 与同轨正面密度列并排进入回归, 检验负面语汇密度对银行结果变量的边际效应是否系统强于正面密度。测量性质上, full 轨比率的分母是三轨中最大的 (全文词数), 单个负面词的边际贡献最小, 比率的组内方差最平滑, 对短文极值最不敏感; 代价是长文稀释, 即与目标银行无关的正文段落会压低归属于该银行的负面信号强度, 这正是 ctx 与 ss 轨存在的理由。与其他轨相同, 本列在状态机全规则口径下计数 (否定翻转、程度识别、转折识别的骨架全开, 计数只随最终符号变动), 不受政治词权重梯子影响 (权重只改幅度不改符号, 政治正面词在正侧), 也无规则消融孪生。核对口径时须注意: 本列不是 du_2022_tone_full (净语调)、不是 du_2022_neg_count_full (负面篇数)、也不是 union 口径的 avg_neg_ratio_full, 三者构念各异, 详见家族核心节的相邻测度区分。计算与复现性质上, 本列全程零 API 依赖: 分词器版本冻结、词典以 config/tone_dicts.json 为单一事实源、状态机为纯确定性遍历, 给定同一语料与同一环境种子, 篇章级比率逐字节可复现, 面板均值不含任何浮点归约顺序敏感项, 不在网络类 BLAS 漂移列清单内; 这使本列成为审计场景下最先核对的锚点列之一, 当 LLM 轨或嵌入轨因缓存、厂商切换等原因数值漂移时, 本列的稳定性可用来隔离漂移来源是文本上游还是模型层: 若本列纹丝不动而模型轨漂移, 则问题定位在模型层; 若本列亦动, 则须回溯到分词、过滤或语料层。这一诊断价值恰恰依赖 full 轨的确定性最纯, 因为 ctx 与 ss 轨的窗口物化还涉及实体判定与同句共现判据, 引入了额外的边界敏感性, 而 full 轨只做标题 prepend 与整篇切词, 是三轨中最接近纯词典计数的一轨。回归使用建议: 作为解释变量时, 因比率量纲为词数占比、组内变异幅度小, 报告标准化系数或以样本标准差为单位解释效应量更稳妥; 与六词典同名列或与正面密度列做跨列比较时一律先做 z-score 标准化, 因各词典词表规模不同导致原始方差不可比。留篇门控层面还须知晓一处数值副作用: full-only 门控与厂商切换会改变留篇集合, 从而改变本列的聚合分母与均值水平, 项目要求 manuscript 披露该口径变动 (n_articles 与相关份额列的收缩属口径变更而非缺陷), 跨版本比较本列水平值须先确认两侧留篇口径一致。词典维、轨道维、方法维的全部对照臂与本列的关系均为互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 本列作为 canonical 只是叙事排序上的 headline, 不隐含测度优劣排序。

## VAR: avg_du_2022_neg_ratio_ss

【变体差分】同句轨变体, 三轨中归因判据最严的一臂: 篇章级比率在 content_ss 上计算, 即标题 prepend 加银行与金融科技词严格同句共现句及其前后 ±N 句窗口的拼接文本, 窗宽由 config/filtering.yaml 的 ss_sentence_radius 控制, 默认 1; 该键与 stage 13 共现硬过滤的 sentence_radius 是两个不同配置键, 判据原语也不同口径, 勿混。相比 ctx 轨以银行实体提及为锚, ss 轨进一步要求银行与金融科技词出现在同一句内才纳入计数域, 测到的构念是紧扣银行金融科技议题句群的负面密度, 对一篇泛泛报道银行多项业务、仅一句涉及金科的文章, ss 轨几乎只统计那一句邻域的负面语汇, 主题归因最纯。判定采用不对称口径: 银行侧含否定与短名过滤, 金融科技侧为裸自动机词表匹配。回退语义镜像 ctx 口径: 全文不存在银行与金科词的严格同句共现时, content_ss 回退为全文 body 并置 ss_is_fallback 为真, 该行比率退化为全文口径但仍计入聚合 (共享 n_articles 分母); 金融科技自动机不可用时全体回退标志置真, 优雅降级不丢行。行宇宙同为 conditional-on-full: 留篇只看 full 门控, ss 列在留篇集上照算。开发语料下 ss 轨命中稀疏, 整格 NaN 属预期退化, 生产语料正常。本列与 full、ctx 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 同时是 disag_du_2022_ss 分歧指标的负侧输入, 与同轨的 avg_du_2022_pos_ratio_ss 配对进入分歧公式。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. Journal of Economics and Development, 27(4), 309-321. https://doi.org/10.1108/JED-06-2025-0296
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Valdenegro, D., Yan, J., Dai, D., & Rahal, C. (2025). RobustiPy: An efficient next generation multiversal library with model selection, averaging, resampling, and explainable artificial intelligence. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.19958
Fišar, M., Greiner, B., Huber, C., Katok, E., Ozkes, A. I., & the Management Science Reproducibility Collaboration. (2024). Reproducibility in Management Science. Management Science, 70(3), 1343-1356. https://doi.org/10.1287/mnsc.2023.03556
Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. Energy Policy, 184, Article 113917. https://doi.org/10.1016/j.enpol.2023.113917
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J. (2021). Does fintech innovation improve bank efficiency? Evidence from China's banking industry. International Review of Economics & Finance, 74, 468-483. https://doi.org/10.1016/j.iref.2021.03.009
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
<!-- rendered-citations:end -->
