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


# ============================================================================
# v3.2.0 M7 (plan v14 §9.3): build_replication_package
# ============================================================================

# Plan v14 §9.2 已知占位符白名单 (与 test_stata_templates.py 同源)
_KNOWN_PLACEHOLDERS = {
    'MAIN_LOCUS_TRACK',  # lf / lc
    'MAIN_SUBST_TRACK',  # sf / sc
    'MAIN_SENT_TRACK',   # full / ctx
    'PROJECT_ROOT',      # absolute path
}

_VALID_SPEC_VALUES = {
    'MAIN_LOCUS_TRACK': {'lf', 'lc'},
    'MAIN_SUBST_TRACK': {'sf', 'sc'},
    'MAIN_SENT_TRACK':  {'full', 'ctx'},
}


def _get_git_commit_hash_with_dirty() -> str:
    """Plan v14 §9.3 (R48-A + R49-A): git commit hash + dirty 检测.

    Returns:
        '<hash>' (clean) 或 '<hash>+dirty' (working tree dirty)
    """
    try:
        repo_root = Path(__file__).resolve().parents[3]
        h = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        ).stdout.strip()[:12]
        dirty = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=str(repo_root), capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        return f'{h}+dirty' if dirty else h
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return 'unknown'


def _validate_spec_choices(main_spec_choices: dict) -> None:
    """Plan v14 §9.3: 校验 main spec 选择合法 (避免静默错误占位符)."""
    for key, value in main_spec_choices.items():
        if key not in _KNOWN_PLACEHOLDERS:
            raise ValueError(
                f"未知占位符 key='{key}'. 合法值: {sorted(_KNOWN_PLACEHOLDERS)}"
            )
        if key in _VALID_SPEC_VALUES and value not in _VALID_SPEC_VALUES[key]:
            raise ValueError(
                f"占位符 {key}='{value}' 非法. 合法值: {sorted(_VALID_SPEC_VALUES[key])}"
            )

    required = {'MAIN_LOCUS_TRACK', 'MAIN_SUBST_TRACK', 'MAIN_SENT_TRACK'}
    missing = required - set(main_spec_choices.keys())
    if missing:
        raise ValueError(f"缺必需占位符: {sorted(missing)}")


def _substitute_placeholders(content: str, choices: dict) -> str:
    """{{KEY}} → value 直接替换.

    Args:
        content: 模板文件内容
        choices: 占位符值字典
    Returns:
        替换后内容; 未替换的 {{...}} 抛 ValueError (fail-fast)
    """
    result = content
    for key, value in choices.items():
        result = result.replace(f'{{{{{key}}}}}', str(value))
    # fail-fast: 检测残留未替换占位符
    import re
    leftover = re.findall(r'\{\{([A-Z_]+)\}\}', result)
    if leftover:
        raise ValueError(
            f"占位符未替换完整, 残留: {set(leftover)}. "
            f"检查 _KNOWN_PLACEHOLDERS 与 main_spec_choices 一致性."
        )
    return result


def build_replication_package(
    main_spec_choices: dict,
    output_root: str | Path | None = None,
    template_dir: str | Path | None = None,
) -> Path:
    """生成 v3.2.0 replication 包 (plan v14 §9.3, Action #9 Stata Recommended scope).

    Args:
        main_spec_choices: {'MAIN_LOCUS_TRACK': 'lc', 'MAIN_SUBST_TRACK': 'sf',
                            'MAIN_SENT_TRACK': 'ctx', 'PROJECT_ROOT': '/path/to/repl'}
        output_root: replication 包父目录 (默认 repo_root)
        template_dir: 模板目录 (默认 papers/_common/stata_templates)

    Returns:
        生成的 replication 包目录路径

    工作流 (plan v14 §9.3):
        1. 校验 main_spec_choices (合法占位符 + 合法值)
        2. 实例化目录 replication_v3.2.0_<locus>_<subst>_<sent>/
        3. 复制 / 替换 .do.tmpl → .do
        4. 复制 README.md
        5. 写 README.md 含 git commit hash + dirty 检测
    """
    _validate_spec_choices(main_spec_choices)

    locus = main_spec_choices['MAIN_LOCUS_TRACK']
    subst = main_spec_choices['MAIN_SUBST_TRACK']
    sent  = main_spec_choices['MAIN_SENT_TRACK']

    if template_dir is None:
        template_dir = Path(__file__).resolve().parent / 'stata_templates'
    template_dir = Path(template_dir)
    if not template_dir.is_dir():
        raise FileNotFoundError(f"Template dir not found: {template_dir}")

    if output_root is None:
        output_root = Path(__file__).resolve().parents[3]
    output_root = Path(output_root)

    pkg_dir = output_root / f'replication_v3.2.0_{locus}_{subst}_{sent}'
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / 'code').mkdir(exist_ok=True)
    (pkg_dir / 'data').mkdir(exist_ok=True)
    (pkg_dir / 'output' / 'tables').mkdir(parents=True, exist_ok=True)
    (pkg_dir / 'output' / 'figures').mkdir(parents=True, exist_ok=True)

    # 实例化模板 .do.tmpl → .do
    n_templates = 0
    for tpl_path in sorted(template_dir.glob('*.do.tmpl')):
        out_name = tpl_path.stem  # 去掉 .tmpl 后缀, e.g., 11_table2_main_m1m6.do
        out_path = pkg_dir / 'code' / out_name
        content = tpl_path.read_text(encoding='utf-8')
        substituted = _substitute_placeholders(content, main_spec_choices)
        out_path.write_text(substituted, encoding='utf-8')
        n_templates += 1

    # 复制 README.md (附加 spec choices + commit hash)
    readme_src = template_dir / 'README.md'
    commit_hash = _get_git_commit_hash_with_dirty()
    if readme_src.exists():
        readme_content = readme_src.read_text(encoding='utf-8')
        appendix = f"""

---

## This replication package / 本复现包

- **Generated at**: {commit_hash}
- **Main spec choices** (locked at generation):
  - locus track: `{locus}` ({'full-text' if locus == 'lf' else 'entity-context'} classification)
  - subst track: `{subst}` ({'full-text' if subst == 'sf' else 'entity-context'} classification)
  - sent track:  `{sent}` ({'Hassan 2019 QJE entity-proximity' if sent == 'ctx' else 'full-text'})
- **Templates instantiated**: {n_templates}
- **Plan version**: v14 (62 rounds audit; user confirmed 9 Action Items)
"""
        (pkg_dir / 'README.md').write_text(readme_content + appendix, encoding='utf-8')

    return pkg_dir


__all__ = [
    'StataNotFoundError',
    'discover_stata_bin',
    'run_do',
    'build_replication_package',
    '_validate_spec_choices',  # 测试可见
    '_substitute_placeholders',
]
