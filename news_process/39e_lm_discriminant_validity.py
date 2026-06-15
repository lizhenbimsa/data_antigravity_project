"""39e_lm_discriminant_validity.py — thin shim (v3.5.2 PR #4).

实现正文位于 ``news_process.pipeline.audit.lm_discriminant_validity:main``.
保留根目录入口契约: ``python 39e_lm_discriminant_validity.py``.
详见底层模块 news_process/pipeline/audit/lm_discriminant_validity.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.lm_discriminant_validity import main
    main()
