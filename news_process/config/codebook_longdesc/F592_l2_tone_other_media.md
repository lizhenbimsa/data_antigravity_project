---
family_id: F592
columns:
- tone_other_media_ctx
- tone_other_media_full
- tone_other_media_ss
unit: 语调/正向倾向得分 (连续, 名义 [-1,1]; bank-year 面板聚合均值)
formula: 'tone_other_media{track} = mean(llm_vote_score{track}) 分组于 (target_bank, year), 限定样本子集 _media_type == "other" (df["媒体(中文)"] 经 _classify_content 规则分类既非 fin 也非 comp 的剩余媒体类); track ∈ {_full, _ctx, _ss}, 源列缺失 (`llm_vote_score{track} not in df.columns`) 则整轨优雅跳过不产列'
producer: pipeline\panel\attention_media.py ; pipeline\panel\export.py
upstream:
- 21_tone_llms.parquet (llm_vote_score_full / _ctx / _ss)
- 11_news_bank.parquet ; 12_news_fintech.parquet (媒体(中文) 原始来源字段)
citations:
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock market'
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: 'Firm-level political risk: Measurement and effects'
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: What drives media slant? Evidence from U.S. daily newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
- doi: "10.1016/j.frl.2023.104865"
  title: "Media sentiment and management earnings forecasts: Evidence from China"
  authors: "Chen, T., Chiu, P.-C., & Wang, Y."
  year: 2024
  venue: "Finance Research Letters"
  type: "journal"
- doi: "10.1016/j.ememar.2024.101234"
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  venue: "Emerging Markets Review"
  type: "journal"
new_dois:
  - "10.1016/j.frl.2023.104865"
  - "10.1016/j.ememar.2024.101234"
---

## CORE

【构念与来源】
tone_other_media{track} 度量的是"剩余媒体渠道"(既非财经专业媒体 fin, 也非综合性大报 comp 的其余出处) 报道本银行时的平均语调, 是 attention_media.py 媒体异质性模块沿"内容类型"这一维度对 llm_vote_score{track} 做的一个切片均值。构念动机来自媒体经济学的一个基本观察: 不同媒体渠道在专业能力、编辑立场、受众定位、乃至与被报道对象的利益关联上系统性不同, 因此同一事件在不同渠道笔下的语调可能存在结构性差异, 而这种差异本身就是一个可被利用的信号来源 (Gentzkow & Shapiro (2010) 对媒体倾向成因的经典论证即建立在这一前提之上)。本家族与 tone_fin_media / tone_comp_media 是同一媒体三分类 (fin/comp/other) 下的并列切片, 三者穷尽样本 (即 fin_media_frac + comp_media_frac + [1 减去二者之和] 恰好覆盖 other 的隐含占比), 因此 tone_other_media 天然承担"基线/对照组"的解释角色: 它代表既非专业财经媒体、也非头部综合大报覆盖下的报道语调, 常被面板中的 tone_gap_fin_other / tone_gap_comp_other 用作差分基准 (fin 减 other、comp 减 other), 用以检验专业媒体或权威大报的语调是否系统性偏离一般媒体。
【方法学与计算】
产出路径分两段。第一段在 21_tone_llms.parquet 里, 由三家 LLM (gpt54nano/gemini31/deepseekv4) 对每篇文章逐轨 (full/ctx/ss) 投票产出 llm_vote_score{track} 这一篇章级语调分数; 第二段在 pipeline/panel/attention_media.py 里做面板聚合: 先用 _classify_content 规则把 df["媒体(中文)"] (原始媒体来源中文名) 分成 fin/comp/other 三类互斥标签, 写入临时列 _media_type; 再对每个 track (full/ctx/ss 依次遍历, 缺列 `if src not in df.columns: continue` 优雅跳过而非报错), 取 `_media_type == 'other'` 的子集, 按 (target_bank, year) groupby 后对 llm_vote_score{track} 取算术均值, 命名为 tone_other_media{track}, 再 left-merge 进 panel 主表。分母是"该银行该年、该 track 下由 other 类媒体产出且落入该 track 有效样本的篇数"; 若某银行-年在 other 媒体上恰好零篇覆盖, 该格为 NaN 而非 0 (均值算子对空组返回缺失, 不做人为填零, 避免把"无覆盖"误读为"零语调")。三轨遵循与家族兄弟 tone_fin_media / tone_comp_media 完全一致的三轨铁律: full/ctx/ss 各自基于同一批文章的不同文本窗口 (全文 / 实体上下文窗 / 银行∧金科同句窗) 独立跑一遍 LLM 打分再独立聚合, 三者是各自 just-identified 并排的稳健性配置, 互为稳健性、不分主次, 禁止把三轨混进同一个 over-identified 的 Hansen J 检验框架。ss 轨遵循全仓统一的回退语义 (镜像 ctx): 当某篇文章不存在银行∧金科同句共现窗口时, content_ss 退化为全文正文, 对应 ss_is_fallback 标记为 True, 但该篇文章依旧计入 n_articles 分母, 因此 tone_other_media_ss 在覆盖率上并不会因回退而系统性缩水, 只是退化样本在语义上更接近 full 轨。
【文献定位】
情感度量本身植根于 Tetlock (2007) 开创的"用媒体语调预测/刻画市场反应"范式, 该文首次系统证明报纸语调是可从文本中提取的定量信号; 本家族沿用其"语调作为可聚合的连续测度"思路, 但在中国银行业语境下引入媒体类型异质性的切片。You, Zhang & Zhang (2018) 的"谁在执笔"研究证明中国媒体报道存在系统性的渠道差异, 且这种差异部分源自记者与被报道公司之间的利益关联, 为把媒体按类型切片、检验语调是否随渠道系统变化提供了直接的理论支持——tone_gap_fin_other / tone_gap_comp_other 正是在这一逻辑下构造的诊断量。Holzman, Miller & Twedt (2023, *The Accounting Review*) 进一步表明媒体情绪本身会与企业信息披露事件 (如季度盈余公告) 交互放大或抑制市场反应, 说明"媒体语调"并非中性传声筒而是带有自身编辑倾向的中介变量, 这构成本家族切片设计 (专业财经媒体 vs 综合大报 vs 其余渠道) 的方法学依据: 若 other 类媒体的平均语调系统性偏离 fin/comp 两类, 则说明媒体类型本身携带信息, 需要在回归中加以控制或作为异质性来源单独讨论。中国场景下的应用先例可见 Fang, Wang, Wang & Yuan (2024) 对媒体情感与银行系统性风险关系的实证, 该文同样采用银行-年层面的媒体语调聚合口径, 与本家族在聚合粒度上高度可比。本家族及其上游 llm_vote_score 与 P2 注意力测度族 (Hassan et al. 2019 firm-level political risk 方法学脉络下的 attention_index 系列) 共享同一批文章池, 但语调聚合 (本家族) 与注意力强度聚合 (attention_index) 是两个正交维度, 前者回答"报道得正面还是负面", 后者回答"报道得多还是少"。 Chen, Chiu & Wang (2024, Finance Research Letters) 该文以2007-2022年中国A股上市公司为样本, 发现媒体情绪与管理层盈余预测的发布倾向及预测精度存在系统性关联, 为按媒体渠道类型切片语调测度提供了中国场景下的实证支持。 Xu, Hua & Zhang (2025, Emerging Markets Review) 该文用文本分析结合BERT构建中国官方媒体情绪指数, 发现负面官方媒体情绪主要通过散户交易渠道预测市场收益反转, 说明媒体渠道类型 (官方vs其余) 携带异质信息, 支持本家族按渠道切片语调的构念设计。

## VAR: tone_other_media_ctx

【变体差分】
本列是 ctx 轨: 分子 llm_vote_score_ctx 由 LLM 在"标题 + 实体上下文窗口" (标题 prepend 后, 围绕目标银行/金科实体截取的上下文片段, 而非全文) 上打分, 相较 full 轨剔除了与银行-金科关系无直接语义关联的大段正文, 更贴近"报道焦点段落"的语调而非"全文整体基调"。分母同样限定为该银行-年下 _media_type=='other' 且 llm_vote_score_ctx 非缺失的文章数; 若该银行-年样本中所有 other 类文章在 ctx 轨均无有效实体窗口 (理论上罕见, 因 ctx 缺失通常靠回退到全文兜底而非直接置空), 则该格聚合为 NaN。ctx 轨与 full/ss 轨在同一 groupby-mean 逻辑下各自独立计算, 三者是并排的稳健性配置而非层级关系——ctx 并非 full 的"更精确版本", 而是对"语调应基于全文还是应基于焦点片段"这一构念选择的显式敏感性检验, 使用时应报告三轨结果而非只挑 ctx 或只挑 full。与本家族兄弟列 tone_fin_media_ctx / tone_comp_media_ctx 共享完全相同的 ctx 轨文本构造与聚合口径, 唯一差异是被聚合的媒体子样本从 fin/comp 换成了 other。使用建议: 若研究问题聚焦于"银行与金科关系相关段落的语调是否随媒体渠道系统性变化", ctx 轨比 full 轨更贴合构念, 因为它把与该关系无关的大段背景叙述从打分文本中剔除, 降低了噪声段落对整体语调均值的稀释效应; 但代价是当某类媒体 (如篇幅短、叙事密度高的 other 类渠道) 本身较少出现可清晰界定的实体上下文窗口时, 该轨的有效样本量可能小于 full 轨, 需结合 n_articles 分母交叉核对再下结论。

## VAR: tone_other_media_full

【变体差分】
本列是 full 轨, 也是本家族的口径基准 (canonical): 分子 llm_vote_score_full 由 LLM 在"标题 + 完整正文"上打分, 未做任何文本截取, 是三轨中信息量最完整、也是留篇门控 (full-only gate, 2026-06-29 起) 唯一直接依赖的一轨——即"某篇文章是否算作一篇有效的银行-金科报道"这一判定只看 llm_verified_full, 而 ctx/ss 是在该门控确定的行宇宙子集上分轨计算的测度/稳健性轨, 并非独立的留篇口径。因此 tone_other_media_full 在样本覆盖 (n_articles) 意义上是最完整的一轨, ctx/ss 的样本行宇宙是 full 轨留篇集的子集。计算逻辑与 ctx/ss 完全一致 (同一 _media_type=='other' 子集分组均值), 差异只在于送入 LLM 打分的文本窗口。fin_media/comp_media/other_media 三个族的 _full 后缀列在面板导出层 (export.py) 被标注为"Avg Tone: Other Media (Full)"这类可读标签, 与 llm_vote_tone_full 的头部整体语调 (面板主处理变量, P1 canonical treatment) 是两个不同粒度的量: llm_vote_tone_full 是全样本 (不分媒体类型) 的银行-年整体语调, 而 tone_other_media_full 是限定在 other 类媒体子样本上的语调, 二者在数值上通常不相等且不应互相替代。作为三轨中样本最完整、门控地位最高的一轨, tone_other_media_full 是本家族在 tone_gap_fin_other_full / tone_gap_comp_other_full 两个差分诊断量中的减数基准: 若某银行-年的 fin 减 other 或 comp 减 other 缺口显著为正, 说明专业财经媒体或综合大报对该银行的报道语调系统性优于一般媒体渠道, 这一判断的可靠性直接取决于 tone_other_media_full 分母 (other 类文章数) 是否足够, 分母过小 (如个位数) 时该格波动性偏大, 解读须谨慎。

## VAR: tone_other_media_ss

【变体差分】
本列是 ss 轨: 分子 llm_vote_score_ss 由 LLM 在"标题 + 银行∧金科实体同句 (±N 句窗, 默认 N=1) 共现片段"上打分, 是三轨中文本窗口最窄、语义最聚焦于"银行与金科关系本身"的一轨。回退语义镜像 ctx: 当某篇文章不存在银行∧金科同句共现时, content_ss 退化为全文正文, ss_is_fallback 置 True, 但该篇文章仍计入分母 (不会因回退而从 other 类聚合样本中剔除), 只是其打分文本此时等同于 full 轨。这意味着 tone_other_media_ss 在覆盖率上不因回退而系统性收缩, 但在退化比例较高的银行-年上, ss 轨的数值会向 full 轨靠拢, 二者相关性升高属预期现象而非计算错误。与 ctx 轨一样, ss 轨与 full/ctx 是并排的稳健性配置, 三者各自 just-identified, 检验或论证中不应把三轨强行并入同一个 over-identified 的过度识别框架 (如共用同一组工具变量做单一 Hansen J 检验), 而应分别报告、互相印证。ss 轨聚合逻辑 (`_media_type=='other'` 分组均值) 与 fin/comp 两个兄弟族的 _ss 后缀列完全同构, 唯一差异同样是被聚合的媒体子样本口径。使用建议: ss 轨适合作为"语调是否真的由银行-金科关系本身驱动、而非泛泛的银行整体报道基调驱动"这一构念争议的最严格检验——因为它把打分文本压缩到最贴近关系语义的同句片段, 若该轨结果与 full/ctx 两轨方向一致, 可显著增强"other 类媒体对银行-金科关系的语调倾向"这一结论的稳健性; 但由于同句共现窗口较窄, 该轨在 other 类媒体 (通常报道篇幅更碎片化) 上的回退比例可能高于 fin/comp 两类, 解读时应结合 ss_is_fallback 占比一并披露。
<!-- rendered-citations:begin -->
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Chen, T., Chiu, P.-C., & Wang, Y. (2024). Media sentiment and management earnings forecasts: Evidence from China. Finance Research Letters. https://doi.org/10.1016/j.frl.2023.104865
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
<!-- rendered-citations:end -->
