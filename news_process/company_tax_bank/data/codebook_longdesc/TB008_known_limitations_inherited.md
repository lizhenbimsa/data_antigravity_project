---
family_id: TB008
novelty_exempt_rationale: "该家族是继承自母管线的已知局限披露, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- n_docs
- n_docs_frac
- cooc_wt_base_full
unit: 无量纲 (局限披露段, 非独立数值列)
formula: "显式声明继承母本company_listed_bank §7通用局限 (非默认继承): 名录灌水/variant子串重叠双计/大小写敏感/联播稿权重放大/覆盖自选择/多重检验负担等十二条"
producer: company_tax_bank/pipeline/02_build_cooc_panel.py (§7 已知局限段生成分支, 母本通用部分)
upstream:
- company_listed_bank/data/company_bank_cooc_panel_codebook.md (§7 通用局限措辞源头, 独立复述非指针引用)
- _company_tax_bank_cooc_pairs.parquet (n_docs_frac 子串重叠双计诊断来源)
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

## VAR

除税调数据特有的七条局限外, 税调企业银企共现面板还显式声明继承母本上市公司体系已经披露的一整套通用局限, 之所以强调"显式声明继承"而非任其默认成立, 是因为两条产品线虽然共享同一套加权引擎与同一套匹配逻辑, 但其数据源头, 也就是税调企业名单与上市公司名单, 在覆盖范围与灌水动机上并不完全相同, 继承关系需要经过审视而非想当然地照搬。第一类继承局限涉及企业名录本身的质量问题, 部分企业名称或简称可能出现在通稿式报道或名录灌水式内容中, 造成人为拉高的共现计数, 本项目刻意不设硬性剔除阈值, 而是将相关诊断信息写入日志供分析端自行判断, 这一处理立场与媒体倾向性测度文献中反复强调应对文本数据构造过程保持透明的方法论态度一致, 该文献的核心论点在于媒体测度是否可信取决于其构造细节能否被完整还原, 而非取决于是否做了看似严谨实则武断的裁剪。

第二类继承局限是变体重叠导致的双重计数问题, 一部分变体在企业之间存在字符串子串关系, 也存在银行与企业名称之间的子串重叠对, 这类重叠会导致同一篇报道被计入多个企业或多个银行, 本项目采取保守口径记录该类重叠对数, 而不试图算法性地消解全部重叠, 这一保守取向的理论支撑来自观察者间一致性测量框架, 该框架强调在编码规则本身存在歧义空间时, 保守记录优于强行统一的武断规则。第三类局限涉及全文轨联播稿现象: 同一篇通稿在多个媒体渠道联合播发会造成全文轨权重被系统性放大, 同时使集中度测度出现假分散的表观现象, 这一现象与探讨政治敏感信息在中国企业媒体环境中如何被系统性处理的研究所描述的媒体生态特征相呼应, 该研究揭示的媒体报道生成机制本身即存在渠道间高度同质化的结构性特征。其余继承局限还包括企业侧覆盖的自选择性质、变体快照的非逐年生效、加权测度银行覆盖缺口以及多重检验负担等, 均与母本上市公司体系的披露内容同构, 分析端在两条产品线间做横向比较时应对此保持一致的审慎态度。

之所以要在税调侧的 codebook 中把母本已经披露过的通用局限逐条重新写出而不是简单标注"参见母本文档", 除了让读者无需跨产品线来回查阅之外, 还有一个更深层的方法论考虑: 两条产品线共享同一套加权引擎并不意味着每一条通用局限在两侧的量级或影响方向完全一致, 通稿式联播稿现象在税调企业名单中的具体表现可能因企业本身媒体曝光度普遍低于上市公司而有所减弱, 但县域集中的中小企业在地方性媒体中出现批量通稿的概率反而可能因地方媒体资源集中而有所上升, 这类量级差异需要使用者结合具体研究样本自行评估, 而非默认母本体系的经验量级可以直接套用到税调体系。多重检验负担这一条局限尤其值得在税调侧单独强调, 因为加权测度通式可覆盖的候选源列数量本身已经十分庞大, 叠加双替代权与三文本轨的组合后, 潜在可检验的假设数量进一步膨胀, 探讨政治敏感信息处理机制的相关研究提醒, 大规模测度族群若不辅以恰当的多重检验校正或预先声明的主口径限定, 极易在事后挑选出若干偶然显著的结果并误读为稳健发现, 这一风险在税调侧因组合规模更大而更为突出。

<!-- rendered-citations:begin -->
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310
<!-- rendered-citations:end -->
