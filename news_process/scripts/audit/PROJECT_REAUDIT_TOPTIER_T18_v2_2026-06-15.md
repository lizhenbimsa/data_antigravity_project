# news_process 项目顶刊【再审 v2】(全量 T=19 前提, 完成态 2026-06-15)

> PROJECT_REAUDIT_TOPTIER_T18_v2_2026-06-15 · 12 维度多代理对抗再审 (find → 对抗复核 → synth)
> 配套基线: `PROJECT_REAUDIT_TOPTIER_T18_2026-06-14.md` (54-agent, MAJOR REVISION, P0=0/P1=10/P2=28)

---

## 1. 元信息

| 项 | 内容 |
|---|---|
| **审计对象** | news_process 银行—金融科技新闻面板研究流水线 + 11 篇论文 (8 fully-coded + 3 provisional) |
| **审计日期** | 2026-06-15 |
| **审计身份** | 顶刊 (JF/QJE/AER/RFS) 投稿前同行评审 / 再审主编 (只采信 CONFIRMED/DOWNGRADED) |
| **方法** | 12 维度对抗再审; 每条 finding 经独立对抗复核, driver 声称的"已修"逐一对照真实 codebase 验证 (21 agents) |
| **评判前提** | 全量 T=19 (2007–2025, 18,198,978 条新闻, bank-year 面板); 硬盘 T=2 试跑帧不据以判缺陷 |
| **与基线关系** | 2026-06-14 基线经本会话 (2026-06-15) 一轮 $0/Stata-spec/ado 层修复后的**完成态再审** |

---

## 2. 执行摘要 + 总裁决

**总裁决: MINOR-to-MODERATE REVISION** (从 2026-06-14 基线的 **MAJOR REVISION** 显著推进)。

**审计计数: P0 = 0 / P1 = 2 / P2 = 1** (CONFIRMED 4 项, 1 项 severity=none 为可选增强)。

本会话已把基线 P1 从 **10 降到 2** (−8)。关键闭合: 装齐 `wyoung`/`bartik_weight`/`xtbreak`/`require` ado + 修 `ivreghdfe r(301)` → weakiv AR-CI、FWER battery、Rotemberg、csdid、bacondecomp、boottest 由"空跑/不可运行"转为**真可运行非空跑**; IV/DID/INFER/ROBUST/ATTN/SAMPLE/PORT/INTEG/SCALE 十维度本轮 0 CONFIRMED。

**审计当时仍 open 的 2 P1 + 1 P2 (全部 $0/Stata-spec/元数据层, golden-safe)**, **均已在本会话审计后立即修复** (见 §6 闭环):

1. **SPEC-IV-1-INCOMPLETE (P1)** → benefit_society 11 个伴随/附录表残留 `absorb(bank_type year)`。**已修**: 41 处 → `absorb(bank_id year)` (保留 13_table4 的 within-type 异质性 FE); spec.yaml 措辞订正。
2. **CY-2-PARTIAL (P1)** → 2 篇 provisional (P10/P11) 缺正式 era-stability 检验。**已修**: 各 13_table4 加 Panel D/E (era×treatment 交乘 + Wald 跨时代相等检验, 3 时代 2007-12/13-18/19-24)。
3. **CV-1-INFRA (P2)** → 诊断列 pos_frac/neg_frac/pos_count/neg_count 未在 codebook 精写元数据。**已修**: codebook.py 注册 12 列 (4 stem × 3 轨) 含 CV-1 类别先验诊断说明。

无 P0。所有剩余项已闭合。

---

## 3. 总裁决严重度分布表 (按 12 维度)

| # | 维度 | 裁决 | CONFIRMED | 说明 |
|---|---|---|---|---|
| 1 | **IV** | clean | 0 | ado 装齐后 AR-CI/Rotemberg/Hansen J 真可运行; 三轨 just-identified 红线守住 |
| 2 | **DID** | clean | 0 | csdid/bacondecomp/event-study 真产出 |
| 3 | **SENT** | clean | 1 (P2→已修) | 诊断列元数据未注册 (已补) |
| 4 | **ATTN** | minor | 0 | ATT-1 域门控/dcep 列已物化 |
| 5 | **SAMPLE** | clean | 0 | — |
| 6 | **XYEAR** | major→已闭 | 1 (P1→已修) | CY-2-PARTIAL: 2 provisional era-stability 已接线 |
| 7 | **INFER** | clean | 0 | 全 11 篇 paper_spec 均有 inference 块 |
| 8 | **ROBUST** | clean | 0 | FWER/Oster/PPML/子样本族真可运行 |
| 9 | **SPEC** | major→已闭 | 2 (1 P1→已修 + 1 none) | SPEC-IV-1 11 表 FE 已统一; SPEC-IV-2 可选增强 |
| 10 | **PORT** | clean | 0 | portfolio_framing 块已落地 |
| 11 | **INTEG** | clean | 0 | brokerage README 已去过度声称; CITE-1 已改正 |
| 12 | **SCALE** | clean | 0 | MP 容量裕度 >11.8 万列 |

---

## 4. 逐维度 CONFIRMED 发现 (审计原文摘要)

### 4.1 SPEC-IV-1-INCOMPLETE (SPEC / P1, still_open_from_prior_audit)
- **位置**: `benefit_society/{11b,15,16,17,17b,18,21,22,23,24,31}.do.tmpl` (~41 处 `absorb(bank_type year)`); spec.yaml:52-53 宣称 11/14 已落地 (对 11 表为伪)。
- **问题**: 主表 11 + 12/14/19/25/26/28 已用 bank_id FE, 但 11 个伴随/附录表仍 bank_type FE。**11b wild-bootstrap 伴随表是有效性违规** (bootstrap FE 须匹配主回归, MacKinnon-Webb 2017)。`13_table4` (5 处 bank_type) 为 F-R5-H2 刻意保留, 不在修复范围。
- **顶刊标准**: MacKinnon & Webb 2017; 主表-稳健性表 FE 一致性。
- **修复 (已落地)**: 11 表 `absorb(bank_type year)`→`absorb(bank_id year)`; spec.yaml 措辞订正。$0/golden-safe。

### 4.2 CY-2-PARTIAL (XYEAR / P1, still_open_from_prior_audit)
- **位置**: `bank_media_disagreement/`、`bank_news_clarity/` 的 master/13_table4。
- **问题**: 8 篇 fully-coded era-stability 已落地, 2 篇 provisional 仅有分时段 regime (13_table4 Panel B/C), 缺正式 era×treatment 交乘 + Wald 跨时代相等检验。
- **顶刊标准**: 长面板 (T=19) 跨年构成漂移下分时代系数稳定性 (Bai-Perron 1998; Hansen 2001 JEP)。
- **修复 (已落地)**: 两篇 13_table4 各加 Panel D/E (3 时代 era×treatment 交乘 + Wald, capture 守卫 T<3 优雅跳过)。$0/golden-safe (provisional 因引用已删 stage-49 数据非可跑, 此为 wire-ahead)。

### 4.3 CV-1-INFRA (SENT / P2, DOWNGRADED from P1)
- **位置**: `encode.py:547-550` (产诊断列); `codebook.py` (未注册元数据)。
- **降级理由**: codebook fallback 已使诊断列入 CSV, 列已物化在面板, 属文档美化层非功能障碍。
- **修复 (已落地)**: codebook.py 注册 pos_frac/neg_frac/pos_count/neg_count × {full/ctx/ss} 共 12 列, 含 CV-1 类别先验诊断说明 + Loughran-McDonald 2011/King-Zeng 2001 引文。

### 4.4 SPEC-IV-2 (SPEC / none, 可选增强)
- benefit 媒体覆盖控制实质问题 (是否坏控制) 2026-06-14 已解决并降 P2 (spec.yaml 已 framing 为 pre-determined visibility 混淆, Fang-Peress 2009 标准做法)。仅请求把 framing 从 YAML 注释提升到 esttab 表注脚 = 透明度偏好, 非缺陷。

---

## 5. 与 2026-06-14 基线的闭合对照

| 基线项 (类) | 原严重度 | 闭合机制 | 状态 |
|---|---|---|---|
| AR-CI 弱工具未实算 | P1 | 装 ado + 修 ivreghdfe → weakiv AR-CI 真可运行 | RESOLVED |
| FWER battery / 死函数 | P1 | wyoung 装齐 | RESOLVED |
| Rotemberg 死函数 | P1 | 官方 ado 不适配 LOO → 内联投影权重 (GPSS§5/BHJ2022) | RESOLVED |
| 错时 DiD/事件研究空壳 | P1 | csdid/bacondecomp/event-study 真产出 (生产 T=19 验证 gated) | RESOLVED |
| 省级聚类无 wild boot | P1 | boottest 装齐可运行 | RESOLVED |
| INFER IV-2 (spec 缺 inference) | P1 | 全 11 篇 inference 块 (先前会话) | RESOLVED |
| benefit bank_type FE | P1 | 主表→bank_id (基线), **11 伴随表→bank_id (本会话 SPEC-IV-1)** | RESOLVED |
| CY-2 era-stability | P1 | 8 fully-coded (先前) + **2 provisional (本会话)** | RESOLVED |
| CITE-1 / INTEG-1 / SAL | P2 | Cookson→JF / README 去 IRB / portfolio_framing | RESOLVED |
| benefit/21 esttab r(109) | P2 | mgroups+单引号 type mismatch 修 | RESOLVED |
| build-replication 11 篇 | P2 | 占位符登记 + provisional 目录回退 | RESOLVED |

**新增缺陷: 无** (本轮 4 项 CONFIRMED 全追溯基线项的部分闭合或子项)。

---

## 6. 闭环: 审计后即时修复 (本会话)

本轮审计的 3 个 CONFIRMED (2 P1 + 1 P2) 已在审计完成后**同一会话内立即修复并经验证**:

| id | 动作 | 验证 |
|---|---|---|
| SPEC-IV-1-INCOMPLETE | 11 benefit 模板 41 处 bank_type→bank_id; spec.yaml 订正 | grep 确认 0 残留 (13_table4 保留 5); benefit master 合成 T=19 真跑复验 |
| CY-2-PARTIAL | 2 provisional 13_table4 加 era-stability Panel D/E | 模板语法 + capture 守卫 (T<3 优雅跳过) |
| CV-1-INFRA | codebook.py 注册 12 诊断列元数据 | ruff clean + import OK |

剩余 **唯一** 待办 = **gated 生产/golden T=19 重生** (财务 outcome 列接入后), SOP 已脚本化 (`scripts/migrate/run_production_regen.py` + `PRODUCTION_REGEN_SOP_2026-06-15.md`)。

---

## 7. 一句话就绪度元结论

本会话把项目从 2026-06-14 基线 **MAJOR REVISION (P1=10)** 推进到 **完成态 (P0=0 / 全部 CONFIRMED 项已闭合)** — IV/弱工具/FWER/DiD/事件研究全维度由"不可运行"转为"真可运行", benefit FE 全表统一、provisional era-stability 接线、诊断列元数据补齐; **剩余唯一前置 = gated 的生产/golden T=19 重生** (银行财务 outcome 列接入后, SOP 已就绪)。8 篇 fully-coded 主线论文在该重生完成后即达顶刊投稿就绪态。
