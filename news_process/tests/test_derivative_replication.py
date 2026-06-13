"""tests/test_derivative_replication.py — 衍生 paper replication 测试.

P1.4 (plan-r3 derivative-paper extension, 2026-05-15)

``news_process.papers._common.derivative_replication`` 的测试, 覆盖 7 篇衍生
paper (legacy 4: benefit_society / brokerage_network / strategic_diff /
llm_peer; RR9-1 后新增 B-route 3: bank_fintech_attention / substance / locus)。
主线 paper bank_fintech_tone 路径由既有 ``test_stata_templates.py`` 套件覆盖,
本文件不重复。

测试面
------
1. 模块可干净 import (与 ``stata_runner`` 无循环 import)。
2. ``_DERIVATIVE_PAPER_IDS`` 恰好包含预期的衍生 paper 集合。
3. ``_PAPER_DEFAULTS`` 每篇结构良构:
   - 必备 Tier 2 key 齐全: PAPER_ID / MAIN_DV / CONTROLS / CLUSTER_VAR / HET_VAR
   - PAPER_ID 自洽
4. ``get_paper_defaults`` 对未知 paper_id raise, 且返回 dict 副本。
5. ``build_derivative_replication_package`` 逐篇端到端:
   - 模板目录存在于 ``stata_templates/<paper_id>/``
   - 生成 >= 7 个 .do 文件 (Table 1-5 + Figure 1 + Master + Data prep;
     7 是为测试鲁棒性设的下限)
   - 任何 .do 文件中零 ``{{...}}`` 占位符残留
   - README.md 存在且含 paper_id 附录
6. ``build_derivative_replication_package`` 对以下情形 raise:
   - 未知 paper_id
   - overrides 引用未知占位符 key
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
# 常量 — 衍生 paper 的不变式
# ============================================================================

# RR9-1: 拆为 legacy 4 + B-route 3 — legacy 专属不变式
# (ROA outcome, 11_table2 文件名) 仅适用于 legacy 4 篇.
# 2026-06-13 outcome 重定位: legacy 4 中 llm_peer (avg_ft_intensity_full, 主规格
# 重构) 与 strategic_diff (tobin_q, 特许权价值) 的 MAIN_DV 不再是 'ROA' 哨兵,
# 改为与 spec.outcome.primary 动态对齐 (并入下方 SPEC_ALIGNED 检查); ROA 哨兵
# 不变式仅余 benefit_society (PAP v1.0-final 锁定) + brokerage_network。
EXPECTED_DERIVATIVE_PAPERS_LEGACY = frozenset({
    'benefit_society',
    'brokerage_network',
    'strategic_diff',
    'llm_peer',
})

EXPECTED_DERIVATIVE_PAPERS_ROA_SENTINEL = frozenset({
    'benefit_society',
    'brokerage_network',
})

EXPECTED_DERIVATIVE_PAPERS_B_ROUTE = frozenset({
    'bank_fintech_attention',
    'bank_fintech_substance',
    'bank_fintech_locus',
})

# MAIN_DV 须与 paper_spec.yaml outcome.primary 动态对齐的集合 (B-route 3 +
# 2026-06-13 重定位的 legacy 2)。
EXPECTED_DERIVATIVE_PAPERS_SPEC_ALIGNED = EXPECTED_DERIVATIVE_PAPERS_B_ROUTE | frozenset({
    'llm_peer',
    'strategic_diff',
})

EXPECTED_DERIVATIVE_PAPERS = EXPECTED_DERIVATIVE_PAPERS_LEGACY | EXPECTED_DERIVATIVE_PAPERS_B_ROUTE

REQUIRED_TIER2_KEYS = frozenset({
    'PAPER_ID', 'MAIN_DV', 'CONTROLS', 'CLUSTER_VAR', 'HET_VAR',
})

# 所有衍生 paper 至少应生成的 .do 模板数下限.
MINIMUM_EXPECTED_DO_FILES = 7

# ============================================================================
# 1. 模块级不变式
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


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS_ROA_SENTINEL))
def test_paper_defaults_main_dv_is_roa(paper_id):
    """ROA 哨兵 2 篇 (benefit_society / brokerage_network) 约定: ROA 是规范 DV.

    RR9-1 原 legacy 4 篇不变式; 2026-06-13 outcome 重定位后 llm_peer /
    strategic_diff 移入 SPEC_ALIGNED 动态对齐 (见下), 本不变式仅余 2 篇
    (benefit_society 受 PAP v1.0-final 锁定; brokerage_network 维持 roa 主因变量)."""
    assert _PAPER_DEFAULTS[paper_id]['MAIN_DV'] == 'ROA'


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS_SPEC_ALIGNED))
def test_b_route_paper_defaults_main_dv_from_spec(paper_id):
    """RR9-1: spec-aligned 集合 (B-route 3 + 重定位 legacy 2) 的 defaults 须与
    paper_spec.yaml 的 outcome.primary 对齐."""
    from news_process.papers._common.paper_registry import get_spec
    spec = get_spec(paper_id)
    expected_dv = spec.raw['outcome']['primary']
    assert _PAPER_DEFAULTS[paper_id]['MAIN_DV'] == expected_dv, (
        f"{paper_id}: defaults MAIN_DV={_PAPER_DEFAULTS[paper_id]['MAIN_DV']!r} "
        f"differs from spec.outcome.primary={expected_dv!r} — drift detected"
    )


def test_brokerage_network_clusters_at_province():
    """brokerage_network 用 prov_id 而非 bank_id 聚类 (Cameron-Miller 2015 依据)."""
    assert _PAPER_DEFAULTS['brokerage_network']['CLUSTER_VAR'] == 'prov_id'


def test_other_papers_cluster_at_bank():
    """除 brokerage_network 外的 paper 都在 bank_id 上聚类.

    RR12-1: 已扩展覆盖 B-route 3 篇新 paper; brokerage_network 除外
    (依 Cameron-Miller 2015 用 prov_id)."""
    expected_bank_cluster = sorted(EXPECTED_DERIVATIVE_PAPERS - {'brokerage_network'})
    for pid in expected_bank_cluster:
        assert _PAPER_DEFAULTS[pid]['CLUSTER_VAR'] == 'bank_id', (
            f"{pid} expected CLUSTER_VAR='bank_id'"
        )


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS_B_ROUTE))
def test_b_route_paper_defaults_main_treat_from_spec(paper_id):
    """RR12-2: 漂移检测 — defaults[MAIN_TREAT] vs spec.treatment.primary
    (P4 用 primary_pair[0])."""
    from news_process.papers._common.paper_registry import get_spec
    spec = get_spec(paper_id)
    t = spec.raw.get('treatment', {})
    expected_treat = t.get('primary') or (t.get('primary_pair', [''])[0] if t.get('primary_pair') else '')
    assert _PAPER_DEFAULTS[paper_id]['MAIN_TREAT'] == expected_treat, (
        f"{paper_id}: defaults MAIN_TREAT={_PAPER_DEFAULTS[paper_id]['MAIN_TREAT']!r} "
        f"differs from spec.treatment={expected_treat!r} — drift detected"
    )


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS_B_ROUTE))
def test_b_route_paper_defaults_cluster_var_bank_id(paper_id):
    """RR12-2: B-route 3 篇新 paper 均在 bank_id 上聚类 (依 spec 设计)."""
    assert _PAPER_DEFAULTS[paper_id]['CLUSTER_VAR'] == 'bank_id'


# ============================================================================
# 2. get_paper_defaults — 访问器不变式
# ============================================================================


def test_get_paper_defaults_returns_copy():
    """改写返回的 dict 不得影响模块内部状态."""
    d = get_paper_defaults('llm_peer')
    d['PAPER_ID'] = 'mutated'
    assert _PAPER_DEFAULTS['llm_peer']['PAPER_ID'] == 'llm_peer'


def test_get_paper_defaults_rejects_unknown():
    with pytest.raises(ValueError, match='Unknown derivative paper_id'):
        get_paper_defaults('bank_fintech_tone')  # 主线 paper 应被拒绝
    with pytest.raises(ValueError, match='Unknown derivative paper_id'):
        get_paper_defaults('no_such_paper')


# ============================================================================
# 3. build_derivative_replication_package — 逐篇端到端
# ============================================================================


@pytest.mark.parametrize('paper_id', sorted(EXPECTED_DERIVATIVE_PAPERS))
def test_build_package_per_paper(paper_id, tmp_path):
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    assert pkg.is_dir()
    assert pkg.name == f'replication_v3.2.0_{paper_id}'

    # 预期的子目录
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
    """所有衍生 paper 的主回归均用 reghdfe.

    RR9-1: legacy 4 篇主回归文件名为 11_table2*.do;
    B-route 3 篇新 paper 用 15_<paper>_main_regression.do (依 plan §5.5.2)."""
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    code_dir = pkg / 'code'
    main_table_files = (
        list(code_dir.glob('11_table2*.do'))                   # legacy 衍生
        + list(code_dir.glob('15_*_main_regression.do'))        # B-route 新 paper
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
    """00_master.do 必须 `do` 至少 5 个子模板."""
    pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
    master = pkg / 'code' / '00_master.do'
    assert master.exists()
    content = master.read_text(encoding='utf-8')
    # 必须引用 data_prep + table1 + table2 + table3/figure
    do_references = content.count('do 0') + content.count('do 1') + content.count('do 2') + content.count('do 3')
    assert do_references >= 5, f"{paper_id}: master.do has only {do_references} `do <N>` calls"


# ============================================================================
# 4. 错误路径
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
    """覆盖已存在的 key 应成功; 验证 MAIN_DV 替换会向下传播."""
    pkg = build_derivative_replication_package(
        'llm_peer',
        overrides={'MAIN_DV': 'Tobin_Q'},
        output_root=tmp_path,
    )
    # 主表应引用 Tobin_Q_w (winsorize 后的列).
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
# 5. 跨 paper 不变式
# ============================================================================


def test_all_four_papers_produce_uniform_subdirs(tmp_path):
    """每个衍生 replication 包都必须有 code/, data/, output/{tables,figures}/."""
    expected_subdirs = ['code', 'data', 'output/tables', 'output/figures']
    for paper_id in sorted(EXPECTED_DERIVATIVE_PAPERS):
        pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
        for sub in expected_subdirs:
            assert (pkg / sub).is_dir(), f"{paper_id}/{sub} missing"


def test_all_four_papers_have_winsor_in_data_prep(tmp_path):
    """每篇 paper 的 01_data_prep.do 都对 MAIN_DV 做 winsorize (项目约定)."""
    for paper_id in sorted(EXPECTED_DERIVATIVE_PAPERS):
        pkg = build_derivative_replication_package(paper_id, output_root=tmp_path)
        data_prep = pkg / 'code' / '01_data_prep.do'
        assert data_prep.exists(), f"{paper_id}: 01_data_prep.do missing"
        content = data_prep.read_text(encoding='utf-8')
        assert 'winsor' in content.lower(), f"{paper_id}: 01_data_prep.do missing winsorize"


# ---------------------------------------------------------------------------
# quality-hardening Round 17 (2026-05-27): derivative_replication 96.67% → 100%
# 补未覆盖行 233 (残留占位符 ValueError) + 290 (output_root None fallback)
# ---------------------------------------------------------------------------


def test_substitute_raises_value_error_on_residue():
    """_substitute 检测残留 {{UNFILLED_KEY}} → ValueError (line 233)."""
    from news_process.papers._common.derivative_replication import _substitute
    # 注意: _PLACEHOLDER_RE = \{\{([A-Z0-9_]+)\}\} — 匹配大写字母/数字/下划线
    # (network-metrics-elevation 2026-06-13 起含数字, 如 OVERID_IV2 / "KEY2" 均会被识别为 placeholder).
    with pytest.raises(ValueError, match="unsubstituted placeholders"):
        _substitute(
            content="hello {{KEY_A}} {{KEY_B}} world",
            choices={"KEY_A": "filled"},  # KEY_B 残留 → ValueError
        )
