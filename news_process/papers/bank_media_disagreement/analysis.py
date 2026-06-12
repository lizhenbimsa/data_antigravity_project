"""news_process.papers.bank_media_disagreement.analysis — 第 10 篇 CLI 入口 (2026-06-01 wiring).

CLI: ``python -m news_process.papers.bank_media_disagreement.analysis [--stage ...] [--dry-run]``
或经统一调度器 ``python -m news_process.run_paper bank_media_disagreement``。

状态 (provisional): paper_spec.yaml 已 frozen + 通过 schema 校验, 本 analysis 入口
符合 Phase-3 契约 (main(argv) + STAGES), 故可被 run_paper 调度。treatment
``cross_outlet_tone_variance_full`` 待 M2-M3 新建 (V4 R3); tables/figures 为占位骨架,
主回归 (Cookson-Niessner 2020 JF disagreement; 勘误: 旧注释误标 RFS) 待 M5 填实。
"""

from __future__ import annotations

import argparse
import logging
import sys

from news_process.core.dag import STAGES_MAIN
from news_process.papers._common import get_paper_config, run_main_pipeline

STAGES = list(STAGES_MAIN)

_LOGGER = logging.getLogger('papers.bank_media_disagreement.analysis')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.papers.bank_media_disagreement.analysis',
        description='第10篇 Bank Media Disagreement — cross-outlet tone variance (Cookson-Niessner 2020; provisional).',
    )
    parser.add_argument('--stage', choices=['pipeline', 'tables', 'figures', 'all'],
                        default='all')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(name)s] %(levelname)s %(message)s')

    pc = get_paper_config('bank_media_disagreement')
    _LOGGER.info("Paper:        %s (provisional — tables/figures 占位)", pc.paper_id)
    _LOGGER.info("Project root: %s", pc.project_root)
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
        from news_process.papers.bank_media_disagreement import tables
        try:
            out = tables.write_table1(pc)
            _LOGGER.info("  [OK] Table 1 -> %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  [SKIP] Table 1 (run pipeline first): %s", e)

    if args.stage in ('figures', 'all'):
        from news_process.papers.bank_media_disagreement import figures
        try:
            out = figures.plot_disagreement_distribution(pc)
            _LOGGER.info("  [OK] Figure 1 -> %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  [SKIP] Figure 1 (missing pipeline output): %s", e)

    return 0


if __name__ == '__main__':
    sys.exit(main())
