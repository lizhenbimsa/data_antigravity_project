# Paper: `strategic_diff` — Strategic Differentiation in Bank FinTech Coverage

**Status (2026-05-15 / post-P4 / commit 8d33c46)**: P0-P4 落地完成. Stata 8 模板 + Python tables/figures + 268+119=387 行 paper-specific .do (override) + en/zh 双语 manuscript 骨架.

## 主题

Strategic-Diff (Guzman & Li 2023 MS + Hoberg & Phillips 2016 JPE + Hoberg-Phillips-Prabhala 2014 JF + 谢佳松 2025 经济研究): **多文本表征方法** (TF-IDF char / TF-IDF jieba / LDA+JSD / Embedding / Centroid) 测度银行金融科技战略差异度, 检验 N-邻 (N=3..7) 敏感性、与产品市场流动性的关系、SOE 异质性、Bartik IV 因果识别.

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.features.strategic_diff` | ~ | 计算 `strat_diff_n{3..7}` / `strat_fluidity` / `centroid_diff_*` 等 |
| `news_process.papers.strategic_diff.analysis` | 68 | CLI 入口 |
| `news_process.papers.strategic_diff.tables` | 88 | Table 1-5 (描述 + 主回归 + Bartik IV + SOE 异质性 + N/方法/Ctx 稳健性) |
| `news_process.papers.strategic_diff.figures` | 91 | Figure 1 (n5 分布) + Figure 2 (main coefplot) + Figure 3 (N-sens coefplot) |

## 资产目录约定

```
papers_assets/strategic_diff/
├── README.md          ← 本文件
├── do/                ← Stata
│   ├── strategic_differentiation.do   ← 268 行 (N-邻 + 方法 + Bartik IV + Centroid + 政策响应)
│   └── text_coherence.do              ← 119 行 (相邻期文本连贯性, 欧阳-胡 2024)
├── output/            ← (gitignored)
└── drafts/
    ├── en/manuscript.tex + refs.bib
    └── zh/manuscript.tex + refs.bib
```

## P0-P4 交付物 (commit 8d33c46)

| 层 | 交付 |
|---|---|
| Stata | 8 .do.tmpl @ `_common/stata_templates/strategic_diff/` + 387 行 paper-specific 2 个 .do (保留) |
| Python | `tables.py` 5 函数 + `figures.py` 3 函数 |
| 复现包 | `python -c "from news_process.papers._common.derivative_replication import build_derivative_replication_package as b; b('strategic_diff')"` |
| Manuscript | en (86 行 / 10 TODO) + zh 双语骨架 + refs.bib |

## 关键变量 (Paper-specific defaults)

- `MAIN_DV`: `tobin_q` (2026-06-13 outcome 重定位: 特许权价值, Hoberg-Phillips 2016 JPE 银行版; 原 ROA 降级 secondary; 仍为外部财务哨兵, 上市行子样本)
- `MAIN_DIFF_VAR`: `strat_diff_n5` (N=5 TF-IDF char 默认)
- `FLUIDITY_VAR`: `strat_fluidity` (Hoberg-Phillips-Prabhala 2014)
- `SIM_MAX_VAR`: `strat_sim_max`
- `BARTIK_IV`: `bartik_type_iv_full` (instrument for `llm_vote_tone_full`)
- `COHERENCE_VAR`: `coh_tfidf_c_full` (text-coherence companion)
- `CLUSTER_VAR`: `bank_id`

## 仍待用户补充

1. Manuscript 实质内容 (10 TODO/lang)
2. ROA 等会计 DV 并入 panel
3. 多方法 (TF-IDF / LDA / Embedding / Centroid) 收敛效度的实证报告
4. Bartik IV 第一阶段 F 与 over-identification 诊断

## 学术依据

- Guzman, J., & Li, A. (2023). Measuring Founding Strategy. *Management Science*, 69(1).
- Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries. *JPE*, 124(5).
- Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product Market Threats, Payouts. *JF*, 69(1).
- Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik Instruments. *AER*, 110(8).
- 谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据与企业创新边界. 经济研究, (11).
- 欧阳志刚, 胡雯华. (2024). 央行沟通公告. 数量经济技术经济研究, 41(10).
