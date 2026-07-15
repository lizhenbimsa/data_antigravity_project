---
family_id: LB004
columns:
- bert_avg_neu
- rule_ablation_variants_conceptual
- allv_anchor_carrier_conceptual
unit: 概念性说明列, 无独立数值量纲(依附于被删源列族本身各自量纲)
formula: "bert_avg_neu = 1 - bert_avg_pos - bert_avg_neg (三分类恒等, 允许残差不超过万分之一浮点误差); 词典规则消融变体与 canonical 口径相关系数介于 0.998 与 0.999 之间, 完整消融梯子经 pair 长表可零成本复现"
producer: company_listed_bank/pipeline/02_build_cooc_panel.py D17 章节(裁剪决策记录) 与 03_build_altweight_panels.py (七权面板同引擎继承)
upstream:
- news_process 40_panel_yearly.parquet (被删源列族原始取值, 供 D17 重构代码段消费)
- _company_bank_cooc_pairs.parquet (加权测度重构底料)
citations:
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: "What drives media slant? Evidence from U.S. daily newspapers"
  venue: Econometrica
  vol: 78
  issue: 1
  pages_or_artno: 35-71
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
- doi: 10.1080/19312450709336664
  type: journal
  authors: Hayes, A. F., & Krippendorff, K.
  year: 2007
  title: "Answering the call for a standard reliability measure for coding data"
  venue: Communication Methods and Measures
  vol: 1
  issue: 1
  pages_or_artno: 77-89
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
---

## CORE

本家族是主面板 D17 三义务段的独立长文承载, 覆盖三条互相独立但同属"裁剪决策预答"性质的说明: bert 中性概率恒等关系、词典规则消融相关性、以及被裁 allv 锚点构念的单载体归属。三条说明的共同动机是, 面板在构造过程中出于列数控制与冗余消除的考虑, 主动裁剪了一批可由其余保留列或由 pair 长表精确重构的候选列, 而这份长文正是为使用者预先解答"某个熟悉的列为何找不到"这一类问题。

bert_avg_neu 恒等说明的是三分类情感概率之间存在数学上的强约束, 中性概率理论上等于一减去正面与负面概率之和, 这一关系并非独立信息而是简单的算术推导, 面板因此不单独保留冗余的恒等列, 但特别提醒使用者三家 BERT 模型中有一家缺失中性类输出, 导致跨模型集成层混入了二分类与三分类两种不同宇宙, 使用时须避免直接把恒等关系当作跨模型可加验证的断言。词典规则消融相关性说明的是本项目对语言学规则族做全幂集消融后得到的多个变体, 彼此之间高度共线, 这一现象与情感分析文献中长期观察到的规则消融变体高度相关但非完全冗余的模式一致, 说明规则组合的边际信息量有限但仍具有诊断价值, 使用者应报告相关系数而非把消融变体直接并入同一可加分解式。allv 锚点构念说明的是某一跨轨聚合构念此前存在多个交叉臂版本, 现已收敛为单一载体承载, 目的是避免同一构念的多份重复度量在回归右侧被误用为独立解释变量, 这一收敛决策与媒体研究文献中反复强调的构念效度单一性原则相呼应, 避免研究者在不知情的情况下把同一潜在信号的多个测量误当作多重稳健性证据。

三条说明背后共享一个更一般性的方法论立场, 即面板列数的控制并非单纯的工程简化, 而是研究设计层面的主动取舍。政治敏感信息披露研究早已指出, 企业倾向于选择性地压制负面信息, 这一现象提示情感测度族本身即存在被操纵或被选择性观察的可能性, 因此任何冗余但貌似独立的测度重复出现在面板中, 都会放大研究者在多重检验情境下无意间挑选出显著结果的风险, D17 的裁剪逻辑正是对这一风险的事先防范, 通过在设计阶段就明确哪些列属于可推导冗余、哪些列属于独立信息增量, 把可加性假设的边界说清楚。词典规则消融族的高度共线现象也值得进一步说明其统计根源: 消融梯子中的各个变体共享同一份底层词典与同一套基础评分公式, 差异仅在于是否叠加否定翻转、程度副词或转折规则等局部语言学修正, 由于这些修正规则在实际文本中触发的频率相对基础词汇匹配而言占比有限, 各变体之间的边际差异天然被压缩, 相关系数因此普遍处于极高区间, 这一现象与媒体偏差测度文献中对多指标度量体系内部高度相关性的一般性观察相符, 使用者应将消融梯子理解为对某一构念稳健性的诊断工具集合, 而非彼此独立的多个假说来源, 报告时宜采用相关系数矩阵而非逐一罗列回归系数的方式呈现。

<!-- rendered-citations:begin -->
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. Communication Methods and Measures, 1(1), 77-89. https://doi.org/10.1080/19312450709336664
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
<!-- rendered-citations:end -->
