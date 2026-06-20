# 根目录 NN_*.py 全量重编号 — 执行计划

> 日期: 2026-06-20 · 作者: Claude (Opus 4.8) · 状态: **GO (2 轮对抗审计收敛: 0 P0; §15 + §16 fold-in 全并入; 待用户授权执行)**
> 依据: 爆炸半径测绘 (wf_4ac627a7-de1) + 产物名测绘 (wf_ac44b87f-81d) + 计划审计 R1 (wf_d4985592-f9b) + 计划终审 R2 (wf_930f26cb-b4f) + 核心单一真源亲读
> **⚠ 执行权威顺序: §18 (行号精校) > §17 (终审定稿) > §16 (终整合) > §15 (R1 修补) > §10–§14 (Scope-Full 规范) > §3–§5 (shim-only 背景)。任何冲突以更高优先节为准。**

## 用户已拍板 (2026-06-20)
- **决策① 范围 = Scope-Full**: shim 名 + 产物名 (parquet/dta/npy/xlsx) + config + golden **全部对齐重编号**。
- **决策② 验证 band = 方案 B**: 验证 16 阶段 → **60–75**。
- **决策③ 外围 = 全选**: 改 26 个 `test_NN_*.py` 文件名 + 刷新 CLAUDE.md+新审计 doc + 订正 config/paths 旧号注释 + `52/53 → 81/82` 归入 8x 工具带。

## Scope-Full 已定子方案 (主控据「shim# = 产物#、最小化高频产物 churn」原则裁定)
- **panel: shim `45 → 40`** (产物 `40_*` 5 文件**不动** → 自动对齐; 比反向 `40_*→45_*` 少动 ~12 figures+stata+golden)。
- **stata `46` / falsification `51` 不变** (产物 `46_*.dta` / `51_*.parquet` 本已同号对齐)。
- **验证数据产物随号迁移**: `39c_*→72_*` / `39d_*→73_*` / `39f_*→75_*` / `32_human_samples.xlsx→61_human_samples.xlsx`。
- **27c → 80** (产物 `27c_alt_anchor_*→80_alt_anchor_*`)。
- **内联 `27_benefit_*.npy` (×8) 保留 27_ 前缀** (内联 panel 子特征, **无编排 stage 27 shim**, 无对齐目标; 仅订正 paths.yaml:83 误导注释)。`42_cessation_report.xlsx` 待测绘确认产者后决定 (疑为 panel 内部子步, 倾向保留)。
- **golden 策略 = 外科 re-key + on-disk `mv`** (产物内容字节不变 → 列哈希不变 → **不重 hash、不跑付费阶段、不触 BLAS/HASHSEED 不确定性**); **禁用** `generate_golden_snapshot.py` 全量重生 (会重 hash 命中本机非确定性)。
- **config KEY 名是否随号改**: 待 config-key 测绘量化 call-site 后定 (倾向: 值+注释必改; 键名按 call-site 成本权衡)。

---

## 0. 任务目标 (用户原话)

1. 把根目录 35 个 `NN_*.py` thin shim 的 **NN 数字**按功能/执行顺序系统重排, 使 NN **准确反映执行先后**。
2. NN ∈ 00–99; **消除字母后缀** (不得再有 `12_*.py` 与 `12b_*.py` 并存)。
3. 在 `run_pipeline_function.py` / `run_pipeline_validation.py` / `run_paper.py` 三个入口重新组织罗列。
4. 多智能体对整个项目**最系统全面的评审/审核/验证**, 确保万无一失。

---

## 1. 关键发现 (耦合模型)

### 1.1 shim 文件名 = 全局主键, 零动态构造
- **零** 处从 NN 数字**动态拼**文件名 (无 f-string / glob / listdir 发现)。全是**硬编码字面量**。单一真源 = `core/dag.py::StageSpec.script`。
- `core/stage.py::run_stage` 用 `os.path.join(base_dir, stage_script)` 起子进程 → **磁盘文件必须与 DAG 字符串同步改名**。
- 35 个 shim 全是 ≤22 行 thin shim, 从 `news_process.pipeline.*` (无编号的模块路径) import, **仅在 docstring** 里提到自己的编号 (非 load-bearing)。

### 1.2 shim 名被引用的三处核心 (改名必须**同一原子提交**)
| 文件 | 引用点 | 说明 |
|---|---|---|
| `core/dag.py` | `StageSpec.script` ×32 + `name="阶段NN:…"` 标签 | 主线 16 + 验证 16 |
| `core/schemas.py` | `OUTPUT_REGISTRY` 键 ×16 + `_OUTPUT_FILENAME_KEYS` 元组首元 ×17 + `EXPECTED_NO_OUTPUT_STAGES` ×16 | `_validate_registry_invariant()` **import 即 fail-fast**, 任一漂移 `RuntimeError` |
| `run_pipeline_function.py` | 硬编码 `script == '21_tone_llms.py'` (L431, skip-21 闸门) | 唯一一处硬编码 shim 名 (指纹逻辑是 parquet 名, 属另一范围) |

> ⚠ 因 `_validate_registry_invariant()` 在 import 时强校验 `OUTPUT_REGISTRY` 键 ↔ `_OUTPUT_FILENAME_KEYS` 首元 ↔ `EXPECTED_NO_OUTPUT_STAGES` 一致, **dag.py + schemas.py + 物理改名 三者必须一次性配套落地**, 不能分步 (中途 import 即崩, 所有测试连带红)。

### 1.3 关键成本不对称 — **shim 名 vs 产物名是两套独立命名空间**
- 产物 parquet/.dta 文件名 (`21_tone_llms.parquet`, 但 stage45 产 `40_*`) 与 shim 名仅靠**约定**耦合, 已天然脱钩 (45→40 早就不一致)。
- **shim-only 改名 → 下游几乎零成本且 golden 安全**:
  - golden 基线 (`golden_panel_v0.json`) **按 parquet 文件名做键**, 不含任何 `.py` 名 → **零改动, 复现 gate 不重跑任何付费阶段** (S1 verdict)。
  - `papers/*` (figures/tables/panel_loader/analysis) 全部**动态读** DAG/`OUTPUT_REGISTRY` → **零改动**。
  - Stata ~60 个 `.do.tmpl` 只读 `.dta` (字面量), 与 shim 名无关 → **零改动**。
  - `config/paths.yaml` 的 `output_NN` 键/`.parquet` 值属 parquet 命名空间 → **零改动** (仅行内注释提到 shim 名, 是注释)。
  - `_llm_cache.db`、磁盘 `data/processed/*.parquet` → **零改动**。
- **若连产物名也改 (Scope-Full) → 爆炸**: ~12 个 figures.py + `tables.py` + panel_loader 默认 + ~60 Stata 模板 + `golden_panel_v0.json` 重键 + `conftest.py` + `test_panel_reproducibility.py` 参数化清单 + `paths.yaml` 值 + `OUTPUT_REGISTRY` 值 + benefit `27_*.npy` 族。**强烈不推荐**。

### 1.4 测试耦合 (shim-only 范围会动到的)
- **硬编码 shim `.py` 字符串** (改名即破, 必须同步改):
  - `tests/integration/test_dag_consistency.py`: L134/142 (`39d`), monkeypatch L347/352-353/364/377/396-408/426 (含 `00`/`21`/`22` .py + 复合键)。另 L244-285 是**通用一致性测试**(若三处配套改对则恒绿, 改漏则正确报红——这是我们的安全网)。
  - `tests/test_39a_inter_track_kappa.py`: L114/116/117/118 (`39a`/`39c`/`39d`)。
  - `tests/test_15_policy_alignment_dual.py`: L202/209/210/211 (`12`/`13`/`14`/`15` 的 `.index()`)。
  - `tests/test_39_prompt_sensitivity.py`: L142 (在 `run_pipeline_validation.py` **源码文本**里搜 `'39_prompt_sensitivity.py'`)。
  - `tests/integration/test_v3_4_to_v3_5_migration.py` + `tests/test_v3_4_to_v3_5_migration.py`: L41/42/60 (`39c` 的 **.py 物理 .exists()** + script)。
  - `tests/test_benefit_society_audit_combined.py`: L63/66/70/80 (`27c` 的 **.py 物理 .exists()**)。
  - `tests/test_papers_common.py`: L123/125/144 (`45`/`11` 作 `OUTPUT_REGISTRY` 键)。
- **计数断言** (16+16 集合不变 → 恒绿, 仅需复核): `test_dag_consistency.py` L103/122/215/222/230/241; `test_39a` L119; `test_39_prompt` L138 ("16 个验证阶段" 字面量, 与 runner 源码同步)。
- **26 个 `test_NN_*.py` 文件名**: pytest 按 glob 发现, 改名纯**装饰性**, 不影响收集/断言 (可选)。
- **rename-safe 误报**: `test_stage_smoke.py` 用 dotted module path (非 shim 名), **勿浪费编辑**。`test_run_pipeline_function.py` 只断言 parquet 名 (对 shim-only 免疫)。

### 1.5 三个未注册 shim + 孤儿
- `27c_placebo_and_alt_anchor.py`: 内联 stage-27 (benefit_society 特征, **无 shim**) 的审计姊妹, 手动/benefit_society 论文调用, 产 `27c_alt_anchor_and_placebo_panel.parquet`。**含字母后缀 `c` → 按规则须改**。被 `test_benefit_society_audit_combined.py` 物理 .exists() 引用。
- `52_stata_data_audit.py` / `53_export_stats_excel.py`: 用户 CLI 包装 (post-export, 按需跑), 无后缀, > 51 → **可保留**。
- **孤儿注释**: `paths.yaml:83` `output_27_benefit_cache` 注释写 `# 27_fintech_benefit_society.py →…`, 但**该 shim 不存在** (产物实为内联 `pipeline/features/benefit_society.py`)。须**订正注释**, 勿当丢失 shim。
- **panel 内部子步 41/42/43/44/46/47 与 25/26/27 不是 shim** — 是 `pipeline/panel/runner.py` 里 stage 45 的内部标签/内联特征。**勿动, 勿建 shim**。

---

## 2. 范围决策 (决策①, 推荐 = shim-only)

**推荐: 仅改 shim 文件名 (NN_*.py), 保持所有产物名 (parquet/.dta/.npy/.xlsx) 不变。**
- 满足用户字面要求 (shim NN 反映执行顺序 + 去后缀); golden 安全; 下游零成本; 不触付费阶段。
- 代价: shim# 与产物# 在少数阶段不一致 (如 panel shim 45 → 产物 `40_*`) —— 但**此不一致本已存在**, 且修它需 Scope-Full 重生 golden。
- 备选 (不推荐): Scope-Full 连产物名一起改 → ~70 文件 + golden 重生 + 多套 Stata/paper 同步, 风险与工作量数量级上升。

---

## 3. 新编号方案 (决策②)

两套方案共用**主线**部分, 区别在**验证**band。主线: 保留所有高频熟悉号 (00/11/12/21-24/45/46/51), 仅修后缀+乱序。

### 3.1 主线 STAGES_MAIN (两方案相同)
| 现 | 新 | shim | 变更原因 |
|---|---|---|---|
| 00  | **00** | preprocessing | 不变 |
| 11  | **11** | news_bank | 不变 |
| 12  | **12** | news_fintech | 不变 |
| 12b | **13** | cooccurrence_filter | 去后缀 `b` |
| 13  | **14** | materialize_ctx | 顺移 |
| 14  | **15** | fintech_intensity | 顺移 |
| 15  | **16** | article_policy_alignment | 顺移 |
| 21  | **21** | tone_llms | 不变 |
| 22  | **22** | tone_words | 不变 |
| 23  | **23** | tone_berts | 不变 |
| 24  | **24** | herd_decay_processor | 不变 |
| 30a | **25** | article_sbert | 去后缀 `a` + 修倒挂 (本就在 24 后跑) |
| 18  | **26** | article_staleness | 修倒挂 (在 25/sbert 后跑, 却号 18) |
| 45  | **45** | panel_export_main | 不变 (产物 `40_*`, 已知脱钩) |
| 46  | **46** | stata_export | 不变 (产物 `46_*.dta` 一致) |
| 51  | **51** | falsification_test | 不变 (产物 `51_*.parquet` 一致) |

主线只动 6 个: `12b→13, 13→14, 14→15, 15→16, 30a→25, 18→26`。结果**严格单调 + 无后缀**。

### 3.2 验证 STAGES_VALIDATION — 两个 band 选项

> 验证 16 阶段历史挤在 31–39 (9 个整数槽) 靠后缀塞下 (32a/38b/39a/c/d/e/f)。去后缀 + 单调 **必然整体重排** (不存在「少改」路径——32a 卡在 32 与 33 之间无整数可用)。

**方案 B「分带·忠于全局执行顺序」(推荐)** — 验证整体落 **60–75**。
理由: 验证是**独立 pipeline**, 消费主线产物, **在主线之后跑** → 号应 > 主线末号 51。现 31–39 数值上**早于** panel(45)/falsif(51), 与执行顺序**矛盾**; 落 60–75 才真正「反映执行先后」, 且与 panel 内部标签 41–47、内联 25/26/27、CLI 工具 52/53 **全无重叠**, 最干净。

**方案 A「保守·验证留在 3x」** — 验证落 **31–44, 47–48** (跳过主线 45/46)。
留在历史 3x 区, 但: ① 出现 44→47 跳号; ② 41–44 与 panel 内部标签 41–44 同号 (仅装饰性混淆, 不破坏); ③ 数值上仍早于 51 (与全局执行顺序略不符)。

| 现 | 方案B (推荐) | 方案A | shim |
|---|---|---|---|
| 31  | **60** | 31 | bank_fintech_threshold |
| 32  | **61** | 32 | news_llms_human |
| 32a | **62** | 33 | dedup_threshold_sensitivity |
| 33  | **63** | 34 | news_llms_evaluation |
| 34  | **64** | 35 | tone_validation |
| 35  | **65** | 36 | radius_sensitivity |
| 36  | **66** | 37 | entity_masking_test |
| 37  | **67** | 38 | dict_coverage_audit |
| 38  | **68** | 39 | media_diversity |
| 38b | **69** | 40 | decay_sensitivity |
| 39  | **70** | 41 | prompt_sensitivity |
| 39a | **71** | 42 | inter_track_kappa |
| 39c | **72** | 43 | construct_orthogonality |
| 39d | **73** | 44 | lexical_discriminant_validity |
| 39e | **74** | 47 | lm_discriminant_validity |
| 39f | **75** | 48 | cross_media_alpha |

### 3.3 未注册 shim
- `27c → **80**` (落审计/工具 8x band, 去后缀 `c`; 它是 paper-side 审计工具, 不在编排 DAG)。
- `52 / 53` 保留 (无后缀, post-export 工具)。
- (可选) 若要 8x 全归工具: `52→81, 53→82` —— 默认**不动** 52/53 (省 churn)。

---

## 4. 逐文件编辑清单 (shim-only · 方案 B)

**A. 物理改名 (git mv, 保历史) — 35→ 改 23 个** (主线 6 + 验证 16 + 27c 1; 12 个不变):
`git mv 12b_cooccurrence_filter.py 13_cooccurrence_filter.py` … (按 §3 对照表), 验证 16 个 31..39f → 60..75, `27c_*→80_*`。
每个改名文件**同步改其 docstring 首行编号**。

**B. `core/dag.py`**: 23 条 `StageSpec.script` 改字面量 + 对应 `name="阶段NN:…"` 标签数字 + stage45 的 `name` 内 "41+42+43+44+46+47" 内部标签**保持** (仍是 stage45 内部, 不受影响, 仅复核措辞) + 顶部/各 block 注释里的阶段号。

**C. `core/schemas.py`**: `OUTPUT_REGISTRY` 键 (00/11/12/**12b→13**/14→… 共动 6 主线键) + `_OUTPUT_FILENAME_KEYS` 复合键首元同步 + `EXPECTED_NO_OUTPUT_STAGES` (16 验证名全部 31..39f → 60..75)。**注意**: 产物名 (值) **不动**, 仅键 (shim 名) 动。

**D. `run_pipeline_function.py`**: ① `script == '21_tone_llms.py'` (L431) — 21 不变, **无需改**; ② docstring ASCII 流程图 (L12-49) + `run_pipeline()` docstring 的阶段号叙述 → 按新号重画。

**E. `run_pipeline_validation.py`**: docstring 阶段清单 (31..39f) + `run_validation()` docstring + 16 行 `logger.info("  60: …")` 描述 + "16 个验证阶段" 字面量 (数量不变) → 全部按新号重写。⚠ `test_39_prompt_sensitivity.py:142` 在本文件源码搜新号 `'70_prompt_sensitivity.py'`, 须同步。

**F. `run_paper.py`**: **无 NN 阶段引用** (它调度 paper_id, 非阶段)。仅复核 docstring 一致性; 无实质改动。

**G. 测试同步** (§1.4 清单): `test_dag_consistency.py`(含 monkeypatch 复合键) / `test_39a_inter_track_kappa.py` / `test_15_policy_alignment_dual.py` / `test_39_prompt_sensitivity.py` / `test_v3_4_to_v3_5_migration.py`(×2, 含 .exists() 物理路径) / `test_benefit_society_audit_combined.py`(27c→80 .exists()) / `test_papers_common.py`。

**H. 文档/配置一致性 (决策③ 决定取舍)**:
- `paths.yaml`: 行内注释里的 producing-shim 名 (注释, 非键值) + **订正 L83 孤儿注释**。
- `CLAUDE.md`: 流程图 + 目录布局块 + 版本叙述里的 `12b`/`30a`/阶段号; 计数 (35/32/16+16) **不变**, 仅号变。
- `config/*.yaml` 散落的「stage NN」注释 (filtering/sentiment/validation/panel/features/preprocessing)。
- `scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md` 等: 按项目惯例**另起新 dated 文件** supersede, 不就地改。

**I. 不动 (确认)**: golden / 所有 parquet·dta·npy 产物名 / Stata 模板 / papers 代码 / paths.yaml 键值 / `_llm_cache.db` / panel 内部 41-47·25-27 标签 / `52`·`53` / pre-commit hooks。

---

## 5. 执行序列 (原子性 + 验证门)

1. **冻结快照**: `git stash`/记录当前 working tree (注意 git status 已有大量并行会话脏文件——**按文件名精确 stage**, 绝不 `git add -A`)。
2. **一次性落地** B+C+物理改名 (因 `_validate_registry_invariant` fail-fast, 必须同批):
   - 写好 dag.py + schemas.py, `git mv` 全部改名文件, 改各 shim docstring。
   - `python -c "import news_process.core.schemas"` —— import 不抛 `RuntimeError` = 三处一致 ✓。
3. **入口重排** D+E+F。
4. **测试同步** G。
5. **门禁 (本地, $0)**:
   - `python -c "import news_process.core.dag, news_process.core.schemas"` (fail-fast 不变式)。
   - `pytest tests/integration/test_dag_consistency.py tests/integration/test_panel_reproducibility.py -q` (一致性 + golden 复现, 必须全绿)。
   - `pytest -q` 全量 sweep (对照 baseline 2581 passed; 允许的 pre-existing 失败须逐项与基线一致, 0 新增)。
   - `ruff check .`。
   - **离线守卫**: `NEWS_PROCESS_LLM_OFFLINE=1` 防偷跑付费阶段。
6. **文档** H (决策③)。
7. **多智能体终审** (§6)。
8. **提交**: 干净分支, by-name add 仅本任务文件 (排除并行脏文件), HEREDOC + Co-Authored-By trailer; **不 push 除非用户要**。

---

## 6. 多智能体评审 / 验证策略 (用户硬要求)

执行后跑**分阶段 Workflow** (非一次性), 我在每阶段间留在 loop:

- **R1 完整性审计 (fan-out by 维度)**: 每个 agent 各扫一类 —— (a) 残留旧号 grep (全 35 旧 token 在代码区应 0 命中, 仅 docs/memory 允许); (b) dag↔schemas↔物理文件三方一致性逐一核对; (c) 测试断言新号正确性; (d) 入口三脚本 docstring 与 DAG 实际顺序一致; (e) 单调性 & 无后缀 & 无重号 静态校验。
- **R2 对抗复核 (adversarial verify)**: 对 R1 每条「已修正」结论, 独立 agent 试图**证伪** (默认 reject), ≥2/3 通过才采信。重点反验: 有没有漏改的硬编码 shim 名、有没有 import-time 崩、golden 是否真未受影响、有没有把产物名误改。
- **R3 完整性批判 (completeness critic)**: 一个 agent 专问「还漏了什么模态/文件类型没扫」(.do/.tmpl/.yaml/.md/.json/pre-commit/CI)。
- **门禁复跑**: 每轮后复跑 §5 步骤 5 的 pytest + import + ruff, 三次 0 漂移收口。

规模随「最高标准/万无一失」拉满 (R1 ~按文件分片数十 agent, R2 三投票)。

---

## 7. 风险与对策
| 风险 | 对策 |
|---|---|
| 三处 (dag/schemas/物理) 漏一处 → import 崩 | 同批落地 + import 探针 + `test_dag_consistency` 通用一致性网 (L244-285) |
| 漏改某测试硬编码 shim 名 | R1(c) 全量 grep 旧 token + 定向跑相关测试文件 |
| 误改产物名牵动 golden | 硬约束 shim-only; R2 反验 golden 未受影响; 复现 gate 必绿 |
| 并行会话脏文件被裹进提交 | by-name `git add`, 绝不 `-A`; 提交前 `git status` 复核 |
| `.exists()` 物理路径测试 (39c/27c) | 改名后这些测试的路径常量必须指向新名 (G 已列) |
| 26 个 `test_NN_*.py` 文件名漂移 | 决策③: 选改则一并 git mv; 不改则装饰性滞后 (功能无碍) |

## 8. 非目标 (本次不做)
- 不改任何产物/列名 (parquet/dta/npy/xlsx) → golden 不重生, 不跑付费阶段。
- 不动 memory (用户所有)。
- 不拆分 stage45 内部子步为真 shim (Plan-r3 P3-18 另议)。
- 不 push (除非用户明示)。

---

## 9. 决策已全部拍板 (见顶部「用户已拍板」)。§3-§5 的 shim-only 分析作为**耦合模型背景保留**; 实际执行以下文 §10-§14 的 **Scope-Full 执行规范**为准。

---

# Scope-Full 执行规范 (权威, 据 wf_ac44b87f-81d 产物测绘定稿)

## 10. 完整 token 重命名表

### 10.1 shim `.py` (git mv, 23 个; 不变 9 个: 00/11/12/21/22/23/24/46/51)
主线 7: `12b_cooccurrence_filter→13` · `13_materialize_ctx→14` · `14_fintech_intensity→15` · `15_article_policy_alignment→16` · `30a_article_sbert→25` · `18_article_staleness→26` · `45_panel_export_main→40`
验证 16: `31_bank_fintech_threshold→60` · `32_news_llms_human→61` · `32a_dedup_threshold_sensitivity→62` · `33_news_llms_evaluation→63` · `34_tone_validation→64` · `35_radius_sensitivity→65` · `36_entity_masking_test→66` · `37_dict_coverage_audit→67` · `38_media_diversity→68` · `38b_decay_sensitivity→69` · `39_prompt_sensitivity→70` · `39a_inter_track_kappa→71` · `39c_construct_orthogonality→72` · `39d_lexical_discriminant_validity→73` · `39e_lm_discriminant_validity→74` · `39f_cross_media_alpha→75`
未注册 3: `27c_placebo_and_alt_anchor→80` · `52_stata_data_audit→81` · `53_export_stats_excel→82`

### 10.2 产物 (on-disk mv + token 替换)
- `12b_cooccurrence_filtered.parquet→13_…` · `13_news_with_ctx.parquet→14_…` · `14_fintech_intensity.parquet→15_…` · `15_article_alignment.parquet→16_…` · `18_article_staleness.parquet→26_…` · `18_staleness_panel.parquet→26_…` · `30a_article_embeddings.parquet→25_…`
- `32_human_samples.xlsx→61_…`(+`_merged`变体; + 代码 fallback 第三名 `32_news_llms_human_samples.xlsx→61_…`)
- `39c_nmi_matrix_*` / `39c_nmi_null_*` / `39c_nmi_summary.json → 72_…`
- `39d_lexical_discriminant*` / `39d_htmt_matrix*.json → 73_…`
- `39f_cross_media_alpha.parquet→75_…`
- `27c_alt_anchor_and_placebo_panel.parquet→80_…` · `27c_alt_anchor_panel.parquet→80_…`(同族姊妹, 一并)
- **产物不变**: `00/11/12(+full)/21(+full)/22/23/24` · `40_*`(panel 全族含 `.dta`) · `46_*.dta/.do/.xlsx` · `51_*`(parquet+dta) · `27_benefit_*.npy`(×8, 内联无 shim, 保号) · `42_cessation_report.xlsx`(内联诊断, 保号) · 39e eval_reports(在 data/ 下, 不动)

### 10.3 config KEY 名 **保持不变** (output_NN_* 全留旧号)
裁定: 键是**稳定抽象句柄**, 早已与 script/文件名脱钩 (output_15_article_alignment ← script 15_article_policy_alignment.py → 文件 15_article_alignment.parquet, 三号并存)。改键 = 35 call-site churn + 3 个 bracket-subscript KeyError 风险 + `test_lineage_input_contract.py:45` 源码串断言脆断, **零行为收益**。→ **只改 paths.yaml 的 VALUE + 行尾注释; 键名 output_NN 全留**。

## 11. 碰撞铁律 (执行安全约束)
1. **只替换扩展名锚定的完整 token** (`STEM.py` / `STEM.parquet` / `STEM.json` / `STEM.xlsx` / `STEM.csv` / `STEM.log`)。扩展名锚定天然: ① 改到所有**文件名**引用; ② **不碰** config 键 `output_NN`(无扩展名); ③ **不碰** 散文标签 `阶段NN`/`stage NN`(无扩展名)。
2. **绝对禁止裸号替换** (`13_`/`14_`/`15_`/`18_`/`40_`/`39c`/`39d`/`39f`)。裸号与 Stata 论文表模板大面积撞名: `13_table4_*`/`14_table5_*`/`15_table6_*`/`18_table9_*`(~10 paper dirs) + `stata/13_label_*`/`14_label_*`/`15_label_*` + **`40_` 是主面板产物前缀(不动)**。
3. **track-suffix 族** (`_full/_ctx/_ss/_cross/_p95/_p99/_merged`) 用 base-stem 前缀替换自动带走后缀 (e.g. `39c_nmi_matrix`→`72_nmi_matrix` 自动覆盖 `_full/_ctx/_ss/_cross`)。
4. **bare STAGE_NAME 常量** (生产模块内 `STAGE_NAME='14_fintech_intensity'` 等无扩展名) → 扩展名锚定**不覆盖**, **手工**改 (注意用 `(?<!output_)` 思路避免误伤 config 键)。
5. **shim vs product 同 stem 区分**: `39c_construct_orthogonality.py`(shim→72) vs `39c_nmi_*`(产物→72); `30a_article_sbert.py`(shim→25) vs `30a_article_embeddings.parquet`(产物→25)。靠扩展名/全名区分, 勿混。
6. **排除清单 (脚本不得触碰)**: `data/**` · `.git/**` · memory 目录 · `_regen_backup_20260620/**` · `scripts/audit/_runcheck_*/**` · `_logaudit_*/**` · `_rawstats_*/**` · `_replan_*/**` · 已 dated 的审计 `*.md` 快照(supersede 不就地改) · `requirements.txt`(`39f` 假阳)。

## 12. 执行策略 (确定性 + 可审计)
1. **物理改名** (脚本): `git mv` 23 shim; `mv` on-disk 产物 (parquet/xlsx/json; 27c×2; 39c/39d/39f 族; 32_human)。
2. **扩展名锚定 token 替换** (脚本, 先 **dry-run 出逐文件 diff 计数** 复核后 apply): 跑遍 vetted 文件集 (.py/.yaml/.json/.do.tmpl/.do/CLAUDE.md), 排除 §11.6。覆盖: dag.py StageSpec.script · schemas.py 键+值+复合键+EXPECTED_NO_OUTPUT · paths.yaml 值 · golden JSON(键+file字段+missing_stages) · runner.py raw-literal 块 · 全部生产/消费 `.parquet` 字面量 · 全部测试 `.parquet` · stata 模板注释 data 依赖 · papers refs · config 常量 json。
3. **手工 SSOT/标签** (扩展名锚定不覆盖的): dag.py `name="阶段NN:"` 标签(26) + block 注释 · run_pipeline_function/validation docstring 流程图+阶段叙述+`logger.info("60:…")` 行(数量不变) · 生产模块 `STAGE_NAME` 裸 stem(~10 模块) · reporting.py 显示标签(L291-292, 键留) · CLAUDE.md 散文 · config/*.yaml `阶段NN` 注释 · paths.yaml 行尾注释 + L83 孤儿注释订正。
4. **golden**: token 替换即完成 re-key (7 键 + 7 file 字段 + missing_stages 的 30a→25); **counts 不动** (1:1 relabel); on-disk `mv` 7 产物 → 复现 gate 读新名。**禁** `generate_golden_snapshot.py` 全量重生 (会重 hash 命中本机 BLAS/HASHSEED 非确定性)。
5. **外围**: git mv 26 个 `test_NN_*.py`(装饰性, 注意并行脏文件) · 新 dated 审计 doc supersede `PIPELINE_NUMBERED_PY_REFERENCE` · `52/53→81/82`。

## 13. 多智能体验证 (执行后)
- **R1 完整性 (fan-out)**: ① 残留旧 token 全仓 grep (排除 §11.6) 应 **代码区 0**; ② dag↔schemas↔物理文件↔golden 四方一致; ③ 单调/无后缀/无重号 静态校验; ④ 三入口 docstring 与 DAG 实序一致; ⑤ config 键保号正确、值已改; ⑥ STAGE_NAME 裸 stem 全改。
- **R2 对抗 (≥2/3 证伪投票)**: 反验 import 不崩、golden 仅 re-key 未动 hash、产物名未误改 40_/46_/51_/27_benefit、Stata 表号未被裸号误伤。
- **R3 完整性批判**: 还漏哪类文件/模态 (eval_reports 路径串、constants.json、rerun.yaml、papers spec)。
- 每轮后复跑 §5 gates, 三次 0 漂移收口。

## 14. 主控裁定的判断项 (无需再问, 如反对可中断)
- **config 键保号** (§10.3): 降风险, 遵循既有抽象惯例。
- **panel shim 45→40** (产物 40_* 不动): 最小化高频产物 churn 即达对齐。
- **27c→80 且同族 `27c_alt_anchor_panel→80`**: 去后缀 + 全族一致。
- **`27_benefit_*.npy` / `42_cessation_report.xlsx` 保号**: 内联无 shim, 无对齐目标; 仅订正误导注释。
- **39e→74 仅 shim/script, 无 data 产物** (eval_reports/39e_* 在 data/ 下不动)。
- **golden 外科 re-key 不重生**: $0、不触本机 BLAS/HASHSEED 非确定性。

---

# 15. 计划审计修补 (9-agent 对抗审计 wf_d4985592-f9b: **0 P0 / 14 P1 / 17 P2**; 核心策略全部 VERIFIED；以下修补全部并入, 计划升 GO)

> 审计确认 VERIFIED-OK (无需改): 扩展名锚定算法正确(不撞 Stata `13_table4`/`14_label`/`40_panel`)· config 键保号安全 · golden 字节级仅 re-key(列哈希零变, 0 重算) · panel 45→40 无碰撞 · 无 importlib 动态派发 · pre-commit/CI/.gitignore 零旧 token · 26 个新号(60–75/80–82)全仓无占用 · 升序链 12b→13→14→15→16 全 stem 不互为前缀(无误级联) · 监控网真相: `test_dag_consistency` **不**校验物理文件存在(故须独立 gate)。

## 15.1 【P1】生产模块 **裸 stem** 完整手工清单 (扩展名锚定**不覆盖**, 全 27 处; 旧计划 §12.3「~10」严重低估)
**STAGE_NAME 常量 (22, 驱动 setup_logging→`<stem>.log` 文件名)**:
`cooccurrence_filter.py:63 12b_cooccurrence_filter→13` · `ctx_materializer.py:104 13_materialize_ctx→14` · `fintech_intensity.py:135 14_fintech_intensity→15` · `policy_alignment.py:149 15_article_policy_alignment→16` · `article_sbert.py:97 30a_article_sbert→25` · `article_staleness.py:121 18_article_staleness→26` · `threshold.py:105 31_bank_fintech_threshold→60` · `llms_human.py:76 32_news_llms_human→61` · `dedup_threshold.py:122 32a_dedup_sensitivity→62` ⚠**stem 异名**(非 `32a_dedup_threshold_sensitivity`, 按 shim 名搜会漏) · `llms_evaluation.py:103 33_news_llms_evaluation→63` · `tone_validation.py:121 34_tone_validation→64` · `radius_sensitivity.py:116 35_radius_sensitivity→65` · `entity_masking.py:127 36_entity_masking_test→66` · `dict_coverage.py:124 37_dict_coverage_audit→67` · `media_diversity.py:148 38_media_diversity→68` · `decay_sensitivity.py:164 38b_decay_sensitivity→69` · `prompt_sensitivity.py:124 39_prompt_sensitivity→70` · `inter_track_kappa.py:71 39a_inter_track_kappa→71` · `lexical_discriminant_validity.py:90 39d_lexical_discriminant_validity→73` · `lm_discriminant_validity.py:104 39e_lm_discriminant_validity→74` · `cross_media_alpha.py:120 39f_cross_media_alpha→75` · `stata_audit.py:100 52_stata_data_audit→81`
**stage_name= kwarg (5)**: `fintech_intensity.py:693→15` · `policy_alignment.py:1081→16` · `attention_media.py:786 45_panel_export_main→40` · `export.py:339→40` · `export.py:1310→40` (⚠ `controls.py:1072 51_falsification_test` = 51 不变, 勿动)
**setup_logging() 内联裸字面 (3, 无 STAGE_NAME)**: `construct_orthogonality.py:375 39c_construct_orthogonality→72` · `stats_excel.py:78 53_export_stats_excel→82` · `benefit_society_audit_combined.py:382 27c_placebo_and_alt_anchor→80`

## 15.2 【P1】新增/订正产物族 (旧 §10.2 漏列, 须并入重命名 map)
- **订正假述**: 39e **确写** data 产物 → `lm_discriminant_validity.py:325 f'39e_lm_htmt_matrix_{suffix}.csv'`、`:334 f'39e_lm_permutation_{suffix}.csv'` → **base-stem 前缀手工** `39e_lm_htmt_matrix_→74_…`、`39e_lm_permutation_→74_…` (§14「39e 无产物」作废)。
- **35_radius 族 → 65**: `35_radius_label_distribution.png` · `35_radius_correlation_heatmap.png` · `35_radius_sensitivity.tex` · `35_radius_sensitivity*.json` · **`35_radius_sensitivity_llm_results.json`(load-bearing Stata 依赖, `papers/_common/stata_templates/23_tableA4_radius_sensitivity.do.tmpl:18` 真 import)**。
- **37/38/38b 诊断 → 新号**: `dict_coverage.py:888-908` 4 个 `37_*.csv→67_…` · `media_diversity.py:1410 38_media_diversity.xlsx→68_…` · `decay_sensitivity.py:963 38b_decay_sensitivity.csv→69_…` · `stata_audit.py:1154 52_stata_data_audit.csv→81_…`。
- **扩展名锚定集补**: §11.1 加 **`.png` `.tex`**。

## 15.3 【P1】f-string concat / infix 变体 → **显式手工** (锚定 base 匹配不到, 解决 §11.1 vs §11.3 矛盾: **凡 stem 与扩展名间有 `{suffix}`/`_merged` infix 的, 一律列显式手工, 不靠 base-stem auto**)
`lexical_discriminant_validity.py:385 f'39d_lexical_discriminant_{suffix}.parquet'`→`73_lexical_discriminant_` · `:387 f'39d_htmt_matrix_{suffix}.json'`→`73_htmt_matrix_` · `32_human_samples_merged.xlsx→61_human_samples_merged.xlsx` (infix `_merged`) · 39e 两个 f-string(见 15.2)。

## 15.4 【P1】测试裸 stem / 叙述断言手工清单 (auto-sweep 故意不碰)
`test_39_prompt_sensitivity.py:133 '阶段39'→'阶段70'` · `:593 '阶段39'→'阶段70'` · `:177 .find('37_dict_coverage_audit')→'67_…'` · `:178 .find('39_prompt_sensitivity')→'70_…'`(67<70 序仍成立) · `:143 '39_prompt_sensitivity.py'→'70_…'`(注: 实测 L143 非旧计划 §E 的 L142) · **`run_pipeline_validation.py:124-139` 16 行 `logger.info("31:…")…"39f:…"`→`"60:…"…"75:…"`**(automation 完全够不到, 最易错的手工块, 整 16 行核对)。另: 确保 §12.2 auto-sweep 文件集**显式含全 tests/ 树**, 6 个产物字面测试 (test_construct_orthogonality/test_39d_lexical_discriminant/test_omni_fix_runner/test_panel_orphan_merges/test_run_pipeline_function/test_dedup_sensitivity) 与其生产者**同一遍**改, 防 producer↔test lockstep 漂移。

## 15.5 【P1+P2】sweep ROOT 钉死 + 排除清单扩充
- **ROOT 钉死 `news_process/`** (cwd 锚定); **排除同级项目** `Awesome-Agent-Skills-for-Empirical-Research/` · `FinBERT/` · `demo-notebooks/`; 允许集**不含** `.ipynb/.smcl`(已天然排除)。
- §11.6 排除增: `scripts/migrate/**`(冻结迁移图) · `scripts/audit/_omni_fix/**` · `scripts/audit/_*_findings_*.json`(如 `_full_audit_findings_2026-06-16.json`) · **`CHANGELOG.md`**(冻结史实, 单点 revert 锚) · `build/**`(gitignored 抛弃) · 已 dated 审计 `*.md`。
- ⚠ **`.log/.csv` 在 §11.1 锚定集但 §12.2 apply-set 现排除** → 解矛盾: **代码/测试里**的 `.log/.csv` 字面量要改, **磁盘** `logs/*.log` 不 mv(每次运行覆盖, 自愈)。

## 15.6 【P2】文档刷新增项 (非 load-bearing, 但 Scope-Full 一致性要求)
`README.md`(验证阶段树 阶段31-39→60-75 + L114 后缀清单 32a/38b/39a-f/30a→新号; shim 计数仍 35) · `reporting.py:389 显示标签 '模块五: 45_panel_export_main'→'40_…'`(键 output_40_panel_yearly 不变) · `reporting.py:436 docstring 30a→25` · `config/pipeline_v34_rerun.yaml:48 id '14_fintech_intensity'→'15_…' / :51 '15_article_policy_alignment'→'16_…'`(裸 id) · `papers/bank_fintech_attention/{paper_spec.yaml:51,tables.py:31,__init__.py:24}` 裸 'stage 14_fintech_intensity' · `papers/_common/stata_runner.py:822` 显示元组 stem · `tests/test_audit_fixes_20260529.py:4` docstring 'test_34_…'→'test_64_…' · `validation/tone_validation.py:748/763/768` 裸 '32_human_samples'。

## 15.7 【P1】新增 3 道门禁 + 回滚 (旧 §5 不足)
1. **物理文件存在 gate**: 跑 `python -c "import os,news_process.core.dag as d; [print('MISSING',s.script) or exit(1) for s in d.STAGES_MAIN+d.STAGES_VALIDATION if not os.path.isfile(os.path.join('"'"'news_process'"'"',s.script))]"` (或 git ls-files 比对) — **因 test_dag_consistency 不查物理存在, 漏 git mv 会过 import+dag 测试只在 runtime 崩**。
2. **repro 零意外 skip gate**: `pytest tests/integration/test_panel_reproducibility.py -rs`, 7 个改名产物**不得 skip**(漏 on-disk mv → 静默 skip 假绿)。
3. **clean-tree 前置 gate**: 开工前 `git status --porcelain` 须**零 tracked 改动**(审计实测当前树已 clean, 并行改动已提交到 `exec/nonpolarity-dims-2026-06-20`); 若 `attention_media.py/export.py/encode.py/test_omni_fix_attention.py` 等含改名 token 的文件被并行会话弄脏 → 该文件改用 `git add -p` 逐 hunk。
4. **回滚**: **产物 mv 放最后**(全部 tracked 改动过 gate 后再 mv 产物) → 失败时只需 `git reset --hard`/`git checkout` tracked, 无需反向 mv gitignored 产物; 另先把 forward-mv map 落 manifest 备反向。

## 15.8 【P2】on-disk 伴生文件
改名 parquet 的同名伴生 `*.meta.json`(cooccurrence_filter.py:187 自动派生)+ `*.csv` debug 导出一并 mv; `logs/*.log` 不 mv(自愈); eval_reports 诊断 csv 由生产者字面改名后下次运行自动落新号(旧文件成无害孤儿)。

## 15.9 【P3】可选/留意
`test_25_audit.py` 头注引用已删 `25_strategic_differentiation.py`(陈旧遗留, 新 shim 25=article_sbert; 功能无碍, 可选顺手退役) · dag.py stage 40 的 name 标签「(内含 41+42+43+44+46+47)」 父号 40 < 子标签 41-47(纯展示, 刻意保留)。

---

# 16. 终整合 (round-2 终审 wf_930f26cb-b4f: **0 P0 · CONVERGED**; 本节为最终执行权威, 与 §10–§15 冲突处以本节为准)

> 终审裁决: **GO_WITH_FIXES → 一次性 fold-in 即 GO**; 边际发现曲线已收敛(R2 仅新增 1 处零散字面 + 6 处测试断言 + 6 处文档层矛盾, 0 逻辑错误); §15.1 的 27 处裸 stem **逐条 100% 对代码核实无误**; 核心策略(扩展名锚定/config 键保号/golden 外科 re-key/panel 45→40)**全部 VERIFIED**。**勿再加审计轮次**(收益递减)。

## 16.1 消解 §10–§15 的 6 处内部矛盾 (按本节为准)
1. **39e 确写产物 (§14/§10.2「39e 无产物」**作废**)**: `lm_discriminant_validity.py:325 f'39e_lm_htmt_matrix_{suffix}.csv'`、`:334 f'39e_lm_permutation_{suffix}.csv'` → **infix 显式手工**改前缀 `39e_lm_htmt_matrix_→74_…`、`39e_lm_permutation_→74_…`(§15.2 措辞「base-stem 前缀手工」**订正为「infix 显式手工」**)。
2. **扩展名锚定集 = 8 个 (订正 §11.1 的 6 个)**: `.py / .parquet / .json / .xlsx / .csv / .log / **.png** / **.tex**`(`.png/.tex` 为 35_radius 图/表所必需)。
3. **`_merged` / `{suffix}` infix = 显式手工 (订正 §11.3「auto 带走」)**: 凡 stem 与 `.ext` 之间夹 infix 的文件名都是独立 full token, 扩展名锚定**匹配不到**, 必须 §15.3 显式列。**例外**: `32_..._merged.xlsx` 与 `*.meta.json`/`*.sidecar.json` 是运行时由 base 动态派生(`os.path.splitext(base)+'_merged'+ext`), **无独立代码字面量**, 改 base(§10.2 已含)即自动带走, **无需手工**(§15.3 该项是「结果名」非「待改字面」)。auto-carry **仅**适用于 base-stem 后**紧跟轨后缀再接扩展名**且按 base-stem 子串替换者(如 `39c_nmi_matrix`→`72_nmi_matrix` 带走 `_full/_ctx/_ss/_cross`)。
4. **唯一权威排除清单 (合并 §11.6 + §15.5)**: `data/**` · `.git/**` · memory 目录 · `_regen_backup_20260620/**` · `scripts/audit/_runcheck_*/**` · `_logaudit_*/**` · `_rawstats_*/**` · `_replan_*/**` · `scripts/migrate/**` · `scripts/audit/_omni_fix/**` · `scripts/audit/_*_findings_*.json` · `CHANGELOG.md` · `build/**` · 已 dated 审计 `*.md` · `requirements.txt` · 同级项目 `Awesome-Agent-Skills-for-Empirical-Research/` `FinBERT/` `demo-notebooks/`;**ROOT 钉死 `news_process/`**。
5. **执行序拆分 (订正 §12.1「mv STEP 1」vs §15.7.4「mv LAST」)**: **1a** `git mv` 23 tracked shim(连同所有 tracked 编辑: dag/schemas/paths.yaml 值/golden JSON re-key/全部 token 替换/手工 stem) → 过 tracked gates → **1b(最后)** `mv` gitignored on-disk 产物 → 跑 repro `-rs` gate(改名产物零 skip)。**golden JSON re-key 属 tracked 编辑在 1a; parquet mv 属 gitignored 在 1b**。
6. **裸号禁替换增 `25_`/`26_` (补 §11.2)**: 25_/26_ 被 Stata 表前缀占用(`25_tableA6/A8/A12.do`、`26_tableA7/A13.do`, 全 `.do`-anchored, 与新 `.py/.parquet` 产物异 token, 算法层无碰撞)。⚠ §15 header「26 个新号全仓无占用」**仅指验证号 60–75/80–82**; MAIN-line 新号 13/14/15/16/25/26/40 中 **25_/26_ 确被 Stata .do 表占用**, R1 forward-check 须**白名单** `25_table*`/`26_table*`。

## 16.2 R2 新发现的手工编辑项 (并入 §15.4 测试清单 + §15.6 文档清单)
**新增「生产者源码叙述 stage/Stage NN」类 (扩展名锚定够不到, 驱动运行期文本 + 测试断言, 须 producer 与 test 同改)**:
- `herd_decay.py` 警告字面 **`'stage 13'→'stage 14'`**(多处, ~L54/56/60/467/470/492-494)+ 配套测试 `test_24_herd_decay_dual.py:196` + `test_omni_fix_herd.py:258`。
- `codebook.py` `source_stage` 标签 **`'Stage 45 …'→'Stage 40 …'`**(全部 ~50 处含 L404/597/1632/1634 fallback)+ 配套测试 `test_omni_fix_codebook.py:133/139/145`。⚠ `:149 'Stage 21'` **不动**(21 不变); `codebook.py:1636 'Stage 25'`(strat 内联, 历史退役模块)与新 shim 25=article_sbert 语义撞号 → **纯描述性 metadata, 列为 §15.9 可接受残留**(可选订正为 'Stage 40 (panel/strategic_diff inline)')。
**新增零散字面 (Scope-Full 一致性, 顺带修 latent bug)**:
- `pipeline/panel/export.py:109` 读 `'38_decay_sensitivity.csv'`(陈旧错名, 生产者实写 `38b_…`)→ **`69_decay_sensitivity.csv`**(同时修好 G-14 块找不到产物的 pre-existing bug)。
- `validation/dict_coverage.py:695`(docstring)`/:718`(log 串)+ `test_omni_fix_val_robust.py:263` 的 `'37_false_negative_estimate.csv'`(死路径, 从不生成)→ `'67_…'`(纯叙述/log, 清 R1 残留)。
- `test_papers_common.py:144` 裸 `'45_panel_export_main'`(无 .py)→ `'40_panel_export_main'`(L123/124 的 `.py` 形已被 auto-sweep)。
- `35_radius_sensitivity_llm_results.json`(**订正 §15.2 误attr**): 该字面**全仓仅存在于** `papers/_common/stata_templates/23_tableA4_radius_sensitivity.do.tmpl:18`(读侧, capture-confirm 守卫)+ 计划; **无任何 .py 生产者**(`radius_sensitivity.py:1333` 写的是 `35_radius_sensitivity.json` 另一文件)→ 仅需把**模板:18** 该字面手工 `35→65`; 别指望 base-stem auto 命中。

## 16.3 R1 forward-check (执行后残留 token grep) 白名单 (防 §13-R1① 假 RED)
以下旧号 token **刻意保留**, 残留 grep 须排除: `40_*`/`46_*`/`51_*`/`42_cessation`/`27_benefit_*`(产物不变) · `25_table*`/`26_table*`/`13_table4*`/`14_table5*`/`15_table6*`/`18_table9*`(Stata 表号, 异 namespace) · `stata/1[1-5]_label_*.do`(标签脚本) · golden hash **值**内含 `39c…/39d…/39f…` 十六进制子串(如 `39cfb1b3…`, 非文件名, 扩展名锚定不碰) · `radius_sensitivity_llm.py:283 {'stage':'35_radius_sensitivity_llm'}`(metadata 值非路径) · `runner.py:345-346` 注释裸 token · `CHANGELOG.md`/`migrate_data_layout.py`/`_omni_fix`/`_*_findings_*.json`(冻结史实)。

## 16.4 收敛证据 (供用户判断「是否够」)
R1(9-agent): 0 P0 / 14 P1 / 17 P2 → 全 fold-in §15。 R2(7-agent): 0 P0; §15.1 100% 核实; fstring-hunt=GO(无遗漏类); convergence-redteam=**CONVERGED**(新号空间实测无占用, 升序链 stem 互不为前缀, golden 仅 re-key); 仅新增 1 零散字面 + 6 测试断言 + 6 文档矛盾(全 fold-in §16)。**每轮新增实质问题数 → 0; 策略零返工。** 终审建议: 「proceed to execute; no further audit round needed」。

---

# 17. 终审定稿 (round-3 终极验证 wf_3c0d4414-e67: **0 P0 · CONVERGED**; 本节最高执行权威)

> 终裁: **GO_WITH_FIXES → 本节 fold-in 即 GO**; §16 经独立核验**内部自洽、6 矛盾真消解、token map 1:1 无歧义**; 核心机器(扩展名锚定/SSOT import-fail-fast/golden 外科 re-key/1a-tracked·1b-gitignored mv 序/$0·clean-tree·repro-rs·physical-file gates/rollback)**全部 VERIFIED 可单操作员零歧义执行**; clean-tree 前置实测当前 HOLDS。**第 4 轮审计 = 纯收益递减, 终裁明示「not warranted」。**

## 17.1 【P1·本轮最有价值发现】重定义 R1① 残留 gate — 旧/新号空间**重叠**, 「全 35 旧 token 残留=0」机械上**不可达**
- **根因**: 旧 stage-13(ctx_materialize)→14, 但**新** stage-13=cooccurrence_filter; 裸 `grep 'stage 13'` **无法区分**「陈旧注释(应改 14)」与「正确的新引用(指 cooccurrence)」。14→15、15→16、18→26、45→40 同理。实测生产 *.py 内 'stage 13'=153、'stage 14'=57、'stage 15'=61、'Stage 45'=61 处。
- **R1① 重定义 (替代 §13-R1①/§15.5 的「代码区 0 残留」)**: R1 改为 **POSITIVE grep** —— 只断言下列**载荷 token 类**已 100% 迁移: ① 扩展名锚定文件名 token(`STEM.{py,parquet,json,xlsx,csv,log,png,tex}`); ② STAGE_NAME/stage_name=/setup_logging 裸 stem(§15.1 全 27 处); ③ §15.4+§16.2 列举的 test/producer-narrative lockstep 项(herd_decay 'stage 13'、codebook 'Stage 45' 等)。**不再**对全部裸号叙述做「残留=0」硬断言。
- **门禁判据**: 上述 3 类残留=0 即 R1 GREEN; 纯注释/docstring/logger 横幅的 `'(stage|阶段) NN'` **不计入** load-bearing gate。

## 17.2 叙述注释层政策 (~500 处纯注释/横幅)
- **定级 P3 cosmetic, 非 gate-critical, 不破任何测试**(扩展名锚定 §11.1③ 故意不碰)。
- **清理 = best-effort 可选, 且必须逐阶段人工判断, 严禁机械 grep-replace**(重叠会把「正确新引用」误改)。Scope-Full 决策③「一致」对此类按**尽力而为**处理, 不阻断执行/提交。
- 若执行: 按**单个改名阶段**逐一甄别其旧号叙述(借 §15.1 的精确文件清单缩小范围), 非全局替换。

## 17.3 codebook 计数订正 + test-lock
- `codebook.py` `'Stage 45'` 实为 **61 处**(非 §16.2 的「~50」)→ 指令改为「**grep-all 全 61 处** `'Stage 45 …'`→`'Stage 40 …'` 逐一改」, 勿当 ~50 预算停手。`:149` 行号引用作废(实为 `_AUTO_INFER_NOTE`; 'Stage 21' 真实标签在 499/516/578/693/721/751 等, **保留不动**)。
- `codebook.py:1636 'Stage 25'`(退役 strat_diff 内联)被 `test_omni_fix_codebook.py:152` **硬锁**(`assert ...=='Stage 25'`)→ **留 as-is**(§15.9 可接受残留); 「可选订正 Stage 40」**不安全**(须连改该 test), 默认**不动**。

## 17.4 补漏 (并入 §15.3/§15.6 手工清单)
- **infix 漏网 (载荷)**: `papers/_common/stata_templates/bank_fintech_substance/21_substance_clarity_robustness.do.tmpl:64` 的 `39d_htmt_matrix.json`(`_matrix` 后**紧接** `.json`, 无尾下划线 → §15.3 的 `39d_htmt_matrix_` 前缀**匹配不到**)→ 显式 `→73_htmt_matrix.json`(+ 同行叙述 stage 39d→73)。
- **.sh 文件类型**: `scripts/audit/round1_triple_run.sh:22-24` 硬编码 3 个改名 parquet(`13_news_with_ctx`/`14_fintech_intensity`/`15_article_alignment`)→ **二选一**: 入 §16.1.4 排除清单(audit 一次性驱动, 优雅退化为假 MISS, 非生产 DAG), 或手工改 3 行 →14_/15_/16_。**`.sh` 不入自动 sweep 允许集**。
- **shim body 交叉引用**(首行号规则 + 自动 sweep 都够不到): `13_materialize_ctx.py:2` 正文「供 stage 14/15」→「stage 15/16」; `39c_construct_orthogonality.py:5` 「39c 紧跟 39a/39 … 避开 40 panel_export」→「72 紧跟 71/70 …」(纯注释)。
- **§15.7.1 physical-file gate**: 须**从 repo root 跑**(`cwd=f:/WiseSearch/data_antigravity_project/`; `os.path.join('news_process',s.script)` 仅 repo-root 解析); 或改 `Path(__file__)` 锚定。
- **§16.3 白名单**扩 `25_*.do.tmpl`/`26_*.do.tmpl`(除 table 外尚有 `25_collab_ppml`/`25_locus_era_stability`/`26_substance_era_stability` 等; 实际无碰撞因 25/26 是 target 非 source, sweep 只匹配 source token, 本就不碰——仅文档清晰化)。

## 17.5 收敛声明 (供用户判断「是否够」)
- **3 轮对抗审计 0 P0**; gate-critical(test-asserted lockstep)叙述子类 **CONVERGED**(无第三处, pytest gate 安全); 核心策略零返工。
- 本轮新增实质项 = 2 P1(R1-gate 重定义 + codebook 计数)+ 3 P2(infix/sh/test-lock)+ 余 P3 cosmetic, **全 golden-safe、不破 pytest/repro gate**。
- 终裁原话: **「A 4th audit round is pure diminishing returns and is NOT warranted … fold in … then EXECUTE.」** 计划至此 **GO**。

---

# 18. 行号精校 (round-4 建构式 dry-run + 冷启动 fresh-eyes wf_2f8fbcec-66c: **0 P0 · FLOOR REACHED**; 最高执行权威)

> 终裁: **GO_WITH_FIXES → 本节精校即 GO**。本轮换用**建构式模拟**(实际构造执行者的 token map + 手工清单)+ **冷启动 fresh-eyes**(不看计划独立重导): ① 构造的 token map **零载荷 gap、零死条目、1:1 无碰撞**(target shim 40/25/26/60-82 实测全 FREE; schemas import 干净); ② 冷启动审计**只重新发现已覆盖类别**(eval_reports 产物 / runner `_OPTIN` 字典 / Stata 表号碰撞 三个「新」类全在 §15.4/§16/§17 已处理)——**收敛实锤**; ③ 上轮疑似 infix-asymmetry(39d bare full-track)**经查证伪**(`:384/:386` 是 stem+紧接 `.ext`, 扩展名锚定**够得到**, 非 infix)。**第 5 轮纯浪费**(原话 "pure waste")。本节仅修若干行号 off-by-one/幻影项(执行者首次 Read/Edit 即自纠):

## 18.1 行号/计数精校 (并入对应手工清单)
- **herd_decay.py `'stage 13'` 实为 12 处**(穷举, 替代 §16.2 的「~7 处」): L54/56/60/429/467/470/472/492/494/501/503/852 **全部** →`'stage 14'`(`test_omni_fix_herd.py:258` 是 presence-grep, 漏一处则半改而测试仍假绿 → **必须穷举**)。配套 `test_24_herd_decay_dual.py:196-197` + `test_omni_fix_herd.py:258` →`'stage 14'`。
- **`core/reporting.py` 显示标签订正**(§15.6 的 `:436 30a→25` 是**幻影**, reporting.py 仅 429 行且无 '30a' token, **删除该项**): 真实 4 处 = `L291 '模块二: 12b_cooccurrence_filter'→13` · `L292 '模块二: 14_fintech_intensity'→15` · `L389 '模块五: 45_panel_export_main'→40` · `L390 '模块五: 45_article_bank'→40`(均元组首元显示标签; 第二元 `output_NN` 键**保留**)。
- **`test_v3_4_to_v3_5_migration.py` 实为 ×1 非 ×2**(根级 `tests/test_v3_4_to_v3_5_migration.py` **不存在**, 仅 `tests/integration/` 一份; 其 `:41 '39c_construct_orthogonality.py'` 是 `.py` 扩展名锚定→自动 sweep→`72_`, 配 §15.7.1 physical-file gate 双保)。
- **`run_pipeline_validation.py` logger 块 = L125-139**(非 §15.4 的 L124-139; **L123 是 header `'📖 16 个验证阶段说明'`, 其字面 `16` 被 `test_39_prompt_sensitivity.py:138` 断言, 保留不动**; L124 空行)。16 行 `'31:'…'39f:'`→`'60:'…'75:'`; 配套 docstring L8-24 `'阶段31'…'阶段39f'` + `:133/:593 '阶段39'→'阶段70'`。
- **载荷遗漏补 1 处**: `core/dag.py` panel-spec 的 name 标签 `'阶段45 (内含 41+42+43+44+46+47)'` → `'阶段40 (...)'`(内部 41-47 **保留** per §15.9; 此项按 `'阶段45:'` 键 grep 会漏, 故显式列)。
- **shim-body 交叉引用行号** off-by-one 订正: `13_materialize_ctx.py` 实 **L3**(非 §17.4 的 L2)· `39c_construct_orthogonality.py` 实 **L6**(非 L5)。无害。

## 18.2 冷启动审计独立证实(供用户判断「是否够」)
冷启动 reviewer(**未读计划、未见前 3 轮**)独立枚举 14 类引用 + 风险, **全部落入计划已覆盖范围**, 0 个未知载荷漏洞; 其点名「最危险易漏类」(无 config-key fallback 的硬编码 parquet 字面: `article_staleness.py:540/581/597/610`、`article_sbert.py:265/311`)**已在 §10.2/§15 覆盖**(扩展名锚定 `.parquet` 自动命中)。

## 18.3 四轮收敛终判
- **4 轮对抗审计 · 每轮 0 P0**; 边际新发现:R1(14 P1)→R2(2 P1)→R3(2 P1)→R4(**0 载荷 P1, 仅 4 行号 P2 + P3 cosmetic**)。
- 4 个独立 Phase-1 reviewer **收敛于同一核心机器**(扩展名锚定 + 裸号禁替 + KEEP 白名单 + SSOT import-fail-fast + golden 外科 re-key + 链移 temp-name 序 + POSITIVE-grep R1), **零互斥载荷断言、零新 P0/P1**。
- 终裁原话: **「Proceed to execution. A 5th round is PURE WASTE … the gate-critical lockstep is VERIFIED stable across rounds §10-17.」**
- **计划 GO; 剩余保障来自执行内置 gate + 执行后 R1/R2/R3, 而非再审。**
