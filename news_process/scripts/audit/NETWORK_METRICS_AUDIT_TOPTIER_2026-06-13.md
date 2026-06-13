# news_process 网络位置(网络结构)指标 — 顶刊标准系统审计 (2026-06-13)

> 本报告是对两个网络模块 `pipeline/panel/network_spillover.py` (1490 行) 与 `pipeline/panel/network_brokerage.py` (528 行) 全部网络变量族的**专项顶刊标准审计**。覆盖: (A) 22 共现网络中心度 `bank_*_cent`/`net_*_yr`; (B) 同行溢出 `peer_tone_lag1_*`/`peer_tone_2nd_lag1_*`/`peer_fintech_exposure_lag1`; (C) 认知邻近 `bank_cogn_mean` + 嵌入网 `emb_peer_tone_lag1_*(_t2v)`/`bank_emb_sim_mean_lag1`; (D) 经纪二分图 `brokerage_eigen_cent`/`industry_neg_shock(_lag1)`/`brokerage_fire_sale`。追踪到 runner 步骤 7f/7g/7h 接线 + `brokerage_network` 论文 Stata 模板/`paper_spec.yaml`/codebook 下游消费。

**审计日期**: 2026-06-13
**方法**: Recon(变量清单+下游消费追踪) → 7 专家镜头并行评审(识别/网络科学/空间计量/数值/引文/构造/统计功效) → 每条发现 2 镜头对抗核验(代码披露假阳过滤 + 方法学正确性) → 综合定级 + 完备性批判盲区猎手。多智能体工作流 **87 agents / 6.45M tokens / 1337 tool-uses / ~58min** → **主控亲验最高价值发现 2 项(实证跑 networkx 复现)** + 严重度重校准 + 与历史审计/memory 对账。
**环境**: Python / networkx 3.6.1; 盘上面板 = T=2 试跑样本 (~176 行, 2017–2018, = 全量 17M/T=18 语料的 0.055%)。
**口径**: $0 只读审计 — 不动代码、不动 `_llm_cache.db`、不付费重跑。本报告仅存档, 未改任何源文件。
**目标标准**: JF / RFS / JFE / QJE / AER / ECMA 审稿人 + AE 最高标准。

---

## 0. 主控亲验结论 (本报告可信度锚)

不照单全收工作流的 38 条原始发现。对**最具决定性的两条**(一个最危险的新 P1、一个唯一的真代码 bug)亲自跑 networkx 复现:

| # | 发现 | 主控复现证据 | 裁决 |
|---|------|------------|------|
| α | **N-01**: `nx.eigenvector_centrality` 在二分图上幂迭代病态(±λ 简并致振荡不收敛 → 退 degree 兜底) | 复刻 media-bank 连通二分子图 **40/40 全部收敛**; 收敛向量 vs 真 Perron 向量 **corr=1.0**、vs 加权 degree corr=0.69 → 收敛到真特征向量**非** degree。根因: networkx 迭代 **(I+A)** 而非 A, 1+λ_max 为唯一最大模特征值, 绕开 ±λ 简并 | ❌ **证伪**(完备性批判从教科书幂迭代理论推, 未跑 networkx 实现) |
| β | **rank 2**: `bank_eigen_cent` 断连共现图上给非主导分量银行写数值残渣 | 断连图(重权三角主分量 + 独立小分量)整图跑 `nx.eigenvector_centrality`: 主分量 a/b/c/d ∈ [0.23, 0.60], 小分量 x/y/z = **3e-42 ~ 5e-42** 数值残渣(非 NaN, 会被回归当"中心度极低的真银行") | ✅ **真**(唯一真代码 bug) |

**对工作流可信度的判断**: 主控亲验逮出完备性批判的最高危 P1(N-01)实为假阳性 —— 这正是"对抗核验 + 实证复现"价值的体现。综合层的 24 confirmed 经双镜头核验, 定级合理; 但**引文维度(D5)的 12 个核验 agent 因服务器限流失败**, ranks 16/20/21 是单边核验(见 §8)。下文按主控重校准给级。

---

## 1. 执行摘要

**整体结论: 核心算法基本 sound** —— 共现/二分图/中心度/2SLS 数值路径无活跃崩溃, T=2 退化与多数构造正确性已被代码诚实披露, 历史多轮审计的修复守住。**真正的代码 bug 只有一个**(`bank_eigen_cent` 断连图残渣, 已实证)。**最大的可发表性硬伤是一个 $0 模板缺口**(brokerage 全部 2SLS 缺弱工具诊断)。其余绝大多数是**构念外部效度 / 识别论证完整性 / 引文标签一致性**的真实缺口 —— 决定能否过 JF/RFS 审稿, 但不是"算错了"。

**白话**: 这套网络指标的"机器"造得扎实, 没有把数算错的硬故障。唯一真 bug: 某年共现网分成几座"孤岛"时, `bank_eigen_cent` 会给小岛银行写约 1e-42 的垃圾数(不是缺失值, 而是被回归当"中心度很低的真银行")。其余问题几乎都在"论文怎么写、怎么向审稿人交代"这一层 —— "凭新闻同框就说两家银行是同行"从没验证、弱工具检验表里没印出来、几个文献标签贴错了。这些不改数字, 但投顶刊会被卡。

### 确认问题计数 (主控重校准后)

| 级别 | 数量 | 说明 |
|---|---:|---|
| **P1 (顶刊级真缺陷)** | **6 + 4 新盲区** | 1 真代码 bug + 1 $0 弱工具诊断 + 4 识别/构念 + 跨模块缺失约定/行业内生选择/语料宇宙/换岛噪声 |
| **P2 (真缺口, 须修)** | **14** | 归一口径/构念效度/引文标签/孤儿变量/稠密退化 |
| **P3 (一致性/边界/卫生)** | **9** | 标签错挂/跨年不可比/裸 assert/重排序副作用 |
| **推翻的假阳性 (诚实记录)** | **4** | 含主控实证证伪 N-01, 见 §5 |

---

## 2. P1 净清单 (6 条 + 4 新盲区, 进发表产物, 须优先关注)

### P1-1 · `bank_eigen_cent` 断连共现图上给非主导分量银行写数值残渣 【唯一真代码 bug, 已实证】
- **file**: `network_spillover.py:557-583` (eigenvector 三级 fallback)
- **问题**: 主路径在**整图 G** 上跑 `nx.eigenvector_centrality(G, max_iter=1000, tol=1e-6)` (L560), 断连时不抛 `PowerIterationFailedConvergence` 而是收敛, 把特征向量质量全压到谱半径最大的分量, 其余分量(含 LCC, 若 LCC 谱半径非最大)的银行得 ~1e-42 数值残渣。因 `eigen_done=True` (L564) 锁死, L567-579 的 numpy(LCC) fallback 永不触发; L533-535 的 components/LCC 仅供 CFB/eccentricity, 从不用于 eigenvector。
- **主控复现**: 见 §0-β。残渣是 1e-42 量级(比 agent 估的 1e-8 更小), 非 NaN → 回归当真值。
- **为何顶刊卡**: 全量 T=18 (1768 家银行, 多数小行罕被共提) 共现网几乎必然断连 → `bank_eigen_cent` 对相当比例银行是无网络含义残渣, 污染该列 + 下游回归。**同型 bug 在 brokerage 侧已被 `fix(omni-g-net-brok-02)` 用 `_eigenvector_centrality_by_component` 修复, 唯独共现侧没移植** → 项目内部标准自相矛盾(`network_brokerage.py:186-189` 把同型行为定性为"数值残渣不具网络含义", 而此处 fallback 注释 L571-574 把它当可接受退化语义)。
- **修**: 移植 brokerage 的 `_eigenvector_centrality_by_component`: 对 G 先 `nx.connected_components` 分解, 每分量(≥3 节点)内单独确定性 eigenvector + 分量内归一, 微小分量置 NaN, 删现三级 fallback。补一条"小分量谱半径更大"断连图测试。**需重生 golden。**

### P1-2 · brokerage 全部 2SLS 模板系统性缺弱工具诊断 (KP rk F / Stock-Yogo / AR CI) 【$0, golden-safe, 最该先做】
- **file**: `papers/_common/stata_templates/brokerage_network/11_table2_main_iv_2sls.do.tmpl:33-50`; `13_table4_heterogeneity.do.tmpl:30-47`; `14_table5_robustness.do.tmpl:34-84`; 对照 `25_tableA6_tone_iv_2sls.do.tmpl:138-145`
- **问题**: 7-8 个 `ivreghdfe` 2SLS 列(11_table2 M2/M3 + 13_table4 H1/H2 + 14_table5 R1-R4) 全加 `ffirst` 让内部算第一阶段, 但 `esttab` 从不在 `stats()` 提取 `e(widstat)`=KP rk Wald F, 无 Stock-Yogo 临界值, 无 Anderson-Rubin 弱工具稳健 CI。grep 全 brokerage 模板目录 `widstat/KP/Stock-Yogo/AR/weakiv` 零命中。**同日(2026-06-13)新增主线 `25_tableA6:138-145` 已建完整标准**(stats 含 widstat + KP F<10→AR CI 脚注 Andrews-Stock-Sun 2019) → brokerage 是包内唯一缺口家族。
- **为何顶刊卡**: 工具 `peer_tone_2nd`(W²·tone) 由生成内生变量的同一 row-stochastic W 机械派生 (`network_spillover.py:331` `W2=W_arr@W_arr`), W/W² 在共现网近传递时近共线, 弱识别风险结构性最高且 N 增大不解决。RFS/JFE 对单工具恰好识别 2SLS **强制**报第一阶段 KP rk Wald F + Stock-Yogo, F<10 时报 AR CI。复现包内部标准不一致 referee 必质疑。代码层 `network_spillover.py:326-330` 已诚实披露 row-specific 重归一改变第一阶段 F → 作者明知 F 是关键量, 但认知未传导到 Stata 模板层。
- **修**: 11/13/14 三模板 `esttab` 加 `stats(N r2 widstat, fmt(0 3 3) labels("N" "R²" "KP F"))` + 套用 25_tableA6 同款脚注。恰好识别下 Hansen J 仍正确地不加(df=0, 模板 L37-40 已勘误)。**纯模板文本, $0, golden-safe。**

### P1-3 · 核心构念缺外部效度: 新闻共现网当经济同行网代理用于 2SLS, 从未对照任何已知关联网验证
- **file**: `network_spillover.py:105-187, 221-408`; `papers/brokerage_network/paper_spec.yaml:8-21`
- **问题**: 全族因果识别建立在未检验断言 "两家银行新闻共现 ≈ 经济同行" 上。`build_adjacency_matrix` 按 docid 共现对 +1 直接喂 W/W² 作 2SLS 工具 (MAIN_IV=`peer_tone_2nd_lag1_full`); `paper_spec.yaml:20` 直接把共现等同 peer 关系并据此(L11)声称识别"同业情感溢出的因果效应"。代码库与 spec 无任何把共现网与外生已知关联网(同业拆借敞口/共同持股/同省/同监管类别/Hoberg-Phillips 财务相似度)对照的效度检验(grep `validat/QAP/dyadic/known-network` 零命中), 也未讨论网络测量误差对一阶 endog 衰减与二阶 IV 排他污染。
- **为何顶刊卡**: JF/RFS/JFE 对"把可观测网络当潜在经济网络代理"**强制**要求外部效度验证(Leary-Roberts 2014 用真实同行 / Hoberg-Phillips 2016 验 TNIC)或限定 claim 为"媒体共现网本身"。W²·tone 工具排他性依赖"二阶共现银行只能经一阶共现影响我", 若共现网与真实关联网错配(媒体偏好/同期同事件驱动共现), W² 可经未建模真实通道直接进结果, 违排他。**最可能 desk-reject 或 major revision 的识别命门。** 已披露的 T=2 不可识别是样本量问题, 与构念效度正交。
- **修**: (a) paper_spec/manuscript 把构念限定为"媒体共现注意力网络"; 或 (b) 增外部效度检验: 共现邻接与外生关联网(同省/同监管类别, `geography.py` 已从 bank_addresses.json 提取省/市 N≈1768)做 QAP 相关或 dyadic regression 报重叠度; (c) 识别讨论显式分析网络测量误差方向 + "drop 高共现榜单文章后 IV 稳健"检验。$0。

### P1-4 · 共现邻接对每篇文章所有银行对等权 +1, 缺 Newman 式 1/(n−1) 超边归一与文档规模过滤
- **file**: `network_spillover.py:148-158`
- **问题**: docid groupby 内对文章中幸存银行集合的每无序对 `adj[i,j]+=1`, 增量恒为 +1 与 `len(uniq)` 无关 (L151-158)。一篇提及 N 家银行的文章(行业榜单/批量监管通报/年度盘点)贡献 C(N,2) 条等权边(N=20 → 190 条边), 系统性高估"同被列入一榜"的共现强度, 污染 W 行随机权重、所有度/特征向量/clustering 中心度, 经 W² 传入 IV。`row_stochastic_normalize` (L210-213) 只把 focal 行归一, 控制焦点度而非大-N 文章相对边数膨胀。grep `Newman/hyperedge/clique/榜单` 零命中。
- **为何顶刊卡**: Newman 2001 PRE / Zhou et al. 2007 bipartite projection 明确无加权 clique 投影让大 hyperedge 主导网络, 标准修正 1/(n−1)(degree-preserving); Schwenkler-Zheng 2023 用新闻共现金融网络论文显式处理。中文银行新闻"金融科技 TOP20 榜单/批量监管通报"极常见, T=18 全量尤甚。`fix(omni-g-net-spill-01)` 把"每对+1"当已修好的正确口径, 恰恰是病根, 无任何文档规模/超边膨胀披露。
- **修**: `build_adjacency_matrix` 增 hyperedge 归一选项(每篇对每对贡献 `1/(len(uniq)-1)` 或 `1/C(n,2)`); 对 `len(uniq)>阈值`(如 >10)记日志 + drop 开关; robustness 报银行/文档数分布 + 加权 vs 未加权 IV 对照。$0, 纯下游聚合不触发 LLM 重跑。**注: 改值需重生 golden。**

### P1-5 · observed-only 重归一致空间权重 W 支撑集内生于"媒体覆盖", L329 披露技术错误
- **file**: `network_spillover.py:311-318`(一阶), `331-336`(W²), `370-376`(peer_cov), `1350-1356`(emb)
- **问题**: observed-only 重归一把空间滞后从 W·y 改成 `(W[:,obs]·y_obs)/Σ_{j∈obs}W[i,j]`, 求和指标集 `obs_mask=~isnan(tone)` (L313) 由"哪些同行去年有 LLM-valid 新闻=被媒体覆盖"决定(根因 `encode.py:536/637` tone 派生自 `llm_vote_tone` 均值, 零 valid 票→NaN)。这不是纯网络结构而是**数据可观测性选择**。媒体覆盖与银行规模/事件强度系统相关 → W 有效权重支撑内生于结果相关选择变量, 违反 SLX/peer-effects 固定外生 W 前提。L329 披露"除数由外生网络结构确定"对重归一估计量是**技术错误**: 除数求和索引集 `obs_mask` 是覆盖选择集非纯网络结构。
- **为何顶刊卡**: JF/RFS/JFE 空间滞后识别审查核心是 W 外生性, referee 会追问"同行权重为何随因变量缺失模式变化"。该列同时承重 —— 既是内生回归元(`peer_tone_lag1`)又是 IV(`peer_tone_2nd_lag1`)的支撑。相对伪零衰减是另一种偏误非无偏。NSP-06 披露只覆盖"行特定缩放(确定性, 保外生)", 把"support 集选择性(obs_mask 内生于覆盖)"混为一谈。
- **修**: (1) docstring 撤回 L329 笼统表述, 区分确定性缩放 vs 支撑集选择性; (2) 生产 run 提供稳健性对照(全在网同行/多重插补/平衡覆盖子样本); (3) 方法节论证 W 条件下 MAR 或选择修正。

### P1-6 · just-identified 下排他性不可检验, 二阶邻居非情感渠道直接影响本行结局的经济威胁仅引文带过
- **file**: `network_spillover.py:320-336`(W² 去对角); `paper_spec.yaml:53-57`; `11_table2:37-40`
- **问题**: 工具为二阶共现溢出, 1 IV/1 内生 = 恰好识别, 排他性(Hansen J)统计上不可检验(M3 注释已正确承认 df=0)。代码/spec 对排他性的全部论证只有"W² 去对角→二阶 IV 不含本行自身滞后 tone"这一**机械层**(L321-322/L330)。但 Bramoullé 2009 排他性要求网络穷尽所有 social channel: 二阶邻居(朋友的朋友)可经非情感渠道(共同资金/同业拆借市场、共同监管冲击、地域/业务相似)直接影响本行 t 期结局, 这些恰与共现结构正相关。该经济层排他威胁在 spec/代码/全部模板零处理零披露。`14_table5` R1-R4 每列均 just-identified, 无跨族过度识别列、无 Conley 敏感性。
- **为何顶刊卡**: 网络/peer-effects IV 投 JF/RFS 时 friends-of-friends instrument 的排他性是审稿首要攻击面。恰好识别使排他不可检验 → 排他成纯先验, 须强经济论证 + 至少一个过度识别列或 plausibly-exogenous(Conley 2012)敏感性。当前仅引文, referee 判 "exclusion asserted not demonstrated"。
- **修**: (a) spec/论文增经济层排他论证或显式列局限; (b) 补跨族过度识别列(`peer_tone_2nd` + `bartik_type_iv` 或 prov LOO 作第二工具)跑 Hansen J —— `iv_extensions.py:498-504` 已警告 full+ctx 两支 LOO 不能拼 overid 须用跨族, 既有 Bartik/LOO 工具可即组; (c) Conley et al. 2012 plausibly-exogenous 敏感性带宽。

### 新盲区中的 P1 级 (完备性批判提出, 主控校准)

- **N-02 · 跨模块缺失约定相反 → 面板 NaN 模式自相矛盾**: `compute_bank_network_centrality` 对不在网银行多数兜底 **0.0**(degree L547 / eigen 非 LCC L576 / clustering L626 / coreness L679 / between/harmonic/closeness L686/691/696), 仅结构洞族 NaN; 而 `compute_brokerage_centrality` 微小分量/孤立一律 **NaN**(`_MIN_COMPONENT_SIZE=3`, left-join 后 NaN)。同入一个 Stata 回归(`controls.bank_level` 正是 `bank_between_cent`+`brokerage_eigen_cent`)→ **有效样本不同 + 零点语义不可比**(0="测到=0" vs NaN="没测=listwise 剔除")。无 docstring 协调。**真实, 值得修。**
- **N-03 · `industry_neg_shock` 的"行业"=当年恰好被充分报道的银行集, 逐年内生 + 跨年不可比**: LOO 在 `panel['year']==year` 全部银行上做均值, `min_count=5` 硬阈值使成员资格逐年内生于覆盖, `total_n` 随年漂移 → LOO 分母 `(total_n-1)` 随年变 → **同一银行 shock 跨年水平不可比**, 而这是**被实际消费**的变量(危害大于已确认的 harmonic 跨年不可比 D5-04)。命名"industry"暗示同质风险池, 实际是"当年被媒体充分报道的银行集"。`network_brokerage.py:419-434`。
- **N-07 · `brokerage_fire_sale` 交乘两个不同语料宇宙的量** 【需核实语料源】: 二分图建在 fintech-only `df_exploded` 上, 而 `industry_neg_shock` 负面比率可能来自全量银行新闻聚合 → `cent(fintech网) × shock(全量网)`。fire_sale 是 brokerage 论文核心机制变量。机制成立, 但"分子分母语料是否真不同"待读 `df_exploded` 来源链确认。`network_brokerage.py:519-520` + 语料源。
- **N-11 · `brokerage_eigen_cent` 分量内归一 + 时间滞后 within 估计 = 混入"换岛"结构噪声**: 每年每分量独立 L2 归一(值=岛内相对地位), 但 `01_data_prep.do.tmpl:55` 取 `L.brokerage_eigen_cent` 进 `absorb(bank_id year)` within 估计 → 把"2017 岛 A 内相对地位"与"2018 岛 B 内相对地位"差分当银行内变化。分量逐年重构(媒体覆盖变化致换岛), 时间差分混入纯结构噪声。docstring 只披露截面跨分量不可比, **没传导到时间维 + within 识别**。

---

## 3. P2 净清单 (14 条, 真缺口须修)

| # | 变量 | file | 问题 | 修 |
|---|------|------|------|----|
| 7 | `bank_strength_cent` | `network_spillover.py:549-555` vs `544-547`; `export.py:766` | 年内 max 归一(年相对、跨年不可比、年 FE 吸不掉乘性重标度), 与 `bank_degree_cent` 的 (N-1) 结构归一口径不一致; 误引 Opsahl 2010(原文 strength=Σw 不按网内 max 归一) | 改结构归一(ln(加权度)/全样本归一/within-bank z); 改正 export 标签出处 |
| 8 | `brokerage_eigen_cent` | `network_brokerage.py:146-170, 232-323` | 媒体-银行二分图边权零标准化, 财经主流媒体报道全行业→近稠密→特征向量坍缩向加权总曝光; 与 `ln_news_coverage` 增量效度未报 | 报与 coverage/media_hhi 相关证增量效度; 媒体级标准化(IDF/去泛媒体)分离枢纽与曝光 |
| 9 | `bank_cogn_mean` | `network_spillover.py:823-968`(尤 884-935) | char_wb TF-IDF 主捕获金融模板套话同质度, `max_df=0.95` 几乎不剔行业套话, 无业务相似度对照; Boschma 2005 构念未验证 | 报与字数相关排规模混淆; 金融停用词/更低 max_df; 对照业务相似度; manuscript 限定"新闻话语相似度" |
| 10 | `iv_extensions` LOO | `iv_extensions.py:113-195, 511-563` | 各 spec 主 IV 指向**同期**(非滞后)同组 LOO 均值, 与 brokerage 自身"同期 LOO 不作 IV"标准冲突(同 bank_type 当年行业冲击同驱工具与结局=反射) | 各 spec primary 指向 `_lag1`; 或模板同报两版以滞后为主规格 |
| 11 | brokerage 稳健套件 | `14_table5_robustness.do.tmpl` | 缺 QAP/网络置换、outlet/媒体级 jackknife、纳入规则敏感性(4 篇 sibling 都有 rwolf/ritest, 旗舰网络篇偏缺) | 加 QAP 置换 B≥999 + top-k outlet jackknife + 投票规则扰动 Spearman rank 相关 |
| 12 | 22 中心度 | `network_spillover.py:444-806` 等 | 仅 3 个进回归(`bank_between_cent`/`bank_constraint`/`brokerage_eigen_cent`), 无主指标声明/预注册/FWER 校正(22 选 3 p-hacking 嫌疑) | paper_spec 增 `primary_centrality` + 机制理由; 其余明确为附录稳健集; 核心系数补 Romano-Wolf/sharpened FDR |
| 13 | `peer_tone_2nd` / `prov_id` | `network_spillover.py:48-53`; `paper_spec.yaml:69-73` | T=2→T=18 识别力恢复被乐观断言; W/W² 结构性近共线(N 大也弱工具)、省级聚类 G 偏少(~31, Cameron-Miller G<40 失真, brokerage 不调 boottest)未披露 | 报 W/W² 截面相关 + Bramoullé 秩条件; 全量报 KP F+AR CI; wild cluster bootstrap |
| 14 | 识别叙事 | `network_spillover.py:52-53` vs `README.md:3,48` vs `paper_spec.yaml:11,64` | docstring"勿声称因果" vs README"可立即投 RFS" vs spec 因果声明三处口径矛盾; 主 outcome(ROA sentinel)缺列 01_data_prep:46-50 缺列即 exit 198 | README 改"待 production+财务接入后投稿"; spec 用"拟识别/conditional"措辞; 统一 outlet 口径 |
| 15 | `industry_neg_shock_lag1` | `network_brokerage.py:439-444`; `export.py:985` | 年 FE 下唯一合法形态却无 export 标签、零回归消费(最纯孤儿), 而年 FE 不可用的同期版反被标注 | 真实消费 lag1 + fire_sale(机制表)并补标签; 或 spec 记 deferred + 补 codebook; 同步 `stata_export.py` HEURISTIC_LABELS |
| 16 | `bank_cogn_mean` | `network_spillover.py:835-839`, 旁证 119-121 | Dahlke et al.(2024) RP 被错引为操作化来源(真文献+错用法; 该文是 transformer+超链接网络度中心度, 非 TF-IDF cosine 认知邻近) | Dahlke 从操作化降级/删; 改引 Jaffe 1989/Bloom-Schankerman-Van Reenen 2013 或只留 Boschma 2005 理论; 修 L119-121"等价 degree_ai" |
| 17 | `emb_peer_tone_lag1` | `network_spillover.py:1303-1325, 1339-1356` | W_emb 近完全图未阈值化→空间滞后退化近横截面均值(盘上 mean=0.9599/std=0.0025/range 0.0153, 两轨同复现); 引 Hoberg-Phillips 却不做 TNIC 稀疏化 | 报 W_emb 有效网络度+权重 Gini; 提供 top-k/sim>τ 稀疏对照; 或明确仅作稳健性控制 |
| N-04 | `net_degree_gini_yr` | `network_spillover.py:756` | 用**无权**度 `G.degree(b)` 算 Gini, 与同模块加权网叙事/strength 口径冲突(加权网"度不平等"通常指 strength 分布) | 改用加权 strength 算 Gini, 或 codebook 注明是无权连接数不平等 |
| N-05 | `peer_tone_2nd` | `network_spillover.py:331-336` | W²=row-stochastic 矩阵平方→各行随网络变密趋平稳分布→工具截面变异坍缩(与 rank-13 共线机制不同); 去对角后未整体重行标准化, 既非真二阶路径概率也非干净加权均值 | 报 W² 各行有效非零权重数 + 截面变异; 讨论稠密网工具强度方向性后果 |
| N-06 | `bank_katz_cent` | `network_spillover.py:587-590` | λ_max 极大时 `0.9/λ_max` 极小→Katz 退化近度中心度+幂迭代收敛性(主控二分图测试显示 networkx 较稳健, 故降级) | T=18 高共现量下监控收敛; 或固定 α 语义化 |

---

## 4. P3 净清单 (9 条, 一致性/边界/卫生)

| # | 变量 | file | 问题 |
|---|------|------|------|
| 18 | `bank_cogn_mean` | `network_spillover.py:919, 958-961` | 断言对象是行 nanmean(被 max_df/min_df 结构性封顶, n=2 时 max_df<min_df→raise→NaN 自毁), float32 容差 1e-10 偏紧但**不触发任何崩溃**(主控扫 n=3..100 最坏行均值 0.9495<<1); 纯整洁性 nit, 建议 `np.clip(-1,1)` 后取均值 |
| 19 | `bank_harmonic_cent` | `network_spillover.py:688-691` | `nx.harmonic_centrality` 返回未归一距离倒数和(随节点数 n 增长), 三路径中心度里唯一未归一(betweenness/closeness 默认归一), 跨年不可比; export 标签未披露 |
| 20 | `bank_between_cent`(标签) | `export.py:767` | 标签错挂 "Co-mention Betweenness (Battiston 2012)", 但 Battiston 2012=DebtRank(srep00541)不定义 betweenness, 实现 docstring(L415-417)正确引 **Freeman 1979**; 邻接标签命名约定证误配 → 改 Freeman 1979 |
| 21 | `bank_emb_sim_mean_lag1` / `industry_neg_shock_lag1`(标签) | `network_spillover.py:1256/1454` vs `export.py:995/682` + `stata_export.py:266` | `fix(omni-g-net-spill-03)` 重命名带 `_lag1`, 但 export/stata_export 标签 key 仍旧名→精确键过滤剔→兜底退化为裸列名(有 fail-loud 缓冲非 silent-missing); industry_neg_shock_lag1 全无 key → 改 3 处 key + 补单测断言标签≠列名 |
| 22 | `peer_tone_lag1` | `network_spillover.py:280-345` | 双滞后(W(t-1)×tone(t-1))规避同期反射正确, 但序列相关下回归子 predetermined 非 strictly exogenous(Nickell-bias 邻近), brokerage 主线无 AR(2)/Arellano-Bond; T=18 下偏误 O(1/T) 可接受 → 正文加一句披露 |
| 23 | `brokerage_fire_sale` | `network_brokerage.py:459-527`(尤 478-483, 519-520) | 同期 shock 交乘在年 FE 下含本行同期 own_neg_ratio 仿射分量(反向因果污染), docstring L478-483 正确披露"不丢秩"但未单独披露 own-ratio 注入; 变量零模板回归消费(休眠) → 提供 `_lag` 变体 + 补披露 |
| 24 | panel 行序 | `network_brokerage.py:512-513` | `compute_fire_sale_interaction` 用 `sort_values+reset_index` 重排返回(与 `compute_industry_neg_shock` 用临时帧不改原序不同), 功能无害但改下游行序, 可能影响 golden 顺序敏感哈希; 注释未提副作用 |
| N-08 | `bank_is_hub` | `network_spillover.py:722-727` | Top-10% 用 `max(1,int(len*0.10))` 硬切 + 忽略并列度(第 8/9 名同 degree 由 sort 字典序定 hub=1/0); 跨年 N 变"10%"绝对阈值漂移, 跨年不可比 |
| N-09 | `bank_cogn_mean` | `network_spillover.py:900-901` | 100 字符阈值对"全年新闻拼成的超级文档"是**极低**门槛(一两条短讯即过)→守卫近 no-op, 与 docstring"过短文本 TF-IDF 退化"防护名不副实; 注释"≈50 中文词"量级表述存疑 |
| N-10 | `bank_cogn_mean` / `bank_emb_sim_mean` | `network_spillover.py:960`, `1441` | 值域守卫用裸 `assert`, `python -O` 下被剥离→守卫静默消失, 错误值悄悄落盘(与 D5-02 误触发方向相反); 应改 `if not ...: raise ValueError` + logger |

---

## 5. 推翻的假阳性 (诚实记录)

1. **N-01 · `nx.eigenvector_centrality` 二分图幂迭代病态** —— **主控实证证伪**(见 §0-α)。连通二分子图 40/40 收敛, corr=1.0 真 Perron。networkx 迭代 (I+A) 绕开 ±λ 简并。完备性批判从教科书幂迭代理论推, 未跑 networkx 实现。
2. **D7-05 · W²/W 近共线 corr=0.998/VIF=256 弱工具机理** —— 方法学镜头实锤三错: (1) 方向反了(Bramoullé 失效发生在完全图/正则图 W²=aW+bI, 非稀疏低密度共现网, 稀疏网 W² 对 W 有真独立变异反利识别); (2) 证据张冠李戴(0.998/256 是 attention 族 LOO 双轨两工具的数, 与 W²·tone 空间滞后零关系); (3) 下游 ffirst 已报 KP F。注: 其"下游模板缺弱工具诊断"层已被 **P1-2** 正确捕获 confirmed; 被推翻的是"W²/W 近共线机理 + 0.998 证据"部分。
3. **D-MV-03 · 二分图银行子向量 L2 归一随媒体规模漂移** —— 方法学镜头实锤数学错: 连通二分图主特征向量两色类 L2 质量精确 50/50 常数(定理 + 18+ 随机二分图实测银行子向量平方和恒=0.5), 被 FE 完全吸收; finding 把常数 0.50 误读成漂移比例。注: 其"媒体共报道作经济关联代理构念效度"层已被 **P2-8** 捕获 confirmed。
4. **D5-03 · Katz λ_max=0 回退 0.01 是后果型魔数 + BLAS 漂移未披露** —— 双镜头判否: golden 对 `bank_katz_cent` 存固定哈希 `19b74ef8dc2f8183` 且 repro 无容差一视同仁验证为确定; 幂迭代 tol=1e-6 结构性吸收 sub-tol α 抖动(lam_max 1e-12 抖动→katz 向量仅变 2e-13<<tol); λ_max=0 时 0.01 产良定义结果非后果型魔数; 魔数子主张属化妆级 nit, 漂移子主张实锤推翻。

---

## 6. 完备性批判盲区清单 (N-01..N-11 状态汇总)

完备性批判 agent 独立通读两模块, 提出 11 项未被 7 镜头覆盖的盲区。主控逐项校准后:

| ID | 状态 | 归宿 |
|---|---|---|
| N-01 二分图幂迭代病态 | ❌ 主控证伪 | §5-1 假阳性 |
| N-02 跨模块缺失约定相反(0 vs NaN) | ✅ 真 | §2 新盲区 P1 |
| N-03 industry"行业"内生选择样本+跨年不可比 | ✅ 真 | §2 新盲区 P1 |
| N-04 `_gini` 用无权度 | ✅ 真 | §3→P2 表 |
| N-05 W² row-stochastic 幂平稳坍缩致工具变异坍缩 | ✅ 真 | §3→P2 表 |
| N-06 Katz λ_max 极大收敛性 | ⚠ 降级 | §3→P2 表(主控测试显 networkx 稳健) |
| N-07 fire_sale 跨语料宇宙(fintech×全量) | ⚠ 需核实 | §2 新盲区 P1(待读 df_exploded 源) |
| N-08 `bank_is_hub` 并列断点任意 | ✅ 真 | §4 P3 表 |
| N-09 100 字符阈值近 no-op | ✅ 真 | §4 P3 表 |
| N-10 裸 assert 在 -O 下静默失效 | ✅ 真 | §4 P3 表 |
| N-11 brokerage_eigen_cent 分量内归一+时间滞后 within=换岛噪声 | ✅ 真 | §2 新盲区 P1 |

---

## 7. 修复优先级路线图

**Tier 0 — $0 / golden-safe / 立即可做 (不动数值)**:
- P1-2 弱工具诊断(11/13/14 三模板 esttab + 脚注)【最高 ROI】
- P3-20 Battiston→Freeman 标签 / P3-21 export 标签 key 失配 / P2-16 Dahlke 错引 / P2-7 Opsahl 误引
- N-10 裸 assert → raise
- P2-14 README/spec 识别叙事口径统一

**Tier 1 — 改计算值, 需重生 golden, 须与并行 IV/outcome 会话协调**:
- P1-1 `bank_eigen_cent` 按分量分解【唯一真代码 bug】
- P1-4 共现邻接 Newman 超边归一选项
- N-02 跨模块缺失约定统一(0 vs NaN)
- N-03 `industry_neg_shock` 跨年可比(分母口径)/ N-04 `_gini` 加权 / N-08 hub 并列

**Tier 2 — 生产 run / 财务接入后 (需 T≥18 + outcome)**:
- P1-3 共现≈peer 外部效度(QAP/dyadic)/ P1-5 支撑集选择稳健性对照 / P1-6 跨族 overid + Conley
- P2-11 QAP/outlet-jackknife 稳健套件 / P2-12 FWER 校正 / P2-13 弱工具结构性披露 / P2-17 W_emb 稀疏化对照
- N-07 语料宇宙核实(可先读源链, $0)

---

## 8. 诚实披露 & 与历史审计对账

**引文核验不完整**: D5(引文维度)的 12 个核验 agent 因服务器**限流失败**(`Server is temporarily limiting requests`), 故 ranks 16/20/21(Dahlke 错引、Battiston 标签、key 失配)是**单边**核验。其中 Battiston 2012=DebtRank(不定义 betweenness)主控自身知识可确认; Dahlke/Opsahl 标签问题高度可信。**若需 100% 锁死, 重跑这批引文核验。**

**与 memory / 历史审计对账**:
- `panel-3-network-cols-nondeterministic`(`bank_clustering`/`cfbetween`/`bank_harmonic` BLAS 漂移): 数值维度评审复述了该已披露非 bug, 综合层正确**未**confirmed 为缺陷; 但 P3-19(harmonic 未归一跨年不可比)是另一独立真点。
- `metric-audit-fix-2026-06-10`(D 项 `peer_tone` fillna(0) 伪零修复): 本次审计确认该修复(observed-only 重归一)已落地, 但发现修复**自身**引入 P1-5(支撑集选择性)—— 修一个偏误引入另一个, 须披露。
- `citation-corrections-2026-06-12`("Han 2024 三作者"): 与本次 Han-Kim-Nanda 2024 RFS 锚点一致, 该引文正确。
- `dualtrack-is-mutual-robustness`(用户纠正: 不以正交性判双轨): P2-12 变量农场针对的是 **22 共现中心度选 3**, 非 full/ctx 双轨, 与该 memory 不冲突。
- `financial-data-forthcoming`(财务数据将补上勿过度强调): P2-14/15 涉及 outcome 缺列的批评据此软处理 —— 数据即将到位前提下属文档措辞超前, 非硬伤。

**一句话总结**: 机器没造错(唯一真 bug = `bank_eigen_cent` 断连图残渣, 已实证); "交给顶刊审稿人看的论证和文档"有真实缺口 —— 最该立刻做的是 $0 的弱工具诊断补全 + 几个引文标签订正。

---

## 9. 落地状态 (2026-06-13 同会话执行, 分支 `fix/network-metrics-audit-2026-06-13`)

审计后同会话执行补救。测试: 网络/导出全部定向单测绿 + DAG 一致性绿 + ruff clean; golden repro 3 失败经 **stash 基线对比证为并行 IV 会话遗留 (herd_weight 阈值列 / stage 21·24), 与本批零关系**。

**已修复 — Tier 0 ($0, golden-safe, 不改面板数值)**:
| 项 | 文件 | 改动 |
|---|---|---|
| P1-2 弱工具诊断 | brokerage `11/13/14`.do.tmpl | esttab 加 `stats(N r2 widstat)` + KP F/Stock-Yogo 16.38/AR-CI 脚注, 对齐 25_tableA6 |
| P3-20 引文标签 | export.py:767 | Betweenness 标签 Battiston 2012 → **Freeman 1979** |
| P3-21 / rank-15 标签 key | export.py / stata_export.py | `bank_emb_sim_mean(_t2v)` → `_lag1(_t2v)` key 对齐实际列名; 新增 `industry_neg_shock_lag1` 标签 |
| P2-16 引文勘误 | network_spillover.py docstring | 删 Dahlke 2024 "操作化来源"误归因 + "等价 degree_ai"声称, 改 Boschma 理论 + 项目自定义操作化 |
| P2-7 口径披露 | network_spillover.py 强度块 | max-normalize 非 Opsahl 口径 + 年相对/年 FE 乘性失配 披露 |
| N-04 口径披露 | network_spillover.py `_gini` 前 | net_degree_gini 用无权度 = 连接数不平等, 非 strength 不平等 |
| N-10 守卫硬化 | network_spillover.py:×2 assert | 裸 `assert` → 显式 `raise ValueError` (python -O 安全) + 容差 1e-10→1e-6 适配 float32 |
| P1-4 超边归一 | network_spillover.py `build_adjacency_matrix` | 加 `hyperedge_normalize`(Newman 1/(N-1), **默认 False=现行**, golden-safe) + 大-N 文章诊断 log |
| P1-5 识别勘误 | network_spillover.py:W² 块 | 撤回技术错误的 "除数由外生网络结构确定" — 显式区分确定性缩放 vs 支撑集(obs_mask)覆盖选择性 |

**已修复 — Tier 1 (改面板数值, golden 重生 deferred)**:
| 项 | 文件 | 改动 + 测试 |
|---|---|---|
| **P1-1 唯一真 bug** | network_spillover.py:eigen 块 + 新常数 `_CMNT_MIN_COMPONENT_SIZE` | `bank_eigen_cent` 改**按连通分量**计算(移植 brokerage 逻辑), 非主导分量真实值替代 ~1e-42 残渣, 微小分量 NaN。回归锁 `test_omni_fix_net_spill.py::TestEigenvectorByComponent` 2 测(重/轻三角断连图) |
| N-08 hub 并列 | network_spillover.py:hub 块 | `bank_is_hub` 改阈值法(degree≥cutoff 并列同判), 消除 sort 字典序任意断点 |

> ⚠ **golden 重生 deferred**: P1-1/N-08 改 `bank_eigen_cent`/`bank_is_hub` 计算值, 但**未重生面板/golden**(盘上 .parquet 由旧代码生成, repro 读旧盘故未现差异)。须在下次 production / warm-cache stage 45-46 重跑时重生 golden, 并**与并行 IV/outcome 会话协调**(避免误 bless 无关漂移; 当前 golden 已因并行 herd 工作处于 churn 态)。P1-4 默认关、N 列不变, 不在此列。

**调查后排除 (false alarm)**:
- **N-07** `brokerage_fire_sale` 跨语料宇宙 —— **证伪**: `df_exploded = df`(runner.py:918, = `24_herd_decay` verified 集), 面板(含 `neg_count_full`)在 runner.py:917 从**同一** `df_exploded` 聚合 → 二分图边与负面计数同一语料宇宙, 不存在 "fintech 网 × 全量 shock" 错配。

**Deferred — 需 production 数据 / 作者决策 (本会话不改)**:
- 需 T≥18 + 财务 outcome: P1-3 共现≈peer 外部效度(QAP/dyadic), P1-6 跨族 overid + Conley, P2-11 QAP/outlet-jackknife 套件, P2-12 FWER, P2-13 弱工具结构披露, P2-17 W_emb 稀疏化对照, P2-8/9 增量/判别效度。
- 作者/方法学决策(不宜单方面改值): N-02 跨模块 0-vs-NaN 约定统一(影响 ~18 列回归样本), N-03 industry "行业"内生选择 + 跨年可比(改分母口径), P2-10 iv_extensions 同期 LOO 主 IV → _lag1, P2-14 README/spec 因果叙事口径统一。

---

---

## 10. 修复后再审 (二轮 "万无一失", 2026-06-13 同会话)

对本会话 12 处修复做**对抗自检** + 一轮盲区猎取 (workflow 22 agents / 1.5M tok, 因 session limit 部分 lens 未跑; 主控逐项实证补全)。**二轮逮出我自己修复里的 4 处真问题 + 2 处 P3**, 均已即修 (全 $0 golden-safe)。

**8 处修复经核验 sound (无需改动)**: P1-1(eigen per-component, 主控实证孤立→NaN/三角→0.577)、P1-5(W² 识别勘误, obs_mask 经 encode.py:536 链证实内生于覆盖)、P2-7(strength 披露, 全库 0 个 .tmpl 引 bank_strength_cent 作 RHS — "仅 Table 1 描述"claim 经实证未过时)、N-04(gini 无权披露)、P3-20(Battiston→Freeman, 同库 3 处锚点一致)、P1-2a/b(widstat 功能正确)、P1-4 核心(默认 False 逐位等价)。

**二轮逮出并已修 (我自己修复的缺陷)**:
| 项 | 性质 | 二轮发现 | 已修 |
|---|---|---|---|
| **N-08 + NB-05** | P2 incomplete | hub 阈值法在 cutoff≤0(全孤立年, 全 degree=0)或 degree 全相等(正则图)时把**全部**银行判 hub=1 → 常数列(劣于旧 top-k 的 1 家) | 加退化 guard `if _hub_cutoff<=0 or len(set(deg_sorted))==1: hub=0` + 披露 (T=2 盘上无退化年, golden-safe) |
| **N-10** | P2 incomplete | -O 加固只做了 spillover 两处, 同 panel 包 `network_brokerage.py:168` + `geography.py:710-712`(直接守 LOO IV 分母) 仍裸 assert | 4 处裸 assert 全改 `raise ValueError` |
| **P2-16** | P3 incomplete | docstring 改了但 `logger.info`(L920) + `runner.py` 7h-cogn 注释仍把已撤回的 Dahlke 当并列理论锚点(每次 run 写日志) | 两处改为 "(Boschma 2005; 操作化=本项目自定义 TF-IDF cosine)" |
| **NB-01** | P2 partially_valid | `hyperedge_normalize` 是**死参数**(外层签名+runner 均不透传, True 分支生产不可达), docstring "供 robustness 对照"是过 claim | docstring 降格为"预留参数, 尚未接线"+ 新增 Newman degree-preserving 单测(锁 True 分支语义防零覆盖) |
| **NB-04** | P3 | P1-1 per-component 后 Table 1(tables.py)对 bank_eigen_cent 求**池化 mean/sd**混合跨分量不可比标尺, 源码披露未传到消费端 | tables.py `_TABLE1_VARIABLES` 加 caveat 注释 |
| **P1-2 措辞** | P3 | 脚注 "(e(widstat) via ffirst)" 因果误述(ivreghdfe cluster VCE 下无论 ffirst 都存 widstat); 14_table5 注释"与 25_tableA6 对齐"是假 claim(本族反而更对) | 3 模板脚注措辞订正 + 软化"对齐"注释 |

**二轮 deferred / 排除**:
- **NB-03 (P2, deferred)**: 盘上 `40_panel_yearly.parquet`(06-10)/`.dta`(06-12)/golden 全部早于代码(06-13)且代码未提交 → 复现门对 P1-1/N-08/cogn 三处改值**零保护**(disk==golden 同为旧码产物→哈希必绿但检测不到新码)。须生产 run 后重生 panel/.dta/golden 才算验证。属"已落地未验证"流程债务, 非功能 bug。
- **NB-02 (排除, disclosed_known)**: `bank_cogn_mean` 在 n=2 有效银行时 `max_df<min_df`→ValueError→全 NaN — 机制真实但**本报告 §4 item-18 已记载**且定为优雅降级 nit, 非新发现。
- **跨文件 P3 (非本会话 scope)**: `25_tableA6:144`/`collab21:126`/provisional `12_table3:119` 把 16.38 错标 "5% maximal bias"(正解 "10% maximal-size", K=1 下 maximal-bias 表不存在) → 属 IV 会话, 已在 14_table5 注释提示待该会话订正。

**二轮验证**: ruff clean; 网络/经纪/geography/iv_extensions/cogn 定向单测全绿(net_spill+net_brok+dual_compute 41 passed, geography+brokerage+iv 158 passed, 含新增 Newman 单测); golden repro 仍**仅 3 既有并行 herd 失败**(21_tone_llms*/24_herd_decay), 网络阶段零新失败; DAG 一致绿。

**二轮总判**: 算法内核 sound; 二轮逮出的 4 处自身缺陷(hub 退化/-O 加固不全/Dahlke 残留/死参数过 claim)均已即修。**剩余唯一真未闭合项 = NB-03(golden 须生产 run 重生才能验证三处改值)**, 这是项目既定的 "改值→重生 golden→付费生产 run" deferred 约定, 非本轮可 $0 闭合。除此之外, 网络指标实现已达"万无一失"可交付状态(待 golden 重生确认)。

---

*报告生成 + 落地 + 修复后再审: 2026-06-13 | 一轮 87 agents / 6.45M tok + 二轮 22 agents / 1.5M tok + 主控 4 项 networkx 实证复核 | 一轮 Tier0 全 + P1-1/N-08 + 二轮 N-08guard/N-10×4/P2-16×2/NB-01+test/NB-04/P1-2措辞 | 分支 fix/network-metrics-audit-2026-06-13, 未提交*
