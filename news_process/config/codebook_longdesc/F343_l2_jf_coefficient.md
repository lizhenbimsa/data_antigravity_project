---
family_id: F343
columns:
- jf_coefficient_ctx
- jf_coefficient_full
- jf_coefficient_ss
unit: 无量纲极性系数 (值域 [-1, 1])
formula: 'jf_coefficient = (P^2 - P*N) / T^2, P>N; = (P*N - N^2) / T^2, N>P; = 0, P=N; T=0 -> NaN (P=pos_count, N=neg_count, T=n_articles_llm_valid, 均逐轨对应 track 后缀; canonical Janis-Fadner 1965 / Deephouse 2000 分母, fix(jf-denominator, metric-audit 2026-06-10) 已由旧 (P+N)^2 式改为 T^2)'
producer: pipeline\panel\runner.py ; pipeline\panel\export.py
upstream:
- 21_tone_llms.parquet
citations:
- doi: 10.1016/j.jfineco.2018.11.009
  type: journal
  authors: Calomiris, C. W., & Mamaysky, H.
  year: 2019
  title: How news and its context drive risk and returns around the world
  venue: Journal of Financial Economics
  vol: '133'
  issue: '2'
  pages_or_artno: 299-336
- doi: 10.1016/j.jfineco.2016.01.032
  type: journal
  authors: Manela, A., & Moreira, A.
  year: 2017
  title: News implied volatility and disaster concerns
  venue: Journal of Financial Economics
  vol: '123'
  issue: '1'
  pages_or_artno: 137-162
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: 'Word power: A new approach for content analysis'
  venue: Journal of Financial Economics
  vol: '110'
  issue: '3'
  pages_or_artno: 712-729
- doi: "10.1016/j.iref.2025.104564"
  type: "journal"
  authors: "Branzoli, N., Marchetti, S., & Tarducci, E."
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "International Review of Economics & Finance"
  vol: "104"
  pages_or_artno: "104564"
- doi: "10.1016/j.aglobe.2026.100139"
  type: "journal"
  authors: "Huynh, T. H. H., & Nguyen, T. M. H."
  year: 2026
  title: "Signals in the news: How media reputation improves stock liquidity around the world"
  venue: "Asia and the Global Economy"
  vol: "6"
  issue: "1"
  pages_or_artno: "100139"
- doi: "10.3390/app16041987"
  type: "journal"
  authors: "Venčkauskas, A., Jusas, V., & Barisas, D."
  year: 2026
  title: "Evaluation of a Company’s Media Reputation Based on the Articles Published on News Portals"
  venue: "Applied Sciences"
  vol: "16"
  issue: "4"
  pages_or_artno: "1987"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是银行—金科报道在 bank-year 面板单元内的情感极性集中度, 即所谓 Janis-Fadner 系数 (Janis & Fadner 1965 提出的内容分析极性测度, 经 Deephouse (2000) 在管理学/媒体声誉研究中系统化为 J-F Coefficient 并广泛用于媒体口碑测量文献)。历史上本仓库曾把这一列错误标注为「Jiang et al. (2019) 姜富伟 PLS 市场情绪指数」, 该勘误已在 producer 源码注释 (pipeline\panel\export.py, 2026-06-05) 中留痕: 二者名字相近但构念完全不同, Jiang et al. (2019, JFE) 做的是跨市场投资者情绪 PLS 提取, 与本列所计算的单一 bank-year 单元内部报道极性无关, 本长文以 producer 源码为准记为 J-F 系数, 不再沿用 Jiang 2019 的误注。J-F 系数的直觉是: 单纯统计"正面篇数减负面篇数"或"正面占比"都不能区分「舆论高度一致地正面/负面」与「舆论两极分裂但净值恰好为零」这两种质地完全不同的媒体环境; J-F 系数通过把正负篇数的乘积项 P·N 计入分母侧的惩罚, 使得在总篇数 (P+N) 给定时, 极性越集中于一端 (即 P、N 差距越大) 系数绝对值越接近 1, 而 P、N 势均力敌 (争议度高) 时系数被压向 0, 从而同时刻画了「方向」与「集中度/一致性」两个维度, 是简单净情感值 (net tone) 的一个非线性再加工, 而非其替代品。

【方法学与计算】
producer 端 (pipeline\panel\runner.py) 的计算契约以 bank-year 面板单元为单位, 输入是同一轨道 (full/ctx/ss) 上由 stage 21 三家 LLM 多数投票产出并经 encode 层聚合到面板的 pos_count{track}/neg_count{track}/n_articles_llm_valid{track} 三列 (即该 bank-year、该轨道下判为正面/负面的文章篇数, 以及该轨道全部有效 LLM 投票篇数, 含正面+负面+中性)。设 P=pos_count{track}, N=neg_count{track}, T=n_articles_llm_valid{track} (T 即该轨道全部有效编码数, 含中性篇), 标准 J-F 系数 (Janis & Fadner 1965; Deephouse 2000, *Journal of Management*, 26(6) 系统化的 canonical 定义) 是以 T² 而非 (P+N)² 为分母的分段函数: 当 P>N 时取 (P²−PN)/T², 当 N>P 时取 (PN−N²)/T², 当 P=N (含 P=N=0 的情形) 时取 0, 值域被限制在 [−1, 1], 符号即报道净方向, 绝对值即极性集中度。本仓库产出该列的代码曾在早期版本误用 (P+N)² 作分母 (丢弃中性覆盖, 会对中性主导的 bank-year 系统性高估 |J-F| 绝对值, 例如 P=10、N=0、中性 90 篇的场景, 旧式给出 1.0 而 canonical T² 式仅给出 0.01), 该缺陷已在 `fix(jf-denominator, metric-audit 2026-06-10)` 中修复为以 T² 为分母的 canonical Deephouse (2000) 实现, 本长文按修复后的现行口径记述。真正触发 NaN 缺失的条件是 T=0 (该轨道该年该行完全没有任何 LLM 有效判定, 即该轨道情感彻底不可测), 而非 P+N=0; 若 P=N=0 但存在中性篇 (T>0, 即该行有报道但全部判为中性), 系数按上式的 P=N 分支输出 0.0, 表示"方向净值为零"而非"未测量"。这一"完全无有效投票即缺失、有中性覆盖但无方向差异则记 0"的两层区分与本仓库同族语调类指标的红线口径 (Allison 2001; Heckman 1979 关于缺失应与"测量到的中性/均衡"严格区分的一般原则) 相符, 使用者不应把两者混为一谈。三条轨道 (full/ctx/ss) 的 P、N、T 分别来自 stage 21 在标题+正文全文 (full)、标题+实体窗口 (ctx)、标题+银行∧金科同句±N窗 (ss) 三种文本物化口径下独立跑出的 LLM 情感判定, 因此 jf_coefficient_full/ctx/ss 三列是同一构念在三套不同文本暴露定义下的三个各自独立、just-identified 的并排测度, 彼此互为稳健性、不分主次, 严禁把三轨系数混入同一个 over-identified 的 Hansen J 检验 (会造成过度识别约束在构念上不成立)。ss 轨道遵循与 ctx 镜像的回退语义: 若某 bank-year 该轨道下不存在"银行∧金科同句共现"的文章, 则该文章级样本退回全文 body 兜底 (`ss_is_fallback=True`), 面板聚合时仍共享该轨道自身的 T (n_articles_llm_valid) 分母, 不借用 full 轨道的分母, 这一点与 CLAUDE.md「三轨文本架构」及「留篇门控=full-only」的口径完全一致: 一篇报道是否被认定为"银行金科报道"只由 full 轨道的 LLM 验证结果 (`llm_verified_full`) 决定, ctx/ss 是在该留篇集合子集上分轨计算的 conditional-on-full 稳健性测度, 因此三条 jf_coefficient 列共享同一个"是否入样本"的门, 但 P、N、T 本身各轨独立计数。

【文献定位】
本家族的方法学血统直接来自内容分析传统里对媒体报道净情感/极性的经典测度构造思路。Jegadeesh & Wu (2013, JFE) 在构造 "Word Power" 词权重情感测度时同样强调, 简单的正负词计数差不足以刻画信息含量, 需要对篇章内的方向一致性做进一步加权处理, 这与 J-F 系数用乘积项惩罚方向分裂的思路是同一方法论谱系下的不同实现路径。Manela & Moreira (2017, JFE) 在用新闻文本构造 "News-Implied Volatility" 时同样面临"净情感值掩盖舆论分裂程度"的问题, 说明极性集中度这一维度在金融文本挖掘文献中具有独立于净方向的信息含量, 这正是本家族相对于家族内其它简单净情感指标 (如 `_gated_log_sent` 所计算的 log1p(P)−log1p(N)) 的边际价值所在: 后者只反映方向与规模, 而 J-F 系数额外把"一致性/争议度"编码进同一个标量。Calomiris & Mamaysky (2019, JFE) 在构建跨国新闻文本风险测度时也指出, 报道文本的情感结构 (而非单纯正负计数) 对资产定价具有增量解释力, 为本家族在 bank-year 面板层面继续沿用这一分段非线性系数、而非退化为线性净值提供了方法论支持。三条轨道并排稳健性检验的设计精神, 与本项目「co-primary 双轨嵌入禁混同一 Hansen J」「LLM 三家/BERT 三模型互为稳健性」等已确立的梯子式稳健性架构一脉相承 — 各测度各自 just-identified, 通过在多篇论文的多组回归中反复出现来积累外部效度, 而非试图在单一过度识别系统内联合估计。 就该测度族在近年的存续与应用而言, Branzoli、Marchetti 与 Tarducci (2025) 构造了媒体报道的语调测度并将其应用于银行融资条件这一银行层级的实证问题, 是「新闻语调 → 银行层级结果」链条中与本家族应用域最贴近的近期实践; 但其语调测度并非 Janis-Fadner 式的分段二次系数, 语料为意大利语/英语新闻而非中文报道, 亦无 full/ctx/ss 三轨文本切分, 故只锚定应用域的同构性, 不背书本家族的公式与分母口径。Huynh 与 Nguyen (2026) 以 2000–2020 年 40 国企业样本发现企业媒体声誉与股票流动性正相关, 且在信息透明度低、可见度低的企业中更强, 并最终降低融资成本, 说明「把企业相关新闻的褒贬倾向聚合为单一实体层极性/声誉标量」这一构念在 2024 年后仍是活跃的研究对象、且承载可观测的经济后果; 惟可得摘要未披露其声誉指标的具体公式, 无法证实其采用 J-F 失衡系数, 故本文只锚定构念族的使用前沿, 不得据以主张 jf_coefficient 的公式本身在近年仍被沿用, 其实体为多国上市公司、DV 为股票流动性, 对本家族按 metric-audit 2026-06-10 把分母由 (P+N)² 改为 T²=n_articles_llm_valid² 以及逐轨分别计算这两项调整均无任何对应, 期刊层级亦非顶刊。Venčkauskas、Jusas 与 Barisas (2026) 构建了一条从新闻门户文章自动抽取、分类并聚合为企业媒体声誉分值的计算流水线, 与本家族「逐篇判正负 → 银行-年聚合为单一极性标量」的产线形态同族, 可作该测度族工程化实现在 2026 年的存在性锚; 但该文属计算/工程导向研究, 聚合函数为其自定义评分而非 Janis-Fadner 二次式, 语料为立陶宛语新闻门户, 既无经济学识别设计亦无银行样本, 不构成本家族公式的方法出处。
## VAR: jf_coefficient_ctx

【变体差分】
本列是 J-F 系数在 ctx (context) 轨道上的实现: 分子分母中的 P=pos_count_ctx、N=neg_count_ctx 均取自 stage 21 在"标题+目标银行实体窗口"文本 (`content_ctx`, 由 stage 14 `ctx_materializer` 物化, prepend_title 拼接) 上跑出的三家 LLM 多数投票情感判定, 而非全文。ctx 窗口聚焦于银行实体周边的局部语境, 相对 full 轨道剔除了同一篇报道中与该银行无关段落 (例如同版面其它公司新闻、行业综述性文字) 带来的情感稀释或噪声, 因此 ctx 轨道的 J-F 系数理论上应比 full 轨道对"该银行本身在该报道中的舆论集中/分裂程度"更聚焦。该列行使用者门控仍以 full 轨道的 `llm_verified_full` 留篇结果为准 (conditional-on-full), 即该行是否进入样本由 full 轨判定, 但 P、N 的取值、以及 T=n_articles_llm_valid_ctx=0 时的 NaN 缺失判定 (canonical 分母为 T² 而非 (P+N)²), 均严格在 ctx 轨道自身内部完成, 不借用 full 轨道分母。与 jf_coefficient_full、jf_coefficient_ss 相比, 本列不代表更优或更劣的测度, 三者是互为稳健性的并排轨道, 差异仅在文本暴露口径, 不应在同一识别策略里把 ctx 与其它轨道系数同时作为工具变量组用于同一个过度识别 Hansen J 检验。就统计行为而言, ctx 轨道的 P、N、T 计数一般不大于 full 轨道 (同一篇文章在 ctx 窗口下更可能被判为中性或未覆盖, 因窗口截断可能丢失原本支撑方向判定的上下文线索), 因此 ctx 轨道下 T=0 触发 NaN 的概率通常高于 full 轨道, 但低于 ss 轨道 (ss 的窗口更窄); 这一样本量梯度 (full ≥ ctx ≥ ss) 是三轨设计上的自然结果, 而非某一轨道优先失效。使用者在做稳健性汇报时应把 ctx 轨道的回归系数与 full、ss 并列展示, 而不是仅在 ctx 显著时才报告, 以避免选择性汇报造成的稳健性假象。

## VAR: jf_coefficient_full

【变体差分】
本列是 J-F 系数的 full (全文) 轨道实现, 也是家族内文本暴露口径最宽的 canonical 版本: P=pos_count_full、N=neg_count_full 取自 stage 21 在"标题+全文正文" (`content_full`) 上跑出的三家 LLM 多数投票情感判定, 覆盖该篇报道的全部文本信息而非局部实体窗口或同句窗口。由于 2026-06-29 起「留篇门控=full-only」的口径调整, 一篇报道是否被认定为有效的银行金科报道 (`llm_verified_full == True`) 完全由 full 轨道决定, 因此本列所依赖的 n_articles 分母同时也是 ctx/ss 两个 conditional-on-full 轨道所共享的行样本上界 (但 ctx/ss 各自内部分母仍取自身轨道的有效计数, 非借用 full 分母)。作为家族三轨中样本覆盖最完整、文本信息量最大的一支, full 轨道常被 P1 (`bank_fintech_tone`) 等下游论文选作情感类处理变量的首要参照点, 但这并不改变本家族内部"三轨并排、互为稳健性"的铁律 — full 轨道不因样本覆盖优势而获得 over-identified 系统内的特殊地位, 与 ctx、ss 轨道一样只能作为独立的 just-identified 稳健性检验之一使用。需要特别提醒的是, full 轨道的 P、N 计数以整篇报道 (含与目标银行无直接关系的段落) 为基础, 因此当一篇报道同时报道多家银行或涉及大量行业综述性文字时, full 轨道的情感判定有可能被目标银行以外的信息稀释或污染, 这正是 ctx/ss 两个更窄轨道存在的动机: 三者并非"从粗到细的层层过滤", 而是对"文本暴露应该多宽"这一构念争议给出的三种同等有效的操作化, 使用者应把三列同时纳入结果附录作为并排稳健性证据, 而非把 full 当作默认唯一口径、ctx/ss 仅作补充脚注。

## VAR: jf_coefficient_ss

【变体差分】
本列是 J-F 系数在 ss (同句) 轨道上的实现: P=pos_count_ss、N=neg_count_ss 取自 stage 21 在"标题+目标银行∧金科关键词同句 (或按 `config/filtering.yaml::context_window.ss_sentence_radius` 配置的 ±N 句窗, 默认半径为 1) 共现窗口"文本 (`content_ss`) 上跑出的三家 LLM 情感判定, 是三轨中文本暴露范围最窄、语境最贴近"银行与金科议题被同一句话直接关联"这一最严格共现判据的一支。当某篇报道不存在银行∧金科同句共现时, 该篇文章级样本按镜像 ctx 轨道的回退语义退回全文 body 兜底并标记 `ss_is_fallback=True`, 但仍计入 ss 轨道自身的 T=n_articles_llm_valid_ss 分母 (不借用 full 分母), 这与 ctx 轨道回退语义完全对称、仅共现判据的严格程度不同 (ss 要求同句, ctx 只要求实体窗口, 二者与 stage 13 硬过滤所用的 ±1 句窗口共现判据也是不同粒度的判据, 不可混淆)。由于文本窗口更窄, ss 轨道的 P、N、T 计数在稀疏样本 (如某银行某年金科相关报道本就很少) 下更容易出现 T=0 从而输出 NaN 缺失 (canonical 分母为 T² 而非 (P+N)², T=0 才是真正的缺失触发条件), 这是该轨道设计上固有的代价, 并非测量错误; 使用者在解读 jf_coefficient_ss 时应留意其相对 full/ctx 两轨样本量更小、方差更大, 三轨依旧互为稳健性并排、不设主次, 且不得混入同一 over-identified Hansen J 检验体系。正因为 ss 轨道判据最严 (要求银行与金科关键词字面同句共现, 而非仅同篇或同一实体窗口), 它对"报道确实在同一句话里把银行与金科议题绑定讨论"这一最强的相关性假设最不容易被无关段落污染, 在小样本 bank-year 单元上可作为对 full/ctx 两轨结论的严格性检验: 若某项发现仅在 full/ctx 显著而在 ss 轨道方向逆转或消失, 应在稳健性讨论中如实披露, 而非选择性隐去。

<!-- rendered-citations:begin -->
Calomiris, C. W., & Mamaysky, H. (2019). How news and its context drive risk and returns around the world. Journal of Financial Economics, 133(2), 299-336. https://doi.org/10.1016/j.jfineco.2018.11.009
Manela, A., & Moreira, A. (2017). News implied volatility and disaster concerns. Journal of Financial Economics, 123(1), 137-162. https://doi.org/10.1016/j.jfineco.2016.01.032
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
Huynh, T. H. H., & Nguyen, T. M. H. (2026). Signals in the news: How media reputation improves stock liquidity around the world. Asia and the Global Economy, 6(1), 100139. https://doi.org/10.1016/j.aglobe.2026.100139
Venčkauskas, A., Jusas, V., & Barisas, D. (2026). Evaluation of a Company’s Media Reputation Based on the Articles Published on News Portals. Applied Sciences, 16(4), 1987. https://doi.org/10.3390/app16041987
<!-- rendered-citations:end -->
