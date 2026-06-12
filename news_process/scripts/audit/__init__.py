"""news_process.scripts.audit — 手动审计/验证脚本包。

本包内每个脚本都设计为一次性检查, 通过
``python -m news_process.scripts.audit.<script_name>`` 运行。它们**不可**被
pytest 发现: 其模块级执行模型 (失败即 sys.exit、顶层语句直接执行) 与 pytest
的 collection 机制不兼容。

Phase 4e (2026-05-04) 确立本目录为此类非 pytest-discoverable 审计脚本的家
(最初是为了收容那些在模块加载时就调 ``sys.exit(1)`` 从而搞崩 pytest
collection 的脚本)。

Phase 9c (Phase 9 baseline) 删除了其中若干条目 (``audit_changes`` /
``final_integrity``): 它们 grep 的目标 — Phase 7a thin shim — 已不再包含被检
字符串, 这些脚本沦为死代码。保留的 ``audit_deep`` 仍在校验 canonical core
API, 故留存。

白话: 这个目录放的是"手动跑一次看结果"的体检脚本, pytest 不会自动收集它们,
因为它们一加载就直接执行甚至直接退出进程, 会把测试框架带崩。
"""
