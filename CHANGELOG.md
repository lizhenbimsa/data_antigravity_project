# CHANGELOG — news_process 架构重整记录

按 Phase 演进记录全部架构改动。每个 phase 末打 git tag，单点 `git revert <hash>` 可回滚任意子任务。

格式: 每个 phase 标 (a/b/c/...) 子任务，含 commit hash、LOC 净改动、关键决策。

---

## post-v2.1.0 / HEAD baseline (2026-05-09 截止)

### 测试 baseline 漂移记录 (round 1 ~ round 3 全程)

| 时点 | 来源 | passed / skipped |
|---|---|---|
| v2.1.0 release tag (frozen) | git tag | **772 / 6** |
| post-round 1+2 (recode + 5 feat 子 commit, +10 回归测试) | 中间 HEAD | **782 / 6** |
| post-round 2 P1-5 sidecar 化 (Win SKIP→PASS, +4) | round 2 末 HEAD | **786 / 2** |
| post-round 3 / Plan-r3 P0-P3 17 单元 | round 3 中间 HEAD | **805 / 2** |
| post-recode 审查 (round 3 末段, 修 1 cache 真 bug + 加 3 不变量) | round 3 末 | **808 / 2** |
| post-final recode 审查 (修 1 接口契约 bug + 加 2 不变量) | **当前 HEAD** | **810 / 2** |

> 本轮 (round 3 含两轮 recode 审查) 增量 +24 来源:
>   - P0-2 +2 invariant test (TestStataLabelsInvariant 防 STATA_LABELS dict-key 重复)
>   - P1-4 +2 invariant test (TestEnvExampleCoversYamlPlaceholders 防 .env.example 错位)
>   - P1-8 +12 smoke test (6 个零测 stage × 2 类: import + main-callable)
>   - P3-17 +3 cache key invariant (prompt_version + temperature + SCHEMA_VERSION)
>   - **recode 审查 +3 cache edge-case** (temperature precision .4f→repr / pipe collision / v0 fallback strict)
>   - **final recode +2 cache 边角** (None vs '' / v0+v1 共存优先级)
>
> 两轮 recode 审查共发现 2 个真 bug 并修复:
>
> **Bug 1 (recode 审查)**: P3-17 用 ``f"{temp:.4f}"`` 格式化 temperature 入键,
> 让 ``temperature=1e-30`` 与 ``0.0`` 都格式化为 ``"0.0000"`` → 键碰撞,
> 1e-4 以下精度被静默吞掉.
>   - **修复**: 改用 ``repr(float(temp))`` 获得 Python 浮点 shortest
>     unambiguous representation.
>   - **不变量**: ``test_cache_temperature_precision_no_collision`` 防回归.
>
> **Bug 2 (final recode 审查)**: ``_make_key`` 中 ``str(x) if x is not None
> else ""`` 让 ``model_id=None`` 与 ``model_id=""`` 共用 namespace, 接口契约
> 违反 (生产 yaml 配置永远不传 None, 但作为公开 API 必须严格).
>   - **修复**: 用 null byte (``\\x00<None>\\x00``) 哨兵区分 — null byte
>     不会出现在合法 model_id / prompt 中.
>   - **不变量**: ``test_cache_none_vs_empty_string_no_collision``
>     + ``test_cache_v0_fallback_priority_when_v1_exists`` 防回归.
>
> 任何后续 PR 应以 HEAD baseline (810) 为合并门槛, 不得低于该数.
> 历史 anchor (772 / 782 / 786 / 805 / 808) 仅作回溯参考.

### Plan-r3 P0-P3 17 修复单元记录 (2026-05-09)

| # | 修复单元 | 关键变更 | commit |
|---|---|---|---|
| **P0-1** | yunwu API key 轮换 + git filter-repo 改写 history + force push | 旧 key 从 3 个历史 commit 中清除 (2c529f5/5f1dce4/6d60e21 → 39bfdfe/fc89174/4c9db27); user 已轮换并写新 key 到 .env | history rewrite (无 commit) |
| **P0-2** | STATA_LABELS dedupe + F601 invariant test | export.py 9 dup keys 清零, peer_compete_idx 标签覆盖 silent override 修复 | f9477d6 |
| **P1-3** | baseline 786 → 800 同步 | __init__.py / README / CHANGELOG / quickstart / ci.yml 全部刷至 805 | e9b0d90 |
| **P1-4** | .env.example 重整 + _validate_env_placeholders 校验 | YAML 引用 ${YUNWU_API_KEY} 但 env.example 漏声明的契约错位修复 | 577172f |
| **P1-5** | papers_assets/llm_peer/ 资产目录补齐 | 5 paper 白名单与目录契约一致 | a0d7b8f |
| **P1-6** | 5-paper 成熟度梯度显式化 | README 区分 1 主线 / 3 半成熟 / 1 全骨架 | ddc8ff6 |
| **P1-7** | 5 god function v3.0-split TODO 锚点 | runner.py:main 1325 行等加 ``.. todo:: v3.0-split`` 锚点 | f2d8cfd |
| **P1-8** | 6 个零测 stage smoke test | test_stage_smoke.py +12 test (import + main-callable) | 6be5edb |
| **P2-11** | core/caching + core/quality 头部 docstring | utils/llm_cache.py / data_quality.py 旧名修正 | ec632e0 |
| **P2-12** | rapidfuzz 优先 + requirements.lock 生成 | thefuzz fallback + 67 transitive deps 锁定 | 78fcb62 |
| **P2-13** | ruff pyproject 接入 + 4 类高风险 lint 修复 | F601 / B023 / F811 / B033 全清零, CI 双层 lint (advisory + blocking) | f856853 |
| **P2-14** | 13 处 swallow except 文档化 | docs/guides/exception_handling.md 集中索引 + 不变量 | 62d7b00 |
| **P3-15** | Makefile + cleanup.py 数据生命周期工具 | _cache 8472 MiB / _backup 98 MiB / 14+ derived 480 MiB 可一键清理 | eb6c4f1 |
| **P3-16** | 4 god function docstring backfill | threshold/media_diversity/tone_validation 缺 docstring 函数从 4 → 0 | 7d4b672 |
| **P3-17** | LLM cache key 加 SCHEMA_VERSION + prompt_version + temperature (BREAKING) | 防 silent staleness; v0→v1 read fallback 让历史 cache 仍能被新代码读 | f3a0000, 426e57c |
| **P3-18** | 26 thin shim v3.0 退役 plan 文档化 | thin_shim_pattern.md §11 含 4 步退役 path + 26 shim 替换映射表 | 223ab3b |

### round 1+2 5 个 feat/recode 子 commit (2026-05-08)

- `fb89495` docs(news_process): Phase 9 recode — fix 5 docstring/doc inconsistencies
- `119bfef` feat(schemas): add `EXPECTED_NO_OUTPUT_STAGES`; orchestrator raises on truly missing entries
- `edcc750` refactor(dag): move method→predicate map into dag.py; orchestrator drops local copy
- `8115f54` fix(recode): tighten registry invariants and config type checks
- `f0b93ca` fix(recode round 2): add 2 missing invariants for cross-stage uniqueness

### Plan P0/P1/P2 修复记录 (2026-05-09)

依据独立 plan 文件 `news_process_缺陷修复路线` (`.cursor/plans/`), 完成 12 个独立工作单元中的 P0/P1/P2 + P3 命名层修正部分:

| # | 修复单元 | 范围 |
|---|---|---|
| P0-1 | `_load_dotenv` fallback 支持 `${VAR}` 嵌套展开 + 行内注释剥离 | [`core/config.py`](news_process/core/config.py) |
| P0-2 | finbert2 模型路径外部化为 `${FINBERT2_MODEL_DIR}` env var; 删除代码内 80 行硬编码 fallback (双源真值) | [`config/sentiment.yaml`](news_process/config/sentiment.yaml), [`pipeline/sentiment/tone_berts.py`](news_process/pipeline/sentiment/tone_berts.py), [`.env.example`](news_process/.env.example) |
| P0-3 | 测试 baseline 数 772 → 786, 多处文档同步 (含历史 anchor 保留) | README, CHANGELOG, `__init__.py` |
| P1-4 | stage 24 加 `enabled_when=berts_method_enabled` 谓词; 撤销 stage 24 的"无条件预清理"特例 | [`core/dag.py`](news_process/core/dag.py), [`run_pipeline_function.py`](news_process/run_pipeline_function.py), `tests/integration/test_dag_consistency.py` |
| P1-5 | PipelineLock sidecar 化: PID/启动时间存独立 `.pipeline.lock.info`, 跨平台 (Win/Unix) 一致可读; 6 个 SKIP → 2 个 (剩余为平台天然差异) | [`core/locking.py`](news_process/core/locking.py), `tests/test_pipeline_lock*.py` |
| P1-6 | stage 45 StageSpec.name 显式列出 41+42+43+44+46+47 子步执行顺序 | [`core/dag.py`](news_process/core/dag.py) |
| P2-7 | `tests/test_39_prompt_sensitivity.py` 改用 pytest `tmp_path` fixture, 消除 `.test_tmp/` 累积 (历史累积 56 个 UUID) | `tests/test_39_prompt_sensitivity.py` |
| P2-8 | `requirements.txt` 内容迁入 `pyproject.toml [project] dependencies`; `transformers <6 → <5`, `pyarrow <24 → <22`, `psutil <8 → <7` | [`pyproject.toml`](news_process/pyproject.toml), [`requirements.txt`](news_process/requirements.txt) |
| P2-9 | 新增 GitHub Actions CI: ubuntu+windows × py 3.11+3.13 矩阵, baseline 锁定 786 | [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| P2-10 | 新增 [`docs/guides/data_lifecycle.md`](docs/guides/data_lifecycle.md): 阐明 `data/processed/_backup_*` (99MB) 与 `data_excel/back/` (43GB) 的保留与清理策略 | docs/guides/, README §6.5 |
| P2-11 | CHANGELOG.md v2.0.0 章节顶部补登 2 段 BREAKING CHANGES (`data_processed/` 重命名 + 真包化) | CHANGELOG.md |
| P3-12 (部分) | papers/bank_fintech_tone logger 名 + docstring CLI 示例修正; pyproject NOTE 时态修正 | `papers/bank_fintech_tone/analysis.py`, `pyproject.toml` |

#### 净基线变化

| 指标 | 修复前 (HEAD) | 修复后 (本批 commit) |
|------|--------------|---------------------|
| pytest passed | 782 | **786** (+4 来自 P1-5 sidecar 让 4 个 Win SKIP 转 PASS) |
| pytest skipped | 6 | **2** (-4, 同上) |
| pytest failed | 0 | 0 |

#### 仍 deferred 至 v3.0 的项目

- **26 个数字前缀 thin shim 完整退役**: 删 26 个 ≤30 行 shim, `core/dag.py:StageSpec.script` 从文件名 (`"00_preprocessing.py"`) 改为 module path (`"news_process.pipeline.preprocess.runner"`), `core/stage.py:run_stage` 改用 `subprocess.Popen([python, "-m", module])`. 工程量大且涉及外部 ``python NN_xxx.py`` 调用契约破坏, 与 v2.x 释出不兼容. 详见 [`docs/guides/thin_shim_pattern.md`](docs/guides/thin_shim_pattern.md).
- **stage 45 panel runner 真拆分** (Plan P1-6 选项 B): 把单文件 7-step 编排拆为 41/42/43/44/46/47/45 七个独立 stage; OUTPUT_REGISTRY 同步重整. 这能让 `enabled_methods` 配置矩阵真正可用 (当前任何不含 `tone_berts` 的组合仍会在 stage 45 因输入缺失崩溃, 见 [`core/dag.py`](news_process/core/dag.py) StageSpec 注释).
- **LLM cache key 维度扩展** (Plan #14, 已降级): 把 `temperature` / `force_json` / `top_p` 等非 prompt 参数也纳入 cache key. 当前生产配置下这些参数恒定, 不出问题; 仅在未来引入参数 sweep 实验时需要.

---

## v2.1.0 / phase-9-baseline (2026-05-08, current HEAD)

### v2.1.0 总目标
清理 Phase 3 / Phase 7a 之后的架构遗留物 — papers DAG 空壳、papers 反射 import (生产代码)、scripts dead code、orchestrator OUTPUT_REGISTRY 兜底 dict. 不引入新抽象, 不动 26 个 thin shim (留待真正 v3.0).

公开 API 缩减: `news_process.papers.<id>.dag` 子模块取消 (5 paper × 1 处复制, 0 外部消费者). 等价路径: `from news_process.core.dag import STAGES_MAIN`. v2.1 minor bump 是对外契约改变信号.

### Phase 9c (`fcdb6ad`) — scripts dead code 清扫 (-1180 / +10 LOC)
5 个 audit/test 脚本经静态分析全部 broken:
- `_test_network_functions.py` / `_test_integration.py` / `_test_final_round.py`: 加载 Phase 2a 已删的 root 文件 (43/46/47_*.py); 部分含硬编码 Windows 绝对路径
- `final_integrity.py` / `audit_changes.py`: grep Phase 7a 后已 thin shim 化的源码内容 (LLMCache/cache.close()/finally/pairwise_distances 等字符串), 在 21 行 shim 内 0 命中
- 保留 `audit_deep.py` (canonical core API 仍有效) 与 `_replan_v5_evidence/` (历史归档)
- 附带清理: `scripts/audit/__init__.py` docstring 反映现状; `scripts/build_city_coordinates.py:88-90` 注释悬挂引用

pytest: 787 → 787 (5 文件不在 `testpaths=['tests']` 收集范围, 数不变).

### Phase 9d (`5f768f0`) — orchestrator OUTPUT_REGISTRY fallback 删除 (-32 / +30 LOC)
`run_pipeline_function._get_stage_output_files` 历史兜底 dict (Phase 2d 弃用期安全网) 删除. 自 Phase 2d 起 OUTPUT_REGISTRY 是单一真值, fallback 属 'never reached' 代码; 删除强制让任何新增 stage 必须在 schemas.py 登记, 否则陈旧文件预清理静默失效.

新增 `test_stages_main_all_registered_in_output_registry` 守护 STAGES_MAIN ↔ OUTPUT_REGISTRY 一致性 (放 `tests/integration/test_dag_consistency.py` 与现有 DAG 一致性测试同位, 与 `test_main_orchestrator_uses_canonical_stages` 一起构成 DAG ↔ orchestrator ↔ schemas registry 三角不变式).

静态 cross-check: 12 个 STAGES_MAIN scripts 全部已在 OUTPUT_REGISTRY 登记, 新测试当前 PASS.

pytest: 787 → 788 (+1).

### Phase 9a (`69ee2de`) — papers DAG 空壳清理 (-234 / +71 LOC, -16 tests)
5 个 `papers/<id>/dag.py` 自 Phase 3c-3d 起就是 `STAGES = list(STAGES_MAIN)` 的 5 处复制. 没有任何 paper 真的需要切片 (Phase 3d 留的扩展点未实现), 而 `test_papers_dag_consistency.py` 用 16 个测试守护 '5 个空壳必须 == STAGES_MAIN' — 即 16 个测试守护 0 个差异.

变更:
- 删 5 个 `papers/<id>/dag.py`
- 删 `test_papers_dag_consistency.py` 整文件 (16 tests)
- 5 个 `papers/<id>/analysis.py`: 改 import + 加 `STAGES = list(STAGES_MAIN)`
- 5 个 `papers/<id>/__init__.py`: 删 `from . import dag` + 从 `__all__` 移除 `'dag'`
- `test_papers_imports.py`: 删 `assert hasattr(mod, 'dag')`; 把 `test_paper_dag_module_has_stages` 重命名为 `test_paper_analysis_has_stages_list`, STAGES 守护转移到 analysis 模块 (而非简单删除 — 失去的不变式不应同时失去守护)
- `docs/guides/adding_paper.md` Step 3 / Step 8 / §4a / §5 DoD 同步重写

公开 API 缩减: `news_process.papers.<id>.dag` 子模块取消, 等价路径 `from news_process.core.dag import STAGES_MAIN`. 项目内 5 处消费者全部纳入本 commit; 项目外无已知消费者 (无 PyPI 发布, 无 install 历史).

pytest: 788 → 772 (-16, 仅整删 `test_papers_dag_consistency.py`; v3 计划预期 -21 含 `test_paper_dag_module_has_stages` 删 5, 实际改为重命名 + 转移守护 = -16).

Smoke: 5 个 paper `run_paper.py <id> --dry-run` 全部 exit 0 + DAG length: 12 stages.

### Phase 9b (`9d003c6`) — papers 反射 import 净化 (-104 / +44 LOC)
5 个 paper `analysis.py` 中复制 5 份的 `_run_pipeline_via_existing_orchestrator()` 反射加载块 (Phase 3e 引入) 违反了 Phase 2a (commit `722bc0e`) 的 reflection-purge 不变式 (限生产代码). v2.0 起 `news_process` 是真包 (`pyproject.toml` `setuptools.packages.find`), 可走规范包导入 — 'run_pipeline_function 不是 package 一部分' 的 v1.x 历史理由已不成立.

变更:
- 新增 `papers/_common/pipeline_runner.py`: `run_main_pipeline()` 函数体内延迟 import `news_process.run_pipeline_function` (保持原反射设计的 '`--stage tables/figures` import-time 隔离' 意图)
- 5 个 paper `analysis.py`: 删 `_run_pipeline_via_existing_orchestrator()` 函数 (5×~17 LOC) + 改调用点 → `run_main_pipeline()` + import 行加 `run_main_pipeline`
- `bank_fintech_tone/analysis.py`: 顶层 unused `from pathlib import Path` 删除
- `_common/__init__.py`: 加 `from .pipeline_runner import run_main_pipeline` + `__all__` 加 `'run_main_pipeline'`

不变式验证:
- `_run_pipeline_via_existing_orchestrator` grep: 仅余 `pipeline_runner.py` docstring 历史性提及
- `_bft_/_bs_/_sd_/_lp_/_bn_run_pipeline_module` grep: 0 匹配
- `spec_from_file_location` in `news_process/papers/`: 仅余 `pipeline_runner.py` docstring 注释 (生产代码 0 反射调用)
- `spec_from_file_location` in `tests/integration/test_dag_consistency.py:37` 保留 (v1.7 测试有意隔离设计, 不在本子任务范围)

pytest: 772 (不变, 当时为 v2.1.0 release tag baseline; HEAD 当前 baseline = 800, 见顶部漂移表).

### v2.1.0 收官 (本 commit)
- `news_process/__init__.py`: `__version__ = "2.1.0"` + docstring 加 v2.1 状态段
- `news_process/pyproject.toml`: `version = "2.1.0"`, description = `(v2.1.0 / phase-9-baseline)`
- `news_process/requirements-docs.txt`: 注释版本号同步
- 本 CHANGELOG + `docs/changelog.md` 同步
- Tag chain: `phase-9c-baseline` → `phase-9d-baseline` → `phase-9a-baseline` → `phase-9b-baseline` → `phase-9-baseline` → `v2.1.0`

### v2.1.0 验收
- pytest `news_process/tests/` → **772 passed / 6 skipped / 0 failed** (v2.0.0 后 HEAD 实测 baseline 787 + 1 [9d 新增 test_stages_main_all_registered_in_output_registry] - 16 [9a 删 test_papers_dag_consistency.py 整文件] = 772; CHANGELOG v2.0.0 章节历史记录的 778 比当前 HEAD baseline 少 9, 因 v2.0.0 release 后又落了 3 个 fix commit 各自带新测试)
- 反射 import 全 papers/ 生产代码零结果 (恢复 Phase 2a 不变式)
- 所有 5 个 paper `python -m news_process.run_paper <id> --dry-run` 返回 0
- `python -m news_process.run_paper --list` 输出 5 个 paper

### v2.1.0 累计净改动
~ -1430 LOC (主要来自 9c 删 5 broken scripts -1180); 净增加 1 测试用例 - 16 删除 = -15 (在 v2.0.0 baseline 778 基础上 = 763; 但 HEAD 是 v2.0.0 + 3 fix commits = 787, 故实际从 HEAD 视角是 -15).

---

## v2.0.0 / phase-8-baseline (2026-05-04)

### ⚠ BREAKING CHANGES (Plan P2-11 补登, 2026-05-09)

> v2.0.0 release 当时仅在 §7 Phase 8 末尾用一句话提及"项目外 Stata 用户脚本中硬编码 `data_processed/...` 的需要搜索替换", 没有专门的 BREAKING CHANGES 段, 外部用户极易错过. 本段为补登, 让从 v1.x 升级或外部分支用户首次升级时能从 CHANGELOG 顶部看到破坏性变更提示.

#### 1. 数据目录物理重命名: `data_processed/` → `data/processed/`

**影响面**:
- 任何在 `data_processed/` 路径下硬编码读写的 *项目外* 脚本 (Stata `.do`、外部 Python 分析、Jupyter notebook 等)
- 项目内 5 个 Stata `.do` 已在本 release 内同步修复, 见 §Phase 8 详情

**迁移步骤** (项目外用户必读):

```bash
# 1. 物理移动数据 (如果你 fork 的旧仓库还在用 data_processed/)
mv news_process/data_processed news_process/data/processed

# 2. 搜索替换硬编码路径 (.do 文件)
sed -i 's|data_processed/|data/processed/|g' your_scripts/*.do

# 3. 搜索替换硬编码路径 (.py 文件)
grep -rn 'data_processed' your_external_scripts/
# 人工确认后再 sed -i

# 4. 校验
python -c "from news_process.core.config import load_config; print(load_config()['paths']['output_dir'])"
# 期望输出: <project_root>/news_process/data/processed
```

**为何破坏**: Phase 4f/5b/6e 蓝图原本规划"业务组子分区"(`data/processed/00_preprocess/` 等), 但因 stage 间交叉读取会迫使 `CONFIG['filenames']` 携带组前缀 (违反 DRY) 而撤销, 最终选定单层重命名方案. 此举属"长痛不如短痛", 让物理布局与项目内部"`paths.output_dir = ./data/processed`"约定一致.

#### 2. `news_process` 真包化与 `python NN_xxx.py` 调用契约保留

**v2.0.0 之前** (v1.x):
- `news_process/` 不是真 Python 包 (无 `__init__.py` 真实导出)
- 26 个 `NN_xxx.py` (00_preprocessing.py ... 53_export_stats_excel.py) 是 fully-bodied 业务脚本
- 调用方式: `python news_process/00_preprocessing.py` (cwd 必须是项目父目录, 或脚本顶部 sys.path 注入)

**v2.0.0 之后**:
- `news_process/` 是真 Python 包 (`pyproject.toml` `setuptools.packages.find = ["news_process*"]`)
- 26 个 root 脚本退化为 ≤30 行的 thin shim, body 已迁入 `news_process.pipeline.*` / `news_process.validation.*`
- **`python news_process/00_preprocessing.py` 仍可用** (历史调用契约保留)
- 推荐调用方式: `python -m news_process.pipeline.preprocess.runner` (规范包路径)

**影响面**:
- 任何 `from news_process import <legacy_name>` 直接导入根级文件内函数的代码 (历史从未推荐, 但理论可能存在)
- `run_pipeline_function` 等编排器从 `subprocess.Popen([python, "NN_xxx.py"])` 改为内部消费 `core.dag.STAGES_MAIN` 后再 spawn (子进程契约不变, 但内部 spec 来源变化)

**迁移成本**: 0, 除非你直接 import 了根级文件内的私有函数 (此种代码理论上违反封装, 修法是改 import 子包内规范路径).

---

### v2.0.0 总目标
完成八期重构 (Phase 0 → 8) 的全终态：26 个根级数字前缀脚本全部统一为 thin shim；`news_process/{core, pipeline, papers, validation, scripts, config}` 形成完整 canonical 包结构；data 物理布局规范化；版本号正式 bump 到 v2.0.0。

### Phase 7a (`bcfea64`) — 8 pipeline 类 root body 迁入子包 (+5,527 / -5,397 LOC)
- **目标**: 把 8 个 pipeline 业务的 fully-bodied root scripts 的 body 迁入对应 `news_process.pipeline.*` 子包，root 文件变 thin shim (~23 行)，保留 `python NN_xxx.py` subprocess 调用契约。
- **迁移列表 (5,441 LOC body)**:
  - `11_news_bank.py` (445L)              → `pipeline/filtering/news_bank.py`
  - `12_news_fintech.py` (356L)           → `pipeline/filtering/news_fintech.py`
  - `14_fintech_intensity.py` (444L)      → `pipeline/filtering/fintech_intensity.py`
  - `21_tone_llms.py` (1036L)             → `pipeline/sentiment/tone_llms.py`
  - `22_tone_words.py` (1168L)            → `pipeline/sentiment/tone_words.py`
  - `23_tone_berts.py` (818L)             → `pipeline/sentiment/tone_berts.py`
  - `24_herd_decay_processor.py` (278L)   → `pipeline/sentiment/herd_decay.py`
  - `52_stata_data_audit.py` (896L)       → `pipeline/audit/stata_audit.py`
- **关键修复**:
  - 子包内 `sys.path` 注入路径深度从 root 的 1 级升级为 3 级 (`os.path.dirname × 3`)。
  - `36/39` 内部 `import_module('21_tone_llms')` 改为 `'news_process.pipeline.sentiment.tone_llms'` 以让 thin shim 化后内部函数仍可解析。
  - 5 个测试文件 (test_11/12/22/23/24) 的 `importlib.import_module(...)` / `spec_from_file_location(...)` 加载 fixture 改为规范包 import。
- **验收**: 778 passed / 7 skipped / 0 failed (与 phase-6-baseline 完全持平).

### Phase 7b (`a4d8aec`) — 13 validation 类 root body 迁入扁平包 (+11,005 / -10,608 LOC)
- **目标**: 把 13 个 validation 业务的 fully-bodied root scripts 的 body 迁入 `news_process/validation/` 扁平布局，原 placeholder 包正式填实。
- **迁移列表 (10,734 LOC body)**:
  - `30_robustness_text2vec.py` (240L)        → `validation/text2vec.py`
  - `31_bank_fintech_threshold.py` (644L)     → `validation/threshold.py`
  - `32_news_llms_human.py` (298L)            → `validation/llms_human.py`
  - `32a_dedup_threshold_sensitivity.py`(193L)→ `validation/dedup_threshold.py`
  - `33_news_llms_evaluation.py` (1502L)      → `validation/llms_evaluation.py`
  - `34_tone_validation.py` (1893L)           → `validation/tone_validation.py`
  - `35_radius_sensitivity.py` (1047L)        → `validation/radius_sensitivity.py`
  - `36_entity_masking_test.py` (674L)        → `validation/entity_masking.py`
  - `37_dict_coverage_audit.py` (993L)        → `validation/dict_coverage.py`
  - `38_media_diversity.py` (1251L)           → `validation/media_diversity.py`
  - `38a_temporal_mask_test.py` (194L)        → `validation/temporal_mask.py`
  - `38b_decay_sensitivity.py` (779L)         → `validation/decay_sensitivity.py`
  - `39_prompt_sensitivity.py` (1000L)        → `validation/prompt_sensitivity.py`
- **关键决策**: 选择**扁平**布局 (`validation/<name>.py`) 而非按风格再分子包 (`validation/sensitivity/`, `validation/comparison/`...)，因为 12 个验证模块彼此独立、关系平行，扁平更符合 Occam's Razor。
- **关键修复**:
  - `entity_masking.py` / `prompt_sensitivity.py` 内 `import_module('33_news_llms_evaluation')` → `'news_process.validation.llms_evaluation'`。
  - 6 个测试文件 (test_32/33/35/37/38b/39) fixture 修复。
  - 临时迁移辅助脚本 `_phase7b_fix.py` 用完即删。
- **验收**: 778 passed / 7 skipped / 0 failed.

### Phase 8 (`6c31adf`) — `data_processed/` → `data/processed/` 物理重命名 (+92 / -59 LOC)
- **目标**: 顶层数据目录重命名为更规范的层级形式。
- **关键决策（修订原计划）**: 原 Phase 4f/5b/6e 蓝图要求的「业务组子分区」(`data/processed/00_preprocess/`, `10_filter/`, `20_sentiment/`, `40_panel/`, `50_falsification/`, `validation/`) 经审视后**主动撤销**。理由: 跨阶段交叉读取 (stage 21 读 stage 14 输出, stage 24 读 stage 23 输出, stage 51 读 stage 40 输出, stage 32a 读 stage 21 输出) 会迫使 `CONFIG['filenames']` 携带组前缀信息，反向**增加耦合** (DRY 违反)。扁平布局保留原有 `NN_xxx` 文件名前缀纪律，已用最经济方式编码业务组。
- **物理迁移**: 22 GB / 56 文件，同卷 `mv` 原子操作 2.5 秒完成。
- **代码改动 (12 处功能性 + ~15 处文档同步)**:
  - `news_process/config/paths.yaml`: `output_dir: ./data_processed` → `./data/processed`。
  - `news_process/.gitignore`: `news_process/data_processed/` → `news_process/data/`。
  - 5 个 Stata `.do` 文件 path prelude 硬路径统一替换。
  - `tests/fixtures/golden_panel_v0.json` 中 `data_dir` 字段更新（列 hash 不受路径影响，无需重建 fixture）。
  - 4 个测试/脚本中的 path 解析 (test_panel_reproducibility, test_dual_track, generate_golden_snapshot, extract_papers)。
  - `papers/_common/paper_config.py:get_paper_config()` 默认 fallback 路径更新。
  - `migrate_data_layout.py` 头部加入 Phase 8 status notes，并把 src_dir 从 `data_processed/` 切到 `data/processed/`（变成对未来任意子分区的辅助脚本）。
- **验收**: pytest 778 / 7 / 0；config 加载 `output_dir` 解析到 `.../news_process/data/processed`，目录可达；golden snapshot 列 hash 测试照常通过。
- **外部影响**: 项目外 Stata 用户脚本中硬编码 `data_processed/...` 的需要搜索替换。

### v2.0.0 收官 (本 commit)
- `news_process/__init__.py`: `__version__ = "2.0.0"`，docstring 改写为 v2.0 终态描述。
- `news_process/pyproject.toml`: `version = "2.0.0"`, description = `(v2.0.0 / phase-8-baseline)`。
- README + 本 CHANGELOG 同步。
- Tag chain (8 个 baseline + 1 个 release):
  - `baseline-pre-restructure` (Phase 0 起点)
  - `phase-1-baseline`, `phase-2-baseline`, `phase-3-baseline`, `phase-4-baseline`,
    `phase-5-baseline`, `phase-6-baseline`, `phase-7a-baseline`, `phase-7b-baseline`,
    `phase-8-baseline`
  - `v2.0.0` (本次 release tag)

### v2.0.0 终态架构
```
news_process/
├── __init__.py (v2.0.0)
├── pyproject.toml
├── 26 × thin shim (≤30 LOC each)         # python NN_xxx.py 历史调用契约保留
├── run_paper.py                            # 多论文 CLI 调度器
├── run_pipeline_function.py                # 主流水线编排器
├── run_pipeline_validation.py              # 验证模块编排器
├── core/                                   # 共享内核 (config, logging, dag, schemas, ...)
├── pipeline/                               # 业务流水线
│   ├── preprocess/   (load, normalize, filter, dedup, runner, _constants)
│   ├── filtering/    (news_bank, news_fintech, fintech_intensity, policy_alignment)
│   ├── sentiment/    (tone_llms, tone_words, tone_berts, herd_decay)
│   ├── features/     (benefit_society, strategic_diff, policy_similarity)
│   ├── panel/        (encode, attention_media, geography, iv_did, network_*, llm_peer_iv, runner, export)
│   ├── falsification/(controls)
│   └── audit/        (stats_excel, stata_audit)
├── validation/                             # 验证模块 (扁平 13 文件)
├── papers/                                 # 多论文代码 (5 papers + _common)
├── papers_assets/                          # 多论文非代码资产 (do/, drafts/, output/, ...)
├── config/                                 # 7 域 YAML + prompts/
├── data/processed/                         # 各阶段输出 (gitignored, 22 GB)
├── data_excel/                             # 原始数据 (gitignored)
├── tests/                                  # pytest 778 测试套件
├── scripts/                                # CLI 工具与迁移辅助
└── stata/                                  # README only (5 .do 已迁至 papers_assets/)
```

---

## phase-6-baseline (2026-05-04)

### Phase 6 总目标
完成 v2.0 utils/ 退役承诺：21 个根级 fully-bodied 脚本 + 2 个 orchestrator + 4 个 audit/legacy 助手统一迁移到 `news_process.core.*` canonical 路径；`news_process/utils/` 整目录删除。

### 子任务

- **Phase 6a (`2dd6b1a`) — 根脚本 + orchestrator + audit utils → core 迁移** (+279/-58 LOC)
  - 21 个根脚本 (filtering 11/12/14, sentiment 21/22/23/24, validation 30-39, audit 52)
  - 2 个 orchestrator (run_pipeline_function.py, run_pipeline_validation.py)
  - 1 个 pipeline 函数体内 runtime import 漏网之鱼 (policy_alignment.py L585)
  - 3 个 scripts/audit/ 文件 (audit_changes / audit_deep / final_integrity)
  - 1 个 scripts/legacy/ docstring 更新
  - 1 个 test 测试断言调整 (test_39 cleaned 列表)
  - 关键边界处理: 32a 修复 Phase 2c 后的 ArticleDeduplicator 路径; 37 保留已知-broken `utils.llm_clients` 死代码
  - 验证: 778 passed, 7 skipped, 0 failed; warning 39 → 33

- **Phase 6b (本 commit) — `news_process/utils/` 整目录删除**
  - 删除 9 个 forward shim + __init__.py = 共 10 个文件
  - 兑现 Phase 1 的 "slated for removal in v2.0" 承诺
  - README + CHANGELOG 同步移除 utils/ 章节
  - 验证: 778 passed; warning 33 → ~25 (utils 系彻底退役)

### Phase 6 验收
- pytest news_process/tests/ → **778 passed, 7 skipped, 0 failed**
- grep `from utils\.` 仅剩字符串字面量 / docstring 历史注释 (无实际 import)
- `news_process/utils/` 目录不存在

---

## phase-5-baseline (2026-05-04, `d4a89ba`)

### Phase 5 总目标
Phase 4 后 long-tail closure: 修复 Phase 2c 遗留测试故障；消除 pipeline/ 与 tests/ 的所有 `from utils.*` legacy import；项目级 README + CHANGELOG 文档化。

### 子任务

- **Phase 5a (`0d01823`) — fix Phase-2c-broken test_45 + test_51 imports** (+40 LOC tests)
  - test_45_panel_export_main.py 用 facade 类把 `pipeline/panel/{encode,export,geography}` 的 5 函数 + 3 常量整合到 `bp` 命名空间
  - test_51_falsification_test.py 替换 `import_module('51_falsification_test')` 为 `from news_process.pipeline.falsification import controls as mod`
  - 验证: 24 测试全通过，Phase 4 acceptance 命令不再需要 `--ignore`

- **Phase 5c-1 (`92cdc6c`) — pipeline/ utils.* 迁移** (+68/-12 LOC)
  - 9 个 pipeline/ 模块从 `from utils.X` 迁到 `news_process.core.X`
  - 每文件加 sys.path 注入块，确保包模式调用 (`python -m news_process.pipeline.X.module`) 在任意 cwd 可用
  - 涉及: panel/{encode,export,runner,llm_peer_iv,network_brokerage,network_spillover}, features/{benefit_society,strategic_diff}, filtering/policy_alignment

- **Phase 5c-2 (`08ee1a8`) — tests/ utils.* 迁移** (+114/-64 LOC)
  - 10 个 tests/ 文件从 `from utils.X` 迁到 `news_process.core.X`
  - 32 个 runtime 调用点 (函数体内 import) 同步迁移
  - 验证: pipeline/ + tests/ 零 utils.X DeprecationWarning

- **Phase 5d (本 commit) — 文档收口**
  - 创建项目根 `README.md` (~150 行) 反映 Phase 1-5 完整架构
  - 创建项目根 `CHANGELOG.md` (本文件)
  - news_process/__init__.py 与 pyproject.toml 版本号 → `0.5.0-phase5`

### Phase 5 验收
- pytest news_process/tests/ → **778 passed, 7 skipped, 0 failed** (5min22s)
- 全套耗时从 Phase 4 的 11min10s 降至 5min22s (~50% 提速, 主因 utils 迁移省去启动开销)

---

## phase-4-baseline (2026-05-04, `581f655`)

### Phase 4 总目标
Long-tail cleanup: 关闭 Phase 2/3 全部 deferred 子任务（除 4f data 落盘迁移）。

### 子任务

- **Phase 4a (`75dace0`) — Stata .do 归属迁移 + 路径修正**
  - 5 个 .do 按学术依据归属判定，git mv 至 `papers_assets/<paper>/do/`
  - 修正所有 stale path: `output/<X>.dta` → `$panel_dta` (默认 `../../../data_processed/40_panel_yearly.dta`)
  - 添加统一路径前奏块 (`if "$panel_dta" == ""` 模式) 兼容 Stata 11+

- **Phase 4b (`1183d26`) — preprocess runner 5 拆**
  - `pipeline/preprocess/runner.py` 1256 LOC → **370 LOC** (-71%)
  - 拆出 `_constants.py` + `load.py` + `normalize.py` + `filter.py` + `dedup.py`
  - 同步迁移到 `from news_process.core.*` (Phase 5c-1 模式雏形)

- **Phase 4c (`265182c`) — falsification Stata 模板抽出**
  - `pipeline/falsification/controls.py` 2141 LOC → **1135 LOC** (-47%)
  - `print_stata_template()` 内嵌的 1016 行 Stata 模板 → 外置到 `papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl`
  - **决策**: 取消 Phase 2c-2 计划的 `falsification_helpers.py` 提取（现有函数 falsification 专属，跨论文复用价值低）

- **Phase 4d (`7c16e0e`) — config.yaml 7 拆 + prompt 外置 + deep-merge loader**
  - 831 行 monolithic `config.yaml` → 7 领域 YAML + 2 prompt `.txt` + 说明性 stub
  - `core/config.py:load_config()` 增加 split-mode 自动检测 + `_deep_merge` + `_inline_external_prompts`
  - 14 个等价性测试守护 split vs legacy 语义一致性 (`test_config_split_equivalence.py`)

- **Phase 4e (`6db74e3`) — pre-existing 测试故障 triage**
  - 3 个 audit 脚本 (含 `sys.exit(1)` at module load) 移出 tests/ 到 `scripts/audit/`
  - 4 个 Windows 文件锁测试 `@pytest.mark.skipif(sys.platform == 'win32')` 加详细 rationale
  - test_helpers + test_25 + test_39 import 路径修复 (Phase 2a/4d 兼容)

- **Phase 4g (`581f655`) — 空 placeholder 包清理**
  - 删除 `news_process/orchestration/` (零引用，Phase 1 计划未执行)
  - 修订 `news_process/validation/` + `pipeline/falsification/__init__.py` docstring 反映现状

### Phase 4 deferred (未执行)
- **Phase 4f**: `data_processed/` → `data/processed/<group>/` 落盘迁移 (高风险，需独立授权)

---

## phase-3-baseline (2026-05-04, `82f7de3`)

### Phase 3 总目标
多论文产品化: 共享内核 (`papers/_common/`) + 5 个独立论文包 + 多论文 CLI。

### 子任务

- **Phase 3a (`56efdbb`)** — 文献迁移
  - `papers/{big data,GLMY,network}/` 文献 PDF/MD (199 文件, 35MB) → `papers_assets/literature/`
  - 修正空格目录名 `big data` → `big_data`
  - .gitignore 加 `papers_assets/literature/` 全量忽略 + papers_assets 写入白名单

- **Phase 3b (`7244aaa`)** — papers/_common/ 共享内核
  - 5 个模块 (1102 LOC): paper_config, panel_loader, tables, figures, stata_runner
  - 32 个单元测试 (`test_papers_common.py`)
  - PaperConfig dataclass + 白名单守护 + sanitize_stata_columns + apply_publication_style

- **Phase 3c (`70de03e`)** — papers/bank_fintech_tone/ 主线包
  - dag.py 复用 `STAGES_MAIN` (identity-preserved)
  - analysis.py 经 importlib 调主管线; tables.py 生成 Table 1; figures.py 生成 Figure 1

- **Phase 3d (`f439f3f`)** — 4 个衍生论文包 (887 LOC)
  - benefit_society / brokerage_network / llm_peer / strategic_diff
  - 每篇 5 文件骨架 (init/dag/analysis/tables/figures)

- **Phase 3e (`f5a00b6`)** — 多论文 CLI 调度
  - `run_paper.py` 白名单反射加载 + --list / --stage / --dry-run
  - 严防任意路径反射 (只允许 `_VALID_PAPER_IDS`)

- **Phase 3f (`82f7de3`)** — 验收门槛
  - `test_papers_dag_consistency.py` (16 tests): 每论文 DAG ⊂ STAGES_MAIN by identity
  - `test_papers_imports.py` (34 tests): 5 论文 + run_paper.py 全部可 import

---

## phase-2-baseline (2026-05-04, `2866d25`)

### Phase 2 总目标
解耦: 把 39 个数字前缀脚本迁为 `pipeline/` 真包；消除 importlib 反射；OUTPUT_REGISTRY 单源化。

### 子任务

- **Phase 2a (`722bc0e`)** — atomic reflection-purge migration
  - 10 个 library-only 模块 (25-27, 41-44, 46-48) 迁到 `pipeline/{features,panel}/`
  - 15 / 45 body 迁到 `pipeline/{filtering,panel}/runner.py`，根级 thin shim
  - 删除全部 13 处 `importlib.spec_from_file_location` 反射

- **Phase 2b/c/d/e/f/g (`2866d25`) — multi-task batch commit**
  - 2b: pipeline/panel/runner.py 拆分 (含 output_dir 参数化)
  - 2c: 00 / 51 body 迁出根目录, 根级 shim
  - 2d: `core/schemas.py:OUTPUT_REGISTRY` 单源化
  - 2e: `migrate_data_layout.py` 干跑脚本 (deferred 实际 --apply)
  - 2f: `config/SPLIT_PLAN.md` 拆分计划 (Phase 4d 实际执行)
  - 2g: `test_panel_reproducibility.py` 列哈希基线测试

---

## phase-1-baseline (2026-05-03, `969894c`)

### Phase 1 总目标
包骨架 + 共享内核 (`core/`) 拆分 + 声明式 DAG 单源 (`core/dag.py`)。

### 关键改动
- `news_process/__init__.py` 把 news_process 变为可 import 的 Python 包
- `news_process/pyproject.toml` 配置 setuptools.packages.find
- `core/` 8 个模块从 `utils/helpers.py` 1500+ 行单文件拆出
- `utils/*.py` 9 个 forward shim 保留向后兼容
- `core/dag.py:STAGES_MAIN` / `STAGES_VALIDATION` 声明式定义 (StageSpec dataclass)
- `run_pipeline_function.py` / `run_pipeline_validation.py` 改为消费 core.dag
- `tests/integration/test_dag_consistency.py` 守护 orchestrator ↔ core.dag identity

---

## baseline-pre-restructure (2026-05-03, before `969894c`)

### 重整起点
- 39 个数字前缀脚本散落 `news_process/` 根目录
- `utils/helpers.py` 单文件 1500+ 行
- `config.yaml` 831 行 monolith
- 5 个 .do 在 `news_process/stata/` 集中
- 测试: `test_45` / `test_51` / `test_pipeline_lock::*` / `test_audit_changes` 等多处失败

---

## 学术依据汇总

各 phase commit message 含完整文献引用。核心方法论 anchor:
- **Phase 0 reproducibility**: pandas hash baseline + per-column 列哈希
- **Phase 4d split-mode**: deep-merge YAML loader (etcd / k8s configmap 模式)
- **Stata 32-字符列名**: Phase 3b sanitize_stata_columns + STATA_LABELS dict
- **Aho-Corasick automaton**: O(n+m) 多模式匹配 (Aho & Corasick 1975)
- **MinHash LSH dedup**: Broder 1997, SEQUENCES '97
- **Bank-FinTech-Tone main**: Tetlock 2007, JF (volume vs content) + Hassan et al. 2019, QJE (Table 7 falsification)
- **Benefit Society**: Jha, Liu & Manela 2026, RFS §1.3.2
- **Brokerage Network**: Han, Jiang, Zhang & Zhu 2024 + Bramoullé et al. 2009
- **LLM Peer**: Cao, Li, Wang & Zhao 2025
- **Strategic Diff**: Guzman & Li 2023 + Hoberg & Phillips 2016
