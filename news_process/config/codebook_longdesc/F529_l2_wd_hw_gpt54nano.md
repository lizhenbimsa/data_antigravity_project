---
family_id: F529
columns:
- sum_wd_hw_gpt54nano_ctx
- sum_wd_hw_gpt54nano_full
- sum_wd_hw_gpt54nano_ss
unit: 无量纲权重和 (跟风衰减权重之银行-年加总, 非情感分值本身)
formula: 'sum_wd_hw_gpt54nano_{track} = Σ_i∈(bank,year,track) herd_weight_{track,i} · 1[gpt54nano_score_{track,i} 非缺失], 其中 herd_weight 由 stage 24 (herd_decay_processor) 按跟风/抄稿衰减规则逐篇计算, 1[·] 为 gpt54nano 该篇该轨情感分值有效性掩码 (runner.py::_build_llm_valid_masked_weights 生成的 valid-mask 分母列)'
producer: pipeline\panel\runner.py::_build_llm_valid_masked_weights (第 436 行, article-level 掩码构造; encode.py 内仅注释引用 runner._build_llm_valid_masked_weights, 未自行定义同名函数) + pipeline\panel\encode.py::aggregate_panel/agg 聚合 sum (bank-year 加总, encode.py:1197-1203); pipeline\panel\runner.py::步骤 3d (跟风衰减权重逐篇乘算前置)
upstream:
- 21_tone_llms.parquet (gpt54nano_score_full/_ctx/_ss)
- 24_herd_decay_processor.parquet (herd_weight_full/_ctx/_ss)
citations:
- doi: "10.1016/j.jfineco.2017.01.006"
  type: journal
  authors: "Hwang, B.-H., & Kim, H. H."
  year: 2017
  title: "It pays to write well"
  venue: "Journal of Financial Economics"
  vol: "124"
  issue: "2"
  pages_or_artno: "373-394"
- doi: "10.1073/pnas.2305016120"
  type: journal
  authors: "Gilardi, F., Alizadeh, M., & Kubli, M."
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: "Proceedings of the National Academy of Sciences"
  vol: "120"
  issue: "30"
  pages_or_artno: "e2305016120"
- doi: "10.1126/sciadv.adp1528"
  type: journal
  authors: "Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E."
  year: 2024
  title: "Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy"
  venue: "Science Advances"
  vol: "10"
  issue: "45"
  pages_or_artno: "eadp1528"
- doi: "10.1002/isaf.1549"
  type: journal
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: "Intelligent Systems in Accounting, Finance and Management"
  vol: "31"
  issue: "1"
  pages_or_artno: "e1549"
- doi: "10.1080/19312458.2024.2378690"
  type: "journal"
  authors: "Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K."
  year: 2025
  title: "On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions"
  venue: "Communication Methods and Measures"
  vol: "19"
  issue: "1"
  pages_or_artno: "46-62"
- doi: "10.2139/ssrn.5395056"
  type: "wp"
  authors: "Liu, Y., Liu, J., & Wang, T."
  year: 2025
  title: "Large Language Model Disagreement"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "5395056"
new_dois: []
---

## CORE

【构念与来源】
sum_wd_hw_gpt54nano_full / _ctx / _ss 三列是"跟风衰减加权 (herd-weighted) 语调"计算链条中的分母支持列, 而非情感测度本身。它们记录的是: 在某银行-年-轨道单元内, 有效参与 gpt54nano (三家 LLM 投票之一, 见 CLAUDE.md「LLM 三家/BERT 三模型互为稳健性」条) 情感打分的全部文章, 各自的跟风衰减权重 (herd_weight) 之和。"wd" 取自源码内部命名 `_wd_hw_*` (weighted-denominator·herd-weight 的缩写), "hw" 即 herd weight, "gpt54nano" 指三家投票 LLM 中的 `gpt-5.4-nano` 模型 (三家为 gpt54nano/gemini31/deepseekv4, 互为稳健性、不分主次, 详见下文)。该家族与 sum_herd_weight_{track} (家族外, 面向 llm_vote 全体投票口径) 的区别在于: sum_herd_weight 统计的是"跟风衰减引擎认定有效"的全部文章权重和, 而 sum_wd_hw_gpt54nano_{track} 额外叠加了"gpt54nano 该篇该轨情感分值非缺失"这一 model-specific 有效性掩码, 因此分母口径与分子 (gpt54nano_score_hw_sum_{track}, 属另一家族) 严格同域 — encode.py 内部注释称之为"分子分母同域" (encode-01 fix, 2026-06-10), 即分子只累加 gpt54nano 有效打分文章的加权分值, 分母也只累加这些同一批文章的权重, 二者相除才能得到无偏的跟风衰减加权平均语调 avg 值, 避免因某些文章 gpt54nano 缺失打分而分子分母错位导致系统性偏差。
【方法学与计算】
跟风衰减权重 herd_weight 本身产自 stage 24 (`24_herd_decay_processor`), 其构造动机是媒体报道内容普遍存在"抄稿/跟风"现象 (herding): 同一事件短时间内被多家媒体转载或高度雷同改写的报道, 对市场信息含量的边际贡献应打折, 否则简单等权平均会让"重复报道的事件"在语调聚合中被过度加权, 扭曲银行-年语调的真实信息密度。herd_weight 对每篇文章赋予 (0,1] 区间的衰减系数 (与该文章跟同期同银行报道的雷同/聚集程度负相关), 三轨 full/ctx/ss 各自独立计算 herd_weight (因为不同轨道所用文本窗口不同, 雷同判定基于该轨道自身文本, 三轨之间互不借用)。在此基础上, encode.py 调用 runner.py 中定义的 `_build_llm_valid_masked_weights` 为每个 LLM 模型分别构造 valid-mask 分母: 对 gpt54nano 而言, 即把 `herd_weight_{track}` 在 `gpt54nano_score_{track}` 缺失的行置为缺失 (`.where(notna)`), 得到该模型专属的 `_wd_hw_gpt54nano_{track}` 篇章级序列, 再由 `aggregate_panel` 的聚合字典按 `(bank, year)` 分组求和, 落到面板级列 `sum_wd_hw_gpt54nano_{track}`。下游使用方通常以 `gpt54nano_score_hw_sum_{track} / sum_wd_hw_gpt54nano_{track}` 的形式还原出跟风衰减加权平均语调 (对标未加权的 `avg_gpt54nano_score_{track}`), 二者对比构成一组"是否控制媒体跟风偏差"的稳健性比较, 而非另立主测度。
【文献定位】
跟风衰减/媒体重复度打折的构造思路呼应了媒体情感研究中"信息重复不等于信息增量"这一常见主张; 本仓库把该思路制度化为逐篇权重再按模型做 valid-mask 加总, 属于工程实现层面的方法学移植而非新方法论创新。gpt54nano 作为三家投票 LLM 之一的 model-specific 权重分母设计, 部分呼应了 Gilardi, Alizadeh & Kubli (2023, *PNAS*) 关于 ChatGPT 类大语言模型在文本标注任务上可达到甚至超过人类众包标注者质量与效率的发现——这一发现是本仓库敢于把 LLM 打分 (而非纯人工标注) 作为跟风加权分母掩码之依据的方法论前提之一; 同时也呼应了 Schoenegger, Tuminauskaite, Park, Bastos & Tetlock (2024, *Science Advances*) 关于以多模型/多主体集成 (ensemble) 预测优于依赖单一模型的发现, 支撑本仓库坚持三家 LLM (gpt54nano/gemini31/deepseekv4) 各自独立走完整套"打分→跟风加权→分母掩码→面板聚合"链条、互为稳健性、不分主次, 而不是只信任单一厂商的输出这一设计选择。Todd, Bowden & Moshfeghi (2024, *Intelligent Systems in Accounting, Finance and Management*) 对金融文本情感分析文献的系统综述同样强调, 度量的稳健性核查 (含权重构造的敏感性) 是该领域方法论演进的核心议题之一, 本家族三列即服务于该核查链路中的分母核算环节。Hwang & Kim (2017, *Journal of Financial Economics*) 关于文本写作质量/信息密度对金融市场反应存在系统性影响的发现, 可作为"同质重复文本应被降权"这一构造动机的间接类比佐证 (而非直接实证支撑): 若不对雷同报道降权, 简单等权聚合会把"写法雷同但信息量低"的批量转载文章与"写法独特、信息密度高"的原创报道同等对待, 稀释后者对银行-年语调信号的贡献, 二者在"文本质量/独特性影响市场信息含量"这一更宽泛的经济学直觉上相通, 但 Hwang & Kim 本身并未直接研究跟风/重复报道降权问题。 上述引证之外, 尚有两条更贴近本家族 model-specific 掩码本身的近期锚点。Laurer、Casas 与 Welbers (2025) 以对照实验系统检验语言模型作为测量工具的效度问题, 证明指令/提示设计会实质改变效度与偏误; 本家族分母的核心构件恰是"gpt54nano 在该轨给出有效判断"这一掩码, 其覆盖面即模型效度的函数, 该文因而锚定的是本族分母的效度前提而非其加权口径。迁移边界须诚实标明: 原文对象是传播学英文文本分类任务与开源指令微调模型, 本仓库是中文新闻 + 三家商用 API 模型; 原文结论支持"加指令可提效度", 而本仓库嵌入侧刻意零 instruct 前缀、情感提示词 v8 已字节冻结, 两者设计取向不同, 不可直接迁移; 原文亦未涉及任何权重加权分母口径。Liu、Liu 与 Wang (2025) 以金融文本为对象度量并实证刻画不同大语言模型判断之间的分歧程度, 可解释本家族与 gemini31/deepseekv4 对应分母为何彼此不等——差异全部来自各家有效打分覆盖面与判断的不同。须注意该文系 SSRN 工作论文, 尚未经期刊同行评审; 且原文把分歧本身当作待研究的信号/噪声对象, 本仓库不将分歧立为变量, 只以各家有效性掩码构造并排分母, 模型集合与语料亦与本仓库三家 + 中文银行金科语料不同, 故引用严格限于"跨模型分歧存在"这一层。
【口径铁律复述】
本家族三列严格对齐三轨 full/ctx/ss 架构: full=标题+正文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗口 (无同句共现回退为全文, `ss_is_fallback=True`, 镜像 ctx 的回退语义, 共享 `n_articles` 分母)。三轨权重分母各自独立计算、各自 just-identified 并排、互为稳健性不分主次, 禁止混入同一 over-identified Hansen J 设定。gpt54nano 作为三家投票 LLM 之一, 其 model-specific 分母同样与 gemini31/deepseekv4 对应分母互为稳健性并排, 不设跨模型合并的单一权威分母。留篇门控口径为 full-only (2026-06-29): 一篇报道是否计入"银行金科报道"由 `llm_verified_full` 判定, ctx/ss 轨的分母加总行宇宙是 full 留篇集合的子集, 而非独立扩样。
</br>

## VAR: sum_wd_hw_gpt54nano_ctx

【变体差分】
本列取轨道后缀 `_ctx`, 即标题+实体窗口文本轨。该轨用于聚合的 herd_weight 来自 stage 24 对 `content_ctx` 文本 (stage 14 `ctx_materializer` 物化) 计算的跟风衰减系数, 与 `_full`/`_ss` 两轨的 herd_weight 相互独立计算 (雷同度判定只看该轨自身文本窗口, 不借用其他轨道信息)。valid-mask 掩码同样只看 `gpt54nano_score_ctx` 是否缺失: 若某篇文章在 ctx 轨下因文本窗口内无有效情感信号而被 LLM 判定缺失评分 (但 full 轨可能有效), 该篇不计入本列; 反之亦然。ctx 轨的行宇宙受 full-only 留篇门控约束, 即只统计 `llm_verified_full == True` 集合内的文章 (ctx 是 conditional-on-full 的稳健性测度轨, 不单独扩大留篇范围)。本列与 `sum_wd_hw_gpt54nano_full` 之间的差异幅度 (在同一银行-年内) 反映了"只看实体窗口局部语境"相较"看全文"时, gpt54nano 情感打分有效性 (是否缺失) 与文章跟风程度 (herd_weight 数值) 两者叠加后的净效应, 二者互为稳健性并排比较, 不应取二者比值或差值作为新的因果解释变量, 更不能与 `_full`/`_ss` 同放进同一 over-identified 检验设定。分析者若要检验"情感结论是否依赖全文信息还是仅依赖实体附近语境", 应分别用 `_ctx` 与 `_full` 对应的加权平均语调 (分子/本列分母) 各自跑一遍回归比较系数符号与显著性, 而非在同一模型内同时纳入两轨分母。

## VAR: sum_wd_hw_gpt54nano_full

【变体差分】
本列取轨道后缀 `_full`, 即标题+正文全文轨, 是三轨中的 canonical/主轨 (P1 主线 `bank_fintech_tone` 处理变量已切至 `_full`, 留篇门控本身即以 full 轨的 `llm_verified_full` 为准)。herd_weight 在此轨下基于 stage 14 物化的 `content_full` (原文标题+正文全量拼接) 计算跟风衰减系数, 反映的是"整篇报道与同期同银行其他整篇报道"的雷同/聚集程度, 覆盖信息量最大、窗口最宽的文本口径。valid-mask 掩码取 `gpt54nano_score_full` 非缺失的文章子集; 由于留篇门控本身锚定 full 轨的 `llm_verified_full`, 本列的行宇宙即为该论文/面板口径下"确认为银行-金科相关报道"的核心样本, ctx/ss 两轨均是以本列所在 full 集合为超集的子集测度。分析者构造 gpt54nano 跟风衰减加权平均语调 (`gpt54nano_score_hw_sum_full / sum_wd_hw_gpt54nano_full`) 时, 本列即为该比值的分母, 是三轨中默认优先使用、但仍与 ctx/ss 两轨互为稳健性并排、不构成对后两者的统计学优先级的口径。需要特别说明的是, full 轨的样本量通常在三轨中最大 (因为全文覆盖的信息最完整, gpt54nano 在 full 轨给出有效评分而在 ctx/ss 轨因窗口过窄返回缺失的概率更低), 因此 `sum_wd_hw_gpt54nano_full` 在同一银行-年内一般不小于对应的 `_ctx`/`_ss` 两列; 但这只是样本覆盖的自然结果, 不意味着 full 轨的加权平均语调数值本身更"准确" — 三轨仍应作为互为稳健性、不分主次的并排设定看待。此外, full 轨 herd_weight 的雷同度判定覆盖标题与全部正文, 相较 ctx/ss 更容易捕捉到"同一事件被多家媒体几乎逐字转载"的整篇雷同现象, 因此在存在大规模通稿转发的年份, full 轨对应的加权分母降权效应通常最明显, 这也是三轨敏感性对比中值得单独关注的一个维度。

## VAR: sum_wd_hw_gpt54nano_ss

【变体差分】
本列取轨道后缀 `_ss`, 即标题+"银行∧金科词同句共现 (±N 句窗, 默认 N=1, 见 `config/filtering.yaml::context_window.ss_sentence_radius`)"文本轨, 是三轨中窗口最窄、对"银行与金科议题是否真正同处一个语境"要求最严的口径。herd_weight 在此轨下基于 `content_ss` 计算, 若某篇文章不存在银行与金科词的同句共现, 则该轨回退为全文 body 且置 `ss_is_fallback=True` (镜像 ctx 轨的回退语义, 与 ctx 共享同一 `n_articles` 分母口径), 此时该篇的 herd_weight_ss 实质上退化为对全文计算的雷同度, 但仍独立于 `_full` 轨单独计算 (不直接复用 `herd_weight_full` 的数值)。valid-mask 掩码取 `gpt54nano_score_ss` 非缺失的文章子集; 若 `FINTECH_AC` 词典缺失 (`FINTECH_AC=None`) 导致全体 `*_is_fallback` 置 True, ss 轨将优雅退化为等价于 full 轨的行为, 但列名与聚合逻辑保持独立不变。本列与 `_full`/`_ctx` 两列并排构成三轨稳健性梯子的第三支, 各自 just-identified、互为稳健性、不分主次, 分析者不得将三列分母混入同一 over-identified Hansen J 设定, 也不得跨轨相加或取平均后作为单一"总权重"使用。由于 ss 轨对"同句共现"的要求最严, 该轨的有效样本 (未回退的真实同句共现文章) 往往显著少于 ctx/ss 两轨, 使得 `sum_wd_hw_gpt54nano_ss` 在很多银行-年单元内主要由回退样本 (`ss_is_fallback=True`, 即退化为全文口径) 的 herd_weight 贡献, 分析者在解读该列数值差异时应结合面板中 `ss_is_fallback` 的占比一并考察, 避免把"回退退化导致的数值趋同"误读为"ss 轨与 full 轨结论一致"的独立证据; 二者在回退主导的单元里本质上是同一批文章的重复计算, 稳健性含金量应打折看待, 只有在非回退 (真实同句共现) 样本占比较高的银行-年单元, ss 轨才提供与 full/ctx 真正正交的额外识别信息。
<!-- rendered-citations:begin -->
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K. (2025). On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions. Communication Methods and Measures, 19(1), 46-62. https://doi.org/10.1080/19312458.2024.2378690
Liu, Y., Liu, J., & Wang, T. (2025). Large Language Model Disagreement. SSRN Electronic Journal No. 5395056 [Working Paper]. https://doi.org/10.2139/ssrn.5395056
<!-- rendered-citations:end -->
