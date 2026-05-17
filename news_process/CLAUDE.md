# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Communication

- Always respond in Simplified Chinese.
- Explain code changes in Chinese.
- Code comments: technical terms in English, explanations in Chinese where the file already mixes both (the de facto convention across `core/`, `pipeline/`, `papers/`).

## Project Overview

**news_process** is a research data pipeline that transforms raw Chinese news articles into panel datasets for econometric analysis. It processes bank and fintech news through multiple stages: preprocessing, classification, sentiment analysis (LLM/dictionary/BERT), and panel construction.

**Current version**: v3.4.0 (Stage 3 第三维度对称扩张 + P5 立项 + epoch 5 audit;
继承 v3.3.0 multi-paper extension closed + v3.2.0 BREAKING Stage 3 双轨化 + Stata 数据导出层;
Prompt v7 → v8 (additive supplementation per Nosek 2018 PNAS; v7 严格超集);
v3.4.0 BREAKING (2026-05-17): 新增 `innovation_collab_mode_{full,ctx}` + confidence_{full,ctx}
4 LLM 列 (Chesbrough 2003 Open Innovation + Laursen & Salter 2006 SMJ 27:131-150;
positive_class=外部协同; Stata byte 编码 0=自主研发 / 1=外部协同);
面板聚合新增 ~30 列 (_indep / _collab 后缀; encode.py 第三维度 if-block);
codebook + stata_export 同步; v3_3_to_v3_4 panel migration script + 11 tests;
P5 立项 `bank_fintech_collab` (Master plan v2.55 → v2.56 epoch 5 audit, streak 3/3 pending);
61 Stata templates (P5 6 个新增 + bank_fintech_collab/ 子目录); 12 双语 manuscripts (P5 zh + en 新增);
git tag `prompt-v8-supplementation-released` 锚定 v3.4.0 baseline,
`prompt-v7-released` 永不删除作 pre-registration anchor;
LLM cost cap 4200 → 5000 (10% 裕度); calibration v5.2 delta 9 strata × 450 obs × 3 raters 文档化;
锚定: 继承 v3.3.0 anchors + Chesbrough 2003 + Laursen & Salter 2006 SMJ + Cohen-Levinthal 1990 ASQ;
详见 CHANGELOG.md v3.4.0)
**Test baseline**: 1153 → ~1175 passed / 6 skipped / 0 failed (v3.4.0 +25 测试: 11 migration + 14 panel/stata/integration; 3 stale baseline failures from v3.3.0 main 不属于 v3.4.0 引入)

**CLI 子命令** (`python -m news_process.papers._common.stata_runner <cmd>`):
- `build-replication`: 一键 instantiate 14 .do 模板 + spec 替换
- `list-templates [--verbose]`: 14 模板清单 + 占位符 inventory
- `doctor [--verbose]`: 5 段诊断 (deps + pipeline + LLM + Stata bin)
- `verify-replication <path>`: 5 段验证 replication 包结构

**v3.1.1 → v3.2.0 panel 迁移**: `python -m news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade`

## Architecture

### Pipeline Structure

The pipeline is a **declarative DAG** defined in `news_process/core/dag.py`. All stages are registered in `STAGES_MAIN` (production) or `STAGES_VALIDATION` (evaluation). The orchestrator (`run_pipeline_function.py`) executes stages as isolated subprocesses.

**Stage flow** (v3.2.0):
```
00_preprocessing → 11_news_bank → 12_news_fintech → 14_fintech_intensity 
→ 15_article_policy_alignment → 21_tone_llms / 22_tone_words / 23_tone_berts 
→ 24_herd_decay_processor → 45_panel_export_main → 46_stata_export → 51_falsification_test
```

Sentiment methods (21/22/23) are conditionally enabled via `config/sentiment.yaml::sentiment_analysis.enabled_methods`.

### Directory Layout

```
news_process/
├── core/           # Kernel: config, logging, caching, DAG, stage runner
├── pipeline/       # Stage implementations (filtering, sentiment, panel, etc.)
├── papers/         # Multi-paper analysis modules (5 papers supported)
├── validation/     # Robustness tests (threshold sensitivity, entity masking, etc.)
├── config/         # Split YAML configs + prompt templates (config.yaml is a legacy stub)
├── data/           # Input (raw/) + output (processed/*.parquet)
├── tests/          # 1153 passed / 6 skipped HEAD baseline (integration + unit)
└── NN_*.py         # 27 thin shim scripts under news_process/ (≤30 lines each,
                    # NN ∈ {00, 11, 12, 14, 15, 21..24, 30..39 incl. 32a/38a/38b, 45..46, 51..53};
                    # delegate to pipeline/; planned retirement: Plan-r3 P3-18
                    # (拆分约束见 pipeline/panel/runner.py:159)
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
# From repository root
# Create virtual environment
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows cmd.exe:
venv\Scripts\activate
# Windows PowerShell (本项目主环境):
venv\Scripts\Activate.ps1

# Install dependencies (choose one)
pip install -e .                                  # Development: runtime deps only
pip install -e ".[dev]"                           # Development + dev tools (pytest, pre-commit, pytest-cov)
pip install -r news_process/requirements.lock && pip install -e . --no-deps  # Exact deps + editable package
pip install -r news_process/requirements.txt && pip install -e . --no-deps   # Fallback for pip-only users

# Configure environment
cp news_process/.env.example news_process/.env
# Edit .env: set YUNWU_API_KEY (required for LLM stages)

# V4 T1.4: enable local pre-commit hooks (one-time per dev machine)
pre-commit install
# Now `git commit` auto-runs: check-prompt-headers + ruff check
# Manual run against full repo: pre-commit run --all-files
```

### Running the Pipeline

```bash
# Full pipeline (all enabled stages)
python run_pipeline_function.py

# Validation pipeline (robustness tests)
python run_pipeline_validation.py

# Single stage (for debugging)
python 21_tone_llms.py
```

### Testing

> **Must run pytest from the repository root** (`f:\WiseSearch\data_antigravity_project\`).
> Running from `news_process/` subdir may bypass the parent `pyproject.toml::testpaths`
> setting; the `news_process/conftest.py::collect_ignore_glob` covers the common case
> (excluding `data/`), but root-level invocation gives consistent behavior.

```bash
# Run all tests (from repo root)
pytest

# Run specific test file
pytest news_process/tests/test_21_tone_llms.py

# Run specific test
pytest news_process/tests/test_21_tone_llms.py::TestToneLLMs::test_basic_flow

# Run integration tests only
pytest news_process/tests/integration/

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_golden"

# V4 T1.6: tiered runs (auto-tagged by tests/conftest.py)
pytest -m fast              # 759 unit tests (~30s, run before every commit)
pytest -m integration       # 94 integration tests (parquet IO, mocked LLM, ~5min)
pytest                       # full sweep (851 + 2 skipped)
```

### Linting & Formatting

```bash
# Lint with ruff (configured in pyproject.toml)
ruff check .

# Auto-fix issues
ruff check --fix .

# Check specific file
ruff check news_process/core/config.py
```

### Regenerating Golden Baseline

After schema changes that add/remove columns:

```bash
python scripts/migrate/generate_golden_snapshot.py
pytest tests/integration/test_panel_reproducibility.py
```

## Critical Constraints

### Git Commit Protocol

1. **Never amend commits** unless explicitly requested. After pre-commit hook failures, create a NEW commit (amending would modify the wrong commit).
2. **Stage specific files** by name. Avoid `git add .` or `git add -A` (risk of committing `.env` or secrets).
3. **Commit message format**: Use HEREDOC with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer.
4. **Never skip hooks** (`--no-verify`) unless explicitly requested.

### Code Modification Rules

1. **Stage shims are frozen**: The 26 `news_process/NN_*.py` scripts are thin shims (≤30 lines; NN includes lettered variants 32a/38a/38b). All logic belongs in `news_process.pipeline.*` or `news_process.validation.*`.
2. **DAG consistency**: Any stage added/removed must update:
   - `core/dag.py::STAGES_MAIN` or `STAGES_VALIDATION`
   - `core/schemas.py::OUTPUT_REGISTRY` (if it produces parquet)
   - Run `pytest tests/integration/test_dag_consistency.py` to verify
3. **Config split is active**: `core/config.py::load_config()` prefers the 7-domain YAML split and falls back to legacy single-file mode only when all split files are absent. Keep split files semantically equivalent to the legacy config contract.
4. **Golden baseline**: After column schema changes, regenerate `tests/fixtures/golden_panel_v0.json` via `scripts/migrate/generate_golden_snapshot.py`.

### Testing Requirements

- **Integration gate**: `tests/integration/test_panel_reproducibility.py` must pass (validates column hashes against golden baseline).
- **DAG consistency**: `tests/integration/test_dag_consistency.py` enforces:
  - All `STAGES_MAIN` entries are in `OUTPUT_REGISTRY` or `EXPECTED_NO_OUTPUT_STAGES`
  - No duplicate stage names across STAGES_MAIN / STAGES_VALIDATION
  - Orchestrator imports match `core/dag.py` (identity check via `is`)
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

The `papers/` directory contains 5 paper-specific analysis modules:
- `bank_fintech_tone/`: Main paper (bank-fintech sentiment)
- `benefit_society/`: Social benefit analysis
- `brokerage_network/`: Network brokerage effects
- `llm_peer/`: LLM peer review
- `strategic_diff/`: Strategic differentiation

Each paper has `analysis.py` (Stata runner), `figures.py`, and `tables.py`. Common utilities are in `papers/_common/`.

## Stata Environment

**本机 Stata：StataNow/MP 19.5**（2026-05-16 通过 `about` 命令实测确认）。
- 安装路径：`C:\Program Files\StataNow19\StataMP-64.exe`（115 MB）
- Build：Revision **14 Jan 2026**（StataNow 滚动通道；非年度主版 19.0）
- 平台：Windows 64-bit x86-64
- 许可：**64-core lab perpetual**（MP 并行核心数 = 64）
- 硬件：物理内存 128 GB，可用 98 GB
- 默认 `set maxvar = 5,000`（已高于 IC 上限 2,048，可一直上调到 MP 上限 120,000）
- License note：Unicode 支持开启，>2 billion observations 允许

所有 `.do` 模板、replication 脚本与下游回归（reghdfe / ivreg2 / csdid / sdid /
synth / coefplot 等）以 MP 上限为天花板编写。

### Stata/MP vs SE vs BE 技术上限（Stata 19 官方文档，2026-05 抓取；19 vs 18 硬上限未变）

| 限制项 | Stata/BE | Stata/SE | **Stata/MP（本机）** |
|---|---:|---:|---:|
| Max observations | 2,147,483,619 | 2,147,483,619 | **1,099,511,627,775** (≈1.1 兆) |
| Max variables (`maxvar`) | 2,048 | 32,767 | **120,000** |
| Max RHS variables in model | 798 | 10,998 | **65,532** |
| matrix dimension (`matsize`) | 800 × 800 | 11,000 × 11,000 | **65,534 × 65,534** |
| String var `str#` | 2,045 bytes | 2,045 bytes | 2,045 bytes |
| String var `strL` | 2 GB | 2 GB | 2 GB |
| Variable name length | 32 chars | 32 chars | 32 chars |
| Variable label length | 80 chars | 80 chars | 80 chars |
| Value label string | 32,000 bytes | 32,000 bytes | 32,000 bytes |
| Characters in command | 264,408 | 4,227,159 | 4,227,159 |
| Characters in macro | 264,392 | 4,227,143 | **15,480,200** |

来源：https://www.stata.com/products/detailed-size-limits/ +
https://www.stata.com/products/which-stata-is-right-for-me/

### 对本项目（v3.2.0）的含义

1. **当前列数全部在 MP 上限内、远未触顶**：
   - `46_panel_yearly_full.dta` / `40_panel_yearly.dta`：2024 列
   - `46_panel_yearly_core.dta`：49 列（IC 兼容入口）
   - `46_panel_yearly_aux.dta`：1977 列（与 core 互补，merge 1:1 可还原 full）
   - `51_panel_with_controls.dta`：**2033 列（当前最大）**
   - **裕度**：MP 上限 120,000 − 2033 ≈ **117,967 列**，可放心继续加稳健性 / BERT 变体特征。
2. **`pipeline/panel/stata_export.py::STATA_IC_MAX_VARS = 2048` 是 IC 兼容性保留**，
   不是本机限制。`core / aux` 双切分是为外部协作者用 IC 跑通预留的；本机 MP 可
   直接读 `*_full.dta` 或 `51_panel_with_controls.dta` 跳过切分。
3. **matsize 在 Stata 19 已自动管理（Stata 16+ 起 deprecated）**：MP 19.5
   下 `set matsize` 仍可设但被 Stata 内部统一处理，`reghdfe` / `ivreg2`
   等主流命令走 Mata 矩阵不受 matsize 约束。仅在使用 `regress` 原生命令 +
   极多 RHS 时才需要显式 `set matsize 11000`（SE 上限）或更高。
4. **行数维度**：当前 panel 168 行（84 banks × 2 years, 2017–2018）远低于
   MP 上限 1.1 兆，受限的是**面板深度（T=2）**而非 Stata 容量；任何 panel
   扩展瓶颈都在上游数据来源 / stage 41，不在 Stata。
5. **64 核并行**：MP 19.5 license 是 64-core，跑 `bootstrap`、`permute`、
   `rwolf`、`ritest`、`csdid` 多重 placebo / wild bootstrap 时可拉满
   `set processors 64`（默认按 license 上限走，无需手动）；这是当前 v3.2.0
   稳健性矩阵性能上的关键资源。

### 修改 Stata 配置时的注意

- **不要在通用模板中硬编码 BE/IC 才有意义的列截断逻辑**：若发现 .do 模板里
  写了 "前 2048 列" 之类的截断，那是 IC 兼容遗留，本机 MP 应改读 full 版本。
- **新增列时优先扩 `aux.dta`，保持 `core.dta` ≤ 2048**：保留 IC 协作者的
  入口契约，不要因为本机是 MP 就把 core 撑爆。
- **项目策略 (2026-05-16 起): Stata 19+ only, 无需向下兼容**。
  `papers/_common/stata_templates/*.do.tmpl` 全部 46 个模板已统一 bump 为
  `version 19` + `clear all` + `set maxvar 32767` + `set linesize 120`
  （见 `00_master.do.tmpl:13-16`）。新增模板直接复用此头部。
- **可放心使用 v17+ / v19 独有命令**: `xtdidregress` (v17)、`frames` 增强
  (v16/v18)、`bayesmh` GPU、`pystata` 集成、新版 `meta` suite 等无需任何
  `version` 守卫；`version 19` 已锁定最低要求。
- **设置 `version 19` 的副作用**: Stata 18 及更老版本会直接报
  "version 19 is not a valid version" 拒跑 — 这正是 "19+ only" 策略的
  执行机制。外部协作者若仍在 Stata 18，需先升级再跑 replication 包。
- **`set maxvar 32767` 仍是防御性保留**: 本机 MP 19.5 默认 5,000 对当前
  2033 列已够用，但 stage 46 输出可能继续向 IC 上限 2048 逼近；这一行让
  模板独立于 maxvar 默认值（不论用户是 MP / SE）都能装下 full .dta。
  ⚠ `maxvar 32767` 是 SE 上限；如果未来 panel 列数突破 32,767（远期），
  需上调到 `set maxvar 120000`（MP 上限）。
- **pyreadstat 写出的 `.dta` 仍用 format version 118**（见
  `pipeline/panel/stata_export.py:369`、`papers/_common/tables.py:102`）。
  这是 **.dta 文件格式版本**（spec 编号），不是 Stata 应用程序版本；
  118 是 pyreadstat 当前能稳定写出的最高 .dta spec，Stata 19 读取无任何
  限制（变量名 32 字符 / value label 32K bytes 等都满足）。不要把它和
  `version 19` 混为一谈。

## Known Issues & Workarounds

1. **Windows line endings**: Git may warn about CRLF. This is expected on Windows. The repo-root `.gitattributes` marks `*.parquet`/`*.xlsx`/`*.db` as binary; source files keep their on-disk EOL (no forced normalization to avoid churning the existing mixed-CRLF history).
2. **FinBERT2 model**: Stage 23 requires a private fine-tuned model. If `FINBERT2_MODEL_DIR` is unset or invalid, the stage gracefully skips that model (other BERT models still run).

## Phase History

The project underwent 9 restructuring phases (v1.x → v2.1.0):
- **Phase 0-1**: Package skeleton + DAG single-source
- **Phase 2**: Split monoliths + OUTPUT_REGISTRY + acceptance gate
- **Phase 3-7**: Multi-paper productization + active 7-domain config split
- **Phase 8**: Data layout normalization (`data_processed/` → `data/processed/`)
- **Phase 9**: Cleanup of Phase 3/7a residue

Current HEAD baseline tracked in line 16 (top of file).
