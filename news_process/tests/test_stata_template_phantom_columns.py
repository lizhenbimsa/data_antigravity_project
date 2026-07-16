"""F8/M2/M3 (2026-07-16) gate: Stata 模板幻影列名 correctness-04 重映射。

- F8: 01_data_prep 直拼 tech_frac_{{MAIN_LOCUS_TRACK}}/symb_frac_{{MAIN_SUBST_TRACK}}
  在 lf/sf 主规格下展开为面板不存在的幻影列, `foreach … of varlist` 启动期整表
  校验 → r(111), 行内 capture confirm 死代码, master 裸 do → 整条复现链死。
- M2: 20_tableA1 引陈旧列名 indep_frac_cs (实名 indep_frac_cm_ss), confirm 静默置 .。
- M3: 10_table1 引文章级列名 (无 avg_ 前缀) + 4 个 locus/subst 幻影, 被"过滤实际
  存在的列"循环静默跳过 → Table 1 主规格漏报。

断言纪律 (R1/R2 评审教训): 禁子串否定断言 (correctness-04 范式的 else 死分支在
lf/sf 实例下必然含幻影字面量) — 一律行级 regex 结构断言, 容忍多空格对齐风格。
计划: scripts/audit/FATAL_DEFECT_REMEDIATION_EXECUTION_PLAN_2026-07-16.md §2-F8/M2/M3。
"""
import re
from pathlib import Path

TMPL_DIR = (Path(__file__).resolve().parents[1] / 'papers' / '_common'
            / 'stata_templates')


def _read(name: str) -> str:
    return (TMPL_DIR / name).read_text(encoding='utf-8')


def _instantiate(text: str, locus='lf', subst='sf', sent='full') -> str:
    return (text.replace('{{MAIN_LOCUS_TRACK}}', locus)
                .replace('{{MAIN_SUBST_TRACK}}', subst)
                .replace('{{MAIN_SENT_TRACK}}', sent))


class TestF8DataPrep:
    def test_source_no_unconditional_splice(self):
        """无条件直拼行已消失 (被 if/else 包裹; 前提=else 分支内容缩进)。"""
        t = _read('01_data_prep.do.tmpl')
        assert not re.search(
            r'^local main_locus\s+tech_frac_\{\{MAIN_LOCUS_TRACK\}\}', t, re.M)
        assert not re.search(
            r'^local main_subst\s+symb_frac_\{\{MAIN_SUBST_TRACK\}\}', t, re.M)
        # else 分支 (缩进) 保留带后缀直拼 — 镜像 11_table2 范式
        assert re.search(
            r'^\s+local main_locus tech_frac_\{\{MAIN_LOCUS_TRACK\}\}', t, re.M)

    def test_instance_lf_sf_maps_to_bare(self):
        out = _instantiate(_read('01_data_prep.do.tmpl'))
        assert re.search(r'^\s*local main_locus\s+tech_frac\s*$', out, re.M)
        assert re.search(r'^\s*local main_subst\s+symb_frac\s*$', out, re.M)
        assert 'if "lf" == "lf"' in out and 'if "sf" == "sf"' in out

    def test_instance_lc_sc_keeps_suffixed(self):
        out = _instantiate(_read('01_data_prep.do.tmpl'), locus='lc', subst='sc')
        assert re.search(r'^\s*local main_locus\s+tech_frac_lc\s*$', out, re.M)
        assert re.search(r'^\s*local main_subst\s+symb_frac_sc\s*$', out, re.M)

    def test_winsor_loop_uses_in_not_varlist(self):
        """`in` 列表不做启动期校验 → 行内 capture confirm 守卫变活。"""
        t = _read('01_data_prep.do.tmpl')
        assert re.search(r"foreach var in `main_dv' `main_locus' `main_subst'", t)
        assert "foreach var of varlist `main_dv'" not in t


class TestM2TableA1:
    def test_no_stale_indep_frac_cs(self):
        t = _read('20_tableA1_inter_track_kappa.do.tmpl')
        assert not re.search(r'indep_frac_cs\b', t), '陈旧幻影名须全文 0 命中 (含注释)'
        assert 'indep_frac_cm_ss' in t


class TestM3Table1:
    def test_prob_score_uses_panel_name(self):
        t = _read('10_table1_descriptives.do.tmpl')
        assert not re.search(r'(?<!avg_)llm_prob_score_', t), \
            '文章级裸名 (无 avg_ 前缀) 不得残留'
        assert 'avg_llm_prob_score_{{MAIN_SENT_TRACK}}' in t

    def test_locus_subst_remap_lf_sf(self):
        out = _instantiate(_read('10_table1_descriptives.do.tmpl'))
        assert re.search(r'^\s*local locus_vars\s+tech_frac app_frac\s*$', out, re.M)
        assert re.search(r'^\s*local subst_vars\s+sub_frac symb_frac\s*$', out, re.M)

    def test_locus_subst_remap_lc_sc(self):
        out = _instantiate(_read('10_table1_descriptives.do.tmpl'),
                           locus='lc', subst='sc')
        assert 'tech_frac_lc app_frac_lc' in out
        assert 'sub_frac_sc symb_frac_sc' in out


class TestPlaceholderInventoryUnchanged:
    """F8/M2/M3 不引入新占位符 (list-templates inventory 与 test_papers_b_route 零扰动)。"""

    def test_only_known_placeholders(self):
        pat = re.compile(r'\{\{([A-Z0-9_]+)\}\}')
        for name in ('01_data_prep.do.tmpl', '10_table1_descriptives.do.tmpl',
                     '20_tableA1_inter_track_kappa.do.tmpl'):
            found = set(pat.findall(_read(name)))
            assert found <= {'MAIN_LOCUS_TRACK', 'MAIN_SUBST_TRACK',
                             'MAIN_SENT_TRACK'}, f'{name}: 意外占位符 {found}'
