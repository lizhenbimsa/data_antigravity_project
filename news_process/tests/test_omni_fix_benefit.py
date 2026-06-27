"""tests/test_omni_fix_benefit.py — omni 审计 g-benefit 组修复回归锁 (2026-06-11).

锁定修复后行为 (防静默 revert):

  KNOWN-OPEN①        pos/neg_frac 中心改冻结 sidecar (_benefit_center_sidecar.json:
                     首跑计算持久化, 后续读冻结值; model 错配 fail-loud)
  g-benefit-01       27c 链路重接线: _project_texts 真落盘全长 .npy+sidecar /
                     方向向量 27_benefit_direction.npy 产出 / alt-anchor sidecar
                     强制 (陈旧 npy fail-loud) + spec 由 model_id 反查 / ctx 轨 /
                     placebo col_suffix / audit_combined 显式 seed
  g-benefit-02       alt-anchor twin pos/neg_frac median-center (sign-at-0 饱和退化修复)
  g-benefit-03/07/09 shrinkage 方差分量: 单成员组排除 + N−k 自由度 + Morris 噪声
                     扣除 + 文章级 std²/n 抽样方差
  g-benefit-04       full 轨 8191-token 预截断移除 (统一引擎 chunk 池化接管)
  g-benefit-05       benefit_std 单观测 → NaN (主模块 + alt twin; 不再 fillna(0))
  g-benefit-06       shrinkage group_cols 默认加 year (收缩目标跨年泄漏消除)

全部用合成数据 + mock 引擎, 不触网、不调付费 API、不写真实 data/processed。
"""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.papers.benefit_society import shrinkage as sh  # noqa: E402
from news_process.pipeline.features import benefit_society as bs  # noqa: E402
from news_process.pipeline.features import benefit_society_alt_anchor as alt  # noqa: E402
from news_process.pipeline.features import benefit_society_audit_combined as combined  # noqa: E402
from news_process.pipeline.features.benefit_society_placebo import (  # noqa: E402
    compute_placebo_projection,
)

pytestmark = pytest.mark.fast


# ============================================================================
# 共享 helpers
# ============================================================================


def _patch_engine(monkeypatch, dim: int = 4, capture: dict | None = None):
    """mock 统一引擎 embed_texts (确定性, 不触网)。"""
    from news_process.pipeline.text import embedding_engine as eng

    def fake_embed(texts, spec, **kwargs):
        items = list(texts)
        if capture is not None:
            capture.setdefault('calls', []).append(items)
        if not items:
            return None
        rng = np.random.RandomState(len(items) % 97 + 3)
        return rng.rand(len(items), dim).astype(np.float32)

    monkeypatch.setattr(eng, 'embed_texts', fake_embed)


def _write_emb_with_sidecar(path, emb, model_id='gemini-embedding-2-preview'):
    np.save(path, emb)
    with open(f"{path}.sidecar.json", 'w', encoding='utf-8') as f:
        json.dump({'model_id': model_id,
                   'n_rows': int(emb.shape[0]),
                   'dim': int(emb.shape[1])}, f)


# ============================================================================
# KNOWN-OPEN① — pos/neg_frac 中心冻结 sidecar
# ============================================================================


class TestFrozenCenter:
    @pytest.fixture(autouse=True)
    def _allow_small_n_freeze(self, monkeypatch):
        """小样本冻结闸 (_CENTER_MIN_N_TO_FREEZE) 降到 1, 让 4-score fixture
        可走冻结路径; 闸本身的行为由 test_small_n_does_not_freeze 单独锁定。"""
        monkeypatch.setattr(bs, '_CENTER_MIN_N_TO_FREEZE', 1)

    def test_first_run_computes_median_and_freezes(self, monkeypatch, tmp_path):
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        scores = pd.Series([0.1, 0.2, 0.3, 0.9])
        c = bs._get_frozen_center('benefit_score_full', scores, 'm1')
        assert c == pytest.approx(0.25)
        sidecar = json.loads(
            (tmp_path / '_benefit_center_sidecar.json').read_text(encoding='utf-8'))
        entry = sidecar['benefit_score_full']
        assert entry['center'] == pytest.approx(0.25)
        assert entry['model_id'] == 'm1'
        assert entry['n_scores'] == 4

    def test_subsequent_run_reads_frozen_value_not_new_median(
            self, monkeypatch, tmp_path):
        """语料漂移 (新 median=5.0) 不再平移阈值 — 仍读首跑冻结值 0.25。"""
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        bs._get_frozen_center('benefit_score_full',
                              pd.Series([0.1, 0.2, 0.3, 0.9]), 'm1')
        c2 = bs._get_frozen_center('benefit_score_full',
                                   pd.Series([4.0, 5.0, 6.0]), 'm1')
        assert c2 == pytest.approx(0.25)

    def test_per_key_isolation(self, monkeypatch, tmp_path):
        """full/ctx/_lg 各 score 列独立冻结条目。"""
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        c_full = bs._get_frozen_center('benefit_score_full',
                                       pd.Series([0.0, 1.0]), 'm1')
        c_ctx = bs._get_frozen_center('benefit_score_ctx',
                                      pd.Series([10.0, 20.0]), 'm1')
        assert c_full == pytest.approx(0.5)
        assert c_ctx == pytest.approx(15.0)

    def test_model_mismatch_fails_loud(self, monkeypatch, tmp_path):
        """嵌入模型换代 → 冻结条目 model_id 不匹配 → ValueError (防跨空间阈值误用)。"""
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        bs._get_frozen_center('benefit_score_full', pd.Series([0.0, 1.0]), 'm1')
        with pytest.raises(ValueError, match='模型换代'):
            bs._get_frozen_center('benefit_score_full',
                                  pd.Series([0.0, 1.0]), 'm2-new')

    def test_all_nan_scores_fallback_zero_without_freezing(
            self, monkeypatch, tmp_path):
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        c = bs._get_frozen_center('benefit_score_full',
                                  pd.Series([np.nan, np.nan]), 'm1')
        assert c == 0.0
        assert not (tmp_path / '_benefit_center_sidecar.json').exists()

    def test_small_n_does_not_freeze(self, monkeypatch, tmp_path):
        """纵深防御 (2026-06-11 并发污染实测教训): 有效得分 < 冻结闸时只现算
        不持久化 — 防 toy/试跑数据被冻结为生产阈值。"""
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        monkeypatch.setattr(bs, '_CENTER_MIN_N_TO_FREEZE', 50)
        c = bs._get_frozen_center('benefit_score_full',
                                  pd.Series([0.1, 0.2, 0.3, 0.9]), 'm1')
        assert c == pytest.approx(0.25)  # 本次仍用现算 median
        assert not (tmp_path / '_benefit_center_sidecar.json').exists()
        # 大样本 (≥闸) → 正常冻结
        big = pd.Series(np.linspace(-1.0, 1.0, 60))
        c2 = bs._get_frozen_center('benefit_score_full', big, 'm1')
        assert c2 == pytest.approx(float(big.median()))
        assert (tmp_path / '_benefit_center_sidecar.json').exists()


# ============================================================================
# g-benefit-01 — stage 27 落盘 (嵌入 .npy + sidecar + 方向向量)
# ============================================================================


class TestStage27Persistence:
    def test_project_texts_persists_full_length_npy_and_sidecar(
            self, monkeypatch, tmp_path):
        """全长落盘: 行序=输入, 空文本行=NaN; sidecar 含 model_id/n_rows/dim。"""
        _patch_engine(monkeypatch, dim=4)
        monkeypatch.setattr(bs, '_CACHE_EMBEDDINGS', True)
        cache_path = str(tmp_path / '27_benefit_embeddings_full.npy')
        direction = np.array([1.0, 0.0, 0.0, 0.0])
        texts = ['文章一', '', '文章三']  # 中间空文本
        scores = bs._project_texts(texts, direction, cache_path,
                                   spec={'model': 'fake-model'})
        assert len(scores) == 3
        assert np.isnan(scores[1]) and np.isfinite(scores[0]) and np.isfinite(scores[2])

        full = np.load(cache_path)
        assert full.shape == (3, 4)
        assert np.isnan(full[1]).all()
        assert np.isfinite(full[0]).all()

        meta = json.loads(
            Path(f"{cache_path}.sidecar.json").read_text(encoding='utf-8'))
        assert meta['model_id'] == 'fake-model'
        assert meta['n_rows'] == 3
        assert meta['n_valid'] == 2
        assert meta['dim'] == 4

    def test_project_texts_no_persist_when_cache_disabled(
            self, monkeypatch, tmp_path):
        _patch_engine(monkeypatch, dim=4)
        monkeypatch.setattr(bs, '_CACHE_EMBEDDINGS', False)
        cache_path = str(tmp_path / 'no_write.npy')
        bs._project_texts(['x'], np.ones(4), cache_path, spec={'model': 'm'})
        assert not Path(cache_path).exists()

    def test_direction_vector_persisted_with_sidecar(self, monkeypatch, tmp_path):
        """--main-direction-npy 的产出方 (此前从未被任何阶段产出)。"""
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        bs._persist_direction_vector(np.array([1.0, 2.0, 3.0, 4.0]), '',
                                     spec={'model': 'fake-model'})
        npy = tmp_path / '27_benefit_direction.npy'
        assert npy.exists()
        meta = json.loads(
            (tmp_path / '27_benefit_direction.npy.sidecar.json')
            .read_text(encoding='utf-8'))
        assert meta['model_id'] == 'fake-model'
        assert meta['unit_norm'] is False
        assert meta['dim'] == 4
        assert meta['n_anchor_pairs'] == len(bs.POSITIVE_ANCHORS)


# ============================================================================
# g-benefit-04 — full 轨预截断移除 (引擎 chunk 池化接管)
# ============================================================================


class TestNoPretruncation:
    def test_engine_receives_untruncated_text(self, monkeypatch, tmp_path):
        capture: dict = {}
        _patch_engine(monkeypatch, dim=4, capture=capture)
        monkeypatch.setattr(bs, '_CACHE_EMBEDDINGS', False)
        long_text = '银行金融科技数字化转型' * 1500  # 远超 8191 cl100k tokens
        bs._project_texts([long_text], np.ones(4), None, spec={'model': 'm'})
        sent = capture['calls'][0][0]
        assert sent == long_text, "文本送引擎前不得预截断 (chunk 池化由引擎负责)"

    def test_project_texts_source_has_no_pretruncation(self):
        src = inspect.getsource(bs._project_texts)
        assert '_truncate_to_max_tokens(' not in src.replace(
            'fix(omni-g-benefit-04', ''), (
            "_project_texts 不得恢复 8191-token 预截断 (g-benefit-04)")


# ============================================================================
# g-benefit-05 — benefit_std 单观测 → NaN (主模块)
# ============================================================================


class TestSingleObsStdNaN:
    def test_panel_std_nan_for_single_article_bank_year(
            self, monkeypatch, tmp_path):
        _patch_engine(monkeypatch, dim=4)
        monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
        df = pd.DataFrame([
            {'target_bank': 'A行', 'year': 2020,
             '标题': 't1', '内容': '区块链 内容一', 'content_full': 't1。区块链 内容一'},
            {'target_bank': 'A行', 'year': 2020,
             '标题': 't2', '内容': '移动支付 内容二', 'content_full': 't2。移动支付 内容二'},
            {'target_bank': 'B行', 'year': 2020,
             '标题': 't3', '内容': '智能风控 内容三', 'content_full': 't3。智能风控 内容三'},
        ])
        panel = pd.DataFrame({'target_bank': ['A行', 'B行'], 'year': [2020, 2020]})
        out = bs.compute_benefit_society_panel(panel, df)
        a = out[out['target_bank'] == 'A行'].iloc[0]
        b = out[out['target_bank'] == 'B行'].iloc[0]
        assert np.isfinite(a['benefit_std_full']), "两篇文章 → std 有限"
        assert np.isnan(b['benefit_std_full']), (
            "单篇文章 bank-year 的 std 必须为 NaN (不得 fillna(0))")

    def test_alt_twin_singleton_std_nan(self):
        df = pd.DataFrame({'target_bank': ['a'], 'year': [2020]})
        agg = alt.aggregate_to_bank_year(df, np.array([0.7]))
        assert np.isnan(agg.iloc[0]['benefit_jlm_zh_std'])


# ============================================================================
# g-benefit-02 — alt-anchor twin median-center
# ============================================================================


class TestAltAnchorMedianCenter:
    def test_all_positive_scores_dedegenerate(self):
        """全正投影 (模拟各向异性饱和 ~97%>0): sign-at-0 给 pos_frac≡1.0,
        median-center 恢复区分度。"""
        df = pd.DataFrame({'target_bank': ['a'] * 4 + ['b'] * 4,
                           'year': [2020] * 8})
        scores = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
        agg = alt.aggregate_to_bank_year(df, scores)
        a = agg[agg['target_bank'] == 'a'].iloc[0]
        b = agg[agg['target_bank'] == 'b'].iloc[0]
        # pooled median = 0.45: a 全在下方, b 全在上方
        assert a['benefit_jlm_zh_pos_frac'] == 0.0
        assert a['benefit_jlm_zh_neg_frac'] == 1.0
        assert b['benefit_jlm_zh_pos_frac'] == 1.0
        # 旧 sign-at-0 行为: 两家 pos_frac 均为 1.0 (饱和退化) — 不得回退
        assert not (a['benefit_jlm_zh_pos_frac'] == 1.0
                    and b['benefit_jlm_zh_pos_frac'] == 1.0)

    def test_explicit_center_honored(self):
        """显式 center= 传入 (如主模块冻结 sidecar 值) 覆盖默认 pooled median。"""
        df = pd.DataFrame({'target_bank': ['a'] * 4, 'year': [2020] * 4})
        scores = np.array([0.1, 0.2, 0.3, 0.4])
        agg = alt.aggregate_to_bank_year(df, scores, center=0.0)
        assert agg.iloc[0]['benefit_jlm_zh_pos_frac'] == 1.0  # 全 > 0

    def test_ctx_suffix_columns(self):
        df = pd.DataFrame({'target_bank': ['a', 'a'], 'year': [2020, 2020]})
        agg = alt.aggregate_to_bank_year(df, np.array([0.1, 0.5]),
                                         col_suffix='_ctx')
        for col in ['benefit_jlm_zh_mean_ctx', 'benefit_jlm_zh_std_ctx',
                    'benefit_jlm_zh_pos_frac_ctx', 'benefit_jlm_zh_neg_frac_ctx']:
            assert col in agg.columns


# ============================================================================
# g-benefit-01 — alt-anchor sidecar 强制 + spec 反查
# ============================================================================


class TestAltAnchorRewire:
    def test_npy_without_sidecar_fails_loud(self, tmp_path):
        npy = tmp_path / 'stale.npy'
        np.save(npy, np.zeros((2, 3), dtype=np.float32))
        with pytest.raises(FileNotFoundError, match='sidecar'):
            alt.load_article_embeddings(npy)

    def test_sidecar_row_mismatch_fails_loud(self, tmp_path):
        """584 行陈旧 npy vs 857 行 df 的错配形态 → fail-loud。"""
        npy = tmp_path / 'e.npy'
        np.save(npy, np.zeros((2, 3), dtype=np.float32))
        with open(f"{npy}.sidecar.json", 'w', encoding='utf-8') as f:
            json.dump({'model_id': 'm', 'n_rows': 5, 'dim': 3}, f)
        with pytest.raises(ValueError, match='n_rows'):
            alt.load_article_embeddings(npy)

    def test_sidecar_missing_model_id_fails(self, tmp_path):
        npy = tmp_path / 'e.npy'
        np.save(npy, np.zeros((2, 3), dtype=np.float32))
        with open(f"{npy}.sidecar.json", 'w', encoding='utf-8') as f:
            json.dump({'n_rows': 2, 'dim': 3}, f)
        with pytest.raises(ValueError, match='model_id'):
            alt.load_article_embeddings(npy)

    def test_valid_sidecar_loads(self, tmp_path):
        npy = tmp_path / 'e.npy'
        emb_in = np.arange(6, dtype=np.float32).reshape(2, 3)
        _write_emb_with_sidecar(npy, emb_in, model_id='m')
        emb, meta = alt.load_article_embeddings(npy)
        assert emb.shape == (2, 3)
        assert meta['model_id'] == 'm'

    def test_resolve_spec_main_and_coprimary(self):
        """config/features.yaml 双 co-primary spec 反查 (v3.14.0: gemini MAIN +
        text-embedding-3-large _lg; 已删本地 text2vec/_t2v); 未知 model → fail-loud。"""
        spec_main = alt.resolve_embedding_spec('gemini-embedding-2-preview')
        assert spec_main['model'] == 'gemini-embedding-2-preview'
        spec_lg = alt.resolve_embedding_spec('text-embedding-3-large')
        assert spec_lg['model'] == 'text-embedding-3-large'
        with pytest.raises(ValueError, match='未知嵌入模型'):
            alt.resolve_embedding_spec('gpt-7-nonexistent')


# ============================================================================
# g-benefit-01 — placebo col_suffix (ctx 轨) + audit_combined ctx/seed
# ============================================================================


class TestPlaceboAndCombined:
    def test_placebo_col_suffix(self):
        df = pd.DataFrame({
            'target_bank': ['a', 'a'], 'year': [2020, 2020],
            '标题': ['住房贷款 新闻', '其他'], '内容': ['x', 'y'],
        })
        emb = np.eye(2, 4, dtype=np.float32)
        direction = np.array([1.0, 0.0, 0.0, 0.0])
        panel, counts = compute_placebo_projection(
            df, emb, direction, {'housing_loans': ['住房贷款']},
            col_suffix='_ctx')
        assert 'benefit_placebo_housing_loans_mean_ctx' in panel.columns
        assert counts['housing_loans'] == 1

    def test_build_audit_panel_ctx_track_and_seed(self):
        rng = np.random.RandomState(7)
        df = pd.DataFrame({
            'target_bank': ['A', 'A', 'B'], 'year': [2018, 2018, 2018],
            '标题': ['住房贷款 按揭', 'n2', 'n3'], '内容': ['x', 'y', 'z'],
        })
        emb = rng.randn(3, 8).astype(np.float32)
        emb_ctx = rng.randn(3, 8).astype(np.float32)
        direction = rng.randn(8).astype(np.float32)

        def fake_anchor_fn(texts):
            return np.random.RandomState(5).randn(
                len(list(texts)), 8).astype(np.float32)

        panel, meta = combined.build_audit_panel(
            df, emb, direction,
            text_embeddings_ctx=emb_ctx,
            anchor_embedding_fn=fake_anchor_fn,
            embedding_model_id='injected-model',
            seed=123,
        )
        assert 'benefit_jlm_zh_mean' in panel.columns
        assert 'benefit_jlm_zh_mean_ctx' in panel.columns, "ctx 轨缺失 (g-benefit-01)"
        ctx_placebo = [c for c in panel.columns
                       if c.startswith('benefit_placebo_') and c.endswith('_ctx')]
        assert ctx_placebo, "placebo ctx twin 列缺失"
        assert meta['random_seed'] == 123
        assert meta['tracks'] == ['full', 'ctx']
        assert meta['embedding_model'] == 'injected-model'
        assert meta['embedding_dim'] == 8

    def test_build_audit_panel_direction_dim_mismatch_fails(self):
        """方向向量与文章嵌入维度错配 (2026-05-29 换模根因形态) → fail-loud。"""
        df = pd.DataFrame({'target_bank': ['A'], 'year': [2018],
                           '标题': ['t'], '内容': ['c']})
        emb = np.zeros((1, 8), dtype=np.float32)
        bad_direction = np.zeros(768, dtype=np.float32)  # 旧 shibing624 空间
        with pytest.raises(ValueError, match='Dimension mismatch'):
            combined.build_audit_panel(df, emb, bad_direction)

    def test_cli_seed_flag_present(self):
        src = inspect.getsource(combined.main)
        assert '"--seed"' in src, "audit_combined CLI 必须有显式 --seed (组级裁决)"


# ============================================================================
# g-benefit-03/07/09 — shrinkage 方差分量
# ============================================================================


class TestShrinkageVarianceComponents:
    def test_exact_nk_dof_and_noise_subtraction(self):
        """精确数值: 2 组各 2 成员; SS=10, dof=N−k=2 → resid=5;
        σ̂²ᵢ=1 → τ̂²=5−1=4 → w=1/(1+4)=0.2 (Morris MoM)。"""
        values = np.array([0.0, 2.0, 10.0, 14.0])
        n_obs = np.array([1.0, 1.0, 1.0, 1.0])
        groups = np.array(['A', 'A', 'B', 'B'])
        sv = np.ones(4)
        shrunk, w = sh.empirical_bayes_shrinkage(values, n_obs, groups,
                                                 sampling_var=sv)
        assert w == pytest.approx([0.2] * 4)
        # shrunk[0] = 0.2*groupmean(1.0) + 0.8*0.0 = 0.2
        assert shrunk[0] == pytest.approx(0.2)
        assert shrunk[3] == pytest.approx(0.2 * 12.0 + 0.8 * 14.0)

    def test_pure_noise_yields_strong_pooling(self):
        """τ²=0 (组内真实均值相同, 仅抽样噪声): 噪声扣除后 τ̂²≈0 → 权重接近 1。
        旧实现 between=τ̂²+E[σ̂²] → w≈0.5 (欠收缩) — 不得回退。"""
        rng = np.random.default_rng(1)
        G, K = 4, 12
        values, groups = [], []
        for g in range(G):
            values.extend(rng.normal(0.0, 0.1, K))
            groups.extend([f'G{g}'] * K)
        values = np.asarray(values)
        groups = np.asarray(groups)
        n_obs = np.full(values.shape, 10.0)
        sv = np.full(values.shape, 0.1 ** 2)  # 真实抽样方差
        _, w = sh.empirical_bayes_shrinkage(values, n_obs, groups,
                                            sampling_var=sv)
        assert w.mean() > 0.65, f"纯噪声场景应接近完全 pooling, got mean w={w.mean():.3f}"

    def test_strong_signal_yields_no_shrinkage(self):
        """τ² 大 + σ̂² 极小 → 权重 ≈ 0 (保留原值)。"""
        rng = np.random.default_rng(2)
        values = rng.uniform(-1.0, 1.0, 20)
        groups = np.array(['G'] * 20)
        n_obs = np.full(20, 100.0)
        sv = np.full(20, 1e-6)
        _, w = sh.empirical_bayes_shrinkage(values, n_obs, groups,
                                            sampling_var=sv)
        assert w.max() < 0.05

    def test_singleton_groups_do_not_deflate_tau(self):
        """单成员组 (离差恒 0) 不得稀释 τ̂²: 加 20 个 singleton 后
        多成员组行的权重应与无 singleton 基线逐位一致。"""
        multi_values = np.array([0.0, 1.0, 0.0, 1.0, 2.0, 3.0, 2.0, 3.0])
        multi_groups = np.array(['M1'] * 4 + ['M2'] * 4)
        n_multi = np.full(8, 4.0)
        sv_multi = np.full(8, 0.01)
        _, w_base = sh.empirical_bayes_shrinkage(
            multi_values, n_multi, multi_groups, sampling_var=sv_multi)

        single_values = np.zeros(20)
        single_groups = np.array([f'S{i}' for i in range(20)])
        values = np.concatenate([multi_values, single_values])
        groups = np.concatenate([multi_groups, single_groups])
        n_obs = np.concatenate([n_multi, np.full(20, 4.0)])
        sv = np.concatenate([sv_multi, np.full(20, 0.01)])
        _, w_with = sh.empirical_bayes_shrinkage(values, n_obs, groups,
                                                 sampling_var=sv)
        np.testing.assert_allclose(w_with[:8], w_base, atol=1e-12)

    def test_sampling_var_elementwise_fallback(self):
        """sampling_var 的 NaN 元素逐位回退 grand_var/n 代理, 不影响其余行。"""
        values = np.array([0.0, 1.0, 2.0, 3.0])
        n_obs = np.array([5.0, 5.0, 5.0, 5.0])
        groups = np.array(['G', 'G', 'G', 'G'])
        sv = np.array([0.01, np.nan, 0.01, 0.01])
        _, w = sh.empirical_bayes_shrinkage(values, n_obs, groups,
                                            sampling_var=sv)
        assert np.isfinite(w).all()
        assert ((w >= 0) & (w <= 1)).all()

    def test_all_singleton_groups_identity_shrinkage(self):
        """全单成员组: 组均值≡自身 → 收缩恒等 (不 crash)。"""
        values = np.array([1.0, 2.0, 3.0])
        n_obs = np.array([1.0, 1.0, 1.0])
        groups = np.array(['A', 'B', 'C'])
        shrunk, _ = sh.empirical_bayes_shrinkage(values, n_obs, groups)
        np.testing.assert_allclose(shrunk, values)

    def test_docstring_formula_matches_code(self):
        """公式统一回归锁: 旧 docstring 'σ²_within/(σ²_within + n_i × σ²_between)'
        与代码不符 (g-benefit-07) — 现统一为 w = σ̂²ᵢ/(σ̂²ᵢ+τ̂²)。"""
        doc = sh.empirical_bayes_shrinkage.__doc__
        assert 'σ̂²ᵢ / (σ̂²ᵢ + τ̂²)' in doc
        assert 'n_i × σ²_between' not in (sh.__doc__ or '')


# ============================================================================
# g-benefit-06 — shrinkage group 加 year (跨年泄漏)
# ============================================================================


class TestShrinkageYearGroups:
    def test_default_group_cols_include_year(self):
        sig = inspect.signature(sh.apply_shrinkage_to_panel)
        assert sig.parameters['group_cols'].default == (
            'bank_type', 'bank_province', 'year')

    def test_missing_year_column_raises(self):
        df = pd.DataFrame({
            'benefit_mean_full': [0.1, 0.2],
            'n_articles': [5, 5],
            'bank_type': ['A', 'A'],
            'bank_province': ['P', 'P'],
        })
        with pytest.raises(KeyError, match='year'):
            sh.apply_shrinkage_to_panel(df)

    def test_no_cross_year_leakage(self):
        """同 (type,province) 两年符号相反: 收缩目标=同年截面组均值,
        2017 行不得被 2018 (未来) 信息拉向 pooled 0。"""
        df = pd.DataFrame({
            'benefit_mean_full': [0.9, 1.0, 1.1, 1.0, -0.9, -1.0, -1.1, -1.0],
            'n_articles': [1, 2, 1, 2, 1, 2, 1, 2],
            'bank_type': ['city'] * 8,
            'bank_province': ['P1'] * 8,
            'year': [2017] * 4 + [2018] * 4,
        })
        out = sh.apply_shrinkage_to_panel(df, std_col=None)
        shrunk_2017 = out.loc[out['year'] == 2017, 'benefit_mean_full_shrunk']
        shrunk_2018 = out.loc[out['year'] == 2018, 'benefit_mean_full_shrunk']
        assert (shrunk_2017 > 0.5).all(), "2017 行被未来年份信息污染 (跨年泄漏)"
        assert (shrunk_2018 < -0.5).all()

    def test_std_col_auto_used_for_sampling_var(self):
        """std_col='auto' 用 benefit_std_full²/n 作 σ̂²ᵢ: 高离散行权重更大。"""
        df = pd.DataFrame({
            'benefit_mean_full': [0.0, 0.5, 1.0, 1.5],
            'benefit_std_full': [0.1, 0.1, 0.1, 3.0],
            'n_articles': [10, 10, 10, 10],
            'bank_type': ['A'] * 4,
            'bank_province': ['P'] * 4,
            'year': [2017] * 4,
        })
        out = sh.apply_shrinkage_to_panel(df)
        w = out['benefit_mean_full_shrunk_weight']
        assert w.iloc[3] > w.iloc[0], (
            "benefit_std 大 (测量噪) 的行应被更强收缩 (σ̂²ᵢ=std²/n 生效)")

    def test_std_col_none_falls_back_to_proxy(self):
        """std_col=None → 强制 grand_var/n 代理 (legacy), 不读 benefit_std_full。"""
        df = pd.DataFrame({
            'benefit_mean_full': [0.0, 0.5, 1.0, 1.5],
            'benefit_std_full': [0.1, 0.1, 0.1, 3.0],
            'n_articles': [10, 10, 10, 10],
            'bank_type': ['A'] * 4,
            'bank_province': ['P'] * 4,
            'year': [2017] * 4,
        })
        out = sh.apply_shrinkage_to_panel(df, std_col=None)
        w = out['benefit_mean_full_shrunk_weight']
        # 代理 σ̂²ᵢ = grand_var/n 对等 n 行同值 → 权重全相等
        assert w.nunique() == 1
