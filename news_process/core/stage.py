"""news_process.core.stage — subprocess-isolated stage runner + (future) Stage base.

Split from legacy ``utils/helpers.py:666-752``.

Public API preserved: ``run_stage``.

Phase 1 scope: this file hosts ``run_stage`` only (subprocess executor).
Phase 3 will add a ``Stage`` runtime abstract base class + ``@stage`` decorator
here, separately from the *declarative* ``StageSpec`` data class declared in
``core/dag.py``.  The two names ``Stage`` (runtime base) vs ``StageSpec``
(declarative record) are intentionally distinct to avoid collision.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time

from .logging import log_memory_usage, get_run_id


def run_stage(stage_script: str, stage_name: str, logger,
              base_dir: str | None = None,
              timeout: int = 3600) -> tuple[bool, float]:
    """Run a single pipeline stage script as an isolated subprocess.

    Args:
        stage_script: filename (e.g. ``"00_preprocessing.py"``).
        stage_name:   human-readable display name for log lines.
        logger:       parent logger.
        base_dir:     directory containing the stage script; defaults to the
                      project root (parent of this file's package).
        timeout:      hard subprocess timeout in seconds.

    Returns:
        (success: bool, elapsed_seconds: float)

    The child process inherits ``NEWS_PROCESS_RUN_ID`` (and all other env
    vars) from the parent, so per-run log directories propagate
    automatically.
    """
    if base_dir is None:
        # core/stage.py -> core/ -> news_process/  (one level up to project root)
        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

    script_path = os.path.join(base_dir, stage_script)

    if not os.path.exists(script_path):
        logger.error(f"阶段脚本未找到: {script_path}")
        return False, 0.0

    logger.info(f"{'─'*60}")
    logger.info(f"▶ 开始执行: {stage_name} ({stage_script})")
    logger.info(f"{'─'*60}")
    log_memory_usage(logger, f"阶段 {stage_name} 开始前")

    # Ensure run_id is propagated explicitly (defensive — subprocess.run
    # already inherits env, but we materialize it here for clarity in logs).
    env = os.environ.copy()
    run_id = get_run_id()
    if run_id:
        env["NEWS_PROCESS_RUN_ID"] = run_id

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True, text=True,
            encoding='utf-8', errors='replace',
            timeout=timeout,
            env=env,
        )
        elapsed = time.time() - start_time

        if result.returncode == 0:
            logger.info(
                f"✓ {stage_name} 执行成功（耗时 {elapsed:.1f}s）"
            )
            return True, elapsed
        else:
            logger.error(
                f"✗ {stage_name} 执行失败（返回码 {result.returncode}）"
            )
            if result.stderr:
                stderr_lines = result.stderr.strip().split('\n')
                last_lines = stderr_lines[-30:]
                logger.error("最后 30 行 stderr:")
                for line in last_lines:
                    logger.error(f"  | {line}")
            return False, elapsed

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        logger.error(
            f"✗ {stage_name} 执行超时（超过 {timeout}s），已强制终止"
        )
        return False, elapsed

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"✗ {stage_name} 执行异常: {e}")
        return False, elapsed
