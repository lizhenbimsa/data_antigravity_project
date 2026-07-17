---
family_id: F488
columns:
- prox_geo_imputed_frac
unit: 比率/占比 (proportion, [0,1]; bank-year 级, 阈值无关)
formula: 'prox_geo_imputed_frac = n_capital_imputed / n_geocoded (分子=该 bank-year 内经 Level-3 省会回退定位的媒体来源文章数; 分母=该 bank-year 内全部可地理编码文章数, 即三级查找 exact/clean/capital 任一命中的文章; n_geocoded=0 时取 NaN)'
producer: pipeline\panel\geography.py::compute_geo_proximity_buffers
upstream: []
citations:
- doi: 10.1257/aer.20200374
  type: journal
  authors: Aguirregabiria, V., Clark, R., & Wang, H.
  year: 2025
  title: 'The geographic flow of bank funding and access to credit: Branch networks, synergies, and local competition'
  venue: American Economic Review
  vol: '115'
  issue: '6'
  pages_or_artno: 1818-1856
- doi: 10.1002/ijfe.2791
  type: journal
  authors: Ahmad, M., & Law, S. H.
  year: 2024
  title: 'Financial development, institutions, and economic growth nexus: A spatial econometrics analysis using geographical and institutional proximities'
  venue: International Journal of Finance & Economics
  vol: '29'
  issue: '3'
  pages_or_artno: 2699-2721
- doi: 10.1016/j.jbankfin.2023.106964
  type: journal
  authors: Lai, S., Chen, L., Wang, Q. S., & Anderson, H. D.
  year: 2023
  title: 'Bank competition and corporate employment: Evidence from the geographic distribution of bank branches in China'
  venue: Journal of Banking & Finance
  vol: '154'
  pages_or_artno: '106964'
- doi: 10.1016/j.jbankfin.2024.107164
  type: journal
  authors: Dong, D., Jiang, D., Wu, K., & Zhu, H.
  year: 2024
  title: 'Game in another town: Geography of stock watchlists and firm valuation'
  venue: Journal of Banking & Finance
  vol: '163'
  pages_or_artno: '107164'
- doi: "10.1080/24694452.2025.2564220"
  type: "journal"
  authors: "Kong, I., & Purves, R. S."
  year: 2026
  title: "Analyzing Geographic Bias of Newspaper Articles Reporting Global Climate Disasters"
  venue: "Annals of the American Association of Geographers"
  vol: "116"
  issue: "2"
  pages_or_artno: "270-288"
- doi: "10.1007/s10579-024-09730-2"
  type: "journal"
  authors: "Zhang, Z., & Bethard, S."
  year: 2025
  title: "A survey on geocoding: algorithms and datasets for toponym resolution"
  venue: "Language Resources and Evaluation"
  vol: "59"
  issue: "2"
  pages_or_artno: "1775-1796"
- doi: "10.1111/j.1540-6261.2012.01725.x"
  type: "journal"
  authors: "Gurun, U. G., & Butler, A. W."
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: "The Journal of Finance"
  vol: "67"
  issue: "2"
  pages_or_artno: "561-598"
- doi: "10.1111/j.1540-6261.2010.01626.x"
  type: "journal"
  authors: "Engelberg, J. E., & Parsons, C. A."
  year: 2011
  title: "The causal impact of media in financial markets"
  venue: "The Journal of Finance"
  vol: "66"
  issue: "1"
  pages_or_artno: "67-97"
new_dois: []
---

## CORE

【构念与来源】
prox_geo_imputed_frac 不是一个情感或新闻覆盖度指标, 而是同族 F(prox_{50,100,150,200}km_*) 四梯度地理距离缓冲测度族的一个测量误差诊断列, 阈值无关、bank-year 级。它回答一个纯方法学问题: 在计算媒体来源与银行总部之间的 Haversine 球面距离时, 有多大比例的媒体来源坐标不是通过精确城市名匹配得到的, 而是退化用了省会坐标。producer 是 pipeline/panel/geography.py 中的 compute_geo_proximity_buffers, 它的核心任务是以银行总部为圆心画 50/100/150/200 公里四个同心圆, 统计圈内媒体的报道量与情感 (prox_{d}km_n_media / n_articles / frac / is_local / tone_full|ctx|ss / pos_frac / neg_frac), 用来检验本地媒体是否对本地银行系统性更正面, 这是 Gurun & Butler (2012, JF) 与 Engelberg & Parsons (2011, JF) 开创的本地媒体 home-bias 识别策略在中国银行业情境下的操作化。但该识别策略的前提是媒体坐标要足够精确 — 而本项目 3,740 家媒体来源的坐标数据并非全部覆盖到城市级, 于是内部函数 _lookup_coords 实现了三级退化查找: Level 1 精确城市名匹配, Level 2 清洗后 (去标点/统一简繁) 再匹配, Level 3 若前两级都失败但媒体所属省份可识别, 则回退用该省省会城市的坐标代替。prox_geo_imputed_frac 正是统计 Level-3 这一档在全部"可定位"文章中的占比。

【方法学与计算】
计算发生在按年度、按银行的双重循环内部。对每个 bank-year, 先取该银行当年全部相关文章 df_bank (n_total 篇), 再对每篇文章的媒体城市/省份字段做记忆化的三级坐标查找 (_lookup_coords_cached), 返回 (纬度, 经度, level) 三元组, level ∈ {'exact', 'clean', 'capital', None}。凡 level 非 None 的文章计入 n_geocoded (可定位文章数), 其中 level == 'capital' 的计入 n_capital_imputed (省会插补文章数)。prox_geo_imputed_frac = n_capital_imputed / n_geocoded, 当 n_geocoded == 0 (该 bank-year 全部媒体都无法地理编码) 时取 NaN, 而非 0 — 这与同族 prox_{d}km_frac/is_local/n_media/n_articles 在 n_geocoded==0 时统一填 NaN 的语义对齐(fix(omni-g-geography-02, 2026-06-11)), 避免"确知为 0"与"未知"的混淆。省会插补之所以值得单独诊断而非当作普通测量噪声忽略, 是因为它引入的距离误差与银行区位系统相关而非随机: 若某银行总部恰好设在省会城市, 则退化到省会坐标的媒体报道会被系统性算成"距离 ≈ 0", 从而拉高该银行 prox_{d}km_is_local / prox_{d}km_frac 等指标; 若银行总部不在省会, 则退化媒体会被系统性推向一个固定的省会坐标点, 距离误差同样非随机。这种系统性偏差意味着距离缓冲测度族本身可能与"银行是否驻省会"这一区位特征混杂, 论文中必须披露插补率并提供剔除/切分高插补格的稳健性检验。producer 内建的判读阈值把插补均值 0.2 作为经验分界: 低于 0.2 判读为"插补占比低, 定位口径较纯", 达到或超过 0.2 则告警"省会插补偏高, 距离含区位相关误差, 论文须披露+剔除稳健性"(该阈值仅用于运行时日志判读提示, 不改变列的定义或数值计算路径)。本列与其余 prox_ 族列在同一次年度×银行双重循环内一次性产出, 计算成本为 $0 (纯几何 Haversine + 字典查找, 无 LLM/embedding 调用)。

【文献定位】
prox_geo_imputed_frac 所服务的地理接近度测度族, 构念上直接对标 Gurun & Butler (2012, JF)"本地媒体炒作"(local media hype) 与 Engelberg & Parsons (2011, JF) 媒体因果影响力研究中通用的多距离梯度设计。但这两篇经典文献采用的是精确地理编码的美国报纸/公司数据, 隐含假设坐标测量误差可忽略; 本项目转到中国银行-媒体场景后, 坐标覆盖度存在结构性缺口, 因此需要额外一层测量误差自陈。Aguirregabiria, Clark, & Wang (2025, American Economic Review) 关于银行资金地理流动与分支网络协同的识别策略提醒我们, 银行地理网络结构(分支布局、总部区位)本身就是内生的经济决策变量, 与地理测度中的系统性误差存在合流的风险, 这正是本列要求"披露+剔除稳健性"而非简单忽略插补的方法论依据。Ahmad & Law (2024, International Journal of Finance & Economics) 的空间计量框架进一步说明地理邻近性/制度邻近性变量在构造时对坐标精度高度敏感, 呼应本列作为坐标精度诊断指标的定位。Lai, Chen, Wang, & Anderson (2023, Journal of Banking & Finance) 利用中国银行分支的地理分布度量银行竞争, 与本项目 target_bank 总部坐标 + 媒体来源坐标的匹配逻辑同属"银行地理位置作为识别工具"的中国银行业实证传统, 但同样依赖分支/总部坐标的精确性, 若坐标退化未被诊断, 可能把测量误差误读为竞争效应。Dong, Jiang, Wu, & Zhu (2024, Journal of Banking & Finance) 关于股票关注列表地理分布对企业估值影响的研究, 属于近期"地理链接可预测超额收益/估值效应"文献谱系的延伸, 同样建立在精确地理匹配之上, 侧面印证坐标精度诊断在这一文献谱系中并非可有可无的附属列, 而是保证识别有效性的必要前置检验。prox_geo_imputed_frac 因此定位为一个纯粹的方法学透明度列: 它不进入任何行为假设检验的右手边解释变量, 而是供研究者在稳健性附录中报告"剔除高插补 bank-year 后主结果是否稳健"的切分工具变量。 这一透明度定位在方法学近邻中亦有前沿参照。Kong 与 Purves (2026) 对报纸文章检测地名并赋予地理坐标后, 量化报道在空间上的不均衡覆盖 (地理偏倚), 并考察地名粒度与要素类型对分析结果的影响, 构成「先给新闻报道打地理坐标、再在坐标空间上做覆盖度统计并披露地名可解析性问题」这一分析范式的前沿存在性证明, 锚定本列把地理编码回退占比显式记账、而非默认坐标无误的做法; 迁移边界在于原文主题为全球气候灾害报道而非银行金融科技, 分析单位是「报道—事件发生地」的国别/区域覆盖偏倚, 本项目则是「媒体所在地—银行总部」的双坐标距离, 且原文不做 bank-year 面板聚合, 亦无本列 n_geocoded=0 时置 NaN 的哨兵口径, 期刊亦属地理学而非金融计量。Zhang 与 Bethard (2025) 系统综述了 geocoding / toponym resolution 的算法族与评测数据集 (将非结构化文本匹配到地理坐标或本体), 在本族中仅作为媒体来源地三级查找这一 geocoding 步骤所处方法学领域的综述性参照, 支撑对地理编码质量与回退命中占比作显式披露的必要性; 须明确本文并不主张该综述是省会质心回退启发式的方法学出处 (综述系二手梳理, 非方法来源), 亦未经核实其是否讨论行政中心回退这一具体启发式 —— 本项目的省会回退属研究者实现选择。其迁移边界还在于: 该综述面向英文 NLP 语料的通用 geoparsing, 须从自由文本抽取并消歧地名, 而本项目只对结构化的媒体来源城市/省份元数据字段做词典查找, 消歧难度与误差机制均更低; 原文评测指标为地名解析准确率与距离误差中位数, 本列未做此类基准评测, 仅报告回退占比作为质量披露列。
## VAR: prox_geo_imputed_frac

【变体差分】
本列是家族内唯一一列, 无需与同家族其他列做差分区分; 但需要与紧邻的 prox_{50,100,150,200}km_* 四梯度距离缓冲测度族(同一 producer 函数、同一双重循环产出, 但属另一 codebook 家族)做清晰的构念区分。prox_geo_imputed_frac 是阈值无关(threshold-agnostic)的单列诊断量, 不随 50/100/150/200 km 四个距离阈值变化取不同值 — 它衡量的是"分母口径本身有多不干净", 而非"圈内有多少媒体/文章/情感"。prox_{d}km_* 族内部的 tone_full/_ctx/_ss、pos_frac_full/_ctx/_ss、neg_frac_full/_ctx/_ss 是情感三轨测度, 遵循本项目三轨口径铁律: full/ctx/ss 三轨互为稳健性、各自 just-identified 并排, 不分主次, 绝不可混进同一 over-identified Hansen J 设定; 而 prox_geo_imputed_frac 是 track-agnostic 单轨列, 与三轨划分无关, 也没有情感 LLM 三家投票或 BERT 三模型的参与 — 它纯粹是坐标查找层面的地理编码质量指标, 计算路径里不涉及 stage 21/22/23 任何情感测度或 co-primary 双轨嵌入, 因此不受 full-only 留篇门控(2026-06-29)约束, 其分母 n_geocoded 的口径是"该 bank-year 可地理编码的文章数", 与情感面板列的 n_articles/n_articles_llm_valid 分母是两个独立的计数体系, 不可互相替代或混用。使用建议: 在任何以 prox_{d}km_* 为核心解释变量的回归设定中, 应将 prox_geo_imputed_frac 作为控制变量纳入, 或者用它划分高/低插补两个子样本分别重跑主回归, 作为地理测量误差的稳健性检验; 不建议直接把它当作因变量或核心自变量使用, 因为它本身编码的是数据基础设施的覆盖度, 而非任何经济假说要检验的行为。

<!-- rendered-citations:begin -->
Aguirregabiria, V., Clark, R., & Wang, H. (2025). The geographic flow of bank funding and access to credit: Branch networks, synergies, and local competition. American Economic Review, 115(6), 1818-1856. https://doi.org/10.1257/aer.20200374
Ahmad, M., & Law, S. H. (2024). Financial development, institutions, and economic growth nexus: A spatial econometrics analysis using geographical and institutional proximities. International Journal of Finance & Economics, 29(3), 2699-2721. https://doi.org/10.1002/ijfe.2791
Lai, S., Chen, L., Wang, Q. S., & Anderson, H. D. (2023). Bank competition and corporate employment: Evidence from the geographic distribution of bank branches in China. Journal of Banking & Finance, 154, 106964. https://doi.org/10.1016/j.jbankfin.2023.106964
Dong, D., Jiang, D., Wu, K., & Zhu, H. (2024). Game in another town: Geography of stock watchlists and firm valuation. Journal of Banking & Finance, 163, 107164. https://doi.org/10.1016/j.jbankfin.2024.107164
Kong, I., & Purves, R. S. (2026). Analyzing Geographic Bias of Newspaper Articles Reporting Global Climate Disasters. Annals of the American Association of Geographers, 116(2), 270-288. https://doi.org/10.1080/24694452.2025.2564220
Zhang, Z., & Bethard, S. (2025). A survey on geocoding: algorithms and datasets for toponym resolution. Language Resources and Evaluation, 59(2), 1775-1796. https://doi.org/10.1007/s10579-024-09730-2
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
<!-- rendered-citations:end -->
