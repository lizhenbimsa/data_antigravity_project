"""benefit_society cohort manifest 导出 (DP-8 / F-R6 lineage).

生成 ``data/raw/cohort/benefit_society_84banks.csv`` — benefit_society
历史 (full/ctx) 锁定的 84 银行 cohort 名单 (manifest)。该名册 **track-agnostic**
(仅 target_bank + bank_type, 无任何情感轨列) → 三轨 (full/ctx/ss) 共用同一份
cohort, 无需按轨拆分。沿用历史命名仅为 lineage 兼容。
# legacy (full/ctx) 示例 — 本文件 prose 豁免标记 (cohort 名册不分轨, 三轨共用)

PAP v1.0-final §3 把全部分析锚定到此 manifest; 下游对 `target_bank` 的
过滤必须对照它做校验。``is_listed`` 代理以 bank_type ∈ {soe, joint} 视为
上市 (中国五大行 + 主要股份制银行均在 HKEX / SSE / SZSE 上市)。

白话: 这份 CSV 就是"研究对象点名册"——把哪 84 家银行进样本一次性
冻结下来, 之后所有表/图只认这份名单, 防止样本悄悄变动。

CLI: ``python -m news_process.papers.benefit_society.cohort [--dry-run]``
"""
from __future__ import annotations

import argparse
import hashlib
import logging
import sys
from pathlib import Path

import pandas as pd

_LOGGER = logging.getLogger("papers.benefit_society.cohort")

LISTED_TYPES = frozenset({"soe", "joint"})
COHORT_LINEAGE = "benefit_society_v1.0-final_2026-05-16"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def export_cohort_manifest(
    panel_path: Path | None = None,
    output_path: Path | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, object]:
    """从 bank-year panel 构建 84 银行 cohort manifest.

    返回含元数据的 dict (sha256 / n_banks / output_path)。
    """
    root = _repo_root()
    panel_path = panel_path or root / "news_process" / "data" / "processed" / "40_panel_yearly.parquet"
    output_path = output_path or root / "news_process" / "data" / "raw" / "cohort" / "benefit_society_84banks.csv"

    df = pd.read_parquet(panel_path, columns=["target_bank", "bank_type"])

    cohort = (
        df.drop_duplicates(subset=["target_bank"])
        .sort_values("target_bank")
        .reset_index(drop=True)
    )
    cohort["is_listed_proxy"] = cohort["bank_type"].isin(LISTED_TYPES).astype("int8")
    cohort["cohort_lineage"] = COHORT_LINEAGE

    manifest_str = ";".join(cohort["target_bank"].tolist())
    sha = hashlib.sha256(manifest_str.encode("utf-8")).hexdigest()[:16]

    if not dry_run:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cohort.to_csv(output_path, index=False, encoding="utf-8-sig")

    return {
        "n_banks": len(cohort),
        "manifest_sha256_prefix": sha,
        "output_path": str(output_path),
        "n_listed_proxy": int(cohort["is_listed_proxy"].sum()),
        "bank_type_counts": cohort["bank_type"].value_counts().to_dict(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.cohort",
        description="Export benefit_society 84-bank cohort manifest (PAP v1.0-final DP-8)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Compute manifest without writing CSV")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
    )

    result = export_cohort_manifest(dry_run=args.dry_run)
    _LOGGER.info("n_banks: %d", result["n_banks"])
    _LOGGER.info("manifest_sha256_prefix: %s", result["manifest_sha256_prefix"])
    _LOGGER.info("is_listed (proxy): %d listed / %d total", result["n_listed_proxy"], result["n_banks"])
    _LOGGER.info("bank_type counts: %s", result["bank_type_counts"])
    _LOGGER.info("output: %s%s", result["output_path"], " (dry-run, not written)" if args.dry_run else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
