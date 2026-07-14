---
family_id: F270
columns:
- exc_loughran_score_negdeg_ctx
- exc_loughran_score_negdeg_full
- exc_loughran_score_negdeg_ss
unit: 无量纲情感得分 (自归一化, 值域约 [-1, 1]; bank-year 级为存活媒体篇均值)
formula: "exc_loughran_score_negdeg{track} = mean_媒体 a 不属于停刊代理集合 loughran_score_negdeg{track}(a); 其中 loughran_score_negdeg = 在否定翻转(neg) + 程度副词(deg) 两条语言学规则下计算、关闭转折(adv)规则的 loughran 词典自归一化篇章得分"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性聚合; 上游篇章分见 news_process/pipeline/sentiment/tone_words.py)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (loughran_score_negdeg{track} 篇章级词典得分)
- 40_panel_export_main 内 detect_defacto_cessation (停刊代理集合)
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
- doi: 10.1017/S0022109023000716
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2024
  title: "Measuring firm complexity"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2487-2514
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
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
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
本家族度量的是 loughran 中文词典情感得分在「否定翻转 + 程度副词」两条语言学规则下、并剔除疑似停刊媒体后的银行-年度稳健性版本。构念由三层叠加而成。第一层是词典本体: loughran 指 Loughran 与 McDonald (2011) 在《Journal of Finance》提出的金融文本情感词表的中文主译版本 (本项目第 6 部词典, 前缀别名 loughran, 权威源为 tone_words.DICT_COLUMN_ALIAS 与 encode.DICT_NAMES)。该词表的核心洞见是: 通用情感词典 (如 Harvard-IV) 在金融语境下大量误判——诸如「税」「负债」「成本」等词在通用语料中带负面色彩, 在金融披露中却是中性行业术语, 故须以领域专用词表替代。第二层是消融梯度中的 negdeg 变体: 本项目把否定翻转 (neg, 如「不」「未」「无」翻转其后情感词极性)、程度副词 (deg, 如「显著」「大幅」放大或「略微」缩小情感强度) 与转折 (adv, 如「但是」「然而」抑制前句情感) 三条语言学规则做全 powerset 物化, negdeg 即「同时施加 neg 与 deg 两条规则、关闭 adv 转折规则」的臂, 区别于施加全部三条规则的 canonical 无后缀得分, 也区别于 raw / negonly / degonly / advonly / negadv / degadv 其余六个消融臂。第三层是停刊稳健性口径 (exc 前缀): 在把疑似退出报道覆盖 (coverage exit) 的媒体保守剔出样本后, 对存活媒体的篇章得分做银行-年度求均值。需强调该 exc 口径是「话题覆盖退出」的保守代理 (proxy) 而非经证实的报纸停刊, 论文表述须相应留有余地。

【方法学与计算】
篇章级得分 loughran_score_negdeg{track} 在 Stage 22 (22_tone_words.parquet) 计算: 对每篇报道分词后, 用 loughran 词表标注正/负情感词, 在 negdeg 规则下调整极性与强度, 得到自归一化的篇章情感分 (每变体各自归一化, 与其余消融臂高度共线、corr 常达 0.99, 属非可加分解, 报相关而非并入同一线性式)。银行-年度聚合在 attention_media.py 完成: 先由 detect_defacto_cessation 识别疑似退出覆盖的媒体集合并置 _is_ceased_media 标志, 再对 _is_ceased_media 为 0 的存活样本按 (target_bank, year) 分组取该篇章得分均值, 落为 exc_loughran_score_negdeg{track}。该聚合是纯 CPU、零 API、$0 的确定性后处理, 不触发 LLM。计数类兄弟列 (如 n_articles_exc) 对零文章格填 0, 但本情感均值列按契约在空存活子集下保持 NaN, 绝不连带零填, 以免与真实零情感混淆。三条轨道 (full / ctx / ss) 分别聚合、并排产列。

【文献定位】
词典本体锚定 Loughran 与 McDonald (2011): 该文奠定了金融领域专用情感词表相对通用词典的测量优势, 是本家族的方法论根。Loughran 与 McDonald (2016) 的会计与金融文本分析综述系统梳理了词典法的适用边界与消融敏感性, 为本项目把语言学规则做 powerset 消融提供依据。Loughran 与 McDonald (2024) 在《Journal of Financial and Quantitative Analysis》进一步演示了词表族在复杂度测度上的可迁移性, 支撑「同一词表在不同规则配置下并排产列」的做法。Frankel、Jennings 与 Lee (2022) 在《Management Science》比较机器学习与词典法的披露情感抽取, 是「词典 / LLM / BERT 三方法互为稳健」范式的先例。van Atteveldt、van der Velden 与 Boukes (2021) 就人工标注、众包、词典与机器学习四类情感测度做效度对比, 提醒词典法在验证时须与人工基准校准。Barbaglia 等 (2025) 提供了经济文本词典法的近期实证参照。就 exc 停刊稳健性动机——媒体退出引入幸存者偏差、污染基于媒体来源的暴露度识别——本家族做保守剔除以检验系数稳定性。

## VAR: exc_loughran_score_negdeg_full

【变体差分】
本列取 full 轨道: 篇章文本 = 标题 prepend + 全文正文 (content_full), 即把标题拼接在正文之前后整体送入 loughran 词典打分, 在 negdeg 规则 (否定翻转 + 程度副词, 关闭转折) 下自归一化, 再在剔除疑似停刊媒体后按银行-年度取存活样本均值。full 轨是本项目的 canonical 留篇门控轨: 一篇报道是否算作「一篇银行金科报道」只看 full 轨的 llm_verified_full 判定 (2026-06-29 full-only 门控), 故 full 轨的行宇宙即银行-年度报道全集, ctx 与 ss 轨的行宇宙是其 conditional-on-full 子集。相对同家族的 ctx / ss 两列, 本列唯一差分在文本轨道——规则臂 (negdeg)、词典 (loughran)、停刊口径 (exc)、聚合方式 (存活媒体篇均值) 三者完全一致, 仅进料文本从「标题+正文全文」切换而来。full 轨信息量最全但也最易被与银行金科无关的段落稀释情感信号, 因此与 ctx / ss 两轨构成规格稳健性并排关系: 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified 的 Hansen J 过度识别检验。就消融臂而言, 本列固定为 negdeg (施加否定翻转与程度副词、关闭转折), 与同词典的 raw 无规则臂、negonly / degonly / advonly 单规则臂以及 negadv / degadv 其余双规则臂共同构成规则消融梯度; canonical 无后缀得分则是施加全部三条规则的臂。这些消融臂彼此高度共线, 只作为规则敏感性的并排稳健性存在, 用以证明主结论不由某一条语言学规则的取舍驱动, 同样不得并入同一过度识别式。就停刊口径而言, 本列的存活样本剔除的是 detect_defacto_cessation 判定的疑似退出覆盖媒体, 该剔除是保守代理, 目的在于检验媒体来源结构变动下 full 轨情感系数的稳定性, 而非声称严格的报纸停刊。

## VAR: exc_loughran_score_negdeg_ctx

【变体差分】
本列取 ctx 轨道: 篇章文本 = 标题 prepend + 实体窗口 (content_ctx), 即只保留标题以及目标银行实体附近的上下文窗口送入 loughran 词典打分, 在 negdeg 规则 (否定翻转 + 程度副词, 关闭转折) 下自归一化, 再在剔除疑似停刊媒体后按银行-年度取存活样本均值。ctx 轨的动机是收窄进料文本至与目标银行邻近的语段, 削弱 full 轨中无关段落对情感信号的稀释, 但代价是可能截断跨段落的情感线索。在 full-only 留篇门控下, ctx 轨是 conditional-on-full 的测度轨/稳健性轨——只在 full 轨已判为留篇的报道上计算, 其行宇宙是 full 留篇集的子集, per-track 列照常逐轨自算分子分母, 不借用 full 轨分母。相对本家族 full / ss 两列, 本列唯一差分在文本轨道: 规则臂 (negdeg)、词典 (loughran)、停刊口径 (exc) 一致, 仅进料文本从全文切换为「标题+银行实体上下文窗口」。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J。需注意 ctx 轨的实体窗口判定与 ss 轨的同句共现判定是两套不同口径: ctx 以目标银行实体的邻近上下文为界, ss 以银行与金科同句共现为界, 二者不可互相复用。就消融臂而言, 本列同样固定为 negdeg, 与 raw / negonly / degonly / advonly / negadv / degadv 及施加全规则的 canonical 无后缀得分共同构成规则消融梯度, 各臂只作并排规则敏感性、不并入同一过度识别式。就停刊口径而言, 本列在 ctx 轨上对存活媒体求篇均值, 空存活子集下保持 NaN 而非零填, 与计数类兄弟列的零填契约刻意区分, 以免真实零情感与无观测混淆。

## VAR: exc_loughran_score_negdeg_ss

【变体差分】
本列取 ss 轨道: 篇章文本 = 标题 prepend + 银行与金融科技同句共现窗口 (content_ss), 即只保留标题以及目标银行与金科词在同一句子 ±N 句窗内共现的语段 (窗宽由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 送入 loughran 词典打分, 在 negdeg 规则 (否定翻转 + 程度副词, 关闭转折) 下自归一化, 再在剔除疑似停刊媒体后按银行-年度取存活样本均值。ss 轨是三轨中进料最严的一轨, 聚焦银行与金科主题真正同句交汇之处。其回退语义镜像 ctx 轨: 当报道中不存在银行与金科的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 若金科词表 FINTECH_AC 缺失, 则该轨 is_fallback 全置 True, 优雅降级。在 full-only 门控下, ss 同为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集。相对本家族 full / ctx 两列, 本列唯一差分在文本轨道: 规则臂 (negdeg)、词典 (loughran)、停刊口径 (exc) 一致, 仅进料文本切换为「标题+银行金科同句共现窗口」。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J。就消融臂而言, 本列固定为 negdeg (否定翻转 + 程度副词, 关闭转折), 与 raw / negonly / degonly / advonly / negadv / degadv 及施加全部三条规则的 canonical 无后缀得分共同构成规则消融梯度, 各臂高度共线、只作并排规则敏感性检验、不得并入同一过度识别式。就停刊口径而言, 本列在 ss 轨上剔除疑似退出覆盖媒体后对存活样本求篇均值, 空存活子集下保持 NaN 而非零填。需特别提示: 在开发期 T=2 的小样本上, ss 轨因同句共现稀疏而常大面积回退或呈退化, 属预期现象, 生产期 T=18 全量语料下方能稳定出值; 该退化不改变本列与 full / ctx 两轨互为稳健性并排的定位。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Loughran, T., & McDonald, B. (2024). Measuring firm complexity. Journal of Financial and Quantitative Analysis, 59(6), 2487-2514. https://doi.org/10.1017/S0022109023000716
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
