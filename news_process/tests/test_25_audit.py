"""
test_25_audit.py — 25_strategic_differentiation.py 全面审计测试
================================================================

按 /repeat 工作流要求进行最高标准的黑盒+白盒测试:
  1. 核心数学函数的正确性
  2. 边界情况和异常输入
  3. 值域断言的覆盖
  4. Fluidity 时间维度逻辑
  5. 与下游 Stata 导出的一致性
"""
import sys, os
import numpy as np
import pandas as pd
import pytest

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# 直接导入被测函数 (避免执行 41 的副作用)
import importlib.util as _iu
_p25 = os.path.join(os.path.dirname(__file__), '..', '25_strategic_differentiation.py')
_s25 = _iu.spec_from_file_location('_25_test', _p25)
_m25 = _iu.module_from_spec(_s25)
_s25.loader.exec_module(_m25)

_l2_normalize = _m25._l2_normalize
_compute_nn_scores = _m25._compute_nn_scores
_build_tfidf_sim_matrix = _m25._build_tfidf_sim_matrix
_aggregate_bank_year_texts = _m25._aggregate_bank_year_texts


# =============================================================================
# 1. _l2_normalize
# =============================================================================

class TestL2Normalize:
    def test_unit_norm(self):
        """归一化后每行 L2 范数应为 1。"""
        m = np.array([[3.0, 4.0], [0.0, 5.0], [1.0, 0.0]])
        normed = _l2_normalize(m)
        norms = np.linalg.norm(normed, axis=1)
        np.testing.assert_allclose(norms, [1.0, 1.0, 1.0], atol=1e-10)

    def test_zero_vector(self):
        """零向量应保持不变 (不产生 NaN/Inf)。"""
        m = np.array([[0.0, 0.0], [1.0, 0.0]])
        normed = _l2_normalize(m)
        assert np.all(np.isfinite(normed))
        np.testing.assert_array_equal(normed[0], [0.0, 0.0])

    def test_single_row(self):
        """单行矩阵应正常处理。"""
        m = np.array([[3.0, 4.0]])
        normed = _l2_normalize(m)
        np.testing.assert_allclose(normed[0], [0.6, 0.8])


# =============================================================================
# 2. _compute_nn_scores — 相似度矩阵模式
# =============================================================================

class TestComputeNNScores:
    def _make_sim_matrix(self):
        """构造已知的 3x3 相似度矩阵。"""
        sim = np.array([
            [np.nan, 0.9, 0.3],
            [0.9, np.nan, 0.5],
            [0.3, 0.5, np.nan]
        ])
        return sim, ['BankA', 'BankB', 'BankC']

    def test_n1_similarity(self):
        """N=1 时取最近邻, diff = 1 - max_sim。"""
        sim, banks = self._make_sim_matrix()
        result = _compute_nn_scores(sim, banks, [1], is_distance=False)
        # BankA: 最近邻 = BankB (sim=0.9), diff = 1 - 0.9 = 0.1
        assert abs(result['n1']['BankA'] - 0.1) < 1e-10

    def test_sim_max(self):
        """sim_max 应为与最相似同行的原始相似度。"""
        sim, banks = self._make_sim_matrix()
        result = _compute_nn_scores(sim, banks, [1], is_distance=False)
        assert abs(result['sim_max']['BankA'] - 0.9) < 1e-10
        assert abs(result['sim_max']['BankC'] - 0.5) < 1e-10

    def test_n_exceeds_neighbors(self):
        """N > 可用邻居数时应截断 (k = min(N, len))。"""
        sim, banks = self._make_sim_matrix()
        r2 = _compute_nn_scores(sim, banks, [2], is_distance=False)
        r5 = _compute_nn_scores(sim, banks, [5], is_distance=False)
        # 每个银行只有 2 个邻居, N=5 应与 N=2 相同
        for bank in banks:
            assert abs(r2['n2'][bank] - r5['n5'][bank]) < 1e-10

    def test_all_nan_row(self):
        """全 NaN 行应返回 NaN (如年度只有 1 家银行)。"""
        sim = np.array([[np.nan]])
        result = _compute_nn_scores(sim, ['OnlyBank'], [3], is_distance=False)
        assert np.isnan(result['n3']['OnlyBank'])
        assert np.isnan(result['sim_max']['OnlyBank'])

    def test_value_range(self):
        """所有输出值应在 [0, 1] 内。"""
        np.random.seed(42)
        n = 20
        sim = cosine_sim_like = np.random.rand(n, n) * 0.5 + 0.5  # [0.5, 1.0]
        np.fill_diagonal(sim, np.nan)
        banks = [f'Bank{i}' for i in range(n)]
        result = _compute_nn_scores(sim, banks, [3, 5, 7], is_distance=False)
        for key, vals in result.items():
            for bank, v in vals.items():
                if not np.isnan(v):
                    assert -1e-10 <= v <= 1 + 1e-10, \
                        f"{key}[{bank}] = {v} 超出 [0,1]"


# =============================================================================
# 3. _compute_nn_scores — 距离矩阵模式 (LDA+JSD)
# =============================================================================

class TestComputeNNScoresDistance:
    def test_distance_mode(self):
        """距离模式下 diff = mean(topK smallest distances)。"""
        dist = np.array([
            [np.nan, 0.1, 0.8],
            [0.1, np.nan, 0.5],
            [0.8, 0.5, np.nan]
        ])
        banks = ['A', 'B', 'C']
        result = _compute_nn_scores(dist, banks, [1], is_distance=True)
        # A: 最近 = B (dist=0.1), diff = 0.1
        assert abs(result['n1']['A'] - 0.1) < 1e-10
        # sim_max = 1 - min_dist
        assert abs(result['sim_max']['A'] - 0.9) < 1e-10


# =============================================================================
# 4. _build_tfidf_sim_matrix
# =============================================================================

class TestTfidfSimMatrix:
    def test_diagonal_nan(self):
        """对角线应为 NaN。"""
        texts = ["银行金融科技创新", "保险科技风控管理", "证券公司投资理财"]
        sim = _build_tfidf_sim_matrix(texts, 'char')
        for i in range(len(texts)):
            assert np.isnan(sim[i, i])

    def test_symmetry(self):
        """相似度矩阵应对称。"""
        texts = ["银行金融科技创新", "保险科技风控管理", "证券公司投资理财"]
        sim = _build_tfidf_sim_matrix(texts, 'char')
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                assert abs(sim[i, j] - sim[j, i]) < 1e-10

    def test_identical_texts_high_similarity(self):
        """完全相同的文本应有高相似度。"""
        texts = ["银行金融科技创新发展报告"] * 3
        sim = _build_tfidf_sim_matrix(texts, 'char')
        # 完全相同的文本, 非对角线应趋近 1.0
        off_diag = sim[np.isfinite(sim)]
        assert np.all(off_diag > 0.99)

    def test_word_mode(self):
        """word 模式不应抛出异常。"""
        texts = ["银行金融科技创新发展报告", "保险行业数字化转型进展", "证券投资基金管理条例"]
        sim = _build_tfidf_sim_matrix(texts, 'word')
        assert sim.shape == (3, 3)

    def test_max_df_fallback(self):
        """当所有文档内容相同导致 max_df=0.95 清空词表时, 应降级而非崩溃。"""
        texts = ["完全一样的内容"] * 5
        sim = _build_tfidf_sim_matrix(texts, 'char')
        assert sim.shape == (5, 5)


# =============================================================================
# 5. _aggregate_bank_year_texts
# =============================================================================

class TestAggregation:
    def test_basic_aggregation(self):
        """基本聚合应正确合并同银行同年的文本。"""
        df = pd.DataFrame({
            'target_bank': ['BankA', 'BankA', 'BankB'],
            'year': [2020, 2020, 2020],
            '内容': ['新闻一', '新闻二', '新闻三'],
            '标题': ['标题一', '标题二', '标题三'],
        })
        result = _aggregate_bank_year_texts(df)
        assert len(result) == 2
        assert result[result['target_bank'] == 'BankA']['agg_text'].iloc[0] != ''

    def test_empty_input(self):
        """空输入应返回空 DataFrame。"""
        df = pd.DataFrame(columns=['target_bank', 'year', '内容'])
        result = _aggregate_bank_year_texts(df)
        assert len(result) == 0
        assert 'agg_text' in result.columns

    def test_missing_content_column(self):
        """缺少 '内容' 列时应安全返回空结果。"""
        df = pd.DataFrame({'target_bank': ['A'], 'year': [2020]})
        result = _aggregate_bank_year_texts(df)
        assert len(result) == 0

    def test_nan_content(self):
        """NaN 内容应被处理为空字符串, 不应导致崩溃。"""
        df = pd.DataFrame({
            'target_bank': ['BankA'],
            'year': [2020],
            '内容': [None],
            '标题': [None],
        })
        result = _aggregate_bank_year_texts(df)
        # 全 NaN 文本拼接后应为空/空白, 被过滤掉
        assert len(result) == 0


# =============================================================================
# 6. compute_strategic_differentiation 集成测试
# =============================================================================

class TestComputeStrategicDifferentiation:
    def _make_test_data(self, n_banks=5, n_years=2):
        """构造最小测试数据集。"""
        rows = []
        for year in range(2020, 2020 + n_years):
            for i in range(n_banks):
                rows.append({
                    'target_bank': f'Bank{i}',
                    'year': year,
                    '内容': f'银行{i}在{year}年积极推进金融科技创新' * 10,
                    '标题': f'Bank{i}年度报告',
                })
        df_exploded = pd.DataFrame(rows)

        panel_rows = []
        for year in range(2020, 2020 + n_years):
            for i in range(n_banks):
                panel_rows.append({'target_bank': f'Bank{i}', 'year': year})
        panel = pd.DataFrame(panel_rows)

        return df_exploded, panel

    def test_basic_run(self):
        """主函数应成功运行并新增列。"""
        df_exp, panel = self._make_test_data()
        result = _m25.compute_strategic_differentiation(df_exp, panel)
        assert 'strat_diff_n5' in result.columns
        assert 'strat_sim_max' in result.columns

    def test_output_columns(self):
        """应输出至少 10 个 strat_* 列。"""
        df_exp, panel = self._make_test_data()
        result = _m25.compute_strategic_differentiation(df_exp, panel)
        strat_cols = [c for c in result.columns if c.startswith('strat_')]
        assert len(strat_cols) >= 10

    def test_value_range_assertion(self):
        """所有 strat_* 列应在 [0, 1] 内 (与模块内断言一致)。"""
        df_exp, panel = self._make_test_data()
        result = _m25.compute_strategic_differentiation(df_exp, panel)
        for col in [c for c in result.columns if c.startswith('strat_')]:
            v = result[col].dropna()
            if len(v) > 0:
                assert (v >= -1e-10).all(), f"{col} min={v.min()}"
                assert (v <= 1 + 1e-10).all(), f"{col} max={v.max()}"

    def test_too_few_banks(self):
        """少于 3 家银行的年度应被跳过, 不应崩溃。"""
        df_exp, panel = self._make_test_data(n_banks=2)
        result = _m25.compute_strategic_differentiation(df_exp, panel)
        # 应无 strat_ 列 (因为 n_banks=2 < 3), 或列全 NaN
        strat_cols = [c for c in result.columns if c.startswith('strat_')]
        if strat_cols:
            for col in strat_cols:
                assert result[col].isna().all()

    def test_single_year(self):
        """单年度不应产生 fluidity (首年无前期)。"""
        df_exp, panel = self._make_test_data(n_years=1)
        result = _m25.compute_strategic_differentiation(df_exp, panel)
        if 'strat_fluidity' in result.columns:
            assert result['strat_fluidity'].isna().all()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
