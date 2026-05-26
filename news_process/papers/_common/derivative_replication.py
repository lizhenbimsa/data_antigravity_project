"""news_process.papers._common.derivative_replication — Stata replication
package generator for the 4 derivative papers.

P1 (2026-05-15): Parallel to ``stata_runner.build_replication_package`` (which
is locked to the main paper ``bank_fintech_tone``). This module handles the
4 derivative papers (``benefit_society`` / ``brokerage_network`` /
``strategic_diff`` / ``llm_peer``) without touching the main-paper flow.

Why a separate module
---------------------
- ``stata_runner.build_replication_package`` validates main-paper triad
  (``MAIN_LOCUS_TRACK`` / ``MAIN_SUBST_TRACK`` / ``MAIN_SENT_TRACK``) as
  required; derivative papers do not have those tracks.
- Templates for the main paper live at ``stata_templates/*.do.tmpl``;
  derivative papers live at ``stata_templates/<paper_id>/*.do.tmpl``.
- Keeps main-paper code path (and its 73 tests) entirely untouched.

Design rules
------------
- Pure functions; no global state.
- Re-uses ``stata_runner._get_git_commit_hash_with_dirty`` for commit
  fingerprinting (single source of truth for that detail).
- Substitution is fail-fast on unresolved ``{{...}}`` (same discipline as
  ``stata_runner._substitute_placeholders``).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping

# Q1.4 (2026-05-15): commit-hash helper extracted to _git_utils.py to break
# the stata_runner ↔ derivative_replication import cycle introduced by the
# _PAPER_DEFAULTS single-source-of-truth consolidation.
from news_process.papers._common._git_utils import _get_git_commit_hash_with_dirty

# ============================================================================
# 4 derivative paper IDs — main paper bank_fintech_tone deliberately excluded.
# ============================================================================

_DERIVATIVE_PAPER_IDS: frozenset[str] = frozenset({
    'benefit_society',
    'brokerage_network',
    'strategic_diff',
    'llm_peer',
    # RR7-1 (Review-only audit): B-route 3 new papers use same per-paper replication
    # path as the 4 derivative papers. Naming kept as "_DERIVATIVE_*" for backwards-
    # compat (semantically it means "non-main-paper IDs handled by per-paper template
    # instantiation"; the historical "derivative of bank_fintech_tone" framing is
    # superseded by the B-route plan).
    'bank_fintech_attention',
    'bank_fintech_substance',
    'bank_fintech_locus',
    # v3.5.1 final-audit finding (R3): P5 'bank_fintech_collab' (v3.4.0 立项) onboarding
    # 未完整 — 缺 en/zh manuscript + refs.bib (v3.4.0 epoch 4 遗留). 加入会引发
    # test_papers_b_route 4 项 baseline regression (manuscript / refs.bib 缺失). 故 v3.5.1
    # 保持 v3.4.0 现状, P5 完整 onboarding 由独立 PR (P5 follow-up) 处理. 暂留
    # 20_collab_clarity_robustness.do.tmpl 为 "dormant template" 等待启用.
})


def is_derivative_paper(paper_id: str) -> bool:
    """True iff paper_id is one of the 4 derivative papers."""
    return paper_id in _DERIVATIVE_PAPER_IDS


# ============================================================================
# Placeholder defaults per paper (Tier 2 universal + Tier 3 specific).
# ============================================================================

_PAPER_DEFAULTS: dict[str, dict[str, str]] = {
    'benefit_society': {
        'PAPER_ID': 'benefit_society',
        'MAIN_DV': 'ROA',
        'CONTROLS': 'ln_news_coverage media_breadth n_articles',
        'CLUSTER_VAR': 'bank_id',
        'HET_VAR': 'is_listed',  # PAP v1.0-final DP-9: replaces is_soe (F-R3-H2)
        # v3.2.1 dual-track (plan v2.12, F-M1 / F-H3): ATTITUDE_VAR retained as
        # backwards-compat alias = full track; ATTITUDE_FULL / ATTITUDE_CTX are
        # the canonical dual-track placeholders used by new templates
        # (20_tableA1_inter_track_kappa, 21_tableA2_attitude_track_switch,
        # 31_figure2_coefplot_dual, 17b_table8b_shrinkage_dual).
        'ATTITUDE_VAR': 'benefit_mean_full',
        'ATTITUDE_FULL': 'benefit_mean_full',
        'ATTITUDE_CTX': 'benefit_mean_ctx',
        'BENEFIT_POS_FRAC_FULL': 'benefit_pos_frac_full',
        'BENEFIT_POS_FRAC_CTX': 'benefit_pos_frac_ctx',
        'BENEFIT_NEG_FRAC_FULL': 'benefit_neg_frac_full',
        'BENEFIT_NEG_FRAC_CTX': 'benefit_neg_frac_ctx',
        'MECHANISM_TOKEN': 'token_adopt_kw_p50',
        'MECHANISM_HIDDEN': 'hidden_adopt_kw_p50',
        'MECHANISM_SUBST': 'subst_adopt_kw_p50',
        'ROBUSTNESS_DV': 'CAR',
        'BOOTSTRAP_REPS': '999',  # F-R5-H1 wild cluster bootstrap
        'RANDOM_SEED': '20260516',  # F-R6-M2
        # V2.0 J-L-M 2026 alignment Round 9: P2.G4 external Y placeholders.
        # Actual column names depend on UA-2 data acquisition (Wind / 银保监 /
        # CSMAR); defaults below are sentinel names that allow template build to
        # succeed; Stata `capture confirm variable` falls through if absent.
        'EXT_Y1': 'ncd_spread_3m',           # NCD spread (predicted ↓)
        'EXT_Y2': 'regulatory_penalty_n',    # 监管处罚频次 (predicted ↓)
        'EXT_Y3': 'soa_rating_score',        # SOA / Wind rating (predicted ↑)
        # v3.7.3 Plan A v1.0: MAIN_TREAT alias for _title robustness template
        # (26_bs_title_robustness.do.tmpl). benefit_society main attitude = ATTITUDE_VAR.
        'MAIN_TREAT': 'benefit_mean_full',
    },
    'brokerage_network': {
        'PAPER_ID': 'brokerage_network',
        'MAIN_DV': 'ROA',
        'CONTROLS': 'ln_news_coverage media_hhi bank_scale_ord',
        'CLUSTER_VAR': 'prov_id',  # province-level per Cameron-Miller 2015
        'HET_VAR': 'is_soe',
        'MAIN_ENDOG': 'peer_tone_lag1_full',
        'MAIN_IV': 'peer_tone_2nd_lag1_full',
        'TREATMENT_DCEP': 'dcep_post',
        'TREATMENT_SANDBOX': 'sandbox_post',
        'CENTRALITY_BTW': 'bank_between_cent',
        'CENTRALITY_CONS': 'bank_constraint',
        'CENTRALITY_BROKER': 'brokerage_eigen_cent',
        # v3.7.3 Plan A v1.0: MAIN_TREAT + RANDOM_SEED for _title robustness template.
        'MAIN_TREAT': 'peer_tone_lag1_full',  # alias of MAIN_ENDOG
        'RANDOM_SEED': '20260516',
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
        # v3.7.3 Plan A v1.0: MAIN_TREAT + RANDOM_SEED for _title robustness template.
        'MAIN_TREAT': 'strat_diff_n5',  # alias of MAIN_DIFF_VAR
        'RANDOM_SEED': '20260516',
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
        # v3.7.3 Plan A v1.0: MAIN_TREAT + RANDOM_SEED for _title robustness template.
        'MAIN_TREAT': 'llm_vote_tone_full',  # alias of TONE_VAR
        'RANDOM_SEED': '20260516',
    },
    # ========================================================================
    # RR7-1 (Review-only audit): B-route 3 new paper defaults.
    # Source: paper_spec.yaml outcome.primary / treatment.primary / controls.
    # ========================================================================
    'bank_fintech_attention': {
        'PAPER_ID': 'bank_fintech_attention',
        'MAIN_DV': 'ln_fintech_investment',          # spec.outcome.primary (P2)
        'MAIN_TREAT': 'attention_index_full',        # spec.treatment.primary (P2)
        'CONTROLS': ('ln_assets leverage capital_ratio npl_ratio deposit_growth '
                     'gdp_growth m2_growth'),
        'CLUSTER_VAR': 'bank_id',
        'RANDOM_SEED': '20260516',
        'HET_VAR': 'bank_type',                       # per §B.2 heterogeneity (4 bank types)
    },
    'bank_fintech_substance': {
        'PAPER_ID': 'bank_fintech_substance',
        'MAIN_DV': 'long_run_roa_change_3yr',         # spec.outcome.primary (P3 long-run)
        'MAIN_TREAT': 'innovation_substantiveness_full',  # spec.treatment.primary (P3)
        'CONTROLS': ('ln_assets leverage capital_ratio npl_ratio deposit_growth '
                     'gdp_growth m2_growth'),
        'CLUSTER_VAR': 'bank_id',
        'RANDOM_SEED': '20260516',
        'HET_VAR': 'is_soe',                           # per §B.3 heterogeneity
    },
    'bank_fintech_locus': {
        'PAPER_ID': 'bank_fintech_locus',
        'MAIN_DV': 'car_5day_window',                 # spec.outcome.primary (P4)
        # P4 用 primary_pair = (locus_layer_full, locus_scenario_full), 15_locus_main
        # 直接 hardcode pair; MAIN_TREAT 留 locus_layer_full 作单 placeholder fallback
        # 给 16_mechanism 等用 single treatment 的 paper-specific templates.
        'MAIN_TREAT': 'locus_layer_full',
        'CONTROLS': ('ln_assets leverage capital_ratio npl_ratio deposit_growth '
                     'gdp_growth m2_growth'),
        'CLUSTER_VAR': 'bank_id',
        'RANDOM_SEED': '20260516',
        'HET_VAR': 'is_soe',                           # per §B.4 heterogeneity (wave + SOE)
    },
    # v3.4.0 epoch 4: P5 bank_fintech_collab (Chesbrough 2003 + L&S 2006 SMJ)
    'bank_fintech_collab': {
        'PAPER_ID': 'bank_fintech_collab',
        'MAIN_DV': 'm_and_a_fintech',                  # spec.outcome.primary (P5, M&A 直接 outcome)
        'MAIN_TREAT': 'innovation_collab_mode_full',   # spec.treatment.primary (P5, positive_class=外部协同)
        'CONTROLS': ('ln_assets leverage capital_ratio npl_ratio deposit_growth '
                     'gdp_growth m2_growth'),
        'CLUSTER_VAR': 'bank_id',
        'RANDOM_SEED': '20260516',
        'HET_VAR': 'bank_type',                        # 按银行类型异质性 (与 P2 一致)
    },
}


def get_paper_defaults(paper_id: str) -> dict[str, str]:
    """Return a shallow copy of the placeholder defaults for ``paper_id``."""
    if paper_id not in _DERIVATIVE_PAPER_IDS:
        raise ValueError(
            f"Unknown derivative paper_id={paper_id!r}. "
            f"Valid: {sorted(_DERIVATIVE_PAPER_IDS)}"
        )
    return dict(_PAPER_DEFAULTS[paper_id])


# ============================================================================
# Placeholder substitution (fail-fast on residue).
# ============================================================================

_PLACEHOLDER_RE = re.compile(r'\{\{([A-Z_]+)\}\}')


def _substitute(content: str, choices: Mapping[str, str]) -> str:
    """Replace {{KEY}} → value in content. Raises ValueError on residue."""
    result = content
    for key, value in choices.items():
        result = result.replace(f'{{{{{key}}}}}', str(value))
    leftover = _PLACEHOLDER_RE.findall(result)
    if leftover:
        raise ValueError(
            f"unsubstituted placeholders: {sorted(set(leftover))}. "
            f"choices keys: {sorted(choices.keys())}"
        )
    return result


# ============================================================================
# Replication package builder.
# ============================================================================

def build_derivative_replication_package(
    paper_id: str,
    overrides: Mapping[str, str] | None = None,
    output_root: str | Path | None = None,
    template_dir: str | Path | None = None,
) -> Path:
    """Generate a Stata replication package for a derivative paper.

    Args:
        paper_id:     One of {benefit_society, brokerage_network, strategic_diff, llm_peer}.
        overrides:    Optional dict overriding paper defaults (e.g., swap MAIN_DV='Tobin_Q').
                      Must use known placeholder keys (Tier 2 / Tier 3 per paper).
        output_root:  Parent dir for the package (default: news_process repo root).
        template_dir: Override template source dir. Default: stata_templates/<paper_id>/.

    Returns:
        Path to the generated package directory.

    Raises:
        ValueError:        Unknown paper_id, or unsubstituted {{...}} after merge.
        FileNotFoundError: Template dir does not exist.
    """
    if paper_id not in _DERIVATIVE_PAPER_IDS:
        raise ValueError(
            f"Unknown derivative paper_id={paper_id!r}. "
            f"Valid: {sorted(_DERIVATIVE_PAPER_IDS)}"
        )

    # Merge defaults + user overrides.
    effective: dict[str, str] = dict(_PAPER_DEFAULTS[paper_id])
    if overrides:
        bad = set(overrides.keys()) - set(effective.keys())
        if bad:
            raise ValueError(
                f"override keys {sorted(bad)} not in paper defaults "
                f"for {paper_id!r}; known: {sorted(effective.keys())}"
            )
        effective.update(overrides)

    if template_dir is None:
        template_dir = Path(__file__).resolve().parent / 'stata_templates' / paper_id
    template_dir = Path(template_dir)
    if not template_dir.is_dir():
        raise FileNotFoundError(f"Template dir not found: {template_dir}")

    if output_root is None:
        output_root = Path(__file__).resolve().parents[3]
    output_root = Path(output_root)

    pkg_dir = output_root / f'replication_v3.2.0_{paper_id}'
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / 'code').mkdir(exist_ok=True)
    (pkg_dir / 'data').mkdir(exist_ok=True)
    (pkg_dir / 'output' / 'tables').mkdir(parents=True, exist_ok=True)
    (pkg_dir / 'output' / 'figures').mkdir(parents=True, exist_ok=True)

    # Instantiate templates.
    n_templates = 0
    for tpl_path in sorted(template_dir.glob('*.do.tmpl')):
        out_name = tpl_path.stem  # strip .tmpl, e.g., 11_table2_main_iv_2sls.do
        out_path = pkg_dir / 'code' / out_name
        content = tpl_path.read_text(encoding='utf-8')
        out_path.write_text(_substitute(content, effective), encoding='utf-8')
        n_templates += 1

    # Copy README.md with paper-specific appendix.
    readme_src = template_dir / 'README.md'
    if readme_src.exists():
        commit_hash = _get_git_commit_hash_with_dirty()
        keys_used = sorted(effective.keys())
        appendix = (
            "\n\n---\n\n"
            "## This replication package / 本复现包\n\n"
            f"- **Generated at**: {commit_hash}\n"
            f"- **Paper**: `{paper_id}`\n"
            f"- **MAIN_DV**: `{effective.get('MAIN_DV', '?')}`\n"
            f"- **CLUSTER_VAR**: `{effective.get('CLUSTER_VAR', '?')}`\n"
            f"- **CONTROLS**: `{effective.get('CONTROLS', '?')}`\n"
            f"- **Placeholders bound** ({len(keys_used)}): {', '.join(keys_used)}\n"
            f"- **Templates instantiated**: {n_templates}\n"
            "- **Plan version**: v14 + P1 (2026-05-15 derivative-paper extension)\n"
        )
        (pkg_dir / 'README.md').write_text(
            readme_src.read_text(encoding='utf-8') + appendix,
            encoding='utf-8',
        )

    return pkg_dir


__all__ = [
    '_DERIVATIVE_PAPER_IDS',
    '_PAPER_DEFAULTS',
    'is_derivative_paper',
    'get_paper_defaults',
    'build_derivative_replication_package',
]
