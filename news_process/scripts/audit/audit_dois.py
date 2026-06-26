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
FILES = [
    os.path.join(_HERE, "LITERATURE_ANCHORS_2026-06-13.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_2026-06-21.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_EXPANSION_2026-06-22.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_III_2026-06-24.md"),
    os.path.join(_HERE, "LITERATURE_ANCHORS_SUPPLEMENT_IV_2026-06-26.md"),
]

DOIORG_RE = re.compile(r"doi\.org/(10\.\S+)")


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


def main():
    all_refs, file_of = {}, {}
    for p in FILES:
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

    results = []
    for i, doi in enumerate(dois):
        line = all_refs[doi]
        rec, err = None, None
        fetchers = (fetch_datacite,) if is_arxiv(doi) else (fetch_crossref, fetch_datacite)
        for fetcher in fetchers:
            try:
                rec = fetcher(doi)
                if rec and rec.get("title"):
                    break
            except urllib.error.HTTPError as e:
                err, rec = f"HTTP {e.code}", None
            except Exception as e:  # noqa: BLE001
                err, rec = f"{type(e).__name__}:{str(e)[:50]}", None
            time.sleep(0.05)

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
        results.append({
            "doi": doi, "status": status, "overlap": round(ov, 3) if ov is not None else None,
            "apa_year": apa_year, "cr_year": cr_year, "src": src,
            "resolved_title": resolved_title, "apa_line": line[:320],
            "files": sorted(file_of.get(doi, [])), "err": err,
        })
        if (i + 1) % 50 == 0:
            print(f"  ...{i + 1}/{len(dois)}")
        time.sleep(0.06)

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
