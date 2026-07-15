---
family_id: F263
novelty_exempt_rationale: "停刊稳健性(exc_)与词典规则消融(negonly)双重交叉的技术变体家族, 测度定义依据母族姜富伟(2021)词典与消融梯度框架, 非独立新构念, 无需追加新文献。"
columns:
- exc_jiang_2021_score_negonly_ctx
- exc_jiang_2021_score_negonly_full
- exc_jiang_2021_score_negonly_ss
unit: 情感倾向分值 (无量纲, 自归一化, 值域约束于 [-1, 1])
formula: "exc_jiang_2021_score_negonly{track} = mean_文章 i 所属媒体的 _is_ceased_media_i 取 0 (即非疑似退出媒体) jiang_2021_score_negonly{track}_i, 按 (target_bank, year) 分组; 其中文章级 jiang_2021_score_negonly = Σ(final_score) / Σ|final_score|, final_score = base_weight × degree_multiplier(锁1.0) × negation_sign × adversative_multiplier(锁1.0), 即仅启用否定翻转规则 (negation-only rule ablation) 的幅度加权自归一化得分, 程度副词与转折规则关闭 (非裸计数比率 (pos-neg)/(pos+neg), 后者是另一口径 msent_negonly 的定义, 两者不可混用)"
producer: news_process/pipeline/panel/attention_media.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- "22_tone_words.parquet (article: jiang_2021_score_negonly_full / _ctx / _ss)"
- "40_panel_export_main (attention_media: detect_defacto_cessation → _is_ceased_media)"
citations:
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
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
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: China Economic Quarterly
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
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  issue: null
  pages_or_artno: 67-75
new_dois: []
---

## CORE

【构念与来源】
本家族测度的是"排除疑似退出覆盖媒体后, 以姜富伟等 (2021) 中文媒体情绪词典重算、且仅保留否定翻转规则的银行年度情感倾向"。它同时叠加两层限定: 其一是词典与规则层, 底层文章级度量 jiang_2021_score_negonly 采用姜富伟等 (2021) 为中国媒体文本构建的金融情感词典, 并在三条语言学规则 (否定翻转、程度副词加权、转折削减) 中只启用否定翻转一条, 关闭其余两条, 属规则消融梯度里的 negonly 变体; 其二是样本层, exc_ 前缀表示在做银行年度聚合时把"疑似退出覆盖媒体"的报道从分母中保守剔除, 只对存活媒体的报道求均值, 用以检验幸存者偏差 (survivorship bias) 是否驱动主结论。构念上它不是一个新的情绪信号, 而是主情绪信号在"更严格样本 + 更简约规则"双重约束下的稳健性投影, 服务于系数稳定性检验而非独立识别。

【方法学与计算】
计算分两步。第一步在文章级词典打分阶段 (stage 22) 完成: 对每个匹配到的情感词, 先取其在姜富伟等 (2021) 词典中的基础权重 base_weight (逐词固定, 并非统一取一), 再乘以程度副词倍率 degree_multiplier、否定翻转符号 negation_sign、转折放大倍率 adversative_multiplier 得到该词的加权贡献 final_score; negonly 变体只让否定翻转规则生效 (情感词落入否定词辖域时 negation_sign 翻号), 程度副词倍率与转折倍率一律锁定为 1.0 (语言学层面等同关闭该两条规则, 但底层 token 扫描仍保留程度/转折词的识别与句末重置骨架, 只是不产生数值放大效应); 文章级得分按自归一化式 jiang_2021_score_negonly = Σ(final_score) 除以 Σ|final_score| 计算, 分子分母均是逐词加权幅度的求和而非裸计数, 结果恒落在负一到正一的闭区间, 三轨各算一列。该式与仅在裸计数 (pos 减 neg) 除以 (pos 加 neg) 上做否定翻转的另一口径 msent_negonly 是两套不同公式, 数值不可互相替代或比较水平, 二者虽同为"仅否定"消融但一为幅度自归一化、一为计数比率, 项目口径明确要求不可混用。第二步在面板导出的 attention_media 环节完成: 先由 detect_defacto_cessation 依"话题覆盖退出"这一保守代理判定每篇报道来源是否疑似停止覆盖 (打上 _is_ceased_media 标记), 再对 _is_ceased_media 等于零 (即存活媒体) 的子集, 按目标银行与年份分组, 对文章级 jiang_2021_score_negonly 求算术均值, 得到 exc_jiang_2021_score_negonly。需强调该"停刊"实为话题覆盖退出的保守代理, 媒体可能仍正常出版而只是不再报道该主题, 因此下游不可在论文中表述为严格意义上的报纸停刊口径。零文章银行年度按契约保持缺失而非零填 (与计数类列的零填契约刻意区分), 避免把"无观测"误读为"中性"。

【文献定位】
底层词典的权威出处是姜富伟等 (2021), 该文构建中文媒体情绪词典并证明其对股票回报的预测力, 是中文金融文本情绪测量的基础性工作。词典法与机器学习法孰优的方法学定位可锚 Frankel、Jennings 与 Lee (2022) 发表于 Management Science 的比较研究, 其结论支持在可解释性与稳健性场景下保留词典法作为并行测度。Du、Huang、Wermers 与 Wu (2022) 在 Review of Finance 提出的中文金融情感词典进一步论证了领域专用与语言专用词典对中文语料的必要性, 为本项目多词典并置提供合法性。基于词典的经济文本情绪测量的最新方法学综述见 Barbaglia 等 (2025)。否定处理是本家族 negonly 臂的核心, Pröllochs、Feuerriegel 与 Neumann (2016) 系统研究了新闻驱动交易中的否定辖域检测, 直接支撑"仅保留否定翻转规则"这一消融设定的理论意义。情感分析测度效度的多方法比较见 van Atteveldt 等 (2021); 机器可读时代的公司披露文本测度背景见 Cao、Jiang、Yang 与 Zhang (2023) 发表于 Review of Financial Studies 的研究。停刊稳健性设计的因果动机可追溯至报纸关停削弱地方媒体监督的实证文献。

【识别与稳健性口径】
本家族属规则消融梯度与停刊稳健性两条正交稳健性轴的交叉产物。按项目铁律, 词典消融梯度的七个规则变体 (raw、negonly、degonly、advonly、negdeg、negadv、degadv) 各自自归一化、互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 各变体间高度共线 (相关系数常近 0.99), 属规格稳健性并置而非可加分解。三轨 (full/ctx/ss) 同样各自 just-identified 并排、互为稳健性、不分主次、禁混同一 over-identified Hansen J; 其中 ss 轨回退语义镜像 ctx 轨, 无银行与金科同句共现时 content_ss 退回全文正文。exc_ 停刊稳健性与 bal_ 平衡媒体口径共同构成媒体样本组成的稳健性梯子, 二者与主口径 (含全部媒体) 亦为并排稳健性而非替代。银行年度留篇是否成立仍由 full 轨的 llm_verified_full 门控 (full-only 口径, 2026-06-29), ctx/ss 为 conditional-on-full 测度轨。

## VAR: exc_jiang_2021_score_negonly_ctx

【变体差分】
本列是三轨中的 ctx (实体上下文窗口) 轨。相对家族无隐含 canonical 的三轨并置, 本列的文章级底层输入是 jiang_2021_score_negonly_ctx, 即在 content_ctx (标题 prepend 后拼接目标实体邻近窗口文本, 而非整篇正文) 上做词典打分。ctx 轨的动机是把情感信号收敛到与目标银行实体真正邻近的语境, 削弱整篇长文里与银行无关段落对词典计数的稀释与污染。规则层与 full、ss 两轨完全一致: 仍只启用否定翻转规则 (negation_sign 生效), 关闭程度副词加权与转折削减 (degree_multiplier、adversative_multiplier 均锁 1.0), Σ(final_score) 除以 Σ|final_score| 的幅度加权自归一化式不变。样本层的停刊剔除逻辑亦与另两轨同构, 均对 _is_ceased_media 等于零的存活媒体子集按银行年度求均值。按项目铁律, 本 ctx 轨与 full、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨禁混进同一 over-identified Hansen J。在留篇门控上, ctx 轨为 conditional-on-full 测度轨, 其行宇宙是 full 留篇集的子集, 但 per-track 列照常在该子集上逐轨计算, 分子分母严格取自 ctx 轨自身而不借用 full 轨口径。与本家族 full 轨相比, ctx 轨在词典计数上通常匹配到更少的情感词, 因此自归一化分母更小, 单篇得分对个别词的极性判定更敏感; 这一敏感性正是把 ctx 与 full 并置作稳健性对照的价值所在, 若两轨系数方向与显著性一致, 则可佐证情绪信号并非由无关正文段落的噪声词堆积驱动。此外 ctx 轨与 exc_ 停刊剔除的交互意味着本列同时承受"语境收窄"与"样本收窄"两重约束, 是对主口径最保守的一档稳健性检验。dev 环境 T=2 上该列可能因样本稀薄呈现零方差或缺失, 属预期退化, 生产 T=18 语料下方为常态。

## VAR: exc_jiang_2021_score_negonly_full

【变体差分】
本列是三轨中的 full (标题加全文正文) 轨。其文章级底层输入是 jiang_2021_score_negonly_full, 即在 content_full (标题 prepend 后拼接整篇正文) 上做姜富伟等 (2021) 词典打分, 覆盖报道的全部可见文本, 是三轨中信息量最全、也最易受与银行无关段落稀释的轨道。规则层与另两轨一致, 仅启用否定翻转规则 (negation_sign 生效), 程度副词与转折规则关闭 (degree_multiplier、adversative_multiplier 均锁 1.0), 自归一化式为逐词加权幅度之和 Σ(final_score) 除以其绝对值之和 Σ|final_score|, 而非裸计数比率。样本层同样对存活媒体 (_is_ceased_media 等于零) 子集按目标银行与年份求均值, 剔除疑似退出覆盖的媒体报道。在项目口径中, full 轨承担银行年度留篇门控职责: 是否判为一篇银行金科报道只看 full 轨的 llm_verified 结果 (full-only 口径, 2026-06-29), 因此 full 轨是三轨中唯一决定行宇宙成立与否的轨道, ctx 与 ss 轨降为 conditional-on-full 测度与稳健性轨。尽管如此, full 轨在稳健性并置意义上并不比 ctx、ss 两轨"更主": 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。因文本覆盖最全, full 轨的词典匹配词数通常最多, 自归一化分母最大, 单篇得分对个别情感词最不敏感, 因而在三轨中最平滑、最接近整篇报道的整体情感基调; 这也使其成为与 ctx、ss 两轨对照时的"全文参照臂"。本列亦是同一停刊稳健性 exc_ 前缀下 jiang_2021 negonly 变体最完整文本口径的稳健性检验列, 与非停刊剔除的主口径对应列并排, 用以证明主结论不被疑似退出覆盖媒体的幸存者偏差驱动。

## VAR: exc_jiang_2021_score_negonly_ss

【变体差分】
本列是三轨中的 ss (银行与金科同句共现窗口) 轨。其文章级底层输入是 jiang_2021_score_negonly_ss, 即在 content_ss 上做词典打分。content_ss 只保留目标银行与金融科技词在同一句子及前后正负一句窗口 (由 config 的 ss_sentence_radius 控制, 默认一句) 内共现的文本, 是三轨中语境最窄、最贴近"银行谈金科"这一目标事件的轨道。其关键特性是回退语义: 当某报道不存在银行与金科同句共现时, content_ss 回退为全文正文, 并把 ss_is_fallback 置真, 该回退镜像 ctx 轨的降级逻辑; 若金科词表整体为空 (FINTECH_AC 为 None), 则 fallback 标记全真, 属优雅降级。规则层与 full、ctx 一致, 仅启用否定翻转规则。样本层同样对存活媒体子集按银行年度求均值。按项目铁律, ss 轨与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 三轨禁混进同一 over-identified Hansen J; ss 轨为 conditional-on-full 测度轨, 行宇宙是 full 留篇集的子集。由于 ss 轨语境最窄且带回退机制, 其得分在无共现时与 ctx、full 轨趋同 (共享全文正文), 在有共现时则聚焦于最相关句子, 因此本列既非纯粹的窄窗测度也非纯全文测度, 而是两种口径的加权混合, 其权重由语料中银行与金科同句共现的比例内生决定。这一特性使 ss 轨在三轨稳健性并置中扮演"最贴题但样本最稀"的一档, 与 exc_ 停刊剔除叠加后成为语境与样本双重最严的检验列。dev T=2 上因同句共现样本极稀, 本列常呈零方差或大面积缺失, 属预期退化, 生产 T=18 语料下方为常态观测。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. China Economic Quarterly, 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
<!-- rendered-citations:end -->
