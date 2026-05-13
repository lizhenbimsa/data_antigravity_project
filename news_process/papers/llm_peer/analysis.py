"""news_process.papers.llm_peer.analysis — 衍生论文 CLI 入口."""

from __future__ import annotations

import argparse
import logging
import sys

from news_process.core.dag import STAGES_MAIN
from news_process.papers._common import get_paper_config, run_main_pipeline

STAGES = list(STAGES_MAIN)  # Phase 9a: 原 papers.llm_peer.dag 已删, list() 保持原拷贝语义

_LOGGER = logging.getLogger('papers.llm_peer.analysis')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.papers.llm_peer.analysis',
        description='LLM-Peer — LLM 生成的同业竞争 IV (Cao et al. 2025).',
    )
    parser.add_argument('--stage', choices=['pipeline', 'tables', 'figures', 'all'],
                        default='all')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(name)s] %(levelname)s %(message)s')
    pc = get_paper_config('llm_peer')
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
        from news_process.papers.llm_peer import tables
        out = tables.write_table1(pc)
        _LOGGER.info("  ✅ Table 1 → %s", out)
    if args.stage in ('figures', 'all'):
        from news_process.papers.llm_peer import figures
        try:
            out = figures.plot_cutoff_sensitivity(pc)
            _LOGGER.info("  ✅ Figure 1 → %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  ⚠ Figure 1 跳过: %s", e)
    return 0


if __name__ == '__main__':
    sys.exit(main())
