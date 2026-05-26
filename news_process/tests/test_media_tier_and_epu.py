"""Tests for v3.6.1 PR #5 (B1 EPU merge) + PR #6 (C1 媒体 3 级 tier).

覆盖:
- pipeline.panel.encode.compute_media_tier_weights
- pipeline.external.epu_merge.load_epu_china
- pipeline.external.epu_merge.aggregate_epu_to_bank_year
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


# ── PR #5 B1 EPU merge ────────────────────────────────────────────────
class TestEpuLoad:
    def test_missing_file_returns_empty(self, tmp_path):
        from news_process.pipeline.external.epu_merge import load_epu_china
        # 不存在的 path → 空 DataFrame
        d = load_epu_china(path=tmp_path / 'no_such_file.csv')
        assert d.empty
        assert list(d.columns) == ['year', 'month', 'epu']

    def test_load_valid_csv(self, tmp_path):
        from news_process.pipeline.external.epu_merge import load_epu_china
        csv = tmp_path / 'epu.csv'
        csv.write_text(
            "year,month,epu\n"
            "2020,1,100.5\n"
            "2020,2,110.3\n"
            "2020,3,95.7\n",
            encoding='utf-8',
        )
        d = load_epu_china(path=csv)
        assert len(d) == 3
        assert set(d.columns) == {'year', 'month', 'epu'}
        assert d['epu'].iloc[0] == 100.5

    def test_case_insensitive_columns(self, tmp_path):
        from news_process.pipeline.external.epu_merge import load_epu_china
        csv = tmp_path / 'epu.csv'
        csv.write_text("YEAR,MONTH,EPU\n2020,1,100\n", encoding='utf-8')
        d = load_epu_china(path=csv)
        assert 'year' in d.columns and 'month' in d.columns and 'epu' in d.columns

    def test_missing_required_columns(self, tmp_path):
        from news_process.pipeline.external.epu_merge import load_epu_china
        csv = tmp_path / 'bad.csv'
        csv.write_text("year,month\n2020,1\n", encoding='utf-8')
        d = load_epu_china(path=csv)
        assert d.empty  # 缺 'epu' → 退化


class TestEpuAggregateBankYear:
    def test_empty_epu_returns_nan_panel(self):
        from news_process.pipeline.external.epu_merge import (
            aggregate_epu_to_bank_year,
        )
        article = pd.DataFrame({
            'target_bank': ['A', 'A', 'B'],
            'year': [2020, 2020, 2021],
        })
        epu = pd.DataFrame(columns=['year', 'month', 'epu'])
        panel = aggregate_epu_to_bank_year(article, epu)
        assert len(panel) == 2  # 2 bank-year
        assert panel['epu_mean_year'].isna().all()
        assert (panel['epu_data_complete'] == 0).all()

    def test_year_only_fallback(self):
        # 无日期列 → 仅按 year merge
        from news_process.pipeline.external.epu_merge import (
            aggregate_epu_to_bank_year,
        )
        article = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2020, 2020],
        })
        epu = pd.DataFrame({
            'year': [2020] * 12,
            'month': list(range(1, 13)),
            'epu': [100.0] * 12,
        })
        panel = aggregate_epu_to_bank_year(article, epu)
        assert len(panel) == 1
        assert panel['epu_mean_year'].iloc[0] == 100.0

    def test_full_year_complete_flag(self):
        from news_process.pipeline.external.epu_merge import (
            aggregate_epu_to_bank_year,
        )
        article = pd.DataFrame({
            'target_bank': ['A'] * 12,
            'year': [2020] * 12,
            '日期': pd.to_datetime([f'2020-{m:02d}-15' for m in range(1, 13)]),
        })
        epu = pd.DataFrame({
            'year': [2020] * 12,
            'month': list(range(1, 13)),
            'epu': [float(m * 10) for m in range(1, 13)],
        })
        panel = aggregate_epu_to_bank_year(article, epu)
        assert panel['epu_data_complete'].iloc[0] == 1
        assert abs(panel['epu_mean_year'].iloc[0] - 65.0) < 0.01  # mean(10..120)


# ---------------------------------------------------------------------------
# quality-hardening Round 26 (2026-05-27): epu_merge._resolve_epu_path coverage
# lines 65-71 — config path + default path fallback + None when missing
# ---------------------------------------------------------------------------


def test_resolve_epu_path_returns_config_path_when_exists(tmp_path, monkeypatch):
    """cfg['paths']['epu_china_csv'] 存在 → 返回 (line 65-67)."""
    import news_process.pipeline.external.epu_merge as M
    fake_csv = tmp_path / 'epu_real.csv'
    fake_csv.write_text('year,month,epu\n2020,1,100\n', encoding='utf-8')
    monkeypatch.setitem(M.CONFIG['paths'], 'epu_china_csv', str(fake_csv))
    result = M._resolve_epu_path()
    assert result == fake_csv


def test_resolve_epu_path_returns_none_when_both_missing(tmp_path, monkeypatch):
    """cfg 路径不存在 + default 不存在 → None (line 71).

    通过 monkeypatch _PROJECT_PARENT 指向 tmp_path 让 default fallback 不存在.
    """
    import news_process.pipeline.external.epu_merge as M
    monkeypatch.setitem(M.CONFIG['paths'], 'epu_china_csv',
                        str(tmp_path / 'nonexistent.csv'))
    monkeypatch.setattr(M, '_PROJECT_PARENT', str(tmp_path))
    result = M._resolve_epu_path()
    assert result is None
