"""test_dual_compute_coverage — co-primary 双 API 嵌入列覆盖回归门 (v3.14.0).

锁定"主阶段内联多算"契约: 每个嵌入特征在一次运行内用两个 **API** co-primary spec
各算一遍, 并排产出 canonical 列 (无后缀 = Qwen/Qwen3-Embedding-8B, MAIN slot) +
`_lg` 孪生列 (text-embedding-3-large, LARGE slot), 二者**对等互证**、跨厂商
(阿里 Qwen ⟂ OpenAI)、严格 parity (有无后缀列必有 `_lg`, 反之亦然)。

v3.14.0 架构转向 (2026-06-27, all-API-embedding): 项目此后**不加载任何本地嵌入模型**。
旧本地稳健轨 `_t2v` (shibing624/text2vec) 与 `_bge` (BAAI/bge-m3) 及其全部本地推理机器
(encode_local / _LOCAL_MODELS / ensure_torch_determinism / _select_torch_device) **硬删除**。
现仅余双 API 模型: Qwen (无后缀 MAIN) + large (`_lg`)。两者经各 producer 模块级
`_LARGE_SPEC = CONFIG.get('embedding_large', {})` 门控; 因 config/features.yaml 现已激活
`embedding_large` 块 → `_LARGE_SPEC` 非空 → `_lg` 列**实际产出** (ACTIVE, 非休眠)。

策略: monkeypatch ``embedding_engine.embed_texts`` (所有 feature 模块都经 ``_eng.embed_texts``
走它的 **API 路径**), 返回按 spec.model 确定性区分的向量 → canonical / `_lg` 两族列都满列
且数值不同 (非退化)。不触网、不调真实 API。`spec_uses_local` 仍存在 (纯 base_url 谓词),
对所有 API spec 恒返回 False。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast


def _seed_for(spec) -> int:
    # MAIN/large spec 的 model 名各不同 → 不同随机种子 → 不同向量 (验证真双算非别名复制)
    return sum(ord(c) for c in str((spec or {}).get('model', 'x'))) % 9973


def _fake_embed(texts, spec, **kwargs):
    """确定性 mock (API 路径): (n, 16) 随机向量, 按 spec.model 区分 (Qwen/large 各异)。"""
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


def test_strategic_diff_emits_canonical_and_lg(monkeypatch):
    """stage 25: 嵌入派生列须同时含 canonical (Qwen) / `_lg` (large) co-primary 双族。"""
    _patch_engine(monkeypatch)
    from news_process.pipeline.features import strategic_diff as sd

    # _LARGE_SPEC 现由 config (embedding_large 已激活) 注入非空 → co-primary _lg ACTIVE
    assert sd._LARGE_SPEC, "config 已激活 embedding_large → _LARGE_SPEC 应非空 (co-primary _lg ACTIVE)"
    panel = sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())

    # canonical (无后缀 = Qwen, MAIN slot)
    for col in ['strat_diff_n5_emb', 'strat_sim_max_emb', 'centroid_diff_emb']:
        assert col in panel.columns, f"缺 canonical 嵌入列 {col}"
    # co-primary twin (_lg = text-embedding-3-large) + 契约别名 (与无后缀对称)
    for col in ['strat_diff_n5_emb_lg', 'strat_sim_max_emb_lg',
                'centroid_diff_emb_lg', 'strat_diff_lg_full']:
        assert col in panel.columns, f"缺 large co-primary twin 列 {col}"
    # 两族都应有非空值 (真双算)
    assert panel['centroid_diff_emb'].notna().any()
    assert panel['centroid_diff_emb_lg'].notna().any()
    # ctx 轨 twin (_lg 对称)
    for col in ['strat_diff_n5_emb_lg_ctx', 'centroid_diff_emb_lg_ctx',
                'strat_diff_lg_ctx']:
        assert col in panel.columns, f"缺 ctx large twin 列 {col}"


def test_benefit_society_emits_canonical_and_lg(monkeypatch, tmp_path):
    """stage 27: benefit_* 须同时含 canonical (Qwen) / `_lg` (large) co-primary 双族。"""
    _patch_engine(monkeypatch)
    from news_process.pipeline.features import benefit_society as bs

    # fix(omni-g-benefit-01 / KNOWN-OPEN①, 2026-06-11): stage 27 现真实落盘
    # 嵌入/方向 .npy 与冻结 center sidecar → 重定向 OUTPUT_DIR 到 tmp, 防止
    # toy 数据污染真实 data/processed (尤其 _benefit_center_sidecar.json 的
    # 首跑冻结值)。
    monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
    assert bs._LARGE_SPEC, "config 已激活 embedding_large → _LARGE_SPEC 应非空"

    panel = bs.compute_benefit_society_panel(_toy_panel(), _toy_df_exploded())

    canonical = ['benefit_mean_full', 'benefit_std_full',
                 'benefit_pos_frac_full', 'benefit_neg_frac_full']
    lg = ['benefit_mean_lg_full', 'benefit_std_lg_full',
          'benefit_pos_frac_lg_full', 'benefit_neg_frac_lg_full']
    for col in canonical:
        assert col in panel.columns, f"缺 canonical benefit 列 {col}"
    for col in lg:
        assert col in panel.columns, f"缺 large co-primary twin benefit 列 {col}"
    assert panel['benefit_mean_full'].notna().any()
    assert panel['benefit_mean_lg_full'].notna().any()


# ---------------------------------------------------------------------------
# co-primary parity 回归锁 (v3.14.0): config 激活 embedding_large 时 `_lg` 列**实际产出**
# (非休眠)。这是 D-4a"Qwen⟂large 严格 parity (有无后缀列必有 _lg)"不变量的 producer
# 侧锚点。同时锁守卫范围铁律 (MAIN canonical 致命错须 fail-fast 上抛, 不被 _lg twin 守卫
# 静默吞为 NaN 主结果列 + 不吞离线确定性闸)。
# ---------------------------------------------------------------------------


def test_lg_columns_produced_when_large_configured(monkeypatch, tmp_path):
    """co-primary parity 回归锁 (v3.14.0): config 已激活 embedding_large
    (_LARGE_SPEC 非空, 生产默认态) → producer **必产** `_lg` 列 (与无后缀 canonical 对称)。
    覆盖 strategic_diff / benefit_society / network_spillover 三个有 toy fixture 的 producer
    (policy_alignment/policy_similarity 同 `if _LARGE_SPEC:` 门控但需 auth 语料, 不另测)。"""
    _patch_engine(monkeypatch)
    from news_process.pipeline.features import benefit_society as bs
    from news_process.pipeline.features import strategic_diff as sd
    from news_process.pipeline.panel import network_spillover as ns

    # 三 producer 模块级 _LARGE_SPEC 在生产 config (embedding_large 已激活) 下均应非空
    assert sd._LARGE_SPEC and bs._LARGE_SPEC and ns._LARGE_SPEC, \
        "生产态 _LARGE_SPEC 应非空 (embedding_large 已激活, co-primary _lg ACTIVE)"

    p_sd = sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())
    assert 'centroid_diff_emb' in p_sd.columns and 'centroid_diff_emb_lg' in p_sd.columns, \
        "strategic_diff co-primary: 无后缀与 _lg 列须并存"

    monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
    p_bs = bs.compute_benefit_society_panel(_toy_panel(), _toy_df_exploded())
    assert 'benefit_mean_full' in p_bs.columns and 'benefit_mean_lg_full' in p_bs.columns, \
        "benefit_society co-primary: 无后缀与 _lg 列须并存"

    p_ns = ns.compute_embedding_peer_network(_toy_df_exploded_2yr(), _toy_panel_2yr())
    assert 'bank_emb_sim_mean_lag1' in p_ns.columns and 'bank_emb_sim_mean_lag1_lg' in p_ns.columns, \
        "network_spillover co-primary: 无后缀与 _lg 列须并存"


def _fake_embed_raise_main(texts, spec, **kwargs):
    """mock: 对 MAIN canonical spec **raise** 致命错 (模拟离线确定性闸 miss / 鉴权失败);
    co-primary twin (_lg) 返回正常向量 → 验证守卫只软降级 twin、MAIN 仍 fail-fast。

    (二分 _track_of 仅认 model 名是否含 'large': MAIN = Qwen 等非 large 模型。)"""
    if _track_of(spec) == 'main':
        raise RuntimeError("simulated MAIN canonical fatal (offline-gate cache miss)")
    items = list(texts)
    if not items:
        return None
    return np.random.RandomState(_seed_for(spec)).rand(len(items), 16).astype(np.float32)


def test_main_canonical_fatal_raises_not_swallowed_strategic(monkeypatch):
    """守卫范围回归锁: strategic_diff 的 MAIN canonical (Qwen) 致命错
    必须 fail-fast 上抛, 不被 _lg co-primary 守卫静默吞为 NaN 主结果列。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_raise_main)
    from news_process.pipeline.features import strategic_diff as sd

    with pytest.raises(RuntimeError):
        sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())


def test_main_canonical_fatal_raises_not_swallowed_benefit(monkeypatch, tmp_path):
    """守卫范围回归锁: benefit_society 的 MAIN canonical (Qwen) 致命错
    (含离线确定性闸) 必须 fail-fast 上抛, 不被 _lg co-primary 守卫静默降级。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_raise_main)
    from news_process.pipeline.features import benefit_society as bs

    monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))  # 防 toy 污染真实产物
    with pytest.raises(RuntimeError):
        bs.compute_benefit_society_panel(_toy_panel(), _toy_df_exploded())


def test_policy_similarity_emits_canonical_and_lg(monkeypatch):
    """stage 26: auth_sim_emb 须同时含 canonical (Qwen) / `_lg` (large) co-primary 双族
    (需 auth 语料)。"""
    import os

    _patch_engine(monkeypatch)
    from news_process.pipeline.features import policy_similarity as ps

    auth_path = ps.CONFIG['paths'].get('authoritative_corpus_file', '')
    if not auth_path or not os.path.exists(auth_path):
        pytest.skip(f"auth corpus 不存在: {auth_path}")

    assert ps._LARGE_SPEC, "config 已激活 embedding_large → _LARGE_SPEC 应非空"
    panel = ps.compute_authoritative_similarity(_toy_df_exploded(), _toy_panel())
    assert 'auth_sim_emb_full' in panel.columns, "缺 canonical auth_sim_emb_full"
    assert 'auth_sim_emb_lg_full' in panel.columns, "缺 large co-primary twin auth_sim_emb_lg_full"


def test_engine_namespaces_cache_by_model(monkeypatch):
    """主/co-primary spec 经 LLMCache 时以 model_id 隔离, 不串。"""
    from news_process.core.caching import LLMCache
    k_main = LLMCache._make_key('Qwen/Qwen3-Embedding-8B', 'foo', prompt_version='v4-qwen')
    k_lg = LLMCache._make_key('text-embedding-3-large', 'foo', prompt_version='v1-emb3large')
    assert k_main != k_lg, "MAIN/co-primary spec 缓存键必须隔离 (model_id 维度)"


# ---------------------------------------------------------------------------
# F5 (2026-05-30): network_spillover co-primary 覆盖 + 失败路径回归锁。
# 此前本门只覆盖 stage 25/26/27 happy-path; 既漏掉第 5 个 callsite (network),
# 也没有任何"嵌入失败时 REQUIRED 契约列仍存在"的断言 (正是 F1/F2 漏网原因)。
# ---------------------------------------------------------------------------


def _track_of(spec) -> str:
    """按 spec.model 名做**二分** (v3.14.0 双 API co-primary)。

    - 'large' 在 model 名中 → co-primary ② (`_lg`);  # 如 text-embedding-3-large
    - 否则 (Qwen/Qwen3-Embedding-8B 等) → MAIN canonical (无后缀)。

    (v3.14.0 已硬删 `_t2v`/`_bge` 本地轨, 二分足够区分两 API co-primary。)
    """
    model = str((spec or {}).get('model', '')).lower()
    if 'large' in model:
        return 'large'
    return 'main'


def _fake_embed_spec_aware(*, main_returns_none=False, large_returns_none=False):
    """工厂: 确定性 mock, 可按 spec.model **二分** 独立强制某一轨返回 None。

    二分 (MAIN / co-primary `_lg`) 经 ``_track_of``; ``large_returns_none`` 独立模拟
    `_lg` 嵌入失败 (与 MAIN 失败正交)。
    """
    _none_for = {'main': main_returns_none, 'large': large_returns_none}

    def _inner(texts, spec, **kwargs):
        items = list(texts)
        n = len(items)
        if n == 0:
            return None
        if _none_for[_track_of(spec)]:
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


def test_network_embedding_peer_emits_canonical_and_lg(monkeypatch):
    """第 5 个 callsite (network embedding peer): emb_peer_tone_lag1 +
    bank_emb_sim_mean_lag1 须同时含 canonical (Qwen) 与 `_lg` (large) co-primary 双族。

    fix(omni-g-net-spill-03, 2026-06-11): sim 列重命名披露 t-1 文本口径
    (bank_emb_sim_mean → bank_emb_sim_mean_lag1, co-primary 同步), 断言随更新。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_spec_aware())
    from news_process.pipeline.panel import network_spillover as ns

    assert ns._LARGE_SPEC, "config 已激活 embedding_large → _LARGE_SPEC 应非空"
    panel = ns.compute_embedding_peer_network(
        _toy_df_exploded_2yr(), _toy_panel_2yr())

    for col in ['emb_peer_tone_lag1_full', 'bank_emb_sim_mean_lag1',
                'emb_peer_tone_lag1_lg_full', 'bank_emb_sim_mean_lag1_lg']:
        assert col in panel.columns, f"缺 network 嵌入列 {col}"
    # 2020 行 (其 lag 年 2019 有数据) canonical 主轨应算出真值
    y2020 = panel[panel['year'] == 2020]
    assert y2020['bank_emb_sim_mean_lag1'].notna().any(), "canonical 主轨未算出值"
    # config 激活 embedding_large 时, _lg co-primary 轨也应算出真值 (真双算; 与无后缀对称)
    assert y2020['bank_emb_sim_mean_lag1_lg'].notna().any(), "large _lg co-primary 轨未算出值"


def test_policy_alignment_main_fail_keeps_lg_contract(monkeypatch):
    """F1 回归锁: stage 15 MAIN(Qwen API)嵌入失败时, 契约列 (含 co-primary
    policy_cosine_sim_lg_{full,ctx}) 必须全部存在, 否则下游
    export.py::REQUIRED_PANEL_COLUMNS 抛 RuntimeError。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts',
                        _fake_embed_spec_aware(main_returns_none=True))
    from news_process.pipeline.filtering import policy_alignment as pa

    assert pa._LARGE_SPEC, "config 已激活 embedding_large → _LARGE_SPEC 应非空"
    out = pa.compute_article_policy_alignment(_toy_df_exploded())
    for col in ['policy_cosine_sim', 'policy_cosine_sim_full',
                'policy_cosine_sim_ctx']:
        assert col in out.columns, f"MAIN 失败后缺契约中的 {col}"
    # co-primary parity: MAIN 失败早返回时, _lg 占位契约列也须存在 (both-or-neither, 与无后缀对称)
    for col in ['policy_cosine_sim_lg_full', 'policy_cosine_sim_lg_ctx']:
        assert col in out.columns, f"MAIN 失败后缺 _lg 占位契约列 {col}"
    # MAIN 失败 → 早返回, 契约列全 NaN (含 _lg, 因主轨失败时 both-or-neither 同置 NaN)
    assert out['policy_cosine_sim_lg_full'].isna().all()


def test_strategic_diff_large_fail_both_or_neither_with_main(monkeypatch):
    """co-primary both-or-neither parity 锁 (v3.14.0): `_lg` 轨嵌入失败
    (large_returns_none) → MAIN 与 `_lg` 同族嵌入列**一并不产** (无单边孤儿列)。

    v3.14.0 架构转向: Qwen(无后缀) 与 large(`_lg`) 是**对等 co-primary、严格 parity**
    (D-4a)。strategic_diff 在 Full/ctx/ss 三轨均加 both-or-neither 守卫 (源
    `if se is None or se_lg is None: se=cd_emb=se_lg=cd_emb_lg=None`) → 任一 co-primary
    嵌入失败, 两族同族列 (`centroid_diff_emb*` 与 `centroid_diff_emb_lg*`) 一并缺失。
    这与旧 `_t2v` 稳健轨"失败仅置自身 NaN、不误伤 MAIN"的非对称语义**根本不同**
    —— co-primary 是对等双射, 同生共死。

    非嵌入派生列 (centroid_diff_tfidf_c 等 TF-IDF/LDA 距离) 不受影响, 照常产出。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts',
                        _fake_embed_spec_aware(large_returns_none=True))
    from news_process.pipeline.features import strategic_diff as sd

    panel = sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())

    # both-or-neither: _lg 失败 → MAIN 嵌入列与 _lg 嵌入列**一并不产** (对等同生共死)
    assert 'centroid_diff_emb' not in panel.columns, \
        "both-or-neither: _lg 失败时 MAIN centroid_diff_emb 应一并缺失 (无单边孤儿)"
    assert 'centroid_diff_emb_lg' not in panel.columns, \
        "both-or-neither: _lg 失败时 _lg 嵌入列应缺失"
    assert 'strat_diff_lg_full' not in panel.columns, \
        "both-or-neither: _lg 失败时契约别名应缺失"
    # 非嵌入派生列 (TF-IDF 质心距离) 不受嵌入失败影响, 照常产出 (验证未误伤非嵌入族)
    assert 'centroid_diff_tfidf_c' in panel.columns and \
        panel['centroid_diff_tfidf_c'].notna().any(), "非嵌入 TF-IDF 列被嵌入失败误伤"
