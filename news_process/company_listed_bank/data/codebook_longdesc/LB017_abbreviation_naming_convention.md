---
family_id: LB017
novelty_exempt_rationale: "该家族是dta 短名缩写命名规范的约定披露, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- dta_shortname_mapping_table_conceptual
unit: 概念性说明, 无独立数值量纲(依附于映射表所指全名列各自量纲)
formula: "无公式; 缩写规则 = 逐词根固定缩写映射(如 hidden→hid, adopt→adopt, intensity→int, allv 保留) 拼接, 供全名超出 Stata 变量名长度上限时降级使用"
producer: company_listed_bank/data/company_bank_cooc_panel_codebook.md D16 对照表节(手工维护, 随新列全名固化同步扩容)
upstream:
- company_bank_cooc_panel.dta (dta 短名实际落地载体)
- news_process 主项目同款缩写规则先例 (跨项目命名一致性来源)
citations:
- doi: 10.1145/360825.360855
  type: journal
  authors: Aho, A. V., & Corasick, M. J.
  year: 1975
  title: "Efficient string matching: An aid to bibliographic search"
  venue: Communications of the ACM
  vol: 18
  issue: 6
  pages_or_artno: 333-340
- doi: 10.2307/2529310
  type: journal
  authors: Landis, J. R., & Koch, G. G.
  year: 1977
  title: "The measurement of observer agreement for categorical data"
  venue: Biometrics
  vol: 33
  issue: 1
  pages_or_artno: 159-174
- doi: 10.1080/19312450709336664
  type: journal
  authors: Hayes, A. F., & Krippendorff, K.
  year: 2007
  title: "Answering the call for a standard reliability measure for coding data"
  venue: Communication Methods and Measures
  vol: 1
  issue: 1
  pages_or_artno: 77-89
- doi: 10.1137/S003614450342480
  type: journal
  authors: Newman, M. E. J.
  year: 2003
  title: "The structure and function of complex networks"
  venue: SIAM Review
  vol: 45
  issue: 2
  pages_or_artno: 167-256
- doi: 10.1287/mnsc.2023.03556
  type: journal
  authors: Fišar, M., Greiner, B., Huber, C., Katok, E., Ozkes, A. I., & the Management Science Reproducibility Collaboration
  year: 2024
  title: "Reproducibility in Management Science"
  venue: Management Science
  vol: 70
  issue: 3
  pages_or_artno: 1343-1356
---

## CORE

本家族覆盖缩写名与全名对照表的构造规则说明, 这份对照表解决的是变量命名系统内部的一个实务约束: Stata 变量名存在长度上限, 而本项目为保证可解释性, 面板列的全名往往由多个语义词根拼接而成, 例如某个衡量隐性采纳强度中位数的构念全名, 拼接了隐性、采纳、强度、中位数四个语义单元, 全名长度超出限制后必须降级为一个较短但仍可追溯的短名写入实际 dta 文件, 对照表正是全名与短名之间的双向映射 SSOT。

缩写规则采用逐词根固定映射的方式, 每个常见语义词根对应一个固定的英文缩写, 拼接顺序与全名保持一致, 这一设计的核心考量是可预测性与可逆性: 使用者见到短名中的某个片段, 应能根据固定映射表反查出对应的语义词根, 而不需要死记硬背每一个短名的具体含义, 这与实体名称匹配系统中依赖固定模式集合实现高效精确检索的设计哲学是相通的, 即用有限的、可枚举的映射规则集合覆盖尽可能广的命名空间, 而非依赖启发式或上下文相关的动态缩写。对照表的另一重要作用是保障跨项目的命名一致性, 本项目缩写规则刻意延续了主项目已经确立的同款缩写惯例, 使得熟悉主项目面板列命名习惯的使用者能够以较低的学习成本迁移到本侧线项目的面板结构上, 这一跨项目一致性设计与测量学文献中强调编码方案标准化以降低跨研究比较成本的原则相呼应。对照表本身是随新增列全名固化而持续扩容的活文档, 每当一批新列的全名超出长度限制, 相应的缩写映射即被追加进表格, 而非临时创造一次性的缩写, 这一维护纪律保证了短名体系的长期内部一致性, 类似于网络分析文献中对测度定义保持跨研究可比性的持续性要求。

缩写规则在具体设计时还须处理若干边界情形。当两个不同语义词根在缩写后恰好产生字符冲突时, 对照表并不允许静默地接受这一冲突, 而是要求维护者为其中一个词根引入区分性后缀或改用另一套不冲突的缩写形式, 这一冲突消解流程保证了短名到全名的映射始终保持单射性质, 即任意一个短名都能唯一还原出对应的全名, 不存在一个短名对应多个可能全名的歧义情形, 单射性质是短名体系能够被审计工具程序化验证的前提条件, 也是本项目在多个测度族命名体系中反复强调的硬约束。另一类边界情形出现在缩写词根需要跨越轨、权重版本、判据后缀等多重后缀同时拼接的复合列名场景, 此时对照表约定了固定的拼接顺序规则, 例如权重来源缩写通常置于语义主体之后而轨后缀置于全部结构之后, 这一顺序约定的价值在于, 使用者只需掌握一套顺序规则, 即可对任意复合列名做出正确的语义拆解, 而不需要针对每一种具体的后缀组合单独记忆拼接顺序。对照表的可维护性还受益于其与生成型代码路径解耦的设计, 缩写映射以静态表格形式存在而非嵌入生成脚本的条件分支逻辑中, 这一解耦使得对照表本身可以独立于生成代码接受审阅与版本控制追踪, 降低了命名规则漂移不被察觉的风险。

从更宏观的研究可信度视角看, 管理科学领域于 2024 年完成的大规模可复现性协作研究表明, 研究产物能否被他人成功复现, 很大程度上取决于数据与代码构件是否具备标准化、可追溯的命名与文档约定, 变量命名的随意性正是复现失败的高发源头之一; 本对照表把全名与短名的双向映射维护为单一权威源、并坚持逐词根固定缩写而非临时缩写, 正是把这一可复现性要求落实到变量命名层面的工程纪律。

<!-- rendered-citations:begin -->
Aho, A. V., & Corasick, M. J. (1975). Efficient string matching: An aid to bibliographic search. Communications of the ACM, 18(6), 333-340. https://doi.org/10.1145/360825.360855
Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310
Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. Communication Methods and Measures, 1(1), 77-89. https://doi.org/10.1080/19312450709336664
Newman, M. E. J. (2003). The structure and function of complex networks. SIAM Review, 45(2), 167-256. https://doi.org/10.1137/S003614450342480
Fišar, M., Greiner, B., Huber, C., Katok, E., Ozkes, A. I., & the Management Science Reproducibility Collaboration. (2024). Reproducibility in Management Science. Management Science, 70(3), 1343-1356. https://doi.org/10.1287/mnsc.2023.03556
<!-- rendered-citations:end -->
