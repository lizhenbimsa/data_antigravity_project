"""scripts/migrate/v3_7_4_patch_paper_specs.py — v3.7.4 P3.6.b.

One-shot YAML patcher: add 3 new keys to each of 9 paper_spec.yaml files
under the appropriate parent (8 paper × `tables.tA8.title_robustness.*` +
benefit_society × `title_robustness_table.*`).

NEW KEYS (MA-4 SoT: ref pointer, NOT inline copy):
    audit_response_ref: "docs/methodology/title_track_as_robustness.md
                         #5-audit-response-template-for-peer-review"
    panel_d_caveat:     "Stratification by frac_title_mentions_fintech ..."
    panel_e_caveat:     "Stratification by frac_title_long ..."

Idempotent: skip files that already have all 3 keys present.

YAML preservation: uses ruamel.yaml round-trip to keep existing comments
+ key order intact. Falls back to PyYAML with WARNING if ruamel unavailable.
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_PROJECT_ROOT = _HERE.parent.parent

PAPERS_ROOT = _PROJECT_ROOT / "papers"

NEW_AUDIT_REF = (
    "docs/methodology/title_track_as_robustness.md"
    "#5-audit-response-template-for-peer-review"
)
NEW_PANEL_D_CAVEAT = (
    "Stratification by frac_title_mentions_fintech across thresholds "
    "{0.3, 0.5, 0.7} per Antweiler-Frank (2004) JF 59(3) subject-relevance "
    "convention. Per-cell graceful skip if N < 30 bank-year."
)
NEW_PANEL_E_CAVEAT = (
    "Stratification by frac_title_long (above/below bank-year median title "
    "length) per Da-Engelberg-Gao (2011) JF 66(5) attention-channel "
    "separation. Per-cell graceful skip if N < 30."
)


# 8 paper using tables.tA8.title_robustness path + 1 benefit_society alt-key path
TARGETS = [
    ("bank_fintech_tone", "tables.tA8.title_robustness"),
    ("bank_fintech_attention", "tables.tA8.title_robustness"),
    ("bank_fintech_substance", "tables.tA8.title_robustness"),
    ("bank_fintech_locus", "tables.tA8.title_robustness"),
    ("bank_fintech_collab", "tables.tA8.title_robustness"),
    ("brokerage_network", "tables.tA8.title_robustness"),
    ("llm_peer", "tables.tA8.title_robustness"),
    ("strategic_diff", "tables.tA8.title_robustness"),
    ("benefit_society", "title_robustness_table"),
]


def _load_yaml(path: Path):
    try:
        from ruamel.yaml import YAML
        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.indent(mapping=2, sequence=4, offset=2)
        with path.open("r", encoding="utf-8") as f:
            data = yaml.load(f)
        return data, yaml
    except ImportError:
        import yaml as _y
        with path.open("r", encoding="utf-8") as f:
            data = _y.safe_load(f)
        return data, _y


def _dump_yaml(data, path: Path, yaml_inst) -> None:
    if hasattr(yaml_inst, "dump") and yaml_inst.__class__.__name__ == "YAML":
        with path.open("w", encoding="utf-8") as f:
            yaml_inst.dump(data, f)
    else:
        # PyYAML fallback (loses comments!) — warn user
        print(f"  [WARN] ruamel.yaml not available; PyYAML fallback used for {path.name} "
              f"(comments may be lost). Install ruamel.yaml for comment preservation.")
        with path.open("w", encoding="utf-8") as f:
            yaml_inst.dump(data, f, allow_unicode=True, default_flow_style=False)


def _nav_create(d: dict, path: list[str]) -> dict:
    """Navigate / create nested dict path; return innermost dict."""
    cur = d
    for k in path:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    return cur


def patch_one(spec_dir: Path, parent_path: str) -> str:
    """Patch a single paper_spec.yaml under spec_dir at parent_path. Idempotent.

    Returns a status string: '[PATCHED] ...', '[SKIP idempotent] ...', or '[MISS] ...'.
    """
    yaml_path = spec_dir / "paper_spec.yaml"
    if not yaml_path.exists():
        return f"[MISS] {yaml_path}"

    data, yaml_inst = _load_yaml(yaml_path)
    if not isinstance(data, dict):
        return f"[SKIP non-dict root] {yaml_path}"

    parent = _nav_create(data, parent_path.split("."))

    # Idempotent check
    keys = ("audit_response_ref", "panel_d_caveat", "panel_e_caveat")
    if all(k in parent for k in keys):
        return f"[SKIP idempotent] {spec_dir.name}/paper_spec.yaml"

    if "audit_response_ref" not in parent:
        parent["audit_response_ref"] = NEW_AUDIT_REF
    if "panel_d_caveat" not in parent:
        parent["panel_d_caveat"] = NEW_PANEL_D_CAVEAT
    if "panel_e_caveat" not in parent:
        parent["panel_e_caveat"] = NEW_PANEL_E_CAVEAT

    _dump_yaml(data, yaml_path, yaml_inst)
    return f"[PATCHED] {spec_dir.name}/paper_spec.yaml ({parent_path})"


def main() -> int:
    """Walk TARGETS and patch v3.7.4 fields in each paper_spec.yaml. Returns 0."""
    print(f"v3.7.4 paper_spec.yaml patcher: walking {len(TARGETS)} specs")
    print("-" * 60)
    for paper_id, parent_path in TARGETS:
        spec_dir = PAPERS_ROOT / paper_id
        result = patch_one(spec_dir, parent_path)
        print(f"  {result}")
    print("-" * 60)
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
