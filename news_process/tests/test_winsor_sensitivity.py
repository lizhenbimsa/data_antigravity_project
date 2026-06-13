"""缩尾敏感性 (winsorization-sensitivity) 稳健性接线守卫 (2026-06-13).

背景: 7 篇注册论文在 robustness 表新增 winsorization-sensitivity 模型 (wsens_*),
口径为主回归在 raw / 1% / 5% 缩尾下并排, 配套 01_data_prep 增 _w5 档。

本测试锁定两条容易"看着成功实则失败"的红线:
  1. (MF9) 每个被 `eststo` 的 wsens_* 模型, 必须同时出现在该表的动态输出过滤名单
     (cohort-A 的 `local cand_models` / strategic_diff 的显式 esttab / cohort-B 的
     `inlist(...)`) 中 — 否则模型会跑但被静默剔除出输出表, 且无其他测试可捕获。
  2. 每篇 01_data_prep 必须保留原 1% 缩尾行 (winsor) 且新增 5% 档 (_w5) — 不得以
     替换方式删除原行 (test_derivative_replication 依赖 'winsor' 子串)。

纯模板层断言 (读 .do.tmpl 文本), 不实例化、不跑 Stata、不触 Python 面板/golden。
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

_STATA_DIR = Path(__file__).resolve().parents[1] / "papers" / "_common" / "stata_templates"

# paper_id -> robustness 模板文件名 (cohort A 用 14_table5; cohort B 用 18_*)
_ROBUSTNESS_FILE = {
    "benefit_society": "14_table5_robustness.do.tmpl",
    "brokerage_network": "14_table5_robustness.do.tmpl",
    "llm_peer": "14_table5_robustness.do.tmpl",
    "strategic_diff": "14_table5_robustness.do.tmpl",
    "bank_fintech_attention": "18_attention_robustness.do.tmpl",
    "bank_fintech_substance": "18_substance_robustness.do.tmpl",
    "bank_fintech_locus": "18_locus_robustness.do.tmpl",
}

_ALL_PAPERS = sorted(_ROBUSTNESS_FILE)


def _read(paper: str, fname: str) -> str:
    path = _STATA_DIR / paper / fname
    assert path.exists(), f"{paper}/{fname} 不存在: {path}"
    return path.read_text(encoding="utf-8")


def _filter_region(text: str) -> str:
    """提取决定哪些模型进输出表的'白名单'相关文本行。

    包括: `local cand_models ...` / `inlist(...)` / 显式点名 wsens 的 esttab 行。
    新 eststo 名若不在这些行内 → 静默掉列 (MF9)。
    """
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if (
            s.startswith("local cand_models")
            or "inlist(" in s
            or (s.startswith("esttab ") and "wsens" in s)
        ):
            lines.append(ln)
    return "\n".join(lines)


@pytest.mark.parametrize("paper", _ALL_PAPERS)
def test_wsens_models_are_in_output_filter(paper: str) -> None:
    """MF9: 每个 eststo 的 wsens_* 模型必须出现在输出过滤名单中 (防静默掉列)。"""
    text = _read(paper, _ROBUSTNESS_FILE[paper])
    eststo_names = set(re.findall(r"eststo\s+(wsens_\w+)", text))
    assert eststo_names, f"{paper}: robustness 表未找到任何 eststo wsens_* 缩尾敏感性模型"

    region = _filter_region(text)
    for name in sorted(eststo_names):
        assert name in region, (
            f"{paper}: 模型 {name} 被 eststo 但未进输出过滤名单 "
            f"(cand_models / inlist / esttab) → 会静默掉列 (MF9)"
        )


@pytest.mark.parametrize("paper", _ALL_PAPERS)
def test_data_prep_keeps_w1_and_adds_w5(paper: str) -> None:
    """01_data_prep 保留 1% 缩尾且新增 5% 档 _w5。"""
    text = _read(paper, "01_data_prep.do.tmpl")
    assert "winsor" in text.lower(), f"{paper}: 01_data_prep 丢失原 winsor 行 (项目约定)"
    assert "cuts(1 99)" in text, f"{paper}: 01_data_prep 缺 1% 缩尾基准 cuts(1 99)"
    has_w5 = "suffix(_w5)" in text or "{{MAIN_DV}}_w5" in text
    assert has_w5, f"{paper}: 01_data_prep 缺 5% 缩尾敏感性档 _w5"


@pytest.mark.parametrize("paper", _ALL_PAPERS)
def test_wsens_uses_main_dv_suffixed(paper: str) -> None:
    """wsens 回归须切换 DV 缩尾力度 (引用 {{MAIN_DV}}_w / _w5 / raw {{MAIN_DV}})。"""
    text = _read(paper, _ROBUSTNESS_FILE[paper])
    assert "{{MAIN_DV}}_w5" in text, f"{paper}: robustness 表未引用 5% 缩尾列 {{{{MAIN_DV}}}}_w5"


def test_cohort_a_table1_describes_winsorized_dv() -> None:
    """P0-3: cohort-A 4 篇 Table 1 描述统计报告缩尾后 DV ({{MAIN_DV}}_w), 与回归同口径。"""
    for paper in ("benefit_society", "brokerage_network", "llm_peer", "strategic_diff"):
        text = _read(paper, "10_table1_descriptives.do.tmpl")
        assert "{{MAIN_DV}}_w" in text, (
            f"{paper}: Table 1 描述统计未对齐缩尾后 DV {{{{MAIN_DV}}}}_w (P0-3 口径一致)"
        )
