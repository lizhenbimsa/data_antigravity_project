# CHANGELOG — news_process 架构重整记录

按 Phase 演进记录全部架构改动。每个 phase 末打 git tag，单点 `git revert <hash>` 可回滚任意子任务。

格式: 每个 phase 标 (a/b/c/...) 子任务，含 commit hash、LOC 净改动、关键决策。

---

## v2.0.0 / phase-8-baseline (2026-05-04, current HEAD)

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
