"""Fix the Boudoukh-2019 venue mislabel everywhere it appears as the _title-track
anchor (audit follow-up part 2, 2026-05-31).

Boudoukh, Feldman, Kogan & Richardson (2019), "Information, Trading, and
Volatility: Evidence from Firm-Specific News" is **Review of Financial Studies
32(3): 992-1033, DOI 10.1093/rfs/hhy083** — NOT "JFE 133(1): 85-104".

WHY a regex (vs the literal-pair pass in fix_title_track_*.py): the paper_spec.yaml
anchors wrap the citation across a YAML line break —
    anchor: "... Boudoukh et al.
      (2019) JFE; Campbell & Fiske (1959) MTMM"
so a literal "Boudoukh et al. (2019) JFE" never matches. Every pattern here is
ANCHORED on the literal "Boudoukh" token with `\\s+` bridging the wrap, so it can
NEVER touch the false-positive JFE refs in these files:
  - Laeven & Levine (2009) JFE  (year 2009, no Boudoukh)
  - journal-target lists "JFQA / RFS / JFE", "RFS / JFE"  (no year, no Boudoukh)
  - Engelberg-Reed-Ringgenberg (2018) JFE  (year 2018, no Boudoukh)

Idempotent: after the fix the venue reads RFS, so re-running matches nothing.
EXCLUDES the two concurrently-edited (dirty) files
(docs/methodology/title_track_as_robustness.md, tests/test_39g_track_discriminant.py)
— those are deferred to a coordinated pass to avoid clobbering live edits.

Run:  F:\\Anaconda3\\python.exe scripts/migrate/fix_boudoukh_venue_v2.py
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]  # repo root (…/news_process)

# Ordered longest-match-first. Each requires the literal "Boudoukh"; `\s+`
# bridges the YAML line-wrap between "al." and "(2019)".
PATTERNS: list[tuple[str, str]] = [
    # ref-list form: "... Information, trading, and volatility. *JFE*, 133(1), 85-104."
    (r"Information, trading, and volatility\. \*JFE\*, 133\(1\), 85-104\.",
     "Information, trading, and volatility. *RFS*, 32(3), 992-1033. "
     "DOI: 10.1093/rfs/hhy083."),
    # markdown, year-no-parens, with volume: "Boudoukh et al. 2019 *JFE* 133(1)"
    (r"(Boudoukh et al\.?\s+2019\s+)\*JFE\*(\s+)133\(1\)",
     r"\1*RFS*\g<2>32(3): 992-1033"),
    # markdown, year-no-parens, no volume: "Boudoukh ... 2019 *JFE*"
    (r"(Boudoukh[^\n]{0,20}?\s+2019\s+)\*JFE\*",
     r"\1*RFS*"),
    # parenthetical year + venue + full volume
    (r"(Boudoukh et al\.\s+)\(2019\)\s*JFE 133\(1\): 85-104",
     r"\1(2019) RFS 32(3): 992-1033"),
    (r"(Boudoukh et al\.\s+)\(2019\)\s*JFE 133\(1\)",
     r"\1(2019) RFS 32(3): 992-1033"),
    # combined-paren form "(2019 JFE ...)"
    (r"(Boudoukh et al\.\s+)\(2019 JFE",
     r"\1(2019 RFS"),
    (r"(Boudoukh \(2019 JFE)",
     r"Boudoukh (2019 RFS"),
    # bare venue, no volume, parenthetical year: "Boudoukh et al. (2019) JFE"
    (r"(Boudoukh et al\.\s+)\(2019\)\s*JFE",
     r"\1(2019) RFS"),
    # "Boudoukh (2019) JFE" (no "et al.")
    (r"Boudoukh \(2019\) JFE",
     r"Boudoukh et al. (2019) RFS"),
]

COMPILED = [(re.compile(p), r) for p, r in PATTERNS]

# Clean files known to carry the genuine Boudoukh-2019 anchor. The two dirty
# files are deliberately omitted. Already-fixed files are listed too (idempotent).
TARGETS: list[Path] = [
    REPO / "CLAUDE.md",
    REPO / "core" / "dag.py",
    REPO / "39g_track_discriminant_validity.py",
    REPO / "pipeline" / "audit" / "track_discriminant_validity.py",
    REPO / "docs" / "PROJECT_DESCRIPTION.md",
    REPO / "docs" / "methodology" / "implicit_guarantee_framework.md",
    REPO / "docs" / "methodology" / "title_track_robustness_report_v2_6.md",
    REPO / "docs" / "plan" / "B_route_master_plan_v2.md",
    REPO / "docs" / "plan" / "B_route_master_plan_v2_audit_log.md",
    REPO / "docs" / "plan" / "portfolio_channel_matrix.md",
    REPO / "papers" / "bank_fintech_tone" / "paper_spec.yaml",
    REPO / "papers" / "bank_fintech_attention" / "paper_spec.yaml",
    REPO / "papers" / "bank_fintech_substance" / "paper_spec.yaml",
    REPO / "papers" / "bank_fintech_locus" / "paper_spec.yaml",
    REPO / "papers" / "bank_fintech_collab" / "paper_spec.yaml",
    REPO / "papers" / "brokerage_network" / "paper_spec.yaml",
    REPO / "papers" / "llm_peer" / "paper_spec.yaml",
    REPO / "papers" / "strategic_diff" / "paper_spec.yaml",
    REPO / "papers" / "benefit_society" / "paper_spec.yaml",
]

# The 9 Stata Table-A8 templates. Their Boudoukh refs live ONLY in comment/
# addnote text (header anchor list + esttab addnote string), which is disjoint
# from the esttab/guard executable region a concurrent plan edits — so fixing
# the citation here cannot collide with that plan's Panel D/E export work.
_TPL = REPO / "papers" / "_common" / "stata_templates"
TEMPLATE_TARGETS: list[Path] = [
    _TPL / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "bank_fintech_attention" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "bank_fintech_substance" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "bank_fintech_locus" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "bank_fintech_collab" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "brokerage_network" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "llm_peer" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "strategic_diff" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "benefit_society" / "26_bs_title_robustness.do.tmpl",
]
TARGETS = TARGETS + TEMPLATE_TARGETS

# Sanity guard: a fixed file must contain ZERO of these residual JFE forms.
RESIDUAL = re.compile(r"Boudoukh[^\n]{0,30}(?:2019\)?\s*JFE|2019\s+\*JFE\*)"
                      r"|Boudoukh et al\.\s+\(?2019\)?\s*JFE")


def process(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    text = raw
    n = 0
    for rx, repl in COMPILED:
        text, c = rx.subn(repl, text)
        n += c
    changed = text != raw
    if changed:
        path.write_text(text, encoding="utf-8", newline="")
    # residual check on the (possibly updated) text
    residual = len(RESIDUAL.findall(text))
    return {"file": str(path.relative_to(REPO)), "changed": changed,
            "subs": n, "residual_boudoukh_jfe": residual}


def main() -> None:
    print("=== Boudoukh JFE -> RFS (regex, whitespace-tolerant, Boudoukh-anchored) ===")
    total = 0
    residual_total = 0
    for p in TARGETS:
        if not p.exists():
            print(f"  MISSING: {p}")
            continue
        r = process(p)
        total += int(r["changed"])
        residual_total += r["residual_boudoukh_jfe"]
        flag = "CHG" if r["changed"] else " . "
        warn = "  <-- RESIDUAL!" if r["residual_boudoukh_jfe"] else ""
        print(f"  [{flag}] {r['file']}: subs={r['subs']} "
              f"residual={r['residual_boudoukh_jfe']}{warn}")
    print(f"\nSUMMARY: {total} files changed; "
          f"{residual_total} residual Boudoukh+JFE remaining in targets "
          f"(want 0).")


if __name__ == "__main__":
    main()
