# Paper: `benefit_society` — Operating-Benefit Attitude Projection

**Status (历史 P0-P4 快照, 原 2026-05-15 / commit 8d33c46; 计数已刷新至当前态)**: P0-P4 落地完成. Stata 26 模板 + Python tables/figures + 187 行 token_hidden_regression.do (paper-specific override) + en/zh 双语 manuscript 骨架.

## 主题

Benefit-Society (Jha, Liu & Manela 2026 RFS §1.3.2 + Westphal--Zajac 2001 ASQ + Distel et al. 2026 RP): 用 LLM-Embedding **双极锚点投影** (a_j = cos(s_j, pos-neg)) 测度银行 FinTech 报道的"经营效益态度", 检验其对银行绩效与 Token/Hidden 采纳行为的影响.

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.features.benefit_society` | ~ | 计算 `benefit_mean_full` / `benefit_pos_frac_full` 等 |
| `news_process.papers.benefit_society.analysis` | 116 | CLI 入口 + Table 2-5 调度 |
| `news_process.papers.benefit_society.tables` | 136 | Table 1-5 + A1/A2/8b/A9/A10/A11 (描述 + 主回归 + Token/Hidden 机制 + SOE 异质性 + 稳健性 + inter-track kappa + attitude track switch + shrinkage dual + external validation + placebo + anchor alt) |
| `news_process.papers.benefit_society.figures` | 199 | Figure 1 (attitude 分布) + Figure 2 (主回归 coefplot) + Figure 3 (mechanism forest) + subsampling CI 分布图 + placebo 对比图 |

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
| Stata | 26 .do.tmpl @ `_common/stata_templates/benefit_society/` (00_install_packages / 00_master / 01_data_prep / 10_table1_descriptives / 11_table2_main / 11b_table2_boottest / 12_table3_mechanism / 13_table4_heterogeneity / 14_table5_robustness / 15_table6_effect_size / 16_table7_robustness_loo_anchor / 17_table8_shrinkage_robustness / 17b_table8b_shrinkage_dual / 18_table9_dimension_decomposition / 19_bs_num_intensity_robustness / 20_tableA1_inter_track_kappa / 21_tableA2_attitude_track_switch / 22_tableA9_external_validation / 23_tableA10_placebo_business_lines / 24_tableA11_anchor_family_alternative / 25_tableA12_iv_2sls / 26_tableA13_fe_robust_oster / 27_tableA14_subsample_composition / 28_tableA15_era_stability / 30_figure1_attitude_distribution / 31_figure2_coefplot_dual) + 187 行 paper-specific token_hidden_regression.do (保留) |
| Python | `tables.py` 11 函数 + `figures.py` 5 函数 |
| 复现包 | `python -c "from news_process.papers._common.derivative_replication import build_derivative_replication_package as b; b('benefit_society')"` |
| Manuscript | en (170 行 / 15 TODO) + zh 双语骨架 + refs.bib |

## 关键变量 (Paper-specific defaults)

- `MAIN_DV`: ROA (or CAR for short-term reaction in M3)
- `ATTITUDE_VAR`: `benefit_mean_full`
- `MECHANISM_*`: `token_adopt_kw_p50` / `hidden_adopt_kw_p50` / `subst_adopt_kw_p50`
- `CLUSTER_VAR`: `bank_id`

## 仍待用户补充

1. Manuscript `\\NoteThis{...}` 占位 (en=15 TODO; zh 版本待核对)
2. ROA / CAR 等会计变量并入 panel
3. Token/Hidden 阈值 (P25/P50/P75) 与 INT 轨道的实证对比

## 学术依据

- Jha, M., Liu, H., & Manela, A. (2026). Does Finance Benefit Society? *RFS*, 39(5).
- Westphal, J. D., & Zajac, E. J. (2001). Decoupling Policy from Practice. *ASQ*, 46(2).
- Distel, A. P., Grimpe, C., & Poetz, M. (2026). From Evidence to Impact. *Research Policy*, 55(3).
- Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The Geometry of Culture. *ASR*, 84(5).
