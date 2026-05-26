"""papers/_common/paper_spec_schema.py — v3.7.4 P3.6.a.

Lightweight schema validator for `papers/*/paper_spec.yaml`.

P0.7 真实状态 (2026-05-26 verify): 此前 9 轮 audit 假设此文件已存在 — false.
v3.7.4 NEW file (not extension).

Validates that v3.7.4 NEW fields are well-formed when present:
  - tables.tA8.title_robustness.audit_response_ref       (str, anchor format)
  - tables.tA8.title_robustness.panel_d_caveat           (str, optional)
  - tables.tA8.title_robustness.panel_e_caveat           (str, optional)
  - title_robustness_table.audit_response_ref            (str; benefit_society alt-key)

Anchor format expected:
    "docs/methodology/title_track_as_robustness.md#5-audit-response-template-for-peer-review"

Public API:
    validate_paper_spec(spec_dict) -> list[str]   # returns violations, empty = ok
    is_valid_audit_response_ref(s)  -> bool

Usage:
    from papers._common.paper_spec_schema import validate_paper_spec
    import yaml
    with open("papers/bank_fintech_tone/paper_spec.yaml") as f:
        spec = yaml.safe_load(f)
    errs = validate_paper_spec(spec)
    assert not errs, errs
"""
from __future__ import annotations

import re
from typing import Any

_EXPECTED_REF_PATTERN = re.compile(
    r"^docs/methodology/title_track_as_robustness\.md"
    r"#\d+-[a-z][a-z0-9\-]*$"
)


def is_valid_audit_response_ref(s: Any) -> bool:
    """True iff s is a well-formed anchor reference to methodology v1.1 §5."""
    if not isinstance(s, str):
        return False
    return bool(_EXPECTED_REF_PATTERN.match(s))


def _get_path(d: dict, path: list[str]) -> Any:
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def validate_paper_spec(spec: dict) -> list[str]:
    """Validate v3.7.4 fields in a paper_spec.yaml dict.

    Returns:
        List of human-readable violation messages (empty list = valid).
    """
    errs: list[str] = []
    if not isinstance(spec, dict):
        errs.append(f"paper_spec must be a dict, got {type(spec).__name__}")
        return errs

    # Pattern A: tables.tA8.title_robustness.* (8 papers + 1 deferred)
    tA8_tr = _get_path(spec, ["tables", "tA8", "title_robustness"])
    if isinstance(tA8_tr, dict):
        ref = tA8_tr.get("audit_response_ref")
        if ref is not None and not is_valid_audit_response_ref(ref):
            errs.append(
                f"tables.tA8.title_robustness.audit_response_ref invalid: {ref!r}; "
                f"expected anchor like '{_EXPECTED_REF_PATTERN.pattern}'"
            )
        for caveat_key in ("panel_d_caveat", "panel_e_caveat"):
            v = tA8_tr.get(caveat_key)
            if v is not None and not isinstance(v, str):
                errs.append(
                    f"tables.tA8.title_robustness.{caveat_key} must be str, "
                    f"got {type(v).__name__}"
                )

    # Pattern B: top-level title_robustness_table.* (benefit_society alt-key)
    bs_tr = _get_path(spec, ["title_robustness_table"])
    if isinstance(bs_tr, dict):
        ref = bs_tr.get("audit_response_ref")
        if ref is not None and not is_valid_audit_response_ref(ref):
            errs.append(
                f"title_robustness_table.audit_response_ref invalid: {ref!r}"
            )
        for caveat_key in ("panel_d_caveat", "panel_e_caveat"):
            v = bs_tr.get(caveat_key)
            if v is not None and not isinstance(v, str):
                errs.append(
                    f"title_robustness_table.{caveat_key} must be str, "
                    f"got {type(v).__name__}"
                )

    return errs
