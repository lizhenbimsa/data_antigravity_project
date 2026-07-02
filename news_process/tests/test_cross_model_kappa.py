"""compute_cross_model_kappa (Phase 3 跨模型 κ, 互为稳健性) gate 测试 (2026-07-02)。

守护活跃生产路径 (_run_validation_for_track 每轨调用)。验证:
  · 非负重映射 _KAPPA_LABEL_CODE (负面≥0, 非 -1) — 避 compute_krippendorffs_alpha 的 -1 缺标哨兵
    把负面标签静默丢弃致 α 虚高 (关键回归)。
  · 矩阵形状 (n_coders×n_items) 正确 → 产 LLM/BERT 两组 Krippendorff α + pairwise Cohen κ。
  · finbert2 (2 分类) 参与 BERT 组 (名义 κ 原生容类别子集, 不崩)。
  · 'llm' 投票聚合被剔除 (仅 3 独立 LLM 入组)。
  · 产物 sentiment_model_kappa{track}.csv 落盘。

扩展 (2026-07-03, ROBUSTNESS_GAP_BACKFILL §2 A3): compute_cross_model_classification_kappa
(三 LLM 分类维度 subst/locus/collab 的 per-model 跨模型一致性) gate:
  ① 中文分类标签因子化后码值全非负 (Krippendorff -1 缺标哨兵铁律, 含缺标 mock);
  ② 三维 × 三轨 α/κ 产出存在 (合成 per-model 分类列 DataFrame);
  ③ 缺标 (None) 容错 + 2-vs-3 类容错 (一列全缺 → 优雅 NaN/跳过不炸);
  ④ eval_report 输出键结构锁契约 (cross_model_classification.{dim}.{track}.{alpha|kappa_a_vs_b});
  ⑤ 既有 tone 版跨模型统计零扰动 (原有 CSV schema/键仍在, 无新列泄漏)。
全 mock/合成数据, 不依赖盘上 parquet (本机 21_tone_llms.parquet 无 per-model 分类列)。
"""
import logging
import math

import numpy as np
import pandas as pd

from news_process.validation import tone_validation as tv


def _synth_cols():
    return {
        'words': {},
        'llm': {
            'gpt54nano': {'sentiment': 'gpt54nano_sentiment_full', 'confidence': None},
            'gemini31': {'sentiment': 'gemini31_sentiment_full', 'confidence': None},
            'deepseekv4': {'sentiment': 'deepseekv4_sentiment_full', 'confidence': None},
            'llm': {'sentiment': 'llm_sentiment_full', 'confidence': None},  # 聚合, 应剔除
        },
        'bert': {
            'finbert_cn': {'label': 'finbert_cn_label_full', 'probs': {}},
            'fin_sent_zh': {'label': 'fin_sent_zh_label_full', 'probs': {}},
            'finbert2': {'label': 'finbert2_label_full', 'probs': {}},  # 2 分类, 无中性
        },
    }


def _mk_df(n=60, seed=0):
    rng = np.random.RandomState(seed)
    labs = ['正面', '中性', '负面']
    d = {c: rng.choice(labs, size=n) for c in [
        'gpt54nano_sentiment_full', 'gemini31_sentiment_full', 'deepseekv4_sentiment_full',
        'llm_sentiment_full', 'finbert_cn_label_full', 'fin_sent_zh_label_full']}
    d['finbert2_label_full'] = rng.choice(['正面', '负面'], size=n)  # 2 分类无中性
    return pd.DataFrame(d)


def test_label_code_is_nonnegative():
    # ⚠ 负面必须编 0 (非 -1): compute_krippendorffs_alpha 以 -1 为缺标哨兵, 负面=-1 会被静默丢弃。
    assert tv._KAPPA_LABEL_CODE == {'负面': 0, '中性': 1, '正面': 2}
    assert min(tv._KAPPA_LABEL_CODE.values()) == 0


def test_output_groups_and_metrics(tmp_path):
    df = _mk_df()
    tv.compute_cross_model_kappa(df, _synth_cols(), '_full', str(tmp_path), logging.getLogger('t'))
    out = tmp_path / 'sentiment_model_kappa_full.csv'
    assert out.exists(), '产物 sentiment_model_kappa_full.csv 未落盘'
    res = pd.read_csv(out)
    assert set(res['group'].unique()) == {'LLM', 'BERT'}
    assert set(res['metric'].unique()) == {'krippendorff_alpha', 'cohen_kappa'}
    # 每组 1 Krippendorff + 3 pairwise Cohen = 8 行
    assert len(res) == 8, f'期望 8 行 (2组×(1α+3κ)), 实得 {len(res)}'


def test_llm_aggregate_excluded(tmp_path):
    df = _mk_df()
    tv.compute_cross_model_kappa(df, _synth_cols(), '_full', str(tmp_path), logging.getLogger('t'))
    res = pd.read_csv(tmp_path / 'sentiment_model_kappa_full.csv')
    # 'llm' 聚合不得作为独立评分员出现在任何配对里
    for pair in res['pair']:
        assert not any(tok.strip() == 'llm' for tok in str(pair).replace('vs', ' ').split()), \
            f"'llm' 聚合未被剔除: {pair}"


def test_finbert2_participates(tmp_path):
    df = _mk_df()
    tv.compute_cross_model_kappa(df, _synth_cols(), '_full', str(tmp_path), logging.getLogger('t'))
    res = pd.read_csv(tmp_path / 'sentiment_model_kappa_full.csv')
    bert_pairs = res[res.group == 'BERT']['pair'].tolist()
    assert any('finbert2' in p for p in bert_pairs), 'finbert2 (2 分类) 未参与 BERT 组 κ'


def test_negative_labels_counted_not_dropped(tmp_path):
    # 关键回归: 若误用 {正:1,中:0,负:-1} 原码, Krippendorff -1 哨兵把负面全丢 → 随机数据 α 虚高≈1.0。
    # 正确非负码下随机三家标签 α 应接近 0 (远 < 0.9)。
    df = _mk_df(seed=7)
    tv.compute_cross_model_kappa(df, _synth_cols(), '_full', str(tmp_path), logging.getLogger('t'))
    res = pd.read_csv(tmp_path / 'sentiment_model_kappa_full.csv')
    llm_row = res[(res.group == 'LLM') & (res.metric == 'krippendorff_alpha')].iloc[0]
    # 有效判别量 = n_units (非 α): 非负码下全部标签有效 → n_units == 全部行; 若误用 {负面:-1}
    # 原码, 负面被 Krippendorff -1 缺标哨兵当缺失丢弃 → n_units < len(df) (buggy 实测 ~47 vs 正确 60)。
    # (α<0.9 无判别力: buggy/correct 随机数据皆 <0.9; revert 另由 test_label_code_is_nonnegative 拦。)
    assert int(llm_row['n_units']) == len(df), \
        f"n_units={llm_row['n_units']} != {len(df)} → 疑似 -1 哨兵 bug 把负面标签当缺失丢弃"


# ============================================================================
# §2 A3 扩展: 跨模型分类维度一致性 (2026-07-03)
# ============================================================================

DIMS = ('subst', 'locus', 'collab')
SHORTS = ('gpt54nano', 'gemini31', 'deepseekv4')
TRACKS = ('_full', '_ctx', '_ss')

#: 各维度中文标签词表 (mock; 与 encode.LLM_CLASS_SPEC 值[1] 目标类同族)
_DIM_LABELS = {
    'subst': ['实质性', '象征性'],
    'locus': ['底层技术', '应用场景'],
    'collab': ['外部协同', '自主研发'],
}


def _mk_class_df(track='_full', n=60, seed=0, none_frac=0.1, all_none_model=None):
    """合成 per-model 分类列 DataFrame (含随机缺标; all_none_model 指定整列全缺)。"""
    rng = np.random.RandomState(seed)
    d = {}
    for dim, labs in _DIM_LABELS.items():
        for s in SHORTS:
            col = f'{s}_{dim}{track}'
            if s == all_none_model:
                d[col] = [None] * n
            else:
                vals = rng.choice(labs, size=n).astype(object)
                miss = rng.rand(n) < none_frac
                vals[miss] = None
                d[col] = vals
    return pd.DataFrame(d)


def _pair_keys(shorts):
    return [f'kappa_{shorts[a]}_vs_{shorts[b]}'
            for a in range(len(shorts)) for b in range(a + 1, len(shorts))]


class TestClassificationCodeMap:
    """① 中文分类标签因子化后码值全非负 (Krippendorff -1 缺标哨兵铁律)。"""

    def test_codes_nonnegative_and_dense(self):
        for labs in _DIM_LABELS.values():
            cm = tv._classification_code_map(labs)
            assert min(cm.values()) == 0, f'{labs}: 因子化码含负值/非零起始 → -1 哨兵冲突风险'
            assert sorted(cm.values()) == list(range(len(labs))), f'{labs}: 码值非稠密 0..k-1'

    def test_deterministic_and_dedup(self):
        # 排序去重 → 与输入顺序/重复无关 (确定性因子化)
        a = tv._classification_code_map(['象征性', '实质性', '实质性'])
        b = tv._classification_code_map(['实质性', '象征性'])
        assert a == b and set(a.values()) == {0, 1}

    def test_spec_resolves_three_dims_three_shorts(self):
        # try-import encode SSOT / fallback 两侧都容忍 — 结构契约恒定
        spec, shorts = tv._resolve_llm_class_spec()
        assert set(spec) == set(DIMS)
        assert set(shorts) == set(SHORTS) and len(shorts) == 3
        # fallback 副本与 SSOT 结构同步 (三元组: metric/目标类/解析键)
        assert set(tv._LLM_CLASS_SPEC_FALLBACK) == set(DIMS)
        for v in tv._LLM_CLASS_SPEC_FALLBACK.values():
            assert len(v) == 3
        # 终审 #8: fallback 字面副本逐字节锁 (仅结构断言是恒真盲区, 内容漂移不可测)
        from news_process.pipeline.panel import encode as enc
        assert dict(enc.LLM_CLASS_SPEC) == tv._LLM_CLASS_SPEC_FALLBACK
        assert tuple(tv._LLM_SHORTS_FALLBACK) == tuple(enc.LLM_MODELS)

    def test_end_to_end_codes_nonnegative_with_missing(self, tmp_path):
        # 含缺标 mock 走完整路径: n_units 计满非缺行 → 证明缺标走 -1 哨兵而真标签全非负
        df = _mk_class_df(none_frac=0.0)
        df.loc[0, 'gpt54nano_subst_full'] = None  # 单点缺标
        res = tv.compute_cross_model_classification_kappa(
            df, '_full', str(tmp_path), logging.getLogger('t'))
        # 其余两家该行仍有标 → 可配对单元 = 全部行 (若真标签被误编 -1 会 < len(df))
        assert res['subst']['full']['n_units_alpha'] == len(df)
        assert res['locus']['full']['n_units_alpha'] == len(df)


class TestClassificationOutput:
    """② 三维 × 三轨 α/κ 产出存在 + ④ eval_report 键结构锁契约。"""

    def test_three_dims_all_tracks(self, tmp_path):
        _, shorts = tv._resolve_llm_class_spec()
        for track in TRACKS:
            df = _mk_class_df(track=track, seed=3)
            res = tv.compute_cross_model_classification_kappa(
                df, track, str(tmp_path), logging.getLogger('t'))
            trk = track.lstrip('_')
            assert set(res) == set(DIMS), f'{track}: 维度覆盖不齐 {set(res)}'
            for dim in DIMS:
                node = res[dim][trk]
                assert isinstance(node['alpha'], float)
                assert node['n_units_alpha'] > 0
                for pk in _pair_keys(shorts):
                    assert pk in node, f'{track}/{dim}: 缺 pairwise 键 {pk}'
                    assert isinstance(node[pk], float)
            out = tmp_path / f'classification_model_kappa{track}.csv'
            assert out.exists(), f'产物 classification_model_kappa{track}.csv 未落盘'
            csv = pd.read_csv(out)
            # 每维 1 Krippendorff + 3 pairwise Cohen = 3 维 × 4 = 12 行
            assert len(csv) == 12, f'{track}: 期望 12 行, 实得 {len(csv)}'
            assert set(csv['dim'].unique()) == set(DIMS)
            assert set(csv['metric'].unique()) == {'krippendorff_alpha', 'cohen_kappa'}

    def test_report_key_structure(self, tmp_path):
        # ④ 锁契约: 完整键路径 cross_model_classification.{dim}.{track}.{alpha|kappa_a_vs_b}
        _, shorts = tv._resolve_llm_class_spec()
        df = _mk_class_df(seed=5)
        res = tv.compute_cross_model_classification_kappa(
            df, '_full', str(tmp_path), logging.getLogger('t'))
        for dim in DIMS:
            node = res[dim]['full']
            expected = ({'alpha', 'n_units_alpha', 'labels', 'members'}
                        | set(_pair_keys(shorts))
                        | {f'n_units_{pk}' for pk in _pair_keys(shorts)})
            assert set(node) == expected, f'{dim}: 键集漂移 {set(node) ^ expected}'
            assert node['labels'] == sorted(_DIM_LABELS[dim])
            assert set(node['members']) == set(shorts)
        # CSV 侧 'key' 列 = 同一键路径的点分平铺 (供跨产物对账)
        csv = pd.read_csv(tmp_path / 'classification_model_kappa_full.csv')
        keys = set(csv['key'])
        for dim in DIMS:
            assert f'cross_model_classification.{dim}.full.alpha' in keys
            for pk in _pair_keys(shorts):
                assert f'cross_model_classification.{dim}.full.{pk}' in keys

    def test_kappa_perfect_agreement(self, tmp_path):
        # 数值 sanity: 三家完全一致 → 全部 κ = 1, α = 1
        n = 40
        d = {}
        for dim, labs in _DIM_LABELS.items():
            same = np.resize(labs, n)
            for s in SHORTS:
                d[f'{s}_{dim}_full'] = same.copy()
        res = tv.compute_cross_model_classification_kappa(
            pd.DataFrame(d), '_full', str(tmp_path), logging.getLogger('t'))
        _, shorts = tv._resolve_llm_class_spec()
        for dim in DIMS:
            node = res[dim]['full']
            assert node['alpha'] > 0.999
            for pk in _pair_keys(shorts):
                assert node[pk] > 0.999


class TestClassificationGracefulDegradation:
    """③ 缺标/缺列容错: 一列全缺 → 优雅 NaN/跳过不炸; 2-vs-3 类容错。"""

    def test_missing_columns_skip_no_crash(self, tmp_path):
        # 本机现状镜像: parquet 无任何 per-model 分类列 → 全维跳过, 返回 {}, 不落盘不崩
        df = pd.DataFrame({'其它列': ['x', 'y']})
        res = tv.compute_cross_model_classification_kappa(
            df, '_full', str(tmp_path), logging.getLogger('t'))
        assert res == {}
        assert not (tmp_path / 'classification_model_kappa_full.csv').exists()

    def test_one_model_all_none_yields_nan_pairs(self, tmp_path):
        # ③ 一列全缺 (None): 与之配对的 κ = 优雅 NaN (键仍在), α 由其余两家照算不炸
        df = _mk_class_df(seed=11, none_frac=0.0, all_none_model='deepseekv4')
        res = tv.compute_cross_model_classification_kappa(
            df, '_full', str(tmp_path), logging.getLogger('t'))
        for dim in DIMS:
            node = res[dim]['full']
            assert math.isnan(node['kappa_gpt54nano_vs_deepseekv4'])
            assert node['n_units_kappa_gpt54nano_vs_deepseekv4'] == 0
            assert math.isnan(node['kappa_gemini31_vs_deepseekv4'])
            # 其余两家交集完整 → α/κ 正常有限值
            assert not math.isnan(node['kappa_gpt54nano_vs_gemini31'])
            assert not math.isnan(node['alpha'])
        # CSV 侧镜像 tone 版惯例: 无效配对不落行 (每维 1α + 1 有效 κ = 6 行)
        csv = pd.read_csv(tmp_path / 'classification_model_kappa_full.csv')
        assert len(csv) == 6

    def test_single_available_column_skips_dim(self, tmp_path):
        # 仅 1 家有列 (<2) → 该维 INFO 跳过; 其余维不受影响
        df = _mk_class_df(seed=13)
        drop = [c for c in df.columns
                if c.endswith('_subst_full') and not c.startswith('gpt54nano')]
        res = tv.compute_cross_model_classification_kappa(
            df.drop(columns=drop), '_full', str(tmp_path), logging.getLogger('t'))
        assert 'subst' not in res
        assert set(res) == {'locus', 'collab'}

    def test_all_labels_missing_skips_dim(self, tmp_path):
        # 三家该维全缺标 (列在标全 None) → 无有效标签, 优雅跳过不炸
        df = _mk_class_df(seed=17)
        for s in SHORTS:
            df[f'{s}_locus_full'] = None
        res = tv.compute_cross_model_classification_kappa(
            df, '_full', str(tmp_path), logging.getLogger('t'))
        assert 'locus' not in res
        assert set(res) == {'subst', 'collab'}

    def test_two_vs_three_class_tolerance(self, tmp_path):
        # 2-vs-3 类词表失配: gpt54nano 额外发第三类标签 (类比 finbert2 先例的类别子集),
        # 名义尺度 Krippendorff/Cohen 原生容忍, 不需要二值化, 不炸
        rng = np.random.RandomState(19)
        n = 60
        d = {
            'gpt54nano_subst_full': rng.choice(['实质性', '象征性', '中间态'], size=n),
            'gemini31_subst_full': rng.choice(['实质性', '象征性'], size=n),
            'deepseekv4_subst_full': rng.choice(['实质性', '象征性'], size=n),
        }
        res = tv.compute_cross_model_classification_kappa(
            pd.DataFrame(d), '_full', str(tmp_path), logging.getLogger('t'))
        node = res['subst']['full']
        assert node['labels'] == ['中间态', '实质性', '象征性']  # 三类并集入因子化
        assert not math.isnan(node['alpha'])
        assert node['n_units_alpha'] == n


class TestToneZeroPerturbation:
    """⑤ 既有 tone 版跨模型统计零扰动 (扩展后原路径原键仍在)。"""

    def test_tone_csv_schema_unchanged(self, tmp_path):
        # tone 版 CSV schema 不因 §2 A3 扩展漂移 (无 'dim'/'key' 列泄漏)
        df = _mk_df()
        tv.compute_cross_model_kappa(df, _synth_cols(), '_full', str(tmp_path),
                                     logging.getLogger('t'))
        res = pd.read_csv(tmp_path / 'sentiment_model_kappa_full.csv')
        assert list(res.columns) == ['track', 'group', 'metric', 'pair', 'value', 'n_units']
        assert set(res['group'].unique()) == {'LLM', 'BERT'}
        assert len(res) == 8

    def test_tone_and_classification_coexist(self, tmp_path):
        # 同一 output_dir 下两统计并存: 各写各的 CSV, 互不覆盖/污染
        tone_df = _mk_df(seed=23)
        cls_df = _mk_class_df(seed=23)
        tv.compute_cross_model_kappa(tone_df, _synth_cols(), '_full', str(tmp_path),
                                     logging.getLogger('t'))
        tv.compute_cross_model_classification_kappa(cls_df, '_full', str(tmp_path),
                                                    logging.getLogger('t'))
        tone_csv = pd.read_csv(tmp_path / 'sentiment_model_kappa_full.csv')
        cls_csv = pd.read_csv(tmp_path / 'classification_model_kappa_full.csv')
        assert len(tone_csv) == 8 and 'dim' not in tone_csv.columns
        assert len(cls_csv) == 12 and 'group' not in cls_csv.columns
        # 分类维度列名不含 sentiment 后缀 → tone 的 discover 路径不会误吸分类列
        assert not any(c.endswith('_sentiment_full') for c in cls_df.columns)
