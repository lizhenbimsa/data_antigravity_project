"""15_article_policy_alignment.py — DEPRECATED CLI shim (Phase 2a).

Body migrated to ``news_process.pipeline.filtering.policy_alignment:main`` during
Phase 2a's atomic reflection-purge migration. The historical contract
``python 15_article_policy_alignment.py`` is preserved by this thin shim.

External tooling should migrate to:
    python -m news_process.pipeline.filtering.policy_alignment

Slated for removal in v2.0.
"""

import pathlib
import sys

# Inject project parent so ``import news_process`` resolves regardless of cwd.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.filtering.policy_alignment import main
    main()
