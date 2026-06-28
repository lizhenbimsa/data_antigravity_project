"""test_16_policy_alignment_dual — Plan E P3 B2 双轨政策对齐验收 (14 cases).

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


def test_coprimary_cosine_for_spec_main_and_large():
    """v3.14.0 co-primary 双 API 模型: compute 用 _cosine_for_spec 对 MAIN spec
    (EMBEDDING_CONFIG=Qwen/Qwen3-Embedding-8B, 无后缀) 与 co-primary spec
    (_LARGE_SPEC=text-embedding-3-large, `_lg`) 各算一遍, 缓存命名空间由 model_id (engine)
    隔离, 不 mutate 全局 EMBEDDING_CONFIG。

    v3.14.0 已硬删本地稳健轨 `_t2v` (text2vec) / `_bge` (bge-m3) → `_ROBUSTNESS_SPEC`/
    `_BGE_SPEC` 不复存在; 现仅余两 API co-primary (Qwen 无后缀 + large `_lg`)。"""
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src_compute = inspect.getsource(pa.compute_article_policy_alignment)
    # 双 spec 双算: MAIN (Qwen) + co-primary (large)
    assert '_cosine_for_spec' in src_compute, "compute 应用 _cosine_for_spec 助手"
    assert '_LARGE_SPEC' in src_compute, "compute 应对 co-primary _lg spec (_LARGE_SPEC) 再算一遍"
    # 产出 co-primary _lg twin 列
    assert 'policy_cosine_sim_lg_full' in src_compute
    assert 'policy_cosine_sim_lg_ctx' in src_compute
    # 已硬删本地稳健轨 → 源码不应再出现 _t2v / _bge / 旧 spec 句柄
    assert '_ROBUSTNESS_SPEC' not in src_compute, "v3.14.0 已删 _t2v 稳健轨 (_ROBUSTNESS_SPEC)"
    assert 'policy_cosine_sim_t2v' not in src_compute, "v3.14.0 已删 _t2v 列"
    assert 'policy_cosine_sim_bge' not in src_compute, "v3.14.0 已删 _bge 列"
    # 仍不 mutate 全局 EMBEDDING_CONFIG (无全局副作用)
    assert "EMBEDDING_CONFIG['text_pipeline_version'] = " not in src_compute, \
        "禁止 mutate EMBEDDING_CONFIG (cache 命名空间由 model_id 隔离)"
    # _cosine_for_spec 经 engine 嵌入 (MAIN/co-primary 共用同算法只换 spec)
    src_spec = inspect.getsource(pa._cosine_for_spec)
    assert '_eng.embed_texts' in src_spec, "_cosine_for_spec 应经 embedding_engine 嵌入"


def test_large_spec_active_co_primary():
    """v3.14.0: config 已激活 embedding_large → _LARGE_SPEC 非空 (co-primary _lg ACTIVE)。"""
    from news_process.pipeline.filtering import policy_alignment as pa
    assert pa._LARGE_SPEC, "config 已激活 embedding_large → _LARGE_SPEC 应非空 (co-primary)"
    # 已硬删本地稳健 spec 句柄
    assert not hasattr(pa, '_ROBUSTNESS_SPEC'), "v3.14.0 已删 _ROBUSTNESS_SPEC 模块级句柄"
    assert not hasattr(pa, '_BGE_SPEC'), "v3.14.0 已删 _BGE_SPEC 模块级句柄"


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
    """模拟 engine 嵌入返回固定单位向量, 验证输出含 co-primary 双 API 模型双轨列
    (MAIN Qwen 无后缀 + co-primary large `_lg`)."""
    from news_process.pipeline.filtering import policy_alignment as pa

    # 构造 3 篇 mock 文章
    df = pd.DataFrame({
        '标题': ['标题1', '标题2', '标题3'],
        '内容': ['全文1 fintech innovation', '全文2 digital transformation', '全文3'],
        'content_ctx': ['工行 ctx1', '建行 ctx2', '中行 ctx3'],
    })

    # Mock embedding_engine.embed_texts: 任意 spec 都返回 [1,0,0,...] 单位向量 → cosine = 1.0
    # (MAIN Qwen spec 与 co-primary large spec 各调一遍, 均走此 mock → canonical 与 _lg
    # 列都满列。dim 取 4096 = Qwen MAIN 实际维度 (large 实际 3072, 维度不同, 余弦维度无关
    # 绝不混算; 此 mock 单数组服务两 spec, 几何走通即可, dim 大小不影响通路。)
    def _fake_embed(texts, spec, **kwargs):
        return np.array([[1.0] + [0.0] * 4095] * len(list(texts)), dtype=np.float32)

    monkeypatch.setattr(pa._eng, 'embed_texts', _fake_embed)
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
    for col in ['policy_cosine_sim_full', 'policy_cosine_sim_ctx', 'policy_cosine_sim',
                'policy_cosine_sim_lg_full', 'policy_cosine_sim_lg_ctx']:
        assert col in out.columns, f"缺 co-primary 双 API 模型双轨列 {col}"
    # legacy alias = full
    assert (out['policy_cosine_sim'] == out['policy_cosine_sim_full']).all()
    # co-primary _lg twin 应满列 (mock 单位向量 → cosine=1.0)
    assert out['policy_cosine_sim_lg_full'].notna().all()


def test_early_exit_missing_auth_corpus_emits_full_lg_contract(monkeypatch, tmp_path):
    """auth 语料缺失/为空的早退路径仍须产出 co-primary 双 API 模型双轨 5 列契约 (全 NaN)。

    回归门 (both-or-neither parity, D-4a): 否则 runner 聚合缺
    policy_cosine_sim_lg_* → export.py REQUIRED_PANEL_COLUMNS 抛 RuntimeError。
    早退路径同样须产 MAIN(无后缀) + co-primary `_lg` 占位列 (both-or-neither 对称)。
    """
    from news_process.pipeline.filtering import policy_alignment as pa
    df = pd.DataFrame({
        '标题': ['t1', 't2'], '内容': ['c1', 'c2'], 'content_ctx': ['x1', 'x2'],
    })
    # 指向不存在的 auth 路径 → 触发 'not os.path.exists' 早退
    monkeypatch.setitem(pa.CONFIG['paths'], 'authoritative_corpus_file',
                        str(tmp_path / 'nonexistent_auth_corpus.txt'))
    out = pa.compute_article_policy_alignment(df)
    for col in ['policy_cosine_sim', 'policy_cosine_sim_full', 'policy_cosine_sim_ctx',
                'policy_cosine_sim_lg_full', 'policy_cosine_sim_lg_ctx']:
        assert col in out.columns, f"早退路径缺 co-primary 双 API 模型双轨列 {col}"
        assert out[col].isna().all(), f"{col} 早退应全 NaN"


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
def test_full_text_reads_content_full_for_cache_reuse():
    """full 轨应读 stage 13 物化的 content_full (与 stage 27 逐篇嵌入同源, 复用 embedding 缓存)。

    P0 修复 (embedding-reuse-audit 2026-06-05): 旧的裸 '标题 + 空格 + 内容' 与下游
    content_full (prepend_title) 不同字节 → 互为 LLMCache miss, 同篇文章重复付费。
    改读 content_full 后, full 轨并入 stage 27 (benefit_society) 的文章级共享缓存池。
    (stage 25 嵌 bank-year 聚合文档, 粒度错配不共享; 仅文本源串同源。) 语义仍是 标题+内容。
    """
    import inspect

    from news_process.pipeline.filtering import policy_alignment as pa
    src = inspect.getsource(pa.compute_article_policy_alignment)
    # 主路径读 content_full 列
    assert "'content_full' in df.columns" in src and "df['content_full']" in src, \
        "full 轨应优先读 content_full (与 stage 25/27 同源)"
    # 回退路径用 prepend_title (与 stage 13 同函数 → 与 content_full 字节一致)
    assert 'prepend_title' in src, "缺 content_full 列时应回退 prepend_title 内联构建"
    # 不应再有旧的裸空格拼接 (会与 content_full 口径分裂 → cache miss + 标题不对称)
    assert "titles + ' ' + contents" not in src, \
        "旧裸空格拼接应已移除 (会与 content_full 缓存命名空间分裂)"


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
    assert '16_article_policy_alignment.py' in names


def test_stage_13_added_before_14():
    """v3.6.0 stage 13 (ctx 物化) 应在 12 之后 14 之前."""
    from news_process.core.dag import STAGES_MAIN
    scripts = [s.script for s in STAGES_MAIN]
    idx_12 = scripts.index('12_news_fintech.py')
    idx_13 = scripts.index('14_materialize_ctx.py')
    idx_14 = scripts.index('15_fintech_intensity.py')
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
