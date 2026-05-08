# 多论文工作流

`news_process` v2.1 通过 `papers/` + `papers_assets/` + `run_paper.py`
实现"一个 pipeline 内核 + N 篇独立论文"的产品化模式。本教程演示如何
为每篇论文生成专属的 tables / figures / Stata 输出。

## 1. 已有论文产品（5 篇）

| paper_id | 主题 | 主依赖 stage |
|---|---|---|
| `bank_fintech_tone` | 主线：银行金融科技语调 | 21/22/23 → 41 |
| `benefit_society` | 经营态度 → 社会福祉投影 | 27 (embedding) |
| `brokerage_network` | 信息经纪网络 | 47 (network_brokerage) |
| `llm_peer` | LLM 同业工具变量 | 48 (llm_peer_iv) |
| `strategic_diff` | 战略差异度 | 25 (strategic_diff) |

## 2. CLI 调度器

```bash
# 列出所有可用论文
.venv/Scripts/python.exe news_process/run_paper.py --list

# 跑指定论文（生成 tables + figures）
.venv/Scripts/python.exe news_process/run_paper.py bank_fintech_tone

# 仅跑特定 stage（如调试 figure 不重跑回归）
.venv/Scripts/python.exe news_process/run_paper.py benefit_society --stage figures

# Dry-run（仅打印计划，不执行）
.venv/Scripts/python.exe news_process/run_paper.py llm_peer --dry-run
```

## 3. 论文输出位置

每篇论文的产出分两类：

### 3a. 代码层 (`papers/<paper_id>/`)

```
news_process/papers/bank_fintech_tone/
├── __init__.py        # PAPER_ID = "bank_fintech_tone"
├── analysis.py        # main() — CLI 入口
│                      #   顶部 STAGES = list(STAGES_MAIN)  (Phase 9a 契约)
│                      #   调主流水线走 run_main_pipeline() (Phase 9b 桥接)
├── tables.py          # build_table1(), write_table1() ...
└── figures.py         # plot_news_coverage_distribution() ...
```

> **Phase 9a 改动**: v2.1 起每个 paper 不再有独立的 ``dag.py`` 子模块,
> ``STAGES`` 直接挂在 ``analysis.py`` 顶部 (``STAGES = list(STAGES_MAIN)``).
> 详见 [新增 Paper 指南 §4a](../guides/adding_paper.md#4a-stages-拷贝语义).

调用时 `analysis.main()` 内部调用 `tables.write_table1(...)` 和
`figures.plot_*(...)`，把结果写到对应的 `papers_assets/`。

### 3b. 非代码资产 (`papers_assets/<paper_id>/`)

```
news_process/papers_assets/bank_fintech_tone/
├── do/                          # Stata 回归脚本
│   ├── 50_robustness_text2vec_stata.do
│   └── falsification_template.do.tmpl
├── output/                      # 论文表与图（gitignored）
│   ├── tables/
│   │   ├── table1_summary_stats.tex
│   │   └── table1_summary_stats.csv
│   └── figures/
│       └── fig1_news_coverage.pdf
└── drafts/                      # 论文手稿（PDF/docx 默认 gitignored）
    └── manuscript_v1.docx
```

## 4. 共享 `_common` 内核

5 篇论文共用 `news_process.papers._common`：

```python
from news_process.papers._common import (
    PaperConfig,                  # dataclass: paper_id, project_root, panel_dir, ...
    get_paper_config,             # PaperConfig 工厂（自动从 config 读路径）
    load_panel,                   # 加载 40_panel_yearly.parquet
    list_available_panels,        # 列出 data/processed/ 下所有 panel
    sanitize_stata_columns,       # 列名 ASCII-清洗（Stata 兼容）
    export_dta,                   # pandas DataFrame → .dta with metadata
    summary_stats,                # publication-grade summary stats table
    apply_publication_style,      # matplotlib 学术发表样式
    FIGSIZE_SINGLE, FIGSIZE_WIDE, FIGSIZE_SQUARE,
    StataRunner,                  # subprocess 包装，跨平台 Stata .do 调用
)
```

## 5. 编程式使用

不通过 CLI，而是从 Jupyter / 自己的 Python 脚本调用：

```python
from news_process.papers._common import get_paper_config, load_panel, summary_stats
from news_process.papers.bank_fintech_tone import tables, figures

# 1. 加载 paper 配置
cfg = get_paper_config("bank_fintech_tone")
print(cfg.panel_dir)        # → news_process/data/processed
print(cfg.do_dir)           # → news_process/papers_assets/bank_fintech_tone/do
print(cfg.output_dir)       # → news_process/papers_assets/bank_fintech_tone/output

# 2. 加载主面板
panel = load_panel("40_panel_yearly", paper_id="bank_fintech_tone")
print(panel.shape)

# 3. 生成 publication-style summary stats
stats_df = summary_stats(
    panel,
    columns=["llm_tone_full", "fintech_intensity_score", "log_assets"],
    by="bank_id",  # optional: stratified by bank
)

# 4. 跑论文专属 table 1
tables.write_table1(panel, output_dir=cfg.output_dir / "tables")
print((cfg.output_dir / "tables" / "table1_summary_stats.tex").read_text()[:200])
```

## 6. Stata 集成（在 paper 上下文中）

`papers_assets/<paper_id>/do/*.do` 中的硬路径已**自动**指向
`data/processed/`：

```stata
* papers_assets/bank_fintech_tone/do/50_robustness_text2vec_stata.do
if "$panel_dta" == "" {
    global panel_dta "../../../data/processed/40_panel_yearly.dta"
}
if "$out_dir" == "" {
    global out_dir "../output"
}

use "$panel_dta", clear
* ... 回归代码
esttab using "$out_dir/tables/robustness_text2vec.tex", replace ...
```

通过 `StataRunner` 编程式调用：

```python
from news_process.papers._common.stata_runner import StataRunner
runner = StataRunner()  # 自动检测 stata.exe / stata-mp / stata-se
result = runner.run_do(
    cfg.do_dir / "50_robustness_text2vec_stata.do",
    cwd=cfg.do_dir,  # 重要：让 ../../../data/processed/ 相对路径解析正确
)
print(result.returncode, result.stdout[:200])
```

## 7. 跨论文一致性测试

```bash
.venv/Scripts/python.exe -m pytest news_process/tests/integration/test_papers_imports.py
```

* `test_papers_imports`: 验证 5 个 paper 包均可 import 且暴露
  `PAPER_ID` 字符串 + ``analysis.main`` 函数 + ``analysis.STAGES`` 列表
  (Phase 9a: STAGES 守护从原 ``papers.<id>.dag`` 子模块迁至
  ``analysis`` 模块; ``test_papers_dag_consistency.py`` 已在 9a 整删).

## 8. 下一步

* [Stata 集成深度教程](05_stata_integration.md)
* [新增 Paper 指南](../guides/adding_paper.md) — 添加你自己的论文产品
* [`PaperConfig` API 参考](../api/papers.md)
