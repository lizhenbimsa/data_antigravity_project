"""tests/test_omni_fix_templates.py — omni 审计修复组 g-templates 回归锁 (2026-06-11).

锁定 papers/_common/stata_templates/**.do.tmpl (+ falsification 模板) 的修复行为:
    g-templates-01  falsification 模板 Hassan 检验 1-4 ctx 平行块 (主指标
                    llm_vote_tone_ctx 首次纳入伪造检验) + 模板头双轨披露
    g-templates-03  brokerage R3 假稳健性列 → 真实剔除 singleton 银行组;
                    Table 2 M3 注释不再虚称 over-identification
    g-templates-04  守卫模式缺陷族: 连续双 capture confirm 合并 (brokerage/llm_peer);
                    benefit 14 foreach-continue no-op 守卫改整块 if; esttab 硬点名
                    → estimates dir 动态名单 (含 strategic_diff table5c)
    g-templates-06  36 字符 outcome 全链改 ≤32 字符短名 car_3day_window_ft_announce
    g-templates-07  guard-跳过 + 未守卫具名 esttab → 动态名单 (collab 15/16/18,
                    attention 19 等)
    g-templates-08  collab/17 字符串 HET_VAR 比较加引号 (st-did-05 传播补全)
    g-templates-10  boottest wild p 经 estadd 进表 (collab/18 对齐 attention/
                    substance/locus 18)
    g-templates-14  主线模板 eststo clear 隔离估计命名空间
    g-esttab-csv    主线 5 篇 Tables2-5 esttab .tex 后增 estout CSV side-channel,
                    文件名与 python read_paper_esttab 消费名精确一致, 格式与
                    stata_postprocess.parse_esttab_csv 兼容
    (组级)          benefit 15_table6 esttab `se ci` 互斥 → 拆 SE 主表 + CI 伴表

全部测试为 python 层模板文本断言 + parse_esttab_csv 合成格式契约, 不启动 Stata。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

_PKG_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = _PKG_ROOT / 'papers' / '_common' / 'stata_templates'
FALSIFICATION_TMPL = (
    _PKG_ROOT / 'papers_assets' / 'bank_fintech_tone' / 'do'
    / 'falsification_template.do.tmpl'
)

# g-zscore-papers 组管辖, 本组不动 — 扫描类断言一并跳过, 防越界误锁。
_OTHER_GROUP_DIRS = {'bank_media_disagreement', 'bank_news_clarity'}


def _read(rel: str) -> str:
    p = TEMPLATE_DIR / rel
    assert p.exists(), f"template not found: {p}"
    return p.read_text(encoding='utf-8')


def _all_templates() -> list[Path]:
    out = []
    for p in sorted(TEMPLATE_DIR.rglob('*.do.tmpl')):
        if any(part in _OTHER_GROUP_DIRS for part in p.parts):
            continue
        out.append(p)
    assert out, f"no templates under {TEMPLATE_DIR}"
    return out


def _stata_statements(text: str) -> list[str]:
    """重组 Stata 语句: 去注释行, 合并 /// 续行."""
    stmts: list[str] = []
    buf = ''
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith('*'):
            continue
        if '///' in line:
            buf += line.split('///')[0] + ' '
            continue
        buf += line
        if buf.strip():
            stmts.append(buf.strip())
        buf = ''
    if buf.strip():
        stmts.append(buf.strip())
    return stmts


# ============================================================================
# g-esttab-csv: CSV side-channel — 文件名与 python 消费者精确一致
# ============================================================================

# (模板相对路径, python read_paper_esttab 消费的 csv 文件名)
_CSV_SIDE_CHANNELS = [
    # 主线 (P1 bank_fintech_tone 复现包根模板)
    ('11_table2_main_m1m6.do.tmpl', 'table2_main.csv'),
    ('12_table3_mechanism.do.tmpl', 'table3_mechanism.csv'),
    ('13_table4_heterogeneity.do.tmpl', 'table4_heterogeneity.csv'),
    ('14_table5_advanced_robustness.do.tmpl', 'table5_advanced_robust.csv'),
    # P2 attention — papers/bank_fintech_attention/tables.py:82/90/96/103
    ('bank_fintech_attention/15_attention_main_regression.do.tmpl', 'table2_main.csv'),
    ('bank_fintech_attention/16_attention_mechanism.do.tmpl', 'table3_mechanism.csv'),
    ('bank_fintech_attention/17_attention_heterogeneity.do.tmpl', 'table4_heterogeneity.csv'),
    ('bank_fintech_attention/18_attention_robustness.do.tmpl', 'table5_robustness.csv'),
    # P3 substance — papers/bank_fintech_substance/tables.py:78/86/92/98
    ('bank_fintech_substance/15_substance_main_regression.do.tmpl', 'table2_main.csv'),
    ('bank_fintech_substance/16_substance_mechanism.do.tmpl', 'table3_dual_outcome.csv'),
    ('bank_fintech_substance/17_substance_heterogeneity.do.tmpl', 'table4_heterogeneity.csv'),
    ('bank_fintech_substance/18_substance_robustness.do.tmpl', 'table5_robustness.csv'),
    # P4 locus — papers/bank_fintech_locus/tables.py:81/89/95/101
    ('bank_fintech_locus/15_locus_main_regression.do.tmpl', 'table2_main.csv'),
    ('bank_fintech_locus/16_locus_mechanism.do.tmpl', 'table3_mechanism.csv'),
    ('bank_fintech_locus/17_locus_heterogeneity.do.tmpl', 'table4_heterogeneity.csv'),
    ('bank_fintech_locus/18_locus_robustness.do.tmpl', 'table5_robustness.csv'),
    # P5 collab — papers/bank_fintech_collab/tables.py:75 (仅 Table 2 经 csv 消费)
    ('bank_fintech_collab/15_collab_main_regression.do.tmpl', 'table2_main.csv'),
]


@pytest.mark.parametrize('rel,csv_name', _CSV_SIDE_CHANNELS,
                         ids=[r for r, _ in _CSV_SIDE_CHANNELS])
def test_csv_side_channel_present(rel, csv_name):
    """每张 .tex 表后必有同名 .csv side-channel (estout 写出, 防 esttab csv 的
    ="..." Excel 包裹破坏 parse_esttab_csv 解析)."""
    text = _read(rel)
    csv_stmts = [s for s in _stata_statements(text)
                 if s.startswith('estout') and f'{csv_name}"' in s]
    assert csv_stmts, f"{rel}: 缺 estout → {csv_name} side-channel 行"
    stmt = csv_stmts[0]
    assert 'delimiter(",")' in stmt, f"{rel}: estout csv 必须 delimiter(\",\")"
    assert 'se(par' in stmt, f"{rel}: estout csv 必须 se(par ...) — SE 括号行是 parse_esttab_csv 契约"
    assert 'b(star' in stmt, f"{rel}: estout csv 必须 b(star ...) — 星号显著性是 parse_esttab_csv 契约"


def test_csv_names_match_python_consumers():
    """模板写出的 csv 文件名 ⊇ papers/<id>/tables.py read_paper_esttab 消费名
    (Tables 2-5 链; 防两侧文件名漂移再造死接线)."""
    consumed = {
        'bank_fintech_attention': {'table2_main.csv', 'table3_mechanism.csv',
                                   'table4_heterogeneity.csv', 'table5_robustness.csv'},
        'bank_fintech_substance': {'table2_main.csv', 'table3_dual_outcome.csv',
                                   'table4_heterogeneity.csv', 'table5_robustness.csv'},
        'bank_fintech_locus': {'table2_main.csv', 'table3_mechanism.csv',
                               'table4_heterogeneity.csv', 'table5_robustness.csv'},
        'bank_fintech_collab': {'table2_main.csv'},
    }
    name_re = re.compile(r'read_paper_esttab\(\s*[\'"]?\w*[\'"]?,?\s*[\'"]([\w]+\.csv)[\'"]')
    for paper_id, expected in consumed.items():
        # 1) python 侧消费名快照仍成立 (tables.py 变更时本测试提醒同步模板)
        tables_py = _PKG_ROOT / 'papers' / paper_id / 'tables.py'
        src = tables_py.read_text(encoding='utf-8')
        actual_consumed = set(name_re.findall(src))
        table25 = {n for n in actual_consumed
                   if re.match(r'table[2-5]', n)}
        assert table25 == expected, (
            f"{paper_id}/tables.py Tables2-5 csv 消费名漂移: {table25} != {expected}; "
            f"须同步更新对应 .do.tmpl 的 estout side-channel")
        # 2) 模板侧逐名有 estout 写出
        tmpl_dir = TEMPLATE_DIR / paper_id
        all_text = '\n'.join(p.read_text(encoding='utf-8')
                             for p in sorted(tmpl_dir.glob('*.do.tmpl')))
        for name in expected:
            assert re.search(rf'estout[^\n]*{re.escape(name)}"', all_text), (
                f"{paper_id}: 模板缺 estout → {name}")


def test_estout_csv_format_parsable_by_stata_postprocess(tmp_path):
    """合成 estout delimiter(\",\") cells(b(star) se(par)) stats(N r2) 输出,
    锁 parse_esttab_csv 端到端可解析 (格式契约)."""
    from news_process.papers._common.stata_postprocess import parse_esttab_csv

    csv_text = (
        ',M1,M2\n'
        'tech_frac,0.123*,-0.456***\n'
        ',(0.045),(0.078)\n'
        'digital_frontier,1.5e-03,.\n'
        ',(2.1e-04),\n'
        'N,176,176\n'
        'r2,0.512,0.601\n'
    )
    p = tmp_path / 'table2_main.csv'
    p.write_text(csv_text, encoding='utf-8')
    df = parse_esttab_csv(p)
    assert list(df.columns) == ['M1', 'M2']
    cell = df.loc['tech_frac', 'M1']
    assert cell.value == pytest.approx(0.123)
    assert cell.se == pytest.approx(0.045)
    assert cell.stars == 1
    cell2 = df.loc['tech_frac', 'M2']
    assert cell2.value == pytest.approx(-0.456)
    assert cell2.stars == 3
    # e-notation (omni-g-papers-misc-07 配套)
    assert df.loc['digital_frontier', 'M1'].value == pytest.approx(1.5e-03)
    assert df.loc['N', 'M1'].value == 176


# ============================================================================
# 组级: esttab se 与 ci 互斥
# ============================================================================

def test_no_esttab_combines_se_and_ci():
    """esttab 的 se 与 ci 同抢系数下方括号行, 共存即 r(198) 整表零产出 —
    全仓模板扫描禁止共存."""
    se_re = re.compile(r'\bse\b')
    ci_re = re.compile(r'\bci\b')
    offenders = []
    for p in _all_templates():
        for stmt in _stata_statements(p.read_text(encoding='utf-8')):
            if not stmt.startswith('esttab'):
                continue
            opts = stmt.split(',', 1)[1] if ',' in stmt else ''
            if se_re.search(opts) and ci_re.search(opts):
                offenders.append(f"{p.relative_to(TEMPLATE_DIR)}: {stmt[:90]}...")
    assert not offenders, f"esttab se+ci 共存 (r(198)): {offenders}"


def test_benefit15_table6_split_se_and_ci_tables():
    """benefit 15_table6: SE 主表 + CI 伴表拆分落地."""
    text = _read('benefit_society/15_table6_effect_size.do.tmpl')
    stmts = [s for s in _stata_statements(text) if s.startswith('esttab')]
    se_stmts = [s for s in stmts if 'table6_effect_size.tex' in s]
    ci_stmts = [s for s in stmts if 'table6_effect_size_ci.tex' in s]
    assert len(se_stmts) == 1 and len(ci_stmts) == 1
    assert re.search(r'\bse\b', se_stmts[0].split(',', 1)[1])
    assert not re.search(r'\bci\b', se_stmts[0].split(',', 1)[1])
    assert re.search(r'\bci\(', ci_stmts[0].split(',', 1)[1])
    assert not re.search(r'\bse\b', ci_stmts[0].split(',', 1)[1])


# ============================================================================
# g-templates-03: brokerage 假稳健性列 + overid 虚称
# ============================================================================

def test_brokerage_r3_actually_drops_singletons():
    text = _read('brokerage_network/14_table5_robustness.do.tmpl')
    assert '_bank_grp_n' in text, "R3 须真实剔除 singleton 银行组 (非复读基线)"
    assert re.search(r'if\s+_bank_grp_n\s*>\s*1', text)
    # R3 的 ivreghdfe 与 R2 不再逐 token 相同 (R3 带 if 子样本限制)
    stmts = [s for s in _stata_statements(text) if s.startswith('ivreghdfe')]
    r3 = [s for s in stmts if '_bank_grp_n' in s]
    assert r3, "R3 ivreghdfe 必须引用 _bank_grp_n 子样本"


def test_brokerage_m3_no_overid_claim():
    text = _read('brokerage_network/11_table2_main_iv_2sls.do.tmpl')
    assert 'over-identification check via additional IV' not in text
    assert 'just-identified' in text, "M3 注释须明示恰好识别 (Hansen J 不存在)"


# ============================================================================
# g-templates-04: 守卫模式缺陷族
# ============================================================================

def test_brokerage_r1_single_merged_confirm():
    """连续双 capture confirm (后者覆盖 _rc) → 合并单次多变量 confirm."""
    text = _read('brokerage_network/14_table5_robustness.do.tmpl')
    assert 'capture confirm variable peer_tone_lag1_ctx peer_tone_2nd_lag1_ctx' in text
    # 不再存在两条相邻的单变量 confirm
    assert not re.search(
        r'capture confirm variable peer_tone_lag1_ctx\s*\n\s*capture confirm variable',
        text)


def test_llm_peer_r3_single_merged_confirm():
    text = _read('llm_peer/14_table5_robustness.do.tmpl')
    assert 'capture confirm variable llm_vote_tone_ctx llm_peer_tone_iv_ctx' in text
    assert not re.search(
        r'capture confirm variable llm_vote_tone_ctx\s*\n\s*capture confirm variable',
        text)


def _exec_text(text: str) -> str:
    """仅可执行行 (去注释行 — fix 注释里保留的历史模式不参与断言)."""
    return '\n'.join(ln for ln in text.splitlines()
                     if not ln.strip().startswith('*'))


def test_benefit14_guards_are_real():
    """foreach-continue 空守卫已死; R1-R3 整块 if 包裹 + esttab 动态名单."""
    text = _read('benefit_society/14_table5_robustness.do.tmpl')
    assert 'if _rc continue' not in _exec_text(text), (
        "foreach-continue 守卫是 no-op, 必须移除")
    assert "capture confirm variable `kw_p25'" in text
    assert "capture confirm variable `kw_p75'" in text, "R2 旧版无守卫"
    assert "capture confirm variable `int_p50'" in text, "R3 旧版无守卫"
    assert 'estimates dir' in text, "esttab 名单须动态化 (任一 R 缺失防 r(111))"


def test_strategic_diff_table5c_dynamic():
    text = _read('strategic_diff/14_table5_robustness.do.tmpl')
    # table5c 不再硬点名 N5 R7_ctx
    for stmt in _stata_statements(text):
        if stmt.startswith('esttab') and 'table5c_ctx_track' in stmt:
            assert 'N5 R7_ctx' not in stmt, "table5c esttab 仍硬点名 N5 R7_ctx"
            assert '`c_models' in stmt
            break
    else:
        pytest.fail("table5c esttab 语句未找到")


# ============================================================================
# g-templates-06: 36 字符 outcome 短名化
# ============================================================================

def test_no_executable_reference_to_36char_outcome():
    """car_3day_window_fintech_announcement (36 字符 > Stata 32 硬限) 不得出现在
    任何可执行行 (注释行保留作历史勘误说明)."""
    bad = 'car_3day_window_fintech_announcement'
    offenders = []
    for p in _all_templates():
        for raw in p.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if line.startswith('*'):
                continue
            if bad in line:
                offenders.append(f"{p.relative_to(TEMPLATE_DIR)}: {line[:80]}")
    assert not offenders, f"36 字符旧名仍在可执行行: {offenders}"
    # 短名已在 substance 链落地
    assert len('car_3day_window_ft_announce') <= 32
    text = _read('bank_fintech_substance/16_substance_mechanism.do.tmpl')
    assert 'car_3day_window_ft_announce' in text


# ============================================================================
# g-templates-07: esttab 动态名单 (guard-跳过站点)
# ============================================================================

@pytest.mark.parametrize('rel', [
    '12_table3_mechanism.do.tmpl',
    '13_table4_heterogeneity.do.tmpl',
    '14_table5_advanced_robustness.do.tmpl',
    '21_tableA2_main_spec_switch.do.tmpl',
    '22_tableA3_bartik_iv.do.tmpl',
    'bank_fintech_attention/15_attention_main_regression.do.tmpl',
    'bank_fintech_attention/16_attention_mechanism.do.tmpl',
    'bank_fintech_attention/17_attention_heterogeneity.do.tmpl',
    'bank_fintech_attention/18_attention_robustness.do.tmpl',
    'bank_fintech_attention/19_attention_iv_first_stage.do.tmpl',
    'bank_fintech_substance/15_substance_main_regression.do.tmpl',
    'bank_fintech_substance/16_substance_mechanism.do.tmpl',
    'bank_fintech_substance/17_substance_heterogeneity.do.tmpl',
    'bank_fintech_substance/18_substance_robustness.do.tmpl',
    'bank_fintech_substance/19_substance_lr_reversal.do.tmpl',
    'bank_fintech_substance/20_substance_disclosure_quality.do.tmpl',
    'bank_fintech_locus/15_locus_main_regression.do.tmpl',
    'bank_fintech_locus/16_locus_mechanism.do.tmpl',
    'bank_fintech_locus/17_locus_heterogeneity.do.tmpl',
    'bank_fintech_locus/18_locus_robustness.do.tmpl',
    'bank_fintech_collab/15_collab_main_regression.do.tmpl',
    'bank_fintech_collab/16_collab_mechanism.do.tmpl',
    'bank_fintech_collab/18_collab_robustness.do.tmpl',
    'benefit_society/14_table5_robustness.do.tmpl',
    'brokerage_network/14_table5_robustness.do.tmpl',
    'llm_peer/12_table3_cutoff_sensitivity.do.tmpl',
    'llm_peer/14_table5_robustness.do.tmpl',
    'strategic_diff/12_table3_mechanism.do.tmpl',
    'strategic_diff/14_table5_robustness.do.tmpl',
])
def test_esttab_uses_dynamic_estimate_list(rel):
    """guard-跳过站点的收尾 esttab 必须经 estimates dir 动态拼装 (防 r(111) 丢表)."""
    text = _read(rel)
    assert 'estimates dir' in text, f"{rel}: esttab 名单未动态化"


def test_mainline_eststo_clear_isolation():
    """g-templates-14: 主线模板链共享 session, 每表开头 eststo clear 隔离命名空间
    (防 Table 2 陈旧估计静默泄入后续表)."""
    for rel in ['11_table2_main_m1m6.do.tmpl', '12_table3_mechanism.do.tmpl',
                '13_table4_heterogeneity.do.tmpl',
                '14_table5_advanced_robustness.do.tmpl',
                '21_tableA2_main_spec_switch.do.tmpl',
                '22_tableA3_bartik_iv.do.tmpl',
                '31_figure_coefplot_dual.do.tmpl']:
        assert 'eststo clear' in _read(rel), f"{rel}: 缺 eststo clear"


# ============================================================================
# g-templates-08: collab/17 字符串 HET_VAR 比较
# ============================================================================

def test_collab17_quoted_string_levels():
    text = _read('bank_fintech_collab/17_collab_heterogeneity.do.tmpl')
    assert 'capture confirm string variable {{HET_VAR}}' in text
    assert '== "`lvl\'"' in text, "字符串 HET_VAR (bank_type) 的 level 比较必须加引号"
    # 数值分支保留 (HET_VAR 二态兼容)
    assert re.search(r"==\s*`lvl'\s*,", text), "数值 HET_VAR 分支须保留裸比较"


def test_soe_phantom_column_gone():
    """attention/17 + locus/17 的幻影列 soe → 面板实名 is_soe (st-did-05 传播补全)."""
    for rel in ['bank_fintech_attention/17_attention_heterogeneity.do.tmpl',
                'bank_fintech_locus/17_locus_heterogeneity.do.tmpl']:
        text = _read(rel)
        assert 'confirm variable is_soe' in text, f"{rel}: SOE 切分须用 is_soe"
        assert not re.search(r'confirm variable soe\b', _exec_text(text)), (
            f"{rel}: 幻影列 soe 残留")


# ============================================================================
# g-templates-10: wild bootstrap p 进表
# ============================================================================

@pytest.mark.parametrize('rel', [
    'bank_fintech_attention/18_attention_robustness.do.tmpl',
    'bank_fintech_substance/18_substance_robustness.do.tmpl',
    'bank_fintech_locus/18_locus_robustness.do.tmpl',
    'bank_fintech_collab/18_collab_robustness.do.tmpl',
])
def test_wild_boot_p_injected_into_estimates(rel):
    """boottest 不改写 e(b)/e(V) — wild p 须经 estadd 注入 e(p_wild) 并在 esttab
    stats 行呈现, 否则 'Wild boot' 列名实不符."""
    text = _read(rel)
    assert 'estadd scalar p_wild' in text, f"{rel}: wild p 未注入 eststo"
    assert 'p_wild' in ' '.join(
        s for s in _stata_statements(text) if s.startswith('esttab')), (
        f"{rel}: esttab 未呈现 p_wild stats 行")
    assert 'capture which boottest' in text, f"{rel}: boottest 缺安装守卫"


# ============================================================================
# g-templates-01: falsification 模板 ctx 平行块
# ============================================================================

def test_falsification_ctx_parallel_block():
    assert FALSIFICATION_TMPL.exists(), f"missing: {FALSIFICATION_TMPL}"
    text = FALSIFICATION_TMPL.read_text(encoding='utf-8')
    # 守卫与检验 16-4 同款
    assert text.count('capture confirm variable llm_vote_tone_ctx') >= 2, (
        "检验 1-4 ctx 平行块须有自己的 capture confirm 守卫 (独立于检验 16-4)")
    for est in ['base_ctx', 'ctrl_nf_ctx', 'ctrl_all_ctx']:
        assert f'est store {est}' in text, f"falsification: 缺 ctx 平行估计 {est}"
    # 基准/控制NF/赛马三联的 ctx 方程真实存在 (非仅注释)
    exec_lines = [ln for ln in text.splitlines() if not ln.strip().startswith('*')]
    exec_text = '\n'.join(exec_lines)
    assert exec_text.count('reghdfe Y llm_vote_tone_ctx') >= 3, (
        "ctx 平行块须以 llm_vote_tone_ctx 为解释变量重估基准/控制NF/赛马")
    # 头部双轨披露
    assert 'llm_vote_tone_ctx' in text.split('use "51_panel_with_controls.dta"')[0], (
        "模板头部须披露主指标 ctx 轨的伪造检验要求")


# ============================================================================
# 占位符完整性: 本组改动不引入白名单外 {{TOKEN}}
# ============================================================================

def test_placeholder_integrity_all_templates():
    """全部 .do.tmpl 的 {{TOKEN}} ⊆ stata_runner 白名单 ∪ 所属 paper 默认值键
    (保证 build-replication 替换后零残留 → _substitute fail-fast 不触发)."""
    from news_process.papers._common.derivative_replication import _PAPER_DEFAULTS
    from news_process.papers._common.stata_runner import _KNOWN_PLACEHOLDERS

    ph_re = re.compile(r'\{\{([A-Z_][A-Z0-9_]*)\}\}')
    for p in _all_templates():
        sub = p.parent.name
        legal = set(_KNOWN_PLACEHOLDERS)
        if sub in _PAPER_DEFAULTS:
            # 直读 _PAPER_DEFAULTS (get_paper_defaults 仅收录 7 篇 derivative,
            # 不含 bank_fintech_collab 等 B-route 键)
            legal |= set(_PAPER_DEFAULTS[sub])
        elif sub not in ('stata_templates',):
            # 历史归档 (v3_5_0/v3_5_1) 等沿用主线白名单 + 全部 paper 键并集
            for pid in _PAPER_DEFAULTS:
                legal |= set(_PAPER_DEFAULTS[pid])
        found = set(ph_re.findall(p.read_text(encoding='utf-8')))
        unknown = found - legal
        assert not unknown, (
            f"{p.relative_to(TEMPLATE_DIR)}: 白名单外占位符 {sorted(unknown)} — "
            f"build-replication 将以 unsubstituted residue 失败")
