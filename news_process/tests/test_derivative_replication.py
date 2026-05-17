"""tests/test_derivative_replication.py — Derivative paper replication tests.

P1.4 (plan-r3 derivative-paper extension, 2026-05-15)

Tests for ``news_process.papers._common.derivative_replication`` covering 4
derivative papers (benefit_society / brokerage_network / strategic_diff /
llm_peer). The main-paper bank_fintech_tone path is covered by the existing
``test_stata_templates.py`` suite (73 tests), which this file does NOT
duplicate.

Test surface
------------
1. Module imports cleanly (no circular import with ``stata_runner``).
2. ``_DERIVATIVE_PAPER_IDS`` contains exactly the 4 expected papers.
3. ``_PAPER_DEFAULTS`` is well-formed for each paper:
   - Required Tier 2 keys present: PAPER_ID / MAIN_DV / CONTROLS / CLUSTER_VAR / HET_VAR
   - PAPER_ID self-consistent
4. ``get_paper_defaults`` raises on unknown paper_id and returns dict-copy.
5. ``build_derivative_replication_package`` end-to-end for each paper:
   - Template dir exists at ``stata_templates/<paper_id>/``
   - Generates >= 7 .do files (Table 1 + Table 2 + Table 3 + Table 4 + Table 5 + Figure 1 + Master + Data prep, but 7 is the floor for resilient testing)
   - Zero ``{{...}}`` placeholder residue in any .do file
   - README.md exists with paper_id appendix
6. ``build_derivative_replication_package`` raises on:
   - Unknown paper_id
   - Overrides referencing unknown placeholder keys
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))

from news_process.papers._common.derivative_replication import (  # noqa: E402
    _DERIVATIVE_PAPER_IDS,
    _PAPER_DEFAULTS,
    build_derivative_replication_package,
    get_paper_defaults,
    is_derivative_paper,
)

# ============================================================================
# Constants — invariant for derivative papers
# ============================================================================

# RR9-1: split into legacy 4 + B-route 3 — legacy-specific invariants
# (ROA outcome, 11_table2 filename) only apply to the legacy 4.
EXPECTED_DERIVATIVE_PAPERS_LEGACY = frozenset({
    'benefit_society',
    'brokerage_network',
    'strategic_diff',
    'llm_peer',
})

EXPECTED_DERIVATIVE_PAPERS_B_ROUTE = frozenset({
    'bank_fintech_attention',
    'bank_fintech_substance',
    'bank_fintech_locus',
})

EXPECTED_DERIVATIVE_PAPERS = EXPECTED_DERIVATIVE_PAPERS_LEGACY | EXPECTED_DERIVATIVE_PAPERS_B_ROUTE

REQUIRED_TIER2_KEYS = frozenset({
    'PAPER_ID', 'MAIN_DV', 'CONTROLS', 'CLUSTER_VAR', 'HET_VAR',
})

# Templates expected at a minimum across all 4 papers.
MINIMUM_EXPECTED_DO_FILES = 7

# ============================================================================
# 1. Module-level invariants
# ============================================================================


def test_derivative_paper_ids_match_expected():
    assert set(_DERIVATIVE_PAPER_IDS) == set(EXPECTED_DERIVATIVE_PAPERS), (
        f"derivative_paper_ids mismatch. Got {sorted(_DERIVATIVE_PAPER_IDS)}, "
        f"expected {sorted(EXPECTED_DERIVATIVE_PAPERS)}"
    )


def test_is_derivative_paper_main_excluded():
    assert is_derivative_paper('bank_fintech_tone') is False
    assert is_derivative_paper('benefit_society') is True
    assert is_derivative_paper('unknown_paper') is False


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS))
def test_paper_defaults_has_required_tier2_keys(paper_id):
    defaults = _PAPER_DEFAULTS[paper_id]
    missing = REQUIRED_TIER2_KEYS - set(defaults.keys())
    assert not missing, f"{paper_id} missing Tier 2 keys: {sorted(missing)}"


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS))
def test_paper_defaults_paper_id_self_consistent(paper_id):
    assert _PAPER_DEFAULTS[paper_id]['PAPER_ID'] == paper_id


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS_LEGACY))
def test_paper_defaults_main_dv_is_roa(paper_id):
    """Legacy 4 衍生 paper convention: ROA is the canonical DV.

    RR9-1: B-route 3 new papers use paper-specific outcome.primary
    (ln_fintech_investment / long_run_roa_change_3yr / car_5day_window) per spec
    and are excluded from this legacy invariant."""
    assert _PAPER_DEFAULTS[paper_id]['MAIN_DV'] == 'ROA'


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS_B_ROUTE))
def test_b_route_paper_defaults_main_dv_from_spec(paper_id):
    """RR9-1: 3 new B-route paper defaults align with paper_spec.yaml outcome.primary."""
    from news_process.papers._common.paper_registry import get_spec
    spec = get_spec(paper_id)
    expected_dv = spec.raw['outcome']['primary']
    assert _PAPER_DEFAULTS[paper_id]['MAIN_DV'] == expected_dv, (
        f"{paper_id}: defaults MAIN_DV={_PAPER_DEFAULTS[paper_id]['MAIN_DV']!r} "
        f"differs from spec.outcome.primary={expected_dv!r} — drift detected"
    )


def test_brokerage_network_clusters_at_province():
    """brokerage_network uses prov_id, not bank_id (Cameron-Miller 2015 rationale)."""
    assert _PAPER_DEFAULTS['brokerage_network']['CLUSTER_VAR'] == 'prov_id'


def test_other_papers_cluster_at_bank():
    """Non-brokerage_network derivative papers cluster at bank_id."""
    for pid in ('benefit_society', 'strategic_diff', 'llm_peer'):
        assert _PAPER_DEFAULTS[pid]['CLUSTER_VAR'] == 'bank_id', (
            f"{pid} expected CLUSTER_VAR='bank_id'"
        )


# ============================================================================
# 2. get_paper_defaults — accessor invariants
# ============================================================================


def test_get_paper_defaults_returns_copy():
    """Mutating the returned dict must not affect module state."""
    d = get_paper_defaults('llm_peer')
    d['PAPER_ID'] = 'mutated'
    assert _PAPER_DEFAULTS['llm_peer']['PAPER_ID'] == 'llm_peer'


def test_get_paper_defaults_rejects_unknown():
    with pytest.raises(ValueError, match='Unknown derivative paper_id'):
        get_paper_defaults('bank_fintech_tone')  # main paper rejected
    with pytest.raises(ValueError, match='Unknown derivative paper_id'):
        get_paper_defaults('no_such_paper')


# ============================================================================
# 3. build_derivative_replication_package — end-to-end per paper
# ============================================================================


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS))
def test_build_package_per_paper(paper_id, tmp_path):
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    assert pkg.is_dir()
    assert pkg.name == f'replication_v3.2.0_{paper_id}'

    # Expected subdirs
    assert (pkg / 'code').is_dir()
    assert (pkg / 'data').is_dir()
    assert (pkg / 'output' / 'tables').is_dir()
    assert (pkg / 'output' / 'figures').is_dir()


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS))
def test_build_generates_enough_do_files(paper_id, tmp_path):
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    do_files = sorted((pkg / 'code').glob('*.do'))
    assert len(do_files) >= MINIMUM_EXPECTED_DO_FILES, (
        f"{paper_id}: only {len(do_files)} .do files (expected >= {MINIMUM_EXPECTED_DO_FILES})"
    )


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS))
def test_build_no_placeholder_residue(paper_id, tmp_path):
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    residue: list[str] = []
    for do_file in (pkg / 'code').glob('*.do'):
        content = do_file.read_text(encoding='utf-8')
        if '{{' in content or '}}' in content:
            residue.append(do_file.name)
    assert not residue, f"{paper_id}: placeholder residue in {residue}"


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS))
def test_build_readme_contains_paper_id(paper_id, tmp_path):
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    readme = pkg / 'README.md'
    assert readme.exists()
    content = readme.read_text(encoding='utf-8')
    assert paper_id in content
    assert 'Generated at' in content
    assert 'MAIN_DV' in content


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS))
def test_build_templates_use_reghdfe(paper_id, tmp_path):
    """All derivative papers use reghdfe for the main regression.

    RR9-1: legacy 4 papers name main regression as 11_table2*.do;
    B-route 3 new papers use 15_<paper>_main_regression.do (per plan §5.5.2)."""
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    code_dir = pkg / 'code'
    main_table_files = (
        list(code_dir.glob('11_table2*.do'))                   # legacy 衍生
        + list(code_dir.glob('15_*_main_regression.do'))        # B-route new
    )
    assert main_table_files, (
        f"{paper_id}: no main regression file matching 11_table2*.do "
        f"or 15_*_main_regression.do"
    )
    content = main_table_files[0].read_text(encoding='utf-8')
    assert 'reghdfe' in content, (
        f"{paper_id}: {main_table_files[0].name} lacks reghdfe"
    )


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS))
def test_build_master_references_subtemplates(paper_id, tmp_path):
    """00_master.do must `do` at least 5 subtemplates."""
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    master = pkg / 'code' / '00_master.do'
    assert master.exists()
    content = master.read_text(encoding='utf-8')
    # Must reference data_prep + table1 + table2 + table3/figure
    do_references = content.count('do 0') + content.count('do 1') + content.count('do 2') + content.count('do 3')
    assert do_references >= 5, f"{paper_id}: master.do has only {do_references} `do <N>` calls"


# ============================================================================
# 4. Error paths
# ============================================================================


def test_build_unknown_paper_id_raises():
    with tempfile.TemporaryDirectory() as tmp:
        with pytest.raises(ValueError, match='Unknown derivative paper_id'):
            build_derivative_replication_package('bank_fintech_tone', output_root=tmp)
        with pytest.raises(ValueError, match='Unknown derivative paper_id'):
            build_derivative_replication_package('no_such_paper', output_root=tmp)


def test_build_rejects_unknown_override_key(tmp_path):
    with pytest.raises(ValueError, match='not in paper defaults'):
        build_derivative_replication_package(
            'llm_peer',
            overrides={'TOTALLY_UNKNOWN_KEY': 'foo'},
            output_root=tmp_path,
        )


def test_build_accepts_known_override(tmp_path):
    """Override of an existing key should succeed; verify MAIN_DV swap propagates."""
    pkg = build_derivative_replication_package(
        'llm_peer',
        overrides={'MAIN_DV': 'Tobin_Q'},
        output_root=tmp_path,
    )
    # The main table should reference Tobin_Q_w (winsorized).
    main_tex = (pkg / 'code' / '11_table2_main_iv_2sls.do').read_text(encoding='utf-8')
    assert 'Tobin_Q_w' in main_tex, (
        "MAIN_DV override did not propagate to 11_table2_main_iv_2sls.do"
    )


def test_build_missing_template_dir_raises(tmp_path):
    fake_dir = tmp_path / 'no_such_template_dir'
    with pytest.raises(FileNotFoundError, match='Template dir not found'):
        build_derivative_replication_package(
            'llm_peer',
            output_root=tmp_path,
            template_dir=fake_dir,
        )


# ============================================================================
# 5. Cross-paper invariants
# ============================================================================


def test_all_four_papers_produce_uniform_subdirs(tmp_path):
    """Every derivative package must have code/, data/, output/{tables,figures}/."""
    expected_subdirs = ['code', 'data', 'output/tables', 'output/figures']
    for paper_id in sorted(EXPECTED_DERIVATIVE_PAPERS):
        pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
        for sub in expected_subdirs:
            assert (pkg / sub).is_dir(), f"{paper_id}/{sub} missing"


def test_all_four_papers_have_winsor_in_data_prep(tmp_path):
    """01_data_prep.do for each paper performs winsorize on MAIN_DV (per project convention)."""
    for paper_id in sorted(EXPECTED_DERIVATIVE_PAPERS):
        pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
        data_prep = pkg / 'code' / '01_data_prep.do'
        assert data_prep.exists(), f"{paper_id}: 01_data_prep.do missing"
        content = data_prep.read_text(encoding='utf-8')
        assert 'winsor' in content.lower(), f"{paper_id}: 01_data_prep.do missing winsorize"
