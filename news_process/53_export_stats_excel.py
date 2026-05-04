"""53_export_stats_excel.py — 已弃用的 CLI 极薄适配层 (Phase 1.4b pilot).

实现正文已迁至 ``news_process.pipeline.audit.stats_excel:main``。
历史约定 ``python 53_export_stats_excel.py`` 由本文件保留；编排器仍以子进程方式调用该脚本文件名。

建议外部工具改用:
    python -m news_process.pipeline.audit.stats_excel

计划于 v2.0 后移除 (pilot / 早期迁移项)。
"""

import pathlib
import sys

# 将项目父目录置于 sys.path, 使任意 cwd 下 ``import news_process`` 均可解析。
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.stats_excel import main
    main()
