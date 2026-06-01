# Paper: `brokerage_network` — Information Brokerage Network & Causal Identification

**Status (2026-05-15 / post-P4 / commit 8d33c46)**: P0-P4 落地完成. Stata 8 模板 + Python tables/figures + 345 行 network_causal.do (paper-specific override) + en/zh 双语 manuscript 骨架.

## 主题

Brokerage-Network (Han et al. 2024 RFS + Bramoullé--Djebbari--Fortin 2009 JoE + Manski 1993 RES + Burt 1992): 利用银行在金融科技报道共现网络中的中心性 (betweenness / constraint / brokerage eigenvector), 通过**二阶同业语调** (W²·tone) 作为一阶溢出 (W·tone) 的工具变量, 识别同业情感溢出对银行绩效的因果效应; 检验 DCEP / Sandbox 政策冲击下网络位置异质性.

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.panel.network_brokerage` | ~ | 计算 `brokerage_eigen_cent` |
| `news_process.pipeline.panel.network_spillover` | ~ | 计算 `bank_between_cent` / `bank_constraint` / `peer_tone_lag1_*` / `peer_tone_2nd_lag1_*` |
| `news_process.papers.brokerage_network.analysis` | 68 | CLI 入口 |
| `news_process.papers.brokerage_network.tables` | 81 | Table 1-5 (描述 + Network 2SLS + DCEP/Sandbox 交互 + SOE 异质性 + 稳健性) |
| `news_process.papers.brokerage_network.figures` | 93 | Figure 1 (centrality 分布) + Figure 2 (Network 2SLS coefplot) + Figure 3 (policy forest) |

## 资产目录约定

```
papers_assets/brokerage_network/
├── README.md          ← 本文件
├── do/                ← Stata
│   └── network_causal.do   ← 345 行 (OLS + Net-2SLS + DCEP×3 + Sandbox×3 + Ctx)
├── output/            ← (gitignored)
└── drafts/
    ├── en/manuscript.tex + refs.bib
    └── zh/manuscript.tex + refs.bib
```

## P0-P4 交付物 (commit 8d33c46)

| 层 | 交付 |
|---|---|
| Stata | 8 .do.tmpl @ `_common/stata_templates/brokerage_network/` + 345 行 paper-specific network_causal.do (保留) |
| Python | `tables.py` 5 函数 + `figures.py` 3 函数 |
| 复现包 | `python -c "from news_process.papers._common.derivative_replication import build_derivative_replication_package as b; b('brokerage_network')"` |
| Manuscript | en (86 行 / 10 TODO) + zh 双语骨架 + refs.bib |

## 关键变量 (Paper-specific defaults)

- `MAIN_DV`: ROA
- `MAIN_ENDOG`: `peer_tone_lag1_full` (一阶同业溢出)
- `MAIN_IV`: `peer_tone_2nd_lag1_full` (二阶溢出, Bramoullé 排他性约束)
- `TREATMENT_*`: `dcep_post` / `sandbox_post`
- `CENTRALITY_*`: `bank_between_cent` / `bank_constraint` / `brokerage_eigen_cent` (lagged L1)
- `CLUSTER_VAR`: `prov_id` (省份 / Cameron-Miller 2015 JHR 偏好)

## 仍待用户补充

1. Manuscript 实质内容 (10 TODO/lang)
2. ROA / NPL_ratio / Z_score 等会计 DV 并入 panel
3. Network 2SLS 的弱 IV 诊断 (Kleibergen-Paap F > 10 验证)
4. L2.brokerage_eigen_cent 二阶滞后稳健性

## 学术依据

- Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of Peer Effects. *JoE*, 150(1).
- Manski, C. F. (1993). Identification of Endogenous Social Effects. *RES*, 60(3).
- Han, M., Kim, S. H., Nanda, V., & Ramadorai, T. (2024). Institutional Brokerage Networks. *RFS*, 37(9).
- Burt, R. S. (1992). *Structural Holes*. Harvard University Press.
- Cameron, A. C., & Miller, D. L. (2015). Cluster-Robust Inference. *JHR*, 50(2).
