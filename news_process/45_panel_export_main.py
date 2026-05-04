"""45_panel_export_main.py — 已弃用的 CLI 极薄适配层 (Phase 2a).

实现正文已迁至 ``news_process.pipeline.panel.runner:main``。
历史约定 ``python 45_panel_export_main.py`` 由本文件保留；编排器仍以子进程方式调用该脚本文件名。

建议外部工具改用:
    python -m news_process.pipeline.panel.runner

计划于 v2.0 后移除 (pilot / 早期迁移项)。
"""

import pathlib
import sys

# 将项目父目录置于 sys.path, 使 ``import news_process`` 与 cwd 无关。
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.panel.runner import main
    main()
