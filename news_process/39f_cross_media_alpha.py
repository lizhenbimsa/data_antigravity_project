"""39f_cross_media_alpha.py — thin shim (v3.7.0 PR #12, D3).

⚠️  与 v3.7.0 第 10 篇 bank_media_disagreement 重叠; 启用前对齐 spec.
实现正文位于 ``news_process.pipeline.audit.cross_media_alpha:main``.
详见底层模块 news_process/pipeline/audit/cross_media_alpha.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.cross_media_alpha import main
    main()
