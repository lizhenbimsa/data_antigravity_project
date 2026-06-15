"""24_herd_decay_processor.py — CLI 适配层 shim (Phase 7a-7).

实现正文已迁至 ``news_process.pipeline.sentiment.herd_decay:main``。
历史约定 ``python 24_herd_decay_processor.py`` 由本文件保留；编排器仍以子进程方式调用该脚本文件名。

建议外部工具改用:
    python -m news_process.pipeline.sentiment.herd_decay

详见底层模块 news_process/pipeline/sentiment/herd_decay.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.sentiment.herd_decay import main
    main()
