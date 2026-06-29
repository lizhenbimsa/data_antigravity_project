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
- 方法学锚点: 内容寻址 (content-addressed) 出处与版本追踪, 对应
  Sandve et al. (2013) 可复现计算研究规则 4-6 (记录所有中间结果/版本/精确出处);
  详见 main() / write_manifest() 运行期 emit 的 📖 引文 (refs_added=[10.1371/journal.pcbi.1003285])。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import platform
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

from news_process.core.logging import pct4, sig4

logger = logging.getLogger(__name__)

# ── 经核验参考文献 (VERIFIED_REFERENCES 注册表, 逐字照抄 APA-7 + DOI; 仅日志用) ──
# emit 进运行期日志的方法学依据, 让 .log 自证可复现性锚点 (非仅留注释)。
# 本下载器的设计原则 (保存原始 URL + 下载时间戳 + SHA-256 校验和 + manifest 记
# schema_version / per-record sha256 / timestamp_iso 以支持断点续传与复现) 正是
# 内容寻址 (content-addressed) 的出处与版本追踪, 与 core/data_versioning.py 锚定同源。
_REFERENCES = {
    # 白话: 可复现计算研究的十条准则; 本模块落实其规则 4-6——记录所有中间结果 (PDF)、
    #       版本 (schema_version) 与精确出处 (原始 URL + SHA-256 校验和 + 下载时间戳),
    #       让每份抓取的评级报告都能溯源、可复现校验、断点续传。
    "reproducible_provenance": (
        "Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple "
        "rules for reproducible computational research. PLoS Computational Biology, "
        "9(10), e1003285. https://doi.org/10.1371/journal.pcbi.1003285"
    ),
}

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
    """解析给定 bank-year-agency 评级报告的公开下载 URL.

    **NOTE**: 真实实现需 Phase 0 D4 (LLM 抽取 PoC) 后, 通过站内搜索 API 解析.
    当前为 stub, 总是返回 None.
    """
    del bank_name, year  # 预留给未来站内搜索实现 (消除未用参数告警)
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
    """下载单份 PDF 报告.

    session 为 None 时即 dry-run / stub 模式 (不发任何 HTTP 请求)。
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
    """按 (bank × year × agency) 网格批量下载.

    已存在于 ``output_dir`` 的条目自动跳过 (支持断点续传)。
    """
    records: list[DownloadRecord] = []
    banks_list = list(banks)
    years_list = list(years)
    agencies_list = list(agencies)  # 一次性物化, 防迭代器耗尽 (F1 fix)

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
    """落盘下载 manifest, 保障可复现性."""
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
    # 📊 manifest status_summary 占比 (pct4; 纯日志 try/except, 复现 payload 已算的份额)
    try:
        _n = payload["total_records"]
        if _n > 0:
            _ss = payload["status_summary"]
            logger.info(
                "  📊 manifest status_summary 占比: "
                + ", ".join(f"{k}={pct4(v / _n)}" for k, v in _ss.items())
                + f" (schema_version={payload['schema_version']}, total={_n:,d})"
            )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  manifest status 占比统计失败 (不影响落盘): {e}")


def _log_environment_and_config(
    args: argparse.Namespace,
    n_banks: int,
    n_years: int,
    n_agencies: int,
    *,
    stub_mode: bool,
) -> None:
    """打印 ① 项目/环境信息 + ② 输入输出 + ③ 运行配置 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些文件/目录、用了哪些可调参数、抓取哪些数据源"一次性
    落进日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。本模块是
    数据获取脚手架 (非分析), 但其内容寻址出处/版本追踪 (URL + SHA-256 + manifest) 直接
    锚定 Sandve et al. (2013) 可复现计算准则, 故 refs_added=[10.1371/journal.pcbi.1003285]
    (运行期由 main() / write_manifest() emit 📖 引文)。
    """
    try:
        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 模块: NCD 主体评级报告 PDF 批量下载器 (benefit_society 论文数据获取脚手架)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'}")
        if stub_mode:
            logger.info("     · 运行模式: stub / dry-run (无 HTTP session) → 零网络、零流量、$0")
        else:
            logger.info("     · 运行模式: 真实下载 (HTTP session 已注入) → 会产生网络流量")

        logger.info("  📂 输入 / 输出")
        logger.info(f"     · 银行清单 CSV:  {os.path.abspath(args.banks)}")
        logger.info(f"     · PDF 输出目录:  {os.path.abspath(args.output_dir)}")
        logger.info(f"     · manifest 路径: {os.path.abspath(args.manifest)}")

        logger.info("  ⚙ 运行配置")
        logger.info(
            f"     · 抓取网格: {n_banks:,d} 银行 × {n_years:,d} 年份 × {n_agencies:,d} 机构 "
            f"= {n_banks * n_years * n_agencies:,d} 次尝试"
        )
        logger.info(
            f"     · 速率限制 delay_sec={sig4(DEFAULT_DELAY_SEC)}秒 (礼貌爬取) | "
            f"timeout={DEFAULT_TIMEOUT:,d}秒 | max_retries={DEFAULT_MAX_RETRIES:,d}"
        )
        logger.info(
            "     · 评级机构数据源: "
            + " | ".join(f"{k}={v}" for k, v in RATING_AGENCIES.items())
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置信息打印失败 (不影响下载): {e}")


def main(argv: list[str] | None = None) -> int:
    """CLI 入口: 批量下载 NCD 评级报告 (Phase 0 stub 模式).

    无失败返回 0, 否则返回 1。stub 模式 (无 session) 下所有尝试标记为
    status='stub' 或 status='skip', 不产生 HTTP 流量。
    """
    _start_time = time.time()
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

    # ── 【功能】banner (黄金范式, 对齐 main=4d9333dd 63 模块日志富集风格) ──
    logger.info("=" * 72)
    logger.info("NCD 评级报告 PDF 下载器 (benefit_society 论文; Phase 0 数据获取脚手架)")
    logger.info("=" * 72)
    logger.info("【功能】把各家评级机构 (中诚信/大公/联合资信) 公开的银行主体评级报告 PDF")
    logger.info("        批量抓到本地, 供 benefit_society 论文做后续外部财务/评级 outcome 对接。")
    logger.info("【方法】按 (银行 × 年份 × 机构) 网格逐项抓取; 站内搜索解析下载 URL → 礼貌限速下载")
    logger.info("        → 落盘 PDF + SHA-256 校验和; 已存在的条目自动跳过 (断点续传)。")
    logger.info("【判读】末尾 status 汇总: ok=成功落盘 / skip=已存在或无 URL / stub=dry-run 占位")
    logger.info("        / failed=重试耗尽仍失败。失败>0 → 进程返回码 1, 供编排器感知。")
    logger.info("【确定性】Phase 0 当前为 stub (无真实 API), 不发任何 HTTP 请求、零流量、$0;")
    logger.info("          manifest 记录原始 URL + 时间戳 + SHA-256 以保障后续可复现。")
    # 📖 方法论依据 (内容寻址 · 可复现出处与版本追踪): 本下载器以原始 URL + SHA-256 校验和
    #    + manifest (schema_version / per-record sha256 / timestamp_iso) 落盘, 正是该文规则
    #    4-6 (记录所有中间结果/版本/精确出处) 在数据获取层的落地。emit 进 .log 自证锚点。
    logger.info("【方法论依据】可复现计算研究 · 出处与版本追踪:")
    logger.info(f"  📖 {_REFERENCES['reproducible_provenance']}")
    logger.info("     (白话: 可复现计算研究十准则; 本模块落实规则 4-6——记录每份 PDF 的精确出处")
    logger.info("      [原始 URL + SHA-256 + 下载时间戳] 与 manifest 版本, 使抓取可溯源、可复现。)")

    import csv
    with open(args.banks, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        banks = [(row["bank_id"], row["bank_name"]) for row in reader]

    # 📂 输入出处 (CSV 读取边界, 纯日志, 不改 comprehension/数据): 行数 + 列 schema, 便于审计
    logger.info(f"  读取银行清单 CSV: {len(banks):,d} 行, 列=[bank_id, bank_name]")

    years = [int(y) for y in args.years.split(",")]

    # Phase 0: 无 HTTP session (stub 模式); D4 解阻塞后传入 requests.Session()
    session = None if args.dry_run else None

    # 项目/环境信息 + 输入输出 + 运行配置 (日志富集 2026-06-24, 参数解析后打印)
    _log_environment_and_config(
        args, len(banks), len(years), len(("ccxr", "dagong", "lhratings")),
        stub_mode=(session is None),
    )

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
    skip = sum(1 for r in records if r.status == "skip")
    logger.info(
        f"  Summary: ok={ok:,d}, skip={skip:,d}, stub={stub:,d}, "
        f"failed={failed:,d}, total={len(records):,d}"
    )
    # 📊 结果分布 (status 占比, pct4; 纯日志 try/except, total=0 空网格时优雅跳过)
    try:
        _total = len(records)
        if _total > 0:
            logger.info(
                f"  📊 status 占比: ok={pct4(ok / _total)}, skip={pct4(skip / _total)}, "
                f"stub={pct4(stub / _total)}, failed={pct4(failed / _total)} "
                f"(成功落盘率={pct4(ok / _total)}, 失败率={pct4(failed / _total)})"
            )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  status 占比统计失败 (不影响返回码): {e}")

    # ⏱ 阶段计时 (墙钟秒, sig4; 纯日志, golden-safe)
    _elapsed = time.time() - _start_time
    logger.info(f"  ⏱ 总耗时: {sig4(_elapsed)}秒 (网格 {len(records):,d} 项)")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
