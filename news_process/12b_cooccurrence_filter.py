"""12b_cooccurrence_filter.py — stage 12b thin shim.

银行×金科邻近共现硬过滤 (Andreou et al. 2026): 只保留 "目标银行与 ≥1 金科词在
±sentence_radius 句窗口内邻近共现" 的文章行, 丢弃其余 —— 降低 stage 12 关键词
判定的虚假相关。实现正文见
``news_process.pipeline.filtering.cooccurrence_filter:main``。

历史约定 ``python 12b_cooccurrence_filter.py`` 由本文件保留; 编排器仍以子进程方式
调用该脚本文件名。建议外部工具改用:
    python -m news_process.pipeline.filtering.cooccurrence_filter
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.filtering.cooccurrence_filter import main
    main()
