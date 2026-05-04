"""21_tone_llms.py — DEPRECATED CLI shim (Phase 7a-4).

Body migrated to ``news_process.pipeline.sentiment.tone_llms:main`` during
Phase 7a-4.  The historical contract ``python 21_tone_llms.py`` is preserved
by this thin shim; orchestrators continue to invoke it as a subprocess.

External tooling should migrate to:
    python -m news_process.pipeline.sentiment.tone_llms

Slated for removal in v3.0.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.sentiment.tone_llms import main
    main()
