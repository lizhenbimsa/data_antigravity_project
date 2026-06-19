# Phase 2f — `config.yaml` Split Plan (historical; **执行完成于 Phase 4d**)

> **Status (post-v3.2.0)**: 本计划已落地。`config.yaml` 现为 stub, 7 个 split YAML
> (`paths/preprocessing/filtering/sentiment/features/panel/validation.yaml`) +
> 外部化 prompt 模板 + deep-merge loader 全部交付; 见
> `core/config.py::load_config()::_SPLIT_DOMAINS`. 本文档保留作历史记录,
> 实际运行时行为以代码为准。

The Phase 2 restructuring blueprint mandated splitting the 788-line monolithic
`config.yaml` into seven domain-specific YAML files plus externalized prompt
templates.  This was a non-trivial refactor that required:

1. Implementing deep-merge YAML loading in `news_process/core/config.py`.
2. Carefully mapping 20+ top-level sections to the 7 target files without
   accidental key collision.
3. Extracting the `tone_llm_processing.prompt_template` into a `.txt` file (not
   `.j2` — it uses `str.format()` placeholders, not Jinja2 syntax).
   （remove-title-track: 原计划同时外部化的 `title_sentiment_prompt_template`
   已随标题情感轨取消而移除，sentiment.yaml 不再含 `title_sentiment_prompt_template_file`。）
4. Updating each stage that reads these prompts to load them from disk.

Until that work lands, Phase 2 delivers everything else (Phase 2a/b/c/d/e/g
all complete).  Runtime semantics are unchanged; the existing monolithic
`config.yaml` continues to be the single source of truth.

## Target file layout (Phase 2f-2 deliverable)

```
config/
├── config.yaml                   # ← CURRENT SOURCE OF TRUTH (frozen during 2f-2)
├── paths.yaml                    # paths + filenames + parallel
├── preprocessing.yaml            # preprocessing + normalization + deduplication
├── filtering.yaml                # bank/fintech_news_classification + fintech_intensity
│                                 # + article_alignment + context_window
├── sentiment.yaml                # tone_llm_processing (sans prompts) + sentiment_analysis
│                                 # + herd_detection
├── features.yaml                 # embedding_api + benefit_society
├── panel.yaml                    # panel_building (temporal_mask_test 已随 stage 38a 于 2026-06-12 移除)
├── validation.yaml               # human_validation + validation
│                                 # + entity_masking_test + prompt_sensitivity_test
│                                 # + threshold_sensitivity
└── prompts/
    ├── unified_cot.txt           # ← extracted from tone_llm_processing.prompt_template
    └── fintech_rating_prompt.jinja2  # fintech rating prompt (jinja2)
```

## Loader change required

`core/config.py:load_config` currently does a single `yaml.safe_load`.
Phase 2f-2 must:

1. Detect whether per-domain YAMLs exist; if so, load each and **deep-merge**
   into a single config dict (paths.yaml supplies `paths:` + `filenames:` +
   `parallel:` keys; preprocessing.yaml supplies `preprocessing:`; etc.).
2. Continue working with the legacy monolithic `config.yaml` if no split
   files are present (backwards compatibility during transition).
3. Schema-validate the merged dict via pydantic (Phase 2f-2 adds models).

## Why deferred

Per the restructuring plan's design discipline, this refactor is fundamentally
file-organization work — high-volume, low-value-per-line, and benefits from
manual review of every section boundary to prevent accidental key duplication
or shadowing.  Sequencing it after Phase 2g's reproducibility test gate
ensures the column-hash baseline cannot be silently broken by a YAML edit.

## Acceptance for Phase 2f-2 (when unfrozen)

- All 7 split YAMLs created with all sections accounted for; `git diff` of
  the legacy `config.yaml` against the union of split files shows zero
  semantic delta.
- prompt templates externalized to disk; LLM stage runners updated to load them. (remove-title-track: 原计划抽取 tone_llm_processing.prompt_template + title_sentiment_prompt_template 两个模板; 标题情感轨取消后 prompts/title_sentiment.txt 已删除, 现仅 prompts/unified_cot.txt 一个由 config 外部化, 见 config/sentiment.yaml:59 与 config/config.yaml:16-19)
- `tests/integration/test_config_split_equivalence.py` asserts that
  `load_config()` produces an identical dict whether reading the legacy
  monolithic file or the new split files.
- `phase-1-baseline` reproducibility test (Phase 2g) still passes.
