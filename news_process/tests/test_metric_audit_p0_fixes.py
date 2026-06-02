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


class TestDiscriminant39eCoWSafe:
    """P0 (漏报): stage 39e np.fill_diagonal(df.values) 在 pandas 3.0 CoW 下崩溃."""

    def test_corr_values_is_readonly_under_cow(self):
        # 文档化崩溃前提: pandas 3.0 CoW 下 corr().abs().values 为只读.
        m = pd.DataFrame(np.random.RandomState(0).rand(6, 6))
        v = m.corr().abs().values
        if not v.flags.writeable:
            with pytest.raises(ValueError):
                np.fill_diagonal(v, np.nan)  # 旧代码在此崩

    def test_offdiag_max_no_crash_and_matches_legacy(self):
        from news_process.pipeline.audit.lm_discriminant_validity import (
            _offdiag_max,
        )
        corr = pd.DataFrame(np.random.RandomState(1).rand(6, 6)).corr().abs()
        od = _offdiag_max(corr)  # 不得崩
        # 语义=非对角最大值 (旧 fill_diagonal+max().max() 在可写副本上的结果)
        a = corr.to_numpy(copy=True)
        np.fill_diagonal(a, np.nan)
        legacy = float(np.nanmax(a))
        assert abs(od - legacy) < 1e-12
        assert od < 1.0, "必须排除对角自相关(=1.0)"

    def test_permutation_null_runs(self):
        from news_process.pipeline.audit.lm_discriminant_validity import (
            INDICATORS_FULL,
            permutation_null,
        )
        rng = np.random.default_rng(0)
        panel = pd.DataFrame({c: rng.random(60) for c in INDICATORS_FULL})
        out = permutation_null(panel, INDICATORS_FULL, n_perm=20, seed=42)
        assert not out.empty
        assert out['obs_htmt_max'].iloc[0] < 1.0  # off-diag, 非对角 1.0


class TestRiskBankListPath:
    """P1 (漏报): bank_list.yaml 默认路径从 cwd=news_process/ 解析失败 → metadata 全 NaN."""

    def test_default_path_resolves_to_real_file(self):
        from news_process.pipeline.panel.risk_taking_outcomes import (
            _DEFAULT_BANK_LIST,
        )
        # 相对模块解析的默认路径必须指向真实存在的 config/bank_list.yaml
        assert _DEFAULT_BANK_LIST.exists(), f"默认 bank_list 路径不存在: {_DEFAULT_BANK_LIST}"
        assert _DEFAULT_BANK_LIST.name == 'bank_list.yaml'

    def test_merge_loads_metadata_not_all_nan(self):
        import yaml

        from news_process.pipeline.panel.risk_taking_outcomes import (
            _DEFAULT_BANK_LIST,
            merge_bank_metadata,
        )
        banks = yaml.safe_load(_DEFAULT_BANK_LIST.open(encoding='utf-8')).get('banks', [])
        if not banks:
            pytest.skip('bank_list.yaml banks 为空')
        tb = banks[0]['target_bank']
        df = pd.DataFrame({'target_bank': [tb], 'year': [2018]})
        merged = merge_bank_metadata(df)  # 用默认路径 (修复前从 cwd 解析失败→全 NaN)
        assert merged['is_soe'].notna().all(), '默认路径应能加载 metadata, 不应全 NaN'


class TestCohenKappaConstantAxisGuard:
    """P1 (漏报): 39d Cohen κ 在常量轴下 vacuous 退化为 0.0, 应返回 NaN."""

    def test_constant_substance_axis_returns_nan(self):
        from news_process.pipeline.audit.lexical_discriminant_validity import (
            compute_cohen_kappa_substance_vs_clarity,
        )
        # substance 全 < 0.5 → s_bin 全 0 (常量轴); 旧代码 vacuous κ=0.0, 修复后 NaN
        out = compute_cohen_kappa_substance_vs_clarity(
            substance=np.full(50, 0.2),
            clarity=np.random.RandomState(0).rand(50),
        )
        assert np.isnan(out['kappa']), f"常量轴 κ 应为 NaN(未定义), 实得 {out['kappa']}"

    def test_varying_axes_still_compute_finite_kappa(self):
        from news_process.pipeline.audit.lexical_discriminant_validity import (
            compute_cohen_kappa_substance_vs_clarity,
        )
        rs = np.random.RandomState(1)
        out = compute_cohen_kappa_substance_vs_clarity(
            substance=rs.rand(80), clarity=rs.rand(80),
        )
        assert np.isfinite(out['kappa']), '有变异时 κ 应正常算出有限值'


class TestHerdWeightActuallyApplies:
    """P0/P1: encode_collab 此前按幽灵列 herd_decay_weight 加权 → herd 静默失效.

    修复后改读真列 herd_weight_full. 本测试用 herd_weight_full≠1.0 证明权重真生效
    (审计要求的非平凡守卫: bug 复活则加权均值回到等权值 → 必挂).
    """

    def test_herd_weight_changes_weighted_clarity_mean(self):
        from news_process.pipeline.panel.encode_collab import (
            aggregate_clarity_panel,
        )
        # bank A 2 篇: 第 2 篇 herd_weight_full=0 (跟风稿被剔除).
        df = pd.DataFrame([
            {'target_bank': 'A', 'year': 2020,
             'clarity_frac_ambiguous_full': 0.05, 'clarity_frac_definite_full': 0.05,
             'clarity_clarity_score_full': 1.0,
             'clarity_frac_ambiguous_ctx': 0.05, 'clarity_frac_definite_ctx': 0.05,
             'clarity_clarity_score_ctx': 1.0,
             'media_authority_weight': 1.0, 'herd_weight_full': 1.0},
            {'target_bank': 'A', 'year': 2020,
             'clarity_frac_ambiguous_full': 0.05, 'clarity_frac_definite_full': 0.05,
             'clarity_clarity_score_full': 0.0,
             'clarity_frac_ambiguous_ctx': 0.05, 'clarity_frac_definite_ctx': 0.05,
             'clarity_clarity_score_ctx': 0.0,
             'media_authority_weight': 1.0, 'herd_weight_full': 0.0},
        ])
        panel = pd.DataFrame([{'target_bank': 'A', 'year': 2020}])
        aggregate_clarity_panel(df, panel, median_amb_d0=0.05)
        mean_full = panel[panel['target_bank'] == 'A'].iloc[0]['mean_clarity_score_full']
        # herd 生效: (1.0*1.0 + 0.0*0.0)/(1.0+0.0)=1.0; herd 失效(bug): 0.5.
        assert abs(mean_full - 1.0) < 1e-6, (
            f'herd_weight_full 应真生效 → 加权均值=1.0; 实得 {mean_full} '
            f'(=0.5 说明 herd 列被忽略, bug 复活)'
        )


class TestEpuMonthEqualWeighting:
    """P1: EPU 年度暴露须月度等权 (BBD 2016 QJE), 非 article-count 加权."""

    def _epu_df(self):
        rows = []
        for y in (2017, 2018):
            for m in range(1, 13):
                rows.append({'year': y, 'month': m,
                             'epu': float(m * 10 + (0 if y == 2017 else 100))})
        return pd.DataFrame(rows)

    def test_month_equal_not_article_weighted(self):
        from news_process.pipeline.external.epu_merge import (
            aggregate_epu_to_bank_year,
        )
        # bank A 在 1 月发 100 篇 (高发稿月), bank B 各月各 1 篇.
        arts = ([{'target_bank': 'A', '日期': '2017-01-15'}] * 100
                + [{'target_bank': 'A', '日期': f'2017-{m:02d}-15'} for m in range(2, 13)]
                + [{'target_bank': 'B', '日期': f'2017-{m:02d}-15'} for m in range(1, 13)])
        art = pd.DataFrame(arts)
        art['year'] = 2017
        out = aggregate_epu_to_bank_year(art, self._epu_df())
        a = out[out.target_bank == 'A'].iloc[0]
        b = out[out.target_bank == 'B'].iloc[0]
        simple_mean = float(self._epu_df().query('year==2017')['epu'].mean())
        # 银行间相同(年内 EPU 不随发稿量变) + 等于月度等权均值 (旧实现 A 会被拉偏)
        assert abs(a.epu_mean_year - b.epu_mean_year) < 1e-9
        assert abs(a.epu_mean_year - simple_mean) < 1e-9
        # year_end = 12 月值; complete=1 (12 月齐, 旧实现恒 0)
        assert abs(a.epu_year_end - 120.0) < 1e-9
        assert int(a.epu_data_complete) == 1

    def test_main_and_fallback_paths_consistent(self):
        # 验证工作流残留项: year-only fallback(无 date 列) 须与主路径(有 日期)同口径.
        from news_process.pipeline.external.epu_merge import (
            aggregate_epu_to_bank_year,
        )
        epu = self._epu_df()
        main_in = pd.DataFrame({'target_bank': ['A'] * 12, 'year': [2017] * 12,
                                '日期': [f'2017-{m:02d}-15' for m in range(1, 13)]})
        fb_in = pd.DataFrame({'target_bank': ['A'], 'year': [2017]})  # 无 date 列 → fallback
        m = aggregate_epu_to_bank_year(main_in, epu).iloc[0]
        f = aggregate_epu_to_bank_year(fb_in, epu).iloc[0]
        assert abs(m.epu_mean_year - f.epu_mean_year) < 1e-9
        assert abs(m.epu_year_end - f.epu_year_end) < 1e-9
        assert int(m.epu_data_complete) == int(f.epu_data_complete)
        # 且 fallback 也取 12 月值(非旧 .last())
        assert abs(f.epu_year_end - 120.0) < 1e-9


class TestNArticlesPhysicalRefactor:
    """encode-02 正确重构: n_articles=物理篇数(coverage), 分类 frac 分母=n_articles_llm_valid.

    端到端跑真实 aggregate_panel, 钉住: (1) n_articles=物理(含LLM失败行);
    (2) n_articles_llm_valid=有效计数; (3) tech_frac+app_frac==1 (分子分母同口径);
    (4) ln_news_coverage 用物理. bug 复活(分母错配)则 frac 和≠1 → 必挂.
    """

    def test_n_articles_physical_and_frac_consistent(self):
        from news_process.pipeline.panel.encode import aggregate_panel
        # 物理 20 篇: 18 LLM-valid (10 底层技术 / 8 应用场景), 2 LLM-fail(NA, 无 locus).
        score = [1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, 1, -1, 0, None, None]
        locus = ['底层技术'] * 10 + ['应用场景'] * 8 + [None, None]
        df = pd.DataFrame({
            'target_bank': ['A'] * 20, 'year': [2018] * 20,
            'llm_vote_score_full': pd.array(score, dtype='Int8'),
            'llm_vote_score_ctx': pd.array(score, dtype='Int8'),
            'innovation_locus_full': locus,
            'is_positive_full': pd.array([1 if s == 1 else 0 for s in score], dtype='Int8'),
            'is_negative_full': pd.array([1 if s == -1 else 0 for s in score], dtype='Int8'),
            'in_title': [0] * 20, 'is_multi_bank': [0] * 20, 'bank_count': [1] * 20,
        })
        out = aggregate_panel(df).iloc[0]
        assert out['n_articles'] == 20, "n_articles 应为物理篇数(含 LLM 失败行)"
        assert out['n_articles_llm_valid'] == 18, "n_articles_llm_valid 应为 LLM 有效计数"
        assert abs(out['tech_frac'] - 10 / 18) < 1e-9, "tech_frac 分母应为 valid 计数"
        assert abs(out['app_frac'] - 8 / 18) < 1e-9
        # 关键不变式: 分子分母同口径 → tech_frac+app_frac==1 (bug 复活则 <1)
        assert abs((out['tech_frac'] + out['app_frac']) - 1.0) < 1e-9, (
            "tech_frac+app_frac 应==1; <1 说明分母用了物理篇数(口径破坏 bug 复活)"
        )
        # ln_news_coverage 用物理篇数
        assert abs(out['ln_news_coverage'] - np.log1p(20)) < 1e-9


class TestStrategicDiffNoDoubleTitle:
    """P1 (漏报): strategic_diff/policy_similarity 共享 _aggregate 对 ctx 轨双标题."""

    def test_ctx_track_title_not_doubled(self):
        from news_process.core.text.entity_context import prepend_title
        from news_process.pipeline.features.strategic_diff import (
            _aggregate_bank_year_texts,
        )
        T = '某银行金融科技战略'
        df = pd.DataFrame({
            'target_bank': ['A', 'A'], 'year': [2018, 2018],
            '标题': [T, T], '内容': ['正文数字化转型布局推进', '正文数字化转型布局推进'],
            'content_ctx': [prepend_title(T, '实体窗口附近几句'),
                            prepend_title(T, '实体窗口附近几句')],
        })
        full = _aggregate_bank_year_texts(df, text_col='内容').iloc[0]['agg_text']
        ctx = _aggregate_bank_year_texts(df, text_col='content_ctx').iloc[0]['agg_text']
        # 2 篇文章, 每篇标题应恰 1 次 → 共 2 次 (旧 ctx bug 为 4)
        assert full.count(T) == 2, f"full 标题次数={full.count(T)}"
        assert ctx.count(T) == 2, f"ctx 双标题未修复: {ctx.count(T)} (应 2, 旧 bug=4)"
