"""M0 G0 acceptance — 8 paper × paper_spec.yaml schema 一致性测试.

Plan v2.x §5.2.3.bis + §5.2.4 G0 acceptance:
    "8 paper × spec.yaml 全部 conform 此 schema"

红线不变式
----------
1. 8 个 paper_spec.yaml 文件全部存在且可被 yaml.safe_load 解析。
2. 每份 spec 的 ``paper_id`` 字段必须与所在目录名一致。
3. Schema-required 字段 (12 个) 必须全部 present。
4. ``spec_version`` 必须满足 semver-ish (X.Y.Z 三段, 数字).
5. ``status`` 必须 ∈ {existing, new, skeleton}。
6. ``differentiation_claim`` 必须非空 (反 anti-pattern: 防止 boilerplate).
7. ``audit_rounds_target_min`` 必须为正整数。
8. ``targets.primary_outlet`` 必须非空。
9. ``targets.submission_window`` 必须是 YYYY-MM-DD 形式 (per §5.11.1 投稿计划)。
10. 8 paper 的 spec_version 主版本号 ≤ plan major (per §13 R1-m07/R6-m02)。
"""

from __future__ import annotations

import re
from datetime import date

import pytest

from news_process.papers._common.paper_registry import (
    PAPER_IDS_ALL,
    REQUIRED_FIELDS,
    get_spec,
    load_all_specs,
)

VALID_STATUS = frozenset({'existing', 'new', 'skeleton'})

SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+$')
DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')

# Plan v2.x major = 2; spec_version major must ≤ 2 per §13.
PLAN_MAJOR_VERSION = 2


# ---------------------------------------------------------------------------


def test_all_8_specs_loadable() -> None:
    """11 spec.yaml 全部能被 yaml.safe_load 解析 (5 existing + 3 new + 3 provisional, 2026-06-01)."""
    specs = load_all_specs()
    assert set(specs) == set(PAPER_IDS_ALL), (
        f"loaded specs {sorted(specs)} != PAPER_IDS_ALL {sorted(PAPER_IDS_ALL)}"
    )
    assert len(specs) == 11, f"expected 11 papers, got {len(specs)}"


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_spec_has_all_required_fields(paper_id: str) -> None:
    spec = get_spec(paper_id)
    missing = REQUIRED_FIELDS - set(spec.raw)
    assert not missing, f"{paper_id} missing required fields: {sorted(missing)}"


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_paper_id_matches_directory(paper_id: str) -> None:
    spec = get_spec(paper_id)
    assert spec.raw['paper_id'] == paper_id, (
        f"declared paper_id={spec.raw['paper_id']!r} != directory={paper_id!r}"
    )


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_spec_version_is_semver(paper_id: str) -> None:
    spec = get_spec(paper_id)
    sv = str(spec.raw['spec_version'])
    assert SEMVER_RE.match(sv), f"{paper_id}: spec_version={sv!r} not semver"
    major = int(sv.split('.')[0])
    assert major <= PLAN_MAJOR_VERSION, (
        f"{paper_id}: spec_version major={major} exceeds plan major "
        f"{PLAN_MAJOR_VERSION} (per §13 R1-m07/R6-m02)"
    )


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_status_in_valid_enum(paper_id: str) -> None:
    spec = get_spec(paper_id)
    assert spec.raw['status'] in VALID_STATUS, (
        f"{paper_id}: status={spec.raw['status']!r} not in {sorted(VALID_STATUS)}"
    )


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_differentiation_claim_nonempty(paper_id: str) -> None:
    spec = get_spec(paper_id)
    claim = spec.raw.get('differentiation_claim', '')
    assert claim and len(claim.strip()) >= 20, (
        f"{paper_id}: differentiation_claim too short / empty (anti-boilerplate)"
    )


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_audit_rounds_target_min_positive_int(paper_id: str) -> None:
    spec = get_spec(paper_id)
    n = spec.raw['audit_rounds_target_min']
    assert isinstance(n, int) and n >= 1, (
        f"{paper_id}: audit_rounds_target_min={n!r} not positive int"
    )


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_targets_primary_outlet_nonempty(paper_id: str) -> None:
    spec = get_spec(paper_id)
    po = spec.raw.get('targets', {}).get('primary_outlet', '')
    assert po and isinstance(po, str), (
        f"{paper_id}: targets.primary_outlet missing or non-string"
    )


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_targets_submission_window_valid_date(paper_id: str) -> None:
    spec = get_spec(paper_id)
    sw = spec.raw.get('targets', {}).get('submission_window')
    # YAML 1.1 loads YYYY-MM-DD as datetime.date by default
    if isinstance(sw, date):
        return  # already parsed
    assert isinstance(sw, str), f"{paper_id}: submission_window type {type(sw).__name__}"
    assert DATE_RE.match(sw), (
        f"{paper_id}: submission_window={sw!r} not YYYY-MM-DD"
    )


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_controls_has_three_subkeys(paper_id: str) -> None:
    spec = get_spec(paper_id)
    controls = spec.raw.get('controls', {})
    for key in ('bank_level', 'year_level', 'fixed_effects'):
        assert key in controls, f"{paper_id}: controls missing {key!r}"
        assert isinstance(controls[key], list), (
            f"{paper_id}: controls.{key} not a list"
        )


@pytest.mark.parametrize('paper_id', PAPER_IDS_ALL)
def test_sample_block_complete(paper_id: str) -> None:
    spec = get_spec(paper_id)
    sample = spec.raw.get('sample', {})
    for key in ('n_bank_min', 't_year', 'obs_target_min'):
        assert key in sample, f"{paper_id}: sample missing {key!r}"
        assert isinstance(sample[key], int) and sample[key] > 0, (
            f"{paper_id}: sample.{key} not positive int"
        )


# ----------------------------------------------------------------------------
# v3.5.0 D2 8-cell decomposition: tables.t6 field schema
# Per stage3_v3_5_0_augmentation_plan.md §2.1.6 + master plan v2 §5.2.3.bis.
# (修 E-NEW-2 + F2: v3.5.0 D6 day 扩展 schema 测试)
#
# 注: 这些测试用直接 YAML load (绕过 paper_registry.get_spec) 因为 v3.4.0 PAPER_IDS_NEW
# 不含 P5 bank_fintech_collab (epoch 5 立项 baseline gap, 非 v3.5.0 问题).
# Filesystem-based load 让 v3.5.0 schema 测试独立于 v3.4.0 baseline registry.
# ----------------------------------------------------------------------------

from pathlib import Path  # noqa: E402

import yaml as _yaml  # noqa: E402

_PAPERS_DIR_V3_5_0 = Path(__file__).resolve().parents[2] / 'papers'

# 9 paper portfolio split per plan §2.1.6:
#   - D2 main regression users (Table 6 i.cell_id_full): P3/P4/P5
#   - D2 not used (explicit null to prevent schema drift): P1/P2 + 4 retrofit
V3_5_0_D2_USING = (
    'bank_fintech_substance',
    'bank_fintech_locus',
    'bank_fintech_collab',
)
V3_5_0_D2_NULL = (
    'bank_fintech_tone',
    'bank_fintech_attention',
    'benefit_society',
    'brokerage_network',
    'llm_peer',
    'strategic_diff',
)
V3_5_0_ALL_9 = V3_5_0_D2_USING + V3_5_0_D2_NULL
V3_5_0_D2_TEMPLATE = '19_table6_cell_decomposition'


def _load_spec_yaml_v3_5_0(paper_id: str) -> dict:
    """Filesystem YAML load bypassing v3.4.0 paper_registry (which misses P5)."""
    path = _PAPERS_DIR_V3_5_0 / paper_id / 'paper_spec.yaml'
    if not path.exists():
        pytest.skip(f"paper_spec.yaml missing for {paper_id}")
    return _yaml.safe_load(path.read_text(encoding='utf-8'))


@pytest.mark.parametrize('paper_id', V3_5_0_ALL_9)
def test_v3_5_0_tables_t6_field_explicit(paper_id: str) -> None:
    """v3.5.0 D2: tables.t6 必须 explicit declare (防 schema drift).

    Per plan §2.1.6: 全 9 paper_spec.yaml 强制声明 tables.t6 (template or null).
    """
    spec = _load_spec_yaml_v3_5_0(paper_id)
    tables = spec.get('tables')
    assert tables is not None, (
        f"{paper_id}: 缺少 'tables' 字段 "
        "(v3.5.0 新增 per plan §5 + master plan v2 §5.2.3.bis)"
    )
    assert 't6' in tables, f"{paper_id}.tables 缺少 t6 字段 (v3.5.0 D2 explicit declare)"


@pytest.mark.parametrize('paper_id', V3_5_0_D2_USING)
def test_v3_5_0_d2_using_papers_template(paper_id: str) -> None:
    """P3/P4/P5: tables.t6.template == '19_table6_cell_decomposition'."""
    spec = _load_spec_yaml_v3_5_0(paper_id)
    t6 = spec['tables']['t6']
    assert t6 is not None, f"{paper_id} (D2-using) tables.t6 不应为 null"
    assert t6.get('template') == V3_5_0_D2_TEMPLATE, (
        f"{paper_id}.tables.t6.template = {t6.get('template')!r}, "
        f"expected {V3_5_0_D2_TEMPLATE!r}"
    )


@pytest.mark.parametrize('paper_id', V3_5_0_D2_NULL)
def test_v3_5_0_d2_null_papers_explicit(paper_id: str) -> None:
    """P1/P2 + 4 retrofit: tables.t6 == None (explicit null 防 schema test fail).

    Per plan §2.1.6: 不用 D2 主回归的 paper 也必须 explicit null declaration,
    避免 future audit 把缺 t6 当作 schema breaking. 这是 F2 / E-NEW-2 finding 修复.
    """
    spec = _load_spec_yaml_v3_5_0(paper_id)
    t6 = spec['tables']['t6']
    assert t6 is None, (
        f"{paper_id} (non-D2-using) tables.t6 应为 null (explicit declaration), got {t6!r}"
    )


# ----------------------------------------------------------------------------
# v3.5.0 D2 P5-specific: treatment.alternative + alternative_construction extensions
# Per plan §2.1.7 (修 A-NEW-2 P5 treatment.alternative 同步)
# ----------------------------------------------------------------------------

def test_v3_5_0_p5_treatment_alternative_includes_cell_id_full() -> None:
    """P5 (bank_fintech_collab): treatment.alternative 必含 'cell_id_full' (v3.5.0 D2)."""
    spec = _load_spec_yaml_v3_5_0('bank_fintech_collab')
    alts = spec['treatment'].get('alternative', [])
    assert 'cell_id_full' in alts, (
        f"P5 treatment.alternative 缺 cell_id_full (v3.5.0 D2 alt 见 plan §2.1.7); "
        f"actual = {alts!r}"
    )


def test_v3_5_0_p5_alternative_construction_cell_id_formula() -> None:
    """P5: alternative_construction 必含 cell_id_full 公式 (v3.5.0 D2 derivation rule)."""
    spec = _load_spec_yaml_v3_5_0('bank_fintech_collab')
    construction = spec['treatment'].get('alternative_construction', {})
    assert 'cell_id_full' in construction, (
        f"P5 alternative_construction 缺 cell_id_full formula; "
        f"got = {list(construction)!r}"
    )


# ----------------------------------------------------------------------------
# v3.5.1 A1 + A3 tables.tA7 / tA8 / tA9 schema 扩展 (per plan v0.3 §5 修 R6-C1)
# 5 active paper + 4 explicit null, 全 9 paper 必须 explicit declare 各 tA* 字段.
# ----------------------------------------------------------------------------

# A1 clarity_robustness 主用 paper (3): P3 substance / P4 locus / P5 collab
V3_5_1_TA7_USING = ('bank_fintech_substance', 'bank_fintech_locus', 'bank_fintech_collab')
V3_5_1_TA7_TEMPLATES = {
    'bank_fintech_substance': '21_substance_clarity_robustness',
    'bank_fintech_locus': '19_locus_clarity_robustness',
    'bank_fintech_collab': '20_collab_clarity_robustness',
}
# A3 num_intensity 主用 paper (2): P1 tone (tA9) + benefit_society (tA8)
V3_5_1_TA9_USING = 'bank_fintech_tone'
V3_5_1_TA9_TEMPLATE = '27_tableA9_num_intensity'
V3_5_1_TA8_USING = 'benefit_society'
V3_5_1_TA8_TEMPLATE = '19_bs_num_intensity_robustness'


@pytest.mark.parametrize('paper_id', V3_5_0_ALL_9)
def test_v3_5_1_tables_tA7_tA8_tA9_explicit(paper_id: str) -> None:
    """v3.5.1: 全 9 paper 必须 explicit declare tA7/tA8/tA9 字段 (修 R6-C1 schema 授权).

    Per plan v0.3 §5 + master plan §5.2.3.bis 扩 schema 已加入 tA*. 全 9 paper 必须
    explicit declare (template 或 null) 以防止 schema drift.
    """
    spec = _load_spec_yaml_v3_5_0(paper_id)
    tables = spec.get('tables', {})
    for ta_field in ('tA7', 'tA8', 'tA9'):
        assert ta_field in tables, (
            f"{paper_id}.tables 缺 '{ta_field}' (v3.5.1 explicit declare per plan v0.3 §5)"
        )


@pytest.mark.parametrize('paper_id', V3_5_1_TA7_USING)
def test_v3_5_1_tA7_using_papers_have_template(paper_id: str) -> None:
    """P3/P4/P5: tables.tA7.template 应为对应 A1 clarity_robustness 模板名 (修 R3-C1)."""
    spec = _load_spec_yaml_v3_5_0(paper_id)
    ta7 = spec['tables']['tA7']
    assert ta7 is not None, f"{paper_id} (A1-using) tables.tA7 不应为 null"
    expected = V3_5_1_TA7_TEMPLATES[paper_id]
    assert ta7.get('template') == expected, (
        f"{paper_id}.tables.tA7.template = {ta7.get('template')!r}, expected {expected!r}"
    )


def test_v3_5_1_p1_tone_has_tA9_template() -> None:
    """P1 bank_fintech_tone: tables.tA9.template == '27_tableA9_num_intensity' (A3 真双轨)."""
    spec = _load_spec_yaml_v3_5_0(V3_5_1_TA9_USING)
    ta9 = spec['tables']['tA9']
    assert ta9 is not None, "P1 (A3-using) tables.tA9 不应为 null"
    assert ta9.get('template') == V3_5_1_TA9_TEMPLATE, (
        f"P1.tables.tA9.template = {ta9.get('template')!r}, expected {V3_5_1_TA9_TEMPLATE!r}"
    )


def test_v3_5_1_benefit_society_has_tA8_template() -> None:
    """benefit_society: tables.tA8.template == '19_bs_num_intensity_robustness' (A3 真双轨)."""
    spec = _load_spec_yaml_v3_5_0(V3_5_1_TA8_USING)
    ta8 = spec['tables']['tA8']
    assert ta8 is not None, "benefit_society (A3-using) tables.tA8 不应为 null"
    assert ta8.get('template') == V3_5_1_TA8_TEMPLATE, (
        f"benefit_society.tables.tA8.template = {ta8.get('template')!r}, expected {V3_5_1_TA8_TEMPLATE!r}"
    )
