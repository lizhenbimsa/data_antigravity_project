"""Tests for ``news_process.core.dag`` enabled_when predicates.

quality-hardening Round 35 (2026-05-27): core/dag.py 58.82% → ~100%.
模块此前覆盖率低因 predicates 多数路径未被任何测试直接调用; 此 file 把所有
predicates 各 case 都覆盖 (true / false / missing-key fallback).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.core.dag import (
    _VALIDATION_PREDS,
    _validation_flag,
    always_enabled,
    article_staleness_enabled,
    berts_method_enabled,
    llm_method_enabled,
    words_method_enabled,
)


def test_always_enabled_true_regardless_of_cfg():
    """always_enabled 永远返回 True (line 34)."""
    assert always_enabled({}) is True
    assert always_enabled({'whatever': 'value'}) is True


@pytest.mark.parametrize("method,predicate", [
    ('tone_llms', llm_method_enabled),
    ('tone_words', words_method_enabled),
    ('tone_berts', berts_method_enabled),
])
def test_method_predicate_returns_true_when_in_enabled_methods(method, predicate):
    """X_method_enabled True 当 enabled_methods 含 X (lines 39-58)."""
    cfg = {'sentiment_analysis': {'enabled_methods': [method, 'other']}}
    assert predicate(cfg) is True


@pytest.mark.parametrize("predicate", [
    llm_method_enabled, words_method_enabled, berts_method_enabled,
])
def test_method_predicate_returns_false_when_not_in_enabled_methods(predicate):
    """X_method_enabled False 当 enabled_methods 缺 X."""
    cfg = {'sentiment_analysis': {'enabled_methods': ['unrelated']}}
    assert predicate(cfg) is False


@pytest.mark.parametrize("predicate", [
    llm_method_enabled, words_method_enabled, berts_method_enabled,
])
def test_method_predicate_handles_missing_section(predicate):
    """X_method_enabled False 当 sentiment_analysis 缺失."""
    assert predicate({}) is False


def test_validation_flag_factory_creates_named_predicate():
    """_validation_flag 返回 named predicate, 默认 True (line 64-66)."""
    pred = _validation_flag('my_test_key')
    assert pred.__name__ == 'validation_my_test_key_enabled'
    # missing → default True
    assert pred({}) is True
    # explicit True
    assert pred({'validation': {'my_test_key': True}}) is True
    # explicit False
    assert pred({'validation': {'my_test_key': False}}) is False


def test_validation_flag_factory_with_default_false():
    """_validation_flag(key, default=False) 缺失 → False."""
    pred = _validation_flag('opt_in_key', default=False)
    assert pred({}) is False
    assert pred({'validation': {'opt_in_key': True}}) is True


def test_validation_preds_contain_expected_keys():
    """_VALIDATION_PREDS 含完整 14 个 validation 子任务 predicate."""
    expected = {
        'threshold_sensitivity', 'dedup_sensitivity', 'classification_eval',
        'sentiment_validation', 'radius_sensitivity', 'entity_masking',
        'dict_coverage_audit', 'media_diversity', 'prompt_sensitivity',
        'inter_track_kappa', 'construct_orthogonality',
        'lexical_discriminant_validity', 'lm_discriminant_validity',
        'cross_media_alpha',
    }
    assert expected.issubset(set(_VALIDATION_PREDS.keys()))


@pytest.mark.parametrize("predicate,cfg_key", [
    (article_staleness_enabled, 'article_staleness'),
])
def test_optin_predicate_default_false(predicate, cfg_key):
    """所有 opt-in 谓词缺 cfg → False (line 82)."""
    assert predicate({}) is False


@pytest.mark.parametrize("predicate,cfg_key", [
    (article_staleness_enabled, 'article_staleness'),
])
def test_optin_predicate_true_when_enabled(predicate, cfg_key):
    """opt-in 谓词在 cfg[key].enabled=true 时返回 True."""
    cfg = {cfg_key: {'enabled': True}}
    assert predicate(cfg) is True


# ---------------------------------------------------------------------------
# quality-hardening Round 37 (2026-05-27): filter_enabled / get_script_for_method
# 补 dag.py 剩余 8 miss (lines 556, 594-600) → ≥90%
# ---------------------------------------------------------------------------


def test_filter_enabled_keeps_only_true_predicates():
    """filter_enabled 仅保留 enabled_when(cfg)==True 的 stages (line 556)."""
    from news_process.core.dag import StageSpec, filter_enabled

    spec_on = StageSpec(name='on', script='on.py', group='main',
                        enabled_when=lambda _c: True)
    spec_off = StageSpec(name='off', script='off.py', group='main',
                         enabled_when=lambda _c: False)
    result = filter_enabled([spec_on, spec_off], {})
    assert result == [spec_on]


def test_filter_enabled_empty_when_all_false():
    """全部谓词 False → 空列表."""
    from news_process.core.dag import StageSpec, filter_enabled

    spec = StageSpec(name='off', script='off.py', group='main',
                     enabled_when=lambda _c: False)
    assert filter_enabled([spec, spec], {}) == []


def test_filter_enabled_preserves_order_for_truthy_subset():
    """filter_enabled 保留原列表顺序 (list comprehension 不重排)."""
    from news_process.core.dag import StageSpec, filter_enabled

    s1 = StageSpec(name='1', script='1.py', group='main',
                   enabled_when=lambda _c: True)
    s2 = StageSpec(name='2', script='2.py', group='main',
                   enabled_when=lambda _c: False)
    s3 = StageSpec(name='3', script='3.py', group='main',
                   enabled_when=lambda _c: True)
    result = filter_enabled([s1, s2, s3], {})
    assert [s.name for s in result] == ['1', '3']


def test_get_script_for_method_known_methods():
    """METHOD_TO_PREDICATE 中的 3 个 method 都能找到 STAGES_MAIN 中 stage script."""
    from news_process.core.dag import METHOD_TO_PREDICATE, get_script_for_method

    for method in METHOD_TO_PREDICATE:
        script = get_script_for_method(method)
        # 锚定: 21_tone_llms / 22_tone_words / 23_tone_berts 三个 stage 在 STAGES_MAIN
        # 中以对应 method 名为前缀
        assert script is not None, f"method {method} maps to no STAGES_MAIN script"
        assert script.endswith('.py')
        # method ↔ script 命名约定: script 文件名含 method
        # ('tone_llms' → '21_tone_llms.py' etc.)
        assert method in script


def test_get_script_for_method_unknown_returns_none():
    """未登记的 method (lines 594-596) 返回 None."""
    from news_process.core.dag import get_script_for_method

    assert get_script_for_method('nonexistent_method') is None
    assert get_script_for_method('') is None


def test_get_script_for_method_fallback_when_predicate_unmounted():
    """method 已登记但 STAGES_MAIN 无 stage 用此谓词 → None (line 600 fallthrough).

    用 monkeypatch 把 METHOD_TO_PREDICATE 加一项指向陌生谓词, 验证 fallthrough.
    """
    import news_process.core.dag as dag

    fake_pred = lambda _c: True  # noqa: E731 — module-level scope unnecessary, just需 identity 不匹配
    original = dag.METHOD_TO_PREDICATE.copy()
    try:
        dag.METHOD_TO_PREDICATE['__test_unknown__'] = fake_pred
        # fake_pred 不在 STAGES_MAIN 任一 enabled_when 上 → for loop fallthrough → return None
        assert dag.get_script_for_method('__test_unknown__') is None
    finally:
        dag.METHOD_TO_PREDICATE.clear()
        dag.METHOD_TO_PREDICATE.update(original)
