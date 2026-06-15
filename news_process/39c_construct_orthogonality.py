"""Thin shim → news_process.pipeline.audit.construct_orthogonality.

Stage 39c: NMI 三 construct 正交性测度 + permutation null distribution.
v3.5.0 D3 stage 39c (实现见 news_process.pipeline.audit.construct_orthogonality;
DAG 注册见 core/dag.py::STAGES_VALIDATION 'construct_orthogonality').
Plan v11 §2.2.1 + B-NEW-5 (39c 紧跟 39a/39 validation 序列, 避开 40 panel_export).
≤30 lines per shim invariant.
详见底层模块 news_process/pipeline/audit/construct_orthogonality.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
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
