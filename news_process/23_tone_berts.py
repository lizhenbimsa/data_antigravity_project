"""23_tone_berts.py — DEPRECATED CLI shim (Phase 7a-6).

Body migrated to ``news_process.pipeline.sentiment.tone_berts:main`` during
Phase 7a-6.  The historical contract ``python 23_tone_berts.py`` is preserved
by this thin shim; orchestrators continue to invoke it as a subprocess.

External tooling should migrate to:
    python -m news_process.pipeline.sentiment.tone_berts

Slated for removal in v3.0.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.sentiment.tone_berts import main
    main()
