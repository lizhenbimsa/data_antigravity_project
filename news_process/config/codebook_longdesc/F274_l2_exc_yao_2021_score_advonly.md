---
family_id: F274
columns:
- exc_yao_2021_score_advonly_ctx
- exc_yao_2021_score_advonly_full
- exc_yao_2021_score_advonly_ss
unit: 无量纲情感得分 (bank-year 聚合均值, 值域约 [-1, +1]; 排除疑似退出覆盖媒体子样本; 仅转折规则消融变体)
formula: "exc_yao_2021_score_advonly{track} = mean_{i in bank-year, media not ceased}( yao_2021_score_advonly{track}_i ); 其中 yao_2021_score_advonly 是姚加权等 (2021) 词典在仅启用转折 (adversative) 规则、否定翻转与程度副词加权均关闭的条件下算出的文章级归一化语调; track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (detect_defacto_cessation + C.4 exc_* 动态聚合); 文章级 yao_2021_score_advonly 由 news_process/pipeline/sentiment/tone_words.py::classify_batch 经 _RULE_ABLATION_VARIANTS 谱 (advonly=(False,False,True)) 调用 _compute_sentiment_with_rules 产出
upstream:
- 22_tone_words.parquet (yao_2021_score_advonly{track} 文章级仅转折规则消融得分)
- 40_article_bank_level.parquet (_is_ceased_media 退出媒体标记)
citations:
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
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
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是"在剔除疑似退出覆盖的媒体之后, 目标银行当年金融科技相关报道所呈现的字典法情感语调水平, 且该语调只由转折 (adversative) 语言学规则单独驱动"。它把两条正交的稳健性线索叠合在同一列上: 第一条是样本侧的退出媒体剔除, 前缀 exc_ 标示 "excluding ceased media" —— 在样本期内疑似停止覆盖该话题的媒体来源被整体移出聚合分母, 只保留仍在持续覆盖的"存活"媒体所贡献的报道, 目的是防止媒体进入退出造成的样本构成变动 (composition change) 冒充银行基本面或情绪的真实变化。第二条是词典侧的规则消融, advonly 后缀标示本列取自 v3.11.1 引入的语言学规则全 powerset 消融梯度 (`_RULE_ABLATION_VARIANTS`) 中的"仅转折"档位: 姚加权等 (2021) 中文金融情感词典 (yao_2021, 本项目并列装载的六部中文金融情感词典之一, jiang_2021/yao_2021/bian_2021/du_2022/you_2018/loughran 中文主译本互为稳健性、不分主次) 在打分时通常叠加三条语言学规则——否定翻转、程度副词加权、转折加权——而本列刻意关闭否定翻转 (apply_negation=False) 与程度副词加权 (apply_degree=False), 只保留转折规则 (apply_adversative=True) 参与计算, 从而把"转折结构单独对语调合成的边际作用"从其余两条规则中分离出来考察。之所以要构造这样一条窄口径的消融列, 是因为主语调测度 (无后缀 yao_2021_score) 同时叠加三条规则, 若三者中任一条对结果驱动过强, 主结论就可能对该规则的具体实现方式过度敏感; 全 powerset 消融梯度 (raw/negonly/degonly/advonly/negdeg/negadv/degadv, 加上叠满三规则的 full) 逐一开关规则组合, 使研究者能诊断主语调对每一条规则单独及组合的敏感性, 论文表述的目标是证明"定性结论不变", 而非声称某一消融变体更优越。

【方法学与计算】
计算分三层, 与家族其余同源家族 (如无消融后缀的 exc_yao_2021_score) 共享同一聚合骨架, 差异集中在文章级打分环节。第一层是文章级词典打分: tone_words.py 的 classify_batch 对每篇报道逐轨调用 _compute_sentiment_with_rules, 在分词后遍历命中词, 对每个情感词取其基准极性得分; 本列对应的调用把 apply_negation 与 apply_degree 均锁为 False、apply_adversative 锁为 True——否定词与程度副词的识别、continue 分支与窗口递减骨架仍然保留 (与其余消融变体共享同一 scoping 机制, 只是数值效应被锁), 但否定不翻号、程度倍率恒为 1.0, 只有命中转折词 (adversative words, 如"但是""然而"类连接词) 时才对被强调分句内的情感词施加 ADVERSATIVE_BOOST 倍率放大。逐词最终贡献累加为 total_score, 归一化得分 = total_score / Σ|final_score| ∈ [-1, +1], 即以本变体自身的加权幅度和为分母做自归一化 (self-normalize), 而非借用全规则档的分母——这意味着七个消融变体 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 与叠满三规则的 full 各自独立归一化, 相邻档位之差并非可加分解的"某规则纯贡献" (审计口径 MATH-1): 否定与程度作用于同一词时倍率是乘在翻转后幅度上的, 含交互项, 且分母本身随启用规则集合变化而变化, 因此本列与 full 列之差不能解读为"转折规则的独立边际效应", 只能作为消融稳健性对照读数, 实测 corr(full, 各消融变体) 高度共线 (corr≈0.99 量级)。第二层是退出媒体识别: attention_media.py 的 detect_defacto_cessation 以"话题覆盖退出"为停刊的保守代理, 取数据实测退出与 NPPA 名录交叉验证的并集, 标记 _is_ceased_media, 这是覆盖退出而非经证实的出版停刊, 论文表述须用保守稳健性口径而非严格停刊口径。第三层是 bank-year 聚合: compute_media_heterogeneity 在存活媒体子样本 (df_alive) 上按 (target_bank, year) 对文章级 yao_2021_score_advonly{track} 取均值, 动态发现以情感前缀开头的列并生成对应 exc_* 输出; 缺样本格保持 NaN (不零填), 避免把"该银行当年无存活媒体报道"误读为语调为零。

【文献定位】
词典法情感测度的方法学根基在 Taboada 等 (2011) 系统阐述的基于词典的情感分析框架中, 该文明确指出否定、程度副词与转折结构 (valence shifters) 是极性合成中三类相互独立、须分别刻画的语言学机制, 是本项目三条规则及其全 powerset 消融梯度的直接方法论原型——本列正是把该框架中的转折机制单独隔离出来做敏感性检验。就中文金融语域而言, Du 等 (2022) 指出通用情感词典迁移到专业金融语境会失真, 论证了领域与语言双重专用的中文金融情感词典 (如本家族依托的 yao_2021) 有必要与其它词典并列互为稳健性, 也间接支持了本项目在规则层面同样做穷举消融而非只信任单一规则组合的研究设计。van Atteveldt 等 (2021) 系统比较人工标注、众包编码、词典法与机器学习算法的效度, 强调任何单一情感测度都需要交叉验证——这一提醒不仅适用于词典/LLM/BERT 三法并置的宏观架构, 也适用于词典内部规则层面的消融梯度: 本列即是把交叉验证原则下沉到"规则粒度"的产物。Frankel 等 (2022) 以机器学习与词典法的直接对照说明词典法在可解释性与可复现性上的比较优势, 但也提示词典法结果对具体规则实现较为敏感, 这正是本项目构造 raw/negonly/degonly/advonly/negdeg/negadv/degadv 全消融梯度、以经验方式而非先验假设去检验该敏感性的直接动机。exc_ 前缀所代表的退出媒体剔除设计, 呼应了媒体覆盖进入退出会系统性改写被报道主体信息环境结构这一支实证文献的关切, 在本列中与规则消融两条正交稳健性线索叠加, 共同构成"样本构成 × 打分规则"二维稳健性网格的一个格点。

## VAR: exc_yao_2021_score_advonly_full

【变体差分】
本列是家族内的参照读数: full 轨、仅转折规则消融。full 轨的文本口径 = 标题 prepend 到全文正文, 是留篇门控的判定基准——一篇报道是否算作"银行金科报道"由 full 轨 LLM 判定 (llm_verified_full, 2026-06-29 full-only 口径确立), ctx/ss 是 conditional-on-full 的子集轨, 因此 full 轨的行宇宙即留篇集本身。文章级打分调用 _compute_sentiment_with_rules(tokens, yao_2021_dict, apply_negation=False, apply_degree=False, apply_adversative=True), 归一化得分再在剔除疑似退出覆盖媒体后的存活媒体子样本上按 bank-year 取算术均值 (等权, 不叠加 herd_weight 或 mention_density 加权——本消融梯度不与 hw/w 加权维度交叉, 避免规则消融 × 加权 × 三轨三维网格进一步膨胀)。相对家族其它两列, 本列的区别仅在轨道: full 取最宽文本, 信噪比最高但可能掺入与银行金科主题弱相关的段落。三轨 (full/ctx/ss) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同轨的同名消融列混入同一 over-identified Hansen J 方程。本列宜作为该家族在回归中的首要读数, ctx/ss 两列是围绕它的文本轨道稳健性梯子, 而家族之外的 raw/negonly/degonly/negdeg/negadv/degadv/full(全规则) 诸消融档位构成规则维度的正交梯子, 两条梯子 (轨道 × 规则) 相互正交、不交叉, 不应把不同规则消融档位的同轨列硬凑进同一回归右端。需特别提示: 由于转折词在中文金融报道中出现频率显著低于否定词与程度副词, advonly 档在覆盖率上通常是七个非-full 消融变体中最稀疏的一档, 大量文章可能因未命中任何转折词而使 ADVERSATIVE_BOOST 从未触发、退化为等同于零规则 raw 档的打分; 这一退化是构念内生的 (转折结构本身在文本中确实稀少), 不代表实现缺陷, 论文披露稳健性梯度时应报告 advonly 与 raw 两档的相关系数与逐篇变号占比, 而非仅报告 advonly 与 full 的相关系数。

## VAR: exc_yao_2021_score_advonly_ctx

【变体差分】
本列与参照列 exc_yao_2021_score_advonly_full 的唯一差异在文本轨道: 由 full 改为 ctx。ctx 轨 = 标题 prepend + 实体上下文窗口, 即只保留标题加上目标银行实体附近的局部文本 (而非全文), 在 stage 14 ctx_materializer 物化为 content_ctx。其构念用意是把语调计算聚焦到"确实谈及该银行"的局部, 剔除全文中与银行金科弱相关的背景段落对情感的稀释或污染, 相对 full 轨更保守, 代价是可用文本更短、方差更大。文章级打分同样只启用转折规则 (apply_negation=False, apply_degree=False, apply_adversative=True), 在 ctx 超级文档上独立分词计算, 归一化分母 Σ|final_score| 也在 ctx 文本范围内自算, 不借用 full 轨的分母或得分。聚合口径与 full 列一致: 在剔除疑似退出覆盖媒体后的存活媒体子样本上按 bank-year 取均值。ctx 轨在 full-only 门控下降为 conditional-on-full 的稳健性测度轨, 其行宇宙是 full 留篇集的子集, per-track 列照常计算。本列与 full/ss 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混入同一 over-identified Hansen J; 它同时叠加了两层稳健性问题: "把情感读取范围收窄到银行实体上下文后"以及"只保留转折规则打分后", 剔除退出媒体的语调结论是否依然成立。由于 ctx 窗口本身文本量远短于 full 全文, 而转折词在中文金融报道中出现频率又显著低于否定词与程度副词, 二者叠加使 advonly_ctx 成为本家族三轨消融读数中样本内命中率最低、方差最大的一格: 相当比例的报道在其实体上下文窗口内根本不含转折连接词, 导致 ADVERSATIVE_BOOST 从未触发、逐篇打分退化为等同于零规则的 raw 档水平, 这是构念内生的稀疏性而非实现缺陷。论文披露该列时应同时报告与同轨 raw 档、以及与 full 轨 advonly 档的相关系数与逐篇变号占比, 并结合样本量说明退化格点的占比, 不宜单独依据本列的点估计做强结论, 而应将其作为轨道稳健性梯子上的一个佐证读数看待。

## VAR: exc_yao_2021_score_advonly_ss

【变体差分】
本列与参照列的差异同样在文本轨道: 取 ss (同句共现) 轨。ss 轨 = 标题 prepend + 目标银行与金融科技词在同一句子内共现的窗口 (句半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 ±1 句), 是三轨中最严格的文本口径, 只在银行与金科概念真正同句耦合处读取语调, 力图刻画"银行—金科"这一特定关系上的情感, 而非银行泛报道情感。ss 的回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True; 当金科 AC 自动机为 None 时该轨全部优雅降级。因此 ss 轨在稀疏语料 (如盘上 T=2 开发样本) 上可能大量回退甚至零方差退化, 属预期行为, 生产 T=18 语料下才充分展开。文章级打分同样只保留转折规则 (apply_negation=False, apply_degree=False, apply_adversative=True), 归一化分母在 ss 超级文档范围内自算; 聚合仍限于剔除退出媒体后的存活媒体子样本, bank-year 取均值。ss 与 full/ctx 互为稳健性、不分主次, 各自 just-identified 并排, 禁混入同一 over-identified Hansen J。本列同时回答两层稳健性问题: "把语调读取收紧到银行与金科同句关系上后"以及"打分规则只保留转折机制后", 退出媒体剔除的结论是否稳健——是本家族中约束最强、最易在小样本下呈现回退与零方差退化的一格。

<!-- rendered-citations:begin -->
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
