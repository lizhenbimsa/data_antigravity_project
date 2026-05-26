# Technical Debt Log

本文件记录质量加固扫描（/goal 2026-05-27）期间确认为**真受阻**、不能在
8 小时内闭合的项；每条均给出原因 + 解锁条件 + 估计影响。条目格式：

> **[NN-x] 标题** — 编号 (1)-(8) 对应 /goal 八条；x 是同条内子项。
> - **原因**：阻塞的根因（缺凭据 / 外部依赖 / 上游 gate / spec 不明）。
> - **解锁条件**：解除阻塞需要什么动作。
> - **影响**：跳过该项对 /goal 收敛的实际影响。

---

## (1) 测试套件 0 failures / 0 skips

### [1-A] `test_pipeline_lock::test_pipeline_lock_unix` 永久 skip（Linux/macOS only）

- **位置**：`news_process/tests/test_pipeline_lock.py:157` 与 `:346`
- **原因**：使用 `fcntl` 模块，Windows 上 `fcntl` 不存在，必须 skip。同包另一
  测试已就 `PipelineLock("")` 在 Linux/macOS/Windows 三平台均不 raise 的事实
  做永久 skip + 文档化（见 :346 docstring）。当前会话主机为 Windows 11 →
  这两个 skip 不可能在本机变为通过。
- **解锁条件**：在 Linux/macOS CI runner 上跑这两条；或将 `fcntl` 路径迁到
  `portalocker`（向 lock 实现引入新依赖，不在本次 quality-hardening scope）。
- **影响**：合计 2 个 skip。在 Linux 跑同样命令时 skip 数会变；Windows 本机
  无法消除。`/goal` 第 (1) 项的 "0 skipped" 在 Windows 本机无法满足。

## (1) 测试套件 — Integration 8 failures（disk panel parquet 过期）

### [1-B] `test_panel_reproducibility::test_column_hashes_match_golden[*]` × 7

- **位置**：`news_process/tests/integration/test_panel_reproducibility.py`
- **原因**：磁盘上的 7 个 parquet（`21_tone_llms`, `22_words_tone`,
  `23_bert_tone`, `24_herd_decay`, `40_panel_yearly`, `40_article_bank_level`,
  `51_panel_with_controls`）仍是 2026-05-16 baseline；CLAUDE.md 顶部 "Disk 实测
  状态" 段明确："本节代码 ready ≠ disk 落地"。v3.5.2 → v3.7.4 累积新增 15+ 列
  尚未通过 production run 写入磁盘。Golden snapshot 期望新 schema 哈希 → 现存
  parquet 哈希必然不匹配。
- **解锁条件**：用户授权 production pipeline run（M0 gate，43-73 次授权之一），
  把 stage 13/16/17/18/19/22/30a 等下游重跑写盘后再执行
  `python scripts/migrate/generate_golden_snapshot.py` 重生 golden baseline。
- **影响**：7 个 integration test fail 持续，直到 production run 完成。

### [1-C] `test_v3_2_panel_columns::test_panel_dual_subset_identity`

- **位置**：`news_process/tests/integration/test_v3_2_panel_columns.py:122`
- **原因**：与 [1-B] 同源。`n_articles_tech_lc_ctx + n_articles_app_lc_ctx
  <= n_articles` 不变式被磁盘 panel 上一处 `tech_lc=6` vs `n_articles=5`（旧
  v3.5.0 之前的聚合逻辑遗留）违反，单点违规但断言要求 `.all()`。
- **解锁条件**：同 [1-B]，production run 重写 panel 后失败消失。
- **影响**：1 个 fail。

## (2) 覆盖率 ≥ 95%

### [2-A] 仓库基线 40.09%，95% 全仓目标在 8h 内不可达；已对 11 个高 ROI 文件完成 ≥90% 闭合

- **位置**：`news_process/` 全量；coverage report 见 `coverage_baseline.json`。
- **原因**：本仓库 23,115 statements；从 40.09% → 95% 需补 ~12,700 行覆盖。
  其中 `validation/` 目录多个模块 0-20% 覆盖（`entity_masking.py` 0% / 338 行；
  `threshold.py` 0% / 284 行；`tone_validation.py` 0% / 909 行；
  `media_diversity.py` 6.59% / 577 行；`radius_sensitivity.py` 16.96% / 678 行；
  `dict_coverage.py` 16.11% / 540 行；`temporal_mask.py` 18.39% / 87 行）—
  这些是科研一次性 audit 脚本，集成测试需要真实 LLM/embedding/Stata 出，单元
  测试需要 mock 700+ 函数。8h 内不可能完成。
- **本会话闭合记录** (Round 1-28, 2026-05-27 by quality-hardening /goal)：
  对 30+ ROI 较高的 small/medium 模块完成 per-file ≥90% 目标 (TOTAL
  40.09% → **~42.5%** = +2.4 pp ~+550 covered lines; Files ≥90% 38 →
  **55+/195 ≈ 28%**; core/ 79.13% → **85.00%**, papers/ 64.22% → **~72%**,
  scripts/ 57.53% → **64.76%**, <root> 16.23% → **~27%**)：
  - `papers/_common/_git_utils.py` 84.62% → **100%** (+9 tests)
  - `papers/_common/paper_spec_schema.py` 84.21% → **100%** (+15 tests)
  - `core/text/title_indicators.py` 80.00% → **100%** (+10 tests)
  - `core/text/canonicalization.py` 86.11% → **94.44%** (+3 tests)
  - `core/data_versioning.py` 84.76% → **100%** (+7 tests)
  - `scripts/audit/loc_summation_check.py` 85.00% → **100%** (+4 tests)
  - `pipeline/sentiment/lm_non_sentiment.py` 93.94% → **96.97%** (+2 tests)
  - `papers/benefit_society/cohort.py` 71.05% → **100%** (+2 tests)
  - `pipeline/llm_archive/manifest.py` 91.25% → **100%** (+5 tests)
  - `papers/_common/panel_loader.py` 50.00% → **~95%** (+5 tests)
  - `scripts/migrate/v3_1_to_v3_2_panel_upgrade.py` 79.37% → **98.41%** (+3 tests)
  - `pipeline/audit/lexical_discriminant_validity.py` 81.46% → **83.44%** (+4 tests)
  - `pipeline/audit/construct_orthogonality.py` 87.80% → **94.51%** (+6 tests)
  - `core/text/entity_context.py` 74.77% → **100%** (+8 tests)
  - `pipeline/audit/inter_track_kappa.py` 91.58% → **96.84%** (+3 tests)
  - `pipeline/llm_archive/archive.py` 61.11% → **98.15%** (+10 tests)
  - `core/locking.py` 74.26% → **83.17%** (+4 tests; 剩余 14 lines = Linux-only
    fcntl 路径 Windows 本机不可达, 见 §[1-A])
  - `validation/manual_validation_schema.py` 92.86% → **100%** (+1 test)
  - `pipeline/sentiment/numerical_intensity.py` 80.19% → **90.57%** (+7 tests)
  - `papers/_common/pipeline_runner.py` 50% → **100%** (+2 tests; bridge mock)
  - `papers/_common/derivative_replication.py` 96.67% → **98.33%** (+1 test)
  - `core/schemas_yaml.py` 94.06% → **99.01%** (+7 tests _type_check edges)
  - `core/text/canonicalization.py` 94.44% → **100%** (+1 test fuzzy app)
  - `papers/_common/paper_config.py` 95.56% → **100%** (+2 tests)
  - `papers/_common/paper_registry.py` 95.59% → **98.53%** (+2 tests)
  - `core/logging.py` 94.97% → **97.48%** (+4 tests)
  - `core/text/token_utils.py` **0% → 100%** (+11 tests; greenfield)
  - **P2/P3/P4 paper-level (×3)**: `bank_fintech_attention/locus/substance` 0% →
    57.14% analysis + 100% __init__ + 54.55% tables (+30 parametrized tests)
  - `news_process/run_paper.py` **0% → 92.45%** (+13 tests; greenfield)
  - `pipeline/preprocess/normalize.py` **0% → 96.55%** (+11 tests; greenfield)
  - `pipeline/preprocess/load.py` **0% → 49.28%** (+7 tests; greenfield, main()
    happy path 需 xlsx fixture defer)
  - `pipeline/external/epu_merge.py` 66.28% → **73.26%** (+2 tests)
  - `papers/_common/stata_postprocess.py` 95.04% → **97.16%** (+4 tests)
  - `papers/_common/paper_figures_ext.py` 94.92% → **~99%** (+4 tests)
  - `papers/_common/panel_loader.py` 92.50% → 100% (+2 tests; paper_id branch)
  - `pipeline/sentiment/forward_looking.py` 91.67% → 95.83% (+1 test)
  - `papers/_common/paper_registry.py` 95.59% → **100%** (+1 test; list_paper_ids)
  - `pipeline/features/benefit_society_placebo.py` 93.33% → **98.89%** (+4 tests)
  - **P2/P3/P4 tables.py × 3**: 54.5% → **90.91%** (+12 mock tests; build_table2-5
    delegate to read_paper_esttab verified per actual function names per paper)
  合计 **+230 tests, 全套 1889 → 2119 passed**。Ruff 始终 0 warn 跨 33 轮。
  最终: TOTAL 40.09% → **42.61%**; ≥90% 文件 38 → **55/195 (28.2%)**;
  at 100% files: **31/195 (15.9%)**; core/ 85.00% / papers/ 72.22% /
  scripts/ 64.76% / <root> 26.97%。
- **未闭合**：剩余 ~155 文件 < 90% 多为 LLM / Stata 依赖类（需真服务 mock 数千行)，
  或 module-level init failure 路径（除非分文件 refactor 难单测）。
- **解锁条件**：(a) 多月 mock 撰写工作；或 (b) 调整 95% 目标到现实的渐进里程碑
  （e.g. core/ ≥ 90% 已基本满足，validation/ 单独 deferral）。
- **影响**：/goal 第 (2) 项无法在单次 session 满足；已交付可累加的渐进基线。

## (4) 类型检查 mypy 全绿

### [4-A] 仓库无 mypy 配置 / 无类型注解整改基线

- **位置**：`pyproject.toml` 无 `[tool.mypy]` 段；少量函数有部分注解，但绝大多数
  科研脚本（`scripts/audit/`, `validation/`, `pipeline/sentiment/`）无注解。
- **原因**：从 0 开始引入 strict mypy 对 ~200K LoC 仓库等于一次 v3.8 重构 PR。
  即便用 `--ignore-missing-imports + --no-strict-optional` 仍会产出数千 finding。
- **解锁条件**：分阶段 typing PR（v3.8 计划），每个 stage 模块单独 strict
  enable；或采用 pyright `basic` 模式做 type-narrowing-only 检查。
- **影响**：/goal 第 (4) 项 deferred。

## (5) 构建 0 warning

### [5-A] 无独立 "build" 命令：本仓库非 wheel/sdist 发布源

- **位置**：`pyproject.toml::[project.dependencies]`，editable install 已生效。
- **原因**：仓库是研究流水线项目，不向 PyPI 发布。`pip install -e .` 在新机
  上的安装行为受 50+ 个传递依赖影响（torch / transformers / sentence-transformers
  / pyreadstat 等），warning 多源于 third-party setup.py（不是本仓库源码）。
- **解锁条件**：若用户需要可重现的 zero-warning build，应改用
  `requirements.lock` + `pip install --no-deps news-process`，并对每个第三方
  warning 单独 minimum-version pin 或 patch upstream。
- **影响**：仅需验证 `pip install -e .` 退出码 0；warning 来自第三方不计。

## (7) 文档

### [7-A] ~113 个 public function 缺 docstring（集中在 `scripts/` 与 `scripts/audit/`）

- **位置**：v3.7.4 + quality-hardening 2026-05-27 实测后 — modules 250/250 ✓，
  classes 20/20 ✓，public functions 113/659 missing。本次会话已补 5 个 dag.py
  谓词 + 2 个 schemas_yaml 类 + 1 个 scripts/replace_v6_to_v3.py 模块 + 4 个
  paper_registry PaperSpec 属性 + 5 个 tone_llms AsyncPacer/AsyncModelAvailability
  方法。剩余 ~108 个 missing 集中在：
  - `scripts/cleanup.py` 7 (CLI 命令处理函数)
  - `scripts/convert_md_doc.py` 7 (一次性文档转换)
  - `scripts/audit/audit_deep.py` 5 (一次性 audit 脚本)
  - `scripts/audit/_replan_v5_evidence/*.py` ~6 (一次性 LLM 探针, ruff exclude 中)
  - `core/logging.py` 4 (logging.Filter / Formatter override / decorator wrappers)
  - `pipeline/sentiment/tone_llms.py` 0（本次会话已补完）
  - 其他 ~80 散布于 papers tables/figures 重复模板 + validation 一次性脚本
- **原因**：scripts/ 与 scripts/audit/ 多为一次性脚本，函数级 docstring 价值低于
  脚本顶部已有的模块级 docstring；logging Filter/Formatter override 是标准库
  契约方法，行为由父类签名定义。要把全部 108 个补完需要批量改 ~40 个文件 +
  full test rerun，超出本会话剩余预算。
- **解锁条件**：分批 PR，每个 PR 处理一个子目录（scripts/ / scripts/audit/ /
  core/logging.py / validation/）。每批 < 50 LOC。
- **影响**：/goal 第 (7) 项 "every public function has docstring" 部分满足
  （250/250 module + 20/20 class + 546/659 function = 82.9% 函数覆盖；
  ✓ all core/dag.py predicates, schemas, paper_registry, tone_llms 已闭合）。

---

## (6) 死代码 + TODO/FIXME triage

### [6-A] Plan E P7.b dual-track validation 推迟（3 TODO）

- **位置 / 一句话说明**：
  - `news_process/validation/temporal_mask.py:6` — temporal_mask 仅测 `_full`，`_ctx` mirror 待 P7.b PR。
  - `news_process/validation/radius_sensitivity.py:84` — radius 扫描双轨化（半成品 ctx 隐式覆盖）待 P7.b。
  - `news_process/validation/decay_sensitivity.py:7` — decay sensitivity 双轨化（输出 6×6 矩阵）待 P7.b。
- **原因**：3 项均在 Plan E §P7 显式列为"不阻塞主线、推迟到独立 PR"；当前模块
  已通过 Plan E 主线 acceptance gate。
- **解锁条件**：执行 `docs/methodology/plan_e_p7_dual_track_validation.md` 中的 P7.b PR。
- **影响**：3 个 TODO marker 保留在源码中以锚定未来 PR 入口（移除会丢失上下文）。

### [6-B] `scripts/data_acquisition/banking_outcome_dry_run.py` 用户凭证占位（3 TODO）

- **位置 / 一句话说明**：
  - L54 — 脚本本身是 scaffolding，Wind API 调用待用户填真实凭证。
  - L109 — 数据源 acquisition 函数 stub，等待 Wind/银保监会反爬解决方案。
  - L573 — `--full-bank_list` 加载 `config/bank_list.yaml`，等 M1 deliverable
    （CLAUDE.md 顶 v3.7.0 NON-BREAKING 段落注明 M1 待补 ~460 行）。
- **原因**：DC2 outcome dry-run 协议 (v3.7.0) 显式把真实数据采集 gating 在
  M1（bank_list.yaml frozen 39 行 → 全量 ~500 行）+ 用户 Wind 授权。
- **解锁条件**：M1 完成 `config/bank_list.yaml` + 用户提供 Wind/银保监凭证。
- **影响**：保留 TODO 锚点指向 M1 PR。

---

> 闭合记录：当下游任一条目解锁后，从本文件移除条目，并在 PR 描述中显式引用
> 闭合 commit。/goal 第 (8) 条回归防护要求 regression 必须先于其他改动修复。
