---
family_id: F284
novelty_exempt_rationale: "exc_ 前缀家族是 attention_media.py C.4 停刊媒体稳健性聚合 + degadv 规则消融梯度的双重技术变体, 其测度定义依据 you_2018 母族词典与规则消融 SSOT (_RULE_ABLATION_VARIANTS), 非独立新构念, 无需单独追加新颖文献。"
columns:
- exc_you_2018_score_degadv_ctx
- exc_you_2018_score_degadv_full
- exc_you_2018_score_degadv_ss
unit: 无量纲情感得分 (银行-年面板级, 由文章级自归一化分值 ∈ [−1, 1] 在 bank-year 内取算术均值; 该 bank-year 无存活媒体文章时记 NaN)
formula: "exc_you_2018_score_degadv{_full,_ctx,_ss} = mean_{i ∈ (target_bank,year), _is_ceased_media(i)=0}( you_2018_score_degadv{_full,_ctx,_ss}_i ), 其中文章级 you_2018_score_degadv = Σ(final_valence)/Σ|final_valence| 由 you_2018 词典在 apply_negation=False、apply_degree=True、apply_adversative=True 规则下逐篇计算 (degadv = 完整三规则 − 否定翻转); exc_ 聚合剔除被判定为已停刊/停更 (_is_ceased_media=1) 媒体来源产出的文章后再按 bank-year 取均值"
producer: news_process/pipeline/panel/attention_media.py (C.4 停刊稳健性变量块, df_alive=df[df['_is_ceased_media']==0] 上 groupby(['target_bank','year'])[src].mean() 动态生成 exc_{src} 列; 依赖同名无 exc 前缀的文章级列 you_2018_score_degadv{_full,_ctx,_ss} 作为输入, 该文章级列由 pipeline/sentiment/tone_words.py::compute_dict_scores 产出, 是否停刊由 detect_defacto_cessation 判定)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (文章级 you_2018_score_degadv{_full,_ctx,_ss}, 无 exc 前缀)
- 40_panel_export_main.parquet (attention_media.py 停刊检测 detect_defacto_cessation 与 C.4 bank-year 聚合发生于面板构建阶段)
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
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
- doi: "10.1177/10944281251334777"
  type: "journal"
  authors: "Iqbal, F., & Pfarrer, M. D."
  year: 2025
  title: "Using Coreference Resolution to Mitigate Measurement Error in Text Analysis"
  venue: "Organizational Research Methods"
  pages_or_artno: "10944281251334777"
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
new_dois: []
---

## CORE

【构念与来源】
本家族测度的是银行-年面板级、剔除已停刊媒体来源后的词典情感均值, 词典底本取自 You、Zhang 与 Zhang (2018) 发表于 The Review of Financial Studies 的中文金融情感词典。该文研究"谁掌握了媒体之笔"这一问题, 在辨识媒体报道对公司信息环境影响的过程中, 构造并公开了一套面向中文财经文本的情感词表, 其中 Panel C 为语义确定 (definite) 词集、Panel D 为语义歧义 (ambiguous) 词集。本项目在 tone_words 阶段加载 you_2018 词表的正负极性词, 对每篇报道计算带语言学规则的情感倾向分, 产出无 exc 前缀的文章级列 you_2018_score_degadv{_full,_ctx,_ss}。列名前缀 exc 并非"排除已停业主体"的文章级去伪存真标记, 而是在面板构建阶段 (attention_media.py) 对上述文章级列执行"排除已停刊媒体来源" (exclude ceased media) 后取 bank-year 均值所得的稳健性替代指标: 面板脚本先以 detect_defacto_cessation 对每条媒体来源做隐性停刊 (de facto cessation) 判定, 写入文章级布尔标记 _is_ceased_media, 再在 df_alive=df[_is_ceased_media==0] 子集上按 (target_bank, year) 分组取该文章级列的算术均值, 得到 exc_you_2018_score_degadv{_full,_ctx,_ss} 这一 bank-year 面板列。其学术动机是: 媒体来源在样本期内消失(停刊/停更)会引入幸存者偏差, 使情感指标系统性地向存活至今的媒体倾斜, 进而污染以媒体结构为工具的 Bartik 型工具变量; exc_ 前缀系列正是为检验该偏差是否驱动主结果而构造的系数稳定性稳健性列, 供 Stata 端与未剔除停刊媒体的面板层聚合列 you_2018_degadv_tone{_full,_ctx,_ss} 对照。

【方法学与计算】
计分内核 _compute_sentiment_with_rules 是一台确定性有限状态机, 依次施加三条中文情感语言学规则: 否定翻转 (遇否定词对随后极性词变号)、程度副词六级加权 (极其/非常/较/稍等程度词按连续档位放大或衰减)、转折增强 (遇但是/然而等转折连词对其后子句极性做增强)。本家族对应的 degadv 变体在规则消融梯度 (rule-ablation ladder, 单一事实源 _RULE_ABLATION_VARIANTS) 中定义为 apply_negation=False、apply_degree=True、apply_adversative=True, 即在完整三规则之上关闭否定翻转这一条 (degadv 等价于 full 减去否定通道)。文章级计算发生在 tone_words 阶段: 每篇文本先经 jieba 冻结词典分词, 命中 you_2018 极性词后累加加权后的极性值 final_valence, 分子为其代数和、分母为其绝对值之和, 得到自归一化的文章级倾向分; 空文本或词典缺失时按对称规则回填 NaN 或 0.0, 不静默造零。面板级聚合发生在 attention_media.py 停刊稳健性代码块 (C.4): 该块以 _SCORE_PATTERNS 动态发现全部方法族 (LLM 投票/三家 LLM/六部词典/三个 BERT) 产出的文章级分值列, 逐列在 df_alive 子集 (排除 _is_ceased_media=1 的文章) 上按 (target_bank, year) 分组取均值, 并以 exc_ 前缀重命名写回面板; 权重加权变体 (_w/_mw_/_idf_ 后缀) 与已在 C.3 单独处理的 llm_vote_score 系列被显式跳过, 以避免命名与口径冲突。需要强调的是, degadv 相对完整三规则主分的规则消融属非可加分解: 否定与程度作用于同一词时含交互项, 相邻档位级差不代表"某条规则的纯贡献", 只能作为对照稳健性使用; 而 exc_ 前缀本身的"是否剔除停刊媒体"这一维度与规则消融梯度正交, 二者不应混淆或交叉解读为同一敏感性来源。

【文献定位】
就构念谱系而言, 本家族坐落在中文金融文本情感词典测量这一方法学脉络上。You et al. (2018) 提供了词表底本与媒体报道信息含量的识别背景; Du et al. (2022) 在 Review of Finance 系统论证了中文金融情感的语言域特异性, 说明通用词表迁移到财经语料时须做本地化, 这正是本项目并置多部中文词典 (jiang_2021/yao_2021/bian_2021/du_2022/you_2018 等) 互为稳健性的动机。就规则内核而言, 程度副词与转折的效价移位 (valence shifting) 建模承接 Taboada et al. (2011) 在 Computational Linguistics 上系统化的词典法效价移位框架。就方法学地位而言, Frankel、Jennings 与 Lee (2022) 在 Management Science 上对比机器学习与词典法披露情感的证据, 支持将词典法作为与 LLM、BERT 并列的第三条互为稳健性测量轨; van Atteveldt et al. (2021) 与 Barbaglia et al. (2025) 则分别从人工标注效度校验与经济文本词典法应用两个侧面, 为词典分值的可信度提供外部佐证。本项目将规则消融各档位视为方法学稳健性梯子: 各档位各自 just-identified 并排、互为稳健性不分主次, 严禁把不同消融档位混进同一 over-identified 的 Hansen J 过度识别检验, 以免制造伪工具变量冗余。 近期方法学文献进一步为本家族的具体环节提供了外部佐证。Naldi 与 Petroni (2023) 以人工构造测试集评估多种词典法情感工具对否定的检测与处理能力, 实证发现各工具在该环节表现差异显著; 该证据正锚定 degadv 档位的构造理由——否定翻转是词典状态机内部可被单独测量、单独失效的模块, 故关闭该规则而保留程度副词与转折的档位有独立报告价值。惟原文系英文通用领域的工具评测、以否定检测准确率为度量, 本项目不做准确率评测, 而是把否定开关作为中文金融新闻语调面板测度的一条并排稳健性臂。Iqbal 与 Pfarrer (2025) 在 Organizational Research Methods 上以共指消解处理为例, 证明一项具体的语言学处理选择会系统性改变文本测度取值并构成实质性测量误差来源, 支持本项目对语言学规则不作默认采纳、而显式呈现其后果的立场; 但其所处理的规则是实体指代还原, 与本家族的否定/程度/转折三规则并非同一项, 且原文取规范性取向 (主张采纳该规则以减少误差), 与本项目令七臂互为稳健性并排、不设主次的取向不同, 故不得视为 powerset 规则消融设计的同构先例。就 exc_ 前缀所做的样本裁剪而言, Cziraki 与 Gider (2024) 以报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 为「剔除疑似退出覆盖媒体后再作银行-年度聚合」提供了现实动机: 媒体退出是真实且有经济后果的样本组成变化。其停刊判定取自外部事件数据并用于识别冲击, 而本项目的 ceased_set 由 detect_defacto_cessation 自语料内部推断 (confirmed ∪ suspected), 属保守代理而非严格停刊事实, 用途亦仅限稳健性子样本; 该文为工作论文, 尚未经同行评审。
## VAR: exc_you_2018_score_degadv_ctx

【变体差分】
本列是 degadv 消融变体在实体窗轨 (ctx) 上、剔除已停刊媒体来源后的银行-年面板均值。上游文章级分值 you_2018_score_degadv_ctx 由 ctx 轨文本 content_ctx 计算, 该文本在 stage 14 ctx_materializer 物化, 由标题 prepend 后拼接目标实体上下文窗口构成, 相较全文轨只保留与银行/金融科技实体邻近的语段, 意在削弱与主体无关的噪声段落对情感计分的稀释。规则设定与 full 轨严格一致: 关闭否定翻转、开启程度副词六级加权与转折增强, 文章级分子分母同为自归一化口径。attention_media.py C.4 在 df_alive (即 _is_ceased_media==0 的存活媒体子集) 上对该文章级列按 (target_bank, year) 分组取均值, 得到本列; 若某 bank-year 内全部文章均来自已停刊媒体或本身无文章, 本列记 NaN, 不借用 full 轨或未剔除停刊媒体的面板层聚合列 you_2018_degadv_tone_ctx 的数值回填。ctx 轨与 full、ss 三轨互为稳健性、不分主次, 各自 just-identified 并排进入各自的规格, 严禁把三轨混入同一 over-identified Hansen J 过度识别检验。需注意留篇门控为 full-only 口径 (2026-06-29): 一篇报道是否计入银行金融科技报道宇宙只由 full 轨的 llm_verified_full 判定, ctx 轨为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 文章级分值照其自身文本独立计算, 停刊剔除亦在该子集上独立执行。在与其他消融档位横向比较时, 本列与同轨的 raw、negonly、degonly、advonly、negdeg、negadv 及三规则全开的主分对应的 exc_ 系列共享同一批"存活媒体"文章池, 差异只来自文章级规则开关组合, 该差值仍不构成可加分解意义上的单一规则贡献, 只能作为方法学稳健性对照使用。审计时应同时报告本列与 ctx 轨未剔除停刊媒体的对应聚合列的系数稳定性对比, 以证明主结论不由幸存者偏差驱动。

## VAR: exc_you_2018_score_degadv_full

【变体差分】
本列是 degadv 消融变体在全文轨 (full) 上、剔除已停刊媒体来源后的银行-年面板均值, 也是三轨中口径最完整、留篇门控所依据的那一轨。上游文章级分值 you_2018_score_degadv_full 的文本 content_full 由标题 prepend 后拼接原始正文全文构成, 覆盖整篇报道, 因此其 you_2018 命中词与规则触发次数通常多于 ctx、ss 两轨; 规则设定为 degadv: 关闭否定翻转、开启程度副词六级加权与转折增强, 即在完整三规则之上单独剥离否定通道, 用于检验主语调对否定翻转规则是否敏感。full 轨承担 full-only 留篇门控职责: stage 21 判定一篇是否为银行金融科技报道只看 full 轨的 llm_verified_full, ctx、ss 轨降为 conditional-on-full 的稳健性轨。attention_media.py C.4 在 df_alive (排除 detect_defacto_cessation 判定为已停刊的媒体来源产出的文章) 子集上, 按 (target_bank, year) 分组对该文章级列取均值, 得到本列; 该聚合是本家族"停刊稳健性"构造的核心动机: 若停刊媒体的报道倾向系统性偏离存活媒体, 未剔除的面板层聚合列 you_2018_degadv_tone_full 就可能受幸存者偏差污染, 本列作为剔除后的对照, 供 Stata 端做系数稳定性检验。full 轨与 ctx、ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。作为规则消融梯度成员, 本列与 you_2018 主分 (full 三规则)、raw、negonly、degonly、advonly、negdeg、negadv 各档位对应的 exc_ 系列同样各自 just-identified 并排, 相邻档位级差因非可加分解不可解读为单一规则纯效应, 仅供定性不变的稳健性对照; 某 bank-year 若全部文章均属已停刊媒体, 本列记 NaN。研究者在报告本列时应同时呈现 ctx、ss 两轨的对应 exc_ 聚合值以及未剔除停刊媒体的 tone_full 对照列, 共同构成对 you_2018 词典打分是否受否定翻转规则、以及是否受媒体停刊幸存者偏差驱动的双重稳健性证据链, 任一单列结果都不应单独作为定论。

## VAR: exc_you_2018_score_degadv_ss

【变体差分】
本列是 degadv 消融变体在同句轨 (ss) 上、剔除已停刊媒体来源后的银行-年面板均值。上游文章级分值 you_2018_score_degadv_ss 的文本 content_ss 在 stage 14 物化, 只保留目标银行与金融科技词在同一句子 ± N 句窗 (config filtering.yaml context_window.ss_sentence_radius, 默认 1) 内共现的语段, 是三轨中语境最紧、对主体相关性要求最严的一轨; 其规则设定与 full、ctx 一致: 关闭否定翻转、开启程度副词加权与转折增强, 自归一化到 [−1, 1]。ss 轨的回退语义严格镜像 ctx: 当一篇报道不存在银行与金融科技同句共现时, content_ss 回退为全文正文、ss_is_fallback 记 True 并共享 n_articles 分母; 当 FINTECH_AC 为 None 时 is_fallback 全 True 优雅降级; 该回退发生在文章级计算阶段, 与本列的 bank-year 聚合是两个独立步骤。attention_media.py C.4 在 df_alive (排除已停刊媒体文章) 子集上按 (target_bank, year) 对该文章级列取均值, 得到本列, 若该 bank-year 无存活媒体文章记 NaN。ss 轨同样是 full-only 留篇门控下的 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集子集, per-track 文章级分值照其自身文本独立计算; ss 与 full、ctx 三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J 过度识别检验。在 T=2 开发样本上 ss 轨因同句共现稀疏可能出现较多回退, 属预期退化而非缺陷。研究者若在稳健性附录中报告本列, 应同时披露该 bank-year 内 ss 轨回退样本占比与 ceased_media_frac (停刊媒体文章占比, 同属 attention_media.py C.1 输出), 使读者能够判断结果是否主要由回退样本或幸存者偏差校正本身驱动, 而非真正的同句语境效应。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
</content>
</invoke>
