import requests
import json
import time
from pathlib import Path

queries = [
    "fintech dictionary textual analysis",
    "large language models finance textual analysis",
    "financial dictionary construct Loughran McDonald",
    "textual analysis machine learning finance",
    "FinBERT financial text mining",
    "ChatGPT finance stock market language models"
]

papers = []
seen_ids = set()

for q in queries:
    print(f"Searching for: {q}")
    url = f"https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": q,
        "limit": 30,
        "fields": "title,authors,venue,year,url,externalIds,abstract"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "data" in data:
            for p in data["data"]:
                if p["paperId"] not in seen_ids:
                    seen_ids.add(p["paperId"])
                    # Filter for decent venues or recent years
                    venue = p.get("venue", "") or ""
                    year = p.get("year", 0) or 0
                    if year >= 2011: # Post Loughran & McDonald 2011
                        authors = ", ".join([a["name"] for a in p.get("authors", [])])
                        url_link = p.get("url", "")
                        if "externalIds" in p and "DOI" in p["externalIds"]:
                            url_link = f"https://doi.org/{p['externalIds']['DOI']}"
                        papers.append({
                            "title": p.get("title", ""),
                            "authors": authors,
                            "venue": venue,
                            "year": year,
                            "url": url_link,
                            "abstract": p.get("abstract", "")
                        })
    except Exception as e:
        print(f"Error on {q}: {e}")
    time.sleep(2) # rate limit

# specifically add Loughran and McDonald 2011 as it's the foundation
papers.insert(0, {
    "title": "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks",
    "authors": "Tim Loughran, Bill McDonald",
    "venue": "The Journal of Finance",
    "year": 2011,
    "url": "https://doi.org/10.1111/j.1540-6261.2010.01625.x",
    "abstract": ""
})

papers = sorted(papers, key=lambda x: x["year"], reverse=True)

with open(Path(__file__).resolve().parent / "fetched_papers.json", "w", encoding="utf-8") as f:
    json.dump(papers[:60], f, ensure_ascii=False, indent=2)

print(f"Saved {min(len(papers), 60)} papers.")
