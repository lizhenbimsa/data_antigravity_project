"""Tests for v3.6.1 PR #6 (C1 媒体 3 级 tier).

覆盖:
- pipeline.panel.encode.compute_media_tier_weights
- panel runner.py 集成验证 (P0.1 修复后)
"""
from __future__ import annotations

import pandas as pd
import pytest

pytestmark = pytest.mark.fast


# ── PR #6 C1 媒体 3 级 tier ──────────────────────────────────────────
class TestComputeMediaTierWeights:
    def test_empty_df(self):
        from news_process.pipeline.panel.encode import (
            compute_media_tier_weights,
        )
        df = pd.DataFrame(columns=['媒体(中文)'])
        out = compute_media_tier_weights(df)
        assert 'media_authority_weight_tier' in out.columns
        assert 'media_tier_label' in out.columns

    def test_no_media_column(self):
        # 缺 '媒体(中文)' 列, 应退化为全 'other' weight 1.0
        from news_process.pipeline.panel.encode import (
            compute_media_tier_weights,
        )
        df = pd.DataFrame({'foo': [1, 2, 3]})
        out = compute_media_tier_weights(df)
        assert (out['media_authority_weight_tier'] == 1.0).all()
        assert (out['media_tier_label'] == 'other').all()

    def test_central_media_classified(self):
        # '光明日报' 仅在 central_media (不双归属 comprehensive); 测纯 central 分类.
        # 注: '人民日报' 同时出现在 central 与 comprehensive 列, 按设计
        # financial > comprehensive > central 优先级会落 comprehensive.
        from news_process.pipeline.panel.encode import (
            compute_media_tier_weights,
        )
        df = pd.DataFrame({'媒体(中文)': ['光明日报']})
        out = compute_media_tier_weights(df)
        assert out['media_tier_label'].iloc[0] == 'central'
        assert out['media_authority_weight_tier'].iloc[0] == 2.5

    def test_priority_financial_over_comprehensive_over_central(self):
        # 双归属 (人民日报 ∈ central ∩ comprehensive) 应落 comprehensive
        from news_process.pipeline.panel.encode import (
            compute_media_tier_weights,
        )
        df = pd.DataFrame({'媒体(中文)': ['人民日报']})
        out = compute_media_tier_weights(df)
        assert out['media_tier_label'].iloc[0] == 'comprehensive', \
            "人民日报双归属应优先 comprehensive (financial > comprehensive > central)"

    def test_financial_media_classified(self):
        # '21 世纪经济报道' 在 financial_media
        from news_process.pipeline.panel.encode import (
            compute_media_tier_weights,
        )
        df = pd.DataFrame({'媒体(中文)': ['21世纪经济报道', '第一财经日报']})
        out = compute_media_tier_weights(df)
        assert (out['media_tier_label'] == 'financial').all()
        assert (out['media_authority_weight_tier'] == 2.0).all()

    def test_comprehensive_media_classified(self):
        from news_process.pipeline.panel.encode import (
            compute_media_tier_weights,
        )
        df = pd.DataFrame({'媒体(中文)': ['南方都市报', '新京报']})
        out = compute_media_tier_weights(df)
        assert (out['media_tier_label'] == 'comprehensive').all()
        assert (out['media_authority_weight_tier'] == 1.5).all()

    def test_unknown_media_falls_other(self):
        from news_process.pipeline.panel.encode import (
            compute_media_tier_weights,
        )
        df = pd.DataFrame({'媒体(中文)': ['不存在的报纸 XYZ']})
        out = compute_media_tier_weights(df)
        assert out['media_tier_label'].iloc[0] == 'other'
        assert out['media_authority_weight_tier'].iloc[0] == 1.0

    def test_custom_weights(self):
        from news_process.pipeline.panel.encode import (
            compute_media_tier_weights,
        )
        # '光明日报' 仅 central; '不存在' 落 other
        df = pd.DataFrame({'媒体(中文)': ['光明日报', '不存在的报纸 XYZ']})
        custom = {'central': 5.0, 'financial': 3.0,
                  'comprehensive': 2.0, 'other': 0.5}
        out = compute_media_tier_weights(df, weights=custom)
        assert out['media_authority_weight_tier'].iloc[0] == 5.0
        assert out['media_authority_weight_tier'].iloc[1] == 0.5

    def test_append_only_no_override(self):
        # P0.1 关键: 新加 _tier 列与原 media_authority_weight 并存, 不覆盖
        from news_process.pipeline.panel.encode import (
            compute_media_tier_weights,
        )
        df = pd.DataFrame({
            '媒体(中文)': ['人民日报'],
            'media_authority_weight': [3.14],  # 原 continuous 列
        })
        out = compute_media_tier_weights(df)
        assert out['media_authority_weight'].iloc[0] == 3.14, \
            "C1 必须 append-only, 不破坏原 main spec"
        assert 'media_authority_weight_tier' in out.columns


class TestPanelRunnerCallerIntegration:
    def test_runner_imports_compute_media_tier_weights(self):
        """P0.1 修复验证: panel/runner.py 已 import compute_media_tier_weights."""
        import inspect

        from news_process.pipeline.panel import runner
        src = inspect.getsource(runner)
        assert 'compute_media_tier_weights' in src, \
            "P0.1 未修复: panel/runner.py 未 import compute_media_tier_weights"
        # 必须真调用, 不只是 import
        assert 'compute_media_tier_weights(df)' in src, \
            "P0.1 未修复: panel/runner.py 未真调用"
