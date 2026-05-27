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
    article_topic_enabled,
    berts_method_enabled,
    executive_ner_enabled,
    llm_method_enabled,
    risk_taking_outcomes_enabled,
    temporal_mask_enabled,
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
        'cross_media_alpha', 'track_discriminant_validity',
    }
    assert expected.issubset(set(_VALIDATION_PREDS.keys()))


@pytest.mark.parametrize("predicate,cfg_key", [
    (temporal_mask_enabled, 'temporal_mask_test'),
    (risk_taking_outcomes_enabled, 'risk_taking_outcomes'),
    (executive_ner_enabled, 'executive_ner'),
    (article_topic_enabled, 'article_topic'),
    (article_staleness_enabled, 'article_staleness'),
])
def test_optin_predicate_default_false(predicate, cfg_key):
    """所有 opt-in 谓词缺 cfg → False (lines 72, 86, 101, 116, 131)."""
    assert predicate({}) is False


@pytest.mark.parametrize("predicate,cfg_key", [
    (temporal_mask_enabled, 'temporal_mask_test'),
    (risk_taking_outcomes_enabled, 'risk_taking_outcomes'),
    (executive_ner_enabled, 'executive_ner'),
    (article_topic_enabled, 'article_topic'),
    (article_staleness_enabled, 'article_staleness'),
])
def test_optin_predicate_true_when_enabled(predicate, cfg_key):
    """opt-in 谓词在 cfg[key].enabled=true 时返回 True."""
    cfg = {cfg_key: {'enabled': True}}
    assert predicate(cfg) is True
