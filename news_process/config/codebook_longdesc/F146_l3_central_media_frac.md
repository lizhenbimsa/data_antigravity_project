---
family_id: F146
columns:
- central_media_frac
unit: 比率/占比 (proportion, 值域 [0,1]; 银行-年内中央级媒体报道篇数占比)
formula: "central_media_frac(bank,year) = mean_over_articles( 1[媒体(中文) ∈ CENTRAL] ); CENTRAL = media_classification.json['central_media']; 按 (target_bank, year) 分组求 _is_central 指示变量的组内均值"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (维度④) ; news_process/pipeline/panel/export.py (标签落地)
upstream:
- "24_herd_decay.parquet (article-level df_exploded: stage-21 full-only verified 留篇集; 提供 target_bank / year / 媒体(中文))"
- config/media_classification.json (central_media 名单)
citations:
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: 1145-1182
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics and Finance
  vol: 91
  issue: ""
  pages_or_artno: 1150-1172
- doi: 10.1016/j.ememar.2024.101234
  type: journal
  authors: Xu, Z., Hua, X., & Zhang, T.
  year: 2025
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  venue: Emerging Markets Review
  vol: 64
  issue: ""
  pages_or_artno: 101234
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: "The media and the diffusion of information in financial markets: Evidence from newspaper strikes"
  venue: The Journal of Finance
  vol: 69
  issue: 5
  pages_or_artno: 2007-2043
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: "What drives media slant? Evidence from U.S. daily newspapers"
  venue: Econometrica
  vol: 78
  issue: 1
  pages_or_artno: 35-71
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
new_dois: []
---

## CORE

【构念与来源】
central_media_frac 度量的是单家银行在某一年度所收到的全部媒体报道中, 来自中央级 (national/央属) 媒体的报道所占的篇数比例。它属于面板媒体异质性 (media heterogeneity) 指标族中的一条行政层级 (administrative-tier) 占比测度, 由生产函数 compute_media_heterogeneity 的"维度④: 中央级 vs 地方级"分支产出, 与同族的财经/综合内容分类 (维度①②③)、官方/市场化主办属性分类 (维度⑤⑥) 在构念上刻意保持正交。构念的直觉是: 在中国的媒体制度中, 媒体来源的行政层级是新闻可信度、议程设置权与信息穿透力的一个结构性代理——中央级党报党刊与央属通讯社通常具有更强的权威背书、更广的跨地域发行覆盖, 以及更接近监管与政策口径的报道立场; 而地方级媒体则更贴近属地商业利益与本地广告主, 报道偏斜的可能性更高。因此, 一家银行的报道来源结构中中央级占比越高, 大体反映其被置于全国性视野下审视、其新闻更可能被跨地域投资者与监管者观察到。数据来源上, 每篇文章的媒体归属取自文章级字段"媒体(中文)", 中央级名单来自 config/media_classification.json 的 central_media 键 (在生产日志中回显为"中央级: N 家")。该名单与财经/综合内容分类正交——源码在装载后专门记录"财经/综合 ∩ 中央级"的交叉家数并说明这属正交分类的合理重叠, 即一家媒体既可是财经类内容取向、又可是中央级行政层级, 两套判据互不排斥。

【方法学与计算】
计算在文章级 DataFrame 上分两步落地; 该输入 DataFrame 是由上游 24_herd_decay 阶段炸开 (df_exploded) 得到的 stage-21 full-only verified 留篇集, 携带 target_bank、year 与篇级"媒体(中文)"来源名等字段, 并非 stage 40 之后的银行-年下游产物 40_article_bank_level (后者是 stage 51 falsification 的输入, 位于本列产出之后, 与本列无 DAG 上的输入关系)。第一步构造行政层级指示变量: df['_is_central'] = df['媒体(中文)'].isin(CENTRAL).astype(int), 即逐篇判断该篇报道的媒体名是否命中中央级名单, 命中记 1、否则记 0; 生产日志随即回显中央级篇数及其在全样本文章中的占比。第二步按银行-年聚合: 以 (target_bank, year) 为分组键对 _is_central 求组内均值 (groupby(...).mean()), 得到 central_media_frac, 再以左连接并入银行-年面板。由于取的是 0/1 指示变量的均值, 结果天然落在 [0,1] 闭区间——生产函数在收尾校验中显式把 central_media_frac 纳入占比值域 [0,1] 的断言清单, 与 fin_media_frac、comp_media_frac、official_media_frac 等姊妹占比列一同守护。分母口径与全族占比一致, 是该银行-年内进入留篇集的报道总篇数; 依 2026-06-29 起生效的 full-only 留篇门控, 一篇报道是否算作"银行金科报道"仅由 full 轨的 LLM 判定决定, 故此处分母与全局 n_articles 口径对齐, ctx/ss 轨不参与分母定义。一个关键的构念属性是: central_media_frac 是一条 track-agnostic 的元数据度量——它只依赖媒体来源名这一篇级元数据, 与文章正文的三轨 (full/ctx/ss) 文本无关, 因此不存在 _full/_ctx/_ss 孪生列, 也没有 co-primary 双轨嵌入的 _lg 孪生; 这与本族中依赖情感打分的 tone_central_media_full/_ctx 列 (那些才分轨) 形成对照。作为规格稳健性维度, 行政层级占比与内容分类占比、主办属性占比属于并排的、互为稳健性、不分主次的替代性媒体异质性刻画: 各自 just-identified 并排进入分析, 禁混进同一 over-identified 的 Hansen J 检验, 以避免把语义正交的异质性维度错误地捆入同一组过度识别约束。

【文献定位】
把媒体来源结构当作可测协变量的做法, 根植于金融媒体经济学的一支实证传统。Peress (2014) 借助报业罢工这一外生冲击, 证明媒体作为信息扩散渠道对交易量与价格发现具有因果性的实际作用, 为"媒体覆盖的构成与强度会改变市场信息环境"这一前提提供了识别层面的支撑。Gentzkow 和 Shapiro (2010) 系统刻画了报纸媒体的立场 (media slant) 及其被受众与所有权结构驱动的机制, 说明不同来源的媒体在报道倾向上具有系统性差异, 这正是把媒体按类型/层级切分并分别度量占比的理论前提。在中国制度语境下, You、Zhang 和 Zhang (2018, RFS) 直接考察了"谁掌握了媒体之笔的权力", 揭示了官方/央属媒体与市场化媒体在报道立场与市场影响上的分野, 是本族区分行政层级与主办属性维度的核心构念锚。晚近文献进一步验证了官方/央属媒体口径在中国资本市场的独立信息含量: Xu、Hua 和 Zhang (2025) 发现官方媒体情感对股市有可测的影响, Fang 等 (2024) 在中国银行样本上刻画了媒体情感对存款稳定与银行系统性风险的作用, 与本项目银行-年层级的研究对象高度同域。Xu (2024, JAR) 则从财经记者社会网络的角度揭示新闻偏斜的来源结构性成因, 提示媒体来源构成本身携带偏斜信息。综合而言, central_media_frac 把上述"来源结构携带信息"的洞见操作化为一条可纳入银行-年面板的稳健性协变量: 它既可作为报道曝光质量的控制项, 也可作为衡量一家银行被置于全国性 vs 地方性舆论视野下的暴露度代理。

## VAR: central_media_frac

【变体差分】
central_media_frac 是本单列家族 (singleton) 的唯一列, tier=standard, 因而其语义即家族 canonical 语义, 不存在需要与其它列区分的轨道/模型/阈值/权重/滞后差分。相对于媒体异质性族内的其它占比列, 它的区别性语义在于判据维度: 它按"行政层级"切分媒体 (中央级 vs 地方级), 而非按"内容取向"(财经/综合/其它, 见 fin_media_frac/comp_media_frac) 或"主办属性"(官方/市场化, 见 official_media_frac/market_media_frac)。三套切分判据语义正交、互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。具体到本列: 分子是银行-年内媒体名命中 media_classification.json 的 central_media 名单的报道篇数, 分母是该银行-年的报道总篇数 (与 full-only 留篇门控下的 n_articles 口径一致), 商即中央级占比, 值域严格 [0,1] 并受生产收尾断言守护。需要特别强调本列是一条 track-agnostic 元数据度量: 它仅依赖篇级"媒体(中文)"来源名, 与文章正文无关, 故不分 full/ctx/ss 三轨、无 _lg 嵌入孪生——这一点使它区别于同族依赖情感打分因而分轨的 tone_central_media_full/tone_central_media_ctx 与缺口列 tone_gap_central_local_full/_ctx。由于中央级判据与内容判据正交, 一家媒体可同时被计入财经类与中央级 (生产日志将该交叉记为合理的正交重叠), 因此 central_media_frac 与 fin_media_frac 在数值上并不互斥、可同时较高; 使用者不应将两者当作同一 partition 的份额来解读。缺失与降级语义上, 若 media_classification.json 不存在则整条媒体异质性分支跳过并告警 (本列不产出), 若 central_media 名单为空则所有 _is_central 记 0、本列在有报道的银行-年上退化为常数 0, 属可预期的优雅降级而非缺陷。

<!-- rendered-citations:begin -->
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics and Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review, 64, 101234. https://doi.org/10.1016/j.ememar.2024.101234
Peress, J. (2014). The media and the diffusion of information in financial markets: Evidence from newspaper strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
<!-- rendered-citations:end -->
