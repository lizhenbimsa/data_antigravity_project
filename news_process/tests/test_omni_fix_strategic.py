"""test_omni_fix_strategic — g-strategic 组 omni 审计修复回归锁 (2026-06-11).

锁定 strategic_diff.py 的修复后行为 (合成 DataFrame, mock 嵌入, 不触网/不读盘):
  - g-strategic-01: 同 (bank, year) 内逐字重复全文 content 去重 (只计一次)
  - g-strategic-09: 跨银行共提及同文默认保留 + co_mention_downweight 开关
    (句子级 round-robin 均分, 跨银行零逐字重叠, 期望权重 1/n_banks)
  - g-strategic-02: emb 余弦真值域 [-1,1] / 距离 [0,2] (sim_bounds/dist_bounds
    参数化, clip 仅作浮点容忍而非值域删失); TF-IDF 默认 [0,1] 口径不变
  - g-strategic-05: N-NN |peers| < N → NaN (原 k=min 静默降级伪稳健)
  - g-strategic-10: 行业质心改 leave-one-out (c_{-i} = (n·c − v_i)/(n−1)); n<2 → NaN
  - g-strategic-03/12: coh_emb* 保留合法负余弦且 clip [-1,1]; 诊断断言分族放宽
  - g-strategic-04/15/16: LDA n_jobs=1 (跨机确定性) + 同机逐位可复现
  - g-strategic-11: fluidity TF-IDF 补 sublinear_tf=True (与家族统一)
  - g-strategic-13: fluidity 落列独立于 NN ≥3 银行闸门 (2 银行年份不再静默丢弃)
  - g-strategic-06/07/08/14: 披露项 (K=10 伪自适应 / 契约别名=centroid 构念 /
    t2v 128-token 截断已由 embedding_engine 修复 / lazy_minedit 前缀任意性)

# 白话: "战略差异化"衡量一家银行的报道内容跟同行有多不一样。这组测试守住:
# 同一篇稿子被重复收录只算一次; 找"最近 N 个邻居"时同行不够 N 个就记 NaN,
# 不许悄悄少拿几个凑数; 算"离行业平均有多远"时, 行业平均不能把自己也算进去
# (否则人人都显得不极端); 向量余弦本来可以是负数, 不能一刀切夹到 0~1;
# LDA 主题模型固定单线程+固定种子, 换台机器跑结果也一字不差。
"""
from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest
from scipy.sparse import csr_matrix

import news_process.pipeline.features.strategic_diff as sd

pytestmark = pytest.mark.fast


# ---------------------------------------------------------------------------
# g-strategic-01 / 09: 文章级 content 去重 + 共提及降权开关
# ---------------------------------------------------------------------------

class TestAggregateDedupAndCoMention:

    def test_same_bank_year_duplicate_counted_once(self):
        # 同 (bank, year) 两篇逐字相同文章 → 聚合文档中正文只出现 1 次
        body = '移动支付钱包战略布局持续推进数字化转型'
        df = pd.DataFrame({
            'target_bank': ['A', 'A'], 'year': [2018, 2018],
            '内容': [body, body],
        })
        agg = sd._aggregate_bank_year_texts(df, text_col='内容')
        assert len(agg) == 1
        assert agg.iloc[0]['agg_text'].count(body) == 1, \
            "重复全文应去重只计一次 (omni-g-strategic-01)"

    def test_distinct_articles_not_deduped(self):
        df = pd.DataFrame({
            'target_bank': ['A', 'A'], 'year': [2018, 2018],
            '内容': ['正文甲移动支付', '正文乙区块链结算'],
        })
        agg = sd._aggregate_bank_year_texts(df, text_col='内容')
        text = agg.iloc[0]['agg_text']
        assert '正文甲移动支付' in text and '正文乙区块链结算' in text

    def test_cross_bank_shared_article_kept_by_default(self):
        # 共提及同文默认保留 (co_mention_downweight=False, 维持原口径)
        body = '一篇同时报道两家银行的金融科技文章。包含多个句子。第三句。'
        df = pd.DataFrame({
            'target_bank': ['A', 'B'], 'year': [2018, 2018],
            '内容': [body, body],
        })
        agg = sd._aggregate_bank_year_texts(df, text_col='内容')
        texts = dict(zip(agg['target_bank'], agg['agg_text']))
        assert texts['A'] == body and texts['B'] == body, \
            "默认口径下共提及文章应逐字保留于每家银行 (披露项, 非删除)"

    def test_co_mention_downweight_round_robin_no_overlap(self):
        # 开关开: 共享同文句子 round-robin 均分, 两银行句子集互斥且并集=原文
        s1, s2, s3, s4 = '第一句移动支付。', '第二句区块链。', '第三句智能投顾。', '第四句开放银行。'
        body = s1 + s2 + s3 + s4
        df = pd.DataFrame({
            'target_bank': ['A', 'B'], 'year': [2018, 2018],
            '内容': [body, body],
        })
        agg = sd._aggregate_bank_year_texts(df, text_col='内容',
                                            co_mention_downweight=True)
        texts = dict(zip(agg['target_bank'], agg['agg_text']))
        # rank 按银行名排序: A=rank0 → [s1,s3], B=rank1 → [s2,s4]
        assert texts['A'] == s1 + s3
        assert texts['B'] == s2 + s4
        # 互斥: 任一句子只归一家银行
        for s in (s1, s2, s3, s4):
            assert (s in texts['A']) != (s in texts['B'])

    def test_co_mention_downweight_keeps_unshared_articles_intact(self):
        # 非共享文章不受开关影响
        body_a = '银行A独家报道句一。句二。'
        body_shared = '共享报道句一。共享报道句二。'
        df = pd.DataFrame({
            'target_bank': ['A', 'A', 'B'], 'year': [2018, 2018, 2018],
            '内容': [body_a, body_shared, body_shared],
        })
        agg = sd._aggregate_bank_year_texts(df, text_col='内容',
                                            co_mention_downweight=True)
        texts = dict(zip(agg['target_bank'], agg['agg_text']))
        assert body_a in texts['A'], "独家文章不应被降权切分"

    def test_round_robin_n1_identity(self):
        assert sd._round_robin_sentences('任意文本。', 0, 1) == '任意文本。'

    def test_round_robin_single_sentence_exclusive(self):
        # 无句界可切 → 退化为独占指派: 仅 rank=0 保留全文
        t = '单句无句界文本'
        assert sd._round_robin_sentences(t, 0, 3) == t
        assert sd._round_robin_sentences(t, 1, 3) == ''
        assert sd._round_robin_sentences(t, 2, 3) == ''

    def test_round_robin_partition_covers_all_sentences(self):
        pieces = [f'句{i}。' for i in range(5)]
        t = ''.join(pieces)
        parts = [sd._round_robin_sentences(t, r, 2) for r in range(2)]
        assert ''.join(sorted(pieces)) == ''.join(
            sorted(p for part in parts for p in
                   [s for s in sd._SENT_SPLIT_RE.split(part) if s]))

    def test_config_switch_default_off(self):
        # config/features.yaml strategic_diff.co_mention_downweight 默认 false
        assert sd.CONFIG.get('strategic_diff', {}) \
            .get('co_mention_downweight') is False


# ---------------------------------------------------------------------------
# g-strategic-02 / 05: N-NN sim_bounds 参数化 + |peers| < N → NaN
# ---------------------------------------------------------------------------

def _sim_matrix_3banks():
    """sim(x,y)=-0.5, sim(x,z)=-0.2, sim(y,z)=0.3, 对角 NaN."""
    m = np.array([[np.nan, -0.5, -0.2],
                  [-0.5, np.nan, 0.3],
                  [-0.2, 0.3, np.nan]])
    return m


class TestNNScoresEmbBounds:

    def test_negative_cosine_not_floored_with_emb_bounds(self):
        m = _sim_matrix_3banks()
        res = sd._compute_nn_scores(m, ['x', 'y', 'z'], [2],
                                    sim_bounds=(-1.0, 1.0))
        # x 的全部 peer 相似度为负 → sim_max 保留负值 (旧 clip[0,1] 报 0.0)
        assert res['sim_max']['x'] == pytest.approx(-0.2)
        # δ = 1 - sim 可 >1 (emb 距离 ∈ [0,2]): mean(1.2, 1.5) = 1.35
        assert res['n2']['x'] == pytest.approx(1.35)

    def test_default_tfidf_bounds_unchanged(self):
        # TF-IDF 默认 (0,1): 负值仍地板到 0 (非负向量算子的浮点容忍口径不变)
        m = _sim_matrix_3banks()
        res = sd._compute_nn_scores(m, ['x', 'y', 'z'], [2])
        assert res['sim_max']['x'] == pytest.approx(0.0)
        assert res['n2']['x'] == pytest.approx(1.0)

    def test_peers_lt_n_nan_similarity_branch(self):
        # 3 银行 → 每行 2 个 peer: n2 有值, n3..n5 必须 NaN (不再 k=min 降级)
        m = _sim_matrix_3banks()
        res = sd._compute_nn_scores(m, ['x', 'y', 'z'], [2, 3, 5])
        assert np.isfinite(res['n2']['x'])
        assert np.isnan(res['n3']['x']), \
            "|peers|=2 < N=3 应 NaN (omni-g-strategic-05)"
        assert np.isnan(res['n5']['y'])

    def test_peers_lt_n_nan_distance_branch(self):
        d = np.array([[np.nan, 0.4, 0.6],
                      [0.4, np.nan, 0.2],
                      [0.6, 0.2, np.nan]])
        res = sd._compute_nn_scores(d, ['x', 'y', 'z'], [2, 3],
                                    is_distance=True)
        assert res['n2']['x'] == pytest.approx(0.5)
        assert np.isnan(res['n3']['x'])


# ---------------------------------------------------------------------------
# g-strategic-10 / 02: leave-one-out 质心 + emb 距离 [0,2]
# ---------------------------------------------------------------------------

class TestCentroidLeaveOneOut:

    @staticmethod
    def _manual_loo(vectors):
        v = np.asarray(vectors, dtype=np.float64)
        n = v.shape[0]
        out = []
        for i in range(n):
            c = (v.sum(axis=0) - v[i]) / (n - 1)
            cos = v[i] @ c / (np.linalg.norm(v[i]) * np.linalg.norm(c))
            out.append(1.0 - cos)
        return out

    def test_loo_matches_manual_dense(self):
        v = np.array([[1.0, 0.2], [0.8, 0.6], [0.1, 1.0]])
        got = sd._compute_centroid_scores(v, ['a', 'b', 'c'])
        want = self._manual_loo(v)
        for bank, w in zip(['a', 'b', 'c'], want):
            assert got[bank] == pytest.approx(np.clip(w, 0.0, 1.0), abs=1e-12)

    def test_orthogonal_bank_no_self_attenuation(self):
        # v3 与其余银行正交: LOO 质心不含自身 → 距离恰 1.0
        # (旧自含质心 cos>0 → 距离 <1, 右尾被机械压缩)
        v = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
        got = sd._compute_centroid_scores(v, ['a', 'b', 'c'])
        assert got['c'] == pytest.approx(1.0, abs=1e-12), \
            "正交银行的 LOO 质心距离应恰为 1 (omni-g-strategic-10)"

    def test_sparse_input_matches_dense(self):
        v = np.array([[1.0, 0.2], [0.8, 0.6], [0.1, 1.0]])
        dense = sd._compute_centroid_scores(v, ['a', 'b', 'c'])
        sparse = sd._compute_centroid_scores(csr_matrix(v), ['a', 'b', 'c'],
                                             is_sparse=True)
        for bank in ('a', 'b', 'c'):
            assert sparse[bank] == pytest.approx(dense[bank], abs=1e-12)

    def test_single_bank_nan(self):
        got = sd._compute_centroid_scores(np.array([[1.0, 0.0]]), ['solo'])
        assert np.isnan(got['solo']), "n<2 时 LOO 质心无定义 → NaN"

    def test_emb_dist_bounds_allow_gt1(self):
        # emb 轨: 银行与 LOO 质心近乎反向 → 距离 ≈ 2, dist_bounds=(0,2) 不删失
        v = np.array([[1.0, 0.0], [-1.0, 0.0], [-1.0, 1e-3]])
        got = sd._compute_centroid_scores(v, ['a', 'b', 'c'],
                                          dist_bounds=(0.0, 2.0))
        assert got['a'] > 1.5, \
            "emb 距离 δ=1-cos 应可超 1 (旧 clip[0,1] 是值域删失)"
        assert got['a'] <= 2.0 + 1e-10

    def test_default_tfidf_dist_bounds_unchanged(self):
        # TF-IDF/LDA 默认 (0,1): 越界仍按 [0,1] 容忍 (非负算子口径不变)
        v = np.array([[1.0, 0.0], [-1.0, 0.0], [-1.0, 1e-3]])
        got = sd._compute_centroid_scores(v, ['a', 'b', 'c'])
        assert got['a'] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# g-strategic-03 / 12: coh_emb 保留负余弦 + clip 浮点容忍 + 诊断分族断言
# ---------------------------------------------------------------------------

class TestCoherenceValueDomain:

    def test_emb_coherence_keeps_negative_cosine(self, monkeypatch):
        # 相邻两年嵌入反向 → coherence = -1.0 (保留, 不删失到 0; clip 至 [-1,1])
        agg = pd.DataFrame({
            'target_bank': ['A', 'A'], 'year': [2017, 2018],
            'agg_text': ['去年文本', '今年文本'],
        })
        monkeypatch.setattr(
            sd, '_embed_texts_with_chunk_pooling',
            lambda texts, spec=None, log_prefix='': np.array(
                [[1.0, 0.0], [-1.0, 0.0]], dtype=np.float32))
        coh = sd._compute_emb_coherence(agg)
        assert coh[('A', 2018)] == pytest.approx(-1.0), \
            "合法负余弦应保留 (omni-g-strategic-03), 旧裸值+[0,1] 断言为 latent 崩溃"
        assert -1.0 <= coh[('A', 2018)] <= 1.0

    def test_diagnostics_accept_negative_coh_emb(self):
        panel = pd.DataFrame({'coh_emb_full': [-0.5, 0.3],
                              'coh_emb_lg_ctx': [-0.99, 0.94]})
        sd._log_coherence_diagnostics(panel)  # 不应 raise

    def test_diagnostics_reject_negative_tfidf_coh(self):
        panel = pd.DataFrame({'coh_tfidf_c_full': [-0.5, 0.3]})
        with pytest.raises(AssertionError):
            sd._log_coherence_diagnostics(panel)

    def test_diagnostics_reject_coh_emb_below_minus_one(self):
        panel = pd.DataFrame({'coh_emb_full': [-1.5]})
        with pytest.raises(AssertionError):
            sd._log_coherence_diagnostics(panel)

    def test_tfidf_coherence_identical_texts_capped_at_one(self):
        # 完全相同的相邻期文档: cos=1 (float 可 1+ε) → clip 后恰 ≤ 1
        agg = pd.DataFrame({
            'target_bank': ['A', 'A', 'B', 'B'],
            'year': [2017, 2018, 2017, 2018],
            'agg_text': ['移动支付战略布局'] * 2 + ['区块链跨境结算'] * 2,
        })
        coh = sd._compute_tfidf_coherence(agg, 'char')
        assert coh[('A', 2018)] == pytest.approx(1.0)
        assert coh[('A', 2018)] <= 1.0


class TestRobustnessDiagnosticsFamilies:

    def test_emb_families_extended_bounds_accepted(self):
        panel = pd.DataFrame({
            'strat_sim_max_emb': [-0.3, 0.9],          # emb 相似度 ∈ [-1,1]
            'strat_diff_n5_emb': [1.7, 0.4],           # emb 距离 ∈ [0,2]
            'strat_diff_n5_emb_lg_ctx': [1.95, 0.2],   # co-primary _lg 孪生 (text-embedding-3-large)
            'centroid_diff_emb_lg': [1.9, 0.1],
            'strat_diff_lg_full': [1.9, 0.1],          # 契约别名 (centroid emb, _lg)
            'strat_diff_n5': [0.5, 0.7],               # TF-IDF ∈ [0,1]
            'strat_fluidity': [0.2, 0.8],
        })
        sd._log_robustness_diagnostics(panel)  # 不应 raise

    def test_tfidf_out_of_bounds_raises(self):
        with pytest.raises(AssertionError):
            sd._log_robustness_diagnostics(
                pd.DataFrame({'strat_diff_n5': [1.5]}))

    def test_emb_distance_above_two_raises(self):
        with pytest.raises(AssertionError):
            sd._log_robustness_diagnostics(
                pd.DataFrame({'strat_diff_n5_emb': [2.5]}))

    def test_emb_simmax_below_minus_one_raises(self):
        with pytest.raises(AssertionError):
            sd._log_robustness_diagnostics(
                pd.DataFrame({'strat_sim_max_emb': [-1.2]}))


# ---------------------------------------------------------------------------
# g-strategic-04 / 15 / 16: LDA n_jobs=1 确定性
# ---------------------------------------------------------------------------

class TestLDADeterminism:

    def test_n_jobs_pinned_to_1_in_both_sites(self):
        # AST 解析实际调用参数 (docstring/注释中的"原 n_jobs=-1"历史叙述不算数)
        import ast
        import textwrap
        for fn in (sd._build_lda_jsd_matrix, sd._compute_lda_coherence):
            tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
            calls = [node for node in ast.walk(tree)
                     if isinstance(node, ast.Call)
                     and getattr(node.func, 'id', '') == 'LatentDirichletAllocation']
            assert calls, f"{fn.__name__}: 未找到 LatentDirichletAllocation 调用"
            for call in calls:
                kw = {k.arg: k.value for k in call.keywords}
                assert 'n_jobs' in kw, f"{fn.__name__}: n_jobs 未显式指定"
                njv = ast.literal_eval(kw['n_jobs'])
                assert njv == 1, (
                    f"{fn.__name__}: n_jobs={njv} — 跨机器核数依赖破坏逐位可复现性, "
                    f"须为 1 (omni-g-strategic-16)")
                assert 'random_state' in kw and \
                    ast.literal_eval(kw['random_state']) == 42

    def test_lda_jsd_bitwise_reproducible_same_process(self):
        texts = ['移动支付钱包战略布局推进', '区块链跨境结算平台上线',
                 '智能投顾财富管理转型', '开放银行接口生态共建']
        m1, t1 = sd._build_lda_jsd_matrix(texts, len(texts))
        m2, t2 = sd._build_lda_jsd_matrix(texts, len(texts))
        np.testing.assert_array_equal(m1, m2)   # NaN 对角按相等处理
        np.testing.assert_array_equal(t1, t2)

    def test_policy_similarity_reuses_fixed_lda(self):
        # policy_similarity.py 复用 _build_lda_jsd_matrix → auth_sim_lda* 同受益
        import news_process.pipeline.features.policy_similarity as ps
        assert getattr(ps, '_build_lda', None) is sd._build_lda_jsd_matrix


# ---------------------------------------------------------------------------
# g-strategic-11: fluidity TF-IDF sublinear_tf 与家族统一
# ---------------------------------------------------------------------------

class TestFluiditySublinearTf:

    def test_fluidity_vectorizer_has_sublinear_tf(self):
        src = inspect.getsource(sd._compute_fluidity)
        assert src.count('sublinear_tf=True') >= 2, \
            "char/word 两组 kwargs 均须 sublinear_tf=True (omni-g-strategic-11)"


# ---------------------------------------------------------------------------
# g-strategic-13: fluidity 落列独立于 NN ≥3 银行闸门
# ---------------------------------------------------------------------------

class TestFluidityGateDecoupled:

    def test_fluidity_attached_when_all_years_below_nn_gate(self, monkeypatch):
        # 全部年份仅 2 家银行 (< NN 闸门 3): 旧实现 strat_fluidity 列根本不创建;
        # 修复后 fluidity 仅需 t-1 非空 (2 银行即可定义) → 直接以 panel 为骨架附着
        monkeypatch.setattr(
            sd, '_embed_texts_with_chunk_pooling',
            lambda texts, spec=None, log_prefix='': None)  # emb 轨优雅跳过, 零网络
        rows = []
        for bank, seed in (('A', '移动支付钱包战略布局'),
                           ('B', '区块链跨境结算平台')):
            for year in (2017, 2018):
                rows.append({
                    'target_bank': bank, 'year': year,
                    '标题': f'{bank}银行{year}金融科技',
                    '内容': f'{seed}持续推进数字化转型{year}年度报道正文',
                    'content_ctx': f'{bank}银行{year}金融科技 {seed}实体窗口{year}',
                })
        df = pd.DataFrame(rows)
        panel = pd.DataFrame({'target_bank': ['A', 'A', 'B', 'B'],
                              'year': [2017, 2018, 2017, 2018]})
        out = sd.compute_strategic_differentiation(df, panel)

        # NN 族确实没产 (闸门未过) — 锁住"闸门只管 NN, 不再连坐 fluidity"
        assert 'strat_diff_n5' not in out.columns
        for col in ('strat_fluidity', 'strat_fluidity_w',
                    'strat_fluidity_ctx', 'strat_fluidity_w_ctx'):
            assert col in out.columns, f"{col} 应独立于 NN 闸门创建"
        a2018 = out[(out['target_bank'] == 'A') & (out['year'] == 2018)]
        assert np.isfinite(a2018['strat_fluidity'].iloc[0]), \
            "2 银行年份的 fluidity 不应再被静默丢弃 (omni-g-strategic-13)"
        a2017 = out[(out['target_bank'] == 'A') & (out['year'] == 2017)]
        assert np.isnan(a2017['strat_fluidity'].iloc[0])  # 首年无 t-1 → NaN
        # co-primary _lg 嵌入轨契约列兜底仍在 (emb 轨失败 → 全 NaN; v3.14.0: _t2v 已删,
        # _lg=text-embedding-3-large 是唯一稳健嵌入孪生; coh_emb_lg_* 与 fluidity 同以
        # panel 为骨架附着, 独立于 NN ≥3 银行闸门)。
        for col in ('coh_emb_lg_full', 'coh_emb_lg_ctx'):
            assert col in out.columns
            assert out[col].isna().all()


# ---------------------------------------------------------------------------
# g-strategic-06 / 07 / 08 / 14 + 01/09: 披露项回归锁 (docstring 不可静默回退)
# ---------------------------------------------------------------------------

class TestDisclosures:

    def test_module_docstring_value_domain_and_alias(self):
        doc = sd.__doc__
        # 02/03: emb 值域口径
        assert '[-1,1]' in doc and '[0,2]' in doc
        # 07: 契约别名 = centroid 构念, 非 N-NN; 真 _lg 孪生 = strat_diff_n5_emb_lg
        # (v3.14.0: 本地 _t2v 已删, co-primary _lg=text-embedding-3-large)
        assert 'centroid_diff_emb_lg' in doc
        assert 'strat_diff_n5_emb_lg' in doc
        # 01/09: 共提及机械相似披露 + 开关
        assert '共提及' in doc
        assert 'co_mention_downweight' in doc
        # 08: 超长文本 token 分段 + 均值池化 (引擎接管, 不再本地截断)
        assert 'token 分段' in doc and '均值池化' in doc

    def test_lda_k_disclosure(self):
        # 06: K=max(10, n//30) 实为固定常数 10 的伪自适应 + 两处基数不一致披露
        assert '固定常数 10' in sd._build_lda_jsd_matrix.__doc__
        src = inspect.getsource(sd._compute_lda_coherence)
        assert 'n_total' in src and '不同' in src

    def test_lazy_minedit_prefix_disclosure(self):
        # 14: minedit 前缀任意性披露 (groupby 保序头部文章, 上游行序依赖)
        doc = sd._compute_lazy_distances.__doc__
        assert '前缀' in doc
        assert 'jaccard/overlap' in doc

    def test_aggregate_docstring_dedup_semantics(self):
        # 01: 去重语义变更必须在 docstring 留痕
        doc = sd._aggregate_bank_year_texts.__doc__
        assert '只计一次' in doc
        assert 'co_mention_downweight' in doc


# ---------------------------------------------------------------------------
# inject-fintech-word-lda (2026-06-21): word/LDA 轨注入金科词回归锁
# 白话: word 级稳健性轨改用"注入了金融科技词典的独立分词器", 让"金融科技""区块链"
# 这类领域复合词整体保留(不再被裸 jieba 切成"金融"+"科技"), 与 char/embedding 轨口径一致;
# 注入只进独立实例, 全局 jieba 保持纯净; 结果跨调用确定。
# ---------------------------------------------------------------------------

class TestFintechInjectionWordLDA:

    def test_injection_takes_effect_whole_compound(self):
        # 注入后金科复合词整词保留 (核心修复断言)
        toks = sd._jieba_tokenizer('银行的金融科技战略推进区块链')
        assert '金融科技' in toks, '注入后"金融科技"应为整词 token'
        assert '区块链' in toks, '注入后"区块链"应为整词 token'
        # 旧裸 jieba 行为 (切碎) 不应再出现为孤立子词
        assert '金融' not in toks and '科技' not in toks, \
            '注入后不应再把"金融科技"切成孤立的"金融"/"科技"'

    def test_global_jieba_stays_pure_isolation(self):
        # 隔离: 注入只进独立实例, 全局 jieba 仍切碎 (不污染 posseg/FLS 等全局消费者)
        import jieba
        sd._get_diff_tokenizer()  # 触发注入
        assert list(jieba.cut('金融科技')) == ['金融', '科技'], \
            '全局 jieba 应保持纯净 (注入只进 _DIFF_TOKENIZER 独立实例)'

    def test_injected_tokenizer_deterministic(self):
        # 注入态两次分词逐 token 一致 (确定性 → golden 可复现前提)
        s = '移动支付与智能投顾及开放银行的数字化转型布局'
        assert sd._jieba_tokenizer(s) == sd._jieba_tokenizer(s)

    def test_stopword_and_len_filter_preserved(self):
        # len>=2 + 停用词过滤规则保持不变 (注入不改这两条)
        toks = sd._jieba_tokenizer('的 在 和 区块链')
        assert '的' not in toks and '在' not in toks and '和' not in toks
        assert '区块链' in toks

    def test_diff_tokenizer_singleton(self):
        # DCL 单例: 多次取同一实例
        assert sd._get_diff_tokenizer() is sd._get_diff_tokenizer()

    def test_inject_disclosure_in_docstring(self):
        # 口径变更须在 docstring 留痕 (可审计)
        assert '金科' in sd._get_diff_tokenizer.__doc__ or '注入' in sd._get_diff_tokenizer.__doc__
        assert '金融科技' in sd._jieba_tokenizer.__doc__

    def test_no_bare_global_jieba_in_tokenizer_source(self):
        # 源码级回归锁 (镜像 tone_words 的 'jieba.cut(' not in src): _jieba_tokenizer
        # 不得回退到裸全局 jieba.lcut/jieba.cut, 必须经 _get_diff_tokenizer 独立实例。
        src = inspect.getsource(sd._jieba_tokenizer)
        assert 'jieba.lcut' not in src and 'jieba.cut' not in src, \
            '_jieba_tokenizer 不得直接调裸全局 jieba (须走 _get_diff_tokenizer 注入实例)'
        assert '_get_diff_tokenizer' in src

    def test_empty_dict_graceful_degrade_loud_warning(self, monkeypatch):
        # 优雅降级 (impl-attestation P2): 词典空/缺失 → loud WARNING + 不 raise +
        # 仍返回可用(未注入) Tokenizer。验证 docstring 承诺的 "loud WARNING" 兑现。
        # 直接 spy 模块 logger.warning (项目 logger propagate=False, caplog 不可靠)。
        import news_process.core.text.ahocorasick as _ahoc
        monkeypatch.setattr(_ahoc, 'load_fintech_dict', lambda *_a, **_k: ([], None))
        warns: list[str] = []
        monkeypatch.setattr(sd.logger, 'warning', lambda msg, *_a, **_k: warns.append(str(msg)))
        sd._DIFF_TOKENIZER = None  # 强制重建以走 patched 路径
        try:
            tk = sd._get_diff_tokenizer()           # 不应 raise
            assert tk is not None
            # 降级后仍可用 **且确为未注入态** (强断言: 金科复合词应被裸 jieba 切碎,
            # 证明走的是降级路径而非误用了注入实例) — closeout P3-a 加固原 tautology 断言。
            assert list(tk.cut('金融科技')) == ['金融', '科技'], \
                '降级 tokenizer 应为未注入态 (金融科技 被切碎), 且可用'
            assert any('为空或缺失' in w or '退化' in w for w in warns), \
                f'空词典须发 loud WARNING (非静默 INFO); 实捕获: {warns}'
        finally:
            sd._DIFF_TOKENIZER = None  # 清掉降级实例, 让后续测试重建真注入实例
