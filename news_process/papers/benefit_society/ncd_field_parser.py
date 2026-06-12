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

# fix(omni-gapfill-12, 2026-06-12): prompt Rule 1 "亿元" 与 *_billion_rmb 字段名
# 冲突 10× (1 billion = 10 亿; prompt 冻结不可改 → 解析侧启发式探测, 见
# ncd_text_extractor.EXTRACTION_PROMPT 上方披露)。命中条件: 值越上界但 ÷10 落回
# 区间 → 高度疑似 LLM 按 亿元 回答; 标记而非静默置 None。
_UNIT_SUSPECT_FIELDS = ("total_assets_billion_rmb", "retail_deposit_billion_rmb")


def detect_unit_mismatch(field_name: str, value: Any) -> bool:
    """10× 单位错误启发式 (亿元 vs billion): 越上界但 ÷10 在区间内 → True。"""
    if field_name not in _UNIT_SUSPECT_FIELDS or not isinstance(value, (int, float)):
        return False
    lo, hi = EXPECTED_FIELDS[field_name][1]
    return value > hi and lo <= value / 10.0 <= hi


# ---------------------------------------------------------------------------
# 字段验证
# ---------------------------------------------------------------------------
def validate_field(field_name: str, value: Any) -> tuple[bool, str]:
    """校验单个字段的类型与取值范围.

    Returns
    -------
    (is_valid, error_msg)
    """
    if value is None:
        return True, ""  # null 可接受 (缺失数据)
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
    """校验解析记录中的全部字段.

    Returns
    -------
    (cleaned_record, list_of_warnings)
    """
    warnings: list[str] = []
    cleaned: dict = {}
    unit_suspects: list[str] = []
    for field_name in EXPECTED_FIELDS:
        value = parsed.get(field_name)
        is_valid, err = validate_field(field_name, value)
        if is_valid:
            cleaned[field_name] = value
        elif detect_unit_mismatch(field_name, value):
            # fix(omni-gapfill-12, 2026-06-12): 越界 + ÷10 落回区间 → 疑似 prompt
            # Rule 1 亿元/billion 10× 单位错误。不静默置 None 了之: 显式警告 +
            # 记入 _unit_suspect_fields (records_to_panel 旁路列), 供人工/三角
            # 对照 (triangulate unit_mismatch_*) 裁决; 值本身仍置 None (不自动
            # ÷10 改写 — 无年报对照时缩放同样可能是错的)。
            unit_suspects.append(field_name)
            warnings.append(
                f"  {field_name}: {err} — SUSPECTED 10x unit error "
                f"(亿元 vs billion, prompt Rule 1 ambiguity; value/10={value / 10.0})"
            )
            cleaned[field_name] = None
        else:
            warnings.append(f"  {field_name}: {err}")
            cleaned[field_name] = None
    cleaned["_unit_suspect_fields"] = unit_suspects
    return cleaned, warnings


# ---------------------------------------------------------------------------
# Bank-year panel 构建
# ---------------------------------------------------------------------------
def records_to_panel(records: list[dict], bank_id_lookup: dict[str, str] | None = None) -> pd.DataFrame:
    """把抽取记录转换为 bank-year DataFrame.

    Parameters
    ----------
    records : list of dict
        每个 dict 须含 'response_parsed' (已校验字段) + 'pdf_path' (用于推断 bank_id)
    bank_id_lookup : optional
        ``{bank_name -> target_bank}`` 映射。``target_bank`` 是主管线面板
        ([40_panel_yearly.parquet]) 使用的规范标识符; None 时按 ``bank_name``
        原样回退。

    Returns
    -------
    含以下列的 DataFrame:
        bank_id, bank_name, year, total_assets, npl, car, profit, retail_dep, info_tech, source_pdf

    Note
    ----
    返回列 ``bank_id`` 即 lookup 结果 — 与主面板 merge 时请重命名为
    ``target_bank`` 以对齐 pipeline 约定。
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
            # fix(omni-gapfill-12, 2026-06-12): 10× 单位疑似旁路列 (';' 连接,
            # '' = 无嫌疑), 供下游审计/三角对照过滤。
            "unit_suspect_fields": ";".join(cleaned.get("_unit_suspect_fields", [])),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # 去重 (每个 bank-year 保留 source_pdf 排序最后的一条)
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
    """新增布尔列 ``outlier_<col>``, 标记偏离中位数超过 sd_threshold 个稳健 SD 的值.

    用 MAD (中位数绝对偏差) × 1.4826 作为稳健 SD 估计量 (Rousseeuw & Croux 1993)。
    与样本 SD 不同, MAD 不会被它要检测的离群值本身推大。

    白话: 如果用普通标准差找离群值, 离群值自己会把标准差撑大、反而藏住自己;
    MAD 用"到中位数的距离的中位数", 对极端值不敏感, 找得更准。
    """
    df = df.copy()
    for col in numeric_cols:
        if col not in df.columns:
            continue
        med = df[col].median()
        deviations = (df[col] - med).abs()
        mad = deviations.median()
        robust_sd = 1.4826 * mad  # 高斯分布假设下 MAD→SD 的换算系数
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
    unit_quotient: float = 10.0,
    unit_quotient_tol_pct: float = 10.0,
) -> pd.DataFrame:
    """Compare NCD-extracted fields with annual-report fields, flagging discrepancies.

    Returns
    -------
    DataFrame with columns ``inconsistent_<field>`` (bool) for each compared field,
    plus ``unit_mismatch_<field>`` (bool) — fix(omni-gapfill-12, 2026-06-12):
    NCD/年报 取整商 ≈ ``unit_quotient`` (默认 10, ±``unit_quotient_tol_pct``%)
    时标记为 亿元/billion 单位错误 (prompt Rule 1 ambiguity), 与普通数值不一致
    区分 — 单位错可机械 ÷10 修复, 普通不一致须人工裁决。
    """
    merged = ncd_panel.merge(
        annual_report_panel,
        on=list(join_keys),
        how="inner",
        suffixes=("_ncd", "_ar"),
    )
    q_lo = unit_quotient * (1 - unit_quotient_tol_pct / 100.0)
    q_hi = unit_quotient * (1 + unit_quotient_tol_pct / 100.0)
    for f in fields_to_compare:
        ncd_col = f"{f}_ncd"
        ar_col = f"{f}_ar"
        if ncd_col not in merged.columns or ar_col not in merged.columns:
            continue
        ar_nonzero = merged[ar_col].replace(0, np.nan).abs()
        diff_pct = (merged[ncd_col] - merged[ar_col]).abs() / ar_nonzero * 100
        merged[f"inconsistent_{f}"] = diff_pct > tolerance_pct
        quotient = merged[ncd_col].abs() / ar_nonzero
        merged[f"unit_mismatch_{f}"] = quotient.between(q_lo, q_hi).fillna(False)
    return merged


def main(argv: list[str] | None = None) -> int:
    """CLI 入口: 把 NCD 抽取记录 JSON 转换为 bank-year panel parquet。

    执行 schema 校验、离群值标记, 以及可选的 R11 与年报数据三角互证。
    成功返回 0, 输入 JSON 不存在返回 1。
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
