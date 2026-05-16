"""news_process.papers.bank_fintech_substance.analysis — P3 CLI 入口."""

from __future__ import annotations

import argparse
import logging
import sys

from news_process.core.dag import STAGES_MAIN
from news_process.papers._common import get_paper_config, run_main_pipeline

STAGES = list(STAGES_MAIN)

_LOGGER = logging.getLogger('papers.bank_fintech_substance.analysis')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.papers.bank_fintech_substance.analysis',
        description='P3 Bank Fintech Substance — W&Z 1994/1998 ASQ substantive vs symbolic.',
    )
    parser.add_argument('--stage', choices=['pipeline', 'tables', 'figures', 'all'],
                        default='all')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(name)s] %(levelname)s %(message)s')

    pc = get_paper_config('bank_fintech_substance')
    _LOGGER.info("Paper:        %s", pc.paper_id)
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
        from news_process.papers.bank_fintech_substance import tables
        try:
            out = tables.write_table1(pc)
            _LOGGER.info("  [OK] Table 1 -> %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  [SKIP] Table 1 (run pipeline first): %s", e)

    if args.stage in ('figures', 'all'):
        from news_process.papers.bank_fintech_substance import figures
        try:
            out = figures.plot_substantiveness_distribution(pc)
            _LOGGER.info("  [OK] Figure 1 -> %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  [SKIP] Figure 1 (missing pipeline output): %s", e)

    return 0


if __name__ == '__main__':
    sys.exit(main())
