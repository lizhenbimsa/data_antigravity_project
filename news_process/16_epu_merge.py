"""16_epu_merge.py — thin shim (v3.6.1 PR #5, B1).

实现正文位于 ``news_process.pipeline.external.epu_merge:main``.
保留根目录入口契约: ``python 16_epu_merge.py``.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.external.epu_merge import main
    main()
