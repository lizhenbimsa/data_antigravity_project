"""news_process.papers.benefit_society.ncd_field_parser
========================================================
NCD 抽取结果 → bank-year panel 结构化转换 + 字段验证

【输入】
- ncd_text_extractor.py 输出: extraction records JSON

【输出】
- bank-year panel parquet:
    columns = [bank_id, bank_name, year, total_assets, npl, car, profit, retail_dep, info_tech]

【校验】
- 字段范围检查 (npl ∈ [0, 50], car ∈ [5, 50], etc.)
- 与年报 / 监管披露三角对照 (R11 robustness)
- 异常值 flag (≥ 3 SD from group median)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 字段 schema
# ---------------------------------------------------------------------------
EXPECTED_FIELDS = {
    "bank_name": (str, None),
    "report_year": (int, (2010, 2030)),
    "total_assets_billion_rmb": (float, (0.5, 50_000)),
    "npl_ratio_pct": (float, (0.0, 50.0)),
    "car_ratio_pct": (float, (5.0, 50.0)),
    "net_profit_million_rmb": (float, (-100_000, 5_000_000)),
    "retail_deposit_billion_rmb": (float, (0.0, 30_000)),
    "info_tech_invest_million_rmb": (float, (0.0, 100_000)),
}


# ---------------------------------------------------------------------------
# 字段验证
# ---------------------------------------------------------------------------
def validate_field(field_name: str, value: Any) -> tuple[bool, str]:
    """Validate a single field's type and range.

    Returns
    -------
    (is_valid, error_msg)
    """
    if value is None:
        return True, ""  # null is acceptable (missing data)
    if field_name not in EXPECTED_FIELDS:
        return False, f"unknown field: {field_name}"

    expected_type, expected_range = EXPECTED_FIELDS[field_name]
    if not isinstance(value, expected_type):
        if expected_type is float and isinstance(value, int):
            value = float(value)
        elif expected_type is int and isinstance(value, float) and value.is_integer():
            value = int(value)
        else:
            return False, f"type mismatch: expected {expected_type.__name__}, got {type(value).__name__}"

    if expected_range is not None and not (expected_range[0] <= value <= expected_range[1]):
        return False, f"out of range [{expected_range[0]}, {expected_range[1]}]: {value}"

    return True, ""


def validate_record(parsed: dict) -> tuple[dict, list[str]]:
    """Validate all fields in a parsed record.

    Returns
    -------
    (cleaned_record, list_of_warnings)
    """
    warnings: list[str] = []
    cleaned: dict = {}
    for field_name in EXPECTED_FIELDS:
        value = parsed.get(field_name)
        is_valid, err = validate_field(field_name, value)
        if is_valid:
            cleaned[field_name] = value
        else:
            warnings.append(f"  {field_name}: {err}")
            cleaned[field_name] = None
    return cleaned, warnings


# ---------------------------------------------------------------------------
# Bank-year panel 构建
# ---------------------------------------------------------------------------
def records_to_panel(records: list[dict], bank_id_lookup: dict[str, str] | None = None) -> pd.DataFrame:
    """Convert extraction records to bank-year DataFrame.

    Parameters
    ----------
    records : list of dict
        Each dict must have 'response_parsed' (the validated fields) + 'pdf_path' (for bank_id inference)
    bank_id_lookup : optional
        ``{bank_name -> target_bank}`` mapping. ``target_bank`` is the canonical
        identifier used by the main pipeline panel ([40_panel_yearly.parquet]);
        if None, falls back to ``bank_name`` verbatim.

    Returns
    -------
    DataFrame with columns:
        bank_id, bank_name, year, total_assets, npl, car, profit, retail_dep, info_tech, source_pdf

    Note
    ----
    The returned column ``bank_id`` is the lookup result — when merging with the
    main panel, rename to ``target_bank`` to align with pipeline convention.
    """
    rows: list[dict] = []
    for rec in records:
        parsed = rec.get("response_parsed")
        if parsed is None:
            continue

        cleaned, warns = validate_record(parsed)
        if warns:
            logger.warning(f"PDF {rec.get('pdf_path', '?')}:")
            for w in warns:
                logger.warning(w)

        bank_name = cleaned.get("bank_name")
        if bank_name is None:
            continue

        bank_id = bank_id_lookup.get(bank_name, bank_name) if bank_id_lookup else bank_name

        rows.append({
            "bank_id": bank_id,
            "bank_name": bank_name,
            "year": cleaned.get("report_year"),
            "total_assets": cleaned.get("total_assets_billion_rmb"),
            "npl": cleaned.get("npl_ratio_pct"),
            "car": cleaned.get("car_ratio_pct"),
            "profit": cleaned.get("net_profit_million_rmb"),
            "retail_dep": cleaned.get("retail_deposit_billion_rmb"),
            "info_tech": cleaned.get("info_tech_invest_million_rmb"),
            "source_pdf": rec.get("pdf_path", ""),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # Deduplicate (keep latest source_pdf for each bank-year)
    df = df.sort_values(["bank_id", "year", "source_pdf"])
    df = df.drop_duplicates(subset=["bank_id", "year"], keep="last").reset_index(drop=True)
    return df


# ---------------------------------------------------------------------------
# 异常值检测 (≥ 3 SD)
# ---------------------------------------------------------------------------
def flag_outliers(
    df: pd.DataFrame,
    *,
    numeric_cols: tuple[str, ...] = ("total_assets", "npl", "car", "profit", "retail_dep", "info_tech"),
    sd_threshold: float = 3.0,
) -> pd.DataFrame:
    """Add boolean ``outlier_<col>`` columns flagging values > sd_threshold robust SD from median.

    Uses MAD (median absolute deviation) scaled by 1.4826 as a robust SD estimator
    (Rousseeuw & Croux 1993). MAD is not inflated by the outliers it is meant to
    detect, unlike sample SD.
    """
    df = df.copy()
    for col in numeric_cols:
        if col not in df.columns:
            continue
        med = df[col].median()
        deviations = (df[col] - med).abs()
        mad = deviations.median()
        robust_sd = 1.4826 * mad  # scale factor under Gaussian assumption
        if not np.isfinite(robust_sd) or robust_sd == 0:
            df[f"outlier_{col}"] = False
            continue
        df[f"outlier_{col}"] = (deviations / robust_sd) > sd_threshold
    return df


# ---------------------------------------------------------------------------
# 三角对照 (R11)
# ---------------------------------------------------------------------------
def triangulate_with_annual_report(
    ncd_panel: pd.DataFrame,
    annual_report_panel: pd.DataFrame,
    *,
    join_keys: tuple[str, str] = ("bank_id", "year"),
    fields_to_compare: tuple[str, ...] = ("total_assets", "npl", "car"),
    tolerance_pct: float = 5.0,
) -> pd.DataFrame:
    """Compare NCD-extracted fields with annual-report fields, flagging discrepancies.

    Returns
    -------
    DataFrame with columns ``inconsistent_<field>`` (bool) for each compared field.
    """
    merged = ncd_panel.merge(
        annual_report_panel,
        on=list(join_keys),
        how="inner",
        suffixes=("_ncd", "_ar"),
    )
    for f in fields_to_compare:
        ncd_col = f"{f}_ncd"
        ar_col = f"{f}_ar"
        if ncd_col not in merged.columns or ar_col not in merged.columns:
            continue
        diff_pct = (merged[ncd_col] - merged[ar_col]).abs() / merged[ar_col].replace(0, np.nan).abs() * 100
        merged[f"inconsistent_{f}"] = diff_pct > tolerance_pct
    return merged


def main(argv: list[str] | None = None) -> int:
    """CLI entry: convert NCD extraction records JSON to bank-year panel parquet.

    Performs schema validation, outlier flagging, and optional R11 triangulation
    against annual-report data. Returns 0 on success, 1 if input JSON not found.
    """
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.ncd_field_parser",
        description="NCD 抽取结果 → bank-year panel + 字段验证",
    )
    parser.add_argument(
        "--extracted-json",
        type=str,
        default="news_process/data/intermediate/ncd_extracted.json",
    )
    parser.add_argument(
        "--bank-id-map",
        type=str,
        default=None,
        help="Optional CSV with columns [bank_name, bank_id]",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="news_process/data/processed/ncd_panel.parquet",
    )
    parser.add_argument(
        "--annual-report",
        type=str,
        default=None,
        help="Optional annual-report panel parquet for R11 triangulation",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

    extracted_path = Path(args.extracted_json)
    if not extracted_path.exists():
        logger.error(f"Extracted JSON not found: {extracted_path}")
        return 1

    payload = json.loads(extracted_path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    logger.info(f"Loaded {len(records)} extraction records")

    bank_id_lookup = None
    if args.bank_id_map:
        import csv
        with open(args.bank_id_map, encoding="utf-8") as f:
            bank_id_lookup = {row["bank_name"]: row["bank_id"] for row in csv.DictReader(f)}

    panel = records_to_panel(records, bank_id_lookup=bank_id_lookup)
    logger.info(f"Built panel: {panel.shape}")

    panel = flag_outliers(panel)
    n_outliers = sum(panel[c].sum() for c in panel.columns if c.startswith("outlier_"))
    logger.info(f"Flagged {n_outliers} outlier cells")

    if args.annual_report and Path(args.annual_report).exists():
        ar_panel = pd.read_parquet(args.annual_report)
        triangulation = triangulate_with_annual_report(panel, ar_panel)
        inconsistent_cols = [c for c in triangulation.columns if c.startswith("inconsistent_")]
        n_inconsistent = sum(triangulation[c].sum() for c in inconsistent_cols)
        logger.info(f"R11 triangulation: {n_inconsistent} inconsistent rows across {len(inconsistent_cols)} fields")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    logger.info(f"Wrote panel to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
