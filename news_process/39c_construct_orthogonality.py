"""Thin shim → news_process.pipeline.audit.construct_orthogonality.

Stage 39c: NMI 三 construct 正交性测度 + permutation null distribution.
v3.5.0 D3 per docs/methodology/stage3_v3_5_0_augmentation_plan.md §2.2.
Plan v11 §2.2.1 + B-NEW-5 (39c 紧跟 39a/39 validation 序列, 避开 40 panel_export).
≤30 lines per shim invariant.
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from news_process.pipeline.audit.construct_orthogonality import run_stage  # noqa: E402

if __name__ == "__main__":
    run_stage()
