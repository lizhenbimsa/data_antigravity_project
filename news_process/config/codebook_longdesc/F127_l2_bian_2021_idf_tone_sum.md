---
family_id: F127
columns:
- bian_2021_idf_tone_sum_ctx
- bian_2021_idf_tone_sum_full
- bian_2021_idf_tone_sum_ss
unit: 语调总和 (无量纲连续; bank-year 内逐篇 IDF 加权语调得分之和, 随留篇报道数放大, 不限于 [-1,1])
formula: "article: bian_2021_idf_score{track} = (Σ_pos idf(w)·|score(w)| − Σ_neg idf(w)·|score(w)|) / (Σ_pos idf(w)·|score(w)| + Σ_neg idf(w)·|score(w)|) ∈ [-1,1]; idf(w) = Winsorize_{P1,P99}( log10(N/(1+df(w))) / mean(log10(N/(1+df(·)))) ); panel: bian_2021_idf_tone_sum{track} = Σ_{a ∈ bank-year 留篇集} bian_2021_idf_score_a{track}"
producer: news_process/pipeline/sentiment/tone_words.py::build_idf_weights + _analyze_single_article → classify_batch (article idf_score) ; news_process/pipeline/panel/encode.py (bank-year 'sum' 聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (bian_2021_idf_score{track})
- 22_idf_weights.json (语料级 IDF 权重快照)
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
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: "Measuring news sentiment"
  venue: Journal of Econometrics
  vol: 228
  issue: 2
  pages_or_artno: 221-243
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
new_dois: []
---

## CORE

【构念与来源】
本家族三列度量的是"以 Bian 词典为极性底本、经 IDF 逆文档频率重加权后, 在银行-年层面按报道逐篇相加的语调总量"。词典底本取自 Bian, Jia, Li 与 Yan (2021) 构建的中文金融情感词典 (SSRN 3446388): 该词典专为会计与金融文本的中文语料设计, 相较通用情感词表更贴合银行、信贷、监管、金融科技等语域的褒贬用法, 是本项目六部并置情感词典之一。家族短名中的 idf 标识"逆文档频率加权"这一构造维度, sum 标识 bank-year 聚合口径为"求和"而非"求均值"。因此本家族与同底本的均值轨 bian_2021_idf_tone (逐篇取算术平均) 是同一条 IDF 加权测度链上的两个聚合端: 均值轨刻画银行当年报道的平均语调水平, 与报道条数无关; 求和轨 bian_2021_idf_tone_sum 则刻画语调的累积总量, 数值随该银行-年留篇报道数同向放大, 从而把"语调方向"与"曝光强度"耦合进单一标量。这一求和口径在实证上对应"净情感存量"式的媒体信号累积, 与 Tetlock (2007) 传统以计数或占比衡量媒体基调的思路一脉相承, 但把每篇的连续语调而非单纯正负计数纳入累加。

【方法学与计算】
计算分三步。第一步在文章层求逐篇 IDF 加权语调得分 bian_2021_idf_score{track}: 先用注入态 tone tokenizer 对每篇文本切词, 命中 Bian 词典的褒贬词按其极性归入正、负两侧, 每个命中词的幅值再乘以该词的语料级 IDF 权重, 正负两侧分别求加权和后作归一化, 得到落在闭区间 [-1,1] 的连续得分, 正值表正面语调、负值表负面语调。IDF 权重由 build_idf_weights 在全语料上一次性估计: 以平滑逆文档频率 log10(N/(1+df(w))) 为原始权重, 再除以全体情感词原始权重的均值做归一化 (使加权版得分量级与等权版可比、共享阈值), 最后对归一化权重做 P1/P99 Winsorization 抑制极端稀有词或极高频词的杠杆。文档频率 df(w) 与文档总数 N 均在"按文本内容去重后的唯一文档"上统计, 以免同一篇报道被展开成多家银行多行时虚增计数。三轨 (full/ctx/ss) 共享同一份基于 content_full 语料估计的 IDF 权重, 绝不按轨分别估权, 保证跨轨权重可比。IDF 加权的方法学根据是文本即数据范式中对高信息量稀有词赋权、压低套话高频词权重的通行做法, 其金融文本内的先例可追溯至 Jegadeesh 与 Wu (2013) 的词权重内容分析。第二步在银行-年层对逐篇得分做求和聚合 (encode 层的 'sum' 归约), 分母不做规范化。第三步经面板导出与 Stata 导出落列。

【文献定位】
本家族坐落于金融文本情感测度的词典法一支。García, Hu 与 Rohrer (2023) 在顶级金融学期刊系统检验了金融词表的极性构造, 指出词典的领域适配与词权重设定对下游测度有实质影响, 为本家族"专用中文词典 + IDF 重加权"的双重设计提供了直接的文献支撑。Du, Huang, Wermers 与 Wu (2022) 论证了中文金融情感词典相对英文词典直译的领域优越性, 与本项目并置多部中文词典 (含 Bian 词典) 互为稳健性的做法同源。方法论上, 词典法只是本项目情感测度三角的一支: Frankel, Jennings 与 Lee (2022) 比较了机器学习法与词典法披露情感, Shapiro, Sudhof 与 Wilson (2022) 给出词典法新闻情感的量化范式, Holzman, Miller 与 Twedt (2023) 则示范了媒体基调的权威加权累积——这些工作共同界定了求和口径累积语调在媒体金融研究中的解释边界。须强调: Bian 词典轨与本项目其余五部词典轨、以及 IDF 加权轨与等权轨, 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同词典或加权口径的多列混入同一 over-identified 的 Hansen J 过度识别检验。

## VAR: bian_2021_idf_tone_sum_ctx

【变体差分】
本列是 IDF 加权 Bian 语调求和的实体窗轨 (ctx track)。它与家族内其余两列的唯一差别在文本底料: ctx 轨的逐篇得分算在 content_ctx 上, 即"标题 prepend + 围绕银行/金融科技实体的上下文窗口"文本, 而非全文正文。实体窗由 stage 14 ctx_materializer 物化, 取实体命中位置周边的句子窗口拼接, 意在把语调判定聚焦到与目标实体真正相关的语段、削弱全文中与银行无关段落的语调噪声。除文本底料外, 其 IDF 权重、词典底本、归一化与 Winsorization、bank-year 求和聚合口径均与 full 轨完全一致 (IDF 权重更是三轨共用的同一份 content_full 语料估计, 不按轨重估)。在留篇口径上须明确: 全项目采用 full-only 留篇门控 (2026-06-29), 即一篇报道是否计入某银行-年的行宇宙, 只由 full 轨的 llm 判定决定; ctx 轨降为 conditional-on-full 的测度与稳健性轨, 其求和仅在 full 留篇集的子集上逐轨自算, 不另立行宇宙。定位上, ctx 轨与 full、ss 两轨互为稳健性、各自 just-identified 并排, 三轨严禁混入同一 over-identified 的 Hansen J; 三轨间是文本聚焦口径的规格稳健性并置, 而非可加分解, 相邻轨差异反映的是语调判定域的收窄程度而非某种纯效应。作为求和轨, 本列同样把语调方向与曝光强度耦合: 银行当年实体窗报道越多, 其累积总量的绝对量级越大, 因此在跨银行比较时须与报道条数或均值轨并读, 避免把高曝光误读为强语调。

## VAR: bian_2021_idf_tone_sum_full

【变体差分】
本列是 IDF 加权 Bian 语调求和的全文轨 (full track), 是家族内的首要轨与留篇门控的定义轨。其逐篇得分算在 content_full 上, 即"标题 prepend + 完整正文"文本, 覆盖报道全部可用文字, 不做实体窗或同句收窄。full 轨在三轨体系中地位特殊有二: 其一, 全项目的留篇门控是 full-only (2026-06-29)——某篇报道是否计入银行-年行宇宙, 仅由 full 轨判定裁决, 因此 full 轨定义了本家族三列共享的分母行集; 其二, 供 IDF 权重估计的语料恒为 content_full, 故 full 轨的文本底料与 IDF 估权语料严格同源, 是三轨中口径最"原生"的一轨。除文本覆盖范围最广外, 其词典底本、IDF 加权公式、归一化、Winsorization 及 bank-year 求和聚合与 ctx/ss 两轨逐字节同构。作为求和轨, 本列数值随该银行-年留篇报道数放大, 度量的是"IDF 加权净语调的累积总量"而非平均水平, 与均值轨 bian_2021_idf_tone_full 构成同链两端。定位上, full 与 ctx、ss 各自 just-identified 并排, 互为稳健性、不分主次, 三轨严禁混入同一 over-identified 的 Hansen J; full 轨作为首要轨承担主检验, ctx/ss 作条件稳健性对照。由于 full 轨文本域最宽、命中褒贬词最多, 其求和总量在三轨中通常绝对量级最大, 跨银行解读时同样须警惕曝光强度对总量的放大, 建议与 bian_2021_idf_tone_full 均值轨及留篇报道数联合判读, 以分离语调方向与媒体曝光两重信号。

## VAR: bian_2021_idf_tone_sum_ss

【变体差分】
本列是 IDF 加权 Bian 语调求和的同句轨 (ss track), 三轨中文本域最窄的一轨。其逐篇得分算在 content_ss 上, 即"标题 prepend + 银行与金融科技词在同一句 (±N 句半径, 默认半径 1) 内共现的语段"文本, 把语调判定进一步收紧到银行与金科真正同句共现的最小语境, 意在剔除仅泛泛提及银行、并无银行-金科实质关联的段落对语调的稀释。回退语义须与 CLAUDE.md 口径一致: ss 轨镜像 ctx 轨的降级逻辑——当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文正文, 并置 ss_is_fallback=True (与 ctx 的 ctx_is_fallback 同构, 共享 n_articles 分母); 若金融科技 AC 自动机为 None 则全体 *_is_fallback 置真, 优雅降级。除文本底料与回退语义外, 其 IDF 权重 (仍复用 content_full 语料估计的同一份, 不按 ss 轨重估)、词典底本、归一化、Winsorization 与 bank-year 求和聚合均与 full 轨一致。留篇仍遵 full-only 门控, ss 轨为 conditional-on-full 的稳健性轨, 在 full 留篇集子集上逐轨自算求和。定位上, ss 与 full、ctx 各自 just-identified 并排, 互为稳健性、不分主次, 三轨严禁混入同一 over-identified 的 Hansen J; 三轨是语调判定域宽窄的规格稳健性并置, 非可加分解。作为求和轨, 本列在 ss 轨的最窄语境下累积: 因同句共现语段常短于全文与实体窗, 单篇命中词数往往更少, 故 ss 轨求和总量在三轨中通常绝对量级最小, 跨银行比较时须与留篇报道数及回退占比联合判读, 以免把语境收窄导致的量级下降误读为语调转弱。

<!-- rendered-citations:begin -->
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
<!-- rendered-citations:end -->
