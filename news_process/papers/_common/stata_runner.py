"""news_process.papers._common.stata_runner — 调用本地 Stata 执行 .do 文件.

设计原则
--------
- **零代码侵入**: 现有 ``.do`` 文件不需要任何改造; 本模块仅做进程调度。
- **可发现 / 可覆盖**: Stata 可执行路径优先级
    1. 函数参数 ``stata_bin``
    2. 环境变量 ``NEWS_PROCESS_STATA_BIN``
    3. 自动探测 (Windows: StataMP/SE/IC.exe; Linux/Mac: stata-mp/se/ic)
- **超时与错误**: ``timeout`` 默认 30 分钟, 超时或非零退出抛出
   带清晰诊断信息的异常。
- **可测**: ``stata_bin`` 是显式参数, 单测可注入虚拟可执行路径。
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Sequence


class StataNotFoundError(RuntimeError):
    """无法定位本地 Stata 可执行文件时抛出."""


# Stata 可执行候选名 — 按"专业版/标准版/初级版"优先级递减.
_STATA_CANDIDATES_WINDOWS = (
    'StataMP-64.exe', 'StataMP.exe',
    'StataSE-64.exe', 'StataSE.exe',
    'StataIC-64.exe', 'StataIC.exe',
    'Stata-64.exe', 'Stata.exe',
)
_STATA_CANDIDATES_UNIX = (
    'stata-mp', 'stata-se', 'stata-ic', 'stata',
)


def _is_windows() -> bool:
    return os.name == 'nt'


def _candidates() -> tuple[str, ...]:
    return _STATA_CANDIDATES_WINDOWS if _is_windows() else _STATA_CANDIDATES_UNIX


def discover_stata_bin() -> str | None:
    """探测系统上的 Stata 可执行路径; 找不到返回 ``None``.

    优先级:
        1. 环境变量 ``NEWS_PROCESS_STATA_BIN``
        2. shutil.which() 在 PATH 中按候选名查找
        3. Windows 常见安装目录 (Program Files\\Stata*)
    """
    env_path = os.environ.get('NEWS_PROCESS_STATA_BIN')
    if env_path and os.path.exists(env_path):
        return env_path

    for cand in _candidates():
        found = shutil.which(cand)
        if found:
            return found

    if _is_windows():
        for prog_files in (
            os.environ.get('ProgramFiles', r'C:\Program Files'),
            os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)'),
        ):
            if not prog_files or not os.path.isdir(prog_files):
                continue
            try:
                for sub in os.listdir(prog_files):
                    if sub.lower().startswith('stata'):
                        sub_dir = os.path.join(prog_files, sub)
                        for cand in _candidates():
                            cand_path = os.path.join(sub_dir, cand)
                            if os.path.exists(cand_path):
                                return cand_path
            except OSError:
                pass

    return None


def run_do(do_path: str | Path,
           args: Sequence[str] | None = None,
           *,
           stata_bin: str | None = None,
           cwd: str | Path | None = None,
           timeout: int = 1800,
           batch_mode: bool = True,
           check: bool = True) -> subprocess.CompletedProcess:
    """执行单个 .do 文件.

    Args:
        do_path:     ``.do`` 文件绝对/相对路径。
        args:        传给 .do 的命令行参数 (在 .do 中通过 ``args`` 宏访问)。
        stata_bin:   覆盖 Stata 可执行路径; 为 None 时调用 ``discover_stata_bin()``。
        cwd:         子进程工作目录; 默认是 ``do_path`` 所在目录
                     (.do 中的相对路径才能找到对应数据文件)。
        timeout:     秒, 默认 30 分钟。
        batch_mode:  使用 ``/b`` 批处理模式 (Windows) 或 ``-b`` (Unix)。
        check:       True (默认) 时非零退出抛 CalledProcessError。

    Returns:
        subprocess.CompletedProcess。

    Raises:
        StataNotFoundError:           没找到 Stata 可执行文件。
        FileNotFoundError:            do_path 不存在。
        subprocess.TimeoutExpired:    超时。
        subprocess.CalledProcessError: ``check=True`` 时进程非零退出。
    """
    do_path = Path(do_path).resolve()
    if not do_path.exists():
        raise FileNotFoundError(f"do 文件不存在: {do_path}")

    bin_path = stata_bin or discover_stata_bin()
    if bin_path is None:
        raise StataNotFoundError(
            "未能定位 Stata 可执行文件. 请通过 stata_bin 参数显式指定, "
            "或设置环境变量 NEWS_PROCESS_STATA_BIN, "
            f"或将以下任一文件加入 PATH: {_candidates()}"
        )

    if cwd is None:
        cwd = do_path.parent

    batch_flag = '/b' if _is_windows() else '-b'
    cmd: list[str] = [bin_path]
    if batch_mode:
        cmd.append(batch_flag)
    cmd.append('do')
    cmd.append(str(do_path))
    if args:
        cmd.extend(str(a) for a in args)

    return subprocess.run(
        cmd,
        cwd=str(cwd),
        timeout=timeout,
        check=check,
        capture_output=True,
        text=True,
    )


__all__ = [
    'StataNotFoundError',
    'discover_stata_bin',
    'run_do',
]
