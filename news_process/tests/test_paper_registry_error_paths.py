"""paper_registry 错误路径单元测试 (RR2-2, Review-only audit 补充)。

覆盖 paper_registry.get_spec / _load_one 此前零显式测试覆盖的失败模式:
    1. 未知 paper_id (不在 PAPER_IDS_ALL 白名单) → ValueError
    2. yaml 文件缺失 (文件系统缺口) → FileNotFoundError
    3. 畸形 yaml (根节点非 mapping) → ValueError
    4. paper_id 不匹配 (目录名 vs 声明字段) → ValueError
    5. 缺必填字段 → ValueError
    6. targets 非 dict 时 PaperSpec.primary_outlet 防御性回退 → ''
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
# 公共 API 错误路径
# ---------------------------------------------------------------------------


def test_unknown_paper_id_raises_value_error() -> None:
    """get_spec 拒绝不在 PAPER_IDS_ALL 白名单中的 paper_id。"""
    with pytest.raises(ValueError, match=r"Unknown paper_id"):
        get_spec('not_a_real_paper')


def test_empty_paper_id_raises_value_error() -> None:
    with pytest.raises(ValueError, match=r"Unknown paper_id"):
        get_spec('')


# ---------------------------------------------------------------------------
# _load_one 错误路径 (私有函数, 但错误模式有文档约定)
# ---------------------------------------------------------------------------


def test_missing_yaml_raises_file_not_found(tmp_path, monkeypatch):
    """paper_spec.yaml 缺失时 → FileNotFoundError 且报错信息上下文清晰。"""
    clear_cache()

    # monkeypatch _spec_path_for 使其返回一个不存在的路径
    fake_path = tmp_path / 'nonexistent' / 'paper_spec.yaml'
    monkeypatch.setattr(
        'news_process.papers._common.paper_registry._spec_path_for',
        lambda pid: fake_path,
    )
    with pytest.raises(FileNotFoundError, match=r"paper_spec\.yaml missing"):
        _load_one('bank_fintech_tone')


def test_malformed_yaml_non_mapping_raises_value_error(tmp_path, monkeypatch):
    """yaml 解析结果非 dict (如 list/string) → ValueError。"""
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
    """声明的 paper_id ≠ 目录名 → ValueError。"""
    clear_cache()

    # 写一个形状最小但 paper_id 字段错误的 yaml
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
    """yaml 缺 schema 必填字段时, ValueError 须列出缺失项。"""
    clear_cache()

    bad = tmp_path / 'partial.yaml'
    bad.write_text(
        "paper_id: bank_fintech_tone\n"
        "spec_version: 1.0.0\n"
        "status: existing\n",  # 12 个必填字段缺了 9 个
        encoding='utf-8',
    )
    monkeypatch.setattr(
        'news_process.papers._common.paper_registry._spec_path_for',
        lambda pid: bad,
    )
    with pytest.raises(ValueError, match=r"missing required fields"):
        _load_one('bank_fintech_tone')


# ---------------------------------------------------------------------------
# PaperSpec 防御性 property 回退 (RR2-1)
# ---------------------------------------------------------------------------


def test_primary_outlet_returns_empty_when_targets_not_dict() -> None:
    """RR2-1 — 防御性回退: targets 解析为非 dict 时返回 '' 而非崩溃。"""
    from pathlib import Path

    bad_spec = PaperSpec(
        paper_id='x',
        spec_version='0.0.0',
        status='skeleton',
        spec_path=Path('/tmp/x'),
        raw={'targets': ['list', 'not', 'dict']},  # 畸形输入
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
    """改动返回的 list 不应影响 spec.raw (返回副本而非引用)。"""
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
# paper_registry.py 覆盖率 95.59% → ~100% (补 98, 103, 193 行)
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
    """list_paper_ids 返回 PAPER_IDS_ALL (paper_registry.py:193).

    注: 函数名中的 "8_element" 是历史遗留 (当时 8 篇); 2026-06-01 起为 11 篇,
    断言以下方 len == 11 为准。"""
    from news_process.papers._common.paper_registry import (
        PAPER_IDS_ALL,
        list_paper_ids,
    )
    result = list_paper_ids()
    assert result == PAPER_IDS_ALL
    # 11 paper id (5 existing + 3 new + 3 provisional, 2026-06-01)
    assert len(result) == 11
