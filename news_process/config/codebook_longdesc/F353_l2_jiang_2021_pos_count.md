---
family_id: F353
columns:
- jiang_2021_pos_count_ctx
- jiang_2021_pos_count_full
- jiang_2021_pos_count_ss
unit: 篇数加权词次 (count, 每篇正面命中词次原始计数, 未做长度归一)
formula: 'pos_count_{trk} = 对 content_{trk} 分词后, 命中姜富伟等(2021)金融情感词典正面词表(且未被否定规则翻转)的词次求和; 面板列为该口径下 bank-year 内文章级计数的汇总统计(如 sum/mean, 具体聚合子式见 stata_export.py 标签映射与 encode.py 聚合层)'
producer: pipeline\sentiment\tone_words.py (词典打分原语与否定/程度规则) ; pipeline\panel\encode.py (文章级→面板聚合) ; pipeline\panel\stata_export.py (标签映射)
upstream:
- 14_materialize_ctx (content_full/content_ctx/content_ss 三轨文本物化)
- 21_tone_words (词典打分产出 jiang_2021_score_* 系列文章级列)
citations:
- doi: 10.1016/j.jfineco.2024.103899
  type: journal
  authors: Jiang, E. X., Matvos, G., Piskorski, T., & Seru, A.
  year: 2024
  title: 'Monetary tightening and U.S. bank fragility in 2023: Mark-to-market losses and uninsured depositor runs?'
  venue: Journal of Financial Economics
  vol: '159'
  pages_or_artno: '103899'
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: 媒体文本情绪与股票回报预测
  venue: 经济学(季刊)
  vol: '21'
  issue: '4'
  pages_or_artno: 1323-1344
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: A new Chinese financial sentiment dictionary for textual analysis in accounting and finance
  venue: SSRN Working Paper
  pages_or_artno: '3446388'
- doi: "10.1016/j.cjar.2025.100406"
  type: "journal"
  authors: "Zhao, J., & Ren, M."
  year: 2025
  title: "Innovative or conservative? How clan culture shapes bank digital transformation in China"
  venue: "China Journal of Accounting Research"
  vol: "18"
  issue: "2"
  pages_or_artno: "100406"
new_dois: []
---

## CORE

【构念与来源】
本家族测度金融领域中文新闻报道中正面语调词的原始命中词次, 词典来源为姜富伟、孟令超、唐国豪(2021, 《经济学(季刊)》)基于中国金融市场语料构建的中文金融情感词典。该词典延续了 Loughran & McDonald (2011) 在美国 10-K 文本情感分析中开创的"领域专属词典优于通用情感词典"的方法论传统, 但并非通用情感词汇的机械翻译, 而是从中国财经媒体、公告与分析师报告语料中提炼出的正面/负面词表, 因而对"利好""增持""扭亏为盈"等中国金融新闻语境下的惯用褒义表达具有更高的覆盖率与更低的语义漂移。姜富伟等(2021)的原始研究证明该词典构造的媒体情绪指标对股票收益具有显著预测力, 是国内金融文本分析文献中较早、被后续研究反复引用与对照的中文金融专用情感词典之一, 与 Bian, Jia, Li & Yan (2021, SSRN) 提出的另一部中文金融情感词典构成互补/对照关系——本项目在词典消融梯度设计中已将 jiang_2021 与 bian_2021、yao_2021、du_2022、you_2018、loughran(中译版) 六部词典并列纳入, 各词典口径互不隶属、互为稳健性对照, 不设单一"标准"词典压倒其余五部。

`jiang_2021_pos_count` 是六部词典打分体系中口径最"原生态"的一支产出: 它不是情感极性 tone(即(正词-负词)/(正词+负词)式的标准化差分), 也不是情感得分(带程度副词/转折修饰的加权分), 而是词典打分流水线中最上游的正面词命中计数——统计每篇文章中被识别为姜富伟词典正面词、且未被否定规则(如"不"、"没有"等否定词紧邻翻转)剔除的词次总和。这一原始计数保留了文本长度信息(长文章倾向于命中更多正面词), 因而在稳健性设计上与经长度归一的 tone/score 变体形成天然对照: 研究者可用 pos_count 检验"结论是否被文章长度驱动"这一常见文本分析混淆因素, 也可将其作为分母(与 n_articles 或总词数联立)自行构造归一化指标。

【方法学与计算】
计算流程分两层。第一层是文章级词典打分(producer 主体在 `pipeline/text/tone_words.py`): 对每篇文章的 `content_{full,ctx,ss}` 文本(三轨文本均已在 stage 14 `materialize_ctx` 完成"标题前置(prepend_title)+ 实体窗口/同句窗口截取"的物化处理, 与原始"内容"列不同)先经 jieba(版本冻结 0.42.1, 保证跨次运行分词结果确定性)分词, 再逐词与姜富伟(2021)正面词表做字符串匹配; 命中词若其紧邻上下文触发否定翻转规则(三条语言学规则之一, 与程度副词、转折规则并列, 详见 `tone_words._RULE_ABLATION_VARIANTS` 消融口径), 则不计入本口径的正面命中(该词转而影响 tone 的符号, 但 pos_count 本身统计的是"未被规则剔除的原始正面词次", 与 tone 的加权计分路径分叉发生在打分函数内部, 打分函数同时产出 pos_count/neg_count/tone/score 等多个并行输出列, 而非串行推导关系——因此 pos_count 与 tone 并非简单的"分子/复合公式"关系, 而是共享底层分词与词典匹配结果的两个独立读出量)。第二层是文章级到银行-年面板级的聚合(`pipeline/panel/encode.py` 与其在 `pipeline/panel/stata_export.py` 中的标签映射), 将同一 bank-year 单元内全部合格文章(受 stage 21 留篇门控约束, 详见下节)的 pos_count 汇总为面板统计量。

需要特别澄清计数与"篇数"的关系: 单位标注"篇数/计数"意指该列的量纲是"词次的加和计数"而非"命中篇数的计数"——即便某篇文章命中 5 个正面词, 计入该篇对面板汇总量的贡献是 5 而非 1。这一点是本家族测度与 `n_articles`/`pos_frac`(命中正面词的篇数占比)等篇数口径测度的关键构念区分, 使用时不应混用两类量纲做除法或差分而不做说明。

【文献定位】
本家族方法论直接继承文本-based 情感测度的两条脉络: 一是词典法情感分析在会计与金融文本分析中的奠基传统, 二是中国金融市场语境下的中文词典本地化改造。姜富伟、孟令超、唐国豪(2021)的原始工作以媒体文本情绪预测股票回报为核心贡献, 其词典构造流程与结果验证发表于《经济学(季刊)》, 是本项目采纳该词典作为六部并列词典之一的直接依据。与之互为参照的 Bian, Jia, Li & Yan (2021, SSRN 工作论文)从会计与金融文本分析角度独立构造了另一部中文金融情感词典, 两部词典在构造语料、词表规模与覆盖领域上存在差异, 本项目并未预设二者孰优, 而是将其与另外四部词典(yao_2021、du_2022、you_2018、loughran 中译版)一并纳入词典消融梯度, 作为互为稳健性、不分主次的并排测度。银行-媒体情感测度与银行系统性风险/脆弱性关联的最新实证证据可参见 Jiang, Matvos, Piskorski & Seru (2024, *Journal of Financial Economics*) 对 2023 年美国银行体系紧缩期挤兑与浮亏风险的研究, 该文虽非中文语境, 但为"媒体/市场文本信号如何传导至银行层面风险结果"这一构念族提供了顶刊层级的理论与实证背书, 支撑本项目将银行相关新闻文本情感测度(包括 jiang_2021 系列)作为解释银行经营结果的关键自变量这一识别路径的合理性。

三轨(full/ctx/ss)、否定/程度/转折规则消融梯度、以及六部词典并列均遵循本项目一以贯之的"各自 just-identified 并排、互为稳健性不分主次"设计铁律: 三条文本轨道(full=标题+全文, ctx=标题+实体窗口, ss=标题+银行∧金科同句窗口)对应同一构念在不同文本范围下的读出, 不应混入同一 over-identified 的 Hansen J 检验框架联合估计; ss 轨在无银行∧金科同句共现时镜像 ctx 的回退语义, 退化为全文 body 并置位 `ss_is_fallback=True`, 与 `n_articles` 共享同一分母口径。留篇门控口径自 2026-06-29 起统一为 full-only: 一篇文章是否计入"银行金科相关报道"的样本宇宙, 仅由 `llm_verified_full == True` 判定; ctx/ss 两轨的行宇宙是该 full 留篇集合的子集, 在此子集内各轨道独立按各自文本重新分词打分, 而非借用 full 轨的计数结果。 同域参照方面, Zhao 与 Ren (2025) 研究中国非正式制度对银行数字化转型的影响, 发现宗族文化经「短半径信任推高物理网点与人员依赖」与「风险规避降低风险承担意愿」两条供给侧机制, 以及「宗族内资源共济削弱信贷需求」的需求侧机制, 共同抑制银行数字化转型; 该文与本项目同国别、同行业(中国商业银行)、同为银行-年层的文本型变量, 因而可作为「在中国银行业以文本型变量构造银行-年测度」这一研究形态的同域存在性参照。援引须诚实标明举证边界: 该文数字化转型测度是否为分词后固定词表逐词命中计数, 在可得材料中未见披露、亦未经本项目核实, 故不可据此宣称本家族「词表命中词次」的技术路线获得背书; 且原文词表(若有)指向数字化/科技关键词而非情感词表, 全文不涉情感极性与正负面判定, 因此它不锚定本列的正面极性方向。其余迁移边界为: 原文文本源为银行年报(每银行-年单文档), 本项目为第三方新闻报道逐篇打分后聚合; 原文亦无否定翻转、程度副词、转折三条语言学规则层, 更无 full/ctx/ss 三轨并排。
## VAR: jiang_2021_pos_count_ctx

【变体差分】
本列是 jiang_2021 词典正面词命中计数在 ctx(实体窗口)轨道上的读出。ctx 轨文本 `content_ctx` 由 stage 14 `materialize_ctx` 从原始"内容"列中截取目标银行实体周边窗口拼接标题(prepend_title)物化而成, 与 full 轨(标题+全文)相比文本范围更窄, 因而在同一篇文章上 ctx 轨的正面词命中数在多数情形下不会大于 full 轨的对应计数(除非 ctx 窗口恰好落在正面词密集出现的银行相关语句附近而全文的其余部分词密度更稀), 这是理解本列与 `_full` 列相对大小关系的基本直觉, 但不构成严格的数学不等式约束(因二者分词与匹配是各自独立的文本重新处理, 非窗口截取自 full 轨已计算好的词序列)。

ctx 轨的构念定位是"聚焦目标银行相关语境的情感信号", 相较 full 轨排除了文章中与目标银行无关段落(如同篇报道其他银行、宏观政策背景等)可能引入的情感噪声, 因而在识别"该银行本身受到怎样的媒体正面评价"这一构念时理论上信噪比更高; 但代价是窗口截取本身依赖实体识别与窗口半径参数的准确性, 窗口边界误差可能截断本应计入的正面表述。ctx 轨与 full 轨、ss 轨三者严格并排, 是互为稳健性检验、不分主次的三个独立测度, 不应将三者混合进同一过度识别(over-identified)的联合估计框架, 也不应把 ctx 与 full 的差值本身当作一个新的构念解释变量使用(除非有独立的理论动机并明确披露)。

受 full-only 留篇门控约束, ctx 轨纳入统计的文章行宇宙与 full 轨相同(均以 `llm_verified_full == True` 为准), 但每篇文章在 ctx 轨下的分词与词典匹配基于 `content_ctx` 独立重算, 并非从 full 轨计数中按窗口比例折算得出。若某篇文章缺乏可识别的银行实体窗口(即窗口截取失败), `content_ctx` 会回退为该篇的 `content_full`(或等价的全文兜底), 相应地该篇在 ctx 轨的 pos_count 读数会趋同于 full 轨读数, 这属于设计内的优雅降级而非数据缺陷。

## VAR: jiang_2021_pos_count_full

【变体差分】
本列是家族的全文轨(full track)版本, 也是本项目在 P1 情感相关处理变量设计中确立的 full-only 主口径下的默认基线读出——即 stage 21 留篇门控本身即以 full 轨的 LLM 验证结果(`llm_verified_full`)为唯一判据, ctx 与 ss 两轨在此意义上是"以 full 轨行宇宙为条件"的稳健性/补充测度轨道(conditional-on-full), 而非与 full 轨完全对等、各自独立生成行宇宙的三分天下关系。

full 轨文本 `content_full` = 标题(prepend_title)+ 全文正文, 是 stage 14 物化的三轨文本中范围最宽的一支, 对应文章可能包含的全部姜富伟词典正面词命中(不限于银行实体附近或银行-金科同句范围)。因此 `jiang_2021_pos_count_full` 在同一样本内往往是三轨中数值上界最高的一支(文本范围更广, 词次基数更大), 但这并不意味着 full 轨在构念效度上优于 ctx/ss 两轨——三轨各自对应不同的理论问句(全篇整体语调 vs. 聚焦银行的语调 vs. 严格同句共现处的语调), 铁律要求三者并排使用、互为稳健性, 不设主次。

在词典消融维度上, full 轨的 pos_count 与同轨的 tone/score/negonly 等变体共享同一底层分词与词表匹配过程, 仅在"是否应用否定/程度/转折规则"及"是否做长度归一"上存在下游读出差异; pos_count 本身不施加否定翻转以外的任何规则修饰(不做程度副词加权、不做转折权重调整), 是这一系列变体中最贴近"原始词表命中"构念的一支, 常被用作检验 tone/score 等经规则修饰的复合指标是否与原始词次计数保持定性一致的对照基线。

## VAR: jiang_2021_pos_count_ss

【变体差分】
本列是家族在 ss(同句, sentence-level)轨道上的读出。ss 轨文本 `content_ss` 由 stage 14 物化, 判据为"目标银行实体与金科(金融科技)相关词在同一句子内共现"(句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认取值为 1, 与 stage 13 共现硬过滤所用的 `cooccurrence_filter.sentence_radius` 是两个不同配置键, 不可混用), 是三轨中文本范围最窄、判定条件最严格的一支, 拼接标题(prepend_title)后形成最终打分文本。

ss 轨的回退语义严格镜像 ctx 轨: 当某篇文章不存在满足银行∧金科同句共现条件的句子时, `content_ss` 回退为该篇全文 body(即退化为近似 full 轨的文本), 并置位 `ss_is_fallback=True`, 该标记列与 `n_articles` 共享同一分母口径, 供下游做"仅取真实同句命中样本"与"含回退样本"两种口径的稳健性对照。当上游 `FINTECH_AC`(金科词自动机)为 None 时(如金科词典未加载), `*_is_fallback` 全体置 True, 即全部退化为优雅降级路径, 而非静默产出空值或报错中断。

`jiang_2021_pos_count_ss` 在构念上度量的是"银行与金融科技同句提及处的正面语调密度", 相较 ctx 轨(仅要求银行实体窗口)进一步收窄到"银行-金科强相关语句"这一更精确但样本量更小的子集, 尤其适合用于检验研究结论是否被"泛泛提及银行"的噪声段落而非"银行金科业务本身"的报道段落所驱动。由于窗口/句子截取更严格, 该列在回退发生率较高的样本(如金科相关报道占比低的银行-年单元)中会有相当比例的观测退化为等价 full 轨读数, 分析时应结合 `ss_is_fallback` 标记做敏感性说明, 并遵循三轨并排、禁止混入同一 Hansen J 联合估计的项目铁律, 不与 ctx/full 两轨直接合并回归。

<!-- rendered-citations:begin -->
Jiang, E. X., Matvos, G., Piskorski, T., & Seru, A. (2024). Monetary tightening and U.S. bank fragility in 2023: Mark-to-market losses and uninsured depositor runs?. Journal of Financial Economics, 159, 103899. https://doi.org/10.1016/j.jfineco.2024.103899
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Zhao, J., & Ren, M. (2025). Innovative or conservative? How clan culture shapes bank digital transformation in China. China Journal of Accounting Research, 18(2), 100406. https://doi.org/10.1016/j.cjar.2025.100406
<!-- rendered-citations:end -->
