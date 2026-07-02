"""compute_cross_model_kappa (Phase 3 跨模型 κ, 互为稳健性) gate 测试 (2026-07-02)。

守护活跃生产路径 (_run_validation_for_track 每轨调用)。验证:
  · 非负重映射 _KAPPA_LABEL_CODE (负面≥0, 非 -1) — 避 compute_krippendorffs_alpha 的 -1 缺标哨兵
    把负面标签静默丢弃致 α 虚高 (关键回归)。
  · 矩阵形状 (n_coders×n_items) 正确 → 产 LLM/BERT 两组 Krippendorff α + pairwise Cohen κ。
  · finbert2 (2 分类) 参与 BERT 组 (名义 κ 原生容类别子集, 不崩)。
  · 'llm' 投票聚合被剔除 (仅 3 独立 LLM 入组)。
  · 产物 sentiment_model_kappa{track}.csv 落盘。
"""
import logging

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
