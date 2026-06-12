"""tests/test_omni_fix_replication.py — omni 审计 g-replication 组修复回归锁.

fix(omni-g-replication-*, 2026-06-11) 行为锁定 (防静默 revert):

- 01: 4 篇原始衍生论文 MAIN_DV='ROA' (+benefit CAR/is_listed) 为外部财务 sentinel —
      保留列名, 但 01_data_prep 给出指向 config/银行面板2007-2025年.xlsx 的明确
      [ERROR]/[WARN], 00_master 对 01 失败 fail-loud 带可读原因 (而非裸 r(198))。
- 02: 主线 01_data_prep IC 回退 core+aux merge 加 keep(master match) + _rc 诊断
      (601 优雅降级 / 其余 fail-loud)。
- 03: paper-10/11 处理变量 merge 拆为逐列 capture merge (keepusing all-or-nothing
      r(111) 不再连坐 fallback 列), 诊断区分 601 (文件) 与 111 (列)。
- 04: P3/P5 treatment 改绑 panel 真实聚合列 (sub_frac / collab_frac; 原 article-level
      innovation_substantiveness_full / innovation_collab_mode_full 不在 bank-year panel)。
- 05: 4 篇 B-route CONTROLS 去 gdp_growth/m2_growth — 15_* M5 "+macro" 真增量,
      不再与 M4 重复 regressor 被 reghdfe 静默 omit。
- 06: collab 开/闭 dummy 对改从 collab_frac/indep_frac 派生 (locus R35-M02 模式):
      !missing 守卫 (missing 不再落 both-0 幻影参照组) + 平局 both-0 显式参照组
      (非缺失时不再 open+closed≡1 完全共线)。
- 07: 11 份 paper_spec.yaml controls 块加 enrichment-pending 披露注记;
      paper-10/11 data_prep 从 bank_type encode 派生 bank_type_id。
- 08: paper-10/11 恒真条件 `"total_assets" != ""` 改为 capture confirm 嵌套守卫。

全部测试为模板文本 / placeholder 默认值 / spec yaml 断言 + 合成 DataFrame 语义镜像;
不依赖盘上大数据, 不调外部 API, 不跑 Stata。

# 白话: "复现包"是给外部研究者一键重跑论文的 Stata 脚本包。这组测试守住:
# 银行财务数据(ROA 等)还没接入时, 脚本要明确报错并告诉用户该补哪个 xlsx,
# 不能含糊地崩; 合并数据失败要区分"文件不在"和"列不在", 一列缺失不连累其他
# 列; 回归里的处理变量必须是面板里真实存在的列; "加宏观控制"那一档要真的是
# 新增变量, 不能和上一档重复导致被 Stata 静默丢掉。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.papers._common.derivative_replication import (  # noqa: E402
    _DERIVATIVE_PAPER_IDS,
    _PAPER_DEFAULTS,
    _substitute,
    build_derivative_replication_package,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # news_process/
TEMPLATES = PROJECT_ROOT / 'papers' / '_common' / 'stata_templates'

LEGACY_4 = ('benefit_society', 'brokerage_network', 'strategic_diff', 'llm_peer')
# 2026-06-13 outcome 重定位: llm_peer (avg_ft_intensity_full, panel 实存列) /
# strategic_diff (tobin_q, 外部 sentinel) 的 MAIN_DV 改与 spec.outcome.primary
# 动态对齐 (锁在 test_derivative_replication.py SPEC_ALIGNED); 'ROA' 哨兵不变式
# 仅余下面 2 篇。
ROA_SENTINEL_2 = ('benefit_society', 'brokerage_network')
B_ROUTE_4 = ('bank_fintech_attention', 'bank_fintech_substance',
             'bank_fintech_locus', 'bank_fintech_collab')
ALL_8 = LEGACY_4 + B_ROUTE_4

XLSX_HINT = '银行面板2007-2025年.xlsx'


def _read(p: Path) -> str:
    return p.read_text(encoding='utf-8')


def _data_prep(paper_id: str) -> str:
    return _read(TEMPLATES / paper_id / '01_data_prep.do.tmpl')


def _master(paper_id: str) -> str:
    return _read(TEMPLATES / paper_id / '00_master.do.tmpl')


def _load_spec(paper_id: str) -> dict:
    p = PROJECT_ROOT / 'papers' / paper_id / 'paper_spec.yaml'
    return yaml.safe_load(p.read_text(encoding='utf-8'))


# ============================================================================
# omni-g-replication-01 — 外部财务 sentinel: 保留名 + 明确指引 + master fail-loud
# ============================================================================


@pytest.mark.parametrize('paper_id', ROA_SENTINEL_2)
def test_legacy_main_dv_roa_sentinel_retained(paper_id):
    """裁决: 财务列无 panel 对应 → 保留 'ROA' sentinel (不静默换列)。

    2026-06-13 起范围收窄至 2 篇 (见 ROA_SENTINEL_2 注); llm_peer/strategic_diff
    的 MAIN_DV-spec 对齐由 test_derivative_replication.py 动态锁定。"""
    assert _PAPER_DEFAULTS[paper_id]['MAIN_DV'] == 'ROA'


@pytest.mark.parametrize('paper_id', ALL_8)
def test_data_prep_financial_guard_points_to_external_source(paper_id):
    """01_data_prep 对缺失 MAIN_DV 的 [ERROR] 必须指向外部数据源 (而非裸 missing)。"""
    content = _data_prep(paper_id)
    assert XLSX_HINT in content, (
        f"{paper_id}: 01_data_prep 缺外部财务数据指引 ({XLSX_HINT})"
    )
    assert '{{MAIN_DV}}' in content
    # MAIN_DV 缺失仍是硬失败 (exit 198), 但带可读指引
    assert 'exit 198' in content


@pytest.mark.parametrize('paper_id', ALL_8)
def test_master_fail_loud_on_data_prep_failure(paper_id):
    """00_master 对 01_data_prep 失败 fail-loud 带可读原因 (capture noisily + [FATAL] + exit rc)。"""
    content = _master(paper_id)
    assert 'capture noisily do 01_data_prep.do' in content, (
        f"{paper_id}: master 未捕获 01_data_prep 失败"
    )
    assert '[FATAL]' in content
    assert re.search(r"exit\s+`_prep_rc'", content), (
        f"{paper_id}: master 须以原 rc fail-loud 退出"
    )
    # 不允许残留裸 `do 01_data_prep.do` (无 capture) 的第二处调用
    bare = re.findall(r'^do 01_data_prep\.do\s*$', content, flags=re.M)
    assert not bare, f"{paper_id}: 残留未守卫的 `do 01_data_prep.do`"


def test_benefit_optional_external_vars_disclosed():
    """benefit: ROBUSTNESS_DV (CAR) / HET_VAR (is_listed) 缺失须显式 [WARN] 披露
    (此前仅靠下游 capture confirm 静默跳过整表)。"""
    content = _data_prep('benefit_society')
    assert '{{ROBUSTNESS_DV}}' in content
    assert '{{HET_VAR}}' in content
    assert '[WARN]' in content


@pytest.mark.parametrize('paper_id', B_ROUTE_4)
def test_b_route_controls_self_validated(paper_id):
    """B-route 4 篇: $controls 以 capture confirm 自校验拼装 (幻影财务控制不再
    直接进 reghdfe 致 r(111))。"""
    content = _data_prep(paper_id)
    assert 'foreach v in {{CONTROLS}}' in content, (
        f"{paper_id}: 01_data_prep 缺 $controls 自校验循环"
    )
    assert '_ctrl_missing' in content
    # 不允许回退到旧式无校验直赋
    assert 'global controls "{{CONTROLS}}"' not in content


# ============================================================================
# omni-g-replication-02 — 主线 01_data_prep IC 回退 merge 完整性
# ============================================================================


def test_mainline_aux_merge_keeps_master_match_and_diagnoses():
    content = _read(TEMPLATES / '01_data_prep.do.tmpl')
    m = re.search(
        r'capture merge 1:1 target_bank year using '
        r'"data/processed/46_panel_yearly_aux\.dta", ([^\n]*)', content)
    assert m, "mainline 01_data_prep: aux merge 行缺失"
    opts = m.group(1)
    assert 'keep(master match)' in opts, (
        "aux merge 缺 keep(master match) — using-only 幻影 bank-year 会被静默追加"
    )
    # _rc 诊断: 601 优雅降级, 其余 fail-loud
    assert '601' in content
    assert re.search(r"exit\s+`_aux_rc'", content), "非 601 的 merge 失败须 fail-loud"


# ============================================================================
# omni-g-replication-03 — paper-10/11 逐列 merge (no all-or-nothing keepusing)
# ============================================================================

_P10 = PROJECT_ROOT / 'papers' / 'bank_media_disagreement' / 'stata_templates' / '01_data_prep.do.tmpl'
_P11 = PROJECT_ROOT / 'papers' / 'bank_news_clarity' / 'stata_templates' / '01_data_prep.do.tmpl'


@pytest.mark.parametrize('tmpl_path', [_P10, _P11], ids=['paper10', 'paper11'])
def test_panel_merge_is_per_column(tmpl_path):
    """40_panel merge 的 keepusing 只允许单 token (循环变量 `v'), 不允许
    多列 all-or-nothing (任一缺失整条 r(111) 连坐 fallback 列)。"""
    content = _read(tmpl_path)
    for m in re.finditer(r'keepusing\(([^)]*)\)', content):
        tokens = m.group(1).split()
        assert len(tokens) == 1, (
            f"{tmpl_path.name}: keepusing 含 {len(tokens)} 列 — all-or-nothing 回归: {tokens}"
        )
    # 逐列循环 + _rc 区分 111 (列缺失)
    assert "keepusing(`v')" in content
    assert '111' in content
    # 文件缺失 (601) 与列缺失分开诊断
    assert 'capture confirm file "data/processed/40_panel_yearly.dta"' in content
    # 旧误导诊断 ("不可读" 把列缺失归因于文件) 不得回归
    assert '40_panel_yearly.dta 不可读' not in content


@pytest.mark.parametrize('tmpl_path', [_P10, _P11], ids=['paper10', 'paper11'])
def test_bank_type_id_derived_from_bank_type(tmpl_path):
    """fix(omni-g-replication-07): spec controls 的 bank_type_id 由主 panel
    字符串列 bank_type encode 派生。"""
    content = _read(tmpl_path)
    assert 'encode bank_type, gen(bank_type_id)' in content


# ============================================================================
# omni-g-replication-04 — P3/P5 treatment 绑 panel 真实聚合列
# ============================================================================


def test_substance_main_treat_is_panel_aggregate():
    assert _PAPER_DEFAULTS['bank_fintech_substance']['MAIN_TREAT'] == 'sub_frac'
    spec = _load_spec('bank_fintech_substance')
    assert spec['treatment']['primary'] == 'sub_frac', (
        "spec.treatment.primary 与 defaults MAIN_TREAT 漂移"
    )


def test_collab_main_treat_is_panel_aggregate():
    assert _PAPER_DEFAULTS['bank_fintech_collab']['MAIN_TREAT'] == 'collab_frac'
    spec = _load_spec('bank_fintech_collab')
    assert spec['treatment']['primary'] == 'collab_frac'


def test_substance_data_prep_requires_panel_aggregates_not_article_level():
    content = _data_prep('bank_fintech_substance')
    assert 'foreach v in sub_frac symb_frac' in content
    assert 'innovation_substantiveness_full' not in content.replace(
        '* 原 foreach 要求 article-level 列 innovation_substantiveness_full', ''), (
        "P3 data prep 不得再把 article-level 列当 required 变量 (注释中的历史说明除外)"
    )


def test_collab_data_prep_requires_panel_aggregates_not_article_level():
    content = _data_prep('bank_fintech_collab')
    assert 'foreach v in collab_frac indep_frac' in content
    # 旧的 article-level mode 派生不得回归
    assert '(innovation_collab_mode_full == 1)' not in content
    assert '(innovation_collab_mode_full == 0)' not in content


@pytest.mark.parametrize('paper_id', sorted(_DERIVATIVE_PAPER_IDS))
def test_build_package_no_residue_after_fixes(paper_id, tmp_path):
    """修复后 build-replication 仍可实例化全部模板且零 {{...}} 残留。"""
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    do_files = sorted((pkg / 'code').glob('*.do'))
    assert do_files
    for f in do_files:
        assert '{{' not in _read(f), f"{paper_id}/{f.name}: placeholder 残留"


def test_collab_templates_substitute_clean():
    """P5 collab 不在 _DERIVATIVE_PAPER_IDS (dormant) — 手工替换验证零残留。"""
    tdir = TEMPLATES / 'bank_fintech_collab'
    for tpl in sorted(tdir.glob('*.do.tmpl')):
        out = _substitute(_read(tpl), _PAPER_DEFAULTS['bank_fintech_collab'])
        assert '{{' not in out, f"collab/{tpl.name}: placeholder 残留"


# ============================================================================
# omni-g-replication-05 — M5 "+macro" 真增量 (CONTROLS 去宏观)
# ============================================================================


@pytest.mark.parametrize('paper_id', B_ROUTE_4)
def test_b_route_controls_exclude_macro(paper_id):
    controls = _PAPER_DEFAULTS[paper_id]['CONTROLS'].split()
    assert 'gdp_growth' not in controls, (
        f"{paper_id}: CONTROLS 复含 gdp_growth → M5 与 M4 重复 regressor 被 reghdfe 静默 omit"
    )
    assert 'm2_growth' not in controls
    assert controls == ['ln_assets', 'leverage', 'capital_ratio',
                        'npl_ratio', 'deposit_growth']


@pytest.mark.parametrize('paper_id, main_tmpl', [
    ('bank_fintech_attention', '15_attention_main_regression.do.tmpl'),
    ('bank_fintech_substance', '15_substance_main_regression.do.tmpl'),
    ('bank_fintech_locus', '15_locus_main_regression.do.tmpl'),
    ('bank_fintech_collab', '15_collab_main_regression.do.tmpl'),
])
def test_m5_macro_truly_incremental(paper_id, main_tmpl):
    """M5 模板显式追加 gdp_growth m2_growth, 且 $controls (来自 CONTROLS 默认值)
    不再含宏观列 → 无重复 regressor。"""
    content = _read(TEMPLATES / paper_id / main_tmpl)
    assert '$controls gdp_growth m2_growth' in content
    instantiated = _substitute(content, _PAPER_DEFAULTS[paper_id])
    # CONTROLS 替换后任何一行不得同时出现两次 gdp_growth (重复 regressor)
    for line in instantiated.splitlines():
        assert line.count('gdp_growth') <= 1, f"{paper_id}: M5 重复 regressor: {line}"


# ============================================================================
# omni-g-replication-06 — collab 开/闭 dummy 对: !missing 守卫 + 平局参照组
# ============================================================================


def test_collab_pair_derivation_has_missing_guard_and_tie_reference():
    content = _data_prep('bank_fintech_collab')
    assert re.search(
        r'gen collab_open_full\s*=\s*\(collab_frac > indep_frac\) '
        r'if !missing\(collab_frac, indep_frac\)', content)
    assert re.search(
        r'gen collab_closed_full\s*=\s*\(indep_frac > collab_frac\) '
        r'if !missing\(collab_frac, indep_frac\)', content)
    # gap ∈ {-1, 0, +1} (平局参照组), 不再是旧二元 {-1, +1}
    assert '{-1, 0, +1}' in content


def test_collab_pair_semantics_mirror():
    """合成 DataFrame 语义镜像 (与 .do gen 逻辑逐式对应):
    (i) fracs 缺失 → 两 dummy 均缺失 (排除出回归, 不再落 both-0 幻影参照组);
    (ii) 平局 → both-0 显式参照组; (iii) 非平局 → 恰一者为 1 (open+closed 不恒等 1,
    含平局样本时与常数项不完全共线)。"""
    df = pd.DataFrame({
        'collab_frac': [0.8, 0.2, 0.5, None, 0.0],
        'indep_frac':  [0.2, 0.8, 0.5, 0.3,  0.0],
    })
    nonmiss = df['collab_frac'].notna() & df['indep_frac'].notna()
    open_d = (df['collab_frac'] > df['indep_frac']).where(nonmiss)
    closed_d = (df['indep_frac'] > df['collab_frac']).where(nonmiss)

    # (i) missing 行: 两 dummy 均缺失
    assert pd.isna(open_d[3]) and pd.isna(closed_d[3])
    # (ii) 平局 (0.5/0.5 与 0/0): both-0 参照组
    for i in (2, 4):
        assert open_d[i] == 0 and closed_d[i] == 0
    # (iii) 非平局: 恰一者为 1
    assert open_d[0] == 1 and closed_d[0] == 0
    assert open_d[1] == 0 and closed_d[1] == 1
    # 估计样本内 open+closed 不恒等于 1 (平局行 = 0) → 不与常数项完全共线
    s = (open_d + closed_d)[nonmiss]
    assert set(s.astype(int)) == {0, 1}


# ============================================================================
# omni-g-replication-07 — spec controls 块 pending 披露
# ============================================================================

ALL_11 = ALL_8 + ('bank_fintech_tone', 'bank_media_disagreement', 'bank_news_clarity')


@pytest.mark.parametrize('paper_id', ALL_11)
def test_spec_controls_block_has_pending_annotation(paper_id):
    raw = (PROJECT_ROOT / 'papers' / paper_id / 'paper_spec.yaml').read_text(encoding='utf-8')
    m = re.search(r'^controls:\n((?:[ \t#].*\n|\n)*)', raw, flags=re.M)
    assert m, f"{paper_id}: controls 块缺失"
    assert 'fix(omni-g-replication-07' in m.group(0), (
        f"{paper_id}: controls 块缺 enrichment-pending 披露注记"
    )
    # 注记不得破坏 yaml 解析, 控制集语义不变 (财务 5 列仍声明)
    spec = _load_spec(paper_id)
    assert 'ln_assets' in spec['controls']['bank_level']


@pytest.mark.parametrize('paper_id, proxy', [
    ('benefit_society', 'ln_news_coverage media_breadth n_articles'),
    ('brokerage_network', 'ln_news_coverage media_hhi bank_scale_ord'),
    ('strategic_diff', 'ln_news_coverage media_hhi bank_scale_ord'),
    ('llm_peer', 'ln_news_coverage media_hhi n_articles'),
])
def test_legacy_spec_discloses_actual_proxy_controls(paper_id, proxy):
    """4 篇衍生 spec 须列明复现包实跑的 coverage 代理控制集 (与
    derivative_replication CONTROLS 一致)。"""
    raw = (PROJECT_ROOT / 'papers' / paper_id / 'paper_spec.yaml').read_text(encoding='utf-8')
    assert proxy.split()[1] in raw  # media_* token 在披露注记中
    assert _PAPER_DEFAULTS[paper_id]['CONTROLS'] == proxy


# ============================================================================
# omni-g-replication-08 — 恒真 `"total_assets" != ""` 守卫修复
# ============================================================================


@pytest.mark.parametrize('tmpl_path', [_P10, _P11], ids=['paper10', 'paper11'])
def test_total_assets_tautology_removed(tmpl_path):
    content = _read(tmpl_path)
    # 只检查可执行行 (排除 `*` 注释 — 修复说明注释里引用了旧写法原文)
    code_lines = [ln for ln in content.splitlines() if not ln.lstrip().startswith('*')]
    code = '\n'.join(code_lines)
    assert '"total_assets" != ""' not in code, (
        f"{tmpl_path.name}: 恒真字符串字面量比较回归 (无守卫 gen ln(total_assets) → r(111))"
    )
    assert 'capture confirm variable total_assets' in content
    # gen 仍在 (数据接入后正常派生)
    assert 'gen ln_assets = ln(total_assets) if total_assets > 0' in content
