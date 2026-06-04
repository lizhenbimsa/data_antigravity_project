from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _source(relative_path: str) -> str:
    return (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")


def test_sentiment_stage_lineage_uses_actual_upstream_paths():
    """Guard against lineage metadata drifting away from real stage inputs."""
    tone_words = _source("pipeline/sentiment/tone_words.py")
    assert "input_files=[input_path]" in tone_words

    tone_berts = _source("pipeline/sentiment/tone_berts.py")
    assert "input_files=[input_path]" in tone_berts

    herd_decay = _source("pipeline/sentiment/herd_decay.py")
    assert "input_filename = filenames.get('output_23_bert_tone'" in herd_decay
    assert "input_files=[input_file]" in herd_decay
    assert "CONFIG['filenames']['output_21_tone_llms']" not in herd_decay


def test_fintech_intensity_lineage_records_both_stage12_inputs():
    fintech_intensity = _source("pipeline/filtering/fintech_intensity.py")
    assert "input_files=[full_path, input_file]" in fintech_intensity


# ── audit-fixes 2026-05-29: 守卫本次新增/修正的三处 fan-in 血缘记录 ──
# (final sign-off 发现: 这三处是最新改动却无回归测试, 静默 revert 不可察)

def test_stage45_panel_lineage_records_full_fanin():
    """Stage 45 面板导出须记硬上游闭包 24+15 (panel 级 fan-in)。

    2026-05-29 双模型重构: 原 stage 30 (30_text2vec_indicators) 已退役, 其 t2v 列
    改由 stage 15/25 内联双模型产出, 不再是独立上游 parquet, 故从血缘闭包移除。
    """
    export = _source("pipeline/panel/export.py")
    assert "_fn['output_24_herd_decay']" in export
    assert "_fn.get('output_15_article_alignment'" in export
    # stage 30 已退役: 不再作为 panel 上游 parquet 出现在 input_files 闭包
    assert "os.path.join(_od, '30_text2vec_indicators.parquet')" not in export
    # panel save 用 list 闭包变量
    assert "input_files=input_files)" in export


def test_stage45_article_lineage_is_stage24_only():
    """文章级 df_exploded 仅依赖 stage 24; 不得过度归因 15/30 (panel 级 merge)。"""
    export = _source("pipeline/panel/export.py")
    # article save 用单输入 [input_file] (revert 到 list 闭包会使此断言失败)
    assert "input_files=[input_file])" in export


def test_stage51_falsification_lineage_records_three_inputs():
    """Stage 51 是 3-way fan-in (12_fintech_full + 40_article_bank + 40_panel)。"""
    controls = _source("pipeline/falsification/controls.py")
    assert "_fn['output_40_panel_yearly']" in controls
    assert "_fn.get('output_12_fintech_full'" in controls
    assert "_fn.get('output_40_article_bank'" in controls


def test_attention_media_lineage_uses_real_source():
    """注意力指数源是 12_fintech_news_full (此前误记 24_herd_decay, mis-attribution)。"""
    attn = _source("pipeline/panel/attention_media.py")
    assert "CONFIG['filenames'].get('output_12_fintech_full'" in attn
