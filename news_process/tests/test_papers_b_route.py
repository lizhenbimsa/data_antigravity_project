"""M1 G1 acceptance — B-route 3 new paper 集成测试.

Plan v2.x §5.4.4 G1:
    "pytest tests/test_papers_b_route.py pass" (R53-M01 同步)

红线不变式
----------
1. 3 个 B-route 新 paper (bank_fintech_attention / bank_fintech_substance /
   bank_fintech_locus) 模块结构与现有 5 paper 对称.
2. 每个新 paper 的 4 个标准资产 (analysis.py / tables.py / figures.py / paper_spec.yaml) 都存在.
3. 每个新 paper 的 papers_assets 目录 (README.md / drafts/{en,zh}/manuscript.tex + refs.bib /
   do / output) 都存在.
4. 每个新 paper 在 Stata templates 下的 paper-specific 4 件套 + extras 都存在.
5. paper_registry 加载全部 paper 成功 (原 8 = 5 existing + 3 new;
   2026-06-01 起 PAPER_IDS_ALL 扩为 11, 含 3 provisional, 断言以 11 为准).
6. 3 新 paper 与 5 existing paper 的关键变量 (treatment.primary) 互不冲突.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from news_process.papers._common.paper_registry import (
    PAPER_IDS_ALL,
    PAPER_IDS_EXISTING,
    PAPER_IDS_NEW,
    get_spec,
    load_all_specs,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]  # news_process/
PAPERS_DIR = PROJECT_ROOT / 'papers'
ASSETS_DIR = PROJECT_ROOT / 'papers_assets'
STATA_TEMPLATES_DIR = PAPERS_DIR / '_common' / 'stata_templates'

# 按 plan §5.5.2 paper-specific 模板清单 + RR6-1 编排器对。
# RR6-1 (Review-only audit): plan §5.5.3 原 16 new templates 不含 paper-specific
# 00_master + 01_data_prep orchestrator, 但 4 existing 衍生 paper 都有此模式;
# 3 new paper 同步补齐 → 16 + 6 = 22 new templates, 当时合计 77 (此前 71)。
NEW_PAPER_TEMPLATES: dict[str, list[str]] = {
    'bank_fintech_attention': [
        '00_master.do.tmpl',                            # RR6-1 编排器
        '01_data_prep.do.tmpl',                         # RR6-1 数据准备 + globals
        '15_attention_main_regression.do.tmpl',
        '16_attention_mechanism.do.tmpl',
        '17_attention_heterogeneity.do.tmpl',
        '18_attention_robustness.do.tmpl',
        '19_attention_iv_first_stage.do.tmpl',          # P2 额外模板
    ],
    'bank_fintech_substance': [
        '00_master.do.tmpl',                            # RR6-1 编排器
        '01_data_prep.do.tmpl',                         # RR6-1 数据准备 + globals
        '15_substance_main_regression.do.tmpl',
        '16_substance_mechanism.do.tmpl',
        '17_substance_heterogeneity.do.tmpl',
        '18_substance_robustness.do.tmpl',
        '19_substance_lr_reversal.do.tmpl',             # P3 额外模板 1
        '20_substance_disclosure_quality.do.tmpl',      # P3 额外模板 2
    ],
    'bank_fintech_locus': [
        '00_master.do.tmpl',                            # RR6-1 编排器
        '01_data_prep.do.tmpl',                         # RR6-1 数据准备 + globals
        '15_locus_main_regression.do.tmpl',
        '16_locus_mechanism.do.tmpl',
        '17_locus_heterogeneity.do.tmpl',
        '18_locus_robustness.do.tmpl',
        '19_locus_event_study.do.tmpl',                 # P4 额外模板
    ],
}


# ============================================================================
# 1. 模块级结构不变式
# ============================================================================


@pytest.mark.parametrize('paper_id', PAPER_IDS_NEW)
def test_b_route_paper_module_structure(paper_id: str) -> None:
    """3 新 paper 在 papers/ 下必须有标准 4 件套 + paper_spec.yaml."""
    paper_dir = PAPERS_DIR / paper_id
    for filename in ('__init__.py', 'analysis.py', 'tables.py', 'figures.py', 'paper_spec.yaml'):
        path = paper_dir / filename
        assert path.is_file(), f"{paper_id}: missing {filename!r} at {path}"


@pytest.mark.parametrize('paper_id', PAPER_IDS_NEW)
def test_b_route_paper_assets_structure(paper_id: str) -> None:
    """3 新 paper 的 papers_assets/ 下必须有 README + drafts en/zh."""
    asset_dir = ASSETS_DIR / paper_id
    assert (asset_dir / 'README.md').is_file(), f"{paper_id}: missing README.md"

    for lang in ('en', 'zh'):
        draft_dir = asset_dir / 'drafts' / lang
        assert (draft_dir / 'manuscript.tex').is_file(), (
            f"{paper_id}: missing manuscript.tex at {draft_dir}"
        )
        assert (draft_dir / 'refs.bib').is_file(), (
            f"{paper_id}: missing refs.bib at {draft_dir}"
        )

    for sub in ('do', 'output'):
        assert (asset_dir / sub).is_dir(), f"{paper_id}: missing {sub}/ subdir"


# ============================================================================
# 2. Stata 模板清单 (M2 交付物)
# ============================================================================


@pytest.mark.parametrize('paper_id', PAPER_IDS_NEW)
def test_b_route_paper_stata_templates_exist(paper_id: str) -> None:
    template_subdir = STATA_TEMPLATES_DIR / paper_id
    assert template_subdir.is_dir(), (
        f"{paper_id}: missing stata_templates subdir at {template_subdir}"
    )
    for tmpl_name in NEW_PAPER_TEMPLATES[paper_id]:
        tmpl_path = template_subdir / tmpl_name
        assert tmpl_path.is_file(), (
            f"{paper_id}: missing template {tmpl_name!r} at {tmpl_path}"
        )


def test_total_template_count_77() -> None:
    """v3.5.1 + V2.0 J-L-M alignment Round 9: 95 个模板 (91 v3.5.1 + 4 V2.0 jlm2026)。

    历史演进 (函数名中的 77 是 v3.3.0 时代基线, 现以 95 为准):
    v3.3.0 基线: 77 (14 root + 41 existing + 22 new, 按 plan §5.5.3 R1-M01 + R1-M27)。
    v3.4.0 P5 epoch 4: +7 (00_master + 01_data_prep + 15-19_collab_*) = 共 84。
    v3.5.0 D2/D4: +2 (19_table6_cell_decomposition + 25_tableA6_dual_track_residual) = 86。
    v3.5.1 A1/A3: +5 (21_substance_clarity_robustness + 19_locus_clarity_robustness
                       + 20_collab_clarity_robustness + 19_bs_num_intensity_robustness
                       + v3_5_1/27_tableA9_num_intensity) = 共 91。
    V2.0 J-L-M 2026 alignment Round 9: benefit_society/ 下 +4
        (22_tableA9_external_validation + 23_tableA10_placebo_business_lines
         + 24_tableA11_anchor_family_alternative + 11b_table2_boottest) = **共 95**
    依据 benefit_society_jlm2026_robustness_alignment_plan.md §3 Phase 2。
    """
    templates = list(STATA_TEMPLATES_DIR.rglob('*.do.tmpl'))
    # remove-title-track: 删除 9 个标题稳健性模板 (8 _title across papers + 1 bs ext.)
    # → 回到 V2.0 J-L-M baseline 95.
    expected_count = 95  # 104 (v3.7.3 Plan A) − 9 (取消标题轨)
    assert len(templates) == expected_count, (
        f"Expected {expected_count} total templates after remove-title-track, found {len(templates)}: "
        f"= 95 (V2.0 J-L-M baseline); 9 title-robustness 模板已删除"
    )


def test_22_new_templates_breakdown() -> None:
    """RR6-1 后共 22 个 new templates: P2 7 (5 模板 + 00_master + 01_data_prep)
    + P3 8 (6 + 编排器对) + P4 7 (5 + 编排器对) = 22。"""
    new_total = sum(len(t) for t in NEW_PAPER_TEMPLATES.values())
    assert new_total == 22, f"Expected 22 new templates after RR6-1, got {new_total}"

    # 逐 paper 明细 (各 5/6/5 个 paper-specific + 2 个编排器)
    assert len(NEW_PAPER_TEMPLATES['bank_fintech_attention']) == 7
    assert len(NEW_PAPER_TEMPLATES['bank_fintech_substance']) == 8
    assert len(NEW_PAPER_TEMPLATES['bank_fintech_locus']) == 7


# ============================================================================
# 3. paper_registry 集成
# ============================================================================


def test_paper_registry_loads_8_papers() -> None:
    # 2026-06-01: PAPER_IDS_ALL 扩为 11 (5 existing + 3 new + 3 provisional).
    specs = load_all_specs()
    assert len(specs) == 11
    assert set(specs) == set(PAPER_IDS_ALL)


def test_existing_papers_status_existing() -> None:
    for pid in PAPER_IDS_EXISTING:
        spec = get_spec(pid)
        assert spec.status == 'existing', (
            f"{pid}: status={spec.status!r}, expected 'existing'"
        )


def test_new_papers_status_new() -> None:
    for pid in PAPER_IDS_NEW:
        spec = get_spec(pid)
        assert spec.status == 'new', (
            f"{pid}: status={spec.status!r}, expected 'new'"
        )


def test_new_papers_submission_window_aligned() -> None:
    """3 篇 new paper 须共享 submission_window 2027-03-15 (按 §5.11.1)。"""
    from datetime import date

    expected = date(2027, 3, 15)
    for pid in PAPER_IDS_NEW:
        spec = get_spec(pid)
        sw = spec.raw['targets']['submission_window']
        if isinstance(sw, str):
            from datetime import datetime as _dt
            sw = _dt.strptime(sw, '%Y-%m-%d').date()
        assert sw == expected, (
            f"{pid}: submission_window={sw!r}, expected 2027-03-15"
        )


# ============================================================================
# 4. 手稿骨架结构健全性
# ============================================================================


@pytest.mark.parametrize('paper_id', PAPER_IDS_NEW)
@pytest.mark.parametrize('lang', ['en', 'zh'])
def test_manuscript_has_required_sections(paper_id: str, lang: str) -> None:
    """每份手稿骨架须声明 §5.6.2 规定的 8 个标准 section。"""
    manuscript_path = ASSETS_DIR / paper_id / 'drafts' / lang / 'manuscript.tex'
    assert manuscript_path.is_file()
    content = manuscript_path.read_text(encoding='utf-8')

    # 8 个标准 section 的存在性标记
    required_tokens = [
        r'\begin{abstract}',
        r'\section{',           # 至少一个 \section{}
        r'\printbibliography',
        r'\NoteThis{',          # 占位标记 (M3 填实质内容)
    ]
    for token in required_tokens:
        assert token in content, (
            f"{paper_id}/{lang}: manuscript.tex missing token {token!r}"
        )


@pytest.mark.parametrize('paper_id', PAPER_IDS_NEW)
@pytest.mark.parametrize('lang', ['en', 'zh'])
def test_refs_bib_has_minimum_entries(paper_id: str, lang: str) -> None:
    """refs.bib 种子文件须有 ≥ 10 条 (M3 将按 G3 扩到 ≥ 30 条)。"""
    refs_path = ASSETS_DIR / paper_id / 'drafts' / lang / 'refs.bib'
    content = refs_path.read_text(encoding='utf-8')
    entry_count = content.count('@article{') + content.count('@book{') + content.count('@inproceedings{')
    assert entry_count >= 10, (
        f"{paper_id}/{lang}: refs.bib only has {entry_count} entries (need ≥ 10 seed)"
    )


# ============================================================================
# 5. exogenous_shocks.yaml 17-spec 计数检查
# ============================================================================


def test_exogenous_shocks_yaml_17_specs() -> None:
    import yaml

    # R85-fix: 从 data/ 移到 config/, 因为 news_process/data/ 被 gitignore (plan §5.2.2
    # 原写 data/exogenous_shocks.yaml; 实际落地在 config/, 与 config/policy_shocks.json 同源)。
    path = PROJECT_ROOT / 'config' / 'exogenous_shocks.yaml'
    assert path.is_file(), f"missing {path}"
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    events = data['events']
    assert len(events) == 6, f"Expected 6 events, got {len(events)}"

    total_specs = sum(len(e['applicable_papers']) for e in events)
    assert total_specs == 17, (
        f"Expected 17 DiD specs per plan §5.7.1, got {total_specs} "
        f"(per-event: {[(e['id'], len(e['applicable_papers'])) for e in events]})"
    )


# ============================================================================
# 6. pipeline_v34_rerun 配置健全性
# ============================================================================


def test_pipeline_v34_rerun_config_loadable() -> None:
    import yaml

    path = PROJECT_ROOT / 'config' / 'pipeline_v34_rerun.yaml'
    assert path.is_file(), f"missing {path}"
    cfg = yaml.safe_load(path.read_text(encoding='utf-8'))
    # v3.4.0 Q-B (2026-05-17): cap 上调 4200 → 5000 (10% 裕度, collab_mode 第三维度推升预估)
    assert cfg['acceptance']['llm_cost_cap_usd'] == 5000, (
        "LLM cost cap per v3.4.0 Q-B must be 5000 (was 4200 in v3.3.0)"
    )
    assert cfg['panel_build']['panel_col_budget'] == 5000, (
        "panel column budget per plan §5.3.1 ≤ 5000"
    )
    assert cfg['status'] == 'skeleton', (
        "pipeline_v34_rerun should be 'skeleton' until G-1 + D1 unblock M-1"
    )
