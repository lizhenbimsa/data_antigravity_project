"""
test_omni_fix_llm_peer.py — omni 审计修复回归锁 (g-llm-peer 组, 2026-06-11)
================================================================================
锁定 9 条 confirmed/confirmed-latent 缺陷的修复后行为 (fix omni-g-llm-peer-01..-09),
防静默 revert。全部使用合成 DataFrame + 合成 bank_names/fintech_dict + stub LLM,
不依赖盘上大数据、不调外部 API、不触碰 _llm_cache.db。

覆盖:
  -01 tone IV 文章级 leave-out (剔除与焦点银行共提的 t-1 报道) + 缺列回退披露
  -02 句子筛选: 变体 → canonical 归一后数 distinct (防同实体子串双计)
  -03 句子筛选: 焦点银行必须在句中 (修 PEER_PROMPT 虚假前提)
  -04 _normalize_peer_names: 泛称歧义守卫 (子串命中>1 → 拒绝) + difflib OOV 拒绝
  -05 cutoff 五档结构性逐位相同 — 披露注释在位 (producer + 消费端 CUTOFF_VARS)
  -06 NEWS_PROCESS_LLM_OFFLINE 离线守卫: 缓存 miss → raise LLMCacheMissError
  -07 '查证后零同行' → count/compete_idx 显式 0 + llm_peer_queried 旗标
  -08 等权均值文档修正 + llm_peer_n_effective 诊断列 (count 与均值域不一致披露)
  -09 _normalize_peer_names 保序去重 (dict.fromkeys 替代 list(set))

# 白话: 让 LLM 找"某银行的竞争对手"再用对手的舆论情绪当工具变量, 这条链上
# 的修复锁: 算对手情绪时要剔掉和本行同篇报道的文章(否则自己影响自己);
# 同一家银行的不同叫法(工行/工商银行)只算一家; LLM 报出的不认识的银行名
# 宁可扔掉也不硬凑近似匹配; LLM 明确说"没有对手"时记 0, 和"没问过"区分开;
# 离线模式下缓存没命中就报错, 绝不偷偷联网花钱。
"""
import asyncio
import json
import math
import os
import sys
from pathlib import Path

import pandas as pd
import pytest

# 注入 news_process 父目录, 解析 ``news_process.*`` (与既有测试一致)
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.panel import llm_peer_iv as lpi  # noqa: E402

# ============================================================================
# 共用 fixture: 合成 bank_names / fintech 词典 / 变体映射
# ============================================================================

_BANK_ICBC = '中国工商银行'
_BANK_CCB = '中国建设银行'

_V2C = {
    _BANK_ICBC: _BANK_ICBC, '工商银行': _BANK_ICBC, '工行': _BANK_ICBC,
    _BANK_CCB: _BANK_CCB, '建设银行': _BANK_CCB, '建行': _BANK_CCB,
}
_ALL_NAMES = set(_V2C.keys())
_CANONICAL = [_BANK_ICBC, _BANK_CCB]
_FT_KW = {'金融科技'}


def _mk_df(rows):
    return pd.DataFrame(rows)


def _extract(sentence_rows, focal):
    df = _mk_df([
        {'标题': '', '内容': s, 'co_mentioned_banks': co}
        for s, co in sentence_rows
    ])
    return lpi._extract_multi_bank_sentences(
        df, _ALL_NAMES, _FT_KW, _V2C, focal)


# ============================================================================
# -02: 变体子串双计被规范化击破
# ============================================================================

class TestSentenceFilterCanonicalDistinct:
    def test_single_bank_via_variants_rejected(self):
        """'中国工商银行' 同实体命中变体 '工商银行' — 规范化后仅 1 家 → 拒绝
        (旧实现 banks_found={'中国工商银行','工商银行'} 伪装成 ≥2 银行过筛)."""
        sents = _extract(
            [('中国工商银行佛山分行获评金融科技创新成果奖项。', '中国建设银行')],
            focal=_BANK_ICBC)
        assert sents == []

    def test_two_variants_same_canon_rejected(self):
        """'建设银行'+'建行' 双变体同 canonical → 仍 1 家 → 拒绝."""
        sents = _extract(
            [('建设银行即建行积极运用金融科技大数据技术升级。', '中国工商银行')],
            focal=_BANK_CCB)
        assert sents == []

    def test_true_two_bank_sentence_kept(self):
        """真双银行比较句 (焦点在句中) → 保留."""
        s = '工商银行与建设银行在金融科技领域展开正面竞争。'
        sents = _extract([(s, _BANK_CCB)], focal=_BANK_ICBC)
        assert sents == [s]


# ============================================================================
# -03: 焦点银行必须在句中 (修 PEER_PROMPT 虚假前提)
# ============================================================================

class TestSentenceFilterFocalRequired:
    def test_sentence_without_focal_rejected(self):
        """两家非焦点银行的句子 (旧实现 46% 过筛) → 现拒绝."""
        v2c = dict(_V2C)
        v2c.update({'招商银行': '招商银行', '招行': '招商银行'})
        all_names = set(v2c.keys())
        df = _mk_df([{
            '标题': '',
            '内容': '工商银行与建设银行在金融科技领域展开正面竞争。',
            'co_mentioned_banks': _BANK_ICBC,
        }])
        sents = lpi._extract_multi_bank_sentences(
            df, all_names, _FT_KW, v2c, '招商银行')
        assert sents == []

    def test_focal_matched_via_variant_kept(self):
        """焦点以变体出现 ('工行') 也算在句中 — 经 canonical 归一识别."""
        s = '工行与建设银行在金融科技赛道上对标布局智能风控。'
        sents = _extract([(s, _BANK_CCB)], focal=_BANK_ICBC)
        assert sents == [s]

    def test_fintech_keyword_still_required(self):
        """条件 2 未连带放松: 双银行但无 fintech 词 → 拒绝."""
        sents = _extract(
            [('工商银行与建设银行签署常规授信合作协议确认函。', _BANK_CCB)],
            focal=_BANK_ICBC)
        assert sents == []


# ============================================================================
# -04: 归一化泛称歧义守卫 + OOV 拒绝
# ============================================================================

class TestNormalizePeerNames:
    _CANON_RURAL = ['北京农村商业银行', '上海农村商业银行', '中国农业银行']

    def test_generic_substring_ambiguous_rejected(self):
        """泛称 '农村商业银行' ⊂ 多家规范名 → 歧义拒绝 (旧实现 max(key=len) 任取)."""
        out = lpi._normalize_peer_names(['农村商业银行'], self._CANON_RURAL)
        assert out == []

    def test_unique_substring_accepted(self):
        """唯一子串命中 (全称带后缀) → 仍接受."""
        out = lpi._normalize_peer_names(
            ['中国工商银行股份有限公司'], _CANONICAL)
        assert out == [_BANK_ICBC]

    def test_oov_not_difflib_absorbed(self):
        """'中国农业发展银行' (政策行, 词典外, difflib ratio=0.857) →
        不再吸附为 '中国农业银行', 直接丢弃."""
        out = lpi._normalize_peer_names(
            ['中国农业发展银行'], ['中国农业银行'])
        assert out == []

    def test_variant_mapping_still_works(self):
        out = lpi._normalize_peer_names(['工行'], _CANONICAL,
                                        variant_to_canonical=_V2C)
        assert out == [_BANK_ICBC]

    def test_cutoff_inert(self):
        """fix 后 cutoff 不再影响归一化结果 (difflib 兜底已移除)."""
        raw = ['中国农业发展银行', '工商银行', '农村商业银行']
        outs = [
            lpi._normalize_peer_names(
                raw, self._CANON_RURAL + _CANONICAL,
                variant_to_canonical=_V2C, cutoff=c)
            for c in (0.70, 0.75, 0.80, 0.85, 0.90)
        ]
        assert all(o == outs[0] for o in outs)

    def test_no_difflib_import(self):
        """源码层防 revert: difflib 兜底 import 已移除."""
        src = Path(lpi.__file__).read_text(encoding='utf-8')
        assert 'from difflib import' not in src
        assert 'get_close_matches(' not in src.replace(
            'difflib.get_close_matches', '')  # 注释提及不算


# ============================================================================
# -09: 保序去重 (dict.fromkeys 替代 list(set))
# ============================================================================

class TestNormalizeOrderPreserved:
    def test_order_preserved_dedup(self):
        """LLM '按竞争强度排列' 的输出序保留, 重复去除 — 未来 top-N 截断
        不受 hash 序漂移影响."""
        out = lpi._normalize_peer_names(
            [_BANK_CCB, _BANK_ICBC, _BANK_CCB], _CANONICAL)
        assert out == [_BANK_CCB, _BANK_ICBC]

    def test_variant_dedup_keeps_first_position(self):
        out = lpi._normalize_peer_names(
            ['建行', _BANK_ICBC, _BANK_CCB], _CANONICAL,
            variant_to_canonical=_V2C)
        assert out == [_BANK_CCB, _BANK_ICBC]


# ============================================================================
# -06: 离线确定性守卫 (NEWS_PROCESS_LLM_OFFLINE)
# ============================================================================

class _StubMissCache:
    def get(self, *a, **k):
        return None


class _StubHitCache:
    def get(self, *a, **k):
        return '{"peers": []}'


class TestOfflineGuard:
    _MODEL_CFG = {'model_name': 'stub-m', 'api_key': 'k', 'base_url': 'http://x'}

    def test_offline_miss_raises(self, monkeypatch):
        """LLM_OFFLINE=1 + 缓存 miss → raise LLMCacheMissError, 不触网."""
        monkeypatch.setattr(lpi, 'LLM_OFFLINE', True)
        with pytest.raises(lpi.LLMCacheMissError):
            asyncio.run(lpi._call_llm_peer(
                None, None, 'X银行', 2018, ['句子一。'],
                self._MODEL_CFG, _StubMissCache()))

    def test_offline_cache_hit_returns(self, monkeypatch):
        """LLM_OFFLINE=1 + 缓存命中 → 正常返回缓存值 (零网络)."""
        monkeypatch.setattr(lpi, 'LLM_OFFLINE', True)
        bank, year, result = asyncio.run(lpi._call_llm_peer(
            None, None, 'X银行', 2018, ['句子一。'],
            self._MODEL_CFG, _StubHitCache()))
        assert (bank, year) == ('X银行', 2018)
        assert json.loads(result) == {'peers': []}

    def test_guard_flag_exists_and_default_off(self):
        """守卫开关存在; 测试环境未设环境变量时默认关闭 (不改生产首跑)."""
        assert hasattr(lpi, 'LLM_OFFLINE')
        if not os.environ.get('NEWS_PROCESS_LLM_OFFLINE'):
            assert lpi.LLM_OFFLINE is False

    def test_offline_miss_propagates_through_compute(self, peer_env,
                                                     monkeypatch):
        """守卫必须穿透 asyncio.gather(return_exceptions=True) loud-fail —
        若被吞成普通失败日志, peer 网络会以残缺结果静默继续构建
        (镜像 tone_llms as_completed 的立即中止语义)."""
        async def _raise_miss(session, semaphore, bank, year, sentences,
                              model_cfg, cache):
            raise lpi.LLMCacheMissError(f'stub 离线 miss: {bank}_{year}')

        monkeypatch.setattr(lpi, '_call_llm_peer', _raise_miss)
        with pytest.raises(lpi.LLMCacheMissError, match='stub 离线 miss'):
            lpi.compute_llm_peer_iv(_build_panel(), _build_exploded())


# ============================================================================
# -01: 文章级 leave-out 索引/均值 (单元层)
# ============================================================================

class TestLeaveOutHelpers:
    def _index(self):
        df = _mk_df([
            # peer B 在 2017: 1 篇与 A 共提 (tone +1), 1 篇 solo (tone -1)
            {'target_bank': 'B', 'year': 2017,
             'co_mentioned_banks': 'A', 'llm_vote_score_full': 1},
            {'target_bank': 'B', 'year': 2017,
             'co_mentioned_banks': '', 'llm_vote_score_full': -1},
            {'target_bank': 'B', 'year': 2017,
             'co_mentioned_banks': 'C', 'llm_vote_score_full': 1},
        ])
        return lpi._build_article_tone_index(df, ['llm_vote_score_full'])

    def test_leave_out_excludes_co_mentioned(self):
        idx = self._index()
        # 排除与 A 共提 → mean(-1, 1) = 0.0 (≠ plain mean 1/3)
        assert lpi._peer_leave_out_tone_mean(
            idx, 'B', 2017, 'llm_vote_score_full', 'A') == pytest.approx(0.0)

    def test_no_co_mention_equals_plain_mean(self):
        idx = self._index()
        # 排除不存在的 'Z' → 与 panel 级 plain mean 等价
        assert lpi._peer_leave_out_tone_mean(
            idx, 'B', 2017, 'llm_vote_score_full', 'Z'
        ) == pytest.approx(1 / 3)

    def test_all_articles_co_mentioned_returns_none(self):
        df = _mk_df([
            {'target_bank': 'B', 'year': 2017,
             'co_mentioned_banks': 'A;C', 'llm_vote_score_full': 1},
        ])
        idx = lpi._build_article_tone_index(df, ['llm_vote_score_full'])
        assert lpi._peer_leave_out_tone_mean(
            idx, 'B', 2017, 'llm_vote_score_full', 'A') is None

    def test_missing_peer_year_returns_none(self):
        idx = self._index()
        assert lpi._peer_leave_out_tone_mean(
            idx, 'B', 2016, 'llm_vote_score_full', 'A') is None

    def test_na_tone_skipped(self):
        df = _mk_df([
            {'target_bank': 'B', 'year': 2017,
             'co_mentioned_banks': '', 'llm_vote_score_full': pd.NA},
            {'target_bank': 'B', 'year': 2017,
             'co_mentioned_banks': '', 'llm_vote_score_full': 1},
        ])
        df['llm_vote_score_full'] = df['llm_vote_score_full'].astype('Int8')
        idx = lpi._build_article_tone_index(df, ['llm_vote_score_full'])
        assert lpi._peer_leave_out_tone_mean(
            idx, 'B', 2017, 'llm_vote_score_full', 'Z') == pytest.approx(1.0)


# ============================================================================
# 集成: compute_llm_peer_iv 全链 (stub LLM, 合成词典/面板)
# -01 leave-out 数值 / -07 零同行+queried / -08 n_effective / -05 五档相同
# ============================================================================

class _StubLLMCache:
    """替身 LLMCache — 严禁测试触碰真 _llm_cache.db."""

    def __init__(self, path):
        self.path = path

    def size(self):
        return 0

    def close(self):
        pass


@pytest.fixture()
def peer_env(tmp_path, monkeypatch):
    """合成 bank_names/fintech 词典 + stub LLM + stub 缓存的 compute 环境."""
    pytest.importorskip('aiohttp')

    bank_names = [
        {'bank_name': _BANK_ICBC, 'variants': ['工商银行', '工行']},
        {'bank_name': _BANK_CCB, 'variants': ['建设银行', '建行']},
    ]
    bn_path = tmp_path / 'bank_names.json'
    bn_path.write_text(json.dumps(bank_names, ensure_ascii=False),
                       encoding='utf-8')
    ft_path = tmp_path / 'fintech_dict.json'
    ft_path.write_text(json.dumps(['金融科技'], ensure_ascii=False),
                       encoding='utf-8')

    monkeypatch.setitem(lpi.CONFIG['paths'], 'bank_names_file', str(bn_path))
    monkeypatch.setitem(lpi.CONFIG['paths'], 'fintech_dict_file', str(ft_path))
    monkeypatch.setattr(lpi, 'MODELS', [
        {'model_name': 'stub-m', 'api_key': 'k', 'base_url': 'http://x'}])
    monkeypatch.setattr(lpi, 'LLMCache', _StubLLMCache)

    calls = []

    async def _stub_call(session, semaphore, bank, year, sentences,
                         model_cfg, cache):
        calls.append((bank, year, tuple(sentences)))
        if bank == _BANK_ICBC:
            return bank, year, json.dumps({'peers': [_BANK_CCB]},
                                          ensure_ascii=False)
        return bank, year, json.dumps({'peers': []})  # affirmative 零同行

    monkeypatch.setattr(lpi, '_call_llm_peer', _stub_call)
    return calls


def _build_panel():
    rows = []
    for bank in (_BANK_ICBC, _BANK_CCB):
        for year in (2017, 2018):
            rows.append({
                'target_bank': bank, 'year': year,
                # (建设,2017) panel 级 tone = 0.0 (= mean(+1,-1)), 用于证明
                # leave-out 值 (-1.0) ≠ 旧 panel 级口径
                'llm_vote_tone_full': 0.0,
                'llm_vote_tone_ctx': 0.5,
                'ln_news_coverage': 2.0,
            })
    return pd.DataFrame(rows)


def _build_exploded(with_article_tone=True):
    sent = '工商银行与建设银行在金融科技领域展开正面竞争。'
    rows = [
        # 焦点 工商 2017: 共提文章 (触发查询)
        {'target_bank': _BANK_ICBC, 'year': 2017, '标题': '', '内容': sent,
         'co_mentioned_banks': _BANK_CCB,
         'llm_vote_score_full': 1, 'llm_vote_score_ctx': 1},
        # 建设 2017: 同一篇共提文章的镜像行 (explode 病根)
        {'target_bank': _BANK_CCB, 'year': 2017, '标题': '', '内容': sent,
         'co_mentioned_banks': _BANK_ICBC,
         'llm_vote_score_full': 1, 'llm_vote_score_ctx': -1},
        # 建设 2017: solo 文章 — leave-out 后唯一幸存者
        {'target_bank': _BANK_CCB, 'year': 2017, '标题': '',
         '内容': '中国建设银行发布金融科技年度专项报告。',
         'co_mentioned_banks': '',
         'llm_vote_score_full': -1, 'llm_vote_score_ctx': 0},
    ]
    df = pd.DataFrame(rows)
    if not with_article_tone:
        df = df.drop(columns=['llm_vote_score_full', 'llm_vote_score_ctx'])
    return df


def _row(panel, bank, year):
    sel = panel[(panel['target_bank'] == bank) & (panel['year'] == year)]
    assert len(sel) == 1
    return sel.iloc[0]


class TestComputeIntegration:
    def test_full_chain(self, peer_env):
        panel = lpi.compute_llm_peer_iv(_build_panel(), _build_exploded())
        calls = peer_env

        # 两家 2017 均被查询 (2018 无共提文章 → 不查)
        assert {(b, y) for b, y, _ in calls} == {
            (_BANK_ICBC, 2017), (_BANK_CCB, 2017)}

        # ── -01: leave-out tone IV ──
        # (工商,2018) lag 2017, peers=[建设]; 建设 2017 排除共提工商的文章后
        # 仅剩 solo (full=-1, ctx=0) → IV ≠ 旧 panel 级口径 0.0
        r = _row(panel, _BANK_ICBC, 2018)
        assert r['llm_peer_tone_iv_full'] == pytest.approx(-1.0)
        assert r['llm_peer_tone_iv_ctx'] == pytest.approx(0.0)
        assert r['llm_peer_count'] == 1
        # ── -08: n_effective (面板内进入均值的 peer 数) ──
        assert r['llm_peer_n_effective'] == 1
        # coverage IV 仍 panel 级 (披露项)
        assert r['llm_peer_coverage_iv'] == pytest.approx(2.0)

        # ── -07: affirmative 零同行 → count/n_effective = 0, tone IV 缺失 ──
        rz = _row(panel, _BANK_CCB, 2018)
        assert rz['llm_peer_count'] == 0
        assert rz['llm_peer_n_effective'] == 0
        assert math.isnan(rz['llm_peer_tone_iv_full'])

        # ── -07: llm_peer_queried 旗标 (同年口径) ──
        assert _row(panel, _BANK_ICBC, 2017)['llm_peer_queried'] == 1
        assert _row(panel, _BANK_CCB, 2017)['llm_peer_queried'] == 1
        assert _row(panel, _BANK_ICBC, 2018)['llm_peer_queried'] == 0
        assert _row(panel, _BANK_CCB, 2018)['llm_peer_queried'] == 0

        # ── -07: compete idx — 查证后零同行 = 0.0, 有同行共现 = 1.0 ──
        assert _row(panel, _BANK_ICBC, 2017)[
            'peer_compete_idx'] == pytest.approx(1.0)
        assert _row(panel, _BANK_CCB, 2017)[
            'peer_compete_idx'] == pytest.approx(0.0)

        # ── -05: cutoff 五档结构性逐位相同 ──
        for fam in ('llm_peer_tone_iv_full', 'llm_peer_count',
                    'llm_peer_coverage_iv'):
            cols = [f'{fam}_{c}' for c in (70, 75, 80, 85, 90)]
            assert all(col in panel.columns for col in cols)
            base = panel[cols[0]]
            for col in cols[1:]:
                pd.testing.assert_series_equal(
                    panel[col], base, check_names=False)

    def test_fallback_without_article_tone(self, peer_env):
        """df_exploded 缺文章级情感列 → 回退旧 panel 级均值 (无 leave-out)."""
        panel = lpi.compute_llm_peer_iv(
            _build_panel(), _build_exploded(with_article_tone=False))
        r = _row(panel, _BANK_ICBC, 2018)
        # panel 级口径: (建设,2017) llm_vote_tone_full = 0.0
        assert r['llm_peer_tone_iv_full'] == pytest.approx(0.0)
        assert r['llm_peer_tone_iv_ctx'] == pytest.approx(0.5)
        assert r['llm_peer_n_effective'] == 1


# ============================================================================
# -05/-08: 源码级披露锁 (producer + 消费端)
# ============================================================================

class TestDisclosures:
    def test_producer_disclosure_in_place(self):
        src = Path(lpi.__file__).read_text(encoding='utf-8')
        assert 'disclosure(omni-g-llm-peer-05' in src
        # -08: '加权' 声称已纠正为等权
        assert '等权同行情感均值' in src
        assert 'LLM-Peer 加权情感 IV' not in src

    def test_consumer_cutoff_vars_disclosure(self):
        from news_process.papers._common import derivative_replication as dr
        src = Path(dr.__file__).read_text(encoding='utf-8')
        assert 'disclosure(omni-g-llm-peer-05' in src

    def test_erratum_keywords_preserved(self):
        """不连带破坏 test_omni_fix_misc 的既有锁 (难度勘误关键词仍在位)."""
        src = Path(lpi.__file__).read_text(encoding='utf-8')
        assert 'difflib.get_close_matches' in src
        assert '命名勘误' in src
