"""去重阈值敏感性 (panel/dedup_sensitivity.py + preprocess/dedup.py 参数化重构) 守护测试。

覆盖:
  A. dedup.py 重构默认参数锚点 (诚实表述, fix test-2 2026-06-13):
     _perform_near_deduplication 薄包装 == compute_minhashes + find(默认参数) 串联,
     并把默认参数 (W=5, self.threshold) 的剔除结果**钉为行为锚点** (synthetic fixture
     上 drop=={d2})。注: 拆分前后等价由"纯方法抽取"(git diff 仅参数化两处) 在构造层
     保证, 本测试不持有拆分前旧代码副本, 故名为"默认参数锚点 + 自洽"而非"逐位金值对比";
     window_busdays/threshold 参数化方向 (更长窗口/更低阈值 ⇒ 剔除集为超集) 由子集关系断言。
  B. compute_dedup_sensitivity_treatments 契约:
     - B1 合成 12_full+14 fixture (不依赖盘上试跑产物, fix test-3/4/5):
       列齐全 / pct∈[0,1] / index≥0 / 零-fintech→0 (显式) / 全集外→NaN / 更严窗口单调;
     - B2 真实试跑产物 (盘上有则跑, 否则 skip): 同契约在真实分布上复核。
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

    def test_lower_threshold_drops_superset(self, tmp_path, near_dup_df):
        # fix(test-1 2026-06-13): 原 `len(drop_lo) >= len(drop_hi)` 在 drop_hi 恒空时
        # 退化为 len>=0 近乎恒真, 无法捕捉方向反转。改为子集关系 + 非平凡性钉桩:
        # 低阈值的 LSH 簇是高阈值簇的超集 → 剔除索引集为超集 (drop_hi ⊆ drop_lo),
        # 且低阈值在该高相似 fixture 上至少删 1 篇 (否则断言空过)。
        dd = _make_dedup(tmp_path)
        prep = dd._prepare_dataframe(near_dup_df.copy())
        mh = dd.compute_minhashes(prep)
        drop_hi = dd.find_near_duplicate_indices(prep, mh, threshold=0.9)
        drop_lo = dd.find_near_duplicate_indices(prep, mh, threshold=0.5)
        assert drop_hi.issubset(drop_lo), f'方向反转: drop_hi={drop_hi} ⊄ drop_lo={drop_lo}'
        assert len(drop_lo) >= 1, '低阈值在高相似 fixture 上应至少删 1 篇 (防恒真空过)'

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
# B1. 合成 12_full + 14 fixture 上的面板契约 (不依赖盘上试跑产物)
#     fix(test-3/4/5 2026-06-13): 闭合 "@_disk skip-if-missing → 干净 checkout/CI
#     上契约零覆盖" 盲区; 并显式覆盖 docstring 承诺的 NaN 契约 (全集外→NaN) 与
#     零契约 (零-fintech→0), 不再靠 if z.any() 守卫可能静默空过。
# ============================================================================

# 长文本 (确保 a1/a2 的 3-gram Jaccard 远高于 0.70, LSH 必聚簇)
_SYN_BODY = (
    '中国人民银行宣布下调金融机构存款准备金率以支持实体经济发展并保持流动性合理充裕，'
    '同时引导金融机构加大对小微企业和民营企业的信贷投放力度优化金融资源配置结构。'
)


@pytest.fixture()
def synthetic_corpus(tmp_path, monkeypatch):
    """写合成 12_full + 14_intensity 到 tmp, 并重定向 dedup_sensitivity 的读盘路径。

    构造覆盖三类 bank-year:
      BankA/2017 — a1(ft)+a2(ft, a1 的 7 工作日后近似转载)+a3(非ft) → 窗口敏感
      BankB/2017 — b1(非ft 银行新闻) → 零-fintech (有新闻无 fintech) → 零契约
      BankA/2018 — a4(ft) → 正常有曝光
    变体网格 [(0.70,5),(0.70,10)]: w5 不删 (a1-a2 隔 7 工作日>5), w10 删 a2。
    """
    import news_process.pipeline.panel.dedup_sensitivity as ds
    f12 = pd.DataFrame({
        'docid': ['a1', 'a2', 'a3', 'b1', 'a4'],
        'target_bank': ['BankA', 'BankA', 'BankA', 'BankB', 'BankA'],
        '日期': ['2017-03-01', '2017-03-10', '2017-05-01', '2017-04-01', '2018-03-01'],
        '媒体(中文)': ['新华社', '地方小报', '某晚报', '某报', '某网'],
        '标题': ['降准公告', '降准公告', '理财产品', '新设网点', '降准回顾'],
        '内容': [_SYN_BODY, _SYN_BODY + '(本报记者报道)', '某行理财产品年化收益走高',
                 '某行在县域新设两家网点', _SYN_BODY + '年度综述'],
        'is_fintech_news': [True, True, False, False, True],
    })
    s14 = pd.DataFrame({  # 14_intensity 仅 fintech 文章带强度分
        'docid': ['a1', 'a2', 'a4'],
        'target_bank': ['BankA', 'BankA', 'BankA'],
        '日期': ['2017-03-01', '2017-03-10', '2018-03-01'],
        'fintech_intensity_score_full': [1.0, 1.0, 2.0],
        'fintech_intensity_score_ctx': [0.8, 0.8, 1.5],
    })
    f12.to_parquet(tmp_path / '12_fintech_news_full.parquet')
    s14.to_parquet(tmp_path / '14_fintech_intensity.parquet')
    monkeypatch.setattr(ds, 'OUTPUT_DIR', str(tmp_path))
    monkeypatch.setattr(ds, 'FILENAMES', {})
    monkeypatch.setitem(ds.CONFIG.setdefault('panel_building', {}),
                        'dedup_sensitivity', {'variants': [[0.70, 5], [0.70, 10]]})
    return tmp_path


def _syn_panel() -> pd.DataFrame:
    # 末行 GHOST/2099 = 12_full 全集外 bank-year → 触发 NaN 契约
    return pd.DataFrame({
        'target_bank': ['BankA', 'BankA', 'BankB', 'GHOST'],
        'year': [2017, 2018, 2017, 2099],
    })


class TestSyntheticPanelContract:

    def test_columns_present_and_bounds(self, synthetic_corpus):
        out = compute_dedup_sensitivity_treatments(_syn_panel())
        for sfx in ('j70w5', 'j70w10'):
            for m in ('attention_index_full', 'attention_index_ctx',
                      'attention_pct_full', 'n_ft_articles', 'n_all_articles'):
                assert f'{m}_{sfx}' in out.columns, f'缺列 {m}_{sfx}'
            p = out[f'attention_pct_full_{sfx}'].dropna()
            assert p.between(0, 1).all(), f'pct_{sfx} 越界 [{p.min()},{p.max()}]'
            idx = out[f'attention_index_full_{sfx}'].dropna()
            assert (idx >= 0).all() and np.isfinite(idx).all()

    def test_zero_fintech_contract_explicit(self, synthetic_corpus):
        # BankB/2017: 有银行新闻(b1)但零 fintech → index/pct == 0 (真零曝光, 非 NaN)。
        # 显式定位该行断言, 不靠 if z.any() (fix test-5: 防数据变化致守卫静默空过)。
        out = compute_dedup_sensitivity_treatments(_syn_panel())
        row = out[(out['target_bank'] == 'BankB') & (out['year'] == 2017)]
        assert len(row) == 1
        for sfx in ('j70w5', 'j70w10'):
            assert row[f'n_ft_articles_{sfx}'].iloc[0] == 0
            assert row[f'attention_index_full_{sfx}'].iloc[0] == 0
            assert row[f'attention_pct_full_{sfx}'].iloc[0] == 0

    def test_out_of_universe_nan_contract(self, synthetic_corpus):
        # fix(test-4): GHOST/2099 不在 12_full 全集 → LEFT-merge 后全部变体列 NaN。
        out = compute_dedup_sensitivity_treatments(_syn_panel())
        row = out[(out['target_bank'] == 'GHOST') & (out['year'] == 2099)]
        assert len(row) == 1
        for sfx in ('j70w5', 'j70w10'):
            for m in ('attention_index_full', 'attention_index_ctx',
                      'attention_pct_full', 'n_ft_articles', 'n_all_articles'):
                assert pd.isna(row[f'{m}_{sfx}'].iloc[0]), f'{m}_{sfx} 应为 NaN'

    def test_stricter_window_drops_more_monotone(self, synthetic_corpus):
        # j70w10 (W=10 捕获 a1-a2 的 7 工作日窗口) 比 j70w5 (W=5 不删) 在 BankA/2017
        # 少 1 篇 fintech — 单调性非平凡 (真发生删除, 非两侧恒等空过)。
        out = compute_dedup_sensitivity_treatments(_syn_panel())
        row = out[(out['target_bank'] == 'BankA') & (out['year'] == 2017)]
        w5 = row['n_ft_articles_j70w5'].iloc[0]
        w10 = row['n_ft_articles_j70w10'].iloc[0]
        assert w10 <= w5
        assert w10 == w5 - 1, f'期望 w10 比 w5 少 1 篇 (a2 被删), 实得 w5={w5}, w10={w10}'


# ============================================================================
# B2. 真实试跑产物上的面板契约 (缺产物则 skip, 同 test_attention_treatments)
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
