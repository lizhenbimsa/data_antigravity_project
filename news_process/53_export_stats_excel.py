"""53_export_stats_excel.py — DEPRECATED CLI shim (Phase 1.4b pilot).

The canonical body has been relocated to
``news_process.pipeline.audit.stats_excel:main`` during Phase 1's body-migration
pilot.  This file remains as a backwards-compatible CLI entrypoint so that the
historical contract ``python 53_export_stats_excel.py`` keeps working.

External tooling should migrate to either:
    python -m news_process.pipeline.audit.stats_excel
or (Phase 3+):
    python -m news_process.cli run --target paper:bank_fintech_tone

This shim is slated for removal in v2.0.
"""

import pathlib
import sys

# Inject project parent on sys.path so that ``import news_process`` works
# regardless of cwd.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.stats_excel import main
    main()
