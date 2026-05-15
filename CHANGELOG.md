# CHANGELOG — news_process 架构重整记录

按 Phase 演进记录全部架构改动。每个 phase 末打 git tag，单点 `git revert <hash>` 可回滚任意子任务。

格式: 每个 phase 标 (a/b/c/...) 子任务，含 commit hash、LOC 净改动、关键决策。

---

## [Unreleased / post-v3.2.0 multi-paper extension] — 2026-05-15 (commit 8d33c46)

**Scope**: 把 4 个衍生论文 (benefit_society / brokerage_network / strategic_diff / llm_peer)
从"Python 骨架 + 单文件 Stata"补齐到与主线 bank_fintech_tone 对称的成熟度：
3 新 `_common` 模块 + 32 Stata templates + 10 双语 manuscript 骨架 + 4 新测试文件。

### ✨ Added — _common 三个新模块

- **`papers/_common/derivative_replication.py`** (245 LOC): 衍生论文复现包 orchestrator
  - `build_derivative_replication_package(paper_id, overrides=None, ...)` 一键打包
  - `_PAPER_DEFAULTS`: 4 衍生 paper 的 Tier 2/3 占位符默认 (PAPER_ID / MAIN_DV /
    CONTROLS / CLUSTER_VAR / HET_VAR + 各 paper 专属如 ATTITUDE_VAR / MAIN_ENDOG /
    BARTIK_IV / LLM_PEER_IV / CUTOFF_VARS 等)
- **`papers/_common/stata_postprocess.py`** (340 LOC): Stata esttab 输出后处理
  - `parse_esttab_csv()`: CSV → DataFrame[variable → model → Coefficient(value, se, stars)]
  - `to_markdown_table()` / `to_latex_booktabs()`: 发表级渲染
  - `read_paper_esttab(paper_id, csv_filename)`: paper-aware 路径解析
- **`papers/_common/paper_figures_ext.py`** (279 LOC): 论文级 matplotlib 图表助手
  - `coefplot_from_esttab_df()` (系数图 + 95% CI)
  - `forest_plot_from_esttab_df()` (异质性 forest)
  - `event_study_plot()` (TWFE 动态)

### ✨ Added — stata_runner.py 占位符 3-tier 系统

- **Tier 1 (universal, 已存在)**: `MAIN_LOCUS_TRACK` / `MAIN_SUBST_TRACK` /
  `MAIN_SENT_TRACK` / `PROJECT_ROOT`
- **Tier 2 (paper-level, 新)**: `PAPER_ID` / `MAIN_DV` / `CONTROLS` /
  `CLUSTER_VAR` / `HET_VAR`
- **Tier 3 (paper-specific, 新)**: paper-particular keys
  (`ATTITUDE_VAR` for benefit_society, `MAIN_ENDOG`/`MAIN_IV` for
  brokerage_network, `BARTIK_IV`/`COHERENCE_VAR` for strategic_diff,
  `LLM_PEER_IV`/`CUTOFF_VARS` for llm_peer, etc.)
- `build_replication_package(paper_id='bank_fintech_tone', ...)` 新 paper_id 参数
  (backward-compat 默认值保持原行为)
- `_VALID_PAPER_IDS_BUILD` 白名单 (5 paper)

### ✨ Added — 32 Stata templates (4 paper × 8)

- `_common/stata_templates/benefit_society/` (8 .do.tmpl + README)
- `_common/stata_templates/brokerage_network/` (8 .do.tmpl + README)
- `_common/stata_templates/strategic_diff/` (8 .do.tmpl + README)
- `_common/stata_templates/llm_peer/` (8 .do.tmpl + README)
- 每 paper 模板结构: `00_master / 01_data_prep / 10_table1_descriptives /
  11_table2_main_* / 12_table3_* / 13_table4_heterogeneity /
  14_table5_robustness / 30_figure1_*`

### ✨ Added — 10 manuscript skeletons (5 paper × en/zh)

- `papers_assets/<paper>/drafts/{en,zh}/manuscript.tex` × 10 (8 节标准结构 + V6 F1-F4 方法学注入)
- `papers_assets/<paper>/drafts/{en,zh}/refs.bib` × 10
- `papers_assets/_shared/preamble_{en,zh}.tex`: 共享 LaTeX 前置
- `papers_assets/_shared/README.md`: 共享资产说明

### ✨ Added — 4 paper-level README

- `papers_assets/{bank_fintech_tone,benefit_society,brokerage_network,strategic_diff}/README.md`
  (新建, 镜像 llm_peer/README.md 结构)
- `papers_assets/llm_peer/README.md` 更新为 P0-P4 状态描述 (移除"骨架"自报)
- `papers/llm_peer/__init__.py` 模块级 docstring 同步更新 (移除"骨架"残留)

### ✨ Added — 4 新测试文件 (+242 tests)

- `tests/test_derivative_replication.py` (+48 tests, 274 LOC)
- `tests/test_stata_postprocess.py` (+41 tests, 312 LOC)
- `tests/test_paper_figures_ext.py` (+20 tests, 221 LOC)
- `tests/test_manuscripts_structure.py` (+126 tests, 253 LOC)

### 📋 各 paper Python 包扩展

- `papers/<paper>/tables.py` × 4 衍生 paper: 加 `build_table2_main` /
  `build_table3_*` / `build_table4_heterogeneity` / `build_table5_robustness`
  (读 Stata esttab CSV → DataFrame)
- `papers/<paper>/figures.py` × 4 衍生 paper: 加 `plot_main_*_coefplot` /
  `plot_*_forest` 或 `plot_n_sensitivity_coefplot`
- `papers/<paper>/analysis.py` × 4 衍生 paper: `--stage tables/all` 阶段调度
  Table 2-5 (含 FileNotFoundError skip pattern)

### 🧪 测试基线演进

| 版本 / commit | passed | skipped | 增量来源 |
|---|---|---|---|
| v2.1.0 frozen | 814 | 2 | (历史) |
| v3.2.0 release | 1144 | 6 | +150 dual-track + Stata layer + 14 templates |
| 8d33c46 (HEAD) | **1388** | 6 | +242: derivative_replication (+48) + stata_postprocess (+41) + paper_figures_ext (+20) + manuscripts_structure (+126) + 其它 (+7) |

### 🛡 Backward compat

- `bank_fintech_tone` 主线 (Tier 1 only) 路径完全未受影响
- 既有 73 stata_templates tests 继续 pass
- `build_replication_package(main_spec_choices)` 旧调用方式不变

### 🚧 仍待用户补充

- 10 manuscript 内 `\NoteThis{...}` 实质内容 (Intro / Lit Review / Results 等)
- 会计变量 (ROA / NPL_ratio / Z_score / Tobin_Q) 并入 `40_panel_yearly.parquet`
- 32 .do 端到端跑通 (依赖上一项)
- LaTeX xelatex 真实编译 (Q1.1a/b CI 接管中)

---

## v3.2.0 / 2026-05-15 — BREAKING: Stage 3 双轨化 + Stata 数据导出层 (62 轮 plan 审计 + 7 milestone 自动执行)

**Plan v14**: 62 轮极致审计（v1-v14 累计）+ 68 项 finding 全部修复 + 9 项 Action Items 用户书面确认 → M0-M6 自动化执行 + 7 轮 M1 自审收敛。

### 🔥 BREAKING Changes

- **stage 21 输出列重命名**:
  - `innovation_locus` → `innovation_locus_full` + 新增 `innovation_locus_ctx`
  - `innovation_substantiveness` → `innovation_substantiveness_full` + 新增 `innovation_substantiveness_ctx`
  - `category_confidence` → `category_confidence_full` + 新增 `category_confidence_ctx`
- **stage 21 新增 dual gate 三互斥指示列**: `llm_verified_dual_full_only` / `llm_verified_dual_ctx_only` / `llm_verified_dual_both`
- **stage 21 ctx gate 致命修复** ([tone_llms.py:1416](news_process/pipeline/sentiment/tone_llms.py#L1416)):
  原 `df[df['llm_verified_full'] == True]` 让 ctx 轨样本完全 conditional on full →
  改为并集 `verified_full | verified_ctx`，使 ctx 轨独立可作 main spec
  （Hassan 2019 QJE entity-proximity independence; plan v14 §3.1 P1 R1-A 修复）。

### ✨ Added — Stage 3 双轨化

- **stage 21 双轨独立产出**: `_aggregate_track` 同时对 full / ctx 轨道运行
  - majority vote 平局策略**完全对称** (locus 平局→应用场景；substantiveness 平局→象征性)
  - canonicalize_topic(topics_full / topics_ctx) **双轨独立**关键词分类器交叉验证
  - +0.2 / ×0.5 confidence 调整双轨独立适用
- **方法学锚定** (plan v14 §1):
  - Hassan et al. (2019, QJE) entity-proximity attribution for firm-level multidim measures
  - Sautner, Van Lent, Vilkov, Zhang (2023, JF) firm × topic 邻近化
  - Bingler, Kraus, Leippold, Webersinke (2022, FRL) substantive vs cheap talk
  - Westphal & Zajac (1994, 1998, ASQ) substantive-symbolic 框架
  - Gomber, Kauffman, Parker, Weber (2018, JMIS) enabling tech vs business function

### ✨ Added — Stata 数据导出层 (Stage 46)

- **新建 stage 46** `news_process/pipeline/panel/stata_export.py` + thin shim:
  - `encode_categorical_columns`: 中文 str → byte 0/1 (**R32-B 编码方向**: 0=baseline, 1=对照)
  - `build_variable_labels`: ≤ 80 字符英文标签（含 codebook 集成 + heuristic fallback）
  - `assign_core_columns`: core ≤ 2048 (Stata IC license 兼容, **R42-A**)
  - `validate_stata_compat`: 列名 ≤ 32 + label ≤ 80 字节双校验
  - `write_labels_do_file`: 生成 labels.do (label var + define + values)
  - `export_panel_to_stata`: 主入口产 core/aux/full .dta + labels.do + codebook.xlsx
- **Value labels 双语** (plan v14 普通人版变更 20):
  - `locus_lbl`: `0 "底层技术 (Technology)" 1 "应用场景 (Application)"`
  - `subst_lbl`: `0 "实质性 (Substantive)" 1 "象征性 (Symbolic)"`
- **依赖**: pyreadstat>=1.2 (跨平台无 Stata license)
- DAG 集成: STAGES_MAIN 12 → 13；OUTPUT_REGISTRY +5 文件登记

### ✨ Added — Panel 双轨对角线子集 (M2 P2 加性)

- encode.py `_lc × _ctx` 对角线子集列追加:
  - `n_articles_{tech,app}_lc_ctx` + `llm_vote_tone_{tech,app}_lc_ctx` + `llm_prob_score_{tech,app}_lc_ctx`
  - `tech_frac_lc` / `app_frac_lc`
  - `tone_gap_tech_app_lc_ctx` (含 min ≥ 5 防御)
- encode.py `_sc × _ctx` 对角线 (W&Z + Hassan QJE):
  - `n_articles_{sub,symb}_sc_ctx` + `llm_vote_tone_{sub,symb}_sc_ctx`
  - `sub_frac_sc` / `symb_frac_sc`
  - `tone_gap_sub_symb_sc_ctx`
- **加性策略**: 现有 `_tech` / `_app` / `_sub` / `_symb` 列保留（语义 = `_lf × _full` + `_sf × _full`），
  完整 BREAKING 重命名延至未来版本与 golden baseline 重生成同期完成。

### 🧪 Test baseline

- **994 → 1011 passed** / 2 skipped / 0 failed (+17 测试)
  - +6 `test_stage3_dual_track.py`：双轨独立性、平局对称、空票回退
  - +11 `test_stata_export.py`：编码方向、长度限制、core ≤ 2048、labels.do
- DAG 一致性 17 测试全绿

### 📁 Changed — touched files (M0-M6)

| File | Change | Lines |
|---|---|---|
| `pipeline/sentiment/tone_llms.py` | M1: 双轨标签 + ctx gate 并集 + dual gate 指示列 | +128 / -61 |
| `pipeline/panel/encode.py` | M1: 引用更名 _full; M2 P2: _lc × _ctx + _sc × _ctx 对角线 | +71 / -2 |
| `pipeline/panel/runner.py` | M1: 引用更名 _full (M2 P3 4-way 后续)| +3 / -1 |
| `config/schemas.yaml` | M1: 9 双轨/dual gate required_columns 注册 | +12 / -2 |
| `pipeline/panel/stata_export.py` | M6: 新建 (300 行) | +319 |
| `46_stata_export.py` | M6: thin shim (8 行) | +9 |
| `core/dag.py` | M6: StageSpec(46_stata_export.py) 注册 | +9 |
| `core/schemas.py` | M6: OUTPUT_REGISTRY 5 文件 + 复合键 5 条 | +15 |
| `pyproject.toml` | M6: + pyreadstat>=1.2 | +5 |
| `tests/test_stage3_dual_track.py` | M1 audit: +6 双轨独立测试 | +130 (新建) |
| `tests/test_stata_export.py` | M6: +11 stata_export 测试 | +160 (新建) |
| `tests/integration/test_dag_consistency.py` | M6: stage count 12 → 13 | +9 / -9 |

### 📋 Action Items (用户已确认)

1. ✅ Scope = Recommended
2. ✅ BREAKING (v3.0.0 先例)
3. ✅ main spec 由论文 Methods 决定
4. ✅ stage 33 扩展 (不新建 33b)
5. ✅ mean 对角线 + count 4-way
6. ✅ ctx gate 并集 + 3 指示列
7. ✅ Git tag plan-stage3-dual-track-frozen + v3.2.0
8. ✅ 6 PR 分批 + xfail 单调递减
9. ✅ Stata scope = Recommended (stage 46 + 14 模板预留)

### ✅ 累计完成 Phase (本次 14 commit 总览)

| Milestone | 内容 | Commit |
|---|---|---|
| M0 | feature branch + plan-stage3-dual-track-frozen tag | (git op) |
| M1 | tone_llms.py 双轨化 (BREAKING) + ctx gate 致命修复 (R1-A) | 2070e52 |
| M1 audit | 双轨独立性测试 (+6) + 注释消歧 | f3d3cc9 |
| M2 P2 | encode.py _lc × _ctx + _sc × _ctx 对角线追加 | 73c4d65 |
| M6 stage 46 | stata_export 新建 (300 行) + 11 测试 | 5a21614 |
| M6 DAG | stage 46 注册 + DAG 一致性测试更新 | 0d4a4cc |
| docs init | CHANGELOG + CLAUDE.md baseline | 16bc60d |
| M3 P4 | iv_did.py Bartik IV 双套独立 (lf / lc) | e67cc66 |
| docs fix | 180k → 10.5k LLM 调用估算更正 (17× 高估) | b4c5245 |
| M2 P3 | runner.py 洗稿率 count 4-way (+16 篇章列) | fdfc470 |
| M4 codebook | +13 双轨 VariableMetadata 条目 | 116ba0e |
| M5 P5.2 | stage 35 radius_sensitivity LLM 接口 + 10.5k 估算 (+9 测试) | (next) |
| M6 templates | 3 核心 Stata .do.tmpl + README 双语 (+14 测试) | (next) |
| M7 | build_replication_package 一键打包 (+12 测试) | (next) |
| M4 docs | 3 方法学文档 + 列名迁移 CSV | (next) |

### ⏳ 余下后续工作 (v3.2.1 或同 release)

- M5 第 2 commit: stage 35 LLM 实际 10.5k API launch (需 yunwu API key)
- M6 11 个剩余 .do.tmpl (01_data_prep, 10_table1, 12-13 mechanism/heterogeneity, 20-23 robustness, 30-31 figures)
- 完整 BREAKING 重命名 (`_tech` → `_tech_lf` 等显式化, 现为加性策略保 baseline)
- Golden baseline 重生成 (需完整 pipeline 跑通)
- `git tag v3.2.0` (代码完整后)

### 📊 累计统计 (v3.2.0 完整版, 含 30+ commit 二期推进)

- **Test baseline**: 994 → **1122 passed** / 2 skipped / 0 failed (+128 测试)
- **Code 改动**: ~2200+ 行 (含测试 / 文档 / 迁移 CSV / 14 Stata 模板 / CLI / 集成测试)
- **30+ commits** in `feature/stage3-dual-track-v3.2.0` branch
- **Stata 模板**: 14/14 完整交付 ✓ (Tables 5 + Robustness Appendix 5 + Figures 2 + master + data prep)
- **CLI 子命令**: build-replication (M7) + list-templates (M4/7) + --verbose flag
- **集成测试**: 8-spec × 14 模板 = 112 实例化, 占位符零残留 (R54-A 并存命名)

### 🆕 v3.2.0 CLI 子命令全景 (4 个)

| CLI subcommand | 用途 | 添加于 |
|---|---|---|
| `build-replication --locus ... --subst ... --sent ... --root ...` | 一键打包 replication 包 (14 .do + README + commit hash) | M7 |
| `list-templates [--verbose]` | 列举 14 模板 + 占位符使用 inventory | M4/7 |
| `doctor [--verbose]` | 诊断 5 段: Python deps / pipeline 数据 / LLM cache / API key / Stata bin | M2/7 (第二批) |
| `verify-replication <path>` | 验证 replication 包结构 (5 段检查) | M4/7 (第二批) |

调用入口: `python -m news_process.papers._common.stata_runner <subcommand>`

stage 35 LLM 升级独立 CLI: `python -m news_process.validation.radius_sensitivity_llm [--dry-run|--launch]`

### 🆕 v3.1.1 → v3.2.0 迁移工具

`python -m news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade <old.parquet> <new.parquet> [--verbose]`

把旧 v3.1.1 panel parquet 升级到 v3.2.0 schema:
- bare `innovation_locus` / `_substantiveness` / `category_confidence` → `_full` 后缀
- 新加 `_ctx` 列 (NaN; 用户需重跑 stage 21 LLM 产实际值)
- 派生 `llm_verified_dual_full_only/_ctx_only/_both` 三互斥指示

### 🆕 Stata 模板交付 (12/14, plan v14 §9.2)

**Tables (论文主体, 4 模板)**:
| File | Title | Reference |
|---|---|---|
| 01_data_prep.do.tmpl | Data prep + xtset + winsor | infrastructure |
| 10_table1_descriptives.do.tmpl | Descriptive Statistics | Loughran & McDonald 2011 JF |
| 12_table3_mechanism.do.tmpl | Mechanism (tone_gap channels) | Adner-Kapoor 2010 + Bingler 2022 |
| 13_table4_heterogeneity.do.tmpl | Heterogeneity (size × frontier × geo) | Engelberg & Parsons 2011 JF |

**Robustness Appendix (双轨核心, 4 模板)**:
| File | Title | Reference |
|---|---|---|
| 20_tableA1_inter_track_kappa.do.tmpl | Inter-track κ | plan v14 §5.2 R5-B |
| 21_tableA2_main_spec_switch.do.tmpl | 8-spec Switch Sensitivity | Hassan 2019 + Sautner 2023 |
| 22_tableA3_bartik_iv.do.tmpl | Bartik IV (lf vs lc) | Goldsmith-Pinkham 2020 AER |
| 23_tableA4_radius_sensitivity.do.tmpl | Radius Sensitivity (LLM) | plan v14 §3.5 P5.2 |

**Figures (2 模板)**:
| File | Title | Reference |
|---|---|---|
| 30_figure1_event_study.do.tmpl | Event Study TWFE | Sun & Abraham 2021 JoE |
| 31_figure_coefplot_dual.do.tmpl | Coefplot 8-spec | 双轨核心可视化 |

### 🎯 CLI 一键打包 (M7)

```bash
python -m news_process.papers._common.stata_runner build-replication \
    --locus lc --subst sf --sent ctx \
    --root replication_v3.2.0_lc_sf_ctx
```

输出: 12 Stata .do 文件实例化到 `code/`, 数据 / 输出目录预创建, README 含 commit hash + dirty 检测。

### 📚 References

- Plan v14 冻结: `git tag plan-stage3-dual-track-frozen` (commit before this branch)
- 62 轮 plan 审计累计：v1-v12 (R1-R10, 38 finding) + v12-v13 (R11-R31, 53 累计) + v13-v14 (R32-R61, 68 累计)
- 7 轮 M1 自审：Round 1-7（Round 3-4 finding → 修复后 1000 → 1011 passed）

---

## v3.1.1 / 2026-05-15 — feat: tone_gap_tech_app symmetric counterpart (988 → 994)

### Added
- panel 新增 1 列: `tone_gap_tech_app` (locus 维度对称借鉴 v3.0.0 tone_gap_sub_symb)
- module-level helper `_compute_tone_gap_tech_app(panel)` (encode.py 顶层, hermetic 可测)
- 公式: `(llm_vote_tone_tech_full - llm_vote_tone_app_full) if min(n_tech, n_app) >= 5 else NaN`

### Methodology (三层文献锚定)
- Adner & Kapoor (2010 SMJ) ecosystem components vs complements
- Gomber et al. (2018 JMIS) enabling-tech vs business-function 双层框架
- 与 v3.0.0 tone_gap_sub_symb (Westphal & Zajac 1994/1998 ASQ) 形成方法层对称
- 设计来源: 15 轮审核 (8 自审 + 2 独立 Plan subagent 盲审 + 5 dry-run/dependency
  /验证轮) 共 57 项修订收敛; 连续 R13/R14/R15 三轮 0 新问题
- 修订声明: 修订 v3.1.0 commit 123da11 "刻意未实现"清单第 1 项
  (理由: tone_gap 是派生指标层, 非聚合源层, 不构成 locus 块功能新增)
- 探索性指标 (无预先理论符号), 实证用途仅作描述统计或交互项
- min ≥ 5 过滤防 compositional confound (R8 audit P confound-S3)

### Changed
- encode.py: module-level helper +17 行 (含 docstring) + aggregate_panel 调用 +5 行
- codebook.py: 新增 metadata['tone_gap_tech_app'] +21 行
- stata/05_label_advanced.do: 新增 1 行标签 (UTF-8 + CRLF)
- tests/fixtures/golden_panel_v0.json: 重生成 (40_panel_yearly + 51_panel_with_controls)
- CLAUDE.md: 测试基线 988 → 994, 当前版本 v3.1.0 → v3.1.1

### Added (tests)
- tests/test_tone_gap_tech_app.py: 6 hermetic 测试, 直接调用 _compute_tone_gap_tech_app
  (无 live parquet 依赖, 无 setup_logging 副作用)
  覆盖 mutation kill: 阈值边界 (=5/<5)、min vs max、减法方向、Float64 dtype、value range

### Test baseline
- 988 → 994 passed / 2 skipped / 0 failed (+6 测试)

### Caveat
- papers/ 层暂无回归引用; calibration v5.1 G1 解锁前不进主回归矩阵
- helper 与 sub_symb (无 min 过滤) 暂存设计不对称, 未来 v3.x.x 可统一
- **当前数据集 (164 行 / 82 银行 / 2017-2018) 中**: n_articles_tech 极稀疏 (max=4),
  无 bank-year 满足 min ≥ 5 → tone_gap_tech_app 全 NaN.
  这是 confound 防御正常运作的证明, 非 bug; 未来扩展年份/媒体后列才有面板观测.

### Pre-existing drift captured (golden snapshot)
本次 golden 重生成额外捕获了 stage 45 的 pre-existing 非确定性:
- 3 个 network 列 hash 漂移: bank_cfbetween_cent / bank_clustering / bank_harmonic_cent
  (network centrality 算法浮点精度差异, 与 v3.1.1 无关)
- 4 个 stage 45 副产物文件 size_bytes 微变 (article_bank, attn_index × 3)
- 元数据时间戳 (generated_utc, llm_snapshot_date)
- **R-impl-8 验证**: 跨连续两次跑 stage 45 + golden 重生成, 40_panel_yearly.parquet
  size_bytes 在第二次跑时仍微变 (2477561 → 2477545, 16 字节差) — 证实
  stage 45 存在 run-to-run 非确定性, 不只是跨 commit drift.
  当前 commit 锁定 commit 时刻的 disk+golden, reproducibility test pass.
建议作为 future work 单独修复 stage 45 确定性 (随机种子或浮点稳定算法).

### Dependencies
- v3.1.0 (commit 123da11) - 提供 _tech/_app 子集聚合
- v3.0.0 (commit 7666e2e) - 术语正名前置 (tone_gap_sub_symb 设计原型)

### Audit Trail (15 轮 + 5 轮实施后审核)
- R1-R7 自审 (完备性 / contract / 方法学 / 测试 / 文档 / 风险 / 排序)
- R8 Plan subagent 盲审 #1 (排序异议 + 3 method confound)
- R9 dry-run (np.where → pandas .where + 测试基线 988→994 修正)
- R10 跨文件依赖 (testpaths + .dta 自动同步)
- R11 Plan subagent 盲审 #2 (FATAL: stage 51 重跑 + pre-regen guard)
- R12 修复后自查 (CRITICAL: 抽 module-level helper 保 hermetic)
- R13/R14/R15 连续 0 新问题验证 = 计划级收敛
- R-impl-1 至 R-impl-5: 实施级 5 轮审核 (本 patch)

---

## v3.1.0 / 2026-05-15 — feat: iss subset LLM score aggregation (baseline 986 → 988)

### Added

panel 新增 **12 列** innovation_substantiveness 子集 LLM 逐模型 sentiment 均值:
- `{LLM}_tone_sub_{full,ctx}`   (3 LLM × 2 tracks = 6 列, 实质性子集 mean)
- `{LLM}_tone_symb_{full,ctx}`  (3 LLM × 2 tracks = 6 列, 象征性子集 mean)
- 其中 LLM ∈ {gpt54nano, gemini31111, deepseekv4}

### Methodology

- 依据: Westphal & Zajac (1998 ASQ) substantive-symbolic framework
- 范围依据 (经六轮审核):
  - 不补 `_title`: W&Z framework title-only 偏向 symbolic
  - 不补 `_cont`: 二分类下与 `_score` 高度共线
  - 不补 BERT/词典/IDF: 范围外
  - 不补 VW/MW/HW: 公关稿件密度反向因果风险
  - 不写 BH 校正: 多重比较校正属 papers/ 回归层职责

### Changed

- `news_process/pipeline/panel/encode.py`: substantiveness 子集循环新增 LLM 逐模型 _score 聚合
- `news_process/pipeline/panel/codebook.py`: family-level register 块 (12 entries)
- `news_process/tests/fixtures/golden_panel_v0.json`: 重生成

### Added (tests)

- `news_process/tests/test_iss_llm_score_subset.py`:
  - `test_iss_llm_score_subset_aggregation`: 12 列存在性
  - `test_iss_llm_score_subset_value_sanity`: 值范围 [-1,+1] + 非空校验

### Test baseline

- 986 → 988 passed / 2 skipped / 0 failed (+2 新测试)
- ruff check: All passed

### 前置约束

12 新列不应进入正式论文回归矩阵, 直到 calibration_plan v5.1 G1
(人工标注 baseline) 完成. BH FDR 校正应在 papers/bank_fintech_tone/analysis.py 实施.

### 依赖

v3.0.0 (commit 7666e2e) - 术语正名前置, 提供 _symb 后缀

---

## v3.0.0 / 2026-05-15 — BREAKING: 翻译层废除 + 38 列 `_desc → _symb` 术语正名 (baseline 991 → 986)

### 总览

W&Z (1998 ASQ) substantive-symbolic 框架术语对齐. v7 翻译层 (`tone_llms.py`
将 LLM 输出 '象征性' 映射为 '描述性' 以兼容 v6 panel/Stata 列名) 已废除.
panel 列值即 LLM 原始输出, 列名后缀由 `_desc` 重命名为 `_symb`.

### BREAKING CHANGES (panel schema)

**38 个 panel 列重命名** (panel parquet 不向后兼容):
- 主列: `n_articles_desc → n_articles_symb`, `llm_vote_tone_desc_{full,ctx,title}
  → llm_vote_tone_symb_{...}`, `tone_gap_sub_desc → tone_gap_sub_symb`,
  `pos_desc_count_{full,ctx} → pos_symb_count_{...}`, `pos_desc_hc_count_{...}
  → pos_symb_hc_count_{...}`
- 衍生指标: `desc_frac → symb_frac`, `tone_gap_desc_sub_{...}
  → tone_gap_symb_sub_{...}`
- 中间列: `_is_pos_desc_{...} → _is_pos_symb_{...}`, `_is_{llm|dict|bert|
  finbert_cn|fin_sent_zh|erlangshen|jiang_2021|yao_2021|bian_2021|du_2022|
  you_2018|hw2942|finbert2}_pos_desc_{...} → _is_..._pos_symb_{...}`,
  `_is_dict_pos_desc_{...}`, `_is_bert_pos_desc_{...}`, 等
- panel 列值: innovation_substantiveness '描述性' → '象征性'
- Stata 英文标签: 'Descriptive News' → 'Symbolic News (W&Z 1998)'

### 改动文件 (12 个)

- `news_process/pipeline/sentiment/tone_llms.py`: 删除翻译映射 + fallback '描述性'→'象征性'
- `news_process/pipeline/panel/encode.py`: `tt_mapping` + 17 处列名
- `news_process/pipeline/panel/runner.py`: 30+ 处列名 + 注释
- `news_process/pipeline/panel/export.py`: 列名 + Stata 英文标签
- `news_process/pipeline/panel/codebook.py`: 头部 docstring + entries
- `news_process/stata/{05_label_advanced,11_label_washing_disag,15_label_complete}.do`: 42 行
- `news_process/papers_assets/strategic_diff/do/{strategic_differentiation,text_coherence}.do`
- `news_process/data/processed/{21_tone_llms,22_words_tone,23_bert_tone,24_herd_decay,40_article_bank_level}.parquet`: 数据值修正
- `news_process/tests/fixtures/golden_panel_v0.json`: 重生成 (366 个 `_symb` 引用)
- `news_process/tests/test_majority_vote_categorical.py`, `pytest_run_pilot.py`: 测试硬编码
- `news_process/docs/methodology/prompt_terminology_mapping.md`: 重写为 v3.0.0 正名记录
- `news_process/CLAUDE.md`: 版本号 + 测试基线

### 删除

- `news_process/tests/test_translation_layer.py` (5 个测试; 翻译层废除后无需)

### 方法学动机

- Westphal & Zajac (1998 ASQ) substantive-vs-symbolic framework 严格对齐
- v7 翻译层为 v6 panel/Stata 兼容妥协, 但 `papers/` 模块已 0 引用 `_desc`,
  移除时机成熟
- W&Z framework 下 "象征性 (symbolic)" 是标准学术术语;
  "描述性 (descriptive)" 是 v6 历史命名遗产, 易被误读为 descriptive

### 测试基线

- 991 passed (v7 baseline) → 986 passed / 2 skipped / 0 failed (-5 = 删除 test_translation_layer.py)
- ruff check: All passed
- pytest 全套: 0 fail

### 回滚

`baseline/pre-v6` tag 标记 v7 终态; `git switch main` 即可放弃本次重构.

### 下游依赖

- **paper-final-audit-4**: 论文表格 / 文本中所有 `_desc` 列名引用须迁移至 `_symb`;
  论文方法节 "象征性" / "实质性" 术语已统一. 由用户单独启动.

---

## post-v2.1.0 / 2026-05-14 — Prompt v7: Westphal-Zajac substantive-symbolic + Gomber innovation locus (baseline 986 → 991)

### 总览

unified_cot.txt 从 v6 升级到 v7，对齐国际金融学 / 管理学顶刊方法学术语：
- 三阶段命名升级为 Entity-Topic Relevance / Sentiment Attribute /
  Innovation Attribute Classification（Bybee et al. 2021 RFS + Loughran &
  McDonald 2011 JF + Westphal & Zajac 1994/1998 ASQ）。
- `fintech_category` 从 stage 1 迁移到 stage 3 并重命名为 `innovation_locus`
  （Gomber et al. 2018 JMIS enabling-technology-vs-business-function 框架）。
- `text_type` 重命名为 `innovation_substantiveness`，判定标准从 descriptive
  框架升级为 Westphal & Zajac substantive-vs-symbolic 框架，强调 decoupling
  和 impression management（非"含可验证事实"）。
- 新增两个 confidence 字段（innovation_*_confidence × 2 维度 × 2 轨道 = 4 panel 聚合列）
  对齐 verification/sentiment 信心评分。

### 主要决策

- **W&Z 框架 prompt 文本完整重写**（R5-A）：阶段三判定标准从"含可验证事实
  vs 无事实"切换为"实质经济后果 vs 合法性信号 / 印象管理 / decoupling"。审稿
  人对照 replication 包时方法学声明与执行一致。
- **翻译层设计 (方案 B)**：tone_llms.py `_aggregate_track` 内联翻译 LLM 输出
  '象征性' → parquet '描述性'。保持 panel 列后缀 _sub/_desc/_tech/_app 稳定，
  Stata 变量名 50+ 零改动，papers/ 5 模块零影响。Stata 中文标签 28 处升级到
  symbolic 框架（变量名后缀不变；docs/methodology/prompt_terminology_mapping.md
  显式说明 `_desc` 后缀在 v7 起的 W&Z symbolic 解读）。
- **prompt_sensitivity.py 4 变体同步**（B 方案，R5-C）：4 变体（V1 角色/V2
  结构/V3 精简/V4 改写）全面升级到 v7 三阶段 schema；新增
  PASS_THRESHOLD_INNOVATION_SUBSTANTIVENESS=0.75 / _LOCUS=0.80 至 validation.yaml。
- **方法学透明性兜底**：新建 docs/methodology/prompt_terminology_mapping.md
  含 8 轮审查脚注 + Stata 标签说明 + 翻译层语义 + APA 7 References。
- **9 轮严谨审查 + 26 项遗漏修复**：本变更经 8 轮事实查证 + 自评审 +
  用户决策检查点 + 第 9 轮执行级深度评审，累计修复 N1-N7 (影响面遗漏) +
  R5-A/C/G/H/K (方法学瑕疵 + W&Z 框架失真修正) + R6-B/E/J/M (执行细节) +
  R7-A/B/C/D/E/F/G/H (commit 事务性 + entity_masking + logger + 灰度 + 缓存)
  + R8-A/B (validation.yaml 配置层 + Stata 标签升级) 共 26 个潜在风险。

### 与 calibration freeze 协同

本 v7 升级**严格正交**于 git tag `calibration-plan-v5.1-frozen`：
- tone_validation.py（ECE 校准模块）Grep 零命中 v7 schema 字段
- v5.1 calibration Day 0 G1 fail 状态下，32_human_samples.xlsx 标注尚未启动
  （用户决策检查点 G1 = a），v7 输出将作为标注新基线
- v7 重跑 LLM (~$25, 1170 行 × 3 模型 × 2 轨道 = 7020 calls, 57 分钟) 已用户授权
- 兼容: panel 列后缀 _desc 与 v6 同名，所有 papers/{paper}/analysis.py 零影响

### Baseline 更新

- pytest baseline: **986 passed → 991 passed**（+5 测试：test_translation_layer.py
  含 R5-A 翻译层验证；+1 dual_track 测试扩展 W&Z confidence 字段断言）
- prompt_template_version: `v6-2026-05-13` → `v7-2026-05-14`
- 21_tone_llms.parquet 列变化:
  - 删: text_type, fintech_category (从 stage 1)
  - 加: innovation_substantiveness, innovation_locus, innovation_*_confidence × 2 dims × 2 tracks
  - 行数: 849 (v6=861, v7 verification 通过率从 73.6% → 72.6%;
            stage 21 输入 1170 不变; W&Z 框架略严让 12 个样本翻 false。
            另有 134 次模型 API 调用失败影响 per-row 投票但不改变行数。)
- 40_panel_yearly.parquet: 164 行 × 1989 列（v7 + R6-H 4 个 avg confidence 聚合）

### Commit chain

- `25a61d0` refactor(prompt): unified_cot v7 — atomic schema + code + tests + docs (18 files, 603+/138-)
- (本提交) refactor(prompt): v7 golden refresh + parquet rerun + CHANGELOG + CLAUDE.md baseline
- git tag `prompt-v7-released` (供单点回滚参照)

---

## post-v2.1.0 / 2026-05-14 — Refactor: 统一 categorical voting (baseline 956 → ~971)

### 总览

把 `pipeline/sentiment/tone_llms.py` 中分散的 3 处分类多数投票实现（sentiment /
fintech_category / text_type）统一为参数化函数 `majority_vote_categorical`。
**0 行为变更**（已 byte-level 边界跟踪验证 case-by-case 等价性）；平局策略差异
（`undefined` for sentiment 保留独立中性类；`conservative` for binary fields 归
modal class prior, MAP under uniform prior）通过显式参数声明，便于论文 Methods
章节直接 quote。

### 主要决策

- **统一抽象**：`majority_vote_sentiment` 改为对 `majority_vote_categorical` 的薄
  包装（向后 100% 兼容；现有 3 处生产 callsite + 4 个测试 0 修改）；
  `fintech_category` 与 `text_type` 内联 `Counter.most_common()` 改为统一调用。
- **fail-fast 入口校验**：`majority_vote_categorical` 在函数入口立即校验
  `tie_strategy` 与 `tie_default`，misuse 即时抛 ValueError 而非延迟到平局时。
- **测试覆盖**：新增 `tests/test_majority_vote_categorical.py`，~15 个 parametrize
  子用例（含 3-way tie 覆盖：[A, B, C] 各 1 票，避免 2-way tie 单一覆盖盲区）。
- **学术依据 docstring**：引用 Wang et al. (2023) ICLR self-consistency + Bishop
  (2006) PRML §1.5 Decision Theory（after Roberts 2017 PNAS 幻觉引用清理后，
  本次学术引用已逐条 verify 真实性）。
- **`majority_vote_bool` 未并入**：二值布尔投票用严格多数（>50%），与 plurality
  语义不同，保持独立抽象（[tone_llms.py:569](news_process/pipeline/sentiment/tone_llms.py#L569)）。

### 与 calibration freeze 协同

本重构与 git tag `calibration-plan-v5.1-frozen` (→ commit `6c12ad4`) **完全正交**：
- 不触碰 frozen tag
- 落在 `tone_llms.py` 主投票函数；v5.1 calibration plan 的 Stage 45 校准 apply
  独立路径，不依赖此函数
- 未来 Day 1 calibration 实施时无影响

---

## post-v2.1.0 / 2026-05-13 — Wave 0/1 + Batch P0 + V8 + Priority ABC (baseline 814 → 956)

### 总览

2026-05-13 一天内完成五轮"清理 → 加固 → 扩展 → 覆盖"工作链, 把 v2.1.0
后的本地 pytest baseline 从 814 推进到 956 (+142 tests, +18% 测试覆盖),
同时把 CI 从 4 连红推回 6/6 绿、修 7+9 处 CLAUDE.md/ci.yml 自相矛盾文档、
补主论文 + 4 衍生论文 + 6 个 panel 模块的零测试覆盖.

| Batch | passed delta | 核心交付 | commits |
|---|---|---|---|
| Wave 0/1 | 814 → 855 (+41) | golden 增 llm_snapshot_date 元数据; BERT cpu_strict 确定性 (4 unit + 1 implementation); ruff 409→0; pre-commit 框架 | eef7ed1 fa952ce 4687328 ea823dc |
| Batch P0 | 855 → 863 (+8) | LLMCache hit/miss 计数 (T0.0a); Wave 4 BERT→panel fail-fast invariant (2 tests); CI threshold 780→820 | 6b3d52b 2afe44a 7275612 4d440e2 e6d99e1 |
| V8 | 863 → 879 → 891 (+28) | pyproject `[project.optional-dependencies].dev`; logs/runs/ 按年龄修剪 (5 tests); main paper `bank_fintech_tone` smoke (11 tests); ruff exclude 9 外部目录; iv_did Wave 2 batch 1 (12 tests) | cd5ec08 0316712 79553a2 34b0b9e 4df9c68 0da42a9 bb6574a |
| Priority ABC | 891 → 956 (+65) | 4 衍生论文 parametrized smoke (40 tests); 6 panel 模块 import + math (17 tests); merge_policy_shocks DID Wave 2 b2 (8 tests) | d429834 5eec166 f37ae4f 04cc0ca |

### Wave 0/1 (golden + BERT determinism + ruff clean + pre-commit + CI fix)

主要决策:
- **golden 列入 llm_snapshot_date + llm_models**: 让 panel reproducibility 测试在 LLM 模型集变动时能感知到, 不再 silent regression.
- **BERT cpu_strict 模式**: 在 tone_berts.py 顶部统一调用 torch.manual_seed +
  np.random.seed + transformers.set_seed + torch.use_deterministic_algorithms(warn_only=True);
  cuDNN benchmark=False, AMP=False (gpu_strict 也覆盖). 4 个 deterministic
  test 防回归.
- **CI 4 连红根因**: Wave 1 T1.1a 创建 test_tone_berts_deterministic.py 顶层
  `import torch`, 但 CI light 矩阵 (win/linux × py3.11/3.13) 节省 4GB DL 依赖
  不装 torch → ModuleNotFoundError, 4/5 job 全红. 修复 = 加 `pytest.importorskip("torch")`
  在 module top, light job 干净 skip.
- **CLAUDE.md 7 处自相矛盾修复**: shim path/count (XX_*.py→NN_*.py, 但数量
  写错为 23 — V8 中再次修正回正确的 26), .gitattributes 声明 vs 文件实际
  不存在, baseline 数字过期等.
- **二级 CI 失败暴露**: 修了 torch import 后 test_25_audit 的
  TestComputeStrategicDifferentiation 5 测试因 strategic_diff.py:235 lazy
  `import sentence_transformers` 而 CI light 全失败, 用 class-fixture
  importorskip 修复.
- **.gitattributes binary-only 策略**: 不写 `* text=auto` 避免 git renormalize
  现有混合 CRLF/LF 文件, 仅 mark binary 文件 (parquet/xlsx/db/pkl 等).
- **死 workflow 清理**: news_process/.github/workflows/ci.yml 是 GitHub
  Actions 不识别的子目录 workflow, 从未运行过 → 删除; PR 模板从 news_process/.github
  移到根 .github/.

### Batch P0 (collected: S1+S2+S3+S4+S5; T0.0a 落地)

- **LLMCache.stats() 方法**: 暴露 hit/v0_hit/miss/writes/lookups/hit_rate 6 项
  process-local 计数 (非持久化). 用于诊断 "为什么这次 run 比上次慢" 之类
  问题. 6 单元测试 (test_caching_stats.py).
- **Wave 4 invariant**: tests/integration/test_bert_panel_invariant.py 加 2
  fail-fast 测试 — 对每个 config 列出的 BERT model 验证 stage 23 parquet
  必含 {short_name}_label_{ctx,full,title} 3 列, 且不全 NaN. 触发场景:
  hw2942 因 HF 不可达而 graceful skip 时 panel encode 会 KeyError, 本测试
  在 <1s 内拦住, 不让等到 stage 45 才炸.
- **CI threshold 收紧**: 实测 829 (full job post Batch P0) > 820, 把可容忍
  回归从 43 测试压到 9.
- **23 / 26 shim regex bug 自纠**: V7 把 `^\d{2}_` 数 shim 得 23, 漏 32a/38a/38b
  字母后缀, 改 `^\d{2}[a-z]?_` 后真值是 26. CLAUDE.md + docs/architecture.md
  从 26→23 又改回 26. memory/shim_inventory.md 记录这个教训.

### Priority ABC (paper-critical 覆盖批量, post V8 audit 发现)

V8 收尾时的"再三验证"审计用 grep `panel\.{module}` 跨 6 个角度查到
pipeline/panel/ 仍有 5 个零测试模块共 5300+ LOC, 加 4 个衍生论文模块
共 620 LOC, 加 iv_did 中 merge_policy_shocks (Wave 2 b1 显式延后).

- **Priority B — 4 衍生论文 smoke (d429834, +40 tests)**:
  benefit_society / brokerage_network / llm_peer / strategic_diff 全部
  零测试. 因 4 论文结构与 bank_fintech_tone 100% 同构 (analysis +
  figures + tables + STAGES + main --dry-run), 用一个 parametrized
  文件 (4 papers × {4 modules + main callable + STAGES + 4 dry-run
  stages}) = 40 tests in 0.5s.
- **Priority A — 6 panel modules smoke + 纯数学 (5eec166, +17 tests)**:
  runner (1505 LOC) / network_spillover (1216) / attention_media (995) /
  llm_peer_iv (723) / codebook (461) / network_brokerage (426).
  parametrized import + callable-API 检查 (12 tests) + 纯函数数学验证
  (5 tests: row_stochastic 行和=1, _gini 边界, codebook metadata
  非空, _infer_track fallback, compute_industry_neg_shock 列契约).
  关键决策: 大模块如 runner.main() 只做 import smoke (实跑会触发
  panel build); 纯函数才做真数学验证.
- **Priority C1 — merge_policy_shocks Wave 2 b2 (f37ae4f, +8 tests)**:
  Wave 2 b1 (bb6574a) 已显式延后此函数 (因需 JSON config + 复杂城市/
  省匹配). Priority C1 关闭 gap: tmp policy_shocks.json + 4 银行 × 4 年
  panel, 8 测试覆盖 city/province/control/post/rel_year/lag-lead/
  missing-file. iv_did.py 现 6 个核心函数全部测试覆盖 (b1 + b2 = 20 tests).

### V8 (P-1 + P-3 + P-4; Wave 2 batch 1 启动)

- **pyproject `[project.optional-dependencies].dev`**: 解决 CLAUDE.md "pyproject
  是 single source of truth" 与现实 (requirements.txt 才有 pytest/pre-commit/
  pytest-cov) 不符问题. `pip install -e ".[dev]"` 现在能装齐 dev 工具.
- **logs/runs/ 按年龄修剪**: `python -m news_process.scripts.cleanup prune-logs
  --keep-days 30 [--dry-run]` 与既有 `clean-logs` (核选项 rmtree) 互补. 实测
  本机 132 run 子目录, --keep-days 30 报告 0 需删 (全部 < 30 天).
- **bank_fintech_tone main paper smoke**: 主论文 analysis.py/figures.py/
  tables.py 三入口零测覆盖, 加 11 smoke (4 import × parametrized + main
  callable + STAGES 契约 + --dry-run × 4 stages) 防 silent regression.
- **ruff scope 修正**: `ruff check .` 在仓库根扫到 748 vendored 误报
  (.gemini/ Awesome-Agent-Skills/ literature/ annual_reports/ FinBERT/ 等),
  加 9 dirs 到 `[tool.ruff].exclude` 后 0 errors.
- **CI workflow 9 处过期 baseline 同步**: 实测 845 → 阈值仍 820 (25 buffer),
  panel_reproducibility 18→19, data-dep skip 32→33.
- **Wave 2 batch 1 (paper-critical iv_did)**: 812 行 Bartik IV + DID + Rotemberg
  实现, 此前 0 测试. 加 12 合成-mock 测试覆盖 5 个核心函数 (skip merge_policy_shocks
  到后续 batch 因其需 JSON config + 复杂城市/省匹配). 不依赖网络 / 大数据,
  执行 <0.5s.

### Memory 系统新增 (跨会话持久化)

- `ci_matrix.md`: CI 5-job 矩阵 + light/full 区分 + importorskip 规约
- `shim_inventory.md`: shim 真实数量 26, regex `^\d{2}[a-z]?_` 才能数全
- `hf_network.md`: 本机 huggingface.co 直连超时, hw2942 等未缓存模型不可下

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
| post-final recode 审查 (修 1 接口契约 bug + 加 2 不变量) | round 3 final recode | **810 / 2** |
| post-round-3 review (R1-R8 修补 + M1/M2 缺失测试 + R8 哨兵 ASCII 化) | **当前 HEAD** | **814 / 2** |

> 本轮 (round 3 含两轮 recode + 一轮 review) 增量 +28 来源:
>   - P0-2 +2 invariant test (TestStataLabelsInvariant 防 STATA_LABELS dict-key 重复)
>   - P1-4 +2 invariant test (TestEnvExampleCoversYamlPlaceholders 防 .env.example 错位)
>   - P1-8 +12 smoke test (6 个零测 stage × 2 类: import + main-callable)
>   - P3-17 +3 cache key invariant (prompt_version + temperature + SCHEMA_VERSION)
>   - **recode 审查 +3 cache edge-case** (temperature precision .4f→repr / pipe collision / v0 fallback strict)
>   - **final recode +2 cache 边角** (None vs '' / v0+v1 共存优先级)
>   - **round-3 review +6 reliability** (M1 rapidfuzz/thefuzz parity + M2×2 env 间接引用警告 + R8 哨兵 known-limitation + 其它 R1-R7 不增 test)
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
> **round-3 review (2026-05-09) 修补 7 项**:
>
> - **R1 修补**: ci.yml light job 内联 deps 漏装 rapidfuzz, 让 light 矩阵
>   3/4 单元走 thefuzz fallback 而 full 矩阵 1/4 走 rapidfuzz first. 修补
>   后 4/4 单元一致走 rapidfuzz first.
> - **R2 修补**: ci.yml full job 跑了两次 pytest (一次 -v + 一次 tee), CI 时长
>   double. 现合并为单次 ``set -o pipefail; pytest -v 2>&1 | tee /tmp/...``,
>   pipefail 防 tee 掩盖 pytest 失败码.
> - **R3 文档化**: caching.py docstring 明示 prompt_version 维度是 "infrastructure
>   ready, NOT YET wired into production callers" (5 个生产 callsite 仍走默认
>   "v0"); v3.0 PR 应让 callsites 显式传入 ``prompt_version=cfg['prompts']
>   ['version']`` 才能真正激活防御.
> - **R5 + M2 修补**: ``_validate_env_placeholders`` 加第二阶段递归扫描 —
>   ``.env.example`` 中 ``KEY=${OTHER}`` 形式的间接引用, 若 OTHER 未声明也
>   未在 os.environ 中, 触发 warning. 防止"复制 .env.example 后只填一个
>   var, 间接引用 silent 展开为空字符串"的 silent failure.
> - **R6 修补**: test_stage_smoke.py 加 conftest fixture 在每个 import test
>   后清理 logs/ 中新增 .log 文件, 避免 4 个 backing module 顶层 setup_logging
>   污染仓库.
> - **R7 修补**: Makefile purge-all 加 ``CONFIRM=yes`` 守门, 与 cleanup.py
>   ``--yes`` 一致. 防止 ``make purge-all`` 一键无确认地删除 9.4 GiB 数据.
> - **R8 修补**: cache ``_NONE_SENTINEL`` 由 ``\\x00<None>\\x00`` (含 null
>   byte) 改为 ``<<NULL_SENTINEL>>`` (纯 ASCII), 避免 sqlite/终端跨版本
>   边角. 配套 ``test_cache_sentinel_known_limitation_with_literal_input``
>   显式文档化"用户字面量传入哨兵会与 None 碰撞"是预期行为.
> - **M1 新增**: rapidfuzz vs thefuzz parity 测试 (允许 ±1 取整误差),
>   守护 P2-12 "drop-in replacement" 假设.
>
> 任何后续 PR 应以 HEAD baseline (814) 为合并门槛, 不得低于该数.
> 历史 anchor (772 / 782 / 786 / 805 / 808 / 810) 仅作回溯参考.

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
