"""scripts/audit/loc_summation_check.py — v3.7.4 L4 lint 脚本.

LOC 加和链检查器 (LOC summation chain checker)。

强制执行 LOC-summation lint 协议: 在标记区段内, 任何形如
"N+N+...+N = M" 的加和链必须满足 左侧各项之和 == M
(即声明的总数 M 必须等于左侧各加数之和)。

标记 (Marker):
    <!-- loc-summation-check -->
    ... 含加和链的 markdown 内容 ...
    <!-- /loc-summation-check -->

命令行开关 (8R-A2 stdin + 8R-B2 self-check):
    --from-stdin : 从 stdin 读文档内容, 而非文件路径
    --self-check : 校验本脚本自身行数与声明值 DECLARED_LOC 一致
                   (容差 ±5 行; 白话: 防止文档里写的脚本行数与实际脱节)

退出码:
    0 = 全部加和链有效
    1 = 至少一处违规 (有算错的加法)
    2 = self-check 失败 (脚本自身行数与声明不符)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# 8R-B2 self-check 锚点: 自引用 LOC 锚 (无外部 plan 文档可对照; docs/ 已删)
DECLARED_LOC = 147  # Round 57 给 3 个公开函数补 docstring 后的实际行数;
                    # Round-57 前为 136; 当时 self-check 在 diff>5 时正确报警,
                    # 证明 4.D 机械强制机制有效。(翻译注释时须保持总行数 ±5 内)
TOLERANCE = 5

MARKER_OPEN = "<!-- loc-summation-check -->"
MARKER_CLOSE = "<!-- /loc-summation-check -->"

# 匹配如 "60 + 30 + 20 = 110" 或 "60+30+20=110"; 允许 Unicode 减号 −
CHAIN_RE = re.compile(
    r"(?P<lhs>(?:\d+(?:\s*[+\-−]\s*\d+)+))\s*=\s*(?P<rhs>\d+)"
)


def extract_marked_sections(text: str) -> list[str]:
    """返回所有 MARKER_OPEN 与 MARKER_CLOSE 配对之间的内容切片列表。

    未闭合的开标记会捕获从 MARKER_OPEN 到文件末尾的全部内容。
    """
    sections: list[str] = []
    idx = 0
    while True:
        a = text.find(MARKER_OPEN, idx)
        if a < 0:
            break
        b = text.find(MARKER_CLOSE, a)
        if b < 0:
            # 未闭合标记: 纳入文件剩余全部内容
            sections.append(text[a + len(MARKER_OPEN):])
            break
        sections.append(text[a + len(MARKER_OPEN):b])
        idx = b + len(MARKER_CLOSE)
    return sections


def evaluate_chain(lhs: str) -> int:
    """求值 'A+B-C+D' 形式的整数表达式 (支持 Unicode 减号)。"""
    # 把 Unicode 减号归一化为 ASCII 减号
    norm = lhs.replace("−", "-")
    # 按 +/- 切分为项; 首项隐含 + 号
    parts = re.split(r"\s*([+\-])\s*", norm)
    total = int(parts[0])
    for i in range(1, len(parts) - 1, 2):
        op, num = parts[i], parts[i + 1]
        if op == "+":
            total += int(num)
        else:
            total -= int(num)
    return total


def check_text(text: str, src: str = "<stdin>") -> list[tuple[str, str, int, int]]:
    """返回违规列表: (src, lhs, 实算和, 声明值)。"""
    violations: list[tuple[str, str, int, int]] = []
    sections = extract_marked_sections(text)
    if not sections:
        return violations
    for section in sections:
        for m in CHAIN_RE.finditer(section):
            lhs = m.group("lhs").strip()
            declared = int(m.group("rhs"))
            actual = evaluate_chain(lhs)
            if actual != declared:
                violations.append((src, lhs, actual, declared))
    return violations


def self_check() -> int:
    """8R-B2: 校验本脚本自身行数与 DECLARED_LOC ± TOLERANCE 相符。"""
    self_path = Path(__file__)
    actual_loc = sum(1 for _ in self_path.open(encoding="utf-8"))
    diff = abs(actual_loc - DECLARED_LOC)
    if diff > TOLERANCE:
        print(f"[self-check FAIL] {self_path.name} actual={actual_loc} declared={DECLARED_LOC} "
              f"diff={diff} > tolerance={TOLERANCE}", file=sys.stderr)
        return 2
    print(f"[self-check OK] actual={actual_loc} declared={DECLARED_LOC} diff={diff}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI 入口: 解析参数, 执行检查, 返回退出码。

    退出码 0 = 干净; 1 = 至少一处加和违规; 2 = self-check 失败。
    """
    p = argparse.ArgumentParser(description="LOC summation chain checker (v3.7.4 4.D)")
    p.add_argument("paths", nargs="*", help="Markdown files to check")
    p.add_argument("--from-stdin", action="store_true", help="read content from stdin")
    p.add_argument("--self-check", action="store_true", help="verify self LOC")
    args = p.parse_args(argv)

    if args.self_check:
        return self_check()

    all_violations: list[tuple[str, str, int, int]] = []
    if args.from_stdin:
        all_violations.extend(check_text(sys.stdin.read(), src="<stdin>"))
    for path_str in args.paths:
        path = Path(path_str)
        if not path.exists():
            print(f"[skip] {path} not found", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8")
        all_violations.extend(check_text(text, src=str(path)))

    if all_violations:
        for src, lhs, actual, declared in all_violations:
            print(f"[VIOLATION] {src}: '{lhs}' sum={actual} but declared={declared}",
                  file=sys.stderr)
        return 1
    print(f"[OK] no LOC summation violations across {len(args.paths)} file(s)"
          f"{' + stdin' if args.from_stdin else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
