---
family_id: TB015
columns:
- data_lineage_disclosure
- redistribution_downgrade_path
unit: 无量纲 (谱系与许可披露段, 非独立数值列)
formula: "税调名单(政府调查数据)与权源dta(商业数据)均恒不入库; 派生聚合面板可分发, 名单/行级长表按需申请的降级路径; 谱系七字段(数据商/数据库名与表编号/版本/获取日期/提取过滤条件/许可条款/第三方获取路径)核定DEFERRED至生产机轮"
producer: company_tax_bank/pipeline/02_build_cooc_panel.py + 03_build_altweight_panels.py (T-D19①/T-D20 数据谱系段生成分支)
upstream:
- config/company_tax_names.yaml (税调企业名单, 政府调查数据保密性来源)
- config/银行业金融机构基本信息表.dta (603,907行商业数据权源, 不入库)
citations:
- doi: 10.1214/24-STS939
  type: journal
  authors: Kamat, G., & Gutman, R.
  year: 2026
  title: "Analysis of linked files: A missing data perspective"
  venue: Statistical Science
  vol: 41
  issue: 1
  pages_or_artno: ""
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
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

## VAR

税调企业银企共现面板的数据谱系披露比上市公司体系更为尖锐, 根本原因在于其两个核心输入源都不属于普通商业可得数据。税调企业名单本身是政府调查数据的派生产物, 保密性要求远高于面向公众的上市公司名录, 权源银行网点信息表虽属商业数据库产品, 但同样因授权条款限制无法随意再分发; 两者共同构成本项目全部输出物中外部可复现性最弱的一环, 若脱离这两个源头数据, 完整重跑本管线在外部环境中并不可行。基于这一现实约束, 本项目为不同产物设定了差异化的分发地位: 已经完成聚合脱敏的企业年面板本身可以正常分发, 因为聚合过程本身已经抹除了逐条原始记录的可识别性, 但更细粒度的名单本身以及行级别的共现长表, 由于直接暴露企业与银行之间未加总的关系细节, 采用按需申请的降级分发路径, 而非默认随复现包一并公开。

这一分级分发策略的方法论依据可以从两个方向理解。其一, 关联档案分析的缺失数据视角框架系统论证了跨源关联数据在缺乏原始明细的情况下依然可以通过恰当设计的中间产物实现有限但充分的可复现性, 本项目选择随复现包附带 pair 长表与双权长表作为原始名单与权源数据不可得情形下的代偿方案, 正是这一思路的具体落地, 使外部研究者即便无法访问受限的原始名单, 依然能够验证聚合面板的构造逻辑是否正确执行。其二, 探讨政治敏感信息如何在中国企业媒体环境与监管情境中被处理的相关研究揭示, 涉及政府调查数据与企业敏感信息的实证研究普遍面临数据可得性与研究透明度之间的张力, 完整披露谱系细节, 即便部分字段因授权条款限制暂未能核定生产环境下的具体版本与获取日期, 也应当以占位声明的方式明确标注延迟核定的状态而非彻底略去, 这一做法与媒体覆盖度测度研究强调构造过程透明是测度可信度基础的立场相呼应。谱系七字段核定工作被明确延后至生产语料机执行轮次完成, 复现包使用者在此之前应将本条目视为过渡态披露, 待生产机轮回填后以更新版本为准。

分级分发策略在实际执行中还须区分两类完全不同的"不可分发": 一类是法律与授权层面的硬约束, 例如税调名单作为政府调查数据其保密义务不因研究目的正当而自动豁免, 另一类是纯粹的商业授权限制, 例如权源银行网点信息表虽不涉及政府保密要求, 但其商业数据库许可条款同样禁止随意再分发给授权范围之外的第三方, 两类限制虽然性质不同, 但在本项目的处理效果上是一致的, 即两者均恒不入库、不随复现包公开。使用者若需要访问受限的原始名单或权源明细数据, 应当通过按需申请的正式渠道单独获取授权, 而不能以复现包本身已经包含企业年聚合面板为由, 推定自己已经默认获得了访问更细粒度数据的权利, 这一区分对于遵守数据提供方的授权条款、避免研究团队因数据使用不当而承担法律或合规风险至关重要, 也是本条目将谱系与许可两个看似独立的主题合并在同一段披露中呈现的根本原因, 二者共同构成使用者在触碰本项目底层数据源之前必须完整理解的前提性约束。

<!-- rendered-citations:begin -->
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
<!-- rendered-citations:end -->
