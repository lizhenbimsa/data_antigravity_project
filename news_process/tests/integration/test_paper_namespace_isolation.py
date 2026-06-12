"""M0 G0 acceptance — 跨 paper 列名冲突扫描 (现为 11 篇, 2026-06-01 起)。

Plan v2.x §5.2.2 M0.3 + §5.2.4 G0 (历史计划原文, 当时为 8 篇):
    "8 paper 列名冲突: 0 冲突 (跨 8 paper)"

红线不变式
----------
1. 各 paper 的 ``treatment.primary`` 必须互不重复 (paper-specific signal column).
2. 各 paper 的 ``mediator.primary`` (P2/P4 有 mediator) 互不重复.
3. 各 paper 的 paper-specific derived outcome 名 (如 car_3day_window_tone_shock,
   long_run_roa_change_3yr, car_5day_window) 互不重复.
4. ``controls.fixed_effects`` 跨 paper 允许复用 (bank_fe / year_fe 是共享 FE),
   不视为冲突。
5. ``controls.bank_level`` / ``controls.year_level`` 的银行/年度标准控制变量
   (ln_assets / leverage / capital_ratio / npl_ratio / deposit_growth /
   gdp_growth / m2_growth) 跨 paper 共享, 不视为冲突。
"""

from __future__ import annotations

from collections import defaultdict

import pytest

from news_process.papers._common.paper_registry import (
    load_all_specs,
)

# 共享工具列 (controls / FE) — 允许跨 paper 重叠。
SHARED_CONTROLS: frozenset[str] = frozenset({
    # 银行层面标准控制变量
    'ln_assets', 'leverage', 'capital_ratio', 'npl_ratio', 'deposit_growth',
    # 年度层面宏观控制变量
    'gdp_growth', 'm2_growth',
    # 固定效应
    'bank_fe', 'year_fe',
    # ROA / market-cap 作为 outcome.secondary 跨 paper 共享 (P1+benefit+broker+llm+strategic)
    'roa', 'loan_growth', 'ln_market_cap',
    # CAR 3 日通用版 — 部分 spec 可能把它放在 secondary 下
    'car_3day',
    'tobin_q',
    'strat_fluidity',  # strategic_diff 的 secondary
    # z_score = Laeven-Levine (2009 JFE) bank-stability outcome, 由第10篇
    # (bank_media_disagreement) 与第11篇 (bank_news_clarity) *刻意共享* 作 outcome.primary
    # (两篇 spec 均注明 "与第 10/11 篇共享, Laeven-Levine 2009 标准"; provisional 2026-06-01)。
    'z_score',
    'sigma_roa_5y_rolling',  # z_score 分母, 同属共享 risk-taking 量
})


def _flatten(value: object) -> list[str]:
    """treatment.alternative / outcome.secondary 字段可能是 list / str / scalar.

    统一展平为 str 列表 (剥掉 list wrapper). 非字符串 entry 过滤掉
    (这些是 list of derivation hints, 不是真实列名)."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if isinstance(v, str)]
    if isinstance(value, str):
        return [value]
    return []


def _collect_paper_specific_signals(specs: dict) -> dict[str, list[tuple[str, str]]]:
    """收集每个 paper 的 paper-specific 信号列 (treatment.primary / mediator.primary /
    derived outcome) → mapping ``column_name -> list[(paper_id, field_origin)]``.
    """
    bucket: dict[str, list[tuple[str, str]]] = defaultdict(list)

    for paper_id, spec in specs.items():
        treatment = spec.raw.get('treatment', {}) or {}
        outcome = spec.raw.get('outcome', {}) or {}
        mediator = spec.raw.get('mediator', {}) or {}

        # P4 的 treatment 用 primary_pair (list) 而非 primary
        for col in _flatten(treatment.get('primary')):
            bucket[col].append((paper_id, 'treatment.primary'))
        for col in _flatten(treatment.get('primary_pair')):
            bucket[col].append((paper_id, 'treatment.primary_pair'))

        # mediator.primary (仅 P2/P4 存在)
        for col in _flatten(mediator.get('primary')):
            bucket[col].append((paper_id, 'mediator.primary'))

        # outcome.primary — 只有 paper-specific 的派生名才计入
        for col in _flatten(outcome.get('primary')):
            if col not in SHARED_CONTROLS:
                bucket[col].append((paper_id, 'outcome.primary'))

    return bucket


def test_treatment_primary_columns_are_unique() -> None:
    specs = load_all_specs()

    primaries: dict[str, str] = {}  # 列名 -> paper_id
    for paper_id, spec in specs.items():
        t = spec.raw.get('treatment', {}) or {}
        # primary 可能是 str, 或 primary_pair 是 list (P4)
        names: list[str] = []
        names.extend(_flatten(t.get('primary')))
        names.extend(_flatten(t.get('primary_pair')))
        for col in names:
            if col in primaries:
                pytest.fail(
                    f"treatment.primary collision: column {col!r} "
                    f"declared by both {primaries[col]!r} and {paper_id!r}"
                )
            primaries[col] = paper_id


def test_mediator_primary_columns_are_unique_across_papers_with_mediator() -> None:
    specs = load_all_specs()

    mediators: dict[str, str] = {}
    for paper_id, spec in specs.items():
        m = spec.raw.get('mediator') or {}
        for col in _flatten(m.get('primary')):
            if col in mediators:
                pytest.fail(
                    f"mediator.primary collision: column {col!r} "
                    f"declared by both {mediators[col]!r} and {paper_id!r}"
                )
            mediators[col] = paper_id


def test_paper_specific_derived_outcome_names_unique() -> None:
    """Plan §B.X 刻意让 car_3day_window 命名在 P1 (tone_shock) /
    P3 (fintech_announcement) / P4 (5day) 间分化, 以避免 salami slicing 冲突 (R10-M01)。
    """
    specs = load_all_specs()
    paper_derived_outcomes: dict[str, str] = {}
    for paper_id, spec in specs.items():
        primary = spec.raw.get('outcome', {}).get('primary', '')
        if primary in SHARED_CONTROLS:
            continue  # 共享 outcome (如 roa); 已由 SHARED_CONTROLS 豁免覆盖
        if not primary:
            continue
        if primary in paper_derived_outcomes:
            pytest.fail(
                f"outcome.primary collision: {primary!r} declared by both "
                f"{paper_derived_outcomes[primary]!r} and {paper_id!r}"
            )
        paper_derived_outcomes[primary] = paper_id


def test_paper_specific_signal_columns_no_unexpected_overlap() -> None:
    """全面扫描: 任何被 2+ 篇 paper 同时声明为 paper-specific 的列
    都必须在显式的 SHARED_CONTROLS 白名单中。"""
    specs = load_all_specs()
    bucket = _collect_paper_specific_signals(specs)

    collisions = []
    for col, claims in bucket.items():
        if len(claims) > 1 and col not in SHARED_CONTROLS:
            collisions.append((col, claims))

    if collisions:
        msg_lines = ['paper-specific signal column collisions (not in SHARED_CONTROLS allow-list):']
        for col, claims in collisions:
            msg_lines.append(f"  {col!r}: {claims}")
        pytest.fail("\n".join(msg_lines))


def test_8_paper_treatment_primary_count_equals_paper_count() -> None:
    """全部 11 篇 paper (5 既有 + 3 新增 + 3 provisional, 2026-06-01) 必须各自
    恰好声明一个 primary treatment 'spec' (可以是 primary str 或 primary_pair list)。"""
    specs = load_all_specs()
    assert len(specs) == 11

    for paper_id, spec in specs.items():
        t = spec.raw.get('treatment', {}) or {}
        has_primary = bool(_flatten(t.get('primary')))
        has_pair = bool(_flatten(t.get('primary_pair')))
        assert has_primary or has_pair, (
            f"{paper_id}: treatment missing both primary and primary_pair"
        )
