"""Unit tests for papers/benefit_society/ncd_{downloader,extractor,parser}.py modules.

Covers PDF downloader (stub mode), extractor (cache/stub paths), and field parser.
No real HTTP / LLM API calls are made.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

# =============================================================================
# PDF Downloader Tests
# =============================================================================

@pytest.fixture
def downloader():
    from news_process.papers.benefit_society import ncd_pdf_downloader as d
    return d


def test_downloader_search_report_url_returns_none_for_unknown_agency(downloader):
    """search_report_url stub must return None for unknown agency."""
    assert downloader.search_report_url("某银行", 2018, "unknown_agency") is None


def test_downloader_search_report_url_stub_always_none(downloader):
    """In Phase 0 stub mode, search returns None for all valid agencies."""
    for agency in downloader.RATING_AGENCIES:
        assert downloader.search_report_url("Test Bank", 2018, agency) is None


def test_downloader_build_record_default_status_stub(downloader):
    rec = downloader._build_record("BID-1", "Test Bank", 2018, "ccxr")
    assert rec.bank_id == "BID-1"
    assert rec.status == "stub"
    assert rec.sha256 is None


def test_downloader_download_one_no_url_returns_skip(downloader, tmp_path):
    rec = downloader._build_record("BID-1", "Test Bank", 2018, "ccxr", url=None)
    out = downloader.download_one(rec, tmp_path)
    assert out.status == "skip"


def test_downloader_download_one_no_session_returns_stub(downloader, tmp_path):
    rec = downloader._build_record(
        "BID-1", "Test Bank", 2018, "ccxr",
        url="https://example.com/x.pdf",
    )
    out = downloader.download_one(rec, tmp_path, session=None)
    assert out.status == "stub"
    assert "dry-run" in out.error


def test_downloader_batch_download_dry_run(downloader, tmp_path):
    records = downloader.batch_download(
        [("BID-1", "Bank A"), ("BID-2", "Bank B")],
        [2017, 2018],
        output_dir=tmp_path,
        session=None,
        agencies=["ccxr"],
    )
    # 2 banks × 2 years × 1 agency = 4 records, all stub (no URL)
    assert len(records) == 4
    assert all(r.status in ("skip", "stub") for r in records)


def test_downloader_write_manifest_structure(downloader, tmp_path):
    records = [
        downloader._build_record("BID-1", "Bank A", 2018, "ccxr", status="ok"),
        downloader._build_record("BID-2", "Bank B", 2018, "ccxr", status="failed"),
    ]
    manifest_path = tmp_path / "manifest.json"
    downloader.write_manifest(records, manifest_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "v1"
    assert payload["total_records"] == 2
    assert payload["status_summary"]["ok"] == 1
    assert payload["status_summary"]["failed"] == 1


def test_downloader_batch_skips_existing(downloader, tmp_path):
    # Pre-create one file
    existing = tmp_path / "BID-1_2017_ccxr.pdf"
    existing.write_bytes(b"fake pdf content")

    records = downloader.batch_download(
        [("BID-1", "Bank A")],
        [2017, 2018],
        output_dir=tmp_path,
        session=None,
        agencies=["ccxr"],
    )
    skip_records = [r for r in records if r.status == "skip" and "already exists" in (r.error or "")]
    assert len(skip_records) == 1


# =============================================================================
# Text Extractor Tests
# =============================================================================

@pytest.fixture
def extractor():
    from news_process.papers.benefit_society import ncd_text_extractor as e
    return e


def test_extractor_extract_missing_pdf_returns_failed(extractor, tmp_path):
    missing = tmp_path / "nonexistent.pdf"
    rec = extractor.extract_one(missing, provider="gpt4o")
    assert rec.status == "failed"
    assert "PDF not found" in rec.error


def test_extractor_unimplemented_provider_returns_stub(extractor, tmp_path):
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 fake content")
    rec = extractor.extract_one(fake_pdf, provider="gpt4o")
    # In Phase 0, all providers raise NotImplementedError → status="stub"
    assert rec.status == "stub"
    assert "unblock" in rec.error.lower() or "D4" in rec.error or "API" in rec.error


def test_extractor_cache_hit_short_circuits_api(extractor, tmp_path):
    """If cache has a previous response, no API call is attempted."""
    from news_process.core.caching import LLMCache

    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 fake content")
    cache_path = tmp_path / "fake.db"

    pdf_sha = extractor._sha256_of_file(fake_pdf)
    cache_key = f"{pdf_sha}|{extractor.EXTRACTION_PROMPT}"
    cached_json = json.dumps({"bank_name": "TestBank", "report_year": 2018})

    with LLMCache(str(cache_path)) as cache:
        cache.put(
            extractor.DEFAULT_MODELS["gpt4o"],
            cache_key,
            cached_json,
            prompt_version=extractor.EXTRACTION_PROMPT_VERSION,
        )

    rec = extractor.extract_one(
        fake_pdf,
        provider="gpt4o",
        cache_db_path=str(cache_path),
    )
    assert rec.status == "cache_hit"
    assert rec.response_parsed["bank_name"] == "TestBank"


def test_extractor_pdf_to_base64(extractor, tmp_path):
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 minimal")
    b64 = extractor._pdf_to_base64(pdf_path)
    assert isinstance(b64, str)
    assert len(b64) > 0


def test_extractor_unknown_provider_raises(extractor, tmp_path):
    fake_pdf = tmp_path / "fake.pdf"
    fake_pdf.write_bytes(b"%PDF-1.4 fake content")
    rec = extractor.extract_one(fake_pdf, provider="unknown_provider")
    assert rec.status == "failed"


# =============================================================================
# Field Parser Tests
# =============================================================================

@pytest.fixture
def parser():
    from news_process.papers.benefit_society import ncd_field_parser as p
    return p


def test_parser_validate_field_accepts_none(parser):
    ok, _ = parser.validate_field("npl_ratio_pct", None)
    assert ok


def test_parser_validate_field_range_check(parser):
    ok_in, _ = parser.validate_field("npl_ratio_pct", 5.0)
    ok_out, msg = parser.validate_field("npl_ratio_pct", 99.0)
    assert ok_in
    assert not ok_out
    assert "out of range" in msg


def test_parser_validate_field_type_check(parser):
    ok, msg = parser.validate_field("npl_ratio_pct", "not_a_number")
    assert not ok
    assert "type mismatch" in msg


def test_parser_validate_field_int_to_float_coercion(parser):
    ok, _ = parser.validate_field("npl_ratio_pct", 5)  # int → float OK
    assert ok


def test_parser_validate_field_unknown_field(parser):
    ok, msg = parser.validate_field("not_a_field", 1.0)
    assert not ok
    assert "unknown field" in msg


def test_parser_validate_record_returns_cleaned(parser):
    raw = {
        "bank_name": "Test",
        "report_year": 2018,
        "npl_ratio_pct": 99.0,  # Out of range
        "car_ratio_pct": 12.0,
    }
    cleaned, warns = parser.validate_record(raw)
    assert cleaned["bank_name"] == "Test"
    assert cleaned["npl_ratio_pct"] is None  # Cleaned to None
    assert cleaned["car_ratio_pct"] == 12.0
    assert len(warns) >= 1


def test_parser_records_to_panel_basic(parser):
    records = [
        {
            "pdf_path": "/tmp/A.pdf",
            "response_parsed": {
                "bank_name": "Bank A",
                "report_year": 2018,
                "total_assets_billion_rmb": 100.0,
                "npl_ratio_pct": 1.5,
                "car_ratio_pct": 12.0,
                "net_profit_million_rmb": 500.0,
                "retail_deposit_billion_rmb": 50.0,
                "info_tech_invest_million_rmb": 20.0,
            },
        },
    ]
    panel = parser.records_to_panel(records)
    assert len(panel) == 1
    assert panel.iloc[0]["bank_name"] == "Bank A"
    assert panel.iloc[0]["npl"] == 1.5


def test_parser_records_to_panel_dedups_bank_year(parser):
    records = [
        {"pdf_path": "/a.pdf", "response_parsed": {"bank_name": "A", "report_year": 2018, "total_assets_billion_rmb": 100.0}},
        {"pdf_path": "/b.pdf", "response_parsed": {"bank_name": "A", "report_year": 2018, "total_assets_billion_rmb": 110.0}},
    ]
    panel = parser.records_to_panel(records)
    assert len(panel) == 1  # Dedup'd


def test_parser_flag_outliers(parser):
    df = pd.DataFrame({
        "bank_id": ["A", "B", "C", "D"],
        "year": [2018] * 4,
        "total_assets": [100.0, 105.0, 102.0, 100_000.0],  # last is outlier
        "npl": [1.0, 1.5, 1.2, 1.3],
        "car": [12.0, 12.5, 13.0, 12.2],
        "profit": [100.0, 110.0, 105.0, 102.0],
        "retail_dep": [50.0, 55.0, 52.0, 51.0],
        "info_tech": [10.0, 11.0, 10.5, 10.2],
    })
    flagged = parser.flag_outliers(df, sd_threshold=2.0)
    assert flagged["outlier_total_assets"].sum() >= 1


def test_parser_triangulation_inconsistency_flag(parser):
    ncd = pd.DataFrame({
        "bank_id": ["A"],
        "year": [2018],
        "total_assets": [100.0],
        "npl": [1.5],
        "car": [12.0],
    })
    ar = pd.DataFrame({
        "bank_id": ["A"],
        "year": [2018],
        "total_assets": [110.0],  # 10% diff → inconsistent
        "npl": [1.45],  # ~3% diff → consistent
        "car": [12.1],
    })
    out = parser.triangulate_with_annual_report(ncd, ar, tolerance_pct=5.0)
    assert out["inconsistent_total_assets"].iloc[0] == True
    assert out["inconsistent_npl"].iloc[0] == False
