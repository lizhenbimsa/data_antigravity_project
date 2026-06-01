"""tests/integration/test_bert_panel_invariant.py — Wave 4 fail-fast invariant.

Catches the "stage 23 silently drops a BERT model" failure mode at test time
rather than at panel construction time.

Concrete failure mode (originally observed 2026-05-13 in Wave 0/1 finalization):
  - config/sentiment.yaml lists 3 BERT models (finbert_cn / fin_sent_zh /
    finbert2).
  - If HuggingFace huggingface.co is unreachable from the dev machine, a
    model whose weights are uncached locally graceful-skips while the
    cached ones succeed.
  - Such a silent skip drops that model's columns from the stage 23 output.
  - Downstream panel encode (pipeline/panel/encode.py:63) reads BERT_MODELS
    from the SAME config; trying to read a dropped `<model>_label_ctx` would
    KeyError ~30 min later. This test catches it in <1s.

The invariant: for every model declared in `tone_berts.models`, the stage 23
parquet must contain its 2 label columns: `{short_name}_label_{ctx,full}`
(remove-title-track 后 BERT 收为 _full/_ctx 双轨).

The test auto-skips when 23_bert_tone.parquet is absent (CI light/CI full
both have `data/processed/` .gitignored) and is auto-marked `integration`.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PARQUET = REPO_ROOT / "news_process" / "data" / "processed" / "23_bert_tone.parquet"
SENTIMENT_YAML = REPO_ROOT / "news_process" / "config" / "sentiment.yaml"


def _configured_bert_short_names() -> list[str]:
    """Read sentiment.yaml -> tone_berts.models -> list of short_name."""
    with SENTIMENT_YAML.open(encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}
    models = (
        cfg.get("sentiment_analysis", {})
        .get("tone_berts", {})
        .get("models", [])
    )
    return [m["short_name"] for m in models if isinstance(m, dict) and "short_name" in m]


@pytest.fixture(scope="module")
def bert_parquet() -> pd.DataFrame:
    if not PARQUET.exists():
        pytest.skip(f"stage 23 output absent (data/processed/ gitignored): {PARQUET}")
    return pd.read_parquet(PARQUET)


def test_every_configured_bert_model_has_label_columns(bert_parquet):
    """每个 config 列出的 BERT model 必须在 stage 23 输出里有 label_{ctx,full} (remove-title-track 后双轨).

    若某个 model 因 HF 不可达 graceful skip, 此 test 立刻报错; 不会让缺失
    传到 stage 45 才以 KeyError 形式炸 ~30min 后。
    """
    expected = _configured_bert_short_names()
    assert expected, "sentiment.yaml::tone_berts.models 为空, 配置自身有问题"

    missing_per_model: dict[str, list[str]] = {}
    for short_name in expected:
        required = [f"{short_name}_label_{ctx}" for ctx in ("ctx", "full", "title")]
        absent = [c for c in required if c not in bert_parquet.columns]
        if absent:
            missing_per_model[short_name] = absent

    if missing_per_model:
        lines = ["stage 23 输出缺失 BERT label 列, 下游 panel encode 会 KeyError:"]
        for name, cols in missing_per_model.items():
            lines.append(f"  - model={name!r}: missing {cols}")
        lines.append(
            "可能原因: HuggingFace 不可达 + 该模型未本地缓存 (见 ~/.claude/memory/hf_network.md), "
            "或 config 改了 short_name 没同步重跑 stage 23."
        )
        pytest.fail("\n".join(lines))


def test_bert_label_columns_have_no_all_null_rows(bert_parquet):
    """label 列至少含一个非空值 — 防止"全 NaN" 静默退化.

    如果模型加载成功但推理全失败 (e.g. cuda OOM 跳过 fallback), parquet
    schema 完整但所有 row 都 NaN. 此 test 强制每个 model 的 ctx 上下文
    至少有一个 row 非空, 确保推理真的发生过.
    """
    expected = _configured_bert_short_names()
    null_models: list[str] = []
    for short_name in expected:
        col = f"{short_name}_label_ctx"
        if col not in bert_parquet.columns:
            continue  # 由上一个 test 报缺失; 这里只看存在的
        if bert_parquet[col].notna().sum() == 0:
            null_models.append(short_name)

    if null_models:
        pytest.fail(
            f"以下 BERT model 的 {{}}_label_ctx 列全为 NaN, 推理可能完全失败: "
            f"{null_models}"
        )
