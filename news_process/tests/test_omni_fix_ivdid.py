"""tests/test_omni_fix_ivdid.py — omni 审计 g-ivdid 组修复回归锁 (2026-06-11).

锁定 pipeline/panel/iv_did.py 的修复后行为 (防静默 revert):

  g-ivdid-01/-08  基期无暴露银行 share/IV 保持 NaN (原 fillna(0) 伪零)
  g-ivdid-02      base_years 池化基期 (真 _t01) + year < 基期末年 IV 前视掩码
  g-ivdid-03/-09  share>0 × shift 缺失 → IV=NaN 传播 (原零插补+exclusion 误注)
  g-ivdid-04      zone LOO 排除 'other' 伪经济圈
  g-ivdid-05      never-treated 控制组趋空警告 + csdid notyet 建议
  g-ivdid-06      HQ-based 处理分配假设披露日志
  g-ivdid-07      Int8 列减法前先 astype(float64) — 防静默回绕翻转 LOO 符号

全部用合成 DataFrame, 不依赖盘上数据, 无外部 API。

# 白话: Bartik 工具变量 = "基期的暴露份额 × 别人的当期变化"。这组测试守住:
# 基期没数据的银行该记"不知道"(NaN), 不能记 0 冒充"零暴露"; 份额必须用不晚于
# 当期的信息算(不许偷看未来); "other"这种凑数分组不能当成真实经济圈参与
# 留一法平均; Int8 小整数相减可能溢出回绕把正数变负数, 必须先转 float 再算;
# 对照组快空了、处理组按总部所在地划分这些方法论风险要在日志里明示。
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.pipeline.panel import iv_did  # noqa: E402

# ============================================================================
# 共享 helpers
# ============================================================================


def _panel(banks, years, province='北京', city='北京'):
    rows = [{'target_bank': b, 'year': y,
             'bank_province': province, 'bank_city': city}
            for b in banks for y in years]
    return pd.DataFrame(rows)


def _article(docid, bank, year, score, co='', cat='支付'):
    return {'docid': docid, 'target_bank': bank, 'year': year,
            'co_mentioned_banks': co, 'innovation_locus': cat,
            'llm_vote_score_full': float(score),
            'llm_vote_score_ctx': float(score)}


class _ListHandler(logging.Handler):
    """收集 iv_did.logger 消息 (绕过 propagate=False 的项目 logger 配置)."""

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.messages: list[str] = []

    def emit(self, record):
        self.messages.append(record.getMessage())


@pytest.fixture
def log_capture():
    handler = _ListHandler()
    iv_did.logger.addHandler(handler)
    old_level = iv_did.logger.level
    iv_did.logger.setLevel(logging.DEBUG)
    yield handler
    iv_did.logger.setLevel(old_level)
    iv_did.logger.removeHandler(handler)


# ============================================================================
# g-ivdid-01 / -08: 基期无暴露银行 share/IV 保持 NaN (伪零消除)
# ============================================================================


class TestNoBaseExposureNaN:
    GROUP_MAP = {'bank_a': 'soe', 'bank_b': 'joint', 'bank_x': 'city'}

    def _run(self):
        panel = _panel(['bank_a', 'bank_b', 'bank_x'], [2020, 2021])
        articles = pd.DataFrame([
            _article(1, 'bank_a', 2020, 1, co='bank_b'),
            _article(2, 'bank_b', 2020, -1, co='bank_a'),
            _article(3, 'bank_a', 2021, 1),
            _article(4, 'bank_b', 2021, -1),
            # bank_x 基期 2020 无文章, 仅 2021 有
            _article(5, 'bank_x', 2021, 0),
        ])
        return iv_did.compute_bartik_iv(panel, articles, self.GROUP_MAP,
                                        group_prefix='t', base_year=2020)

    def test_share_is_nan_not_zero_for_no_base_bank(self):
        out = self._run()
        x = out[out['target_bank'] == 'bank_x']
        share_cols = [c for c in out.columns if c.startswith('bartik_t_share_')]
        assert share_cols, "share 列缺失"
        for c in share_cols:
            assert x[c].isna().all(), f"基期无文章银行 {c} 应 NaN (非伪零), got {x[c].tolist()}"

    def test_iv_is_nan_not_zero_for_no_base_bank(self):
        out = self._run()
        x = out[out['target_bank'] == 'bank_x']
        for track in ('_full', '_ctx'):
            col = f'bartik_t_iv{track}'
            assert x[col].isna().all(), (
                f"基期无文章银行 {col} 应 NaN (伪零消除), got {x[col].tolist()}")

    def test_legit_banks_share_row_sum_is_one_and_iv_valid(self):
        """有基期暴露的银行不受影响: share 行和=1, IV 正常计算."""
        out = self._run()
        a = out[out['target_bank'] == 'bank_a']
        share_cols = [c for c in out.columns if c.startswith('bartik_t_share_')]
        row_sum = a[share_cols].sum(axis=1)
        assert np.allclose(row_sum, 1.0), f"bank_a share 行和应=1, got {row_sum.tolist()}"
        # bank_a share_joint=1, 2021 年组 joint 的 LOO (排除 a) = bank_b 的 -1
        a_2021 = a.loc[a['year'] == 2021, 'bartik_t_iv_full'].iloc[0]
        assert abs(a_2021 - (-1.0)) < 1e-9, f"bank_a 2021 IV 应=-1.0, got {a_2021}"

    def test_unmapped_bank_zero_cross_exposure_share_iv_nan(self):
        """own_group=='other' (未映射银行) 且基期零跨组暴露 → share/IV NaN.

        旧行为: one-hot 兜底退化为全 0 share 行 (own group 不在 kept groups)
        → Σshare=0≠1, IV 输出伪零 (g-ivdid-01 同根边角)。
        """
        group_map = {'bank_a': 'soe', 'bank_b': 'joint'}  # bank_u 未映射 → 'other'
        panel = _panel(['bank_a', 'bank_b', 'bank_u'], [2020, 2021])
        articles = pd.DataFrame([
            _article(1, 'bank_a', 2020, 1, co='bank_b'),
            _article(2, 'bank_b', 2020, -1, co='bank_a'),
            # bank_u 基期有文章但零 co-mention → total=0 且 own_group='other'
            _article(3, 'bank_u', 2020, 0),
            _article(4, 'bank_a', 2021, 1),
            _article(5, 'bank_b', 2021, -1),
        ])
        out = iv_did.compute_bartik_iv(panel, articles, group_map,
                                       group_prefix='t', base_year=2020)
        u = out[out['target_bank'] == 'bank_u']
        share_cols = [c for c in out.columns if c.startswith('bartik_t_share_')]
        for c in share_cols:
            assert u[c].isna().all(), (
                f"未映射银行零跨组暴露 {c} 应 NaN (非全 0), got {u[c].tolist()}")
        for track in ('_full', '_ctx'):
            col = f'bartik_t_iv{track}'
            assert u[col].isna().all(), (
                f"未映射银行 {col} 应 NaN (伪零消除), got {u[col].tolist()}")
        # mapped 银行的 own-group one-hot 兜底不受影响 (T=2 退化披露行为保留)
        a = out[out['target_bank'] == 'bank_a']
        assert np.allclose(a[share_cols].sum(axis=1), 1.0)


class TestFintechNoBaseExposureNaN:
    CAT_MAP = {'支付': 'pay', '借贷': 'lend', '其他': 'other'}

    def _run(self):
        panel = _panel(['bank_a', 'bank_b', 'bank_x', 'bank_z'], [2020, 2021])
        articles = pd.DataFrame([
            _article(1, 'bank_a', 2020, 1, cat='支付'),
            _article(2, 'bank_b', 2020, -1, cat='借贷'),
            # bank_x 基期文章全为兜底类别 'other' → total=0 → share 未定义
            _article(3, 'bank_x', 2020, 0, cat='其他'),
            # bank_z 基期无文章
            _article(4, 'bank_a', 2021, 1, cat='支付'),
            _article(5, 'bank_b', 2021, -1, cat='支付'),
            _article(6, 'bank_z', 2021, 0, cat='支付'),
        ])
        return iv_did.compute_bartik_iv_fintech(
            panel, articles, self.CAT_MAP, group_prefix='ft',
            base_year=2020, category_col='innovation_locus')

    def test_all_other_base_bank_share_iv_nan(self):
        out = self._run()
        x = out[out['target_bank'] == 'bank_x']
        for g in ('pay', 'lend'):
            col = f'bartik_ft_share_{g}'
            assert x[col].isna().all(), (
                f"基期文章全 'other' 的银行 {col} 应 NaN, got {x[col].tolist()}")
        assert x['bartik_ft_iv_full'].isna().all(), "全-other 基期银行 IV 应 NaN"

    def test_no_base_bank_share_iv_nan(self):
        out = self._run()
        z = out[out['target_bank'] == 'bank_z']
        assert z['bartik_ft_share_pay'].isna().all(), "基期无文章银行 share 应 NaN"
        assert z['bartik_ft_iv_full'].isna().all(), "基期无文章银行 IV 应 NaN"

    def test_legit_bank_unaffected(self):
        out = self._run()
        a = out[out['target_bank'] == 'bank_a']
        assert abs(a['bartik_ft_share_pay'].iloc[0] - 1.0) < 1e-9
        # a 的 2021 IV = share_pay(1.0) × shift_pay(LOO 排除 a):
        # pay 组 2021 剩 bank_b(-1) + bank_z(0) → (-1+0)/2 = -0.5
        a_2021 = a.loc[a['year'] == 2021, 'bartik_ft_iv_full'].iloc[0]
        assert abs(a_2021 - (-0.5)) < 1e-9, f"bank_a 2021 IV 应=-0.5, got {a_2021}"


# ============================================================================
# g-ivdid-02: base_years 池化 + 前视掩码
# ============================================================================


class TestBaseYearsPoolingAndForesightMask:
    GROUP_MAP = {'bank_a': 'soe', 'bank_b': 'joint', 'bank_x': 'city'}

    def _articles(self):
        return pd.DataFrame([
            # bank_x: 2020 co-mention soe, 2021 co-mention joint → 池化 share 0.5/0.5
            _article(1, 'bank_x', 2020, 0, co='bank_a'),
            _article(2, 'bank_x', 2021, 0, co='bank_b'),
            # shift 来源 (排除 x 后): a (soe) / b (joint) 每年 1 篇 score=1
            _article(3, 'bank_a', 2020, 1),
            _article(4, 'bank_b', 2020, 1),
            _article(5, 'bank_a', 2021, 1),
            _article(6, 'bank_b', 2021, 1),
        ])

    def test_base_years_pools_shares(self):
        """base_years=[2020,2021] 时 share 在两年并集上池化 (真 _t01)."""
        panel = _panel(['bank_a', 'bank_b', 'bank_x'], [2020, 2021])
        out = iv_did.compute_bartik_iv(panel, self._articles(), self.GROUP_MAP,
                                       group_prefix='t',
                                       base_years=[2020, 2021])
        x = out[out['target_bank'] == 'bank_x']
        assert abs(x['bartik_t_share_soe'].iloc[0] - 0.5) < 1e-9
        assert abs(x['bartik_t_share_joint'].iloc[0] - 0.5) < 1e-9

    def test_base_years_single_equals_base_year(self):
        """base_years=[y] 与 base_year=y 语义一致 (向后兼容)."""
        panel = _panel(['bank_a', 'bank_b', 'bank_x'], [2020, 2021])
        out_a = iv_did.compute_bartik_iv(panel, self._articles(), self.GROUP_MAP,
                                         group_prefix='t', base_year=2020)
        out_b = iv_did.compute_bartik_iv(panel, self._articles(), self.GROUP_MAP,
                                         group_prefix='t', base_years=[2020])
        cols = [c for c in out_a.columns if c.startswith('bartik_t_')]
        for c in cols:
            pd.testing.assert_series_equal(out_a[c], out_b[c], check_names=False)

    def test_pooled_base_masks_pre_base_rows(self):
        """池化基期 [2020,2021]: year<2021 的行 share 测自未来 → IV NaN."""
        panel = _panel(['bank_a', 'bank_b', 'bank_x'], [2020, 2021])
        out = iv_did.compute_bartik_iv(panel, self._articles(), self.GROUP_MAP,
                                       group_prefix='t',
                                       base_years=[2020, 2021])
        x = out[out['target_bank'] == 'bank_x']
        assert x.loc[x['year'] == 2020, 'bartik_t_iv_full'].isna().all(), (
            "year=2020 < 基期末年 2021 应被前视掩码置 NaN")
        # 2021 行有效: IV = 0.5×shift_soe + 0.5×shift_joint = 0.5×1 + 0.5×1 = 1.0
        x_2021 = x.loc[x['year'] == 2021, 'bartik_t_iv_full'].iloc[0]
        assert abs(x_2021 - 1.0) < 1e-9, f"x 2021 IV 应=1.0, got {x_2021}"

    def test_pre_base_year_rows_masked_single_base(self):
        """单基期 T0=2020, 面板含 2019 行 → 2019 IV NaN (T=18 全量 latent 触发)."""
        panel = _panel(['bank_a', 'bank_b', 'bank_x'], [2019, 2020, 2021])
        articles = pd.concat([
            self._articles(),
            pd.DataFrame([_article(7, 'bank_a', 2019, 1),
                          _article(8, 'bank_b', 2019, 1)]),
        ], ignore_index=True)
        out = iv_did.compute_bartik_iv(panel, articles, self.GROUP_MAP,
                                       group_prefix='t', base_year=2020)
        pre = out[out['year'] == 2019]
        for track in ('_full', '_ctx'):
            assert pre[f'bartik_t_iv{track}'].isna().all(), (
                f"2019 < T0=2020 的行 bartik_t_iv{track} 应 NaN (share 前视)")
        # 非 pre-T0 行不受影响
        x_2021 = out.loc[(out['target_bank'] == 'bank_x') & (out['year'] == 2021),
                         'bartik_t_iv_full'].iloc[0]
        assert np.isfinite(x_2021)

    def test_fintech_pre_base_year_rows_masked(self):
        """compute_bartik_iv_fintech 同口径前视掩码."""
        panel = _panel(['bank_a', 'bank_b'], [2019, 2020, 2021])
        articles = pd.DataFrame([
            _article(1, 'bank_a', 2019, 1, cat='支付'),
            _article(2, 'bank_b', 2019, 1, cat='支付'),
            _article(3, 'bank_a', 2020, 1, cat='支付'),
            _article(4, 'bank_b', 2020, 1, cat='支付'),
            _article(5, 'bank_a', 2021, 1, cat='支付'),
            _article(6, 'bank_b', 2021, 1, cat='支付'),
        ])
        out = iv_did.compute_bartik_iv_fintech(
            panel, articles, {'支付': 'pay'}, group_prefix='ft',
            base_year=2020, category_col='innovation_locus')
        assert out.loc[out['year'] == 2019, 'bartik_ft_iv_full'].isna().all()
        assert out.loc[out['year'] == 2021, 'bartik_ft_iv_full'].notna().all()

    def test_fintech_base_years_pools_shares(self):
        """fintech 变体的 base_years 池化."""
        panel = _panel(['bank_a', 'bank_x'], [2020, 2021])
        articles = pd.DataFrame([
            _article(1, 'bank_x', 2020, 0, cat='支付'),
            _article(2, 'bank_x', 2021, 0, cat='借贷'),
            _article(3, 'bank_a', 2020, 1, cat='支付'),
            _article(4, 'bank_a', 2021, 1, cat='借贷'),
        ])
        out = iv_did.compute_bartik_iv_fintech(
            panel, articles, {'支付': 'pay', '借贷': 'lend'}, group_prefix='ft',
            base_years=[2020, 2021], category_col='innovation_locus')
        x = out[out['target_bank'] == 'bank_x']
        assert abs(x['bartik_ft_share_pay'].iloc[0] - 0.5) < 1e-9
        assert abs(x['bartik_ft_share_lend'].iloc[0] - 0.5) < 1e-9


# ============================================================================
# g-ivdid-03 / -09: share>0 × shift 缺失 → NaN 传播; share==0 维度不受影响
# ============================================================================


class TestShiftMissingNaNPropagation:
    def test_share_pos_shift_missing_propagates_nan(self):
        """share>0 的组该年 LOO 不可计算 (组内仅剩自身) → IV=NaN 而非 0."""
        group_map = {'bank_a': 'soe', 'bank_b': 'joint'}
        panel = _panel(['bank_a', 'bank_b'], [2020, 2021])
        articles = pd.DataFrame([
            # a 基期 co-mention b → share_joint=1
            _article(1, 'bank_a', 2020, 1, co='bank_b'),
            _article(2, 'bank_b', 2020, -1, co='bank_a'),
            # 2021: joint 组只有 b 自己的 0 篇 → 对 a 的 shift_joint 不可计算?
            # 不: a∉joint, b 的文章是 joint 组全集; 2021 joint 组无任何文章
            # → shift_joint(2021)=NaN, a 的 share_joint=1 → IV NaN
            _article(3, 'bank_a', 2021, 1),
        ])
        out = iv_did.compute_bartik_iv(panel, articles, group_map,
                                       group_prefix='t', base_year=2020)
        a_2021 = out.loc[(out['target_bank'] == 'bank_a') & (out['year'] == 2021),
                         'bartik_t_iv_full']
        assert a_2021.isna().all(), (
            f"share_joint=1 × shift_joint(2021) 缺失应传播 NaN, got {a_2021.tolist()}")

    def test_share_zero_dim_with_missing_shift_does_not_contaminate(self):
        """share==0 的维度 shift 缺失 → 0 贡献, 其余维度正常计算 IV."""
        group_map = {'bank_a': 'soe', 'bank_b': 'joint', 'bank_c': 'city'}
        panel = _panel(['bank_a', 'bank_b', 'bank_c'], [2020, 2021])
        articles = pd.DataFrame([
            # a 基期只 co-mention b → share_joint=1, share_city=0, share_soe=0
            _article(1, 'bank_a', 2020, 1, co='bank_b'),
            _article(2, 'bank_b', 2020, -1, co='bank_a'),
            _article(3, 'bank_c', 2020, 0, co='bank_a'),
            # 2021: joint 有 b 文章 (shift_joint 可计算); city 组无文章 (shift_city NaN)
            _article(4, 'bank_b', 2021, -1),
        ])
        out = iv_did.compute_bartik_iv(panel, articles, group_map,
                                       group_prefix='t', base_year=2020)
        a_2021 = out.loc[(out['target_bank'] == 'bank_a') & (out['year'] == 2021),
                         'bartik_t_iv_full'].iloc[0]
        # share_city=0 × shift_city(NaN) 不应污染: IV = 1×(-1) = -1
        assert abs(a_2021 - (-1.0)) < 1e-9, (
            f"share=0 维度的缺失 shift 不应污染 IV, expect -1.0 got {a_2021}")

    def test_exclusion_restriction_comment_removed(self):
        """误注 'exclusion restriction' 已从 fillna(0) 零插补处删除."""
        src = Path(iv_did.__file__).read_text(encoding='utf-8')
        assert '等价于 exclusion restriction' not in src, (
            "iv_did.py 仍含 '等价于 exclusion restriction' 误注 (g-ivdid-03)")


# ============================================================================
# g-ivdid-04: zone LOO 排除 'other' 伪经济圈
# ============================================================================


class TestZoneOtherExcluded:
    def test_other_zone_outputs_nan(self):
        """bank_province 未映射 (→'other') 的银行 zone LOO 应 NaN, 即使样本充足."""
        rows = []
        # 5 家未映射省份银行 (伪 'other' 圈) + 3 家北京银行 (真 京津冀)
        for i in range(5):
            rows.append({'target_bank': f'hk_{i}', 'year': 2020,
                         'bank_province': '香港', 'bank_city': '香港'})
        for i in range(3):
            rows.append({'target_bank': f'bj_{i}', 'year': 2020,
                         'bank_province': '北京', 'bank_city': '北京'})
        panel = pd.DataFrame(rows)
        articles = pd.DataFrame(
            [_article(i, f'hk_{i % 5}', 2020, 1) for i in range(10)]
            + [_article(100 + i, f'bj_{i % 3}', 2020, 1) for i in range(9)]
        )
        out = iv_did.compute_zone_leave1out(panel, articles, min_group_size=3)

        hk = out[out['target_bank'].str.startswith('hk_')]
        assert (hk['bank_zone'] == 'other').all()
        assert hk['zone_leave1out_tone_full'].isna().all(), (
            "'other' 伪经济圈银行的 zone LOO 应 NaN (g-ivdid-04)")
        # 真实经济圈不受影响
        bj = out[out['target_bank'].str.startswith('bj_')]
        assert bj['zone_leave1out_tone_full'].notna().all(), "京津冀真圈 LOO 应有效"
        assert np.allclose(bj['zone_leave1out_tone_full'], 1.0)


# ============================================================================
# g-ivdid-07: Int8 减法回绕防线 (float64 转换前移到操作数)
# ============================================================================


def _int8_loo_articles(year, extra_rows=None):
    """构造 Int8 回绕触发场: a 65×(+1), b 65×(+1), x 6×(−1) 于同 (组, year).

    组和 = 124 ∈ Int8 (pandas 按值降型保持 Int8), x 的 LOO 余数 = 130 > 127
    → 旧代码 Int8−Int8 回绕为 −126, LOO=−0.969; 新代码 LOO=+1.0。
    """
    rows = []
    docid = 0
    for bank, n, score in [('bank_a', 65, 1), ('bank_b', 65, 1), ('bank_x', 6, -1)]:
        for _ in range(n):
            rows.append({'docid': docid, 'target_bank': bank, 'year': year,
                         'co_mentioned_banks': '', 'innovation_locus': '支付',
                         '_score': score})
            docid += 1
    if extra_rows:
        for r in extra_rows:
            r = dict(r)
            r['_score'] = r.pop('score')
            rows.append(r)
    df = pd.DataFrame(rows)
    df['llm_vote_score_full'] = pd.array(df['_score'].tolist(), dtype='Int8')
    df['llm_vote_score_ctx'] = pd.array(df['_score'].tolist(), dtype='Int8')
    return df.drop(columns=['_score'])


def test_int8_wraparound_precondition_documented():
    """坐实环境前提: masked Int8 groupby sum 按值降型 + Int8 减法静默回绕.

    若未来 pandas 修复降型行为本测试 skip (fix(omni-g-ivdid-07) 防线仍正确,
    只是不再被触发)。
    """
    df = pd.DataFrame({'k': ['a'] * 136,
                       'v': pd.array([1] * 130 + [-1] * 6, dtype='Int8')})
    agg = df.groupby('k')['v'].agg(['sum', 'count'])
    if str(agg['sum'].dtype) != 'Int8':
        pytest.skip('pandas 已不再按值降型 Int8 groupby sum — 回绕前提不再成立')
    assert agg['sum'].iloc[0] == 124
    own = pd.Series([-6], index=['a'], dtype='Int8')
    # 旧代码模式 (减法先于转换): 124−(−6) 回绕为 −126
    assert (agg['sum'] - own).iloc[0] == -126
    # 修复模式 (操作数先转 float64): 130
    assert (agg['sum'].astype('float64') - own.astype('float64')).iloc[0] == 130.0


class TestInt8NoWraparound:
    def test_zone_leave1out_int8_no_sign_flip(self):
        panel = _panel(['bank_a', 'bank_b', 'bank_x'], [2020])
        articles = _int8_loo_articles(2020)
        out = iv_did.compute_zone_leave1out(panel, articles, min_group_size=3)
        x_loo = out.loc[out['target_bank'] == 'bank_x',
                        'zone_leave1out_tone_full'].iloc[0]
        # LOO = (124−(−6)) / (136−6) = 130/130 = 1.0; 回绕旧值为 −126/130 ≈ −0.969
        assert abs(x_loo - 1.0) < 1e-9, (
            f"bank_x zone LOO 应=+1.0 (Int8 回绕会给出 −0.969), got {x_loo}")

    def test_bartik_iv_int8_no_sign_flip(self):
        group_map = {'bank_a': 'soe', 'bank_b': 'soe', 'bank_x': 'soe'}
        panel = _panel(['bank_a', 'bank_b', 'bank_x'], [2020, 2021])
        articles = _int8_loo_articles(
            2021,
            extra_rows=[{'docid': 999, 'target_bank': 'bank_x', 'year': 2020,
                         'co_mentioned_banks': 'bank_a', 'innovation_locus': '支付',
                         'score': 1}])
        out = iv_did.compute_bartik_iv(panel, articles, group_map,
                                       group_prefix='t', base_year=2020)
        x_2021 = out.loc[(out['target_bank'] == 'bank_x') & (out['year'] == 2021),
                         'bartik_t_iv_full'].iloc[0]
        # share_soe=1 × shift_soe(2021)=130/130=1.0
        assert abs(x_2021 - 1.0) < 1e-9, (
            f"bank_x 2021 Bartik IV 应=+1.0 (Int8 回绕会翻转符号), got {x_2021}")

    def test_bartik_iv_fintech_int8_no_sign_flip(self):
        panel = _panel(['bank_a', 'bank_b', 'bank_x'], [2020, 2021])
        articles = _int8_loo_articles(
            2021,
            extra_rows=[{'docid': 999, 'target_bank': 'bank_x', 'year': 2020,
                         'co_mentioned_banks': '', 'innovation_locus': '支付',
                         'score': 1}])
        out = iv_did.compute_bartik_iv_fintech(
            panel, articles, {'支付': 'pay'}, group_prefix='ft',
            base_year=2020, category_col='innovation_locus')
        x_2021 = out.loc[(out['target_bank'] == 'bank_x') & (out['year'] == 2021),
                         'bartik_ft_iv_full'].iloc[0]
        assert abs(x_2021 - 1.0) < 1e-9, (
            f"bank_x 2021 fintech Bartik IV 应=+1.0, got {x_2021}")


# ============================================================================
# g-ivdid-05 / -06: merge_policy_shocks 披露日志
# ============================================================================


class TestPolicyShockDisclosures:
    @pytest.fixture
    def policy_file(self, tmp_path, monkeypatch):
        p = tmp_path / "policy_shocks.json"
        p.write_text(json.dumps({
            "policy_X": {
                "prefix": "px",
                "groups": [{"year": 2020, "cities": ["北京", "上海", "深圳"]}],
            },
        }, ensure_ascii=False), encoding='utf-8')
        monkeypatch.setitem(iv_did.CONFIG['paths'], 'policy_shocks_file', str(p))
        return p

    def _did_panel(self):
        banks = [
            ('t1', '北京', '北京'), ('t2', '北京', '北京'), ('t3', '上海', '上海'),
            ('t4', '上海', '上海'), ('t5', '深圳', '广东'), ('t6', '深圳', '广东'),
            # 仅 2 家 never-treated → 触发控制组趋空警告
            ('c1', '武汉', '湖北'), ('c2', '长沙', '湖南'),
        ]
        rows = [{'target_bank': b, 'year': y, 'bank_city': c, 'bank_province': p}
                for b, c, p in banks for y in (2019, 2020, 2021)]
        return pd.DataFrame(rows)

    def test_never_treated_scarcity_warning_and_notyet(self, policy_file, log_capture):
        out = iv_did.merge_policy_shocks(self._did_panel())
        msgs = '\n'.join(log_capture.messages)
        # g-ivdid-05: never-treated 趋空警告
        assert 'never-treated 控制组仅 2 家' in msgs, (
            f"应触发 never-treated 趋空警告, 日志:\n{msgs}")
        # g-ivdid-05: csdid 命令推荐 notyet
        assert 'notyet' in msgs, f"csdid 日志应推荐 notyet 控制组, 日志:\n{msgs}"
        # DID 列本身行为不变 (gvar 编码正确)
        assert (out.loc[out['target_bank'] == 't1', 'px_treat_year'] == 2020).all()
        assert (out.loc[out['target_bank'] == 'c1', 'px_treat_year'] == 0).all()

    def test_hq_based_assignment_disclosure_logged(self, policy_file, log_capture):
        iv_did.merge_policy_shocks(self._did_panel())
        msgs = '\n'.join(log_capture.messages)
        assert 'HQ-based' in msgs, (
            f"应输出 HQ-based 处理分配假设披露 (g-ivdid-06), 日志:\n{msgs}")

    def test_no_warning_when_control_group_large(self, policy_file, log_capture):
        """控制组充足 (≥5 家) 时不应误报趋空警告."""
        panel = self._did_panel()
        extra = pd.DataFrame([
            {'target_bank': f'c_extra_{i}', 'year': y,
             'bank_city': '南昌', 'bank_province': '江西'}
            for i in range(5) for y in (2019, 2020, 2021)])
        panel = pd.concat([panel, extra], ignore_index=True)
        iv_did.merge_policy_shocks(panel)
        msgs = '\n'.join(log_capture.messages)
        assert 'never-treated 控制组仅' not in msgs, "控制组充足时不应警告"
