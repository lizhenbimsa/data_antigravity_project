"""37_dict_coverage_audit.py — CLI 适配层 shim (Phase 7b).

实现正文已迁至 ``news_process.validation.dict_coverage:main``。
历史约定 ``python 37_dict_coverage_audit.py`` 由本文件保留；编排器仍以子进程方式调用该脚本文件名。

建议外部工具改用:
    python -m news_process.validation.dict_coverage
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.validation.dict_coverage import main
    main()
