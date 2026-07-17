---
family_id: F486
columns:
- prox_100km_n_media
- prox_150km_n_media
- prox_200km_n_media
- prox_50km_n_media
unit: 计数 (个, 银行总部圈内当年报道过该行的去重媒体来源数)
formula: 'within = df_bank[haversine(bank_hq, media_geocode) <= d]; prox_{d}km_n_media
  = within["媒体(中文)"].nunique() (若该 bank-year 全部媒体地理编码缺失即 n_geocoded==0
  则整列填 NaN, 与 is_local/n_articles/frac 同批 NaN 语义对齐; 否则圈内 0 条命中记 0, 非 NaN)'
producer: pipeline/panel/geography.py::compute_geo_proximity_buffers (runner 步骤
  12, 四梯度地理距离缓冲)
upstream:
- 40_panel_export_main (df_exploded 篇章级表, 含 城市/国家地区/省份 媒体地理列)
- config/city_coordinates.json (城市坐标表, scripts/build_city_coordinates.py 生成)
- config/province_capital_map (省会映射, 供 Level-3 坐标回退)
- config/bank_addresses (银行总部地址→城市, 供银行侧坐标)
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: 'Don''t believe the hype: Local media slant, local advertising, and firm value'
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/j.1540-6261.2010.01626.x
  type: journal
  authors: Engelberg, J. E., & Parsons, C. A.
  year: 2011
  title: The causal impact of media in financial markets
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 67-97
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media coverage and the cross-section of stock returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: "10.1007/s10579-024-09730-2"
  type: "journal"
  authors: "Zhang, Z., & Bethard, S."
  year: 2025
  title: "A survey on geocoding: algorithms and datasets for toponym resolution"
  venue: "Language Resources and Evaluation"
  vol: "59"
  issue: "2"
  pages_or_artno: "1775-1796"
new_dois: []
---

## CORE

【构念与来源】
`prox_{d}km_n_media` 是 F486 家族的 track-agnostic 单轨计数指标, 度量以目标银行总部为圆心、半径 d ∈ {50, 100, 150, 200} 公里的地理缓冲圈内, 当年报道过该银行的去重媒体来源数(而非文章数)。它衡量的是"银行周边有多少家不同的新闻出版机构在关注它", 与同家族姊妹指标 `prox_{d}km_n_articles`(圈内文章总量, F485)、`prox_{d}km_frac`(圈内文章占该行当年可定位报道的比例)、`prox_{d}km_is_local`(圈内是否存在≥1 家媒体的 0/1 指示, F484)共同构成同一 producer 一次批量产出的四梯度地理接近度指标簇。构念上, `n_media` 回答的是媒体来源的广度/多样性问题(有几家不同报社在关注), 与 `n_articles` 回答的强度问题(总共写了多少篇)是两个正交维度: 同样是 10 篇圈内报道, 可能来自 1 家媒体的连续跟踪报道, 也可能来自 10 家不同媒体各写 1 篇, `n_media` 只能区分这两种情形, `n_articles` 不能。
本指标的经验动机来自"本地媒体偏向"(local media bias)文献: 距离公司总部越近的新闻出版机构, 因广告依赖、消息源便利、读者本地认同等渠道, 报道倾向与频率往往系统性区别于远端媒体(Gurun & Butler, 2012)。Engelberg & Parsons (2011) 进一步用多层级地理缓冲(而非单一"本地/非本地"二分)刻画媒体覆盖强度随距离衰减的连续形态, 是本家族"50/100/150/200km 四梯度而非单一阈值"设计的直接方法论依据。Fang & Peress (2009) 是媒体覆盖广度—股票横截面收益关系研究的计数主锚, 其"覆盖媒体数量而非仅文章数量"的计数惯用法与本列 `n_media` 的构念取向一致: 报道来源的分散度本身携带信息(多家独立媒体同时关注, 相较单一媒体连续追踪, 对信息扩散/关注度的代理含义不同)。
本列的地理坐标构造是三级退化查找: 媒体所在城市名精确匹配城市坐标表(Level 1)→清洗行政区划后缀再匹配(Level 2)→均未命中时退化为该媒体所属省份的省会坐标(Level 3)。Level-3 省会插补会引入系统性(非经典)测量误差: 省会所在地银行的圈内距离被系统性压低(→ `is_local`/`frac`/`n_media` 上偏), 非省会银行则一律被拉到"到省会的距离", 二者误差方向与银行区位系统相关而非随机噪声。producer 同批产出的诊断列 `prox_geo_imputed_frac`(阈值无关, bank-year 级, 记录可定位文章中经 Level-3 回退定位的比例)是使用本列做实证分析时必须联合披露、并可用作剔除/切分高插补格稳健性检验的配套列; 本列自身不携带插补标记, 使用者若不联合参照 `prox_geo_imputed_frac` 便无法判断某一 bank-year 的 `n_media` 数值有多少可信度是被坐标退化人为抬高的。

【方法学与计算】
计算发生在 `pipeline/panel/geography.py::compute_geo_proximity_buffers` (runner 步骤 12), 输入是篇章级 exploded 表 `df_exploded`(每行一篇文章, 含 `城市`/`国家地区/省份` 两个媒体地理列)与 bank-year 面板骨架 `panel`。对每个 (bank, year) 组: 先用 `_lookup_coords` 定位银行总部坐标(经 `bank_addresses` 银行→城市映射, 再走同一三级坐标查找); 若银行坐标本身查不到, 该 bank-year 整批 prox 列不产出(不落 buf_results, 后续合并时为 NaN)。再逐篇计算该文章所属媒体的坐标(同一三级查找, 带记忆化缓存 `_coord_cache` 保证同一 (city, province) 对重复查找返回位级相同结果, 纯性能优化非语义改变), 用 Haversine 球面距离公式(地球半径 R=6371km)算出媒体—银行总部距离 `_dist_km`。`n_geocoded` = 该 bank-year 中距离非缺失(即媒体地理信息可定位)的文章数, 是本家族全部 4 个 track-agnostic 列的共同分母/存在性判据。对每个阈值 d, `within` = `_dist_km <= d` 的子集; 若 `n_geocoded == 0`(该 bank-year 全部媒体地理信息不可定位), 则 `n_media`/`n_articles`/`frac`/`is_local` 四列整批填 NaN — 这是 2026-06-11 的一处口径修正(omni-g-geography-02): 此前 `is_local` 在此情形被填 0, 与同批 `frac` 因分母为零而填 NaN 相互矛盾(圈内媒体存在性"未知"被误记成"确知为无"), 现已对齐为四列同一 NaN 语义。若 `n_geocoded > 0` 但圈内命中为空集, `n_media` 记为整数 0(而非 NaN), 与"有媒体地理数据、但均在圈外"的确知状态一致。当 `n_geocoded > 0` 且圈内非空时, `n_media` = `within['媒体(中文)'].nunique()`(去重媒体来源名计数); 若 `df_exploded` 缺失 `媒体(中文)` 列(不应发生但作防御性兜底), 该值退化填 0。
本列是 track-agnostic 单轨(不区分 full/ctx/ss 三轨文本口径) — 因为它统计的是圈内命中的原始文章行(基于地理坐标, 与文章文本轨道无关), 与同批产出的情感聚合列 `prox_{d}km_tone_full/_ctx/_ss` 等三轨列不同; 后者才需要遵循「三轨各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J」的项目铁律, `n_media` 本身不参与该铁律约束的三轨口径分歧。producer 对 `_n_articles`/`_frac` 两个列族内建有拓扑一致性校验循环(校验同一 bank-year 内 `prox_50km_* <= prox_100km_* <= prox_150km_* <= prox_200km_*` 单调不减; 违规行仅 `logger.warning`, 非 `assert`/`raise`, 不阻断流程), 该循环未覆盖 `_n_media`(亦未覆盖 `_is_local`)。但同样的单调不减关系对 `n_media` 在数学上天然成立: 更大半径的缓冲圈是更小半径圆的严格超集, 圈内去重媒体来源集合只会随半径扩大而扩大或不变, 这是集合包含关系的机械推论, 而非 producer 显式程序校验的结果——使用者不应将其误认为"由 producer 断言保证", 而应理解为构造上必然成立、但未经程序断言的结构性约束。
本列与"留篇门控 = full-only"(2026-06-29) 铁律无直接交互: `n_media` 的计数对象是全部可定位地理坐标的文章(不区分是否通过 LLM 情感三家投票判定为"确认的银行金科报道"), 而非仅 `llm_vote_tone_full` 门控后的子样本; 该门控只影响同批产出的情感聚合三轨列(`prox_{d}km_tone/_pos_frac/_neg_frac` 等消费 `llm_vote_score{_track}`/`is_positive{_track}` 等门控后文章级列), `n_media`/`n_articles`/`frac`/`is_local` 四个 track-agnostic 列的分母口径是"可地理编码的文章"而非"门控留篇"。

【文献定位】
本家族方法论直接承袭 Engelberg & Parsons (2011, *The Journal of Finance*) 用多梯度地理距离缓冲刻画媒体覆盖随距离连续衰减的设计, 以及 Gurun & Butler (2012, *The Journal of Finance*) 关于本地媒体系统性偏向本地公司的经验发现——`n_media` 与其姊妹指标 `is_local` 一起, 提供了检验"银行周边媒体生态密度是否影响其被报道方式"这一假说所需的地理暴露测度。计数层面的方法学惯用法参照 Fang & Peress (2009, *The Journal of Finance*) 对媒体覆盖广度的计数处理——用来源数而非单纯文章量捕捉信息扩散渠道的分散程度; 三篇顶刊文献分别从"本地偏向为何存在"(Gurun & Butler)、"距离衰减应以连续梯度而非二分刻画"(Engelberg & Parsons)、"广度计数惯用法"(Fang & Peress)三个互补角度, 支撑本家族"四梯度去重媒体来源计数"这一具体设计选择。 这三个角度共同作用于圈内/圈外判定的前提——媒体来源必须先被解析为坐标, 而这一步的方法学领域可参照 Zhang 与 Bethard (2025, *Language Resources and Evaluation*) 对 geocoding / toponym resolution 算法族与评测数据集的系统综述: 该文梳理了将非结构化文本匹配到地理坐标或地名本体的算法谱系与基准数据集, 在本家族只作为上游坐标输入所处方法学领域的综述性参照, 用以支撑对地理编码质量与回退命中占比(`prox_geo_imputed_frac`)作显式披露的必要性。迁移边界须诚实标注: 该综述面向英文 NLP 语料的通用 geoparsing(从自由文本中抽取并消歧地名), 而本项目不做文本内地名抽取, 仅对结构化的「媒体来源城市/省份」元数据字段做词典查找, 消歧难度与误差机制均显著更低; 原文评测指标为地名解析准确率与距离误差中位数, 本项目未做此类基准评测, 只报告回退占比作为质量披露列。尤须声明的是, 本项目不主张该综述是 Level-3 省会质心回退启发式的方法学出处——综述系二手梳理而非方法来源, 且未经核实其是否讨论行政中心回退这一具体启发式, 省会回退属研究者自身的实现选择, 其对 50km 最窄档的偏误影响仍须按前述插补率分组自行核查。
## VAR: prox_50km_n_media

【变体差分】
d=50 公里, 本家族四阈值中最窄的缓冲圈, 是"严格本地"媒体生态密度的最保守测度: 只统计与银行总部距离不超过 50 公里的媒体来源数。相较其余三个更宽阈值, 本列受 Level-3 省会坐标插补的影响最敏感——若银行本身位于省会城市, 省会插补会把大量原本"实际距离未知"的省内媒体错误地压进这一最窄圈内, 使 `n_media` 系统性偏高; 若银行不在省会, 则该行本身与省会距离通常已超过 50km, 省会插补反而可能把本应"极近"的同城媒体误判为圈外(若该媒体因坐标缺失被拉到省会而非其实际所在地)。50km 是四梯度中样本方差最大、对坐标插补噪声最不稳健的一档, 使用时应优先联合 `prox_geo_imputed_frac` 做插补率高低分组的稳健性核查, 且与 100/150/200km 三档互为稳健性并排、不设主次——四档拓扑单调关系(50km 值 ≤ 100km 值 ≤ …)在数学上是超集关系的机械推论(更大半径的圆天然包含更小半径的圆), 而非由 producer 程序校验强制(producer 的拓扑一致性校验循环只覆盖 `_n_articles`/`_frac` 两个列族, 不含 `_n_media`, 且该校验本身仅 `logger.warning` 不 `raise`), 不代表 50km 档在识别上"更差"或"更好", 而是代理不同的地理接近度构念半径。
阈值判据为 `_dist_km <= 50`, 分母仍是可地理编码文章数 `n_geocoded`; `n_geocoded == 0` 时本列与 `prox_50km_n_articles`/`prox_50km_frac`/`prox_50km_is_local` 一并填 NaN(圈内媒体存在性未知), `n_geocoded > 0` 但圈内命中为空集合时记为整数 0(圈内媒体存在性确知为无)。在中国地级市尺度下, 50km 大致对应同一地级市市域或紧邻县区范围, 是四档中最接近"同城"直觉的一档, 因而也最贴合 Gurun & Butler (2012) 原始"本地媒体"构念的地理尺度; 但正因半径窄, 单个坐标误差(无论是媒体侧还是银行侧)对圈内/圈外判定的边际影响最大, 使用本列做本地媒体偏向检验时, 建议与 100km 档联合报告, 观察结果是否对半径选择稳健。

## VAR: prox_100km_n_media

【变体差分】
d=100 公里, 四梯度中的次窄阈值, 大致覆盖银行总部所在城市及邻近地级市范围内的媒体来源数。相较 50km 档, 对省会坐标插补噪声的敏感度有所下降(圈半径更宽, 插补引起的位移相对更容易落在圈内/圈外的判定不那么临界), 但仍显著受 Level-3 回退影响, 尤其是省域面积较小的银行所在省份。100km 与 50/150/200km 三档同为 track-agnostic 计数口径, 各自反映不同半径下的媒体来源密度, 互为稳健性并排, 不构成对彼此的替代或校正关系。
计算路径与家族内其余三档完全一致, 唯一差别是阈值判据 `_dist_km <= 100` 取代 `<= 50`; 分母仍是该 bank-year 可地理编码文章数 `n_geocoded`, `n_geocoded == 0` 时本列填 NaN、非"确知为零", 与 `prox_100km_n_articles`/`prox_100km_frac`/`prox_100km_is_local` 三个同批 track-agnostic 兄弟列共享同一存在性判据与 NaN 语义。`prox_50km_n_media <= prox_100km_n_media <= prox_150km_n_media` 在数学上必然成立(非 producer 程序断言保证, 该校验循环不含 `_n_media`), 因为 100km 圆是 50km 圆的严格超集, 圈内去重媒体集合只增不减; 但增量本身携带信息——若某银行从 50km 到 100km 档 `n_media` 几乎不增, 说明其本地媒体生态高度集中于市域内, 反之则说明周边地级市媒体亦在持续关注该行, 这一"边际增量"读数须结合相邻档位联合解读, 单独一档数值不能承载完整的地理衰减信息。

## VAR: prox_150km_n_media

【变体差分】
d=150 公里, 四梯度中偏宽的一档, 通常已能覆盖银行总部所在省份的大部分地级市乃至邻近省份的部分城市, 圈内命中的去重媒体来源数普遍高于 50/100km 两档(超集关系在数学上保证 `prox_150km_n_media >= prox_100km_n_media`, 该结论不依赖 producer 程序断言——producer 的拓扑一致性校验循环不覆盖 `_n_media` 列族)。该阈值下省会插补引起的"圈内/圈外"临界误判概率进一步降低(插补噪声量级相对圈半径更小), 但仍应结合 `prox_geo_imputed_frac` 判读, 不因半径变宽而豁免披露义务。与其余三档同为地理接近度四梯度并排测度之一, 不分主次。
阈值判据为 `_dist_km <= 150`, 计算主体与家族内其余三档共用同一 producer 单次遍历(同一 `within` 子集分层扩展), 分母口径 `n_geocoded` 与是否可地理编码的存在性判据也完全一致——本列不引入任何独立于家族的计算分支或额外过滤条件, 是纯粹的半径参数变体。150km 档在中国地级行政区划密度下往往已跨越省界, 对经济发达、地级市密集的沿海省份银行, 该档与 200km 档之间的边际增量可能已趋近饱和(新增的圈内环带媒体数量有限), 而对地广人稀、地级市稀疏的内陆/边疆省份银行, 150→200km 的边际增量仍可能显著; 这种跨省份异质性本身就是使用四梯度而非单一阈值的方法论理由——单一固定半径无法在不同地理密度的省份间保持"本地"这一构念的可比性。

## VAR: prox_200km_n_media

【变体差分】
d=200 公里, 四梯度中最宽的阈值, 对多数省会型银行或沿海城市群银行而言已能覆盖整个都市圈乃至跨省邻近区域的媒体来源。200km 档下圈内去重媒体来源数通常最多且波动相对最小(四档间的超集包含关系在数学上保证其为四档中的上界: `prox_200km_n_media >= prox_150km_n_media >= prox_100km_n_media >= prox_50km_n_media`, 此关系不依赖 producer 程序断言, producer 的拓扑一致性校验循环不覆盖 `_n_media` 列族), 是四梯度中受省会坐标插补边际影响最弱的一档(插补引起的位移量级相对 200km 半径而言更不容易改变圈内/圈外的判定), 但并不因此成为"canonical"或首选口径——四阈值在本项目方法论上互为稳健性、并排使用, 研究者应报告距离衰减的完整梯度模式(是否随半径扩大而 unbiased 增长、增长斜率是否在某阈值附近出现拐点), 而非仅取某一档作为唯一指标。
阈值判据为 `_dist_km <= 200`, 计算路径、分母口径 `n_geocoded` 与 NaN/0 存在性语义与其余三档完全一致, 唯一差异仍是半径参数。因 200km 已是本家族地理接近度谱系的上界, 其读数最接近"该银行当年全部可地理编码报道的媒体来源总数"的近似上限(除非有媒体距离银行总部超过 200km 仍被计入报道), 与不设距离限制的家族外指标(如全样本去重媒体数)存在概念上的接近但不等同的关系——后者不受 Haversine 距离门槛约束, 前者仍受 200km 硬截断, 二者数值差异本身即可作为"超远距离媒体报道占比"的辅助判读依据, 但该差异并非本列自身携带的输出, 需研究者自行与家族外全量媒体计数列联合构造。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Zhang, Z., & Bethard, S. (2025). A survey on geocoding: algorithms and datasets for toponym resolution. Language Resources and Evaluation, 59(2), 1775-1796. https://doi.org/10.1007/s10579-024-09730-2
<!-- rendered-citations:end -->
