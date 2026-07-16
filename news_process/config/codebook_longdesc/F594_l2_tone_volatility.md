---
family_id: F594
columns:
- tone_volatility_ctx
- tone_volatility_full
- tone_volatility_ss
unit: "语调标准差 (逐年滚动, 与 llm_vote_tone 同尺度; 理论值域 [0, +∞), 因底层语调有界 [-1,1] 实际上界随窗口内有效观测数 n 而变: min_periods=2 允许 n=2 时可达约 1.414 (两点序列如 [-1,1] 的样本 SD), n=3 时上界降为约 1.155; 银行进入面板早期 (窗口内仅 2 个观测) 更易触及 1.414 一侧的上界)"
formula: 'panel.sort_values([target_bank, year]) 后, 按 target_bank 分组对 llm_vote_tone{track} 做
  rolling(window=3, min_periods=2).std() (pandas 默认 ddof=1), 结果对齐回原索引; 首年 (该银行仅 1 个观测) 恒 NaN,
  第 2 年起若窗口内 ≥2 个非缺观测即出值'
producer: pipeline\panel\runner.py (第 i2 步, TONE_VOL_WINDOW=3/TONE_VOL_MINP=2) ; pipeline\panel\codebook.py
  (_DUAL_TEXT_SPECS 统一元数据入口) ; pipeline\panel\export.py (dta 标签)
upstream:
- llm_vote_tone_full
- llm_vote_tone_ctx
- llm_vote_tone_ss
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1093/rfs/hhu072
  type: journal
  authors: Da, Z., Engelberg, J., & Gao, P.
  year: 2015
  title: The Sum of All FEARS Investor Sentiment and Asset Prices
  venue: The Review of Financial Studies
  vol: '28'
  issue: '1'
  pages_or_artno: 1-32
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: Measuring News Sentiment
  venue: Journal of Econometrics
  vol: '228'
  issue: '2'
  pages_or_artno: 221-243
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from
    China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1002/jae.3095
  type: journal
  authors: Bodilsen, S. T., & Lunde, A.
  year: 2025
  title: Exploiting News Analytics for Volatility Forecasting
  venue: Journal of Applied Econometrics
  vol: '40'
  issue: '1'
  pages_or_artno: 18-36
new_dois: []
---

## CORE

【构念与来源】
tone_volatility 测的不是"银行这一年报道语调是正是负", 而是"这家银行的媒体语调在跨年时间轴上抖不抖" — 一家银行如果去年舆论热捧、今年舆论翻脸、明年又回暖, 即便三年均值看起来平稳, 也该被识别为"语调不稳定"; 另一家银行则可能三年语调持续温和正向, 均值相近但完全没有这种跳跃。这是一个时间维的二阶矩测度, 与"同一年内不同文章之间语调有多分散"(年内跨篇 SD, 如各 BERT/LLM 模型的 `_pos_std`/`net_tone` 系列离散度)、与"语调一阶变化方向"(`tone_reversal` = 本年语调减上一年语调)是三个刻意区分、互不替代的构念: 后两者一个是横截面(同年内)离散度, 一个是相邻两期的带符号一阶差分, 而 tone_volatility 是滚动窗口内的无符号波动幅度, 捕捉的是"这家银行舆论环境是否处于高频反复"这一时间序列性质, 论文正文须明写三者的正交关系以防被审稿人质疑重复测量同一构念。

设计动机直接承袭行为金融学对投资者情绪"过度反应—均值回归"假说的关注: De Bondt & Thaler (1985) 提出极端情感/极端表现后往往伴随反转, `tone_reversal` 是这一假说在一阶差分层面的对应物; tone_volatility 则是对"反转有多剧烈、多频繁"做进一步的二阶矩补全 — 一家银行如果反复经历"捧杀—棒杀"式的舆论摆动, 其一阶反转量可能正负相互抵消而在均值上不可见, 但 tone_volatility 会捕捉到这种波动本身。Tetlock (2007) 与 Da, Engelberg & Gao (2015) 均确立了媒体语调/投资者情绪的时间序列结构对资产价格与交易行为具有独立解释力, 而不仅是横截面语调水平; Shapiro, Sudhof & Wilson (2022) 在构建新闻情绪指数时同样强调需要区分情绪水平与情绪的时间波动两个维度; Bodilsen & Lunde (2025) 进一步在新闻分析情绪与已实现波动率预测之间建立了直接的方法学桥梁, 支持"文本语调序列的二阶矩本身携带经济信息, 而非纯噪声"这一前提。Fang, Wang, Wang & Yuan (2024) 在中国银行业媒体情感与系统性风险的研究中提供了同一研究对象 (中国银行样本、媒体语调) 下的直接对照, 说明语调的不稳定性与银行的存款稳定性/系统性风险敞口相关联, 为 tone_volatility 作为银行层面稳健性/风险代理变量提供了实证先例。

【方法学与计算】
底层输入是 stage 21 三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票共识语调 `llm_vote_tone{track}` (面板层聚合列, 已由 bank-year 篇级语调均值构成), 而非再重新读取文章级语调。计算按 `target_bank` 分组、按 `year` 排序后, 对该银行的语调时间序列施加窗口宽度 3、`min_periods=2` 的滚动标准差 (pandas 默认 ddof=1 的样本标准差), 即每个 bank-year 观测点用"自身及此前至多 2 年"(共至多 3 期) 的语调值算样本 SD; 银行进入面板的第一年因窗口内只有 1 个观测, 标准差在数学上无定义, 故恒为 NaN, 是预期缺失而非数据故障。窗口宽度取 3 是研究者对"平滑到能反映持续性、又不过度拉长导致早期观测被稀释"之间的折中选择, 未做超参数梯子——这与本项目其余"消融/权重/判据"梯子(词典规则消融、政治词权重、罕见词频次 cutoff 等)不同, tone_volatility 不设窗口宽度稳健性变体, 仅在三个文本轨道 (full/ctx/ss) 维度上并排稳健。

三个轨道对应的正是三条独立的语调时间序列: full 轨基于标题+全文正文的语调判定, ctx 轨基于标题+目标银行实体窗口的语调判定, ss 轨基于标题+银行与金科词同句±N窗的语调判定; 三条序列独立滚动、独立产出 tone_volatility, 三列各自 just-identified 并排, 互为稳健性、不分主次, 严禁在同一 over-identified 的 Hansen J 检验中把三轨波动率一并塞入(镜像项目对三轨文本、co-primary 双轨嵌入、各梯子测度的一贯铁律)。留篇门控口径遵循 2026-06-29 起生效的 full-only 铁律: 一篇报道是否被判定为"银行—金科"相关报道, 唯一依据是 `llm_verified_full==True`, ctx/ss 两轨降格为"条件于 full 留篇集的" robustness 轨, 其 `llm_vote_tone_ctx`/`llm_vote_tone_ss` 的行宇宙是 full 留篇集的子集; 这意味着 tone_volatility_ctx/_ss 的滚动窗口所消费的年度语调序列, 其样本已隐含继承了 full 轨的留篇边界, 不能被误读为"ctx/ss 各自独立圈定的更宽或更窄的样本"。ss 轨若某年内该银行与金科词从未在同一句/同一窗口内共现, 其对应年度的 `llm_vote_tone_ss` 依回退语义(镜像 ctx: 无共现则用全文正文兜底并标记 `ss_is_fallback=True`)取值, 进而参与 tone_volatility_ss 的滚动计算; 三轨底层语调若整年缺失 (如 `FINTECH_AC=None` 导致的优雅降级全 True), 对应年份的滚动 SD 计算按缺失值处理, 窗口内有效观测不足 2 个时仍输出 NaN。

【文献定位】
Tetlock (2007) 首次系统证明媒体语调时间序列(而非单期水平)对股票市场收益与交易量具有可预测的滞后效应, 是本项目在 `tone_reversal` 与 tone_volatility 两处都反复引用的方法学与理论双重出处; Da, Engelberg & Gao (2015) 把这一逻辑推进到情绪指数的时间序列结构(FEARS 指数)与资产价格短期反转/长期修正的关系, 强化了"情感序列的波动性本身即信息"这一定位。Shapiro, Sudhof & Wilson (2022) 与 Bodilsen & Lunde (2025) 代表更晚近的文本情绪计量方法学进展, 前者建立起可复制的新闻情绪测度框架并区分水平与波动两条测度线, 后者直接把新闻分析情绪序列接入已实现波动率预测模型, 为本项目"语调时间序列的二阶矩具有独立解释力"的前提提供跨市场佐证。Fang, Wang, Wang & Yuan (2024) 则是与本项目高度可比的中国银行业实证先例, 采用媒体情感度量银行系统性风险敞口, 为 tone_volatility 未来接入 outcome 变量(如资金成本、存款稳定性)时的解释框架提供直接文献锚点。

## VAR: tone_volatility_ctx

【变体差分】
本列以 `llm_vote_tone_ctx` (标题+目标银行实体窗口轨语调) 作为滚动波动率的输入序列, 与 canonical 的 full 轨、另一个 ss 轨各自独立计算, 互不借用彼此的时间序列或滚动结果; 三者是"互为稳健性、不分主次"的并排关系, 而非以 full 为主、ctx 为辅的层级关系。计算细节 (窗口=3, min_periods=2, 按 target_bank 分组滚动, 样本标准差 ddof=1) 与 full/ss 完全一致, 唯一差异是输入的语调序列来源轨道。

由于 2026-06-29 起生效的 full-only 留篇门控铁律, ctx 轨语调 `llm_vote_tone_ctx` 的行宇宙是 full 轨留篇集的子集 (即某篇报道只有在 `llm_verified_full==True` 时才会被纳入统计, ctx 轨自身不再独立圈定文章样本), 这意味着 tone_volatility_ctx 所消费的年度语调均值, 其样本边界继承自 full 轨判定, ctx 轨本身只决定"用哪段文本窗口去读取语调", 不再决定"这篇文章算不算数"。这一点在解释 tone_volatility_ctx 与 tone_volatility_full 差异时尤为关键: 两者的样本行数理论上应当一致(因为都在同一留篇集上计算), 差异纯粹来自"读全文语调"与"读实体窗口语调"这两种测量口径本身的语调判定分歧, 而非样本选择差异。ctx 轨作为实体窗口测度, 理论上比全文轨对无关段落(如同一篇报道里提及其他银行或宏观背景的部分)更聚焦, 若这些无关段落本身携带独立的语调噪声, ctx 轨波动率可能表现出与 full 轨不同的抖动模式, 二者的并列比较可用于判断银行层面语调时间序列的不稳定性是源于该银行本身相关内容的真实语调摆动、还是源于全文语境中无关信息的噪声混入。回归实践中若同时纳入 full/ctx 两轨 tone_volatility 作为解释变量或控制变量, 须遵守本项目"三轨禁混同一 over-identified Hansen J"的铁律, 分别单独识别、单独报告, 不得将其构造为单一工具变量集合联合检验。

## VAR: tone_volatility_full

【变体差分】
本列是家族的 canonical 主轨, 输入序列为 `llm_vote_tone_full` (标题+全文正文轨的三家 LLM 多数投票共识语调), 是 stage 21 情感 LLM 处理链路中留篇门控 (full-only, 2026-06-29 起生效) 直接依赖的主测度轨道, 也是 P1 论文 `bank_fintech_tone` 处理变量 `llm_vote_tone_full` 的时间序列二阶矩对应物。计算口径同家族其余两列: 按 `target_bank` 分组、按年份排序, 窗口宽度 3、`min_periods=2` 的滚动样本标准差, 首年恒 NaN。

作为 full-only 门控体系下唯一"自主圈定留篇集"的轨道, tone_volatility_full 所依赖的年度语调序列样本边界不依赖任何其他轨道, 是三列中样本口径最"干净"、最少歧义的一支, 也因此在稳健性讨论中通常作为默认展示或首要讨论对象——但这只是叙事习惯上的便利, 并不意味着在计量识别层面 full 轨对 ctx/ss 轨具有统计优先权; 三轨仍应各自 just-identified 并排报告, 不应把 full 轨波动率单独作为"真值"而把 ctx/ss 轨波动率仅作陪衬式脚注。tone_volatility_full 与同名的 `abnormal_tone_full`(语调对银行基本面回归后的残差, 目前因缺财务基本面列而处于 dormant 状态)、`tone_reversal_full`(一阶反转)在概念谱系上构成互补三件套: 反转测一阶方向变化, 波动率测无向的抖动幅度, 残差语调测剔除基本面可解释部分后的"异常"水平, 三者理论上互不冗余但均来自同一 `llm_vote_tone_full` 母序列, 论文行文中若三者并用于同一回归须逐一说明各自的正交性依据, 避免被解读为同一信号的三次重复计量。

## VAR: tone_volatility_ss

【变体差分】
本列以 `llm_vote_tone_ss` (标题+银行∧金科词同句/±N窗轨语调) 为滚动波动率输入, ss 轨的判定原语比 ctx 轨更严格——ctx 是"实体窗口"级邻近, ss 要求银行实体与金科词汇在同一句 (或配置的 `context_window.ss_sentence_radius` 窗口, 与 stage 13 硬过滤的 `cooccurrence_filter.sentence_radius` 是两个刻意区分、互不混用的独立配置键) 内共现才判定为"真正命中"。ss 轨的回退语义镜像 ctx: 一旦该银行某年内某篇文章不存在银行∧金科同句共现, 该篇文章的 `content_ss` 退化为全文 body、`ss_is_fallback` 标记为 True 并共享 `n_articles` 分母, 语调判定依旧照常进行, 只是所读文本窗口退化为全文; 若 `FINTECH_AC=None`(金科词典缺失), 全部 `*_is_fallback` 优雅降级为 True。这意味着 tone_volatility_ss 的年度输入序列, 在共现稀疏的银行—年份格上, 实质上会与 full 轨高度趋同(因为回退后读的就是全文), 而在共现丰富的格上则真正体现"同句上下文"这一更收紧口径下的语调判定, 二者混合导致 ss 轨波动率的解释需要结合该银行—年度的共现覆盖率一并考量, 不能脱离覆盖率单独解释波动幅度大小。

与 ctx 轨相同, ss 轨的行宇宙同样是 full 轨留篇集的子集 (full-only 门控铁律), ss 轨本身不再独立决定"这篇文章是否算数", 只决定"读哪段文本判语调"。ss 是三轨中口径最收紧、最容易受回退语义稀释的一支, 在样本覆盖稀疏的银行 (如报道量小、金科相关性弱的银行) 或本项目当前磁盘态 T=2 开发样本上, ss 轨语调序列可能因回退比例过高而与 full 轨高度共线, 此时 tone_volatility_ss 与 tone_volatility_full 的差异信息量会明显收窄, 这是预期的退化行为而非产出缺陷; 在生产级 T=19、报道覆盖充分的样本上, ss 轨的收紧判据才能真正发挥其相对 ctx/full 轨更精细的语境甄别价值。计算参数(窗口=3, min_periods=2, 按 target_bank 分组, ddof=1 样本 SD)与另外两列完全一致, 三轨并排、互为稳健性、禁止混入同一 over-identified Hansen J 的铁律同样适用于本列。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Da, Z., Engelberg, J., & Gao, P. (2015). The Sum of All FEARS Investor Sentiment and Asset Prices. The Review of Financial Studies, 28(1), 1-32. https://doi.org/10.1093/rfs/hhu072
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring News Sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Bodilsen, S. T., & Lunde, A. (2025). Exploiting News Analytics for Volatility Forecasting. Journal of Applied Econometrics, 40(1), 18-36. https://doi.org/10.1002/jae.3095
<!-- rendered-citations:end -->
