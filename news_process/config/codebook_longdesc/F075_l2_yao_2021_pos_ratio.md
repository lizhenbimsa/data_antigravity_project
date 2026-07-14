---
family_id: F075
columns:
- avg_yao_2021_pos_ratio_ctx
- avg_yao_2021_pos_ratio_full
- avg_yao_2021_pos_ratio_ss
unit: 正面词频占比 (proportion, 无量纲, 理论域 [0,1], 实际取值远低于上界)
formula: "article: yao_2021_pos_ratio_{trk} = pos_cnt / n_word_tokens, pos_cnt = 施加语言学规则后最终极性为正的 yao_2021 词典命中词次 (该词典 positive∩negative 跨类重叠为 0, 无两侧计数), n_word_tokens = 剔除纯标点/纯数字 token 的词 token 数; n_word_tokens=0 或词典缺失 → NaN, 逐篇 round 6 位; panel: avg_yao_2021_pos_ratio_{trk} = bank-year 内文章级值的等权算术均值, trk ∈ {full, ctx, ss}"
producer: pipeline/sentiment/tone_words.py::_analyze_single_article (stage 22 文章级三轨打分) ; pipeline/panel/encode.py::build_aggregation_dict 聚合块 M (stage 40 bank-year 均值)
upstream:
- 14_news_with_ctx.parquet (content_full/content_ctx/content_ss + *_is_fallback)
- 21_tone_llms.parquet (full-only 留篇门控, llm_verified_full)
- 22_words_tone.parquet (yao_2021_pos_ratio_{full,ctx,ss} 文章级列)
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
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: "Advance online publication"
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
- doi: 10.1093/rfs/hhad044
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A.
  year: 2023
  title: "Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1"
  venue: The Review of Financial Studies
  vol: 36
  issue: 12
  pages_or_artno: 4919-4964
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
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
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: The Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1080/21697213.2019.1701259
  type: journal
  authors: Xu, W., Yao, Z., & Chen, D.
  year: 2019
  title: "Chinese annual report readability: Measurement and test"
  venue: China Journal of Accounting Studies
  vol: 7
  issue: 3
  pages_or_artno: 407-437
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
- doi: 10.1016/j.jeconom.2005.02.011
  type: journal
  authors: Kleibergen, F., & Paap, R.
  year: 2006
  title: "Generalized reduced rank tests using the singular value decomposition"
  venue: Journal of Econometrics
  vol: 133
  issue: 1
  pages_or_artno: 97-126
- doi: "10.3390/bdcc9100263"
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  venue: "Big Data and Cognitive Computing"
  type: "journal"
- doi: "10.1016/j.ememar.2024.101234"
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  venue: "Emerging Markets Review"
  type: "journal"
new_dois:
  - "10.3390/bdcc9100263"
  - "10.1016/j.ememar.2024.101234"
---

## CORE

【构念与来源】
本家族测度目标银行在其年度媒体报道语料中获得的正面情感词汇密度, 词典依据是姚加权、冯绪、王赞钧等 (2021) 发表于管理科学学报的中文金融情绪词典 (原文题为语调、情绪与市场影响: 基于金融情绪词典, 管道内部键名 yao_2021)。对银行-年格子内每一篇留存报道, 用该词典逐词扫描, 统计施加语言学规则后极性为正的词典命中词次, 再除以该篇文本剔除纯标点与纯数字之后的分词 token 总数, 得到文章级正面词频占比, 最后在银行-年内取等权算术均值。yao_2021 词典在本管道备选的六部中文情感词典中有一处最鲜明的身份特征: 它不是从英文词典翻译移植, 而是从两个真实的中文金融文本语域数据驱动地抽取正负情感词——一路取自上市公司年报文本, 一路取自金融社交媒体文本。年报语域贡献正面词三千五百九十二条、负面词一千六百三十三条; 社交媒体语域贡献正面词九百一十二条、负面词九百六十五条; 两语域正面词并集去重后得三千八百四十四条 (两语域正面重叠六百六十条), 负面词并集去重后得两千零七十四条 (两语域负面重叠五百二十四条)。管道加载时消费的正是这两条并集列表。这一构造带来第二处关键特征, 也是本家族区别于其余五部同名家族的构念要害: yao_2021 是正面词条显著多于负面词条的一部词典 (正面三千八百四十四对负面两千零七十四, 约一点八五比一), 极性配比方向与姜富伟等 (2021) 及 Loughran-McDonald 英文母词典所代表的负面词更丰富的惯例恰好相反。因此本家族所度量的正面成分, 其分子取自一部正面词汇本就更细密的词表, 这一点在跨词典水平比较与解释时必须置于首位。第三处特征是: 该词典的正负两集在跨类去重后没有任何重叠词, 即 positive∩negative 为空集, 因而 yao_2021 不进入管道的跨类重叠词两侧计数注册表 (_BOTH_SIDED_BY_DICT)——这与姜富伟词典保留二十一个跨类重叠词两侧计数、Loughran 中文主译本保留二十三词的情形不同, yao_2021 的每一个命中词都是无歧义的单极词, 正面计数 pos_cnt 因此是干净的单极词次, 不涉及任何双票平衡。词典文本的单一事实源是 config/tone_dicts.json, 管道铁律规定凡消费该词典一律读取此 JSON 而不回读源料, 以保证跨阶段的词表逐字节一致、复现无歧义; 词典亦经公开渠道分发, 便于第三方核验其词条集合。构念本质上是正负分离设计中的正面单极成分: 与净语调 (正减负) 不同, 本列只度量赞誉侧的词汇密度, 其孪生列 avg_yao_2021_neg_ratio 度量贬抑侧的词汇密度, 两列并置进入模型。极性分离的学理依据是金融文本分析中广为接受的极性对冲掩蔽关切: 净情感指标会把正负词都密集的争议性报道与正负词都稀疏的中性报道压缩到同一数值, 使高分歧文本被误判为中性; 把正负词频拆成两个独立协变量, 便能让赞誉密度与贬抑密度各自的边际效应可辨识。本家族的应用域是银行×金融科技新闻: 语料先经共现硬过滤、再经 LLM 语义精筛, 最终仅保留目标银行与金融科技议题存在实质关联的报道——Wu 等 (2025) 表明银行与金科企业的战略合作会显著影响银行的风险承担行为, 这为本语料域界定了清晰的经济学意义。媒体正面叙事密度对银行研究有特殊价值: 银行负债端对信息环境高度敏感——Chen 等 (2022) 证明存款流动会系统性响应银行透明度, Jiang 等 (2024) 记录了未保险存款人挤兑如何在信息触发下被放大, Fang 等 (2024) 则以中国数据直接证明媒体情感影响存款稳定性与银行系统性风险——因此媒体赞誉密度既是银行声誉资本的一个代理, 也是其融资环境的一个先行信号。

【方法学与计算】
计算链路分四段, 全部为确定性、零 API 成本的本地操作。第一段是文本物化 (stage 14): 对每篇文章物化三条文本轨——content_full 为标题前置拼接全文正文, content_ctx 为标题加目标银行实体窗口文本, content_ss 为标题加银行与金科词同句 (含前后各一句窗口) 文本; ss 轨的回退语义严格镜像 ctx 轨: 当银行与金科词无同句共现时 content_ss 回退为全文正文并置 ss_is_fallback 为真, 且与其他轨共享同一 n_articles 分母。第二段是留篇门控 (stage 21): 按 2026-06-29 生效的 full-only 口径, 一篇文章是否计入一篇银行金融科技报道只看 llm_verified_full 是否为真; ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的一个子集, 本身不设独立门控。第三段是文章级打分 (stage 22): 分词器 jieba 冻结在 0.42.1 版本作为确定性锚, 六部词典的词条被注入 jieba 自定义词表, 防止多字情感词被错误切碎; 打分函数对每一轨的 token 序列运行语言学规则状态机——否定词在两个分词单元的窗口内翻转其后情感词的极性, 程度副词按六级权重体系缩放幅度, 转折连词之后的情感词权重放大一点五倍, 句末标点重置规则的作用域。分子 pos_cnt 是施加全部规则之后最终极性为正的 yao_2021 命中词次: 关键在于计数发生在规则之后——这意味着否定结构会改变计数的归属 (良好被不字否定后计入负侧而非正侧), 而程度与转折规则只按正系数缩放幅度、不改变符号, 因此对计数没有影响。据此, 本列虽是计数型测度, 却仍然继承了否定处理这一条最重要的中文语言学修正, 而把强度信息留给同词典的 tone 列去刻画。因 yao_2021 没有跨类重叠词, 本词典的计数比姜富伟词典更为直接: 每个命中词唯一地落入正侧或负侧, 不存在同一词既加正一票又加负一票的双侧情形, pos_cnt 是纯粹的单极计数。分母 n_word_tokens 是剔除纯标点与纯数字 token 之后的词 token 数: 该口径与金融文本分析中词数占比的分母定义一致; 修复前使用的物理 token 分母包含逐篇占比一成三到两成六、且跨篇非常数的标点与数字成分, 会造成系统性且不均匀的稀释偏误, 分母词化后予以消除。边界语义遵循缺失即不可测、不冒充零的原则: 全文无有效词 token 时取 NaN, 词典加载失败时取 NaN; 文章级取值四舍五入到小数点后六位。第四段是面板聚合 (stage 40): encode 模块的 build_aggregation_dict 在聚合块 M 中, 按银行-年分组对文章级 yao_2021_pos_ratio 的各轨取等权算术均值, 产出本家族三列; 均值是本家族唯一的聚合矩——单词典比率不设标准差孪生列 (只有跨词典 union 口径的 avg_pos_ratio 才配 std)。下游消费上, 本列与孪生负面列成对喂入面板级意见分歧指数 disag_yao_2021 的各轨, 其公式为一减去正负差与正负和之比的平方再开根号, 取零表示情感完全一致、取一表示正负相等的最大分歧; 本列因此同时是水平测度与分歧测度的原料。三轨的调度机制值得单独说明: stage 22 对同一篇文章的三轨文本在同一次批处理内各自独立调用同一打分函数, 三轨共享同一部词典、同一套规则常量与同一分词器, 唯一变动的输入是文本字符串本身——这保证三轨之间的差分完全可归因于文本口径而非实现差异; 三轨列名以后缀区分, 即便某篇缺 ss 文本, 上游回退机制也保证键必存在, 提取层不会静默丢列。确定性保障上: 整段链路无任何网络调用与随机源, 词典 JSON、jieba 版本与规则常量三者冻结即可逐字节复现, 这使本家族列成为全部情感测度中复现成本最低的一族——LLM 列依赖缓存命中、BERT 列依赖模型权重文件, 而词典比率列在任何裸机上可零成本重算。另须与同词典的 IDF 加权变体区分: stage 22 亦产 yao_2021_idf_score 族, 其对词条按逆文档频率加权以压低高频套词, 但该加权只进入 score 族, 比率族保持纯计数口径、不受 IDF 影响, 两族回答的问题不同——前者问罕见强词说了什么, 后者问正面词说得多密。

【文献定位】
在方法论谱系上, 词典法在文本情感测量效度阶梯中的位置已有系统证据。van Atteveldt、van der Velden 和 Boukes (2021) 比较人工标注、众包编码、词典法与机器学习四类方法, 发现词典法的效度通常低于监督学习与深度模型, 但它完全透明、逐字节可复现、边际成本为零且不依赖训练数据, 这一组性质无可替代。本管道据此不把词典法当作唯一测度, 而是让六部词典与 LLM 三家投票、BERT 三模型并排, 各方法族互为稳健性、不分主次: 若词典法与深度方法给出的银行情感时序高度一致, 结论便不系于任一方法族的内部偏差。中文情感词典构建仍是一个活跃前沿而非被淘汰的旧技术: yao_2021 本身的数据驱动构造 (从年报与社交媒体两语域抽取) 正是这一路线的代表, 而近作进一步印证其生命力——Ma、Zhang 和 Zhang (2025) 构建面向中国个人投资者的细粒度情感词典 (CN-FSD) 并证明其竞争力, Sun、Yuan 和 Xu (2025) 将词典知识作为先验注入预训练语言模型并获得增益, 二者共同说明高质量的领域词典即便在深度学习时代仍承载不可替代的领域知识, 也为本管道保留词典族与深度族并排提供了前沿依据。与 yao_2021 直接可比的另一部中文金融情感词典是 Du、Huang、Wermers 和 Wu (2022) 的作品, 二者同为服务中文金融文本、同以正负词表为核心, 只是 du_2022 另设政治正面词类而 yao_2021 无此设置——两部词典并排于本管道, 正是同构念不同词表的受控敏感性设计。在文本测量方法学的更广脉络上, Hansen、McMahon 和 Prat (2018) 以计算语言学方法量化 FOMC 讨论的透明度, Li、Mai、Shen 和 Yan (2021) 用机器学习从文本中测量企业文化, Hassan 等 (2023) 以文本共现构造企业层面的疾病暴露, 三者共同确立了从非结构化文本中提取可复现企业级信号的合法性, 本家族的词频占比正属这一测量传统中最透明的一档。在应用文献上, Anastasiou、Katsafados 和 Tzomakas (2026) 以文本特征预测银行股价崩盘风险, Li、Yuan、Zhu 等 (2026) 从文本风险披露中还原金融网络结构与关联度, 表明银行文本的情感与语义成分对尾部风险和系统关联具有前瞻信息; 结合前述 Fang 等 (2024) 与 Chen 等 (2022) 的存款渠道证据, 银行媒体正面密度这一测度在文本情绪到投资者与存款人行为再到银行经营结果的因果链条上有清晰的文献落点。

【识别策略定位】
本列 avg_yao_2021_pos_ratio_full 于 2026-07-10 经类别六扩围签核为 core 列, 定位是词典 yao_2021 正面成分占比的 canonical full 轨。在识别设计中它承担三重角色。其一, 作为解释变量侧的正负分离测度: 它与孪生列 avg_yao_2021_neg_ratio_full 成对进入同一方程, 允许赞誉密度与贬抑密度携带不同符号、不同大小的系数, 这是净语调规格无法表达的; 二者同源同分母, 其共线性须在诊断中报告。其二, 作为主测度的跨方法族旁证: 论文一号主处理变量是 LLM 三家投票的 llm_vote_tone_full, 词典族比率列提供完全独立于任何神经模型的平行证据, 属于测量方法维度的稳健性梯子。其三, 作为复合指标原料: disag 分歧族与词典族横向均值均以本列为输入。识别铁律必须完整复述: 六部词典各自 just-identified 并排、互为稳健性、不分主次, 禁止把多部词典的同构念测度混进同一个 over-identified 方程去做 Hansen J 检验——同理适用于三轨 full/ctx/ss、LLM 三家、BERT 三模型、co-primary 双轨嵌入、规则消融与政治词权重各梯子: 任何一族内部的变体都只能各自单独入方程做系数稳定性比较, 因为族内变体间的高相关会使联合过度识别检验既无功效又误导。涉及工具变量的场景中, 本列若作为内生变量的测度, 每次只允许一个测度进入 just-identified 的 2SLS; 弱工具与识别秩的判读依 Kleibergen 和 Paap (2006) 的广义简约秩检验展开, 而跨测度的推断汇总走系数并排表而非联合检验。跨模型多重假设的族错误率控制由根级 rwolf 模板承担, 词典族比率列不进入该 FWER 族 (该模板仅覆盖同构念替代 headline 测量), 其跨词典并排属规格稳健性展示而非族错误率控制对象。计量处理层面另有三点定位。其一, 测量误差方向: 词典法的漏词与误判在经典误差假设下造成解释变量的衰减偏误, 使系数向零收缩——这意味着词典列上的显著结果是保守的, 与深度模型列结果的一致性因此更具说服力。其二, 固定效应吸收: 面板回归默认吸收银行与年份固定效应, 本列的识别变异来自银行内跨年的赞誉密度变动, 词典本身的静态偏性 (yao_2021 正面词汇本就细密, 某些银行的业务语汇天然偏正) 被银行固定效应吸收, 剩余威胁只来自随时间变动的语域漂移。其三, 量纲处理: 占比原始值极小且分布右偏, 进入回归前按样本标准差标准化是默认做法, 系数解释为正面密度提高一个标准差的效应, 便于与其他情感测度的系数并排比较; 因 yao_2021 正面词条基数高于负面词条, 本列的水平值天然高于负面孪生列, 跨极性只应在各自标准化后比较系数而不比较原始水平。降级语义须在识别层单列一笔: 词典加载失败时, 打分函数只把 yao_2021 一族的 pos_ratio 与 neg_ratio 置 NaN (源码 _analyze_single_article 的词典缺失分支明确按词典逐部处理), 其余五部词典的同名列不受牵连——这是逐词典独立降级, 结构上镜像 LLM 三家与 BERT 三模型的逐模型独立降级 (某家缺席只掉自身族), 而绝非 co-primary 双轨嵌入那种任一 embed 缺失即两列同置 NaN 的 both-or-neither 联坐。本列是纯词汇计数测度, 没有 _lg 孪生, 被明确划在嵌入 parity 体制之外 (非嵌入 carve-out); 因此在识别设计里, 词典族的缺失容错与嵌入族的严格 parity 是两套不可混用的规则, 处理本列时不得援引嵌入的双列同置逻辑。测度类型与其测量误差谱亦须区分: 本列是计数口径 (pos_cnt 只被否定翻号影响归属, 程度副词与转折权重只作用于 score 族、不改变计数, 源码可证), 因此对强度误测不敏感——略有好转与大幅飙升在本列各计一词; 而同词典的 tone 列是幅度口径, 对强度误测敏感。二者的测量误差方向与来源不同, 使它们成为两把结构不同的尺子。当计数尺 (本列) 与幅度尺 (tone) 作为各自 just-identified 的平行工具给出一致的银行情感时序时, 这种跨口径的一致性比两把同为幅度口径的尺子之间的一致性更有说服力, 因为它排除了共同的强度刻画偏差。本列在计量上还同时承担两种正交角色, 不可在同一方程内重复计入: 其一是水平角色, 作为赞誉密度直接进入水平方程的右端; 其二是分歧原料角色, 作为正侧输入喂给 disag_yao_2021 分歧指数, 该指数的因变量语义 (情感一致性对分歧) 与水平方程完全不同。同一原语进入两个不同因变量的方程属合法的多用途复用, 但把 pos_ratio 与由它派生的 disag 同时塞进同一条方程的右端则会造成机械共线, 须在规格设计时回避; 这与前述禁混同一 over-identified Hansen J 的铁律同源——凡由本列机械派生或与本列高度共线的量, 都不得与本列联立于一个过度识别式。

【与相邻测度的构念区分】
与 yao_2021_tone 族的区分: tone 是带幅度加权的自归一化净语调——分子为全部命中词的最终得分之和、分母为其绝对值之和, 取值负一到正一, 程度副词与转折权重会直接改变数值; 本列是纯计数占比, 幅度信息被抹平, 只有否定翻号影响计数归属, 且分母是全文词数而非命中词的幅度和——前者度量方向与强度, 本列度量密度。与跨词典 union 口径 avg_pos_ratio 族的区分: union 列的分子是六词典固定并集词表的命中数 (重叠词以正负平衡的双票消解), 度量广义词典共识下的正面密度; 本列分子仅取 yao_2021 单词典的命中, 保留词典个性, 服务于跨词典敏感性与词典间分歧分析。与 msent_score 的区分: msent 是命中词计数口径的净指标——负词数减正词数再除以正负词数之和, 分母是命中词数, 属构成比, 且其计数按原始词典查找不施加否定翻号; 本列分母是全文词数, 属密度, 且计数在否定翻号之后, 两者在长文与短文之间的行为完全不同, 不可互替。与同名的 jiang_2021、bian_2021、du_2022、you_2018、loughran 五个姊妹家族的区分仅在词典本身: 词条集合、语域来源与正负配比各不相同, 计算规则逐字节相同, 这正是测量工具固定、词表来源变动的受控敏感性设计; 而 yao_2021 在这五部姊妹里最独特之处有二——它是唯一从年报加社交媒体双语域数据驱动抽取的一部, 也是唯一正面词条多于负面词条的一部 (其余多依 L&M 惯例负面更细), 因此它对赞誉密度的刻画颗粒最细, 相应地对政治性、程式化的官样正面表述也最易吸收, 这一点必须在解释本家族数值时与其余词典切分开来。与 BERT 概率列及 LLM 投票列的区分: 后两者由模型隐空间输出, 无法逐词归因; 本列每一个数值都可分解到具体命中词, 审计性最强。与 clarity、readability、boilerplate 等文本形态测度的区分: 那些是非情感的语言形式控制变量, 与本列无构念重叠, 但套话密度会与正面词密度机械相关, 回归中应同时纳入以吸收程式化语言的混淆。上述文本形态测度中的可读性一支有其独立的中文测量传统: Xu、Yao 和 Chen (2019) 为中文年报可读性提出系统的度量与检验, 确立了汉语文本形式复杂度的量化口径; 该支与本列的赞誉密度构念零重叠, 但同样作为语言形式控制变量与本列并置, 以免把行文风格 (长句、生僻词、结构繁复) 误读为情感倾向。近年方法学前沿进一步充实了词典法之外与官方媒体情感测度两方面的当代参照: Chuang, He, & Hu (2025, Big Data and Cognitive Computing) 系统比较五类词向量表征与17种传统、深度与Transformer模型及LLaMA3在中文财经新闻情感分类与短期股价预测联合任务上的表现, 为词典法之外的中文金融文本情感测量提供当代基准; Xu, Hua, & Zhang (2025, Emerging Markets Review) 构建基于文本分析与BERT的中国官方媒体负面情绪指数, 证明其可预测股市收益反转, 进一步佐证中文媒体情感测度对市场行为的前瞻信息价值。与关注度/曝光量族 (如金科报道占比、注意力份额) 的区分同样关键: 那些测度回答该银行被报道了多少、金科议题被谈得多密, 属数量与篇幅维度; 本列回答在这些报道里正面词说得多密, 属极性密度维度——两者正交, 一家银行可以被大量报道却语调平淡 (高曝光低正面密度), 也可以被零星报道却字字褒扬 (低曝光高正面密度), 因此关注度族与本列须作为不同构念分列, 既不可互替, 也不宜不加设计地简单相乘。与孪生负面列 avg_yao_2021_neg_ratio 的区分是极性分离设计的核心承重点: 二者同源同分母、共用同一部词典与同一套规则, 唯一差别是分子取正侧还是负侧命中; 因 yao_2021 正面词条基数远高于负面 (三千八百四十四对两千零七十四), 本列的先验命中率与水平值天然高于负面孪生, 二者只应各自标准化后比较系数, 绝不比较原始水平差, 也绝不能因正面列水平更高就推断该银行更受赞誉——那只是词表构造的先验偏置, 须先被标准化与银行固定效应剥离。

【已知局限与稳健性梯子】
已知局限有六。第一, 词典覆盖的语域漂移: 任何固定词表都无法覆盖未登录新词、反讽与隐喻, van Atteveldt 等 (2021) 给出的词典法效度上限约束同样适用于本列; yao_2021 以年报与社交媒体双语域为构造基座可缓解但不能消除该问题, 且其社媒来源的词条在处理规范化的银行新闻文本时可能存在语域错配。第二, 中文财经报道的程式化客套语 (成功举办、圆满完成之类) 会机械抬高正面词密度而不承载真实评价; 尤须警惕的是 yao_2021 正面词表本就细密, 对这类官样正面表述的吸收比负面偏重的词典更强, 该污染由 boilerplate 套话比率三轨测度单独刻画并在回归中控制; Piotroski、Wong 和 Zhang (2017) 记录了中国企业新闻中的政治性偏向, 提示中文媒体的正面框架可能被政治与宣传因素系统性抬高, 这对以正面词密度为核心的本家族是一层需要披露的构念效度威胁。第三, 计数口径抹平强度: 略有改善与大幅飙升各计一词, 强度信息须由同词典 tone 列补足, 两列联合使用方能同时识别方向、强度与密度。第四, 分母敏感性: 占比对文章长度分布的变化敏感, word-token 分母修复消除了标点与数字的稀释, 但长文的稀释效应仍在——面板均值层面由 n_articles 与文章长度控制变量吸收。第五, 正负词条数不对称且方向与惯例相反 (正面三千八百四十四对负面两千零七十四, 约一点八五倍, 正面更多) 意味着本词典的正面命中先验率高于其负面孪生, 也高于其余多数负面偏重的词典, 跨极性与跨词典比较水平值都没有意义, 只应各自标准化后比较系数。第六, dev 语料期 T=2 下取值稀疏, 分布矩不具生产代表性, 任何以本列分布形状为输入的阈值决策须待 T=18 生产语料重估。稳健性梯子按维度正交铺设、梯子之间不交叉: 词典维度——六词典同名列并排, 外加 union 口径与词典族横向均值; 轨道维度——full/ctx/ss 三轨; 方法族维度——LLM 三家与 BERT 三模型的对应情感测度; 极性维度——正负孪生列成对呈现。注意规则消融梯度与政治词权重梯度均只作用于 score 族, 比率族刻意不设消融变体 (计数口径不入该谱), 且政治词权重梯度仅 du_2022 独有、与 yao_2021 无涉; 比率的唯一规则依赖是否定翻号, 其敏感性已由 score 族的 negonly 臂间接覆盖。每一级梯子内的变体都遵循前述铁律: 各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J。另有三点构念使用层的警示须补记。其一是同时性与反向因果: 媒体赞誉密度与银行经营结果是联合决定的——Fang 等 (2024) 证明媒体情感影响存款稳定性与银行系统性风险, 但银行基本面向好也会反过来诱发更正面的报道, Chen 等 (2022) 记录的存款对透明度的响应同样是双向可解释的, 故本列与银行结果变量之间的水平相关不能径直读作因果, 须由面板固定效应加工具变量的识别设计在模型层承接, 本测度自身不解决内生性。其二是轨间回退率差异对跨轨稳健性判读的干扰: ss 轨在无银行与金科词同句共现的报道上回退为全文正文并与 full 同源, 高回退率的银行-年格子里 ss 与 full 的差分被机械压缩, 因此跨轨一致性在高回退子样本上会被系统性高估——判读三轨稳健性时须同时报告各轨的回退占比, 避免把回退导致的同源假一致误当作测度稳健, 这一点在开发语料 T=2 上尤其突出 (格子内文章极少、回退占比高)。其三是面板聚合层的缺失语义须再强调: 文章级 NaN (无有效词 token 或词典缺失) 在 bank-year 求均值时被自动剔除而非计零, 故本列的隐含分母是该格子内可测文章数而非 n_articles 本身, 在含哨兵文本或短文密集的格子上两者可能不等, 以本列做二次加权或除法运算时须意识到这层错位, 不可想当然地用 n_articles 反推可测篇数。

## VAR: avg_yao_2021_pos_ratio_ctx

【变体差分】
本列是家族的实体窗轨 (ctx) 变体, tier 为 standard。与 canonical full 轨的唯一差分在被扫描文本: 分子与分母均改在 content_ctx 上计算——标题前置拼接目标银行实体周边的窗口文本, 而非全文正文。银行侧实体判定采用不对称口径: 否定过滤加短名过滤, 只认可靠的目标银行提及。构念含义随之收窄: full 轨度量整篇报道的赞誉密度, 本列度量目标银行叙事邻域的赞誉密度, 从而剔除同篇文章中与目标银行无关段落 (如同篇罗列的其他银行新闻、宏观背景铺陈) 的情感污染, 是对情感是否真的落在目标银行身上这一归属问题的直接回应。代价是双重的: 其一, ctx 文本显著短于全文, 分母 word-token 数缩小使占比的抽样方差放大, 短窗口内单个正面词的进出即可显著搬动数值; 因 yao_2021 正面词表细密, 短窗口内命中的绝对概率高于负面偏重的词典, 这一放大在本词典上尤为明显。其二, 窗口截断可能切掉跨句指代的评价语。行宇宙口径必须与 full-only 门控 (2026-06-29) 一致: 本列不设独立留篇判定, 其行宇宙是 llm_verified_full 为真的 full 留篇集的一个子集, 属 conditional-on-full 的测度轨。文章级源列为 yao_2021_pos_ratio_ctx, 聚合为 bank-year 等权均值, 无标准差孪生列; 计数继承家族口径——规则后正极性单极命中 (yao_2021 无跨类重叠词, 计数不涉双票), 分母为剔除纯标点纯数字的词 token 数, NaN 语义与六位舍入同家族。使用铁律: 本列与 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排进入各自的回归, 禁止把两轨或三轨混进同一 over-identified 方程去做 Hansen J 检验; 与孪生列 avg_yao_2021_neg_ratio_ctx 成对使用, 以保持极性分离设计的完整性。

## VAR: avg_yao_2021_pos_ratio_full

【变体差分】
本列是家族的 canonical 列与唯一 core 列 (2026-07-10 类别六扩围签核: 词典 yao_2021 正面成分占比的 canonical full 轨, 作为正负分解成分入核)。轨道语义: full 轨文本等于标题前置拼接全文正文 (content_full), 是三轨中信息最全、分母最稳定的一轨——全文 word-token 数远大于 ctx 与 ss 窗口, 单词进出对占比的扰动最小, 抽样方差最低, 因而被选为家族的 headline。它同时是留篇门控轨本尊: 2026-06-29 起管道对一篇银行金融科技报道的判定只看 llm_verified_full 是否为真, 本列的行宇宙与面板 n_articles 分母宇宙完全同一, 不存在 ctx/ss 轨那种测度文本与门控文本相分离的错位; 这也使本列与论文一号主处理变量 llm_vote_tone_full 同轨同宇宙, 词典法对 LLM 法的旁证在本列上最为干净——两者差异只能来自测量方法本身, 不混入轨道与样本构成的差异。计算的差分归零点: 本列即家族 CORE 节公式的直接实例——文章级 yao_2021_pos_ratio_full 等于规则后正极性命中词次除以全文 word-token 数 (标题参与分子与分母, 因标题已前置进 content_full), NaN 语义与六位舍入同家族口径, 面板级取 bank-year 等权均值, 无标准差孪生列。词典个性须在本列上强调: yao_2021 是六部词典里唯一从年报加社交媒体双语域数据驱动构造、且唯一正面词条 (三千八百四十四) 多于负面词条 (两千零七十四) 的一部, 又因其正负两集跨类零重叠, 本列的 pos_cnt 是无歧义的单极计数, 不像姜富伟词典那样存在跨类重叠词的两侧双票——这三点使本列成为对赞誉密度刻画最细、审计最直接、但也对官样正面表述最敏感的一条词典正面轨。数据特征与使用注意: 全文分母带来长文稀释——篇幅越长、与银行无关的铺陈越多, 占比越被压低, 因此跨银行比较时宜控制平均文章长度或同时报告 ctx 轨; 与孪生列 avg_yao_2021_neg_ratio_full 成对进入方程是默认规格, 单独使用正面列会重新引入极性对冲掩蔽; 跨词典比较系数须先各自标准化, 因六部词典的正面词条基数不同、yao_2021 的正面先验命中率尤其偏高, 原始水平不可比。下游接线上, 本列是 disag_yao_2021_full 分歧指数的正侧输入, 也进入词典族横向均值与分歧类衍生指标的原料池; Stata 导出层为其挂接英文标签 (Avg Pos Ratio 系列) 与中文 codebook 条目, 变量在最宽 dta 中随词典比率块整体落位。质量语义须再强调一次: 文章级 NaN (无有效词 token 或词典缺失) 在聚合时被 pandas 均值自动剔除而非计零, 因此本列的隐含分母是该银行-年内可测文章数而非 n_articles 本身, 两者在含哨兵文本的格子上可能有别——以本列做加权或除法运算时须意识到这一层。开发语料警示: T=2 开发环境下银行-年格子内文章数极少, 均值由个位数文章驱动, 分布不具生产代表性, 任何基于本列分布形状的建模决策须待 T=18 生产语料重估。识别角色上, 本列作为词典族的一条正面成分轨, 与孪生负面列共同承载正负分离设计, 又与 LLM 三家投票及 BERT 三模型的对应情感测度构成测量方法维度的稳健性梯子; 词典法的漏词与误判在经典误差假设下使系数向零衰减, 故本列上的显著结果偏保守, 与深度方法列结果的一致性因此更具说服力。铁律复述: 本列与 ctx、ss 两轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 与其余五部词典的同名 full 列同理并排, 且不进入跨模型 FWER 族 (该族仅覆盖同构念替代 headline 测量)。

## VAR: avg_yao_2021_pos_ratio_ss

【变体差分】
本列是家族的同句轨 (ss) 变体, tier 为 standard, 是三轨中口径最窄的一轨。被扫描文本为 content_ss: 标题前置拼接目标银行与金融科技词出现在同一句的句子及其前后各一句的窗口 (窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认一句; 须注意该键与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同的配置键, 口径互不复用)。构念含义: 度量银行×金科交汇叙事本身的赞誉密度——报道在直接谈论该银行金融科技业务的句群里用了多少正面词, 是三轨中对研究问题最贴身、也最激进的一次收窄。回退语义为 ss 轨铁律, 严格镜像 ctx: 当一篇留存文章内不存在银行与金科词的同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置真, 该篇仍与其他轨共享 n_articles 分母; 金科词典不可用 (FINTECH_AC 为空) 时全部行的 fallback 置真、优雅降级不崩。因此本列在回退行上的数值与 full 轨同源, 解释时须意识到 ss 轨是同句窗口与全文回退的混合体, 高回退率格子上 ss 与 full 的差分会被机械压缩。行宇宙同 ctx: conditional-on-full, 是 full 留篇集的一个子集, 无独立门控。分母为 ss 文本的 word-token 数, 窗口极短时占比方差最大, 是三轨中的统计噪声上界; 因 yao_2021 正面词表细密, 极短窗口内正面命中的抽样波动在本词典上尤为剧烈。计数继承家族口径 (规则后正极性单极命中, yao_2021 零跨类重叠不涉双票)。使用铁律: 与 full、ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与 avg_yao_2021_neg_ratio_ss 成对使用。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. Applied Economics, Advance online publication. https://doi.org/10.1080/00036846.2025.2536881
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Jiang, E. X., Matvos, G., Piskorski, T., & Seru, A. (2024). Monetary tightening and U.S. bank fragility in 2023: Mark-to-market losses and uninsured depositor runs?. Journal of Financial Economics, 159, 103899. https://doi.org/10.1016/j.jfineco.2024.103899
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Xu, W., Yao, Z., & Chen, D. (2019). Chinese annual report readability: Measurement and test. China Journal of Accounting Studies, 7(3), 407-437. https://doi.org/10.1080/21697213.2019.1701259
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. The Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news: The role of conglomeration reform in China. The Journal of Law and Economics, 60(1), 173-207. https://doi.org/10.1086/693096
Kleibergen, F., & Paap, R. (2006). Generalized reduced rank tests using the singular value decomposition. Journal of Econometrics, 133(1), 97-126. https://doi.org/10.1016/j.jeconom.2005.02.011
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
<!-- rendered-citations:end -->
