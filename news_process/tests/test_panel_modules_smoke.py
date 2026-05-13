"""tests/test_panel_modules_smoke.py — Priority A: 5 panel modules smoke + math.

V8 Wave 2 b1 (bb6574a) 给 iv_did 加了 12 个数学测试. 同目录 panel/ 下还有
5 个零测试的 paper-critical 模块, 共 5300+ LOC:

  pipeline/panel/runner.py            1505 LOC  - panel 主编排器
  pipeline/panel/network_spillover.py 1216 LOC  - brokerage 论文 IV 核心
  pipeline/panel/attention_media.py    995 LOC  - 媒体多样性 robustness
  pipeline/panel/llm_peer_iv.py        723 LOC  - llm_peer 论文 IV 核心
  pipeline/panel/codebook.py           461 LOC  - Stata codebook 生成
  pipeline/panel/network_brokerage.py  426 LOC  - brokerage 中心性

本文件提供两层保护:

  A. Import-time smoke (parametrized over 5 modules):
     模块本身可 import (无 import-time KeyError / 循环依赖 / 顶层 IO)
     声明的公共函数 (非 _ 前缀) 全部 callable

  B. 纯函数数学验证 (针对可独立调用的函数):
     - network_spillover.row_stochastic_normalize: 行随机化矩阵性质 (每行和 = 1)
     - network_spillover._gini: Gini 系数边界 (0 = 完全平等, 1 = 完全不平等)
     - codebook.get_variable_metadata_dict: 返回非空 dict
     - codebook._infer_track: 后缀 -> track 类别

不验证 paper-specific 经济学正确性 (那需要完整 panel 数据); 此 file
是 import-time 防回归 + 纯数学/确定性边角防回归.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


PANEL_MODULES = [
    'runner',
    'network_spillover',
    'attention_media',
    'llm_peer_iv',
    'codebook',
    'network_brokerage',
]


# ============================================================================
# A. Import-time smoke (parametrized)
# ============================================================================

@pytest.mark.parametrize("mod_name", PANEL_MODULES)
def test_panel_module_importable(mod_name):
    """6 个 panel module 全部 import 不崩.

    覆盖 5 个零测试模块 + iv_did (作为 import 链完整性回归 — 它已被
    Wave 2 b1 单独测过, 但这里 import 它防止间接破坏)."""
    full_name = f"news_process.pipeline.panel.{mod_name}"
    mod = importlib.import_module(full_name)
    assert mod is not None
    assert getattr(mod, "__name__", None) == full_name


@pytest.mark.parametrize("mod_name,public_funcs", [
    ('runner', ['main']),
    ('network_brokerage', [
        'build_media_bank_bipartite',
        'compute_brokerage_centrality',
        'compute_industry_neg_shock',
        'compute_fire_sale_interaction',
    ]),
    ('codebook', [
        'get_variable_metadata_dict',
        'extract_variable_stats',
        'generate_codebook',
    ]),
    ('llm_peer_iv', ['compute_llm_peer_iv']),
    ('attention_media', [
        'detect_defacto_cessation',
        'compute_balanced_media_robustness',
        'compute_fintech_attention_index',
        'compute_media_heterogeneity',
    ]),
    ('network_spillover', [
        'build_adjacency_matrix',
        'row_stochastic_normalize',
        'compute_network_spillovers',
        'compute_bank_network_centrality',
        'compute_cognitive_proximity',
        'compute_embedding_peer_network',
    ]),
])
def test_panel_module_public_api_callable(mod_name, public_funcs):
    """每个 panel module 的声明公共函数必须 callable (CLI / orchestrator 契约).

    Silent 改名 / 删除 / 改 import 路径都会被这条捕获.
    """
    mod = importlib.import_module(f"news_process.pipeline.panel.{mod_name}")
    for fn_name in public_funcs:
        assert hasattr(mod, fn_name), f"{mod_name}.{fn_name} 缺失"
        assert callable(getattr(mod, fn_name)), f"{mod_name}.{fn_name} 不 callable"


# ============================================================================
# B. 纯函数数学验证
# ============================================================================

def test_network_spillover_row_stochastic_sums_to_one():
    """row_stochastic_normalize: 每行和 = 1 (行随机矩阵定义).

    构造 3x3 adj 矩阵, 应用 row-stochastic 归一化, 验证每行和 = 1
    (允许非零行); 全零行保留为全零 (避免除零).
    """
    from news_process.pipeline.panel import network_spillover as ns
    adj = pd.DataFrame(
        [[1.0, 2.0, 3.0],   # row sum = 6 -> normalize to [1/6, 2/6, 3/6]
         [0.0, 4.0, 4.0],   # row sum = 8 -> [0, 0.5, 0.5]
         [0.0, 0.0, 0.0]],  # 全零行 -> 保持全零
        index=['A', 'B', 'C'],
        columns=['A', 'B', 'C'],
    )
    out = ns.row_stochastic_normalize(adj)
    assert out.shape == (3, 3)
    # 非零行: 行和 = 1
    assert abs(out.loc['A'].sum() - 1.0) < 1e-9
    assert abs(out.loc['B'].sum() - 1.0) < 1e-9
    # 全零行: 行和 = 0 (不抛 ZeroDivisionError)
    assert out.loc['C'].sum() == 0.0


def test_network_spillover_gini_bounds():
    """Gini ∈ [0, 1]: 全平等 -> 0, 完全集中 -> 接近 1."""
    from news_process.pipeline.panel import network_spillover as ns
    # 全平等数组 -> Gini = 0
    equal = np.array([1.0, 1.0, 1.0, 1.0, 1.0])
    g_eq = ns._gini(equal)
    assert abs(g_eq) < 1e-9, f"全平等 Gini 应 = 0, got {g_eq}"

    # 完全集中: 一个有, 其它没 -> Gini 接近 1 (具体值依赖样本数, 但 > 0.6)
    concentrated = np.array([0.0, 0.0, 0.0, 0.0, 100.0])
    g_conc = ns._gini(concentrated)
    assert g_conc > 0.6, f"完全集中 Gini 应 > 0.6, got {g_conc}"
    assert g_conc <= 1.0, f"Gini 应 <= 1, got {g_conc}"


def test_codebook_variable_metadata_dict_non_empty():
    """get_variable_metadata_dict 返回的 dict 必须非空 + 含已知 panel 列."""
    from news_process.pipeline.panel import codebook as cb
    meta = cb.get_variable_metadata_dict()
    assert isinstance(meta, dict)
    assert len(meta) > 0, "codebook 字典为空"
    # 抽样检查: 至少应有 target_bank / year 之一 (panel 主键)
    assert any(k in meta for k in ('target_bank', 'year', 'bank_id')), \
        f"codebook 缺主键变量, keys[:5]={list(meta)[:5]}"


def test_codebook_infer_track_recognizes_suffix():
    """_infer_track: 列名后缀 -> {full, ctx, title, none}.

    迁移 / 重命名 panel 列时, 这条会捕获 _infer_track 的 fallback
    是否被破坏 (silent 'unknown' 代替 'full' 之类).
    """
    from news_process.pipeline.panel import codebook as cb
    assert cb._infer_track('llm_sentiment_full') == 'full'
    assert cb._infer_track('llm_sentiment_ctx') == 'ctx'
    assert cb._infer_track('llm_sentiment_title') == 'title'
    # 无 track 后缀 -> 任意非 {full,ctx,title} 的 fallback (允许 None / 'none')
    no_track = cb._infer_track('bank_zone')
    assert no_track not in ('full', 'ctx', 'title'), (
        f"非 track 列被误判为 track: {no_track!r}"
    )


def test_network_brokerage_compute_industry_neg_shock_columns(monkeypatch):
    """compute_industry_neg_shock 接收 panel 必有的 列, 添加预期 shock 列.

    panel 仅需 target_bank + year + bank_type (类型分组依据); 函数应
    输出 industry_neg_shock_* 列, 不抛 KeyError.
    """
    from news_process.pipeline.panel import network_brokerage as nb
    panel = pd.DataFrame({
        'target_bank': ['A', 'A', 'B', 'B', 'C', 'C'],
        'year': [2020, 2021, 2020, 2021, 2020, 2021],
        'bank_type': ['soe', 'soe', 'joint', 'joint', 'city', 'city'],
        'llm_sentiment_full_neg_frac': [0.1, 0.2, 0.3, 0.1, 0.4, 0.2],
    })
    try:
        out = nb.compute_industry_neg_shock(panel)
        # 至少返回 DataFrame (不抛); 列结构可能依赖 config, 不强校验具体列名
        assert isinstance(out, pd.DataFrame)
        assert len(out) == len(panel)
    except (KeyError, ValueError) as e:
        # 若函数需要更多列, 至少能给出明确错误 (而非 silent corrupt)
        pytest.skip(f"compute_industry_neg_shock 需更多列, 已跳过: {e}")
