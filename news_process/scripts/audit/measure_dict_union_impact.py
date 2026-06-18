"""measure_dict_union_impact — v3.10.0 测度变更影响审计 (Part C Tier-1, R1 披露支撑).

把 L&M 2011 中文主译本 (loughran) 接成第 6 部主情感词典后, 跨词典固定 **union** 词典
从 5 部扩为 6 部 → 驱动 ``pos_ratio / neg_ratio / msent_score`` 的计数基改变 (有意测度变更,
非 bug, 见 plan §R1)。本脚本量化该漂移, 供 manuscript/codebook 如实披露:

  对每篇文章并行用 **union-5** (排除 loughran) 与 **union-6** (含 loughran) 重算 msent_score,
  报告 Pearson r / 均值漂移 / 符号翻转率。**门控**: r < 0.95 或符号翻转 > 5% 文章 →
  强制附录敏感性表 (打印 MANDATORY DISCLOSURE)。

口径与生产严格一致 (复用 tone_words 内部函数):
  - union = ``build_union_dictionary`` (极性多数票消解, 平票剔除);
  - 计数 = ``_compute_sentiment_with_rules(tokens, union)`` 的 matched['base'] 原始极性;
  - msent = (raw_neg − raw_pos) / (raw_pos + raw_neg); n_word_token==0 → NaN。

纯 CPU / 纯读 / $0 (无 LLM/网络)。读 stage 22 输出 ``22_words_tone.parquet`` 的 content_full 列。

用法:
    python -m news_process.scripts.audit.measure_dict_union_impact
    python -m news_process.scripts.audit.measure_dict_union_impact --parquet <path> --sample 5000
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.pipeline.sentiment import tone_words as tw  # noqa: E402

# loughran 列前缀别名 (与生产一致); union-5 = 排除此别名的前 5 部。
_LOUGHRAN_ALIAS = tw.DICT_COLUMN_ALIAS['loughran_mcdonald_zh_2026']

# 门控阈值 (plan §R1)
_R_GATE = 0.95
_SIGN_FLIP_GATE = 0.05


def _msent_for_text(text: str, union: dict[str, float], tokenizer) -> float:
    """复刻 tone_words._analyze_single_article 的 msent_score 计数口径."""
    if not isinstance(text, str) or not text.strip():
        return float('nan')
    tokens = list(tokenizer.cut(text))
    word_tokens = [
        t for t in tokens
        if t.strip() and not tw._LMFLS_NONWORD_RE.fullmatch(t.strip())
    ]
    if not word_tokens:
        return float('nan')
    if not union:
        return float('nan')
    _, _, _, _, matched = tw._compute_sentiment_with_rules(tokens, union)
    raw_pos = sum(1 for m in matched if m['base'] > 0)
    raw_neg = sum(1 for m in matched if m['base'] < 0)
    total = raw_pos + raw_neg
    return (raw_neg - raw_pos) / total if total > 0 else 0.0


def measure(parquet_path: str, sample: int | None = None) -> dict:
    """返回 union-5 vs union-6 的 msent 漂移诊断 dict."""
    if not os.path.exists(parquet_path):
        return {'error': f'parquet 不存在: {parquet_path}', 'gate': 'SKIP'}

    df = pd.read_parquet(parquet_path)
    text_col = 'content_full' if 'content_full' in df.columns else (
        '内容' if '内容' in df.columns else None)
    if text_col is None:
        return {'error': 'parquet 缺 content_full / 内容 列', 'gate': 'SKIP'}

    texts = df[text_col].dropna().astype(str).drop_duplicates().tolist()
    if sample and len(texts) > sample:
        # 确定性截取 (前 N, 不随机) → 可复现
        texts = texts[:sample]
    if not texts:
        return {'error': '语料为空', 'gate': 'SKIP'}

    # 6 部词典 (含 loughran 别名) + 5 部 (排除 loughran)
    all_dicts = tw.load_all_dictionaries()
    dicts_5 = [(n, d) for n, d in all_dicts if n != _LOUGHRAN_ALIAS]
    union_6 = tw.build_union_dictionary(all_dicts)
    union_5 = tw.build_union_dictionary(dicts_5)
    tokenizer = tw._get_tone_tokenizer()

    m5 = np.array([_msent_for_text(t, union_5, tokenizer) for t in texts])
    m6 = np.array([_msent_for_text(t, union_6, tokenizer) for t in texts])

    valid = ~(np.isnan(m5) | np.isnan(m6))
    n_valid = int(valid.sum())
    if n_valid < 2:
        return {'error': f'有效文章 < 2 ({n_valid})', 'gate': 'SKIP'}

    a, b = m5[valid], m6[valid]
    pearson = float(np.corrcoef(a, b)[0, 1]) if np.std(a) > 0 and np.std(b) > 0 else 1.0
    mean_shift = float(np.mean(b - a))
    max_abs_shift = float(np.max(np.abs(b - a)))
    sign_flip = float(np.mean(np.sign(a) != np.sign(b)))

    breach = (pearson < _R_GATE) or (sign_flip > _SIGN_FLIP_GATE)
    return {
        'n_articles': len(texts),
        'n_valid': n_valid,
        'union_5_size': len(union_5),
        'union_6_size': len(union_6),
        'mean_msent_5': float(np.mean(a)),
        'mean_msent_6': float(np.mean(b)),
        'pearson_r': round(pearson, 6),
        'mean_shift': round(mean_shift, 6),
        'max_abs_shift': round(max_abs_shift, 6),
        'sign_flip_rate': round(sign_flip, 6),
        'gate': 'MANDATORY_DISCLOSURE' if breach else 'PASS',
    }


def main() -> int:
    ap = argparse.ArgumentParser(description='v3.10.0 union 5→6 msent 漂移审计')
    ap.add_argument('--parquet', default=None,
                    help='stage 22 输出路径 (默认从 config paths 派生)')
    ap.add_argument('--sample', type=int, default=None,
                    help='只取前 N 篇 (确定性截取, 加速大语料)')
    args = ap.parse_args()

    parquet = args.parquet
    if parquet is None:
        cfg = load_config()
        out_dir = cfg['paths'].get('output_dir', os.path.join('data', 'processed'))
        parquet = os.path.join(out_dir, '22_words_tone.parquet')

    res = measure(parquet, sample=args.sample)
    print('=' * 60)
    print('v3.10.0 测度变更影响审计 (union 5→6, 含 Loughran-McDonald 2026)')
    print('=' * 60)
    for k, v in res.items():
        print(f'  {k:22s} = {v}')
    if res.get('gate') == 'MANDATORY_DISCLOSURE':
        print('\n⚠ 漂移超阈值 (r<0.95 或符号翻转>5%) → manuscript/附录须出 5-dict vs '
              '6-dict 敏感性对照表 (plan §R1 披露包)。')
    elif res.get('gate') == 'PASS':
        print('\n✓ 漂移在容许范围 (r≥0.95 且符号翻转≤5%); 仍须在 codebook 标注 union 5→6 '
              '词表覆盖改善 (非方法误)。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
