"""M0 G0 acceptance — 8 paper 列名冲突扫描.

Plan v2.x §5.2.2 M0.3 + §5.2.4 G0:
    "8 paper 列名冲突: 0 冲突 (跨 8 paper)"

红线不变式
----------
1. 8 paper 的 ``treatment.primary`` 必须互不重复 (paper-specific signal column).
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

# Shared utility columns (controls / FE) — allowed to overlap across papers.
SHARED_CONTROLS: frozenset[str] = frozenset({
    # bank-level standard controls
    'ln_assets', 'leverage', 'capital_ratio', 'npl_ratio', 'deposit_growth',
    # year-level macro controls
    'gdp_growth', 'm2_growth',
    # fixed effects
    'bank_fe', 'year_fe',
    # ROA / market-cap 作为 outcome.secondary 跨 paper 共享 (P1+benefit+broker+llm+strategic)
    'roa', 'loan_growth', 'ln_market_cap',
    # CAR 3-day generic — some specs may have it under secondary
    'car_3day',
    'tobin_q',
    'strat_fluidity',  # strategic_diff secondary
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

        # P4 treatment uses primary_pair (list) instead of primary
        for col in _flatten(treatment.get('primary')):
            bucket[col].append((paper_id, 'treatment.primary'))
        for col in _flatten(treatment.get('primary_pair')):
            bucket[col].append((paper_id, 'treatment.primary_pair'))

        # mediator.primary (only present on P2/P4)
        for col in _flatten(mediator.get('primary')):
            bucket[col].append((paper_id, 'mediator.primary'))

        # outcome.primary — only paper-specific derived names count
        for col in _flatten(outcome.get('primary')):
            if col not in SHARED_CONTROLS:
                bucket[col].append((paper_id, 'outcome.primary'))

    return bucket


def test_treatment_primary_columns_are_unique() -> None:
    specs = load_all_specs()

    primaries: dict[str, str] = {}  # column -> paper_id
    for paper_id, spec in specs.items():
        t = spec.raw.get('treatment', {}) or {}
        # primary may be str OR primary_pair may be list (P4)
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
    """Plan §B.X intentionally diverges car_3day_window names between P1 (tone_shock) /
    P3 (fintech_announcement) / P4 (5day) to avoid salami slicing collision (R10-M01).
    """
    specs = load_all_specs()
    paper_derived_outcomes: dict[str, str] = {}
    for paper_id, spec in specs.items():
        primary = spec.raw.get('outcome', {}).get('primary', '')
        if primary in SHARED_CONTROLS:
            continue  # shared outcome (e.g. roa); covered by SHARED_CONTROLS exemption
        if not primary:
            continue
        if primary in paper_derived_outcomes:
            pytest.fail(
                f"outcome.primary collision: {primary!r} declared by both "
                f"{paper_derived_outcomes[primary]!r} and {paper_id!r}"
            )
        paper_derived_outcomes[primary] = paper_id


def test_paper_specific_signal_columns_no_unexpected_overlap() -> None:
    """Comprehensive scan: any column claimed as paper-specific by 2+ papers
    should be in the explicit SHARED_CONTROLS allow-list."""
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
    """Each of 8 papers must declare exactly one primary treatment 'spec' (could be
    primary str or primary_pair list)."""
    specs = load_all_specs()
    assert len(specs) == 8

    for paper_id, spec in specs.items():
        t = spec.raw.get('treatment', {}) or {}
        has_primary = bool(_flatten(t.get('primary')))
        has_pair = bool(_flatten(t.get('primary_pair')))
        assert has_primary or has_pair, (
            f"{paper_id}: treatment missing both primary and primary_pair"
        )
