"""tests/test_sbert_whole_text_v2.py — stage 25 输入构造 v2 (整篇) gate。

背景 (2026-07-26 用户裁定): stage 25 由 v1「Bybee 标题(≤100)+首段(≤300) 截断」改为
v2「整篇」, 目的是与 stage 16 (policy_alignment) **逐字节同构**从而完全复用其已播种的
嵌入缓存 (只读探针实证: 三轨并集 582,724 唯一块, 两 spec 各 582,724/582,724 命中 miss=0)。

本文件锁死四条命门, 任一破损都会导致「该轨全体 cache miss + 付费重嵌」或「静默串代」:
  ① 三轨构造与 stage 16 逐字节同构 —— 含 **full 轨独有 `.strip()`** 的不对称;
  ② 无预截断 (>400 字文本整篇送出);
  ③ **绝不因本模块构造变更 bump spec 级 `text_pipeline_version`** (一 bump 全项目嵌入缓存作废);
  ④ 产物带 `sbert_input_strategy` provenance 列 (两代产物的 text_pipeline_version 相同,
     无此列则不可区分 → 混用会静默串代)。
另锁 v1 回退口径可用 (INPUT_STRATEGY='bybee400_v1')。
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.text import article_sbert as S  # noqa: E402


def _df():
    """三轨文本各带首尾空白 (唯有 full 轨应被 strip)。"""
    return pd.DataFrame({
        '标题': ['某行推出数字人民币'],
        '内容': ['  正文段落。  '],
        'content_full': ['  某行推出数字人民币。正文段落。  '],
        'content_ctx': ['  某行推出数字人民币。实体窗口句。  '],
        'content_ss': ['  某行推出数字人民币。同句共现。  '],
    })


# ── ① 与 stage 16 逐字节同构 (含 full 轨独有 strip 的不对称) ──

def test_v2_three_tracks_byte_identical_to_stage16():
    df = _df()
    got_full = S._build_track_docs(df, 'content_full', None, strip_text=True)
    got_ctx = S._build_track_docs(df, 'content_ctx', None, strip_text=False)
    got_ss = S._build_track_docs(df, 'content_ss', None, strip_text=False)
    # stage 16 `policy_alignment.main()` 的三轨构造 (逐字照搬其表达式)
    exp_full = df['content_full'].fillna('').astype(str).str.strip().tolist()
    exp_ctx = df['content_ctx'].fillna('').astype(str).tolist()
    exp_ss = df['content_ss'].fillna('').astype(str).tolist()
    assert got_full == exp_full, 'full 轨与 stage 16 构造不一致 → 全轨 cache miss + 付费重嵌'
    assert got_ctx == exp_ctx, 'ctx 轨与 stage 16 构造不一致 (stage 16 的 ctx 轨**不** strip)'
    assert got_ss == exp_ss, 'ss 轨与 stage 16 构造不一致 (stage 16 的 ss 轨**不** strip)'


def test_strip_asymmetry_is_load_bearing():
    """full 带 strip / ctx·ss 不带 —— 该不对称照抄 stage 16, 不得"统一"。"""
    df = _df()
    full = S._build_track_docs(df, 'content_full', None, strip_text=True)[0]
    ctx = S._build_track_docs(df, 'content_ctx', None, strip_text=False)[0]
    assert not full.startswith(' ') and not full.endswith(' '), 'full 轨必须 strip'
    assert ctx.startswith(' ') and ctx.endswith(' '), \
        'ctx 轨必须**不** strip (与 stage 16 一致); 擅自 strip 会使该轨全体 cache miss'


def test_fallback_branch_matches_stage16_fallback():
    """旧 schema 回退 (无 content_*) 亦须对齐 stage 16 的 prepend_title(...).strip()。"""
    from news_process.core.text.entity_context import prepend_title
    df = _df().drop(columns=['content_full', 'content_ctx', 'content_ss'])
    got = S._build_track_docs(df, '内容', '标题')
    exp = [prepend_title(t, b).strip()
           for t, b in zip(df['标题'].fillna('').astype(str),
                           df['内容'].fillna('').astype(str))]
    assert got == exp, '回退分支与 stage 16 回退分支不一致 → 回退路径亦无法共享缓存'


# ── ② 无预截断 ──

def test_v2_does_not_truncate():
    long_text = '甲' * 5000
    df = pd.DataFrame({'content_full': [long_text]})
    got = S._build_track_docs(df, 'content_full', None, strip_text=True)[0]
    assert len(got) == 5000, f'v2 不得预截断 (实得 {len(got)} 字); 超长应交引擎切块池化'
    assert got == long_text


# ── ③ 严禁 bump spec 级版本号 ──

def test_text_pipeline_version_is_spec_level_not_local_literal():
    """版本号必须仍由 spec (config) 读出 —— 本模块绝不得自持字面量覆盖。

    一旦因本阶段构造变更去 bump 该值, stage 15/16/26/27/40 共用的全部已播种嵌入
    (2026-07-24/25 生产首播 117 万条 + 增量) 会**整体作废需重播**。"""
    from news_process.pipeline.text import embedding_engine as eng
    assert eng.spec_version(S._MAIN_SPEC) == S._TEXT_PIPELINE_VERSION
    assert eng.spec_version(S._LARGE_SPEC) == S._TEXT_PIPELINE_VERSION_LG


# ── ④ provenance 列 ──

def test_output_frame_carries_input_strategy_provenance():
    df = pd.DataFrame({
        'docid': ['x', 'y'],
        'target_bank': ['A', 'B'],
        'year': [2020, 2021],
        '日期': pd.to_datetime(['2020-01-01', '2021-01-01']),
    })
    embs = np.ones((2, 3), dtype=np.float32)
    out = S._build_output_frame(df, embs, embs, embs,
                                embs_full_lg=embs, embs_ctx_lg=embs, embs_ss_lg=embs)
    assert 'sbert_input_strategy' in out.columns, (
        '缺 sbert_input_strategy 列 → v1/v2 两代产物 provenance 不可区分 (会静默串代)')
    assert out['sbert_input_strategy'].iloc[0] == S.INPUT_STRATEGY


# ── 策略开关: 合法值 / fail-loud / v1 回退可用 ──

def test_unknown_strategy_fails_loud(monkeypatch):
    monkeypatch.setattr(S, 'INPUT_STRATEGY', 'bogus_v9')
    with pytest.raises(ValueError, match='INPUT_STRATEGY'):
        S._build_track_docs(_df(), 'content_full', None, strip_text=True)


def test_v1_rollback_restores_400char(monkeypatch):
    monkeypatch.setattr(S, 'INPUT_STRATEGY', 'bybee400_v1')
    long_text = '乙' * 5000
    df = pd.DataFrame({'content_full': [long_text]})
    got = S._build_track_docs(df, 'content_full', None)[0]
    assert len(got) == S.TITLE_CHARS + S.FIRST_PARA_CHARS == 400, \
        'v1 回退口径应恢复 400 字截断 (常量与 _truncate_for_sbert 须保留可用)'


def test_current_strategy_is_v2():
    assert S.INPUT_STRATEGY == 'whole_text_v2', (
        '现行口径应为 v2 整篇 (2026-07-26 用户裁定); 若确需回退请连同说明书/计划一并更新')
