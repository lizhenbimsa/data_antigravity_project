---
family_id: F061
columns:
- avg_nominalization_ctx
- avg_nominalization_full
- avg_nominalization_ss
unit: 无量纲比率 (银行-年名词化率均值, 取值区间 [0,1])
formula: "文章级 nominalization_ratio = n_nominal / n_real; n_nominal = 计数(词性 ∈ {vn, an}) + 计数(名词且末字 ∈ {性,化,度,型,制}); n_real = 实词总数。银行-年聚合 avg_nominalization{track} = mean_over_articles(nominalization_ratio{track}), 'mean' 自动跳过 NaN。track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/sentiment/lexical_complexity.py::compute_lexical_complexity ; news_process/pipeline/panel/encode.py (bank-year 'mean' 聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (文章级 nominalization_ratio{track})
citations:
- doi: 10.1057/s41599-025-06094-y
  type: journal
  authors: Lesmy, D., Muchnik, L., & Mugerman, Y.
  year: 2025
  title: "Lost in the fog: Growing complexity in financial reporting — A comparative study"
  venue: Humanities and Social Sciences Communications
  vol: 12
  pages_or_artno: 850
- doi: 10.1016/j.pacfin.2023.102074
  type: journal
  authors: Li, F., Yang, M., & Zhang, T.
  year: 2023
  title: "Does prospectus readability matter for bond issuance pricing? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 80
  pages_or_artno: 102074
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1111/1475-679X.12179
  type: journal
  authors: Bushee, B. J., Gow, I. D., & Taylor, D. J.
  year: 2018
  title: "Linguistic complexity in firm disclosures: Obfuscation or information?"
  venue: Journal of Accounting Research
  vol: 56
  issue: 1
  pages_or_artno: 85-121
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K.
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: 63
  issue: 2-3
  pages_or_artno: 329-357
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/jofi.12162
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2014
  title: "Measuring readability in financial disclosures"
  venue: Journal of Finance
  vol: 69
  issue: 4
  pages_or_artno: 1643-1671
- doi: "10.1108/arj-03-2023-0094"
  title: "Fighting through the Flesch and Fog: the readability of risk disclosures"
  authors: "Toerien, F. E., & du Toit, E."
  year: 2024
  venue: "Accounting Research Journal"
  type: "journal"
  one_sentence_zh: "该文在南非上市公司风险披露语境下实证发现文本可读性随会计准则修订而持续恶化, 为本家族以词性驱动的名词化率刻画披露语言复杂度提供了2023-2026年最新的外部效度佐证。"
new_dois:
  - "10.1108/arj-03-2023-0094"
---

## CORE

【构念与来源】
本家族刻画中文银行新闻报道的名词化程度 (nominalization), 即行文把本可用动词、形容词直陈的动作与性状"憋"成抽象名词来表述的倾向。名词化是语域分析与披露可读性文献公认的"官腔/晦涩"句法信号: 当作者反复用抽象名词短语代替具体的施动句式, 文本在字面信息量不增的情况下抬高了句法加工成本, 读者需要更多认知资源才能还原事件的主体、动作与对象。会计与金融的披露文献把这一维度纳入综合可读性刻度: Bonsall, Leone, Miller 与 Rennekamp (2017) 提出的 Bog Index 明确把名词化列为其惩罚性句法成分之一, 认为动词被压成抽象名词是"晦涩化" (obfuscation) 的典型表面特征; Loughran 与 McDonald (2014) 则系统论证金融披露里的"可读性"应以词汇与句法的机械可复现代理来测量, 而非直接套用英文音节口径的 Fog 指数。本家族即是把这一构念落到中文新闻语料的一次 $0 成本操作化: 一篇报道名词化率越高, 其行文越接近抽象、程式化的官样表述, 越偏离具体、可核验的事件叙述。之所以对"银行×金融科技"新闻测量该维度, 是因为新闻文本的句法风格本身即是一个可能与银行属性、报道质量相关的混淆变量与自变量候选: 高名词化的报道可能反映来源方 (银行公关稿、监管转述) 的程式化语言, 也可能稀释报道的硬信息含量, 因而在情感与关注度分析中需要作为文本风格控制变量进入回归。

【方法学与计算】
文章级测度由 lexical_complexity 模块的 compute_lexical_complexity 完成: 对一篇报道做单次 jieba.posseg (0.42.1 冻结版) 词性标注 pass, 遍历标注结果, 分子 n_nominal 计入两类词——其一是词性标签直接为 vn (动名词) 或 an (形名词) 的词, 其二是名词性词 (词性首字母为 n) 且词末字落在名词化后缀集合 {性, 化, 度, 型, 制} 内 (例如"安全性""数字化""集中度""平台型""监管制"这类由动词/形容词派生的抽象名词); 分母 n_real 为该篇的实词总数。二者相除得到取值于 [0,1] 的名词化率, 短文本或空文本在实词数为零时返回 NaN。此测度全程 $0: 不调付费 LLM、不新增 PyPI 依赖、不触 M0 审批门、不动 Prompt v8 冻结锚, 分词与词性一律走独立未注入的 pristine jieba Tokenizer 实例, 因而任何其它模块对全局分词器的领域词注入都不改变本测度取值, 保证跨运行确定性。银行-年面板列由 encode 层对文章级 nominalization_ratio{track} 做 'mean' 聚合得到, 'mean' 天然跳过 NaN, 故短文本或缺轨文本不污染分母。诚实限定须随论文如实披露: jieba.posseg 走词典加 HMM, vn/an 与专名词性 (nr/ns/nt/nz) 的边界与歧义精度低于专用 NER, 名词化判据中"名词首字母 n 且后缀命中"的规则会把被 jieba 误标为专名的少量人名 (如把"赵性"误判 nr) 计入分子, 造成小幅高估, 属上界噪声估计; 措辞应为"以 jieba 词性近似名词化类别", 不得声称等同金融文本的规范句法解析。名词化后缀集合亦是可复现的中文近似, 而非穷尽的形态学清单, 未来可用更完整的派生后缀表做 drop-in 替换。

【文献定位】
本家族的直接构念锚是 Bonsall 等 (2017) 的 Bog Index 及其对名词化作为晦涩化句法成分的操作化, 顶刊定位则由 Loughran 与 McDonald (2014, 发表于 Journal of Finance) 奠定——该文确立了"金融披露可读性应以机械、可复现的词汇/句法代理测量"的方法论底线, 是本家族把英文可读性研究范式迁移到中文新闻语料时最核心的合法性来源。Bushee, Gow 与 Taylor (2018) 进一步区分了语言复杂度的"晦涩"与"信息"两种成因, 提醒名词化等表面特征既可能是刻意模糊, 也可能是内容本身专业性的自然结果, 故本测度在回归中定位为文本风格控制变量而非因果处理变量。Loughran 与 McDonald (2016) 的综述、Gentzkow, Kelly 与 Taddy (2019) 关于"文本即数据"的方法学纲领, 共同支撑本项目以词典/词性驱动的低成本文本测度族来刻画报道语言风格。近期证据方面, Li, Yang 与 Zhang (2023) 在中国债券招募说明书语境下发现文本可读性影响发行定价, Lesmy, Muchnik 与 Mugerman (2025) 则跨市场记录了财务报告复杂度的持续上升, 二者印证了披露文本语言复杂度维度在中国与跨国场景下的持续经济相关性, 从而为在中文银行新闻中测量名词化率提供了外部效度旁证。Toerien 与 du Toit (2024, Accounting Research Journal) 在南非上市公司风险披露语境下实证发现文本可读性随会计准则修订而持续恶化, 为本家族以词性驱动的名词化率刻画披露语言复杂度提供了2023-2026年最新的外部效度佐证。

## VAR: avg_nominalization_full

【变体差分】
本列是名词化率家族的 full 轨, 也是本家族的 canonical 主轨。其文章级输入文本为 content_full——标题 prepend 后拼接全文正文的完整报道全文, 因而在三轨中承载最完整的句法信息, 名词化率的估计方差最小、口径最贴近"整篇报道的行文风格"。full 轨与留篇门控口径严格对齐 (2026-06-29 full-only 铁律): 一篇报道是否被判为"一篇银行×金融科技报道"仅由 llm_verified_full 决定, 故本列的银行-年行宇宙即 full 留篇集本身, 分母为该银行该年通过 full-only 门控的报道数经 'mean' 聚合 (跳过实词数为零而返回 NaN 的短文本)。相对于同家族的 _ctx 与 _ss 变体, full 轨的差分语义在于文本窗口最宽: 它不做实体窗口截断、也不做银行与金融科技同句共现约束, 因而既捕捉报道主体叙事、也纳入背景与铺陈段落的名词化倾向。作为 canonical 主轨, full 是回归中优先进入的文本风格控制变量刻度; 三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨的名词化率混入同一 over-identified 的 Hansen J 过度识别检验。当需要区分"整篇风格"与"银行语境局部风格"时, 应以本列与 _ctx/_ss 并列报告而非合并。作为家族无后缀历史命名产物的落地形式, full 轨在实务中承担基准角色: 描述性统计、图表主刻度、以及作为文本风格控制变量进入情感与关注度回归时, 默认取本列; _ctx 与 _ss 则以稳健性列并排验证主结论不被文本窗口的选择所驱动。开发期 T=2 短面板下本列因文本最完整而 NaN 最少、估计最稳, 是三轨中最先可用的刻度。

## VAR: avg_nominalization_ctx

【变体差分】
本列是名词化率家族的 ctx 轨。其文章级输入文本为 content_ctx——标题 prepend 后, 仅保留实体上下文窗口内的文本 (银行实体命中位置周围的句子窗口), 因而相对 full 轨聚焦于报道中真正谈及目标银行的局部段落, 剔除了与该银行无关的背景铺陈。这一窗口截断使 ctx 轨的名词化率刻画"围绕银行的那部分行文有多程式化", 语义上比 full 轨更贴近报道对具体银行的直接表述风格, 但代价是可用文本变短、估计方差上升。口径上, ctx 轨是 conditional-on-full 的测度/稳健性轨: 其银行-年行宇宙是 full 留篇集的子集, 留篇判定仍由 full-only 门控 (llm_verified_full) 决定, ctx 轨自身不另设留篇门, 只在留篇集内按 content_ctx 逐篇计算并 'mean' 聚合 (缺轨或空文本篇返回 NaN 由 'mean' 跳过, 不借 full 分母)。相对 canonical 的 full 主轨, 本列的差分维度是文本窗口——由全文收窄为实体上下文窗口, 而非改动名词化判据、后缀集合或聚合方式。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ctx 与 full/ss 的名词化率混入同一 over-identified 的 Hansen J。开发期 T=2 短面板上, ctx 轨因文本更短可能出现更多 NaN 与更高方差, 属预期退化, 生产期 T=18 全量语料下方能体现其作为局部风格稳健性轨的价值。

## VAR: avg_nominalization_ss

【变体差分】
本列是名词化率家族的 ss 轨 (same-sentence, 银行∧金融科技同句共现轨)。其文章级输入文本为 content_ss——标题 prepend 后, 仅保留银行实体与金融科技词在同一句 (±N 句窗, 由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 内共现的最窄语境文本, 因而在三轨中语境最紧、最聚焦于"银行谈金融科技"这一核心命题句的行文风格。ss 轨采用镜像 ctx 的优雅回退语义: 当一篇报道没有银行与金融科技的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 若上游金融科技词表 FINTECH_AC 为 None 则整轨回退标记全 True 优雅降级——因此本列的取值在同句共现存在时刻画最窄语境的名词化倾向, 在回退时退化为与全文口径接近的估计, 论文报告须结合 fallback 占比解读。口径上, ss 轨同为 conditional-on-full 的稳健性轨: 行宇宙是 full 留篇集子集, 留篇判定仍由 full-only 门控决定, ss 自身不另设门, 逐篇按 content_ss 计名词化率再 'mean' 聚合 (NaN 自动跳过)。相对 canonical 的 full 主轨, 本列差分维度是语境判据——由全文收窄为银行∧金融科技严格同句共现窗口, 判据原语与 stage 13 共现硬过滤不同口径不可互相复用。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把 ss 与 full/ctx 的名词化率混入同一 over-identified 的 Hansen J。开发期 T=2 上 ss 轨因语境最窄、回退频繁而方差与退化最显著, 属预期现象。

<!-- rendered-citations:begin -->
Lesmy, D., Muchnik, L., & Mugerman, Y. (2025). Lost in the fog: Growing complexity in financial reporting — A comparative study. Humanities and Social Sciences Communications, 12, 850. https://doi.org/10.1057/s41599-025-06094-y
Li, F., Yang, M., & Zhang, T. (2023). Does prospectus readability matter for bond issuance pricing? Evidence from China. Pacific-Basin Finance Journal, 80, 102074. https://doi.org/10.1016/j.pacfin.2023.102074
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Bushee, B. J., Gow, I. D., & Taylor, D. J. (2018). Linguistic complexity in firm disclosures: Obfuscation or information?. Journal of Accounting Research, 56(1), 85-121. https://doi.org/10.1111/1475-679X.12179
Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. Journal of Accounting and Economics, 63(2-3), 329-357. https://doi.org/10.1016/j.jacceco.2017.03.002
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2014). Measuring readability in financial disclosures. Journal of Finance, 69(4), 1643-1671. https://doi.org/10.1111/jofi.12162
Toerien, F. E., & du Toit, E. (2024). Fighting through the Flesch and Fog: the readability of risk disclosures. Accounting Research Journal. https://doi.org/10.1108/arj-03-2023-0094
<!-- rendered-citations:end -->
