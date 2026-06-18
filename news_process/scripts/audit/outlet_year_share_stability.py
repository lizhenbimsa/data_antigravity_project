"""outlet_year_share_stability.py — (媒体, 年) 级议程份额跨期稳定性描述诊断。

这是 ``ATTENTION_OUTLET_SHARE_PLAN_2026-06-18.md`` Round-3 收敛后**唯一存活的测度
形态**: 在 **(outlet, year) 粒度** (无 bank 维度 / 无 bank-mapping / 无标准化-到-bank /
无 min-coverage 门 / 无 IV) 上, 把"金科议程份额"作为一个**纯描述性的跨年漂移诊断**, 不
是处理变量、不进任何回归。三轮 (134→109→11-agent) 评审一致裁定 bank-mapped companion
列是错的载体; 本脚本只保留它正确的那一面: 看同一家媒体的金科报道占其银行报道的比例, 在
相邻年份之间稳不稳 (跨年构成漂移诊断)。

--------------------------------------------------------------------------------
白话: 每家报纸 (媒体) 在某一年里, 它写的银行新闻中有多大比例是金科话题, 这个比例叫
"议程份额 s"。如果同一家报纸 2017 年是 30%、2018 年也差不多 30%, 说明它的报道口味稳定;
如果 2017 是 30%、2018 跳到 5%, 说明这家媒体的金科关注度在跨年时漂移很大。本脚本就是
把所有 (媒体, 年) 的 s 算出来, 再看相邻年之间 s 的相关性 (越接近 1 越稳) 和平均跳动幅度
(mean |Δs|, 越小越稳)。这是一个**描述性体检**, 不掺任何因果/识别。
--------------------------------------------------------------------------------

测度定义 (与计划 §0/§1 + verified_universe.py 口径一致):
- 主题条件份额  s[o, y] = (该 (媒体,年) 的金科文章数) / (该 (媒体,年) 的全部银行新闻数)
- 分母恒为**全部银行新闻** (12_fintech_news_full, is_bank_news 全 True); Fang-Peress
  议程份额分母语义 — 非金科银行新闻从不经 stage 21 验证, 物理上不可门控, 故不门控分母。
- 分子两套口径 (并排报告, 互为稳健性):
    (A) keyword  — 关键词判定 is_fintech_news==True (12_full, 总是可算);
    (B) verified — 经 stage-21 LLM 语义精筛的 verified 集 (24_herd_decay 的
        (docid, target_bank) inner-join 子集; 镜像 restrict_to_verified 口径)。
        24_herd_decay 缺失时该口径优雅跳过 (loud warning), 不影响 keyword 口径。

跨期稳定性 (本盘只有 2 个年度 → 一对相邻期):
- 对**在 >=2 个 period 都出现**的媒体, 报告 s 的跨期 Pearson 相关 (corr) 与
  平均绝对漂移 mean |Δs|;
- 报告跨越 period 边界的媒体数 n_outlets;
- 报告 s 的分布 (count/mean/std/min/median/max + 分位)。

输入:
- data/processed/12_fintech_news_full.parquet  (必需; 分母 + keyword 分子)
- data/processed/24_herd_decay.parquet         (可选; verified 分子, 缺则跳过 B 口径)

输出:
- build/outlet_year_diagnostic/outlet_year_shares.csv    (逐 (媒体,年) 份额长表)
- build/outlet_year_diagnostic/cross_period_stability.csv (逐相邻期对的稳定性汇总)
- 控制台打印汇总。

引用锚点 (描述性诊断, 非识别):
- Hassan et al. (2019, QJE 134(4)) — 主题条件 share 的语义来源;
- Fang & Peress (2009, JF 64(5)) — extensive 议程份额分母 (全部银行新闻)。

⚠ 这是一次性审计脚本 (scripts/audit/), 非流水线阶段; 不写 panel、不进 OUTPUT_REGISTRY、
不碰 golden、不修改任何既有文件。运行: ``F:/Anaconda3/python.exe scripts/audit/outlet_year_share_stability.py``
"""
from __future__ import annotations

import os
import sys

import pandas as pd

# ── 路径常量 (相对仓库根 news_process/) ────────────────────────────────────────
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.abspath(os.path.join(_THIS_DIR, os.pardir, os.pardir))
_PROCESSED = os.path.join(_REPO_ROOT, "data", "processed")
_OUT_DIR = os.path.join(_REPO_ROOT, "build", "outlet_year_diagnostic")

_FULL_PATH = os.path.join(_PROCESSED, "12_fintech_news_full.parquet")
_HERD_PATH = os.path.join(_PROCESSED, "24_herd_decay.parquet")

# 列名 (与 pipeline 同口径; 媒体=outlet, 日期→year, is_fintech_news=keyword 金科旗标)
_OUTLET_COL = "媒体(中文)"
_DATE_COL = "日期"
_JOIN_KEYS = ["docid", "target_bank"]


def _derive_year(df: pd.DataFrame) -> pd.DataFrame:
    """从 '日期' 列派生 int 'year' (镜像 runner.py:1631-1635 口径)。"""
    df = df.copy()
    df[_DATE_COL] = pd.to_datetime(df[_DATE_COL], errors="coerce")
    df = df[df[_DATE_COL].notna()].copy()
    df["year"] = df[_DATE_COL].dt.year.astype(int)
    return df


def _verified_keyset(herd_path: str) -> set[tuple] | None:
    """读 24_herd_decay 的 (docid, target_bank) verified 键集; 缺失/读错返回 None。"""
    if not os.path.exists(herd_path):
        print(
            f"[WARN] 24_herd_decay 缺失 ({herd_path}) — 跳过 verified 口径, 仅报 keyword 口径"
        )
        return None
    try:
        verified = pd.read_parquet(herd_path, columns=_JOIN_KEYS).drop_duplicates()
    except Exception as exc:  # noqa: BLE001 — 读键失败优雅跳过 verified 口径
        print(f"[WARN] 读 24_herd_decay 键失败 ({exc}) — 跳过 verified 口径")
        return None
    return set(map(tuple, verified.itertuples(index=False, name=None)))


def compute_outlet_year_shares(
    full: pd.DataFrame, verified_keys: set[tuple] | None
) -> pd.DataFrame:
    """计算逐 (媒体, 年) 的议程份额长表。

    返回列: outlet, year, n_bank_news, n_fintech_keyword, share_keyword,
            (若 verified 可用) n_fintech_verified, share_verified。
    """
    g = full.groupby([_OUTLET_COL, "year"], dropna=False)

    out = g.agg(
        n_bank_news=("docid", "size"),
        n_fintech_keyword=("is_fintech_news", "sum"),
    ).reset_index()
    out = out.rename(columns={_OUTLET_COL: "outlet"})
    out["n_fintech_keyword"] = out["n_fintech_keyword"].astype(int)
    # 分母恒 >=1 (groupby 产生的格至少 1 行) → 无零除
    out["share_keyword"] = out["n_fintech_keyword"] / out["n_bank_news"]

    if verified_keys is not None:
        key_tuples = list(zip(full["docid"], full["target_bank"], strict=True))
        full = full.assign(
            _is_verified_ft=[k in verified_keys for k in key_tuples]
        )
        gv = (
            full.groupby([_OUTLET_COL, "year"], dropna=False)["_is_verified_ft"]
            .sum()
            .astype(int)
            .reset_index()
            .rename(columns={_OUTLET_COL: "outlet", "_is_verified_ft": "n_fintech_verified"})
        )
        out = out.merge(gv, on=["outlet", "year"], how="left")
        out["n_fintech_verified"] = out["n_fintech_verified"].fillna(0).astype(int)
        out["share_verified"] = out["n_fintech_verified"] / out["n_bank_news"]

    return out.sort_values(["outlet", "year"]).reset_index(drop=True)


def cross_period_stability(
    shares: pd.DataFrame, share_col: str
) -> tuple[pd.DataFrame, dict]:
    """对相邻 period 对计算跨期份额稳定性 (corr + mean|Δs|)。

    period = 年度。本盘只有 2 个年度 → 1 个相邻对。返回逐对汇总表 + 总览 dict。
    """
    years = sorted(shares["year"].unique().tolist())
    rows = []
    overall = {"share_col": share_col, "periods": years}
    for y0, y1 in zip(years[:-1], years[1:], strict=False):
        s0 = shares[shares["year"] == y0].set_index("outlet")[share_col]
        s1 = shares[shares["year"] == y1].set_index("outlet")[share_col]
        common = s0.index.intersection(s1.index)
        n_common = len(common)
        if n_common >= 2:
            paired = pd.DataFrame({"s0": s0.loc[common], "s1": s1.loc[common]})
            corr = paired["s0"].corr(paired["s1"])  # Pearson; NaN 若任一侧零方差
            mean_abs_delta = (paired["s1"] - paired["s0"]).abs().mean()
        else:
            corr = float("nan")
            mean_abs_delta = float("nan")
        rows.append(
            {
                "period_from": y0,
                "period_to": y1,
                "n_outlets_both": n_common,
                "cross_period_corr": corr,
                "mean_abs_delta_share": mean_abs_delta,
            }
        )
    return pd.DataFrame(rows), overall


def _print_distribution(shares: pd.DataFrame, share_col: str) -> None:
    s = shares[share_col]
    print(f"  分布 [{share_col}]  (n (媒体,年) 格 = {len(s)})")
    desc = s.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9])
    for k, v in desc.items():
        print(f"    {k:>6}: {v:.4f}")
    print(f"    零金科格占比: {(s == 0).mean():.4f}  ({int((s == 0).sum())} 格)")


def main() -> int:
    if not os.path.exists(_FULL_PATH):
        print(f"[FATAL] 缺少必需输入 {_FULL_PATH}", file=sys.stderr)
        return 1
    os.makedirs(_OUT_DIR, exist_ok=True)

    full = pd.read_parquet(_FULL_PATH)
    n_raw = len(full)
    full = _derive_year(full)
    if len(full) < n_raw:
        print(f"[INFO] 丢弃 {n_raw - len(full)} 行 (日期不可解析)")

    verified_keys = _verified_keyset(_HERD_PATH)

    print("=" * 78)
    print("(媒体, 年) 议程份额跨期稳定性描述诊断")
    print("=" * 78)
    print(f"输入 12_fintech_news_full: {len(full)} 行银行新闻 (分母全集)")
    print(f"  is_bank_news 全 True: {bool(full['is_bank_news'].all())}")
    print(f"  关键词金科 (is_fintech_news=True): {int(full['is_fintech_news'].sum())} 行")
    if verified_keys is not None:
        print(f"  verified 键集 (24_herd_decay): {len(verified_keys)} 个 (docid,target_bank)")
    print(f"  唯一媒体 outlet: {full[_OUTLET_COL].nunique()}")
    print(f"  年度 (period): {sorted(full['year'].unique().tolist())}")
    print()

    shares = compute_outlet_year_shares(full, verified_keys)
    shares_path = os.path.join(_OUT_DIR, "outlet_year_shares.csv")
    shares.to_csv(shares_path, index=False, encoding="utf-8-sig")
    print(f"[写出] 逐 (媒体,年) 份额长表: {shares_path}  ({len(shares)} 格)")
    print(f"  唯一 (媒体,年) 格: {len(shares)}")
    print()

    share_cols = ["share_keyword"]
    if verified_keys is not None:
        share_cols.append("share_verified")

    stab_frames = []
    for col in share_cols:
        print("-" * 78)
        print(f"口径: {col}")
        _print_distribution(shares, col)
        stab, _overall = cross_period_stability(shares, col)
        stab.insert(0, "share_col", col)
        stab_frames.append(stab)
        print("  跨期稳定性 (相邻年度对):")
        if stab.empty:
            print("    (仅 1 个 period, 无相邻对可比)")
        else:
            for _, r in stab.iterrows():
                print(
                    f"    {int(r['period_from'])}->{int(r['period_to'])}: "
                    f"n_outlets(两期都在)={int(r['n_outlets_both'])}  "
                    f"cross_period_corr={r['cross_period_corr']:.4f}  "
                    f"mean|Δs|={r['mean_abs_delta_share']:.4f}"
                )
        print()

    stab_all = pd.concat(stab_frames, ignore_index=True)
    stab_path = os.path.join(_OUT_DIR, "cross_period_stability.csv")
    stab_all.to_csv(stab_path, index=False, encoding="utf-8-sig")
    print(f"[写出] 跨期稳定性汇总: {stab_path}")
    print()

    print("=" * 78)
    print("汇总 (实盘数字)")
    print("=" * 78)
    for _, r in stab_all.iterrows():
        print(
            f"  [{r['share_col']}] {int(r['period_from'])}->{int(r['period_to'])}: "
            f"n_outlets={int(r['n_outlets_both'])}, "
            f"cross_period_corr={r['cross_period_corr']:.4f}, "
            f"mean_abs_delta_share={r['mean_abs_delta_share']:.4f}"
        )
    print()
    print("注: 这是描述性跨年漂移诊断, 非处理变量/识别; 本盘仅 2 个年度 (78 天窗的")
    print("    日历假象), 跨期稳定性数字仅为占位, 生产 18M/T≈19 上方有统计功效。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
