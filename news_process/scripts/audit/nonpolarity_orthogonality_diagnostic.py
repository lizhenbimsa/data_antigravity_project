"""WS-D 非极性维度正交性诊断 (bank-year 连续变量 Pearson + Spearman).

目的 (执行计划 NONPOLARITY_DIMENSIONS WS-D): 为顶刊 Appendix "Construct Validity" 提供
"非极性文本维度与情感极性/创新构念正交"的实证。stage 39c 现有 NMI 引擎只吃 article 级离散
创新码, 喂连续 bank-year 列统计无效 (计划已定级 open-redesign); 故本诊断作**独立可复现**
补充 (validation-only, golden-safe, 不进 40_panel/不改 DAG)。

口径: 读 40_panel_yearly, 在 bank-year 连续列上算 Pearson + Spearman 相关矩阵, 报告
非极性维度 × 情感极性锚点的最大 |corr| (低 = 正交); |corr|>0.5 显式标记。
[WARN] T=2 盘面仅证方法 + 给 T=2 实测值; 生产 T=18 须重跑回填论文表。
"""
from __future__ import annotations

import sys

import numpy as np
import pandas as pd

DD = 'data/processed'
OUT = 'scripts/audit/_nonpolarity_orthogonality_T2.csv'

# 非极性文本维度 (代表列; 缺则跳过)
NONPOLARITY = [
    'avg_named_entity_full', 'avg_boilerplate_full', 'avg_specificity_full',
    'avg_within_doc_redund_full', 'mean_num_intensity_full', 'mean_clarity_score_full',
    'uncert_frac_full', 'litig_frac_full', 'constr_frac_full',
    'modal_strong_frac_full', 'modal_weak_frac_full', 'complexity_frac_full',
    'frac_fls_full',
]
# 情感极性锚点 (正交性对照基准)
POLARITY = ['llm_vote_tone_full', 'msent_full', 'avg_msent_full',
            'jiang_2021_tone_full', 'loughran_tone_full']


def main() -> int:
    df = pd.read_parquet(f'{DD}/40_panel_yearly.parquet')
    npy = [c for c in NONPOLARITY if c in df.columns]
    pol = [c for c in POLARITY if c in df.columns]
    if not npy or not pol:
        print(f'[SKIP] 列不足: non-polarity={len(npy)} polarity={len(pol)}')
        return 0
    cols = npy + pol
    sub = df[cols].apply(pd.to_numeric, errors='coerce')
    pear = sub.corr(method='pearson')
    spear = sub.corr(method='spearman')
    pear.to_csv(OUT)
    print(f'[OUT] Pearson 相关矩阵 -> {OUT} ({len(cols)} 列)')

    # 非极性 × 极性 块的 |corr| (正交性证据)
    block = pear.loc[npy, pol].abs()
    print(f'\n非极性({len(npy)}) × 情感极性({len(pol)}) Pearson |corr|:')
    print(f'  max |corr| = {block.values[np.isfinite(block.values)].max():.4f} '
          f'(低 = 正交); mean = {np.nanmean(block.values):.4f}')
    flagged = [(i, c, block.loc[i, c]) for i in npy for c in pol
               if np.isfinite(block.loc[i, c]) and block.loc[i, c] > 0.5]
    if flagged:
        print('  [WARN] |corr|>0.5 (非正交, 须披露):')
        for i, c, v in sorted(flagged, key=lambda x: -x[2]):
            print(f'     {i} × {c}: {v:.3f}')
    else:
        print('  [OK] 全部 |corr| ≤ 0.5 → 非极性维度与情感极性正交 (T=2 盘面)')

    # 非极性内部高共线对 (诊断, 不进同回归)
    npblock = pear.loc[npy, npy].abs()
    hi = [(npy[a], npy[b], npblock.iloc[a, b]) for a in range(len(npy))
          for b in range(a + 1, len(npy))
          if np.isfinite(npblock.iloc[a, b]) and npblock.iloc[a, b] > 0.8]
    print(f'\n非极性内部 |corr|>0.8 高共线对 (勿同进一回归): {len(hi)}')
    for x, y, v in sorted(hi, key=lambda t: -t[2]):
        print(f'     {x} × {y}: {v:.3f}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
