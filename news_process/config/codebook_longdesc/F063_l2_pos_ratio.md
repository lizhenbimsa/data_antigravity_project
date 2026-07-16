---
family_id: F063
columns:
- avg_pos_ratio_ctx
- avg_pos_ratio_full
- avg_pos_ratio_ss
- avg_pos_ratio_std_ctx
- avg_pos_ratio_std_full
- avg_pos_ratio_std_ss
unit: 比率 (正面词占比, 无量纲, 值域 [0,1]); std 列为同一比率在 bank-year 单元内的样本标准差 (无量纲, 非负)
formula: "pos_ratio{track} = |正面极性匹配词| / n_words{track} (文章级, 固定 6 词典 union 词表); avg_pos_ratio{track} = mean_{i∈bank-year}(pos_ratio_i{track}); avg_pos_ratio_std{track} = std_{i∈bank-year}(pos_ratio_i{track})"
producer: pipeline\sentiment\tone_words.py (文章级 pos_ratio 打分) ; pipeline\panel\encode.py (bank-year 聚合 mean/std)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 21_tone_llms.parquet (full-only 留篇门控)
- 22_tone_words.parquet (文章级 pos_ratio{track} 源列)
citations:
- doi: 10.1007/s10479-025-06567-y
  type: journal
  authors: Anastasiou, D., Katsafados, A., & Tzomakas, C.
  year: 2026
  title: "Banks' stock price crash risk prediction with textual analysis: A machine learning approach"
  venue: Annals of Operations Research
  vol: 357
  issue: 1
  pages_or_artno: 89-111
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics and Finance
  vol: 91
  issue: ""
  pages_or_artno: 1150-1172
- doi: 10.1093/rfs/hhad044
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A.
  year: 2023
  title: "Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1"
  venue: Review of Financial Studies
  vol: 36
  issue: 12
  pages_or_artno: 4919-4964
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1093/qje/qjx045
  type: journal
  authors: Hansen, S., McMahon, M., & Prat, A.
  year: 2018
  title: "Transparency and deliberation within the FOMC: A computational linguistics approach"
  venue: Quarterly Journal of Economics
  vol: 133
  issue: 2
  pages_or_artno: 801-870
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一篇银行金融科技新闻的"正面词覆盖强度", 即文本中被判定为正面极性的词语所占的比重, 再聚合到 bank-year 面板层。文章级原语是 pos_ratio{track}, 定义为该篇文本命中的正面极性匹配词数除以该轨分词后的总词数, 值域落在闭区间零到一之间, 数值越大表示正面用语在报道语言中占据的密度越高。该原语在 stage 22 由 pipeline\sentiment\tone_words.py 产出, 随后在 pipeline\panel\encode.py 内以 bank-year 单元为组做两种一阶矩/二阶矩聚合: avg_pos_ratio{track} 取组内文章 pos_ratio 的算术均值, 度量该银行该年报道的平均正面词密度; avg_pos_ratio_std{track} 取组内样本标准差, 度量同一 bank-year 内不同报道之间正面词密度的离散程度, 即报道口径的一致性/异质性。两者互为水平与离散的配对读数, 不可互相替代。

【方法学与计算】
正面词的判定基础不是逐篇临时择优的最佳词典, 而是六部中文金融情感词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 / loughran_mcdonald_zh_2026, 即 Loughran 与 McDonald 2011 中文主译本) 经 build_union_dictionary 合并出的固定 union 词表。该固化处理 (fix omni-g-tonewords-01/-05) 将计数基从"跨观测漂移的 best-dict"改为跨全样本恒定的并集词表, 使正面词频成为一个不随观测切换测量工具的构念, 兑现 Tetlock (2007)、Garcia (2013) 与 Henry (2008) 所主张的固定词表口径。合并时对同时出现在某词典正负两侧的重叠词, 按用户 2026-06-24 决策以对称双票 (加一, 减一) 喂入 union, 极性 margin 守恒, 保证 union 逐位可复现。分词由 jieba 静默初始化完成, frozenset 加速 O(1) 查表, joblib 并行分批。需强调的是, pos_ratio 是纯正面覆盖率读数, 只数正面命中而不做净化: 它不等于净语调 (pos 减 neg 类的 tone/msent), 也不减去负面词, 因此可与同源的 neg_ratio 配对, 支持对正负两侧非对称反应的分离检验, 呼应 Berger、Kim 与 Ma (2024) 关于正负面词信息含量不对称的发现, 以及 Loughran 与 McDonald 2011 主张的正负分列而非合成的口径。文章级 pos_ratio 不叠加否定翻转、程度副词与转折加权这些语言学规则 (那些规则服务于 msent/score 型净语调), 故它是"未加权的原始极性覆盖率", 语义上更接近词频统计而非语气强度。

【文献定位】
把新闻文本的词频占比作为可回归的银行级信号, 属于计算语言学与金融文本分析的主流范式。Hansen、McMahon 与 Prat (2018) 在 FOMC 语料上以词频与主题计数刻画沟通内容, 示范了词级计数如何成为稳健的可解释度量; Li、Mai、Shen 与 Yan (2021) 用机器学习词表法度量企业文化, 佐证固定词表的正面/价值类词频在跨样本比较中的构念效度; Hassan、Hollander、van Lent、Schwedeler 与 Tahoun (2023) 以固定 bigram 词表在公司电话会议文本上计数敞口, 与本家族"固定 union 词表逐篇计数再归一"的方法学同源。在银行与中国语境的对接上, Chen、Goldstein、Huang 与 Vashishtha (2022) 揭示银行披露透明度经由存款流动影响银行, 说明银行文本信息具真实经济后果; Fang、Wang、Wang 与 Yuan (2024) 直接在中国银行级媒体情感与存款稳定/系统性风险之间建立联系, 与本家族的样本域和被解释对象高度契合; Anastasiou、Katsafados 与 Tzomakas (2026) 进一步以银行文本分析预测股价崩盘风险, 印证正面/负面词密度类文本测度的预测价值。

【三轨与门控口径】
三轨 full / ctx / ss 分别对应标题加全文正文、标题加实体窗口、标题加银行与金科同句窗口三种文本切片, 由 stage 14 ctx_materializer 物化。留篇门控为 full-only (2026-06-29): 一篇报道是否计入某 bank-year 的行宇宙, 只看 full 轨经 stage 21 LLM 精筛确认 (llm_verified_full 为真); ctx 与 ss 轨降为 conditional-on-full 的测度轨与稳健性轨, 其行集是 full 留篇集的子集, per-track 列在此子集上照算。三轨严格互为稳健性、各自 just-identified 并排、不分主次, 铁律是禁止把三轨混进同一个 over-identified 的 Hansen J 检验; ss 轨在无银行与金科同句共现时按镜像 ctx 的回退语义降级为全文正文并置 fallback 标记。本家族为非嵌入的词频测度, 不产生 co-primary 双轨的 _lg 孪生列。

## VAR: avg_pos_ratio_ctx

【变体差分】
本列是家族水平读数在 ctx 轨上的实例: 对每个 bank-year 单元, 取该单元内各篇报道 pos_ratio_ctx 的算术均值。与 canonical 的 full 轨版本相比, 唯一差别在文本切片: ctx 轨的文本 = 标题 prepend 后再拼接实体上下文窗口 (content_ctx), 即只保留围绕目标实体的邻近语句而非整篇正文, 因此正面词密度是在更聚焦、更短的实体相关片段上度量的。由于门控为 full-only, 本列的行宇宙是 full 留篇集的子集, 属 conditional-on-full 的测度轨/稳健性轨, 不改变留篇判定。它与 avg_pos_ratio_full、avg_pos_ratio_ss 互为稳健性、不分主次、各自 just-identified 并排, 铁律是三轨禁混进同一 over-identified Hansen J。当某 bank-year 内 ctx 源列缺失 (旧 parquet 未回填) 时, valid_agg 过滤令本列优雅缺席而不借 full 分母。相对同轨的 std 列, 本列只报水平不报离散, 二者须配对解读: 高均值不必然对应低离散。方法学上本列继承家族的固定 6 词典 union 词表口径, 不随观测切换测量工具, 也不叠加否定翻转与程度副词等语言学规则, 故它是实体聚焦片段上的未加权正面覆盖率均值, 而非语气强度。因 ctx 切片较 full 更短, 单篇 pos_ratio_ctx 的方差通常更高, 聚合到均值后仍可能与 full 轨读数出现系统性水平差, 这一差异本身即三轨互为稳健性的信息来源, 应作为规格稳健性并排解读而非视为不一致。

## VAR: avg_pos_ratio_full

【变体差分】
本列是家族的 canonical 水平读数, 定义在 full 轨上: 对每个 bank-year 单元, 取该单元内各篇报道 pos_ratio_full 的算术均值; pos_ratio_full 由固定 6 词典 union 词表在 content_full (标题 prepend 后拼接全文正文) 上逐篇计数正面词并除以该轨总词数得到。full 轨同时是留篇门控轨: 一篇报道是否计入本 bank-year 的行宇宙以 llm_verified_full 为准 (full-only, 2026-06-29), 故本列的分母语料与门控口径完全一致, 是三轨中信息最完整、最贴近"整篇报道正面用语密度"的读数。它与 ctx、ss 两轨的同名列互为稳健性、不分主次、各自 just-identified 并排, 铁律禁止三轨混进同一 over-identified Hansen J。作为水平列, 它只回答"平均而言这家银行这一年的报道正面词占多大比重", 与 avg_pos_ratio_std_full 报告的组内离散配对使用; 同时它是纯正面覆盖率, 不减负面、不加语言学规则, 因此与净语调/msent 家族正交, 应与同源 neg_ratio 家族并列进入正负非对称检验而非合成单一 tone。在识别策略上, 因 full 轨同时是留篇门控轨, 本列的样本框与被解释银行的报道宇宙完全对齐, 是三轨中唯一分母语料与门控口径逐篇一致者, 故当研究者只需单一水平代理时, 应以本列为首选主轨, 而将 ctx、ss 两轨保留为规格稳健性。需强调本列度量的是正面用语的相对密度而非绝对篇数, 已对报道长度做归一, 因此不受某银行某年报道条数多寡的机械驱动; 报道条数信息另由 n_articles 类列承载, 二者不可混淆。

## VAR: avg_pos_ratio_ss

【变体差分】
本列是家族水平读数在 ss 轨上的实例: 对每个 bank-year 单元, 取该单元内各篇报道 pos_ratio_ss 的算术均值。ss 轨的文本 content_ss = 标题 prepend 后拼接"银行与金融科技同句共现的正负 N 句窗口" (句半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认一句), 是三轨中最严格、最聚焦银行金科共现语境的切片, 因此其正面词密度反映的是共现语境内的正面用语强度。ss 轨的回退语义镜像 ctx: 当某篇无银行与金科同句共现时, content_ss 回退为全文正文, ss_is_fallback 置真并共享 n_articles 分母, 属优雅降级而非丢行。留篇门控仍为 full-only, 本列行宇宙是 full 留篇集子集, 属 conditional-on-full 稳健性轨。它与 full、ctx 同名列互为稳健性、不分主次、各自 just-identified 并排, 铁律是三轨禁混进同一 over-identified Hansen J。在 T 较小的开发样本上 ss 轨可能因共现稀疏而退化, 属预期现象, 生产 T=19 语料上恢复正常方差。方法学上本列同样采用固定 6 词典 union 词表逐篇计数、除以该轨总词数, 不叠加语言学规则, 故是共现语境内的未加权正面覆盖率均值。相较 full 与 ctx 两轨, ss 轨的判定口径最严格 (银行与金科须同句共现), 因此本列对"银行金科议题本身的正面框定"最敏感, 而对与该议题无关的泛正面报道语言最不敏感; 这一构念聚焦使本列在三轨中最贴近论文核心处理变量的语境, 但也最易受共现稀疏与回退比例的影响, 解读时须结合 ss_is_fallback 的占比一并披露。它与同轨 avg_pos_ratio_std_ss 报告的离散配对使用, 水平与离散正交。

## VAR: avg_pos_ratio_std_ctx

【变体差分】
本列是家族离散读数在 ctx 轨上的实例: 对每个 bank-year 单元, 取该单元内各篇报道 pos_ratio_ctx 的样本标准差, 度量在实体上下文窗口切片上, 同一银行同一年不同报道之间正面词密度的分散程度, 即报道口径的一致性。与同轨的水平列 avg_pos_ratio_ctx 是配对读数: 前者答"平均多高", 本列答"篇际有多不一致"。数值为无量纲非负数, 当某 bank-year 仅一篇有效报道时标准差不可定义, 按聚合口径产出 NaN。差分维度与家族其它 std 列的唯一区别是文本轨: ctx 轨只在实体邻近窗口上计数, 故本列捕捉的是聚焦片段口径下的篇际异质性。门控为 full-only, 行宇宙为 full 留篇集子集, 属 conditional-on-full 稳健性轨; 本列与 full、ss 轨的 std 列互为稳健性、不分主次、各自 just-identified 并排, 铁律禁止三轨混进同一 over-identified Hansen J。离散读数常用于刻画媒体对该银行金科议题的分歧或口径统一度, 与水平读数正交, 不应互相替代。构念上, 高离散可解读为报道对该银行正面框定的分歧或多元, 低离散可解读为口径趋同或存在统一的宣传/引用模板, 这一维度无法由水平均值反推, 因此本列携带独立于 avg_pos_ratio_ctx 的信息。方法学口径与家族一致: 计数基为固定 6 词典 union 词表, 逐篇 pos_ratio 已对轨内总词数归一, 故本列度量的是密度的篇际标准差而非绝对词数的波动, 不受报道长度或条数的机械放大。当研究关心媒体一致性/分歧作为机制变量时, 本列可作为 ctx 轨的代理并与 full、ss 轨的同名离散列并排做规格稳健性。

## VAR: avg_pos_ratio_std_full

【变体差分】
本列是家族离散读数在 canonical 的 full 轨上的实例: 对每个 bank-year 单元, 取该单元内各篇报道 pos_ratio_full 的样本标准差, 度量整篇口径下不同报道之间正面词密度的分散程度。它是水平列 avg_pos_ratio_full 的离散配对: 同一均值可对应截然不同的篇际一致性, 高标准差意味着这家银行这一年的报道在正面用语浓度上分歧较大, 低标准差意味着口径趋同。full 轨同时是留篇门控轨 (full-only, 2026-06-29), 本列分母语料与门控完全一致, 是三轨离散读数中信息最完整者。数值无量纲非负, 单篇 bank-year 单元的标准差不可定义而产出 NaN。差分维度与 ctx、ss 轨的 std 列只在文本切片上不同: full 轨在整篇正文上计数。三轨 std 列互为稳健性、不分主次、各自 just-identified 并排, 铁律禁止混进同一 over-identified Hansen J。作为纯正面覆盖率的离散, 它与净语调离散、msent 家族正交, 宜与同源 neg_ratio 的离散读数并列用于正负两侧异质性的非对称分析。作为 canonical 离散读数, 本列是三轨 std 中样本框与门控最对齐者, 当研究者只需单一离散代理时应以本列为首选主轨。构念解读上, avg_pos_ratio_std_full 越高, 表示该银行该年不同媒体报道在正面用语浓度上越不一致, 可能对应事件密集期的多元叙事或不同来源立场分化; 越低则对应口径统一。该维度与水平均值正交: 均值给出中心趋势, 本列给出围绕中心的散布, 二者共同刻画正面框定的分布形状。方法学上口径与家族一致, pos_ratio 已按轨内总词数归一, 故本列反映密度的篇际标准差而非绝对词数波动, 不受报道条数或长度机械驱动。

## VAR: avg_pos_ratio_std_ss

【变体差分】
本列是家族离散读数在 ss 轨上的实例: 对每个 bank-year 单元, 取该单元内各篇报道 pos_ratio_ss 的样本标准差, 度量在银行与金科同句共现窗口切片上, 同一银行同一年不同报道之间正面词密度的分散程度。ss 轨文本最严格聚焦共现语境, 故本列刻画的是共现语境内篇际正面用语强度的一致性。ss 轨回退语义镜像 ctx: 无同句共现时 content_ss 回退全文正文并置 ss_is_fallback 标记、共享 n_articles 分母, 属优雅降级不丢行。数值无量纲非负, 单篇单元标准差不可定义而产出 NaN; 在共现稀疏的小 T 开发样本上本列易退化为零方差或 NaN, 属预期, 生产 T=19 语料恢复正常。差分维度相较 full、ctx 的 std 列只在文本轨: ss 轨在同句共现窗口上计数。三轨 std 列互为稳健性、不分主次、各自 just-identified 并排, 铁律禁止混进同一 over-identified Hansen J; 本列与同轨水平列 avg_pos_ratio_ss 配对, 水平与离散正交不可互代。构念上本列刻画的是共现语境内不同报道对该银行金科议题正面框定强度的分歧程度: 高值表示媒体对同一议题的正面用语浓度不一致, 低值表示口径趋同。因 ss 轨判定最严格且回退机制可能把整篇正文引入个别观测, 本列的离散读数对 ss_is_fallback 占比尤为敏感, 解读时须一并披露回退比例, 以免把回退带来的口径混合误读为真实的媒体分歧。方法学口径与家族一致: 固定 6 词典 union 词表逐篇计数、pos_ratio 已按轨内总词数归一, 故本列度量密度的篇际标准差而非绝对词数波动, 不受报道条数或长度机械放大。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics and Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
<!-- rendered-citations:end -->
