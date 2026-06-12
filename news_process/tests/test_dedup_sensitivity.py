"""去重阈值敏感性 (panel/dedup_sensitivity.py + preprocess/dedup.py 参数化重构) 守护测试。

覆盖:
  A. dedup.py 重构等价性: compute_minhashes + find_near_duplicate_indices(默认参数)
     == 旧 _perform_near_deduplication 行为 (窗口 5 工作日, self.threshold);
     window_busdays/threshold 参数化方向正确 (更长窗口/更低阈值 ⇒ 删得更多)。
  B. compute_dedup_sensitivity_treatments 在真实试跑产物上的契约:
     列齐全 / pct∈[0,1] / index≥0 / 计数单调 (变体 ≤ 生产, 更严变体 ≤ 较宽变体)
     / 宽松方向变体被拒绝。
"""

from __future__ import annotations

import json
import logging
import os

import numpy as np
import pandas as pd
import pytest

import news_process.pipeline.preprocess.dedup as dedup_mod
from news_process.pipeline.panel.dedup_sensitivity import (
    DEFAULT_VARIANTS,
    FILENAMES,
    OUTPUT_DIR,
    _load_variants,
    _variant_suffix,
    compute_dedup_sensitivity_treatments,
)

# ============================================================================
# A. dedup.py 参数化重构 (合成数据, 不依赖盘上产物)
# ============================================================================


def _make_dedup(tmp_path, threshold=0.8):
    wfile = tmp_path / 'media_weights.json'
    wfile.write_text(json.dumps({'其他媒体': 10}, ensure_ascii=False),
                     encoding='utf-8')
    config = {
        'deduplication': {
            'jaccard_similarity_threshold': threshold,
            'minhash_permutations': 64,
            'ngram_size': 3,
            'parallel_workers': 1,
        },
        'paths': {
            'media_weights_file': str(wfile),
            'output_dir': str(tmp_path / 'out'),
        },
    }
    return dedup_mod.ArticleDeduplicator(
        config=config, logger_instance=logging.getLogger('test_dedup_sens'))


_BODY = (
    '中国人民银行今日宣布下调金融机构存款准备金率零点五个百分点, '
    '释放长期资金约一万亿元, 旨在支持实体经济发展, 保持流动性合理充裕, '
    '引导金融机构加大对小微企业和民营企业的信贷投放力度。'
)


@pytest.fixture()
def near_dup_df():
    """1 原稿 + 1 高相似转载(3 工作日后) + 1 高相似转载(8 工作日后)。"""
    return pd.DataFrame({
        '标题': ['央行宣布降准', '央行宣布降准', '央行宣布降准'],
        '内容': [_BODY, _BODY + '(记者王某报道)', _BODY + '(转载自新华社)'],
        '媒体(中文)': ['新华社', '地方小报', '另一晚报'],
        '日期': ['2018-03-05', '2018-03-08', '2018-03-15'],
        'docid': ['d1', 'd2', 'd3'],
    })


@pytest.fixture(autouse=True)
def _single_worker(monkeypatch):
    monkeypatch.setattr(dedup_mod, 'nb_workers', 1)


class TestDedupRefactorEquivalence:

    def test_default_params_equal_production_method(self, tmp_path, near_dup_df):
        # 重构后 _perform_near_deduplication == compute_minhashes + find(默认参数)
        dd = _make_dedup(tmp_path)
        prep = dd._prepare_dataframe(near_dup_df.copy())
        out = dd._perform_near_deduplication(prep)
        mh = dd.compute_minhashes(prep)
        drop = dd.find_near_duplicate_indices(prep, mh)
        assert set(prep.index) - drop == set(out.index)
        # 生产口径: 5 工作日窗口 → d2 (3 工作日) 删, d3 (8 工作日) 存活
        assert set(out['docid']) == {'d1', 'd3'}

    def test_longer_window_drops_more(self, tmp_path, near_dup_df):
        dd = _make_dedup(tmp_path)
        prep = dd._prepare_dataframe(near_dup_df.copy())
        mh = dd.compute_minhashes(prep)
        drop5 = dd.find_near_duplicate_indices(prep, mh, window_busdays=5)
        drop10 = dd.find_near_duplicate_indices(prep, mh, window_busdays=10)
        assert drop5 <= drop10
        survivors10 = set(prep.loc[~prep.index.isin(drop10), 'docid'])
        assert survivors10 == {'d1'}  # 10 工作日窗口连 d3 一起删

    def test_lower_threshold_drops_at_least_as_much(self, tmp_path, near_dup_df):
        dd = _make_dedup(tmp_path)
        prep = dd._prepare_dataframe(near_dup_df.copy())
        mh = dd.compute_minhashes(prep)
        drop_hi = dd.find_near_duplicate_indices(prep, mh, threshold=0.9)
        drop_lo = dd.find_near_duplicate_indices(prep, mh, threshold=0.5)
        assert len(drop_lo) >= len(drop_hi)

    def test_empty_minhashes_returns_empty_set(self, tmp_path):
        dd = _make_dedup(tmp_path)
        assert dd.find_near_duplicate_indices(
            pd.DataFrame(), pd.Series(dtype=object)) == set()


class TestVariantConfig:

    def test_suffix_format(self):
        assert _variant_suffix(0.70, 5) == 'j70w5'
        assert _variant_suffix(0.80, 10) == 'j80w10'

    def test_loose_direction_rejected(self, monkeypatch):
        # 宽松方向 (J>0.8 或 J=0.8∧W≤5) 在已去重语料上不可识别 → 必须被拒绝
        import news_process.pipeline.panel.dedup_sensitivity as ds
        monkeypatch.setitem(
            ds.CONFIG.setdefault('panel_building', {}), 'dedup_sensitivity',
            {'variants': [[0.90, 5], [0.80, 5], [0.80, 3], [0.70, 5]]})
        assert _load_variants() == [(0.70, 5)]

    def test_default_grid_all_strict(self):
        for th, w in DEFAULT_VARIANTS:
            assert th < 0.80 or (th == 0.80 and w > 5)


# ============================================================================
# B. 真实试跑产物上的面板契约 (缺产物则 skip, 同 test_attention_treatments)
# ============================================================================

_S14 = os.path.join(OUTPUT_DIR, FILENAMES.get(
    'output_14_fintech_intensity', '14_fintech_intensity.parquet'))
_F12 = os.path.join(OUTPUT_DIR, FILENAMES.get(
    'output_12_fintech_full', '12_fintech_news_full.parquet'))

_disk = pytest.mark.skipif(
    not (os.path.exists(_S14) and os.path.exists(_F12)),
    reason='需 14_fintech_intensity + 12_fintech_news_full 试跑产物',
)

_SUFFIXES = [_variant_suffix(t, w) for t, w in DEFAULT_VARIANTS]
_METRICS = ['attention_index_full', 'attention_index_ctx',
            'attention_pct_full', 'n_ft_articles', 'n_all_articles']


def _universe_panel() -> pd.DataFrame:
    f12 = pd.read_parquet(_F12, columns=['target_bank', '日期'])
    f12['year'] = pd.to_datetime(f12['日期'], errors='coerce').dt.year
    f12 = f12.dropna(subset=['year'])
    f12['year'] = f12['year'].astype(int)
    return (f12.drop_duplicates(['target_bank', 'year'])[['target_bank', 'year']]
            .reset_index(drop=True))


@pytest.fixture(scope='module')
def out():
    if not (os.path.exists(_S14) and os.path.exists(_F12)):
        pytest.skip('需试跑产物')
    return compute_dedup_sensitivity_treatments(_universe_panel())


@_disk
class TestPanelContract:

    def test_all_variant_columns_present(self, out):
        for sfx in _SUFFIXES:
            for m in _METRICS:
                assert f'{m}_{sfx}' in out.columns, f'缺列 {m}_{sfx}'

    def test_pct_bounded_index_nonneg(self, out):
        for sfx in _SUFFIXES:
            p = out[f'attention_pct_full_{sfx}'].dropna()
            assert p.between(0, 1).all(), f'pct_{sfx} 越界'
            for m in ('attention_index_full', 'attention_index_ctx'):
                v = out[f'{m}_{sfx}'].dropna()
                assert np.isfinite(v).all() and (v >= 0).all(), f'{m}_{sfx} 异常'

    def test_counts_monotone_vs_production(self, out):
        # 变体计数 ≤ 生产计数 (12_full 直接聚合), 逐 bank-year
        f12 = pd.read_parquet(_F12, columns=['target_bank', '日期'])
        f12['year'] = pd.to_datetime(f12['日期'], errors='coerce').dt.year
        f12 = f12.dropna(subset=['year'])
        f12['year'] = f12['year'].astype(int)
        prod = (f12.groupby(['target_bank', 'year']).size()
                .rename('n_all_prod').reset_index())
        m = out.merge(prod, on=['target_bank', 'year'], how='left')
        for sfx in _SUFFIXES:
            v = m[f'n_all_articles_{sfx}']
            mask = v.notna() & m['n_all_prod'].notna()
            assert (v[mask] <= m.loc[mask, 'n_all_prod']).all(), \
                f'n_all_{sfx} 超过生产计数 (单调性破坏)'

    def test_stricter_variant_monotone(self, out):
        # j70w10 (双向最严) ≤ j70w5 与 j80w10, 逐 bank-year
        for looser in ('j70w5', 'j80w10'):
            a = out['n_all_articles_j70w10']
            b = out[f'n_all_articles_{looser}']
            mask = a.notna() & b.notna()
            assert (a[mask] <= b[mask]).all(), f'j70w10 > {looser} (单调性破坏)'

    def test_zero_fintech_index_is_zero_not_nan(self, out):
        # 变体全集内零-fintech → index/pct = 0 (真零曝光, 镜像 B1 契约)
        for sfx in _SUFFIXES:
            z = (out[f'n_ft_articles_{sfx}'] == 0)
            if z.any():
                assert (out.loc[z, f'attention_index_full_{sfx}'] == 0).all()
                assert (out.loc[z, f'attention_pct_full_{sfx}'] == 0).all()
