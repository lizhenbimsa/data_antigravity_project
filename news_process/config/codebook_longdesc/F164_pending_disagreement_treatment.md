---
family_id: F164
columns:
- cross_outlet_tone_variance_full
unit: 语调方差 (无量纲; outlet 级 tone 的跨来源方差, 事件窗内 episode 加权后聚合到 bank-year)
formula: "cross_outlet_tone_variance = Var_{m in M}(T_{m,b}); T_{m,b} = mean tone of outlet m's articles on bank b within event episode; require |M|>=2 else NaN; bank-year = article-count-weighted mean of per-episode cross-outlet variances (np.var, ddof=1)"
producer: news_process/pipeline/audit/cross_media_alpha.py (stage 39f) ; news_process/papers/bank_media_disagreement/tables.py
upstream:
- 21_tone_llms.parquet (article-level tone; full 轨留篇门控)
- 00_preprocessing.parquet (媒体来源 outlet 标识 + 事件窗时间戳)
citations:
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1016/j.gfj.2025.101126
  type: journal
  authors: Garcia, J.
  year: 2025
  title: "Beyond the headlines: Sentiment divergence and financial distress"
  venue: Global Finance Journal
  vol: 66
  pages_or_artno: 101126
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: "Measuring news sentiment"
  venue: Journal of Econometrics
  vol: 228
  issue: 2
  pages_or_artno: 221-243
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1111/j.1540-6261.2006.00885.x
  type: journal
  authors: Baker, M., & Wurgler, J.
  year: 2006
  title: "Investor sentiment and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 61
  issue: 4
  pages_or_artno: 1645-1680
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是「媒体分歧」构念的处理变量: 同一家银行在同一时间窗内, 被不同媒体来源 (outlet) 报道时所呈现的语调 (tone) 离散程度。直觉是, 当各家媒体对某银行的评价高度一致 (跨来源方差小) 时, 市场收到的是清晰、低噪声的信号; 当各家媒体众说纷纭、褒贬不一 (跨来源方差大) 时, 信号内含更强的观点分歧与不确定性。这一「跨来源语调方差」被第十篇 provisional 论文 bank_media_disagreement 采作正文级主处理变量, 用以检验媒体分歧对银行稳定性的作用; 其结果变量为 provisional 占位列 z_score (一个刻画银行稳定性/偿付能力的代理指标名, 待财务面板接入时构造实体), 此处不对其口径附加任何具体测度学限定, 仅按 CLAUDE.md 记载沿用该占位变量名。构念根源来自金融学「异质信念/分歧」传统与「文本情感即信号」传统的交汇: 前者认为投资者之间的意见分歧本身是资产定价的一个状态变量, 后者认为新闻文本的情感倾向是可度量的市场情绪代理。就本银行样本而言, 数据来源为经三轨情感流水线打分的文章级 tone, 以及预处理阶段保留的媒体来源字段与事件窗时间戳。

【方法学与计算】
生产实现位于 stage 39f 的 cross_media_alpha 审计模块。对每一个 (银行 b, 事件 episode) 二元组, 算法先收集在该事件窗内报道该银行的媒体集合 M, 并要求 |M| ≥ 2, 否则该 episode 记为缺失 (单一来源无从谈「跨来源」分歧); 随后对每家媒体 m 计算其窗口内文章 tone 的均值 T_{m,b}; 再取这些 outlet 级均值在 M 上的样本方差 (np.var, ddof=1) 作为该 episode 的跨来源语调方差; 最后把同一银行同一年内各 episode 的方差按 episode 内文章数加权求均值, 聚合到 bank-year。作为一致性稳健性的姊妹测度, 同一模块还并算 interval 尺度的 Krippendorff α 作为跨标注者 (此处「标注者」= 各媒体来源) 一致性指标。文章级 tone 遵循全仓 full-only 留篇门控 (2026-06-29): 一篇报道是否计入「银行金科报道」宇宙只看 full 轨的 LLM 判定, ctx/ss 轨为 conditional-on-full 的稳健性轨。三轨 full/ctx/ss 由此派生出三个并列变体, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J; ss 轨的回退语义镜像 ctx 轨 (无银行金科同句共现时降级为全文 body)。

【文献定位】
分歧作为定价状态变量的理论锚见 Carlin, Longstaff, and Matoba (2014), 该文在 Journal of Financial Economics 上直接把「分歧」与资产价格、收益与波动联系起来, 为本处理变量提供了「方差即分歧、分歧即风险溢价来源」的定价学理据; 投资者情绪作为横截面定价因子的经典证据见 Baker and Wurgler (2006), 该文奠定了「情绪可度量且系统性影响资产价格」的传统, 是本流水线把文本 tone 视为信号的上游前提。新近文献进一步把「分歧」从投资者层面推进到「新闻文本层面」: Li and Luan (2025) 以新闻构造投资者分歧并检验其对股票收益的可预测性, 与本处「跨来源语调方差」构念几乎同源; Garcia (2025) 直接研究「情感分歧」与财务困境的关系, 为把媒体分歧接入银行稳定性结果变量提供了同构念的实证先例。度量层面, Shapiro, Sudhof, and Wilson (2022) 系统讨论了新闻情感的可度量性与偏误校正, 是 tone 测度的方法学基准; 媒体情感对市场的约束与纪律作用见 Holzman, Miller, and Twedt (2023); 就中国银行样本的直接同域证据而言, Fang, Wang, Wang, and Yuan (2024) 检验了媒体情感、存款稳定性与银行系统性风险的关系, 与本论文的样本域、结果变量取向高度契合。综合而言, 本家族在「分歧定价」与「文本情感度量」两支文献的交汇处, 以跨来源方差把「媒体分歧」这一构念操作化。

## VAR: cross_outlet_tone_variance_full

【变体差分】
本列是家族在 full 轨上的实现, 也是 bank_media_disagreement paper_spec 冻结的 treatment.primary (main_track = _full)。full 轨的文本口径为「标题 prepend + 全文正文」, 与 ctx 轨 (标题 + 实体窗口)、ss 轨 (标题 + 银行金科同句 ±N 窗) 构成三轨并列; 三个 tone-variance 变体各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J, 这与政治词权重梯子、co-primary 双轨嵌入所遵循的铁律一致。留篇门控采 full-only 口径: 篇入样与否只看 full 轨 LLM 判定, 故 full 轨的跨来源方差建立在完整留篇集上, ctx/ss 为其条件子集轨; 在早期试跑盘上 T=2 的开发样本里 ss 轨可能因同句共现稀疏而部分缺列, build_summary_table 对缺列/NaN 防御性跳过, 不致整表崩。

需要特别标注的是本列的 tier=pending 状态与「同名异构」披露。stage 39f 模块产出的 cross_outlet_tone_variance_full 与第十篇 paper_spec 冻结的 main treatment 同名但不同构: spec 冻结的构造是 bank-year 无条件全年截面上 outlet 级均值的跨来源方差 (待新建, 属 M2-M3 里程碑), 而本审计模块的现实现是事件窗条件子样本上逐 episode 的跨来源方差再按 episode 内文章数加权聚合。两者差异有二: 其一, 估计域不同 (事件窗条件 vs 全年无条件); 其二, 聚合方式不同 (episode 加权均值 vs 单一截面计算)。因此本列当前不是 spec 承诺的最终主处理变量, 论文采用前须二选一: 或对齐 spec 冻结构造并起用新列名, 或重命名本模块产物以释放保留名; 相应地本列在面板中不实存, 属 pending 占位, 其单位为无量纲的跨来源语调方差 (聚合后 bank-year 标量), 语义上恒非负且随各媒体评价越发不一致而增大。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. Global Finance Journal, 66, 101126. https://doi.org/10.1016/j.gfj.2025.101126
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Baker, M., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. The Journal of Finance, 61(4), 1645-1680. https://doi.org/10.1111/j.1540-6261.2006.00885.x
<!-- rendered-citations:end -->
