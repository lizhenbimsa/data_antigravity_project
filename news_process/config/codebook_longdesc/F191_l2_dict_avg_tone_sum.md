---
family_id: F191
columns:
- dict_avg_tone_sum_ctx
- dict_avg_tone_sum_full
- dict_avg_tone_sum_ss
unit: 语调分值求和的跨词典均值 (无量纲; bank-year 内逐篇词典 score 之和, 随报道量放大, 再对六部词典取算术平均)
formula: "dict_avg_tone_sum{track} = mean_{d in DICT_NAMES}( {d}_tone_sum{track} ); {d}_tone_sum{track} = sum_{article in bank-year}( {d}_score{track} ); DICT_NAMES = {jiang_2021, yao_2021, bian_2021, du_2022, you_2018, loughran}; track in {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/geography.py
upstream:
- 22_tone_words.parquet (逐篇 {d}_score{track})
- 40_panel_export_main (encode.py::sum 聚合产 {d}_tone_sum{track})
citations:
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
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
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族 dict_avg_tone_sum 度量的是「银行—年」层面上, 六部金融情感词典各自打出的逐篇语调分值在该银行当年全部涉金融科技报道上的求和, 再对六部词典取算术平均后的综合值。它与同一生产函数隔壁的强度型均值指标 dict_avg_tone 构成一对互补测度: dict_avg_tone 走的是「逐篇比率再取平均」的集约边际 (intensive margin), 数值近似落在正负一之间, 反映一篇典型报道的语调倾向; 而本家族走的是「逐篇分值直接相加」的扩展边际 (extensive margin), 其量纲不是有界比率, 而是随该银行当年被报道篇数线性放大的累积量 —— 一家全年负面新闻既多且篇篇更负的银行, 其 tone_sum 会同时在「篇数」与「单篇强度」两个维度上被拉低。因此 tone_sum 天然吸收了媒体关注的音量 (volume) 信息, 更贴近「一年里累积压到这家银行头上的净情感总质量」这一构念, 而非单篇的平均口吻。构念根源可上溯到媒体情感对资产定价与银行负债端稳定性的经典研究: Tetlock (2007) 证明媒体悲观语调对股市有可度量的价格效应; Holzman、Miller 与 Twedt (2023) 则从另一方向刻画了这一存量的经济意义 —— 他们发现是季度盈余公告的定期硬信息披露对媒体情感 (尤其是媒体的过度乐观倾向) 起到纪律性校正作用, 而非媒体情感反过来规训披露, 换言之媒体累积语调本身是一个会被公司硬信息周期性修正、却在两次公告之间持续累积的存量。正因为媒体情感是这样一个「量与质叠加、随时间沉淀」的存量而非瞬时流量, 对逐篇分值取求和 (而非取比率均值) 的口径才与它的经济含义直接对应。

【方法学与计算】
计算链条分三段。第一段在 stage 22 (22_tone_words.parquet): 对每一篇报道、每一部词典 d, 依据该词典的正负词表并施加统一的三条语言学规则 (否定翻转、程度副词加权、转折削弱) 算出逐篇分值 {d}_score{track}。第二段在面板聚合 (encode.py): 以 sum 聚合把银行—年内全部报道的 {d}_score{track} 相加, 得到六个逐词典求和列 {d}_tone_sum{track}; 六部词典为 jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran (本仓库 tone_dicts.json 中 JSON 键 loughran_mcdonald_zh_2026、别名 loughran 的词典轨, 系将 Loughran 与 McDonald 2011 英文金融情感词表逐词中译并面向中文银行业媒体语料做本土化扩展的版本, 沿用其八类情感框架)。第三段在 geography.py: 用 _safe_mean 对这六个逐词典求和列做跨词典算术平均, 落成本家族列 dict_avg_tone_sum{track}。_safe_mean 对缺席的源列优雅返回 NaN, 因此在 golden 重生之前若某轨或某词典的源列尚未落盘, 该综合列不会崩溃而是按可得词典求平均。跨词典求平均的动机与稳健文本测度的主张一致 (Loughran & McDonald 2011; García, Hu & Rohrer 2023): 任何单一词表都带有其构造语料与领域的特异偏差, 六部词典的均值削平了词表选择这一研究者自由度, 使综合测度对「换一部词典结论就变」的批评更有抵抗力。van Atteveldt、van der Velden 与 Boukes (2021) 在方法论层面比较了人工标注、众包、词典与机器学习四条路径, 指出词典法虽召回稳定但对领域漂移敏感 —— 跨词典平均正是对这一敏感性的低成本对冲。

【文献定位】
本测度处在「财务文本情感测量三角」中的词典法顶点。相对基于机器学习的判别法 (Frankel, Jennings & Lee 2022 比较了词典法与机器学习在披露情感上的分歧) 与本仓库并行的 BERT、三家 LLM 投票法, 词典法的优势在于完全透明、零推断成本、逐词可追溯, 劣势在于无法捕捉上下文与反讽。García 等 (2023) 用大样本证明金融词汇的情感色彩本身具有可度量的横截面结构, 为词典法的效度提供了新证据。Du、Huang、Wermers 与 Wu (2022) 与 Bian、Jia、Li 与 Yan (2021) 分别构造了面向中文金融语料的情感词典, 二者均进入本家族的六部词典集合, 确保综合测度在中文媒体语境下不被英文词表 (Loughran) 的语义错位主导。在识别与推断纪律上须复述本仓库铁律: 求和口径 (本家族) 与均值口径 (dict_avg_tone)、IDF 加权口径 (dict_avg_idf_tone)、规则消融梯度各变体, 以及三条文本轨 full/ctx/ss, 彼此「各自 just-identified 并排、互为稳健性、不分主次」, 严禁把它们混进同一条 over-identified 的 Hansen J 过度识别检验 —— 它们是同一构念的替代测量而非可叠加的独立工具变量。

## VAR: dict_avg_tone_sum_full

【变体差分】
本列是 full 文本轨的求和综合语调, 也是本家族在留篇门控意义上的 canonical 轨。full 轨的文本 = 标题 prepend 到全文正文 (content_full), 即把新闻标题拼接在正文之前后整体送入词典打分, 覆盖报道的全部文字。按 2026-06-29 确立的 full-only 留篇门控口径, 一篇报道是否被计入「银行金融科技报道」宇宙, 只看该篇 full 轨的 LLM 判定 (llm_verified_full == True); 因此 full 轨的银行—年报道集合是三轨中的母集, ctx 与 ss 轨在此母集内做 conditional-on-full 的子测量。就本列而言, 求和的分母 (篇数) 与分子 (逐篇 score) 均落在这一 full 留篇集上, 逐篇 du_2022、bian_2021、jiang_2021、yao_2021、you_2018、loughran 六部词典的 full 轨分值先各自在银行—年内求和, 再跨六部取平均。相对同家族的 ctx 与 ss 轨, full 轨吸收了最完整的文本证据 (全文而非窗口), 因而在报道量大的银行—年上其求和绝对值也最大。full 轨与 ctx、ss 轨各自 just-identified 并排, 三者互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。作为主轨, 它承担综合词典情感的基准角色, 而两条窗口轨用于检验结论是否被「全文里与银行金融科技无关的段落」污染。需强调本列是求和口径而非均值口径: 与 dict_avg_tone_full (逐篇比率取平均、近似有界) 相比, 本列的数值随该银行当年 full 留篇篇数线性放大, 因此在跨银行、跨年份比较时须注意它同时编码了媒体关注的音量与单篇语调的强度, 二者不可分离 —— 这正是求和口径相对均值口径的构念取舍, 也是它作为扩展边际测度存在的意义。

## VAR: dict_avg_tone_sum_ctx

【变体差分】
本列是 ctx (实体上下文窗口) 文本轨的求和综合语调。ctx 轨的文本 = 标题 prepend 加上围绕目标实体的上下文窗口 (content_ctx), 即只保留标题与银行、金融科技实体附近的语句, 剔除全文中与主体无关的远端段落, 用以逼近「专门谈这家银行金融科技」的净文本。相对 full 轨, ctx 轨在同一 full 留篇母集内做 conditional-on-full 子测量: 报道是否留篇仍由 full 轨判定, 但本列的逐篇分值改用 ctx 窗口文本计算, 因此当一篇报道大段与银行金融科技无关时, ctx 轨会显著削弱这些无关文字对语调求和的贡献。六部词典各自在 ctx 轨上逐篇打分、银行—年内求和, 再跨词典取平均, 落成本列。ctx 轨的功能定位是首要稳健性轨: 若 full 轨的求和综合语调结论在 ctx 轨上依然成立, 则可排除「全文噪声驱动结果」的替代解释。ctx 与 full、ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J —— 它们是同一综合情感构念在不同文本切分下的平行测量, 不可当作可叠加的多重工具。与本家族 full 轨相同, 本列亦为求和口径: 逐篇 ctx 分值先在银行—年内累加再跨词典平均, 数值随留篇篇数放大而非落在有界比率区间, 故它继承了扩展边际测度对媒体音量的敏感性, 只是把每篇的语调贡献限定在实体上下文窗口之内, 从而在保留音量信息的同时净化了单篇的语调强度估计。

## VAR: dict_avg_tone_sum_ss

【变体差分】
本列是 ss (银行与金融科技同句共现窗口) 文本轨的求和综合语调, 是三轨中文本切分最严的一轨。ss 轨的文本 = 标题 prepend 加上「目标银行与金融科技词在同一句子及其前后正负 N 句窗口内共现」的语句 (content_ss, 窗口半径由 config 的 ss_sentence_radius 控制, 默认 1), 用以逼近「这家银行与金融科技被同时、同句谈及」的最窄证据。ss 轨的回退语义严格镜像 ctx 轨: 当一篇报道中不存在银行与金融科技的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 ctx 轨共享 n_articles 分母; 若金融科技 AC 自动机为空 (FINTECH_AC=None), 则该轨 *_is_fallback 全 True 优雅降级。与 full、ctx 相同, ss 轨在 full 留篇母集内做 conditional-on-full 子测量, 报道留篇仍由 full 轨判定, 本列只改用 ss 窗口文本对六部词典逐篇打分、银行—年内求和、跨词典取平均。ss 轨定位为最保守的稳健性轨: 它最大限度地排除了与银行金融科技话题不直接相邻的文字, 代价是在共现稀疏的样本上大量回退至全文而退化。ss 与 full、ctx 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。就求和口径而言, 本列同样把逐篇 ss 分值在银行—年内累加后跨六部词典取平均, 数值随留篇篇数放大; 但由于 ss 轨在共现稀疏样本上频繁回退至全文, 其求和在稠密共现的银行—年上最能体现「银行与金融科技被同句谈及」的净累积情感, 而在稀疏样本上则趋近于 full 轨口径, 这一退化行为在解读跨样本差异时须予以注意。

<!-- rendered-citations:begin -->
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
