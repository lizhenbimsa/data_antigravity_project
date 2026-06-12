"""news_process.papers._common.derivative_replication — 非主线论文的
Stata replication 包生成器。

P1 (2026-05-15): 与 ``stata_runner.build_replication_package`` 并行 (后者
锁定主线论文 ``bank_fintech_tone``)。本模块最初处理 4 篇衍生论文
(``benefit_society`` / ``brokerage_network`` / ``strategic_diff`` /
``llm_peer``); RR7-1 后又纳入 3 篇 B-route 论文 (attention / substance /
locus), 现共 7 个 paper id, 全程不触碰主线论文流程。

为什么独立成模块
---------------------
- ``stata_runner.build_replication_package`` 把主线三轨 triad
  (``MAIN_LOCUS_TRACK`` / ``MAIN_SUBST_TRACK`` / ``MAIN_SENT_TRACK``)
  作为必填项校验; 衍生论文没有这些轨道。
- 主线模板位于 ``stata_templates/*.do.tmpl``;
  衍生论文模板位于 ``stata_templates/<paper_id>/*.do.tmpl``。
- 保证主线代码路径 (及其当时的 73 个测试) 完全不受影响。

设计规则
------------
- 纯函数; 无全局状态。
- 复用 ``stata_runner._get_git_commit_hash_with_dirty`` 做 commit
  指纹 (该细节的单一可信源)。
- 占位符替换对残留 ``{{...}}`` fail-fast (与
  ``stata_runner._substitute_placeholders`` 同一纪律)。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Mapping

# Q1.4 (2026-05-15): commit-hash helper 抽到 _git_utils.py, 以打破
# _PAPER_DEFAULTS 单源化合并时引入的 stata_runner ↔ derivative_replication
# import 循环。
from news_process.papers._common._git_utils import _get_git_commit_hash_with_dirty

# ============================================================================
# 非主线 paper id 白名单 (4 衍生 + 3 B-route, 共 7) — 主线 bank_fintech_tone
# 刻意排除在外; bank_fintech_collab 因 P5 onboarding 未完成 (缺 derivative
# 注册, 见 paper_registry.PAPER_IDS_PROVISIONAL 注) 暂不在此, 待独立 PR 接线。
# ============================================================================

_DERIVATIVE_PAPER_IDS: frozenset[str] = frozenset({
    'benefit_society',
    'brokerage_network',
    'strategic_diff',
    'llm_peer',
    # RR7-1 (Review-only audit): B-route 3 篇新论文复用与 4 篇衍生论文相同的
    # per-paper replication 路径。命名保留 "_DERIVATIVE_*" 以向后兼容
    # (语义上它指 "由 per-paper 模板实例化处理的非主线 paper id";
    # 历史上 "bank_fintech_tone 的衍生" 这一框架已被 B-route 计划取代)。
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
    """当且仅当 paper_id 属于 _DERIVATIVE_PAPER_IDS (7 个非主线 id) 时为 True。"""
    return paper_id in _DERIVATIVE_PAPER_IDS


# ============================================================================
# 各 paper 的占位符默认值 (Tier 2 通用 + Tier 3 paper-specific)。
# ============================================================================

_PAPER_DEFAULTS: dict[str, dict[str, str]] = {
    # fix(omni-g-replication-01, 2026-06-11): MAIN_DV='ROA' (及 benefit 的
    # ROBUSTNESS_DV='CAR' / HET_VAR='is_listed') 是外部财务数据 sentinel — 当前
    # bank-year panel (40_panel_yearly) 无任何 roa/car/is_listed 列, 数据源为
    # config/银行面板2007-2025年.xlsx (待接入)。按裁决保留列名不改; 各 paper 的
    # 01_data_prep 模板对缺失财务列给出明确 [ERROR]/[WARN] 指引, 00_master 对
    # 01 失败 fail-loud 带可读原因 (而非裸 r(198))。CLUSTER_VAR bank_id / prov_id
    # 非幻影: 每个 01_data_prep 均由 panel 真实列 encode 派生 (target_bank /
    # bank_province)。
    'benefit_society': {
        'PAPER_ID': 'benefit_society',
        'MAIN_DV': 'ROA',  # external sentinel — 见上方 fix(omni-g-replication-01) 注
        'CONTROLS': 'ln_news_coverage media_breadth n_articles',
        'CLUSTER_VAR': 'bank_id',
        'HET_VAR': 'is_listed',  # PAP v1.0-final DP-9: 取代 is_soe (F-R3-H2); external sentinel
        # v3.2.1 dual-track (plan v2.12, F-M1 / F-H3): ATTITUDE_VAR 保留为
        # 向后兼容别名 = full 轨; ATTITUDE_FULL / ATTITUDE_CTX 才是新模板
        # 使用的规范双轨占位符
        # (20_tableA1_inter_track_kappa, 21_tableA2_attitude_track_switch,
        # 31_figure2_coefplot_dual, 17b_table8b_shrinkage_dual)。
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
        'ROBUSTNESS_DV': 'CAR',  # external sentinel — 见上方 fix(omni-g-replication-01) 注
        'BOOTSTRAP_REPS': '999',  # F-R5-H1 wild cluster bootstrap
        'RANDOM_SEED': '20260516',  # F-R6-M2
        # V2.0 J-L-M 2026 对齐 Round 9: P2.G4 外部 Y 占位符。
        # 实际列名取决于 UA-2 数据获取 (Wind / 银保监 / CSMAR); 下方默认值
        # 是 sentinel 名, 仅保证模板能 build 成功; 列缺失时 Stata
        # `capture confirm variable` 安全跳过。
        'EXT_Y1': 'ncd_spread_3m',           # NCD 利差 (预期 ↓)
        'EXT_Y2': 'regulatory_penalty_n',    # 监管处罚频次 (预期 ↓)
        'EXT_Y3': 'soa_rating_score',        # SOA / Wind 评级 (预期 ↑)
        # MAIN_TREAT 别名保留为 benefit_society 主态度变量 = ATTITUDE_VAR
        # (benefit_mean_full)。注意: benefit_society 的 .do 模板消费的是
        # ATTITUDE_* 命名空间而非 {{MAIN_TREAT}}; 其唯一消费者 (_title
        # robustness 模板) 已随 remove-title-track 重构删除, 此别名现为
        # 无害闲置默认值。
        'MAIN_TREAT': 'benefit_mean_full',
    },
    'brokerage_network': {
        'PAPER_ID': 'brokerage_network',
        'MAIN_DV': 'ROA',  # external sentinel — 见 benefit_society 块上方 fix(omni-g-replication-01) 注
        'CONTROLS': 'ln_news_coverage media_hhi bank_scale_ord',
        'CLUSTER_VAR': 'prov_id',  # 省级聚类, 依 Cameron-Miller 2015
        'HET_VAR': 'is_soe',
        'MAIN_ENDOG': 'peer_tone_lag1_full',
        'MAIN_IV': 'peer_tone_2nd_lag1_full',
        'TREATMENT_DCEP': 'dcep_post',
        'TREATMENT_SANDBOX': 'sandbox_post',
        'CENTRALITY_BTW': 'bank_between_cent',
        'CENTRALITY_CONS': 'bank_constraint',
        'CENTRALITY_BROKER': 'brokerage_eigen_cent',
        # 残留默认值: MAIN_TREAT/RANDOM_SEED 原供已删的 _title robustness 模板
        # (25_tableA8_title_robustness, remove-title-track 已删) 使用; 现
        # brokerage_network 无存活模板消费此二 placeholder, 保留为无害默认值。
        'MAIN_TREAT': 'peer_tone_lag1_full',  # MAIN_ENDOG 的别名
        'RANDOM_SEED': '20260516',
    },
    'strategic_diff': {
        'PAPER_ID': 'strategic_diff',
        # 2026-06-13 outcome 重定位 (顶刊组合定稿): 差异化 → 市场势力 → 特许权价值
        # (Hoberg-Phillips 2016 JPE 银行版; Keeley 1990 AER charter value)。tobin_q
        # 仍为外部财务 sentinel (上市行子样本, 财务面板+市值接入前列缺失,
        # 01_data_prep capture confirm 安全跳过), 性质同原 'ROA' 哨兵。
        'MAIN_DV': 'tobin_q',  # spec.outcome.primary (external sentinel, 上市行)
        'CONTROLS': 'ln_news_coverage media_hhi bank_scale_ord',
        'CLUSTER_VAR': 'bank_id',
        'HET_VAR': 'is_soe',
        'MAIN_DIFF_VAR': 'strat_diff_n5',
        'FLUIDITY_VAR': 'strat_fluidity',
        'SIM_MAX_VAR': 'strat_sim_max',
        'BARTIK_IV': 'bartik_type_iv_full',
        'TONE_VAR': 'llm_vote_tone_full',
        'COHERENCE_VAR': 'coh_tfidf_c_full',
        # MAIN_TREAT/RANDOM_SEED: 原为 v3.7.3 Plan A _title robustness 模板
        # (strategic_diff/25_tableA8_title_robustness.do.tmpl) 而加; 该 _title 情感轨
        # 模板已随 remove-title-track 删除, 现 strategic_diff 无模板引用这两个
        # placeholder, 保留为无害 unused default (无测试依赖, _substitute 不报错)。
        'MAIN_TREAT': 'strat_diff_n5',  # MAIN_DIFF_VAR 的别名
        'RANDOM_SEED': '20260516',
    },
    'llm_peer': {
        'PAPER_ID': 'llm_peer',
        # 2026-06-13 主规格重构 (顶刊组合定稿): outcome 改为银行自身 fintech 报道
        # 强度年度聚合 (panel 真实在产列, encode.py:847) — 方法学论文用 "peer-IV →
        # own tone → own fintech 战略响应" (Leary-Roberts 2014 JF 同群范式) 最大化
        # 展示 LLM 语义同业尺子; 不再用外部财务 sentinel 'ROA' (roa 降级 secondary)。
        'MAIN_DV': 'avg_ft_intensity_full',  # spec.outcome.primary (panel 实存列)
        'CONTROLS': 'ln_news_coverage media_hhi n_articles',
        'CLUSTER_VAR': 'bank_id',
        'HET_VAR': 'is_soe',
        'TONE_VAR': 'llm_vote_tone_full',
        'LLM_PEER_IV': 'llm_peer_tone_iv_full',
        'LLM_PEER_COVERAGE_IV': 'llm_peer_coverage_iv',
        'COMPETE_IDX': 'peer_compete_idx',
        # disclosure(omni-g-llm-peer-05, 2026-06-11): cutoff 五档列结构性逐位
        # 相同 — cutoff 原仅作用于 llm_peer_iv 已移除的 difflib 兜底, 策略 1-3
        # 与之无关 (盘上实证: 五档 nonnull/mean 全同)。该 '灵敏度电池' 无识别
        # 变差, 论文表注必须如实披露 (详见 pipeline/panel/llm_peer_iv.py 步骤 5)。
        'CUTOFF_VARS': ('llm_peer_tone_iv_full_70 llm_peer_tone_iv_full_75 '
                        'llm_peer_tone_iv_full_80 llm_peer_tone_iv_full_85 '
                        'llm_peer_tone_iv_full_90'),
        # MAIN_TREAT (alias of TONE_VAR) + RANDOM_SEED: 原供已删的 _title robustness
        # 模板 (llm_peer/25_tableA8_title_robustness.do.tmpl, remove-title-track 已删)
        # 使用; 现 llm_peer 无存活模板消费此二 placeholder, 保留为无害默认值。
        'MAIN_TREAT': 'llm_vote_tone_full',  # TONE_VAR 的别名
        'RANDOM_SEED': '20260516',
    },
    # ========================================================================
    # RR7-1 (Review-only audit): B-route 3 篇新论文的默认值。
    # 来源: paper_spec.yaml 的 outcome.primary / treatment.primary / controls。
    # ========================================================================
    # fix(omni-g-replication-05, 2026-06-11): 4 篇 B-route CONTROLS 去掉
    # gdp_growth/m2_growth — 15_* 主回归 M5 设计为 "M4 + macro" 并显式追加
    # `$controls gdp_growth m2_growth`; 旧默认值已含两宏观列 → reghdfe 重复
    # regressor 被静默 omit, M5 ≡ M4 (M1→M6 渐进设计名存实亡)。现 M4 = bank-level
    # only, M5 真增量。bank-level 5 列亦为外部财务 sentinel (见 fix(omni-g-replication-01)
    # 注), 01_data_prep 以 capture confirm 自校验拼装 $controls。
    'bank_fintech_attention': {
        'PAPER_ID': 'bank_fintech_attention',
        'MAIN_DV': 'ln_fintech_investment',          # spec.outcome.primary (P2)
        'MAIN_TREAT': 'attention_index_full',        # spec.treatment.primary (P2)
        'CONTROLS': 'ln_assets leverage capital_ratio npl_ratio deposit_growth',
        'CLUSTER_VAR': 'bank_id',
        'RANDOM_SEED': '20260516',
        'HET_VAR': 'bank_type',                       # 依 §B.2 异质性 (4 类银行)
    },
    'bank_fintech_substance': {
        'PAPER_ID': 'bank_fintech_substance',
        # 2026-06-13 outcome 重定位: 效率试金石 (W&Z decoupling — 实质性采纳应改善
        # 成本收入比, 象征性宣告应无效); long_run_roa_change_3yr 降级 secondary。
        'MAIN_DV': 'cost_income_ratio_change_3yr',    # spec.outcome.primary (P3, 3 年前向 CIR 变化)
        # fix(omni-g-replication-04, 2026-06-11): 原 'innovation_substantiveness_full'
        # 是 stage 21 article-level 列, 永不在 bank-year panel (stage 45 聚合真名 =
        # sub_frac/symb_frac) → 01_data_prep exit 198 全包死亡。改为 panel 真实聚合列
        # sub_frac (实质性文章占比, 连续测度; 与 spec.treatment.primary 同步,
        # spec 侧同次修于 omni-g-papers-misc-11)。
        'MAIN_TREAT': 'sub_frac',                     # spec.treatment.primary (P3, panel 聚合列)
        'CONTROLS': 'ln_assets leverage capital_ratio npl_ratio deposit_growth',  # fix(omni-g-replication-05): 去 macro, M5 真增量
        'CLUSTER_VAR': 'bank_id',
        'RANDOM_SEED': '20260516',
        'HET_VAR': 'is_soe',                           # 依 §B.3 异质性
    },
    'bank_fintech_locus': {
        'PAPER_ID': 'bank_fintech_locus',
        # 2026-06-13 outcome 重定位 (年度数据约束): 事件窗 CAR 需日频 → 降级上市行
        # 扩展; 主 outcome = 引用加权专利 (Kogan 2017 QJE 谱系, 底层技术轨直接产出)。
        'MAIN_DV': 'citation_weighted_patent',        # spec.outcome.primary (P4)
        # P4 用 primary_pair = (locus_layer_full, locus_scenario_full), 15_locus_main
        # 直接 hardcode pair; MAIN_TREAT 留 locus_layer_full 作单 placeholder fallback
        # 给 16_mechanism 等用 single treatment 的 paper-specific 模板。
        'MAIN_TREAT': 'locus_layer_full',
        'CONTROLS': 'ln_assets leverage capital_ratio npl_ratio deposit_growth',  # fix(omni-g-replication-05): 去 macro, M5 真增量
        'CLUSTER_VAR': 'bank_id',
        'RANDOM_SEED': '20260516',
        'HET_VAR': 'is_soe',                           # 依 §B.4 异质性 (wave + SOE)
    },
    # v3.4.0 epoch 4: P5 bank_fintech_collab (Chesbrough 2003 + L&S 2006 SMJ)
    'bank_fintech_collab': {
        'PAPER_ID': 'bank_fintech_collab',
        'MAIN_DV': 'm_and_a_fintech',                  # spec.outcome.primary (P5, M&A 直接 outcome)
        # fix(omni-g-replication-04, 2026-06-11): 原 'innovation_collab_mode_full'
        # 是 article-level 列 (panel 聚合真名 = collab_frac/indep_frac) →
        # 01_data_prep exit 198 全包死亡。改为 panel 真实聚合列 collab_frac (外部协同
        # 文章占比; 与 spec.treatment.primary 同步, spec 侧同次修于 omni-g-papers-misc-11)。
        # 15_collab 的 binary pair (collab_open/closed_full) 由 01_data_prep 照 locus
        # R35-M02 模式从 collab_frac/indep_frac 派生 (同修 omni-g-replication-06 的
        # missing→both-0 / open+closed≡1 共线缺陷)。
        'MAIN_TREAT': 'collab_frac',                   # spec.treatment.primary (P5, panel 聚合列)
        'CONTROLS': 'ln_assets leverage capital_ratio npl_ratio deposit_growth',  # fix(omni-g-replication-05): 去 macro, M5 真增量
        'CLUSTER_VAR': 'bank_id',
        'RANDOM_SEED': '20260516',
        'HET_VAR': 'bank_type',                        # 按银行类型异质性 (与 P2 一致)
    },
}


def get_paper_defaults(paper_id: str) -> dict[str, str]:
    """返回 ``paper_id`` 占位符默认值字典的浅拷贝。"""
    if paper_id not in _DERIVATIVE_PAPER_IDS:
        raise ValueError(
            f"Unknown derivative paper_id={paper_id!r}. "
            f"Valid: {sorted(_DERIVATIVE_PAPER_IDS)}"
        )
    return dict(_PAPER_DEFAULTS[paper_id])


# ============================================================================
# 占位符替换 (残留即 fail-fast)。
# ============================================================================

_PLACEHOLDER_RE = re.compile(r'\{\{([A-Z_]+)\}\}')


def _substitute(content: str, choices: Mapping[str, str]) -> str:
    """把 content 中的 {{KEY}} → value 逐个替换; 有残留占位符即抛 ValueError。"""
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
# Replication 包构建器。
# ============================================================================

def build_derivative_replication_package(
    paper_id: str,
    overrides: Mapping[str, str] | None = None,
    output_root: str | Path | None = None,
    template_dir: str | Path | None = None,
) -> Path:
    """为一篇非主线论文生成 Stata replication 包。

    Args:
        paper_id:     _DERIVATIVE_PAPER_IDS 之一 (4 衍生: benefit_society /
                      brokerage_network / strategic_diff / llm_peer + 3 B-route:
                      bank_fintech_attention / substance / locus)。
        overrides:    可选, 覆盖 paper 默认值的字典 (如换 MAIN_DV='Tobin_Q')。
                      key 必须是该 paper 已知占位符 (Tier 2 / Tier 3)。
        output_root:  包的父目录 (默认: news_process 仓库根)。
        template_dir: 覆盖模板源目录。默认: stata_templates/<paper_id>/。

    Returns:
        生成的包目录路径。

    Raises:
        ValueError:        未知 paper_id, 或合并后仍有未替换的 {{...}}。
        FileNotFoundError: 模板目录不存在。
    """
    if paper_id not in _DERIVATIVE_PAPER_IDS:
        raise ValueError(
            f"Unknown derivative paper_id={paper_id!r}. "
            f"Valid: {sorted(_DERIVATIVE_PAPER_IDS)}"
        )

    # 合并: 默认值 + 用户覆盖。
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

    # 实例化模板。
    n_templates = 0
    for tpl_path in sorted(template_dir.glob('*.do.tmpl')):
        out_name = tpl_path.stem  # 去掉 .tmpl 后缀, 如 11_table2_main_iv_2sls.do
        out_path = pkg_dir / 'code' / out_name
        content = tpl_path.read_text(encoding='utf-8')
        out_path.write_text(_substitute(content, effective), encoding='utf-8')
        n_templates += 1

    # 复制 README.md 并追加 paper-specific 附录。
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
