---
family_id: F471
columns:
- peer_fintech_exposure_lag1
unit: 无量纲加权平均对数指标 (行随机空间滞后, 与 ln_news_coverage 同尺度)
formula: 'peer_fintech_exposure_lag1[i,t] = Σ_j W[i,j,t-1] × ln_news_coverage[j,t-1], 其中 W 为按共现网络行归一化 (row-stochastic) 的空间权重矩阵, 分母仅对 ln_news_coverage 非缺失的在网同行求和并重归一 (非缺失同行以外一律置零, 不做 fillna(0) 伪零注入)'
producer: pipeline\panel\network_spillover.py ; pipeline\panel\export.py
upstream:
- ln_news_coverage
- bank_cooccurrence_network (t-1 年共现边)
citations:
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: Network effects in corporate financial policies
  venue: Journal of Financial Economics
  vol: '144'
  issue: '1'
  pages_or_artno: 247–272
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: Identification of peer effects through social networks
  venue: Journal of Econometrics
  vol: '150'
  issue: '1'
  pages_or_artno: 41–55
- doi: 10.1016/j.jbankfin.2024.107356
  type: journal
  authors: Ge, S., Li, S., & Zheng, H.
  year: 2025
  title: 'Diamond cuts diamond: News co-mention momentum spillover prevails in China'
  venue: Journal of Banking & Finance
  vol: '171'
  pages_or_artno: Article 107356
- doi: 10.1002/ijfe.3025
  type: journal
  authors: Ahmad, M., Hall, S. G., Law, S. H., & Nayan, S.
  year: 2024
  title: 'Spillover effects in the nexus of finance-institutions-growth: New insights from spatial Durbin analysis on emerging economies'
  venue: International Journal of Finance & Economics
  vol: '30'
  issue: '3'
  pages_or_artno: 2470–2491
- doi: "10.1016/j.jfineco.2026.104274"
  type: "journal"
  authors: "Avramov, D., Ge, S., Li, S., & Linton, O."
  year: 2026
  title: "Dual peer effects and cross-stock predictability"
  venue: "Journal of Financial Economics"
  vol: "180"
  pages_or_artno: "104274"
- doi: "10.1080/1540496x.2025.2605157"
  type: "journal"
  authors: "Ouyang, H., Liu, X., Yin, J., & Huang, C."
  year: 2026
  title: "Firm Network Complexity and Stock Returns: Case of Shared Analyst Coverage in China"
  venue: "Emerging Markets Finance and Trade"
  vol: "62"
  issue: "11"
  pages_or_artno: "4113-4136"
- doi: "10.1162/rest.a.1630"
  type: "journal"
  authors: "Boucher, V., & Houndetoungan, A."
  year: 2025
  title: "Estimating Peer Effects Using Partial Network Data"
  venue: "Review of Economics and Statistics"
  pages_or_artno: "1-48"
- doi: "10.1177/1536867x251341145"
  type: "journal"
  authors: "Estrada, P., Estrada, J., Huynh, K. P., Jacho-Chávez, D., & Sánchez-Aragón, L."
  year: 2025
  title: "netivreg: Estimation of peer effects in endogenous social networks"
  venue: "The Stata Journal: Promoting communications on statistics and Stata"
  vol: "25"
  issue: "2"
  pages_or_artno: "344-373"
new_dois: []
---

## CORE

【构念与来源】
本家族仅一列 `peer_fintech_exposure_lag1`, 度量目标银行 i 在第 t 年所面对的"同行金融科技声量溢出"(peer fintech exposure), 即同一新闻共现网络中与 i 相连的同行银行群体、在 t-1 年的金融科技报道声量加权平均, 经一期滞后后归给 i。构念来源双支: 一支是空间计量的行随机权重矩阵框架 (LeSage & Pace, 2009, *Introduction to Spatial Econometrics*), 用共现网络诱导的行归一化矩阵 W 对同行变量做空间滞后 W·y; 另一支是公司金融"同行效应"(peer effects) 范式, 尤以 Leary & Roberts (2014, *Journal of Finance*) 提出的"同行均值驱动本行财务政策"框架为直接参照 — 本列把该范式从"同行财务政策均值"迁移到"同行金融科技报道声量均值", 用以刻画金融科技话题在银行同业网络中的扩散/模仿压力。产出层挂靠在 `network_spillover.py` 的同行溢出计算段 (与 `peer_tone_lag1`/`peer_tone_2nd_lag1` 出自同一代码区块, 共享 W 与滞后年构造), 列标签在 `export.py` 中登记为 "Peer Fintech Exposure (L1)"。
本构念曾有一处历史锚点勘误 (2026-06-10 metric-audit, `omni-g-misc-01`): 早期注释误引 Berger et al. (2022, *Journal of Financial Intermediation*) 关于宏观经济政策不确定性 (EPU) 与银行流动性囤积的研究, 该文与本列所刻画的"同行共提网络行随机空间滞后"构念并不相符 — 二者虽同属银行行为的外部冲击传导议题, 但 Berger 等人研究的是单一宏观时间序列冲击对流动性决策的影响, 不涉及银行间网络结构与同行加权均值。经勘误后正确锚点收敛为 LeSage & Pace (2009) 的空间滞后算子与 Leary & Roberts (2014) 的同行均值范式, 本文档沿用勘误后的口径, 不再引用 Berger et al. (2022)。

【方法学与计算】
计算发生在 `pipeline\panel\network_spillover.py` 的按年循环体内, 紧邻同名 `peer_tone_lag1`/`peer_tone_2nd_lag1` 的构造逻辑, 复用同一年度共现网络诱导的行随机权重矩阵 W (基于 t-1 年银行两两共现边构建, 逐行归一化使每行权重和为 1, 满足空间计量对外生权重矩阵的形式要求)。具体步骤: 先取上游列 `ln_news_coverage` (对数化的金融科技新闻报道声量, 按行 t-1 年对齐入 `panel_lag`), 对目标银行列表 `bank_list` 逐一取值构成向量 `cov_vec`; 若某银行在 `panel_lag` 中缺失或值为 NaN, 不做零填充, 而是标记为"未观测"并从加权和的分母中剔除。随后按行执行 `W @ cov_obs`(仅对观测值求和的分子) 除以 `denom_c`(该行对所有"在网且非缺失"同行的权重和), 得到 `peer_cov` 向量; 当某行 `denom_c <= 0`(即该银行在网络中无任何拥有非缺失覆盖度的同行) 时, 结果置为 NaN 而非 0, 避免把"无可用同行信息"误记为"同行金融科技声量为零"这一实质性不同的状态。
该处理修正了早期版本 (`completeness-01`) 遗留的"伪零"缺陷: 原实现仅对 W 整行为 0 (孤立节点、无边) 的银行做了 NaN 守卫, 但未处理"银行在网络中有边、却因其自身 `ln_news_coverage` 缺失而被隐式当 0 参与同行均值"的情形 — 这与 `peer_tone_lag1` 曾出现的同型缺陷同源同修 (`netspill-peercov-fillna`, 2026-06-10 metric-audit)。修复后, 分母 `denom_c` 严格只累加"观测到覆盖度的同行"权重, 相当于对缺失值做 listwise 而非 0-imputation 处理, 使 `peer_fintech_exposure_lag1` 的量纲与 `ln_news_coverage` 本身保持一致 (加权平均而非加权和), 且不因同行缺失覆盖度而产生系统性向下偏误。滞后期为固定一期 (t-1 年网络 × t-1 年声量 → 落到 t 年该银行行), 因此该列在样本首年 (无 t-1 观测) 恒为缺失, 这是滞后派生列的通用边界条件, 非数据质量问题。
需要强调的方法论警示 (源码内嵌注释, 2026-06-10 metric-audit 追加): 共现网络本身的构造方式是"事件强度系统相关"的 — 银行两两共现与否, 部分取决于二者是否同时成为报道热点, 这一构造机制可能使权重矩阵 W 的"有效支撑"(哪些同行进入分母) 内生于与结果 (声量、语气) 相关的选择变量, 违背空间计量 / peer-effects 文献中"固定外生 W" 的前提假设。本处理区分了两类问题: 其一是"行特定确定性缩放"(即分母按观测同行重归一化), 这一步保持外生性, 不引入选择偏误; 其二是"支撑集选择性"本身 (即哪些同行进入 W 的非零集合, 取决于共现是否发生), 这一步的外生性无法由本列内部的技术处理担保。生产环境使用该列做识别推断时, 建议提供"全在网同行"或"平衡覆盖子样本"的稳健性对照组, 并对 W 条件下数据缺失机制是否满足"随机缺失" (MAR) 做额外论证; 家族内 `peer_tone_2nd_lag1` 所用的二阶去对角处理 (W² 去除自身路径) 只解决机械排他性问题 (确保本行自身滞后语气不通过二阶路径混入), 并不能替代对上述覆盖选择性问题的实质论证。

【文献定位】
本列所用的行随机空间滞后算子直接对应 LeSage 与 Pace (2009) 关于空间计量经济学的经典教材式框架: 给定行归一化权重矩阵 W, 空间滞后变量 W·y 表示"每个观测单位的所有邻居 (按权重) 的加权平均"; 本列将该算子应用于金融科技报道声量而非空间地理邻近关系, 用共现网络关系替代地理邻近关系, 属于该框架向社交/交易网络场景的迁移应用, 与 Grieser, Hadlock, LeSage & Zekhnini (2022, *Journal of Financial Economics*) 用网络结构刻画企业财务政策同行效应的建模思路一脉相承 — 该文同样以 LeSage 传统的行随机权重矩阵度量公司间网络关联, 并讨论了此类网络诱导变量在识别同行效应时面临的内生权重矩阵挑战, 与本列源码内嵌的"支撑集选择性"警示高度呼应。识别层面的一般性讨论另见 Bramoullé, Djebbari & Fortin (2009, *Journal of Econometrics*) 关于社交网络中同行效应可识别性的经典结果 — 该文证明, 在网络结构提供足够的排他性变异 (二阶及以上邻居结构差异) 时, 同行效应参数可分离识别, 这一逻辑框架是本列服务的下游回归 (以本列作为同行金融科技声量的滞后回归元或工具变量构造分量) 得以成立的理论前提之一。
同行效应度量范式的实证先例是 Leary & Roberts (2014, *Journal of Finance*), 该文用同行公司资本结构决策的加权均值预测本公司资本结构调整, 确立了"同行均值滞后作为回归元"这一实证套路; 本列将该套路中的"同行财务政策均值"替换为"同行金融科技新闻声量均值", 构念上从公司金融决策模仿迁移到银行业金融科技话题传播/模仿压力。中国银行业情境下的金融科技网络溢出实证近年亦有直接对标, 例如 Ge, Li & Zheng (2025, *Journal of Banking & Finance*) 利用新闻共提 (news co-mention) 构造的动量溢出网络, 证实了基于中国新闻语料构造的实体共现关系能够捕捉具有经济含义的跨主体信息传导, 为本列"以新闻共现网络为空间权重支撑"的设计选择提供了同源方法论效度支撑; 更一般的金融-空间溢出证据参见 Ahmad, Hall, Law & Nayan (2024, *International Journal of Finance & Economics*), 该文用空间杜宾模型刻画新兴市场金融机构增长的跨主体溢出效应, 印证了行随机空间权重范式在金融机构层面网络溢出研究中的适用性与稳健性。
在本项目口径体系中, `peer_fintech_exposure_lag1` 与同一代码区块产出的 `peer_tone_lag1`/`peer_tone_2nd_lag1`(同行语气溢出, 一阶/二阶) 是"构念平行、来源同构"的姊妹变量族: 三者共享同一 t-1 年共现网络诱导的权重矩阵 W 与相同的"仅对观测同行重归一化"缺失处理逻辑, 区别仅在于被空间滞后的底层变量 (`ln_news_coverage` vs. `llm_vote_tone` 及其派生轨道)。作为面板派生列, 本列继承本项目的一般性口径铁律: 若该家族未来扩展出多轨版本 (例如按 full/ctx/ss 三种文本口径分别构造 `ln_news_coverage` 进而分别空间滞后), 各轨须各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J 检验; 就现状而言, 本列本身不区分三轨、不涉及 co-primary 双轨嵌入, 亦不含消融/权重/阈值/判据梯子, 其滞后结构 (t-1→t) 与本项目 `n_articles`/留篇门控的 full-only 口径 (2026-06-29 起) 相独立 — 本列的"报道声量"上游 `ln_news_coverage` 本身是否已切至 full-only 口径, 应以该上游列自身的文档为准, 本列不重复引入该判定。 晚近文献从应用、连接构造、识别与实现四个侧面进一步巩固了这一测度族的坐标。Avramov、Ge、Li 与 Linton (2026) 在 Journal of Financial Economics 构造股票间的同侪连接矩阵, 以加权同侪特征作为暴露变量度量其向自身的溢出, 与本列 Σ_j W[i,j,t-1]×ln_news_coverage[j,t-1] 的行随机加权同属一个测度族, 可视为该形式在顶级金融期刊的最新应用存在性证明; 迁移边界在于原文的连接基于股票间经济联系、被加权量为收益或特征、目标是横截面收益可预测性, 而本列的 W 来自银行新闻共现网络、被加权量为媒体报道量对数, 层级为银行-年且不做收益预测。Ouyang、Liu、Yin 与 Huang (2026) 以「共享分析师覆盖」这一信息中介的共现关系构造中国企业间网络并研究其上的传导, 与本列以新闻共现 (同一篇报道同时提及两家银行) 定义 W 的思路同族——均以第三方信息生产者的共同覆盖来推断实体间连接; 但原文的连接来自分析师覆盖重叠、被解释对象为股票收益, 亦未涉及本列对缺失同行的重归一处理。计量识别层面, Boucher 与 Houndetoungan (2025) 针对网络结构仅被部分观测 (抽样网络、删失网络或链接误分类) 的情形提出同侪效应估计方法, 证明只要网络分布可一致估计即可在 linear-in-means 模型中识别同侪效应, 并以 Add Health 数据显示网络数据误差会造成同侪效应的大幅向下偏误; 其规范对象正是行归一化 W 与空间滞后项 W·y, 故该文既锚定本列这一形式的计量地位, 也提示网络测量误差对此类估计的衰减风险——迁移边界是原文对缺失链接作模型化推断, 本列则采取「仅对 ln_news_coverage 非缺失的在网同行重归一、其余一律置零」的确定性口径, 二者处理缺失的机制完全不同, 原文亦不涉及银行、媒体报道量与中国语境。实现层面, Estrada、Estrada、Huynh、Jacho-Chávez 与 Sánchez-Aragón (2025) 提供 netivreg 的 Stata 实现, 针对内生社会网络下的 linear-in-means 同侪效应模型实现广义三阶段最小二乘与 GMM 估计量, 其识别利用 two-layered multiplex network 的数据结构提供外生变异, 估计对象同为行归一化 W 与空间滞后; 该文是软件实现与方法说明而非实证发现, 本项目未使用 netivreg、亦不做内生网络校正而是将 W 视为前定 (取 t-1 期), 故它仅锚定同族方法在 Stata 生态 (本项目分析端亦落在 Stata) 的存在与可行性, 以及「W 内生时需专门校正」这一提示, 并不背书本列的前定假设。
## VAR: peer_fintech_exposure_lag1

【变体差分】
本列是家族内唯一一列, 因此不存在与家族内其他列的"变体差分"关系, 此处转而说明其与网络三轨面板中相邻但构念不同的其他列的区分边界。首先, 本列与 `peer_tone_lag1`/`peer_tone_2nd_lag1` 出自同一代码区块、共享同一 W 矩阵构造与滞后年对齐逻辑, 但被空间滞后的底层变量不同: 后者滞后的是银行自身报道的语气 (`llm_vote_tone` 及其后缀变体), 刻画"同行语气如何外溢影响本行"; 本列滞后的是银行自身金融科技报道的对数声量 (`ln_news_coverage`), 刻画"同行金融科技话题热度如何外溢影响本行", 二者在构念上分属"情感传导"与"话题声量传导"两条并行但不同的机制, 不可互换或合并入同一回归设定。
其次, 本列与家族外的 `industry_neg_shock`/`industry_neg_shock_lag1` 系列 (留一法同期/滞后行业负面冲击, 见 `brokerage_fire_sale` 相邻代码区) 亦需区分: `industry_neg_shock` 系列度量的是行业层面 (leave-one-out) 平均负面冲击强度, 其空间/加总结构是"同行业其余银行的简单或加权平均负面事件强度", 而本列是"网络加权的金融科技声量", 两者虽都属于"同行/同业外部性"大类, 但一个锚定负面冲击传导, 一个锚定金融科技话题声量传导, 经济学机制不同, 不应在同一模型设定中互为替代解释变量而不加区分。
再次, 本列与 `emb_peer_tone_lag1_*`/`emb_peer_tone_diag_lag1_*`/`bank_emb_sim_mean_lag1_*` 等 embedding 同业网络 W-轨系列 (Hoberg & Phillips 2016 式文本相似度网络, 2026-07-03 新增) 的核心区别在于权重矩阵 W 的构造来源: 本列的 W 来自银行两两新闻共现网络 (基于是否同时出现在报道中构造边), 而 embedding 系列的 W 来自文本向量空间余弦相似度构造的连续型网络; 两类 W 反映不同的"同行"定义 (共现驱动的注意力共振 vs. 文本内容相似驱动的业务/构念邻近), 依本项目铁律二者互为稳健性并排、不分主次, 严禁混入同一 over-identified 的 Hansen J 检验框架。
最后, 就滞后结构本身而言, "_lag1" 后缀表示该列采用 t-1 年的网络结构与 t-1 年的 `ln_news_coverage` 共同构造, 落位于 t 年该银行所在行, 目的是保证空间滞后变量相对于同期 (t 年) 结果变量在时间上前定 (predetermined), 缓解与结果同期决定的联立性/反向因果担忧, 且避免与年份固定效应共线 (镜像 `industry_neg_shock_lag1` 系列 "year-FE-safe" 的设计动机)。样本首年 (无可用 t-1 网络与声量观测) 该列恒为缺失, 属滞后派生列的常规边界情形, 使用时应配合面板起始年做相应的样本期说明, 不应将首年缺失误判为数据缺陷。

<!-- rendered-citations:begin -->
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247–272. https://doi.org/10.1016/j.jfineco.2021.05.060
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41–55. https://doi.org/10.1016/j.jeconom.2008.12.021
Ge, S., Li, S., & Zheng, H. (2025). Diamond cuts diamond: News co-mention momentum spillover prevails in China. Journal of Banking & Finance, 171, Article 107356. https://doi.org/10.1016/j.jbankfin.2024.107356
Ahmad, M., Hall, S. G., Law, S. H., & Nayan, S. (2024). Spillover effects in the nexus of finance-institutions-growth: New insights from spatial Durbin analysis on emerging economies. International Journal of Finance & Economics, 30(3), 2470–2491. https://doi.org/10.1002/ijfe.3025
Avramov, D., Ge, S., Li, S., & Linton, O. (2026). Dual peer effects and cross-stock predictability. Journal of Financial Economics, 180, 104274. https://doi.org/10.1016/j.jfineco.2026.104274
Ouyang, H., Liu, X., Yin, J., & Huang, C. (2026). Firm Network Complexity and Stock Returns: Case of Shared Analyst Coverage in China. Emerging Markets Finance and Trade, 62(11), 4113-4136. https://doi.org/10.1080/1540496x.2025.2605157
Boucher, V., & Houndetoungan, A. (2025). Estimating Peer Effects Using Partial Network Data. Review of Economics and Statistics, 1-48. https://doi.org/10.1162/rest.a.1630
Estrada, P., Estrada, J., Huynh, K. P., Jacho-Chávez, D., & Sánchez-Aragón, L. (2025). netivreg: Estimation of peer effects in endogenous social networks. The Stata Journal: Promoting communications on statistics and Stata, 25(2), 344-373. https://doi.org/10.1177/1536867x251341145
<!-- rendered-citations:end -->
</content>
