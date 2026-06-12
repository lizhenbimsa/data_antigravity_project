"""tests/test_omni_fix_gapfill.py — omni 审计孤儿项清尾回归锁 (2026-06-12).

g-benefit 组按文件白名单申报域外、g-templates 组只修自己任务清单内模板后的
9 条孤儿项 (g-benefit-08/10/11/12/14/15/16/17; -13 已由 g-templates-misc 拆表
修复) + 1 条跨组接缝 (gapfill-18):

  gapfill-08  benefit_society 模板补 esttab CSV side-channel (estout 约定,
              文件名与 papers/benefit_society/tables.py read_paper_esttab
              消费名精确一致; 20_tableA1 为 file-write 手工 CSV)
  gapfill-10  merge_dimensions_to_panel 真实现 (dimension_analysis.py; 此前
              18_table9 模板引用的是全仓不存在的幻影函数) + 主面板写保护
  gapfill-11  plot_placebo_comparison Coefficient namedtuple float() TypeError
              修复 (_to_value_se + footer stats 行排除 + 比率标注)
  gapfill-12  NCD prompt 亿元/billion 10× 单位冲突 — prompt 冻结不动, 解析侧
              启发式探测 (validate_record SUSPECTED 10x + unit_suspect_fields
              旁路列 + triangulate unit_mismatch_* 商≈10 旗标)
  gapfill-14  18_table9 esttab 名单动态化 (estimates dir; 旧硬点名 r(111) 被
              master capture 吞掉) + master capture noisily 回显 _rc
  gapfill-15  00_master 补 5 个 spec 承诺却从不执行的 .do (11b/19/22/23/24)
  gapfill-16  WCB 推断真正进表: 21_tableA2 六规格逐一 boottest + estadd p_wild
              + stats 行; 31_figure2 图注去 WCB 名实不符; 11b p_cluster 改
              t(e(df_r)) 口径
  gapfill-17  19_bs: 双轨拆单轨回归 (不同进一 RHS) + 单维 cluster(bank_id) +
              DV {{MAIN_DV}}_w + ctx 守卫 + esttab 动态化
  gapfill-18  validation/prompt_sensitivity locus 聚合直接 import 生产
              tone_llms._resolve_locus_track (baseline↔variant 规则永久同源;
              取代 g-val-prompt-04 手工内联的旧生产行为)

全部为模板文本断言 + 合成 DataFrame, 不启动 Stata、不调 API、不触盘上大数据。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pandas as pd
import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

_PKG_ROOT = Path(__file__).resolve().parents[1]
BENEFIT_TMPL_DIR = _PKG_ROOT / 'papers' / '_common' / 'stata_templates' / 'benefit_society'

pytestmark = pytest.mark.fast


def _read(name: str) -> str:
    p = BENEFIT_TMPL_DIR / name
    assert p.exists(), f"template not found: {p}"
    return p.read_text(encoding='utf-8')


def _stata_statements(text: str) -> list[str]:
    """重组 Stata 语句: 去注释行, 合并 /// 续行 (同 test_omni_fix_templates 约定)."""
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
# gapfill-08: benefit_society esttab CSV side-channel
# ============================================================================

_BENEFIT_CSV_SIDE_CHANNELS = [
    ('11_table2_main.do.tmpl', 'table2_main.csv'),
    ('12_table3_mechanism.do.tmpl', 'table3_mechanism.csv'),
    ('13_table4_heterogeneity.do.tmpl', 'table4_heterogeneity.csv'),
    ('14_table5_robustness.do.tmpl', 'table5_robustness.csv'),
    ('17b_table8b_shrinkage_dual.do.tmpl', 'table8b_shrinkage_dual.csv'),
    ('21_tableA2_attitude_track_switch.do.tmpl', 'tableA2_attitude_track_switch.csv'),
    ('22_tableA9_external_validation.do.tmpl', 'tableA9_external_validation.csv'),
    ('23_tableA10_placebo_business_lines.do.tmpl', 'tableA10_placebo_business_lines.csv'),
    ('24_tableA11_anchor_family_alternative.do.tmpl',
     'tableA11_anchor_family_alternative.csv'),
]


@pytest.mark.parametrize('rel,csv_name', _BENEFIT_CSV_SIDE_CHANNELS,
                         ids=[r for r, _ in _BENEFIT_CSV_SIDE_CHANNELS])
def test_benefit_csv_side_channel_present(rel, csv_name):
    """每张 esttab .tex 表后必有同名 estout .csv side-channel (g-esttab-csv 约定
    补齐 benefit 子目录; parse_esttab_csv 契约: delimiter + b(star + se(par)."""
    text = _read(rel)
    csv_stmts = [s for s in _stata_statements(text)
                 if s.startswith('estout') and f'{csv_name}"' in s]
    assert csv_stmts, f"{rel}: 缺 estout → {csv_name} side-channel 行"
    stmt = csv_stmts[0]
    assert 'delimiter(",")' in stmt, f"{rel}: estout csv 必须 delimiter(\",\")"
    assert 'se(par' in stmt, f"{rel}: estout csv 必须 se(par ...)"
    assert 'b(star' in stmt, f"{rel}: estout csv 必须 b(star ...)"


def test_benefit_tableA1_filewrite_csv_side_channel():
    """20_tableA1 是 file-write 手工 .tex (非 esttab, parse_esttab_tex 不可解析)
    → 须有 file-write CSV side-channel (header + 数据行, parse_esttab_csv 兼容)."""
    text = _read('20_tableA1_inter_track_kappa.do.tmpl')
    assert 'tableA1_inter_track_kappa.csv' in text
    stmts = _stata_statements(text)
    assert any(s.startswith('file open') and 'tableA1_inter_track_kappa.csv' in s
               for s in stmts), "缺 file open → tableA1 csv"
    # header 行: 首列变量名 + 模型标签 (parse_esttab_csv 首非空行约定)
    assert any('field,' in s for s in stmts), "缺 CSV header 行"


def test_benefit_csv_names_match_python_consumers():
    """papers/benefit_society/tables.py 全部 read_paper_esttab 消费名 ⊆ 模板侧
    CSV 产出名 (防两侧文件名漂移再造死接线)."""
    tables_py = _PKG_ROOT / 'papers' / 'benefit_society' / 'tables.py'
    src = tables_py.read_text(encoding='utf-8')
    consumed = set(re.findall(
        r"read_paper_esttab\(\s*'benefit_society',\s*'([\w]+\.csv)'", src))
    assert consumed, "benefit tables.py 应有 read_paper_esttab 消费名"

    all_text = '\n'.join(p.read_text(encoding='utf-8')
                         for p in sorted(BENEFIT_TMPL_DIR.glob('*.do.tmpl')))
    produced = set(re.findall(r'using "\$tables_dir/([\w]+\.csv)"', all_text))
    missing = consumed - produced
    assert not missing, f"benefit 模板缺 CSV 产出: {missing}"


# ============================================================================
# gapfill-10: merge_dimensions_to_panel 真实现
# ============================================================================

def _synth_dimension_frames():
    panel = pd.DataFrame({
        'target_bank': ['工商银行', '建设银行', '招商银行'],
        'year': [2017, 2017, 2018],
        'roa': [0.9, 1.1, 1.0],
    })
    dims = pd.DataFrame({
        'target_bank': ['工商银行', '建设银行'],
        'year': [2017, 2017],
        **{f'benefit_{d}_{t}': [0.1, -0.2]
           for t in ('full', 'ctx')
           for d in ('core_op', 'growth', 'resource', 'compliance')},
    })
    return panel, dims


class TestMergeDimensionsToPanel:
    def test_function_exists_in_dimension_analysis(self):
        """18_table9 模板声称的前置真实存在 (此前全仓 0 命中的幻影函数)。"""
        from news_process.papers.benefit_society import dimension_analysis as da
        assert callable(getattr(da, 'merge_dimensions_to_panel', None))

    def test_both_tracks_left_merge(self):
        from news_process.papers.benefit_society.dimension_analysis import (
            merge_dimensions_to_panel,
        )
        panel, dims = _synth_dimension_frames()
        out = merge_dimensions_to_panel(panel, dims, track='both')
        assert len(out) == 3  # left join: 面板行数不变
        for t in ('full', 'ctx'):
            for d in ('core_op', 'growth', 'resource', 'compliance'):
                assert f'benefit_{d}_{t}' in out.columns
        # 无覆盖 bank-year → NaN (招商银行 2018)
        assert pd.isna(out.loc[2, 'benefit_core_op_full'])
        assert out.loc[0, 'benefit_growth_ctx'] == pytest.approx(0.1)

    def test_single_track_selects_only_that_track(self):
        from news_process.papers.benefit_society.dimension_analysis import (
            merge_dimensions_to_panel,
        )
        panel, dims = _synth_dimension_frames()
        out = merge_dimensions_to_panel(panel, dims, track='full')
        assert 'benefit_core_op_full' in out.columns
        assert 'benefit_core_op_ctx' not in out.columns

    def test_missing_dimension_columns_fail_loud(self):
        from news_process.papers.benefit_society.dimension_analysis import (
            merge_dimensions_to_panel,
        )
        panel, dims = _synth_dimension_frames()
        with pytest.raises(ValueError, match='lacks columns'):
            merge_dimensions_to_panel(
                panel, dims.drop(columns=['benefit_core_op_ctx']), track='both')

    def test_refuses_to_overwrite_main_panel(self, tmp_path):
        """golden 锚定: output_path 指向主面板 parquet → fail-loud, 严禁改写。"""
        from news_process.papers.benefit_society.dimension_analysis import (
            merge_dimensions_to_panel,
        )
        panel, dims = _synth_dimension_frames()
        main_panel = tmp_path / '40_panel_yearly.parquet'
        with pytest.raises(ValueError, match='refusing to overwrite'):
            merge_dimensions_to_panel(
                panel, dims, track='both',
                panel_path=main_panel, output_path=main_panel)

    def test_writes_sidecar_copy(self, tmp_path):
        from news_process.papers.benefit_society.dimension_analysis import (
            merge_dimensions_to_panel,
        )
        panel, dims = _synth_dimension_frames()
        out_p = tmp_path / '40_panel_yearly_dimensions.parquet'
        merge_dimensions_to_panel(
            panel, dims, track='both',
            panel_path=tmp_path / '40_panel_yearly.parquet', output_path=out_p)
        assert out_p.exists()
        assert 'benefit_compliance_ctx' in pd.read_parquet(out_p).columns

    def test_invalid_track_rejected(self):
        from news_process.papers.benefit_society.dimension_analysis import (
            merge_dimensions_to_panel,
        )
        panel, dims = _synth_dimension_frames()
        with pytest.raises(ValueError, match='track'):
            merge_dimensions_to_panel(panel, dims, track='title')

    def test_cli_exposes_merge_panel_output_flag(self):
        from news_process.papers.benefit_society import dimension_analysis as da
        src = Path(da.__file__).read_text(encoding='utf-8')
        assert '--merge-panel-output' in src


def test_table9_template_no_phantom_prerequisite_and_dynamic_esttab():
    """gapfill-10/-14: 18_table9 前置注释不再指向 pipeline/features 幻影函数;
    esttab 经 estimates dir 动态拼装 (守卫跳过后不再 r(111))。"""
    text = _read('18_table9_dimension_decomposition.do.tmpl')
    assert 'pipeline/features/benefit_society.py\n* merge_dimensions_to_panel' not in text
    assert 'dimension_analysis' in text, "前置注释须指向真实产出链 (dimension_analysis)"
    assert 'estimates dir' in text, "esttab 名单未动态化"
    # 旧硬点名 esttab (10 个具名 eststo) 不复存在
    hard = [s for s in _stata_statements(text)
            if s.startswith('esttab') and 'D_core_op_full' in s]
    assert not hard, f"18_table9 仍硬点名维度估计: {hard[0][:90]}"
    assert "esttab `models'" in text


# ============================================================================
# gapfill-11: plot_placebo_comparison Coefficient TypeError
# ============================================================================

class TestPlaceboFigure:
    def _fake_pc(self, tmp_path):
        from news_process.papers._common.paper_config import PaperConfig
        return PaperConfig(
            paper_id='benefit_society',
            project_root=tmp_path,
            panel_dir=tmp_path,
            output_dir=tmp_path / 'output',
            do_dir=tmp_path / 'do',
            drafts_dir=tmp_path / 'drafts',
            config={},
        )

    def _fake_esttab_df(self):
        from news_process.papers._common.stata_postprocess import Coefficient
        cols = ['Main', 'Housing', 'Cards']
        return pd.DataFrame(
            {
                'Main': [Coefficient(0.40, 0.10, 3), Coefficient(176, None, 0),
                         Coefficient(0.51, None, 0)],
                'Housing': [Coefficient(0.08, 0.09, 0), Coefficient(176, None, 0),
                            Coefficient(0.32, None, 0)],
                'Cards': [None, Coefficient(176, None, 0), Coefficient(0.30, None, 0)],
            },
            index=pd.Index(['benefit_attitude', 'N', 'r2'], name='variable'),
        )[cols]

    def test_coefficient_cells_no_typeerror(self, tmp_path, monkeypatch):
        """实测 TypeError 复现路径: Coefficient 单元格 → 现经 _to_value_se 提值,
        图正常落盘 (修复前 float(Coefficient) 必崩)。"""
        import matplotlib
        matplotlib.use('Agg', force=True)

        from news_process.papers.benefit_society import figures as figs
        from news_process.papers.benefit_society import tables as tbls

        monkeypatch.setattr(tbls, 'build_table_a10_placebo',
                            lambda pc=None: self._fake_esttab_df())
        out = figs.plot_placebo_comparison(self._fake_pc(tmp_path))
        assert out.exists()

    def test_stats_first_row_skipped(self, tmp_path, monkeypatch):
        """footer stats 行 (N/r2) 不冒充系数行: 即使 stats 行排在最前,
        选取的系数行也是首个非 stats 变量。"""
        import matplotlib
        matplotlib.use('Agg', force=True)

        from news_process.papers._common.stata_postprocess import Coefficient
        from news_process.papers.benefit_society import figures as figs
        from news_process.papers.benefit_society import tables as tbls

        df = pd.DataFrame(
            {'Main': [Coefficient(176, None, 0), Coefficient(0.4, 0.1, 2)],
             'Housing': [Coefficient(176, None, 0), Coefficient(0.1, 0.1, 0)]},
            index=pd.Index(['N', 'beta_x'], name='variable'),
        )
        monkeypatch.setattr(tbls, 'build_table_a10_placebo', lambda pc=None: df)
        out = figs.plot_placebo_comparison(self._fake_pc(tmp_path),
                                           filename='figA2_alt.pdf')
        assert out.exists()

    def test_source_no_bare_float_cast(self):
        """回归锁: 源码不再对 esttab 单元格裸 float() (pd.notna 挡不住 namedtuple);
        旧崩溃表达式仅允许出现在 docstring 披露里。"""
        from news_process.papers.benefit_society import figures as figs
        src = Path(figs.__file__).read_text(encoding='utf-8')
        assert 'pd.notna(coef_row' not in src  # 旧执行路径 (必崩) 不复存在
        assert '[float(coef_row' not in src
        assert '_to_value_se' in src


# ============================================================================
# gapfill-12: NCD 亿元/billion 10× 单位冲突 — 解析侧防御 (prompt 冻结)
# ============================================================================

class TestNcdUnitMismatch:
    def test_prompt_string_frozen(self):
        """⚠ prompt 本体严禁改动 (改动 → 缓存键 bump → 付费重抽): Rule 1 原文与
        版本号逐字节保持; 修复只落在注释披露 + 解析侧。"""
        from news_process.papers.benefit_society import ncd_text_extractor as ext
        assert ext.EXTRACTION_PROMPT_VERSION == 'v1-2026-05-16'
        assert ('1. Convert all monetary amounts to consistent units (亿元/百万元) '
                'per field spec') in ext.EXTRACTION_PROMPT
        # 披露注释存在 (解析侧防御的指路牌)
        src = Path(ext.__file__).read_text(encoding='utf-8')
        assert 'fix(omni-gapfill-12, 2026-06-12)' in src

    def test_detect_unit_mismatch_heuristic(self):
        from news_process.papers.benefit_society.ncd_field_parser import (
            detect_unit_mismatch,
        )
        # 工行 ≈45,000 billion → 按亿元回答 450,000: 越上界 50,000 但 ÷10 落回
        assert detect_unit_mismatch('total_assets_billion_rmb', 450_000.0)
        assert detect_unit_mismatch('retail_deposit_billion_rmb', 60_000.0)
        # 区间内值 / 非 billion 字段 / 非数值 → False
        assert not detect_unit_mismatch('total_assets_billion_rmb', 45_000.0)
        assert not detect_unit_mismatch('npl_ratio_pct', 99.0)
        assert not detect_unit_mismatch('total_assets_billion_rmb', None)

    def test_validate_record_marks_suspect_not_silent(self):
        from news_process.papers.benefit_society.ncd_field_parser import (
            validate_record,
        )
        cleaned, warns = validate_record({
            'bank_name': '工商银行',
            'report_year': 2018,
            'total_assets_billion_rmb': 450_000.0,  # 亿元口径 10×
            'npl_ratio_pct': 99.0,                  # 普通越界 (非 10×)
        })
        assert cleaned['total_assets_billion_rmb'] is None  # 不自动 ÷10 改写
        assert cleaned['_unit_suspect_fields'] == ['total_assets_billion_rmb']
        assert any('SUSPECTED 10x' in w for w in warns)
        # 普通越界不误标
        assert not any('SUSPECTED 10x' in w for w in warns if 'npl' in w)

    def test_records_to_panel_surfaces_suspect_column(self):
        from news_process.papers.benefit_society.ncd_field_parser import (
            records_to_panel,
        )
        records = [{
            'pdf_path': '/tmp/icbc.pdf',
            'response_parsed': {
                'bank_name': '工商银行', 'report_year': 2018,
                'total_assets_billion_rmb': 450_000.0,
            },
        }]
        panel = records_to_panel(records)
        assert 'unit_suspect_fields' in panel.columns
        assert panel.iloc[0]['unit_suspect_fields'] == 'total_assets_billion_rmb'

    def test_triangulate_flags_10x_quotient(self):
        from news_process.papers.benefit_society.ncd_field_parser import (
            triangulate_with_annual_report,
        )
        ncd = pd.DataFrame({'bank_id': ['A', 'B'], 'year': [2018, 2018],
                            'total_assets': [1000.0, 110.0],
                            'npl': [1.5, 1.5], 'car': [12.0, 12.0]})
        ar = pd.DataFrame({'bank_id': ['A', 'B'], 'year': [2018, 2018],
                           'total_assets': [100.0, 100.0],
                           'npl': [1.5, 1.5], 'car': [12.0, 12.0]})
        out = triangulate_with_annual_report(ncd, ar)
        # A: 商=10 → 单位错; B: 商=1.1 → 普通不一致, 非单位错
        assert bool(out.loc[out['bank_id'] == 'A', 'unit_mismatch_total_assets'].iloc[0])
        assert not bool(out.loc[out['bank_id'] == 'B', 'unit_mismatch_total_assets'].iloc[0])
        assert bool(out.loc[out['bank_id'] == 'B', 'inconsistent_total_assets'].iloc[0])


# ============================================================================
# gapfill-14/-15: 00_master 编排补全 + capture 回显 _rc
# ============================================================================

class TestBenefitMaster:
    def test_master_orchestrates_all_promised_dos(self):
        """spec 承诺的 11b/19/22/23/24 进 master 路径 (此前装进包但永不运行)。"""
        master = _read('00_master.do.tmpl')
        for needle in ['11b_table2_boottest.do',
                       '19_bs_num_intensity_robustness.do',
                       '22_tableA9_external_validation.do',
                       '23_tableA10_placebo_business_lines.do',
                       '24_tableA11_anchor_family_alternative.do']:
            assert needle in master, f"00_master 仍未编排 {needle}"

    def test_master_capture_echoes_rc(self):
        """每个 capture noisily do 后必有 _rc 回显 (旧裸 capture do 静默吞错)。"""
        master = _read('00_master.do.tmpl')
        exec_lines = [ln.strip() for ln in master.splitlines()
                      if ln.strip() and not ln.strip().startswith('*')]
        n_capture = sum(1 for ln in exec_lines
                        if ln.startswith('capture noisily do '))
        n_echo = sum(1 for ln in exec_lines
                     if ln.startswith('if _rc display as error'))
        assert n_capture >= 12, f"capture noisily do 数量 {n_capture} < 12"
        # 01_data_prep 的 fail-loud 用 exit 而非 display 行, 故 echo ≥ capture-1
        assert n_echo >= n_capture - 1, (
            f"capture ({n_capture}) 与 _rc 回显 ({n_echo}) 不配对")
        # 旧裸 capture do (无 noisily, 静默吞错) 清零
        bare = [ln for ln in exec_lines
                if ln.startswith('capture do ')]
        assert not bare, f"裸 capture do 残留 (静默吞错): {bare}"


# ============================================================================
# gapfill-16: WCB 推断真正进表 (21/31/11b)
# ============================================================================

class TestWildBootstrapIntoTables:
    def test_tableA2_per_spec_estadd_p_wild(self):
        text = _read('21_tableA2_attitude_track_switch.do.tmpl')
        assert text.count('estadd scalar p_wild') >= 6, (
            "6 个规格须逐一 boottest + estadd p_wild (此前仅 full 主回归 1 条且只进 log)")
        assert 'capture which boottest' in text
        esttab_stmts = [s for s in _stata_statements(text) if s.startswith('esttab')]
        assert any('p_wild' in s for s in esttab_stmts), "esttab 未呈现 p_wild stats 行"
        # 表注如实: SE 是渐近 cluster, 不再笼统声称 WCB inference
        assert 'asymptotic cluster-robust' in text

    def test_figure2_note_no_false_wcb_claim(self):
        text = _read('31_figure2_coefplot_dual.do.tmpl')
        exec_text = '\n'.join(ln for ln in text.splitlines()
                              if not ln.strip().startswith('*'))
        assert 'Wild cluster bootstrap inference' not in exec_text, (
            "coefplot 画的是渐近 cluster CI, 图注不得声称 WCB inference")
        assert 'asymptotic cluster-robust' in exec_text

    def test_11b_p_cluster_uses_t_distribution(self):
        text = _read('11b_table2_boottest.do.tmpl')
        assert 'ttail(e(df_r)' in text, "p_cluster 须用 t(e(df_r)) 口径 (reghdfe 同款)"
        assert 'normal(abs(' not in text, "normal() z 近似残留 (与表内 t(G-1) p 值口径不一)"


# ============================================================================
# gapfill-17: 19_bs 双轨纪律 + 聚类 + DV 口径
# ============================================================================

class TestNumIntensityTemplate:
    def test_tracks_not_in_same_rhs(self):
        """双轨互为稳健性 (用户钦定): full/ctx 不得同进一条 reghdfe RHS。"""
        text = _read('19_bs_num_intensity_robustness.do.tmpl')
        offenders = [s for s in _stata_statements(text)
                     if s.startswith('reghdfe')
                     and 'mean_num_intensity_full' in s
                     and 'mean_num_intensity_ctx' in s]
        assert not offenders, f"双轨同 RHS 残留: {offenders[0][:90]}"
        # 两轨各有自己的单轨回归列
        assert any(s.startswith('reghdfe') and 'mean_num_intensity_ctx' in s
                   for s in _stata_statements(text)), "ctx 单轨回归缺失"

    def test_no_year_clustering_and_winsorized_dv(self):
        text = _read('19_bs_num_intensity_robustness.do.tmpl')
        reg_stmts = [s for s in _stata_statements(text) if s.startswith('reghdfe')]
        assert reg_stmts
        for s in reg_stmts:
            # 仅扫可执行语句 (修复注释里如实引用旧写法属披露, 不计违规)
            assert 'cluster bank_id year' not in s, (
                f"G_year=2 红线: 不得按 year 二维聚类 (cf. 11b 头注): {s[:80]}")
            assert '{{MAIN_DV}}_w' in s, f"DV 未用 winsorized _w 口径: {s[:80]}"

    def test_ctx_guard_and_dynamic_esttab(self):
        text = _read('19_bs_num_intensity_robustness.do.tmpl')
        assert 'capture confirm variable mean_num_intensity_ctx' in text
        assert 'estimates dir' in text, "esttab 名单未动态化 (守卫跳过 → r(111))"


# ============================================================================
# gapfill-18: prompt_sensitivity locus 聚合与生产同源 (跨组接缝)
# ============================================================================

class TestLocusResolverSeam:
    @pytest.fixture(scope='class')
    def mod39(self):
        from news_process.validation import prompt_sensitivity
        return prompt_sensitivity

    def test_binding_is_production_function_object(self, mod39):
        from news_process.pipeline.sentiment import tone_llms
        assert mod39._resolve_locus_track is tone_llms._resolve_locus_track

    def test_source_no_manual_inline_alignment(self):
        """回归锁: aggregate_variant_results 不再为 locus 手工内联
        majority_vote_categorical(empty_fallback=keyword) — 那是 g-tonellms-10
        之前的旧生产行为, 会与生产再度漂移。"""
        src_path = _PKG_ROOT / 'validation' / 'prompt_sensitivity.py'
        src = src_path.read_text(encoding='utf-8')
        assert 'empty_fallback=_kw_cat' not in src
        assert '_resolve_locus_track = _tone_llms._resolve_locus_track' in src

    @pytest.mark.parametrize('votes,topics', [
        ([], []),                                   # 零证据空票
        ([], ['区块链']),                            # 空票 + keyword 真实证据
        (['底层技术', '底层技术', '应用场景'], []),     # 多数票
        (['底层技术', '应用场景'], ['移动支付']),       # 平局 + keyword
    ])
    def test_variant_aggregation_parity_with_production(self, mod39, monkeypatch,
                                                        votes, topics):
        """任意票型下, 变体聚合 label == 生产 _resolve_locus_track label (同源)。"""
        from news_process.pipeline.sentiment import tone_llms

        def fake_aggregate(_model_res, _models):
            return (True, '正面', 1.0, 1.0, 3, 3, 0, 0,
                    {}, list(topics), list(votes), [],
                    0, 0.75, 0.5, 0.5, [], 0.5)

        monkeypatch.setattr(mod39, '_aggregate_track', fake_aggregate)
        df = pd.DataFrame(index=[0])
        out = mod39.aggregate_variant_results(
            df.copy(), {0: {'full': {}, 'ctx': {}}},
            [{'model_name': 'm0', 'short_name': 'm0',
              'base_url': 'http://mock.invalid', 'api_key': 'k'}],
            'VX')
        expected_label, _ = tone_llms._resolve_locus_track(list(votes), list(topics))
        assert out['VX_innovation_locus_full'].iloc[0] == expected_label
