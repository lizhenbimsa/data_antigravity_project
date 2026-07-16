"""omni-g-encode 组 10 项缺陷修复回归锁 (fix/omni-2026-06-11).

覆盖 scripts/audit/_omni_fix/g-encode.json 的全部条目 (合成数据, 零盘上依赖, $0):

- g-encode-01/03/09: balance_panel 零填契约补漏 (n_articles* 前缀全族 +
  sum_herd_weight_full/_ctx + coverage_active_days 在零新闻行填 0 而非 NaN)
- g-encode-02: avg_llm_conf / avg_{model}_conf / avg_agreement_rate 聚合域
  对齐 valid-vote (与被调节的 llm_vote_tone 同口径)
- g-encode-04: coverage_continuity 分母改当年自然天数 (365/366), 单日爆发
  不再得 1.0 满分
- g-encode-05: ctx 对角线聚合 (_lc/_sc/_cm) 源列存在性守卫 (stage 21 部分
  产出时优雅跳过而非 KeyError)
- g-encode-06: ctx_is_fallback object→bool 显式缺失策略 (缺失=非 fallback)
- g-encode-07: locus/substantiveness 恒等式校验统一为 R6 `>=` 语义
- g-encode-08: 聚合出口计数/和列 dtype pin Int64 (消除值依赖 schema 漂移)
- g-encode-10: avg_category_confidence 死列复活 (改接 v3.2.0 双轨源)

锁旧行为断言更新说明: 本文件为新增, 不改既有测试; 既有测试无锁旧分母/旧零填/
旧 `==` 恒等式的断言 (核对 test_40_panel_export_main / test_audit_fixes_20260529 /
test_metric_audit_p0_fixes), 无需迁移。

# 白话: 面板聚合(把一篇篇文章汇总成"银行×年份"一行)有十个修过的坑:
# 某银行某年零新闻时, "篇数"类该填 0、"情感/比例"类该留空(NaN), 不能混;
# 算平均置信度只看有效投票的文章; 报道连续性的分母用全年 365/366 天, 不能
# "只报道一天就得满分"; 源数据少列时优雅跳过而不是崩溃; 计数列固定整数类型,
# 防止换数据规模后 Stata 文件格式漂移。
"""

from unittest import mock

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.panel import encode
from news_process.pipeline.panel.encode import (
    LLM_MODELS,
    _aggregate_ctx_diagonal,
    _check_partition_identity,
    aggregate_panel,
    balance_panel,
    build_aggregation_dict,
    encode_sentiment,
)


@pytest.fixture(autouse=True)
def _isolate_cwd_relative_writes(tmp_path, monkeypatch):
    """与 test_40_panel_export_main 同款隔离: aggregate_panel →
    encode_collab.apply_v3_5_1 写 sidecar JSON。

    fix(M1, 2026-07-14): writer 已切 config 绝对路径 (manifest._resolve_sidecar_path
    同源), 旧 chdir 隔离失效 → 改设 env ``LLM_ARCHIVE_SIDECAR_PATH`` 重定向到
    tmp (该 env 在解析链最高优先级), 防测试直写生产冻结锚; chdir 保留兜其他
    cwd 相对副作用。"""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('LLM_ARCHIVE_SIDECAR_PATH',
                       str(tmp_path / 'v3_5_1_constants.json'))


# ============================================================================
# g-encode-01 / 03 / 09: balance_panel 零填契约补漏
# ============================================================================

class TestBalancePanelZeroFillContract:
    """零新闻 bank-year 行: 计数/和列填 0, 比例/情感列保持 NaN."""

    @pytest.fixture
    def unbalanced_panel(self):
        # A 有 2017+2018, B 仅 2018 → balance 后插入 B-2017 零新闻行
        return pd.DataFrame({
            'target_bank': ['A', 'A', 'B'],
            'year': [2017, 2018, 2018],
            # --- 此前漏填的计数/和族 (修复对象) ---
            'n_articles': pd.array([3, 2, 4], dtype='Int64'),
            'n_articles_llm_valid': pd.array([3, 2, 4], dtype='Int64'),
            'n_articles_llm_valid_ctx': pd.array([2, 2, 3], dtype='Int64'),
            'n_articles_tech_lc_ctx': [1, 1, 2],
            'n_articles_sub_sc_ctx': [1, 0, 1],
            'n_articles_indep_cm_ctx': [0, 1, 1],
            'n_articles_for_ctx_independence': np.array([2, 1, 3], dtype='int32'),
            'n_articles_cell_1_full': [1.0, 0.0, 2.0],
            'n_articles_subst_disagree': [0.0, 1.0, 1.0],
            'sum_herd_weight_full': [2.5, 1.5, 3.0],
            'sum_herd_weight_ctx': [2.0, 1.0, 2.5],
            'coverage_active_days': [3.0, 2.0, 4.0],
            # --- 既有契约对照组 (回归保护: F4/F5/vwmwhw-F1 行为不回退) ---
            'pos_count_full': pd.array([2, 1, 3], dtype='Int64'),
            'sum_wd_vw_llm_full': [1.2, 0.8, 2.0],
            'sum_mention_density': [5.0, 3.0, 7.0],
            # --- 比例/均值/情感: 必须保持 NaN ---
            'coverage_continuity': [3 / 365, 2 / 365, 4 / 365],
            'llm_vote_tone_full': [0.5, 0.1, -0.2],
            'avg_word_count_full': [120.0, 80.0, 95.0],
            'tech_frac': [0.33, 0.5, 0.5],
        })

    def test_inserted_row_count_sum_cols_zero(self, unbalanced_panel):
        balanced = balance_panel(unbalanced_panel)
        assert len(balanced) == 4
        row = balanced[(balanced['target_bank'] == 'B')
                       & (balanced['year'] == 2017)].iloc[0]
        zero_cols = [
            'n_articles', 'n_articles_llm_valid', 'n_articles_llm_valid_ctx',
            'n_articles_tech_lc_ctx', 'n_articles_sub_sc_ctx',
            'n_articles_indep_cm_ctx', 'n_articles_for_ctx_independence',
            'n_articles_cell_1_full', 'n_articles_subst_disagree',
            'sum_herd_weight_full', 'sum_herd_weight_ctx',
            'coverage_active_days',
            'pos_count_full', 'sum_wd_vw_llm_full', 'sum_mention_density',
        ]
        for col in zero_cols:
            assert row[col] == 0, f"{col} 零新闻行应为 0, 实际 {row[col]!r}"
            assert not pd.isna(row[col]), f"{col} 零新闻行残留 NA"

    def test_inserted_row_ratio_and_tone_stay_nan(self, unbalanced_panel):
        balanced = balance_panel(unbalanced_panel)
        row = balanced[(balanced['target_bank'] == 'B')
                       & (balanced['year'] == 2017)].iloc[0]
        for col in ('coverage_continuity', 'llm_vote_tone_full',
                    'avg_word_count_full', 'tech_frac'):
            assert pd.isna(row[col]), f"{col} 应保持 NaN (比例/均值/情感类)"

    def test_n_articles_family_integer_dtype_restored(self, unbalanced_panel):
        """reindex 把 numpy int 漂成 float64; 填 0 后须恢复整型
        (nullable Int 经 fillna 原样保持)."""
        balanced = balance_panel(unbalanced_panel)
        for col in balanced.columns:
            if col.startswith('n_articles'):
                assert pd.api.types.is_integer_dtype(balanced[col]), \
                    f"{col} 应为整型, 实际 {balanced[col].dtype}"

    def test_existing_rows_unchanged(self, unbalanced_panel):
        """已有观测的值不被零填触碰 (只动笛卡尔积新建行)."""
        balanced = balance_panel(unbalanced_panel)
        a17 = balanced[(balanced['target_bank'] == 'A')
                       & (balanced['year'] == 2017)].iloc[0]
        assert a17['n_articles_llm_valid'] == 3
        assert a17['sum_herd_weight_full'] == pytest.approx(2.5)
        assert a17['coverage_continuity'] == pytest.approx(3 / 365)


# ============================================================================
# g-encode-02: avg_llm_conf / 逐模型 conf / agreement_rate 聚合域 = valid-vote
# ============================================================================

def _article_df_with_one_invalid():
    """3 篇文章 (bank A, 2017): idx1 验证失败 (低置信度 0.5), 其余有效."""
    df = pd.DataFrame({
        'target_bank': ['A', 'A', 'A'],
        'year': [2017, 2017, 2017],
        'llm_sentiment_full': ['正面', '负面', '中性'],
        'llm_verified_full': [True, False, True],
        'llm_agreement_rate_full': [1.0, 1.0, 2 / 3],
    })
    for short in LLM_MODELS:
        df[f'{short}_sentiment_full'] = ['正面', '负面', '中性']
        df[f'{short}_sentiment_confidence_full'] = [0.9, 0.5, 0.8]
        df[f'{short}_verified_full'] = [True, False, True]
    return df


class TestAvgLlmConfValidDomain:
    def test_invalid_article_conf_masked_out(self):
        df = encode_sentiment(_article_df_with_one_invalid())
        # idx1 无效票 → avg_llm_conf_full 不计入 (NaN), 有效票保留宏平均
        assert pd.isna(df['avg_llm_conf_full'].iloc[1]), \
            "无效票文章的置信度应被掩码 (旧物理域口径回归)"
        assert df['avg_llm_conf_full'].iloc[0] == pytest.approx(0.9)
        assert df['avg_llm_conf_full'].iloc[2] == pytest.approx(0.8)

    def test_per_model_masked_helper_cols(self):
        df = encode_sentiment(_article_df_with_one_invalid())
        for short in LLM_MODELS:
            col = f'_conf_valid_{short}_full'
            assert col in df.columns
            assert pd.isna(df[col].iloc[1]), f"{col} 应在无效票行为 NaN"
            assert df[col].iloc[0] == pytest.approx(0.9)

    def test_agreement_rate_masked_helper_col(self):
        df = encode_sentiment(_article_df_with_one_invalid())
        assert '_agree_valid_full' in df.columns
        assert pd.isna(df['_agree_valid_full'].iloc[1])
        assert df['_agree_valid_full'].iloc[0] == pytest.approx(1.0)
        assert df['_agree_valid_full'].iloc[2] == pytest.approx(2 / 3)

    def test_agg_dict_prefers_masked_sources(self):
        df = encode_sentiment(_article_df_with_one_invalid())
        agg = build_aggregation_dict(df)
        for short in LLM_MODELS:
            assert agg[f'avg_{short}_conf_full'] == \
                (f'_conf_valid_{short}_full', 'mean')
        assert agg['avg_agreement_rate_full'] == ('_agree_valid_full', 'mean')

    def test_agg_dict_falls_back_to_raw_cols(self):
        """掩码列缺失 (legacy parquet / df=None) → 回退物理域源列, 向后兼容."""
        raw = pd.DataFrame({
            f'{LLM_MODELS[0]}_sentiment_confidence_full': [0.9],
            'llm_agreement_rate_full': [1.0],
        })
        agg_raw = build_aggregation_dict(raw)
        assert agg_raw[f'avg_{LLM_MODELS[0]}_conf_full'] == \
            (f'{LLM_MODELS[0]}_sentiment_confidence_full', 'mean')
        assert agg_raw['avg_agreement_rate_full'] == \
            ('llm_agreement_rate_full', 'mean')
        agg_none = build_aggregation_dict(None)
        assert agg_none['avg_agreement_rate_full'] == \
            ('llm_agreement_rate_full', 'mean')

    def test_panel_level_mean_excludes_invalid(self):
        """端到端: bank-year avg_llm_conf_full = 有效票文章均值
        (旧物理域口径 = (0.9+0.5+0.8)/3 ≈ 0.7333, 修复后 = 0.85)."""
        df = encode_sentiment(_article_df_with_one_invalid())
        panel = aggregate_panel(df)
        assert panel['avg_llm_conf_full'].iloc[0] == pytest.approx(0.85)
        assert panel['avg_agreement_rate_full'].iloc[0] == \
            pytest.approx((1.0 + 2 / 3) / 2)
        for short in LLM_MODELS:
            assert panel[f'avg_{short}_conf_full'].iloc[0] == \
                pytest.approx(0.85)


# ============================================================================
# g-encode-04: coverage_continuity 分母 = 当年自然天数 (365/366)
# ============================================================================

class TestCoverageContinuityCalendarDenominator:
    def test_single_day_burst_not_max(self):
        """单日单篇 (旧 span 分母 → 1/1 = 1.0 满分) → 1/365."""
        df = pd.DataFrame({
            'target_bank': ['A'],
            'year': [2017],
            '日期': ['2017-05-01'],
            'llm_vote_score_full': pd.array([1], dtype='Int8'),
        })
        panel = aggregate_panel(df)
        assert panel['coverage_active_days'].iloc[0] == 1.0
        assert panel['coverage_continuity'].iloc[0] == pytest.approx(1 / 365)

    def test_leap_year_denominator_366(self):
        df = pd.DataFrame({
            'target_bank': ['B', 'B'],
            'year': [2020, 2020],
            '日期': ['2020-01-01', '2020-12-31'],
            'llm_vote_score_full': pd.array([1, 0], dtype='Int8'),
        })
        panel = aggregate_panel(df)
        assert panel['coverage_active_days'].iloc[0] == 2.0
        assert panel['coverage_continuity'].iloc[0] == pytest.approx(2 / 366)

    def test_same_day_articles_count_one_active_day(self):
        """同日多篇只算 1 个活跃日 (nunique 语义不变)."""
        df = pd.DataFrame({
            'target_bank': ['A'] * 3,
            'year': [2017] * 3,
            '日期': ['2017-03-05', '2017-03-05', '2017-09-01'],
            'llm_vote_score_full': pd.array([1, 0, -1], dtype='Int8'),
        })
        panel = aggregate_panel(df)
        assert panel['coverage_active_days'].iloc[0] == 2.0
        assert panel['coverage_continuity'].iloc[0] == pytest.approx(2 / 365)

    def test_no_date_column_graceful_nan(self):
        df = pd.DataFrame({
            'target_bank': ['A'],
            'year': [2017],
            'llm_vote_score_full': pd.array([1], dtype='Int8'),
        })
        panel = aggregate_panel(df)
        assert pd.isna(panel['coverage_active_days'].iloc[0])
        assert pd.isna(panel['coverage_continuity'].iloc[0])


# ============================================================================
# g-encode-05: ctx 对角线聚合源列存在性守卫
# ============================================================================

def _locus_ctx_df(include_ctx_vote=True, include_prob=False):
    df = pd.DataFrame({
        'target_bank': ['A'] * 4,
        'year': [2017] * 4,
        'llm_vote_score_full': pd.array([1, 0, -1, 1], dtype='Int8'),
        'innovation_locus_full': ['底层技术', '应用场景', '底层技术', '应用场景'],
        'innovation_locus_ctx': ['底层技术', '应用场景', '底层技术', np.nan],
    })
    if include_ctx_vote:
        df['llm_vote_score_ctx'] = pd.array([1, 0, -1, pd.NA], dtype='Int8')
    if include_prob:
        df['llm_prob_score_ctx'] = [0.8, 0.2, 0.6, 0.4]
    return df


class TestCtxDiagonalSourceGuards:
    def test_missing_prob_score_no_keyerror(self):
        """llm_prob_score_ctx 缺失 (stage 21 logit 探针关闭) → 优雅跳过,
        旧版 groupby.agg 硬编码该源列直接 KeyError."""
        panel = aggregate_panel(_locus_ctx_df(include_prob=False))
        assert panel['n_articles_tech_lc_ctx'].iloc[0] == 2
        assert panel['n_articles_app_lc_ctx'].iloc[0] == 1
        assert panel['llm_vote_tone_tech_lc_ctx'].iloc[0] == pytest.approx(0.0)
        # prob 输出列以 NaN 占位 (schema 稳定)
        assert 'llm_prob_score_tech_lc_ctx' in panel.columns
        assert panel['llm_prob_score_tech_lc_ctx'].isna().all()

    def test_missing_ctx_vote_no_keyerror_frac_nan(self):
        """llm_vote_score_ctx 整列缺失 → n_articles_llm_valid_ctx 不产出,
        frac 分母守卫置 NaN 而非 KeyError."""
        panel = aggregate_panel(_locus_ctx_df(include_ctx_vote=False))
        assert 'n_articles_llm_valid_ctx' not in panel.columns
        assert panel['tech_frac_lc'].isna().all()
        assert panel['app_frac_lc'].isna().all()
        # count 占位 0 (与既有 empty-category 分支同语义)
        assert (panel['n_articles_tech_lc_ctx'] == 0).all()

    def test_full_sources_values_unchanged(self):
        """双源齐备时输出与旧实现等价 (count/mean/prob-mean + ctx 分母 frac)."""
        panel = aggregate_panel(_locus_ctx_df(include_prob=True))
        assert panel['n_articles_llm_valid_ctx'].iloc[0] == 3
        assert panel['tech_frac_lc'].iloc[0] == pytest.approx(2 / 3)
        assert panel['app_frac_lc'].iloc[0] == pytest.approx(1 / 3)
        assert panel['llm_prob_score_tech_lc_ctx'].iloc[0] == \
            pytest.approx((0.8 + 0.6) / 2)

    def test_helper_direct_sc_mapping_missing_both_sources(self):
        """helper 直测 (_sc 维度): vote/prob 双缺 → 全部占位列, 不崩溃."""
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2017],
            'innovation_substantiveness_ctx': ['实质性', '象征性'],
        })
        panel = pd.DataFrame({'target_bank': ['A'], 'year': [2017]})
        out = _aggregate_ctx_diagonal(
            df, panel, 'innovation_substantiveness_ctx',
            [('实质性', '_sub_sc_ctx'), ('象征性', '_symb_sc_ctx')])
        for suffix in ('_sub_sc_ctx', '_symb_sc_ctx'):
            assert out[f'n_articles{suffix}'].iloc[0] == 0
            assert pd.isna(out[f'llm_vote_tone{suffix}'].iloc[0])
            assert pd.isna(out[f'llm_prob_score{suffix}'].iloc[0])


# ============================================================================
# g-encode-06: ctx_is_fallback 缺失策略 (缺失=非 fallback, 显式 fillna)
# ============================================================================

class TestCtxFallbackMissingPolicy:
    def test_nan_and_none_both_treated_as_not_fallback(self):
        """旧裸 astype('bool'): np.nan→True / None→False (同种缺失结果相反);
        修复后统一 fillna(False): frac=1/4, independence=4-1=3."""
        df = pd.DataFrame({
            'target_bank': ['A'] * 4,
            'year': [2017] * 4,
            'llm_vote_score_full': pd.array([1, 0, 1, 0], dtype='Int8'),
            'ctx_is_fallback': pd.Series([True, False, np.nan, None],
                                         dtype=object),
        })
        panel = aggregate_panel(df)
        assert panel['frac_ctx_fallback'].iloc[0] == pytest.approx(0.25)
        assert panel['n_articles_for_ctx_independence'].iloc[0] == 3

    def test_missing_count_warning_logged(self):
        df = pd.DataFrame({
            'target_bank': ['A'] * 3,
            'year': [2017] * 3,
            'llm_vote_score_full': pd.array([1, 0, 1], dtype='Int8'),
            'ctx_is_fallback': pd.Series([True, np.nan, None], dtype=object),
        })
        with mock.patch.object(encode, 'logger') as mock_logger:
            aggregate_panel(df)
        warned = [str(c.args[0]) for c in mock_logger.warning.call_args_list]
        assert any('ctx_is_fallback' in w and '2' in w for w in warned), \
            "缺失值填 False 须 logger.warning 报缺失数"

    def test_pure_bool_column_untouched(self):
        """物理 bool 列 (盘上常态) 不走防御分支, 行为不变."""
        df = pd.DataFrame({
            'target_bank': ['A'] * 2,
            'year': [2017] * 2,
            'llm_vote_score_full': pd.array([1, 0], dtype='Int8'),
            'ctx_is_fallback': pd.Series([True, False], dtype=bool),
        })
        panel = aggregate_panel(df)
        assert panel['frac_ctx_fallback'].iloc[0] == pytest.approx(0.5)
        assert panel['n_articles_for_ctx_independence'].iloc[0] == 1


# ============================================================================
# g-encode-07: 恒等式校验三维度统一 R6 (>=) 语义
# ============================================================================

class TestPartitionIdentityR6:
    def test_partial_failure_passes_with_gap(self):
        """valid >= Σ 分类 (差额 = 分类 NaN 文章数) → 通过, 不再伪告警."""
        panel = pd.DataFrame({
            'n_articles_llm_valid': pd.array([5, 3], dtype='Int64'),
            'n_a': [3, 0],
            'n_b': [1, 3],
        })
        n_fail, gap = _check_partition_identity(
            panel, 'n_articles_llm_valid', ['n_a', 'n_b'], 'dim_x')
        assert n_fail == 0
        assert gap == 1

    def test_true_violation_still_warns(self):
        """valid < Σ 分类 = 真 bug (上游 race condition) → 仍告警."""
        panel = pd.DataFrame({
            'n_articles_llm_valid': pd.array([2], dtype='Int64'),
            'n_a': [2],
            'n_b': [1],
        })
        with mock.patch.object(encode, 'logger') as mock_logger:
            n_fail, gap = _check_partition_identity(
                panel, 'n_articles_llm_valid', ['n_a', 'n_b'], 'dim_x')
        assert n_fail == 1
        assert gap == -1
        assert mock_logger.warning.called

    def test_locus_nan_label_no_spurious_warning(self):
        """端到端: locus 标签部分 NaN (全量语料常态) → 不触发 ✗ WARNING
        (旧严格 == 在此必然伪告警, 与 collab 维度行为矛盾)."""
        df = pd.DataFrame({
            'target_bank': ['A'] * 3,
            'year': [2017] * 3,
            'llm_vote_score_full': pd.array([1, 0, -1], dtype='Int8'),
            'innovation_locus_full': ['底层技术', '应用场景', np.nan],
        })
        with mock.patch.object(encode, 'logger') as mock_logger:
            panel = aggregate_panel(df)
        warned = [str(c.args[0]) for c in mock_logger.warning.call_args_list]
        assert not any('恒等式校验失败' in w for w in warned), \
            f"分类部分失败不应伪告警: {warned}"
        assert panel['n_articles_llm_valid'].iloc[0] == 3
        assert panel['n_articles_tech'].iloc[0] == 1
        assert panel['n_articles_app'].iloc[0] == 1

    def test_substantiveness_nan_label_no_spurious_warning(self):
        """substantiveness 维度同语义 (R6 同步)."""
        df = pd.DataFrame({
            'target_bank': ['A'] * 3,
            'year': [2017] * 3,
            'llm_vote_score_full': pd.array([1, 0, -1], dtype='Int8'),
            'innovation_substantiveness_full': ['实质性', '象征性', np.nan],
        })
        with mock.patch.object(encode, 'logger') as mock_logger:
            aggregate_panel(df)
        warned = [str(c.args[0]) for c in mock_logger.warning.call_args_list]
        assert not any('恒等式校验失败' in w for w in warned)


# ============================================================================
# g-encode-08: 聚合出口计数/和列 dtype pin Int64
# ============================================================================

class TestAggOutputDtypePin:
    def test_small_sums_pinned_to_int64(self):
        """组和 ∈[-128,127] 时 pandas 保留 Int8 → 出口统一 pin Int64,
        消除 T=2 (byte) vs T=19 (long) 的 .dta 存储型漂移."""
        df = pd.DataFrame({
            'target_bank': ['A', 'A', 'B'],
            'year': [2017] * 3,
            'llm_vote_score_full': pd.array([1, 0, 1], dtype='Int8'),
            'is_positive_full': pd.array([1, 0, 1], dtype='Int8'),
            'is_negative_full': pd.array([0, 0, 0], dtype='Int8'),
        })
        panel = aggregate_panel(df)
        for col in ('pos_count_full', 'neg_count_full'):
            if col in panel.columns:
                assert str(panel[col].dtype) == 'Int64', \
                    f"{col} 应 pin 为 Int64, 实际 {panel[col].dtype}"
        # count 类本就是 Int64 (groupby.count), 保持不变
        assert str(panel['n_articles_llm_valid'].dtype) == 'Int64'

    def test_values_lossless_after_pin(self):
        df = pd.DataFrame({
            'target_bank': ['A'] * 3,
            'year': [2017] * 3,
            'llm_vote_score_full': pd.array([1, 1, -1], dtype='Int8'),
            'is_positive_full': pd.array([1, 1, 0], dtype='Int8'),
        })
        panel = aggregate_panel(df)
        assert panel['pos_count_full'].iloc[0] == 2
        if 'llm_vote_tone_sum_full' in panel.columns:
            assert panel['llm_vote_tone_sum_full'].iloc[0] == 1


# ============================================================================
# g-encode-10: avg_category_confidence 死列复活 (v3.2.0 双轨源)
# ============================================================================

class TestAvgCategoryConfidenceRevival:
    def test_dual_track_source_produces_values(self):
        """v3.2.0 列名 category_confidence_<track> → 三列全有值
        (旧裸名检查恒假 → 永久全 NaN 死列)."""
        df = pd.DataFrame({
            'target_bank': ['A', 'A', 'B'],
            'year': [2017] * 3,
            'llm_vote_score_full': pd.array([1, 0, 1], dtype='Int8'),
            'innovation_locus_full': ['底层技术', '应用场景', '底层技术'],
            'category_confidence_full': [0.8, 0.6, 0.9],
            'category_confidence_ctx': [0.7, 0.5, 0.3],
        })
        panel = aggregate_panel(df).set_index('target_bank')
        assert panel.loc['A', 'avg_category_confidence_full'] == \
            pytest.approx(0.7)
        assert panel.loc['A', 'avg_category_confidence_ctx'] == \
            pytest.approx(0.6)
        assert panel.loc['B', 'avg_category_confidence_full'] == \
            pytest.approx(0.9)
        # 裸名 = _full 别名 (export.py / codebook 既有消费者继续工作)
        assert panel.loc['A', 'avg_category_confidence'] == \
            pytest.approx(panel.loc['A', 'avg_category_confidence_full'])

    def test_legacy_bare_name_still_supported(self):
        """v3.1.x 裸名 parquet 兼容路径."""
        df = pd.DataFrame({
            'target_bank': ['A', 'A'],
            'year': [2017, 2017],
            'llm_vote_score_full': pd.array([1, 0], dtype='Int8'),
            'innovation_locus_full': ['底层技术', '应用场景'],
            'category_confidence': [0.4, 0.6],
        })
        panel = aggregate_panel(df)
        assert panel['avg_category_confidence'].iloc[0] == pytest.approx(0.5)
        # 双轨源缺失 → 轨道列 NaN 占位 (schema 稳定)
        assert panel['avg_category_confidence_full'].isna().all()
        assert panel['avg_category_confidence_ctx'].isna().all()

    def test_no_source_all_nan(self):
        df = pd.DataFrame({
            'target_bank': ['A'],
            'year': [2017],
            'llm_vote_score_full': pd.array([1], dtype='Int8'),
            'innovation_locus_full': ['底层技术'],
        })
        panel = aggregate_panel(df)
        assert panel['avg_category_confidence'].isna().all()
        assert panel['avg_category_confidence_full'].isna().all()
        assert panel['avg_category_confidence_ctx'].isna().all()


# ============================================================================
# F3 (2026-07-16): avg_llm_conf 宏平均 per-model 有效票掩码
# (FATAL_DEFECT_REMEDIATION_EXECUTION_PLAN §2-F3; D5 口径 — 缺席与在场判伪/缺标
#  模型格均不入分子分母, 与 _conf_valid_* 掩码列同源同式)
# ============================================================================

def _article_df_permodel(specs):
    """specs: 逐模型 (conf, verified, sentiment) 三元组; 单篇文章 (bank A, 2017)."""
    df = pd.DataFrame({
        'target_bank': ['A'], 'year': [2017],
        'llm_sentiment_full': ['正面'],
        'llm_verified_full': [True],
        'llm_agreement_rate_full': [1.0],
    })
    for short, (conf, ver, sent) in zip(LLM_MODELS, specs):
        df[f'{short}_sentiment_full'] = [sent]
        df[f'{short}_sentiment_confidence_full'] = [conf]
        df[f'{short}_verified_full'] = [ver]
    return df


class TestF3InvalidModelCellMasking:
    def test_t1_absent_model_zero_excluded(self):
        """缺席模型 (sentiment=None/verified=None/conf=0.0 结构性哨兵) 不稀释宏平均
        (旧式 raw mean = (0.9+0.85+0.0)/3 ≈ 0.5833, 审计离线重放实证)."""
        df = encode_sentiment(_article_df_permodel([
            (0.9, True, '正面'), (0.85, True, '正面'), (0.0, None, None)]))
        assert df['avg_llm_conf_full'].iloc[0] == pytest.approx(0.875)

    def test_t2_all_valid_regression_anchor(self):
        """三模型全部投出有效票: 与旧 raw 宏平均逐位一致 (回归锚)."""
        df = encode_sentiment(_article_df_permodel([
            (0.9, True, '正面'), (0.85, True, '正面'), (0.8, True, '正面')]))
        assert df['avg_llm_conf_full'].iloc[0] == pytest.approx((0.9 + 0.85 + 0.8) / 3)

    def test_t5_present_unverified_real_conf_excluded(self):
        """在场但判伪 (conf=0.7 真实值, score=NA) 亦剔 — 锚死"剔的是 score=NA 格"
        而非"仅 conf==0.0 格" (D5 构念级口径)."""
        df = encode_sentiment(_article_df_permodel([
            (0.9, True, '正面'), (0.7, False, '正面'), (0.8, True, '正面')]))
        assert df['avg_llm_conf_full'].iloc[0] == pytest.approx((0.9 + 0.8) / 2)

    def test_t3_all_invalid_nan(self):
        df = encode_sentiment(_article_df_permodel([
            (0.0, None, None), (0.0, None, None), (0.0, None, None)]))
        assert pd.isna(df['avg_llm_conf_full'].iloc[0])

    def test_t4_missing_score_source_falls_back_raw(self):
        """某模型缺 sentiment 列 → score 列不建 → 该模型回退 raw 置信度 (旧 schema 兼容)."""
        base = _article_df_permodel([
            (0.9, True, '正面'), (0.85, True, '正面'), (0.8, True, '正面')])
        base = base.drop(columns=[f'{LLM_MODELS[2]}_sentiment_full'])
        df = encode_sentiment(base)
        assert df['avg_llm_conf_full'].iloc[0] == pytest.approx((0.9 + 0.85 + 0.8) / 3)


# ============================================================================
# F3b (2026-07-16): 验证置信度诊断 _conf 参与域掩码 (llms_evaluation)
# ⚠ 与 D5 (情感有效票域) 刻意不同构: 在场判伪格是有效验证票、其 conf 是诊断对象须保留;
#   只剔缺席哨兵格 (verified=None ∧ conf=0.0)。
# ============================================================================

class TestF3bVerificationConfParticipationMask:
    def _fixture(self):
        n = 8
        df = pd.DataFrame({
            '最终_验证': [1, 1, 0, 0] * 2,
            'llm_verified_full': [True, False, True, False] * 2,
            'llm_sentiment_full': ['正面', '负面', '中性', '正面'] * 2,
            '内容': ['文本样例' * 5] * n,
        })
        m0, m1, m2 = LLM_MODELS
        df[f'{m0}_verification_confidence_full'] = 0.9
        df[f'{m0}_verified_full'] = True
        df[f'{m1}_verification_confidence_full'] = 0.7
        df[f'{m1}_verified_full'] = False      # 在场判伪: 真值必须保留
        df[f'{m2}_verification_confidence_full'] = 0.0
        df[f'{m2}_verified_full'] = None       # 缺席哨兵: 必须剔除
        return df

    def test_absent_excluded_present_false_kept(self, caplog):
        import logging

        from news_process.validation.llms_evaluation import (
            diagnose_misclassification_bias,
        )
        lg = logging.getLogger('test_f3b_participation')
        with caplog.at_level(logging.INFO, logger='test_f3b_participation'):
            diagnose_misclassification_bias(
                self._fixture(), '最终_验证', track='_full', logger_inst=lg)
        msgs = [r.message for r in caplog.records if '验证置信度' in r.message]
        assert msgs, '未见 (c) 验证置信度日志'
        # 掩码后 _conf = mean(0.9, 0.7) = 0.8 (缺席 0.0 剔除, 在场判伪 0.7 保留)
        assert 'mean=0.8000' in msgs[0], msgs[0]
        assert '剔除 8 篇×模型格' in msgs[0], msgs[0]
