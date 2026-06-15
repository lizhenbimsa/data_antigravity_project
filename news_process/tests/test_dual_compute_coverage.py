"""test_dual_compute_coverage — 双模型嵌入 (2026-05-29) 列覆盖回归门.

锁定"主阶段内联双算"契约: 每个嵌入特征在一次运行内用主 spec (text-embedding-3-small)
+ 稳健 spec (text2vec) 各算一遍, 并排产出 canonical 列 + `_t2v` 列。

策略: monkeypatch ``embedding_engine.embed_texts`` (所有 feature 模块都经
``_eng.embed_texts`` 走它), 返回按 spec.model 确定性区分的向量 → canonical 与 `_t2v`
列都满列且数值不同 (非退化)。不触网、不调真实模型。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast


def _seed_for(spec) -> int:
    # 主/稳健 spec 的 model 名不同 → 不同随机种子 → 不同向量 (验证真双算非别名复制)
    return sum(ord(c) for c in str((spec or {}).get('model', 'x'))) % 9973


def _fake_embed(texts, spec, **kwargs):
    """确定性 mock: (n, 16) 随机单位前向量, 按 spec.model 区分。"""
    items = list(texts)
    n = len(items)
    if n == 0:
        return None
    rng = np.random.RandomState(_seed_for(spec))
    return rng.rand(n, 16).astype(np.float32)


def _patch_engine(monkeypatch):
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed)


def _toy_df_exploded():
    """4 银行 × 1 年的合成文章级数据 (满足 strat_diff 年度 ≥3 银行门槛)。

    三轨 (ss, 2026-06-14): 同时供 content_ss (银行+金科同句轨) 输入列, 与
    content_ctx 平价 — 嵌入特征模块经泛型 content 读取, ss 输入列对其透明。
    """
    banks = ['工商银行', '建设银行', '中国银行', '农业银行']
    rows = []
    for i, b in enumerate(banks):
        rows.append({
            'target_bank': b,
            'year': 2020,
            '标题': f'{b} 金融科技 标题 {i}',
            '内容': f'{b} 区块链 移动支付 智能风控 数字化转型 内容 {i} ' * 3,
            'content_ctx': f'{b} 实体上下文 金融科技 段落 {i} ' * 2,
            'content_ss': f'{b} 同句共现 金融科技 区块链 {i} ' * 2,
        })
    return pd.DataFrame(rows)


def _toy_panel():
    banks = ['工商银行', '建设银行', '中国银行', '农业银行']
    return pd.DataFrame({'target_bank': banks, 'year': [2020] * 4})


def test_strategic_diff_emits_canonical_and_t2v(monkeypatch):
    """stage 25: 嵌入派生列须同时含 canonical 与 _t2v 双族。"""
    _patch_engine(monkeypatch)
    from news_process.pipeline.features import strategic_diff as sd

    panel = sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())

    # canonical (主轨 text-embedding-3-small)
    for col in ['strat_diff_n5_emb', 'strat_sim_max_emb', 'centroid_diff_emb']:
        assert col in panel.columns, f"缺 canonical 嵌入列 {col}"
    # 稳健 twin (text2vec) + 契约别名
    for col in ['strat_diff_n5_emb_t2v', 'strat_sim_max_emb_t2v',
                'centroid_diff_emb_t2v', 'strat_diff_t2v_full']:
        assert col in panel.columns, f"缺稳健 twin 列 {col}"
    # 双族都应有非空值 (真双算)
    assert panel['centroid_diff_emb'].notna().any()
    assert panel['centroid_diff_emb_t2v'].notna().any()
    # ctx 轨 twin
    for col in ['strat_diff_n5_emb_t2v_ctx', 'centroid_diff_emb_t2v_ctx',
                'strat_diff_t2v_ctx']:
        assert col in panel.columns, f"缺 ctx 稳健 twin 列 {col}"


def test_benefit_society_emits_canonical_and_t2v(monkeypatch, tmp_path):
    """stage 27: benefit_* 须同时含 canonical 与 _t2v 双族 (8 + 8)。"""
    _patch_engine(monkeypatch)
    from news_process.pipeline.features import benefit_society as bs

    # fix(omni-g-benefit-01 / KNOWN-OPEN①, 2026-06-11): stage 27 现真实落盘
    # 嵌入/方向 .npy 与冻结 center sidecar → 重定向 OUTPUT_DIR 到 tmp, 防止
    # toy 数据污染真实 data/processed (尤其 _benefit_center_sidecar.json 的
    # 首跑冻结值)。
    monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))

    panel = bs.compute_benefit_society_panel(_toy_panel(), _toy_df_exploded())

    canonical = ['benefit_mean_full', 'benefit_std_full',
                 'benefit_pos_frac_full', 'benefit_neg_frac_full']
    t2v = ['benefit_mean_t2v_full', 'benefit_std_t2v_full',
           'benefit_pos_frac_t2v_full', 'benefit_neg_frac_t2v_full']
    for col in canonical:
        assert col in panel.columns, f"缺 canonical benefit 列 {col}"
    for col in t2v:
        assert col in panel.columns, f"缺稳健 twin benefit 列 {col}"
    assert panel['benefit_mean_full'].notna().any()
    assert panel['benefit_mean_t2v_full'].notna().any()


def test_policy_similarity_emits_canonical_and_t2v(monkeypatch):
    """stage 26: auth_sim_emb 须同时含 canonical 与 _t2v 双族 (需 auth 语料)。"""
    import os

    _patch_engine(monkeypatch)
    from news_process.pipeline.features import policy_similarity as ps

    auth_path = ps.CONFIG['paths'].get('authoritative_corpus_file', '')
    if not auth_path or not os.path.exists(auth_path):
        pytest.skip(f"auth corpus 不存在: {auth_path}")

    panel = ps.compute_authoritative_similarity(_toy_df_exploded(), _toy_panel())
    assert 'auth_sim_emb_full' in panel.columns, "缺 canonical auth_sim_emb_full"
    assert 'auth_sim_emb_t2v_full' in panel.columns, "缺稳健 twin auth_sim_emb_t2v_full"


def test_engine_namespaces_cache_by_model(monkeypatch):
    """主/稳健 spec 经 LLMCache 时以 model_id 隔离, 不串。"""
    from news_process.core.caching import LLMCache
    k_main = LLMCache._make_key('text-embedding-3-small', 'foo', prompt_version='v2-api')
    k_t2v = LLMCache._make_key('shibing624/text2vec-base-chinese', 'foo',
                               prompt_version='v2-t2v')
    assert k_main != k_t2v, "主/稳健 spec 缓存键必须隔离 (model_id 维度)"


# ---------------------------------------------------------------------------
# F5 (2026-05-30): 补 network_spillover _t2v 覆盖 + 失败路径回归锁。
# 此前本门只覆盖 stage 25/26/27 happy-path; 既漏掉第 5 个 callsite (network),
# 也没有任何"嵌入失败时 REQUIRED 契约列仍存在"的断言 (正是 F1/F2 漏网原因)。
# ---------------------------------------------------------------------------


def _fake_embed_spec_aware(*, main_returns_none=False, robust_returns_none=False):
    """工厂: 确定性 mock, 可按 spec.model 强制 MAIN 或 ROBUSTNESS 轨返回 None。

    'text2vec' 在 model 名中 → ROBUSTNESS 轨; 否则 MAIN 轨。用于复现单侧嵌入失败。
    """
    def _inner(texts, spec, **kwargs):
        items = list(texts)
        n = len(items)
        if n == 0:
            return None
        is_robust = 'text2vec' in str((spec or {}).get('model', ''))
        if (is_robust and robust_returns_none) or (not is_robust and main_returns_none):
            return None
        rng = np.random.RandomState(_seed_for(spec))
        return rng.rand(n, 16).astype(np.float32)
    return _inner


def _toy_df_exploded_2yr():
    """4 银行 × 2 年 (2019/2020): network lag-1 (year-1) pass 在 2020 才有滞后数据。

    三轨 (ss, 2026-06-14): 同时供 content_ss 输入列与 content_ctx 平价。
    """
    banks = ['工商银行', '建设银行', '中国银行', '农业银行']
    rows = []
    for year in (2019, 2020):
        for i, b in enumerate(banks):
            rows.append({
                'target_bank': b,
                'year': year,
                '标题': f'{b} 金融科技 标题 {year}-{i}',
                '内容': f'{b} 区块链 移动支付 智能风控 数字化转型 内容 {year}-{i} ' * 3,
                'content_ctx': f'{b} 实体上下文 金融科技 段落 {year}-{i} ' * 2,
                'content_ss': f'{b} 同句共现 金融科技 区块链 {year}-{i} ' * 2,
            })
    return pd.DataFrame(rows)


def _toy_panel_2yr():
    banks = ['工商银行', '建设银行', '中国银行', '农业银行']
    rows = []
    for year in (2019, 2020):
        for b in banks:
            rows.append({'target_bank': b, 'year': year,
                         'llm_vote_tone_full': 0.1})
    return pd.DataFrame(rows)


def test_network_embedding_peer_emits_canonical_and_t2v(monkeypatch):
    """第 5 个 callsite (network embedding peer): emb_peer_tone_lag1 +
    bank_emb_sim_mean_lag1 须同时含 canonical 与 _t2v 双族 (闭合此前覆盖缺口)。

    fix(omni-g-net-spill-03, 2026-06-11): sim 列重命名披露 t-1 文本口径
    (bank_emb_sim_mean → bank_emb_sim_mean_lag1, _t2v 同步), 断言随更新。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_spec_aware())
    from news_process.pipeline.panel import network_spillover as ns

    panel = ns.compute_embedding_peer_network(
        _toy_df_exploded_2yr(), _toy_panel_2yr())

    for col in ['emb_peer_tone_lag1_full', 'bank_emb_sim_mean_lag1',
                'emb_peer_tone_lag1_t2v_full', 'bank_emb_sim_mean_lag1_t2v']:
        assert col in panel.columns, f"缺 network 嵌入列 {col}"
    # 2020 行 (其 lag 年 2019 有数据) canonical 主轨应算出真值
    y2020 = panel[panel['year'] == 2020]
    assert y2020['bank_emb_sim_mean_lag1'].notna().any(), "canonical 主轨未算出值"
    # 配置含 embedding_robustness 时, _t2v 稳健轨也应算出真值 (真双算)
    if ns._ROBUSTNESS_SPEC:
        assert y2020['bank_emb_sim_mean_lag1_t2v'].notna().any(), "稳健 _t2v 轨未算出值"


def test_policy_alignment_main_fail_keeps_t2v_contract(monkeypatch):
    """F1 回归锁: stage 15 MAIN(API)嵌入失败时, 5 列契约 (含
    policy_cosine_sim_t2v_{full,ctx}) 必须全部存在, 否则下游
    export.py::REQUIRED_PANEL_COLUMNS 抛 RuntimeError。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts',
                        _fake_embed_spec_aware(main_returns_none=True))
    from news_process.pipeline.filtering import policy_alignment as pa

    out = pa.compute_article_policy_alignment(_toy_df_exploded())
    for col in ['policy_cosine_sim', 'policy_cosine_sim_full',
                'policy_cosine_sim_ctx', 'policy_cosine_sim_t2v_full',
                'policy_cosine_sim_t2v_ctx']:
        assert col in out.columns, f"MAIN 失败后缺 5 列契约中的 {col}"
    # MAIN 失败 → 早返回, 全 5 列 NaN (含 _t2v, 因主轨失败时稳健轨不再计算)
    assert out['policy_cosine_sim_t2v_full'].isna().all()


def test_strategic_diff_robust_fail_keeps_t2v_contract(monkeypatch):
    """F2 回归锁: stage 25 ROBUSTNESS(text2vec)嵌入失败时, 契约别名
    strat_diff_t2v_{full,ctx} 必须仍存在 (置 NaN); canonical 主轨不受影响。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts',
                        _fake_embed_spec_aware(robust_returns_none=True))
    from news_process.pipeline.features import strategic_diff as sd

    panel = sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())

    for col in ['strat_diff_t2v_full', 'strat_diff_t2v_ctx']:
        assert col in panel.columns, f"ROBUSTNESS 失败后缺契约列 {col}"
    # canonical 主轨 (MAIN spec 成功) 仍应算出值
    assert panel['centroid_diff_emb'].notna().any(), "canonical 主轨被稳健失败误伤"
    # 稳健 twin 失败 → 兜底全 NaN (不破坏 canonical)
    assert panel['strat_diff_t2v_full'].isna().all(), "稳健失败时 _t2v 应为 NaN"
