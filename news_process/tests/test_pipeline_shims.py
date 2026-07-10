"""不注册 shim (80/81/82) 的退出码契约 gate (G1, 八入口审计计划 2026-07-10)。

背景: 81/82 shim 曾裸调 ``main()`` 丢弃返回值 → 底层审计发现 FAIL (return 1)
时进程仍退 0, 外层看退出码必漏报 ("报警器没装电池")。修复 = 三个 user-CLI/
audit-only shim 统一以 ``sys.exit(main())`` 收尾 (与 80 shim 既有口径拉齐)。

本 gate 用文本断言锁死该契约 — 纯静态, 不 import shim (import 会触发
``sys.path`` 注入副作用), 不跑管道。
"""

from __future__ import annotations

from pathlib import Path

import pytest

# tests/ 的父目录 = news_process 包目录 (shim 所在地)
_PKG_DIR = Path(__file__).resolve().parents[1]

_SHIMS = [
    "80_placebo_and_alt_anchor.py",
    "81_stata_data_audit.py",
    "82_export_stats_excel.py",
]


@pytest.mark.fast
@pytest.mark.parametrize("shim_name", _SHIMS)
def test_unregistered_shim_propagates_exit_code(shim_name: str) -> None:
    """三个不注册 shim 必须以 sys.exit(main()) 收尾, 传播底层退出码。"""
    shim_path = _PKG_DIR / shim_name
    assert shim_path.exists(), f"shim 不在盘: {shim_path}"
    text = shim_path.read_text(encoding="utf-8")
    assert "sys.exit(main())" in text, (
        f"{shim_name} 未以 sys.exit(main()) 传播退出码 — 裸调 main() 会吞掉"
        " FAIL 返回码 (G1, 八入口审计计划 2026-07-10)"
    )
    # 反向: 收尾行不得是裸 main() (排除 docstring/注释里的字样, 只看代码尾部)
    code_lines = [
        ln.strip() for ln in text.splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    assert code_lines[-1] == "sys.exit(main())", (
        f"{shim_name} 最后一条代码语句应为 sys.exit(main()), 实为: {code_lines[-1]!r}"
    )
