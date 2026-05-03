"""00_preprocessing.py — DEPRECATED CLI shim (Phase 2c).

Body migrated to ``news_process.pipeline.preprocess.runner:main`` during
Phase 2c.  The historical contract ``python 00_preprocessing.py`` is
preserved by this thin shim.

Phase 2c-2 follow-up will further split the runner into
``load/normalize/filter/dedup`` sub-modules under
``news_process.pipeline.preprocess``.

External tooling should migrate to:
    python -m news_process.pipeline.preprocess.runner

Slated for removal in v2.0.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.preprocess.runner import main
    main()
