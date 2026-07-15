---
family_id: LB016
columns:
- deliberately_not_done_ladder_conceptual
unit: 概念性说明, 无独立数值量纲
formula: "无公式; 八条刻意不做条目逐条附一句话理由, 供质疑时人工复核触发梯子扩容评估"
producer: company_listed_bank/data/company_bank_cooc_panel_codebook.md 替代聚合面板章"刻意不做"节(手工维护)
upstream:
- frozenw/mainbankw 已实现口径 (对照基线)
- pair 长表 (声明"可 $0 重构"条目的技术依据)
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
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
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
---

## CORE

本家族覆盖替代聚合面板刻意不做清单的完整展开说明, 这份清单记录的是在设计 frozenw 与 mainbankw 两种聚合臂时经过评估后主动放弃的候选构造方案, 每一条均附有一句话理由, 目的是防止使用者或审阅者反复提出已被评估过的替代设计, 同时也为未来若有新证据表明有必要时预留了扩容评估的触发点。

八条条目大致可归为三类动机。第一类是与已有臂功能高度重叠的候选设计, 例如广义工具变量式的份额差分构造, 由于该框架依赖特定的因子结构假设, 与本项目已有的份额乘冲击设计在识别逻辑上分属不同估计框架, 需要另立门户而非简单并入现有梯子; 又如严格意义上的留一法测度, 真正的留一法须回到文章级别重新计算, 而本项目上游已在构造阶段对自身银行做了排除处理, 窄版留一效应已被天然覆盖, 不再需要额外实现。第二类是与现有构造回答同一威胁但被判断为冗余的候选设计, 例如关系存量随时间衰减的加权方案, 这类衰减权重设计所要回应的识别顾虑与基期冻结方案高度相似, 在没有实证证据表明衰减权重能提供额外增量信息之前, 属于先验判断下的冗余梯子, 质疑时应通过 pair 长表实测衰减权重与冻结权重的相关性来决定是否值得扩容。第三类是被禁止的交叉组合, 例如冻结基期与主办行两种聚合逻辑本身正交, 二者的交叉臂会引入难以解释的复合识别假设, 属于梯子设计原则上明确禁止交叉的情形。份额乘冲击类识别设计的方法论文献近年持续演进, 从最初的初始份额工具变量构造, 到对非随机暴露与排除性约束放松的更细致讨论, 这些进展为未来重新评估当前刻意不做清单提供了持续更新的参照系, 使用者若在这些前沿讨论中发现足以推翻当前判断的新证据, 应通过明确的实证检验而非先验直觉来触发扩容。

刻意不做清单的维护机制本身也是一项值得说明的治理设计。每当有新的候选替代聚合方案被提出, 无论来自内部审阅还是外部使用者反馈, 该方案首先会被归入三类动机之一并评估是否与现有臂功能重叠、是否回应已被覆盖的识别威胁、或是否触犯已知的交叉组合禁令, 只有当候选方案被确认既不重叠也不冗余且不违反禁令时, 才会进入正式的扩容评估流程, 这一前置筛查机制的目的是防止聚合臂数量在缺乏充分论证的情况下无序膨胀, 每新增一支聚合臂都意味着使用者需要额外理解一套识别假设与一套局限清单, 过度膨胀的聚合臂谱系反而会降低整个替代聚合体系的可用性与可解释性。清单中被放弃的候选方案并非被永久否决, 而是被降级为"当前证据不足以支持实现"的状态, 这一区分至关重要: 若未来生产语料规模扩大或新的方法论文献提供了更充分的理论支持, 相应候选方案完全可能被重新评估并转正为正式实现的聚合臂, 使用者若认为某一被列入清单的方案对自身研究问题具有不可替代的价值, 建议的做法是先利用 pair 长表自行做小规模的探索性重构, 用实证结果反映实施该方案的边际价值, 再据此向维护者提出正式的扩容申请, 而非仅凭理论推测主张该方案应当被纳入。

<!-- rendered-citations:begin -->
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. The Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
<!-- rendered-citations:end -->
