"""news_process.papers.benefit_society.ncd_field_parser
========================================================
NCD 抽取结果 → bank-year panel 结构化转换 + 字段验证

【输入】
- ncd_text_extractor.py 输出: extraction records JSON

【输出】
- bank-year panel parquet:
    columns = [bank_id, bank_name, year, total_assets, npl, car, profit, retail_dep, info_tech]

【校验】
- 字段范围检查 (npl ∈ [0, 50], car ∈ [5, 50], etc.)
- 与年报 / 监管披露三角对照 (R11 robustness)
- 异常值 flag (≥ 3 SD from group median)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from news_process.core.logging import pct4, sig4

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 字段 schema
# ---------------------------------------------------------------------------
EXPECTED_FIELDS = {
    "bank_name": (str, None),
    "report_year": (int, (2010, 2030)),
    "total_assets_billion_rmb": (float, (0.5, 50_000)),
    "npl_ratio_pct": (float, (0.0, 50.0)),
    "car_ratio_pct": (float, (5.0, 50.0)),
    "net_profit_million_rmb": (float, (-100_000, 5_000_000)),
    "retail_deposit_billion_rmb": (float, (0.0, 30_000)),
    "info_tech_invest_million_rmb": (float, (0.0, 100_000)),
}

# fix(omni-gapfill-12, 2026-06-12): prompt Rule 1 "亿元" 与 *_billion_rmb 字段名
# 冲突 10× (1 billion = 10 亿; prompt 冻结不可改 → 解析侧启发式探测, 见
# ncd_text_extractor.EXTRACTION_PROMPT 上方披露)。命中条件: 值越上界但 ÷10 落回
# 区间 → 高度疑似 LLM 按 亿元 回答; 标记而非静默置 None。
_UNIT_SUSPECT_FIELDS = ("total_assets_billion_rmb", "retail_deposit_billion_rmb")


# ── 经核验参考文献 (VERIFIED_REFERENCES; 逐字照抄 APA-7 + DOI, 仅运行期日志 emit 用) ──
# 镜像 pipeline/panel/geography.py 的 _GEO_REFERENCES 范式: 把方法学锚点 emit 进 .log,
# 让日志自证学术依据 (而非仅留在注释)。⚠ 仅放经 Crossref/DataCite 真值核验的 DOI。
_REFERENCES = {
    # R11 跨源构念效度 (construct validity): 用年报 ground-truth 反向核验 LLM 抽取的
    # 会计/披露字段 — 与本模块 triangulate_with_annual_report 的 "NCD vs 年报差异 +
    # 10× 单位错标记" 直接对标。白话: LLM 抽出来的数字不能只看抽得快不快, 还得拿权威
    # 年报对一遍才算可信; 这篇正是讲生成式 LLM 在会计研究中如何对照基准做抽取效度验证。
    # ⚠ pinned 在 R11/验证点 (非顶 banner): 本模块仅"校验"而不"运行"LLM 抽取, 避免装饰式引用。
    "dekok_llm_validation": (
        "de Kok, T. (2025). ChatGPT for textual analysis? How to use generative "
        "LLMs in accounting research. Management Science, 71(9), 7888-7906. "
        "https://doi.org/10.1287/mnsc.2023.03253"
    ),
}


def detect_unit_mismatch(field_name: str, value: Any) -> bool:
    """10× 单位错误启发式 (亿元 vs billion): 越上界但 ÷10 在区间内 → True。"""
    if field_name not in _UNIT_SUSPECT_FIELDS or not isinstance(value, (int, float)):
        return False
    lo, hi = EXPECTED_FIELDS[field_name][1]
    return value > hi and lo <= value / 10.0 <= hi


# ---------------------------------------------------------------------------
# 字段验证
# ---------------------------------------------------------------------------
def validate_field(field_name: str, value: Any) -> tuple[bool, str]:
    """校验单个字段的类型与取值范围.

    Returns
    -------
    (is_valid, error_msg)
    """
    if value is None:
        return True, ""  # null 可接受 (缺失数据)
    if field_name not in EXPECTED_FIELDS:
        return False, f"unknown field: {field_name}"

    expected_type, expected_range = EXPECTED_FIELDS[field_name]
    if not isinstance(value, expected_type):
        if expected_type is float and isinstance(value, int):
            value = float(value)
        elif expected_type is int and isinstance(value, float) and value.is_integer():
            value = int(value)
        else:
            return False, f"type mismatch: expected {expected_type.__name__}, got {type(value).__name__}"

    if expected_range is not None and not (expected_range[0] <= value <= expected_range[1]):
        return False, f"out of range [{expected_range[0]}, {expected_range[1]}]: {value}"

    return True, ""


def validate_record(parsed: dict) -> tuple[dict, list[str]]:
    """校验解析记录中的全部字段.

    Returns
    -------
    (cleaned_record, list_of_warnings)
    """
    warnings: list[str] = []
    cleaned: dict = {}
    unit_suspects: list[str] = []
    for field_name in EXPECTED_FIELDS:
        value = parsed.get(field_name)
        is_valid, err = validate_field(field_name, value)
        if is_valid:
            cleaned[field_name] = value
        elif detect_unit_mismatch(field_name, value):
            # fix(omni-gapfill-12, 2026-06-12): 越界 + ÷10 落回区间 → 疑似 prompt
            # Rule 1 亿元/billion 10× 单位错误。不静默置 None 了之: 显式警告 +
            # 记入 _unit_suspect_fields (records_to_panel 旁路列), 供人工/三角
            # 对照 (triangulate unit_mismatch_*) 裁决; 值本身仍置 None (不自动
            # ÷10 改写 — 无年报对照时缩放同样可能是错的)。
            unit_suspects.append(field_name)
            warnings.append(
                f"  {field_name}: {err} — SUSPECTED 10x unit error "
                f"(亿元 vs billion, prompt Rule 1 ambiguity; value/10={value / 10.0})"
            )
            cleaned[field_name] = None
        else:
            warnings.append(f"  {field_name}: {err}")
            cleaned[field_name] = None
    cleaned["_unit_suspect_fields"] = unit_suspects
    return cleaned, warnings


# ---------------------------------------------------------------------------
# Bank-year panel 构建
# ---------------------------------------------------------------------------
def records_to_panel(records: list[dict], bank_id_lookup: dict[str, str] | None = None) -> pd.DataFrame:
    """把抽取记录转换为 bank-year DataFrame.

    Parameters
    ----------
    records : list of dict
        每个 dict 须含 'response_parsed' (已校验字段) + 'pdf_path' (用于推断 bank_id)
    bank_id_lookup : optional
        ``{bank_name -> target_bank}`` 映射。``target_bank`` 是主管线面板
        ([40_panel_yearly.parquet]) 使用的规范标识符; None 时按 ``bank_name``
        原样回退。

    Returns
    -------
    含以下列的 DataFrame:
        bank_id, bank_name, year, total_assets, npl, car, profit, retail_dep, info_tech, source_pdf

    Note
    ----
    返回列 ``bank_id`` 即 lookup 结果 — 与主面板 merge 时请重命名为
    ``target_bank`` 以对齐 pipeline 约定。
    """
    rows: list[dict] = []
    for rec in records:
        parsed = rec.get("response_parsed")
        if parsed is None:
            continue

        cleaned, warns = validate_record(parsed)
        if warns:
            logger.warning(f"PDF {rec.get('pdf_path', '?')}:")
            for w in warns:
                logger.warning(w)

        bank_name = cleaned.get("bank_name")
        if bank_name is None:
            continue

        bank_id = bank_id_lookup.get(bank_name, bank_name) if bank_id_lookup else bank_name

        rows.append({
            "bank_id": bank_id,
            "bank_name": bank_name,
            "year": cleaned.get("report_year"),
            "total_assets": cleaned.get("total_assets_billion_rmb"),
            "npl": cleaned.get("npl_ratio_pct"),
            "car": cleaned.get("car_ratio_pct"),
            "profit": cleaned.get("net_profit_million_rmb"),
            "retail_dep": cleaned.get("retail_deposit_billion_rmb"),
            "info_tech": cleaned.get("info_tech_invest_million_rmb"),
            "source_pdf": rec.get("pdf_path", ""),
            # fix(omni-gapfill-12, 2026-06-12): 10× 单位疑似旁路列 (';' 连接,
            # '' = 无嫌疑), 供下游审计/三角对照过滤。
            "unit_suspect_fields": ";".join(cleaned.get("_unit_suspect_fields", [])),
        })

    # ── 日志富集 (Round 8, log-only): 记录→面板抽取漏斗 + 字段校验质量摘要 ──
    # 上游 LLM 抽取的银行财务字段 (含取值域核验) 的 attrition/质量是审稿核心关切。
    # 纯只读重算: re-iterate records + 重调纯函数 validate_record (无副作用/不写全局),
    # 结果仅 feed logger 后丢弃, 绝不参与 rows/df 构建 → 控制流与产物字节不变 (golden-safe)。
    try:
        _total_recs = len(records)
        _n_parsed = sum(1 for _r in records if _r.get("response_parsed") is not None)
        _n_rows = len(rows)  # parsed 且 bank_name 非空 → 追加成行 (已是上方既算 local)
        _n_field_warn = 0     # ≥1 字段告警的记录数
        _n_coerced = 0        # 类型/范围失败被置 None 的字段数 (排除 10× 单位疑似子集)
        _n_unit_suspect = 0   # 10× 单位疑似 (亿元 vs billion) 标记总数
        _n_fields_checked = 0  # 累计校验字段数 (分母)
        for _r in records:
            _p = _r.get("response_parsed")
            if _p is None:
                continue
            _cl, _w = validate_record(_p)  # 纯函数, 仅取计数 (此处不重复 emit warning)
            _n_fields_checked += len(EXPECTED_FIELDS)
            if _w:
                _n_field_warn += 1
            _us = set(_cl.get("_unit_suspect_fields", []))
            _n_unit_suspect += len(_us)
            # input 非空但 cleaned 置 None 且非 10× 单位疑似 → 纯类型/范围失败 (干净分区)
            _n_coerced += sum(
                1 for _f in EXPECTED_FIELDS
                if _cl.get(_f) is None and _p.get(_f) is not None and _f not in _us
            )
        logger.info("  🔎 记录→面板抽取漏斗 (provenance)")
        logger.info(
            f"     · 总抽取记录: {_total_recs:,d} → 含 response_parsed: {_n_parsed:,d} "
            f"({pct4(_n_parsed / _total_recs) if _total_recs else '—'} of 总记录)"
        )
        logger.info(
            f"     · 含非空 bank_name (追加成行): {_n_rows:,d} "
            f"({pct4(_n_rows / _total_recs) if _total_recs else '—'} of 总记录; "
            f"{pct4(_n_rows / _n_parsed) if _n_parsed else '—'} of parsed)"
        )
        logger.info("  🔬 字段校验质量摘要 (LLM 抽取数值的范围/类型核验)")
        logger.info(
            f"     · ≥1 字段告警的记录: {_n_field_warn:,d} "
            f"({pct4(_n_field_warn / _n_parsed) if _n_parsed else '—'} of parsed)"
        )
        logger.info(
            f"     · 类型/范围失败置 None 的字段: {_n_coerced:,d} / 累计校验 "
            f"{_n_fields_checked:,d} 字段 "
            f"({pct4(_n_coerced / _n_fields_checked) if _n_fields_checked else '—'})"
        )
        logger.info(
            f"     · 10× 单位疑似 (亿元 vs billion) 标记: {_n_unit_suspect:,d} "
            f"({pct4(_n_unit_suspect / _n_fields_checked) if _n_fields_checked else '—'} of 字段)"
        )
    except Exception as _e:  # noqa: BLE001 — 日志块绝不让转换崩 (golden-safe)
        logger.warning(f"  (记录→面板漏斗/校验质量日志失败, 忽略不影响产物): {_e}")

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # 去重 (每个 bank-year 保留 source_pdf 排序最后的一条)
    df = df.sort_values(["bank_id", "year", "source_pdf"])
    _n_pre_dedup = len(df)  # log-only: 去重前行数 (== len(rows), sort 不丢行)
    df = df.drop_duplicates(subset=["bank_id", "year"], keep="last").reset_index(drop=True)
    # 日志富集 (Round 8, log-only): bank-year 去重折叠量 (纯 len 读, 不改 df)
    try:
        _n_collapsed = _n_pre_dedup - len(df)
        logger.info(
            f"  🧹 bank-year 去重: {_n_pre_dedup:,d} → {len(df):,d} 行 "
            f"(折叠重复 bank-year {_n_collapsed:,d} 条, 保留 source_pdf 排序最末; "
            f"保留率 {pct4(len(df) / _n_pre_dedup) if _n_pre_dedup else '—'})"
        )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  (去重计数日志失败, 忽略): {_e}")
    return df


# ---------------------------------------------------------------------------
# 异常值检测 (≥ 3 SD)
# ---------------------------------------------------------------------------
def flag_outliers(
    df: pd.DataFrame,
    *,
    numeric_cols: tuple[str, ...] = ("total_assets", "npl", "car", "profit", "retail_dep", "info_tech"),
    sd_threshold: float = 3.0,
) -> pd.DataFrame:
    """新增布尔列 ``outlier_<col>``, 标记偏离中位数超过 sd_threshold 个稳健 SD 的值.

    用 MAD (中位数绝对偏差) × 1.4826 作为稳健 SD 估计量 (Rousseeuw & Croux 1993)。
    与样本 SD 不同, MAD 不会被它要检测的离群值本身推大。

    白话: 如果用普通标准差找离群值, 离群值自己会把标准差撑大、反而藏住自己;
    MAD 用"到中位数的距离的中位数", 对极端值不敏感, 找得更准。
    """
    df = df.copy()
    for col in numeric_cols:
        if col not in df.columns:
            continue
        med = df[col].median()
        deviations = (df[col] - med).abs()
        mad = deviations.median()
        robust_sd = 1.4826 * mad  # 高斯分布假设下 MAD→SD 的换算系数
        if not np.isfinite(robust_sd) or robust_sd == 0:
            df[f"outlier_{col}"] = False
            continue
        df[f"outlier_{col}"] = (deviations / robust_sd) > sd_threshold
    return df


# ---------------------------------------------------------------------------
# 三角对照 (R11)
# ---------------------------------------------------------------------------
def triangulate_with_annual_report(
    ncd_panel: pd.DataFrame,
    annual_report_panel: pd.DataFrame,
    *,
    join_keys: tuple[str, str] = ("bank_id", "year"),
    fields_to_compare: tuple[str, ...] = ("total_assets", "npl", "car"),
    tolerance_pct: float = 5.0,
    unit_quotient: float = 10.0,
    unit_quotient_tol_pct: float = 10.0,
) -> pd.DataFrame:
    """Compare NCD-extracted fields with annual-report fields, flagging discrepancies.

    Returns
    -------
    DataFrame with columns ``inconsistent_<field>`` (bool) for each compared field,
    plus ``unit_mismatch_<field>`` (bool) — fix(omni-gapfill-12, 2026-06-12):
    NCD/年报 取整商 ≈ ``unit_quotient`` (默认 10, ±``unit_quotient_tol_pct``%)
    时标记为 亿元/billion 单位错误 (prompt Rule 1 ambiguity), 与普通数值不一致
    区分 — 单位错可机械 ÷10 修复, 普通不一致须人工裁决。
    """
    merged = ncd_panel.merge(
        annual_report_panel,
        on=list(join_keys),
        how="inner",
        suffixes=("_ncd", "_ar"),
    )
    q_lo = unit_quotient * (1 - unit_quotient_tol_pct / 100.0)
    q_hi = unit_quotient * (1 + unit_quotient_tol_pct / 100.0)
    for f in fields_to_compare:
        ncd_col = f"{f}_ncd"
        ar_col = f"{f}_ar"
        if ncd_col not in merged.columns or ar_col not in merged.columns:
            continue
        ar_nonzero = merged[ar_col].replace(0, np.nan).abs()
        diff_pct = (merged[ncd_col] - merged[ar_col]).abs() / ar_nonzero * 100
        merged[f"inconsistent_{f}"] = diff_pct > tolerance_pct
        quotient = merged[ncd_col].abs() / ar_nonzero
        merged[f"unit_mismatch_{f}"] = quotient.between(q_lo, q_hi).fillna(False)
    return merged


def _log_environment_and_config(
    extracted_path: Path,
    output_path: Path,
    annual_report: str | None,
    sd_threshold: float = 3.0,
) -> None:
    """打印 ① 项目/环境信息 + ② 输入输出 + ③ 运行配置 + ④ 方法论依据 (日志富集, 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    ④ 方法论引文仅 emit 经 Crossref 真值核验的条目, 含 DOI 可访问链接, 绝不伪造 DOI。
    """
    try:
        import os
        import platform

        logger.info("  🧭 项目 / 环境信息")
        logger.info("     · 模块: ncd_field_parser (NCD/普惠披露文本抽取记录 → bank-year 面板字段结构化+校验)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get("NEWS_PROCESS_RUN_ID")
        logger.info(
            f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
            "本模块纯 CPU / 无 LLM·Embedding·网络·API ($0; 上游 LLM 抽取已落 JSON) → 逐位可复现"
        )

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:   {extracted_path} (ncd_text_extractor.py 输出的 extraction records JSON)")
        logger.info(f"     · 输出:   {output_path} (bank-year panel parquet)")
        logger.info(
            f"     · R11 三角对照源: {annual_report or '(未提供 — 跳过年报互证)'}"
        )

        logger.info("  ⚙ 运行配置 (字段 schema + 校验阈值)")
        logger.info(f"     · 抽取字段数: {len(EXPECTED_FIELDS):,d} (含取值域校验; 越界/类型错 → 置 None + warning)")
        logger.info(
            f"     · 离群判据: MAD×1.4826 稳健 SD, sd_threshold={sig4(sd_threshold)} "
            f"(|x−median|/robust_sd > 阈值 → outlier_<col>=True)"
        )
        _lo, _hi = EXPECTED_FIELDS["npl_ratio_pct"][1]
        logger.info(
            f"     · 单位错启发式 (亿元 vs billion, 10×): 字段 {_UNIT_SUSPECT_FIELDS} 越上界但 ÷10 落回区间 → 标记;"
            f" 示例域 npl_ratio_pct∈[{sig4(_lo)}, {sig4(_hi)}]%"
        )

        logger.info("  📖 方法论依据 (核心方法/构念学术出处)")
        logger.info(
            "     · 披露文本 → 结构化数据抽取 (text-as-data): Gentzkow, M., Kelly, B., & Taddy, M. "
            "(2019). Text as data. Journal of Economic Literature, 57(3), 535-574. "
            "https://doi.org/10.1257/jel.20181020"
        )
        logger.info(
            "     · 会计/金融披露文本分析: Loughran, T., & McDonald, B. (2016). Textual analysis in "
            "accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. "
            "https://doi.org/10.1111/1475-679X.12123 — 财报/CSR 披露字段化口径"
        )
        logger.info(
            "     · 稳健离群检测 (MAD 替代样本 SD, 不被离群值自身撑大): Rousseeuw, P. J., & Croux, C. "
            "(1993). Alternatives to the median absolute deviation. Journal of the American Statistical "
            "Association, 88(424), 1273-1283. https://doi.org/10.1080/01621459.1993.10476408"
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main(argv: list[str] | None = None) -> int:
    """CLI 入口: 把 NCD 抽取记录 JSON 转换为 bank-year panel parquet。

    执行 schema 校验、离群值标记, 以及可选的 R11 与年报数据三角互证。
    成功返回 0, 输入 JSON 不存在返回 1。
    """
    import time
    _start = time.time()
    phase_durations: dict[str, float] = {}
    parser = argparse.ArgumentParser(
        prog="python -m news_process.papers.benefit_society.ncd_field_parser",
        description="NCD 抽取结果 → bank-year panel + 字段验证",
    )
    parser.add_argument(
        "--extracted-json",
        type=str,
        default="news_process/data/intermediate/ncd_extracted.json",
    )
    parser.add_argument(
        "--bank-id-map",
        type=str,
        default=None,
        help="Optional CSV with columns [bank_name, bank_id]",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="news_process/data/processed/ncd_panel.parquet",
    )
    parser.add_argument(
        "--annual-report",
        type=str,
        default=None,
        help="Optional annual-report panel parquet for R11 triangulation",
    )
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s %(message)s")

    # ── 【功能】banner (黄金范式; 替换裸启动头, 对齐 herd_decay main() 单 banner 范式) ──
    logger.info("=" * 72)
    logger.info("NCD 字段解析器: 普惠/CSR 披露文本抽取记录 → bank-year 面板字段结构化+校验")
    logger.info("=" * 72)
    logger.info(
        "【功能】把上游 LLM 从 NCD/普惠披露 PDF 抽取的字段 JSON, 转成规范的 bank-year 面板"
    )
    logger.info(
        "        (total_assets/npl/car/profit/retail_dep/info_tech), 并做字段校验、稳健离群标记、"
    )
    logger.info(
        "        以及可选的 R11 与年报三角互证, 供 benefit_society 论文 outcome 侧消费。"
    )
    logger.info(
        f"【方法】逐记录按 {len(EXPECTED_FIELDS):,d} 字段 schema 校验类型+取值域 (越界/类型错→置 None+warning);"
    )
    logger.info(
        "        '亿元 vs billion' 10× 单位错启发式标记 (不静默改写); 同 bank-year 去重保留 source_pdf 最末;"
    )
    logger.info(
        "        离群用 MAD×1.4826 稳健 SD (不被离群值自身撑大), 偏离中位数 > 阈值个 SD 即 flag。"
    )
    logger.info(
        "【判读】outlier_<col>=True 即该值离群待核; unit_suspect_fields 非空即疑似 10× 单位错;"
    )
    logger.info(
        "        R11 inconsistent_<f>=True 即 NCD 与年报差异超容差, unit_mismatch_<f> 区分单位错 vs 真不一致。"
    )
    logger.info(
        "【确定性】纯 CPU, $0, 无 LLM/Embedding/网络 (上游抽取已落 JSON) → 逐位可复现。"
    )

    extracted_path = Path(args.extracted_json)
    if not extracted_path.exists():
        logger.error(f"Extracted JSON not found: {extracted_path}")
        return 1

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论依据 (日志富集 2026-06-24, 路径确定后打印)
    _log_environment_and_config(extracted_path, Path(args.output), args.annual_report)

    _t = time.time()
    payload = json.loads(extracted_path.read_text(encoding="utf-8"))
    records = payload.get("records", [])
    phase_durations["①读抽取JSON"] = time.time() - _t
    logger.info(f"Loaded {len(records):,d} extraction records")

    bank_id_lookup = None
    if args.bank_id_map:
        import csv
        with open(args.bank_id_map, encoding="utf-8") as f:
            bank_id_lookup = {row["bank_name"]: row["bank_id"] for row in csv.DictReader(f)}

    _t = time.time()
    panel = records_to_panel(records, bank_id_lookup=bank_id_lookup)
    phase_durations["②记录→bank-year面板"] = time.time() - _t
    logger.info(f"Built panel: {panel.shape}")

    _t = time.time()
    panel = flag_outliers(panel)
    phase_durations["③稳健离群标记"] = time.time() - _t
    n_outliers = sum(panel[c].sum() for c in panel.columns if c.startswith("outlier_"))
    _n_cells = len(panel) * sum(1 for c in panel.columns if c.startswith("outlier_"))
    logger.info(
        f"Flagged {n_outliers:,d} outlier cells"
        + (f" ({pct4(n_outliers / _n_cells)} of {_n_cells:,d} checked)" if _n_cells else "")
    )

    # ── 📊 抽取 outcome 字段分布 (Round 8, log-only): 6 个核心财务字段的描述统计 ──
    # 模块的核心产物 = bank-year 面板的抽取财务字段; 上方仅 logged shape + 离群计数,
    # 缺字段层分布。逐列 emit n/均值/中位/标准差/四分位/极值 (非整数一律 sig4), 供审稿
    # 核验 LLM 抽取数值的量纲与离散合理性 (审稿评估抽取数据质量的最高价值缺口)。
    # 纯只读 panel, 结果仅 feed logger 后丢弃, 不回写/不参与计算 → golden-safe。
    try:
        _outcome_cols = ("total_assets", "npl", "car", "profit", "retail_dep", "info_tech")
        logger.info("  📊 抽取 outcome 字段分布 (bank-year panel; 非整数均 sig4)")
        for _col in _outcome_cols:
            if _col not in panel.columns:
                continue
            _s = pd.to_numeric(panel[_col], errors="coerce").dropna()
            _n = len(_s)
            if _n == 0:
                logger.info(f"     · {_col}: n=0 (全空, 无有效抽取值)")
                continue
            _q25, _q75 = _s.quantile(0.25), _s.quantile(0.75)
            logger.info(
                f"     · {_col}: n={_n:,d} mean={sig4(_s.mean())} "
                f"median={sig4(_s.median())} std={sig4(_s.std())} "
                f"p25/p75={sig4(_q25)}/{sig4(_q75)} "
                f"[min,max]=[{sig4(_s.min())},{sig4(_s.max())}]"
            )
    except Exception as _e:  # noqa: BLE001 — 分布日志块绝不让阶段崩 (golden-safe)
        logger.warning(f"  (outcome 字段分布日志失败, 忽略不影响产物): {_e}")

    if args.annual_report and Path(args.annual_report).exists():
        _t = time.time()
        ar_panel = pd.read_parquet(args.annual_report)
        triangulation = triangulate_with_annual_report(panel, ar_panel)
        inconsistent_cols = [c for c in triangulation.columns if c.startswith("inconsistent_")]
        n_inconsistent = sum(triangulation[c].sum() for c in inconsistent_cols)
        phase_durations["④R11年报三角对照"] = time.time() - _t
        logger.info(
            f"R11 triangulation: {n_inconsistent:,d} inconsistent rows across "
            f"{len(inconsistent_cols):,d} fields"
        )
        # 📖 构念效度锚点 (Round 8): R11 = 用年报 ground-truth 反向核验 LLM 抽取的会计
        # 字段 (差异 + 10× 单位错标记), 正是"对照基准验证生成式 LLM 抽取结果"的方法学步骤。
        # 锚点 pinned 在 R11 验证点 (非顶 banner) — 本模块仅校验、不运行 LLM 抽取 (避免装饰式引用)。
        logger.info(f"  📖 {_REFERENCES['dekok_llm_validation']}")
        # 📊 单位错 vs 真不一致区分 (log-only): unit_mismatch_<f>=True 可机械 ÷10 修复,
        # 余为须人工裁决的真数值不一致; 纯只读 triangulation 列求和, 结果仅 feed logger。
        try:
            _um_cols = [c for c in triangulation.columns if c.startswith("unit_mismatch_")]
            if _um_cols:
                _n_unit_mismatch = int(sum(int(triangulation[c].sum()) for c in _um_cols))
                _n_rows_tri = len(triangulation)
                logger.info(
                    f"     · 其中 10× 单位错 (亿元/billion) 标记: {_n_unit_mismatch:,d} "
                    f"({pct4(_n_unit_mismatch / _n_rows_tri) if _n_rows_tri else '—'} of "
                    f"{_n_rows_tri:,d} 三角对照行; 可机械 ÷10 修复)"
                )
        except Exception as _e:  # noqa: BLE001 — 单位错统计日志块绝不让阶段崩
            logger.warning(f"  (R11 单位错统计日志失败, 忽略): {_e}")

    _t = time.time()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(output_path, index=False)
    phase_durations["⑤写出parquet"] = time.time() - _t
    logger.info(f"Wrote panel to {output_path}")

    # ── 📦 落盘 schema provenance (Round 8, log-only): 写出 parquet 的列/类型契约 ──
    # shape 已在上方 logged; 此处补列清单 + dtype 直方图, 完成 stage-boundary I/O 契约
    # (per-column 非空计数已在上方 outcome 分布块逐列 emit, 此处刻意不重复以避免冗余)。
    # 纯只读 panel.dtypes/columns, 结果仅 feed logger → golden-safe。
    try:
        _dtype_hist: dict[str, int] = {}
        for _dt in panel.dtypes.astype(str):
            _dtype_hist[_dt] = _dtype_hist.get(_dt, 0) + 1
        logger.info(
            f"  📦 落盘 schema: {panel.shape[0]:,d} 行 × {panel.shape[1]:,d} 列 "
            f"→ {output_path.name}"
        )
        logger.info(f"     · dtype 直方图: {_dtype_hist}")
        logger.info(f"     · 列清单: {list(panel.columns)}")
    except Exception as _e:  # noqa: BLE001 — 落盘 schema 日志块绝不让阶段崩
        logger.warning(f"  (落盘 schema 日志失败, 忽略): {_e}")

    # ── ⏱ 阶段计时汇总 (墙钟秒, sig4; 纯日志, golden-safe) ──
    _total = time.time() - _start
    logger.info("  ⏱ 阶段计时 (墙钟秒)")
    for _name, _dur in phase_durations.items():
        _share = pct4(_dur / _total) if _total > 0 else "—"
        logger.info(f"     · {_name}: {sig4(_dur)}s ({_share})")
    logger.info(f"     · 总计: {sig4(_total)}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
