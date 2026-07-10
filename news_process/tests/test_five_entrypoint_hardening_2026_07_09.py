"""五入口顺序执行诊断整改 gate (2026-07-09): A2 validation argparse + A3 日志截断时机 + A10 flag 透传。

配套整改批次 3-a(A2) / 3-b(A3) / 3-c(A10)。A5/A9 的锁回归见
tests/test_company_{tax_,}bank_run_pipeline_lock.py。
全 import-only / mock / subprocess-CLI, 绝不实跑 pipeline、不获真锁、不触付费 LLM。
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO = Path(__file__).resolve().parents[1]            # news_process/
_PROJECT_PARENT = Path(__file__).resolve().parents[2]  # repo 根 (news_process 的父)
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


# ── A2: run_pipeline_validation 加了 argparse — --help/--dry-run 不到达 run_validation/不获锁 ──

def test_validation_help_and_dry_run_never_run(tmp_path):
    """A2: --help 打印用法退出 0(不实跑); --dry-run 打印 STAGES_VALIDATION 清单且声明未获锁。
    原文件无 argparse → 任何参数被静默忽略直接全量实跑 + 获锁 + 覆写产物。"""
    py = sys.executable
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "NEWS_PROCESS_LLM_OFFLINE": "1"}
    r = subprocess.run([py, str(REPO / "run_pipeline_validation.py"), "--help"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, env=env)
    assert r.returncode == 0, f"--help 应退出 0, got {r.returncode}: {r.stderr[-500:]}"
    assert "--dry-run" in r.stdout, "--help 未列出 --dry-run 选项"
    r2 = subprocess.run([py, str(REPO / "run_pipeline_validation.py"), "--dry-run"],
                        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, env=env)
    assert r2.returncode == 0
    assert "[dry-run]" in r2.stdout and "未获锁" in r2.stdout, \
        "--dry-run 应打印阶段清单并声明未获锁, 不进入 run_validation 全量实跑"


# ── A3: RUN_ID emit 下沉函数入口 — 模块级(行首无缩进)不再 emit, import 期不截断 .log ──

@pytest.mark.fast
@pytest.mark.parametrize("fname", ["run_pipeline_function.py", "run_pipeline_validation.py"])
def test_run_id_emit_moved_out_of_module_level(fname):
    """A3: 模块级(行首无缩进)不得有 logger.info(NEWS_PROCESS_RUN_ID) —— 那会在 import/--help/
    pytest 收集 / run_paper 懒 import 期触发 _DelayedTruncatingRotatingHandler 首写截断 .log。
    该 emit 必须存在于函数体内(有缩进)。"""
    src = (REPO / fname).read_text(encoding="utf-8")
    module_level = re.search(r'^logger\.info\(f?["\'].*NEWS_PROCESS_RUN_ID', src, re.M)
    assert module_level is None, f"{fname}: 模块级 RUN_ID emit 未下沉 → import 期会截断 .log"
    func_level = re.search(r'^\s+logger\.info\(f?["\'].*NEWS_PROCESS_RUN_ID', src, re.M)
    assert func_level is not None, f"{fname}: RUN_ID emit 应下沉到函数体内(有缩进)"


# ── F4 (2026-07-10): 编排器 `with PipelineLock` 之前不得有 file emit + 须传 console_only_on_reject ──

@pytest.mark.fast
@pytest.mark.parametrize("fname", ["run_pipeline_function.py", "run_pipeline_validation.py"])
def test_no_file_emit_before_pipeline_lock(fname):
    """F4 结构护栏: run_pipeline/run_validation 函数体内 `with PipelineLock` 之前不得有任何
    logger file emit —— 否则被拒并发实例会在获锁前经 delayed-truncating file handler 首写截断
    在跑实例的共享 .log。且该锁须传 console_only_on_reject=True (被拒实例诊断走 stderr 不触盘)。
    防未来在 with 前加日志静默重引截断 bug。"""
    src = (REPO / fname).read_text(encoding="utf-8")
    m = re.search(r'^\s*with PipelineLock\(', src, re.M)
    assert m is not None, f"{fname}: 未找到 with PipelineLock"
    lock_stmt = src[m.start():m.start() + 220]
    assert "console_only_on_reject=True" in lock_stmt, \
        f"{fname}: with PipelineLock 未传 console_only_on_reject=True → 被拒实例仍 logger.error 截断 .log"
    func_start = src.rfind("\ndef ", 0, m.start())
    assert func_start != -1, f"{fname}: 未定位到 with PipelineLock 的宿主函数"
    body_before_lock = src[func_start:m.start()]
    stray = re.search(r'^\s+logger\.(info|warning|error)\(', body_before_lock, re.M)
    assert stray is None, \
        f"{fname}: `with PipelineLock` 之前有 file emit ({stray.group()!r}) → 被拒实例会截断在跑实例 .log"


# ── A10: run_main_pipeline(argv) 透传流水线 flag; argv 空/None 走零参保 bridge ──

@pytest.mark.fast
def test_run_main_pipeline_forwards_flags():
    """A10: 非空 argv → 经 _parse_cli_args 转 Namespace 传 run_pipeline; 空/None → 零参调用
    (保 test_pipeline_runner_bridge 的 assert_called_once_with())。"""
    from news_process.papers._common.pipeline_runner import run_main_pipeline
    with patch("news_process.run_pipeline_function.run_pipeline") as mock_run:
        run_main_pipeline(["--skip-21-if-exists"])
        assert mock_run.call_count == 1
        ns = mock_run.call_args.args[0]
        assert ns.skip_21_if_exists is True, "flag 未透传到 run_pipeline 的 Namespace"
    with patch("news_process.run_pipeline_function.run_pipeline") as mock_run2:
        run_main_pipeline([])
        mock_run2.assert_called_once_with()
    with patch("news_process.run_pipeline_function.run_pipeline") as mock_run3:
        run_main_pipeline(None)
        mock_run3.assert_called_once_with()


@pytest.mark.fast
def test_analysis_forwards_unknown_flags_to_run_main_pipeline():
    """A10: paper analysis.main 用 parse_known_args, 把未知流水线 flag 经 extra 透传给
    run_main_pipeline (原严格 parse_args → --skip-21-if-exists 触 SystemExit(2))。"""
    from news_process.papers.bank_fintech_tone import analysis
    with patch.object(analysis, "run_main_pipeline") as mock_rmp:
        rc = analysis.main(["--stage", "pipeline", "--skip-21-if-exists"])
        assert rc == 0
        mock_rmp.assert_called_once()
        extra = mock_rmp.call_args.args[0]
        assert "--skip-21-if-exists" in extra, "未知 flag 未经 parse_known_args 透传给 run_main_pipeline"
