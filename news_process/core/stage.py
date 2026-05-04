"""news_process.core.stage — 子进程隔离的阶段执行器 + (未来) Stage 基类。

由历史 ``utils/helpers.py:666-752`` 拆分而来。

保留的公开 API: ``run_stage``。

Phase 1 范围: 本文件仅承载 ``run_stage`` (子进程执行器)。
Phase 3 将在此处增加 ``Stage`` 运行时抽象基类 + ``@stage`` 装饰器,
与 ``core/dag.py`` 中声明的 *声明式* ``StageSpec`` 数据类分离。
两个名字 ``Stage`` (运行时基类) 与 ``StageSpec`` (声明式记录) 刻意不同,
以避免命名冲突。
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
    """以隔离的子进程方式运行单个流水线阶段脚本.

    Args:
        stage_script: 文件名 (例如 ``"00_preprocessing.py"``)。
        stage_name:   日志中显示的人类可读阶段名。
        logger:       父进程 logger。
        base_dir:     阶段脚本所在目录; 默认为本文件所属包的父目录
                      (即项目根)。
        timeout:      子进程硬超时, 单位为秒。

    Returns:
        (success: bool, elapsed_seconds: float)

    子进程从父进程继承 ``NEWS_PROCESS_RUN_ID`` (以及其他全部 env 变量),
    使得每次运行的日志目录自动传播。
    """
    if base_dir is None:
        # core/stage.py -> core/ -> news_process/  (上溯一层到项目根)
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

    # 显式传播 run_id (防御性写法 — subprocess.run 默认已继承 env,
    # 但此处显式物化, 便于日志可读性)。
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
