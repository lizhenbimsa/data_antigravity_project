# -*- coding: utf-8 -*-
"""
APEP 生产基础设施 — R 脚本执行器
==========================================
通过子进程安全地调用 Rscript，捕获输出并验证结果。
"""

import subprocess
import time
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from config import setup_logging

logger = setup_logging("apep.r_executor")


@dataclass
class RExecutionResult:
    """R 脚本执行结果"""
    success: bool
    script: str
    stdout: str
    stderr: str
    exit_code: int
    duration_seconds: float
    output_files: list  # 执行后检测到的新文件


class RExecutor:
    """
    R 脚本执行器。

    负责在指定工作目录下安全调用 Rscript，
    捕获所有输出，并验证预期的输出文件是否生成。
    """

    def __init__(self, rscript_path: str = "Rscript"):
        self.rscript = rscript_path
        self.available = self._verify_r_installation()

    def _verify_r_installation(self) -> bool:
        """验证 Rscript 是否可用，返回 True/False"""
        try:
            result = subprocess.run(
                [self.rscript, "--version"],
                capture_output=True, text=True, encoding="utf-8", timeout=10
            )
            version_info = result.stderr.strip() or result.stdout.strip()
            logger.info(f"✅ R 环境已就绪: {version_info.split(chr(10))[0]}")
            return True
        except FileNotFoundError:
            logger.warning("⚠️ Rscript 未找到。R 相关阶段将生成代码但跳过执行。")
            return False
        except subprocess.TimeoutExpired:
            logger.warning("⚠️ Rscript --version 响应超时，但可能仍可用。")
            return True

    def execute(
        self,
        script_path: str | Path,
        working_dir: str | Path,
        expected_outputs: Optional[list[str]] = None,
        timeout_minutes: int = 30,
        env_vars: Optional[dict] = None,
    ) -> RExecutionResult:
        """
        执行 R 脚本。

        Args:
            script_path: R 脚本路径（相对于 working_dir 或绝对路径）
            working_dir: 工作目录
            expected_outputs: 预期输出文件列表（相对于 working_dir）
            timeout_minutes: 超时时间（分钟）
            env_vars: 额外的环境变量

        Returns:
            RExecutionResult
        """
        # 如果 R 不可用，返回跳过结果
        if not self.available:
            logger.warning(f"⚠️ R 未安装，跳过脚本执行: {script_path}")
            return RExecutionResult(
                success=False,
                script=str(script_path),
                stdout="",
                stderr="Rscript 未安装，已跳过执行。请安装 R 语言环境。",
                exit_code=-2,
                duration_seconds=0,
                output_files=[],
            )
        script_path = Path(script_path)
        working_dir = Path(working_dir)

        if not working_dir.exists():
            raise FileNotFoundError(f"工作目录不存在: {working_dir}")

        # 确定脚本完整路径
        if not script_path.is_absolute():
            full_script = working_dir / script_path
        else:
            full_script = script_path

        if not full_script.exists():
            raise FileNotFoundError(f"R 脚本不存在: {full_script}")

        logger.info(f"🔬 执行 R 脚本: {script_path}")
        logger.info(f"   工作目录: {working_dir}")

        # 记录执行前的文件快照
        pre_files = self._snapshot_files(working_dir)

        # 构建环境变量
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        # 执行
        t0 = time.time()
        try:
            result = subprocess.run(
                [self.rscript, str(full_script)],
                cwd=str(working_dir),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=timeout_minutes * 60,
                env=env,
            )
            duration = time.time() - t0

            # 记录执行后的新文件
            post_files = self._snapshot_files(working_dir)
            new_files = sorted(post_files - pre_files)

            exec_result = RExecutionResult(
                success=result.returncode == 0,
                script=str(script_path),
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration_seconds=duration,
                output_files=new_files,
            )

            if exec_result.success:
                logger.info(
                    f"✅ 脚本执行成功 ({duration:.1f}s) | "
                    f"新文件: {len(new_files)}"
                )
            else:
                logger.error(
                    f"❌ 脚本执行失败 (exit={result.returncode}) | "
                    f"stderr: {(result.stderr or '')[:500]}"
                )

            # 验证预期输出
            if expected_outputs and exec_result.success:
                self._verify_outputs(working_dir, expected_outputs, exec_result)

            return exec_result

        except subprocess.TimeoutExpired:
            duration = time.time() - t0
            logger.error(f"⏰ 脚本执行超时 ({timeout_minutes} 分钟)")
            return RExecutionResult(
                success=False,
                script=str(script_path),
                stdout="",
                stderr=f"执行超时 ({timeout_minutes} 分钟)",
                exit_code=-1,
                duration_seconds=duration,
                output_files=[],
            )

    def execute_pipeline(
        self,
        working_dir: str | Path,
        scripts: list[dict],
    ) -> list[RExecutionResult]:
        """
        按顺序执行多个 R 脚本（流水线模式）。

        Args:
            working_dir: 工作目录
            scripts: 脚本列表，每项为 dict:
                     {"path": "code/01_fetch_data.R",
                      "expected_outputs": ["output/panel_data.rds"],
                      "timeout_minutes": 30}

        Returns:
            所有执行结果的列表
        """
        results = []
        for i, script_info in enumerate(scripts, 1):
            logger.info(f"\n{'='*50}")
            logger.info(f"📌 流水线步骤 {i}/{len(scripts)}: {script_info['path']}")
            logger.info(f"{'='*50}")

            result = self.execute(
                script_path=script_info["path"],
                working_dir=working_dir,
                expected_outputs=script_info.get("expected_outputs"),
                timeout_minutes=script_info.get("timeout_minutes", 30),
            )
            results.append(result)

            if not result.success:
                logger.error(
                    f"🛑 流水线在步骤 {i} 中断: {script_info['path']}"
                )
                break

        return results

    def _snapshot_files(self, directory: Path) -> set:
        """获取目录下所有文件的快照"""
        files = set()
        for root, dirs, filenames in os.walk(directory):
            for f in filenames:
                files.add(os.path.relpath(os.path.join(root, f), directory))
        return files

    def _verify_outputs(
        self,
        working_dir: Path,
        expected_outputs: list[str],
        result: RExecutionResult,
    ):
        """验证预期输出文件是否存在"""
        missing = []
        for out in expected_outputs:
            full_path = working_dir / out
            if not full_path.exists():
                missing.append(out)

        if missing:
            logger.warning(
                f"⚠️ 缺少预期输出文件: {missing}"
            )
            result.success = False
        else:
            logger.info(f"✅ 所有预期输出文件已验证: {expected_outputs}")


# ============================================================
# 标准 R 流水线定义
# ============================================================

STANDARD_R_PIPELINE = [
    {
        "path": "code/00_packages.R",
        "expected_outputs": [],
        "timeout_minutes": 10,
    },
    {
        "path": "code/01_fetch_data.R",
        "expected_outputs": ["output/panel_data.rds"],
        "timeout_minutes": 30,
    },
    {
        "path": "code/03_main_analysis.R",
        "expected_outputs": [],  # 动态生成，不易预测
        "timeout_minutes": 30,
    },
    {
        "path": "code/05_figures.R",
        "expected_outputs": [],
        "timeout_minutes": 15,
    },
]


if __name__ == "__main__":
    print("=" * 60)
    print("APEP R 执行器自测")
    print("=" * 60)

    try:
        executor = RExecutor()
        print("✅ R 执行器初始化成功")
        print(f"📋 标准流水线包含 {len(STANDARD_R_PIPELINE)} 个步骤")
    except FileNotFoundError:
        print("❌ R 执行器初始化失败：Rscript 未找到")
