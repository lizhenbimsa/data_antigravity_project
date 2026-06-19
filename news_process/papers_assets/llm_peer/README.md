# Paper: `llm_peer` — LLM-Peer Competition Network IV

**Status (2026-05-15 / post-P4 / commit 8d33c46)**: P0-P4 落地完成。Paper-level 资产、Python tables/figures、Stata 12 模板、中英双语 manuscript 骨架均到位; 仅 manuscript 实质内容 (\\NoteThis{...} 占位) 待作者填充。

## 主题

LLM-Peer (Cao, Chen, Tucker & Wan 2025, Review of Accounting Studies) 同业竞争网络 IV: 用 LLM 判定的语义同业关系 (vs 传统 SIC 行业代码) 构造 leave-one-out 工具变量，估计同业语调溢出对银行 fintech 战略响应的因果效应。

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.panel.llm_peer_iv` | 1025 | 计算 `llm_peer_tone_iv_full` / `llm_peer_count` / `peer_compete_idx` 等 panel 列 |
| `news_process.papers.llm_peer.analysis` | 68 | CLI 入口 (`--stage pipeline\|tables\|figures\|all`) |
| `news_process.papers.llm_peer.tables` | 79 | Table 1-5 (描述 + IV 2SLS + cutoff + heterogeneity + robustness) |
| `news_process.papers.llm_peer.figures` | 95 | Figure 1 (cutoff dist) + Figure 2 (main IV coefplot) + Figure 3 (het forest) |

## 资产目录约定

```
papers_assets/llm_peer/
├── README.md          ← 本文件 (paper 主题 + 状态)
├── do/                ← (gitignored) — 历史; P1 起 Stata 模板移至 _common/stata_templates/llm_peer/
├── output/            ← (gitignored) — runtime mkdir; tables/ figures/ logs/
└── drafts/
    ├── en/manuscript.tex + refs.bib    ← 英文版手稿
    └── zh/manuscript.tex + refs.bib    ← 中文版手稿
```

## P0-P4 交付物 (commit 8d33c46)

| 层 | 交付 |
|---|---|
| Stata | 12 .do.tmpl @ `_common/stata_templates/llm_peer/` (00_master / 01_data_prep / 10_table1 / 11_table2_iv_2sls / 12_table3_cutoff / 13_table4_het / 14_table5_robust / 15_tableA6_aggregation_robustness / 16_tableA7_fe_oster_robust / 17_tableA8_subsample_timing / 18_tableA9_era_stability / 30_figure1_F) |
| Python | `tables.py` 5 函数 + `figures.py` 3 函数 |
| 复现包 | `python -c "from news_process.papers._common.derivative_replication import build_derivative_replication_package as b; b('llm_peer')"` |
| Manuscript | en + zh 双语骨架 (8 节标准结构 + V6 F1-F4 注入) + refs.bib |

## 仍待用户补充

1. Manuscript 内 `\\NoteThis{...}` 占位 (Intro / Lit Review / Results / Conclusion 等实质内容)
2. BibLaTeX 文献库扩展 (当前 5 条共享 + 1 条 LLM-Peer 专属 = 共 6 条, 需扩到 ~30-50 条)
3. 跑通 12 .do 端到端验证 (llm_peer 衍生复现包, 与 L34 模板表一致)。2026-06-14 PORT SAL-3 顶刊重审后主回归 DV 改回 `roa` (外部财务哨兵, 撤销 2026-06-13 短暂采用的 avg_ft_intensity_full 主规格 — 该文本量 Y 与 P2 attention 同源派生自同一媒体语料); avg_ft_intensity_full 降为 first-stage 机制佐证 (spec.outcome.mechanism_evidence); roa / Tobin_Q 待财务数据并入 panel 后补跑。

## 学术依据

> **R1-R5 audit follow-up (2026-05-27) — Cao 引用已 unify 到 canonical source**:
> 此前仓库内有 3 个不一致 Cao 引用版本 (R3-A2 / R4-A8 / R5-A1 实测), 已统一
> 到 `pipeline/panel/llm_peer_iv.py:16-18` 内部存证版本. 投稿前 user 需在线
> CrossRef DOI `10.1007/s11142-025-09892-6` 二次验证.

- **Cao, Y., Chen, L., Tucker, J. W., & Wan, C. (2025). Can generative AI help
  identify peer firms? *Review of Accounting Studies*, 30(4), 3344-3386.
  https://doi.org/10.1007/s11142-025-09892-6**
- Stock, J. H., & Yogo, M. (2005). Testing for weak instruments. In Andrews & Stock (Eds.).
- Kleibergen, F., & Paap, R. (2006). Generalized reduced rank tests. *JoE*, 133(1).
- Manski, C. F. (1993). Identification of endogenous social effects. *RES*, 60(3).
