"""一次性外科注入: 把 named_entity_ratio 新列注入 6 个 golden record (WS-B1/WS-G).

非破坏: 只 ADD 列, 不改任何既有列值 (golden column_hash 用 index=False, 仅依赖列值)。
两道忠实性 gate:
  A 文章级: 重算 specificity_index == 盘上 (证 compute 路径 == 生产 stage 22)。
  B 面板级: 重算 avg_specificity (groupby bank-year mean) == 盘上 40_panel (证聚合 == encode)。
两 gate 全过才注入 named_entity (同路径/同聚合)。任一 mismatch → SystemExit(1)。
"""
from __future__ import annotations

import math
import sys

import pandas as pd

from news_process.pipeline.sentiment.lexical_complexity import compute_lexical_complexity

DD = 'data/processed'
TRACKS = ['full', 'ctx', 'ss']
ART_FILES = ['22_words_tone.parquet', '23_bert_tone.parquet',
             '24_herd_decay.parquet', '40_article_bank_level.parquet']
PANEL_FILES = ['40_panel_yearly.parquet', '51_panel_with_controls.parquet']
KEY = ['docid', 'target_bank']


def _ne_spec(text):
    r = compute_lexical_complexity(text if isinstance(text, str) else '')
    return r['named_entity_ratio'], r['specificity_index']


def _mismatch(a, b, tol=1e-9):
    m = 0
    for x, y in zip(a, b):
        xn, yn = (x is None or (isinstance(x, float) and math.isnan(x))), \
                 (y is None or (isinstance(y, float) and math.isnan(y)))
        if xn and yn:
            continue
        if xn != yn or abs(float(x) - float(y)) > tol:
            m += 1
    return m


def _insert_after(df, anchor, newcol, values):
    cols = list(df.columns)
    df[newcol] = values
    pos = cols.index(anchor) + 1
    neworder = cols[:pos] + [newcol] + cols[pos:]
    return df[neworder]


# ── 1. 文章级: 从 22 的 content 重算 named_entity + specificity (gate A) ──
df22 = pd.read_parquet(f'{DD}/22_words_tone.parquet')
ne = {}   # (docid,target_bank) -> {named_entity_ratio_<track>}
keyed = df22[KEY].copy()
for tr in TRACKS:
    ne_vals, spec_rec = [], []
    for t in df22[f'content_{tr}']:
        a, b = _ne_spec(t)
        ne_vals.append(a)
        spec_rec.append(b)
    m = _mismatch(df22[f'specificity_index_{tr}'].tolist(), spec_rec)
    print(f'[GATE A] specificity_index_{tr} recompute vs disk: {m} mismatch')
    if m:
        sys.exit(1)
    keyed[f'named_entity_ratio_{tr}'] = ne_vals
    # 真子集断言
    bad = sum(1 for a, b in zip(ne_vals, df22[f'specificity_index_{tr}'])
              if not (isinstance(a, float) and math.isnan(a))
              and not (isinstance(b, float) and math.isnan(b)) and a > b + 1e-9)
    print(f'[CHECK] named_entity_{tr} <= specificity_{tr}: {bad} violations')
    if bad:
        sys.exit(1)
print('[GATE A] PASS — compute 路径 == 生产 stage 22\n')

# ── 2. 注入 4 个文章级 record (insert after specificity_index_<track>) ──
for f in ART_FILES:
    df = pd.read_parquet(f'{DD}/{f}')
    merged = df.merge(keyed, on=KEY, how='left', validate='one_to_one')
    assert len(merged) == len(df), f'{f} merge changed row count'
    for tr in TRACKS:
        col = f'named_entity_ratio_{tr}'
        vals = merged[col].values
        df = _insert_after(df, f'specificity_index_{tr}', col, vals)
        assert df[col].isna().sum() == merged[col].isna().sum()
    df.to_parquet(f'{DD}/{f}', index=False)
    print(f'[ART] {f}: +{len(TRACKS)} cols -> {df.shape[1]} (named_entity after specificity)')

# ── 3. 面板级: gate B (重算 avg_specificity == 盘) + 注入 avg_named_entity ──
art = pd.read_parquet(f'{DD}/40_article_bank_level.parquet')  # 含 year + 新 named_entity
panel0 = pd.read_parquet(f'{DD}/40_panel_yearly.parquet')[['target_bank', 'year']].copy()
agg = {}
for tr in TRACKS:
    g_spec = art.groupby(['target_bank', 'year'])[f'specificity_index_{tr}'].mean()
    g_ne = art.groupby(['target_bank', 'year'])[f'named_entity_ratio_{tr}'].mean()
    pj = panel0.merge(g_spec.rename('rec_spec'), on=['target_bank', 'year'], how='left')
    on_disk = pd.read_parquet(f'{DD}/40_panel_yearly.parquet')[f'avg_specificity_{tr}'].values
    m = _mismatch(on_disk, pj['rec_spec'].tolist())
    print(f'[GATE B] avg_specificity_{tr} recompute vs 40_panel: {m} mismatch')
    if m:
        sys.exit(1)
    agg[tr] = (g_spec, g_ne)
print('[GATE B] PASS — 聚合 == encode\n')

for f in PANEL_FILES:
    df = pd.read_parquet(f'{DD}/{f}')
    for tr in TRACKS:
        g_spec, g_ne = agg[tr]
        col = f'avg_named_entity_{tr}'
        mp = df[['target_bank', 'year']].merge(
            g_ne.rename(col), on=['target_bank', 'year'], how='left')
        # NaN-mask 必与 avg_specificity 一致 (同覆盖)
        nm_ne = mp[col].isna().values
        nm_sp = df[f'avg_specificity_{tr}'].isna().values
        if (nm_ne != nm_sp).any():
            print(f'[FAIL] {f} avg_named_entity_{tr} NaN-mask != avg_specificity')
            sys.exit(1)
        df = _insert_after(df, f'avg_specificity_{tr}', col, mp[col].values)
    df.to_parquet(f'{DD}/{f}', index=False)
    print(f'[PANEL] {f}: +{len(TRACKS)} cols -> {df.shape[1]} (avg_named_entity after avg_specificity)')

print('\nINJECTION COMPLETE — 6 records, named_entity raw(4) + avg(2), 两 gate 全过')
