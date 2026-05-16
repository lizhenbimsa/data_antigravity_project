"""Single source of truth for manual_validation_samples.xlsx schema.

Plan v1.37 P0 §3.3.1 (R23A-01 — sampling-script v3.2.0 migration is
tracked as a separate prerequisite ticket; this module captures the
expected schema for downstream evaluation).

Used by:
  - news_process/validation/llms_evaluation.py (P0 4-task extension)
  - news_process/tests/test_33_evaluation.py (test_r_column_schema_coupling)

The sampling script at news_process/scripts/migrate/manual_validation_sampling.py
populates rater-column NAMES via f-string templates
(`f'{rater}_stage3a_substantiveness'` for rater in ['R1','R2','R3']);
this module mirrors the templates as concrete constants.
"""
import pandas as pd

# 3-rater consensus design (plan v1.37 §3.3.1)
R_COLUMNS_BY_RATER = {
    'substantiveness': [
        'R1_stage3a_substantiveness',
        'R2_stage3a_substantiveness',
        'R3_stage3a_substantiveness',
    ],
    'locus': [
        'R1_stage3b_locus',
        'R2_stage3b_locus',
        'R3_stage3b_locus',
    ],
}


# Rater cell values may be in English (per sampling script L130-144);
# LLM predictions + Stata encoding use Chinese. Normalize before
# downstream comparison (R3C-01 + R5C-01).
_RATER_VALUE_TO_CANONICAL_LABEL_RAW = {
    'substantive': '实质性',
    'symbolic':    '象征性',
    'technology':  '底层技术',
    'application': '应用场景',
    # Already-Chinese pass-through
    '实质性': '实质性',
    '象征性': '象征性',
    '底层技术': '底层技术',
    '应用场景': '应用场景',
}


def normalize_rater_value(raw):
    """Normalize a rater cell value to canonical Chinese label or None.

    Rules (plan v1.37 §3.3.1 + R4A-02 + R5C-01):
      - None / pandas.isna(raw) / empty string → None (silent).
      - Bool / int / float that survives isna() → None (silent;
        openpyxl auto-typing artifacts).
      - Strings .strip()'d; English keys case-folded via .lower();
        Chinese keys (CJK unaffected by case folding) match directly.
      - Unknown strings (typos like 'subtantive') → None.
    """
    try:
        if raw is None or pd.isna(raw):
            return None
    except (TypeError, ValueError):
        pass
    if not isinstance(raw, str):
        return None
    s = raw.strip()
    if not s:
        return None
    return (_RATER_VALUE_TO_CANONICAL_LABEL_RAW.get(s)
            or _RATER_VALUE_TO_CANONICAL_LABEL_RAW.get(s.lower()))


def merge_three_rater_majority(row, rater_columns):
    """Three-rater majority-vote consensus for a single row.

    Returns canonical Chinese label or None.

    Rules (plan v1.37 §3.3.1):
      1. Normalize 3 cells via normalize_rater_value; drop None.
      2. 0 valid cells → None (skip from gold).
      3. Exactly 1 cell → None (insufficient inter-rater; R3C-13).
      4. ≥ 2 cells, ≥ 2 agree → majority label.
      5. Exactly 2 cells disagree (with 1 missing) → None (tie).
    """
    values = [normalize_rater_value(row.get(c)) for c in rater_columns]
    values = [v for v in values if v is not None]
    if len(values) == 0:
        return None
    if len(values) == 1:
        return None  # insufficient inter-rater confirmation
    # Counts
    from collections import Counter
    counts = Counter(values)
    most_common = counts.most_common(2)
    if most_common[0][1] >= 2:
        return most_common[0][0]
    return None  # 1-1 tie with missing 3rd, or 1-1-1 (impossible for binary)
