"""v7 schema 翻译层单测 (R5-A + R8-B)

验证 tone_llms.py 内联翻译层把 LLM 输出 '象征性' (W&Z 1994/1998 ASQ symbolic)
映射为 parquet 值域 '描述性'，以兼容 v6 panel 列后缀 _desc 与 Stata 变量名。

设计原则:
    - prompt 层用 W&Z 顶刊术语 (实质性 / 象征性)
    - parquet 落地用 v6 值域 (实质性 / 描述性)
    - codebook 在 docs/methodology/prompt_terminology_mapping.md 显式说明
      _desc 后缀在 v7 起的 symbolic 解读
"""
import json

import pytest


def _make_response(substantiveness_value: str) -> str:
    """构造 v7 schema 的 LLM JSON 响应。"""
    return json.dumps({
        "is_bank_fintech_news": True,
        "sentiment": "中性",
        "verification_confidence": 0.9,
        "sentiment_confidence": 0.8,
        "fintech_topic": "数字人民币",
        "innovation_locus": "底层技术",
        "innovation_locus_confidence": 0.85,
        "innovation_substantiveness": substantiveness_value,
        "innovation_substantiveness_confidence": 0.75,
    }, ensure_ascii=False)


@pytest.fixture(scope="module")
def models():
    return [
        {"short_name": "gpt54nano",   "model_name": "gpt-5.4-nano"},
        {"short_name": "gemini31111", "model_name": "gemini-3.1-flash-lite-preview"},
        {"short_name": "deepseekv4",  "model_name": "deepseek-v4-flash"},
    ]


def test_translation_symbolic_to_descriptive(models):
    """LLM 输出 '象征性' → 翻译为 '描述性' 进入下游聚合。"""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track

    model_res = {m["model_name"]: _make_response("象征性") for m in models}
    result = _aggregate_track(model_res, models)
    innov_substs = result[11]  # 第 12 元素 (translation 后值域)
    assert all(v == "描述性" for v in innov_substs), \
        f"翻译层失效: 期望全部 '描述性'，实际 {innov_substs}"
    assert "象征性" not in innov_substs


def test_translation_substantive_unchanged(models):
    """LLM 输出 '实质性' → 保持 '实质性' (翻译层不动)。"""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track

    model_res = {m["model_name"]: _make_response("实质性") for m in models}
    result = _aggregate_track(model_res, models)
    innov_substs = result[11]
    assert all(v == "实质性" for v in innov_substs)


def test_translation_invalid_value_skipped(models):
    """LLM 输出非合法值 → 不进入投票 (现有 schema 过滤)。"""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track

    model_res = {m["model_name"]: _make_response("未知") for m in models}
    result = _aggregate_track(model_res, models)
    innov_substs = result[11]
    assert len(innov_substs) == 0, f"非法值应被丢弃，实际 {innov_substs}"


def test_translation_preserves_descriptive_legacy(models):
    """向后兼容: 若 LLM 偶尔输出 '描述性' (v6 习惯)，直接保留 (翻译层幂等)。"""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track

    model_res = {m["model_name"]: _make_response("描述性") for m in models}
    result = _aggregate_track(model_res, models)
    innov_substs = result[11]
    assert all(v == "描述性" for v in innov_substs)


def test_per_model_confidence_recorded(models):
    """v7 R6-H: per-model innovation_*_confidence 应记录在 per_model_parsed。"""
    from news_process.pipeline.sentiment.tone_llms import _aggregate_track

    model_res = {m["model_name"]: _make_response("实质性") for m in models}
    result = _aggregate_track(model_res, models)
    per_model_parsed = result[8]
    for m in models:
        short = m["short_name"]
        assert per_model_parsed.get(f"{short}_innovation_substantiveness_confidence") == 0.75
        assert per_model_parsed.get(f"{short}_innovation_locus_confidence") == 0.85
