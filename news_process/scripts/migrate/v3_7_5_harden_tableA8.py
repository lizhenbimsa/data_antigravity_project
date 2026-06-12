"""v3.7.5 — Harden the 9 Table A8 _title-robustness templates (Item 4 + F2/F5 fixes). [OBSOLETE — 历史/已废]

⚠ 已废 (标题情感轨已删): 本脚本硬化的 9 个 Table A8 标题稳健性模板 (root + 7 paper copies ×
25_tableA8_title_robustness.do.tmpl + benefit_society × 26_bs_title_robustness.do.tmpl) 已在
remove-title-track 改造中全部删除; docstring 与 repls 描述的 _title 变体 / title_applicable /
tone_gap_title_full / frac_title_* 守卫均属已取消的标题情感轨。当前 .do 模板总数 95 (旧 104)。
仅作历史留存, 请勿当作活体迁移工具运行。下方为历史描述。

对每个 `25_tableA8_title_robustness.do.tmpl` (root + 7 份 paper 拷贝) 与
`26_bs_title_robustness.do.tmpl` 幂等地施加三处防御性改动:

  (a) `title_applicable` 守卫 — MAIN_TREAT 无 _full/_ctx 后缀时为 false, 使
      subinstr 空转 (title_var == MAIN_TREAT, 如 strategic_diff strat_diff_n5)
      不再产生静默重跑主回归的退化 Panel A/B。
  (b) `has_dv` / `has_treat` — 对每个 reghdfe (A/B/C/D/E) 按 MAIN_DV / MAIN_TREAT
      存在性 gate, 使缺列 (活体 derivative-paper panel 缺 ROA 与多数 main
      treatment) 不再在 esttab *之前*的 Panel C 处 r(111) 中止。
  (c) `a8_models` / `a8_titles` — 动态、限定范围的 esttab (只含 3 个 A/B/C 估计;
      绝不含 Panel D/E 模型) + 一个写 stub .tex 的 else 分支, 使完全被跳过的表
      不会崩掉 .do 链。

幂等: 已含 'v3.7.5' 标记的文件跳过。
快速失败: 替换前断言每个锚点字符串存在。

运行:  python scripts/migrate/v3_7_5_harden_tableA8.py
"""
from __future__ import annotations

from pathlib import Path

MARKER = "v3.7.5 Table A8 hardening"

_TEMPLATES_DIR = (
    Path(__file__).resolve().parents[2] / "papers" / "_common" / "stata_templates"
)

# 使用 m_* 估计命名的 8 个文件 (root + 7 份 paper 拷贝); 现均已删除。
_M_GROUP = [
    _TEMPLATES_DIR / "25_tableA8_title_robustness.do.tmpl",  # root (P1)
    _TEMPLATES_DIR / "bank_fintech_attention" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "bank_fintech_substance" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "bank_fintech_locus" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "bank_fintech_collab" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "brokerage_network" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "llm_peer" / "25_tableA8_title_robustness.do.tmpl",
    _TEMPLATES_DIR / "strategic_diff" / "25_tableA8_title_robustness.do.tmpl",
]
_BS_FILE = _TEMPLATES_DIR / "benefit_society" / "26_bs_title_robustness.do.tmpl"

# ---- 共享构件块 ----------------------------------------------------------------

_GUARD_BLOCK = """local title_var = subinstr("`title_var'", "_full", "_title", .)

* ==== v3.7.5 Table A8 hardening (Item 4 no-op fix + F2 reghdfe gating + F5 dynamic esttab) ====
* (a) title_applicable=0 when MAIN_TREAT lacks a _full/_ctx suffix (subinstr no-op -> title_var==MAIN_TREAT);
*     prevents the degenerate Panel A/B that silently re-runs the main regression (e.g. strategic_diff strat_diff_n5).
* (b) has_dv/has_treat gate every reghdfe so an absent MAIN_DV/MAIN_TREAT does not r(111)-abort the .do.
* (c) a8_models/a8_titles drive a dynamic, scoped esttab (3 A/B/C estimates only) so a skipped panel never crashes the table.
local title_applicable = ("`title_var'" != "{{MAIN_TREAT}}")
if !`title_applicable' display "  [WARN] {{MAIN_TREAT}} has no _full/_ctx suffix; no genuine _title variant -> Panels A/B N/A."
capture confirm variable {{MAIN_DV}}
local has_dv = (_rc == 0)
capture confirm variable {{MAIN_TREAT}}
local has_treat = (_rc == 0)
local a8_models ""
local a8_titles \"\""""

# 注: 末尾的 `local a8_titles ""` 只是在 Python 字面量里写成转义引号;
# 落盘后就是普通的 `local a8_titles ""`。
_GUARD_BLOCK = _GUARD_BLOCK.replace('local a8_titles ""', 'local a8_titles ""')


def _stub_esttab(open_line: str, tex_name: str) -> tuple[str, str]:
    """返回 (old, new) 对: 把 `esttab <models> ///` 开头行包进
    "空则写 stub / 否则 esttab 动态列表" 守卫。"""
    new = (
        'if "`a8_models\'" == "" {\n'
        '    display "  [WARN] Table A8: no estimable panel for {{PAPER_ID}}; writing stub .tex."\n'
        f'    file open _a8stub using "$tables_dir/{tex_name}", write replace\n'
        '    file write _a8stub "% Table A8 N/A for {{PAPER_ID}}: no usable _title panel (MAIN cols or _title variant absent)." _n\n'
        '    file close _a8stub\n'
        '}\n'
        "else esttab `a8_models' ///"
    )
    return open_line, new


def _m_group_repls() -> list[tuple[str, str]]:
    return [
        # (a)(b)(c) 守卫块 — 锚定在 (唯一的) 第 2 条 subinstr 行上。
        ('local title_var = subinstr("`title_var\'", "_full", "_title", .)', _GUARD_BLOCK),
        # Panel A/B gate (root 模板: 2 处, 全部 gate; 各拷贝: 1 处)。
        (
            "capture confirm variable `title_var'\nif !_rc {",
            "capture confirm variable `title_var'\nif `title_applicable' & `has_dv' & `has_treat' & !_rc {",
        ),
        # 在 3 个渲染出的估计之后各累加 a8_models/a8_titles。
        (
            "    eststo m_title_only\n",
            '    eststo m_title_only\n    local a8_models "`a8_models\' m_title_only"\n    local a8_titles `"`a8_titles\' "Title-only""\'\n',
        ),
        (
            "    eststo m_main_plus_title\n",
            '    eststo m_main_plus_title\n    local a8_models "`a8_models\' m_main_plus_title"\n    local a8_titles `"`a8_titles\' "Main+Title""\'\n',
        ),
        (
            "    eststo m_with_gap\n",
            '    eststo m_with_gap\n    local a8_models "`a8_models\' m_with_gap"\n    local a8_titles `"`a8_titles\' "+Gap control""\'\n',
        ),
        # Panel C / D / E 的 reghdfe 按 MAIN 列存在性 gate。
        (
            "capture confirm variable tone_gap_title_full\nif !_rc {",
            "capture confirm variable tone_gap_title_full\nif `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "capture confirm variable frac_title_mentions_fintech\nif !_rc {",
            "capture confirm variable frac_title_mentions_fintech\nif `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "capture confirm variable frac_title_long\nif !_rc {",
            "capture confirm variable frac_title_long\nif `has_dv' & `has_treat' & !_rc {",
        ),
        # 动态、限定范围的 esttab + stub。
        _stub_esttab(
            "esttab m_title_only m_main_plus_title m_with_gap ///",
            "tableA8_title_robustness.tex",
        ),
        # 动态 mtitles (与 a8_models 并行 -> 部分表也能拿到正确标签)。
        (
            '    mtitles("Title-only" "Main+Title" "+Gap control") ///',
            "    mtitles(`a8_titles') ///",
        ),
    ]


def _bs_repls() -> list[tuple[str, str]]:
    return [
        ('local title_var = subinstr("`title_var\'", "_full", "_title", .)', _GUARD_BLOCK),
        (
            "capture confirm variable `title_var'\nif !_rc {",
            "capture confirm variable `title_var'\nif `title_applicable' & `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "    eststo bs_m_title_only\n",
            '    eststo bs_m_title_only\n    local a8_models "`a8_models\' bs_m_title_only"\n    local a8_titles `"`a8_titles\' "Title-only""\'\n',
        ),
        (
            "    eststo bs_m_main_plus_title\n",
            '    eststo bs_m_main_plus_title\n    local a8_models "`a8_models\' bs_m_main_plus_title"\n    local a8_titles `"`a8_titles\' "Main+Title""\'\n',
        ),
        (
            "    eststo bs_m_with_gap\n",
            '    eststo bs_m_with_gap\n    local a8_models "`a8_models\' bs_m_with_gap"\n    local a8_titles `"`a8_titles\' "+Gap control""\'\n',
        ),
        (
            "capture confirm variable tone_gap_title_full\nif !_rc {",
            "capture confirm variable tone_gap_title_full\nif `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "capture confirm variable frac_title_mentions_fintech\nif !_rc {",
            "capture confirm variable frac_title_mentions_fintech\nif `has_dv' & `has_treat' & !_rc {",
        ),
        (
            "capture confirm variable frac_title_long\nif !_rc {",
            "capture confirm variable frac_title_long\nif `has_dv' & `has_treat' & !_rc {",
        ),
        _stub_esttab(
            "esttab bs_m_title_only bs_m_main_plus_title bs_m_with_gap ///",
            "bs_title_robustness.tex",
        ),
        (
            '    mtitles("Title-only" "Main+Title" "+Gap control") ///',
            "    mtitles(`a8_titles') ///",
        ),
    ]


def _apply(path: Path, repls: list[tuple[str, str]]) -> str:
    content = path.read_text(encoding="utf-8")
    if MARKER in content:
        return "skip (already hardened)"
    for old, new in repls:
        if old not in content:
            raise AssertionError(f"{path.name}: anchor not found:\n---\n{old}\n---")
        content = content.replace(old, new)
    # 后置条件断言
    assert MARKER in content, f"{path.name}: marker not written"
    assert "a8_models" in content and "a8_titles" in content
    assert 'mtitles("Title-only"' not in content, f"{path.name}: static mtitles remains"
    path.write_text(content, encoding="utf-8")
    return "hardened"


def main() -> None:
    results = []
    for p in _M_GROUP:
        results.append((p, _apply(p, _m_group_repls())))
    results.append((_BS_FILE, _apply(_BS_FILE, _bs_repls())))
    for p, status in results:
        rel = p.relative_to(_TEMPLATES_DIR.parents[2])
        print(f"  [{status:>22}] {rel}")
    n_done = sum(1 for _, s in results if s == "hardened")
    print(f"\nv3.7.5 Table A8 hardening: {n_done} hardened, {len(results) - n_done} skipped.")


if __name__ == "__main__":
    main()
