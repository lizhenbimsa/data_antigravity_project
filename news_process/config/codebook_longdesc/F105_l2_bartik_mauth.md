---
family_id: F105
columns:
- bartik_mauth_share_high
- bartik_mauth_share_low
- bartik_mauth_share_mid
unit: 基期份额 (proportion, 无量纲, [0,1]; 同一银行 high/mid/low 三档在基期有覆盖时行和为 1)
formula: "share_{i,k,T0} = N_{i,k,T0} / Σ_{k'∈{high,mid,low}} N_{i,k',T0}, k∈{high,mid,low}; 媒体权威档位 = high(score≥80) / mid(score≥60) / low(其余, 未映射媒体默认评分 10 → low); 基期无覆盖银行 share 保持 NaN (非伪零)"
producer: news_process/pipeline/panel/iv_did.py::compute_bartik_iv_fintech (runner.py 步骤 7e 以 group_prefix='mauth' 调用)
upstream:
- 40_panel 构建期 df_exploded (article-bank 展开级, 含 '媒体(中文)' 与 year 列)
- config/media_weights.json (媒体来源权威性评分, 决定 high/mid/low 档位切分)
citations:
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: "Journal of the Royal Statistical Society Series A: Statistics in Society"
  vol: 187
  issue: 3
  pages_or_artno: 748-771
- doi: 10.48550/arXiv.2404.17049
  type: arxiv
  authors: Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W.
  year: 2024
  title: "Overidentification in shift-share designs"
  venue: arXiv
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.1257/aer.20211063
  type: journal
  authors: Lee, D. S., McCrary, J., Moreira, M. J., & Porter, J.
  year: 2022
  title: "Valid t-ratio inference for IV"
  venue: American Economic Review
  vol: 112
  issue: 10
  pages_or_artno: 3260-3290
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.17848/9780585223940
  type: book
  authors: Bartik, T. J.
  year: 1991
  title: "Who benefits from state and local economic development policies?"
  venue: W.E. Upjohn Institute for Employment Research
- doi: "10.1093/ectj/utae003"
  title: "Design-based identification with formula instruments: a review"
  authors: "Borusyak, K., Hull, P., & Jaravel, X."
  year: 2024
  venue: "The Econometrics Journal"
  type: "journal"
  one_sentence_zh: "该文系统评述基于设计的公式工具变量(含shift-share/Bartik型)识别框架,为F105媒体权威度shift-share构造的份额-冲击正交性假设提供最新方法论依据。"
new_dois:
  - "10.1093/ectj/utae003"
---

## CORE

【构念与来源】
本家族三列 bartik_mauth_share_high / bartik_mauth_share_mid / bartik_mauth_share_low 是"媒体权威性"维度 shift-share (Bartik) 工具变量的基期份额分量 (base-period exposure shares)。它们刻画的构念是: 在冻结的前处理基期 T0, 某银行的全部媒体报道中, 分别来自高权威、中权威、低权威三档媒体来源的结构性占比。份额本身不是情感或注意力测度, 而是把某银行"暴露在何种权威档位媒体之下"的历史结构固定下来, 作为工具变量的横截面权重 (share), 待与随时间变动的行业级冲击 (shift) 相乘, 合成媒体权威维度的 Bartik IV (bartik_mauth_iv_full / _ctx / _ss)。因此三列是 IV 的"配料"而非终成品: 它们回答"这家银行在基期结构上偏向高权威还是低权威媒体报道", 冻结在 T0 以满足外生性公理。

媒体权威档位来自 config/media_weights.json 中对每一家媒体来源的权威性评分。运行期 runner.py 步骤 7e 读入该评分表, 对每篇报道按其"媒体(中文)"来源查分, 并以硬阈值切档: 评分 ≥80 记为 high、≥60 记为 mid、其余 (含评分表未收录、默认回退评分 10 的来源) 记为 low。切档规则在前处理期固定, 不随年份漂移, 这正是把媒体档位当作合法 share 维度的前提。该权威性思想承袭媒体经济学中"不同媒体的可信度/影响力不对称"的传统: 权威档位越高的来源, 其报道对市场与监管注意力的传导强度越大, 故银行在基期偏向哪一档媒体, 构成一条与其后续处理暴露相关、却又由历史媒体生态决定的结构性通道。

【方法学与计算】
计算在 pipeline/panel/iv_did.py::compute_bartik_iv_fintech 内完成 (通用文章属性维度 Bartik 接口, 以 group_prefix='mauth'、category_col='_media_authority' 传入)。第一步冻结基期份额: 取 df_exploded 中 year 落在解析后的基期年集合 (生产口径 T0 = max(panel.year.min(), 2010), 且强制 T0 < 政策冲击里程碑 2019, 否则抛错) 的报道, 按 (target_bank, 媒体权威档位) 计数, reindex 到 {high, mid, low} 三个保留档位, 再以该银行基期三档总篇数为分母归一化。由于媒体权威映射 mauth_map 不含 'other' 兜底类, 三档即为全部保留组, 故对基期有覆盖的银行, 三列份额行和恰为 1; 基期完全无报道的银行, 分母为 0 被置 NaN, 保持缺失而非伪零暴露 (fix omni-g-ivdid 系列的行为变更: 拒绝用 fillna(0) 制造精确零份额, 因为零暴露与"无从判定暴露"在 IV 一阶段中含义不同)。第二步 (shift) 与本家族三列无关: 它对每个档位在类别×年份上做 leave-one-out 的行业情感均值, 再与 share 相乘合成 IV; 三个 share 列只落地为 IV 的横截面权重, 独立成列供审计与诊断。

需要强调基期敏感性与外生性守卫: 基期若落入 2019 (DCEP 沙盒里程碑) 及之后, share 已处于后处理区间, 违反份额外生性公理, 代码会直接抛错或将敏感性变体置 NaN。三 share 列本身不含 full/ctx/ss 轨道分叉 (轨道差异只体现在下游 IV 的情感 shift 上), 也不含滞后或阈值梯子后缀, 属于"每档一列"的静态结构分量。

【文献定位】
shift-share/Bartik 工具变量的当代计量基础由三条互补路线奠定: Goldsmith-Pinkham, Sorkin & Swift (2020) 从份额外生性 (share exposure) 视角给出识别条件与 Rotemberg 权重诊断, 本项目"share 必须在前处理期固定"的公理与删除 28 类内生 IV 维度的决策直接引用该文; Adão, Kolesár & Morales (2019) 从冲击 (shift) 相关性视角刻画推断偏误并给出稳健标准误; Borusyak, Hull & Jaravel (2022) 则将两条路线统一到准实验 shift-share 框架, 其后 Borusyak, Hull & Jaravel (2025) 给出面向应用者的操作检查表, 明确 share×shift 的构造、incomplete-shares 与重归一化选择。媒体权威作为一条份额维度, 其合法性依赖档位在前处理期固定这一条件, 与上述份额外生路线一致。Apfel (2024) 讨论了在部分份额可能违反排他性时如何放松约束, 为本维度的稳健性叙事提供退路。有效工具的弱识别推断则参照 Lee, McCrary, Moreira & Porter (2022) 的 valid t-ratio 框架。范式源头为 Bartik (1991) 的 share×shift 加权思想。Borusyak, Hull & Jaravel (2024, The Econometrics Journal) 系统评述了基于设计的公式工具变量 (含 shift-share/Bartik 型) 识别框架, 为本家族媒体权威度 shift-share 构造的份额-冲击正交性假设提供了最新方法论依据。

方法学铁律: 本项目共保留 type/scale/fintech/media/geoprox/mauth 六类核心 Bartik 维度, 媒体权威 (mauth) 属其中的稳健性维度之一。六维度各自 just-identified 并排、互为稳健性、不分主次, 严禁把多维度的 share×shift 工具混入同一 over-identified 方程做 Hansen J 过度识别检验 (过度识别的联合矩条件会把维度间的构念差异误当作可检验的过度识别约束, 参见 Hahn, Kuersteiner, Santos & Willigrod (2024) 对 shift-share 过度识别的讨论)。媒体权威三档份额之间同理: high/mid/low 是同一 share 向量的互补分量, 只应整体进入某一维度的一阶段, 不得跨维度拼装。

## VAR: bartik_mauth_share_high

【变体差分】
本列是媒体权威三档份额向量中的高权威分量: 银行 i 在基期 T0 的全部媒体报道里, 来自权威评分 ≥80 的高权威来源的篇数占比。它区别于同族 mid、low 两列的唯一维度是档位取值 k=high (评分阈值 ≥80 这一最高切档)。该列语义为"基期结构上, 这家银行在多大程度上被高权威媒体报道所覆盖"; 数值越高, 表示其历史媒体暴露越集中于权威来源, 在下游 Bartik 一阶段中承担高权威档位行业情感冲击的横截面权重。计算口径: 分子=基期落入 high 档的报道篇数, 分母=该银行基期 high/mid/low 三档报道总篇数 (不含未保留兜底类), 故与 mid/low 两列行和为 1 (基期有覆盖时)。基期完全无报道的银行本列为 NaN, 与另两列同步缺失, 不置伪零。该列不分 full/ctx/ss 轨道 (轨道差异只在下游 IV 的情感 shift 上体现)、不含滞后与阈值梯子后缀, 是静态的基期结构分量。作为份额外生性维度, 高权威档位在前处理期固定, 严禁与 mid/low 拆开单独塞入过度识别方程; 三档整体构成媒体权威维度的一条 just-identified 工具, 与其余五类 Bartik 维度互为稳健性、禁混同一 Hansen J。因高权威档由单侧硬阈值 (评分 ≥80) 界定, 本列数值对 media_weights.json 中头部权威来源的评分定档较敏感, 但对长尾未映射来源不敏感 (后者一律落入 low), 解读时应关注高权威来源在基期语料中的覆盖厚度。

## VAR: bartik_mauth_share_low

【变体差分】
本列是媒体权威三档份额向量中的低权威分量: 银行 i 在基期 T0 的全部媒体报道里, 来自权威评分低于 60、以及评分表未收录 (默认回退评分 10) 来源的篇数占比。它区别于 high、mid 两列的唯一维度是档位取值 k=low, 且 low 档在实现上兼作兜底档——凡未被 high(≥80)/mid(≥60) 命中的来源一律归入 low, 包括 media_weights.json 未映射的媒体 (默认评分 10 远低于 60)。因此本列在实际数据中往往承接了权威评分缺失或长尾小媒体的报道, 语义为"基期结构上, 这家银行报道来源的低权威/未知权威占比"。计算分子=基期 low 档报道篇数, 分母=该银行基期三档总篇数, 与 high/mid 两列行和为 1 (基期有覆盖时); 基期无报道则为 NaN, 三列同步缺失。本列同样不分轨道、不含滞后或阈值梯子后缀, 为静态基期结构分量。因 low 档吸收了未映射来源, 其数值对 media_weights.json 收录完整度较敏感, 解读时应结合评分表覆盖率: 评分表越不完整, 越多长尾来源被默认回退到 low, 本列会被系统性抬高。作为份额外生维度, 低权威档位在前处理期固定, 须与 high/mid 整体构成一条 just-identified 工具, 严禁拆列单塞过度识别方程, 亦不得与其余五类 Bartik 维度混入同一 over-identified Hansen J; 六维度各自 just-identified 并排、互为稳健性、不分主次。

## VAR: bartik_mauth_share_mid

【变体差分】
本列是媒体权威三档份额向量中的中权威分量: 银行 i 在基期 T0 的全部媒体报道里, 来自权威评分落在 [60, 80) 区间来源的篇数占比。它区别于 high、low 两列的唯一维度是档位取值 k=mid, 由双侧阈值界定 (评分 ≥60 但未达 high 档的 ≥80), 是三档中唯一的"中间带", 既非最高权威亦非低权威/未知兜底。语义为"基期结构上, 这家银行报道来源的中等权威占比", 在下游 Bartik 一阶段中承担中权威档位行业情感冲击的横截面权重。计算分子=基期 mid 档报道篇数, 分母=该银行基期 high/mid/low 三档总篇数, 与 high/low 两列行和为 1 (基期有覆盖时); 基期无报道的银行本列为 NaN, 与另两列同步缺失, 不置伪零。本列不分 full/ctx/ss 轨道、不含滞后与阈值梯子后缀, 为静态基期结构分量。由于它由双侧阈值界定, 对 media_weights.json 评分在 60 与 80 两条切线附近的分布较敏感, 阈值处的来源归档变化会在 mid 与相邻档之间此消彼长。作为份额外生维度, 中权威档位在前处理期固定, 须与 high/low 整体构成媒体权威维度的一条 just-identified 工具, 严禁拆列单塞过度识别方程, 更不得与 type/scale/fintech/media/geoprox 五类维度混入同一 over-identified Hansen J——六维度各自 just-identified 并排、互为稳健性、不分主次。

<!-- rendered-citations:begin -->
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in shift-share designs. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.17049
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Lee, D. S., McCrary, J., Moreira, M. J., & Porter, J. (2022). Valid t-ratio inference for IV. American Economic Review, 112(10), 3260-3290. https://doi.org/10.1257/aer.20211063
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Bartik, T. J. (1991). Who benefits from state and local economic development policies? W.E. Upjohn Institute for Employment Research. https://doi.org/10.17848/9780585223940
Borusyak, K., Hull, P., & Jaravel, X. (2024). Design-based identification with formula instruments: a review. The Econometrics Journal. https://doi.org/10.1093/ectj/utae003
<!-- rendered-citations:end -->
