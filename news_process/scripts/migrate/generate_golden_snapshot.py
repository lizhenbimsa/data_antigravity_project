"""
generate_golden_snapshot.py — Phase 0 交付物

对 ``data/processed/`` (Phase 8 目录重命名) 下**当前磁盘上已存在**的全部
parquet 产物逐列计算值哈希, 并写入 ``tests/fixtures/golden_panel_v0.json``。

本脚本走**降级路径** Phase 0 快照 (见重整方案): **不**重跑主流水线,
仅对现存文件做哈希。若某预期阶段输出缺失, JSON 标记 ``"incomplete": true``;
Phase 2 的 ``test_panel_reproducibility.py`` 将仅对有基线的阶段列做比对。

哈希语义:
- 单列: ``hex(int(pd.util.hash_pandas_object(df[col], index=False).sum()))``
  的无符号 64 位十六进制表示 (见 ``column_hash``)。
- 同时记录行数、列数与 dtype 字典, 便于廉价结构 diff。
- **不**记录 parquet 文件字节级哈希 (pyarrow 元数据、Snappy 块边界、
  时间戳等在重复写出间不稳定)。

用法:
    python news_process/scripts/migrate/generate_golden_snapshot.py

白话: 给当前磁盘上每个 parquet 产物的每一列拍一张"数值指纹"存进 JSON 基线。
以后任何代码改动后重跑流水线, 测试拿新指纹和这份基线逐列比对 —— 指纹变了
就说明数据真的变了 (而不是文件时间戳之类的无关差异), 防止悄悄破坏结果。
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml

# 与 run_pipeline_function 管线阶段输出文件名对齐 (方案 §1)。
# 磁盘上可能仅存在子集; 缺失项使 ``incomplete`` 为 true。
#
# audit S9 修复 (2026-05-30): 从 core/schemas.py::OUTPUT_REGISTRY 单源派生, 消除
# 三份手抄 stage 清单 (OUTPUT_REGISTRY / 本 EXPECTED_STAGES / test_panel_reproducibility
# parametrize) 两两漂移。早期硬编码列表漏掉 v3.6-v3.7 新增 stage (13/16/17/18/19/30a/49),
# 下次 golden 重生 (deferred 到 production run) 时本派生自动覆盖之。
# (历史注: 其中 16/17/19/49 此后又被整体移除并从 OUTPUT_REGISTRY 注销 —— 单源派生
#  机制同样自动跟随, 无需改本脚本。)
# 白话: 期望文件清单不再手抄, 直接照抄注册表, 注册表加减 stage 这里自动同步。
from news_process.core.schemas import OUTPUT_REGISTRY  # noqa: E402

# 无生产 stage 的 orphan 产物: golden 历史追踪但 OUTPUT_REGISTRY 无登记。
# 待正式处置 (确认废弃 → 从 golden 移除 / 否则补回生产 stage)。
_ORPHAN_WHITELIST = [
    "30_text2vec_indicators.parquet",  # stage 30 已退役 (2026-05-29 双模型重构, 内联到 15/25)
    # 41_panel_with_controls.parquet 已删除 (2026-05-30): 无生产者孤儿, 且仍含已移除的
    # erlangshen/hw2942 列; 删除文件并移出白名单, OUTPUT_REGISTRY 仅 51_panel_with_controls。
]


def _derive_expected_stages() -> list[str]:
    """从 OUTPUT_REGISTRY 派生期望 .parquet 列表 + orphan 白名单 (去重保序)。"""
    seen: set[str] = set()
    result: list[str] = []
    for files in OUTPUT_REGISTRY.values():
        for fname in files:
            if fname.endswith('.parquet') and fname not in seen:
                seen.add(fname)
                result.append(fname)
    for fname in _ORPHAN_WHITELIST:
        if fname not in seen:
            seen.add(fname)
            result.append(fname)
    return result


EXPECTED_STAGES = _derive_expected_stages()


def column_hash(s: pd.Series) -> str:
    """单列取值经 pandas 哈希后的十六进制摘要 (忽略行索引)。"""
    h = int(pd.util.hash_pandas_object(s, index=False).sum())
    h_unsigned = h & ((1 << 64) - 1)
    return f"{h_unsigned:016x}"


def hash_parquet(path: Path) -> dict:
    """对单个 parquet 文件按列计算哈希及结构元数据。"""
    df = pd.read_parquet(path)
    return {
        "file": path.name,
        "size_bytes": path.stat().st_size,
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "columns_order": list(df.columns),
        "dtypes": {c: str(df[c].dtype) for c in df.columns},
        "column_hashes": {c: column_hash(df[c]) for c in df.columns},
    }


def _read_sentiment_models(project_root: Path) -> list[str]:
    """从 ``config/sentiment.yaml`` 返回 LLM 模型短名列表。

    直接读 ``tone_llm_processing.models`` (而非经 load_config), 使本迁移脚本
    不引入项目配置加载的副作用。
    """
    cfg_path = project_root / "config" / "sentiment.yaml"
    if not cfg_path.exists():
        return []
    try:
        with cfg_path.open(encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        models = cfg.get("tone_llm_processing", {}).get("models", []) or []
        return [
            m.get("short_name") or m.get("model_name")
            for m in models
            if isinstance(m, dict)
        ]
    except Exception:
        return []


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    # Phase 8 (2026-05-04): data_processed → data/processed
    data_dir = project_root / "data" / "processed"
    fixture_path = project_root / "tests" / "fixtures" / "golden_panel_v0.json"
    fixture_path.parent.mkdir(parents=True, exist_ok=True)

    if not data_dir.is_dir():
        print(f"错误: 未找到 data/processed/ 目录: {data_dir}", file=sys.stderr)
        return 2

    snapshot: dict = {
        "schema_version": 2,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_tag": "baseline-pre-restructure",
        "data_dir": str(data_dir.relative_to(project_root)),
        "hash_method": "pd.util.hash_pandas_object(s, index=False).sum() -> u64 hex",
        # v2 新增: 面向跨时间可复现性的 LLM 快照元数据。
        # 记录 golden 生成时刻的 LLM 模型阵容, 让未来的 diff 会话能区分
        # "数据漂移" 与 "LLM API 端点漂移"。
        "llm_snapshot_date": datetime.now(timezone.utc).date().isoformat(),
        "llm_models": _read_sentiment_models(project_root),
        "stages": {},
    }

    present = []
    missing = []
    for filename in EXPECTED_STAGES:
        path = data_dir / filename
        if not path.is_file():
            missing.append(filename)
            continue
        try:
            snapshot["stages"][filename] = hash_parquet(path)
            present.append(filename)
        except Exception as exc:  # noqa: BLE001 — 诊断性捕获
            snapshot["stages"][filename] = {
                "file": filename,
                "error": f"{type(exc).__name__}: {exc}",
            }
            missing.append(filename)

    snapshot["incomplete"] = len(missing) > 0
    snapshot["counts"] = {
        "expected": len(EXPECTED_STAGES),
        "present": len(present),
        "missing": len(missing),
    }
    snapshot["missing_stages"] = missing

    with fixture_path.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"已写入 {fixture_path.relative_to(project_root)}")
    print(f"  已存在: {len(present)} / {len(EXPECTED_STAGES)}")
    if missing:
        print(f"  缺失: {missing}")
        print("  incomplete = true (Phase 2 可复现性测试将跳过缺失阶段)")
    else:
        print("  incomplete = false (全覆盖)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
