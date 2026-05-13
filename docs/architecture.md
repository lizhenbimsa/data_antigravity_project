# 架构总览（v2.1.0 / phase-9-baseline）

本页是 `news_process` v2.1.0 包结构、依赖关系与设计决策的**最高层视图**。
为细节实现请进入对应 [API 参考](api/core.md) 或 [开发指南](guides/adding_stage.md)。

## 1. 顶层包结构

```
news_process/
├── __init__.py                # __version__ = "2.0.0"
├── pyproject.toml             # setuptools.packages.find = ["news_process*"]
├── requirements.txt           # 主流水线运行时依赖
├── requirements-docs.txt      # 文档构建依赖（Phase D 新增）
│
├── 23 × thin shim (≤30 LOC each)         # python news_process/NN_xxx.py 历史调用契约
├── run_pipeline_function.py   # 主流水线编排（消费 STAGES_MAIN）
├── run_pipeline_validation.py # 验证流水线编排（消费 STAGES_VALIDATION）
├── run_paper.py               # 多论文 CLI 调度器
│
├── core/                      # 共享内核（v2.0 重构核心）
├── pipeline/                  # 业务流水线（6 子包）
├── validation/                # 验证模块（13 扁平文件）
├── papers/                    # 多论文代码层（5 papers + _common）
├── papers_assets/             # 多论文非代码资产
├── config/                    # 7 域配置 + prompts/
├── data/processed/            # 各阶段输出 (gitignored, 22 GB)
├── data_excel/                # 原始 XLSX 数据 (gitignored)
├── tests/                     # pytest 778 测试套件
├── scripts/                   # CLI 工具 + 迁移辅助 + 审计
└── stata/                     # README only（5 .do 已迁至 papers_assets/）
```

## 2. 三层依赖（自上而下）

```{mermaid}
graph TB
    subgraph "应用层（用户入口）"
        RootShim[23 × thin shim<br/>news_process/NN_xxx.py]
        RunMain[run_pipeline_function.py]
        RunVal[run_pipeline_validation.py]
        RunPaper[run_paper.py]
    end

    subgraph "业务层（v2.0 三大支柱）"
        Pipeline[news_process.pipeline.*]
        Validation[news_process.validation.*]
        Papers[news_process.papers.*]
    end

    subgraph "内核层（v2.0 共享基础）"
        Core[news_process.core.*<br/>config / logging / dag / stage / ...]
    end

    RootShim -->|delegate to| Pipeline
    RootShim -->|delegate to| Validation
    RunMain -->|consumes STAGES_MAIN| Pipeline
    RunVal -->|consumes STAGES_VALIDATION| Validation
    RunPaper -->|loads paper module| Papers

    Pipeline --> Core
    Validation --> Core
    Papers --> Core
    Papers --> Pipeline
```

**严格层依赖**：上层可调用下层，下层不可反向 import 上层。Phase 5/6 迁移
期间专门 grep 验证过反向 import = 0。

## 3. 数据流（流水线视角）

```{mermaid}
graph LR
    Raw[~37 GB XLSX] -->|阶段 00 preprocess| P0[00_preprocessing.parquet<br/>6.9 GB]
    P0 -->|阶段 11 filter| P11[11_bank_news.parquet<br/>2.4 GB]
    P11 -->|阶段 12 filter| P12[12_fintech_news.parquet<br/>674 MB]
    P12 -->|阶段 14 intensity| P14[14_fintech_intensity.parquet<br/>676 MB]
    P14 -->|阶段 15 alignment| P15[15_article_alignment.parquet]
    P15 -->|阶段 21 LLM| P21[21_tone_llms.parquet]
    P15 -.->|阶段 22 词典| P22[22_words_tone.parquet]
    P15 -.->|阶段 23 BERT| P23[23_bert_tone.parquet]
    P21 -->|阶段 24 herd decay| P24[24_herd_decay.parquet]
    P24 -->|阶段 41-48 panel| P40[40_panel_yearly.parquet/dta]
    P40 -->|阶段 51 falsification| P51[51_panel_with_controls.parquet/dta]
    P40 -.->|阶段 52 audit| P52[52_stata_data_audit.csv]
    P40 -.->|阶段 30-39 validation| Reports[eval_reports/]
```

* 实线 = `STAGES_MAIN` 主线（`enabled_when=always_enabled` 默认）
* 虚线 = config-conditional（如 `sentiment_analysis.enabled_methods`
  控制 22/23 启用与否；`validation.*` 各项开关控制验证模块）

完整 stage 清单与谓词见 [`StageSpec` 参考](reference/dag.md)。

## 4. v2.0 关键设计模式

### 4.1 Thin shim 模式（26 处应用）

**问题**：原 root 脚本以 `NN_xxx.py` 命名（数字前缀），无法用合法 Python
identifier import；外部脚本/orchestrator 通过 `subprocess.run([python,
"NN_xxx.py"])` 调用，迁入子包后必须保留这个调用契约。

**方案**：root 文件保留 ≤30 行 thin shim，将 body 全部迁入子包，shim 仅
负责 `sys.path` 注入 + delegate 到子包 `main()`。

```python
# 11_news_bank.py — 23 行 thin shim
"""DEPRECATED CLI shim (Phase 7a-1)."""
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    from news_process.pipeline.filtering.news_bank import main
    main()
```

详见 [Thin shim 设计模式](guides/thin_shim_pattern.md)。

### 4.2 声明式 DAG 模式

**问题**：两个 orchestrator（main + validation）需要执行不同 stage 集合，
原代码用内联 `for method in enabled_methods: stages.append(...)` 链，难
以测试与维护。

**方案**：`StageSpec` dataclass + `enabled_when: Callable[[Config], bool]`
谓词。orchestrator 仅消费 `filter_enabled(STAGES_MAIN, CONFIG)`，无内联
分支。

```python
StageSpec(
    name="阶段21: 统一 LLM 语义精筛",
    script="21_tone_llms.py",
    group="main", kind="sentiment",
    enabled_when=llm_method_enabled,  # cfg → bool
)
```

详见 [DAG 参考](reference/dag.md)。

### 4.3 7 域配置拆分

**问题**：单一 `config.yaml` 增长到 1000+ 行，多人编辑冲突频繁。

**方案**：按业务域拆为 7 个 YAML（paths / preprocessing / filtering /
sentiment / features / panel / validation） + 外部 prompt 模板（`config/
prompts/*.txt`）。`load_config()` 自动 deep-merge + prompt 内联，对消费
方完全透明。

旧的单一 `config.yaml` 现在是 stub，仅含历史兼容说明。

详见 [配置拆分指南](guides/config_split.md)。

### 4.4 多研究产品共享内核

**问题**：基于同一 pipeline 输出可以发表多篇独立论文，但每篇论文有自己
的回归规格、表 1 变量列表、figure 风格。

**方案**：
* `papers/_common/` 提供共享 helpers（`PaperConfig`、`load_panel`、
  publication-style figures、Stata runner）
* `papers/<paper_id>/` 提供论文专属代码（`dag.py`、`analysis.py`、
  `tables.py`、`figures.py`）
* `papers_assets/<paper_id>/` 提供非代码资产（`do/`、`drafts/`、
  `output/`、`README.md`）
* `run_paper.py` 是统一 CLI 调度器，按 `paper_id` 白名单加载并执行

详见 [新增 Paper 指南](guides/adding_paper.md)。

## 5. 测试与质量门禁

| 测试套件 | 数量 | 跑时 | DoD |
|---|---|---|---|
| `tests/` | 772 unit + integration | ~1.2 min | 100% pass, 0 failed |
| Integration: `test_dag_consistency` | 验证 orchestrator-DAG 身份相等 + STAGES_MAIN ↔ OUTPUT_REGISTRY 一致性 (Phase 9d) | < 1s | identity check |
| Integration: `test_panel_reproducibility` | 列级 hash 比对 golden snapshot | < 5s | 0 hash drift |
| Integration: `test_papers_imports` | 验证 5 个 paper 包均可 import + 暴露 PAPER_ID + analysis.STAGES + main (Phase 9a) | < 5s | smoke pass |
| Integration: `test_config_split_equivalence` | 验证 7 域 YAML deep-merge ≡ 单 YAML | < 5s | recursive equal |

跑命令：`.venv/Scripts/python.exe -m pytest news_process/tests/`

## 6. Rollback 锚点链

11 个 git tag 沿八期重构演进顺序：

```
baseline-pre-restructure         # Phase 0 起点
  ↓
phase-1-baseline                 # 包结构骨架 + DAG 抽取
phase-2-baseline                 # 模块化 reflection 净化
phase-3-baseline                 # 多论文产品层
phase-4-baseline                 # 配置 7 域拆分
phase-5-baseline                 # utils/ 引用清理 + README/CHANGELOG
phase-6-baseline                 # utils/ 整目录退役（v2.0 承诺）
phase-7a-baseline                # 8 pipeline body 迁入子包
phase-7b-baseline                # 13 validation body 迁入扁平包
phase-8-baseline                 # data_processed → data/processed
  ↓
v2.0.0                           # release tag (八期重构终态)
  ↓
phase-9c-baseline                # scripts dead code 清扫 (-1180 LOC)
phase-9d-baseline                # OUTPUT_REGISTRY fallback 删除 + 一致性测试
phase-9a-baseline                # papers DAG 空壳清理 + 公开 API 缩减
phase-9b-baseline                # papers 反射 import 净化
phase-9-baseline                 # Phase 9 收官
  ↓
v2.1.0                           # release tag (本版本; post-restructure cleanup)
```

任意子阶段单点 `git revert <hash>` 即可回滚。详见 [Rollback 指南](
reference/rollback_anchors.md)。
