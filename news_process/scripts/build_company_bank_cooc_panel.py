"""WP1 — 上市公司×年 银企共现媒体报道面板 (COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v34).

产出 (D9/D10):
  data/processed/company_bank_cooc_panel.dta        主面板 (105,032 行, 19 固定列 + 加权列)
  data/processed/company_bank_cooc_panel.parquet    伴生 (未缩写全名)
  data/processed/company_bank_cooc_panel_codebook.md
  data/processed/_company_bank_cooc_pairs.parquet   pair 长表 10 列 (被删加权列唯一重构载体)

模块级 SSOT 双函数 (D18, WP5 import 复用, 禁第二份实现):
  build_measure_library(input21_df, panel40_df, alignment_df, benefit_df, controls_df, registry)
  compute_weighted_panel(weights, measures, registry)

独立派生数据脚本, 不注册 DAG; $0 纯字符串匹配, 无 API 无随机。
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "processed"
CONFIG = REPO / "config"
TRACKS = ("full", "ctx", "ss")
ABS_YEAR_MIN, ABS_YEAR_MAX = 2007, 2025  # 绝对合法域 (D10)

import logging

logger = logging.getLogger("company_bank_cooc_panel")
if not logger.handlers:
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[cooc_panel] %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


def log(msg: str, warn: bool = False) -> None:
    (logger.warning if warn else logger.info)(msg)


# ---------------------------------------------------------------- paths.yaml 解析 (D10 键名钉死)
def default_paths() -> dict[str, Path]:
    paths_yaml = yaml.safe_load((CONFIG / "paths.yaml").read_text(encoding="utf-8"))

    def p(key: str, fallback: str) -> Path:
        rel = paths_yaml.get(key, fallback) if isinstance(paths_yaml, dict) else fallback
        q = Path(rel)
        return q if q.is_absolute() else REPO / q
    return {
        "input": p("output_21_tone_llms_full", "data/processed/21_tone_llms_full.parquet"),
        "panel": p("output_40_panel_yearly", "data/processed/40_panel_yearly.parquet"),
        "alignment": p("output_15_article_alignment", "data/processed/16_article_alignment.parquet"),
        # 27 号 paths.yaml 无键 (v18 核实) — 脚本内常量, 镜像 dimension_analysis.py 落盘路径
        "benefit": DATA / "27_benefit_dimensions_panel.parquet",
        "controls": p("output_51_panel_controls", "data/processed/51_panel_with_controls.parquet"),
    }


# ---------------------------------------------------------------- 名单载入 + AC 自动机 + D4/D4b
def load_name_assets(registry: dict):
    companies = yaml.safe_load((CONFIG / "company_listed_names.yaml").read_text(encoding="utf-8"))["companies"]
    banks = yaml.safe_load((CONFIG / "bank_names.json").read_text(encoding="utf-8"))
    company_names = [c["company_listed_name"] for c in companies]

    import ahocorasick
    A = ahocorasick.Automaton()
    variant_owner: dict[str, list[str]] = {}
    for c in companies:
        for v in c["variants"]:
            if not v or not v.strip():
                raise SystemExit(f"variant 空串守卫: 公司 {c['company_listed_name']} 含空/纯空白 variant")
            variant_owner.setdefault(v, []).append(c["company_listed_name"])
    for v, owners in variant_owner.items():
        A.add_word(v, (v, owners))
    A.make_automaton()

    bank_canonical = {b["bank_name"] for b in banks}
    # D4b: bank_name → 其全部 variants 的公司-variant 真子串集
    company_variants = set(variant_owner)
    bank_substr: dict[str, frozenset[str]] = {}
    for b in banks:
        sub = set()
        for vb in b["variants"]:
            for cv in company_variants:
                if cv != vb and cv in vb:  # 真子串 (cv ⊊ vb)
                    sub.add(cv)
        if sub:
            bank_substr[b["bank_name"]] = frozenset(sub)
    # D4 own-bank 对照 (registry SSOT)
    own_map = {comp: set(bs) for comp, bs in registry["bank_company_map"].items()}
    bank_company_set = set(own_map)
    return A, variant_owner, bank_canonical, bank_substr, own_map, bank_company_set, company_names


# ---------------------------------------------------------------- 21_full 载入与断言 (WP1-2)
INPUT_COLS = ["docid", "日期", "target_bank", "content_full", "content_ctx", "content_ss",
              "ss_is_fallback", "llm_verified_full",
              "fintech_total_count", "fintech_upper_count", "fintech_lower_count",
              "fintech_distinct_keywords", "fintech_in_title",
              "mention_density", "target_bank_mention_count"]


def load_input21(path: Path, bank_canonical: set[str]) -> pd.DataFrame:
    df = pd.read_parquet(path, columns=INPUT_COLS)
    if len(df) == 0:
        raise SystemExit("21 号 0 行输入")
    if df["docid"].isna().any():
        raise SystemExit("docid 非空断言失败 (null docid 会折叠去重单元静默减计)")
    dates = pd.to_datetime(df["日期"], errors="raise")  # object 字符串, 显式解析 fail-loud
    df = df.assign(_year=dates.dt.year)
    # (docid, target_bank) 去重: keep='first' 按读入序; 重复行三轨文本 hash 须一致
    dup_mask = df.duplicated(subset=["docid", "target_bank"], keep=False)
    if dup_mask.any():
        grp = df.loc[dup_mask].groupby(["docid", "target_bank"])
        for keycols in ("content_full", "content_ctx", "content_ss"):
            if (grp[keycols].nunique(dropna=False) > 1).any():
                raise SystemExit(f"(docid,target_bank) 重复行 {keycols} 不一致 — 确定性失锚")
        n_before = len(df)
        df = df.drop_duplicates(subset=["docid", "target_bank"], keep="first")
        log(f"(docid,target_bank) 去重删行 {n_before - len(df)}", warn=True)
    extra = set(df["target_bank"].unique()) - bank_canonical
    if extra:
        raise SystemExit(f"target_bank ⊄ canonical 集: {sorted(extra)[:5]} — D4b 子串作废会静默失效")
    df["_verified"] = df["llm_verified_full"].eq(True)  # NaN 按未验证 (D7)
    for t in TRACKS:
        col = f"content_{t}"
        n_empty = int((df[col].isna() | (df[col] == "")).sum())
        df[col] = df[col].fillna("")
        if n_empty:
            level = n_empty / len(df) > 0.01
            log(f"{t} 轨空文本 {n_empty} 行 ({n_empty/len(df):.2%})", warn=level)
    return df


# ---------------------------------------------------------------- 三轨 AC 扫描 (WP1-3)
def scan_hits(df: pd.DataFrame, A, bank_substr, own_map) -> pd.DataFrame:
    """逐行三轨 AC 扫描, D4/D4b 内联作废 → 命中明细 (company, bank, year_raw, docid, track,
    verified, ss_fallback, min_variant_len, max_variant_len)。"""
    records: list[tuple] = []
    it = df[["docid", "_year", "target_bank", "content_full", "content_ctx", "content_ss",
             "ss_is_fallback", "_verified"]].itertuples(index=False, name=None)
    for docid, year, bank, c_full, c_ctx, c_ss, ss_fb, verified in it:
        sub = bank_substr.get(bank)
        for track, text in (("full", c_full), ("ctx", c_ctx), ("ss", c_ss)):
            if not text:
                continue
            per_company: dict[str, list[str]] = {}
            for _, (variant, owners) in A.iter(text):
                for comp in owners:  # D5 跨公司重复 variant: 全部归属公司各计
                    per_company.setdefault(comp, []).append(variant)
            for comp, vars_hit in per_company.items():
                if bank in own_map.get(comp, ()):  # D4 own-bank 跳过 (银行系公司自共现)
                    continue
                if sub and all(v in sub for v in vars_hit):  # D4b 逐轨: 全部命中 ⊂ 子串集 → 作废
                    continue
                lens = [len(v) for v in vars_hit]
                records.append((comp, bank, year, docid, track, verified, bool(ss_fb),
                                min(lens), max(lens)))
    hits = pd.DataFrame(records, columns=["company", "bank", "year_raw", "docid", "track",
                                          "verified", "ss_fallback", "min_vlen", "max_vlen"])
    return hits


# ---------------------------------------------------------------- 归年映射与年窗 (D1/D10/v19/v20)
def build_year_map(hits: pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
    """绝对合法域剔除 → 全局 docid→min(年) 映射 (窗口裁剪之前建立, v20 顺序封口)。"""
    bad = (hits["year_raw"] < ABS_YEAR_MIN) | (hits["year_raw"] > ABS_YEAR_MAX)
    n_bad = int(bad.sum())
    if n_bad:
        frac = n_bad / len(hits)
        log(f"绝对合法域外年份行剔除 {n_bad} ({frac:.3%})", warn=True)
        if frac > 0.001:
            raise SystemExit(f"合法域外年份占比 {frac:.3%} > 0.1%")
        hits = hits.loc[~bad]
    year_map = hits.groupby("docid")["year_raw"].min()
    n_multi = int((hits.groupby("docid")["year_raw"].nunique() > 1).sum())
    if n_multi:
        log(f"同 docid 跨年 {n_multi} 篇 → min(日期) 归年", warn=True)
    hits = hits.assign(year=hits["docid"].map(year_map))
    return year_map, hits


# ---------------------------------------------------------------- pair 长表 (WP1-3 v22, 10 列)
def build_pair_table(hits: pd.DataFrame, year_min: int, year_max: int) -> pd.DataFrame:
    h = hits[(hits["year"] >= year_min) & (hits["year"] <= year_max)].copy()
    # k / k_v: 该 docid 该公司逐轨的去重有效银行数 (作废后; verified 版限 verified 行)
    dk = h.drop_duplicates(["company", "track", "docid", "bank"]).copy()
    key3 = pd.MultiIndex.from_frame(dk[["company", "track", "docid"]])
    key4 = pd.MultiIndex.from_frame(dk[["company", "bank", "track", "docid"]])
    k = dk.groupby(["company", "track", "docid"])["bank"].nunique()
    kv = dk[dk["verified"]].groupby(["company", "track", "docid"])["bank"].nunique()
    d = dk
    d["k"] = key3.map(k)
    d["k_v"] = key3.map(kv) if len(kv) else np.nan
    d["frac"] = 1.0 / d["k"]
    d["frac_v"] = np.where(d["verified"], 1.0 / d["k_v"], 0.0)
    # longhit: 该 (company,bank,docid,track) 存在任一 ≥4 字 variant 命中即计 (v23 混合命中语义)
    lh = h.groupby(["company", "bank", "track", "docid"])["max_vlen"].max() >= 4
    d["longhit"] = key4.map(lh)
    # strict (仅 ss 轨语义): 剔 ss_fallback 行; full/ctx 恒等填充
    strict_docs = h.groupby(["company", "bank", "track", "docid"])["ss_fallback"].agg(lambda s: not s.all())
    d["nonfb"] = key4.map(strict_docs)
    d["ver_any"] = key4.map(h.groupby(["company", "bank", "track", "docid"])["verified"].any())
    d = d.sort_values(["company", "bank", "track", "docid"], kind="mergesort")  # 稳定排序后 sum (§5.3)
    g = d.groupby(["company", "bank", "year", "track"], sort=True)
    pair = pd.DataFrame({
        "n_docs": g["docid"].nunique(),
        "n_docs_v": g.apply(lambda x: x.loc[x["ver_any"], "docid"].nunique(), include_groups=False),
        "n_docs_strict": g.apply(lambda x: x.loc[x["nonfb"], "docid"].nunique(), include_groups=False),
        "n_docs_frac": g["frac"].sum(),
        "n_docs_frac_v": g["frac_v"].sum(),
        "n_docs_longhit": g.apply(lambda x: x.loc[x["longhit"], "docid"].nunique(), include_groups=False),
    }).reset_index()
    # full/ctx 轨 n_docs_strict = n_docs 恒等填充 (fallback 概念仅 ss 轨有, schema 注明)
    m = pair["track"].isin(["full", "ctx"])
    pair.loc[m, "n_docs_strict"] = pair.loc[m, "n_docs"]
    for c in ("n_docs", "n_docs_v", "n_docs_strict", "n_docs_longhit"):
        pair[c] = pair[c].astype("int32")
    return pair


# ---------------------------------------------------------------- 计数聚合 (A) (WP1-4)
def build_counts(hits: pd.DataFrame, companies: list[str], year_min: int, year_max: int,
                 bank_company_set: set[str]) -> pd.DataFrame:
    h = hits[(hits["year"] >= year_min) & (hits["year"] <= year_max)]
    # 全局去重键 = (company, track, docid) 不含 year (v19); year 由映射赋值
    dd = h.drop_duplicates(["company", "track", "docid"])
    out: dict[str, pd.Series] = {}
    for t in TRACKS:
        s = dd[dd["track"] == t]
        out[f"n_cooc_{t}"] = s.groupby(["company", "year"])["docid"].nunique()
        sv = h[(h["track"] == t) & h["verified"]].drop_duplicates(["company", "docid"])
        out[f"n_cooc_{t}_v"] = sv.groupby(["company", "year"])["docid"].nunique()
        out[f"n_banks_{t}"] = h[h["track"] == t].groupby(["company", "year"])["bank"].nunique()
    # ss_strict: 剔除该 docid 全部 ss 行均 fallback 的报道
    ss = h[h["track"] == "ss"].copy()
    if len(ss):
        nonfb_doc = ss.groupby(["company", "docid"])["ss_fallback"].agg(lambda s: not s.all())
        ss["nonfb"] = pd.MultiIndex.from_frame(ss[["company", "docid"]]).map(nonfb_doc)
        out["n_cooc_ss_strict"] = (ss[ss["nonfb"]].drop_duplicates(["company", "docid"])
                                   .groupby(["company", "year"])["docid"].nunique())
    else:
        out["n_cooc_ss_strict"] = pd.Series(dtype="float64")
    years = list(range(year_min, year_max + 1))
    idx = pd.MultiIndex.from_product([companies, years], names=["company_listed_name", "year"])
    panel = pd.DataFrame(index=idx)
    for name, s in out.items():
        if len(s) == 0:  # 空轨/空组: groupby 空 df 产单层索引, 换成空双层
            s = pd.Series(dtype="float64", index=pd.MultiIndex.from_arrays(
                [[], []], names=["company_listed_name", "year"]))
        else:
            s.index.names = ["company_listed_name", "year"]
        panel[name] = s
    panel = panel.fillna(0).astype("int32").reset_index()
    panel["year"] = panel["year"].astype("int16")
    panel["is_bank_company"] = panel["company_listed_name"].isin(bank_company_set).astype("int8")
    return panel


def add_hhi(panel: pd.DataFrame, pair: pd.DataFrame) -> pd.DataFrame:
    """D8b cooc_hhi_{track}: canonical n_docs 份额平方和; 单银行≡1; 零共现 NaN。"""
    for t in TRACKS:
        p = pair[pair["track"] == t]
        tot = p.groupby(["company", "year"])["n_docs"].transform("sum")
        share2 = (p["n_docs"] / tot) ** 2
        hhi = share2.groupby([p["company"], p["year"]]).sum()
        hhi.index.names = ["company_listed_name", "year"]
        panel = panel.merge(hhi.rename(f"cooc_hhi_{t}"), how="left",
                            left_on=["company_listed_name", "year"], right_index=True)
    return panel


# ---------------------------------------------------------------- 测度库 (SSOT 函数, WP5 复用)
def _measure_col_id(entry: dict, track: str) -> str | None:
    """entry×track → 测度库列 ID (40/51/27 直读=源列名; 16/21 自聚合=输出名)。"""
    if entry["source"] in ("16",):
        src = entry["col_by_track"].get(track)
        return f"__agg16__{entry['basename']}_{track}" if src else None
    if entry["source"] in ("21",):
        return f"__agg21__{entry['basename']}"  # track-agnostic 自聚合
    return entry["col_by_track"].get(track)


def build_measure_library(input21_df: pd.DataFrame, panel40_df: pd.DataFrame,
                          alignment_df: pd.DataFrame | None, benefit_df: pd.DataFrame | None,
                          controls_df: pd.DataFrame | None, registry: dict) -> pd.DataFrame:
    """五上游 → 统一银行×年测度库 (index=(target_bank, year), 列 = emit 条目源列)。

    v33 S1 签名钉死: 入参 = 五上游已读 DataFrame + registry 对象, 读盘留调用方。
    引擎只迭代 emit_panel=true 条目, join 只取其源列 (v23 引擎迭代域)。
    """
    emit = [e for e in registry["entries"] if e["emit_panel"]]
    frames: list[pd.DataFrame] = []

    def keyed(df: pd.DataFrame) -> pd.DataFrame:
        return df.set_index(["target_bank", "year"])

    # 40/51/27 直读
    for src_tag, df in (("40", panel40_df), ("51", controls_df), ("27", benefit_df)):
        if df is None:
            continue
        want = sorted({c for e in emit if e["source"] == src_tag
                       for c in e["col_by_track"].values() if c and c in df.columns})
        if want:
            frames.append(keyed(df)[want])
    # 16 号 PA 自聚合 (verified 子集 semi-join, v16 P0; 双向差分日志 v20)
    if alignment_df is not None:
        ver_keys = input21_df.loc[input21_df["_verified"], ["docid", "target_bank"]].drop_duplicates()
        merged = alignment_df.merge(ver_keys, on=["docid", "target_bank"], how="inner")
        miss = len(ver_keys) - len(merged.drop_duplicates(["docid", "target_bank"]))
        if miss:
            frac = miss / max(len(ver_keys), 1)
            log(f"PA 双向差分: verified ∖ 16 号 = {miss} ({frac:.3%})", warn=frac > 0.001)
        # 16 号无日期列 → 借 21 号 (docid,target_bank)→_year (归年与计数侧同源)
        y21 = input21_df.set_index(["docid", "target_bank"])["_year"]
        merged["year"] = pd.MultiIndex.from_frame(merged[["docid", "target_bank"]]).map(y21)
        pa_cols = {}
        for e in emit:
            if e["source"] != "16":
                continue
            for t in TRACKS:
                src = e["col_by_track"].get(t)
                if src and src in merged.columns:
                    pa_cols[f"__agg16__{e['basename']}_{t}"] = src
        if pa_cols:
            g = merged.groupby(["target_bank", "year"])
            pa = pd.DataFrame({out: g[src].mean() for out, src in pa_cols.items()})
            frames.append(pa)
    # 21 号 KW/FOCUS 自聚合 (verified 子集宇宙, mean/share)
    ver = input21_df.loc[input21_df["_verified"]]
    g21 = ver.groupby(["target_bank", "_year"])
    agg21 = {}
    for e in emit:
        if e["source"] != "21":
            continue
        src = e["col_by_track"]["full"]
        col = f"__agg21__{e['basename']}"
        agg21[col] = g21[src].mean()  # share 型源列为 0/1, mean 即 share
    if agg21:
        a21 = pd.DataFrame(agg21)
        a21.index.names = ["target_bank", "year"]
        frames.append(a21)

    lib = pd.concat(frames, axis=1)
    lib = lib.loc[:, ~lib.columns.duplicated()]
    lib.index.names = ["target_bank", "year"]
    return lib


# ---------------------------------------------------------------- 加权引擎 (SSOT 纯函数, D18)
def compute_weighted_panel(weights: pd.DataFrame, measures: pd.DataFrame, registry: dict,
                           chunk: int = 100) -> pd.DataFrame:
    """权重长表 + 测度库 → 加权列宽表 (company×year × cw/ce 全名列, 列序 registry SSOT)。

    weights schema (D18/DV1 引擎消费面): (company, bank, year, w[, track])。
    含 track 列 → 逐轨三矩阵 (媒体); 无 track 列 → 同一 W 对三轨广播 (七替代权)。
    引擎入口统一预处理 = 丢弃命名稳健臂列 + drop w 缺失行 (DV4a 组级全缺互锁)。
    cw = Σ(w·X.fillna(0)·notna(X)) / Σ(w·notna(X)); ce = mean(X|notna); N=1 短路 cw:=X。
    """
    keep = [c for c in ("company", "bank", "year", "w", "track") if c in weights.columns]
    W = weights[keep].dropna(subset=["w"]).copy()
    has_track = "track" in W.columns
    emit = [e for e in registry["entries"] if e["emit_panel"]]

    out_frames: list[pd.DataFrame] = []
    for t in TRACKS:
        Wt = W[W["track"] == t] if has_track else W
        if Wt.empty:
            continue
        # 分块 join (WP1-5 内存陷阱二选一之 (a)); 每批 chunk 列
        todo: list[tuple[str, str]] = []  # (输出全名, 测度库列)
        for e in emit:
            if t not in e["emit_tracks"]:
                continue
            col = _measure_col_id(e, t)
            todo.append((f"{e['basename']}__{t}", col))
        results: dict[str, pd.Series] = {}
        for i in range(0, len(todo), chunk):
            batch = todo[i:i + chunk]
            cols = [c for _, c in batch if c and c in measures.columns]
            sub = Wt.merge(measures[sorted(set(cols))], left_on=["bank", "year"],
                           right_index=True, how="left") if cols else Wt.copy()
            for out_name, mcol in batch:
                if not mcol or mcol not in measures.columns:
                    results[f"cw_{out_name}"] = pd.Series(dtype="float64")
                    results[f"ce_{out_name}"] = pd.Series(dtype="float64")
                    continue
                x = sub[mcol]
                valid = x.notna()
                num = (sub["w"] * x.fillna(0) * valid).groupby([sub["company"], sub["year"]]).sum()
                den = (sub["w"] * valid).groupby([sub["company"], sub["year"]]).sum()
                cw = num / den.replace(0, np.nan)
                ce = x.groupby([sub["company"], sub["year"]]).mean()  # mean skipna
                nvalid = valid.groupby([sub["company"], sub["year"]]).sum()
                # N=1 短路: 唯一非缺失测度银行 → cw := X (防浮点漂移, D13/v21 N 语义;
                # R2 P2-3: 限 den>0, w=0 理论边界不短路)
                if (nvalid == 1).any():
                    one = nvalid[(nvalid == 1) & (den > 0)].index
                    xonly = x[valid].groupby([sub.loc[valid, "company"], sub.loc[valid, "year"]]).first()
                    cw.loc[one] = xonly.loc[one]
                results[f"cw_{out_name}"] = cw
                results[f"ce_{out_name}"] = ce
        nonempty = {k: v for k, v in results.items() if len(v)}
        if nonempty:
            wide = pd.DataFrame(nonempty)
            for k in results:
                if k not in wide.columns:
                    wide[k] = np.nan  # 缺源列 → 全 NaN 列, schema 恒等 registry 推导值
        else:  # 全部缺源列: 用权重键构造空骨架
            idx = pd.MultiIndex.from_frame(Wt[["company", "year"]].drop_duplicates())
            wide = pd.DataFrame({k: np.nan for k in results}, index=idx)
        wide.index.names = ["company_listed_name", "year"]
        # 列名规整: basename__track → basename_track (占位分隔避免基名内下划线歧义)
        wide.columns = [c.replace("__", "_") for c in wide.columns]
        out_frames.append(wide)
    if not out_frames:
        return pd.DataFrame()
    # (R2 P2-2) 某轨权重行为空 → 该轨列仍须在 (全 NaN), schema 恒等 registry 推导值跨环境不变
    have = {c for f in out_frames for c in f.columns}
    missing_track_cols = [f"{arm}_{e['basename']}_{t}" for e in emit for t in TRACKS
                          if t in e["emit_tracks"] for arm in ("cw", "ce")
                          if f"{arm}_{e['basename']}_{t}" not in have]
    if missing_track_cols:
        for c in missing_track_cols:
            out_frames[0][c] = np.nan
    out = pd.concat(out_frames, axis=1)
    # 列序 = registry SSOT: 逐条目 → 轨 full/ctx/ss → 臂 cw/ce
    order = [f"{arm}_{e['basename']}_{t}" for e in emit for t in TRACKS if t in e["emit_tracks"]
             for arm in ("cw", "ce")]
    order = [c for c in order if c in out.columns] + [c for c in out.columns if c not in set(order)]
    return out[order]


def compute_wt_base(pair: pd.DataFrame, measures: pd.DataFrame) -> pd.DataFrame:
    """cooc_wt_base_{track} (D12 pair 级公式; 引擎边界外由调用方计算, v31 R3)。"""
    in_panel_keys = set(measures.index)
    p = pair.assign(_in=[(b, y) in in_panel_keys for b, y in zip(pair["bank"], pair["year"])])
    out = {}
    for t in TRACKS:
        pt = p[p["track"] == t]
        num = (pt["n_docs"] * pt["_in"]).groupby([pt["company"], pt["year"]]).sum()
        den = pt.groupby(["company", "year"])["n_docs"].sum()
        s = num / den
        s.index.names = ["company_listed_name", "year"]
        out[f"cooc_wt_base_{t}"] = s
    return pd.DataFrame(out)


# ---------------------------------------------------------------- 标签 (D9 双闸)
FAMILY_LABEL = {
    "Q": "数量", "F": "金科强度", "S1": "情感LLM", "S1b": "情感LLM连续", "S1c": "情感正负份额",
    "S2": "情感词典", "S2b": "词典零规则", "S3": "词典均值", "S4": "情感BERT", "S4b": "BERT份额",
    "S5": "加权情感", "S6": "LM扩展", "S7": "情感切片", "C1": "分类共识", "C1b": "分类概率",
    "C2": "分类per-model", "QD": "分维度数量", "F2": "数字强度", "W": "洗白", "B": "社会效益",
    "ST": "陈旧度", "BP": "模板化", "RW": "罕见词", "AD": "采纳", "FE": "金科暴露", "CO": "语义凝聚",
    "AS": "权威相似", "AC": "算法迎合", "HD": "羊群", "SD": "战略差异化", "MC": "媒体构成",
    "NW": "网络", "CV": "媒体覆盖", "AT": "注意力", "PC": "同伴竞争", "IN": "行业冲击",
    "DA": "媒体分歧", "CS": "报道形态", "DS": "维度情感", "CL": "清晰度", "DP": "词典正负比",
    "TD": "情感动态", "CT": "迎合", "PE": "政策暴露", "PA": "政策对齐", "BD": "效益维度",
    "CTRL": "覆盖控制", "KW": "金科关键词", "FOCUS": "聚焦度", "MISC": "杂项",
    "GAP_UNPLANNED": "补遗", "S5_GAP": "加权情感补漏",
}


def make_label(arm: str, base: str, track: str, family: str, scheme_word: str = "共现") -> str:
    arm_word = f"{scheme_word}加权" if arm == "cw" else "等权均值"
    lbl = f"{arm_word}-{FAMILY_LABEL.get(family, family)}-{base}-{track}轨"
    lbl = lbl[:80]  # 截断单位 = 字符 (v20 封口); 字节闸只作断言
    assert len(lbl.encode("utf-8")) <= 320
    return lbl


# ---------------------------------------------------------------- dta 写出
def write_outputs(panel: pd.DataFrame, registry: dict, out_dta: Path, scheme_word: str = "共现",
                  fixed_labels: dict[str, str] | None = None) -> None:
    import pyreadstat
    emit = {e["basename"]: e for e in registry["entries"] if e["emit_panel"]}
    rename: dict[str, str] = {}
    labels: dict[str, str] = dict(fixed_labels or {})
    for col in panel.columns:
        m = None
        for arm in ("cw", "ce"):
            if col.startswith(arm + "_"):
                rest = col[len(arm) + 1:]
                for t in TRACKS:
                    if rest.endswith("_" + t):
                        base = rest[: -(len(t) + 1)]
                        if base in emit:
                            m = (arm, base, t)
                        break
                break
        if m:
            arm, base, t = m
            e = emit[base]
            short = f"{arm}_{e['short_name']}_{t}"
            rename[col] = short
            labels[short] = make_label(arm, base, t, e["family"], scheme_word)
    dta = panel.rename(columns=rename)
    assert all(len(c) <= 32 for c in dta.columns), "dta 变量名超 32"
    assert len(set(dta.columns)) == len(dta.columns), "dta 变量名碰撞"
    pyreadstat.write_dta(dta, str(out_dta), column_labels=[labels.get(c, c) for c in dta.columns])
    panel.to_parquet(out_dta.with_suffix(".parquet"))  # 伴生用未缩写全名


FIXED_LABELS = {
    "company_listed_name": "上市公司中文全称",
    "year": "报道发表年",
    "is_bank_company": "该公司自身是否为银行(D4, 42家)",
    "n_cooc_full": "银企共现报道数-full轨",
    "n_cooc_ctx": "银企共现报道数-ctx轨",
    "n_cooc_ss": "银企共现报道数-ss轨",
    "n_cooc_full_v": "同full轨, 限LLM验证通过报道",
    "n_cooc_ctx_v": "同ctx轨, 限LLM验证通过报道",
    "n_cooc_ss_v": "同ss轨, 限LLM验证通过报道",
    "n_cooc_ss_strict": "同ss轨, 剔除ss回退报道",
    "n_banks_full": "full轨共现去重银行家数",
    "n_banks_ctx": "ctx轨共现去重银行家数",
    "n_banks_ss": "ss轨共现去重银行家数",
    "cooc_hhi_full": "full轨共现权重集中度HHI",
    "cooc_hhi_ctx": "ctx轨共现权重集中度HHI",
    "cooc_hhi_ss": "ss轨共现权重集中度HHI",
    "cooc_wt_base_full": "full轨共现落在银行面板的比例",
    "cooc_wt_base_ctx": "ctx轨共现落在银行面板的比例",
    "cooc_wt_base_ss": "ss轨共现落在银行面板的比例",
}

FIXED_ORDER = list(FIXED_LABELS)


# ---------------------------------------------------------------- codebook (D9)
def write_codebook(path: Path, registry: dict, panel: pd.DataFrame, input21: pd.DataFrame,
                   year_min: int, year_max: int) -> None:
    emit = [e for e in registry["entries"] if e["emit_panel"]]
    yearly = input21.groupby("_year").size()
    lines = [
        "# company_bank_cooc_panel — codebook",
        "",
        f"> 机器可读 emit 子集 SSOT = `config/company_bank_cooc_registry.yaml` (registry_sha256 "
        f"{registry['meta']['registry_sha256'][:16]}…); 按 §3b 全谱表找列请先查该清单 (D17 裁剪在案)。",
        "",
        "## 数据谱系",
        "原始媒体语料 → stage 11/12 银行·金科实体识别 → stage 13 银∧金科邻近共现硬过滤 → stage 14 "
        "三轨文本物化 → stage 21 三家 LLM 情感/验证 (21_tone_llms_full.parquet 全宇宙, 行=报道×目标银行) "
        "→ 本脚本对三轨文本做上市公司名 AC 匹配 → 按公司×年聚合。计数的语料宇宙是\"银行金融科技报道\", "
        "不是全部新闻。",
        "",
        "## 两套缺失语义",
        "计数列无命中填 0 (面板基底语义); 加权测度列无共现/无可用银行置缺失 (Stata `.`), 绝非 0。",
        "",
        "## 门控双宇宙 (D7/§3b ⑦)",
        "权重 = canonical 不门控计数 (21_full 全宇宙); 测度侧统一为 verified 宇宙 "
        "(40 面板沿上游门控, 自聚合族 = verified 子集 semi-join)。两宇宙刻意不同属设计。",
        "",
        "## 固定列 (19)",
        "| 变量 | 标签 |", "|---|---|",
    ]
    lines += [f"| `{k}` | {v} |" for k, v in FIXED_LABELS.items()]
    lines += [
        "",
        "## 加权测度列",
        "构造通式: `cw_X_t(i,yr) = Σ_b [n_cooc_t(b,i,yr)/Σ_b' n_cooc_t(b',i,yr)] × X_t(b,yr)` "
        "(分母限该测度该年非缺失共现银行并重归一, D12); `ce_X_t` 等权算术平均稳健臂 (D13)。"
        "权重与测度同轨; track-agnostic 源列以权重轨为准。",
        "",
        "### D17 三义务段",
        "- allv 锚点构念由 PA 族单载体承载 (auth_sim/AD allv 交叉臂已裁, pair 表可重构)。",
        "- `bert_avg_neu ≡ 1 − bert_avg_pos − bert_avg_neg` 恒等 (残差 ≤1e-4; finbert2 无 neu 致 "
        "ensemble 层混 2/3 模型宇宙, 禁加和断言)。",
        "- 被删 410 基名 ×6 臂列研究地位不降: 全部可由 pair 长表 + 银行×年面板 (46/40 dta 全列) 按 D12 "
        "公式一行 merge 精确重构 (isclose 级)。重构代码段:",
        "",
        "```python",
        "import pandas as pd",
        "pair = pd.read_parquet('_company_bank_cooc_pairs.parquet')",
        "bank = pd.read_parquet('40_panel_yearly.parquet')  # 或 46 dta 全列",
        "t, X = 'full', '<被删源列名>'",
        "p = pair[pair.track == t].merge(bank[['target_bank', 'year', X]],",
        "        left_on=['bank', 'year'], right_on=['target_bank', 'year'])",
        "p = p[p[X].notna()]",
        "w = p.n_docs / p.groupby(['company', 'year']).n_docs.transform('sum')",
        "cw = (w * p[X]).groupby([p.company, p.year]).sum()  # cw_<X>_full",
        "ce = p.groupby(['company', 'year'])[X].mean()       # ce_<X>_full",
        "```",
        "",
        "### 消融预答 (D17 黄牌)",
        "词典规则消融变体与 canonical 相关 0.998–0.999 (主仓 audit MATH-1 在案), 完整梯子经 pair 表可复现。",
        "",
        "## 逐年上游语料覆盖表 (D9; 计数 0 可判真零 vs 无语料假零)",
        "| 年 | 输入报道行数 |", "|---|---|",
    ]
    for y in range(year_min, year_max + 1):
        lines.append(f"| {y} | {int(yearly.get(y, 0))} |")
    lines += [
        "",
        f"2025 覆盖取决于上游语料截止; 整年 0 属预期而非缺失。",
        "",
        "## 缩写名↔全名对照表 (D16)",
        "| 全名基名 | dta 短名 |", "|---|---|",
    ]
    lines += [f"| {e['basename']} | {e['short_name']} |" for e in emit
              if e["short_name"] != e["basename"]]
    lines += [
        "",
        "## Stata merge 示例 (D9)",
        "```stata",
        "use company_bank_cooc_panel.dta, clear",
        "merge 1:1 company_listed_name year using firm_financials.dta",
        "keep if year<=2024 & year>=ipo_year   // 2025 无语料假零 + 上市样本裁剪 (推荐默认动作)",
        "xtset, clear",
        "```",
        "",
        "## 匹配精度分层抽样 (WP3 R3-2, dev 一轮 2026-07-06; 生产机重跑后再一轮)",
        "variant 长度 × k^c 双维分层抽 86 个命中逐条人工判读: **≤2 字层 precision ≈0.71 (n=14)** "
        "(假阳性例: '凯龙'→红星美凯龙家居卖场) / **3 字层 ≈0.76 (n=29)** ('大智慧'→普通词语、"
        "'祁连山'→自然保护区、'陆家嘴'→地名用法) / **≥4 字层 ≈0.92 (n=36)** ('上海科技'→'上海科技型"
        "企业'、'二三四五'→'一二三四五'口号、'华联超市'→北京华联为残余通道)。短名假阳性通道实证 → "
        "`n_docs_longhit` (≥4 字 variant 命中计数臂) 是唯一可执行稳健工具; 高 k^c 名录稿层多为真命中"
        "弱关联 (与假阳性是两个不同通道)。",
        "",
        "## 已知局限 (§7 摘要)",
        "短简称误匹配 (≤2 字 variant 10 个/3 字 1,750 个; 稳健工具 = pair 表 n_docs_longhit) / "
        "名录稿灌水 (k^c 分位诊断入日志, 刻意不设剔除阈值) / variant 子串双计 (保守口径) / "
        "拉丁字母大小写敏感 / full 轨联播稿权重放大 / D4b 残余第三方假阳性 / 企业侧覆盖自选择 / "
        "variant 集 2026 快照 / 21_full 行宇宙 = stage 13 过滤后 / 加权测度银行覆盖缺口 "
        "(cooc_wt_base 诊断) / shift-share 推断须 exposure-robust SE (AKM 2019) / "
        "LLM 前瞻偏差 (词典/BERT 系弱通道梯度对照)。",
        "",
        "三轨/嵌入双轨/LLM 三家/词典梯子/BERT 三模型/加权-等权两臂: 互为稳健、不分主次, "
        "各自 just-identified 并排, 禁混同一 over-identified Hansen J。",
        "",
        "pair 长表 `n_docs_strict` 语义注: 仅 ss 轨剔 `ss_is_fallback` 报道; full/ctx 轨恒等",
        "`n_docs` 填充 (fallback 概念仅 ss 轨有, 勿按 ctx_is_fallback 重算)。",
        "",
    ]
    text = "\n".join(lines)
    # (R3 P1-2) 保留 WP5 七权章区块 (section-replace 标记), 整文件重写不清掉既有章
    if path.exists():
        old = path.read_text(encoding="utf-8")
        b, e = "<!-- BEGIN 七替代权面板章 (WP5 生成, 勿手改) -->", "<!-- END 七替代权面板章 -->"
        if b in old and e in old:
            block = old.split(b)[1].split(e)[0]
            text = text.rstrip("\n") + "\n\n" + b + block + e + "\n"
    path.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------- gates (WP3 内联, fail-loud)
def run_gates(panel: pd.DataFrame, pair: pd.DataFrame, registry: dict,
              n_rows_expect: int) -> None:
    assert len(panel) == n_rows_expect, f"行数 {len(panel)} ≠ {n_rows_expect}"
    for t in TRACKS:
        assert (panel[f"n_cooc_{t}_v"] <= panel[f"n_cooc_{t}"]).all()
        nb, nc = panel[f"n_banks_{t}"], panel[f"n_cooc_{t}"]
        assert ((nb >= 1) == (nc >= 1)).all()
        hhi = panel[f"cooc_hhi_{t}"].dropna()
        assert ((hhi > 0) & (hhi <= 1)).all(), f"HHI 值域违例 {t}"
        sub = panel.loc[panel[f"cooc_hhi_{t}"].notna()]
        assert (sub[f"cooc_hhi_{t}"] >= 1 / sub[f"n_banks_{t}"] - 1e-12).all()
        single = sub[sub[f"n_banks_{t}"] == 1]
        assert (single[f"cooc_hhi_{t}"] == 1.0).all(), "单银行格 HHI 须无容差 ==1.0"
        wb = panel[f"cooc_wt_base_{t}"].dropna()
        assert ((wb >= 0) & (wb <= 1)).all()
    assert (panel["n_cooc_ss_strict"] <= panel["n_cooc_ss"]).all()
    # dev 严格分化断言 (v19 反转): Σ n_cooc_*_v < Σ n_cooc_* 全轨
    for t in TRACKS:
        assert panel[f"n_cooc_{t}_v"].sum() < panel[f"n_cooc_{t}"].sum(), \
            f"{t} 轨 verified 未分化 (21_full 应含 unverified 行)"
    # pair 恒等式 (v22): Σ_b n_docs_frac == n_cooc 全格三轨 isclose (禁精确相等)
    for t in TRACKS:
        p = pair[pair["track"] == t]
        s = p.groupby(["company", "year"])["n_docs_frac"].sum()
        s_v = p.groupby(["company", "year"])["n_docs_frac_v"].sum()
        s.index.names = s_v.index.names = ["company_listed_name", "year"]
        lhs = panel.set_index(["company_listed_name", "year"])[f"n_cooc_{t}"]
        lhs_v = panel.set_index(["company_listed_name", "year"])[f"n_cooc_{t}_v"]
        joined = pd.DataFrame({"frac": s}).join(lhs.rename("n"), how="left")
        assert joined["n"].notna().all(), f"pair 表 (company,year) 落在面板骨架外 ({t})"
        assert np.isclose(joined["frac"], joined["n"]).all(), f"Σ n_docs_frac ≠ n_cooc ({t})"
        joined_v = pd.DataFrame({"frac": s_v}).join(lhs_v.rename("n"), how="left")
        assert np.isclose(joined_v["frac"], joined_v["n"]).all(), f"Σ n_docs_frac_v ≠ n_cooc_v ({t})"
        assert (p["n_docs_longhit"] <= p["n_docs"]).all()
    # 单银行公司×年格 cw == ce (N=1 短路后精确; 双方同 NaN 亦过, v20 容错) — 抽 registry 前 20 emit 列
    emit_entries = [e for e in registry["entries"] if e["emit_panel"]][:20]
    single_mask = panel["n_banks_full"] == 1
    for e in emit_entries:
        if "full" not in e["emit_tracks"]:
            continue
        cwc, cec = f"cw_{e['basename']}_full", f"ce_{e['basename']}_full"
        if cwc in panel.columns:
            a, b = panel.loc[single_mask, cwc], panel.loc[single_mask, cec]
            ok = (a.isna() & b.isna()) | np.isclose(a, b, equal_nan=True)
            assert ok.all(), f"单银行格 cw≠ce: {cwc}"
    # 值域 gate: registry range_gate 字段展开 (禁列名圈定)
    for e in registry["entries"]:
        if not e["emit_panel"] or e["range_gate"] == "none":
            continue
        lo, hi = (-1.0, 1.0) if e["range_gate"] == "tone" else (0.0, 1.0)
        for t in e["emit_tracks"]:
            for arm in ("cw", "ce"):
                col = f"{arm}_{e['basename']}_{t}"
                if col not in panel.columns:
                    continue
                v = panel[col].dropna()
                if len(v):
                    assert (v >= lo - 1e-9).all() and (v <= hi + 1e-9).all(), f"值域违例 {col}"
    # 缺失语义互斥: n_cooc_t==0 ⇒ 该轨全部 cw/ce 缺失
    cw_cols_by_track = {t: [c for c in panel.columns
                            if (c.startswith("cw_") or c.startswith("ce_")) and c.endswith("_" + t)
                            and not c.startswith("cooc_")] for t in TRACKS}
    for t in TRACKS:
        zero = panel[f"n_cooc_{t}"] == 0
        if cw_cols_by_track[t]:
            assert panel.loc[zero, cw_cols_by_track[t]].isna().all().all(), \
                f"零共现格出现非缺失加权值 ({t})"
    log("WP3 内联 gate 全过")


# ---------------------------------------------------------------- dev 双法等价断言 (WP1-5, 抽样列)
def _sparse_equivalence_check(weights: pd.DataFrame, measures: pd.DataFrame, registry: dict,
                              weighted: pd.DataFrame, n_sample: int = 60) -> None:
    """稀疏矩阵法 cw = (W@X.fillna(0)) / (W@notna(X)) 对分块 join 法抽样对照 (isclose)。"""
    from scipy import sparse
    emit = [e for e in registry["entries"] if e["emit_panel"]]
    Wt = weights[weights["track"] == "full"] if "track" in weights.columns else weights
    Wt = Wt.dropna(subset=["w"])
    if Wt.empty:
        return
    comps = pd.MultiIndex.from_frame(Wt[["company", "year"]]).unique()
    banks = pd.MultiIndex.from_frame(Wt[["bank", "year"]]).unique()
    ci = {k: i for i, k in enumerate(comps)}
    bi = {k: i for i, k in enumerate(banks)}
    rows = [ci[(c, y)] for c, y in zip(Wt["company"], Wt["year"])]
    cols = [bi[(b, y)] for b, y in zip(Wt["bank"], Wt["year"])]
    W = sparse.csr_matrix((Wt["w"].astype(float), (rows, cols)), shape=(len(comps), len(banks)))
    checked = 0
    for e in emit:
        if checked >= n_sample or "full" not in e["emit_tracks"]:
            continue
        mcol = _measure_col_id(e, "full")
        if not mcol or mcol not in measures.columns:
            continue
        x = measures[mcol].reindex(banks).to_numpy(dtype=float)
        mask = ~np.isnan(x)
        num = W @ np.where(mask, x, 0.0)   # 禁直写 W@X (无 skipna 语义, v18)
        den = W @ mask.astype(float)
        cw_sp = pd.Series(np.divide(num, den, out=np.full_like(num, np.nan), where=den > 0),
                          index=comps)
        col = f"cw_{e['basename']}_full"
        if col not in weighted.columns:
            continue
        cw_join = weighted[col].reindex(comps)
        both = cw_sp.notna() & cw_join.notna()
        assert (cw_sp.isna() == cw_join.isna()).all(), f"双法缺失掩码分叉: {col}"
        assert np.isclose(cw_sp[both], cw_join[both]).all(), f"双法数值分叉: {col}"
        checked += 1
    log(f"dev 双法等价断言过 ({checked} 列抽样, isclose)")


# ---------------------------------------------------------------- main
def main(argv=None) -> int:
    dp = default_paths()
    ap = argparse.ArgumentParser()
    ap.add_argument("--input"); ap.add_argument("--panel"); ap.add_argument("--alignment")
    ap.add_argument("--benefit"); ap.add_argument("--controls")
    ap.add_argument("--registry", default=str(CONFIG / "company_bank_cooc_registry.yaml"))
    ap.add_argument("--output", default=str(DATA / "company_bank_cooc_panel.dta"))
    ap.add_argument("--year-min", type=int, default=2007)
    ap.add_argument("--year-max", type=int, default=2025)
    args = ap.parse_args(argv)
    if args.year_min > args.year_max:
        raise SystemExit(2)

    def resolve(name: str, required: bool = False) -> Path | None:
        given = getattr(args, name)
        if given:  # 显式传参: 缺失 → SystemExit (v18)
            path = Path(given)
            if not path.exists():
                raise SystemExit(f"显式传参 --{name} 路径不存在: {path}")
            return path
        path = dp[name]
        if not path.exists():
            if required:
                raise SystemExit(f"必需上游缺失: {path}")
            log(f"默认路径缺失 {path.name} → 对应族全缺失列", warn=True)
            return None
        return path

    registry = yaml.safe_load(Path(args.registry).read_text(encoding="utf-8"))
    # 启动自校验 (D10): registry 基名数 + 40 面板实读列集 ⊆ 已判定全集
    if registry["meta"]["n_entries"] < 600:
        raise SystemExit("registry 基名数 < 600 — 疑损坏")
    p_input = resolve("input", required=True)
    p_panel = resolve("panel", required=True)
    p_align, p_benefit, p_controls = resolve("alignment"), resolve("benefit"), resolve("controls")

    import pyarrow.parquet as pq
    cols40_live = {n for n in pq.ParquetFile(p_panel).schema_arrow.names if n != "__index_level_0__"}
    judged = {c for e in registry["entries"] if e["source"] == "40"
              for c in e["col_by_track"].values() if c}
    judged |= {k for k in registry["excluded"] if ":" not in k}
    drift = cols40_live - judged
    if drift:
        raise SystemExit(f"40 面板出现 registry 未判定新列 (WP0 后漂移): {sorted(drift)[:10]}")

    A, variant_owner, bank_canonical, bank_substr, own_map, bank_company_set, company_names = \
        load_name_assets(registry)
    input21 = load_input21(p_input, bank_canonical)

    hits = scan_hits(input21, A, bank_substr, own_map)
    if hits.empty:
        raise SystemExit(1)  # 全表零命中不可能 (5,528 家对生产语料)
    year_map, hits = build_year_map(hits)
    # 合法域内、窗外 → INFO 裁剪 (第二层)
    n_outwin = int(((hits["year"] < args.year_min) | (hits["year"] > args.year_max)).sum())
    if n_outwin:
        log(f"INFO: 窗口外年份行裁剪 {n_outwin} (属预期)")

    pair = build_pair_table(hits, args.year_min, args.year_max)
    panel = build_counts(hits, company_names, args.year_min, args.year_max, bank_company_set)
    panel = add_hhi(panel, pair)

    panel40 = pd.read_parquet(p_panel)
    align = pd.read_parquet(p_align) if p_align else None
    benefit = pd.read_parquet(p_benefit) if p_benefit else None
    controls = pd.read_parquet(p_controls) if p_controls else None
    measures = build_measure_library(input21, panel40, align, benefit, controls, registry)

    wt_base = compute_wt_base(pair, measures)
    panel = panel.merge(wt_base, how="left", left_on=["company_listed_name", "year"], right_index=True)

    # 媒体权重长表 (canonical n_docs, 逐轨)
    weights = pair.rename(columns={"n_docs": "w"})[["company", "bank", "year", "track", "w"]]
    weighted = compute_weighted_panel(weights, measures, registry)
    # 缺源列 WARNING (v20: 全 NaN 列诊断)
    n_all_nan = int(weighted.isna().all().sum()) if len(weighted.columns) else 0
    if n_all_nan:
        log(f"{n_all_nan} 个加权列全 NaN (缺源列/dev 数据态)", warn=True)
    panel = panel.merge(weighted, how="left", left_on=["company_listed_name", "year"], right_index=True)

    # 列序: 固定 19 列 + 加权列 (registry SSOT 序, weighted 已排)
    ordered = FIXED_ORDER + [c for c in panel.columns if c not in FIXED_ORDER]
    panel = panel[ordered]

    n_expect = len(company_names) * (args.year_max - args.year_min + 1)
    run_gates(panel, pair, registry, n_expect)
    _sparse_equivalence_check(weights, measures, registry, weighted)

    out_dta = Path(args.output)
    # pair 长表落盘 (含 registry 哈希 + 输入指纹 metadata, v33 J2 ②)
    import pyarrow as pa
    import pyarrow.parquet as pqw
    tbl = pa.Table.from_pandas(pair, preserve_index=False)
    fingerprint = hashlib.sha256(f"{p_input.stat().st_size}|{len(input21)}".encode()).hexdigest()
    tbl = tbl.replace_schema_metadata({**(tbl.schema.metadata or {}),
                                       b"registry_sha256": registry["meta"]["registry_sha256"].encode(),
                                       b"input_fingerprint": fingerprint.encode()})
    pqw.write_table(tbl, DATA / "_company_bank_cooc_pairs.parquet")

    write_outputs(panel, registry, out_dta, fixed_labels=FIXED_LABELS)
    write_codebook(out_dta.parent / "company_bank_cooc_panel_codebook.md", registry, panel,
                   input21, args.year_min, args.year_max)
    # k^c 分位诊断 (§7, 无剔除阈值)
    for t in TRACKS:
        ht = hits[hits["track"] == t].drop_duplicates(["company", "docid"])
        kc = ht.groupby("docid")["company"].nunique()
        if len(kc):
            q = kc.quantile([0.5, 0.9, 0.99]).tolist()
            log(f"k^c {t}: p50={q[0]:.0f} p90={q[1]:.0f} p99={q[2]:.1f} max={kc.max()}"
                f" | top docid: {kc.nlargest(3).to_dict()}")
    log(f"完成: {len(panel)} 行 × {len(panel.columns)} 列 → {out_dta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
