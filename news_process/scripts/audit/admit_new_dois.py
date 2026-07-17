"""admit_new_dois — 新 DOI 台账**唯一机器准入 CLI** (批收尾①, 计划 §2.4 / §6 v2.8)。

★ 2026-07-11 红队整改 (P1: 台账无机器准入路径): _new_dois_ledger.json 此前无任何
写入工具 — 谁写谁准入、被差集闸盲信, 计划 §2.4 声称防住的自我授权循环只是从
frontmatter 挪到了台账。本 CLI 是台账的唯一合法写入路径:

  逐 DOI 五步准入:
    1. 必须已在某家族 md 的 frontmatter citations 落地 (new_dois ⊆ citations 不变量;
       凭空 DOI 不准入);
    2. fetch_crossref (arXiv/DataCite DOI 走 fetch_datacite) 解析元数据;
    3. DOI→题名回比: Crossref 题名 vs 该引文条目 APA 渲染行 overlap ≥ --min-overlap
       (默认 0.6, 与 audit_dois 同阈) — 幻觉 DOI / 张冠李戴被拦;
    4. 撤稿筛查 (计划 §2.4 承诺, 此前零实现): Crossref update-to / updated-by /
       relation 撤稿类字段 + 题名 RETRACTED 前缀 — 命中即拒;
    5. 写台账条目 {doi, admitted_date, admitted_by='admit_new_dois.py', crossref_title
       回比记录, title_overlap, retraction_check='pass', verify_agent='pending',
       entry_sha 内容哈希} (原子写)。

  check_longdesc_whitelist.load_ledger_verified 只认含上述完整核验记录且 entry_sha
  复算相等的条目 — 手写直入台账的条目视为未准入。对抗五元组复核归编排会话的
  verify agent (翻 verify_agent: pending→done; 该键刻意不入 entry_sha 哈希域)。

  --register-ack: no_doi_ack 编号登记 (写台账 no_doi_acks 节) — 引用无 DOI 文献前
  须先登记 ack 编号, 否则 check_longdesc_whitelist 判 fatal。

用法:
    python -m news_process.scripts.audit.admit_new_dois 10.1234/abc [10.5678/def ...]
    python -m news_process.scripts.audit.admit_new_dois --scan-drafts   # 自动收集
        全库 draft 家族 new_dois 中尚未准入 (不在白名单 ∪ 已核验台账) 的 DOI
    python -m news_process.scripts.audit.admit_new_dois --register-ack ACK-001 \\
        --ack-note "Chesbrough 2003 开放式创新专著, worldcat 链接见引文条目"
    可选: [--longdesc-dir DIR] [--min-overlap 0.6] [--dry-run]
"""
from __future__ import annotations

import argparse
import datetime
import glob as _glob
import json
import os
import re
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

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

LEDGER_BASENAME = "_new_dois_ledger.json"

# 撤稿类关系词 (Crossref update-to/updated-by 的 type 值域: retraction / withdrawal /
# removal 等; expression of concern 从严同拒 — 准入是白名单扩容, 宁严勿宽)
_RETRACT_PAT = re.compile(r"retract|withdraw|removal|expression[-_ ]of[-_ ]concern", re.I)


# ============================================================================
# 元数据获取 + 撤稿筛查
# ============================================================================

def fetch_crossref_message(doi: str) -> Dict[str, Any]:
    """Crossref works 完整 message (audit_dois.fetch_crossref 只取 3 字段并丢弃
    update-to/updated-by — 撤稿筛查须读全量, 故此处独立取)。"""
    import urllib.parse
    url = ("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
           + "?mailto=" + audit_dois.MAILTO)
    return audit_dois.http_json(url)["message"]


def default_fetch_meta(doi: str) -> Dict[str, Any]:
    """解析单 DOI: {title, container, year, src, message}; 失败 raise。
    arXiv (10.48550) 走 DataCite (无 update 字段, message=None — 撤稿筛查退化为
    题名前缀检查, source 记录在案供 verify agent 补核)。"""
    if audit_dois.is_arxiv(doi):
        rec = audit_dois.fetch_datacite(doi)
        rec["message"] = None
        return rec
    msg = fetch_crossref_message(doi)
    title = (msg.get("title") or [""])
    title = title[0] if title else ""
    cont = (msg.get("container-title") or [])
    cont = cont[0] if cont else ""
    yr = None
    for k in ("published-print", "published", "issued", "published-online"):
        v = msg.get(k)
        if v and v.get("date-parts") and v["date-parts"][0]:
            yr = v["date-parts"][0][0]
            break
    return {"title": title, "container": cont, "year": yr, "src": "crossref",
            "message": msg}


def retraction_screen(message: Optional[Dict[str, Any]], title: str) -> List[str]:
    """撤稿筛查 (计划 §2.4; 红队 P2: 原零实现)。返回问题清单 (空=通过)。

    · update-to 非空 → 该 DOI 本身是更新通告类记录 (撤稿声明/更正声明), 不是可
      引用的一手文献 — 一律拒 (写手应引被更正后的原文 DOI);
    · updated-by / relation 含撤稿类关系 → 该文献已被撤稿/撤回 — 拒;
    · 题名以 RETRACTED/WITHDRAWN 前缀开头 (出版社通行做法) — 拒。
    """
    issues: List[str] = []
    if message:
        for u in (message.get("update-to") or []):
            label = str(u.get("type", "") or u.get("label", "") or "?")
            issues.append(
                f"该 DOI 本身是更新通告类记录 (update-to type={label}, "
                f"指向 {u.get('DOI', '?')}) — 应引原文而非通告"
            )
        for u in (message.get("updated-by") or []):
            label = str(u.get("type", "") or u.get("label", "") or "")
            if _RETRACT_PAT.search(label):
                issues.append(
                    f"该 DOI 已被撤稿/撤回 (updated-by type={label}, "
                    f"通告 DOI={u.get('DOI', '?')})"
                )
        for rk in (message.get("relation") or {}):
            if _RETRACT_PAT.search(str(rk)):
                issues.append(f"Crossref relation 含撤稿类关系键: {rk}")
        subtype = str(message.get("subtype", "") or "")
        if _RETRACT_PAT.search(subtype):
            issues.append(f"Crossref subtype 为撤稿类: {subtype}")
    if title and re.match(r"\s*(retracted|withdrawn)\b", title, re.I):
        issues.append(f"题名以撤稿前缀开头: {title[:80]!r}")
    return issues


# ============================================================================
# 家族库定位 (准入前提: DOI 已在某家族 citations 落地)
# ============================================================================

def collect_library_citations(longdesc_dir: str) -> Dict[str, Tuple[str, str]]:
    """全库 {归一 DOI: (family_id, APA 渲染行)} — 题名回比的 APA 侧来源。"""
    out: Dict[str, Tuple[str, str]] = {}
    idx_path = os.path.join(longdesc_dir, "_index.json")
    file_by_fid: Dict[str, str] = {}
    if os.path.exists(idx_path):
        with open(idx_path, encoding="utf-8") as f:
            idx = json.load(f)
        file_by_fid = {str((m or {}).get("file", "")): fid
                       for fid, m in (idx.get("families", {}) or {}).items()}
    for p in sorted(_glob.glob(os.path.join(longdesc_dir, "*.md"))):
        base = os.path.basename(p)
        if base.startswith("_"):
            continue
        fam = cl.parse_family_md(p, family_id=file_by_fid.get(base, ""))
        fid = file_by_fid.get(base, fam.family_id)
        for c in fam.frontmatter.get("citations", []) or []:
            if not isinstance(c, dict):
                continue
            d = str(c.get("doi", "") or "").strip()
            if d:
                out[cl.normalize_doi(d)] = (fid, cl.render_citation_apa(c))
    return out


def scan_draft_new_dois(longdesc_dir: str, allowed: Set[str]) -> List[str]:
    """全库家族 frontmatter new_dois 中尚未准入 (∉ allowed) 的归一 DOI 清单。"""
    pend: Set[str] = set()
    for p in sorted(_glob.glob(os.path.join(longdesc_dir, "*.md"))):
        if os.path.basename(p).startswith("_"):
            continue
        fam = cl.parse_family_md(p)
        for d in fam.frontmatter.get("new_dois", []) or []:
            nd = cl.normalize_doi(str(d))
            if nd and nd not in allowed:
                pend.add(nd)
    return sorted(pend)


# ============================================================================
# 台账读写 (原子)
# ============================================================================

def _ledger_path(longdesc_dir: str) -> str:
    return os.path.join(longdesc_dir, LEDGER_BASENAME)


def load_ledger_file(longdesc_dir: str) -> Dict[str, Any]:
    path = _ledger_path(longdesc_dir)
    if not os.path.exists(path):
        return {"entries": [], "no_doi_acks": []}
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):  # 兼容裸 list 旧形状 → 升格 (旧条目无核验记录, 保留供审计)
        data = {"entries": data, "no_doi_acks": []}
    data.setdefault("entries", [])
    data.setdefault("no_doi_acks", [])
    return data


def save_ledger_file(longdesc_dir: str, data: Dict[str, Any]) -> str:
    path = _ledger_path(longdesc_dir)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, path)
    return path


def build_ledger_entry(
    doi_norm: str,
    meta: Dict[str, Any],
    ov: float,
    fid: str,
    apa_line: str,
) -> Dict[str, Any]:
    entry = {
        "doi": doi_norm,
        "admitted_date": datetime.date.today().isoformat(),
        "admitted_by": chk.LEDGER_ADMITTED_BY,
        "family_id": fid,
        "apa_line": apa_line[:320],
        "crossref_title": str(meta.get("title", "") or "")[:320],
        "crossref_container": str(meta.get("container", "") or "")[:160],
        "crossref_year": meta.get("year"),
        "meta_source": meta.get("src", ""),
        "title_overlap": round(float(ov), 3),
        "retraction_check": "pass",
        "verify_agent": "pending",   # 对抗五元组复核接口 (编排会话 verify agent 翻 done)
    }
    entry["entry_sha"] = chk.ledger_entry_sha(entry)
    return entry


def register_ack(longdesc_dir: str, ack_id: str, note: str = "",
                 dry_run: bool = False) -> Dict[str, Any]:
    """no_doi_ack 编号登记 (台账 no_doi_acks 节; check 的 ack 闸消费)。"""
    ack_id = str(ack_id).strip()
    if not ack_id:
        raise SystemExit("[admit_new_dois] --register-ack 编号为空")
    data = load_ledger_file(longdesc_dir)
    existing = {str(e.get("ack_id") if isinstance(e, dict) else e).strip()
                for e in data["no_doi_acks"]}
    if ack_id in existing:
        return {"ack_id": ack_id, "status": "already-registered"}
    rec = {"ack_id": ack_id, "note": str(note or ""),
           "registered_date": datetime.date.today().isoformat(),
           "registered_by": chk.LEDGER_ADMITTED_BY}
    data["no_doi_acks"].append(rec)
    if not dry_run:
        save_ledger_file(longdesc_dir, data)
    return {"ack_id": ack_id, "status": "registered", "dry_run": dry_run}


# ============================================================================
# 准入主流程
# ============================================================================

def admit_dois(
    dois: List[str],
    longdesc_dir: str,
    min_overlap: float = 0.6,
    fetch=None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """逐 DOI 五步准入。返回 {admitted, skipped, failed} 报告 (failed 非空 → CLI exit 1)。

    fetch 参数注入 (默认 default_fetch_meta) — 测试 mock 网络。
    """
    fetch = fetch or default_fetch_meta
    whitelist = {cl.normalize_doi(d) for d in audit_dois.whitelist_dois()}
    already = chk.load_ledger_verified(longdesc_dir)
    lib_cites = collect_library_citations(longdesc_dir)

    report: Dict[str, Any] = {"admitted": [], "skipped": [], "failed": []}
    data = load_ledger_file(longdesc_dir)
    n_new = 0
    for raw in dois:
        doi = cl.normalize_doi(str(raw))
        if not re.match(r"^10\.\d{4,9}/", doi):
            report["failed"].append((doi, "非法 DOI 形状 (须 10.xxxx/...)"))
            continue
        if doi in whitelist:
            report["skipped"].append((doi, "已在主白名单 (FILES_WHITELIST_ANCHOR 动态派生; 无需台账准入)"))
            continue
        if doi in already:
            report["skipped"].append((doi, "台账已有完整核验条目"))
            continue
        hit = lib_cites.get(doi)
        if hit is None:
            report["failed"].append(
                (doi, "不在任何家族 citations 中 — 先在家族 md 落 citations 条目 "
                      "+ new_dois 声明, 再跑准入 (凭空 DOI 不准入)"))
            continue
        fid, apa_line = hit
        try:
            meta = fetch(doi)
        except Exception as e:  # noqa: BLE001
            report["failed"].append((doi, f"元数据解析失败: {type(e).__name__}: {str(e)[:80]}"))
            continue
        title = str((meta or {}).get("title", "") or "")
        if not title.strip():
            report["failed"].append((doi, "Crossref/DataCite 无题名 — 无法回比, 拒准入"))
            continue
        issues = retraction_screen((meta or {}).get("message"), title)
        if issues:
            report["failed"].append((doi, "撤稿筛查未过: " + "; ".join(issues)))
            continue
        ov = audit_dois.overlap(title, apa_line)
        if ov < min_overlap:
            report["failed"].append(
                (doi, f"题名回比 overlap={ov:.3f} < {min_overlap} "
                      f"(resolved={title[:80]!r} vs apa={apa_line[:80]!r})"))
            continue
        entry = build_ledger_entry(doi, meta, ov, fid, apa_line)
        data["entries"].append(entry)
        n_new += 1
        report["admitted"].append((doi, fid, round(ov, 3)))
        if fetch is default_fetch_meta:
            time.sleep(0.1)   # Crossref 礼貌节流
    if n_new and not dry_run:
        save_ledger_file(longdesc_dir, data)
    report["ledger_path"] = _ledger_path(longdesc_dir)
    report["dry_run"] = dry_run
    return report


def main(argv: Optional[List[str]] = None) -> int:
    try:  # Windows GBK 控制台防崩
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    ap = argparse.ArgumentParser(description="新 DOI 台账唯一机器准入 CLI (批收尾①, §2.4)")
    ap.add_argument("dois", nargs="*", help="待准入 DOI 清单")
    ap.add_argument("--scan-drafts", action="store_true",
                    help="自动收集全库家族 new_dois 未准入项")
    ap.add_argument("--longdesc-dir", default=cl.default_longdesc_dir())
    ap.add_argument("--min-overlap", type=float, default=0.6)
    ap.add_argument("--dry-run", action="store_true", help="只核验不写台账")
    ap.add_argument("--register-ack", default=None, metavar="ACK_ID",
                    help="登记 no_doi_ack 编号 (与 DOI 准入互斥使用)")
    ap.add_argument("--ack-note", default="", help="ack 登记备注 (文献与替代链接说明)")
    args = ap.parse_args(argv)

    if args.register_ack:
        res = register_ack(args.longdesc_dir, args.register_ack, args.ack_note,
                           dry_run=args.dry_run)
        print(f"[admit_new_dois] ack {res['ack_id']}: {res['status']}"
              + (" (dry-run, 未写盘)" if res.get("dry_run") else ""))
        return 0

    dois = list(args.dois)
    if args.scan_drafts:
        whitelist = {cl.normalize_doi(d) for d in audit_dois.whitelist_dois()}
        allowed = whitelist | chk.load_ledger_verified(args.longdesc_dir)
        dois += scan_draft_new_dois(args.longdesc_dir, allowed)
    dois = sorted(dict.fromkeys(cl.normalize_doi(str(d)) for d in dois))
    if not dois:
        print("[admit_new_dois] 无待准入 DOI (new_dois 全部已准入/白名单内)")
        return 0

    rep = admit_dois(dois, args.longdesc_dir, min_overlap=args.min_overlap,
                     dry_run=args.dry_run)
    print("===== admit_new_dois =====")
    for doi, fid, ov in rep["admitted"]:
        print(f"  ADMITTED {doi} (family={fid}, overlap={ov})")
    for doi, why in rep["skipped"]:
        print(f"  SKIP     {doi}: {why}")
    for doi, why in rep["failed"]:
        print(f"  FAIL     {doi}: {why}")
    print(f"  admitted={len(rep['admitted'])} skipped={len(rep['skipped'])} "
          f"failed={len(rep['failed'])} dry_run={rep['dry_run']}")
    print(f"  ledger -> {rep['ledger_path']}")
    return 1 if rep["failed"] else 0


if __name__ == "__main__":
    sys.exit(main())
