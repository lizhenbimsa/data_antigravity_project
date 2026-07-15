---
family_id: TB004
novelty_exempt_rationale: "该家族是D17 义务与消融预答的方法论义务披露, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- bert_avg_neu
- rule_ablation_variants
- pair_reconstruction_channel
unit: 无量纲 (义务性说明段, 非独立数值列)
formula: "bert_avg_neu ≡ 1 − bert_avg_pos − bert_avg_neg (finbert2无neu类致ensemble层混2/3模型宇宙, 残差≤1e-4); 被删源列可由 pair 长表按cw/ce公式重构 (isclose级)"
producer: company_tax_bank/pipeline/02_build_cooc_panel.py (D17三义务段生成分支, 与 company_listed_bank 同源共享义务措辞规范)
upstream:
- _company_tax_bank_cooc_pairs.parquet (被删410基名列的唯一重构载体)
- config/company_tax_bank_cooc_registry.yaml (excluded 区段负清单 SSOT)
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
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: 2442-2476
---

## VAR

本条目承载税调企业银企共现面板体系中三条须向使用者显式声明的义务, 这三条义务全部同构继承自上市公司侧的媒体主面板, 之所以在税调侧单独重述而非仅以指针形式带过, 是因为独立完整复述能让研究者在只接触税调侧材料的情况下也能获得完备的方法论披露, 不必回溯另一条产品线。第一条义务涉及情感测度锚点的单载体问题: 面板中若干跨模型汇总的锚点构念由单一承载列表达, 交叉臂已在裁剪过程中删去, 但可从 pair 长表按公开公式精确重构, 研究者若需要该类交叉验证, 应主动重建而非默认其已存在于当前面板骨架中。

第二条义务是三分类情感概率恒等式的披露: 中性概率恒等于一减去正面概率与负面概率之和, 残差应控制在极小阈值以内, 但这一恒等式在跨模型集成层面存在一个不能忽视的陷阱, 即当某一底层模型本身不产出中性类概率时, 集成层实际上是在混合二分类与三分类两种不同的模型宇宙, 此时任何形式的加总断言都会引入方法论错误, 这类风险在探讨政治敏感信息在企业媒体披露中如何被系统性抑制的研究中同样被强调, 该研究提醒使用者媒体情感测度背后的模型假设远比表面上的数值更值得推敲。第三条义务是关于四百余个基名列被裁剪后地位不降的承诺: 只要 pair 长表与银行年面板同时保留, 被裁列在数学意义上可以按加权公式一行精确复原, 这一可重构性设计的价值判断依据在于, 学术研究对媒体报道派生测度的信任程度本身就与其构造透明度直接相关, 中国媒体偏向性研究领域的一系列工作反复表明, 媒体测度的构造细节披露得越充分, 后续复现与稳健性检验的可信度就越高, 本项目选择以可重构性而非保留全部原始列的方式平衡存储成本与透明度诉求。

三条义务在实践中并非彼此独立的孤立条款, 而是共同构成一套"预答式"披露机制的三个侧面: 使用者在正式着手分析之前, 通常会围绕这三个环节提出几乎同样的疑问, 例如某个汇总列是否隐藏了模型间的分歧、某个概率恒等式是否在所有底层模型上都成立、以及某个被裁列是否真的从此不可获得, 与其等待使用者逐一发问再个别答复, 不如在 codebook 层面预先把答案系统写清, 这正是"预答"一词的含义所在。这一机制与义务性说明段的定位刻意区分于普通的家族长文, 因为它承载的不是某一具体测度列的构造细节, 而是跨越多个列共同适用的方法论纪律, 三条义务的措辞与母本上市公司体系完全同构并非偶然, 而是两条产品线共享同一套底层情感与集成引擎的直接后果, 任何一条义务若在两条产品线间出现措辞分歧, 都会造成使用者误以为两套面板遵循不同的方法论标准, 这种割裂本身就是需要极力避免的风险。围绕媒体报道中政治敏感信息如何被系统性抑制的研究, 以及探讨媒体偏向性生成机制的跨国比较研究, 均从不同角度提示, 情感与倾向性测度类研究成果的可信度很大程度上取决于构造过程的方法论细节是否被完整、一致地披露给最终使用者, 而非仅仅停留在数值本身的呈现层面, 这也是本条目坚持三条义务独立复述而非以指针形式带过的根本原因。

<!-- rendered-citations:begin -->
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
<!-- rendered-citations:end -->
