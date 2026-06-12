"""news_process.papers.benefit_society.ncd_text_extractor
==========================================================
PDF → 文本 抽取器 (GPT-4o vision / Claude vision / Gemini vision)

【设计原则】
- 多 provider 支持: --provider {gpt4o, claude, gemini, local_ocr}
- Reproducibility: 固定模型版本 + temperature=0 + seed
- 原始响应持久化: 每次 API 调用保存至 raw_responses/
- 速率限制 + 重试

【Phase 0 状态】
- D4 阻塞 (需 API 预算)
- 本脚本提供完整框架, 但 API 调用部分 stub

【缓存】
- 复用 [news_process.core.caching.LLMCache] (公开 API)
- 缓存键: (model_id, pdf_hash, prompt_version, temperature)
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

# Reproducibility 锁定
DEFAULT_MODELS = {
    "gpt4o": "gpt-4o-2024-08-06",
    "claude": "claude-opus-4-5-20251001",
    "gemini": "gemini-2.0-pro",
    "local_ocr": "tesseract-zh+eng",  # 备选
}

# Prompt 版本 (变更需 bump → cache miss → 重新抽取)
EXTRACTION_PROMPT_VERSION = "v1-2026-05-16"

# fix(omni-gapfill-12, 2026-06-12) ⚠ 已知缺陷披露 (prompt 本体冻结, 改 prompt 会
# bump 缓存键 → 付费重抽, 故只在解析侧防御):
#   Rule 1 写 "亿元/百万元" 与 total_assets_billion_rmb / retail_deposit_billion_rmb
#   字段名及 ncd_field_parser.EXPECTED_FIELDS 的 billion (十亿) 校验区间冲突 10×
#   (1 billion = 10 亿)。LLM 若遵循 亿元 指令 (中文评级报告原生单位), 返回值是
#   billion 口径的 10 倍: 大行越界被 validate 置 None (静默丢失), 中小行以 10×
#   错值入 ncd_panel。百万元字段 (net_profit/info_tech) 无此冲突。
#   解析侧防御: ncd_field_parser.validate_record 的 10× 启发式探测
#   (suspected unit error 警告 + _unit_suspect_fields 旁路列) +
#   triangulate_with_annual_report 的 unit_mismatch_* 商≈10 旗标 (R11)。
#   D4 解禁真接 API 前若决定改 prompt, 须同步 bump EXTRACTION_PROMPT_VERSION。
EXTRACTION_PROMPT = """You are extracting structured financial data from a Chinese bank NCD (Negotiable Certificates of Deposit) credit rating report.

Extract the following 8 fields, returning JSON only. Use null for fields you cannot find.

{
  "bank_name": "全称",
  "report_year": int,
  "total_assets_billion_rmb": float,
  "npl_ratio_pct": float,
  "car_ratio_pct": float,
  "net_profit_million_rmb": float,
  "retail_deposit_billion_rmb": float,
  "info_tech_invest_million_rmb": float
}

Rules:
1. Convert all monetary amounts to consistent units (亿元/百万元) per field spec
2. Use null (not 0) for missing values
3. Return ONLY the JSON, no markdown fences
"""


@dataclass
class ExtractionRecord:
    """单次抽取记录"""
    pdf_path: str
    pdf_sha256: str
    provider: str
    model_id: str
    prompt_version: str
    response_raw: str | None
    response_parsed: dict | None
    status: str  # ok | failed | cache_hit | stub
    error: str | None
    timestamp_iso: str


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _pdf_to_base64(path: Path) -> str:
    """Convert PDF to base64 for vision API payload."""
    return base64.b64encode(path.read_bytes()).decode("ascii")


# ---------------------------------------------------------------------------
# Provider stubs (Phase 0: 全部返回 stub 响应)
# ---------------------------------------------------------------------------
def _call_gpt4o_vision(pdf_b64: str, prompt: str, *, model_id: str) -> str:
    """Call GPT-4o vision API. Phase 0 stub returns None to indicate unimplemented."""
    del pdf_b64, prompt, model_id  # reserved for real implementation
    raise NotImplementedError(
        "GPT-4o vision API call requires Phase 0 D4 unblock (API key + budget approval). "
        "Wire up openai.ChatCompletion here with model_id, temperature=0, seed=42."
    )


def _call_claude_vision(pdf_b64: str, prompt: str, *, model_id: str) -> str:
    del pdf_b64, prompt, model_id
    raise NotImplementedError(
        "Claude vision API call requires Phase 0 D4 unblock. "
        "Wire up anthropic.Messages.create here."
    )


def _call_gemini_vision(pdf_b64: str, prompt: str, *, model_id: str) -> str:
    del pdf_b64, prompt, model_id
    raise NotImplementedError("Gemini vision unimplemented in Phase 0 stub")


def _call_local_ocr(pdf_path: Path, prompt: str) -> str:
    """Local OCR fallback wrapping OCR text in a JSON envelope (F2 fix).

    Returns a JSON string with shape {"_local_ocr_text": "<full OCR text>"} so that
    downstream JSON parsing in extract_one succeeds; structured field extraction
    can be deferred to a post-processing step that operates on _local_ocr_text.
    """
    del prompt  # OCR ignores the prompt; structured extraction is downstream
    try:
        import pytesseract  # type: ignore[import-not-found]
        from pdf2image import convert_from_path  # type: ignore[import-not-found]
    except ImportError as e:
        raise NotImplementedError(f"local_ocr requires pytesseract + pdf2image: {e}")

    images = convert_from_path(str(pdf_path), dpi=200)
    pages_text = [pytesseract.image_to_string(img, lang="chi_sim+eng") for img in images]
    full_text = "\n\n=== PAGE BREAK ===\n\n".join(pages_text)
    # F2 fix: wrap in JSON envelope so downstream json.loads() succeeds
    return json.dumps({"_local_ocr_text": full_text}, ensure_ascii=False)


PROVIDER_DISPATCH = {
    "gpt4o": _call_gpt4o_vision,
    "claude": _call_claude_vision,
    "gemini": _call_gemini_vision,
    "local_ocr": None,  # special-case in extract_one
}


# ---------------------------------------------------------------------------
# 抽取入口
# ---------------------------------------------------------------------------
def extract_one(
    pdf_path: Path,
    *,
    provider: str = "gpt4o",
    model_id: str | None = None,
    prompt: str = EXTRACTION_PROMPT,
    prompt_version: str = EXTRACTION_PROMPT_VERSION,
    cache_db_path: str | None = None,
    raw_response_dir: Path | None = None,
) -> ExtractionRecord:
    """Extract structured fields from a single PDF.

    On cache hit, returns the cached response without re-calling the API.
    """
    if not pdf_path.exists():
        return ExtractionRecord(
            pdf_path=str(pdf_path),
            pdf_sha256="",
            provider=provider,
            model_id=model_id or "",
            prompt_version=prompt_version,
            response_raw=None,
            response_parsed=None,
            status="failed",
            error=f"PDF not found: {pdf_path}",
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

    pdf_sha = _sha256_of_file(pdf_path)
    resolved_model = model_id or DEFAULT_MODELS.get(provider, provider)

    # 缓存查询
    cache_key_prompt = f"{pdf_sha}|{prompt}"
    cached_response: str | None = None
    if cache_db_path:
        try:
            from news_process.core.caching import LLMCache
            with LLMCache(cache_db_path) as cache:
                cached_response = cache.get(
                    resolved_model,
                    cache_key_prompt,
                    prompt_version=prompt_version,
                )
        except ImportError:
            logger.warning("LLMCache unavailable; skipping cache layer")

    if cached_response is not None:
        try:
            parsed = json.loads(cached_response)
        except json.JSONDecodeError:
            parsed = None
        return ExtractionRecord(
            pdf_path=str(pdf_path),
            pdf_sha256=pdf_sha,
            provider=provider,
            model_id=resolved_model,
            prompt_version=prompt_version,
            response_raw=cached_response,
            response_parsed=parsed,
            status="cache_hit",
            error=None,
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

    # API 调用
    try:
        if provider == "local_ocr":
            response_raw = _call_local_ocr(pdf_path, prompt)
        else:
            call_fn = PROVIDER_DISPATCH.get(provider)
            if call_fn is None:
                raise ValueError(f"Unknown provider: {provider}")
            pdf_b64 = _pdf_to_base64(pdf_path)
            response_raw = call_fn(pdf_b64, prompt, model_id=resolved_model)
    except NotImplementedError as e:
        return ExtractionRecord(
            pdf_path=str(pdf_path),
            pdf_sha256=pdf_sha,
            provider=provider,
            model_id=resolved_model,
            prompt_version=prompt_version,
            response_raw=None,
            response_parsed=None,
            status="stub",
            error=str(e),
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )
    except Exception as e:
        return ExtractionRecord(
            pdf_path=str(pdf_path),
            pdf_sha256=pdf_sha,
            provider=provider,
            model_id=resolved_model,
            prompt_version=prompt_version,
            response_raw=None,
            response_parsed=None,
            status="failed",
            error=f"{type(e).__name__}: {e}",
            timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%S"),
        )

    # 持久化原始响应 (reproducibility)
    if raw_response_dir:
        raw_response_dir.mkdir(parents=True, exist_ok=True)
        raw_path = raw_response_dir / f"{pdf_sha[:16]}_{provider}.json"
        raw_path.write_text(response_raw, encoding="utf-8")

    # 解析 JSON
    parsed = None
    try:
        parsed = json.loads(response_raw)
    except json.JSONDecodeError as e:
        logger.warning(f"  JSON parse failed for {pdf_path.name}: {e}")

    # 写入缓存
    if cache_db_path:
        try:
            from news_process.core.caching import LLMCache
            with LLMCache(cache_db_path) as cache:
                cache.put(
                    resolved_model,
                    cache_key_prompt,
                    response_raw,
                    prompt_version=prompt_version,
                )
        except ImportError:
            pass

    return ExtractionRecord(
        pdf_path=str(pdf_path),
        pdf_sha256=pdf_sha,
        provider=provider,
        model_id=resolved_model,
        prompt_version=prompt_version,
        response_raw=response_raw,
        response_parsed=parsed,
        status="ok",
        error=None,
        timestamp_iso=time.strftime("%Y-%m-%dT%H:%M:%S"),
    )


def batch_extract(
    pdf_dir: Path,
    *,
    provider: str = "gpt4o",
    cache_db_path: str | None = None,
    raw_response_dir: Path | None = None,
    pattern: str = "*.pdf",
) -> list[ExtractionRecord]:
    """Extract all PDFs in a directory."""
    pdfs = sorted(pdf_dir.glob(pattern))
    logger.info(f"Found {len(pdfs)} PDFs in {pdf_dir}")
    records = []
    for pdf in pdfs:
        rec = extract_one(
            pdf,
            provider=provider,
            cache_db_path=cache_db_path,
            raw_response_dir=raw_response_dir,
        )
        records.append(rec)
        logger.info(f"  [{rec.status}] {pdf.name}: {rec.error or 'OK'}")
    return records


def main(argv: list[str] | None = None) -> int:
    """CLI entry: extract structured fields from NCD rating PDFs via vision API.

    Returns 0 on success, 1 if PDF directory not found. In Phase 0, all providers
    return status='stub' until API budget D4 is unblocked.
    """
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.ncd_text_extractor",
        description="NCD 评级报告 PDF → 结构化字段抽取 (stub 模式)",
    )
    parser.add_argument(
        "--pdf-dir",
        type=str,
        default="news_process/data/raw/ncd_ratings",
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=list(PROVIDER_DISPATCH) + ["local_ocr"],
        default="gpt4o",
    )
    parser.add_argument("--cache-db", type=str, default=None)
    parser.add_argument(
        "--raw-response-dir",
        type=str,
        default="news_process/data/intermediate/ncd_raw_responses",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="news_process/data/intermediate/ncd_extracted.json",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

    pdf_dir = Path(args.pdf_dir)
    if not pdf_dir.exists():
        logger.error(f"PDF directory not found: {pdf_dir}")
        return 1

    records = batch_extract(
        pdf_dir,
        provider=args.provider,
        cache_db_path=args.cache_db,
        raw_response_dir=Path(args.raw_response_dir),
    )

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "v1",
        "prompt_version": EXTRACTION_PROMPT_VERSION,
        "provider": args.provider,
        "records": [asdict(r) for r in records],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Wrote {len(records)} records to {output_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
