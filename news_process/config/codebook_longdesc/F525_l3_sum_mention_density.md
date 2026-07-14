---
family_id: F525
columns:
- sum_mention_density
unit: 银行-年度加总的提及密度 (无量纲, 词频/字符数之比的年度求和)
formula: 'sum_mention_density = Σ_{article ∈ bank-year} mention_density_article, 其中 mention_density_article = target_bank_mention_count / max(len(str(内容)), 1)'
producer: pipeline\filtering\news_bank.py ; pipeline\panel\encode.py
upstream:
- mention_density
- target_bank_mention_count
- doc_length
citations:
- doi: 10.1007/s11187-024-00910-6
  type: journal
  authors: Gama, P. M., Sol Murta, F., & Vieira, E. S.
  year: 2024
  title: Local banking development and SME conservative financing policy. Does bank branch density matter?
  venue: Small Business Economics
  vol: '63'
  issue: '4'
  pages_or_artno: 1747-1765
- doi: 10.1016/j.jbankfin.2024.107356
  type: journal
  authors: Ge, S., Li, S., & Zheng, H.
  year: 2025
  title: 'Diamond cuts diamond: News co-mention momentum spillover prevails in China'
  venue: Journal of Banking and Finance
  vol: '171'
  pages_or_artno: '107356'
- doi: 10.3386/w31462
  type: wp
  authors: Benmelech, E., Yang, J., & Zator, M.
  year: 2023
  title: Bank Branch Density and Bank Runs
  venue: National Bureau of Economic Research Working Paper
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-Level Political Risk: Measurement and Effects"
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
new_dois: []
---

## CORE

【构念与来源】
sum_mention_density 是银行-年度面板层面的一个 value-weighted (以下简称 VW) 辅助测度, 刻画某银行在某年度全部合格报道中被提及的"密度"总量, 与仅计文章篇数的 count-weighted 口径 (如 n_articles) 形成互补。它的血缘上游是文章级列 mention_density, 该列由 pipeline\filtering\news_bank.py 在 stage 11 (银行新闻识别) 阶段产出: 对每篇被判定为"银行新闻"的文章-银行配对, mention_density = target_bank_mention_count / max(len(str(内容)), 1), 即该银行全部别名在标题+正文中的命中次数, 除以正文字符数 (以 1 为下限防零除)。这是一个 within-article 归一化的强度指标 — 同样提及 3 次, 在 500 字短讯里的密度远高于 5000 字长篇报道, 后者更可能只是背景提及而非核心议题。sum_mention_density 则是 pipeline\panel\encode.py 在 stage 40 面板聚合阶段, 对同一银行-年度全部合格文章的 mention_density 做 groupby('sum') 求和, 归入代码注释所称"F. Value-weighted 辅助列"分组, 与同批产出的 sum_doc_length (正文长度年度加总)、avg_doc_length (正文长度年度均值)、sum_target_mentions (提及次数年度加总) 并列构成一套"篇幅-强度"辅助测度族。

【方法学与计算】
计算链路分两段。第一段在文章级 (stage 11 news_bank): 一篇文章可同时命中多家银行, 每家合格银行独立展开为一条物理行 (firm-document expansion, 输出行数可多于输入行数), 每行携带该银行专属的 target_bank_mention_count 与共享的 doc_length, 二者相除得到该银行在该篇文章中的 mention_density。判定"合格"(is_bank_news=True) 的前置条件与 stage 11 家族共享: 全文+标题别名总命中 ≥ MIN_NAME_OCCURRENCES (默认 2), 且满足上下半文分布条件之一 (上半 ≥ MIN_UPPER 且下半 ≥ MIN_LOWER; 或标题命中且全文合计达标), 并经否定模式 (NEGATION_AC, 如"务农行列"误配"农行") 与短名歧义消解 (≤2 字简称按上下文窗口排除) 双重假阳性过滤; 匹配引擎是全局 Aho-Corasick 自动机, 一次线性扫描完成全部银行别名匹配, 复杂度 O(文本长度)。第二段在面板级 (stage 40 encode): 以银行-年度为聚合单元, 对该单元下全部合格文章的 mention_density 逐条累加 (pandas groupby.agg 的 'sum' 命名聚合), 得到 sum_mention_density。这一"先归一化再求和"的两段式设计, 使得该列既保留了单篇文章内部的强度信号 (避免长文因绝对词频高而机械压过短文), 又通过年度加总把强度信号累积为一个可比的银行-年度暴露量, 天然对篇幅分布不同的银行样本更具可比性 — 这正是与仅用绝对提及次数加总 (sum_target_mentions) 或篇均密度 (若存在) 相区别之处: sum_mention_density 是"密度的总量", 兼具"多篇高强度报道"与"单篇高强度长期占据版面"两类暴露模式的敏感性, 而非二者中任一单独测度。该列的分母字符数计数以原始 Python str 长度为准 (未做分词或去标点归一), 因此对不同排版风格 (如大量数字、引号、空白字符) 的文章存在轻微的量纲噪声, 使用者在做跨来源比较时应留意这一点; 该噪声在同一新闻来源内部相对稳定, 不构成系统性偏误。

【文献定位】
本测度真正的方法论血统, 是源码注释显式标注的 value-weighted exposure 框架: pipeline\filtering\news_bank.py 在提及密度计算处的注释与 pipeline\panel\encode.py 在该列所属"F. Value-weighted 辅助列"分组处的注释, 均将其方法论谱系直接归给 Hassan et al. (2019, Quarterly Journal of Economics) 提出的"以文本命中频次归一化构造企业/机构层面风险与关注度暴露"这一设计范式, 以及 Sautner et al. (2023, Journal of Finance) 在气候变化文本暴露测度上对同一框架的延伸应用。这两篇文献才是"归一化文本命中→暴露强度"这一构念最直接的方法论源头; 其中 Hassan et al. (2019) 经核验确属项目 874-DOI 主白名单收录文献, 已正式列入本家族 citations (QJE 顶刊锚), 印证以文本命中频次归一化构造企业/机构层面暴露强度这一设计范式的方法学正当性; Sautner et al. (2023) 因不在本家族当前引文候选池 (citations_pool.md) 的白名单范围内, 未收录为结构化 citations 条目, 此处仅据源码注释如实标注其血统, 不作为可核验引注呈现。本节实际引用的三篇文献服务的是一个更外围但仍然相关的目的——为"归一化强度指标优于绝对计数"这一一般性方法论选择提供跨领域佐证, 使用者应留意其构念差异: Gama, Sol Murta & Vieira (2024, Small Business Economics) 与 Benmelech, Yang & Zator (2023, NBER Working Paper No. 31462) 研究的是银行分支物理密度 (bank branch density per capita/area), 即银行网点在地理空间上的结构性暴露, 与本列 mention_density 度量的"单篇文章内文本提及次数相对于正文长度的归一化强度"是两个完全不同的构念, 二者仅字面共享"density"一词, 不构成方法论同源; 引用二者的用意仅在于说明"密度型 (归一化) 指标相较绝对计数更能反映单位基数上的信号强度"这一构造原则在银行业实证文献中具有跨构念的一般适用性, 而非声称其研究对象与本列相同。与本列构念真正相关的是 Ge, Li & Zheng (2025, Journal of Banking and Finance) 对中国语境下新闻共现 (co-mention) 动量跨企业溢出效应的研究——其"新闻文本中的提及/共现频次是可量化、可预测后续经济结果的信息载体"这一核心假设, 与本 pipeline 中银行-金科同句/同文共现判定 (stage 13) 及本家族"提及密度加总作为文本暴露强度代理变量"的设计目的直接同源, 是三篇引文中唯一在构念层面而非仅关键词层面与 sum_mention_density 相关的文献。sum_mention_density 在本项目全部论文模块 (P1-P5 及衍生 provisional 论文) 中定位为 stage 40 输出的一批"篇幅-强度"辅助列之一, 供研究者在主回归之外做稳健性核查 (如检验主结果是否仅由篇数驱动而非提及强度驱动), 不作为任一论文的主处理变量 (treatment) 或结果变量 (outcome), 但可作为控制变量或异质性分组依据纳入面板回归设计。

## VAR: sum_mention_density

【变体差分】
本家族在 stage 40 面板层面为 singleton (仅此一列), 没有并列的 tier 变体、轨道分支或阈值梯子, 因此本节聚焦该列自身在计算口径上需要精确交代的边界条件, 而非与家族内其它列的差分。首先, 该列的行文本来源是"内容"全文 (未经 stage 14 三轨 (full/ctx/ss) 物化处理), 因为它的血缘上游 mention_density 产生于 stage 11 (银行新闻识别), 时序上早于 stage 14 的三轨文本物化与 stage 21-24 的情感/属性测度; 因此不应将 sum_mention_density 误读为三轨口径下的某一轨专属测度, 它是 track-agnostic 的、基于原始"内容"字段的密度加总, 与三轨情感/语义测度族 (各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J 的铁律) 没有交叉适用关系。其次, 该列所依赖的"合格文章"判定, 即是否计入某银行-年度加总, 由 stage 11 的 is_bank_news 前置条件与假阳性过滤共同决定, 与 stage 21 情感 LLM 的 full-only 留篇门控 (llm_verified_full == True, 2026-06-29 起口径) 是两套独立、时序前置的判定逻辑: 一篇文章只要通过 stage 11 银行新闻识别即计入本列的年度加总, 无需满足下游情感三家投票的留篇条件, 因此 sum_mention_density 的行覆盖面天然宽于任何以情感留篇集为行宇宙的测度, 使用者若将二者联立回归须注意样本口径不完全重合。第三, 该列是求和 (sum) 聚合而非均值或计数聚合, 数值随该银行-年度合格文章数量的增加而单调不减, 在跨银行比较时天然偏向报道量更大的银行 (通常是资产规模更大、媒体关注度更高的大型银行); 若研究目的是比较"单位报道的平均提及强度"而非"年度累积暴露总量", 应改用 sum_mention_density 除以合格文章数得到的篇均密度, 或结合 avg_doc_length/sum_doc_length 等同批辅助列做联合解释, 该列本身不提供这一归一化, 使用者需自行在下游构造。第四, mention_density 的分子 target_bank_mention_count 计入该银行全部已识别别名变体的命中次数 (含标题), 但不含被否定模式或短名歧义消解排除的假阳性命中, 因此 sum_mention_density 已经继承了 stage 11 假阳性过滤的全部保守性, 是一个经过实体消歧之后的"净"提及强度加总, 而非原始粗糙词频统计。
<!-- rendered-citations:begin -->
Gama, P. M., Sol Murta, F., & Vieira, E. S. (2024). Local banking development and SME conservative financing policy. Does bank branch density matter?. Small Business Economics, 63(4), 1747-1765. https://doi.org/10.1007/s11187-024-00910-6
Ge, S., Li, S., & Zheng, H. (2025). Diamond cuts diamond: News co-mention momentum spillover prevails in China. Journal of Banking and Finance, 171, 107356. https://doi.org/10.1016/j.jbankfin.2024.107356
Benmelech, E., Yang, J., & Zator, M. (2023). Bank Branch Density and Bank Runs. National Bureau of Economic Research Working Paper [Working Paper]. https://doi.org/10.3386/w31462
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
<!-- rendered-citations:end -->
