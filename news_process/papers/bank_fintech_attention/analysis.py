"""news_process.papers.bank_fintech_attention.analysis — P2 CLI 入口.

CLI: ``python -m news_process.papers.bank_fintech_attention.analysis [--stage ...] [--dry-run]``
"""

from __future__ import annotations

import argparse
import logging
import sys

from news_process.core.dag import STAGES_MAIN
from news_process.papers._common import get_paper_config, run_main_pipeline

STAGES = list(STAGES_MAIN)

_LOGGER = logging.getLogger('papers.bank_fintech_attention.analysis')


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog='python -m news_process.papers.bank_fintech_attention.analysis',
        # fix(omni-g-papers-misc-09, 2026-06-11): 锚点更正 — attention_index 为
        # Fang-Peress (2009 JF) extensive 覆盖; Hassan QJE 仅限 pct/density/ctx 归因
        description=('P2 Bank Fintech Attention — firm-level attention intensity '
                     '(Fang-Peress 2009 JF extensive; Hassan 2019 QJE 限 pct/density)。'),
    )
    parser.add_argument('--stage', choices=['pipeline', 'tables', 'figures', 'all'],
                        default='all')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s [%(name)s] %(levelname)s %(message)s')

    pc = get_paper_config('bank_fintech_attention')
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
        from news_process.papers.bank_fintech_attention import tables
        # metric-audit 2026-06-02 (attention_media-01): 放宽 except.
        # 缺列触发 pyarrow ArrowInvalid (非 FileNotFoundError), 原窄 except
        # 接不住 → 整体 traceback。改为 catch Exception, 单表失败仅 warning
        # 跳过, 不阻塞其余阶段 / 不抛非零退出码。
        try:
            out = tables.write_table1(pc)
            _LOGGER.info("  [OK] Table 1 -> %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  [SKIP] Table 1 (run pipeline first): %s", e)
        except Exception as e:  # noqa: BLE001 — 单表失败不应使整个 CLI 崩
            _LOGGER.warning("  [SKIP] Table 1 (生成失败, 已优雅跳过): %s", e)

    if args.stage in ('figures', 'all'):
        from news_process.papers.bank_fintech_attention import figures
        try:
            out = figures.plot_attention_distribution(pc)
            if out is None:
                _LOGGER.warning("  [SKIP] Figure 1 (注意力强度列缺失或为空)")
            else:
                _LOGGER.info("  [OK] Figure 1 -> %s", out)
        except FileNotFoundError as e:
            _LOGGER.warning("  [SKIP] Figure 1 (missing pipeline output): %s", e)
        except Exception as e:  # noqa: BLE001 — 单图失败不应使整个 CLI 崩
            _LOGGER.warning("  [SKIP] Figure 1 (生成失败, 已优雅跳过): %s", e)

    return 0


if __name__ == '__main__':
    sys.exit(main())
