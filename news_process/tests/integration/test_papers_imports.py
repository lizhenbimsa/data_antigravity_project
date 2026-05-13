"""Phase 3f 集成测试 — 多论文包导入冒烟测试 (Phase 9a 修订).

红线不变式
----------
1. ``news_process.papers._common`` 与 5 个 paper 包都必须可 import 不报错。
2. 每个 paper 包必须暴露 ``PAPER_ID`` 字符串。
3. 每个 paper 的 ``analysis`` 子模块必须暴露 ``main(argv)`` 函数 +
   ``STAGES`` 列表 (Phase 9a: STAGES 守护从 ``papers.<id>.dag`` 子模块
   迁移至 ``papers.<id>.analysis``; ``dag`` 子模块本身已删除).
4. 每个 paper 的 ``tables`` / ``figures`` 子模块必须可 import (即使依赖
   pandas/matplotlib 也应 lazy 处理, 不在 import-time 触发数据加载)。
5. ``news_process.run_paper`` 顶层调度脚本必须可 import 且 main() 存在。

这些覆盖"软件可装载性"边界 — 任何 import-time 副作用 / 顶层数据 I/O /
循环依赖都会在这里被捕获。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

PROJECT_PARENT = Path(__file__).resolve().parents[3]
if str(PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(PROJECT_PARENT))

from news_process.papers._common.paper_config import _VALID_PAPER_IDS

# ============================================================================
# 1. _common 内核
# ============================================================================


def test_common_kernel_importable():
    mod = importlib.import_module("news_process.papers._common")
    expected_symbols = {
        'PaperConfig', 'get_paper_config', 'get_papers_assets_root',
        'load_panel', 'list_available_panels',
        'sanitize_stata_columns', 'export_dta', 'summary_stats',
        'apply_publication_style', 'COLORBLIND_PALETTE',
        'FIGSIZE_SINGLE', 'FIGSIZE_WIDE', 'FIGSIZE_SQUARE',
        'run_do', 'StataNotFoundError',
    }
    actual = set(getattr(mod, '__all__', []))
    missing = expected_symbols - actual
    assert not missing, f"papers._common 缺少导出符号: {missing}"


# ============================================================================
# 2-4. 5 个 paper 包
# ============================================================================


@pytest.mark.parametrize("paper_id", sorted(_VALID_PAPER_IDS))
def test_paper_package_importable(paper_id: str):
    """整个 paper 包能 import.

    Phase 9a: 取消 ``hasattr(mod, 'dag')`` 子模块断言 — papers.<id>.dag
    子模块在 9a 删除, STAGES 改由 analysis.py 顶部 ``list(STAGES_MAIN)``
    取得.  test_paper_analysis_has_stages_list (下方) 接管 STAGES 守护.
    """
    mod = importlib.import_module(f"news_process.papers.{paper_id}")
    assert hasattr(mod, 'PAPER_ID'), \
        f"{paper_id} 包缺少 PAPER_ID 常量"
    assert paper_id == mod.PAPER_ID, \
        f"{paper_id}.PAPER_ID = {mod.PAPER_ID!r}, 预期 {paper_id!r}"


@pytest.mark.parametrize("paper_id", sorted(_VALID_PAPER_IDS))
def test_paper_analysis_has_stages_list(paper_id: str):
    """Phase 9a: STAGES 守护转移到 analysis 模块.

    每个 paper 的 ``analysis`` 子模块顶部必须暴露 ``STAGES`` 列表
    (由 ``list(STAGES_MAIN)`` 取拷贝). 9a 前由 papers.<id>.dag 子模块
    暴露; 9a 起 STAGES 直接挂在 analysis 模块上.
    """
    analysis_mod = importlib.import_module(
        f"news_process.papers.{paper_id}.analysis"
    )
    assert hasattr(analysis_mod, 'STAGES'), \
        f"{paper_id}.analysis 缺少 STAGES 列表"
    assert isinstance(analysis_mod.STAGES, list), \
        f"{paper_id}.analysis.STAGES 不是 list"
    assert len(analysis_mod.STAGES) > 0, \
        f"{paper_id}.analysis.STAGES 为空"


@pytest.mark.parametrize("paper_id", sorted(_VALID_PAPER_IDS))
def test_paper_analysis_main_callable(paper_id: str):
    analysis_mod = importlib.import_module(
        f"news_process.papers.{paper_id}.analysis"
    )
    assert hasattr(analysis_mod, 'main'), \
        f"{paper_id}.analysis 缺少 main() 入口"
    assert callable(analysis_mod.main), \
        f"{paper_id}.analysis.main 不可调用"


@pytest.mark.parametrize("paper_id", sorted(_VALID_PAPER_IDS))
def test_paper_tables_module_importable(paper_id: str):
    tables_mod = importlib.import_module(
        f"news_process.papers.{paper_id}.tables"
    )
    assert hasattr(tables_mod, 'build_table1'), \
        f"{paper_id}.tables 缺少 build_table1"
    assert hasattr(tables_mod, 'write_table1'), \
        f"{paper_id}.tables 缺少 write_table1"


@pytest.mark.parametrize("paper_id", sorted(_VALID_PAPER_IDS))
def test_paper_figures_module_importable(paper_id: str):
    """figures 模块必须能 import — 即使 matplotlib 未配置后端,
    模块顶层不应触发 plt.show() / 数据 I/O 等副作用。"""
    figures_mod = importlib.import_module(
        f"news_process.papers.{paper_id}.figures"
    )
    # 至少有一个公共绘图函数
    public = [n for n in dir(figures_mod)
              if n.startswith('plot_') and callable(getattr(figures_mod, n))]
    assert public, f"{paper_id}.figures 没有公开绘图函数 (plot_*)"


# ============================================================================
# 5. run_paper.py 顶层调度脚本
# ============================================================================


def test_run_paper_module_importable():
    mod = importlib.import_module("news_process.run_paper")
    assert hasattr(mod, 'main'), "news_process.run_paper 缺少 main"
    assert callable(mod.main), "news_process.run_paper.main 不可调用"


def test_run_paper_list_command_no_crash():
    """``python -m news_process.run_paper --list`` 必须正常退出."""
    mod = importlib.import_module("news_process.run_paper")
    rc = mod.main(['--list'])
    assert rc == 0, f"--list 应该返回 0, 实际 {rc}"


def test_run_paper_rejects_unknown_paper_id():
    mod = importlib.import_module("news_process.run_paper")
    rc = mod.main(['totally_unknown_paper'])
    assert rc == 2, f"未知 paper_id 应返回 exit 2, 实际 {rc}"


@pytest.mark.parametrize("paper_id", sorted(_VALID_PAPER_IDS))
def test_run_paper_dispatches_dry_run(paper_id: str):
    """``python -m news_process.run_paper <paper_id> --dry-run`` 必须返回 0."""
    mod = importlib.import_module("news_process.run_paper")
    rc = mod.main([paper_id, '--dry-run'])
    assert rc == 0, f"{paper_id} dry-run 应返回 0, 实际 {rc}"
