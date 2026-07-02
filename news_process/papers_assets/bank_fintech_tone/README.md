# Paper: `bank_fintech_tone` — Bank-FinTech Media Tone (主线论文)

**Status (历史 P0-P4 快照, 原 2026-05-15 / commit 8d33c46; 计数已刷新至当前态)**: 主线 paper, v3.2.0 完整发布 + post-v3.2.0 multi-paper 扩展. Stata 19 主模板 (主线 root-level; 原 v3.2.0 为 14) + 1874 行 falsification template + Python tables/figures (Phase 9b) + en/zh 双语 manuscript 骨架.

## 主题

Bank-FinTech-Tone (Hassan et al. 2019 QJE 方法 + Westphal--Zajac 1994/1998 ASQ + Gomber et al. 2018 JMIS): 用 LLM 三家族真三角验证情感, 度量银行金融科技战略的媒体语调, 检验对银行绩效与战略响应的影响. **三维 spec** (locus(2) × subst(2) × sent(3, full/ctx/ss) = 12 种 main spec 选项)。

## 与 pipeline 的对应关系

| 子模块 | 行数 | 责任 |
|---|---|---|
| `news_process.pipeline.panel.stata_export` | ~769 | HEURISTIC_LABELS 字典 + bank-year panel .dta 导出 |
| `news_process.papers.bank_fintech_tone.analysis` | 99 | CLI 入口 (`--stage pipeline\|tables\|figures\|all`) |
| `news_process.papers.bank_fintech_tone.tables` | 127 | Table 1 (描述统计) |
| `news_process.papers.bank_fintech_tone.figures` | 86 | Figure 1 (核心变量分布) |

## 资产目录约定

```
papers_assets/bank_fintech_tone/
├── README.md          ← 本文件
├── do/                ← Stata .do
│   ├── 50_robustness_text2vec_stata.do   ← 59 行
│   └── falsification_template.do.tmpl    ← 1874 行 (主线 falsification template)
├── output/            ← (gitignored) — runtime mkdir; tables/ figures/ logs/
└── drafts/
    ├── en/manuscript.tex + refs.bib    ← 英文版手稿
    └── zh/manuscript.tex + refs.bib    ← 中文版手稿
```

## P0-P4 交付物 (commit 8d33c46)

| 层 | 交付 |
|---|---|
| Stata | **20 .do.tmpl @ `_common/stata_templates/`** (主线 root-level; v3.2.0 M7 原 14, 后经 IV 补全/agg-audit/FE-saturation/era-stability 扩至 19, 2026-07-02 +27_tableA12 跨模型 FWER → 20) + 1874 行 falsification template (论文专属) |
| Python | `tables.py` Table 1 + `figures.py` Figure 1 |
| 复现包 | `python -m news_process.papers._common.stata_runner build-replication --locus lc --subst sf --sent ctx` |
| Manuscript | en (114 行 / 12 处 \NoteThis{} 占位) + zh 双语骨架 + refs.bib |

## 仍待用户补充

1. Manuscript 实质内容 (Intro / Lit / Results 等; 当前 12 处 \NoteThis{} 占位)
2. ROA / Tobin_Q 等会计变量并入 panel
3. Falsification template (1874 行) 实际渲染 + 跑通

## 学术依据

- Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk. *QJE*, 134(4).
- Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism. *ASQ*, 39(3).
- Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments. *AER*, 110(8).
- Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the FinTech revolution. *JMIS*, 35(1).
