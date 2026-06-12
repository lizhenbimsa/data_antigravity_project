"""回归测试: omni-fix g-embed 组修复 (2026-06-11).

锁定以下修复行为 (权威裁决: scripts/audit/_omni_fix/g-embed.json):
- g-embed-01: compute_semantic_staleness 窗口改日粒度 [d-7d, d) 且严格排除同日行
  (对齐 surface 轨 `day < d` 语义; 同 docid 跨行复制行不再机械得 1.0)
- g-embed-02: Tetlock 2011 构念保真披露 — '原文 cosine 范式' 误称清除 (源码文本锁)
- g-embed-03/09: stage 18 消费 30a 改 article_id 显式 join (长度/键/辅键不一致
  fail-loud); 30a 产出端新增 model_id/model_revision/text_pipeline_version provenance
- g-embed-04 (+KNOWN-OPEN⑧): embed_texts / encode_local 多块池化改 "逐块 L2 归一 +
  token 数加权" (尾段碎片不再获整段同权); encode_local 超模型 max_seq_length 文本
  按自身 tokenizer 分块防静默截断 (不超长直送, 与旧实现逐位一致)
- g-embed-05: article_sbert 模型真单源 = config embedding_robustness.model
  (+ 可选 revision 钉死); 不再读不存在的 'embedding' 顶级键
- g-embed-06/08: bank-year 聚合 *平均域* 收缩到 verified 面板语料
  (_restrict_to_panel_domain; 参照窗口仍用 stage-13 全集)
- g-embed-07: ensure_torch_determinism 共享硬化 (encode_local / encode_articles 接线)

外部依赖处理: 无网络调用; SBERT 模型用 fake (注入 _LOCAL_MODELS); faiss/datasketch/
tiktoken 为已装本地包; torch 测试 importorskip。
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast

import news_process  # noqa: E402

_PKG = Path(news_process.__file__).parent


def _read_src(*rel_parts: str) -> str:
    return (_PKG.joinpath(*rel_parts)).read_text(encoding='utf-8')


# ════════════════════════════════════════════════════════════════════════
# g-embed-01: semantic staleness 同日行排除 (日粒度窗口)
# ════════════════════════════════════════════════════════════════════════

class TestSemanticStalenessSameDayExclusion:
    """fix(omni-g-embed-01): 窗口 = [d-7d, d) 日粒度, 同日行不互为候选."""

    @staticmethod
    def _compute(dates, embs):
        pytest.importorskip('faiss')
        from news_process.pipeline.text.article_staleness import (
            compute_semantic_staleness,
        )
        df = pd.DataFrame({'日期': pd.to_datetime(dates)})
        return compute_semantic_staleness(df, np.asarray(embs, dtype=np.float32))

    def test_same_day_dup_rows_not_mechanically_one(self):
        # day2 两行 embedding 相同 (同 docid 复制行场景), 与 day1 行正交。
        # 旧 bug: 第 3 行窗口含同日第 2 行 → cosine=1.0; 修后两行只看 day1 → 0.0。
        stale = self._compute(
            ['2020-01-01', '2020-01-02', '2020-01-02'],
            [[1, 0, 0], [0, 1, 0], [0, 1, 0]],
        )
        assert np.isnan(stale[0])  # 首日无前邻
        assert stale[1] == pytest.approx(0.0, abs=1e-6)
        assert stale[2] == pytest.approx(0.0, abs=1e-6), (
            f"同日 dup 行不应机械得 1.0, 实际 {stale[2]}"
        )
        # 同日两行口径对称 (不再依赖任意行序决定谁得 1.0)
        assert stale[1] == pytest.approx(stale[2], abs=1e-6)

    def test_first_day_same_day_dups_are_nan(self):
        # 首日同日 dup: 窗口空 → NaN (与 surface 轨空窗口口径一致; 旧 bug 第 2 行=1.0)
        stale = self._compute(
            ['2020-01-01', '2020-01-01'],
            [[1, 0], [1, 0]],
        )
        assert np.isnan(stale).all()

    def test_cross_day_duplicate_within_window_still_one(self):
        # 防过度击杀: 跨日 (2d) 重复文章仍应得 ~1.0
        stale = self._compute(
            ['2020-01-01', '2020-01-03'],
            [[0, 1], [0, 1]],
        )
        assert np.isnan(stale[0])
        assert stale[1] == pytest.approx(1.0, abs=1e-5)

    def test_8d_apart_outside_window_nan(self):
        # cutoff = d - 7d; 8d 前的行被排除 → 窗口空 → NaN
        stale = self._compute(
            ['2020-01-01', '2020-01-09'],
            [[1, 0], [1, 0]],
        )
        assert np.isnan(stale[1])

    def test_all_nat_dates_all_nan(self):
        stale = self._compute([None, None, None], [[1, 0]] * 3)
        assert np.isnan(stale).all()


# ════════════════════════════════════════════════════════════════════════
# g-embed-02: Tetlock 构念保真披露 (源码文本锁, 防静默 revert)
# ════════════════════════════════════════════════════════════════════════

class TestTetlockDisclosureSourceLock:
    def test_misnomer_removed_and_disclosure_present(self):
        src = _read_src('pipeline', 'text', 'article_staleness.py')
        assert '原文 cosine 范式' not in src, (
            "g-embed-02 revert: Tetlock 2011 是同公司 72h 词重叠率, "
            "SBERT cosine 不得再称'原文范式'"
        )
        assert '构念保真披露' in src
        assert 'fix(omni-g-embed-02' in src
        # corpus-level 匹配域偏离须留在披露中
        assert 'corpus-level' in src


# ════════════════════════════════════════════════════════════════════════
# g-embed-03/09: 30a embeddings 按 article_id 显式 join (消费端)
# ════════════════════════════════════════════════════════════════════════

def _make_art_df(n: int = 4) -> pd.DataFrame:
    return pd.DataFrame({
        'target_bank': [f'银行{i}' for i in range(n)],
        '日期': pd.to_datetime([f'2020-01-0{i + 1}' for i in range(n)]),
    })


def _make_emb_df(art_df: pd.DataFrame, order=None, **extra) -> pd.DataFrame:
    """构造 30a 风格 emb parquet frame; emb_full[id] = [id]*3, emb_ctx[id] = [id+10]*3."""
    ids = list(range(len(art_df))) if order is None else list(order)
    df = pd.DataFrame({
        'article_id': ids,
        'target_bank': [art_df['target_bank'].iloc[i] for i in ids],
        '日期': [art_df['日期'].iloc[i] for i in ids],
        'emb_full': [np.full(3, float(i), dtype=np.float32) for i in ids],
        'emb_ctx': [np.full(3, float(i) + 10.0, dtype=np.float32) for i in ids],
    })
    for k, v in extra.items():
        df[k] = v
    return df


class TestLoadAlignedEmbeddings:
    """fix(omni-g-embed-03/09): 裸位置对齐 → article_id 键 join + fail-loud."""

    def test_shuffled_rows_realigned_by_article_id(self, tmp_path):
        from news_process.pipeline.text.article_staleness import (
            _load_aligned_embeddings,
        )
        art_df = _make_art_df(4)
        emb_df = _make_emb_df(art_df, order=[2, 0, 3, 1])  # 行序与 art_df 不同
        p = tmp_path / '30a_article_embeddings.parquet'
        emb_df.to_parquet(p, index=False)
        embs_full, embs_ctx = _load_aligned_embeddings(art_df, str(p))
        for i in range(4):
            # 旧位置对齐: embs_full[0] 会是 [2,2,2] (错配); join 后必须按 id 还原
            assert np.allclose(embs_full[i], float(i)), f"row {i} 错配: {embs_full[i]}"
            assert np.allclose(embs_ctx[i], float(i) + 10.0)

    def test_length_mismatch_fails_loud(self, tmp_path):
        from news_process.pipeline.text.article_staleness import (
            _load_aligned_embeddings,
        )
        art_df = _make_art_df(4)
        emb_df = _make_emb_df(art_df).iloc[:3]  # 30a 陈旧: 行数变短
        p = tmp_path / '30a.parquet'
        emb_df.to_parquet(p, index=False)
        with pytest.raises(SystemExit):
            _load_aligned_embeddings(art_df, str(p))

    def test_missing_article_id_column_fails_loud(self, tmp_path):
        from news_process.pipeline.text.article_staleness import (
            _load_aligned_embeddings,
        )
        art_df = _make_art_df(3)
        emb_df = _make_emb_df(art_df).drop(columns=['article_id'])
        p = tmp_path / '30a.parquet'
        emb_df.to_parquet(p, index=False)
        with pytest.raises(SystemExit):
            _load_aligned_embeddings(art_df, str(p))

    def test_duplicate_article_id_fails_loud(self, tmp_path):
        from news_process.pipeline.text.article_staleness import (
            _load_aligned_embeddings,
        )
        art_df = _make_art_df(3)
        emb_df = _make_emb_df(art_df)
        emb_df.loc[2, 'article_id'] = 0  # 键重复 + id=2 缺失
        p = tmp_path / '30a.parquet'
        emb_df.to_parquet(p, index=False)
        with pytest.raises(SystemExit):
            _load_aligned_embeddings(art_df, str(p))

    def test_aux_key_mismatch_fails_loud(self, tmp_path):
        # target_bank 逐行不一致 = 两 parquet 非同一 stage-13 快照 (等长陈旧 30a)
        from news_process.pipeline.text.article_staleness import (
            _load_aligned_embeddings,
        )
        art_df = _make_art_df(3)
        emb_df = _make_emb_df(art_df)
        emb_df.loc[1, 'target_bank'] = '幽灵银行'
        p = tmp_path / '30a.parquet'
        emb_df.to_parquet(p, index=False)
        with pytest.raises(SystemExit):
            _load_aligned_embeddings(art_df, str(p))

    def test_model_id_provenance_column_tolerated(self, tmp_path):
        # 新版 30a 带 provenance 列时正常读 (不混入向量, 不崩溃)
        from news_process.pipeline.text.article_staleness import (
            _load_aligned_embeddings,
        )
        art_df = _make_art_df(2)
        emb_df = _make_emb_df(art_df, model_id='shibing624/text2vec-base-chinese')
        p = tmp_path / '30a.parquet'
        emb_df.to_parquet(p, index=False)
        embs_full, _ = _load_aligned_embeddings(art_df, str(p))
        assert embs_full.shape == (2, 3)

    def test_main_wiring_uses_explicit_join(self):
        src = _read_src('pipeline', 'text', 'article_staleness.py')
        assert '_load_aligned_embeddings(art_df, emb_path)' in src, (
            "g-embed-03/09 revert: main() 必须经 _load_aligned_embeddings 显式 join"
        )
        assert "np.stack(emb_df['emb_full'].tolist())" not in src.split(
            'def _load_aligned_embeddings')[0], "main() 不得再裸位置 np.stack"


# ════════════════════════════════════════════════════════════════════════
# g-embed-03 (产出端) + g-embed-05: 30a provenance 列 + 模型配置真单源
# ════════════════════════════════════════════════════════════════════════

class TestSbertProvenanceAndConfig:
    def test_build_output_frame_has_provenance_columns(self):
        from news_process.pipeline.text import article_sbert as sbert
        df = pd.DataFrame({
            'docid': ['x', 'y'],
            'target_bank': ['A', 'B'],
            'year': [2020, 2021],
            '日期': pd.to_datetime(['2020-01-01', '2021-01-01']),
        })
        embs = np.ones((2, 3), dtype=np.float32)
        out = sbert._build_output_frame(df, embs, embs)
        for col in ('article_id', 'docid', 'model_id', 'model_revision',
                    'text_pipeline_version'):
            assert col in out.columns, f"30a 输出缺 provenance/键列: {col}"
        assert list(out['article_id']) == [0, 1]  # = stage-13 df.index
        assert out['model_id'].iloc[0] == sbert._SBERT_MODEL_ID
        assert out['text_pipeline_version'].iloc[0] == sbert._TEXT_PIPELINE_VERSION

    def test_resolve_model_reads_embedding_robustness(self):
        from news_process.pipeline.text.article_sbert import _resolve_sbert_model
        m, r = _resolve_sbert_model(
            {'embedding_robustness': {'model': 'org/custom-zh', 'revision': 'abc123'}})
        assert (m, r) == ('org/custom-zh', 'abc123')

    def test_resolve_model_default_fallback(self):
        from news_process.pipeline.text.article_sbert import _resolve_sbert_model
        m, r = _resolve_sbert_model({})
        assert m == 'shibing624/text2vec-base-chinese'
        assert r is None

    def test_resolve_model_ignores_phantom_embedding_key(self):
        # 旧 bug: 读不存在的 'embedding' 顶级键 — 修后该键不再被消费
        from news_process.pipeline.text.article_sbert import _resolve_sbert_model
        m, _ = _resolve_sbert_model({'embedding': {'model': 'org/phantom'}})
        assert m == 'shibing624/text2vec-base-chinese'

    def test_source_lock_no_phantom_key_and_determinism_wired(self):
        src = _read_src('pipeline', 'text', 'article_sbert.py')
        assert "get('embedding', {})" not in src, (
            "g-embed-05 revert: 不得再读不存在的 'embedding' 顶级键"
        )
        assert 'embedding_robustness' in src
        assert 'ensure_torch_determinism()' in src, (
            "g-embed-07 revert: encode_articles 推理前须确定性硬化"
        )


# ════════════════════════════════════════════════════════════════════════
# g-embed-06/08: bank-year 聚合域收缩到 verified 面板语料
# ════════════════════════════════════════════════════════════════════════

def _domain_art_df() -> pd.DataFrame:
    return pd.DataFrame({
        'docid': ['d1', 'd2', 'd3', 'd4'],
        'target_bank': ['A', 'A', 'B', 'B'],
        'year': [2020] * 4,
        'surface_staleness_full': [0.1, 0.9, 0.5, 0.7],
    })


class TestRestrictToPanelDomain:
    """fix(omni-g-embed-06/08): 平均域 = (docid, target_bank) ∩ verified 语料."""

    def test_filters_to_verified_keys_via_herd_decay(self, tmp_path):
        from news_process.pipeline.text.article_staleness import (
            _restrict_to_panel_domain,
        )
        art_df = _domain_art_df()
        ver = pd.DataFrame({'docid': ['d1', 'd3'], 'target_bank': ['A', 'B']})
        ver.to_parquet(tmp_path / '24_herd_decay.parquet', index=False)
        out = _restrict_to_panel_domain(art_df, str(tmp_path))
        assert sorted(out['docid']) == ['d1', 'd3'], (
            "未验证文章 (d2/d4) 不得进入 bank-year 平均域"
        )

    def test_key_match_requires_both_docid_and_bank(self, tmp_path):
        # 同 docid 不同 bank 的复制行: 只有 verified 的 (docid, bank) 组合保留
        from news_process.pipeline.text.article_staleness import (
            _restrict_to_panel_domain,
        )
        art_df = pd.DataFrame({
            'docid': ['d1', 'd1'],
            'target_bank': ['A', 'B'],
            'year': [2020, 2020],
            'surface_staleness_full': [0.2, 0.3],
        })
        ver = pd.DataFrame({'docid': ['d1'], 'target_bank': ['A']})
        ver.to_parquet(tmp_path / '24_herd_decay.parquet', index=False)
        out = _restrict_to_panel_domain(art_df, str(tmp_path))
        assert len(out) == 1 and out['target_bank'].iloc[0] == 'A'

    def test_falls_back_to_tone_llms_when_herd_missing(self, tmp_path):
        from news_process.pipeline.text.article_staleness import (
            _restrict_to_panel_domain,
        )
        art_df = _domain_art_df()
        ver = pd.DataFrame({'docid': ['d2'], 'target_bank': ['A']})
        ver.to_parquet(tmp_path / '21_tone_llms.parquet', index=False)
        out = _restrict_to_panel_domain(art_df, str(tmp_path))
        assert list(out['docid']) == ['d2']

    def test_degrades_to_full_set_when_no_verified_files(self, tmp_path):
        # 两文件均缺: ERROR 披露口径降级, 返回全集 (不静默丢数据、不崩溃)
        from news_process.pipeline.text.article_staleness import (
            _restrict_to_panel_domain,
        )
        art_df = _domain_art_df()
        out = _restrict_to_panel_domain(art_df, str(tmp_path))
        assert len(out) == len(art_df)

    def test_degrades_when_keys_missing_in_art_df(self, tmp_path):
        from news_process.pipeline.text.article_staleness import (
            _restrict_to_panel_domain,
        )
        art_df = _domain_art_df().drop(columns=['docid'])
        out = _restrict_to_panel_domain(art_df, str(tmp_path))
        assert len(out) == len(art_df)

    def test_main_wiring_restricts_before_aggregation(self):
        src = _read_src('pipeline', 'text', 'article_staleness.py')
        assert ('aggregate_to_bank_year(_restrict_to_panel_domain(art_df, output_dir))'
                in src), "g-embed-06/08 revert: 聚合前必须收缩平均域"


# ════════════════════════════════════════════════════════════════════════
# g-embed-04 (+KNOWN-OPEN⑧): embed_texts 多块池化 — 逐块 L2 归一 + token 数加权
# ════════════════════════════════════════════════════════════════════════

class TestEmbedTextsChunkPooling:
    def test_tail_fragment_chunk_downweighted(self, monkeypatch):
        from news_process.pipeline.text import embedding_engine as eng
        # 8200 token → 恰 2 块 (8191 + 9-token 碎片尾段, 老 bug 下尾段占 50% 方向权重)
        long_text = ' a' * 8200
        n_tok = len(eng._EMB_ENCODING.encode(long_text))
        assert n_tok > eng.EMB_MAX_TOKENS, "测试前提: 文本须超长"
        assert n_tok - eng.EMB_MAX_TOKENS < 50, "测试前提: 尾段须是碎片块"
        chunks = eng.split_text_for_embedding(long_text)
        assert len(chunks) == 2

        # chunk0 (≈8191 tok) → [1,0]; chunk1 (尾段) → [0,100] (大范数, 老 bug 双重放大源)
        def _fake_encode_local(texts, spec, *, log_prefix='Embedding'):
            out = []
            for t in texts:
                out.append([1.0, 0.0] if t == chunks[0] else [0.0, 100.0])
            return np.asarray(out, dtype=np.float32)

        monkeypatch.setattr(eng, 'encode_local', _fake_encode_local)
        spec = {'base_url': 'local', 'model': 'fake-t2v'}
        emb = eng.embed_texts([long_text], spec)
        assert emb is not None and emb.shape == (1, 2)
        # 旧等权 mean: [0.5, 50] → 归一后尾段方向 ≈ 1.0 (碎片+大范数双重主导)。
        # 修后: 逐块 L2 归一 + token 数加权 → 主段方向主导。
        assert emb[0, 0] > 0.999, f"主段应主导池化方向, 实际 {emb[0]}"
        assert abs(emb[0, 1]) < 0.01

    def test_short_text_passthrough_bitwise_unchanged(self, monkeypatch):
        from news_process.pipeline.text import embedding_engine as eng

        def _fake_encode_local(texts, spec, *, log_prefix='Embedding'):
            return np.asarray([[3.0, 4.0]] * len(texts), dtype=np.float32)

        monkeypatch.setattr(eng, 'encode_local', _fake_encode_local)
        emb = eng.embed_texts(['短文本'], {'base_url': 'local', 'model': 'fake'})
        # 单块直通: 不归一不加权, 与旧实现逐位一致 (缓存键/已存向量不受影响)
        assert np.array_equal(emb, np.asarray([[3.0, 4.0]], dtype=np.float32))


# ════════════════════════════════════════════════════════════════════════
# g-embed-04 (local 轨) + g-embed-07: encode_local 按模型 max_seq_length 分块
# ════════════════════════════════════════════════════════════════════════

class _FakeTokenizer:
    def encode(self, text, add_special_tokens=False):
        return text.split()

    def decode(self, ids, skip_special_tokens=True):
        return ' '.join(ids)


class _FakeLocalModel:
    max_seq_length = 8  # effective_max = 6 (留 [CLS]/[SEP])
    tokenizer = _FakeTokenizer()

    def __init__(self, vec_map):
        self._vec_map = vec_map

    def encode(self, chunks, batch_size=32, show_progress_bar=False):
        return np.asarray([self._vec_map[c] for c in chunks], dtype=np.float32)


class TestEncodeLocalChunking:
    _LONG = 'w0 w1 w2 w3 w4 w5 w6 w7 w8 w9'   # 10 词 → 块 (6 词) + (4 词)
    _C0 = 'w0 w1 w2 w3 w4 w5'
    _C1 = 'w6 w7 w8 w9'
    _SHORT = 'w0 w1'

    def _spec_and_model(self, monkeypatch):
        from news_process.pipeline.text import embedding_engine as eng
        calls = []
        monkeypatch.setattr(
            eng, 'ensure_torch_determinism', lambda *a, **k: calls.append(1))
        model = _FakeLocalModel({
            self._C0: [2.0, 0.0],     # 非单位范数 → 验证逐块 L2 归一
            self._C1: [0.0, 8.0],
            self._SHORT: [3.0, 4.0],
        })
        monkeypatch.setitem(eng._LOCAL_MODELS, 'fake-pool-model', model)
        spec = {'base_url': 'local', 'model': 'fake-pool-model', 'batch_size': 4}
        return eng, spec, calls

    def test_overlength_text_chunked_and_weighted(self, monkeypatch):
        pytest.importorskip('sentence_transformers')
        eng, spec, calls = self._spec_and_model(monkeypatch)
        out = eng.encode_local([self._LONG], spec)
        # 期望: 单位向量 [1,0]/[0,1], 权重 6/4 → pooled [0.6,0.4] → L2 归一
        expected = np.array([0.6, 0.4]) / np.linalg.norm([0.6, 0.4])
        assert out.shape == (1, 2)
        assert np.allclose(out[0], expected, atol=1e-5), (
            f"分块加权池化错误: {out[0]} vs {expected} "
            "(旧 bug: 超长文本被模型静默截断到首段)"
        )
        assert calls, "g-embed-07 revert: encode_local 须先调 ensure_torch_determinism"

    def test_short_text_direct_passthrough(self, monkeypatch):
        pytest.importorskip('sentence_transformers')
        eng, spec, _ = self._spec_and_model(monkeypatch)
        out = eng.encode_local([self._SHORT], spec)
        # 不超长 → 原样直送, 与旧实现逐位一致 (不归一)
        assert np.array_equal(out, np.asarray([[3.0, 4.0]], dtype=np.float32))

    def test_mixed_batch_short_rows_unscaled(self, monkeypatch):
        pytest.importorskip('sentence_transformers')
        eng, spec, _ = self._spec_and_model(monkeypatch)
        out = eng.encode_local([self._SHORT, self._LONG], spec)
        assert out.shape == (2, 2)
        assert np.allclose(out[0], [3.0, 4.0])  # 单块行不被归一/加权
        expected = np.array([0.6, 0.4]) / np.linalg.norm([0.6, 0.4])
        assert np.allclose(out[1], expected, atol=1e-5)

    def test_model_without_tokenizer_falls_back_to_direct(self, monkeypatch):
        # 测试 fake / 旧模型无 tokenizer 元数据 → 旧行为直送 (防过度击杀)
        pytest.importorskip('sentence_transformers')
        from news_process.pipeline.text import embedding_engine as eng
        monkeypatch.setattr(eng, 'ensure_torch_determinism', lambda *a, **k: None)

        class _NoTok:
            max_seq_length = 8
            tokenizer = None

            def encode(self, chunks, batch_size=32, show_progress_bar=False):
                return np.asarray([[1.0, 2.0]] * len(chunks), dtype=np.float32)

        monkeypatch.setitem(eng._LOCAL_MODELS, 'fake-notok-model', _NoTok())
        out = eng.encode_local(
            ['任意 文本'], {'base_url': 'local', 'model': 'fake-notok-model'})
        assert np.array_equal(out, np.asarray([[1.0, 2.0]], dtype=np.float32))


# ════════════════════════════════════════════════════════════════════════
# g-embed-07: ensure_torch_determinism 行为
# ════════════════════════════════════════════════════════════════════════

class TestTorchDeterminism:
    def test_sets_torch_deterministic_flags(self, monkeypatch):
        torch = pytest.importorskip('torch')
        from news_process.pipeline.text import embedding_engine as eng
        monkeypatch.setattr(eng, '_TORCH_DETERMINISM_DONE', False)
        eng.ensure_torch_determinism(seed=123)
        assert torch.are_deterministic_algorithms_enabled(), (
            "g-embed-07: use_deterministic_algorithms 须开启"
        )
        assert eng._TORCH_DETERMINISM_DONE is True

    def test_idempotent_second_call_noop(self, monkeypatch):
        pytest.importorskip('torch')
        from news_process.pipeline.text import embedding_engine as eng
        monkeypatch.setattr(eng, '_TORCH_DETERMINISM_DONE', True)
        eng.ensure_torch_determinism(seed=999)  # 已设过 → 直接返回, 不重播种


# ════════════════════════════════════════════════════════════════════════
# 集成冒烟: 修复后 stage-18 聚合链路在合成数据上端到端可跑
# ════════════════════════════════════════════════════════════════════════

class TestAggregationSmoke:
    def test_aggregate_after_domain_restriction(self, tmp_path):
        from news_process.pipeline.text.article_staleness import (
            _restrict_to_panel_domain,
            aggregate_to_bank_year,
        )
        art_df = _domain_art_df()
        ver = pd.DataFrame({'docid': ['d1', 'd3'], 'target_bank': ['A', 'B']})
        ver.to_parquet(os.path.join(tmp_path, '24_herd_decay.parquet'), index=False)
        panel = aggregate_to_bank_year(_restrict_to_panel_domain(art_df, str(tmp_path)))
        assert len(panel) == 2  # (A,2020) + (B,2020)
        a_row = panel[panel['target_bank'] == 'A']
        # A 的均值只含 verified d1 (0.1), 未验证 d2 (0.9) 不进平均域
        assert a_row['surface_staleness_full'].iloc[0] == pytest.approx(0.1)
