"""38b_decay_sensitivity.py — CLI 适配层 shim (Phase 7b).

实现正文已迁至 ``news_process.validation.decay_sensitivity:main``。
历史约定 ``python 38b_decay_sensitivity.py`` 由本文件保留；编排器仍以子进程方式调用该脚本文件名。

建议外部工具改用:
    python -m news_process.validation.decay_sensitivity
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.validation.decay_sensitivity import main
    main()
