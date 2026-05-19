# `news_process.papers` — 多论文产品层 API

`papers` 是 v2.0 引入的**多研究产品**层，让一套 pipeline 内核同时驱动多篇独立论文。
每个论文产品是 `news_process.papers.<paper_id>` 子包，共享同一个 `_common` 内核，
但可以独立定义 DAG、tables、figures、analysis CLI。

```{eval-rst}
.. autosummary::

   news_process.papers._common
   news_process.papers.bank_fintech_tone
   news_process.papers.bank_fintech_attention
   news_process.papers.bank_fintech_substance
   news_process.papers.bank_fintech_locus
   news_process.papers.bank_fintech_collab
   news_process.papers.benefit_society
   news_process.papers.brokerage_network
   news_process.papers.llm_peer
   news_process.papers.strategic_diff
   news_process.papers.bank_media_disagreement
   news_process.papers.bank_news_clarity
```

## 论文产品速查（v3.7.0：5 Bank-FinTech 主线 + 4 衍生 + 2 立项 = 11 paper）

| paper_id | 主题 | 核心方法 | 状态 |
|---|---|---|---|
| `bank_fintech_tone` | P1 主线：bank-fintech 媒体语调 | LLM 三角验证 + 词典/BERT 对照; v3.6.0 G3 main=`_ctx` | 主线 |
| `bank_fintech_attention` | P2: firm-level fintech attention intensity | Hassan 2019 QJE 框架 | 主线 |
| `bank_fintech_substance` | P3: 实质/象征二元属性 | Westphal & Zajac 1998 ASQ | 主线 |
| `bank_fintech_locus` | P4: 底层/应用二元属性 | Gomber 2018 JMIS | 主线 |
| `bank_fintech_collab` | P5: 自主研发 vs 外部协同 | Chesbrough open innovation；v3.4.0 立项 | 主线 |
| `benefit_society` | 经营态度 → 社会福祉投影 | Jha-Liu-Manela (2026, RFS) embedding | 衍生 |
| `brokerage_network` | 信息经纪网络 | Han et al. (2024) 网络中心度 | 衍生 |
| `llm_peer` | LLM 同业工具变量 | Cao et al. (2025) LLM-IV | 衍生 |
| `strategic_diff` | 战略差异度 | Guzman-Li (2023) + Hoberg-Phillips (2016) | 衍生 |
| `bank_media_disagreement` | 第 10 篇：跨媒体语调分歧 | path B = SSRN + `_full` main; v3.7.0 立项 | 立项 |
| `bank_news_clarity` | 第 11 篇：外部信息环境质量 | path C = No-SSRN + `_ctx` G3 解锁; v3.7.0 立项 | 立项 |

## `_common` 共享内核

| 模块 | 公开 API |
|---|---|
| `paper_config.py` | `PaperConfig`（dataclass） + `get_paper_config()` + `_VALID_PAPER_IDS` |
| `panel_loader.py` | `load_panel()`, `list_available_panels()` |
| `tables.py` | `sanitize_stata_columns()`, `export_dta()`, `summary_stats()` |
| `figures.py` | `apply_publication_style()`, `FIGSIZE_SINGLE/WIDE/SQUARE`, 配色调色板 |
| `stata_runner.py` | 跨平台 Stata `.do` 调用包装 |

## 调用约定（每个 paper 子包）

```text
news_process/papers/<paper_id>/
├── __init__.py                  # 定义 PAPER_ID = "<paper_id>"
├── analysis.py                  # CLI 入口 main()，--list/--stage/--dry-run
│                                # 顶部 STAGES = list(STAGES_MAIN) (Phase 9a)
├── tables.py                    # build_table1() / write_table1() ...
└── figures.py                   # plot_*() 学术级 matplotlib
```

> **Phase 9a 改动**: v2.1 起每个 paper 不再有独立的 ``dag.py`` 子模块,
> ``STAGES`` 直接挂在 ``analysis.py`` 顶部 (``STAGES = list(STAGES_MAIN)``).

通过 `run_paper.py` 调度器统一调用：

```bash
python news_process/run_paper.py bank_fintech_tone     # 主线
python news_process/run_paper.py --list
python news_process/run_paper.py benefit_society --dry-run
```
