"""tests/test_omni_fix_audit_family.py — omni 2026-06-11 g-audit-family 组修复回归锁.

锁定 g-audit-family 组中仍在仓的 finding 修复后行为 (全部用合成 DataFrame, 零盘上大数据 / 零外部 API):
  01 cross_media_alpha 重叠事件窗合并为 episode + n_articles 加权契约
  04 construct_orthogonality 观测/null 同 listwise 域 + 未用 Z 常量删除
  05 39e 与 39d 统一 LLM-valid mask + permutation null listwise 域 + 聚类披露
  08 cross_media_alpha 同名异构披露 (docstring 不再宣称 39f 列 = paper 10 main treatment)

注: 原 finding 02/03/06/07 (llm_contamination_test verdict |r| 口径 / straddle 年剔除 /
    Jeffreys BF 标签 / 39h outcome audit-local join) 随 stage 39h + stage 49 移除
    (2026-06-12, 无财务数据无法计算) 一并删除。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast


# ════════════════════════════════════════════════════════════════════════
# finding 01 — cross_media_alpha episode 合并 + 文章数加权
# ════════════════════════════════════════════════════════════════════════
class TestEpisodeMerge:
    def test_overlapping_peaks_merged_into_single_episode(self):
        from news_process.pipeline.audit.cross_media_alpha import (
            _merge_overlapping_events,
        )
        events = pd.DataFrame({
            'target_bank': ['A', 'A', 'A'],
            'event_date': pd.to_datetime(['2020-06-01', '2020-06-05', '2020-06-20']),
        })
        merged = _merge_overlapping_events(events, window_days=3)
        # 前两 peak gap=4d ≤ 2×3 → 窗口重叠合并; 第三 peak gap=15d → 独立 episode
        assert len(merged) == 2
        ep1 = merged.iloc[0]
        assert ep1['event_date'] == pd.Timestamp('2020-06-01')
        # 窗口并集 = [first_peak − 3d, last_peak + 3d]
        assert ep1['window_start'] == pd.Timestamp('2020-05-29')
        assert ep1['window_end'] == pd.Timestamp('2020-06-08')

    def test_transitive_chain_merged_to_one_episode(self):
        from news_process.pipeline.audit.cross_media_alpha import (
            _merge_overlapping_events,
        )
        # 相邻 gap 5d ≤ 6 但首尾 gap 10d > 6: 传递重叠仍须合并为 1 个 episode
        events = pd.DataFrame({
            'target_bank': ['A'] * 3,
            'event_date': pd.to_datetime(['2020-06-01', '2020-06-06', '2020-06-11']),
        })
        merged = _merge_overlapping_events(events, window_days=3)
        assert len(merged) == 1
        assert merged.iloc[0]['window_end'] == pd.Timestamp('2020-06-14')

    def test_no_cross_bank_merge(self):
        from news_process.pipeline.audit.cross_media_alpha import (
            _merge_overlapping_events,
        )
        events = pd.DataFrame({
            'target_bank': ['A', 'B'],
            'event_date': pd.to_datetime(['2020-06-01', '2020-06-02']),
        })
        merged = _merge_overlapping_events(events, window_days=3)
        assert len(merged) == 2

    def test_detect_bank_events_merges_adjacent_peaks(self):
        from news_process.pipeline.audit.cross_media_alpha import detect_bank_events
        # bank A: 10 个安静日 (每天 1 篇) + 相邻两个 peak 日 (各 5 篇)
        rows = [{'target_bank': 'A', '日期': d}
                for d in pd.date_range('2020-05-01', periods=10)]
        for d in ('2020-06-01', '2020-06-02'):
            rows += [{'target_bank': 'A', '日期': pd.Timestamp(d)}] * 5
        df = pd.DataFrame(rows)
        events = detect_bank_events(df)
        assert {'window_start', 'window_end'}.issubset(events.columns)
        # 两个相邻 peak 日 (gap 1d ≤ 6) 合并为单一 episode → n_events 不再高估
        assert len(events) == 1
        assert events.iloc[0]['window_end'] == pd.Timestamp('2020-06-05')

    def test_aggregates_honor_episode_union_window_and_count_articles(self):
        from news_process.pipeline.audit.cross_media_alpha import (
            compute_outlet_tone_aggregates,
        )
        # episode 并集窗口 [05-29, 06-08]: 06-07 的文章在 ±3d (of 06-01) 之外
        # 但在 episode 窗内 → 必须纳入且只计 1 次
        article_df = pd.DataFrame({
            'target_bank': ['A'] * 4,
            '媒体(中文)': ['M1', 'M2', 'M1', 'M2'],
            '日期': pd.to_datetime(['2020-06-01', '2020-06-01',
                                    '2020-06-07', '2020-06-07']),
            'tone': [0.5, -0.5, 0.3, -0.3],
        })
        events = pd.DataFrame({
            'target_bank': ['A'],
            'event_date': [pd.Timestamp('2020-06-01')],
            'window_start': [pd.Timestamp('2020-05-29')],
            'window_end': [pd.Timestamp('2020-06-08')],
        })
        out = compute_outlet_tone_aggregates(article_df, events, tone_col='tone')
        assert len(out) == 1
        v = next(iter(out.values()))
        assert v['n_articles'] == 4  # 全部 4 篇, 各计 1 次

    def test_aggregate_to_bank_year_weights_by_n_articles(self):
        from news_process.pipeline.audit.cross_media_alpha import (
            aggregate_to_bank_year,
        )
        em = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'event_date': [pd.Timestamp('2020-03-01'), pd.Timestamp('2020-09-01')],
            'n_outlets': [2, 2],
            'n_days': [1, 1],
            'n_articles': [1, 3],
            'variance': [0.0, 1.0],
            'alpha': [np.nan, np.nan],
        })
        panel = aggregate_to_bank_year(em, 'full')
        # 文章数加权契约 (module docstring): (0×1 + 1×3) / 4 = 0.75
        # 旧 n_outlets 加权会给 0.5 — 必须不再如此
        assert panel['cross_outlet_tone_variance_full'].iloc[0] == pytest.approx(0.75)
        assert panel['n_events_full'].iloc[0] == 2

    def test_aggregate_to_bank_year_fallback_n_outlets_when_legacy_frame(self):
        from news_process.pipeline.audit.cross_media_alpha import (
            aggregate_to_bank_year,
        )
        em = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'event_date': [pd.Timestamp('2020-03-01'), pd.Timestamp('2020-09-01')],
            'n_outlets': [1, 3],
            'n_days': [1, 1],
            'variance': [0.0, 1.0],
            'alpha': [np.nan, np.nan],
        })
        panel = aggregate_to_bank_year(em, 'full')  # 旧格式缺 n_articles → 回退
        assert panel['cross_outlet_tone_variance_full'].iloc[0] == pytest.approx(0.75)


# ════════════════════════════════════════════════════════════════════════
# finding 04 — 39c 观测/null 同 listwise 域 + Z 常量删除
# ════════════════════════════════════════════════════════════════════════
class TestOrthogonalityDomainMatch:
    def test_unused_z_constants_removed(self):
        import news_process.pipeline.audit.construct_orthogonality as co
        # 旧 Z_STRONG=1.96 / Z_MODERATE=2.58 从未被实现引用, 且与单侧 p95/p99
        # 分位口径 (≈1.645/2.326) 不符 → 已删除
        assert not hasattr(co, 'Z_STRONG')
        assert not hasattr(co, 'Z_MODERATE')

    def test_classify_uses_full_dims_listwise_null(self, tmp_path):
        """ctx 列大量缺失时: 6 列 listwise < 100 (旧实现 null 全 NaN → classify 全
        undefined), 而 DIMS_FULL 3 列 listwise 充足 → 新实现 classify 必须可定档."""
        from news_process.pipeline.audit.construct_orthogonality import run_stage
        rng = np.random.default_rng(11)
        n = 200
        df = pd.DataFrame({
            'innovation_substantiveness_full': rng.choice(['实质性', '象征性'], n),
            'innovation_locus_full': rng.choice(['底层技术', '应用场景'], n),
            'innovation_collab_mode_full': rng.choice(['自主研发', '外部协同'], n),
            'innovation_substantiveness_ctx': rng.choice(['实质性', '象征性'], n),
            'innovation_locus_ctx': rng.choice(['底层技术', '应用场景'], n),
            'innovation_collab_mode_ctx': rng.choice(['自主研发', '外部协同'], n),
        })
        # 6 列 listwise = 50 < 100; DIMS_FULL listwise = 200 ≥ 100
        df.loc[df.index[:150], 'innovation_substantiveness_ctx'] = None
        stage21 = tmp_path / 'stage21.parquet'
        df.to_parquet(stage21)
        summary = run_stage(
            stage_21_parquet=str(stage21), out_dir=str(tmp_path),
            bootstrap_n=10, n_permutations=20, seed=42,
        )
        classify = summary['classify_full_3x3']
        assert any(v != 'undefined' for v in classify.values()), (
            "classify 应基于 DIMS_FULL 自身 listwise 域的 null (旧实现对照 6 列域 "
            f"null 全 NaN → 全 undefined): {classify}")
        # 口径披露字段
        assert 'classify_threshold_scale' in summary
        assert 'one-sided' in summary['classify_threshold_scale']


# ════════════════════════════════════════════════════════════════════════
# finding 05 — 39e mask 统一 + permutation listwise 域
# ════════════════════════════════════════════════════════════════════════
class Test39eMaskAndListwiseNull:
    def test_mask_prefers_llm_valid_col(self):
        from news_process.pipeline.audit.lm_discriminant_validity import (
            MIN_N_ARTICLES,
            _apply_llm_valid_mask,
        )
        assert MIN_N_ARTICLES == 2  # 与 39d run_discriminant_validity 默认一致
        panel = pd.DataFrame({
            'n_articles_llm_valid': [0, 1, 2, 5],
            'n_articles': [9, 9, 9, 9],  # 若误用本列会保留全部 4 行
            'x': [1.0, 2.0, 3.0, 4.0],
        })
        masked = _apply_llm_valid_mask(panel)
        assert len(masked) == 2
        assert set(masked['n_articles_llm_valid']) == {2, 5}

    def test_mask_falls_back_to_n_articles(self):
        from news_process.pipeline.audit.lm_discriminant_validity import (
            _apply_llm_valid_mask,
        )
        panel = pd.DataFrame({'n_articles': [1, 2, 3], 'x': [1.0, 2.0, 3.0]})
        assert len(_apply_llm_valid_mask(panel)) == 2

    def test_mask_graceful_when_count_cols_absent(self):
        from news_process.pipeline.audit.lm_discriminant_validity import (
            _apply_llm_valid_mask,
        )
        panel = pd.DataFrame({'x': [1.0, 2.0, 3.0]})
        assert len(_apply_llm_valid_mask(panel)) == 3  # 不崩, 不过滤

    def test_permutation_null_on_listwise_domain_with_disclosure(self):
        from news_process.pipeline.audit.lm_discriminant_validity import (
            permutation_null,
        )
        rng = np.random.default_rng(0)
        n = 120
        cols = ['uncert_frac_full', 'litig_frac_full']
        panel = pd.DataFrame({cols[0]: rng.random(n), cols[1]: rng.random(n)})
        panel.loc[:19, cols[0]] = np.nan    # 行 0-19 缺 col0
        panel.loc[100:, cols[1]] = np.nan   # 行 100-119 缺 col1
        out = permutation_null(panel, cols, n_perm=30, seed=42)
        assert not out.empty
        # 观测与 null 同 listwise-complete 域 (行 20-99 = 80 行); 旧实现把 NaN
        # 一起洗牌, 破坏列间缺失对齐
        assert out['n_listwise'].iloc[0] == 80
        sub = panel[cols].dropna()
        expected_obs = float(sub.corr().abs().iloc[0, 1])
        assert out['obs_htmt_max'].iloc[0] == pytest.approx(expected_obs)
        # 面板聚类未处理 → note 必须披露
        assert '聚类' in out['note'].iloc[0]

    def test_permutation_null_skips_tiny_listwise(self):
        from news_process.pipeline.audit.lm_discriminant_validity import (
            permutation_null,
        )
        cols = ['uncert_frac_full', 'litig_frac_full']
        panel = pd.DataFrame({
            cols[0]: [0.1, np.nan, 0.3, np.nan],
            cols[1]: [np.nan, 0.2, np.nan, 0.4],
        })  # listwise = 0 行
        out = permutation_null(panel, cols, n_perm=5, seed=42)
        assert out.empty


# ════════════════════════════════════════════════════════════════════════
# finding 08 — 同名异构披露 (docstring 宣称修正)
# ════════════════════════════════════════════════════════════════════════
def test_cross_media_alpha_no_longer_claims_main_treatment():
    import news_process.pipeline.audit.cross_media_alpha as cma
    doc = cma.__doc__
    assert '同名异构' in doc, "模块 docstring 必须披露与 paper 10 spec 的同名异构"
    assert 'omni-g-audit-family-08' in doc
    # 旧宣称 "第 10 篇 main treatment = cross_outlet_tone_variance_full" 必须移除
    assert '第 10 篇 main treatment =' not in doc
    assert '不是**第 10 篇 spec 承诺的 main treatment' in doc
