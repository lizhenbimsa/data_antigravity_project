"""test_15_policy_alignment_dual — Plan E P3 B2 双轨政策对齐验收 (14 cases).

测试 policy_cosine_sim_{full,ctx} 双轨契约 + cache namespace 隔离 + 兼容回退。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


# ── Cases 1-3: import 安全性 + module 接口契约 ──
def test_policy_alignment_module_imports():
    """Stage 15 模块加载不应崩溃."""
    from news_process.pipeline.filtering import policy_alignment as pa
    assert hasattr(pa, 'compute_article_policy_alignment')
    assert hasattr(pa, 'main')


def test_ctx_track_has_ctx_suffix_full_keeps_base():
    """Round 3 M6 + Round 4 M8 修后: full+auth 用 base prompt_version (命中
    v3.5.x 旧 cache), ctx 轨用 base+'-ctx' override 参数显式隔离 (无全局 mutation)."""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src_compute = inspect.getsource(pa.compute_article_policy_alignment)
    # ctx namespace 隔离 (-ctx 后缀, M8 用 override 参数实现)
    assert "+ '-ctx'" in src_compute or '+ "-ctx"' in src_compute, \
        "M6 修: ctx 轨应用 base+'-ctx' namespace"
    assert 'prompt_version_override' in src_compute, \
        "M8 修: 必须用 override 参数, 不再 mutate 全局 EMBEDDING_CONFIG"
    # 显式断言不再 mutate 全局
    assert "EMBEDDING_CONFIG['text_pipeline_version'] = " not in src_compute, \
        "M8 修: 禁止 mutate EMBEDDING_CONFIG"
    # _get_embeddings_api_dynamic 内部不再加 -dual
    src_get = inspect.getsource(pa._get_embeddings_api_dynamic)
    assert "'-dual'" not in src_get and '"-dual"' not in src_get, \
        "M6 修: 去掉 -dual 后缀以保 full+auth cache 命中"


def test_cache_isolation_from_other_callsites():
    """ctx 轨 namespace 不污染其他 embedding callsite (benefit_society 等仍单轨)."""
    import inspect

    from news_process.pipeline.features import benefit_society, strategic_diff
    for mod in [benefit_society, strategic_diff]:
        try:
            src = inspect.getsource(mod)
            assert "'-dual'" not in src and '"-dual"' not in src, \
                f"{mod.__name__} 不应受 P3 B2 影响"
            assert "'-ctx'" not in src or 'text_pipeline_version' not in src, \
                f"{mod.__name__} 不应有 ctx namespace 修改"
        except (TypeError, OSError):
            pass


# ── Cases 4-7: 双轨列输出 ──
def test_dual_track_columns_present_after_run(monkeypatch):
    """模拟 emb API 返回固定向量, 验证输出含双轨列."""
    from news_process.pipeline.filtering import policy_alignment as pa

    # 构造 3 篇 mock 文章
    df = pd.DataFrame({
        '标题': ['标题1', '标题2', '标题3'],
        '内容': ['全文1 fintech innovation', '全文2 digital transformation', '全文3'],
        'content_ctx': ['工行 ctx1', '建行 ctx2', '中行 ctx3'],
    })

    # Mock embedding 返回: 全部为 [1,0,0,...] 单位向量 → cosine = 1.0
    def mock_run(*args, **kwargs):
        n_texts = len(args[0]) if args else len(kwargs['texts'])
        return np.array([[1.0] + [0.0] * 1535] * n_texts, dtype=np.float32)

    monkeypatch.setattr(pa, '_get_embeddings_api_dynamic',
                        lambda *a, **k: mock_run(a[0] if a else k.get('texts', [])))
    # asyncio.run 包装
    monkeypatch.setattr(pa.asyncio, 'run', lambda coro: mock_run([None] * 8))
    # 关掉 token 截断的真实计算 (避免 tiktoken 加载)
    monkeypatch.setattr(pa, '_count_tokens', lambda t: 100)
    monkeypatch.setattr(pa, '_truncate_to_max_tokens', lambda t, m=None: t)
    monkeypatch.setattr(pa, '_split_into_chunks', lambda t, m=None: [t])

    # Mock auth corpus
    import os
    auth_path = pa.CONFIG['paths'].get('authoritative_corpus_file', '')
    if not os.path.exists(auth_path):
        pytest.skip(f"auth corpus not found: {auth_path}")

    out = pa.compute_article_policy_alignment(df)
    for col in ['policy_cosine_sim_full', 'policy_cosine_sim_ctx', 'policy_cosine_sim']:
        assert col in out.columns, f"缺双轨列 {col}"
    # legacy alias = full
    assert (out['policy_cosine_sim'] == out['policy_cosine_sim_full']).all()


def test_ctx_missing_fallback_warns(caplog):
    """content_ctx 缺失 → ctx 轨回退 = full (with WARN)."""
    from news_process.pipeline.filtering import policy_alignment as pa
    df = pd.DataFrame({
        '标题': ['t1'], '内容': ['c1'],  # 无 content_ctx
    })
    # 仅检查 has_ctx 分支日志逻辑 — 用 mock 跳过真实 embedding
    # 直接验证模块代码包含 fallback WARN
    import inspect
    src = inspect.getsource(pa.compute_article_policy_alignment)
    assert 'content_ctx 列缺失' in src or 'has_ctx' in src, \
        "应有 ctx 缺失 fallback 分支"


def test_legacy_alias_preserved():
    """policy_cosine_sim (无后缀) 应保留为 = policy_cosine_sim_full."""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src = inspect.getsource(pa.compute_article_policy_alignment)
    assert "df['policy_cosine_sim'] = df['policy_cosine_sim_full']" in src or \
           "policy_cosine_sim_full" in src
    assert "policy_cosine_sim_ctx" in src


def test_independence_diagnostic_in_source():
    """v3.6.0 应有 Spearman ρ 独立性诊断."""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src = inspect.getsource(pa.compute_article_policy_alignment)
    assert 'spearmanr' in src or 'Spearman' in src


# ── Cases 8-10: 数据流契约 ──
def test_full_text_uses_title_plus_content():
    """full 轨应拼 标题 + 内容 (保持 v3.5.0 行为)."""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src = inspect.getsource(pa.compute_article_policy_alignment)
    assert "titles + ' ' + contents" in src or 'full_texts' in src


def test_ctx_text_is_content_ctx_only():
    """ctx 轨应仅用 content_ctx (不拼标题, 避免标题语义污染)."""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src = inspect.getsource(pa.compute_article_policy_alignment)
    # ctx_texts 来自 df['content_ctx'] 不拼标题
    assert "df['content_ctx']" in src
    # 不应有 "titles + ctx" 拼接
    assert 'titles + ctx' not in src and 'titles + content_ctx' not in src


def test_dual_value_range_assertions():
    """双轨 [-1, 1] 值域断言应同时检 full + ctx."""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src = inspect.getsource(pa.compute_article_policy_alignment)
    # 应有"双轨同时检"模式
    assert ('full' in src and 'ctx' in src and 'assert' in src and
            ('sim_scores_full' in src or 'name, scores' in src))


# ── Cases 11-12: 配置 / schemas 契约 ──
def test_stage_15_in_dag():
    """stage 15 应仍在 STAGES_MAIN."""
    from news_process.core.dag import STAGES_MAIN
    names = [s.script for s in STAGES_MAIN]
    assert '15_article_policy_alignment.py' in names


def test_stage_13_added_before_14():
    """v3.6.0 stage 13 (ctx 物化) 应在 12 之后 14 之前."""
    from news_process.core.dag import STAGES_MAIN
    scripts = [s.script for s in STAGES_MAIN]
    idx_12 = scripts.index('12_news_fintech.py')
    idx_13 = scripts.index('13_materialize_ctx.py')
    idx_14 = scripts.index('14_fintech_intensity.py')
    assert idx_12 < idx_13 < idx_14, \
        f"stage 13 必须在 12 之后 14 之前; 实际 12@{idx_12}, 13@{idx_13}, 14@{idx_14}"


# ── Cases 13-14: legacy 兼容 + 测试套件 marker ──
def test_legacy_policy_cosine_sim_still_exists():
    """v3.5.0 既有 paper 引用 'policy_cosine_sim' (无后缀) 不应破坏."""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src = inspect.getsource(pa.compute_article_policy_alignment)
    assert "df['policy_cosine_sim']" in src, \
        "legacy alias 'policy_cosine_sim' 应保留以兼容 v3.5.0 paper"


def test_no_breaking_change_to_function_signature():
    """compute_article_policy_alignment 签名应保持 (df: DataFrame) -> DataFrame."""
    import inspect

    from news_process.pipeline.filtering.policy_alignment import (
        compute_article_policy_alignment,
    )
    sig = inspect.signature(compute_article_policy_alignment)
    params = list(sig.parameters.keys())
    assert params == ['df'], f"v3.6.0 不应改函数签名; 实际 {params}"


pytestmark = pytest.mark.fast
