"""14_fintech_intensity.py — 已弃用的 CLI 极薄适配层 (Phase 7a-3).

实现正文已迁至 ``news_process.pipeline.filtering.fintech_intensity:main``。
历史约定 ``python 14_fintech_intensity.py`` 由本文件保留；编排器仍以子进程方式调用该脚本文件名。

建议外部工具改用:
    python -m news_process.pipeline.filtering.fintech_intensity

计划于 v3.0 移除。
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.filtering.fintech_intensity import main
    main()
