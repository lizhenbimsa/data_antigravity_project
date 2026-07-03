"""银行∧银行三判据共现稀疏度实测 (Phase 0, 只读审计)。

执行计划 = scripts/audit/NETWORK_TRITRACK_AND_CRITERIA_EXECUTION_PLAN_2026-07-02.md
(G5/D13)。直接调用**生产函数** network_spillover.build_adjacency_matrix
(criterion ∈ {article, win1, sent}) — 审计==生产单一事实源, 禁 ad-hoc 判据复制。

输入写死 = data/processed/24_herd_decay.parquet (runner df_exploded 同源, F0.9);
⚠ 禁沿用 measure_bank_fintech_cooccurrence.py 的 14_/12_ 输入样板 (过滤前/
非幸存宇宙)。多银行 docid 组预过滤发生在生产函数内部 (单银行组不产边),
本脚本不重复实现。

产出: 三判据逐年 节点/边数/LCC/density + ①-A 三轨 dev 基线 (industry_neg_shock
分子分母/退化态) + 多银行组扫描耗时外推 (R9)。结果人工记入计划 §9。

用法 (from repo 根):
    python -m news_process.scripts.audit.measure_bank_bank_cooccurrence
"""
import os
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_PKG_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PKG_PARENT not in sys.path:
    sys.path.insert(0, _PKG_PARENT)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402


def _lcc_size(adj_df) -> int:
    """最大连通分量节点数 (纯 numpy BFS, 不依赖 networkx)。"""
    a = (adj_df.to_numpy() > 0)
    n = a.shape[0]
    seen = np.zeros(n, dtype=bool)
    best = 0
    for s in range(n):
        if seen[s]:
            continue
        stack, comp = [s], 0
        seen[s] = True
        while stack:
            u = stack.pop()
            comp += 1
            for v in np.nonzero(a[u])[0]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        best = max(best, comp)
    return best


def main() -> None:
    from news_process.pipeline.panel.network_spillover import (
        build_adjacency_matrix,
    )

    pkg_root = os.path.dirname(os.path.dirname(_HERE))
    src = os.path.join(pkg_root, 'data', 'processed', '24_herd_decay.parquet')
    df = pd.read_parquet(src)
    print(f"输入: {src}")
    print(f"  行数={len(df):,} 列数={df.shape[1]:,} "
          f"docid 组={df['docid'].nunique():,}")
    multi = df.groupby('docid')['target_bank'].nunique()
    n_multi = int((multi >= 2).sum())
    print(f"  多银行 docid 组 (≥2 幸存 target_bank) = {n_multi:,}")

    years = sorted(df['year'].unique()) if 'year' in df.columns else []
    if not years:
        # runner 在 encode 后才造 year 列; 24_herd_decay 若无则由日期派生
        df['year'] = pd.to_datetime(df['日期'], errors='coerce').dt.year
        years = sorted(df['year'].dropna().unique().astype(int))
        print(f"  (year 列由 '日期' 派生: {years})")

    print("\n== 三判据逐年网络规模 ==")
    print(f"{'year':>6} {'criterion':>9} {'nodes':>6} {'edges':>6} "
          f"{'LCC':>5} {'density':>9} {'耗时s':>7}")
    timings = {}
    for crit in ('article', 'win1', 'sent'):
        for year in years:
            t0 = time.time()
            adj, banks = build_adjacency_matrix(df, year, criterion=crit)
            dt = time.time() - t0
            timings.setdefault(crit, 0.0)
            timings[crit] += dt
            if adj.empty:
                print(f"{year:>6} {crit:>9}   (空)")
                continue
            n = len(banks)
            edges = int((adj.to_numpy() > 0).sum() // 2)
            lcc = _lcc_size(adj)
            dens = edges / (n * (n - 1) / 2) if n > 1 else float('nan')
            print(f"{year:>6} {crit:>9} {n:>6} {edges:>6} {lcc:>5} "
                  f"{dens:>9.4f} {dt:>7.2f}")

    scan_total = timings.get('win1', 0.0)
    per_group = scan_total / max(1, n_multi)
    print(f"\n== R9 耗时外推 == win1 全年扫描 {scan_total:.2f}s / "
          f"{n_multi} 多银行组 ≈ {per_group*1000:.2f} ms/组 "
          f"(生产按多银行组数线性外推)")

    print("\n== ①-A 三轨 dev 基线 (industry_neg_shock 原料) ==")
    panel_p = os.path.join(pkg_root, 'data', 'processed',
                           '40_panel_yearly.parquet')
    if os.path.exists(panel_p):
        pn = pd.read_parquet(panel_p)
        for trk, num, den in (
                ('full', 'neg_count_full', 'n_articles_llm_valid'),
                ('ctx', 'neg_count_ctx', 'n_articles_llm_valid_ctx'),
                ('ss', 'neg_count_ss', 'n_articles_llm_valid_ss')):
            if num in pn.columns:
                nz = pn[pn[num].fillna(0) > 0]
                print(f"  {trk:>4}: {num} sum={pn[num].sum()} 非零行={len(nz)}"
                      + (f" (其 {den}={nz[den].tolist()})"
                         if den in pn.columns and len(nz) else ''))
    else:
        print("  (40_panel_yearly.parquet 不在盘上, 跳过)")


if __name__ == '__main__':
    main()
