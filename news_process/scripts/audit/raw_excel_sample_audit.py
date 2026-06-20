"""raw_excel_sample_audit.py — 统计 data_excel 下全部原始 Excel 表格的样本数据情况.

只读审计 (READ-ONLY): 递归扫描 ``news_process/data_excel/**/*.xlsx`` (含 back/),
逐文件用 calamine 引擎全量读取, 并行聚合下列原始 (未过滤) 样本统计:

- 总行数 / 每文件行数 / 按来源 (wisers vs TIT_K) 拆分
- 年份分布 (按 ``日期``) + 年×来源
- 媒体类型分布 (``媒体类型(中文)``; pipeline 仅保留"报纸")
- 媒体 (报刊) 分布 + 唯一媒体数 (top-N)
- 地域分布 (``国家地区/省份``; pipeline 仅保留中国大陆) + 唯一省份数
- 关键字段缺失 (``标题`` / ``内容`` / ``媒体(中文)`` / ``日期``)
- 内容字符长度分布 + ``字数`` (Wisers 原始词数) 分布
- 重复: 按 ``MD5 Docid`` (两来源通用 dedup 键) 的文件内重复 + 全局唯一文档数

⚠ 本脚本绝不写 data_excel, 绝不触发 stage 00 预处理; 仅向 OUT_DIR 写统计产物。

用法:
    F:/Anaconda3/python.exe news_process/scripts/audit/raw_excel_sample_audit.py            # 全量 184 文件
    F:/Anaconda3/python.exe news_process/scripts/audit/raw_excel_sample_audit.py --limit 3  # 仅前 3 文件 (冒烟)
    F:/Anaconda3/python.exe news_process/scripts/audit/raw_excel_sample_audit.py --files a.xlsx b.xlsx
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import time
import warnings
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))             # news_process/scripts/audit
NEWS_PROCESS_ROOT = os.path.dirname(os.path.dirname(HERE))    # news_process/
DATA_EXCEL = os.path.join(NEWS_PROCESS_ROOT, "data_excel")
OUT_DIR = os.path.join(HERE, "_rawstats_20260620")

SHEET = "Sheet1"
KEY_NA_COLS = ["标题", "内容", "媒体(中文)", "日期"]
# 读取列 (排除 翻译内容/翻译标题 等冗余大列以省 pandas 内存; calamine 仍全量解析)
USECOLS = [
    "docid", "MD5 Docid", "媒体(中文)", "媒体类型(中文)", "日期",
    "标题", "内容", "国家地区/省份", "城市", "字数",
]

# 内容字符长度直方图分箱 (左闭右开, 末箱到 inf)
LEN_BINS = [0, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000, 20000, 10**12]
# 字数 (Wisers 词数) 直方图分箱
WC_BINS = [0, 50, 100, 200, 300, 500, 1000, 2000, 5000, 10000, 10**12]

# pipeline 内容长度过滤区间 (汉字数; 此处用总字符近似, 仅作参考)
CONTENT_MIN, CONTENT_MAX = 100, 10000


def _source_of(fname: str) -> str:
    base = os.path.basename(fname)
    if base.startswith("wisers"):
        return "wisers"
    if base.startswith("TIT_K"):
        return "TIT_K"
    return "other"


def process_file(path: str) -> dict:
    """读取并统计单个 xlsx, 返回紧凑聚合 dict (在子进程中运行)."""
    res: dict = {"file": os.path.basename(path), "source": _source_of(path), "ok": False}
    t0 = time.time()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # 先读全部列名以做 usecols 交集 (防个别文件列缺失)
            df = pd.read_excel(path, sheet_name=SHEET, engine="calamine")
        cols = list(df.columns)
        res["n_rows"] = int(len(df))
        res["raw_ncols"] = len(cols)

        # ---- 缺失值 (空字符串/NaN 都算缺失) ----
        nulls = {}
        for c in KEY_NA_COLS:
            if c in df.columns:
                s = df[c]
                isnull = s.isna() | (s.astype(str).str.strip() == "")
                nulls[c] = int(isnull.sum())
            else:
                nulls[c] = -1  # 列不存在
        res["nulls"] = nulls

        # ---- 年份分布 (日期 → 前4位) ----
        ycnt = Counter()
        bad_date = 0
        if "日期" in df.columns:
            yr = df["日期"].astype(str).str.strip().str[:4]
            ynum = pd.to_numeric(yr, errors="coerce")
            valid = ynum.between(1990, 2035)
            bad_date = int((~valid).sum())
            for y, c in ynum[valid].astype(int).value_counts().items():
                ycnt[int(y)] += int(c)
            # 日期范围
            dts = pd.to_datetime(df["日期"], errors="coerce")
            res["date_min"] = None if dts.notna().sum() == 0 else str(dts.min().date())
            res["date_max"] = None if dts.notna().sum() == 0 else str(dts.max().date())
        res["year_counts"] = dict(ycnt)
        res["bad_date"] = bad_date

        # ---- 媒体类型 / 媒体 / 地域 ----
        def vc(col):
            if col not in df.columns:
                return {}
            s = df[col].astype(str).str.strip().replace({"": "(空)", "nan": "(空)", "None": "(空)"})
            return {str(k): int(v) for k, v in s.value_counts().items()}

        res["mediatype_counts"] = vc("媒体类型(中文)")
        res["media_counts"] = vc("媒体(中文)")
        res["region_counts"] = vc("国家地区/省份")

        # ---- 内容字符长度 ----
        if "内容" in df.columns:
            clen = df["内容"].astype(str).str.len().to_numpy()
            res["len_hist"] = np.histogram(clen, bins=LEN_BINS)[0].tolist()
            res["len_sum"] = int(clen.sum())
            res["len_min"] = int(clen.min()) if len(clen) else 0
            res["len_max"] = int(clen.max()) if len(clen) else 0
            res["len_in_pipeline_range"] = int(((clen >= CONTENT_MIN) & (clen <= CONTENT_MAX)).sum())
        # ---- 字数 (Wisers) ----
        if "字数" in df.columns:
            wc = pd.to_numeric(df["字数"], errors="coerce")
            res["wc_nonnull"] = int(wc.notna().sum())
            res["wc_sum"] = float(np.nansum(wc.to_numpy()))
            res["wc_hist"] = np.histogram(wc.dropna().to_numpy(), bins=WC_BINS)[0].tolist()

        # ---- 重复键 (MD5 Docid, 回退 docid) ----
        if "MD5 Docid" in df.columns:
            key = df["MD5 Docid"].astype(str).str.strip()
            empty = (key == "") | (key.str.lower() == "nan")
            if "docid" in df.columns and empty.any():
                key = key.where(~empty, df["docid"].astype(str))
        elif "docid" in df.columns:
            key = df["docid"].astype(str)
        else:
            key = pd.Series([], dtype=str)
        h = pd.util.hash_pandas_object(key, index=False).to_numpy(dtype=np.uint64)
        uniq = np.unique(h)
        res["n_key_total"] = int(len(h))
        res["n_key_unique_infile"] = int(len(uniq))
        # 存盘以便主进程做全局并集 (避免 pickle 巨数组占内存; 落 .npy)
        npy = os.path.join(OUT_DIR, "_keyhash", res["file"] + ".npy")
        os.makedirs(os.path.dirname(npy), exist_ok=True)
        np.save(npy, uniq)
        res["keyhash_npy"] = npy

        res["ok"] = True
        res["secs"] = round(time.time() - t0, 1)
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
        res["secs"] = round(time.time() - t0, 1)
    return res


def merge_counter(dst: Counter, src: dict):
    for k, v in src.items():
        dst[k] += v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 个文件 (0=全部)")
    ap.add_argument("--files", nargs="*", default=None, help="指定文件 (basename 或路径)")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    if args.files:
        files = []
        for f in args.files:
            files.append(f if os.path.isabs(f) else os.path.join(DATA_EXCEL, "back", os.path.basename(f))
                         if not os.path.exists(f) else f)
    else:
        files = sorted(glob.glob(os.path.join(DATA_EXCEL, "**", "*.xlsx"), recursive=True))
    # 按 basename 去重: 递归 glob 会把同一源文件的顶层副本与 back/ 归档副本各扫一次
    # (实测 wisers_20250702070833_1.xlsx 在两处字节级相同), 不去重会把该源行数双计。
    _seen, _deduped, _dropped = set(), [], []
    for _f in files:
        _b = os.path.basename(_f)
        if _b in _seen:
            _dropped.append(_f)
        else:
            _seen.add(_b)
            _deduped.append(_f)
    if _dropped:
        print(f"[raw-audit] 跨目录同名副本去重: 跳过 {len(_dropped)} 个 "
              f"({', '.join(os.path.basename(d) for d in _dropped)})", flush=True)
    files = _deduped
    if args.limit:
        files = files[: args.limit]

    print(f"[raw-audit] files={len(files)} workers={args.workers} out={OUT_DIR}", flush=True)
    t0 = time.time()

    results = []
    with ProcessPoolExecutor(max_workers=args.workers, max_tasks_per_child=1) as ex:
        futs = {ex.submit(process_file, f): f for f in files}
        done = 0
        for fut in as_completed(futs):
            r = fut.result()
            results.append(r)
            done += 1
            tag = "OK " if r.get("ok") else "ERR"
            print(f"  [{done:>3}/{len(files)}] {tag} {r['file']:<40} "
                  f"rows={r.get('n_rows','?'):>8} {r.get('secs','?')}s "
                  f"{r.get('error','')}", flush=True)

    elapsed = time.time() - t0
    print(f"[raw-audit] read done in {elapsed/60:.1f} min", flush=True)

    # ---- 聚合 ----
    ok = [r for r in results if r.get("ok")]
    err = [r for r in results if not r.get("ok")]
    by_source = Counter()
    rows_by_source = Counter()
    year_counts = Counter()
    year_by_source = {}             # source -> Counter(year)
    mediatype = Counter()
    media = Counter()
    region = Counter()
    nulls = Counter()
    len_hist = np.zeros(len(LEN_BINS) - 1, dtype=np.int64)
    wc_hist = np.zeros(len(WC_BINS) - 1, dtype=np.int64)
    total_rows = 0
    total_len = 0
    total_in_range = 0
    total_key = 0
    total_uniq_infile = 0
    date_min, date_max = "9999", "0000"

    for r in ok:
        s = r["source"]
        by_source[s] += 1
        rows_by_source[s] += r["n_rows"]
        total_rows += r["n_rows"]
        merge_counter(year_counts, r.get("year_counts", {}))
        yb = year_by_source.setdefault(s, Counter())
        merge_counter(yb, r.get("year_counts", {}))
        merge_counter(mediatype, r.get("mediatype_counts", {}))
        merge_counter(media, r.get("media_counts", {}))
        merge_counter(region, r.get("region_counts", {}))
        for k, v in r.get("nulls", {}).items():
            if v >= 0:
                nulls[k] += v
        if "len_hist" in r:
            len_hist += np.array(r["len_hist"], dtype=np.int64)
            total_len += r["len_sum"]
            total_in_range += r["len_in_pipeline_range"]
        if "wc_hist" in r:
            wc_hist += np.array(r["wc_hist"], dtype=np.int64)
        total_key += r.get("n_key_total", 0)
        total_uniq_infile += r.get("n_key_unique_infile", 0)
        if r.get("date_min") and r["date_min"] < date_min:
            date_min = r["date_min"]
        if r.get("date_max") and r["date_max"] > date_max:
            date_max = r["date_max"]

    # 全局唯一文档 (并所有 per-file 唯一 keyhash)
    all_hashes = []
    for r in ok:
        p = r.get("keyhash_npy")
        if p and os.path.exists(p):
            all_hashes.append(np.load(p))
    if all_hashes:
        global_uniq = int(len(np.unique(np.concatenate(all_hashes))))
    else:
        global_uniq = 0

    summary = {
        "n_files": len(results),
        "n_ok": len(ok),
        "n_err": len(err),
        "errors": [{"file": r["file"], "error": r.get("error")} for r in err],
        "total_rows": total_rows,
        "rows_by_source": dict(rows_by_source),
        "files_by_source": dict(by_source),
        "date_min": None if date_min == "9999" else date_min,
        "date_max": None if date_max == "0000" else date_max,
        "year_counts": dict(sorted(year_counts.items())),
        "year_by_source": {s: dict(sorted(c.items())) for s, c in year_by_source.items()},
        "mediatype_counts": dict(mediatype.most_common()),
        "n_unique_media": len(media),
        "media_top50": dict(media.most_common(50)),
        "n_unique_region": len(region),
        "region_counts": dict(region.most_common()),
        "nulls": dict(nulls),
        "content_len": {
            "bins": LEN_BINS,
            "hist": len_hist.tolist(),
            "total_chars": total_len,
            "mean_chars": round(total_len / total_rows, 1) if total_rows else 0,
            "n_in_pipeline_range_100_10000_approx": total_in_range,
        },
        "wordcount_zishu": {"bins": WC_BINS, "hist": wc_hist.tolist()},
        "dedup": {
            "total_key_rows": total_key,
            "sum_unique_within_file": total_uniq_infile,
            "global_unique_docs": global_uniq,
            "global_dup_rows": total_rows - global_uniq,
            "global_dup_rate": round(1 - global_uniq / total_rows, 4) if total_rows else 0,
        },
        "elapsed_min": round(elapsed / 60, 2),
    }

    # 落盘: JSON summary + per-file CSV
    with open(os.path.join(OUT_DIR, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    perfile_rows = []
    for r in sorted(results, key=lambda x: x["file"]):
        perfile_rows.append({
            "file": r["file"], "source": r["source"], "ok": r.get("ok"),
            "n_rows": r.get("n_rows"), "raw_ncols": r.get("raw_ncols"),
            "date_min": r.get("date_min"), "date_max": r.get("date_max"),
            "null_title": r.get("nulls", {}).get("标题"),
            "null_content": r.get("nulls", {}).get("内容"),
            "null_media": r.get("nulls", {}).get("媒体(中文)"),
            "null_date": r.get("nulls", {}).get("日期"),
            "n_key_total": r.get("n_key_total"),
            "n_key_unique_infile": r.get("n_key_unique_infile"),
            "len_in_range": r.get("len_in_pipeline_range"),
            "secs": r.get("secs"), "error": r.get("error"),
        })
    pd.DataFrame(perfile_rows).to_csv(
        os.path.join(OUT_DIR, "per_file.csv"), index=False, encoding="utf-8-sig")

    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print(f"\n[raw-audit] wrote {OUT_DIR}/summary.json + per_file.csv", flush=True)


if __name__ == "__main__":
    main()
