"""14_fintech_intensity.py — DEPRECATED CLI shim (Phase 7a-3).

Body migrated to ``news_process.pipeline.filtering.fintech_intensity:main`` during
Phase 7a-3.  The historical contract ``python 14_fintech_intensity.py`` is preserved
by this thin shim; orchestrators continue to invoke it as a subprocess.

External tooling should migrate to:
    python -m news_process.pipeline.filtering.fintech_intensity

Slated for removal in v3.0.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.filtering.fintech_intensity import main
    main()
