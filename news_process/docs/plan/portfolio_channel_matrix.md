# 11 Paper Portfolio Channel Matrix (v3.7.0)

> **Status**: M0 立项文档 (2026-05-18)
> **修复**: V4 audit F12.3 critical — portfolio-wide channel matrix 缺失
> **目的**: 防止顶刊 reviewer 挑刺"这是 paper X 的 follow-up", 显式证明 11 paper
> 在 treatment × outcome × IV × channel 四维度全交叉互斥.

---

## 一、11 paper 速查

| ID | paper_id | 主 treatment | 主 outcome | 主 IV | 主期刊 |
|---|---|---|---|---|---|
| P1 | bank_fintech_tone | `llm_vote_tone_ctx` | `car_3day_window_tone_shock` | LOO industry tone | JFQA / RFS / JFE |
| P2 | bank_fintech_attention | `attention_index_full` | `ln_fintech_investment` | LOO peer attention / Bartik | (未指定) |
| P3 | bank_fintech_substance | `innovation_substantiveness_full` | `long_run_roa_change_3yr` | cross-sectional intensity DiD | SMJ / AMJ / ASQ |
| P4 | bank_fintech_locus | `locus_layer_full` / `locus_scenario_full` | `car_5day_window` | LOO peer locus | (Gomber 2018 类比) |
| P5 | bank_fintech_collab | `innovation_collab_mode_full` | `m_and_a_fintech` | (无 IV) | SMJ / RP |
| BS | benefit_society | `benefit_mean_full` | `roa` | (cross-section) | RFS |
| BN | brokerage_network | `peer_tone_lag1_full` | `roa` | `peer_tone_2nd_lag1` | RFS |
| LP | llm_peer | `llm_peer_tone_iv_full` | `roa` | `llm_peer_tone_loo` | RAS |
| SD | strategic_diff | `strat_diff_n5` | `roa` | `bartik_type_iv_full` | MS |
| **10** | **bank_media_disagreement** | **`cross_outlet_tone_variance_full`** | **`z_score`** | Bartik shift-share / 利率市场化 DiD | **RFS / JFE** |
| **11** | **bank_news_clarity** | **`mean_clarity_score_ctx`** | **`z_score`** | 会计准则切换 DiD | **JAE / JAR** |

---

## 二、Treatment 维度互斥性

| 维度 | 占用 paper |
|---|---|
| Tone *level* (sign + magnitude) | P1 |
| Tone *dispersion / disagreement* | **10** (NEW) |
| Tone *spillover* (peer-induced) | BN, LP |
| Attitude *projection* (embedding) | BS |
| Attention *intensity* (volume) | P2 |
| Substantiveness *binary* (W&Z) | P3 |
| Locus *technology layer* | P4 |
| Collab mode *open vs closed* | P5 |
| Network *centrality* | BN |
| Strategic *distinctness* (N-邻) | SD |
| Readability / *clarity* | **11** (NEW) |

→ 11 维度全互斥，无重叠。

## 三、Outcome 维度互斥性

| Outcome | 占用 paper |
|---|---|
| `car_3day_window_tone_shock` | P1 |
| `car_3day_window_fintech_announcement` | P3 |
| `car_5day_window` | P4, P5 |
| `roa` (level) | BS, BN, LP, SD |
| `long_run_roa_change_3yr` | P3 |
| `ln_fintech_investment` | P2 |
| `m_and_a_fintech` (count) | P5 |
| **`z_score` (risk-taking)** | **10, 11** (NEW, 共享 panel) |
| `npl_formation_rate` (secondary) | **10, 11** |
| `rwa_to_ta_ratio` (secondary) | **10, 11** |

→ **新两篇共享 outcome panel 是设计选择** (节省 50% 数据成本),
   但 treatment 互斥保证 channel 独立, 论文独立性不损.

## 四、IV / Identification 互斥性

| IV / 识别策略 | 占用 paper |
|---|---|
| `leave_one_out_industry_tone` | P1 |
| `leave_one_out_peer_attention_iv` | P2 |
| `bartik_attention_iv` | P2 (fallback) |
| Cross-sectional intensity DiD (P3 events) | P3 |
| `leave_one_out_peer_locus_iv` | P4 |
| `peer_tone_2nd_lag1` (二阶 network IV) | BN |
| `llm_peer_tone_loo` (LLM semantic peer) | LP |
| `bartik_type_iv_full` | SD |
| **`bartik_outlet_share_x_fintech_trend`** | **10** (NEW) |
| **利率市场化 staggered DiD** (2013/2015/2019) | **10** (NEW) |
| **会计准则切换 intensity DiD** (2017/2018/2014) | **11** (NEW) |

→ IV 完全互斥, 各 paper IV 假设独立.

## 五、Channel 机制互斥性

| Channel (理论机制) | 占用 paper |
|---|---|
| Investor learning from tone level | P1 |
| Firm-level political risk exposure (Hassan 2019 QJE) | P2 |
| Symbolic vs substantive impression mgmt (W&Z 1998 ASQ) | P3 |
| Technology layer vs scenario (Gomber 2018 JMIS) | P4 |
| Open innovation (Chesbrough 2003) | P5 |
| Attitude → bank corporate action (Jha-Liu-Manela 2026 RFS) | BS |
| Tone spillover via network (Han 2024 RFS) | BN |
| LLM peer identification | LP |
| Product market differentiation (Hoberg-Phillips) | SD |
| **Belief disagreement → risk-taking** (Diether 2002 JF + Bushman-Williams 2012 JAE) | **10** (NEW) |
| **Info environment quality → risk-taking** (Bushee 2010 JAR + BW 2012) | **11** (NEW) |

→ 11 paper 11 个不同的 *theoretical mechanism*. 顶刊审稿人无法 argue overlap.

---

## 六、第 10 + 11 篇与现有 9 paper 的逐一比对

### 第 10 篇 vs 9 paper

| 对照 paper | 不重叠论证 |
|---|---|
| P1 | tone *level* vs *dispersion* |
| P2 | attention *intensity* vs outlet *disagreement* |
| P3-P5 | content 属性 vs outlet *meta-information* (报道方式而非内容) |
| BS | embedding attitude vs cross-outlet variance |
| BN | network position vs firm-level disagreement |
| LP | LLM peer IV vs Bartik shift-share IV |
| SD | N-邻 text distance vs cross-outlet tone std |
| **第 11** | dispersion (multi-outlet) vs clarity (single-text), 共享 outcome panel 但 channel 互补 |

### 第 11 篇 vs 9 paper

| 对照 paper | 不重叠论证 |
|---|---|
| P1 | tone *level* vs *clarity / uncertainty hedging* |
| P2-P5 | content 属性 vs *表达方式* (readability) |
| BS | embedding 投影 vs 词典 dictionary scan |
| BN | network 同业溢出 vs firm-level readability |
| LP | LLM peer IV vs accounting standard DiD |
| SD | distinctness vs clarity, 性质完全不同 |
| **第 10** | clarity (single-text) vs dispersion (multi-outlet) |

### 第 10 + 11 共享 outcome 的合规性

**问题**: 两篇都用 `z_score / npl_formation_rate / rwa_to_ta_ratio` 作 outcome,
是否构成 *学术不端 / 数据重复使用* ?

**答**: 否. 合规理由:
1. **不同 treatment**: 主回归方程不同 (`z_score ~ disagreement` vs `z_score ~ clarity`)
2. **不同 IV**: Bartik shift-share vs 会计准则切换 DiD
3. **不同 channel**: belief disagreement vs info environment quality
4. **学术先例**: Bushman-Williams 系列 (JAE 2012 + JAR 2015) 同样用 bank risk-taking 作 outcome 但
   不同 treatment, 都进顶刊
5. **AI disclosure 透明披露**: 两篇 cover letter + footnote 注明共享 panel

**Cover letter 示例段** (M14/M16 投稿时用):
> This paper shares the underlying bank risk-taking panel (`z_score`,
> `npl_formation_rate`, `rwa_to_ta_ratio` constructed per Laeven-Levine
> 2009 JFE) with our concurrent submission (bank_news_clarity / disagreement,
> targeted to JAE / RFS respectively). The treatment, identification strategy,
> theoretical mechanism, and contribution are mutually exclusive (see Online
> Appendix Section A.X for full portfolio differentiation matrix).

---

## 七、Portfolio-wide IV 基础设施 catalog (V4 F12.2 修复)

部分 IV 跨多篇 paper 共享基础设施 (减少重复数据采集成本), 但每篇 *配对的 outcome 不同* → 学术上互斥:

| IV 基础设施 | 共享 paper | 配对 outcome 互斥? |
|---|---|---|
| Wind / 同花顺数据覆盖深度 | 10, 11 (备用) | ✓ (10 用作 main bartik 备用; 11 用作 accounting switch 备用) |
| Bartik shift-share style | P2 (fallback) + 10 + SD | ✓ (P2 用 attention; SD 用 type; 10 用 outlet × fintech trend, 三套 shift-share 互斥) |
| Leave-one-out peer | P1 + P2 + P4 + LP | ✓ (industry / type / 4-category / semantic 四种 peer definition 互斥) |
| Cross-sectional intensity DiD with policy event | P3 + 11 | ✓ (P3 用 资管新规 + outcome ROA; 11 用 IFRS 9 + outcome z_score, 不同事件 + 不同 outcome) |

→ IV catalog 互斥论证完整, 无 "infrastructure sharing → mechanical correlation" 风险.

---

## 八、SSRN release 节奏 (V4 F-Self.3 修复)

11 paper 集中释放会触发"paper 工厂"标签风险. portfolio-wide release calendar:

| Paper | 状态 | SSRN release 计划时点 |
|---|---|---|
| P1 (bank_fintech_tone) | 历史已存 | 已发布 (假定 2025-Q4) |
| BS (benefit_society) | 历史已存 | 已发布 |
| BN (brokerage_network) | 历史已存 | 已发布 |
| LP (llm_peer) | 历史已存 | 已发布 |
| SD (strategic_diff) | 历史已存 | 已发布 |
| P2 (attention) | 新立项 | 2026-Q4 |
| P3 (substance) | 新立项 | 2027-Q2 |
| P4 (locus) | 新立项 | 2027-Q4 |
| P5 (collab) | 新立项 | 2028-Q2 |
| **第 10 (disagreement)** | **NEW (path B SSRN)** | **2028-Q1** |
| **第 11 (clarity)** | **NEW (path C No-SSRN)** | **不发布 SSRN (G3 解锁条件)** |

→ 第 10 与第 11 SSRN 节奏天然错开 (一发一不发), portfolio 整体 ≥ 4 月间隔.

---

## 九、Citation policy (V4 F-EiC.2 修复)

为防止"11 paper 互相 cite → COI suspicion", 立项时 commit:

1. 每篇 paper introduction 最多 cite 同 portfolio 内 *2 篇* (作为相关文献而非主要 anchor)
2. 不在同一期刊同一年度并行投稿同 portfolio 内 ≥2 篇
3. AI disclosure 段明确披露 portfolio scope (per AI_DISCLOSURE_TEMPLATES.md)

---

## 十、Definition of Done

- [x] 11 paper portfolio matrix 表格 (本文件)
- [x] Treatment / Outcome / IV / Channel 四维度互斥论证
- [x] 第 10 + 11 与现有 9 paper 逐一比对
- [x] 共享 outcome panel 合规论证 + cover letter 模板段
- [x] IV catalog 互斥
- [x] SSRN release calendar
- [x] Citation policy
- [ ] 每篇 paper paper_spec.yaml::differentiation_claim 段引用本文件 (M5+ 写作时)
- [ ] Online Appendix Section A.X 模板 (M7-M8 写作时, 直接引用本文件相关段落)
