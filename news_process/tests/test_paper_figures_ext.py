"""tests/test_paper_figures_ext.py — Figure 2-4 generic + paper-level tests.

P3.3 (plan-r3 derivative-paper extension, 2026-05-15)

Tests use matplotlib's Agg backend (headless safe) and write to tmp_path.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Force Agg backend before importing pyplot
os.environ.setdefault('MPLBACKEND', 'Agg')
import matplotlib  # noqa: E402

matplotlib.use('Agg', force=True)

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.papers._common.paper_figures_ext import (  # noqa: E402
    coefplot_from_esttab_df,
    event_study_plot,
    forest_plot_from_esttab_df,
)
from news_process.papers._common.stata_postprocess import parse_esttab_csv  # noqa: E402

_FIXTURE_CSV = """,M1,M2,M3
llm_vote_tone_full,0.123***,0.150**,0.180***
,(0.034),(0.062),(0.045)
peer_compete_idx,,-0.025,-0.030*
,,(0.018),(0.017)
ln_news_coverage,0.001,0.002*,-0.001
,(0.001),(0.001),(0.001)
benefit_mean_full,0.075**,0.068*,0.080**
,(0.030),(0.034),(0.032)
peer_tone_lag1_full,0.090***,0.110**,0.105***
,(0.025),(0.045),(0.030)
strat_diff_n5,0.045*,0.052**,0.060**
,(0.024),(0.025),(0.027)
N,164,164,164
r2,0.45,0.52,0.61
"""


@pytest.fixture
def fixture_df(tmp_path):
    csv = tmp_path / 'fixture.csv'
    csv.write_text(_FIXTURE_CSV, encoding='utf-8')
    return parse_esttab_csv(csv)


# ============================================================================
# 1. coefplot
# ============================================================================


def test_coefplot_creates_pdf(fixture_df, tmp_path):
    out = tmp_path / 'coef.pdf'
    result = coefplot_from_esttab_df(
        fixture_df,
        variables=['llm_vote_tone_full', 'peer_compete_idx'],
        output_path=out,
        title='Test',
    )
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 1000


def test_coefplot_missing_variable_raises(fixture_df, tmp_path):
    out = tmp_path / 'coef.pdf'
    with pytest.raises(KeyError):
        coefplot_from_esttab_df(
            fixture_df,
            variables=['nonexistent_variable'],
            output_path=out,
        )


def test_coefplot_with_explicit_models(fixture_df, tmp_path):
    out = tmp_path / 'coef.pdf'
    coefplot_from_esttab_df(
        fixture_df, variables=['llm_vote_tone_full'],
        models=['M1', 'M3'],  # skip M2
        output_path=out,
    )
    assert out.exists()


# ============================================================================
# 2. forest plot
# ============================================================================


def test_forest_creates_pdf(fixture_df, tmp_path):
    out = tmp_path / 'forest.pdf'
    result = forest_plot_from_esttab_df(
        fixture_df, variable='llm_vote_tone_full',
        output_path=out, title='Forest test',
    )
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 1000


def test_forest_unknown_variable_raises(fixture_df, tmp_path):
    with pytest.raises(KeyError):
        forest_plot_from_esttab_df(
            fixture_df, variable='nonexistent',
            output_path=tmp_path / 'fail.pdf',
        )


# ============================================================================
# 3. event_study
# ============================================================================


def test_event_study_creates_pdf(tmp_path):
    out = tmp_path / 'es.pdf'
    result = event_study_plot(
        periods=[-3, -2, -1, 0, 1, 2, 3],
        coefficients=[0.01, 0.02, 0.0, 0.15, 0.18, 0.20, 0.17],
        standard_errors=[0.05, 0.04, 0.0, 0.05, 0.06, 0.07, 0.06],
        output_path=out,
    )
    assert result == out
    assert out.exists()
    assert out.stat().st_size > 1000


def test_event_study_without_se(tmp_path):
    out = tmp_path / 'es_no_se.pdf'
    event_study_plot(
        periods=[-2, -1, 0, 1, 2],
        coefficients=[0.0, 0.0, 0.1, 0.15, 0.18],
        standard_errors=None,
        output_path=out,
    )
    assert out.exists()


# ============================================================================
# 4. Paper-level figure functions (4 papers × 2 new figs = 8 cases)
# ============================================================================


def _make_paper_config(paper_id: str, base: Path):
    """Construct a PaperConfig pointing at tmp dirs for testing."""
    from news_process.papers._common import paper_config
    return paper_config.PaperConfig(
        paper_id=paper_id,
        project_root=base,
        panel_dir=base / 'panel',
        output_dir=base / 'output',
        do_dir=base / 'do',
        drafts_dir=base / 'drafts',
        config={'paths': {'output_dir': str(base / 'panel')}},
    )


def _drop_fixture(pc, csv_basename: str):
    """Drop the standard fixture CSV at pc.output_dir / tables / <name>."""
    target_dir = pc.output_dir / 'tables'
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / csv_basename).write_text(_FIXTURE_CSV, encoding='utf-8')


@pytest.mark.parametrize('paper_id,fig_module,fn_name,csv_basename', [
    ('llm_peer',           'news_process.papers.llm_peer.figures',
     'plot_main_iv_coefplot',         'table2_main_iv_2sls.csv'),
    ('llm_peer',           'news_process.papers.llm_peer.figures',
     'plot_heterogeneity_forest',     'table4_heterogeneity.csv'),
    ('benefit_society',    'news_process.papers.benefit_society.figures',
     'plot_main_coefplot',            'table2_main.csv'),
    ('brokerage_network',  'news_process.papers.brokerage_network.figures',
     'plot_main_iv_coefplot',         'table2_main_iv_2sls.csv'),
    ('strategic_diff',     'news_process.papers.strategic_diff.figures',
     'plot_main_coefplot',            'table2_main.csv'),
])
def test_paper_figure_renders_with_fixture(paper_id, fig_module, fn_name,
                                           csv_basename, tmp_path):
    """End-to-end: drop fixture CSV → call paper figure fn → verify PDF written."""
    import importlib

    pc = _make_paper_config(paper_id, tmp_path)
    _drop_fixture(pc, csv_basename)

    mod = importlib.import_module(fig_module)
    fn = getattr(mod, fn_name)
    out = fn(pc)
    assert isinstance(out, Path)
    assert out.exists(), f"{paper_id}/{fn_name} did not produce {out}"
    assert out.stat().st_size > 500


@pytest.mark.parametrize('paper_id,fig_module,fn_name', [
    ('llm_peer',          'news_process.papers.llm_peer.figures',          'plot_main_iv_coefplot'),
    ('llm_peer',          'news_process.papers.llm_peer.figures',          'plot_heterogeneity_forest'),
    ('benefit_society',   'news_process.papers.benefit_society.figures',   'plot_main_coefplot'),
    ('benefit_society',   'news_process.papers.benefit_society.figures',   'plot_mechanism_forest'),
    ('brokerage_network', 'news_process.papers.brokerage_network.figures', 'plot_main_iv_coefplot'),
    ('brokerage_network', 'news_process.papers.brokerage_network.figures', 'plot_policy_centrality_forest'),
    ('strategic_diff',    'news_process.papers.strategic_diff.figures',    'plot_main_coefplot'),
    ('strategic_diff',    'news_process.papers.strategic_diff.figures',    'plot_n_sensitivity_coefplot'),
])
def test_paper_figure_raises_when_csv_missing(paper_id, fig_module, fn_name, tmp_path):
    """Without the fixture CSV, the figure fn must raise FileNotFoundError."""
    import importlib

    pc = _make_paper_config(paper_id, tmp_path)
    mod = importlib.import_module(fig_module)
    fn = getattr(mod, fn_name)
    with pytest.raises(FileNotFoundError):
        fn(pc)


# ---------------------------------------------------------------------------
# quality-hardening Round 28 (2026-05-27): paper_figures_ext 94.92% → ~100%
# missing 70-73 (_to_value_se numeric scalar + TypeError fallback) + 265 (title)
# ---------------------------------------------------------------------------


def test_to_value_se_handles_numeric_scalar():
    """_to_value_se 接受 int/float scalar → (float, None) (lines 70-71)."""
    from news_process.papers._common.paper_figures_ext import _to_value_se
    v, se = _to_value_se(3.14)
    assert v == 3.14
    assert se is None
    v2, se2 = _to_value_se(42)
    assert v2 == 42.0
    assert se2 is None


def test_to_value_se_handles_unconvertible_input():
    """_to_value_se 对 string/list 等不可 float-cast → (nan, None) (lines 72-73)."""
    import math

    from news_process.papers._common.paper_figures_ext import _to_value_se
    v, se = _to_value_se("not_a_number")
    assert math.isnan(v)
    assert se is None
    v2, se2 = _to_value_se([1, 2, 3])
    assert math.isnan(v2)


def test_to_value_se_handles_none():
    """_to_value_se(None) → (nan, None) (lines 66-67)."""
    import math

    from news_process.papers._common.paper_figures_ext import _to_value_se
    v, se = _to_value_se(None)
    assert math.isnan(v)
    assert se is None


def test_event_study_plot_with_explicit_title(tmp_path):
    """event_study_plot title 非空 → ax.set_title (line 265)."""
    from news_process.papers._common.paper_figures_ext import event_study_plot
    out = tmp_path / 'event_study_titled.pdf'
    result = event_study_plot(
        periods=[-2, -1, 0, 1, 2],
        coefficients=[0.0, 0.05, 0.1, 0.2, 0.15],
        standard_errors=[0.02, 0.02, 0.02, 0.03, 0.025],
        output_path=out,
        title='Event Study Test Title',  # 触发 line 264-265
    )
    assert result.exists()
