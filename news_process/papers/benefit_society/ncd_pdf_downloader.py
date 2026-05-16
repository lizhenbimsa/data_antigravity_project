"""news_process.papers.benefit_society.ncd_pdf_downloader
==========================================================
NCD 主体评级报告 PDF 批量下载器 (中诚信 / 大公 / 联合资信)

【设计原则】
- 输入: 银行清单 (bank_id, bank_name) + 年份
- 输出: 本地 PDF 副本 + 下载元数据 JSON
- 失败重试 + 速率限制 + 断点续传
- Phase 0 D4 阻塞前的脚手架 (未调用真实 API)

【Reproducibility】
- 保存原始 URL + 下载时间戳 + SHA-256 校验和
- 失败日志单独保存供后续重试
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

# 速率限制 — 礼貌爬取
DEFAULT_DELAY_SEC = 2.0
DEFAULT_TIMEOUT = 60
DEFAULT_MAX_RETRIES = 3

# 评级机构数据源 (PoC stub; 实际 URL 需 Phase 1 D4 解阻塞后填入)
RATING_AGENCIES = {
    "ccxr": "https://www.ccxr.com.cn",      # 中诚信国际
    "dagong": "https://www.dagongcredit.com",  # 大公国际
    "lhratings": "https://www.lhratings.com",  # 联合资信
}


@dataclass
class DownloadRecord:
    """下载记录元数据 (用于断点续传 + reproducibility)"""
    bank_id: str
    bank_name: str
    year: int
    agency: str
    url: str | None
    local_path: str | None
    status: str  # "ok" | "failed" | "skip" | "stub"
    sha256: str | None
    timestamp_iso: str
    error: str | None


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _build_record(
    bank_id: str,
    bank_name: str,
    year: int,
    agency: str,
    *,
    url: str | None = None,
    local_path: str | None = None,
    status: str = "stub",
    sha256: str | None = None,
    error: str | None = None,
) -> DownloadRecord:
    return DownloadRecord(
        bank_id=bank_id,
        bank_name=bank_name,
        year=year,
        agency=agency,
        url=url,
        local_path=local_path,
        status=status,
        sha256=sha256,
        timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%S"),
        error=error,
    )


def search_report_url(
    bank_name: str,
    year: int,
    agency: str,
) -> str | None:
    """Resolve the public download URL for a given bank-year-agency report.

    **NOTE**: 真实实现需 Phase 0 D4 (LLM 抽取 PoC) 后, 通过站内搜索 API 解析.
    当前为 stub, 总是返回 None.
    """
    del bank_name, year  # reserved for future site-search impl (silences unused-param)
    if agency not in RATING_AGENCIES:
        return None
    return None  # stub


def download_one(
    record: DownloadRecord,
    output_dir: Path,
    *,
    session=None,
    delay_sec: float = DEFAULT_DELAY_SEC,
    max_retries: int = DEFAULT_MAX_RETRIES,
    timeout: int = DEFAULT_TIMEOUT,
) -> DownloadRecord:
    """Download a single PDF report.

    If session is None, this is a dry-run / stub mode (no HTTP calls).
    """
    if record.url is None:
        record.status = "skip"
        record.error = "no URL resolved"
        return record

    if session is None:
        record.status = "stub"
        record.error = "dry-run (no HTTP session provided)"
        return record

    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{record.bank_id}_{record.year}_{record.agency}.pdf"
    local_path = output_dir / filename

    for attempt in range(1, max_retries + 1):
        try:
            time.sleep(delay_sec)
            resp = session.get(record.url, timeout=timeout)
            resp.raise_for_status()
            local_path.write_bytes(resp.content)
            record.local_path = str(local_path)
            record.sha256 = _sha256_of_file(local_path)
            record.status = "ok"
            return record
        except Exception as e:
            record.error = f"attempt {attempt}: {type(e).__name__}: {e}"
            logger.warning(f"  {record.bank_name} ({record.year}, {record.agency}): {record.error}")
            time.sleep(delay_sec * attempt)

    record.status = "failed"
    return record


def batch_download(
    banks: Iterable[tuple[str, str]],
    years: Iterable[int],
    *,
    output_dir: Path,
    session=None,
    agencies: Iterable[str] = ("ccxr", "dagong", "lhratings"),
    delay_sec: float = DEFAULT_DELAY_SEC,
) -> list[DownloadRecord]:
    """Batch download across (bank × year × agency) grid.

    Skips entries already present in ``output_dir`` (resume-friendly).
    """
    records: list[DownloadRecord] = []
    banks_list = list(banks)
    years_list = list(years)
    agencies_list = list(agencies)  # materialize once (F1 fix)

    total = len(banks_list) * len(years_list) * len(agencies_list)
    logger.info(f"Planning {total} download attempts ({len(banks_list)} banks × {len(years_list)} years × {len(agencies_list)} agencies)")

    for bank_id, bank_name in banks_list:
        for year in years_list:
            for agency in agencies_list:
                expected = output_dir / f"{bank_id}_{year}_{agency}.pdf"
                if expected.exists():
                    records.append(_build_record(
                        bank_id, bank_name, year, agency,
                        local_path=str(expected),
                        status="skip",
                        sha256=_sha256_of_file(expected),
                        error="already exists",
                    ))
                    continue

                url = search_report_url(bank_name, year, agency)
                record = _build_record(bank_id, bank_name, year, agency, url=url)
                record = download_one(record, output_dir, session=session, delay_sec=delay_sec)
                records.append(record)

    return records


def write_manifest(records: list[DownloadRecord], manifest_path: Path) -> None:
    """Persist download manifest for reproducibility."""
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "v1",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "total_records": len(records),
        "status_summary": {
            status: sum(1 for r in records if r.status == status)
            for status in {"ok", "failed", "skip", "stub"}
        },
        "records": [asdict(r) for r in records],
    }
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Manifest written to {manifest_path}")


def main(argv: list[str] | None = None) -> int:
    """CLI entry: batch download NCD rating reports (Phase 0 stub mode).

    Returns 0 if no failures, 1 otherwise. In stub mode (no session), all attempts
    are marked status='stub' or status='skip' without HTTP traffic.
    """
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.ncd_pdf_downloader",
        description="NCD 评级报告 PDF 批量下载器 (stub 模式)",
    )
    parser.add_argument("--banks", type=str, required=True, help="CSV with columns bank_id,bank_name")
    parser.add_argument("--years", type=str, default="2017,2018", help="Comma-separated years")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="news_process/data/raw/ncd_ratings",
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default="news_process/data/raw/ncd_ratings/_manifest.json",
    )
    parser.add_argument("--dry-run", action="store_true", help="Force stub mode (no HTTP)")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

    import csv
    with open(args.banks, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        banks = [(row["bank_id"], row["bank_name"]) for row in reader]

    years = [int(y) for y in args.years.split(",")]

    # Phase 0: no HTTP session (stub mode); D4 解阻塞后传入 requests.Session()
    session = None if args.dry_run else None

    records = batch_download(
        banks,
        years,
        output_dir=Path(args.output_dir),
        session=session,
    )
    write_manifest(records, Path(args.manifest))

    ok = sum(1 for r in records if r.status == "ok")
    failed = sum(1 for r in records if r.status == "failed")
    stub = sum(1 for r in records if r.status == "stub")
    logger.info(f"Summary: ok={ok}, failed={failed}, stub={stub}, total={len(records)}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
