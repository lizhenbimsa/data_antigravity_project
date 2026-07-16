from __future__ import annotations

import pandas as pd

import news_process.run_pipeline_function as rpf


def _stage14_df(n_rows: int = 2) -> pd.DataFrame:
    rows = []
    for idx in range(n_rows):
        # F7 (2026-07-16): 13 项与 _STAGE21_UPSTREAM_FINGERPRINT_COLUMNS 顺序严格
        # 对位 (在 '内容' 后插 content_ctx/content_ss/ctx_is_fallback/ss_is_fallback)
        values = [
            f"DOC{idx:03d}",
            f"PUB{idx:03d}",
            "BankA",
            "BankB",
            f"2025-01-{idx + 1:02d}",
            f"Title {idx}",
            f"Body {idx}",
            f"Ctx {idx}",
            f"SS {idx}",
            False,
            False,
            float(idx + 1),
            True,
        ]
        # 防 zip 静默截断 (R1 评审教训: 列扩后 zip 会静默丢新列致夹具错构)
        assert len(values) == len(rpf._STAGE21_UPSTREAM_FINGERPRINT_COLUMNS)
        rows.append(dict(zip(rpf._STAGE21_UPSTREAM_FINGERPRINT_COLUMNS, values)))
    return pd.DataFrame(rows)


def _patch_config(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        rpf,
        "CONFIG",
        {
            "paths": {"output_dir": str(tmp_path)},
            "filenames": {
                "output_14_fintech_intensity": "15_fintech_intensity.parquet",
            },
        },
    )


def test_stage21_skip_is_compatible_accepts_current_outputs(monkeypatch, tmp_path):
    _patch_config(monkeypatch, tmp_path)
    stage14 = _stage14_df(2)

    stage14.to_parquet(tmp_path / "15_fintech_intensity.parquet", index=False)
    full = stage14.copy()
    full["llm_verified_full"] = [True, False]
    # full-only gating (用户决策 2026-06-29; 逆转 v3.2.0 R1-A 并集): _stage21_skip_is_compatible
    # 留篇判据 = (verified_full == True) only, 与 tone_llms.py 的 df_filtered 留篇门控 producer 同步。
    # Test mock 保留 llm_verified_ctx 列且令 row 1 = ctx-only (full=False) —— full-only
    # 下 row 1 **被排除**, 故 main 只含 row 0 (full=True), 用以守卫 "ctx-only 行不再进
    # 下游样本" 的回归 (此前并集门会把 row 1 也纳入)。
    full["llm_verified_ctx"] = [False, True]
    # v3.7.1 (test drift fix): v3.2.0 dual-track BREAKING 后, _stage21_skip_is_compatible
    # 加 schema 漂移防护 (run_pipeline_function.py:289-306) — _STAGE21_REQUIRED_OUTPUT_COLUMNS
    # 缺失即 reject skip. test 必须 mock 这些 v3.2.0 双轨列才能 KEEP 兼容性.
    for col in rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS:
        full[col] = "symbolic"
    full.to_parquet(tmp_path / "21_tone_llms_full.parquet", index=False)
    # full-only: 只 row 0 (full=T) 进 main; row 1 (ctx-only, full=F) 被排除 → main 含 1 行。
    # (reason 里的 "N rows" 报的是 *上游 stage14* 行数 = 2, 非过滤后 main 行数。)
    main_keep = full[full["llm_verified_full"] == True]  # noqa: E712 - pandas boolean mask
    main_keep[list(rpf._STAGE21_FILTERED_FINGERPRINT_COLUMNS) + list(rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS)].to_parquet(
        tmp_path / "21_tone_llms.parquet",
        index=False,
    )

    ok, reason = rpf._stage21_skip_is_compatible(
        ["21_tone_llms.parquet", "21_tone_llms_full.parquet"]
    )

    assert ok is True
    assert "2 rows" in reason


def test_stage21_skip_is_compatible_rejects_stale_full_output(monkeypatch, tmp_path):
    _patch_config(monkeypatch, tmp_path)
    current_stage14 = _stage14_df(1)
    stale_full = _stage14_df(2)

    current_stage14.to_parquet(tmp_path / "15_fintech_intensity.parquet", index=False)
    stale_full["llm_verified_full"] = [True, False]
    stale_full.to_parquet(tmp_path / "21_tone_llms_full.parquet", index=False)
    stale_full.loc[[0], list(rpf._STAGE21_FILTERED_FINGERPRINT_COLUMNS)].to_parquet(
        tmp_path / "21_tone_llms.parquet",
        index=False,
    )

    ok, reason = rpf._stage21_skip_is_compatible(
        ["21_tone_llms.parquet", "21_tone_llms_full.parquet"]
    )

    assert ok is False
    assert "row count" in reason


def test_stage21_skip_rejects_ctx_ss_text_drift(monkeypatch, tmp_path):
    """F7 T1 (2026-07-16): 仅 content_ss 单字符差异 → reject — 轨道物化参数变更
    (如 ss_sentence_radius) 的指纹哨兵 (此前九列指纹对 ctx/ss 文本全盲误放行)。"""
    _patch_config(monkeypatch, tmp_path)
    stage14 = _stage14_df(2)
    full = _stage14_df(2)
    full["llm_verified_full"] = [True, False]
    full["llm_verified_ctx"] = [False, True]
    for col in rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS:
        full[col] = "symbolic"
    # 15 号侧 content_ss 改一字符 (模拟窗口参数变更后 stage 14 重物化)
    stage14.loc[0, "content_ss"] = stage14.loc[0, "content_ss"] + "改"
    stage14.to_parquet(tmp_path / "15_fintech_intensity.parquet", index=False)
    full.to_parquet(tmp_path / "21_tone_llms_full.parquet", index=False)
    main_keep = full[full["llm_verified_full"] == True]  # noqa: E712 - pandas boolean mask
    main_keep[list(rpf._STAGE21_FILTERED_FINGERPRINT_COLUMNS)
              + list(rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS)].to_parquet(
        tmp_path / "21_tone_llms.parquet", index=False)

    ok, reason = rpf._stage21_skip_is_compatible(
        ["21_tone_llms.parquet", "21_tone_llms_full.parquet"]
    )

    assert ok is False
    assert "fingerprint differs" in reason


def test_stage21_skip_legacy_missing_track_cols_rejects_gracefully(monkeypatch, tmp_path):
    """F7 T3 (2026-07-16): legacy 21_full 缺新指纹列 (content_ctx/ss + 回退位) →
    reject 且不抛未捕获异常 (与 REQUIRED_OUTPUT_COLUMNS 缺列同语义: 离线 $0 重放回填)。"""
    _patch_config(monkeypatch, tmp_path)
    stage14 = _stage14_df(2)
    stage14.to_parquet(tmp_path / "15_fintech_intensity.parquet", index=False)
    _new_cols = ("content_ctx", "content_ss", "ctx_is_fallback", "ss_is_fallback")
    legacy_cols = [c for c in rpf._STAGE21_UPSTREAM_FINGERPRINT_COLUMNS
                   if c not in _new_cols]
    legacy_full = stage14[legacy_cols].copy()
    legacy_full["llm_verified_full"] = [True, False]
    for col in rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS:
        legacy_full[col] = "symbolic"
    legacy_full.to_parquet(tmp_path / "21_tone_llms_full.parquet", index=False)
    main_keep = legacy_full[legacy_full["llm_verified_full"] == True]  # noqa: E712 - pandas boolean mask
    main_keep[list(rpf._STAGE21_FILTERED_FINGERPRINT_COLUMNS)
              + list(rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS)].to_parquet(
        tmp_path / "21_tone_llms.parquet", index=False)

    ok, reason = rpf._stage21_skip_is_compatible(
        ["21_tone_llms.parquet", "21_tone_llms_full.parquet"]
    )

    assert ok is False
    assert "failed to compare" in reason
