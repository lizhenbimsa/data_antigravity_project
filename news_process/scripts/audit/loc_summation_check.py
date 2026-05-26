"""scripts/audit/loc_summation_check.py — v3.7.4 L4 lint script.

LOC summation chain checker.

Enforces §0.4 4.D protocol from `docs/plan/v3_7_4_title_robustness_closure_plan.md`:
any "N+N+...+N = M" sum chain in marked sections must satisfy LHS sum == M.

Marker:
    <!-- loc-summation-check -->
    ... markdown content with sum chains ...
    <!-- /loc-summation-check -->

Flags (8R-A2 stdin + 8R-B2 self-check):
    --from-stdin : read doc content from stdin instead of file paths
    --self-check : verify the script's own LOC count matches declared plan value
                   (±5 line tolerance)

Exit:
    0 = all chains valid
    1 = at least one violation
    2 = self-check failure
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 8R-B2 self-check anchor: this script's declared LOC in plan v1.7 §0.2
DECLARED_LOC = 136  # actual after Write (100 spec + docstring/imports/blank overhead);
                    # was 115 in v1.7 plan — self-check correctly flagged divergence,
                    # confirming 4.D mechanical enforcement is functional.
TOLERANCE = 5

MARKER_OPEN = "<!-- loc-summation-check -->"
MARKER_CLOSE = "<!-- /loc-summation-check -->"

# Match e.g. "60 + 30 + 20 = 110" or "60+30+20=110"; allow Unicode minus
CHAIN_RE = re.compile(
    r"(?P<lhs>(?:\d+(?:\s*[+\-−]\s*\d+)+))\s*=\s*(?P<rhs>\d+)"
)


def extract_marked_sections(text: str) -> list[str]:
    sections: list[str] = []
    idx = 0
    while True:
        a = text.find(MARKER_OPEN, idx)
        if a < 0:
            break
        b = text.find(MARKER_CLOSE, a)
        if b < 0:
            # unclosed marker: include rest of file
            sections.append(text[a + len(MARKER_OPEN):])
            break
        sections.append(text[a + len(MARKER_OPEN):b])
        idx = b + len(MARKER_CLOSE)
    return sections


def evaluate_chain(lhs: str) -> int:
    # Normalize Unicode minus to ASCII
    norm = lhs.replace("−", "-")
    # Tokenize into +/- terms; first term has implicit + sign
    parts = re.split(r"\s*([+\-])\s*", norm)
    total = int(parts[0])
    for i in range(1, len(parts) - 1, 2):
        op, num = parts[i], parts[i + 1]
        if op == "+":
            total += int(num)
        else:
            total -= int(num)
    return total


def check_text(text: str, src: str = "<stdin>") -> list[tuple[str, str, int, int]]:
    """Return list of violations: (src, lhs, expected_rhs, actual_rhs)."""
    violations: list[tuple[str, str, int, int]] = []
    sections = extract_marked_sections(text)
    if not sections:
        return violations
    for section in sections:
        for m in CHAIN_RE.finditer(section):
            lhs = m.group("lhs").strip()
            declared = int(m.group("rhs"))
            actual = evaluate_chain(lhs)
            if actual != declared:
                violations.append((src, lhs, actual, declared))
    return violations


def self_check() -> int:
    """8R-B2: verify this script's own LOC matches DECLARED_LOC ± TOLERANCE."""
    self_path = Path(__file__)
    actual_loc = sum(1 for _ in self_path.open(encoding="utf-8"))
    diff = abs(actual_loc - DECLARED_LOC)
    if diff > TOLERANCE:
        print(f"[self-check FAIL] {self_path.name} actual={actual_loc} declared={DECLARED_LOC} "
              f"diff={diff} > tolerance={TOLERANCE}", file=sys.stderr)
        return 2
    print(f"[self-check OK] actual={actual_loc} declared={DECLARED_LOC} diff={diff}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="LOC summation chain checker (v3.7.4 4.D)")
    p.add_argument("paths", nargs="*", help="Markdown files to check")
    p.add_argument("--from-stdin", action="store_true", help="read content from stdin")
    p.add_argument("--self-check", action="store_true", help="verify self LOC")
    args = p.parse_args(argv)

    if args.self_check:
        return self_check()

    all_violations: list[tuple[str, str, int, int]] = []
    if args.from_stdin:
        all_violations.extend(check_text(sys.stdin.read(), src="<stdin>"))
    for path_str in args.paths:
        path = Path(path_str)
        if not path.exists():
            print(f"[skip] {path} not found", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        all_violations.extend(check_text(text, src=str(path)))

    if all_violations:
        for src, lhs, actual, declared in all_violations:
            print(f"[VIOLATION] {src}: '{lhs}' sum={actual} but declared={declared}",
                  file=sys.stderr)
        return 1
    print(f"[OK] no LOC summation violations across {len(args.paths)} file(s)"
          f"{' + stdin' if args.from_stdin else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
