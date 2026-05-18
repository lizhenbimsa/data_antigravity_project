"""19_executive_ner.py — thin shim (v3.7.0 PR #13, D4).

实现正文位于 ``news_process.pipeline.sentiment.executive_ner:main``.
启用前置: yunwu API + ~$12 预算 + DC3 archive 已就绪.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.sentiment.executive_ner import main
    main()
