"""一次性外科注入: boilerplate_phrase_ratio_full (WS-B2) 注入 6 个 golden record.

单轨 (full only); 非破坏 (只 ADD 列)。忠实性保证:
- 构造同一性: 注入用 compute_boilerplate_ratios == 生产 enrich_with_boilerplate 同一函数。
- 确定性 gate: 同一语料重算两次逐值相等 (sorted vocab + 固定参数, 无 HASHSEED 依赖)。
- 覆盖 gate: 面板 avg_boilerplate_full 的 NaN-mask == avg_specificity (同 bank-year 聚合域)。
任一 gate 失败 → SystemExit(1)。
"""
from __future__ import annotations

import math
import sys

import pandas as pd

from news_process.pipeline.sentiment.boilerplate import compute_boilerplate_ratios

DD = 'data/processed'
ART_FILES = ['22_words_tone.parquet', '23_bert_tone.parquet',
             '24_herd_decay.parquet', '40_article_bank_level.parquet']
PANEL_FILES = ['40_panel_yearly.parquet', '51_panel_with_controls.parquet']
KEY = ['docid', 'target_bank']
ART_COL = 'boilerplate_phrase_ratio_full'
AVG_COL = 'avg_boilerplate_full'


def _isnan(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


# ── 1. 文章级: 从 22 content_full 算 boilerplate (+ 确定性 gate) ──
df22 = pd.read_parquet(f'{DD}/22_words_tone.parquet')
texts = df22['content_full'].tolist()
r1 = compute_boilerplate_ratios(texts)
r2 = compute_boilerplate_ratios(texts)
det = all((_isnan(a) and _isnan(b)) or a == b for a, b in zip(r1, r2))
print(f'[GATE 确定性] boilerplate 两次重算逐值相等: {det}')
if not det:
    sys.exit(1)
nv = sum(1 for v in r1 if not _isnan(v))
rng = [v for v in r1 if not _isnan(v)]
print(f'[INFO] boilerplate: {nv}/{len(r1)} 非空, range [{min(rng):.4f}, {max(rng):.4f}]')
keyed = df22[KEY].copy()
keyed[ART_COL] = r1

# ── 2. 注入 4 个文章级 record (append; 列序不影响 golden 哈希/repro set 断言) ──
for f in ART_FILES:
    df = pd.read_parquet(f'{DD}/{f}')
    merged = df.merge(keyed, on=KEY, how='left', validate='one_to_one')
    assert len(merged) == len(df), f'{f} merge changed rows'
    df[ART_COL] = merged[ART_COL].values
    assert df[ART_COL].isna().sum() == merged[ART_COL].isna().sum()
    df.to_parquet(f'{DD}/{f}', index=False)
    print(f'[ART] {f}: +1 col -> {df.shape[1]} ({ART_COL})')

# ── 3. 面板级: bank-year mean (== encode groupby) + 覆盖 gate + 注入 ──
art = pd.read_parquet(f'{DD}/40_article_bank_level.parquet')  # 含 year + 新 boilerplate
g_bp = art.groupby(['target_bank', 'year'])[ART_COL].mean()
for f in PANEL_FILES:
    df = pd.read_parquet(f'{DD}/{f}')
    mp = df[['target_bank', 'year']].merge(
        g_bp.rename(AVG_COL), on=['target_bank', 'year'], how='left')
    # 覆盖 gate: avg_boilerplate NaN-mask == avg_specificity (同 bank-year 聚合域)
    nm_bp = mp[AVG_COL].isna().values
    nm_sp = df['avg_specificity_full'].isna().values
    if (nm_bp != nm_sp).any():
        print(f'[FAIL] {f} {AVG_COL} NaN-mask != avg_specificity_full '
              f'(差 {int((nm_bp != nm_sp).sum())} 行)')
        sys.exit(1)
    df[AVG_COL] = mp[AVG_COL].values
    df.to_parquet(f'{DD}/{f}', index=False)
    print(f'[PANEL] {f}: +1 col -> {df.shape[1]} ({AVG_COL}); 覆盖==avg_specificity OK')

print('\nINJECTION COMPLETE — 6 records, boilerplate raw(4) + avg(2), 确定性+覆盖 gate 全过')
