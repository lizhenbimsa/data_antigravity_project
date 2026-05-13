"""news_process package-root conftest (V4 T0.2).

Prevents pytest from scanning data/ when launched from the news_process/
subdirectory (where the parent pyproject.toml's testpaths setting may not
apply consistently). Without this, stray files like
data/processed/test_*.txt cause UnicodeDecodeError during collection.

Coexists with tests/conftest.py — pytest auto-loads both per its hierarchical
conftest discovery; they do not conflict.
"""

# Relative to this conftest's directory (news_process/), exclude data/* fully.
collect_ignore_glob = ["data/*"]
