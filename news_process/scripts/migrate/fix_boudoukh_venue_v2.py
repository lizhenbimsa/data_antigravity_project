"""修正 Boudoukh-2019 在所有 _title 轨锚点处的期刊误标
(audit follow-up part 2, 2026-05-31)。[OBSOLETE — 历史/已废一次性脚本]

⚠ 已废: 本脚本 TARGETS / TEMPLATE_TARGETS 列出的多个修复目标现已删除 — docs/ 目录整体删除
(commit 1698bda5, 0 文件); 39g shim (39g_track_discriminant_validity.py)、
pipeline/audit/track_discriminant_validity.py、9 个 Table A8 标题稳健性模板均随 remove-title-track
改造删除。脚本有 `if not p.exists(): MISSING` 兜底故不崩, 但 docstring 把它们列为"携带真锚点的
clean 文件"已与活体不符。仅作历史留存。下方为历史描述。

正确引用: Boudoukh, Feldman, Kogan & Richardson (2019), "Information, Trading, and
Volatility: Evidence from Firm-Specific News" 刊于 **Review of Financial Studies
32(3): 992-1033, DOI 10.1093/rfs/hhy083** — 而**不是** "JFE 133(1): 85-104"。

为何用正则 (而非 fix_title_track_*.py 的字面值成对替换): paper_spec.yaml 的
anchor 把引用折行在 YAML 换行处 —
    anchor: "... Boudoukh et al.
      (2019) JFE; Campbell & Fiske (1959) MTMM"
所以字面值 "Boudoukh et al. (2019) JFE" 永远匹配不上。这里每条 pattern 都
锚定在字面 "Boudoukh" token 上, 用 `\\s+` 跨越折行, 因此**绝不会**误伤这些
文件里的假阳性 JFE 引用:
  - Laeven & Levine (2009) JFE  (年份 2009, 无 Boudoukh)
  - 期刊目标清单 "JFQA / RFS / JFE", "RFS / JFE"  (无年份, 无 Boudoukh)
  - Engelberg-Reed-Ringgenberg (2018) JFE  (年份 2018, 无 Boudoukh)

幂等: 修复后期刊已是 RFS, 重跑不再有任何匹配。
(历史: 此前 EXCLUDES 两个并发编辑文件 docs/methodology/title_track_as_robustness.md 与
tests/test_39g_track_discriminant.py; 两者现均已删除, 该排除说明已失效。)

运行:  F:\\Anaconda3\\python.exe scripts/migrate/fix_boudoukh_venue_v2.py

白话: 一次性的"全仓改错别字"脚本 —— 把引错期刊的那条文献从 JFE 批量改成 RFS,
正则写得只认 "Boudoukh" 这个词, 防止把别人家正经的 JFE 引用也改了。现在目标
文件大多已删, 脚本只剩历史价值。
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]  # 仓库根 (…/news_process)

# 按最长匹配优先排序。每条都要求字面 "Boudoukh"; `\s+`
# 跨越 "al." 与 "(2019)" 之间的 YAML 折行。
PATTERNS: list[tuple[str, str]] = [
    # 参考文献条目形式: "... Information, trading, and volatility. *JFE*, 133(1), 85-104."
    (r"Information, trading, and volatility\. \*JFE\*, 133\(1\), 85-104\.",
     "Information, trading, and volatility. *RFS*, 32(3), 992-1033. "
     "DOI: 10.1093/rfs/hhy083."),
    # markdown, 年份无括号, 带卷号: "Boudoukh et al. 2019 *JFE* 133(1)"
    (r"(Boudoukh et al\.?\s+2019\s+)\*JFE\*(\s+)133\(1\)",
     r"\1*RFS*\g<2>32(3): 992-1033"),
    # markdown, 年份无括号, 无卷号: "Boudoukh ... 2019 *JFE*"
    (r"(Boudoukh[^\n]{0,20}?\s+2019\s+)\*JFE\*",
     r"\1*RFS*"),
    # 括号年份 + 期刊 + 完整卷期页码
    (r"(Boudoukh et al\.\s+)\(2019\)\s*JFE 133\(1\): 85-104",
     r"\1(2019) RFS 32(3): 992-1033"),
    (r"(Boudoukh et al\.\s+)\(2019\)\s*JFE 133\(1\)",
     r"\1(2019) RFS 32(3): 992-1033"),
    # 年份期刊同括号形式 "(2019 JFE ...)"
    (r"(Boudoukh et al\.\s+)\(2019 JFE",
     r"\1(2019 RFS"),
    (r"(Boudoukh \(2019 JFE)",
     r"Boudoukh (2019 RFS"),
    # 裸期刊名, 无卷号, 括号年份: "Boudoukh et al. (2019) JFE"
    (r"(Boudoukh et al\.\s+)\(2019\)\s*JFE",
     r"\1(2019) RFS"),
    # "Boudoukh (2019) JFE" (不带 "et al.")
    (r"Boudoukh \(2019\) JFE",
     r"Boudoukh et al. (2019) RFS"),
]

COMPILED = [(re.compile(p), r) for p, r in PATTERNS]

# 已知携带真 Boudoukh-2019 锚点的 clean 文件 (历史清单, 多数现已删除, 见 docstring)。
# 两个并发编辑中的 dirty 文件刻意不列入。已修复文件也照常列出 (幂等)。
TARGETS: list[Path] = [
    REPO / "CLAUDE.md",
    REPO / "core" / "dag.py",
    REPO / "39g_track_discriminant_validity.py",
    REPO / "pipeline" / "audit" / "track_discriminant_validity.py",
    REPO / "docs" / "PROJECT_DESCRIPTION.md",
    REPO / "docs" / "methodology" / "implicit_guarantee_framework.md",
    REPO / "docs" / "methodology" / "title_track_robustness_report_v2_6.md",
    REPO / "docs" / "plan" / "B_route_master_plan_v2.md",
    REPO / "docs" / "plan" / "B_route_master_plan_v2_audit_log.md",
    REPO / "docs" / "plan" / "portfolio_channel_matrix.md",
    REPO / "papers" / "bank_fintech_tone" / "paper_spec.yaml",
    REPO / "papers" / "bank_fintech_attention" / "paper_spec.yaml",
    REPO / "papers" / "bank_fintech_substance" / "paper_spec.yaml",
    REPO / "papers" / "bank_fintech_locus" / "paper_spec.yaml",
    REPO / "papers" / "bank_fintech_collab" / "paper_spec.yaml",
    REPO / "papers" / "brokerage_network" / "paper_spec.yaml",
    REPO / "papers" / "llm_peer" / "paper_spec.yaml",
    REPO / "papers" / "strategic_diff" / "paper_spec.yaml",
    REPO / "papers" / "benefit_society" / "paper_spec.yaml",
]

# 9 个 Stata Table-A8 模板 (历史清单, 已随 remove-title-track 删除)。其中的
# Boudoukh 引用只出现在注释/addnote 文本 (头部锚点清单 + esttab addnote 字符串),
# 与某并发 plan 正在编辑的 esttab/guard 可执行区互不相交 — 故在此修引用
# 不会与该 plan 的 Panel D/E 导出工作冲突。
_TPL = REPO / "papers" / "_common" / "stata_templates"
TEMPLATE_TARGETS: list[Path] = [
    _TPL / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "bank_fintech_attention" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "bank_fintech_substance" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "bank_fintech_locus" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "bank_fintech_collab" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "brokerage_network" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "llm_peer" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "strategic_diff" / "25_tableA8_title_robustness.do.tmpl",
    _TPL / "benefit_society" / "26_bs_title_robustness.do.tmpl",
]
TARGETS = TARGETS + TEMPLATE_TARGETS

# 健全性守卫: 修复后的文件必须零残留以下任何 JFE 形式。
RESIDUAL = re.compile(r"Boudoukh[^\n]{0,30}(?:2019\)?\s*JFE|2019\s+\*JFE\*)"
                      r"|Boudoukh et al\.\s+\(?2019\)?\s*JFE")


def process(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    text = raw
    n = 0
    for rx, repl in COMPILED:
        text, c = rx.subn(repl, text)
        n += c
    changed = text != raw
    if changed:
        path.write_text(text, encoding="utf-8", newline="")
    # 对 (可能已更新的) 文本做残留检查
    residual = len(RESIDUAL.findall(text))
    return {"file": str(path.relative_to(REPO)), "changed": changed,
            "subs": n, "residual_boudoukh_jfe": residual}


def main() -> None:
    print("=== Boudoukh JFE -> RFS (regex, whitespace-tolerant, Boudoukh-anchored) ===")
    total = 0
    residual_total = 0
    for p in TARGETS:
        if not p.exists():
            print(f"  MISSING: {p}")
            continue
        r = process(p)
        total += int(r["changed"])
        residual_total += r["residual_boudoukh_jfe"]
        flag = "CHG" if r["changed"] else " . "
        warn = "  <-- RESIDUAL!" if r["residual_boudoukh_jfe"] else ""
        print(f"  [{flag}] {r['file']}: subs={r['subs']} "
              f"residual={r['residual_boudoukh_jfe']}{warn}")
    print(f"\nSUMMARY: {total} files changed; "
          f"{residual_total} residual Boudoukh+JFE remaining in targets "
          f"(want 0).")


if __name__ == "__main__":
    main()
