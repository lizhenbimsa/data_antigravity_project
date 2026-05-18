"""scripts/data_acquisition/outcome_schema_validator.py
─────────────────────────────────────────────────────────────────────────────
Outcome panel schema 校验脚本 — 自动检查 dry-run 输出是否满足
第 10/11 篇 paper_spec.yaml::outcome 字段定义.

Usage
-----
    python scripts/data_acquisition/outcome_schema_validator.py \\
        --input data/dry_run/2024Q1_outcome.parquet \\
        --report data/dry_run/2024Q1_validation_report.json

输出
----
JSON report:
{
  "schema_compliance": true / false,
  "missing_columns": [...],
  "type_mismatches": {...},
  "value_range_violations": {...},
  "per_outcome_stats": {...},
  "passes_z_score_feasibility": true / false   # 关键 fallback 决策依据
}
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# 与 banking_outcome_dry_run.py::OUTCOME_SCHEMA 一致
REQUIRED_COLUMNS = {
    'target_bank', 'year', 'quarter',
    'roa', 'capital_adequacy_ratio', 'total_assets', 'rwa',
    'npl_balance', 'npl_ratio', 'total_loans',
    'loan_writeoffs', 'loan_loss_provision',
    'data_source', 'acquisition_timestamp',
}

# Value range 健全性 (业务常识)
VALUE_RANGES = {
    'roa': (-10.0, 10.0),                     # ROA: 极端 +/-10% (理论上限)
    'capital_adequacy_ratio': (0.0, 50.0),    # CAR: 0-50% (8% 最低监管要求)
    'npl_ratio': (0.0, 50.0),                 # NPL: 0-50% (包商 50%+ 是异常案例)
    'total_assets': (0.0, 1e8),               # 总资产: 0 - 100 万亿元 (工行约 50 万亿)
    'rwa': (0.0, 1e8),
    'total_loans': (0.0, 1e8),
    'npl_balance': (0.0, 1e6),
}

# Z-score 计算必需字段 (任一缺失则 Z-score 不可算)
Z_SCORE_REQUIRED = {'roa', 'capital_adequacy_ratio'}

# NPL formation rate 必需字段
NPL_FORMATION_REQUIRED = {'npl_balance', 'total_loans'}  # loan_writeoffs 可选

# RWA ratio 必需字段
RWA_RATIO_REQUIRED = {'rwa', 'total_assets'}


def validate(df: pd.DataFrame) -> dict:
    """校验单个 dry-run output dataframe."""
    report = {
        'n_rows': len(df),
        'schema_compliance': True,
        'missing_columns': [],
        'type_mismatches': {},
        'value_range_violations': {},
        'per_outcome_stats': {},
        'feasibility': {},
    }

    # 1. 必填列存在性
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        report['schema_compliance'] = False
        report['missing_columns'] = missing

    # 2. Value range 校验
    for col, (lo, hi) in VALUE_RANGES.items():
        if col not in df.columns:
            continue
        s = df[col].dropna()
        if len(s) == 0:
            continue
        violations = ((s < lo) | (s > hi)).sum()
        if violations > 0:
            report['value_range_violations'][col] = {
                'n_violations': int(violations),
                'expected_range': [lo, hi],
                'observed_min': float(s.min()),
                'observed_max': float(s.max()),
            }

    # 3. Per-outcome 统计 (可得率 + 描述统计)
    outcome_cols = ['roa', 'capital_adequacy_ratio', 'rwa', 'total_assets',
                    'npl_balance', 'npl_ratio', 'total_loans',
                    'loan_writeoffs', 'loan_loss_provision']
    for col in outcome_cols:
        if col not in df.columns:
            continue
        s = df[col]
        report['per_outcome_stats'][col] = {
            'availability_rate': float(s.notna().mean()),
            'n_obs': int(s.notna().sum()),
            'mean': float(s.mean()) if s.notna().any() else None,
            'std': float(s.std()) if s.notna().sum() > 1 else None,
            'p25': float(s.quantile(0.25)) if s.notna().any() else None,
            'p50': float(s.quantile(0.50)) if s.notna().any() else None,
            'p75': float(s.quantile(0.75)) if s.notna().any() else None,
        }

    # 4. Feasibility 决策 (per outcome 都需要的字段全可得才算 feasible)
    def _check_outcome_feasibility(required_cols: set) -> dict:
        avail_per_col = {
            col: df[col].notna().mean() if col in df.columns else 0.0
            for col in required_cols
        }
        # 所有 required 字段在 same row 全可得才算 ok
        if all(c in df.columns for c in required_cols):
            joint = df[list(required_cols)].notna().all(axis=1).mean()
        else:
            joint = 0.0
        return {
            'per_col_availability': {k: float(v) for k, v in avail_per_col.items()},
            'joint_availability': float(joint),
        }

    report['feasibility']['z_score'] = _check_outcome_feasibility(Z_SCORE_REQUIRED)
    report['feasibility']['npl_formation_rate'] = _check_outcome_feasibility(NPL_FORMATION_REQUIRED)
    report['feasibility']['rwa_ratio'] = _check_outcome_feasibility(RWA_RATIO_REQUIRED)

    # Z-score 单独标记: 主 outcome, 决定 path α/β/γ
    z_avail = report['feasibility']['z_score']['joint_availability']
    report['passes_z_score_feasibility'] = z_avail >= 0.40

    return report


def main():
    parser = argparse.ArgumentParser(description='Validate outcome panel schema')
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--report', default='data/dry_run/validation_report.json',
                        type=Path)
    args = parser.parse_args()

    df = pd.read_parquet(args.input)
    report = validate(df)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    with args.report.open('w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)

    print("\n" + "=" * 60)
    print(f"SCHEMA VALIDATION REPORT: {args.input}")
    print("=" * 60)
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))


if __name__ == '__main__':
    main()
