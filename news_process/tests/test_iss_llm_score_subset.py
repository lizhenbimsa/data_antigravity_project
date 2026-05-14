"""v3.1.0: LLM 逐模型 _score 在 substantiveness 子集的均值聚合.

术语 (v3.0.0 正名后):
  _sub  → 实质性 (substantive)
  _symb → 象征性 (symbolic)     ← Westphal & Zajac 1998 ASQ
  panel 列值即 LLM 原始输出 (翻译层已废除)

LLM_MODELS 硬编码 + 同步注释 (而非 import), 理由:
  避免 from encode import LLM_MODELS 触发 setup_logging 副作用
"""
import pandas as pd

# 与 encode.py:55-56 LLM_MODELS 同步
_LLM_MODELS_FOR_TEST = ['gpt54nano', 'gemini31111', 'deepseekv4']
_PANEL_PATH = 'news_process/data/processed/40_panel_yearly.parquet'


def test_iss_llm_score_subset_aggregation():
    """3 LLM × _full/_ctx × _sub/_symb = 12 列必须存在."""
    panel = pd.read_parquet(_PANEL_PATH)
    required = [
        f'{short}_tone{suffix}{track}'
        for short in _LLM_MODELS_FOR_TEST
        for suffix in ('_sub', '_symb')
        for track in ('_full', '_ctx')
    ]
    missing = [c for c in required if c not in panel.columns]
    assert not missing, f"缺列: {missing}"


def test_iss_llm_score_subset_value_sanity():
    """12 列值必须在 [-1, +1] 范围, 且不应全 NaN."""
    panel = pd.read_parquet(_PANEL_PATH)
    for short in _LLM_MODELS_FOR_TEST:
        for suffix in ('_sub', '_symb'):
            for track in ('_full', '_ctx'):
                col = f'{short}_tone{suffix}{track}'
                vals = panel[col].dropna()
                max_abs = vals.abs().max() if len(vals) else 0.0
                assert max_abs <= 1.0001, f"{col}: 超出 [-1,+1], max abs={max_abs}"
                assert len(vals) > 0, f"{col}: 全 NaN"
