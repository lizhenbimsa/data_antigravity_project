"""v3.2.0 Stata replication 包跨 8-spec 集成测试 (plan v14 §5.3 + §9.3).

测试范围:
    - 8-spec matrix (2 locus × 2 subst × 2 sent) build_replication_package 全部成功
    - 18 .do 文件正确实例化 (占位符 0 残留, 主要 locals 正确替换)
    - 复现包目录结构一致 (code/ data/ output/{tables,figures}/)
    - README.md 含 spec 信息 + git commit hash
    - 多 spec 并存目录命名 R54-A: replication_v3.2.0_{locus}_{subst}_{sent}/
"""
from __future__ import annotations

import sys
from itertools import product
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[3]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


# 8 spec 笛卡尔积 (plan v14 §5.3 main spec switch)
ALL_SPECS = list(product(['lf', 'lc'], ['sf', 'sc'], ['full', 'ctx']))


@pytest.mark.parametrize("locus,subst,sent", ALL_SPECS)
def test_build_replication_8spec_matrix(tmp_path, locus, subst, sent):
    """plan v14 §9.3 + R54-A: 8 个 spec 全部 build 成功 + 目录名唯一."""
    from news_process.papers._common.stata_runner import build_replication_package
    pkg = build_replication_package({
        'MAIN_LOCUS_TRACK': locus,
        'MAIN_SUBST_TRACK': subst,
        'MAIN_SENT_TRACK': sent,
        'PROJECT_ROOT': str(tmp_path),
    }, output_root=tmp_path)
    # 目录命名规则 (R54-A)
    assert pkg.name == f'replication_v3.2.0_{locus}_{subst}_{sent}'
    # 必备子目录
    for sub in ['code', 'data', 'output/tables', 'output/figures']:
        assert (pkg / sub).exists(), f"spec {locus}_{subst}_{sent}: 缺 {sub}/"
    # 19 个 .do 文件全部实例化 (remove-title-track 后 14; 2026-06-13 IV 补全
    # +25_tableA6_tone_iv_2sls → 15; agg-toptier-audit +26_tableA7_aggregation_robustness → 16;
    # 2026-06-14 顶刊稳健性扩充 +32_tableA8_fe_saturation_robust_est +33_tableA9_subsample_timing → 18;
    # 2026-06-14 T18 重审 +34_tableA11_era_stability → 19
    # 2026-07-02 互为稳健性 option B +27_tableA12_cross_model_fwer (根级 rwolf) → 20
    # 2026-07-03 稳健性缺口补齐 §6 +28_tableA13_policy_family_robustness → 21)
    do_files = list((pkg / 'code').glob('*.do'))
    assert len(do_files) == 21, f"spec {locus}_{subst}_{sent}: 应 21 .do, 实际 {len(do_files)}"
    # README.md 含 spec 信息
    readme = (pkg / 'README.md').read_text(encoding='utf-8')
    assert locus in readme
    assert subst in readme
    assert sent in readme


@pytest.mark.parametrize("locus,subst,sent", ALL_SPECS)
def test_table2_locals_match_spec(tmp_path, locus, subst, sent):
    """每 spec 下 11_table2 的 LOCUS/SUBST/DV locals 与 spec 严格一致."""
    import re

    from news_process.papers._common.stata_runner import build_replication_package
    pkg = build_replication_package({
        'MAIN_LOCUS_TRACK': locus, 'MAIN_SUBST_TRACK': subst,
        'MAIN_SENT_TRACK': sent, 'PROJECT_ROOT': str(tmp_path),
    }, output_root=tmp_path)
    t2 = (pkg / 'code' / '11_table2_main_m1m6.do').read_text(encoding='utf-8')
    assert re.search(rf'local\s+DV\s+llm_vote_tone_{sent}', t2), f"spec {locus}_{subst}_{sent}: DV 错"
    assert re.search(rf'local\s+LOCUS\s+tech_frac_{locus}', t2), f"spec {locus}_{subst}_{sent}: LOCUS 错"
    assert re.search(rf'local\s+SUBST\s+symb_frac_{subst}', t2), f"spec {locus}_{subst}_{sent}: SUBST 错"


@pytest.mark.parametrize("locus,subst,sent", ALL_SPECS)
def test_no_placeholder_residue_across_specs(tmp_path, locus, subst, sent):
    """plan v14 §9.5: 20 .do 文件占位符零残留 (跨 8 specs)."""
    from news_process.papers._common.stata_runner import build_replication_package
    pkg = build_replication_package({
        'MAIN_LOCUS_TRACK': locus, 'MAIN_SUBST_TRACK': subst,
        'MAIN_SENT_TRACK': sent, 'PROJECT_ROOT': str(tmp_path),
    }, output_root=tmp_path)
    issues = []
    for do_file in (pkg / 'code').glob('*.do'):
        content = do_file.read_text(encoding='utf-8')
        if '{{' in content or '}}' in content:
            issues.append(do_file.name)
    assert not issues, f"spec {locus}_{subst}_{sent}: 占位符残留 in {issues}"


def test_master_do_references_all_17_subdo(tmp_path):
    """plan v14 §9.2: 00_master.do.tmpl 引用全部 20 子模板 (除 master 自己;
    2026-06-13 IV +25_tableA6 / agg +26_tableA7; 2026-06-14 顶刊稳健性扩充 +32_tableA8 +33_tableA9;
    2026-06-14 T18 重审 +34_tableA11_era_stability; 2026-07-02 互为稳健性 +27_tableA12_cross_model_fwer; 2026-07-03 稳健性缺口补齐 +28_tableA13_policy_family_robustness)."""
    from news_process.papers._common.stata_runner import build_replication_package
    pkg = build_replication_package({
        'MAIN_LOCUS_TRACK': 'lc', 'MAIN_SUBST_TRACK': 'sf',
        'MAIN_SENT_TRACK': 'ctx', 'PROJECT_ROOT': str(tmp_path),
    }, output_root=tmp_path)
    master = (pkg / 'code' / '00_master.do').read_text(encoding='utf-8')
    expected_subdo = [
        '01_data_prep.do', '10_table1_descriptives.do',
        '11_table2_main_m1m6.do', '12_table3_mechanism.do',
        '13_table4_heterogeneity.do', '14_table5_advanced_robustness.do',
        '20_tableA1_inter_track_kappa.do', '21_tableA2_main_spec_switch.do',
        '22_tableA3_bartik_iv.do', '23_tableA4_radius_sensitivity.do',
        '24_tableA5_dictionary_method.do', '25_tableA6_tone_iv_2sls.do',
        '26_tableA7_aggregation_robustness.do',
        '27_tableA12_cross_model_fwer.do',
        '28_tableA13_policy_family_robustness.do',
        '32_tableA8_fe_saturation_robust_est.do', '33_tableA9_subsample_timing.do',
        '34_tableA11_era_stability.do',
        '30_figure1_event_study.do', '31_figure_coefplot_dual.do',
    ]
    for sub_name in expected_subdo:
        assert sub_name in master, f"master.do 未引用 {sub_name}"
