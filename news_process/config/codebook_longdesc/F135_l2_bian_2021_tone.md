---
family_id: F135
columns:
- bian_2021_tone_app_ctx
- bian_2021_tone_app_full
- bian_2021_tone_app_ss
- bian_2021_tone_ctx
- bian_2021_tone_full
- bian_2021_tone_hw_ctx
- bian_2021_tone_hw_full
- bian_2021_tone_hw_ss
- bian_2021_tone_mw_ctx
- bian_2021_tone_mw_full
- bian_2021_tone_mw_ss
- bian_2021_tone_ss
- bian_2021_tone_std_ctx
- bian_2021_tone_std_full
- bian_2021_tone_std_ss
- bian_2021_tone_tech_ctx
- bian_2021_tone_tech_full
- bian_2021_tone_tech_ss
- bian_2021_tone_vw_ctx
- bian_2021_tone_vw_full
- bian_2021_tone_vw_ss
unit: 语调得分 (连续; 文章级恒有界 [-1,1]; bank-year 均值/加权均值同界; _std 变体为年内标准差, 非负)
formula: "article: bian_2021_score{track} = Σ(final_score)/Σ|final_score| ∈ [-1,1], final_score = base × negation(±1, 窗口 2) × degree(≤3.0) × adversative(1.5); panel: bian_2021_tone{track} = mean(score); _std = std(score); _vw = Σ(score×mention_density)/Σ(mention_density); _mw = Σ(score×media_authority_weight)/Σ(media_authority_weight); _hw = Σ(score×herd_weight{track})/Σ(herd_weight{track}); _tech/_app = mean(score | innovation_locus_full = 底层技术/应用场景)"
producer: news_process/pipeline/sentiment/tone_words.py::_compute_sentiment_with_rules (文章级打分) → news_process/pipeline/panel/runner.py (步骤 3b/3c/3d 加权列预计算) → news_process/pipeline/panel/encode.py (bank-year mean/std 聚合 + VW/MW/HW 派生 + locus 条件均值)
upstream:
- 21_tone_llms.parquet (三轨文本 content_full/content_ctx/content_ss + llm_verified_full 留篇门控 + innovation_locus_full)
- 22_words_tone.parquet (bian_2021_score_{full,ctx,ss} 文章级得分)
- 24_herd_decay.parquet (herd_weight_{full,ctx,ss}, 供 _hw 变体)
- config/tone_dicts.json (bian_2021 词表 SSOT, positive 1,107 / negative 1,488)
citations:
- doi: 10.1002/mde.70100
  type: journal
  authors: Li, Y.
  year: 2026
  title: "The textual tone of annual reports and market attention: Evidence from Chinese listed companies"
  venue: Managerial and Decision Economics
- doi: "10.1016/j.ememar.2024.101234"
  type: "journal"
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  venue: "Emerging Markets Review"
- doi: "10.1038/s41598-025-03875-y"
  type: "journal"
  authors: "Sun, Y., Yu, Z., Sun, Y., Xu, Y., & Song, B."
  year: 2025
  title: "A novel approach for multiclass sentiment analysis on Chinese social media with ERNIE-MCBMA"
  venue: "Scientific Reports"
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: "100148"
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: Article 20
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1080/07421222.2023.2301176
  type: journal
  authors: Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y.
  year: 2024
  title: "The effects of sentiment evolution in financial texts: A word embedding approach"
  venue: Journal of Management Information Systems
  vol: 41
  issue: 1
  pages_or_artno: 178-205
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1016/j.mlwa.2023.100508
  type: journal
  authors: Fatouros, G., Soldatos, J., Kouroumali, K., Makridis, G., & Kyriazis, D.
  year: 2023
  title: "Transforming sentiment analysis in the financial domain with ChatGPT"
  venue: Machine Learning with Applications
  vol: 14
  pages_or_artno: "100508"
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1111/joes.12370
  type: journal
  authors: Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K.
  year: 2020
  title: "Econometrics meets sentiment: An overview of methodology and applications"
  venue: Journal of Economic Surveys
  vol: 34
  issue: 3
  pages_or_artno: 512-547
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.18653/v1/d16-1057
  type: journal
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing (EMNLP)
  pages_or_artno: 595-605
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1145/1341531.1341561
  type: journal
  authors: Ding, X., Liu, B., & Yu, P. S.
  year: 2008
  title: "A holistic lexicon-based approach to opinion mining"
  venue: Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08)
  pages_or_artno: 231-240
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: "International Review of Economics & Finance"
- doi: "10.1016/j.ribaf.2025.102881"
  title: "Annual report tone and bank risk-taking behavior: Evidence from China"
  authors: "Wei, L., Wei, M., Jing, H., & Jing, Z."
  year: 2025
  venue: "Research in International Business and Finance"
  type: "journal"
- doi: "10.1002/for.3089"
  title: "Incorporating media news to predict financial distress: Case study on Chinese listed companies"
  authors: "Zhang, L., Abedin, M. Z., & Liu, Z."
  year: 2024
  venue: "Journal of Forecasting"
  type: "journal"
new_dois:
- "10.1016/j.ememar.2024.101234"
- "10.1038/s41598-025-03875-y"
- "10.1016/j.iref.2024.01.067"
- "10.1016/j.ribaf.2025.102881"
- "10.1002/for.3089"
---

## CORE

该文构建中国官方媒体语调指数并检验其对股票市场收益反转、交易量与投资者情绪的影响,为词典/规则法媒体语调测度在中国场景的资本市场后果提供了最新顶刊证据,呼应本家族语调影响银行经营与融资环境的理论渠道。 该文提出融合ERNIE预训练模型与多通道CNN-BiLSTM-注意力机制的中文社交媒体多分类情感分析框架,代表词典法之外基于深度学习的中文情感测量前沿路线,可作为词典与LLM/BERT情感测度方法学谱系对照的补充参照。

【构念与来源】
本家族测量的构念是"目标银行的金融科技相关媒体报道语调" (media tone), 具体以 Bian et al. (2021) 中文金融情感词典打分。语调在本项目的理论框架里是银行金融科技转型的媒体呈现维度: 一家银行在某年被媒体如何报道其金融科技活动, 报道倾向是肯定还是质疑, 会通过投资者情绪、存款人信心与监管注意力等渠道影响该行的融资成本与经营行为 (Tetlock, 2007; Holzman et al., 2023)。词典法测语调的传统由 Loughran and McDonald (2011) 在英文财务文本上确立, 其核心论点是通用情感词典在财务领域系统性失真, 必须使用领域专属词表; 该传统随后被系统综述为财务文本分析的基准方法学 (Loughran and McDonald, 2016; Algaba et al., 2020)。中文语境下的对应工作包括 You et al. (2018) 的中国媒体报道研究、Du et al. (2022) 的中文金融情感词典, 以及 Ma et al. (2025) 的细粒度投资者情感词典; 本家族使用的 Bian et al. (2021) 词典是这一谱系中"Loughran-McDonald 词表中文本土化扩充版"的代表, 由作者在会计与金融文本分析场景下针对中文语料重制正负词表。项目内该词典的单一事实源是 config/tone_dicts.json 中的 bian_2021 键, 收录 positive 词 1,107 个、negative 词 1,488 个, 加载序位是六部词典中的第三部 (另五部为 jiang_2021、yao_2021、du_2022、you_2018 与 loughran_mcdonald_zh_2026 中文主译本)。需要说明一处年份口径: 词典键名与正文引注均按 bian_2021 记, 对应 SSRN 工作论文编号 3446388, 该预印本存在多个修订版本, 引用口径以 DOI 解析记录为准。数据来源是本项目的中文银行×金融科技新闻语料: 原始媒体报道经 stage 13 银行与金科词邻近共现硬过滤、stage 14 三轨文本物化后, 在 stage 22 (tone_words) 对每篇文章逐轨打分, 最终由 panel 聚合层压缩为银行-年 (bank-year) 面板变量。分析单元是银行-年, 生产语料覆盖 2007 至 2025 共 19 年, 样本银行约一百一十家; 早期试跑盘为两年浅切片, 涉及面板取值分布的一切实测数字以引擎注入的动态统计为准。选择银行-年而非文章级作为回归单元有三点考虑: 其一, 下游结果变量 (融资成本、金科投资等) 是年度财务量, 处理与结果须同频; 其二, 单篇报道语调噪声大, 年度均值经大数定律平滑后测量误差衰减; 其三, 银行-年口径允许双向固定效应吸收银行恒定特征与年度宏观冲击, 是媒体语调文献的标准面板设计 (Marchetti et al., 2025)。之所以在 LLM 与 BERT 之外仍保留词典支柱并为其配齐六部词表, 是因为词典法是三支柱中唯一"打分过程可被审稿人逐词复核"的方法: 每篇文章的得分都能还原为一张命中词明细表, 这对以中文媒体文本为核心证据的论文是不可替代的可信度资产 (van Atteveldt et al., 2021)。

【方法学与计算】
文章级打分由 pipeline/sentiment/tone_words.py 的 _compute_sentiment_with_rules 实现, 输入是冻结版本 jieba 0.42.1 的分词序列 (自定义词典注入后), 核心是一个带三条语言学规则的状态机。规则一是否定翻转: 遇否定词开启长度为 2 个 token 的否定窗口, 窗口内命中的情感词极性取反, 这是词典法情感计算中公认最重要的修饰规则 (Pröllochs et al., 2016; Punetha and Jain, 2025)。规则二是程度副词加权: 程度词设置一个不超过 3.0 的倍率, 由下一个情感词消费后重置, 未被情感词消费即遇到其他词则清零。规则三是转折增强: 遇转折连词后区域内的情感词幅度乘以 1.5, 体现"但是之后才是真实态度"的语用直觉; 转折作用域限定在从句级, 句末标点重置全部状态, 防止修饰效果跨句串味 (Ding et al., 2008)。这一"词典加规则"的架构直接承袭 Taboada et al. (2011) 的 lexicon-based 方法论。归一化采用加权幅度和分母: 文章得分等于全部命中词最终得分之和除以最终得分绝对值之和, 因分子分母同含程度与转折权重, 得分恒有界于负一到正一, 与 LLM 及 BERT 语调轨的量纲可比; 全文无命中词时返回 0 记为中性。词典内正负两侧同时收录的跨类重叠词按"两侧同计"处理: 对分子净贡献为零、对分母贡献双倍幅度, 效果是把该词把语调拉向中性而非武断选边或剔除。面板聚合发生在 pipeline/panel/encode.py: 无中缀的 canonical 列是文章得分在银行-年格内的算术平均, _std 变体是同格内标准差; 三个加权变体先在 runner 步骤 3b 至 3d 预计算"得分乘权重"的文章级列, 聚合为分子和后除以对应权重和, 其中 _vw 用目标银行提及密度 mention_density (价值加权思路承袭 Hassan et al., 2019), _mw 用媒体权威性权重 media_authority_weight (Holzman et al., 2023), _hw 用 stage 24 产出的跟风衰减权重 herd_weight, 对疑似跟风转载的报道降权。分母口径有一处承重差异: _vw 与 _mw 的权重是轨道无关的文章级属性, 分母对三轨共用一个权重和; _hw 的权重本身分三轨, 分母严格逐轨匹配。_tech 与 _app 变体是按 LLM 分类维度 innovation_locus_full 取值等于底层技术或应用场景的子样本条件均值, 分组判据恒取 full 轨分类。行宇宙口径与全项目一致: 留篇门控为 full-only (2026-06-29 口径), 一篇文章是否计入"银行金融科技报道"只看 llm_verified_full 为真; ctx 与 ss 是 conditional-on-full 的测度轨, 行宇宙是 full 留篇集的子集。三轨文本语义为: full 轨等于标题前置拼接全文正文; ctx 轨等于标题加目标银行实体窗口文本; ss 轨等于标题加银行与金科词同句共现句及其邻句窗口, 回退语义镜像 ctx, 即无银行与金科同句共现时 content_ss 回退为全文正文并置 ss_is_fallback 为真, 与 full 共享 n_articles 分母。整条计算链不调用任何付费 API, 词典打分确定性可零成本复现。若干实现细节对正确解读本家族有承重意义, 在此一并交代。第一, 程度副词采用六级离散倍率表 (最高 3.0), 倍率由紧随其后的情感词一次性消费, 未消费即遇非情感词立即重置, 这保证"非常"只放大它真正修饰的词而不会泄漏到句子后段; 否定窗口与转折状态同样受句末标点硬重置约束, 修饰规则的作用域被严格限制在从句内部。第二, 规则消融口径: 归一化得分进入本家族, 而平行的计数口径 (msent 族) 刻意不套用程度与转折乘子, 因为严格正乘子不改变词的正负判定, 对计数无效应; 这也是为什么本家族与计数族不能互相换算。第三, 与本家族同源的 IDF 加权词典族在打分前对词典权重乘以逆文档频率, 稀有词权重被放大, 属于另一个独立家族, 本家族全部 21 列均为非 IDF 的原始词典权重口径。第四, 聚合时序: 文章级得分在 stage 22 落盘后, 面板层先由 runner 完成加权列预计算, 再由 encode 单次 groupby 产出全部 mean、std 与分子分母和, 加权语调在聚合后的派生块中相除, 分母为零的银行-年格以缺失标记而非零填充, 使用者不会把无报道格误读为中性语调。第五, 词典打分对空文本与纯标点文本返回中性 0 并正常计入分母, 这一选择保证三轨分母一致, 但也意味着 ctx 与 ss 轨的零命中膨胀会向中性方向稀释均值, 相关诊断应结合命中词数列进行。

【文献定位】
本家族在方法学光谱上位于"词典加语言学规则"一档, 处在裸词频计数与机器学习或 LLM 打分之间。财务文本情感测量的方法学综述 (Loughran and McDonald, 2016; Algaba et al., 2020; Todd et al., 2024) 一致将词典法列为基准: 其优势是完全透明、逐词可审计、跨样本零训练成本且不存在前视偏误; 其劣势是覆盖率受词表限制、无法处理词表外的隐含情感。方法比较文献给出的证据是分化的: Frankel et al. (2022) 发现机器学习在披露文本情感上优于词典但两者互补, van Atteveldt et al. (2021) 在新闻语调上发现人工标注、众包、词典与机器学习各有系统性差异, Fatouros et al. (2023) 与 Sun et al. (2025) 展示 LLM 与融合词典知识的预训练模型可进一步提升, Zheng et al. (2024) 则用词嵌入刻画情感词义的时变演化, 提示静态词表存在语义漂移风险; Barbaglia et al. (2025) 在经济新闻上系统论证了 lexicon-based 途径在宏观经济预测中的持续有效性。正是因为方法之间没有一致的支配关系, 本项目将词典法、LLM 三家投票与 BERT 三模型设计为三条互为稳健性的测量支柱, 词典支柱内部再并排六部词典。中文场景的定位参照包括 You et al. (2018) 对中国财经媒体激励的研究、Du et al. (2022) 对语言与领域双重特异性的论证 (通用译词典在中文金融文本失真, 呼应 Bian 词典的本土化动机), 以及 Li (2026) 对中国上市公司文本语调与市场注意力的近期证据。银行媒体语调聚合到机构-年的口径先例见 Marchetti et al. (2025)。就词典选型而言, 直接把 Loughran-McDonald 词表机器翻译为中文会同时引入翻译噪声与语域错配, Du et al. (2022) 对此给出系统证据并主张从中文金融语料原生构建词表; Bian et al. (2021) 走的是折中路线 — 保留 LM 的类别框架与财务领域定位, 但词条按中文表达习惯重制筛选, 因此它在六词典梯子中的独特身份是"LM 框架、中文词条"的桥接臂: 与中文主译本对比隔离出词条本土化的影响, 与原生中文词典对比隔离出类别框架的影响。这种把词典差异本身设计为可检验维度的做法, 呼应了 Algaba et al. (2020) 关于情感测度选择应作为研究者自由度显式披露的方法论主张, 也与近年规格曲线分析对测量规格透明化的要求一致。Fang, Wang, Wang, and Yuan (2024, International Review of Economics & Finance) 以中文媒体报道语调测量中国银行的媒体情感, 并检验其对存款稳定性与银行系统性风险的影响, 与本家族"媒体语调影响银行经营与融资环境"的理论渠道高度对应, 为 Bian 词典法测度银行媒体语调的中国场景应用提供了最新的顶刊证据。Wei, Wei, Jing, and Jing (2025, Research in International Business and Finance) 以2000至2020年中国A股上市银行年报文本语调为测度,发现正常语调更积极的银行未来风险承担上升,与本家族媒体语调影响银行经营行为的理论渠道相呼应。Zhang, Abedin, and Liu (2024, Journal of Forecasting) 验证中文媒体新闻文本情感信息在预测上市公司财务困境中具有超越财务指标的增量价值,支持词典法媒体语调测度对企业经营后果的可信度。

【识别策略定位】
在 P1 主线论文 (bank_fintech_tone) 的识别设计中, canonical 处理变量是 LLM 三家投票的 llm_vote_tone_full, 本家族全部 21 列都属于测量稳健性梯子: 用完全独立的测量技术 (静态词典对生成式模型) 复算同一构念, 若主效应在词典轨上同号且量级可比, 则排除"结果由 LLM 打分的黑箱特性驱动"的替代解释。词典轨的额外识别价值有三点: 其一, 词典打分不依赖任何模型权重或 API 版本, 是全链路里唯一可逐词审计的语调测度, 对应可复现性最强的一档; 其二, 词典打分与 LLM 打分的误差结构近乎正交 (词表覆盖误差对提示词敏感性), 两轨一致性本身就是测量效度证据; 其三, 六部词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran 中文主译) 构成跨词表梯子, bian_2021 是其中的 LM 本土化扩充臂。口径铁律必须复述: 六词典互为稳健性、不分主次, 三轨 full/ctx/ss、VW/MW/HW 加权臂、tech/app 条件臂同理, 每个变体各自 just-identified 并排进入各自的回归, 严禁把任意两个及以上变体混进同一个 over-identified 的 Hansen J 检验 — 它们是同一构念的替代测量而非独立工具变量, 混用会让过度识别检验在构造上失效。跨词典与跨方法的多重检验膨胀由根级 rwolf FWER 模板控制 (Stata 复现包的跨模型族错误率表), 词典臂在其中作为 canonical 处理变量的替代测量进入同一检验族; 需要强调的是, paper_spec 里声明的跨模型稳健性字段是文档性质, 运行时的真 FWER 控制只在该根级模板发生。跨方法系数比较另有一条量纲纪律: 词典得分、LLM 三分类得分与 BERT 概率差的原始方差不同, 跨方法对照表中的系数一律经 z-score 标准化后再比大小, 未标准化的原始系数只在各自规格内部解读。此外, 词典轨在识别体系中还承担一个反事实功能: 当 LLM 供应商、模型版本或提示词发生任何变更时, 词典列是唯一保证字节级不动的语调测度, 复现审计以它为跨版本锚点检验其余轨道的漂移是否属于预期。从测量误差结构看, 词典轨与生成式轨的偏误来源不同, 因而两轨点估计的一致性可作为经典测量误差衰减方向的诊断: 若词典轨系数系统性小于 LLM 轨, 提示词表覆盖不全导致的非差分测量误差把词典系数向零衰减, 这一模式本身是可解读的证据而非缺陷; 反之若两轨量级贴合, 则任一轨的特异性偏误 (词表漂移或提示词框架) 都不足以驱动主结论。识别体系中还需厘清本家族与工具变量的分野: P1 的 IV 扩展 (同组 LOO 均值、广义 Bartik、媒体 house-style 暴露) 是为 canonical 处理变量寻找外生变异, 而本家族 21 列是同一处理变量的替代测量, 二者在识别图上占据完全不同的位置 — 替代测量进入 reduced-form 与 OLS 的稳健性并排, 绝不作为工具进入第一阶段, 也绝不与 IV 列混入同一过度识别约束。最后, 词典轨的低成本与确定性使其成为规格曲线 (specification curve) 展开的天然骨架: 六词典乘三轨乘七规则消融的测量规格网格全部可零成本重算, 为"测量自由度是否驱动显著性"提供可穷举的边际证据, 这是 LLM 轨受 API 成本约束难以完整铺开的。

【与相邻测度的构念区分】
同层相邻的五个词典家族测同一构念但词表来源不同: loughran_tone 用 L&M 2011 词表的中文主译全本, 强调与英文基准的可比性; bian_2021 是在 LM 框架上针对中文金融语料重制的本土化扩充, 词表规模更精简 (正 1,107 负 1,488, 对比主译本正 1,295 负 3,729), 负面词占比更低, 经验上得分分布更居中; du_2022_tone 额外含 1,434 个政治正面词并带 0.5 权重及 polw 权重梯子, 是唯一嵌入政治语言维度的词典; you_2018 与 jiang_2021、yao_2021 分别源自媒体报道与年报及社媒语料。与本家族同词典但不同家族的相邻列须严格区分: bian_2021_negonly_tone 族是"规则削减"消融臂 (仅保留否定规则), 属规则消融梯度而非本家族; bian_2021_idf_tone 族在词典得分上叠加 IDF 词权; 文章级 bian_2021_score_raw 等七个消融变体属 22 阶段中间产物家族。与跨方法相邻测度的区分: llm_vote_tone 是三家 LLM 投票共识, BERT 族 net_tone 是分类概率差, 两者对上下文语义敏感但不可逐词审计; msent 计数口径不含程度与转折乘子。所有这些相邻族与本家族之间同样只允许并排, 不允许合并识别。还有两组易混列须点名: 其一, avg_pos_ratio 与 avg_neg_ratio 族测的是词典命中词的正负占比而非归一化净语调, 分母是命中词数而非加权幅度和, 与本家族量纲不同; 其二, 网络溢出族中带 _sent 后缀的列是银行与银行同句判据的结构指标, 后缀语义与本家族的 _ss 文本轨毫无关系, 机械匹配列名时极易误归, 项目在推断入口已作判据后缀剥离防御, 人工引用时同样须区分。还有第三组须点名的相邻测度是跨方法族: 词典语调与 LLM 投票语调、BERT 净语调虽同测"语调"构念, 但三者对语用现象的敏感面不同 — 词典法对显式极性词敏感、对反讽与隐含情感盲视; LLM 对上下文语用最敏感但不可逐词审计且随版本漂移; BERT 介于两者之间且受微调语料语域约束。三支柱因此不是同一测度的三次抽样, 而是三种系统性偏误互补的独立技术, 这正是把它们设为互为稳健性支柱而非取平均集成的方法论根据; 集成平均会掩盖偏误结构, 稳健性并排则暴露之。再须与 std 二阶矩族区分: bian_2021_tone_std 系测语调离散度而非水平, 与本家族均值列测不同构念 (分歧对方向), 可作为调节变量与均值列共存于同一回归, 但仍不与均值列混入同一过度识别检验。最后与加权臂内部区分: vw 权重 (提及密度) 刻画报道与银行的相关强度, mw 权重 (媒体权威) 刻画来源分量, hw 权重 (跟风衰减) 刻画信息新颖度, 三种权重回答三个正交的稳健性问题, 刻意并排不合并, 权重之间也不做交叉展开以防列爆炸。

【已知局限与稳健性梯子】
第一, 词表覆盖局限: Bian 词典为会计金融通用文本构建, 对金融科技子领域的新词 (如具体技术名词的褒贬用法) 覆盖不全, 词表外情感一律漏计; 语义漂移文献 (Zheng et al., 2024) 提示 2007 至 2025 长窗口内部分词的情感色彩可能变化, 静态词典无法自适应。第二, 规则参数为研究者选择: 否定窗口 2、程度倍率上限 3.0、转折增强 1.5 均为固定超参; 对应的稳健性由规则消融梯度承接 — 三条规则的全 powerset 物化为 raw、negonly、degonly、advonly、negdeg、negadv、degadv 七个自归一化变体列族, 各变体与全规则版本高度共线 (审计口径报相关系数而非可加分解), 因为 full 与消融臂各自自归一化且否定乘程度存在交互, 差值不可解读为单条规则的纯贡献 (MATH-1 审计结论)。第三, 自归一化的构造性后果: 得分是相对强度而非绝对量, 命中词极少的短文本得分方差大, ctx 与 ss 轨文本更短、零命中比例更高, 得分向 0 收缩属机械现象而非情感中性。第四, 聚合层的小格问题: 早期试跑 T=2 盘上部分银行-年格文章数极少, _std 与 tech/app 条件均值在小格上噪声大, 生产 T=19 语料下缓解; 涉及格内篇数的实测分布一律以引擎注入的动态统计为准, 此处不引数字。稳健性梯子的完整结构是: 词表维度六词典并排, 规则维度七消融臂并排, 文本维度三轨并排, 加权维度等权对 VW 对 MW 对 HW 四臂并排, 内容维度全样本对 tech 对 app 三臂并排, 方法维度词典对 LLM 对 BERT 三支柱并排; 各梯子相互正交、刻意不做交叉展开以防列爆炸, 且每一臂各自 just-identified, 禁混同一 over-identified Hansen J。最后是效度证据的分工: 词典轨的收敛效度由跨方法一致性承接 (词典语调与 LLM 投票、BERT 净语调在文章级与面板级的相关结构进入验证管线), 内容效度由人工盲标双编码协议承接, 区分效度由词典语调与非情感文本特征 (可读性、套话比率等) 的低相关承接; 本家族自身不内嵌任何效度统计, 相关数字见验证阶段产物, 此处不引。使用者若需单一词典结论, 应默认报告六词典全臂而非只挑显著臂, 这是本项目对词典选型研究者自由度的预注册式约束。第五, 加权臂的权重区分度局限: 当媒体权威权重或提及密度在某银行-年格内高度集中或近乎均匀时, 加权均值与等权均值机械趋同, 此时加权臂并未提供额外识别信息, 日志层的权重标准差诊断输出用于甄别这种退化, 使用者不应把趋同误读为"加权稳健性通过"。第六, locus 条件臂的分类依赖: tech 与 app 变体的内容切片完全依赖 LLM 分类维度 innovation_locus_full 的质量, 分类判据恒取 full 轨且含关键词回退, 因此这两臂的效度上限受制于分类器效度, 分类误差会以子样本错配的形式传入语调均值; 相应的分类稳健性由 LLM 分类 per-model 梯子在别处承接, 本家族不重复展开, 但解读 tech/app 差值时须记得它混合了语调差异与分类噪声两种来源。第七, 三轨零命中的非对称暴露: ctx 与 ss 轨文本更短, 零命中篇 (记 0 中性) 占比更高, 自归一化得分向 0 收缩是构造性机械现象而非情感中性, 因此跨轨绝不比较语调水平、只比较各自标准化后的效应方向, 这条与三轨禁混同一 over-identified Hansen J 的口径互为表里 — 前者是解读纪律, 后者是推断纪律。整个稳健性体系的设计哲学是把每一处研究者自由度 (词表选择、规则参数、文本轨道、加权方案、内容切片) 都显式物化为可穷举的并排梯子, 用透明的规格铺开替代隐藏的规格挑选, 这与 Algaba et al. (2020) 关于情感测度选择须作为自由度披露的方法论主张、以及 van Atteveldt et al. (2021) 关于不同测量技术系统性分歧须实证呈现的证据一脉相承。

## VAR: bian_2021_tone_app_ctx

【变体差分】
本列是家族 canonical (bian_2021_tone_full) 的双重条件化变体: 内容维度上仅对 LLM 分类维度 innovation_locus_full 取值为"应用场景"的文章子样本取均值, 文本维度上情感得分取 ctx 轨 (bian_2021_score_ctx, 即标题前置加目标银行实体窗口文本上的词典打分)。两个维度的判据来源刻意不对称: 分组判据恒用 full 轨的 locus 分类 (对角线展开刻意未做), 得分才随轨道切换, 因此本列回答的问题是"在被 full 轨判定为应用场景导向的报道里, 银行实体近旁语境的 Bian 词典语调如何"。相对 canonical 的语义收窄有两层含义: 剔除底层技术导向与无法归类的文章, 消解不同银行报道构成差异带来的组成性混杂; 同时把打分文本收窄到实体窗口, 削弱同篇文章中与目标银行无关段落的情感污染。行宇宙仍是 full-only 留篇门控下的留篇集子集, ctx 属 conditional-on-full 稳健轨。小格告警: 应用场景子样本与 ctx 短文本双重收窄后, 格内篇数和命中词数都变少, 得分噪声高于 canonical。本列与 app_full、app_ss 及 tech 系互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。与 app_full 对比可分离"文本收窄"的边际影响, 与 tech_ctx 对比可分离"内容切片"的边际影响, 两组对比正交, 报告时应成对呈现而非单列孤证。

## VAR: bian_2021_tone_app_full

【变体差分】
本列是 canonical 的内容条件化变体: 得分仍取 full 轨 (标题前置加全文正文的 Bian 词典打分, 与 canonical 完全同源), 唯一差分是聚合样本从银行-年格内全部留篇收窄为 innovation_locus_full 等于"应用场景"的文章子集, 即"该银行当年被媒体报道为应用场景导向金融科技活动的那部分报道"的平均语调。构念动机来自创新位置 (innovation locus) 理论: 媒体对银行做支付、财富管理等应用层创新的评价, 与对底层技术投入的评价可能系统性不同, 把两类报道的语调分开测量才能检验"语调效应是否由特定创新叙事驱动"。计算上由 encode.py 的分类聚合块实现: 按 locus 类别切片后单次 groupby 取 mean, 仅产均值不产 std、sum 或加权孪生 (刻意取舍, 防列爆炸); 类别缺文章的银行-年格该列为缺失, n_articles_app 记 0。与之配套的构成性防御是 tone_gap_tech_app 的最小篇数过滤, 但本列自身不设门槛, 使用者须自查小格。本列与 tech_full 是一对内容对照臂, 与 app_ctx、app_ss 是同内容跨轨梯子, 全部互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。另注意分母差异: 本列均值的分母是应用场景子集篇数 n_articles_app 而非全格 n_articles, 与 app_frac (子集篇数占 LLM 有效篇数比) 联合使用时二者分母口径不同, 不可直接相乘还原总量。

## VAR: bian_2021_tone_app_ss

【变体差分】
本列在 app 内容条件化基础上把得分轨道切到 ss 轨: 对 innovation_locus_full 等于"应用场景"的留篇子集, 取 bian_2021_score_ss 的银行-年均值。ss 轨文本等于标题前置加"目标银行与金融科技词严格同句共现"的句子及其正负一句邻句窗口, 是三轨中语义最锐利的一轨 — 打分文本几乎只剩直接把该银行与金科议题绑定的句子, 最大限度剥离文章其余部分的情感底色。回退语义必须按项目口径复述: 当一篇留篇文章不存在银行与金科同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置真, 该篇仍计入分母 (与 full 共享 n_articles 口径), 因此本列在共现稀疏的银行-年格上会向 full 轨语调回归, 解释时须结合回退占比。分组判据仍恒取 full 轨 locus 分类, 不随轨道切换。三重收窄 (留篇、应用场景、同句窗口) 使本列是全家族 21 列中格内有效信息量最小的列之一, 早期试跑 T=2 盘上表现为高缺失与高方差, 生产 T=19 下缓解。本列与 app_full、app_ctx 构成跨轨梯子, 与 tech_ss 构成内容对照, 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。实务上建议把本列放在异质性附表而非主表: 它的作用是证明应用叙事语调效应对最严格文本口径的耐受性, 而非提供主效应点估计。

## VAR: bian_2021_tone_ctx

【变体差分】
本列是 canonical 的纯轨道变体: 聚合口径与 bian_2021_tone_full 完全一致 (银行-年格内全部留篇的算术平均, 无内容条件、无加权), 唯一差分是文章级得分取 ctx 轨 bian_2021_score_ctx, 即在"标题前置加目标银行实体上下文窗口"文本上运行同一套词典状态机。ctx 轨的测量论动机是实体归因: 一篇报道可能同时讨论多家银行或穿插行业背景, 全文语调未必反映针对目标银行的评价; 把打分范围收窄到实体近旁窗口, 相当于把测量对象从"文章的情感"移向"文章对该银行的情感"。代价是双重的: 窗口截断可能切掉修饰该行的远距离情感表达, 且文本变短后词典命中数下降, 自归一化得分的方差机械上升、零命中篇份额上升 (零命中记 0 中性)。行宇宙口径: 留篇门控为 full-only, 一篇是否计入只看 llm_verified_full, ctx 是 conditional-on-full 的测度轨, 本列绝不改变行宇宙, 只改变每行的取值文本。本列与 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 若主效应仅在 full 轨显著而 ctx 轨消失, 提示效应可能由文章背景情绪而非针对性评价驱动, 这正是三轨设计要暴露的信息; 反向情形 (仅 ctx 显著) 则提示全文噪声掩盖了针对性信号, 两种模式都有明确的测量论解释。

## VAR: bian_2021_tone_full

【变体差分】
本列是家族 canonical 列与 core 列: Bian et al. (2021) 中文金融情感词典在 full 轨文本上的文章级得分, 于银行-年格内取等权算术平均, 不加任何权重、不设任何内容条件。full 轨文本等于标题前置拼接全文正文 (原标题独立轨已于 v3.8.0 移除, 标题信号以 prepend 方式并入), 是三轨中信息最完整、词典命中数最多、自归一化得分最稳定的一轨, 因此被指定为词典族六部词典各自的 headline 轨。选择该列作为家族 core 列的理由有四。第一, 它是六词典跨词表梯子中 LM 中文本土化扩充臂的代表列, 在词典支柱内与 loughran_tone_full、du_2022_tone_full 等并排, 承担"换一部词表结论是否还在"的直接检验。第二, 它是本家族全部 20 个变体列的语义锚: std 变体是它的格内二阶矩, vw、mw、hw 变体是它的加权重述, tech、app 变体是它的内容切片, ctx、ss 变体是它的文本收窄 — 读懂本列即读懂全家族的差分结构。第三, 它的计算链在全项目语调测度中确定性最强: jieba 0.42.1 冻结分词加静态词表加固定规则参数, 不依赖任何模型权重、API 版本或随机种子, 逐词命中明细可完整还原, 在复现包审计中充当 LLM 轨与 BERT 轨的可审计参照系。第四, 它与 P1 主线处理变量 llm_vote_tone_full 同轨同聚合口径 (同为 full 轨等权均值), 两列的差异干净地隔离出"测量技术"单一维度, 是跨方法稳健性表的标准对照格。计算细节复述: 文章得分等于命中词最终得分之和除以其绝对值之和, 最终得分含否定翻转 (窗口 2)、程度倍率 (上限 3.0)、转折增强 (1.5) 三条规则与句末重置; 跨类重叠词两侧同计拉向中性; 无命中记 0。聚合分母是 full-only 留篇门控下该银行-年的留篇数, 与 n_articles 口径一致。使用铁律: 本列与其余 20 列以及其他五部词典、LLM、BERT 的对应列一律互为稳健性、不分主次, 各自 just-identified 并排进入各自回归, 严禁把任意组合混进同一 over-identified Hansen J; 跨词典与跨方法的推断多重性由根级 rwolf FWER 模板统一控制, 不在本列层面处理。解读本列时还有三条实务提醒。其一, 量纲与阈值: 得分是自归一化的相对强度, 正负零点即词典意义上的褒贬平衡点, 文章级标签化沿用正负 0.1 的对称阈值, 但面板均值不做标签化, 直接以连续值入回归; 跨词典比较水平无意义 (各词典词表规模与极性构成不同, 基线各异), 只应比较标准化系数。其二, 缺失语义: 本列缺失当且仅当该银行-年格无任何留篇, 与 n_articles 为零严格对应; 零值是有效观测 (命中词正负抵消或全篇零命中), 不是缺失, 清洗时不可将零值当缺失剔除。其三, 与规则消融族的关系: 本列等价于消融谱中的全规则臂, raw 至 degadv 七个变体列族以它为参照端点, 报告消融稳健性时本列即梯子的 canonical 端, 无需另设。作为家族 core 列, 它同时是六词典梯子在复现包 Stata 模板中的默认词典臂入选列, 变量标签为 Avg Tone Bian et al. 2021 LM-CN-extended (full-track), 标签与列名的映射在 stata_export 的 curated 标签块中显式维护, 不走泛型推断; 该 curated 待遇是 2026-06-20 对称补全的产物 — 六部词典的 headline 极性列各补六个人工标签, 而本家族其余 std、vw、mw、hw、tech、app 衍生列对全部六部词典一律走泛型推断, 保持跨词典对称, 这也是本列在家族内地位的一个外部印记。就本列在 P1 识别体系中的确切角色再补三点。其一, 本列与 llm_vote_tone_full 的对照是全项目跨方法稳健性表的标准格: 两列同取 full 轨、同为等权银行-年均值、同受 full-only 留篇门控约束, 唯一变化的维度是测量技术 (静态词典对三家生成式模型投票), 因此两列系数之差干净地归因于测量技术而非轨道或聚合口径, 这是把"测量技术"作为单一可变维度隔离出来的最纯净设计。其二, 跨方法系数比较必须遵守量纲纪律: 词典自归一化得分、LLM 三分类得分与 BERT 概率差的原始方差各不相同, 跨方法对照表内一律先对系数作 z-score 标准化再比大小, 未标准化的原始系数只在各自规格内解读; 本列作为词典臂入表时同样受此约束。其三, 本列是复现包默认词典臂: 在根级 Stata 模板实例化时, 六词典梯子以本列为 bian 词典的入选代表, 跨词典多重检验的族错误率由根级 rwolf FWER 模板统一控制, 本列在其中作为 canonical 处理变量的替代测量进入同一检验族, 而 paper_spec 内声明的跨模型稳健性字段仅为文档、运行时无消费者。还须强调本列相对其余 20 列的锚点地位不等于主次地位: 家族内 21 列一律不分主次、互为稳健性, 本列被称 canonical 仅因它是差分结构的语义参照端 (无中缀、无加权、无条件、full 轨), 而非因它享有优先证据权重; 报告时应默认全臂呈现, 挑选本列单列作结论与项目的预注册式全臂披露约束相悖。

## VAR: bian_2021_tone_hw_ctx

【变体差分】
本列是 ctx 轨得分的跟风衰减加权 (herd-decay weighted, HW) 变体: 分子为格内 bian_2021_score_ctx 乘 herd_weight_ctx 的和, 分母为 sum_herd_weight_ctx, 即用 stage 24 产出的 ctx 轨跟风权重对文章降权后的加权平均。HW 的测量论动机是信息增量: 中文财经媒体存在大量转载与跟风报道, 等权均值会把同一原始信号重复计入; herd 权重对与既往报道高度相似的后发文章衰减, 使加权语调更接近"新信息流的语调"而非"报道量加权的语调"。与 vw、mw 两个加权臂的承重差异在分母口径: herd 权重本身分三轨独立计算, 本列分子分母严格同取 ctx 轨 (v3.6.0 修正了旧版全文权重和错配多轨分母的缺陷), 属逐轨匹配口径; 而 vw、mw 的权重轨道无关、分母三轨共用。若上游为 legacy 单列 herd_weight, 三轨会退化为同源并有 WARNING 日志, 使用前应确认非伪多轨。本列与等权 ctx 列的差值反映跟风报道的语调偏向。加权四臂 (等权、vw、mw、hw) 与三轨、六词典各梯子正交, 每臂各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。ctx 轨与 herd 权重的组合有一层特别的解释价值: 跟风转载稿往往整段复制原稿, 其实体窗口文本与原稿高度重合, 等权 ctx 均值因此重复计入同一窗口语调, 本列对这类重复的修正比 full 轨更直接。分母权重和为零的格记缺失, 不与零语调混同。

## VAR: bian_2021_tone_hw_full

【变体差分】
本列是 canonical 的跟风衰减加权变体: 与 bian_2021_tone_full 同为 full 轨全留篇聚合, 唯一差分是把等权均值换成 herd_weight_full 加权 — 分子取格内文章得分乘权重的和 (bian_2021_score_hw_sum_full, 由 runner 步骤 3d 预计算), 分母取 sum_herd_weight_full, 权重和为零的格记缺失。herd 权重由 stage 24 (herd_decay_processor) 基于报道与既往报道流的相似度构造, 相似度越高 (越像转载或跟风稿) 权重越低, 原创或首发性强的报道权重接近上限。经济含义: 等权 canonical 回答"该银行当年全部报道的平均语调", 本列回答"剔除重复信息后的有效语调信号"; 若两列系数在主回归中同号同量级, 说明结论不被媒体回声室效应驱动, 若 hw 臂明显更强, 提示语调效应集中于携带新信息的报道, 与媒体信息中介机制一致 (Tetlock, 2007)。跟风判定阈值本身另有敏感性网格 (thrNN 变体族, 刻意仅施于 LLM 投票主测度以防列爆炸, 词典族不展开), 本列使用生产阈值单点; 若审稿要求词典轨的阈值敏感性, 应引用 LLM 轨网格结果作方法层证据而非为词典族新增列。分母逐轨匹配口径同 hw_ctx 所述: 分子分母同取 full 轨权重, 不与 ctx、ss 分母串用。本列与等权、vw、mw 三臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 加权臂之间的系数差异本身不构成检验统计量, 只作方向一致性判读。

## VAR: bian_2021_tone_hw_ss

【变体差分】
本列是 ss 轨的跟风衰减加权变体: 分子取 bian_2021_score_ss 乘 herd_weight_ss 的格内和, 分母取 sum_herd_weight_ss, 逐轨匹配口径与 hw_full、hw_ctx 一致。ss 轨文本为标题加银行与金科同句共现句窗口, 回退语义镜像 ctx: 无同句共现的留篇其 content_ss 回退为全文正文、ss_is_fallback 置真且仍在分母中。本列的双重稳健性语义: 文本维度上把语调收窄到银行金科绑定最紧的句子, 加权维度上对跟风转载降权, 两者叠加后测量的是"针对该银行金融科技活动的、剔除重复信息的语调信号", 是全家族中概念上最接近"新增的针对性评价"的列。工程守卫: 当 stage 24 未跑同句轨导致 sum_herd_weight_ss 缺失时, encode.py 以 NaN 分母兜底, 本列整列优雅缺失而不影响 full 与 ctx 兄弟列 (逐源列 if-in-columns 守卫); 上游 legacy 单列 herd_weight 场景下三轨权重同源退化并打 WARNING, 此时本列与 hw_full 的差异只来自得分轨而非权重轨, 解释口径须相应收窄, 且日志中的伪多轨警告应在结果附注中披露。小格与回退占比告警同 ss 系其他列, 且 herd 权重对首发稿加权的特性使本列在报道量大而原创稿少的银行-年上有效样本进一步收缩。本列与其余加权臂及跨轨兄弟互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_mw_ctx

【变体差分】
本列是 ctx 轨得分的媒体权威性加权 (media-authority weighted, MW) 变体: 分子为格内 bian_2021_score_ctx 乘 media_authority_weight 的和, 分母为 sum_media_authority_weight。媒体权威权重由 encode.py 的 compute_media_authority_weights 按媒体来源层级构造并以原始权重除以均值归一化, 权威财经媒体的报道权重高于地方小报或门户转载源; 主规格用连续权重, 另有三级 tier 权重列并行作敏感性 (不进本列)。测量论动机来自 Holzman et al. (2023): 媒体情感对市场与公司行为的影响随媒体影响力分层, 权威媒体的语调信号更可能被投资者与监管者消费; MW 臂回答"若只听有分量的声音, 该银行的金科语调如何"。与 hw 臂的分母口径差异须注意: media_authority_weight 是文章级轨道无关属性, 分母对三轨共用同一个权重和, 本列与 mw_full、mw_ss 的分母相同, 差异全部来自分子的得分轨。ctx 轨语义 (实体窗口打分、conditional-on-full、短文本方差放大) 同 bian_2021_tone_ctx 所述。本列的典型判读场景: 若等权 ctx 列显著而本列不显著, 提示针对性语调效应主要由低权威来源承载, 结论的政策含义须相应弱化; 反之则说明效应经得起"只算权威声音"的收紧。权重和为零的格记缺失; tier 三级权重的敏感性版本不产词典族孪生列, 本列即 MW 口径在本家族的唯一代表。本列与等权、vw、hw 三臂及跨轨兄弟互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_mw_full

【变体差分】
本列是 canonical 的媒体权威性加权变体: full 轨得分不变, 等权均值换成 media_authority_weight 加权平均, 分子由 runner 步骤 3c 预计算的 bian_2021_score_mw 列聚合为和, 分母为该银行-年全部留篇的权威权重之和, 权重和为零的格记缺失。构念上, canonical 把每篇报道当作等价的一票, 本列把媒体分量引入投票权: 同样一批报道, 若负面评价集中在权威财经媒体而正面吹捧集中在低权威来源, 本列会显著低于等权列, 反之亦然, 因此两列之差本身携带"语调的来源结构"信息。文献锚点是 Holzman et al. (2023) 对媒体情感分层影响的证据, 以及中文语境下 You et al. (2018) 关于不同媒体激励结构导致报道内容系统性差异的发现 — 在中国财经媒体市场, 官方背景媒体与市场化媒体的语调基线不同, 权威加权可部分吸收这一构成差异。权重构造为原始层级分值除以样本均值的连续归一化 (均值锚定为一, 使加权均值与等权均值量纲直接可比), 权重区分度诊断在日志层有标准差判读输出, 区分度过低时加权臂与等权臂机械趋同, 属预期而非异常。分母三轨共用口径同 mw_ctx 所述, 权重和为零的格记缺失。本列与等权、vw、hw 三臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_mw_ss

【变体差分】
本列是 ss 轨得分的媒体权威性加权变体: 分子为格内 bian_2021_score_ss 乘 media_authority_weight 的和, 分母沿用三轨共用的 sum_media_authority_weight。语义组合是"权威媒体视角下的银行金科同句语调": 文本维度把打分收窄到银行与金融科技直接绑定的句子窗口, 权重维度放大权威来源的话语权。ss 回退语义照例复述: 无银行金科同句共现的留篇, content_ss 回退为全文正文且 ss_is_fallback 置真, 仍计入分母; 因此在共现稀疏格上本列向 mw_full 回归, 两列差异收缩属机械现象。使用场景: 当研究关心"权威媒体是否更倾向以质疑口吻报道银行的金科绑定叙事"时, 本列与 mw_full 的对比提供直接证据 (二者分母相同, 差异干净地来自打分文本的收窄, 这是三轨共用分母口径带来的解释便利); 当关心的是加权方式本身的稳健性时, 本列应与 ss 轨等权列及 vw_ss、hw_ss 并排。工程口径: ss 源列缺失时逐源守卫优雅跳过, 不影响兄弟列; 本列继承 ss 轨全部小格与零命中告警, 加权后有效样本量进一步由权重分布决定, 权威权重高度集中的格上实际自由度低于篇数。本列与各加权臂、各轨道兄弟互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_ss

【变体差分】
本列是 canonical 的第二个纯轨道变体: 聚合口径与 full、ctx 完全一致 (全留篇等权均值), 得分取 ss 轨 bian_2021_score_ss。ss 轨是三轨梯子中语义最严格的一轨: 文本等于标题前置加"目标银行与至少一个金融科技词出现在同一句"的句子及其正负一句邻句 (窗口半径由 config 键 ss_sentence_radius 控制, 默认 1), 銀行侧判定含否定与短名过滤、金科侧为裸 AC 自动机词表命中, 判定口径刻意不对称。回退语义是本列解释的承重墙, 必须按项目铁律复述: 无银行金科同句共现的留篇, content_ss 回退为全文正文、ss_is_fallback 置真, 该篇仍计入分母 (与 full 共享 n_articles 口径), 优雅降级下 FINTECH_AC 缺失时全部置回退。因此本列不是"仅共现文章的语调"而是"共现文章取同句窗口、其余文章取全文"的混合测度, 共现占比越低越接近 full 列; 若需纯共现子样本口径, 应结合回退指示列自行切片。测量价值: 同句共现是银行与金科议题绑定强度的最硬判据, 本列在三轨中对"针对性语调"的效度最高、对样本损失和短文本噪声的暴露也最大。三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 注意 ss 轨与 stage 13 共现硬过滤及网络判据后缀 _sent 是三个不同口径, 禁互相混淆。

## VAR: bian_2021_tone_std_ctx

【变体差分】
本列不是语调水平而是语调离散度: bian_2021_score_ctx 在银行-年格内的样本标准差, 与 std_full、std_ss 构成二阶矩三轨梯子。构念上, 均值列回答"媒体总体怎么评价", 本列回答"媒体评价有多分裂": 同一银行同一年内, 若不同报道对其金科活动的 ctx 轨语调高度分化 (有的实体窗口满是正面词、有的满是风险词), 本列取高值, 对应媒体分歧 (media disagreement) 构念, 与 bank_media_disagreement 论文模块的测度族概念相邻但计算独立。ctx 轨的离散度有其特有的机械成分: 实体窗口文本短、词典命中稀疏, 自归一化得分在少词文本上取值粗粝 (少数几个词决定得分正负), 因此 ctx 轨标准差的水平天然高于 full 轨, 跨轨比较离散度水平无意义, 只应比较各自标准化后的效应; 把本列解读为分歧信号前, 应先以格内篇数与平均命中词数为条件排除机械方差。计算为 pandas groupby std (样本口径, ddof 为 1), 格内仅一篇时记缺失, 小格上估计噪声大, 早期试跑 T=2 盘上尤甚。使用铁律: 本列作为二阶矩测度与均值列测不同构念, 可以同均值列共存于同一回归的不同角色 (如均值为处理、离散度为调节), 但其三轨与跨词典变体之间仍互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_std_full

【变体差分】
本列是 full 轨语调的格内标准差, 二阶矩梯子的 headline 轨: 对银行-年格内全部留篇的 bian_2021_score_full 取样本标准差。测量论定位: 词典语调的均值与离散度携带互补信息, 均值刻画评价方向, 离散度刻画评价共识度; 财务文本文献中分歧类测度与波动、交易量及信息不确定性相关联, 媒体语调离散度可作为银行信息环境不确定性的代理。在本项目的测度体系中, 本列有三个用途: 其一作为描述性统计刻画语调分布形状 (与 BERT 分布形状五族的年内波动测度概念平行但方法独立); 其二作为均值效应的调节变量候选 (语调效应在媒体共识高的银行-年上是否更强); 其三作为异质性稳健性 — 若主效应仅存在于低离散度子样本, 提示效应由一致性叙事而非个别极端报道驱动。计算细节: std 与 mean 在同一 groupby 中产出, 分母同为 full-only 留篇集, 格内仅一篇时缺失; 自归一化得分有界于负一到正一, 故标准差理论上界为 1, 实际分布以引擎注入的动态统计为准, 此处不手填数字。本列与 std_ctx、std_ss 及其他词典的 std 列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_std_ss

【变体差分】
本列是 ss 轨语调的格内标准差: bian_2021_score_ss 在银行-年格内的样本 std, 二阶矩梯子的同句共现臂。解释本列须同时叠加 ss 轨的两条特性。其一是回退混合: ss 得分列对无同句共现的留篇取全文打分 (回退语义镜像 ctx, ss_is_fallback 置真、共享分母), 因此本列测到的离散度部分来自"共现篇的窗口语调与回退篇的全文语调之间的口径差", 在回退占比中等的格上这一机械成分最大, 纯粹的评价分歧解释须以回退占比为条件。其二是短文本粗粝性: 同句窗口通常只有一到三句, 词典命中数少, 单篇得分接近离散取值, 格内 std 相应偏高且对个别零命中篇 (记 0 中性) 敏感。因此本列的合理用法是作为 std_full 的方向性稳健臂 (分歧信号在收窄到银行金科绑定句后是否仍在), 而非独立的水平测度; 跨轨比较 std 水平无意义。计算口径与兄弟列一致: groupby 样本标准差 (ddof 为 1), 单篇格缺失, ss 源列整列缺失时优雅跳过、不牵连 full 与 ctx 兄弟。本列与 std_full、std_ctx 及跨词典对应列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 二阶矩三轨同样不设主次, 跨轨只比方向不比水平。

## VAR: bian_2021_tone_tech_ctx

【变体差分】
本列是内容与文本双重条件化变体的技术臂: 对 innovation_locus_full 等于"底层技术"的留篇子集, 取 bian_2021_score_ctx 的银行-年均值, 与 app_ctx 构成 locus 二分的另一半。构念动机: 底层技术导向的报道 (银行自研系统、区块链、大数据风控等基础设施叙事) 与应用场景报道的媒体评价逻辑不同 — 技术投入报道更常与不确定性、投入产出质疑并存, 应用报道更常与用户增长、便利性等正面框架并存, 分开测量使"语调效应的内容来源"可检验。分组判据恒用 full 轨 locus 分类 (LLM 混合分类加关键词回退产生, 带类别置信度列), 得分取 ctx 轨实体窗口打分, 组合语义是"技术叙事报道中银行实体近旁的词典语调"。工程口径: locus 类别缺文章的格记 n_articles_tech 为 0、语调列缺失; 非预期类别值有防御性告警且不计入。小格告警在本列尤为突出: 技术导向报道在多数银行-年格内占比不高, 叠加 ctx 短文本后有效信息进一步压缩。本列与 tech_full、tech_ss 构成跨轨梯子, 与 app_ctx 构成内容对照臂, 全部互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。判读提示: 技术叙事报道的行文常以技术本身为主语, 银行实体在句中出现的频率与位置和应用报道不同, 本列与 tech_full 的差异因此混合了窗口截断与叙事结构两种成分, 不宜过度解读其差值。

## VAR: bian_2021_tone_tech_full

【变体差分】
本列是 canonical 的技术内容条件化变体: full 轨得分不变, 聚合样本收窄为 innovation_locus_full 等于"底层技术"的文章子集, 即"该银行当年被报道为底层技术导向金融科技活动的报道"的平均 Bian 词典语调。它与 app_full 合起来构成对 canonical 的一个内容分解: canonical 均值近似等于两个条件均值按各自篇数份额的加权组合再加上未归类篇的贡献, 因此三列联合读出"总体语调水平中有多少来自技术叙事、多少来自应用叙事"。识别用途有二: 其一, P4 主线 (innovation locus) 的处理变量是 locus 份额类测度, 本列提供"份额之外的语调质量"补充维度 — 银行不仅在多大程度上被报道为技术导向, 还被以何种口吻报道; 其二, 作为 P1 语调效应的内容异质性稳健臂, 若语调效应仅由某一 locus 子类驱动, 本列与 app_full 的并排回归会暴露。计算由 encode.py 分类聚合块单次 groupby 产出, 仅 mean 不产 std 与加权孪生 (刻意取舍); 配套的 tone_gap_tech_app 设有双侧最小五篇过滤以防构成性混杂, 本列自身无门槛, 小格自查; 类别缺篇的银行-年格本列缺失而 n_articles_tech 记 0, 两列联合读出覆盖结构。本列与 tech_ctx、tech_ss、app 系互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_tech_ss

【变体差分】
本列是技术内容臂的 ss 轨变体: 对 innovation_locus_full 等于"底层技术"的留篇子集, 取 bian_2021_score_ss 的银行-年均值。三重口径叠加 — full-only 留篇门控决定行宇宙, full 轨 locus 分类决定内容切片, ss 轨同句窗口决定打分文本 — 使本列成为"银行与金科在句子层面直接绑定、且整篇被判为技术叙事"这一最窄口径下的词典语调。测量价值与代价并存: 价值在于它剥离得最干净, 若在这一口径下语调效应仍存在, 针对性解释最强; 代价在于三重收窄的复合样本损耗, 多数银行-年格内满足条件的篇数很少, 得分噪声与缺失率是全家族最高档, 在浅面板上常整列退化, 生产 T=19 语料下才具备稳定估计条件。ss 回退语义照例适用且与内容切片交互: 回退篇 (无同句共现) 的 ss 得分等于全文打分, 若技术叙事报道的共现率系统性低于应用叙事 (技术报道可能整篇谈技术而不逐句点名银行), 本列的回退占比会高于 app_ss, 跨臂比较时须意识到这一构成差异。工程守卫与兄弟列一致: 源列缺失优雅跳过, 类别缺篇记缺失。本列与 tech_full、tech_ctx 及 app_ss 互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_vw_ctx

【变体差分】
本列是 ctx 轨得分的价值加权 (value-weighted, VW) 变体: 分子为格内 bian_2021_score_ctx 乘 mention_density 的和 (runner 步骤 3b 预计算的 bian_2021_score_w_ctx 聚合), 分母为 sum_mention_density。mention_density 是目标银行在该篇文章中的提及密度, 加权逻辑承袭 Hassan et al. (2019) 的暴露度加权思想: 一篇通篇聚焦该银行的深度报道与一篇仅顺带提及的行业综述, 对该银行信息环境的贡献不应等价, 提及密度作为文章层面"与该银行相关程度"的连续代理, 把语调均值从"每篇一票"改为"按相关度计票"。与 ctx 轨自身的实体窗口逻辑形成互补而非重复: ctx 收窄的是打分文本 (窗口内的词), VW 加权的是文章间的相对话语权 (整篇的密度), 两个机制作用于不同层次, 叠加后本列同时抑制"窗口外情感污染"与"低相关报道稀释"两类测量误差, 是针对性语调的双保险口径。分母口径: mention_density 轨道无关, 分母三轨共用, 本列与 vw_full、vw_ss 分母相同; 密度和为零的格记缺失。词典族 VW 分母用全留篇权重和 (LLM 族才走 valid-mask 匹配分母, 词典得分无缺标问题故不需), 口径以代码为准; 密度和为零的格记缺失。本列与等权 ctx、mw_ctx、hw_ctx 构成加权四臂, 与 vw_full、vw_ss 构成跨轨梯子, 全部互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_vw_full

【变体差分】
本列是 canonical 的价值加权变体: full 轨得分不变, 等权均值换成 mention_density 加权平均, 分子为 bian_2021_score_w_full 的格内和, 分母为 sum_mention_density, 密度和为零的格记缺失。构念对照: canonical 假设该银行-年的每篇留篇对语调信号贡献相同, 本列假设贡献与目标银行在文中的提及密度成正比, 后者更接近"读者实际接收到的关于该银行的语调剂量"。加权思想的文献锚点是 Hassan et al. (2019) 在电话会议文本上按主题相关片段占比构造公司层面暴露度的做法; 在媒体语调场景, Marchetti et al. (2025) 的银行报道语调聚合同样面临"报道相关度异质"问题。本列与 canonical 的差值有诊断价值: 若二者背离, 说明高密度报道 (深度聚焦该行的稿件) 与低密度报道 (顺带提及) 的语调系统性不同, 这本身是媒体注意力配置的信息; 若几乎重合, 说明等权口径足够稳健、报道相关度分布对该银行-年近似同质。工程细节: 权重取文章级 mention_density 并对缺失填零 (缺失密度的文章不进分子分母, 等价于零权重剔除), 与 is_positive、is_negative 等频次列共用同一套加权预计算基建; VW 分子分母均在 encode 聚合后于派生块相除, 密度和为零的格记缺失。本列与等权、mw、hw 三臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: bian_2021_tone_vw_ss

【变体差分】
本列是 ss 轨得分的价值加权变体: 分子为格内 bian_2021_score_ss 乘 mention_density 的和, 分母沿用三轨共用的 sum_mention_density。语义组合为"按银行提及密度计票的同句共现语调": ss 轨保证打分文本是银行与金科直接绑定的句子窗口, VW 权重保证深度聚焦该行的报道话语权更大, 两个相关性机制叠加后, 本列是家族内对"高相关报道的针对性语调"最敏感的加权列。与 hw_ss 的概念分工: vw 加权针对报道与银行的相关强度, hw 加权针对报道的信息新颖度, 两者回答不同的稳健性问题, 刻意并排不合并。ss 回退语义照例复述: 无同句共现的留篇 content_ss 回退全文、ss_is_fallback 置真且仍计入分子分母, 故在共现稀疏格上本列向 vw_full 回归; 又因深度聚焦报道更可能存在同句共现, 回退篇的 VW 权重经验上偏低, 回退对本列的实际污染小于等权 ss 列, 这是 VW 与 ss 叠加的一个良性交互; 定量的回退占比与密度分布以引擎注入的动态统计为准, 此处不引数字。工程口径: ss 源列缺失时逐源守卫优雅跳过、不牵连兄弟列, 密度和为零格缺失, 小格告警继承 ss 系全部条款。本列与 vw_full、vw_ctx 及其余加权臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Li, Y. (2026). The textual tone of annual reports and market attention: Evidence from Chinese listed companies. Managerial and Decision Economics. https://doi.org/10.1002/mde.70100
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
Sun, Y., Yu, Z., Sun, Y., Xu, Y., & Song, B. (2025). A novel approach for multiclass sentiment analysis on Chinese social media with ERNIE-MCBMA. Scientific Reports. https://doi.org/10.1038/s41598-025-03875-y
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y. (2024). The effects of sentiment evolution in financial texts: A word embedding approach. Journal of Management Information Systems, 41(1), 178-205. https://doi.org/10.1080/07421222.2023.2301176
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Fatouros, G., Soldatos, J., Kouroumali, K., Makridis, G., & Kyriazis, D. (2023). Transforming sentiment analysis in the financial domain with ChatGPT. Machine Learning with Applications, 14, 100508. https://doi.org/10.1016/j.mlwa.2023.100508
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K. (2020). Econometrics meets sentiment: An overview of methodology and applications. Journal of Economic Surveys, 34(3), 512-547. https://doi.org/10.1111/joes.12370
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing (EMNLP), 595-605. https://doi.org/10.18653/v1/d16-1057
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based approach to opinion mining. Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08), 231-240. https://doi.org/10.1145/1341531.1341561
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.01.067
Wei, L., Wei, M., Jing, H., & Jing, Z. (2025). Annual report tone and bank risk-taking behavior: Evidence from China. Research in International Business and Finance. https://doi.org/10.1016/j.ribaf.2025.102881
Zhang, L., Abedin, M. Z., & Liu, Z. (2024). Incorporating media news to predict financial distress: Case study on Chinese listed companies. Journal of Forecasting. https://doi.org/10.1002/for.3089
<!-- rendered-citations:end -->
