---
family_id: F190
columns:
- dict_avg_tone_app_ctx
- dict_avg_tone_app_full
- dict_avg_tone_app_ss
- dict_avg_tone_ctx
- dict_avg_tone_ctx_z
- dict_avg_tone_full
- dict_avg_tone_full_z
- dict_avg_tone_hw_ctx
- dict_avg_tone_hw_ctx_z
- dict_avg_tone_hw_full
- dict_avg_tone_hw_full_z
- dict_avg_tone_hw_ss
- dict_avg_tone_hw_ss_z
- dict_avg_tone_mw_ctx
- dict_avg_tone_mw_ctx_z
- dict_avg_tone_mw_full
- dict_avg_tone_mw_full_z
- dict_avg_tone_mw_ss
- dict_avg_tone_mw_ss_z
- dict_avg_tone_ss
- dict_avg_tone_ss_z
- dict_avg_tone_std_ctx
- dict_avg_tone_std_full
- dict_avg_tone_std_ss
- dict_avg_tone_tech_ctx
- dict_avg_tone_tech_full
- dict_avg_tone_tech_ss
- dict_avg_tone_vw_ctx
- dict_avg_tone_vw_ctx_z
- dict_avg_tone_vw_full
- dict_avg_tone_vw_full_z
- dict_avg_tone_vw_ss
- dict_avg_tone_vw_ss_z
unit: 语调得分 (连续, 约 [-1,1]; _z 变体为年度截面标准化后的无量纲 z 值; _std 变体为组内标准差, 非负)
formula: "文章级: {d}_score = Σ(final_score)/Σ|final_score| ∈ [-1,1] (final_score = 词典基础极性 × 程度副词乘子 × 否定翻转 × 转折乘子); 面板级: {d}_tone{track} = bank-year 内文章得分等权均值; dict_avg_tone{track} = mean_d({d}_tone{track}), d ∈ 6 词典 {jiang_2021, yao_2021, bian_2021, du_2022, you_2018, loughran}; 加权变体: dict_avg_tone_vw = mean_d(Σ(w_vw·score)/Σw_vw) (w_vw = 提及密度), _mw 同构 (w_mw = 媒体权威权重), _hw 同构 (w_hw = 跟风衰减权重, 分母逐轨 sum_herd_weight_{track}); dict_avg_tone_std{track} = mean_d({d}_tone_std{track}) (组内文章得分标准差的跨词典均值); dict_avg_tone_app/_tech{track} = innovation_locus_full ∈ {应用场景, 底层技术} 条件子样本上的同构均值; *_z = 年度截面 z-score (仅 n_articles>0 行, 组内 μ=0/σ=1)"
producer: pipeline/panel/encode.py::aggregate_panel (逐词典聚合 + vw/mw/hw 加权 + _tech/_app 分类聚合) ; pipeline/panel/geography.py::compute_composite_indicators (步骤 7 跨词典综合) ; pipeline/panel/geography.py::standardize_panel_variables (步骤 7b 年度截面 _z)
upstream:
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本)
- 22_tone_words.parquet (六词典文章级得分)
- 21_tone_llms.parquet (llm_verified_full 留篇门控 + innovation_locus 分类标签)
- 24_herd_decay.parquet (跟风衰减权重, _hw 变体)
citations:
- doi: 10.1016/j.econlet.2025.112803
  type: journal
  authors: Aksoy-Yurdagul, D., Buchner, A., & Zareei, A.
  year: 2026
  title: "The persistence of news sentiment: Implications for return predictability"
  venue: Economics Letters
  vol: 260
  pages_or_artno: "112803"
- doi: "10.1111/acfi.13328"
  type: "journal"
  authors: "Ni, Y."
  year: 2024
  title: "Media coverage and disclosure of short‐termism tone: Evidence from China"
  venue: "Accounting & Finance"
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
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: Article 20
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
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
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
- doi: 10.1111/joes.12370
  type: journal
  authors: Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K.
  year: 2020
  title: "Econometrics meets sentiment: An overview of methodology and applications"
  venue: Journal of Economic Surveys
  vol: 34
  issue: 3
  pages_or_artno: 512-547
- doi: 10.18653/v1/d16-1057
  type: journal
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
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
- doi: 10.2469/faj.v73.n3.3
  type: journal
  authors: Heston, S. L., & Sinha, N. R.
  year: 2017
  title: "News vs. sentiment: Predicting stock returns from news stories"
  venue: Financial Analysts Journal
  vol: 73
  issue: 3
  pages_or_artno: 67-83
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
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
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1007/s11135-024-01896-9"
  type: journal
  authors: "Rutkowska, A., & Szyszko, M."
  year: 2024
  title: "Dictionary-based sentiment analysis of monetary policy communication: on the applicability of lexicons"
  venue: "Quality & Quantity"
- doi: "10.1016/j.ribaf.2025.102881"
  type: journal
  authors: "Wei, L., Wei, M., Jing, H., & Jing, Z."
  year: 2025
  title: "Annual report tone and bank risk-taking behavior: Evidence from China"
  venue: "Research in International Business and Finance"
- doi: "10.3390/bdcc9100263"
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  venue: "Big Data and Cognitive Computing"
  type: "journal"
- doi: "10.1002/mde.70100"
  title: "The Textual Tone of Annual Reports and Market Attention: Evidence From Chinese Listed Companies"
  authors: "Li, Y."
  year: 2026
  venue: "Managerial and Decision Economics"
  type: "journal"
new_dois:
- "10.1111/acfi.13328"
- "10.1007/s11135-024-01896-9"
- "10.1016/j.ribaf.2025.102881"
- "10.3390/bdcc9100263"
- "10.1002/mde.70100"
---

## CORE

该文利用文本语调(tone)测度方法, 考察中国上市公司媒体报道与短期主义披露语调之间的关系, 与本测度族基于词典的语调打分构念高度相关。

【构念与来源】
本家族测度的构念是银行金融科技新闻报道的词典法语调 (dictionary-based tone): 对每一篇进入样本的银行与金融科技共现报道, 用情感词典逐词计分并归一化为区间约在负一到正一之间的极性得分, 再在银行乘年份的面板格内做均值聚合, 得到该银行当年被媒体报道时的平均情感倾向。得分为正表示该银行金融科技相关报道整体偏正面, 为负表示整体偏负面, 接近零表示中性或正负相抵。家族名中的关键词是跨词典综合 (dict average): 本家族不依赖任何单一词典, 而是把六部中文金融情感词典的银行年语调逐格做等权算术平均, 从而把单一词典的词表覆盖偏差与编纂口味平均掉。六部词典在代码单一事实源 (encode 模块的词典名列表) 中登记为姜富伟等中文金融词典, 姚加权等词典, 边江泽等词典 (Bian et al. (2021) 会计金融中文情感词典), Du et al. (2022) 发表于金融评论的中文金融情感词典, 游家兴等媒体报道词典 (You et al. (2018) 关于中国财经媒体笔杆子俘获的研究所配套的词表传统), 以及 Loughran 与 McDonald 金融词典的中文主译全本 (Loughran 和 McDonald (2011) 原典, 项目内以词表主译落地, 单一事实源为 tone_dicts.json)。词典法测量金融文本语调的范式由 Tetlock (2007) 与 Loughran 和 McDonald (2011) 奠基: 前者证明媒体悲观语调对市场有系统性预测力, 后者证明通用词典在金融语境会系统性误判, 领域专用词典是必需品。中文语境的领域专用性论证由 Du et al. (2022) 给出: 中文金融文本的情感词分布与英文和通用中文都显著不同, 直接翻译或借用通用词典会引入大量噪声, 这正是本家族坚持六部中文金融专用词典并联的原因。近年的细粒度中文词典工作 (Ma et al. (2025) 的 CN-FSD) 进一步表明中文金融情感词典仍在演进, 多词典平均是对"词典代际差异"这一测量不确定性来源的直接对冲。数据来源链条是: 原始媒体报道语料经 stage 13 银行与金融科技词邻近共现硬过滤 (只保留目标银行与至少一个金融科技词在正负一句窗口内共现的文章, 标题参与匹配; 银行侧判定带否定与短名过滤以剔除误匹配, 金融科技侧为词表裸匹配, 这一判定不对称是全项目统一口径), stage 14 物化三轨文本 (标题 prepend 进正文, 原始内容列不动), stage 22 逐词典计分, 面板聚合阶段按银行乘年份收拢。语料的经济学身份是"银行乘金融科技"交叉叙事的媒体切片, 因此本家族语调不是银行的一般媒体形象, 而是特定于其金融科技活动的媒体评价 — 这一构念窄化是与一般银行声誉测度的根本区别。词典列名与别名的单一事实源在 tone_words 模块的词典列别名映射与 tone_dicts.json 词表文件: loughran 词典在 v3.10.0 加入为第六部 (Loughran 和 McDonald (2011) 词表的中文主译全本, 正面与负面两侧均译), 加入的同时删除了旧的非情感占位词表, 凡涉 L&M 词表内容一律以 tone_dicts.json 落盘版本为准而不回读词典源料。

【方法学与计算】
文章级计分在 stage 22 (tone_words 模块) 完成。文本先经 jieba 分词 (版本冻结在 0.42.1, 保证跨机器跨时间的分词确定性), 逐 token 查六部词典各自的极性表; 命中的词取词典基础极性作为底分, 然后依次施加三条语言学规则: 否定词窗口内极性翻转 (处理"不良"与"不 良好"这类否定结构, 否定处理是词典法公认的首要误差源, 见 Punetha 和 Jain (2025) 的专门研究), 程度副词乘数放大 (最高乘三倍, "大幅改善"强于"改善"), 转折连词乘数加权 (转折后子句按一点五倍加权, "虽然亏损但大幅减亏"的重心落在转折后)。这套规则体系的方法学源头是 Taboada et al. (2011) 的词典加规则范式: 纯词袋计数丢失局部语法信息, 少量高频语法规则能以极低成本回收大部分损失。逐篇得分的归一化公式是全部命中词最终得分之和除以最终得分绝对值之和, 落在负一到正一闭区间; 分母用绝对值和而非裸词数, 保证程度副词与转折乘数不会把得分推出界。六部词典中 du_2022 有一个特殊处理: 其政治正面词子表按零点五权重计入正侧, 依据是 Du et al. (2022) 发现政治正面词的情感信号弱于普通正面词; 该权重另有零和一两个敏感性臂 (政治词权重梯子, 属 du_2022 单词典族, 不在本家族), 三权重互为稳健性不分主次。面板聚合在 encode 模块的 aggregate_panel 完成: 每个银行乘年份格内, 先把该银行当年全部留存文章的逐篇得分做等权平均得到单词典列 (等权均值是媒体语调聚合的标准口径, Marchetti et al. (2025) 对银行融资条件语调的聚合采用同构做法), 再由 geography 模块的 compute_composite_indicators (步骤 7) 把六个单词典银行年语调做跨词典等权平均, 生成本家族无加权后缀的三轨基准列; 缺列时 _safe_mean 优雅返回缺失而不崩溃。留篇门控遵循 full-only 口径 (2026-06-29 裁定): 一篇文章是否计入"银行金融科技报道"只看 full 轨的 LLM 验证标志, ctx 与 ss 轨是 conditional-on-full 的测度轨, 行宇宙为 full 留篇集的子集。加权变体在 encode 内逐词典先算再跨词典平均: vw 用文章对目标银行的提及密度作权重 (权重设计承袭 Hassan et al. (2019) 用相关文本占比刻画暴露强度的思想), mw 用媒体权威性权重 (锚定 Holzman et al. (2023) 对媒体情感按媒体权威分层的证据), hw 用跟风衰减权重 (stage 24 生成, 对短窗口内重复跟进的报道按衰减折扣, 使测度偏向首发信息; 新闻情感的持续性与陈旧信息问题见 Aksoy-Yurdagul et al. (2026) 与 Heston 和 Sinha (2017)); 三种加权的公式统一为权重乘得分之和除以权重之和。一个承重的实现细节: 词典族的加权分母用全物理域权重和, 不做 LLM 族那种有效行掩码修正, 因为词典对每篇文章都产出数值得分 (无匹配词记零而非缺失), 分子分母天然同域, 套掩码反而会过度修正; 这与 LLM 加权列的 valid-mask 分母是刻意的不对称。hw 分母自 v3.6.0 起逐轨独立 (full, ctx, ss 各用自己的权重和), 修正了早期版本把全文权重和错配给多轨的度量与处理不匹配问题。标准化变体 _z 由步骤 7b standardize_panel_variables 生成: 对白名单内的核心回归变量, 在每个年度截面内 (仅限当年有新闻覆盖即 n_articles 大于零的银行) 减截面均值除截面标准差, 沿袭金融实证中两阶段截面回归传统对变量截面可比性的要求; 观测不足十个的列跳过, 原始列保留不动。白名单覆盖本家族的基准三轨与 vw, mw, hw 三种加权三轨共十二个格, 离散度列与分类条件列刻意不入白名单 (标准差与条件子样本均值的截面分布不满足标准化的解释前提)。分类条件变体 _app 与 _tech 的样本域由 stage 21 的创新落点分类决定: LLM 把每篇报道的创新叙事归入应用场景或底层技术两类 (混合 LLM 与关键词回退的分类器, 带分类置信度列), encode 的分类聚合分支按 full 轨分类标签切子集后逐词典求子集均值, 三轨情感源列均可与该 full 轨标签交叉 — 分类锚定 full 而情感允许换轨, 因为分类判断需要全篇语境, 情感窗口收紧则是测度稳健性设计。缺失语义全家族统一: 零新闻覆盖的银行年不参与聚合, 全部列记缺失而非零 — 把"没被报道"编码为零会与"被中性报道"混同, 是媒体测度面板的经典陷阱; 分类条件列在类内零篇时同样记缺失且配套计数列记零, 供使用者显式建模选择性。全部列以双精度浮点落盘, 经 stata_export 阶段带英文变量标签导出至最终 dta, 供 Stata 模板直接消费。

【文献定位】
本家族处在金融文本情感测量三角 (词典法, 机器学习或 BERT, 大语言模型) 的词典法顶点。Frankel et al. (2022) 系统比较了机器学习与词典法测披露情感, 结论是两法各有测量误差且不完全重叠, 学界最佳实践是并行报告而非单选; van Atteveldt et al. (2021) 用人工标注作金标准比较了词典, 众包与机器学习的效度, 发现词典法效度虽然通常低于监督学习, 但其完全透明, 零训练成本与完美可复现的特性使其成为不可替代的基准臂; Todd et al. (2024) 对金融文本情感文献的综述同样把词典法列为持续活跃的基础方法而非被淘汰的旧法。本项目据此把词典法设计为与 LLM 三家投票和 BERT 三模型并排的三方法之一: dict_avg_tone 是词典法的家族旗舰, 与 llm_vote_tone 和 bert 综合列互为跨方法稳健性。方法学的计量经济学定位见 Algaba et al. (2020) 的情感计量综述: 情感变量进入回归的核心威胁是测量误差导致的系数向零衰减, 多测度并行与截面标准化都是标准应对。词典质量本身的证据链是: García et al. (2023) 用重叠样本证明金融词典的词级信号在控制了体裁与话题后仍然显著载荷于收益, 词典法的信息含量有底; Hamilton et al. (2016) 从无标注语料自动归纳领域情感词典的扩展传统与 Sun et al. (2025) 把词典知识注入预训练模型的混合路线, 说明词典与神经方法正在融合而非替代。中国银行业场景的外部效度锚是 Fang et al. (2024): 中国媒体情感对存款稳定性与银行系统性风险有实证可测的影响, 银行年媒体语调是有经济后果的变量。Barbaglia et al. (2025) 对经济文本词典法的当代重述则支撑本家族"规则增强词典"的具体技术选型: 该文证明在经济新闻语料上, 配备否定与修饰规则的词典测度对宏观与信用变量有稳定预测力, 词典法的简单性在大规模纵向语料上反而是优势 — 本项目一千八百一十九万条量级的生产语料上, 词典臂是唯一能以零边际成本全量重算, 且任何第三方拿到词表即可字节级复核的方法臂, 这一可审计性对政策与监管取向的研究场景 (Fang et al. (2024) 所处的中国银行稳定性脉络) 具有独立价值。Rutkowska 和 Szyszko (2024, Quality & Quantity) 系统检验了词典法情感分析在不同语域文本上的适用边界与词表迁移问题, 呼应本家族六词典并联以对冲单一词表覆盖偏差的设计动机。Wei 等 (2025, Research in International Business and Finance) 用中国上市银行年报文本语调预测银行风险承担行为, 为本家族银行年语调测度提供中国银行业场景下的经济后果外部效度佐证。Chuang 等 (2025, Big Data and Cognitive Computing) 比较词典法与语言模型在中文财经新闻情感分类与股价预测任务上的表现, 为词典法跨方法基准提供最新对照证据。Li (2026, Managerial and Decision Economics) 用词典法测度中国上市公司年报文本语调, 检验其与市场关注度的关联, 与本家族词典语调聚合的构念高度对应。跨词典平均的统计学依据是测量误差的经典结果: 若六部词典对同一潜在语调各自给出带独立特异误差的测量, 等权平均把特异误差方差按词典数缩减, 且不像数据驱动的最优加权那样引入过拟合与前视风险; 词典间的系统性共同偏差 (譬如全部词典对新词的覆盖缺口) 无法被平均消除, 这一残余偏差正是需要 LLM 与 BERT 臂交叉验证的部分。

【识别策略定位】
在论文组合中, 本家族不是任何一篇论文的主处理变量: P1 (bank_fintech_tone) 的 treatment 主轨是 llm_vote_tone_full, 词典家族的角色是三方法三角中的词典臂, 用于证明主结论不依赖 LLM 这一种测量技术。跨词典等权平均使 dict_avg_tone 成为词典臂的单点代表: 六个单词典列各自与 dict_avg_tone 并排, 供逐词典替换的规格曲线使用。识别口径上必须复述项目铁律: 三轨 (full, ctx, ss), 四种聚合权重 (等权, vw, mw, hw), 六部单词典, 以及 LLM 与 BERT 方法臂, 全部是互为稳健性不分主次的并排测度, 每一个都只在各自 just-identified 的回归里出现, 严禁把任意两个及以上塞进同一个 over-identified 的 Hansen J 检验做联合过度识别 — 它们测的是同一构念的不同噪声实现, 联合检验的拒绝只反映测量差异而非工具无效。多重检验纪律由根级跨模型 FWER 模板 (Romano-Wolf 逐步法) 承担, 词典臂参与其中作为同构念替代测量。_z 变体的识别角色是让系数可读为一个截面标准差语调变化对应的因变量变动, 并缓解 Algaba et al. (2020) 所述的衰减偏误在跨年方差漂移下的恶化。识别威胁的具体形态还需要按本测度的生成机制逐条对表。第一是反向因果: 银行的经营状况与金融科技投入本身会驱动媒体报道的语调, 语调回归结果变量时天然存在双向箭头; 项目层面的应对是 IV 扩展工具族 — 同组银行留一均值工具利用同业语调冲击的共同成分, 广义 Bartik 工具用银行对不同媒体来源的历史暴露份额乘来源层语调冲击构造外生变异, 媒体来源风格工具利用媒体机构写作风格的持久差异, 三类工具各配 just-identified 的两阶段最小二乘模板, 词典臂语调可作为其中的被工具变量或第一阶段观测。第二是遗漏变量: 银行年层面的规模, 业务结构与地区暴露同时影响报道语调与结果变量, 面板双向固定效应 (银行加年份) 吸收不随时间变的银行特质与共同年度冲击, 剩余识别变异来自银行内语调的逐年偏离。第三是测量误差本身的识别含义: 词典语调是潜在媒体评价的带噪测量, 经典测量误差使系数向零衰减, 因此词典臂显著本身是保守证据, 而词典臂与 LLM 臂系数量级的差异不能直接读作方法优劣 — 两臂的误差方差不同, 衰减程度不同, 只有符号与显著性模式的一致性才是可比结论。第四是选择性: 进入面板的文章宇宙由 stage 13 共现硬过滤与 full-only 留篇门控共同决定, "该银行当年是否被报道"与"报道语调如何"是两个耦合的过程, 零覆盖银行年记缺失的设计把选择问题显式留给使用者, 覆盖强度变量 (n_articles 及其对数族) 应作为控制或样本选择模型的一阶段变量与本家族联用。

【与相邻测度的构念区分】
第一, 与六个单词典族 (各词典名加 tone 后缀的系列列) 的区分: 本家族是它们的跨词典均值, 信息上是降噪聚合, 不是新构念; 单词典列保留供词典异质性分析。第二, 与 dict_avg_idf_tone 族的区分: 后者在词计分时引入逆文档频率加权 (罕见情感词权重更高), 属于另一个独立家族, 两者是计分权重维度的并排臂。第三, 与规则消融梯子 (dict_avg_negonly_tone 及 powerset 变体) 的区分: 那一族固定词典集合而变动语言学规则子集, 本家族恒在全规则口径下计算, 两梯子刻意正交不交叉。第四, 与 avg_msent 的区分: msent 是零规则的正负词裸计数极性, 与本家族 (全规则) 和 negonly (仅否定) 构成三点消融谱的两端。第五, 与 dict_avg_tone_sum 族的区分: sum 族聚合的是逐篇得分之和 (载荷随报道量放大), 本家族是均值 (纯强度不含数量); 数量信息由 n_articles 与 ln_news_coverage 单独承载。第六, 与 llm_models_avg_tone 及 bert_avg 系列的区分: 同为跨模型或跨词典综合, 但方法臂不同, 三臂各自 just-identified 并排, 禁混同一 Hansen J。第七, 与本家族内部的 _std 离散度三列的区分须再强调一次层级: 它们挂在同一家族名下但测的是二阶矩构念 (组内报道分歧), 与一阶矩语调水平列不是稳健性替代关系而是互补构念, 可以同时入模, 这一点与家族内其余全部变体 (轨, 权重, z) 的"并排互斥"关系性质不同。第八, 与媒体分组语调族 (官方对市场化媒体, 及其语调缺口列) 的区分: 分组族按媒体身份切分样本后分别聚合, 回答"谁在说时语调如何"; 本家族的 mw 变体则把媒体身份压缩为连续权重进入同一均值, 回答"按权威计权后总体语调如何", 前者保留身份维度供交互分析, 后者是单指标稳健臂, 两族同源不同构。第九, 与 fintech_intensity 及注意力族 (attention_pct 等) 的区分: 那些列度量报道内容里金融科技的强度与银行获得的注意力份额, 是"说了多少与说得多专", 本家族是"说得多正面", 极性与强度在构念上正交, 回归中常联用但绝不互为替代。

【已知局限与稳健性梯子】
词典法的固有局限必须如实披露: 其一, 上下文盲区 — 词典无法识别反讽, 引语与假设语气, 语言学规则只能回收局部语法信息 (Taboada et al. (2011) 的规则上限讨论); 其二, 词表覆盖 — 六部词典的编纂年代不一, 对 2020 年代新兴金融科技语汇的覆盖存在代际衰减, CN-FSD 类新词典 (Ma et al. (2025)) 的出现本身就是覆盖缺口的证据, 跨词典平均缓解但不能消除该问题; 其三, 分词依赖 — jieba 词典冻结保证确定性但也冻结了分词错误; 其四, 规则消融审计发现各消融变体高度共线 (MATH-1 披露: 规则贡献非可加, 只报相关不做分解)。对应的稳健性梯子有六层: 六单词典逐一替换; 规则 powerset 消融 (独立家族); du_2022 政治词权重三点梯子 (独立家族); 三轨文本口径 (full, ctx, ss); 四种聚合权重 (等权, vw, mw, hw); 年度截面标准化前后。全部梯子臂互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 梯子之间刻意不做交叉展开以避免列爆炸。零新闻覆盖的银行年在全家族记缺失而非零, _z 变体额外把标准化域限制在有覆盖行, 避免把"没被报道"错读成"被中性报道"。最后是效度证据的定位: 词典臂与 LLM 臂, BERT 臂及人工盲标的相互一致性由独立的验证阶段度量 (跨方法一致性系数与人工标注对照), 本家族列自身不内嵌效度统计; 使用者若需要报告词典法与金标准的一致性, 应引用验证阶段产物而非从面板列反推。词典得分对文本长度也有已知的机械依赖 — 长文命中词多, 归一化虽然消除了量纲但短文本得分的粒度更粗, 三轨设计天然内嵌了这一长度梯度 (全文最长, 实体窗次之, 同句窗最短), 跨轨系数比较时应意识到轨道差异同时混合了关联纯度与文本长度两个因素, 文章长度控制变量族可在回归中显式吸收后者。还有一条中国场景特有的局限须写明: 媒体语调不是自然生成的中性信号, 中国财经媒体的报道激励受权属结构与广告关系影响 (You et al. (2018) 对笔杆子俘获的系统证据), 词典法忠实测量的是"报道呈现出的语调"而非"客观事实应得的语调", 当银行与媒体存在商业或行政关联时语调本身可能被管理; 这不是测量误差而是构念的一部分, 研究设计上应通过媒体分组语调族与 mw 权威加权臂的对照, 以及媒体来源风格工具变量, 把被管理的语调成分与信息性语调成分分离, 而不是指望换一部词典能解决。最后补一条工程层面的确定性声明: 词典臂全链条无任何随机源 — jieba 版本冻结, 词表以 tone_dicts.json 落盘为准, 计分与聚合均为确定性算术, 任何机器任何时间重跑字节级一致, 这使本家族成为整个情感测度体系里复现性最强的一臂, 也是三方法三角中作为审计基准臂的资格来源。

## VAR: dict_avg_tone_app_ctx

【变体差分】
本列是应用场景条件子样本乘 ctx 轨的交叉格: 只对被 LLM 分类为"应用场景"类创新报道的文章计算词典语调, 且情感得分取自 ctx 轨文本。分类判据来自 stage 21 的 innovation_locus 维度 (Gomber 框架下的创新落点分类, P4 论文的核心维度), 且分组标签固定用 full 轨分类列 (innovation_locus_full): 即"哪些文章算应用场景类"由全文口径的分类决定, 而"这些文章的语调是多少"用 ctx 轨 (标题加实体窗口文本) 的词典得分度量。这一不对称是刻意设计: 分类需要全文语境才可靠, 情感则允许按文本窗口收紧做稳健性。计算上, encode 的分类聚合分支先把银行年内应用场景类文章取子集, 对六部词典各算子集内逐篇得分的等权均值 (仅 mean, 不产 sum 与 std), geography 步骤 7 再做跨词典平均。与家族 canonical (dict_avg_tone_full) 的差分因此有两重: 样本域从全部留存文章收窄到应用场景类子集, 文本域从全文收窄到实体上下文窗口。该列无对应 _z 变体 (分类条件列不在步骤 7b 标准化白名单)。当银行年内无应用场景类文章时该列记缺失, 分类计数列 n_articles_app 记零。使用时注意子样本均值在类内篇数很小时噪声极大, 姊妹测度 tone_gap_tech_app 对此设了两类各至少五篇的门槛, 本列自身不设门槛, 由使用者自行按 n_articles_app 过滤。ctx 轨与 full, ss 轨互为稳健性不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: dict_avg_tone_app_full

【变体差分】
本列是应用场景条件子样本的 full 轨词典语调, 是 app 条件族里与家族 canonical 文本口径一致的一格: 情感得分取自 full 轨 (标题 prepend 加全文正文) 的六词典得分, 样本域收窄到 stage 21 innovation_locus_full 分类为"应用场景"的文章子集。构念上它回答的问题是: 当媒体报道该银行的金融科技创新落在应用与场景层面 (支付产品, 手机银行, 场景获客等) 时, 报道的词典语调如何。与不加条件的 dict_avg_tone_full 的差分只有样本域一重: 分子分母都只数应用场景类文章。它与孪生列 dict_avg_tone_tech_full 构成 P4 创新落点异质性分析的一对条件均值, 两者之差的门槛化版本单独物化为 tone_gap_tech_app (LLM 口径), 而本列提供的是同一异质性切面的词典法平行测度 — 若 LLM 分类语调差与词典条件语调差同向, 则落点异质性结论对情感测量方法稳健。聚合链与家族基准一致: encode 分类聚合分支逐词典求子集均值, geography 跨词典等权平均, _safe_mean 对缺列优雅返回缺失。留篇门控为 full-only 口径, 分类标签轨与情感轨在本列恰好重合 (均为 full), 是三格 app 条件列中语义最干净的解读锚。无 _z 变体, 无加权变体 (条件子样本只做等权均值)。类内篇数小时慎用, 建议按 n_articles_app 设最小篇数过滤; 与 tech 条件列及三轨其余格互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_app_ss

【变体差分】
本列是应用场景条件子样本乘 ss 轨的交叉格: 样本域为 innovation_locus_full 分类为"应用场景"的文章, 情感文本域为 ss 轨 — 标题加"目标银行与金融科技词出现在同一句及其前后一句窗口"的最紧文本口径 (句窗半径由 config 的 ss_sentence_radius 控制, 默认一句)。ss 轨的回退语义必须按项目公理复述: 当一篇文章不存在银行与金科词同句共现时, content_ss 回退为全文正文且 ss_is_fallback 标记为真, 与 ctx 轨镜像, 共享同一 n_articles 分母; 因此本列在回退占比高的银行年上语义趋近 app_full, 解读时应连同回退率一起看。与家族 canonical 的差分为两重: 样本域收窄到应用场景类, 文本域收窄到同句共现窗。ss 轨的构念价值是把语调测量钉死在"银行与金融科技被同一句话谈论"的最强关联文本上, 最大限度剔除同篇文章里与目标银行无关段落的情感污染, 代价是文本极短时词典命中稀疏, 得分方差放大。分类标签仍来自 full 轨 (分类需要全文语境), 情感来自 ss 窗, 与 app_ctx 列的设计不对称同构。无 _z 变体与加权变体。在 ctx 与 ss 源列未落盘的环境下, _safe_mean 优雅返回缺失不崩。三轨与 tech/app 条件维度的所有格子互为稳健性不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J 做联合检验。

## VAR: dict_avg_tone_ctx

【变体差分】
本列是家族基准测度的 ctx 轨: 六词典跨词典等权语调, 文本域为 content_ctx — 标题 prepend 加目标银行实体提及位置周边的窗口文本, 由 stage 14 物化。构念动机是压制全文轨的"篇内混杂": 一篇长新闻可能只有两段谈目标银行, 其余篇幅谈行业或其他机构, 全文词典计分会把无关段落的情感记在目标银行头上; ctx 轨把计分域收缩到实体邻域, 换取更高的"语调对准银行"信噪比, 代价是丢失篇章级语境与更短的文本。与 canonical 列 dict_avg_tone_full 的唯一差分是文本轨: 样本域完全相同 (留篇门控为 full-only 口径, ctx 是 conditional-on-full 测度轨, 行宇宙为 full 留篇集的子集, 不独立决定哪篇文章入样)。计算链逐轨平行: stage 22 对 content_ctx 逐词典计分 (全语言学规则: 否定翻转, 程度副词, 转折加权; du_2022 政治正面词按零点五权重), encode 做银行年等权均值, geography 步骤 7 跨六词典平均。历史上 P1 论文主轨曾用 ctx, 2026 年 6 月底切换为 full 后 ctx 降为首要稳健性轨, 本列的当前身份即词典臂的 ctx 稳健测度。配套 _z 变体见 dict_avg_tone_ctx_z; 加权变体 (vw, mw, hw) 与离散度及分类条件变体各有独立的 ctx 格。full, ctx, ss 三轨互为稳健性不分主次, 各自 just-identified 并排进各自的回归, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_ctx_z

【变体差分】
本列是 dict_avg_tone_ctx 的年度截面标准化版本, 由 geography 步骤 7b standardize_panel_variables 生成。变换规则: 在每个年度截面内, 仅取当年有新闻覆盖 (n_articles 大于零) 的银行行, 减去截面均值再除以截面标准差, 得到组内均值为零方差为一的 z 值; 零覆盖行保持缺失; 整列有效观测 (合并全部年份) 不足十个时步骤 7b 不生成该 _z 列以防病态标准化, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化 (列仍存在); 原始列 dict_avg_tone_ctx 原样保留, _z 是增列不是替换。构念动机有二: 其一, 使回归系数可直接读为"ctx 轨词典语调一个截面标准差的变化对应因变量 β 个单位的变动", 便于与其他情感测度的系数做同尺度比较 (不同词典与方法的原始方差不同, 生系数不可比); 其二, 媒体语调的截面离散度逐年漂移 (报道总量, 词汇风尚, 词典覆盖衰减都随年份变), 按年标准化吸收了这一漂移, 缓解情感测量噪声带来的系数向零衰减问题 (Algaba et al. (2020) 综述的衰减偏误脉络)。方法学传统上承金融实证的逐年截面回归对变量可比性的要求。与母列的差分仅此一重线性变换, 不改变样本域与文本轨; 与母列在同一回归里只能二选一, 与其他轨其他权重的 _z 列互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_full

【变体差分】
本列是 F190 家族的 canonical 旗舰列与 core 列: 六部中文金融情感词典在 full 轨 (标题 prepend 加全文正文) 上的银行年语调跨词典等权均值, 是整个词典法方法臂在面板中的单点代表。它在三个层级上都是"基准格": 文本轨层级取 full (2026-06-29 全项目主轨从 ctx 切换为 full 后的权威口径, 留篇门控 full-only — 一篇文章是否计入银行金融科技报道宇宙, 只看 full 轨 LLM 验证标志); 聚合权重层级取等权 (每篇留存文章一票, 不做提及密度, 媒体权威或跟风衰减加权); 词典层级取跨六词典平均 (jiang_2021, yao_2021, bian_2021, du_2022, you_2018, loughran 中文主译各贡献一个银行年语调, 六值等权平均, 缺列由 _safe_mean 优雅置缺失)。计算链完整展开为四步: 第一步 stage 14 物化 content_full; 第二步 stage 22 对每篇文章逐词典计分, 公式为全部命中词最终得分之和除以最终得分绝对值之和, 最终得分等于词典基础极性乘程度副词乘子乘否定翻转乘转折乘子 (Taboada et al. (2011) 的词典加规则范式), du_2022 的政治正面词按零点五权重计入 (Du et al. (2022) 的政治词弱信号发现, 该权重另有梯子在独立家族); 第三步 encode 的 aggregate_panel 把银行年内全部留存文章的逐篇得分做等权均值, 得到六个单词典列; 第四步 geography 步骤 7 跨词典平均成本列。它的识别角色必须写准: 它不是 P1 的 treatment 主轨 (那是 llm_vote_tone_full), 而是三方法三角 (LLM, 词典, BERT) 中词典臂的旗舰, 与 llm_vote_tone_full 和 bert 综合列互为跨方法稳健性 — 词典法的价值在于零边际成本, 完全透明, 字节级可复现, 与 LLM 的黑箱性和 BERT 的训练依赖形成证据互补 (Frankel et al. (2022) 与 van Atteveldt (2021) 的方法比较传统)。与相邻列的边界: 六个单词典 full 列是它的分量; dict_avg_idf_tone_full 是 IDF 计分权重的并排臂; dict_avg_negonly_tone_full 与消融 powerset 是语言学规则维度的梯子; avg_msent_full 是零规则计数极性端点; dict_avg_tone_sum_full 载入报道量信息而本列是纯强度均值。所有这些臂连同三轨, 四权重, 三方法, 全部互为稳健性不分主次, 各自 just-identified 并排, 严禁把任意组合混进同一 over-identified Hansen J; 跨测度的多重检验纪律走根级 Romano-Wolf FWER 模板。与它最容易混淆的近邻是 llm_models_avg_tone_full (跨三家 LLM 的均值综合) 与 bert 三分类模型综合列: 三者都是"跨模型或跨词典的方法内综合", 结构同构但方法臂不同, 在稳健性表中应作为三行并排呈现而非互相替换。等权设计的两个层次值得分开辩护: 篇级等权意味着每篇留存报道对银行年语调贡献相同, 这是最中性的先验, 其全部替代方案 (提及密度, 媒体权威, 跟风衰减) 都已物化为本家族的 vw, mw, hw 变体供并排检验; 词典级等权则意味着六部词典地位平等, 不按词表规模或发表期刊加权 — 任何数据驱动的词典加权都会引入样本内过拟合, 而六个单词典列的逐一替换回归已经提供了比加权更透明的词典敏感性证据。缺失传播语义: 六个单词典列中任何一列缺失时 _safe_mean 用其余列继续平均 (而非整列置缺), 只有六列全缺才记缺失, 这保证了词典层面的局部数据问题不放大为家族列的整体缺口。局限与母家族共享: 上下文盲区, 词表代际覆盖衰减, jieba 冻结分词误差; 解读时零覆盖银行年为缺失而非零, 配套年度截面标准化列为 dict_avg_tone_full_z。

## VAR: dict_avg_tone_full_z

【变体差分】
本列是 core 列 dict_avg_tone_full 的年度截面标准化孪生, 由步骤 7b 按标准化白名单生成。变换域与规则: 每个年度截面内只取有新闻覆盖 (n_articles 大于零) 的银行, 减截面均值除截面标准差; 零覆盖行保持缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化; 原始列不动, 本列为新增。它是词典臂进入标准化回归组的入口列: 当研究设计要求把 LLM, 词典, BERT 三方法臂的系数放在同一张表里按"一个标准差语调变化"的口径比较时 (跨方法的原始方差差异会让生系数比较失真, 与跨模型表 A5 须 z 标准化同理), 词典臂应换用本列。方法学锚为金融实证逐年截面回归的可比性传统; 经济动机是媒体语调截面离散度的年际漂移 — 样本期横跨中国金融科技叙事从萌芽到监管收紧的完整周期, 不同年份"语调偏正一个单位"的稀有程度完全不同, 按年标准化把系数解释锚定在当年同业相对位置上, 这与银行年面板配年份固定效应的识别逻辑同构但作用在测度侧。与母列差分仅一重线性变换, 样本域文本轨聚合权重全部继承; 二者在同一回归只能取一, 分别对应"语调水平效应"与"语调相对位置效应"两种解读。与其他 _z 列 (三轨乘四权重共十二个标准化格) 互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_hw_ctx

【变体差分】
本列是跟风衰减加权 (hw) 乘 ctx 轨的词典语调: 银行年内每篇文章的 ctx 轨词典得分不再等权, 而是按 stage 24 herd_decay_processor 生成的跟风衰减权重加权平均 — 同一银行短时间窗内重复跟进的报道权重按时间衰减折扣, 首发与独立报道权重高, 蹭热点的复读报道权重低。构念动机: 媒体报道存在显著的跟风羊群现象, 一条负面新闻引发几十篇改写转载, 等权均值会把同一信息事件重复计数几十次; 衰减加权把测度拉回"独立信息事件的语调", 与新闻情感持续性和陈旧信息文献的关切一致 (Aksoy-Yurdagul et al. (2026) 论新闻情感的持续性, Heston 和 Sinha (2017) 论新旧新闻的信息含量差异)。计算: encode 内逐词典求权重乘得分之和除以权重之和, 分母自 v3.6.0 起逐轨独立 (ctx 用 sum_herd_weight_ctx, 修正了旧版全文权重和错配多轨的度量处理不匹配), 词典族分母为全物理域权重和 (词典得分零而非缺失, 不套 LLM 族的 valid-mask 修正); geography 步骤 7 再跨六词典平均。与家族 canonical 的差分为两重: 聚合权重从等权换为跟风衰减, 文本轨从 full 换为 ctx。衰减阈值另有敏感性变体族 (LLM 列族内), 词典 hw 族固定生产阈值。配套标准化列为 dict_avg_tone_hw_ctx_z。四权重三轨各格互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_hw_ctx_z

【变体差分】
本列是 dict_avg_tone_hw_ctx 的年度截面标准化版本: 跟风衰减加权乘 ctx 轨乘 z 变换的三维交叉格。变换规则与家族其他 _z 列完全一致 — 步骤 7b 在每个年度截面内, 仅对有新闻覆盖的银行行减截面均值除截面标准差, 零覆盖行保持缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 原始列保留。hw 加权列做截面标准化有一个额外的口径理由: 跟风衰减权重的绝对水平依赖当年的报道密度与跟风节奏 (报道越密集, 衰减折扣的作用越强), 因此 hw 语调的原始方差年际漂移比等权列更明显, 按年标准化后的相对位置解读更稳。本列的典型用途是稳健性表格: 当主表用 dict_avg_tone_full_z (等权 full 轨标准化) 时, 本列提供"换聚合权重且换文本轨后结论是否翻转"的双重偏离检验格。与母列 dict_avg_tone_hw_ctx 的差分仅一重线性变换; 与家族内其余十一个 _z 格 (基准与 vw, mw, hw 三权重乘三轨) 互为稳健性不分主次, 各自 just-identified 并排进各自回归, 严禁与母列或任何姊妹列混进同一 over-identified Hansen J 做联合过度识别检验。解读系数时口径为: ctx 轨跟风衰减加权词典语调在当年截面内每偏离同业一个标准差, 因变量变动 β 个单位。

## VAR: dict_avg_tone_hw_full

【变体差分】
本列是跟风衰减加权的 full 轨词典语调, 是 hw 权重族中与家族 canonical 文本口径一致的基准格: 文本域取 content_full (标题 prepend 加全文), 与 dict_avg_tone_full 的唯一差分是把银行年内的逐篇等权均值换成 stage 24 跟风衰减权重的加权均值。权重的生成逻辑: herd_decay_processor 对每篇文章检测其相对同银行前序报道的跟风程度, 短窗口内的重复跟进按时间衰减折扣, 使权重向首发与独立报道集中; 公式为权重乘得分之和除以权重之和, full 轨分母为 sum_herd_weight_full (v3.6.0 起逐轨独立分母), 词典族用全物理域分母不套有效行掩码 (词典逐篇必有数值得分, 分子分母天然同域, 这与 LLM 族的 valid-mask 分母是刻意不对称, 详见家族核心节)。构念上本列回答: 剔除媒体羊群式重复报道的放大效应后, 该银行当年金融科技报道的独立信息事件语调是多少。它与等权基准列的差值本身有信息含量 — 若某银行年 hw 语调显著低于等权语调, 说明负面语调集中在首发独立报道而正面语调多为跟风复读, 反之亦然。方法学脉络: 新闻情感持续性与陈旧信息折价 (Aksoy-Yurdagul et al. (2026), Heston 和 Sinha (2017))。geography 步骤 7 跨六词典等权平均收口。配套标准化列 dict_avg_tone_hw_full_z。与等权, vw, mw 权重臂及三轨互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_hw_full_z

【变体差分】
本列是 dict_avg_tone_hw_full 的年度截面标准化孪生: 在跟风衰减加权 full 轨语调的基础上, 由步骤 7b 逐年度截面减均值除标准差, 标准化域限于当年有新闻覆盖的银行行, 零覆盖行缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 母列保留不动。作为 hw 权重族在 full 轨上的标准化格, 它在稳健性矩阵中的位置是"主文本轨加替代聚合权重加截面可比化": 与主标准化列 dict_avg_tone_full_z 相比只偏离权重一个维度, 是检验"结论是否被媒体跟风报道的重复计数驱动"的最干净标准化对照 — 若等权 z 列显著而本列不显著, 提示效应主要来自跟风放大的报道浪而非独立信息事件; 若两者同向同量级, 则语调效应对报道羊群结构稳健。截面标准化对 hw 列尤为必要: 跟风衰减权重的分布随当年报道生态变化 (热点年份跟风链条长, 衰减折扣重), hw 语调的原始尺度跨年可比性弱于等权列, z 变换把它拉回逐年同业相对位置的统一标尺。与母列在同一回归二选一; 与家族内其余 _z 格及原始格互为稳健性不分主次, 各自 just-identified 并排, 严禁任意组合混进同一 over-identified Hansen J。系数解读口径: full 轨跟风衰减加权词典语调在当年截面内相对同业每高一个标准差, 因变量变动 β 单位。

## VAR: dict_avg_tone_hw_ss

【变体差分】
本列是跟风衰减加权乘 ss 轨的词典语调: 情感文本域为 content_ss (标题加银行与金科词同句共现窗, 句窗半径默认一句), 聚合权重为 stage 24 跟风衰减权重, 分母为 ss 轨独立的 sum_herd_weight_ss。ss 轨回退公理必须复述: 无银行金科同句共现的文章, content_ss 回退为全文正文且 ss_is_fallback 置真 (镜像 ctx 回退语义, 共享 n_articles 分母), 故回退率高的银行年本列语义向 hw_full 收敛。与家族 canonical 的差分为两重: 文本域收窄到最强关联的同句窗口, 聚合权重换为跟风衰减。两重收紧叠加使本列成为家族内"信息纯度"取向最激进的格子之一 — 既要求语调文本与银行金科关联最紧, 又折扣重复跟进报道; 相应代价是双重的样本与方差压力: ss 短文本词典命中稀疏, hw 权重又把有效样本向少数首发报道集中。实现守卫: sum_herd_weight_ss 缺失时 (stage 24 未跑同句轨) 分母兜底为缺失, 本列整列优雅置缺失不崩, 不影响 full 与 ctx 格; geography 跨词典平均的 _safe_mean 同样缺列容错。配套标准化列 dict_avg_tone_hw_ss_z。报告本列时应连同 ss 回退率与银行年篇数一起呈现, 便于读者判断其偏离 hw_full 的真实幅度。三轨与四权重的所有交叉格互为稳健性不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; ss 轨与 full, ctx 轨绝不进同一 RHS。

## VAR: dict_avg_tone_hw_ss_z

【变体差分】
本列是 dict_avg_tone_hw_ss 的年度截面标准化版本, 家族 z 族中偏离基准维度最多的格子: 文本轨 (ss), 聚合权重 (hw), 尺度 (z) 三个维度全部偏离 canonical。变换规则与族内一致: 步骤 7b 逐年截面对有新闻覆盖行减均值除标准差, 零覆盖行缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 母列保留。在稳健性谱系上, 本列是词典臂"最大偏离仍同向"论证的端点格之一: 若从 dict_avg_tone_full_z 一路换轨换权重到本列, 系数符号与显著性保持稳定, 则词典语调效应对文本窗口口径与报道羊群结构的联合扰动稳健; 若在某一格翻转, 翻转发生的维度本身就是机制线索 (是同句窗口剔除的篇章语境在驱动, 还是跟风报道的重复计数在驱动)。ss 轨的回退语义与 hw 的 ss 独立分母守卫全部继承自母列: 回退率高时语义向 hw_full_z 收敛, sum_herd_weight_ss 缺失时整列缺失。T=2 开发环境下 ss 轨样本极薄, 整列有效观测 (合并全部年份) 常不足十个, 本列可能不被步骤 7b 生成 (整列跳过), 属预期守卫行为而非缺陷; 生产 T=19 面板下正常出值。与母列在同一回归二选一; 与家族内其余原始格和 z 格互为稳健性不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: dict_avg_tone_mw_ctx

【变体差分】
本列是媒体权威性加权 (mw) 乘 ctx 轨的词典语调: 银行年内每篇文章的 ctx 轨词典得分按其发布媒体的权威性权重加权平均, 权重高的全国性权威财经媒体报道对银行年语调的贡献大于地方小报与边缘媒体。构念锚是 Holzman et al. (2023): 媒体情感对市场的作用强度随媒体权威分层, 权威媒体的语调更能移动预期; 中国场景下媒体身份的异质性更突出 (官方媒体与市场化媒体的报道激励结构性不同, You et al. (2018) 论中国财经媒体的笔杆子俘获), 权威加权是对"每篇报道一票"这一等权假设的直接替代检验。计算: encode 内逐词典求权重乘得分之和除以媒体权威权重总和 sum_media_authority_weight (权重是文章级属性, 不随文本轨变, 故 mw 分母跨轨共用; 分子逐轨取 ctx 源列), 词典族用全物理域分母不套掩码; geography 跨六词典平均。与家族 canonical 的差分两重: 权重从等权换为媒体权威, 文本轨从 full 换为 ctx。与 vw (提及密度加权, 权重来自文章与银行的关联强度) 和 hw (跟风衰减, 权重来自报道的时序独立性) 相比, mw 的权重来自信息源的可信度维度, 三种权重臂刻意覆盖三个正交的加权动机。配套标准化列 dict_avg_tone_mw_ctx_z。各权重各轨互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_mw_ctx_z

【变体差分】
本列是 dict_avg_tone_mw_ctx 的年度截面标准化版本: 媒体权威加权乘 ctx 轨乘 z 变换。步骤 7b 的统一规则全部适用: 逐年度截面, 仅对当年有新闻覆盖的银行减截面均值除截面标准差, 零覆盖行保持缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 原始列保留为水平口径。mw 列做截面标准化的特有动机: 媒体权威权重的分布本身随媒体生态演变 — 样本期内中国财经媒体经历了纸媒衰退与新媒体崛起, 高权威媒体在语料中的占比逐年变化, 使 mw 语调的原始截面方差存在结构性年际漂移, z 变换把这一漂移吸收进标准化常数, 让系数稳定解读为"当年截面内权威加权语调相对同业一个标准差的差异"。在稳健性矩阵中本列与 dict_avg_tone_ctx_z 构成同轨换权重的对照对 (等权对权威加权, 均在 ctx 轨标准化口径下), 用于检验 ctx 轨语调效应是否被低权威媒体的噪声报道稀释或驱动 (Holzman et al. (2023) 的权威分层逻辑)。与母列在同一回归二选一; 与家族内其余 _z 格互为稳健性不分主次, 各自 just-identified 并排, 严禁与任何姊妹测度混进同一 over-identified Hansen J 做联合过度识别。

## VAR: dict_avg_tone_mw_full

【变体差分】
本列是媒体权威性加权的 full 轨词典语调, mw 权重族中与 canonical 文本口径一致的基准格: 文本域取全文轨, 与 dict_avg_tone_full 的唯一差分是把逐篇等权均值换成媒体权威权重的加权均值 (权重乘得分之和除以 sum_media_authority_weight)。构念上本列回答: 若只按信息源的权威性重新分配每篇报道的话语权, 该银行当年金融科技报道的语调是多少 — 它把"三家权威财经大报的深度负面报道"与"三十家地方媒体的通稿式正面转载"的天平从篇数多数倒向权威多数。方法学锚为 Holzman et al. (2023) 对媒体情感按权威分层的实证; 中国媒体制度语境的补充锚是 You et al. (2018) — 不同权属媒体的报道激励系统性不同, 权威加权同时隐含着对媒体身份构成的重加权, 解读时应意识到 mw 语调的变动可能来自语调本身或来自高低权威媒体报道构成比的变化, 后者由姊妹测度族 (官方对非官方, 市场化对非市场化媒体的分组语调与语调缺口列族) 单独刻画。实现细节: 权重为文章级属性跨轨共用分母, full 轨分子取全文轨得分加权和; 词典族全物理域分母, 不套 LLM 族的 valid-mask 修正; geography 步骤 7 跨六词典等权收口, _safe_mean 缺列容错。配套标准化列 dict_avg_tone_mw_full_z。与等权, vw, hw 权重臂互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_mw_full_z

【变体差分】
本列是 dict_avg_tone_mw_full 的年度截面标准化孪生: 媒体权威加权 full 轨语调经步骤 7b 逐年截面减均值除标准差, 标准化域限于当年有新闻覆盖的银行, 零覆盖行缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 母列保留。在标准化回归组里, 本列与主列 dict_avg_tone_full_z 构成 full 轨上"等权对权威加权"的最小偏离对照: 二者只差聚合权重一个维度, 若系数同向同量级, 则词典语调效应不依赖报道话语权的分配规则; 若权威加权显著更强, 与 Holzman et al. (2023) 的权威媒体情感更具约束力的发现同构, 本身即是机制证据。截面标准化的口径意义在 mw 族尤其实质: 媒体权威权重的年度总量与分布随媒体格局变迁 (纸媒占比萎缩, 权威源集中度变化), mw 语调的生值尺度年际可比性弱, z 变换后系数统一读为当年同业相对位置差一个标准差的效应, 与年份固定效应的组内识别逻辑对齐。使用纪律与族内一致: 与母列同一回归二选一 (水平效应对相对位置效应两种解读); 与家族内其余十一个 _z 格互为稳健性不分主次, 各自 just-identified 并排进各自回归, 严禁任意两个及以上混进同一 over-identified Hansen J 检验。

## VAR: dict_avg_tone_mw_ss

【变体差分】
本列是媒体权威性加权乘 ss 轨的词典语调: 情感文本域为银行与金科词同句共现窗 (content_ss, 句窗半径默认一句), 聚合权重为媒体权威性权重, 分母沿用跨轨共用的 sum_media_authority_weight (权重是文章级媒体属性, 不随文本窗口变), 分子取 ss 轨得分的权威加权和。ss 回退公理照常适用: 无同句共现的文章其 content_ss 回退为全文正文, ss_is_fallback 置真, 镜像 ctx 回退语义并共享 n_articles 分母; 回退率高的银行年本列语义向 mw_full 收敛, 解读须配合回退率。构念定位: 本列同时在两个维度上收紧"哪些情感算数"— 文本维度只数与银行金科关联最紧的句子, 信源维度按权威折价低可信度媒体; 它逼近的构念是"权威媒体在直接谈论该银行金融科技时的语调", 是词典臂里对信息质量要求最高的格子之一。与家族 canonical 差分两重 (轨与权重)。实现守卫: ss 源列未落盘时逐项 if 守卫优雅跳过, 不影响 full 与 ctx 格; geography 跨词典平均缺列容错。配套标准化列 dict_avg_tone_mw_ss_z。小样本银行年上权威权重向少数几篇报道集中, 有效自由度收缩, 使用时建议按篇数过滤。三轨四权重所有格互为稳健性不分主次, 各自 just-identified 并排, ss 与 full, ctx 绝不同 RHS, 严禁混进同一 over-identified Hansen J。

## VAR: dict_avg_tone_mw_ss_z

【变体差分】
本列是 dict_avg_tone_mw_ss 的年度截面标准化版本, 媒体权威加权乘同句共现轨乘 z 变换的三维交叉格。步骤 7b 统一规则: 逐年截面仅对有新闻覆盖行减均值除标准差, 零覆盖行缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 母列保留水平口径。本列在家族稳健性矩阵中的角色是 mw 权重臂的最紧文本口径标准化端点: 从 dict_avg_tone_full_z 出发, 换权重 (等权到权威) 与换轨 (全文到同句窗) 双偏离后若结论仍同向, 词典语调效应对"谁在说"与"在哪句说"两个口径同时稳健。ss 轨继承的两条语义须复述: 其一, 回退公理 — 无银行金科同句共现的文章回退为全文正文且共享分母, 回退率高时本列趋近 mw_full_z; 其二, 短文本稀疏 — 同句窗内词典命中少, 逐篇得分方差大, 加权聚合后仍偏噪, 截面标准化不消除这一噪声只统一其尺度。开发环境的小面板上 ss 轨整列有效观测 (合并全部年份) 常不足十, 本列可能不被步骤 7b 生成 (整列跳过), 属预期守卫行为而非数据缺陷; 生产规模面板下正常出值。与母列同一回归二选一 (水平口径与相对位置口径两种解读各取其一); 与家族其余格互为稳健性不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J 做联合检验。

## VAR: dict_avg_tone_ss

【变体差分】
本列是家族基准测度的 ss 轨: 六词典跨词典等权语调, 文本域为 content_ss — 标题加"目标银行与至少一个金融科技词出现在同一句及前后一句窗口内"的最紧文本口径, 由 stage 14 物化, 句窗半径由 config 过滤域的 ss_sentence_radius 键控制 (默认一句; 注意这与 stage 13 共现硬过滤的 sentence_radius 是两个不同的配置键, 前者管文本物化窗口, 后者管留篇判据)。构念动机是把语调测量钉死在银行与金融科技被同一句话直接关联的文本上, 彻底剔除同篇文章中谈其他银行或行业背景段落的情感污染, 是三轨中"语调归属"最无争议的口径。回退公理必须复述: 当一篇留存文章不存在银行金科同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置真, 与 ctx 轨回退语义镜像, 共享同一 n_articles 分母 — 因此本列不是"仅有同句共现文章的子样本均值", 而是"同句窗文本与回退全文的混合均值", 回退率高的银行年语义向 dict_avg_tone_full 收敛, 严谨使用须报告回退率。样本域与 full 轨完全一致 (留篇门控 full-only, ss 为 conditional-on-full 测度轨)。判定口径的不对称也须记录: 银行侧命中带否定与短名过滤, 金科侧为裸词表匹配。配套标准化列 dict_avg_tone_ss_z。三轨互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_ss_z

【变体差分】
本列是 dict_avg_tone_ss 的年度截面标准化版本: 等权 ss 轨词典语调经步骤 7b 逐年度截面减均值除标准差。标准化规则与族内统一: 仅对当年有新闻覆盖 (n_articles 大于零) 的银行行变换, 零覆盖行保持缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 母列保留。ss 轨标准化的特有意义: 同句共现窗文本极短, 词典命中稀疏导致逐篇得分呈重尾分布, 银行年均值的截面方差显著大于 full 轨且随当年语料的共现密度波动; z 变换把这一轨道特有的方差结构统一到逐年同业相对位置标尺上, 使 ss 轨系数能与 full, ctx 轨的标准化系数在同一张稳健性表里按标准差口径并排比较 — 这正是三轨稳健性论证的规范呈现方式 (各轨各自回归, 系数并排对照, 而非同一回归联合检验)。母列的回退公理全部继承: 无同句共现文章回退全文, 回退率高时本列趋近 dict_avg_tone_full_z。T=2 开发面板上 ss 轨整列有效观测 (合并全部年份) 常不足十, 本列可能不被步骤 7b 生成 (整列跳过), 属预期守卫行为; 生产规模下正常出值。与母列同一回归二选一; 与家族内其余 _z 格互为稳健性不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: dict_avg_tone_std_ctx

【变体差分】
本列不是语调水平而是语调离散度: ctx 轨上, 六部词典各自的银行年内逐篇得分标准差 (单词典 tone_std 的 ctx 轨列) 的跨词典等权均值。构念是"报道语调的组内分歧"— 同一银行同一年内, 不同报道对其金融科技的评价有多不一致: 低值表示媒体口径高度一致 (无论一致偏正还是偏负), 高值表示评价撕裂, 既有唱多也有唱空。语调离散度在金融文本文献中是独立于语调水平的信息量: 它是媒体分歧与叙事不确定性的代理, 与家族外的 fintech_exposure 复合指标 (覆盖强度乘语调波动) 及 bank_media_disagreement 论文线共享构念地基, Tetlock (2007) 之后的媒体情感文献也早已从一阶矩扩展到二阶矩。计算: encode 聚合时对每个词典的逐篇 ctx 轨得分在银行年格内求标准差, geography 步骤 7 把六个单词典 std 列做 _safe_mean 跨词典平均。与家族 canonical 的差分是统计矩本身 (标准差对均值) 加文本轨 (ctx 对 full)。单篇文章的银行年无法定义标准差, 该格记缺失; 篇数很小时标准差估计噪声大, 使用时建议按 n_articles 过滤。本列不在步骤 7b 标准化白名单, 无 _z 变体; 也无加权变体 (std 只做等权口径)。三轨 std 列互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; std 与同轨 tone 水平列测不同构念, 可同时入模但解释各异。

## VAR: dict_avg_tone_std_full

【变体差分】
本列是 full 轨的词典语调离散度: 六部词典各自在银行年格内的逐篇全文轨得分标准差, 跨六词典等权平均。它是 std 三格中与家族 canonical 文本口径一致的基准格, 与 dict_avg_tone_full 构成同源同轨的一阶矩与二阶矩配对: 前者说该银行当年被报道得偏正还是偏负, 本列说这些报道彼此之间有多不一致。构念价值有三层: 其一, 媒体分歧本身是信息环境变量 — 高分歧年份市场对该银行金融科技战略的信念更发散, 情感冲击的传导路径不同于共识年份; 其二, 它是语调水平测度的质量诊断 — 同样的均值零, 可能是"全部中性"也可能是"一半强正一半强负", 后者的均值解释力弱, 分析中把 std 作为调节变量或加权依据能显式处理这一异质性; 其三, 项目的叙事暴露复合指标用语调波动乘覆盖强度刻画银行的叙事风险暴露, 本列提供该构念在词典臂的平行实现 (复合指标本身用 LLM 轨波动)。计算链: stage 22 逐篇计分, encode 银行年 std 聚合 (与 mean, sum 并列的聚合算子), geography 跨词典 _safe_mean。单篇银行年记缺失, 小样本格标准差噪声大。无 _z 变体 (不在标准化白名单), 无 vw, mw, hw 加权版本。与 ctx, ss 轨 std 列互为稳健性不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: dict_avg_tone_std_ss

【变体差分】
本列是 ss 轨的词典语调离散度: 六部词典各自在银行年格内的逐篇同句共现窗得分标准差, 跨六词典等权平均。与 std_full 的差分是文本域收窄到银行金科同句共现窗 (含标题, 句窗半径默认一句), 构念收窄为"媒体在直接把该银行与金融科技绑定谈论的那些句子上, 评价有多分裂"。两条 ss 轨公理照常适用并影响解读: 其一, 回退语义 — 无同句共现的文章回退为全文正文计分且共享分母, 回退率高的银行年本列混入全文离散度, 语义向 std_full 收敛; 其二, 短文本稀疏 — 同句窗词典命中少, 逐篇得分本身呈粗粒化重尾分布 (少数命中词就决定整篇得分), 其组内标准差因此系统性偏大且对篇数敏感, 本列跨银行比较时这部分是测量噪声而非真实分歧, 与 full 轨 std 的水平不可直接比, 只宜做组内相对比较或标准化系数比较。计算链与姊妹格一致: encode 逐词典 std 聚合, geography 跨词典 _safe_mean, ss 源列未落盘时优雅缺失。单篇银行年记缺失。无 _z 变体与加权变体。T=2 开发面板上 ss 轨样本薄, 本列大面积缺失属预期退化。三轨 std 列互为稳健性不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: dict_avg_tone_tech_ctx

【变体差分】
本列是底层技术条件子样本乘 ctx 轨的交叉格: 只对被 stage 21 LLM 分类为"底层技术"类创新报道的文章 (innovation_locus_full 标签, Gomber 框架的创新落点维度, 对应区块链, 云计算, 大数据风控等基础设施层创新叙事) 计算 ctx 轨词典语调。与 app_ctx 列构成条件均值对: 前者数应用与场景层创新报道的语调, 本列数底层技术层的, 两者共同支撑 P4 论文关于创新落点异质性的分析 — 媒体对银行"做底层技术"与"做应用场景"的评价基调是否系统性不同。设计上分类标签固定取 full 轨 (分类需要全文语境才可靠), 情感取 ctx 轨 (标题加实体窗口), 分类与情感的轨道不对称与 app_ctx 完全镜像。计算: encode 分类聚合分支取 innovation_locus_full 等于底层技术的文章子集, 逐词典求子集内 ctx 轨得分等权均值 (仅 mean, 无 sum, std, 加权), geography 跨六词典平均; 银行年内无底层技术类文章时记缺失且 n_articles_tech 记零。无 _z 变体。底层技术类报道在多数银行的语料中占比低于应用场景类, 本列的小样本噪声问题更突出, 使用时按 n_articles_tech 过滤; 配套的 LLM 口径缺口测度 tone_gap_tech_app 设了两类各五篇的门槛可作参照。条件维度与三轨各格互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_tech_full

【变体差分】
本列是底层技术条件子样本的 full 轨词典语调: 样本域收窄到 innovation_locus_full 分类为"底层技术"的报道, 情感取全文轨六词典得分的子集等权均值再跨词典平均。它是 tech 条件族中分类轨与情感轨重合 (均为 full) 的最干净格子, 构念直读为: 当媒体报道该银行的金融科技创新落在底层技术层 (自研核心系统, 区块链平台, 数据基础设施等) 时, 报道的词典语调水平。与孪生列 dict_avg_tone_app_full 的对照是 P4 创新落点异质性的词典法证据: 理论预期上底层技术叙事更常与"投入大, 周期长, 前景不确定"的评价词共现, 应用场景叙事更常与"用户增长, 便捷, 普惠"共现, 两列之差捕捉媒体对两类创新路线的系统性评价差; LLM 口径的同构差已门槛化物化为 tone_gap_tech_app, 本列与 app_full 提供其词典臂平行测度, 两方法同向则异质性结论对情感测量技术稳健。计算链: encode 分类聚合 (子集逐词典 mean), geography 跨词典 _safe_mean 收口; 无底层技术类文章的银行年记缺失。无 _z 变体与加权变体。类内篇数普遍偏小, 按 n_articles_tech 过滤后使用。与 app 条件列, 三轨其余格及 LLM, BERT 方法臂的同构条件列互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_tech_ss

【变体差分】
本列是底层技术条件子样本乘 ss 轨的交叉格: 样本域为 innovation_locus_full 分类为"底层技术"的文章, 情感文本域为银行金科同句共现窗 (content_ss, 含标题, 句窗半径默认一句)。它是 tech 条件族的最紧文本口径: 构念逼近"媒体在同一句话里把该银行与金融科技直接绑定, 且整篇属于底层技术叙事时的评价基调"。两条 ss 公理继续适用: 无同句共现的文章回退为全文正文计分, ss_is_fallback 置真, 镜像 ctx 回退语义共享分母, 回退率高时本列语义向 tech_full 收敛; 同句窗短文本词典命中稀疏, 逐篇得分粗粒化, 子样本条件均值的噪声进一步放大。本列的样本压力是家族内最大的三重叠加: 底层技术类报道本就占比小, 同句共现进一步筛紧文本, 词典命中再打折扣, 因此它在开发面板上大面积缺失属预期, 在生产面板上也应视为"方向性稳健参考格"而非主证据格, 报告时务必连同 n_articles_tech 与 ss 回退率一起呈现。计算链与守卫: encode 分类聚合分支逐词典求子集 ss 轨均值, ss 源列缺失时逐项守卫优雅跳过, geography 跨词典 _safe_mean 缺列容错。无 _z 变体与加权变体。与 app_ss 及条件族, 三轨各格互为稳健性不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: dict_avg_tone_vw_ctx

【变体差分】
本列是提及密度加权 (vw) 乘 ctx 轨的词典语调: 银行年内每篇文章的 ctx 轨词典得分按该文对目标银行的提及密度加权平均 — 通篇聚焦该银行的深度报道权重高, 只在名单式罗列中捎带提及的文章权重低。权重设计承袭 Hassan et al. (2019) 的思想: 用与主题相关的文本占比刻画暴露与关注强度, 一篇文章"多大程度上是关于这家银行的"应当决定其语调对银行年测度的话语权。计算: encode 内逐词典求提及密度乘得分之和除以密度总和 sum_mention_density (密度为文章级属性, 分母跨轨共用; 分子取 ctx 轨得分加权和), 词典族用全物理域分母 (词典逐篇必有数值得分, 不套 LLM 族 valid-mask 修正); geography 步骤 7 跨六词典等权平均。与家族 canonical 的差分两重: 权重从等权换为提及密度, 文本轨从 full 换为 ctx。注意 vw 与 ctx 的组合存在轻微的构念重叠: ctx 轨已在文本侧收紧到实体邻域, vw 再在权重侧强调高提及文章, 两者都指向"语调更归属于该银行", 本列因此是归属取向的双重加强格, 与等权 full 格的对照最能暴露归属噪声的影响方向。配套标准化列 dict_avg_tone_vw_ctx_z。三权重臂与三轨互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_vw_ctx_z

【变体差分】
本列是 dict_avg_tone_vw_ctx 的年度截面标准化版本: 提及密度加权乘 ctx 轨乘 z 变换的交叉格。步骤 7b 统一规则适用: 逐年度截面仅对当年有新闻覆盖 (n_articles 大于零) 的银行减截面均值除截面标准差, 零覆盖行保持缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 母列保留水平口径。vw 列截面标准化的特有动机: 提及密度的分布随报道生态漂移 — 名单式行业盘点文与单银行深度报道的构成比逐年变化, 直接影响 vw 语调的有效权重集中度与截面方差, z 变换把该结构性漂移吸收后, 系数统一解读为"当年截面内提及密度加权语调相对同业一个标准差的差异"。在稳健性矩阵中, 本列与 dict_avg_tone_ctx_z 构成 ctx 轨上"等权对密度加权"的最小偏离对照, 检验 ctx 轨语调效应是否被低关联度文章的噪声语调稀释; 与 dict_avg_tone_vw_full_z 构成 vw 权重下"全文对实体窗口"的换轨对照。母列的样本域, 文本轨与权重结构全部继承, 差分仅一重线性变换。使用纪律: 与母列同一回归二选一; 与家族内其余原始格与 _z 格互为稳健性不分主次, 各自 just-identified 并排进各自回归, 严禁任意组合混进同一 over-identified Hansen J 做联合过度识别检验。

## VAR: dict_avg_tone_vw_full

【变体差分】
本列是提及密度加权的 full 轨词典语调, vw 权重族中与家族 canonical 文本口径一致的基准格: 与 dict_avg_tone_full 的唯一差分是把银行年内逐篇等权均值换成按目标银行提及密度加权的均值。权重逻辑: 每篇文章对目标银行的提及密度 (银行在文中被提及的密集程度) 决定该篇语调的话语权, 深度聚焦报道压过顺带提及; 方法学思想源自 Hassan et al. (2019) 用主题相关文本份额度量企业级暴露的范式, 迁移到媒体语调聚合即"报道越是关于这家银行, 其语调越该算数"。公式为密度乘得分之和除以 sum_mention_density; 词典族分母为全物理域密度和, 不套 LLM 族的有效行掩码 (词典逐篇必有得分, 分子分母天然同域, 套掩码反成过度修正 — 这一不对称是审计确认的刻意设计)。构念上本列与等权基准的差值反映"高关联报道与低关联报道的语调差": 若某银行年 vw 语调显著高于等权语调, 说明深度报道比顺带提及更正面, 这类结构信息本身可作机制分析素材。geography 步骤 7 跨六词典等权平均收口, _safe_mean 缺列容错。配套标准化列 dict_avg_tone_vw_full_z。与等权, mw, hw 权重臂及三轨各格互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: dict_avg_tone_vw_full_z

【变体差分】
本列是 dict_avg_tone_vw_full 的年度截面标准化孪生: 提及密度加权 full 轨语调经步骤 7b 逐年截面减均值除标准差, 标准化域限于当年有新闻覆盖的银行行, 零覆盖行缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 母列保留。它在标准化回归组中的位置是 full 轨上"等权对密度加权"的对照格: 与主标准化列 dict_avg_tone_full_z 只差聚合权重一个维度, 若两者系数同向同量级, 词典语调效应不依赖报道关联强度的话语权分配; 若密度加权显著更强, 提示效应集中来自深度聚焦报道, 与 Hassan et al. (2019) 式"相关文本份额承载真实暴露"的解读一致。截面标准化对 vw 列的口径意义: 提及密度分布的年际结构变化 (行业盘点文风潮起落, 单银行深度报道占比波动) 使 vw 语调生值的截面方差漂移, z 变换统一到逐年同业相对位置标尺, 与年份固定效应的组内识别对齐, 系数读为"当年截面内密度加权语调相对同业每高一个标准差, 因变量变动 β 单位"。使用纪律: 与母列同一回归二选一, 分别承载水平效应与相对位置效应两种解读; 与家族内其余 _z 格互为稳健性不分主次, 各自 just-identified 并排, 严禁与任何姊妹测度混进同一 over-identified Hansen J。

## VAR: dict_avg_tone_vw_ss

【变体差分】
本列是提及密度加权乘 ss 轨的词典语调: 情感文本域为银行金科同句共现窗 (content_ss, 含标题, 句窗半径默认一句), 聚合权重为文章对目标银行的提及密度, 分母沿用跨轨共用的 sum_mention_density, 分子取 ss 轨得分的密度加权和。ss 回退公理适用: 无同句共现的文章回退为全文正文计分且 ss_is_fallback 置真, 镜像 ctx 回退语义共享 n_articles 分母, 回退率高的银行年本列语义向 vw_full 收敛。构念定位: vw 权重与 ss 轨都服务于"语调归属于该银行与金融科技的直接关联"这一目标, 但作用在不同层 — ss 在文本层裁剪到同句窗, vw 在权重层提升高提及文章的话语权; 两者叠加是家族内关联归属取向仅次于 mw_ss 的强收紧格, 适合作为"语调效应确实来自银行金科直接关联文本"的机制性稳健检验。代价同样是双重: 同句窗词典命中稀疏放大逐篇噪声, 密度权重又使有效样本向少数深度报道集中, 有效自由度进一步压缩, 小样本银行年慎用。实现守卫: ss 源列未落盘时逐项 if 守卫优雅跳过, geography 跨词典 _safe_mean 缺列容错。配套标准化列 dict_avg_tone_vw_ss_z。三轨四权重所有格互为稳健性不分主次, 各自 just-identified 并排, ss 与 full, ctx 绝不同 RHS, 严禁混进同一 over-identified Hansen J。

## VAR: dict_avg_tone_vw_ss_z

【变体差分】
本列是 dict_avg_tone_vw_ss 的年度截面标准化版本: 提及密度加权乘同句共现轨乘 z 变换的三维交叉格, 与 hw_ss_z, mw_ss_z 并列构成家族 z 族在 ss 轨上的三个加权端点。步骤 7b 统一规则: 逐年截面仅对有新闻覆盖行减均值除标准差, 零覆盖行缺失, 整列有效观测 (合并全部年份) 不足十个时不生成该 _z 列, 已生成的列再在每个年度截面内对有效观测不足三个的年份该年行留缺失不做标准化, 母列保留。在稳健性谱系上, 本列服务于"最大偏离仍同向"的论证收口: 若词典语调效应从等权全文标准化格 (dict_avg_tone_full_z) 一路收紧文本口径 (到同句窗), 重分配话语权 (到高提及密度报道), 再统一截面尺度后依然保持符号与量级, 则该效应对文本归属口径与报道权重结构的联合扰动稳健; 反之翻转格的维度即机制线索。ss 轨两条语义全部继承: 回退率高时趋近 vw_full_z; 同句窗短文本的粗粒化得分使标准化前的截面分布重尾, z 变换统一尺度但不消除噪声, 系数的置信区间预期宽于 full 轨对应格。T=2 开发面板上本列常因 ss 轨整列有效观测 (合并全部年份) 不足十而不被步骤 7b 生成 (整列跳过), 属预期守卫而非缺陷, 生产 T=19 下正常出值。与母列同一回归二选一; 与家族内其余原始格与 _z 格互为稳健性不分主次, 各自 just-identified 并排, 严禁任意组合混进同一 over-identified Hansen J 做联合过度识别检验。

<!-- rendered-citations:begin -->
Aksoy-Yurdagul, D., Buchner, A., & Zareei, A. (2026). The persistence of news sentiment: Implications for return predictability. Economics Letters, 260, 112803. https://doi.org/10.1016/j.econlet.2025.112803
Ni, Y. (2024). Media coverage and disclosure of short‐termism tone: Evidence from China. Accounting & Finance. https://doi.org/10.1111/acfi.13328
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K. (2020). Econometrics meets sentiment: An overview of methodology and applications. Journal of Economic Surveys, 34(3), 512-547. https://doi.org/10.1111/joes.12370
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Heston, S. L., & Sinha, N. R. (2017). News vs. sentiment: Predicting stock returns from news stories. Financial Analysts Journal, 73(3), 67-83. https://doi.org/10.2469/faj.v73.n3.3
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Rutkowska, A., & Szyszko, M. (2024). Dictionary-based sentiment analysis of monetary policy communication: on the applicability of lexicons. Quality & Quantity. https://doi.org/10.1007/s11135-024-01896-9
Wei, L., Wei, M., Jing, H., & Jing, Z. (2025). Annual report tone and bank risk-taking behavior: Evidence from China. Research in International Business and Finance. https://doi.org/10.1016/j.ribaf.2025.102881
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Li, Y. (2026). The Textual Tone of Annual Reports and Market Attention: Evidence From Chinese Listed Companies. Managerial and Decision Economics. https://doi.org/10.1002/mde.70100
<!-- rendered-citations:end -->
