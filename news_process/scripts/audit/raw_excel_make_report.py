"""raw_excel_make_report.py — 把 raw_excel_sample_audit 的统计结果渲染为报告 + Excel.

读取 OUT_DIR/summary.json + per_file.csv, 产出:
  - RAW_EXCEL_SAMPLE_REPORT_2026-06-20.md  (UTF-8 中文报告)
  - raw_excel_sample_stats.xlsx            (多 sheet: 概览/逐文件/年份/媒体类型/媒体Top/地域/长度分布)
"""
from __future__ import annotations

import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "_rawstats_20260620")


def fmt(n):
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return str(n)


def pct(a, b):
    return f"{100*a/b:.2f}%" if b else "—"


def main():
    d = json.load(open(os.path.join(OUT_DIR, "summary.json"), encoding="utf-8"))
    perfile = pd.read_csv(os.path.join(OUT_DIR, "per_file.csv"))

    total = d["total_rows"]
    nulls = d["nulls"]
    null_content = nulls.get("内容", 0)
    with_content = total - null_content
    mt = d["mediatype_counts"]
    n_paper = mt.get("报纸", 0)
    cl = d["content_len"]
    in_range = cl.get("n_in_pipeline_range_100_10000_approx", 0)
    dedup = d["dedup"]

    # ---------- Markdown 报告 ----------
    L = []
    w = L.append
    w("# 原始 Excel 样本数据情况统计报告\n")
    w(f"> 数据目录: `news_process/data_excel/` (含 `back/`) · 生成日期: 2026-06-20 · "
      f"读取耗时 {d.get('elapsed_min','?')} 分钟\n")
    w("> 口径: **未经预处理过滤的原始 Excel 全量** (直接读 `Sheet1`, 26 列原始 schema)。\n")

    w("## 一、总量概览\n")
    w("| 指标 | 数值 |")
    w("|---|---|")
    w(f"| Excel 文件总数 | {fmt(d['n_files'])} (成功 {fmt(d['n_ok'])} / 失败 {fmt(d['n_err'])}) |")
    w(f"| **原始样本总行数** | **{fmt(total)}** |")
    for s, c in d["files_by_source"].items():
        w(f"| └ 来源 `{s}` | {fmt(d['rows_by_source'].get(s,0))} 行 / {fmt(c)} 文件 |")
    w(f"| 日期跨度 | {d.get('date_min')} ~ {d.get('date_max')} |")
    w(f"| 唯一媒体(报刊)数 | {fmt(d['n_unique_media'])} |")
    w(f"| 唯一省份/地区数 | {fmt(d['n_unique_region'])} |")
    w(f"| 原始单文件最大列数 | 26 |")
    w("")

    w("## 二、关键字段缺失 (空值/空串)\n")
    w("> pipeline 在预处理阶段会因下列字段缺失而剔除整行 (`key_columns_for_na_check`)。\n")
    w("| 字段 | 缺失行数 | 占比 |")
    w("|---|---|---|")
    for c in ["标题", "内容", "媒体(中文)", "日期"]:
        v = nulls.get(c, 0)
        w(f"| {c} | {fmt(v)} | {pct(v,total)} |")
    w("")
    w(f"- **含正文 (内容非空) 的行**: {fmt(with_content)} ({pct(with_content,total)}) — "
      f"其余 {fmt(null_content)} 行仅有标题/元数据、正文为空 (多集中于早期年份), 会被 pipeline 丢弃。\n")

    w("## 三、媒体类型分布 (`媒体类型(中文)`)\n")
    w("> pipeline 仅保留 **报纸**, 其余类型 (新闻通讯社/杂志/网页 等) 全部剔除。\n")
    w("| 媒体类型 | 行数 | 占比 |")
    w("|---|---|---|")
    for k, v in mt.items():
        w(f"| {k} | {fmt(v)} | {pct(v,total)} |")
    w("")

    w("## 四、年份分布 (`日期`)\n")
    w("| 年份 | 总行数 | wisers | TIT_K |")
    w("|---|---|---|---|")
    ybs = d.get("year_by_source", {})
    for y, v in d["year_counts"].items():
        w(f"| {y} | {fmt(v)} | {fmt(ybs.get('wisers',{}).get(str(y), ybs.get('wisers',{}).get(y,0)))} "
          f"| {fmt(ybs.get('TIT_K',{}).get(str(y), ybs.get('TIT_K',{}).get(y,0)))} |")
    if d.get("bad_date"):
        w(f"\n(无法解析年份的行: 见各文件; 总计含个别异常)")
    w("")

    w("## 五、地域分布 Top (`国家地区/省份`)\n")
    w("> pipeline 仅保留中国大陆省级行政区。\n")
    w("| 省份/地区 | 行数 | 占比 |")
    w("|---|---|---|")
    for k, v in list(d["region_counts"].items())[:25]:
        w(f"| {k} | {fmt(v)} | {pct(v,total)} |")
    w(f"\n(共 {fmt(d['n_unique_region'])} 个不同取值, 上表为前 25)\n")

    w("## 六、媒体(报刊) Top 20\n")
    w("| 报刊 | 行数 |")
    w("|---|---|")
    for k, v in list(d["media_top50"].items())[:20]:
        w(f"| {k} | {fmt(v)} |")
    w(f"\n(共 {fmt(d['n_unique_media'])} 家媒体)\n")

    w("## 七、正文长度分布 (`内容` 总字符数)\n")
    w("> 注: pipeline 实际过滤用**汉字数** 100~10000; 此处为**总字符数**近似 (含标点数字, 略宽)。\n")
    bins = cl["bins"]
    hist = cl["hist"]
    w("| 字符区间 | 行数 | 占比 |")
    w("|---|---|---|")
    for i, h in enumerate(hist):
        lo, hi = bins[i], bins[i+1]
        hi_s = "∞" if hi >= 10**11 else fmt(hi)
        w(f"| [{fmt(lo)}, {hi_s}) | {fmt(h)} | {pct(h,total)} |")
    w(f"\n- 平均正文字符数: {fmt(cl.get('mean_chars'))}")
    w(f"- 落在 pipeline 长度区间 [100, 10000] (总字符近似) 的行: "
      f"{fmt(in_range)} ({pct(in_range,total)})\n")

    w("## 八、重复情况 (按 `MD5 Docid`)\n")
    w("| 指标 | 数值 |")
    w("|---|---|")
    w(f"| 参与去重的行 | {fmt(dedup['total_key_rows'])} |")
    w(f"| 全局唯一文档数 | {fmt(dedup['global_unique_docs'])} |")
    w(f"| 重复行 (全局) | {fmt(dedup['global_dup_rows'])} |")
    w(f"| 重复率 | {dedup['global_dup_rate']*100:.2f}% |")
    w("\n> 注: 这是基于 `MD5 Docid` 的**精确重复**; pipeline 另有 MinHash 近似去重 (近似转载), 删除量更大。\n")

    w("## 九、原始 → 可用样本 漏斗 (粗估)\n")
    w("| 阶段 | 行数 | 相对总量 |")
    w("|---|---|---|")
    w(f"| 原始全量 | {fmt(total)} | 100% |")
    w(f"| 媒体类型=报纸 | {fmt(n_paper)} | {pct(n_paper,total)} |")
    w(f"| 正文非空 | {fmt(with_content)} | {pct(with_content,total)} |")
    w(f"| 正文长度合规(近似) | {fmt(in_range)} | {pct(in_range,total)} |")
    w(f"| 精确去重后唯一文档 | {fmt(dedup['global_unique_docs'])} | {pct(dedup['global_unique_docs'],total)} |")
    w("\n> 漏斗各级为**独立单条件**计数 (非逐级求交), 仅示意各过滤维度的削减幅度; "
      "真实 pipeline 是逐级取交 + 银行关键词 + 大陆地区 + 近似去重, 最终样本更小。\n")

    if d.get("errors"):
        w("## 附: 读取失败文件\n")
        for e in d["errors"]:
            w(f"- {e['file']}: {e['error']}")
        w("")

    md = "\n".join(L)
    md_path = os.path.join(OUT_DIR, "RAW_EXCEL_SAMPLE_REPORT_2026-06-20.md")
    open(md_path, "w", encoding="utf-8").write(md)

    # ---------- Excel 工作簿 ----------
    xlsx_path = os.path.join(OUT_DIR, "raw_excel_sample_stats.xlsx")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as xw:
        # 概览
        ov = [
            ("Excel 文件总数", d["n_files"]),
            ("成功读取", d["n_ok"]), ("读取失败", d["n_err"]),
            ("原始样本总行数", total),
            ("来源 wisers 行数", d["rows_by_source"].get("wisers", 0)),
            ("来源 TIT_K 行数", d["rows_by_source"].get("TIT_K", 0)),
            ("日期最早", d.get("date_min")), ("日期最晚", d.get("date_max")),
            ("唯一媒体数", d["n_unique_media"]), ("唯一省份数", d["n_unique_region"]),
            ("内容为空行数", null_content), ("含正文行数", with_content),
            ("媒体类型=报纸", n_paper),
            ("正文长度合规(近似)", in_range),
            ("全局唯一文档(精确去重)", dedup["global_unique_docs"]),
            ("精确重复行", dedup["global_dup_rows"]),
        ]
        pd.DataFrame(ov, columns=["指标", "数值"]).to_excel(xw, sheet_name="概览", index=False)
        perfile.to_excel(xw, sheet_name="逐文件", index=False)
        pd.DataFrame(sorted(d["year_counts"].items()), columns=["年份", "行数"]).to_excel(
            xw, sheet_name="年份分布", index=False)
        pd.DataFrame(mt.items(), columns=["媒体类型", "行数"]).to_excel(
            xw, sheet_name="媒体类型", index=False)
        pd.DataFrame(d["media_top50"].items(), columns=["媒体", "行数"]).to_excel(
            xw, sheet_name="媒体Top50", index=False)
        pd.DataFrame(d["region_counts"].items(), columns=["省份/地区", "行数"]).to_excel(
            xw, sheet_name="地域分布", index=False)
        lr = [(f"[{fmt(bins[i])},{'inf' if bins[i+1]>=10**11 else fmt(bins[i+1])})", h)
              for i, h in enumerate(hist)]
        pd.DataFrame(lr, columns=["字符区间", "行数"]).to_excel(
            xw, sheet_name="正文长度分布", index=False)

    print("wrote:")
    print(" ", md_path)
    print(" ", xlsx_path)


if __name__ == "__main__":
    main()
