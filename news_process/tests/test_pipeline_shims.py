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


# ---------------------------------------------------------------------------
# D4 (2026-07-18 第六轮审计 C-2): 注册 shim 盘上存在性 + thin 契约 + 35 计数普查。
# 此前 35 个 shim 中仅 4 个 (72/80/81/82) 有存在性守卫; 误删/改名注册 shim 时
# pytest 全绿、只有生产真跑才 fail-loud 暴露。纯静态 (read_text/glob), 零 import。
# ---------------------------------------------------------------------------

def _registered_scripts() -> list:
    from news_process.core import dag as core_dag
    return sorted({s.script for s in core_dag.STAGES_MAIN}
                  | {s.script for s in core_dag.STAGES_VALIDATION})


@pytest.mark.fast
def test_registered_stage_scripts_exist_and_thin() -> None:
    """全部 32 个注册 StageSpec.script 必须在盘且为 thin shim (非空行 ≤30)。"""
    missing, fat = [], []
    for script in _registered_scripts():
        p = _PKG_DIR / script
        if not p.exists():
            missing.append(script)
            continue
        n_nonblank = sum(
            1 for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()
        )
        if n_nonblank > 30:
            fat.append((script, n_nonblank))
    assert not missing, f"注册 shim 缺盘 (orchestrator 子进程按文件名启动必败): {missing}"
    assert not fat, f"shim 超 thin 上限 30 非空行 (业务逻辑应归 pipeline/validation 包): {fat}"


@pytest.mark.fast
def test_numbered_shim_census_is_35() -> None:
    """盘上编号 shim 普查: 恰 35 个 = 32 注册 ∪ {80,81,82} 不注册 (CLAUDE.md 计数不变量)。

    集合恒等同时抓「孤儿 shim」(盘上有但未注册且不在 80/81/82 白名单) 与
    「缺失 shim」(注册了但盘上无)。
    """
    on_disk = {p.name for p in _PKG_DIR.glob("[0-9][0-9]_*.py")}
    expected = set(_registered_scripts()) | set(_SHIMS)
    assert len(on_disk) == 35, f"编号 shim 计数漂移: 期望 35, 实际 {len(on_disk)}"
    assert on_disk == expected, (
        f"编号 shim 集合与注册面不恒等 — 孤儿: {sorted(on_disk - expected)}; "
        f"缺失: {sorted(expected - on_disk)}"
    )
