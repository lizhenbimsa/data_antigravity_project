---
family_id: F067
columns:
- avg_sent_len_ctx
- avg_sent_len_full
- avg_sent_len_ss
unit: 字符数每句 (article-level 平均句长, 再取 bank-year 均值; 有量纲)
formula: "avg_sent_len{track} = mean_over_articles( avg_sentence_len{track} ); avg_sentence_len{track} = 篇内总字符数 / 篇内句数 (按句末标点切句)"
producer: news_process/pipeline/panel/encode.py
upstream:
  - 14_materialize_ctx.parquet (content_full, content_ctx, content_ss)
  - 文章级可读性列 avg_sentence_len{track} (由 sentiment 模块 pipeline/sentiment/tone_words.py::_compute_readability 计算、经 analyze 主路径写回; encode.py 仅做 bank-year mean 聚合)
citations:
  - doi: 10.1002/widm.70019
    type: journal
    authors: Alva Principe, R., Chiarini, N., & Viviani, M.
    year: 2025
    title: "Long document classification in the transformer era: A survey on challenges, advances, and open issues"
    venue: WIREs Data Mining and Knowledge Discovery
    vol: 15
    issue: 2
    pages_or_artno: e70019
  - doi: 10.1093/rfs/hhad044
    type: journal
    authors: Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A.
    year: 2023
    title: "Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1"
    venue: The Review of Financial Studies
    vol: 36
    issue: 12
    pages_or_artno: 4919-4964
  - doi: 10.1093/qje/qjz021
    type: journal
    authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
    year: 2019
    title: "Firm-level political risk: Measurement and effects"
    venue: The Quarterly Journal of Economics
    vol: 134
    issue: 4
    pages_or_artno: 2135-2202
  - doi: 10.1016/j.jocs.2010.12.007
    type: journal
    authors: Bollen, J., Mao, H., & Zeng, X.
    year: 2011
    title: "Twitter mood predicts the stock market"
    venue: Journal of Computational Science
    vol: 2
    issue: 1
    pages_or_artno: 1-8
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是一家银行在某一年度所获媒体报道的平均句长 (average sentence length), 即报道文本经切句后每一句所含字符数的篇内均值, 再在 bank-year 层面对该年度留篇报道取算术平均。它属于文本可读性 (readability) 与句法复杂度控制变量族, 参照 Loughran 与 McDonald (2014) 在会计与金融文本分析中确立的可读性控制传统: 当研究把新闻语调、金融科技关注度、报道属性等文本派生量作为处理变量或结果变量时, 文本本身的书写风格 (句子长短、用词难度、篇幅) 会与这些语义信号共变, 若不加控制便可能把纯粹的文体差异误读为语义差异。平均句长是这一族控制量中最基础、最稳健的一维: 句子越长, 通常意味着从句嵌套更多、信息打包密度更高、阅读认知负荷更大, 因此长句占优的报道往往被认为可读性较低。本族与词汇难度 (罕见词比率、生僻字比率)、名词化率、功能词比率、具体性指数、篇内冗余等姊妹控制量并列, 共同刻画报道文本的"形式"维度, 与刻画"内容"维度的语调、属性、共现测度正交, 从而在计量中充当剥离文体混杂的协变量。

【方法学与计算】
计算分两层。文章层由 sentiment 模块 tone_words.py 的 _compute_readability 承担 (非 lexical/controls 模块): 对每篇报道先按中文句末标点切句得到句集, 剔除空白句后, 篇内各句去空白后的字符总数除以句数即得该篇平均句长 avg_sentence_len; 句数取 max(句集长度, 1) 作分母, 故正常路径永不产生除零或 NaN。空文本或退化短文本走统一的空文章返回契约 _empty_article_result, 该契约将三个可读性长度列 (含 avg_sentence_len) 显式置 0.0——与语调 score/ratio 空文本置 NaN 的缺失契约刻意不同: 对长度类度量而言, 空文本的长度为 0 是真值而非缺失, 因此空报道以 0.0 计入。这意味着本列在文章层从不产出 NaN。面板层: encode.py 的 H 段可读性聚合把文章级 avg_sentence_len{track} 以 mean 归约到 bank-year 单元, 得到 avg_sent_len{track}; 由于上游无 NaN 产出, 该 mean 是对全部留篇报道句长的直接算术平均, 个别空报道会以 0.0 真值参与并相应拉低该年度均值 (此为 by-design 的长度契约, 非缺陷)——因此不应把本列理解为"自动跳过缺失、单篇不影响均值"的度量, 其年度水平会随该年空/极短报道占比而系统性下移。单位为字符每句, 属有量纲量, 不宜与无量纲的比率型控制 (如罕见词比率) 直接比较绝对水平, 在回归中一般各自标准化后使用。本族沿三轨物化: full 轨文本为标题 prepend 加全文正文, ctx 轨为标题加实体上下文窗口, ss 轨为标题加银行与金融科技同句共现窗口 (回退时镜像 ctx 语义, 即无同句共现则退化为全文正文并置 ss_is_fallback)。三轨文本在 stage 14 ctx_materializer 统一物化, 上游原始内容列不动。留篇门控采 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科报道宇宙, 仅由 full 轨的 llm_verified_full 判定, ctx/ss 轨降为 conditional-on-full 的测度与稳健性轨, 其行宇宙是 full 留篇集的子集。因此三轨的 avg_sent_len 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混进同一 over-identified 的 Hansen J 过度识别检验; 它们是同一构念在不同文本切片上的平行测量, 而非可加分解。

【文献定位】
把文本形式特征作为控制或处理纳入公司—年度、银行—年度面板, 是文本即数据 (text-as-data) 金融研究的标准做法。Hassan 等 (2019) 在其构造企业级政治风险测度的经典工作中, 系统地在文本层做切句与句法解析, 并对文档长度、样板化程度等书写特征加以处理, 以确保所提取的语义暴露不被纯篇幅或文体驱动; Hassan 等 (2023) 把同一测量范式推广到流行病暴露, 再次说明句、段层面的文本结构量是此类面板测度可信度的前提。平均句长正是这一处理逻辑中最直接的形式协变量。从文本处理方法本身看, Alva Principe 等 (2025) 对 transformer 时代长文档分类的综述指出, 文档与句子长度是决定文本表示与下游任务表现的一阶因素, 长句、长文档会显著改变模型对信息的编码方式, 这为把句长作为独立的文本复杂度维度加以控制提供了方法学依据。Bollen 等 (2011) 则代表了以文本派生信号预测金融市场的更广脉络, 提示语义信号与文体特征在实证中必须彼此剥离, 否则文本测度的外部效度存疑。综合而言, 本族的价值不在于单独进入结构方程, 而在于作为稳健的形式控制, 保证语调、关注度、属性等语义处理变量的识别不被报道书写风格的年度或银行间差异所污染。

## VAR: avg_sent_len_full

【变体差分】
本列是 full 轨的平均句长, 也是本家族的门控基准轨。其文本口径为标题 prepend 加全文正文, 即在 stage 14 由 ctx_materializer 物化的 content_full; 切句与字符计数覆盖整篇报道, 因而在三轨中信息量最全、样本覆盖最广。依 full-only 留篇门控口径 (2026-06-29), 一篇报道是否被判为银行金融科技报道、从而进入 bank-year 聚合分母, 完全由 full 轨的 llm_verified_full 决定; 故 avg_sent_len_full 的行宇宙即该银行该年的全部留篇报道, 而 ctx 与 ss 两轨只在此留篇集的子集上取值。正因如此, full 轨承担 canonical 角色: 当下游把可读性作为控制纳入主回归时, 优先使用本列; ctx/ss 两轨作为条件于 full 的稳健性轨与其并排。三轨各自 just-identified, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。本列度量的是整篇报道句法长度的形式特征, 与刻画银行金融科技语义关系的语调、属性、共现测度正交, 且不受词典、模型、阈值、权重、滞后等任何维度的调制——它纯由 full 轨文本的切句结果驱动, 与家族内 ctx/ss 两列的唯一差别就在文本切片范围。在实证使用上, 本列作为形式协变量出现在以语调或关注度为处理变量的主设定中, 目的是吸收报道书写风格在银行间与年度间的系统性差异, 避免把长句偏好较高的媒体所报道的银行误判为语义信号更强或更弱; 由于句长为有量纲量, 通常在回归前对本列做组内标准化处理, 使其系数可与其他可读性维度的贡献相互比较。

## VAR: avg_sent_len_ctx

【变体差分】
本列是 ctx 轨的平均句长, 文本口径为标题 prepend 加实体上下文窗口 content_ctx, 即只截取围绕目标银行等实体的邻近上下文而非整篇正文再切句、计长。相对 full 轨, ctx 轨聚焦于实体相关段落, 屏蔽掉与银行金融科技主题无关的篇首导语、背景铺陈或尾部套话, 因此其平均句长刻画的是"实体语境局部"的句法长度特征, 是对 full 轨整篇口径的稳健性替代测量。依 full-only 门控, 本列为 conditional-on-full 轨: 其取值只在 full 轨已判留篇的报道子集上计算, per-track 列照常按各自文本切片归约, 不借用 full 轨分母。ctx 与 full、ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J 过度识别检验。本列与家族内另两列的唯一区别在文本切片范围 (实体窗口 vs 全文 vs 同句共现窗), 不涉及任何词典、模型、阈值、判据、权重或滞后维度的差异; 当研究者关心可读性控制是否对文本截取口径敏感时, 应把本列与 full 轨结果并置比较, 以证主结论不被文本窗口选择驱动。由于实体窗口剔除了与银行金融科技主题无关的篇幅, ctx 轨的平均句长往往对报道整体篇幅波动更不敏感, 更能反映实体语境本身的句法密度; 但窗口截取也可能切断跨句从句, 使个别句子的字符计数偏短, 这一测量取舍正是把本列列为稳健性轨而非主轨的原因。当 ctx 与 full 两轨的可读性控制在主回归中给出方向一致的结论时, 即可佐证语义处理变量的识别对文本截取口径稳健。

## VAR: avg_sent_len_ss

【变体差分】
本列是 ss 轨的平均句长, 文本口径为标题 prepend 加银行与金融科技同句共现窗口 content_ss, 即只保留目标银行与金融科技词在同一句 (含前后各若干句半径, 由 filtering 配置的 ss_sentence_radius 控制, 默认 1) 共现所界定的最窄语境, 再切句、计长。这是三轨中语境最紧、最贴近银行金融科技共现事件的文本切片, 度量的是共现语境局部的句法长度。其回退语义严格镜像 ctx: 若某留篇报道内不存在银行与金融科技的同句共现, 则 content_ss 退化为全文正文, 并置 ss_is_fallback 为真, 与 ctx 轨共享 n_articles 分母; 若金融科技 AC 自动机为空则该轨 is_fallback 全真, 属优雅降级。依 full-only 门控, 本列同为 conditional-on-full 稳健性轨, 只在 full 留篇子集上取值, 不借 full 分母。ss、ctx、full 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。本列与家族另两列的唯一差异仍在文本切片范围, 不含任何模型、阈值、权重或滞后调制; 在开发期 T 较小时 ss 轨因共现语料稀疏可能退化, 属预期行为, 不影响生产规模下的正常取值。ss 轨把语境收窄到共现事件所在句及其邻近半径, 因此其平均句长最贴近"银行与金融科技被同时提及"这一瞬时语境的书写特征, 是三轨中语境最专一的形式测量; 当共现频繁的报道其同句往往更长或更短时, 本列相对 full、ctx 两轨的偏离即揭示了共现语境与整篇语境在文体上的差异。正因窗口最窄, 本列在语料稀疏时最易触发全文回退, 使用时须结合 ss_is_fallback 比例判读其有效样本, 并与 full、ctx 两轨并置以确认可读性控制的结论稳健。

<!-- rendered-citations:begin -->
Alva Principe, R., Chiarini, N., & Viviani, M. (2025). Long document classification in the transformer era: A survey on challenges, advances, and open issues. WIREs Data Mining and Knowledge Discovery, 15(2), e70019. https://doi.org/10.1002/widm.70019
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Bollen, J., Mao, H., & Zeng, X. (2011). Twitter mood predicts the stock market. Journal of Computational Science, 2(1), 1-8. https://doi.org/10.1016/j.jocs.2010.12.007
<!-- rendered-citations:end -->
