"""benefit 4 维度分解 六轨扩展 gate 测试 (2026-07-03, ROBUSTNESS_GAP_BACKFILL 计划 §3 B3)。

六轨 = {full, ctx, ss} × {MAIN Qwen, '_lg' large}; 列名 SSOT = ``_dim_col``
(``benefit_<dim><suffix>_<track>``, **lg 中置**)。⚠ 铁律: MAIN 与 _lg co-primary
互为稳健性 both-or-neither (无单边孤儿); 各轨 just-identified 并排, 禁混同一
over-identified Hansen J。维度列停留孤儿 parquet (27_benefit_dimensions_panel),
不进主面板 → 主面板 parity 扫描器 (test_embedding_coprimary_parity) 扫不到,
双射断言在本文件内完成 (计划 B2 决策, 防"看似受测实则空转"的假保险)。

覆盖 (计划 B3 八条):
  1. DIMENSION_INDICES 10 锚点全覆盖不重不漏;
  2. 24 列名三方同源 (_dim_col 输出 == 生成端实际列 == merge wanted);
  3. both-or-neither 守卫行为 (单边缺失 → 同族两列同置 NaN);
  4. full/ctx canonical 逐字节不变 (str 键旧式调用 == 元组键新式调用);
     fixture MAIN 与 _lg 用**不同维度** (8 vs 6) — 配对错误在测试内必炸;
  5. _lg 锚点缓存键完整二元组 + main() 级接线 (mock 断言 _lg 调用收到 _lg model_id);
  6. CLI 冒烟 (--track ss / all; 缺 .npy 优雅 skip 返回 0);
  7. merge 桥接 (track='all'+include_lg → 24 列; 'both' 回归锚; 剪枝 tracks 透传);
  8. 空 embedding_large 降级 (剔除 _lg 不崩 MAIN, 无错键缓存查询)。
"""
import json

import numpy as np
import pandas as pd
import pytest

from news_process.papers.benefit_society import dimension_analysis as da

DIMS = ('core_op', 'growth', 'resource', 'compliance')
TRACKS = ('full', 'ctx', 'ss')
_MAIN_DIM, _LG_DIM = 8, 6  # 刻意不同维: 跨 spec 混投影在测试内必炸而非同维静默通过


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def _dirs(dim: int) -> dict:
    """4 维确定性方向向量 (互不平行)。"""
    out = {}
    for i, d in enumerate(DIMS):
        v = np.zeros(dim, dtype=np.float32)
        v[i % dim] = 1.0
        v[(i + 1) % dim] = 0.5
        out[d] = _unit(v)
    return out


DIRS_MAIN, DIRS_LG = _dirs(_MAIN_DIM), _dirs(_LG_DIM)


def _df_exploded(n=6):
    return pd.DataFrame({
        'target_bank': ['工商银行', '工商银行', '建设银行'] * (n // 3),
        'year': [2017, 2018, 2017] * (n // 3),
    })


def _emb(n, dim, seed_row=1.0):
    rng = np.arange(n * dim, dtype=np.float32).reshape(n, dim) + seed_row
    return rng / np.linalg.norm(rng, axis=1, keepdims=True)


class TestDimensionIndices:
    def test_ten_anchors_partition(self):
        idx = [i for tup in da.DIMENSION_INDICES.values() for i in tup]
        assert sorted(idx) == list(range(10)), 'DIMENSION_INDICES 未不重不漏覆盖 10 锚点'
        assert tuple(da.DIMENSION_INDICES) == DIMS


class TestDimColSSOT:
    def test_lg_infix_position(self):
        assert da._dim_col('core_op', '_lg', 'ss') == 'benefit_core_op_lg_ss'
        assert da._dim_col('growth', '', 'full') == 'benefit_growth_full'

    def test_generation_side_matches_ssot(self):
        # 生成端实际列名 == _dim_col 全集 (24 名) — 三方同源之一/二
        df = _df_exploded()
        emb = {(t, ''): _emb(len(df), _MAIN_DIM) for t in TRACKS}
        emb.update({(t, '_lg'): _emb(len(df), _LG_DIM) for t in TRACKS})
        panel = da.compute_dual_track_dimensions(
            df, emb, DIRS_MAIN, directions_by_suffix={'_lg': DIRS_LG})
        got = {c for c in panel.columns if c.startswith('benefit_')}
        want = {da._dim_col(d, s, t) for d in DIMS for s in ('', '_lg') for t in TRACKS}
        assert got == want and len(want) == 24

    def test_merge_wanted_matches_ssot(self):
        # merge wanted 白名单 == _dim_col 全集 — 三方同源之三 (缺列 fail-loud 即证 wanted)
        panel = pd.DataFrame({'target_bank': ['A'], 'year': [2017]})
        dims_ok = pd.DataFrame({
            'target_bank': ['A'], 'year': [2017],
            **{da._dim_col(d, s, t): [0.1]
               for d in DIMS for s in ('', '_lg') for t in TRACKS},
        })
        out = da.merge_dimensions_to_panel(panel, dims_ok, track='all', include_lg=True)
        assert {c for c in out.columns if c.startswith('benefit_')} == {
            da._dim_col(d, s, t) for d in DIMS for s in ('', '_lg') for t in TRACKS}
        with pytest.raises(ValueError, match='lacks columns'):
            da.merge_dimensions_to_panel(
                panel, dims_ok.drop(columns=[da._dim_col('growth', '_lg', 'ss')]),
                track='all', include_lg=True)


class TestBothOrNeither:
    def test_one_sided_lg_nans_both(self):
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2017],
            **{da._dim_col(d, '', t): [0.5] for d in DIMS for t in ('full',)},
            # _lg 侧整体缺列 (单边孤儿场景)
        })
        out = da._apply_both_or_neither(panel, ['full'])
        for d in DIMS:
            assert da._dim_col(d, '_lg', 'full') in out.columns
            assert out[da._dim_col(d, '', 'full')].isna().all(), 'MAIN 侧未随缺失的 _lg 同置 NaN'
            assert out[da._dim_col(d, '_lg', 'full')].isna().all()

    def test_both_sides_valid_untouched(self):
        panel = pd.DataFrame({
            'target_bank': ['A'], 'year': [2017],
            **{da._dim_col(d, s, 'ctx'): [0.3] for d in DIMS for s in ('', '_lg')},
        })
        out = da._apply_both_or_neither(panel, ['ctx'])
        for d in DIMS:
            assert out[da._dim_col(d, '', 'ctx')].iloc[0] == pytest.approx(0.3)
            assert out[da._dim_col(d, '_lg', 'ctx')].iloc[0] == pytest.approx(0.3)


class TestCanonicalUnchanged:
    def test_str_key_legacy_call_equals_tuple_key(self):
        # 旧式 str 键 (MAIN 单 spec) 与新式 ('full','') 元组键逐字节等值 (canonical 锚)
        df = _df_exploded()
        e_full, e_ctx = _emb(len(df), _MAIN_DIM), _emb(len(df), _MAIN_DIM, 2.0)
        legacy = da.compute_dual_track_dimensions(
            df, {'full': e_full, 'ctx': e_ctx}, DIRS_MAIN)
        new = da.compute_dual_track_dimensions(
            df, {('full', ''): e_full, ('ctx', ''): e_ctx}, DIRS_MAIN)
        pd.testing.assert_frame_equal(
            legacy.sort_index(axis=1), new.sort_index(axis=1))
        # 数值 = 归一化嵌入 @ 方向 的 bank-year 均值 (与直接投影一致)
        proj = (e_full / np.linalg.norm(e_full, axis=1, keepdims=True)) @ DIRS_MAIN['core_op']
        manual = pd.DataFrame({'target_bank': df['target_bank'], 'year': df['year'], 'p': proj}) \
            .groupby(['target_bank', 'year'])['p'].mean()
        got = legacy.set_index(['target_bank', 'year'])['benefit_core_op_full']
        for k, v in manual.items():
            assert got[k] == pytest.approx(v)

    def test_cross_spec_projection_fails_loud(self):
        # 4096-vs-3072 同构缩影: _lg 槽位喂 MAIN 维度嵌入 → 显式 ValueError 带 spec 名
        df = _df_exploded()
        with pytest.raises(ValueError, match='spec'):
            da.compute_dual_track_dimensions(
                df, {('full', '_lg'): _emb(len(df), _MAIN_DIM)}, DIRS_MAIN,
                directions_by_suffix={'_lg': DIRS_LG})

    def test_missing_lg_directions_fails_loud(self):
        df = _df_exploded()
        with pytest.raises(ValueError, match='directions_by_suffix'):
            da.compute_dual_track_dimensions(
                df, {('full', '_lg'): _emb(len(df), _LG_DIM)}, DIRS_MAIN)


class TestLgCacheKeys:
    def test_spec_cache_keys_from_spec_dict(self):
        model, ver = da._spec_cache_keys(
            {'model': 'text-embedding-3-large',
             'text_pipeline_version': 'v1-2026-06-27-emb3large'})
        assert (model, ver) == ('text-embedding-3-large', 'v1-2026-06-27-emb3large')

    def test_anchor_embeddings_query_full_tuple(self, tmp_path, monkeypatch):
        # mock LLMCache: 断言 _lg 查询用完整二元组 (model_id, prompt_version)
        seen = []

        class _FakeCache:
            def __init__(self, path):
                pass

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def get(self, model_id, anchor, prompt_version=None):
                seen.append((model_id, prompt_version))
                return json.dumps([0.1] * _LG_DIM)

        import news_process.core.caching as caching
        monkeypatch.setattr(caching, 'LLMCache', _FakeCache)
        db = tmp_path / 'cache.db'
        db.write_text('')
        out = da._get_anchor_embeddings(
            ['锚点甲', '锚点乙'], cache_db_path=str(db),
            model_id='text-embedding-3-large',
            prompt_version='v1-2026-06-27-emb3large')
        assert out.shape == (2, _LG_DIM)
        assert set(seen) == {('text-embedding-3-large', 'v1-2026-06-27-emb3large')}

    def test_resolve_prompt_version_is_main_bound(self):
        # 佐证"禁沿用 _resolve_prompt_version 于 _lg": 它返回 MAIN 版本号 (非 _lg 的)
        v = da._resolve_prompt_version()
        assert v != 'v1-2026-06-27-emb3large'


def _patch_directions(monkeypatch, calls):
    def _fake(pos, neg, *, cache_db_path=None, model_id=None, prompt_version=None):
        calls.append({'model_id': model_id, 'prompt_version': prompt_version})
        return DIRS_LG if model_id == 'text-embedding-3-large' else DIRS_MAIN
    monkeypatch.setattr(da, 'compute_direction_vectors', _fake)
    monkeypatch.setattr(da, '_import_anchors', lambda: (['p'] * 10, ['n'] * 10))


class TestMainWiring:
    def _write_npy(self, d, n, sfx_dims):
        for (sfx, trk), dim in sfx_dims.items():
            np.save(d / f'27_benefit_embeddings{sfx}_{trk}.npy', _emb(n, dim))

    def test_lg_spec_passed_to_direction_vectors(self, tmp_path, monkeypatch):
        calls = []
        _patch_directions(monkeypatch, calls)
        monkeypatch.setattr(da, '_resolve_large_spec', lambda: {
            'model': 'text-embedding-3-large',
            'text_pipeline_version': 'v1-2026-06-27-emb3large'})
        df = _df_exploded()
        dfp = tmp_path / 'exploded.parquet'
        df.to_parquet(dfp)
        self._write_npy(tmp_path, len(df), {('', 'full'): _MAIN_DIM, ('', 'ctx'): _MAIN_DIM,
                                            ('_lg', 'full'): _LG_DIM, ('_lg', 'ctx'): _LG_DIM})
        rc = da.main([
            '--track', 'both', '--include-lg',
            '--df-exploded', str(dfp),
            '--embeddings-dir', str(tmp_path),
            '--text-embeddings-full', str(tmp_path / '27_benefit_embeddings_full.npy'),
            '--text-embeddings-ctx', str(tmp_path / '27_benefit_embeddings_ctx.npy'),
            '--output', str(tmp_path / 'dims.parquet'),
        ])
        assert rc == 0
        assert [c['model_id'] for c in calls] == [None, 'text-embedding-3-large'], \
            '_lg 方向向量未按 spec 单独计算 (main 接线断言)'
        out = pd.read_parquet(tmp_path / 'dims.parquet')
        assert da._dim_col('core_op', '_lg', 'ctx') in out.columns

    def test_empty_lg_spec_degrades_to_main(self, tmp_path, monkeypatch):
        calls = []
        _patch_directions(monkeypatch, calls)
        monkeypatch.setattr(da, '_resolve_large_spec', lambda: {})
        df = _df_exploded()
        dfp = tmp_path / 'exploded.parquet'
        df.to_parquet(dfp)
        self._write_npy(tmp_path, len(df), {('', 'full'): _MAIN_DIM, ('', 'ctx'): _MAIN_DIM})
        rc = da.main([
            '--track', 'both', '--include-lg',
            '--df-exploded', str(dfp),
            '--embeddings-dir', str(tmp_path),
            '--text-embeddings-full', str(tmp_path / '27_benefit_embeddings_full.npy'),
            '--text-embeddings-ctx', str(tmp_path / '27_benefit_embeddings_ctx.npy'),
            '--output', str(tmp_path / 'dims.parquet'),
        ])
        assert rc == 0
        assert [c['model_id'] for c in calls] == [None], '空 _lg spec 仍发生了 _lg 键查询'
        out = pd.read_parquet(tmp_path / 'dims.parquet')
        assert da._dim_col('core_op', '', 'full') in out.columns
        assert da._dim_col('core_op', '_lg', 'full') not in out.columns

    def test_cli_ss_track_smoke(self, tmp_path, monkeypatch):
        calls = []
        _patch_directions(monkeypatch, calls)
        df = _df_exploded()
        dfp = tmp_path / 'exploded.parquet'
        df.to_parquet(dfp)
        self._write_npy(tmp_path, len(df), {('', 'ss'): _MAIN_DIM})
        rc = da.main([
            '--track', 'ss',
            '--df-exploded', str(dfp),
            '--text-embeddings-ss', str(tmp_path / '27_benefit_embeddings_ss.npy'),
            '--output', str(tmp_path / 'dims.parquet'),
        ])
        assert rc == 0
        out = pd.read_parquet(tmp_path / 'dims.parquet')
        assert da._dim_col('growth', '', 'ss') in out.columns

    def test_dir_only_derives_all_slots_same_source(self, tmp_path, monkeypatch):
        # 终审 #1 (dir-同源不变量): 只传 --embeddings-dir 不传任何 --text-embeddings-*
        # → MAIN 与 _lg 六槽全部从该目录派生 (防 MAIN 落 SSOT 默认目录的跨目录混源)
        calls = []
        _patch_directions(monkeypatch, calls)
        monkeypatch.setattr(da, '_resolve_large_spec', lambda: {
            'model': 'text-embedding-3-large',
            'text_pipeline_version': 'v1-2026-06-27-emb3large'})
        df = _df_exploded()
        dfp = tmp_path / 'exploded.parquet'
        df.to_parquet(dfp)
        self._write_npy(tmp_path, len(df), {('', 'full'): _MAIN_DIM, ('', 'ctx'): _MAIN_DIM,
                                            ('_lg', 'full'): _LG_DIM, ('_lg', 'ctx'): _LG_DIM})
        rc = da.main([
            '--track', 'both', '--include-lg',
            '--df-exploded', str(dfp),
            '--embeddings-dir', str(tmp_path),
            '--output', str(tmp_path / 'dims.parquet'),
        ])
        assert rc == 0
        out = pd.read_parquet(tmp_path / 'dims.parquet')
        # MAIN 与 _lg 列全部产出且非空 → 六槽路径均从 dir 解析 (SSOT 默认目录无这些 tmp 数据)
        for sfx in ('', '_lg'):
            for trk in ('full', 'ctx'):
                col = da._dim_col('core_op', sfx, trk)
                assert col in out.columns and out[col].notna().any(), \
                    f'{col} 缺失/全空 — --embeddings-dir 未对该槽生效 (跨目录混源风险)'

    def test_cli_missing_npy_graceful(self, tmp_path, monkeypatch):
        calls = []
        _patch_directions(monkeypatch, calls)
        df = _df_exploded()
        dfp = tmp_path / 'exploded.parquet'
        df.to_parquet(dfp)
        rc = da.main([
            '--track', 'ss',
            '--df-exploded', str(dfp),
            '--text-embeddings-ss', str(tmp_path / 'nonexistent.npy'),
            '--output', str(tmp_path / 'dims.parquet'),
        ])
        assert rc == 0  # 优雅 skip, 不炸

    def test_merge_bridge_end_to_end(self, tmp_path, monkeypatch):
        # --merge-panel-output 走通 (含 _lg 桥接 + 剪枝 tracks 透传, 锁旧 'both' 启发式回归)
        calls = []
        _patch_directions(monkeypatch, calls)
        monkeypatch.setattr(da, '_resolve_large_spec', lambda: {
            'model': 'text-embedding-3-large',
            'text_pipeline_version': 'v1-2026-06-27-emb3large'})
        df = _df_exploded()
        dfp = tmp_path / 'exploded.parquet'
        df.to_parquet(dfp)
        # 只落 full+ss (ctx 缺 .npy → 剪枝后 {full, ss}, 旧启发式会误判 'both' 而崩)
        self._write_npy(tmp_path, len(df), {('', 'full'): _MAIN_DIM, ('', 'ss'): _MAIN_DIM,
                                            ('_lg', 'full'): _LG_DIM, ('_lg', 'ss'): _LG_DIM})
        panel_p = tmp_path / '40_panel_yearly.parquet'
        pd.DataFrame({'target_bank': ['工商银行'], 'year': [2017], 'roa': [1.0]}).to_parquet(panel_p)
        rc = da.main([
            '--track', 'all', '--include-lg',
            '--df-exploded', str(dfp),
            '--embeddings-dir', str(tmp_path),
            '--text-embeddings-full', str(tmp_path / '27_benefit_embeddings_full.npy'),
            '--text-embeddings-ctx', str(tmp_path / '27_benefit_embeddings_ctx.npy'),
            '--text-embeddings-ss', str(tmp_path / '27_benefit_embeddings_ss.npy'),
            '--output', str(tmp_path / 'dims.parquet'),
            '--panel', str(panel_p),
            '--merge-panel-output', str(tmp_path / 'panel_with_dims.parquet'),
        ])
        assert rc == 0
        merged = pd.read_parquet(tmp_path / 'panel_with_dims.parquet')
        for t in ('full', 'ss'):
            assert da._dim_col('compliance', '', t) in merged.columns
            assert da._dim_col('compliance', '_lg', t) in merged.columns
        assert da._dim_col('compliance', '', 'ctx') not in merged.columns  # 剪枝轨不并入
