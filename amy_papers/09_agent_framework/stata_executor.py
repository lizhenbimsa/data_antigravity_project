# -*- coding: utf-8 -*-
"""
AutoPaper 生产基础设施 — Stata 脚本执行器
==========================================
通过子进程安全地调用 Stata，捕获输出并验证结果。
"""

import subprocess
import time
import os
import shutil
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from config import setup_logging

logger = setup_logging("paper.stata_executor")


@dataclass
class StataExecutionResult:
    """Stata 脚本执行结果"""
    success: bool
    script: str
    stdout: str
    stderr: str
    exit_code: int
    duration_seconds: float
    output_files: list  # 执行后检测到的新文件


class StataExecutor:
    """
    Stata 脚本执行器。

    负责在指定工作目录下安全调用 Stata 批处理命令，
    捕获 .log 文件中的所有输出，并验证预期的输出文件是否生成。
    """

    def __init__(self, stata_path: Optional[str] = None):
        if stata_path:
            self.stata_cmd = stata_path
            self.available = self._verify_stata_installation(self.stata_cmd)
        else:
            self.stata_cmd, self.available = self._find_stata_installation()

    def _find_stata_installation(self):
        """尝试自动寻找可用的 Stata 可执行文件名称"""
        candidates = [
            "StataMP-64", "StataSE-64", "Stata-64", "stata-mp", "stata-se", "stata", "StataMP-64.exe", "stata.exe",
            r"C:\Program Files\StataNow19\StataMP-64.exe",
            r"C:\Program Files\Stata18\StataMP-64.exe",
            r"C:\Program Files\Stata17\StataMP-64.exe"
        ]
        for cmd in candidates:
            if shutil.which(cmd) or os.path.exists(cmd):
                logger.info(f"✅ 找到 Stata 环境: {cmd}")
                return cmd, True
        logger.warning("⚠️ 未找到常见的 Stata 可执行程序。相关阶段将生成代码但跳过执行。")
        return "stata", False

    def _verify_stata_installation(self, cmd: str) -> bool:
        """验证指定的 Stata 命令行是否可用"""
        if shutil.which(cmd) or os.path.exists(cmd):
            logger.info(f"✅ 找到 Stata 环境: {cmd}")
            return True
        logger.warning(f"⚠️ 指定的 Stata 命令未找到: {cmd}")
        return False

    def execute(
        self,
        script_path: str | Path,
        working_dir: str | Path,
        expected_outputs: Optional[list[str]] = None,
        timeout_minutes: int = 30,
        env_vars: Optional[dict] = None,
    ) -> StataExecutionResult:
        """
        执行 Stata do 脚本。

        Args:
            script_path: Stata do 脚本路径（相对于 working_dir 或绝对路径）
            working_dir: 工作目录
            expected_outputs: 预期输出文件列表（相对于 working_dir）
            timeout_minutes: 超时时间（分钟）
            env_vars: 额外的环境变量

        Returns:
            StataExecutionResult
        """
        # 如果 Stata 不可用，返回跳过结果
        if not self.available:
            logger.warning(f"⚠️ Stata 未安装，跳过脚本执行: {script_path}")
            return StataExecutionResult(
                success=False,
                script=str(script_path),
                stdout="",
                stderr="Stata 未安装或未在 PATH 中，已跳过执行。请配置 Stata 环境变量。",
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
            raise FileNotFoundError(f"Stata 脚本不存在: {full_script}")

        logger.info(f"🔬 执行 Stata 脚本: {script_path}")
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
            # Stata 批处理命令: stata-mp -e do script.do
            # 这会在执行目录下生成一个同名的 .log 文件，例如 01_fetch_data.log
            # 注意: Stata 在批处理模式下如果脚本里没有明确 exit, clear 返回的退出代码可能仍是 0，通过解析 log 是判断错误的最好方法，但为简单我们先依赖返回码
            cmd = [self.stata_cmd, "-e", "do", str(full_script)]
            
            result = subprocess.run(
                cmd,
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
            
            # 读取 log 文件提取 stdout 
            # Stata 会在执行当前工作目录下生成一个于 do-file 同名的 log 文件
            log_stdout = ""
            log_file_name = full_script.stem + ".log"
            log_file_path = working_dir / log_file_name
            if log_file_path.exists():
                try:
                    log_stdout = log_file_path.read_text(encoding="utf-8", errors="replace")
                    
                    # 移动 log 文件到专门的 log 文件夹
                    log_target_dir = working_dir / "log"
                    log_target_dir.mkdir(exist_ok=True, parents=True)
                    shutil.move(str(log_file_path), str(log_target_dir / log_file_name))
                except Exception as e:
                    log_stdout = f"[Error reading or moving Stata log file: {e}]"

            # 简单的错误捕获，若带有 r(xxx); 一般为 stata 错误
            has_error = False
            if result.returncode != 0 or ("r(" in log_stdout and ");" in log_stdout):
                has_error = True
                
            exec_result = StataExecutionResult(
                success=not has_error,
                script=str(script_path),
                stdout=log_stdout or result.stdout,
                stderr=result.stderr,
                exit_code=1 if has_error else 0,
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
                    f"❌ 脚本执行可能失败 (exit={result.returncode} or found r() code in log) | "
                    f"请检查生成的 {log_file_name}"
                )

            # 验证预期输出
            if expected_outputs and exec_result.success:
                self._verify_outputs(working_dir, expected_outputs, exec_result)

            return exec_result

        except subprocess.TimeoutExpired:
            duration = time.time() - t0
            logger.error(f"⏰ 脚本执行超时 ({timeout_minutes} 分钟)")
            return StataExecutionResult(
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
    ) -> list[StataExecutionResult]:
        """
        按顺序执行多个 Stata 脚本（流水线模式）。

        Args:
            working_dir: 工作目录
            scripts: 脚本列表，每项为 dict:
                     {"path": "code/01_fetch_data.do",
                      "expected_outputs": ["data/clean_data.dta"],
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
        result: StataExecutionResult,
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
# 标准 Stata 流水线定义
# ============================================================

STANDARD_STATA_PIPELINE = [
    {
        "path": "code/00_packages.do",
        "expected_outputs": [],
        "timeout_minutes": 10,
    },
    {
        "path": "code/01_fetch_data.do",
        "expected_outputs": [],
        "timeout_minutes": 30,
    },
    {
        "path": "code/03_main_analysis.do",
        "expected_outputs": [],  # 动态生成，不易预测
        "timeout_minutes": 30,
    },
    {
        "path": "code/05_figures.do",
        "expected_outputs": [],
        "timeout_minutes": 15,
    },
]


if __name__ == "__main__":
    print("=" * 60)
    print("AutoPaper Stata 执行器自测")
    print("=" * 60)

    executor = StataExecutor()
    if executor.available:
        print(f"✅ Stata 执行器初始化成功，使用执行程序: {executor.stata_cmd}")
        print(f"📋 标准流水线包含 {len(STANDARD_STATA_PIPELINE)} 个步骤")
    else:
        print("❌ Stata 执行器初始化失败：未找到 Stata 可执行程序")
