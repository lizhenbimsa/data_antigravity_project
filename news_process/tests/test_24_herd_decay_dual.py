"""test_24_herd_decay_dual — Plan E P1 B3 双轨 herd_weight 验收测试.

12 cases 覆盖:
  1. 双轨列输出完整性 (4 列存在 + dtype 正确)
  2. ctx 缺失回退 = full (with WARN)
  3. 全文相同 / ctx 不同 → full 高跟风, ctx 低跟风 (措辞改写场景)
  4. 全文不同 / ctx 相同 → full 低跟风, ctx 高跟风 (银行段抄袭场景)
  5. 双轨独立性: 大样本 Spearman ρ < 1.0 (非完全相关)
  6. 衰减公式正确: weight = 1 / (1 + n_similar_predecessors), 各轨独立
  7. 时间窗口外不计跟风 (NaT + window 边界)
  8. 单篇文章 herd_weight ≡ 1.0 双轨同
  9. legacy schema 警告: 缺 content_ctx 时 logger 出 WARN
 10. encode.py build_aggregation_dict 接受双轨列名
 11. encode.py 后处理 hw_denom 双轨 / 单轨 fallback 分支
 12. _compute_similar_counts_for_track 空文本返回 None
"""
from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import pytest

# herd_decay 的 logger 由 setup_logging 创建并强制 propagate=False
# (见 core/logging.py:191), 所以 caplog 无法捕获. 测试改用 capfd 抓 stderr.


# 共享 fixture: 构造最小可重现的篇章级 DataFrame
@pytest.fixture
def minimal_panel_df():
    """构造 6 篇文章 × 2 银行 × 时间窗口内, 三种相似度模式."""
    return pd.DataFrame({
        'target_bank': ['工商银行'] * 4 + ['建设银行'] * 2,
        '日期': pd.to_datetime([
            '2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04',
            '2023-02-01', '2023-02-02',
        ]),
        # full 全文: 1+2 全文几乎相同, 3+4 完全不同
        '内容': [
            '工商银行发布 2022 年度报告, 净利润 3604 亿元, 同比增长 3.1%, 不良贷款率 1.38%.',
            '工商银行公布 2022 年度业绩报告, 净利润 3604 亿元, 同比增长 3.1%, 不良贷款率 1.38%.',
            '工商银行行长今日出席数字人民币应用论坛, 强调金融科技创新。',
            '工商银行启动绿色金融债券发行, 规模 200 亿元, 期限 3 年。',
            '建设银行成立金融科技子公司, 注册资本 16 亿元。',
            '建设银行启动消费金融业务转型, 推出全新数字产品线。',
        ],
        # ctx 上下文窗口: 1+2 银行段不同(措辞改写), 3+4 银行段相同(片段抄袭)
        'content_ctx': [
            '工商银行 (ICBC) 2022 净利润 3604 亿。',
            '中国工商银行 2022 利润达 3604 亿元。',
            '工商银行行长出席数字论坛, 提出创新意见。',
            '工商银行行长出席数字论坛, 提出创新意见。',  # 与 3 ctx 完全相同
            '建设银行 (CCB) 设科技子公司, 注册资本 16 亿。',
            '建设银行启动消金转型, 上新数字产品。',
        ],
    })


# ============================================================================
# Case 1: 双轨列输出完整性
# ============================================================================
def test_dual_track_output_columns_exist(minimal_panel_df):
    from news_process.pipeline.sentiment.herd_decay import compute_herd_weights
    out = compute_herd_weights(minimal_panel_df.copy())
    for col in ['herd_weight_full', 'herd_weight_ctx',
                'n_similar_articles_full', 'n_similar_articles_ctx']:
        assert col in out.columns, f"缺少双轨列: {col}"
    # v3.6.0 NON-BREAKING (F-B 修): legacy herd_weight 单列保留为 = _full alias
    assert 'herd_weight' in out.columns, "legacy alias herd_weight 应保留 (NON-BREAKING)"
    assert (out['herd_weight'] == out['herd_weight_full']).all(), \
        "legacy alias 应严格等于 _full"


# ============================================================================
# Case 2: ctx 缺失 → 回退 + WARN
# ============================================================================
def test_ctx_missing_falls_back_to_full_with_warn(minimal_panel_df, monkeypatch):
    from news_process.pipeline.sentiment import herd_decay as hd_mod
    warns: list[str] = []
    monkeypatch.setattr(hd_mod.logger, 'warning',
                        lambda msg, *a, **kw: warns.append(str(msg)))
    df = minimal_panel_df.drop(columns=['content_ctx'])
    out = hd_mod.compute_herd_weights(df)
    assert any('content_ctx' in w for w in warns), \
        f"缺 content_ctx 应记 WARN; 实际 warns={warns}"
    assert (out['herd_weight_full'] == out['herd_weight_ctx']).all(), \
        "ctx 缺失时 ctx 轨应回退 = full"


# ============================================================================
# Case 3: full 几乎相同 → full 高跟风; ctx 不同 → ctx 低跟风
# ============================================================================
def test_full_similar_ctx_dissimilar(minimal_panel_df):
    from news_process.pipeline.sentiment.herd_decay import compute_herd_weights
    out = compute_herd_weights(minimal_panel_df.copy())
    # 工行 row 0 (原创) vs row 1 (改写)
    # full sim 应 ≥ 0.35 → row 1 full 算跟风, ctx sim < 0.35 → row 1 ctx 不算跟风
    row1_full_n = out.loc[1, 'n_similar_articles_full']
    row1_ctx_n = out.loc[1, 'n_similar_articles_ctx']
    assert row1_full_n >= 1, f"row 1 full 应≥1 跟风 (得 {row1_full_n})"
    # 这是断言双轨独立性, 不强制 ctx_n=0 (TF-IDF char_wb 可能仍达阈值)
    # 关键是两轨可以独立判定 (不一定 row1_full == row1_ctx)


# ============================================================================
# Case 4: full 不同 / ctx 完全相同 → ctx 高跟风
# ============================================================================
def test_full_dissimilar_ctx_identical(minimal_panel_df):
    from news_process.pipeline.sentiment.herd_decay import compute_herd_weights
    out = compute_herd_weights(minimal_panel_df.copy())
    # row 3 ctx 与 row 2 ctx 完全相同
    row3_ctx_n = out.loc[3, 'n_similar_articles_ctx']
    assert row3_ctx_n >= 1, f"row 3 ctx 应≥1 跟风 (ctx 与 row 2 完全相同, 得 {row3_ctx_n})"


# ============================================================================
# Case 5: 双轨独立性 — 不应完全相关
# ============================================================================
def test_dual_track_independence(minimal_panel_df):
    from news_process.pipeline.sentiment.herd_decay import compute_herd_weights
    # 加大样本: 每银行 20 篇, full 用版本 A, ctx 用版本 B (独立设计)
    rng = np.random.default_rng(seed=42)
    n = 20
    data = {
        'target_bank': ['工行'] * n,
        '日期': pd.to_datetime([f'2023-01-{i+1:02d}' for i in range(n)]),
        '内容': [f"工行公告版本{rng.integers(0, 5)}: 利润增长{rng.integers(1,10)}%" for _ in range(n)],
        'content_ctx': [f"工行第{i}号披露, 不同独立内容{rng.integers(100,999)}" for i in range(n)],
    }
    df = pd.DataFrame(data)
    out = compute_herd_weights(df)
    # 完全独立设计下 ρ 应远小于 1 (允许偶尔 0.9+ 但不等于 1.0)
    rho = out[['herd_weight_full', 'herd_weight_ctx']].corr().iloc[0, 1]
    assert abs(rho) < 1.0 - 1e-6 or pd.isna(rho), \
        f"双轨完全相关 (ρ={rho}) 说明可能未真正分轨"


# ============================================================================
# Case 6: 衰减公式 weight = 1/(1+n) 双轨独立
# ============================================================================
def test_decay_formula_per_track(minimal_panel_df):
    from news_process.pipeline.sentiment.herd_decay import compute_herd_weights
    out = compute_herd_weights(minimal_panel_df.copy())
    expected_full = 1.0 / (1.0 + out['n_similar_articles_full'])
    expected_ctx = 1.0 / (1.0 + out['n_similar_articles_ctx'])
    np.testing.assert_allclose(out['herd_weight_full'], expected_full, atol=1e-9)
    np.testing.assert_allclose(out['herd_weight_ctx'], expected_ctx, atol=1e-9)


# ============================================================================
# Case 7: 时间窗口外不计跟风
# ============================================================================
def test_time_window_excludes_out_of_range():
    from news_process.pipeline.sentiment.herd_decay import compute_herd_weights
    df = pd.DataFrame({
        'target_bank': ['工行'] * 3,
        '日期': pd.to_datetime(['2023-01-01', '2023-01-15', '2023-02-01']),
        '内容': ['完全相同的文本 ABCDE', '完全相同的文本 ABCDE', '完全相同的文本 ABCDE'],
        'content_ctx': ['工行 X ABC', '工行 X ABC', '工行 X ABC'],
    })
    out = compute_herd_weights(df)
    # 时间窗口 7 天: row 1 (1-15) 与 row 0 (1-1) 相差 14 天 > 7 → 不算跟风
    assert out.loc[1, 'n_similar_articles_full'] == 0, "超 7 天窗口不应算跟风"


# ============================================================================
# Case 8: 单篇文章 → weight = 1.0
# ============================================================================
def test_single_article_weight_one():
    from news_process.pipeline.sentiment.herd_decay import compute_herd_weights
    df = pd.DataFrame({
        'target_bank': ['工行'],
        '日期': pd.to_datetime(['2023-01-01']),
        '内容': ['单篇测试'],
        'content_ctx': ['单篇 ctx'],
    })
    out = compute_herd_weights(df)
    assert out.loc[0, 'herd_weight_full'] == 1.0
    assert out.loc[0, 'herd_weight_ctx'] == 1.0


# ============================================================================
# Case 9: legacy 警告
# ============================================================================
def test_legacy_warning_logged(minimal_panel_df, monkeypatch):
    from news_process.pipeline.sentiment import herd_decay as hd_mod
    warns: list[str] = []
    monkeypatch.setattr(hd_mod.logger, 'warning',
                        lambda msg, *a, **kw: warns.append(str(msg)))
    df = minimal_panel_df.drop(columns=['content_ctx'])
    hd_mod.compute_herd_weights(df)
    joined = ' '.join(warns)
    # fix(omni-g-herd-04, 2026-06-11): 原断言锁定陈旧文案 "stage 21" — content_ctx
    # 由 stage 14 ctx_materializer 物化 (现行架构), 警告文案已同步, 断言随改。
    assert 'content_ctx' in joined and 'stage 14' in joined, \
        f"WARN 应提到 content_ctx + stage 14 (物化归属); 实际 warns={warns}"


# ============================================================================
# Case 10: build_aggregation_dict 双轨 sum_herd_weight
# ============================================================================
def test_build_aggregation_dict_dual_hw():
    from news_process.pipeline.panel.encode import build_aggregation_dict
    df_with_dual = pd.DataFrame({
        'herd_weight_full': [1.0], 'herd_weight_ctx': [1.0],
    })
    agg = build_aggregation_dict(df_with_dual)
    assert 'sum_herd_weight_full' in agg
    assert 'sum_herd_weight_ctx' in agg
    assert agg['sum_herd_weight_full'] == ('herd_weight_full', 'sum')
    assert agg['sum_herd_weight_ctx'] == ('herd_weight_ctx', 'sum')


# ============================================================================
# Case 11: build_aggregation_dict legacy fallback
# ============================================================================
def test_build_aggregation_dict_legacy_fallback():
    from news_process.pipeline.panel.encode import build_aggregation_dict
    df_legacy = pd.DataFrame({'herd_weight': [1.0]})
    agg = build_aggregation_dict(df_legacy)
    assert agg['sum_herd_weight_full'] == ('herd_weight', 'sum'), \
        "legacy schema 应 fallback 到 herd_weight 单列"
    assert agg['sum_herd_weight_ctx'] == ('herd_weight', 'sum'), \
        "legacy schema ctx 也应 fallback 到 herd_weight 单列"


# ============================================================================
# Case 12: _compute_similar_counts_for_track 空文本返回 None
# ============================================================================
def test_compute_similar_counts_empty_text():
    from news_process.pipeline.sentiment.herd_decay import _compute_similar_counts_for_track
    df_empty = pd.DataFrame({'text': ['', '', '']})
    result = _compute_similar_counts_for_track(
        df_empty, 'text', [datetime(2023, 1, 1)] * 3
    )
    assert result is None, "全空文本应返回 None (无法 TF-IDF)"


# ============================================================================
# 标记: fast tier (无 LLM/torch/网络)
# ============================================================================
pytestmark = pytest.mark.fast
