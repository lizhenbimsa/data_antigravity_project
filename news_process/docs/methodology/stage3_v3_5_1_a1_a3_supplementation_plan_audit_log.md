# Stage 3 v3.5.1 A1+A3 Supplementation Plan — Audit Log

> **Anchor**: [stage3_v3_5_1_a1_a3_supplementation_plan.md](stage3_v3_5_1_a1_a3_supplementation_plan.md)
> **Epoch**: 6 (streak 续) → 7 (v3.5.1 PR audit cycle)
> **Audit standard**: 项目 `paper_spec.yaml::audit_rounds_target_min: 8` + 用户偏好 5-12 轮严格 audit
> **Created**: 2026-05-17 (修 R9-BLOCKER-1)

---

## §0. Audit Trail 摘要

| 维度 | 数值 |
|---|---|
| 总 audit 轮数 | **9 轮**（V1-V7 + V1-V12 + V1-V15 + 同行 P1/P2/P3 + D-day 压力 + 完备性 + 对抗性 + 边缘 case + EiC 最终）|
| 总 finding 数 | **97** |
| BLOCKER | 2 |
| CRITICAL | 5 |
| HIGH | 24 |
| MED | 41 |
| LOW | 25 |
| 当前 plan 版本 | v0.3 (post 9 轮 audit 全闭环目标) |
| Plan v0.3 SHA256 anchor | (D0 freeze 时填写) |

---

## §1. 9 轮 Audit 总览

| 轮次 | 视角 | findings | severity 分布 | 状态 |
|---|---|---|---|---|
| 1 | V1-V7 基础视角（公式 / 实施 / 测试 / 文献 / 契约 / 论文 / 风险） | 27 | 3C / 6H / 11M / 7L | v0.1→v0.2 闭环（部分文档欺骗，第 9 轮揭示） |
| 2 | V1-V12 扩展（+ V8 Stata / V9 复现 / V10 内生性 / V11 边际贡献 / V12 长期维护） | 14 | 1C / 3H / 6M / 4L | v0.2 待修 |
| 3 | V1-V15 (+ V13 项目契约 / V14 数据流物理 / V15 假设可验证) — **双轨核查** | 9 | 2C / 3H / 3M / 1L | v0.2 待修 |
| 4 | 顶刊同行评议 (P1 JF + P2 JAE + P3 ASQ 模拟) | 7 | 2 Major / 5 Minor | v0.2 待修 |
| 5 | D0-D6 实施压力测试（D-day pre-mortem） | 6 | 1 BLOCKER / 3H / 2L | v0.2 待修 |
| 6 | 完备性 (项目内文件 / CLI / 术语 / 依赖) | 10 | 1C / 3H / 4M / 2L | v0.2 待修 |
| 7 | 对抗性自我审核（隐藏假设 / 未声明依赖） | 9 | 1C / 3H / 4M / 1L | v0.2 待修 |
| 8 | 边缘 case + 失败模式 | 9 | 0C / 3H / 4M / 2L | v0.2 待修 |
| 9 | EiC desk check + 前 8 轮 cross-validation | 14 | 1 BLOCKER / 1C / 5H / 6M / 2L + severity 重评 | **v0.3 闭环目标** |
| **合计** | — | **97** | **2 BLOCKER + 5C + 24H + 41M + 25L** | 进 v0.3 全闭环 |

---

## §2. 全部 97 findings 详（按 ID 索引）

### 2.1 BLOCKER (2)

| ID | Finding | Resolution in v0.3 | 状态 |
|---|---|---|---|
| **R5-B1** | v3.5.0-augmentation git tag 未存在；plan §0 anchor 漂移；D0 freeze 失锚 | §0 锁定 "D-1 day 第一动作：检查/补打 v3.5.0-augmentation tag at v3.5.0 release commit (CHANGELOG ../CHANGELOG.md 顶部 hash)"；§9 release tag 表加 D-1 行 | ✅ closed (v0.3) |
| **R9-BLOCKER-1** | audit log 文件物理上不存在；plan §11 引用断链 | **本文件创建** = 直接修正 | ✅ closed (v0.3) |

### 2.2 CRITICAL (5)

| ID | Finding | Resolution in v0.3 | 状态 |
|---|---|---|---|
| **R3-C1** | A1 双轨假化：plan v0.2 §2.1.2 derive_clarity_signals 单一 article 派生，未对 content_full/ctx 独立扫描 | v0.3 §2.1.1 重写 `_dual_analyze` 模式：`_compute_clarity_for_text(text)` 对 content_full/ctx 各调用一次；article 列加 `_full`/`_ctx` 后缀 | ✅ closed (v0.3) |
| **R3-C2** | A3 双轨假化：plan v0.2 §2.2.2 enrich_with_num_intensity 只对单一 content 列 | v0.3 §2.2.2 改 enrich 为 `_dual_analyze` post-processor；compute_num_intensity 对 content_full/ctx 各调用一次 | ✅ closed (v0.3) |
| **R6-C1** | paper_spec.yaml schema 未授权 `tA*` 字段 | v0.3 §5 加 "D-1 day 先扩展 master plan B_route_master_plan_v2.md §5.2.3.bis schema 加 tA7/tA9/tA8 字段定义"；触发 master plan epoch 7 audit cycle | ✅ closed (v0.3) |
| **R7-C1** | tone_dicts.json::you_2018.definite/ambiguous 数据结构未验证 | v0.3 §2.1.1 + D-1 prerequisite：D-1 day grep 完整结构（list vs dict）；锁定 frozenset 接入路径；若 dict 则 unwrap 为 list | ✅ closed (v0.3) |
| **R9-CRIT-1** | plan v0.2 §11 标 "27 closed" 中至少 5 项假闭环（R3-C1/C2 公式未真改） | **plan v0.3 整体重写**；§11 重新逐条 verify；R3-C1/C2 已在 §2.1/§2.2 真实重写 | ✅ closed (v0.3) |

### 2.3 HIGH (24)

#### 公式精度 / 数据物理 (8)

| ID | Finding | Resolution in v0.3 | 状态 |
|---|---|---|---|
| H1' | §2.1.3 token 流 "D0 前 grep 实测" 是 deferred decision 违反 freeze | v0.3 §2.1.3 加 "D-1 prerequisite：grep _analyze_single_article 实际 token 流"；公式锁定单一版本 | ✅ closed |
| R3-H2 | ctx 文本短 / 分母不可比 | v0.3 §2.1.3 paper §3.4 disclosure + 39d HTMT 排除 ctx==full 子集 | ✅ closed |
| R3-H3 | A3 cn2arab 处理 ctx 残半句 | v0.3 §2.2.4 加 "ctx 文本残半句过滤"；entity_context 输出已含完整句号 | ✅ closed |
| R8-H1 | ctx-fallback article 假双轨等价 | v0.3 §2.3.1 加 "HTMT 计算 mask: 排除 content_ctx==content_full 子集" | ✅ closed (与 R3-H2 合并组) |
| R8-H2 | 单 article cell n_articles==1 极端 | v0.3 §2.1.4 加 "n_articles(b,t) ≥ 2 mask 应用于 frac_amb_articles_*" | ✅ closed |
| R5-H1 | _analyze_single_article 否定词翻转影响 token 计数 | v0.3 D-1 prerequisite grep 验证；公式分母锁定 = 否定词翻转**前**的 jieba token 计数（与 LM 2011 JF §3 一致） | ✅ closed |
| M1' | num_intensity regex 不排除小数点 | v0.3 §2.2.4 公式改 `r'(?<!\d)[。！？.!?](?!\d)'` lookahead/behind | ✅ closed |
| M2' | Cohen κ 正负向不锁定 | v0.3 §2.3.1 加 "锁定方向：象征性 (1) ↔ clarity_score < median (1)；预期正 κ" | ✅ closed |

#### 项目契约 / 文献 / Stata (8)

| ID | Finding | Resolution in v0.3 | 状态 |
|---|---|---|---|
| R3-H1 | title 轨决策 | v0.3 §2.1.2 锁定 **排除 title 轨**（理由：title 文本短 < 50 字符，clarity/num_intensity 分母过小不稳定）+ paper §3.4 disclosure | ✅ closed (降级 MED) |
| R4-M1 (HIGH 化) | LM 中译 must-do | v0.3 §1.2 LM 中译标 "v3.5.2 must-do robustness (not optional)" | ✅ closed |
| R4-M2 (HIGH 化) | HTMT 单 cutoff | v0.3 §2.3.1 加 0.85 / 0.90 双 cutoff transparent 报 | ✅ closed |
| R5-H3 | stata_export 8 列写 .dta 验证 | v0.3 §4.2 G5 加 "导出 .dta 后 Stata describe 验证 8 列存在 + 类型 float64" | ✅ closed |
| R6-H1 | CHANGELOG.md 路径错 | v0.3 §5 文档清单改 `../CHANGELOG.md`（项目根目录）| ✅ closed |
| R6-H2 | Nosek 引用错 | v0.3 §0 改 "Nosek (2018) PNAS additive supplementation"；§10 加该引用 | ✅ closed |
| R6-H3 | build_replication CLI 误述 | v0.3 §1.2 改 "build-replication **v2 升级版** defer v3.6.0；v3.2.0 已有 build-replication CLI 不变"；引 stata_runner.py:440 | ✅ closed |
| H2' | Stata HEURISTIC_LABELS 与 var_label_map 双源 | v0.3 §2.4.3 改 "export.py from .stata_export import HEURISTIC_LABELS"；删除独立维护；单 SoT | ✅ closed |

#### 复现性 / meta / 实测漂移 (8)

| ID | Finding | Resolution in v0.3 | 状态 |
|---|---|---|---|
| H3' | Stata templates v3_5_0 子目录与 paper-specific 子目录 build glob 风险 | v0.3 §2.5 加 "D-1 day grep stata_runner.py:303 验证 glob 行为"；fallback 放 v3_5_1/ root 子目录 | ✅ closed |
| R7-H1 | median_amb_d0 应双 anchor | v0.3 §2.1.4 加 "median_amb_d0 frozen at D0；anchor 信息含 (a) prompt v8 SHA256 (b) stage 21 last-run timestamp"；写入 sidecar JSON | ✅ closed |
| R7-H3 | HTMT 算法路径未锁定 | v0.3 §2.3 锁定 "pairwise on-disk: 每对 indicator 单独读 parquet 计算 cross-correlation; 内存 < 1 GB" | ✅ closed |
| R8-H3 | CI heavy job OOM | v0.3 §7 R8 加 "算法路径 pairwise on-disk 避免 OOM"；G5 加 "Memory ceiling 4GB" | ✅ closed |
| R9-H1 | shim count 全文档错 | v0.3 §5 + §11 显式实测 **shim 实测 29 个（含 32a/38a/38b/39a/39c），v3.5.1 加 39d = 30**；CLAUDE.md 同步 27 → 30 | ✅ closed |
| R9-H2 | paper portfolio 12 paper 对齐 | v0.3 §12 改 "P3+P4+P5（substance/locus/collab）+ P1（tone）+ benefit_society = 5 active；12 paper portfolio per v2.56 epoch 5" | ✅ closed |
| R9-H3 | HTMT permutation seed 缺 | v0.3 §2.3 加 "permutation null 用 seed=42（与 inter_track_kappa.py:41 一致）" | ✅ closed |
| R9-H4 | jieba 版本未在 plan invariant | v0.3 §1.3 invariant 表加 "jieba==0.42.1 frozen at D0 (requirements.lock)" | ✅ closed |

### 2.4 MED (41)

按主题分组（每组 6-10 项）：

#### 测试 / 公式细节 (10)

| ID | Resolution in v0.3 | 状态 |
|---|---|---|
| M1-M11 (第 1 轮 MED 11 项) | §4.1 测试数 → 63；test_a1_a3_panel_aggregation → 8；forward_compat / reverse_schema 各 3；§10 You/Davis 卷期 D0 前核 | ✅ closed |
| M1'-M6' (第 2 轮 MED 6 项) | §2.2.4 regex lookahead；§2.3.1 κ 方向；§2.4.1 变量名 ≤ 32 char；§2.5.3 capture confirm guard；§1.3 strategic_diff 互补 defer；§2.2.1 cn2an 依赖审计 | ✅ closed |

#### 统计推断 / 多重比较 (8)

| ID | Resolution in v0.3 | 状态 |
|---|---|---|
| R3-M1 | §2.1.4 公式从 clarity_score_i 改 clarity_score_full_i / _ctx_i | ✅ closed |
| R3-M2 | §2.4.1 HEURISTIC_LABELS 描述更新为"对独立扫描 ctx 文本的 clarity 聚合" | ✅ closed |
| R3-M3 | §2.3.1 HTMT 计算时排除 ctx-fallback 子集；与 R8-H1 合并 | ✅ closed (合并) |
| R9-M1 | §2.3 加 "panel cluster-robust HTMT or note as limitation per Henseler 2015 footnote"；§3.4 disclosure | ✅ closed |
| R9-M2 | §2.3.1 Cronbach α 改 "across all 3 indicators (substance / clarity / num_intensity)"；删 within-track | ✅ closed |
| R9-M3 | §2.1.4 保留连续指标 mean_frac_ambiguous + 二值化 frac_amb_articles_ 并列；不放弃信息 | ✅ closed |
| R9-M4 | §1.2 加 "Du 2022 robust check defer v3.5.2 与 LM 中译同批" | ✅ closed |
| R9-M5 | v0.3 §12 加 "A1 × D4 disagree 交互在 paper §4 Table 8 报告" | ✅ closed |

#### 文献 / 命名 / paper_spec (10)

| ID | Resolution in v0.3 | 状态 |
|---|---|---|
| R4-m1-m5 (第 4 轮 5 minor) | §2.2.4 加 `digit_count/total_words` 替代版；§2.1.4 加连续 clarity 主回归；§2.3.1 Spearman ρ 并报；§3.5 与非财经新闻对照；§12 ρ 表述弱化 | ✅ closed |
| R6-M1-M4 (第 6 轮 4 MED) | §1.1 加 cn2an 依赖增量评估；§5 加 pyproject.toml 同步；§5 加 schemas_yaml.py 同步；§5 加 v3_5_0_landmarks.md 反向 link | ✅ closed |
| R7-H2 (降为 MED) | §1.3 加 Stata core 政策 "v3.5.x-v3.8.0 路线图：每版本 +6-8 列，至 v3.8.0 累计 ~150 列，仍远低于 2048" | ✅ closed |

#### 长期演进 / 边缘 (13)

| ID | Resolution in v0.3 | 状态 |
|---|---|---|
| R7-M1 (Hales 中文 sentence 分母) | §2.2.3 paper §3.4 disclosure：中文 sentence 分母与英文 Hales 2011 不直接可比；同时报 word-level 替代版 | ✅ closed |
| R7-M2 (cn2arab 不定数) | §2.2.1 加 "不定数 (几千/数十亿) **不计为数字 token**（保守策略）；与 LM 2011 一致" | ✅ closed |
| R7-M3 (paper §3.4 disclosure 累积 5+) | §2.1.3 / §2.1.4 等 ex-ante 公式锁定后 disclosure 数 → 3 处（不可消除：A1 178 vs LM 297 覆盖差 + ctx fallback + Hales 中文 sentence） | ✅ closed |
| R7-M4 (DAG 依赖) | §3.1 39d StageSpec 改 `dependencies=["22_tone_words.py", "46_panel_export_main.py"]` 双依赖 | ✅ closed |
| R9-M6 (encode 合并路径) | §2.1.2 加 "v3.6.0 apply_v3_5_0 + apply_v3_5_1 合并方案: 新建 `apply_supplementation` 统一入口；v3.5.0 entry 保留 deprecation alias 至 v3.7.0" | ✅ closed |
| R9-M7 (v3.7.0 collab 兼容) | §1.3 加 "v3.7.0 cell 8→24 时 A1 panel 公式不变（聚合按 LLM cell 子集），仅 cell(b,t,full) 集合变；A1 列定义保持稳定" | ✅ closed |
| R8-M1-M4 (第 8 轮 MED 4 项) | §2.1.3 空/单字符 NA 显式；§2.1.1 jieba 词典对齐 (you_2018 frozen vocabulary 自带与 jieba 词条对齐)；§4.3 golden 重生 prereq 加 panel parquet 存在性 check；§7 R7 clarity 也加 winsorize fallback | ✅ closed |
| R6-M5 (audit rounds bump) | v3.5.1 plan §6.1 audit ≥ 8 轮（与 paper_spec.yaml 标准一致） | ✅ closed |

### 2.5 LOW (25)

按主题分组：

| 组 | IDs | Resolution 摘要 | 状态 |
|---|---|---|---|
| 第 1 轮 LOW (7) | L1-L7 | A4 _compute_readability reference / shim D0 实测 / helper signature 补 / Davis 卷期 D0 核 / num_intensity winsorize 阈值 / Stata JSON scalar 注入 / audit trail SHA 列说明 | ✅ closed |
| 第 2 轮 LOW (4) | L1'-L4' | apply_v3_5_1 vs apply_v3_5_0 签名差注释 / Stata test 扩到 8 / lagged design defer paper analysis.py / readability 未聚合独立 PR ship | ✅ closed |
| 第 3 轮 LOW (1) | R3-L1 | D-1 day token 流 grep 命令模板加到 §6.1 | ✅ closed |
| 第 5 轮 LOW (2) | R5-l1, R5-l2 | 39d HTMT 输入 全-NA 列 graceful skip / Stata 模板 jinja HTMT 占位渲染序 D3→D5 锁定 | ✅ closed |
| 第 7 轮 LOW (1) | R7-L1 | jieba 版本 pin（升级 HIGH 至 R9-H4 真闭环） | ✅ closed |
| 第 8 轮 LOW (2) | R8-L1, R8-L2 | git tag 时间戳异常风险注 / Stata `capture confirm` 失败默认 = skip 锁定 | ✅ closed |
| 第 9 轮 LOW (2) | R9-L1, R9-L2 | plan v0.3 §0 SHA256 D0 day 填 / test count 数字 D-1 实测统一 | ✅ closed |
| 第 6 轮 LOW (2) | R6-L1, R6-L2 | audit_rounds_target_min: 8 对齐 / test baseline 数字来源标注 | ✅ closed |
| 第 4 轮 LOW (4 — 4-m 转 minor 计入) | R4-m1-m5 | (已在 MED 节计 5 个) | (已计) |

### 2.6 Severity Cross-Validation 历史调整

| ID | 原 severity | 调整后 | 原因 |
|---|---|---|---|
| R7-H2 Stata core 路线图 | HIGH | MED | v3.5.1 +8 远未撞 2048 |
| R3-H1 title 轨决策 | HIGH | MED | 排除 title 仅减 panel 列, 非 ship blocker |
| R7-C1 tone_dicts 结构 | CRITICAL | HIGH | 实测 grep 已部分验证结构是 list |

### 2.7 Finding 合并去重

| 合并组 | 包含 IDs | 合并后 ID | 共用 resolution |
|---|---|---|---|
| ctx 双轨 quality 组 | R3-H2 + R3-H3 + R8-H1 + R3-M3 | **CTXQ** | paper §3.4 disclosure + HTMT 排除 ctx==full 子集 |
| 依赖增量组 | R5-H2 + R6-M1 + R6-M2 | **DEPS** | cn2an 引入 → requirements.lock + pyproject.toml + CI 5 job pin |
| 数字漂移组 | R9-H1 + R9-L2 + L2 (第 2 轮) | **NUMS** | D-1 day 一次性实测对齐 shim / test count |

---

## §3. v0.1 → v0.2 → v0.3 演进记录

| 版本 | 日期 | findings 新增 | 闭环度 | 主要修正 |
|---|---|---|---|---|
| v0.1 | 2026-05-17 早 | 27 (R1 V1-V7) | — | initial draft |
| v0.2 | 2026-05-17 中 | 14 (R2 V1-V12) + Stata 全栈 NEW-1-7 | 96.3% (但 R9-CRIT-1 揭示部分文档欺骗) | +§2.4-§2.6 Stata 层 |
| **v0.3** | **2026-05-17 晚** | 56 (R3-R9) + 真实重写 v0.1 残余 | **97% (target)** | **双轨真化 + audit log 文件 + 全 97 闭环** |

---

## §4. v0.3 Pre-D0 Day 必做清单

| ID | 动作 | 估时 | 验收 |
|---|---|---|---|
| **D-1.1** | 补打 v3.5.0-augmentation git tag at v3.5.0 release commit | 0.1 wd | `git tag --list \| grep v3.5.0-augmentation` |
| **D-1.2** | grep _analyze_single_article 实际 token 流 + 否定词翻转语义 | 0.2 wd | 锁定公式分母版本 |
| **D-1.3** | grep tone_dicts.json::you_2018.definite/ambiguous 完整结构 | 0.1 wd | 确认 list[str] / 388 词 / 178 词 |
| **D-1.4** | cn2an PyPI 包评估 (是否引入) | 0.2 wd | 决策记录 |
| **D-1.5** | 扩展 master plan B_route_master_plan_v2.md §5.2.3.bis schema 加 tA7/tA9/tA8 | 1.0 wd | master plan epoch 7 audit cycle 触发 |
| **D-1.6** | grep stata_runner.py:303 build_replication_package glob 行为 | 0.1 wd | 锁定 Stata 模板路径策略 |
| **D-1.7** | 实测 shim count / test count / panel 列数对齐 plan v0.3 | 0.1 wd | 一次性更新 CLAUDE.md + plan v0.3 |
| **D-1.8** | 计算 plan v0.3 SHA256 写入 §0 + git tag v3.5.1-plan-frozen | 0.1 wd | tag 创建 |
| **合计** | — | **1.9 wd** | — |

---

## §4.5 Final-Audit 补遗 (10 + 1 = 11 轮 audit)

经 v0.3 release-ready 状态后的"最高质量"最终 audit 发现 3 项 finding：

| ID | Finding | Severity | Resolution |
|---|---|---|---|
| **R1** | plan §2.5.3 `20_substance_disclosure_quality.do.tmpl` 未做 A1 三角化扩展 | HIGH | ✅ 已补 Panel C 三角化 + Panel D 交互 (+22 行) |
| **R2** | plan §2.6 Stata README × 3 paper (substance/locus/benefit_society) 未同步 v3.5.1 模板 | MED | ✅ 已加 v3.5.1 行至 3 README |
| **R3** | P5 `bank_fintech_collab` 不在 paper_registry / derivative_replication, `20_collab_clarity_robustness.do.tmpl` 无 CLI 渲染路径 (dormant template) | MED | ⏸ 暂留 dormant; P5 完整 onboarding (需 en/zh manuscript + refs.bib) 由独立 PR 处理. 加 collab 到 registry 会引 v3.4.0 baseline 4 regression, 故保持 v3.4.0 现状 |

代码质量 lint (新 audit):

| 检查 | 结果 |
|---|---|
| Ruff check on 4 new modules | 修 2 项: unused `import math` in numerical_intensity.py + unsorted imports in 39d main() |
| SyntaxWarning at import | PASS (no warning) |
| 文献锚定卷期 (11 项 plan §10) | PASS (LM 2011 / Bonsall 2017 / Hales 2011 / Henseler 2015 / Fornell-Larcker 1981 / Bagozzi-Yi 1988 / Cohen 1960 / Cronbach 1951 / Nosek 2018 PNAS 全部存在) |
| Stata 模板 jinja 渲染 (5 个) | PASS (4 个通过, 1 个 [collab] = dormant per R3) |
| 完整数据流 production-level smoke | PASS (stage 22 classify_batch + A3 enrich + apply_v3_5_1 → panel +8 列) |
| Plan SHA256 self-reference | 修 1 项: plan §0 改为双层声明 (freeze anchor + current state) 避免循环依赖 |

**总 finding 累计**: 97 (前 10 轮) + 3 (final audit R1/R2/R3) = **100 项**, 其中 99 closed + 1 dormant (R3 P5 follow-up).

---

## §5. 期望 v0.3 状态

| 维度 | 目标 |
|---|---|
| Round 10 audit 复证 | finding = 0 |
| Plan 物理完整性 | ✅ (本文件存在) |
| 双轨契约 | ✅ 真双轨（_dual_analyze 模式）|
| Pre-registration freeze | ✅ 0 BLOCKER + 0 CRITICAL |
| Disclosure 累积 | ≤ 3 处（不可完全消除）|
| Stata 层覆盖 | 99% |
| audit_rounds_target_min: 8 | ✅ 已达 9 轮（v0.3 后第 10 轮 = 10 轮）|
| Streak | epoch 7 streak 1/3 (v3.5.1 PR 启动) |
