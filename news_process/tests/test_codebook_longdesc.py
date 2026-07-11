"""家族长文库组装引擎 + 引文闸 gate 测试 (WP1, 计划 §5 WP1 行)。

权威口径 = scripts/audit/STATA_VARATTR_AND_CODEBOOK_LONGDESC_EXECUTION_PLAN_2026-07-10.md。
全部用 tmp_path fixture 家族库 — **不依赖真实 config/codebook_longdesc/_index.json**
(WP0 并行会话产出, 可能尚不存在; 引擎须容忍缺失)。

覆盖 (WP1 gate 列):
  组装确定性/幂等 · 双字数闸 (draft/final 分级) · 四态渲染 · 宽占位符零命中 ·
  白名单差集 (含 v2.9 draft 出口) · 两列表分离三断言 · 渲染物化一致性双断言 ·
  gitignore 双断言 · index draft 字段防双头 · 列集合三处全等 · 方法学声明存在 ·
  缺库回退告警 · 导出路径不 import 组装器 · no_doi_ack 闸 · CJK 计数单元测试 ·
  顶刊结构闸 · xlsx 组装层守卫 · csv QUOTE_ALL。

2026-07-11 整改追加 (六维评审 P1-1/P2 群/NIT):
  段首标题契约 (组装器不前置构念/变体标题, 双重标题 gate) · pending 列∈panel 实测分支 ·
  notes_zh/【备注】备注回填通道 · 重复 heading fail-loud · 占位符四类拼错收紧
  (含未闭合/全角) · json 权威载体 NaN→null 严格解析 · tier 幽灵键闸 · BOM 容忍 ·
  family_id 双头闸 · CRLF 人工区保持 · draft citation 分级 · AST 版 import gate。
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd
import pytest
import yaml

from news_process.pipeline.panel import codebook as cb
from news_process.pipeline.panel import codebook_longdesc as cl
from news_process.scripts.audit import audit_dois
from news_process.scripts.audit import check_longdesc_whitelist as chk

# ============================================================================
# fixture 家族库构造
# ============================================================================

# 白名单 DOI 池 (fixture 注入, 不触真实 874 白名单)
WL_DOIS = [f'10.1000/wl{i}' for i in range(1, 15)]

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


CITES_STD = [_cite(i) for i in range(1, 4)]        # 3 条 (standard 下限)
CITES_CORE = [_cite(i) for i in range(1, 11)]      # 10 条 (core 下限)

# P1-1 契约 (2026-07-11): 段首小标题归写手正文 — fixture 与骨架/模板同口径自带标题,
# 组装器不再前置【构念与来源】/【变体差分】(只加机械段标题)
CORE_STD = '【构念与来源】\n' + '构' * 750          # standard 家族核心长文段地板 700
VAR_STD = '【变体差分】\n' + '差' * 400             # standard 变体差分段地板 350
CORE_DEEP = '【构念与来源】\n' + '构' * 4300        # core 家族深核心地板 4200
VAR_DEEP = '【变体差分】\n' + '差' * 950            # core 列差分段地板 900


def _fam_md_text(fid, columns, core_text, var_texts, citations, *, unit='比率',
                 formula='x = a / b', producer='pipeline/sentiment/tone_words.py::fn',
                 new_dois=(), rendered=None):
    fm = {
        'family_id': fid, 'columns': list(columns), 'unit': unit, 'formula': formula,
        'producer': producer, 'upstream': ['21_tone_llms.parquet'],
        'citations': citations, 'new_dois': list(new_dois),
    }
    txt = '---\n' + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + '---\n\n'
    txt += '## CORE\n\n' + core_text + '\n\n'
    for c in columns:
        if c in var_texts:
            txt += f'## VAR: {c}\n\n{var_texts[c]}\n\n'
    for extra_c, extra_t in var_texts.items():
        if extra_c not in columns:
            txt += f'## VAR: {extra_c}\n\n{extra_t}\n\n'
    if rendered is not None:
        txt += f'{cl.RENDERED_BEGIN}\n{rendered}\n{cl.RENDERED_END}\n'
    return txt


def make_lib(tmp_path: Path, families, structural=('target_bank', 'year')) -> str:
    """families: list of dict(fid, columns, core, vars, cites, status, tiers, **md_kw)。"""
    libdir = tmp_path / 'longdesc'
    libdir.mkdir(parents=True, exist_ok=True)
    index = {
        'tier_signoff': {'date': '2026-07-10', 'method': 'test', 'user_ack': True,
                         'signed_manifest_sha': 'testsha'},
        'structural_whitelist': list(structural),
        'families': {},
    }
    for f in families:
        fid = f['fid']
        fname = f.get('fname', f'{fid}_test.md')
        index['families'][fid] = {
            'file': fname,
            'columns': f.get('index_columns', list(f['columns'])),
            'tier_by_col': f.get('tiers', {c: 'standard' for c in f['columns']}),
            'core_rationale_by_col': f.get('rationale', {}),
            'status': f.get('status', 'draft'),
            'batch': 1,
            'unit_draft': f.get('unit_draft', ''),
            'formula_draft': '', 'producer_draft': '',
        }
        if not f.get('skip_md'):
            (libdir / fname).write_text(
                _fam_md_text(fid, f['columns'], f.get('core', CORE_STD),
                             f.get('vars', {c: VAR_STD for c in f['columns']}),
                             f.get('cites', CITES_STD),
                             unit=f.get('unit', '比率'),
                             new_dois=f.get('new_dois', ()),
                             rendered=f.get('rendered')),
                encoding='utf-8')
    (libdir / '_index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding='utf-8')
    return str(libdir)


@pytest.fixture
def panel():
    return pd.DataFrame({
        'target_bank': ['A行', 'B行'],
        'year': [2017, 2018],
        'alpha_tone_full': [0.1, 0.2],
        'alpha_tone_ctx': [float('nan'), float('nan')],   # 四态②: 全 NaN
        'beta_core_full': [1.0, 2.0],
    })


def _std_families():
    return [
        {'fid': 'F001', 'columns': ['alpha_tone_full', 'alpha_tone_ctx']},
        {'fid': 'F002', 'columns': ['beta_core_full'], 'core': CORE_DEEP,
         'vars': {'beta_core_full': VAR_DEEP}, 'cites': CITES_CORE,
         'tiers': {'beta_core_full': 'core'},
         'rationale': {'beta_core_full': 'paper_spec treatment 主列'}},
        {'fid': 'F003', 'columns': ['roa'], 'tiers': {'roa': 'pending'}},
    ]


@pytest.fixture
def libdir(tmp_path, panel):
    return make_lib(tmp_path, _std_families())


WL_SET = {cl.normalize_doi(d) for d in WL_DOIS}
TOPCFG = {'top': ['Journal of Finance'], 'field': ['Journal of Banking and Finance']}


# ============================================================================
# 1. CJK 计数单元测试 (v2.7 汉字口径)
# ============================================================================

class TestCjkCount:
    def test_english_digits_punct_not_counted(self):
        assert cl.count_cjk('abc XYZ 12345 ,.;:!? []{}()') == 0
        assert cl.count_cjk('https://doi.org/10.1093/rof/rfab036') == 0
        # 全角标点/空白不计 (U+3002 句号 / U+FF0C 逗号 / 全角空格均在区外)
        assert cl.count_cjk('。，　') == 0

    def test_hanzi_counted(self):
        assert cl.count_cjk('汉字') == 2
        assert cl.count_cjk('汉a字1。') == 2
        # 基本区端点 + 扩展 A 端点 — 真 \u 转义构造 (2026-07-11 修复: 原为字面端点
        # 字符而注释谎称转义, GBK 控制台断言失败回显即二次 UnicodeEncodeError)
        assert cl.count_cjk('\u4e00\u9fff\u3400\u4dbf') == 4
        assert cl.count_cjk('') == 0
        assert cl.count_cjk(None) == 0


# ============================================================================
# 2. 组装确定性 / 幂等
# ============================================================================

class TestComposeDeterminism:
    def test_same_input_twice_byte_equal(self, panel, libdir):
        lib1 = cl.load_library(libdir)
        lib2 = cl.load_library(libdir)
        a = cl.compose_long_description('alpha_tone_full', panel, lib1)
        b = cl.compose_long_description('alpha_tone_full', panel, lib2)
        assert a['description'] == b['description']
        assert a['description'].encode('utf-8') == b['description'].encode('utf-8')

    def test_five_segments_present(self, panel, libdir):
        lib = cl.load_library(libdir)
        d = cl.compose_long_description('alpha_tone_full', panel, lib)['description']
        for t in ('【构念与来源】', '【变体差分】', '【计算链路】', '【动态统计】', '【学术文献】'):
            assert t in d

    def test_materialize_idempotent(self, libdir):
        lib = cl.load_library(libdir)
        n1 = cl.materialize_all(lib)
        assert n1 == 3                    # 首次: 3 家族尾节写入
        lib2 = cl.load_library(libdir)
        assert cl.materialize_all(lib2) == 0   # 幂等: 已最新 no-op


# ============================================================================
# 3. 字数双闸 (draft 告警计数 / final SystemExit 分级)
# ============================================================================

class TestWordGates:
    def test_draft_insufficient_warns_not_crash(self, tmp_path, panel):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'vars': {'alpha_tone_full': '差' * 100},  # < 350
                                 'status': 'draft'}])
        lib = cl.load_library(d)
        counters = {'warnings': [], 'composed': 0}
        out = cl.compose_long_description('alpha_tone_full', panel, lib, counters=counters)
        assert out is not None            # draft 组装照常返回, 渐进批次不断链
        assert any('变体差分段' in w for w in counters['warnings'])

    def test_final_insufficient_systemexit(self, tmp_path, panel):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'vars': {'alpha_tone_full': '差' * 100},
                                 'status': 'final'}])
        lib = cl.load_library(d)
        with pytest.raises(SystemExit):
            cl.compose_long_description('alpha_tone_full', panel, lib)

    def test_core_col_requires_5000_total(self, tmp_path, panel):
        # core 列但只给 standard 深度 → 段落闸 (4200/900) + 总量闸 (5000) 皆红
        d = make_lib(tmp_path, [{'fid': 'F002', 'columns': ['beta_core_full'],
                                 'core': CORE_STD, 'vars': {'beta_core_full': VAR_STD},
                                 'tiers': {'beta_core_full': 'core'}, 'status': 'final',
                                 'cites': CITES_CORE}])
        lib = cl.load_library(d)
        with pytest.raises(SystemExit):
            cl.compose_long_description('beta_core_full', panel, lib)

    def test_core_passes_at_core_depth(self, panel, libdir):
        lib = cl.load_library(libdir)
        out = cl.compose_long_description('beta_core_full', panel, lib)
        assert out['tier'] == 'core'
        assert out['cjk_total'] >= 5000
        assert out['gate_violations'] == []

    def test_structural_whitelist_exempt(self, tmp_path, panel):
        # 结构列入家族但文本远低于地板 → 白名单豁免不触闸 (final 也不崩)
        d = make_lib(tmp_path, [{'fid': 'F009', 'columns': ['year'],
                                 'core': '构' * 10, 'vars': {'year': '差' * 5},
                                 'status': 'final'}])
        lib = cl.load_library(d)
        out = cl.compose_long_description('year', panel, lib)
        assert out is not None and out['gate_violations'] == []

    def test_citation_quality_floor(self, tmp_path, panel):
        # standard 引文 <3 条 → final 崩
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'cites': [_cite(1)], 'status': 'final'}])
        lib = cl.load_library(d)
        with pytest.raises(SystemExit):
            cl.compose_long_description('alpha_tone_full', panel, lib)


# ============================================================================
# 4. 动态统计段四态 + 宽占位符残留
# ============================================================================

class TestFourStates:
    def test_state3_normal_with_footnote(self, panel, libdir):
        lib = cl.load_library(libdir)
        d = cl.compose_long_description('alpha_tone_full', panel, lib)['description']
        assert 'mean=' in d and '缺失率=' in d
        assert '生产 T=18 重生后以实读为准' in d

    def test_state2_all_nan(self, panel, libdir):
        lib = cl.load_library(libdir)
        d = cl.compose_long_description('alpha_tone_ctx', panel, lib)['description']
        assert '全缺失 (非缺失 n=0' in d

    def test_state4_pending_sentinel(self, panel, libdir):
        lib = cl.load_library(libdir)
        out = cl.compose_long_description('roa', panel, lib)   # roa 不在 panel
        assert '待外部财务面板接入' in out['description']
        assert out['value_range'] == '待接入'
        # pending 豁免 ≥5000 (standard 地板照适用): 本 fixture standard 深度即过
        assert out['gate_violations'] == []

    def test_state1_placeholder_ghost_col_systemexit(self, tmp_path, panel):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'core': CORE_STD + ' {stats:ghost_col} '}])
        lib = cl.load_library(d)
        with pytest.raises(SystemExit):
            cl.compose_long_description('alpha_tone_full', panel, lib)

    def test_placeholder_substitution_works(self, tmp_path, panel):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'core': CORE_STD + ' {stats:beta_core_full} '}])
        lib = cl.load_library(d)
        desc = cl.compose_long_description('alpha_tone_full', panel, lib)['description']
        assert '{stats:' not in desc
        assert desc.count('mean=') >= 2   # 占位符注入 + 本列自身动态统计段

    # P2-④ (2026-07-11) 收紧后覆盖: 大小写拼错 / 冒号前空格 / 名带数字(两向) /
    # 未闭合 / 全角花括号 — 六类拼错全部 fail-loud, 零静默穿过
    @pytest.mark.parametrize('typo', [
        ' {STAT:beta_core_full} ',            # 大小写拼错 (原有覆盖)
        ' {stats :beta_core_full} ',          # 冒号前空格
        ' {stats2:beta_core_full} ',          # 名尾带数字
        ' {2stats:beta_core_full} ',          # 名首带数字
        ' {stats:beta_core_full 未闭合到行尾',   # 未闭合
        ' \uFF5Bstats:beta_core_full\uFF5D ',   # 全角花括号 (\u 转义构造)
    ])
    def test_wide_placeholder_typo_failloud(self, tmp_path, panel, typo):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'core': CORE_STD + typo}])
        lib = cl.load_library(d)
        with pytest.raises(SystemExit, match='占位符|placeholder|残留'):
            cl.compose_long_description('alpha_tone_full', panel, lib)

    def test_composed_zero_wide_residue(self, panel, libdir):
        lib = cl.load_library(libdir)
        for col in ('alpha_tone_full', 'alpha_tone_ctx', 'beta_core_full'):
            desc = cl.compose_long_description(col, panel, lib)['description']
            assert cl.find_placeholder_residue(desc) == []


# ============================================================================
# 5. 引文渲染 + no_doi_ack 闸 + 渲染物化一致性双断言
# ============================================================================

class TestCitations:
    def test_apa_render_ends_with_doi_link(self):
        line = cl.render_citation_apa(_cite(1))
        assert line.endswith('https://doi.org/' + WL_DOIS[1])
        assert 'Journal of Finance, 79(2)' in line

    def test_wp_and_arxiv_templates(self):
        wp = cl.render_citation_apa(_cite(2, ctype='wp', venue='NBER Working Paper',
                                          pages_or_artno='31210'))
        assert '[Working Paper]' in wp and 'No. 31210' in wp
        ax = cl.render_citation_apa(_cite(3, ctype='arxiv', venue='arXiv'))
        assert '[Preprint]' in ax

    def test_no_doi_ack_gate(self):
        bad = _cite(1, ctype='book'); bad['doi'] = ''
        assert any('no_doi_ack' in e for e in cl.validate_citation(bad, 'F00X'))
        ok = _cite(1, ctype='book')
        ok['doi'] = ''; ok['no_doi_ack'] = 'ACK-001'
        ok['alt_link'] = 'https://worldcat.org/isbn/9780000000000'
        assert cl.validate_citation(ok, 'F00X') == []
        rendered = cl.render_citation_apa(ok)
        assert '[no-DOI ack #ACK-001]' in rendered and 'worldcat' in rendered

    def test_materialize_then_extract_refs_consistent(self, libdir):
        lib = cl.load_library(libdir)
        cl.materialize_all(lib)
        fam = lib.families['F002']
        # 断言② 前提: 渲染段 DOI 集 == citations DOI 集
        rendered = {audit_dois.clean_doi(m.group(1)).lower()
                    for m in audit_dois.DOIORG_RE.finditer(fam.rendered_block)}
        assert rendered == cl.rendered_dois(fam.frontmatter['citations'])
        # 断言① 前提: extract_refs (doi.org 链接口径) 能从家族 md 提取
        refs = audit_dois.extract_refs(fam.path)
        assert set(refs) == rendered

    def test_run_checks_double_assertions(self, libdir):
        rep = chk.run_checks(libdir, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert rep['fatal'] == []
        assert rep['n_extracted_dois'] >= rep['n_frontmatter_dois'] > 0

    def test_stale_rendered_tail_fatal(self, tmp_path, panel):
        # 物化后改 frontmatter 引文 (不重物化) → 断言② 陈旧集 fatal
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'cites': CITES_STD,
                                 'rendered': cl.render_citations_block([_cite(9)])}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG)
        assert any('渲染段 DOI 集 != citations DOI 集' in e for e in rep['fatal'])

    def test_doiorg_outside_tail_lint(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'core': CORE_STD + ' 见 https://doi.org/10.1/bad 处'}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert any('doi.org' in e for e in rep['fatal'])

    def test_weak_prose_citation_warn_only(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'core': CORE_STD + ' 参见 Smith (2019) 的研究'}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert any('Smith (2019)' in w for w in rep['warnings'])
        assert not any('Smith' in e for e in rep['fatal'])


# ============================================================================
# 6. 白名单差集闸 (§2.3, 含 v2.9 draft 出口)
# ============================================================================

class TestWhitelistDiff:
    def test_final_over_doi_fatal(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'cites': CITES_STD + [_cite(0, doi='10.9999/rogue1')],
                                 'status': 'final'}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert any('10.9999/rogue1' in e for e in rep['fatal'])

    def test_draft_exit_with_new_dois_declared(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'cites': CITES_STD + [_cite(0, doi='10.9999/new1')],
                                 'new_dois': ['10.9999/new1'], 'status': 'draft'}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert rep['fatal'] == []
        assert any('draft 越权' in w for w in rep['warnings'])

    def test_draft_over_doi_without_declaration_fatal(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'cites': CITES_STD + [_cite(0, doi='10.9999/sneak1')],
                                 'status': 'draft'}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert any('10.9999/sneak1' in e for e in rep['fatal'])

    def test_ledger_admits_doi(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'cites': CITES_STD + [_cite(0, doi='10.9999/adm1')],
                                 'status': 'final'}])
        # 2026-07-11 红队整改后台账口径: run_checks 只认 admit_new_dois.py 完整核验
        # 条目 (admitted_by + crossref_title 回比 + retraction_check + entry_sha) —
        # fixture 升级为合规条目 (裸条目视为未准入的负例见 test_citation_gate_hardening)
        entry = {'doi': '10.9999/adm1', 'admitted_date': '2026-07-10',
                 'admitted_by': chk.LEDGER_ADMITTED_BY,
                 'crossref_title': _LONG_TITLE + '0',
                 'retraction_check': 'pass', 'verify_agent': 'pending'}
        entry['entry_sha'] = chk.ledger_entry_sha(entry)
        (Path(d) / '_new_dois_ledger.json').write_text(
            json.dumps({'entries': [entry]}), encoding='utf-8')
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert rep['fatal'] == []

    def test_new_dois_must_land_in_citations(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'new_dois': ['10.9999/orphan1']}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert any('new_dois 未同时以 citations 条目落地' in e for e in rep['fatal'])

    def test_reconciliation_parsed_vs_index(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['a_full']},
                                {'fid': 'F002', 'columns': ['b_full'], 'skip_md': True}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG)
        assert any('家族数' in e for e in rep['fatal'])

    def test_frontmatter_parse_failure_systemexit(self, tmp_path):
        libdir = tmp_path / 'longdesc'
        libdir.mkdir()
        (libdir / '_index.json').write_text(json.dumps(
            {'families': {'F001': {'file': 'F001_x.md', 'columns': ['a'],
                                   'tier_by_col': {}, 'status': 'draft'}}}),
            encoding='utf-8')
        (libdir / 'F001_x.md').write_text('---\n: broken: [yaml\n---\nbody',
                                          encoding='utf-8')
        with pytest.raises(SystemExit):
            chk.run_checks(str(libdir), whitelist=WL_SET, top_journal_cfg=TOPCFG)

    def test_empty_library_exit0(self, tmp_path):
        rep = chk.run_checks(str(tmp_path / 'nolib'), whitelist=WL_SET,
                             top_journal_cfg=TOPCFG)
        assert rep.get('empty') is True


# ============================================================================
# 7. 顶刊结构闸 (§2.7)
# ============================================================================

class TestTopJournalGate:
    # v2.11 双层语义 (2026-07-11 C1 实证校准): 零 top 锚 = 家族级硬闸 (final FATAL /
    # draft WARN); (top+field 内) 非 top 占比 >30% 一律降级 WARN (记录数字)。

    def test_non_top_over_30pct_returns_message(self):
        cites = [_cite(1), _cite(2), _cite(3, venue='Obscure Journal of Things'),
                 _cite(4, venue='Journal of Banking and Finance')]
        v = chk.family_top_journal_gate(cites, TOPCFG)
        assert v is not None and '> 30%' in v

    def test_zero_top_anchor_final_fatal(self, tmp_path):
        # 层① 硬闸: final 家族全非 top → FATAL
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'cites': [_cite(i, venue='Obscure Journal of Things')
                                           for i in range(1, 4)],
                                 'status': 'final'}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert any('零 top 锚' in e for e in rep['fatal'])

    def test_zero_top_anchor_draft_warn_only(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'cites': [_cite(i, venue='Obscure Journal of Things')
                                           for i in range(1, 4)],
                                 'status': 'draft'}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert not any('零 top 锚' in e for e in rep['fatal'])
        assert any('零 top 锚' in w for w in rep['warnings'])

    def test_over_30pct_with_top_anchor_final_warn_not_fatal(self, tmp_path):
        # 层② 降级: final 家族占比 40% 但有 top 锚 → WARN 记录数字, 不 FATAL
        cites = CITES_STD + [_cite(4, venue='Obscure Journal of Things'),
                             _cite(5, venue='Another Obscure Review')]
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'cites': cites, 'status': 'final'}])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        assert rep['fatal'] == []
        assert any('> 30%' in w for w in rep['warnings'])

    def test_top_journal_mix_report_final_only(self, tmp_path):
        d = make_lib(tmp_path, [
            {'fid': 'F001', 'columns': ['alpha_tone_full'],
             'cites': CITES_STD + [_cite(4, venue='Journal of Banking and Finance'),
                                   _cite(5, venue='Obscure Journal of Things')],
             'status': 'final'},
            {'fid': 'F002', 'columns': ['beta_core_full'],
             'cites': CITES_STD, 'status': 'draft'},  # draft 不入聚合
        ])
        rep = chk.run_checks(d, whitelist=WL_SET, top_journal_cfg=TOPCFG,
                             materialize=True)
        mix = rep['top_journal_mix_final']['counts']
        assert mix['top'] == 3 and mix['field'] == 1 and mix['unlisted'] == 1

    def test_wp_preprint_excluded_from_denominator(self):
        cites = [_cite(1), _cite(2),
                 _cite(3, ctype='wp', venue='NBER Working Paper'),
                 _cite(4, ctype='arxiv', venue='arXiv')]
        assert chk.family_top_journal_gate(cites, TOPCFG) is None

    def test_unknown_journal_counts_non_top(self):
        assert chk.classify_citation(_cite(1, venue='Totally Unknown Rev'), TOPCFG) == 'field'
        assert chk.classify_citation(_cite(1), TOPCFG) == 'top'

    def test_real_yaml_loads_and_normalizes(self):
        cfg = chk.load_top_journal_cfg()
        assert cfg is not None and 'top' in cfg and 'field' in cfg
        # '&' → 'and' 归一: JBF 两拼法同判
        assert chk.classify_citation(
            _cite(1, venue='Journal of Banking & Finance'), cfg) == 'field'
        assert chk.classify_citation(_cite(1), cfg) == 'top'


# ============================================================================
# 8. 两列表分离三断言 (audit_dois, §2.5)
# ============================================================================

class TestTwoListSeparation:
    def test_anchor_frozen_13_paths_and_alias(self):
        assert len(audit_dois.FILES_WHITELIST_ANCHOR) == 13
        assert audit_dois.FILES is audit_dois.FILES_WHITELIST_ANCHOR
        # 锚内零 codebook_longdesc 路径 (白名单唯一派生源冻结)
        assert not any('codebook_longdesc' in p for p in audit_dois.FILES_WHITELIST_ANCHOR)

    def test_audit_all_includes_glob_and_disjoint(self, tmp_path, monkeypatch, libdir):
        monkeypatch.setattr(audit_dois, 'LONGDESC_DIR', libdir)
        allf = audit_dois.audit_all_files()
        globbed = [p for p in allf if 'longdesc' in p]
        assert len(globbed) == 3     # fixture 3 家族 md; _index.json/_ledger 不入
        anchor = set(map(str.lower, audit_dois.FILES_WHITELIST_ANCHOR))
        assert anchor.isdisjoint(set(map(str.lower, globbed)))

    def test_assert1_glob_zero_with_families_systemexit(self, tmp_path, monkeypatch):
        libdir = tmp_path / 'longdesc'
        libdir.mkdir()
        (libdir / '_index.json').write_text(json.dumps(
            {'families': {'F001': {'file': 'F001_x.md', 'columns': []}}}),
            encoding='utf-8')
        monkeypatch.setattr(audit_dois, 'LONGDESC_DIR', str(libdir))
        with pytest.raises(SystemExit):
            audit_dois.audit_all_files()

    def test_assert2_count_mismatch_systemexit(self, tmp_path, monkeypatch, libdir):
        # index 3 家族, 删 1 个 md → 对账崩
        victims = sorted(Path(libdir).glob('F00*_test.md'))
        victims[0].unlink()
        monkeypatch.setattr(audit_dois, 'LONGDESC_DIR', libdir)
        with pytest.raises(SystemExit):
            audit_dois.audit_all_files()

    def test_assert3_anchor_glob_intersection_systemexit(self, tmp_path, monkeypatch):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['a_full']}])
        fam_md = str(sorted(Path(d).glob('F001*.md'))[0])
        monkeypatch.setattr(audit_dois, 'LONGDESC_DIR', d)
        monkeypatch.setattr(audit_dois, 'FILES_WHITELIST_ANCHOR',
                            list(audit_dois.FILES_WHITELIST_ANCHOR) + [fam_md])
        with pytest.raises(SystemExit):
            audit_dois.audit_all_files()

    def test_whitelist_derivation_excludes_glob(self, tmp_path, monkeypatch):
        anchor = tmp_path / 'anchor.md'
        anchor.write_text('x https://doi.org/10.5555/anchor1 y\n', encoding='utf-8')
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['a_full'],
                                 'rendered': 'z https://doi.org/10.5555/fromlib1 w'}])
        monkeypatch.setattr(audit_dois, 'FILES_WHITELIST_ANCHOR', [str(anchor)])
        monkeypatch.setattr(audit_dois, 'LONGDESC_DIR', d)
        wl = audit_dois.whitelist_dois()
        assert wl == {'10.5555/anchor1'}
        assert '10.5555/fromlib1' not in wl   # 家族 md 渲染 DOI 永不自动并入白名单


# ============================================================================
# 9. 列集合三处全等 + index draft 字段防双头 + 缺库回退
# ============================================================================

class TestLibraryIntegrity:
    def test_index_vs_frontmatter_mismatch_systemexit(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['a_full'],
                                 'index_columns': ['a_full', 'b_full']}])
        with pytest.raises(SystemExit):
            cl.load_library(d)

    def test_phantom_var_heading_systemexit(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['a_full'],
                                 'vars': {'a_full': VAR_STD, 'zz_ghost': VAR_STD}}])
        with pytest.raises(SystemExit):
            cl.load_library(d)

    def test_missing_var_draft_warns_final_crashes(self, tmp_path):
        fams = [{'fid': 'F001', 'columns': ['a_full', 'b_full'],
                 'vars': {'a_full': VAR_STD}, 'status': 'draft'}]
        lib = cl.load_library(make_lib(tmp_path / 'd1', fams))
        assert any('缺 "## VAR:" 节' in w for w in lib.load_warnings)
        fams[0]['status'] = 'final'
        with pytest.raises(SystemExit):
            cl.load_library(make_lib(tmp_path / 'd2', fams))

    def test_duplicate_column_across_families_systemexit(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['dup_full']},
                                {'fid': 'F002', 'columns': ['dup_full']}])
        with pytest.raises(SystemExit):
            cl.load_library(d)

    def test_index_draft_fields_not_consumed(self, tmp_path, panel):
        # frontmatter unit='比率' 存在 → index unit_draft 不再被消费 (防双头 gate)
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'unit': '比率', 'unit_draft': '废弃草稿单位'}])
        lib = cl.load_library(d)
        out = cl.compose_long_description('alpha_tone_full', panel, lib)
        assert out['unit'] == '比率'
        assert '废弃' not in out['unit']

    def test_missing_library_returns_none(self, tmp_path):
        assert cl.load_library(str(tmp_path / 'ghost')) is None
        assert cl.load_library(None) is None

    def test_markdown_structure_lint_in_human_zone(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['a_full'],
                                 'core': CORE_STD + '\n**加粗违规**',
                                 'status': 'final'}])
        with pytest.raises(SystemExit):
            cl.load_library(d)


# ============================================================================
# 10. generate_codebook 挂载点集成 (md writer / 方法学声明 / 报告 / csv / 缺库回退)
# ============================================================================

class TestGenerateCodebookIntegration:
    def _run(self, panel, tmp_path, libdir, formats=('markdown', 'json', 'csv')):
        out_dir = tmp_path / 'out'
        ver_dir = tmp_path / 'ver'
        return cb.generate_codebook(panel, str(out_dir), formats=list(formats),
                                    versioned_dir=str(ver_dir), longdesc_dir=libdir)

    def test_long_descriptions_land_in_json(self, panel, tmp_path, libdir):
        out = self._run(panel, tmp_path, libdir)
        rows = json.loads(Path(out['json']).read_text(encoding='utf-8'))
        by_name = {r['变量名']: r for r in rows}
        assert len(rows) == len(panel.columns)
        d = by_name['alpha_tone_full']['描述']
        assert '【构念与来源】' in d and cl.count_cjk(d) >= 1000
        assert cl.count_cjk(by_name['beta_core_full']['描述']) >= 5000
        # 12 字段机械回填 (§4)
        assert by_name['alpha_tone_full']['单位'] == '比率'
        assert by_name['alpha_tone_full']['计算公式'] == 'x = a / b'
        assert '生成时实测' in by_name['alpha_tone_full']['取值范围']
        assert 'doi.org' in by_name['alpha_tone_full']['学术引用']

    def test_md_sectioned_with_methodology_and_pending_appendix(self, panel, tmp_path, libdir):
        out = self._run(panel, tmp_path, libdir)
        md = Path(out['markdown']).read_text(encoding='utf-8')
        assert '## 方法学声明' in md and '刻意设计' in md
        assert '## 变量总览' in md and '## 变量详情' in md
        assert '## beta_core_full' in md
        assert '## 附录: 待接入变量 (tier=pending)' in md and '### roa' in md
        # 宽占位符零命中 (最终产物 gate)
        assert cl._WIDE_PLACEHOLDER_RE.findall(md) == []

    def test_reports_written_and_fallback_zero(self, panel, tmp_path, libdir):
        out = self._run(panel, tmp_path, libdir)
        fcr = json.loads(Path(out['field_coverage_report']).read_text(encoding='utf-8'))
        assert fcr['n_variables'] == len(panel.columns)
        assert fcr['fields']['单位']['non_empty'] >= 3
        size = json.loads(Path(out['size_report']).read_text(encoding='utf-8'))
        assert size['longdesc_counters']['fallback'] == 0   # 全列有家族/结构豁免
        assert size['summary']['n_cols'] == len(panel.columns)
        assert size['per_col']['beta_core_full']['cjk'] >= 5000
        assert {'cjk', 'chars', 'utf8_bytes'} <= set(size['per_col']['beta_core_full'])

    def test_missing_library_fallback_with_warning(self, panel, tmp_path, caplog):
        import logging
        with caplog.at_level(logging.WARNING):
            out = self._run(panel, tmp_path, str(tmp_path / 'ghost_lib'),
                            formats=('json',))
        assert any('家族长文库缺失' in r.message for r in caplog.records)
        size = json.loads(Path(out['size_report']).read_text(encoding='utf-8'))
        assert size['longdesc_counters']['fallback'] == len(panel.columns)
        rows = json.loads(Path(out['json']).read_text(encoding='utf-8'))
        assert len(rows) == len(panel.columns)   # 回退现状短描述, 不崩

    def test_csv_quote_all(self, panel, tmp_path, libdir):
        out = self._run(panel, tmp_path, libdir, formats=('csv',))
        first = Path(out['csv']).read_text(encoding='utf-8-sig').splitlines()[0]
        assert first.startswith('"变量名"')
        assert first.count('"') >= 24    # 12 元数据字段全引号

    def test_versioned_dir_default_backcompat(self, panel, tmp_path, libdir):
        # versioned_dir=None → 回退 output_dir (既有调用/测试兼容)
        out = cb.generate_codebook(panel, str(tmp_path), formats=['json'],
                                   longdesc_dir=libdir)
        assert Path(out['json']).parent == tmp_path


# ============================================================================
# 10b. 2026-07-11 整改 gate: P1-1 双重标题契约 / P2-①②③⑤⑥ / NIT (BOM/双头/CRLF)
# ============================================================================


class TestSegTitleContract:
    """P1-1 契约: 构念/变体段首小标题归写手正文, 组装器只加机械段标题。"""

    def test_composer_does_not_duplicate_titles(self, panel, libdir):
        lib = cl.load_library(libdir)
        d = cl.compose_long_description('alpha_tone_full', panel, lib)['description']
        # 每个段首标题恰出现一次 (写手正文 1 次 + 组装器 0 次)
        for t in ('【构念与来源】', '【变体差分】', '【计算链路】', '【动态统计】', '【学术文献】'):
            assert d.count(t) == 1, f'{t} 出现 {d.count(t)} 次 (应恰 1)'
        assert cl._DOUBLE_SEG_TITLE_RE.search(d) is None
        assert d.startswith('【构念与来源】')

    def test_double_title_in_writer_text_failloud(self, tmp_path, panel):
        # 写手正文自带双重标题 (镜像旧缺陷形态) → 组装器 gate 无条件崩
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                                 'core': '【构念与来源】\n【构念与来源】\n' + '构' * 750}])
        lib = cl.load_library(d)
        with pytest.raises(SystemExit, match='双重段首标题'):
            cl.compose_long_description('alpha_tone_full', panel, lib)

    def test_missing_inline_title_warns_never_blocks(self, tmp_path, panel):
        # 写手正文缺段首标题: 纯告警 (draft/final 均不崩、不入 violations —
        # 契约只硬约束零双重标题; 入 violations 会连坐 batch gate promote 判定)
        for status, sub in (('draft', 'd1'), ('final', 'd2')):
            fams = [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                     'core': '构' * 750, 'vars': {'alpha_tone_full': '差' * 400},
                     'status': status}]
            lib = cl.load_library(make_lib(tmp_path / sub, fams))
            counters = {'warnings': [], 'composed': 0}
            out = cl.compose_long_description('alpha_tone_full', panel, lib,
                                              counters=counters)
            assert out is not None
            assert any('P1-1 契约' in w for w in counters['warnings'])
            assert not any('P1-1' in v for v in out['gate_violations'])

    def test_product_md_json_zero_double_titles(self, panel, tmp_path, libdir):
        out_dir, ver_dir = tmp_path / 'out', tmp_path / 'ver'
        out = cb.generate_codebook(panel, str(out_dir), formats=['markdown', 'json'],
                                   versioned_dir=str(ver_dir), longdesc_dir=libdir)
        md = Path(out['markdown']).read_text(encoding='utf-8')
        assert cl._DOUBLE_SEG_TITLE_RE.search(md) is None, '产物 md 出现双重段首标题'
        rows = json.loads(Path(out['json']).read_text(encoding='utf-8'))
        for r in rows:
            assert cl._DOUBLE_SEG_TITLE_RE.search(str(r.get('描述', '') or '')) is None


class TestPendingActualPresence:
    """P2-①: pending 分支按 col∈panel 实测判, 非 tier 静态判。"""

    def test_pending_col_present_renders_real_stats(self, tmp_path):
        panel2 = pd.DataFrame({'target_bank': ['A行'], 'year': [2017],
                               'roa': [0.012]})
        d = make_lib(tmp_path, [{'fid': 'F003', 'columns': ['roa'],
                                 'tiers': {'roa': 'pending'}}])
        lib = cl.load_library(d)
        counters = {'warnings': [], 'composed': 0}
        out = cl.compose_long_description('roa', panel2, lib, counters=counters)
        assert '当前面板不产生数值' not in out['description']   # 哨兵文本不再矛盾渲染
        assert 'mean=' in out['description']                     # 实测统计
        assert out['value_range'] != '待接入'
        assert any('tier=pending 但面板已实存' in w for w in counters['warnings'])

    def test_pending_col_absent_keeps_sentinel(self, panel, libdir):
        lib = cl.load_library(libdir)
        out = cl.compose_long_description('roa', panel, lib)
        assert '待外部财务面板接入' in out['description']
        assert out['value_range'] == '待接入'


class TestNotesBackfillChannel:
    """P2-②: notes_zh frontmatter (str/映射) + VAR 节内联【备注】通道。"""

    def _mklib_with_notes(self, tmp_path, *, fm_notes=None, inline=None):
        var_txt = VAR_STD + (f'\n【备注】{inline}' if inline else '')
        md = _fam_md_text('F001', ['alpha_tone_full'], CORE_STD,
                          {'alpha_tone_full': var_txt}, CITES_STD)
        if fm_notes is not None:
            # 在 frontmatter 尾部注入 notes_zh (yaml 兼容)
            md = md.replace('\n---\n', '\nnotes_zh: ' + json.dumps(
                fm_notes, ensure_ascii=False) + '\n---\n', 1)
        libdir = tmp_path / 'longdesc'
        libdir.mkdir()
        (libdir / 'F001_test.md').write_text(md, encoding='utf-8')
        (libdir / '_index.json').write_text(json.dumps({
            'tier_signoff': {}, 'structural_whitelist': [],
            'families': {'F001': {'file': 'F001_test.md',
                                  'columns': ['alpha_tone_full'],
                                  'tier_by_col': {'alpha_tone_full': 'standard'},
                                  'core_rationale_by_col': {}, 'status': 'draft',
                                  'batch': 1, 'unit_draft': '', 'formula_draft': '',
                                  'producer_draft': ''}}},
            ensure_ascii=False), encoding='utf-8')
        return str(libdir)

    def test_family_level_notes_str(self, panel, tmp_path):
        d = self._mklib_with_notes(tmp_path, fm_notes='家族级备注一句话')
        lib = cl.load_library(d)
        out = cl.compose_long_description('alpha_tone_full', panel, lib)
        assert out['notes_zh'] == '家族级备注一句话'

    def test_per_col_mapping_and_inline_priority(self, panel, tmp_path):
        d = self._mklib_with_notes(tmp_path,
                                   fm_notes={'alpha_tone_full': '映射级备注'},
                                   inline='内联备注优先')
        lib = cl.load_library(d)
        out = cl.compose_long_description('alpha_tone_full', panel, lib)
        assert out['notes_zh'] == '内联备注优先'      # VAR 内联 > frontmatter 映射

    def test_auto_infer_note_replaced_in_product(self, panel, tmp_path):
        d = self._mklib_with_notes(tmp_path, fm_notes='已人工核对的备注')
        out = cb.generate_codebook(panel, str(tmp_path / 'o'), formats=['json'],
                                   versioned_dir=str(tmp_path / 'v'), longdesc_dir=d)
        rows = json.loads(Path(out['json']).read_text(encoding='utf-8'))
        by_name = {r['变量名']: r for r in rows}
        note = by_name['alpha_tone_full']['备注']
        assert '已人工核对的备注' in note
        assert '自动推断的元数据' not in note   # _AUTO_INFER_NOTE 被替换 (归零通道打通)


class TestParseHardening:
    """P2-③ 重复 heading / P2-⑥ tier 幽灵键 / NIT BOM·family_id 双头。"""

    def test_duplicate_core_heading_failloud(self, tmp_path):
        md = _fam_md_text('F001', ['a_full'], CORE_STD, {'a_full': VAR_STD}, CITES_STD)
        md += '\n## CORE\n\nsecond core text\n'
        p = tmp_path / 'F001_test.md'
        p.write_text(md, encoding='utf-8')
        with pytest.raises(SystemExit, match='重复 "## CORE"'):
            cl.parse_family_md(str(p), family_id='F001')

    def test_duplicate_var_heading_failloud(self, tmp_path):
        md = _fam_md_text('F001', ['a_full'], CORE_STD, {'a_full': VAR_STD}, CITES_STD)
        md += '\n## VAR: a_full\n\ntext two\n'
        p = tmp_path / 'F001_test.md'
        p.write_text(md, encoding='utf-8')
        with pytest.raises(SystemExit, match='重复 "## VAR: a_full"'):
            cl.parse_family_md(str(p), family_id='F001')

    def test_tier_ghost_key_failloud(self, tmp_path):
        # tier_by_col 含 columns 外幽灵键 → load 期 SystemExit (原: pending 列无声消失)
        d = make_lib(tmp_path, [{'fid': 'F001', 'columns': ['a_full'],
                                 'tiers': {'a_full': 'standard',
                                           'ghost_pending': 'pending'}}])
        with pytest.raises(SystemExit, match='幽灵键'):
            cl.load_library(d)

    def test_bom_tolerated(self, tmp_path):
        md = _fam_md_text('F001', ['a_full'], CORE_STD, {'a_full': VAR_STD}, CITES_STD)
        p = tmp_path / 'F001_test.md'
        p.write_text(md, encoding='utf-8-sig')     # PowerShell 5.1 默认带 BOM
        fam = cl.parse_family_md(str(p), family_id='F001')
        assert fam.core_text.startswith('【构念与来源】')

    def test_family_id_two_heads_failloud(self, tmp_path):
        md = _fam_md_text('F999', ['a_full'], CORE_STD, {'a_full': VAR_STD}, CITES_STD)
        p = tmp_path / 'F001_test.md'
        p.write_text(md, encoding='utf-8')
        with pytest.raises(SystemExit, match='双头漂移'):
            cl.parse_family_md(str(p), family_id='F001')

    def test_crlf_human_zone_preserved_on_materialize(self, tmp_path):
        md = _fam_md_text('F001', ['a_full'], CORE_STD, {'a_full': VAR_STD}, CITES_STD)
        p = tmp_path / 'F001_test.md'
        p.write_bytes(md.replace('\n', '\r\n').encode('utf-8'))
        fam = cl.parse_family_md(str(p), family_id='F001')
        assert cl.materialize_rendered_citations(fam) is True
        raw = p.read_bytes()
        assert b'\r\n' in raw            # 人工区 CRLF 不被整文件归一 (NIT 修复)
        assert cl.RENDERED_BEGIN.encode() in raw

    def test_draft_bad_citation_warns_final_crashes(self, tmp_path, panel):
        bad = _cite(1)
        bad['type'] = 'jurnal'      # type 拼错
        fams = [{'fid': 'F001', 'columns': ['alpha_tone_full'],
                 'cites': CITES_STD + [bad], 'status': 'draft'}]
        lib = cl.load_library(make_lib(tmp_path / 'd1', fams))
        counters = {'warnings': [], 'composed': 0}
        out = cl.compose_long_description('alpha_tone_full', panel, lib, counters=counters)
        assert out is not None                     # draft 渐进批次不断链
        assert any('type 非法' in w for w in counters['warnings'])
        fams[0]['status'] = 'final'
        lib2 = cl.load_library(make_lib(tmp_path / 'd2', fams))
        with pytest.raises(SystemExit, match='citation 结构校验失败'):
            cl.compose_long_description('alpha_tone_full', panel, lib2)


class TestJsonNanFree:
    """P2-⑤: json 权威载体 NaN → null 归一 (严格 JSON, 非 Python 解析器可读)。"""

    def test_json_authoritative_carrier_strict(self, panel, tmp_path, libdir):
        out = cb.generate_codebook(panel, str(tmp_path / 'o'), formats=['json'],
                                   versioned_dir=str(tmp_path / 'v'), longdesc_dir=libdir)
        txt = Path(out['json']).read_text(encoding='utf-8')

        def _reject(_):
            raise AssertionError('json 权威载体含非法 NaN/Infinity token')
        rows = json.loads(txt, parse_constant=_reject)   # 严格解析不崩 = 零裸 NaN
        # 全 NaN 列 (alpha_tone_ctx) 的统计字段应为 null 而非 NaN
        by_name = {r['变量名']: r for r in rows}
        stats_keys = [k for k in by_name['alpha_tone_ctx']
                      if k not in ('变量名', '标签', '描述', '数据类型', '单位', '取值范围',
                                   '计算公式', '来源阶段', '学术引用', '备注', '变量类别', '文本轨道')]
        assert stats_keys, '统计列缺失 (fixture 失真)'


# ============================================================================
# 11. xlsx 组装层守卫 (§4)
# ============================================================================

class TestXlsxGuard:
    def test_cell_guard_truncates_with_note(self):
        big = '长' * 40000
        safe, truncated = cl.xlsx_cell_guard(big)
        assert truncated and len(safe) <= 30000
        assert safe.endswith('全文见 codebook.md / codebook.json】')
        small, t2 = cl.xlsx_cell_guard('短文本')
        assert not t2 and small == '短文本'

    def test_dataframe_guard_counts(self):
        df = pd.DataFrame({'描述': ['x' * 40000, '短'], '变量名': ['a', 'b']})
        safe, n = cl.xlsx_safe_dataframe(df)
        assert n == 1
        assert len(safe.loc[0, '描述']) <= 30000
        assert df.loc[0, '描述'] == 'x' * 40000   # 原 df 不动 (副本守卫)


# ============================================================================
# 12. gitignore 双断言 + 导出路径不 import 组装器
# ============================================================================

_NEWS_PROCESS_ROOT = Path(cb.__file__).resolve().parents[2]


class TestRepoWiring:
    def test_gitignore_double_assert(self):
        try:
            r1 = subprocess.run(['git', 'check-ignore', '-q', 'build/codebook/x.md'],
                                cwd=str(_NEWS_PROCESS_ROOT), capture_output=True)
            r2 = subprocess.run(['git', 'check-ignore', '-q', 'build/manual_facts/x.md'],
                                cwd=str(_NEWS_PROCESS_ROOT), capture_output=True)
        except FileNotFoundError:
            pytest.skip('git 不可用')
        assert r1.returncode != 0, 'build/codebook/ 应可入 git (三行组合豁免, §4)'
        assert r2.returncode == 0, 'build/manual_facts 应仍被忽略 (/build/* 规则)'

    def test_export_paths_do_not_import_composer(self):
        # §0 铁律 gate: 三条导出链 (stata_export/export/controls) 不 import/调用组装器 —
        # 组装成本/SystemExit 不进 stage 40/46/51 (except Exception 捕不到 SystemExit)。
        # 2026-07-11 反作弊加固 (评审 P1): 原 regex 行首锚定漏掉本仓惯用形态
        # `from news_process.pipeline.panel import codebook_longdesc`, 且调用面只查带
        # 下划线的 '_compose_long_description(' 漏掉叶模块公开名 → 改 AST 判定:
        # 任一 import 节点含 codebook_longdesc / 任一 Name·Attribute 引用
        # (compose_long_description 带或不带下划线) 均 fail; docstring/注释天然豁免。
        import ast
        targets = [
            _NEWS_PROCESS_ROOT / 'pipeline' / 'panel' / 'stata_export.py',
            _NEWS_PROCESS_ROOT / 'pipeline' / 'panel' / 'export.py',
            _NEWS_PROCESS_ROOT / 'pipeline' / 'falsification' / 'controls.py',
        ]
        banned_names = {'compose_long_description', '_compose_long_description'}
        for p in targets:
            tree = ast.parse(p.read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        assert 'codebook_longdesc' not in a.name, \
                            f'{p}:{node.lineno}: 导出路径 import 了组装器模块'
                elif isinstance(node, ast.ImportFrom):
                    mod = node.module or ''
                    assert 'codebook_longdesc' not in mod, \
                        f'{p}:{node.lineno}: 导出路径 from-import 了组装器模块'
                    for a in node.names:
                        assert 'codebook_longdesc' not in a.name, \
                            f'{p}:{node.lineno}: 导出路径 import 了组装器模块'
                        assert a.name not in banned_names, \
                            f'{p}:{node.lineno}: 导出路径 import 了组装器函数 {a.name}'
                elif isinstance(node, ast.Name):
                    assert node.id not in banned_names, \
                        f'{p}:{node.lineno}: 导出路径引用了组装器函数 {node.id}'
                    assert node.id != 'codebook_longdesc', \
                        f'{p}:{node.lineno}: 导出路径引用了组装器模块名'
                elif isinstance(node, ast.Attribute):
                    assert node.attr not in banned_names, \
                        f'{p}:{node.lineno}: 导出路径经属性调用了组装器 {node.attr}'

    def test_import_gate_catches_repo_idiomatic_forms(self, tmp_path):
        # documenting gate 强度: 本仓惯用 import/调用形态 (原 regex 恒绿的两种) 必须被抓
        import ast
        banned_names = {'compose_long_description', '_compose_long_description'}

        def _violates(src: str) -> bool:
            for node in ast.walk(ast.parse(src)):
                if isinstance(node, ast.Import) and any(
                        'codebook_longdesc' in a.name for a in node.names):
                    return True
                if isinstance(node, ast.ImportFrom) and (
                        'codebook_longdesc' in (node.module or '')
                        or any(a.name in banned_names or 'codebook_longdesc' in a.name
                               for a in node.names)):
                    return True
                if isinstance(node, ast.Name) and (
                        node.id in banned_names or node.id == 'codebook_longdesc'):
                    return True
                if isinstance(node, ast.Attribute) and node.attr in banned_names:
                    return True
            return False

        assert _violates('from news_process.pipeline.panel import codebook_longdesc\n')
        assert _violates('from news_process.pipeline.panel import codebook_longdesc as _cl\n')
        assert _violates('import news_process.pipeline.panel.codebook_longdesc as cl\n')
        assert _violates('from .codebook import _compose_long_description\n')
        assert _violates('x = codebook_longdesc.compose_long_description(1)\n')
        assert _violates('y = _compose_long_description(1)\n')
        # docstring/注释声明性提及豁免 (WP2 已落声明)
        assert not _violates('"""刻意不 import codebook_longdesc (§0)"""\n# 见 compose_long_description\nz = 1\n')

    def test_composer_not_in_get_variable_metadata_dict(self):
        # 挂载点唯一性: 组装器刻意不进无参 get_variable_metadata_dict (§0 v2.3)
        import inspect
        src = inspect.getsource(cb.get_variable_metadata_dict)
        assert '_compose_long_description' not in src
        assert 'codebook_longdesc' not in src

    def test_static_metadata_free_of_placeholder_lookalikes(self):
        # 产物级宽占位符零命中的上游守卫: 显式元数据 283 条的文本字段禁含
        # {word:...} 形态 (集合构造记号 #{i: ...} 已改写 count(i ∣ ...), 2026-07-10)
        meta = cb.get_variable_metadata_dict()
        for name, m in meta.items():
            for field_val in (m.description, m.formula, m.notes, m.reference, m.label):
                hits = cl._WIDE_PLACEHOLDER_RE.findall(str(field_val))
                assert hits == [], f'{name}: 元数据字段含占位符形态残留 {hits}'
