"""Unit tests for paper_registry error paths (RR2-2 added by Review-only audit).

Covers the failure modes of paper_registry.get_spec / _load_one that previously had
0 explicit test coverage:
    1. Unknown paper_id (not in PAPER_IDS_ALL) → ValueError
    2. Missing yaml file (file system gap) → FileNotFoundError
    3. Malformed yaml (non-mapping root) → ValueError
    4. paper_id mismatch (directory vs declared field) → ValueError
    5. Missing required fields → ValueError
    6. PaperSpec.primary_outlet defensive fallback on non-dict targets → ''
"""

from __future__ import annotations

import pytest

from news_process.papers._common.paper_registry import (
    PaperSpec,
    _load_one,
    clear_cache,
    get_spec,
)

# ---------------------------------------------------------------------------
# Public API error paths
# ---------------------------------------------------------------------------


def test_unknown_paper_id_raises_value_error() -> None:
    """get_spec rejects paper_id not in PAPER_IDS_ALL whitelist."""
    with pytest.raises(ValueError, match=r"Unknown paper_id"):
        get_spec('not_a_real_paper')


def test_empty_paper_id_raises_value_error() -> None:
    with pytest.raises(ValueError, match=r"Unknown paper_id"):
        get_spec('')


# ---------------------------------------------------------------------------
# _load_one error paths (private but documented error modes)
# ---------------------------------------------------------------------------


def test_missing_yaml_raises_file_not_found(tmp_path, monkeypatch):
    """If paper_spec.yaml is missing, FileNotFoundError with clear context."""
    clear_cache()

    # Monkey-patch _spec_path_for to return a non-existent path
    fake_path = tmp_path / 'nonexistent' / 'paper_spec.yaml'
    monkeypatch.setattr(
        'news_process.papers._common.paper_registry._spec_path_for',
        lambda pid: fake_path,
    )
    with pytest.raises(FileNotFoundError, match=r"paper_spec\.yaml missing"):
        _load_one('bank_fintech_tone')


def test_malformed_yaml_non_mapping_raises_value_error(tmp_path, monkeypatch):
    """Yaml that parses to non-dict (e.g. list/string) → ValueError."""
    clear_cache()

    bad = tmp_path / 'bad.yaml'
    bad.write_text('- not\n- a\n- mapping\n', encoding='utf-8')
    monkeypatch.setattr(
        'news_process.papers._common.paper_registry._spec_path_for',
        lambda pid: bad,
    )
    with pytest.raises(ValueError, match=r"must be a YAML mapping"):
        _load_one('bank_fintech_tone')


def test_paper_id_mismatch_raises_value_error(tmp_path, monkeypatch):
    """Declared paper_id ≠ directory name → ValueError."""
    clear_cache()

    # Write a minimal valid-shape yaml but with wrong paper_id field
    bad = tmp_path / 'spec.yaml'
    bad.write_text(
        "paper_id: WRONG_NAME\n"
        "spec_version: 1.0.0\n"
        "status: existing\n"
        "differentiation_claim: dummy text long enough\n"
        "outcome: {primary: x}\n"
        "treatment: {primary: y}\n"
        "controls: {bank_level: [], year_level: [], fixed_effects: []}\n"
        "identification: {baseline: z}\n"
        "event_studies: []\n"
        "targets: {primary_outlet: TEST, ambitious_outlet: T, submission_window: 2027-01-01}\n"
        "sample: {n_bank_min: 1, t_year: 1, obs_target_min: 1}\n"
        "audit_rounds_target_min: 1\n",
        encoding='utf-8',
    )
    monkeypatch.setattr(
        'news_process.papers._common.paper_registry._spec_path_for',
        lambda pid: bad,
    )
    with pytest.raises(ValueError, match=r"paper_id mismatch"):
        _load_one('bank_fintech_tone')


def test_missing_required_fields_raises_value_error(tmp_path, monkeypatch):
    """If yaml is missing schema-required field, ValueError lists them."""
    clear_cache()

    bad = tmp_path / 'partial.yaml'
    bad.write_text(
        "paper_id: bank_fintech_tone\n"
        "spec_version: 1.0.0\n"
        "status: existing\n",  # missing 9 of 12 required fields
        encoding='utf-8',
    )
    monkeypatch.setattr(
        'news_process.papers._common.paper_registry._spec_path_for',
        lambda pid: bad,
    )
    with pytest.raises(ValueError, match=r"missing required fields"):
        _load_one('bank_fintech_tone')


# ---------------------------------------------------------------------------
# PaperSpec defensive property fallbacks (RR2-1)
# ---------------------------------------------------------------------------


def test_primary_outlet_returns_empty_when_targets_not_dict() -> None:
    """RR2-1 — defensive fallback: targets parsed as non-dict yields '' not crash."""
    from pathlib import Path

    bad_spec = PaperSpec(
        paper_id='x',
        spec_version='0.0.0',
        status='skeleton',
        spec_path=Path('/tmp/x'),
        raw={'targets': ['list', 'not', 'dict']},  # malformed
    )
    assert bad_spec.primary_outlet == ''


def test_primary_outlet_returns_empty_when_targets_missing() -> None:
    from pathlib import Path

    bad_spec = PaperSpec(
        paper_id='x', spec_version='0.0.0', status='skeleton',
        spec_path=Path('/tmp/x'), raw={},
    )
    assert bad_spec.primary_outlet == ''


def test_primary_outlet_returns_value_when_targets_well_formed() -> None:
    from pathlib import Path

    good_spec = PaperSpec(
        paper_id='x', spec_version='0.0.0', status='skeleton',
        spec_path=Path('/tmp/x'),
        raw={'targets': {'primary_outlet': 'JFE'}},
    )
    assert good_spec.primary_outlet == 'JFE'


def test_event_study_ids_returns_empty_list_when_non_list() -> None:
    from pathlib import Path

    spec_with_bad_events = PaperSpec(
        paper_id='x', spec_version='0.0.0', status='skeleton',
        spec_path=Path('/tmp/x'),
        raw={'event_studies': 'not_a_list'},
    )
    assert spec_with_bad_events.event_study_ids == []


def test_event_study_ids_returns_copy_not_reference() -> None:
    """Mutating the returned list should not affect spec.raw."""
    from pathlib import Path

    spec = PaperSpec(
        paper_id='x', spec_version='0.0.0', status='skeleton',
        spec_path=Path('/tmp/x'),
        raw={'event_studies': ['E1', 'E2']},
    )
    ids = spec.event_study_ids
    ids.append('E_INJECTED')
    assert 'E_INJECTED' not in spec.raw['event_studies']


# ---------------------------------------------------------------------------
# quality-hardening Round 19 (2026-05-27): PaperSpec.get + differentiation_claim
# paper_registry.py 95.59% → ~100% (lines 98, 103, 193)
# ---------------------------------------------------------------------------


def test_paper_spec_get_method_delegates_to_raw_dict():
    """PaperSpec.get 透传到 raw.get (paper_registry.py:98)."""
    from pathlib import Path
    spec = PaperSpec(
        paper_id='x', spec_version='0.0.0', status='skeleton',
        spec_path=Path('/tmp/x'),
        raw={'arbitrary_key': 'arbitrary_val', 'nested': {'a': 1}},
    )
    assert spec.get('arbitrary_key') == 'arbitrary_val'
    assert spec.get('nonexistent_field') is None  # 默认 default=None
    assert spec.get('nonexistent_field', 'my_default') == 'my_default'
    assert spec.get('nested') == {'a': 1}


def test_paper_spec_differentiation_claim_property():
    """differentiation_claim property: 有值 + 缺失 fallback '' (paper_registry.py:103)."""
    from pathlib import Path
    spec_with = PaperSpec(
        paper_id='x', spec_version='0.0.0', status='skeleton',
        spec_path=Path('/tmp/x'),
        raw={'differentiation_claim': 'our claim is unique'},
    )
    assert spec_with.differentiation_claim == 'our claim is unique'
    spec_without = PaperSpec(
        paper_id='y', spec_version='0.0.0', status='skeleton',
        spec_path=Path('/tmp/y'),
        raw={},
    )
    assert spec_without.differentiation_claim == ''


def test_list_paper_ids_returns_8_element_tuple():
    """list_paper_ids 返回 PAPER_IDS_ALL (paper_registry.py:193)."""
    from news_process.papers._common.paper_registry import (
        PAPER_IDS_ALL,
        list_paper_ids,
    )
    result = list_paper_ids()
    assert result == PAPER_IDS_ALL
    # 8 paper id (5 existing + 3 new)
    assert len(result) == 8
