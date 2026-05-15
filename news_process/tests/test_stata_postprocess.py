"""tests/test_stata_postprocess.py — esttab CSV postprocess tests.

P2.4 (plan-r3 derivative-paper extension, 2026-05-15)

Covers:
1. parse_esttab_csv on representative fixtures (3-star, 2-star, 1-star, no-star)
2. Coefficient namedtuple basic invariants
3. Markdown rendering correctness
4. LaTeX booktabs structural correctness
5. Footer stats (N, r2, F) parsed as no-SE entries
6. Error path: missing file → FileNotFoundError
7. read_paper_esttab — path resolution + propagation of FileNotFoundError
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.papers._common.stata_postprocess import (  # noqa: E402
    Coefficient,
    esttab_csv_to_latex,
    esttab_csv_to_markdown,
    parse_esttab_csv,
    read_paper_esttab,
    to_latex_booktabs,
    to_markdown_table,
)

# ============================================================================
# Fixture: a minimal esttab CSV with mixed star levels + footer stats
# ============================================================================

_FIXTURE_CSV = """,M1,M2,M3
llm_vote_tone_full,0.123***,0.150**,0.180***
,(0.034),(0.062),(0.045)
peer_compete_idx,,-0.025,-0.030*
,,(0.018),(0.017)
ln_news_coverage,0.001,0.002*,-0.001
,(0.001),(0.001),(0.001)
N,164,164,164
r2,0.45,0.52,0.61
F,5.32,7.18,9.04
"""


@pytest.fixture
def fixture_csv(tmp_path):
    p = tmp_path / 'table2_sample.csv'
    p.write_text(_FIXTURE_CSV, encoding='utf-8')
    return p


# ============================================================================
# 1. Parser tests
# ============================================================================


def test_parse_returns_dataframe(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    assert df.shape[1] == 3, "expected 3 model columns"
    assert df.shape[0] >= 4, "expected at least 4 variable rows (3 vars + footer)"


def test_parse_columns_named_correctly(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    assert list(df.columns) == ['M1', 'M2', 'M3']


def test_parse_index_contains_variables(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    for v in ['llm_vote_tone_full', 'peer_compete_idx', 'ln_news_coverage']:
        assert v in df.index, f"variable {v!r} not in parsed index"


def test_parse_three_star_coefficient(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    coef = df.loc['llm_vote_tone_full', 'M1']
    assert isinstance(coef, Coefficient)
    assert coef.value == pytest.approx(0.123)
    assert coef.se == pytest.approx(0.034)
    assert coef.stars == 3


def test_parse_two_star_coefficient(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    coef = df.loc['llm_vote_tone_full', 'M2']
    assert coef.stars == 2
    assert coef.se == pytest.approx(0.062)


def test_parse_one_star_coefficient(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    coef = df.loc['peer_compete_idx', 'M3']
    assert coef.stars == 1
    assert coef.value == pytest.approx(-0.030)


def test_parse_no_star_coefficient(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    coef = df.loc['peer_compete_idx', 'M2']
    assert coef.stars == 0
    assert coef.value == pytest.approx(-0.025)


def test_parse_missing_cell_is_none(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    assert df.loc['peer_compete_idx', 'M1'] is None


def test_parse_footer_stats(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    for stat in ['N', 'r2', 'F']:
        assert stat in df.index
        coef = df.loc[stat, 'M1']
        assert coef.se is None, f"{stat} should have no SE"
        assert coef.stars == 0


def test_parse_n_value(fixture_csv):
    df = parse_esttab_csv(fixture_csv)
    assert df.loc['N', 'M1'].value == pytest.approx(164)


def test_parse_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        parse_esttab_csv('/nonexistent/path/foo.csv')


# ============================================================================
# 2. Coefficient namedtuple
# ============================================================================


def test_coefficient_as_string_three_stars():
    c = Coefficient(value=0.123, se=0.034, stars=3)
    assert c.as_string() == '0.123*** (0.034)'


def test_coefficient_as_string_no_se():
    c = Coefficient(value=164.0, se=None, stars=0)
    assert c.as_string() == '164.000'


# ============================================================================
# 3. Markdown rendering
# ============================================================================


def test_markdown_has_header_row(fixture_csv):
    md = to_markdown_table(parse_esttab_csv(fixture_csv))
    assert '| Variable | M1 | M2 | M3 |' in md


def test_markdown_has_stars(fixture_csv):
    md = to_markdown_table(parse_esttab_csv(fixture_csv))
    assert '0.123***' in md
    assert '0.150**' in md
    assert '-0.030*' in md


def test_markdown_has_parenthesized_se(fixture_csv):
    md = to_markdown_table(parse_esttab_csv(fixture_csv))
    assert '(0.034)' in md
    assert '(0.062)' in md


def test_markdown_footer_separator(fixture_csv):
    """Footer stats (N/r2/F) should appear under a horizontal-rule separator."""
    md = to_markdown_table(parse_esttab_csv(fixture_csv), stats_separator=True)
    # Two HR-line markers expected (one after header, one before stats)
    hr_count = sum(1 for line in md.splitlines() if line.startswith('|---|'))
    assert hr_count >= 2, f"expected >= 2 HR rules, got {hr_count}"


def test_esttab_csv_to_markdown_shortcut(fixture_csv):
    md = esttab_csv_to_markdown(fixture_csv)
    assert '0.123***' in md


# ============================================================================
# 4. LaTeX rendering
# ============================================================================


def test_latex_has_booktabs_structure(fixture_csv):
    tex = to_latex_booktabs(parse_esttab_csv(fixture_csv))
    assert r'\toprule' in tex
    assert r'\midrule' in tex
    assert r'\bottomrule' in tex


def test_latex_has_caption_and_label(fixture_csv):
    tex = to_latex_booktabs(parse_esttab_csv(fixture_csv),
                            caption='Main IV 2SLS', label='tab:main')
    assert r'\caption{Main IV 2SLS}' in tex
    assert r'\label{tab:main}' in tex


def test_latex_stars_in_superscript(fixture_csv):
    tex = to_latex_booktabs(parse_esttab_csv(fixture_csv))
    assert '$^{***}$' in tex
    assert '$^{**}$' in tex


def test_latex_escapes_underscore_in_var(fixture_csv):
    tex = to_latex_booktabs(parse_esttab_csv(fixture_csv))
    assert r'llm\_vote\_tone\_full' in tex


def test_esttab_csv_to_latex_shortcut(fixture_csv):
    tex = esttab_csv_to_latex(fixture_csv)
    assert r'\begin{tabular}' in tex


# ============================================================================
# 5. read_paper_esttab — paper-aware path resolution
# ============================================================================


def test_read_paper_esttab_raises_for_missing_csv(tmp_path, monkeypatch):
    """If the expected CSV is missing under the paper's output_dir, raise."""
    from news_process.papers._common import paper_config

    # Build a custom PaperConfig pointing at tmp_path
    pc = paper_config.PaperConfig(
        paper_id='llm_peer',
        project_root=tmp_path,
        panel_dir=tmp_path / 'panel',
        output_dir=tmp_path / 'output',
        do_dir=tmp_path / 'do',
        drafts_dir=tmp_path / 'drafts',
        config={'paths': {'output_dir': str(tmp_path / 'panel')}},
    )
    (pc.output_dir / 'tables').mkdir(parents=True, exist_ok=True)

    with pytest.raises(FileNotFoundError, match='esttab CSV not found'):
        read_paper_esttab('llm_peer', 'table2.csv', paper_config=pc)


def test_read_paper_esttab_returns_df_for_existing_csv(tmp_path, fixture_csv):
    """Drop the fixture CSV into the paper's expected location → parse succeeds."""
    from news_process.papers._common import paper_config

    pc = paper_config.PaperConfig(
        paper_id='llm_peer',
        project_root=tmp_path,
        panel_dir=tmp_path / 'panel',
        output_dir=tmp_path / 'output',
        do_dir=tmp_path / 'do',
        drafts_dir=tmp_path / 'drafts',
        config={'paths': {'output_dir': str(tmp_path / 'panel')}},
    )
    target_dir = pc.output_dir / 'tables'
    target_dir.mkdir(parents=True, exist_ok=True)
    # Copy fixture into target
    (target_dir / 'table2.csv').write_text(_FIXTURE_CSV, encoding='utf-8')

    df = read_paper_esttab('llm_peer', 'table2.csv', paper_config=pc)
    assert df.shape[1] == 3
    assert 'llm_vote_tone_full' in df.index


# ============================================================================
# 6. Paper-level builders (build_tableN per paper) — error path
# ============================================================================

@pytest.mark.parametrize('paper_module,fn_name', [
    ('news_process.papers.llm_peer.tables', 'build_table2_main'),
    ('news_process.papers.llm_peer.tables', 'build_table3_cutoff'),
    ('news_process.papers.llm_peer.tables', 'build_table4_heterogeneity'),
    ('news_process.papers.llm_peer.tables', 'build_table5_robustness'),
    ('news_process.papers.benefit_society.tables', 'build_table2_main'),
    ('news_process.papers.benefit_society.tables', 'build_table3_mechanism'),
    ('news_process.papers.benefit_society.tables', 'build_table4_heterogeneity'),
    ('news_process.papers.benefit_society.tables', 'build_table5_robustness'),
    ('news_process.papers.brokerage_network.tables', 'build_table2_main'),
    ('news_process.papers.brokerage_network.tables', 'build_table3_mechanism'),
    ('news_process.papers.brokerage_network.tables', 'build_table4_heterogeneity'),
    ('news_process.papers.brokerage_network.tables', 'build_table5_robustness'),
    ('news_process.papers.strategic_diff.tables', 'build_table2_main'),
    ('news_process.papers.strategic_diff.tables', 'build_table3_mechanism'),
    ('news_process.papers.strategic_diff.tables', 'build_table4_heterogeneity'),
    ('news_process.papers.strategic_diff.tables', 'build_table5_robustness'),
])
def test_paper_builders_raise_when_csv_missing(paper_module, fn_name, tmp_path):
    """Each paper's build_tableN_X must raise FileNotFoundError when CSV absent."""
    import importlib

    from news_process.papers._common import paper_config

    paper_id = paper_module.split('.')[2]
    mod = importlib.import_module(paper_module)
    fn = getattr(mod, fn_name)

    pc = paper_config.PaperConfig(
        paper_id=paper_id,
        project_root=tmp_path,
        panel_dir=tmp_path / 'panel',
        output_dir=tmp_path / 'output',
        do_dir=tmp_path / 'do',
        drafts_dir=tmp_path / 'drafts',
        config={'paths': {'output_dir': str(tmp_path / 'panel')}},
    )
    with pytest.raises(FileNotFoundError):
        fn(pc)
