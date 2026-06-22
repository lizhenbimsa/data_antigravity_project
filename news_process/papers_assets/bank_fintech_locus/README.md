# Paper: `bank_fintech_locus` (P4) — Layer vs Scenario Fintech Locus

**Status (2026-05-17 / M0 scaffolded per B-route plan v2.55)**: M0 设计契约冻结. Python modules + paper_spec.yaml + manuscript skeleton 到位. Stata templates (M2) + 实证回归 (M5/M6) 待后续 milestone.

## 主题

P4 = Bank Fintech Locus: 区分银行 fintech 公告中的"底层技术 (区块链 / AI / 云)"与"应用场景 (支付 / 信贷 / 理财)"二元 locus 属性, 检验差异化的市场反应与创新产出. 跨三波 fintech 浪潮 + consolidation period 的异质性。

学术锚定:
- **Gomber, Kauffman, Parker, Weber (2018) JMIS 35(1), 220–265** — fintech taxonomy (locus: technology vs business function, 主框架 anchor)
- **Kogan, Papanikolaou, Seru, Stoffman (2017) QJE 132(2), 665–712** — patent market-value 度量算法
- **Goldstein, Jiang, Karolyi (2019) RFS 32(5), 1647–1661** — fintech special issue editorial (RFS-style exemplar)
- **Cong & He (2019) RFS 32(5), 1754–1797** — blockchain disruption (P4 对照; R1-M03 替换 unverifiable Cong-Xie-Zhang 2024)

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.sentiment.tone_llms` (v3.2.0 stage 21) | ~ | LLM 分类产出 `innovation_locus_full` (底层技术 / 应用场景 中文类别列; Gomber 2018 JMIS); Stata 导出时按 `stata_export.py::LOCUS_ENCODING` 编码 底层技术=0 / 应用场景=1 (见 tone_llms.py:~1818 赋值) |
| `news_process.papers.bank_fintech_locus.analysis` | ~60 | CLI 入口 |
| `news_process.papers.bank_fintech_locus.tables` | ~80 | Table 1-5 (descriptive + main + mechanism + heterogeneity + robustness) |
| `news_process.papers.bank_fintech_locus.figures` | ~50 | Figure 1 (layer vs scenario 双柱) |

## 资产目录约定

```
papers/bank_fintech_locus/
├── __init__.py        ← PAPER_ID = 'bank_fintech_locus'
├── paper_spec.yaml    ← M0 G0 frozen spec (原 B-route master plan §B.4 已随 docs/ 目录整体删除)
├── analysis.py        ← CLI 入口
├── tables.py
└── figures.py

papers_assets/bank_fintech_locus/
├── README.md
├── do/                ← (当前仅 .gitkeep; 共享模板 14 个已生成于 papers/_common/stata_templates/bank_fintech_locus/: 00_master / 01_data_prep / 15_locus_main_regression / 16_locus_mechanism / 17_locus_heterogeneity / 18_locus_robustness / 19_locus_clarity_robustness / 19_locus_event_study / 20_locus_iv_2sls / 21_locus_agg_robustness / 22_locus_fe_saturation_oster / 23_locus_subsample_extension / 24_locus_ppml_count / 25_locus_era_stability)
├── output/
└── drafts/{en,zh}/manuscript.tex + refs.bib
```

## 关键变量

### Treatment (primary_pair, R35-M02 derived from `innovation_locus_full`):
- `locus_layer_full`     = 1 if `innovation_locus_full == '底层技术'` else 0  ← 底层 (区块链 / AI / 云)
- `locus_scenario_full`  = 1 if `innovation_locus_full == '应用场景'` else 0  ← 应用 (支付 / 信贷 / 理财)
- `locus_gap`            = `locus_layer_full - locus_scenario_full` ∈ {-1, +1}

### Outcome:
- `MAIN_DV`: `citation_weighted_patent` (Kogan 2017 algo; spec.outcome.primary, 底层技术轨直接产出)
- `SECONDARY`: `patent_fintech_count` (IncoPat) / `noninterest_income_share` (应用场景轨对照 outcome)
- `LISTED_SUBSAMPLE_EXTENSION`: `car_5day_window` (event-window 5-day CAR, 上市行扩展, 非年度主线, 待日频数据)

### Mediator (R7-M04):
- `capex_it`             ← CSMAR 资本支出 IT 板块 (primary)
- `r_and_d_intensity`    ← 国家专利局衍生 R&D investment intensity (secondary)

### IV:
- `iv.primary`: `leave_one_out_peer_locus_iv` (4 银行类型分类 peer mean; Cao 2025 RAS 风格但用分类同业, 不是 LLM-determined 语义同业 — 与 llm_peer paper 机制完全不同)
- `iv.fallback`: `leave_one_out_peer_locus_iv_lag1` (full 轨滞后)

## Heterogeneity Wave (R4-M03 三波严格对称 + consolidation)

| Wave | Years | Description |
|------|-------|-------------|
| `pre_period`    | 2007-2012 | Pre-fintech baseline (中文媒体几乎无"金融科技"一词) |
| `wave_1`        | 2013-2015 | 互联网金融 wave (余额宝触发) |
| `wave_2`        | 2016-2018 | 区块链 / 早期 AI wave |
| `consolidation` | 2019-2021 | 蚂蚁叫停后 monetary tightening + 监管收紧 transition |
| `wave_3`        | 2022-2024 | 大模型 wave |

NB: "三波 fintech 浪潮"严格指 wave_1 / wave_2 / wave_3 各 3 年; consolidation 是 transition (对照组), 不计入"三波"narrative.

## 投稿目标

- Primary: **RFS** (Review of Financial Studies)
- Ambitious: **JF** (Journal of Finance, 顶配)
- Backup: **JFE** (backup_outlet, 2027-09 if reject; 原 B-route master plan §B.4 已随 docs/ 目录整体删除)
- Submission window: **2027-03-15**

## DiD 设计

P4 applicable events:
- **E1** (2013-06-13 余额宝上线)
- **E4** (2020-11-03 蚂蚁 IPO 暂停)
- **E5a** (2022-09-01 数据出境安全评估办法)
- **E5b** (2023-09-30 数据出境管理办法)

总 P4 DiD spec count: **4**.

## 仍待用户补充

1. Raw + CSMAR/Wind 日行情 (M0.5.11 enrichment for car_5day)
2. IncoPat / 国家专利局 fintech 专利计数 + Kogan 2017 市值加权
3. M3 manuscript 实质内容
