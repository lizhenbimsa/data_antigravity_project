---
family_id: F410
columns:
- locus_disagree_frac
- locus_freerider_frac
- locus_quietworker_frac
unit: 比率/占比 (proportion, [0,1]; bank-year 面板级, 分母限定在 both_valid 子集且施加最小样本量门槛, 小样本置 NaN)
formula: 'locus_disagree_frac = Σ_article locus_disagree / n_bothvalid; locus_freerider_frac = Σ_article locus_freerider / n_bothvalid; locus_quietworker_frac = Σ_article locus_quietworker / n_bothvalid (n_bothvalid < 5 → NaN; both_valid = full 与 ctx 两轨 innovation_locus 标签均落在 {底层技术, 应用场景} canonical 集合内的文章数)'
producer: pipeline\panel\encode_collab.py (derive_residual_signals / aggregate_d4_panel) ; pipeline\sentiment\tone_llms.py (innovation_locus_full / innovation_locus_ctx 上游标签来源)
upstream: []
citations:
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: 'Digital finance and FinTech: Current research and future research directions'
  venue: Journal of Business Economics
  vol: '87'
  issue: '5'
  pages_or_artno: 537-580
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: Disagreement and asset prices
  venue: Journal of Financial Economics
  vol: '114'
  issue: '2'
  pages_or_artno: 226-238
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: Disagreement and the stock market
  venue: Journal of Economic Perspectives
  vol: '21'
  issue: '2'
  pages_or_artno: 109-128
- doi: 10.1287/mnsc.2015.2405
  type: journal
  authors: Cen, L., Wei, K. C. J., & Yang, L.
  year: 2017
  title: 'Disagreement, underreaction, and stock returns'
  venue: Management Science
  vol: '63'
  issue: '4'
  pages_or_artno: 1214-1231
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: News-based investor disagreement and stock returns
  venue: Review of Accounting Studies
  vol: '30'
  issue: '3'
  pages_or_artno: 2312-2375
- doi: 10.1613/jair.1.12752
  type: journal
  authors: Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M.
  year: 2021
  title: 'Learning from disagreement: A survey'
  venue: Journal of Artificial Intelligence Research
  vol: '72'
  issue: ''
  pages_or_artno: 1385-1470
- doi: 10.1287/isre.1100.0322
  type: journal
  authors: Yoo, Y., Henfridsson, O., & Lyytinen, K.
  year: 2010
  title: 'The new organizing logic of digital innovation: An agenda for information systems research'
  venue: Information Systems Research
  vol: '21'
  issue: '4'
  pages_or_artno: 724-735
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的不是某篇报道"是不是在讲底层技术"这一水平量, 而是同一篇报道在两种不同取材范围下, 对 innovation_locus (创新落点: 底层技术 enabling technology 还是应用场景 business function, 分类锚点取自 Gomber, Kauffman, Parker & Weber 2018 JMIS 及本家族引注的 Gomber, Koch & Siering 2017 JBE 对金融科技研究方向的二分框架) 判定是否发生了"说一套做一套"式的漂移。stage 21 情感 LLM 对每篇文章同时产出 full 轨 (标题+全文) 与 ctx 轨 (标题+实体窗口) 两套 innovation_locus 标签; full 轨看到的是整篇报道的完整叙事, ctx 轨只看到围绕目标银行实体的窗口文本。二者理应给出一致判断, 但由于全文里可能还夹杂着与目标银行无关的技术背景介绍, 或者实体窗口本身截断了关键的技术细节, 两轨标签会出现分歧, 而分歧本身携带信息: 它揭示了报道叙事在"整体技术定位"与"聚焦到具体银行时的技术定位"之间的不对称暴露。locus_disagree_frac、locus_freerider_frac、locus_quietworker_frac 三列正是把这种文章级的跨轨标签不一致现象聚合到 bank-year 面板, 成为 D4 (Decoupling Detection, 说做解耦探测) 残差信号族在 locus 维度上的具体实现, 与 subst (实质性/象征性) 维度的 F524 家族、collab (自主研发/外部协同) 维度的 F159 家族并列, 三者共用同一套跨轨比对逻辑但各自作用在不同的分类维度上。
【方法学与计算】
计算的第一步发生在文章级 (`encode_collab.py::derive_residual_signals`): 先对 full 轨与 ctx 轨的 innovation_locus 原始标签做归一化 (`_normalize_label`), 再用 `_both_valid_mask` 判定两轨标签是否都落在 canonical 集合 {底层技术, 应用场景} 内 (both_valid); 只有两轨都给出有效、可比较的标签, 该文章才进入分母域, 这一口径经 2026-06-11 的 omni-g-encode-collab-02 修复从"非空即可"收紧为"isin 白名单", 目的是保证下方三个不变式在构造上可证: (i) freerider + quietworker ≤ 1 互斥; (ii) freerider + quietworker == disagree 恒等 (由 both_valid 的白名单口径保证, 脏标签或非 canonical 值不会进分母, 从而不会推高 disagree 却不落进两个子类); (iii) 任一轨为缺失值或非 canonical 脏标签, 三个文章级布尔列全部记为 False 而非 NaN, 避免缺标签文章被系统性误记为"不分歧"。三个文章级信号的精确定义为: locus_disagree = (full 标签 != ctx 标签) 且两轨均 both_valid; locus_freerider = full 标签 == 底层技术 (基线) 且 ctx 标签 == 应用场景 (对照); locus_quietworker = full 标签 == 应用场景 且 ctx 标签 == 底层技术。直觉上, freerider 对应"通篇叙事描绘成底层技术布局, 但聚焦到该银行本身时其实只是应用场景层面的采购或合作" (说得比做得大), quietworker 对应反过来"整体叙事只当作一次应用场景报道, 但聚焦到该银行的实体窗口其实透露出底层技术自主投入的信息" (做得比说得多, 未被充分渲染)。第二步在面板聚合 (`aggregate_d4_panel`) 把三个文章级布尔列在 bank-year 分组内求和, 除以该组内 both_valid 文章数 n_bothvalid; n_bothvalid < 5 (含 0) 时三个 frac 列一律置 NaN, 该小样本门槛与文章级信号的 both_valid 分母域保持同一集合, 避免"分子有效域"与"分母物理域"错配造成的系统性下偏 (2026-06-11 omni-g-encode-collab-01 修复); 上游标签列若缺失导致无法重建 both_valid, 则回退到 legacy 的物理文章数分母, 并额外产出 n_articles_locus_bothvalid 供论文披露覆盖率。ss 轨 (银行∧金科同句窗口) 是纯情感轨, 不产 innovation_locus 属性标签, 因此本家族只比较 full 与 ctx 两轨, 不产 `_ss` 残差列, 这是刻意设计而非遗漏; 三条 frac 之间也不构成 over-identified 的同一识别策略, 三个分类维度 (subst/locus/collab) 各自 just-identified 并排, 互为稳健性、不分主次, 禁止混进同一 over-identified Hansen J。
【文献定位】
本家族的方法论根基是"说一套做一套"型解耦 (decoupling) 测度传统, 在治理与社会责任文献中已有系统梳理 (与本模块另行引注的 decoupling 综述同族); 具体到金融科技的 locus 二分框架, 直接取自 Gomber, Koch & Siering (2017, Journal of Business Economics) 对金融科技研究议程按底层使能技术与前台应用场景的划分, 后者在信息系统领域的组织逻辑分层思路可追溯到 Yoo, Henfridsson & Lyytinen (2010, Information Systems Research) 对数字创新分层组织逻辑的论述。跨轨标签不一致的构念定位则借鉴投资者/分析师分歧 (disagreement) 文献: Hong & Stein (2007, Journal of Economic Perspectives) 综述了分歧如何在股票市场中系统性地影响定价与交易量, Carlin, Longstaff & Matoba (2014, Journal of Financial Economics) 与 Cen, Wei & Yang (2017, Management Science) 分别在资产定价与反应不足框架下把分歧度量化为可预测收益的横截面变量, Li & Luan (2025, Review of Accounting Studies) 进一步把新闻文本衍生的分歧度量与股票收益相联系, 为本家族"用同一语料的不同取材范围衍生分歧信号"的思路提供了直接的方法论先例。跨评注者/跨口径标注不一致本身的度量传统另参 Uma, Fornaciari, Hovy, Paun, Plank & Poesio (2021, Journal of Artificial Intelligence Research) 对标注分歧建模的系统综述, 该文把"分歧"本身视为可建模信号而非噪声待去除, 与本家族把 full/ctx 分歧当作独立研究变量 (而非仅用于稳健性剔除) 的立场一致。

## VAR: locus_disagree_frac

【变体差分】
locus_disagree_frac 是 D4 locus 维度三条残差 frac 中的总量指标, 反映 bank-year 分组内 innovation_locus 标签在 full 轨与 ctx 轨之间"发生任何不一致"的文章占比, 不区分不一致的方向。分子是文章级布尔列 locus_disagree 在组内的求和, 该布尔列的判定条件是 full 归一化标签与 ctx 归一化标签不相等, 且两轨标签都通过 both_valid 校验 (即都落在 {底层技术, 应用场景} 这两个 canonical 取值内, 排除因模型未给出有效判断、验证未通过、或标签值本身不属于该维度取值域而导致的伪不一致)。分母是同一 bank-year 组内的 n_bothvalid, 与分子共享同一有效域, 这是 2026-06-11 修复后的口径要求, 修复前的实现曾用组内物理文章数做分母, 会把标签缺失的文章系统性地计入"未分歧"从而低估真实分歧率; 现口径下 n_bothvalid 本身也作为独立面板列 n_articles_locus_bothvalid 披露, 供读者判断该 bank-year 格的样本支撑是否充分。按不变式 (ii), locus_disagree_frac 在数值上恒等于 locus_freerider_frac 与 locus_quietworker_frac 之和 (因为二者互斥且并集即为分歧全集), 这意味着单独使用 locus_disagree_frac 只能捕捉"分歧发生了多少", 若要进一步区分分歧的方向性含义 (是叙事夸大技术定位, 还是叙事低估了技术定位), 须同时参照另两列。该列与 F524 (subst 维度) 及 F159 (collab 维度) 的同名 disagree_frac 列共享完全相同的构造逻辑, 仅分类维度与 canonical 取值集合不同, 三者是互为稳健性的并排测度, 不应合并进同一识别方程。n_bothvalid<5 的组会被置 NaN, 在生产 T=18 全量语料下预期绝大多数 bank-year 格有充分样本支撑, 但本机 T=2 dev 语料样本稀疏, 该列大概率呈现大量 NaN, 属预期退化而非缺陷。

## VAR: locus_freerider_frac

【变体差分】
locus_freerider_frac 是 locus_disagree_frac 的方向性子成分之一, 只统计分歧中"full 轨判定为底层技术 (基线, baseline)、ctx 轨判定为应用场景 (对照, contrast)"这一特定方向的文章占比, 分母同样是该 bank-year 组的 n_bothvalid。这一方向的直觉含义是: 整篇报道的叙事把该行业事件描绘成具有底层技术属性的创新 (例如提及自主研发的核心系统、算法或基础设施), 但当把视野收窄到围绕目标银行本身的实体窗口时, 报道实际呈现的只是该银行在应用场景层面的采购、接入或合作行为, 并未真正涉及底层技术投入。该现象被命名为 freerider ("搭便车"), 借用了组织行为学中免费搭车者利用集体叙事声誉却未实际承担相应贡献的隐喻——报道整体的技术形象被用于渲染, 但具体到该银行的可验证部分并不支持这一形象。这一方向性信号与本模块同族引注的解耦 (decoupling) 文献所关注的"言行不一"现象在结构上同构: 组织对外传递的整体叙事 (full 轨) 与聚焦到具体行动主体时可观察的实际内容 (ctx 轨) 出现系统性落差。需要强调, freerider 与 quietworker 在构造上严格互斥 (同一篇文章不可能同时满足两个方向的条件, 因为一篇文章的 full 标签与 ctx 标签是唯一确定的一对取值), 因此二者之和恒等于 disagree, 三列构成一个恒等式闭合的三元组而非三个独立自由度。分析时若发现某银行 locus_freerider_frac 系统性偏高, 提示其相关报道存在"技术形象被整体叙事拔高、但聚焦细节时证据不足"的模式, 这是一个描述性/探索性信号, 本身不预设因果方向, 亦不应与其余分类维度 (subst/collab) 的对应残差信号混入同一个 over-identified 识别方程, 三个维度各自 just-identified 并排、互为稳健性。

## VAR: locus_quietworker_frac

【变体差分】
locus_quietworker_frac 是 locus_disagree_frac 的另一个方向性子成分, 统计的是与 freerider 相反的方向: full 轨判定为应用场景 (对照)、ctx 轨判定为底层技术 (基线) 的文章占比, 分母同样是该 bank-year 组的 n_bothvalid。其直觉含义与 freerider 正好相反: 整篇报道的叙事只把事件当作一次常规的应用场景层面的报道 (例如渠道上线、产品接入等), 未在整体行文中特别强调技术属性, 但当聚焦到围绕目标银行本身的实体窗口时, 文本实际透露出该银行在底层技术层面确有实质投入的信息, 只是这部分信息未被整篇报道的宏观叙事充分渲染或强调。该现象被命名为 quietworker ("闷头干活者"), 借用了做了实事却未被充分宣传/披露的隐喻, 与 freerider 的"说得多做得少"方向相反, 构成"做得多说得少"。两者在 both_valid 域内互斥且并集恒等于 disagree, 因此 locus_quietworker_frac 单独观察时只能反映分歧总量的一半图景, 完整刻画分歧的方向性结构需要 disagree/freerider/quietworker 三列联合解读。与 locus_freerider_frac 相同, 该列的分母口径 (n_bothvalid, both_valid 定义见家族 CORE 节) 与分子共域, 小样本组 (n_bothvalid<5) 置 NaN; 该列与 F524 (subst_quietworker_frac) 及 F159 (collab_quietworker_frac) 是并排的、互为稳健性的同构测度, 分别作用于不同的分类维度, 不构成同一识别策略下可合并的重复变量, 使用时应分别报告而非取平均或加总跨维度混用。ss 轨不产该维度标签, 因此本列与 F410 家族整体一样只在 full/ctx 两轨间比较, 无 `_ss` 版本, 这与三轨情感测度族 (locus_disagree_frac 之外的多数量表) 的架构约定不同, 属该 D4 残差信号族的刻意设计。

<!-- rendered-citations:begin -->
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M. (2021). Learning from disagreement: A survey. Journal of Artificial Intelligence Research, 72, 1385-1470. https://doi.org/10.1613/jair.1.12752
Yoo, Y., Henfridsson, O., & Lyytinen, K. (2010). The new organizing logic of digital innovation: An agenda for information systems research. Information Systems Research, 21(4), 724-735. https://doi.org/10.1287/isre.1100.0322
<!-- rendered-citations:end -->
