"""18_article_staleness.py — thin shim (v3.7.0 PR #11+#11.5, D2).

实现正文位于 ``news_process.pipeline.text.article_staleness:main``.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.text.article_staleness import main
    main()
