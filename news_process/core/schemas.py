"""news_process.core.schemas — column contracts + ``OUTPUT_REGISTRY`` (Phase 2d).

Phase 2d delivers the single-source ``OUTPUT_REGISTRY`` mapping every stage
script name to the parquet outputs it produces.  Both the orchestrator
(for stale-data pre-cleanup) and stage runners (for write-path resolution)
will consume this dict.

Phase 1 had the orchestrator hold a private ``_get_stage_output_files``
hardcode while stages independently read filenames from
``CONFIG['filenames']['output_XX_*']`` — a textbook double-source-of-truth
hazard.  Phase 2d eliminates the divergence at this single registry.

The registry preserves the legacy parquet-filename contract verbatim so
that existing files in ``data_processed/`` remain reachable through the
new abstraction.
"""

from __future__ import annotations

from typing import Mapping


# Stage-script name (legacy root filename, used for backward compatibility) →
# list of output parquet filenames produced.  Pipeline stages whose runner
# main() writes ZERO parquet outputs (e.g. validation runners that emit
# eval_reports/*.csv) are intentionally absent here; the orchestrator
# treats absence as "no pre-cleanup needed".
OUTPUT_REGISTRY: Mapping[str, list[str]] = {
    # Module 1: preprocess
    "00_preprocessing.py": ["00_preprocessing.parquet"],
    # Module 2: filtering
    "11_news_bank.py": ["11_bank_news.parquet"],
    "12_news_fintech.py": [
        "12_fintech_news.parquet",
        "12_fintech_news_full.parquet",
    ],
    "14_fintech_intensity.py": ["14_fintech_intensity.parquet"],
    "15_article_policy_alignment.py": ["15_article_alignment.parquet"],
    # Module 3: sentiment
    "21_tone_llms.py": [
        "21_tone_llms.parquet",
        "21_tone_llms_full.parquet",
    ],
    "22_tone_words.py": ["22_words_tone.parquet"],
    "23_tone_berts.py": ["23_bert_tone.parquet"],
    "24_herd_decay_processor.py": ["24_herd_decay.parquet"],
    # Module 5: panel construction (45 emits the bank-year + article-bank panels)
    "45_panel_export_main.py": [
        "40_panel_yearly.parquet",
        "40_article_bank_level.parquet",
        "40_attn_index_year.parquet",
        "40_attn_index_province_year.parquet",
        "40_attn_index_city_year.parquet",
    ],
    # Module 6: falsification
    "51_falsification_test.py": ["51_panel_with_controls.parquet"],
}


def get_stage_outputs(stage_script: str) -> list[str]:
    """Return parquet filenames produced by a given stage script (or empty list)."""
    return list(OUTPUT_REGISTRY.get(stage_script, []))


__all__ = ["OUTPUT_REGISTRY", "get_stage_outputs"]
