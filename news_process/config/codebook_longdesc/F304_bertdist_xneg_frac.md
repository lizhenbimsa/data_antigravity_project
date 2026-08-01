---
family_id: F304
columns:
- fin_sent_zh_xneg_frac_ctx
- fin_sent_zh_xneg_frac_full
- fin_sent_zh_xneg_frac_ss
- fin_sent_zh_xneg_frac_t80_ctx
- fin_sent_zh_xneg_frac_t80_full
- fin_sent_zh_xneg_frac_t80_ss
- fin_sent_zh_xneg_frac_t95_ctx
- fin_sent_zh_xneg_frac_t95_full
- fin_sent_zh_xneg_frac_t95_ss
- finbert2_xneg_frac_ctx
- finbert2_xneg_frac_full
- finbert2_xneg_frac_ss
- finbert2_xneg_frac_t80_ctx
- finbert2_xneg_frac_t80_full
- finbert2_xneg_frac_t80_ss
- finbert2_xneg_frac_t95_ctx
- finbert2_xneg_frac_t95_full
- finbert2_xneg_frac_t95_ss
- finbert_cn_xneg_frac_ctx
- finbert_cn_xneg_frac_full
- finbert_cn_xneg_frac_ss
- finbert_cn_xneg_frac_t80_ctx
- finbert_cn_xneg_frac_t80_full
- finbert_cn_xneg_frac_t80_ss
- finbert_cn_xneg_frac_t95_ctx
- finbert_cn_xneg_frac_t95_full
- finbert_cn_xneg_frac_t95_ss
unit: 占比 (proportion, 取值 [0,1], 无量纲)
formula: "{b}_xneg_frac{tag}{trk} = bank-year 内 mean( 1{ P_b(负面) > tau } ); tau ∈ {0.80, 0.90, 0.95}, canonical = 0.90 ≡ 无 tag 后缀 (_t80/_t95 为梯子臂); 指示为 float, P(负面)=NaN 保持 NaN 禁 fillna(0), 分母 = 该 bank-year 内概率非缺篇数; 三阈值同源同掩码故逐格精确单调 t80 ≥ 无后缀 ≥ t95"
producer: "news_process/pipeline/panel/bert_distribution.py::compute_article_distribution_cols (文章级指示 _xneg_ind_{b}{tag}{trk}) + iter_agg_entries (经 encode.build_aggregation_dict 以 mean 聚合到面板); 概率上游 = pipeline/sentiment/tone_berts.py (stage 23)"
upstream:
- 23_bert_tone.parquet ({b}_负面{_full,_ctx,_ss} 概率列, stage 23 三模型三轨推理)
- 22_words_tone.parquet (stage 23 的输入载体, 携带三轨文本列)
- 14_materialize_ctx.parquet (content_ctx / content_ss 物化, stage 14)
citations:
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
- doi: "10.3390/jrfm19050302"
  type: "journal"
  authors: "Lizelle Ann V. Cruz"
  year: 2026
  title: "Sentiment as Early Warning: A Systemic Risk Index for the Philippines"
  venue: "Journal of Risk and Financial Management"
- doi: "10.1007/s10479-025-06567-y"
  type: "journal"
  authors: "Dimitris Anastasiou, Apostolos Katsafados, Christos Tzomakas"
  year: 2025
  title: "Banks' stock price crash risk prediction with textual analysis: a machine learning approach"
  venue: "Annals of Operations Research"
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: 65
  issue: 4
  pages_or_artno: "1373-1403"
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: "24883-24892"
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: "1150-1172"
- doi: 10.1016/j.jfineco.2024.103899
  type: journal
  authors: Jiang, E. X., Matvos, G., Piskorski, T., & Seru, A.
  year: 2024
  title: "Monetary tightening and U.S. bank fragility in 2023: Mark-to-market losses and uninsured depositor runs?"
  venue: Journal of Financial Economics
  vol: 159
  pages_or_artno: "103899"
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: "105227"
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: "103870"
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: "806-841"
- doi: 10.1093/rof/rfac052
  type: journal
  authors: Goldstein, I.
  year: 2023
  title: "Information in financial markets and its real effects"
  venue: Review of Finance
  vol: 27
  issue: 1
  pages_or_artno: "1-32"
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: "475-501"
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: "673-719"
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: "5514-5532"
- doi: 10.1007/978-3-030-32381-3_16
  type: book
  authors: Sun, C., Qiu, X., Xu, Y., & Huang, X.
  year: 2019
  title: "How to fine-tune BERT for text classification?"
  venue: "Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science, Springer"
  vol: 11856
  pages_or_artno: "194-206"
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: "43-96"
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: "2442-2476"
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: "1187-1230"
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: "405-459"
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: "35-65"
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: "1139-1168"
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: "1237-1282"
- doi: 10.1016/j.ribaf.2025.102881
  type: journal
  authors: Wei, L., Wei, M., Jing, H., & Jing, Z.
  year: 2025
  title: "Annual report tone and bank risk-taking behavior: Evidence from China"
  venue: Research in International Business and Finance
new_dois:
- "10.3390/jrfm19050302"
- "10.1007/s10479-025-06567-y"
- "10.1016/j.ribaf.2025.102881"
---

## CORE

该研究用金融领域情感模型集成从新闻标题构建高频系统性风险情绪指数,发现情绪急剧恶化往往领先于重大金融压力事件数周出现,呼应了极端负面尾部占比作为阈值型风险信号的构念。 该研究以机器学习文本分析方法从银行相关文本中提取情感信号预测银行股价崩盘风险,支持负面情绪尾部信息(而非均值语调)对银行类阈值触发型后果具有更强解释力的构念。

【构念与来源】
本家族测度的构念是媒体报道情绪分布的极端负面尾部占比 (extreme negative fraction), 即在一家银行一个年度的全部有效报道中, 被中文金融领域 BERT 情感模型以高置信度判定为负面的报道所占的比例。它回答的问题与均值语调截然不同: 均值语调问的是"这一年媒体对这家银行的总体口风偏正还是偏负", 而极端负面占比问的是"这一年里有多大比例的报道属于几乎不留余地的强烈唱衰"。这一区分具有实质经济含义。文本情绪研究的开山工作已经确认负面词语承载了金融文本中最主要的信息含量, Tetlock (2007) 发现媒体悲观情绪对市场价格与交易量有可测度的预测力, Loughran & McDonald (2011) 则表明负面词表是词典法中最稳健、噪声最低的一支。但均值测度天然掩盖分布形状: 两家银行可以拥有完全相同的年度平均语调, 其中一家的报道全部温和中性略偏负, 另一家则是多数正面报道与少数极端负面报道的混合。对于存款人挤兑、监管介入、同业信任这类具有阈值触发性质的后果变量, 起作用的往往正是后一种"少数极端坏消息"而非前一种"普遍轻微不满"。Chen, Goldstein, Huang & Vashishtha (2022) 关于银行透明度与存款流动的证据, 以及 Cookson, Fox, Gil-Bazo, Imbet & Schiller (2026) 关于社交媒体作为挤兑催化剂的研究, 都指向储户对负面信息的反应是高度非线性的: 温和的坏消息可以被忽略, 而极端负面叙事一旦越过某个显著性门槛, 就可能引发提款、传染与自我实现的流动性螺旋; Jiang, Matvos, Piskorski & Seru (2024) 对二〇二三年美国银行动荡的分析同样强调未保险存款人对尾部风险信号的敏感。在中国语境下这一尾部测度还有一层额外的信息经济学价值: Piotroski, Wong & Zhang (2015) 证明政治激励会系统性压制负面信息的发布, Qin, Strömberg & Wu (2018) 与 You, Zhang & Zhang (2018) 分别刻画了中国媒体的偏倚结构与市场化媒体的监督功能。在负面报道整体受抑的环境中, 一篇仍然以极高负面概率见报的文章, 其越过审查与自我审查成本的事实本身就构成更强的信号, 因此极端负面占比在中国银行业样本中的信息密度可能高于负面报道比例的一般水平。本家族数据来源为 pipeline 阶段二十三: 三个中文金融 BERT 模型对每篇银行金融科技报道输出逐类概率, 本家族只消费其中的负面类概率列, 在阶段四十的面板构造中以纯后处理方式派生, 不重跑任何模型推理, 属于零额外成本的分布形状测度族。

用白话概括这一族变量在做什么: 想象把某家银行一年内的所有相关报道排成一排, 请三位读金融新闻的机器评审逐篇打分, 每位评审对每篇给出"这篇有多负面"的把握程度; 均值语调是把所有分数加起来取平均, 而本家族是数一数"评审几乎可以拍板说这篇是在唱衰"的报道占全部有效报道的几成。为什么要单独数这一头: 因为很多金融后果不是被"平均口风差一点"触发的, 而是被"出现了几篇谁看了都心里一沉的报道"触发的 — 储户看到的是那几篇爆款坏消息, 不是全年报道的平均值。为什么要三位评审、三个把握门槛、三种读法 (全文、只读提到这家银行的段落、只读银行和金融科技同时出现的句子) 各算一遍: 因为任何单一算法、单一门槛、单一读法都可能有自己的脾气, 只有当结论在这些替代口径下都站得住, 才能说测到的是真实现象而不是算法的偏好。

【方法学与计算】
计算分文章级与面板级两层, 全部实现于叶模块 bert_distribution.py。文章级: 对每个模型 b 与每条文本轨 trk, 读取该篇报道的负面类概率 P_b(负面), 构造指示变量, 当 P_b(负面) 严格大于阈值 tau 时记一, 否则记零; 指示以浮点存储, 且当负面概率缺失时指示保持缺失, 明确禁止以零填充 — 这一约定保证了面板占比的分母是"概率非缺的有效篇数"而非"全部篇数", 推理失败或空文本的报道既不进分子也不进分母, 避免把技术性缺失误算成"不极端"。阈值取三档梯子: 零点八零、零点九零与零点九五, 其中零点九零为 canonical 档, 列名不带阈值后缀; 零点八零与零点九五分别以 _t80 与 _t95 后缀标识。三档指示由同一概率列在同一缺失掩码下生成, 因此面板占比在每个银行年度格点上精确满足单调关系: 宽阈值臂不小于 canonical, canonical 不小于严阈值臂, 任何违反单调的格点都指示上游数据损坏, 这一性质被 gate 测试锁死。面板级: 文章级指示列以中间列形式命名, 经 encode 的聚合字典对每个银行年度取算术均值, 得到本家族的二十七个面板列; 中间列在写出文章级 parquet 之前由 runner 单点清除, 绝不落盘。上游概率的生成口径由阶段二十三决定: 三个模型分别为 finbert_cn (公开的中文金融语调三分类模型)、fin_sent_zh (基于金融短语库微调的中文三分类模型) 与 finbert2 (项目本地私有微调的二分类模型, 仅正负两类); 超长文本按滑动窗口切片、窗口间百分之五十重叠、按各窗置信度加权池化聚合 logits, 推理失败写哨兵且与空文本严格区分。三条文本轨 full、ctx、ss 分别对应标题拼接全文、标题拼接银行实体窗口、标题拼接银行与金融科技词同句邻域窗, 三轨在阶段十四物化、在阶段二十三各自独立推理。留篇门控遵循 full-only 口径: 一篇报道是否计入"银行金融科技报道"宇宙只由 full 轨的 LLM 验证结果决定, ctx 与 ss 是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集。ss 轨的回退语义镜像 ctx: 当银行与金融科技词无同句共现时, ss 文本回退为全文正文并置回退标志, 极端情形下金融科技词表缺失则全体回退、优雅降级。本家族属非嵌入测度, 依 carve-out 口径不存在 _lg 孪生列; per-model 独立降级: finbert2 因本地模型目录未配置而缺席时, 仅其自身列族缺失, 另两个模型照常产出, 不实行嵌入族的双列同缺语义。

工程与确定性口径补充三点。第一, 中间列生命周期: 文章级极端负面指示列以下划线前缀命名, 由 runner 在诊断日志之前按声明集与实际列的交集单点清除, 保证文章级 parquet 不携带任何本家族中间产物, 面板列是其唯一落盘形态; 声明器与数据框无关、恒返回声明全集, 声明集与实际产出集的差恰为合法缺席的模型轨组合, 这一对账逻辑使"模型缺席"与"数据损坏"可机械区分。第二, 确定性: 本家族计算只含概率读取、阈值比较与算术均值, 无随机数、无浮点归约顺序敏感项, 给定上游概率列即逐位可复现; 上游阶段二十三的确定性来自冻结的模型权重与取最大类判别, 混合精度推理不改变概率比较的相对次序。第三, 质量闸: 家族行为由专门的 gate 测试族锁定, 覆盖阈值梯子的逐格单调、缺失掩码不填零、canonical 档与无后缀列的等价、二分类模型只读两列概率、以及 per-model 缺席时键集的正确收缩; 任何改动本家族口径的提交都必须先过该测试族, 这使本文档描述的语义具有可执行的约束力而非单纯的文字约定。

【文献定位】
本家族在方法论上位于金融文本情绪测量的第三条路线 — 预训练语言模型微调分类 — 之上。Loughran & McDonald (2016) 的综述确立了词典法的边界与陷阱, Frankel, Jennings & Lee (2022) 系统比较了机器学习与词典法在披露文本情绪提取上的相对优势, 结论是监督学习在样本外拟合上普遍占优但可解释性下降; Huang, Wang & Yang (2023) 的 FinBERT 工作证明领域预训练的 BERT 在金融文本信息提取上显著超越通用模型与词典基线, 是本家族三个模型选型的直接方法学依据; Sun, Qiu, Xu & Huang (2019) 提供了 BERT 文本分类微调的系统性配方, 支撑阶段二十三的推理超参选择。中文场景的适配性由两支文献支撑: Du, Huang, Wermers & Wu (2022) 论证了语言与领域双重特异性对中文金融情绪测量的必要性, Ma, Zhang & Zhang (2025) 构造的中文细粒度情感词典与 Lan, Wu, Xu, Feng & Zhang (2025) 的中文金融大模型细粒度情感工作共同说明中文金融文本情绪已发展出独立的测量传统, 通用英文工具不可直接移植。Todd, Bowden & Moshfeghi (2024) 对金融文本情绪分析的综合综述与 Kirtac & Germano (2024) 的大模型情绪交易证据, 把神经网络情绪测度与资产定价后果直接联系起来。在应用端, 本家族服务的是媒体语调与银行行为的因果链: Marchetti, Tarducci & Branzoli (2025) 展示了媒体语调偏移对银行融资条件的测量应用, Fang, Wang, Wang & Yuan (2024) 提供了中国场景下媒体情绪、存款稳定性与银行系统性风险的直接证据, Gutknecht (2025) 表明负面媒体覆盖对权益风险的传导, Cookson, Lu, Mullins & Niessner (2024) 则提醒社交信号与传统媒体信号的信息含量差异; Goldstein (2023) 的综述框架把这类金融市场信息测度与实体后果的联结一般化。极端尾部占比而非均值的构造思路, 其家族级动机锚点是计数式极端事件指数传统, 与净语调均值形成互补的分布形状信息。

【识别策略定位】
本家族在识别设计中的角色是稳健性与机制测度, 不是任何一篇论文的 primary treatment。P1 语调主线的处理变量是三家 LLM 投票共识的 full 轨语调, BERT 三模型是与 LLM 法、词典法并列的第三条独立测量路线, 三法互为印证; 在 BERT 路线内部, 本家族又把测量从一阶矩推进到尾部占比。使用时必须遵守以下并排口径, 这是仓库级计量铁律: 三档阈值梯子的各臂、三个模型的各列、三条文本轨的各列, 都各自进入 just-identified 的独立回归并排呈现, 互为稳健性、不分主次, 严禁把梯子臂、模型臂或轨道臂混入同一个 over-identified 的 GMM 方程去做 Hansen J 过度识别检验 — 它们是同一构念的替代测量, 相关性极高, 混用只会制造虚假的过度识别自由度。跨模型推断纪律有两条: 第一, 阈值语义是 model-specific 的, 不同模型的负面概率标定不同, 同一 tau 在不同模型上切出的尾部截然不同, 因此禁止直接比较占比水平, 跨模型只比较各自回归的标准化回归系数; 第二, 跨模型的多重假设校正走 Romano & Wolf (2005) 的逐步降压程序, 由根级 FWER 模板在同构念替代测量族上统一执行, 家族内的阈值梯子属规格稳健性并排, 不适用该模板。极端负面占比在机制检验中的典型用法是替换均值语调作解释变量, 检验"结论是否由尾部报道驱动", 或与均值语调同时呈现以区分水平效应与尾部效应。在与外部财务后果变量对接时, 本家族的自然假设形态是: 极端负面占比的抬升先于或伴随融资成本上升、存款增速放缓、监管关注加强等阈值型后果, 且该关联在控制均值语调后仍存留 — 这是"尾部信息含量超出均值"的可检验表述。面板回归的标准配置为银行与年份双固定效应加银行层面聚类, 稀疏臂可改用报道量加权或把占比二值化为"存在极端负面报道"的事件指示以缓解小分母噪声; 无论哪种形态, 梯子各臂都必须各自单独进入方程, 并排呈现于同一表格的相邻列, 这既是稳健性展示的惯例, 也是前述禁混 Hansen J 铁律的操作化。

【与相邻测度的构念区分】
与本家族最近邻的测度有六类, 须逐一划界。其一, 逐模型负面概率均值列 (模型名加 neg 后缀族): 那是负面概率的一阶矩, 对全体报道的负面强度取平均, 而本家族是越过高阈值的报道占比, 是尾部质量测度; 一组温和偏负的报道会推高前者却完全不触碰后者。其二, 逐模型净语调 (net_tone 族): 正负概率之差的均值, 双向对称测度, 正面报道的增加会改变它, 却不影响本家族。其三, 语调熵 (tone_entropy 族): 测量模型判类的犹豫程度, 是不确定性构念, 与负面方向无关; 一篇被模型以接近均匀概率判类的报道熵最高, 却几乎必然不计入极端负面。其四, 净语调偏度 (net_tone_skew 族): 刻画银行年度内报道语调分布的不对称性, 是相对形状测度, 与占比的绝对水平正交。其五, 跨模型分歧列 (bert_xmodel 双轨): 测量三个模型互相之间的标签不一致度, 构念是测量分歧而非情绪本身。其六, LLM 路线与词典路线的负面测度 (LLM 逐家语调、词典负面词占比): 测量技术完全独立, 与本家族构成方法三角验证的另外两角, 而非同族变体。此外须与共现面板管道中的报道计数类负面指标区分: 那些是事件计数, 本家族是条件占比, 分母口径不同。

Wei, Wei, Jing & Jing (2025, Research in International Business and Finance) 利用中国上市银行年报文本语调构造情绪测度, 检验负面语调与银行风险承担行为之间的关系, 为本家族极端负面占比测度在银行文本情绪—风险行为传导机制上的应用提供了2025年最新的同类中国银行文本情绪证据。

【已知局限与稳健性梯子】
第一, 阈值的跨模型不可比性是本家族最重要的解释边界。三个模型的概率输出未经联合校准, finbert2 是二分类模型, 正负概率和接近一, 没有中性类分走概率质量, 其负面概率的分布整体右移, 同一阈值切出的"极端"篇数与三分类模型不可比; 因此任何叙述都不得写成"模型甲的极端负面占比高于模型乙", 只能写成"在模型甲的测量下该效应的标准化系数如何"。第二, 阈值选择本身是研究者自由度, 应对方式即三档梯子: canonical 取零点九零, 宽臂零点八零把中度负面纳入尾部、占比更高更平滑, 严臂零点九五只留最极端报道、更稀疏方差更大; 主结论须在三臂下方向一致、显著性格局相近方可声称对阈值稳健。第三, 概率来自滑动窗口置信度加权池化, 超长报道的窗口聚合是近似而非全文一次前向, 长文的极端判定可能被稀释; 三轨中 ctx 与 ss 文本更短, 受此影响更小, 构成天然的敏感性检查。第四, 报道少的银行年度格点占比波动剧烈, 一篇极端报道即可使小分母格点跳变, 回归中应配合报道量控制或加权; 早期试跑环境短面板上部分格点稀疏属预期退化, 生产全量语料下缓解。第五, 留篇门控为 full-only, ctx 与 ss 轨的占比继承 full 留篇集, 若门控模型对极端负面报道的验证通过率存在系统差异, 三轨会同向受影响, 这是三法三角验证而非单轨内部能解决的问题。第六, 本家族确定性来自模型权重与阈值比较, 不含随机采样环节, 离线重跑可复现; 重跑阶段二十三须置 HF 离线开关, finbert2 缺席时其九列整族缺失属合法降级而非数据损坏。

## VAR: fin_sent_zh_xneg_frac_ctx

【变体差分】
本列是 fin_sent_zh 模型、canonical 阈值零点九零、ctx 轨的极端负面占比, 与家族 canonical 列 (同模型同阈值的 full 轨) 的唯一差分维度是文本轨道。fin_sent_zh 为基于金融短语库微调的公开中文金融三分类模型, 输出正面、中性、负面三类概率, 本列消费其 ctx 轨负面概率列。ctx 轨文本 = 标题拼接目标银行实体邻域窗口, 在阶段十四物化, 目的在于剔除与目标银行无关的篇章段落, 降低把同篇报道中其他主体的负面叙述误归给目标银行的归因噪声; 对于一篇同时评述多家银行的行业综述, full 轨可能因他行的极端负面段落而将整篇判为强负面, ctx 轨则只让目标银行邻域的措辞说话。代价是窗口截断可能丢失篇章级语气铺垫, 且实体窗口无法命中时存在回退。行宇宙遵循 full-only 留篇门控, 本列是 conditional-on-full 的测度轨: 篇是否入宇宙由 full 轨门控决定, 本列仅改变入选篇的测量文本。与同模型 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排进独立回归, 禁混同一 over-identified Hansen J。分母为该银行年度内 ctx 轨概率非缺篇数, 缺失指示不填零。本列相对 full 轨结论的典型用法是归因检验: 若 full 轨效应在本列复现, 说明极端负面确实指向目标银行本身, 而非同篇他行叙述的溢出。

## VAR: fin_sent_zh_xneg_frac_full

【变体差分】
本列是 fin_sent_zh 模型在 canonical 配置下的极端负面占比: 阈值取梯子的 canonical 档零点九零 (列名无阈值后缀即此档), 文本轨取 full 轨 (标题 prepend 拼接全文正文), 是该模型九个家族列中的基准列, 列清单将其标记为 core, 理由是它同时落在三个 canonical 维度的交点上 — canonical 阈值、canonical 轨道、以及 BERT 三模型并排中作为公开可复现模型的一支。模型本体为 bardsai 发布的中文金融情感三分类模型, 在金融短语库语料上微调, 是三个模型中唯一以句子级金融陈述标注为监督信号的模型, 其负面概率对措辞级负面断言较敏感。本列的构造语义: 对该银行该年度 full 留篇集内每篇报道, 取 fin_sent_zh 在 full 轨文本上输出的负面类概率, 概率严格大于零点九零记一、不大于记零、概率缺失保持缺失, 再对指示取均值; 分母为概率非缺篇数, 空文本与推理失败篇被缺失掩码自然排除。留篇门控为 full-only 口径, 本列的文本轨与门控轨重合, 因此它是三轨中唯一"宇宙与测量同轨"的列, 也因此被指定为该模型极端负面测度的 headline 位置。解释时的并排纪律: 与同模型的 ctx、ss 轨列, 与同轨的 t80、t95 阈值臂, 以及与 finbert_cn、finbert2 两个模型的对应列, 均为互为稳健性、不分主次的 just-identified 并排臂, 严禁混入同一 over-identified Hansen J; 尤其注意与 finbert2 对应列的水平不可直接比较, 因为二分类模型无中性概率质量, 同一阈值的尾部语义不同, 跨模型只比较标准化回归系数。与相邻列的构念边界: 它不是 fin_sent_zh 负面概率均值 (一阶矩), 不是净语调 (双向差), 不是熵 (犹豫度), 而是高置信负面报道的条件占比; 一个格点上它的抬升意味着该年度出现了模型几乎不留余地判负的报道集中出现, 这是挤兑触发、监管关注类非线性后果研究中最贴近机制的测量形态。使用建议为替换或伴随均值语调进入回归, 检验尾部驱动假说。本列属非嵌入 carve-out, 无 _lg 孪生; per-model 独立降级下, 该模型为公开 HF 权重, 正常配置下恒在场。

进一步说明本列在三法三角中的位置与解释要点。情感测量在本管道中有三条彼此独立的技术路线: 三家大模型投票、六部词典规则计分、三个 BERT 模型概率推理; 本列所在的 BERT 路线不依赖关键词命中也不依赖生成式模型的指令遵循, 而是由判别式微调模型直接输出类别概率, 其误差结构与另两条路线正交, 这正是它作为旁证路线的价值。在 BERT 路线内部, 本列相对逐模型负面概率均值的增量在于把"负面强度的平均水平"换成"高置信负面的发生频率", 两者在报道情绪同质的格点上高度相关, 在情绪两极分化的格点上分离 — 后者恰是尾部机制最关心的情形。解释单篇层面的语义时应记住: 金融短语库的监督信号以陈述句级金融事实为主, 该模型对"业绩恶化""风险暴露"类事实性负面表述的判负置信度高, 对反讽、隐喻类软性负面相对不敏感, 这一特性使本列偏向捕捉硬信息负面而非修辞负面, 与词典法的负面词占比形成有意义的构念互补。复现口径: 给定阶段二十三落盘的概率列, 本列可离线逐位复现, 无任何付费或随机环节。

## VAR: fin_sent_zh_xneg_frac_ss

【变体差分】
本列是 fin_sent_zh 模型、canonical 阈值零点九零、ss 轨的极端负面占比, 差分维度是文本轨道取三轨中最窄的同句共现窗。ss 轨文本 = 标题拼接"目标银行与金融科技词出现在同一句"的句子及其前后各一句 (半径由 config 的 ss_sentence_radius 控制, 默认一句), 是对银行与金融科技议题交叠最精确的文本切片: 本列因此测量的是"在银行金融科技语境最浓缩的表述里, 模型以高置信度判负的报道占比", 对金融科技战略相关的负面评价最敏感, 而对银行其他业务线的负面新闻最不敏感。回退语义镜像 ctx 口径: 当该篇不存在银行与金融科技词的同句共现时, ss 文本回退为全文正文并置回退标志位, 极端情形金融科技词表缺失则全体回退、优雅降级; 回退篇的测量因此与 full 轨趋同, 解释 ss 轨结果时应意识到其与 full 的差异集中体现在非回退篇上。行宇宙依 full-only 留篇门控为 full 留篇集子集, 分母 = ss 轨概率非缺篇数。与同模型 full、ctx 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。本列的典型价值场景是金科议题机制检验: 当研究问题是"极端负面舆情是否特别针对银行的金融科技布局"时, 本列相对 full 轨的增量差异即为直接证据来源。

## VAR: fin_sent_zh_xneg_frac_t80_ctx

【变体差分】
本列是 fin_sent_zh 模型、宽阈值臂零点八零、ctx 轨的极端负面占比, 相对家族 canonical 存在两个差分维度: 阈值由零点九零放宽到零点八零, 文本轨由 full 换为银行实体窗口 ctx。放宽阈值把"中度偏强"的负面报道也纳入尾部计数, 使占比水平系统性不低于同轨 canonical 列 — 三档指示由同一概率列同一缺失掩码生成, 该单调关系在每个银行年度格点上精确成立, 违反即数据损坏。宽臂的作用是平滑与功效: 在报道量少或极端报道稀缺的格点上, 严阈值占比接近退化, 宽臂提供更连续的变异来源, 代价是把部分并非真正极端的报道混入尾部, 构念纯度下降。ctx 轨含义与同模型 ctx canonical 列一致: 只让目标银行实体邻域的文本说话, 抑制他行负面叙述的归因污染, 行宇宙仍由 full-only 门控决定。使用口径: 本列与同轨 canonical、t95 构成阈值梯子三臂, 与 full、ss 轨构成轨道三臂, 各臂互为稳健性、不分主次, 各自 just-identified 并排回归, 禁混同一 over-identified Hansen J; 主结论应在阈值三臂下方向一致方可声称对阈值选择稳健。金融短语库监督的事实性判负倾向在本臂同样成立, 宽阈值只放宽置信门槛, 不改变模型偏好硬信息负面的构念底色。

## VAR: fin_sent_zh_xneg_frac_t80_full

【变体差分】
本列是 fin_sent_zh 模型、宽阈值臂零点八零、full 轨的极端负面占比, 与家族 canonical 列同模型同轨, 唯一差分是阈值放宽一档。构造上, 该银行年度 full 留篇集内负面概率严格大于零点八零的报道计入分子, 概率非缺篇数为分母; 由三档指示同源同掩码的构造保证, 本列在每个格点上不小于无后缀 canonical 列、不小于 t95 列, 逐格精确单调。零点八零档的测量含义是"明显负面"而非"几乎确定负面": 三分类模型下负面概率过零点八零已要求正面与中性两类合计不足零点二, 判负已相当明确, 但尚未达到 canonical 档几乎排他的置信水平。该臂在梯子中的角色一是功效储备 — 尾部事件稀缺时提供更多变异; 二是构念边界检验 — 若某效应在 t80 显著而在 canonical 与 t95 消失, 说明驱动力量来自中度负面报道而非真正的极端尾部, 结论叙述须相应弱化。full 轨为标题拼接全文, 与留篇门控同轨。铁律: 与 canonical、t95 两臂互为稳健性、不分主次, 三臂各自 just-identified 并排, 禁混同一 over-identified Hansen J; 阈值语义 model-specific, 不与其他模型的 t80 列比较占比水平, 只比标准化系数。作为与 core 基准列同轨的相邻宽档, 本列是阈值稳健性表格中紧贴 headline 的第一比较臂。

## VAR: fin_sent_zh_xneg_frac_t80_ss

【变体差分】
本列是 fin_sent_zh 模型、宽阈值臂零点八零、ss 轨的极端负面占比, 相对家族 canonical 的差分是阈值放宽与文本轨收窄双重变化。ss 轨取标题拼接银行与金融科技词同句及前后一句的窗口, 是金融科技议题浓度最高的文本切片; 叠加宽阈值后, 本列测量"在银行金科最直接交叠的表述中, 明显负面 (概率过零点八零) 的报道占比", 是梯子中对金融科技相关负面舆情最敏感、门槛最宽的组合臂。ss 回退语义与家族口径一致: 无同句共现的篇回退为全文正文并置回退标志, 金融科技词表缺失时全体回退优雅降级, 因此稀疏共现样本下本列的实际测量文本可能大面积与 full 轨重合, 其相对 full 轨的增量信息集中在非回退篇。行宇宙为 full-only 留篇集子集, 分母 = ss 轨概率非缺篇数, 缺失不填零。单调性上本列逐格不小于同轨 canonical 与 t95 列。与同模型同轨的另两档阈值臂、与同档阈值的另两轨, 均互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。回退占比高的年份本列信息含量下降, 解读时可结合回退标志列的年度均值判断该格点的 ss 测量有多少真同句成分。

## VAR: fin_sent_zh_xneg_frac_t95_ctx

【变体差分】
本列是 fin_sent_zh 模型、严阈值臂零点九五、ctx 轨的极端负面占比, 差分维度为阈值收严一档加轨道取实体窗口。零点九五档只统计模型以近乎排他置信度判负的报道 — 三分类下正面与中性合计不足零点零五 — 是梯子中构念最纯、噪声最低但也最稀疏的一臂; 多数银行年度格点上此类报道为零, 占比呈大量零值与少量正值的混合分布, 回归中更接近事件强度指标, 小分母格点上单篇报道即可造成跳变, 应配合报道量控制解释。ctx 轨把测量文本限定在目标银行实体邻域, 与严阈值叠加后, 本列刻画"明确针对目标银行本身的、模型几乎不留余地判负"的报道占比, 是二十七列中归因最严格的组合之一, 适合作为"结论是否由确凿指向目标银行的极端唱衰驱动"的机制检验臂。行宇宙由 full-only 门控给定, ctx 为 conditional-on-full 测度轨; 分母 = ctx 轨概率非缺篇数。逐格单调上本列不大于同轨 canonical 与 t80。三阈值臂与三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。当研究叙事需要"确凿针对本行的极端唱衰"这一最强表述时, 本列是该模型九列中最接近该表述的测量形态。

## VAR: fin_sent_zh_xneg_frac_t95_full

【变体差分】
本列是 fin_sent_zh 模型、严阈值臂零点九五、full 轨的极端负面占比, 与家族 canonical 同模型同轨, 唯一差分是阈值收严至梯子顶档。测量含义是该银行年度 full 留篇集中被模型以近乎确定的置信度判为负面的报道占比: 概率过零点九五要求其余两类概率合计不足零点零五, 在实践中对应措辞严厉、通篇负面、无对冲表述的报道。该臂在梯子中的角色是构念上限检验: 若主效应随阈值收严而增强, 说明后果变量确由分布最尾部驱动, 尾部机制叙事得到最强支持; 若在本臂消失, 则效应更可能来自中度负面报道的量变。统计性质上本臂最稀疏, 零膨胀最重, 格点方差最大, 早期试跑期短面板上大量格点取零属预期; 生产全量语料下有效变异恢复。分母与两个宽臂完全同源同掩码, 逐格满足本列不大于 canonical 不大于 t80 的精确单调。full 轨与 full-only 留篇门控同轨, 无 ctx、ss 的回退与窗口截断问题。铁律与家族一致: 阈值三臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 阈值语义 model-specific, 跨模型禁比占比水平。剂量反应式的展示建议: 把 t80、canonical 与本臂并排列于同表相邻列, 系数强度沿阈值收严的走向本身即是可读的机制证据。

## VAR: fin_sent_zh_xneg_frac_t95_ss

【变体差分】
本列是 fin_sent_zh 模型、严阈值臂零点九五、ss 轨的极端负面占比, 是该模型九列中约束最紧的组合: 文本上只取银行与金融科技词同句及前后一句的最窄切片, 阈值上只认几乎排他置信度的判负。它测量"在银行金科交叠最浓缩的表述里, 模型近乎确定判负"的报道占比, 对金融科技战略遭遇媒体极端唱衰的事件最具针对性, 例如涉及银行金科业务的重大风险事件报道。稀疏性是本列的主要统计特征: 严阈值与窄窗口叠加使非零格点稀少, 使用时宜作为事件敏感性臂而非主要变异来源。ss 回退语义照家族口径执行: 无同句共现篇回退为全文正文并置回退标志, 词表缺失则全体优雅回退, 回退篇上本列测量与同档 full 轨趋同。行宇宙 = full-only 留篇集子集, 分母 = ss 轨概率非缺篇数, 缺失指示不填零。逐格单调: 本列不大于同轨 canonical 与 t80 臂。使用纪律: 与同轨两档宽阈值臂、与同档两条宽轨, 皆为互为稳健性、不分主次的并排臂, 各自 just-identified 进独立回归, 禁混同一 over-identified Hansen J。若以事件指示形式使用, 建议将本列二值化为该年度是否存在同句极端负面报道, 以规避小分母占比的方差爆炸。

## VAR: finbert2_xneg_frac_ctx

【变体差分】
本列是 finbert2 模型、canonical 阈值零点九零、ctx 轨的极端负面占比, 差分维度为模型换成项目本地私有微调的二分类模型, 轨道取银行实体窗口。finbert2 仅输出负面与正面两类概率, 无中性类, 两类概率和接近一, 这带来与三分类模型的根本构念差异: 三分类模型可以把大量概率质量放到中性类, 其负面概率过阈值意味着同时压倒正面与中性两类; finbert2 的负面概率只需压倒正面一类, 同一阈值切出的尾部整体更宽, 占比水平系统性偏高。因此本列与另两个模型对应列之间禁止比较占比水平, 只比较各自回归的标准化系数。ctx 轨含义与家族口径一致: 标题拼接目标银行实体邻域窗口, 抑制他行叙述的归因污染, 行宇宙由 full-only 留篇门控给定, ctx 为 conditional-on-full 测度轨。per-model 独立降级: finbert2 依赖本地模型目录环境变量, 未配置时本列连同该模型全族缺席, 另两模型照常, 属合法降级非损坏。与同模型另两轨、同轨另两档阈值互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。实体窗口的短文本特性与二分类的强制表态在此叠加: 三分类模型会判中性的模糊窗口文本, 本模型仍须给出正负倾向, 故本列的占比底噪高于公开模型同位列, 解释时以组内变异为准。

## VAR: finbert2_xneg_frac_full

【变体差分】
本列是 finbert2 模型在 canonical 配置 (阈值零点九零、full 轨) 下的极端负面占比, 列清单标记为 core, 是 BERT 三模型并排中私有微调臂的基准列。finbert2 为项目自行微调的中文金融二分类模型, 经环境变量指向本地权重目录加载, 其在三模型三角中的独特价值有二: 其一, 它是唯一针对本项目语料域微调的模型, 对中国银行业新闻的语域、机构名与政策表述的适配性可能优于两个公开模型; 其二, 它提供了与公开模型架构决策独立的测量, 若三模型的极端负面占比在回归中给出同向结论, 测量误差同源性的担忧即被显著削弱。二分类结构对本列语义的影响必须写明: 无中性类意味着负面概率 = 一减正面概率 (近似), 模型被迫在正负之间二选一, 大量在三分类模型下会落入中性的模糊报道, 在 finbert2 下概率质量向两极分摊, 其负面概率分布整体比三分类模型右移, 同一零点九零阈值切出的"极端"实为"相当明确的负面", 尾部更宽、占比水平更高。因此第一铁律是跨模型水平不可比: 本列与 fin_sent_zh、finbert_cn 对应列之间只比较标准化回归系数, 任何"finbert2 测得的极端负面占比更高所以舆情更糟"的叙述都是构念错误。第二铁律是并排纪律: 本列与同模型另两轨、同轨另两档阈值、另两个模型的对应列, 全部互为稳健性、不分主次, 各自 just-identified 并排进独立回归, 禁混同一 over-identified Hansen J; 跨模型多重检验走根级 Romano-Wolf FWER 模板。第三是降级语义: 该模型缺席时本列整族不产, 面板中列缺席即合法缺席, 不得以零或均值填补。构造细节与家族一致: full 轨为标题拼接全文, 与 full-only 留篇门控同轨, 分子为负面概率严格大于零点九零的篇数, 分母为概率非缺篇数, 缺失指示保持缺失; 本列与同模型 t80、t95 臂逐格精确单调。另注意该模型的中性概率列是全缺失占位列, 家族的极端负面指示只读负面概率列, 不受占位列影响照常产出。

关于本列的解释还有两点值得展开。其一是熵测度联动的警示对本列的间接含义: 二分类模型的判类熵是净语调绝对值的严格单调递减变换, 换言之 finbert2 的"犹豫程度"与其"表态强度"在逐篇层面完全冗余, 因此在该模型上区分"模型犹豫"与"报道温和"是不可能的; 这意味着本列的高置信判负在 finbert2 语义下等价于"强烈表态", 而非三分类模型语义下"排除了中性解读之后的强烈表态", 机制叙述中引用本列时应使用前一种措辞。其二是缺席年份的处理纪律: 该模型的可用性取决于本地权重目录, 跨机器复现时若目录未配置, 本列在产出面板中整族不在场, 复现者不得将缺席解读为管道故障, 也不得以任何插补手段补齐 — 正确的做法是在该机器上仅以两个公开模型的对应列复现三角验证的公开侧, 并在稿件中披露私有臂缺席; 项目的验收测试对这一降级路径有显式覆盖, 缺席时另两个模型的列集与数值不受任何影响。这一"私有模型可缺席、公开结论可独立复现"的设计, 是本列虽为私有测量却不损害整体可复现性声明的原因。

## VAR: finbert2_xneg_frac_ss

【变体差分】
本列是 finbert2 模型、canonical 阈值零点九零、ss 轨的极端负面占比, 差分维度为私有二分类模型与最窄同句窗轨道的组合。ss 轨取标题拼接银行与金融科技词同句及前后一句, 测量银行金科议题最浓缩表述中的高置信负面占比; finbert2 的二分类结构在窄文本上有一个值得注意的交互: 短窗口文本语气线索少, 三分类模型倾向把模糊短文本判入中性, 而 finbert2 无中性出口, 必须在正负间表态, 因此在 ss 轨上二分类与三分类模型的测量分歧可能比 full 轨更大, 这恰是跨模型三角验证在窄轨上的价值所在。回退语义照家族口径: 无同句共现篇回退为全文正文并置回退标志, 金融科技词表缺失全体优雅回退; 回退篇上本列与同模型 full 轨趋同。行宇宙 = full-only 留篇集子集, 分母 = ss 轨概率非缺篇数。per-model 独立降级: 本地模型目录未配置时本列缺席, 属合法缺席。跨模型禁比占比水平只比标准化系数; 与同模型另两轨、同轨另两档阈值互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。当本列与三分类模型的 ss 同位列给出同向回归结论时, 窄轨结论对"中性出口有无"这一建模自由度即告免疫。

## VAR: finbert2_xneg_frac_t80_ctx

【变体差分】
本列是 finbert2 模型、宽阈值臂零点八零、ctx 轨的极端负面占比, 相对家族 canonical 的差分为模型、阈值、轨道三维同时偏离, 是梯子交叉臂之一。二分类模型叠加宽阈值使本列成为二十七列中尾部定义最宽的组合之一: 负面概率过零点八零在无中性类分流的概率结构下, 大体对应"负面明显占优"的报道, 涵盖面远宽于三分类模型同档阈值, 占比水平上本列通常是同轨同档三模型中最高的 — 再次强调这是概率标定差异而非舆情差异, 禁止跨模型比水平。ctx 轨限定目标银行实体邻域文本, 降低多主体报道的归因噪声。宽臂在该模型梯子中的作用与家族口径一致: 提供更平滑的变异与功效储备, 并充当构念边界检验 — 效应仅在宽臂显著则驱动力来自中度负面而非极端尾部。逐格单调: 本列不小于同模型同轨 canonical 与 t95 臂。行宇宙 full-only 门控, ctx 为 conditional-on-full; 模型缺席时整族合法缺席。阈值三臂、轨道三臂、模型三臂各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。分母与掩码口径照家族执行: 指示浮点存储、缺失保持缺失禁填零, 分母为该格点 ctx 轨概率非缺篇数。

## VAR: finbert2_xneg_frac_t80_full

【变体差分】
本列是 finbert2 模型、宽阈值臂零点八零、full 轨的极端负面占比, 与该模型 core 基准列同轨, 唯一差分是阈值放宽一档。在二分类概率结构下, 零点八零档的语义与三分类模型有实质差异: 三分类模型负面概率过零点八零已属明确判负, 而 finbert2 由于概率质量只在正负两类间分配, 过零点八零大致相当于"负面显著强于正面"的中等强度判断, 因此本臂在该模型内部承担的角色更接近"广义负面占比"而非严格意义的极端尾部, 解释时应据此校准措辞。它与同模型 canonical、t95 臂构成该模型的阈值梯子, 三档指示同源同掩码, 逐格满足 t80 不小于 canonical 不小于 t95 的精确单调; 主结论在三臂下同向方可声称对阈值稳健。full 轨为标题拼接全文正文, 与 full-only 留篇门控同轨, 无回退与窗口归因问题, 分母 = full 轨概率非缺篇数。per-model 独立降级: 本地权重目录未配置时本列随族缺席。使用纪律与家族一致: 阈值臂之间、与另两轨、与另两模型对应列之间, 互为稳健性、不分主次, 各自 just-identified 并排进独立回归, 禁混同一 over-identified Hansen J, 跨模型只比标准化系数。本臂另可用作私有模型的量纲敏感性参照: 其与本模型 canonical 档的占比落差幅度, 直观呈现了二分类概率右移对阈值切割的影响强度。

## VAR: finbert2_xneg_frac_t80_ss

【变体差分】
本列是 finbert2 模型、宽阈值臂零点八零、ss 轨的极端负面占比, 三个差分维度全部偏离家族 canonical: 私有二分类模型、最宽阈值档、最窄文本轨。其测量对象是银行与金融科技词同句邻域文本中"负面显著占优"的报道占比 — 二分类无中性出口加宽阈值, 使本列在三模型同位列中覆盖面最宽; 而 ss 窗口的议题浓缩性又把测量对准金融科技语境, 两个方向的松紧恰好互补, 使本列适合作为"金科相关负面舆情广义水平"的敏感性臂。回退语义照常: 无同句共现篇回退为全文正文并置回退标志, 词表缺失全体优雅回退, 回退面大时本列向同模型同档 full 轨收敛。行宇宙 = full-only 留篇集子集, 分母 = ss 轨概率非缺篇数, 缺失指示保持缺失。逐格单调: 本列不小于同模型同轨 canonical 与 t95。per-model 独立降级下模型缺席即全族合法缺席。铁律照家族执行: 阈值梯子臂、轨道臂、模型臂各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 与另两模型对应列禁比占比水平。若把本列用于"金科舆情广义负面"的描述性呈现, 应同时报告回退标志年度均值, 使读者能够判断窄轨语义在该样本上的实际覆盖面。

## VAR: finbert2_xneg_frac_t95_ctx

【变体差分】
本列是 finbert2 模型、严阈值臂零点九五、ctx 轨的极端负面占比。零点九五档在二分类概率结构下的含义是正面概率不足零点零五, 即模型近乎完全排除正面解读 — 这是 finbert2 梯子中唯一在语义强度上与三分类模型的 canonical 档大致相当的档位, 因为二分类的概率右移效应在极高阈值处被压缩; 但这仍是启发式对应而非校准等价, 跨模型比较仍只允许标准化系数。ctx 轨限定目标银行实体邻域, 与严阈值叠加后本列刻画"明确指向目标银行、模型几乎完全判负"的报道占比, 归因与置信双重严格。统计上本列稀疏, 零值格点多, 单篇极端报道可使小分母格点跳变, 宜配合报道量控制或作事件指示解释; 早期试跑期短面板大量取零属预期退化。行宇宙由 full-only 留篇门控决定, ctx 为 conditional-on-full 测度轨, 分母 = ctx 轨概率非缺篇数。逐格单调: 本列不大于同模型同轨 canonical 与 t80。模型缺席即全族合法缺席。三阈值臂与三轨、三模型各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。私有微调的语料域适配在本臂尤其可贵: 顶档置信加实体窗口下仍越线的判负, 最不可能来自领域外措辞的误读。

## VAR: finbert2_xneg_frac_t95_full

【变体差分】
本列是 finbert2 模型、严阈值臂零点九五、full 轨的极端负面占比, 与该模型 core 基准列同轨, 差分为阈值收严至顶档。测量含义: 该银行年度 full 留篇集中, finbert2 对全文文本给出的负面概率超过零点九五 — 即正面概率被压到不足零点零五 — 的报道占比。如同模型 t95_ctx 列所述, 顶档阈值部分抵消了二分类概率右移, 使本臂成为该模型内构念上最接近"真极端尾部"的档位, 是检验尾部机制叙事在私有模型测量下是否成立的关键臂: 若效应在 fin_sent_zh 与 finbert_cn 的 canonical 档成立, 且在 finbert2 的本臂同向, 则尾部结论获得跨架构、跨监督信号来源的三角支持。统计特征为高稀疏与零膨胀, 格点方差大, 解释时须配合报道量; 生产全量语料下变异恢复。构造细节: 三档指示同源同掩码, 本列逐格不大于同模型 canonical 与 t80 臂; full 轨与 full-only 留篇门控同轨; 分母 = 概率非缺篇数, 缺失指示禁填零。per-model 独立降级, 模型缺席全族合法缺席。铁律: 与同模型两档宽臂、另两轨、另两模型对应列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J, 跨模型禁比占比水平只比标准化系数。

## VAR: finbert2_xneg_frac_t95_ss

【变体差分】
本列是 finbert2 模型、严阈值臂零点九五、ss 轨的极端负面占比, 是该模型九列中最严组合: 顶档置信阈值叠加银行金科同句最窄文本窗。测量语义为"在银行与金融科技交叠最浓缩的表述中, 私有二分类模型几乎完全排除正面解读"的报道占比, 针对性指向银行金科业务遭遇媒体极端唱衰的具体事件, 是事件研究式机制检验的天然臂; 常态年份多数格点为零, 其非零跳变本身即携带事件信息。二分类与窄窗的交互在此档位表现为: 短文本线索少时模型仍须二选一表态, 但顶档阈值要求表态近乎排他, 实际能越线的多为措辞极重的同句表述, 构念纯度在该模型内最高。回退语义照家族口径: 无同句共现篇回退全文并置标志, 词表缺失全体优雅回退, 回退篇测量向同档 full 轨收敛。行宇宙 = full-only 留篇集子集, 分母 = ss 轨概率非缺篇数。逐格单调: 本列为同模型同轨三档中的下界臂。模型缺席全族合法缺席, 禁填补。与两档宽臂、两条宽轨、两个公开模型对应列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。展示上建议将本列与公开模型的对应严档臂并排呈现方向而非水平, 因为档位间的语义强度对应关系在二分类与三分类之间是错位的。

## VAR: finbert_cn_xneg_frac_ctx

【变体差分】
本列是 finbert_cn 模型、canonical 阈值零点九零、ctx 轨的极端负面占比, 差分维度为模型换为公开的中文金融语调三分类模型, 轨道取银行实体窗口。finbert_cn 即 yiyanghkust 发布的中文 finbert-tone 模型, 以金融语调标注为监督信号, 与 fin_sent_zh 的金融短语库监督来源不同, 两个公开三分类模型构成同架构异语料的平行测量, 其对应列之间的一致性是排除单一训练语料偏差的直接证据。本列消费该模型 ctx 轨负面概率: 文本为标题拼接目标银行实体邻域窗口, 把多主体报道中他行的负面叙述隔离在测量之外, 归因噪声低于 full 轨, 代价是丢失篇章级语气铺垫与窗口未命中时的回退。行宇宙遵循 full-only 留篇门控, ctx 为 conditional-on-full 测度轨, 分母 = ctx 轨概率非缺篇数, 缺失指示保持缺失禁填零。作为三分类模型, 其负面概率过零点九零意味着正面与中性合计不足零点一, 判负近乎排他, 尾部构念纯度高。与同模型 full、ss 轨及同轨 t80、t95 臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 与另两模型对应列禁比占比水平。语调监督的整篇基调倾向叠加窗口截断, 使本列偏向捕捉实体邻域行文的评价性负面, 与 fin_sent_zh 同位列的事实性负面互补。

## VAR: finbert_cn_xneg_frac_full

【变体差分】
本列是 finbert_cn 模型在 canonical 配置 (阈值零点九零、full 轨) 下的极端负面占比, 列清单标记为 core, 是 BERT 三模型并排中第二支公开模型的基准列。finbert_cn 为中文金融语调三分类模型, 输出中性、正面、负面三类概率, 其监督信号来自金融语调标注传统 — 该传统直接承接 Huang, Wang & Yang (2023) 所确立的金融领域 BERT 范式, 与 fin_sent_zh 所依托的金融短语库句子级标注形成语料来源上的独立平行。在三模型三角中, 本列与 fin_sent_zh 对应列的关系最为对称: 同为三分类、同为公开权重、同一概率语义, 二者对应列的回归结论若同向, 排除的是训练语料与标注偏好的特异性; 而与 finbert2 对应列的比较则跨越分类结构差异, 排除的是架构与类别设计的特异性。构造语义: 该银行年度 full 留篇集内, finbert_cn 对标题拼接全文的文本输出的负面概率严格大于零点九零者计入分子, 概率非缺篇数为分母, 缺失指示保持缺失; 负面概率过零点九零在三分类下要求正面与中性合计不足零点一, 对应几乎不留余地的判负报道, 构念为高置信极端负面尾部占比。full 轨与 full-only 留篇门控同轨, 宇宙与测量一致, 无 ctx 的窗口归因问题与 ss 的回退问题, 因此本列与 fin_sent_zh 的 core 列、finbert2 的 core 列共同构成家族的三支 headline 臂。解释纪律有三: 其一, 并排铁律 — 本列与同模型另两轨、同轨另两档阈值、另两模型对应列, 互为稳健性、不分主次, 各自 just-identified 并排进独立回归, 禁混同一 over-identified Hansen J; 其二, 阈值语义 model-specific, 跨模型禁比占比水平, 只比标准化回归系数, 跨模型多重检验走根级 Romano-Wolf FWER 模板; 其三, 构念边界 — 本列非负面概率均值、非净语调、非熵, 一个格点的抬升意味着高置信唱衰报道的集中出现, 对接的是储户与监管反应的非线性触发机制。逐格单调: 本列介于同模型同轨 t80 与 t95 之间。该模型为公开 HF 权重, 正常配置恒在场, 无降级顾虑; 本家族属非嵌入 carve-out, 无 _lg 孪生列。

补充两点该模型特有的解释语境。语调标注监督的含义: 与以句子级金融事实陈述为监督的 fin_sent_zh 不同, finbert_cn 的训练目标是篇章语调分类, 其判负更依赖整体行文的评价性倾向而非单句事实断言, 因此本列偏向捕捉"整篇基调的极端负面"而非"含有个别负面事实的报道", 与 fin_sent_zh 的 core 列形成事实性负面对基调性负面的构念互补 — 两列同向时, 既有硬信息负面又有基调负面的结论最为完整。滑动窗口聚合的影响: 该模型对超长报道按重叠窗口分段推理再按置信度加权合并, 篇章语调这种全局属性在窗口切分下比句级事实更易被稀释, 意味着本列对长篇深度负面报道的判定相对保守, 长文占比高的银行年度格点上本列可能低估极端负面 — 这是把 ctx 与 ss 两条短文本轨作为其并排稳健臂的另一层理由。复现口径与家族一致: 给定落盘概率列, 本列离线逐位可复现, 无付费与随机环节。最后一点关于本列在方法论文献中的定位: 词典法与监督学习法在披露文本情绪测量上的相对优劣已由 Frankel, Jennings & Lee (2022) 系统评估, 其结论是监督分类在样本外拟合上占优而牺牲可解释性; 本列作为监督分类的尾部占比派生, 恰是把这一样本外优势从均值水平推进到分布尾部的具体实现, 而其可解释性损失则由与词典负面词占比、LLM 逐家语调两条平行路线的三角对照来补偿。Loughran & McDonald (2016) 的综述亦提醒, 任何单一文本情绪工具都携带其训练来源的系统偏好, 因此本列的解释效力不寄托于该模型自身的绝对水平, 而寄托于它与另两模型对应列在标准化系数层面的方向一致性 — 这一并排互证结构是本列区别于任意单模型情绪指标的根本方法学立场。

## VAR: finbert_cn_xneg_frac_ss

【变体差分】
本列是 finbert_cn 模型、canonical 阈值零点九零、ss 轨的极端负面占比, 差分维度为轨道收窄到银行金科同句窗。ss 轨文本 = 标题拼接目标银行与金融科技词同句共现的句子及前后各一句, 是金融科技议题浓度最高的切片; 本列因此测量金融语调模型在金科语境最浓缩表述上的高置信判负占比, 与该模型 full 轨列的差异集中反映"极端负面是否特别集中于金科相关叙述"。作为三分类模型, finbert_cn 在短窗口文本上有充足的中性出口, 模糊短文本多被判中性而非强行两极化, 这使其 ss 轨占比相对保守, 与二分类 finbert2 的同位列形成有意义的测量对照。回退语义镜像 ctx 口径: 无同句共现篇的 ss 文本回退为全文正文并置回退标志, 金融科技词表缺失时全体回退优雅降级, 回退篇上本列测量与 full 轨趋同, 增量信息集中于非回退篇。行宇宙依 full-only 留篇门控为 full 留篇集子集, 分母 = ss 轨概率非缺篇数, 缺失不填零。与同模型 full、ctx 轨及同轨另两档阈值臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。当金科机制叙事需要"基调层面的极端负面聚焦于金科语境"这一证据时, 本列是该模型内最贴合的测量位。

## VAR: finbert_cn_xneg_frac_t80_ctx

【变体差分】
本列是 finbert_cn 模型、宽阈值臂零点八零、ctx 轨的极端负面占比, 相对家族 canonical 的差分为模型、阈值、轨道三维偏离。零点八零档在三分类结构下对应"明确负面但未至排他"的报道 — 正面与中性合计仍可达零点二 — 把中度偏强的负面纳入尾部, 提供比 canonical 更平滑的变异; ctx 轨限定目标银行实体邻域文本, 抑制多主体报道的归因污染。两者叠加后, 本列适合在极端报道稀缺、格点零膨胀严重的子样本中充当功效储备臂, 同时保持归因的严格性。构造细节与家族口径一致: 指示 = 负面概率严格大于零点八零, 缺失保持缺失, 分母 = ctx 轨概率非缺篇数; 三档指示同源同掩码, 本列逐格不小于同模型同轨 canonical 与 t95 臂, 违反单调即数据损坏。行宇宙由 full-only 留篇门控给定, ctx 为 conditional-on-full 测度轨。解释纪律: 若效应仅在本臂显著而在两个严档消失, 应将叙事从极端尾部弱化为广义负面; 阈值三臂、轨道三臂、模型三臂各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J, 跨模型禁比占比水平。语调监督在宽阈值下的覆盖面扩展主要来自评价性措辞偏负但保留部分对冲的报道, 构念上仍属基调负面而非事实负面。

## VAR: finbert_cn_xneg_frac_t80_full

【变体差分】
本列是 finbert_cn 模型、宽阈值臂零点八零、full 轨的极端负面占比, 与该模型 core 基准列同轨同模型, 唯一差分为阈值放宽一档。三分类结构下负面概率过零点八零已是明确判负 — 其余两类合计不足零点二 — 但保留了少量对冲空间, 因此本臂捕捉的是"明显负面"报道的占比, 覆盖面宽于 canonical 档的"几乎排他负面"。它在该模型阈值梯子中的双重角色与家族口径一致: 功效储备与构念边界检验。前者在报道稀少或极端事件罕见的格点上尤其重要, 宽臂的连续变异可避免回归退化; 后者体现为诊断价值 — 效应在本臂与 canonical、t95 三臂同向且强度随阈值收严递增, 是尾部机制的最强证据形态, 反之若仅宽臂显著则驱动来自中度负面。full 轨为标题拼接全文, 与 full-only 留篇门控同轨, 分母 = full 轨概率非缺篇数, 缺失指示禁填零; 三档同源同掩码, 本列逐格不小于 canonical 与 t95。该模型公开权重恒在场。铁律: 阈值三臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 与另两模型的 t80 列禁比占比水平, 跨模型推断只经标准化系数与根级 FWER 模板。本列同时是该模型 core 基准列在阈值稳健性表格中的第一相邻臂, 表格排布上通常置于 headline 列右侧。

## VAR: finbert_cn_xneg_frac_t80_ss

【变体差分】
本列是 finbert_cn 模型、宽阈值臂零点八零、ss 轨的极端负面占比, 差分为阈值放宽与文本轨收窄的组合。测量对象是银行与金融科技词同句邻域文本上, 金融语调模型给出明确负面判断 (概率过零点八零) 的报道占比: 窄窗口对准金科议题, 宽阈值保证变异充足, 该组合是检验"金科相关负面舆情的广义水平"的均衡臂 — 比同轨 canonical 更平滑, 比同档 full 轨更聚焦。三分类模型在短文本上的中性出口使其判负天然保守, 宽阈值恰好部分补偿这一保守性, 因此本列相对 finbert2 同位列的占比差距通常小于 canonical 档的对应差距; 但这仍属概率标定差异, 跨模型禁比水平的铁律不因差距缩小而放松。回退语义照家族口径: 无同句共现篇回退为全文正文并置标志, 词表缺失全体优雅回退, 回退面大时本列向同模型 t80_full 收敛。行宇宙 = full-only 留篇集子集, 分母 = ss 轨概率非缺篇数, 缺失保持缺失。逐格单调: 本列不小于同轨 canonical 与 t95。与同模型另两档、另两轨及另两模型对应列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。分母口径照家族: ss 轨概率非缺篇数, 空文本与推理失败篇经缺失掩码自然剔除。

## VAR: finbert_cn_xneg_frac_t95_ctx

【变体差分】
本列是 finbert_cn 模型、严阈值臂零点九五、ctx 轨的极端负面占比。三分类结构下负面概率过零点九五要求正面与中性合计不足零点零五, 是该模型判负置信度的极限档; 叠加 ctx 轨的实体窗口限定后, 本列测量"明确指向目标银行、金融语调模型以近乎完全的置信度判负"的报道占比, 与 fin_sent_zh 的同位列构成双公开模型在最严归因加最严置信组合上的平行测量。其统计特征为高稀疏: 常态经营年份多数格点为零, 非零值多对应重大负面事件年份, 回归中更接近事件强度指标, 小分母格点单篇跳变问题显著, 应配合报道量控制; 早期试跑期短面板大面积取零属预期退化, 生产全量语料下恢复变异。构造细节: 指示同源同掩码, 本列逐格不大于同模型同轨 canonical 与 t80; 行宇宙由 full-only 留篇门控给定, ctx 为 conditional-on-full 测度轨, 分母 = ctx 轨概率非缺篇数, 缺失禁填零。铁律照家族执行: 阈值三臂、轨道三臂、模型三臂互为稳健性、不分主次, 各自 just-identified 并排进独立回归, 禁混同一 over-identified Hansen J, 跨模型禁比占比水平只比标准化系数。与 fin_sent_zh 同位列并排呈现时, 两个公开三分类模型在最严组合上的方向一致性是本档位最有说服力的稳健形态。

## VAR: finbert_cn_xneg_frac_t95_full

【变体差分】
本列是 finbert_cn 模型、严阈值臂零点九五、full 轨的极端负面占比, 与该模型 core 基准列同轨, 差分为阈值收严至梯子顶档。测量含义: 该银行年度 full 留篇集中, 金融语调模型对标题拼接全文给出的负面概率超过零点九五的报道占比 — 正面与中性两类合计被压到不足零点零五, 实践中对应通篇严厉、无任何对冲表述的极端唱衰报道。本臂是该模型构念纯度的上限: 若效应强度沿 t80、canonical、本臂逐级递增, 尾部机制叙事获得单调剂量反应式支持; 若在本臂消失, 结论应回撤到广义负面驱动。与 fin_sent_zh 的 t95_full 列平行使用可进一步检验该单调格局是否跨公开模型稳健。统计上本臂零膨胀最重、格点方差最大, 单篇极端报道即可主导小分母格点, 使用时须配合报道量控制或以事件指示形式进入回归; 短面板开发环境大量取零属预期。构造细节: full 轨与 full-only 留篇门控同轨, 无回退与窗口问题; 三档指示同源同掩码, 本列为同模型同轨梯子的逐格下界; 分母 = 概率非缺篇数, 缺失指示保持缺失。该模型公开权重恒在场, 无降级顾虑。铁律: 与两档宽臂、另两轨、另两模型对应列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 跨模型多重检验统一走根级 Romano-Wolf 模板。

## VAR: finbert_cn_xneg_frac_t95_ss

【变体差分】
本列是 finbert_cn 模型、严阈值臂零点九五、ss 轨的极端负面占比, 是该模型九列中约束最紧的组合臂: 顶档置信阈值叠加银行金科同句最窄窗口。测量语义为"在银行与金融科技交叠最浓缩的表述中, 金融语调模型近乎完全排除非负解读"的报道占比, 其非零值高度指向银行金科业务的具体负面事件 — 风险暴露、监管处罚、项目失败类报道的同句表述 — 因此本列的角色是金科负面事件的敏感性臂与机制检验臂, 而非常规变异来源。三分类模型的中性出口叠加顶档阈值使本列在全家族二十七列中最为稀疏保守, 与 finbert2 同位列 (二分类、无中性出口) 的对照最为极端, 两者结论若仍同向, 是跨分类结构稳健性的最强形态。回退语义照家族口径: 无同句共现篇回退为全文正文并置回退标志, 金融科技词表缺失时全体优雅回退, 回退篇测量向同模型 t95_full 收敛。行宇宙 = full-only 留篇集子集, 分母 = ss 轨概率非缺篇数, 缺失禁填零。逐格单调: 本列为同模型同轨三档下界。铁律: 与两档宽臂、两条宽轨、另两模型对应列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 跨模型禁比占比水平。

<!-- rendered-citations:begin -->
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Lizelle Ann V. Cruz. (2026). Sentiment as Early Warning: A Systemic Risk Index for the Philippines. Journal of Risk and Financial Management. https://doi.org/10.3390/jrfm19050302
Dimitris Anastasiou, Apostolos Katsafados, Christos Tzomakas. (2025). Banks' stock price crash risk prediction with textual analysis: a machine learning approach. Annals of Operations Research. https://doi.org/10.1007/s10479-025-06567-y
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Jiang, E. X., Matvos, G., Piskorski, T., & Seru, A. (2024). Monetary tightening and U.S. bank fragility in 2023: Mark-to-market losses and uninsured depositor runs? Journal of Financial Economics, 159, 103899. https://doi.org/10.1016/j.jfineco.2024.103899
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Goldstein, I. (2023). Information in financial markets and its real effects. Review of Finance, 27(1), 1-32. https://doi.org/10.1093/rof/rfac052
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Sun, C., Qiu, X., Xu, Y., & Huang, X. (2019). How to fine-tune BERT for text classification? Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science, Springer. https://doi.org/10.1007/978-3-030-32381-3_16
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Wei, L., Wei, M., Jing, H., & Jing, Z. (2025). Annual report tone and bank risk-taking behavior: Evidence from China. Research in International Business and Finance. https://doi.org/10.1016/j.ribaf.2025.102881
<!-- rendered-citations:end -->
