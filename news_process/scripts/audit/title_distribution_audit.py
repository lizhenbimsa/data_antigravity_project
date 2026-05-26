"""scripts/audit/title_distribution_audit.py — v3.7.4 Phase 2 (L2).

# DO NOT IMPORT INTO PIPELINE; one-shot audit only.

Measures the 5 quantities (Q1-Q5) that anchor the joint-occurrence
discussion in Report v2.6 §1.1 and methodology v1.1 §4.4:

  Q1 = headline character-length distribution (percentiles)
  Q2 = body character-length distribution (percentiles)
  Q3 = P(F ∈ title) — title-level fintech-keyword hit rate
  Q4 = P(B ∈ title) — title-level bank-alias hit rate
  Q5 = article-level P(B ∩ F ∩ S ∈ title) joint-occurrence rate

S detection uses the same article-level signal that stages 22/23 use
(non-zero dict tone on the title text), via the shared lib
news_process.core.text.title_indicators.

Provenance:
  - panel SHA / commit hash captured in the output JSON
  - fintech keywords from config/preprocessing.yaml (frozen at d9bdea9d)
  - bank aliases from data/raw/bank_names.csv

Usage:
  python F:/Anaconda3/python.exe scripts/audit/title_distribution_audit.py \
      --in data/processed/13_news_with_ctx.parquet \
      --out logs/audit/title_distribution_$(timestamp).json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

# Path injection
_HERE = Path(__file__).resolve().parent
_PROJ_PARENT = _HERE.parent.parent.parent
if str(_PROJ_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJ_PARENT))

from news_process.core.config import load_config  # noqa: E402
from news_process.core.text.title_indicators import (  # noqa: E402
    compute_title_mentions_fintech,
    detect_bank_alias_in_title,
    detect_title_sentiment_word,
)


def _git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=_PROJ_PARENT
        ).decode().strip()
    except Exception:
        return "unknown"


def main() -> int:
    """CLI entrypoint: compute Q1-Q5 and emit JSON. Returns 0 on success."""
    p = argparse.ArgumentParser()
    p.add_argument("--in", dest="inp", required=True)
    p.add_argument("--out", dest="out", required=True)
    args = p.parse_args()

    cfg = load_config()
    df = pd.read_parquet(args.inp)
    n_total = len(df)

    title_col = "标题" if "标题" in df.columns else "title"
    body_col = "内容" if "内容" in df.columns else "content"
    target_bank_col = "target_bank" if "target_bank" in df.columns else None

    titles = df[title_col].fillna("").astype(str)
    bodies = df[body_col].fillna("").astype(str)

    title_lens = titles.str.len()
    body_lens = bodies.str.len()

    # v3.7.4 execution-time fix: load via load_fintech_dict() (matches stage 12)
    try:
        from news_process.core.text.ahocorasick import load_fintech_dict
        fintech_lex, _ac = load_fintech_dict(
            cfg.get("paths", {}).get("fintech_dict_file", "")
        )
        if not isinstance(fintech_lex, list):
            fintech_lex = list(fintech_lex) if fintech_lex else []
    except Exception:
        fintech_lex = []

    q3_hits = titles.apply(lambda t: compute_title_mentions_fintech(t, fintech_lex))
    if target_bank_col is None:
        q4_hits = pd.Series([False] * n_total, index=titles.index)
    else:
        q4_hits = pd.Series(
            [detect_bank_alias_in_title(t, str(b) if pd.notna(b) else "")
             for t, b in zip(titles, df[target_bank_col])],
            index=titles.index,
        )
    q5_sentiment_hits = titles.apply(detect_title_sentiment_word)

    q5_joint = (q3_hits & q4_hits & q5_sentiment_hits)

    def pct(s: pd.Series, p: float) -> float:
        """Return the p-th quantile of series s as a float."""
        return float(s.quantile(p))

    result = {
        "provenance": {
            "git_head": _git_head(),
            "input_parquet": args.inp,
            "input_sha256_first_4kb": hashlib.sha256(
                Path(args.inp).open("rb").read(4096)
            ).hexdigest(),
            "n_articles": int(n_total),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "fintech_lexicon_size": len(fintech_lex),
        },
        "Q1_title_length": {
            "p5": pct(title_lens, 0.05),
            "p25": pct(title_lens, 0.25),
            "p50_median": pct(title_lens, 0.50),
            "p75": pct(title_lens, 0.75),
            "p95": pct(title_lens, 0.95),
            "mean": float(title_lens.mean()),
        },
        "Q2_body_length": {
            "p5": pct(body_lens, 0.05),
            "p25": pct(body_lens, 0.25),
            "p50_median": pct(body_lens, 0.50),
            "p75": pct(body_lens, 0.75),
            "p95": pct(body_lens, 0.95),
            "mean": float(body_lens.mean()),
        },
        "Q3_title_fintech_hit_rate": float(q3_hits.mean()),
        "Q4_title_bank_alias_hit_rate": float(q4_hits.mean()),
        "Q5_joint_occurrence_rate": float(q5_joint.mean()),
        "framing_zone": (
            "<15%" if q5_joint.mean() < 0.15 else
            "15-50%" if q5_joint.mean() < 0.50 else
            "50-70%" if q5_joint.mean() < 0.70 else
            ">70%"
        ),
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"[OK] Q1-Q5 written to {out_path}")
    print(json.dumps({k: v for k, v in result.items() if not k.startswith("Q1")}, indent=2,
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
