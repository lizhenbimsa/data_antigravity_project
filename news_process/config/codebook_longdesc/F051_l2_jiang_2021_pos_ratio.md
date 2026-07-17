---
family_id: F051
columns:
- avg_jiang_2021_pos_ratio_ctx
- avg_jiang_2021_pos_ratio_full
- avg_jiang_2021_pos_ratio_ss
unit: 正面词频占比 (proportion, 无量纲, 理论域 [0,1], 实际取值远低于上界)
formula: "article: jiang_2021_pos_ratio_{trk} = pos_cnt / n_word_tokens, pos_cnt = 施加语言学规则后最终极性为正的 jiang_2021 词典命中词次 (21 个 positive∩negative 跨类重叠词两侧计数), n_word_tokens = 剔除纯标点/纯数字 token 的词 token 数; n_word_tokens=0 或词典缺失 → NaN, 逐篇 round 6 位; panel: avg_jiang_2021_pos_ratio_{trk} = bank-year 内文章级值的等权算术均值, trk ∈ {full, ctx, ss}"
producer: pipeline/sentiment/tone_words.py::_analyze_single_article (stage 22 文章级三轨打分) ; pipeline/panel/encode.py::build_aggregation_dict 聚合块 M (stage 40 bank-year 均值)
upstream:
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss + *_is_fallback)
- 21_tone_llms.parquet (full-only 留篇门控, llm_verified_full)
- 22_words_tone.parquet (jiang_2021_pos_ratio_{full,ctx,ss} 文章级列)
- 40_panel_yearly.parquet
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
- doi: 10.1080/00036846.2025.2536881
  type: journal
  authors: Wu, M., Shen, L., Wu, T., & Shao, Y.
  year: 2025
  title: "Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China"
  venue: Applied Economics
  pages_or_artno: "Advance online publication"
- doi: 10.1016/j.jfineco.2024.103910
  type: journal
  authors: Cao, S., Jiang, W., Wang, J., & Yang, B.
  year: 2024
  title: "From man vs. machine to man + machine: The art and AI of stock analyses"
  venue: Journal of Financial Economics
  vol: 160
  pages_or_artno: "103910"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2024.103899
  type: journal
  authors: Jiang, E. X., Matvos, G., Piskorski, T., & Seru, A.
  year: 2024
  title: "Monetary tightening and U.S. bank fragility in 2023: Mark-to-market losses and uninsured depositor runs?"
  venue: Journal of Financial Economics
  vol: 159
  pages_or_artno: "103899"
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1016/j.jfineco.2018.10.001
  type: journal
  authors: Jiang, F., Lee, J., Martin, X., & Zhou, G.
  year: 2019
  title: "Manager sentiment and stock returns"
  venue: Journal of Financial Economics
  vol: 132
  issue: 1
  pages_or_artno: 126-149
- doi: "10.3390/math11173675"
  title: "Media Tone and Stock Price Crash Risk: Evidence from China"
  authors: "Zhao, R., Fan, R., Xiong, X., Wang, J., & Hilliard, J."
  year: 2023
  venue: "Mathematics"
  type: "journal"
- doi: "10.1111/acfi.13328"
  title: "Media coverage and disclosure of short-termism tone: Evidence from China"
  authors: "Ni, Y."
  year: 2024
  venue: "Accounting & Finance"
  type: "journal"
new_dois:
  - "10.3390/math11173675"
  - "10.1111/acfi.13328"
---

## CORE

【构念与来源】
本家族测度目标银行在其年度媒体报道语料中获得的正面情感词汇密度。对银行-年格子内每一篇留存报道, 用姜富伟等 (2021) 中文金融情感词典逐词扫描, 统计施加语言学规则后极性为正的词典命中词次, 再除以该篇文本剔除纯标点与纯数字后的分词 token 总数, 得到文章级正面词频占比, 最后在银行-年内取等权算术均值。词典来源是姜富伟、孟令超、唐国豪发表于经济学(季刊)的中文金融情感词典 (管道内部键名 jiang_2021)。该词典以国际主流的 Loughran 与 McDonald 英文金融情感词典为蓝本翻译并按中文语料本土化扩充, 收录正面词三千一百九十四条、负面词五千六百二十一条; 负面词条数显著多于正面词条, 与金融文本分析中负面词汇信息含量更高、需要更细颗粒刻画的经验惯例一致。词典原文在中文媒体语料上证明了文本情绪对股票回报的预测力, 这构成本家族词典选择的直接学理依据: 在管道备选的六部中文情感词典中, jiang_2021 属于以媒体新闻文本 (而非上市公司年报或社交媒体贴文) 为目标语域校准、并完成资产定价效度验证的少数几部之一, 与本管道所处理的银行新闻语料在语域上高度贴合。须如实交代的是, 这一「媒体语域加效度验证」的组合并非 jiang_2021 独有 — 同管道的 du_2022 词典即基于 Word2Vec 在三百一十万篇中文财经新闻语料上自动构建并同样完成了收益预测效度验证, 二者在语域贴合度上属并列而非排他; jiang_2021 的差异化价值在其谱系而非语域垄断: 它以 Loughran 与 McDonald 英文金融词典为蓝本人工翻译扩充, 词条极性直接锚定国际主流 L&M 口径, 使本家族的正负分解成分可与国际文献的同名测度逐概念对齐, 而 du_2022 的词嵌入自动扩充路线则以覆盖广度见长, 两条构建路线在管道内互为稳健性、不分主次。词典文本的单一事实源是 config/tone_dicts.json, 管道铁律规定凡消费该词典一律读取此 JSON 而不回读 Excel 源料, 以保证跨阶段的词表逐字节一致、复现无歧义。构念本质上是正负分离设计中的正面单极成分: 与净语调 (正减负) 不同, 本列只度量赞誉侧的词汇密度, 其孪生列 avg_jiang_2021_neg_ratio 度量贬抑侧的词汇密度, 两列并置进入模型。极性分离的学理依据是金融文本分析中广为接受的极性对冲掩蔽关切: 净情感指标会把正负词都密集的争议性报道与正负词都稀疏的中性报道压缩到同一数值, 使高分歧文本被误判为中性; 将正负词频拆为两个独立协变量, 便能让赞誉密度与贬抑密度各自的边际效应可辨识。Jiang, Lee, Martin 和 Zhou (2019) 构建管理层情绪指数时同样以正、负词频作为独立原料, 并证明其对股票回报具有样本外预测力, 说明词频型情感成分在金融预测中承载真实信息而非纯噪声。本家族的应用域是银行×金融科技新闻: 语料先经共现硬过滤、再经 LLM 语义精筛, 最终仅保留目标银行与金融科技议题存在实质关联的报道 — Wu 等 (2025) 表明银行与金科企业的战略合作会显著影响银行风险承担, 该文献界定了本语料域的经济学意义。媒体正面叙事密度对银行研究有特殊价值: 银行负债端对信息环境高度敏感 — Chen 等 (2022) 证明存款流动会系统性响应银行透明度, Jiang 等 (2024) 记录了未保险存款人挤兑如何在信息触发下放大银行脆弱性, Fang 等 (2024) 则以中国数据直接证明媒体情感影响存款稳定性与银行系统性风险 — 因此媒体赞誉密度既是银行声誉资本的一个代理, 也是其融资环境的一个先行信号。

【方法学与计算】
计算链路分四段, 全部为确定性、零 API 成本的本地操作。第一段是文本物化 (stage 14): 对每篇文章物化三条文本轨 — content_full 为标题前置拼接全文正文, content_ctx 为标题加目标银行实体窗口文本, content_ss 为标题加银行与金科词同句 (含前后各一句窗口) 文本; ss 轨的回退语义严格镜像 ctx 轨: 当银行与金科词无同句共现时 content_ss 回退为全文正文并置 ss_is_fallback 为真, 且与其他轨共享同一 n_articles 分母。第二段是留篇门控 (stage 21): 按 2026-06-29 生效的 full-only 口径, 一篇文章是否计入「一篇银行金融科技报道」只看 llm_verified_full 是否为真; ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的一个子集, 本身不设独立门控。第三段是文章级打分 (stage 22): 分词器 jieba 冻结在 0.42.1 版本作为确定性锚, 六部词典的词条被注入 jieba 自定义词表, 防止多字情感词被错误切碎; 打分函数对每一轨的 token 序列运行语言学规则状态机 — 否定词在两个分词单元的窗口内翻转其后情感词的极性, 程度副词按六级权重体系缩放幅度, 转折连词之后的情感词权重放大一点五倍, 句末标点重置规则的作用域。分子 pos_cnt 是施加全部规则之后最终得分为正的 jiang_2021 命中词次: 关键在于计数发生在规则之后 — 这意味着否定结构会改变计数的归属 (「不良好」中的「良好」计入负侧而非正侧), 而程度与转折规则只按正系数缩放幅度、不改变符号, 因此对计数没有影响。据此, 本列虽是计数型测度, 却仍然继承了否定处理这一条最重要的中文语言学修正, 而把强度信息留给同词典的 tone 列去刻画。词典内二十一个同时出现在正负两类的跨类重叠词, 按 2026-06-24 的决策予以保留并两侧计数 (pos_cnt 与 neg_cnt 各加一), 不作武断的选边取舍。分母 n_word_tokens 是剔除纯标点与纯数字 token 之后的词 token 数: 该口径与金融文本分析中「词数占比」的分母定义一致; 修复前使用的物理 token 分母包含逐篇占比一成三到两成六、且跨篇非常数的标点与数字成分, 会造成系统性且不均匀的稀释偏误, 分母词化后予以消除。边界语义遵循「缺失即不可测、不冒充零」原则: 全文无有效词 token 时取 NaN, 词典加载失败时取 NaN; 文章级取值四舍五入到小数点后六位。第四段是面板聚合 (stage 40): encode 模块的 build_aggregation_dict 在聚合块 M 中, 按银行-年分组对文章级 jiang_2021_pos_ratio 的各轨取等权算术均值, 产出本家族三列; 均值是本家族唯一的聚合矩 — 单词典比率不设标准差孪生列 (只有跨词典 union 口径的 avg_pos_ratio 才配 std)。下游消费上, 本列与孪生负面列成对喂入面板级意见分歧指数 disag_jiang_2021 的各轨, 其公式为一减去「正负差与正负和之比」的平方再开根号, 取零表示情感完全一致、取一表示正负相等的最大分歧; 本列因此同时是水平测度与分歧测度的原料。三轨的调度机制值得单独说明: stage 22 对同一篇文章的三轨文本在同一次批处理内各自独立调用同一打分函数, 三轨共享同一部词典、同一套规则常量与同一分词器, 唯一变动的输入是文本字符串本身 — 这保证三轨之间的差分完全可归因于文本口径而非实现差异; 三轨列名以后缀区分, 即便某篇缺 ss 文本, 上游回退机制也保证键必存在, 提取层不会静默丢列。确定性保障上: 整段链路无任何网络调用与随机源, 词典 JSON、jieba 版本与规则常量三者冻结即可逐字节复现, 这使本家族列成为全部情感测度中复现成本最低的一族 — LLM 列依赖缓存命中、BERT 列依赖模型权重文件, 而词典比率列在任何裸机上可零成本重算。另须与同词典的 IDF 加权变体区分: stage 22 亦产 jiang_2021_idf_score 族, 其对词条按逆文档频率加权以压低高频套词, 但该加权只进入 score 族, 比率族保持纯计数口径、不受 IDF 影响, 两族回答的问题不同 — 前者问「罕见强词说了什么」, 后者问「正面词说得多密」。

【文献定位】
在方法论谱系上, 词典法在文本情感测量的效度阶梯中的位置已有系统证据。van Atteveldt, van der Velden 和 Boukes (2021) 比较人工标注、众包编码、词典法与机器学习四类方法, 发现词典法的效度通常低于监督学习与深度模型, 但它完全透明、逐字节可复现、边际成本为零且不依赖训练数据, 这一组性质无可替代。本管道据此不把词典法当作唯一测度, 而是让六部词典与 LLM 三家投票、BERT 三模型并排, 各方法族互为稳健性、不分主次: 若词典法与深度方法给出的银行情感时序高度一致, 结论便不系于任一方法族的内部偏差 — 这正是 Cao 等 (2024)「人加机器」互补性逻辑在测量层面的落地: 透明规则系统与黑箱模型各有独立的失效模式, 组合使用可降低联合失效的概率。中文情感词典构建仍是一个活跃前沿而非被淘汰的旧技术: Ma, Zhang 和 Zhang (2025) 构建面向中国个人投资者的细粒度情感词典, 并证明其在中文金融文本上的竞争力; Sun, Yuan 和 Xu (2025) 将词典知识作为先验注入预训练语言模型并获得增益, 说明高质量的领域词典即便在深度学习时代仍承载不可替代的领域知识, 也说明本管道保留词典族与深度族并排具有前沿依据。在应用文献上, Anastasiou, Katsafados 和 Tzomakas (2026) 以文本特征预测银行股价崩盘风险, 表明银行文本的情感成分对尾部风险具有前瞻信息; 结合前述 Fang 等 (2024) 与 Chen 等 (2022) 的存款渠道证据, 银行媒体正面密度这一测度在「文本情绪 → 投资者与存款人行为 → 银行经营结果」的因果链条上有清晰的文献落点。Zhao, Fan, Xiong, Wang 和 Hilliard (2023, Mathematics) 用中国互联网媒体2008-2021年文本情绪词典测度报道语调, 证明乐观(悲观)语调与未来股价崩盘风险显著正(负)相关, 为媒体正面词密度这一测度提供最新的股价风险传导证据; Ni (2024, Accounting & Finance) 基于词频词典法度量中国上市公司MD&A文本中的短期主义语调, 发现媒体报道会促使公司减少短期主义措辞, 为词典法正负词频占比测度在中文财经文本治理效应中的应用提供2024年新证据。

【识别策略定位】
本列 avg_jiang_2021_pos_ratio_full 于 2026-07-10 经类别六扩围签核为 core 列, 定位是「词典 jiang_2021 正面成分占比的 canonical full 轨」。在识别设计中它承担三重角色。其一, 作为解释变量侧的正负分离测度: 它与孪生列 avg_jiang_2021_neg_ratio_full 成对进入同一方程, 允许赞誉密度与贬抑密度携带不同符号、不同大小的系数, 这是净语调规格无法表达的; 二者同源同分母, 其共线性须在诊断中报告, 但即便高度相关也不应合并为单一净指标, 因为正负分离的全部价值恰在于让两侧边际效应各自可辨识 — 一篇正负词都密集的争议报道与一篇正负词都稀疏的中性报道, 只有在保留两列时才能被模型区分开来。其二, 作为主测度的跨方法族旁证: 论文一号主处理变量是 LLM 三家投票的 llm_vote_tone_full, 词典族比率列提供完全独立于任何神经模型的平行证据, 属于「测量方法维度」的稳健性梯子, 其价值在于与 LLM 法、BERT 法共享极低的联合失效概率。其三, 作为复合指标原料: disag_jiang_2021 分歧族以本列 (及其孪生负面列) 的面板均值为直接输入, 其公式为一减去「正负差与正负和之比」的平方再开根号, 取零表示情感完全一致 (正负有一侧为零)、取一表示正负相等的最大分歧。这条链路把水平测度 (本列) 与二阶分歧测度用同一原料串起来: 本列的测量误差会同步传导进 disag, 因此本列与 disag_jiang_2021 的回归系数携带相关的测量噪声, 不可当作两条独立证据简单叠加, 报告时须交代二者的共源关系。

处理变量与控制变量是两种截然不同的身份, 而本列在不同 paper spec 里可分别承担而不改变构造。当研究问题是「媒体赞誉密度是否影响银行融资成本或存款稳定性」时, 本列 (或其孪生净语调族) 是处理变量的一个测量工具; 当研究问题聚焦金科合作对银行经营的因果效应、而媒体情感只是需要净化的信息环境混淆时, 本列转为控制变量, 与 boilerplate、readability 等文本形态列一同吸收报道语言环境。同一列的角色由 paper_registry 的 treatment/control 声明决定, 不由列本身的构造决定 — 这也是 codebook 只描述测度语义而不锁定其因果地位的原因: 一个占比列的经济学含义随它在哪张识别表里出现而变。

识别铁律必须完整复述: 六部词典各自 just-identified 并排、互为稳健性、不分主次, 禁止把多部词典的同构念测度混进同一个 over-identified 方程去做 Hansen J 检验 — 同理适用于三轨 full/ctx/ss、LLM 三家投票、BERT 三模型、co-primary 双轨嵌入、规则消融梯度与政治词权重梯度各梯子: 任何一族内部的变体都只能各自单独入方程做系数稳定性比较, 因为族内变体间的高相关会使联合过度识别检验既无功效又误导。涉及工具变量的场景中, 本列若作为内生变量的测度, 每次只允许一个测度进入 just-identified 的 2SLS; 跨测度的推断汇总走系数并排表而非联合检验。跨模型多重假设的族错误率控制由根级 rwolf 模板承担, 词典族比率列不进入该 FWER 族 (该模板仅覆盖同构念替代 headline 测量), 其跨词典并排属规格稳健性展示而非族错误率控制对象。

计量处理层面另有四点定位。其一, 测量误差方向: 在经典误差假设 (测量误差与真值统计独立) 下, 词典法的漏词与误判造成解释变量的衰减偏误, 使系数向零收缩 — 这意味着词典列上的显著结果是保守的, 与深度模型列结果的一致性因此更具说服力; 但须留意误差未必经典 — 系统性套话污染会给赞誉密度叠加一个与银行类型 (如国有大行的官式业务语汇) 相关的正向偏置, 这属非经典误差, 衰减方向不再确定, 须靠 boilerplate 控制变量与银行固定效应联合净化, 不能简单援引「衰减偏误使结果保守」来搪塞。其二, 固定效应吸收: 面板回归默认吸收银行与年份固定效应, 本列的识别变异来自银行内跨年、且相对当年全市场的赞誉密度偏离 — 银行固定效应吸收词典对某类银行业务语汇的静态偏性, 年份固定效应吸收全市场情感潮汐 (如危机年整体转负), 剩余威胁只来自随时间变动、且跨银行差异化的语域漂移。其三, 量纲处理: 占比原始值极小且分布右偏, 进入回归前按样本标准差标准化是默认做法, 系数解释为「正面密度提高一个标准差」的效应, 便于与其他情感测度的系数并排比较; 因六部词典的正面词条基数不同、先验命中率不可比, 跨词典比较水平值无意义, 必须先各自标准化再比系数。其四, 机制通道定位: 在把媒体赞誉密度当作金科合作影响银行结果的中介通道来检验时, 本列可作为通道测度的一个稳健性版本, 但中介分析对测量误差尤其敏感 — 通道系数的衰减会低估中介占比, 故此处的中介结论亦系偏保守的下界, 而非点估计。

【与相邻测度的构念区分】
与 jiang_2021_tone 族的区分: tone 是带幅度加权的自归一化净语调 — 分子为全部命中词的最终得分之和、分母为其绝对值之和, 取值负一到正一, 程度副词与转折权重会直接改变数值; 本列是纯计数占比, 幅度信息被抹平, 只有否定翻号影响计数归属, 且分母是全文词数而非命中词的幅度和 — 前者度量「方向与强度」, 本列度量「密度」。与同词典的规则消融变体 jiang_2021_score_negonly 的区分尤须点破, 因二者极易被误认同构: negonly 与本列都只启用否定规则、都不用程度与转折规则, 但在两个维度上正交 — negonly 是双极净值 (正负相抵后自归一化的语调), 本列是单极密度 (只数正侧、除以全文词数); 一个问「加权净语调偏正还是偏负」, 一个问「正面词占全文多密」, 计数与幅度、单极与净值两层都不同, 不可互替。与同词典 IDF 加权变体 jiang_2021_idf_score 的区分: idf_score 按逆文档频率给词降权以压低高频套词, 度量「罕见强词说了什么」; 本列纯计数不降权, 高频套语与罕见强词在分子里等权计入, 度量「正面词说得多密」, 两族回答的问题不同。与跨词典 union 口径 avg_pos_ratio 族的区分: union 列的分子是六词典固定并集词表的命中数 (重叠词以正负平衡的双票消解), 度量「广义词典共识下的正面密度」, 并配有标准差孪生列; 本列分子仅取 jiang_2021 单词典的命中、无标准差孪生列, 保留该词典的媒体语域个性, 服务于跨词典敏感性与词典间分歧分析。与 msent_score 的区分: msent 是命中词计数口径的净指标 — 负词数减正词数再除以正负词数之和, 分母是命中词数, 属「构成比」, 且其计数按词典查找不施加否定翻号; 本列分母是全文词数, 属「密度」, 且计数在否定翻号之后, 两者在长文与短文之间的行为完全不同, 不可互替。与同名的 du_2022、yao_2021、bian_2021、you_2018、loughran 五个姊妹家族的区分仅在词典本身: 词条集合、语域来源与正负配比各不相同, 而计算规则、分词器与分母口径逐字节相同, 这正是「测量工具固定、词表来源变动」的受控敏感性设计, 也是六词典能互为稳健性并排的前提。与 BERT 概率列及 LLM 投票列的区分: 后两者由模型隐空间输出, 无法逐词归因; 本列每一个数值都可分解到具体命中词, 审计性最强, 这也是保留词典族与深度族并排的核心理由 — 透明可归因的规则系统与高精度的黑箱模型各有独立失效模式。与 attention、herd 等关注度族的区分: 那些度量报道量与关注热度, 与情感极性正交 — 一家银行可被大量报道却赞誉密度很低, 关注度高不等于评价正面, 两类测度不可相互代理。与 clarity、readability、boilerplate 等文本形态测度的区分: 那些是非情感的语言形式控制变量, 与本列无构念重叠, 但套话密度会与正面词密度机械相关 (客套语多含程式化褒词), 回归中应同时纳入以吸收程式化语言对赞誉密度的机械抬升。

【已知局限与稳健性梯子】
已知局限有八。第一, 词典覆盖的语域漂移: 任何固定词表都无法覆盖未登录新词、反讽与隐喻, van Atteveldt 等 (2021) 给出的词典法效度上限约束同样适用于本列; jiang_2021 以媒体文本为目标语域可缓解但不能消除该问题。第二, 时序语域漂移特为金科应用域所加重: 生产语料横跨二〇〇七至二〇二四共十九年, 而金融科技术语在此期间高速演化, 冻结在发表版的词典对晚期新兴金科业务的正面框架语汇 (如特定新产品名所携的褒义修辞) 覆盖不足, 会使晚期年份的赞誉密度被系统性低估; 该时序效度威胁部分被年份固定效应吸收, 但年内跨银行差异化的漂移无法完全吸收。第三, 中文财经报道的程式化客套语 (「成功举办」「圆满完成」之类) 会机械抬高正面词密度而不承载真实评价, 该污染由 boilerplate 套话比率三轨测度单独刻画并在回归中控制。第四, 计数口径抹平强度: 「略有改善」与「大幅飙升」各计一词, 强度信息须由同词典 tone 列补足, 两列联合使用方能同时识别方向、强度与密度。第五, 分母敏感性: 占比对文章长度分布的变化敏感, word-token 分母修复消除了标点与数字的稀释, 但长文的实质稀释效应仍在 — 篇幅越长、与银行无关的铺陈越多, 密度越被摊薄, 面板均值层面由 n_articles 与文章长度控制变量吸收。第六, 聚合等权局限: bank-year 取值是文章级值的等权算术均值, 对一篇长篇深度调查与一条百字简讯一视同仁, 不按篇幅或显著度加权; word-weighted 或 salience-weighted 的替代聚合口径存在但非 canonical, 属未来稳健性方向而非当前实现。第七, 正负词条数不对称 (负面词条五千六百二十一对正面词条三千一百九十四, 约一点七六倍) 意味着正负两列的先验命中率不同, 跨极性比较水平值没有意义, 只应各自标准化后比较系数。第八, dev 语料期 T=2 下取值稀疏, 分布矩不具生产代表性, 任何以本列分布形状为输入的阈值决策须待 T=19 生产语料重估。

稳健性梯子按维度正交铺设、梯子之间不交叉: 词典维度 — 六词典同名 pos_ratio 列并排, 外加固定并集 union 口径 (avg_pos_ratio); 轨道维度 — full/ctx/ss 三轨; 方法族维度 — LLM 三家投票与 BERT 三模型的对应情感测度; 极性维度 — 正负孪生列成对呈现。须特别说明: 规则消融梯度与政治词权重梯度均只作用于 score 族, 比率族刻意不设消融变体, 计数口径不入该谱 — 这是设计决策而非遗漏。比率的唯一规则依赖是否定翻号 (程度与转折规则只按正系数缩放幅度、不改变符号, 对计数没有影响), 其对否定规则的敏感性已由 score 族的 negonly 臂间接覆盖, 无须在比率族内再铺一条冗余消融梯子, 以免列数无谓膨胀。每一级梯子内的变体都遵循前述铁律: 各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J; 梯子与梯子之间保持正交, 例如三轨的稳健性不与六词典的稳健性交叉相乘, 政治词权重的三档也只在 score 族内、不与本比率族交叉, 以避免列数组合爆炸并保持每条稳健性论断的可解释性。

## VAR: avg_jiang_2021_pos_ratio_ctx

【变体差分】
本列是家族的实体窗轨 (ctx) 变体, tier 为 standard。与 canonical full 轨的唯一差分在被扫描文本: 分子与分母均改在 content_ctx 上计算 — 标题前置拼接目标银行实体周边的窗口文本, 而非全文正文。银行侧实体判定采用不对称口径: 否定过滤加短名过滤, 只认可靠的目标银行提及。构念含义随之收窄: full 轨度量整篇报道的赞誉密度, 本列度量「目标银行叙事邻域」的赞誉密度, 从而剔除同篇文章中与目标银行无关段落 (如同篇罗列的其他银行新闻、宏观背景铺陈) 的情感污染, 是对「情感是否真的落在目标银行身上」这一归属问题的直接回应。代价是双重的: 其一, ctx 文本显著短于全文, 分母 word-token 数缩小使占比的抽样方差放大, 短窗口内单个正面词的进出即可显著搬动数值; 其二, 窗口截断可能切掉跨句指代的评价语。行宇宙口径必须与 full-only 门控 (2026-06-29) 一致: 本列不设独立留篇判定, 其行宇宙是 llm_verified_full 为真的 full 留篇集的一个子集, 属 conditional-on-full 的测度轨。文章级源列为 jiang_2021_pos_ratio_ctx, 聚合为 bank-year 等权均值, 无标准差孪生列。使用铁律: 本列与 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排进入各自的回归, 禁止把两轨或三轨混进同一 over-identified 方程去做 Hansen J 检验; 与孪生列 avg_jiang_2021_neg_ratio_ctx 成对使用, 以保持极性分离设计的完整性。

## VAR: avg_jiang_2021_pos_ratio_full

【变体差分】
本列是家族的 canonical 列与唯一 core 列 (2026-07-10 类别六扩围签核: 词典 jiang_2021 正面成分占比的 canonical full 轨, 作为 L&M 谱系正负分解成分入核)。轨道语义: full 轨文本等于标题前置拼接全文正文 (content_full), 是三轨中信息最全、分母最稳定的一轨 — 全文 word-token 数远大于 ctx 与 ss 窗口, 单词进出对占比的扰动最小, 抽样方差最低, 因而被选为家族的 headline。它同时是留篇门控轨本尊: 2026-06-29 起管道对「一篇银行金融科技报道」的判定只看 llm_verified_full 是否为真, 本列的行宇宙与面板 n_articles 分母宇宙完全同一, 不存在 ctx/ss 轨那种「测度文本与门控文本相分离」的错位; 这也使本列与论文一号主处理变量 llm_vote_tone_full 同轨同宇宙, 词典法对 LLM 法的旁证在本列上最为干净 — 两者差异只能来自测量方法本身, 不混入轨道与样本构成的差异。计算的差分归零点: 本列即家族 CORE 节公式的直接实例 — 文章级 jiang_2021_pos_ratio_full 等于规则后正极性命中词次除以全文 word-token 数 (标题参与分子与分母, 因标题已前置进 content_full), NaN 语义与六位舍入同家族口径, 面板级取 bank-year 等权均值, 无标准差孪生列。数据特征与使用注意: 全文分母带来长文稀释 — 篇幅越长、与银行无关的铺陈越多, 占比越被压低, 因此跨银行比较时宜控制平均文章长度或同时报告 ctx 轨; 与孪生列 avg_jiang_2021_neg_ratio_full 成对进入方程是默认规格, 单独使用正面列会重新引入极性对冲掩蔽; 跨词典比较系数须先各自标准化, 因六部词典的正面词条基数不同、先验命中率不可比。下游接线上, 本列与孪生列 avg_jiang_2021_neg_ratio_full 成对喂入 disag_jiang_2021_full 分歧指数 (公式为一减去「正负差与正负和之比」的平方再开根号), 本列是其正侧输入, 也进入分歧类衍生指标的原料池; Stata 导出层为其挂接英文标签 (Avg Pos Ratio 系列) 与中文 codebook 条目, 变量在最宽 dta 中随词典比率块整体落位。质量语义须再强调一次: 文章级 NaN (无有效词 token 或词典缺失) 在聚合时被 pandas 均值自动剔除而非计零, 因此本列的隐含分母是「该银行-年内可测文章数」而非 n_articles 本身, 两者在含哨兵文本的格子上可能有别 — 以本列做加权或除法运算时须意识到这一层。作为 core 列, 本列在识别设计中的特殊地位来自它三重对齐: 测度文本、门控文本与 n_articles 分母宇宙三者同为 full 口径, 这在 ctx/ss 轨上并不成立, 因此把词典法与 LLM 主处理变量 llm_vote_tone_full 放在一起做「同一构念、不同测量工具」的稳健性对照时, 本列是最少混入无关差异的一轨; 反过来看, 也正因如此, 本列上一旦出现与 LLM 法方向不一致的信号, 就无法用轨道错位或样本构成差异来搪塞, 诊断价值最高。测量误差方向上, 词典法的漏词与误判在经典假设下使系数向零衰减, 故本列上的显著结果偏保守, 与深度模型列的一致性因此更具说服力。开发语料警示: T=2 开发环境下银行-年格子内文章数极少, 均值由个位数文章驱动, 分布不具生产代表性, 任何基于本列分布形状的建模决策须待 T=19 生产语料重估。铁律复述: 本列与 ctx、ss 两轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 与其余五部词典的同名 full 列同理并排, 且不进入跨模型 FWER 族 (该族仅覆盖同构念替代 headline 测量)。

## VAR: avg_jiang_2021_pos_ratio_ss

【变体差分】
本列是家族的同句轨 (ss) 变体, tier 为 standard, 是三轨中口径最窄的一轨。被扫描文本为 content_ss: 标题前置拼接「目标银行与金融科技词出现在同一句」的句子及其前后各一句的窗口 (窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认一句; 须注意该键与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同的配置键, 口径互不复用)。构念含义: 度量「银行×金科交汇叙事」本身的赞誉密度 — 报道在直接谈论该银行金融科技业务的句群里用了多少正面词, 是三轨中对研究问题最贴身、也最激进的一次收窄。回退语义为 ss 轨铁律, 严格镜像 ctx: 当一篇留存文章内不存在银行与金科词的同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置真, 该篇仍与其他轨共享 n_articles 分母; 金科词典不可用 (FINTECH_AC 为空) 时全部行的 fallback 置真、优雅降级不崩。因此本列在回退行上的数值与 full 轨同源, 解释时须意识到 ss 轨是「同句窗口与全文回退的混合体」, 高回退率格子上 ss 与 full 的差分会被机械压缩。行宇宙同 ctx: conditional-on-full, 是 full 留篇集的一个子集, 无独立门控。分母为 ss 文本的 word-token 数, 窗口极短时占比方差最大, 是三轨中的统计噪声上界。使用铁律: 与 full、ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与 avg_jiang_2021_neg_ratio_ss 成对使用。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. Applied Economics, Advance online publication. https://doi.org/10.1080/00036846.2025.2536881
Cao, S., Jiang, W., Wang, J., & Yang, B. (2024). From man vs. machine to man + machine: The art and AI of stock analyses. Journal of Financial Economics, 160, 103910. https://doi.org/10.1016/j.jfineco.2024.103910
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Jiang, E. X., Matvos, G., Piskorski, T., & Seru, A. (2024). Monetary tightening and U.S. bank fragility in 2023: Mark-to-market losses and uninsured depositor runs? Journal of Financial Economics, 159, 103899. https://doi.org/10.1016/j.jfineco.2024.103899
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Jiang, F., Lee, J., Martin, X., & Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
Zhao, R., Fan, R., Xiong, X., Wang, J., & Hilliard, J. (2023). Media Tone and Stock Price Crash Risk: Evidence from China. Mathematics. https://doi.org/10.3390/math11173675
Ni, Y. (2024). Media coverage and disclosure of short-termism tone: Evidence from China. Accounting & Finance. https://doi.org/10.1111/acfi.13328
<!-- rendered-citations:end -->
