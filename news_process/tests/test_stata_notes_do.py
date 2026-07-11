"""test_stata_notes_do — WP2 §3b notes .do 生成全套 gate (纯文本断言, 不依赖 Stata)。

覆盖 (计划 §5 WP2 行 + 编排会话 2026-07-10 规则①重议后的 fuzz 清单):
    - _stata_notes_text 转义 fuzz: `" / $ / 换行 / ` // ` / ` ///` / 段首 TS / \\$ / \\\\ / 尾 \\
      (全角中和方案: 输出零 ASCII 反引号、零 ASCII 反斜杠、零 $+宏名起始序列; $100 保真)
    - 前缀歧义名 exact fuzz (confirm 必带 , exact — probe 实锤缩写匹配 rc=0)
    - 分段字节边界 (多字节字符不切坏 + 每段 ≤4000 字节 + 段首 TS/'//' 守卫, 切分在中和后)
    - 重放两次 == 一次 (幂等结构: notes drop 先行 + 再生成字节确定)
    - 对账数含改名列 (rename_map 短名域)
    - 子卷禁 use/save/exit; master 结构 (version 19 / maxvar / use 一次 / labels 先行 /
      子卷顺序 / save, replace / exit, clear 收尾)
"""
from __future__ import annotations

import json
import os
import re

import pytest

from news_process.pipeline.panel.stata_export import (
    _CODEBOOK_NOTES_JSON_NAMES,
    NOTES_MANIFEST_FILENAME,
    STATA_NOTES_DTA_TARGETS,
    STATA_NOTES_SEG_MAX_BYTES,
    _codebook_notes_json_candidates,
    _load_notes_from_codebook_json,
    _split_note_segments,
    _stata_notes_text,
    compute_expected_notes_count,
    parse_notes_applied_from_log,
    write_notes_do_file,
)

# 危险宏序列检测 (编排会话 fuzz gate 口径)
_DOLLAR_MACRO_RE = re.compile(r'\$[A-Za-z_{]')


def _assert_neutralized(text: str):
    """规则① 全角中和三断言 + 规则④ 空白前导 // 断言。"""
    assert '`' not in text, f'ASCII 反引号残留: {text!r}'
    assert '\\' not in text, f'ASCII 反斜杠残留: {text!r}'
    assert not _DOLLAR_MACRO_RE.search(text), f'$+宏名起始序列残留: {text!r}'
    assert not re.search(r'(?:(?<=\s)|^)/{2,}', text), f'空白前导 // 残留: {text!r}'


# ---------------------------------------------------------------------------
# 1. _stata_notes_text 转义 fuzz
# ---------------------------------------------------------------------------

class TestNotesTextFuzz:
    def test_backtick_and_compound_open(self):
        # `" compound 开定界符: 反引号全量中和后不可能再构成 compound 序列
        out = _stata_notes_text('a `"compound"\' b `x\' c ` alone')
        _assert_neutralized(out)
        assert '｀"compound"\'' in out  # 引号原样, 反引号全角
        assert '｀x\'' in out

    def test_dollar_narrow_neutralization(self):
        out = _stata_notes_text('cost $100, share $ 50%, tail $')
        assert '$100' in out           # $+数字 保真 (probe 边界实证安全)
        assert '$ 50%' in out          # $+空格 保真
        assert out.endswith('$')       # 行尾 $ 保真
        _assert_neutralized(out)
        out2 = _stata_notes_text('macro $gprobe and ${brace} and $_x')
        assert '＄gprobe' in out2 and '＄{brace}' in out2 and '＄_x' in out2
        _assert_neutralized(out2)

    def test_backslash_full_neutralization(self):
        # \$ / \\ / 尾 \ — probe 实锤反斜杠保护在 notes 语境不生效 → 全量中和
        out = _stata_notes_text('esc \\$100 dbl \\\\ tail \\')
        assert '＼$100' in out
        assert '＼＼' in out
        assert out.endswith('＼')
        _assert_neutralized(out)

    def test_newline_normalized_first(self):
        out = _stata_notes_text('a\r\nb\nc\rd\x0be\x0cf g h')
        assert out == 'a b c d e f g h'

    def test_newline_then_comment_interaction(self):
        # 换行先归一 → 换行后紧跟的 // 变成空白前导 // → 须被中和
        out = _stata_notes_text('a\n// b')
        _assert_neutralized(out)
        assert '／／' in out

    def test_comment_sequences(self):
        out = _stata_notes_text('a // b')
        assert 'a ／／ b' in out
        out = _stata_notes_text('a /// b')
        assert 'a ／／／ b' in out
        out = _stata_notes_text('a\t// b')          # tab 前导
        assert '／／' in out
        out = _stata_notes_text('//lead')           # 文首 (notes 行内 ": " 前导空白)
        assert out.startswith('／／')

    def test_doi_url_intact(self):
        out = _stata_notes_text('见 https://doi.org/10.1093/rof/rfab036 全文')
        assert 'https://doi.org/10.1093/rof/rfab036' in out

    def test_no_compound_wrapping_added(self):
        # 规则②: 不包 compound quotes; ASCII 引号原样
        out = _stata_notes_text('say "hello" and \'hi\'')
        assert out == 'say "hello" and \'hi\''

    def test_cjk_passthrough(self):
        s = '构念与来源: 该指标依据 Du et al. (2022) 政治正面词权重 0.5 的研究者选择。'
        assert _stata_notes_text(s) == s

    def test_reconciliation_marker_neutralized(self):
        # P2 整改 (2026-07-11): 正文自含对账 marker 字样 → '=' 换全角 ＝,
        # log 对账 regex (行首锚定版) 必不再命中, 幻影 part 键/last-wins 覆盖通道封死
        s = '文档引用: 收尾打 NOTES_APPLIED_PART01=999 与 NOTES_MASTER_DONE=46 标记。'
        out = _stata_notes_text(s)
        assert 'NOTES_APPLIED_PART01＝999' in out
        assert 'NOTES_MASTER_DONE＝46' in out
        assert parse_notes_applied_from_log(out) == {}
        assert parse_notes_applied_from_log('\n' + out + '\n') == {}
        # 无 '=' 紧跟时不误伤 (纯提及不构成可匹配序列)
        assert _stata_notes_text('见 NOTES_APPLIED_PART 机制') == '见 NOTES_APPLIED_PART 机制'


# ---------------------------------------------------------------------------
# 2. 分段字节边界 (切分须在全角中和之后)
# ---------------------------------------------------------------------------

class TestSegmentation:
    def test_multibyte_not_broken_and_reconstruct(self):
        text = _stata_notes_text('汉' * 3000)  # 9000 字节
        segs = _split_note_segments(text)
        assert len(segs) >= 3
        for s in segs:
            assert len(s.encode('utf-8')) <= STATA_NOTES_SEG_MAX_BYTES
        assert ''.join(segs) == text  # 无守卫触发 → 无损重组 (多字节零切坏)

    def test_default_4000_byte_cap_with_guard_headroom(self):
        # 段首守卫 (U+3000, 3 字节) 含在 4000 预算内
        text = _stata_notes_text('TS ' + '汉' * 2000)
        segs = _split_note_segments(text)
        assert segs[0].startswith('　TS')
        for s in segs:
            assert len(s.encode('utf-8')) <= 4000

    def test_boundary_split_never_starts_with_slashes(self):
        # 构造边界: 首段恰在 'https:' 后切开 → 次段裸 '//' 开头必须被守卫
        budget = STATA_NOTES_SEG_MAX_BYTES - 3
        prefix = 'a' * (budget - 7) + ' https:'
        assert len(prefix.encode('utf-8')) == budget
        text = _stata_notes_text(prefix + '//doi.org/10.1/x')
        segs = _split_note_segments(text)
        assert segs[1].startswith('　//')
        for s in segs:
            assert not s.startswith('/') and not s.startswith('TS')
            assert len(s.encode('utf-8')) <= STATA_NOTES_SEG_MAX_BYTES

    def test_boundary_split_ts_guard(self):
        budget = STATA_NOTES_SEG_MAX_BYTES - 3
        text = _stata_notes_text('b' * budget + 'TS 时间戳守卫')
        segs = _split_note_segments(text)
        assert segs[1].startswith('　TS')

    def test_custom_small_budget(self):
        segs = _split_note_segments('汉字混 mix', max_bytes=7)  # budget=4
        for s in segs:
            assert len(s.encode('utf-8')) <= 7
        # 本例无纯空白段 → 无损重组 (NIT 整改 2026-07-11: 删除原 no-op replace 冗余断言)
        assert ''.join(segs) == '汉字混 mix'


# ---------------------------------------------------------------------------
# 3. write_notes_do_file — 子卷 / master / manifest / 对账
# ---------------------------------------------------------------------------

LONG_ORIG = 'a_very_long_panel_column_name_exceeding_stata_limit_full'
SHORT_OF_LONG = 'a_very_long_pan_c0ffee12'

NOTES = {
    'alpha_var': '普通列注释。含 $abc 宏与 `local\' 与 // 注释与 https://doi.org/10.1/x。',
    'alpha_var2': '前缀歧义列: 与 alpha_var 互为前缀, exact 守卫的存在理由。',
    LONG_ORIG: '超长原名列 (>32 字符), do 内必须用 dta 短名。' + '正文' * 50,
    'zz_tail': 'TS 开头守卫测试文本不在此段 (TS 不在段首)。',
}
RENAME_MAP = {SHORT_OF_LONG: LONG_ORIG}  # {short: original}


@pytest.fixture()
def gen(tmp_path):
    manifest = write_notes_do_file(dict(NOTES), dict(RENAME_MAP), str(tmp_path))
    return tmp_path, manifest


def _read(p):
    return p.read_text(encoding='utf-8')


class TestWriteNotesDoFile:
    def test_rename_map_required(self, tmp_path):
        with pytest.raises(ValueError, match='rename_map'):
            write_notes_do_file(dict(NOTES), None, str(tmp_path))

    def test_empty_notes_rejected(self, tmp_path):
        with pytest.raises(ValueError):
            write_notes_do_file({}, {}, str(tmp_path))

    def test_short_name_collision_failloud(self, tmp_path):
        notes = {'orig_a': 'x', 'col_s': 'y'}
        with pytest.raises(ValueError, match='短名碰撞'):
            write_notes_do_file(notes, {'col_s': 'orig_a'}, str(tmp_path))

    def test_illegal_short_name_skipped_not_silent(self, tmp_path):
        notes = dict(NOTES)
        notes['中文列名'] = '非法 Stata 名, 应跳过并入 manifest 台账。'
        manifest = write_notes_do_file(notes, dict(RENAME_MAP), str(tmp_path))
        assert '中文列名' in manifest['skipped_illegal']
        assert '中文列名' not in manifest['short_to_orig'].values()

    def test_uses_short_name_with_exact_confirm(self, gen):
        tmp_path, manifest = gen
        part = _read(tmp_path / manifest['parts'][0])
        # 改名列: 一律短名作命令对象
        assert f'capture confirm variable {SHORT_OF_LONG}, exact' in part
        assert f'capture notes drop {SHORT_OF_LONG}' in part
        # 原名绝不作命令对象 (只出现在 note 正文/注释行)
        assert f'confirm variable {LONG_ORIG}' not in part
        assert f'notes drop {LONG_ORIG}' not in part
        # note 首段写明原始 panel 列名
        assert f'【原始 panel 列名】{LONG_ORIG}' in part
        # 全部 confirm 行必带 , exact (前缀歧义 fuzz: alpha_var vs alpha_var2)
        confirms = [ln for ln in part.splitlines()
                    if 'confirm variable' in ln and not ln.lstrip().startswith('*')]
        assert len(confirms) == manifest['n_cols_total']
        for ln in confirms:
            assert ln.rstrip().endswith(', exact'), ln

    def test_notes_lines_neutralized(self, gen):
        tmp_path, manifest = gen
        part = _read(tmp_path / manifest['parts'][0])
        note_lines = [ln for ln in part.splitlines() if ln.lstrip().startswith('notes ')]
        assert note_lines
        for ln in note_lines:
            text = ln.split(':', 1)[1]
            _assert_neutralized(text)

    def test_idempotent_structure_drop_before_notes(self, gen):
        tmp_path, manifest = gen
        part = _read(tmp_path / manifest['parts'][0])
        for short in manifest['columns_short']:
            block = part.split(f'* ---- {short} ')[1]
            i_drop = block.find(f'capture notes drop {short}')
            i_note = block.find(f'notes {short}:')
            assert 0 <= i_drop < i_note, f'{short}: notes drop 必须先于注入 (重放幂等)'

    def test_regeneration_deterministic(self, gen, tmp_path):
        _, manifest = gen
        first = {p: _read(tmp_path / p) for p in manifest['parts'] + list(manifest['masters'].values())}
        manifest2 = write_notes_do_file(dict(NOTES), dict(RENAME_MAP), str(tmp_path))
        assert manifest2['parts'] == manifest['parts']
        for p, content in first.items():
            assert _read(tmp_path / p) == content, f'{p}: 重生成字节漂移'

    def test_part_counter_and_footer_marker(self, gen):
        tmp_path, manifest = gen
        part = _read(tmp_path / manifest['parts'][0])
        assert 'local notes_n = 0' in part
        assert "local notes_n = `notes_n' + 1" in part
        assert part.rstrip().endswith('display "NOTES_APPLIED_PART01=`notes_n\'"')

    def test_subvolume_forbids_use_save_exit(self, gen):
        tmp_path, manifest = gen
        for p in manifest['parts']:
            for ln in _read(tmp_path / p).splitlines():
                s = ln.strip().lower()
                assert not s.startswith('use '), ln
                assert not s.startswith('save'), ln
                assert not (s == 'exit' or s.startswith('exit,') or s.startswith('exit ')), ln

    def test_parts_le_500_vars(self, tmp_path):
        notes = {f'col_{i:04d}': f'第 {i} 列注释正文。' for i in range(1203)}
        manifest = write_notes_do_file(notes, {}, str(tmp_path))
        assert manifest['n_parts'] == 3
        assert list(manifest['per_part_counts'].values()) == [500, 500, 203]
        # 各卷 footer 标记编号与文件名一致
        for idx, p in enumerate(manifest['parts'], 1):
            assert f'NOTES_APPLIED_PART{idx:02d}=' in _read(tmp_path / p)

    def test_master_structure(self, gen):
        tmp_path, manifest = gen
        assert set(manifest['masters']) == {'40', '46', '51'}
        for key, mname in manifest['masters'].items():
            assert mname == f'{key}_apply_notes_master.do'
            m = _read(tmp_path / mname)
            lines = [ln.strip() for ln in m.splitlines() if ln.strip() and not ln.startswith('*')]
            dta = STATA_NOTES_DTA_TARGETS[key]
            assert lines[0] == 'version 19'
            assert 'set maxvar 32767' in lines
            # use 恰一次, 且先 labels 后子卷, save 收尾于子卷后, exit, clear 终结
            assert lines.count(f'use "{dta}"') == 1
            i_use = m.find(f'use "{dta}"')
            i_labels = m.find(f'do "{manifest["labels_do"]}"')
            i_part1 = m.find(f'do "{manifest["parts"][0]}"')
            i_save = m.find(f'save "{dta}", replace')
            i_exit = m.find('exit, clear')
            assert 0 < i_use < i_labels < i_part1 < i_save < i_exit
            # 子卷顺序
            pos = [m.find(f'do "{p}"') for p in manifest['parts']]
            assert pos == sorted(pos) and all(x > 0 for x in pos)
            assert lines[-1] == 'exit, clear'
            assert f'NOTES_MASTER_DONE={key}' in m

    def test_manifest_on_disk_matches_return(self, gen):
        tmp_path, manifest = gen
        on_disk = json.loads(_read(tmp_path / NOTES_MANIFEST_FILENAME))
        assert on_disk == manifest


# ---------------------------------------------------------------------------
# 4. 对账 (log 标记法) — 期望数含改名列 / 51-only 列排除
# ---------------------------------------------------------------------------

class TestReconciliation:
    def test_expected_count_includes_renamed_column(self, gen):
        _, manifest = gen
        # dta 宇宙含短名 → 改名列计入期望数 (§7.5: 假绿即改名列永久无 notes)
        dta_cols = ['alpha_var', 'alpha_var2', SHORT_OF_LONG, 'zz_tail', 'other_col']
        assert compute_expected_notes_count(dta_cols, manifest['columns_short']) == 4
        # 40/46 宇宙缺列 (镜像 51-only 11 列): exact-confirm 跳过并从期望数排除
        assert compute_expected_notes_count(['alpha_var', 'zz_tail'], manifest['columns_short']) == 2
        # 用原名对账 = 假绿形态 → 改名列必不计入 (防御性验证)
        assert compute_expected_notes_count([LONG_ORIG], manifest['columns_short']) == 0

    def test_parse_log_markers_ignores_echoed_command(self):
        log = (
            '. do "apply_notes_part01.do"\n'
            '. display "NOTES_APPLIED_PART01=`notes_n\'"\n'   # 命令回显: = 后非数字, 不匹配
            'NOTES_APPLIED_PART01=500\n'
            'NOTES_APPLIED_PART02=203\n'
        )
        assert parse_notes_applied_from_log(log) == {1: 500, 2: 203}

    def test_parse_log_replay_last_wins(self):
        log = 'NOTES_APPLIED_PART01=3\nblah\nNOTES_APPLIED_PART01=5\n'
        assert parse_notes_applied_from_log(log) == {1: 5}

    def test_parse_log_anchored_rejects_non_line_start(self):
        """P2 整改 (2026-07-11): 非行首/带前后缀的 marker 一律不计 (回显/折行通道)."""
        log = (
            '. display 伪回显 NOTES_APPLIED_PART01=999\n'      # 行中: 回显通道
            '> NOTES_APPLIED_PART02=888\n'                     # 折行续行 '> ' 前缀
            '  NOTES_APPLIED_PART03=777\n'                     # 缩进
            'NOTES_APPLIED_PART04=666 尾随正文\n'               # 行首但尾随非空白
            'NOTES_APPLIED_PART05=5\n'                         # 唯一合法行
        )
        assert parse_notes_applied_from_log(log) == {5: 5}
        # CRLF log (Stata Windows 实况): \r 由 \s*$ 吸收
        assert parse_notes_applied_from_log('NOTES_APPLIED_PART01=42\r\n') == {1: 42}

    def test_generated_part_file_has_zero_marker_matches_before_execution(self):
        """端到端: 正文带 marker 字样的列, 生成的子卷文本本身 0 命中对账 regex.

        (footer display 行 '=' 后跟反引号、命令行非行首输出形态 — 只有 Stata
        实际执行后的 display 输出才可能产生合法 marker 行。)
        """
        notes = {'poison_col': '引用机制文档: NOTES_APPLIED_PART01=123; NOTES_MASTER_DONE=46。'}
        import pathlib
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            manifest = write_notes_do_file(notes, {}, td)
            part = pathlib.Path(td, manifest['parts'][0]).read_text(encoding='utf-8')
        assert parse_notes_applied_from_log(part) == {}
        assert 'NOTES_APPLIED_PART01＝123' in part  # 全角中和后的正文仍保留可读语义


# ---------------------------------------------------------------------------
# 5. loader ↔ WP1 落盘 json 接线 gate (P1 整改 2026-07-11)
#    背景: loader 曾读 build/codebook/codebook.json, 而 WP1 权威落盘名是
#    variable_codebook.json → 生产上整条 notes 注入链静默失活且日志误导
#    ("两端各自绿、合起来死"的接线断点必须有跨端 gate)。
# ---------------------------------------------------------------------------

_REAL_CODEBOOK_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'build', 'codebook'))


class TestLoaderCodebookJsonWiring:
    def test_canonical_filename_is_variable_codebook_json(self):
        """落盘名 SSOT 接线锚: 首选名 = variable_codebook.json (WP1 写端同名)."""
        assert _CODEBOOK_NOTES_JSON_NAMES[0] == 'variable_codebook.json'
        cands = _codebook_notes_json_candidates()
        assert os.path.basename(cands[0]) == 'variable_codebook.json'
        assert os.path.normpath(cands[0]).replace('\\', '/').endswith(
            'build/codebook/variable_codebook.json')

    def test_loader_reads_fixture_named_variable_codebook_json(self, tmp_path):
        """fixture 接线: loader 必须能从 **该文件名** 取出非空 notes 文本
        (schema = 真实 WP1 记录键 变量名/描述 的 list[dict] 形态)."""
        recs = [
            {'变量名': 'alpha_var', '描述': '【构念与来源】测试长注释正文, 含 DOI '
                                          'https://doi.org/10.1093/rof/rfab036。',
             '标签': '甲列', '数据类型': 'float64'},
            {'变量名': 'empty_desc_col', '描述': '   ', '标签': '空描述应被跳过'},
        ]
        (tmp_path / 'variable_codebook.json').write_text(
            json.dumps(recs, ensure_ascii=False), encoding='utf-8')
        out = _load_notes_from_codebook_json(base_dir=str(tmp_path))
        assert out == {'alpha_var': recs[0]['描述']}

    def test_loader_falls_back_to_legacy_codebook_json_name(self, tmp_path):
        """旧名 codebook.json 回退仍可读 (deprecated 兼容, 首选名缺席时)."""
        (tmp_path / 'codebook.json').write_text(
            json.dumps([{'变量名': 'x', '描述': '旧名产物注释。'}], ensure_ascii=False),
            encoding='utf-8')
        assert _load_notes_from_codebook_json(base_dir=str(tmp_path)) == {'x': '旧名产物注释。'}

    def test_loader_prefers_canonical_over_legacy(self, tmp_path):
        (tmp_path / 'variable_codebook.json').write_text(
            json.dumps([{'变量名': 'x', '描述': '权威名。'}], ensure_ascii=False),
            encoding='utf-8')
        (tmp_path / 'codebook.json').write_text(
            json.dumps([{'变量名': 'x', '描述': '旧名。'}], ensure_ascii=False),
            encoding='utf-8')
        assert _load_notes_from_codebook_json(base_dir=str(tmp_path)) == {'x': '权威名。'}

    def test_loader_missing_dir_returns_empty_not_raise(self, tmp_path):
        assert _load_notes_from_codebook_json(base_dir=str(tmp_path / 'nope')) == {}

    def test_loader_reads_real_wp1_output_when_present(self):
        """跨端集成 gate: 盘上真实 WP1 产物存在时 loader 必须取出非空 notes.

        (2026-07-10 评审实锤: 盘上 variable_codebook.json 3,453 条而 loader 返回
        0 条 — 本 gate 在真实产物上锁死 '写端 3453 / 读端 0' 这类接线漂移。)
        """
        real = os.path.join(_REAL_CODEBOOK_DIR, 'variable_codebook.json')
        if not os.path.exists(real):
            pytest.skip('build/codebook/variable_codebook.json 不在盘上 (WP1 未跑)')
        out = _load_notes_from_codebook_json()
        assert out, 'WP1 json 在盘却取出 0 条 notes — loader↔落盘接线再次漂移'
        sample = next(iter(out.items()))
        assert isinstance(sample[0], str) and sample[0]
        assert isinstance(sample[1], str) and sample[1].strip()
