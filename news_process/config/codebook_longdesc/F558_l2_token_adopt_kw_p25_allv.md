---
family_id: F558
columns:
- token_adopt_kw_p25_allv
- token_adopt_kw_p25_allv_ctx
- token_adopt_kw_p25_allv_ss
unit: 比例 (0–1 区间; 银行-年内落入 Token 象限的文章占已测量文章之比)
formula: '逐篇: high_freq_i = 1[freq_i ≥ 年度p25分位数(freq)]; high_sim_i = 1[sim_i ≥ 年度p25分位数(sim)]; token_i = high_freq_i ∧ ¬high_sim_i (仅当 sim_i、freq_i 双双非缺失时定义, 否则 NaN); bank-year 值 = mean(token_i), 分母 = 该年已测量 (sim/freq 均非 NaN) 且落在 verified 域 (24_herd_decay semi-join) 的文章数'
producer: pipeline/panel/runner.py::_classify_policy_quadrants (步骤7h 四象限政策对齐块调用)
upstream:
- policy_cosine_sim_allv (stage 16 article_policy_alignment 全语料静态锚点变体)
- fintech_distinct_keywords (stage 12 news_fintech AC 去重关键词计数, track-agnostic 元数据)
- 24_herd_decay (verified 域 semi-join)
citations:
- doi: "10.1017/S0022109023000662"
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: Journal of Financial and Quantitative Analysis
  vol: "59"
  issue: "6"
  pages_or_artno: 2618-2646
- doi: "10.1086/730053"
  type: journal
  authors: Fan, H., Liu, Y., Qian, N., & Wen, J.
  year: 2024
  title: "Technological adoption and taxation: The case of China's Golden Tax reform"
  venue: Tax Policy and the Economy
  vol: "38"
  pages_or_artno: 101-122
- doi: "10.1080/09296171003643098"
  type: journal
  authors: Covington, M. A., & McFall, J. D.
  year: 2010
  title: "Cutting the Gordian knot: The moving-average type-token ratio (MATTR)"
  venue: Journal of Quantitative Linguistics
  vol: "17"
  issue: "2"
  pages_or_artno: 94-100
- doi: "10.1016/j.rmal.2024.100168"
  type: journal
  authors: Bestgen, Y.
  year: 2025
  title: "Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons"
  venue: Research Methods in Applied Linguistics
  vol: "4"
  issue: "1"
  pages_or_artno: "100168"
- doi: "10.1103/rxxz-lk3n"
  type: journal
  authors: Rosillo-Rodes, P., San Miguel, M., & Sánchez, D.
  year: 2025
  title: "Entropy and type-token ratio in gigaword corpora"
  venue: Physical Review Research
  vol: "7"
  issue: "3"
  pages_or_artno: "033054"
new_dois: []
---

## CORE

【构念与来源】
本家族 3 列同属"政策对齐四象限"测度族中的 Token (符号化/象征性科技采纳) 象限占比, 生产于 `pipeline/panel/runner.py` 步骤7h 网络族区块内的 `_classify_policy_quadrants` 函数, 上游消费 stage 16 `article_policy_alignment` 产出的政策语义相似度 (`policy_cosine_sim*`) 与 stage 12 `news_fintech` 产出的金科关键词计数 (`fintech_distinct_keywords*`)。四象限逻辑同时物化 token/hidden/subst 三支 (`token_adopt_*`/`hidden_adopt_*`/`subst_adopt_*`), 本家族只承载 token 支; 三支互斥但不穷尽 (低词频且低相似度的第四象限——"无采纳基线"——刻意不物化为独立列, 因其在构念上等价于"既不谈也不做", 不构成本研究关心的采纳类型)。构念含义: 一篇报道若在金科关键词出现频次上处于年度高位 (freq ≥ 年度 p25 分位), 但其文本与政策语义锚点的余弦相似度却处于年度低位 (sim < 年度 p25 分位), 则被归为 Token——即"高谈阔论金科词汇, 但内容与官方政策语义脱耦"的报道; 这与组织理论中"象征性/仪式性采纳" (symbolic or ceremonial adoption, 亦称脱耦 decoupling) 的经典区分一致: 表面话语上的采纳信号与实质政策内容对齐度可以分离度量, 二者并非同一件事。`kw` 词频轨指该分类使用的词频列是关键词计数 (`fintech_distinct_keywords`, 与 `int`=`fintech_intensity_score` 强度轨并列, 本家族外的姊妹族); `p25` 指年度分位阈值取第 25 百分位 (家族内固定, 未做梯子扫描); `allv` 指相似度锚点采用全语料静态锚点变体 `policy_cosine_sim_allv` (与逐年 vintage 主轨 `policy_cosine_sim` 并排的姊妹族, 详见 F3/policy_cosine_sim 家族), 二者互为稳健性、不分主次, 均遵循「各自 just-identified 并排、禁混进同一 over-identified Hansen J」的口径铁律。

【方法学与计算】
`_classify_policy_quadrants(df_align, sim_col, freq_col, pct)` 对每年 (`groupby('year')`) 分别对 `sim_col`、`freq_col` 取 `quantile(pct/100)` 作为该年阈值 (`transform`, 逐行广播回原表), 再逐篇布尔判定 `high_freq = freq ≥ 年度阈值`、`high_sim = sim ≥ 年度阈值`, `token = high_freq & ~high_sim`。2026-06-11 的 fix(omni-g-runner-03/g-runner-11) 修正了一处历史缺陷: 旧实现在 `sim`/`freq` 缺失 (`NaN`) 时把 `NaN >= thresh` 隐式当作 `False`, 导致 stage 15 三条优雅早退路径写出的全 `NaN` `policy_cosine_sim` 会让全部高词频文章被误判为 Token (零测量被静默伪造成非缺失的面板值)。修正后先算 `measured = sim.notna() & freq.notna()` 掩码, 用 `.where(measured)` 把未测量行显式置 `NaN`, 使 `groupby(...).mean()` 聚合到 bank-year 时自动跳过未测量文章——占比分母是"该年已测量的文章数"而非全部文章数, 与本项目"无数据=未测量(NaN), 而非伪零"的既定契约一致 (同一契约亦见于 `_gated_log_sent`、`jf_coefficient`、`concern_score` 等姊妹测度)。聚合前还先经 `_filter_to_verified_universe` 做 semi-join 过滤 (与 stage 24 `herd_decay` 交集), 确保象限占比只在"已通过留篇门控 (full-only, 2026-06-29)"的文章域上计算——ctx/ss 两轨同样承接 full 轨确定的行宇宙, 不各自独立留篇。年度分位阈值随年份浮动 (每年各自取该年内的 p25), 因此该占比刻画的是银行相对同年同业的"符号化采纳倾向"排位, 而非绝对词频/相似度水平的跨年可比刻度; 分位阈值取 p25 (而非中位数 p50) 意味着"高词频"门槛相对宽松、"低相似度"门槛也相对宽松, 该占比因而对处于分布中段的报道较敏感。

【文献定位】
该测度所刻画的"话语层面的科技采纳信号与政策实质内容脱耦"这一构念, 呼应银行数字化能力测度与危机压力情境下真实 vs. 表面数字化程度之辨析——Kwan et al. (2024, *Journal of Financial and Quantitative Analysis*) 在压力测试银行数字化能力时同样强调, 仅凭话语或投入规模无法准确反映实质数字化能力, 需要构造能区分"名义投入"与"实际能力"的度量, 这与本测度用双重分位阈值分离"词频高企"与"语义对齐"的思路一脉相承。技术采纳的度量本身在实证文献中也需谨慎处理测量误差与异质性, Fan et al. (2024, *Tax Policy and the Economy*) 在研究金税改革驱动的技术采纳时同样面对"报告/申报行为"与"实质技术使用"的分离问题, 为本测度将"提及"与"对齐"拆分为两个独立可测维度提供了方法论上的平行参照。`kw` 词频轨的构造 (对每篇文章统计 AC 自动机去重命中的金科关键词类型数, 即 distinct keyword count, 本质是一个"类型计数"而非"标记计数") 在方法论谱系上与语料语言学中的型例比 (type-token ratio, TTR) 及其改进指标一脉相承: Covington & McFall (2010) 提出移动平均型例比 (MATTR) 以修正长度依赖偏误, Bestgen (2025) 对 MATTR 的优劣做了系统评估, Rosillo-Rodes et al. (2025) 则在千兆词语料上用熵与型例比联合刻画词汇多样性——三者共同的方法论要点 (基于窗口/分位的相对阈值优于绝对计数阈值, 以规避语料规模/长度对计数型指标的机械偏误) 支持了本测度选择"年度分位数"而非"绝对词数阈值"作为高/低词频判据的设计取舍。

## VAR: token_adopt_kw_p25_allv

【变体差分】
本列是家族 canonical 全文 (full) 轨: 相似度输入固定为 `policy_cosine_sim_allv` (全语料静态锚点, 不随年度 vintage 滚动), 词频输入固定为 `fintech_distinct_keywords` (stage 12 `news_fintech` 产出的金科关键词去重计数, 该列本身是 track-agnostic 元数据——AC 自动机在全文正文上一次性扫描去重关键词类型, 没有 ctx/ss 专属变体, 三支轨道均复用同一份 full 词频输入, 仅相似度输入随轨道切换)。计算时先按年度分别对 `policy_cosine_sim_allv`、`fintech_distinct_keywords` 取 p25 分位阈值, 再判定 `token_i = 1[freq_i ≥ p25(freq)] ∧ ¬1[sim_i ≥ p25(sim)]`, 仅在 sim/freq 双双非缺失时有定义; bank-year 聚合为该年已测量、已过 verified 域 semi-join 的文章中 token 指示的均值。作为家族内唯一的 full 轨, 该列是三轨对照中的默认基准, 与 `_ctx`、`_ss` 两个姊妹列互为稳健性并排、不分主次, 三者共同遵循「禁混进同一 over-identified Hansen J」的口径铁律——下游模型不应把三轨同时塞进同一方程做联合识别, 而应分别单独进入回归、以三次并排结果检验结论对文本窗口选择的稳健性。全语料静态锚点 (`_allv` 后缀) 与逐年滚动锚点 (无 `_allv` 后缀的姊妹家族) 之间同样是并排稳健性关系而非替代关系: 前者用固定的全期语料中心衡量政策语义漂移是否随时间改变了银行的相对定位, 后者用逐年滚动锚点吸收政策话语本身的年度漂移, 两者对"政策相似度是否真高/真低"给出两套互补但同样有效的判断基准。

## VAR: token_adopt_kw_p25_allv_ctx

【变体差分】
本列是家族 ctx (实体窗口) 轨: 相似度输入切换为 `policy_cosine_sim_allv_ctx` (stage 16 在标题+银行/金科实体窗口文本上计算的政策相似度, 而非全文), 词频输入优先取同轨变体 `fintech_distinct_keywords_ctx` (若该列存在于 `df_align`); 因 `fintech_distinct_keywords` 在当前 schema 下是 track-agnostic 元数据 (AC 关键词扫描本就覆盖全文, 未按 ctx 窗口单独重算), 实际生产中该列不存在时, 运行时代码优雅回退复用 full 轨的 `fintech_distinct_keywords`——即词频侧退化为与 full 列相同的输入, 只有相似度侧真正切轨。这一"词频侧可能复用 full、相似度侧切轨"的非对称设计在 producer 注释中被明确披露 (2026-06-11 fix(omni-g-runner-07)), 写手在解读本列与 canonical 列的差异时不应默认两侧输入都已切轨——差异的确定性来源永远是相似度输入 `_ctx` 后缀, 词频输入是否切轨需视盘上 schema 而定。ctx 轨的构念含义是: 在把文本窗口收窄到银行与金科实体附近的语境后, "话语提及与政策语义脱耦"的判定是否依然成立——若某银行只在 ctx 窗口 (证据密度更高的局部语境) 仍被归为 Token, 则该脱耦信号比仅在全文粗粒度下观察到的更可信。本列与 canonical `token_adopt_kw_p25_allv`、姊妹列 `_ss` 三者各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 联合估计; 与三轨文本架构的一般口径一致 (full/ctx/ss 分列不合并), 留篇门控仍以 full 轨的 `llm_verified_full` 为行宇宙锚点, ctx 轨不独立筛选行。

## VAR: token_adopt_kw_p25_allv_ss

【变体差分】
本列是家族 ss (银行∧金科同句) 轨: 相似度输入切换为 `policy_cosine_sim_allv_ss` (stage 16 在"银行与金科关键词同句共现 (默认 ±1 句半径)"窗口文本上计算的政策相似度), 词频输入同样优先取同轨变体 `fintech_distinct_keywords_ss` (若存在), 不存在则回退复用 full 轨 `fintech_distinct_keywords`——回退逻辑与 `_ctx` 列完全对称。`_ss` 轨的语境窗口比 `_ctx` 更严格 (要求银行实体与金科关键词落在同一句而非同一实体窗口内), 因此其"未共现回退"语义严格镜像 `_ctx`: 当某篇文章不存在银行∧金科同句共现时, 该篇的 `content_ss` 在 stage 14 物化阶段已回退为全文 body (`ss_is_fallback=True`), 本列的相似度输入 `policy_cosine_sim_allv_ss` 相应地也是在这份回退后的文本上计算, 而非因未共现而缺失——即回退不产生额外缺失, 只是退化为与 full 轨近似的宽口径文本。构念上, ss 轨的 Token 判定是三轨中语境最紧的一档: 若在银行与金科词严格同句共现的最窄语境下仍判定为高词频低相似度, 该脱耦信号的语境噪声最小、可信度最高, 但样本量 (同句共现命中率) 也最小, 与 `_ctx`、full 轨相比更容易出现年度分位数在稀疏数据上不稳定的问题。本列同样与 canonical 列、`_ctx` 列三支并排、互为稳健性不分主次, 遵循禁止混入同一 over-identified Hansen J 的口径铁律, 下游使用须以三轨并列稳健性检验的方式呈现, 而非把三者当作可相互替代或可加总的单一测度。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Fan, H., Liu, Y., Qian, N., & Wen, J. (2024). Technological adoption and taxation: The case of China's Golden Tax reform. Tax Policy and the Economy, 38, 101-122. https://doi.org/10.1086/730053
Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type-token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94-100. https://doi.org/10.1080/09296171003643098
Bestgen, Y. (2025). Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons. Research Methods in Applied Linguistics, 4(1), 100168. https://doi.org/10.1016/j.rmal.2024.100168
Rosillo-Rodes, P., San Miguel, M., & Sánchez, D. (2025). Entropy and type-token ratio in gigaword corpora. Physical Review Research, 7(3), 033054. https://doi.org/10.1103/rxxz-lk3n
<!-- rendered-citations:end -->
