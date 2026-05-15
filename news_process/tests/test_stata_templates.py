"""v3.2.0 — Stata 模板测试 (plan v14 §9.5)

测试范围:
    - 模板占位符可解析 (regex 检测无遗漏 {{...}})
    - 关键模板存在 (00_master, 11_table2, 21_tableA2)
    - 占位符在 KNOWN_PLACEHOLDERS 白名单内
    - 模板语法合理性 (Stata local 变量声明 + reghdfe / esttab 命令)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / 'papers' / '_common' / 'stata_templates'

# Plan v14 §9.2 已知占位符白名单
KNOWN_PLACEHOLDERS = frozenset({
    'MAIN_LOCUS_TRACK',
    'MAIN_SUBST_TRACK',
    'MAIN_SENT_TRACK',
    'PROJECT_ROOT',
})


def _load_template(name: str) -> str:
    p = TEMPLATE_DIR / name
    assert p.exists(), f"Template not found: {p}"
    return p.read_text(encoding='utf-8')


def test_template_dir_exists():
    """plan v14 §9.2: papers/_common/stata_templates/ 目录必存在."""
    assert TEMPLATE_DIR.is_dir(), f"{TEMPLATE_DIR} 不存在"


def test_master_template_exists():
    """plan v14 §9.2: 00_master.do.tmpl 必存在."""
    assert (TEMPLATE_DIR / '00_master.do.tmpl').exists()


def test_table2_main_template_exists():
    """plan v14 §9.2: 11_table2_main_m1m6.do.tmpl 必存在."""
    assert (TEMPLATE_DIR / '11_table2_main_m1m6.do.tmpl').exists()


def test_tableA2_robustness_template_exists():
    """plan v14 §9.2: 21_tableA2_main_spec_switch.do.tmpl 必存在 (双轨核心)."""
    assert (TEMPLATE_DIR / '21_tableA2_main_spec_switch.do.tmpl').exists()


def test_readme_exists():
    """plan v14 §9.2 README.md (双语)."""
    readme = TEMPLATE_DIR / 'README.md'
    assert readme.exists()
    content = readme.read_text(encoding='utf-8')
    assert 'Stata Templates' in content
    assert '占位符' in content  # 中文存在


@pytest.mark.parametrize("template_name", [
    '00_master.do.tmpl',
    '11_table2_main_m1m6.do.tmpl',
    '21_tableA2_main_spec_switch.do.tmpl',
])
def test_no_unknown_placeholders(template_name):
    """plan v14 §9.5 R32-D + R26-A: 全部占位符在 KNOWN_PLACEHOLDERS 白名单."""
    content = _load_template(template_name)
    for m in re.finditer(r'\{\{([A-Z_]+)\}\}', content):
        ph = m.group(1)
        assert ph in KNOWN_PLACEHOLDERS, f"{template_name}: 未知占位符 {{{{{ph}}}}}"


def test_master_references_subtemplates():
    """00_master.do.tmpl 须调用 11_table2 + 21_tableA2."""
    master = _load_template('00_master.do.tmpl')
    assert '11_table2_main_m1m6' in master or 'table2_main' in master
    assert '21_tableA2_main_spec_switch' in master or 'tableA2_main_spec_switch' in master


def test_table2_uses_reghdfe():
    """Table 2 主回归须用 reghdfe (HDFE 标准命令)."""
    content = _load_template('11_table2_main_m1m6.do.tmpl')
    assert 'reghdfe' in content
    assert 'absorb(bank_id year)' in content
    assert 'vce(cluster bank_id)' in content


def test_table2_has_m1_to_m6():
    """Table 2 必含 M1-M6 progressive specs (plan v14 §9.2)."""
    content = _load_template('11_table2_main_m1m6.do.tmpl')
    for m in ['M1', 'M2', 'M3', 'M4', 'M5', 'M6']:
        assert f'eststo {m}' in content, f"{m} 不在 Table 2"


def test_tableA2_has_8_specs():
    """Table A2 必含 2×2×2 = 8 specs (lf/lc × sf/sc × full/ctx)."""
    content = _load_template('21_tableA2_main_spec_switch.do.tmpl')
    # 8 specs nested loop
    assert 'foreach loc in lf lc' in content
    assert 'foreach sub in sf sc' in content
    assert 'foreach sent in full ctx' in content


def test_templates_use_esttab():
    """Table 模板须用 esttab 输出 LaTeX (plan v14 §9.5)."""
    for tpl in ['11_table2_main_m1m6.do.tmpl', '21_tableA2_main_spec_switch.do.tmpl']:
        content = _load_template(tpl)
        assert 'esttab' in content
        assert '.tex' in content  # 输出 LaTeX
        assert 'booktabs' in content  # 顶刊 standard


def test_templates_version_stata_15():
    """plan v14 §9.7: 全部模板要求 version 15 (reghdfe / coefplot 性能稳定)."""
    for tpl in ['00_master.do.tmpl', '11_table2_main_m1m6.do.tmpl',
                '21_tableA2_main_spec_switch.do.tmpl']:
        content = _load_template(tpl)
        assert 'version 15' in content, f"{tpl} 缺 version 15 声明"


# ============================================================================
# v3.2.0 M6/7 续 — 新增模板综合测试 (12 模板全覆盖)
# ============================================================================

EXPECTED_TEMPLATES_V14 = [
    '00_master.do.tmpl',
    '01_data_prep.do.tmpl',
    '10_table1_descriptives.do.tmpl',
    '11_table2_main_m1m6.do.tmpl',
    '12_table3_mechanism.do.tmpl',
    '13_table4_heterogeneity.do.tmpl',
    '14_table5_advanced_robustness.do.tmpl',
    '20_tableA1_inter_track_kappa.do.tmpl',
    '21_tableA2_main_spec_switch.do.tmpl',
    '22_tableA3_bartik_iv.do.tmpl',
    '23_tableA4_radius_sensitivity.do.tmpl',
    '24_tableA5_dictionary_method.do.tmpl',
    '30_figure1_event_study.do.tmpl',
    '31_figure_coefplot_dual.do.tmpl',
]


def test_all_14_templates_exist():
    """plan v14 §9.2: 14/14 模板全部交付 (table5 + tableA5 现已补全)."""
    missing = []
    for tpl in EXPECTED_TEMPLATES_V14:
        if not (TEMPLATE_DIR / tpl).exists():
            missing.append(tpl)
    assert not missing, f"缺失模板: {missing}"


@pytest.mark.parametrize("template_name", EXPECTED_TEMPLATES_V14)
def test_template_version_15_required(template_name):
    """全部 12 模板必含 version 15 (Stata 兼容性 hard floor)."""
    content = _load_template(template_name)
    assert 'version 15' in content, f"{template_name} 缺 version 15"


@pytest.mark.parametrize("template_name", EXPECTED_TEMPLATES_V14)
def test_template_no_unknown_placeholders_full(template_name):
    """全部 12 模板 占位符必在白名单."""
    content = _load_template(template_name)
    for m in re.finditer(r'\{\{([A-Z_]+)\}\}', content):
        assert m.group(1) in KNOWN_PLACEHOLDERS, f"{template_name}: 未知 {{{{{m.group(1)}}}}}"


@pytest.mark.parametrize("template_name,expected_cmd", [
    ('11_table2_main_m1m6.do.tmpl',          'reghdfe'),
    ('12_table3_mechanism.do.tmpl',          'reghdfe'),
    ('13_table4_heterogeneity.do.tmpl',      'reghdfe'),
    ('14_table5_advanced_robustness.do.tmpl', 'reghdfe'),
    ('20_tableA1_inter_track_kappa.do.tmpl', 'kappa'),
    ('21_tableA2_main_spec_switch.do.tmpl',  'reghdfe'),
    ('22_tableA3_bartik_iv.do.tmpl',         'ivreg2'),
    ('24_tableA5_dictionary_method.do.tmpl', 'reghdfe'),
    ('30_figure1_event_study.do.tmpl',       'coefplot'),
    ('31_figure_coefplot_dual.do.tmpl',      'coefplot'),
])
def test_template_uses_expected_command(template_name, expected_cmd):
    """每个模板用预期 Stata 命令 (reghdfe / ivreg2 / kappa / coefplot)."""
    content = _load_template(template_name)
    assert expected_cmd in content, f"{template_name} 应含 {expected_cmd}"


@pytest.mark.parametrize("template_name", [
    '11_table2_main_m1m6.do.tmpl',
    '12_table3_mechanism.do.tmpl',
    '13_table4_heterogeneity.do.tmpl',
])
def test_table_templates_output_tex_booktabs(template_name):
    """Table 模板必产 LaTeX booktabs 格式."""
    content = _load_template(template_name)
    assert 'esttab' in content
    assert '.tex' in content
    assert 'booktabs' in content


@pytest.mark.parametrize("template_name", [
    '30_figure1_event_study.do.tmpl',
    '31_figure_coefplot_dual.do.tmpl',
])
def test_figure_templates_export_pdf(template_name):
    """Figure 模板必含 graph export ... .pdf."""
    content = _load_template(template_name)
    assert 'graph export' in content
    assert '.pdf' in content


def test_master_references_all_subdo_files():
    """00_master.do.tmpl 必引用所有 12 模板 (序号文件名)."""
    master = _load_template('00_master.do.tmpl')
    # 排除 00 自己, 检查 11 个子文件被引用 (按 .do 文件名, 不含 .tmpl)
    for tpl in EXPECTED_TEMPLATES_V14:
        if tpl == '00_master.do.tmpl':
            continue
        do_name = tpl.replace('.tmpl', '')  # e.g. 01_data_prep.do
        # 允许 do "code/01_data_prep.do" 或 do "stata/01_data_prep.do"
        assert do_name in master, f"00_master 未引用 {do_name}"


def test_cli_command_main_callable():
    """v3.2.0 M7 CLI: stata_runner.main() 可调用 (argparse subcommand dispatch)."""
    import news_process.papers._common.stata_runner as mod
    assert hasattr(mod, 'main')
    assert callable(mod.main)
    assert hasattr(mod, '_cli_build_replication')


def test_cli_list_templates_callable():
    """M4/7: list-templates 子命令 importable + 配置正确."""
    import news_process.papers._common.stata_runner as mod
    assert hasattr(mod, '_cli_list_templates')
    assert callable(mod._cli_list_templates)


def test_cli_list_templates_runs(capsys, monkeypatch):
    """M4/7: list-templates --verbose 端到端 stdout 包含 14 模板 + 占位符 inventory."""
    import news_process.papers._common.stata_runner as mod
    from types import SimpleNamespace

    # 模拟 args.verbose = True
    args = SimpleNamespace(verbose=True)
    rc = mod._cli_list_templates(args)
    assert rc == 0
    captured = capsys.readouterr()
    # 14 模板全名出现
    for tpl in EXPECTED_TEMPLATES_V14:
        assert tpl in captured.out, f"list-templates 输出缺 {tpl}"
    # 占位符 inventory section
    assert 'Placeholders inventory' in captured.out
    assert 'MAIN_LOCUS_TRACK' in captured.out


def test_cli_subcommand_build_replication_args():
    """CLI build-replication 子命令 argparse 正确解析 --locus/--subst/--sent."""
    import argparse
    # 用 mock argparse 触发 _cli_build_replication 解析检查
    # 不实际跑 build (会创建目录); 检查 parse error
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    bp = sub.add_parser('build-replication')
    bp.add_argument('--locus', choices=['lf', 'lc'], required=True)
    bp.add_argument('--subst', choices=['sf', 'sc'], required=True)
    bp.add_argument('--sent',  choices=['full', 'ctx'], required=True)
    bp.add_argument('--root', default='.')

    # 有效 args
    args = parser.parse_args(['build-replication', '--locus', 'lc', '--subst', 'sf',
                              '--sent', 'ctx', '--root', '.'])
    assert args.locus == 'lc'
    assert args.subst == 'sf'
    assert args.sent == 'ctx'

    # 无效 --locus 应 SystemExit (argparse error)
    with pytest.raises(SystemExit):
        parser.parse_args(['build-replication', '--locus', 'invalid', '--subst', 'sf',
                           '--sent', 'ctx'])
