---
family_id: LB002
columns:
- company
- bank
- year
- track
- n_docs
- n_docs_v
- n_docs_strict
- n_docs_frac
- n_docs_frac_v
- n_docs_longhit
unit: 计数列均为整数(篇数); n_docs_frac/n_docs_frac_v 为分数计数, 非负实数, 上界为该(公司,年,轨)去重报道篇数
formula: "n_docs(company,bank,year,track) = 去重共现篇数(不门控); n_docs_v = 限llm_verified_full==True 子集的篇数; n_docs_strict = ss 轨剔除 ss_is_fallback 报道后的篇数, full/ctx 轨恒等填充 n_docs; n_docs_frac = 该篇按 1/k 分摊, k = 该篇该公司该轨去重有效银行数(同篇涉及多家银行时避免整数计数重复计入总量); n_docs_frac_v = 分数计数的 verified 门控版本(未验证行计 0); n_docs_longhit = 该(公司,银行,年,轨)下存在任一四字及以上 variant 命中的篇数"
producer: company_listed_bank/pipeline/02_build_cooc_panel.py (公司乘银行乘年乘轨共现聚合引擎, 中间产物先落 pair 长表再向上聚合为主面板固定列)
upstream:
- news_process 21_tone_llms_full.parquet (报道乘目标银行全宇宙表, 含 llm_verified_full 验证旗标)
- company_listed_names.yaml (上市公司全称与曾用名 variant 主清单, AC 自动机匹配 SSOT)
citations:
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: 2442-2476
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
---

## CORE

本家族覆盖 pair 长表即 company_bank_cooc_pairs 的十个列, 这张表是公司乘银行乘年乘轨的最细粒度共现记录, 也是主面板全部固定列与全部加权测度列被删源列可精确重构的唯一底料。表的行单位是一次公司与银行在某年某轨下的共现关系, 而非报道本身, 因此同一篇报道若涉及多家银行, 会在表中拆分为多行。

十列可分三组理解。身份组由公司、银行、年、轨四列构成主键, 银行取自银行名主清单的规范名, 轨含全文、实体窗与同句三种文本处理口径。计数组由 n_docs 到 n_docs_longhit 共六列构成, 其中 n_docs 是权重侧使用的不门控原始计数, n_docs_v 是测度侧使用的验证门控计数, 二者刻意分裂对应主面板的门控双宇宙设计。n_docs_strict 只在同句轨有实质意义, 用于剔除因缺乏严格同句共现而回退到全文语境的报道。n_docs_frac 与 n_docs_frac_v 引入分数计数, 目的是修正同一篇报道涉及多家银行时整数计数会重复放大总量的问题, 这一分摊思路借鉴了媒体覆盖度量文献中对多主体共同出现事件的标准化处理惯例, 即事件本身只应计入总量一次, 涉及主体越多则每一主体分摊的份额越小。n_docs_longhit 提供了一个基于变体长度的精度稳健工具, 短名匹配存在较高的假阳性风险, 而四字及以上的公司简称命中在人工抽样核验中表现出显著更高的准确率, 因此该列可作为剔除短名噪声后的保守口径。

pair 表的另一重要角色是重构通道: 由于主面板对被删的源列族只保留加权测度结果而不保留中间过程, 使用者若需要审计或复现某一具体测度的加权构造, 可以直接用 pair 表与银行乘年面板做一次显式的合并计算, 精确还原出与主面板列逐位一致的数值, 这一设计既节省了存储空间, 又保留了完整的可追溯性, 呼应了媒体研究文献中反复强调的透明度与可复现性原则。

三轨并存这一设计在 pair 表层面尤其值得展开说明。全文轨、实体窗轨与同句轨三种文本处理口径在共现判定的严格程度上依次递增, 全文轨只要求公司与银行的名称在同一篇报道全文中同时出现, 实体窗轨要求二者出现在以命中位置为中心的局部窗口内, 同句轨则要求二者出现在严格意义上的同一句话中。三轨并非互相替代关系, 而是刻意设计为互为稳健性的并排测度, 这一设计哲学与本项目在其他多个测度族中反复应用的三轨范式一致, 目的是让使用者能够观察某一实证结论对共现判定严格程度的敏感性: 若某一系数在三轨下方向一致、显著性稳健, 则说明结论不依赖于对共现邻近程度的具体假设; 反之若仅在宽松的全文轨下显著, 而在严格的同句轨下消失, 则提示该结论可能部分来自报道中公司与银行虽同篇出现但实质上并无紧密关联的噪声共现。同句轨在实践中面临的一个已知约束是, 当一篇报道确实不存在严格同句共现时, 引擎会按既定的回退规则退回全文文本, 并以专门的旗标标记该行属于回退情形, 使用者在对同句轨做严格解读时应先按该旗标过滤, 否则会把回退产生的全文语境误当作真实的同句证据纳入分析, 这一回退语义与本项目在新闻主项目中对同类三轨架构的既有实现完全对称, 保证了跨项目口径的一致性。

<!-- rendered-citations:begin -->
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Aho, A. V., & Corasick, M. J. (1975). Efficient string matching: An aid to bibliographic search. Communications of the ACM, 18(6), 333-340. https://doi.org/10.1145/360825.360855
Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310
<!-- rendered-citations:end -->
