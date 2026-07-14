---
family_id: F272
columns:
- exc_loughran_score_raw_ctx
- exc_loughran_score_raw_full
- exc_loughran_score_raw_ss
unit: 情感倾向分值 (无量纲, 逐篇归一化后按停刊稳健子样本聚合)
formula: "exc_loughran_score_raw_<track> = mean_{i ∈ 停刊稳健子样本}(loughran_score_raw_<track>,i); loughran_score_raw = Σ(final_score) / Σ|final_score| ∈ [-1, +1] (幅度归一化, 逐词命中按词典基础极性累加再除以加权幅度绝对值和), raw = 零语言学规则端点 (不施否定翻转 / 程度副词 / 转折; 与同为零规则但口径不同的 msent_score 计数比率 (neg-pos)/(pos+neg) 勿混)"
producer: news_process/pipeline/panel/attention_media.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (loughran_score_raw_full / _ctx / _ss 文章级)
- 40_panel_export_main (媒体来源停刊检测与子样本聚合)
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"停刊稳健子样本下、由 Loughran-McDonald 词典中文主译版计算的零规则原始词典情感"这一测度。它由两条独立的构造逻辑叠合而成: 其一是词典法情感的词典与规则维度, 其二是媒体来源存续性 (停刊/幸存) 的子样本切分维度。词典维度上, loughran 指的是本项目第 6 部情感词典, 即 Loughran and McDonald (2011) 在会计金融文本分析中确立的金融领域正负面词表的中文主译版本; 其权威来源为 tone_words 的 DICT_COLUMN_ALIAS 与 encode 的 DICT_NAMES, 与其余五部中文词典 (jiang、yao、bian、du、you) 并列构成六部词典族。score_raw 中的 raw 指语言学规则消融梯度里"零规则"这一端点: 逐篇打分时不施加否定翻转、程度副词加权、转折让步三条语言学规则中的任何一条, 直接以命中正面词与负面词的裸计数构造倾向分。这与 canonical 的全规则口径 (无 raw 后缀) 相对, 是消融梯度七个非全规则变体之一, 各消融变体自归一化、彼此高度共线 (相关系数常近 0.99)、属非可加分解, 因此互为稳健性并排、不分主次, 各自 just-identified, 禁混进同一 over-identified Hansen J。子样本维度上, exc 前缀标记"停刊稳健性"子样本: 在媒体来源存续性检测中, 剔除样本期内曾经停刊的报道来源后, 仅以幸存来源的报道重新聚合词典情感, 以此检验主结论是否被那些中途退出的媒体所驱动。它与另一并列前缀 bal (平衡媒体) 同为来源结构稳健性的两条并排轨, 各自 just-identified, 禁混进同一 over-identified Hansen J。

【方法学与计算】
计算分两级。文章级由 stage 22 tone_words 产出 loughran_score_raw 的三轨版本 (full/ctx/ss), 其打分逐词累加词典基础极性得到 Σfinal_score, 再除以该篇全部命中词的加权幅度绝对值和 Σ|final_score|, 得到落在闭区间 [-1, 1] 的逐篇倾向分 (幅度归一化口径, 而非命中词计数比率), 分母为零时该篇留空; raw 端点意味着此处不做否定语境翻转、不按程度副词缩放、不因转折词调整权重, 仅以词典基础极性直接累加幅度归一化。该幅度归一化口径与另一同为零规则的 msent_score 计数比率 (neg-pos)/(pos+neg) 是两套不同构造, 源码明确警示二者勿混淆。面板级由 attention_media.py 承接: 该模块是 panel runner 在步骤 6b/6b-2/6c 调用的库函数, 无独立入口, 复用 encode 的 logger 写入共享的 40_panel_export_main 日志。停刊检测借助一组情感列前缀 (_SCORE_PATTERNS) 动态发现待聚合的分值列, loughran_score_ 为其中之一; 检测识别出样本期内停刊的来源后, 将其报道排除在 exc 子样本之外, 再在幸存来源上按银行-年重新求均值, 得到 exc_loughran_score_raw 的三轨面板列。需要强调, 前缀表曾在新增第 6 部 loughran 词典时漏列该前缀, 导致 exc_loughran_* 与 bal_loughran_* 两族相对其余五部词典缺列; 修补后六部词典走完全相同的动态发现路径, exc_loughran_* 一族的列后缀结构 (三轨 × 规则消融梯度各变体) 与 exc_jiang_2021_* 等其余五部词典对齐一致, 不再相对其余词典缺列。留篇与门控口径遵循 full-only 原则: 一篇是否计为银行金科报道只看 full 轨的 LLM 判定, ctx 与 ss 轨为条件于 full 留篇集的子集测度。

【文献定位】
词典法金融情感的方法学基石是 Loughran and McDonald (2011), 该文首次系统论证通用情绪词表在金融文本上的失真, 并给出金融领域专用正负面词表, 成为此后十余年文本情感研究的事实标准; 本家族的 loughran 词典正是其词表的中文主译。Loughran and McDonald (2016) 的综述进一步梳理了词典法在会计金融中的适用边界与消融敏感性, 为本项目将规则消融物化为并排稳健性梯子提供依据。Frankel, Jennings, and Lee (2022) 在 Management Science 上直接比较机器学习与词典法的披露情感测量, 支持将词典法作为与 LLM、BERT 三方法互为稳健的一轨而非唯一真值。van Atteveldt, van der Velden, and Boukes (2021) 从效度角度比较人工标注、众包、词典与机器学习, 提示词典法在特定语域下系统偏差的存在, 正是本项目保留停刊/平衡两类来源结构稳健性子样本的动因。Barbaglia et al. (2025) 展示经济文本上基于词典的情感抽取, 佐证 raw 零规则端点作为最保守读数的合理性。

## VAR: exc_loughran_score_raw_ctx

【变体差分】
本列是停刊稳健子样本下 loughran 零规则原始词典情感的 ctx 轨版本。ctx 轨的文本口径为"标题 prepend + 实体上下文窗口": 在 stage 14 ctx_materializer 物化的 content_ctx 上打分, 仅保留围绕目标实体 (银行/金科词) 的邻近窗口文本, 而非全文正文。相对 full 轨, ctx 轨聚焦实体附近语境, 削弱了远离实体的段落对倾向分的稀释, 属条件于 full 留篇集的子集测度与稳健性轨。与家族内 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。就消融维度而言, 本列固定在 raw 零规则端点 (不做否定翻转、程度副词、转折), 与全规则 canonical 及其余六个消融变体互为稳健性并排; 就子样本维度而言, 本列固定在 exc 停刊稳健子样本 (剔除样本期内停刊来源), 与 bal 平衡媒体轨、与无前缀全样本轨并排。ctx 轨的价值在于它把打分注意力收束到目标实体的直接语境, 因此当同一篇报道以银行或金科为由头却夹带大量无关行业背景段落时, ctx 轨的倾向读数比 full 轨更不易被这些无关段落的正负面词稀释或反向拉扯; 这一收束在停刊稳健子样本上尤为有意义, 因为退出媒体往往偏好某类版面结构, 剔除后的实体窗口情感更能反映幸存主流来源的真实笔调。判定实体窗口时银行侧采用否定加短名过滤、金科侧采用裸 AC 词表的非对称口径, 与 ss 轨的严格同句口径属两套不同判据, 禁互相复用。在开发期 T=2 的极小盘面上, ctx 轨可能因实体窗口稀疏而出现退化取值或零方差, 属预期现象, 生产期 T=18 恢复正常。

## VAR: exc_loughran_score_raw_full

【变体差分】
本列是停刊稳健子样本下 loughran 零规则原始词典情感的 full 轨版本, 是本家族三轨中语料最完整的一轨。full 轨的文本口径为"标题 prepend + 全文正文": 在 content_full 上逐篇打分, 覆盖报道全部正文, 不做实体窗口裁剪。按 full-only 留篇门控, 一篇是否计入银行金科报道只由 full 轨的 LLM 判定决定, 因而 full 轨的行宇宙是三轨的母集, ctx 与 ss 均为其子集测度。本列同样固定在 raw 零规则消融端点与 exc 停刊稳健子样本两个坐标上: raw 端点给出最保守、不受语言学规则处理影响的裸倾向读数, exc 子样本剔除样本期内曾停刊的报道来源以检验主结论对媒体退出的敏感性。与 ctx、ss 两轨, 与全规则及其余消融变体, 与 bal 平衡媒体轨、无前缀全样本轨, 均互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。作为语料最完整的一轨, full 轨在停刊稳健性检验中承担主证角色: 若无前缀全样本的 loughran 情感在剔除停刊来源后仍与 exc 子样本读数方向一致、量级相近, 即说明主结论并非由中途退出媒体的选择性笔调所驱动, 这正是 exc 轨设置的目的。之所以选择 raw 零规则端点而非全规则口径进入本子样本检验, 是因为零规则读数不叠加语言学处理带来的额外自由度, 给出对词表命中最直接、最保守的情感刻画, 使停刊稳健性结论不至于与规则实现细节纠缠。需注意 loughran 词典在项目历史上曾因前缀表漏列而使 exc_loughran_* 与 bal_loughran_* 族相对其余五部词典缺列, 修补后本列走与 exc_jiang_2021_* 一致的动态发现与聚合路径, 六部词典各自的 exc_* 与 bal_* 列后缀结构对齐。

## VAR: exc_loughran_score_raw_ss

【变体差分】
本列是停刊稳健子样本下 loughran 零规则原始词典情感的 ss 轨版本。ss 轨的文本口径为"标题 prepend + 银行与金科同句共现窗口": 在 stage 14 物化的 content_ss 上打分, 仅取目标银行与金科词落在同一句子正负若干句半径 (由 filtering 配置 ss_sentence_radius 决定, 默认 1) 内的片段。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金科同句共现时, content_ss 回退为全文正文并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母; 当金科 AC 词表为空时优雅降级为全 fallback。ss 轨是三轨中语境约束最严的一轨, 属条件于 full 留篇集的子集测度与稳健性轨。本列在消融维度固定 raw 零规则端点, 在子样本维度固定 exc 停刊稳健子样本。与 full、ctx 两轨, 与全规则及其余消融变体, 与 bal 平衡媒体轨, 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。ss 轨的严格同句共现口径由 entity_context 的 extract_bank_fintech_cooccurrence 原语实现, 与 stage 13 共现硬过滤所用的 has_bank_fintech_cooccurrence_within_radius 是两套不同口径, 禁互相复用: 前者要求银行与金科落在同一句半径窗内并据此裁出超级文档, 后者只做行级保留判定。因此 ss 轨给出的是三轨中语境约束最强、最贴近"银行与金科被直接放在一起讨论"这一构念的情感读数, 在停刊稳健子样本上尤能排除退出媒体因版面拼贴而带来的伪共现噪声。本列固定 raw 零规则端点与 exc 停刊稳健子样本两坐标。开发期 T=2 上 ss 轨常因同句共现稀疏而零方差退化, 属预期, 生产期 T=18 恢复。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
<!-- rendered-citations:end -->
