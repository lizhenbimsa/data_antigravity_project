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


def test_text2vec_lineage_uses_stage14_input():
    text2vec = _source("validation/text2vec.py")
    assert "input_path = os.path.join(output_dir, '14_fintech_intensity.parquet')" in text2vec
    assert "input_files=[input_path]" in text2vec


def test_fintech_intensity_lineage_records_both_stage12_inputs():
    fintech_intensity = _source("pipeline/filtering/fintech_intensity.py")
    assert "input_files=[full_path, input_file]" in fintech_intensity
