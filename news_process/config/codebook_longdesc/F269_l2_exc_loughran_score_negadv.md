---
family_id: F269
novelty_exempt_rationale: "exc_ 前缀停刊稳健性聚合 + negadv 规则消融变体的双重衍生家族, 测度定义依据母族词典 (Loughran & McDonald 中译) 及既有稳健性口径文献, 非独立新构念, 无需追新引文。"
columns:
- exc_loughran_score_negadv_ctx
- exc_loughran_score_negadv_full
- exc_loughran_score_negadv_ss
unit: 情感语调分值 (无量纲, 自归一化落于 [-1, 1]); bank-year 级为存活媒体子集内文章级得分的算术均值
formula: "article: loughran_score_negadv = Σ signed(base × negation × adversative) / Σ|matched|, 程度副词规则关闭 (apply_degree=False, apply_negation=True, apply_adversative=True); panel: exc_loughran_score_negadv{track} = mean_{i ∈ bank-year, _is_ceased_media_i = 0}(loughran_score_negadv{track}_i)"
producer: news_process/pipeline/panel/attention_media.py::compute_ceased_media_robustness (C.4 动态发现块); 上游文章级得分 news_process/pipeline/sentiment/tone_words.py::_dict_tone_scores (rule-ablation 变体 _RULE_ABLATION_VARIANTS)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (loughran_score_negadv_full / _ctx / _ss)
- 40_panel_export_main 前置聚合 (_is_ceased_media 停刊代理旗标)
citations:
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2020
  title: "Textual analysis in finance"
  venue: Annual Review of Financial Economics
  vol: 12
  issue: 1
  pages_or_artno: 357-375
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.1145/1341531.1341561
  type: journal
  authors: Ding, X., Liu, B., & Yu, P. S.
  year: 2008
  title: "A holistic lexicon-based approach to opinion mining"
  venue: "Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08)"
  pages_or_artno: 231-240
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
new_dois: []
---

## CORE

【构念与来源】
本家族测度的是"排除停刊媒体后、以 Loughran & McDonald (2011) 财经词典中文主译版计得、且只应用否定翻转与转折两条语言学规则 (关闭程度副词加权) 的银行—年度情感语调均值"。名字里三段前缀各自承载一层含义, 缺一不可。第一段 exc_ 是"停刊稳健性 (cessation robustness)"聚合口径的标记: 银行—年度层的取值不是对该银行当年全部报道求均值, 而是先剔除被判定为"疑似退出覆盖"的媒体来源, 只对存活媒体 (df_alive, 即 `_is_ceased_media == 0` 的行) 求算术均值。第二段 loughran 指第 6 部词典, 即 Loughran & McDonald (2011, Journal of Finance) 原生英文财经词典的中文主译版本, 在本仓词典命名域中列前缀别名为 loughran (权威 = tone_words.DICT_COLUMN_ALIAS / encode.DICT_NAMES)。第三段 score_negadv 是词典消融梯度 (rule-ablation ladder, v3.11.1) 的一个具体变体: 在否定翻转、程度副词、转折三条语言学规则构成的全 powerset 里, negadv 表示"否定 (neg) + 转折 (adv) 两条规则开启、程度副词 (deg) 一条规则关闭"。

【方法学与计算】
计算分两级。文章级由 `tone_words.py::_dict_tone_scores` 产出: 对一篇报道的相应轨文本逐句扫描, 命中 loughran 词典的情感词按其正负基值计分, 途中若遇否定词则翻转当前情感符号 (作用域限当前句, 遇句末标点重置), 若遇转折连词则激活转折状态并把其后情感词权重放大 ADVERSATIVE_BOOST 倍 (转折后的表述更能反映作者真实立场, 即"末尾效应")；negadv 变体特有的是把程度副词加权通道关闭 (apply_degree=False), 也就是"很/极/稍微"等程度副词不再放大或缩小其后情感词的强度, 但其 token 识别与 scoping 仍保留 (方案 a: 只锁数值效应不动作用域)。最终得分对全篇匹配词的带符号加权和除以匹配词绝对量做自归一化, 落于 [-1, 1]。面板级由 `attention_media.py` 的停刊稳健性块 (C.4 动态发现) 产出: 把文章级 `loughran_score_negadv{track}` 在 `_is_ceased_media == 0` 的存活子集内按 target_bank×year 分组求均值, 列名前缀 exc_。三条轨道 full/ctx/ss 各走一遍。需注意, 该家族属"全方法动态发现"分支 (C.4), 已加权变体 (_w / _mw_ / _idf_) 与 llm_vote_score_ 已在别处单独处理故被显式跳过, 而 negadv 属规则消融的纯净变体故被收入。exc_ 均值对零文章银行—年度按契约保持 NaN (不像计数类 n_articles_exc 那样零填), 这是"情感类比例列勿连带零填"契约的直接落地。

【文献定位】
词典法情感测度的方法论根系是 Loughran & McDonald (2011), 他们证明通用心理学词典 (如 Harvard IV) 会把大量在财经语境中中性的词误判为负面 ("when is a liability not a liability"), 从而催生了领域专用词典这一整条研究线; 本仓第 6 部词典正是该英文词典的中文主译。Loughran & McDonald (2016, Journal of Accounting Research) 的综述进一步系统化了会计金融文本分析的方法选择, 是本仓做词典消融敏感性 (即为何要物化 raw/negonly/.../negadv 全梯度而非只报一个"最优"配置) 的直接依据: 语言学规则的取舍会实质影响测度, 唯有并排展示才能证明主结论不被某一处规则开关驱动。Loughran & McDonald (2020) 的年鉴综述把这一立场推广到金融文本分析全域。就 negadv 变体所开启的两条规则而言, 转折规则的从句级作用域直接采自 Ding, Liu & Yu (2008) 的 holistic lexicon 框架 (句末标点重置、转折激活), 逗号刻意不计入句末标点因其连接同一复句内从句; Taboada et al. (2011) 则系统论证了 valence shifter (否定、程度、转折) 在词典法中的处理是测度效度的关键。方法互补性上, Frankel, Jennings & Lee (2022, Management Science) 比较机器学习与词典法, 是本仓"三方法 (LLM/词典/BERT) 互为稳健性"格局的先例; 而 Du et al. (2022, Review of Finance) 确立了中文财经情感词典的领域专用性, 支撑本仓并置多部中文词典 (含 loughran 中译) 作为稳健性梯子的做法。

依口径铁律: 本家族三条轨道 full/ctx/ss 各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J; 词典消融梯度的各语言学规则变体 (含 negadv) 亦为各自 just-identified 并排的稳健性臂, 同样禁混同一 over-identified Hansen J。停刊稳健性 exc_ 聚合是对基线 (全媒体) 情感均值的稳健性对照臂, 用于检验幸存者偏差 (survivorship bias) 是否污染情感测度与下游 Bartik IV, 并非独立构念。留篇门控口径承 full-only (2026-06-29): 是否算作"一篇银行金科报道"只看 full 轨的 LLM 判定, ctx/ss 为 conditional-on-full 的测度/稳健轨; ss 回退语义镜像 ctx, 无银行∧金科同句共现时 content_ss 退化为全文 body。

## VAR: exc_loughran_score_negadv_ctx

【变体差分】
本列是 negadv 变体的 ctx 轨实例。ctx 轨文本 = 标题 prepend + 实体上下文窗口 (银行/金科实体附近的窗口切片, 而非全文正文), 在 stage 14 `ctx_materializer` 物化为 content_ctx。相对家族 full 轨, 本列只把情感扫描限定在实体上下文窗口而非整篇, 意在削弱与目标银行—金科议题无关的段落对语调的稀释, 是 full 轨的稳健性对照轨 (conditional-on-full)。相对同轨其它消融变体, 它固定为"否定翻转 + 转折两条规则开启、程度副词加权关闭"的 negadv 配置: 即 valence shifter 中保留符号翻转与转折末尾效应放大, 但不再让程度副词等比缩放情感强度。词典固定为第 6 部 loughran 中译。exc_ 前缀表示 bank-year 均值只在存活媒体子集 (`_is_ceased_media == 0`) 内计得, 剔除疑似退出覆盖的媒体, 用于检验幸存者偏差。本列与 _full / _ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与同轨 raw/negonly/degonly/advonly/negdeg/degadv 各消融变体亦为并排稳健性臂, 同禁混同一 over-identified Hansen J。需强调 ctx 轨的差分不改变词典与规则配置, 只改变喂入情感扫描的文本范围: full 轨读整篇, ctx 轨读实体上下文窗口, ss 轨读同句共现窗, 三者对同一篇报道可能给出不同语调, 这正是三轨作为规格稳健性并排的意义所在。exc_ 聚合又在此之上叠加"只用存活媒体"的样本约束, 使本列同时承载两层稳健性检验 (文本范围 + 幸存者偏差)。dev T=2 盘面上 exc_ 族因平衡/存活子集稀疏可能整列缺 (即缺 12 列的 loughran 族之一属预期), 生产 T=19 全量方显; 论文中若引用本列须明示口径为"疑似退出覆盖媒体的保守剔除", 不可表述为严格报纸停刊。

## VAR: exc_loughran_score_negadv_full

【变体差分】
本列是 negadv 变体的 full 轨实例, 也是家族内最接近 canonical 的口径。full 轨文本 = 标题 prepend + 全文正文 (content_full), 情感扫描覆盖整篇报道, 是三轨中信息量最全、也是留篇门控 (2026-06-29 full-only) 唯一裁决轨的那一条。相对 ctx/ss, 本列不做实体窗口或同句共现截断, 直接对全文计得 loughran_score_negadv 再在存活媒体子集内求 bank-year 均值。规则配置固定为 negadv: 否定翻转与转折两条规则开启 (符号翻转 + 转折后 ×ADVERSATIVE_BOOST 放大), 程度副词加权关闭 (apply_degree=False, 程度 token 仍被识别与消费但不产生数值倍率)。这与 raw (三规则全关) 相比多了否定与转折的净效应, 与 full 配置 (三规则全开) 相比恰少了程度副词一维, 因此 (full − negadv) 隔离的是程度副词规则的联合净效应 (注意此差为高度共线的非可加分解, audit MATH-1: 各变体自归一化、相关系数近 0.99, 只可报相关不可并入同式)。词典为第 6 部 loughran 中译, exc_ 前缀限定存活媒体子集均值以对照幸存者偏差。本列与 _ctx / _ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与同轨其余六个消融变体同为并排稳健性臂, 同禁混。作为家族里信息量最全的轨, full 轨也是留篇门控的唯一裁决轨, 因此本列的银行—年度行宇宙即 full 留篇集在存活媒体子集内的进一步收敛; ctx/ss 两轨的行宇宙是 full 留篇集的子集, 三列不必逐行同时非空。就与相邻测度的区分而言, 本列不是 LLM 投票情感 (llm_vote_score) 也不是 BERT 概率情感, 而是纯词典法在 negadv 规则配置下的自归一化语调, 三方法各产一套并互为稳健性; 与政治词权重梯度、co-primary 嵌入双轨等其它稳健性梯子正交、不交叉。

## VAR: exc_loughran_score_negadv_ss

【变体差分】
本列是 negadv 变体的 ss 轨实例。ss 轨文本 = 标题 prepend + 银行∧金科同句±N窗超级文档 (config/filtering.yaml::context_window.ss_sentence_radius, 默认 1), 在 stage 14 物化为 content_ss, 是三轨中判定最严的一条 (要求银行与金科词在同一句邻域共现)。回退语义镜像 ctx: 当某篇无银行∧金科同句共现时 content_ss 退化为全文 body 且 ss_is_fallback=True (共享 n_articles 分母); 若 FINTECH_AC 为 None 则 `*_is_fallback` 全 True 优雅降级。相对 full/ctx, 本列把情感扫描收敛到最贴近"银行—金科"议题的同句窗口, 是最保守的稳健性轨。规则配置固定为 negadv: 否定 + 转折开、程度副词关。词典为第 6 部 loughran 中译, exc_ 前缀限定存活媒体子集 (`_is_ceased_media == 0`) 内 bank-year 均值以对照幸存者偏差。本列与 _full / _ctx 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁混同一 over-identified Hansen J; 与同轨其余消融变体亦为并排稳健性臂, 同禁混。dev T=2 上 ss 轨因同句共现稀疏且叠加存活媒体子集过滤, 更易整列退化或缺失, 属预期, 生产 T=19 正常出值。就三轨的层级关系而言, ss 是判定最严的一条 (银行∧金科同句), ctx 次之 (实体窗口), full 最宽 (全文): 从 full 到 ss, 情感扫描的文本逐级收敛到最贴近银行—金科议题的片段, 语调随之更少被无关段落稀释, 因而三轨对同一稳健性问题给出由宽到严的一族答案。ss 的回退设计保证了无同句共现的报道不被直接丢弃而是优雅退回全文, 与 ctx 完全同款回退语义, 使 ss 轨的银行—年度覆盖不因严判据而系统性坍缩。本列与其余六个消融变体、与 LLM/BERT 两法、与政治词权重及嵌入双轨等梯子均正交并排, 各自 just-identified, 一律禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based approach to opinion mining. Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08), 231-240. https://doi.org/10.1145/1341531.1341561
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
