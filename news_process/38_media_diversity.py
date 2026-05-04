"""38_media_diversity.py — DEPRECATED CLI shim (Phase 7b).

Body migrated to ``news_process.validation.media_diversity:main`` during
Phase 7b.  The historical contract ``python 38_media_diversity.py`` is
preserved by this thin shim; orchestrators continue to invoke it as a
subprocess.

External tooling should migrate to:
    python -m news_process.validation.media_diversity

Slated for removal in v3.0.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.validation.media_diversity import main
    main()
