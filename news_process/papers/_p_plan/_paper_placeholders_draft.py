"""_paper_placeholders_draft.py — DRAFT for P1 merge into _common/stata_runner.py

⚠ THIS FILE IS NOT LOADED BY RUNTIME. It is a planning artifact.

Generated 2026-05-15 in P0.4 based on `_p0_audit_memo.md` § 4 (P1 parameterization).
At P1 it will be merged into `_common/stata_runner.py` next to the existing
`_KNOWN_PLACEHOLDERS` and `_VALID_SPEC_VALUES` constants.

Design rules:
- Tier 1 (universal) placeholders match the existing main-paper triad: kept as-is.
- Tier 2 (paper-level) are NEW. They default to project conventions but can be
  overridden via `--paper <id>` CLI or programmatic `paper_placeholders` arg.
- Tier 3 (paper-specific) are sparse per-paper add-ons; only the keys a paper
  actually uses appear in its dict.

At template rendering time, the merge order is:
    universal_choices → paper_defaults[paper_id] → user_overrides
(later wins.)
"""

from __future__ import annotations

# ============================================================================
# Tier 1: Universal placeholders (existing, do not modify)
# ============================================================================

_TIER1_UNIVERSAL = {
    'PROJECT_ROOT',       # absolute path injected at packaging time
    'MAIN_LOCUS_TRACK',   # 'lf' | 'lc'  — main paper only; derivative ignores
    'MAIN_SUBST_TRACK',   # 'sf' | 'sc'  — main paper only
    'MAIN_SENT_TRACK',    # 'full' | 'ctx'  — main paper only
}

# ============================================================================
# Tier 2: Paper-level placeholders (NEW in P1, all 5 papers fill these)
# ============================================================================

_TIER2_PAPER_LEVEL = {
    'PAPER_ID',
    'MAIN_DV',            # canonical dependent variable
    'CONTROLS',           # standard control set (string of var names)
    'CLUSTER_VAR',        # vce(cluster <var>) target
    'HET_VAR',            # heterogeneity interaction variable
}

# ============================================================================
# Tier 3: Paper-specific placeholders (NEW in P1, sparse per paper)
# ============================================================================

_TIER3_PAPER_SPECIFIC: dict[str, set[str]] = {
    'bank_fintech_tone': set(),  # all coverage via Tier 1 main-spec triad
    'benefit_society': {
        'ATTITUDE_VAR',      # benefit_mean_full
        'MECHANISM_TOKEN',   # token_adopt_kw_p50
        'MECHANISM_HIDDEN',  # hidden_adopt_kw_p50
        'MECHANISM_SUBST',   # subst_adopt_kw_p50
        'ROBUSTNESS_DV',     # CAR (short-term reaction, used in m3)
    },
    'brokerage_network': {
        'MAIN_ENDOG',        # peer_tone_lag1_full
        'MAIN_IV',           # peer_tone_2nd_lag1_full
        'TREATMENT_DCEP',    # dcep_post
        'TREATMENT_SANDBOX', # sandbox_post
        'CENTRALITY_BTW',    # bank_between_cent
        'CENTRALITY_CONS',   # bank_constraint
        'CENTRALITY_BROKER', # brokerage_eigen_cent
    },
    'strategic_diff': {
        'MAIN_DIFF_VAR',     # strat_diff_n5
        'FLUIDITY_VAR',      # strat_fluidity
        'SIM_MAX_VAR',       # strat_sim_max
        'BARTIK_IV',         # bartik_type_iv_full
        'TONE_VAR',          # llm_vote_tone_full (Bartik endogenous)
        'COHERENCE_VAR',     # coh_tfidf_c_full (for text_coherence companion)
    },
    'llm_peer': {
        'TONE_VAR',          # llm_vote_tone_full (endogenous)
        'LLM_PEER_IV',       # llm_peer_tone_iv_full (instrument)
        'LLM_PEER_COVERAGE_IV',  # llm_peer_coverage_iv
        'COMPETE_IDX',       # peer_compete_idx
        'CUTOFF_VARS',       # space-separated: llm_peer_tone_iv_full_70 ... _90
    },
}


# ============================================================================
# Paper defaults — project conventions
# ============================================================================

_PAPER_DEFAULTS: dict[str, dict[str, str]] = {
    'bank_fintech_tone': {
        'PAPER_ID': 'bank_fintech_tone',
        'MAIN_DV': 'ROA',
        'CONTROLS': 'ln_news_coverage media_breadth_z fin_media_frac central_media_frac',
        'CLUSTER_VAR': 'bank_id',
        'HET_VAR': 'is_soe',
        # Tier 1 (main paper triad) values supplied per build, not defaulted here.
    },
    'benefit_society': {
        'PAPER_ID': 'benefit_society',
        'MAIN_DV': 'ROA',
        'CONTROLS': 'ln_news_coverage media_breadth n_articles',
        'CLUSTER_VAR': 'bank_id',
        'HET_VAR': 'is_soe',
        'ATTITUDE_VAR': 'benefit_mean_full',
        'MECHANISM_TOKEN': 'token_adopt_kw_p50',
        'MECHANISM_HIDDEN': 'hidden_adopt_kw_p50',
        'MECHANISM_SUBST': 'subst_adopt_kw_p50',
        'ROBUSTNESS_DV': 'CAR',
    },
    'brokerage_network': {
        'PAPER_ID': 'brokerage_network',
        'MAIN_DV': 'ROA',
        'CONTROLS': 'ln_news_coverage media_hhi bank_scale_ord',
        'CLUSTER_VAR': 'prov_id',  # note: province-level, not bank
        'HET_VAR': 'is_soe',
        'MAIN_ENDOG': 'peer_tone_lag1_full',
        'MAIN_IV': 'peer_tone_2nd_lag1_full',
        'TREATMENT_DCEP': 'dcep_post',
        'TREATMENT_SANDBOX': 'sandbox_post',
        'CENTRALITY_BTW': 'bank_between_cent',
        'CENTRALITY_CONS': 'bank_constraint',
        'CENTRALITY_BROKER': 'brokerage_eigen_cent',
    },
    'strategic_diff': {
        'PAPER_ID': 'strategic_diff',
        'MAIN_DV': 'ROA',
        'CONTROLS': 'ln_news_coverage media_hhi bank_scale_ord',
        'CLUSTER_VAR': 'bank_id',
        'HET_VAR': 'is_soe',
        'MAIN_DIFF_VAR': 'strat_diff_n5',
        'FLUIDITY_VAR': 'strat_fluidity',
        'SIM_MAX_VAR': 'strat_sim_max',
        'BARTIK_IV': 'bartik_type_iv_full',
        'TONE_VAR': 'llm_vote_tone_full',
        'COHERENCE_VAR': 'coh_tfidf_c_full',
    },
    'llm_peer': {
        'PAPER_ID': 'llm_peer',
        'MAIN_DV': 'ROA',
        'CONTROLS': 'ln_news_coverage media_hhi n_articles',
        'CLUSTER_VAR': 'bank_id',
        'HET_VAR': 'is_soe',
        'TONE_VAR': 'llm_vote_tone_full',
        'LLM_PEER_IV': 'llm_peer_tone_iv_full',
        'LLM_PEER_COVERAGE_IV': 'llm_peer_coverage_iv',
        'COMPETE_IDX': 'peer_compete_idx',
        'CUTOFF_VARS': ('llm_peer_tone_iv_full_70 llm_peer_tone_iv_full_75 '
                        'llm_peer_tone_iv_full_80 llm_peer_tone_iv_full_85 '
                        'llm_peer_tone_iv_full_90'),
    },
}


# ============================================================================
# Combined whitelist (P1 will assign this to stata_runner._KNOWN_PLACEHOLDERS)
# ============================================================================

def build_known_placeholders() -> set[str]:
    """All accepted placeholder keys across all 5 papers (union)."""
    union: set[str] = set(_TIER1_UNIVERSAL) | set(_TIER2_PAPER_LEVEL)
    for keys in _TIER3_PAPER_SPECIFIC.values():
        union |= keys
    return union


# ============================================================================
# Smoke check (run via `python -m news_process.papers._p_plan._paper_placeholders_draft`)
# ============================================================================

def _self_check() -> None:
    """Self-consistency check: every Tier3 key per paper must appear in defaults."""
    errs: list[str] = []
    for paper, specific_keys in _TIER3_PAPER_SPECIFIC.items():
        defaults = _PAPER_DEFAULTS.get(paper, {})
        for key in specific_keys:
            if key not in defaults:
                errs.append(f"paper={paper!r} has Tier3 key {key!r} but no default")
        # Tier 2 keys all required
        for key in _TIER2_PAPER_LEVEL:
            if key not in defaults:
                errs.append(f"paper={paper!r} missing Tier2 key {key!r}")
    if errs:
        for e in errs:
            print(f"FAIL: {e}")
        raise SystemExit(1)
    union = build_known_placeholders()
    print(f"OK: 5 papers, {len(union)} placeholder keys total")
    print(f"   Tier 1 (universal): {sorted(_TIER1_UNIVERSAL)}")
    print(f"   Tier 2 (paper-level): {sorted(_TIER2_PAPER_LEVEL)}")
    for p in sorted(_PAPER_DEFAULTS):
        ks = sorted(_PAPER_DEFAULTS[p])
        print(f"   {p}: {len(ks)} defaults — {ks}")


if __name__ == '__main__':
    _self_check()
