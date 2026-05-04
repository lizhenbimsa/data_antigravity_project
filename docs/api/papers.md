# `news_process.papers` — 多论文产品层 API

`papers` 是 v2.0 引入的**多研究产品**层，让一套 pipeline 内核同时驱动多篇独立论文。
每个论文产品是 `news_process.papers.<paper_id>` 子包，共享同一个 `_common` 内核，
但可以独立定义 DAG、tables、figures、analysis CLI。

```{eval-rst}
.. autosummary::

   news_process.papers._common
   news_process.papers.bank_fintech_tone
   news_process.papers.benefit_society
   news_process.papers.brokerage_network
   news_process.papers.llm_peer
   news_process.papers.strategic_diff
```

## 论文产品速查

| paper_id | 主题 | 核心方法 | 状态 |
|---|---|---|---|
| `news_process` | 主线：银行金融科技语调 | LLM 三角验证 + 词典/BERT 对照 | 主线 |
| `benefit_society` | 经营态度 → 社会福祉投影 | Jha-Liu-Manela (2026, RFS) embedding | 衍生 |
| `brokerage_network` | 信息经纪网络 | Han et al. (2024) 网络中心度 | 衍生 |
| `llm_peer` | LLM 同业工具变量 | Cao et al. (2025) LLM-IV | 衍生 |
| `strategic_diff` | 战略差异度 | Guzman-Li (2023) + Hoberg-Phillips (2016) | 衍生 |

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
├── dag.py                       # 定义 STAGES（通常 = STAGES_MAIN 子集 / 全集）
├── analysis.py                  # CLI 入口 main()，--list/--stage/--dry-run
├── tables.py                    # build_table1() / write_table1() ...
└── figures.py                   # plot_*() 学术级 matplotlib
```

通过 `run_paper.py` 调度器统一调用：

```bash
python news_process/run_paper.py news_process
python news_process/run_paper.py --list
python news_process/run_paper.py benefit_society --dry-run
```
