# -*- coding: utf-8 -*-
"""
AutoPaper 生产基础设施 — 质量扫描器
==========================================
发布前的自动化质量检查：验证文件完整性、
元数据格式、代码可执行性，生成 scan_report.json。
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "09_agent_framework"))

from config import setup_logging

logger = setup_logging("paper.quality_scan")


# ============================================================
# 检查项定义
# ============================================================

# Combined list of expected files, with updated severities and file types
expected_files = [
    ("research_plan.md", "error", "必须有研究计划"),
    ("metadata.json", "error", "必须有元数据"),
    ("REPLICATION.md", "warning", "建议有复现指南"),
    ("paper.md", "error", "必须有最终论文"),
    ("code/00_packages.do", "info",     "Stata 包安装脚本"),
    ("code/01_fetch_data.do", "warning", "数据获取脚本"),
    ("code/03_main_analysis.do", "warning", "主分析脚本"),
    ("code/05_figures.do", "info",     "图表生成脚本"),
]


class QualityScanner:
    """论文质量扫描器"""

    def __init__(self, paper_dir: Path | str):
        self.paper_dir = Path(paper_dir)
        self.checks: list[dict] = []
        self.errors = 0
        self.warnings = 0

    def scan(self) -> dict:
        """
        执行完整的质量扫描。

        Returns:
            扫描报告 dict
        """
        logger.info(f"🔍 扫描论文目录: {self.paper_dir}")

        self._check_expected_files() # Renamed from _check_required_files and _check_recommended_files
        self._check_metadata()
        self._check_markdown()
        self._check_stata_code() # Renamed from _check_r_code
        self._check_figures()

        report = {
            "paper_dir": str(self.paper_dir),
            "scanned_at": datetime.now().isoformat(),
            "overall": self._overall_status(),
            "errors": self.errors,
            "warnings": self.warnings,
            "total_checks": len(self.checks),
            "checks": self.checks,
        }

        # 保存报告
        report_path = self.paper_dir / "scan_report.json"
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        logger.info(f"📊 扫描完成: {report['overall'].upper()} "
                     f"({self.errors} errors, {self.warnings} warnings)")

        return report

    def _add_check(self, name: str, status: str, detail: str = ""):
        """添加一项检查结果"""
        self.checks.append({
            "name": name,
            "status": status,  # pass / fail / warning / info
            "detail": detail,
        })
        if status == "fail" or status == "error": # Added "error" as a synonym for "fail"
            self.errors += 1
        elif status == "warning":
            self.warnings += 1

    def _overall_status(self) -> str:
        if self.errors > 0:
            return "fail"
        elif self.warnings > 0:
            return "warning"
        return "pass"

    # ---- 检查项实现 ----

    def _check_expected_files(self):
        """检查预期文件是否存在"""
        for filename, severity, desc in expected_files:
            path = self.paper_dir / filename
            if path.exists():
                self._add_check(
                    f"file_exists:{filename}", "pass",
                    f"{desc} 存在 ({path.stat().st_size} bytes)"
                )
            else:
                self._add_check(
                    f"file_exists:{filename}", severity, # Use the severity from the list
                    f"{desc} 缺失"
                )

    def _check_metadata(self):
        """验证 metadata.json 格式和内容"""
        meta_path = self.paper_dir / "metadata.json"
        if not meta_path.exists():
            return

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))

            # 必需字段
            required_fields = [
                "paper_id", "title", "method", "contributor",
                "authoring_model", "published_at", "paper_family_id", "version"
            ]
            for field in required_fields:
                if field in meta and meta[field] is not None:
                    self._add_check(
                        f"metadata:{field}", "pass",
                        f"字段存在: {str(meta[field])[:50]}"
                    )
                else:
                    self._add_check(
                        f"metadata:{field}", "fail",
                        f"必需字段缺失或为 null"
                    )

            # 方法验证
            valid_methods = {"DiD", "RDD", "DR", "IV", "Unknown"}
            if meta.get("method") not in valid_methods:
                self._add_check(
                    "metadata:method_valid", "warning",
                    f"方法 '{meta.get('method')}' 不在标准列表中"
                )

            # 版本号验证
            if isinstance(meta.get("version"), int) and meta["version"] > 0:
                self._add_check("metadata:version_valid", "pass", "版本号有效")
            else:
                self._add_check("metadata:version_valid", "fail", "版本号无效")

            # ISO 时间格式验证
            try:
                datetime.fromisoformat(meta.get("published_at", ""))
                self._add_check("metadata:timestamp_valid", "pass", "时间戳格式正确")
            except (ValueError, TypeError):
                self._add_check("metadata:timestamp_valid", "warning", "时间戳格式异常")

        except json.JSONDecodeError as e:
            self._add_check("metadata:parse", "fail", f"JSON 解析失败: {e}")

    def _check_markdown(self):
        """检查 Markdown 源码基本结构"""
        md_path = self.paper_dir / "paper.md"
        if not md_path.exists():
            return

        content = md_path.read_text(encoding="utf-8", errors="ignore")

        # 检查必需的 Markdown 结构
        structures = {
            r"^#\s+": "标题",
            r"## 引言": "章节 - 引言",
            r"## 结论": "章节 - 结论",
        }

        for pattern, desc in structures.items():
            if re.search(pattern, content, flags=re.MULTILINE):
                self._add_check(f"markdown:{desc}", "pass", f"找到 {desc}")
            else:
                self._add_check(f"markdown:{desc}", "warning", f"未找到 {desc}")

        # 文件大小检查
        size_kb = len(content) / 1024
        if size_kb < 5:
            self._add_check(
                "markdown:size", "warning",
                f"论文过短 ({size_kb:.1f} KB)"
            )
        else:
            self._add_check(
                "markdown:size", "pass",
                f"论文大小合理 ({size_kb:.1f} KB)"
            )

    def _check_stata_code(self):
        """检查 Stata 代码基本质量"""
        code_dir = self.paper_dir / "code"
        if not code_dir.exists():
            self._add_check("code:directory", "warning", "code/ 目录不存在")
            return

        do_files = list(code_dir.glob("*.do"))
        self._add_check(
            "code:count", "pass" if do_files else "warning",
            f"找到 {len(do_files)} 个 Stata 脚本"
        )

        for do_file in do_files:
            content = do_file.read_text(encoding="utf-8", errors="ignore")

            # 检查是否有硬编码的绝对路径
            abs_paths = re.findall(r'["\'](?:[A-Z]:\\|/Users/|/home/)[^"\']+["\']', content)
            if abs_paths:
                self._add_check(
                    f"code:{r_file.name}:abs_paths", "warning",
                    f"发现硬编码绝对路径: {abs_paths[:3]}"
                )

            # 检查是否设置了随机种子
            if "set.seed" in content or "SEED" in content:
                self._add_check(
                    f"code:{r_file.name}:seed", "pass",
                    "随机种子已设置"
                )

            # 检查是否有聚类标准误
            if "cluster" in content.lower():
                self._add_check(
                    f"code:{r_file.name}:cluster_se", "pass",
                    "使用了聚类标准误"
                )

    def _check_figures(self):
        """检查图表目录"""
        fig_dir = self.paper_dir / "figures"
        if not fig_dir.exists():
            self._add_check("figures:directory", "info", "figures/ 目录不存在")
            return

        figures = list(fig_dir.glob("*"))
        self._add_check(
            "figures:count",
            "pass" if figures else "warning",
            f"找到 {len(figures)} 个图表文件"
        )


# ============================================================
# 批量扫描
# ============================================================

def scan_all_papers(
    papers_dir: Path | str,
    changed_only: Optional[str] = None,
) -> list[dict]:
    """
    批量扫描所有论文。

    Args:
        papers_dir: 论文根目录
        changed_only: 仅扫描指定的论文（空格/逗号分隔的 ID 列表）

    Returns:
        所有扫描报告列表
    """
    papers_dir = Path(papers_dir)
    reports = []

    # 确定要扫描的目录
    if changed_only:
        paper_ids = re.split(r'[,\s]+', changed_only.strip())
        dirs_to_scan = []
        for pid in paper_ids:
            pid = pid.strip().replace("papers/", "")
            paper_path = papers_dir / pid
            if paper_path.exists():
                # 查找最新版本目录
                versions = sorted(paper_path.glob("v*/"))
                if versions:
                    dirs_to_scan.append(versions[-1])
                else:
                    dirs_to_scan.append(paper_path)
    else:
        dirs_to_scan = sorted(papers_dir.glob("paper_*/v*/"))

    for paper_dir in dirs_to_scan:
        scanner = QualityScanner(paper_dir)
        report = scanner.scan()
        reports.append(report)

    # 汇总
    total_errors = sum(r["errors"] for r in reports)
    total_warnings = sum(r["warnings"] for r in reports)
    logger.info(
        f"\n📋 批量扫描完成: {len(reports)} 篇论文 | "
        f"{total_errors} errors | {total_warnings} warnings"
    )

    return reports


# ============================================================
# CLI 入口
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AutoPaper 论文质量扫描")
    parser.add_argument("path", help="论文目录路径（单篇或批量）")
    parser.add_argument("--changed", default=None,
                        help="仅扫描变更的论文 ID 列表")

    args = parser.parse_args()

    path = Path(args.path)

    if (path / "metadata.json").exists() or (path / "paper.md").exists():
        # 单篇论文
        scanner = QualityScanner(path)
        report = scanner.scan()
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        # 批量扫描
        reports = scan_all_papers(path, changed_only=args.changed)
        for r in reports:
            status_emoji = {"pass": "✅", "warning": "⚠️", "fail": "❌"}
            emoji = status_emoji.get(r["overall"], "❓")
            print(f"  {emoji} {r['paper_dir']}: {r['overall']}")
