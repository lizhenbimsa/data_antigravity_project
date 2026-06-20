from __future__ import annotations

import pandas as pd

import news_process.run_pipeline_function as rpf


def _stage14_df(n_rows: int = 2) -> pd.DataFrame:
    rows = []
    for idx in range(n_rows):
        values = [
            f"DOC{idx:03d}",
            f"PUB{idx:03d}",
            "BankA",
            "BankB",
            f"2025-01-{idx + 1:02d}",
            f"Title {idx}",
            f"Body {idx}",
            float(idx + 1),
            True,
        ]
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
    # O2.5 修复 (2026-05-25): _stage21_skip_is_compatible 改 OR-filter 语义对齐
    # tone_llms.py:1744-1746 实际行为 (verified_full | verified_ctx since v3.2.0 R1-A).
    # Test mock 须含 llm_verified_ctx 列. row 0 verified_full=True, row 1 verified_ctx=True
    # → OR 后两行都进 main, 与原 AND-only test 期待 1 row 差异.
    full["llm_verified_ctx"] = [False, True]
    # v3.7.1 (test drift fix): v3.2.0 dual-track BREAKING 后, _stage21_skip_is_compatible
    # 加 schema 漂移防护 (run_pipeline_function.py:289-306) — _STAGE21_REQUIRED_OUTPUT_COLUMNS
    # 缺失即 reject skip. test 必须 mock 这些 v3.2.0 双轨列才能 KEEP 兼容性.
    for col in rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS:
        full[col] = "symbolic"
    full.to_parquet(tmp_path / "21_tone_llms_full.parquet", index=False)
    # OR-filter: 两行都满足 (row 0 full=T, row 1 ctx=T) → main 含全部 2 行
    full[list(rpf._STAGE21_FILTERED_FINGERPRINT_COLUMNS) + list(rpf._STAGE21_REQUIRED_OUTPUT_COLUMNS)].to_parquet(
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
