"""
test_omni_fix_net_brok.py — omni 审计修复回归锁 (g-net-brok 组, 2026-06-11)
================================================================================
锁定 pipeline/panel/network_brokerage.py 5 条 confirmed 缺陷的修复后行为
(fix omni-g-net-brok-01..-05), 防静默 revert。全部使用合成 DataFrame /
合成二分图, 不依赖盘上大数据、不调外部 API。

覆盖:
  -01 industry_neg_shock 同期 LOO 在年 FE 下与自身 neg_ratio 精确共线
      → 新增 industry_neg_shock_lag1 滞后变体 + docstring/模块头披露
  -02 非连通图幂迭代残渣 (1e-180 级伪值) → 按连通分量分别计算 (分量内归一),
      孤立点/微小分量 NaN
  -03 neg_ratio 无最小篇数守门 → min_count 参数化守门 (默认 5, 对齐项目惯例)
  -04 latent: eigenvector_centrality_numpy ARPACK 随机初值非确定 → 删除
      numpy 路径, 统一确定性迭代法 (跨 run 逐位一致)
  -05 own ratio NaN 时 shock 整体置 NaN → 同行均值天然 leave-out 直接可算

# 白话: "媒体-银行网络"指标的修复锁: 图不连通时, 每块单独算中心度, 不让
# 算法残渣给孤立小块塞进 1e-180 这种伪数值; 只发过一两篇新闻的银行不够格
# 进"行业负面冲击"的平均(样本太少比率失真); 算中心度统一用确定性算法,
# 每次跑结果一字不差; 同期冲击和自身负面率在年固定效应下数学上完全共线,
# 所以补了滞后一年的版本并在文档里写明白。
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# 注入 news_process 父目录, 解析 ``news_process.*`` (与既有测试一致)
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

nx = pytest.importorskip('networkx')

from news_process.pipeline.panel import network_brokerage as nb  # noqa: E402

# ============================================================================
# 共用合成数据
# ============================================================================

def _df_exploded_disconnected(year: int = 2020) -> pd.DataFrame:
    """3 个连通分量的媒体-银行二分图素材:
      分量1 (5 节点, P5 路径 A-M1-B-M2-C): 大分量, B 为枢纽
      分量2 (2 节点, M3-D): 微小分量 (< _MIN_COMPONENT_SIZE) → D 应为 NaN
      分量3 (3 节点, E-M4-F): 恰达门槛的星型分量
    """
    rows = [
        ('M1', 'A'), ('M1', 'B'), ('M2', 'B'), ('M2', 'C'),
        ('M3', 'D'),
        ('M4', 'E'), ('M4', 'F'),
    ]
    return pd.DataFrame({
        '媒体(中文)': [m for m, _ in rows],
        'target_bank': [b for _, b in rows],
        'year': year,
    })


def _panel(banks, year: int = 2020) -> pd.DataFrame:
    return pd.DataFrame({'target_bank': list(banks), 'year': year})


# ============================================================================
# fix-02: 按连通分量计算特征向量中心度 (分量内归一, 微小分量 NaN)
# ============================================================================

class TestComponentEigenCent:
    def test_tiny_component_bank_is_nan(self):
        out = nb.compute_brokerage_centrality(
            _panel('ABCDEF'), _df_exploded_disconnected())
        s = out.set_index('target_bank')['brokerage_eigen_cent']
        # 微小分量 (M3-D, 2 节点) → NaN, 不再获得幂迭代残渣伪值
        assert pd.isna(s['D']), "微小分量银行应为 NaN (fix omni-g-net-brok-02)"

    def test_no_power_iteration_residue(self):
        """旧 bug: 非主分量值低至 3.2e-180 (纯迭代衰减残渣)。
        修复后所有非 NaN 值都是分量内归一的真中心度, 远离 0。"""
        out = nb.compute_brokerage_centrality(
            _panel('ABCDEF'), _df_exploded_disconnected())
        s = out.set_index('target_bank')['brokerage_eigen_cent']
        for b in 'ABCEF':
            assert pd.notna(s[b]), f"大分量银行 {b} 应有值"
            assert s[b] > 1e-6, (
                f"银行 {b} 值 {s[b]:.3e} 疑似幂迭代残渣 (应 >> 0)")

    def test_within_component_l2_normalization(self):
        G = nb.build_media_bank_bipartite(_df_exploded_disconnected(), 2020)
        vals = nb._eigenvector_centrality_by_component(G, 2020)
        # 微小分量节点 (M3/D) 无值
        assert 'D' not in vals and 'M3' not in vals
        # 每个被计算分量内 (媒体+银行) 的 L2 范数 = 1 (分量内归一)
        n_computed = 0
        for comp in nx.connected_components(G):
            comp_vals = [vals[n] for n in comp if n in vals]
            if comp_vals:
                n_computed += 1
                norm = float(np.sqrt(np.sum(np.square(comp_vals))))
                assert np.isclose(norm, 1.0, atol=1e-4), (
                    f"分量 {sorted(comp)} L2 范数 {norm} != 1")
        assert n_computed == 2, "应恰有 2 个大分量被计算"

    def test_star_component_exact_value(self):
        """E-M4-F 星型分量 (P3): 特征向量 = (0.5, 1/sqrt2, 0.5) → 银行端 0.5。"""
        out = nb.compute_brokerage_centrality(
            _panel('ABCDEF'), _df_exploded_disconnected())
        s = out.set_index('target_bank')['brokerage_eigen_cent']
        assert np.isclose(s['E'], 0.5, atol=1e-3)
        assert np.isclose(s['F'], 0.5, atol=1e-3)

    def test_hub_bank_highest_within_component(self):
        """分量1 是 P5 路径 A-M1-B-M2-C, 中点 B (双媒体覆盖) 中心度最高。"""
        out = nb.compute_brokerage_centrality(
            _panel('ABCDEF'), _df_exploded_disconnected())
        s = out.set_index('target_bank')['brokerage_eigen_cent']
        assert s['B'] > s['A'] and s['B'] > s['C']


# ============================================================================
# fix-04: 删除 ARPACK 随机初值路径, 统一确定性迭代法
# ============================================================================

class TestDeterministicCentrality:
    def test_repeat_runs_bitwise_identical_disconnected(self):
        df = _df_exploded_disconnected()
        runs = []
        for _ in range(3):
            out = nb.compute_brokerage_centrality(_panel('ABCDEF'), df.copy())
            runs.append(out.sort_values('target_bank')
                        ['brokerage_eigen_cent'].to_numpy())
        assert np.array_equal(runs[0], runs[1], equal_nan=True)
        assert np.array_equal(runs[0], runs[2], equal_nan=True)

    def test_repeat_runs_bitwise_identical_connected(self):
        """连通图 (单分量) 也走同一确定性迭代路径 — 旧 numpy/ARPACK 路径
        (随机 v0) 同图重算非逐位一致, 是 latent 非确定源。"""
        rows = [('M1', 'A'), ('M1', 'B'), ('M2', 'B'), ('M2', 'C')]
        df = pd.DataFrame({
            '媒体(中文)': [m for m, _ in rows],
            'target_bank': [b for _, b in rows],
            'year': 2020,
        })
        G = nb.build_media_bank_bipartite(df, 2020)
        assert nx.is_connected(G), "前提: 该图须连通"
        v1 = nb._eigenvector_centrality_by_component(G, 2020)
        v2 = nb._eigenvector_centrality_by_component(G, 2020)
        assert set(v1) == set(v2)
        for n in v1:
            assert v1[n] == v2[n], f"节点 {n} 重算不逐位一致"

    def test_arpack_random_v0_path_removed(self):
        """源码静态锁: 不得回归 eigenvector_centrality_numpy 调用
        (scipy ARPACK eigs 无 v0 → 随机初始向量) 及 is_connected 分流。"""
        src = Path(nb.__file__).read_text(encoding='utf-8')
        assert 'eigenvector_centrality_numpy(' not in src, (
            "ARPACK 随机初值路径不得回归 (fix omni-g-net-brok-04)")
        assert 'nx.is_connected(' not in src, (
            "is_connected 整图分流已删, 统一按连通分量计算")


# ============================================================================
# fix-03: neg_ratio 最小篇数守门 (min_count 参数化, 默认 5)
# ============================================================================

class TestNegRatioMinCountGuard:
    @staticmethod
    def _panel_one_year() -> pd.DataFrame:
        # A: 10 篇 0 负 (ratio=0.0); B: 10 篇 2 负 (0.2); C: 1 篇 1 负 ({0,1} 极值)
        # n_articles (物理) 故意 != llm_valid: 锁定分母用 LLM-valid 口径
        return pd.DataFrame({
            'target_bank': ['A', 'B', 'C'],
            'year': [2020] * 3,
            'neg_count_full': [0, 2, 1],
            'n_articles': [12, 11, 2],
            'n_articles_llm_valid': [10, 10, 1],
        })

    def test_single_article_bank_excluded_from_index(self):
        out = nb.compute_industry_neg_shock(self._panel_one_year())
        s = out.set_index('target_bank')['industry_neg_shock']
        # C (1 篇 < min_count=5) 被守门, 其 ratio=1.0 极值不再独家抬升指数
        assert np.isclose(s['A'], 0.2), "A 的 LOO 应只含 B (=0.2)"
        assert np.isclose(s['B'], 0.0), "B 的 LOO 应只含 A (=0.0)"
        # C 自身 ratio 被守门置 NaN → 获同行均值 (fix-05 联动) = (0+0.2)/2
        assert np.isclose(s['C'], 0.1)

    def test_min_count_parameterized(self):
        out = nb.compute_industry_neg_shock(self._panel_one_year(), min_count=1)
        s = out.set_index('target_bank')['industry_neg_shock']
        # min_count=1 → C (ratio=1.0) 重新进入: A 的 LOO = (0.2+1.0)/2 = 0.6
        assert np.isclose(s['A'], 0.6)
        assert np.isclose(s['C'], 0.1), "C 的 LOO = (0.0+0.2)/2"

    def test_default_min_count_is_5(self):
        """默认值对齐项目 min-n>=5 惯例 (attention_media._ATTN_MIN_ARTICLES)。"""
        import inspect
        sig = inspect.signature(nb.compute_industry_neg_shock)
        assert sig.parameters['min_count'].default == 5


# ============================================================================
# fix-05: own ratio NaN 时 shock = 同行均值 (天然 leave-out), 不再整体 NaN
# ============================================================================

class TestOwnNanShockComputable:
    def test_zero_article_bank_gets_peer_mean(self):
        panel = pd.DataFrame({
            'target_bank': ['A', 'B', 'Z'],
            'year': [2020] * 3,
            'neg_count_full': [0, 2, 0],
            'n_articles': [12, 11, 0],
            'n_articles_llm_valid': [10, 10, 0],  # Z 零文章 → own NaN
        })
        out = nb.compute_industry_neg_shock(panel)
        s = out.set_index('target_bank')['industry_neg_shock']
        # 旧行为: Z 为 NaN (listwise 剔除); 修复后 = 同行均值 (0+0.2)/2
        assert np.isclose(s['Z'], 0.1), (
            "own NaN 时同行均值天然 leave-out, 不应 NaN (fix omni-g-net-brok-05)")

    def test_single_valid_peer_still_computable_for_nan_own(self):
        panel = pd.DataFrame({
            'target_bank': ['A', 'Z'],
            'year': [2020] * 2,
            'neg_count_full': [2, 0],
            'n_articles': [12, 0],
            'n_articles_llm_valid': [10, 0],
        })
        out = nb.compute_industry_neg_shock(panel)
        s = out.set_index('target_bank')['industry_neg_shock']
        # A 自身有效但仅 1 家有效银行 → LOO 不可算, 保留 NaN (原行为)
        assert pd.isna(s['A'])
        # Z own NaN 且 total_n=1 → 同行均值 = 0.2
        assert np.isclose(s['Z'], 0.2)

    def test_all_invalid_year_stays_nan(self):
        panel = pd.DataFrame({
            'target_bank': ['A', 'B'],
            'year': [2020] * 2,
            'neg_count_full': [0, 0],
            'n_articles': [0, 0],
            'n_articles_llm_valid': [0, 0],
        })
        out = nb.compute_industry_neg_shock(panel)
        assert out['industry_neg_shock'].isna().all()


# ============================================================================
# fix-01: industry_neg_shock_lag1 滞后变体 + 年 FE 共线披露
# ============================================================================

class TestLag1VariantAndDisclosure:
    @staticmethod
    def _panel_multi_year() -> pd.DataFrame:
        # 3 银行 × 2 年, 全部过守门 (10 篇)
        return pd.DataFrame({
            'target_bank': ['A', 'A', 'B', 'B', 'C', 'C'],
            'year': [2020, 2021] * 3,
            'neg_count_full': [1, 2, 3, 4, 5, 0],
            'n_articles': [11, 12, 13, 14, 15, 10],
            'n_articles_llm_valid': [10] * 6,
        })

    def test_lag1_column_values(self):
        out = nb.compute_industry_neg_shock(self._panel_multi_year())
        assert 'industry_neg_shock_lag1' in out.columns
        s = out.set_index(['target_bank', 'year'])
        # 首年无前期 → NaN
        assert pd.isna(s.loc[('A', 2020), 'industry_neg_shock_lag1'])
        # 2021 的 lag1 = 2020 的同期值: A=(0.3+0.5)/2=0.4, B=0.3, C=0.2
        assert np.isclose(s.loc[('A', 2021), 'industry_neg_shock_lag1'], 0.4)
        assert np.isclose(s.loc[('B', 2021), 'industry_neg_shock_lag1'], 0.3)
        assert np.isclose(s.loc[('C', 2021), 'industry_neg_shock_lag1'], 0.2)

    def test_lag1_alignment_with_unsorted_input(self):
        """输入行序打乱时, lag1 仍按 (target_bank, year) 语义对齐且不重排面板。"""
        base = self._panel_multi_year()
        shuffled = base.sample(frac=1.0, random_state=7)
        out = nb.compute_industry_neg_shock(shuffled.copy())
        assert list(out.index) == list(shuffled.index), "函数不得重排输入行序"
        s = out.set_index(['target_bank', 'year'])['industry_neg_shock_lag1']
        assert np.isclose(s[('A', 2021)], 0.4)
        assert pd.isna(s[('B', 2020)])

    def test_within_year_affine_collinearity_is_documented_fact(self):
        """披露的代数恒等式回归锁: 同年内 corr(shock, own ratio) = -1 精确
        (这正是同期水平项在年 FE 下不可用、必须用 lag1 的原因)。"""
        panel = pd.DataFrame({
            'target_bank': ['A', 'B', 'C', 'D'],
            'year': [2020] * 4,
            'neg_count_full': [1, 3, 5, 7],
            'n_articles': [11, 12, 13, 14],
            'n_articles_llm_valid': [10] * 4,
        })
        out = nb.compute_industry_neg_shock(panel)
        ratio = (panel['neg_count_full'] / panel['n_articles_llm_valid']).to_numpy()
        shock = out['industry_neg_shock'].to_numpy()
        corr = np.corrcoef(shock, ratio)[0, 1]
        assert np.isclose(corr, -1.0, atol=1e-12)

    def test_disclosure_in_docstrings(self):
        """披露锁: 模块头 + 两个函数 docstring 必须写明年 FE 共线与 lag1 替代。"""
        assert 'industry_neg_shock_lag1' in nb.__doc__
        assert '年 FE' in nb.__doc__
        fn_doc = nb.compute_industry_neg_shock.__doc__
        assert 'industry_neg_shock_lag1' in fn_doc
        assert '精确共线' in fn_doc
        # fire_sale: 交乘项 vs 主效应区分披露
        fs_doc = nb.compute_fire_sale_interaction.__doc__
        assert 'industry_neg_shock_lag1' in fs_doc

    def test_fire_sale_unaffected_and_still_computes(self):
        panel = pd.DataFrame({
            'target_bank': ['A', 'A', 'B', 'B'],
            'year': [2020, 2021] * 2,
            'brokerage_eigen_cent': [0.5, 0.6, 0.2, 0.3],
            'industry_neg_shock': [0.1, 0.2, 0.3, 0.4],
        })
        out = nb.compute_fire_sale_interaction(panel)
        s = out.set_index(['target_bank', 'year'])['brokerage_fire_sale']
        assert np.isclose(s[('A', 2021)], 0.5 * 0.2)  # cent(t-1) × shock(t)
        assert pd.isna(s[('A', 2020)])
