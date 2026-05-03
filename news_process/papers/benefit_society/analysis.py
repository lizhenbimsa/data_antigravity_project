"""news_process.papers.benefit_society.analysis — 衍生论文 CLI 入口.

CLI: ``python -m news_process.papers.benefit_society.analysis [--stage ...] [--dry-run]``
"""

from __future__ import annotations

import argparse
import logging
import sys

from news_process.papers._common import get_paper_config
from news_process.papers.benefit_society.dag import STAGES

_LOGGER = logging.getLogger('papers.benefit_society.analysis')


def _run_pipeline_via_existing_orchestrator() -> None:
    """复用 ``run_pipeline_function:run_pipeline`` (与主线一致)."""
    import importlib.util
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[3]
    script_path = project_root / 'run_pipeline_function.py'
    if not script_path.exists():
        raise FileNotFoundError(f"未找到 run_pipeline_function.py: {script_path}")
    spec = importlib.util.spec_from_file_location(
        '_bs_run_pipeline_module', script_path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    mod.run_pipeline()


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
        _run_pipeline_via_existing_orchestrator()

    if args.stage in ('tables', 'all'):
        from news_process.papers.benefit_society import tables
        out = tables.write_table1(pc)
        _LOGGER.info("  ✅ Table 1 → %s", out)

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
