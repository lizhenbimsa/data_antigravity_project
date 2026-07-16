---
family_id: F320
columns:
- ft_vol_city
- ft_vol_prov
- ft_vol_yr
unit: 自然对数变换后的篇数 (ln(1+n), 无量纲)
formula: 'ft_vol_yr = ln(1 + 当年金融科技唯一篇数); ft_vol_prov/city = ln(1 + 曝露加权 leave-one-out
  金融科技篇数, 按 (省/市, 年) 单元汇总后映射到 bank-year)'
producer: pipeline\panel\attention_media.py (compute_fintech_attention_index) ; pipeline\panel\codebook.py
upstream:
- 12_fintech_news_full.parquet
- 40_panel_yearly (bank-year 曝露加权映射)
citations:
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media Coverage and the Cross-Section of Stock Returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2011.01679.x
  type: journal
  authors: Da, Z., Engelberg, J., & Gao, P.
  year: 2011
  title: In Search of Attention
  venue: The Journal of Finance
  vol: '66'
  issue: '5'
  pages_or_artno: 1461-1499
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1540-6261.2010.01626.x
  type: journal
  authors: Engelberg, J. E., & Parsons, C. A.
  year: 2011
  title: The Causal Impact of Media in Financial Markets
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 67-97
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: 'Identification of Endogenous Social Effects: The Reflection Problem'
  venue: The Review of Economic Studies
  vol: '60'
  issue: '3'
  pages_or_artno: 531-542
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: Identification of Peer Effects through Social Networks
  venue: Journal of Econometrics
  vol: '150'
  issue: '1'
  pages_or_artno: 41-55
- doi: "10.1016/j.iref.2022.09.007"
  type: journal
  authors: "Chen, R., Huang, J., Jin, C., Yang, Y., & Chen, B."
  year: 2023
  title: "Multidimensional attention to Fintech, trading behavior and stock returns"
  venue: "International Review of Economics & Finance"
new_dois:
- "10.1016/j.iref.2022.09.007"
---

## CORE

【构念与来源】
F320 (`ft_vol_yr`/`ft_vol_prov`/`ft_vol_city`) 是"金融科技媒体覆盖总量"三档地理层级孪生族, 度量的是 extensive margin (报道规模) 而非 intensive margin (报道占比)。三列由 `pipeline\panel\attention_media.py::compute_fintech_attention_index` 在 stage 40 panel encode 阶段物化, 元数据登记于 `pipeline\panel\codebook.py`。构念定位直接对齐 Fang & Peress (2009, *The Journal of Finance*) 的媒体覆盖范式: 该文用"是否被主流媒体报道"以及报道规模作为投资者关注 (investor attention) 的代理变量, 发现无媒体覆盖股票相对有覆盖股票存在显著超额收益, 即关注度本身具有可定价的信息含量。本族把这一"覆盖计数"范式移植到银行-金融科技语境: `ft_vol_*` 回答"该银行 (或其所在省/市) 在该年被金融科技相关新闻覆盖的规模有多大", 是一个纯粹的曝光量 (volume) 测度, 不涉及情感方向、也不涉及该曝光在全部报道中的占比。

本族与同一 producer 函数产出的比值族 `ft_attn_yr`/`ft_attn_prov`/`ft_attn_city` 是严格的"总量-比值"孪生对: `ft_attn_*` 回答"金融科技新闻占该单元全部银行新闻的份额是多少" (intensive, 议程份额, ∈[0,1]), `ft_vol_*` 回答"金融科技新闻的绝对报道规模有多大" (extensive, 覆盖规模, ∈[0,+∞))。两族共享同一底层数据源 (`12_fintech_news_full.parquet` 的 `is_fintech_news` 标记) 与同一 min_articles=5 稀疏单元守卫, 因而缺失样本完全对齐, 但测度构念不同, 在回归中互为稳健性、分别进各自设定, 不应把两者同时塞进同一设定视为对同一构念的重复冗余控制。

年度层 (`ft_vol_yr`) 是最粗粒度的基准: 全样本按年份汇总当年金融科技唯一篇数 (docid 去重), 取自然对数变换 ln(1+n)。该列是 year-level 常量 — 同一年份下所有银行取同一数值, 不含任何银行个体差异, 其作用类似时间固定效应之外单独可解释的"当年媒体议程整体升温/降温"控制变量, 在含年份固定效应的设定中会被年份哑变量吸收, 主要用于不含年份 FE 或需要显式讨论年度媒体环境水平的设定。

省级 (`ft_vol_prov`) 与市级 (`ft_vol_city`) 层则引入了地理维度与曝露加权 leave-one-out (LOO) 构造, 试图捕捉"焦点银行所处地理媒体环境"对该行金融科技曝光的外溢影响, 而非该行自身的报道规模。构造上先按 (省, 年) 或 (市, 年) 单元汇总该地理单元内的金融科技篇数, 计算 leave-one-out 时剔除焦点银行自身贡献的报道, 再按银行在该地理单元内的曝露权重加权映射回 bank-year 面板, 最后取 ln(1+·)。剔除自身报道是关键的反身性 (reflexivity) 内生守卫: 若不剔除, 一家银行自身的金融科技新闻会同时出现在被解释变量的构造成分与解释变量 (其所处地理环境的媒体热度) 中, 制造机械性正相关, 污染系数的因果解释; 该做法呼应 Manski (1993) 对"反射问题" (reflection problem) 的经典刻画 — 个体结果与其所属群体的均值结果同时含有该个体自身信息时, 内生性无法与真实的同侪/环境效应分离, 必须先做 leave-one-out 处理。

【方法学与计算】
底层数据取自 `12_fintech_news_full.parquet` 的全量银行新闻, 以 `is_fintech_news` 标记作为分子的计数依据, 按 docid 去重后计入。⚠ 需明确披露的样本宇宙口径 (2026-06-18 审计 ATT-2 修复后现状): 本地理族 (`ft_attn_*`/`ft_vol_*`, 由同一 `compute_fintech_attention_index` 产出) 的 `is_fintech` 分子已经门控 — 该函数内部对 fintech 子集按 (docid, target_bank) semi-join 到 stage 21 (LLM 三家投票共识) verified 集 (`24_herd_decay` 落地的 `llm_verified_full`), 将未通过验证的 fintech 行就地重标为非 fintech 后再计数, 实测剔除约 26.8% 判伪文章; 分母 (总篇数/覆盖判定) 保持全集不变, 仅分子受重标影响。该 verified 门控经 `is_fintech_news` 向下游传播, 覆盖本族全部三列 (`ft_vol_yr`/`ft_vol_prov`/`ft_vol_city`), 与同一 producer 文件内 firm-level 处理变量族 (`compute_attention_treatments` 产出的 `attention_index_*`/`attention_pct_*` 等) 采用的是同一 verified 域口径, 二者不再存在口径差异, 论文 data/sample 段可按统一的 full-only 留篇门控 (2026-06-29) 披露, 无需就本族与 firm-level 族分别披露不同的验证状态。此前 (审计 ATT-2 修复前) 本族一度直读未经验证的 12_full 全集、与 firm-level 族不一致, 该旧状态已被修复淘汰, 现状文档仅描述修复后的当前实现。 多银行文章的 fintech 身份自 F4 (2026-07-16) 起为任一对级 verified (any, 行序无关)。

省/市两档的计算流程: 第一步按 (地理单元, 年) 聚合出该单元当年金融科技篇数总量 `cell_ft` 与全部篇数 `cell_total`; 第二步做 leave-one-out, 即 `(cell_ft − own_ft)` 剔除焦点银行自身贡献; 第三步按银行在该地理单元的曝露权重 (源于银行分支机构/总部所在地的媒体归属映射) 做加权平均, 映射回每个 bank-year 观测; 第四步取自然对数 ln(1+·) 压缩右偏尾部并把量纲从"篇数"转为"弹性可解释的对数篇数", 便于与其他对数化控制变量 (如资产规模 ln(assets)) 在同一量纲下比较。稀疏单元守卫: 与 `ft_attn_prov`/`ft_attn_city` 共享同一 `min_articles=5` 门槛, LOO 剩余分母低于该阈值的单元记为缺失 (NaN), 而非人为拉伸到不可靠的小样本比值/总量估计上, 这一守卫在总量族与比值族之间完全对齐, 保证两族的非缺失样本宇宙一致, 便于在同一回归表中并排展示。

年度层 `ft_vol_yr` 不涉及地理曝露映射与 LOO, 是最简单的"当年全样本金融科技篇数取对数", 无跨银行差异。

三列共同遵循的 NaN 语义契约: panel 是 balance_panel 笛卡尔积, 可能含 12_full universe 之外的 bank-year (该银行该年完全无任何银行新闻覆盖, `has_coverage=0`); 这类行经 panel LEFT-join 后天然得全 NaN。这与"有新闻但零金融科技新闻"的情形刻意不对称处理: 前者是"注意力不可测" (无信息, 应做 NaN 并在回归中 listwise 删除), 后者是"真零曝光" (有信息, 保留为信息性零, ln(1+0)=0)。两者混淆会低估或高估金融科技媒体覆盖的实际零值比例, 该契约在 `test_attention_treatments::test_panel_superset_rows_are_nan` 中被锁定测试。

【文献定位】
本族的核心构念直接来自 Fang & Peress (2009, *The Journal of Finance*) 提出的媒体覆盖度量范式: 该文以"是否被全国性/地方性报纸报道"以及报道次数刻画投资者关注广度, 发现媒体覆盖的缺失本身预测未来超额收益, 确立了"覆盖计数"作为关注度代理变量的合法性, 是本族 extensive-margin 设计思路的直接理论来源。与之互补的 Da, Engelberg & Gao (2011, *The Journal of Finance*) 则用 Google 搜索量构造"投资者关注指数" (Search Volume Index), 二者共同构成"媒体侧覆盖 vs. 需求侧关注"两条平行的关注度测度传统, 本族选择前者 (供给侧媒体覆盖计数) 而非后者。Tetlock (2007, *The Journal of Finance*) 与 Engelberg & Parsons (2011, *The Journal of Finance*) 进一步论证媒体报道 (而非仅仅是媒体所报道的公司基本面) 对交易行为与股价具有独立于信息内容的因果影响, 为把"报道规模"本身 (而非报道内容的情感极性, 后者在本项目中由 stage 21/22/23 情感族单独测度) 作为一个独立可解释变量提供了理论支撑。地理维度的 leave-one-out 加权设计所处理的反身性问题, 呼应 Manski (1993, *The Review of Economic Studies*) 对社会效应识别中"反射问题"的经典论述, 以及后续 Bramoullé, Djebbari & Fortin (2009, *Journal of Econometrics*) 关于社会网络中同侪效应识别的方法论传统 — 二者共同提示: 任何把"个体所处群体环境"作为解释变量的设计, 都必须先从群体均值中剔除个体自身贡献, 否则估计系数无法与真实的环境外溢效应区分开。此外, Chen, Huang, Jin, Yang & Chen (2023, International Review of Economics & Finance) 构建多维度金融科技关注度指数(含媒体报道维度)并证明其对交易行为与股票收益具有增量解释力, 为本族以媒体覆盖规模刻画金融科技曝光度的构念提供了2023年最新实证支撑。

## VAR: ft_vol_city

【变体差分】
`ft_vol_city` 是三档地理层级中粒度最细的一档: 汇总单元为 (城市, 年), 而非省或全国。其余构造步骤与省级 `ft_vol_prov` 完全一致 — 先按 (市, 年) 单元统计 `cell_ft`/`cell_total`, 做 leave-one-out 剔除焦点银行自身金融科技报道贡献, 再按银行在该城市内的曝露权重加权映射到 bank-year, 最后 ln(1+·) 变换。与省级相比, 城市粒度的地理单元样本容量天然更小, 更容易触发 `min_articles=5` 的稀疏守卫而被记为缺失, 因此 `ft_vol_city` 的非缺失覆盖率预期低于 `ft_vol_prov` 与全样本 `ft_vol_yr`。使用上, 城市层是三档中"环境外溢范围"假设最窄的一档 — 隐含焦点银行主要受其所在城市本地媒体生态影响; 若研究者关心更宽泛的省域媒体环境外溢, 应改用 `ft_vol_prov`; 三档(年/省/市)各自 just-identified 并排使用、互为稳健性、不分主次, 不应混入同一 over-identified 设定联合估计。城市层与其比值孪生 `ft_attn_city` 共享同一 LOO 样本与同一稀疏守卫, 二者在回归表中通常并列汇报, 分别捕捉"报道占比"与"报道规模"两个不同侧面。就适用场景而言, 城市层最适合研究者相信媒体资源与舆论环境高度本地化的假设 — 例如同一省内不同城市之间金融科技报道密度可能因当地是否设有区域性金融中心、是否为地方性都市报重镇而存在系统性差异, 若真实的外溢渠道确实局限在城市尺度, 使用省级汇总会把城市间的异质性平均掉、稀释估计精度; 反之若真实外溢渠道更宽 (跨城市但同省), 城市层会因样本切分过细而在小样本年份 (如本项目 T=2 试跑窗口) 大量触发 `min_articles=5` 缺失守卫, 估计效率显著下降。因此实证操作上建议将 `ft_vol_city` 与 `ft_vol_prov` 同时汇报为并排稳健性设定, 而非事先假定何者是"正确"粒度; 二者孰优取决于金融科技媒体报道的真实地理外溢半径, 这是一个经验问题而非先验可判定的问题。

## VAR: ft_vol_prov

【变体差分】
`ft_vol_prov` 是三档地理层级中的中间粒度: 汇总单元为 (省份, 年)。相对城市层, 省级单元样本容量更大, 触发 `min_articles=5` 稀疏守卫而缺失的比例更低, 因而在 T=2 等观测年数有限的小样本场景下, 省级层通常是地理曝露族中数据可用性最好的一档, 常被用作城市层结果不稳健时的首选稳健性检验。其构造与市级完全同构 (仅聚合单元的地理粒度不同): (省, 年) 单元下的 leave-one-out 金融科技篇数, 按银行在该省内的曝露权重加权后映射到 bank-year, 取 ln(1+·)。省级层隐含的假设是焦点银行受其所在省份 (而非仅所在城市) 的媒体报道生态影响, 地理外溢半径比城市层更宽, 但比全国年度层 `ft_vol_yr` 更窄、更能捕捉跨省的媒体资源分布差异 (例如金融中心省份的金融科技报道密度系统性高于非金融中心省份)。省级与市级两档在同一回归中应作为互为稳健性的并排设定分别检验, 不建议同时纳入同一设定作为联合解释变量, 以免因地理单元嵌套 (市⊂省) 产生的机械共线性混淆系数解释。省级层的实际使用价值还体现在数据可用性上: 在本项目当前 T=2 (2017-2018) 的开发期试跑样本中, 省级 (省, 年) 单元的报道基数普遍高于城市 (市, 年) 单元, 更不容易跌破 `min_articles=5` 稀疏守卫而被记为缺失, 因而在生产级全量语料 (T=19, 2007-2025) 之前的开发验证阶段, `ft_vol_prov` 往往是三档地理测度中覆盖率最完整、可用于早期诊断的一档; 待生产语料到位、时间跨度充分拉长后, 城市层的样本容量瓶颈会随观测年数增加而缓解, 届时省/市两档的相对可用性差距预期会收窄。研究者在解读省级系数时应注意, 其反映的是"省域尺度"的媒体环境外溢, 若同时观察到城市层系数方向一致但幅度更大 (或更小), 可作为地理外溢半径的间接证据, 但不构成正式的空间衰减检验。

## VAR: ft_vol_yr

【变体差分】
`ft_vol_yr` 是三档中粒度最粗、构造最简单的一档: 不涉及任何地理曝露映射或 leave-one-out 处理, 直接对全样本按年份汇总当年金融科技新闻唯一篇数 (docid 去重后), 取自然对数 ln(1+n)。该列是 year-level 常量 — 同一年份下所有银行观测取值相同, 不携带任何跨银行截面差异信息, 其经济含义更接近"当年金融科技媒体议程整体热度"的宏观时间序列控制变量, 而非某一具体银行的曝光测度。正因如此, 在含年份固定效应 (year FE) 的面板设定中, `ft_vol_yr` 会被年份哑变量完全吸收, 此时纳入该列没有额外识别信息; 该列的适用场景主要是 (a) 不含年份固定效应、需要显式控制年度媒体环境水平的设定, 或 (b) 单独讨论"金融科技媒体覆盖的时间趋势"本身作为研究对象时。与省/市两档不同, `ft_vol_yr` 不受 leave-one-out 反身性守卫约束 (因其本就不是"焦点银行所处环境"的测度, 而是全市场共同暴露的宏观时间变量, 不存在自身报道污染自身环境测度的问题), 也因此不受 `min_articles=5` 稀疏单元缺失守卫的直接约束, 缺失通常只发生在整年无任何金融科技报道的极端情形。三档时间/空间粒度 (年/省/市) 互为稳健性并排, `ft_vol_yr` 是其中唯一的纯时间维基准, 不应与省/市两档地理曝露列混入同一 over-identified 估计设定。

<!-- rendered-citations:begin -->
Fang, L., & Peress, J. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Da, Z., Engelberg, J., & Gao, P. (2011). In Search of Attention. The Journal of Finance, 66(5), 1461-1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Engelberg, J. E., & Parsons, C. A. (2011). The Causal Impact of Media in Financial Markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Manski, C. F. (1993). Identification of Endogenous Social Effects: The Reflection Problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of Peer Effects through Social Networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Chen, R., Huang, J., Jin, C., Yang, Y., & Chen, B. (2023). Multidimensional attention to Fintech, trading behavior and stock returns. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2022.09.007
<!-- rendered-citations:end -->
