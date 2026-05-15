"""Thin shim → news_process.pipeline.audit.inter_track_kappa.

Stage 39a: inter-track Cohen's κ for innovation_locus and
innovation_substantiveness on the llm_verified_dual_both subset.
Plan v1.37 P1 (R7C-01 placement; ≤30 lines per shim invariant).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from news_process.pipeline.audit.inter_track_kappa import run_stage  # noqa: E402

if __name__ == "__main__":
    run_stage()
