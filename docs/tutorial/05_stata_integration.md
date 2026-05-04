# Stata 集成

`news_process` v2.0 与 Stata 的集成有 3 个层次：

1. **数据层**：`40_panel_yearly.dta` 直接被 Stata `use` 读取
2. **脚本层**：`papers_assets/<paper_id>/do/*.do` 是论文专属回归脚本
3. **调度层**：`StataRunner` 让 Python 脚本编程式调用 `stata.exe`

## 1. 数据层

主面板由阶段 45 (`pipeline.panel.runner.main()`) 同步导出 3 种格式：

| 格式 | 路径 | 用途 |
|---|---|---|
| Parquet | `data/processed/40_panel_yearly.parquet` | Python / R / Julia 读取 |
| CSV | `data/processed/40_panel_yearly.csv` | Excel / 通用导入 |
| **Stata** | `data/processed/40_panel_yearly.dta` | **Stata 直接 use** |

`.dta` 文件含完整的：
* 变量标签（中文，UTF-8）
* 值标签（如 `sentiment: 1 "正面" 2 "中性" 3 "负面"`）
* 字符串列长度自动检测
* `_panel_yearly_export` 元数据签名（导出时间 + version）

`pipeline.panel.export.export_panel()` 调用 `_common.tables.export_dta()`
做最高标准的 Stata 友好导出。

## 2. 脚本层（论文专属 .do）

```bash
# 进入论文 do/ 目录（重要：相对路径要正确解析）
cd news_process/papers_assets/bank_fintech_tone/do/

# Stata 命令行调用
stata -b do 50_robustness_text2vec_stata.do

# 或在 Stata GUI 里：
# . do "50_robustness_text2vec_stata.do"
```

每个 `.do` 顶部有标准 path prelude：

```stata
* path prelude — 自动解析数据 / 输出位置
if "$panel_dta" == "" {
    global panel_dta "../../../data/processed/40_panel_yearly.dta"
}
if "$out_dir" == "" {
    global out_dir "../output"
}

* 现在可以用 $panel_dta / $out_dir 引用，相对路径在 do/ 目录运行时正确
use "$panel_dta", clear
```

```{warning}
**`cwd` 必须是 `do/` 目录** — 否则 `../../../data/processed/...` 解析
错误。在 Stata 里用 `. cd "/abs/path/to/do/"` 切到正确目录。

如果在 IDE 里运行，确保 IDE 的 working directory 设置正确，或在脚本顶部
显式 `cd` 到正确路径。
```

### 5 个内置 .do 文件

| 论文 | .do 文件 | 用途 |
|---|---|---|
| `news_process` | `50_robustness_text2vec_stata.do` | text2vec 替代度量回归 |
| `benefit_society` | `token_hidden_regression.do` | Token / Hidden 四象限回归 |
| `brokerage_network` | `network_causal.do` | 网络中心度因果识别 |
| `strategic_diff` | `strategic_differentiation.do` | 战略差异度主回归 |
| `strategic_diff` | `text_coherence.do` | 文本一致性 robustness |

外加 `papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl`：
被 `pipeline.falsification.controls.print_stata_template()` 加载并打印
为 stage 51 输出的回归 boilerplate。

## 3. 调度层（`StataRunner`）

### 自动检测 Stata 二进制

```python
from news_process.papers._common.stata_runner import StataRunner

runner = StataRunner()
print(runner.stata_path)
# Windows: C:/Program Files/Stata18/StataMP-64.exe (优先 MP > SE > IC)
# Linux/macOS: /usr/local/stata18/stata-mp（环境变量 STATA_PATH 可覆盖）
```

### 跑指定 .do

```python
from pathlib import Path

result = runner.run_do(
    do_path=Path("news_process/papers_assets/bank_fintech_tone/do/50_robustness_text2vec_stata.do"),
    cwd=Path("news_process/papers_assets/bank_fintech_tone/do"),  # 让相对路径解析正确
    timeout=3600,
)

if result.returncode != 0:
    print("Stata error:", result.stderr[:500])
else:
    print("OK, output:", result.stdout[-500:])
```

### 传入 global 变量

```python
result = runner.run_do(
    do_path=...,
    cwd=...,
    globals={
        "panel_dta": "/abs/path/to/custom_panel.dta",  # 覆盖默认 panel
        "out_dir": "/abs/path/to/custom_output",
    },
)
# 等价于在 .do 开头 `global panel_dta "/abs/path/..."` 等
```

## 4. 论文专属命令规范

每个 `.do` 顶部应：

1. **有 path prelude**（已统一为 `$panel_dta` / `$out_dir` 模式）
2. **顶部声明依赖** — 注释列出所需变量
3. **结尾保存输出**到 `$out_dir/tables/` 或 `$out_dir/figures/`
4. **使用 `esttab` 或 `outreg2`** 输出 LaTeX / CSV，避免 Stata 内置的不可重用格式

例：

```stata
* token_hidden_regression.do
* Required variables (from 40_panel_yearly.dta):
*   - bank_id, year (panel index)
*   - llm_tone_full, fintech_intensity_score
*   - log_assets, ROA, NPL_ratio (controls)

if "$panel_dta" == "" {
    global panel_dta "../../../data/processed/40_panel_yearly.dta"
}
if "$out_dir" == "" {
    global out_dir "../output"
}

use "$panel_dta", clear
xtset bank_id year

* Token regression
xtreg llm_tone_full fintech_intensity_score log_assets ROA NPL_ratio, fe robust
estimates store token

* Hidden regression
xtreg llm_tone_ctx fintech_intensity_score log_assets ROA NPL_ratio, fe robust
estimates store hidden

* Output
esttab token hidden using "$out_dir/tables/token_hidden.tex", replace ///
    se star(* 0.10 ** 0.05 *** 0.01) booktabs ///
    title("Token vs Hidden Adoption Regressions") ///
    coeflabels(...) addnotes("Notes: ...")
```

## 5. 测试 Stata 集成

```bash
# 仅在装了 Stata 的机器上有效
.venv/Scripts/python.exe -m pytest news_process/tests/test_papers_common.py -k "stata_runner"
```

## 6. 故障排查

| 症状 | 处理 |
|---|---|
| `StataRunner` 找不到 stata.exe | 设置环境变量 `STATA_PATH=/abs/path/to/stata-mp.exe` |
| `.do` 报 "file not found" | 检查 `cwd` — 必须是 `do/` 目录 |
| `.dta` 无法读取（编码错误） | Stata 16+ 需要 `set rmsg on` + UTF-8 locale |
| 列名 `target_bank_in_title` 太长 | 自动 `sanitize_stata_columns()` 截断到 32 字符 |

## 7. 下一步

* [新增 Paper 指南](../guides/adding_paper.md) — 添加你自己的论文与 .do
* [`StataRunner` API 参考](../api/papers.md)
* [Rollback 锚点](../reference/rollback_anchors.md) — 回滚到任意 phase
