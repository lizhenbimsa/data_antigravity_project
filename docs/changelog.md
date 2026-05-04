# 变更日志

完整变更记录见项目根的 [`CHANGELOG.md`](https://github.com/example/news_process/blob/main/CHANGELOG.md)
（本地文件路径：`<repo_root>/CHANGELOG.md`）。

文档站这里仅做高层 phase summary 速查与 rollback 锚点导航。
完整 commit hash + LOC 净改动 + 子任务说明请翻原始 CHANGELOG。

## 八期重构总览

| Phase | Tag | Commit | 主交付 |
|---|---|---|---|
| **0** | `baseline-pre-restructure` | — | 原始扁平结构基线（前 v2.0） |
| **1** | `phase-1-baseline` | `phase-1-baseline` | `news_process/` 真包 + `core/dag.py` 声明式 DAG + `StageSpec` |
| **2** | `phase-2-baseline` | `phase-2-baseline` | `pipeline/` 子包结构 + `importlib` 反射净化 + `panel/` 拆分 |
| **3** | `phase-3-baseline` | `phase-3-baseline` | `papers/` 多论文产品层 + `_common` 内核 + `papers_assets/` |
| **4** | `phase-4-baseline` | `phase-4-baseline` | 7 域配置拆分（paths/preprocessing/.../validation） + 外部 prompt |
| **5** | `phase-5-baseline` | `d4a89ba` | `pipeline/` + `tests/` `utils.*` 迁移 + README + CHANGELOG |
| **6** | `phase-6-baseline` | `6618dc9` | 根脚本 + orchestrators utils → core 迁移 + `utils/` 退役 |
| **7a** | `phase-7a-baseline` | `bcfea64` | 8 个 pipeline 类 root body → `pipeline/<sub>/` + thin shim |
| **7b** | `phase-7b-baseline` | `a4d8aec` | 13 个 validation 类 root body → `validation/` 扁平包 + thin shim |
| **8** | `phase-8-baseline` | `6c31adf` | `data_processed/` → `data/processed/` 单层重命名（22 GB mv） |
| **v2.0.0** | `v2.0.0` | `f629688` | 收官：version bump + README + CHANGELOG + release tag |

## 关键架构决策（按主题归类）

### 决策 1: 真包化（Phase 1）

**问题**：原项目是扁平 `.py` 文件 + 数字前缀文件名，无 `__init__.py`，
无法 `import news_process.X`。

**决策**：建立 `news_process/__init__.py` 让目录成为真正 Python 包；
`pyproject.toml` 用 `setuptools.packages.find = ["news_process*"]` 做包
发现，明确排除根级数字前缀脚本（它们不是合法 Python identifier）。

### 决策 2: 声明式 DAG（Phase 1）

**问题**：原 orchestrator 用内联 `if-append` 链定义阶段顺序，难测试，
两个 orchestrator 间没有结构化共享。

**决策**：`core/dag.py` 引入 `StageSpec` dataclass，`STAGES_MAIN` /
`STAGES_VALIDATION` 是单源真值；orchestrator 仅消费 `filter_enabled(
STAGES, CONFIG)`。`enabled_when` 谓词是模块级 callable，确保 `is`
identity 跨 import site 成立（DAG consistency test 依赖此）。

### 决策 3: importlib 反射净化（Phase 2）

**问题**：原代码用 `importlib.util.spec_from_file_location("11_news_bank",
"/path/to/11_news_bank.py")` 来 import 数字前缀文件，导致：
* 无法静态分析依赖
* 文件移动后路径硬编码失效
* 类型检查器无法识别

**决策**：所有反射 import 改为规范包 import；数字前缀文件全部 thin shim
化（Phase 7），body 迁入合法 identifier 的子包。

### 决策 4: utils/ 退役（Phase 6）

**问题**：原 `utils/helpers.py` 是巨石模块（1500+ LOC），混合配置加载、
日志、并行、报告等无关职责。

**决策**：拆分为 `core/{config, logging, parallel, reporting, stage,
locking, caching, quality, schemas, text/}` 等单职责模块；保留
`news_process/utils/` 作 forward shim 一段时间（Phase 1-5），最终在
Phase 6b 整目录删除。

### 决策 5: 配置 7 域拆分（Phase 4）

**问题**：单一 `config.yaml` 增长到 1000+ 行，多人编辑冲突频繁；prompt
模板与配置混杂。

**决策**：拆为 `paths/preprocessing/filtering/sentiment/features/panel/
validation.yaml` 7 个文件；prompts 进一步外部化到 `config/prompts/*.txt`；
`load_config()` 自动 deep-merge + prompt 内联，**对所有消费方 API 完全
透明**（这是关键 — 消费方代码零改动）。

### 决策 6: 多论文产品化（Phase 3）

**问题**：研究通常基于同一 pipeline 输出衍生多篇论文（主线 + 多个衍生），
但传统单 `analysis.py` 单 paper 模式无法支持多 paper 并存。

**决策**：`papers/<paper_id>/` 是 Python 代码层；`papers_assets/<paper_id>/`
是非代码资产（Stata `.do`、drafts、output）；`_common/` 是共享 helpers
（PaperConfig、load_panel、publication-style figures、Stata runner）；
`run_paper.py` 是统一 CLI 调度器。

### 决策 7: data 物理布局规范化（Phase 8）

**问题**：原 `data_processed/` 不分组、命名不规范。

**决策**（**修订原计划**）：原计划做 `data/processed/<group>/` 业务组
子分区，但深度审视后撤销 — 跨阶段交叉读取会迫使 `CONFIG['filenames']`
携带组前缀信息，**反向增加耦合**（DRY 违反）。改为最小变动：单层重命名
`data_processed/` → `data/processed/`，子分区作为可选 archival helper
保留。

## Rollback 实操速查

```bash
# 回滚到 phase-N-baseline (例: 回 phase-7a)
git checkout phase-7a-baseline

# 仅回退某次 commit (例: 撤销 Phase 8)
git revert 6c31adf

# 列出所有可用 tag
git tag --list | sort
```

完整 rollback 路径与影响面分析见 [Rollback 锚点指南](reference/rollback_anchors.md)。
