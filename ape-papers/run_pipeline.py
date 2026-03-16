#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APEP — 一键运行入口
==========================================
整合所有生产基础设施模块，提供单一命令行入口：

    python run_pipeline.py 500 --domain "labor economics"

流程:
  1. 生成 5 个研究创意 (ideas.md)
  2. 排名并选择最佳创意
  3. 制定研究计划 (initial_plan.md)
  4. 生成 R 数据获取代码并执行
  5. 生成 R 分析代码并执行
  6. 撰写学术论文 (paper.tex)
  7. 多模型同行评审
  8. 修订并发布
"""

import os
import sys
import argparse
from pathlib import Path

# 强制 stdout/stderr 使用 UTF-8，避免 Windows GBK 编码无法处理 emoji
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# 确保所有子模块都可以导入
PROJECT_ROOT = Path(__file__).parent.resolve()

# 自动切换工作目录到脚本所在的 ape-papers 目录
os.chdir(PROJECT_ROOT)

sys.path.insert(0, str(PROJECT_ROOT / "09_agent_framework"))
sys.path.insert(0, str(PROJECT_ROOT / "10_review_pipeline"))
sys.path.insert(0, str(PROJECT_ROOT / "11_tournament"))
sys.path.insert(0, str(PROJECT_ROOT / "12_CI_CD"))

# 设置项目根目录
os.environ.setdefault("APEP_ROOT", str(PROJECT_ROOT))

# 确保 LaTeX 和 Perl 取向正常
if sys.platform == "win32":
    os.environ["PATH"] = f"C:\\Strawberry\\perl\\bin;{os.environ.get('PATH', '')}"


def check_prerequisites():
    """检查运行前提条件"""
    errors = []
    warnings = []

    # Python 依赖
    try:
        import httpx  # noqa
    except ImportError:
        errors.append("缺少 httpx，请运行: pip install httpx")

    # R 环境（非阻断性警告）
    import shutil
    if not shutil.which("Rscript"):
        warnings.append("未找到 Rscript — 数据获取和分析阶段将跳过 R 执行")

    # API 配置
    from config import UNIFIED_API_KEY
    if not UNIFIED_API_KEY:
        errors.append("缺少 API Key，请在 config.py 中配置 UNIFIED_API_KEY")

    if errors:
        print("\n🛑 前提条件检查失败:")
        for e in errors:
            print(f"   ❌ {e}")
        print("\n请参考 01_env_config.md 设置环境。")
        return False

    if warnings:
        for w in warnings:
            print(f"   ⚠️  {w}")

    print("✅ 核心前提条件满足")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="APEP 论文生产流水线 — 一键生成学术论文",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_pipeline.py 500 --domain "labor economics"
  python run_pipeline.py 501 --model gpt-4.1 --contributor SocialCatalystLab
  python run_pipeline.py 500 --resume-from analysis  # 从分析阶段恢复
  python run_pipeline.py 500 --check-only  # 仅检查环境
        """
    )

    parser.add_argument(
        "paper_num", type=int, nargs="?", default=None,
        help="论文编号（如 500 → apep_0500）"
    )
    parser.add_argument(
        "--version", type=int, default=1,
        help="论文版本号（默认: 1）"
    )
    parser.add_argument(
        "--model", default="claude-write",
        choices=["gemini-write", "gpt-write", "claude-write", "grok-write", "deepseek-write"],
        help="撰写使用的 LLM 模型（默认: claude-write）"
    )
    parser.add_argument(
        "--contributor", default="anonymous",
        help="贡献者名称（默认: anonymous）"
    )
    parser.add_argument(
        "--domain", default="labor economics",
        help="政策研究领域（默认: labor economics）"
    )
    parser.add_argument(
        "--resume-from", default=None,
        choices=["ideas", "plan", "data", "analysis", "paper", "review", "revision", "publish"],
        help="从指定阶段恢复运行"
    )
    parser.add_argument(
        "--check-only", action="store_true",
        help="仅检查环境，不运行流水线"
    )

    args = parser.parse_args()

    # ---- 环境检查 ----
    print("=" * 60)
    print("🚀 APEP 论文生产流水线")
    print("=" * 60)
    print()

    if not check_prerequisites():
        sys.exit(1)

    if args.check_only:
        print("\n✅ 环境检查完成。使用 --help 查看运行选项。")
        sys.exit(0)

    if args.paper_num is None:
        parser.error("请指定论文编号（如: python run_pipeline.py 500）")

    # ---- 启动流水线 ----
    from agent_orchestrator import PaperPipeline

    paper_id = f"apep_{args.paper_num:04d}"

    print(f"\n📝 论文: {paper_id} v{args.version}")
    print(f"🤖 模型: {args.model}")
    print(f"👤 贡献者: {args.contributor}")
    print(f"📚 领域: {args.domain}")
    if args.resume_from:
        print(f"🔄 从阶段恢复: {args.resume_from}")
    print()

    pipeline = PaperPipeline(
        paper_id=paper_id,
        version=args.version,
        model_key=args.model,
        contributor=args.contributor,
        policy_domain=args.domain,
    )

    success = pipeline.run(start_from=args.resume_from)

    if success:
        print("\n" + "=" * 60)
        print("🎉 论文生成完成！")
        print("=" * 60)
        print(f"\n📂 论文目录: {pipeline.paper_dir}")
        print(f"📄 论文文件: {pipeline.paper_dir / 'paper.tex'}")
        if (pipeline.paper_dir / "paper.pdf").exists():
            print(f"📋 PDF 文件: {pipeline.paper_dir / 'paper.pdf'}")
        print(f"📊 分析结果: {pipeline.paper_dir / 'data' / 'main_results_summary.csv'}")
        print(f"🔍 质量报告: {pipeline.paper_dir / 'scan_report.json'}")
    else:
        print("\n❌ 流水线运行失败。检查日志获取详细信息。")
        print("   使用 --resume-from <stage> 从失败阶段恢复。")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
