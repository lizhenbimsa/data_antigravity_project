"""13_cooccurrence_filter.py — stage 13 thin shim.

银行×金科邻近共现硬过滤 (Andreou et al. 2026): 生产默认只保留 "目标银行与 ≥1 金科词在
【±1 句窗口】(命中句前后各 1 句) 内邻近共现" 的文章行 (sentence_radius=1 = ±1 句窗口邻近;
radius=0 严格同句为最严特例稳健性备选), 丢弃其余 —— 降低 stage 12 关键词判定的虚假相关。
实现正文见 ``news_process.pipeline.filtering.cooccurrence_filter:main``。

历史约定 ``python 13_cooccurrence_filter.py`` 由本文件保留; 编排器仍以子进程方式
调用该脚本文件名。建议外部工具改用:
    python -m news_process.pipeline.filtering.cooccurrence_filter
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.filtering.cooccurrence_filter import main
    main()
