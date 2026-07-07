"""银企共现面板流水线 orchestrator (COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN v34).

按硬依赖顺序串跑三步 (子进程隔离, 任一步非零退出即中断, 镜像 run_pipeline_function.py 风格):
  01 WP0 注册表对账   → config/company_bank_cooc_registry.yaml (加权引擎唯一 SSOT)
  02 WP1 主面板构建   → company_listed_bank/data/company_bank_cooc_panel.{dta,parquet} + codebook + pair 长表
  03 WP5 七权源互验   → company_listed_bank/data/ 七替代权长表 + 七权面板 ×7 + 互验报告

日志: 本 orchestrator 与三步各写 company_listed_bank/logs/<stem>.log (格式/覆盖语义同主管道
core/logging.py::setup_logging); 数据产物统一落 company_listed_bank/data/ (不入库)。

用法 (从 news_process/ 目录, conda base python):
  python company_listed_bank/run_pipeline.py                 # 全链 01→02→03
  python company_listed_bank/run_pipeline.py --steps 02,03   # 从 02 起 (registry 已就绪时)
  python company_listed_bank/run_pipeline.py --dry-run       # 只打印将执行的命令

⚠ 重跑 01 会重生 registry → 哈希锚变 → 须 bump
  tests/test_company_bank_cooc_registry.py::EXPECTED_REGISTRY_SHA256 并级联 02 (pair 指纹)
  → 03 (DV2 双向锁); 本 orchestrator 跑完含 01 的链后会打印该提醒。
独立派生数据流水线, 不注册 DAG (镜像 generate_company_listed_names.py 定位)。
"""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
OUT_DATA = HERE / "data"

logger = logging.getLogger("run_pipeline")
if not logger.handlers:  # console 兜底; main() 实跑时由 setup_logging 接管
    _h = logging.StreamHandler(sys.stdout)
    _h.setFormatter(logging.Formatter("[pipeline] %(levelname)s %(message)s"))
    logger.addHandler(_h)
    logger.setLevel(logging.INFO)


def _init_stage_logging() -> None:
    """接入主管道日志基建 (core/logging.py::setup_logging): 写 company_listed_bank/logs/run_pipeline.log,
    格式/每次运行覆盖/50MB rotate 与主管道各阶段日志完全一致。单文件 importlib 加载, 不引入包依赖。"""
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return  # WP-A: 测试进程绝不接管文件日志 (2026-07-07 审计: 负例测试曾首写截断覆盖生产 02 日志)
    import importlib.util
    spec = importlib.util.spec_from_file_location("_np_core_logging", REPO / "core" / "logging.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.setup_logging(Path(__file__).stem, str(HERE / "logs"))
    # setup_logging 置 propagate=False (主管道防双打惯例); 本脚本进程 root 无 handler,
    # 恢复 True 无双打副作用, 且保 pytest caplog (root handler) 可捕 — 否则负例测试调过
    # main() 后, 同会话后续 caplog 断言静默失捕 (2026-07-07 实弹)
    logging.getLogger(Path(__file__).stem).propagate = True


STEPS: list[tuple[str, str, str]] = [
    ("01", "01_build_company_bank_cooc_registry.py",
     "WP0 注册表对账 → config/company_bank_cooc_registry.yaml"),
    ("02", "02_build_company_bank_cooc_panel.py",
     "WP1 主面板 + pair 长表 + codebook"),
    ("03", "03_build_company_bank_weight_validation.py",
     "WP5 七权源 + 八权面板 ×7 + 互验报告"),
]
STEP_IDS = [s[0] for s in STEPS]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="银企共现面板流水线: 01 registry → 02 panel → 03 weights (硬依赖顺序)")
    ap.add_argument("--steps", default=",".join(STEP_IDS),
                    help="逗号分隔步骤子集 (默认全链); 顺序恒按 01→02→03, 传入序不生效")
    ap.add_argument("--dry-run", action="store_true", help="只打印将执行的命令, 不实跑")
    args = ap.parse_args(argv)
    if not args.dry_run:
        _init_stage_logging()

    wanted = {s.strip() for s in args.steps.split(",") if s.strip()}
    unknown = wanted - set(STEP_IDS)
    if unknown:
        ap.error(f"未知步骤 {sorted(unknown)} (合法: {STEP_IDS})")
    selected = [s for s in STEPS if s[0] in wanted]  # 恒按声明序执行
    if not selected:
        ap.error("--steps 为空")

    # 跳步前置自检 (fail-loud 提前于子进程闸, 报错更可读; 02/03 自身仍有权威闸)
    if "01" not in wanted and {"02", "03"} & wanted:
        reg = REPO / "config" / "company_bank_cooc_registry.yaml"
        if not reg.exists():
            logger.error("缺 %s 且未选 01 — registry 是 02/03 的唯一 SSOT", reg)
            return 1
    if "02" not in wanted and "03" in wanted:
        pairs = OUT_DATA / "_company_bank_cooc_pairs.parquet"
        if not pairs.exists():
            logger.error("缺 %s 且未选 02 — 无锚即无互验", pairs)
            return 1

    t_all = time.monotonic()
    for step_id, script, desc in selected:
        cmd = [sys.executable, "-u", str(HERE / script)]
        logger.info("%s %s", step_id, desc)
        logger.info("  $ %s", " ".join(cmd))
        if args.dry_run:
            continue
        t0 = time.monotonic()
        rc = subprocess.run(cmd, cwd=str(REPO)).returncode
        dt = time.monotonic() - t0
        if rc != 0:
            logger.error("步骤 %s 失败 (exit=%d, %.0fs) — 中断, 后续步骤未跑", step_id, rc, dt)
            return rc
        logger.info("步骤 %s 完成 (%.0fs)", step_id, dt)

    if not args.dry_run:
        logger.info("全部 %d 步完成 (%.0fs)", len(selected), time.monotonic() - t_all)
        if "01" in wanted:
            logger.warning("本次重生了 registry: 若哈希变更, 须 bump "
                           "tests/test_company_bank_cooc_registry.py::EXPECTED_REGISTRY_SHA256 "
                           "并确认 02→03 已级联 (本链若含 02/03 则已级联)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
