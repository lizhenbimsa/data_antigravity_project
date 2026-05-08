"""news_process.papers.brokerage_network.analysis — 衍生论文 CLI 入口."""

from __future__ import annotations

import argparse
import logging
import sys

from news_process.papers._common import get_paper_config, run_main_pipeline
from news_process.core.dag import STAGES_MAIN

STAGES = list(STAGES_MAIN)  # Phase 9a: 原 papers.brokerage_network.dag 已删, list() 保持原拷贝语义

_LOGGER = logging.getLogger('papers.brokerage_network.analysis')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.papers.brokerage_network.analysis',
        description='Brokerage-Network — 信息经纪网络与企业表现 (Han et al. 2024).',
    )
    parser.add_argument('--stage', choices=['pipeline', 'tables', 'figures', 'all'],
                        default='all')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(name)s] %(levelname)s %(message)s')
    pc = get_paper_config('brokerage_network')
    _LOGGER.info("Paper:        %s", pc.paper_id)
    _LOGGER.info("Output dir:   %s", pc.output_dir)
    _LOGGER.info("DAG length:   %d stages", len(STAGES))

    if args.dry_run:
        _LOGGER.info("[dry-run] 计划阶段: %s", args.stage)
        for s in STAGES:
            _LOGGER.info("  - %s (%s)", s.script, s.name)
        return 0

    if args.stage in ('pipeline', 'all'):
        run_main_pipeline()
    if args.stage in ('tables', 'all'):
        from news_process.papers.brokerage_network import tables
        out = tables.write_table1(pc)
        _LOGGER.info("  ✅ Table 1 → %s", out)
    if args.stage in ('figures', 'all'):
        from news_process.papers.brokerage_network import figures
        try:
            out = figures.plot_brokerage_centrality_distribution(pc)
            _LOGGER.info("  ✅ Figure 1 → %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  ⚠ Figure 1 跳过: %s", e)
    return 0


if __name__ == '__main__':
    sys.exit(main())
