---
family_id: F077
columns:
- avg_you_2018_pos_ratio_ctx
- avg_you_2018_pos_ratio_full
- avg_you_2018_pos_ratio_ss
unit: 比率 (正面词次占 word-token 数之比, 无量纲; 文章级 ∈ [0,1], 面板级为银行-年内文章均值)
formula: "avg_you_2018_pos_ratio{trk} = mean_over_articles(you_2018_pos_ratio{trk}), trk ∈ {full, ctx, ss}; 文章级 you_2018_pos_ratio = pos_count / n_word_tokens; pos_count = 经否定/程度/转折状态机处理后最终极性为正的 you_2018 词典命中词次数, 外加该词典 5 个 positive∩negative 跨类重叠词的命中次 (2026-06-24「保留并两侧计数」决策: 重叠词命中同时 +1 计入 pos_count 与 neg_count, 与翻号及幅度无关); n_word_tokens = 剔除纯标点/纯数字 token 后的词元数; n_word_tokens = 0 或空文本或词典缺失 → NaN"
producer: news_process/pipeline/sentiment/tone_words.py::_analyze_single_article (打分内核 _compute_sentiment_with_rules); 面板聚合 news_process/pipeline/panel/encode.py (avg_{d}_pos_ratio{track} = ({d}_pos_ratio{track}, 'mean')); Stata 标签 news_process/pipeline/panel/export.py + stata_export.py
upstream:
- config/tone_dicts.json (you_2018 词典: positive 1,425 / negative 1,583 / definite 388 / ambiguous 178 [后两类 v3.5.1 起供 clarity 用, 不入 pos_ratio]; positive∩negative 跨类重叠 5 词两侧计数)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- 22_words_tone.parquet (文章级 you_2018_pos_ratio_{full,ctx,ss})
- 21_tone_llms.parquet (llm_verified_full 留篇门控, full-only 口径 2026-06-29)
citations:
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: Advance online publication
- doi: 10.1007/s10479-025-06567-y
  type: journal
  authors: Anastasiou, D., Katsafados, A., & Tzomakas, C.
  year: 2026
  title: "Banks' stock price crash risk prediction with textual analysis: A machine learning approach"
  venue: Annals of Operations Research
  vol: 357
  issue: 1
  pages_or_artno: 89-111
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: "100148"
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.1080/00036846.2025.2536881
  type: journal
  authors: Wu, M., Shen, L., Wu, T., & Shao, Y.
  year: 2025
  title: "Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China"
  venue: Applied Economics
  pages_or_artno: Advance online publication
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1016/j.intfin.2024.102002
  type: journal
  authors: Koranteng, B., & You, K.
  year: 2024
  title: "Fintech and financial stability: Evidence from spatial analysis for 25 countries"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 93
  pages_or_artno: "102002"
- doi: 10.1093/qje/qjac038
  type: journal
  authors: Abadie, A., Athey, S., Imbens, G. W., & Wooldridge, J. M.
  year: 2023
  title: "When should you adjust standard errors for clustering?"
  venue: The Quarterly Journal of Economics
  vol: 138
  issue: 1
  pages_or_artno: 1-35
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
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1177/0081175018777988
  type: journal
  authors: Muñoz, J., & Young, C.
  year: 2018
  title: "We ran 9 billion regressions: Eliminating false positives through computational model robustness"
  venue: Sociological Methodology
  vol: 48
  issue: 1
  pages_or_artno: 1-33
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
new_dois: []
---

## CORE

【构念与来源】
本家族测度银行-年面板层面的词典法正面情感词密度: 对每一篇经留篇门控保留的目标银行金融科技相关报道, 以 You、Zhang 与 Zhang 构建的中文金融情感词典 (管道内代号 you_2018) 为量尺, 统计经语言学规则处理后最终极性为正面的词典命中词次数, 除以该篇文章剔除纯标点与纯数字后的词元总数, 得到文章级正面词占比 you_2018_pos_ratio; 再在每个银行-年单元内对全部留存文章取无加权算术均值, 得到面板列 avg_you_2018_pos_ratio。三条轨道 full、ctx、ss 分别在三种文本视窗上重复同一计算, 构成同一构念在不同文本口径下的三个并排测量。本族的核心构念不是情感的方向, 而是正面表述在一篇报道篇幅中的浓度: 它回答的问题是, 在关于某家银行金融科技动向的媒体叙事里, 有多大比例的词是被明确渲染为正面的, 而非这些正面词与负面词相抵之后偏向哪一侧。

词典来源上, you_2018 出自 You、Zhang 与 Zhang (2018) 一文, 该文的主题是媒体报道对中国股票市场的影响, 即所谓谁捕获了这支笔的力量, 关切的是国有媒体与市场化媒体在财经报道中的语调差异及其定价后果。为支撑这一议题, 作者需要一套能在中文金融新闻上稳定判读语调的词表, 由此形成了本管道采用的情感词典。该词典有两个正交维度: 一是语调维度, 区分积极与消极; 二是准确性维度, 区分明确与模糊。管道内的实现依据 You et al. (2018) 一文的补充材料重新生成词表, 收录正面词 1,425 条、负面词 1,583 条, 另含确定性词 388 条、模糊性词 178 条, 词汇合计 3,574 条, 其中一部分沿用 Loughran 与 McDonald 中文译本, 另一部分由作者随机审阅约两千篇金融新闻自建。本族只取其中的正面词集作为分子的极性判据, 语调维度中的负面词集喂给镜像列 avg_you_2018_neg_ratio, 准确性维度的确定性与模糊性两类词自 v3.5.1 起被激活为独立的报道清晰度指标 (clarity), 与本族分属不同构念, 不进入 pos_ratio 的任何计算。这一点是 you_2018 相对管道内其它五部词典的独有结构特征: 它是唯一自带准确性维度的词典, 因此在同一词典文件里同时供养了情感浓度与信息清晰度两条彼此正交的测度链。

构念设计上, 本族刻意与净语调分离。净语调类测度把正负两侧信息压缩为单一带号分值, 当一篇报道同时含有强烈正面与强烈负面表述时, 两侧在分子中相互抵消, 净值趋近零, 与一篇通篇平淡、几乎不含情感词的报道在净语调上不可分辨, 这就是词典法文献所称的极性对冲掩蔽问题。把正面侧单独析出为独立协变量后, 回归设计可以让正负两侧各自进入模型、比较两侧系数的相对大小, 也可以用两侧占比构造情感分歧类的二阶指标, 从而保留净语调压缩过程中丢失的单侧强度信息。管道内, 本族与镜像列 avg_you_2018_neg_ratio 构成正负分离对, 并作为下游词级情感分歧指标族的直接输入; 六部词典的同名正负占比对共同支撑跨词典分歧的计算。换言之, 本族既是一个可以独立进入回归右端的浓度型协变量, 又是一个专供二阶分歧构念取用的原材料, 双重身份决定了它的定义必须是分侧的、可加的、不做净额抵消的。

应用语境上, 本面板的观测单元是中国商业银行乘年份, 语料是银行与金融科技共现的媒体报道。银行层面的媒体情感测度已有直接同域先例: Fang et al. (2024) 用中国银行业的媒体情感解释存款稳定性与系统性风险, 证明报道情感在银行样本上具有经济后果层面的信息含量; Chen et al. (2022) 表明银行的信息透明度会经由存款流动影响其融资端, 为媒体所携带的银行信息为何重要提供了机制侧的支撑。金融科技切片则连接到本管道的研究议题: Wu et al. (2025) 直接考察中国银行与金融科技企业的战略合作及其风险承担后果, 与本面板银行乘金科报道的语料切片同域; Koranteng 与 You (2024) 从跨国空间分析给出金融科技与金融稳定关系的宏观证据, 为该切片的研究问题提供更广的背景。you_2018 的母文关切国有与市场化媒体的语调分化, 这一视角与本面板刻意选取银行金科报道语料相契合, 因为该类报道恰是媒体立场差异最容易显现的题材之一。

【方法学与计算】
文章级计算位于管道 stage 22 (producer 为 pipeline/sentiment/tone_words.py), 入口函数 _analyze_single_article, 打分内核 _compute_sentiment_with_rules。分词使用 stage 22 词典匹配专用的独立 jieba Tokenizer 实例 (注入隔离, 见 _get_tone_tokenizer): 领域复合词只注入此实例, 全局 jieba 分词器保持纯净, 以免污染其它依赖词性标注的度量; jieba 版本冻结在 0.42.1。每篇文章仅切分一次, 六部词典共享同一份词元序列, 调用方预切的 raw token 复用回内核以保证逐字节等价。计数遵循一个逐词元的状态机: 遍历词元序列时维护否定窗口、程度副词倍率与转折激活三个句法状态; 遇句末标点全部重置, 实现从句级作用域; 遇转折连词激活转折并重置否定与程度; 遇否定词开启定长否定窗口; 遇程度副词记录倍率。当词元命中 you_2018 词典时, 取词典基础分, 正面词与负面词为满幅; 若处于否定窗口内则翻转符号, 再乘以程度倍率 (最高约 3.0) 与转折增强 (约 1.5), 得到该词次的最终带号分值。这套从句级作用域的规则设计遵循转折效应限定为从句级的语言学惯例, 使否定与转折不会跨句串味。

本族分子 pos_count 是计数口径: 统计最终带号分值为正的命中词次数, 每个词次记一次, 与其幅度无关。由此有两个必须写明的、专属 you_2018 的推论。其一, 否定翻转改变计数归属, 不乐观里的乐观最终计入负面词次而非正面词次, 因此本族并非裸词表匹配频次, 而是语言学规则处理后的极性计数, 这一点区别于纯词频法。其二, you_2018 词典存在 5 个正负跨类重叠词, 即同时出现在 positive 与 negative 两侧的词; 依据 2026-06-24 用户「保留并两侧计数」决策 (逆转此前的双侧剔除做法), 这 5 个词不再被判定单极, 而是登记到跨类两侧计数词表, 命中时同时 +1 计入 pos_count 与 neg_count。这一规则对本族的直接含义是: 一次跨类重叠词命中会无条件把 pos_count 抬高一次, 且这一抬高与该词次的否定翻号、程度缩放、转折增强全部无关 (两侧计数分支在符号判定之前触发, 幅度对称抵消, 只作用于分母的净语调而不改变各自的计数)。这是 you_2018 家族区别于无跨类重叠的 du_2022 家族的关键方法学特征: du_2022 无重叠词, 其正面占比纯由单极正面命中构成; 而 you_2018 的正面占比在结构上包含了 5 个双向词的贡献。需要强调的是, you_2018 词典不含政治正面词类 (政治词单列与降权是 du_2022 的独有构造), 因此政治词权重梯子 (polw00、polw05、polw10 三权重) 不为 you_2018 物化任何变体, 本族在该维度上天然不涉。

分母 n_word_tokens 为 word-token 口径: 剔除纯标点与纯数字词元后的词元数, 复用 lm_non_sentiment 模块的非词正则 _LMFLS_NONWORD_RE, 与该模块占比类分母的修复同口径。分母收紧的动机是标点与数字词元的占比逐篇差异大且非常数, 若以物理词元总数作分母, 会引入与内容无关的稀释噪声, 使占比在标点密集的短讯与正文连贯的长稿之间不可比; 而词典命中词本为真词, 分子不受此剔除影响。文章级值保留六位小数。缺失语义为: 空文本、纯符号文本、分母为零, 或 you_2018 词典整体缺失时, 文章级值置 NaN, 与有词但零命中的真零严格区分; 该缺失契约与同模块其它比率列一致, 保证真零 (有实词却无正面命中) 与不可测 (无实词可供计数) 在下游聚合时不被混为一谈。

三轨文本在 stage 14 物化: content_full 为标题 prepend 后的全文正文, 原始内容列不动, 标题作为第 0 句参与扫描; content_ctx 为标题加目标银行实体提及句的邻域窗口文本; content_ss 为标题加银行与金融科技词同句共现句的正负 1 句窗口文本, 半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1, 该键与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同的键。stage 22 对三轨文本各自独立运行同一状态机, 产出文章级三列写入 22_words_tone.parquet。面板聚合位于 pipeline/panel/encode.py: 对每个银行-年单元, avg_you_2018_pos_ratio 等于该单元内留存文章对应轨道文章级值的无加权算术均值, NaN 值自动剔除不入分母, 因此银行-年均值的有效篇数是该单元内该轨道非缺失文章数。行宇宙遵循 2026-06-29 起的 full-only 留篇门控: 一篇文章是否计入面板只看 stage 21 的 llm_verified_full 是否为真; ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集, 逐轨照算各自的文章级值, 不另设留篇判据, ss 的回退语义镜像 ctx。Stata 导出层为本族生成正面占比均值系列的变量标签, 家族内三列在最宽 dta 中随其它词典占比列一并落盘。

【文献定位】
词典法是金融文本分析的基线方法学, 其优势是透明、可复现、零边际成本, 与机器学习法和大语言模型法互补而非替代。Anastasiou et al. (2026) 在银行股价崩盘风险预测中系统比较文本特征与机器学习方法, 显示词典类特征仍是不可或缺的可解释基准; Li et al. (2026) 进一步从文本风险披露中恢复金融网络结构与关联性, 说明文本测度已从单变量情感扩展到结构性信息抽取, 本管道的词典情感列位于这一谱系的基础层, 为上层的分歧、网络与语义类测度提供构件。方法融合方向上, Sun et al. (2025) 把词典知识与中性特征注入预训练语言模型的金融情感分析, 恰说明词典信号并未被端到端模型取代, 而是作为先验注入以提升可解释性与稳健性, 与本管道保留词典轨作为解释性锚点的定位一致。测度效度上, van Atteveldt et al. (2021) 系统比较人工标注、众包编码、词典法与机器学习法, 指出词典法在特定语料上可靠但依赖词表与领域匹配, 因此多方法三角互证是缓解单一方法系统偏差的正道; 本管道的词典、生成式与判别式三条情感轨正是这一三角设计的操作化。中文金融情感词典的构建此后仍在活跃迭代, Ma et al. (2025) 面向中国个人投资者语料构建了细粒度中文金融情感词典, 说明该文献分支持续演进; you_2018 只是本管道并行维护的六部中文金融与通用情感词典之一, 六部词典的同名占比列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。中国媒体环境的制度特征也是本族语境的一部分: Piotroski et al. (2017) 记录了中国企业新闻的政治偏向, you_2018 的母文关切国有与市场化媒体的语调分野, 二者共同提示本管道所处的媒体语料带有制度性立场差异; 需要说明的是, you_2018 本身不设政治正面词类, 对政治性语言的处理由 du_2022 的政治词降权承担, 本族在此维度保持中立。

【识别策略定位】
在论文组合中, 本族不是任何一篇论文的 headline 处理变量。P1 主线 (bank_fintech_tone) 的 canonical 处理变量是 LLM 三家投票共识的 llm_vote_tone_full, 其结果变量为融资成本 funding_cost; 词典法的 you_2018 净语调轨是该 headline 的跨方法学稳健性臂, 而本族正面占比又是这条词典净语调轨内部的正面侧分解臂。三者层层嵌套, 本族在识别策略中承担的是三重支撑角色, 而非独立的因果处理变量。其一, 机制与分解: 词典净语调的估计效应可以分解到正负两侧分别检验, 若净语调对融资成本的效应完全由负面侧驱动而正面侧系数近零, 则对媒体乐观情绪压低融资成本的解释就必须让位于负面信息披露抬高融资成本的解释, 本族正是这一正负分解的正面臂, 它提供的是净语调单一系数无法回答的方向归因。其二, 分歧输入: 正负占比对是词级与跨词典情感分歧指标族的直接构件, 分歧类构念只能从分离的两侧构造, 一旦压缩为净值即不可逆地恢复不出, 因此本族与镜像列 avg_you_2018_neg_ratio 成对喂入分歧构造, 是二阶构念的原材料而非终点。其三, 跨词典规格稳健性: 六部词典的同名占比列构成互为稳健性、不分主次的规格并排, you_2018 臂的独特信息在于其词表出自谁捕获这支笔力量的媒体语调研究、并自带准确性维度, 使它在六词典并排中不是冗余复制而是携带独立词表覆盖与独有重叠结构的一票。

计量口径必须严格执行仓库铁律。三轨 full、ctx、ss 之间, 六部词典之间, 以及一切梯子变体之间, 各自 just-identified 并排, 互为稳健性、不分主次, 禁止把不同轨、不同词典或不同变体混进同一个 over-identified 的 Hansen J 检验。把同一构念的多个测量当作多只工具塞进一条广义矩估计, 会把测量之间的误差结构差异伪装成过度识别拒绝, 使检验丧失对排除性约束的解释力: 六词典的占比高度共线, 其相互间的偏离主要来自词表覆盖与重叠词处理的技术差异而非独立的经济信号, 强行并入 over-identified GMM 只会人为制造 J 统计量的拒绝, 却无法据以判断任何一条排除性约束的成立与否。当本族列进入工具变量设计时, 面板 IV 扩展 (pipeline/panel/iv_extensions.py) 提供三类恰好识别的工具: 同组 leave-one-out 均值利用同群银行的媒体暴露、广义 Bartik 利用 shift-share 暴露结构、媒体来源 house-style 利用来源固定的文风倾向, 分别落地为 leave_one_out_peer_*_iv、bartik_*_iv、outlet_*_iv 三个列族。每条规格保持恰好识别, 因此弱识别诊断依 Kleibergen 与 Paap (2006) 的广义降秩检验统计量报告, 而非依赖在恰好识别设定下没有自由度、根本无法计算的过度识别检验; 这也正是禁混 Hansen J 铁律在识别层面的技术根据。跨词典的多重比较问题按规格稳健性并排处理: 仓库既有的族错误率校正模板只覆盖同构念替代 headline 测量的场景, 即跨 LLM 厂商 (根级模板 27_tableA12_cross_model_fwer) 与跨 BERT 模型的族, 六词典占比族不属于该口径, 不设 FWER 模板, 论文表述以主结论定性不变的稳健性叙事呈现, 而非以校正后的 p 值断言。标准误层面, 银行-年面板的聚类结构须按 Abadie et al. (2023) 的抽样与设计视角确定聚类维度: 究竟按银行、按年、还是双向聚类, 取决于处理变量的变异来源与抽样设计, 而非机械默认, 在错误层级上聚类会导致推断失真。多规格稳健性的整体逻辑亦可参照 Muñoz 与 Young (2018) 的计算式稳健性思想: 与其挑选单一最优规格, 不如系统展示测度在合理设定空间上的分布, 六词典乘三轨构成十八种测量组合, 它们的系数分布本身就是一条测量维度上的规格曲线, 主结论的可信度取决于这条曲线的集中程度而非任一单点的显著性, 本族只是这十八点之一。

【与相邻测度的构念区分】
与 you_2018_tone 及其面板聚合的区分: tone 是幅度口径的净语调, 分子为全部命中词次最终带号分值之和, 分母为其绝对值之和, 自归一化到正负 1 区间, 度量的是情感的净方向与相对强度; 本族是计数口径的单侧密度, 分母是全文词数而非命中词幅度和, 度量的是正面表述在篇幅中的浓度。两者分母性质不同, 一个是文内相对量, 一个是占篇幅绝对量, 不可互相换算; 且 you_2018 的 5 个跨类重叠词在 tone 里以正负对冲拉向中性、对净值贡献为零, 在本族里却各计一次正面, 两条链对这 5 个词的处理方向相反, 更凸显二者不可混读。

与同为词典占比的 avg_du_2022_pos_ratio 的区分尤须写明, 因为二者看似同构实则结构相异。其一, 跨类重叠: you_2018 含 5 个正负跨类重叠词 (反弹、整顿、脱离、落后、规避, 均为语境依赖的双向金融用语), 命中即两侧各计一次, 本族的正面占比在结构上包含这 5 个双向词的贡献; 而 du_2022 无跨类重叠词, 其正面占比纯由单极正面命中构成, 不含任何双向抬升成分。其二, 政治词类: du_2022 独有 1,434 个政治正面词以 0.5 权重计入正侧, 并据此物化 polw00、polw05、polw10 三权重敏感性梯子; you_2018 不含政治正面词类, 故政治词权重梯子不为本族物化任何变体, 本族在该维度天然中立。因此即便两列都叫正面占比, 它们回答的是两套不同词表、不同重叠结构、不同政治处理下的正面密度, 是家族层面的不同构念而非同列变体。六部词典的跨类重叠数各不相同 (jiang_2021 21 词、you_2018 5 词、loughran 23 词, 其余为零), 这一结构差异正是六词典并排携带独立信息、而非彼此冗余复制的技术根源之一。

与无词典前缀的 avg_pos_ratio 的区分, 关键在量尺与重叠词处理两处。无前缀列的计数基是六词典构成的固定 union 词典, 全样本统一词表, 跨词典极性平票的歧义词被剔除; 更关键的是, union 构建时跨类重叠词以正一负一的平衡双票喂入, 极性 margin 守恒, 故 union 占比对重叠词的净贡献为零、且逐位不受重叠词消歧决策影响。本族则以 you_2018 单部词典为量尺, 跨类重叠词两侧各计一次、对本族正面占比有实打实的正向贡献。两者在词表覆盖与重叠词处理上均相反, 是家族层面的不同构念而非同列的轨道变体。

与 avg_you_2018_neg_ratio 的区分: 严格镜像, 分子换为最终极性为负的词次数, 两列共享分母与全部口径, 设计上成对使用; 5 个跨类重叠词同时进两列的分子, 是两列共有的结构成分, 也是两列相关性被结构性抬高的来源。与 msent 类计数净值指标的区分: msent 用词典原始极性计数且不经语言学规则、基于 union 词典、输出净值占比; 本族用规则处理后的最终极性、基于单词典、输出单侧占比, 三个维度全部不同。与规则消融梯子的区分: 消融梯子把否定、程度、转折三规则的全组合物化为 score 类变体列, pos_ratio 族不设消融变体, 本族数值恒为全规则口径下的计数。与 you_2018 clarity 指标的区分尤须强调: clarity 取的是同一 you_2018 词典的准确性维度 (确定性词 388 / 模糊性词 178), 度量报道用语的明确与模糊, 与本族取的语调维度正交, 两者共用一部词典文件却回答两个互不相干的问题, 不可因同源而混淆; you_2018 是六部词典中唯一自带准确性维度者, 这一双维度结构正是它在同一词典文件里同时供养情感浓度与信息清晰度两条正交测度链的原因。与 LLM 与 BERT 情感轨的区分: 方法学家族不同, 词典法、生成式模型法与判别式模型法互为稳健性、不分主次, 各自 just-identified 并排, 同样禁混进同一 over-identified Hansen J。

【已知局限与稳健性梯子】
第一, 计数口径丢失幅度信息。pos_count 把强烈褒扬与轻微肯定同记一次, 程度副词与转折增强只影响极性判定后的分值幅度而不改变计数, 因此本族对情感强度不敏感; 与幅度口径的净语调列并读可以互补, 两者在解读中分别承担浓度与强度两个维度。更进一步, 单侧密度本身也无法区分正负双高与正高负低两种情形: 一篇正负词都密集的争议性报道与一篇只密集褒扬的报道可能有相近的正面占比, 二者的辨识须借助 neg_ratio 与情感分歧族联合刻画, 本族单列不足以还原一篇报道的完整情感结构。

第二, 跨类重叠词的两侧计数会系统性抬高 you_2018 的正面占比。5 个双向词 (反弹、整顿、脱离、落后、规避) 每次命中都无条件对 pos_count 记一次, 且这一记入与该词次的否定翻号、程度缩放、转折增强全部无关; 这些词在中文金融报道中并非罕见边角, 其在银行金科语料里的实际频次是经验问题, 但只要非零, 本族相对无跨类重叠的 du_2022 就会呈现结构性偏高。解读时应与无跨类重叠的 du_2022 及重叠更少的词典的同名列对照, 系数方向与显著性在对照中保持一致方可下结论, 这也是六词典并排在本族尤为必要的原因。

第三, 词典时效与覆盖漂移。you_2018 词表冻结于其构建语料期, 而生产面板语料横跨 2007 至 2024 共 18 年, 词典构建之后才出现的金融科技新词不在词表内, 覆盖率可能随时间漂移并与年份效应混同; 六词典并排与 LLM、BERT 轨提供跨方法学对照, 年份固定效应吸收共同漂移, 但无法分离词典专属的覆盖衰减。第四, 分词依赖。词典命中以 jieba 切分的词元为准, 分词错误直接改变命中集与分母; jieba 版本冻结在 0.42.1 保证跨次运行的确定性, 且词典匹配使用注入隔离的独立 Tokenizer 实例以免污染全局分词器, 但版本冻结只消除运行间的不确定性、不消除分词本身的系统误差。

第五, 可复现性是本族相对模型轨的独特价值。本族全链条无随机源: 词典冻结在 config/tone_dicts.json, 分词器版本冻结, 状态机为纯确定性函数, 词典法列不涉 LLM 缓存与嵌入接口, 可离线零成本逐字节重放; 这与本管道对词典法作为透明可审计基线的定位相符, 也是它在换嵌入模型、换 LLM 厂商等改动中零误改的原因。第六, 开发态退化与轨道覆盖。当前盘上为两年开发面板 (T=2), 银行-年内文章数少使均值的抽样方差偏大, 生产全量语料 (T=18) 下缓解; 本族无 _lg 孪生列, co-primary 双轨口径仅适用于嵌入族, 词典法属于非嵌入 carve-out, 这是设计使然而非缺漏。

稳健性梯子的适用范围须明确划界, 以免误接不属于本族的梯子。本族参与的稳健性并排有二: 一是六词典同名占比的跨词典并排, 二是 full、ctx、ss 三轨的跨文本口径并排; 两者均属规格稳健性、互为稳健性不分主次、各自 just-identified 并排、禁混进同一 over-identified Hansen J。本族不参与的梯子有三: 政治词权重梯子 (polw00 与 polw05 与 polw10) 是 du_2022 独有, you_2018 无政治词类故不物化; 规则消融梯子 (negonly 与 degonly 与 advonly 等七变体) 只作用于 score 类列, pos_ratio 族不设消融变体; co-primary 双轨嵌入 (无后缀与 _lg 孪生) 只覆盖嵌入族, 本族是非嵌入 carve-out。这一适用与不适用的划界本身就是防止把不同梯子混入同一识别设计的防线。最后重申轨道铁律: full、ctx、ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 任何情况下禁混进同一 over-identified Hansen J。

## VAR: avg_you_2018_pos_ratio_ctx

【变体差分】
本列为实体窗口轨。计算内核、词典、分子分母口径与家族 canonical 的 full 轨完全一致, 唯一差分在输入文本: 文章级值在 content_ctx 上计算, 即标题 prepend 加目标银行实体提及句的邻域窗口文本, 由 stage 14 物化。银行实体的判定采用管道的不对称口径, 银行侧施加否定与短名过滤以防常见短名误匹配, 与金融科技侧的裸词表匹配判据不同。构念含义上, 本列把测量视窗收窄到目标银行被直接谈及的语句邻域, 剔除同一篇文章中与目标银行无关的段落, 例如同篇报道其它银行或铺陈宏观背景的部分所携带的情感噪声, 换取的解释是针对该银行的正面表述密度, 情感归属更干净。代价有二: 其一, 窗口文本显著短于全文, 分母 n_word_tokens 变小, 比率的抽样方差变大, 单篇取值更不稳定; 其二, 窗口截断可能切断跨句的情感修饰结构, 否定窗口与转折作用域在截断边界处失效, 个别词次的极性判定可能与全文口径不同, 从而使同一命中词在 ctx 与 full 两轨落入不同的 pos_count 归属; 对 you_2018 而言, 5 个跨类重叠词是否落入窗口也随窗口边界变化, 其对 pos_count 的结构性贡献在 ctx 轨与 full 轨可能不同。行宇宙与家族一致, 是 full-only 留篇门控下的 conditional-on-full 测度轨, 不另设留篇判据。本列与 full、ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 论文中作为 canonical full 结论的文本口径稳健性对照臂使用。

## VAR: avg_you_2018_pos_ratio_full

【变体差分】
本列为家族 canonical 列, tier 为 core, 2026-07-10 签核扩围的类别六即词典分解成分类核心列, 签核理由是其作为 you_2018 词典正面成分占比的全文轨规范口径。文章级值在 content_full 上计算, 即标题 prepend 后的全文正文, 原始内容列不动, 标题作为第 0 句参与状态机扫描, 因此标题中的正面词与正文同权计数, 标题词元也一并进入分母 n_word_tokens。full 轨被选为家族 canonical 有四点依据。第一, 口径与留篇门控同轨: 2026-06-29 起管道的留篇判据只看 llm_verified_full, full 轨的文本视窗与定义面板行宇宙的门控视窗完全重合, canonical 测度与样本构成之间没有口径错位; ctx 与 ss 是该行宇宙上的 conditional-on-full 附加测量, 它们的行集是 full 留篇集的同一集, 只是文本视窗更窄。第二, 统计性质最稳: 全文是三轨中最长的文本, 分母词元数最大, 占比的抽样方差最小, 作为进入回归的基准测度信噪比最优, 银行-年均值对个别文章的敏感度也最低。第三, 跨文献可比: 词典法金融文本文献的标准做法是在整篇文档上计算占词比, 全文轨与该口径直接可比, 而窗口轨是本管道特有的构造, 缺少外部基准, 因此以全文轨承担对外报告与跨文献对照的角色最稳妥。第四, 语言学规则的作用域完整: 否定窗口、程度副词与转折的从句级作用域在连续全文上不受截断干扰, 极性判定最接近状态机的设计语义, 不会因窗口边界把一个本应被否定翻转的正面词误计入 pos_count。本列在论文组合中的典型用法有三: 作为 you_2018 净语调全文轨的正面侧分解臂, 检验净效应由哪一侧驱动; 作为词级与跨词典分歧指标的输入构件, 与 avg_you_2018_neg_ratio 成对喂入分歧构造; 作为六词典正面占比并排中的 you_2018 臂参与跨词典稳健性叙事。解读本列时须记住三点计数口径的特性。其一, 否定翻转改变计数归属, 本列不是裸词频, 一处被否定的正面词会转记入负面而非正面, 因此本列度量的是净规则处理后的正面浓度, 而非表层正面词的出现频率。其二, you_2018 的 5 个正负跨类重叠词依 2026-06-24 决策两侧计数, 命中即对本列分子记一次, 且这一记入与该词的否定翻号、程度缩放、转折增强无关; 因此当报道频繁使用这类双向词时, 本列会带有该结构成分, 需与不含或少含跨类重叠的词典的同名列对照解读, 判断正面密度的抬升是否部分来自双向词。其三, you_2018 不含政治正面词类, 政治词权重梯子对本列不物化任何变体, 本列在政治词维度上恒为中立口径, 这与 du_2022 家族的同名列在结构上不同。还须区分本列的分子分母语义与净语调列的根本不同: 本列的分母是全文剔除标点数字后的词元总数, 是一个篇幅量, 与命中词多寡无直接联系, 所以当一篇报道整体信息密度上升、正面词绝对数增加而篇幅同比膨胀时, 本列可以保持平稳, 它捕捉的是正面表述占用篇幅的比例而非绝对条数。缺失契约在本列上同样严格: 空文本、纯符号文本或分母为零时本列置 NaN, 与有实词却零正面命中的真零区分, 面板均值自动剔除 NaN 而不把不可测样本当作零值稀释银行-年浓度。与 ctx、ss 的关系是并排而非嵌套修正: 全文口径包含与目标银行无直接关联的段落, 存在情感归属误差, 该误差由两条窗口轨对照评估, 而非由窗口轨去修正全文轨; 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。本列作为 core 列在最宽 dta 中落盘并被赋予正面占比均值全文轨的规范变量标签, 是家族对外呈现的默认口径。

## VAR: avg_you_2018_pos_ratio_ss

【变体差分】
本列为同句共现轨, 三轨中视窗最窄的一条。文章级值在 content_ss 上计算, 即标题加银行与金融科技词在同一句内共现的句子及其前后各 1 句的窗口文本, 半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1。共现判定采用管道的不对称口径: 银行侧施加否定与短名过滤, 金融科技侧为裸词表匹配。回退语义与 ctx 轨机制镜像: 当一篇文章不存在银行与金科的同句共现时, content_ss 回退为全文正文, 同时 ss_is_fallback 置真, 回退篇仍留在行宇宙内共享分母, 其 ss 轨取值实际按全文计算; 金科词表整体缺失时全部文章置回退标志, 优雅降级不崩溃。因此本列在解读上是一个混合口径: 能定位到银行金科同句共现处的文章聚焦到共现语句邻域, 度量的是最贴近该银行金融科技业务表述的正面词密度, 定位不到的文章退回全文口径。这一构造使本列成为三轨中情感归属最强、但受回退混合与短文本方差影响也最大的一臂, 单篇分母最小, 银行-年均值对个别短窗口文章敏感; you_2018 的 5 个跨类重叠词对本列的贡献同样随窗口而变, 在短窗口内其影响相对更突出。行宇宙与家族一致, 为 full-only 留篇门控下的 conditional-on-full 测度轨。本列与 full、ctx 两轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 若 canonical full 的结论在本列上定性保持, 则可排除结论由与银行金科主题无关的篇幅情感所驱动的替代解释。

<!-- rendered-citations:begin -->
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. Applied Economics, Advance online publication. https://doi.org/10.1080/00036846.2025.2536881
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Koranteng, B., & You, K. (2024). Fintech and financial stability: Evidence from spatial analysis for 25 countries. Journal of International Financial Markets, Institutions and Money, 93, 102002. https://doi.org/10.1016/j.intfin.2024.102002
Abadie, A., Athey, S., Imbens, G. W., & Wooldridge, J. M. (2023). When should you adjust standard errors for clustering?. The Quarterly Journal of Economics, 138(1), 1-35. https://doi.org/10.1093/qje/qjac038
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Muñoz, J., & Young, C. (2018). We ran 9 billion regressions: Eliminating false positives through computational model robustness. Sociological Methodology, 48(1), 1-33. https://doi.org/10.1177/0081175018777988
Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news: The role of conglomeration reform in China. The Journal of Law and Economics, 60(1), 173-207. https://doi.org/10.1086/693096
Kleibergen, F., & Paap, R. (2006). Generalized reduced rank tests using the singular value decomposition. Journal of Econometrics, 133(1), 97-126. https://doi.org/10.1016/j.jeconom.2005.02.011
<!-- rendered-citations:end -->
