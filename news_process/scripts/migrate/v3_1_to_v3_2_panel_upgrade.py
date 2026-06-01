"""v3.2.0 panel BREAKING rename migration utility (plan v14 §3.6).

把 v3.1.1 panel parquet 升级到 v3.2.0 列名约定:
  innovation_locus → innovation_locus_full + innovation_locus_ctx (后者填 NaN)
  innovation_substantiveness → _full + _ctx
  category_confidence → _full + _ctx

注意:
- 仅 stage 21 输出 (21_tone_llms.parquet) 含 stage 3 字段, 此 utility 针对该层
- 旧 panel 没有 _ctx 标签 (因为 v3.1.x 已丢弃), 升级后 _ctx 列填 NaN
- 用户需重跑 v3.2.0 stage 21 才能产实际 _ctx 标签
- 同时新增 dual gate 三互斥指示列 (基于现有 llm_verified_full/ctx 派生)

CLI:
  python -m news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade <old.parquet> <new.parquet>
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pandas as pd

_PROJECT_PARENT = Path(__file__).resolve().parents[3]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


# v3.1.1 → v3.2.0 列名映射 (本字典即权威单源; 原 docs/ CSV 已随 docs/ 目录整体删除, commit 1698bda5)
COLUMN_RENAME_MAP = {
    # bare → _full (BREAKING; ctx 列另起新加)
    'innovation_locus': 'innovation_locus_full',
    'innovation_substantiveness': 'innovation_substantiveness_full',
    'category_confidence': 'category_confidence_full',
}

# 升级后须新加的列 (填 NaN, 用户需重跑 stage 21 LLM 才有实际值)
NEW_NAN_COLUMNS = [
    'innovation_locus_ctx',
    'innovation_substantiveness_ctx',
    'category_confidence_ctx',
]


def upgrade_panel(old_parquet: str, new_parquet: str, verbose: bool = False) -> dict:
    """把 v3.1.1 panel parquet 升级到 v3.2.0 schema.

    Args:
        old_parquet: 输入 v3.1.1 parquet 路径
        new_parquet: 输出 v3.2.0 parquet 路径
        verbose: 详细日志

    Returns:
        dict: {n_renamed, n_added, n_dual_gate_derived, n_rows, n_cols_before, n_cols_after}
    """
    if not os.path.exists(old_parquet):
        raise FileNotFoundError(f"Input parquet 不存在: {old_parquet}")

    df = pd.read_parquet(old_parquet)
    n_rows = len(df)
    n_cols_before = len(df.columns)
    if verbose:
        print(f"  Loaded: {n_rows} rows × {n_cols_before} cols from {old_parquet}")

    # 1. RENAME bare → _full
    rename_dict = {old: new for old, new in COLUMN_RENAME_MAP.items() if old in df.columns}
    df = df.rename(columns=rename_dict)
    if verbose:
        for o, n in rename_dict.items():
            print(f"  RENAMED: {o} → {n}")

    # 2. ADD _ctx 列 (NaN; 用户需重跑 stage 21 产实际值)
    n_added = 0
    for col in NEW_NAN_COLUMNS:
        if col not in df.columns:
            df[col] = None
            n_added += 1
            if verbose:
                print(f"  ADDED (NaN): {col}")

    # 3. DERIVE dual gate 三互斥指示列 (基于现有 verified_full/ctx)
    n_dual = 0
    if 'llm_verified_full' in df.columns and 'llm_verified_ctx' in df.columns:
        _vf = df['llm_verified_full'].astype(bool)
        _vc = df['llm_verified_ctx'].astype(bool)
        for col, mask in [
            ('llm_verified_dual_full_only', _vf & ~_vc),
            ('llm_verified_dual_ctx_only',  ~_vf & _vc),
            ('llm_verified_dual_both',       _vf & _vc),
        ]:
            if col not in df.columns:
                df[col] = mask.values
                n_dual += 1
                if verbose:
                    print(f"  DERIVED: {col}")

    n_cols_after = len(df.columns)
    df.to_parquet(new_parquet, index=False)
    if verbose:
        print(f"  Saved: {n_rows} rows × {n_cols_after} cols to {new_parquet}")

    return {
        'n_renamed': len(rename_dict),
        'n_added_nan': n_added,
        'n_dual_gate_derived': n_dual,
        'n_rows': n_rows,
        'n_cols_before': n_cols_before,
        'n_cols_after': n_cols_after,
    }


def main(argv=None):
    """CLI entry — argparse + upgrade_panel + stdout 报告 (plan v14 §3.6 utility).

    Args:
        argv: 可选 argv list (默认 sys.argv[1:]); 测试可注入 mock args.
    Returns:
        exit code (0 OK / 1 FileNotFoundError)
    """
    parser = argparse.ArgumentParser(
        prog='python -m news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade',
        description='v3.1.1 → v3.2.0 panel parquet BREAKING rename migration',
    )
    parser.add_argument('old_parquet', help='Input v3.1.1 panel parquet')
    parser.add_argument('new_parquet', help='Output v3.2.0 panel parquet')
    parser.add_argument('--verbose', action='store_true', help='Show per-column rename log')
    args = parser.parse_args(argv)

    try:
        stats = upgrade_panel(args.old_parquet, args.new_parquet, verbose=args.verbose)
    except FileNotFoundError as e:
        sys.stderr.write(f"[ERROR] {e}\n")
        return 1

    print("v3.2.0 panel upgrade complete:")
    print(f"  Renamed {stats['n_renamed']} bare → _full columns")
    print(f"  Added {stats['n_added_nan']} _ctx columns (NaN; rerun stage 21 for real values)")
    print(f"  Derived {stats['n_dual_gate_derived']} dual gate indicator columns")
    print(f"  Shape: {stats['n_rows']} rows × ({stats['n_cols_before']} → {stats['n_cols_after']} cols)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
