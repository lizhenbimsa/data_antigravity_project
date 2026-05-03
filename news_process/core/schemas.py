"""news_process.core.schemas — column contracts + OUTPUT_REGISTRY (Phase 2 deliverable).

Phase 1: placeholder.  Phase 2d will populate ``OUTPUT_REGISTRY`` here as the
single source of stage→outputs mapping (consumed by both stage runners for
their write paths and by the orchestrator for stale-data pre-cleanup).

Phase 2 will also add pydantic schema validation for the seven domain YAML
files produced by Phase 2f's config split.
"""

from __future__ import annotations


# Phase 2d will fill this in.
OUTPUT_REGISTRY: dict[str, list[str]] = {}
