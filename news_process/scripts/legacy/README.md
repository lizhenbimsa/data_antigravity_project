# scripts/legacy/

Modules archived from `news_process/utils/` during the Phase 1 refactor.

Both files are **orphans** (verified with `rg "from utils\.<name>"` returning
no non-self matches at the time of archival). They are kept here for
historical traceability but are not part of the active pipeline.

| File | Origin | Status | Reason |
|---|---|---|---|
| `extract_papers.py` | `utils/extract_papers.py` | Orphan | Zero imports across the codebase. One-off paper-PDF extractor. |
| `schema_validator.py` | `utils/schema_validator.py` | Orphan | Only its own docstring refers to `validate_schema` / `load_schemas`. No call sites. |

If a future need arises, port the relevant functions into `news_process/core/`
(or a new sub-package) rather than reviving the legacy `utils/` path.
