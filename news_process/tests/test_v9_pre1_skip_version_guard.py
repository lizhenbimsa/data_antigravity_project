"""V9-PRE-1 gate: stage 21 skip 守卫的 prompt 版本盲区修复。

背景: `run_pipeline_function.py::_stage21_skip_is_compatible` (--skip-21-if-exists 的
安检函数) 此前只比对上游 stage14 输入与既有 stage21 输出的行数/内容指纹, 对"这些
parquet 是拿哪个版本的 prompt 生成的"完全失明。v9 prompt 升级落地后, 若不修这个盲区,
旧 v8 parquet 会被 skip 守卫原样放行, 下游 (stage 22/23/40...) 静默消费过期标签。

构造: 写侧 (`tone_llms.py` 的两处 `save_dataset` 调用) 现附加
`extra_schema_metadata={b"news_process.prompt_version": PROMPT_VERSION.encode()}`,
经 `save_parquet_with_metadata` 落进 parquet 的 pyarrow schema metadata (非数据列,
golden-safe)。读侧 `_read_stage21_prompt_version` 取回该值; metadata 缺失 (legacy
parquet, 必产于本修复落地前) 时兜底假定 `_STAGE21_LEGACY_PROMPT_VERSION`
('v8-2026-05-17')。`_stage21_skip_is_compatible` 用这一读数与当前
`tone_llms.PROMPT_VERSION` 比较, 不等则 reject skip。

设计: 四条读侧分支 (对应真实运行时会遇到的四种 parquet 状态) + 一条写侧回归 (确认附加
metadata 不改变列数据字节)。

防误用铁律: 本文件全程用 tmp_path 造小 fixture parquet, 绝不触碰 data/processed/ 下
的真实盘上产物; 涉及"当前 PROMPT_VERSION" 的分支用 monkeypatch 覆盖
`tone_llms.PROMPT_VERSION` 而非改动真实 config/prompts/unified_cot.txt (改那个文件
会字节级废缓存, 见 CLAUDE.md v9 升级纪律)。

白话: 这组测试确保"要不要跳过昂贵的 LLM 阶段"这个安检, 除了看数据对不对得上, 也会
先看"这批数据是不是用现在这版提示词跑出来的"——版本不对就老老实实重跑, 不会拿旧提示
词的答案冒充新提示词的答案。
"""

from __future__ import annotations

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

import news_process.pipeline.sentiment.tone_llms as tone_llms_mod
import news_process.run_pipeline_function as rpf
from news_process.core.data_versioning import save_parquet_with_metadata
from news_process.tests.test_run_pipeline_function import _patch_config, _stage14_df

_PV_KEY = rpf._STAGE21_PROMPT_VERSION_METADATA_KEY


def _write_parquet(path, df: pd.DataFrame, prompt_version: str | None = None) -> None:
    """写 parquet, 可选附加 prompt_version schema metadata (镜像 tone_llms.py 写侧路径)。"""
    table = pa.Table.from_pandas(df, preserve_index=False)
    if prompt_version is not None:
        existing = table.schema.metadata or {}
        merged = {**existing, _PV_KEY: prompt_version.encode("utf-8")}
        table = table.cast(table.schema.with_metadata(merged))
    pq.write_table(table, path)


def _write_stage21_fixture(
    tmp_path,
    *,
    main_prompt_version: str | None = None,
    full_prompt_version: str | None = None,
) -> None:
    """构造一套通过既有指纹/schema 校验的 stage14 + stage21(main/full) parquet 三件套。

    行数/内容指纹/_STAGE21_REQUIRED_OUTPUT_COLUMNS 全部对齐 (镜像
    test_run_pipeline_function.py::test_stage21_skip_is_compatible_accepts_current_outputs
    的构造), 使得除 prompt_version 外的既有校验一律通过 —— 这样任何 reject 都可
    唯一归因于版本校验分支, 不会被其它既有检查的假阳性污染判读。
    """
    stage14 = _stage14_df(2)
    _write_parquet(tmp_path / "15_fintech_intensity.parquet", stage14)

    full = stage14.copy()
    full["llm_verified_full"] = [True, False]
    full["llm_verified_ctx"] = [False, True]
    for col in rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS:
        full[col] = "symbolic"
    _write_parquet(
        tmp_path / "21_tone_llms_full.parquet", full, prompt_version=full_prompt_version
    )

    main_keep = full[full["llm_verified_full"] == True]  # noqa: E712 - pandas boolean mask
    main_df = main_keep[
        list(rpf._STAGE21_FILTERED_FINGERPRINT_COLUMNS)
        + list(rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS)
    ]
    _write_parquet(
        tmp_path / "21_tone_llms.parquet", main_df, prompt_version=main_prompt_version
    )


# ---------------------------------------------------------------------------
# 读侧: 四分支
# ---------------------------------------------------------------------------


def test_branch_a_present_and_matches_current_is_compatible(monkeypatch, tmp_path):
    """分支 (a): metadata 存在且与当前 PROMPT_VERSION 一致 → 版本校验通过, 整体兼容。"""
    _patch_config(monkeypatch, tmp_path)
    current = tone_llms_mod.PROMPT_VERSION
    _write_stage21_fixture(tmp_path, main_prompt_version=current, full_prompt_version=current)

    ok, reason = rpf._stage21_skip_is_compatible(
        ["21_tone_llms.parquet", "21_tone_llms_full.parquet"]
    )

    assert ok is True
    assert "mismatch" not in reason


def test_branch_b_present_but_mismatched_rejects_skip(monkeypatch, tmp_path):
    """分支 (b): metadata 存在但与当前 PROMPT_VERSION 不同 → reject, reason 含双方版本号。"""
    _patch_config(monkeypatch, tmp_path)
    _write_stage21_fixture(
        tmp_path, main_prompt_version="v7-2025-01-01", full_prompt_version="v7-2025-01-01"
    )

    ok, reason = rpf._stage21_skip_is_compatible(
        ["21_tone_llms.parquet", "21_tone_llms_full.parquet"]
    )

    assert ok is False
    assert "prompt_version mismatch" in reason
    assert "v7-2025-01-01" in reason
    assert tone_llms_mod.PROMPT_VERSION in reason


def test_branch_c_missing_metadata_and_current_is_legacy_v8_is_compatible(
    monkeypatch, tmp_path, caplog
):
    """分支 (c): metadata 缺失 (legacy parquet) + 当前 PROMPT_VERSION == 'v8-2026-05-17'
    (今日实况, grandfather 条款) → 兜底假定 legacy=v8 后二者相等 → 兼容; 且必须打印
    warning 留痕 (§0-5 注释/日志同步纪律: 静默兜底本身不是错误, 但须可见)。
    """
    _patch_config(monkeypatch, tmp_path)
    assert tone_llms_mod.PROMPT_VERSION == rpf._STAGE21_LEGACY_PROMPT_VERSION, (
        "本用例断言今日 PROMPT_VERSION 仍是历史 legacy sentinel (v8-2026-05-17); "
        "若 v9 已落地此断言会先失败, 提示需要更新本测试的前置假设 (预期内变化)"
    )
    _write_stage21_fixture(tmp_path)  # 不传 prompt_version → 两份都无 metadata (legacy)

    # rpf.logger 由 core/logging.py::setup_logging 配置 propagate=False (阶段日志不
    # 冒泡到 root), caplog 默认挂在 root logger 上收不到 —— 直接把 caplog.handler
    # 挂到 rpf.logger 自身 (不受 propagate 影响, 只影响向上冒泡而非本 logger 自己的
    # handler 触发), 用完即拆, 不污染其它测试。
    rpf.logger.addHandler(caplog.handler)
    try:
        with caplog.at_level("WARNING", logger="news_process.run_pipeline_function"):
            ok, reason = rpf._stage21_skip_is_compatible(
                ["21_tone_llms.parquet", "21_tone_llms_full.parquet"]
            )
    finally:
        rpf.logger.removeHandler(caplog.handler)

    assert ok is True
    assert any(
        "缺 prompt_version schema metadata" in rec.message for rec in caplog.records
    ), "legacy 兜底分支必须打 warning 留痕, 不能纯静默"


def test_branch_c_prime_missing_metadata_but_current_is_future_v9_rejects(
    monkeypatch, tmp_path
):
    """分支 (c) 的镜像反例: metadata 缺失, 但当前 PROMPT_VERSION 已 monkeypatch 为假想
    v9 → legacy 兜底值 ('v8-2026-05-17') != 假想 v9 → reject skip。这是本修复的核心
    承诺: v9 落地后, 旧 v8 parquet 不会被 --skip-21-if-exists 静默放行。
    """
    _patch_config(monkeypatch, tmp_path)
    monkeypatch.setattr(tone_llms_mod, "PROMPT_VERSION", "v9-2099-01-01")
    _write_stage21_fixture(tmp_path)  # 不传 prompt_version → legacy (无 metadata)

    ok, reason = rpf._stage21_skip_is_compatible(
        ["21_tone_llms.parquet", "21_tone_llms_full.parquet"]
    )

    assert ok is False
    assert "prompt_version mismatch" in reason
    assert "v9-2099-01-01" in reason
    assert rpf._STAGE21_LEGACY_PROMPT_VERSION in reason


def test_branch_d_schema_read_failure_is_conservative_reject(monkeypatch, tmp_path):
    """分支 (d): parquet schema 本身读取失败 (文件损坏/非法内容) → 保守 reject, 不上抛。"""
    _patch_config(monkeypatch, tmp_path)
    # 让 15_fintech_intensity.parquet 存在与否不重要 —— 版本校验先于上游指纹比对执行,
    # 这里只需 main/full 两个"parquet"文件 os.path.exists 为真, 内容非法即可触发 (d)。
    (tmp_path / "21_tone_llms_full.parquet").write_bytes(b"not a real parquet file")
    (tmp_path / "21_tone_llms.parquet").write_bytes(b"not a real parquet file either")

    ok, reason = rpf._stage21_skip_is_compatible(
        ["21_tone_llms.parquet", "21_tone_llms_full.parquet"]
    )

    assert ok is False
    assert "failed to read stage 21" in reason
    assert "prompt_version metadata" in reason


# ---------------------------------------------------------------------------
# 写侧: 附加 metadata 不改变列数据字节
# ---------------------------------------------------------------------------


def test_write_side_extra_metadata_is_byte_identical_on_columns(tmp_path):
    """save_parquet_with_metadata 附加 extra_schema_metadata 后, 用 pandas 读回的
    DataFrame 必须与不附加时逐字节 (逐值) 相等 —— 只多一条 schema metadata, 不动任何
    数据列 (golden-safe 的核心承诺)。
    """
    df = pd.DataFrame(
        {
            "docid": ["D0", "D1", "D2"],
            "llm_sentiment_full": ["正面", "负面", "中性"],
            "llm_prob_score": [0.5, -0.3, 0.0],
        }
    )
    config = {"dummy": "config"}

    path_without = tmp_path / "no_extra_metadata.parquet"
    path_with = tmp_path / "with_extra_metadata.parquet"

    save_parquet_with_metadata(
        df=df,
        output_path=path_without,
        stage_name="test_v9_pre1",
        config=config,
    )
    save_parquet_with_metadata(
        df=df,
        output_path=path_with,
        stage_name="test_v9_pre1",
        config=config,
        extra_schema_metadata={_PV_KEY: b"v8-2026-05-17"},
    )

    df_without = pd.read_parquet(path_without)
    df_with = pd.read_parquet(path_with)
    assert df_without.equals(df_with), "附加 extra_schema_metadata 不应改变任何列数据"
    assert df.equals(df_with), "写回读出的列数据必须与原始 df 逐值相等"

    schema_metadata = pq.read_schema(path_with).metadata
    assert schema_metadata is not None
    assert schema_metadata[_PV_KEY] == b"v8-2026-05-17"
    # 未附加 extra_schema_metadata 的一侧不应含该键 (纯 opt-in, 不污染既有调用方)。
    schema_metadata_without = pq.read_schema(path_without).metadata or {}
    assert _PV_KEY not in schema_metadata_without
