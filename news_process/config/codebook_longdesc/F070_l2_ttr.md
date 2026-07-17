---
family_id: F070
columns:
- avg_ttr_ctx
- avg_ttr_full
- avg_ttr_ss
unit: 无量纲比率 (词型数/词例数, 取值区间 (0,1])
formula: "type_token_ratio = |set(real_tokens)| / |real_tokens| (jieba 分词剔标点后逐篇算, 四位小数); avg_ttr{track} = bank-year mean(type_token_ratio{track}), track ∈ {full, ctx, ss}"
producer: news_process/pipeline/sentiment/tone_words.py (逐篇 type_token_ratio) + news_process/pipeline/panel/encode.py (bank-year 均值聚合 avg_ttr{track})
upstream:
- 22_tone_words.parquet (type_token_ratio{full,ctx,ss})
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1016/j.rmal.2024.100168
  type: journal
  authors: Bestgen, Y.
  year: 2025
  title: "Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons"
  venue: Research Methods in Applied Linguistics
  vol: 4
  issue: 1
  pages_or_artno: 100168
- doi: 10.1111/jofi.12162
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2014
  title: "Measuring readability in financial disclosures"
  venue: Journal of Finance
  vol: 69
  issue: 4
  pages_or_artno: 1643-1671
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: Bonsall, S. B., Leone, A. J., Miller, B. P., & Rennekamp, K.
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: 63
  issue: 2-3
  pages_or_artno: 329-357
- doi: 10.1080/09296171003643098
  type: journal
  authors: Covington, M. A., & McFall, J. D.
  year: 2010
  title: "Cutting the Gordian knot: The moving-average type-token ratio (MATTR)"
  venue: Journal of Quantitative Linguistics
  vol: 17
  issue: 2
  pages_or_artno: 94-100
- doi: "10.1080/09296174.2025.2483080"
  type: "journal"
  authors: "Fang, Y., Wang, F., & Dai, Z."
  year: 2025
  title: "A Zipfian Approach to Exploring Lexical Complexity Changes in Mandarin Chinese: A Corpus-Based Analysis of Word N-Grams"
  venue: "Journal of Quantitative Linguistics"
  vol: "32"
  issue: "3"
  pages_or_artno: "251-278"
- doi: "10.1080/23311983.2025.2584418"
  type: "journal"
  authors: "Zheng, W."
  year: 2025
  title: "Text length requirements for stable and genre-sensitive lexical diversity measurement"
  venue: "Cogent Arts & Humanities"
  vol: "12"
  issue: "1"
  pages_or_artno: "2584418"
- doi: "10.1515/csh-2024-0026"
  type: "journal"
  authors: "Wang, Z., Xu, H., & Liu, K."
  year: 2024
  title: "Lexical Complexity in Corporate Communication: A Corpus-Based Study of Translated and Non-Translated Chairman’s Statements"
  venue: "Corpus-based Studies across Humanities"
  vol: "2"
  issue: "2"
  pages_or_artno: "265-284"
new_dois:
- 10.1111/jofi.12162
- 10.1016/j.jacceco.2017.03.002
---

## CORE

【构念与来源】
本家族三列 avg_ttr_full / avg_ttr_ctx / avg_ttr_ss 度量的是银行-年层面新闻文本的词汇丰富度 (lexical diversity), 底层构念是语言学里的词型-词例比 (Type-Token Ratio, TTR), 即一篇文本里不重复的词 (词型, type) 数量除以全部实词出现次数 (词例, token) 的比值。TTR 越高, 说明文本用词越多样、越少重复, 通常对应更专业、更信息密集、可读性更低的表述; TTR 越低, 说明遣词造句高度重复, 常见于套话密集、模板化的报道。它与家族外的平均句长 (avg_sent_len) 与平均词长 (char_per_word, avg_cpw) 并列, 共同构成新闻文本的可读性与文本复杂度控制变量组, 目的不是作为主处理变量, 而是在情感与关注度回归里剥离"文本是否难读、是否啰嗦"这一混淆通道, 使金融科技语调的估计不被文本风格差异污染。构念来源直接锚定 Loughran 与 McDonald (2014) 关于财务披露可读性度量的开创性研究: 他们在金融文本语境下系统论证了传统可读性公式 (如 Fog Index) 在专业披露上的失效, 提倡以更贴合语料的代理指标刻画文本处理难度; 本项目在中文语料上无法直接套用英文句法型公式, 遂改用 TTR、平均句长、平均词长三个与语言无关的表层代理来近似这一维度。

【方法学与计算】
逐篇计算发生在情感词典阶段 (stage 22, pipeline/sentiment/tone_words.py): 对每篇报道先用 jieba (冻结锚点 0.42.1) 分词得到 token 序列, 随后用一个标点与空白集合 (含中英文标点、全角符号、换行制表符) 把纯标点、纯空白 token 彻底剔除, 得到"实词" real_tokens; TTR 定义为 len(set(real_tokens)) / max(len(real_tokens), 1), 结果四舍五入到四位小数落列 type_token_ratio。分母的 max(·, 1) 是空文本除零保护, 保证极端退化篇不产生 NaN 或异常。逐篇列命名带轨道后缀 type_token_ratio_full / _ctx / _ss。银行-年聚合发生在面板编码阶段 (pipeline/panel/encode.py): avg_ttr{track} = 该银行该年全部留篇的 type_token_ratio{track} 的算术平均 (pandas mean), 即把文章级词汇丰富度按简单均值折叠到 bank-year 面板格。取值区间为 (0,1]: 每个 token 至少贡献自身一个词型, 故 TTR 严格为正且不超过 1, 全篇无重复词时取 1。需要强调 TTR 的一个内生机械缺陷: 它对文本长度强负相关——文本越长, 常见词被重复使用的概率越高, 词型增速慢于词例增速, 于是长文的 TTR 被系统性压低。这一"长度依赖"是 TTR 族公认的构念污染, Covington 与 McFall (2010) 正是为解决此问题提出移动平均型 TTR (MATTR), 用固定窗口滑动平均消除长度敏感性; Bestgen (2025) 进一步对 MATTR 的估计性质做了正反两面评估, 指出其在中短文本上仍有窗宽选择的权衡。本项目的 avg_ttr 采用的是未做长度校正的原始 TTR, 因此在回归使用时应与文本长度控制 (如篇均字数、平均句长) 同置, 或将其定位为可读性代理的稳健性成员而非唯一测度; 更贴合的长度稳健替代方向 (MATTR 式窗口平均) 已在 stage 22 日志中作为已知局限锚定。与之相邻的 Bonsall 等 (2017) 提出的 Bog Index 从句法成分角度刻画"平白英语"可读性, 与 TTR 的词汇多样性视角互补而非替代, 二者度量的是文本难度的不同侧面。

【文献定位】
在金融文本分析谱系里, 可读性与文本复杂度作为控制变量的正当性由 Loughran 与 McDonald (2014, Journal of Finance) 奠定: 他们证明文本处理成本会独立于内容影响市场对披露的反应, 因此在以文本情感或关注度为解释变量的回归里, 若不控制文本本身的可读性, 估计会吸收"难读文本更少被消化"的混淆效应。本家族三列即为此而设, 与家族外的句长、词长测度共同承担这一控制职责。词汇多样性度量本身的方法学争议 (原始 TTR 的长度依赖) 由 Covington 与 McFall (2010) 与 Bestgen (2025) 在计量语言学侧界定, 本项目据此把 avg_ttr 明确定位为长度敏感的代理指标, 并在回归叙事里与长度控制协同、不单独承担识别。Bonsall 等 (2017, Journal of Accounting and Economics) 的 Bog Index 提供了句法侧的平白语言测度参照, 提示可读性是多维构念, TTR 仅覆盖其词汇多样性一维。三轨 (full/ctx/ss) 在此均为文本复杂度的规格稳健性成员: 各轨对应不同文本切片下的词汇多样性, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨列混进同一 over-identified 的 Hansen J 过度识别检验。 近年的定量语言学证据从三个方向补强并约束了本族定位。Fang、Wang 与 Dai (2025) 在《人民日报》1946–2020 新闻语料上以 Zipf 律指数刻画现代汉语词汇复杂度的历时变化, 并证明该指数与词汇多样性、词汇密度、词汇复杂度三大构念系统相关, 为"词汇多样性可用频次—类型统计量刻画"这一测度路线提供了当代依据, 且其语料同为新闻文体, 优于跨域外推; 惟其算子是 word n-gram 的 Zipf 参数, 与本族未作长度校正的原始 TTR 数学形式不同, 二者仅共享"频次—类型分布刻画复杂度"的方法论前提, 原文亦无 bank-year 面板层级。Zheng (2025) 用四类文体语料实证给出词汇多样性测量所需的最低文本长度门槛 (500 词以下高度不稳、1000–2000 词方趋稳定), 直接刻画了本族原始 TTR 对文本长度敏感这一测量学问题; 本项目引该文是为诚实披露 avg_ttr 口径的局限, 而非据其背书 TTR 的正确性——原文语料为日语且以词计长度, 未涉中文 jieba 分词与金融新闻, 其补救方案为设定最低文本长度门槛并改用长度校正型多样性指标 (如 Corrected/Root TTR、MTLD), 与本族实际使用的未校正 TTR 不同, 原文亦未主张把文本长度作为同期控制变量与多样性指标并列入回归; 该文因而只承接 Covington 与 McFall (2010) 已界定的长度依赖脉络, 强化 avg_ttr 仅作长度敏感代理、须与长度控制协同而不单独承担识别的定位。Wang、Xu 与 Liu (2024) 用语料库方法对比翻译与非翻译董事长致辞的词汇复杂度, 显式采用 TTR 及其 Corrected/Root/Bi-logarithmic 变体、NDW、词汇密度与动词复杂度等指标族, 本族仅据此锚定"把型例比类指标施加于企业沟通类金融文本"的方法先例存在性; 须更正的是其语料为英文董事长致辞 (中译英译文与美国、香港原生英文), 并非中文文本, 故不得据本文声称中文金融文本上的同语境先例, 且该文系描述性对比研究 (翻译对非翻译), 无因果计量与面板结构, 文本类型为公司自述致辞而非第三方新闻报道, 其复杂度算子亦未必与本族 TTR 完全同式。
## VAR: avg_ttr_full

【变体差分】
本列是家族在 full 轨上的词汇丰富度: 底层 type_token_ratio_full 计算所用文本 content_full = 标题 prepend 后拼接的全文正文 (stage 14 ctx_materializer 物化, 标题被前置到正文首句)。full 轨是最完整的文本切片, 覆盖整篇报道的全部实词, 因此其 TTR 最受"长度依赖"影响——全文越长, 常见词重复越多, avg_ttr_full 相对 ctx/ss 两轨通常偏低。它在留篇门控上与 full-only 口径 (2026-06-29) 一致: 一篇报道是否被判为"一篇银行金科报道"只看 llm_verified_full, 银行-年行宇宙由 full 留篇集定义; ctx/ss 两轨是 conditional-on-full 的子集测度。full 轨对应可读性控制里最标准、覆盖面最广的文本视角, 是三轨中天然的参照轨, 但并非"主"轨——三轨为规格稳健性并列关系, 不分主次。avg_ttr_full 与 avg_ttr_ctx、avg_ttr_ss 各自 just-identified 并排、互为稳健性, 严禁三者同时进入同一 over-identified 的 Hansen J。聚合口径为该银行该年全部 full 留篇的 type_token_ratio_full 简单算术平均, 取值区间 (0,1], 长度越长者拉低本列水平。回归使用时应与全文长度控制协同, 以剥离 TTR 的机械长度成分。需要提醒的是, full 轨文本因含标题前置与完整正文, 其分母 (实词总数) 在三轨中最大, 故本列对个别超长报道的稀释最敏感; 当某银行某年报道普遍偏长时, avg_ttr_full 会被系统性压低, 这属于 Covington 与 McFall (2010) 所刻画的原始 TTR 长度依赖, 而非该行报道信息真的更贫乏, 解读须与篇均长度联读。作为家族最完整覆盖轨, 本列是可读性控制里的默认参照成员, 但其"参照"地位仅指文本切片最全, 不含任何主次优先级——三轨严格并列。

## VAR: avg_ttr_ctx

【变体差分】
本列是家族在 ctx 轨上的词汇丰富度: 底层 type_token_ratio_ctx 所用文本 content_ctx = 标题 prepend 后拼接的实体特异性上下文窗口 (proximity-based attribution, 只保留目标银行实体邻近的文本片段, 而非全文)。相比 full 轨, ctx 轨文本更短、密度更高: 剪掉了与银行无关的段落, 保留的是围绕实体的语义窗口, 因此其实词总数更少。由于 TTR 对长度强负相关, 更短的 ctx 文本通常产出比 full 更高的 avg_ttr_ctx 水平——这不是"信息更丰富", 而是短文本词型/词例比天然更高的机械效应, 解读时须与 full 轨对照而非直接比水平高低。ctx 轨在留篇口径上是 conditional-on-full 的稳健性/测度轨: 行宇宙仍是 full 留篇集的子集, 逐轨照算本列。作为文本复杂度控制的一个规格变体, avg_ttr_ctx 与 avg_ttr_full、avg_ttr_ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨列混入同一 over-identified 的 Hansen J。聚合口径为该银行该年全部 ctx 轨可用篇的 type_token_ratio_ctx 简单均值, 取值区间 (0,1]。当某篇无有效实体窗口 (ctx 缺列) 时该篇不进本轨分子, 不借 full 轨数据填充, 分子分母严格逐轨对齐以免跨轨污染。ctx 轨的价值在于它把词汇多样性的度量聚焦到与目标银行真正相关的语义邻域, 剔除了全文里与实体无关的背景段落, 因此当研究关心"围绕银行的那部分表述有多丰富"时, 本列比 full 轨更贴切; 但正因文本被裁短, 其 TTR 水平不可与 full 轨直接横比, 只能在各自轨内做截面或时序比较。本列与其余两轨互为稳健性, 用以检验可读性控制的结论不被文本切片选择所驱动。

## VAR: avg_ttr_ss

【变体差分】
本列是家族在 ss 轨上的词汇丰富度: 底层 type_token_ratio_ss 所用文本 content_ss = 标题 prepend 后拼接的"银行与金融科技词同句共现 ±N 窗"文本 (config filtering.yaml 的 ss_sentence_radius 默认 1, 即银行∧金科同句及其相邻窗口的句子)。ss 轨是三轨中最窄的文本切片, 只保留银行与金科主题同句邻近的句群, 因此实词数最少、TTR 的短文本抬升效应最强, avg_ttr_ss 水平通常在三轨中最高。关键的回退语义与 CLAUDE.md 铁律一致: ss 轨镜像 ctx 轨——当某篇无银行∧金科同句共现时, content_ss 退化为全文 body (与 full 轨文本相同)、ss_is_fallback 置 True, 并共享 n_articles 分母; 当 FINTECH_AC=None 时该篇 is_fallback 全 True 优雅降级。因此 avg_ttr_ss 在共现稀疏的银行-年上会因大量回退篇而向 full 轨水平靠拢, 解读须结合回退占比。ss 轨在留篇上同为 conditional-on-full 子集测度。作为文本复杂度控制的规格变体, avg_ttr_ss 与 avg_ttr_full、avg_ttr_ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨列混进同一 over-identified 的 Hansen J。聚合口径为该银行该年全部 ss 轨篇 (含回退篇) 的 type_token_ratio_ss 简单均值, 取值区间 (0,1]。由于同句共现窗口是三轨中最激进的裁剪, 非回退篇的 ss 文本往往只有寥寥数句, 实词总数极小, 此时 TTR 因短文本效应可逼近 1, 方差也更大; 而回退篇又与 full 文本等长, 于是同一银行-年内 ss 轨可能混合"极短高 TTR"与"全文低 TTR"两类篇, 均值的可解释性高度依赖回退占比, 使用时建议同时观察 ss_is_fallback 的年度比例。本列刻画的是银行与金融科技主题真正同句讨论时那部分文本的用词多样性, 是三轨里语义最聚焦、也最需谨慎解读的稳健性成员, 与 full/ctx 两轨严格并列、不分主次。

<!-- rendered-citations:begin -->
Bestgen, Y. (2025). Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons. Research Methods in Applied Linguistics, 4(1), 100168. https://doi.org/10.1016/j.rmal.2024.100168
Loughran, T., & McDonald, B. (2014). Measuring readability in financial disclosures. Journal of Finance, 69(4), 1643-1671. https://doi.org/10.1111/jofi.12162
Bonsall, S. B., Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. Journal of Accounting and Economics, 63(2-3), 329-357. https://doi.org/10.1016/j.jacceco.2017.03.002
Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type-token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94-100. https://doi.org/10.1080/09296171003643098
Fang, Y., Wang, F., & Dai, Z. (2025). A Zipfian Approach to Exploring Lexical Complexity Changes in Mandarin Chinese: A Corpus-Based Analysis of Word N-Grams. Journal of Quantitative Linguistics, 32(3), 251-278. https://doi.org/10.1080/09296174.2025.2483080
Zheng, W. (2025). Text length requirements for stable and genre-sensitive lexical diversity measurement. Cogent Arts & Humanities, 12(1), 2584418. https://doi.org/10.1080/23311983.2025.2584418
Wang, Z., Xu, H., & Liu, K. (2024). Lexical Complexity in Corporate Communication: A Corpus-Based Study of Translated and Non-Translated Chairman’s Statements. Corpus-based Studies across Humanities, 2(2), 265-284. https://doi.org/10.1515/csh-2024-0026
<!-- rendered-citations:end -->
