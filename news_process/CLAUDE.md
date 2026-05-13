# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Communication

- Always respond in Simplified Chinese.
- Explain code changes in Chinese.
- Code comments: technical terms in English, explanations in Chinese where the file already mixes both (the de facto convention across `core/`, `pipeline/`, `papers/`).

## Project Overview

**news_process** is a research data pipeline that transforms raw Chinese news articles into panel datasets for econometric analysis. It processes bank and fintech news through multiple stages: preprocessing, classification, sentiment analysis (LLM/dictionary/BERT), and panel construction.

**Current version**: v2.1.0 + cleanup/2026-05-13 + Wave 0 (golden refresh + LLM snapshot metadata)
**Test baseline**: 851 passed / 2 skipped / 0 failed (refreshed 2026-05-13 after `f3a0000` + `1448611` prompt_version cache key migration)

## Architecture

### Pipeline Structure

The pipeline is a **declarative DAG** defined in `news_process/core/dag.py`. All stages are registered in `STAGES_MAIN` (production) or `STAGES_VALIDATION` (evaluation). The orchestrator (`run_pipeline_function.py`) executes stages as isolated subprocesses.

**Stage flow**:
```
00_preprocessing → 11_news_bank → 12_news_fintech → 14_fintech_intensity 
→ 15_article_policy_alignment → 21_tone_llms / 22_tone_words / 23_tone_berts 
→ 24_herd_decay_processor → 45_panel_export_main → 51_falsification_test
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
├── tests/          # 851 passed / 2 skipped HEAD baseline (integration + unit)
└── XX_*.py         # 23 thin shim scripts (≤30 lines each, delegate to pipeline/);
                    # planned retirement: Plan-r3 P3-18 (see docs/guides/thin_shim_pattern.md §11)
```

**Key invariant**: Root `XX_*.py` scripts are thin shims. All logic lives in `news_process.pipeline.*`. Never add business logic to root scripts.

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
pip install -e .                                  # Development: range versions from pyproject.toml
pip install -r news_process/requirements.lock && pip install -e . --no-deps  # Exact deps + editable package
pip install -r news_process/requirements.txt && pip install -e . --no-deps   # Fallback for pip-only users

# Configure environment
cp news_process/.env.example news_process/.env
# Edit .env: set YUNWU_API_KEY (required for LLM stages)
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

1. **Root scripts are frozen**: The 26 `XX_*.py` scripts are thin shims (≤30 lines). All logic belongs in `news_process.pipeline.*`.
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
2. Create thin shim `XX_<stage>.py` in project root (≤30 lines, imports and calls pipeline function)
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
2. Run the stage in isolation: `python XX_<stage>.py`
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

## Known Issues & Workarounds

1. **Windows line endings**: Git may warn about CRLF. This is expected on Windows; the project uses `.gitattributes` to normalize.
2. **FinBERT2 model**: Stage 23 requires a private fine-tuned model. If `FINBERT2_MODEL_DIR` is unset or invalid, the stage gracefully skips that model (other BERT models still run).

## Phase History

The project underwent 9 restructuring phases (v1.x → v2.1.0):
- **Phase 0-1**: Package skeleton + DAG single-source
- **Phase 2**: Split monoliths + OUTPUT_REGISTRY + acceptance gate
- **Phase 3-7**: Multi-paper productization + active 7-domain config split
- **Phase 8**: Data layout normalization (`data_processed/` → `data/processed/`)
- **Phase 9**: Cleanup of Phase 3/7a residue

Current HEAD baseline: **814 passed / 2 skipped / 0 failed**.
