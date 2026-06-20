"""test_raw_census — 原始 Excel 样本普查模块 + stage 00 集成的快速单测.

覆盖 (2026-06-20 顶刊多智能体评审 GO-WITH-FIXES 后补齐):
- dedup_files_by_basename: 跨目录同名副本去重 (P1 双计修复的核心)
- compute_raw_census: 串行路径下的聚合/年份/媒体/地域/精确去重正确性
- render_census_to_logger: 关键节齐全 + 百分比正确 + 日志文件无 ANSI 控制码
- runner.main() 集成: 真正把普查 + banner + 下游日志共存写进 logs/00_preprocessing.log,
  且开头单次 setup_logging(file_mode='w') 不会把普查截断 (评审 gap #2)

只读、不触发任何 stage 00 处理 (load_and_process_data 被 stub)。
"""
from __future__ import annotations

import logging
import os

import pandas as pd
import pytest

from news_process.pipeline.preprocess import raw_census

CENSUS_COLS = ["docid", "MD5 Docid", "媒体(中文)", "媒体类型(中文)", "内容",
               "日期", "标题", "国家地区/省份", "城市", "字数"]


def _write_xlsx(path, rows):
    """写一个含普查所需列的小 xlsx (Sheet1)."""
    df = pd.DataFrame(rows, columns=CENSUS_COLS)
    df.to_excel(path, sheet_name="Sheet1", index=False, engine="openpyxl")


def _row(docid, md5, media, mtype, content, date, title, region, city, wc):
    return [docid, md5, media, mtype, content, date, title, region, city, wc]


def test_dedup_files_by_basename():
    files = ["data_excel/back/x.xlsx", "data_excel/x.xlsx",
             "data_excel/back/y.xlsx"]
    deduped, dropped = raw_census.dedup_files_by_basename(files)
    assert sorted(os.path.basename(f) for f in deduped) == ["x.xlsx", "y.xlsx"]
    assert [os.path.basename(f) for f in dropped] == ["x.xlsx"]
    # 排序首个保留 (back/x 排在 x 前)
    assert deduped[0].endswith("back/x.xlsx") or deduped[0].endswith("back\\x.xlsx")


def test_compute_raw_census_small(tmp_path):
    f1 = tmp_path / "wisers_a.xlsx"
    f2 = tmp_path / "wisers_b.xlsx"
    _write_xlsx(f1, [
        _row(1, "m1", "人民日报", "报纸", "银行内容" * 60, "2007-03-03 00:00:00", "标题一", "北京", "北京", 120),
        _row(2, "m2", "深圳特区报", "报纸", "金融内容" * 60, "2008-05-05 00:00:00", "标题二", "广东", "深圳", 120),
        _row(3, "m1", "人民日报", "报纸", "重复内容" * 60, "2007-09-09 00:00:00", "标题三", "北京", "北京", 120),
    ])
    _write_xlsx(f2, [
        _row(4, "m4", "大公报", "杂志", "短", "2025-12-01 00:00:00", "标题四", "香港", "香港", 1),
        _row(5, "", "明报", "报纸", "内容" * 60, "2025-06-01 00:00:00", "", "香港", "香港", 60),
    ])
    summary, perfile = raw_census.compute_raw_census(
        [str(f1), str(f2)], workers=1, raw_data_dir=str(tmp_path))

    assert summary["total_rows"] == 5
    assert summary["n_files"] == 2 and summary["n_ok"] == 2 and summary["n_err"] == 0
    assert summary["rows_by_source"] == {"wisers": 5}
    assert summary["year_counts"] == {"2007": 2, "2008": 1, "2025": 2}
    assert summary["date_min"] == "2007-03-03" and summary["date_max"] == "2025-12-01"
    assert summary["mediatype_counts"]["报纸"] == 4
    assert summary["mediatype_counts"]["杂志"] == 1
    assert summary["region_counts"]["北京"] == 2
    assert summary["region_counts"]["香港"] == 2
    # 缺失: f2 行5 标题空 → 标题缺失 1; 无内容缺失 (都非空)
    assert summary["nulls"]["标题"] == 1
    # 精确去重: 5 行键 = m1,m2,m1,m4,(空→回退docid 5) → 唯一 {m1,m2,m4,5}=4
    assert summary["dedup"]["total_key_rows"] == 5
    assert summary["dedup"]["global_unique_docs"] == 4
    assert summary["dedup"]["global_dup_rows"] == 1
    assert len(perfile) == 2
    # relpath 展示 (相对 raw_data_dir)
    assert {p["file"] for p in perfile} == {"wisers_a.xlsx", "wisers_b.xlsx"}


def test_render_census_no_ansi_and_sections(tmp_path, monkeypatch):
    f1 = tmp_path / "wisers_a.xlsx"
    _write_xlsx(f1, [
        _row(1, "m1", "人民日报", "报纸", "银行" * 80, "2010-03-03 00:00:00", "标题", "北京", "北京", 160),
        _row(2, "m2", "大公报", "报纸", "金融" * 80, "2011-05-05 00:00:00", "题二", "香港", "香港", 160),
    ])
    summary, perfile = raw_census.compute_raw_census(
        [str(f1)], workers=1, raw_data_dir=str(tmp_path))

    logfile = tmp_path / "census.log"
    logger = logging.getLogger("test_census_render")
    logger.handlers.clear()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(logfile, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(fh)

    raw_census.render_census_to_logger(
        summary, perfile, logger, scan_root=str(tmp_path),
        data_source_note="单测", mainland_regions={"北京", "上海"},
        stage00_ingest_count=1, dropped_dups=[])
    fh.close()
    logger.handlers.clear()

    text = logfile.read_text(encoding="utf-8")
    # 关键节齐全
    for marker in ["原始 Excel 全量样本数据普查", "一、总量概览", "二、关键字段缺失",
                   "三、媒体类型分布", "四、年份分布", "五、地域分布", "六、媒体(报刊)",
                   "七、正文长度分布", "八、精确重复", "九、原始 → 可用样本 漏斗",
                   "十、逐文件明细"]:
        assert marker in text, f"缺少节: {marker}"
    # 无 ANSI 控制码
    assert "\x1b[" not in text
    # 地域保留/剔除标注正确
    assert "北京" in text and "[保留·大陆]" in text
    assert "[剔除·非大陆]" in text  # 香港
    # 总行数正确
    assert "原始样本总行数 : 2" in text


def test_main_integration_writes_census_to_log(tmp_path, monkeypatch):
    """评审 gap #2: 真跑 runner.main() 证明 banner+普查+下游日志共存于一个文件,
    且开头单次 setup_logging(file_mode='w') 不会把普查截断。load 被 stub, 不触发处理。"""
    from news_process.pipeline.preprocess import runner

    # 造一个递归小语料 (top + back/, 含一对同名副本以触发去重披露)
    raw = tmp_path / "raw"
    (raw / "back").mkdir(parents=True)
    _write_xlsx(raw / "wisers_a.xlsx", [
        _row(1, "m1", "人民日报", "报纸", "银行" * 80, "2009-03-03 00:00:00", "标题", "北京", "北京", 160),
    ])
    _write_xlsx(raw / "back" / "wisers_a.xlsx", [  # 同名副本 → 应被去重
        _row(1, "m1", "人民日报", "报纸", "银行" * 80, "2009-03-03 00:00:00", "标题", "北京", "北京", 160),
    ])
    _write_xlsx(raw / "back" / "wisers_b.xlsx", [
        _row(2, "m2", "大公报", "报纸", "金融" * 80, "2010-05-05 00:00:00", "题二", "香港", "香港", 160),
    ])
    out = tmp_path / "out"
    logs = tmp_path / "logs"
    out.mkdir()
    logs.mkdir()

    # patch 路径 → 临时目录 (绝不碰真实 data_excel / logs / parquet)
    monkeypatch.setitem(runner.CONFIG["paths"], "raw_data_dir", str(raw))
    monkeypatch.setitem(runner.CONFIG["paths"], "output_dir", str(out))
    monkeypatch.setitem(runner.CONFIG["paths"], "log_dir", str(logs))
    monkeypatch.setitem(runner.PARAMS, "raw_census_workers", 1)  # 串行, 免 spawn
    monkeypatch.setitem(runner.PARAMS, "raw_census_logging", True)

    # stub 掉重处理: 只记一行 + 返回 0 (不写 parquet → main 跳过去重)
    def _stub_load(raw_data_dir, output_path):
        runner.logger.info("STUB_LOAD_AND_PROCESS 调用 (测试; 未真正处理)")
        return 0
    monkeypatch.setattr(runner, "load_and_process_data", _stub_load)

    runner.main()  # 不应抛异常

    logfile = logs / "00_preprocessing.log"
    assert logfile.exists()
    text = logfile.read_text(encoding="utf-8")
    # banner (来自 main 开头) + 普查节 + stub 下游 三者共存 (普查未被截断)
    assert "阶段 00: 数据预处理" in text                       # main banner
    assert "原始 Excel 全量样本数据普查" in text               # 普查节
    assert "STUB_LOAD_AND_PROCESS" in text                     # 下游
    # 去重生效: 2 个去重源 (wisers_a 去重后 1 份 + wisers_b), 同名副本被跳过披露
    assert "跨目录同名副本" in text
    assert "原始样本总行数 : 2" in text
    # 非递归 ingest 口径披露 (top-level glob 命中 1 个 wisers_a)
    assert "stage 00 真正处理走" in text


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
