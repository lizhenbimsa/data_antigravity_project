"""check_prompt_headers — 校验 prompt 模板首行版本头.

P1-1 (cleanup/2026-05-13) 配套 lint 工具.

背景
----
``core.config._inline_external_prompts`` 解析 ``# version: <token>`` 首行后,
把 ``<token>`` 写入 ``<key>_version`` 配置字段, 该字段串入 ``LLMCache.get/put``
的 ``prompt_version`` 维度. 若 prompt 文件缺该头, fallback 为 ``'v0'``;
编辑 prompt 但渲染结果 byte-identical 时, ``v0`` 命名空间下的旧 cache 静默
命中, 污染分析结果.

本脚本扫描 ``config/prompts/`` 下所有 ``.txt`` (``.jinja2`` 暂不在 P3-17 范围),
对缺头者返回非零退出码. 推荐在本地 pre-commit / CI 中执行.

使用
----
    python -m news_process.scripts.lint.check_prompt_headers

退出码
------
0   全部 prompt 都有合法版本头
1   至少一个 prompt 缺头或格式异常
"""

from __future__ import annotations

import os
import re
import sys

_VERSION_HEADER = re.compile(r"^#\s*version:\s*(\S+)\s*\r?\n")


def _project_root() -> str:
    # scripts/lint/check_prompt_headers.py -> scripts/lint/ -> scripts/ -> news_process/
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(here))


def check_prompts() -> int:
    root = _project_root()
    prompts_dir = os.path.join(root, "config", "prompts")
    if not os.path.isdir(prompts_dir):
        print(f"[ERROR] prompts 目录不存在: {prompts_dir}", file=sys.stderr)
        return 1

    missing: list[str] = []
    invalid: list[str] = []
    found: list[tuple[str, str]] = []

    for fname in sorted(os.listdir(prompts_dir)):
        if not fname.endswith(".txt"):
            continue
        path = os.path.join(prompts_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            first = f.readline()
        m = _VERSION_HEADER.match(first)
        if m is None:
            if first.strip().startswith("#"):
                invalid.append(f"{fname}: 首行是注释但不匹配 '# version: <token>' 模式: {first.rstrip()!r}")
            else:
                missing.append(f"{fname}: 缺版本头 (首行非 '# version: ...')")
        else:
            found.append((fname, m.group(1)))

    if found:
        print("[OK] 已找到版本头的 prompt:")
        for fname, ver in found:
            print(f"  {fname}: version={ver}")

    if missing:
        print("\n[FAIL] 缺版本头的 prompt:", file=sys.stderr)
        for line in missing:
            print(f"  {line}", file=sys.stderr)

    if invalid:
        print("\n[FAIL] 格式异常的 prompt:", file=sys.stderr)
        for line in invalid:
            print(f"  {line}", file=sys.stderr)

    if missing or invalid:
        print(
            "\n修复建议: 在 prompt 文件首行加 '# version: vX-YYYY-MM-DD',"
            " 其中 vX 是有意义的版本号 (例 v6-2026-05-13). "
            "见 plan P1-1 与 LLMCache.get/put 的 prompt_version 维度文档.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(check_prompts())
