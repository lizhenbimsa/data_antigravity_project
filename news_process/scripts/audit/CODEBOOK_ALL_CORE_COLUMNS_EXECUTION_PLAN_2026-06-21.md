# 执行计划：codebook 取消"分析核心列 vs 辅助列"区分 (所有列均为核心列)

**日期**: 2026-06-21
**作者**: Claude Opus 4.8 (1M context)
**状态**: v3 FINAL (用户已拍板基线 **A2 + β**; 经 13-agent 对抗审核, 0 confirmed P0; **本轮仅交付计划, 暂不实施**)
**指令**: "codebook 不再区分'分析核心列'与辅助列，所有列均属于核心列清单范围。"

> ⚠ **行号口径**: 行号为**近似导航**, 工作树自基准漂移 (±约 9–17 行)。**实施前一律以符号锚 (函数名/distinctive string) grep 定位**, 勿照裸行号机械编辑。

---

## 0. 用户已拍板的基线 (本计划据此展开)

| 决策点 | 选定 | 含义 |
|---|---|---|
| **A. is_core 列去留** | **A2 = 删除 `is_core` 列** | codebook xlsx 从 8 列降为 7 列, 不再输出 is_core; 最贴"不再区分", 零回归 (无程序化消费者) |
| **B. 内部机制** | **β = 彻底退役** | 删 `assign_core_columns` 函数 + `core_patterns` + `STATA_IC_MAX_VARS` 常量 + `core_cols` 形参 + 调用与日志 |
| **下一步** | **仅交付计划, 暂不实施** | 本文档为交付物; 不改任何源码/测试 |

> α (解耦保留) / γ (改名) / A1 (保留恒 True) 已被用户否决, 仅在 §11 留作"已否决备选"备查。

---

## 1. TL;DR (执行摘要)

- **主改动面 = `pipeline/panel/stata_export.py`**: 删除整个 `is_core` + `assign_core_columns` + `core_patterns` + `STATA_IC_MAX_VARS` 机制。
- **连带清理 (β 必做)**: 3 个生产者文件的悬空注释 (`encode.py` / `encode_collab.py` / `runner.py` 引用 "stata_export.py core_patterns") + 1 个历史 sidecar 计数键 + 4 个测试文件的删除/重写 + CLAUDE.md。
- `codebook.py` 的 `variable_codebook.{csv,json,md,xlsx}` **本就无 is_core** → 零改动。
- **golden-safe / .dta-safe**: 只动 codebook xlsx 元数据列, 不改 panel 列值/`.dta`/列哈希; golden 派生只过滤 `.parquet`。
- **⚠ 关键跨计划耦合 (必读 §3)**: β 删 `core_patterns` + A2 删 `is_core` 会**使同日姊妹计划 `SEMANTIC_STALENESS_SS_EXECUTION_PLAN_2026-06-21.md:81` 的两处文字描述失效** (它依赖 core_patterns 声明 `semantic_staleness_ss` + "Phase B 列被标 is_core")。**非功能性破坏** (该列仍由 stage 18/30a 照常产出), 但落地时须同步标注姊妹计划。

---

## 2. 现状 (Single Source of Truth 核实)

### 2.1 `is_core` / `core_patterns` 机制的全部触点 (符号锚, 行号近似)

`pipeline/panel/stata_export.py`:

| 符号锚 (grep 用) | 角色 | β 处置 |
|---|---|---|
| 模块 docstring `is_core 列仍标注分析核心变量子集` (~L10) | 散文 | 删 is_core 描述 |
| 模块 docstring step 6 `assign_core_columns(STATA_IC_MAX_VARS=2048 守卫…)` (~L51) | 散文 | 删该步骤描述 |
| `STATA_IC_MAX_VARS = 2048` (~L82-85) | 常量 + 注释 | **删** |
| `def assign_core_columns(` (~L477-698) | 函数全体 (docstring/`core_patterns`(218 条)/WARN/`raise` 守卫/`Core 列数` INFO 日志) | **整函数删** |
| `export_panel_to_stata` docstring `assign_core_columns 经原名反查` (~L1143) | 散文 | 改为只提 `build_variable_labels` 反查 |
| `core_cols = assign_core_columns(...)` + `含 N 个分析核心列` 日志 + 上方注释 (~L1222-1224, ~L1229-1230) | 调用 | **删调用 + 删/改日志** |
| `def _write_codebook_xlsx(..., core_cols, ...)` + `core_set = set(core_cols)` + `'is_core': col in core_set` (~L1235-1259) | writer | **删 `core_cols` 形参 + `core_set` 行 + `'is_core'` 键** |
| `export_panel_to_stata` docstring `codebook is_core 列仍标注分析核心变量子集` (~L1136) | 散文 | 删 is_core 描述 |
| banner 日志 `含 is_core/original_name 反查` (~L1378) | 散文 | 删 is_core 字样 (该列已不存在) |

**关键不变量 (核实)**: `core_cols` 只流向 codebook xlsx 的 `is_core` 列 + 一条日志; `write_dta` 写全列与之无关 → **`.dta` 不受影响**。`export_panel_to_stata` 返回 dict 键 = `{full_dta, labels_do, codebook_xlsx, backend}` (无 is_core/core_cols 键, 无外部依赖)。已 grep 核实**无程序化消费者**读 codebook 的 is_core 列。

### 2.2 生产者文件的悬空注释 (β 连带清理, 全部已核实存在)

删 `core_patterns` 后, 下列注释成悬空引用 (它们声称"某列已在 stata_export.py core_patterns 注册"):

- **`pipeline/panel/encode.py`** (~L1339): `# (stata_export core_patterns 已预留两名), 裸名列保留 = _full 别名` → 改为不提 core_patterns (改述"下游 Stata/codebook 期待这两名")。
- **`pipeline/panel/encode_collab.py`** (~L1056 / ~L1062 / ~L1102): `与 stata_export.py core_patterns 注册名一致` / `这些 panel 列已在 stata_export.py 注册 core_patterns` / `# 与 stata_export.py core_patterns 一致` → 改为"与下游 Stata 期待列名一致"。
- **`pipeline/panel/runner.py`** (~L2295 / ~L2298): `stata_export.py core_patterns 已声明期待 (*_staleness 等)` / `cross_outlet_tone_variance_* 在 stata_export core_patterns` → 改为不提 core_patterns。

### 2.3 历史 sidecar 计数键

- **`config/v2_3_implementation_constants.json`** (~L145): `"stata_export_core_patterns_added_cols": 28` —— 这是 **v2.3 历史实现快照键** (记录"当时往 core_patterns 加了 28 列")。**建议作历史记录冻结保留** (项目惯例: 带版本号的 sidecar 不回改; 删 core_patterns 不使该历史陈述变假, 它描述的是 v2.3 当时状态)。若审稿坚持去悬空, 可加注释标"core_patterns 已于 2026-06-21 退役"。**默认: 不动 (历史锚)。**

### 2.4 `codebook.py` 无 core/aux 概念 (核实)

`generate_codebook` 产出 `variable_codebook.{csv,json,md,xlsx}` 无 `is_core`/core/aux (grep 0 命中) → **零改动**。

### 2.5 范围外 (历史 `.dta` 切分残留 + 历史快照锚, 勿动)

- 历史 `.dta` 文件级双切分残留 (与 codebook is_core 无关): `core/schemas.py`、`config/pipeline_v34_rerun.yaml`、3 个 `.do.tmpl`、`stata_templates/README.md`、`stata_export.py` 内 `full/aux .dta` 散文 (~L841/L1175)。
- 历史快照锚 (刻意不改): `scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md` 的 "codebook is_core 标注" 描述。

---

## 3. ⚠ 关键跨计划耦合 (β + A2 必须协调)

**同日姊妹计划** `scripts/audit/SEMANTIC_STALENESS_SS_EXECUTION_PLAN_2026-06-21.md` **第 81 行明文**:

> "**不改 `stata_export.py`** (line 615 `core_patterns` 已声明 `semantic_staleness_ss`; 现缺席触发 `assign_core_columns` 'schema 漂移监测' WARN…)。⚠ 该 warning 是 pre-existing… **Phase B 列产出后它自动消失 + 列被标 `is_core`**。"

**冲突**: 本计划 β 删 `core_patterns` (含其对 `semantic_staleness_ss` 的声明 + 那条 WARN), A2 删 `is_core` 列 → 姊妹计划的两处承诺 (**"WARN 自动消失"** 与 **"列被标 is_core"**) 双双失去前提。

**性质判定**: **文档协调问题, 非功能破坏**。`semantic_staleness_ss` 列仍由 stage 18/30a 照常产出 (与 core_patterns/is_core 无关); β 后那条 WARN 根本不存在 (=自动满足"消失"), is_core 列也不存在 (=该承诺 moot)。姊妹计划的**功能目标不受影响**。

**落地处置 (必做)**:
1. β 落地时**同步标注**姊妹计划 §:81: "core_patterns/is_core 已于 2026-06-21 (本计划) 退役; semantic_staleness_ss 不再触发 WARN / 不再被标 is_core; 列产出本身不受影响。"
2. 若两计划由不同人/不同时段执行, **先落地者须在 release note 交叉引用另一计划**, 避免后者按陈旧前提操作。

**第二个耦合计划 (round-2 验证补充, round-1 漏)**: `scripts/audit/NONPOLARITY_DIMENSIONS_EXECUTION_PLAN_2026-06-20.md` (tracked/committed) 的 **WS-C** (L129 / L175 排序图) 明文要"补 `avg_specificity`/`avg_within_doc` 等 ~12 列到 `assign_core_columns` 核心列清单"。β 删 `assign_core_columns`/`core_patterns` 后该子项**永久作废** (无 core 清单可补)。**性质同 SEMANTIC_STALENESS = 文档协调, 非功能破坏** (该计划仅产计划文档未实施; WS-C 又是其自身审计已部分推翻的待办)。**落地处置 (已做)**: 在该 NONPOLARITY 计划 WS-C 段加同款更正 blockquote (镜像 SEMANTIC_STALENESS L82); WS-A 的 `HEURISTIC_LABELS` 标签增强不受影响 (标签字典独立于 core 清单)。

---

## 4. 改动清单 (基线 A2 + β)

> 实施前先 `grep -nE 'is_core|分析核心列|核心列|aux|Core 列|IC 余量|core_patterns|assign_core_columns|STATA_IC_MAX_VARS' pipeline/panel/stata_export.py` 兜底全量列出位点。

### 4.1 `pipeline/panel/stata_export.py` (主改)

1. **删常量** `STATA_IC_MAX_VARS = 2048` + 其注释块 (~L82-85)。
2. **删整个 `assign_core_columns` 函数** (~L477-698): def + docstring + `core_patterns`(218 条) + 反查循环 + WARN 块 + `raise` 守卫 + `Core 列数` INFO 日志, 全删。
3. **`export_panel_to_stata`**: 删 `core_cols = assign_core_columns(...)` 调用 (~L1224) + 上方注释 (~L1222-1223) + `含 N 个分析核心列` 日志行 (~L1229-1230); 删传给 `_write_codebook_xlsx` 的 `core_cols` 实参 (~L1239)。
4. **`_write_codebook_xlsx`**: 签名删 `core_cols: List[str]` 形参; 删 `core_set = set(core_cols)` (~L1252); 行字典**删 `'is_core'` 键** (~L1259)。docstring 同步去 is_core 描述。
5. **散文** (精确): 模块 docstring **仅 L10** (勿动 L7-9 的 .dta 散文) + step 6 **L51** (删 assign_core_columns 步骤, 后续步骤号 6/7 顺延或保留编号注明) + `export_panel_to_stata` docstring **L1136**(删 is_core 句)/**L1143**(改为只提 build_variable_labels 反查) + banner **L1378**(删 is_core 字样)。
   - ⚠ 改模块 docstring 时**保留 `未实现`/`missing_user_values`/`no-op` 三 token** (被 `test_omni_fix_stata_export.py::test_module_docstring_no_longer_claims_extended_missing` ~L378 锁定; 与 is_core 无关, 误删即挂)。

### 4.2 生产者悬空注释 (§2.2, β 连带)

- `encode.py:~1339`、`encode_collab.py:~1056/~1062/~1102`、`runner.py:~2295/~2298`: 把"已在 stata_export.py core_patterns 注册/声明"改述为"下游 Stata/codebook 期待该列名"(去对已删机制的引用)。**纯注释, golden-safe。**

### 4.3 测试 (`tests/`) — 删除 / 重写 (β, 穷举)

| 文件 | 测试 / 行 | 处置 (原因) |
|---|---|---|
| `test_omni_fix_stata_export.py` | `test_core_contains_real_bartik_iv_names` (~L266/272)、`test_core_phantom_bartik_name_retired` (~L278/281)、`test_core_missing_patterns_warn` (~L285/289)、`test_assign_core_resolves_renamed_columns` (~L298/304) | **全删** (`se.assign_core_columns` 已不存在 → AttributeError); 文件 docstring L11 顺改 |
| `test_stata_export.py` | `test_core_columns_fit_ic` (~L116, import `STATA_IC_MAX_VARS, assign_core_columns`) | **删** (collection ImportError) |
| `test_stata_export.py` | `test_write_codebook_rename_map_none_default` (~def L443, 调用 ~L452 `_write_codebook_xlsx(mock_panel, var_labels, {}, list(mock_panel.columns), str(out), rename_map=None)`) | **重写调用**: 删去 `list(mock_panel.columns)` 这个 core_cols 实参 (新签名无该形参) |
| `test_stata_export.py` | 文件 docstring L7 | 顺改 (去 "core 列归属…供 codebook is_core") |
| `test_stata_export_v3_5_1.py` | `test_a1_a3_cols_in_core_patterns` (~L28/31)、`test_core_count_below_stata_ic_max` (~L52/56-57) | **全删** |
| `test_stata_export_v3_5_1.py` | `test_old_panel_without_a1_a3_graceful` (~L88, 同时调 `build_variable_labels` 与 `assign_core_columns` ~L93) | **重写**: 删 assign_core_columns 部分, 仅保留 `build_variable_labels` graceful 断言 |
| `test_stata_export_v3_5_1.py` | 文件 docstring L4/L7 (提 STATA_IC_MAX_VARS) | 顺改 |
| `test_v3_5_to_v3_5_1_migration.py` | `test_stata_ic_core_below_2048` (~L114, import `STATA_IC_MAX_VARS, assign_core_columns` ~L117-118) | **删** (collection ImportError) |

- **⚠ 新增回归测试 (必做, 可判别)** — 验证 codebook **不再输出 is_core 列**:
  ```python
  def test_codebook_xlsx_has_no_is_core_column(tmp_path):
      import pandas as pd
      from news_process.pipeline.panel.stata_export import _write_codebook_xlsx
      df = pd.DataFrame({'target_bank': ['A'], 'year': [2020], 'some_aux_col': [1.0]})
      out = tmp_path / 'cb.xlsx'
      _write_codebook_xlsx(df, {}, {}, str(out))          # 新签名: 无 core_cols 形参
      cb = pd.read_excel(out)
      assert 'is_core' not in cb.columns, "A2: codebook 已取消核心/辅助区分, 不应再有 is_core 列"
      # 仍保留的反查列存在性 (回归保护)
      assert 'var_name' in cb.columns and 'original_name' in cb.columns
  ```
  改动前 (有 is_core 列) **失败**, 改动后通过 → 真正锁住本次变更。**确定性、零 data/raw、零付费阶段。**

### 4.4 文档 + 记忆

- **CLAUDE.md** (~L306, Stata 容量段): 删/改 "`assign_core_columns` 守卫'分析核心列'清单… 该清单现在只供 codebook is_core 标注" → "2026-06-21: codebook 取消核心/辅助区分 (删 is_core 列); `assign_core_columns`/`STATA_IC_MAX_VARS`/`core_patterns` 整体退役"。
- **新增 memory** `codebook-all-core-columns-2026-06-21.md` + `MEMORY.md` 一行指针: 记 A2+β 决策、is_core 单一生产者=stata_export、codebook.py 无该概念、golden-safe、生产者注释 3 文件、**姊妹 SEMANTIC_STALENESS 计划耦合 (§3)**。

---

## 5. golden / 复现 安全性论证

1. **panel 列值不变**: 只动 codebook xlsx 元数据列, 不触 panel 数值。
2. **`.dta` 不变**: `write_dta` 写全列, 与已删的 `core_cols` 无关。
3. **golden snapshot 不哈希 codebook (精确根因)**: codebook xlsx **虽在 `OUTPUT_REGISTRY` 注册** (`core/schemas.py`), 但 golden 派生与漂移闸门均以 **`endswith('.parquet')` 过滤** (`generate_golden_snapshot.py` ~L63 + `test_panel_reproducibility.py` ~L99) → xlsx 任何改动都不进 golden。→ **无需重生 golden**, 无需跑付费 stage 21。
4. **复现门禁不受影响**: `test_panel_reproducibility` parametrize 清单物理上仅含 `.parquet`。
   - 注: 该门禁现有 pre-existing 漂移失败 (盘面 T=2/schema) 与本改动**无关**; 以 baseline stash 区分。
5. **生产者注释清理 + 测试删除 + sidecar 不动**: 全部 golden-safe (无 panel-producer 逻辑改动)。

---

## 6. 验证步骤 (实施后)

```bash
# 1) ruff
ruff check news_process/pipeline/panel/stata_export.py \
           news_process/pipeline/panel/encode.py \
           news_process/pipeline/panel/encode_collab.py \
           news_process/pipeline/panel/runner.py \
           news_process/tests/

# 2) 静态: 确认 assign_core_columns / STATA_IC_MAX_VARS / core_patterns 全仓零残留 (除历史 sidecar/审计 md)
grep -rnE 'assign_core_columns|STATA_IC_MAX_VARS|core_patterns' news_process/pipeline news_process/tests

# 3) 定向单测 (含新增回归 + 删后无 ImportError)
pytest news_process/tests/test_stata_export.py \
       news_process/tests/test_stata_export_v3_5_1.py \
       news_process/tests/test_omni_fix_stata_export.py \
       news_process/tests/integration/test_v3_5_to_v3_5_1_migration.py -v

# 4) DAG 一致性 (零影响, 无阶段增删)
pytest news_process/tests/integration/test_dag_consistency.py

# 5) 复现门禁 (确认无新增失败; pre-existing 以 baseline stash 区分)
pytest news_process/tests/integration/test_panel_reproducibility.py

# 6) 全量 sweep 抽查 (确认删函数未连带破其它 import)
pytest news_process/tests -q
```

**通过判据**: ruff clean; step2 grep 在 pipeline/tests 下零残留 (sidecar/审计 md 除外); 定向单测全绿 (含可判别新增回归 + 无 collection ImportError); sweep 无**新增**失败。

---

## 7. 风险与回滚

| 风险 | 级别 | 缓解 |
|---|---|---|
| 删 `STATA_IC_MAX_VARS` 致 3 测试 collection ImportError | 高 (确定发生) | §4.3 已列这 3 测试为 **删除项** (`test_core_columns_fit_ic` / `test_core_count_below_stata_ic_max` / `test_stata_ic_core_below_2048`); 先删测试再删常量 |
| 删 `assign_core_columns` 致 4 个 omni 测试 AttributeError | 高 (确定发生) | §4.3 已列删除 |
| 漏改 `_write_codebook_xlsx` 调用方仍传 core_cols → TypeError | 中 | §4.1.3+4.3 同步改 `export_panel_to_stata` 调用 + `test_stata_export.py:452` 直调 |
| 生产者悬空注释残留 (无害但误导) | 低 | §4.2 列 3 文件; §6 step2 grep 兜底 |
| **β 破坏姊妹 SEMANTIC_STALENESS 计划 §:81 前提** | 中 (协调项) | §3: 落地时同步标注姊妹计划; release note 交叉引用 |
| 新增回归测试写成"假绿" | 中 | §4.3 给 A2 可判别写法 (`assert 'is_core' not in cb.columns`) |
| 误改历史 `.dta`-split 散文 / 历史 sidecar | 低 | §2.3/§2.5 明确范围外 |

**回滚**: `git checkout` 受影响文件 (stata_export.py + encode.py + encode_collab.py + runner.py + 4 测试 + CLAUDE.md); 无数据/golden 牵连, 成本极低。

---

## 8. 实施顺序 (建议)

1. **先删测试** (§4.3): 4 个 omni 测试 + 3 个 ≤2048 测试 + 重写 `test_old_panel_without_a1_a3_graceful` + 重写 `test_write_codebook_rename_map_none_default` 调用 + 加新增回归测试 (此时新测试会失败/旧码尚在 → 预期)。
2. **改源码** (§4.1): `_write_codebook_xlsx` 删 is_core/core_cols → `export_panel_to_stata` 删调用/日志 → 删 `assign_core_columns` 函数 → 删 `STATA_IC_MAX_VARS` → 改散文 (保 3 token)。
3. **改生产者注释** (§4.2): encode.py / encode_collab.py / runner.py。
4. **改 CLAUDE.md** (§4.4)。
5. **同步标注两个耦合计划** (§3): SEMANTIC_STALENESS (L82/L325) + NONPOLARITY WS-C。
6. **验证** (§6 全 6 步)。
7. **写 memory + MEMORY.md 指针** (§4.4)。
8. **(按用户指示) 提交 —— ⚠ hunk 级隔离铁律 (round-2 验证新增)**: 工作树 `stata_export.py` 与 `runner.py` 混入**并行 `_allv`(All-Vintage anchor) 会话**的外来 hunk (另有 semantic_staleness_ss 会话改 ~10 文件)。**禁** `git add stata_export.py/runner.py` 整文件 / `git add -A` / `git stash push -- <file>` (均会带入或还原并行 hunk; 实测 `git stash push -- runner.py` 把 _allv 匹配从 21 降到 0 = 整文件被 stash)。**须** by-hunk 暂存 (`git add -p` 选本改动 codebook-退役 hunk; 或干净 worktree off origin/main 逐 hunk 重贴)。经 round-2 实证我的 hunk 与 `_allv` hunk **物理分离可摘**: stata_export.py 排除 `@@ -428` 纯加 _allv 块, runner.py 仅取 `@@ -2255` 注释 hunk。洁净提交 10 文件清单见 memory `codebook-all-core-columns-2026-06-21`。

---

## 9. 待办边界 (本轮)

- **本轮 = 仅交付本计划**, 不改任何源码/测试 (用户指示)。
- 实施触发后, 按 §8 顺序执行; golden 无需重生 (§5)。

---

## 10. 审核结论摘要 (13-agent 对抗审核, 0 confirmed P0)

核心结论经实测全部成立: is_core 唯一生产者=stata_export、codebook.py 无该概念、无程序化消费者、golden-safe (xlsx 不进 golden)。已修正 v1 缺陷: 虚构函数名 (`write_panel_exports`→`export_panel_to_stata`)、计数 (~140→实测 **218** 声明)、散文位点补全、回归测试假绿陷阱、β 真实失败模式 (ImportError/生产者注释/sidecar)、**姊妹 SEMANTIC_STALENESS 计划耦合**。

## 11. 已否决备选 (备查)

- **A1** (保留 is_core 恒 True): 被 A2 取代 (A2 更贴"不再区分", schema 稳定收益在纯人读产物前提下近乎为 0)。
- **α** (解耦保留 assign_core_columns 作监测): 被 β 取代 (用户要彻底退役; 且该 schema 漂移 WARN 现为慢性噪声 — 真盘每跑必报 34 个永久死 pattern, 监测价值已退化)。
- **γ** (改名而非删除): 被 β 取代 (彻底删除比改名更干净)。
