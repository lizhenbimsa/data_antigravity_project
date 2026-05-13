"""tests/test_papers_derived_smoke.py — Priority B 4 个衍生论文 smoke.

V8 P-3 (commit 79553a2) 给主论文 ``bank_fintech_tone`` 加了 11 smoke 测试,
但 4 个衍生论文 (benefit_society / brokerage_network / llm_peer / strategic_diff)
仍是零测试覆盖. 4 个模块结构 100% 同构 (analysis/figures/tables + STAGES
契约), 用 ``pytest.mark.parametrize`` 一个文件覆盖全部, 比 4 单独文件 DRY 80%.

每个论文的保护与 P-3 一致:
  1. 包 import 不崩 (无 import-time 副作用)
  2. analysis / figures / tables 三个 submodule import 不崩
  3. analysis.main 可调用 (CLI 契约)
  4. STAGES 是 STAGES_MAIN 的 list-copy (Phase 9a 契约)
  5. analysis.main --dry-run 对所有 4 个 stage 选项返回 0

不验证 paper-specific Stata 数学正确性 (那需要完整数据 + 各论文专属
mock); 此 file 是 import-time 防回归 + CLI 契约校验.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


DERIVED_PAPERS = ['benefit_society', 'brokerage_network', 'llm_peer', 'strategic_diff']
SUBMODULES = ['', '.analysis', '.figures', '.tables']  # '' = 包本身


@pytest.mark.parametrize("paper", DERIVED_PAPERS)
@pytest.mark.parametrize("sub", SUBMODULES)
def test_module_importable(paper, sub):
    """4 个衍生论文 × 4 个 module = 16 import smoke."""
    name = f"news_process.papers.{paper}{sub}"
    mod = importlib.import_module(name)
    assert mod is not None
    assert getattr(mod, "__name__", None) == name


@pytest.mark.parametrize("paper", DERIVED_PAPERS)
def test_analysis_main_is_callable(paper):
    """analysis.main 必须是可调用对象 (CLI 契约)."""
    mod = importlib.import_module(f"news_process.papers.{paper}.analysis")
    assert callable(mod.main)


@pytest.mark.parametrize("paper", DERIVED_PAPERS)
def test_analysis_stages_is_list_copy_of_main_dag(paper):
    """STAGES 是 STAGES_MAIN 的 list 拷贝, 不共享底层 list 引用 (Phase 9a)."""
    from news_process.core.dag import STAGES_MAIN
    mod = importlib.import_module(f"news_process.papers.{paper}.analysis")
    assert isinstance(mod.STAGES, list)
    assert len(mod.STAGES) > 0
    assert len(mod.STAGES) == len(STAGES_MAIN)
    assert mod.STAGES is not STAGES_MAIN


@pytest.mark.parametrize("paper", DERIVED_PAPERS)
@pytest.mark.parametrize("stage", ["pipeline", "tables", "figures", "all"])
def test_analysis_dry_run_returns_zero(paper, stage):
    """analysis.main(['--dry-run', '--stage', X]) 对所有 4 stage 返回 0.

    覆盖 4 papers × 4 stages = 16 测试. dry-run 不实跑 pipeline / 表/图,
    仅打印 DAG 与计划; 任何 import 链断裂 / argparse 改动 / paper_config
    KeyError 都会被这条捕获.
    """
    mod = importlib.import_module(f"news_process.papers.{paper}.analysis")
    rc = mod.main(['--dry-run', '--stage', stage])
    assert rc == 0, f"papers.{paper}.analysis.main --stage {stage} 返回 {rc} 而非 0"
