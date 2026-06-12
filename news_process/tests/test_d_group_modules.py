"""v3.7.0 D 组的测试: PR #11 (staleness) + #12 (α).

覆盖:
- pipeline.text.article_staleness.compute_surface_staleness (P0.3 算法验证)
- pipeline.audit.cross_media_alpha.compute_outlet_tone_aggregates (P1.6 修复)
"""
from __future__ import annotations

import time

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast


# ── PR #11 D2.a surface staleness (P0.3 重写后) ───────────────────────
class TestSurfaceStaleness:
    def test_empty_df(self):
        from news_process.pipeline.text.article_staleness import (
            compute_surface_staleness,
        )
        df = pd.DataFrame({'日期': [], '内容': []})
        stale = compute_surface_staleness(df, content_col='内容', num_perm=32)
        assert len(stale) == 0

    def test_all_nan_dates_returns_nan(self):
        from news_process.pipeline.text.article_staleness import (
            compute_surface_staleness,
        )
        df = pd.DataFrame({
            '日期': pd.to_datetime([None] * 3),
            '内容': ['银行 fintech 公告 A', '银行 fintech 公告 B', '银行 fintech 公告 C'],
        })
        stale = compute_surface_staleness(df, content_col='内容', num_perm=32)
        assert np.isnan(stale).all()

    def test_first_day_articles_are_nan(self):
        # 第 1 天的文章前面无邻居 (cutoff = day - 7d 内无 article)
        from news_process.pipeline.text.article_staleness import (
            compute_surface_staleness,
        )
        df = pd.DataFrame({
            '日期': pd.to_datetime(['2020-01-01', '2020-01-15']),
            '内容': ['银行 fintech A', '银行 fintech A'],  # 文本相同
        })
        stale = compute_surface_staleness(df, content_col='内容', num_perm=32)
        assert np.isnan(stale[0])  # 第 1 篇无 cutoff 前邻居
        assert np.isnan(stale[1])  # 第 2 篇距第 1 篇 14d > 7d window → 也 NaN

    def test_within_window_high_staleness_for_duplicates(self):
        from news_process.pipeline.text.article_staleness import (
            compute_surface_staleness,
        )
        df = pd.DataFrame({
            '日期': pd.to_datetime(['2020-01-01', '2020-01-05']),  # 4d apart
            '内容': ['完全相同的银行新闻'] * 2,
        })
        stale = compute_surface_staleness(df, content_col='内容', num_perm=64)
        assert np.isnan(stale[0])
        assert stale[1] >= 0.95, f"重复文本应 jaccard ≈ 1, 实际 {stale[1]}"

    def test_window_boundary_exact_7d_excluded(self):
        # WINDOW_DAYS=7, 第 8 天前的文章不应被算 (cutoff = day - 7d, < cutoff 才排除)
        from news_process.pipeline.text.article_staleness import (
            compute_surface_staleness,
        )
        df = pd.DataFrame({
            '日期': pd.to_datetime(['2020-01-01', '2020-01-09']),  # 8d apart
            '内容': ['银行 fintech 业务'] * 2,
        })
        stale = compute_surface_staleness(df, content_col='内容', num_perm=32)
        # 8d 距离恰超 WINDOW_DAYS=7, 第 2 篇看不到第 1 篇
        # 实测预期 NaN (window 空) 或 0.0 (无 candidate)
        assert np.isnan(stale[1]) or stale[1] == 0.0

    def test_algorithm_complexity_subquadratic(self):
        """P0.3 关键: 200 篇 × 30 天 surface staleness 必须 < 5s (原 O(N²) 1+ min)."""
        from news_process.pipeline.text.article_staleness import (
            compute_surface_staleness,
        )
        np.random.seed(42)
        n = 200
        dates = pd.to_datetime('2020-01-01') + pd.to_timedelta(
            np.sort(np.random.randint(0, 30, n)), unit='D'
        )
        contents = [f'银行业务 fintech 战略 {i}' for i in range(n)]
        df = pd.DataFrame({'日期': dates, '内容': contents})
        t0 = time.time()
        compute_surface_staleness(df, content_col='内容', num_perm=64)
        elapsed = time.time() - t0
        assert elapsed < 5.0, f"P0.3 算法回归: 200 articles took {elapsed:.2f}s (期望 < 5s)"


# ── PR #12 D3 Krippendorff α (P1.6 修复后 outlet × day matrix) ──────
class TestCrossMediaAlphaAggregates:
    def test_returns_dict_with_outlet_tones_and_matrix(self):
        from news_process.pipeline.audit.cross_media_alpha import (
            compute_outlet_tone_aggregates,
        )
        article_df = pd.DataFrame({
            'target_bank': ['A'] * 6,
            '媒体(中文)': ['M1', 'M1', 'M2', 'M2', 'M3', 'M3'],
            '日期': pd.to_datetime([
                '2020-06-01', '2020-06-02',
                '2020-06-01', '2020-06-03',
                '2020-06-02', '2020-06-04',
            ]),
            'llm_vote_tone_full': [0.5, 0.4, -0.3, -0.2, 0.1, 0.2],
        })
        events = pd.DataFrame({
            'target_bank': ['A'],
            'event_date': ['2020-06-02'],
        })
        out = compute_outlet_tone_aggregates(
            article_df, events, tone_col='llm_vote_tone_full',
        )
        assert len(out) == 1
        key = ('A', '2020-06-02')
        assert key in out
        v = out[key]
        assert 'outlet_tones' in v and 'daily_matrix' in v
        assert v['outlet_tones'].shape == (3,)  # 3 outlets
        # daily_matrix shape (n_outlets, n_days within ±3d window)
        assert v['daily_matrix'].shape[0] == 3

    def test_min_outlets_threshold(self):
        # 只 1 个 outlet 报道 → 跳过 (MIN_OUTLETS_PER_EVENT=2)
        from news_process.pipeline.audit.cross_media_alpha import (
            compute_outlet_tone_aggregates,
        )
        article_df = pd.DataFrame({
            'target_bank': ['A'],
            '媒体(中文)': ['只此一家'],
            '日期': pd.to_datetime(['2020-06-02']),
            'llm_vote_tone_full': [0.5],
        })
        events = pd.DataFrame({
            'target_bank': ['A'],
            'event_date': ['2020-06-02'],
        })
        out = compute_outlet_tone_aggregates(
            article_df, events, tone_col='llm_vote_tone_full',
        )
        assert len(out) == 0  # 跳过

    def test_variance_computation(self):
        """variance (第 10 篇 main 指标) 应可在无 krippendorff 包时也算出."""
        from news_process.pipeline.audit.cross_media_alpha import (
            compute_outlet_tone_aggregates,
            compute_variance_and_alpha,
        )
        article_df = pd.DataFrame({
            'target_bank': ['A'] * 4,
            '媒体(中文)': ['M1', 'M2', 'M3', 'M4'],
            '日期': pd.to_datetime(['2020-06-02'] * 4),
            'llm_vote_tone_full': [0.5, -0.5, 0.3, -0.3],
        })
        events = pd.DataFrame({
            'target_bank': ['A'],
            'event_date': ['2020-06-02'],
        })
        out = compute_outlet_tone_aggregates(
            article_df, events, tone_col='llm_vote_tone_full',
        )
        m = compute_variance_and_alpha(out)
        assert len(m) == 1
        assert m['n_outlets'].iloc[0] == 4
        assert m['variance'].iloc[0] > 0  # 4 outlets tone 分散, 必有方差
