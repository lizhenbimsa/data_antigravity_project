"""52_stata_data_audit.py — DEPRECATED CLI shim (Phase 7a-8).

Body migrated to ``news_process.pipeline.audit.stata_audit:main`` during
Phase 7a-8.  The historical contract ``python 52_stata_data_audit.py`` is
preserved by this thin shim; orchestrators continue to invoke it as a
subprocess.

External tooling should migrate to:
    python -m news_process.pipeline.audit.stata_audit

Slated for removal in v3.0.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.stata_audit import main
    main()
