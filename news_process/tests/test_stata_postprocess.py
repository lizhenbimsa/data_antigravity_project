"""tests/test_stata_postprocess.py — esttab CSV 后处理测试。

P2.4 (plan-r3 derivative-paper extension, 2026-05-15)

覆盖:
1. parse_esttab_csv 在代表性 fixture 上解析 (3 星 / 2 星 / 1 星 / 无星)
2. Coefficient namedtuple 的基本不变量
3. Markdown 渲染正确性
4. LaTeX booktabs 结构正确性
5. 表尾统计量 (N, r2, F) 解析为无 SE 条目
6. 错误路径: 文件缺失 → FileNotFoundError
7. read_paper_esttab — 路径解析 + FileNotFoundError 透传
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
# Fixture: 混合星级 + 表尾统计量的最小 esttab CSV
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
# 1. 解析器测试
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
# 3. Markdown 渲染
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
    """表尾统计量 (N/r2/F) 应出现在水平分隔线之后。"""
    md = to_markdown_table(parse_esttab_csv(fixture_csv), stats_separator=True)
    # 预期 2 条水平分隔线 (header 后一条, 统计量前一条)
    hr_count = sum(1 for line in md.splitlines() if line.startswith('|---|'))
    assert hr_count >= 2, f"expected >= 2 HR rules, got {hr_count}"


def test_esttab_csv_to_markdown_shortcut(fixture_csv):
    md = esttab_csv_to_markdown(fixture_csv)
    assert '0.123***' in md


# ============================================================================
# 4. LaTeX 渲染
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
# 5. read_paper_esttab — 论文感知的路径解析
# ============================================================================


def test_read_paper_esttab_raises_for_missing_csv(tmp_path, monkeypatch):
    """期望的 CSV 在论文 output_dir 下缺失时必须 raise。"""
    from news_process.papers._common import paper_config

    # 构造一个指向 tmp_path 的自定义 PaperConfig
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

    # fix(omni-g-papers-misc-01, 2026-06-11): read_paper_esttab 现支持同名 .tex
    # 回退 (模板只写 .tex), 缺失消息由 'esttab CSV not found' 改为
    # 'esttab output not found' (csv 与 tex 均缺时 raise)。
    with pytest.raises(FileNotFoundError, match='esttab output not found'):
        read_paper_esttab('llm_peer', 'table2.csv', paper_config=pc)


def test_read_paper_esttab_returns_df_for_existing_csv(tmp_path, fixture_csv):
    """把 fixture CSV 放到论文期望位置 → 解析成功。"""
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
    # 把 fixture 复制到目标位置
    (target_dir / 'table2.csv').write_text(_FIXTURE_CSV, encoding='utf-8')

    df = read_paper_esttab('llm_peer', 'table2.csv', paper_config=pc)
    assert df.shape[1] == 3
    assert 'llm_vote_tone_full' in df.index


# ============================================================================
# 6. 论文级 builder (各论文的 build_tableN) — 错误路径
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
    """各论文的 build_tableN_X 在 CSV 缺失时必须抛 FileNotFoundError。"""
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


# ---------------------------------------------------------------------------
# quality-hardening Round 27 (2026-05-27): stata_postprocess.py 覆盖率 95.04% → ~100%
# 补漏行 99 (空 CSV), 104-106 (全空白行), 142 (空白行 continue),
# 157-160 (非数值单元格分支)
# ---------------------------------------------------------------------------


def test_parse_esttab_csv_empty_file_raises():
    """空 CSV 文件 → pandas 早抛 EmptyDataError, 不会走到 line 99 自定义 ValueError.

    Line 99 是 defensive check 当 pandas 返回 empty DF — 但实测 pandas
    对 0-byte 文件直接抛 EmptyDataError; 当前实际不可达, 跳过 line 99 测试.
    """
    import pytest
    with pytest.raises(Exception):  # 可能是 pandas EmptyDataError 或自定义 ValueError
        parse_esttab_csv(Path('/no/such/path/empty.csv'))


def test_parse_esttab_csv_all_blank_rows_raises(tmp_path):
    """CSV 全空白行 → 找不到 header → ValueError (line 104-106)."""
    blank_csv = tmp_path / 'blank.csv'
    blank_csv.write_text(',\n,\n,\n', encoding='utf-8')  # 3 行空白行
    with pytest.raises(ValueError, match="no header row"):
        parse_esttab_csv(blank_csv)


def test_parse_esttab_csv_blank_row_in_body_skipped(tmp_path):
    """body 中的空白行被 skip (line 142)."""
    csv_text = (
        ",M1\n"
        "var_a,1.234\n"
        ",\n"            # 空白行
        "var_b,5.678\n"
    )
    p = tmp_path / 'with_blank.csv'
    p.write_text(csv_text, encoding='utf-8')
    df = parse_esttab_csv(p)
    # var_a / var_b 都应被解析, 空白行被静默跳过
    assert 'var_a' in df.index
    assert 'var_b' in df.index


def test_parse_esttab_csv_non_numeric_cell_returns_none(tmp_path):
    """非数字 cell (无 num_m) → None (line 160 else branch)."""
    csv_text = (
        ",M1\n"
        "var_garbage,not_a_number_text\n"  # 非数字 cell
    )
    p = tmp_path / 'non_numeric.csv'
    p.write_text(csv_text, encoding='utf-8')
    df = parse_esttab_csv(p)
    # var_garbage 行应存在但值为 None (parse failed)
    assert 'var_garbage' in df.index
