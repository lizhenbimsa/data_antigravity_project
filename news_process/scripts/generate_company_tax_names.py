"""scripts/generate_company_tax_names.py — company_tax_names.yaml 从
税调企业名称.xlsx 自动派生 (2026-07-07).

设计原则
--------
- 单一可信源 = ``news_process/config/税调企业名称.xlsx`` (税调企业清单,
  44772 行 / 9 列批次; 前身 2 列批次的派生物 tax_survey_frims_names.yaml
  已随本次升级退役)
- company_tax_names.yaml 为 derived artifact, 跑此脚本同步
- 派生规则 frozen 在本脚本中 (审计 trail); schema 镜像
  config/company_listed_names.yaml (每企业一条记录 + variants 列表)

派生规则
--------
- company_tax_name = 「企业名称」列 (全称, 无空值; 1 对完全重复行合并)
- usci = 「统一社会信用代码」列 (18 位, 恒引号; 源全非空)
- province / city / district = 「所属省份 / 所属城市 / 所属区县」原样透传
- address = 「企业地址」原样透传 (源仅一列地址, 不区分注册/办公)
- variants = [企业名称] + 「曾用名」拆分 + [简称] + 「曾用名简称」拆分,
  组内去重保序, 主名固定居首 (全称在前、简称在后)
- 源分隔符实测 (本批次): 曾用名多值以 ``,\\n`` 连接 (``,`` 与 ``\\n`` 各
  3786 处); 曾用名简称以 ``,`` 连接 (3599 处, 无 ``\\n``); 统一用
  ``[,\\n]`` 拆分。主名/简称列不含 ``[,\\n]`` → 无误拆风险
- ⚠ 刻意不按 ``、`` 拆分 (曾用名仅 3 处, 出现在括注/联合名称内部,
  拆分会产生残片; 同 tax_survey_frims_names.yaml v1.0.0 先例)

已知非问题 (刻意保留)
--------------------
- 跨企业重复 variant — 客观现实 (集团简称共用等), 仅组内去重;
  下游匹配须容忍一名多主 (同 company_listed_names.yaml 口径)
- 2 字超短简称 (如 "建发"/"金地") — 真实品牌简称, 保留;
  短名假阳性 (如 "科技"/"电脑" 等通用 token 挂个别企业) **不在源头裁剪** — 与
  company_listed_names.yaml 同口径 (刻意不裁剪只披露)。⚠ F1(b) 据实校正 (2026-07-10):
  税调 02 cooc 匹配层**刻意不硬过滤短名**, 仅 surface B1 单企业占比告警 + 提供
  `n_docs_longhit` (≥4 字命中稳健臂) + 分析端 usci 剔除受污企业行作对冲 (见
  company_tax_bank/02 codebook §7 L1); 故非"同银行侧短名过滤"口径 —— 原措辞已按实现校正。

输出
----
news_process/config/company_tax_names.yaml (覆盖现有)
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
XLSX = CONFIG_DIR / "税调企业名称.xlsx"
OUT = CONFIG_DIR / "company_tax_names.yaml"

# 数据冻结日 (与 xlsx 导出批次对应; 重导出新批次时更新)
GENERATED_DATE = "2026-07-07"
VERSION = "1.0.0"

SPLIT_RE = re.compile(r"[,\n]")

# 透传字段: (yaml 键, xlsx 列名)
PASSTHROUGH = [
    ("usci", "统一社会信用代码"),
    ("province", "所属省份"),
    ("city", "所属城市"),
    ("district", "所属区县"),
    ("address", "企业地址"),
]

REQUIRED_COLS = ["企业名称", "简称", "曾用名", "曾用名简称"] + [c for _, c in PASSTHROUGH]


def _cell(row: pd.Series, col: str) -> str:
    v = row[col]
    return str(v).strip() if pd.notna(v) else ""


def _quote(s: str) -> str:
    """YAML 双引号转义 (名称/地址可能含引号/特殊字符)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_records(df: pd.DataFrame) -> list[dict]:
    """从 xlsx 派生记录: 主名 + 5 透传字段 + variants."""
    records: list[dict] = []
    seen_primary: set[str] = set()
    for _, row in df.iterrows():
        primary = _cell(row, "企业名称")
        if not primary or primary in seen_primary:
            continue
        seen_primary.add(primary)
        variants: list[str] = []
        seen: set[str] = set()
        candidates = (
            [primary]
            + SPLIT_RE.split(_cell(row, "曾用名"))
            + [_cell(row, "简称")]
            + SPLIT_RE.split(_cell(row, "曾用名简称"))
        )
        for name in candidates:
            name = name.strip()
            if name and name not in seen:
                seen.add(name)
                variants.append(name)
        rec = {"company_tax_name": primary, "variants": variants}
        for key, col in PASSTHROUGH:
            rec[key] = _cell(row, col)
        records.append(rec)
    return records


def render_yaml(records: list[dict]) -> str:
    lines = [
        "# news_process/config/company_tax_names.yaml",
        "# " + "─" * 74,
        "# 税调企业名称主清单 — 派生自 config/税调企业名称.xlsx (9 列批次)。",
        "# schema 镜像 config/company_listed_names.yaml; 前身 2 列批次派生物",
        "# tax_survey_frims_names.yaml 已退役。",
        "#",
        "# Schema (每家企业一条记录):",
        "#   company_tax_name: 企业名称 (「企业名称」列, 全称)",
        "#   usci: 统一社会信用代码 (18 位, 恒引号)",
        "#   province / city / district: 所属省份 / 所属城市 / 所属区县 (原样透传)",
        "#   address: 企业地址 (源仅一列, 不区分注册/办公; 原样透传)",
        "#   variants: 企业名称 + 曾用名拆分 + 简称 + 曾用名简称拆分,",
        "#             组内去重保序 (全称在前、简称在后; 多值分隔符 [,\\n];",
        "#             「、」仅 3 处且在括注/联合名称内部, 刻意不拆)",
        "#",
        "# 重新生成: python scripts/generate_company_tax_names.py",
        "",
        "metadata:",
        f'  version: "{VERSION}"',
        '  source: "config/税调企业名称.xlsx (统一社会信用代码 + 企业名称 + 简称'
        ' + 曾用名 + 曾用名简称 + 所属省份/城市/区县 + 企业地址)"',
        f"  total_companies: {{n}}",
        f'  generated_date: "{GENERATED_DATE}"',
        "",
        "companies:",
    ]
    lines = [ln.format(n=len(records)) if "{n}" in ln else ln for ln in lines]
    for rec in records:
        lines.append(f"  - company_tax_name: {_quote(rec['company_tax_name'])}")
        for key, _ in PASSTHROUGH:
            lines.append(f"    {key}: {_quote(rec[key])}")
        lines.append("    variants:")
        lines.extend(f"      - {_quote(v)}" for v in rec["variants"])
    return "\n".join(lines) + "\n"


def main() -> None:
    df = pd.read_excel(XLSX, dtype=str)
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    assert not missing, f"xlsx 缺列: {missing}; 实有 {df.columns.tolist()}"
    records = build_records(df)
    text = render_yaml(records)
    OUT.write_text(text, encoding="utf-8", newline="\n")

    # round-trip 自检: YAML 合法 + 主名居首 + 组内无重复 + usci 18 位
    data = yaml.safe_load(text)
    assert data["metadata"]["total_companies"] == len(data["companies"]) == len(records)
    for rec in data["companies"]:
        vs = rec["variants"]
        assert vs and rec["company_tax_name"] == vs[0] and len(vs) == len(set(vs)), rec
        assert len(rec["usci"]) == 18, rec

    n_var = sum(len(r["variants"]) for r in records)
    n_with_former = sum(1 for r in records if len(r["variants"]) > 2)
    print(
        f"rows_in_xlsx={len(df)} companies={len(records)} total_variants={n_var} "
        f"with_former={n_with_former}"
    )
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
