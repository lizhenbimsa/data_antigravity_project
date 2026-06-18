#!/usr/bin/env python
"""P1-A 披露包: 跨年比值漂移 (cross-year ratio drift) 的纯描述性诊断表。

【功能】
  本脚本是 P1-A "首要修复"的**纯描述性披露包** (primary fix for cross-year
  ratio drift)。它**不改任何 producer 逻辑、不新增 parquet 列、不重跑付费阶段、
  $0、golden-safe**, 仅读取已落盘的中间产物并产出供 manuscript/codebook/附录
  如实披露的 CSV 诊断表。核心关切: fintech_share / attention 等"比值"测度在
  2007–2024 (T=18) 长面板上, 其分子/分母的**口径构成会逐年漂移** (媒体进出、
  转载放大、分类器在不同年代的判定漂移、报道篇幅/数量的时代变化), 威胁跨年识别。
  本包把这些漂移源逐年量化, 以便审稿人评估其对主结果的威胁。

【四张表】(对应 task a/b/c/d)
  (a) yearly_outlet_entry_exit.csv  — 逐年媒体 (outlet) 进入/退出/流失率
      口径: 按 媒体(中文) × year, 统计每年活跃 outlet 数、首次出现 (entering)、
            末次出现 (exiting)、churn = (entering + exiting) / active。
  (b) wire_reprint_share.csv         — 逐 (outlet, year) 转载/通稿份额
      口径: 同一 (标题, 日期, target_bank) 在不同 outlet 间近重复 = 转载;
            报告每个 outlet-year 的转载份额, 及全年总趋势 (yearly_reprint_trend.csv)。
            另含 is_wire 列 (上游通讯社旗标) 的逐年份额作为交叉印证。
  (c) verified_keep_rate_by_year.csv — 逐年 verified-keep-rate (分类器漂移代理)
      口径: 候选集 = 12_fintech_news_full 中 is_fintech_news==True 的
            (docid, target_bank) 对; 存活集 = 24_herd_decay 中 llm_verified_*==True;
            keep-rate = 存活 / 候选, 逐年逐轨 (full/ctx/ss)。
            要求 24_herd_decay 存在; 缺失则跳过此表并 loud WARNING。
  (d) length_volume_drift_by_year.csv — 逐年篇幅 + 报道量漂移
      口径: 逐年平均字符数 (doc_length / cn_char_count(内容))、平均汉字数
            (cn_han_count(内容))、n_articles (去重口径)、fintech_share (去重同基)。

【计数域 / 与主管道一致性】(correct at 18M scale)
  - 复合键去重 = (target_bank, 标题, _date_str), 与
    pipeline/falsification/controls.py 的 anti-join 集合语义一致 (同稿件 = 一行)。
  - fintech_share = ft_dedup / all_bank_news_dedup (Hassan 2019 QJE Table 7 同计数域,
    PRisk/(PRisk+NPRisk)); 分子分母同取复合键去重口径。
  - 汉字口径复用 core.text.cn_text_utils.cn_han_count / cn_char_count (与
    lexical_complexity 篇内口径字节一致), 保证 18M 全量上口径不漂。
  - year 由 日期 列经 pd.to_datetime 派生 (docid 不含年份信息, 故用 日期)。

【盘面提示】当前 disk 仅 78 天窗口 (2017-11-13..2018-01-30, 仅 2017/2018 两年),
  所有逐年数字仅为**示意 (illustrative)**, 不代表 18M 全量。脚本逻辑按 T=18
  设计 (任意年份集合、任意 outlet 数均正确)。

引用锚点:
  - Hassan et al. (2019, QJE, 134(4), 2135-2202): PRisk/NPRisk 互补划分同计数域。
  - Fang & Peress (2009, JF, 64(5), 2023-2052): 媒体覆盖广度。
  - Bushee et al. (2010, JAR, 48(1), 1-19): 不同媒体来源数 (media breadth)。
  - Gentzkow & Shapiro (2010, ECMA, 78(1), 35-71): outlet house-style / 转载放大。
  - Tetlock (2007, JF, 62(3), 1139-1168): 媒体内容 vs 数量的概念区分。

用法:
  F:/Anaconda3/python.exe -m news_process.scripts.audit.p1a_disclosure_tables
  或:
  F:/Anaconda3/python.exe scripts/audit/p1a_disclosure_tables.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

# --- 复用主管道汉字/字符口径原语 (SSOT, 与 lexical_complexity 字节一致) ---
try:
    from news_process.core.text.cn_text_utils import cn_char_count, cn_han_count
except Exception:  # pragma: no cover - 直跑脚本时的路径兜底
    # parents[3] = 仓库根 (news_process 包的父目录), 供 `news_process.*` 导入
    _ROOT = Path(__file__).resolve().parents[3]
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))
    from news_process.core.text.cn_text_utils import cn_char_count, cn_han_count

# --- 路径常量 ---
# 本文件: news_process/scripts/audit/p1a_disclosure_tables.py
#   parents[0]=audit, parents[1]=scripts, parents[2]=news_process (包根)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PROCESSED = _PROJECT_ROOT / "data" / "processed"
_FINTECH_FULL = _PROCESSED / "12_fintech_news_full.parquet"
_HERD_DECAY = _PROCESSED / "24_herd_decay.parquet"
_OUT_DIR = _PROJECT_ROOT / "build" / "p1a_disclosure"

# --- 列名常量 (语料为 GBK 来源, 中文列名含中文括号) ---
COL_MEDIA = "媒体(中文)"
COL_TITLE = "标题"
COL_DATE = "日期"
COL_CONTENT = "内容"
KEY_COLS = ["target_bank", COL_TITLE, "_date_str"]


def _log(msg: str = "") -> None:
    print(msg, flush=True)


# ============================================================================
# 公共预处理
# ============================================================================
def _add_year_and_datestr(df: pd.DataFrame) -> pd.DataFrame:
    """派生标准化日期字符串 _date_str 与整数 year (由 日期 列)。

    与 controls.py anti-join 同口径: pd.to_datetime(errors='coerce')。
    """
    df = df.copy()
    dt = pd.to_datetime(df[COL_DATE], errors="coerce")
    n_nat = int(dt.isna().sum())
    if n_nat:
        _log(f"  [WARN] {n_nat:,} 行日期解析为 NaT (将从逐年统计中剔除)")
    df["_date_str"] = dt.dt.strftime("%Y-%m-%d")
    df["_year"] = dt.dt.year  # nullable float -> 后续 dropna
    return df


def _dedup_composite(df: pd.DataFrame) -> pd.DataFrame:
    """按复合键 (target_bank, 标题, _date_str) 去重 (同稿件 = 一行)。

    与 controls.py 集合语义一致: keep='first'。
    """
    return df.drop_duplicates(subset=KEY_COLS, keep="first").copy()


# ============================================================================
# (a) 媒体进入/退出/流失率
# ============================================================================
def build_outlet_entry_exit(df: pd.DataFrame) -> pd.DataFrame:
    """逐年 outlet 进入/退出/churn。

    - active(y)   = 年 y 出现过的 distinct outlet 数
    - entering(y) = 在 y 首次出现 (此前任何年未出现) 的 outlet 数
    - exiting(y)  = 在 y 末次出现 (此后任何年不再出现) 的 outlet 数
    - churn(y)    = (entering + exiting) / active   (流失/换手率)

    口径用**物理行** (含跨媒体转载), 因为问的是"哪些信息中介在场",
    转载本身即在场证据 (Bushee et al. 2010 广度构念)。
    """
    sub = df.dropna(subset=[COL_MEDIA, "_year"]).copy()
    sub["_year"] = sub["_year"].astype(int)

    # 每个 outlet 出现过的年份集合
    outlet_years = sub.groupby(COL_MEDIA)["_year"].agg(
        first_year="min", last_year="max"
    )
    first_seen = outlet_years["first_year"]
    last_seen = outlet_years["last_year"]

    years = sorted(sub["_year"].unique())
    rows = []
    prev_active: set[str] | None = None
    for y in years:
        active_outlets = set(sub.loc[sub["_year"] == y, COL_MEDIA].unique())
        n_active = len(active_outlets)
        n_enter = int((first_seen == y).sum())
        n_exit = int((last_seen == y).sum())
        # carried_over = 上一活跃年也在场的 outlet 数 (信息辅助)
        carried = (
            len(active_outlets & prev_active) if prev_active is not None else pd.NA
        )
        churn = (n_enter + n_exit) / n_active if n_active else float("nan")
        rows.append(
            {
                "year": y,
                "n_outlets_active": n_active,
                "n_entering": n_enter,
                "n_exiting": n_exit,
                "n_carried_from_prev_active": carried,
                "churn_rate": round(churn, 6),
                "entry_rate": round(n_enter / n_active, 6) if n_active else float("nan"),
                "exit_rate": round(n_exit / n_active, 6) if n_active else float("nan"),
            }
        )
        prev_active = active_outlets

    return pd.DataFrame(rows)


# ============================================================================
# (b) 转载/通稿份额
# ============================================================================
def build_wire_reprint_share(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """逐 (outlet, year) 转载份额 + 全年趋势。

    转载判据 (near-duplicate): 同一 (标题, 日期, target_bank) 在 **≥2 个不同
    outlet** 出现 → 该稿件组内除首发外的副本皆记为 reprint (转载)。这是
    Gentzkow-Shapiro (2010) house-style/转载放大在 article 级的操作化。
    另用上游 is_wire 旗标 (通讯社稿) 作交叉印证的逐年份额。

    返回:
      per_outlet_year — 每 (outlet, year): n_articles / n_reprints / reprint_share
      yearly_trend    — 每 year: 全样本 reprint_share + is_wire_share
      group_dist      — 转载组规模分布 (一稿被多少 outlet 转载)
    """
    sub = df.dropna(subset=["_year"]).copy()
    sub["_year"] = sub["_year"].astype(int)
    sub[COL_MEDIA] = sub[COL_MEDIA].fillna("__UNKNOWN_OUTLET__")

    # 稿件组键: (标题, 日期, target_bank) —— 不含 outlet, 故跨 outlet 同稿会聚到一组
    grp_cols = [COL_TITLE, "_date_str", "target_bank"]
    # 先排序再派生所有组内列, 保证全部列与同一行索引对齐 (避免跨对象 reindex)
    sub = sub.sort_values(grp_cols + [COL_MEDIA]).reset_index(drop=True)
    # 每组覆盖的 distinct outlet 数 (≥2 即存在转载)
    sub["_grp_outlet_n"] = sub.groupby(grp_cols)[COL_MEDIA].transform("nunique")
    # 组内序号: 同组内首行算首发 (0), 其余算转载 (≥1)
    sub["_intra_rank"] = sub.groupby(grp_cols).cumcount()
    # 转载标记: 组内 outlet>1 且非首发
    sub["_is_reprint"] = (sub["_grp_outlet_n"] > 1) & (sub["_intra_rank"] > 0)

    # per-outlet-year
    per_oy = (
        sub.groupby([COL_MEDIA, "_year"])
        .agg(
            n_articles=("_is_reprint", "size"),
            n_reprints=("_is_reprint", "sum"),
        )
        .reset_index()
        .rename(columns={COL_MEDIA: "outlet", "_year": "year"})
    )
    per_oy["reprint_share"] = (
        per_oy["n_reprints"] / per_oy["n_articles"].where(per_oy["n_articles"] > 0)
    ).round(6)
    per_oy = per_oy.sort_values(["year", "outlet"]).reset_index(drop=True)

    # yearly trend (全样本)
    has_wire = "is_wire" in sub.columns
    yearly_rows = []
    for y, g in sub.groupby("_year"):
        n = len(g)
        n_rp = int(g["_is_reprint"].sum())
        row = {
            "year": int(y),
            "n_articles": n,
            "n_reprints": n_rp,
            "reprint_share": round(n_rp / n, 6) if n else float("nan"),
            "n_distinct_stories": int(g.groupby(grp_cols).ngroups),
        }
        if has_wire:
            wire = pd.to_numeric(g["is_wire"], errors="coerce")
            n_wire_known = int(wire.notna().sum())
            row["is_wire_share"] = (
                round(float((wire == 1).sum()) / n_wire_known, 6)
                if n_wire_known
                else float("nan")
            )
            row["is_wire_n_known"] = n_wire_known
        yearly_rows.append(row)
    yearly_trend = pd.DataFrame(yearly_rows).sort_values("year").reset_index(drop=True)

    # 转载组规模分布
    grp_sizes = sub[sub["_grp_outlet_n"] > 1].groupby(grp_cols)[COL_MEDIA].nunique()
    if len(grp_sizes):
        gd = grp_sizes.value_counts().sort_index()
        group_dist = pd.DataFrame(
            {"n_outlets_per_story": gd.index, "n_stories": gd.values}
        )
    else:
        group_dist = pd.DataFrame(columns=["n_outlets_per_story", "n_stories"])

    return per_oy, yearly_trend, group_dist


# ============================================================================
# (c) verified-keep-rate (分类器漂移代理)
# ============================================================================
def build_verified_keep_rate(
    df_full: pd.DataFrame, herd_path: Path
) -> pd.DataFrame | None:
    """逐年 verified-keep-rate, 逐轨 (full/ctx/ss)。

    候选集 = 12_fintech_news_full 中 is_fintech_news==True 的去重
            (docid, target_bank) 对 (rule-based 预筛通过的 fintech 候选)。
    存活集 = 24_herd_decay 中 llm_verified_<track>==True 的 (docid, target_bank)。
    keep-rate = |存活| / |候选|, 逐年。LLM 在不同年代对同类稿件判定漂移
                → keep-rate 的跨年波动即 classifier-drift 代理。

    24_herd_decay 缺失 → 返回 None + loud WARNING (任务要求)。
    """
    if not herd_path.exists():
        _log("")
        _log("  " + "!" * 66)
        _log(f"  [WARN] 24_herd_decay 不存在 ({herd_path}); 跳过 verified-keep-rate 表 (c)。")
        _log("  " + "!" * 66)
        return None

    herd = pd.read_parquet(herd_path)
    herd = _add_year_and_datestr(herd)

    # 候选集: fintech-flagged, 去重 (docid, target_bank); year 由 日期 派生
    cand = df_full[df_full["is_fintech_news"]].copy()
    cand = cand.dropna(subset=["_year"])
    cand["_year"] = cand["_year"].astype(int)
    cand_keys = cand.drop_duplicates(subset=["docid", "target_bank"])
    cand_by_year = (
        cand_keys.groupby("_year").size().rename("n_candidate").reset_index()
    )

    # 存活集: 逐轨
    track_cols = {
        "full": "llm_verified_full",
        "ctx": "llm_verified_ctx",
        "ss": "llm_verified_ss",
    }
    herd_y = herd.dropna(subset=["_year"]).copy()
    herd_y["_year"] = herd_y["_year"].astype(int)
    herd_keys = herd_y.drop_duplicates(subset=["docid", "target_bank"])

    out = cand_by_year.copy()
    for track, col in track_cols.items():
        if col not in herd_keys.columns:
            _log(f"  [WARN] {col} 不在 24_herd_decay; 轨 {track} 跳过。")
            continue
        verified = herd_keys[herd_keys[col].astype("boolean").fillna(False)]
        surv = verified.groupby("_year").size().rename(f"n_verified_{track}")
        out = out.merge(surv, left_on="_year", right_index=True, how="left")
        out[f"n_verified_{track}"] = out[f"n_verified_{track}"].fillna(0).astype(int)
        out[f"keep_rate_{track}"] = (
            out[f"n_verified_{track}"] / out["n_candidate"].where(out["n_candidate"] > 0)
        ).round(6)

    # 也报告 herd 中到达 stage 21 的总候选 (reached) 逐年, 与预筛候选的差即"未到达"
    reached = (
        herd_keys.groupby("_year").size().rename("n_reached_stage21").reset_index()
    )
    out = out.merge(reached, on="_year", how="left")
    out["n_reached_stage21"] = out["n_reached_stage21"].fillna(0).astype(int)

    return out.rename(columns={"_year": "year"}).sort_values("year").reset_index(
        drop=True
    )


# ============================================================================
# (d) 篇幅 + 报道量漂移
# ============================================================================
def build_length_volume_drift(df_full: pd.DataFrame) -> pd.DataFrame:
    """逐年篇幅 (字符/汉字) + 报道量 (n_articles) + fintech_share。

    - avg_char_len  = 平均 cn_char_count(内容) (与 doc_length 字节一致, 交叉核验)
    - avg_han_len   = 平均 cn_han_count(内容)  (汉字口径, 与 lexical_complexity 一致)
    - n_articles    = 去重口径全部银行新闻篇数 (复合键去重)
    - n_fintech     = 去重口径 fintech 篇数 (is_fintech_news==True)
    - fintech_share = n_fintech / n_articles (Hassan 2019 同计数域)

    全部逐年; n_articles/share 用复合键去重 (与 controls.py 同基), avg 长度
    用去重后行集 (避免转载放大长度均值)。
    """
    dedup = _dedup_composite(df_full)
    dedup = dedup.dropna(subset=["_year"]).copy()
    dedup["_year"] = dedup["_year"].astype(int)

    # 汉字/字符长度 (复用 SSOT 原语)
    content = dedup[COL_CONTENT].fillna("")
    dedup["_char_len"] = content.map(cn_char_count)
    dedup["_han_len"] = content.map(cn_han_count)

    rows = []
    for y, g in dedup.groupby("_year"):
        n_art = len(g)
        n_ft = int(g["is_fintech_news"].sum())
        rows.append(
            {
                "year": int(y),
                "n_articles": n_art,
                "n_fintech": n_ft,
                "fintech_share": round(n_ft / n_art, 6) if n_art else float("nan"),
                "avg_char_len": round(float(g["_char_len"].mean()), 4),
                "avg_han_len": round(float(g["_han_len"].mean()), 4),
                "median_char_len": float(g["_char_len"].median()),
                "median_han_len": float(g["_han_len"].median()),
                # doc_length 上游字符口径, 交叉核验 avg_char_len
                "avg_doc_length": round(float(g["doc_length"].mean()), 4)
                if "doc_length" in g.columns
                else float("nan"),
            }
        )
    return pd.DataFrame(rows).sort_values("year").reset_index(drop=True)


# ============================================================================
# 主程序
# ============================================================================
def main() -> int:
    _log("=" * 74)
    _log("P1-A 披露包: 跨年比值漂移 (cross-year ratio drift) 描述性诊断")
    _log("=" * 74)

    if not _FINTECH_FULL.exists():
        _log(f"[FATAL] 输入缺失: {_FINTECH_FULL}")
        return 1

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    _log(f"  输入: {_FINTECH_FULL}")
    _log(f"  输入: {_HERD_DECAY} (存在={_HERD_DECAY.exists()})")
    _log(f"  输出目录: {_OUT_DIR}")
    _log("")

    df_full = pd.read_parquet(_FINTECH_FULL)
    df_full = _add_year_and_datestr(df_full)
    dt = pd.to_datetime(df_full[COL_DATE], errors="coerce")
    _log(
        f"  12_fintech_news_full: {len(df_full):,} 行; "
        f"日期窗口 {dt.min().date()} .. {dt.max().date()}; "
        f"年份 {sorted(df_full['_year'].dropna().astype(int).unique().tolist())}"
    )
    _log(
        "  ⚠ 盘面为 78 天窗口 (示意/illustrative); 逻辑按 T=18 全量设计, 18M 上正确。"
    )
    _log("")

    # (a)
    _log("─" * 74)
    _log("(a) 逐年媒体进入/退出/流失率 → yearly_outlet_entry_exit.csv")
    tbl_a = build_outlet_entry_exit(df_full)
    tbl_a.to_csv(_OUT_DIR / "yearly_outlet_entry_exit.csv", index=False, encoding="utf-8-sig")
    _log(tbl_a.to_string(index=False))
    _log("")

    # (b)
    _log("─" * 74)
    _log("(b) 转载/通稿份额 → wire_reprint_share.csv + yearly_reprint_trend.csv")
    per_oy, yearly_trend, group_dist = build_wire_reprint_share(df_full)
    per_oy.to_csv(_OUT_DIR / "wire_reprint_share.csv", index=False, encoding="utf-8-sig")
    yearly_trend.to_csv(
        _OUT_DIR / "yearly_reprint_trend.csv", index=False, encoding="utf-8-sig"
    )
    group_dist.to_csv(
        _OUT_DIR / "reprint_group_size_dist.csv", index=False, encoding="utf-8-sig"
    )
    _log("  逐年趋势 (yearly_reprint_trend):")
    _log(yearly_trend.to_string(index=False))
    _log(f"  per-(outlet,year) 行数: {len(per_oy):,} (见 wire_reprint_share.csv)")
    _log(f"  转载组规模分布: {len(group_dist)} 档 (见 reprint_group_size_dist.csv)")
    _log("")

    # (c)
    _log("─" * 74)
    _log("(c) 逐年 verified-keep-rate (分类器漂移代理) → verified_keep_rate_by_year.csv")
    tbl_c = build_verified_keep_rate(df_full, _HERD_DECAY)
    if tbl_c is not None:
        tbl_c.to_csv(
            _OUT_DIR / "verified_keep_rate_by_year.csv", index=False, encoding="utf-8-sig"
        )
        _log(tbl_c.to_string(index=False))
    else:
        _log("  (跳过: 24_herd_decay 缺失)")
    _log("")

    # (d)
    _log("─" * 74)
    _log("(d) 逐年篇幅 + 报道量漂移 → length_volume_drift_by_year.csv")
    tbl_d = build_length_volume_drift(df_full)
    tbl_d.to_csv(
        _OUT_DIR / "length_volume_drift_by_year.csv", index=False, encoding="utf-8-sig"
    )
    _log(tbl_d.to_string(index=False))
    _log("")

    # 汇总
    _log("=" * 74)
    _log("汇总 (summary.txt)")
    _log("=" * 74)
    summary_lines = [
        "P1-A cross-year ratio-drift disclosure package — summary",
        "=" * 60,
        f"source_fintech_full : {_FINTECH_FULL}",
        f"source_herd_decay   : {_HERD_DECAY} (exists={_HERD_DECAY.exists()})",
        f"date_window         : {dt.min().date()} .. {dt.max().date()} "
        f"(78-day disk slice; ILLUSTRATIVE only — logic correct at 18M / T=18)",
        f"years_on_disk       : {sorted(df_full['_year'].dropna().astype(int).unique().tolist())}",
        f"n_rows_physical     : {len(df_full):,}",
        f"n_rows_dedup        : {len(_dedup_composite(df_full)):,} "
        "(composite-key dedup = controls.py set semantics)",
        f"n_distinct_outlets  : {df_full[COL_MEDIA].nunique():,}",
        f"n_distinct_banks    : {df_full['target_bank'].nunique():,}",
        "",
        "tables written:",
        "  (a) yearly_outlet_entry_exit.csv     — outlet entry/exit/churn per year",
        "  (b) wire_reprint_share.csv           — reprint share per (outlet,year)",
        "      yearly_reprint_trend.csv         — reprint + is_wire share per year",
        "      reprint_group_size_dist.csv      — #outlets-per-reprinted-story dist",
        "  (c) verified_keep_rate_by_year.csv   — LLM-verified keep-rate per year/track"
        + ("" if tbl_c is not None else "  [SKIPPED: herd_decay missing]"),
        "  (d) length_volume_drift_by_year.csv  — char/han length + n_art + ft_share",
        "",
        "overall yearly reprint_share:",
    ]
    for _, r in yearly_trend.iterrows():
        summary_lines.append(
            f"  {int(r['year'])}: reprint_share={r['reprint_share']:.4f} "
            f"(n={int(r['n_articles'])})"
        )
    summary_lines.append("")
    summary_lines.append("overall yearly fintech_share (dedup, same counting domain):")
    for _, r in tbl_d.iterrows():
        summary_lines.append(
            f"  {int(r['year'])}: fintech_share={r['fintech_share']:.4f} "
            f"(n_articles={int(r['n_articles'])}, n_fintech={int(r['n_fintech'])})"
        )
    if tbl_c is not None:
        summary_lines.append("")
        summary_lines.append("verified keep-rate (full track) per year:")
        for _, r in tbl_c.iterrows():
            kr = r.get("keep_rate_full", float("nan"))
            summary_lines.append(
                f"  {int(r['year'])}: keep_rate_full={kr:.4f} "
                f"(candidate={int(r['n_candidate'])}, "
                f"verified={int(r.get('n_verified_full', 0))})"
            )

    summary_text = "\n".join(summary_lines)
    (_OUT_DIR / "summary.txt").write_text(summary_text + "\n", encoding="utf-8")
    _log(summary_text)
    _log("")
    _log(f"[OK] 所有表已写入 {_OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
