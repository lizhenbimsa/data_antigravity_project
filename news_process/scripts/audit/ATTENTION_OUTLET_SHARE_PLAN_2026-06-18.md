# attention_outlet_share 执行 + 验证计划 (v2 + Round-2 + Round-3 收敛闭幕)

> ## ★★★ ROUND-3 收敛闭幕 (2026-06-18, 11-agent 重定向: 盲审小组 + 反方 steelman + ATT-2 实现就绪锁 + 3-skeptic 对抗验证; 全程无截断)
>
> **已收敛且稳定 (`converged=true, verdict_stable=true`)。** 第三次重定向评审 + **真·反方辩护(devil's advocate 力保留列)经 3 个 skeptic 对抗后 `reverses_verdict=false`(high)** + 独立新 AE 同判 → **三轮(134→109→本轮)经不同经验角度全部收敛于"弃 bank-mapped 列, 做 $0 三件套"。**
>
> **steelman 的新角度(前两轮没跑过, 值得记)**: 在真盘上建最佳 salvage 列, 测得 FE-残差化 `partial corr(outlet_share, attention_pct)=0.317`(看似过 M4 的 >0.9 门、像有独立信息); 但其**自我压力测试**发现这 ~90% "独立变异"是噪声 —— 限定到干净的 **≥2-outlet 子集, 相关性反**升**到 0.398**(57.5% 行单 outlet / 71% 金科格单篇)→ "独立性恰好在格子干净处消失" = 顶刊判为致命效度问题, 非优点。**列被新角度再次否决。**
>
> **★ ATT-2 实现就绪 (唯一真实/FATAL/现在可动手项; 经 skeptic 修正后)**: 根因是**一处** `df_all` 就地重赋值 —— 在 `compute_fintech_attention_index` 内 `df_unique = df_all.drop_duplicates()` (≈:600) **之前**插入 `df_all = restrict_to_verified(df_all, OUTPUT_DIR, FILENAMES, keys=['docid','target_bank'], logger=logger, label='attention.geo_numerator')`。**年级/_build_geo_index/_merge LOO 三处共享同一 `df_all` 引用 → 一次门控传播到 yr/prov/city("三处"实为一条 lineage, 非三个独立修)。** **不门控分母/n_all**(Fang-Peress 议程份额语义); fail-open 已对; $0(prompt v8 冻结/缓存复用)。⚠ skeptic 抓到原 spec 的 "589-590" 是 logger 行(off-by-one, 无害)且把"三处"误作三修 —— 已订正。**载荷意义**: `ft_attn_prov/city` 是 shipped **P1-tone** `falsification_template.do.tmpl:336/345/427` 的活体 2SLS 工具, 现含 ~26.8% 判伪 → 修它对 P1-tone 识别 load-bearing, 与被弃列正交。爆炸半径: 6 列 `ft_attn_*`/`ft_vol_*` 下移 + golden 重生(stage45/46, 排 3 个 BLAS-FP 网络列, 勿在脏树 bless)+ falsification .do 重跑(一阶段 F 预期升)。
>
> **★ 诚实"万无一失": 不可达。** 最终有效性活在**本机跑不了的 18M/T=19**, 78 天单窗盘上列的存在理由(跨年漂移)本就**不可测**, 任何 FE-残差化相关都是 1-df/bank 假象。能给的最高诚信保证 = **结构确定的"决策"(弃列, 三轮独立同判 + 每条前提一手核验), 非数值认证的"产物"。**
>
> **★ 进一步评审 = 零边际产出, 应停。** 三轮 + steelman 经不同角度全部再确认(非新发现)= 教科书式收敛。**唯一剩余的新信息源是生产 run 本身(stage 30a 4-6h→45/46→受控 golden + radius∈{0,1,2} 网格), 不是再审。** → **停审, 动手**: 先做 ATT-2(+ 测试 `test_geo_index_verified_restriction`/docstring/golden 重生) → P1-A 披露包($0; 待写 2 个 ~20-30 行派生: outlet 进出表 + wire 转载份额/(outlet,year)) → era-stability 实例化(模板就绪) → 至多 (outlet,year) 描述性诊断(无 bank-mapping)。

---

# attention_outlet_share 执行 + 验证计划 (v2 + Round-2 终审)

> ## ★★ ROUND-2 终审裁决 (2026-06-18, 109-agent; 29 claims 重验/11 refuted-or-uncertain; 31 新 findings/19 confirmed; 主裁决 agent 被会话上限截断, 由主控亲自合成 + 一处 grep 决断)
>
> **收敛性: 列设计层 = 未收敛; 战略层 = 已收敛。** Round-2 又确认 19 条多为 MAJOR 的"修复不完整", 证明 v2 的 8 修多是**方向性重标, 非完整解决** — 每轮评审都剥出新一层缺陷, 这种"挖不完"本身就是信号: **bank-mapped companion 列在与稀薄+内生的银行级入射死磕, 是错的载体。**
>
> **★ 战略结论 (各轮一致收敛, 这是真答案)**: **不要实现 bank-mapped `attention_outlet_share` 列** (过度工程化 / 净 FE 后近共线 attention_pct / 立在 median-1 内生入射上 / 每轮新出 MAJOR)。真正稳、$0、可收敛的交付是: **① P1-A 披露包 (主修); ② ATT-2 门控 (实测确为活体污染, 见下, 高优先); ③ 分时代稳定性 (模板已有)**。若仍要测度, 正确形态是 **(outlet,year) 级描述性 share-稳定性诊断 (无 bank-mapping)** — 绕开 M1/M1-2/RT1/IC-1, 不需决策矩阵。
>
> **★ 重验逮到 v2 (我自己计划) 的真错 (须改)**: (1) **M5 引文错** — Efron-Morris 1975 shrink 的是**均值**非方差; SD/方差收缩应锚 Bühlmann credibility / Smyth 2004 limma。 (2) **M5 公式/测试自相矛盾 (我引入的新缺陷)** — 非负份额+无中心化→正均值, 但 Phase-2 测试要 mean≈0 → 构造无法满足自身测试; 须对齐 (std≈1 mean-free 或中心化)。 (3) **M5 n_o 未定义** (年数 vs 文章数)。 (4) **M4 误设** — 诊断含 bank-FE 会抽掉本列该携带的跨行变异; 应仅 year-FE 残差化; 且 0.9/VIF>5 冗余 (VIF>5⟺corr>0.894) 且对"判别性"太宽 (应 |corr|<0.7)。 (5) **M1 内部矛盾 (IC-1/RT1)** — M1 强制文章量曝露加权, 但 §0/D2 锚定等权 shares-exogeneity(GPSS/BHJ/AKM)→不同 estimand, 从未调和, 且曝露加权破坏 GPSS。 (6) **M1 G1.5 门粒度错** — 用文章数而非 outlet-breadth; 应丢 <2 distinct outlet (57.5% 单 outlet 行塌成一个 z)。 (7) **M3 决策矩阵从未真写** — 只把 FATAL 重标为"要求+门", 没装进交付物。 (8) **M7 误判** — 非"冲突", 是单个 stale 惰性版本戳 (无消费者), version-aware loader 是净新代码非"调和"; 选 3→4 反造幻影 v3。 (9) **shift-share 引文不精** — BHJ 是 exogenous-SHOCKS(与 share-exogeneity 相反), AKM 仅 inference; 只 GPSS 支持 share-exogeneity。 (10) **(outlet,year) 密度依帧** — `12_fintech_news_full`(4024 行) median=7, 较小的 `12_fintech_news`(1168 行) median=4; (outlet,bank,year) median=1 跨帧稳健。
>
> **★ 逮到上轮 134-agent 评审的错 (本轮 + 主控 grep 订正)**: 本轮 M2 把 ATT-2 降级为"非活体工具/只在 labeling .do"是**错的** — 它只 grep 了 P2 attention 模板, 漏了 **P1 tone 论文 shipped `papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl:336/345/427`** 里 `ivreghdfe Y (llm_vote_tone_full = ft_attn_prov/city)` **确为活体 2SLS 工具** (含 ~26.8% LLM 判伪, 可在 78 天盘上跑)。→ **上轮 ATT-2 FATAL 成立, M2 高优先不变。**
>
> **★ 诚实"万无一失"声明**: 一个最终有效性取决于**本机无法运行的 18M 数据**的计划, **不可能在纸面认证"完美无缺"**; 两轮深审恰恰证明: 列在反复出新 MAJOR, 因构造在与数据结构死磕。诚实结论不是"已打磨至完美", 而是"反复评审已收敛于: bank-mapped companion 是错载体, 稳路是披露包+ATT-2+era-stability"。**已验证扎实 (两轮一致, 一手)**: 全部经验事实 (78 天窗/firm-level 已门控/fail-open/ATT-2 未门控码/schema 硬编码 2/FWER foreach/era 单替换/geo LOO 存在); 文献归属 (Hassan=share / BBD=per-unit SD / Fang-Peress) 正确; HRS→Hassan 切换站得住。
>
> 下文 v2 正文保留作历史 + 实现细节参考; 凡与上方 Round-2 结论冲突处, **以 Round-2 为准**。

---

# attention_outlet_share 执行 + 验证计划 v2 (经顶刊级 134-agent 评审硬化)

> **评审裁决 (2026-06-18, 134-agent / 42 findings raised / 28 confirmed / 7 missing): `MAJOR_REVISION`** — 计划可救, 非推倒重来; 但**作为"可执行计划"当前不安全**, 须先关闭 3 个 FATAL 门。companion 定位 (P2-subsidiary, 非 P1-A 主修) 是它免于 reject 的原因。
> 状态: **已审核未采纳, 且经评审须先做 M1-M8 方可实现**。关联记忆 `attention-bbd-outlet-share-reco-2026-06-18`。
> 生产规模 = 18M 条 / 2007-2025 / T≈19; ⚠ **本机磁盘实为 78 天窗口 (2017-11-13→2018-01-30 跨年, "2017/2018" 是日历假象)**, 跨年漂移**无法在盘验证** → 全部 Phase 3/4/5 数值是占位, Phase 5 golden 双重建只认证一个**全 NaN 列**。

---

## ★ 三个 FATAL 门 (实现前必关, 否则禁动代码)

- **M1 (FATAL): bank-mapping 粒度问题未解 — 这是最深缺陷。** 标准化在 `(outlet,year)` (盘 median=7, 稠), 但映射回 bank-year **需要 `(outlet,bank,year)` 入射** (盘 median=**1 篇/格, 57.8% 单篇, 金科子集 71% 单篇**)。`(outlet,year)` 的稠密论证**与映射粒度无关**。两个候选入射源**都坏**: `f12_ft`(verified-fintech 子集)→ 平均权重**treatment-endogenous**(毁识别, 禁用); all-bank-news → 一家写过零金科的 outlet 仍把其 z 拉进均值, 且审计当初翻转掉的薄格在此回流。**计划从未写明入射源**。→ 必须: 先写死入射源 + 实测其行数; 用文章量/曝露加权 (镜像 geo LOO `attention_media.py:761,767-771`) + 加 **within-(outlet,year) 置换 placebo**(在格内打乱 fintech_intensity 重建, 要求 placebo 列主回归系数不显著); 加 **G1.5 门**: 若 (outlet,bank,year) median<2 → 本列降级为纯描述性, 放弃 bank-mapping。
- **M2 (FATAL): ATT-2 升为 HARD 门 (G0-blocking), 非"并行"。** `_build_geo_index` (`attention_media.py:701-704`) + 年级 (`:606-608`) 从裸 `is_fintech_news` 算 `_ft`, 无 `restrict_to_verified`; `ft_attn_prov/city` 是 shipped falsification `.do` 里**现可在盘运行的 2SLS 工具/Hansen-J 输入**, 26.8% LLM 判伪直接进**识别用工具**。在 geo-IV 未门控时把 attention 包当 P1-A 解药呈交 = AE 收下一个含活体识别污染的包。→ 门控 geo 分子 (两处) **或** 从活 falsification `.do` 撤下 geo-IV 列, 直到门控; 这是**工具外生性修复**, 非稳健性琐事。
- **M3 (FATAL): 预登记四象限决策规则。** 两测度被设计成不同 (extensive level vs within-outlet z-deviation), 中度相关是预期, 回归"不一致"很可能且当前**无管理**。须在跑之前预登记 agree-sig / agree-insig / disagree-sign / disagree-mag 四格各自对 headline 的含义 + 提前写好"不一致"的披露语; 且把 FWER/era 接线与"一致性通过"**解耦**(不一致不得被静默发表)。否则"twin agreement"检验**不可证伪**。

---

## ★ 五个 MAJOR 必修 (M4-M8)

- **M4: 用 FE-残差化偏相关检验替换 year-FE 共线检查。** 现 with/without-year-FE 检查测的是**全局**共线, 非**净 FE 后**的关键问题。改: 回归 `attention_outlet_share ~ attention_pct + bank-FE + year-FE`, 报 **FE-残差化偏相关 / 增量 within-R² / VIF**; 预承诺阈值: 偏相关 >0.9 或 VIF>5 → **降级为纯描述性/Table-1**。报跨 outlet 的 shrunk-SD 分布; 近退化 → 宣告变换近仿射、放弃净识别声称。**设为 Phase 3 首个 gating 诊断。**
- **M5: 精确写定 EB 收缩估计量 (现未写未引 = 自由研究者 DoF)。** 写公式 + 引 **Efron-Morris (1975 JASA)**: `z=s/sqrt(w_o·SD_o²+(1−w_o)·SD_pool²)`, `w_o=n_o/(n_o+k)`, k 用矩估计 + 敏感性网格 k∈{1,3,5,10}, 预登记 k。**删除 "<N_min → 回退裸份额" 分支**(薄 outlet 必须 pooled-SD 标准化或丢弃, 绝不把裸份额混进等权均值); 报"混合 regime bank-year 占比"。
- **M6: 拆分 Phase 0 (反捆绑)。** ATT-2(改工具值 → 非 golden-safe, 触 shipped 复现资产) + DI-6(重写语料行身份 → 全管线 golden 重生 + byte-identity 审计) + companion 列(纯加列) = **三个独立 gated PR**, 各自 golden/复现 blast-radius 评估。计划自述的 "$0 / drop-column / golden-safe 回滚"**只在解耦后成立**。DI-6 验证从 "drop_duplicates(docid) ±0 行" 强化为 "多年 fixture 上**精确 drop-INDEX-SET 等价** + 跨缝行走 kept-chain 工程化 + 证明/界定 kept-chain 触及范围"(固定 90 天 lookback 可切断链, 改变保留哪一份/哪一日)。
- **M7: 调和 schema_version 命名空间并真正实现 bump。** 实测: `generate_golden_snapshot.py:131` **硬编码 schema_version:2**, golden fixture 是 2, `test_panel_reproducibility.py` 零 version 分支; 且 `_ss` 轨**已占用 2→3**(CLAUDE.md v3.9.0)→ **命名空间冲突**。→ 本列用 **3→4**(或特征位 manifest, 非单调整数); patch 生成器真发新版 + 加 version-aware loader 条件 + 加"旧版 golden 经丢弃新列 round-trip"测试。G5 显式标注"**全 NaN 列上的可复现性, 非行为验证**"。
- **M8: 预算并写明 Stata 模板手术 (成本节漏了)。** FWER 族 (`18_attention_robustness.do.tmpl:56-60`) 是**硬编码 foreach 列表 + esttab keep()/stats lockstep**(静默丢列陷阱); era 模板 (`22_*`) 用 `{{MAIN_TREAT}}` 作**paper 级单次替换** (= `attention_index_full`, `derivative_replication.py:229`)。→ "把新列当 {{MAIN_TREAT}} 变体跑"**结构上不可能**, 须: 把列加进 foreach + esttab keep/stats lockstep (加 lockstep-pin 测试); **作为独立 rwolf 族**进入(不混进现有 3 成员族, 否则 step-down 重排会改既有/已发表表的校正 p — 须新旧 FWER 表并列); era 用**独立实例化模板/二级 treatment 循环**。

---

## 0. 设计冻结 (审计已定 + 评审追加冻结注)

- **粒度 = `(outlet, year)` 标准化** (禁 `(outlet,bank,year)`)。**⚠ 评审冻结注 (DELTA-2)**: `(outlet,year)` 密度 (盘 median=7) 是**标准化粒度**; **bank-mapping 粒度是 `(outlet,bank,year)` (盘 median=1, 57.8% 单篇/金科 71%)**, 入射源须实现前写死, `f12_ft` 禁用(treatment-endogenous), all-bank-news 回流薄格; 加 within-(outlet,year) 置换 placebo (见 M1)。
- **加孪生, 不替换** `attention_index_full` (Fang-Peress 水平测度不动)。**⚠ 评审注 (S7)**: 函数 docstring (`attention_media.py:262-266`) 曾被刻意订正为 "attention_index 是 Fang-Peress extensive, **NOT Hassan**"; 在同函数加 Hassan 锚的列须加 docstring 调和 + comment-test, 防未来重构塌缩两锚。
- **锚点 (DELTA-10 拆分)**: **Hassan 2019 QJE = 仅 step-① 主题条件 SHARE**(其 PRisk 是 transcript 内份额, 用**单一共同样本 SD**, **非**逐源单位 SD, **无** EB 收缩); **BBD 2016 QJE = step-② 逐单位标准化**; **Efron-Morris 1975 JASA = EB 收缩**(现未引)。加 BHJ 2022 REStud / AKM 2019 QJE / GPSS 2020 AER(share-exogeneity, 各一句, 因等权-均值-over-outlets 是 shares-based 暴露设计)。`attention_index` 仍锚 Fang-Peress (补页码 2023-2052)。**不是 HRS** 领衔。
- **回归列不要均值-100**。

## 0b. 上线前裁决 (D1 升为 construct 决策)

| # | 裁决 | 评审后定调 |
|---|---|---|
| D1 | 分子/分母宇宙 + 门控不对称 | **construct 决策, 非 feasibility**。门控不对称本身随时代变 (分类器/词典命中率 era-dependent) → gated-num/ungated-denom 比值继承**分类器漂移**, 直接污染"跨年可比"目标。若本列意在作 `attention_pct` 的抗漂移孪生 → **匹配 attention_pct 的 ungated 分母**, 只让标准化/聚合不同; 披露**逐年** verified-keep-rate。加列专属 denominator-universe 测试 (镜像 `test_denominator_is_full_bank_news_universe`)。⚠ **隐藏第三态 (S2)**: `restrict_to_verified` 在 (docid,target_bank) 键缺失时 **FAIL-OPEN 不门控** (`verified_universe.py:86,97}` → dense fixture 须含 docid (否则 Phase-2 T3/T4 验的是 fail-open 路径而非生产); 加"分子分母同一 restrict_to_verified 调用/键集"不变量测试; D1 有三态 (both-gated / num-gated-denom-ungated / fail-open-both), fail-open 生产环境绝不可静默发生。 |
| D2 | 几轨 | single-track `_full` (控 FWER); 起草 referee-facing 单轨理由 (为何此列破 full/ctx/ss 平价惯例) |
| D3 | 给 IV? | **否** |
| D4 | 进 main spec? | **否** (subsidiary) |
| D5 | balance spine 1771? | 独立计量范围决策; ⚠ **三候选宇宙 (R5)**: 86 verified / 243 ever-mentioned / 1771 registry; 现 baseline=86, byte-match 钉在 86, 披露为何 86 而非 243 |

---

## Phase 0 — 三独立 gated PR (反捆绑, 见 M6)

> ⚠ **评审推翻原"ATT-2 非硬阻塞"**: ATT-2 是**整 attention 包的 HARD G0 门** (DELTA-1)。三者独立 PR + 各自 golden/复现 blast-radius。

- **P0.1 ATT-2 (HARD 门, 工具外生性)**: 门控 `_build_geo_index` (:701-704) + 年级 (:606-608) 分子; 新测 `test_geo_index_verified_restriction` 断言非空 geo 格按 verified 率下降。**改工具值 → 非 golden-safe, 触 shipped falsification 资产 → 须自身 golden + 复现资产 re-bless。**
- **P0.2 DI-6 dedup 分块 (18M 可行性, 重写语料身份)**: 按日期窗分块 LSH。**验证强化**: 多年 fixture 上**精确 drop-INDEX-SET 等价** + 跨缝 kept-chain 工程化 + 界定 kept-chain 触及 (固定 lookback 可切链); + `psutil` RAM>90% loud-fail。**全管线 golden 重生 + byte-identity 审计 (非仅行数)。**
- **P0.3 DI-2 balance spine (计量范围, 独立)**: 不阻塞本列。若扩 → 86→1771 + `has_coverage`; byte-match 钉现 86 spine。

**Gate G0**: 三 PR 各自 golden 影响评估 + 5 裁决文档化 + ATT-2 已关。

---

## Phase 1 — 实现 (`compute_attention_treatments` 内)

1. **(outlet,year) 主题条件份额** `s[o,y]` (分子 gated, 分母按 D1; ⚠ 分子分母**同一** restrict_to_verified 键集, 防 fail-open 不一致, S2)。⚠ numerator 现仅按 `GK=['target_bank','year']` 分组 (`:382,399-408`), outlet 仅进 HHI 支 (:424) → 须新增 `(outlet,year)` 聚合 pass。
2. **EB 收缩 SD** (M5 公式, Efron-Morris, 预登记 k + 网格; **无裸份额回退**)。
3. **bank-year 映射** (M1: 写死入射源 + 曝露加权 + 置换 placebo + G1.5 demote 门)。
4. **NaN-vs-0 契约** (⚠ S6: "share"名却走 **index-family** 0-rule(覆盖零金科→有限 0)非 disp/sd-rule; codebook 须注明; 锁 SD-floor 作回归守卫)。
5. `_validate_attention_treatments` (:231) 扩 `(None,None)` + 有限性。
6. 标签/codebook (export.py STATA_LABELS :398-405 / stata_export.py core_patterns / codebook.py _ATTN_TREAT :326-351; 27 字符 ≤32; docstring 调和 S7)。

**Gate G1 + G1.5**: ruff clean; T=2 不崩 (全 NaN 预期); **G1.5: (outlet,bank,year) median<2 → 降级纯描述性**。

---

## Phase 2 — 测试 (扩 `test_attention_treatments.py` + 稠密 fixture, **fixture 须含 docid**, S2)

9 用例 (列存在 / 无界有限 / 标准化 mean≈0 std≈1 / NaN-vs-0 index-family / universe 超集 / codebook 标签 / 收缩诊断 / min-coverage 流失 / 多轨对称) + **置换 placebo 测试 (M1)** + **分子分母同键集不变量 (S2)** + **零方差 outlet→有限 z / 单覆盖 outlet→NaN (S6)** + **FWER lockstep-pin (M8)**。

**Gate G2**: 定向绿 + 全量 sweep 零新增失败。

---

## Phase 3 — 统计有效性 (需 18M; ⚠ 78 天盘只能占位, R3)

- **3.0 (新, gating)**: **FE-残差化偏相关/VIF (M4)** — Phase 3 首诊断; >0.9 或 VIF>5 → 降级, 不进 Phase 4-6。
- 3.1 18M 重测密度 (**含 (outlet,bank,year) 映射粒度密度, M1**) → 锁 N_min/min-coverage。
- 3.2 收缩强度分布 (混合 regime 占比, M5)。
- 3.3 coverage 流失 (⚠ S5: 金科 bank-year median 覆盖=2, ≥3 门 NaN 掉**多数**金科活跃格 → 改 estimand 为"重覆盖(大行/晚期)"= coverage 选择; 改**网格** {≥1,≥2,≥3,≥5} + 优先文章量门; 披露 conditional-on-coverage estimand + 删留行 size/tier/era 画像)。
- 3.4 corr+VIF (⚠ completeness: 加近共线第 5 成员**机械抬高全族 VIF + 重排 rwolf** → 退化既有已发表推断; 用独立族 + 新旧并列, M8)。

**Gate G3**: 阈值锁 + 全文档化; **G3 fail-branch: 18M 上 min-coverage 留 >X% NaN → 降级纯描述性**。

---

## Phase 4 — 计量 (M3 决策规则先行)

- 4.1 = M4 FE-残差化 (已移 3.0)。
- 4.2 跨年可比 (⚠ M3 四象限规则 + DELTA-5: 这是**判别性抗漂移相对测度**, **非** extensive level 的**收敛**孪生; 一致至多证"构造交叉核对", **非**抗漂移 — 抗漂移证据路由到 Phase 6 + era-stability)。
- 4.3 FWER (M8: 独立 rwolf 族 + lockstep-pin + 新旧并列)。
- 4.4 era-stability (M8: 独立实例化模板, 不能复用 {{MAIN_TREAT}})。

**Gate G4**: 决策规则预登记 + 稳健性表 + FWER 校正 p。

---

## Phase 5 — golden (M7 + ⚠ 78 天盘全 NaN)

- OMP 钥匙 (`OMP_NUM_THREADS=1`+`KMP_DUPLICATE_LIB_OK=TRUE`) + 重跑链 22→24→45→46 + `generate_golden_snapshot`。
- **schema_version 3→4 (M7, 真实现 + version-aware loader + 旧版丢列 round-trip 测试)。**
- 双重重建确定性 (⚠ **G5 = 全 NaN 列上的可复现性, 非行为验证**)。

**Gate G5**: 双重建 hash 匹配 + 新旧 schema round-trip + repro 绿。

---

## Phase 6 — P1-A 主修披露包 (本列只是辅助, 真核心在此)

逐年 outlet 进出表 / 篇均长+wire 转载占比漂移 / geo footprint / 分时代稳定性 (`22_*`) / manuscript 披露语言 (样本宇宙不对称 + 收缩分布 + coverage 流失有效 N + companion 状态 + HRS→Hassan 适配三点 + **逐年 verified-keep-rate**)。
⚠ **R2 (披露铁律)**: 本列**不闭合 P1-C 零人工 criterion validity** — 与其它**未验证** attention 测度的 corr 是 "convergent-with-unvalidated", 非 criterion validity。至少加 $0 外部检查 (与已物化 front-page/lead-position prominence `encode.py:718-723` 相关) + split-half/奇偶-outlet 信度比, 界定经典衰减; 勿让 Phase-3 内部检查读作"已验证"。

---

## 残余风险 (即使全修后)

- **R1**: net-of-FE 可能仍近共线 attention_pct → twin 只证构造等价非抗漂移; 抗漂移证据**必须**来自 Phase-6 披露包 + era-stability; manuscript 须明说"本 companion 是构造交叉核对, 非主漂移防御"。
- **R2**: P1-C 零 criterion validity **继承未闭合**, 加第三未验证代理**加重**之 (见 Phase 6)。
- **R3**: 全部 Phase 3/4/5 数值是占位至 18M; 78 天盘无法练跨年漂移、无法估逐源 SD (≤2 点几周间隔)、golden 双重建认证全 NaN 列; N_min/min-coverage/k 在 18M 上可能仍不可行 → G3 fail-branch (降级) 是安全阀, 必须遵守。
- **R4**: P1-B 事件研究空壳出域但 paper_spec 仍声明 E1-E5b 对零生产者; 须说明, 免 AE 误以为本 companion 后识别套件已完整。
- **R5**: DI-2 三候选宇宙 (86/243/1771); 仅 86 vs 1771 对比不足。

## 验收 / 回滚 / 成本

- **验收**: G0-G6 + 三 FATAL 门关 + 全量 sweep 零新增 + golden 双重建确定 + 新旧 schema round-trip。
- **回滚 (每变更独立, M6)**: companion 列 "$0/drop-column/golden-safe" **仅在与 ATT-2/DI-6 解耦后成立**; ATT-2/DI-6 各有自己的 golden+复现 blast-radius。
- **成本**: companion 列 $0 LLM + 新 (outlet,year) 聚合+收缩+映射+placebo + 6 处标签/codebook + ~12 测试 + **Stata 模板手术 (M8, 原成本节漏)**; ATT-2/DI-6 各自独立成本。
- **铁律**: 禁同 RHS attention_index / 禁三轨拼 Hansen J / 冻结 prompt v8 / 纯增量不碰 shim / 不删 `_llm_cache.db`。

## 引用锚点 (DELTA-10 拆分)

Hassan et al. (2019, QJE 134(4), doi:10.1093/qje/qjz021) — **step-① 主题条件 share** (共同 SD, 非逐源单位 SD);
Baker, Bloom & Davis (2016, QJE 131(4):1593-1636, doi:10.1093/qje/qjw024) — **step-② 逐单位标准化**;
Efron & Morris (1975, JASA 70(350):311-319) — **EB 收缩** (M5);
Fang & Peress (2009, JF 64(5):2023-2052, doi:10.1111/j.1540-6261.2009.01493.x) — `attention_index` 不变锚;
Borusyak-Hull-Jaravel (2022, REStud) / Adão-Kolesár-Morales (2019, QJE) / Goldsmith-Pinkham-Sorkin-Swift (2020, AER) — shares-based 暴露 share-exogeneity;
Bai & Perron (1998) / Hansen (2001) — 分时代断点; Romano & Wolf (2005) — FWER。
Husted, Rogers & Sun (2020, JME 115:20-36) — 三步法源 (适配披露, 非项目主锚)。
