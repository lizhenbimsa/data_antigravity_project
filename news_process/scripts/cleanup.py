"""news_process.scripts.cleanup — 数据目录生命周期清理 (Plan-r3 P3-15).

与项目根 ``Makefile`` 等价的纯 Python 实现, 让无 make 工具的 Windows
用户也能用. 调用方式:

    python -m news_process.scripts.cleanup --help
    python -m news_process.scripts.cleanup sizes
    python -m news_process.scripts.cleanup clean-cache
    python -m news_process.scripts.cleanup clean-backup
    python -m news_process.scripts.cleanup clean-derived
    python -m news_process.scripts.cleanup clean-logs
    python -m news_process.scripts.cleanup purge-all  --yes

文档: docs/guides/data_lifecycle.md.
"""

from __future__ import annotations

import argparse
import glob
import logging
import os
import re
import shutil
import sys
from pathlib import Path

logger = logging.getLogger('news_process.scripts.cleanup')


def _root() -> Path:
    """项目根 (含 ``news_process/`` 子目录)."""
    # scripts/cleanup.py -> scripts/ -> news_process/ -> project_root
    return Path(__file__).resolve().parents[2]


def _processed() -> Path:
    return _root() / 'news_process' / 'data' / 'processed'


def _logs() -> Path:
    return _root() / 'news_process' / 'logs'


def _size_mib(p: Path) -> float:
    if not p.exists():
        return 0.0
    if p.is_file():
        return p.stat().st_size / 1024 / 1024
    return sum(f.stat().st_size for f in p.rglob('*') if f.is_file()) / 1024 / 1024


# ----------------------------------------------------------------------------
# stage 14+ 派生文件正则 (与 Makefile clean-derived 对齐).
# ----------------------------------------------------------------------------

_DERIVED_STAGES = [
    '14', '15', '21', '22', '23', '24', '30', '31', '32', '32a', '33',
    '34', '35', '36', '37', '38', '38a', '38b', '39',
    '40', '41', '42', '43', '44', '45', '46', '47',
    '50', '51', '52', '53',
]
_DERIVED_PATTERN = re.compile(
    r'(?:'
    + '|'.join(re.escape(s) for s in _DERIVED_STAGES)
    + r')_'
)


def _derived_files() -> list[Path]:
    proc = _processed()
    if not proc.exists():
        return []
    files: list[Path] = []
    for f in proc.iterdir():
        if not f.is_file():
            continue
        if f.suffix not in ('.parquet', '.csv', '.dta'):
            continue
        if _DERIVED_PATTERN.match(f.name):
            files.append(f)
    return files


# ----------------------------------------------------------------------------
# Targets.
# ----------------------------------------------------------------------------


def cmd_sizes(_args: argparse.Namespace) -> int:
    proc = _processed()
    print(f"Plan-r3 P3-15 sizes (HEAD 实测, 单位 MiB; 项目根 = {_root()})")
    print(f"  _cache/             : {_size_mib(proc / '_cache'):.1f}")
    print(f"  _llm_cache.db       : {_size_mib(proc / '_llm_cache.db'):.1f}")
    bk_total = sum(_size_mib(Path(p)) for p in glob.glob(str(proc / '_backup_*')))
    print(f"  _backup_* (合计)    : {bk_total:.1f}")
    derived = _derived_files()
    derived_total = sum(_size_mib(f) for f in derived)
    print(f"  stage 14+ derived  : {derived_total:.1f}  ({len(derived)} files)")
    print(f"  logs/               : {_size_mib(_logs()):.1f}")
    return 0


def cmd_clean_cache(_args: argparse.Namespace) -> int:
    proc = _processed()
    cache = proc / '_cache'
    db = proc / '_llm_cache.db'
    if cache.exists():
        shutil.rmtree(cache)
        print(f"  ✓ {cache} 已删除")
    else:
        print(f"  - {cache} 不存在, skipped")
    if db.exists():
        db.unlink()
        print(f"  ✓ {db} 已删除")
    else:
        print(f"  - {db} 不存在, skipped")
    return 0


def cmd_clean_backup(_args: argparse.Namespace) -> int:
    proc = _processed()
    paths = [Path(p) for p in glob.glob(str(proc / '_backup_*'))]
    if not paths:
        print("  - 无 _backup_* 目录, skipped")
        return 0
    for p in paths:
        shutil.rmtree(p)
        print(f"  ✓ {p} 已删除")
    return 0


def cmd_clean_derived(_args: argparse.Namespace) -> int:
    files = _derived_files()
    if not files:
        print("  - 无 stage 14+ 派生文件, skipped")
        return 0
    for f in files:
        f.unlink()
    print(f"  ✓ {len(files)} 个 stage 14+ 派生文件已删除")
    return 0


def cmd_clean_logs(_args: argparse.Namespace) -> int:
    logs = _logs()
    if logs.exists():
        shutil.rmtree(logs)
    logs.mkdir(parents=True, exist_ok=True)
    print(f"  ✓ {logs} 已清空")
    return 0


def cmd_purge_all(args: argparse.Namespace) -> int:
    if not args.yes:
        print("DANGER: purge-all 会删除全部派生数据 + 缓存 + 备份 + 日志.")
        print("加 --yes 显式确认后再执行.")
        return 2
    cmd_clean_cache(args)
    cmd_clean_backup(args)
    cmd_clean_derived(args)
    cmd_clean_logs(args)
    print("\nPlan-r3 P3-15: purge-all 完成. 下一次 run_pipeline_function.py 会从 "
          "stage 11/12 (上游 parquet) 重建全部派生数据.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.scripts.cleanup',
        description='news_process 数据目录生命周期 cleanup (Plan-r3 P3-15).',
    )
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('sizes', help='显示可清理体积').set_defaults(func=cmd_sizes)
    sub.add_parser('clean-cache', help='删除 _cache + _llm_cache.db').set_defaults(func=cmd_clean_cache)
    sub.add_parser('clean-backup', help='删除 _backup_*').set_defaults(func=cmd_clean_backup)
    sub.add_parser('clean-derived', help='删除 stage 14+ 派生 parquet/csv/dta').set_defaults(func=cmd_clean_derived)
    sub.add_parser('clean-logs', help='清空 logs/').set_defaults(func=cmd_clean_logs)
    p = sub.add_parser('purge-all', help='全部 cleanup 并集 (DANGER)')
    p.add_argument('--yes', action='store_true', help='显式确认')
    p.set_defaults(func=cmd_purge_all)

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(name)s] %(levelname)s %(message)s')
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
