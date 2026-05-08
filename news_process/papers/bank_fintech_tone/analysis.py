"""news_process.papers.bank_fintech_tone.analysis — 主线论文 CLI 入口.

CLI 用法
--------
通过 ``python -m news_process.papers.bank_fintech_tone.analysis`` 调用,
或经 Phase 3e 的统一调度器 ``python -m news_process.run_paper news_process``。

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

from news_process.papers._common import get_paper_config, run_main_pipeline
from news_process.core.dag import STAGES_MAIN

STAGES = list(STAGES_MAIN)  # Phase 9a: 原 papers.bank_fintech_tone.dag 已删, list() 保持原拷贝语义


_LOGGER = logging.getLogger('papers.news_process.analysis')


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
        run_main_pipeline()

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
