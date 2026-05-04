"""34_tone_validation.py — DEPRECATED CLI shim (Phase 7b).

Body migrated to ``news_process.validation.tone_validation:main`` during
Phase 7b.  The historical contract ``python 34_tone_validation.py`` is
preserved by this thin shim; orchestrators continue to invoke it as a
subprocess.

External tooling should migrate to:
    python -m news_process.validation.tone_validation

Slated for removal in v3.0.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.validation.tone_validation import main
    main()
