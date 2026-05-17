"""v3.4.0 panel BREAKING migration utility (plan v3.4.0 Phase 1 Step C).

把 v3.3.0 panel parquet 升级到 v3.4.0 列契约约定:
  + innovation_collab_mode_full (Chesbrough 2003 + L&S 2006 SMJ; 第三维度对称扩张)
  + innovation_collab_mode_ctx
  + innovation_collab_mode_confidence_full
  + innovation_collab_mode_confidence_ctx

设计原则 (per master plan §3.4 panel 迁移路径):
- 列名向后兼容: v3.3.0 全部 2024 列名保留 (即便为 NaN)
- 新增列以 LLM 输出 schema 命名 (与 v3.2.0 innovation_locus_full / innovation_substantiveness_full
  对称, 不引入 _v34_* 前缀; 与 v3.2.0 BREAKING 命名规范一致)
- 4 个新列以 None 占位; 用户须重跑 stage 21 (prompt v8) 才能填实际值
- idempotent: 若新列已存在 → 直通; 若不存在 → 补 None 列
- 不破坏现有列, 不改变现有行数 (v3.3.0 panel 168 obs 不变, 仅列扩 +4)

Plan v3.4.0 §C1 hard deliverable; Pre-registration β supplementation (Q-E 锁定):
v8 = v7 严格超集, prompt-v7-released git tag 不删, 新 git tag
prompt-v8-supplementation-released 锚定 v3.4.0 baseline.

CLI:
  python -m news_process.scripts.migrate.v3_3_to_v3_4_panel_upgrade <old.parquet> <new.parquet>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

_PROJECT_PARENT = Path(__file__).resolve().parents[3]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


# v3.3.0 → v3.4.0 新增列 (填 None / 0.0, 用户需重跑 stage 21 prompt v8 才有实际值)
# 与 config/schemas.yaml::stage_21_output.required_columns 一致
NEW_LABEL_COLUMNS = [
    'innovation_collab_mode_full',     # str: 自主研发 / 外部协同 / None
    'innovation_collab_mode_ctx',
]
NEW_CONFIDENCE_COLUMNS = [
    'innovation_collab_mode_confidence_full',   # float [0, 1]
    'innovation_collab_mode_confidence_ctx',
]


def upgrade_panel_v3_3_to_v3_4(df: pd.DataFrame) -> pd.DataFrame:
    """把 v3.3.0 panel DataFrame 升级到 v3.4.0 列契约.

    Args:
        df: v3.3.0 panel DataFrame (含 v3.2.0 BREAKING 后的 innovation_locus_full/_ctx
            与 innovation_substantiveness_full/_ctx 列).

    Returns:
        pd.DataFrame: 升级后的 v3.4.0 panel, 新增 4 个 collab_mode 列 (None / 0.0 占位).

    Idempotent: 若新列已存在则保留原值; 若不存在则补 None / 0.0.
    """
    df = df.copy()
    # 新增 label 列 (None 占位)
    for col in NEW_LABEL_COLUMNS:
        if col not in df.columns:
            df[col] = None
    # 新增 confidence 列 (0.0 占位)
    for col in NEW_CONFIDENCE_COLUMNS:
        if col not in df.columns:
            df[col] = 0.0
    return df


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description='Upgrade v3.3.0 panel parquet to v3.4.0 schema (添加 innovation_collab_mode 4 列)'
    )
    parser.add_argument('input', type=Path, help='v3.3.0 输入 parquet 路径')
    parser.add_argument('output', type=Path, help='v3.4.0 输出 parquet 路径')
    args = parser.parse_args(argv)

    if not args.input.exists():
        print(f'❌ 输入文件不存在: {args.input}', file=sys.stderr)
        return 1

    print(f'读取 v3.3.0 panel: {args.input}')
    df = pd.read_parquet(args.input)
    print(f'  原 panel 形状: {df.shape}')

    df_v34 = upgrade_panel_v3_3_to_v3_4(df)
    n_new = df_v34.shape[1] - df.shape[1]
    print(f'  v3.4.0 panel 形状: {df_v34.shape} (+{n_new} 新增列)')

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df_v34.to_parquet(args.output, index=False)
    print(f'✅ 写入 v3.4.0 panel: {args.output}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
