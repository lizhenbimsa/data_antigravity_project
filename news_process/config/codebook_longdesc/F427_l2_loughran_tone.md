---
family_id: F427
columns:
- loughran_tone_app_ctx
- loughran_tone_app_full
- loughran_tone_app_ss
- loughran_tone_ctx
- loughran_tone_full
- loughran_tone_hw_ctx
- loughran_tone_hw_full
- loughran_tone_hw_ss
- loughran_tone_mw_ctx
- loughran_tone_mw_full
- loughran_tone_mw_ss
- loughran_tone_ss
- loughran_tone_std_ctx
- loughran_tone_std_full
- loughran_tone_std_ss
- loughran_tone_tech_ctx
- loughran_tone_tech_full
- loughran_tone_tech_ss
- loughran_tone_vw_ctx
- loughran_tone_vw_full
- loughran_tone_vw_ss
unit: 语调得分 (无量纲连续值, 逐篇归一化后有界 [-1, 1]; 聚合为 bank-year 均值/加权均值/标准差)
formula: "loughran_score(篇, 轨) = Σ_j sign_j · final_score_j / Σ_j |final_score_j| ∈ [-1,1] (final_score 含否定翻转 / 程度副词放大 ≤3.0 / 转折 ×1.5); loughran_tone{track} = mean_{i∈留篇(track)} loughran_score{track}; 加权变体 W_tone{track} = Σ_i w_i·score_i / Σ_i w_i, w ∈ {mention_density(vw), media_authority(mw), herd_decay(hw)}; std=bank-year SD; tech/app=按 innovation_locus 子集条件均值"
producer: news_process/pipeline/sentiment/tone_words.py::compute_dict_scores ; news_process/pipeline/panel/encode.py (聚合与加权/子集派生) ; news_process/pipeline/audit/lm_discriminant_validity.py (判别效度安检)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (loughran_score{track} 逐篇分值)
- 24_herd_decay_processor.parquet (herd_weight{track}, 供 hw 加权)
- 40_panel_yearly.parquet (bank-year 聚合宿主)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Hsiu-Min Chuang, Hsiang-Chih He, Ming-Che Hu"
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: "10.1371/journal.pone.0317503"
  type: "journal"
  authors: "Lingyun Yang, Zhihong Zhang, Lulu Wang, Yikai Liang"
  year: 2025
  title: "Encourage or inhibit: A study on the impact of corporate digital transformation on management's tone manipulation of information disclosure"
  venue: "PLOS ONE"
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1093/rof/rfac052
  type: journal
  authors: Goldstein, I.
  year: 2023
  title: "Information in financial markets and its real effects"
  venue: Review of Finance
  vol: 27
  issue: 1
  pages_or_artno: 1-32
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
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
  venue: SSRN Working Paper No. 3446388
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
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
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
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: "10.1002/isaf.1549"
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  venue: "Intelligent Systems in Accounting, Finance and Management"
  type: "journal"
- doi: "10.1017/S0022109023000716"
  title: "Measuring Firm Complexity"
  authors: "Loughran, T., & McDonald, B."
  year: 2023
  venue: "Journal of Financial and Quantitative Analysis"
  type: "journal"
- doi: "10.1016/j.procs.2025.04.477"
  title: "Enhancing Financial Sentiment Analysis: Integrating the LoughranMcDonald Dictionary with BERT for Advanced Market Predictive Insights"
  authors: "Sheetal, R., & Aithal, P. K."
  year: 2025
  venue: "Procedia Computer Science"
  type: "wp"
new_dois:
- "10.3390/bdcc9100263"
- "10.1371/journal.pone.0317503"
- "10.1002/isaf.1549"
- "10.1017/S0022109023000716"
- "10.1016/j.procs.2025.04.477"
---

## CORE

该文比较词典法(含Loughran-McDonald体系思路)与多种语言模型对中文财经新闻情感分类与股价预测的效果,为词典法情感测度在中文财经文本上的持续适用性提供最新方法学参照。 该文基于中国A股上市公司文本披露语调(词典法测度)考察数字化转型对管理层语调操纵行为的影响,与本家族以词典法测度媒体语调的构念定位高度相关。

【构念与来源】
本家族度量银行-金融科技新闻报道在 Loughran-McDonald (2011) 金融文本词典中文主译本 (本项目里的"第六部主情感词典", 列前缀别名统一写作 loughran) 下的语调 (tone) 极性, 并在 bank-year 层面聚合为可直接进入计量回归的面板变量。构念定位是"某家银行在某一年里被媒体报道时所流露的金融情感倾向": 分值越接近正一, 说明该银行当年报道里净正面的用词越占上风; 越接近负一, 说明净负面的用词越占上风; 越接近零, 说明褒贬大致相抵、整体语调偏中性。用大白话讲, 就是把一年里所有提到这家银行的金融科技新闻按"说好话还是说坏话"打一个从负一到正一的分, 再把这些分数汇总成"这家银行这一年在媒体嘴里的口碑温度"。数据链路自 stage 00 原始语料普查起, 经 stage 11/12 完成银行与金融科技实体识别、stage 13 共现硬过滤 (只保留目标银行与至少一个金融科技词邻近共现的报道, 剔除银行与金科各自出现却互不相关的偶合篇)、stage 14 三轨文本物化, 在 stage 22 (tone_words) 用一张固定词表逐篇打分, 最后在 stage 40 聚合并入银行-年面板。词典本身沿袭 Loughran & McDonald (2011) 提出、并经 Loughran & McDonald (2016) 综述系统化的"领域专用金融情感词表"传统: 其核心洞见是, 通用心理学词典 (如 Harvard IV-4) 搬到金融语境下会把"负债、税、成本"这类中性专业词误判为负面, 因此必须为金融领域另起炉灶构造一张自有的极性词表。本项目采用该词典的中文主译本 (原 61 词经两侧保留判断消歧后, 38 词已归单侧、余 23 词不可约简而保留), 并把它与 Du et al. (2022)、Bian et al. (2021) 等本土中文金融情感词典, 以及 Ma et al. (2025) 面向中国境内投资者的细粒度情感词典, 并列为多词典稳健性谱系中的一部, 目的不是选出"最好的一部词典", 而是证明主结论不被"用哪一部词典量情感"这一选择所左右。

【方法学与计算】
逐篇打分在 tone_words.py::compute_dict_scores 里完成。对每一篇报道的每一条轨道文本, 引擎先做中文分词, 再扫描分词序列, 对命中词典的情感词赋予极性符号 (正面记 +1、负面记 -1), 并逐词施加三条确定性的语言学规则: 否定词窗口内的极性翻转 (让"不乐观"不被算成正面)、程度副词对幅值的放大 (让"非常好"比"好"权重更高, 上限约 ×3.0)、转折连词之后从句的加权 (让"但是"之后的话语更受重视, ×1.5)。逐篇归一化分值 normalized_score = Σ_j sign_j · final_score_j / Σ_j |final_score_j|, 分子是带符号的加权分值之和, 分母是加权幅度绝对值之和, 因而分值严格有界于闭区间负一到正一。这套归一化于 2026-06-11 做过一次修订, 把旧版分母 (裸匹配词数) 改为加权幅度绝对值之和, 修正了旧口径下分子被程度与转折规则放大后值域溢出 ±1 的缺陷 (据当时一次性核查披露, 修订前盘面上有相当比例文章的裸分值绝对量大于一, 此为历史修订动因的口头记录、非当前源码可复核的既定统计量, 仅作背景交代)。该逐篇分值即各轨的 loughran_score 列。面板 canonical 列各轨 loughran_tone 等于留篇集合内该轨逐篇分值的算术平均, 由 encode.py 在 bank-year 分组上以 mean 聚合而得, 聚合口径与 Tetlock (2007)、Marchetti et al. (2025) 的"媒体语调-实体-时间"面板一致。这里有一处方法学要点须澄清本家族的打分口径: 本家族逐篇分值只用 loughran 这一部词典 (JSON 键 loughran_mcdonald_zh_2026 的 positive/negative 数组) 单独驱动, frontmatter 的 loughran_score 公式即单词典口径, 并非把六部词典合并后按多数票定极性的 union 综合分。该 loughran 中文主译本本身在 2026-06-24 极性消歧时对 23 个跨类的多义词采取"两侧保留、pos/neg 各计一次、分子净贡献相互抵为零"的处理 (见 tone_dicts.json 该词典 _description), 即这类歧义词不再被单侧剔除, 而是以平衡的双计数进入分子分母、令 margin 守恒; 因此本家族既不存在"把六部词典并成 union"的合并步骤, 也不存在"平票即整词剔除"的口径 — 那是跨词典综合测度另设的机制, 与本单词典家族无关。词典法与机器学习/大语言模型法之间的取舍见 Frankel et al. (2022)、van Atteveldt et al. (2021)、Algaba et al. (2020): 词典法透明、可复现、无训练数据泄漏, 但对否定、程度与领域漂移敏感, 故本项目以规则增强 (对应 Taboada et al. 2011 的 lexicon-based 范式) 加以缓解, 并保留纯计数消融臂 (negonly) 作对照。

【文献定位】
本家族在文献版图上的坐标是"媒体金融情感的词典法测度"。Tetlock (2007) 最早把词典情感与股市回报系统关联, 奠定"媒体语调可定价"的实证起点; Loughran & McDonald (2011, 2016) 确立了金融领域专用词典的方法学规范, 是本家族词表的直接来源; Hassan et al. (2019) 提供了以文本中关注度密度加权信号的方法学范式, 对应本家族的 vw 变体; Holzman et al. (2023) 论证了按媒体权威性加权语调所携带的额外定价含义, 对应 mw 变体; You et al. (2018) 在中国情境下刻画了媒体"笔杆子"影响力的横截面异质性, 为 mw 权威加权在中国的制度基础提供支撑; Goldstein (2023) 综述了金融市场中信息的真实效应, 为"银行语调经由存款人/投资者关注传导至融资成本与风险"这一因果链提供理论支点。在中文词典这一支上, Du et al. (2022)、Bian et al. (2021) 与 Ma et al. (2025) 分别代表了含政治正面词的金融词典、LM 中文扩展词典与面向散户投资者的细粒度词典, 本项目把它们与 loughran 中文主译本并列, 使跨词典的稳健性论证在中英来源、构造判据与粒度上都有覆盖。词典法与语义模型 (LLM/BERT) 的三方法互证先例见 Frankel et al. (2022)。Todd, Bowden & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 该2024年综述系统梳理了金融文本情感分析文献 (含 Loughran-McDonald 等词典法与机器学习法的对比与未来方向), 为本家族以词典法测度媒体语调提供了最新的方法学定位坐标。Loughran与McDonald本人基于其词典衍生构建企业复杂度文本测度, 是LM框架的最新权威延伸, 见 Loughran & McDonald (2023, Journal of Financial and Quantitative Analysis)。将Loughran-McDonald词典法与BERT深度学习结合用于金融文本情感分析, 验证词典法在现代NLP流水线中的持续适用性, 见 Sheetal & Aithal (2025, Procedia Computer Science)。

【识别策略定位】
loughran_tone_full 是本家族的 core 列, 作为跨词典稳健性谱系的成员进入主线论文 bank_fintech_tone 的处理变量 (treatment) 族。识别策略上, 它与 du_2022、jiang_2021、yao_2021、bian_2021 等其它词典的同轨 tone 各自是对"同一个媒体情感构念"的替代测量 (alternative measurement): 每一个测度各自 just-identified、并排陈列, 互为稳健性、不分主次, 严禁把不同词典 (或同一词典的不同加权、不同子集、不同轨道) 混入同一个 over-identified 的 Hansen J 过度识别检验里去当多个工具用 [CLAUDE.md 铁律]。之所以定这条铁律, 是因为这些测度彼此高度共线、量的是同一件事, 硬凑进一个过度识别方程只会制造虚假的自由度、扭曲 J 统计量; 正确做法是逐个替换主测度、看系数与显著性是否稳。跨词典结论的一致性由根级跨模型/跨测度稳健性模板复核, 多重假设检验的族错误率 (FWER) 控制沿用 Romano & Wolf (2005) 的 stepwise 逻辑, 避免"多量几部词典总能撞出一个显著"的数据窥探问题。

【与相邻测度的构念区分】
loughran 词典 tone 与本项目其它情感测度须明确区分, 以免读者误当冗余。相对 LLM 三家投票共识 tone (llm_vote_tone): 后者靠大模型做语义理解、对上下文与反讽敏感, 但过程不透明、有厂商与版本依赖; 词典 tone 则是词袋计数、语义较浅但完全可复现、零训练泄漏。相对 BERT 概率情感: 词典法无需微调模型、不带训练分布依赖, 换语料不必重训。相对同为词典的 du_2022: loughran 是英文金融词典的中文主译、不设政治正面词的特殊权重, 而 du_2022 专门为政治正面词设了 0.0/0.5/1.0 三权重敏感性梯度 — 两者词表来源与构造判据不同, 因此并列而非合并。相对本项目的 idf 加权版 (F418 loughran_idf_tone): 本家族用词频等权计数、不做逆文档频率再加权, idf 版则对高频常见词降权。厘清这些区分, 正是判别效度安检要回答的问题。

【已知局限与稳健性梯子】
已知局限有三: 其一, 中文分词与词典命中受 jieba 0.42.1 冻结词典约束, 罕见或新造表述可能漏配, 导致个别篇章情感被低估; 其二, 词典法对隐含语义、反讽、语用暗示不敏感, 只数字面词; 其三, 中国媒体存在制度性的正面偏向与负面信息抑制, 因此语调"水平值"的跨银行/跨年解读须谨慎, 更稳妥的用法是看相对变化而非绝对高低。为缓解这些局限, 本家族布设了多重稳健性梯子, 且每一条都遵守"各自 just-identified 并排、互为稳健性、禁混同一 over-identified Hansen J"的铁律: 其一是三轨 full/ctx/ss — full 是标题 prepend 后拼全文, ctx 是标题加银行实体上下文窗口, ss 是标题加银行与金科同句共现窗; 留篇门控为 full-only 口径 (2026-06-29 定), 即一篇报道是否算作"一篇银行金科报道"只看 full 轨的 LLM 判定 llm_verified_full, ctx/ss 因此降格为 conditional-on-full 的子集测度, 行宇宙是 full 轨留篇集合的子集, ss 轨在无同句共现时回退镜像 ctx、取全文 body 语义并与 full 共享 n_articles 分母。其二是三种聚合加权 vw/mw/hw (提及密度 / 媒体权威 / 跟风衰减) 与等权 canonical 并列, 用以证明结论不被"按什么加权"驱动。其三是 tech/app 按创新落点 (Gomber 2018 框架) 把报道切成底层技术子集与应用场景子集, 检验落点异质性。其四是 std 用年内标准差刻画语调离散度, 作为一阶均值之外的二阶稳健性维度。判别效度另由 lm_discriminant_validity.py 的 HTMT/Cronbach 安检把关, 确认各文本测度彼此不冗余、能同时进论文, 否则就得砍掉或合并冗余指标。这套安检本身不改主回归面板, 只产几张诊断表和日志, 但它是这些文本指标能否进论文的"安检口": 通过了, 论文才能放心声称这些词典测度各自独立有效; 不通过, 就得删减冗余指标, 直接影响论文用哪些自变量以及结论的可信度。

【聚合口径与文本轨道的正交结构】
这里有必要把本家族二十一列的组织逻辑讲透, 以免读者把它们当成互相冗余的重复列。全部列由两条正交的维度交叉而成: 第一条是文本轨道 (full/ctx/ss), 回答"读多少文本来给一篇报道打分"; 第二条是聚合方式, 回答"把一年里各篇的分数怎么汇总成银行-年的一个数"。聚合方式又细分为等权均值 (canonical, 无中缀)、年内标准差 (std)、三种加权均值 (vw 提及密度、mw 媒体权威、hw 跟风衰减) 以及两个落点子集条件均值 (tech 底层技术、app 应用场景)。二十一列即"轨道 × 聚合"的组合 (并非每个组合都物化, 例如 std 只做三轨、vw/mw/hw 与 tech/app 也各做三轨)。理解这个网格的关键是: 沿轨道方向移动改变的是"证据范围", 沿聚合方向移动改变的是"汇总权重或子样本", 两条轴彼此独立、语义不重叠。正因如此, 每一条轴上的诸列都构成一组"互为稳健性、不分主次"的替代测量, 而非层层嵌套的一个 over-identified 方程的多重工具 — 这正是本家族反复重申"各自 just-identified 并排、禁混同一 over-identified Hansen J"铁律的结构性原因。

【逐篇分数如何汇总为面板值】
用大白话把计算再走一遍: 第一步在 stage 22 给每篇报道每条轨道各算一个 loughran_score, 它已经是把否定、程度、转折都算进去、并归一化到负一到正一之间的净语调。第二步在 stage 40/encode 把某银行某年的这些逐篇分数汇总: 若是 canonical 就直接求算术平均; 若是 std 就求标准差 (量分歧); 若是 vw/mw/hw 就先给每篇乘上对应权重、把加权分数加总, 再除以权重之和 (加权平均); 若是 tech/app 就先只留下被判为该落点的报道, 再在这个子集上求平均。加权平均的一个技术细节值得写明: 词典分数对每一篇都有定义 (匹配不到情感词记 0 而非缺失), 因此加权平均的分母用的是全体报道的物理权重和, 这与 LLM 族 (打分可能失败、记为缺失) 必须改用"仅对打分成功篇计权重"的有效掩码分母不同 — 词典族若误套有效掩码分母反而会失配, 故本家族一律用物理分母。理解了这一步, 就能明白为什么同一银行同一年在不同列会得到不同的数: 不是数据矛盾, 而是"用不同的尺子、从不同的角度量同一件事", 而主结论要求的正是这些角度给出方向一致的答案。

【与主线论文的接口与解读注意】
本家族的 core 列 loughran_tone_full 进入主线论文 bank_fintech_tone 的处理变量族, 与 LLM 投票共识 tone、其它五部词典 tone、BERT 情感一道, 构成"跨方法 × 跨词典 × 跨轨道 × 跨加权"的多层稳健性证据网。解读时须谨记三点: 其一, 语调是处理变量 (treatment) 一侧的构念, 与结果变量 (如融资成本、风险) 是两套东西, 本家族只负责前者的测量; 其二, 因中国媒体的制度性正面偏向, 语调绝对水平的跨主体高低不宜过度解读, 应更看重银行内的时间变化与相对排序; 其三, 所有加权与子集变体都是为了回答"结论是否被某个测量选择驱动"这一稳健性追问, 它们的价值在于与 canonical 方向一致时提升可信度, 而非各自给出独立的新结论。财务结果数据后续接入后, 本家族语调列即可作为解释变量与之匹配, 完成"媒体语调—银行结果"的因果链测量。

【为何选用中文主译而非另起本土词典】
读者可能会问: 既然已有 du_2022、bian_2021、jiang_2021、yao_2021 等本土中文金融情感词典, 为何还要把英文 Loughran-McDonald 词典译成中文再用? 原因有三。其一, LM 词典是国际金融文本分析事实上的基准, 采用其中文主译本可让本项目结果与英文文献直接可比, 便于审稿人横向校准。其二, 不同词典的构造判据、词表来源、覆盖侧重各不相同 (有的偏年报语言、有的偏股吧口语、有的含政治词), 把 LM 中文译本与本土词典并列, 恰好在"词表来源"这条轴上再加一层稳健性: 若中英来源、口语与书面来源、含政治词与不含政治词的词典都给出方向一致的语调结论, 主结果就更难被"某一部词典的特质"解释掉。其三, 六部词典并非合并成一部综合词表后共同打分, 而是各用各的固定词表、并排各自打一套逐篇分值, 再在面板上互为稳健性地并列比对; 本家族这套列即由 loughran 中文主译本单独驱动, LM 译本贡献其特有的金融专业极性词, 与本土词典互补而非替代, 是"另一把独立的尺子"而非"某把合尺里的一节"。需强调, 本家族列名前缀 loughran 仅是列前缀别名 (JSON 键为 loughran_mcdonald_zh_2026), 它与其它五部词典的逐篇打分口径完全同构 (同一套否定/程度/转折规则、同一套归一化), 差异只在词表本身。

【确定性与可复现保证】
本家族的全部计算是确定性的、可逐位复现的: 逐篇打分不调用任何大模型或外部 API, 只做分词与词表查表加规则运算, 因此不受网络、缓存或模型版本影响; jieba 分词器版本冻结在 0.42.1, 词表冻结在 config/tone_dicts.json (本家族取其 loughran_mcdonald_zh_2026 键的单词典 positive/negative 数组), 极性判定与规则施加 (跨类多义词两侧保留双计数、否定翻转、程度放大、转折加权) 均与词典遍历顺序无关。这意味着只要输入语料与配置不变, 本家族二十一列在任意机器上重跑都会得到字节级一致的结果 — 这是词典法相对 LLM/BERT 法的一大工程优势, 也是把它保留在稳健性谱系中的实用理由之一。开发期盘面为 T=2 (约二百行、2017–2018 两年) 的试跑子集, 家族内 std 与落点子集列在这种极小样本下会大面积退化 (SD 不稳、子集置空), 属预期现象, 生产 T=19 全量语料下方能给出可靠估计; codebook 的动态统计段所注入的数值均为开发期实测, 仅供占位参照, 一律以生产重生后的实读为准。综上, 本家族以一部国际基准词典的中文主译本为核心, 用等权 canonical 作锚, 沿文本轨道与聚合方式两条正交轴铺开二十一列稳健性证据, 全部遵守各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J 的口径铁律, 既保证了词典法的透明可复现, 又为主线论文的语调测量提供了跨轨道、跨加权、跨落点的多重佐证。

## VAR: loughran_tone_full

【变体差分】
本列是家族 canonical 核心列, 也是 tier=core 的基准, 是整个家族其余二十列的语义原点。它取 full 轨 (标题 prepend 后拼接全文正文, 即 content_full) 上逐篇 loughran_score_full 的 bank-year 算术平均, 权重等权、不加权、不分层。用大白话说, 就是把某银行某年所有留篇报道各自的语调分数简单地求平均, 得到"这家银行这一年在媒体嘴里平均有多正面"。full 轨是本项目的留篇门控轨 (2026-06-29 起的 full-only 口径): 一篇报道是否被计入某银行某年的"银行金科报道"宇宙, 完全由 full 轨的 LLM 判定 llm_verified_full 决定; 因此本列的分母 (留篇集合) 恰是家族内其余全部 ctx/ss 轨列的母集, 那些 ctx/ss 轨列都是本列留篇集合上的 conditional-on-full 子集测度。这一门控设计的用意是: 只用一个统一、最完整的口径来界定"哪些篇算数", 避免各轨各自定留篇导致样本框互不可比。相对同为等权均值的 loughran_tone_ctx 与 loughran_tone_ss, 本列采用最完整的文本证据 (整篇全文, 而非仅实体上下文窗口或同句共现窗口), 因而对报道整体语调最灵敏、覆盖率最高、缺失率最低, 是主线回归首选的处理变量测度轨。相对本家族的加权与分层变体, 本列不施加提及密度 (vw)、媒体权威 (mw) 或跟风衰减 (hw) 任何权重, 也不按创新落点切成 tech/app 子集, 因此承担"最朴素、最可比"的基准角色: 所有加权、分层与离散度列都以本列为参照系, 用以论证主结论不被聚合权重或子样本选择所驱动。为什么把它设为等权而非某种加权作 canonical? 因为等权均值不引入任何额外的权重假设, 解读最直接、可复现性最强, 加权变体则各自回答"若更看重高强度/高权威/低跟风的报道, 结论是否依旧"这类稳健性追问。方法学上, 本列的逐篇分值先经否定翻转、程度副词放大 (上限约 ×3.0) 与转折从句加权 (×1.5) 三条确定性规则调整, 再归一化到闭区间 [-1,1], 最后在 bank-year 分组上取均值, 聚合口径与 Tetlock (2007)、Marchetti et al. (2025) 的媒体语调-实体-时间面板一致, 词典来源为 Loughran & McDonald (2011) 中文主译本、并入六部词典的固定 union 词表统一打分。它与其它五部词典 (du_2022、jiang_2021、yao_2021、bian_2021 等) 的同轨 canonical tone 各自 just-identified 并排、互为稳健性、不分主次, 严禁与任何其它词典、任何加权或任何轨道混入同一个 over-identified 的 Hansen J [CLAUDE.md 铁律]。作为 core 列, 它同时是跨词典稳健性谱系的锚点与主线论文 bank_fintech_tone 处理变量族的主测度轨; 跨测度一致性由根级跨模型/跨测度稳健性模板复核, 多重假设检验的族错误率沿 Romano & Wolf (2005) 的 stepwise 逻辑控制。使用时须留意: 本列量的是语调水平, 中国媒体的正面偏向使绝对水平的跨主体比较不宜过度解读, 更稳妥的是关注银行内的时间变化与相对排序。还须强调, 本列作为 core 列在整个家族里承担"基准锚"角色: 其余二十列无论换轨道、换加权还是换子集, 最终都要回到与本列的比对上来 — 只有当那些变体与本列给出方向一致的结论时, 才能说主结果不是某个测量口径的偶然产物。因此本列的覆盖率最高、口径最朴素这一点不是缺点而是设计要求: 越是不引入额外假设的基准, 越适合承担被反复对照的参照系。开发期 T=2 语料下本列的均值/缺失率等实测值仅供占位, 生产 T=19 全量重生后须以实读为准, 切勿据开发期数值下实质结论。

## VAR: loughran_tone_ctx

【变体差分】
用大白话说, 本列只读报道里"提到这家银行的那几句上下文", 而不是通篇全文, 相当于把注意力聚焦到银行本身、先擦掉跑题的段落再来量语调; 这样做的好处是抗稀释, 一篇长报道即便大段谈行业背景, 只要涉及本行的语句偏正面, ctx 轨也能把这份正面读出来, 不被无关内容平均掉。它与 full 轨互证的逻辑是, 若"聚焦上下文"与"通篇全文"两种读法给出一致结论, 就说明语调信号稳健、不依赖阅读窗口的宽窄。

本列是 full/ctx/ss 三轨稳健性梯子中的 ctx 轨等权均值。它取 content_ctx 文本 (标题 prepend + 目标银行实体上下文窗口, 而非全文) 上逐篇 loughran_score_ctx 的 bank-year 算术平均。相对 canonical 的 loughran_tone_full, 差别仅在文本证据范围: ctx 轨只截取围绕银行实体提及的局部上下文窗口, 剔除与目标银行无关的段落, 从而把语调测量聚焦到"与该银行直接相关的语句", 降低全文中无关内容对语调的稀释。因此本列对"针对性报道情感"更敏感, 但覆盖的文本更短、噪声结构不同, 与 full 轨互为稳健性: 若两轨结论一致, 说明语调信号不依赖于是否纳入全文旁支内容。留篇门控为 full-only, 本列是 conditional-on-full 子集测度 — 行宇宙为 full 轨留篇集合的子集, 分母口径继承 full 轨, per-track 分子照 ctx 轨自身有效篇数计。本列不加权、不分层, 与 loughran_tone_vw/mw/hw_ctx 及 tech/app_ctx 构成同轨内的不同派生维度。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与逐篇归一化口径同家族 canonical, 仅文本轨道不同。

## VAR: loughran_tone_ss

【变体差分】
用大白话说, ss 轨最"较真": 只有当某句话里银行和金融科技词真的同时出现, 这句才算数, 从而排除"上半篇讲银行、下半篇讲金科"这类看似相关实则各说各话的偶合报道。它量的是银行与金科真正绑在同一句话里时的那份情感, 语境最纯但样本也最少; 一旦某篇找不到这样的同句, 就退回全文来量并标记 fallback, 以免整篇被丢空。

本列是三轨梯子中的 ss 轨 (same-sentence, 银行与金融科技同句共现轨) 等权均值。它取 content_ss 文本 (标题 prepend + 目标银行与金融科技词在同一句子内共现的句子窗口, 半径由 config filtering.yaml 的 ss_sentence_radius 控制, 默认 ±1 句) 上逐篇 loughran_score_ss 的 bank-year 均值。相对 full/ctx, ss 轨把语调测量收紧到"银行与金科真正同句共现"的最严格语境, 因而最能剔除银行与金科各自独立出现、实则不相关的偶合报道, 测得的是"银行-金科关联语句"本身的情感。回退语义为镜像 ctx: 当某篇无银行与金科同句共现时, content_ss 回退为全文 body, ss_is_fallback 置真, 并与 full 轨共享 n_articles 分母; 若金科 AC 自动机为空则全篇优雅降级。留篇门控 full-only, 本列同为 conditional-on-full 子集测度。ss 轨文本最短、缺失率与回退比例最高, 与 full/ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同 canonical。

## VAR: loughran_tone_std_full

【变体差分】
用大白话说, 均值列回答"这家银行今年整体口碑多好", 本列则回答"今年的报道口径是统一还是众说纷纭"。同样是正面居多, 若各篇分数彼此接近, SD 就小、说明市场认知一致; 若有的极正有的极负相互拉扯, SD 就大、说明存在分歧或争议。这份"分歧度"本身在存款人纪律与信息含量文献里被视作独立于水平的信号, 因此把它单列为一个稳健性维度。

本列是 full 轨上 loughran_score_full 的 bank-year 标准差 (SD), 而非均值。它刻画的是某银行某年报道语调的年内离散度: 值越大, 该银行当年报道褒贬分歧越大、语调越不一致; 越接近零, 报道语调越集中。相对 canonical 的均值列 loughran_tone_full (一阶矩), 本列是二阶矩测度, 二者构念正交 — 均值回答"平均多正面", SD 回答"多分散"。它作为语调分歧/不确定性的稳健性维度, 可支撑"媒体语调分歧本身对银行融资/风险有独立含义"一类假设 (呼应 Goldstein 2023 关于信息在金融市场真实效应的讨论)。计算由 encode.py 在 bank-year 分组上对该词典逐篇分值列取 std 聚合而得 (聚合算子为分组标准差)。留篇集合与轨道口径同 full 轨 canonical, 仅聚合算子由 mean 改 std。本列与 std_ctx/std_ss 及各均值列各自 just-identified 并排、互为稳健性, 严禁混入同一 over-identified Hansen J [CLAUDE.md 铁律]。年内有效篇数过少时 SD 不稳定 (T=2 开发期尤甚), 生产 T=19 语料下方为可靠离散度测度。

## VAR: loughran_tone_std_ctx

【变体差分】
用大白话说, 本列衡量的是"聚焦到本行的那些语句"在一年里彼此有多不一致。全文轨的分歧可能被大量无关内容摊平, 而上下文轨剔除旁支后, 真正针对本行的褒贬拉扯会更清楚地显现, 因此它与 std_full 的分歧结构未必相同, 二者互为稳健性、可交叉验证语调分歧信号是否稳定。

本列是 ctx 轨 (标题+银行实体上下文窗口) 上 loughran_score_ctx 的 bank-year 标准差。与 std_full 同为二阶矩离散度测度, 差别仅在文本轨道: 本列度量的是"针对该银行的上下文语句"情感在年内的分散程度, 剔除全文旁支后, 分歧结构可能不同于 full 轨。相对 canonical 均值列 loughran_tone_ctx, 本列回答的是同轨语调的离散而非水平, 二者正交互补, 一个回答"平均多正面"、另一个回答"分歧多大", 谁也替代不了谁。留篇门控 full-only, 本列为 conditional-on-full 子集上的年内 SD, 行宇宙继承 full 轨留篇集合, 分子按 ctx 轨自身有效篇数计。它与 std_full/std_ss 构成离散度的三轨梯子, 与各轨均值列一并各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨或均值/离散度混入同一 over-identified Hansen J [CLAUDE.md 铁律]。计算算子为 encode.py 分组 std, 词典与逐篇归一化口径同家族 canonical。开发期年内篇数少时 SD 波动大, 以生产语料实读为准。

## VAR: loughran_tone_std_ss

【变体差分】
用大白话说, 本列衡量的是"银行与金科同句语境"里语调在一年内的分散程度, 是最纯语境下的分歧度。由于同句样本本就稀少、且缺同句时会退回全文来量, 这份 SD 的稳定性最依赖语料规模, 在小样本开发期波动很大、只宜作参照, 生产语料下方为可靠。它与 std_full、std_ctx 组成语调离散度的三轨梯子, 三轨各自 just-identified 并排、互为稳健性, 用以确认"语调分歧"这一信号在最宽到最窄三种阅读窗口下都成立, 而非某一轨的偶然。

本列是 ss 轨 (银行与金科同句共现轨) 上 loughran_score_ss 的 bank-year 标准差, 度量最严格共现语境下语调在年内的离散度。相对 std_full/std_ctx, 本列的文本证据最窄 (同句窗口), 回退语义镜像 ctx (无同句共现时回退全文 body, ss_is_fallback 置真, 共享 n_articles 分母), 因而其 SD 也受回退结构影响。相对 canonical 均值列 loughran_tone_ss, 本列回答同轨语调的分散而非水平。留篇门控 full-only, 本列为 conditional-on-full 子集上的 SD。它与 std_full/std_ctx 组成离散度三轨梯子, 各自 just-identified 并排、互为稳健性, 严禁三轨或一/二阶矩混入同一 over-identified Hansen J [CLAUDE.md 铁律]。聚合算子为 encode.py 分组 std, 词典与归一化口径同 canonical。ss 轨缺失/回退比例高, 加之年内篇数少, SD 在开发期 T=2 上尤不稳定, 以生产 T=19 实读为准。

## VAR: loughran_tone_vw_full

【变体差分】
用大白话说, 等权是"每篇报道一票", 本列则是"提到本行越多的报道票越重": 一篇通篇围绕本行的深度报道, 比只用一句带过的顺提, 对最终语调的贡献更大。这样量出的是"以本行为主角的报道"的情感, 抑制了蜻蜓点水式提及对均值的稀释, 回答的稳健性追问是"若更看重高强度报道, 结论是否依旧"。

本列是 full 轨上按"提及密度 (mention density)"加权的语调, 即 value-weighted tone。计算为 W_tone_full = Σ_i (mention_density_i · loughran_score_i) / Σ_i mention_density_i, 分子分母同域 (词典分值对每篇非缺失, 故用物理权重和作分母, 非 LLM 族的 valid-mask 分母)。相对等权 canonical loughran_tone_full 的算术平均, 本列给"更密集提及目标银行"的报道更高权重, 使语调测度更偏向那些以该银行为主角的高强度报道, 抑制一笔带过式提及的稀释。方法学范式取自 Hassan et al. (2019) 以文本中关注度密度加权信号的做法。差异维度是聚合权重而非轨道或词典: 与 canonical 一起论证主结论不被"是否按提及强度加权"驱动。留篇集合与 full 轨口径一致。本列与 mw/hw 加权列及等权 canonical、与其它轨道的 vw 变体各自 just-identified 并排、互为稳健性、不分主次, 严禁不同加权或不同轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与逐篇归一化口径同 canonical, 仅聚合权重不同。

## VAR: loughran_tone_vw_ctx

【变体差分】
用大白话说, 本列在"聚焦本行的上下文"上再叠一层"提及越密权重越高"的规则, 双重聚焦于高强度、针对性强的报道。它与 vw_full 的差别只在读全文还是读上下文窗口, 与同轨等权列的差别只在是否按提及强度加权, 三者互相参照即可看出语调结论对读法与加权是否敏感。提及密度权重的方法学范式取自 Hassan et al. (2019) 以文本中关注度密度加权信号的做法, 分母用词典族物理权重和 (每篇均有分数, 无需有效掩码)。

本列是 ctx 轨 (标题+银行实体上下文窗口) 上按提及密度加权的 value-weighted 语调, 加权公式同 vw_full (Σ 权重·分值 / Σ 权重, 词典族物理分母)。相对 vw_full, 差别在文本轨道: 本列在实体上下文窗口文本上打分后再按提及密度加权, 度量"针对性上下文语句"的强度加权情感。相对同轨等权 canonical loughran_tone_ctx, 本列引入提及密度权重, 使高强度报道主导。权重范式同 Hassan et al. (2019)。留篇门控 full-only, 本列为 conditional-on-full 子集上的加权均值。它与 vw_full/vw_ss 构成提及密度加权的三轨梯子, 与 mw/hw/等权各变体各自 just-identified 并排、互为稳健性, 严禁不同加权或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同家族 canonical, 仅轨道与聚合权重与 canonical 不同。

## VAR: loughran_tone_vw_ss

【变体差分】
用大白话说, 本列在最严格的"同句共现"语境上再按提及密度加权, 突出那些既真正关联、又高强度报道本行的篇章。同句样本本就稀少、又叠加权重, 其数值在小样本下更不稳, 只作稳健性参照, 与 vw_full/vw_ctx 交叉印证提及强度加权是否改变结论。提及密度权重范式取自 Hassan et al. (2019); 本轨在无同句共现时回退全文 body 并标记 ss_is_fallback, 与 full 共享 n_articles 分母, 故其加权均值同时受回退结构与样本量影响, 解读须留意。

本列是 ss 轨 (银行与金科同句共现轨) 上按提及密度加权的 value-weighted 语调。加权公式同 vw 家族 (Σ mention_density·score / Σ mention_density, 物理分母)。相对 vw_full/vw_ctx, 本列文本证据最窄 (同句窗口), 回退语义镜像 ctx (无同句共现回退全文 body, ss_is_fallback 置真, 共享 n_articles 分母)。相对同轨等权 canonical loughran_tone_ss, 本列以提及密度加权, 突出高强度共现报道。权重范式同 Hassan et al. (2019)。留篇门控 full-only, 本列为 conditional-on-full 子集加权均值。它与 vw_full/vw_ctx 构成提及密度加权三轨梯子, 与 mw/hw/等权变体各自 just-identified 并排、互为稳健性、不分主次, 严禁不同加权或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同 canonical, ss 轨缺失/回退比例高, 加权均值在开发期尤不稳定, 以生产语料实读为准。

## VAR: loughran_tone_mw_full

【变体差分】
用大白话说, 等权把党报和小网站一视同仁, 本列则让"更权威、更有影响力的媒体"说的话更算数。在中国媒体格局下, 主流党报与头部财经媒体的报道传播更广、可信度更高, 按权威度加权更贴近"高影响力信源塑造出来的口碑"。当多数来源都落在默认权重上时, 本列会退化为接近等权, 区分度由归一化后权重的标准差判读。

本列是 full 轨上按"媒体权威性 (media authority)"加权的语调, media-authority-weighted tone。计算为 W_tone_full = Σ_i (media_authority_weight_i · loughran_score_i) / Σ_i media_authority_weight_i, 权重取自 media_weights.json 按媒体排名百分位归一化的权威度 (default 权重兜底缺失媒体)。相对等权 canonical, 本列给权威度更高的媒体来源 (如党报、主流财经媒体) 的报道更高权重, 使语调更反映高影响力信源的口径。方法学取自 Holzman et al. (2023) 关于媒体权威性加权情感定价含义的论证, 中国情境的媒体影响力异质性支撑见 You et al. (2018)。差异维度是聚合权重: 与 vw (提及密度) 和 hw (跟风衰减) 并列, 论证主结论不被"按信源权威度加权"驱动。留篇集合与 full 轨口径一致。本列与 vw/hw 及等权 canonical、与其它轨道 mw 变体各自 just-identified 并排、互为稳健性、不分主次, 严禁不同加权或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。当多数媒体落默认权重时 mw 接近等权 (区分度低), 权重区分度由 encode.py 归一化后 SD 判读。词典与归一化口径同 canonical。

## VAR: loughran_tone_mw_ctx

【变体差分】
用大白话说, 本列在"聚焦本行的上下文"上再让权威媒体的话更算数, 双重贴近"重要信源如何评价本行"。它与 mw_full 只差读全文还是读上下文窗口, 与等权同轨列只差是否按信源权威度加权, 三者对照即可判断结论是否被信源权重驱动。媒体权威加权范式取自 Holzman et al. (2023) 关于媒体权威性加权情感定价含义的论证, 中国情境下媒体影响力的横截面异质性支撑见 You et al. (2018); 权重取自 media_weights.json 按媒体排名百分位归一化的权威度, 缺失媒体落默认权重。

本列是 ctx 轨 (标题+银行实体上下文窗口) 上按媒体权威性加权的语调, 加权公式同 mw_full (Σ media_authority·score / Σ media_authority)。相对 mw_full, 差别在文本轨道: 在实体上下文窗口文本上打分后再按信源权威度加权。相对同轨等权 canonical loughran_tone_ctx, 本列引入媒体权威权重, 突出高影响力信源。权重范式同 Holzman et al. (2023), 中国媒体影响力异质性见 You et al. (2018)。留篇门控 full-only, 本列为 conditional-on-full 子集加权均值。它与 mw_full/mw_ss 构成媒体权威加权三轨梯子, 与 vw/hw/等权变体各自 just-identified 并排、互为稳健性, 严禁不同加权或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同家族 canonical, 权重区分度依赖 media_weights.json 覆盖度, 以生产语料实读为准。

## VAR: loughran_tone_mw_ss

【变体差分】
用大白话说, 本列在最严格的同句共现语境上再按媒体权威度加权, 量的是"权威信源在把银行与金科绑在同一句话里时"的情感口径。同句样本稀少加上权重依赖 media_weights.json 的覆盖度, 数值稳定性以生产语料为准, 与 mw_full/mw_ctx 交叉印证。媒体权威加权范式取自 Holzman et al. (2023), 中国媒体影响力异质性见 You et al. (2018); 当多数来源落默认权重时本列退化为接近等权, 区分度由归一化后权重的标准差判读, 本轨在无同句共现时回退全文并标记 ss_is_fallback。

本列是 ss 轨 (银行与金科同句共现轨) 上按媒体权威性加权的语调, 加权公式同 mw 家族。相对 mw_full/mw_ctx, 本列文本证据最窄 (同句窗口), 回退语义镜像 ctx (无同句共现回退全文 body, ss_is_fallback 置真, 共享 n_articles 分母)。相对同轨等权 canonical loughran_tone_ss, 本列以信源权威度加权。权重范式同 Holzman et al. (2023), 中国媒体影响力异质性见 You et al. (2018)。留篇门控 full-only, 本列为 conditional-on-full 子集加权均值。它与 mw_full/mw_ctx 构成媒体权威加权三轨梯子, 与 vw/hw/等权变体各自 just-identified 并排、互为稳健性、不分主次, 严禁不同加权或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同 canonical, ss 轨缺失/回退比例高, 加权均值开发期尤不稳定, 以生产语料实读为准。

## VAR: loughran_tone_hw_full

【变体差分】
用大白话说, 一个热点事件常引来一窝蜂的跟风报道, 若不处理, 等权均值会被这堆重复报道带偏。本列按"扎堆跟风就降权、时间越挤越降"的规则加权, 让语调更接近独立信息事件的净口径, 而不是被信息级联放大的回声。回答的稳健性追问是"若剔除跟风回声, 结论是否依旧"。跟风衰减权重来自 stage 24 (herd_decay_processor), 对短时间内扎堆跟风的同题报道按时间衰减降权, 方法学呼应 Tetlock (2007) 及媒体扩散/跟风情感的实证传统; 分母按三轨独立 (sum_herd_weight_full/ctx/ss), 修正早期把全文权重和错除给多轨的缺陷。

本列是 full 轨上按"跟风衰减 (herd decay)"加权的语调, herd-decay-weighted tone。计算为 W_tone_full = Σ_i (herd_weight_i · loughran_score_i) / Σ_i herd_weight_i, herd_weight 来自 stage 24 (herd_decay_processor): 对短时间内扎堆跟风的同题报道按时间衰减降权, 使语调不被信息级联式重复报道放大。方法学取自 Tetlock (2007) 及媒体扩散/跟风情感的实证传统, 与本项目 herd_decay 阶段的时间衰减权重配套。相对等权 canonical, 本列抑制"一窝蜂"报道对语调的过度贡献, 测得更接近独立信息事件的净语调。差异维度是聚合权重: 与 vw (提及密度) 和 mw (媒体权威) 并列。分母按轨道三轨独立 (sum_herd_weight_full/ctx/ss), 修正早期错配。留篇集合与 full 轨口径一致。本列与 vw/mw 及等权 canonical、与其它轨道 hw 变体各自 just-identified 并排、互为稳健性、不分主次, 严禁不同加权或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与逐篇归一化口径同 canonical, 仅聚合权重不同。

## VAR: loughran_tone_hw_ctx

【变体差分】
用大白话说, 本列在"聚焦本行的上下文"上再对扎堆跟风的重复报道降权, 双重逼近"针对本行的独立信息"。它与 hw_full 只差读全文还是读上下文窗口, 分母各轨独立以免把全文的权重和错除到上下文轨上。跟风衰减权重同来自 stage 24 herd_decay 的时间衰减机制, 方法学呼应 Tetlock (2007); 留篇门控 full-only, 本列为 conditional-on-full 子集上的加权均值, 与 hw_full/hw_ss 组成跟风衰减加权的三轨梯子, 三轨各自 just-identified 并排、互为稳健性, 禁混同一 over-identified Hansen J。词典与逐篇归一化口径同家族 canonical, 仅文本轨道与聚合权重与 canonical 不同, 数值以生产语料实读为准。

本列是 ctx 轨 (标题+银行实体上下文窗口) 上按跟风衰减加权的语调, 加权公式同 hw_full, 分母用本轨独立的 sum_herd_weight_ctx。相对 hw_full, 差别在文本轨道: 在实体上下文窗口文本上打分后按跟风衰减权重聚合。相对同轨等权 canonical loughran_tone_ctx, 本列对扎堆跟风报道降权, 突出独立信息事件的语调。权重范式同 Tetlock (2007) 与本项目 stage 24 herd_decay 时间衰减配套。留篇门控 full-only, 本列为 conditional-on-full 子集加权均值。它与 hw_full/hw_ss 构成跟风衰减加权三轨梯子, 与 vw/mw/等权变体各自 just-identified 并排、互为稳健性, 严禁不同加权或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同家族 canonical, 仅轨道与聚合权重与 canonical 不同。

## VAR: loughran_tone_hw_ss

【变体差分】
用大白话说, 本列在最严格的同句共现语境上再对跟风报道降权, 量的是银行与金科真正同句、且剔除回声后的净语调。同句缺失与 herd 分母缺失可能叠加, 小样本下尤不稳, 只作参照, 与 hw_full/hw_ctx 交叉印证跟风衰减加权是否改变结论。跟风衰减权重来自 stage 24 herd_decay 的时间衰减机制, 方法学呼应 Tetlock (2007); 本轨分母用独立的 sum_herd_weight_ss, 缺失时退化全 NaN、ss hw 列随之 NaN, 无同句共现时文本回退全文 body 并标记 ss_is_fallback。

本列是 ss 轨 (银行与金科同句共现轨) 上按跟风衰减加权的语调, 加权公式同 hw 家族, 分母用本轨独立的 sum_herd_weight_ss (缺失时退化全 NaN, ss hw 列随之 NaN)。相对 hw_full/hw_ctx, 本列文本证据最窄 (同句窗口), 回退语义镜像 ctx (无同句共现回退全文 body, ss_is_fallback 置真, 共享 n_articles 分母)。相对同轨等权 canonical loughran_tone_ss, 本列对扎堆跟风报道降权。权重范式同 Tetlock (2007) 与 stage 24 herd_decay 配套。留篇门控 full-only, 本列为 conditional-on-full 子集加权均值。它与 hw_full/hw_ctx 构成跟风衰减加权三轨梯子, 与 vw/mw/等权变体各自 just-identified 并排、互为稳健性、不分主次, 严禁不同加权或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同 canonical, ss 轨缺失/回退与 herd 分母缺失叠加, 开发期尤不稳定, 以生产语料实读为准。

## VAR: loughran_tone_tech_full

【变体差分】
用大白话说, 金融科技报道大致可分两类: 一类讲底层使能技术 (系统、算法、基础设施等看不见的"发动机"), 一类讲面向客户的应用业务 (产品、场景等看得见的"车")。本列只在被判为"底层技术"的报道上量语调, 回答"关于本行底层技术的报道有多正面", 与应用子集对照就能看出两类报道的语调是否系统不同, 这正是落点异质性主线关心的问题。

本列是 full 轨上"底层技术落点 (tech-locus)"报道子集的语调条件均值。它只在被分类为创新落点=底层使能技术 (innovation_locus 底层技术) 的报道子集上取 loughran_score_full 的 bank-year 均值, 度量"关于该银行底层金融科技技术 (如系统、算法、基础设施) 报道"的情感。创新落点二分框架取自 Gomber et al. (2018): 把金融科技创新分为面向底层的使能技术与面向客户的应用业务两类。相对 canonical 的全篇等权均值 loughran_tone_full, 本列施加子样本选择 (仅 tech-locus 篇), 覆盖率显著更低 (盘上缺失率约九成), 与 app 子集列构成落点异质性梯子, 可支撑"技术类与应用类报道语调是否系统不同"的分层假设 (P4 locus 主线)。留篇门控 full-only, 子集在 full 轨留篇集合内按 locus 分类切分。本列与 tech_ctx/tech_ss、与 app 子集列各自 just-identified 并排、互为稳健性、不分主次, 严禁不同子集或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与逐篇归一化口径同 canonical, 仅按创新落点分层且样本量小, 年内篇数不足格 (min-n 门槛) 时置 NaN。

## VAR: loughran_tone_tech_ctx

【变体差分】
用大白话说, 本列在"聚焦本行的上下文"上只挑"底层技术"类报道来量语调。它与 tech_full 只差读全文还是读上下文窗口, 与同轨全篇列的差别在于只取技术落点子集, 因此样本较稀、覆盖率更低, 主要用作技术类报道语调的稳健性参照。创新落点二分框架取自 Gomber et al. (2018), 把金融科技创新分为面向底层的使能技术与面向客户的应用业务两类; 落点分类由 LLM 多模型在实体上下文轨判定, 留篇门控 full-only, 本列为 conditional-on-full 子集内再按 locus 分层, 年内篇数不足 min-n 门槛时置 NaN。

本列是 ctx 轨 (标题+银行实体上下文窗口) 上底层技术落点报道子集的语调条件均值。它在 ctx 轨文本打分、且报道创新落点分类为底层技术的子集上取 bank-year 均值。相对 tech_full, 差别在文本轨道 (上下文窗口而非全文); 相对同轨全篇 canonical loughran_tone_ctx, 本列施加 tech-locus 子样本选择。落点框架同 Gomber et al. (2018)。留篇门控 full-only, 本列为 conditional-on-full 子集内再按 locus 分层。它与 tech_full/tech_ss、与 app 子集列各自 just-identified 并排、互为稳健性, 严禁不同子集或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同家族 canonical, 样本量小 (缺失率高)、年内篇数不足格时置 NaN, 以生产语料实读为准。

## VAR: loughran_tone_tech_ss

【变体差分】
用大白话说, 本列在最严格的同句共现语境上只挑"底层技术"类报道来量语调, 是技术落点里语境最纯、样本最稀的一格。同句叠上技术子集后常因年内篇数不足格而置空, 只作参照, 与 tech_full/tech_ctx 交叉印证技术类报道语调是否稳健。创新落点二分框架取自 Gomber et al. (2018); 本轨文本证据最窄, 无同句共现时回退全文 body 并标记 ss_is_fallback、与 full 共享 n_articles 分母, 落点分层叠加同句约束后样本极稀, 数值以生产语料实读为准。

本列是 ss 轨 (银行与金科同句共现轨) 上底层技术落点报道子集的语调条件均值。它在 ss 轨文本打分、报道创新落点为底层技术的子集上取 bank-year 均值。相对 tech_full/tech_ctx, 本列文本证据最窄 (同句窗口), 回退语义镜像 ctx (无同句共现回退全文 body, ss_is_fallback 置真, 共享 n_articles 分母)。相对同轨全篇 canonical loughran_tone_ss, 本列施加 tech-locus 子样本选择。落点框架同 Gomber et al. (2018)。留篇门控 full-only, 本列为 conditional-on-full 子集内再按 locus 分层。它与 tech_full/tech_ctx、与 app 子集列各自 just-identified 并排、互为稳健性、不分主次, 严禁不同子集或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同 canonical, ss 轨叠加 tech 子集后样本极稀, 年内篇数不足格时置 NaN, 以生产语料实读为准。

## VAR: loughran_tone_app_full

【变体差分】
用大白话说, 本列只在被判为"应用场景"类 (面向客户的产品与业务) 的报道上量语调, 回答"关于本行金融科技应用的报道有多正面"。应用类报道通常比底层技术类更常见, 故本列覆盖率高于 tech 子集; 它与技术子集的语调差, 正是落点异质性主线 (配套 tone_gap_tech_app 语调差距) 关心的对象。创新落点二分框架取自 Gomber et al. (2018) 对金融科技创新的底层技术与应用业务二分; 若两类报道语调系统不同 (如应用类更乐观、技术类更审慎), 便提示媒体对"看得见的产品"与"看不见的底座"存在差别化叙事, 这一异质性正是主线 P4 假设的检验对象。

本列是 full 轨上"应用场景落点 (app-locus)"报道子集的语调条件均值。它只在创新落点分类为面向客户的应用业务 (innovation_locus 应用场景) 的报道子集上取 loughran_score_full 的 bank-year 均值, 度量"关于该银行金融科技应用/产品/业务报道"的情感。落点二分框架同 Gomber et al. (2018)。相对 canonical 全篇等权均值 loughran_tone_full, 本列施加 app-locus 子样本选择; 相对 tech 子集列, 本列覆盖的是应用侧报道 (盘上覆盖率高于 tech 子集, 因应用类报道更常见), 二者构成落点异质性对照 (P4 locus 主线, 与 tone_gap_tech_app 语调差距配套)。留篇门控 full-only, 子集在 full 轨留篇集合内按 locus 切分。本列与 app_ctx/app_ss、与 tech 子集列各自 just-identified 并排、互为稳健性、不分主次, 严禁不同子集或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与逐篇归一化口径同 canonical, 仅按创新落点分层, 年内篇数不足格时置 NaN。

## VAR: loughran_tone_app_ctx

【变体差分】
用大白话说, 本列在"聚焦本行的上下文"上只挑"应用场景"类报道来量语调。它与 app_full 只差读全文还是读上下文窗口, 与同轨全篇列的差别在于只取应用落点子集, 主要用作应用类报道语调的稳健性参照。创新落点二分框架取自 Gomber et al. (2018); 落点分类由 LLM 多模型判定, 留篇门控 full-only, 本列为 conditional-on-full 子集内再按 locus 分层, 年内篇数不足 min-n 门槛时置 NaN, 与 app_full/app_ss 组成应用落点的三轨梯子、三轨各自 just-identified 并排互为稳健性, 禁混同一 over-identified Hansen J, 词典与逐篇归一化口径同家族 canonical, 数值以生产语料实读为准。

本列是 ctx 轨 (标题+银行实体上下文窗口) 上应用场景落点报道子集的语调条件均值。它在 ctx 轨文本打分、报道创新落点为应用场景的子集上取 bank-year 均值。相对 app_full, 差别在文本轨道 (上下文窗口而非全文); 相对同轨全篇 canonical loughran_tone_ctx, 本列施加 app-locus 子样本选择。落点框架同 Gomber et al. (2018)。留篇门控 full-only, 本列为 conditional-on-full 子集内再按 locus 分层。它与 app_full/app_ss、与 tech 子集列各自 just-identified 并排、互为稳健性, 严禁不同子集或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同家族 canonical, 仅轨道与子集与 canonical 不同, 年内篇数不足格时置 NaN, 以生产语料实读为准。

## VAR: loughran_tone_app_ss

【变体差分】
用大白话说, 本列在最严格的同句共现语境上只挑"应用场景"类报道来量语调, 是应用落点里语境最纯的一格。同句叠上应用子集后样本较稀, 年内篇数不足格时置空, 只作参照, 与 app_full/app_ctx 交叉印证应用类报道语调是否稳健。创新落点二分框架取自 Gomber et al. (2018); 本轨文本证据最窄, 无同句共现时回退全文 body 并标记 ss_is_fallback、与 full 共享 n_articles 分母, 落点分层叠加同句约束后覆盖率进一步下降, 数值以生产语料实读为准。

本列是 ss 轨 (银行与金科同句共现轨) 上应用场景落点报道子集的语调条件均值。它在 ss 轨文本打分、报道创新落点为应用场景的子集上取 bank-year 均值。相对 app_full/app_ctx, 本列文本证据最窄 (同句窗口), 回退语义镜像 ctx (无同句共现回退全文 body, ss_is_fallback 置真, 共享 n_articles 分母)。相对同轨全篇 canonical loughran_tone_ss, 本列施加 app-locus 子样本选择。落点框架同 Gomber et al. (2018)。留篇门控 full-only, 本列为 conditional-on-full 子集内再按 locus 分层。它与 app_full/app_ctx、与 tech 子集列各自 just-identified 并排、互为稳健性、不分主次, 严禁不同子集或轨道混入同一 over-identified Hansen J [CLAUDE.md 铁律]。词典与归一化口径同 canonical, ss 轨叠加 app 子集后样本较稀, 年内篇数不足格时置 NaN, 以生产语料实读为准。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Hsiu-Min Chuang, Hsiang-Chih He, Ming-Che Hu. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Lingyun Yang, Zhihong Zhang, Lulu Wang, Yikai Liang. (2025). Encourage or inhibit: A study on the impact of corporate digital transformation on management's tone manipulation of information disclosure. PLOS ONE. https://doi.org/10.1371/journal.pone.0317503
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Goldstein, I. (2023). Information in financial markets and its real effects. Review of Finance, 27(1), 1-32. https://doi.org/10.1093/rof/rfac052
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Algaba, A., Ardia, D., Bluteau, K., Borms, S., & Boudt, K. (2020). Econometrics meets sentiment: An overview of methodology and applications. Journal of Economic Surveys, 34(3), 512-547. https://doi.org/10.1111/joes.12370
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
Loughran, T., & McDonald, B. (2023). Measuring Firm Complexity. Journal of Financial and Quantitative Analysis. https://doi.org/10.1017/S0022109023000716
Sheetal, R., & Aithal, P. K. (2025). Enhancing Financial Sentiment Analysis: Integrating the LoughranMcDonald Dictionary with BERT for Advanced Market Predictive Insights. Procedia Computer Science [Working Paper]. https://doi.org/10.1016/j.procs.2025.04.477
<!-- rendered-citations:end -->
