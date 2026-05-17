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
    """8 spec.yaml 全部能被 yaml.safe_load 解析."""
    specs = load_all_specs()
    assert set(specs) == set(PAPER_IDS_ALL), (
        f"loaded specs {sorted(specs)} != PAPER_IDS_ALL {sorted(PAPER_IDS_ALL)}"
    )
    assert len(specs) == 8, f"expected 8 papers, got {len(specs)}"


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
