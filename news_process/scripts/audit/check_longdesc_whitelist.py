"""check_longdesc_whitelist — 家族长文库引文白名单差集闸 (WP1, 计划 §2.3/§2.5/§2.7)。

组装期 + 每批收尾即时跑 (不等收口): audit_dois 只做 DOI→标题回比, 抓得住幻觉文献但
抓不住"真实存在却白名单外"的记忆引文 — **集合差断言是唯一防线**。

检查项 (计划 §2 引文铁律; ★ = 2026-07-11 红队整改新增/加固):
  1. 白名单差集闸: 逐家族 citations[].doi ⊆ (白名单 [FILES_WHITELIST_ANCHOR 派生]
     ∪ _new_dois_ledger.json 已准入); 差集非空 → SystemExit(1) 打印越权 DOI。
     **draft 出口 (v2.9)**: status==draft 且越权 DOI ⊆ 该家族自身 new_dois: 声明 →
     降级告警计数 (批收尾①准入后归零; final 态一律崩)。
     ★ 台账只认 admit_new_dois.py 写出的完整核验条目 (admitted_by + crossref_title
     回比记录 + retraction_check=pass + entry_sha 内容哈希复算相等); 缺任一 = 视为
     未准入 + WARN 点名 (旁路: 写手 agent 直写台账即自我扩容白名单)。
  2. frontmatter 解析失败 = SystemExit(1) (fail-open 同构静默漏检);
     ★ 对账 = 双向集合相等 (frontmatter 家族键集 == _index 家族键集, 非仅计数 —
     等长换键欺骗被封); ★ family_id / status 的 SSOT 只认 _index.json:
     frontmatter family_id != _index 中该文件对应键 = fatal, frontmatter 声明
     status 键 = fatal (旁路: final 家族 frontmatter 自贬 draft 使差集闸降级告警)。
  3. no_doi_ack 闸: 无 doi 条目须带 no_doi_ack 台账编号 + alt_link 替代可访问链接;
     ★ ack 编号须对应台账登记 (_no_doi_ack_ledger.json 或 _new_dois_ledger.json
     的 no_doi_acks 节, admit_new_dois.py --register-ack 写入), 未登记 = fatal。
  4. 渲染物化一致性双断言 (§2.1 v2.3 P0):
     ① longdesc 域 extract_refs 提取 DOI 数 ≥ 全库 frontmatter citations 去重后唯一
       DOI 总数 (两侧同用 clean_doi().lower() 归一; 防"0 红旗"恒真空转);
     ② 逐家族 渲染段 DOI 集 == citations DOI 集 (防 frontmatter 改后忘重渲染)。
  5. 尾节外 doi.org 零命中 lint (§2.6) + new_dois ⊆ citations[].doi 一致性断言;
     ★ lint 扫描域扩到 frontmatter 全部标量值 (递归; citations[].doi / new_dois[]
     结构化字段之外任何 doi.org = fatal — 旁路: formula/unit 等标量藏链接逃逸
     lint 与差集闸并流入组装产物); ★ 大小写变体 (DOI.ORG/ 等) 同 fatal
     (audit_dois.DOIORG_RE 已 re.IGNORECASE 化, extract_refs 同步多捕)。
  6. 顶刊结构闸 (§2.7, SSOT=config/top_journal_list.yaml; v2.11 双层, 2026-07-11
     C1 实证校准): ① 家族级硬闸 = 每 final 家族 citations 中 top 分类 ≥1 条
     (零 top 锚 = FATAL, draft 仅 WARN); ② (top+field 内) 非 top 占比 >30% 降级
     为 WARN (记录占比数字, 供对抗审核与 WP5 终局报告); wp/preprint 不计入分母;
     全卷级 final 家族 top/field/unlisted 三分类构成进 report (不设新硬闸);
     ★ type 自报 ∈ {wp,arxiv,book} 但 venue 在 top/field 清单 → 交叉校验 WARN
     (type 误标/恶标可无限稀释分母)。
  7. 弱断言 (§2.6): 正文 "作者 (年份)" 型引注 ⊆ citations 渲染集, 未命中仅 WARN。
  8. ★ 重复 DOI 闸 (计划 §2.10): 同家族 citations 内重复 DOI = fatal (重复条目
     可灌水凑 CITATION_MIN 条数闸, 渲染/差集两侧 set 化察觉不到)。
  9. ★ 新颖度闸 (计划 §2.8): 2023+ 年份引文占比 ≥50% — 全卷级 (全家族 final 或
     novelty_hard=True) 硬闸 fatal, 批级别 (尚有 draft) 仅进 report 不硬崩 (批内
     家族天然偏科); 构念定义型家族在 frontmatter 声明 novelty_exempt_rationale
     即整族豁免出统计池 (豁免清单进 report 供人工复核)。

用法:
    python -m news_process.scripts.audit.check_longdesc_whitelist [--longdesc-dir DIR]
        [--materialize]   # 检查前先做引文渲染物化回写 (幂等)
        [--novelty-hard | --no-novelty-hard]   # 新颖度闸强制硬/软 (默认 auto: 全 final 才硬)
库为空 (目录缺失 / 无 _index.json 且无家族 md) → 提示后 exit 0 (WP0 未跑属预期)。
"""
from __future__ import annotations

import argparse
import glob as _glob
import json
import os
import re
import sys
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
except ImportError:  # standalone 直跑回退 (scripts/audit 内相对导入)
    import audit_dois  # type: ignore
    sys.path.insert(0, _NEWS_PROCESS_ROOT)
    from pipeline.panel import codebook_longdesc as cl  # type: ignore

DEFAULT_TOP_JOURNAL_YAML = os.path.join(_NEWS_PROCESS_ROOT, "config", "top_journal_list.yaml")


# ============================================================================
# 台账 / 顶刊清单加载
# ============================================================================

LEDGER_ADMITTED_BY = "admit_new_dois.py"
# entry_sha 哈希域排除键: entry_sha 自身 + verify_agent (对抗五元组复核归编排会话
# 的 verify agent, 其 pending→done 翻转不应使内容哈希失配)
_LEDGER_SHA_EXCLUDE = ("entry_sha", "verify_agent")
_LEDGER_SHA_SALT = "news-process-new-dois-ledger-v1:"


def ledger_entry_sha(entry: Dict[str, Any]) -> str:
    """台账条目内容哈希 (admit_new_dois.py 写入 / 本闸复算比对; SSOT 在此防两头漂移)。"""
    import hashlib
    payload = {k: v for k, v in (entry or {}).items() if k not in _LEDGER_SHA_EXCLUDE}
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256((_LEDGER_SHA_SALT + blob).encode("utf-8")).hexdigest()


def _ledger_entry_verified(e: Any) -> Optional[str]:
    """单条台账条目完整核验记录校验; 合格 → None, 否则返回拒绝理由。

    ★ 2026-07-11 红队整改 (P1 台账无机器准入路径): 谁写谁准入被封 — 只认
    admit_new_dois.py 写出的条目 {doi, admitted_by, crossref_title (Crossref
    题名回比记录), retraction_check == 'pass', entry_sha 内容哈希复算相等}。
    """
    if not isinstance(e, dict):
        return f"条目非 dict (裸字符串直写无核验记录): {e!r}"
    doi = str(e.get("doi", "") or "").strip()
    if not doi:
        return f"条目缺 doi: {e!r}"
    if e.get("admitted_by") != LEDGER_ADMITTED_BY:
        return f"{doi}: 缺 admitted_by={LEDGER_ADMITTED_BY!r} 机器准入标记 (手写直入台账?)"
    if not str(e.get("crossref_title", "") or "").strip():
        return f"{doi}: 缺 crossref_title 回比记录 (未过 fetch_crossref DOI→题名回比)"
    if e.get("retraction_check") != "pass":
        return f"{doi}: retraction_check != 'pass' (撤稿筛查未过/未跑)"
    if e.get("entry_sha") != ledger_entry_sha(e):
        return f"{doi}: entry_sha 内容哈希复算不符 (条目被篡改)"
    return None


def load_ledger(
    longdesc_dir: str,
    verified_only: bool = False,
    rejected: Optional[List[str]] = None,
) -> Set[str]:
    """_new_dois_ledger.json 已准入 DOI 集 (归一)。缺失 → 空集 (尚无新增准入)。

    verified_only=True (run_checks 生产口径): 只认含完整核验记录的条目
    (_ledger_entry_verified), 不合格条目视为未准入并逐条写入 rejected (若传入)。
    verified_only=False 为宽松历史视图 (batch_longdesc_gate 既有调用向后兼容;
    该路径的准入把关由批收尾①先行的 admit_new_dois.py + git diff 人工审查兜底)。
    """
    path = os.path.join(longdesc_dir, "_new_dois_ledger.json")
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    entries = data.get("entries", data) if isinstance(data, dict) else data
    out = set()
    for e in entries or []:
        if verified_only:
            why = _ledger_entry_verified(e)
            if why is not None:
                if rejected is not None:
                    rejected.append(why)
                continue
        doi = e.get("doi") if isinstance(e, dict) else e
        if doi:
            out.add(cl.normalize_doi(str(doi)))
    return out


def load_ledger_verified(longdesc_dir: str, rejected: Optional[List[str]] = None) -> Set[str]:
    """严格视图别名 (供 run_checks / WP5 终验): 只认完整核验记录条目。"""
    return load_ledger(longdesc_dir, verified_only=True, rejected=rejected)


def load_ack_registry(longdesc_dir: str) -> Set[str]:
    """no_doi_ack 编号登记集 (★ 检查项 3 加固)。

    来源二选一 (并集): _no_doi_ack_ledger.json (独立台账, list 或 {entries: [...]}) /
    _new_dois_ledger.json 的 no_doi_acks 节。条目 = 裸编号字符串或 {ack_id: ...} dict。
    """
    out: Set[str] = set()

    def _collect(items: Any) -> None:
        for e in items or []:
            ack = e.get("ack_id") if isinstance(e, dict) else e
            if ack and str(ack).strip():
                out.add(str(ack).strip())

    p1 = os.path.join(longdesc_dir, "_no_doi_ack_ledger.json")
    if os.path.exists(p1):
        with open(p1, encoding="utf-8") as f:
            data = json.load(f)
        _collect(data.get("entries", data) if isinstance(data, dict) else data)
    p2 = os.path.join(longdesc_dir, "_new_dois_ledger.json")
    if os.path.exists(p2):
        with open(p2, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            _collect(data.get("no_doi_acks"))
    return out


def load_top_journal_cfg(path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """顶刊清单 SSOT (config/top_journal_list.yaml)。缺失 → None (跳过该闸 + WARN)。"""
    p = path or DEFAULT_TOP_JOURNAL_YAML
    if not os.path.exists(p):
        return None
    import yaml
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _norm_venue(v: str) -> str:
    v = (v or "").lower().replace("&", "and")
    v = re.sub(r"\s+", " ", v).strip().rstrip(".")
    # ★ 官方刊名 'The Journal of Finance' 类前缀归一 (原为假红方向: 带 The 误判 field)
    v = re.sub(r"^the\s+", "", v)
    return v


def classify_citation(c: Dict[str, Any], cfg: Dict[str, Any]) -> str:
    """计分三分类 (§2.7): top / field / wp-preprint (+book 不计分母)。

    journal 型 venue 不在 top 清单 → 一律计非 top (field 或未知刊同待遇,
    进 (top+field) 分母); wp/arxiv → wp-preprint 不计"非顶刊"分母; book 同免。
    """
    t = c.get("type", "journal")
    if t in ("wp", "arxiv"):
        return "wp-preprint"
    if t == "book":
        return "book"
    v = _norm_venue(str(c.get("venue", "")))
    tops = {_norm_venue(x) for x in (cfg.get("top") or [])}
    return "top" if v in tops else "field"


def classify_citation_detailed(c: Dict[str, Any], cfg: Dict[str, Any]) -> str:
    """报告用五分类: top / field (清单列名) / unlisted (未列名刊) / wp-preprint / book。

    与 classify_citation 的计分口径 (field ≡ unlisted 同计非 top 分母) 不冲突 —
    本函数仅供全卷级构成报告 (v2.11, WP5 终局报告消费), 不参与闸判定。
    """
    coarse = classify_citation(c, cfg)
    if coarse != "field":
        return coarse
    v = _norm_venue(str(c.get("venue", "")))
    fields = {_norm_venue(x) for x in (cfg.get("field") or [])}
    return "field" if v in fields else "unlisted"


def family_top_anchor_gate(citations: List[Dict[str, Any]], cfg: Dict[str, Any]) -> Optional[str]:
    """★ v2.11 家族级硬闸 (2026-07-11 C1 实证校准): citations 中 top 分类 ≥1 条。

    零 top 锚 → 违规文案 (final 崩 / draft 告警, run_checks 分级); 合格 → None。
    保住每家族的顶刊支撑底线 (用户"国际顶级期刊学术支持"字面要求)。
    """
    classes = [classify_citation(c, cfg) for c in citations or []]
    if not classes:
        return None  # 无引文由 CITATION_MIN 条数闸另管, 此处不重复报
    if "top" not in classes:
        return ("顶刊结构闸: citations 中 top 分类 0 条 (零 top 锚, §2.7 v2.11 "
                "家族级硬闸 — 每家族须 ≥1 条顶刊支撑)")
    return None


def family_top_journal_gate(citations: List[Dict[str, Any]], cfg: Dict[str, Any]) -> Optional[str]:
    """家族级占比检查 (v2.11 降级为 WARN): (top+field 内) 非 top 占比 >30% → 文案。

    原 FATAL 判据经 C1 实证校准降级 (finance-centric 清单曾结构性打回 20+/36
    方法学家族); 占比数字记录供对抗审核聚焦与 WP5 终局报告。合格 → None。
    """
    classes = [classify_citation(c, cfg) for c in citations or []]
    denom = [x for x in classes if x in ("top", "field")]
    if not denom:
        return None
    non_top = sum(1 for x in denom if x != "top")
    frac = non_top / len(denom)
    if frac > 0.30:
        return (f"顶刊结构闸: (top+field 内) 非 top 占比 {non_top}/{len(denom)} = "
                f"{frac:.1%} > 30% (§2.7 v2.11 降级 WARN, 供对抗审核聚焦)")
    return None


def type_venue_crosscheck(
    citations: List[Dict[str, Any]], cfg: Dict[str, Any], fid: str,
) -> List[str]:
    """★ type↔venue 交叉校验 (WARN, 红队 NIT): type 自报 ∈ {wp, arxiv, book} 即整条
    退出 (top+field) 分母 — 期刊论文误标/恶标为 wp 可无限稀释非 top 占比绕过 30% 闸。
    venue 命中 top/field 清单却自报非 journal → WARN 供人工复核 (不改分类结果)。
    """
    warns: List[str] = []
    known = ({_norm_venue(x) for x in (cfg.get("top") or [])}
             | {_norm_venue(x) for x in (cfg.get("field") or [])})
    for c in citations or []:
        t = c.get("type", "journal")
        if t in ("wp", "arxiv", "book") and _norm_venue(str(c.get("venue", ""))) in known:
            warns.append(
                f"{fid}: citation type={t!r} 但 venue {c.get('venue')!r} 在 top/field "
                "清单内 (type 自报稀释顶刊分母嫌疑, 交叉校验 WARN — 确为该刊 WP 前身请改 venue)"
            )
    return warns


# ============================================================================
# ★ doi.org lint 扩域 (红队 P1-B / P2-C): frontmatter 递归标量 + 大小写变体
# ============================================================================

_DOIORG_CI_RE = re.compile(r"doi\.org/", re.IGNORECASE)
# 豁免路径 = DOI 的结构化承载字段 (差集闸/一致性断言的正规输入域)
_LINT_EXEMPT_PATH_RE = re.compile(r"^(citations\[\d+\]\.doi|new_dois\[\d+\])$")


def _iter_frontmatter_scalars(obj: Any, path: str = ""):
    """递归遍历 frontmatter, yield (路径, 字符串标量)。"""
    if isinstance(obj, str):
        yield path, obj
    elif isinstance(obj, dict):
        for k, v in obj.items():
            sub = f"{path}.{k}" if path else str(k)
            yield from _iter_frontmatter_scalars(v, sub)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            yield from _iter_frontmatter_scalars(v, f"{path}[{i}]")


def lint_frontmatter_doiorg(fam: cl.FamilyDoc) -> List[str]:
    """★ P1-B: frontmatter 全部标量值递归扫 doi.org (含大小写变体) = fatal。

    旁路封堵: formula/producer/unit 等标量字段藏 doi.org 链接可同时逃逸
    human_zone lint 与差集闸 (只查 citations[].doi), 并经计算链路段流入组装产物。
    citations[].doi 与 new_dois[] 是结构化 DOI 承载域 (裸 DOI, 本不含 doi.org),
    豁免; 其余一切标量 (含 citations[].title/alt_link 等) 命中即 fatal。
    """
    out: List[str] = []
    for path, val in _iter_frontmatter_scalars(fam.frontmatter or {}):
        if _LINT_EXEMPT_PATH_RE.match(path):
            continue
        if _DOIORG_CI_RE.search(val):
            out.append(
                f"{fam.family_id}: frontmatter 标量字段 {path} 含 doi.org 链接 "
                f"(§2.6 lint 扩域, 逃逸差集闸的旁路): {val[:80]!r}"
            )
    return out


def lint_doiorg_case_variants(fam: cl.FamilyDoc) -> List[str]:
    """★ P2-C: human_zone 大小写变体 doi.org (如 DOI.ORG/) 补捕。

    cl.lint_doiorg_outside_tail 的小写精确子串已捕小写命中; 本函数只在
    case-insensitive 命中数 > 精确小写命中数时报 (避免同一违规双报)。
    """
    hz = fam.human_zone or ""
    n_ci = len(_DOIORG_CI_RE.findall(hz))
    n_exact = hz.count("doi.org/")
    if n_ci > n_exact:
        return [
            f"{fam.family_id}: 渲染尾节外出现大小写变体 doi.org 链接 "
            f"(如 DOI.ORG/, {n_ci - n_exact} 处; §2.6 lint case-insensitive 扩域)"
        ]
    return []


def duplicate_doi_violations(citations: List[Dict[str, Any]], fid: str) -> List[str]:
    """★ 重复 DOI 闸 (计划 §2.10): 同家族 citations 内同一归一 DOI 出现 ≥2 次 = fatal。"""
    dois = [cl.normalize_doi(str(c.get("doi")))
            for c in citations or []
            if isinstance(c, dict) and str(c.get("doi", "") or "").strip()]
    dups = sorted({d for d in dois if dois.count(d) > 1})
    if dups:
        return [f"{fid}: citations 内重复 DOI (§2.10 禁灌水凑条数闸): {dups}"]
    return []


# ============================================================================
# ★ 新颖度闸 (计划 §2.8, 红队 P2: 原零实现)
# ============================================================================

NOVELTY_YEAR_MIN = 2023
NOVELTY_MIN_FRAC = 0.50
NOVELTY_EXEMPT_KEY = "novelty_exempt_rationale"


def compute_novelty(parsed: Dict[str, cl.FamilyDoc]) -> Dict[str, Any]:
    """全库 2023+ 引文占比统计 (供 run_checks 与 WP5 终验独立调用)。

    构念定义型家族例外: frontmatter 声明非空 novelty_exempt_rationale → 整族
    豁免出统计池 (分子分母都不计), 豁免家族与 rationale 进 report 供人工复核。
    """
    n_scored = n_recent = 0
    exempt: Dict[str, str] = {}
    for fid, fam in sorted(parsed.items()):
        rationale = str(fam.frontmatter.get(NOVELTY_EXEMPT_KEY, "") or "").strip()
        if rationale:
            exempt[fid] = rationale[:120]
            continue
        for c in fam.frontmatter.get("citations", []) or []:
            if not isinstance(c, dict):
                continue
            m = re.search(r"\d{4}", str(c.get("year", "")))
            if not m:
                continue
            n_scored += 1
            if int(m.group(0)) >= NOVELTY_YEAR_MIN:
                n_recent += 1
    frac = (n_recent / n_scored) if n_scored else None
    return {
        "year_min": NOVELTY_YEAR_MIN, "min_frac": NOVELTY_MIN_FRAC,
        "n_scored": n_scored, "n_recent": n_recent, "frac": frac,
        "exempt_families": exempt,
    }


def novelty_gate(
    parsed: Dict[str, cl.FamilyDoc],
    hard: Optional[bool] = None,
) -> Tuple[Dict[str, Any], Optional[str]]:
    """新颖度闸判定。返回 (统计 dict, 违规文案|None)。

    hard=None (auto): 全部家族 status=='final' (全卷收口) 才硬判 — 批级别家族
    天然偏科, 仅报告; hard=True/False 显式强制 (WP5 终验传 True)。
    """
    nov = compute_novelty(parsed)
    all_final = bool(parsed) and all(f.status == "final" for f in parsed.values())
    enforce = all_final if hard is None else bool(hard)
    nov["enforced"] = bool(enforce and nov["n_scored"] > 0)
    if nov["enforced"] and nov["frac"] < NOVELTY_MIN_FRAC:
        return nov, (
            f"新颖度硬闸 (§2.8): {NOVELTY_YEAR_MIN}+ 引文占比 "
            f"{nov['n_recent']}/{nov['n_scored']} = {nov['frac']:.1%} < "
            f"{NOVELTY_MIN_FRAC:.0%} (全卷级; 构念定义型家族可在 frontmatter 声明 "
            f"{NOVELTY_EXEMPT_KEY} 例外, 现豁免 {len(nov['exempt_families'])} 族)"
        )
    return nov, None


# ============================================================================
# 弱断言 (§2.6): 正文引注 (作者, 年份) ⊆ citations 渲染集 — WARN only
# ============================================================================

_PROSE_CITE_RE = re.compile(r"([A-Z][A-Za-z\-']{2,})(?:\s+(?:et\s+al\.?|and\s+\S+|&\s+\S+))?\s*\((\d{4})[a-z]?\)")


def weak_prose_citation_check(fam: cl.FamilyDoc) -> List[str]:
    warns = []
    citations = fam.frontmatter.get("citations", []) or []
    for m in _PROSE_CITE_RE.finditer(fam.human_zone or ""):
        surname, year = m.group(1), m.group(2)
        hit = any(
            str(c.get("year", "")) == year and surname.lower() in str(c.get("authors", "")).lower()
            for c in citations
        )
        if not hit:
            warns.append(
                f"{fam.family_id}: 正文引注 {surname} ({year}) 未命中 citations 渲染集 "
                "(弱断言 WARN, 供对抗审核聚焦; 中文行文误报可忽略)"
            )
    return warns


# ============================================================================
# 主检查
# ============================================================================

def run_checks(
    longdesc_dir: str,
    whitelist: Optional[Set[str]] = None,
    top_journal_cfg: Optional[Dict[str, Any]] = None,
    materialize: bool = False,
    novelty_hard: Optional[bool] = None,
) -> Dict[str, Any]:
    """全库检查。返回 report dict; 致命项非空时由 main() SystemExit(1)。

    参数注入 (whitelist/top_journal_cfg 可传, 便于测试 fixture 注入) —
    None 时取生产默认 (FILES_WHITELIST_ANCHOR 派生 / config/top_journal_list.yaml)。
    novelty_hard: None=auto (全 final 才硬判) / True/False 显式强制 (WP5 终验传 True)。
    """
    fatal: List[str] = []
    warns: List[str] = []

    idx_path = os.path.join(longdesc_dir, "_index.json")
    md_files = sorted(
        p for p in _glob.glob(os.path.join(longdesc_dir, "*.md"))
        if not os.path.basename(p).startswith("_")
    )
    if not os.path.exists(idx_path):
        if not md_files:
            return {"empty": True, "fatal": [], "warnings": [],
                    "note": f"长文库为空 ({longdesc_dir}) — WP0 未跑属预期, 跳过"}
        fatal.append(f"_index.json 缺失但存在 {len(md_files)} 个家族 md — 登记缺口, 拒跑")
        return {"empty": False, "fatal": fatal, "warnings": warns}

    with open(idx_path, encoding="utf-8") as f:
        index = json.load(f)
    families_idx: Dict[str, Any] = index.get("families", {}) or {}

    # frontmatter 解析 (失败 = SystemExit inside parse_family_md, §2.3 fail-loud)。
    # ★ P1-A 加固: family_id / status 的 SSOT 只认 _index.json — parsed 键一律取
    #   _index 中该文件对应键 (file_by_fid), frontmatter family_id 只作一致性校验
    #   (不等=fatal, 不得覆盖键→status 查表); frontmatter 声明 status 键 = fatal。
    parsed: Dict[str, cl.FamilyDoc] = {}
    file_by_fid = {str((m or {}).get("file", "")): fid for fid, m in families_idx.items()}
    for p in md_files:
        base = os.path.basename(p)
        idx_fid = file_by_fid.get(base, "")
        fam = cl.parse_family_md(p, family_id=idx_fid)
        fm_fid = str((fam.frontmatter or {}).get("family_id", "") or "").strip()
        if not idx_fid:
            fatal.append(f"{base}: 家族 md 未在 _index.json 登记 (file 键无此文件) — 登记缺口")
        elif fm_fid and fm_fid != idx_fid:
            fatal.append(
                f"{base}: frontmatter family_id {fm_fid!r} != _index.json 该文件对应键 "
                f"{idx_fid!r} (family_id SSOT=_index, frontmatter 不得覆盖 — 自贬 draft 旁路)"
            )
        if "status" in (fam.frontmatter or {}):
            fatal.append(
                f"{base}: frontmatter 声明 status 键 (status SSOT=_index.json, "
                "frontmatter 不得声明/覆盖)"
            )
        key = idx_fid or fm_fid or base
        fam.family_id = key                       # 强制 SSOT 键 (违规消息定位一致)
        fam.status = str((families_idx.get(key, {}) or {}).get("status", "draft"))
        if key in parsed:
            fatal.append(f"family_id 重复: {key} ({p})")
        parsed[key] = fam

    # 解析对账 (§2.3 防 fail-open; ★ P1-A: 集合相等而非仅家族数长度 — 等长换键欺骗被封)
    if set(parsed) != set(families_idx):
        fatal.append(
            f"解析对账闸: frontmatter 家族键集 != _index.json 家族键集 "
            f"(家族数 {len(parsed)} vs {len(families_idx)}; "
            f"index-only={sorted(set(families_idx) - set(parsed))[:5]}, "
            f"md-only={sorted(set(parsed) - set(families_idx))[:5]})"
        )

    if whitelist is None:
        whitelist = audit_dois.whitelist_dois()
    # ★ P1 台账加固: 生产口径只认 admit_new_dois.py 完整核验条目; 不合格条目视为
    #   未准入 + WARN 点名 (其 DOI 随后照走差集闸: final 崩 / draft 未声明崩)。
    ledger_rejected: List[str] = []
    ledger = load_ledger_verified(longdesc_dir, rejected=ledger_rejected)
    for why in ledger_rejected:
        warns.append(f"台账条目缺完整核验记录, 视为未准入 (须经 admit_new_dois.py): {why}")
    allowed = set(whitelist) | ledger
    ack_registry = load_ack_registry(longdesc_dir)
    if top_journal_cfg is None:
        top_journal_cfg = load_top_journal_cfg()
        if top_journal_cfg is None:
            warns.append(f"顶刊清单缺失 ({DEFAULT_TOP_JOURNAL_YAML}) — 顶刊结构闸跳过")

    all_frontmatter_dois: Set[str] = set()
    n_draft_over = 0
    # ★ v2.11 全卷级报告项 (不设新硬闸): final 家族聚合 top/field/unlisted 构成
    tj_mix: Dict[str, int] = {"top": 0, "field": 0, "unlisted": 0,
                              "wp-preprint": 0, "book": 0}
    for fid, fam in sorted(parsed.items()):
        status = fam.status
        citations = fam.frontmatter.get("citations", []) or []

        # no_doi_ack 闸 + citation 结构校验 (一律 fatal — 写手捏造书籍引文的自由通道)
        fatal.extend(e for c in citations for e in cl.validate_citation(c, fid))

        # ★ no_doi_ack 编号登记核验 (检查项 3 加固): 未登记 = fatal
        for c in citations:
            if not isinstance(c, dict) or str(c.get("doi", "") or "").strip():
                continue
            ack = str(c.get("no_doi_ack", "") or "").strip()
            if ack and ack not in ack_registry:
                fatal.append(
                    f"{fid}: no_doi_ack 编号 {ack!r} 未在台账登记 "
                    "(_no_doi_ack_ledger.json / _new_dois_ledger.json no_doi_acks 节; "
                    "经 admit_new_dois.py --register-ack 登记后方可引用)"
                )

        # ★ 重复 DOI 闸 (§2.10)
        fatal.extend(duplicate_doi_violations(citations, fid))

        cited = cl.rendered_dois(citations)
        all_frontmatter_dois |= cited

        # new_dois ⊆ citations[].doi 一致性断言 (§2.4)
        new_dois = {cl.normalize_doi(str(d)) for d in fam.frontmatter.get("new_dois", []) or []}
        if not new_dois <= cited:
            fatal.append(f"{fid}: new_dois 未同时以 citations 条目落地: {sorted(new_dois - cited)}")

        # 白名单差集闸 (§2.3, 含 v2.9 draft 出口)
        over = cited - allowed
        if over:
            if status == "draft" and over <= new_dois:
                n_draft_over += len(over)
                warns.append(
                    f"{fid}: draft 越权 DOI {sorted(over)} ⊆ 自身 new_dois 声明 "
                    "(降级告警; 批收尾①增量核验准入后归零)"
                )
            else:
                fatal.append(f"{fid}[{status}]: 白名单差集闸越权 DOI: {sorted(over)}")

        # 渲染物化一致性断言② (§2.1)
        if materialize:
            cl.materialize_rendered_citations(fam)
        if fam.rendered_block is None:
            msg = f"{fid}: 渲染尾节缺失 (rendered-citations fence) — audit_dois 核验域对其提取 0 条"
            (fatal if status == "final" else warns).append(msg)
        else:
            rdois = {
                audit_dois.clean_doi(m.group(1)).lower()
                for m in audit_dois.DOIORG_RE.finditer(fam.rendered_block)
            }
            if rdois != cited:
                fatal.append(
                    f"{fid}: 渲染段 DOI 集 != citations DOI 集 (陈旧尾节, 重跑物化): "
                    f"rendered-only={sorted(rdois - cited)[:3]}, cite-only={sorted(cited - rdois)[:3]}"
                )

        # 尾节外 doi.org 零命中 lint (§2.6) + ★ 大小写变体补捕 + ★ frontmatter 扩域
        fatal.extend(cl.lint_doiorg_outside_tail(fam))
        fatal.extend(lint_doiorg_case_variants(fam))
        fatal.extend(lint_frontmatter_doiorg(fam))

        # 顶刊结构闸 (§2.7 v2.11 双层) + ★ type↔venue 交叉校验 (WARN)
        if top_journal_cfg is not None:
            # 层①: 零 top 锚硬闸 (final 崩 / draft 告警)
            v_anchor = family_top_anchor_gate(citations, top_journal_cfg)
            if v_anchor:
                (fatal if status == "final" else warns).append(
                    f"{fid}[{status}]: {v_anchor}")
            # 层②: 非 top 占比 >30% 一律 WARN (原 FATAL 降级, 记录数字)
            v_frac = family_top_journal_gate(citations, top_journal_cfg)
            if v_frac:
                warns.append(f"{fid}[{status}]: {v_frac}")
            # 全卷级构成聚合 (final 家族; 报告项, 不设新硬闸)
            if status == "final":
                for c in citations:
                    if isinstance(c, dict):
                        tj_mix[classify_citation_detailed(c, top_journal_cfg)] += 1
            warns.extend(type_venue_crosscheck(citations, top_journal_cfg, fid))

        # 弱断言 (WARN only)
        warns.extend(weak_prose_citation_check(fam))

    # ★ 新颖度闸 (§2.8): 全卷级硬崩 / 批级别仅进 report
    novelty, nov_violation = novelty_gate(parsed, hard=novelty_hard)
    if nov_violation:
        fatal.append(nov_violation)

    # 渲染物化断言① (§2.1): longdesc 域 extract_refs 提取 DOI 数 ≥ 全库 frontmatter
    # citations 去重后唯一 DOI 总数 (⚠ 勿实现成逐家族求和 — 跨家族共享 DOI 恒红)
    extracted: Set[str] = set()
    for p in md_files:
        extracted |= set(audit_dois.extract_refs(p))
    if md_files and len(extracted) < len(all_frontmatter_dois):
        fatal.append(
            f"断言① 失败: longdesc 域 extract_refs 提取 {len(extracted)} 唯一 DOI "
            f"< frontmatter citations 全库去重 {len(all_frontmatter_dois)} — "
            "渲染物化空转 (先跑 --materialize 或生产入口物化)"
        )

    return {
        "empty": False,
        "n_families": len(parsed),
        "n_whitelist": len(whitelist),
        "n_ledger": len(ledger),
        "n_ledger_rejected": len(ledger_rejected),
        "n_frontmatter_dois": len(all_frontmatter_dois),
        "n_extracted_dois": len(extracted),
        "n_draft_over": n_draft_over,
        "top_journal_mix_final": {
            "counts": tj_mix,
            "fracs": {k: (v / total if total else None)
                      for total in [sum(tj_mix.values())] for k, v in tj_mix.items()},
        },
        "novelty": novelty,
        "fatal": fatal,
        "warnings": warns,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="家族长文库引文白名单差集闸 (WP1 §2.3)")
    ap.add_argument("--longdesc-dir", default=cl.default_longdesc_dir())
    ap.add_argument("--materialize", action="store_true",
                    help="检查前先做引文渲染物化回写 (幂等)")
    ap.add_argument("--top-journal-config", default=None)
    nov = ap.add_mutually_exclusive_group()
    nov.add_argument("--novelty-hard", dest="novelty_hard", action="store_true",
                     default=None, help="新颖度闸强制硬判 (WP5 终验口径)")
    nov.add_argument("--no-novelty-hard", dest="novelty_hard", action="store_false",
                     help="新颖度闸强制只报告 (默认 auto: 全 final 才硬判)")
    args = ap.parse_args(argv)

    report = run_checks(
        args.longdesc_dir,
        top_journal_cfg=load_top_journal_cfg(args.top_journal_config)
        if args.top_journal_config else None,
        materialize=args.materialize,
        novelty_hard=args.novelty_hard,
    )
    if report.get("empty"):
        print(report["note"])
        return 0
    print("===== check_longdesc_whitelist =====")
    for k in ("n_families", "n_whitelist", "n_ledger", "n_ledger_rejected",
              "n_frontmatter_dois", "n_extracted_dois", "n_draft_over"):
        print(f"  {k:<22} {report.get(k)}")
    nv = report.get("novelty") or {}
    frac = nv.get("frac")
    if frac is not None:
        print(f"  novelty_2023plus       {nv.get('n_recent')}/{nv.get('n_scored')} "
              f"({frac:.1%}, enforced={nv.get('enforced')})")
    else:
        print("  novelty_2023plus       0/0 (无可计年份引文, 跳过)")
    if nv.get("exempt_families"):
        print(f"  novelty_exempt         {sorted(nv['exempt_families'])}")
    mix = (report.get("top_journal_mix_final") or {}).get("counts") or {}
    if sum(mix.values()):
        total = sum(mix.values())
        parts = ", ".join(f"{k}={v} ({v / total:.1%})" for k, v in mix.items() if v)
        print(f"  top_journal_mix(final) {parts}  [n={total}]")
    for w in report["warnings"]:
        print("  WARN:", w)
    if report["fatal"]:
        for e in report["fatal"]:
            print("  FATAL:", e)
        raise SystemExit(1)
    print(f"  OK — 0 致命项 / {len(report['warnings'])} 告警 (终验须归零)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
