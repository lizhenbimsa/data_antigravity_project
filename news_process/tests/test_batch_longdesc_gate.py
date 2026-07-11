"""batch_longdesc_gate 五件套一键运行器 gate 测试 (计划 §6)。

全部用 tmp_path 假库 + 假 panel (镜像 test_codebook_longdesc.py fixture 工艺),
**不依赖真实 config/codebook_longdesc/ 655 家族库状态** (WP4 滚动落地期状态随批漂移)。

覆盖 (任务规格 5 项):
  1. 全过 → --promote-final 生效且只改指定家族 status (他家族/签核块零触碰);
  2. 一家族字数不足 → exit 1 且零迁移;
  3. 越权 DOI → FAIL (final 级判定, draft 状态 + new_dois 自声明也不豁免 — v2.9
     draft 出口只属组装期 check_longdesc_whitelist, 批收尾闸刻意禁用);
  4. 守恒破坏 → 拒跑 (逐家族闸不跑, 零迁移);
  5. 报告 JSON schema (逐家族逐闸 pass/fail + 数字)。
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from news_process.pipeline.panel import codebook_longdesc as cl
from news_process.scripts.audit import batch_longdesc_gate as blg

# ============================================================================
# fixture 家族库构造 (镜像 test_codebook_longdesc.py, 白名单注入不触真实 874)
# ============================================================================

WL_DOIS = [f'10.1000/wl{i}' for i in range(1, 15)]
WL_SET = {cl.normalize_doi(d) for d in WL_DOIS}

_LONG_TITLE = ('A sufficiently long empirical study of bank fintech news sentiment '
               'measurement construction and validation methodology, part ')


def _cite(i: int, doi=None, ctype='journal', venue='Journal of Finance', **kw):
    c = {
        'doi': WL_DOIS[i] if doi is None else doi,
        'type': ctype,
        'authors': f'Author{i}, A., & Coauthor{i}, B.',
        'year': 2024,
        'title': _LONG_TITLE + str(i),
        'venue': venue,
        'vol': 79, 'issue': 2, 'pages_or_artno': f'{100 + i}-{200 + i}',
    }
    c.update(kw)
    return c


CITES_STD = [_cite(i) for i in range(1, 4)]      # 3 条 (standard 下限)

CORE_STD = '构' * 750       # standard 家族核心长文段地板 700
VAR_STD = '差' * 400        # standard 变体差分段地板 350


def _fam_md_text(fid, columns, core_text, var_texts, citations, *, new_dois=()):
    fm = {
        'family_id': fid, 'columns': list(columns), 'unit': '比率',
        'formula': 'x = a / b',
        'producer': 'pipeline/sentiment/tone_words.py::fn',
        'upstream': ['21_tone_llms.parquet'],
        'citations': citations, 'new_dois': list(new_dois),
    }
    txt = '---\n' + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + '---\n\n'
    txt += '## CORE\n\n' + core_text + '\n\n'
    for c in columns:
        txt += f'## VAR: {c}\n\n{var_texts[c]}\n\n'
    return txt


def make_lib(tmp_path: Path, families) -> str:
    libdir = tmp_path / 'longdesc'
    libdir.mkdir(parents=True, exist_ok=True)
    index = {
        'tier_signoff': {'date': '2026-07-10', 'method': 'test', 'user_ack': True,
                         'signed_manifest_sha': 'testsha'},
        'structural_whitelist': [],
        'families': {},
    }
    for f in families:
        fid = f['fid']
        fname = f'{fid}_test.md'
        index['families'][fid] = {
            'file': fname,
            'columns': list(f['columns']),
            'tier_by_col': f.get('tiers', {c: 'standard' for c in f['columns']}),
            'core_rationale_by_col': {},
            'status': f.get('status', 'draft'),
            'batch': 1,
            'unit_draft': '', 'formula_draft': '', 'producer_draft': '',
        }
        (libdir / fname).write_text(
            _fam_md_text(fid, f['columns'], f.get('core', CORE_STD),
                         f.get('vars', {c: VAR_STD for c in f['columns']}),
                         f.get('cites', CITES_STD),
                         new_dois=f.get('new_dois', ())),
            encoding='utf-8')
    (libdir / '_index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
    return str(libdir)


def _write_panel(tmp_path: Path, cols) -> str:
    df = pd.DataFrame({c: [0.1, 0.2] for c in cols})
    p = tmp_path / 'panel51.parquet'
    df.to_parquet(p)
    return str(p)


def _run(tmp_path, monkeypatch, families, run_fids='F001', panel_cols=None,
         promote=True):
    """构库 + 假 panel + monkeypatch 白名单 → 跑 main(); 返回 (rc, report, libdir)。"""
    libdir = make_lib(tmp_path, families)
    all_cols = [c for f in families for c in f['columns']]
    ppath = _write_panel(tmp_path, panel_cols if panel_cols is not None else all_cols)
    rpath = str(tmp_path / 'report.json')
    monkeypatch.setattr(blg, '_load_whitelist', lambda: set(WL_SET))
    argv = ['--families', run_fids, '--longdesc-dir', libdir,
            '--panel', ppath, '--report', rpath]
    if promote:
        argv.append('--promote-final')
    rc = blg.main(argv)
    report = json.loads(Path(rpath).read_text(encoding='utf-8'))
    return rc, report, libdir


TWO_FAMS = [
    {'fid': 'F001', 'columns': ['tone_a']},
    {'fid': 'F002', 'columns': ['tone_b']},
]


# ============================================================================
# ① 全过 → promote 生效且只改指定家族 status
# ============================================================================

def test_all_pass_promote_only_specified(tmp_path, monkeypatch):
    rc, report, libdir = _run(tmp_path, monkeypatch, TWO_FAMS, run_fids='F001')
    assert rc == 0
    assert report['all_pass'] is True
    assert report['refused'] is None
    assert report['promoted'] == ['F001']
    fe = report['families']['F001']
    assert fe['pass'] is True
    assert all(fe['gates'][k]['pass'] for k in blg.GATE_KEYS)

    idx = json.loads((Path(libdir) / '_index.json').read_text(encoding='utf-8'))
    # 指定家族迁 final; 未指定家族与签核块零触碰
    assert idx['families']['F001']['status'] == 'final'
    assert idx['families']['F002']['status'] == 'draft'
    assert idx['tier_signoff']['signed_manifest_sha'] == 'testsha'
    assert idx['structural_whitelist'] == []
    # 增量局部更新: 其余键原样
    assert idx['families']['F001']['columns'] == ['tone_a']


def test_promote_is_idempotent_and_rendered_tail_materialized(tmp_path, monkeypatch):
    """全过路径顺带验证: 引文渲染尾节被物化回写 (闸 4 前置 materialize, 幂等)。"""
    rc, report, libdir = _run(tmp_path, monkeypatch, TWO_FAMS, run_fids='F001,F002')
    assert rc == 0
    assert report['promoted'] == ['F001', 'F002']
    md = (Path(libdir) / 'F001_test.md').read_text(encoding='utf-8')
    assert cl.RENDERED_BEGIN in md and cl.RENDERED_END in md
    assert 'https://doi.org/10.1000/wl2' in md   # CITES_STD = _cite(1..3) → wl2..wl4
    # 第二次跑同一库 (家族已 final): materialize 幂等 no-op, 闸照过
    rpath2 = str(tmp_path / 'report2.json')
    rc2 = blg.main(['--families', 'F001', '--longdesc-dir', libdir,
                    '--panel', str(tmp_path / 'panel51.parquet'),
                    '--report', rpath2])
    report2 = json.loads(Path(rpath2).read_text(encoding='utf-8'))
    assert rc2 == 0
    assert report2['families']['F001']['gates']['g4_render']['materialized_this_run'] is False


# ============================================================================
# ② 字数不足 → exit 1 且零迁移
# ============================================================================

def test_wordcount_fail_exit1_zero_migration(tmp_path, monkeypatch):
    fams = [
        {'fid': 'F001', 'columns': ['tone_a'], 'vars': {'tone_a': '差' * 100}},  # <350
        {'fid': 'F002', 'columns': ['tone_b']},
    ]
    rc, report, libdir = _run(tmp_path, monkeypatch, fams, run_fids='F001')
    assert rc == 1
    fe = report['families']['F001']
    assert fe['pass'] is False
    g2 = fe['gates']['g2_wordcount']
    assert g2['pass'] is False
    assert any('350' in v for v in g2['violations'])   # 差额数字列明
    assert report['promoted'] == []
    idx = json.loads((Path(libdir) / '_index.json').read_text(encoding='utf-8'))
    assert idx['families']['F001']['status'] == 'draft'   # 零迁移
    assert idx['families']['F002']['status'] == 'draft'


def test_core_tier_judged_at_5000_floor(tmp_path, monkeypatch):
    """core 列按 5000 汉字总量闸 + 4200/900 段落闸判 (standard 体量必 FAIL)。"""
    fams = [
        {'fid': 'F001', 'columns': ['tone_a'], 'tiers': {'tone_a': 'core'},
         'cites': [_cite(i) for i in range(1, 11)]},   # 10 条满足 core 引文下限
        {'fid': 'F002', 'columns': ['tone_b']},
    ]
    rc, report, _ = _run(tmp_path, monkeypatch, fams, run_fids='F001')
    assert rc == 1
    g2 = report['families']['F001']['gates']['g2_wordcount']
    assert g2['pass'] is False
    assert any('4200' in v or '5000' in v for v in g2['violations'])


# ============================================================================
# ③ 越权 DOI → FAIL (final 级判定, draft + new_dois 自声明不豁免)
# ============================================================================

def test_rogue_doi_fails_final_level_even_for_draft(tmp_path, monkeypatch):
    rogue = '10.9999/rogue-not-in-whitelist'
    fams = [
        {'fid': 'F001', 'columns': ['tone_a'],
         'cites': CITES_STD + [_cite(5, doi=rogue)],
         'new_dois': (rogue,), 'status': 'draft'},     # draft 出口条件全满足
        {'fid': 'F002', 'columns': ['tone_b']},
    ]
    rc, report, libdir = _run(tmp_path, monkeypatch, fams, run_fids='F001')
    assert rc == 1
    g3 = report['families']['F001']['gates']['g3_whitelist']
    assert g3['pass'] is False
    assert rogue in g3['over_dois']                    # 批收尾闸不走 draft 出口
    assert report['promoted'] == []
    idx = json.loads((Path(libdir) / '_index.json').read_text(encoding='utf-8'))
    assert idx['families']['F001']['status'] == 'draft'


def test_ledger_admitted_doi_passes(tmp_path, monkeypatch):
    """已过批收尾① 准入 (_new_dois_ledger.json) 的 DOI 不再算越权。"""
    admitted = '10.8888/newly-admitted'
    fams = [
        {'fid': 'F001', 'columns': ['tone_a'],
         'cites': CITES_STD + [_cite(6, doi=admitted)], 'new_dois': (admitted,)},
        {'fid': 'F002', 'columns': ['tone_b']},
    ]
    libdir = make_lib(tmp_path, fams)
    # 2026-07-11 收编整改 B 后批次闸走 load_ledger_verified 严格视图: fixture 须为
    # admit_new_dois.py 完整核验条目 (裸条目=未准入的负例归 test_citation_gate_hardening)
    from news_process.scripts.audit import check_longdesc_whitelist as chk
    entry = {'doi': admitted, 'admitted_date': '2026-07-10',
             'admitted_by': chk.LEDGER_ADMITTED_BY,
             'crossref_title': _LONG_TITLE + '6',
             'retraction_check': 'pass', 'verify_agent': 'pending'}
    entry['entry_sha'] = chk.ledger_entry_sha(entry)
    (Path(libdir) / '_new_dois_ledger.json').write_text(
        json.dumps({'entries': [entry]}), encoding='utf-8')
    ppath = _write_panel(tmp_path, ['tone_a', 'tone_b'])
    rpath = str(tmp_path / 'report.json')
    monkeypatch.setattr(blg, '_load_whitelist', lambda: set(WL_SET))
    rc = blg.main(['--families', 'F001', '--longdesc-dir', libdir,
                   '--panel', ppath, '--report', rpath])
    report = json.loads(Path(rpath).read_text(encoding='utf-8'))
    assert rc == 0
    assert report['families']['F001']['gates']['g3_whitelist']['pass'] is True


# ============================================================================
# ④ 守恒破坏 → 拒跑 (逐家族闸不跑, 零迁移)
# ============================================================================

def test_conservation_broken_refuses_to_run(tmp_path, monkeypatch):
    # panel 缺 tone_b → set(_index 非 pending 列) != set(panel.columns)
    rc, report, libdir = _run(tmp_path, monkeypatch, TWO_FAMS, run_fids='F001',
                              panel_cols=['tone_a'])
    assert rc == 1
    assert report['refused'] is not None
    assert 'gate1' in report['refused']
    g1 = report['global']['gate1_conservation']
    assert g1['pass'] is False
    assert 'tone_b' in g1['index_only']
    assert report['families'] == {}                    # 逐家族闸未跑
    assert report['promoted'] == []
    idx = json.loads((Path(libdir) / '_index.json').read_text(encoding='utf-8'))
    assert idx['families']['F001']['status'] == 'draft'


def test_duplicate_column_across_families_breaks_sigma(tmp_path, monkeypatch):
    """Σ|各家族列清单| != |并集| (同列被两家族收录) → 拒跑。"""
    fams = [
        {'fid': 'F001', 'columns': ['tone_a']},
        {'fid': 'F002', 'columns': ['tone_a', 'tone_b']},   # tone_a 重复收录
    ]
    libdir = make_lib(tmp_path, fams)
    ppath = _write_panel(tmp_path, ['tone_a', 'tone_b'])
    rpath = str(tmp_path / 'report.json')
    monkeypatch.setattr(blg, '_load_whitelist', lambda: set(WL_SET))
    rc = blg.main(['--families', 'F001', '--longdesc-dir', libdir,
                   '--panel', ppath, '--report', rpath])
    report = json.loads(Path(rpath).read_text(encoding='utf-8'))
    assert rc == 1
    g1 = report['global']['gate1_conservation']
    assert g1['pass'] is False
    assert 'tone_a' in g1['duplicated_cols']


def test_missing_panel_refuses(tmp_path, monkeypatch):
    """51 面板缺失 = 拒跑 (禁回退 40 宇宙), 报告照落盘。"""
    libdir = make_lib(tmp_path, TWO_FAMS)
    rpath = str(tmp_path / 'report.json')
    monkeypatch.setattr(blg, '_load_whitelist', lambda: set(WL_SET))
    rc = blg.main(['--families', 'F001', '--longdesc-dir', libdir,
                   '--panel', str(tmp_path / 'nonexistent.parquet'),
                   '--report', rpath, '--promote-final'])
    report = json.loads(Path(rpath).read_text(encoding='utf-8'))
    assert rc == 1
    assert 'missing' in report['refused']
    idx = json.loads((Path(libdir) / '_index.json').read_text(encoding='utf-8'))
    assert idx['families']['F001']['status'] == 'draft'


def test_unknown_family_refuses(tmp_path, monkeypatch):
    rc, report, _ = _run(tmp_path, monkeypatch, TWO_FAMS, run_fids='F999')
    assert rc == 1
    assert 'unknown family' in report['refused']
    assert report['families'] == {}


# ============================================================================
# ⑤ 报告 JSON schema
# ============================================================================

def test_report_json_schema(tmp_path, monkeypatch):
    rc, report, _ = _run(tmp_path, monkeypatch, TWO_FAMS, run_fids='F001,F002')
    assert rc == 0
    for key in ('tool', 'plan', 'timestamp', 'longdesc_dir', 'families_requested',
                'global', 'families', 'all_pass', 'refused', 'promoted', 'panel_path'):
        assert key in report, key
    assert report['tool'] == 'batch_longdesc_gate'
    assert set(report['families']) == {'F001', 'F002'}
    g = report['global']
    assert 'gate1_conservation' in g and 'gate3_frontmatter_recon' in g
    assert g['gate1_conservation']['n_panel_cols'] == 2
    for fe in report['families'].values():
        assert set(blg.GATE_KEYS) <= set(fe['gates'])
        for k in blg.GATE_KEYS:
            assert isinstance(fe['gates'][k]['pass'], bool)
        # 逐闸数字: 字数/引文条数机器可读
        assert fe['gates']['g2_wordcount']['per_col_cjk']
        assert isinstance(fe['gates']['g3_whitelist']['n_citations'], int)
        assert isinstance(fe['gates']['g4_render']['rendered_chars'], int)
        assert isinstance(fe['pass'], bool)
        assert isinstance(fe['n_columns'], int)
