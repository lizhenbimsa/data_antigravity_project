"""tests/test_omni_fix_audit_family.py — omni 2026-06-11 g-audit-family 组修复回归锁.

锁定 8 条 finding 的修复后行为 (全部用合成 DataFrame, 零盘上大数据 / 零外部 API):
  01 cross_media_alpha 重叠事件窗合并为 episode + n_articles 加权契约
  02 llm_contamination verdict |r| 口径 (负向关系下真污染不再误判 reverse_pattern)
  03 跨 cutoff 之年整年剔出留出集 + n_straddle_excluded 披露
  04 construct_orthogonality 观测/null 同 listwise 域 + 未用 Z 常量删除
  05 39e 与 39d 统一 LLM-valid mask + permutation null listwise 域 + 聚类披露
  06 Bayes factor 标签对齐 Jeffreys (1961) 原表档位
  07 39h outcome 列 audit-local join 自 stage 49 产物 (结构性死路打通)
  08 cross_media_alpha 同名异构披露 (docstring 不再宣称 39f 列 = paper 10 main treatment)
"""
from __future__ import annotations

import json

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
# finding 02 — verdict |r| 口径
# ════════════════════════════════════════════════════════════════════════
def _make_corr_panel(r_pre: float, r_post: float, n: int = 300,
                     seed: int = 123) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    pre_y = rng.standard_normal(n)
    pre_llm = r_pre * pre_y + np.sqrt(1 - r_pre ** 2) * rng.standard_normal(n)
    post_y = rng.standard_normal(n)
    post_llm = r_post * post_y + np.sqrt(1 - r_post ** 2) * rng.standard_normal(n)
    return pd.DataFrame({
        'date': (list(pd.date_range('2010-01-01', periods=n, freq='D'))
                 + list(pd.date_range('2025-01-01', periods=n, freq='D'))),
        'llm': list(pre_llm) + list(post_llm),
        'y': list(pre_y) + list(post_y),
    })


class TestVerdictAbsScale:
    def test_negative_relationship_contamination_detected(self):
        """负向 LLM-outcome 关系下真污染: 旧带符号比较 (r_pre < r_post) 误判
        reverse_pattern_anomaly; 新 |r| 口径正确判 contamination_detected."""
        from news_process.pipeline.audit.llm_contamination_test import (
            contamination_test,
        )
        df = _make_corr_panel(r_pre=-0.85, r_post=-0.05)
        report = contamination_test(
            df, llm_col='llm', outcome_col='y', date_col='date',
            cutoff_date='2024-01-01',  # test-frozen, NOT 来自 LLM provider
        )
        assert report['r_pre_cutoff'] < 0  # 关系确为负向
        assert report['verdict'] == 'contamination_detected'
        assert report['abs_r_pre_cutoff'] > report['abs_r_post_cutoff']

    def test_positive_contamination_still_detected(self):
        from news_process.pipeline.audit.llm_contamination_test import (
            contamination_test,
        )
        df = _make_corr_panel(r_pre=0.85, r_post=0.05)
        report = contamination_test(
            df, llm_col='llm', outcome_col='y', date_col='date',
            cutoff_date='2024-01-01',
        )
        assert report['verdict'] == 'contamination_detected'

    def test_report_carries_both_signed_and_abs_scales(self):
        from news_process.pipeline.audit.llm_contamination_test import (
            contamination_test,
        )
        df = _make_corr_panel(r_pre=0.4, r_post=0.4)
        report = contamination_test(
            df, llm_col='llm', outcome_col='y', date_col='date',
            cutoff_date='2024-01-01',
        )
        for key in ('r_pre_cutoff', 'r_post_cutoff', 'abs_r_pre_cutoff',
                    'abs_r_post_cutoff', 'fisher_z_stat', 'fisher_p_value',
                    'fisher_z_stat_abs', 'fisher_p_value_abs', 'verdict_scale'):
            assert key in report, f"report 缺字段 {key}"
        assert report['verdict'] != 'contamination_detected'


# ════════════════════════════════════════════════════════════════════════
# finding 03 — 跨 cutoff 之年整年剔出
# ════════════════════════════════════════════════════════════════════════
class TestStraddleYearExclusion:
    def test_straddle_year_excluded_with_disclosure(self):
        from news_process.pipeline.audit.llm_contamination_test import (
            year_to_test_dates_excluding_straddle,
        )
        df = pd.DataFrame({'year': [2023] * 5 + [2024] * 5 + [2025] * 5,
                           'x': range(15)})
        kept, n_excl, yrs = year_to_test_dates_excluding_straddle(df, '2024-04-01')
        # 2024 跨界 (1-3 月 pre / 4-12 月 post) → 整年剔出, 不得划入 post 留出集
        assert n_excl == 5
        assert yrs == [2024]
        assert set(kept['year']) == {2023, 2025}
        assert '_test_date' in kept.columns
        assert (kept.loc[kept['year'] == 2025, '_test_date']
                == pd.Timestamp('2025-07-01')).all()

    def test_jan1_cutoff_year_is_pure_post_not_straddle(self):
        from news_process.pipeline.audit.llm_contamination_test import (
            year_to_test_dates_excluding_straddle,
        )
        df = pd.DataFrame({'year': [2023, 2024, 2025]})
        kept, n_excl, yrs = year_to_test_dates_excluding_straddle(df, '2024-01-01')
        # cutoff 恰为 1 月 1 日 → 2024 整年 ≥ cutoff (纯 post), 无跨界剔除
        assert n_excl == 0
        assert yrs == []
        assert len(kept) == 3


# ════════════════════════════════════════════════════════════════════════
# finding 07 (+ 03 E2E) — 39h run_stage: stage 49 audit-local join
# ════════════════════════════════════════════════════════════════════════
class TestRunStage39hWiring:
    @staticmethod
    def _cfg(tmp_path, cutoff='2024-04-01'):
        return {
            'paths': {'output_dir': str(tmp_path)},
            'filenames': {},
            'llm_contamination_test': {
                'cutoff': cutoff,
                'llm_col': 'llm_vote_tone_full',
                'outcome_col': 'z_score',
                'date_col': 'year',
                'method': 'pearson',
                'report': str(tmp_path / 'llm_contamination_report.json'),
            },
        }

    @staticmethod
    def _write_inputs(tmp_path, with_outcome_file=True):
        rng = np.random.default_rng(42)
        banks = [f'B{i:02d}' for i in range(30)]
        years = list(range(2018, 2026))  # 2018-2025
        panel = pd.DataFrame(
            [{'target_bank': b, 'year': y} for b in banks for y in years])
        panel['llm_vote_tone_full'] = rng.standard_normal(len(panel))
        # 面板刻意不含 z_score (runner 8c: stage 49 DV master 不并入 40_panel)
        panel.to_parquet(tmp_path / '40_panel_yearly.parquet')
        if with_outcome_file:
            odf = panel[['target_bank', 'year']].copy()
            odf['z_score'] = (0.5 * panel['llm_vote_tone_full'].to_numpy()
                              + rng.standard_normal(len(panel)))
            odf.to_parquet(tmp_path / '49_risk_taking_outcomes.parquet')

    def test_outcome_joined_from_49_and_report_written(self, tmp_path):
        """旧接线结构性死路: 面板无 z_score → 永远 skip. 新接线: 自动 join 49 产物."""
        from news_process.pipeline.audit.llm_contamination_test import run_stage
        self._write_inputs(tmp_path)
        rc = run_stage(self._cfg(tmp_path))
        assert rc == 0
        report_path = tmp_path / 'llm_contamination_report.json'
        assert report_path.exists(), "39h 应产出 report (不再结构性 skip)"
        report = json.loads(report_path.read_text(encoding='utf-8'))
        # straddle 披露 (finding 03): 2024 跨 2024-04-01 → 30 行整年剔出
        assert report['n_straddle_excluded'] == 30
        assert report['straddle_years'] == [2024]
        # pre = 2018-2023 (6×30); post = 2025 纯 post 年 (1×30)
        assert report['n_pre_cutoff'] == 180
        assert report['n_post_cutoff'] == 30
        assert report['verdict'] in (
            'contamination_detected', 'no_contamination_evidence',
            'reverse_pattern_anomaly', 'inconclusive')

    def test_graceful_skip_when_49_output_missing(self, tmp_path):
        from news_process.pipeline.audit.llm_contamination_test import run_stage
        self._write_inputs(tmp_path, with_outcome_file=False)
        rc = run_stage(self._cfg(tmp_path))
        assert rc == 0
        assert not (tmp_path / 'llm_contamination_report.json').exists()

    def test_graceful_skip_when_cutoff_unset(self, tmp_path):
        from news_process.pipeline.audit.llm_contamination_test import run_stage
        self._write_inputs(tmp_path)
        rc = run_stage(self._cfg(tmp_path, cutoff=None))
        assert rc == 0
        assert not (tmp_path / 'llm_contamination_report.json').exists()


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
# finding 06 — Jeffreys (1961) BF 标签档位
# ════════════════════════════════════════════════════════════════════════
class TestJeffreysBayesLabels:
    @staticmethod
    def _label_for(bf01: float) -> str:
        from news_process.pipeline.audit.llm_contamination_test import (
            BAYES_FACTOR_LABELS,
        )
        for threshold, label in BAYES_FACTOR_LABELS:
            if bf01 <= threshold:
                return label
        return 'UNREACHED'

    def test_ladder_cutpoints_match_jeffreys(self):
        from news_process.pipeline.audit.llm_contamination_test import (
            BAYES_FACTOR_LABELS,
        )
        thresholds = [t for t, _ in BAYES_FACTOR_LABELS]
        finite = thresholds[:-1]
        assert finite == pytest.approx(
            [0.01, 10 ** -1.5, 0.10, 10 ** -0.5, 1.0, 10 ** 0.5,
             10.0, 10 ** 1.5, 100.0])
        assert thresholds[-1] == float('inf')

    def test_decisive_requires_bf10_over_100(self):
        # 旧表: bf_01 ≤ 0.10 (BF_10 ≥ 10) 即标 decisive — Jeffreys 要求 BF_10 > 100
        assert self._label_for(0.005) == 'decisive evidence FOR contamination'
        assert self._label_for(0.05) == 'strong evidence FOR contamination'
        assert self._label_for(0.2) == 'substantial evidence FOR contamination'

    def test_against_side_no_longer_inflated(self):
        # 旧表: (1, 3] 标 moderate / (3, 10] 标 strong — Jeffreys: barely / substantial
        assert self._label_for(2.0).startswith('barely worth mentioning')
        assert self._label_for(5.0) == 'substantial evidence AGAINST contamination'
        assert self._label_for(50.0) == 'very strong evidence AGAINST contamination'
        assert self._label_for(500.0) == 'decisive evidence AGAINST contamination'

    def test_classify_bayes_factor_strong_evidence_path(self):
        from news_process.pipeline.audit.llm_contamination_test import (
            classify_bayes_factor,
        )
        bf, label = classify_bayes_factor(1e-8, 200, 200)
        assert bf < 0.01
        assert label == 'decisive evidence FOR contamination'


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
