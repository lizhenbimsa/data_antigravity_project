# Paper: `llm_peer` — LLM-Peer Competition Network IV

**Status (2026-05-15 / post-P4 / commit 8d33c46)**: P0-P4 落地完成。Paper-level 资产、Python tables/figures、Stata 14 模板、中英双语 manuscript 骨架均到位; 仅 manuscript 实质内容 (\\NoteThis{...} 占位) 待作者填充。

## 主题

LLM-Peer (Cao, Li, Wang & Zhao 2025, RAS) 同业竞争网络 IV: 用 LLM 判定的语义同业关系 (vs 传统 SIC 行业代码) 构造 leave-one-out 工具变量，估计同业语调溢出对银行 fintech 战略响应的因果效应。

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.panel.llm_peer_iv` | 714 | 计算 `llm_peer_tone_iv_full` / `llm_peer_count` / `peer_compete_idx` 等 panel 列 |
| `news_process.papers.llm_peer.analysis` | 71 | CLI 入口 (`--stage pipeline\|tables\|figures\|all`) |
| `news_process.papers.llm_peer.tables` | 75 | Table 1-5 (描述 + IV 2SLS + cutoff + heterogeneity + robustness) |
| `news_process.papers.llm_peer.figures` | 96 | Figure 1 (cutoff dist) + Figure 2 (main IV coefplot) + Figure 3 (het forest) |

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
| Stata | 8 .do.tmpl @ `_common/stata_templates/llm_peer/` (00_master / 01_data_prep / 10_table1 / 11_table2_iv_2sls / 12_table3_cutoff / 13_table4_het / 14_table5_robust / 30_figure1_F) |
| Python | `tables.py` 5 函数 + `figures.py` 3 函数 |
| 复现包 | `python -c "from news_process.papers._common.derivative_replication import build_derivative_replication_package as b; b('llm_peer')"` |
| Manuscript | en + zh 双语骨架 (8 节标准结构 + V6 F1-F4 注入) + refs.bib |

## 仍待用户补充

1. Manuscript 内 `\\NoteThis{...}` 占位 (Intro / Lit Review / Results / Conclusion 等实质内容)
2. BibLaTeX 文献库扩展 (当前 6 条共享 + 2 条 LLM-Peer 专属, 需扩到 ~30-50 条)
3. 实际 ROA / Tobin_Q 等会计变量并入 panel 后, 跑通 32 .do 端到端验证

## 学术依据

- Cao, Z., Li, W., Wang, Y., & Zhao, Y. (2025). Can generative AI help identify peer firms? *Review of Asset Studies*, forthcoming.
- Stock, J. H., & Yogo, M. (2005). Testing for weak instruments. In Andrews & Stock (Eds.).
- Kleibergen, F., & Paap, R. (2006). Generalized reduced rank tests. *JoE*, 133(1).
- Manski, C. F. (1993). Identification of endogenous social effects. *RES*, 60(3).
