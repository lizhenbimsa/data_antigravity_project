"""tests/test_papers_bank_fintech_tone.py — V8 P-3 main paper smoke tests.

`bank_fintech_tone` 是主线论文模块, 此前在 tests/ 中**零覆盖**. 5 个 papers/
模块里只有 strategic_diff + benefit_society 有 embedding-相关单元测试,
papers_common 有共享工具测试; main paper 自身的 analysis.py / figures.py /
tables.py 入口完全无保护, 任何 import error / 拼写错误都要靠手动 CLI 才能发现.

参照 tests/test_stage_smoke.py 的 P1-8 pattern (Plan-r3), 提供两类保护:
  1. 模块可 import (无 import-time KeyError / 循环依赖崩溃 / 顶层 IO)
  2. analysis.main 可调用 (CLI 契约, --dry-run 模式不实际跑 pipeline)

不验证 Stata 数学正确性 (那需要完整数据), 但任何 silent break (重命名 main /
改 STAGES 类型 / 砍掉 --dry-run 等) 都会立即被 CI 抓到.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


@pytest.mark.parametrize("submodule", [
    "news_process.papers.bank_fintech_tone",
    "news_process.papers.bank_fintech_tone.analysis",
    "news_process.papers.bank_fintech_tone.figures",
    "news_process.papers.bank_fintech_tone.tables",
])
def test_module_importable(submodule):
    """4 个 paper-level module 全部可 import (含 __init__)."""
    mod = importlib.import_module(submodule)
    assert mod is not None
    # 防止 placeholder/空模块: 至少要有 __name__
    assert getattr(mod, "__name__", None) == submodule


def test_analysis_main_is_callable():
    """analysis.main 必须是可调用 (CLI 契约)."""
    from news_process.papers.bank_fintech_tone import analysis
    assert callable(analysis.main)


def test_analysis_stages_is_list_copy_of_main_dag():
    """STAGES 是 STAGES_MAIN 的 list 拷贝 (Phase 9a 契约: 不共享底层 list 引用)."""
    from news_process.core.dag import STAGES_MAIN
    from news_process.papers.bank_fintech_tone import analysis
    assert isinstance(analysis.STAGES, list)
    assert len(analysis.STAGES) > 0
    assert len(analysis.STAGES) == len(STAGES_MAIN)
    # 不是同一对象 (list 拷贝)
    assert analysis.STAGES is not STAGES_MAIN


def test_analysis_dry_run_pipeline_returns_zero():
    """analysis.main(['--dry-run', '--stage', 'pipeline']) 不实跑, 退出 0."""
    from news_process.papers.bank_fintech_tone import analysis
    rc = analysis.main(['--dry-run', '--stage', 'pipeline'])
    assert rc == 0


@pytest.mark.parametrize("stage", ["pipeline", "tables", "figures", "all"])
def test_analysis_dry_run_accepts_all_stage_choices(stage):
    """全部 4 个 --stage 值在 --dry-run 下都返回 0."""
    from news_process.papers.bank_fintech_tone import analysis
    rc = analysis.main(['--dry-run', '--stage', stage])
    assert rc == 0
