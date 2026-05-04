"""
generate_golden_snapshot.py — Phase 0 交付物

对 ``data/processed/`` (Phase 8 目录重命名) 下**当前磁盘上已存在**的全部
parquet 产物逐列计算值哈希, 并写入 ``tests/fixtures/golden_panel_v0.json``。

本脚本走**降级路径** Phase 0 快照 (见重整方案): **不**重跑主流水线,
仅对现存文件做哈希。若某预期阶段输出缺失, JSON 标记 ``"incomplete": true``;
Phase 2 的 ``test_panel_reproducibility.py`` 将仅对有基线的阶段列做比对。

哈希语义:
- 单列: ``hex(int(pd.util.hash_pandas_object(df[col], index=False).sum()))``
  的无符号 64 位十六进制表示 (见 ``column_hash``)。
- 同时记录行数、列数与 dtype 字典, 便于廉价结构 diff。
- **不**记录 parquet 文件字节级哈希 (pyarrow 元数据、Snappy 块边界、
  时间戳等在重复写出间不稳定)。

用法:
    python news_process/scripts/migrate/generate_golden_snapshot.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


# 与 run_pipeline_function 管线阶段输出文件名对齐 (方案 §1)。
# 磁盘上可能仅存在子集; 缺失项使 ``incomplete`` 为 true。
EXPECTED_STAGES = [
    "00_preprocessing.parquet",
    "11_bank_news.parquet",
    "12_fintech_news.parquet",
    "12_fintech_news_full.parquet",
    "14_fintech_intensity.parquet",
    "15_article_alignment.parquet",
    "21_tone_llms.parquet",
    "21_tone_llms_full.parquet",
    "22_words_tone.parquet",
    "23_bert_tone.parquet",
    "24_herd_decay.parquet",
    "40_panel_yearly.parquet",
    "40_article_bank_level.parquet",
    "40_attn_index_year.parquet",
    "40_attn_index_province_year.parquet",
    "40_attn_index_city_year.parquet",
    "41_panel_with_controls.parquet",
    "51_panel_with_controls.parquet",
]


def column_hash(s: pd.Series) -> str:
    """单列取值经 pandas 哈希后的十六进制摘要 (忽略行索引)。"""
    h = int(pd.util.hash_pandas_object(s, index=False).sum())
    h_unsigned = h & ((1 << 64) - 1)
    return f"{h_unsigned:016x}"


def hash_parquet(path: Path) -> dict:
    """对单个 parquet 文件按列计算哈希及结构元数据。"""
    df = pd.read_parquet(path)
    return {
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "columns_order": list(df.columns),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "column_hashes": {c: column_hash(df[c]) for c in df.columns},
    }


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    # Phase 8 (2026-05-04): data_processed → data/processed
    data_dir = project_root / "data" / "processed"
    fixture_path = project_root / "tests" / "fixtures" / "golden_panel_v0.json"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)

    if not data_dir.is_dir():
        print(f"错误: 未找到 data/processed/ 目录: {data_dir}", file=sys.stderr)
        return 2

    snapshot: dict = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_tag": "baseline-pre-restructure",
        "data_dir": str(data_dir.relative_to(project_root)),
        "hash_method": "pd.util.hash_pandas_object(s, index=False).sum() -> u64 hex",
        "stages": {},
    }

    present = []
    missing = []
    for filename in EXPECTED_STAGES:
        path = data_dir / filename
        if not path.is_file():
            missing.append(filename)
            continue
        try:
            snapshot["stages"][filename] = hash_parquet(path)
            present.append(filename)
        except Exception as exc:  # noqa: BLE001 — 诊断性捕获
            snapshot["stages"][filename] = {
                "file": filename,
                "error": f"{type(exc).__name__}: {exc}",
            }
            missing.append(filename)

    snapshot["incomplete"] = len(missing) > 0
    snapshot["counts"] = {
        "expected": len(EXPECTED_STAGES),
        "present": len(present),
        "missing": len(missing),
    }
    snapshot["missing_stages"] = missing

    with fixture_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"已写入 {fixture_path.relative_to(project_root)}")
    print(f"  已存在: {len(present)} / {len(EXPECTED_STAGES)}")
    if missing:
        print(f"  缺失: {missing}")
        print("  incomplete = true (Phase 2 可复现性测试将跳过缺失阶段)")
    else:
        print("  incomplete = false (全覆盖)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
