"""news_process.pipeline.preprocess.raw_census — 原始 Excel 全量样本普查 (只读, 写入预处理日志).

动机
----
预处理阶段 (00_preprocessing) 的 `logger` 在 ``_constants.py`` 中以 ``console_only=True``
配置 (为防 ProcessPoolExecutor worker 并发写同一日志文件), 故 stage 00 自身**不落**
``logs/00_preprocessing.log`` 文件。结果: **过滤前的原始语料体量与构成从未被单独记录**。

本模块补这一空白: 对 ``paths.raw_data_dir`` (递归含 ``back/``) 下**全部**原始 Excel
做一次**只读**普查 (绝不写 parquet / 绝不触发 stage 00 的清洗·去重·覆盖), 把
"最初原始所有 Excel 表格中的样本数据情况" 写进 ``logs/00_preprocessing.log``:

  总行数 / 来源拆分 / 年份分布 (年×来源) / 媒体类型分布 / 地域分布 (大陆保留 vs 非大陆剔除) /
  媒体(报刊) Top / 关键字段缺失 / 正文长度分布 / 精确去重 (MD5 Docid) / 原始→可用样本漏斗 /
  逐文件明细 (含来源目录 relpath)。

⚠ 铁律: 只读。不改 data_excel, 不写任何 parquet, 不调用 stage 00 的 main()。

口径与去重 (2026-06-20 顶刊多智能体评审后修正):
- **跨目录同名副本去重**: 递归 glob 会把同一源文件的顶层副本与 ``back/`` 归档副本各扫一次
  (实测 wisers_20250702070833_1.xlsx 在两处字节级相同), 若不去重会把该源行数双计。故按
  **basename 去重 (每个源只计一次)**, 并 loud WARNING 列出被跳过的副本。
- **stage 00 实际处理范围**: 本普查为**递归全量** (含 back/); 而 stage 00 真正 ingest 走
  **非递归** glob ``data_excel/*.xlsx``。两者文件集可不同 (本机归档布局下尤甚), 日志显式两边都报。

用法
----
  # 随 stage 00 运行自动调用 (runner.main); 或独立重算 + 落普查产物:
  python -m news_process.pipeline.preprocess.raw_census --recompute --workers 10 \
      --save-artifacts scripts/audit/_rawstats_20260620
  # 用已算好的产物快速渲染日志 (不重读 44GB):
  python -m news_process.pipeline.preprocess.raw_census \
      --from-summary scripts/audit/_rawstats_20260620/summary.json \
      --from-perfile scripts/audit/_rawstats_20260620/per_file.csv
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
import time
import warnings
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import pandas as pd

# 让 ``python -m`` 与直跑都能解析 ``news_process`` 包。
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging

STAGE_NAME = "00_preprocessing"
SHEET = "Sheet1"
KEY_NA_COLS = ["标题", "内容", "媒体(中文)", "日期"]
LEN_BINS = [0, 50, 100, 200, 300, 500, 1000, 2000, 3000, 5000, 10000, 20000, 10**12]
CONTENT_MIN, CONTENT_MAX = 100, 10000


def _source_of(fname: str) -> str:
    base = os.path.basename(fname)
    if base.startswith("wisers"):
        return "wisers"
    if base.startswith("TIT_K"):
        return "TIT_K"
    return "other"


def dedup_files_by_basename(files):
    """按 basename 去重 (跨目录同名副本只保留排序首个), 返回 (deduped, dropped).

    递归 glob 会把同一源文件的顶层副本与 ``back/`` 归档副本各计一次; 二者 basename 相同
    (实测字节级一致)。去重避免行数双计。返回被丢弃的副本路径以便 loud 披露。
    """
    seen, deduped, dropped = set(), [], []
    for f in sorted(files):
        b = os.path.basename(f)
        if b in seen:
            dropped.append(f)
        else:
            seen.add(b)
            deduped.append(f)
    return deduped, dropped


# ============================================================================
# 1. 单文件普查 worker (只读)
# ============================================================================

def _census_worker(path: str) -> dict:
    """读取并统计单个原始 xlsx 的过滤前样本情况 (子进程入口, 只读)."""
    res: dict = {"file": os.path.basename(path), "path": path,
                 "source": _source_of(path), "ok": False}
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            df = pd.read_excel(path, sheet_name=SHEET, engine="calamine")
        res["n_rows"] = int(len(df))
        res["raw_ncols"] = len(df.columns)

        nulls = {}
        for c in KEY_NA_COLS:
            if c in df.columns:
                s = df[c]
                nulls[c] = int((s.isna() | (s.astype(str).str.strip() == "")).sum())
            else:
                nulls[c] = -1
        res["nulls"] = nulls

        # 年份 + 日期范围 (统一 validity: 同一个 between(1990,2035) 掩码; 日期范围用
        # ISO 字符串 min/max == 年代序, 避免 pd.to_datetime 与 str[:4] 口径不一致)。
        ycnt = Counter()
        if "日期" in df.columns:
            s = df["日期"].astype(str).str.strip()
            ynum = pd.to_numeric(s.str[:4], errors="coerce")
            valid = ynum.between(1990, 2035)
            for y, c in ynum[valid].astype(int).value_counts().items():
                ycnt[int(y)] += int(c)
            datestr = s[valid].str[:10]
            res["date_min"] = None if datestr.empty else str(datestr.min())
            res["date_max"] = None if datestr.empty else str(datestr.max())
        res["year_counts"] = dict(ycnt)

        def vc(col):
            if col not in df.columns:
                return {}
            s = df[col].astype(str).str.strip().replace(
                {"": "(空)", "nan": "(空)", "None": "(空)"})
            return {str(k): int(v) for k, v in s.value_counts().items()}

        res["mediatype_counts"] = vc("媒体类型(中文)")
        res["media_counts"] = vc("媒体(中文)")
        res["region_counts"] = vc("国家地区/省份")

        if "内容" in df.columns:
            clen = df["内容"].astype(str).str.len().to_numpy()
            res["len_hist"] = np.histogram(clen, bins=LEN_BINS)[0].tolist()
            res["len_sum"] = int(clen.sum())
            res["len_in_range"] = int(((clen >= CONTENT_MIN) & (clen <= CONTENT_MAX)).sum())

        # 去重键: 优先 MD5 Docid, 空则回退 docid; 无任一列则空 (该文件不计入去重)
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
        res["_uniq_hashes"] = np.unique(h)
        res["n_key_total"] = int(len(h))
        res["n_key_unique_infile"] = int(len(res["_uniq_hashes"]))
        res["ok"] = True
    except Exception as e:  # noqa: BLE001
        res["error"] = f"{type(e).__name__}: {e}"
    return res


def compute_raw_census(files, workers: int = 10, raw_data_dir: str | None = None):
    """并行只读普查 (调用方须先做 basename 去重)。返回 (summary, perfile)."""
    t0 = time.time()
    results = []
    if workers <= 1:
        # 串行路径: 单文件/测试场景, 免去 ProcessPoolExecutor spawn 开销与不确定性
        for f in files:
            results.append(_census_worker(f))
    else:
        with ProcessPoolExecutor(max_workers=workers, max_tasks_per_child=1) as ex:
            futs = {ex.submit(_census_worker, f): f for f in files}
            for fut in as_completed(futs):
                results.append(fut.result())

    ok = [r for r in results if r.get("ok")]
    err = [r for r in results if not r.get("ok")]
    by_source, rows_by_source = Counter(), Counter()
    year_counts, year_by_source = Counter(), {}
    mediatype, media, region, nulls = Counter(), Counter(), Counter(), Counter()
    len_hist = np.zeros(len(LEN_BINS) - 1, dtype=np.int64)
    total_rows = total_len = total_in_range = total_key = total_uniq_infile = 0
    date_min, date_max = "9999", "0000"
    all_hashes = []

    for r in ok:
        s = r["source"]
        by_source[s] += 1
        rows_by_source[s] += r["n_rows"]
        total_rows += r["n_rows"]
        for k, v in r.get("year_counts", {}).items():
            year_counts[k] += v
            year_by_source.setdefault(s, Counter())[k] += v
        for d, c in [(mediatype, "mediatype_counts"), (media, "media_counts"),
                     (region, "region_counts")]:
            for k, v in r.get(c, {}).items():
                d[k] += v
        for k, v in r.get("nulls", {}).items():
            if v >= 0:
                nulls[k] += v
        if "len_hist" in r:
            len_hist += np.array(r["len_hist"], dtype=np.int64)
            total_len += r["len_sum"]
            total_in_range += r["len_in_range"]
        total_key += r.get("n_key_total", 0)
        total_uniq_infile += r.get("n_key_unique_infile", 0)
        if r.get("date_min") and r["date_min"] < date_min:
            date_min = r["date_min"]
        if r.get("date_max") and r["date_max"] > date_max:
            date_max = r["date_max"]
        if "_uniq_hashes" in r:
            all_hashes.append(r.pop("_uniq_hashes"))

    global_uniq = int(len(np.unique(np.concatenate(all_hashes)))) if all_hashes else 0
    # 去重率分母用 total_key (参与去重的行) 而非 total_rows: 若个别文件缺 key 列,
    # 其行不计入去重统计, 用 total_key 才是 keyed 行内的真实重复率。
    summary = {
        "n_files": len(results), "n_ok": len(ok), "n_err": len(err),
        "errors": [{"file": r["file"], "error": r.get("error")} for r in err],
        "total_rows": total_rows, "rows_by_source": dict(rows_by_source),
        "files_by_source": dict(by_source),
        "date_min": None if date_min == "9999" else date_min,
        "date_max": None if date_max == "0000" else date_max,
        "year_counts": {str(k): v for k, v in sorted(year_counts.items())},
        "year_by_source": {s: {str(k): v for k, v in sorted(c.items())}
                           for s, c in year_by_source.items()},
        "mediatype_counts": dict(mediatype.most_common()),
        "n_unique_media": len(media), "media_top50": dict(media.most_common(50)),
        "n_unique_region": len(region), "region_counts": dict(region.most_common()),
        "nulls": dict(nulls),
        "content_len": {"bins": LEN_BINS, "hist": len_hist.tolist(),
                        "total_chars": total_len,
                        "mean_chars": round(total_len / total_rows, 1) if total_rows else 0,
                        "n_in_pipeline_range_100_10000_approx": total_in_range},
        "dedup": {"total_key_rows": total_key, "sum_unique_within_file": total_uniq_infile,
                  "global_unique_docs": global_uniq,
                  "global_dup_rows": total_key - global_uniq,
                  "global_dup_rate": round(1 - global_uniq / total_key, 4) if total_key else 0},
        "elapsed_min": round((time.time() - t0) / 60, 2),
    }

    def _disp(r):
        if raw_data_dir and r.get("path"):
            try:
                return os.path.relpath(r["path"], raw_data_dir).replace(os.sep, "/")
            except ValueError:
                return r["file"]
        return r["file"]

    perfile = [{
        "file": _disp(r), "source": r["source"], "ok": r.get("ok"),
        "n_rows": r.get("n_rows"), "date_min": r.get("date_min"), "date_max": r.get("date_max"),
        "null_title": r.get("nulls", {}).get("标题"),
        "null_content": r.get("nulls", {}).get("内容"),
        "null_media": r.get("nulls", {}).get("媒体(中文)"),
        "null_date": r.get("nulls", {}).get("日期"),
        "len_in_range": r.get("len_in_range"), "error": r.get("error"),
    } for r in sorted(results, key=lambda x: (x["source"], _disp(x)))]
    return summary, perfile


# ============================================================================
# 2. 渲染普查到 logger
# ============================================================================

def _f(n):
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


def _pct(a, b):
    return f"{100*a/b:.2f}%" if b else "—"


def render_census_to_logger(summary: dict, perfile: list[dict], logger,
                            *, scan_root: str, data_source_note: str,
                            mainland_regions: set[str],
                            stage00_ingest_count: int | None = None,
                            dropped_dups: list[str] | None = None) -> None:
    """把普查结果以紧凑日志行写入 logger (golden-safe: 纯日志, 无产物)."""
    d, total = summary, summary["total_rows"]
    nulls = d.get("nulls", {})
    null_content = nulls.get("内容", 0)
    with_content = total - null_content
    mt = d.get("mediatype_counts", {})
    n_paper = mt.get("报纸", 0)
    cl = d.get("content_len", {})
    in_range = cl.get("n_in_pipeline_range_100_10000_approx", 0)
    dd = d.get("dedup", {})
    dropped_dups = dropped_dups or []

    bar = "=" * 78
    logger.info(bar)
    logger.info("阶段 00 · 原始 Excel 全量样本数据普查 (过滤前; 只读, 不改语料)")
    logger.info(bar)
    logger.info("【功能】统计『最初原始所有 Excel 表格』(预处理过滤·去重之前) 的样本体量与构成,")
    logger.info("       为论文 data appendix / 样本透明性供数。本普查只读 Excel, 不产出 parquet,")
    logger.info("       不触发 stage 00 的清洗/去重/覆盖。")
    logger.info(f"【扫描范围】{scan_root} (递归含 back/; 已按 basename 去重跨目录同名副本)")
    logger.info(f"【数据来源】{data_source_note}")
    if stage00_ingest_count is not None:
        logger.info(f"⚠ 口径: 本普查=递归全量 {_f(d['n_files'])} 个去重源文件; "
                    f"而 stage 00 真正处理走**非递归** glob data_excel/*.xlsx, "
                    f"本机命中 {_f(stage00_ingest_count)} 个文件 — 二者文件集可不同, 普查总量 ≠ 本次实际处理量。")
    if dropped_dups:
        logger.info(f"⚠ 跨目录同名副本: 已跳过 {len(dropped_dups)} 个 (每源只计一次, 避免行数双计): "
                    f"{', '.join(os.path.basename(x) for x in dropped_dups)}")
    logger.info("-" * 78)

    logger.info("一、总量概览")
    logger.info(f"  · 去重后源文件数 : {_f(d['n_files'])} (成功 {_f(d['n_ok'])} / 失败 {_f(d['n_err'])})")
    logger.info(f"  · 原始样本总行数 : {_f(total)}  ★")
    for s, c in d.get("files_by_source", {}).items():
        logger.info(f"      └ 来源 {s:<7}: {_f(d['rows_by_source'].get(s,0)):>12} 行 / {_f(c)} 文件")
    logger.info(f"  · 日期跨度       : {d.get('date_min')} ~ {d.get('date_max')}")
    logger.info(f"  · 唯一媒体(报刊) : {_f(d.get('n_unique_media'))} 家")
    logger.info(f"  · 唯一省份/地区  : {_f(d.get('n_unique_region'))} 个")

    logger.info("-" * 78)
    logger.info("二、关键字段缺失 (空值/空串; pipeline 据此剔除整行 key_columns_for_na_check)")
    for c in KEY_NA_COLS:
        v = nulls.get(c, 0)
        logger.info(f"  · {c:<8}: 缺失 {_f(v):>10} ({_pct(v,total)})")
    logger.info(f"  · 含正文(内容非空)行: {_f(with_content)} ({_pct(with_content,total)}); "
                f"其余 {_f(null_content)} 行仅标题/元数据、正文空, 多集中早期年份, 会被丢弃。")

    logger.info("-" * 78)
    logger.info("三、媒体类型分布 (媒体类型(中文); pipeline 仅保留 报纸)")
    for k, v in mt.items():
        keep = " [保留]" if k == "报纸" else " [剔除]"
        logger.info(f"  · {k:<8}: {_f(v):>12} ({_pct(v,total)}){keep}")

    logger.info("-" * 78)
    logger.info("四、年份分布 (日期; 年份 | 总行数 | wisers | TIT_K)")
    ybs = d.get("year_by_source", {})
    for y, v in d.get("year_counts", {}).items():
        wv = ybs.get("wisers", {}).get(str(y), 0)
        tv = ybs.get("TIT_K", {}).get(str(y), 0)
        logger.info(f"  · {y} : {_f(v):>10} | wisers {_f(wv):>10} | TIT_K {_f(tv):>9}")

    logger.info("-" * 78)
    logger.info("五、地域分布 Top20 (国家地区/省份; pipeline 仅保留中国大陆省级行政区)")
    for k, v in list(d.get("region_counts", {}).items())[:20]:
        keep = " [保留·大陆]" if k in mainland_regions else " [剔除·非大陆]"
        logger.info(f"  · {k:<10}: {_f(v):>12} ({_pct(v,total)}){keep}")
    logger.info(f"  (共 {_f(d.get('n_unique_region'))} 个不同取值)")

    logger.info("-" * 78)
    logger.info("六、媒体(报刊) Top15")
    for k, v in list(d.get("media_top50", {}).items())[:15]:
        logger.info(f"  · {k:<24}: {_f(v):>10}")
    logger.info(f"  (共 {_f(d.get('n_unique_media'))} 家媒体)")

    logger.info("-" * 78)
    logger.info("七、正文长度分布 (内容 总字符数; 注: pipeline 实际过滤用汉字数 100~10000, 此处总字符近似)")
    bins, hist = cl.get("bins", LEN_BINS), cl.get("hist", [])
    for i, h in enumerate(hist):
        hi = "∞" if bins[i+1] >= 10**11 else _f(bins[i+1])
        logger.info(f"  · [{_f(bins[i]):>6}, {hi:>6}) : {_f(h):>12} ({_pct(h,total)})")
    logger.info(f"  · 平均正文字符数: {_f(cl.get('mean_chars'))}; "
                f"落在 [100,10000] (总字符近似): {_f(in_range)} ({_pct(in_range,total)})")

    logger.info("-" * 78)
    logger.info("八、精确重复 (按 MD5 Docid; 分母=参与去重行; pipeline 另有 MinHash 近似去重删更多)")
    logger.info(f"  · 参与去重的行 : {_f(dd.get('total_key_rows'))}")
    logger.info(f"  · 全局唯一文档 : {_f(dd.get('global_unique_docs'))}")
    logger.info(f"  · 精确重复行   : {_f(dd.get('global_dup_rows'))} "
                f"(重复率 {dd.get('global_dup_rate',0)*100:.2f}%)")

    logger.info("-" * 78)
    logger.info("九、原始 → 可用样本 漏斗 (各级为独立单条件边际计数, 非逐级求交)")
    logger.info(f"  · 原始全量          : {_f(total):>12} (100%)")
    logger.info(f"  · 媒体类型=报纸     : {_f(n_paper):>12} ({_pct(n_paper,total)})")
    logger.info(f"  · 正文非空          : {_f(with_content):>12} ({_pct(with_content,total)})")
    logger.info(f"  · 正文长度合规(近似): {_f(in_range):>12} ({_pct(in_range,total)})")
    logger.info(f"  · 精确去重后唯一文档: {_f(dd.get('global_unique_docs')):>12} "
                f"({_pct(dd.get('global_unique_docs',0),total)})")
    logger.info("  ⚠ 真实 pipeline 逐级取交 (报纸 ∩ 大陆 ∩ 有正文 ∩ 银行关键词 ∩ 近似去重),")
    logger.info("    最终分析样本远小于上表任一级 (主削减来自银行关键词保留过滤)。")

    logger.info("-" * 78)
    logger.info(f"十、逐文件明细 (共 {len(perfile)} 个去重源; 文件(相对 data_excel) | 来源 | 行数 | 内容空 | 日期范围)")
    for r in perfile:
        if not r.get("ok"):
            logger.info(f"  · {r['file']:<40} [读取失败] {r.get('error')}")
            continue
        nc = r.get("null_content")
        ncs = f"{_f(nc)}({100*nc/r['n_rows']:.0f}%)" if nc and r["n_rows"] else _f(nc)
        logger.info(f"  · {r['file']:<40} {r['source']:<6} {_f(r['n_rows']):>9} "
                    f"内容空={ncs:<12} {r.get('date_min')}~{r.get('date_max')}")

    if d.get("errors"):
        logger.info("-" * 78)
        logger.info("附: 读取失败文件")
        for e in d["errors"]:
            logger.info(f"  · {e['file']}: {e['error']}")
    logger.info(bar)
    logger.info("=== 完成: 原始 Excel 全量样本普查 (已写入 logs/00_preprocessing.log) ===")


# ============================================================================
# 3. CLI / 集成入口
# ============================================================================

def _load_from_artifacts(summary_path: str, perfile_path: str | None):
    with open(summary_path, encoding="utf-8") as f:
        summary = json.load(f)
    perfile = []
    if perfile_path and os.path.exists(perfile_path):
        with open(perfile_path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                for k in ("n_rows", "null_title", "null_content", "null_media",
                          "null_date", "len_in_range"):
                    if row.get(k) not in (None, ""):
                        try:
                            row[k] = int(float(row[k]))
                        except ValueError:
                            pass
                row["ok"] = str(row.get("ok")).strip().lower() in ("true", "1")
                perfile.append(row)
    return summary, perfile


def log_raw_corpus_census(logger, raw_data_dir: str, mainland_regions: set[str],
                          *, workers: int = 10,
                          from_summary: str | None = None,
                          from_perfile: str | None = None,
                          save_artifacts_dir: str | None = None) -> dict | None:
    """对 raw_data_dir (递归含 back/) 全部原始 Excel 做只读普查并写入给定 logger.

    供 stage 00 (``runner.main``) 直接调用: 把『最初原始所有 Excel 表格中的样本数据
    情况』作为预处理日志的一节真正落入 ``logs/00_preprocessing.log`` (前提: 调用方
    已让该 logger 持有文件 handler)。只读, 不产出 parquet, 不触发任何过滤/去重。

    Returns: 普查 summary (dict); 无文件可读时返回 None。
    """
    stage00_ingest = None
    dropped = []
    if from_summary:
        summary, perfile = _load_from_artifacts(from_summary, from_perfile)
        rel = (os.path.relpath(from_summary, _PROJECT_PARENT)
               if os.path.isabs(from_summary) else from_summary)
        note = (f"渲染自已保存普查产物 {rel} "
                f"(全量读取耗时 {summary.get('elapsed_min','?')} 分钟)")
    else:
        all_files = glob.glob(os.path.join(raw_data_dir, "**", "*.xlsx"), recursive=True)
        files, dropped = dedup_files_by_basename(all_files)
        # stage 00 真正处理用的非递归 glob (披露口径差异)
        stage00_ingest = len(glob.glob(os.path.join(raw_data_dir, "*.xlsx")))
        if not files:
            logger.warning(f"[原始普查] {raw_data_dir} 下未找到任何 .xlsx, 跳过普查。")
            return None
        if dropped:
            logger.warning(f"[原始普查] 检测到 {len(dropped)} 个跨目录同名副本, 已按 basename 去重 "
                           f"(每源只计一次): {', '.join(os.path.basename(x) for x in dropped)}")
        logger.info(f"[原始普查] 开始并行只读 {len(files)} 个去重后原始 Excel "
                    f"(workers={workers}); 仅统计、不改语料, 预计数分钟 ...")
        summary, perfile = compute_raw_census(files, workers=workers, raw_data_dir=raw_data_dir)
        note = (f"本次随 stage 00 运行从零重算 (并行只读 {summary['n_files']} 去重源文件, "
                f"耗时 {summary['elapsed_min']} 分钟)")
        if save_artifacts_dir:
            os.makedirs(save_artifacts_dir, exist_ok=True)
            with open(os.path.join(save_artifacts_dir, "summary.json"), "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            pd.DataFrame(perfile).to_csv(
                os.path.join(save_artifacts_dir, "per_file.csv"),
                index=False, encoding="utf-8-sig")
            logger.info(f"[原始普查] 已保存普查产物到 {save_artifacts_dir}")

    render_census_to_logger(summary, perfile, logger,
                            scan_root=raw_data_dir, data_source_note=note,
                            mainland_regions=mainland_regions,
                            stage00_ingest_count=stage00_ingest,
                            dropped_dups=dropped)
    return summary


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="原始 Excel 全量样本普查 → logs/00_preprocessing.log (只读)")
    ap.add_argument("--from-summary", help="已算好的 summary.json (渲染模式, 不重读 Excel)")
    ap.add_argument("--from-perfile", help="已算好的 per_file.csv (配合 --from-summary)")
    ap.add_argument("--recompute", action="store_true", help="从零并行重算 (读全部原始 Excel)")
    ap.add_argument("--save-artifacts", help="重算模式下把 summary.json/per_file.csv 落到该目录")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args(argv)

    if not (args.from_summary or args.recompute):
        ap.error("须指定 --from-summary 或 --recompute 其一")

    cfg = load_config()
    log_dir = cfg["paths"]["log_dir"]
    raw_dir = cfg["paths"]["raw_data_dir"]
    mainland = set(cfg["preprocessing"].get("mainland_china_regions", []))

    logger = setup_logging(STAGE_NAME, log_dir, console_only=False, file_mode="w")
    log_raw_corpus_census(logger, raw_dir, mainland, workers=args.workers,
                          from_summary=args.from_summary, from_perfile=args.from_perfile,
                          save_artifacts_dir=args.save_artifacts)
    print(f"[raw_census] 已写入 {os.path.join(log_dir, STAGE_NAME + '.log')}")


if __name__ == "__main__":
    main()
