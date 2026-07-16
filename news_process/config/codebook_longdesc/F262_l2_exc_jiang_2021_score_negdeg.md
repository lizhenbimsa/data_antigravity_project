---
family_id: F262
columns:
- exc_jiang_2021_score_negdeg_ctx
- exc_jiang_2021_score_negdeg_full
- exc_jiang_2021_score_negdeg_ss
unit: 情感倾向分值 (无量纲, 自归一化于 [-1, 1]; 停刊稳健性 bank-year 聚合)
formula: "exc_jiang_2021_score_negdeg{track} = mean_{i in bank-year, _is_ceased_media_i == 0} jiang_2021_score_negdeg{track}_i; 其中文章级 jiang_2021_score_negdeg = (pos_neg_deg - neg_neg_deg) / (pos_neg_deg + neg_neg_deg), 否定翻转 + 程度副词两规则开、转折规则关"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (C.4 停刊稳健性动态发现块)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (jiang_2021_score_negdeg_full / _ctx / _ss)
- 40_panel_export_main 内 _is_ceased_media 停刊代理标记 (detect_defacto_cessation)
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
- doi: 10.1016/j.jfineco.2024.103910
  type: journal
  authors: Cao, S., Jiang, W., Wang, J., & Yang, B.
  year: 2024
  title: "From man vs. machine to man + machine: The art and AI of stock analyses"
  venue: Journal of Financial Economics
  vol: 160
  pages_or_artno: 103910
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
  authors: 姜富伟, 孟令超, & 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1016/j.jfineco.2018.10.001
  type: journal
  authors: Jiang, F., Lee, J., Martin, X., & Zhou, G.
  year: 2019
  title: "Manager sentiment and stock returns"
  venue: Journal of Financial Economics
  vol: 132
  issue: 1
  pages_or_artno: 126-149
- doi: "10.1111/1475-679x.12560"
  title: "News Bias in Financial Journalists' Social Networks"
  authors: "Xu, G."
  year: 2024
  venue: "Journal of Accounting Research"
  type: "journal"
- doi: "10.1016/j.eswa.2024.125739"
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  authors: "Wang, et al."
  year: 2025
  venue: "Expert Systems with Applications"
  type: "journal"
new_dois:
  - "10.1111/1475-679x.12560"
  - "10.1016/j.eswa.2024.125739"
---

## CORE

【构念与来源】
本家族是"排除疑似退出覆盖媒体"口径下, 以姜富伟等 (2021) 中文财经媒体情绪词典的 negdeg 规则消融变体计算的银行-年度情感均值, 三条文本轨 (full / ctx / ss) 并列。构念可拆成四个互相独立的层: 第一层是底层词典, 姜富伟、孟令超、唐国豪 (2021) 在《经济学(季刊)》构建的中文财经情绪词表, 用于从媒体文本抽取正负情感词; 第二层是语言学规则消融口径 negdeg, 即在否定翻转与程度副词两条规则同时开启、而转折规则关闭的组合下重新计正负词; 第三层是文本轨口径, 决定情感词在标题加正文的哪一段文本上统计; 第四层, 也是本家族相对同底词典其它家族的定义性差异, 是"停刊稳健性 (cessation-robustness)"聚合口径, 即在做 bank-year 平均之前先剔除被判定为疑似退出覆盖的媒体来源。前三层与其它 jiang_2021 家族共享, 第四层的 exc_ 前缀是本家族的身份标记。

【方法学与计算】
计算分文章级与面板级两步。文章级在 stage 22 (22_tone_words) 产出 jiang_2021_score_negdeg{track}: 对每篇报道在指定文本轨上扫描姜富伟 (2021) 词表, 在否定翻转 (遇否定副词翻转其后情感词极性) 与程度副词 (按程度副词调节情感词强度) 两规则下分别累计正、负强度, 转折规则 (遇转折连词后重置或反转前分句情感) 刻意关闭; 得分按 (pos - neg) / (pos + neg) 自归一化到闭区间 [-1, 1], 分母为零 (无任何命中情感词) 时该篇取缺失。面板级在 attention_media.py 的停刊稳健性块 (源码注释 C.4) 动态发现所有匹配 _SCORE_PATTERNS 前缀的文章级情感列, jiang_2021_score_ 是其中之一, 对每一列先用 df_alive = df[_is_ceased_media == 0] 剔除疑似退出媒体的报道, 再按 target_bank × year 分组取均值, 落为 exc_jiang_2021_score_negdeg{track}。停刊判据来自 detect_defacto_cessation: 它检测的是"话题覆盖退出"而非经证实的报纸停刊, 是一种保守代理 (proxy), 媒体可能仍在正常出版只是不再覆盖本话题, 因此本家族应解读为对幸存者偏差 (survivorship bias) 的保守稳健性口径, 不可在论文中表述为严格的出版停刊口径。剔除后若某 bank-year 全部报道皆来自存活媒体, 则该家族值与不剔除口径重合; 若无存活报道则按情感类契约保持缺失 (不做零填, 与计数类 n_articles_exc 的零填契约相区分)。留篇宇宙遵循 2026-06-29 起的 full-only 门控: 一篇报道是否计入银行金科语料只看 full 轨的 llm_verified_full, ctx / ss 轨为 conditional-on-full 的子集测度, 因此三轨的行宇宙同源, 差别只在情感词统计所依托的文本片段。

【文献定位】
底层词典锚定姜富伟等 (2021) 的中文媒体情绪构建, 与 Du et al. (2022) 在《Review of Finance》提出的领域与语言特异性中文财经情绪词典互为可比的中文词典证据, 二者共同支撑"通用英文词典直译到中文财经语境会失真、须用本土词典"的方法学立场。词典法本身的效度与边界由 Barbaglia et al. (2025) 的经济文本词典法系统评估给出参照。将词典法置于更广的情感抽取谱系中, Frankel, Jennings & Lee (2022) 在《Management Science》系统比较了机器学习与词典法两条披露情绪测度路径, 为本项目"三方法 (LLM / 词典 / BERT) 互为稳健性、不分主次"的设计提供了直接先例; Cao, Jiang, Yang & Zhang (2023) 与 Cao, Jiang, Wang & Yang (2024) 进一步刻画了机器与人协作抽取文本信号的边界。情绪测度对资产定价的经济含义则由 Jiang, Lee, Martin & Zhou (2019) 的经理情绪与股票回报证据奠定。停刊稳健性的动机 (媒体来源消失引入幸存者偏差、污染基于媒体暴露的工具变量) 与规则消融、三轨口径一样, 属规格稳健性范畴。本家族的三条文本轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混进同一 over-identified 的 Hansen J 检验; negdeg 与其它规则消融变体高度共线 (corr 约 0.99), 亦须各自 just-identified 并排、报相关而非并入同一识别方程。

## VAR: exc_jiang_2021_score_negdeg_ctx

【变体差分】
本列是三轨中的 ctx (entity-context, 实体上下文) 轨: 文章级 jiang_2021_score_negdeg_ctx 在 content_ctx 上统计正负情感词, content_ctx = 标题 prepend 之后, 只保留目标实体 (银行 / 金融科技词) 命中位置周边的实体窗口文本, 而非整篇正文。相对 _full 轨, ctx 轨把情感抽取聚焦到与目标实体真正邻近的语句, 削弱与银行金科主题无关的段落对情绪均值的稀释, 是"信噪比换覆盖"的一端; 相对 _ss 轨, ctx 的窗口以实体命中为中心、不强制银行与金科同句共现, 覆盖范围居中。停刊稳健性聚合口径与其它两轨完全一致: 均先剔除 _is_ceased_media == 1 的疑似退出媒体报道, 再按 bank-year 取均值; negdeg 规则口径 (否定翻转开、程度副词开、转折关) 与其它两轨一致, 三轨之间只差文本片段。行宇宙遵循 full-only 门控, ctx 轨为 conditional-on-full 的子集测度轨。本列与 _full、_ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 在 dev T=2 盘面上 ctx 轨可能因窗口内无命中而更易取缺失, 属预期退化, 生产 T=19 语料下正常出值。需强调本列不与 negdeg 之外的规则消融变体 (raw、negonly、degonly、advonly、negadv、degadv) 并入同一识别方程: 各消融变体自归一化、非可加分解, 彼此相关系数约 0.99, 只作互为稳健性的并排臂, 报相关而非叠入同式。与不剔除停刊媒体的 jiang_2021 基准 ctx 均值相比, 本列仅在存在疑似退出覆盖媒体的 bank-year 上取值不同, 用于检验 ctx 轨系数对幸存者偏差的稳定性; 若某 bank-year 全部报道来自存活媒体, 二者数值重合。

## VAR: exc_jiang_2021_score_negdeg_full

【变体差分】
本列是三轨中的 full 轨: 文章级 jiang_2021_score_negdeg_full 在 content_full 上统计, content_full = 标题 prepend 之后的整篇正文, 覆盖最全的文本片段, 也是留篇门控 (full-only, 2026-06-29) 的判定所依托的轨, 一篇报道是否计入银行金科语料只看 full 轨的 llm_verified_full。相对 ctx / ss 两轨, full 轨不做实体窗口或同句共现的裁剪, 因此覆盖最广、对与目标实体弱相关的语句最敏感, 是三轨中信息覆盖最高、主题聚焦最弱的一端; 它天然承担 conditional-on-full 体系里的"母集"角色, ctx 与 ss 的行宇宙都是 full 留篇集的子集。停刊稳健性聚合与规则消融口径与其它两轨严格一致: 先按 _is_ceased_media == 0 剔除疑似退出覆盖媒体的报道, 再按 target_bank × year 求文章级 jiang_2021_score_negdeg_full 的均值; negdeg 保持否定翻转与程度副词两规则开、转折规则关。本列与 _ctx、_ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨同入一条 over-identified Hansen J; 与不剔除停刊媒体的基准情感均值相比, 二者在无疑似退出媒体的 bank-year 上重合, 差异只在存在疑似退出媒体的样本, 用于检验系数对幸存者偏差的稳定性。作为 full 轨, 本列还承担留篇门控的判定角色: 是否将一篇报道计入银行金科语料只看本轨的 llm_verified_full, 因此 full 轨的行宇宙定义了 ctx 与 ss 两轨的母集, 三轨在同一留篇集上对齐, 差别只在情感词统计所依托的文本片段。negdeg 与其它规则消融变体高度共线, 只作互为稳健性并排臂, 各自 just-identified, 禁并入同一 over-identified Hansen J。

## VAR: exc_jiang_2021_score_negdeg_ss

【变体差分】
本列是三轨中的 ss (same-sentence, 同句共现) 轨: 文章级 jiang_2021_score_negdeg_ss 在 content_ss 上统计, content_ss = 标题 prepend 之后, 只保留目标银行与金融科技词同句 (或 config 指定的同句 ±N 句窗, 默认半径 1) 共现的语句。相对 full 与 ctx 两轨, ss 轨的主题聚焦最严, 只在银行与金科真正同句出现的语境里抽取情绪, 信噪比最高、覆盖最窄。ss 轨遵循镜像 ctx 的回退语义: 当某篇报道没有银行与金科同句共现时, content_ss 回退为整篇正文 body, 同时 ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 若上游金科自动机 FINTECH_AC 为 None, 则 _is_fallback 全部为 True, 优雅降级。停刊稳健性聚合与其它两轨一致: 先剔除疑似退出媒体报道再按 bank-year 求均值; negdeg 规则口径 (否定翻转开、程度副词开、转折关) 亦一致。行宇宙同样服从 full-only 门控, ss 为 conditional-on-full 子集测度轨。本列与 _full、_ctx 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 在 dev T=2 盘面上 ss 轨因同句共现约束最严而最易取缺失或退化为零方差, 属预期现象, 生产 T=19 语料下正常出值。与不剔除停刊媒体的 jiang_2021 基准 ss 均值相比, 本列仅在存在疑似退出覆盖媒体的 bank-year 上取值不同, 用于检验 ss 轨系数对幸存者偏差的稳定性。同样, negdeg 与其它规则消融变体高度共线 (相关系数约 0.99), 只作互为稳健性并排臂, 各自自归一化、非可加分解, 报相关而不并入同一识别方程; ss 轨的严格同句判据与 stage 13 共现硬过滤的 sentence_radius 是两个不同键, 前者服务情感文本片段裁剪, 后者服务上游丢行, 不可互相复用。发现与公司管理层有工作/校友/社交连接的财经记者在报道中系统性引入媒体偏向, 与本家族排除疑似退出覆盖媒体的稳健性动机同属媒体覆盖选择性偏差范畴, 参见 Xu (2024, Journal of Accounting Research)。基于近180万条中国股吧评论构建中文细粒度情绪词典 (CN-FSD), 与姜富伟等 (2021, 经济学(季刊)) 本土中文财经情绪词典构建路径互为可比证据, 参见 Wang et al. (2025, Expert Systems with Applications)。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Cao, S., Jiang, W., Wang, J., & Yang, B. (2024). From man vs. machine to man + machine: The art and AI of stock analyses. Journal of Financial Economics, 160, 103910. https://doi.org/10.1016/j.jfineco.2024.103910
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
姜富伟, 孟令超, & 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Jiang, F., Lee, J., Martin, X., & Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
Xu, G. (2024). News Bias in Financial Journalists' Social Networks. Journal of Accounting Research. https://doi.org/10.1111/1475-679x.12560
Wang, et al. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications. https://doi.org/10.1016/j.eswa.2024.125739
<!-- rendered-citations:end -->
