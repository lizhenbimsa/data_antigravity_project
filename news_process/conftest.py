"""news_process 包根 conftest (V4 T0.2)。

防止从 news_process/ 子目录启动 pytest 时扫描 data/ (该场景下父级
pyproject.toml 的 testpaths 设置可能不稳定生效)。没有本文件时,
data/processed/test_*.txt 之类的杂散文件会在收集阶段触发
UnicodeDecodeError。

与 tests/conftest.py 共存 — pytest 按层级 conftest 发现机制自动加载
两者, 互不冲突。
"""

# 相对于本 conftest 所在目录 (news_process/), 完整排除 data/*。
collect_ignore_glob = ["data/*"]
