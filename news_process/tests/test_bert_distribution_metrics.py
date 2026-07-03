"""BERT 概率分布形状族 gate (2026-07-03 执行计划 BERT_DISTRIBUTION_METRICS P4-1)。

15 项 (14+1): 镜像 test_political_weight_ladder 六件套 (SSOT 字面量锚 / 跨模块
sync / agg 精确元组闭环 / stata 标签 / codebook 正负例+铁律短语+覆盖差集 /
geography 反卷入) + 本族专属 (熵构念锁 ρ==−1 / 梯子单调 / 恒等式 / WP-E 合同)。
全部合成数据纯计算, $0 无外部 API。

fixture 最小 schema = 27 列: 3 模型×3 轨×(正/负)=18 + 2 三分类×3 轨×中性=6 +
target_bank/year/日期=3 (闭环/标签/codebook 项必须全源, 否则合法缺席假红)。
⚠ finbert2 构造用**互异 |nt| 的精确小数对** — neg=1−pos 的浮点构造会产生
"|nt| 恰并列而熵差 1e-17"的秩镜像破坏 (实施冒烟实证), 真实数据为 4 位小数
存储、镜像对精确并列不受此影响。
"""

import numpy as np
import pandas as pd
import pytest
from scipy.stats import spearmanr

from news_process.pipeline.panel import bert_distribution as bd
from news_process.pipeline.panel import codebook as cb
from news_process.pipeline.panel import encode as enc
from news_process.pipeline.panel import stata_export as se
from news_process.pipeline.panel.encode import BERT_MODELS, THREE_CLASS_MODELS

TRACKS = bd.TRACKS
M3 = list(BERT_MODELS)


def _synth_df(n_extra_nan_row=True):
    """27 列全源合成 df; finbert2 概率 = 互异 |nt| 精确小数对。"""
    pos2 = [0.95, 0.80, 0.70, 0.55, 0.35, 0.15]
    neg2 = [0.05, 0.20, 0.30, 0.45, 0.65, 0.85]
    pos3 = [0.70, 0.20, 0.60, 0.34, 0.10, 0.50]
    neg3 = [0.10, 0.60, 0.20, 0.33, 0.80, 0.10]
    n = len(pos2)
    cols = {
        'target_bank': ['A'] * 3 + ['B'] * (n - 3),
        'year': [2017] * n,
        '日期': pd.to_datetime(['2017-01-05', '2017-02-10', '2017-03-15',
                                '2017-01-05', '2017-02-10', '2017-03-15']),
    }
    for b in M3:
        if b in THREE_CLASS_MODELS:
            cols[f'{b}_正面'] = pos3
            cols[f'{b}_负面'] = neg3
            cols[f'{b}_中性'] = [round(1 - p - q, 4) for p, q in zip(pos3, neg3)]
        else:
            cols[f'{b}_正面'] = pos2
            cols[f'{b}_负面'] = neg2
            cols[f'{b}_中性'] = [np.nan] * n  # 全 NaN 占位 (镜像 tone_berts 磁盘态)
    df = pd.DataFrame(cols)
    # 复制到三轨
    for b in M3:
        for trk in TRACKS:
            df[f'{b}_正面{trk}'] = df[f'{b}_正面']
            df[f'{b}_负面{trk}'] = df[f'{b}_负面']
            df[f'{b}_中性{trk}'] = df[f'{b}_中性']
        df = df.drop(columns=[f'{b}_正面', f'{b}_负面', f'{b}_中性'])
    if n_extra_nan_row:
        nan_row = {c: np.nan for c in df.columns}
        nan_row.update({'target_bank': 'B', 'year': 2017,
                        '日期': pd.Timestamp('2017-04-01')})
        df = pd.concat([df, pd.DataFrame([nan_row])], ignore_index=True)
    return df


class TestSSOTAnchors:
    """#3: SSOT 全元组字面量锚死 (漂移 = encode 聚合静默漏列 → panel 全 NaN)。"""

    def test_thresholds_tuple(self):
        assert bd.XNEG_THRESHOLDS == (0.80, 0.90, 0.95)
        assert bd.XNEG_CANONICAL == 0.90

    def test_canonical_tag_mapping(self):
        assert bd._xneg_tag(0.90) == ''      # canonical ≡ 无后缀
        assert bd._xneg_tag(0.80) == '_t80'
        assert bd._xneg_tag(0.95) == '_t95'

    def test_min_n_anchors(self):
        assert bd.SKEW_MIN_N == 10
        assert bd.IYVOL_MIN_MONTHS == 3
        assert bd.IYTREND_MIN_MONTHS == 6

    def test_declared_counts(self):
        assert len(bd.iter_intermediate_cols(M3)) == 51
        assert len(bd.iter_panel_cols(M3)) == 69
        assert len(list(bd.iter_agg_entries(M3))) == 60  # 51 面板前身 + 9 _nt_n_


class TestEntropy:
    """#1/#2: 熵边界/路径/NaN 传播 + 构念锁 (ρ==−1)。"""

    def test_onehot_and_uniform(self):
        df = pd.DataFrame({
            'finbert_cn_正面_full': [1.0, 1 / 3], 'finbert_cn_负面_full': [0.0, 1 / 3],
            'finbert_cn_中性_full': [0.0, 1 / 3],
            'finbert2_正面_full': [1.0, 0.5], 'finbert2_负面_full': [0.0, 0.5],
            'finbert2_中性_full': [np.nan, np.nan],
        })
        out = bd.compute_article_distribution_cols(df, ['finbert_cn', 'finbert2'],
                                                   THREE_CLASS_MODELS)
        assert abs(out['_ent_finbert_cn_full'][0] - 0.0) < 1e-12   # one-hot → 0
        assert abs(out['_ent_finbert_cn_full'][1] - 1.0) < 1e-12   # 均匀 → 1
        assert abs(out['_ent_finbert2_full'][0] - 0.0) < 1e-12
        assert abs(out['_ent_finbert2_full'][1] - 1.0) < 1e-12     # 二分类归一同尺度

    def test_finbert2_allnan_neutral_not_zeroed(self):
        """S-F2 陷阱: 中性列存在且全 NaN 不得把 finbert2 熵整族清零。"""
        df = _synth_df(n_extra_nan_row=False)
        out = bd.compute_article_distribution_cols(df, M3, THREE_CLASS_MODELS)
        assert out['_ent_finbert2_full'].notna().all()

    def test_nan_propagation(self):
        """np.where 反模式回归锁: NaN 概率行 → 熵/nt/xneg 全 NaN (非 0)。"""
        df = _synth_df()  # 末行全 NaN
        out = bd.compute_article_distribution_cols(df, M3, THREE_CLASS_MODELS)
        i = len(df) - 1
        for b in M3:
            assert np.isnan(out[f'_ent_{b}_full'][i])
            assert np.isnan(out[f'_nt_art_{b}_full'][i])
            assert np.isnan(out[f'_xneg_ind_{b}_full'][i])

    def test_construct_lock_spearman_minus_one(self):
        """#2: finbert2 熵 = |nt| 严格单调**递减**变换 → Spearman ρ == −1
        (⚠ 评审教训: 首轮评审给的 ρ==+1 方向是错的)。fixture |nt| 全互异。"""
        df = _synth_df(n_extra_nan_row=False)
        out = bd.compute_article_distribution_cols(df, M3, THREE_CLASS_MODELS)
        ent = out['_ent_finbert2_full']
        abs_nt = out['_nt_art_finbert2_full'].abs()
        assert abs_nt.nunique() == len(abs_nt), 'fixture |nt| 须全互异'
        rho = spearmanr(ent, abs_nt).statistic
        assert abs(rho - (-1.0)) < 1e-12, f'ρ={rho} 应精确 −1'


class TestXnegLadder:
    """#4: 单调性 (NaN-aware) + 同源同掩码。"""

    def test_monotone_and_mask(self):
        df = _synth_df()
        out = bd.compute_article_distribution_cols(df, M3, THREE_CLASS_MODELS)
        for b in M3:
            t80 = out[f'_xneg_ind_{b}_t80_full']
            t90 = out[f'_xneg_ind_{b}_full']
            t95 = out[f'_xneg_ind_{b}_t95_full']
            assert t80.isna().equals(t90.isna()) and t90.isna().equals(t95.isna())
            m = t90.notna()
            assert not (t95[m] > t90[m]).any()
            assert not (t90[m] > t80[m]).any()
            assert t80[~m].isna().all()  # 全 NaN 行三列同时 NaN

    def test_float_dtype_keeps_nan(self):
        df = _synth_df()
        out = bd.compute_article_distribution_cols(df, M3, THREE_CLASS_MODELS)
        ind = out['_xneg_ind_finbert2_full']
        assert ind.dtype == float and ind.isna().sum() == 1  # 禁 fillna(0)


class TestIdentityAndSkewMask:
    """#5: mean(_nt_art) ≡ net_tone (rtol=0, atol=1e-12); 掩码只触 skew 列。"""

    def test_identity(self):
        df = _synth_df()
        out = bd.compute_article_distribution_cols(df, M3, THREE_CLASS_MODELS)
        g = df.groupby(['target_bank', 'year'])
        for b in M3:
            nt_mean = pd.DataFrame({'nt': out[f'_nt_art_{b}_full'],
                                    'target_bank': df['target_bank'],
                                    'year': df['year']}
                                   ).groupby(['target_bank', 'year'])['nt'].mean()
            net_tone = (g[f'{b}_正面_full'].mean() - g[f'{b}_负面_full'].mean())
            assert np.allclose(nt_mean, net_tone, rtol=0, atol=1e-12)

    def test_skew_mask_via_aggregate_entries(self):
        """_nt_n_ 计数与 groupby 'skew' 的 n 同口径; SKEW_MIN_N 掩码在 encode
        post-agg (集成路径 P5-1 真跑验证; 此处锁 count 口径)。"""
        df = _synth_df()
        out = bd.compute_article_distribution_cols(df, M3, THREE_CLASS_MODELS)
        nt = pd.DataFrame({'nt': out['_nt_art_finbert2_full'],
                           'target_bank': df['target_bank'], 'year': df['year']})
        g = nt.groupby(['target_bank', 'year'])['nt']
        assert (g.count() == g.apply(lambda s: s.notna().sum())).all()


class TestXModel:
    """#6: lblhet 算术 (含 sign(0)) / disp ddof=1 / <2 模型 NaN。"""

    def test_lblhet_arithmetic(self):
        df = pd.DataFrame({
            'a_正面_full': [0.7, 0.7, 0.5], 'a_负面_full': [0.2, 0.2, 0.5],
            'b_正面_full': [0.6, 0.6, 0.7], 'b_负面_full': [0.1, 0.1, 0.2],
            'c_正面_full': [0.8, 0.1, 0.6], 'c_负面_full': [0.1, 0.8, 0.3],
        })
        out = bd.compute_xmodel_dispersion(df, ['a', 'b', 'c'])
        lbl = out['_lblhet_art_full']
        assert lbl[0] == 0.0                       # (+,+,+) 三同判
        assert abs(lbl[1] - 2 / 3) < 1e-12          # (+,+,−) 一异 → 2/3
        assert abs(lbl[2] - 2 / 3) < 1e-12          # (0,+,+): 0 vs ± 记不一致 → 2/3

    def test_zero_vs_zero_agrees(self):
        df = pd.DataFrame({
            'a_正面_full': [0.5], 'a_负面_full': [0.5],
            'b_正面_full': [0.5], 'b_负面_full': [0.5],
        })
        out = bd.compute_xmodel_dispersion(df, ['a', 'b'])
        assert out['_lblhet_art_full'][0] == 0.0   # 0 与 0 记一致

    def test_disp_nonneg_and_row_nan_under_two(self):
        df = _synth_df()
        out = bd.compute_xmodel_dispersion(df, M3)
        disp = out['_xmd_art_full']
        assert (disp.dropna() >= 0).all()
        assert np.isnan(disp[len(df) - 1])          # 全 NaN 行可用 0 模型 → NaN
        assert np.isnan(out['_lblhet_art_full'][len(df) - 1])

    def test_track_absent_under_two_models(self):
        df = pd.DataFrame({'a_正面_full': [0.7], 'a_负面_full': [0.2]})
        out = bd.compute_xmodel_dispersion(df, ['a', 'b', 'c'])
        assert '_lblhet_art_full' not in out and '_xmd_art_full' not in out


class TestIntrayear:
    """#7: 校正公式手算对拍 (含 n_t=1 月) / 双门槛边界 / 空输入合同。"""

    @staticmethod
    def _mk(months, nts, bank='A', year=2017):
        rows = []
        for mth, vals in zip(months, nts):
            for v in vals:
                rows.append({'target_bank': bank, 'year': year,
                             '日期': pd.Timestamp(f'{year}-{mth:02d}-15'),
                             'x_正面_full': (1 + v) / 2, 'x_负面_full': (1 - v) / 2})
        return pd.DataFrame(rows)

    def test_handcalc_with_single_article_month(self):
        # 3 个有效月: m1={0.4}(n=1), m2={0.2, 0.6}(n=2), m3={-0.2}(n=1)
        df = self._mk([1, 2, 3], [[0.4], [0.2, 0.6], [-0.2]])
        out = bd.compute_intrayear_dynamics(df, ['x'])
        m = np.array([0.4, 0.4, -0.2])
        var1 = m.var(ddof=1)
        s2_m2 = np.var([0.2, 0.6], ddof=1)          # 0.08
        sigma2 = (2 - 1) * s2_m2 / (2 - 1)           # 池化 = 0.08
        corr = sigma2 * (1 / 1 + 1 / 2 + 1 / 1) / 3  # 含单篇月 σ̂²/n_t
        expect = np.sqrt(max(0.0, var1 - corr))
        got = out['x_nt_iyvol_full'].iloc[0]
        assert np.isclose(got, expect, rtol=0, atol=1e-12), f'{got} != {expect}'

    def test_iyvol_thresholds(self):
        # T=2 (<3) → NaN
        df2 = self._mk([1, 2], [[0.4, 0.2], [0.6]])
        assert np.isnan(bd.compute_intrayear_dynamics(df2, ['x'])['x_nt_iyvol_full'].iloc[0])
        # T=3 全单篇月 (无 n_t≥2) → σ̂² 不可估 → NaN
        df3 = self._mk([1, 2, 3], [[0.4], [0.2], [0.6]])
        assert np.isnan(bd.compute_intrayear_dynamics(df3, ['x'])['x_nt_iyvol_full'].iloc[0])
        # T=3 且 ≥1 月 n_t≥2 → 出值
        df4 = self._mk([1, 2, 3], [[0.4, 0.2], [0.2], [0.6]])
        assert np.isfinite(bd.compute_intrayear_dynamics(df4, ['x'])['x_nt_iyvol_full'].iloc[0])

    def test_iytrend_threshold_and_sign(self):
        # 5 个有效月 → NaN
        df5 = self._mk(list(range(1, 6)), [[v] for v in (0.1, 0.2, 0.3, 0.4, 0.5)])
        assert np.isnan(bd.compute_intrayear_dynamics(df5, ['x'])['x_nt_iytrend_full'].iloc[0])
        # 6 个单调上行月 → 斜率 = 0.1/月 (闭式精确)
        df6 = self._mk(list(range(1, 7)), [[v] for v in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6)])
        got = bd.compute_intrayear_dynamics(df6, ['x'])['x_nt_iytrend_full'].iloc[0]
        assert np.isclose(got, 0.1, rtol=0, atol=1e-12)

    def test_empty_input_schema_contract(self):
        out = bd.compute_intrayear_dynamics(_synth_df().iloc[0:0], M3)
        assert list(out.columns[:2]) == ['target_bank', 'year']
        assert len(out.columns) == 20 and len(out) == 0
        metric_cols = [c for c in out.columns if c not in ('target_bank', 'year')]
        assert all(str(out[c].dtype) == 'float64' for c in metric_cols)


class TestPerModelDegradation:
    """#8: 删 finbert2 概率列 → 仅其族缺席, xmodel 退化 2 模型照产。"""

    def test_degradation(self):
        df = _synth_df().drop(columns=[c for c in _synth_df().columns
                                       if c.startswith('finbert2_')])
        out = bd.compute_article_distribution_cols(df, M3, THREE_CLASS_MODELS)
        assert not any('finbert2' in k for k in out)
        assert any('finbert_cn' in k for k in out)   # 兄弟不连坐
        xm = bd.compute_xmodel_dispersion(df, M3)
        assert '_lblhet_art_full' in xm and '_xmd_art_full' in xm
        iy = bd.compute_intrayear_dynamics(df, M3)
        assert iy['finbert2_nt_iyvol_full'].isna().all()   # 在位全 NaN (schema 合同)
        assert 'finbert2_nt_iyvol_full' in iy.columns


class TestThreeWayClosure:
    """#9: 产出键集 ∪ == 声明集 == agg 消费源集 (前缀过滤) + 精确元组。"""

    def test_closure(self):
        df = _synth_df()
        left = set(bd.compute_article_distribution_cols(df, M3, THREE_CLASS_MODELS))
        left |= set(bd.compute_xmodel_dispersion(df, M3))
        declared = set(bd.iter_intermediate_cols(M3))
        assert left == declared, f'差集: {left ^ declared}'
        agg = enc.build_aggregation_dict()   # 无参: 条目无条件在场
        srcs = {src for (src, _f) in agg.values()
                if src.startswith(('_ent_', '_xneg_ind_', '_nt_art_',
                                   '_xmd_art', '_lblhet_art'))}
        assert srcs == declared, f'差集: {srcs ^ declared}'

    def test_exact_tuples(self):
        agg = enc.build_aggregation_dict()
        for panel_col, src_col, func in bd.iter_agg_entries(M3):
            assert agg.get(panel_col) == (src_col, func), \
                f'{panel_col}: {agg.get(panel_col)} != ({src_col}, {func})'


class TestStataLabels:
    """#10: 69 列全量非 fallback 且 ≤80 UTF-8 bytes (R6: 无既有 gate 兜底)。"""

    def test_labels(self):
        cols = bd.iter_panel_cols(M3)
        labels = se.build_variable_labels(pd.DataFrame({c: [0.0] for c in cols}))
        for c in cols:
            assert labels.get(c, c) != c, f'{c} 落 fallback 裸列名'
            assert len(labels[c].encode('utf-8')) <= 80


class TestCodebook:
    """#11+#13: 显式条目全覆盖/推断正例/category 同值/铁律短语/负例匹配锁。"""

    def test_explicit_entries_cover_ssot(self):
        md = cb.get_variable_metadata_dict()
        missing = [c for c in bd.iter_panel_cols(M3) if c not in md]
        assert not missing, f'codebook 缺显式条目: {missing}'

    def test_source_stage_and_category(self):
        md = cb.get_variable_metadata_dict()
        cats = set()
        for c in bd.iter_panel_cols(M3):
            assert cb._infer_source_stage(c) == 'Stage 23'
            cats.add(md[c].category)
        assert cats == {'情感指标-BERT分布形状'}   # 三模型同值 (防 'sent' 子串分叉)

    def test_hansen_iron_rule_phrase(self):
        md = cb.get_variable_metadata_dict()
        for c in bd.iter_panel_cols(M3):
            assert 'over-identified Hansen J' in md[c].notes, f'{c} notes 缺铁律短语'

    def test_negative_matcher_lock(self):
        """#13: _BERT_MODEL_RE 全锚定不误捕 (防未来去掉 $ 锚静默回归)。"""
        for name in ('finbert_cn_net_tone_skew_full', 'fin_sent_zh_xneg_frac_t80_ss',
                     'finbert2_tone_entropy_ctx', 'fin_sent_zh_nt_iyvol_full'):
            assert cb._bert_model_match(name) is None, f'{name} 被 per-model 匹配误捕'


class TestGeographyNoRollup:
    """#12: 新列不被 bert_avg_*/dict_avg_*/llm_models_avg_* 卷入。"""

    def test_no_rollup(self):
        from news_process.pipeline.panel import geography as geo
        cols = {'target_bank': ['A', 'B'], 'year': [2017, 2018], 'n_articles': [5, 5]}
        for c in bd.iter_panel_cols(M3):
            cols[c] = [0.5, 0.4]
        out = geo.compute_composite_indicators(pd.DataFrame(cols))
        leaked = [c for c in out.columns
                  if any(k in c for k in ('entropy', 'xneg', 'skew', 'xmodel',
                                          'iyvol', 'iytrend'))
                  and c.startswith(('bert_avg', 'dict_avg', 'llm_models_avg'))]
        assert not leaked, f'geography 误卷入分布形状列: {leaked}'


class TestNamesAndResidue:
    """#14: 全列名 ≤32 / 中间列下划线前缀 / 真实产出无残留 (盘上有货才验)。"""

    def test_name_length(self):
        for c in bd.iter_panel_cols(M3):
            assert len(c) <= 32, f'{c} 超 Stata 32 字符'

    def test_intermediates_underscore_prefixed(self):
        for c in bd.iter_intermediate_cols(M3):
            assert c.startswith('_'), f'{c} 中间列须下划线前缀'
        for _p, src, _f in bd.iter_agg_entries(M3):
            pass  # 面板临时列 _nt_n_* 由 encode 掩码后即刻 drop, 集成断言在下方

    def test_no_residue_in_real_outputs(self):
        """P5-1 真跑后的落盘断言: panel 无 _nt_n_*, 文章级 parquet 无中间列。"""
        from news_process.core.config import load_config
        cfg = load_config()
        out_dir = cfg.get('paths', {}).get('output_dir') or 'data/processed'
        import os
        panel_path = os.path.join(out_dir, '40_panel_yearly.parquet')
        art_path = os.path.join(out_dir, '40_article_bank_level.parquet')
        if not (os.path.exists(panel_path) and os.path.exists(art_path)):
            pytest.skip('dev 产物未落盘 (fresh clone) — P5-1 真跑后生效')
        import pyarrow.parquet as pq
        panel_cols = set(pq.ParquetFile(panel_path).schema_arrow.names)
        art_cols = set(pq.ParquetFile(art_path).schema_arrow.names)
        assert not [c for c in panel_cols if c.startswith('_nt_n_')]
        residue = art_cols & set(bd.iter_intermediate_cols(M3))
        assert not residue, f'文章级 parquet 中间列残留: {sorted(residue)}'


class TestWpeMergeContract:
    """#15: merge 行数不变 + (bank,year) 键无重复。"""

    def test_keys_unique_and_left_merge_rowcount(self):
        df = _synth_df()
        iy = bd.compute_intrayear_dynamics(df, M3)
        assert not iy.duplicated(subset=['target_bank', 'year']).any()
        panel = pd.DataFrame({'target_bank': ['A', 'B', 'C'],
                              'year': [2017, 2017, 2017], 'roa': [1.0, 2.0, 3.0]})
        merged = panel.merge(iy, on=['target_bank', 'year'], how='left')
        assert len(merged) == len(panel)
        assert merged.loc[merged['target_bank'] == 'C',
                          'finbert_cn_nt_iyvol_full'].isna().all()  # 无新闻格天然 NaN
