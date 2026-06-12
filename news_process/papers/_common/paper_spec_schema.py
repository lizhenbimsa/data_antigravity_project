"""papers/_common/paper_spec_schema.py — 轻量级 paper_spec.yaml 校验器。

remove-title-track: 此模块原为校验已删除的「标题情感稳健性轨」字段而建
(tables.tA8.title_robustness.* / title_robustness_table.*)。这些字段已从所有
papers/*/paper_spec.yaml 移除, 故本模块的检查在当前 spec 上恒为 no-op (字段缺失时
直接通过)。模块予以保留仅因 11 份 paper_spec.yaml 顶部以注释方式引用其路径
(`# Schema reference: papers/_common/paper_spec_schema.py`)。

公开 API:
    validate_paper_spec(spec_dict) -> list[str]   # 返回违规消息列表, 空 = 通过
    is_valid_audit_response_ref(s)  -> bool

用法:
    from papers._common.paper_spec_schema import validate_paper_spec
    import yaml
    with open("papers/bank_fintech_tone/paper_spec.yaml") as f:
        spec = yaml.safe_load(f)
    errs = validate_paper_spec(spec)
    assert not errs, errs
"""
from __future__ import annotations

from typing import Any

# Round 62 audit (62-A1): 用显式 allowlist 而非通配正则,
# 防止过期或打错的锚点 (如 '#999-bogus') 蒙混过关。
_VALID_AUDIT_RESPONSE_REFS: frozenset[str] = frozenset({
    "docs/methodology/title_track_as_robustness.md"
    "#5-audit-response-template-for-peer-review",
})


def is_valid_audit_response_ref(s: Any) -> bool:
    """当且仅当 s 是显式 allowlist 中的 audit-response 锚点时为 True。

    remove-title-track: 该 audit-response 体系随标题情感稳健性轨一并停产, 不再
    新增 variant; 此函数在当前 spec 上恒返回 False 对缺失字段无影响 (调用方仅在
    audit_response_ref 存在时才检查)。
    """
    if not isinstance(s, str):
        return False
    return s in _VALID_AUDIT_RESPONSE_REFS


def _get_path(d: dict, path: list[str]) -> Any:
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


def validate_paper_spec(spec: dict) -> list[str]:
    """校验 paper_spec.yaml dict 中的 v3.7.4 字段。

    Returns:
        人类可读的违规消息列表 (空列表 = 通过)。
    """
    errs: list[str] = []
    if not isinstance(spec, dict):
        errs.append(f"paper_spec must be a dict, got {type(spec).__name__}")
        return errs

    # 模式 A: tables.tA8.title_robustness.* (历史字段, 已从全部 spec 移除; 8 papers + 1 deferred)
    tA8_tr = _get_path(spec, ["tables", "tA8", "title_robustness"])
    if isinstance(tA8_tr, dict):
        ref = tA8_tr.get("audit_response_ref")
        if ref is not None and not is_valid_audit_response_ref(ref):
            errs.append(
                f"tables.tA8.title_robustness.audit_response_ref invalid: {ref!r}; "
                f"expected one of {sorted(_VALID_AUDIT_RESPONSE_REFS)}"
            )
        for caveat_key in ("panel_d_caveat", "panel_e_caveat"):
            v = tA8_tr.get(caveat_key)
            if v is not None and not isinstance(v, str):
                errs.append(
                    f"tables.tA8.title_robustness.{caveat_key} must be str, "
                    f"got {type(v).__name__}"
                )

    # 模式 B: 顶层 title_robustness_table.* (benefit_society 替代键, 同为历史字段)
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
