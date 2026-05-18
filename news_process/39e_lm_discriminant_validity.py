"""39e_lm_discriminant_validity.py — thin shim (v3.5.2 PR #4).

实现正文位于 ``news_process.pipeline.audit.lm_discriminant_validity:main``.
保留根目录入口契约: ``python 39e_lm_discriminant_validity.py``.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.lm_discriminant_validity import main
    main()
