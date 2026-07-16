---
family_id: F318
columns:
- ft_attn_city
- ft_attn_prov
- ft_attn_yr
unit: 比率 (议程份额, ∈[0,1])
formula: 'ft_attn_yr = 当年金融科技新闻篇数 / 当年全部唯一银行新闻篇数 (docid 去重, year-level 常量);
  ft_attn_prov / ft_attn_city = 曝露加权 leave-one-out (剔除焦点银行自身报道) 的
  省/市×年金融科技议程份额, 逐行 LOO 指数 = (cell_ft − own_ft) / (cell_total − own_total)
  按 (target_bank, year) 取均值; 分母 < min_articles=5 → NaN'
producer: pipeline\panel\attention_media.py::compute_fintech_attention_index ; pipeline\panel\codebook.py
upstream:
- 12_fintech_news_full.parquet
- 24_herd_decay.parquet (verified 域门控)
citations:
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media coverage and the cross-section of stock returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2011.01679.x
  type: journal
  authors: Da, Z., Engelberg, J., & Gao, P.
  year: 2011
  title: In search of attention
  venue: The Journal of Finance
  vol: '66'
  issue: '5'
  pages_or_artno: 1461-1499
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: 'Don''t believe the hype: Local media slant, local advertising, and firm value'
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock
    market'
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: "10.1111/jofi.70009"
  title: "Institutional Investor Attention"
  authors: "Kwan, A., Liu, Y., & Matthies, B."
  year: 2026
  venue: "The Journal of Finance"
  type: "journal"
  one_sentence_zh: "机构投资者对宏观与个股新闻的注意力配置存在系统性异质,可用交易活动与持仓调整识别,为本族'新闻覆盖占比即注意力代理'的构念提供最新顶刊佐证。"
- doi: "10.1111/jofi.13377"
  title: "Business News and Business Cycles"
  authors: "Bybee, L., Kelly, B., Manela, A., & Xiu, D."
  year: 2024
  venue: "The Journal of Finance"
  type: "journal"
  one_sentence_zh: "基于80万篇华尔街日报文章构建可解释的新闻主题注意力指数,证明媒体议题关注度对产出、就业与股市回报具有显著预测力,呼应本族以新闻篇数占比刻画议程份额的方法论。"
new_dois:
  - "10.1111/jofi.70009"
  - "10.1111/jofi.13377"
---

## CORE

【构念与来源】
本家族三列 (ft_attn_yr / ft_attn_prov / ft_attn_city) 共同操作化"金融科技公众注意力" (fintech public attention) 这一构念, 其理论谱系源自 Fang & Peress (2009) 提出的报纸覆盖率范式: 媒体覆盖是信息中介机制, 覆盖越密集, 该主题在投资者/公众议程中的相对权重就越高。本族测度以此为主锚, 用"当年/当地金融科技新闻篇数占全部银行新闻篇数的比例"直接操作化"议程份额" (agenda share)。作为对照 (非主锚) 引用 Da, Engelberg & Gao (2011) 的 In Search of Attention 范式: 该研究以 Google 搜索量指数 (SVI) 作直接注意力代理, 并论证报纸/媒体覆盖是搜索量数据缺失情形下的间接替代代理; 本项目语料为报纸新闻文本、无搜索量数据, 故仅以报纸覆盖构造间接注意力代理, Da et al. 在此仅是方法论对照, 不构成本比值指数本身的奠基文献。三列在地理粒度上依次递进: 年度 (ft_attn_yr, 无地理维度, 全国宏观基准) → 省级 (ft_attn_prov, 曝露加权 leave-one-out) → 市级 (ft_attn_city, 曝露加权 leave-one-out, 单元更细), 三者互为不同粒度稳健性参照, 非彼此替代关系。

本家族与同一 producer 模块内另一支处理变量族 (compute_attention_treatments 产出的 attention_pct/attention_index/attention_density/attention_disp 等) 是两支不同的测度, 勿混淆: 本家族 (ft_attn_*, 由 compute_fintech_attention_index 生成) 是"地理注意力指数族", 覆盖省/市/年三级地理粒度的 fintech 议程份额及其总量孪生 (ft_vol_yr/prov/city, 本家族外的兄弟列); 另一支 (ATT-1) 是"firm-level attention 处理变量族", 涵盖 full/ctx/ss 三轨与 HHI 集中度分支, 二者共享同一套 verified 域门控原则但计算函数、样本单元与列名空间完全独立, 不应在同一回归设定中把两支的列混同互替。

【方法学与计算】
三列的分子分母结构均遵循同一原语: 分子 = 单元内经 stage-21 LLM 验证为真的金融科技新闻篇数 (verified fintech, 按 docid 去重), 分母 = 该单元内全部银行新闻篇数 (含 fintech 与非 fintech, 不去重后再按 docid 去重到唯一文章)。verified 域门控 (2026-06-18 审计 ATT-2 修复) 的具体做法是: 先取 is_fintech_news==True 的候选子集, 按 (docid, target_bank) 与 stage-21 verified 集 (源自 24_herd_decay) 做 semi-join, 未通过验证的候选行就地重标为 is_fintech_news=False — 注意这是"原地重标"而非"物理删行", 因此分母 (全部银行新闻行数) 不受影响, 只有分子 (fintech 计数) 收窄到 verified 子集, 与本项目留篇门控口径 (full-only, 2026-06-29) 及另一支处理变量族 (ATT-1) 保持同一 verified 域, 剔除约 26.8% 被 LLM 判伪的银行-金融科技文章。这一"只门控分子、分母维持全集未门控"的设计是刻意的: 非 fintech 银行新闻从未进入 stage-21 验证流程, 物理上不可能门控, 若对全集做 inner-join 会把全部非 fintech 行删除、导致分母塌缩为 fintech-only 子集、比值退化趋近 1, 因此实现上采用"仅分子重标"而非"整体过滤"。 自 F4 (2026-07-16) 起, 多银行文章的文章级 fintech 身份 = 任一 (docid, bank) 对级 verified (any, 行序无关), 不再由 12_full 行序首位银行决定。

ft_attn_yr 是三列中最简单的一支: 按年份对全国唯一文章计数, 无地理维度、无 leave-one-out, 是一个 year-level 常量 (同一年份下所有银行取同一数值), 用作省/市两级的宏观基准与稳健性参照。

ft_attn_prov 与 ft_attn_city 共享同一套"曝露加权 leave-one-out (LOO)"构造, 差异仅在地理粒度 (省 vs 市)。构造分两步: 第一步 (_build_geo_index) 先在去重后的唯一文章层面, 按 (地理列, year) 分组统计该单元的全部银行新闻篇数 (_total) 与 verified fintech 篇数 (_ft), 并施加 min_articles=5 的最小样本量守卫 — 低于该阈值的 geo×year 单元被整体剔除, 不参与后续任何计算, 因为过小的单元 (如仅 1-2 篇文章) 会产生 0/1 型的伪极端比值噪声, 尤以市级细粒度单元为甚 (实测市级单一银行可支配单元 own-share 最高达 0.875, 若不设阈值会让该银行的注意力指数几乎完全由自身报道决定)。第二步 (_merge_geo_index_to_panel) 是核心的反身性内生守卫: 对每一篇提及焦点银行的文章, 先计算该银行在其所在 geo×year 单元内的自身贡献 (own_total = 该银行在该地区该年的唯一文章数, own_ft = 其中 verified fintech 篇数), 然后从单元总量中剔除该银行自身的贡献, 得到 leave-one-out 指数: LOO 分子 = cell_ft − own_ft, LOO 分母 = cell_total − own_total, 逐行算出 (cell_ft−own_ft)/(cell_total−own_total) 后按 (target_bank, year) 取曝露加权均值 (加权基于 df_all 未去重的 article×bank 出现频次, 报道该银行越多的地区在均值中天然权重越大)。这一设计消除了"银行自身金融科技报道越多 → 其所在地区注意力指数机械抬高"的反射性内生问题: 若不剔除自身报道, 一家高强度自我营销金融科技转型的银行会人为推高其所在省/市的 fintech 议程份额, 造成解释变量与被解释变量的机械正相关而非真实的外部媒体环境曝露。LOO 分母同样受 min_articles=5 守卫: 剔除自身贡献后剩余样本量不足 5 篇的 geo×year×bank 组合, 该行的 ft_attn_prov/city 记为 NaN, 不参与回归 (与省略自身支配单元后样本过小的噪声守卫逻辑一致)。此外实现中对 LOO 分子设有防御性下界 clip(0): 该守卫依赖"同一 docid 内地理列与 is_fintech 标记恒定"这一未显式断言的数据不变量 (own ⊆ cell ⇒ own_ft ≤ cell_ft), 当前语料经核验零例违反, clip 在生产数据上是 no-op, 但保留以防未来数据源出现跨 geo/标记不一致导致比值转负而逃过 [0,1] 值域校验。

NaN 语义存在两种刻意不对称的来源: 其一是 min_articles=5 守卫产生的"样本量不足"型 NaN (geo×year 或 LOO 分母过小); 其二是 balance_panel 笛卡尔积带来的"该银行该年完全无银行新闻覆盖"型 NaN (has_coverage=0, 该 bank-year 不在 12_fintech_news_full 全集脊柱内, 属于面板超集行, 天然 LEFT-join 得全 NaN)。两者在回归中都应作 listwise 删除处理, 但语义不同: 前者是"该地理单元样本太小、指数不可靠地估计"; 后者是"该银行该年完全不在新闻语料覆盖范围内, 注意力构念本身不可测"; 二者均须与"有银行新闻覆盖但零 fintech 报道"的真零暴露情形 (记 0, 非 NaN) 区分。三列均无地理信息缺失时同样记 NaN (某 bank-year 全部文章缺失省/市字段)。

本族与同一 producer 内并行产出的总量孪生列 (ft_vol_yr/prov/city, 不属本 F318 家族但共享同一计算管线) 构成"比值 vs 总量"互为稳健性的一对测度: ft_attn_* 是 intensive 议程份额 (对样本规模不敏感, 忽略绝对新闻热度), ft_vol_* = ln(1 + 曝露加权 LOO fintech 篇数) 是 extensive 覆盖规模 (Fang & Peress 2009 覆盖计数范式, ∈[0,+∞))。两者复用完全相同的 geo×year 单元划分、min_articles=5 守卫与曝露加权 LOO 映射, 因此共享同一非缺样本, 可直接对照, 但二者高度共线, 应分别进入各自独立回归、不应同时进入同一右手边设定。本族三列本身不涉及情感三轨 (full/ctx/ss) 划分: 其分子仅依赖 is_fintech_news 布尔标记 (源自 stage 15 fintech_intensity 判定加 stage-21 verified 域门控), 不涉及 llm_vote_score/tone 等情感测度, 因此不存在"银行∧金科同句" (_ss) 或"实体窗口" (_ctx) 这类文本轨概念上的分裂——这是本族与同一 producer 文件内其它三轨情感列的关键区别, 混淆二者会误判本族存在不存在的三轨口径。

【文献定位】
本族的核心识别逻辑与顶刊范式一脉相承: Fang & Peress (2009, The Journal of Finance) 首次系统论证媒体覆盖率 (coverage ratio) 作为公众关注度的合法代理变量, 并证明低媒体覆盖股票存在显著的"被忽视效应" (neglected-firm effect) 溢价, 为本族"新闻覆盖占比 = 议程份额"的构造提供了直接的方法论先例。Da, Engelberg & Gao (2011, The Journal of Finance) 提出以 Google 搜索量指数 (SVI) 度量直接注意力, 并系统比较搜索量与媒体覆盖两类代理的异同, 本族据此文献作对照式披露: 项目缺乏搜索量数据, 以报纸覆盖度量间接注意力属已知的替代方案而非最优方案。Gurun & Butler (2012, The Journal of Finance) 关于本地媒体偏斜 (local media slant) 与本地广告的研究进一步支持了本族地理分层构造 (省/市) 的合理性: 媒体的地理属性会系统性影响其报道倾向与覆盖密度, 因而在企业层面构造注意力代理时应显式控制/分层地理维度, 而非仅用全国汇总的年度序列。Tetlock (2007, The Journal of Finance) 关于媒体在股市中的角色 (Giving Content to Investor Sentiment) 进一步佐证了"新闻文本覆盖强度是公众/投资者关注与情绪的合法代理"这一识别前提: 该文证明媒体悲观度可预测股市定价与成交量偏离基本面, 说明新闻文本本身承载了独立于财务基本面的信息内容, 为本族"仅凭新闻篇数占比即可刻画议程份额"的极简加总构造提供了额外的方法论正当性 (议程份额本身不需情感极性信息即可承载有效的关注度信号)。这四篇构成本族识别策略在国际顶刊文献中的直接理论支撑链条。近年顶刊文献进一步夯实了这一识别前提: Kwan, Liu & Matthies (2026, The Journal of Finance) 发现机构投资者对宏观与个股新闻的注意力配置存在系统性异质,可用交易活动与持仓调整识别,为本族"新闻覆盖占比即注意力代理"的构念提供了最新顶刊佐证; Bybee, Kelly, Manela & Xiu (2024, The Journal of Finance) 基于80万篇华尔街日报文章构建可解释的新闻主题注意力指数,证明媒体议题关注度对产出、就业与股市回报具有显著预测力,呼应了本族以新闻篇数占比刻画议程份额的方法论。

## VAR: ft_attn_city

【变体差分】
本列是本家族地理粒度最细的一支, 以"城市" (标准化清洗后的地级市/直辖市字段) 为地理单元, 与 ft_attn_prov 共享完全相同的曝露加权 leave-one-out 构造逻辑与 min_articles=5 守卫, 唯一差异是分组键从省份换为城市。城市粒度的单元天然比省级单元更小、更容易被单一银行的报道主导 (own-share 实测最高达 0.875), 这正是本列必须严格执行 leave-one-out 反身性内生剔除与 min_articles=5 最小样本量守卫的经验依据: 若不做 LOO 剔除, 一家在其总部所在城市高频报道自身金融科技转型的银行, 会机械推高该城市的 fintech 议程份额, 制造银行自身行为与"外部媒体环境曝露"之间虚假的同期正相关; 若不设最小样本量阈值, 极小的城市×年单元 (可能仅 1-2 篇报道) 会产生 0 或 1 的伪极端比值, 掺入噪声而非信号。本列与 ft_attn_prov 互为不同地理粒度上的稳健性对照: 市级单元更贴近银行网点/分支机构实际所在的具体媒体生态圈, 因而理论上对"银行实际感受到的地方性 fintech 舆论压力"更具外部效度; 但市级单元样本量天然更小, 缺失率 (NaN 比例) 通常高于省级。二者应分别进入各自的回归设定互证结论稳健性, 不应同时进入同一右手边模型 (否则因构造上的高度嵌套相关性引发共线性问题), 也不应与该 producer 内另一支 firm-level attention 处理变量族的三轨列 (full/ctx/ss) 混入同一 over-identified 设定。

## VAR: ft_attn_prov

【变体差分】
本列以"国家地区/省份" (标准化清洗后的省级行政区字段) 为地理单元, 与 ft_attn_city 共享完全相同的曝露加权 leave-one-out (LOO) 构造与 min_articles=5 守卫, 是三列中地理粒度居中的一支。省级单元相比市级单元样本量通常更充裕、单一银行支配单元的风险相对更低, 但仍需与市级同样执行 LOO 反身性内生剔除: 逐行计算焦点银行在其所在省份该年的自身贡献 (own_total/own_ft), 从省×年单元总量中剔除后再取比值, 并按 (target_bank, year) 取曝露加权均值 (加权权重来自未去重的 article×bank 出现频次, 该省报道该银行的新闻越多, 该省在均值中的权重越大)。本列与 ft_attn_yr 相比, 关键差异是引入了省级地理曝露维度并叠加了 leave-one-out 剔除 (ft_attn_yr 是全国宏观常量、不涉及任何银行个体的自身贡献剔除); 本列与 ft_attn_city 相比, 差异仅在地理单元粒度粗细, 二者在方法学与守卫逻辑上完全对称, 互为不同粒度层级的稳健性参照, 应各自独立进入回归、不应混同或叠加进同一设定。

省级单元在实证使用上的定位介于全国常量 (ft_attn_yr) 与市级细粒度 (ft_attn_city) 之间: 相比市级, 省份的媒体生态与经济结构更为多元完整, 单一银行支配一个省×年单元的概率显著低于支配一个市×年单元, 因此本列的 NaN 缺失率与噪声水平通常低于 ft_attn_city, 更适合作为地理分层的首要估计; 相比全国年度常量, 本列保留了地区间媒体环境异质性这一关键维度, 能捕捉"银行所在省份的金融科技舆论氛围"这一比全国平均水平更贴近银行实际外部媒体环境的信号。三列共同构成一个地理粒度递进的测度阶梯, 阶梯内各档之间是严格的互为稳健性关系而非替代或嵌套关系: 若某一档因地理信息缺失或样本量不足产生大面积 NaN, 分析者应以另一档作独立稳健性检验, 而非试图用插补或加总方式把某一档数据"补入"另一档, 这会破坏各档各自的 just-identified 属性并制造伪造的过度识别设定。

## VAR: ft_attn_yr

【变体差分】
本列是本家族中唯一不涉及地理维度、也不涉及 leave-one-out 剔除的一支: 它是纯粹的年度全国宏观常量, 计算方式为当年经 stage-21 verified 域门控后的金融科技新闻篇数 (按 docid 去重后唯一文章计数) 除以当年全部唯一银行新闻篇数, 同一年份下所有银行取同一数值 (无 bank 维度的异质性), 因而不存在自身报道反身性内生问题, 也无需 min_articles 守卫 (年度全国样本量天然充足)。本列作为省/市两级的宏观基准与稳健性参照存在: 一方面用于检验省/市级 leave-one-out 估计是否随时间与全国基准同向变动, 另一方面在省/市地理信息缺失导致 ft_attn_prov/ft_attn_city 大量 NaN 的场景下, 本列提供了一个在时间维度上仍然可估的替代 (但构念上更粗糙、无法反映银行个体所在地区的媒体曝露差异)。三列 (yr/prov/city) 互为地理粒度递进的稳健性对照, 各自 just-identified 并排, 不分主次, 严禁在同一回归设定的右手边同时纳入以避免机械共线与解释力度重复计入; 本列亦不与该 producer 内其他情感相关列共享的 full/ctx/ss 三轨口径发生关联, 因其分子分母结构仅基于 is_fintech_news 布尔计数、非情感测度。

<!-- rendered-citations:begin -->
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. The Journal of Finance, 66(5), 1461-1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Kwan, A., Liu, Y., & Matthies, B. (2026). Institutional Investor Attention. The Journal of Finance. https://doi.org/10.1111/jofi.70009
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business News and Business Cycles. The Journal of Finance. https://doi.org/10.1111/jofi.13377
<!-- rendered-citations:end -->
