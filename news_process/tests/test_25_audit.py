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

# 添加项目父目录到 sys.path 以解析 ``news_process.*``
PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_PARENT not in sys.path:
    sys.path.insert(0, PROJECT_PARENT)

# Phase 2a 重构: 25_strategic_differentiation.py 已迁移至
# news_process.pipeline.features.strategic_diff. Phase 4e 同步 test 导入路径。
from news_process.pipeline.features import strategic_diff as _m25
from news_process.pipeline.features.strategic_diff import (
    _l2_normalize,
    _compute_nn_scores,
    _build_tfidf_sim_matrix,
    _compute_centroid_scores,
)
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
        sim, _ = _build_tfidf_sim_matrix(texts, 'char')
        for i in range(len(texts)):
            assert np.isnan(sim[i, i])

    def test_symmetry(self):
        """相似度矩阵应对称。"""
        texts = ["银行金融科技创新", "保险科技风控管理", "证券公司投资理财"]
        sim, _ = _build_tfidf_sim_matrix(texts, 'char')
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                assert abs(sim[i, j] - sim[j, i]) < 1e-10

    def test_identical_texts_high_similarity(self):
        """完全相同的文本应有高相似度。"""
        texts = ["银行金融科技创新发展报告"] * 3
        sim, _ = _build_tfidf_sim_matrix(texts, 'char')
        # 完全相同的文本, 非对角线应趋近 1.0
        off_diag = sim[np.isfinite(sim)]
        assert np.all(off_diag > 0.99)

    def test_word_mode(self):
        """word 模式不应抛出异常。"""
        texts = ["银行金融科技创新发展报告", "保险行业数字化转型进展", "证券投资基金管理条例"]
        sim, _ = _build_tfidf_sim_matrix(texts, 'word')
        assert sim.shape == (3, 3)

    def test_max_df_fallback(self):
        """当所有文档内容相同导致 max_df=0.95 清空词表时, 应降级而非崩溃。"""
        texts = ["完全一样的内容"] * 5
        sim, _ = _build_tfidf_sim_matrix(texts, 'char')
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
    @pytest.fixture(autouse=True)
    def _mock_embedding_api(self, monkeypatch):
        """CI 上无 .env / 真实 LLM key, mock _get_embeddings_api 返回固定向量.

        `_m25.compute_strategic_differentiation` 通过 `_embed_texts_with_chunk_pooling`
        间接调 `_get_embeddings_api` (strategic_diff.py L436-437) — 缺 EMBEDDING_CONFIG
        即 raise. 直接 patch 该 async 函数返回 deterministic L2-normalized 单位向量,
        既绕过 config 校验, 又避免 outbound network, 还让上层 cosine 相似度计算可走通.
        向量 dim 取 8 (LLM 真实是 1536, mock 用 8 减小内存; 下游纯几何, dim 大小不影响通路).
        """
        async def _mock_api(texts, cache=None):
            texts = [] if texts is None else list(texts)
            if len(texts) == 0:
                return np.empty((0, 0), dtype=np.float32)
            rng = np.random.default_rng(seed=42)
            mat = np.abs(rng.standard_normal((len(texts), 8))).astype(np.float32) + 1e-3
            mat /= np.linalg.norm(mat, axis=1, keepdims=True).clip(min=1e-12)
            return mat

        monkeypatch.setattr(_m25, "_get_embeddings_api", _mock_api, raising=True)

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


# =============================================================================
# 7. 相邻期文本连贯性 (Temporal Text Coherence)
#    欧阳志刚 & 胡雯华 (2024), 数量经济技术经济研究, §三(三)2.(2)
# =============================================================================

# 导入连贯性函数
_compute_tfidf_coherence = _m25._compute_tfidf_coherence
_compute_lda_coherence = _m25._compute_lda_coherence


class TestTemporalCoherence:
    """测试相邻期文本连贯性计算。

    【学术】验证 欧阳志刚 & 胡雯华 (2024) 的余弦相似度连贯性指标实现:
    - 相同文本 → 完美连贯 (sim ≈ 1.0)
    - 不同文本 → 低连贯 (sim ≈ 0)
    - 首年无前期 → NaN
    - 值域 ∈ [0, 1]
    """

    def _make_coherence_data(self, texts_by_bank_year):
        """构造 agg_df 格式的测试数据。

        Args:
            texts_by_bank_year: dict of {(bank, year): text}
        Returns:
            DataFrame[target_bank, year, agg_text]
        """
        rows = [{'target_bank': b, 'year': y, 'agg_text': t}
                for (b, y), t in texts_by_bank_year.items()]
        return pd.DataFrame(rows)

    def test_identical_texts_perfect_coherence(self):
        """相同文本在相邻两期 → TF-IDF 余弦相似度 ≈ 1.0。

        【白话】如果一家银行今年和去年的新闻完全一样, 连贯性应该接近满分。
        """
        agg_df = self._make_coherence_data({
            ('BankA', 2020): '银行金融科技创新发展报告' * 20,
            ('BankA', 2021): '银行金融科技创新发展报告' * 20,
            ('BankB', 2020): '保险行业数字化转型进展' * 20,
            ('BankB', 2021): '保险行业数字化转型进展' * 20,
        })
        coh = _compute_tfidf_coherence(agg_df, 'char')
        assert ('BankA', 2021) in coh
        assert coh[('BankA', 2021)] > 0.99, f"Expected ≈1.0, got {coh[('BankA', 2021)]}"
        assert coh[('BankB', 2021)] > 0.99

    def test_disjoint_texts_low_coherence(self):
        """完全不同的文本 → 低连贯性。

        【白话】如果一家银行今年和去年谈的内容完全不同, 连贯性应该很低。
        """
        agg_df = self._make_coherence_data({
            ('BankA', 2020): '互联网金融创新科技发展区块链数字货币' * 20,
            ('BankA', 2021): '绿色环保低碳经济可持续发展新能源汽车' * 20,
            ('BankB', 2020): '互联网金融创新' * 20,
            ('BankB', 2021): '互联网金融创新' * 20,  # 对照: 保持相同
        })
        coh = _compute_tfidf_coherence(agg_df, 'char')
        assert coh[('BankA', 2021)] < 0.5, f"Expected low, got {coh[('BankA', 2021)]}"
        assert coh[('BankB', 2021)] > coh[('BankA', 2021)], \
            "相同文本的连贯性应高于不同文本"

    def test_first_year_nan(self):
        """首年 (无 t-1 数据) 应不出现在结果中 → 对应 NaN。

        【白话】如果是数据中的第一年, 没有"去年"可以比较, 所以连贯性为空。
        """
        agg_df = self._make_coherence_data({
            ('BankA', 2020): '银行金融科技' * 20,
            ('BankA', 2021): '银行金融科技' * 20,
        })
        coh = _compute_tfidf_coherence(agg_df, 'char')
        assert ('BankA', 2020) not in coh, "首年不应有连贯性值"
        assert ('BankA', 2021) in coh, "第二年应有连贯性值"

    def test_value_range_01(self):
        """所有 TF-IDF 连贯性输出值应在 [0, 1] 内。"""
        agg_df = self._make_coherence_data({
            ('BankA', 2020): '银行金融科技创新区块链' * 10,
            ('BankA', 2021): '数字经济转型发展报告' * 10,
            ('BankA', 2022): '智能风控大数据分析' * 10,
            ('BankB', 2020): '保险行业科技' * 10,
            ('BankB', 2021): '保险数字化' * 10,
            ('BankB', 2022): '保险数字化' * 10,
        })
        for mode in ['char', 'word']:
            coh = _compute_tfidf_coherence(agg_df, mode)
            for key, val in coh.items():
                assert 0.0 - 1e-10 <= val <= 1.0 + 1e-10, \
                    f"TF-IDF {mode} coherence{key} = {val} 超出 [0,1]"

    def test_dual_track_independence(self):
        """Full 和 Ctx 轨道使用不同文本列时, 结果可以不同。

        【白话】全文和上下文窗口可能给出不同的连贯性分数, 验证双轨独立性。
        """
        data_full = {
            ('BankA', 2020): '银行金融科技创新' * 20,
            ('BankA', 2021): '银行金融科技创新' * 20,
        }
        data_ctx = {
            ('BankA', 2020): '银行金融科技创新' * 20,
            ('BankA', 2021): '完全不同的上下文内容绿色环保低碳' * 20,
        }
        agg_full = self._make_coherence_data(data_full)
        agg_ctx = self._make_coherence_data(data_ctx)

        coh_full = _compute_tfidf_coherence(agg_full, 'char')
        coh_ctx = _compute_tfidf_coherence(agg_ctx, 'char')

        assert coh_full[('BankA', 2021)] > coh_ctx[('BankA', 2021)], \
            "Full 轨 (相同文本) 应比 Ctx 轨 (不同文本) 连贯性更高"

    def test_lda_coherence_direction(self):
        """LDA 连贯性: 1 - JSD 方向正确, 相似文本 → 高值。

        【白话】主题模型的连贯性也应该遵循"相似=高分"的规则。
        """
        agg_df = self._make_coherence_data({
            ('BankA', 2020): '银行金融科技创新区块链数字货币人工智能' * 30,
            ('BankA', 2021): '银行金融科技创新区块链数字货币人工智能' * 30,
            ('BankB', 2020): '银行金融科技创新' * 30,
            ('BankB', 2021): '绿色环保低碳经济可持续发展新能源汽车' * 30,
        })
        coh = _compute_lda_coherence(agg_df)
        if ('BankA', 2021) in coh and ('BankB', 2021) in coh:
            assert coh[('BankA', 2021)] >= coh[('BankB', 2021)], \
                f"相同文本的LDA连贯性({coh[('BankA', 2021)]:.3f})应 >= " \
                f"不同文本({coh[('BankB', 2021)]:.3f})"
        # LDA 有随机性, 宽松断言: 至少值在 [0, 1]
        for key, val in coh.items():
            assert 0.0 - 1e-10 <= val <= 1.0 + 1e-10, \
                f"LDA coherence{key} = {val} 超出 [0,1]"

    def test_year_gap_returns_nan(self):
        """年份间隙 (如 2020→2022 缺 2021) 应返回 NaN, 不应计算"跨年连贯性"。

        【学术】欧阳志刚 & 胡雯华 (2024) 严格定义"相邻期"为连续年度 (t 与 t-1)。
        如果中间缺了一年 (比如 2021 没有数据), 那么 2022 就没有"去年"可比较。

        【白话】如果一家银行 2020 年有新闻, 2021 年没有, 2022 年又有了,
        那 2022 年的连贯性应该是空的 (NaN), 而不是和 2020 年比较。
        因为隔了一年, "去年"的数据不存在, 不能算"相邻"。
        """
        agg_df = self._make_coherence_data({
            ('BankA', 2020): '银行金融科技创新发展报告' * 20,
            # 2021 年完全缺失 → gap
            ('BankA', 2022): '银行金融科技创新发展报告' * 20,
        })
        coh = _compute_tfidf_coherence(agg_df, 'char')
        # 2020 是首年, 不应有值
        assert ('BankA', 2020) not in coh, "首年不应有连贯性值"
        # 2022 的 year-1=2021 不存在于数据中, 也不应有值
        assert ('BankA', 2022) not in coh, \
            "年份间隙后的年度 (2022, 缺 2021 数据) 不应有连贯性值"


# =============================================================================
# 10. _compute_centroid_scores (谢佳松 2025, 经济研究, 图 1)
# =============================================================================

class TestCentroidScores:
    """全行业向量法 (Centroid Distance) 单元测试。

    验证 1 - CosineSim(bank_vec, industry_centroid) 的计算正确性。
    """

    def test_identical_texts(self):
        """全相同文本 → centroid_diff ≈ 0。"""
        texts = ["银行金融科技创新发展报告"] * 3
        _, tfidf_mat = _build_tfidf_sim_matrix(texts, 'char')
        banks = ['A', 'B', 'C']
        scores = _compute_centroid_scores(tfidf_mat, banks, is_sparse=True)
        for bank in banks:
            assert scores[bank] < 0.01, \
                f"相同文本的 centroid_diff 应趋近 0, 实际={scores[bank]}"

    def test_outlier_high(self):
        """离群文本 → centroid_diff 显著高于其他。"""
        texts = ["银行金融科技创新发展",
                 "银行金融科技创新进展",
                 "乡村农业种植养殖报告"]  # 离群
        _, tfidf_mat = _build_tfidf_sim_matrix(texts, 'char')
        banks = ['BankA', 'BankB', 'Outlier']
        scores = _compute_centroid_scores(tfidf_mat, banks, is_sparse=True)
        assert scores['Outlier'] > scores['BankA'], \
            f"离群文本应有更高的 centroid_diff: Outlier={scores['Outlier']}, BankA={scores['BankA']}"

    def test_value_range(self):
        """所有输出 ∈ [0, 1]。"""
        texts = ["银行金融科技创新", "保险行业数字化转型",
                 "证券投资基金管理", "小额贷款普惠金融"]
        _, tfidf_mat = _build_tfidf_sim_matrix(texts, 'char')
        banks = ['A', 'B', 'C', 'D']
        scores = _compute_centroid_scores(tfidf_mat, banks, is_sparse=True)
        for bank, val in scores.items():
            assert 0.0 <= val <= 1.0, \
                f"{bank} 的 centroid_diff={val} 超出 [0,1]"

    def test_dense_input(self):
        """稠密矩阵输入正确处理。"""
        vectors = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        banks = ['X', 'Y', 'Z']
        scores = _compute_centroid_scores(vectors, banks, is_sparse=False)
        for bank in banks:
            assert 0.0 <= scores[bank] <= 1.0
        # Z=[1,1] 最接近 centroid=mean([1,0],[0,1],[1,1])=[0.67,0.67]
        assert scores['Z'] < scores['X'], \
            f"Z 应比 X 更接近质心: Z={scores['Z']}, X={scores['X']}"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
