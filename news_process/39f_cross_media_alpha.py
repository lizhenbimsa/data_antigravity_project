"""39f_cross_media_alpha.py — thin shim (v3.7.0 PR #12, D3).

⚠️  与 v3.7.0 第 10 篇 bank_media_disagreement 重叠; 启用前对齐 spec.
实现正文位于 ``news_process.pipeline.audit.cross_media_alpha:main``.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.cross_media_alpha import main
    main()
