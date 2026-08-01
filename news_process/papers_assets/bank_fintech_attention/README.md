# Paper: `bank_fintech_attention` (P2) — Bank Fintech Attention Intensity

**Status (2026-05-17 / M0 scaffolded per B-route plan v2.55)**: M0 设计契约冻结. Python modules + paper_spec.yaml + manuscript skeleton 到位. 共享 Stata 模板 (7 个) 已生成于 `papers/_common/stata_templates/bank_fintech_attention/` (2026-05-17, commit 2952bc72). 仅余 paper-specific do/ override (M2) + 实证回归 (M5/M6) 待后续 milestone.

## 主题

P2 = Bank Fintech Attention: 度量银行被 fintech 媒体话题"曝光"的强度 (firm-level attention intensity), 检验该曝光对银行 fintech 战略响应 (年报 fintech 投入披露 / M&A / 专利 / IT 员工增长) 的因果效应.

学术锚定:
- **Hassan, Hollander, van Lent, Tahoun (2019) QJE 134(4), 2135–2202** — firm-level political risk text-based exposure (主方法论 anchor)
- **Florackis, Louca, Michaely, Weber (2023) RFS 36(1), 351–407** — cybersecurity exposure (text-in-finance exemplar)
- **Gomber, Kauffman, Parker, Weber (2018) JMIS 35(1), 220–265** — fintech taxonomy (secondary anchor)

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.filtering.fintech_intensity` (stage 14) | ~ | 计算 fintech intensity 双轨列 (上游 attention 输入) |
| `news_process.pipeline.panel.attention_media::compute_attention_treatments` | ~ | 物化 firm-level Hassan-style 设计列 `attention_index_full` / `attention_index_ctx` / `attention_index_ss` / `attention_pct_full` / `attention_disp_full` (含 density/sd 孪生); runner 步骤 6b-2, verified-domain gated, 标签在 export.py |
| `news_process.pipeline.panel.attention_media::compute_fintech_attention_index` | ~ | 计算地理三级 attention 比值, 产出 `ft_attn_yr` / `ft_attn_prov` / `ft_attn_city` + 总量孪生 `ft_vol_yr` / `ft_vol_prov` / `ft_vol_city` (runner 步骤 6b; 与上一行 firm-level 设计列是两套不同度量) |
| `news_process.papers.bank_fintech_attention.analysis` | ~60 | CLI 入口 (--stage pipeline\|tables\|figures\|all) |
| `news_process.papers.bank_fintech_attention.tables` | ~80 | Table 1-5 (descriptive + main + mechanism + heterogeneity + robustness) |
| `news_process.papers.bank_fintech_attention.figures` | ~45 | Figure 1 (attention 分布) — 后续扩展 event study + time trend |

## 资产目录约定

```
papers/bank_fintech_attention/
├── __init__.py        ← PAPER_ID = 'bank_fintech_attention'
├── paper_spec.yaml    ← M0 G0 frozen spec (per plan §B.2)
├── analysis.py        ← CLI 入口
├── tables.py          ← Table 1-5
└── figures.py         ← Figure 1+

papers_assets/bank_fintech_attention/
├── README.md          ← 本文件
├── do/                ← Stata override (M2 阶段填; 共享模板在 papers/_common/stata_templates/bank_fintech_attention/)
├── output/            ← (gitignored)
└── drafts/
    ├── en/manuscript.tex + refs.bib    ← 英文版手稿骨架 (M3 阶段填实质内容)
    └── zh/manuscript.tex + refs.bib    ← 中文版手稿骨架
```

## M0 交付物 (2026-05-17)

| 层 | 交付 |
|---|---|
| Spec | `paper_spec.yaml` (status: new; 原 B-route master plan §B.2 已随 docs/ 目录整体删除) |
| Python | `analysis.py` / `tables.py` / `figures.py` 骨架 |
| Manuscript | en + zh manuscript.tex 骨架 (M3 实质填充) |
| Stata | 共享模板 7 个已生成于 `papers/_common/stata_templates/bank_fintech_attention/` (00_master / 01_data_prep / 15_attention_main_regression / 16_attention_mechanism / 17_attention_heterogeneity / 18_attention_robustness / 19_attention_iv_first_stage); paper-specific do/ override 仍 M2 阶段填 (当前仅 .gitkeep) |

## 关键变量

- `MAIN_DV`: `ln_fintech_investment` (银行年报 fintech 投入披露, M0.5.11 enrichment)
- `MAIN_TREAT`: `attention_index_full` (firm-level Hassan-style attention intensity)
- `MEDIATOR`: `ln_fintech_mdna_length` (年报 MD&A fintech 章节文本长度; observable proxy)
- `IV.primary`: `leave_one_out_peer_attention_iv` (firm-level peer mean)
- `IV.fallback`: `bartik_attention_iv` (需要 pre-2007 bank fintech-lending share, CSMAR)
- `CLUSTER_VAR`: `bank_id`

## 投稿目标 (per spec.targets)

- Primary: **JCF** (Journal of Corporate Finance)
- Ambitious: **JFE** (Journal of Financial Economics)
- Backup cascade: **JBF → JFI** (backup_outlet=[JBF, JFI]; 原 B-route master plan 章节锚点已随 docs/ 目录整体删除而不可达)
- Submission window: **2027-03-15**

## DiD 设计 (per spec.event_studies)

P2 applicable events (原 B-route master plan 章节锚点已随 docs/ 目录整体删除而不可达):
- **E1** (2013-06-13 余额宝上线)
- **E2** (2016-08-24 P2P 整顿)
- **E4** (2020-11-03 蚂蚁 IPO 暂停)
- **E5a** (2022-09-01 数据出境安全评估办法)
- **E5b** (2023-09-30 数据出境管理办法)

总 P2 DiD spec count: **5** (与原 B-route master plan 的 17 spec total 中 P2 部分一致; 该 master plan 已随 docs/ 目录整体删除).

## 仍待用户补充 (prerequisites; 原 B-route master plan 章节锚点已随 docs/ 目录整体删除而不可达)

1. Raw 语料的物理位置 / 访问凭证 (D1 决策点)
   - **disk 实测 (2026-08-01)**: 1,247 banks × 19 yr (2007-2025) = 23,693 obs (其中 6,224 格 n_articles>0); ⚠ 旧载「84 banks × 2 yr (2017-2018) = 168 obs」系 T=2 试跑期数字, 已作废 (`40_panel_yearly.parquet`,
     frozen 2026-05-16)
   - **M0.5 production run 目标**: ~500 banks × 19 yr (2007-2025) ≈ 9500 obs
   - **R1-R5 audit fix A10 (2026-05-27)**: 此前文档 "Raw 40 万条语料" 与 disk
     168 obs 实测严重 mismatch, 是 R5-A2 消费者视角识别的"学术诚信公关风险".
     修正为 M0 baseline / M0.5 target 两阶段说明, 避免 reviewer / 监管 grep
     replication 包发现 claim-actual gap 后公开质疑.
2. CSMAR/Wind 银行模块访问凭证 (M-1.6 财务匹配率审计 + M0.5.11 enrichment)
3. M3 manuscript 内 `\NoteThis{...}` 占位 (10 TODO/lang) 的实质内容
