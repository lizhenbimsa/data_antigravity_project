"""
test_omni_fix_encode_collab.py — omni 审计修复回归锁 (g-encode-collab 组, 2026-06-11)
================================================================================
锁定 encode_collab 族 confirmed/confirmed-latent 缺陷的修复后行为, 防静默 revert。
全部使用合成 DataFrame, 不依赖盘上大数据、不调外部 API。

覆盖:
  -01 D4 residual *_frac 分母改 both_valid 计数 (与分子同域); n_bothvalid < 5
      (含 ==0 假零) → NaN; 新增 n_articles_{dim}_bothvalid 覆盖披露列;
      上游标签列缺失时回退 legacy 物理分母 + n_articles < 5 门
  -02 _normalize_label gate 兼容 pandas 3 str dtype / StringDtype (脏标签清洗
      不再静默 no-op); both_valid 改 isin canonical 白名单 (修 invariant ii)
  -03/-05/-06 frac_amb_articles_{full,ctx} 分母改 clarity-valid 计数; ≥2 门同步
      迁移 valid 域; 全 NaN 轨 (median=NaN) → NaN 而非全员假零
  -04/-07 apply_v3_5_2 幂等 pre-drop (无 *_x/*_y 幻影列, 陈旧同名列被刷新)
  -08 bank_news_clarity paper_spec.yaml Step 2 权重描述与实现对齐
      (media_authority_weight × herd_weight_ctx, 非 mention_density)
  KNOWN-OPEN② apply_v3_5_1 frozen-median sidecar 接线 (首跑计算并持久化,
      后续跑读冻结值, 阈值不随样本组成漂移)

# 白话: 这组测试管"比例怎么算才诚实": 算分歧比例时, 分子分母必须数同一批
# 文章(两轨都有标签的那批); 样本太少或全缺时给 NaN 而不是假装是 0; 脏标签
# (多空格/换行)先洗干净再比对; 同一函数跑两遍结果要一样, 不能越跑列越多;
# 中位数阈值第一次算好就冻结存盘, 以后换样本也不漂移。
"""
import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

# 注入 news_process 父目录, 解析 ``news_process.*`` (与既有测试一致)
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.panel import encode_collab as ec  # noqa: E402

# ============================================================================
# 辅助函数
# ============================================================================

def _mk_subst_df(rows: list[tuple[str, int, object, object]]) -> pd.DataFrame:
    """rows: (target_bank, year, subst_full, subst_ctx) — 仅 subst 维 (其余维缺列跳过)."""
    return pd.DataFrame(
        rows, columns=['target_bank', 'year',
                       'innovation_substantiveness_full',
                       'innovation_substantiveness_ctx'],
    )


def _mk_panel(keys: list[tuple[str, int]], n_articles: list[int] | None = None) -> pd.DataFrame:
    panel = pd.DataFrame(keys, columns=['target_bank', 'year'])
    if n_articles is not None:
        panel['n_articles'] = n_articles
    return panel


# ============================================================================
# -01: D4 residual frac 分母 = both_valid 计数
# ============================================================================

class TestD4BothValidDenominator:
    def _build(self):
        rows = []
        # bank A 2017: 10 篇物理; 8 篇 both_valid (其中 1 篇 disagree), 2 篇 ctx NaN
        rows += [('A', 2017, '实质性', '实质性')] * 7
        rows += [('A', 2017, '实质性', '象征性')]          # disagree
        rows += [('A', 2017, '实质性', np.nan)] * 2        # 缺 ctx → 不进 both_valid
        # bank B 2017: 6 篇物理, ctx 全 NaN → n_bothvalid = 0
        rows += [('B', 2017, '象征性', np.nan)] * 6
        # bank C 2017: 6 篇物理, 4 篇 both_valid (1 disagree) → n_bothvalid=4 < 5
        rows += [('C', 2017, '实质性', '实质性')] * 3
        rows += [('C', 2017, '象征性', '实质性')]          # disagree (quietworker 方向)
        rows += [('C', 2017, '实质性', np.nan)] * 2
        df = _mk_subst_df(rows)
        ec.derive_residual_signals(df)
        panel = _mk_panel([('A', 2017), ('B', 2017), ('C', 2017)],
                          n_articles=[10, 6, 6])
        diag = ec.aggregate_d4_panel(df, panel)
        return panel, diag

    def test_frac_denominator_is_bothvalid_not_physical(self):
        panel, _ = self._build()
        row_a = panel[panel['target_bank'] == 'A'].iloc[0]
        # 旧 bug: 1/10 = 0.1 (物理分母); 修后: 1/8 = 0.125 (both_valid 分母)
        assert row_a['subst_disagree_frac'] == 1.0 / 8.0
        assert row_a['n_articles_subst_bothvalid'] == 8

    def test_bothvalid_zero_yields_nan_not_fake_zero(self):
        panel, _ = self._build()
        row_b = panel[panel['target_bank'] == 'B'].iloc[0]
        assert row_b['n_articles_subst_bothvalid'] == 0
        # 旧 bug: mean() 分母=物理 6 → 0.0 假零; 修后 NaN
        assert pd.isna(row_b['subst_disagree_frac'])
        assert pd.isna(row_b['subst_freerider_frac'])
        assert pd.isna(row_b['subst_quietworker_frac'])

    def test_small_sample_gate_uses_valid_domain(self):
        panel, _ = self._build()
        row_c = panel[panel['target_bank'] == 'C'].iloc[0]
        # 物理 6 ≥ 5 但 both_valid 4 < 5 → 门在 valid 域 → NaN
        assert row_c['n_articles_subst_bothvalid'] == 4
        assert pd.isna(row_c['subst_disagree_frac'])
        # count 列不受门控 (绝对计数仍披露)
        assert row_c['n_articles_subst_disagree'] == 1

    def test_coverage_disclosure_column_exists(self):
        panel, diag = self._build()
        assert 'n_articles_subst_bothvalid' in panel.columns
        assert diag['residual_skipped'] is False

    def test_fallback_physical_denominator_when_label_cols_missing(self):
        # 标签源列缺失 (无法重建 both_valid) → 回退 legacy 物理分母 + n_articles<5 门
        df = pd.DataFrame({
            'target_bank': ['A'] * 6 + ['B'] * 3,
            'year': [2017] * 9,
            'subst_disagree': [True, False, False, False, False, False,
                               True, False, False],
            'subst_freerider': [False] * 9,
            'subst_quietworker': [False] * 9,
        })
        panel = _mk_panel([('A', 2017), ('B', 2017)], n_articles=[6, 3])
        ec.aggregate_d4_panel(df, panel)
        row_a = panel[panel['target_bank'] == 'A'].iloc[0]
        row_b = panel[panel['target_bank'] == 'B'].iloc[0]
        assert row_a['subst_disagree_frac'] == 1.0 / 6.0   # legacy mean 语义
        assert pd.isna(row_b['subst_disagree_frac'])        # 物理 n<5 门
        assert 'n_articles_subst_bothvalid' not in panel.columns


# ============================================================================
# -02: _normalize_label pandas-3 str dtype + both_valid isin 白名单
# ============================================================================

class TestNormalizeLabelDtypeGate:
    def test_default_str_dtype_is_cleaned(self):
        # pandas 3 默认字符串 dtype (str); pandas 2 下为 object — 两者都须清洗
        s = pd.Series([' 实质性 ', '象征　性', '底层\n技术'])
        out = ec._normalize_label(s)
        assert list(out) == ['实质性', '象征性', '底层技术']

    def test_object_dtype_still_cleaned(self):
        s = pd.Series([' 实质性 ', np.nan], dtype=object)
        out = ec._normalize_label(s)
        assert out.iloc[0] == '实质性'
        assert pd.isna(out.iloc[1])

    def test_string_extension_dtype_cleaned(self):
        s = pd.Series([' 实质性 ', '象征性\t'], dtype='string')
        out = ec._normalize_label(s)
        assert list(out) == ['实质性', '象征性']

    def test_non_string_dtype_passthrough(self):
        s = pd.Series([np.nan, np.nan], dtype='float64')
        out = ec._normalize_label(s)
        assert out is s  # 原样返回

    def test_compute_cell_id_with_dirty_str_dtype_labels(self):
        # 端到端: 脏标签 (空白/全角空格) 在 pandas-3 str dtype 下仍归到合法 cell
        df = pd.DataFrame({
            'innovation_substantiveness_full': [' 实质性 '],
            'innovation_locus_full': ['底层　技术'],
            'innovation_collab_mode_full': ['自主研发\n'],
        })
        cell = ec.compute_cell_id(df, 'full')
        assert cell.iloc[0] == 1  # (0,0,0) baseline

    def test_noncanonical_label_excluded_from_both_valid(self):
        # 非 canonical 但非 NaN 的脏标签 → both_valid False → 三信号全 False
        # (旧 notna() 口径会令 disagree=True 而 freerider+quietworker=0, 破 invariant ii)
        df = _mk_subst_df([
            ('A', 2017, '实质性', '不适用'),
            ('A', 2017, '实质性', '象征性'),
        ])
        ec.derive_residual_signals(df)
        assert not df['subst_disagree'].iloc[0]
        assert df['subst_disagree'].iloc[1]
        # invariant (ii): freerider + quietworker == disagree (逐行)
        lhs = df['subst_freerider'].astype(int) + df['subst_quietworker'].astype(int)
        assert (lhs == df['subst_disagree'].astype(int)).all()


# ============================================================================
# -03/-05/-06: frac_amb_articles 分母 = clarity-valid 计数
# ============================================================================

def _mk_clarity_df(rows):
    """rows: (bank, year, amb_full, amb_ctx); 其余 clarity 列填常数 (非测试焦点)."""
    df = pd.DataFrame(rows, columns=['target_bank', 'year',
                                     'clarity_frac_ambiguous_full',
                                     'clarity_frac_ambiguous_ctx'])
    for c in ('clarity_frac_definite_full', 'clarity_frac_definite_ctx',
              'clarity_clarity_score_full', 'clarity_clarity_score_ctx'):
        df[c] = 0.5
    return df


class TestFracAmbValidDenominator:
    def test_denominator_excludes_nan_clarity_articles(self):
        # bank A: 4 篇物理, 3 篇 clarity-valid (1 篇 ≥ median) → 1/3 (旧 bug: 1/4)
        df = _mk_clarity_df([
            ('A', 2017, 0.8, 0.1),
            ('A', 2017, 0.2, 0.1),
            ('A', 2017, 0.4, 0.1),
            ('A', 2017, np.nan, 0.1),   # 空文/零 token (tone_words 显式 NaN)
        ])
        panel = _mk_panel([('A', 2017)])
        ec.aggregate_clarity_panel(df, panel, median_amb_d0=0.5, median_amb_d0_ctx=0.5)
        assert panel['frac_amb_articles_full'].iloc[0] == 1.0 / 3.0

    def test_valid_count_below_2_gate(self):
        # 物理 5 篇 ≥ 2, 但 clarity-valid 仅 1 篇 → 门在 valid 域 → NaN
        df = _mk_clarity_df([
            ('A', 2017, 0.9, 0.1),
            ('A', 2017, np.nan, 0.1),
            ('A', 2017, np.nan, 0.1),
            ('A', 2017, np.nan, 0.1),
            ('A', 2017, np.nan, 0.1),
        ])
        panel = _mk_panel([('A', 2017)])
        ec.aggregate_clarity_panel(df, panel, median_amb_d0=0.5, median_amb_d0_ctx=0.5)
        assert pd.isna(panel['frac_amb_articles_full'].iloc[0])
        # ctx 轨 5/5 valid, 0 篇 ≥ 0.5 → 真零 (非门控)
        assert panel['frac_amb_articles_ctx'].iloc[0] == 0.0

    def test_all_nan_track_yields_nan_not_fake_zero(self):
        # ctx 轨全 NaN → in-sample median=NaN → 旧 bug: s>=NaN 全 False → 全员假零 0.0
        df = _mk_clarity_df([
            ('A', 2017, 0.8, np.nan),
            ('A', 2017, 0.2, np.nan),
            ('A', 2017, 0.6, np.nan),
        ])
        panel = _mk_panel([('A', 2017)])
        diag = ec.aggregate_clarity_panel(df, panel, median_amb_d0=0.5,
                                          median_amb_d0_ctx=None)
        assert pd.isna(panel['frac_amb_articles_ctx'].iloc[0])
        assert ec._is_nan(diag['median_amb_d0_ctx'])
        # full 轨不受影响: 2/3 篇 ≥ 0.5
        assert panel['frac_amb_articles_full'].iloc[0] == 2.0 / 3.0


# ============================================================================
# -04/-07: apply_v3_5_2 幂等 pre-drop
# ============================================================================

def _mk_v352_df():
    df = pd.DataFrame({
        'target_bank': ['A', 'A', 'B'],
        'year': [2017, 2017, 2017],
    })
    # v3.10.0: 6 LM 子集 × 3 轨 (full/ctx/ss)。
    for k in ('uncert', 'litig', 'constr', 'modal_strong', 'modal_weak', 'complexity'):
        for t in ('full', 'ctx', 'ss'):
            df[f'{k}_frac_{t}'] = [0.1, 0.3, 0.5]
    # 2026-07-03 §5 D2: FLS 双基名 (frac_fls 双门 canonical + frac_fls_fonly 单门稳健臂)
    for base in ('frac_fls', 'frac_fls_fonly'):
        for t in ('full', 'ctx', 'ss'):
            df[f'{base}_{t}'] = [0.2, 0.4, 0.6]
    return df


class TestApplyV352Idempotent:
    def test_stale_column_refreshed_no_phantom_suffixes(self):
        df = _mk_v352_df()
        panel = _mk_panel([('A', 2017), ('B', 2017)])
        panel['uncert_frac_full'] = [999.0, 999.0]  # 陈旧同名列 (二次调用场景)
        diag = ec.apply_v3_5_2(df, panel)
        phantom = [c for c in panel.columns if c.endswith('_x') or c.endswith('_y')]
        assert phantom == [], f"幻影列泄漏: {phantom}"
        # 陈旧值被新聚合覆盖 (A: mean(0.1, 0.3) = 0.2)
        assert panel.loc[panel['target_bank'] == 'A', 'uncert_frac_full'].iloc[0] == 0.2
        assert 'uncert_frac_full' in diag['v3_5_2_lm_added']

    def test_double_invocation_idempotent(self):
        df = _mk_v352_df()
        panel = _mk_panel([('A', 2017), ('B', 2017)])
        ec.apply_v3_5_2(df, panel)
        cols_first = list(panel.columns)
        vals_first = panel['frac_fls_full'].tolist()
        diag2 = ec.apply_v3_5_2(df, panel)  # 二次调用
        assert list(panel.columns) == cols_first
        assert panel['frac_fls_full'].tolist() == vals_first
        assert diag2['v3_5_2_skipped_reason'] is None

    def test_fls_dual_basename_six_cols(self):
        # 2026-07-03 §5 D2 gate (终审 #7: 聚合环 graceful skip 使基名错拼/回退时面板列
        # 无声缺席 — fls_added 计数 3→6 断言把静默吞列固化为红灯)
        df = _mk_v352_df()
        panel = _mk_panel([('A', 2017), ('B', 2017)])
        diag = ec.apply_v3_5_2(df, panel)
        fls_added = diag['v3_5_2_fls_added']
        assert len(fls_added) == 6, f'FLS 双基名应产 6 面板列, 实际 {sorted(fls_added)}'
        for t in ('full', 'ctx', 'ss'):
            assert f'frac_fls_fonly_{t}' in panel.columns
        # 数值锚: A 银行 mean(0.2, 0.4) = 0.3 (同名直聚合语义)
        assert panel.loc[panel['target_bank'] == 'A', 'frac_fls_fonly_full'].iloc[0] == \
            pytest.approx(0.3)


# ============================================================================
# KNOWN-OPEN②: apply_v3_5_1 frozen-median sidecar 接线
# ============================================================================

class TestFrozenMedianSidecar:
    SIDECAR = os.path.join('data', 'processed', 'v3_5_1_constants.json')

    def _df(self, amb_values):
        rows = [('A', 2017, v, v) for v in amb_values]
        return _mk_clarity_df(rows)

    def test_first_run_computes_and_persists(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        df = self._df([0.1, 0.2, 0.3, 0.4])
        panel = _mk_panel([('A', 2017)])
        diag = ec.apply_v3_5_1(df, panel)
        assert diag['median_amb_d0'] == 0.25  # in-sample 首跑
        with open(self.SIDECAR, encoding='utf-8') as f:
            sidecar = json.load(f)
        assert sidecar['median_amb_d0'] == 0.25
        assert sidecar['median_amb_d0_ctx'] == 0.25

    def test_second_run_uses_frozen_threshold(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        panel1 = _mk_panel([('A', 2017)])
        ec.apply_v3_5_1(self._df([0.1, 0.2, 0.3, 0.4]), panel1)  # 冻结 0.25
        # 第二跑: 样本组成漂移 (in-sample median 应为 0.85), 但须用冻结 0.25
        df2 = self._df([0.7, 0.8, 0.9, 1.0])
        panel2 = _mk_panel([('A', 2017)])
        diag2 = ec.apply_v3_5_1(df2, panel2)
        assert diag2['median_amb_d0'] == 0.25  # 冻结值, 非 0.85
        # 二值化用冻结阈值: 4/4 篇 ≥ 0.25 → 1.0 (若误用 0.85 则为 0.5)
        assert panel2['frac_amb_articles_full'].iloc[0] == 1.0
        with open(self.SIDECAR, encoding='utf-8') as f:
            sidecar = json.load(f)
        assert sidecar['median_amb_d0'] == 0.25  # sidecar 不被第二跑覆盖

    def test_explicit_threshold_overrides_in_sample(self):
        # aggregate_clarity_panel 直接传冻结值 → 不做 in-sample 重算
        df = self._df([0.7, 0.8, 0.9, 1.0])
        panel = _mk_panel([('A', 2017)])
        diag = ec.aggregate_clarity_panel(df, panel, median_amb_d0=0.25,
                                          median_amb_d0_ctx=0.25)
        assert diag['median_amb_d0'] == 0.25
        assert panel['frac_amb_articles_full'].iloc[0] == 1.0


# ============================================================================
# -08: bank_news_clarity paper_spec.yaml 权重描述与实现对齐
# ============================================================================

class TestPaperSpecWeightClaim:
    def test_spec_no_longer_claims_mention_density_weight(self):
        spec_path = os.path.join(
            _PROJECT_PARENT, 'news_process', 'papers', 'bank_news_clarity',
            'paper_spec.yaml',
        )
        text = open(spec_path, encoding='utf-8').read()
        # 旧错误声称 (主 treatment 权重 = mention_density) 必须移除
        assert '权重 w_i = mention_density' not in text
        # 新描述与 encode_collab.aggregate_clarity_panel::_track_weight 实现一致
        assert 'media_authority_weight × herd_weight_ctx' in text

    def test_implementation_has_no_mention_density(self):
        # 防双向漂移: 实现侧确实不存在 mention_density 加权分支
        src = open(ec.__file__, encoding='utf-8').read()
        assert 'mention_density' not in src
