"""引文闸红队旁路封堵 gate 测试 (2026-07-11 citation-gates 六维终审整改)。

固化六维对抗评审 citation-gates 维 (红队复现 scratchpad/redteam_repro.py) 实锤的
旁路封堵证据 — 每个旁路一个负例 (整改前可静默穿过, 整改后必 fatal/SystemExit):

  A (P1): frontmatter family_id 覆盖 _index 键 → final 自贬 draft, 越权 DOI 降级告警;
          对账闸只比家族数长度不比集合 → 等长换键欺骗静默漏检。
  B (P2): 大小写变体 DOI.ORG/ 同时逃逸 lint 与 extract_refs。
  C (P1): doi.org 链接藏 frontmatter 标量字段 (formula 等) 同时逃逸 lint 与差集闸
          并流入组装产物。
  台账 (P1): _new_dois_ledger.json 谁写谁准入被差集闸盲信 → 只认 admit_new_dois.py
          完整核验条目 (crossref 回比 + 撤稿筛查 + entry_sha)。
  另: no_doi_ack 登记核验 / 新颖度闸 (§2.8) / 重复 DOI 闸 (§2.10) /
      type↔venue 交叉校验 / 锚缺失 fail-loud / 元数据缓存签名。

刻意独立成文件 (不改 test_codebook_longdesc.py 既有断言 — 该文件由并发整改会话
同时持有); fixture 构造器为本文件自足副本。
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from news_process.pipeline.panel import codebook_longdesc as cl
from news_process.scripts.audit import admit_new_dois as adm
from news_process.scripts.audit import audit_dois
from news_process.scripts.audit import check_longdesc_whitelist as chk

# ============================================================================
# 自足 fixture 构造器
# ============================================================================

WL_DOIS = [f'10.1000/wl{i}' for i in range(1, 15)]
WL = {cl.normalize_doi(d) for d in WL_DOIS}
TOPCFG = {'top': ['Journal of Finance'], 'field': ['Journal of Banking and Finance']}
_LONG_TITLE = ('A sufficiently long empirical study of bank fintech news sentiment '
               'measurement construction and validation methodology, part ')


def _cite(i, doi=None, ctype='journal', venue='Journal of Finance', year=2024, **kw):
    c = {'doi': WL_DOIS[i] if doi is None else doi, 'type': ctype,
         'authors': f'Author{i}, A., & Coauthor{i}, B.', 'year': year,
         'title': _LONG_TITLE + str(i), 'venue': venue}
    c.update(kw)
    return c


CITES = [_cite(1), _cite(2), _cite(3)]


def _fam_md_text(fid_fm, cites, *, columns=('alpha_tone_full',), new_dois=(),
                 extra_fm=None, body_extra='', rendered='auto'):
    fm = {'family_id': fid_fm, 'columns': list(columns), 'unit': '比率',
          'formula': 'x = a / b', 'producer': 'pipeline/sentiment/tone_words.py::fn',
          'upstream': [], 'citations': cites, 'new_dois': list(new_dois)}
    if extra_fm:
        fm.update(extra_fm)
    txt = '---\n' + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + '---\n\n'
    txt += '## CORE\n\n家族核心说明文本。' + body_extra + '\n\n'
    block = cl.render_citations_block(cites) if rendered == 'auto' else rendered
    if block is not None:
        txt += f'{cl.RENDERED_BEGIN}\n{block}\n{cl.RENDERED_END}\n'
    return txt


def make_lib(tmp_path: Path, fams) -> str:
    """fams: list of dict(fid, cites, status, fid_fm, skip_md, md_kw...)。"""
    libdir = tmp_path / 'longdesc'
    libdir.mkdir(parents=True, exist_ok=True)
    index = {'families': {}}
    for f in fams:
        fid = f['fid']
        fname = f.get('fname', f'{fid}_test.md')
        index['families'][fid] = {
            'file': fname, 'columns': list(f.get('columns', ['alpha_tone_full'])),
            'tier_by_col': {}, 'status': f.get('status', 'draft'), 'batch': 1,
        }
        if not f.get('skip_md'):
            (libdir / fname).write_text(
                _fam_md_text(f.get('fid_fm', fid), f.get('cites', CITES),
                             columns=f.get('columns', ('alpha_tone_full',)),
                             new_dois=f.get('new_dois', ()),
                             extra_fm=f.get('extra_fm'),
                             body_extra=f.get('body_extra', ''),
                             rendered=f.get('rendered', 'auto')),
                encoding='utf-8')
    (libdir / '_index.json').write_text(
        json.dumps(index, ensure_ascii=False, indent=1), encoding='utf-8')
    return str(libdir)


def run_capture(libdir, **kw):
    """run_checks 容 SystemExit (引擎层 parse_family_md 亦可能先 fail-loud —
    与 check 层 fatal 同为封堵成立; 双层防御任一触发即算拦截)。"""
    try:
        return chk.run_checks(libdir, whitelist=set(WL), top_journal_cfg=TOPCFG, **kw)
    except SystemExit as e:
        return {'fatal': [f'SystemExit: {e}'], 'warnings': [], 'systemexit': True}


def _verified_entry(doi, title=_LONG_TITLE + '0'):
    e = {'doi': cl.normalize_doi(doi), 'admitted_date': '2026-07-11',
         'admitted_by': chk.LEDGER_ADMITTED_BY, 'crossref_title': title,
         'retraction_check': 'pass', 'verify_agent': 'pending'}
    e['entry_sha'] = chk.ledger_entry_sha(e)
    return e


# ============================================================================
# 旁路 A (P1): family_id 自贬 + 等长换键对账欺骗
# ============================================================================

class TestBypassAFamilyIdSpoof:
    def test_final_family_cannot_self_demote_via_family_id(self, tmp_path):
        # 红队场景 A 原样复现: index 注册 F001 final + 越权 DOI, md frontmatter 声明
        # family_id F999 → 整改前 fatal=[] 仅 draft 降级告警; 整改后必拦截。
        d = make_lib(tmp_path, [{
            'fid': 'F001', 'status': 'final', 'fid_fm': 'F999',
            'cites': CITES + [_cite(0, doi='10.9999/rogue')],
            'new_dois': ('10.9999/rogue',),
        }])
        rep = run_capture(d)
        assert rep['fatal'], '旁路 A 未封: final 自贬 draft 后 0 fatal'
        # 不允许出现"降级告警放行"结局
        assert not (not rep.get('systemexit') and rep['fatal'] == []
                    and any('draft 越权' in w for w in rep['warnings']))
        assert any('family_id' in e for e in rep['fatal'])

    def test_status_ssot_is_index_key_not_frontmatter(self, tmp_path):
        # frontmatter 声明 status 键本身即 fatal (status SSOT=_index.json)
        d = make_lib(tmp_path, [{'fid': 'F001', 'status': 'final',
                                 'extra_fm': {'status': 'draft'}}])
        rep = run_capture(d)
        assert any('status' in e for e in rep['fatal'])

    def test_equal_length_key_swap_caught_by_set_reconciliation(self, tmp_path):
        # index {F001, F002} 家族数=2; F002 md 缺失 + 多一个未登记 md → md 数仍=2,
        # 旧长度对账恒绿; 集合对账 + 未登记 fatal 双双点名。
        d = make_lib(tmp_path, [{'fid': 'F001'},
                                {'fid': 'F002', 'skip_md': True}])
        (Path(d) / 'F003_orphan.md').write_text(
            _fam_md_text('F003', CITES), encoding='utf-8')
        rep = run_capture(d)
        assert any('未在 _index.json 登记' in e for e in rep['fatal'])
        assert any('家族数' in e and ('index-only' in e or 'md-only' in e)
                   for e in rep['fatal'])

    def test_clean_library_still_zero_fatal(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001'}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert rep['fatal'] == [] and rep['warnings'] == []


# ============================================================================
# 旁路 B (P2): 大小写变体 DOI.ORG/
# ============================================================================

class TestBypassBCaseVariant:
    def test_uppercase_doiorg_in_prose_fatal(self, tmp_path):
        # 红队场景 B 原样复现: 整改前 lint ('doi.org/' 小写子串) 与 extract_refs
        # (无 re.I) 双双漏过。
        d = make_lib(tmp_path, [{'fid': 'F001', 'status': 'final',
                                 'body_extra': ' 证据见 https://DOI.ORG/10.9999/evilcase 处'}])
        rep = run_capture(d)
        assert any('doi.org' in e.lower() for e in rep['fatal']), '旁路 B 未封'

    def test_mixed_case_variant_also_fatal(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001',
                                 'body_extra': ' https://Doi.Org/10.9999/mixed 引'}])
        rep = run_capture(d)
        assert any('doi.org' in e.lower() for e in rep['fatal'])

    def test_extract_refs_catches_uppercase_and_normalizes_lower(self, tmp_path):
        p = tmp_path / 'anchor_case.md'
        p.write_text('x https://DOI.ORG/10.5555/UPPER1 y\n'
                     'z https://doi.org/10.5555/lower1 w\n', encoding='utf-8')
        refs = set(audit_dois.extract_refs(str(p)))
        assert '10.5555/upper1' in refs   # 多捕 + clean_doi().lower() 归一
        assert '10.5555/lower1' in refs   # 既有小写行为零回归

    def test_lowercase_prose_doiorg_still_fatal_regression(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001',
                                 'body_extra': ' 见 https://doi.org/10.1/bad 处'}])
        rep = run_capture(d)
        assert any('doi.org' in e for e in rep['fatal'])


# ============================================================================
# 旁路 C (P1): frontmatter 标量藏 doi.org
# ============================================================================

class TestBypassCFrontmatterScalar:
    def test_formula_scalar_doiorg_fatal(self, tmp_path):
        # 红队场景 C 原样复现: formula 标量携带白名单外真实 DOI 链接 → 整改前
        # 同时逃逸 lint (只扫 human_zone) 与差集闸 (只查 citations[].doi)。
        d = make_lib(tmp_path, [{'fid': 'F001', 'status': 'final', 'extra_fm': {
            'formula': 'X = Y; see Rogue paper https://doi.org/10.9999/fmrogue'}}])
        rep = run_capture(d)
        assert any('fmrogue' in e or 'frontmatter' in e for e in rep['fatal']), '旁路 C 未封'

    def test_uppercase_in_frontmatter_scalar_fatal(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'extra_fm': {
            'unit': '见 https://DOI.ORG/10.9999/fmupper'}}])
        rep = run_capture(d)
        assert any('frontmatter' in e for e in rep['fatal'])

    def test_nested_scalar_citation_title_doiorg_fatal(self, tmp_path):
        bad = _cite(4, title='A study, full text at https://doi.org/10.9999/intitle')
        d = make_lib(tmp_path, [{'fid': 'F001', 'cites': CITES + [bad]}])
        rep = run_capture(d)
        assert any('citations[3].title' in e for e in rep['fatal'])

    def test_structured_doi_fields_exempt(self, tmp_path):
        # citations[].doi / new_dois[] 是结构化承载域 (裸 DOI), 不触 frontmatter lint
        d = make_lib(tmp_path, [{'fid': 'F001',
                                 'cites': CITES + [_cite(0, doi='10.9999/declared')],
                                 'new_dois': ('10.9999/declared',)}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert not any('frontmatter 标量' in e for e in rep['fatal'])
        assert any('draft 越权' in w for w in rep['warnings'])   # 走 v2.9 draft 出口


# ============================================================================
# 台账机器准入 (P1): 只认 admit_new_dois.py 完整核验条目
# ============================================================================

class TestLedgerHardening:
    def _lib_with_rogue(self, tmp_path, status='final'):
        return make_lib(tmp_path, [{
            'fid': 'F001', 'status': status,
            'cites': CITES + [_cite(0, doi='10.9999/adm1')],
            'new_dois': ('10.9999/adm1',) if status == 'draft' else (),
        }])

    def test_bare_ledger_entry_no_longer_admits(self, tmp_path):
        # 红队 P1 原样复现: 写手 agent 直写一行 {'doi': ...} 即自我扩容白名单
        d = self._lib_with_rogue(tmp_path)
        (Path(d) / '_new_dois_ledger.json').write_text(json.dumps(
            {'entries': [{'doi': '10.9999/adm1', 'admitted_date': '2026-07-10',
                          'round': 1}]}), encoding='utf-8')
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert any('10.9999/adm1' in e for e in rep['fatal']), '台账直写旁路未封'
        assert any('缺完整核验记录' in w for w in rep['warnings'])

    def test_tampered_entry_sha_rejected(self, tmp_path):
        d = self._lib_with_rogue(tmp_path)
        e = _verified_entry('10.9999/other')
        e['doi'] = '10.9999/adm1'          # 换 DOI 不重算 sha = 篡改
        (Path(d) / '_new_dois_ledger.json').write_text(
            json.dumps({'entries': [e]}), encoding='utf-8')
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert any('10.9999/adm1' in e2 for e2 in rep['fatal'])
        assert any('entry_sha' in w for w in rep['warnings'])

    def test_verified_entry_admits(self, tmp_path):
        d = self._lib_with_rogue(tmp_path)
        (Path(d) / '_new_dois_ledger.json').write_text(json.dumps(
            {'entries': [_verified_entry('10.9999/adm1')]}), encoding='utf-8')
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert rep['fatal'] == []
        assert rep['n_ledger'] == 1 and rep['n_ledger_rejected'] == 0

    def test_verify_agent_flip_does_not_break_sha(self, tmp_path):
        # 对抗五元组复核接口: verify_agent pending→done 刻意不入哈希域
        e = _verified_entry('10.9999/adm1')
        e['verify_agent'] = 'done'
        assert chk._ledger_entry_verified(e) is None

    def test_load_ledger_legacy_default_backcompat(self, tmp_path):
        # batch_longdesc_gate 既有调用 load_ledger(dir) 的宽松历史视图不破坏
        d = self._lib_with_rogue(tmp_path)
        (Path(d) / '_new_dois_ledger.json').write_text(json.dumps(
            {'entries': [{'doi': '10.9999/adm1'}]}), encoding='utf-8')
        assert '10.9999/adm1' in chk.load_ledger(d)
        assert chk.load_ledger_verified(d) == set()


# ============================================================================
# admit_new_dois CLI (准入五步: citations 落地 / crossref 回比 / 撤稿筛查 / 写台账)
# ============================================================================

def _fetch_ok(doi):
    return {'title': _LONG_TITLE + '0', 'container': 'Journal of Finance',
            'year': 2025, 'src': 'crossref', 'message': {}}


class TestAdmitNewDois:
    def _draft_lib(self, tmp_path):
        return make_lib(tmp_path, [{
            'fid': 'F001', 'status': 'draft',
            'cites': CITES + [_cite(0, doi='10.9999/new1', title=_LONG_TITLE + '0')],
            'new_dois': ('10.9999/new1',)}])

    def test_admit_then_check_clears_draft_warning(self, tmp_path):
        d = self._draft_lib(tmp_path)
        rep0 = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert any('draft 越权' in w for w in rep0['warnings'])
        r = adm.admit_dois(['10.9999/new1'], d, fetch=_fetch_ok)
        assert [x[0] for x in r['admitted']] == ['10.9999/new1']
        assert '10.9999/new1' in chk.load_ledger_verified(d)
        rep1 = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert rep1['fatal'] == []
        assert not any('draft 越权' in w for w in rep1['warnings'])

    def test_title_mismatch_refused(self, tmp_path):
        d = self._draft_lib(tmp_path)

        def bad_fetch(doi):
            return {'title': 'Completely unrelated botany treatise on orchids',
                    'container': 'X', 'year': 2025, 'src': 'crossref', 'message': {}}
        r = adm.admit_dois(['10.9999/new1'], d, fetch=bad_fetch)
        assert r['admitted'] == []
        assert any('回比' in why for _, why in r['failed'])
        assert chk.load_ledger_verified(d) == set()

    def test_retracted_refused(self, tmp_path):
        d = self._draft_lib(tmp_path)

        def retracted_fetch(doi):
            m = {'updated-by': [{'type': 'retraction', 'DOI': '10.1/notice'}]}
            return {'title': _LONG_TITLE + '0', 'container': 'X', 'year': 2025,
                    'src': 'crossref', 'message': m}
        r = adm.admit_dois(['10.9999/new1'], d, fetch=retracted_fetch)
        assert any('撤稿' in why for _, why in r['failed'])

    def test_update_notice_record_refused(self, tmp_path):
        d = self._draft_lib(tmp_path)

        def notice_fetch(doi):
            m = {'update-to': [{'type': 'retraction', 'DOI': '10.1/original'}]}
            return {'title': _LONG_TITLE + '0', 'container': 'X', 'year': 2025,
                    'src': 'crossref', 'message': m}
        r = adm.admit_dois(['10.9999/new1'], d, fetch=notice_fetch)
        assert any('通告' in why for _, why in r['failed'])

    def test_retracted_title_prefix_refused(self, tmp_path):
        d = self._draft_lib(tmp_path)

        def prefix_fetch(doi):
            return {'title': 'RETRACTED: ' + _LONG_TITLE + '0', 'container': 'X',
                    'year': 2025, 'src': 'crossref', 'message': {}}
        r = adm.admit_dois(['10.9999/new1'], d, fetch=prefix_fetch)
        assert any('撤稿' in why or 'RETRACTED' in why or '前缀' in why
                   for _, why in r['failed'])

    def test_doi_not_landed_in_citations_refused(self, tmp_path):
        d = self._draft_lib(tmp_path)
        r = adm.admit_dois(['10.9999/ghost'], d, fetch=_fetch_ok)
        assert any('不在任何家族 citations' in why for _, why in r['failed'])

    def test_scan_drafts_collects_pending(self, tmp_path, monkeypatch):
        d = self._draft_lib(tmp_path)
        monkeypatch.setattr(audit_dois, 'whitelist_dois', lambda: set(WL_DOIS))
        pend = adm.scan_draft_new_dois(d, WL | chk.load_ledger_verified(d))
        assert pend == ['10.9999/new1']

    def test_ledger_entry_written_is_verified_shape(self, tmp_path):
        d = self._draft_lib(tmp_path)
        adm.admit_dois(['10.9999/new1'], d, fetch=_fetch_ok)
        data = json.loads((Path(d) / '_new_dois_ledger.json').read_text(encoding='utf-8'))
        e = data['entries'][0]
        assert e['admitted_by'] == chk.LEDGER_ADMITTED_BY
        assert e['retraction_check'] == 'pass' and e['crossref_title']
        assert e['verify_agent'] == 'pending'
        assert chk._ledger_entry_verified(e) is None

    def test_dry_run_does_not_write(self, tmp_path):
        d = self._draft_lib(tmp_path)
        r = adm.admit_dois(['10.9999/new1'], d, fetch=_fetch_ok, dry_run=True)
        assert r['admitted']
        assert not (Path(d) / '_new_dois_ledger.json').exists()


# ============================================================================
# no_doi_ack 登记核验 (P2)
# ============================================================================

class TestNoDoiAckRegistry:
    def _lib_with_ack(self, tmp_path):
        book = {'doi': '', 'type': 'book', 'authors': 'Chesbrough, H.', 'year': 2003,
                'title': 'Open Innovation', 'venue': 'HBS Press',
                'no_doi_ack': 'ACK-9', 'alt_link': 'https://worldcat.org/isbn/1'}
        return make_lib(tmp_path, [{'fid': 'F001', 'cites': CITES + [book]}])

    def test_unregistered_ack_fatal(self, tmp_path):
        d = self._lib_with_ack(tmp_path)
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert any("'ACK-9'" in e and '未在台账登记' in e for e in rep['fatal'])

    def test_registered_ack_passes(self, tmp_path):
        d = self._lib_with_ack(tmp_path)
        adm.register_ack(d, 'ACK-9', note='Chesbrough 2003 专著')
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert not any('ACK-9' in e for e in rep['fatal'])

    def test_standalone_ack_ledger_file_also_accepted(self, tmp_path):
        d = self._lib_with_ack(tmp_path)
        (Path(d) / '_no_doi_ack_ledger.json').write_text(
            json.dumps({'entries': [{'ack_id': 'ACK-9', 'note': 'x'}]}),
            encoding='utf-8')
        assert 'ACK-9' in chk.load_ack_registry(d)
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert not any('ACK-9' in e for e in rep['fatal'])


# ============================================================================
# 新颖度闸 (§2.8, P2: 原零实现)
# ============================================================================

def _old_cites():
    return [_cite(1, year=2015), _cite(2, year=2016), _cite(3, year=2018)]


class TestNoveltyGate:
    def test_all_final_low_recency_hard_fatal(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'status': 'final',
                                 'cites': _old_cites()}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert any('新颖度硬闸' in e for e in rep['fatal'])
        assert rep['novelty']['enforced'] is True

    def test_batch_with_draft_reports_only(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'status': 'final', 'cites': _old_cites()},
                                {'fid': 'F002', 'status': 'draft', 'cites': CITES}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert not any('新颖度' in e for e in rep['fatal'])
        assert rep['novelty']['enforced'] is False
        assert rep['novelty']['n_scored'] == 6

    def test_novelty_hard_true_forces_even_with_draft(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'status': 'draft',
                                 'cites': _old_cites()}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG,
                             novelty_hard=True)
        assert any('新颖度硬闸' in e for e in rep['fatal'])

    def test_construct_definition_family_exempt_with_rationale(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'status': 'final',
                                 'cites': _old_cites(), 'extra_fm': {
                                     'novelty_exempt_rationale':
                                         '构念定义型家族: W&Z 1998 吸收能力原始锚不可替代'}}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert not any('新颖度' in e for e in rep['fatal'])
        assert 'F001' in rep['novelty']['exempt_families']
        assert rep['novelty']['n_scored'] == 0

    def test_recent_majority_passes(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'status': 'final',
                                 'cites': [_cite(1, year=2023), _cite(2, year=2025),
                                           _cite(3, year=2015)]}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert not any('新颖度' in e for e in rep['fatal'])
        assert rep['novelty']['frac'] == pytest.approx(2 / 3)

    def test_skeleton_zero_citations_silent(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001', 'cites': []}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert rep['novelty']['n_scored'] == 0
        assert rep['fatal'] == [] and rep['warnings'] == []


# ============================================================================
# 重复 DOI 闸 (§2.10) + type↔venue 交叉校验 + venue 归一
# ============================================================================

class TestRemainingNits:
    def test_duplicate_doi_in_family_fatal(self, tmp_path):
        d = make_lib(tmp_path, [{'fid': 'F001',
                                 'cites': CITES + [_cite(4, doi=WL_DOIS[1])]}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert any('重复 DOI' in e for e in rep['fatal'])

    def test_type_venue_crosscheck_warns(self, tmp_path):
        wp_disguise = _cite(4, ctype='wp', venue='Journal of Finance')
        d = make_lib(tmp_path, [{'fid': 'F001', 'cites': CITES + [wp_disguise]}])
        rep = chk.run_checks(d, whitelist=set(WL), top_journal_cfg=TOPCFG)
        assert any('交叉校验' in w for w in rep['warnings'])
        assert not any('交叉校验' in e for e in rep['fatal'])   # WARN only

    def test_honest_wp_venue_no_warn(self):
        assert chk.type_venue_crosscheck(
            [_cite(4, ctype='wp', venue='NBER Working Paper')], TOPCFG, 'F00X') == []

    def test_the_prefix_venue_normalized_top(self):
        assert chk.classify_citation(
            _cite(1, venue='The Journal of Finance'), TOPCFG) == 'top'


# ============================================================================
# audit_dois 加固: 锚缺失 fail-loud + 缓存签名 + 锚列表冻结
# ============================================================================

class TestAuditDoisHardening:
    def test_missing_anchor_systemexit(self, monkeypatch, tmp_path):
        good = tmp_path / 'ok.md'
        good.write_text('x https://doi.org/10.5555/ok1 y\n', encoding='utf-8')
        monkeypatch.setattr(audit_dois, 'FILES_WHITELIST_ANCHOR',
                            (str(good), str(tmp_path / 'GONE.md')))
        with pytest.raises(SystemExit):
            audit_dois.whitelist_dois()

    def test_anchor_frozen_immutable_tuple(self):
        assert isinstance(audit_dois.FILES_WHITELIST_ANCHOR, tuple)
        assert audit_dois.FILES is audit_dois.FILES_WHITELIST_ANCHOR

    def test_cache_roundtrip_signed(self, monkeypatch, tmp_path):
        monkeypatch.setattr(audit_dois, 'CACHE_PATH', str(tmp_path / 'cache.json'))
        audit_dois._save_meta_cache({'10.1/a': {'title': 'T', 'src': 'crossref'}})
        assert audit_dois._load_meta_cache() == {'10.1/a': {'title': 'T', 'src': 'crossref'}}

    def test_unsigned_legacy_cache_ignored(self, monkeypatch, tmp_path):
        p = tmp_path / 'cache.json'
        p.write_text(json.dumps({'10.1/a': {'title': 'Poisoned title'}}),
                     encoding='utf-8')
        monkeypatch.setattr(audit_dois, 'CACHE_PATH', str(p))
        assert audit_dois._load_meta_cache() == {}   # 旧扁平/无签名 → 弃用回退网络

    def test_tampered_cache_ignored(self, monkeypatch, tmp_path):
        p = tmp_path / 'cache.json'
        monkeypatch.setattr(audit_dois, 'CACHE_PATH', str(p))
        audit_dois._save_meta_cache({'10.1/a': {'title': 'Real'}})
        data = json.loads(p.read_text(encoding='utf-8'))
        data['entries']['10.1/a']['title'] = 'Poisoned'   # 改内容不改签名
        p.write_text(json.dumps(data), encoding='utf-8')
        assert audit_dois._load_meta_cache() == {}
