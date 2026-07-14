---
family_id: F153
columns:
- city_leave1out_dict_tone_ctx
- city_leave1out_dict_tone_full
- city_leave1out_dict_tone_ss
unit: 语调得分 (无量纲, 约 [-1,1]; 同城他行年度均值, bank-year 级)
formula: "city_leave1out_dict_tone{track}_{i,t} = (Σ_{j∈city(i), j≠i} dict_avg_tone{track}_{j,t}) / (N_{city(i),t} − 1); track ∈ {_full,_ctx,_ss}; 分组键 = (bank_city, year), 排除自身 i"
producer: news_process/pipeline/panel/geography.py::compute_leave_one_out_sentiment
upstream:
- 22_tone_words.parquet (dict_avg_tone_full / dict_avg_tone_ctx / dict_avg_tone_ss)
- 40_panel_yearly.parquet (bank_city, year, 逐轨 dict_avg_tone 聚合列)
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
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
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
- doi: "10.1002/isaf.1549"
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  venue: "Intelligent Systems in Accounting, Finance and Management"
  type: "journal"
new_dois:
  - "10.1002/isaf.1549"
---

## CORE

【构念与来源】
本家族三列 city_leave1out_dict_tone_{full,ctx,ss} 是"同城他行留一平均词典语调" (city leave-one-out dictionary tone), 是一个空间聚合的银行-年度工具变量 (instrumental variable) 度量, 而非某家银行自身的情感读数。它回答的问题是: 对某家注册地在某城市的银行 i, 在年份 t, 与它同城注册的其他所有银行 (排除 i 自身) 的媒体报道综合词典语调平均是多少。构念的直接对象因此是"地方媒体情绪场"对 i 施加的外生推力, 而不是 i 的经营基本面。它服务于计量识别: 当研究者关心某家银行自身新闻语调对其融资成本、存款稳定性、金融科技投资等结果变量的因果影响时, 银行自身语调是内生的 (媒体报道既反映也影响银行状态), 而"同城他行语调"在合理排他性假设下只经由"共同的地方媒体环境/同侪压力"影响 i, 不直接进入 i 的结果方程, 从而可作为工具变量。数据来源沿两条上游: 一是词典法综合语调 dict_avg_tone, 它分两阶段成形: 先由 stage 22 tone_words 在六部中文金融情感词典上逐篇、逐词典分别打分并各自归一化到约 [-1,1], 再由 stage 40 geography.py::compute_composite_indicators 对六部词典的逐篇分做跨词典综合 (_safe_mean 取有效词典均值) 得到综合语调 dict_avg_tone{track}; 二是银行注册地城市 bank_city (取自银行注册地地理信息骨架)。故"逐篇打分"在 stage 22、而"跨词典综合"落在 stage 40, 二者不可混为同一阶段。留一平均在 stage 40 面板导出阶段由 geography.py 计算, 落 bank-year 面板。

【方法学与计算】
计算原语是分组留一均值。对给定轨道 track 与其源列 dict_avg_tone{track}, 先按 (bank_city, year) 分组, 求组内和 grp_sum 与组内有效计数 grp_cnt; 对组内每个观测 i 取 leave1out_i = (grp_sum − dict_avg_tone_i) / (grp_cnt − 1), 即"除我之外的本地年度平均"。这里须精确区分本家族在 geography.py 内的实际执行路径: dict_tone 三列并非走处理 llm_vote_tone 的第一循环, 而是走 G-08「多情感度量 LOO IV 扩展」的第二循环 (该循环对 dict_avg_tone 与 bert_avg_pos 两类源测度、按省级与城市级两种地理键成对产出, 本家族取其中 bank_city × dict_avg_tone 的三轨切片)。第一循环为 llm 分支在 python -O 下加装了三道显式 raise 前置守卫 (源语调不得含空值、组频数不得为 NaN、组内有效银行数须 ≥2 使分母 grp_cnt − 1 > 0), 但这三道 raise 仅存在于该 llm 分支, 并不覆盖本家族; dict_tone 所在的第二循环无任何显式 raise, 其留一分母的合法性仅由两道隐式掩码保证: 其一是分组前的前置掩码, 要求 bank_city 非空且源语调 dict_avg_tone{track} 非 NaN, 剔除空注册地城市与缺分的行; 其二是 valid_idx = grp_cnt > 1 选择掩码, 只对组内有效银行数 ≥2 的观测赋值, 单一银行组 (singleton) 不出值记 NaN 而非除零。第二循环另设一道 len(subset) < 5 的规模跳过守卫: 某 (地理键, 轨) 组合下有效样本不足 5 行则整轨跳过、不产列。因此本家族的分母非零并非靠 -O 下存活的 raise 硬断言强制终止, 而是靠 notna 前置掩码与 grp_cnt > 1 选择掩码的组合隐式实现——二者在语义上等价地排除了除零, 但违例时静默记 NaN 而不抛错, 这是解读本列缺失值口径时须知的关键差别。空注册地城市 (bank_city == '') 的行被前置掩码剔除, 不进入任何城市组。列名词干的对称是一处历史命门: 原始产出列名 city_leave1out_dict_avg_tone_full 长 33 字符超 Stata 32 字符变量名上限, 会被单侧缩写导致 .dta 内三轨词干不对称、Stata 通配只捕获部分轨; 修复方案是把 dict_avg_tone 词干成对压缩为 dict_tone, 使 full/ctx/ss 三轨全部 ≤32 字符且词干对称。这一压缩纯属命名工程, 不改变数值语义: 本家族的 dict_tone 与文章级 dict_avg_tone 是同一综合词典语调, 只是列名更短。三轨源列 dict_avg_tone{track} 若某轨未落盘 (常见于 ss 轨在极稀语料下缺列), 守卫优雅跳过该轨, 不牵连其余轨。

三轨 full/ctx/ss 各自独立走上述留一聚合, 是三条并排的规格稳健性轨: full = 标题 prepend 后的全文正文; ctx = 标题加实体上下文窗口; ss = 标题加"银行与金融科技同句±N窗"共现文本, 其回退语义镜像 ctx (无同句共现时 ss 退化为全文 body)。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨的留一 IV 混进同一个 over-identified 的 Hansen J 过度识别检验; 若研究者要做过度识别, 正确做法是在同一轨内并列多个"独立情感度量"的留一 IV (词典法综合、LLM 投票语调、BERT 正面概率三者), 而非跨轨拼接。留篇门控采 full-only 口径 (2026-06-29): 一篇报道是否计入某银行-年的语料由 full 轨判定, ctx/ss 是 conditional-on-full 的子集测度; 因此三轨的城市组银行集是嵌套的, ss 轨的有效样本量通常最小。

【文献定位】
本度量把两支文献焊在一起。词典法情感测量一支: Loughran 与 McDonald (2011) 奠定了金融文本须用领域词典而非通用词典的方法论, García、Hu 与 Rohrer (2023) 进一步给金融词汇标注方向色彩, Du、Huang、Wermers 与 Wu (2022) 构建中文金融情感词典并揭示领域与语言特异性, 三者共同支撑本项目"六词典综合、逐篇归一"的 dict_avg_tone 源测度; Frankel、Jennings 与 Lee (2022) 则以机器学习对照词典法, 论证词典法在披露情感上仍具竞争力, 为把词典语调当作一条独立情感度量 (而非 LLM/BERT 的次等替身) 提供依据。媒体情绪的资产定价后果一支: Tetlock (2007) 证明媒体语调对市场有可度量的实质影响, 为"地方媒体情绪场经由同侪渠道外生推动 i"的排他性叙事提供机制基础。识别工具一支: Goldsmith-Pinkham、Sorkin 与 Swift (2020) 系统梳理 Bartik/份额-移动型工具变量的识别逻辑与检验, 留一同侪均值正是这一族空间/同侪工具的近亲, 其"排除自身、组内他体均值作外生推力"的构造与本度量同源。综合而言, city_leave1out_dict_tone 不是一个情感构念本身, 而是把词典情感这一被充分验证的测度, 经由城市-年度留一聚合改造为一件识别工具。Todd, Bowden 与 Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述了金融文本情感分析(含词典法与机器学习法)的最新进展与未来方向, 为本家族以词典法综合语调作为独立情感度量源 (dict_avg_tone) 提供最新方法论定位。

## VAR: city_leave1out_dict_tone_ctx

【变体差分】
本列是 ctx 轨的同城他行留一平均词典语调。与家族口径完全一致的空间聚合逻辑 (按 bank_city、year 分组, 排除自身取组内他行均值, singleton 组记 NaN, 空城市剔除), 唯一差分维度是源语调所依附的文本轨: 本列的源列是 dict_avg_tone_ctx, 即"标题 prepend + 实体上下文窗口"文本上的六词典综合语调。ctx 轨相对 full 轨收窄了打分文本, 只保留银行实体附近的上下文窗口, 因而对"报道是否真的在谈这家银行"更敏感、对与银行无关的段落噪声更钝。留一聚合在此轨内自洽: 城市组内每家他行的 ctx 语调先各自算好, 再对同城他行 (排除 i) 求年度平均。本列与家族的 full、ss 两列各自 just-identified 并排、互为稳健性、不分主次, 严禁把本 ctx 留一 IV 与另两轨的留一 IV 混进同一个 over-identified 的 Hansen J 过度识别检验; 跨轨只做规格稳健性对照, 过度识别须在同一轨内换用不同情感度量 (词典/LLM/BERT) 的留一 IV。因留篇门控采 full-only, ctx 轨语料是 full 留篇集的子集, 城市组的有效他行数不大于 full 轨, 故本列在稀薄城市-年更易落入 singleton 而记 NaN。若 dict_avg_tone_ctx 源轨在某次运行缺列, 本列优雅跳过不出值, 不牵连 full 列。实务上本列常作 full 主轨工具的稳健性对照臂: 当结果对 ctx 与 full 两轨的同城他行工具都成立时, 可排除"识别力全靠全文噪声段落"的质疑, 增强排他性叙事的可信度。

## VAR: city_leave1out_dict_tone_full

【变体差分】
本列是 full 轨的同城他行留一平均词典语调, 也是本家族的 canonical 轨。空间聚合逻辑与家族口径逐字一致 (bank_city × year 分组、排除自身、组内他行均值、singleton 记 NaN、空城市剔除), 差分维度是源文本轨: 本列源列为 dict_avg_tone_full, 即"标题 prepend + 全文正文"上的六词典综合语调, 覆盖报道全文、信息面最宽。full 轨是本项目留篇门控的判定轨 (full-only 口径, 2026-06-29): 一篇报道是否计入某银行-年语料由 full 轨认定, 因此 full 轨的城市组银行集是三轨中最全的超集, 本列的城市-年有效样本量在三轨中最大、最少落入 singleton, 作为主工具变量轨最稳。它与 ctx、ss 两列各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨留一 IV 混入同一个 over-identified 的 Hansen J; 需要过度识别时, 在 full 轨内并列词典法综合、LLM 投票语调、BERT 正面概率三种独立情感度量的留一 IV。作为主轨, 本列亦是下游 ivreghdfe 规格里把银行自身语调 (如 llm_vote_tone_full 或 dict_avg_tone_full) 作内生变量、以同城他行语调作外生工具时的首选工具列, 其排他性依赖"地方媒体情绪场只经由同侪渠道、不直接进入 i 的结果方程"这一假设。作为主轨, 本列在弱工具诊断 (第一阶段 F 值) 与相关性检验中表现最稳, 因其城市组样本最全、留一均值方差最小、对个别银行报道的极端语调不敏感; 而 ctx、ss 两轨因样本收窄, 更多承担"换文本口径后结论是否漂移"的规格稳健性检验角色, 三轨证据并置方构成完整的工具变量稳健性梯子。

## VAR: city_leave1out_dict_tone_ss

【变体差分】
本列是 ss 轨的同城他行留一平均词典语调。空间聚合逻辑与家族口径一致, 差分维度为源文本轨: 源列 dict_avg_tone_ss 是"标题 prepend + 银行与金融科技同句±N窗共现文本"上的六词典综合语调, 是三轨中最窄、最聚焦"银行∧金科同句共现"语境的一轨。其回退语义镜像 ctx: 当某篇报道无银行与金融科技的同句共现时, ss 文本优雅退化为全文 body、以 is_fallback 标记, 因此 ss 语调在共现稀薄的语料上会向 full 轨靠拢。留一聚合在 ss 轨内自洽 (同城他行各自的 ss 语调先算好, 再排除 i 求年度均值)。因留篇门控采 full-only, ss 轨语料是 full 留篇集的子集且通常最小, 故本列的城市组有效他行数在三轨中最少, 最易落入 singleton 而记 NaN, 在开发规模 (T 小、语料稀) 下甚至可能整轨缺列——此时 geography.py 的 `if tone_col not in panel.columns` 守卫使本列优雅跳过, 不牵连 full、ctx 两列出值。本列与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨留一 IV 混进同一个 over-identified 的 Hansen J; 跨轨仅作规格稳健性对照, 过度识别须在 ss 轨内换用不同情感度量的留一 IV 完成。本列的价值在于把工具的语义边界收到最紧: 只有当报道确实在同一句里同时谈及银行与金融科技时才计入语调, 因而 ss 轨的同城他行工具最贴近"金融科技相关的地方媒体情绪场"这一狭义机制。若主结论在如此严苛的文本口径下仍由 ss 留一工具支撑, 则对排他性与机制解释都是最强的稳健性证据; 反之, 在开发规模稀薄语料上本列大面积 NaN 属预期退化, 不应据此否定 full 主轨的识别力。

<!-- rendered-citations:begin -->
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
<!-- rendered-citations:end -->
