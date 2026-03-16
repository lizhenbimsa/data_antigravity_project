# -*- coding: utf-8 -*-
"""
AutoPaper 生产基础设施 — 发布器
==========================================
控制论文从私有仓库到公共仓库的发布流程。
包括文件同步、README 索引更新。
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "09_agent_framework"))

from config import setup_logging

logger = setup_logging("paper.publisher")


class Publisher:
    """
    论文发布器。

    负责将论文从私有生产仓库同步到公共仓库，
    包括文件复制、README 论文索引表自动更新。
    """

    # 同步时排除的文件模式
    EXCLUDE_PATTERNS = {
        ".pipeline_state.json",   # 流水线内部状态
        "__pycache__",            # Python 缓存
        ".DS_Store",              # macOS 元数据
        "Thumbs.db",              # Windows 缩略图
        "*.pyc",                  # 编译的 Python
        ".env",                   # 环境变量文件
    }

    def __init__(
        self,
        source_dir: Path | str,
        target_dir: Path | str,
    ):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)

    def sync_papers(
        self,
        changed_papers: Optional[str] = None,
    ) -> list[str]:
        """
        同步论文到公共仓库。

        Args:
            changed_papers: 变更的论文 ID 列表（空格/逗号分隔）
                            若为 None，同步所有论文

        Returns:
            已同步的论文 ID 列表
        """
        synced = []

        if changed_papers:
            paper_ids = re.split(r'[,\s]+', changed_papers.strip())
            paper_ids = [p.strip().replace("papers/", "") for p in paper_ids if p.strip()]
        else:
            paper_ids = [
                d.name for d in sorted(self.source_dir.iterdir())
                if d.is_dir() and d.name.startswith("paper_")
            ]

        logger.info(f"📦 同步 {len(paper_ids)} 篇论文到公共仓库")

        for paper_id in paper_ids:
            src = self.source_dir / paper_id
            dst = self.target_dir / paper_id

            if not src.exists():
                logger.warning(f"⚠️ 源目录不存在: {src}")
                continue

            try:
                self._sync_directory(src, dst)
                synced.append(paper_id)
                logger.info(f"  ✅ {paper_id}")
            except Exception as e:
                logger.error(f"  ❌ {paper_id}: {e}")

        logger.info(f"📦 同步完成: {len(synced)}/{len(paper_ids)}")
        return synced

    def _sync_directory(self, src: Path, dst: Path):
        """递归同步目录，排除特定文件"""
        dst.mkdir(parents=True, exist_ok=True)

        for item in src.rglob("*"):
            # 检查排除规则
            rel_path = item.relative_to(src)
            if self._should_exclude(rel_path):
                continue

            target = dst / rel_path

            if item.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            elif item.is_file():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, target)

    def _should_exclude(self, rel_path: Path) -> bool:
        """检查路径是否应被排除"""
        path_str = str(rel_path)
        for pattern in self.EXCLUDE_PATTERNS:
            if pattern.startswith("*"):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True
        return False

    def update_readme(self, readme_path: Optional[Path] = None):
        """
        自动更新 README.md 中的论文索引表。

        扫描所有论文目录的 metadata.json，
        生成按 ID 排序的 Markdown 表格。
        """
        readme_path = readme_path or (self.target_dir / "README.md")

        # 收集所有论文元数据
        papers = []
        for paper_dir in sorted(self.target_dir.glob("paper_*")):
            if not paper_dir.is_dir():
                continue

            # 查找最新版本
            versions = sorted(paper_dir.glob("v*/metadata.json"))
            if versions:
                meta_file = versions[-1]
            elif (paper_dir / "metadata.json").exists():
                meta_file = paper_dir / "metadata.json"
            else:
                continue

            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                papers.append({
                    "id": paper_dir.name,
                    "title": meta.get("title", "Untitled"),
                    "method": meta.get("method", "Unknown"),
                    "contributor": meta.get("contributor", "anonymous"),
                    "date": meta.get("published_at", "Unknown")[:10],
                    "parent": meta.get("parent_id", "—"),
                })
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"⚠️ 无法解析 {meta_file}: {e}")

        if not papers:
            logger.warning("⚠️ 未找到任何论文元数据")
            return

        # 生成表格
        table_lines = [
            "| ID | Title | Method | Parent | Contributor | Date |",
            "|----|-------|--------|--------|-------------|------|",
        ]
        for p in papers:
            # 截断标题
            title = p["title"][:60] + "..." if len(p["title"]) > 60 else p["title"]
            title = title.replace("|", "\\|")
            contributor = f"@{p['contributor']}" if p["contributor"] else "@anonymous"
            parent = f"[{p['parent']}]({p['parent']}/)" if p["parent"] != "—" else "—"

            table_lines.append(
                f"| [{p['id']}]({p['id']}/) | {title} | {p['method']} | "
                f"{parent} | {contributor} | {p['date']} |"
            )

        table_content = "\n".join(table_lines)

        # 更新 README
        if readme_path.exists():
            readme = readme_path.read_text(encoding="utf-8")

            # 替换论文索引表（在 ## Paper Index 和下一个 ## 之间）
            pattern = r"(## Paper Index\s*\n).*?(\n## )"
            if re.search(pattern, readme, re.DOTALL):
                readme = re.sub(
                    pattern,
                    f"\\1{table_content}\n\n\\2",
                    readme,
                    flags=re.DOTALL
                )
            else:
                # 如果找不到区间，追加到末尾
                readme += f"\n\n## Paper Index\n{table_content}\n"

            readme_path.write_text(readme, encoding="utf-8")
            logger.info(f"✅ README 已更新: {len(papers)} 篇论文")
        else:
            # 创建新的 README
            readme_content = f"""# APE Working Papers

**Autonomous Policy Evaluation**

This repository contains the complete, publicly available archive of all AutoPaper working papers.

## Paper Index
{table_content}

## How This Repository Works
This is a **public mirror** of the APE papers archive. It syncs automatically.

## License
Papers and code are released for research and educational purposes.

## Contact
Maintained by the AutoPaper Team.
"""
            readme_path.write_text(readme_content, encoding="utf-8")
            logger.info(f"✅ README 已创建: {len(papers)} 篇论文")


# ============================================================
# CLI 入口
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AutoPaper 论文发布器")
    parser.add_argument("--source", default="papers/",
                        help="源目录（私有仓库中的论文目录）")
    parser.add_argument("--target", default="../public-repo/",
                        help="目标目录（公共仓库）")
    parser.add_argument("--changed", default=None,
                        help="仅同步变更的论文 ID")
    parser.add_argument("--update-readme", action="store_true",
                        help="仅更新 README 论文索引")

    args = parser.parse_args()

    publisher = Publisher(source_dir=args.source, target_dir=args.target)

    if args.update_readme:
        publisher.update_readme()
    else:
        publisher.sync_papers(changed_papers=args.changed)
        publisher.update_readme()
