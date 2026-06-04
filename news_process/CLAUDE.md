# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Communication

- Always respond in Simplified Chinese.
- Explain code changes in Chinese.
- Code comments: technical terms in English, explanations in Chinese where the file already mixes both (the de facto convention across `core/`, `pipeline/`, `papers/`).

## Project Overview

**news_process** is a research data pipeline that transforms raw Chinese news articles into panel datasets for econometric analysis. It processes bank and fintech news through multiple stages: preprocessing, classification, sentiment analysis (LLM/dictionary/BERT), and panel construction.

**Current version**: v3.8.0 (2026-05-31, remove-title-track, 移除提交 `6382cc67`)。

**v3.8.0 BREAKING** — 删除独立 `_title` 情感轨及全部产物, 标题改 prepend 进 full/ctx 两轨：
- 删 stage 39g (`track_discriminant_validity`) → STAGES_VALIDATION 18→17, 注册阶段共 **36** (STAGES_MAIN 19 + STAGES_VALIDATION 17), thin shim 40→**39**。
- 删 9 个 title 稳健性 Stata 模板 (`25_tableA8` / `26_bs`) → Stata 模板 104→**95**, replication 包 .do 15→**14**。
- 删 `core/text/title_indicators.py` + stage 13 `_add_title_indicators` + title-only migrate/audit 脚本与测试。
- 删所有 `*_title` 情感 panel 列 (`tone_gap_title_full` / `frac_title_*` / `hw_title` / `llm_peer_tone_iv_title` 等) 及 LLM/BERT/词典 title 路径; 下游多轨循环 `['_full','_ctx','_title']` 收为 `['_full','_ctx']`。
- 新增 `core/text/entity_context.py::prepend_title()`; stage 13 `ctx_materializer` 物化 `content_full`(=标题+正文) / `content_ctx`(=标题+实体窗口), 原始 `内容` 列不动; tone_words/tone_berts 改读 prepend 后文本。
- **保留** (非情感轨, 分类/β 显著性信号, 仍活跃, 勿连带删除): `target_bank_in_title` (`news_bank.py`) / `fintech_in_title`+`in_title` (`news_fintech.py`) / `headline_frac` (`controls.py`)。

**Disk 状态** (2026-06-03 实测): panel/.dta 已重生为 v3.8.0 两轨 schema (full/ctx), 无任何 `*_title` 情感列, golden snapshot 同步重生; ~176 行 (banks × 2 years 2017–2018, T=2)。列数详见 Stata 段, 随每次 panel 重生漂移, 以实读 .dta 为准。完整 LLM 重处理 (stage 21 等付费阶段) 仍受 M0 gate (见 memory `paper_portfolio_decision_gates`)。

**冻结锚点**: Prompt v8 字节级冻结 + `jieba == 0.42.1` (不重跑 stage 21, $0 LLM)。

**Test baseline** (v3.8.0 实测 2026-05-31): 全量 sweep **2581 passed / 3 skipped / 0 failed** (ruff clean)。精确 collect 数随 production run 漂移, 以 `pytest --collect-only` 为准; 历史逐版计数已失效, 不再维护。

> 历史版本 (v3.5.x–v3.7.5) 的完整 changelog 与 audit 记录见 git history。本文件顶部 "Current version" 段是版本变更的权威源 (CHANGELOG.md 暂未维护)。

**CLI 子命令** (`python -m news_process.papers._common.stata_runner <cmd>`):
- `build-replication`: 一键 instantiate 14 .do 模板 + spec 替换
- `list-templates [--verbose]`: 模板清单 + 占位符 inventory
- `doctor [--verbose]`: 5 段诊断 (deps + pipeline + LLM + Stata bin)
- `verify-replication <path>`: 5 段验证 replication 包结构

**v3.1.1 → v3.2.0 panel 迁移**: `python -m news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade`

## Architecture

### Pipeline Structure

The pipeline is a **declarative DAG** defined in `news_process/core/dag.py`. All stages are registered in `STAGES_MAIN` (production) or `STAGES_VALIDATION` (evaluation). The orchestrator (`run_pipeline_function.py`) executes stages as isolated subprocesses.

**Stage flow** (illustrative; authoritative set in `core/dag.py`):
```
00_preprocessing → 11_news_bank → 12_news_fintech → 13_materialize_ctx
→ 14_fintech_intensity → 15_article_policy_alignment
→ 21_tone_llms / 22_tone_words / 23_tone_berts → 24_herd_decay_processor
→ 45_panel_export_main → 46_stata_export → 51_falsification_test
```
`13_materialize_ctx` 物化 `content_ctx` 列, 让下游 14/15 在 stage 21 之前即可消费 ctx, 实现 fintech_intensity / policy_alignment 真双轨 (`*_full` / `*_ctx`)。stage 30 (`robustness_text2vec`) 已于 2026-05-29 退役 — `_t2v` 列改由 stage 15/25 inline 产出, 仅余 `30a_article_sbert`。

Sentiment methods (21/22/23) are conditionally enabled via `config/sentiment.yaml::sentiment_analysis.enabled_methods`.

### Directory Layout

```
news_process/
├── core/           # Kernel: config, logging, caching, DAG, stage runner
├── pipeline/       # Stage implementations (filtering, sentiment, panel, etc.)
├── papers/         # Multi-paper module dirs (11: 8 fully-coded + 3 provisional)
├── validation/     # Robustness tests (threshold sensitivity, entity masking, etc.)
├── config/         # Split YAML configs + prompt templates (config.yaml is a legacy stub)
├── data/           # Input (raw/) + output (processed/*.parquet)
├── tests/          # full sweep 2581 passed / 3 skipped / 0 failed (collect 数以 --collect-only 为准)
└── NN_*.py         # 39 thin shim scripts under news_process/ (≤30 lines each);
                    # 36 registered in core/dag.py (19 STAGES_MAIN + 17 STAGES_VALIDATION);
                    # 3 unregistered by design: 27c (audit-only sibling),
                    # 52/53 (user-CLI wrappers, schemas.py:182 显式排除).
                    # planned retirement Plan-r3 P3-18 (拆分约束见 pipeline/panel/runner.py:159).
```

**Key invariant**: `news_process/NN_*.py` scripts are thin shims. All logic lives in `news_process.pipeline.*`. Never add business logic to shims.

### Single Sources of Truth

1. **DAG**: `core/dag.py::STAGES_MAIN` / `STAGES_VALIDATION`
2. **Output registry**: `core/schemas.py::OUTPUT_REGISTRY` (stage → parquet files)
3. **Config**: split YAMLs in `config/{paths,preprocessing,filtering,sentiment,features,panel,validation}.yaml`
4. **Dependencies**: `pyproject.toml::[project].dependencies` (requirements.txt is a fallback)

### Data Flow

- **Input**: `data/raw/*.xlsx` (raw news articles)
- **Intermediate**: `data/processed/*.parquet` (one per stage, e.g., `21_tone_llms.parquet`)
- **Final**: `data/processed/40_panel_yearly.parquet` (bank-year panel for Stata)
- **Logs**: `logs/runs/<run_id>/<stage>.log` (one run_id per pipeline execution)

## Development Commands

### Environment Setup

```bash
# From repository root — create + activate virtual environment
python -m venv venv
source venv/bin/activate            # Linux/macOS
venv\Scripts\Activate.ps1           # Windows PowerShell (本项目主环境)

# Install dependencies (choose one)
pip install -e .                                  # Runtime deps only
pip install -e ".[dev]"                           # + dev tools (pytest, pre-commit, pytest-cov)
pip install -r news_process/requirements.lock && pip install -e . --no-deps  # Exact deps + editable
pip install -r news_process/requirements.txt  && pip install -e . --no-deps  # Fallback for pip-only users

# Configure environment
cp news_process/.env.example news_process/.env    # then set YUNWU_API_KEY (required for LLM stages)

# Enable local pre-commit hooks (one-time per dev machine)
pre-commit install                  # git commit auto-runs check-prompt-headers + ruff check
pre-commit run --all-files          # manual run against full repo
```

### Running the Pipeline

```bash
python run_pipeline_function.py     # Full pipeline (all enabled stages)
python run_pipeline_validation.py   # Validation pipeline (robustness tests)
python 21_tone_llms.py              # Single stage (for debugging)
```

### Testing

> **Run pytest from the repository root** (`f:\WiseSearch\data_antigravity_project\`). Running from the
> `news_process/` subdir may bypass the parent `pyproject.toml::testpaths`; root-level invocation is consistent.

```bash
pytest                              # full sweep (2581 passed / 3 skipped / 0 failed)
pytest -m fast                      # fast tests (~30s, run before every commit)
pytest -m integration               # integration tests (parquet IO, mocked LLM, ~5min)
pytest news_process/tests/test_21_tone_llms.py            # specific file
pytest -k "test_golden"             # tests matching pattern
```

### Linting & Formatting

```bash
ruff check .                        # Lint (configured in pyproject.toml)
ruff check --fix .                  # Auto-fix
```

### Regenerating Golden Baseline

After schema changes that add/remove columns:

```bash
python scripts/migrate/generate_golden_snapshot.py
pytest tests/integration/test_panel_reproducibility.py
```

## Critical Constraints

### Git Commit Protocol

1. **Never amend commits** unless explicitly requested. After pre-commit hook failures, create a NEW commit.
2. **Stage specific files** by name. Avoid `git add .` / `git add -A` (risk of committing `.env` or secrets).
3. **Commit message format**: HEREDOC with `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer.
4. **Never skip hooks** (`--no-verify`) unless explicitly requested.

### Code Modification Rules

1. **Stage shims are frozen**: The 39 `news_process/NN_*.py` scripts are thin shims (≤30 lines). All logic belongs in `news_process.pipeline.*` or `news_process.validation.*`.
2. **DAG consistency**: Any stage added/removed must update `core/dag.py::STAGES_MAIN`/`STAGES_VALIDATION` and `core/schemas.py::OUTPUT_REGISTRY` (if it produces parquet). Verify with `pytest tests/integration/test_dag_consistency.py`.
3. **Config split is active**: `core/config.py::load_config()` prefers the 7-domain YAML split and falls back to legacy single-file mode only when all split files are absent. Keep split files semantically equivalent to the legacy config contract.
4. **Golden baseline**: After column schema changes, regenerate `tests/fixtures/golden_panel_v0.json` via `scripts/migrate/generate_golden_snapshot.py`.

### Testing Requirements

- **Integration gate**: `tests/integration/test_panel_reproducibility.py` must pass (validates column hashes against golden baseline).
- **DAG consistency**: `tests/integration/test_dag_consistency.py` enforces STAGES_MAIN ⊆ OUTPUT_REGISTRY ∪ EXPECTED_NO_OUTPUT_STAGES, no duplicate stage names, and orchestrator imports matching `core/dag.py` (identity check via `is`).
- **Mock external APIs**: Tests must mock LLM/embedding APIs (see `tests/test_25_audit.py` for fixture examples).

## Common Patterns

### Adding a New Stage

1. Create implementation in `news_process/pipeline/<module>/<stage>.py`
2. Create thin shim `NN_<stage>.py` under `news_process/` (≤30 lines, imports and calls pipeline function)
3. Register in `core/dag.py::STAGES_MAIN` with `StageSpec(...)`
4. If it produces parquet, add to `core/schemas.py::OUTPUT_REGISTRY`
5. Add tests in `tests/test_XX_<stage>.py`
6. Run `pytest tests/integration/test_dag_consistency.py` to verify

### Modifying Config Schema

1. Edit the owning split YAML under `config/`
2. Update `core/config.py::load_config()` only if loader semantics change
3. Regenerate golden baseline if column schema changes
4. Run full test suite to catch downstream breakage

### Debugging Pipeline Failures

1. Check `logs/runs/<run_id>/<stage>.log` for the failed stage
2. Run the stage in isolation: `python news_process/NN_<stage>.py`
3. Use `pytest tests/test_XX_<stage>.py -v` to reproduce in test environment
4. Check `data/processed/` for intermediate outputs

## Environment Variables

Required in `.env`:

- `YUNWU_API_KEY`: Unified API key for LLM sentiment analysis (stages 21, 32a, 33, 34, 36, 39) and embedding (stage 15, 27)
- `EMBEDDING_API_KEY`: Defaults to `${YUNWU_API_KEY}` (can override for separate endpoint)
- `FINBERT2_MODEL_DIR`: Optional local BERT model path (stage 23 gracefully skips if missing)

## Multi-Paper Support

`papers/` contains 11 paper-specific module dirs (**8 fully-coded + 3 provisional**)。自 2026-06-01 全功能打开后, 全部 11 篇均具备 `analysis.py` (Stata runner, main+STAGES, --dry-run 可调度) + `figures.py` + `tables.py` 三件套, 并纳入 `paper_registry.PAPER_IDS_ALL` → `run_paper` 可调度全部 11 篇。provisional 三篇的表/图为 `build_table1`/`plot_*` 占位骨架 (主回归 esttab + manuscript/refs.bib 待 onboarding 填实)。

**P1–P5 Bank-FinTech 主线五篇** (统一 `bank_fintech_*` 命名):
- `bank_fintech_tone/` (P1, 主线): 媒体语调; 三轨化 spec, main = `llm_vote_tone_ctx`
- `bank_fintech_attention/` (P2): firm-level fintech attention intensity (Hassan 2019 QJE)
- `bank_fintech_substance/` (P3): W&Z 实质/象征二元属性
- `bank_fintech_locus/` (P4): Gomber 底层/应用二元属性
- `bank_fintech_collab/` (P5, provisional): Chesbrough 自主研发 vs 外部协同

**衍生 / provisional**: `benefit_society/` · `brokerage_network/` · `llm_peer/` (方法学) · `strategic_diff/` · `bank_media_disagreement/` (provisional) · `bank_news_clarity/` (provisional)。

Common utilities in `papers/_common/` (含 `AI_DISCLOSURE_TEMPLATES.md` 6 系列: Nature/AER/JF/ASQ/RP/CSSCI)。

> 注: 顶部 "Current version" 段中的 `P1/P2/P4/P7` 等指 **Plan E 内部步骤**, 与本段 paper-portfolio 的 `P1..P5` paper ID 是两个独立编号空间。

## Stata Environment

**本机 Stata：StataNow/MP 19.5** (2026-05-16 经 `about` 实测)。
- 路径 `C:\Program Files\StataNow19\StataMP-64.exe`; Build 14 Jan 2026; Windows 64-bit
- 许可 **64-core lab perpetual**; 物理内存 128 GB; 默认 `set maxvar = 5,000` (可上调到 MP 上限 120,000)
- **项目策略 (2026-05-16 起): Stata 19+ only, 无需向下兼容**

### 启动 Stata 的命令约定 (自动化必读 — 防「已完成」弹框)

**Windows 上跑 `.do` 一律用 `/b` 批处理 flag，禁用 `/e` 与裸 GUI 启动。** 弹「已完成」模态框需手动点确定的根因是启动模式不对：

- `StataMP-64.exe /b do x.do` — 真·批处理: 后台、跑完自动退出、不弹框 (本机实测退出码 0)。✅ 唯一推荐。
- `StataMP-64.exe /e do x.do` — 跑完弹模态完成框并阻塞等待点击, 卡死自动化。❌ 禁用。
- 无 flag / 双击 — GUI 交互模式, 同样卡。❌ 禁用。
- Windows 用斜杠 `/b` (不是 Unix 的 `-b`; `-b` 在 Windows 上不可靠)。Unix/Mac 才用 `stata-mp -b do x.do`。

推荐写法 (`StataMP-64.exe` 是 GUI 子系统程序, PowerShell `&` 调用会立即返回 → 必须 `Start-Process -Wait`):

```powershell
$exe = "C:\Program Files\StataNow19\StataMP-64.exe"
Start-Process -FilePath $exe -ArgumentList '/b','do','"<绝对路径\x.do>"' `
  -WorkingDirectory "<.do 所在目录>" -Wait -PassThru |
  ForEach-Object { "Stata 退出码=$($_.ExitCode)" }
# 跑完读同名 .log / .smcl 取结果
```

或用项目封装 `papers/_common/stata_runner.py::run_do(...)` (默认 `batch_mode=True` → 跨平台自动选 `/b`(Win) / `-b`(Unix), 从根上不弹框):

```python
from news_process.papers._common.stata_runner import run_do
cp = run_do(r"build\stata_verify\verify.do"); print(cp.returncode)
```

### 容量与列数 (MP 远未触顶)

MP 硬上限: max obs ≈ 1.1 兆 · maxvar 120,000 · RHS 65,532 · matsize 65,534 · macro 15,480,200 字符
(来源: https://www.stata.com/products/detailed-size-limits/)。当前 panel 最大 `51_panel_with_controls.dta` ≈ 1569 列 (2026-06-03 重生; 列数随每次重生漂移, 以实读为准), 距 MP 上限裕度 > 11.8 万列, 可放心继续加特征。

对本项目的含义:
- **`stata_export.py::STATA_IC_MAX_VARS = 2048` 是 IC 兼容性保留**, 不是本机限制。`core/aux` 双切分是给外部协作者用 IC 跑通预留的; 本机 MP 可直接读 `*_full.dta` 或 `51_panel_with_controls.dta` 跳过切分。
- **新增列优先扩 `aux.dta`, 保持 `core.dta` ≤ 2048**; 不要在通用模板里硬编码 "前 2048 列" 之类的 IC 截断逻辑。
- **行数瓶颈在面板深度 (T=2, ~176 行 = banks × 2 years 2017–2018)**, 不在 Stata 容量; panel 扩展瓶颈在上游数据 / stage 41。
- **64 核并行**: 跑 `bootstrap`/`permute`/`rwolf`/`ritest`/`csdid` wild bootstrap 时按 license 上限自动拉满 (`set processors 64`)。
- **matsize 在 Stata 19 已自动管理** (16+ deprecated); `reghdfe`/`ivreg2` 走 Mata 不受约束。仅原生 `regress` + 极多 RHS 才需显式 `set matsize`。

### Stata 模板约定

- **95 个 `.do.tmpl`** = 主线 14 (直接在 `stata_templates/` 下) + 8 个 paper-specific 子目录 78 (attention 7 / collab 8 / locus 8 / substance 9 / benefit_society 22 / brokerage_network 8 / llm_peer 8 / strategic_diff 8) + 历史归档 `v3_5_0/` 2 + `v3_5_1/` 1。全部统一头部 `version 19` + `clear all` + `set maxvar 32767` + `set linesize 120` (见 `00_master.do.tmpl:13-16`)。新增模板复用此头部。
- `version 19` 锁定最低版本: Stata 18 及更老会报 "version 19 is not a valid version" 拒跑 (这正是 "19+ only" 的执行机制), 可放心使用 `xtdidregress`/`frames`/`pystata`/新版 `meta` 等无需 `version` 守卫。
- `set maxvar 32767` 是防御性保留 (SE 上限); 若未来列数突破 32,767 需上调到 `set maxvar 120000`。
- **pyreadstat 写出的 `.dta` 用 format version 118** (`stata_export.py::_write_dta_pyreadstat` 走 pyreadstat 默认 118; pandas fallback `_write_dta_pandas_fallback` / `tables.py::export_dta` 显式 `version=118`; 实读 4 个 .dta header 均 release=118) — 这是 **.dta 文件格式 spec 编号**, 不是 Stata 应用版本; Stata 19 读取无限制。勿与 `version 19` 混为一谈。

## Known Issues & Workarounds

1. **Windows line endings**: Git may warn about CRLF (expected on Windows). The repo-root `.gitattributes` marks `*.parquet`/`*.xlsx`/`*.db` as binary; source files keep their on-disk EOL.
2. **FinBERT2 model**: Stage 23 requires a private fine-tuned model. If `FINBERT2_MODEL_DIR` is unset or invalid, the stage gracefully skips that model (other BERT models still run).

## Phase History

The project underwent 9 restructuring phases (v1.x → v2.1.0): package skeleton + DAG single-source (0-1) → split monoliths + OUTPUT_REGISTRY + acceptance gate (2) → multi-paper productization + 7-domain config split (3-7) → data layout normalization `data_processed/` → `data/processed/` (8) → cleanup (9). 后续版本演进见 git history; 当前 HEAD baseline 见顶部 "Current version" 段。
