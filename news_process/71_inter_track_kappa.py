"""Thin shim → news_process.pipeline.audit.inter_track_kappa。

Stage 71: 在 llm_verified_dual_both 子集上对 innovation_locus /
innovation_substantiveness / collab_mode 三维计算双轨 (inter-track) Cohen's κ。
Plan v1.37 P1 (R7C-01 placement; shim 不变式 ≤30 行)。
详见底层模块 news_process/pipeline/audit/inter_track_kappa.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
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
