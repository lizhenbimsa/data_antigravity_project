"""WP0 家族映射守恒 gate (计划 = scripts/audit/STATA_VARATTR_AND_CODEBOOK_LONGDESC_EXECUTION_PLAN_2026-07-10.md §5 WP0)。

断言 (计划 §5 WP0 gate 列 + §6 机械闸五件套 ①):
  1. 守恒: Σ家族列数 (剔 tier=pending) == 51 面板实存列数, 0 孤儿, set 相等,
     且 Σ|各家族列清单| == |并集| (封死"同列被两家族重复收录"的 set 盲区);
  2. core 候选 ⊆ panel.columns (pending 豁免), 0 幻影名;
  3. core/pending 逐列 core_rationale 非空;
  4. core(含 pending) 占比 ≤10% (反灌水硬闸);
  5. _index.json schema 键完整 (计划 §1 唯一完整 schema);
  6. 增量 merge 不改存量 (存量条目 tier/状态/rationale/签核只增不改)。

纯读 _index.json + parquet schema (pyarrow, 不载数据), 无 LLM/网络; 产物缺失时 skip
(WP0 尚未在本机跑过的环境不红灯)。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

_NEWS_PROCESS_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = _NEWS_PROCESS_ROOT / 'config' / 'codebook_longdesc' / '_index.json'
PANEL_PATH = _NEWS_PROCESS_ROOT / 'data' / 'processed' / '51_panel_with_controls.parquet'

# 计划 §1 代码块: _index.json 唯一完整 schema
_TOP_REQUIRED_KEYS = ('tier_signoff', 'structural_whitelist', 'families')
_FAMILY_REQUIRED_KEYS = ('file', 'columns', 'tier_by_col', 'core_rationale_by_col',
                         'status', 'batch', 'unit_draft', 'formula_draft',
                         'producer_draft')
_VALID_TIERS = frozenset({'core', 'standard', 'pending'})
_VALID_STATUS = frozenset({'draft', 'final'})


@pytest.fixture(scope='module')
def index_doc():
    if not INDEX_PATH.exists():
        pytest.skip(f'_index.json 不存在 (WP0 未跑): {INDEX_PATH}')
    return json.loads(INDEX_PATH.read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def panel_columns():
    if not PANEL_PATH.exists():
        pytest.skip(f'51 面板不存在: {PANEL_PATH}')
    pq = pytest.importorskip('pyarrow.parquet')
    return list(pq.ParquetFile(str(PANEL_PATH)).schema_arrow.names)


def _iter_families(index_doc):
    return index_doc['families'].items()


# ---------------------------------------------------------------------------
# 5. schema 键完整
# ---------------------------------------------------------------------------

def test_index_schema_keys_complete(index_doc):
    for key in _TOP_REQUIRED_KEYS:
        assert key in index_doc, f'_index.json 顶层缺键: {key}'
    assert isinstance(index_doc['tier_signoff'], dict)
    assert index_doc['structural_whitelist'] == ['target_bank', 'year'], \
        '结构列豁免白名单须逐列点名 target_bank/year (计划 §1a 类别 7)'
    assert index_doc['families'], 'families 为空'
    for fid, fam in _iter_families(index_doc):
        assert fid.startswith('F') and fid[1:].isdigit(), f'family_id 编号非法: {fid}'
        for key in _FAMILY_REQUIRED_KEYS:
            assert key in fam, f'{fid} 缺键: {key}'
        assert fam['status'] in _VALID_STATUS, f'{fid} status 非法: {fam["status"]}'
        assert fam['columns'], f'{fid} 列清单为空'
        assert set(fam['tier_by_col']) == set(fam['columns']), \
            f'{fid} tier_by_col 键集 != columns'
        bad_tiers = set(fam['tier_by_col'].values()) - _VALID_TIERS
        assert not bad_tiers, f'{fid} 非法 tier: {bad_tiers}'


# ---------------------------------------------------------------------------
# 1. 守恒 gate
# ---------------------------------------------------------------------------

def test_conservation_no_orphan_no_duplicate(index_doc, panel_columns):
    panel_set = set(panel_columns)
    listed_nonpending: list[str] = []
    listed_all: list[str] = []
    for fid, fam in _iter_families(index_doc):
        listed_all.extend(fam['columns'])
        listed_nonpending.extend(
            c for c in fam['columns'] if fam['tier_by_col'].get(c) != 'pending')
    # Σ|各家族列清单| == |并集| (防同列重复收录, 计划 §6 ① 后式)
    assert len(listed_all) == len(set(listed_all)), \
        '同列被多家族重复收录: ' + str(
            sorted({c for c in listed_all if listed_all.count(c) > 1})[:10])
    # set 相等 + Σ==N (剔 pending)
    nonpending_set = set(listed_nonpending)
    orphan = panel_set - nonpending_set
    phantom = nonpending_set - panel_set
    assert not orphan, f'孤儿列 (面板有而家族无) {len(orphan)}: {sorted(orphan)[:10]}'
    assert not phantom, f'幻影列 (家族有而面板无, 非 pending) {len(phantom)}: {sorted(phantom)[:10]}'
    assert len(listed_nonpending) == len(panel_columns), \
        f'守恒破: Σ非 pending 家族列 {len(listed_nonpending)} != 面板列数 {len(panel_columns)}'


def test_pending_cols_absent_from_panel(index_doc, panel_columns):
    """pending = 外部财务哨兵/未物化 treatment, 定义上不在面板 (在则应升 core)。"""
    panel_set = set(panel_columns)
    for fid, fam in _iter_families(index_doc):
        for c, t in fam['tier_by_col'].items():
            if t == 'pending':
                assert c not in panel_set, \
                    f'{fid}/{c} tier=pending 但面板实存 — 应重跑 WP0 升 core'


# ---------------------------------------------------------------------------
# 2. core ⊆ panel.columns (pending 豁免) — 0 幻影名
# ---------------------------------------------------------------------------

def test_core_subset_of_panel(index_doc, panel_columns):
    panel_set = set(panel_columns)
    for fid, fam in _iter_families(index_doc):
        for c, t in fam['tier_by_col'].items():
            if t == 'core':
                assert c in panel_set, f'{fid}/{c} tier=core 但不在面板 — 幻影名'


# ---------------------------------------------------------------------------
# 3. core/pending 逐列 rationale 非空 (计划 §1a 反灌水守卫: 无条件全量)
# ---------------------------------------------------------------------------

def test_core_rationale_nonempty(index_doc):
    for fid, fam in _iter_families(index_doc):
        for c, t in fam['tier_by_col'].items():
            if t in ('core', 'pending'):
                r = fam['core_rationale_by_col'].get(c, '')
                assert isinstance(r, str) and r.strip(), \
                    f'{fid}/{c} (tier={t}) core_rationale 为空'


# ---------------------------------------------------------------------------
# 4. core(含 pending) 占比 ≤10%
# ---------------------------------------------------------------------------

def test_core_ratio_le_10pct(index_doc, panel_columns):
    n_core_pending = sum(
        1 for _, fam in _iter_families(index_doc)
        for t in fam['tier_by_col'].values() if t in ('core', 'pending'))
    ratio = n_core_pending / len(panel_columns)
    assert ratio <= 0.10, f'反灌水闸: core+pending 占比 {ratio:.2%} > 10%'
    assert n_core_pending > 0, 'core 清单非空 (计划 §1a gate)'


# ---------------------------------------------------------------------------
# 6. 增量 merge 不改存量 (纯函数级测试, 不动盘上 _index.json)
# ---------------------------------------------------------------------------

def _mk_family(file, columns, tier='standard', status='draft', rationale=None):
    return {
        'file': file,
        'columns': list(columns),
        'tier_by_col': {c: tier for c in columns},
        'core_rationale_by_col': dict(rationale or {}),
        'status': status,
        'batch': None,
        'unit_draft': 'u', 'formula_draft': 'f', 'producer_draft': 'p',
    }


def test_incremental_merge_preserves_existing():
    from news_process.scripts.audit.build_codebook_family_map import merge_index

    existing = {
        'tier_signoff': {'date': '2026-07-11', 'user_ack': True,
                         'signed_manifest_sha': 'abc'},
        'structural_whitelist': ['target_bank', 'year'],
        'families': {
            'F001': _mk_family('F001_alpha.md', ['alpha_full', 'alpha_ctx'],
                               tier='core', status='final',
                               rationale={'alpha_full': 'r1', 'alpha_ctx': 'r2'}),
            'F002': _mk_family('F002_beta.md', ['beta_full']),
        },
    }
    # fresh 重算: F001 机械初判翻成 standard/draft (须被存量压制), 且新增 1 列;
    # 另出现全新家族 gamma
    fresh = {
        'tier_signoff': {},
        'structural_whitelist': ['target_bank', 'year'],
        'families': {
            'F001': _mk_family('F001_alpha.md',
                               ['alpha_full', 'alpha_ctx', 'alpha_ss'],
                               tier='standard', status='draft'),
            'F009': _mk_family('F009_gamma.md', ['gamma_full']),
        },
    }
    merged = merge_index(existing, fresh)
    # 顶层签核只增不改
    assert merged['tier_signoff'] == existing['tier_signoff']
    fam1 = merged['families']['F001']
    # 存量 tier/status/rationale 不被 fresh 改写
    assert fam1['status'] == 'final'
    assert fam1['tier_by_col']['alpha_full'] == 'core'
    assert fam1['core_rationale_by_col']['alpha_full'] == 'r1'
    # 新列 additive 追加 (取 fresh 初判 tier)
    assert 'alpha_ss' in fam1['columns']
    assert fam1['tier_by_col']['alpha_ss'] == 'standard'
    # 存量家族 F002 原样保留
    assert merged['families']['F002'] == existing['families']['F002']
    # 全新家族续号追加 (max=2 → F003), 不重排存量
    new_ids = set(merged['families']) - {'F001', 'F002'}
    assert new_ids == {'F003'}
    assert merged['families']['F003']['file'] == 'F009_gamma.md'
    # merge 是纯函数: 不得篡改传入的 existing 对象
    assert existing['families']['F001']['columns'] == ['alpha_full', 'alpha_ctx']


def test_merge_first_run_passthrough():
    from news_process.scripts.audit.build_codebook_family_map import merge_index
    fresh = {'tier_signoff': {}, 'structural_whitelist': ['target_bank', 'year'],
             'families': {'F001': _mk_family('F001_a.md', ['a'])}}
    assert merge_index(None, fresh) == fresh
    assert merge_index({}, fresh) == fresh


# ---------------------------------------------------------------------------
# 签核哈希 gate (计划 §1a signed_manifest_sha 机制): 当前复算哈希 == 签核哈希,
# 不等即强制重新签核 (防"签核对象已非签核时清单"与豁免蠕变双假绿)
# ---------------------------------------------------------------------------

def test_tier_signoff_matches_manifest(index_doc):
    ts = index_doc.get('tier_signoff') or {}
    if not ts:
        pytest.skip('tier_signoff 空置 (未签核) — WP0 签核前属预期')
    from news_process.scripts.audit.build_codebook_family_map import (
        compute_signed_manifest_sha,
    )
    assert ts.get('user_ack') is True, 'tier_signoff.user_ack 须为 true'
    assert ts.get('date') and ts.get('method'), 'tier_signoff 缺 date/method'
    current = compute_signed_manifest_sha(index_doc)
    assert ts.get('signed_manifest_sha') == current, (
        f'签核清单漂移: 当前联合哈希 {current} != 签核时 '
        f'{ts.get("signed_manifest_sha")} — core/pending/结构白名单已变, 须重新签核'
    )


def test_signed_manifest_sha_deterministic():
    """哈希函数确定性: 同清单 (families 键名/列序无关) → 同哈希。"""
    from news_process.scripts.audit.build_codebook_family_map import (
        compute_signed_manifest_sha,
    )
    a = {'structural_whitelist': ['year', 'target_bank'],
         'families': {'F001': _mk_family('f1.md', ['b', 'a'], tier='core',
                                         rationale={'a': 'r', 'b': 'r'})}}
    b = {'structural_whitelist': ['target_bank', 'year'],
         'families': {'F009': _mk_family('f9.md', ['a', 'b'], tier='core',
                                         rationale={'a': 'r', 'b': 'r'})}}
    assert compute_signed_manifest_sha(a) == compute_signed_manifest_sha(b)


# ---------------------------------------------------------------------------
# 2026-07-11 整改 gate: P2-⑦ 渐进前缀兜底 / P2-⑧ 引文池关键词 / P1-1 骨架段首标题
# ---------------------------------------------------------------------------

def test_kw_stop_contains_criteria_suffixes():
    """P2-⑧/NIT: 判据后缀 sent/win1 与归族层级前缀 l2/l2c/l3 必须在停用词表 —
    'sent' 切词进关键词会把无关 sentiment 文献顶到网络家族引文池首位。"""
    from news_process.scripts.audit.build_codebook_family_map import _KW_STOP
    assert {'sent', 'win1', 'l2', 'l2c', 'l3'} <= set(_KW_STOP)


def test_kw_expansion_dictionary_anchors():
    """P2-⑧: 词典基名 → dictionary/构成性锚映射 (锚 token 逐条对白名单池核验)。"""
    from news_process.scripts.audit.build_codebook_family_map import (
        _KW_EXPANSION,
        family_keywords,
    )
    assert 'rfab036' in _KW_EXPANSION['du']                    # Du et al. 2022 RoF
    assert 'when is a liability' in _KW_EXPANSION['loughran']  # L&M 2011 JF
    assert 'ceq.2021.04.10' in _KW_EXPANSION['jiang']
    assert 'ssrn.3446388' in _KW_EXPANSION['bian']
    assert 'power of the pen' in _KW_EXPANSION['you']
    for k in ('du', 'loughran', 'jiang', 'bian', 'you', 'yao'):
        assert 'dictionary' in _KW_EXPANSION[k]
    # 组件家族 (F219 形态) 关键词现在携带构成性锚 token
    kws = family_keywords('l2_du_2022_neg_count', ['du_2022_neg_count_full'])
    assert 'rfab036' in kws
    # 判据后缀不再进关键词 (F078 形态)
    kws_net = family_keywords('net_bank_clustering',
                              ['bank_clustering', 'bank_clustering_sent',
                               'bank_clustering_win1'])
    assert 'sent' not in kws_net and 'win1' not in kws_net


def test_fallback_prefix_bases():
    """P2-⑦: 程序化拼名基名渐进剥尾 (du_2022_neg_count → du_2022_neg → du_2022),
    单 token 短前缀停止 (防 'du' 级噪声)。"""
    from news_process.scripts.audit.build_codebook_family_map import (
        _fallback_prefix_bases,
    )
    fb = _fallback_prefix_bases(['du_2022_neg_count'])
    assert 'du_2022' in fb and 'du_2022_neg' in fb
    assert 'du' not in fb
    assert _fallback_prefix_bases(['already']) == []


def test_source_excerpt_fallback_resolves_programmatic_family():
    """P2-⑦: 完整基名零命中的列族经前缀兜底至少给出 producer 模块与源码摘录。"""
    from news_process.scripts.audit.build_codebook_family_map import source_excerpt_for
    sources = {
        'pipeline/sentiment/tone_words.py':
            "DICTS = ['du_2022', 'loughran']\n" + 'x = 1\n' * 40,
    }
    excerpt, producers = source_excerpt_for(['du_2022_neg_count_full'], sources)
    assert producers == ['pipeline/sentiment/tone_words.py']
    assert 'SSOT 前缀兜底' in excerpt or '前缀' in excerpt


def test_emit_skeletons_inline_seg_titles(tmp_path):
    """P1-1 契约: 骨架 CORE 以【构念与来源】开头、VAR 以【变体差分】开头
    (组装器不再前置这两个标题 — 双侧口径互锁, 组装产物零双重标题)。"""
    from news_process.pipeline.panel import codebook_longdesc as cl
    from news_process.scripts.audit.build_codebook_family_map import (
        emit_family_skeletons,
    )
    merged = {'families': {'F001': {
        'file': 'F001_alpha.md', 'columns': ['alpha_full'],
        'tier_by_col': {'alpha_full': 'standard'},
        'core_rationale_by_col': {}, 'status': 'draft', 'batch': None,
        'unit_draft': 'u', 'formula_draft': 'f', 'producer_draft': 'p'}}}
    n_new, n_exist = emit_family_skeletons(merged, tmp_path)
    assert (n_new, n_exist) == (1, 0)
    fam = cl.parse_family_md(str(tmp_path / 'F001_alpha.md'), family_id='F001')
    assert fam.core_text.startswith('【构念与来源】')
    assert fam.var_sections['alpha_full'].startswith('【变体差分】')
    # 幂等: 已存在绝不覆盖
    assert emit_family_skeletons(merged, tmp_path) == (0, 1)


def test_real_skeletons_zero_double_titles(index_doc):
    """P1-1 回归闸: 盘上全库骨架/写手 md 的人工区零双重段首标题。"""
    from news_process.pipeline.panel import codebook_longdesc as cl
    lib = cl.load_library(str(INDEX_PATH.parent))
    assert lib is not None
    for fid, fam in lib.families.items():
        assert cl._DOUBLE_SEG_TITLE_RE.search(fam.core_text) is None, fid
        for col, txt in fam.var_sections.items():
            assert cl._DOUBLE_SEG_TITLE_RE.search(txt) is None, f'{fid}/{col}'


# ---------------------------------------------------------------------------
# 附: 结构列豁免白名单列必须实存且不为 core (计划 §1a 类别 7)
# ---------------------------------------------------------------------------

def test_structural_whitelist_columns(index_doc, panel_columns):
    panel_set = set(panel_columns)
    tier_lookup = {}
    for _, fam in _iter_families(index_doc):
        tier_lookup.update(fam['tier_by_col'])
    for c in index_doc['structural_whitelist']:
        assert c in panel_set, f'结构列 {c} 不在面板'
        assert tier_lookup.get(c) == 'standard', \
            f'结构列 {c} 不进 core (tier 应为 standard, 实为 {tier_lookup.get(c)})'
