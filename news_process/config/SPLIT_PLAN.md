# Phase 2f — `config.yaml` Split Plan (deferred execution)

The Phase 2 restructuring blueprint mandates splitting the 788-line monolithic
`config.yaml` into seven domain-specific YAML files plus externalized prompt
templates.  This is a non-trivial refactor that requires:

1. Implementing deep-merge YAML loading in `news_process/core/config.py`.
2. Carefully mapping 20+ top-level sections to the 7 target files without
   accidental key collision.
3. Extracting 4 multi-line Prompt templates (`tone_llm_processing.prompt_template`
   / `title_sentiment_prompt_template`) into `.txt` files (not `.j2` — they use
   `str.format()` placeholders, not Jinja2 syntax).
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
├── panel.yaml                    # panel_building + temporal_mask_test
├── validation.yaml               # human_validation + validation
│                                 # + entity_masking_test + prompt_sensitivity_test
│                                 # + threshold_sensitivity
└── prompts/
    ├── unified_cot.txt           # ← extracted from tone_llm_processing.prompt_template
    └── title_sentiment.txt       # ← extracted from title_sentiment_prompt_template
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
- 4 prompt templates extracted; LLM stage runners updated to load from disk.
- `tests/integration/test_config_split_equivalence.py` asserts that
  `load_config()` produces an identical dict whether reading the legacy
  monolithic file or the new split files.
- `phase-1-baseline` reproducibility test (Phase 2g) still passes.
