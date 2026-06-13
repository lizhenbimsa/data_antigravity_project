# 网络位置指标多角色化 — 实施蓝图 (2026-06-13)

> 用户 directive: (1) "网络位置影响同业语调溢出的论文" (= **brokerage_network** 旗舰篇) 不止用一阶 W·tone / 二阶 W²·tone, 还要纳入**其他网络位置(网络结构)指标**; (2) 全项目要**突出网络指标**, 用作解释/中介/工具/调节/异质性等多种角色。
>
> 本蓝图由一个 4 阶段、41-agent 设计工作流产出 (Map 网络指标清单 91 个 → Design 3 路 33 spec → Verify 逐 spec 对抗审计识别有效性 → 主控综合)。工作流的最终综合 agent 因 session limit 失败, 本文件由主控从缓存的设计+裁决直接综合而成。
> 权威设计/裁决原文: 同会话工作流 transcript (`wf_7cc97a3e-e81`)。

---

## 0. 大白话总览 (先讲是什么/为什么/影响)

**是什么**: 这套项目其实早就把"网络位置"算得很全了——共现网络里每家银行有 **22 个中心度** (它认识多少同行、是不是桥梁、邻居重不重要、有没有占住"结构洞"、抱团程度…), 外加媒体-银行二分图的经纪中心度、行业负面冲击、火灾甩卖交乘等。**但 22 个里只有 3 个真正进了回归, 而且只当"控制变量"**, 另外 19 个是"算了存盘但从没用过"的休眠列。主线分析也只用了"同行语调"这一条溢出链 (一阶 W·tone 当处理, 二阶 W²·tone 当工具)。

**为什么要做**: 网络位置是这套论文**最大的、最便宜的、却没变现的资产**——这些列**已经躺在面板 .dta 里了**, 把它们提升成解释/中介/调节/异质性变量, 绝大多数是**纯 Stata 模板 + spec 声明, 不花一分钱、不动任何面板数值 (golden-safe)**。同日的顶刊审计也独立指出同一个问题 (P2-12: "22 选 3"有 p-hacking 嫌疑, 建议声明 primary_centrality + 多重检验校正)。

**影响 (每篇论文意味着什么)**:
- **旗舰 brokerage**: 从"只有 tone 溢出一条线"扩成"网络位置当解释/中介/工具/调节/异质性五种角色都登场", 真正配得上"brokerage (经纪网络)"这个标题。
- **其余 10 篇**: 网络位置最稳妥的角色是**控制变量** (净化"被报道得多/被听到得响"这种媒体可见度混淆), 部分篇可升到**调节/异质性** (网络枢纽地位放大处理效应)。

**一句话现实**: 这些表绝大多数**要等全量数据 (T=18, 2007–2024) 才跑得出**——当前盘面是 T=2 (176 行) 试跑样本, 银行+年份固定效应几乎把网络位置的组内变异吸光, 交乘/分样本/IV 全退化。所以本轮做的是**"把架子搭好、把识别隐患的护栏钉死"**, 数据到位即可激活。

---

## 1. 现状盘点 (Phase 1 实测)

| 族 | 列 (panel 实存) | 当前角色 | 状态 |
|---|---|---|---|
| 共现中心度 22 | `bank_degree_cent` `bank_strength_cent` `bank_between_cent` `bank_harmonic_cent` `bank_eigen_cent` `bank_katz_cent` `bank_subgraph_cent` `bank_cfbetween_cent` `bank_clustering` `bank_constraint` `bank_is_hub` `bank_ego_density` `bank_ci` `bank_effective_size` `bank_closeness_cent` `bank_eccentricity` `bank_avg_nbr_deg` `bank_coreness` + 网络级 `net_density_yr` `net_avg_cluster_yr` `net_avg_path_yr` `net_degree_gini_yr` | **仅 3 进回归** (between/constraint/brokerage_eigen 作 control); 19 休眠 | 已落 40/51 .dta → Stata 消费 **$0** |
| 溢出 | `peer_tone_lag1_{full,ctx}` (1阶) · `peer_tone_2nd_lag1_{full,ctx}` (2阶) · `peer_fintech_exposure_lag1` | brokerage 主线: 1阶=treatment, 2阶=IV | 已落盘 |
| 二分图经纪 | `brokerage_eigen_cent` · `industry_neg_shock(_lag1)` · `brokerage_fire_sale` | brokerage_eigen=control; 后两者**零回归消费** (最纯孤儿) | 已落盘 |
| 认知/嵌入 | `bank_cogn_mean` · `emb_peer_tone_lag1_*(_t2v)` · `bank_emb_sim_mean_lag1` | 描述/控制 | 已落盘 |
| 网络 IV | `leave_one_out_peer_*_iv` · `bartik_*_iv_*` · `prov_leave1out_tone_*` · `llm_peer_tone_iv_*` | 各篇 IV | 已落盘 |

**6 大网络位置族已被既有列充分覆盖** (hub/声望-prestige/桥接-bridging/结构洞-structural-hole/可达-reach/嵌入-embeddedness + 网络级 + 溢出IV); 真正缺口仅 2 个 (见 §4)。

---

## 2. 旗舰 brokerage_network — 五角色化 (核心)

**primary_centrality 裁决 = `bank_between_cent`** (Freeman 1979 介数/桥接 = 唯一直接量化"跨群信息中介(经纪)"的中心度, 与 W·tone 溢出传导机制同构)。
⚠ 审稿裁决更正: 设计的 BRK-PRIMARY-1 曾选 `bank_constraint`, 被否——constraint 只是外生控制、不是溢出引擎; 且**真正的"主识别量"是 W·tone(endogenous)/W²·tone(IV) 谱滞后, 中心度族是"网络位置度量"**。故声明应区分两层: 溢出引擎(主线) vs 网络位置度量(between=primary, eigen=secondary, constraint=结构洞稳健, 余 19 = 附录稳健集)。

| 角色 | 表 | 关键变量 | 估计量 | 裁决 | 必做的护栏 |
|---|---|---|---|---|---|
| **横切** BRK-XSEC-0 | spec 字段 | `primary_centrality=bank_between_cent` + `centrality_battery`(22) + `roles` 块 + `fwer:romano_wolf` | — (spec 层) | ✅ needs_caveat(minor) | schema 设 optional 防 11 篇 lockstep |
| **解释** BRK-EXPL-1 | 15_table6 | `L.bank_between_cent`→outcome | reghdfe | ❌ **reject(fatal as causal)** → 降级**描述性条件关联** | 删因果声明; **删 L2-IV 列**(无效工具); 改"conditional association"; 缺失约定统一 |
| **中介** BRK-MED-2 | 16_table7 | `peer_tone_lag1`→`bank_between_cent`→outcome | 三段回归 | ❌ reject(major) → **附录探索性** | 中介内生→Imai ρ 敏感性; "关联分解非因果中介"; 以调节表为主 |
| **工具** BRK-IV-3 | 17_table8 | `peer_tone_lag1`=(`peer_tone_2nd_lag1` + `prov_leave1out_tone`) | ivreghdfe over-id | ✅ needs_caveat(major) | **跨族**(共现 W² + 地理同省 LOO), **严禁** full+ctx 双支拼 J; Hansen J+KP F+AR CI |
| **调节** BRK-MOD-4 | 18_table9 | `peer_tone × L.中心度` 交乘 | **2SLS 交乘**(交乘项工具化) | ✅ needs_caveat(major) | **禁 OLS**(主表都走 2SLS); 交乘+主项各配工具; N-02 报 N; FWER |
| **异质性** BRK-HET-5 | 19_table10 | 按 `bank_is_hub`/`bank_constraint` 分位 | **pooled 交乘 2SLS** | ✅ needs_caveat(major) | within-year 分位(非绝对阈值 N-08); 组间差用交乘 t 非并排; N<30 守卫; AR CI |
| **FWER** (BRK-PRIMARY-1 的 B 部分) | 20_table11 | 22 battery 多重检验 | wyoung/rwolf2 | ⚠ 语法重写 | **rwolf 无 iv()/不支持 ivreghdfe** → 用 wyoung 或 rwolf2; T=18 才激活, 盘面 runtime-guard 优雅降级 (capture which/confirm + DV 哨兵 exit, 非注释掉) |
| **机制(调节变体)** BRK-FIRESALE-1 | 15_table6b 或并入 | `brokerage_fire_sale` + `industry_neg_shock_lag1` | reghdfe | ✅ needs_caveat(major) | 激活休眠孤儿; **只用 _lag1**(同期版年FE下与自身负面率精确共线) |

**接线点** (全部 golden-safe, 但触碰共享文件):
1. 新模板 `papers/_common/stata_templates/brokerage_network/15_…20_….do.tmpl` (复用统一头部 `version 19`/`clear all`/`set maxvar 32767`/`set linesize 120` + `use "$data_dir/_prepared_panel.dta"`)。
2. `00_master.do.tmpl`: 在 `do 30_figure1` 前依次插入新表。
3. `derivative_replication.py::_PAPER_DEFAULTS['brokerage_network']` 新增占位符: `PRIMARY_CENT='bank_between_cent'` `SECONDARY_CENT='brokerage_eigen_cent'` `MEDIATOR_CENT='bank_between_cent'` `OVERID_IV2='prov_leave1out_tone_full'` `MOD_CENT='brokerage_eigen_cent'` `NET_HET_VAR='bank_is_hub'`。
4. `tests/test_papers_b_route.py:146` 模板计数 (口径 = `STATA_TEMPLATES_DIR.rglob('*.do.tmpl')` 含子目录排除 provisional) + ≥6 处 CLAUDE.md "100" + replication 包 brokerage 子目录 .do 计数, 须 lockstep。
5. `paper_spec.yaml` 加 `network_roles` 块 + `identification.primary_centrality`/`secondary_centrality`/`centrality_battery` + `robustness.fwer`。schema (`paper_spec_schema.py`) 对未知顶层键 no-op → 纯增字段零破坏 (建议 optional 防 lockstep)。
6. esttab 动态名单 lockstep (14_table5 已有范本 `estimates dir`→`r(names)` 过滤): 凡有 capture-confirm 守卫的列必走动态名单, 否则 r(111) 整表丢失。

---

## 3. 全项目 11 篇 — 网络角色铺开 (逐篇, golden-safe 优先)

| 篇 | 身份 | 网络角色 | 列 | spec id | 裁决 | golden |
|---|---|---|---|---|---|---|
| P1 tone | firm-level 语调 | **控制**(可见度混淆) | `bank_between_cent`+`bank_degree_cent` | P1-CTRL-1 | needs_caveat(minor); ⚠**坏控制风险**(可见度可能是 tone 中介→放附表对照, 非默认进 $controls) | ✅ |
| P1 | | 异质性(次) | `bank_is_hub`(within-year 分位) | P1-HET-1 | needs_caveat(major) | ✅ |
| P2 attention | firm-level 曝光 | **控制(最关键)**: 曝光≈共现度机械同源 | `bank_degree_cent`+`net_density_yr`(strength 仅副控, 跨年不可比) | P2-CTRL-1 | (未核验, 控制角色低风险) | ✅ |
| P2 | | 工具 | ~~新建共现 peer-LOO IV~~ | P2-PEERIV-1 | ❌ **reject** → 改用既有 `leave_one_out_peer_attention_iv × bartik_attention_iv` 跨族 over-id | (改后✅) |
| P3 substance | W&Z 实质/象征 | 调节: 高曝光行象征宣告更易被识破 | `sub_frac × bank_between_cent` (Stata gen) | P3-MOD-1 | needs_caveat(major) | ✅ |
| P3 | | 控制 | `bank_degree_cent` | P3-CTRL-1 | needs_caveat(major) | ✅ |
| P4 locus | 底层/应用技术 | 中介: tech→between→专利 | `bank_between_cent` | P4-MED-1 | ❌ reject → 附录探索 | ✅ |
| P4 | | 异质性 | `bank_is_hub`(within-year) | P4-HET-1 | (未核验, 同 BRK-HET caveat) | ✅ |
| P5 collab | 自主/外部协同 | 中介: collab→经纪枢纽→M&A | `brokerage_eigen_cent` | P5-MED-1 | (未核验, 同 P4-MED reject风险→附录) | ✅ |
| P5 | | 调节 | `collab_frac × bank_between_cent` | P5-MOD-1 | (未核验, 同 P3-MOD caveat) | ✅ |
| llm_peer | LLM 语义同业 IV | **控制(方法学卖点)**: 共现网作"传统网络位置 baseline"证语义网增量 | `bank_between_cent`+`brokerage_eigen_cent` | LLMPEER-CTRL-1 | needs_caveat(major); N-02 缺失约定先统一 | ✅ |
| llm_peer | | 调节 | `llm_peer_tone_iv × llm_peer_count` 交乘 | LLMPEER-MOD-1 | ❌ **reject(fatal)** → 交乘工具化过复杂, T=18 才稳 | ✅ |
| strategic_diff | 文本表征差异 | 控制: constraint=嵌入度 区分"文本差异"vs"网络孤立" | `bank_constraint` | STRATDIFF-CTRL-1 | needs_caveat(major) | ✅ |
| strategic_diff | | 调节 | `strat_diff_n5 × bank_between_cent` | STRATDIFF-MOD-1 | ❌ reject(major) → 交乘内生, 附录条件关联 | ✅ |
| benefit_society | 利社会态度 | **控制**(PAP 锁 outcome/treatment, 网络只能进 controls) | `bank_between_cent`+`bank_degree_cent` | BENEFIT-CTRL-1 | needs_caveat(minor) | ✅ |
| bank_media_disagreement (prov) | 跨媒体分歧 | 控制: 分歧度随 outlet 数机械膨胀, 控网络曝光位置防伪信号 | `bank_degree_cent`+`brokerage_eigen_cent` | DISAGREE-CTRL-1 | needs_caveat(minor) | ✅ |
| bank_news_clarity (prov) | 报道清晰度 | 控制: 清晰度部分由"哪些媒体报道你"驱动 | `bank_degree_cent`+`brokerage_eigen_cent` | CLARITY-CTRL-1 | (未核验, 控制角色低风险) | ✅ |

**跨论文共享基础设施** (NET-SHARED, 解 P1-3 红线 + N-02):
- **NET-SHARED-1** (✅ defensible): 每篇 `paper_spec.yaml` 加 `network_roles` 块约定 + `derivative_replication` 加 `NET_CTRL_COLS` 占位符; 统一 **0-vs-NaN 缺失约定** (N-02: `bank_*_cent` 不在网兜底 0.0 vs `brokerage_eigen_cent` 兜底 NaN, 同入一回归致 listwise 样本漂移)。
- **NET-SHARED-2** (✅ needs_caveat): 共享 `_shared/A_network_robustness.do.tmpl`: (a) 加/不加网络控制系数稳定性对比, (b) VIF 共线诊断, (c) **QAP/dyadic 共现网 vs 同省外部效度** (解 P1-3 最危 desk-reject 命门, geography.py 已有 prov/city)。

---

## 4. 值得新增的 Python 列 (Tier-2, 付费 golden 重生, deferred)

| 候选 | 角色 | 增量价值 | 裁决 |
|---|---|---|---|
| **NET-NEW-GF-BROKER** `gf_coordinator/gatekeeper/representative/liaison/total` | 解释 | **顶刊几乎必需**: 论文标题=brokerage 但现仅 `brokerage_eigen_cent` 单一特征向量(测 prestige 不是 brokerage); Gould-Fernandez 1989 才是文献意义的**经纪角色分解** | ✅ needs_caveat — 须自实现(networkx 不直接支持)+ FWER; Crossref 核验 GF 1989(不在 140 文献清单) |
| NET-NEW-BONACICH-POWER `bank_bonacich_pos/neg` | 解释 | 锦上添花: β<0 = 议价权语义(连弱邻居者更有权), 补 eigen/katz 的 prestige | ⚠ 未核验; 按连通分量算+确定性 nstart 防漂移 |
| NET-NEW-DELTA-CENT `d_between_cent` 等 | 解释 | **Stata 内 `gen d_x=x-L.x` 可平替** → 不必新列 | ❌ reject(可 Stata 平替) |
| NET-NEW-COMMUNITY-MOD `bank_community_id` 等 | 控制/聚类层 | 优先级最低; coreness/clustering 已覆盖嵌入维度; Louvain 随机性须固定种子 | ⚠ 未核验; 仅 referee 要 community-robust SE 时补 |
| NET-NEW-COVERED-ALREADY | — | **防过度工程裁决**: PageRank/HITS/load 等与既有 eigen/katz/cfbetween 高度共线(VIF 爆)=variable-farm, 不建议 | ✅ 不新增 |

**落地链** (Tier-2): `network_*.py` 加计算 → runner 7h 接线 → stage45/46 重跑 → `generate_golden_snapshot.py` 重生 → 须与并行 stage21 重跑会话协调 (付费 gate, 用户选下次全量 run)。

---

## 5. 风险与红线汇总

**被否决的 7 个 proposal (诚实记录, 勿当没提过)**:
1. **BRK-EXPL-1** (fatal): 网络位置作 ROA 因果主 RHS + L2-IV → 反向因果(绩效差→负面事件→被多媒体共提→共现度↑)、L2 工具排他必败、跨年不可比。**救法**: 降级"描述性条件关联", 删 L2-IV。
2. **BRK-MED-2 / P4-MED-1** (major): 中介内生(网络位置内生于媒体覆盖 P1-5)→ Imai sequential ignorability 不可信。**救法**: 附录探索 + ρ 敏感性 + "关联分解非因果"。
3. **P2-PEERIV-1** (major): 新建共现 peer-LOO IV = 复活已撤回的双工具 pooled-J (corr=0.998 教训)。**救法**: 用既有 `LOO × bartik` 跨族。
4. **LLMPEER-MOD-1** (fatal): 交乘工具化第一阶段双工具识别过复杂。**救法**: T=18 后谨慎。
5. **STRATDIFF-MOD-1** (major): 交乘内生。**救法**: 附录条件关联。
6. **NET-NEW-DELTA-CENT** (major): Stata 内可平替, 不必新 Python 列。

**必须诚实披露的局限** (写进每篇正文/附录):
- **P1-3 共现≈经济同行从未做外部效度** (最危 desk-reject 命门) → 投稿前 QAP/dyadic vs 同省/同监管类别; 或把构念限定为"媒体共现注意力网络"。
- **P1-6 W² 单工具恰好识别排他不可检验** → 跨族 over-id (BRK-IV-3) 或 Conley plausibly-exogenous 敏感性。
- **P1-5 observed-only 重归一致 W 支撑集内生于媒体覆盖**。
- **N-02 0-vs-NaN 缺失约定不一致** → 统一(NET-SHARED-1)。
- **N-08 `bank_is_hub` 绝对阈值跨年不可比** → within-year 分位。
- **N-11 `brokerage_eigen_cent` 分量内归一+within=换岛噪声**。
- **N-05 W² 行随机幂迭代趋平稳→工具变异坍缩**, 省级聚类 G≈31<40 → wild cluster bootstrap (boottest)。

**硬红线**:
- **T=2 vs T=18**: 盘面 176 行试跑, 交乘/分样本/IV 全退化 (实测 endog+IV 双非空仅 28 行单年, hub 子样本 N=4)。新表全部 **production T=18 才激活**, 模板须 N-守卫优雅跳过, 不据盘面下结论。
- **列名 ≤32 字符** (交乘用紧凑 `pt_x_btw`/`sub_x_btwn`/`collab_x_btwn`/`diff_x_btwn`/`lpeer_x_dens`)。
- **禁 type×year FE** (会吸收 LOO 工具变异; 统一 `absorb(bank_id year)`)。
- **`bank_eigen_cent` 残渣 bug** 已按连通分量修但 golden 未重生 → 用前须重生 (与并行 network-metrics-audit 会话协调)。
- **rwolf 无 iv()/不支持 ivreghdfe** → FWER 用 wyoung/rwolf2/sharpened-FDR (Anderson 2008 q-values), 盘面注释掉对齐 sibling 惯例。
- **并行会话**: brokerage 11/13/14 模板正被另一会话(audit P1-2 弱工具诊断)改, 同一脏工作树 → 勿动这 3 个文件; 勿 `git add -A`。

---

## 6. 推荐的最小可立即落地集 (本轮 $0/golden-safe, 主控先做)

| # | 项 | 文件 | 改动要点 | 碰撞风险 |
|---|---|---|---|---|
| 1 | 蓝图存档 | `scripts/audit/NETWORK_METRIC_ELEVATION_BLUEPRINT_2026-06-13.md` | 本文件 | 无(新文件) |
| 2 | **spec 层骨架** | `papers/brokerage_network/paper_spec.yaml` | 加 `network_roles` + `identification.primary_centrality=bank_between_cent`/`secondary_centrality`/`centrality_battery`(22) + `robustness.fwer` + caveats | 低(并行会话未动 spec) |
| 3 | 五角色 Stata 表 | `papers/_common/stata_templates/brokerage_network/15…20_*.do.tmpl` (新文件) | 解释(描述性)/中介(附录)/跨族IV/2SLS调节/异质性/FWER, 全部 baked-in 护栏 | 中(新文件无碰撞, 但 00_master/计数测试/CLAUDE.md 共享) |
| 4 | 占位符 | `derivative_replication.py::_PAPER_DEFAULTS['brokerage_network']` | +6 占位符 | 中(共享文件) |
| 5 | 全项目 spec 元数据 | 10 篇 `paper_spec.yaml` 加 `network_roles` 块 | 控制/调节/异质角色声明 | 低 |

**Tier-2 (deferred, 付费 golden 重生)**: NET-NEW-GF-BROKER 列 + 全项目调节/异质表的实际系数 (须 T=18)。

---

*蓝图生成: 2026-06-13 | 设计工作流 41 agents / 3.89M tokens + 主控综合 | 设计原文见 transcript wf_7cc97a3e-e81*
