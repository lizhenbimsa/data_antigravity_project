# 网络指标扩展执行计划 (Network Metrics Expansion)

`v3 · 2026-06-21` · 审核轨迹: **v1 (9+3-agent)** → **顶刊级 52-agent 评审 (8 维 find → refute-first verify → 完整性批判)** → **v2 (21 条修订)** → **独立 32-agent ROUND-2 评审 (5 维 fresh, 再验 v2 修复是否落地无回归 + 主源再核)** → **v3 (round-2 确认 0 P0 / 0 净新 P1 correctness, 据 ~10 条 P2/NIT 精修)**。
transcript: `wf_47c7c059-02b` (v1) · `wf_3ab61202-16f` (v2 评审) · `wf_c003b6d2-531` (v3 round-2)。
权威前序 = `scripts/audit/NETWORK_METRIC_ELEVATION_BLUEPRINT_2026-06-13.md` (本计划是其 **follow-on**, 非重做)。

> **本文件仅为执行计划文档, 未改任何代码 / 未跑任何阶段 / 未碰 golden。** 与 `NONPOLARITY_DIMENSIONS_EXECUTION_PLAN_2026-06-20.md` 同性质 (plan-only 交付物)。

---

## 1. 白话总览 + 对前次评估的更正

**是什么**: 用户给的网络分析课程大纲 (复杂网络指标 / QAP / ERGM / 知识图谱 / LLM 建网 / node2vec) 对照本项目现有两套图 (银行×银行共现无向加权图 `G`; 媒体×银行二分图), 判定"还能加哪些网络指标"并落地为分波次执行计划。

**为什么**: 本项目网络层现有 **22 指标 battery (18 节点 + 4 网络级) + 二分图 `brokerage_eigen_cent`** (前次 elevation 已落地)。大纲列的若干算法 (modularity / 二分图原生中心度 / Gould-Fernandez 经纪角色 / QAP) **仍是真缺口**, 且大都能跑在**已建图**上, 增量价值高、成本低。

**影响 (按论文/模块)**: 主要利好 `brokerage_network` (经纪网络旗舰篇) —— 当前它的"经纪"测度只有 `brokerage_eigen_cent` (= prestige/声望, **非 brokerage**); 二分图 betweenness + Gould-Fernandez 角色分解才真正操作化"经纪"。其余 10 篇受益于新增的 G 网络级结构控制 (modularity/transitivity/giant_share) 作年度协变量。

**一句现实**: 真正能加的 = ①G 网络级结构控制 6 列 ②二分图 brokerage 原生中心度 5 列 ③Gould-Fernandez 经纪角色 **5 列 (无向图下 gatekeeper≡representative 合并)** ④QAP/null 两个验证阶段。**非** PageRank/ERGM/node2vec/知识图谱。

### ⚠ 更正前一轮口头建议 (诚实记录)
| 前一轮我说 | 审核实证 | 终判 |
|---|---|---|
| "PageRank 最高性价比, Wave-1 首选" | 前次 elevation **已将 PageRank/HITS/load 判 VIF-collinear variable-farm 驳回**; 审核实测 PageRank 与 `bank_degree_cent`/`bank_strength_cent` 高度共线; 且 `nx.pagerank` 默认走 `_pagerank_scipy`→MKL→BLAS-FP 非确定 | **REJECT** |
| "小世界 σ/ω 加进 Part C" | `nx.sigma/omega` 每调用建 nrand 随机重连图, 实测 40 节点即 3.2s/call; RNG-seeded + FP-fragile; 边际识别力低 | **DEFER** |
| "幂律指数 γ 检验无标度" | N≈86/年 → 幂律 MLE 统计无效; `powerlaw` 包未装; FP-fragile | **REJECT** |

---

## 2. 现状真相盘点 (盘上已有, 勿重复造)

**前次 2026-06-13 elevation 已交付 (do-NOT-duplicate)**:
- 22 指标 battery 全部已算并 left-join 进面板 (`network_spillover.py::compute_bank_network_centrality`): 18 节点 `bank_degree/strength/between/harmonic/eigen/katz/subgraph/cfbetween_cent + clustering/constraint/is_hub/ego_density/ci/effective_size/closeness_cent/eccentricity/avg_nbr_deg/coreness` + 4 网络级 `net_density/avg_cluster/avg_path/degree_gini_yr`; 二分图 `brokerage_eigen_cent`。
- `primary_centrality=bank_between_cent` / `secondary=brokerage_eigen_cent` + `centrality_battery(22)` + `network_roles` 块 (brokerage_network/paper_spec.yaml)。
- brokerage 六张 Stata 表 `15_table6`(centrality-outcome 描述性) / `16_table7`(mediation 附录) / `17_table8`(over-id IV) / `18_table9`(moderation 2SLS) / `19_table10`(het) / `20_table11`(FWER battery, `local battery`=22 列, wyoung/rwolf2) + 全 11 篇 network_roles 元数据。
- ⚠ **修订 (评审 D7-03 confirmed)**: `_shared/A_network_robustness.do.tmpl` **从未被创建** —— 蓝图 NET-SHARED-2 提议但未落地。它在 `paper_spec.yaml:120` (`external_validity_ref`)、`15_table6:87`、`17_table8:154` 有**悬挂引用 (phantom refs)**。故它**不在** do-NOT-duplicate 集; WS-D 须**择一**: (a) 作为 QAP 接线的一部分真正撰写 `_shared/` 宿主 .do.tmpl, 或 (b) 修复/删除三处悬挂引用。
- 已驳回且**勿原样重提**: PageRank/HITS/load (VIF-collinear)、causal-centrality-RHS+L2-IV (反向因果 fatal)、mediation 内生 (major)、新共现 peer-LOO IV (复活 0.998 共线撤回项)。

**前次 elevation 自己 DEFER 的 Tier-2 (= 本计划的旗舰新项)**:
> **Gould-Fernandez 1989 经纪角色分解** —— 蓝图明言"论文标题叫 brokerage 但只有 `brokerage_eigen_cent`(prestige 非 brokerage), 顶刊很可能**要求**此项"; networkx 无原生 API 须自实现。

---

## 3. v1→v2 评审返工 (52-agent 顶刊评审确认缺陷, 须先读)

| # | v1 缺陷 | 严重度 | 实证 (直读代码/Crossref) | v2 修复 |
|---|---|---|---|---|
| R1 | 重生链写 `45→46→51` (4 处: §10/§11/§13/§14) | **P1** | v3.11.0 panel-export shim 已 45→**40**; 盘上无 `45_*.py`; `run_production_regen.py:124` 调 `40_panel_export_main.py` | 全改 `40→46→51` (§3-R1 后全文) |
| R2 | GF 6 角色 (含 gatekeeper/representative 分列) | **P1** | 共现图 `G` 严格**无向** (adj 对称 L185-186); GF 1989 gatekeeper/representative 是**有向**角色, 无向图下二者**机械恒等** (perfect collinear) | GF 收为 **5 列** (gatekeeper≡representative 合并为 `gf_gatekeeper_rep`); 见 §6 |
| R3 | clique 投影膨胀只用于 DEFER ERGM, 未披露其污染 ADOPT 的 transitivity/modularity | **P2** | 一篇提及 N 行的榜单/通报投影为 K_N → `nx.transitivity(K4)=1.0`; 实测 30 行 clique 占年三角 100% | §7 WS-A 增 clique 膨胀披露 + `_hn` 稳健性孪生 (见 R4) |
| R4 | 未引用已存在的 `hyperedge_normalize` | **P2** | `build_adjacency_matrix` **已有** `hyperedge_normalize: bool=False` kwarg (Newman 2001 PRE 1/(N-1) 度守恒), 但 NB-01 未接线 | `_hn` 孪生复用该 kwarg, 同时关闭 NB-01 未接线缺口 |
| R5 | 新验证阶段只列 2 个计数锁 | **P1** | 漏第三锁 `tests/test_70_prompt_sensitivity.py:138` (逐字断言) + 源串 `run_pipeline_validation.py:123` "16 个验证阶段说明" | §7 WS-D / §9 / §12 增 THREE 锁 + 源串 + CLAUDE.md |
| R6 | ~16 新列无 VIF; 22-FWER family 未扩 | **P1** | plan 用 VIF 否决 PageRank 却给 5 二分图 (互相共线 + 与 `brokerage_eigen`/`bank_between` 共线) + `gf_total=Σ角色`(完全共线) 不设 VIF; `paper_spec families.centrality_battery` + `20_table11 local battery` 仍只 22 | §9/§11 增 VIF 筛 + FWER family 扩 |
| R7 | §2 列 `_shared/A_network_robustness.do.tmpl` 为"已交付" | P2 | 该文件从未创建 (phantom) | §2 已更正 |
| R8 | `bank_power_cent` 注 "无依赖" | P2 | nx **无原生 Bonacich power API**; power=Bonacich **1987** (AJS 92:1170-1182), 非 1972(=eigenvector, 已用于 `bank_eigen_cent`) | §5 注 "自实现 (Katz β<0)" + §11.9 拆 1972/1987 |
| R9 | `net_diameter_yr` "复用已算 ecc(L754)" | P2 | L754 ecc 是 `G_inv_lcc` 上**加权** ecc; 无权 diameter 须 fresh `nx.eccentricity(G_lcc)` | 改"复用 `G_lcc` 对象(L574), 非 L754 ecc 字典" |
| R10 | `net_modularity_yr` 未指定 `weight=` | P2 | `greedy_modularity_communities` 默认 `weight=None` 但 `nx.community.modularity` 默认 `weight='weight'` → 检测/打分口径不一致可致符号翻转 | §7 显式 `weight='weight'` 两处一致 |
| R11 | `net_assortativity_yr` 无退化守卫 | P2 | `degree_assortativity_coefficient` 在度-正则/方差零图返 NaN (T=2 常见) | §7 增 度方差=0→NaN 守卫 |
| R12 | GF 节点分组数据流未指定 | P2 | `bank_type_id` 仅存 `config/bank_list.yaml`; **无** pipeline 层 loader 映射 bank-name→type; `G` 节点无 group 属性 | §6 指定数据流 (载 yaml→映射→attach node-attr, key=target_bank) |
| R13 | 二分图 closeness "镜像 spillover L571-575" | P2 | L571-575 是 LCC 子图**构造**块, 非 closeness 守卫 (spillover closeness 跑全 `G_inv` 无 LCC 限制) | 改"复用 L574 子图模式自建 bipartite-LCC, 无现成 closeness 守卫可镜像" |
| R14 | networkx 未在 pyproject/requirements 声明 | P2 | 两模块经 `HAS_NETWORKX` 优雅跳过; clean install 会静默丢这些 golden 列 | §12 增"GF/二分图 load-bearing → 声明 networkx" |
| R15 | T=2 golden 风险只提"无 power", 未提"祝福即背离" | P2 | T=2 golden 只验 plumbing 不验 VALUES; GF 角色语义须 T=19 手核 | §9/§13 增 plumbing-only + T=19 ≥5 行手核 |
| R16 | 引文缩写 (Dekker/Han) + modularity 未署 CNM | NIT | Dekker-Krackhardt-Snijders 2007 Psychometrika 72(4):563-581; Han-Kim-Nanda 2024 RFS 37(9):2903-2935; greedy=Clauset-Newman-Moore 2004 | §11.9 全名 + 分离方法引文 |
| R17 | `.dta` 名写 "40/51_panel.dta" | NIT | 实名 `46_panel_yearly_full.dta` + `51_panel_with_controls.dta` | §14 已改 |

> **未确认/驳回 (不改)**: clique 膨胀对**正确实现的** GF **无效** —— 经典 GF 只数"端点不直连"的 2-path (a,c 非邻接), 故 GF 对 clique **天然鲁棒** (评审 D5-01 自反驳); 本计划 GF 落地须按经典定义**排除直连端点对**。`bank_degree_cent` 等锚点行号未受 v3.11.0 重编号影响 (重编号只动 NN_*.py shim, 不动模块内行号)。

### 3.1 v2→v3 ROUND-2 精修 (独立 32-agent 评审, 0 P0 / 0 净新 P1 correctness)
| # | v2 残留 | 严重度 | 实证 | v3 修复 |
|---|---|---|---|---|
| Q1 | R12 自造 `bank_list.yaml::bank_type_id` loader | P2 | **既有生产 SSOT** `pipeline/panel/iv_did.py::load_bank_group_maps()` 已映射 bank-name→type (nfra_type→soe/joint/city/rural...), 被 `runner.py:2314`/`iv_extensions` 调用; 面板已有 `bank_type` 列 (`runner.py:1167,1351`) | §6 改**复用** `load_bank_group_maps()` (勿重造); §11/§12 增 loader 单测 |
| Q2 | `net_transitivity_hn_yr` 作 clique-鲁棒孪生 | P2 | `nx.transitivity` **只看边存在性, 忽略权重** → `hyperedge_normalize` (纯重权) 对 transitivity **零鲁棒性**, `_hn` 列与主列**列哈希全同** = 浪费 1 golden 列 | **删** `net_transitivity_hn_yr`; `_hn` 仅 scope 到**加权** `net_modularity_hn_yr`; transitivity 真 clique 修复 = 文章规模上限/披露 (非重权) |
| Q3 | Bonacich `可选` (§5) vs Tier-2 DEFER (§8/§13) 冲突 | P2 | 读者无法判定是 now-可选还是 defer | §5 verdict 改 `可选→DEFER (Tier-2)`; §9.2 注"启用则扩 BLAS-FP 排除集" |
| Q4 | net 级年广播列在年 FE 下不可识别未明示 | P2 | density/giant_share/n_components/modularity/assortativity/diameter 年内**恒定** → 年 FE 下与年哑变量完全共线被吸收 (既有 4 net_*_yr 同病) | §7 WS-A 增"仅可作无年-FE 控制或与 bank 级交乘"披露 |
| Q5 | GF 计数约定未明示 | P2 | 无向 2-path 须**唯一计数** (a<c canonical, 排除 a-c 邻接); gf_total 定义 | §6 明示计数约定 |
| Q6 | VIF 筛漏 net 级族 (round-1 D5-10 残留) | P2 | `net_n_components_yr`/`net_giant_share_yr`/`net_density_yr` 近机械共线 | §9.6 VIF 显式纳 net 级族 |
| Q7 | codebook `_infer` token 扩展非具体 + 触点清单不全 | P2 | 实测**所有** net_*_yr (含既有 4) + gf_* + brok_bip_clustering_ra/node_redundancy 今天即落 UNKNOWN/OTHER; STATA_LABELS 全 16 列 + run_pipeline_validation 124-140 逐阶段行 (+76/+77) 未在触点清单 | §7/§12 补具体 token + 全量触点 |
| — | NIT | NIT | `run_production_regen.py` 补 `scripts/migrate/` 前缀; "~16"→"16"; GF "5 角色↔5 列巧合" 防误读注; WS-E 同享 T=2 caveat; 第三计数锁引全行字面 | 已并入 |

> **Round-2 元结论**: v2 较 v1 真改进; 残留全为 P2 披露/复用/触点完整性 + NIT, **无新 correctness 缺陷**。收敛信号明确 (v1=8 P1 → round-2=0 净新 P1), 再审边际收益已低。

---

## 4. WS-0 提交/重生前置门 (铁律, 必先满足)

1. **干净工作树**: 当前 `git status` 有多个并行会话脏文件。golden 重生**必须 clean worktree** (SOP §前置 #5), 否则误祝福并行漂移。开工前 `git stash`/隔离, 仅留本任务文件 by-name。
2. **备份**: `cp tests/fixtures/golden_panel_v0.json _regen_backup_20260621/`。
3. **canonical env 一次性导出**: `PYTHONHASHSEED=0 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_NUM_THREADS=1 KMP_DUPLICATE_LIB_OK=TRUE NEWS_PROCESS_LLM_OFFLINE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`, 用 `F:/Anaconda3/python.exe` (注: `run_production_regen.py:118` 只设 PYTHONHASHSEED+OFFLINE, **不**钉 BLAS 线程 = 已知缺口, 须手动 export)。
4. **重生≠no-op 警示**: 即便代码不变, canonical env 重生可能改若干既有测度列 (memory `golden-regen-omp-determinism`: 旧 golden vs HASHSEED=0 曾差 ~49 列) → **须用户批准**才提交 golden。
5. **盘面 T=2 限制**: 本机 `data/raw` 空/T=2, 仅验管道连通; T=2 golden **只验 plumbing 不验 VALUES**; 真值待 production T=19。

---

## 5. 核心设计: 三层判定 (adopt / defer / reject)

| 候选 | 列名/产物 | 层级 | 图 | 确定性 | 新依赖 | golden | 终判 |
|---|---|---|---|---|---|---|---|
| Gould-Fernandez 经纪角色 (无向, 5 列) | `gf_{coordinator,itinerant,gatekeeper_rep,liaison,total}` | 节点 | cooc+分组 | yes (纯计数, 排除直连端点) | 无 (自实现) | regen | **ADOPT (旗舰)** |
| 二分图介数 | `brok_bip_between_cent` | 节点 | bipartite | yes | 无 | regen | **ADOPT (真经纪测度)** |
| 二分图度 | `brok_bip_degree_cent` | 节点 | bipartite | yes | 无 | regen | ADOPT |
| 二分图聚类 (Robins-Alexander) | `brok_bip_clustering_ra` | 节点 | bipartite | yes | 无 | regen | ADOPT |
| 网络模块度 | `net_modularity_yr` (greedy, **weight='weight'**) | 网络 | cooc | yes (CNM 2004, 无 RNG) | 无 | regen | ADOPT |
| 度相关性 | `net_assortativity_yr` (**度方差=0→NaN 守卫**) | 网络 | cooc | yes | 无 | regen | ADOPT |
| 全局传递性 | `net_transitivity_yr` (fresh call; **clique 膨胀披露**) | 网络 | cooc | yes | 无 | regen | ADOPT |
| 直径 | `net_diameter_yr` (unweighted, fresh `eccentricity(G_lcc)`) | 网络 | cooc | yes | 无 | regen | ADOPT |
| 巨片占比/分量数 | `net_giant_share_yr` / `net_n_components_yr` | 网络 | cooc | yes | 无 | regen | ADOPT |
| 二分图接近 | `brok_bip_closeness_cent` (**自建 bipartite-LCC**) | 节点 | bipartite | yes | 无 | regen | adopt-with-care |
| 二分图冗余 | `brok_bip_node_redundancy` (**degree≥2 预过滤铁律**) | 节点 | bipartite | yes | 无 | regen | adopt-with-care |
| QAP/MRQAP | `eval_reports/76_network_qap.csv` | 模型 | cooc×geo×cogn | needs-seed(42) | 无 | **不动** | ADOPT (新验证阶段) |
| Null-model z-score | `eval_reports/77_network_null.csv` | 模型 | cooc vs ER/config | needs-seed(42) | 无 | **不动** | adopt-with-care |
| Bonacich power | `bank_power_cent` | 节点 | cooc | blas-fp | 无 (**nx 无原生 API, 自实现 Katz β<0**) | regen | **可选→DEFER (Tier-2)** (Bonacich **1987**, β<0; blas-fp 须扩排除集, 见 §8) |
| Louvain 社区 + 角色 | `bank_community_id` + 参与度/within-module-z | 节点 | cooc | needs-seed+canonical-id | 无 | regen | **DEFER→T=19** |
| PageRank | `bank_pagerank_cent` | 节点 | cooc | blas-fp | 无 | regen | **REJECT** (前次已否+共线) |
| 幂律 γ | `net_powerlaw_gamma_yr` | 网络 | cooc | blas-fp | powerlaw | — | **REJECT** (小 N 无效+缺依赖) |
| 小世界 σ/ω | `net_smallworld_{sigma,omega}_yr` | 网络 | cooc | needs-seed | 无 | regen | **DEFER** (贵+边际低) |
| 投影 battery | `brokshare_*` (~18 列) | 节点 | projection | 部分 blas-fp | 无 | regen | **DEFER** (近翻倍列面) |
| ERGM/TERGM | `eval_reports/*` | 模型 | cooc | needs-seed | R statnet + R-bridge | 不动 | **DEFER** |
| node2vec | `<NN>_node2vec_embeddings.parquet` | 嵌入 | cooc | needs-seed (脆) | node2vec+gensim | regen | **DEFER** (SVD/spectral 无依赖替代) |
| LLM/KG 三元组 | `<NN>_kg_triples.parquet` | 网络 | new | no | 付费 API | schema 3→4 | **DEFER** |

**计数**: ADOPT 面板列 = WS-A 6 + WS-B 5 + WS-C 5 = **16 列** (+ 可选**加权** `net_modularity_hn_yr` 1; Bonacich 已 DEFER 见 §8; **`net_transitivity_hn_yr` 删** —— transitivity 忽略权重, `_hn` 对其为 no-op, 见 §3.1 Q2)。
**非目标**: 不为凑指标加 VIF 共线 variable-farm; 不在 T=2 声称因果/时序结构; 不引随机性回归项 (node2vec/ERGM-MCMC)。

---

## 6. 旗舰: Gould-Fernandez 经纪角色 (WS-C, 顶刊很可能必需)

**动机**: brokerage 篇唯一"经纪"列 `brokerage_eigen_cent` 是**特征向量声望**, **不是经纪** (桥接否则不相连的群体)。

**无向图下的正确角色集 (R2 修订)**: GF 1989 原定义在**有向**交易网, 5 角色 = coordinator / itinerant(consultant) / gatekeeper / representative / liaison。本项目 `G` 严格**无向** (adj 对称) → 每条 2-path `a-i-c` 即其自身逆, **gatekeeper 与 representative 机械恒等** (实测 40 节点图 node-by-node 完全相同, perfect collinear)。故落地为 **4 个可区分角色 + 总计 = 5 列**:
- `gf_coordinator` (a,i,c 同群) / `gf_itinerant` (a,c 同群, i 异群) / `gf_gatekeeper_rep` (**gatekeeper≡representative 合并**, 一端跨群) / `gf_liaison` (三方互异群) / `gf_total`。
- 须在 codebook **显式披露**无向坍缩假设; 不得分列 gatekeeper/representative (否则 2 列完全共线, 重蹈 plan 自己否决的 variable-farm)。
- **可选 (b) 延后**: 若要区分 gatekeeper/representative, 须构造**有向关系** (如 larger→smaller bank / 时序-来源不对称), 属新构念, DEFER→T=19。

**clique 鲁棒性 (R3 关联)**: 经典 GF 只计**端点不直连** (a,c 非邻接) 的 2-path 中介 → GF 对 clique 投影**天然鲁棒** (一篇榜单把 N 行投成 K_N, 内部全互邻 → GF 中介计数为 0, 不膨胀)。**落地铁律**: 实现时**排除 a-c 已有边**的 2-path (经典 GF), 否则退化为朴素全-2-path 会被 clique 虚增。

**计数约定 (Q5 明示)**: 每条无向 2-path `a-i-c` **唯一计数** (canonical `a<c` 字典序, 不重复计正/逆), 且**排除 a-c 已邻接** (经典 GF); 跨群 2-path (一端异群) 归 `gf_gatekeeper_rep`; `gf_total = gf_coordinator + gf_itinerant + gf_gatekeeper_rep + gf_liaison` (单测守恒)。

**节点分组数据流 (R12 修订 → Q1 复用既有 SSOT)**: `G` 节点是 bank-name 字符串、**无 group 属性**; ⚠ **勿重造 loader** —— 既有生产 SSOT **`pipeline/panel/iv_did.py::load_bank_group_maps()`** 已把 bank-name 映射为 type (源 `config/bank_addresses.json::nfra_type` → `soe/joint/city/rural/private/foreign/other`, 1768 行), 已被 `runner.py:2314` / `iv_extensions` 调用, 且面板已携 `bank_type` 字符串列 (`runner.py:1167,1351`)。落地: ① GF 模块 import 复用 `load_bank_group_maps()` 得 `target_bank→type`; ② GF 计算前把 type 作 node-attr attach 到 `G` (key 严格匹配 `target_bank`); ③ 名键未命中 → 该行 GF 全 NaN。`nfra_type` 类别与 `bank_list.yaml::bank_type_id`(int 1-8) 一一对应; 分组源**推荐 nfra_type 短码** (与既有 `bank_type` 列同源), province 作稳健性。§11/§12 须单测该 loader 复用 + 名键匹配率。

**落点**: `network_spillover.py` per-year 块 (节点结果存储前), 读已建 `G` (只读, 不重排节点/不重建图 —— 加性铁律); 纯计数→**确定性、golden-safe-logic**。退化守卫: 单成员群/零方差→0/NaN 约定 (镜像 `bank_constraint` L686-688)。

---

## 7. 分波次推进 (golden-safe 优先)

### WS-A · G 网络级结构控制 (6 列, $0, 全确定性, 无新依赖)
- 落点: `network_spillover.py` Part C `net_yr` dict (在 `net_results[year]=net_yr` 前)。复用 scope 内 `G`(L553)/`components`(L572)/`lcc_nodes`(L573)/`n_nodes`(L549)。
- 列与口径:
  - `net_modularity_yr` = `greedy_modularity_communities(G, weight='weight')` + `modularity(G, comms, weight='weight')` (**R10: 两处显式同 `weight='weight'`**, 否则检测无权/打分有权口径不一致可符号翻转); 确定性 (CNM 2004, 无 RNG, **非 louvain**)。
  - `net_assortativity_yr` = `degree_assortativity_coefficient(G)`; **R11 守卫**: 度方差=0 (正则/平凡图, T=2 常见) → NaN (镜像 L686-688 约定)。
  - `net_transitivity_yr` = **fresh** `nx.transitivity(G)` (非"复用", 见 R-D8-11); 全局传递性, 与 `net_avg_cluster_yr`(W-S 局部加权) 构念不同。
  - `net_diameter_yr` = **fresh** `max(nx.eccentricity(G_lcc).values())` (unweighted; **R9: 复用 `G_lcc` 对象 L574, 非 L754 的加权 ecc 字典**); `len(lcc)>=2` 守卫镜像 N3 L813。
  - `net_giant_share_yr` = `len(lcc_nodes)/n_nodes` / `net_n_components_yr` = `len(components)` (复用 L572-573, 零额外计算)。
- 自动经 `panel.merge(net_df, on='year')` (L863) 广播; **无 merge/runner 改动**。
- **R3/R4/Q2 clique 膨胀披露 (codebook)**: `net_transitivity_yr` / `net_modularity_yr` 被多行文章 C(N,2) clique 投影**向上虚增** (一篇 30 行榜单可独占年三角 100%)。须 codebook 如实披露。⚠ **Q2 修订**: `hyperedge_normalize` 只**重权**不改**边是否存在**, 而 `nx.transitivity` **忽略权重只看边存在性** → `_hn` 对 transitivity 是 **no-op** (列哈希与主列全同, 浪费 golden 列) → **删 `net_transitivity_hn_yr`**。`_hn` 孪生**仅限加权** `net_modularity_hn_yr` (复用 `build_adjacency_matrix` 已存在但未接线的 `hyperedge_normalize=True`, Newman 2001 PRE 度守恒 1/(N-1), 同时关闭 NB-01 缺口; 须接 config+runner 透传)。`net_transitivity_yr` 的**真** clique 修复 = 文章规模上限 (≤K 行) 或纯披露, **非重权**。`_hn` 改值随主列一并 golden 重生; 可 DEFER 至 T=19。
- 披露 (同 N-04 口径): transitivity(全局) vs `net_avg_cluster_yr`(加权局部) 分别标注; diameter LCC-only。
- **Q4 年 FE 不可识别披露 (铁律)**: 全部 net_*_yr (新 6 + 既有 4) 是**年度广播列**, 年内对所有银行**恒定** → 在含 `year` FE 的规格中与年哑变量**完全共线被吸收** (无识别力)。故只可作 **(a) 无年-FE 描述性控制**, 或 **(b) 与 bank 级变量交乘** 进入。codebook + paper_spec 须明示, 勿当年 FE 下主 RHS。

### WS-B · 二分图 brokerage 原生中心度 (5 列, $0, 确定性, 带守卫)
- 落点: `network_brokerage.py` per-year 循环 (`bank_nodes` 已抽 L289-290), merge 镜像 `brokerage_eigen_cent` L311-318。
- 列 (优先序):
  - `brok_bip_between_cent` (旗舰, Han-Kim-Nanda 2024 经纪动机 + Freeman 1979 / Borgatti-Everett 1997 二分图中心度方法; **R-D6-08: 经纪动机引文与方法引文分离**)。
  - `brok_bip_degree_cent` (除以当年媒体数 → 年内相对, 年 FE)。
  - `brok_bip_clustering_ra` (`mode='dot'` Robins-Alexander 2004, codebook 标注变体)。
  - `brok_bip_closeness_cent` (**adopt-with-care; R13**: 二分图 closeness 在断连图跨分量不可比 [实测孤立点 1.5 vs 连通 1.0]; **无现成 closeness 守卫可镜像** —— spillover closeness 跑全 `G_inv` 无 LCC 限制。须**复用 L574 的 `G.subgraph(lcc_nodes)` 子图构造模式自建 bipartite-LCC** 并限制, 或 codebook 披露跨分量不可比)。
  - `brok_bip_node_redundancy` (**adopt-with-care; degree≥2 预过滤铁律**: `node_redundancy` 对 degree<2 节点 `raise NetworkXError` 崩整阶段; 须传 `nodes=[b for b in bank_nodes if B.degree(b)>=2]`, 其余 NaN, 镜像 L686-688; **不得**裸调 `node_redundancy(B)` 全图 [会迭代 media 端单边节点同样崩])。
- 全部 `nx.bipartite.*` 返回**两端** → 必 filter `bank_nodes` (L298 式)。
- 披露: 二分图 between/clustering/redundancy **丢边权** (API 约束, 非选择) → unweighted 拓扑经纪, 与加权 `brokerage_eigen_cent` 互补; 如需**加权经纪孪生**须手写加权最短路 (可选, DEFER)。

### WS-C · Gould-Fernandez 经纪角色 (5 列, 旗舰, 见 §6)
- 须先落 R12/Q1 节点分组数据流 (**复用 `iv_did.load_bank_group_maps()`**) + R2 无向 5 列 + R-Q5 唯一计数约定 + 经典"排除直连端点"。中等工作量 (自实现 + 单测 `gf_total=Σ4角色` 守恒 + 退化守卫)。

### WS-D · QAP/MRQAP 新验证阶段 (separate-artifact, golden 不动, **动 stage 计数**)
- 新 `pipeline/audit/network_qap.py::run_stage()` + thin shim `news_process/76_network_qap.py` (60-75 已占; 80/81/82 未注册) + 注册 `core/dag.py::STAGES_VALIDATION` + `core/schemas.py::EXPECTED_NO_OUTPUT_STAGES` (CSV-only → **不需** OUTPUT_REGISTRY); 写 `eval_reports/76_network_qap.csv`。
- 复用 `build_adjacency_matrix`(L110) + `compute_cognitive_proximity` 的 TF-IDF sim_matrix + geo 矩阵 (`config/city_coordinates.json` 329 城 + `geography._haversine` + bank_list province/city)。
- 若要承接 `15_table6:87`/`17_table8:154`/`paper_spec.yaml:120` 的 `_shared/A_network_robustness` 悬挂引用 (R7): WS-D 须**撰写**该宿主 .do.tmpl 或修复三处悬挂引用。
- 铁律: 置换须**联合置换行+列** (relabel 节点) 非独立打乱 cell; MRQAP 多预测须 Dekker-Krackhardt-Snijders 2007 double-semi-partialling; per-year n 须按两矩阵交集对齐; `np.random.default_rng(seed=42)`; **T=2 仅 2 张年度网 (实际有效近 1 张 2018 截面), 逐年报告勿跨年池化 dyad 当独立**。
- **R5 计数影响 (THREE 测试锁 + 源串 + CLAUDE.md)**: 新增 1 验证阶段 `STAGES_VALIDATION 16→17` 须改:
  1. `tests/integration/test_dag_consistency.py:122` (==16)
  2. `tests/test_71_inter_track_kappa.py:119` (==16)
  3. `tests/test_70_prompt_sensitivity.py:138` (逐字断言 "16 个验证阶段说明" `in rpv_code`)
  4. 源串 `run_pipeline_validation.py:123` `logger.info("  📖 16 个验证阶段说明 ...")` 16→17 (其 docstring stage-list/计数亦须手改)
  5. `CLAUDE.md`: thin shim `35→37` (L18 + L109 "35 thin shim scripts") + 注册 `32→34` (OUTPUT_REGISTRY 不变 16) + Current-version 行。
  (WS-E 同时上 → 16→18, 同步。)

### WS-E · Null-model z-score 阶段 (separate-artifact, adopt-with-care)
- 新 `pipeline/audit/network_null_models.py` + shim `77_*`; ER (`gnm_random_graph` n/m 匹配) + **配置模型** (degree-preserving, 比裸 ER 诚实, 因共现图重尾度分布) + BA/WS 作形状基准; z=(obs−mean)/std over ~1000 图/年, seed=42。
- 铁律: **unweighted-vs-unweighted** (观测须二值化); 逐年报告。计数同 WS-D (THREE 锁 + 源串 + CLAUDE.md)。

### Wave-3 · 论文接线 (brokerage 篇)
- 用 GF (`gf_gatekeeper_rep` 等) + `brok_bip_between_cent` 作经纪**正测度** (`brokerage_eigen_cent` 降为声望对照); paper_spec / Stata 模板接线。
- **R6 FWER**: 新增 16 探索性网络列与既有 22-battery 同属 garden-of-forking-paths → 须**扩 `paper_spec families.centrality_battery` + `20_table11 local battery`** 纳入新列, 或声明独立预注册 family (wyoung/rwolf2/sharpened-FDR Anderson 2008)。
- **R-M3-claims (track-agnostic 红线, 轻量)**: 新网络工具 (GF/二分图/QAP) 均 track-agnostic; 接 `17_table8` over-id IV 时**勿**与 `_full/_ctx/_ss` tone 工具混入同一 over-id Hansen J (重申既有三轨红线)。

---

## 8. Tier-2 延后项 (付费/T=19/重依赖)
- `bank_community_id` + 参与度/within-module-z (Louvain+Guimera-Amaral): 名义类别 FE-only, 须 seed+canonical-id, T=2 退化, 与 GF 重叠 → 待 T=19。
- Bonacich power (`bank_power_cent`): 可选, **Bonacich 1987** (AJS 92:1170-1182) β<0 议价语义, **nx 无原生 API 须自实现** (Katz 族 β<0), blas-fp。
- `brokshare_*` 投影 battery: 若做只上确定性核, eigen/CFB 排除 golden。
- node2vec → 改无依赖确定性 SVD/spectral 嵌入 (networkx+scipy+sklearn 已装)。
- ERGM/TERGM: 待 T≥4 + 装 statnet + 建 R-bridge; homophily 问题 WS-D QAP 已更便宜回答。
- LLM/KG 三元组: 多周新上游阶段, 受 M0 付费 gate + golden schema 3→4。

---

## 9. 风险与红线
1. **golden 重生强制**: WS-A/B/C/(Bonacich/`_hn`) 任一新面板列 → `test_column_hashes_match_golden` (列集严格相等) 立 fail 直到重生 40+51; **无外科 re-key 捷径** (新列无已祝福哈希)。
2. **确定性 env 不完整即漂移**: 仅 PYTHONHASHSEED=0 不够, 须同钉 MKL/OPENBLAS/NUMEXPR/OMP=1。WS-A/B/C 核心 16 列本身多确定性 (greedy/计数/二分图组合) → **不扩大 BLAS-FP 排除集**; 既有 4 列仍须 env 钉死才 0 漂移。⚠ **Q3**: 若启用**可选 Bonacich** (`bank_power_cent`, blas-fp) 或 `net_modularity_hn_yr`(谱无关但走加权 greedy, 确定性) → Bonacich **须扩 BLAS-FP 排除集**。
3. **加性铁律**: 新代码只**读已建图**, 不重排节点序 / 不重建 `G/G_inv/G_lcc/components` (否则移既有 BLAS 敏感列哈希)。
4. **二分图守卫非可选**: `node_redundancy` degree≥2 预过滤 (否则崩); `closeness` 自建 bipartite-LCC 限制 (否则跨分量不可比, 实测排名倒挂)。
5. **clique 膨胀 (R3/R4)**: transitivity/modularity 被多行文章 clique 投影虚增 → codebook 披露 + 可选 `hyperedge_normalize` 孪生; GF 须经典实现 (排除直连端点) 才 clique-鲁棒。
6. **共线性 (R6 + Q6)**: VIF/pairwise-corr 筛须覆盖**三族**: (a) 5 二分图中心度互相 + 与 `brokerage_eigen_cent`/`bank_between_cent`; (b) `gf_total = Σ4角色` **完全共线** (回归**勿** total+角色同入); (c) **net 级族 (Q6/round-1 D5-10)** `net_n_components_yr`/`net_giant_share_yr`/`net_density_yr` 近机械共线 (giant_share 与 n_components 同测分裂)。golden 重生**前**跑 (|corr|>0.9 取代表), 与 plan 否决 PageRank 同一标准。
7. **stage 计数锁 (R5)**: WS-D/E 动 `STAGES_VALIDATION` → 改 **THREE** 测试 (dag_consistency:122 / inter_track_kappa:119 / prompt_sensitivity:138) + 源串 run_pipeline_validation.py:123 + CLAUDE.md (shim 35→37, 注册 32→34)。面板列波次 (A/B/C) **不**动 stage 计数。
8. **T=2 vs T=19 (R15)**: T=2 golden **只验 plumbing 不验 VALUES**; GF 角色/QAP 在 T=2 退化, 仅验管道。论文勿在 T=2 声称结构/因果; T=19 须手核 ≥5 行 GF 角色 2-path 计数。
9. **列名 ≤32 字符**: `brok_bip_node_redundancy`(24)/`net_n_components_yr`(19)/`gf_gatekeeper_rep`(17)/`net_modularity_hn_yr`(20) 均合规。
10. **并行会话勿碰**: 当前工作树有并行脏文件, by-name add, 勿 `git add -A`。
11. **依赖声明 (R14)**: GF/二分图 load-bearing 后, networkx 须从 `HAS_NETWORKX` 优雅跳过升级为 `pyproject.toml`/`requirements` 显式声明 (否则 clean install 静默丢 golden 列)。
12. **诚实驳回**: PageRank/幂律 γ = REJECT; σ/ω, Louvain-roles, 投影 battery, ERGM, node2vec, LLM-KG = DEFER。

---

## 10. 顺序与依赖 (wave 图)
```
WS-0 前置门 (clean worktree + 备份 + canonical env)   ← 必先
        │
        ├─ Wave 1 (golden-safe 面板列, 可并行, 1 次重生覆盖)
        │     WS-A (G 网络级 6 列) ─┐
        │     WS-B (二分图 5 列)   ─┼─→ VIF 筛 → 单次受控 golden 重生 (40→46→51, canonical env, 跑两次验 0 漂移)
        │     WS-C (GF 5 列)       ─┘     └→ 用户批准后提交 golden_panel_v0.json
        │
        ├─ Wave 2 (新验证阶段, golden 不动, 动 stage 计数)
        │     WS-D (QAP) ─→ 改 3 测试锁 + run_pipeline_validation.py:123 源串 + CLAUDE.md(shim35→37/注册32→34)
        │     WS-E (null-model)
        │
        └─ Wave 3 (论文接线: brokerage 用 GF/bipartite-between 作经纪正测度; FWER family 扩; Stata/paper_spec)
              [Tier-2 延后项无 wave, 待 T=19]
最终: 全门绿 (§11)
```

---

## 11. 验收门 (全绿 = 完成)
1. `ruff check .` clean。
2. `pytest tests/integration/test_panel_reproducibility.py` 绿 (golden 重生后列集匹配 + 哈希一致)。
3. `pytest tests/integration/test_dag_consistency.py` + `test_71_inter_track_kappa.py` + `test_70_prompt_sensitivity.py` 绿 (面板列波次: 计数不变; WS-D/E: THREE 锁 + run_pipeline_validation.py:123 源串已同步)。
4. WS-A/B/C 列在 `46_panel_yearly_full.dta` / `51_panel_with_controls.dta` 落盘 + codebook 有非"未知/其他"行 (扩 `_infer_source_stage`/`_infer_category` 识别 `net_*_yr`/`gf_*`/`brok_bip_*`, 或显式 metadata)。
5. 二分图守卫单测: `node_redundancy` 对 degree<2 不崩 (返 NaN); `closeness` 自建 bipartite-LCC 限制生效。
6. GF: `gf_total = Σ 4 可区分角色` 守恒断言; gatekeeper≡representative 合并单列单测; 经典"排除直连端点"单测 (K4 → GF 中介=0); 单成员群退化约定单测。
7. WS-D/E: seed=42 复现 (跑两次 CSV 字节同); QAP 联合置换 (非独立 cell shuffle) 单测。
8. 重生确定性: 40→46→51 跑两次列哈希 0 漂移 (canonical env), 用户批准 golden diff。
9. **VIF/FWER (R6+Q6)**: 新 16 列 VIF/pairwise-corr 三族筛通过 (二分图族 + `gf_total`/角色 + net 级 density/giant_share/n_components 族; 代表列入回归, `gf_total` 与角色不同入); `paper_spec families` + `20_table11 local battery` 已扩纳新探索列 (或独立预注册 family)。
9b. **Q1 GF loader 复用门**: GF 分组**复用** `iv_did.load_bank_group_maps()` (非新 loader); 单测验 node-attr 名键匹配率 + 与既有 `bank_type` 列一致。
10. **引文四要素核验 (Crossref/WebSearch, R8/R16)**: 落 manuscript 前验全名全венue — Gould-Fernandez 1989 (Sociological Methodology 19:89-126 "Structures of Mediation") / Robins & Alexander 2004 (Comput Math Organ Theory 10(1):69-94) / **Dekker, Krackhardt & Snijders 2007 (Psychometrika 72(4):563-581)** / **Bonacich 1987 (AJS 92:1170-1182, power) ≠ Bonacich 1972 (J Math Sociol, eigenvector=`bank_eigen_cent`)** / Watts-Strogatz 1998 (Nature 393:440-442) / Newman 2001 (PRE, hyperedge 归一) / **Clauset-Newman-Moore 2004 (greedy modularity)** / **Han, Kim & Nanda 2024 (RFS 37(9):2903-2935)** / Freeman 1979 / Borgatti-Everett 1997。

---

## 12. 铁律 checklist (提交前逐项)
- [ ] WS-0 前置门满足 (clean worktree + 备份 + canonical env 全 export)。
- [ ] thin shim 仍 ≤30 行纯转发; WS-D/E 新 shim 同规。
- [ ] 面板列波次: DAG/OUTPUT_REGISTRY 计数**不变**; WS-D/E: STAGES_VALIDATION + **THREE 测试 (dag_consistency:122 / inter_track_kappa:119 / prompt_sensitivity:138)** + `run_pipeline_validation.py:123` 源串 + CLAUDE.md (shim 35→37 [L18+L109] / 注册 32→34) 同步。
- [ ] 新代码只读已建图, 未重排节点/重建 G 系对象 (加性铁律)。
- [ ] 二分图 degree≥2 预过滤 + 自建 bipartite-LCC 守卫已落; GF 经典"排除直连端点" + 无向 gk≡rep 合并已落。
- [ ] `net_modularity_yr` 两处 `weight='weight'` 一致; `net_assortativity_yr` 度方差=0→NaN 守卫; `net_diameter_yr` fresh unweighted `eccentricity(G_lcc)`。
- [ ] GF 节点分组数据流落地 (**复用** `iv_did.load_bank_group_maps()`, 勿重造; → node-attr attach; 单测 loader 复用 + 名键匹配率)。
- [ ] VIF/pairwise-corr 筛通过 (覆盖二分图族 + `gf_total`/角色 + net 级 density/giant_share/n_components 族); FWER family 已扩。
- [ ] codebook `_infer_source_stage`/`_infer_category` 已加 `net_*_yr`/`gf_*`/`brok_bip_*` token (注: 既有 4 个 net_*_yr 今亦落 UNKNOWN/OTHER, 一并修); export.py STATA_LABELS 已加**全 16 列** (非仅 MVP 4 列); `run_pipeline_validation.py:124-140` 逐阶段说明块加 `+76/+77` 行。
- [ ] networkx 已在 `pyproject.toml`/`requirements` 显式声明 (load-bearing)。
- [ ] golden 在 canonical env 重生且跑两次 0 漂移; 用户批准后**仅** commit `golden_panel_v0.json`。
- [ ] 列名 ≤32 字符; 新列 track-agnostic (不产 _ss); 17_table8 不混三轨 Hansen J。
- [ ] memory + MEMORY.md 索引 + CLAUDE.md Current-version 行更新。
- [ ] by-name `git add` 本任务文件, 排除并行脏文件。

---

## 13. 生产 T=19 待办 (本机 T=2 不可替代)
- 全量重跑 (stage 25 SBERT 4-6h → 26 staleness → … → 40/46/51) 后 GF/QAP/null 才有功效 (T=2 单 2018 截面退化)。
- golden 受控重生 (canonical env; 既有 4 BLAS-FP 列须 env 钉死)。
- **GF 角色语义 T=19 手核 (R15)**: 抽 ≥5 行, 手算 2-path 角色计数核对代码输出 (T=2 golden 只验 plumbing 不验 VALUES)。
- GF 分组稳健性 (nfra_type 短码 [`load_bank_group_maps`] vs province) + QAP geo 覆盖体检 (city ∈ 329 城)。
- `net_modularity_hn_yr` (加权 clique-鲁棒孪生) 接 config+runner 后重生 (transitivity 无 `_hn`, 见 Q2; 其 clique 修复走文章规模上限/披露)。
- 启用 Tier-2 延后项前重估 (Louvain-roles/Bonacich/投影 battery/node2vec-SVD/ERGM)。

---

## 14. 附录: MVP 垂直切片 (最小风险闭环)
最小可落地路径 (单次 golden 重生, 0 新依赖, 0 stage 计数变更):
1. WS-A 仅加 `net_transitivity_yr` + `net_giant_share_yr` + `net_n_components_yr` (3 列, 全 trivial/确定性, 复用 L572-573 已算对象; transitivity 一行 fresh `nx.transitivity(G)`)。
2. WS-B 仅加 `brok_bip_between_cent` (1 列, 旗舰真经纪测度, 确定性, filter bank_nodes)。
3. 扩 codebook `_infer` 识别 `net_*_yr`/`brok_bip_*` + 加 4 列 export.py STATA_LABELS (key 唯一, ≤80 latin-1)。
4. clean worktree + canonical env → **40→46→51** 跑两次验 0 漂移 → `generate_golden_snapshot.py` → 用户批准 → commit golden。落盘核验读 `46_panel_yearly_full.dta` + `51_panel_with_controls.dta`。
5. 绿门 §11(1-4,8)。

→ 4 列闭环验证"加网络列 + 受控重生"全链路通后, 再批量推 WS-A 剩余 + WS-C(GF, 含分组数据流) + WS-D(QAP, 含 3 计数锁)。

---

*生成: 2026-06-21 | v1 = 9-agent 可行性 + 3-agent 验证 (transcript `wf_47c7c059-02b`) | v2 = 顶刊级 52-agent 评审 (8 维 find → refute-first verify → 3 视角完整性批判 → 验证遗漏; transcript `wf_3ab61202-16f`) 确认 21 条缺陷外科修订 (0 P0 / 8 P1 / 余 P2-NIT) | 盘面验证 networkx 3.4.2 / numpy MKL / `F:/Anaconda3/python.exe`*
