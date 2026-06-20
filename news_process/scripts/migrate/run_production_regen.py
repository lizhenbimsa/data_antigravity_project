#!/usr/bin/env python
"""生产/golden 协调式重生驱动 (REPRO-1 闭合) — 配套 PRODUCTION_REGEN_SOP_2026-06-15.md。

把审计 PROJECT_REAUDIT_TOPTIER_T18 的 REPRO-1 (P1) 闭合工序脚本化: preflight 守卫 → 重建
面板 (stage 40/46) → 重生 golden → 复现闸门转绿。**默认 --dry-run** (只打印不执行), 须显式
--execute 才真跑。设计为在【银行财务 outcome + IV enrichment 列接入到盘后】的一次受控 run 内执行。

铁律 (见 SOP §前置): 勿删 _llm_cache.db; 全程 NEWS_PROCESS_LLM_OFFLINE=1; PYTHONHASHSEED=0
(core/stage.py 已强制); prompt v8 冻结; 单一干净工作树。

用法:
    python scripts/migrate/run_production_regen.py            # dry-run (推荐先看)
    python scripts/migrate/run_production_regen.py --execute  # 真执行 (受控环境)
    python scripts/migrate/run_production_regen.py --execute --skip-stages  # 仅重生 golden + 复验
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

_PKG_ROOT = Path(__file__).resolve().parents[2]  # news_process/ (scripts/migrate/<file>)
_DATA = _PKG_ROOT / "data" / "processed"
_CACHE_DB = _DATA / "_llm_cache.db"
_GOLDEN = _PKG_ROOT / "tests" / "fixtures" / "golden_panel_v0.json"

# 接入后须出现的主财务 outcome 列 (任一论文主 DV); preflight 据此判断"财务数据是否已到盘"。
_FINANCIAL_OUTCOME_COLS = [
    "roa", "funding_cost", "cost_income_ratio_change_3yr",
    "citation_weighted_patent", "m_and_a_fintech", "tobin_q", "z_score",
]


def _run(cmd: list[str], *, execute: bool, env: dict | None = None) -> int:
    """打印命令; execute 时真跑并返回退出码, 否则返回 0 (dry-run)。"""
    print(f"    $ {' '.join(cmd)}")
    if not execute:
        return 0
    full_env = {**os.environ, **(env or {})}
    cp = subprocess.run(cmd, cwd=str(_PKG_ROOT), env=full_env)
    return cp.returncode


def preflight() -> list[str]:
    """返回阻断性问题清单 (空 = 通过)。"""
    problems: list[str] = []
    print("[preflight] 守卫检查")

    # 1. _llm_cache.db 在场 (golden 确定性锚点)
    if _CACHE_DB.exists():
        mb = _CACHE_DB.stat().st_size / 1024 / 1024
        print(f"   [OK] _llm_cache.db 在场 ({mb:.0f} MB) — 勿删")
    else:
        problems.append("_llm_cache.db 缺失 → stage 21 会须线上付费重跑 (确认这是你要的)")

    # 2. 财务 outcome 列是否已接入 (REPRO-1 的真正前置)
    try:
        import pandas as pd  # noqa: PLC0415
        panel_path = _DATA / "40_panel_yearly.parquet"
        if panel_path.exists():
            cols = set(pd.read_parquet(panel_path).columns)
            present = [c for c in _FINANCIAL_OUTCOME_COLS if c in cols]
            missing = [c for c in _FINANCIAL_OUTCOME_COLS if c not in cols]
            if present:
                print(f"   [OK] 财务 outcome 列已接入: {present}")
            if missing:
                problems.append(
                    f"财务 outcome 列未到盘: {missing} → 先做 SOP 步骤0 (接入财务面板 + 统一 roa 大小写), "
                    "否则重生只产 sentinel 占位 (主回归仍 capture-confirm 跳过)")
        else:
            problems.append("40_panel_yearly.parquet 不在盘 → 先跑完整 pipeline 或 stage 40")
    except ImportError:
        problems.append("pandas 未装 (pip install -e .)")

    # 3. 确定性环境
    if os.environ.get("PYTHONHASHSEED") not in (None, "0"):
        problems.append(f"PYTHONHASHSEED={os.environ.get('PYTHONHASHSEED')} != 0 (core/stage.py 会对子进程强制 0, 但本进程建议也设 0)")
    else:
        print("   [OK] PYTHONHASHSEED 未设或=0 (stage 子进程会强制 0)")

    # 4. 工作树是否干净 (避免误 bless 并行会话产物)
    try:
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=str(_PKG_ROOT),
                               capture_output=True, text=True).stdout.strip()
        n_dirty = len([ln for ln in dirty.splitlines() if ln.strip()])
        if n_dirty > 0:
            print(f"   [WARN] 工作树有 {n_dirty} 处未提交改动 — 确认无并行会话中间产物会被误 bless")
    except Exception:
        pass

    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="生产/golden 协调式重生驱动 (REPRO-1)")
    ap.add_argument("--execute", action="store_true", help="真执行 (默认 dry-run 只打印)")
    ap.add_argument("--skip-stages", action="store_true", help="跳过 stage 40/46, 仅重生 golden + 复验")
    args = ap.parse_args()
    execute = args.execute

    print("=" * 72)
    print(f"生产/golden 重生驱动  mode={'EXECUTE' if execute else 'DRY-RUN'}")
    print("配套: scripts/migrate/PRODUCTION_REGEN_SOP_2026-06-15.md")
    print("=" * 72)

    problems = preflight()
    if problems:
        print("\n[STOP] preflight 阻断 (修复后重跑):")
        for p in problems:
            print(f"   - {p}")
        if execute:
            print("\n执行模式下 preflight 失败 → 中止, 不重生。")
            return 1
        print("\n(dry-run: 仅列出; 真执行前须先消除上述阻断)")

    det_env = {"NEWS_PROCESS_LLM_OFFLINE": "1", "PYTHONHASHSEED": "0"}

    print("\n[步骤 1] 重建面板 (stage 40 → 46) — 离线确定 ($0, 缓存全命中)")
    if args.skip_stages:
        print("    (--skip-stages: 跳过)")
    else:
        rc = _run([sys.executable, "40_panel_export_main.py"], execute=execute, env=det_env)
        if execute and rc:
            print(f"    [STOP] stage 40 退出码 {rc}"); return rc
        rc = _run([sys.executable, "46_stata_export.py"], execute=execute, env=det_env)
        if execute and rc:
            print(f"    [STOP] stage 46 退出码 {rc}"); return rc

    print("\n[步骤 2] 重生 golden snapshot")
    rc = _run([sys.executable, "scripts/migrate/generate_golden_snapshot.py"], execute=execute, env=det_env)
    if execute and rc:
        print(f"    [STOP] generate_golden_snapshot 退出码 {rc}"); return rc

    print("\n[步骤 3] 复现闸门转绿")
    rc = _run([sys.executable, "-m", "pytest", "tests/integration/test_panel_reproducibility.py",
               "tests/integration/test_dag_consistency.py", "-q"], execute=execute, env=det_env)
    if execute and rc:
        print(f"    [STOP] 复现/DAG 测试失败 (退出码 {rc}) — 见 SOP §步骤3 (BLAS-FP 容差) 与 §可选代码改动")
        return rc

    print("\n[步骤 4] 同 commit freeze (人工)")
    print("    面板(.parquet/.dta/codebook) + golden + 代码 同一 commit; 投稿前打 archival tag。")
    print("    此后禁止单独重跑上游 stage 而不连带重建下游 + 重生 golden。")

    print("\n" + "=" * 72)
    print("完成。" if execute else "DRY-RUN 结束 (未改任何文件)。先消除 preflight 阻断, 再 --execute。")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
