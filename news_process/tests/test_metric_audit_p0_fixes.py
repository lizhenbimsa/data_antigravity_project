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

    def test_article_topic_derives_year_before_groupby(self):
        """metric-audit final (终验逮到): stage 17 article_topic 同型 latent KeyError.

        article_topic.main 从 13_news_with_ctx (无 year) 读 art_df, 在
        out_article['year']=art_df['year'] + 聚合 groupby(['target_bank','year']) 前
        必须从 '日期' 派生 year (与 stage 18/19 同口径). 源契约钉死, 防同型回归.
        """
        import inspect

        from news_process.pipeline.text import article_topic
        src = inspect.getsource(article_topic)
        derive_pos = src.find("art_df['year'] = pd.to_datetime")
        use_pos = src.find("'year': art_df['year']")
        assert derive_pos != -1, (
            "article_topic 缺 art_df['year']=pd.to_datetime(日期).dt.year 派生 → "
            "stage 17 enabled 时 KeyError('year')"
        )
        assert use_pos != -1 and derive_pos < use_pos, "year 派生须在第一次使用前"


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

    def test_main_path_derives_year_from_date_when_no_year_col(self):
        """回归: 真实 13_news_with_ctx 仅有 str '日期' 无 'year' 列.

        旧上面两个测试都给 article_df 塞了 year 列, 漏掉真实 schema. 本批主路径
        重写一度直接 article_df[['target_bank','year']] → KeyError(year). 本测试钉住
        '主路径在 article_df 缺 year 时须从 日期 派生' 的契约 (与 stage 16 实跑一致).
        """
        from news_process.pipeline.external.epu_merge import (
            aggregate_epu_to_bank_year,
        )
        epu = self._epu_df()
        # 注意: 无 'year' 列, 仅 str '日期' (镜像真实 13_news_with_ctx.parquet)
        art = pd.DataFrame({
            'target_bank': ['A'] * 12 + ['B'] * 12,
            '日期': [f'2017-{m:02d}-15 00:00:00' for m in range(1, 13)] * 2,
        })
        assert 'year' not in art.columns
        out = aggregate_epu_to_bank_year(art, epu)  # 不得 KeyError
        assert set(out['year'].unique()) == {2017}
        assert out['target_bank'].nunique() == 2
        simple_mean = float(epu.query('year==2017')['epu'].mean())
        assert abs(out['epu_mean_year'].iloc[0] - simple_mean) < 1e-9
        assert int(out['epu_data_complete'].iloc[0]) == 1

    def test_empty_and_fallback_branches_derive_year_no_crash(self):
        """metric-audit final [5]: 三分支 (empty/fallback/main) 统一 _bank_year_frame,
        消除"只有 main 派生 year, empty 静默吐空 / fallback 崩"的不对称.
        """
        from news_process.pipeline.external.epu_merge import (
            _bank_year_frame,
            aggregate_epu_to_bank_year,
        )
        # has-date-no-year (真实 13 schema)
        art = pd.DataFrame({'target_bank': ['A', 'B'],
                            '日期': ['2017-05-01', '2018-05-01']})
        # empty-epu 分支: 旧版静默返回 (0,6); 修复后从 日期 派生 → 2 行全-NaN 骨架
        o_empty = aggregate_epu_to_bank_year(art, pd.DataFrame())
        assert len(o_empty) == 2, "empty-epu 须从 日期 派生 bank-year, 非静默 0 行"
        assert set(o_empty['year']) == {2017, 2018}
        assert o_empty['epu_mean_year'].isna().all()
        # helper 直接: 缺 target_bank 时返回空 (不崩)
        assert len(_bank_year_frame(pd.DataFrame({'x': [1]}))) == 0


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


class TestCtxDiagonalFracTrackSymmetry:
    """metric-audit final: ctx 对角线分类 frac 须用 ctx 轨分母 (n_articles_llm_valid_ctx).

    病灶: app_frac_lc/sub_frac_sc/collab_frac_cm 分子=ctx 轨计数, 分母却=full 轨
    n_articles_llm_valid → "full 失败但 ctx 成功"的文章使 ctx_valid>full_valid →
    frac 越界至 3.0 (终验工作流逮到 41/117 行对子和≠1). 修复: 配 ctx 分母, 数学保证
    分子≤分母 → frac∈[0,1]. bug 复活 (分母回退 full) 则 frac>1 → 必挂.
    """

    def test_ctx_frac_uses_ctx_denominator_not_full(self):
        from news_process.pipeline.panel.encode import aggregate_panel
        # 5 篇全 '应用场景' locus: full 轨仅 1 篇有效投票 (4 篇 LLM-fail NA),
        # ctx 轨 5 篇全有效 → n_articles_llm_valid=1, n_articles_llm_valid_ctx=5,
        # n_articles_app_lc_ctx=5. 旧 bug: app_frac_lc=5/1=5.0; 修复后=5/5=1.0.
        df = pd.DataFrame({
            'target_bank': ['A'] * 5, 'year': [2018] * 5,
            'llm_vote_score_full': pd.array([1, None, None, None, None], dtype='Int8'),
            'llm_vote_score_ctx': pd.array([1, 1, 1, 1, 1], dtype='Int8'),
            'llm_prob_score_ctx': [0.9] * 5,
            'innovation_locus_full': ['应用场景', None, None, None, None],
            'innovation_locus_ctx': ['应用场景'] * 5,
            'is_positive_full': pd.array([1, 0, 0, 0, 0], dtype='Int8'),
            'is_negative_full': pd.array([0, 0, 0, 0, 0], dtype='Int8'),
            'in_title': [0] * 5, 'is_multi_bank': [0] * 5, 'bank_count': [1] * 5,
        })
        out = aggregate_panel(df).iloc[0]
        # 新增 ctx 轨有效计数列
        assert 'n_articles_llm_valid_ctx' in out.index
        assert out['n_articles_llm_valid'] == 1, "full 轨有效 = 1"
        assert out['n_articles_llm_valid_ctx'] == 5, "ctx 轨有效 = 5"
        assert out['n_articles_app_lc_ctx'] == 5, "应用场景 ctx 计数 = 5"
        # 关键: 分母用 ctx (5) 非 full (1) → frac=1.0 (旧 bug=5.0)
        assert abs(out['app_frac_lc'] - 1.0) < 1e-9, (
            f"app_frac_lc={out['app_frac_lc']}; 旧 bug (ctx分子/full分母)=5.0, "
            f"修复 (ctx分子/ctx分母)=1.0"
        )
        assert out['app_frac_lc'] <= 1.0 + 1e-9, "frac 不得越界 [0,1]"


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


class TestNArticlesCrossFileConsumers:
    """n_articles 重构跨文件消费者对齐: stata_audit 恒等式须用 LLM-valid 口径.

    终验工作流发现: encode.py 内重构正确, 但 stata_audit/encode_collab/network_brokerage
    等下游仍硬编码旧 n_articles=count 假设. stata_audit 恒等式是 P1 阻断
    (FAIL → stage 52 退出码 1). 本测试钉住: 物理 n_articles 的 panel 不再误 FAIL.
    """

    def _run_identity(self, panel):
        import news_process.pipeline.audit.stata_audit as sa
        sa.audit_results.clear()
        sa.audit_sentiment_consistency(panel, 'test')
        ids = [r for r in sa.audit_results if '恒等式' in r['check']]
        return [r for r in ids if r['status'] == 'FAIL']

    def test_new_panel_physical_n_articles_no_false_fail(self):
        # 新 panel: n_articles=物理(含 LLM 失败行), llm_valid=count, tech+app=llm_valid.
        panel = pd.DataFrame({
            'target_bank': ['A', 'B'], 'year': [2018, 2018],
            'n_articles': [10, 12],            # 物理 (2/3 篇 LLM 失败)
            'n_articles_llm_valid': [8, 9],    # 有效
            'n_articles_tech': [5, 6], 'n_articles_app': [3, 3],
            'pos_count_full': [4, 5], 'neg_count_full': [2, 2],
            'pos_frac_full': [0.5, 0.55], 'neg_frac_full': [0.25, 0.22],
        })
        # 修复前: n_articles(10) != tech+app(8) → FAIL; 修复后 _nac=llm_valid → PASS
        assert self._run_identity(panel) == [], "物理 n_articles 不应令恒等式误 FAIL"

    def test_old_frozen_panel_fallback(self):
        # 旧冻结 panel: 无 n_articles_llm_valid, n_articles=count → fallback 用 n_articles.
        panel = pd.DataFrame({
            'target_bank': ['A', 'B'], 'year': [2018, 2018],
            'n_articles': [8, 9],              # 旧口径 = count
            'n_articles_tech': [5, 6], 'n_articles_app': [3, 3],
            'pos_count_full': [4, 5], 'neg_count_full': [2, 2],
            'pos_frac_full': [0.5, 0.55], 'neg_frac_full': [0.25, 0.22],
        })
        assert self._run_identity(panel) == [], "旧 panel fallback 应正常 PASS"

    def test_no_count_column_panel_graceful(self):
        # 终验复核回归守卫: 无任何 count 列 (n_articles/llm_valid 都缺) 的 panel
        # 不得抛 KeyError (须保留 graceful 兜底, 与 audit_variable_quality 对称).
        import news_process.pipeline.audit.stata_audit as sa
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018],
            'pos_frac_full': [0.5], 'neg_frac_full': [0.2],
        })
        sa.audit_results.clear()
        sa.audit_sentiment_consistency(panel, 'test')  # 不得 KeyError


class TestCtxCountOverflowSanity:
    """_ctx 计数越界缺陷修复: 情感计数 sanity 以物理 n_articles 为上界.

    根因: n_articles=full轨有效篇数, pos_count_ctx=ctx轨有效篇数; full失败但ctx成功
    的文章使 ctx-valid > full-valid (合法两轨差异, 非双计). 修复: 3b 用物理
    n_articles(≥任一轨); 旧冻结panel(full-valid)越界降WARN, 重生panel(物理)PASS,
    真双计(物理<pos+neg)仍FAIL.
    """

    def _ctx(self, panel):
        import news_process.pipeline.audit.stata_audit as sa
        sa.audit_results.clear()
        sa.audit_sentiment_consistency(panel, 'test')
        return {r['check']: r['status'] for r in sa.audit_results
                if '情感计数恒等式' in r['check']}

    def test_regen_panel_physical_ge_ctx_pass(self):
        # 重生型: 物理14 ≥ ctx pos13 → PASS (有 n_articles_llm_valid 标记物理)
        p = pd.DataFrame({'target_bank': ['A'], 'year': [2017],
                          'n_articles': [14], 'n_articles_llm_valid': [12],
                          'pos_count_full': [12], 'neg_count_full': [0],
                          'pos_count_ctx': [13], 'neg_count_ctx': [0],
                          'pos_frac_full': [1.0], 'neg_frac_full': [0.0]})
        assert self._ctx(p).get('情感计数恒等式 (_ctx)') == 'PASS'

    def test_frozen_panel_overflow_warn_not_fail(self):
        # 旧冻结型: n_articles=full-valid 12 < ctx 13, 无 n_articles_llm_valid → WARN(非FAIL)
        p = pd.DataFrame({'target_bank': ['A'], 'year': [2017], 'n_articles': [12],
                          'pos_count_full': [12], 'neg_count_full': [0],
                          'pos_count_ctx': [13], 'neg_count_ctx': [0],
                          'pos_frac_full': [1.0], 'neg_frac_full': [0.0]})
        st = self._ctx(p)
        assert st.get('情感计数恒等式 (_ctx)') == 'WARN', "旧 panel 越界应降 WARN(非 FAIL)"

    def test_real_double_count_still_fail(self):
        # 重生型 + 真双计: 物理12 < ctx pos13 → FAIL (sanity 仍守)
        p = pd.DataFrame({'target_bank': ['A'], 'year': [2017],
                          'n_articles': [12], 'n_articles_llm_valid': [12],
                          'pos_count_full': [12], 'neg_count_full': [0],
                          'pos_count_ctx': [13], 'neg_count_ctx': [0],
                          'pos_frac_full': [1.0], 'neg_frac_full': [0.0]})
        assert self._ctx(p).get('情感计数恒等式 (_ctx)') == 'FAIL'
