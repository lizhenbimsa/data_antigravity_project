"""tests/test_omni_fix_papers_misc.py — omni 2026-06-11 g-papers-misc 组回归锁.

锁定 12 条 confirmed 缺陷的修复后行为 (防静默 revert):

  01  esttab CSV 桥死接线 → parse_esttab_tex 分支 + read_paper_esttab 同名 .tex
      回退 + 模板产物/tables.py 读取名 wiring 一致性
  02  P3/P4/P5 figures 幻影列 ArrowInvalid → schema 探测 + 占位图优雅降级
      + analysis CLI broad-except 守卫
  03  P3/P4/P5 Table 1 幻影 treatment → panel 真实列 + NaN 占位 + CSV 脚注披露
  04  P1 tone Figure 1 静默剔除零覆盖 → 显式披露 (标题/图注/警告日志)
  05  locus/collab gap 文档值域 {-1,+1} → {-1, 0, +1} (平票/缺失=0)
  06  P1 Table 1 主轨 (ctx) 连续分与 IV 缺席 → 增补 3 个 ctx 列
  07  parse_esttab 科学计数法截断 + 同名变量行静默覆盖 → e-notation regex
      + __panelN 消歧守卫
  08  attention tables docstring 'staggered DiD baseline' → 与 frozen spec
      (cross-sectional intensity DiD) 对齐
  09  Hassan extensive≠intensive 锚点更正全链传播 (spec/runner/config/codebook/三件套)
  10  block_subsampling_ci 方法标签 (P-R subsampling → block bootstrap) 更正
      + cluster 簇模式 + Deprecation alias
  11  P3/P4/P5 spec 主 treatment 幻影列 → panel 真实聚合列 (frac 族)
  12  P1/P2 spec IV 标识符零实现 → P1 改实存 LOO/Bartik, P2 补 PENDING 标注

全部用合成 DataFrame/fixture, 不依赖盘上大数据; 不触网。

# 白话: 各论文模块的杂项修复锁: 读取 Stata 表格结果时, CSV 不在就读同名
# .tex, 不再直接报错; 画图/做描述统计表引用的列必须是面板里真实存在的列,
# 缺列时画占位图、给 NaN 占位行并在脚注里说明, 而不是崩溃或悄悄删行;
# 解析回归表要认得科学计数法(1.23e-05), 同名变量行要消歧; 论文规格文件里
# 声称的处理变量/工具变量必须指向真实实现, 没实现的明确标 PENDING。
"""

from __future__ import annotations

import inspect
import logging
import re
import sys
import warnings
from pathlib import Path

import matplotlib

matplotlib.use('Agg')  # headless backend (figure 测试不开窗口)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import pytest  # noqa: E402
import yaml  # noqa: E402

_NEWS_PROCESS_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_PARENT = _NEWS_PROCESS_ROOT.parent
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.papers._common.paper_config import PaperConfig  # noqa: E402
from news_process.papers._common.stata_postprocess import (  # noqa: E402
    Coefficient,
    parse_esttab_csv,
    parse_esttab_tex,
    read_paper_esttab,
)
from news_process.papers._common.stats_helpers import (  # noqa: E402
    block_subsampling_ci,
    cluster_block_bootstrap_ci,
)

_TEMPLATES_ROOT = _NEWS_PROCESS_ROOT / 'papers' / '_common' / 'stata_templates'
_PAPERS_ROOT = _NEWS_PROCESS_ROOT / 'papers'


# ----------------------------------------------------------------------------
# 共享 helpers
# ----------------------------------------------------------------------------

def _make_pc(tmp_path: Path, paper_id: str) -> PaperConfig:
    """构造指向 tmp 的 PaperConfig (panel_dir 与 cfg['paths']['output_dir'] 一致,
    使 pc.panel_path 与 load_panel(paper_id=..., project_config=...) 同源)。"""
    panel_dir = tmp_path / 'panel'
    panel_dir.mkdir(parents=True, exist_ok=True)
    root = tmp_path / 'assets' / paper_id
    return PaperConfig(
        paper_id=paper_id,
        project_root=tmp_path,
        panel_dir=panel_dir,
        output_dir=root / 'output',
        do_dir=root / 'do',
        drafts_dir=root / 'drafts',
        config={'paths': {'output_dir': str(panel_dir)}},
    )


def _write_panel(pc: PaperConfig, df: pd.DataFrame,
                 filename: str = '40_panel_yearly.parquet') -> Path:
    p = pc.panel_path(filename)
    df.to_parquet(p)
    return p


# 仿 esttab 默认 LaTeX (booktabs) 输出的最小 fixture
_FIXTURE_TEX = r"""{
\def\sym#1{\ifmmode^{#1}\else\(^{#1}\)\fi}
\begin{tabular}{l*{3}{c}}
\hline\hline
            &\multicolumn{1}{c}{(1)}&\multicolumn{1}{c}{(2)}&\multicolumn{1}{c}{(3)}\\
\hline
llm\_vote\_tone\_full&       0.123\sym{***}&       0.150\sym{**} &       0.180\sym{***}\\
            &     (0.034)         &     (0.062)         &     (0.045)         \\
peer\_compete\_idx&                     &      -0.025         &      -0.030\sym{*}  \\
            &                     &     (0.018)         &     (0.017)         \\
\hline
\(N\)       &         164         &         164         &         164         \\
r2          &        0.45         &        0.52         &        0.61         \\
\hline\hline
\end{tabular}
}
"""


# ============================================================================
# omni-01: esttab .tex 解析分支 + read_paper_esttab 回退 + wiring 一致性
# ============================================================================

class TestEsttabTexBridge:

    def test_parse_esttab_tex_same_semantics_as_csv(self, tmp_path):
        p = tmp_path / 'table2_main.tex'
        p.write_text(_FIXTURE_TEX, encoding='utf-8')
        df = parse_esttab_tex(p)

        assert list(df.columns) == ['(1)', '(2)', '(3)']
        c = df.loc['llm_vote_tone_full', '(1)']
        assert isinstance(c, Coefficient)
        assert c.value == pytest.approx(0.123)
        assert c.se == pytest.approx(0.034)
        assert c.stars == 3
        c2 = df.loc['peer_compete_idx', '(3)']
        assert c2.value == pytest.approx(-0.030)
        assert c2.stars == 1
        # footer stats: \(N\) → N
        assert df.loc['N', '(2)'].value == pytest.approx(164)
        assert df.loc['r2', '(3)'].value == pytest.approx(0.61)

    def test_read_paper_esttab_falls_back_to_sibling_tex(self, tmp_path):
        pc = _make_pc(tmp_path, 'llm_peer')
        tdir = pc.output_dir / 'tables'
        tdir.mkdir(parents=True, exist_ok=True)
        (tdir / 'table2_main.tex').write_text(_FIXTURE_TEX, encoding='utf-8')

        # csv 缺失 → 自动解析同名 .tex (旧实现这里 FileNotFoundError)
        df = read_paper_esttab('llm_peer', 'table2_main.csv', paper_config=pc)
        assert df.loc['llm_vote_tone_full', '(1)'].value == pytest.approx(0.123)

    def test_read_paper_esttab_prefers_csv_when_both_exist(self, tmp_path):
        pc = _make_pc(tmp_path, 'llm_peer')
        tdir = pc.output_dir / 'tables'
        tdir.mkdir(parents=True, exist_ok=True)
        (tdir / 'table2_main.tex').write_text(_FIXTURE_TEX, encoding='utf-8')
        (tdir / 'table2_main.csv').write_text(
            ',M1\nx_var,9.99***\n,(0.10)\nN,42\n', encoding='utf-8')

        df = read_paper_esttab('llm_peer', 'table2_main.csv', paper_config=pc)
        assert 'x_var' in df.index  # 读的是 csv 而非 tex

    def test_read_paper_esttab_raises_when_both_missing(self, tmp_path):
        pc = _make_pc(tmp_path, 'llm_peer')
        (pc.output_dir / 'tables').mkdir(parents=True, exist_ok=True)
        with pytest.raises(FileNotFoundError, match='esttab output not found'):
            read_paper_esttab('llm_peer', 'table9_nope.csv', paper_config=pc)

    @pytest.mark.parametrize('paper_id', [
        'bank_fintech_attention', 'bank_fintech_substance',
        'bank_fintech_locus', 'bank_fintech_collab',
    ])
    def test_tables_py_filenames_have_tex_producers(self, paper_id):
        """wiring: tables.py 读取的每个 <stem>.csv 须有模板写出同名 <stem>.tex."""
        src = (_PAPERS_ROOT / paper_id / 'tables.py').read_text(encoding='utf-8')
        stems = re.findall(
            r"read_paper_esttab\(\s*(?:'[a-z_]+'|PAPER_ID)\s*,\s*'([^']+)\.csv'", src)
        assert stems, f"{paper_id}/tables.py 未发现任何 read_paper_esttab 调用"

        tmpl_dir = _TEMPLATES_ROOT / paper_id
        tmpl_text = '\n'.join(
            p.read_text(encoding='utf-8', errors='replace')
            for p in tmpl_dir.glob('*.do.tmpl'))
        for stem in stems:
            assert f'{stem}.tex' in tmpl_text, (
                f"{paper_id}: tables.py 读 {stem}.csv 但模板未写 {stem}.tex "
                f"(死接线回归, fix(omni-g-papers-misc-01))")


# ============================================================================
# omni-07: e-notation + 同名变量行守卫
# ============================================================================

class TestEsttabParserGuards:

    def test_scientific_notation_value_and_se(self, tmp_path):
        # 旧 regex r'^[\-\d\.]+' 对 1.23e-05 只截到 1.23 (放大 5 个数量级)
        csv = (",M1\n"
               "tiny_coef,1.23e-05***\n"
               ",(4.5e-06)\n"
               "ll,-1.5e+04\n")
        p = tmp_path / 't.csv'
        p.write_text(csv, encoding='utf-8')
        df = parse_esttab_csv(p)
        c = df.loc['tiny_coef', 'M1']
        assert c.value == pytest.approx(1.23e-05)
        assert c.se == pytest.approx(4.5e-06)
        assert c.stars == 3
        assert df.loc['ll', 'M1'].value == pytest.approx(-1.5e+04)

    def test_duplicate_variable_rows_get_panel_suffix(self, tmp_path, caplog):
        # esttab 多 panel 堆叠 (Panel A/B) 同名变量行: 旧实现后行静默覆盖前行
        csv = (",M1\n"
               "x,0.100*\n"
               ",(0.010)\n"
               "x,0.900**\n"
               ",(0.020)\n"
               "N,99\n")
        p = tmp_path / 'dup.csv'
        p.write_text(csv, encoding='utf-8')
        with caplog.at_level(logging.WARNING):
            df = parse_esttab_csv(p)
        assert df.loc['x', 'M1'].value == pytest.approx(0.100)
        assert df.loc['x__panel2', 'M1'].value == pytest.approx(0.900)
        assert df.loc['x__panel2', 'M1'].se == pytest.approx(0.020)
        assert any('duplicate variable row' in r.message for r in caplog.records)


# ============================================================================
# omni-02: P3/P4/P5 figures 缺列优雅降级 + analysis CLI 守卫
# ============================================================================

_FIG_CASES = [
    # (paper_id, figures module, func name, 真实列, 合成值)
    ('bank_fintech_substance', 'plot_substantiveness_distribution',
     {'sub_frac': [0.1, 0.5, 0.9, 0.3]}),
    ('bank_fintech_locus', 'plot_locus_distribution',
     {'tech_frac': [0.6, 0.2, 0.5, 0.0], 'app_frac': [0.1, 0.7, 0.5, 0.4]}),
    ('bank_fintech_collab', 'plot_collab_mode_distribution',
     {'collab_frac': [0.0, 0.4, 0.8, 1.0]}),
]


def _get_figfunc(paper_id: str, func_name: str):
    import importlib
    mod = importlib.import_module(f'news_process.papers.{paper_id}.figures')
    return getattr(mod, func_name)


class TestP3P4P5FigureGuards:

    @pytest.mark.parametrize('paper_id,func_name,cols', _FIG_CASES)
    def test_placeholder_on_missing_columns(self, tmp_path, paper_id,
                                            func_name, cols, caplog):
        """面板存在但候选列全缺 → 占位图 + WARN, 不抛 (旧版 ArrowInvalid 崩 CLI)."""
        pc = _make_pc(tmp_path, paper_id)
        _write_panel(pc, pd.DataFrame({'year': [2017, 2018],
                                       'unrelated': [1.0, 2.0]}))
        fn = _get_figfunc(paper_id, func_name)
        with caplog.at_level(logging.WARNING):
            out = fn(pc)
        assert out is not None and Path(out).exists()
        assert any('占位图' in r.message or 'placeholder' in r.message.lower()
                   for r in caplog.records)

    @pytest.mark.parametrize('paper_id,func_name,cols', _FIG_CASES)
    def test_real_columns_produce_figure(self, tmp_path, paper_id, func_name, cols):
        pc = _make_pc(tmp_path, paper_id)
        df = pd.DataFrame(cols)
        df['year'] = range(2017, 2017 + len(df))
        _write_panel(pc, df)
        out = _get_figfunc(paper_id, func_name)(pc)
        assert out is not None and Path(out).exists()

    @pytest.mark.parametrize('paper_id,func_name,cols', _FIG_CASES)
    def test_none_when_panel_missing(self, tmp_path, paper_id, func_name, cols):
        pc = _make_pc(tmp_path, paper_id)  # panel_dir 为空目录
        assert _get_figfunc(paper_id, func_name)(pc) is None

    @pytest.mark.parametrize('paper_id,func_name', [
        ('bank_fintech_substance', 'plot_substantiveness_distribution'),
        ('bank_fintech_locus', 'plot_locus_distribution'),
        ('bank_fintech_collab', 'plot_collab_mode_distribution'),
    ])
    def test_analysis_cli_survives_arrowinvalid(self, monkeypatch,
                                                paper_id, func_name):
        """analysis.py figures 段 broad except: 单图抛 ArrowInvalid 时 CLI 不崩."""
        import importlib

        from pyarrow.lib import ArrowInvalid

        figures_mod = importlib.import_module(
            f'news_process.papers.{paper_id}.figures')
        analysis_mod = importlib.import_module(
            f'news_process.papers.{paper_id}.analysis')

        def _boom(*args, **kwargs):
            raise ArrowInvalid('No match for FieldRef.Name(phantom_col)')

        monkeypatch.setattr(figures_mod, func_name, _boom)
        # 旧版只 catch FileNotFoundError → 这里会 traceback; 修复后返回 0
        assert analysis_mod.main(['--stage', 'figures']) == 0


# ============================================================================
# omni-03 / omni-06: Table 1 变量清单 — panel 真实列 + 脚注 + ctx 主轨增补
# ============================================================================

class TestTable1Inventories:

    def test_p3p4p5_treatment_rows_are_panel_real(self):
        from news_process.papers.bank_fintech_collab.tables import (
            _TABLE1_VARIABLES as collab_vars,
        )
        from news_process.papers.bank_fintech_locus.tables import (
            _TABLE1_VARIABLES as locus_vars,
        )
        from news_process.papers.bank_fintech_substance.tables import (
            _TABLE1_VARIABLES as subst_vars,
        )

        # panel 真实物化的 bank-year 占比编码进清单
        assert {'sub_frac', 'symb_frac'} <= set(subst_vars)
        assert {'tech_frac', 'app_frac'} <= set(locus_vars)
        assert {'collab_frac', 'indep_frac'} <= set(collab_vars)
        # 文章级字符串 / Stata 临时 gen 幻影列禁止回流
        phantom = {'innovation_substantiveness_full', 'innovation_substantiveness_ctx',
                   'innovation_collab_mode_full', 'innovation_collab_mode_ctx',
                   'locus_layer_full', 'locus_scenario_full', 'locus_gap'}
        for vars_ in (subst_vars, locus_vars, collab_vars):
            assert not (phantom & set(vars_)), (
                f"幻影列回流 Table 1 清单: {phantom & set(vars_)}")

    def test_collab_table1_footnote_and_nan_placeholders(self, tmp_path):
        """treatment 行实数据 + enrichment 缺列 NaN 占位 + CSV 脚注披露."""
        from news_process.papers.bank_fintech_collab import tables as ct

        pc = _make_pc(tmp_path, 'bank_fintech_collab')
        _write_panel(pc, pd.DataFrame({
            'collab_frac': [0.2, 0.4, 0.6],
            'indep_frac': [0.8, 0.6, 0.4],
            'collab_frac_cm': [0.1, 0.3, 0.5],
            'indep_frac_cm': [0.9, 0.7, 0.5],
            'year': [2017, 2018, 2017],
        }))
        csv_path = ct.write_table1(pc, dta_filename=None)
        assert csv_path.exists()

        table = pd.read_csv(csv_path, comment='#', index_col=0)
        assert table.loc['collab_frac', 'Mean'] == pytest.approx(0.4)
        # 金融 enrichment 列保留为可见 NaN 占位行 (非静默剔除)
        assert 'ln_assets' in table.index
        assert np.isnan(table.loc['ln_assets', 'Mean'])
        # CSV 末尾脚注披露 (存在性过滤说明)
        raw = csv_path.read_text(encoding='utf-8-sig')
        assert '# ' in raw and 'M0.5.11' in raw

    def test_tone_table1_includes_ctx_main_track(self):
        """fix(omni-g-papers-misc-06): spec main=ctx 轨 — 连续分与 IV 须列 ctx."""
        from news_process.papers.bank_fintech_tone.tables import _TABLE1_VARIABLES

        v = list(_TABLE1_VARIABLES)
        for ctx_col, full_col in [
            ('llm_vote_cont_ctx', 'llm_vote_cont_full'),
            ('prov_leave1out_tone_ctx', 'prov_leave1out_tone_full'),
            ('bartik_type_iv_ctx', 'bartik_type_iv_full'),
        ]:
            assert ctx_col in v, f"缺主轨列 {ctx_col}"
            assert full_col in v
            assert v.index(ctx_col) < v.index(full_col), (
                f"main-ctx 应排在 {full_col} 之前")


# ============================================================================
# omni-04: tone Figure 1 零覆盖剔除显式披露
# ============================================================================

class TestToneFigureDisclosure:

    def test_zero_coverage_exclusion_disclosed(self, tmp_path, caplog):
        from news_process.papers.bank_fintech_tone.figures import (
            plot_news_coverage_distribution,
        )

        pc = _make_pc(tmp_path, 'bank_fintech_tone')
        _write_panel(pc, pd.DataFrame({'n_articles': [0, 0, 3, 10, 0, 7]}))
        with caplog.at_level(logging.WARNING,
                             logger='papers.bank_fintech_tone.figures'):
            out = plot_news_coverage_distribution(pc)
        assert Path(out).exists()
        # 3 个零覆盖 bank-year 的剔除不再静默
        assert any('3 个零覆盖' in r.message for r in caplog.records)

    def test_figure_labels_carry_conditional_disclosure(self):
        """标题/xlabel 含 'conditional on >=1 article' 披露 (源码级锁定)."""
        from news_process.papers.bank_fintech_tone import figures as f

        src = inspect.getsource(f.plot_news_coverage_distribution)
        assert 'conditional on' in src
        assert 'Excluded' in src  # 图注报告被排除行数


# ============================================================================
# omni-05: gap 值域文档 {-1, 0, +1}
# ============================================================================

class TestGapValueRangeDocs:

    def test_locus_init_docstring(self):
        import news_process.papers.bank_fintech_locus as locus
        assert '{-1, 0, +1}' in (locus.__doc__ or '')
        assert '平票' in (locus.__doc__ or '')

    def test_collab_init_docstring(self):
        import news_process.papers.bank_fintech_collab as collab
        assert '{-1, 0, +1}' in (collab.__doc__ or '')

    def test_locus_spec_secondary_construction(self):
        raw = (_PAPERS_ROOT / 'bank_fintech_locus' / 'paper_spec.yaml'
               ).read_text(encoding='utf-8')
        assert '{-1, 0, +1}' in raw
        assert '{-1, +1}' not in raw.replace('{-1, 0, +1}', '')

    def test_collab_spec_gap_annotation(self):
        raw = (_PAPERS_ROOT / 'bank_fintech_collab' / 'paper_spec.yaml'
               ).read_text(encoding='utf-8')
        assert '{-1, 0, +1}' in raw


# ============================================================================
# omni-08: attention Table 2 docstring 与 frozen spec 对齐
# ============================================================================

class TestAttentionTable2Wording:

    def test_docstrings_say_cross_sectional_intensity_did(self):
        from news_process.papers.bank_fintech_attention import tables as t

        module_doc = t.__doc__ or ''
        fn_doc = t.build_table2_main.__doc__ or ''
        assert 'cross-sectional intensity DiD' in module_doc
        assert 'cross-sectional intensity DiD' in fn_doc
        # 旧无保留宣称禁止回归 (staggered 仅可在 'csdid 仅 T≥3 robustness' 语境出现)
        assert 'staggered DiD baseline + IV' not in module_doc
        assert 'staggered DiD baseline + IV' not in fn_doc

    def test_spec_baseline_is_intensity_did(self):
        spec = yaml.safe_load(
            (_PAPERS_ROOT / 'bank_fintech_attention' / 'paper_spec.yaml'
             ).read_text(encoding='utf-8'))
        assert spec['identification']['baseline'] == 'cross_sectional_intensity_did'


# ============================================================================
# omni-09: Hassan extensive≠intensive 锚点更正全链传播
# ============================================================================

class TestHassanAnchorPropagation:

    def test_attention_spec_discloses_fang_peress_extensive(self):
        raw = (_PAPERS_ROOT / 'bank_fintech_attention' / 'paper_spec.yaml'
               ).read_text(encoding='utf-8')
        assert 'Fang & Peress' in raw
        assert 'extensive' in raw
        # 旧的无保留 '方法对标 Hassan et al. 2019 QJE' 声称已撤
        assert '方法对标 Hassan' not in raw

    def test_attention_package_docstring(self):
        import news_process.papers.bank_fintech_attention as p2
        doc = p2.__doc__ or ''
        assert 'Fang & Peress' in doc and 'extensive' in doc

    def test_attention_media_logger_anchor(self):
        from news_process.pipeline.panel.attention_media import (
            compute_attention_treatments,
        )
        src = inspect.getsource(compute_attention_treatments)
        assert 'Fang-Peress 2009 JF extensive' in src

    def test_runner_and_config_comment_anchor(self):
        runner_raw = (_NEWS_PROCESS_ROOT / 'pipeline' / 'panel' / 'runner.py'
                      ).read_text(encoding='utf-8')
        assert 'Fang-Peress 2009 JF extensive' in runner_raw
        cfg_raw = (_NEWS_PROCESS_ROOT / 'config' / 'panel.yaml'
                   ).read_text(encoding='utf-8')
        assert 'Fang-Peress (2009 JF)' in cfg_raw

    def test_codebook_attention_index_reference(self):
        cb_raw = (_NEWS_PROCESS_ROOT / 'pipeline' / 'panel' / 'codebook.py'
                  ).read_text(encoding='utf-8')
        assert 'Fang & Peress (2009, JF) extensive coverage' in cb_raw
        assert 'cf. Hassan et al. (2019, QJE) intensive share' in cb_raw


# ============================================================================
# omni-10: cluster_block_bootstrap_ci (方法标签更正 + 簇模式 + alias)
# ============================================================================

class TestClusterBlockBootstrap:

    def test_positional_mode_basic(self):
        rng = np.random.default_rng(0)
        vals = rng.normal(0.5, 0.1, size=40)
        point, lo, hi = cluster_block_bootstrap_ci(
            vals, block_size=2, n_resamples=300, seed=42)
        assert point == pytest.approx(float(np.mean(vals)))
        assert lo <= point <= hi

    def test_cluster_mode_reproducible_and_sane(self):
        vals = [1.0, 1.1, 5.0, 5.2, 9.0, 9.1, 9.2]
        banks = ['A', 'A', 'B', 'B', 'C', 'C', 'C']
        r1 = cluster_block_bootstrap_ci(vals, cluster_id=banks,
                                        n_resamples=400, seed=7)
        r2 = cluster_block_bootstrap_ci(vals, cluster_id=banks,
                                        n_resamples=400, seed=7)
        assert r1 == r2
        point, lo, hi = r1
        assert point == pytest.approx(float(np.mean(vals)))
        assert lo <= point <= hi
        # 簇均值范围之外不可能出现 (整簇重采样的代数边界)
        assert lo >= min(np.mean([1.0, 1.1]), np.mean([5.0, 5.2]),
                         np.mean([9.0, 9.1, 9.2])) - 1e-9
        assert hi <= max(np.mean([1.0, 1.1]), np.mean([5.0, 5.2]),
                         np.mean([9.0, 9.1, 9.2])) + 1e-9

    def test_cluster_mode_handles_nan_and_misalignment(self):
        vals = [1.0, np.nan, 2.0, 4.0]
        banks = ['A', 'A', 'B', 'B']
        point, lo, hi = cluster_block_bootstrap_ci(
            vals, cluster_id=banks, n_resamples=100, seed=3)
        assert point == pytest.approx(np.nanmean(vals))
        with pytest.raises(ValueError, match='cluster_id length'):
            cluster_block_bootstrap_ci([1.0, 2.0], cluster_id=['A'],
                                       n_resamples=10, seed=1)

    def test_cluster_mode_requires_two_clusters(self):
        with pytest.raises(ValueError, match='2 distinct clusters'):
            cluster_block_bootstrap_ci([1.0, 2.0, 3.0], cluster_id=['A', 'A', 'A'],
                                       n_resamples=10, seed=1)

    def test_deprecated_alias_warns_and_matches(self):
        vals = list(np.linspace(0, 1, 20))
        with pytest.warns(DeprecationWarning, match='misnomer'):
            r_alias = block_subsampling_ci(vals, block_size=2,
                                           n_subsamples=200, seed=11)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            r_new = cluster_block_bootstrap_ci(vals, block_size=2,
                                               n_resamples=200, seed=11)
        assert r_alias == r_new  # 数值行为逐位一致 (golden-safe)

    def test_method_label_corrected(self):
        """模块/函数文档不得再宣称实现 = Politis-Romano subsampling."""
        from news_process.papers._common import stats_helpers as sh

        assert 'Implements Politis-Romano' not in (sh.__doc__ or '')
        assert 'block bootstrap' in (cluster_block_bootstrap_ci.__doc__ or '')

    def test_benefit_society_figure_uses_cluster_mode(self):
        from news_process.papers.benefit_society import figures as bf

        src = inspect.getsource(bf.plot_benefit_distribution_with_subsampling_ci)
        assert 'cluster_block_bootstrap_ci' in src
        assert 'target_bank' in src
        assert 'cluster block bootstrap' in src  # 图注措辞更正


# ============================================================================
# omni-11: P3/P4/P5 spec 主 treatment = panel 真实聚合列
# ============================================================================

class TestSpecTreatmentRealColumns:

    def test_substance_primary_is_sub_frac(self):
        spec = yaml.safe_load(
            (_PAPERS_ROOT / 'bank_fintech_substance' / 'paper_spec.yaml'
             ).read_text(encoding='utf-8'))
        assert spec['treatment']['primary'] == 'sub_frac'

    def test_collab_primary_is_collab_frac_and_gap_formula_numeric(self):
        spec = yaml.safe_load(
            (_PAPERS_ROOT / 'bank_fintech_collab' / 'paper_spec.yaml'
             ).read_text(encoding='utf-8'))
        assert spec['treatment']['primary'] == 'collab_frac'
        gap = spec['treatment']['alternative_construction'][
            'independent_minus_collab_gap']
        # 旧式 'innovation_collab_mode_full - (1 - innovation_collab_mode_full)'
        # 对分类字符串做算术 — 现须为 frac 列运算
        assert 'indep_frac' in gap and 'collab_frac' in gap
        assert 'innovation_collab_mode' not in gap

    def test_locus_pair_construction_from_frac_columns(self):
        spec = yaml.safe_load(
            (_PAPERS_ROOT / 'bank_fintech_locus' / 'paper_spec.yaml'
             ).read_text(encoding='utf-8'))
        cons = spec['treatment']['primary_pair_construction']
        assert 'tech_frac' in cons['locus_layer_full']
        assert 'app_frac' in cons['locus_scenario_full']
        # 文章级字符串构造式禁止回归 (构造值本身不得引用 innovation_locus_full;
        # 勘误注释引用旧式属披露, 不算回归)
        assert 'innovation_locus_full' not in cons['locus_layer_full']
        assert 'innovation_locus_full' not in cons['locus_scenario_full']

    def test_derivative_defaults_synced(self):
        """接口锁: derivative_replication MAIN_TREAT 与 spec primary 同步
        (g-replication 组落地, 此处锁跨组接口防回退)."""
        from news_process.papers._common.derivative_replication import (
            _PAPER_DEFAULTS,
            get_paper_defaults,
        )

        assert get_paper_defaults('bank_fintech_substance')['MAIN_TREAT'] == 'sub_frac'
        # collab 不在 _DERIVATIVE_PAPER_IDS 白名单 (P5 onboarding 未完成,
        # derivative 注册待独立 PR 接线), 直接锁 _PAPER_DEFAULTS 块
        assert _PAPER_DEFAULTS['bank_fintech_collab']['MAIN_TREAT'] == 'collab_frac'


# ============================================================================
# omni-12: P1/P2 spec IV 标识符
# ============================================================================

class TestSpecIVIdentifiers:

    def test_tone_iv_points_to_materialized_columns(self):
        spec = yaml.safe_load(
            (_PAPERS_ROOT / 'bank_fintech_tone' / 'paper_spec.yaml'
             ).read_text(encoding='utf-8'))
        iv = spec['identification']['iv']
        # 旧 primary=leave_one_out_industry_tone 全管线零实现 → 改实存地理 LOO
        assert iv['primary'] == 'prov_leave1out_tone_ctx'
        assert iv['fallback'] == 'bartik_type_iv_ctx'
        raw = (_PAPERS_ROOT / 'bank_fintech_tone' / 'paper_spec.yaml'
               ).read_text(encoding='utf-8')
        # 已知缺口披露 (22_tableA3 工具化 LOCUS 非 tone) 必须在 spec 中可见
        assert 'LOCUS' in raw

    def test_attention_iv_pending_annotation(self):
        raw = (_PAPERS_ROOT / 'bank_fintech_attention' / 'paper_spec.yaml'
               ).read_text(encoding='utf-8')
        assert 'PENDING M0.5.X' in raw
        spec = yaml.safe_load(raw)
        iv = spec['identification']['iv']
        # 标识符保留 (frozen spec 承诺) 但已具 pending 披露 + interim 替代提示
        assert iv['primary'] == 'leave_one_out_peer_attention_iv'
        assert 'bartik' in raw  # interim 现实可用替代已提示
