"""tests/integration/test_panel_reproducibility.py — Phase 2g 验收门槛。

校验: 磁盘 ``data/processed/`` 上当前存在的各 parquet, 其**逐列取值哈希**
须与 Phase 0 基线 ``golden_panel_v0.json`` 一致。任一列哈希不一致,
即提示重构可能已改变下游数据语义, 应考虑回滚至 ``phase-1-baseline``
(或更早相关 baseline tag)。

Phase 8 (2026-05-04): 物理目录自 ``data_processed/`` 迁至 ``data/processed/``;
``data_dir`` fixture 已指向新路径。

本检查为**仅列级哈希**比对 (重整方案 Phase 2g 规约)。相对 ``assert_frame_equal``
仅采用哈希的理由:
  - Phase 0 基线仅存哈希 (无完整 DataFrame), 无法做结构级相等断言。
  - 哈希方案向前兼容: 若未来 Phase 2e 将布局细分为 ``data/processed/<group>/``,
    本测试仅需调整路径解析, 无需整表重快照。

行为概要:
  - 对 golden 中已登记且磁盘存在的各阶段 parquet, 重算列哈希并与基线比对。
  - 列哈希不一致 → 测试失败并输出诊断差分。
  - golden 中缺失某阶段记录时 → 跳过并附说明 (Phase 0 快照时曾
    ``incomplete=true``, 例如阶段 15 当时无产出)。
  - 磁盘存在而 golden 未收录的阶段 → 同样跳过 (常见于 Phase 0 之后重跑某阶段、
    未同步重快照的情形)。

白话: golden 快照相当于给每个数据文件的每一列拍了张"指纹照" (哈希值)。
本测试重算当前磁盘文件每列的指纹, 和老照片逐一对比 — 任何一列的数据
哪怕变了一个值, 指纹就对不上, 测试立刻失败。这是防止重构悄悄改坏数据
的最后一道门禁; 故意改 schema 后需要重新生成 golden 快照。
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _column_hash(s: pd.Series) -> str:
    """pandas 列取值哈希的无符号 64 位十六进制摘要。"""
    h = int(pd.util.hash_pandas_object(s, index=False).sum())
    return f"{h & ((1 << 64) - 1):016x}"


@pytest.fixture(scope="module")
def golden() -> dict:
    """加载 Phase 0 基线快照 JSON。"""
    fixture_path = (_project_root() / "tests" / "fixtures"
                    / "golden_panel_v0.json")
    if not fixture_path.exists():
        pytest.skip(
            f"未找到 Phase 0 基线文件 {fixture_path}; "
            "请先运行: python news_process/scripts/migrate/generate_golden_snapshot.py"
        )
    with fixture_path.open(encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def data_dir() -> Path:
    """解析 parquet 产出根目录 (Phase 8: ``data_processed`` → ``data/processed``)。"""
    return _project_root() / "data" / "processed"


def _stages_present(golden: dict, data_dir: Path) -> list[str]:
    """同时在 golden 快照与磁盘上存在的阶段文件名列表。"""
    return [
        name for name in golden.get("stages", {})
        if (data_dir / name).is_file()
        and "error" not in golden["stages"][name]
        and "column_hashes" in golden["stages"][name]
    ]


def test_golden_snapshot_has_content(golden):
    """健全性: 快照须至少包含一个已建索引列哈希的阶段。"""
    stages = golden.get("stages", {})
    assert stages, "golden_panel_v0.json 中无任何阶段记录"
    indexed = sum(1 for s in stages.values() if "column_hashes" in s)
    assert indexed > 0, "golden 快照中没有任何阶段含 column_hashes"


def test_golden_stages_subset_of_registry_or_orphan_whitelist(golden):
    """audit S9 漂移闸门 (2026-05-30): golden 追踪的每个 stage 必须 ∈
    OUTPUT_REGISTRY 的 .parquet 产物 ∪ 已知 orphan 白名单。

    防止 OUTPUT_REGISTRY / golden EXPECTED_STAGES / 本文件 parametrize 三份手抄
    stage 清单再次漂移到无人发现。orphan 白名单为已知无生产者产物 (待正式处置:
    确认废弃→从 golden 移除 / 否则补回生产 stage)。
    """
    from news_process.core.schemas import OUTPUT_REGISTRY
    registry_parquets = {
        f for files in OUTPUT_REGISTRY.values() for f in files
        if f.endswith('.parquet')
    }
    # 与 generate_golden_snapshot._ORPHAN_WHITELIST 保持同步
    known_orphans = {
        "30_text2vec_indicators.parquet",
        # 41_panel_with_controls.parquet 已删除 (2026-05-30): 无生产者孤儿 + 含已移除模型列。
    }
    allowed = registry_parquets | known_orphans
    golden_stages = set(golden.get("stages", {}).keys())
    drift = golden_stages - allowed
    assert not drift, (
        f"golden_panel_v0.json 追踪了 OUTPUT_REGISTRY/orphan 白名单外的 stage: "
        f"{sorted(drift)} — 三份清单漂移, 见 audit S9。新增产物请登记 OUTPUT_REGISTRY; "
        f"确认 orphan 请加入白名单并注明处置计划。"
    )


@pytest.mark.parametrize("stage_filename", [
    "00_preprocessing.parquet",
    "11_bank_news.parquet",
    "12_fintech_news.parquet",
    "12_fintech_news_full.parquet",
    "13_cooccurrence_filtered.parquet",
    "15_fintech_intensity.parquet",
    "21_tone_llms.parquet",
    "21_tone_llms_full.parquet",
    "22_words_tone.parquet",
    "23_bert_tone.parquet",
    "24_herd_decay.parquet",
    "30_text2vec_indicators.parquet",
    "40_panel_yearly.parquet",
    "40_article_bank_level.parquet",
    "40_attn_index_year.parquet",
    "40_attn_index_province_year.parquet",
    "40_attn_index_city_year.parquet",
    "51_panel_with_controls.parquet",
])
def test_column_hashes_match_golden(stage_filename, golden, data_dir):
    """逐列取值哈希须与 Phase 0 基线一致。

    若磁盘无该阶段 parquet (Phase 0 不完整), 或 golden 中无该阶段记录
    (例如 Phase 0 之后新增阶段而未重快照), 则跳过。
    """
    parquet_path = data_dir / stage_filename
    if not parquet_path.is_file():
        pytest.skip(f"磁盘上不存在该阶段 parquet: {stage_filename}")

    stage_record = golden.get("stages", {}).get(stage_filename)
    if not stage_record or "column_hashes" not in stage_record:
        pytest.skip(
            f"golden 快照缺少阶段 {stage_filename} "
            "(生成快照时该阶段尚未存在或未写入 column_hashes)"
        )

    expected_hashes: dict = stage_record["column_hashes"]
    expected_columns: list = stage_record.get("columns_order", list(expected_hashes.keys()))

    df = pd.read_parquet(parquet_path)

    # 列集合一致性
    df_cols = set(df.columns)
    expected_cols = set(expected_columns)
    extra = df_cols - expected_cols
    missing = expected_cols - df_cols
    assert not extra and not missing, (
        f"{stage_filename}: 列集合漂移\n"
        f"  磁盘新增 (golden 无):   {sorted(extra)[:10]}\n"
        f"  golden 有而磁盘缺: {sorted(missing)[:10]}"
    )

    # 逐列哈希比对
    mismatches = []
    for col in expected_columns:
        actual = _column_hash(df[col])
        expected = expected_hashes[col]
        if actual != expected:
            mismatches.append((col, expected, actual))

    if mismatches:
        details = "\n".join(
            f"  {col!r}: 基线={exp}  当前={act}"
            for col, exp, act in mismatches[:10]
        )
        n_more = len(mismatches) - 10
        suffix = f"\n  ... 另有 {n_more} 处不一致" if n_more > 0 else ""
        pytest.fail(
            f"{stage_filename}: {len(mismatches)} 处列哈希不一致\n"
            f"{details}{suffix}\n"
            f"  Phase 2 级重构可能已改变下游数据; 可考虑回滚至 phase-1-baseline。"
        )
