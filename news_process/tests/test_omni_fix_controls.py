"""test_omni_fix_controls.py — OMNI 审计 g-controls 组修复回归锁
=================================================================

锁定 2026-06-11 OMNI 审计 (scripts/audit/_omni_fix/g-controls.json) 七条
确认缺陷的修复后行为, 防静默 revert:

  - g-controls-01: placebo DID 伪处理窗口加上界 [ty-k, ty) (旧实现是真实
                   post 的严格超集 → 真效应存在则 placebo 必显著);
                   Hassan QJE Table 7 错配引文移除 (源码级断言)
  - g-controls-02: nf_media_breadth 改物理 (去重前) 行集 nunique — 跨媒体
                   转载属于广度 (Bushee 2010 JAR); nf_n_articles 维持
                   去重基"同稿件"集合语义
  - g-controls-03/07: all_n_articles / ln_ft_articles / ln_nf_articles 计数
                   基统一 (ft_dedup 可用时全部去重同基; 回退混合基如实披露)
  - g-controls-04: L663 同义反复"恒等式校验"删除, 改有信息量的跨源一致性
                   校验 (去重 fintech 计数 ≤ 物理 n_articles 逐行)
  - g-controls-05: fintech_share 分母 0 → NaN (未定义份额不再与真实 0 份额
                   同值混淆) + zero_coverage 指示列
  - g-controls-06: stage 51 .dta 变量标签经共享构建器
                   (stata_export.build_variable_labels) + STATA_LABELS_41
                   覆盖, 每列非空标签且 ≤80 UTF-8 字节

全部用合成 DataFrame, 不依赖盘上大数据, 不调外部 API。
"""

import inspect
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest

from news_process.pipeline.falsification import controls as mod

pytestmark = pytest.mark.fast

SRC = Path(mod.__file__).read_text(encoding='utf-8')


# ============================================================================
# 共享 fixtures
# ============================================================================

@pytest.fixture()
def panel_nf_dedup():
    """merge_to_panel 最小输入: 物理 fintech=10, 去重 fintech=8, NF(去重)=5。"""
    panel = pd.DataFrame({
        'target_bank': ['A'], 'year': [2018], 'n_articles': [10],
    })
    nf_agg = pd.DataFrame({
        'target_bank': ['A'], 'year': [2018], 'nf_n_articles': [5],
    })
    ft_dedup = pd.DataFrame({
        'target_bank': ['A'], 'year': [2018], 'ft_n_articles_dedup': [8],
    })
    return panel, nf_agg, ft_dedup


# ============================================================================
# g-controls-01: placebo DID 伪处理窗口上界
# ============================================================================

class TestPlaceboWindowUpperBound:

    @pytest.fixture()
    def did_panel(self):
        years = list(range(2010, 2021))
        rows = []
        for y in years:
            rows.append({'target_bank': 'T', 'year': y,
                         'dcep_treat_year': 2015, 'dcep_treated': 1})
            rows.append({'target_bank': 'C', 'year': y,
                         'dcep_treat_year': 0, 'dcep_treated': 0})
        return pd.DataFrame(rows)

    def test_placebo_post_window_is_pre_treatment_only(self, did_panel):
        """placebo{k}_post = 1{ty-k <= year < ty}, 真实处理年起必须为 0。"""
        out = mod.generate_placebo_did_variables(
            did_panel.copy(), placebo_shifts=[2, 3], logger_inst=MagicMock())
        t = out[out['target_bank'] == 'T'].set_index('year')
        # k=2: 窗口 [2013, 2015)
        for y in [2013, 2014]:
            assert t.loc[y, 'dcep_placebo2_post'] == 1, f'{y} 应在 placebo2 窗口内'
        for y in [2010, 2011, 2012]:
            assert t.loc[y, 'dcep_placebo2_post'] == 0, f'{y} 早于窗口应为 0'
        # 关键修复: 真实处理年及之后必须为 0 (旧实现这里全是 1)
        for y in range(2015, 2021):
            assert t.loc[y, 'dcep_placebo2_post'] == 0, \
                f'{y} >= 真实处理年 2015, placebo_post 应为 0 (旧超集 bug)'
        # k=3: 窗口 [2012, 2015)
        assert t.loc[2012, 'dcep_placebo3_post'] == 1
        assert t.loc[2015, 'dcep_placebo3_post'] == 0

    def test_placebo_disjoint_from_real_post(self, did_panel):
        """placebo 窗口与真实 post 期 [ty, T] 零重叠 (互斥)。"""
        out = mod.generate_placebo_did_variables(
            did_panel.copy(), placebo_shifts=[1, 2, 3], logger_inst=MagicMock())
        real_post = ((out['dcep_treat_year'] > 0)
                     & (out['year'] >= out['dcep_treat_year'])).astype(int)
        for k in [1, 2, 3]:
            overlap = (real_post & out[f'dcep_placebo{k}_post']).sum()
            assert overlap == 0, f'placebo{k}_post 与真实 post 重叠 {overlap} 行'

    def test_control_bank_all_zero(self, did_panel):
        """未处理银行 (treat_year=0) 的 placebo post/did 全 0。"""
        out = mod.generate_placebo_did_variables(
            did_panel.copy(), placebo_shifts=[2], logger_inst=MagicMock())
        c = out[out['target_bank'] == 'C']
        assert (c['dcep_placebo2_post'] == 0).all()
        assert (c['dcep_placebo2_did'] == 0).all()

    def test_placebo_did_is_treated_times_post(self, did_panel):
        out = mod.generate_placebo_did_variables(
            did_panel.copy(), placebo_shifts=[2], logger_inst=MagicMock())
        expected = out['dcep_treated'] * out['dcep_placebo2_post']
        assert (out['dcep_placebo2_did'] == expected).all()

    def test_hassan_citation_removed_from_placebo_block(self):
        """G-13 placebo 块不再错引 Hassan 2019 QJE Table 7 (源码级断言)。

        Hassan Table 7 是 PRisk/NPRisk 伪造检验 (模块其余部分合法引用),
        与 placebo-in-time 无关; placebo 块应引 Callaway & Sant'Anna (2021)。
        """
        src = inspect.getsource(mod.generate_placebo_did_variables)
        assert 'Hassan' not in src, 'placebo 函数内不应再引 Hassan Table 7'
        assert 'Callaway' in src
        # 日志中的 Stata 建议须控制真实 DID 项或限处理前样本
        assert '_did X' in src and 'year <' in src

    def test_stata_advice_controls_real_did(self, did_panel):
        """Stata 命令建议同时纳入真实 DID 项 (日志行为锁定)。"""
        lg = MagicMock()
        mod.generate_placebo_did_variables(
            did_panel.copy(), placebo_shifts=[2], logger_inst=lg)
        logged = ' '.join(str(c.args[0]) for c in lg.info.call_args_list)
        assert 'dcep_placebo2_did dcep_did' in logged, \
            'Stata 建议应同时控制真实 DID 项'


# ============================================================================
# g-controls-02: nf_media_breadth 物理 (去重前) 口径
# ============================================================================

class TestMediaBreadthPhysicalBasis:

    @pytest.fixture()
    def reprint_corpus(self):
        """同稿跨媒体转载语料: t1 被 3 家媒体转载 (同复合键), t2 单媒体。"""
        df_full = pd.DataFrame({
            'target_bank': ['A'] * 5,
            '标题': ['t1', 't1', 't1', 't2', 'p1'],
            '日期': ['2018-01-01'] * 3 + ['2018-02-02', '2018-03-03'],
            '媒体(中文)': ['新华社', '经济日报', '证券时报', '新华社', '新华社'],
            'is_fintech_news': [False, False, False, False, True],
        })
        # p1 是面板 (fintech) 文章 → anti-join 后不入 NF
        df_art = pd.DataFrame({
            'target_bank': ['A'],
            '标题': ['p1'],
            '日期': ['2018-03-03'],
            'year': [2018],
        })
        return df_full, df_art

    def test_breadth_counts_reprint_outlets(self, reprint_corpus):
        """物理口径: t1 的 3 家转载媒体全部计入 distinct-outlet 广度。"""
        df_full, df_art = reprint_corpus
        df_nf = mod.build_non_fintech(df_full, df_art)
        nf_agg = mod.aggregate_non_fintech(df_nf)
        row = nf_agg[(nf_agg['target_bank'] == 'A') & (nf_agg['year'] == 2018)]
        assert len(row) == 1
        # 物理 NF 行集 = {t1×新华社, t1×经济日报, t1×证券时报, t2×新华社}
        # → 3 家不同媒体; 旧去重基只剩 keep='first' 的 {t1×新华社, t2×新华社} → 1
        assert int(row['nf_media_breadth'].iloc[0]) == 3, \
            '跨媒体转载应计入广度 (Bushee 2010), 去重基旧值=1'

    def test_nf_n_articles_keeps_dedup_semantics(self, reprint_corpus):
        """nf_n_articles 维持去重基"同稿件"集合语义 (t1 折叠为 1 篇)。"""
        df_full, df_art = reprint_corpus
        df_nf = mod.build_non_fintech(df_full, df_art)
        nf_agg = mod.aggregate_non_fintech(df_nf)
        row = nf_agg[(nf_agg['target_bank'] == 'A') & (nf_agg['year'] == 2018)]
        assert int(row['nf_n_articles'].iloc[0]) == 2, \
            'nf_n_articles 应为去重稿件数 2 (t1, t2), 非物理 4'

    def test_physical_breadth_attrs_exposed(self, reprint_corpus):
        """build_non_fintech 经 df_nf.attrs 暴露物理口径广度聚合。"""
        df_full, df_art = reprint_corpus
        df_nf = mod.build_non_fintech(df_full, df_art)
        breadth = df_nf.attrs.get('nf_media_breadth_physical')
        assert breadth is not None
        assert set(breadth.columns) == {'target_bank', 'year', 'nf_media_breadth'}
        assert int(breadth.loc[
            (breadth['target_bank'] == 'A') & (breadth['year'] == 2018),
            'nf_media_breadth'].iloc[0]) == 3

    def test_aggregate_fallback_without_attrs(self):
        """直调 aggregate_non_fintech (无 attrs 注入) → 去重基 fallback 仍可用。"""
        df_nf = pd.DataFrame({
            'target_bank': ['A', 'A'],
            '标题': ['x1', 'x2'],
            '日期': ['2018-01-01', '2018-02-02'],
            '媒体(中文)': ['新华社', '经济日报'],
        })
        nf_agg = mod.aggregate_non_fintech(df_nf)
        row = nf_agg[(nf_agg['target_bank'] == 'A') & (nf_agg['year'] == 2018)]
        assert int(row['nf_media_breadth'].iloc[0]) == 2


# ============================================================================
# g-controls-03/07: all_n_articles / ln_ft / ln_nf 计数基统一
# ============================================================================

class TestCountingBasisUnification:

    def test_all_n_articles_dedup_basis(self, panel_nf_dedup):
        """ft_dedup_agg 可用 → all_n_articles = ft_dedup + nf (去重同基)。"""
        panel, nf_agg, ft_dedup = panel_nf_dedup
        out = mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)
        # 修复后 = 8 + 5 = 13; 旧混合基 bug = 10 + 5 = 15
        assert out['all_n_articles'].iloc[0] == 13, \
            'all_n_articles 应为去重同基 8+5=13, 非混合基 10+5=15'
        assert abs(out['all_ln_coverage'].iloc[0] - np.log1p(13)) < 1e-12

    def test_ln_elasticity_pair_same_basis(self, panel_nf_dedup):
        """挤出弹性对 ln_ft / ln_nf 两端同基 (均去重)。"""
        panel, nf_agg, ft_dedup = panel_nf_dedup
        out = mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)
        # 修复后 ln_ft = log1p(8) (去重); 旧 bug = log1p(10) (物理)
        assert abs(out['ln_ft_articles'].iloc[0] - np.log1p(8)) < 1e-12, \
            'ln_ft_articles 应用去重计数 8, 非物理 10'
        assert abs(out['ln_nf_articles'].iloc[0] - np.log1p(5)) < 1e-12

    def test_fintech_share_consistent_with_all(self, panel_nf_dedup):
        """fintech_share 与 all_n_articles 共享同一去重分母。"""
        panel, nf_agg, ft_dedup = panel_nf_dedup
        out = mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)
        assert abs(out['fintech_share'].iloc[0] - 8.0 / 13.0) < 1e-12

    def test_fallback_mixed_basis_backward_compat(self, panel_nf_dedup):
        """ft_dedup_agg=None → 回退混合基 (物理 fintech + 去重 NF), 向后兼容。"""
        panel, nf_agg, _ = panel_nf_dedup
        out = mod.merge_to_panel(panel.copy(), nf_agg)
        assert out['all_n_articles'].iloc[0] == 15
        assert abs(out['ln_ft_articles'].iloc[0] - np.log1p(10)) < 1e-12
        assert abs(out['fintech_share'].iloc[0] - 10.0 / 15.0) < 1e-12

    def test_docstring_no_longer_claims_physical_nf(self):
        """注释/docstring 不再把混合基谎称'物理覆盖' (源码级断言)。"""
        src = inspect.getsource(mod.merge_to_panel)
        assert 'all_n_articles 维持 n_articles+nf (物理覆盖' not in src
        assert '混合基' in src  # 回退口径如实披露


# ============================================================================
# g-controls-04: 同义反复恒等式 → 跨源一致性校验
# ============================================================================

class TestCrossSourceCheck:

    def test_tautology_removed(self):
        """旧 `all == n_articles + nf` 同义反复校验已删 (源码级断言)。"""
        src = inspect.getsource(mod.merge_to_panel)
        assert ("(panel['all_n_articles'] == panel['n_articles'] + "
                "panel['nf_n_articles']).all()") not in src, \
            '同义反复恒等式校验不应回归'
        assert '跨源一致性校验' in src

    def test_violation_triggers_error_log(self, panel_nf_dedup, monkeypatch):
        """去重计数 > 物理计数 (跨源分叉) → logger.error 报警。"""
        panel, nf_agg, _ = panel_nf_dedup
        # 构造违例: 去重计数 12 > 物理 n_articles 10 (merge 键错位才会发生)
        ft_bad = pd.DataFrame({
            'target_bank': ['A'], 'year': [2018], 'ft_n_articles_dedup': [12],
        })
        fake = MagicMock()
        monkeypatch.setattr(mod, 'logger', fake)
        mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_bad)
        err_msgs = ' '.join(str(c.args[0]) for c in fake.error.call_args_list)
        assert '跨源校验失败' in err_msgs

    def test_consistent_data_no_error(self, panel_nf_dedup, monkeypatch):
        """去重 ≤ 物理逐行成立 → 零 error。"""
        panel, nf_agg, ft_dedup = panel_nf_dedup
        fake = MagicMock()
        monkeypatch.setattr(mod, 'logger', fake)
        mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)
        assert fake.error.call_count == 0


# ============================================================================
# g-controls-05: fintech_share 分母 0 → NaN + zero_coverage
# ============================================================================

class TestFintechShareUndefinedVsTrueZero:

    @pytest.fixture()
    def mixed_panel(self):
        """三类行: 零新闻 (份额无定义) / 真零份额 (ft=0,nf>0) / 正常。"""
        panel = pd.DataFrame({
            'target_bank': ['Z', 'T', 'N'],
            'year': [2018, 2018, 2018],
            'n_articles': [0, 0, 10],
        })
        nf_agg = pd.DataFrame({
            'target_bank': ['T', 'N'],
            'year': [2018, 2018],
            'nf_n_articles': [5, 5],
        })
        ft_dedup = pd.DataFrame({
            'target_bank': ['N'], 'year': [2018], 'ft_n_articles_dedup': [8],
        })
        return panel, nf_agg, ft_dedup

    def test_undefined_share_is_nan(self, mixed_panel):
        panel, nf_agg, ft_dedup = mixed_panel
        out = mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)
        out = out.set_index('target_bank')
        # Z: 全年零新闻 → 份额无定义 = NaN (旧 bug: 填 0 与真零混淆)
        assert np.isnan(out.loc['Z', 'fintech_share'])

    def test_true_zero_share_stays_zero(self, mixed_panel):
        panel, nf_agg, ft_dedup = mixed_panel
        out = mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)
        out = out.set_index('target_bank')
        # T: 有 5 篇 NF 但 0 篇 fintech → 真实零份额 = 0.0 (与 NaN 可区分)
        assert out.loc['T', 'fintech_share'] == 0.0
        # N: 正常 8/(8+5)
        assert abs(out.loc['N', 'fintech_share'] - 8.0 / 13.0) < 1e-12

    def test_zero_coverage_indicator(self, mixed_panel):
        panel, nf_agg, ft_dedup = mixed_panel
        out = mod.merge_to_panel(panel.copy(), nf_agg, ft_dedup_agg=ft_dedup)
        out = out.set_index('target_bank')
        assert out.loc['Z', 'zero_coverage'] == 1
        assert out.loc['T', 'zero_coverage'] == 0
        assert out.loc['N', 'zero_coverage'] == 0

    def test_nan_also_in_fallback_path(self):
        """无 ft_dedup_agg 的回退路径同样 NaN 化分母 0。"""
        panel = pd.DataFrame({
            'target_bank': ['Z'], 'year': [2018], 'n_articles': [0],
        })
        nf_agg = pd.DataFrame({
            'target_bank': pd.Series(dtype=object),
            'year': pd.Series(dtype='int64'),
            'nf_n_articles': pd.Series(dtype='int64'),
        })
        out = mod.merge_to_panel(panel.copy(), nf_agg)
        assert np.isnan(out['fintech_share'].iloc[0])
        assert out['zero_coverage'].iloc[0] == 1


# ============================================================================
# g-controls-06: stage 51 变量标签共享构建器
# ============================================================================

class TestStage51VariableLabels:

    @pytest.fixture(autouse=True)
    def _stub_codebook(self, monkeypatch):
        """隔离盘上 codebook (hermetic): meta 查询返回空 dict。"""
        import news_process.pipeline.panel.codebook as cb
        monkeypatch.setattr(cb, 'get_variable_metadata_dict', lambda: {})

    def test_every_column_gets_nonempty_label(self):
        cols = ['target_bank', 'year', 'ln_ft_articles', 'zz_unknown_col']
        labels = mod.build_stage51_variable_labels(cols, cols)
        assert set(labels.keys()) == set(cols)
        assert all(isinstance(v, str) and v for v in labels.values())

    def test_stage51_overlay_wins(self):
        """STATA_LABELS_41 覆盖优先 (stage-51 专属语义)。"""
        cols = ['ln_ft_articles', 'zero_coverage', 'ft_n_articles_dedup']
        labels = mod.build_stage51_variable_labels(cols, cols)
        for c in cols:
            assert labels[c] == mod.STATA_LABELS_41[c]

    def test_new_columns_present_in_labels_dict(self):
        """fix 新增列 (zero_coverage / ft_n_articles_dedup) 已注册标签。"""
        assert 'zero_coverage' in mod.STATA_LABELS_41
        assert 'ft_n_articles_dedup' in mod.STATA_LABELS_41

    def test_renamed_column_falls_back_to_original_name(self):
        """sanitize 改名列的 fallback 标签 = 原始列名 (保留判别信息)。"""
        labels = mod.build_stage51_variable_labels(
            ['shortc'], ['zz_some_long_original_column_name_unknown'])
        assert labels['shortc'] == 'zz_some_long_original_column_name_unknown'

    def test_labels_within_80_utf8_bytes(self):
        cols = list(mod.STATA_LABELS_41.keys()) + ['zz_unknown_col']
        labels = mod.build_stage51_variable_labels(cols, cols)
        for c, v in labels.items():
            assert len(v.encode('utf-8')) <= 80, f'{c} 标签超 80 字节'

    def test_export_results_uses_shared_builder(self):
        """export_results 接线共享构建器 (源码级断言, 防 revert 回 17 键字典)。"""
        src = inspect.getsource(mod.export_results)
        assert 'build_stage51_variable_labels' in src
        # 旧的函数体内 17 键局部字典定义不应回归
        assert "STATA_LABELS_41 = {" not in src
