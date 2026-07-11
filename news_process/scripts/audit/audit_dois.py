"""全语料文献锚点 DOI 审计引擎: 对四份 LITERATURE_ANCHORS_*.md 逐条 DOI->标题回比。

直连 Crossref (api.crossref.org) + DataCite (api.datacite.org, arXiv/DataCite DOI)。
不调用任何子智能体、不耗模型 token, 不受会话用量上限影响, 故可对全语料 100% 覆盖(非抽样)。
仅从 https://doi.org/<DOI> 链接提取真引用 (避开散文里反引号包裹的已纠错 DOI + 老式括号 DOI)。
报告写系统临时目录 (避免 Windows GBK 控制台崩溃 / 污染仓库)。

权威报告: scripts/audit/LITERATURE_ANCHORS_AUDIT_2026-06-24.md
用法: python scripts/audit/audit_dois.py
"""
import json
import os
import re
import ssl
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    import certifi
    CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:  # noqa: BLE001
    CTX = ssl.create_default_context()

MAILTO = "lizhen.ec@gmail.com"
UA = f"news-process-litaudit/1.0 (mailto:{MAILTO})"
OUTDIR = os.path.join(tempfile.gettempdir(), "litaudit")
os.makedirs(OUTDIR, exist_ok=True)

_HERE = os.path.dirname(os.path.abspath(__file__))

# ── WP1 两列表分离 (2026-07-10 计划 §2.5, v2.3 防自授权环) ──────────────────
# FILES_WHITELIST_ANCHOR = 13 静态路径冻结列表 = **白名单唯一派生源**。
# ⚠ 铁律: config/codebook_longdesc/*.md (家族长文库) **永不**并入本列表 — 若把
# glob 扩进同一列表再派生白名单, 家族 md 渲染出的 DOI 会自动并入白名单 →
# check_longdesc_whitelist 差集闸恒真、_new_dois_ledger 台账整体架空。
# ⚠ 2026-07-11 红队整改 (citation-gates NIT): 冻结为 tuple — FILES 别名与本锚共享
#   同一对象, 若为可变 list, 第三方脚本 append FILES 即静默污染白名单派生源。
FILES_WHITELIST_ANCHOR = (
    os.path.join(_HERE, "LITERATURE_ANCHORS_2026-06-13.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_2026-06-21.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_EXPANSION_2026-06-22.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_III_2026-06-24.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_IV_2026-06-26.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_V_2026-07-01.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_VI_2026-07-06.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_VII_2026-07-06.md"),
    # 第八补编 (2026-07-10): company_tax_bank 税调×银行共现面板专项 79 条
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_VIII_2026-07-10.md"),
    # 第九补编 (2026-07-10): 三文件夹功能专项 (两管线补遗 + LLMs_for_FinTech_dic 全量) 79 条
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_IX_2026-07-10.md"),
    # 前沿(银企共现面板)学术锚点归档: 137 DOI 并入主机械闸 (2026-07-06 第七补编轮)
    os.path.join(_HERE, "COMPANY_BANK_COOC_PANEL_PLAN_ARCHIVE_2026-07-04.md"),
    # LLMs_for_FinTech_dic 两份修复后文档并入主机械闸 (2026-07-10 第九补编轮, 修复台账见第九补编 §二)
    os.path.join(_HERE, "..", "..", "LLMs_for_FinTech_dic", "FinTech_Dictionary_LLMs_Paper_Final.md"),
    os.path.join(_HERE, "..", "..", "LLMs_for_FinTech_dic", "FinTech_Dictionary_Fleiss_Kappa_Methodology.md"),
)

# 向后兼容别名 (其他会话/脚本在用 audit_dois.FILES; 语义 = 白名单锚, 不含 glob 域)
FILES = FILES_WHITELIST_ANCHOR

# 家族长文库目录 (机械核验域第二来源; 只进 FILES_AUDIT_ALL, 永不进白名单派生)
LONGDESC_DIR = os.path.normpath(
    os.path.join(_HERE, "..", "..", "config", "codebook_longdesc"))


def longdesc_md_files():
    """家族长文库 md 清单 (glob; 排除 _ 前缀内部文件如 _TEMPLATE/_index)。"""
    import glob as _glob
    return sorted(
        p for p in _glob.glob(os.path.join(LONGDESC_DIR, "*.md"))
        if not os.path.basename(p).startswith("_")
    )


def audit_all_files(strict=True):
    """FILES_AUDIT_ALL = 锚 ∪ glob(config/codebook_longdesc/*.md) — 机械核验域。

    三断言 (计划 §2.5 / §9.3, strict=True 时 fail-loud):
      ① 库非空 (_index.json 有家族) 时 glob > 0 (防 fail-open 静默漏检);
      ② glob 家族 md 数 == _index.json 家族数 (对账);
      ③ 白名单派生输入 ∩ glob(codebook_longdesc) == ∅ (防白名单膨胀/自授权环)。
    """
    g = longdesc_md_files()
    idx_path = os.path.join(LONGDESC_DIR, "_index.json")
    if strict and os.path.exists(idx_path):
        with open(idx_path, encoding="utf-8") as f:
            idx = json.load(f)
        n_fam = len(idx.get("families", {}) or {})
        if n_fam > 0 and len(g) == 0:
            raise SystemExit(
                f"[audit_dois] 断言① 失败: _index.json 有 {n_fam} 家族但 glob 到 0 个 "
                f"家族 md ({LONGDESC_DIR}) — fail-open 风险, 拒跑")
        if n_fam > 0 and len(g) != n_fam:
            raise SystemExit(
                f"[audit_dois] 断言② 失败: glob 家族 md 数 {len(g)} != _index.json "
                f"家族数 {n_fam} — 核验域与登记不对账, 拒跑")
    anchor_abs = {os.path.normcase(os.path.normpath(os.path.abspath(p)))
                  for p in FILES_WHITELIST_ANCHOR}
    glob_abs = {os.path.normcase(os.path.normpath(os.path.abspath(p))) for p in g}
    inter = anchor_abs & glob_abs
    if inter:
        raise SystemExit(
            f"[audit_dois] 断言③ 失败: 白名单派生输入 ∩ glob(codebook_longdesc) 非空 "
            f"({sorted(inter)[:3]}) — 自授权环, 拒跑")
    return list(FILES_WHITELIST_ANCHOR) + g


def whitelist_dois():
    """白名单 DOI 集 (唯一派生源 = FILES_WHITELIST_ANCHOR; 供 check_longdesc_whitelist)。

    2026-07-11 红队整改: 锚文件缺失从 print-WARN 升级为 SystemExit — 13 路径是
    冻结列表且本 repo 实际发生过并发会话覆盖锚文件事故 (SUPPLEMENT_VIII), 缺失
    继续跑 = 白名单静默塌缩 → 差集闸大面积假红/覆盖缺口, 必须 fail-loud。
    """
    out = set()
    for p in FILES_WHITELIST_ANCHOR:
        try:
            out |= set(extract_refs(p))
        except FileNotFoundError:
            raise SystemExit(
                f"[audit_dois] 白名单锚文件缺失 (fail-loud, 防白名单静默塌缩): {p}")
    return out


# ⚠ 2026-07-11 红队整改 (P2-C): re.IGNORECASE — URL 主机名大小写不敏感, 正文写
#   `https://DOI.ORG/10.x/...` 浏览器照常解析却逃逸大小写敏感的 lint 与 extract_refs。
#   只会多捕不会少捕 (锚文件既有行为零回归); 捕获后统一 clean_doi().lower() 归一
#   (extract_refs / check_longdesc_whitelist / batch_longdesc_gate 三处消费端均已 .lower())。
DOIORG_RE = re.compile(r"doi\.org/(10\.\S+)", re.IGNORECASE)

# 本地 {doi: meta} 元数据缓存 (计划 §2.5: OK 条目免重查 Crossref, 降全量重跑
# 15-30 分钟串行成本; 状态逐 run 重算, 只缓存解析成功的 title/container/year)。
# ⚠ 2026-07-11 红队整改 (缓存投毒 NIT): 缓存位于共享临时目录, 同机任意进程可预写
#   伪造 title 使幻觉 DOI 免网络判 OK → 缓存加来源签名 (内容哈希), 只信任本工具
#   自身写出的缓存; 无签名/签名不符 → 整体弃用回退真网络回比 (旧扁平格式同弃)。
CACHE_PATH = os.path.join(OUTDIR, "doi_meta_cache.json")
_CACHE_SIG_SALT = "news-process-litaudit-cache-v2:"


def _cache_signature(entries):
    import hashlib
    blob = json.dumps(entries, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256((_CACHE_SIG_SALT + blob).encode("utf-8")).hexdigest()


def _load_meta_cache():
    try:
        with open(CACHE_PATH, encoding="utf-8") as f:
            c = json.load(f)
        if not isinstance(c, dict):
            return {}
        entries = c.get("entries")
        if not isinstance(entries, dict) or c.get("_signature") != _cache_signature(entries):
            if c:  # 旧扁平格式 / 无签名 / 被篡改 → 一次性弃用 (回退网络回比, 方向安全)
                print("WARN meta cache unsigned or tampered -> ignored (will refetch)")
            return {}
        return entries
    except Exception:  # noqa: BLE001
        return {}


def _save_meta_cache(cache):
    try:
        payload = {"_generator": "audit_dois.py", "_signature": _cache_signature(cache),
                   "entries": cache}
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=0)
    except Exception as e:  # noqa: BLE001
        print(f"WARN meta cache save failed: {e}")


def clean_doi(d):
    d = d.strip()
    d = re.sub(r"[.,;]+$", "", d)
    if "(" not in d:  # 老式 Elsevier DOI 含 (YY), 不可截断
        d = re.sub(r"[)\]]+$", "", d)
    return d.strip("`*。）)")


def is_cnki(doi):
    return doi.startswith("10.13821") or doi.startswith("10.13653") or "cnki" in doi


def is_arxiv(doi):
    return doi.startswith("10.48550")


def extract_refs(path):
    out = {}
    short = os.path.basename(path)
    with open(path, encoding="utf-8") as f:
        for line in f:
            for m in DOIORG_RE.finditer(line):
                doi = clean_doi(m.group(1)).lower()
                if not re.match(r"^10\.\d{4,9}/", doi):
                    continue
                ln = line.strip()
                if doi not in out or len(ln) > len(out[doi][0]):
                    out[doi] = (ln, short)
    return out


def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, context=CTX, timeout=40) as r:
        return json.load(r)


def fetch_crossref(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="") + "?mailto=" + MAILTO
    d = http_json(url)["message"]
    title = (d.get("title") or [""])
    title = title[0] if title else ""
    cont = (d.get("container-title") or [])
    cont = cont[0] if cont else ""
    yr = None
    for k in ("published-print", "published", "issued", "published-online"):
        v = d.get(k)
        if v and v.get("date-parts") and v["date-parts"][0]:
            yr = v["date-parts"][0][0]
            break
    return {"title": title, "container": cont, "year": yr, "src": "crossref"}


def fetch_datacite(doi):
    url = "https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe="")
    a = http_json(url)["data"]["attributes"]
    titles = a.get("titles") or []
    title = titles[0].get("title", "") if titles else ""
    cont = a.get("publisher") or ""
    if isinstance(cont, dict):
        cont = cont.get("name", "")
    return {"title": title, "container": cont, "year": a.get("publicationYear"), "src": "datacite"}


def norm(s):
    s = s.lower().replace("‐", "-").replace("–", "-").replace("—", "-")
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"[^a-z0-9 ]", " ", s)


def overlap(resolved_title, apa_line):
    ta = {t for t in norm(resolved_title).split() if len(t) > 2}
    if not ta:
        return 1.0
    tb = set(norm(apa_line).split())
    return len(ta & tb) / len(ta)


def _resolve_doi(doi, cache):
    """解析单 DOI 元数据 (缓存命中免网络; 只缓存解析成功条目)。返回 (rec|None, err)。"""
    hit = cache.get(doi)
    if hit and hit.get("title"):
        return hit, None
    rec, err = None, None
    fetchers = (fetch_datacite,) if is_arxiv(doi) else (fetch_crossref, fetch_datacite)
    for fetcher in fetchers:
        try:
            rec = fetcher(doi)
            if rec and rec.get("title"):
                cache[doi] = rec
                break
        except urllib.error.HTTPError as e:
            err, rec = f"HTTP {e.code}", None
        except Exception as e:  # noqa: BLE001
            err, rec = f"{type(e).__name__}:{str(e)[:50]}", None
        time.sleep(0.05)
    return rec, err


def _judge(doi, line, rec, err, file_of):
    """状态判定 (逐 run 重算, 不缓存): OK / TITLE_MISMATCH / YEAR_DIFF / UNRESOLVED / CNKI_EXPECTED。"""
    m = re.search(r"\((\d{4})[a-z]?\)", line)
    apa_year = int(m.group(1)) if m else None
    ov = cr_year = None
    resolved_title = src = ""
    if not rec or not rec.get("title"):
        status = "CNKI_EXPECTED" if is_cnki(doi) else "UNRESOLVED"
    else:
        resolved_title, src, cr_year = rec["title"], rec["src"], rec.get("year")
        ov = overlap(resolved_title, line)
        yr_bad = (cr_year and apa_year and abs(int(cr_year) - apa_year) > 1)
        status = "TITLE_MISMATCH" if ov < 0.6 else ("YEAR_DIFF" if yr_bad else "OK")
    return {
        "doi": doi, "status": status, "overlap": round(ov, 3) if ov is not None else None,
        "apa_year": apa_year, "cr_year": cr_year, "src": src,
        "resolved_title": resolved_title, "apa_line": line[:320],
        "files": sorted(file_of.get(doi, [])), "err": err,
    }


def main():
    all_refs, file_of = {}, {}
    # WP1 两列表分离: 机械核验域 = FILES_AUDIT_ALL (锚 ∪ 家族长文库 glob, 三断言内含)
    for p in audit_all_files():
        try:
            d = extract_refs(p)
        except FileNotFoundError:
            print("WARN missing:", p)
            continue
        for doi, (ln, short) in d.items():
            if doi not in all_refs or len(ln) > len(all_refs[doi]):
                all_refs[doi] = ln
            file_of.setdefault(doi, set()).add(short)

    dois = sorted(all_refs)
    print("UNIQUE reference DOIs (from doi.org links):", len(dois))

    cache = _load_meta_cache()
    n_cache_hit = sum(1 for d in dois if cache.get(d, {}).get("title"))
    print(f"meta cache: {n_cache_hit}/{len(dois)} 命中 ({CACHE_PATH})")

    results = []
    for i, doi in enumerate(dois):
        line = all_refs[doi]
        was_cached = bool((cache.get(doi) or {}).get("title"))
        rec, err = _resolve_doi(doi, cache)
        results.append(_judge(doi, line, rec, err, file_of))
        if (i + 1) % 50 == 0:
            print(f"  ...{i + 1}/{len(dois)}")
        if not was_cached:
            time.sleep(0.06)

    # UNRESOLVED 单次重试 (计划 §2.5: 防网络抖动噪声红旗; CNKI_EXPECTED 不重试)
    retry_idx = [i for i, r in enumerate(results) if r["status"] == "UNRESOLVED"]
    if retry_idx:
        print(f"retrying {len(retry_idx)} UNRESOLVED once ...")
        for i in retry_idx:
            doi = results[i]["doi"]
            time.sleep(0.5)
            rec, err = _resolve_doi(doi, cache)
            results[i] = _judge(doi, all_refs[doi], rec, err, file_of)

    _save_meta_cache(cache)

    with open(os.path.join(OUTDIR, "audit_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    out = ["===== DOI AUDIT SUMMARY =====", f"total unique reference DOIs = {len(results)}"]
    for k in sorted(counts):
        out.append(f"  {k:<16} {counts[k]}")
    out.append("\n===== FLAGGED (status != OK) =====")
    for r in results:
        if r["status"] == "OK":
            continue
        out += [
            "",
            f"[{r['status']}] {r['doi']} (ov={r['overlap']} apa_yr={r['apa_year']} "
            f"cr_yr={r['cr_year']} src={r['src']} err={r['err']})",
            "   resolved: " + r["resolved_title"][:180],
            "   apa     : " + r["apa_line"][:180],
        ]
    report = "\n".join(out)
    with open(os.path.join(OUTDIR, "audit_report.txt"), "w", encoding="utf-8") as f:
        f.write(report)
    print("\n".join(l for l in out if all(ord(c) < 128 for c in l))[:4000])
    print(f"\n[outputs -> {OUTDIR}]")


if __name__ == "__main__":
    main()
