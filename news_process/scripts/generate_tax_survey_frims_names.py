"""scripts/generate_tax_survey_frims_names.py — tax_survey_frims_names.yaml 从
税调企业名称.xlsx 自动派生 (2026-07-03).

设计原则
--------
- 单一可信源 = ``news_process/config/税调企业名称.xlsx`` (税调企业清单,
  44772 行; 消费两列: 企业名称 + 曾用名)
- tax_survey_frims_names.yaml 为 derived artifact, 跑此脚本同步
- 派生规则 frozen 在本脚本中 (审计 trail); 镜像 generate_company_listed_names.py 模式

派生规则
--------
- tax_survey_frims_name = 「企业名称」列 (全称, 无空值; 1 对完全重复行合并)
- variants = [企业名称] + 「曾用名」按分隔符 ``[,\\n]`` 拆分, 组内去重保序,
  主名固定居首
- 源分隔符实测: 曾用名多值以 ``,\\n`` 连接 (``,`` 与 ``\\n`` 各 3786 处);
  主名列 0 含分隔符 → 无误拆风险
- ⚠ 刻意不按 ``、`` 拆分 (仅 3 处, 且出现在括注内部如
  "（罗翔股权不得变更、转让）..." 或联合名称内部, 拆分会产生残片)

已知非问题 (刻意保留)
--------------------
- 跨公司重复曾用名 (实测 1 处) — 客观历史, 仅组内去重;
  下游匹配须容忍一名多主 (同 company_listed_names.yaml 口径)

输出
----
news_process/config/tax_survey_frims_names.yaml (覆盖现有)
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
XLSX = CONFIG_DIR / "税调企业名称.xlsx"
OUT = CONFIG_DIR / "tax_survey_frims_names.yaml"

# 数据冻结日 (与 xlsx 导出批次对应; 重导出新批次时更新)
GENERATED_DATE = "2026-07-03"

SPLIT_RE = re.compile(r"[,\n]")


def _quote(s: str) -> str:
    """YAML 双引号转义 (名称可能含引号/特殊字符)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_records(df: pd.DataFrame) -> list[tuple[str, list[str]]]:
    """从 xlsx 两列派生 (主名, variants) 记录."""
    records: list[tuple[str, list[str]]] = []
    seen_primary: set[str] = set()
    for _, row in df.iterrows():
        primary = str(row["企业名称"]).strip() if pd.notna(row["企业名称"]) else ""
        if not primary or primary in seen_primary:
            continue
        seen_primary.add(primary)
        former = str(row["曾用名"]) if pd.notna(row["曾用名"]) else ""
        variants: list[str] = []
        seen: set[str] = set()
        for name in [primary] + SPLIT_RE.split(former):
            name = name.strip()
            if name and name not in seen:
                seen.add(name)
                variants.append(name)
        records.append((primary, variants))
    return records


def render_yaml(records: list[tuple[str, list[str]]]) -> str:
    lines = [
        "# news_process/config/tax_survey_frims_names.yaml",
        "# " + "─" * 74,
        "# 税调企业名称主清单 — 派生自 config/税调企业名称.xlsx。",
        "#",
        "# Schema (每家企业一条记录):",
        "#   tax_survey_frims_name: 企业名称 (「企业名称」列, 全称)",
        "#   variants: 企业名称 + 「曾用名」拆分 (多值以 ,\\n 连接), 组内去重保序",
        "#",
        "# 重新生成: python scripts/generate_tax_survey_frims_names.py",
        "",
        "metadata:",
        '  version: "1.0.0"',
        '  source: "config/税调企业名称.xlsx (企业名称 + 曾用名)"',
        f"  total_companies: {len(records)}",
        f'  generated_date: "{GENERATED_DATE}"',
        "",
        "companies:",
    ]
    for primary, variants in records:
        lines.append(f"  - tax_survey_frims_name: {_quote(primary)}")
        lines.append("    variants:")
        lines.extend(f"      - {_quote(v)}" for v in variants)
    return "\n".join(lines) + "\n"


def main() -> None:
    df = pd.read_excel(XLSX, dtype=str)
    assert "企业名称" in df.columns and "曾用名" in df.columns, df.columns.tolist()
    records = build_records(df)
    text = render_yaml(records)
    OUT.write_text(text, encoding="utf-8", newline="\n")

    # round-trip 自检: YAML 合法 + 主名居首 + 组内无重复
    data = yaml.safe_load(text)
    assert data["metadata"]["total_companies"] == len(data["companies"]) == len(records)
    for rec in data["companies"]:
        vs = rec["variants"]
        assert vs and rec["tax_survey_frims_name"] == vs[0] and len(vs) == len(set(vs)), rec

    n_var = sum(len(v) for _, v in records)
    n_with_former = sum(1 for _, v in records if len(v) > 1)
    print(f"rows_in_xlsx={len(df)} companies={len(records)} total_variants={n_var} "
          f"with_former={n_with_former}")
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
