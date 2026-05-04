# Rollback 锚点 — 11 个 git tag

`news_process` v2.0 八期重构期间在每个 phase 末打 git tag，提供**单点回滚
颗粒度**。本参考列出全部 11 个 tag、各自的 commit hash、关键变更、以及
回滚的具体场景。

## 1. Tag 链总览

```
baseline-pre-restructure
  ↓
phase-1-baseline   (包结构 + DAG 抽取)
  ↓
phase-2-baseline   (pipeline/ 子包 + 反射净化)
  ↓
phase-3-baseline   (papers/ 多论文层)
  ↓
phase-4-baseline   (config 7 域拆分)
  ↓
phase-5-baseline   (utils/ 引用清理 + 文档化)
  ↓
phase-6-baseline   (utils/ 整目录退役)
  ↓
phase-7a-baseline  (8 pipeline body 迁入)
  ↓
phase-7b-baseline  (13 validation body 迁入)
  ↓
phase-8-baseline   (data 物理布局规范化)
  ↓
v2.0.0             (release tag)
```

每个 tag 都对应一个完整 + 通过 778 pytest 的稳定状态。

## 2. 每个 tag 的关键信息

| Tag | Commit | 跨 LOC | 关键变更 |
|---|---|---|---|
| `baseline-pre-restructure` | (起始) | — | v1.x 原始扁平结构 |
| `phase-1-baseline` | (Phase 1) | ≈ +500 | `news_process/__init__.py` + `core/dag.py` `StageSpec` |
| `phase-2-baseline` | (Phase 2) | ≈ +2000 / -500 | `pipeline/` 子包 + `importlib` 反射净化 + `panel/` 拆分 |
| `phase-3-baseline` | (Phase 3) | ≈ +1500 | `papers/{_common,bank_fintech_tone,...}` + `papers_assets/` |
| `phase-4-baseline` | (Phase 4) | ≈ +0 / -0 (重排) | 7 域 YAML 拆分 + 外部 prompt + 配置 deep-merge |
| `phase-5-baseline` | `d4a89ba` | ≈ +180 / -76 | `pipeline/` + `tests/` `utils.*` 迁移 + README/CHANGELOG |
| `phase-6-baseline` | `6618dc9` | ≈ +279 / -58 | 根脚本 + orchestrator utils → core；`utils/` 整目录退役 |
| `phase-7a-baseline` | `bcfea64` | +5527 / -5397 | 8 pipeline 类 root body → `pipeline/<sub>/` + thin shim |
| `phase-7b-baseline` | `a4d8aec` | +11005 / -10608 | 13 validation 类 root body → `validation/` 扁平 + thin shim |
| `phase-8-baseline` | `6c31adf` | +92 / -59 | `data_processed/` → `data/processed/`（22 GB 物理 mv） |
| `v2.0.0` | `f629688` | +149 / -18 | version bump + README/CHANGELOG + release tag |

## 3. Rollback 场景与命令

### 3a. 完整回到某个 phase（最常见）

```bash
# 例：回到 phase-7a-baseline（撤销 Phase 7b/8/release）
git checkout phase-7a-baseline

# 验证：
git log --oneline -3
.venv/Scripts/python.exe -m pytest news_process/tests/ -q --no-header
```

```{warning}
`git checkout <tag>` 会让你处于 detached HEAD 状态。如果你打算在该 tag
基础上**继续开发**，先创建分支：

    git checkout -b hotfix-from-phase-7a phase-7a-baseline
```

### 3b. 仅撤销某次 commit（保留其他 phase）

```bash
# 例：撤销 Phase 8（保留 Phase 7a/7b/release）
git revert 6c31adf

# 这会创建一个新 commit 反向 Phase 8 的修改
# 不会丢失 Phase 8 之后任何工作
```

### 3c. 局部回滚某个文件

```bash
# 例：撤回某文件到 phase-6-baseline 状态
git checkout phase-6-baseline -- news_process/core/config.py

# 或者撤回某整个目录
git checkout phase-7a-baseline -- news_process/pipeline/
```

### 3d. 比对两个 phase 之间的差异

```bash
# 例：phase-7a 到 phase-7b 之间改了什么
git diff phase-7a-baseline phase-7b-baseline --stat
git diff phase-7a-baseline phase-7b-baseline -- news_process/validation/

# 看完整 commit 列表
git log phase-7a-baseline..phase-7b-baseline --oneline
```

## 4. 已知不可回滚的场景

### 4a. `data_processed/` mv（Phase 8）

`data_processed/` → `data/processed/` 是物理 mv。如果你 `git checkout
phase-7b-baseline` 但**不**手动 mv 数据回去，代码会找不到数据。

**手动恢复**：

```bash
git checkout phase-7b-baseline
mv news_process/data/processed news_process/data_processed
rmdir news_process/data
```

或者**保持数据不动**，只修改 paths.yaml：

```bash
git checkout phase-7b-baseline
# 编辑 news_process/config/paths.yaml
# 把 output_dir: ./data_processed 改回 ./data/processed（保留新位置）
```

### 4b. `utils/` 删除（Phase 6b）

`news_process/utils/` 已物理删除。`git checkout phase-5-baseline` 会
把它**重新创建**（git tracked）。但如果在 phase-6 之后已经基于
`from news_process.core.X` 写了大量新代码，回到 phase-5 会让那些新
import 失败。

**评估方案**：先 `git diff phase-5-baseline HEAD -- news_process/utils/
news_process/core/` 看看影响面，再决定。

### 4c. golden snapshot drift

Phase 8 修改了 `tests/fixtures/golden_panel_v0.json` 中的 `data_dir` 字段
（从 `"data_processed"` 改为 `"data/processed"`）。如果回到 Phase 7b
但 fixture 还是新版本，`test_panel_reproducibility.py` 会从错误目录找
parquet → skip 而不是 fail，但仍是数据不可重现的潜在风险。

`git checkout` 会自动同步 fixture 文件，但要注意：fixture 列 hash 与
**v2.0 实际数据**比对，不是与 phase-7b 时的数据。如果你回到 phase-7b
后又跑了一次新的主流水线，列 hash 可能与 fixture 不一致（伪 fail）。

## 5. CI / 自动化 rollback 检查

```bash
# 一键检查所有 phase tag 是否能 checkout + 跑 pytest
for tag in phase-1-baseline phase-2-baseline phase-3-baseline phase-4-baseline \
           phase-5-baseline phase-6-baseline phase-7a-baseline phase-7b-baseline \
           phase-8-baseline v2.0.0; do
    git checkout "$tag" 2>/dev/null
    echo "=== $tag ==="
    .venv/Scripts/python.exe -m pytest news_process/tests/ -q --no-header --tb=no 2>&1 | tail -1
done
git checkout main  # 切回最新
```

## 6. 见也

* [CHANGELOG](../changelog.md) — 完整 commit 演进史
* [架构总览](../architecture.md) — v2.0 终态架构
* [新增 Stage 指南](../guides/adding_stage.md)
