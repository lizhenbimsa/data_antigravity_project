"""remove_title_track.py — 取消"标题情感轨"的确定性机械变换 (Phase 1: structural).

只做**可逆、可断言、与代码语义解耦**的机械变换; 语义型改动 (content_full 注入、
tone_llms/tone_berts 标题块删除) 由后续手工 Edit 处理。

每个操作:
  - 前置断言 (找不到锚点 → 抛错, 不静默)
  - 幂等 (重复运行无副作用)
  - 打印 before/after 摘要

运行: python news_process/scripts/migrate/remove_title_track.py
"""
from __future__ import annotations

import pathlib
import re

NP = pathlib.Path(__file__).resolve().parents[2]  # news_process/  (scripts/migrate/<file> → parents[2])
report: list[str] = []


def _read(p: pathlib.Path) -> str:
    # newline="" → 保留原始 \r\n / \n 不做翻译 (避免 churn EOL); 需 Py3.13+
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def _write(p: pathlib.Path, s: str) -> None:
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def replace_once(relpath: str, old: str, new: str, *, required: bool = True,
                 count_expected: int | None = None) -> int:
    p = NP / relpath
    if not p.exists():
        if required:
            raise SystemExit(f"[FATAL] 文件不存在: {relpath}")
        report.append(f"  skip (missing): {relpath}")
        return 0
    s = _read(p)
    n = s.count(old)
    if n == 0:
        if required:
            raise SystemExit(f"[FATAL] 锚点未找到于 {relpath}:\n    {old!r}")
        report.append(f"  noop (anchor absent): {relpath} <- {old[:40]!r}")
        return 0
    if count_expected is not None and n != count_expected:
        raise SystemExit(
            f"[FATAL] {relpath} 锚点出现 {n} 次, 期望 {count_expected}: {old[:50]!r}")
    s = s.replace(old, new)
    _write(p, s)
    report.append(f"  edit x{n}: {relpath}  ({old[:34]!r} -> {new[:34]!r})")
    return n


def collapse_track_loops() -> None:
    """把 ['_full', '_ctx', '_title'] 收缩为 ['_full', '_ctx'] (全仓机械替换)。

    下游 _title 列消费者均有 `if col in df.columns` 守卫, 故生产端收缩后
    优雅退化为双轨 (见 encode.py tone_gap_title_full 等的存在性守卫)。
    """
    variants = [
        "['_full', '_ctx', '_title']",
        "['_full','_ctx','_title']",
        '["_full", "_ctx", "_title"]',
    ]
    new_variants = [
        "['_full', '_ctx']",
        "['_full','_ctx']",
        '["_full", "_ctx"]',
    ]
    total = 0
    for base in [NP / "pipeline", NP / "validation"]:
        for p in base.rglob("*.py"):
            s = _read(p)
            orig = s
            for old, new in zip(variants, new_variants):
                s = s.replace(old, new)
            if s != orig:
                _write(p, s)
                n = sum(orig.count(v) for v in variants)
                total += n
                report.append(f"  collapse x{n}: {p.relative_to(NP)}")
    report.append(f"  [track-loop collapse] 共 {total} 处")


def remove_stagespec_39g() -> None:
    """从 core/dag.py 删除 39g StageSpec 块 + 其谓词 + 上方注释。"""
    p = NP / "core" / "dag.py"
    lines = _read(p).splitlines(keepends=True)

    # 1) 谓词行 (152 区域)
    pred_idx = [i for i, ln in enumerate(lines)
                if "'track_discriminant_validity': _validation_flag(" in ln]
    if len(pred_idx) != 1:
        raise SystemExit(f"[FATAL] dag.py 谓词行命中 {len(pred_idx)} 次 (期望1)")

    # 2) StageSpec 块: 定位 script="39g..." 行, 向上找 StageSpec(, 向下配平括号
    spec_line = [i for i, ln in enumerate(lines)
                 if 'script="39g_track_discriminant_validity.py"' in ln]
    if len(spec_line) != 1:
        raise SystemExit(f"[FATAL] dag.py 39g script 行命中 {len(spec_line)} 次")
    si = spec_line[0]
    # 向上找 StageSpec(
    start = si
    while start >= 0 and "StageSpec(" not in lines[start]:
        start -= 1
    if start < 0:
        raise SystemExit("[FATAL] 未找到 39g 的 StageSpec( 开头")
    # 吸收紧邻上方的注释行 (以 # 开头, 属于该 spec)
    while start - 1 >= 0 and lines[start - 1].lstrip().startswith("#"):
        start -= 1
    # 向下配平括号
    depth = 0
    end = si
    for j in range(start, len(lines)):
        depth += lines[j].count("(") - lines[j].count(")")
        if j >= si and depth <= 0 and "StageSpec(" in "".join(lines[start:j + 1]):
            end = j
            break
    # 去掉块后若有尾随逗号行也一并 (StageSpec(...) , )
    block = lines[start:end + 1]
    if "39g_track_discriminant_validity.py" not in "".join(block):
        raise SystemExit("[FATAL] 39g StageSpec 块定位错误 (块内无 39g)")
    if "StageSpec" not in "".join(block) or "阶段39g" not in "".join(block):
        raise SystemExit("[FATAL] 39g StageSpec 块校验失败 (缺 StageSpec/阶段39g)")

    new_lines = [ln for k, ln in enumerate(lines)
                 if k not in set(range(start, end + 1)) and k != pred_idx[0]]
    _write(p, "".join(new_lines))
    report.append(f"  dag.py: 删谓词 1 行 + StageSpec 块 行 {start+1}-{end+1} "
                  f"({end-start+1} 行)")


def remove_schemas_39g() -> None:
    p = NP / "core" / "schemas.py"
    lines = _read(p).splitlines(keepends=True)
    idx = [i for i, ln in enumerate(lines)
           if '"39g_track_discriminant_validity.py"' in ln]
    if len(idx) != 1:
        raise SystemExit(f"[FATAL] schemas.py 39g 行命中 {len(idx)} 次")
    new = [ln for k, ln in enumerate(lines) if k != idx[0]]
    _write(p, "".join(new))
    report.append(f"  schemas.py: 删 EXPECTED_NO_OUTPUT 39g 行 (行 {idx[0]+1})")


def remove_master_do_calls() -> None:
    """删除 10 个 00_master.do.tmpl 中调用标题模板的 `do` 行。"""
    tdir = NP / "papers" / "_common" / "stata_templates"
    pat = re.compile(r".*(25_tableA8_title_robustness|26_bs_title_robustness)\.do.*")
    n_files = 0
    for p in tdir.rglob("00_master.do.tmpl"):
        lines = _read(p).splitlines(keepends=True)
        kept = [ln for ln in lines
                if not (pat.match(ln) and ("do " in ln or "do\t" in ln))]
        if len(kept) != len(lines):
            _write(p, "".join(kept))
            n_files += 1
            report.append(f"  master do-call 删 {len(lines)-len(kept)} 行: "
                          f"{p.relative_to(NP)}")
    report.append(f"  [master do-calls] {n_files} 个 master 文件已清理")


def fix_count_assertions() -> None:
    # test_dag_consistency: STAGES_VALIDATION 18 -> 17
    replace_once(
        "tests/integration/test_dag_consistency.py",
        "assert len(core_dag.STAGES_VALIDATION) == 18",
        "assert len(core_dag.STAGES_VALIDATION) == 17",
        count_expected=1,
    )
    replace_once(
        "tests/integration/test_dag_consistency.py",
        "expected 18 (v3.7.3 +39g), got",
        "expected 17 (39g track-discriminant removed), got",
        required=False,
    )
    # test_stata_replication_matrix: do_files 15 -> 14
    replace_once(
        "tests/integration/test_stata_replication_matrix.py",
        "assert len(do_files) == 15",
        "assert len(do_files) == 14",
        required=False, count_expected=None,
    )
    # test_stata_templates: '15/15 完整' / '14/14 子 .do'
    replace_once("tests/test_stata_templates.py", "15/15 完整", "14/14 完整",
                 required=False)
    replace_once("tests/test_stata_templates.py", "14/14 子 .do", "13/13 子 .do",
                 required=False)


def main() -> None:
    print("=== remove_title_track.py (Phase 1 structural) ===")
    collapse_track_loops()
    remove_stagespec_39g()
    remove_schemas_39g()
    remove_master_do_calls()
    fix_count_assertions()
    print("\n".join(report))
    print("=== Phase 1 done ===")


if __name__ == "__main__":
    main()
