"""batch_longdesc_gate — WP4 每批收尾机械闸五件套一键运行器 (计划 §6)。

权威口径 = scripts/audit/STATA_VARATTR_AND_CODEBOOK_LONGDESC_EXECUTION_PLAN_2026-07-10.md
(v2.9)。§6 v2.8 顺序: 新 DOI 增量核验准入 (fetch_crossref 回比 + 对抗 verify → 台账)
在本脚本**之外先行** (由编排会话跑); 本脚本 = 之后的机械闸五件套 + (可选) draft→final 迁移。

机械闸五件套 (§6, 对 --families 指定家族**一律按 final 级硬闸判** — draft 状态不豁免):
  1. 守恒快检 (全局): set(_index 非 pending 列) == set(51 panel.columns)
     且 Σ|各家族列清单| == |并集| (封死同列被两家族重复收录的 set 盲区)。
     51 面板缺失 = 拒跑 (§0 铁律, 禁回退 40 宇宙)。守恒破坏 = 拒跑 (不再跑逐家族闸)。
  2. 字数双闸: 逐列经引擎五段组装 (真实 panel 注入动态统计段) 后
     standard >=1000 / core >=5000 CJK 汉字总量闸 + 段落闸 (CORE 700/4200,
     VAR 350/900, core 传染 = core 家族全列享 4200 深核心) + 结构列白名单豁免。
  3. DOI 白名单差集闸 (final 级): citations[].doi 全体 ⊆ (主白名单 [FILES_WHITELIST_ANCHOR 动态派生] ∪ 已准入台账),
     越权即 FAIL **不走 v2.9 draft 出口** (draft 出口只属组装期 check_longdesc_whitelist;
     批收尾时 DOI 准入已先行, 残余越权 = 未过准入的引文, 一律打回) +
     no_doi_ack 闸 + new_dois ⊆ citations 一致性 + frontmatter 解析对账 (全局)。
  4. 引文渲染闸: 先 materialize (幂等物化回写指定家族尾节, §2.1), 再断言
     逐家族渲染段 DOI 集 == citations 集 + 尾节外 doi.org 零命中 +
     standard >=3 条 / core 家族 >=10 条引文下限 (含渲染字符下限, CITATION_MIN)。
  5. 占位符残留闸: 组装产物宽 regex \\{[A-Za-z_]+:[^}]*\\} 零命中。

--promote-final: 仅当指定家族**全部** PASS 时把它们在 _index.json 的 status
draft→final (增量局部更新, 只改指定家族的 status 键, 绝不触碰其他键/家族/签核块);
任一 FAIL / 拒跑 → 不迁移任何家族并 exit 1。

--report: 机器可读 JSON 报告 (逐家族逐闸 pass/fail + 数字), 默认落
build/codebook_inputs/batch_gate_reports/<批名或时间戳>.json。

用法:
    python -m news_process.scripts.audit.batch_longdesc_gate \
        --families F001,F007 [--promote-final] [--report PATH] \
        [--longdesc-dir DIR] [--panel PARQUET] [--batch-name NAME]

终端输出 ASCII-safe 概要 (中文详情全部承载于 JSON 报告 — Windows GBK 控制台防崩)。
"""
from __future__ import annotations

import argparse
import datetime
import glob as _glob
import json
import os
import sys
from typing import Any, Dict, List, Optional, Set

_HERE = os.path.dirname(os.path.abspath(__file__))
_NEWS_PROCESS_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
_REPO_ROOT = os.path.dirname(_NEWS_PROCESS_ROOT)
for _p in (_REPO_ROOT, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

try:
    from news_process.pipeline.panel import codebook_longdesc as cl
    from news_process.scripts.audit import audit_dois
    from news_process.scripts.audit import check_longdesc_whitelist as chk
except ImportError:  # standalone 直跑回退 (scripts/audit 内相对导入)
    import audit_dois  # type: ignore
    import check_longdesc_whitelist as chk  # type: ignore
    sys.path.insert(0, _NEWS_PROCESS_ROOT)
    from pipeline.panel import codebook_longdesc as cl  # type: ignore

DEFAULT_PANEL_PATH = os.path.join(
    _NEWS_PROCESS_ROOT, "data", "processed", "51_panel_with_controls.parquet")
DEFAULT_REPORT_DIR = os.path.join(
    _NEWS_PROCESS_ROOT, "build", "codebook_inputs", "batch_gate_reports")

GATE_KEYS = ("g2_wordcount", "g3_whitelist", "g4_render", "g5_placeholder")


def _load_whitelist() -> Set[str]:
    """主 DOI 白名单 (唯一派生源 = audit_dois.FILES_WHITELIST_ANCHOR 动态派生, 勿嵌计数字面), 归一口径与
    引擎 normalize_doi 一致。测试可 monkeypatch 本函数注入 fixture 白名单。"""
    return {cl.normalize_doi(d) for d in audit_dois.whitelist_dois()}


# ============================================================================
# 闸 1: 守恒快检 (全局, 秒级)
# ============================================================================

def gate1_conservation(index: Dict[str, Any], panel_columns) -> Dict[str, Any]:
    """§6 ①: set(_index 非 pending 列) == set(panel.columns) 且 Σ|家族列清单| == |并集|。"""
    families = index.get("families", {}) or {}
    all_cols: List[str] = []
    pending: Set[str] = set()
    for _fid, meta in families.items():
        cols = list((meta or {}).get("columns", []) or [])
        all_cols.extend(cols)
        tiers = (meta or {}).get("tier_by_col", {}) or {}
        pending |= {c for c in cols if tiers.get(c) == "pending"}
    union = set(all_cols)
    non_pending = union - pending
    pset = set(panel_columns)
    index_only = sorted(non_pending - pset)
    panel_only = sorted(pset - non_pending)
    # Σ 快检: 重复收录列点名 (load_library 也会崩, 但本闸先行给出可读报告)
    from collections import Counter
    dup_cols = sorted(c for c, n in Counter(all_cols).items() if n > 1)
    ok = (not index_only) and (not panel_only) and (len(all_cols) == len(union))
    return {
        "pass": ok,
        "n_index_non_pending": len(non_pending),
        "n_panel_cols": len(pset),
        "n_pending": len(pending),
        "sum_family_cols": len(all_cols),
        "n_union_cols": len(union),
        "index_only": index_only[:20],
        "panel_only": panel_only[:20],
        "duplicated_cols": dup_cols[:20],
    }


# ============================================================================
# 逐家族: 闸 2/3/4/5 (指定家族, 一律 final 级判定)
# ============================================================================

def _classify_compose_violation(msg: str, g2: List[str], g3: List[str], g5: List[str]) -> None:
    """compose 违规/SystemExit 消息按闸归桶: 占位符→g5, citation 结构→g3, 其余→g2。"""
    if "占位符" in msg:  # 占位符
        g5.append(msg)
    elif "citation" in msg:
        g3.append(msg)
    else:
        g2.append(msg)


def evaluate_family(
    fid: str,
    lib: cl.LongdescLibrary,
    index: Dict[str, Any],
    panel,
    allowed_dois: Set[str],
) -> Dict[str, Any]:
    """对单个家族跑闸 2–5 (final 级硬闸判, 无论 _index status)。返回逐闸报告 dict。"""
    meta = (index.get("families", {}) or {}).get(fid, {}) or {}
    cols = list(meta.get("columns", []) or [])
    tiers = meta.get("tier_by_col", {}) or {}
    entry: Dict[str, Any] = {
        "status": str(meta.get("status", "draft")),
        "n_columns": len(cols),
        "gates": {},
        "pass": False,
    }
    fam = lib.families.get(fid)
    if fam is None:
        msg = f"{fid}: family md missing (cannot compose)"
        entry["gates"] = {k: {"pass": False, "violations": [msg]} for k in GATE_KEYS}
        return entry

    # ---- 闸 2 (字数双闸) + 闸 5 (占位符残留), 逐列经引擎真实组装 ----
    g2_viol: List[str] = []
    g3_struct: List[str] = []
    g5_viol: List[str] = []
    per_col_cjk: Dict[str, int] = {}
    counters: Dict[str, Any] = {}
    for col in cols:
        try:
            res = cl.compose_long_description(col, panel, lib, counters=counters)
        except SystemExit as e:
            _classify_compose_violation(str(e), g2_viol, g3_struct, g5_viol)
            continue
        if res is None:
            g2_viol.append(f"{fid}/{col}: compose returned None (family text unavailable)")
            continue
        per_col_cjk[col] = int(res["cjk_total"])
        for v in res["gate_violations"]:
            # 引文段质量违规归闸 4 家族级检查, 此处剔除防双计
            if "引文段" in v:  # 引文段
                continue
            _classify_compose_violation(v, g2_viol, g3_struct, g5_viol)
        residues = cl.find_placeholder_residue(res["description"])
        if residues:
            g5_viol.append(f"{fid}/{col}: placeholder residue {residues[:5]}")
    entry["gates"]["g2_wordcount"] = {
        "pass": not g2_viol,
        "violations": g2_viol,
        "per_col_cjk": per_col_cjk,
        "floors": {"total": dict(cl.TOTAL_CJK_FLOOR),
                   "core_seg": dict(cl.CORE_SEG_CJK_FLOOR),
                   "var_seg": dict(cl.VAR_SEG_CJK_FLOOR)},
    }

    # ---- 闸 3 (DOI 白名单差集, final 级 — 不走 draft 出口) ----
    citations = fam.frontmatter.get("citations", []) or []
    g3_struct.extend(e for c in citations for e in cl.validate_citation(c, fid))
    cited = cl.rendered_dois(citations)
    new_dois = {cl.normalize_doi(str(d)) for d in fam.frontmatter.get("new_dois", []) or []}
    not_landed = sorted(new_dois - cited)
    over = sorted(cited - allowed_dois)
    entry["gates"]["g3_whitelist"] = {
        "pass": not (g3_struct or over or not_landed),
        "n_citations": len(citations),
        "n_cited_dois": len(cited),
        "over_dois": over,
        "new_dois_not_in_citations": not_landed,
        "citation_struct_errors": g3_struct,
        "note": "final-level: draft exit (v2.9) deliberately disabled at batch closeout",
    }

    # ---- 闸 4 (引文渲染闸: 先 materialize 再断言) ----
    g4_viol: List[str] = []
    materialized = cl.materialize_rendered_citations(fam)
    rendered = {
        audit_dois.clean_doi(m.group(1)).lower()
        for m in audit_dois.DOIORG_RE.finditer(fam.rendered_block or "")
    }
    if rendered != cited:
        g4_viol.append(
            f"{fid}: rendered DOI set != citations DOI set "
            f"(rendered-only={sorted(rendered - cited)[:5]}, cite-only={sorted(cited - rendered)[:5]})"
        )
    g4_viol.extend(cl.lint_doiorg_outside_tail(fam))
    depth = "core" if any(tiers.get(c) == "core" for c in cols) else "standard"
    n_min, ch_min = cl.CITATION_MIN[depth]
    block = cl.render_citations_block(citations)
    if len(citations) < n_min or len(block) < ch_min:
        g4_viol.append(
            f"{fid}: citations {len(citations)} items / {len(block)} rendered chars "
            f"< floor {n_min} items / {ch_min} chars ({depth} family)"
        )
    entry["gates"]["g4_render"] = {
        "pass": not g4_viol,
        "violations": g4_viol,
        "materialized_this_run": bool(materialized),
        "family_depth": depth,
        "n_rendered_dois": len(rendered),
        "rendered_chars": len(block),
        "floor": {"items": n_min, "chars": ch_min},
    }

    # ---- 闸 5 (占位符残留; 组装期收集 + md 人工区兜底扫) ----
    residues_md = cl.find_placeholder_residue(fam.human_zone or "")
    # frontmatter formula 骨架占位 "(WP0 初判占位 — ...)" 非 {word:...} 语法, 不触本闸
    if residues_md:
        g5_viol.append(f"{fid}: md human zone placeholder residue {residues_md[:5]}")
    entry["gates"]["g5_placeholder"] = {"pass": not g5_viol, "violations": g5_viol}

    entry["pass"] = all(entry["gates"][k]["pass"] for k in GATE_KEYS)
    return entry


# ============================================================================
# promote / report
# ============================================================================

def promote_final(longdesc_dir: str, family_ids: List[str]) -> None:
    """增量局部更新: 只把指定家族的 status 置 'final', 其余键/家族/签核块原样保留。
    原子写 (tmp + os.replace), 与真实库现行格式一致 (ensure_ascii=False, indent=2)。"""
    idx_path = os.path.join(longdesc_dir, "_index.json")
    with open(idx_path, encoding="utf-8") as f:
        index = json.load(f)
    fams = index.get("families", {}) or {}
    for fid in family_ids:
        if fid not in fams:
            raise SystemExit(f"[batch_longdesc_gate] promote: family {fid} not in _index.json")
        fams[fid]["status"] = "final"
    tmp = idx_path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, idx_path)


def _write_report(report: Dict[str, Any], path: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return path


# ============================================================================
# 编排
# ============================================================================

def run_batch_gate(
    longdesc_dir: str,
    family_ids: List[str],
    panel,
    whitelist: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """五件套编排 (纯函数化, panel/whitelist 参数注入供测试)。返回 report dict
    (report['all_pass'] 为总判; 'refused' 非空 = 前置拒跑, 逐家族闸未跑)。"""
    report: Dict[str, Any] = {
        "tool": "batch_longdesc_gate",
        "plan": "STATA_VARATTR_AND_CODEBOOK_LONGDESC_EXECUTION_PLAN_2026-07-10 §6",
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "longdesc_dir": longdesc_dir,
        "families_requested": list(family_ids),
        "global": {},
        "families": {},
        "all_pass": False,
        "refused": None,
        "promoted": [],
    }

    idx_path = os.path.join(longdesc_dir, "_index.json")
    if not os.path.exists(idx_path):
        report["refused"] = f"_index.json missing: {idx_path}"
        return report
    with open(idx_path, encoding="utf-8") as f:
        index = json.load(f)
    families_idx = index.get("families", {}) or {}

    unknown = sorted(set(family_ids) - set(families_idx))
    if unknown:
        report["refused"] = f"unknown family ids (not in _index.json): {unknown}"
        return report

    # ---- 闸 1: 守恒快检 (全局); 破坏 = 拒跑 ----
    g1 = gate1_conservation(index, list(panel.columns))
    report["global"]["gate1_conservation"] = g1
    report["global"]["n_panel_cols"] = len(list(panel.columns))
    if not g1["pass"]:
        report["refused"] = "gate1 conservation broken (see global.gate1_conservation)"
        return report

    # ---- 全局 frontmatter 解析对账 (闸 3 附属, §2.3): md 文件数 == index 家族数 ----
    md_files = sorted(
        p for p in _glob.glob(os.path.join(longdesc_dir, "*.md"))
        if not os.path.basename(p).startswith("_")
    )
    recon = {"pass": len(md_files) == len(families_idx),
             "n_md_files": len(md_files), "n_index_families": len(families_idx)}
    report["global"]["gate3_frontmatter_recon"] = recon

    # ---- 库加载 (frontmatter 解析失败 / 列集不一致 → 引擎 fail-loud, 转拒跑) ----
    try:
        lib = cl.load_library(longdesc_dir)
    except SystemExit as e:
        report["refused"] = f"load_library fail-loud: {e}"
        return report
    if lib is None:
        report["refused"] = f"load_library returned None (empty library): {longdesc_dir}"
        return report

    allowed = set(whitelist if whitelist is not None else _load_whitelist())
    allowed |= chk.load_ledger_verified(longdesc_dir)  # 严格视图: 只认含完整核验记录+entry_sha 的准入条目 (2026-07-11 收编整改 B 建议)
    report["global"]["n_allowed_dois"] = len(allowed)

    # ---- 逐家族: 闸 2/3/4/5 ----
    for fid in family_ids:
        report["families"][fid] = evaluate_family(fid, lib, index, panel, allowed)

    report["all_pass"] = bool(
        recon["pass"] and report["families"]
        and all(v["pass"] for v in report["families"].values())
    )
    if not recon["pass"]:
        # 对账失败属全局闸 3 违规 (非拒跑): 全批打回
        report["global"]["gate3_frontmatter_recon"]["note"] = (
            "md file count != _index families count — global gate3 FAIL, batch rejected")
    return report


def _print_summary(report: Dict[str, Any]) -> None:
    """ASCII-safe 概要 (中文详情只进 JSON 报告)。"""
    print("===== batch_longdesc_gate (plan section 6, five mechanical gates) =====")
    if report.get("refused"):
        print("  REFUSED:", str(report["refused"]).encode("ascii", "replace").decode("ascii"))
        g1 = (report.get("global", {}) or {}).get("gate1_conservation")
        if g1:
            print(f"  gate1 conservation: pass={g1['pass']} "
                  f"index_non_pending={g1['n_index_non_pending']} panel={g1['n_panel_cols']} "
                  f"sum={g1['sum_family_cols']} union={g1['n_union_cols']} "
                  f"index_only={len(g1['index_only'])} panel_only={len(g1['panel_only'])} "
                  f"dups={len(g1['duplicated_cols'])}")
        return
    g1 = report["global"]["gate1_conservation"]
    recon = report["global"]["gate3_frontmatter_recon"]
    print(f"  gate1 conservation: PASS (non-pending={g1['n_index_non_pending']} "
          f"== panel={g1['n_panel_cols']}; sum={g1['sum_family_cols']} == union={g1['n_union_cols']})")
    print(f"  gate3 frontmatter recon: {'PASS' if recon['pass'] else 'FAIL'} "
          f"(md={recon['n_md_files']} vs index={recon['n_index_families']})")
    for fid, fe in report["families"].items():
        flags = " ".join(
            f"{k.split('_')[0]}={'PASS' if fe['gates'][k]['pass'] else 'FAIL'}"
            for k in GATE_KEYS
        )
        nv = sum(len(fe["gates"][k].get("violations", [])) for k in GATE_KEYS)
        print(f"  {fid} [{fe['status']}]: {flags} n_violations={nv} "
              f"=> {'PASS' if fe['pass'] else 'FAIL'}")
    print(f"  ALL_PASS = {report['all_pass']}; promoted = {report['promoted']}")


def main(argv: Optional[List[str]] = None) -> int:
    try:  # Windows GBK 控制台防崩 (计划 v2.7 实测踩坑)
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    ap = argparse.ArgumentParser(description="WP4 批收尾机械闸五件套一键运行器 (计划 §6)")
    ap.add_argument("--families", required=True,
                    help="逗号分隔家族 id 清单, 如 F001,F007")
    ap.add_argument("--promote-final", action="store_true",
                    help="全部 PASS 时把指定家族 _index.json status draft->final (任一 FAIL 零迁移)")
    ap.add_argument("--report", default=None,
                    help=f"JSON 报告落点 (默认 {DEFAULT_REPORT_DIR}/<批名或时间戳>.json)")
    ap.add_argument("--batch-name", default=None, help="批名 (仅用于默认报告文件名)")
    ap.add_argument("--longdesc-dir", default=cl.default_longdesc_dir())
    ap.add_argument("--panel", default=DEFAULT_PANEL_PATH,
                    help="51 面板 parquet 路径 (缺失 = 拒跑, 禁回退 40 宇宙)")
    args = ap.parse_args(argv)

    family_ids = [x.strip() for x in args.families.split(",") if x.strip()]
    if not family_ids:
        print("  REFUSED: --families empty")
        return 1

    report_path = args.report or os.path.join(
        DEFAULT_REPORT_DIR,
        f"{args.batch_name or datetime.datetime.now().strftime('%Y%m%dT%H%M%S')}.json",
    )

    # 51 面板缺失 = 拒跑 (§0 铁律)
    if not os.path.exists(args.panel):
        report = {
            "tool": "batch_longdesc_gate",
            "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
            "longdesc_dir": args.longdesc_dir,
            "families_requested": family_ids,
            "global": {}, "families": {}, "all_pass": False, "promoted": [],
            "refused": f"51 panel parquet missing: {args.panel} "
                       "(section 0 iron rule: refuse, never fall back to 40 universe)",
        }
        _write_report(report, report_path)
        _print_summary(report)
        print(f"  report -> {report_path}")
        return 1

    import pandas as pd
    panel = pd.read_parquet(args.panel)
    report = run_batch_gate(args.longdesc_dir, family_ids, panel)
    report["panel_path"] = args.panel

    if report["all_pass"] and not report.get("refused") and args.promote_final:
        promote_final(args.longdesc_dir, family_ids)
        report["promoted"] = list(family_ids)

    _write_report(report, report_path)
    _print_summary(report)
    print(f"  report -> {report_path}")
    return 0 if (report["all_pass"] and not report.get("refused")) else 1


if __name__ == "__main__":
    sys.exit(main())
