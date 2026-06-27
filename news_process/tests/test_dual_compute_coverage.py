"""test_dual_compute_coverage — 双/三模型嵌入列覆盖回归门.

锁定"主阶段内联多算"契约: 每个嵌入特征在一次运行内用主 spec (text-embedding-3-small,
MAIN/canonical) + 稳健 spec (text2vec, ROBUSTNESS-A → `_t2v`) 各算一遍, 并排产出
canonical 列 + `_t2v` 列。

三模型扩展 (2026-06-27, `_lg` 镜像): 第三嵌入模型 (text-embedding-3-large, 3072 维,
ROBUSTNESS-B → `_lg`) 经各 producer 模块级 `_LARGE_SPEC` **休眠门** 控制 —— 仅当 config
显式提供非空 `embedding_large` 块时才产 `_lg` 列, 缺配置时 `_LARGE_SPEC={}` → 完全不产
`_lg` 列 → 既有行为字节级不变 (golden-safe)。本测试用 monkeypatch 把各 producer 的
`_LARGE_SPEC` 注入为非空假 dict, 模拟休眠门"开"以验证 `_lg` 三族列与 canonical/`_t2v`
并存。生产 config 不配 `embedding_large` 块 (保持休眠), 故本注入仅影响测试进程。

策略: monkeypatch ``embedding_engine.embed_texts`` (所有 feature 模块都经
``_eng.embed_texts`` 走它), 返回按 spec.model 确定性区分的向量 → canonical / `_t2v` /
`_lg` 三族列都满列且数值不同 (非退化)。不触网、不调真实模型。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

pytestmark = pytest.mark.fast

# 注入用假 LARGE spec (休眠门"开"): model 名含 'large' → 经下方 mock 走 ROBUSTNESS-B 轨。
# 维度无关 (mock 恒返 16 维, emb.shape[1] 驱动); 生产侧勿在 config 配此块 (保持休眠)。
_FAKE_LARGE_SPEC = {'model': 'text-embedding-3-large', 'base_url': 'https://x',
                    'api_key': 'k', 'text_pipeline_version': 'tlg'}


def _seed_for(spec) -> int:
    # 主/稳健/large spec 的 model 名各不同 → 不同随机种子 → 不同向量 (验证真多算非别名复制)
    return sum(ord(c) for c in str((spec or {}).get('model', 'x'))) % 9973


def _fake_embed(texts, spec, **kwargs):
    """确定性 mock: (n, 16) 随机前向量, 按 spec.model 区分 (small/text2vec/large 各异)。"""
    items = list(texts)
    n = len(items)
    if n == 0:
        return None
    rng = np.random.RandomState(_seed_for(spec))
    return rng.rand(n, 16).astype(np.float32)


def _patch_engine(monkeypatch):
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed)


def _enable_large(monkeypatch, module):
    """注入假 `_LARGE_SPEC` 到 producer 模块, 打开 `_lg` 休眠门 (镜像既有 `_t2v` 轨)。

    各 producer 在 import 时把模块级 `_LARGE_SPEC = CONFIG.get('embedding_large', {})`
    固化为 {} (生产 config 无该块, 保持休眠)。此处 setattr 为非空 dict → 休眠门"开"。
    """
    monkeypatch.setattr(module, '_LARGE_SPEC', _FAKE_LARGE_SPEC)


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
    """stage 25: 嵌入派生列须同时含 canonical / _t2v / _lg 三族 (休眠门开)。"""
    _patch_engine(monkeypatch)
    from news_process.pipeline.features import strategic_diff as sd

    _enable_large(monkeypatch, sd)  # 注入假 _LARGE_SPEC → 打开 _lg 休眠门
    panel = sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())

    # canonical (主轨 text-embedding-3-small)
    for col in ['strat_diff_n5_emb', 'strat_sim_max_emb', 'centroid_diff_emb']:
        assert col in panel.columns, f"缺 canonical 嵌入列 {col}"
    # 稳健 twin (text2vec) + 契约别名
    for col in ['strat_diff_n5_emb_t2v', 'strat_sim_max_emb_t2v',
                'centroid_diff_emb_t2v', 'strat_diff_t2v_full']:
        assert col in panel.columns, f"缺稳健 twin 列 {col}"
    # 第三嵌入 twin (large) + 契约别名镜像 (与上面 _t2v 断言对称)
    for col in ['strat_diff_n5_emb_lg', 'strat_sim_max_emb_lg',
                'centroid_diff_emb_lg', 'strat_diff_lg_full']:
        assert col in panel.columns, f"缺 large twin 列 {col}"
    # 三族都应有非空值 (真三算)
    assert panel['centroid_diff_emb'].notna().any()
    assert panel['centroid_diff_emb_t2v'].notna().any()
    assert panel['centroid_diff_emb_lg'].notna().any()
    # ctx 轨 twin (_t2v / _lg 对称)
    for col in ['strat_diff_n5_emb_t2v_ctx', 'centroid_diff_emb_t2v_ctx',
                'strat_diff_t2v_ctx']:
        assert col in panel.columns, f"缺 ctx 稳健 twin 列 {col}"
    for col in ['strat_diff_n5_emb_lg_ctx', 'centroid_diff_emb_lg_ctx',
                'strat_diff_lg_ctx']:
        assert col in panel.columns, f"缺 ctx large twin 列 {col}"


def test_benefit_society_emits_canonical_and_t2v(monkeypatch, tmp_path):
    """stage 27: benefit_* 须同时含 canonical / _t2v / _lg 三族 (4 + 4 + 4, 休眠门开)。"""
    _patch_engine(monkeypatch)
    from news_process.pipeline.features import benefit_society as bs

    # fix(omni-g-benefit-01 / KNOWN-OPEN①, 2026-06-11): stage 27 现真实落盘
    # 嵌入/方向 .npy 与冻结 center sidecar → 重定向 OUTPUT_DIR 到 tmp, 防止
    # toy 数据污染真实 data/processed (尤其 _benefit_center_sidecar.json 的
    # 首跑冻结值)。
    monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
    _enable_large(monkeypatch, bs)  # 注入假 _LARGE_SPEC → 打开 _lg 休眠门

    panel = bs.compute_benefit_society_panel(_toy_panel(), _toy_df_exploded())

    canonical = ['benefit_mean_full', 'benefit_std_full',
                 'benefit_pos_frac_full', 'benefit_neg_frac_full']
    t2v = ['benefit_mean_t2v_full', 'benefit_std_t2v_full',
           'benefit_pos_frac_t2v_full', 'benefit_neg_frac_t2v_full']
    lg = ['benefit_mean_lg_full', 'benefit_std_lg_full',
          'benefit_pos_frac_lg_full', 'benefit_neg_frac_lg_full']
    for col in canonical:
        assert col in panel.columns, f"缺 canonical benefit 列 {col}"
    for col in t2v:
        assert col in panel.columns, f"缺稳健 twin benefit 列 {col}"
    for col in lg:
        assert col in panel.columns, f"缺 large twin benefit 列 {col}"
    assert panel['benefit_mean_full'].notna().any()
    assert panel['benefit_mean_t2v_full'].notna().any()
    assert panel['benefit_mean_lg_full'].notna().any()


# ---------------------------------------------------------------------------
# postimpl-audit (2026-06-27) 回归锁: (1) 休眠门铁律 (未配置 embedding_large 时
# 绝不产 _lg 列 — golden 加法安全核心); (2) 守卫范围铁律 (MAIN canonical 致命错
# 须 fail-fast 上抛, 不被 _lg twin 守卫静默吞为 NaN 主结果列 + 不吞离线确定性闸)。
# ---------------------------------------------------------------------------


def test_dormant_no_lg_columns_when_large_unconfigured(monkeypatch, tmp_path):
    """休眠门回归锁 (golden 加法安全核心不变量): 未配置 embedding_large
    (_LARGE_SPEC={}, 生产默认态) 时, producer 绝不产任何 _lg 列; _t2v/canonical 照常。
    **刻意不调** _enable_large。覆盖 strategic_diff / benefit_society / network_spillover
    三个有 toy fixture 的 producer (policy_alignment/policy_similarity 同 `if _LARGE_SPEC:`
    门控但需 auth 语料, 不另测)。"""
    _patch_engine(monkeypatch)
    from news_process.pipeline.features import benefit_society as bs
    from news_process.pipeline.features import strategic_diff as sd
    from news_process.pipeline.panel import network_spillover as ns

    # 三 producer 模块级 _LARGE_SPEC 在生产 config (无 embedding_large 块) 下均应为 {}
    assert sd._LARGE_SPEC == {} and bs._LARGE_SPEC == {} and ns._LARGE_SPEC == {}, \
        "生产态 _LARGE_SPEC 应为空 dict (休眠)"

    p_sd = sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())
    assert [c for c in p_sd.columns if '_lg' in c] == [], "strategic_diff 休眠态不应产 _lg 列"
    assert 'centroid_diff_emb' in p_sd.columns and 'centroid_diff_emb_t2v' in p_sd.columns

    monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))
    p_bs = bs.compute_benefit_society_panel(_toy_panel(), _toy_df_exploded())
    assert [c for c in p_bs.columns if '_lg' in c] == [], "benefit_society 休眠态不应产 _lg 列"
    assert 'benefit_mean_full' in p_bs.columns and 'benefit_mean_t2v_full' in p_bs.columns

    p_ns = ns.compute_embedding_peer_network(_toy_df_exploded_2yr(), _toy_panel_2yr())
    assert [c for c in p_ns.columns if '_lg' in c] == [], "network_spillover 休眠态不应产 _lg 列"
    assert 'bank_emb_sim_mean_lag1' in p_ns.columns and 'bank_emb_sim_mean_lag1_t2v' in p_ns.columns


def _fake_embed_raise_main(texts, spec, **kwargs):
    """mock: 对 MAIN canonical spec **raise** 致命错 (模拟离线确定性闸 miss / 鉴权失败);
    稳健 twin (_t2v/_lg) 返回正常向量 → 验证守卫只软降级 twin、MAIN 仍 fail-fast。"""
    if _track_of(spec) == 'main':
        raise RuntimeError("simulated MAIN canonical fatal (offline-gate cache miss)")
    items = list(texts)
    if not items:
        return None
    return np.random.RandomState(_seed_for(spec)).rand(len(items), 16).astype(np.float32)


def test_main_canonical_fatal_raises_not_swallowed_strategic(monkeypatch):
    """守卫范围回归锁 (postimpl-audit P1): strategic_diff 的 MAIN canonical 致命错
    必须 fail-fast 上抛, 不被新 _lg 守卫静默吞为 NaN 主结果列。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_raise_main)
    from news_process.pipeline.features import strategic_diff as sd

    _enable_large(monkeypatch, sd)  # _lg 休眠门开, 但 MAIN raise 仍须冒泡
    with pytest.raises(RuntimeError):
        sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())


def test_main_canonical_fatal_raises_not_swallowed_benefit(monkeypatch, tmp_path):
    """守卫范围回归锁 (postimpl-audit P1): benefit_society 的 MAIN canonical 致命错
    (含离线确定性闸) 必须 fail-fast 上抛, 不被 _lg 守卫静默降级。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_raise_main)
    from news_process.pipeline.features import benefit_society as bs

    monkeypatch.setattr(bs, 'OUTPUT_DIR', str(tmp_path))  # 防 toy 污染真实产物
    _enable_large(monkeypatch, bs)
    with pytest.raises(RuntimeError):
        bs.compute_benefit_society_panel(_toy_panel(), _toy_df_exploded())


def test_policy_similarity_emits_canonical_and_t2v(monkeypatch):
    """stage 26: auth_sim_emb 须同时含 canonical / _t2v / _lg 三族 (需 auth 语料, 休眠门开)。"""
    import os

    _patch_engine(monkeypatch)
    from news_process.pipeline.features import policy_similarity as ps

    auth_path = ps.CONFIG['paths'].get('authoritative_corpus_file', '')
    if not auth_path or not os.path.exists(auth_path):
        pytest.skip(f"auth corpus 不存在: {auth_path}")

    _enable_large(monkeypatch, ps)  # 注入假 _LARGE_SPEC → 打开 _lg 休眠门
    panel = ps.compute_authoritative_similarity(_toy_df_exploded(), _toy_panel())
    assert 'auth_sim_emb_full' in panel.columns, "缺 canonical auth_sim_emb_full"
    assert 'auth_sim_emb_t2v_full' in panel.columns, "缺稳健 twin auth_sim_emb_t2v_full"
    assert 'auth_sim_emb_lg_full' in panel.columns, "缺 large twin auth_sim_emb_lg_full"


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


def _track_of(spec) -> str:
    """🔴 P1-6 (2026-06-27): 按 spec.model 名做**三分** (二分会把 large 误判 MAIN)。

    - 'text2vec' 在 model 名中 → ROBUSTNESS-A (`_t2v`);
    - 'large'    在 model 名中 → ROBUSTNESS-B (`_lg`);   # 如 text-embedding-3-large
    - 否则 (text-embedding-3-small / 本地 t2v config 等) → MAIN (canonical)。

    旧二分 `is_robust = 'text2vec' in model` 下, large 名不含 'text2vec' 会落入
    `not is_robust` → 被 MAIN 早退/失败开关误伤; 三分使 `_lg` 失败可独立模拟。
    """
    model = str((spec or {}).get('model', ''))
    if 'text2vec' in model:
        return 'robust'
    if 'large' in model:
        return 'large'
    return 'main'


def _fake_embed_spec_aware(*, main_returns_none=False, robust_returns_none=False,
                           large_returns_none=False):
    """工厂: 确定性 mock, 可按 spec.model **三分** 独立强制某一轨返回 None。

    三分 (MAIN / ROBUSTNESS-A `_t2v` / ROBUSTNESS-B `_lg`) 经 ``_track_of``;
    ``large_returns_none`` 独立模拟 `_lg` 嵌入失败 (与 `_t2v` 失败正交)。
    """
    _none_for = {'main': main_returns_none, 'robust': robust_returns_none,
                 'large': large_returns_none}

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


def test_network_embedding_peer_emits_canonical_and_t2v(monkeypatch):
    """第 5 个 callsite (network embedding peer): emb_peer_tone_lag1 +
    bank_emb_sim_mean_lag1 须同时含 canonical 与 _t2v 双族 (闭合此前覆盖缺口)。

    fix(omni-g-net-spill-03, 2026-06-11): sim 列重命名披露 t-1 文本口径
    (bank_emb_sim_mean → bank_emb_sim_mean_lag1, _t2v 同步), 断言随更新。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts', _fake_embed_spec_aware())
    from news_process.pipeline.panel import network_spillover as ns

    _enable_large(monkeypatch, ns)  # 注入假 _LARGE_SPEC → 打开 _lg 休眠门
    panel = ns.compute_embedding_peer_network(
        _toy_df_exploded_2yr(), _toy_panel_2yr())

    for col in ['emb_peer_tone_lag1_full', 'bank_emb_sim_mean_lag1',
                'emb_peer_tone_lag1_t2v_full', 'bank_emb_sim_mean_lag1_t2v',
                'emb_peer_tone_lag1_lg_full', 'bank_emb_sim_mean_lag1_lg']:
        assert col in panel.columns, f"缺 network 嵌入列 {col}"
    # 2020 行 (其 lag 年 2019 有数据) canonical 主轨应算出真值
    y2020 = panel[panel['year'] == 2020]
    assert y2020['bank_emb_sim_mean_lag1'].notna().any(), "canonical 主轨未算出值"
    # 配置含 embedding_robustness 时, _t2v 稳健轨也应算出真值 (真双算)
    if ns._ROBUSTNESS_SPEC:
        assert y2020['bank_emb_sim_mean_lag1_t2v'].notna().any(), "稳健 _t2v 轨未算出值"
    # 休眠门开 (_LARGE_SPEC 注入非空) 时, _lg 第三轨也应算出真值 (真三算; 与 _t2v 对称)
    assert y2020['bank_emb_sim_mean_lag1_lg'].notna().any(), "large _lg 轨未算出值"


def test_policy_alignment_main_fail_keeps_t2v_contract(monkeypatch):
    """F1 回归锁: stage 15 MAIN(API)嵌入失败时, 契约列 (含
    policy_cosine_sim_t2v_{full,ctx} 及休眠门开时的 _lg_{full,ctx}) 必须全部存在,
    否则下游 export.py::REQUIRED_PANEL_COLUMNS 抛 RuntimeError。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts',
                        _fake_embed_spec_aware(main_returns_none=True))
    from news_process.pipeline.filtering import policy_alignment as pa

    _enable_large(monkeypatch, pa)  # 注入假 _LARGE_SPEC → 打开 _lg 休眠门
    out = pa.compute_article_policy_alignment(_toy_df_exploded())
    for col in ['policy_cosine_sim', 'policy_cosine_sim_full',
                'policy_cosine_sim_ctx', 'policy_cosine_sim_t2v_full',
                'policy_cosine_sim_t2v_ctx']:
        assert col in out.columns, f"MAIN 失败后缺契约中的 {col}"
    # 休眠门开 → MAIN 失败早返回时, _lg 占位契约列也须存在 (与 _t2v 对称)
    for col in ['policy_cosine_sim_lg_full', 'policy_cosine_sim_lg_ctx']:
        assert col in out.columns, f"MAIN 失败后缺 _lg 占位契约列 {col}"
    # MAIN 失败 → 早返回, 契约列全 NaN (含 _t2v / _lg, 因主轨失败时稳健轨不再计算)
    assert out['policy_cosine_sim_t2v_full'].isna().all()
    assert out['policy_cosine_sim_lg_full'].isna().all()


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


def test_strategic_diff_large_fail_isolated_from_main_and_t2v(monkeypatch):
    """🔴 P1-6 (2026-06-27): `_lg` 轨独立失败 (large_returns_none) 不得误伤 MAIN/`_t2v`。

    验证三分 (``_track_of``) 的隔离性: 旧二分 `is_robust = 'text2vec' in model` 下,
    large 名 (text-embedding-3-large) 不含 'text2vec' → 落 `not is_robust` → 会被
    MAIN 早退/失败开关误判。三分后 ``large_returns_none=True`` 仅作用 `_lg` 轨。

    `_lg` 在 strategic_diff 为**软诊断** (注释"不入硬契约", 无兜底块) → 轨失败时
    `strat_diff_lg_*` / `centroid_diff_emb_lg` 列**缺失** (非 NaN); 而 canonical 与
    `_t2v` (含硬契约 strat_diff_t2v_full) 完全不受影响。"""
    from news_process.pipeline.text import embedding_engine as eng
    monkeypatch.setattr(eng, 'embed_texts',
                        _fake_embed_spec_aware(large_returns_none=True))
    from news_process.pipeline.features import strategic_diff as sd

    _enable_large(monkeypatch, sd)  # 注入假 _LARGE_SPEC → 打开 _lg 休眠门
    panel = sd.compute_strategic_differentiation(_toy_df_exploded(), _toy_panel())

    # canonical 主轨成功 → 有非空值 (未被 _lg 失败误伤; 这正是旧二分会破的不变量)
    assert panel['centroid_diff_emb'].notna().any(), "canonical 主轨被 _lg 失败误伤"
    # _t2v 稳健轨成功 → 有非空值 (与 _lg 正交, 未被误伤)
    assert panel['centroid_diff_emb_t2v'].notna().any(), "_t2v 轨被 _lg 失败误伤"
    # _t2v 硬契约列恒存在
    assert 'strat_diff_t2v_full' in panel.columns, "缺 _t2v 硬契约列"
    # _lg 软诊断列在轨失败时不建 (无兜底; 与 _t2v 硬契约的差异点)
    assert 'centroid_diff_emb_lg' not in panel.columns, "_lg 软诊断列在轨失败时不应出现"
    assert 'strat_diff_lg_full' not in panel.columns, "_lg 软诊断契约别名在轨失败时不应出现"
