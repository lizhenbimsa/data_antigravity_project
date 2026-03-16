#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoPaper — 一键运行入口
==========================================
整合所有生产基础设施模块，提供单一命令行入口：

    python run_pipeline.py 500 --domain "Commercial Banking"

流程:
  1. 生成 5 个研究创意 (ideas.md)
  2. 排名并选择最佳创意
  3. 制定研究计划 (initial_plan.md)
  4. 生成 Stata 数据获取代码并执行
  5. 生成 Stata 分析代码并执行
  6. 撰写学术论文 (paper.md)
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

# 自动切换工作目录到脚本所在的 amy_papers 目录
os.chdir(PROJECT_ROOT)

sys.path.insert(0, str(PROJECT_ROOT / "09_agent_framework"))
sys.path.insert(0, str(PROJECT_ROOT / "10_review_pipeline"))
sys.path.insert(0, str(PROJECT_ROOT / "11_tournament"))
sys.path.insert(0, str(PROJECT_ROOT / "12_CI_CD"))

# 设置项目根目录
os.environ.setdefault("AUTOPAPER_ROOT", str(PROJECT_ROOT))




def check_prerequisites(logger):
    """检查运行前提条件"""
    errors = []
    warnings = []

    # Python 依赖
    try:
        import httpx  # noqa
    except ImportError:
        errors.append("缺少 httpx，请运行: pip install httpx")

    # Stata 环境（非阻断性警告）
    import shutil
    import os
    stata_found = False
    candidates = [
        "StataMP-64", "StataSE-64", "Stata-64", "stata-mp", "stata-se", "stata", "StataMP-64.exe", "stata.exe",
        r"C:\Program Files\StataNow19\StataMP-64.exe"
    ]
    for cmd in candidates:
        if shutil.which(cmd) or os.path.exists(cmd):
            stata_found = True
            break
    if not stata_found:
        warnings.append("未找到 Stata 批处理执行程序 — 数据获取和分析阶段将跳过 Stata 执行")

    # API 配置
    from config import UNIFIED_API_KEY
    if not UNIFIED_API_KEY:
        errors.append("缺少 API Key，请在 config.py 中配置 UNIFIED_API_KEY")

    if errors:
        logger.error("🛑 前提条件检查失败:")
        for e in errors:
            logger.error(f"   ❌ {e}")
        logger.error("请参考 01_env_config.md 设置环境。")
        return False

    if warnings:
        for w in warnings:
            logger.warning(f"   ⚠️  {w}")

    logger.info("✅ 核心前提条件满足")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="AutoPaper 论文生产流水线 — 一键生成学术论文",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_pipeline.py 500 --domain "Commercial Banking"
  python run_pipeline.py 501 --model gpt-4.1 --contributor User
  python run_pipeline.py 500 --resume-from analysis  # 从分析阶段恢复
  python run_pipeline.py 500 --check-only  # 仅检查环境
        """
    )

    parser.add_argument(
        "paper_num", type=int, nargs="?", default=None,
        help="论文编号（如 500 → paper_0500）"
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
        "--domain", default="Commercial Banking",
        help="政策研究领域（默认: Commercial Banking）"
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

    if not args.check_only and args.paper_num is None:
        parser.error("请指定论文编号（如: python run_pipeline.py 500）")

    from config import setup_logging
    boot_logger = setup_logging("paper.boot")
    boot_logger.info("=" * 60)
    boot_logger.info("🚀 AutoPaper 论文生产流水线")
    boot_logger.info("=" * 60)

    if not check_prerequisites(boot_logger):
        sys.exit(1)

    if args.check_only:
        boot_logger.info("✅ 环境检查完成。使用 --help 查看运行选项。")
        sys.exit(0)


    # ---- 启动流水线 ----
    from config import setup_logging
    logger = setup_logging("paper.main")
    
    from agent_orchestrator import PaperPipeline

    paper_id = f"paper_{args.paper_num:04d}"

    logger.info(f"📝 论文: {paper_id} v{args.version}")
    logger.info(f"🤖 模型: {args.model}")
    logger.info(f"👤 贡献者: {args.contributor}")
    logger.info(f"📚 领域: {args.domain}")
    if args.resume_from:
        logger.info(f"🔄 从阶段恢复: {args.resume_from}")

    pipeline = PaperPipeline(
        paper_id=paper_id,
        version=args.version,
        model_key=args.model,
        contributor=args.contributor,
        policy_domain=args.domain,
    )

    success = pipeline.run(start_from=args.resume_from)

    if success:
        logger.info("=" * 60)
        logger.info("🎉 论文生成完成！")
        logger.info("=" * 60)
        logger.info(f"📂 论文目录: {pipeline.paper_dir}")
        logger.info(f"📄 论文文件: {pipeline.paper_dir / 'paper.md'}")
        logger.info(f"📊 分析结果: {pipeline.paper_dir / 'data' / 'main_results_summary.csv'}")
        logger.info(f"🔍 质量报告: {pipeline.paper_dir / 'scan_report.json'}")
    else:
        logger.error("❌ 流水线运行失败。检查日志获取详细信息。")
        logger.error("   使用 --resume-from <stage> 从失败阶段恢复。")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
