"""check_sideproject_citation_count — 侧线项目长文引用条数硬闸 (轻量薄封装)。

背景 (计划 = SIDEPROJECT_LONGDESC_EXTENSION_EXECUTION_PLAN_2026-07-15.md §6 P3,
P0 决策定案第 5 条): 侧线项目 (company_listed_bank / company_tax_bank) 的
codebook 长文库要求"每篇引用 ≥3 条"为硬性验收标准。共享闸门
`check_longdesc_whitelist.py` 已覆盖白名单差集/新颖度/frontmatter 一致性等检查,
但逐篇 ≥3 条这条独立数量闸交由本脚本专管 —— **严禁改动共享脚本本体**
(改共享脚本会连带影响主项目 `config/codebook_longdesc/`, 违反变更最小化原则)。

复用 (import, 不重复造轮子): `pipeline.panel.codebook_longdesc.parse_family_md` 做单篇
frontmatter 解析 (与 `check_longdesc_whitelist.py::run_checks` 同款轻量遍历方式 —
按 `_index.json::families[*].file` 逐个 md 解析, **不**走
`codebook_longdesc.load_library` 的跨家族列名全局唯一性校验, 因为该校验面向单一
项目场景 `config/codebook_longdesc/`, 侧线宽表/长表并存的家族天然存在同名列如
`year` 跨家族复用, 会被那条校验误判为"§6 守恒快检 Σ 盲区"重复收录而 fail-loud;
`check_longdesc_whitelist.py` 本身也刻意不用 `load_library` 走这条路径, 本脚本与
其保持一致口径), 本脚本只在解析产物之上加一条"逐家族 citations 条数 >= 3"的独立
断言。

用法:
    python -m news_process.scripts.audit.check_sideproject_citation_count \
        --longdesc-dir <DIR> [--min-citations 3]

退出码: 全部家族 citations 条数 >= min-citations → 0; 任一家族 < 阈值 → 1
(打印是哪个家族/几条); 目录缺失或无法加载库 → 1 (fail-loud, 侧线项目场景下
"库不存在"本身就是错误, 与共享脚本"空库提示后 exit 0"的宽容语义不同 — 本脚本
只服务于已知应有长文库存在的侧线目录)。
"""
from __future__ import annotations

import argparse
import glob as _glob
import json
import os
import sys

try:
    from news_process.pipeline.panel import codebook_longdesc as cl
except ImportError:  # pragma: no cover - 脚本内直跑 fallback
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    try:
        from news_process.pipeline.panel import codebook_longdesc as cl
    except ImportError:
        from pipeline.panel import codebook_longdesc as cl  # type: ignore

DEFAULT_MIN_CITATIONS = 3


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--longdesc-dir", required=True, help="家族长文库目录 (含 _index.json)")
    p.add_argument(
        "--min-citations", type=int, default=DEFAULT_MIN_CITATIONS,
        help=f"逐篇最低引用条数下限 (默认 {DEFAULT_MIN_CITATIONS})",
    )
    return p.parse_args(argv)


def load_families(longdesc_dir: str):
    """轻量遍历 (镜像 `check_longdesc_whitelist.py::run_checks` 同款口径):
    按 `_index.json::families[*].file` 逐个 md 用 `cl.parse_family_md` 解析,
    不做跨家族列名全局唯一性校验 (侧线宽/长表并存, 同名列跨家族复用合法)。

    Returns: (families dict[fid -> FamilyDoc], note_or_None)
    """
    idx_path = os.path.join(longdesc_dir, "_index.json")
    md_files = sorted(
        p for p in _glob.glob(os.path.join(longdesc_dir, "*.md"))
        if not os.path.basename(p).startswith("_")
    )
    if not os.path.exists(idx_path):
        return {}, f"_index.json 缺失 ({longdesc_dir}); md 文件数={len(md_files)}"

    with open(idx_path, encoding="utf-8") as f:
        index = json.load(f)
    families_idx = index.get("families", {}) or {}
    file_by_fid = {str((m or {}).get("file", "")): fid for fid, m in families_idx.items()}

    families = {}
    for p in md_files:
        base = os.path.basename(p)
        idx_fid = file_by_fid.get(base, "")
        if not idx_fid:
            continue  # 未登记的杂散 md, 由共享闸门另管, 本脚本不重复报
        fam = cl.parse_family_md(p, family_id=idx_fid)
        fam.family_id = idx_fid
        fam.status = str((families_idx.get(idx_fid, {}) or {}).get("status", "draft"))
        families[idx_fid] = fam
    return families, None


def main(argv=None) -> int:
    args = parse_args(argv)
    longdesc_dir = args.longdesc_dir
    min_citations = args.min_citations

    if not os.path.isdir(longdesc_dir):
        print(f"[check_sideproject_citation_count] 目录不存在: {longdesc_dir}", file=sys.stderr)
        return 1

    families, note = load_families(longdesc_dir)
    if not families:
        print(
            f"[check_sideproject_citation_count] 库为空/加载失败: {note or longdesc_dir}",
            file=sys.stderr,
        )
        return 1

    violations = []
    summary = []
    for fid, fam in sorted(families.items()):
        citations = fam.frontmatter.get("citations", []) or []
        n = len(citations)
        summary.append((fid, n, fam.status))
        if n < min_citations:
            violations.append((fid, n))

    print(f"[check_sideproject_citation_count] {longdesc_dir}")
    print(f"  家族数: {len(summary)}  阈值: >= {min_citations} 条/篇")
    for fid, n, status in summary:
        flag = "OK" if n >= min_citations else "VIOLATION"
        print(f"    {fid}: {n} 条 (status={status}) [{flag}]")

    if violations:
        print(
            f"[check_sideproject_citation_count] FATAL: {len(violations)} 篇低于 "
            f"{min_citations} 条引用下限:",
            file=sys.stderr,
        )
        for fid, n in violations:
            print(f"  - {fid}: 仅 {n} 条", file=sys.stderr)
        return 1

    print(
        f"[check_sideproject_citation_count] PASS: 全部 {len(summary)} 篇均 >= "
        f"{min_citations} 条引用"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
