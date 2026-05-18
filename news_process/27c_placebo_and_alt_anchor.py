"""27c_placebo_and_alt_anchor.py — thin shim.

V2.0 J-L-M 2026 robustness alignment plan §3 Phase 1 P1.6:
Audit-only pipeline that combines:
  - benefit_society_alt_anchor (J-L-M Appendix A 5-pair alternative family)
  - benefit_society_placebo (4 business-line + 1 neutral filtering)

Writes a single `data/processed/27c_alt_anchor_and_placebo_panel.parquet`
that downstream Stata templates (P2.S1, P2.A2) consume. Does NOT modify
main panel `40_panel_yearly.parquet` or its golden snapshot.
"""

from __future__ import annotations

import sys

from news_process.pipeline.features.benefit_society_audit_combined import main

if __name__ == "__main__":
    sys.exit(main())
