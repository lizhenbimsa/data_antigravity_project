"""news_process.core.text.title_indicators — v3.7.4 EP-B3 shared lib.

Shared between:
  - stage 13 production path (`pipeline/text/ctx_materializer.py`)
  - one-shot audit script (`scripts/audit/title_distribution_audit.py`)

Single source of truth eliminates the L2-vs-L3 indicator drift risk
identified in EP-B3 (third-round audit, MEMORY shim_inventory).

Public API:
  compute_title_mentions_fintech(title, lexicon) -> bool
  compute_title_length_bucket(title, median) -> int  (0 = ≤median, 1 = >median)
  detect_title_sentiment_word(title)         -> bool
  detect_bank_alias_in_title(title, target_bank) -> bool

All functions are pure and deterministic.
"""
from __future__ import annotations

# Minimal Chinese sentiment lexicon — anchor: jiang/yao/bian/du/you 5-dict
# union (frozen at v3.7.4 d9bdea9d). Used only for the audit-script Q5
# proxy; production pipelines compute sentiment via stages 21/22/23.
_SENTIMENT_HINTS_CN: frozenset[str] = frozenset({
    # positive
    "上涨", "增长", "盈利", "增", "强势", "突破", "回升", "向好", "利好",
    "良好", "稳健", "提升", "扩大", "成功", "领先", "优秀", "亮眼", "创新高",
    "佳", "繁荣", "积极", "向上", "看好", "推动", "受益",
    # negative
    "下跌", "亏损", "下滑", "暴跌", "重挫", "回落", "走低", "利空", "下行",
    "疲软", "低迷", "萎缩", "失败", "落后", "下降", "不振", "承压", "走弱",
    "降", "减", "弱", "消极", "看空",
    # tone-laden generics
    "震荡", "调整", "整顿", "处罚", "约谈", "调查",
})


def compute_title_mentions_fintech(title: str, fintech_lexicon: list[str]) -> bool:
    """True iff any fintech keyword appears in the title text."""
    if not title or not fintech_lexicon:
        return False
    title = str(title)
    return any(kw and kw in title for kw in fintech_lexicon)


def compute_title_length_bucket(title: str, median: int) -> int:
    """0 if title length ≤ median; 1 if > median."""
    if title is None:
        return 0
    return 0 if len(str(title)) <= int(median) else 1


def detect_title_sentiment_word(title: str) -> bool:
    """True iff title contains any Chinese sentiment hint word.

    Used by L2 audit script for Q5 proxy. NOT a production-grade
    sentiment classifier — that is provided by stages 21/22/23.
    """
    if not title:
        return False
    return any(w in title for w in _SENTIMENT_HINTS_CN)


def detect_bank_alias_in_title(title: str, target_bank: str) -> bool:
    """True iff target_bank name (or simple alias) appears in title.

    Audit-script utility. Production pipeline uses
    `core.text.entity_context.get_target_aliases` for full alias coverage.
    """
    if not title or not target_bank or target_bank in ("nan", "None"):
        return False
    title = str(title)
    target = str(target_bank).strip()
    if not target:
        return False
    if target in title:
        return True
    # Strip common Chinese bank suffixes for fuzzy match
    for suffix in ("银行股份有限公司", "股份有限公司", "银行"):
        if target.endswith(suffix):
            stem = target[: -len(suffix)]
            if stem and stem in title:
                return True
    return False
