---
family_id: F484
columns:
- prox_100km_is_local
- prox_150km_is_local
- prox_200km_is_local
- prox_50km_is_local
unit: 二值指示 (0/1, 缺失=NaN)
formula: 'prox_{d}km_is_local = 1{ n_within(d) > 0 }, 其中 n_within(d) 为该 bank-year
  内、与银行总部 Haversine 距离 ≤ d 公里且媒体地名可地理编码的报道篇数; 若该
  bank-year 全部报道媒体地名均不可地理编码 (n_geocoded=0), 则置 NaN 而非 0。'
producer: pipeline/panel/geography.py::compute_geo_proximity_buffers (runner.py 步骤7d-geo「四梯度地理距离缓冲」)
upstream:
- 40_panel_yearly (bank-year 面板)
- config/city_coordinates_file (城市坐标字典)
- config/province_capital_map_file (省会回退映射)
- config/bank_addresses_file (银行总部地址)
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/0022-1082.00181
  type: journal
  authors: Coval, J. D., & Moskowitz, T. J.
  year: 1999
  title: "Home bias at home: Local equity preference in domestic portfolios"
  venue: The Journal of Finance
  vol: '54'
  issue: '6'
  pages_or_artno: 2045-2073
- doi: 10.1111/j.1540-6261.2010.01626.x
  type: journal
  authors: Engelberg, J. E., & Parsons, C. A.
  year: 2011
  title: The causal impact of media in financial markets
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 67-97
- doi: 10.1257/aer.20200374
  type: journal
  authors: Aguirregabiria, V., Clark, R., & Wang, H.
  year: 2025
  title: "The geographic flow of bank funding and access to credit: Branch networks,
    synergies, and local competition"
  venue: American Economic Review
  vol: '115'
  issue: '6'
  pages_or_artno: 1818-1856
- doi: 10.1111/1911-3846.13049
  type: journal
  authors: Kang, B. U., & Nam, J. S.
  year: 2025
  title: Do local newspapers matter to institutional investors?
  venue: Contemporary Accounting Research
  vol: '42'
  issue: '3'
  pages_or_artno: 1713-1743
- doi: "10.1080/24694452.2025.2564220"
  type: "journal"
  authors: "Kong, I., & Purves, R. S."
  year: 2026
  title: "Analyzing Geographic Bias of Newspaper Articles Reporting Global Climate Disasters"
  venue: "Annals of the American Association of Geographers"
  vol: "116"
  issue: "2"
  pages_or_artno: "270-288"
- doi: "10.1111/irfi.70009"
  type: "journal"
  authors: "Chen, H., Chen, Y., & Li, D."
  year: 2025
  title: "Local bias under natural disasters"
  venue: "International Review of Finance"
  vol: "25"
  issue: "1"
  pages_or_artno: "e70009"
- doi: "10.1111/1911-3846.12935"
  type: "journal"
  authors: "Huang, Y., Li, F., Li, T., & Lin, T."
  year: 2024
  title: "Local information advantage and stock returns: Evidence from social media"
  venue: "Contemporary Accounting Research"
  vol: "41"
  issue: "2"
  pages_or_artno: "1089-1119"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画"银行总部周边多大范围内确实存在过对它的媒体报道", 是地理距离缓冲 (geo-proximity buffer) 测度族里最基础的一支二值判定列, 由 `compute_geo_proximity_buffers` 在 runner.py 步骤7d-geo「四梯度地理距离缓冲」统一产出, 与同族 `prox_{d}km_n_media`(F486)/`prox_{d}km_n_articles`(F485)/`prox_{d}km_frac`(F483) 共用同一 Haversine 距离底座, 但语义收窄为最简单的"有/无"判定: 给定阈值 d ∈ {50, 100, 150, 200} 公里, 只要该 bank-year 内落在半径 d 公里圆圈内的可地理编码报道数 n_within(d) > 0, 该列取 1, 否则取 0。构念对标"本地媒体偏向" (home-bias in local media coverage) 文献谱系: Gurun & Butler (2012) 证明本地媒体对本地上市公司存在系统性正面偏差; Coval & Moskowitz (1999) 的本地权益偏好率先证明地理距离本身是资本市场信息不对称的度量维度; Engelberg & Parsons (2011) 提供了用多重距离阈值检验媒体因果影响力的方法论范式, 本家族的 50/100/150/200 公里四级阈值直接承袭这一多梯度设计思路, 而非单一"是否同城"的粗糙二分。白话讲: 以银行总部为圆心画四个同心圆 (50/100/150/200 公里), 每个圆问一句"圈里有没有报道过这家银行的媒体?" — 有就是 1, 没有就是 0; 圈越小越能反映紧邻本地的媒体关注, 圈越大越接近"区域内"而非"本地"的关注。

【方法学与计算】
距离计算走三级坐标退化: 优先精确匹配媒体所在城市名, 匹配不到则做地名清洗后再匹配, 仍匹配不到则退化到该媒体所属省份的省会坐标 (Level 3 插补); 银行总部坐标同样查表取得。两点间距离用 Haversine 球面公式 (地球半径取 6371 km) 计算, 而非欧氏平面近似, 对中国全域跨纬度比较更准确。is_local 列的分母口径是关键: 只统计"媒体地名可地理编码"的报道 (n_geocoded), 而非该 bank-year 全部报道数 (n_total) — 若某 bank-year 全部报道的媒体地名均无法定位 (n_geocoded=0), 圈内有无媒体是"未知"而非"确知为 0", 此时四个 is_local 列与同族 n_media/n_articles/frac 列一并置 NaN, 避免旧版本"is_local=0 但 frac=NaN"的自相矛盾误分类 (2026-06-11 一致性修复)。当 n_geocoded > 0 时, is_local(d) = 1{n_within(d) > 0} 是严格的存在性判定, 与 frac(d) = n_within(d) / n_geocoded 这一比例测度互补: is_local 只问有没有, frac 问多大比例, 二者在圈内报道稀疏 (n_within 常为个位数) 时携带的信息量不完全重叠, 是同一底层距离分布上的两种不同摘要统计量。四个阈值列满足拓扑单调性 (prox_50km_is_local=1 ⟹ prox_100km_is_local=1 ⟹ prox_150km_is_local=1 ⟹ prox_200km_is_local=1), 这一单调性并非运行时代码显式校验的对象, 而是由 n_within(d) 的单调性 (圈越大, 落入圈内的候选报道集合越大, n_within(d) 关于 d 单调不减) 直接推出的数学推论, is_local(d)=1{n_within(d)>0} 作为单调函数的复合自然继承单调性; 代码内嵌的拓扑断言循环 (对 `_n_articles`/`_frac` 两类列做校验) 并不逐列覆盖 `_is_local`, 后者的单调性属于间接保证而非直接断言。省会插补 (Level 3) 会系统性压低省会所在地银行与该省媒体的计算距离 (趋于 0), 使这些银行在小阈值圈内更容易被判为 is_local=1, 属于与银行区位系统相关的插补偏差而非随机测量误差; 家族配套诊断列 `prox_geo_imputed_frac` (F488) 记录插补比例, 供剔除高插补样本或做插补敏感性切分时使用。

【文献定位】
四阈值梯度设计方法论上呼应 Engelberg & Parsons (2011) 在《Journal of Finance》用多重距离窗口检验媒体报道因果影响衰减模式的做法; is_local 的"是否存在本地覆盖"判定与 Gurun & Butler (2012, Journal of Finance) 的本地媒体炒作假说 (local media hype) 及 Coval & Moskowitz (1999, Journal of Finance) 的本地权益偏好共享"地理距离是信息可得性的代理变量"这一核心识别逻辑。Aguirregabiria, Clark & Wang (2025, American Economic Review) 关于银行分支网络地理流动与信贷可得性的最新证据进一步印证了银行地理布局本身塑造信息与资金流动格局, 支持把"总部周边是否存在媒体覆盖"作为一个有意义的银行层面地理暴露指标。Kang & Nam (2025, Contemporary Accounting Research) 就本地报纸覆盖与机构投资者关注度关联的近期证据, 补强了本家族"本地媒体覆盖存在性"这一二值判定在资本市场信息环境研究中的当代相关性。 在此基础上, 三条近期锚点分别从分析范式、构念前提与设计同族三个侧面进一步定位本家族。Kong 与 Purves (2026) 对报纸文章检测地名并赋予地理坐标后, 量化报道在空间上的不均衡覆盖, 并考察地名粒度与要素类型对分析的影响, 为"先给新闻报道打地理坐标、再在坐标空间上做覆盖度统计、并同时披露地名可解析性问题"这一范式提供了前沿存在性证明, 呼应本家族对可地理编码报道作距离缓冲判定、并以 `prox_geo_imputed_frac`(F488) 披露回退占比的做法; 但该文语料固定为五家英国报纸、主题为全球气候灾害, 分析单位是"报道-事件发生地"的国别覆盖偏倚, 而非本项目"媒体所在地-银行总部"的双坐标距离, 亦无 bank-year 面板聚合与 n_geocoded=0 置 NaN 的哨兵口径。Chen、Chen 与 Li (2025) 利用逾 24,000 名散户的账户级日度持仓记录, 证明自然灾害下本地投资者比非本地投资者更多增持本地股票且效应由信息优势驱动, 为"本地/异地地理二分确实承载真实信息差异"这一构念前提提供近期依据; 其"本地"关系是投资者持仓行为与标的之间的关系, 与本项目媒体来源地对银行总部的关系在主体与关系类型上均不同, 该文以灾害为外生冲击做异质性检验且 local 取同城/同区二分, 并未使用 50/100/150/200 公里四梯度 Haversine 缓冲, 本项目亦无冲击设计。Huang、Li、Li 与 Lin (2024) 用社交媒体用户地理位置识别本地信息发布者, 按发帖者与公司总部的地理关系切分样本, 比较本地组与非本地组的信息含量差异, 与本桶同城 vs 异城子样本对比的设计同族; 但其数据为社交媒体发帖而非报纸/通讯社媒体来源, 地理归属基于用户 IP 或自报位置, 本项目则基于媒体来源城市字段经地名后缀清洗比对, 且该文以股票收益为被解释变量并仅作同城二分, 未使用连续距离缓冲或 Haversine 球面距离, 研究对象亦为一般上市公司而非银行。三者均只支撑构念与范式层面的前提, 不构成 50/100/150/200 公里阈值取值的文献依据 — 四档阈值仍属研究者选择, 按互为稳健性、不分主次的原则各自 just-identified 并排报告, 禁混入同一 over-identified Hansen J 检验。
## VAR: prox_50km_is_local

【变体差分】
本列是四阈值梯度中最紧的一档, 半径仅 50 公里, 近似"同城/紧邻城市群"范围: 只要该 bank-year 内存在至少一篇媒体地名可地理编码、且与银行总部 Haversine 距离不超过 50 公里的报道, 即取 1。因为圈小, 该列相较其余三档阈值对省会插补 (Level 3 坐标退化) 最为敏感 — 省会所在地银行的插补距离被压至 ≈0, 极易被误判为"存在本地覆盖", 而非省会银行则完全不会因插补而虚假地落入 50 公里圈内, 这一不对称性在四档中随阈值增大而递减。作为拓扑嵌套链的起点, prox_50km_is_local=1 蕴含其余三档 (100/150/200km) 全部取 1, 但反向不成立; 因此该列是四者中信息量最"苛刻"、也最贴近"严格本地"构念的判定, 与阈值更宽松的三档互为稳健性并排比较, 不分主次, 更适合作为"强本地覆盖"存在性的下界检验, 而非唯一采信口径。
从统计性质看, 50 公里档在四档中理论上取 0 的 bank-year 占比最高, 区分力 (方差) 也最强, 更容易在横截面上把"总部周边几乎无媒体驻扎"的偏远银行与"总部所在城市媒体密集"的银行分开, 是检验 Gurun & Butler (2012) 式本地媒体炒作效应时最贴近"本地"原始构念的一档; 但正因阈值紧, 样本中该列取 1 的观测数偏少, 若配合 bank-year 面板本就有限的时间跨度使用, 需留意小样本单元格下的统计功效, 通常建议与 100/150/200 公里三档一并报告, 而非仅凭 50 公里档下结论。与同族 n_media(F486)/n_articles(F485)/frac(F483) 相比, 本列丢弃了圈内媒体数量与报道强度的全部信息, 只保留最粗粒度的"有没有"判定, 适合作为存在性检验的稳健性起点, 而非替代比例型或计数型测度。

## VAR: prox_100km_is_local

【变体差分】
半径 100 公里档, 对应"区域内相邻地级市"量级的覆盖判定, 是四档阈值梯度中承上启下的第二档。判定逻辑与家族 canonical 完全一致 (存在性指示, 同一 n_geocoded>0 才有效判定的 NaN 语义), 差异仅在圆圈半径由 50 公里放宽至 100 公里, 因此圈内可纳入的报道候选集合是 prox_50km_is_local 圈的超集, is_local=1 的判定门槛相应放宽, 样本中取 1 的 bank-year 占比理应不低于 50km 档。该列相较 50km 档受省会插补偏差的影响有所稀释 (插补距离压缩效应在更大半径下相对不那么"决定性"), 但仍与更大两档 (150/200km) 一起构成阈值梯度上互为稳健性、各自独立判定的一员, 不应与其他阈值档混入同一识别方程的同一右手边做过度识别 (over-identified) 检验; 各阈值档的合理用法是并排报告结果的敏感性梯度, 而非相互替代的单一"正确"半径。
100 公里大致覆盖多数省份省会到周边地级市的距离量级, 可视为"广义同城通勤圈"或"城市群"层面的媒体覆盖判定, 介于严格本地 (50km) 与区域 (150/200km) 之间, 常被用作 Engelberg & Parsons (2011) 式多重距离窗口检验中的第二个锚点, 用来观察本地媒体偏向效应是否随距离放宽而快速衰减还是缓慢衰减。因为该档拓扑上被 50km 档蕴含 (prox_50km_is_local=1 ⟹ prox_100km_is_local=1), 二者的差集 (100km 内有覆盖但 50km 内无覆盖) 本身即是一个有意义的比较对象, 可用于反推媒体覆盖是否集中在紧邻总部的极小范围内, 还是分散在稍远的城市群内, 这一差分模式是本列相较 50km 档最核心的边际信息增量。

## VAR: prox_150km_is_local

【变体差分】
半径 150 公里档, 是四梯度中的第三档, 覆盖范围已接近多数中国省份的省内跨市尺度。该列的存在性判定与 canonical 定义一致, 圆圈进一步放宽后通常会使更多 bank-year 观测从 0 翻转为 1 (拓扑单调性保证 prox_100km_is_local=1 时该列必为 1), 使得样本中 is_local=1 的占比整体高于 50/100 公里两档, 区分力 (方差) 相应下降, 更适合作为"区域覆盖存在与否"的宽松基准, 而非严格意义上的"本地"判定。与其余三档同样遵循 n_geocoded=0 时置 NaN、圈内即取 1 的口径, 四档阈值梯度设计的意图是让研究者在稳健性检验里逐档报告估计系数是否随半径放宽而单调稳定或衰减, 该列在此梯度序列中承担中间锚点角色, 与 50/100/200 公里三档互为稳健性并排, 禁止混入同一过度识别设定。
150 公里量级通常已跨越单一地级市边界, 更接近"省域内广泛关注"而非紧邻本地关注, 若某 bank-year 在 50/100 公里两档均取 0 但在 150 公里档翻转为 1, 意味着该银行周边确有媒体报道, 但报道来源已明显偏离总部所在城市本身, 这类翻转模式对识别"本地媒体炒作"与"区域性媒体关注"两种不同机制的边界很有参考价值。由于圈内候选报道集合随半径放宽而单调扩大, 该列取 1 的稀疏度显著低于 50 公里档, 在存在大量报道稀疏、媒体地名难以精确定位的银行样本中, 150 公里档往往是四档里最先普遍取 1 的一档, 使用时应留意其相对更弱的区分力, 并结合同族比例列 frac 判断圈内报道究竟是"刚好越过门槛"还是"大量集中"。

## VAR: prox_200km_is_local

【变体差分】
半径 200 公里档, 是四梯度中最宽松的一档, 覆盖范围已逼近部分省份全域或跨省相邻地级市群, 判定门槛最低、is_local=1 占比在四档中理应最高 (拓扑单调链的终点, 蕴含关系为 prox_50km_is_local=1 ⟹ … ⟹ 本列=1, 但不可逆; 该蕴含关系是 n_within(d) 随 d 单调不减这一事实的数学推论, 并非代码运行时对 `_is_local` 列做的显式断言)。由于圈最大, 落入圈内的候选报道集合最广, 该列受任何单一媒体坐标误差 (包括省会插补) 的边际影响相对最小, 判定结果更接近"区域层面是否存在任何相关报道"而非严格意义的本地覆盖, 适合作为四档梯度中最宽松的稳健性上界与 50 公里档的严格下界做对照; 二者及中间两档在实证中应并排报告、各自独立成立, 不设唯一"正确"半径, 也不得把四档同时塞进同一识别方程造成的过度识别 Hansen J 检验中当作互替工具变量使用。
200 公里在中国地理尺度上往往已跨越省界或覆盖一个完整的城市群, "本地" 构念在此档已相当稀释, 更接近"是否存在任何可定位的相关报道"这一近乎全域覆盖的判定, 因此该列取 0 的 bank-year 观测在四档中理应最少, 若某银行在 200 公里档仍取 0 (或 NaN), 通常意味着该 bank-year 报道数极少或媒体地名几乎全部无法定位, 这类观测本身具有较高的数据质量警示价值, 建议结合 `prox_geo_imputed_frac`(F488) 与同族 n_articles(F485) 一并核查是否属于报道稀疏样本而非真实"零关注"样本。作为四档梯度的宽松上界, 本列常与 50 公里档的严格下界组成一对自然对照组, 用以在稳健性附录中报告"本地媒体炒作"效应估计系数是否随距离放宽而单调衰减, 衰减模式本身即是对 Gurun & Butler (2012) 假说边界条件的间接检验。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Coval, J. D., & Moskowitz, T. J. (1999). Home bias at home: Local equity preference in domestic portfolios. The Journal of Finance, 54(6), 2045-2073. https://doi.org/10.1111/0022-1082.00181
Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Aguirregabiria, V., Clark, R., & Wang, H. (2025). The geographic flow of bank funding and access to credit: Branch networks, synergies, and local competition. American Economic Review, 115(6), 1818-1856. https://doi.org/10.1257/aer.20200374
Kang, B. U., & Nam, J. S. (2025). Do local newspapers matter to institutional investors?. Contemporary Accounting Research, 42(3), 1713-1743. https://doi.org/10.1111/1911-3846.13049
Kong, I., & Purves, R. S. (2026). Analyzing Geographic Bias of Newspaper Articles Reporting Global Climate Disasters. Annals of the American Association of Geographers, 116(2), 270-288. https://doi.org/10.1080/24694452.2025.2564220
Chen, H., Chen, Y., & Li, D. (2025). Local bias under natural disasters. International Review of Finance, 25(1), e70009. https://doi.org/10.1111/irfi.70009
Huang, Y., Li, F., Li, T., & Lin, T. (2024). Local information advantage and stock returns: Evidence from social media. Contemporary Accounting Research, 41(2), 1089-1119. https://doi.org/10.1111/1911-3846.12935
<!-- rendered-citations:end -->
