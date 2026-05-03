"""news_process.orchestration — single source of stage execution and DAG composition.

- ``stage_executor.py`` (Phase 3): subprocess-isolated stage runner.
- ``dag_builder.py`` (Phase 3): merges ``core.dag.STAGES_*`` with per-paper DAGs.
- ``progress.py`` (Phase 3): timing/summary statistics.
"""
