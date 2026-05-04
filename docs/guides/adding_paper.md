# 新增 Paper（研究产品）开发指南

本指南演示如何为已有的 pipeline 内核添加一个**新研究论文产品**。
v2.0 的 multi-paper architecture 让一套 pipeline 输出可以同时驱动多篇
独立论文，无需 fork 整个项目。

## 1. 决策树：先确认你需要的是哪种"新增"

```{mermaid}
graph TD
    Q{你想做什么？}
    Q -->|新论文 base 同一面板| Paper[添加新 paper 子包]
    Q -->|新论文 + 新指标 / 新 stage| Stage[先看 adding_stage<br/>再回来这里]
    Q -->|只是新写一组 tables / figures| Lite[直接在已有 paper 加 .py]
```

**本指南**：场景 1（最常见）—— 假设你要写一篇新论文，基于已有
`40_panel_yearly.parquet` 做不同的回归 / table / figure。

## 2. 标准开发流程（8 步）

例：添加一篇关于"AI 监管对银行金融科技投入的影响"的论文，
paper_id = `ai_regulation`。

### Step 1: 创建包目录骨架

```bash
mkdir -p news_process/papers/ai_regulation
mkdir -p news_process/papers_assets/ai_regulation/do
mkdir -p news_process/papers_assets/ai_regulation/output
mkdir -p news_process/papers_assets/ai_regulation/drafts
```

### Step 2: 写 `__init__.py`

```python
# news_process/papers/ai_regulation/__init__.py
"""
news_process.papers.ai_regulation — AI 监管 → 银行金融科技投入

研究主题:
    AI 监管事件（如 EU AI Act 2024、央行 GenAI 指引 2025）对中国 26 家
    上市银行的金融科技投入与披露的影响。

数据基础:
    - 主面板: data/processed/40_panel_yearly.parquet
    - 监管事件清单: news_process/papers_assets/ai_regulation/regulations.json

资产位置:
    - 代码: news_process.papers.ai_regulation.{dag, analysis, tables, figures}
    - .do:  news_process/papers_assets/ai_regulation/do/
    - 表/图: news_process/papers_assets/ai_regulation/output/
"""

PAPER_ID = "ai_regulation"
```

### Step 3: 写 `dag.py`

通常一个新 paper 会消费 `STAGES_MAIN` 全集（即用整条主流水线产出做下游
分析）：

```python
# news_process/papers/ai_regulation/dag.py
"""
news_process.papers.ai_regulation.dag — DAG (paper-level).

用 STAGES_MAIN 全集；如果只需子集，可 STAGES = list(STAGES_MAIN[:N]).
"""

from news_process.core.dag import STAGES_MAIN

# Identity-preserved（test_papers_dag_consistency.py 用 `is` 校验）
STAGES = list(STAGES_MAIN)
```

如果新 paper 仅需主流水线的前 4 个阶段，可以：

```python
STAGES = list(STAGES_MAIN[:4])  # 仍是 identity-preserved 子集
```

### Step 4: 写 `analysis.py` (CLI 入口)

```python
# news_process/papers/ai_regulation/analysis.py
"""
news_process.papers.ai_regulation.analysis — CLI 分析入口.

调用方式:
    python news_process/run_paper.py ai_regulation
    python news_process/run_paper.py ai_regulation --stage figures
    python news_process/run_paper.py ai_regulation --dry-run
"""

import argparse
import sys

from news_process.papers._common import get_paper_config, load_panel
from news_process.papers.ai_regulation import tables, figures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Regulation paper.")
    parser.add_argument("--stage", choices=["tables", "figures", "all"],
                        default="all", help="只跑特定子阶段。")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅打印计划，不写文件。")
    args = parser.parse_args(argv)

    cfg = get_paper_config("ai_regulation")
    panel = load_panel("40_panel_yearly", paper_id="ai_regulation")
    print(f"Loaded panel: {panel.shape}")

    if args.dry_run:
        print(f"[dry-run] would write to {cfg.output_dir}")
        return 0

    if args.stage in ("tables", "all"):
        tables.write_table1(panel, output_dir=cfg.output_dir / "tables")
        tables.write_table2_did(panel, output_dir=cfg.output_dir / "tables")

    if args.stage in ("figures", "all"):
        figures.plot_event_study(panel, output_dir=cfg.output_dir / "figures")

    print(f"Done. Outputs at {cfg.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

### Step 5: 写 `tables.py`

```python
# news_process/papers/ai_regulation/tables.py
"""
news_process.papers.ai_regulation.tables — 论文 tables 生成.
"""

from pathlib import Path
import pandas as pd

from news_process.papers._common import summary_stats, sanitize_stata_columns


def build_table1(panel: pd.DataFrame) -> pd.DataFrame:
    """Table 1: Summary Statistics."""
    return summary_stats(
        panel,
        columns=[
            "llm_tone_full", "fintech_intensity_score",
            "log_assets", "ROA", "NPL_ratio",
            "post_eu_ai_act",  # event-study indicator
        ],
    )


def write_table1(panel: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = build_table1(panel)
    df.to_csv(output_dir / "table1_summary_stats.csv", encoding="utf-8")

    with (output_dir / "table1_summary_stats.tex").open("w", encoding="utf-8") as f:
        f.write(df.to_latex(
            index=False,
            float_format="%.3f",
            caption="Summary Statistics for AI Regulation Sample",
            label="tab:summary_ai_regulation",
        ))


def write_table2_did(panel: pd.DataFrame, output_dir: Path) -> None:
    """Table 2: DID 主回归（如果你想直接在 Python 跑回归）."""
    # ... 用 statsmodels / linearmodels
```

### Step 6: 写 `figures.py`

```python
# news_process/papers/ai_regulation/figures.py
"""
news_process.papers.ai_regulation.figures — 论文 figures 生成.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from news_process.papers._common import (
    apply_publication_style,
    FIGSIZE_WIDE,
)


def plot_event_study(panel: pd.DataFrame, output_dir: Path) -> None:
    apply_publication_style()
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=FIGSIZE_WIDE)
    # ... event study coefficient plot
    ax.axvline(x=2024, linestyle="--", color="gray", label="EU AI Act")
    ax.set_xlabel("Year")
    ax.set_ylabel("Δ Fintech Intensity")
    ax.legend()
    fig.savefig(output_dir / "fig1_event_study.pdf", bbox_inches="tight")
    plt.close(fig)
```

### Step 7: 注册到白名单

编辑 `news_process/papers/_common/paper_config.py`：

```python
_VALID_PAPER_IDS = frozenset({
    "bank_fintech_tone",
    "benefit_society",
    "brokerage_network",
    "llm_peer",
    "strategic_diff",
    "ai_regulation",   # ← 新加
})
```

### Step 8: 跑 + commit

```bash
# Smoke test
.venv/Scripts/python.exe news_process/run_paper.py ai_regulation --dry-run
.venv/Scripts/python.exe news_process/run_paper.py --list   # 应显示 ai_regulation

# 集成测试
.venv/Scripts/python.exe -m pytest \
    news_process/tests/integration/test_papers_imports.py \
    news_process/tests/integration/test_papers_dag_consistency.py -v

# 跑实际产出
.venv/Scripts/python.exe news_process/run_paper.py ai_regulation

# Commit
git add news_process/papers/ai_regulation/ \
        news_process/papers_assets/ai_regulation/ \
        news_process/papers/_common/paper_config.py
git commit -m "feat(papers): add ai_regulation research product"
```

## 3. （可选）Stata 集成

如果论文回归用 Stata：

### 3a. 写 .do 文件

```stata
* news_process/papers_assets/ai_regulation/do/did_main_regression.do
* path prelude
if "$panel_dta" == "" {
    global panel_dta "../../../data/processed/40_panel_yearly.dta"
}
if "$out_dir" == "" {
    global out_dir "../output"
}

use "$panel_dta", clear
xtset bank_id year

* DID 主回归（EU AI Act 2024）
gen post = (year >= 2024)
gen treated = (bank_size_quartile == 4)  // 大行更早响应
gen did = post * treated

xtreg fintech_intensity_score did post treated log_assets ROA NPL_ratio i.year, fe robust
estimates store did_main

esttab did_main using "$out_dir/tables/table3_did_main.tex", replace ///
    title("DID: AI Regulation Effect on Bank Fintech Intensity") ///
    se star(* 0.10 ** 0.05 *** 0.01)
```

### 3b. 在 Python 调用

```python
# 在 analysis.main() 里：
from news_process.papers._common.stata_runner import StataRunner

if args.stage in ("stata", "all"):
    runner = StataRunner()
    runner.run_do(
        do_path=cfg.do_dir / "did_main_regression.do",
        cwd=cfg.do_dir,
    )
```

## 4. 关键约定 ⚠️

### 4a. `STAGES` 必须 identity-preserved

`test_papers_dag_consistency.py` 用 `is` 校验：

```python
# ✗ 错误：列表推导创建新对象
STAGES = [s for s in STAGES_MAIN]

# ✓ 正确：list() 拷贝但元素是同一对象
STAGES = list(STAGES_MAIN)

# ✓ 正确：直接复用
STAGES = STAGES_MAIN

# ✓ 正确：identity-preserved 切片
STAGES = list(STAGES_MAIN[:5])
```

### 4b. 资产 vs 代码隔离

| 项 | 在哪 |
|---|---|
| Python 代码 | `papers/<paper_id>/` |
| Stata `.do` | `papers_assets/<paper_id>/do/` |
| 表 / 图输出 | `papers_assets/<paper_id>/output/`（gitignored） |
| 论文手稿 PDF/docx | `papers_assets/<paper_id>/drafts/`（gitignored） |
| 该论文专属数据（如监管事件清单） | `papers_assets/<paper_id>/<custom>.json` |

`.gitignore` 已配置默认 ignore + 显式白名单 `.do` / `.tex` / `.bib` /
`README.md`。

### 4c. 不要修改 pipeline 输出

新论文应**只读**消费 `data/processed/40_panel_yearly.parquet` 等主流水线
输出。如果需要新指标 / 新数据，那是 [adding_stage](adding_stage.md) 的
范畴，不是新论文范畴。

## 5. DoD 验收

* ✓ `run_paper.py --list` 显示新 paper_id
* ✓ `run_paper.py <new_paper> --dry-run` 不报错
* ✓ `run_paper.py <new_paper>` 生成预期 tables / figures
* ✓ `test_papers_imports` + `test_papers_dag_consistency` 都通过
* ✓ commit 信息含 `feat(papers): add <paper_id>`

## 6. 见也

* [`PaperConfig` API 参考](../api/papers.md)
* [新增 Stage 指南](adding_stage.md)
* [Stata 集成教程](../tutorial/05_stata_integration.md)
