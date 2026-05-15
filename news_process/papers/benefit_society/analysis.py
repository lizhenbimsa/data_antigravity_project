"""news_process.papers.benefit_society.analysis — 衍生论文 CLI 入口.

CLI: ``python -m news_process.papers.benefit_society.analysis [--stage ...] [--dry-run]``
"""

from __future__ import annotations

import argparse
import logging
import sys

from news_process.core.dag import STAGES_MAIN
from news_process.papers._common import get_paper_config, run_main_pipeline

STAGES = list(STAGES_MAIN)  # Phase 9a: 原 papers.benefit_society.dag 已删, list() 保持原拷贝语义

_LOGGER = logging.getLogger('papers.benefit_society.analysis')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.papers.benefit_society.analysis',
        description='Benefit-Society — 经营效益态度投影 (Jha-Liu-Manela 2026 RFS).',
    )
    parser.add_argument('--stage', choices=['pipeline', 'tables', 'figures', 'all'],
                        default='all')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(name)s] %(levelname)s %(message)s')

    pc = get_paper_config('benefit_society')
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
        from news_process.papers.benefit_society import tables
        out = tables.write_table1(pc)
        _LOGGER.info("  ✅ Table 1 → %s", out)
        for label, builder in [
            ('Table 2 (main)', tables.build_table2_main),
            ('Table 3 (mechanism)', tables.build_table3_mechanism),
            ('Table 4 (heterogeneity)', tables.build_table4_heterogeneity),
            ('Table 5 (robustness)', tables.build_table5_robustness),
        ]:
            try:
                df = builder(pc)
                _LOGGER.info("  ✅ %s parsed: %d×%d", label, df.shape[0], df.shape[1])
            except FileNotFoundError as e:
                _LOGGER.warning("  ⚠ %s skip (run Stata first): %s", label, e)

    if args.stage in ('figures', 'all'):
        from news_process.papers.benefit_society import figures
        try:
            out = figures.plot_benefit_distribution(pc)
            _LOGGER.info("  ✅ Figure 1 → %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  ⚠ Figure 1 跳过 (缺少 pipeline 输出): %s", e)

    return 0


if __name__ == '__main__':
    sys.exit(main())
