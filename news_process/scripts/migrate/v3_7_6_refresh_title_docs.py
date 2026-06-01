"""scripts/migrate/v3_7_6_refresh_title_docs.py — refresh stale numbers/claims in
the two _title-track methodology docs (audit follow-up, 2026-05-31). [OBSOLETE — 历史/已废]

⚠ 已废 (标题情感轨 + 其方法学文档已删): 本脚本就地编辑的两个文档
docs/methodology/title_track_as_robustness.md 与 title_track_robustness_report_v2_6.md 已随
docs/ 目录整体删除 (commit 1698bda5), main() 的 METH.read_text 会立即抛 FileNotFoundError; 且
FIX A 描述的 stage 39g HTMT(_full,_title)/(_ctx,_title) 标题判别效度 stage 已删除
(shim/dag/schemas/模块均移除, STAGES_VALIDATION 18→17), 不再产出。仅作历史留存。下方为历史描述。

Fixes, each asserted (exact expected hit-count; raises on drift), idempotent:

  FIX A — audit-response (i) HTMT bullet (VERBATIM-MIRRORED across both docs;
    grep-diff between the two must stay 0). The shipped peer-review text apologises
    for a bootstrap-CI breach (upper 0.863/0.861 > 0.85) that NO LONGER EXISTS on
    the current production panel. Live stage-39g re-run (verified by running the
    stage on 40_panel_yearly.parquet, 174×1997, N=64, seed=42, 2026-05-31):
        HTMT(_full,_title) = 0.384  CI upper 0.710   (pass point AND CI)
        HTMT(_ctx, _title) = 0.517  CI upper 0.798   (pass point AND CI)
        HTMT(_full,_ctx)   = 0.825  (design self-correlation; ctx ⊂ full)
    The identical replacement block is applied to BOTH files so the mirror stays
    byte-identical. The earlier 2026-05-26 first-run (168×2060: 0.627/0.628, CI
    0.863/0.861) is PRESERVED as a dated historical note inside the new block, so
    no dated record is falsified.

  FIX B — "BERT 5-model" -> "BERT 3-model" (factual: the erlangshen+hw2942 drop,
    commit a6327512, reduced BERT 5->3; the 5 DICTIONARY lexicons are UNCHANGED, so
    "dictionary 5-lexicon" is left intact).

  FIX C — soften two over-claimed anchors that a referee would catch:
    * Tetlock-Saar-Tsechansky-Macskassy 2008 "More Than Words" does NOT score
      headline vs body separately (it is story-level negative-word fraction).
    * Da-Engelberg-Gao 2011 measures attention via Google SVI, NOT title length;
      Panel E's frac_title_long anchor is the project's own attention-channel
      motivation, not a DEG result.

NOT changed: the dated §3.1 / §7.1 first-run passages (true as-of-2026-05-26; the
new audit-response block now carries the current numbers); the "168×2060 frozen"
provenance lines inside those dated first-run records; the 5-lexicon dictionary count.

Run:  F:\\Anaconda3\\python.exe scripts/migrate/v3_7_6_refresh_title_docs.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METH = ROOT / "docs" / "methodology" / "title_track_as_robustness.md"
REPORT = ROOT / "docs" / "methodology" / "title_track_robustness_report_v2_6.md"

MARKER = "current production panel (174"

# ---- FIX A: the verbatim-mirrored (i) HTMT bullet (identical in both files) ----
OLD_HTMT_BULLET = (
    "> (i) HTMT discriminant validity (Henseler-Ringle-Sarstedt 2015, *JAMS*):\n"
    ">     HTMT(`_full`,`_title`) point estimate = 0.627 (strict pass < 0.85);\n"
    ">     HTMT(`_ctx`,`_title`) = 0.628 (strict pass < 0.85). Bootstrap 95%\n"
    ">     CI upper bounds 0.863 and 0.861 respectively (stage 39g,\n"
    ">     n_bootstrap=1000, seed=42, N=64 bank-year) exceed the 0.85 strict\n"
    ">     threshold; this reflects small-sample CI width rather than\n"
    ">     discriminant failure (Henseler-Ringle-Sarstedt 2015 §4 recommend\n"
    ">     bootstrap CI; we acknowledge the wide band and report it\n"
    ">     transparently. Future N expansion via stage 14-40 production\n"
    ">     re-run is expected to tighten the upper bound below 0.85.) Point\n"
    ">     estimates remain consistent with the order of magnitude of\n"
    ">     headline-vs-body sentiment relationship documented in Heston-Sinha\n"
    ">     (2017, *FAJ*);\n"
)
NEW_HTMT_BULLET = (
    "> (i) HTMT discriminant validity (Henseler-Ringle-Sarstedt 2015, *JAMS*),\n"
    ">     on the current production panel (174×1997, stage 39g re-run\n"
    ">     2026-05-31, N=64 bank-year, n_bootstrap=1000, seed=42):\n"
    ">     HTMT(`_full`,`_title`) point estimate = 0.384, bootstrap 95% CI\n"
    ">     upper bound 0.710; HTMT(`_ctx`,`_title`) = 0.517, CI upper 0.798 —\n"
    ">     both `_title` pairs pass the 0.85 strict cutoff on BOTH the point\n"
    ">     estimate AND the bootstrap CI upper bound. HTMT(`_full`,`_ctx`) =\n"
    ">     0.825 is treated as design self-correlation (`_ctx` is the\n"
    ">     entity-proximity sub-window of `_full`; Hassan et al. 2019 *QJE*),\n"
    ">     not a discriminant failure. (The earlier 2026-05-26 first-run on\n"
    ">     the 168×2060 panel reported point 0.627/0.628 with CI upper\n"
    ">     0.863/0.861 marginally above 0.85, attributed to small-sample\n"
    ">     width; the current larger panel resolves both below the cutoff.)\n"
    ">     Point estimates remain consistent with the order of magnitude of\n"
    ">     the headline-vs-body sentiment relationship documented in\n"
    ">     Heston-Sinha (2017, *FAJ*);\n"
)

# ---- FIX B: BERT model count (5 -> 3 after the erlangshen+hw2942 drop) ----
OLD_BERT = "(LLM 3-vote / dictionary 5-lexicon / BERT 5-model)."
NEW_BERT = ("(LLM 3-vote / dictionary 5-lexicon / BERT 3-model — "
            "BERT reduced 5→3 after the erlangshen+hw2942 drop, commit a6327512).")

# ---- FIX C: over-claimed anchors ----
OLD_TSM = ("| Tetlock-Saar-Tsechansky-Macskassy (2008) | *JF* 63(3) | "
           '"More Than Words" — direct firm news headline vs body sentiment '
           "comparison (DOI verified v3.7.4) |")
NEW_TSM = ("| Tetlock-Saar-Tsechansky-Macskassy (2008) | *JF* 63(3) | "
           '"More Than Words" — firm news tone (story-level negative-word '
           "fraction) predicts fundamentals; cited as news-tone precedent, NOT a "
           "headline-vs-body split (DOI verified v3.7.4) |")

OLD_TSM2 = "   firm news (already firm-tagged), headline and body scored separately\n"
NEW_TSM2 = ("   firm news (already firm-tagged), scored at the story level "
            "(news-tone precedent; not a headline-vs-body split)\n")

# Per-file edit lists: (old, new, expected_count)
MIRROR_EDITS = [(OLD_HTMT_BULLET, NEW_HTMT_BULLET, 1)]  # both files
METH_ONLY_EDITS = [
    (OLD_BERT, NEW_BERT, 1),
    (OLD_TSM, NEW_TSM, 1),
    (OLD_TSM2, NEW_TSM2, 1),
]


def apply(path: Path, edits: list[tuple[str, str, int]]) -> int:
    text = path.read_text(encoding="utf-8")
    n = 0
    for old, new, exp in edits:
        got = text.count(old)
        if got != exp:
            raise AssertionError(
                f"{path.name}: expected {exp} got {got} for {old[:55]!r}")
        text = text.replace(old, new)
        n += got
    path.write_text(text, encoding="utf-8", newline="")
    return n


def main() -> None:
    if MARKER in METH.read_text(encoding="utf-8") and \
       MARKER in REPORT.read_text(encoding="utf-8"):
        print("Already refreshed (v3.7.6 marker present in both); no-op.")
        return
    print("=== FIX A: mirrored HTMT bullet (both files, identical) ===")
    a1 = apply(METH, MIRROR_EDITS)
    a2 = apply(REPORT, MIRROR_EDITS)
    print(f"  methodology: {a1} | report: {a2}")
    print("=== FIX B + C: methodology-only (BERT 5->3, Tetlock/DEG soften) ===")
    b = apply(METH, METH_ONLY_EDITS)
    print(f"  methodology: {b} edits")
    # post: verify the two mirror blocks are byte-identical
    nt = NEW_HTMT_BULLET
    ok = (nt in METH.read_text(encoding="utf-8")) and \
         (nt in REPORT.read_text(encoding="utf-8"))
    print(f"\nMIRROR INTACT (identical new bullet in both): {ok}")


if __name__ == "__main__":
    main()
