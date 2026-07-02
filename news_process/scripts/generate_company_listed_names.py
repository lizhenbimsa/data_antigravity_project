"""scripts/generate_company_listed_names.py — company_listed_names.yaml 从
全部A股公司名称_iFind.xlsx 自动派生 (2026-07-02).

设计原则
--------
- 单一可信源 = ``news_process/config/全部A股公司名称_iFind.xlsx`` (iFind 导出,
  5528 家 A 股公司; 消费两列: 公司中文名称 + 合并公司中文名称)
- company_listed_names.yaml 为 derived artifact, 跑此脚本同步
- 派生规则 frozen 在本脚本中 (审计 trail); 镜像 generate_bank_list_from_addresses.py 模式

派生规则
--------
- company_listed_name = 「公司中文名称」列 (全称, 5528 行无重复无空值)
- variants = [公司中文名称] + 「合并公司中文名称」按分隔符 ``[,，、;；]`` 拆分
  (历史名 / 曾用名 / 证券简称), 组内去重保序, 主名固定居首
- 源分隔符实测仅 ``,`` (19742 处) 与 ``;`` (20 处); 主名列 0 含分隔符 → 无误拆风险

iFind 导出瑕疵清理 (2026-07-02 审核发现, 恰 15 个脏 variant)
----------------------------------------------------------
- 规则1: 「X 存」/「X存」且 X 是组内既有名称 → 「存续」标记粘名残片 (12 个,
  如 "民生银行 存" / "比亚迪存"; 合法名如 音飞储存 的 base「音飞储」不在组内, 不受累)
- 规则2: 显式黑名单「中国中」→ 中国中冶/中国中车/中国中免 的截断残片
  (3 个, 实体匹配高危: 会误命中 中国中铁/中国中医 等)

已知非问题 (刻意保留)
--------------------
- 31 个跨公司重复 variant (如 "东风股份" / "*ST天龙" 简称复用) — 客观历史,
  仅组内去重; 下游匹配须容忍一名多主

输出
----
news_process/config/company_listed_names.yaml (覆盖现有)
"""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
import yaml

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
XLSX = CONFIG_DIR / "全部A股公司名称_iFind.xlsx"
OUT = CONFIG_DIR / "company_listed_names.yaml"

# 数据冻结日 (与 xlsx 导出批次对应; 重导出新批次时更新)
GENERATED_DATE = "2026-07-02"

SPLIT_RE = re.compile(r"[,，、;；]")

# iFind 导出瑕疵清理 (规则见模块 docstring)
_VARIANT_BLACKLIST = {"中国中"}


def _is_cun_artifact(name: str, group: set[str]) -> bool:
    """「X 存」/「X存」且 X 是组内既有名称 → 「存续」标记粘名残片."""
    if not name.endswith("存"):
        return False
    base = name[:-1].strip()
    return bool(base) and base != name and base in group


def _quote(s: str) -> str:
    """YAML 双引号转义 (名称可能含引号/特殊字符)."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def build_records(df: pd.DataFrame) -> tuple[list[tuple[str, list[str]]], list[tuple[str, str]]]:
    """从 xlsx 两列派生 (主名, variants) 记录; 返回 (records, dropped)."""
    records: list[tuple[str, list[str]]] = []
    dropped: list[tuple[str, str]] = []
    seen_primary: set[str] = set()
    for _, row in df.iterrows():
        primary = str(row["公司中文名称"]).strip() if pd.notna(row["公司中文名称"]) else ""
        if not primary or primary in seen_primary:
            continue
        seen_primary.add(primary)
        merged = str(row["合并公司中文名称"]) if pd.notna(row["合并公司中文名称"]) else ""
        variants: list[str] = []
        seen: set[str] = set()
        for name in [primary] + SPLIT_RE.split(merged):
            name = name.strip()
            if name and name not in seen:
                seen.add(name)
                variants.append(name)
        clean = [v for v in variants
                 if v not in _VARIANT_BLACKLIST and not _is_cun_artifact(v, seen)]
        dropped += [(primary, v) for v in variants if v not in clean]
        records.append((primary, clean))
    return records, dropped


def render_yaml(records: list[tuple[str, list[str]]]) -> str:
    lines = [
        "# news_process/config/company_listed_names.yaml",
        "# " + "─" * 74,
        "# 全部 A 股上市公司名称主清单 — 派生自 config/全部A股公司名称_iFind.xlsx (iFind 导出)。",
        "#",
        "# Schema (每家公司一条记录):",
        "#   company_listed_name: 公司中文名称 (iFind 「公司中文名称」列, 全称)",
        "#   variants: 公司中文名称 + 「合并公司中文名称」拆分 (历史名/曾用名/简称), 组内去重保序",
        "#",
        "# 数据清理 (2026-07-02 审核): 剔除 iFind 导出瑕疵 15 个 —",
        '#   12 个「存续」标记粘名残片 (如 "民生银行 存"/"比亚迪存")',
        '#   3 个截断残片 "中国中" (中国中冶/中国中车/中国中免, 实体匹配高危)',
        "#",
        "# 重新生成: python scripts/generate_company_listed_names.py",
        "",
        "metadata:",
        '  version: "1.0.0"',
        '  source: "config/全部A股公司名称_iFind.xlsx (公司中文名称 + 合并公司中文名称)"',
        f"  total_companies: {len(records)}",
        f'  generated_date: "{GENERATED_DATE}"',
        "",
        "companies:",
    ]
    for primary, variants in records:
        lines.append(f"  - company_listed_name: {_quote(primary)}")
        lines.append("    variants:")
        lines.extend(f"      - {_quote(v)}" for v in variants)
    return "\n".join(lines) + "\n"


def main() -> None:
    df = pd.read_excel(XLSX, dtype=str)
    assert "公司中文名称" in df.columns and "合并公司中文名称" in df.columns, df.columns.tolist()
    records, dropped = build_records(df)
    text = render_yaml(records)
    OUT.write_text(text, encoding="utf-8", newline="\n")

    # round-trip 自检: YAML 合法 + 主名居首 + 组内无重复
    data = yaml.safe_load(text)
    assert data["metadata"]["total_companies"] == len(data["companies"]) == len(records)
    for rec in data["companies"]:
        vs = rec["variants"]
        assert vs and rec["company_listed_name"] == vs[0] and len(vs) == len(set(vs)), rec

    n_var = sum(len(v) for _, v in records)
    print(f"rows_in_xlsx={len(df)} companies={len(records)} total_variants={n_var} "
          f"dropped={len(dropped)}")
    for d in dropped:
        print(f"  dropped: {d}")
    print(f"written: {OUT}")


if __name__ == "__main__":
    main()
