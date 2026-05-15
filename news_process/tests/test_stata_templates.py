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
