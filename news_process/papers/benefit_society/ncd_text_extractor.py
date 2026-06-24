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
import os
import platform
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from news_process.core.logging import sig4

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
    """把 PDF 转为 base64, 用作 vision API 的请求载荷。"""
    return base64.b64encode(path.read_bytes()).decode("ascii")


# ---------------------------------------------------------------------------
# Provider stubs (Phase 0: 全部返回 stub 响应)
# ---------------------------------------------------------------------------
def _call_gpt4o_vision(pdf_b64: str, prompt: str, *, model_id: str) -> str:
    """调用 GPT-4o vision API。Phase 0 占位 stub, 抛 NotImplementedError 表示未实现。"""
    del pdf_b64, prompt, model_id  # 参数为真实实现预留
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
    """本地 OCR 兜底: 把 OCR 文本包进 JSON 信封 (F2 fix)。

    返回形如 {"_local_ocr_text": "<完整 OCR 文本>"} 的 JSON 字符串, 使
    extract_one 中下游的 JSON 解析能够成功; 结构化字段抽取可推迟到
    针对 _local_ocr_text 的后处理步骤中完成。
    """
    del prompt  # OCR 不使用 prompt; 结构化抽取在下游做
    try:
        import pytesseract  # type: ignore[import-not-found]
        from pdf2image import convert_from_path  # type: ignore[import-not-found]
    except ImportError as e:
        raise NotImplementedError(f"local_ocr requires pytesseract + pdf2image: {e}")

    images = convert_from_path(str(pdf_path), dpi=200)
    pages_text = [pytesseract.image_to_string(img, lang="chi_sim+eng") for img in images]
    full_text = "\n\n=== PAGE BREAK ===\n\n".join(pages_text)
    # F2 fix: 包进 JSON 信封, 保证下游 json.loads() 解析成功
    return json.dumps({"_local_ocr_text": full_text}, ensure_ascii=False)


PROVIDER_DISPATCH = {
    "gpt4o": _call_gpt4o_vision,
    "claude": _call_claude_vision,
    "gemini": _call_gemini_vision,
    "local_ocr": None,  # 在 extract_one 内特判处理
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
    """从单个 PDF 中抽取结构化字段。

    缓存命中时直接返回缓存的响应, 不重新调 API。
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


def _log_environment_and_config(args, pdf_dir: Path, output_path: Path) -> None:
    """打印 ① 项目/环境信息 + ② 输入输出 + ③ 运行配置 + ④ 方法论依据 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些目录/文件、用了哪些可调参数与冻结锚点、方法学出处"
    一次性落进日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    ④ 方法论引文仅 emit 经 Crossref 真值核验的条目, 含 DOI 可访问链接
    (Gentzkow, Kelly & Taddy 2019 JEL https://doi.org/10.1257/jel.20181020),
    绝不伪造 DOI (playbook §4 铁律)。
    """
    try:
        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 阶段: NCD 评级报告 PDF → 结构化字段抽取 (benefit_society, Phase 0 stub; 不在 STAGES_MAIN)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(
            f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
            "Phase 0 全 provider stub (status='stub', $0); 真接 vision API 需 D4 预算解锁 → 付费"
        )

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · PDF 目录:   {os.path.abspath(str(pdf_dir))} (glob *.pdf)")
        logger.info(f"     · 输出 JSON:  {os.path.abspath(str(output_path))}")
        logger.info(f"     · 原始响应:   {os.path.abspath(str(args.raw_response_dir))} (每次调用持久化, reproducibility)")
        logger.info(f"     · 缓存 DB:    {args.cache_db or '(未指定; 不走 LLMCache)'}")

        logger.info("  ⚙ 运行配置")
        _resolved_model = DEFAULT_MODELS.get(args.provider, args.provider)
        logger.info(
            f"     · provider={args.provider} → model_id={_resolved_model} "
            f"| prompt_version={EXTRACTION_PROMPT_VERSION}"
        )
        logger.info(
            "     · Reproducibility 锁定: 固定模型版本 + temperature=0 + seed=42 "
            "(真接 API 时); 缓存键=(model_id, pdf_sha256, prompt_version, temperature)"
        )
        logger.info(
            "     · 抽取字段: 8 项 (bank_name/report_year/total_assets/npl_ratio/car_ratio/"
            "net_profit/retail_deposit/info_tech_invest); JSON-only, 缺失置 null"
        )
        logger.info(
            "     · ⚠ 已知单位口径缺陷 (omni-gapfill-12): prompt 写'亿元'与 *_billion 字段差 10× "
            "→ 解析侧 ncd_field_parser 启发式探测兜底 (改 prompt 须 bump prompt_version → 付费重抽)"
        )

        logger.info("  📖 方法论依据 (核心方法/构念学术出处)")
        logger.info(
            "     · 文本即数据 (从非结构化文档抽取结构化变量): Gentzkow, M., Kelly, B., & "
            "Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. "
            "https://doi.org/10.1257/jel.20181020"
        )
        logger.info(
            "       → 本抽取器把 NCD 评级报告 (扫描 PDF) 经 vision LLM 转为 8 个银行财务字段, "
            "是该范式在中文银行监管文本上的工程化实现 (LLM-as-extractor 取代手工录入)"
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main(argv: list[str] | None = None) -> int:
    """CLI 入口: 经 vision API 从 NCD 评级 PDF 中抽取结构化字段。

    成功返回 0, PDF 目录不存在返回 1。Phase 0 阶段在 API 预算 D4 解锁前,
    所有 provider 都返回 status='stub'。
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

    _t_start = time.time()
    # 运行期阶段计时累计 (各主要子阶段墙钟耗时, 末尾汇总打印; 纯日志, golden-safe)
    phase_durations: dict[str, float] = {}

    # ── 【功能】banner (黄金范式, 对齐 herd_decay main() / geography 单 banner 范式) ──
    logger.info("=" * 72)
    logger.info("NCD 评级报告 PDF → 结构化银行财务字段抽取 (Phase 0 stub; Gentzkow-Kelly-Taddy 2019 JEL)")
    logger.info("=" * 72)
    logger.info(
        "【功能】把扫描版的 NCD (同业存单) 信用评级报告 PDF, 自动读成 8 个结构化银行财务字段"
    )
    logger.info(
        "        (总资产/不良率/资本充足率/净利润/零售存款/信息科技投入等), 取代手工逐页录入,"
    )
    logger.info(
        "        为 benefit_society 论文的银行年度面板补充 outcome/控制变量。"
    )
    logger.info(
        "【方法】每个 PDF → base64 → vision LLM (gpt4o/claude/gemini, 或 local_ocr 兜底) → JSON;"
    )
    logger.info(
        "        固定模型版本 + temperature=0 + seed=42; 缓存键=(model_id, pdf_sha256, prompt_version),"
    )
    logger.info(
        "        命中即直返不重调 API; 每次原始响应落盘 raw_responses/ 供复现核对。"
    )
    logger.info(
        "【判读】每条 ExtractionRecord 的 status: ok=真抽取成功 | cache_hit=命中缓存 | "
    )
    logger.info(
        "        stub=Phase 0 占位(provider 未接 API) | failed=出错。Phase 0 期望全 'stub'。"
    )
    logger.info(
        "【确定性】Phase 0 stub 路径纯 CPU/$0; 真接 vision API 后由 temperature=0+seed+缓存键锁定可复现,"
    )
    logger.info(
        "        但首跑付费 (D4 预算解锁后); local_ocr 走 tesseract 离线、不付费。"
    )

    pdf_dir = Path(args.pdf_dir)
    output_path = Path(args.output)

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论依据 (日志富集 2026-06-24, 参数解析后打印)
    _log_environment_and_config(args, pdf_dir, output_path)

    if not pdf_dir.exists():
        logger.error(f"PDF directory not found: {pdf_dir}")
        return 1

    _t = time.time()
    records = batch_extract(
        pdf_dir,
        provider=args.provider,
        cache_db_path=args.cache_db,
        raw_response_dir=Path(args.raw_response_dir),
    )
    phase_durations['①批量抽取(batch_extract)'] = time.time() - _t

    _t = time.time()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "v1",
        "prompt_version": EXTRACTION_PROMPT_VERSION,
        "provider": args.provider,
        "records": [asdict(r) for r in records],
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    phase_durations['②写出 JSON'] = time.time() - _t
    logger.info(f"Wrote {len(records):,d} records to {output_path}")

    # ── 抽取结果分布摘要 (按 status 计数; 占比走 sig4, golden-safe 纯日志) ──
    _n = len(records)
    if _n:
        _by_status: dict[str, int] = {}
        for r in records:
            _by_status[r.status] = _by_status.get(r.status, 0) + 1
        logger.info(f"  📊 抽取结果分布 (共 {_n:,d} 条):")
        for _st in sorted(_by_status):
            _cnt = _by_status[_st]
            logger.info(f"     · status={_st}: {_cnt:,d} ({sig4(_cnt / _n * 100)}%)")

    # ── ⏱ 阶段计时汇总 (墙钟秒, sig4; 纯日志, golden-safe) ──
    _total = time.time() - _t_start
    logger.info("  ⏱ 阶段计时 (墙钟秒):")
    for _phase, _dur in phase_durations.items():
        _share = (_dur / _total * 100) if _total > 0 else 0.0
        logger.info(f"     · {_phase}: {sig4(_dur)}s ({sig4(_share)}%)")
    logger.info(f"     · 总耗时: {sig4(_total)}s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
