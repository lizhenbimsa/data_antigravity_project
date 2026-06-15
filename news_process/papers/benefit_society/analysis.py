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
    parser.add_argument('--stage',
                        choices=['pipeline', 'tables', 'figures', 'all',
                                 'robustness_stage_a'],  # V2.0 plan Round 9
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
        _LOGGER.info("  [OK] Table 1 -> %s", out)
        for label, builder in [
            ('Table 2 (main M1-M6)', tables.build_table2_main),
            ('Table 3 (mechanism)', tables.build_table3_mechanism),
            ('Table 4 (heterogeneity exploratory)', tables.build_table4_heterogeneity),
            ('Table 5 (robustness)', tables.build_table5_robustness),
            ('Table 8b (shrinkage ctx dual)', tables.build_table_8b_shrinkage_dual),
            ('Table A1 (inter-track agreement)', tables.build_table_a1_inter_track_kappa),
            ('Table A2 (dual-track switch)', tables.build_table_a2_attitude_track_switch),
        ]:
            try:
                df = builder(pc)
                _LOGGER.info("  [OK] %s parsed: %d x %d", label, df.shape[0], df.shape[1])
            except FileNotFoundError as e:
                _LOGGER.warning("  [SKIP] %s (run Stata first): %s", label, e)

    if args.stage in ('figures', 'all'):
        from news_process.papers.benefit_society import figures
        try:
            out = figures.plot_benefit_distribution(pc)
            _LOGGER.info("  [OK] Figure 1 -> %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  [SKIP] Figure 1 (missing pipeline output): %s", e)

    # V2.0 J-L-M 2026 稳健性对齐 Stage A (Round 9)
    if args.stage == 'robustness_stage_a':
        from news_process.papers.benefit_society import figures, tables
        _LOGGER.info("Stage A — V2.0 J-L-M 2026 robustness alignment")
        for label, builder in [
            ('Table A9 (External Validation / G4)', tables.build_table_a9_external_validation),
            ('Table A10 (Placebo Business-Lines / S1)', tables.build_table_a10_placebo),
            ('Table A11 (Anchor Alt Family / A2)', tables.build_table_a11_anchor_alt),
        ]:
            try:
                df = builder(pc)
                _LOGGER.info("  [OK] %s: %d x %d", label, df.shape[0], df.shape[1])
            except FileNotFoundError as e:
                _LOGGER.warning("  [SKIP] %s (run Stata 22/23/24 first): %s",
                                label, e)
        # C1 子抽样置信区间图 + A2 placebo 对照条形图
        for label, fn in [
            ('Figure 1 with CI (C1)', figures.plot_benefit_distribution_with_subsampling_ci),
            ('Figure A2 placebo comparison (S1)', figures.plot_placebo_comparison),
        ]:
            try:
                out = fn(pc)
                _LOGGER.info("  [OK] %s -> %s", label, out)
            except FileNotFoundError as e:
                _LOGGER.warning("  [SKIP] %s (depends on Stata first): %s", label, e)

        # Figure 2 三轨 (full/ctx/ss) coefplot (PDF + PNG) 由 Stata 模板
        # 31_figure2_coefplot_dual.do 生成 (ss 列来自 stage 21 ss 情感轨, 缺失时
        # capture confirm 优雅降级为 full/ctx 6 根) — Python 侧只做存在性检查。
        # 文件名 *_dual 沿用历史命名 (lineage 兼容)。
        fig2_pdf = pc.output_dir / 'figures' / 'figure2_coefplot_dual.pdf'
        if fig2_pdf.exists():
            _LOGGER.info("  [OK] Figure 2 -> %s", fig2_pdf)
        else:
            _LOGGER.warning("  [SKIP] Figure 2 (run Stata 31_figure2_coefplot_dual.do first)")

    return 0


if __name__ == '__main__':
    sys.exit(main())
