---
family_id: F032
columns:
- avg_category_confidence
- avg_category_confidence_ctx
- avg_category_confidence_full
unit: 无量纲分类置信度得分, 取值区间 [0, 1], 银行-年层面按篇取算术均值
formula: "avg_category_confidence_{track} = mean_over_articles( category_confidence_{track} ); category_confidence_{track} = locus 分类置信度, 由三家 LLM 对 locus 类目的多数票与关键词分类器类目交叉验证得出, 其数值取自关键词分类器证据强度 kw_conf 经一致/分歧调整 (一致 → min(kw_conf + 0.2, 1.0); 分歧 → round(kw_conf × 0.5, 3)), 而非对 per-model 置信度取均值; 无后缀裸名 = _full 别名"
producer: pipeline\panel\encode.py ; pipeline\sentiment\tone_llms.py
upstream:
- 21_tone_llms.parquet (category_confidence_full, category_confidence_ctx)
- 40_panel_yearly.parquet
citations:
- doi: 10.1177/00131644251380540
  type: journal
  authors: Almehrizi, R. S.
  year: 2026
  title: "Coefficient lambda for interrater agreement among multiple raters: Correction for category prevalence"
  venue: Educational and Psychological Measurement
  vol: 86
  issue: 2
  pages_or_artno: 287-319
- doi: 10.18653/v1/2024.naacl-long.366
  type: journal
  authors: Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I.
  year: 2024
  title: "A survey of confidence estimation and calibration in large language models"
  venue: "Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)"
  pages_or_artno: 6577-6595
- doi: 10.1016/j.csda.2013.03.024
  type: journal
  authors: Gaure, S.
  year: 2013
  title: "OLS with multiple high dimensional category variables"
  venue: Computational Statistics & Data Analysis
  vol: 66
  issue: ""
  pages_or_artno: 8-18
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是银行-年层面上"创新场所 (locus) 类目判定的平均置信度", 是对每篇银行金科报道被归入某一创新场所类目 (如技术层 vs 应用场景) 这一分类动作的可信度度量, 而非情感极性、注意力强度或语义陈旧度。上游信号来自 stage 21 情感与分类阶段的 tone_llms.py: 对每篇文章逐轨解析创新场所标签时, 同时产出一个介于 0 与 1 之间的分类置信度 category_confidence_{track}。该置信度是 LLM 判定与关键词分类器判定交叉验证的产物, 记录了"这篇文章到底属于哪个创新场所类目"这一判断在两条独立证据链上的相互印证程度。encode.py 在构建银行-年面板时, 对每家银行每一年内的所有留篇报道, 按 target_bank 与 year 分组, 对逐篇的 category_confidence_{track} 取算术均值, 得到本家族的三列聚合置信度。构念上它是一个元-测度 (meta-measure): 度量的不是"报道说了什么", 而是"我们对报道被如何归类这件事有多确定", 因此在计量中通常作为分类质量控制变量、低置信度诊断的门槛, 或异质性切分的依据, 而非核心处理变量或结果变量。

【方法学与计算】
计算链路分两层。第一层在文章级 (tone_llms.py::_resolve_locus_track): 对给定轨道, 先把三家 LLM 对该篇创新场所类目的投票做保守式多数投票 (majority_vote_categorical, 平局回退默认类目 '应用场景'), 再用关键词分类器 canonicalize_topic 对同篇主题串给出一个基于词典证据的类目 kw_cat 与证据强度 kw_conf。随后做 LLM×关键词交叉验证: 二者类目一致时给予置信度增益, 令 final_conf = min(kw_conf + 0.2, 1.0); 二者分歧时施加惩罚, 令 final_conf = round(kw_conf × 0.5, 3)。零证据路径经过刻意对称化处理: 当 LLM 无票且关键词分类器亦无真实证据 (kw_conf 为 0) 时返回 (None, 0.0), 使纯零证据的默认归类不再冒充分类信号; 仅当关键词有真实证据时才保留关键词回退类目。这一修正与 substantiveness、collaboration 两维度的空票处理保持一致口径, 避免未验证文章被系统性地默认塞进某一类目而虚增置信度。此处须澄清一处易误张冠的实现细节: 本列的跨模型信息仅通过三家 LLM 对 locus 类目做多数投票 (majority_vote_categorical) 这一步进入 — 投票越一致, 多数票类目越稳, 越可能与关键词类目印证而触发 boost; 而置信度的数值本身取自关键词分类器的证据强度 kw_conf 及其一致/分歧调整, 并不对各家 LLM 自报的 per-model 置信度取算术平均。模块级函数 _avg_innovation_confidence 服务的是另一列族 innovation_locus_confidence_{track} (对 parsed 结果按模型做置信度平均), 与本家族的 category_confidence_{track} 是来源与算法均不同的两列, 切勿把前者的多模型平均语义误安到本列上。第二层在面板级 (encode.py L1642-1660): 逐轨按银行-年分组取均值; 裸名列 avg_category_confidence 直接取 avg_category_confidence_full 作为别名, 并保留对 v3.1.x 旧裸名 schema 的兼容回退。取值恒落在 [0, 1] 内, 无量纲。

【文献定位】
本测度处在大语言模型置信度估计与评分者一致性两条方法学脉络的交叉处。就前者而言, Geng et al. (2024) 系统综述了大语言模型置信度估计与校准的方法谱系, 指出模型自报置信度往往偏离真实正确率, 需要外部证据或多源印证来校准; 本家族以关键词分类器作为独立证据链对 LLM 判定进行 boost/penalty 校正, 正是这一"外部锚定"思路在分类置信度上的落地。而以关键词/词典证据与机器判定两条独立链路交叉印证文本类目, 与 Frankel, Jennings 和 Lee (2022) 在顶刊层面对"机器学习分类器 vs 词典方法"两类文本测度进行系统对照、并据其一致性评估分类可信度的做法一脉相承: 二者判定相合时可信度更高、分歧时须折价的直觉, 正是本测度 boost/penalty 校正机制的度量论依据。就后者而言, LLM 多数票与关键词分类器可视为两组独立"评分者", Almehrizi (2026) 讨论的多评分者一致性系数及其对类目基率的校正, 为理解"一致即加权、分歧即折价"的置信度构造提供了度量论依据 — 尤其当类目分布高度不均 (如应用场景类目占比偏高) 时, 一致性的信息量需按基率折算, 这与本测度对零证据默认归类的谨慎处理动机相通。就下游计量用途而言, 该家族常作为高维类目固定效应或分类质量控制进入回归, Gaure (2013) 关于多重高维类目变量最小二乘估计的讨论, 为把分类置信度纳入含银行、年份等多重固定效应的面板模型提供了估计层面的参照。需强调本家族在面板层是 full 与 ctx 两轨并存、无 ss 列 (与 cell_id 一致的 carve-out), 但须准确表述其成因: 文章级 tone_llms.py 对创新场所判定的三轨 (full/ctx/ss) 均逐轨产出了置信度, category_confidence_ss (同句共现轨) 在文章级确实被计算; 面板家族之所以无 ss 列, 是因为 encode.py 的银行-年聚合映射刻意只纳入 category_confidence_full 与 category_confidence_ctx 两源, 未把 ss 轨聚合进本家族, 而非"创新场所判定不做严格同句轨"。两轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把 full 与 ctx 两列混入同一 over-identified Hansen J 过度识别检验。银行-年留篇宇宙遵循 full-only 门控口径 (2026-06-29): 是否算作一篇银行金科报道只看 full 轨留篇判定, ctx 轨为 conditional-on-full 的稳健性测度轨, 其行宇宙是 full 留篇集的子集, 逐轨列各自照算。

## VAR: avg_category_confidence

【变体差分】
本列是家族的无后缀裸名列, 语义上等同于 avg_category_confidence_full 的别名: encode.py 在检测到上游存在 category_confidence_full 时, 直接把 avg_category_confidence 赋值为 avg_category_confidence_full, 二者逐行相等。无后缀命名是历史契约产物 — export.py 的 G-20 低置信度诊断与既有 codebook、Stata 消费者长期以裸名引用该列, 保留裸名是为兼容这些既有消费者而非表示它是"主轨"。此处需澄清一处曾经的死列史: v3.2.0 起上游列名迁移为 category_confidence_<track>, 旧代码对旧裸名 'category_confidence' 的检查恒假, 致 else 分支恒走、该列一度永久全 NaN (omni-g-encode-10 修复, 2026-06-11); 现改接 full/ctx 源后复活, 并仍对 v3.1.x 旧裸名 parquet 保留 groupby 均值回退路径。因此本列在生产语料上取的是 full 轨值, 落在 [0, 1] 无量纲区间, 银行-年按篇均值。使用时应把它理解为 full 轨置信度的稳定入口, 而非独立第四轨; 凡需与 ctx 轨对照做稳健性时, 应显式引用 _full 与 _ctx 两列, 而两者各自 just-identified 并排、禁混同一 over-identified Hansen J 的铁律对本别名列同样适用。就实证使用而言, 本裸名列最常见的角色是分类质量门槛: 例如在稳健性检验中剔除银行-年层面平均置信度过低的观测, 或据其做异质性切分以检验主结论是否被低置信度分类样本驱动。由于它与 avg_category_confidence_full 逐行相等, 在同一回归中同时纳入两者会造成完全共线, 二者只应择一进入右手边。需再次提醒: 本列既非核心处理变量亦非结果变量, 而是元-测度 (度量分类动作本身的可信度), 其数值高低不直接对应报道对银行金科活动的褒贬, 解读时切勿与情感极性或注意力强度混淆。

## VAR: avg_category_confidence_ctx

【变体差分】
本列是 ctx 轨的分类置信度均值, 与 canonical 的 full 轨的唯一差分在于上游文本通道: ctx 轨的创新场所判定基于"标题 prepend + 实体上下文窗" (content_ctx) 而非全文正文, 即只在目标银行与金融科技实体的邻近窗口内取证据来判定创新场所类目, 因而其置信度反映的是"在实体聚焦语境下"分类的可信程度。相对 full 轨, ctx 轨证据面更窄、噪声更少但可用信号也更稀疏, 因此其置信度分布与 full 轨可能系统性不同 (窗口内证据不足时更易落入关键词零证据路径, 触发 (None, 0.0) 或低 kw_conf 的折价惩罚)。在留篇口径上, ctx 轨是 conditional-on-full 的稳健性测度轨: 行宇宙为 full 留篇集的子集, 是否算一篇报道由 full 轨门控决定 (full-only 门控, 2026-06-29), ctx 列仅在该子集上逐轨照算其置信度均值。本列与 avg_category_confidence_full 互为稳健性、不分主次, 二者各自 just-identified 并排, 严禁混入同一 over-identified Hansen J 过度识别检验。本家族在面板层无 ss 列 (carve-out, 与 cell_id 同): 文章级虽同样计算了 ss 轨的 category_confidence_ss, 但 encode.py 面板映射只纳入 full 与 ctx 两源, 未把 ss 轨聚合进本家族, 故不存在 avg_category_confidence_ss 孪生列, 面板对照仅在 full 与 ctx 两轨间进行。在开发规模 (T=2) 语料上, ctx 轨曾观察到较高比例的未验证行仍获标签且其中相当数量的 category_confidence 恰为 0 (纯零证据默认路径的残留), 这属预期退化而非缺陷: 实体窗内证据稀疏时, LLM 空票叠加关键词零证据会稳定落到 (None, 0.0), 拉低本列均值。生产规模 (T=19) 下窗口内证据更充分, 该退化会显著缓解。使用本列做稳健性对照时, 应意识到其相对 full 轨更易受窗口证据稀疏影响, 因此当 full 与 ctx 结论一致时对主结论的支撑最强; 若两轨分歧, 需回到证据面差异去解释, 而非简单取平均或并入同一过度识别检验。

## VAR: avg_category_confidence_full

【变体差分】
本列是 full 轨的分类置信度均值, 也是家族的 canonical 定义列 (无后缀裸名 avg_category_confidence 即取本列为别名)。full 轨的创新场所判定基于"标题 prepend + 全文正文" (content_full), 即在整篇报道的完整文本上做 LLM 多数票与关键词分类器的交叉验证, 因而证据面最宽、可用信号最充分, 其置信度通常是三列中最稳定、非缺失比例最高的一列。计算上, encode.py 对每家银行每一年内所有 full 留篇报道逐篇的 category_confidence_full 取算术均值; 该逐篇值由三家 LLM 对 locus 类目的多数票与关键词分类器交叉验证得出, 数值取自关键词证据强度 kw_conf 经 LLM×关键词一致/分歧的 boost/penalty 校正 (一致 +0.2 封顶 1.0, 分歧 ×0.5), 并非对各家 LLM 自报的 per-model 置信度取算术平均 (后者是另一列族 innovation_locus_confidence 的算法, 与本列来源不同)。在留篇门控上, full 轨是判定"是否算一篇银行金科报道"的唯一权威轨 (full-only 门控, 2026-06-29), 因此本列的银行-年行宇宙即 full 留篇集本身, 分母口径与 n_articles 一致。本列作为 canonical, 与 ctx 轨互为稳健性、不分主次, 两轨各自 just-identified 并排, 禁混同一 over-identified Hansen J; 其取值恒落 [0, 1] 无量纲区间。下游若做低置信度样本剔除或分类质量异质性切分, 应优先以本列 (或其别名裸名列) 为门槛变量, 而以 ctx 轨作稳健性对照。值得强调本列的置信度均值受两重构造机制影响: 其一是三家 LLM 对 locus 类目的多数投票, 投票越一致则多数票类目越稳、越可能与关键词类目印证而触发 boost (此为跨模型信息进入本列的唯一通道, 并非对 per-model 置信度取均值); 其二是 LLM×关键词交叉验证, 一致时封顶 1.0 的增益与分歧时减半的惩罚共同决定单篇值的高低。因此一个高 avg_category_confidence_full 的银行-年, 既意味着该年报道的创新场所归属较为清晰, 也意味着 LLM 判定与词典证据高度印证; 反之低值可能源于类目模糊、证据稀薄或两条证据链系统性分歧。解读时应结合 n_articles 与分类计数一并看, 避免在报道极少的银行-年上把偶发的高/低置信度当作稳定信号。

<!-- rendered-citations:begin -->
Almehrizi, R. S. (2026). Coefficient lambda for interrater agreement among multiple raters: Correction for category prevalence. Educational and Psychological Measurement, 86(2), 287-319. https://doi.org/10.1177/00131644251380540
Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration in large language models. Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), 6577-6595. https://doi.org/10.18653/v1/2024.naacl-long.366
Gaure, S. (2013). OLS with multiple high dimensional category variables. Computational Statistics & Data Analysis, 66, 8-18. https://doi.org/10.1016/j.csda.2013.03.024
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
