"""papers/benefit_society/ 各模块的 CLI smoke 测试。

验证 argparse 签名与缺输入时的优雅失败行为。
"""

from __future__ import annotations

import pandas as pd
import pytest


def test_dimension_analysis_cli_no_inputs_returns_zero(capsys):
    """缓存 db 缺失时 CLI 必须抛 RuntimeError('LLM cache not found')。

    注: 函数名 "returns_zero" 是历史遗留 — 实际断言的当前契约是 raise
    RuntimeError (fail-loud), 而非返回 0 优雅跳过。"""
    from news_process.papers.benefit_society import dimension_analysis
    argv = [
        "--text-embeddings", "/nonexistent/path.npy",
        "--cache-db", "/nonexistent/cache.db",
    ]
    with pytest.raises(RuntimeError, match="LLM cache not found"):
        dimension_analysis.main(argv)


def test_shrinkage_cli_missing_panel_raises(tmp_path):
    from news_process.papers.benefit_society import shrinkage
    argv = ["--panel", str(tmp_path / "missing.parquet")]
    with pytest.raises(FileNotFoundError):
        shrinkage.main(argv)


def test_shrinkage_cli_missing_columns_returns_nonzero(tmp_path):
    """缺必需列时, CLI 返回 1。"""
    from news_process.papers.benefit_society import shrinkage
    panel = pd.DataFrame({"benefit_mean_full": [0.1, 0.2]})
    panel_path = tmp_path / "panel.parquet"
    panel.to_parquet(panel_path)
    argv = ["--panel", str(panel_path), "--output", str(tmp_path / "out.parquet")]
    rc = shrinkage.main(argv)
    assert rc == 1


def test_ncd_downloader_cli_dry_run(tmp_path):
    """下载器 CLI 在 dry-run 模式下必须产出含 stub 记录的 manifest。"""
    import csv

    from news_process.papers.benefit_society import ncd_pdf_downloader

    banks_csv = tmp_path / "banks.csv"
    with open(banks_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["bank_id", "bank_name"])
        writer.writeheader()
        writer.writerow({"bank_id": "B1", "bank_name": "Test Bank"})

    output_dir = tmp_path / "pdfs"
    manifest = tmp_path / "manifest.json"
    argv = [
        "--banks", str(banks_csv),
        "--years", "2017,2018",
        "--output-dir", str(output_dir),
        "--manifest", str(manifest),
        "--dry-run",
    ]
    rc = ncd_pdf_downloader.main(argv)
    assert rc == 0
    assert manifest.exists()


def test_ncd_extractor_cli_missing_dir_returns_nonzero(tmp_path):
    from news_process.papers.benefit_society import ncd_text_extractor
    argv = ["--pdf-dir", str(tmp_path / "missing")]
    rc = ncd_text_extractor.main(argv)
    assert rc == 1


def test_ncd_extractor_cli_empty_dir_returns_zero(tmp_path):
    """空 PDF 目录应产出空结果文件而非崩溃。"""
    from news_process.papers.benefit_society import ncd_text_extractor
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    output = tmp_path / "out.json"
    raw_dir = tmp_path / "raw"
    argv = [
        "--pdf-dir", str(pdf_dir),
        "--output", str(output),
        "--raw-response-dir", str(raw_dir),
    ]
    rc = ncd_text_extractor.main(argv)
    assert rc == 0
    assert output.exists()


def test_ncd_parser_cli_missing_input_returns_one(tmp_path):
    from news_process.papers.benefit_society import ncd_field_parser
    argv = ["--extracted-json", str(tmp_path / "missing.json")]
    rc = ncd_field_parser.main(argv)
    assert rc == 1


def test_ncd_parser_cli_empty_records_writes_empty_panel(tmp_path):
    """空 records 列表应写出空 parquet 而非崩溃。"""
    import json

    from news_process.papers.benefit_society import ncd_field_parser

    extracted = tmp_path / "extracted.json"
    extracted.write_text(json.dumps({"records": []}), encoding="utf-8")
    output = tmp_path / "panel.parquet"
    argv = [
        "--extracted-json", str(extracted),
        "--output", str(output),
    ]
    rc = ncd_field_parser.main(argv)
    assert rc == 0
