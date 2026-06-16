# Paper: `bank_fintech_substance` (P3) — Substantive vs Symbolic Fintech Strategies

**Status (2026-05-17 / M0 scaffolded per B-route plan v2.55)**: M0 设计契约冻结. Python modules + paper_spec.yaml + manuscript skeleton 到位. Stata templates (M2) + 实证回归 (M5/M6) 待后续 milestone.

## 主题

P3 = Bank Fintech Substance: 度量银行 fintech 战略宣告的"实质性 vs 象征性"差异 (W&Z 1994/1998 ASQ framework), 检验象征性宣告 → 短期股价正反应 → 长期 ROA 反转的 dual outcome 机制.

学术锚定:
- **Westphal & Zajac (1994) ASQ 39(3)** — substance vs symbolism in CEO long-term incentive plans (主框架 anchor)
- **Westphal & Zajac (1998) ASQ 43(1)** — symbolic management in stock-repurchase 公告
- **Westphal & Zajac (2001) ASQ 46(2)** — decoupling policy from practice
- **Fiss & Zajac (2006) AMJ 49(6), 1173–1193** — symbolic management of strategic change (SMJ-style exemplar)
- **Bromiley & Rau (2014) SMJ 35(8), 1249–1256** — practice-based view of strategy (style exemplar)

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.sentiment.tone_llms` (v3.2.0 stage 21) | ~ | 计算 `innovation_substantiveness_full` / `_ctx` 二元 W&Z 标签 |
| `news_process.papers.bank_fintech_substance.analysis` | ~60 | CLI 入口 |
| `news_process.papers.bank_fintech_substance.tables` | ~80 | Table 1-5 (descriptive + main + dual_outcome + heterogeneity + robustness) |
| `news_process.papers.bank_fintech_substance.figures` | ~45 | Figure 1 (substantiveness 分布) |

## 资产目录约定

```
papers/bank_fintech_substance/
├── __init__.py        ← PAPER_ID = 'bank_fintech_substance'
├── paper_spec.yaml    ← M0 G0 frozen spec (原 B-route master plan §B.3 已随 docs/ 目录整体删除)
├── analysis.py        ← CLI 入口
├── tables.py
└── figures.py

papers_assets/bank_fintech_substance/
├── README.md
├── do/
├── output/
└── drafts/{en,zh}/manuscript.tex + refs.bib
```

## M0 交付物 (2026-05-17)

| 层 | 交付 |
|---|---|
| Spec | `paper_spec.yaml` (status: new; 原 B-route master plan §B.3 已随 docs/ 目录整体删除) |
| Python | `analysis.py` / `tables.py` / `figures.py` 骨架 |
| Manuscript | en + zh manuscript.tex 骨架 (M3 实质填充) |
| Stata | 14 templates = 00_master + 01_data_prep + 15_substance_main_regression + 16_substance_mechanism + 17_substance_heterogeneity + 18_substance_robustness + 19_substance_lr_reversal + 20_substance_disclosure_quality + 21_substance_clarity_robustness + 22_substance_iv_2sls + 23_substance_agg_robustness + 24_substance_fe_est_robustness + 25_substance_subsamples + 26_substance_era_stability (已生成于 papers/_common/stata_templates/bank_fintech_substance/; 22-26 为 post-M0 新增: 2026-06-13 IV 补全 + 2026-06-14 顶刊稳健性/era 稳定性扩充) |

## 关键变量 (Dual Outcome)

- `OUTCOME.primary`: `cost_income_ratio_change_3yr` (2026-06-13 outcome 重定位: within-bank 3-year forward CIR change, W&Z decoupling 效率试金石; 原 `long_run_roa_change_3yr` 降级 secondary)
  - Construction: `cost_income_ratio_change_3yr[bank_b, year_t] = CIR[b, t+3] - CIR[b, t]`
- `OUTCOME.listed_subsample_extension`: `car_3day_window_fintech_announcement` (短期 CAR 事件窗口, 与 P1 tone_shock 窗口区分; 年度数据约束下降级上市行扩展, Stata 列用 ≤32 字符短名 `car_3day_window_ft_announce`)
- `MAIN_TREAT`: `sub_frac` (bank-year panel 实质性文章占比列 = n_articles_sub / n_articles_llm_valid, encode.py:1505-1511 产出; stata/05_label_advanced.do:29 打标. NB: `innovation_substantiveness_full`/`_ctx` 是上游 article-level LLM W&Z 标签 (实质性/象征性), 聚合成 sub_frac/sub_frac_sc, 本身**不在** bank-year panel, 非 panel treatment — paper_spec.yaml:48 已纠正)
- `ALT.treat`: `sub_frac_sc` (ctx 轨, 分母 n_articles_llm_valid_ctx) / `substantive_minus_symbolic_gap` (= sub_frac - symb_frac, ∈ [-1, +1], 01_data_prep 现场派生)
- `CLUSTER_VAR`: `bank_id`

P3 **不使用经典 Baron-Kenny mediation**, 而用 **dual outcome regression** (R11-m02 注: 16_mechanism.do template name 仅 stata 命名一致性, header 注明实际是 dual outcome).

## 投稿目标 (per spec.targets sequential_resubmission cascade)

Primary cascade (理论纯化, 同时仅 1 outlet 在审):
1. **SMJ** (Strategic Management Journal) — primary
2. **AMJ** (Academy of Management Journal) — if SMJ reject
3. **ASQ** (Administrative Science Quarterly) — cascade 终点

Salvage path (任一阶段 reject 后):
- 改写为 disclosure quality 框架的独立论文投 **JFE corp finance** track
- (NB: 重新表述研究问题 / 切换理论 anchor / 仅保留 long_run_roa outcome /
  删除组织学叙事 — 是两篇论文, 不是 dual submission, 不违反 ethics)

Submission window: **2027-03-15**.

## DiD 设计 (per spec.event_studies)

P3 applicable events:
- **E1** (2013-06-13 余额宝上线) — substantive-symbolic gap 时间动态起点
- **E2** (2016-08-24 P2P 整顿)
- **E3** (2017-04-27 资管新规) — cross-sectional intensity DiD (pre-2017 理财占比 × post)
- **E4** (2020-11-03 蚂蚁 IPO 暂停)

总 P3 DiD spec count: **4**.

## 仍待用户补充

1. Raw 数据 + CSMAR 财务/CAR/高管离职/薪酬变动 (M-1 + D1 + M0.5.11)
2. M3 manuscript 内 `\NoteThis{...}` 占位的实质内容
