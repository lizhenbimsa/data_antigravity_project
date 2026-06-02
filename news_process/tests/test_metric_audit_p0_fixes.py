"""回归测试: metric-audit 2026-06-02 的 P0 崩溃/错位修复.

覆盖两个修复 (见 scripts/audit/METRIC_AUDIT_FINAL_2026-06-02.md §2):
- P0-④ staleness: compute_surface_staleness 行错位 (返回排序序数组按位置赋回未
  排序帧). 修复后返回值必须跟随**输入行序**.
- P0-③/④ schema 契约: stage 18/19 的输入 13_news_with_ctx 只有 str 型 '日期'、
  无 'year' 列; main() 直接 groupby(['target_bank','year']) → KeyError. 修复在
  聚合前从 '日期' 派生 'year'. 本测试钉住该 schema 契约.

审计教训: 原审第一轮只验 metric 公式、从未跑 main() 真实数据, 致 stage 端到端
崩溃漏报. 这些是缺失的端到端守卫.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast

# 两组明显不同的中文文本 (组内近重复 → MinHash jaccard ≈ 1; 组间低相似)
_TXT_X = '工商银行金融科技数字化转型推进开放银行建设取得显著成效与突破'
_TXT_A = '建设银行发布年度报告净利润同比增长不良贷款率下降资本充足稳健'


class TestSurfaceStalenessRowOrder:
    """P0-④: surface staleness 必须跟随输入行序, 不得返回排序序错位."""

    def _frame(self):
        # 构造: 输入行序 != 日期排序序, 且每篇 staleness 可预测.
        #   pos0 art0: 01-20, 内容X (其 7d 前窗为空 → NaN)
        #   pos1 art1: 01-01, 内容A (首篇无前驱 → NaN)
        #   pos2 art2: 01-21, 内容X (7d 内含 art0 近重复 → 高)
        #   pos3 art3: 01-02, 内容A (7d 内含 art1 近重复 → 高)
        return pd.DataFrame({
            'target_bank': ['工商银行'] * 4,
            '日期': pd.to_datetime(['2018-01-20', '2018-01-01',
                                    '2018-01-21', '2018-01-02']),
            '内容': [_TXT_X, _TXT_A, _TXT_X, _TXT_A],
        })

    def test_staleness_lands_on_correct_rows(self):
        from news_process.pipeline.text.article_staleness import (
            compute_surface_staleness,
        )
        s = compute_surface_staleness(self._frame(), content_col='内容', num_perm=64)
        assert len(s) == 4
        # 修复前 (排序序错位) s[1] 会拿到高值 → 本断言失败; 修复后跟随输入序.
        assert np.isnan(s[0]), f"art0(01-20, 窗空)应 NaN, 实得 {s[0]}"
        assert np.isnan(s[1]), f"art1(01-01, 首篇)应 NaN, 实得 {s[1]}"
        assert s[2] > 0.5, f"art2(01-21, 近重复 art0)应高 staleness, 实得 {s[2]}"
        assert s[3] > 0.5, f"art3(01-02, 近重复 art1)应高 staleness, 实得 {s[3]}"

    def test_shuffle_invariance(self):
        """同一组文章, 输入行序任意打乱, 按行ID映射的 staleness 必须不变."""
        from news_process.pipeline.text.article_staleness import (
            compute_surface_staleness,
        )
        df = self._frame()
        df['_rid'] = range(len(df))
        s1 = compute_surface_staleness(df.copy(), content_col='内容', num_perm=64)
        df2 = df.iloc[[3, 1, 0, 2]].reset_index(drop=True)  # 重排
        s2 = compute_surface_staleness(df2.copy(), content_col='内容', num_perm=64)
        m1 = dict(zip(df['_rid'], s1))
        m2 = dict(zip(df2['_rid'], s2))
        for rid in m1:
            a, b = m1[rid], m2[rid]
            assert (np.isnan(a) and np.isnan(b)) or abs(a - b) < 1e-9, (
                f"行ID {rid} 在不同输入序下 staleness 不一致: {a} vs {b}"
            )


class TestStaleAndNerYearSchemaContract:
    """P0-③/④: stage 18/19 输入无 'year' 列, 须由 '日期' 派生后才能 groupby."""

    def _thirteen_schema(self):
        # 镜像 13_news_with_ctx schema: '日期' 为 str, 无 'year' 列.
        return pd.DataFrame({
            'target_bank': ['工商银行', '工商银行', '建设银行'],
            '日期': ['2017-06-01', '2018-06-01', '2018-06-01'],
            '内容': ['a', 'b', 'c'],
        })

    def test_groupby_year_without_derivation_raises(self):
        # 文档化 bug: 不派生 year 直接 groupby → KeyError (修复前的崩溃).
        df = self._thirteen_schema()
        with pytest.raises(KeyError):
            df.groupby(['target_bank', 'year']).size()

    def test_year_derivation_enables_bank_year_groupby(self):
        # 文档化 fix: 从 '日期' 派生 year 后 groupby 成功 (修复后的行为).
        df = self._thirteen_schema()
        df['year'] = pd.to_datetime(df['日期'], errors='coerce').dt.year
        g = df.groupby(['target_bank', 'year']).size()
        assert len(g) == 3
        assert set(df['year']) == {2017, 2018}

    def test_staleness_aggregate_to_bank_year_with_year(self):
        from news_process.pipeline.text.article_staleness import (
            aggregate_to_bank_year,
        )
        df = self._thirteen_schema()
        df['year'] = pd.to_datetime(df['日期'], errors='coerce').dt.year
        df['surface_staleness_full'] = [0.1, 0.95, 0.5]
        panel = aggregate_to_bank_year(df)
        assert {'target_bank', 'year'} <= set(panel.columns)
        assert 'surface_staleness_full' in panel.columns
        # 工商银行: 2017 + 2018 两行; 建设银行: 2018 一行 → 3 bank-year
        assert len(panel) == 3
