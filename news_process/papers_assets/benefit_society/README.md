# Paper: `benefit_society` — Operating-Benefit Attitude Projection

**Status (2026-05-15 / post-P4 / commit 8d33c46)**: P0-P4 落地完成. Stata 8 模板 + Python tables/figures + 187 行 token_hidden_regression.do (paper-specific override) + en/zh 双语 manuscript 骨架.

## 主题

Benefit-Society (Jha, Liu & Manela 2026 RFS §1.3.2 + Westphal--Zajac 2001 ASQ + Distel et al. 2026 RP): 用 LLM-Embedding **双极锚点投影** (a_j = cos(s_j, pos-neg)) 测度银行 FinTech 报道的"经营效益态度", 检验其对银行绩效与 Token/Hidden 采纳行为的影响.

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.features.benefit_society` | ~ | 计算 `benefit_mean_full` / `benefit_pos_frac_full` 等 |
| `news_process.papers.benefit_society.analysis` | 78 | CLI 入口 + Table 2-5 调度 |
| `news_process.papers.benefit_society.tables` | 78 | Table 1-5 (描述 + 主回归 + Token/Hidden 机制 + SOE 异质性 + 稳健性) |
| `news_process.papers.benefit_society.figures` | 91 | Figure 1 (attitude 分布) + Figure 2 (主回归 coefplot) + Figure 3 (mechanism forest) |

## 资产目录约定

```
papers_assets/benefit_society/
├── README.md          ← 本文件
├── do/                ← Stata
│   └── token_hidden_regression.do   ← 187 行, 4 层架构 (m1-m12)
├── output/            ← (gitignored)
└── drafts/
    ├── en/manuscript.tex + refs.bib
    └── zh/manuscript.tex + refs.bib
```

## P0-P4 交付物 (commit 8d33c46)

| 层 | 交付 |
|---|---|
| Stata | 8 .do.tmpl @ `_common/stata_templates/benefit_society/` (00_master / 01_data_prep / 10_table1 / 11_table2_main / 12_table3_mechanism / 13_table4_het / 14_table5_robust / 30_figure1) + 187 行 paper-specific token_hidden_regression.do (保留) |
| Python | `tables.py` 5 函数 + `figures.py` 3 函数 |
| 复现包 | `python -c "from news_process.papers._common.derivative_replication import build_derivative_replication_package as b; b('benefit_society')"` |
| Manuscript | en (86 行 / 10 TODO) + zh 双语骨架 + refs.bib |

## 关键变量 (Paper-specific defaults)

- `MAIN_DV`: ROA (or CAR for short-term reaction in M3)
- `ATTITUDE_VAR`: `benefit_mean_full`
- `MECHANISM_*`: `token_adopt_kw_p50` / `hidden_adopt_kw_p50` / `subst_adopt_kw_p50`
- `CLUSTER_VAR`: `bank_id`

## 仍待用户补充

1. Manuscript `\\NoteThis{...}` 占位 (10 TODO/lang)
2. ROA / CAR 等会计变量并入 panel
3. Token/Hidden 阈值 (P25/P50/P75) 与 INT 轨道的实证对比

## 学术依据

- Jha, M., Liu, H., & Manela, A. (2026). Does Finance Benefit Society? *RFS*, 39(5).
- Westphal, J. D., & Zajac, E. J. (2001). Decoupling Policy from Practice. *ASQ*, 46(2).
- Distel, A. P., Grimpe, C., & Poetz, M. (2026). From Evidence to Impact. *Research Policy*, 55(3).
- Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The Geometry of Culture. *ASR*, 84(5).
