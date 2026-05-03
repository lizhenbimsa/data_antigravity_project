"""news_process.papers.bank_fintech_tone.analysis — 主线论文 CLI 入口.

CLI 用法
--------
通过 ``python -m news_process.papers.bank_fintech_tone.analysis`` 调用,
或经 Phase 3e 的统一调度器 ``python -m news_process.run_paper bank_fintech_tone``。

支持的阶段
----------
``--stage`` 控制执行范围:
    pipeline : 运行整套数据流水线 (相当于 ``run_pipeline_function.py``)
    tables   : 仅生成本论文的表格 (Table 1, ...)
    figures  : 仅生成本论文的图表 (Figure 1, ...)
    all      : pipeline → tables → figures (默认)

设计说明
--------
- 不重复实现 pipeline 调度: 直接调用既有的 ``run_pipeline_function:run_pipeline``。
   这保证了 "主管线 = 主论文" 的语义并消除双源风险。
- ``--dry-run`` 不真正调起 pipeline, 只打印 DAG 与计划; 用于冒烟测试。
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from news_process.papers._common import get_paper_config
from news_process.papers.bank_fintech_tone.dag import STAGES


_LOGGER = logging.getLogger('papers.bank_fintech_tone.analysis')


def _run_pipeline_via_existing_orchestrator() -> None:
    """调用 ``run_pipeline_function.run_pipeline()``.

    用 ``importlib`` 而非顶层 import: ``run_pipeline_function`` 不是 package
    一部分 (它在 ``news_process/`` 根, 与 paper 包同级), 所以走 spec 加载更
    safe — 即使根脚本加新依赖也不影响 ``news_process.papers.*`` 的可
    importability (例如轻量调用 ``run_paper.py --stage tables`` 时)。
    """
    import importlib.util

    project_root = Path(__file__).resolve().parents[3]  # news_process/
    script_path = project_root / 'run_pipeline_function.py'
    if not script_path.exists():
        raise FileNotFoundError(
            f"未找到 run_pipeline_function.py: {script_path}"
        )

    spec = importlib.util.spec_from_file_location(
        '_bft_run_pipeline_module', script_path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.run_pipeline()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.papers.bank_fintech_tone.analysis',
        description='Bank-FinTech-Tone (主线论文) — 数据管线 + 表/图生成.',
    )
    parser.add_argument(
        '--stage', choices=['pipeline', 'tables', 'figures', 'all'],
        default='all', help='要执行的阶段 (默认: all)',
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='不真正运行 pipeline / 表/图; 仅打印计划, 用于冒烟测试。',
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(name)s] %(levelname)s %(message)s',
    )

    pc = get_paper_config('bank_fintech_tone')
    _LOGGER.info("Paper:        %s", pc.paper_id)
    _LOGGER.info("Project root: %s", pc.project_root)
    _LOGGER.info("Panel dir:    %s", pc.panel_dir)
    _LOGGER.info("Output dir:   %s", pc.output_dir)
    _LOGGER.info("DAG length:   %d stages", len(STAGES))

    if args.dry_run:
        _LOGGER.info("[dry-run] 计划阶段: %s", args.stage)
        for s in STAGES:
            _LOGGER.info("  - %s (%s)", s.script, s.name)
        return 0

    if args.stage in ('pipeline', 'all'):
        _LOGGER.info("阶段 pipeline: 调用 run_pipeline_function.run_pipeline()")
        _run_pipeline_via_existing_orchestrator()

    if args.stage in ('tables', 'all'):
        _LOGGER.info("阶段 tables: 生成主线论文表格")
        from news_process.papers.bank_fintech_tone import tables
        out = tables.write_table1(pc)
        _LOGGER.info("  ✅ Table 1 → %s", out)

    if args.stage in ('figures', 'all'):
        _LOGGER.info("阶段 figures: 生成主线论文图表")
        from news_process.papers.bank_fintech_tone import figures
        try:
            out = figures.plot_news_coverage_distribution(pc)
            _LOGGER.info("  ✅ Figure 1 → %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning(
                "  ⚠ Figure 1 跳过 (缺少 pipeline 输出): %s", e
            )

    return 0


if __name__ == '__main__':
    sys.exit(main())
