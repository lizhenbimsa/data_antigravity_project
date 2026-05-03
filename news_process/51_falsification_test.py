"""51_falsification_test.py — DEPRECATED CLI shim (Phase 2c).

Body migrated to ``news_process.pipeline.falsification.controls:main`` during
Phase 2c.  The historical contract ``python 51_falsification_test.py`` is
preserved by this thin shim.

Phase 2c-2 follow-up will extract the shared bank-year panel-assembly logic
(currently inlined inside this body) into
``news_process.pipeline.panel.falsification_helpers``, leaving
``controls.py`` with only control-variable construction.

External tooling should migrate to:
    python -m news_process.pipeline.falsification.controls

Slated for removal in v2.0.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.falsification.controls import main
    main()
