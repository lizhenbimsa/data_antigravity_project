"""45_panel_export_main.py — DEPRECATED CLI shim (Phase 2a).

Body migrated to ``news_process.pipeline.panel.runner:main`` during Phase 2a's
atomic reflection-purge migration (9 importlib reflections removed).
Phase 2b will further split runner.py into runner+extras+export.

The historical contract ``python 45_panel_export_main.py`` is preserved by
this thin shim.

External tooling should migrate to:
    python -m news_process.pipeline.panel.runner

Slated for removal in v2.0.
"""

import pathlib
import sys

# Inject project parent so ``import news_process`` resolves regardless of cwd.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.panel.runner import main
    main()
