# Paper: `bank_fintech_tone` — Bank-FinTech Media Tone (主线论文)

**Status (2026-05-15 / post-P4 / commit 8d33c46)**: 主线 paper, v3.2.0 完整发布 + post-v3.2.0 multi-paper 扩展. Stata 14 主模板 + 1016 行 falsification template + Python tables/figures (Phase 9b) + en/zh 双语 manuscript 骨架.

## 主题

Bank-FinTech-Tone (Hassan et al. 2019 QJE 方法 + Westphal--Zajac 1994/1998 ASQ + Gomber et al. 2018 JMIS): 用 LLM 三家族真三角验证情感, 度量银行金融科技战略的媒体语调, 检验对银行绩效与战略响应的影响. **三轨化 spec** (locus × subst × sent = 2³ = 8 种 main spec 选项).

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.panel.stata_export` | ~940 | STATA_LABELS 字典 + bank-year panel .dta 导出 |
| `news_process.papers.bank_fintech_tone.analysis` | 99 | CLI 入口 (`--stage pipeline\|tables\|figures\|all`) |
| `news_process.papers.bank_fintech_tone.tables` | 91 | Table 1 (描述统计) |
| `news_process.papers.bank_fintech_tone.figures` | 69 | Figure 1 (核心变量分布) |

## 资产目录约定

```
papers_assets/bank_fintech_tone/
├── README.md          ← 本文件
├── do/                ← Stata .do
│   ├── 50_robustness_text2vec_stata.do   ← 59 行
│   └── falsification_template.do.tmpl    ← 1016 行 (主线 falsification template)
├── output/            ← (gitignored) — runtime mkdir; tables/ figures/ logs/
└── drafts/
    ├── en/manuscript.tex + refs.bib    ← 英文版手稿
    └── zh/manuscript.tex + refs.bib    ← 中文版手稿
```

## P0-P4 交付物 (commit 8d33c46)

| 层 | 交付 |
|---|---|
| Stata | **14 .do.tmpl @ `_common/stata_templates/`** (主线已存在; v3.2.0 M7) + 1016 行 falsification template (论文专属) |
| Python | `tables.py` Table 1 + `figures.py` Figure 1 |
| 复现包 | `python -m news_process.papers._common.stata_runner build-replication --locus lc --subst sf --sent ctx` |
| Manuscript | en (114 行 / 12 TODO) + zh 双语骨架 + refs.bib |

## 仍待用户补充

1. Manuscript 实质内容 (Intro / Lit / Results 等; 当前 12 TODO 占位)
2. ROA / Tobin_Q 等会计变量并入 panel
3. Falsification template (1016 行) 实际渲染 + 跑通

## 学术依据

- Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk. *QJE*, 134(4).
- Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism. *ASQ*, 39(3).
- Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments. *AER*, 110(8).
- Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the FinTech revolution. *JMIS*, 35(1).
