---
family_id: TB014
columns:
- excluded_columns_reason_code
unit: 无量纲 (排除列审计说明表, 计数为列数)
formula: "registry excluded 区段按理由代码分类汇总: D15_1_PEER/D15_2_IV/D15_3_MOMENT/D15_4_Z/D15_5_GAP/D15_6_INTERACT/D15_7_DIAG/D15_8_ALIAS/D15_9_LAG_EVENT/D15_10_ENV_STATIC/D15_11_INVARIANT/DUP_OF_40/KEY/TEXT, 逐列明细共5,324条"
producer: config/company_tax_bank_cooc_registry.yaml (excluded 区段 SSOT, 与 company_listed_bank 共用同一份 CUT_LIST v23)
upstream:
- news_process 40_panel_yearly.parquet (候选源列全集, excluded 判定的输入宇宙)
- company_listed_bank/config/company_bank_cooc_registry.yaml (CUT_LIST v23 共用来源, 独立复述非指针引用)
citations:
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.2308/JFR-2021-003
  type: journal
  authors: Breuer, M.
  year: 2022
  title: "Bartik instruments: An applied introduction"
  venue: Journal of Financial Reporting
  vol: 7
  issue: 1
  pages_or_artno: 49-67
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: "Journal of the Royal Statistical Society Series A: Statistics in Society"
  vol: 187
  issue: 3
  pages_or_artno: 748-771
---

## VAR

排除列审计表是理解本面板"为何某些理论上可构造的加权测度列没有出现在最终产物中"的关键说明性材料。加权测度构造通式原则上可以对银行年层面任意非缺失数值列生成对应的企业年加权测度, 但这会导致组合爆炸式的列数膨胀, 因此登记表 SSOT 引入一整套排除理由代码体系, 对不适合参与加权测度构造的候选源列逐一分类剔除, 剔除决策与理由代码全部记录在案, 使用者可以逐条查阅任何一个被排除列的具体理由而非仅得到一个"未出现"的空白结果。理由代码体系覆盖多个方法论维度, 数量最大的一类是与银行年面板内部已有测度高度重复的列, 其次是同伴效应类、工具变量类、矩估计类、标准化残差类、缺口诊断类、交互项类、诊断辅助类、别名类、滞后事件类、环境静态类以及不变量类等十一个细分理由代码, 再加上与主面板存在重复以及纯键值列与纯文本列两类结构性排除。

这套排除逻辑之所以要与工具变量类和同伴效应类理由代码单列出来重点强调, 是因为份额加权工具变量识别框架的系统梳理明确指出, 工具变量构造对候选变量的选择有着比普通描述性测度更严格的外生性要求, 若把银行年面板中本身已经带有工具变量或同伴效应性质的列不加区分地纳入通式并构造出对应的企业年加权版本, 极易在下游分析中制造出看似独立实则高度共线甚至循环论证的变量组合, 应用导向的份额加权工具变量方法综述进一步强调, 实践中构造份额加权测度时应对每一类候选源列的方法论属性保持警觉, 而不能仅凭数值列这一形式特征就默认其适合参与加权。放松份额加权工具变量识别中排除性约束的相关研究同样提示, 即便某个候选列表面上不属于工具变量本身, 若其构造过程与既有的加权份额结构存在隐藏关联, 仍可能污染后续估计的识别假设, 本项目的排除列审计表正是为提前拦截这类风险而设置的结构性防线, 与银行年主面板共用同一份负清单确保两条产品线在排除逻辑上的一致性, 避免同一候选列在不同产品线间出现互相矛盾的取舍决策。

超过五千条的排除列明细规模本身也传递出一个重要的方法论信息: 加权测度通式若不加约束地覆盖银行年面板全部候选源列, 潜在可构造的企业年测度列数量将是数以千计的量级, 这一规模远超任何单篇实证论文实际能够消费或恰当解释的范围, 排除列审计表的存在因而不仅是方法论透明度的体现, 也是一种主动的范围收窄机制, 帮助使用者把注意力集中在真正适合参与加权测度构造的核心源列子集上。审计表按理由代码分类汇总的呈现方式, 使得使用者可以按照自己的研究关切快速筛选相关的排除条目, 例如若研究设计本身涉及工具变量构造, 可以专门查阅工具变量类理由代码下的全部条目, 逐一核实这些被排除的候选列是否恰好是研究者原本打算使用的变量, 从而在动手建模之前就预先排除潜在的识别陷阱, 而不必等到回归结果出现异常后再回溯排查, 这一前置排查思路与份额加权工具变量方法综述倡导的"构造阶段即嵌入方法论审查"的实践建议是一致的。

<!-- rendered-citations:begin -->
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Breuer, M. (2022). Bartik instruments: An applied introduction. Journal of Financial Reporting, 7(1), 49-67. https://doi.org/10.2308/JFR-2021-003
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
<!-- rendered-citations:end -->
