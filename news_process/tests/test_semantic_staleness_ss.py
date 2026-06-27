"""回归测试: semantic_staleness_ss 第三轨平价上线 (2026-06-21).

权威执行计划: scripts/audit/SEMANTIC_STALENESS_SS_EXECUTION_PLAN_2026-06-21.md (v1.2)。

锁定以下行为 (正向锁, 全部用合成 mock 嵌入, 不调真 SBERT → Phase A 即可跑):
- T1: stage 30a `_build_output_frame` 在 embs_ss 给定时产出 `emb_ss` 列; embs_ss=None 时不含
      该列 (向后兼容, 旧 schema 无 content_ss → 不写 emb_ss)。
- T2: stage 18 `_load_aligned_embeddings` 返 6-tuple (v3.14.0 co-primary 双轨:
      MAIN emb_{full,ctx,ss} + _lg emb_{full,ctx,ss}_lg); 30a parquet 含 emb_ss 列 → embs_ss 为
      ndarray, 不含 → None (优雅降级, 镜像 DEFER, 不 fail-loud); emb_*_lg 列缺失 → 三 _lg 段均 None。
- T3: 全语料皆回退 (content_ss≡content_full 整列 → embs_ss==embs_full) 时, 两轨 semantic
      staleness 逐位相等 —— compute_semantic_staleness 仅用 Faiss exact IP + stable argsort,
      无 BLAS 累积浮点, 同一输入数组 → 输出确定相等 (无需 atol)。
      ⚠ 刻意**不**测"部分回退行 semantic_ss==semantic_full": 参照窗口邻居不同 → 该不变量为假
      (见计划 §1.3)。
- T4: `aggregate_to_bank_year` 在 art_df 含 semantic_staleness_ss 时产出 semantic_staleness_ss
      + semantic_highstale_ss (后者经 .replace('staleness','highstale') 自动派生)。

白话: 守住"语义陈旧度"的第三条轨 (银行+金科同句)。第三条轨的语义向量 (emb_ss) 由 stage 30a
新算一份, 行为镜像已有的 ctx 轨; 旧数据没有这份向量时要优雅跳过、不能崩。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast


# ── 合成 fixtures (镜像 test_omni_fix_embed 的 _make_art_df/_make_emb_df 口径) ──
def _art_df(n: int = 3) -> pd.DataFrame:
    """article-level frame: 显式 article_id + target_bank + 日期 (供 30a join 对齐键)."""
    return pd.DataFrame({
        'article_id': list(range(n)),
        'target_bank': [f'银行{i}' for i in range(n)],
        '日期': pd.to_datetime([f'2020-01-0{i + 1}' for i in range(n)]),
    })


def _emb_df(
    art_df: pd.DataFrame, with_ss: bool = True, with_lg: bool = False,
) -> pd.DataFrame:
    """30a 风格 emb parquet: emb_full[i]=[i]*3, emb_ctx[i]=[i+10]*3, emb_ss[i]=[i+20]*3.

    v3.14.0 (2026-06-27, co-primary 双轨): with_lg=True 时同步写 emb_*_lg 孪生列
    (large, 镜像 MAIN 偏移 +100), 供 _load_aligned_embeddings 的 6-tuple _lg 段验证。
    """
    n = len(art_df)
    d = {
        'article_id': list(range(n)),
        'target_bank': list(art_df['target_bank']),
        '日期': list(art_df['日期']),
        'emb_full': [np.full(3, float(i), dtype=np.float32) for i in range(n)],
        'emb_ctx': [np.full(3, float(i) + 10.0, dtype=np.float32) for i in range(n)],
    }
    if with_ss:
        d['emb_ss'] = [np.full(3, float(i) + 20.0, dtype=np.float32) for i in range(n)]
    if with_lg:
        d['emb_full_lg'] = [np.full(3, float(i) + 100.0, dtype=np.float32) for i in range(n)]
        d['emb_ctx_lg'] = [np.full(3, float(i) + 110.0, dtype=np.float32) for i in range(n)]
        if with_ss:
            d['emb_ss_lg'] = [np.full(3, float(i) + 120.0, dtype=np.float32) for i in range(n)]
    return pd.DataFrame(d)


# ════════════════════════════════════════════════════════════════════════
# T1 — stage 30a _build_output_frame: emb_ss 列条件写出
# ════════════════════════════════════════════════════════════════════════
class TestBuildOutputFrameEmbSs:
    @staticmethod
    def _df():
        return pd.DataFrame({
            'article_id': [0, 1],
            'target_bank': ['工商', '建设'],
            'year': [2018, 2018],
            '日期': pd.to_datetime(['2020-01-01', '2020-01-02']),
        })

    def test_emb_ss_column_present_when_given(self):
        from news_process.pipeline.text.article_sbert import _build_output_frame
        df = self._df()
        full = np.zeros((2, 3), np.float32)
        ctx = np.ones((2, 3), np.float32)
        ss = np.full((2, 3), 2.0, np.float32)
        out = _build_output_frame(df, full, ctx, ss)
        assert 'emb_ss' in out.columns
        assert np.allclose(np.stack(out['emb_ss'].tolist()), 2.0)
        # 其余轨不受影响
        assert 'emb_full' in out.columns and 'emb_ctx' in out.columns

    def test_emb_ss_column_omitted_when_none(self):
        from news_process.pipeline.text.article_sbert import _build_output_frame
        df = self._df()
        full = np.zeros((2, 3), np.float32)
        ctx = np.ones((2, 3), np.float32)
        out = _build_output_frame(df, full, ctx, None)
        assert 'emb_ss' not in out.columns
        # 向后兼容: full/ctx 仍正常产出
        assert 'emb_full' in out.columns and 'emb_ctx' in out.columns

    def test_emb_ss_default_arg_omits_column(self):
        # 不传 embs_ss (默认 None) → 等价旧两轨签名, 不产 emb_ss
        from news_process.pipeline.text.article_sbert import _build_output_frame
        df = self._df()
        out = _build_output_frame(df, np.zeros((2, 3), np.float32), np.ones((2, 3), np.float32))
        assert 'emb_ss' not in out.columns


# ════════════════════════════════════════════════════════════════════════
# T2 — stage 18 _load_aligned_embeddings: 6-tuple (MAIN + _lg co-primary) +
#      emb_ss / emb_*_lg 列存在性优雅降级
# ════════════════════════════════════════════════════════════════════════
class TestLoadAlignedEmbeddingsSs:
    def test_returns_embs_ss_when_column_present(self, tmp_path):
        from news_process.pipeline.text.article_staleness import _load_aligned_embeddings
        art = _art_df(3)
        emb = _emb_df(art, with_ss=True)
        p = tmp_path / '25_article_embeddings.parquet'
        emb.to_parquet(p, index=False)
        full, ctx, ss, full_lg, ctx_lg, ss_lg = _load_aligned_embeddings(art, str(p))
        assert ss is not None
        assert ss.shape == (3, 3)
        assert np.allclose(ss[0], 20.0) and np.allclose(ss[2], 22.0)
        # v3.14.0: 旧 30a parquet 无 emb_*_lg 列 → 三 _lg 段均优雅 None (向后兼容)
        assert full_lg is None and ctx_lg is None and ss_lg is None

    def test_returns_lg_twins_when_columns_present(self, tmp_path):
        # v3.14.0 co-primary 双轨: 30a 含 emb_*_lg 列 → 三 _lg 段为 ndarray (镜像 MAIN)
        from news_process.pipeline.text.article_staleness import _load_aligned_embeddings
        art = _art_df(3)
        emb = _emb_df(art, with_ss=True, with_lg=True)
        p = tmp_path / '25_article_embeddings.parquet'
        emb.to_parquet(p, index=False)
        full, ctx, ss, full_lg, ctx_lg, ss_lg = _load_aligned_embeddings(art, str(p))
        # MAIN 段不受影响
        assert full.shape == (3, 3) and ctx.shape == (3, 3) and ss.shape == (3, 3)
        # _lg 孪生段就位 (large, +100 偏移)
        assert full_lg is not None and full_lg.shape == (3, 3)
        assert np.allclose(full_lg[0], 100.0) and np.allclose(full_lg[2], 102.0)
        assert ctx_lg is not None and np.allclose(ctx_lg[0], 110.0)
        assert ss_lg is not None and np.allclose(ss_lg[0], 120.0)

    def test_returns_none_when_emb_ss_absent(self, tmp_path):
        # 旧 30a parquet (无 emb_ss 列) → embs_ss=None (向后兼容, 不 fail-loud)
        from news_process.pipeline.text.article_staleness import _load_aligned_embeddings
        art = _art_df(3)
        emb = _emb_df(art, with_ss=False)
        p = tmp_path / '25_article_embeddings.parquet'
        emb.to_parquet(p, index=False)
        full, ctx, ss, full_lg, ctx_lg, ss_lg = _load_aligned_embeddings(art, str(p))
        assert ss is None
        # 其余两轨不受影响
        assert full.shape == (3, 3) and ctx.shape == (3, 3)
        # _lg 列亦缺 → 三 _lg 段 None
        assert full_lg is None and ctx_lg is None and ss_lg is None

    def test_emb_ss_dim_differs_loads_ok(self, tmp_path):
        # v3.14.0 (co-primary 双轨): _stack_track 改为仅核行数防错位, 维度可不同
        # (MAIN 与 _lg 同为 3072, 但函数不假设维度)。故 emb_ss 维度 ≠ emb_full 不再
        # fail-loud — 旧 P2 维度守卫已随双轨化撤除 (见 article_staleness.py::_stack_track
        # docstring "维度可不同... 仅核行数防错位")。
        from news_process.pipeline.text.article_staleness import _load_aligned_embeddings
        art = _art_df(3)
        emb = _emb_df(art, with_ss=True)
        emb['emb_ss'] = [np.zeros(5, dtype=np.float32) for _ in range(3)]  # 5 维 vs emb_full 3 维
        p = tmp_path / '25_article_embeddings.parquet'
        emb.to_parquet(p, index=False)
        full, ctx, ss, *_lg = _load_aligned_embeddings(art, str(p))
        # 行数相符 → 正常加载 (维度不再守卫); emb_ss 按其原 5 维 stack
        assert ss is not None and ss.shape == (3, 5)
        assert full.shape == (3, 3)

    def test_emb_ss_row_mismatch_fails_loud(self, tmp_path):
        # 存活守卫: 行数错位 (而非维度) 仍 fail-loud, 防文章-向量静默错配喂给 Faiss。
        # 构造 emb_ss 行数 ≠ emb_full: 直接写一个 emb_ss 列, 其每行元素是错位的标量
        # 不可行 (stack 形状由内容定), 改用上游行数检查路径 — 此处验 30a 行数 != art_df
        # 行数的总行数守卫 (与 emb_ss 同族, 同 sys.exit(1))。
        from news_process.pipeline.text.article_staleness import _load_aligned_embeddings
        art = _art_df(3)
        emb = _emb_df(art, with_ss=True).iloc[:2].copy()  # 30a 行数 2 != art_df 行数 3
        p = tmp_path / '25_article_embeddings.parquet'
        emb.to_parquet(p, index=False)
        with pytest.raises(SystemExit):
            _load_aligned_embeddings(art, str(p))


# ════════════════════════════════════════════════════════════════════════
# T3 — 全语料皆回退: embs_ss==embs_full → semantic staleness 逐位相等
# ════════════════════════════════════════════════════════════════════════
class TestFullFallbackEquivalence:
    def test_whole_corpus_fallback_ss_equals_full(self):
        pytest.importorskip('faiss')
        from news_process.pipeline.text.article_staleness import compute_semantic_staleness
        # 日期跨多天, 使部分行有 [d-7d, d) 非空窗 (产非 NaN 值, 真正走 max-cosine 路径)
        dates = ['2020-01-01', '2020-01-02', '2020-01-03',
                 '2020-01-05', '2020-01-08', '2020-01-09']
        df = pd.DataFrame({'日期': pd.to_datetime(dates)})
        rng = np.arange(6 * 4, dtype=np.float32).reshape(6, 4)
        # 单位归一化 (cosine 友好; 但等价性与归一化无关 —— 同输入数组同输出)
        embs_full = rng / np.linalg.norm(rng, axis=1, keepdims=True)
        embs_ss = embs_full.copy()  # 模拟 content_ss≡content_full 整列回退
        s_full = compute_semantic_staleness(df, embs_full)
        s_ss = compute_semantic_staleness(df, embs_ss)
        # assert_array_equal 视同位置 NaN 为相等; 同确定性函数 + 同输入 → 逐位等
        np.testing.assert_array_equal(s_ss, s_full)
        # 句法守卫: 至少有一行非 NaN (否则等价性空洞)
        assert np.isfinite(s_full).any()


# ════════════════════════════════════════════════════════════════════════
# T4 — aggregate_to_bank_year: semantic_staleness_ss → +semantic_highstale_ss
# ════════════════════════════════════════════════════════════════════════
class TestAggregateSemanticSs:
    def test_panel_gains_both_ss_columns(self):
        from news_process.pipeline.text.article_staleness import aggregate_to_bank_year
        df = pd.DataFrame({
            'target_bank': ['工商', '工商', '建设'],
            'year': [2018, 2018, 2018],
            'semantic_staleness_ss': [0.1, 0.95, 0.5],
        })
        panel = aggregate_to_bank_year(df)
        assert 'semantic_staleness_ss' in panel.columns
        # highstale 由 .replace('staleness','highstale') 自动派生 (一处改动出两列)
        assert 'semantic_highstale_ss' in panel.columns
        # 工商: mean(0.1, 0.95) = 0.525; highstale = mean(0.0, 1.0) = 0.5
        gs = panel[panel['target_bank'] == '工商'].iloc[0]
        assert gs['semantic_staleness_ss'] == pytest.approx(0.525)
        assert gs['semantic_highstale_ss'] == pytest.approx(0.5)


# ════════════════════════════════════════════════════════════════════════
# T5 — call-site None 守卫的必要性 (证 main():605 的 `if embs_ss is not None` 不可删)
# ════════════════════════════════════════════════════════════════════════
class TestNoneGuardNecessity:
    """守 article_staleness.py main() 的 call-site None 守卫: compute_semantic_staleness
    无内部 None 守卫, 传 None 必崩 → 证 main() 的 `if embs_ss is not None` 是 load-bearing,
    不可删/不可内移 (旧 30a parquet 无 emb_ss → embs_ss=None 时必须在调用点拦)。"""

    def test_compute_semantic_staleness_crashes_on_none(self):
        pytest.importorskip('faiss')
        from news_process.pipeline.text.article_staleness import compute_semantic_staleness
        df = pd.DataFrame({'日期': pd.to_datetime(['2020-01-01', '2020-01-02'])})
        # embeddings=None → 内部 embeddings.shape 解包即崩 (无 None 守卫); 故守卫必在 call-site
        with pytest.raises((AttributeError, TypeError)):
            compute_semantic_staleness(df, None)

    def test_load_then_guard_chain_skips_when_no_emb_ss(self, tmp_path):
        # 端到端契约: 旧 30a parquet (无 emb_ss) → _load 返 None → 守卫跳过 (镜像 main() 逻辑)
        from news_process.pipeline.text.article_staleness import (
            _load_aligned_embeddings,
            compute_semantic_staleness,
        )
        art = _art_df(3)
        emb = _emb_df(art, with_ss=False)  # 旧 schema: 无 emb_ss
        p = tmp_path / '25_article_embeddings.parquet'
        emb.to_parquet(p, index=False)
        # v3.14.0 6-tuple unpack (MAIN 三 + _lg 三); 旧 schema 无 emb_ss/emb_*_lg → 全 None
        _full, _ctx, embs_ss, *_lg = _load_aligned_embeddings(art, str(p))
        # main() 的守卫: 仅 embs_ss is not None 才 compute → 此处 None, 不调用, semantic_ss 不产
        produced = {}
        if embs_ss is not None:  # 镜像 article_staleness.py:605
            produced['semantic_staleness_ss'] = compute_semantic_staleness(art, embs_ss)
        assert 'semantic_staleness_ss' not in produced  # 优雅缺席 = 向后兼容
