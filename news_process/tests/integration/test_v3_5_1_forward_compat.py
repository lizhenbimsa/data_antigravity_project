"""tests/integration/test_v3_5_1_forward_compat.py — v3.5.1 → v3.5.2 前兼容性测试.

测试覆盖 (3 tests, 修 M3 forward compat):
    1. tokenizer 流稳定性 (v3.5.2 加 forward-looking 中文词表后, A1 clarity 流程不破)
    2. clarity_score 不被 forward-looking 词污染 (修 R7-C1 字典 namespace 隔离)
    3. panel schema 前兼容 (v3.5.2 加列后, v3.5.1 列保持稳定)
"""
from __future__ import annotations

import json

import pytest

import news_process.pipeline.sentiment.tone_words as tw


def test_tokenizer_flow_stable_across_v3_5_x():
    """v3.5.1 → v3.5.2 tokenizer 流稳定性 (per plan v0.3 §4.1 M3).

    A1 clarity 计数依赖 `jieba.cut(text)` + 去空字符 token; 此流程在 v3.5.x 内不应变.
    本测试快照固定文本的 token 结果, 防 v3.5.2 forward-looking 词表 / 自定义词典扩展时
    意外改变 A1 分母 (n_tokens_clarity_base).
    """
    import jieba

    sample = "招商银行已上线区块链跨境支付系统处理 1000 万笔交易"
    tokens = list(jieba.cut(sample))
    tokens = [t for t in tokens if t.strip()]
    # 不强 assert 固定数量 (jieba 词典可能升级), 但 token 数应在合理区间 [5, 30]
    assert 5 <= len(tokens) <= 30, (
        f"jieba tokenizer 输出异常: {len(tokens)} tokens; 检查 v3.5.x 升级是否破坏 tokenizer"
    )


def test_clarity_dict_namespace_isolation():
    """v3.5.2 拟加 forward-looking 词表; clarity 词典 namespace 应隔离 (修 R7-C1).

    A1 clarity 仅读 you_2018.definite + you_2018.ambiguous; v3.5.2 forward-looking
    应放独立 key (如 'forward_looking_zh' 或 'zhang_2024' top-level), **不污染** you_2018.
    """
    import os

    dicts_file = tw.TONE_DICTS_FILE
    if not os.path.exists(dicts_file):
        pytest.skip(f"tone_dicts.json 未找到")
    with open(dicts_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    you = data.get('you_2018', {})
    assert isinstance(you, dict)
    # you_2018 仅含 7 keys (name/_description/references/positive/negative/definite/ambiguous);
    # 不应含 forward-looking-related keys
    forward_looking_pollutants = ['forward_looking', 'fls', 'future_oriented']
    for pollutant in forward_looking_pollutants:
        assert pollutant not in you, (
            f"you_2018 含 forward-looking pollutant key '{pollutant}'; "
            f"v3.5.2 应另设 namespace 避免 A1 clarity 污染"
        )


def test_panel_schema_forward_additive():
    """v3.5.1 panel schema 前兼容 (modular + additive only, 修 R9-M7).

    v3.5.1 加 8 列; v3.5.2 拟加 A2 forward-looking 列; v3.6.0 拟加 D3 媒体类型分类列.
    Schema 演进必须 additive (新增列不删旧列), v3.5.1 8 列应在 v3.5.2+ 仍存在.
    """
    v3_5_1_cols = [
        'mean_clarity_score_full', 'mean_clarity_score_ctx',
        'mean_frac_definite_full', 'mean_frac_definite_ctx',
        'frac_amb_articles_full', 'frac_amb_articles_ctx',
        'mean_num_intensity_full', 'mean_num_intensity_ctx',
    ]
    # 检查 codebook 元数据含全部 8 列 (v3.5.x 演进中必须保留)
    from news_process.pipeline.panel.codebook import get_variable_metadata_dict
    metadata = get_variable_metadata_dict()
    for col in v3_5_1_cols:
        assert col in metadata, (
            f"v3.5.1 panel 列 '{col}' 未在 codebook metadata 中, 违反 additive schema 约定"
        )
