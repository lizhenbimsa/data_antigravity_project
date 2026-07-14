---
family_id: F285
novelty_exempt_rationale: "该家族是 you_2018 词典情感打分在语言学规则消融梯度 (_RULE_ABLATION_VARIANTS) 下的 degonly (仅程度副词加权) 技术变体, 测度定义与文献依据已在母族 you_2018 词典及其规则消融梯度正文中给出, 非独立新构念, 不需单独追新文献。"
columns:
- exc_you_2018_score_degonly_ctx
- exc_you_2018_score_degonly_full
- exc_you_2018_score_degonly_ss
unit: 无量纲情感得分 (文章级, 自归一化 ∈ [−1, 1]; 缺词典或空文本记 NaN)
formula: "exc_you_2018_score_degonly = Σ(final_valence) / Σ|final_valence|, 其中 final_valence 由 you_2018 词典在 apply_negation=False、apply_degree=True、apply_adversative=False 规则下计算 (degonly = 仅程度副词加权, 关闭否定翻转与转折增强); 逐 track 各算一列"
producer: news_process/pipeline/sentiment/tone_words.py::_analyze_single_article (调用 _compute_sentiment_with_rules; 变体谱 _RULE_ABLATION_VARIANTS 之 'degonly')
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
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
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
new_dois: []
---

## CORE

【构念与来源】
本家族测度的是文章级词典情感得分, 词典底本取自 You、Zhang 与 Zhang (2018) 发表于 The Review of Financial Studies 的中文金融情感词典。该文以"谁掌握了媒体之笔"为题, 研究媒体报道对上市公司信息环境的塑造机制, 在实证过程中构造并公开了一套面向中文财经文本的情感词表, 区分语义确定 (definite) 与语义歧义 (ambiguous) 两个 Panel。本项目在 tone_words 阶段加载 you_2018 词表的正负极性词, 对每篇报道计算带语言学规则的情感倾向分, 并以 self-normalize 口径压缩到 [−1, 1] 区间。列名前缀 exc 标记该分值属于文章级去伪存真 (排除已停业主体) 命名域下的词典打分块, 与面板层聚合列 you_2018_degonly_tone 一一对应但口径不同: 前者是逐篇原始分, 后者是银行-年层的篇均聚合, 二者不可互相替代或混用于同一回归设定。

【方法学与计算】
计分内核 _compute_sentiment_with_rules 是一台确定性有限状态机, 依次可施加三条中文情感语言学规则: 否定翻转 (遇否定词对随后极性词变号)、程度副词六级加权 (极其/非常/较/稍等程度词按连续档位放大或衰减极性值)、转折增强 (遇但是/然而等转折连词对其后子句极性做增强)。本家族对应的 degonly 变体在规则消融梯度 (rule-ablation ladder, 单一事实源 _RULE_ABLATION_VARIANTS) 中定义为 apply_negation=False、apply_degree=True、apply_adversative=False, 即只保留程度副词加权这一条规则, 同时关闭否定翻转与转折增强, 用于单独检验"程度副词能否独立驱动情感强度"这一构念。每篇文本先经 jieba 冻结词典分词, 命中 you_2018 极性词后累加经程度加权后的极性值 final_valence, 分子为其代数和、分母为其绝对值之和, 从而得到自归一化的倾向分; 空文本或词典缺失时按与主分 you_2018_score 对称的规则回填 NaN 或 0.0, 不静默造零。需要强调的是, 规则消融梯度采用非可加分解: 每个变体各自 self-normalize, 分母随启用规则集变化, 且当程度词与本可被否定/转折修饰的极性词共现时, 不同规则组合下同一原始词的贡献权重并不线性可比, 因此相邻档位之间的级差并不代表"某条规则的纯贡献", 只能作为对照稳健性使用; 审计披露须报四级相关系数与逐级变号占比, 论文表述定性不变而非声称某变体更优。degonly 与其对偶变体 negonly (只留否定翻转) 及 advonly (只留转折增强) 共同构成"单规则隔离"三档, 用于把完整规则集拆解为可归因的最小单元, 与 negdeg/negadv/degadv 三档"双规则组合"互补, 覆盖 2³ 全消融梯度中的全部非空/非满子集。

【文献定位】
就构念谱系而言, 本家族坐落在中文金融文本情感词典测量这一方法学脉络上。You et al. (2018) 提供了词表底本与媒体报道信息含量的识别背景, 是本家族列名与构念的直接源头; Du et al. (2022) 在 Review of Finance 系统论证了中文金融情感的语言域特异性, 说明通用词表迁移到财经语料时须做本地化, 这正是本项目并置多部中文词典 (jiang_2021/yao_2021/bian_2021/du_2022/you_2018 等) 互为稳健性的动机。就规则内核而言, 程度副词效价移位 (valence shifting) 建模承接 Taboada et al. (2011) 在 Computational Linguistics 上系统化的词典法效价移位框架, degonly 变体正对应该框架中"intensification/downtoning"这一独立算子的隔离检验。近期方法学文献 Ma、Zhang 与 Zhang (2025) 在 Expert Systems with Applications 上构造面向中国境内投资者的细粒度中文情感词典, 同样强调程度修饰词与否定词须分别建模、不可笼统合并处理, 呼应本项目将三条语言学规则拆解为独立消融维度的设计思路。就方法学地位而言, Frankel、Jennings 与 Lee (2022) 在 Management Science 上对比机器学习与词典法披露情感的证据, 支持将词典法作为与 LLM、BERT 并列的第三条互为稳健性测量轨; van Atteveldt et al. (2021) 则从人工标注效度校验角度, 为词典分值 (含各消融档位) 的可信度提供外部佐证。本项目将规则消融各档位视为方法学稳健性梯子: 各档位各自 just-identified 并排、互为稳健性不分主次, 严禁把不同消融档位混进同一 over-identified 的 Hansen J 过度识别检验, 以免制造伪工具变量冗余。

## VAR: exc_you_2018_score_degonly_ctx

【变体差分】
本列是 degonly 消融变体 (仅程度副词加权, 关闭否定翻转与转折增强) 在实体窗轨 (ctx) 上的文章级分值。ctx 轨的文本 content_ctx 在 stage 14 ctx_materializer 物化, 由标题 prepend 后拼接目标实体上下文窗口构成, 相较全文轨只保留与银行/金融科技实体邻近的语段, 意在削弱与主体无关的噪声段落对情感计分的稀释。除文本轨不同外, 其规则设定与 full 轨严格一致: 只开启程度副词六级加权, 否定翻转与转折增强均关闭, 分子分母同为自归一化口径。ctx 轨与 full、ss 三轨互为稳健性、不分主次, 各自 just-identified 并排进入各自的规格, 严禁把三轨混入同一 over-identified Hansen J 过度识别检验。需注意留篇门控为 full-only 口径 (2026-06-29): 一篇报道是否计入银行金融科技报道宇宙只由 full 轨的 llm_verified_full 判定, ctx 轨为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 分值照其自身文本独立计算。ctx 文本因窗口收窄, 命中的程度副词-极性词搭配数通常少于 full 轨, 使本列相对更依赖局部而非全篇的语气强度; ctx 文本缺失或分词后无 you_2018 命中词时, 本列按与主分对称的缺失语义记 NaN, 不借用 full 轨分母造零。将 ctx 轨与 full 轨在 degonly 规则下并列比较, 可用于诊断"实体窗口收窄"对程度副词捕获率的边际影响, 属规格曲线式的稳健性审计而非替代关系。

## VAR: exc_you_2018_score_degonly_full

【变体差分】
本列是 degonly 消融变体在全文轨 (full) 上的文章级分值, 也是三轨中口径最完整、留篇门控所依据的那一轨。full 轨文本 content_full 由标题 prepend 后拼接原始正文全文构成, 覆盖整篇报道, 因此其 you_2018 命中词与程度副词触发次数通常多于 ctx、ss 两轨。规则设定为 degonly: 只开启程度副词六级加权, 关闭否定翻转与转折增强, 即在完整三规则之上单独剥离否定与转折两条通道, 用于检验主语调对"程度放大/衰减"这一单一机制是否敏感、以及该机制单独能否解释总体语调方差的多大部分。full 轨承担 full-only 留篇门控职责: stage 21 判定一篇是否为银行金融科技报道只看 full 轨的 llm_verified_full, ctx、ss 轨降为 conditional-on-full 的稳健性轨。full 轨与 ctx、ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。作为规则消融梯度成员, 本列与 you_2018 主分 (full 三规则)、raw、negonly、advonly、negdeg、negadv、degadv 各档位同样各自 just-identified 并排, 相邻档位级差因非可加分解不可解读为单一规则纯效应, 仅供定性不变的稳健性对照, 空文本或词典缺失按对称规则记 NaN 或回填 0.0。由于 full 轨文本覆盖最广、样本量最充足, 该列通常作为消融梯度审计报告中相关系数矩阵的基准锚列, 其余档位与其两两比较相关系数与逐级变号占比。

## VAR: exc_you_2018_score_degonly_ss

【变体差分】
本列是 degonly 消融变体在同句轨 (ss) 上的文章级分值。ss 轨文本 content_ss 在 stage 14 物化, 只保留目标银行与金融科技词在同一句子 ± N 句窗 (config filtering.yaml context_window.ss_sentence_radius, 默认 1) 内共现的语段, 是三轨中语境最紧、对主体相关性要求最严的一轨。其规则设定与 full、ctx 一致: 只开启程度副词加权, 否定翻转与转折增强均关闭, 自归一化到 [−1, 1]。ss 轨的回退语义严格镜像 ctx: 当一篇报道不存在银行与金融科技同句共现时, content_ss 回退为全文正文、ss_is_fallback 记 True 并共享 n_articles 分母; 当 FINTECH_AC 为 None 时 is_fallback 全 True 优雅降级。ss 轨同样是 full-only 留篇门控下的 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集子集, per-track 分值照其自身文本独立计算。ss 与 full、ctx 三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J 过度识别检验。在 T=2 开发样本上 ss 轨因同句共现稀疏可能出现较多回退, 且回退后与 full 轨在同一规则设定下分值高度相关, 属预期退化而非缺陷; 生产 T=18 语料上共现更充分, 才能真正区分 ss 轨的独立信息量; 空文本或无命中词时本列按对称缺失语义记 NaN。三轨并排使用时应报告各自样本量与回退占比, 避免把因回退带来的与 full 轨高相关误读为"ss 轨无增量信息"这一结论性判断。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
