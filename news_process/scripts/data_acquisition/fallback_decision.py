"""scripts/data_acquisition/fallback_decision.py
─────────────────────────────────────────────────────────────────────────────
基于 dry-run validation report 自动决策 fallback path α/β/γ.

V4 audit F-D.1 修复: 数据 dry-run 失败时三档预定义路径.

Path 定义 (与 paper_spec.yaml::fallback_paths 一致):
    α: dry-run ≥ 70%       → 全 outcome 设计 (Z-score + NPL + RWA + LLP)
    β: 40-70%              → drop RWA + LLP, 保留 Z-score + NPL
    γ: < 40%               → 退回 ROA + NPL ratio 简单 measure, 撤回 risk-taking

Usage
-----
    python scripts/data_acquisition/fallback_decision.py \\
        --validation-report data/dry_run/2024Q1_validation_report.json \\
        --decision-output data/dry_run/2024Q1_path_decision.json
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Path 阈值 (与 paper_spec.yaml 一致)
THRESHOLD_ALPHA = 0.70   # ≥ 70% → path α
THRESHOLD_BETA = 0.40    # 40-70% → path β; < 40% → path γ


def decide(report: dict) -> dict:
    """基于 validation report 决定 fallback path.

    决策依据 (per outcome joint availability):
        - z_score: 必须可算 (primary outcome)
        - npl_formation_rate: 必须可算 (secondary)
        - rwa_ratio: 决定 path α (含) 或 β (不含)
        - loan_loss_provision: bonus, 影响 第 11 篇 Bushman-Williams 2012 direct match

    Returns:
        dict:
            path: 'alpha' | 'beta' | 'gamma'
            rationale: 决策理由 (string)
            required_actions: 用户后续 action items
            paper_spec_updates: 需要修改的 spec 字段
    """
    feas = report.get('feasibility', {})
    z_avail = feas.get('z_score', {}).get('joint_availability', 0.0)
    npl_avail = feas.get('npl_formation_rate', {}).get('joint_availability', 0.0)
    rwa_avail = feas.get('rwa_ratio', {}).get('joint_availability', 0.0)

    # γ: Z-score 都不可算
    if z_avail < THRESHOLD_BETA:
        return {
            'path': 'gamma',
            'rationale': (
                f'Z-score joint availability {z_avail:.1%} < {THRESHOLD_BETA:.0%}: '
                'roa 或 CAR 大面积缺失, 主 outcome 不可算. '
                '撤回 risk-taking 框架, 退回 ROA + NPL ratio 简单 measure.'
            ),
            'required_actions': [
                '1. 与用户确认是否接受降级设计 (与现有 P1 bank_fintech_tone outcome 重叠)',
                '2. 若接受: 重写两份 paper_spec.yaml::outcome 字段为 [roa, npl_ratio]',
                '3. 若不接受: 转向 #18 policy alignment / #19 media breadth 候选 paper',
                '4. 重新走 V4 audit 评估新方案的顶刊潜力',
            ],
            'paper_spec_updates': {
                'outcome.primary': 'roa',
                'outcome.secondary': ['npl_ratio'],
                'theory.primary_anchors': '需重写 (退出 risk-taking literature)',
                'targets.primary_outlet': '可能从 RFS/JAE 下调到 JCF/JBF',
            },
            'kpi_impact': '严重 — 48 月接收预期从 1.5-2.2 篇下调至 0.5-1.0 篇',
        }

    # β: Z-score 可算, 但 RWA 缺
    if rwa_avail < THRESHOLD_ALPHA:
        return {
            'path': 'beta',
            'rationale': (
                f'Z-score joint availability {z_avail:.1%} ≥ {THRESHOLD_BETA:.0%}: '
                f'主 outcome 可行. RWA joint availability {rwa_avail:.1%} < {THRESHOLD_ALPHA:.0%}: '
                'RWA ratio 缺失较多, 移出 secondary, 保留 Z-score + NPL formation.'
            ),
            'required_actions': [
                '1. 修改两份 paper_spec.yaml::outcome.secondary 移除 rwa_to_ta_ratio',
                '2. 在第 11 篇 outcome.secondary 移除 loan_loss_provision_discretion (若 LLP 可得率也 < 70%)',
                '3. 进入 M2 outcome panel 构建 (基于 Z-score + NPL formation)',
                '4. M5 baseline 时增加 *partial-sample RWA robustness* (仅在 RWA 可得子样本验证)',
            ],
            'paper_spec_updates': {
                'outcome.secondary': ['npl_formation_rate', 'sigma_roa_5y_rolling'],
                'robustness_battery': '增加 rwa_partial_sample_robustness',
            },
            'kpi_impact': '轻微 — 接收预期维持 1.2-1.8 篇 / 48 月',
        }

    # α: 全可行
    return {
        'path': 'alpha',
        'rationale': (
            f'Z-score availability {z_avail:.1%} ≥ {THRESHOLD_ALPHA:.0%}, '
            f'RWA availability {rwa_avail:.1%} ≥ {THRESHOLD_ALPHA:.0%}. '
            '全 outcome 设计可行, 按 paper_spec 原方案推进.'
        ),
        'required_actions': [
            '1. 进入 M2 outcome panel 构建 (Z-score + NPL formation + RWA ratio + LLP discretion)',
            '2. 启动 cross_outlet diagnostic (第 10 篇 R3 critical 修复)',
            '3. M3-M4 IV 设计 + first-stage 测试',
        ],
        'paper_spec_updates': {},  # 无需修改
        'kpi_impact': '维持原计划 — 48 月接收预期 1.5-2.2 篇',
    }


def main():
    parser = argparse.ArgumentParser(description='Fallback path decision')
    parser.add_argument('--validation-report', required=True, type=Path)
    parser.add_argument('--decision-output',
                        default='data/dry_run/path_decision.json', type=Path)
    args = parser.parse_args()

    with args.validation_report.open('r', encoding='utf-8') as f:
        report = json.load(f)

    decision = decide(report)
    args.decision_output.parent.mkdir(parents=True, exist_ok=True)
    with args.decision_output.open('w', encoding='utf-8') as f:
        json.dump(decision, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"FALLBACK PATH DECISION: {decision['path'].upper()}")
    print("=" * 60)
    print(json.dumps(decision, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
