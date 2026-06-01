# Independent R&D vs. External Collaboration: Open Innovation in Chinese Bank Fintech Strategy

**Paper ID**: `bank_fintech_collab` (P5)
**Status**: M3 skeleton (M0 G0 spec frozen 2026-05-17, manuscript implementation M5/M6)
**Master plan**: B_route_master_plan_v2 (内部规划文档; docs/ 目录已于 commit 1698bda5 整体删除, 无存留副本)

---

## Abstract

[M3 阶段填实 ~250 words]

How does a bank's mode of fintech innovation — independent in-house R&D versus external collaboration — shape its long-run capability building, market response, and downstream M&A activity? We construct a novel firm-level binary measure of *innovation collaboration mode* from a large-scale corpus of Chinese fintech news (2007-2024; 500 banks; 400k articles), classified by a triangulated LLM ensemble anchored to Chesbrough's (2003) Open Innovation framework and Laursen & Salter's (2006) search breadth–depth taxonomy. ...

---

## 1. Introduction

[M3 阶段填实 ~1500 words]

- Motivating puzzle: fintech 银行的 "自主 vs 协同" 决策路径与传统制造业 R&D 路径有何异同？
- 现有文献缺口: existing literature 多以单维度衡量 fintech 创新（量、质、locus），但忽视组织来源 (open vs closed)
- 本研究贡献: novel firm-level binary measure + 2³ cross-tab with existing P3/P4 dimensions

---

## 2. Theoretical Framework

[M3 阶段填实 ~2000 words]

### 2.1 Open Innovation (Chesbrough 2003)
### 2.2 Search Breadth and Depth (Laursen & Salter 2006)
### 2.3 Inter-firm R&D Partnerships (Hagedoorn 2002)
### 2.4 Orthogonality to P3 (substantiveness) and P4 (locus)

Cross-tab 2³ = 8 cells (collaboration mode × P3 substantiveness × P4 locus):
- Substantive × Tech × Independent → 真实能力建设 (internal-tech 路径)
- Substantive × App × External → ecosystem play (open-API + 业务侧)
- Symbolic × External → strategic alliance signaling (decoupling per Fiss & Zajac 2006)
- ... (完整 8-cell 枚举待 M3 阶段在本稿 §2.4 inline 补全)

---

## 3. Data and Method

[M3 阶段填实 ~2500 words]

### 3.1 Sample
- 400,000 news articles, 500 Chinese commercial banks, 2007-2024 (18 years)
- M0.5 全量重跑 pipeline produces 46_panel_yearly_v34.dta (~3000-9000 obs)

### 3.2 Measurement: Innovation Collaboration Mode
- LLM ensemble (gpt-5.4-nano + gemini-3.1-flash-lite + deepseek-v4-flash) majority vote
- Prompt v8 (additive supplementation over v7; dedicated git tag `prompt-v8-supplementation-released` not yet created; only `prompt-v7-released` currently exists)
- Binary encoding: 0 = 自主研发 (independent R&D), 1 = 外部协同 (external collaboration)
- Inter-track κ ≥ 0.45 (mirrors the P3 substantiveness fair-to-moderate threshold; threshold defined in `pipeline/audit/inter_track_kappa.py::_THRESHOLDS` per Landis & Koch 1977)

### 3.3 Outcome Variables
- Primary: `m_and_a_fintech` (M&A event count from Tonghuashun)
- Short-run: `car_5day_window` (5-day market-adjusted CAR, 中证银行指数 benchmark)
- Secondary: `r_and_d_intensity`, `patent_fintech_count`, `capex_it`

### 3.4 Identification
- Baseline: long-panel within-bank within-year FE
- Event-study: E1 (yuebao 2013) / E3 (资管新规 2017) / E4 (蚂蚁 IPO 暂停 2020)

---

## 4. Results

[M5 阶段填实 ~2500 words; Table 2 主回归 M1-M6 progressive specs + Table 3 机制 + Table 4 异质性]

---

## 5. Robustness

[M6 阶段填实 ~1500 words; Table 5 advanced robustness battery]

---

## 6. Discussion

[M6 阶段填实 ~1500 words]

- Mechanism: open innovation 是否优于 closed innovation 取决于 fintech 业务侧 vs 技术侧
- Practical implication for 银行管理者
- Limitations: binary proxy 限制（spectrum nature of Chesbrough/L&S; 详见本稿末 Limitations Statement）

---

## 7. Conclusion

[M6 阶段填实 ~500 words]

---

## References

[M3/M6 阶段累积, 共用 §2.3 anchor 15 + paper-specific 衍生 15-25]

- Chesbrough, H. (2003). *Open Innovation: The New Imperative for Creating and Profiting from Technology.* HBS Press.
- Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among UK manufacturing firms. *Strategic Management Journal*, 27(2), 131-150.
- Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. *Research Policy*, 31(4), 477-492.
- Cohen, W. M., & Levinthal, D. A. (1990). Absorptive capacity: A new perspective on learning and innovation. *Administrative Science Quarterly*, 35(1), 128-152.
- [...]

---

## Limitations Statement (Pre-registration β supplementation)

This paper measures innovation collaboration mode using a binary classification (independent R&D vs. external collaboration) as a discrete proxy for Chesbrough's open innovation spectrum and Laursen & Salter's continuous search breadth–depth dimensions. The binary measure compresses information about partnership intensity, partner type, and collaborative scope, which future research can extend to multi-class formulations (e.g., M&A vs. strategic investment vs. API openness vs. industry alliance).

The prompt template used for LLM classification (prompt v8) is an *additive supplementation* of the pre-registered v7 prompt (anchored at git tag `prompt-v7-released`); v7's verification, sentiment, substantiveness, and locus criteria are preserved verbatim (additive non-revisionary adjustment per Nosek et al. 2018 PNAS). The new collaboration mode dimension is to be committed at git tag `prompt-v8-supplementation-released` upon M5 finalization (this tag is not yet created).
