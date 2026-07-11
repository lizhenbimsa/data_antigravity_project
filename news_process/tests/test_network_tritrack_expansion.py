"""网络指标三轨化 (①类) + 网络构造判据敏感性 (②类) — 族专属 gate 测试。

执行计划 = scripts/audit/NETWORK_TRITRACK_AND_CRITERIA_EXECUTION_PLAN_2026-07-02.md
本文件承载计划层 G 的 G1(a)-(k) 断言 (随层 A→F 落地逐节补齐):
  - 层 A (h): 银行∧银行句级共现原语 — 假阳性反例 / 标题第 0 句正例 /
    句窗距离语义 / phantom 反例 (仅幸存银行入参)。
  - (a)  盘上 40_panel_yearly.parquet 含全部 80 新列 (缺盘 skip)。
  - (b)  .dta 标签源 build_variable_labels 对全部新列非列名 fallback。
  - (c)  diag/sim 嵌入族落入 parity 判定面 (n10 逃逸防线)。
  - (d)  ①-A 分母逐轨 (ctx 分子借 full 分母即红)。
  - (e)  ② 无后缀路径对 Phase 0 冻结 fixture 等价 (禁真空自对拍)。
  - (f)  ② _sent ⊆ _win1 ⊆ 同篇 边数单调。
  - (g)  codebook 判据后缀归一 (category/source_stage)。
  - (i)(j) D6/D8 语义断言 (fallback 剔除 / 双标题拦截 / per-W-轨降级隔离)。
  - (k)  ② 标签 bank-bank 限定 + diag/legacy 标签 W 来源措辞。
"""

import json
import os

import numpy as np
import pandas as pd
import pytest

from news_process.core.text.ahocorasick import load_exclusion_patterns
from news_process.core.text.entity_context import (
    _split_sentences,
    bank_pairs_within_sentence_window,
    map_bank_sentence_positions,
    prepend_title,
)

_FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


# ============================================================================
# 共用 fixture (镜像 test_omni_fix_entity.py 的排除规则构造)
# ============================================================================

@pytest.fixture
def exclusions(tmp_path):
    data = {
        'negation_patterns': ['中国银行业', '中国银行间',
                              '中国银行保险监督管理委员会', '涉农行业'],
        'short_name_context_exclusions': {
            'context_window': 6,
            'exclusions': {'农行': ['涉农行'], '工行': ['施工行']},
        },
    }
    p = tmp_path / 'bank_name_exclusions.json'
    p.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return load_exclusion_patterns(str(p))


ALIASES = {
    '中国工商银行': ['中国工商银行', '工商银行', '工行'],
    '中国农业银行': ['中国农业银行', '农业银行', '农行'],
    '中国建设银行': ['中国建设银行', '建设银行', '建行'],
}


# ============================================================================
# 层 A (G1(h)): map_bank_sentence_positions / bank_pairs_within_sentence_window
# ============================================================================

class TestLayerAMapBankSentencePositions:

    def test_false_anchor_excluded(self, exclusions):
        """R4 反例: '涉农行业' 不得为 '农行' 锚定句 (否定+短名排除生效)。"""
        neg_ac, short_excl, cw = exclusions
        body = ('与当地财政、农业、林业、海洋、涉农行业协会等部门开展对接。'
                '工商银行公布财报。市场反应平稳。')
        pos = map_bank_sentence_positions(
            '', body, ALIASES, negation_ac=neg_ac,
            short_name_exclusions=short_excl, context_window=cw)
        assert '中国农业银行' not in pos
        assert pos['中国工商银行'] == {1}

    def test_false_anchor_bare_match_without_exclusions(self):
        """无排除参数时保持裸匹配 (向后兼容, 同 has_unexcluded_occurrence)。"""
        body = '涉农行业协会发布报告。无关句子。再一句。'
        pos = map_bank_sentence_positions('', body, ALIASES)
        assert '中国农业银行' in pos  # 裸匹配误报是旧行为, 生产必传排除参数

    def test_title_is_sentence_zero(self, exclusions):
        """D19 标题正例: 标题双银行、正文锚句分散 → 标题第 0 句同句成边。"""
        neg_ac, short_excl, cw = exclusions
        title = '工商银行与建设银行签署战略合作'
        body = ('工商银行方面表示合作意义重大。分析人士持观望态度。'
                '另据报道其他行业动态若干。建设银行未予置评。')
        pos = map_bank_sentence_positions(
            title, body, ALIASES, negation_ac=neg_ac,
            short_name_exclusions=short_excl, context_window=cw)
        # 标题 = 第 0 句 (prepend_title 补中文句号)
        assert 0 in pos['中国工商银行']
        assert 0 in pos['中国建设银行']
        edges_sent = bank_pairs_within_sentence_window(pos, win_radius=0)
        assert ('中国工商银行', '中国建设银行') in edges_sent

    def test_sentence_index_matches_split_sentences(self, exclusions):
        """句索引口径 = prepend_title 后 _split_sentences (与 _ss 轨同源)。"""
        neg_ac, short_excl, cw = exclusions
        title = '市场综述'
        body = '工商银行上涨。！？建设银行下跌。'  # 连续标点/退化段
        text = prepend_title(title, body)
        sentences = _split_sentences(text)
        pos = map_bank_sentence_positions(
            title, body, ALIASES, negation_ac=neg_ac,
            short_name_exclusions=short_excl, context_window=cw)
        for bank, idx_set in pos.items():
            for i in idx_set:
                assert any(a in sentences[i] for a in ALIASES[bank])

    def test_win_radius_semantics(self, exclusions):
        """win1 距离语义: 邻句成边、隔 2 句不成边; sent 更严。"""
        neg_ac, short_excl, cw = exclusions
        body = ('工商银行公布财报。市场平稳。建设银行发布公告。'
                '另一无关句。农业银行召开会议。')
        pos = map_bank_sentence_positions(
            '', body, ALIASES, negation_ac=neg_ac,
            short_name_exclusions=short_excl, context_window=cw)
        assert pos['中国工商银行'] == {0}
        assert pos['中国建设银行'] == {2}
        assert pos['中国农业银行'] == {4}
        sent = bank_pairs_within_sentence_window(pos, win_radius=0)
        win1 = bank_pairs_within_sentence_window(pos, win_radius=1)
        assert sent == set()          # 无同句
        assert win1 == set()          # 全部隔 ≥2 句
        win2 = bank_pairs_within_sentence_window(pos, win_radius=2)
        assert ('中国工商银行', '中国建设银行') in win2
        # canonical 名序 = sorted(): '农'(U+519C) < '建'(U+5EFA)
        assert ('中国农业银行', '中国建设银行') in win2

    def test_adjacent_sentences_win1_edge(self, exclusions):
        neg_ac, short_excl, cw = exclusions
        body = '工商银行公布财报。建设银行发布公告。无关句子若干。'
        pos = map_bank_sentence_positions(
            '', body, ALIASES, negation_ac=neg_ac,
            short_name_exclusions=short_excl, context_window=cw)
        assert bank_pairs_within_sentence_window(pos, 0) == set()
        assert bank_pairs_within_sentence_window(pos, 1) == {
            ('中国工商银行', '中国建设银行')}

    def test_single_sentence_short_text(self, exclusions):
        """短文本无字符回退: 单句双银行必同句 (D10)。"""
        neg_ac, short_excl, cw = exclusions
        body = '工商银行与建设银行同日发布公告'  # 无句读 → 单句
        pos = map_bank_sentence_positions(
            '', body, ALIASES, negation_ac=neg_ac,
            short_name_exclusions=short_excl, context_window=cw)
        assert bank_pairs_within_sentence_window(pos, 0) == {
            ('中国工商银行', '中国建设银行')}

    def test_phantom_bank_not_in_input_no_edge(self, exclusions):
        """G1(f) phantom 反例: 非幸存银行 (不入参) 即使同句也不可能成边。"""
        neg_ac, short_excl, cw = exclusions
        surviving = {k: v for k, v in ALIASES.items() if k != '中国农业银行'}
        body = '工商银行与农业银行同日发布公告。建设银行未回应。'
        pos = map_bank_sentence_positions(
            '', body, surviving, negation_ac=neg_ac,
            short_name_exclusions=short_excl, context_window=cw)
        assert '中国农业银行' not in pos
        edges = bank_pairs_within_sentence_window(pos, 1)
        assert all('中国农业银行' not in e for e in edges)

    def test_empty_inputs(self):
        assert map_bank_sentence_positions('', '', ALIASES) == {}
        assert map_bank_sentence_positions('标题', '正文。', {}) == {}
        assert bank_pairs_within_sentence_window({}, 1) == set()


# ============================================================================
# ② 判据 (G1(e)(f)): build_adjacency_matrix / compute_bank_network_centrality
# ============================================================================

def _make_synthetic_frame():
    """固定合成小图 (与 fixture 冻结脚本逐字节同一构造, 勿改)。"""
    rows = []
    docs = [
        ('d1', ['银行甲', '银行乙'], '市场动态',
         '银行甲发布公告。银行乙随后回应。分析师关注。'),
        ('d2', ['银行甲', '银行乙'], '合作新闻',
         '银行甲与银行乙签署协议。无关句。再一无关句。'),
        ('d3', ['银行乙', '银行丙'], '行业观察',
         '银行乙披露数据。中间隔一句。银行丙披露数据。'),
        ('d4', ['银行甲', '银行丙', '银行丁'], '深度报道',
         '银行甲与银行丙达成合作。银行丁保持观望。市场平稳。'),
        ('d5', ['银行戊'], '单家新闻', '银行戊召开会议。会议顺利。'),
        ('d6', ['银行丁', '银行戊'], '综合报道',
         '银行丁发布公告。一。二。三。银行戊发布公告。'),
    ]
    for docid, banks, title, body in docs:
        for b in banks:
            rows.append({'docid': docid, 'target_bank': b, 'year': 2020,
                         '标题': title, '内容': body})
    df = pd.DataFrame(rows)
    banks_all = sorted({r['target_bank'] for r in rows})
    panel = pd.DataFrame([{'target_bank': b, 'year': 2020}
                          for b in banks_all])
    return df, panel


@pytest.fixture
def scan_ctx_identity(monkeypatch):
    """判据扫描上下文: 别名=自身, 无排除, win_radius=1 (测试自足, 不依赖生产词表)。"""
    import news_process.core.text.entity_context as ec
    import news_process.pipeline.panel.network_spillover as ns
    monkeypatch.setattr(ec, 'get_target_aliases', lambda bank, f: [bank])
    monkeypatch.setattr(ns, '_BANK_SCAN_CTX', ('', None, None, 5, 1))
    return ns


def _edge_set(adj_df):
    banks = list(adj_df.index)
    return {(banks[i], banks[j])
            for i in range(len(banks)) for j in range(i + 1, len(banks))
            if adj_df.iloc[i, j] > 0}


class TestCriteriaAdjacency:

    def test_edge_monotonicity_sent_win1_article(self, scan_ctx_identity):
        """G1(f): _sent ⊆ _win1 ⊆ 同篇 (边集包含链) + 精确边集。"""
        ns = scan_ctx_identity
        df, _ = _make_synthetic_frame()
        adj_art, _ = ns.build_adjacency_matrix(df, 2020, criterion='article')
        adj_w1, _ = ns.build_adjacency_matrix(df, 2020, criterion='win1')
        adj_st, _ = ns.build_adjacency_matrix(df, 2020, criterion='sent')
        e_art, e_w1, e_st = map(_edge_set, (adj_art, adj_w1, adj_st))
        assert e_st <= e_w1 <= e_art
        assert e_art == {('银行乙', '银行甲'), ('银行丙', '银行乙'),
                         ('银行丙', '银行甲'), ('银行丁', '银行甲'),
                         ('银行丁', '银行丙'), ('银行丁', '银行戊')}
        assert e_w1 == {('银行乙', '银行甲'), ('银行丙', '银行甲'),
                        ('银行丁', '银行甲'), ('银行丁', '银行丙')}
        assert e_st == {('银行乙', '银行甲'), ('银行丙', '银行甲')}
        # 权重口径: 每篇每对 +1 — 甲乙在 d1(win1)+d2(sent) 均命中 win1
        assert adj_w1.loc['银行甲', '银行乙'] == 2
        assert adj_st.loc['银行甲', '银行乙'] == 1

    def test_phantom_bank_never_edges(self, scan_ctx_identity):
        """G1(f) phantom 反例: 文中提及但非幸存 (不在 target_bank 行) 的银行不成边。"""
        ns = scan_ctx_identity
        df, _ = _make_synthetic_frame()
        # d2 正文再提第三家 '银行己' (无对应 target_bank 行 → 非幸存)
        df.loc[df['docid'] == 'd2', '内容'] = (
            '银行甲与银行乙、银行己签署协议。无关句。再一无关句。')
        for crit in ('win1', 'sent'):
            adj, banks = ns.build_adjacency_matrix(df, 2020, criterion=crit)
            assert '银行己' not in banks
            assert all('银行己' not in e for e in _edge_set(adj))

    def test_unknown_criterion_raises(self, scan_ctx_identity):
        ns = scan_ctx_identity
        df, _ = _make_synthetic_frame()
        with pytest.raises(ValueError):
            ns.build_adjacency_matrix(df, 2020, criterion='bogus')

    def test_suffix_criterion_mismatch_raises(self, scan_ctx_identity):
        ns = scan_ctx_identity
        df, panel = _make_synthetic_frame()
        with pytest.raises(ValueError):
            ns.compute_bank_network_centrality(
                panel, df, criterion='win1', suffix='_sent')
        with pytest.raises(ValueError):
            ns.compute_bank_network_centrality(
                panel, df, criterion='article', suffix='_win1')


# BLAS 浮点漂移列 (memory: panel-3-network-cols-nondeterministic) + 谱分解列
_LOOSE_COLS = {'bank_clustering', 'bank_cfbetween_cent',
               'bank_harmonic_cent', 'bank_eigen_cent'}


class TestCriteriaCentralityColumns:

    def test_article_path_matches_frozen_baseline(self):
        """G1(e): criterion='article' 对 Phase 0 冻结基线逐指标等价
        (fixture 由改动前 HEAD 代码在同一合成帧上冻结, 禁真空自对拍)。"""
        import news_process.pipeline.panel.network_spillover as ns
        fx_path = os.path.join(_FIXTURE_DIR,
                               'network_criteria_baseline_v0.json')
        with open(fx_path, encoding='utf-8') as f:
            fx = json.load(f)
        df, panel = _make_synthetic_frame()
        out = ns.compute_bank_network_centrality(
            panel, df, criterion='article', suffix='')
        out = out.sort_values('target_bank').reset_index(drop=True)
        assert out['target_bank'].tolist() == fx['banks']
        for col, expected in fx['metrics'].items():
            assert col in out.columns, f"冻结基线列缺失: {col}"
            got = out[col].to_numpy(dtype=float)
            exp = np.array([np.nan if v is None else v for v in expected],
                           dtype=float)
            atol = 1e-6 if col in _LOOSE_COLS else 1e-12
            assert np.allclose(got, exp, rtol=1e-9, atol=atol,
                               equal_nan=True), f"{col} 偏离冻结基线"

    def test_criterion_suffix_columns_land(self, scan_ctx_identity):
        """② 落列: _win1/_sent 后缀列存在且与 canonical 并排 (33×3)。"""
        ns = scan_ctx_identity
        df, panel = _make_synthetic_frame()
        out = ns.compute_bank_network_centrality(
            panel, df, criterion='article', suffix='')
        out = ns.compute_bank_network_centrality(
            out, df, criterion='win1', suffix='_win1')
        out = ns.compute_bank_network_centrality(
            out, df, criterion='sent', suffix='_sent')
        base_cols = [c for c in out.columns
                     if c.startswith(('bank_', 'net_', 'gf_'))
                     and not c.endswith(('_win1', '_sent'))
                     and c != 'bank_cogn_mean']
        for c in base_cols:
            assert f'{c}_win1' in out.columns, f'缺 {c}_win1'
            assert f'{c}_sent' in out.columns, f'缺 {c}_sent'
        # 判据边集更严 → 度中心度单调不增 (对逐行非 NaN 值)
        m = out[['bank_degree_cent', 'bank_degree_cent_win1',
                 'bank_degree_cent_sent']].dropna()
        assert (m['bank_degree_cent_win1']
                <= m['bank_degree_cent'] + 1e-12).all()
        assert (m['bank_degree_cent_sent']
                <= m['bank_degree_cent_win1'] + 1e-12).all()


# ============================================================================
# ①-A (G1(d)): industry_neg_shock 三轨 — 分母严格逐轨
# ============================================================================

def _make_shock_panel():
    """合成 bank-year 面板: ctx 轨分子分母与 full 刻意不同,
    借 full 分母会得到错误值 → G1(d) 可判别。"""
    return pd.DataFrame([
        # year 2020: 三家银行, full 与 ctx 的 (分子, 分母) 不同
        {'target_bank': 'A', 'year': 2020,
         'neg_count_full': 2, 'n_articles_llm_valid': 10,
         'neg_count_ctx': 1, 'n_articles_llm_valid_ctx': 5,
         'neg_count_ss': 0, 'n_articles_llm_valid_ss': 5,
         'n_articles': 10},
        {'target_bank': 'B', 'year': 2020,
         'neg_count_full': 4, 'n_articles_llm_valid': 10,
         'neg_count_ctx': 4, 'n_articles_llm_valid_ctx': 8,
         'neg_count_ss': 1, 'n_articles_llm_valid_ss': 10,
         'n_articles': 10},
        {'target_bank': 'C', 'year': 2020,
         'neg_count_full': 0, 'n_articles_llm_valid': 20,
         'neg_count_ctx': 0, 'n_articles_llm_valid_ctx': 10,
         'neg_count_ss': 0, 'n_articles_llm_valid_ss': 2,  # <5 → 守门 NaN
         'n_articles': 20},
    ])


class TestIndustryNegShockTriTrack:

    def test_per_track_denominator_strict(self):
        """G1(d): ctx 分子必配 ctx 分母 — 借 full 分母即红。"""
        from news_process.pipeline.panel.network_brokerage import (
            compute_industry_neg_shock,
        )
        out = compute_industry_neg_shock(_make_shock_panel())
        # canonical: ratios = 0.2, 0.4, 0.0 → LOO(A) = (0.4+0)/2 = 0.2
        assert out.loc[out['target_bank'] == 'A',
                       'industry_neg_shock'].iloc[0] == pytest.approx(0.2)
        # ctx: ratios = 1/5=0.2, 4/8=0.5, 0/10=0.0 → LOO(A) = (0.5+0)/2 = 0.25
        # (若错借 full 分母 10: ratios=0.1,0.4,0.0 → LOO(A)=0.2 ≠ 0.25)
        assert out.loc[out['target_bank'] == 'A',
                       'industry_neg_shock_ctx'].iloc[0] == pytest.approx(0.25)
        # ss: C 的分母 2 < min_count=5 → 守门 NaN → LOO(A) 只含 B: 1/10=0.1
        assert out.loc[out['target_bank'] == 'A',
                       'industry_neg_shock_ss'].iloc[0] == pytest.approx(0.1)
        # lag1 三轨列存在 (T=1 全 NaN)
        for sfx in ('', '_ctx', '_ss'):
            col = f'industry_neg_shock_lag1{sfx}'
            assert col in out.columns
            assert out[col].isna().all()

    def test_missing_ctx_denominator_skips_track_only(self):
        """D2: ctx 分母列缺失 → 仅跳过 ctx 轨 (不借 full 分母), canonical/ss 照算。"""
        from news_process.pipeline.panel.network_brokerage import (
            compute_industry_neg_shock,
        )
        pn = _make_shock_panel().drop(columns=['n_articles_llm_valid_ctx'])
        out = compute_industry_neg_shock(pn)
        assert 'industry_neg_shock' in out.columns
        assert 'industry_neg_shock_ss' in out.columns
        assert 'industry_neg_shock_ctx' not in out.columns
        assert 'industry_neg_shock_lag1_ctx' not in out.columns


# ============================================================================
# ①-B (G1(i)(j)): cogn 三轨 + emb diag W-轨 — D6/D8 语义断言
# ============================================================================

def _make_emb_frame():
    """两年 × 三银行合成帧: content_ctx/ss 与 原始'内容' 可判别 (D6 断言用)。

    标记设计: 原始'内容' 含 token 'FULLBODY'; content_ctx 含 'CTXWIN';
    content_ss 含 'SSWIN'; **2019 (滞后年) 的 a2** 是 ss fallback (回退全文,
    不得入 ss 超级文档 — 嵌入永远吃 lag_year 文本); 标题含 'TITLETOK'
    (ctx/ss 超级文档禁 title 通道 → 不得出现)。
    """
    rows = []
    for year, docs in {
        2019: [('a1', 'ㄱ', False), ('a2', 'ㄴ', True), ('a3', 'ㄷ', False)],
        2020: [('b1', 'ㄱ', False), ('b2', 'ㄴ', False), ('b3', 'ㄷ', False)],
    }.items():
        for docid, bank, ss_fb in docs:
            rows.append({
                'docid': docid, 'target_bank': f'银行{bank}', 'year': year,
                '标题': f'TITLETOK-{docid}',
                '内容': f'FULLBODY-{docid} ' + ('正文若干。' * 30),
                'content_full': f'FULLBODY-{docid} ' + ('正文若干。' * 30),
                'content_ctx': f'CTXWIN-{docid} ' + ('窗口文本。' * 30),
                'content_ss': (f'FULLBODY-{docid} ' + ('正文若干。' * 30)
                               if ss_fb else
                               f'SSWIN-{docid} ' + ('同句文本。' * 30)),
                'ctx_is_fallback': False,
                'ss_is_fallback': ss_fb,
            })
    df = pd.DataFrame(rows)
    banks = sorted(df['target_bank'].unique())
    panel = pd.DataFrame([
        {'target_bank': b, 'year': y,
         'llm_vote_tone_full': 0.1, 'llm_vote_tone_ctx': 0.2,
         'llm_vote_tone_ss': 0.3}
        for b in banks for y in (2019, 2020)])
    return df, panel


class TestEmbDiagWTrackUnits:

    def _patch_engine(self, monkeypatch, captured, fail_tracks=()):
        """mock _eng.embed_texts: 记录文本, 按内容 hash 产确定性向量;
        fail_tracks 中的轨 (按文本标记判别) 返回 None 模拟 miss。"""
        import news_process.pipeline.panel.network_spillover as ns

        def _fake_embed(texts, spec, **kw):
            marker = ('CTXWIN' if any('CTXWIN' in t for t in texts) else
                      'SSWIN' if any('SSWIN' in t for t in texts) else
                      'FULL')
            captured.setdefault(marker, []).extend(texts)
            if marker in fail_tracks:
                raise RuntimeError('mock 离线 miss')
            rng = [abs(hash(t)) % 997 for t in texts]
            base = np.array([[1.0, r / 997.0, 0.5] for r in rng])
            return base
        monkeypatch.setattr(ns._eng, 'embed_texts', _fake_embed)
        # _LARGE_SPEC 置空: 单模型口径, 聚焦 W-轨语义 (parity 由专测覆盖)
        monkeypatch.setattr(ns, '_LARGE_SPEC', {})
        return ns

    def test_d6_fallback_and_title_excluded(self, monkeypatch):
        """G1(i): ss fallback 行不入 ss 超级文档; ctx/ss 禁 title 通道;
        ctx 超级文档 == content_ctx 原样拼接。"""
        captured = {}
        ns = self._patch_engine(monkeypatch, captured)
        df, panel = _make_emb_frame()
        out = ns.compute_embedding_peer_network(df, panel)
        # ctx/ss 轨列已产 (2020 年, lag=2019 有数据)
        assert 'bank_emb_sim_mean_lag1_ctx' in out.columns
        assert 'emb_peer_tone_diag_lag1_ctx' in out.columns
        assert 'bank_emb_sim_mean_lag1_ss' in out.columns
        # (i-1) 滞后年 (2019) 的 ss fallback 行 (a2) 全文文本不得进 ss 超级文档
        ss_texts = ' '.join(captured.get('SSWIN', []))
        assert 'FULLBODY-a2' not in ss_texts
        assert 'SSWIN-a1' in ss_texts and 'SSWIN-a3' in ss_texts
        # (i-2) 禁 title 通道: ctx/ss 超级文档零 TITLETOK
        assert 'TITLETOK' not in ' '.join(captured.get('CTXWIN', []))
        assert 'TITLETOK' not in ss_texts
        # (i-3) full 轨保持 标题+内容 拼接 (canonical 口径不动)
        assert 'TITLETOK' in ' '.join(captured.get('FULL', []))
        # (i-4) ctx 超级文档 == content_ctx 原样拼接 (标记逐篇齐)
        ctx_texts = ' '.join(captured.get('CTXWIN', []))
        for d in ('a1', 'a2', 'a3'):
            assert f'CTXWIN-{d}' in ctx_texts

    def test_diag_prefix_registered_in_parity_net(self):
        """G1(c): diag 新列必须落入嵌入族判定面 (n10 静默逃逸教训)。"""
        from news_process.tests.test_embedding_coprimary_parity import (
            _is_emb_family,
        )
        for col in ('emb_peer_tone_diag_lag1_ctx', 'emb_peer_tone_diag_lag1_ss',
                    'bank_emb_sim_mean_lag1_ctx', 'bank_emb_sim_mean_lag1_ss',
                    'emb_peer_tone_diag_lag1_lg_ctx'):
            assert _is_emb_family(col), col
        # cogn 是 TF-IDF 非嵌入 → 不入 parity 面 (合法免 _lg)
        assert not _is_emb_family('bank_cogn_mean_ctx')

    def test_d8_per_unit_isolation(self, monkeypatch):
        """G1(j): ctx 轨嵌入失败 → 仅 ctx 单元 NaN, full 族与 ss 单元不连坐。"""
        captured = {}
        ns = self._patch_engine(monkeypatch, captured,
                                fail_tracks=('CTXWIN',))
        df, panel = _make_emb_frame()
        out = ns.compute_embedding_peer_network(df, panel)
        y2020 = out[out['year'] == 2020]
        # full 族照产 (2020 有 lag 数据)
        assert y2020['bank_emb_sim_mean_lag1'].notna().any()
        assert y2020['emb_peer_tone_lag1_full'].notna().any()
        # ctx 单元全 NaN (本单元降级)
        assert out['bank_emb_sim_mean_lag1_ctx'].isna().all()
        # ss 单元不连坐, 照产
        assert y2020['bank_emb_sim_mean_lag1_ss'].notna().any()

    def test_cogn_tritrack_d6(self, monkeypatch):
        """cogn 三轨: 列落地 + [0,1] + canonical 不变式 (同帧自证)。"""
        import news_process.pipeline.panel.network_spillover as ns
        df, panel = _make_emb_frame()
        before = ns.compute_cognitive_proximity(
            df.drop(columns=['content_ctx', 'content_ss',
                             'ctx_is_fallback', 'ss_is_fallback']),
            panel.copy())
        after = ns.compute_cognitive_proximity(df, panel.copy())
        # canonical 列不受三轨新增影响 (缺轨列时旧行为; 有轨列时同值)
        pd.testing.assert_series_equal(before['bank_cogn_mean'],
                                       after['bank_cogn_mean'],
                                       check_names=False)
        assert 'bank_cogn_mean_ctx' in after.columns
        assert 'bank_cogn_mean_ss' in after.columns
        for c in ('bank_cogn_mean_ctx', 'bank_cogn_mean_ss'):
            vv = after[c].dropna()
            assert ((vv >= -1e-6) & (vv <= 1 + 1e-6)).all()
        # 缺 content 列 → 该轨列不产 (D6 家族级守卫)
        assert 'bank_cogn_mean_ctx' not in before.columns


# ============================================================================
# 层 E (G1(g)): codebook 判据后缀归一 — category/source_stage 正确落族
# ============================================================================

class TestCodebookCriteriaSuffixNormalization:

    def _fns(self):
        from news_process.pipeline.panel.codebook import (
            _infer_category,
            _infer_label,
            _infer_source_stage,
        )
        return _infer_category, _infer_source_stage, _infer_label

    def test_sent_suffix_not_sentiment(self):
        """'sent' 子串陷阱 (终验 identity-trap-1): 全部 _sent 结构列 = 网络指标。"""
        cat, stage, _ = self._fns()
        for base in ('bank_degree_cent', 'net_assortativity_yr', 'gf_total',
                     'bank_is_hub', 'bank_clustering', 'bank_constraint'):
            for sfx in ('_win1', '_sent'):
                col = base + sfx
                assert cat(col) == '网络指标', col
                assert stage(col) != '未知', col
                # 判据变体与无后缀孪生同族 (元数据不分裂)
                assert stage(col) == stage(base), col

    def test_net_yr_endswith_survives_suffix(self):
        cat, stage, _ = self._fns()
        for col in ('net_density_yr_win1', 'net_modularity_yr_sent',
                    'net_diameter_yr_win1'):
            assert stage(col) == stage('net_density_yr'), col
            assert cat(col) == '网络指标', col

    def test_eight_bare_bases_whitelist_both_functions(self):
        """8 个无 'cent' 基名白名单双接 source_stage 与 category (终验 minor)。"""
        cat, stage, _ = self._fns()
        for base in ('bank_clustering', 'bank_constraint', 'bank_ego_density',
                     'bank_effective_size', 'bank_avg_nbr_deg',
                     'bank_coreness', 'bank_ci', 'bank_is_hub'):
            assert stage(base) != '未知', base
            assert cat(base) == '网络指标', base

    def test_new_family_tokens(self):
        """D17: neg_shock/cogn/emb_peer/emb_sim 族不再落 '未知'。"""
        cat, stage, _ = self._fns()
        for col in ('industry_neg_shock', 'industry_neg_shock_ctx',
                    'industry_neg_shock_lag1_ss', 'bank_cogn_mean',
                    'bank_cogn_mean_ctx', 'emb_peer_tone_lag1_full',
                    'emb_peer_tone_diag_lag1_ctx', 'bank_emb_sim_mean_lag1',
                    'bank_emb_sim_mean_lag1_lg_ss'):
            assert stage(col) != '未知', col
        assert cat('bank_cogn_mean_ss') == '网络指标'
        assert cat('bank_emb_sim_mean_lag1_ctx') == '网络指标'
        assert cat('industry_neg_shock_ctx') == '情感指标'

    def test_label_carries_bank_bank_qualifier(self):
        """G1(k)-codebook: 判据变体推断标签带「银行间」限定 (WP3 中文化后
        bank-bank 的中文对应物, 仍与 _ss 银行∧金科「同句轨」措辞可区分)。"""
        _, _, label = self._fns()
        lbl = label('bank_degree_cent_sent')
        assert '银行间' in lbl
        lbl_w = label('net_density_yr_win1')
        assert '银行间' in lbl_w
        # 既有列不受归一影响: 剥后缀对无判据后缀列必须是 no-op (结果审计
        # code-meta-2: 原恒真式改为直接锁 no-op 性质 + 冻结基名推断输出)
        from news_process.pipeline.panel.codebook import (
            _strip_criteria_suffix,
        )
        assert _strip_criteria_suffix('bank_degree_cent') == (
            'bank_degree_cent', None)
        assert _strip_criteria_suffix('llm_vote_tone_full') == (
            'llm_vote_tone_full', None)
        assert label('bank_degree_cent') == 'Network Centrality'
        assert 'bank-bank' not in label('bank_degree_cent')


# ============================================================================
# G1(a)(b)(k): 落盘存在性 + .dta 标签源非 fallback + 措辞断言
# (结果审计 closure-1/closure-2/break-it-3-1 补落地)
# ============================================================================

def _all_new_columns():
    """本次扩展 +80 新列全集 (SSOT: NETWORK_METRIC_BASES × 判据 + ①类清单)。"""
    from news_process.pipeline.panel.network_spillover import (
        NETWORK_METRIC_BASES,
    )
    crit = [f'{b}{s}' for b in NETWORK_METRIC_BASES for s in ('_win1', '_sent')]
    shock = ['industry_neg_shock_ctx', 'industry_neg_shock_ss',
             'industry_neg_shock_lag1_ctx', 'industry_neg_shock_lag1_ss']
    emb = []
    for w in ('ctx', 'ss'):
        emb += [f'bank_cogn_mean_{w}',
                f'bank_emb_sim_mean_lag1_{w}', f'bank_emb_sim_mean_lag1_lg_{w}',
                f'emb_peer_tone_diag_lag1_{w}', f'emb_peer_tone_diag_lag1_lg_{w}']
    return crit, shock, emb


class TestNewColumnsLandingAndLabels:

    def test_g1a_real_output_columns_present(self):
        """G1(a): 盘上 40_panel_yearly.parquet 含全部 80 新列 (缺盘 skip)。"""
        pq = os.path.join(os.path.dirname(__file__), '..', 'data',
                          'processed', '40_panel_yearly.parquet')
        if not os.path.exists(pq):
            pytest.skip('40_panel_yearly.parquet 不在盘上 (fresh clone)')
        cols = set(pd.read_parquet(pq, columns=None).columns)
        crit, shock, emb = _all_new_columns()
        missing = [c for c in (*crit, *shock, *emb) if c not in cols]
        assert not missing, f'落盘缺列: {missing}'
        assert len(crit) + len(shock) + len(emb) == 80

    def test_g1b_dta_labels_not_colname_fallback(self):
        """G1(b): stage-46 .dta 标签源 (build_variable_labels) 对全部新列
        (含 _lg 孪生) 非列名 fallback 且 ≤80 UTF-8 字节
        (镜像 test_network_metrics_expansion 先例; 源② export.py 经
        _apply_label_fallback 复用同一启发式源 + 自带 100% 覆盖硬断言)。"""
        from news_process.pipeline.panel.stata_export import (
            build_variable_labels,
        )
        crit, shock, emb = _all_new_columns()
        cols = [*crit, *shock, *emb, 'industry_neg_shock', 'bank_cogn_mean']
        df = pd.DataFrame({c: [0.0] for c in cols})
        labels = build_variable_labels(df, {c: c for c in cols})
        fallback = [c for c in cols if labels[c] == c]
        assert not fallback, f'标签退化为列名: {fallback}'
        overlong = [c for c in cols
                    if len(labels[c].encode('utf-8')) > 80]
        assert not overlong, f'标签超 80 字节: {overlong}'

    def test_g1k_label_wording(self):
        """G1(k)-.dta: ② 标签含「银行间」限定 (WP3 中文化后的 bank-bank 对应物,
        不与 _ss 文本轨「同句轨」混同); diag/legacy 标签含 W 来源子串。"""
        from news_process.pipeline.panel.stata_export import (
            build_variable_labels,
        )
        crit, _, _ = _all_new_columns()
        wcols = ['emb_peer_tone_lag1_ctx', 'emb_peer_tone_lag1_ss',
                 'emb_peer_tone_diag_lag1_ctx', 'emb_peer_tone_diag_lag1_ss',
                 'bank_emb_sim_mean_lag1_ctx', 'bank_emb_sim_mean_lag1_ss']
        cols = [*crit, *wcols]
        df = pd.DataFrame({c: [0.0] for c in cols})
        labels = build_variable_labels(df, {c: c for c in cols})
        for c in crit:
            assert '银行间' in labels[c], f'{c}: {labels[c]}'
        for c in wcols:
            assert 'W=' in labels[c], f'{c} 缺 W 来源子串: {labels[c]}'


# ---------------------------------------------------------------------------
# G4 (八入口审计计划 2026-07-10): 火灾甩卖混淆诊断块的零方差守卫
# ---------------------------------------------------------------------------


class TestFireSaleConfoundDiag:
    """混淆诊断 corr(cent_t-1, shock_t) 的配对子集零方差守卫 (G4)。

    病灶: Series.corr 是 pairwise dropna 语义 — T=2 下 lag 后配对子集仅剩
    2018 年且该年 shock 全 0 → numpy corrcoef 除 0 → RuntimeWarning 漏 stderr。
    旧"全局 std>0"判法对此无效 (shock 2017 有方差, 全局判定放行)。
    修法 = 配对完备子集 (concat+dropna) 上双侧判 std>0。
    """

    @staticmethod
    def _make_diag_panel():
        """2 银行 × {2017,2018}: shock 2017 两行不同非零 (全局有方差,
        证伪旧全局判法), 2018 两行全 0 (配对子集零方差); lag 后配对子集=2018。"""
        return pd.DataFrame({
            'target_bank': ['甲银行', '甲银行', '乙银行', '乙银行'],
            'year': [2017, 2018, 2017, 2018],
            'brokerage_eigen_cent': [0.10, 0.40, 0.20, 0.80],
            'industry_neg_shock': [0.10, 0.0, 0.30, 0.0],
        })

    def test_paired_subset_guard_no_runtimewarning(self):
        """守卫逻辑等价重演: 配对子集判法在 error-filter 下零 RuntimeWarning。

        (catch_warnings 包真函数调用不会翻红 — 诊断块 try/except 外壳会把升级
        后的异常吞成"混淆诊断失败" WARNING, 故此处在 try 外重演修后判定逻辑。)
        """
        import warnings

        panel = self._make_diag_panel().sort_values(
            ['target_bank', 'year']).reset_index(drop=True)
        _lag_cs = panel.groupby('target_bank')['brokerage_eigen_cent'].shift(1)
        with warnings.catch_warnings():
            warnings.simplefilter('error', RuntimeWarning)
            _pair = pd.concat(
                [_lag_cs, panel['industry_neg_shock']], axis=1).dropna()
            guard = (len(_pair) >= 2
                     and _pair.iloc[:, 0].std() > 0
                     and _pair.iloc[:, 1].std() > 0)
        # 配对子集 = 2018 两行, shock 侧 std=0 → 守卫必须拒绝
        assert not guard, '配对子集零方差应被守卫拒绝 (旧全局判法在此放行=病灶)'
        # 证伪旧判法: 全局双侧 std>0 均为真 → 旧守卫会放行
        assert _lag_cs.std() > 0 and panel['industry_neg_shock'].std() > 0

    def test_real_function_skips_cleanly(self, caplog, monkeypatch):
        """调真函数: caplog 有"跳过"INFO、无"混淆诊断失败"WARNING, 产列正常。"""
        import logging

        from news_process.pipeline.panel import network_brokerage as nb_module
        from news_process.pipeline.panel.network_brokerage import (
            compute_fire_sale_interaction,
        )

        # stage logger propagate=False (core/logging.py:277) → caplog 捕不到;
        # 仓内先例 (test_omni_fix_herd._quiet_logger): 换成可传播的普通 logger。
        test_logger = logging.getLogger('test_fire_sale_diag')
        test_logger.handlers.clear()
        test_logger.setLevel(logging.DEBUG)
        monkeypatch.setattr(nb_module, 'logger', test_logger)

        panel = self._make_diag_panel()
        with caplog.at_level(logging.INFO, logger='test_fire_sale_diag'):
            out = compute_fire_sale_interaction(panel)
        assert 'brokerage_fire_sale' in out.columns
        text = caplog.text
        assert '混淆诊断失败' not in text, (
            '守卫应在 corr 前拦截零方差, 不应走 except 兜底')
        assert '配对子集样本不足/零方差, 跳过' in text
