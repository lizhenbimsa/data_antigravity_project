---
family_id: F277
novelty_exempt_rationale: "exc_ 停刊稳健性聚合 × degonly 规则消融的双重派生变体家族, 测度定义依据母族 yao_2021 词典及规则消融/停刊排除机制的既有文献支撑, 非独立新构念, 无需追新文献。"
columns:
- exc_yao_2021_score_degonly_ctx
- exc_yao_2021_score_degonly_full
- exc_yao_2021_score_degonly_ss
unit: 情感倾向分值 (无量纲, 自归一化于 [-1, +1]); 面板列为 bank-year 篇均值 (排除疑似停刊媒体后)
formula: "article: yao_2021_score_degonly = Σ(final_i) / Σ|final_i|, final_i = base_i × degree_i (apply_degree=True, apply_negation=False, apply_adversative=False); panel: exc_yao_2021_score_degonly{track} = mean over df_alive (_is_ceased_media==0) of yao_2021_score_degonly{track}, 按 (target_bank, year) 分组"
producer: news_process/pipeline/panel/attention_media.py (C.4 exc_* 停刊稳健性聚合环) ← news_process/pipeline/sentiment/tone_words.py::compute_dict_scores (_compute_sentiment_with_rules, _RULE_ABLATION_VARIANTS 'degonly')
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- 22_tone_words.parquet (yao_2021_score_degonly_{full,ctx,ss})
- "40_panel: 隐性停刊检测 detect_defacto_cessation (_is_ceased_media 标记)"
citations:
- doi: 10.1111/jofi.13498
  type: journal
  authors: Derrien, F., Krüger, P., Landier, A., & Yao, T.
  year: 2025
  title: "ESG news, future cash flows, and firm value"
  venue: Journal of Finance
  vol: 80
  issue: 6
  pages_or_artno: 3499-3554
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
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
本家族刻画的是同一条底层测度沿三条正交轴叠加后的一个特定组合: 词典轴取姚加权等 (2021) 的金融领域中文情绪词典 (代号 yao_2021), 语言学规则轴取"仅程度副词"消融变体 (degonly), 聚合口径轴取"排除疑似停刊媒体"的稳健性均值 (exc_ 前缀), 而文本轨道轴则在 full / ctx / ss 三轨上分别落列。构念本身是银行层面的年度新闻语调: 对每篇提及目标银行与金融科技共现的报道, 用 yao_2021 词典逐词打分并按 degonly 规则加权归一, 再在 bank-year 单元内对未停刊媒体的文章取篇均, 得到一个界于负一到正一之间的无量纲语调分。姚加权等 (2021) 的词典由年报语料 (正面 3,592 词、负面 1,633 词) 与社交媒体语料 (正面 912 词、负面 965 词) 两个子表去重合并而成, 合并后正面 3,844 词、负面 2,074 词; 相较于以英文 Loughran-McDonald 翻译扩充为主的 jiang_2021, 它更贴合中文语料的构词与语域分布, 因而在多词典互为稳健性的矩阵里承担"本土年报∪社媒双源"这一独立信息角色。

【方法学与计算】
文章级打分在 stage 22 的 tone_words 引擎里由 _compute_sentiment_with_rules 完成, 其状态机逐 token 扫描分词序列, 维护否定窗口、程度倍率与转折作用域三个状态, 命中情感词时计算 final = base × degree × negation × adversative, 遇句末标点重置全部状态 (从句级作用域, 参照 Ding-Liu-Yu 2008 的整体词典法)。degonly 变体在 _RULE_ABLATION_VARIANTS 中登记为 (apply_negation=False, apply_degree=True, apply_adversative=False): 即只保留程度副词对情感词强度的六级缩放, 而把否定翻号与转折放大两条数值效应锁死为恒等 (否定倍率不翻、转折 boost 锁 1.0), 但仍保留这两类词的识别、continue 与句末重置骨架, 使否定窗口的到达距离与全规则版本共享同一 scoping, 只切换数值效应而不改变扫描几何。归一化采用 Σ(final) / Σ|final|, 值域恒定在负一到正一, 与 LLM 投票语调、BERT 语调等有界轨保持可比 (旧的裸词频分母会因程度×转折放大破界, 已于 v3.11.1 修正)。面板聚合在 attention_media.py 的停刊稳健性区 (C.4) 完成: 先由 detect_defacto_cessation 标记 _is_ceased_media, 再在 df_alive (未停刊子集) 上按 target_bank 与 year 分组取该文章级列的均值, 冠以 exc_ 前缀落列。这一排除设计的学术动机是幸存者偏差 (survivorship bias): 媒体来源在样本期内隐性退出会使语调指标向存活媒体倾斜, 进而污染以媒体来源为暴露的 Bartik 类工具变量 (参见 Gentzkow, Shapiro 与 Sinha 关于报纸市场的证据传统, 以及 Fang 与 Peress 关于媒体覆盖与横截面收益的框架)。因此 exc_ 系列不是主测度而是主语调的一条稳健性臂: 其解读须与含全部媒体的对应列并置, 检验系数在剔除疑似退出媒体后是否稳定, 而非单独作为处理变量进入回归。

【文献定位】
把语言学规则拆成可开关的消融梯度, 其方法论根基在 valence-shifter 谱系: 程度副词、否定与转折作为改变情感词极性与强度的语用算子, 已由 Taboada 等 (2011) 在词典法情感分析中系统化, degonly 恰好隔离出"程度缩放"这一条算子的净贡献。词典法与机器学习法在信息披露语境下的相对表现, Frankel、Jennings 与 Lee (2022) 在 Management Science 上给出了系统比较, 说明词典法在可解释性与跨样本稳定性上的价值, 这正是本项目保留六部词典并对每部做规则消融的动机所在; van Atteveldt、van der Velden 与 Boukes (2021) 进一步以人工标注为金标准比较了词典、众包与机器学习三类方法的效度, 为多方法互证提供了外部依据。就中文金融词典的构建而言, Du、Huang、Wermers 与 Wu (2022) 在 Review of Finance 上论证了语言与领域特异性对情感词典有效性的决定作用, 直接支持了本项目为何不沿用英文词典直译而并置多部本土词典 (yao_2021 即其一); Ma、Zhang 与 Zhang (2025) 与 Bian、Jia、Li 与 Yan (2021) 分别提供了更细粒度与更新的中文金融情绪词表, 构成 yao_2021 的近邻对照。Barbaglia 等 (2025) 在经济文本上重申了词典法的持续适用性, 而 Derrien、Krüger、Landier 与 Yao (2025) 在 Journal of Finance 上以新闻语调为信号刻画了未来现金流与公司价值的关系, 为"银行层面新闻语调具经济含义"这一构念动机提供了顶刊层面的实证支撑。需强调本项目的规则消融与词典消融口径铁律: 七个规则变体 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 与主列全规则版本各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同规则变体或不同词典混入同一 over-identified Hansen J; 三条文本轨道亦然, 各轨各自识别、并排比较, 不得混同。

## VAR: exc_yao_2021_score_degonly_ctx

【变体差分】
本列取 ctx (context) 文本轨道。ctx 轨的文本 = 标题 prepend 后, 仅保留银行与金融科技实体邻近窗口的正文片段 (content_ctx, 在 stage 14 ctx_materializer 物化), 相较 full 轨聚焦于实体上下文而非整篇, 从而降低无关段落对语调的稀释。该列与同家族 full、ss 两列的差异纯粹是文本轨道: 词典 (yao_2021)、规则变体 (degonly, 仅程度缩放、无否定翻号、无转折放大)、聚合口径 (exc_ 排除疑似停刊媒体后按 bank-year 取篇均) 三者完全一致。按项目口径铁律, 留篇门控为 full-only (2026-06-29): 一篇报道是否计入"银行金科报道"只看 full 轨的 llm_verified_full, ctx 轨降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, per-track 列在该子集上照算。ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。在早期试跑 T=2 盘上, ctx 轨在实体窗口稀疏时可能出现较全文更极端或更中性的取值, 属预期的口径差异而非缺陷; 生产 T=19 语料下三轨差异反映的是"聚焦实体上下文 vs 整篇"这一测量选择对语调的敏感性。作为 exc_ 稳健性臂, 本列不单独充当处理变量, 而与含全部媒体的对应 ctx 列并置, 用于诊断剔除疑似退出媒体后语调系数是否稳定。就 degonly 规则变体本身而言, ctx 轨因文本已聚焦实体窗口, 程度副词的密度与全文轨可能不同, 故本列反映的是"实体上下文内、仅施加程度缩放"这一双重限定下的语调, 与全规则 ctx 列对照可读出否定与转折规则在实体窗口口径下的联合净效应。该差异应按"定性不变"披露, 不得据某一规则变体的系数大小声称其更优。

## VAR: exc_yao_2021_score_degonly_full

【变体差分】
本列取 full 文本轨道, 是本家族三轨中的门控基准轨。full 轨文本 = 标题 prepend 加整篇正文 (content_full), 覆盖报道全文, 因而在信息量上最完整, 也是留篇门控 full-only 口径 (2026-06-29) 下唯一决定一篇报道是否计入银行金科报道宇宙的轨道: 判定只看 llm_verified_full, ctx 与 ss 轨则据此降为 conditional-on-full 的测度/稳健性轨。该列与家族内 ctx、ss 两列的唯一差异即文本轨道, 其余维度 (yao_2021 词典、degonly 仅程度规则变体、exc_ 排除疑似停刊媒体后 bank-year 篇均) 全同。degonly 相对家族主规则列 (exc_yao_2021_score_full, 全规则) 的差分在于: 只保留程度副词的六级强度缩放, 关闭否定翻号与转折放大两条数值效应, 用以隔离"程度算子"对最终归一化语调的净贡献; 由于程度与否定、转折作用于同一情感词含交互, 该变体只作 ablation 稳健性对照, 不声称其比全规则更优, 论文表述应为"主结论对是否施加否定/转折规则定性不变"。full、ctx、ss 三轨与 raw/negonly/degonly 等七个规则变体均各自 just-identified 并排、互为稳健性、不分主次, 严禁跨轨或跨规则变体混入同一 over-identified Hansen J。作为 exc_ 稳健性聚合列, 本 full 轨列与含全部媒体的对应列并置解读, 检验剔除疑似退出媒体后的语调系数稳定性。

## VAR: exc_yao_2021_score_degonly_ss

【变体差分】
本列取 ss (same-sentence) 文本轨道。ss 轨文本 = 标题 prepend 后, 仅保留目标银行与金融科技词在同一句 (加减 N 句窗, 默认半径 1) 共现的句子 (content_ss, stage 14 物化), 是三轨中判定最严的轨道, 意在只捕捉银行与金科真正同句耦合语境下的语调。其回退语义镜像 ctx: 当某篇报道不存在银行与金科同句共现时, content_ss 回退为全文正文, ss_is_fallback 置真, 并与 ctx 共享 n_articles 分母; 若 FINTECH_AC 为空则 *_is_fallback 全真, 优雅降级为整篇口径。该列与家族内 full、ctx 两列的差异同样只在文本轨道, 词典 (yao_2021)、规则变体 (degonly, 仅程度缩放)、聚合口径 (exc_ 排除疑似停刊媒体后 bank-year 篇均) 全同。留篇门控仍为 full-only: ss 轨为 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集子集。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。在早期试跑 T=2 盘上, 因同句共现稀疏, ss 轨常出现大量回退或零方差, 属预期退化; 生产 T=19 下 ss 轨提供最保守的实体耦合语调测量。作为 exc_ 稳健性臂, 本列与含全部媒体的对应 ss 列并置, 用于诊断剔除疑似退出媒体后语调系数的稳健性, 而非单独进入回归充当处理变量。由于 ss 轨在多数报道上回退为全文, 其 degonly 语调在回退篇上会与 full 轨的 degonly 语调重合, 仅在真正存在银行与金科同句共现的报道上体现出最严的实体耦合口径; 因此本列相对全规则 ss 列的差分, 集中反映的是在同句共现语境下程度缩放对归一化语调的独立贡献。该口径差异同样按"主结论对规则开关定性不变"披露。

<!-- rendered-citations:begin -->
Derrien, F., Krüger, P., Landier, A., & Yao, T. (2025). ESG news, future cash flows, and firm value. Journal of Finance, 80(6), 3499-3554. https://doi.org/10.1111/jofi.13498
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
