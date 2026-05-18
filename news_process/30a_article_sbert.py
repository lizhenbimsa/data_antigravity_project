"""30a_article_sbert.py — thin shim (v3.7.0 PR #9).

实现正文位于 ``news_process.pipeline.text.article_sbert:main``.
保留根目录入口契约: ``python 30a_article_sbert.py``.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.text.article_sbert import main
    main()
