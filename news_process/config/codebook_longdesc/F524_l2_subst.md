---
family_id: F524
columns:
- subst_disagree_frac
- subst_freerider_frac
- subst_quietworker_frac
unit: 比率/占比 (proportion, [0,1]; both_valid 域内分子/分母同域计数, both_valid<5 记 NaN)
formula: 'subst_disagree_frac = Σ subst_disagree / n_bothvalid; subst_freerider_frac = Σ subst_freerider / n_bothvalid; subst_quietworker_frac = Σ subst_quietworker / n_bothvalid (银行×年分组; n_bothvalid<5 含=0 记 NaN; 逐篇 subst_disagree=(full_norm≠ctx_norm)∧both_valid, subst_freerider=(full_norm==实质性)∧(ctx_norm==象征性), subst_quietworker=(full_norm==象征性)∧(ctx_norm==实质性))'
producer: pipeline\panel\encode_collab.py (derive_residual_signals / aggregate_d4_panel); 上游标签来自 pipeline\sentiment\tone_llms.py (innovation_substantiveness_full / innovation_substantiveness_ctx)
upstream:
- 21_tone_llms.parquet
citations:
- doi: 10.2307/2393295
  type: journal
  authors: "Westphal, J. D.; Zajac, E. J."
  year: 1994
  title: "Substance and Symbolism in CEOs' Long-Term Incentive Plans"
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: 10.2307/2393593
  type: journal
  authors: "Westphal, J. D.; Zajac, E. J."
  year: 1998
  title: "The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions"
  venue: Administrative Science Quarterly
  vol: '43'
  issue: '1'
  pages_or_artno: 127-153
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: "Fiss, P. C.; Zajac, E. J."
  year: 2006
  title: "The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling"
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: 10.1111/jofi.13412
  type: journal
  authors: "Duchin, R.; Gao, J.; Xu, Q."
  year: 2025
  title: "Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution"
  venue: The Journal of Finance
- doi: 10.1287/mnsc.2024.07420
  type: journal
  authors: "Giannetti, M.; Jasova, M.; Loumioti, M.; Mendicino, C."
  year: 2026
  title: "Glossy Green Banks: The Disconnect Between Environmental Disclosures and Lending Activities"
  venue: Management Science
- doi: "10.1016/j.technovation.2023.102880"
  type: "journal"
  authors: "Granados, C., Ayala, Y., & Ramos-Mejia, M."
  year: 2024
  title: "Is it substantive or just symbolic? Understanding innovation theater in organisations: The case of technology-based innovation"
  venue: "Technovation"
  vol: "129"
  pages_or_artno: "102880"
- doi: "10.1016/j.chb.2026.108988"
  type: "journal"
  authors: "Liu, J."
  year: 2026
  title: "Rubric-conditioned large language model labeling: Agreement, uncertainty, and label consistency in subjective text annotation"
  venue: "Computers in Human Behavior"
  vol: "181"
  pages_or_artno: "108988"
new_dois: []
---

## CORE

【构念与来源】
本家族 F524 (l2_subst, 3 列, 全部 standard tier) 度量的是"实质性 vs 象征性" (substantiveness) 这一创新分类标签在 full 文本口径与 ctx 文本口径之间的说做不一致程度, 即 Westphal & Zajac (1994 ASQ; 1998 ASQ) 提出的 decoupling (言行解耦) 传统在本项目里的经验化实现。stage 21 (`tone_llms.py`) 对每篇文章的银行-金科报道, 用三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票产出 `innovation_substantiveness_full` 与 `innovation_substantiveness_ctx` 两个二值分类标签, 取值 ∈ {实质性, 象征性} (实质性=底层技术性/资源投入型创新报道; 象征性=宣传性/口号性报道, 平局按 tie_default='象征性' 保守降级, 即多数票不确定时不偏向声称"实质")。full 轨扫描整篇正文, ctx 轨只扫描围绕目标实体的窗口文本 — 二者对同一篇文章可能给出不同判定, 这个分歧本身就是本家族的核心构念: 一篇报道全文读起来像是"扎实做事", 但聚焦到银行-金科相关句子却像"口号先行" (或反之), 暗示该报道存在选择性呈现/漂绿 (washing) 式的言行不一。`pipeline\panel\encode_collab.py::derive_residual_signals` 在文章级原地新增 `subst_disagree` / `subst_freerider` / `subst_quietworker` 三个布尔列 (连同 locus/collab 两个平行维度共 9 列), `aggregate_d4_panel` 再把它们聚合成银行×年面板比率, 即本家族三列。
【方法学与计算】
计算分两步。步骤一 (文章级, `derive_residual_signals`): 对 `innovation_substantiveness_full`/`innovation_substantiveness_ctx` 先做 `_normalize_label` 归一化 (去首尾空白、全角空格 U+3000、内部所有 `\s`, 防御 LLM 输出携带的格式噪声), 再用 `_both_valid_mask` 判定该篇文章 full 与 ctx 两路标签是否均落在 canonical 二值集合 {实质性, 象征性} 内 (`isin` 白名单口径, 而非简单 notna — 任何脏标签/非二值输出即被排除出 both_valid, 而非被强行归入某一类); 在 both_valid=True 的前提下: `subst_disagree`=(full_norm != ctx_norm), `subst_freerider`=(full_norm==实质性)∧(ctx_norm==象征性) [全文层面看着扎实、聚焦到银行-金科窗口反而落空的"说一套做一套"疑似信号], `subst_quietworker`=(full_norm==象征性)∧(ctx_norm==实质性) [反过来, 全文偏宣传但银行-金科相关片段其实扎实的"做而不说"信号]; both_valid=False (任一轨 NaN 或非 canonical 脏标签) 时三列按构造全部编为 False 而非 NaN, 这是刻意设计使可证不变量成立: (i) freerider 与 quietworker 互斥, (ii) freerider+quietworker 恒等于 disagree (因为两者正是 disagree 的两个互斥子情形), (iii) both_valid=False 的文章对这三个信号的贡献恒为零而非缺失。步骤二 (面板级, `aggregate_d4_panel`): 对每个 (银行, 年) 分组, `n_articles_subst_bothvalid` = 该组 both_valid=True 的文章数, `subst_disagree_frac` 等三个 frac 列 = 对应布尔列在该组的计数之和除以 `n_articles_subst_bothvalid` (分子分母严格同域, 均限定在 both_valid 子集内, 而非除以物理文章总数); 若 `n_bothvalid < 5` (含恰为 0 的"假零"情形) 则该行三列一律记为缺失值而非 0, 防止小样本组把"无法判定"误报成"零分歧"。若上游 `innovation_substantiveness_full`/`_ctx` 源列在给定 build 缺失导致 both_valid 无法重建, 会整体回退到 legacy 物理分母 (`groupby.mean()`, 门槛改用物理 `n_articles<5`) 并记入日志告警, 生产口径以 both_valid 分母为准。三列在数值上满足 `subst_disagree_frac == subst_freerider_frac + subst_quietworker_frac` (由文章级不变量线性传递到面板级比率)。
【文献定位】
本测度的分析传统直接承自 Westphal & Zajac 关于公司治理"实质性采纳 vs 象征性采纳" (substance vs symbolism) 的经典二分, 该框架把治理/创新举措区分为真正改变实践的实质性行动与仅为满足外部合法性压力的象征性姿态 (Westphal & Zajac, 1994, *Administrative Science Quarterly*; Westphal & Zajac, 1998, *Administrative Science Quarterly*), 后续 Fiss & Zajac (2006, *Academy of Management Journal*) 进一步把象征性管理拓展到战略变革的框架化与解耦 (sensegiving via framing and decoupling) 机制。本家族把这一构念从"公司对外公告 vs 实际治理实践"的二元比较, 转译为"同一篇新闻报道在 full 全文口径与 ctx 实体窗口口径下给出的实质性标签是否一致"的文本内部 (within-article) 比较 — 两个口径可理解为对同一事件的两种"观察窗口", 其分歧即为言行 (或者说全篇叙事与聚焦细节) 不一致的经验代理。近期文献进一步把这一 decoupling 传统应用到金融/ESG 语境下的"漂绿"(washing) 现象, 例如 Giannetti, Jasova, Loumioti & Mendicino (即将刊于 *Management Science*) 记录银行环境信息披露与实际放贷行为之间的脱节, Duchin, Gao & Xu (2025, *The Journal of Finance*) 用资产市场证据区分可持续性行动与漂绿, 均与本家族"报道口径分歧代理言行不一"的构造逻辑同源, 是本项目将治理决耦文献移植到银行-金科媒体报道情境的直接方法学参照。 落到创新这一具体语境, Granados、Ayala 与 Ramos-Mejia (2024) 以「创新剧场」(innovation theater) 之名系统刻画技术创新中象征性展演与实质性投入的分野, 为本家族 {实质性, 象征性} 二分提供了当代组织理论层面的构念界定与机制阐述; 惟该文是组织层面的质性/理论化研究, 既未给出文本自动分类算法, 也未做银行样本的面板计量, 本家族则把该构念下沉为 LLM 对单篇报道话语的逐篇标签并按银行-年计数, 操作化层级、数据类型与语境 (中国、银行业) 均与之不同, 引用仅及于构念界定这一层。测量侧的一条诚实边界则由 Liu (2026) 提示: 该文以固定 rubric 提示单一模型重标注英文社交媒体仇恨言论语料, 发现在主观标注任务中模型返回的类别概率向量的 Shannon 熵在人类标注分歧较大处系统性更高, 说明 LLM 标签在此类主观判定上本身带有不可忽略的不确定性 — 据此可推断 subst_disagree_frac 至少有一部分并非言行解耦的真实信号, 而是标注不稳定所设定的噪声地板。须强调该文度量的分歧是同一文本上标注者/模型之间的一致性, 与本家族「同一多数票共识在 full 与 ctx 两个观察窗口下是否一致」并非同一构念层级, 且其语料非中文金融新闻、全程只用单一模型而不涉跨厂商比较、亦无实体-年聚合, 故只作噪声地板的警示引用, 不构成对本家族分歧口径或 per-model 并排安排的任何背书。
## VAR: subst_disagree_frac

【变体差分】
本列是本家族的总量 (umbrella) 测度: 在 both_valid 子集内, full 与 ctx 两路 `innovation_substantiveness` 标签不一致 (无论方向) 的文章占比, 即 `subst_freerider_frac + subst_quietworker_frac` 的算术和 (由文章级构造不变量 (ii) 保证)。它回答"这家银行这一年关于银行-金科的报道里, 全文叙事与聚焦银行-金科的窗口叙事在'实质性/象征性'判定上说不到一起去的比例有多高", 数值越高意味着该行媒体形象的'言行一致性'越低 (要么是报道本身叙事松散, 要么是该行的银行-金科相关内容与报道整体基调存在系统性偏离, 后者常见于选择性披露/漂绿情境)。full 轨与 ctx 轨在本家族语境下不是互为稳健性的并排测度 (与 CLAUDE.md 描述的三轨 full/ctx/ss 各自 just-identified 并排、禁混同一 over-identified Hansen J 的一般铁律不同) —— 本家族恰恰是刻意利用两轨之间的差异本身作为构念, 因此不适用"禁混"表述; ss 轨在本家族不存在对应残差列: `tone_llms.py` 确实同样对 ss 轨计算并写出 `innovation_substantiveness_ss` (三轨平局保守 MAP 口径一致), 该标签本身存在且被家族 F511 (`sub_frac_ss`) 等下游消费, 并非"不存在"; 只是本家族 D4 残差构造 (`derive_residual_signals`/`aggregate_d4_panel`) 按设计只比较 full 与 ctx 两个属性口径, 不纳入 ss 轨参与比较, 因此本家族层面不存在 `subst_*_ss` 系列列, 是刻意的取舍留白而非该标签全项目缺席, ctx/ss 回退语义在本家族无适用对象。分母限定 both_valid≥5 (小于 5 或恰为 0 记 NaN), 覆盖率诊断列 `n_articles_subst_bothvalid` 与本列同批产出、供论文披露。使用本列做横截面比较时须同时报告该覆盖率列, 因为不同银行-年的 both_valid 样本量差异本身也是信息 (some 银行-年可能因报道量小或标签质量差被整组置 NaN, 不应与"分歧率为 0"混淆); 建议在回归中把本列与 locus/collab 两个平行维度的对应 disagree_frac 并列报告而非互相替代, 三者分别刻画"实质性判定"“技术底层 vs 应用场景判定”“自主研发 vs 外部协同判定”三个独立分类轴上的口径分歧, 彼此不可加总也不构成同一 over-identified 设定下的替代工具。

## VAR: subst_freerider_frac

【变体差分】
本列是 subst_disagree_frac 的两个互斥方向子分量之一: 在 both_valid 子集内, full 全文判定为"实质性"但 ctx 银行-金科聚焦窗口判定为"象征性"的文章占比 —— 直觉上对应"说一套做一套"式的疑似信号, 即整篇报道读来扎实厚重, 但真正与目标银行、金融科技直接相关的段落其实偏空洞宣传, 全文的"实质感"更多是由报道中与银行-金科无关的其他内容撑起来的, 故以经济学"搭便车" (free-rider) 隐喻命名。计算严格与 subst_disagree_frac 共享同一 both_valid 掩码与同一 n_bothvalid<5 缺失门槛 (同一 `_both_valid_mask` 调用、同一分母), 二者及 subst_quietworker_frac 三列在文章级布尔层面互斥可加 (freerider+quietworker==disagree, freerider 与 quietworker 本身互斥), 面板级比率因线性聚合继承该关系。方向标签基于 full 与 ctx 的相对位置而非任一轨本身的"正确性"判断, 不隐含全文轨或 ctx 轨谁更可信的先验; 与本家族总量列一样, 不受留篇门控 full-only (2026-06-29 决策) 的三轨互斥规则约束, 因为本列的计算对象是留篇后样本内 full/ctx 两个属性标签的横向比较, 而非留篇判定本身。使用建议上, 本列宜与 subst_quietworker_frac 成对报告而非孤立解读: 单一比例数字无法区分"该行媒体形象总体被夸大"与"该行相关内容被稀释在更宏观叙事里"两种性质迥异的传播模式, 只有把两个方向拆开、结合 n_articles_subst_bothvalid 覆盖率一起看, 才能对该行的银行-金科报道言行一致性做出可靠判断; 与 locus/collab 两个平行维度的对应 freerider 列同理互不替代, 各自刻画独立分类轴上的方向性偏斜。

## VAR: subst_quietworker_frac

【变体差分】
本列是 subst_disagree_frac 的另一互斥方向子分量: 在 both_valid 子集内, full 全文判定为"象征性"但 ctx 银行-金科聚焦窗口判定为"实质性"的文章占比, 即整篇报道整体基调偏宣传/口号性, 但真正涉及目标银行与金融科技的具体段落反而透露出扎实的技术/资源投入信息, 报道对该行金科动作的实质性着墨被淹没在通篇更宏观或更营销化的叙事里, 以"闷头干活不声张" (quiet worker) 隐喻命名, 与 subst_freerider_frac 方向相反但计算口径完全对称 (同一 both_valid 掩码、同一分母、同一 n_bothvalid<5 缺失门槛)。三列 (disagree/freerider/quietworker) 应联合解读: 单看 disagree 只能知道"多大比例的报道言行口径不一", 而 freerider 与 quietworker 的相对大小揭示不一致的方向性偏斜 —— 若某行 freerider 显著高于 quietworker, 暗示该行的媒体叙事存在系统性"整体镀金、局部空心"倾向 (更贴近传统漂绿/象征性管理的方向); 反之若 quietworker 更高, 则暗示该行的银行-金科实质进展被淹没在更中性或更宏观的整体报道基调里, 是被低估而非被夸大的媒体呈现问题, 两种情形对应完全不同的公司传播/治理解读, 不能只报告 disagree 总量而不拆解方向。与 subst_freerider_frac 一样, 本列同样限定 both_valid≥5 才计算, 使用时须同时核对 n_articles_subst_bothvalid 覆盖率列以避免把"样本不足被置 NaN"误读为"无分歧"; locus/collab 两个平行维度存在结构完全对称的 quietworker 列, 三者刻画三条独立分类轴, 互不可替代亦不构成同一 over-identified 设定下的替代工具变量。

<!-- rendered-citations:begin -->
Westphal, J. D.; Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Westphal, J. D.; Zajac, E. J. (1998). The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Fiss, P. C.; Zajac, E. J. (2006). The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Duchin, R.; Gao, J.; Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Giannetti, M.; Jasova, M.; Loumioti, M.; Mendicino, C. (2026). Glossy Green Banks: The Disconnect Between Environmental Disclosures and Lending Activities. Management Science. https://doi.org/10.1287/mnsc.2024.07420
Granados, C., Ayala, Y., & Ramos-Mejia, M. (2024). Is it substantive or just symbolic? Understanding innovation theater in organisations: The case of technology-based innovation. Technovation, 129, 102880. https://doi.org/10.1016/j.technovation.2023.102880
Liu, J. (2026). Rubric-conditioned large language model labeling: Agreement, uncertainty, and label consistency in subjective text annotation. Computers in Human Behavior, 181, 108988. https://doi.org/10.1016/j.chb.2026.108988
<!-- rendered-citations:end -->
