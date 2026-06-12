"""``news_process.papers._common.pipeline_runner.run_main_pipeline`` 的测试。

quality-hardening Round 16 (2026-05-27): pipeline_runner.py 50% → 100%.
覆盖 Phase 9b 引入的薄 bridge (run_main_pipeline → run_pipeline_function.run_pipeline).
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def test_run_main_pipeline_delegates_to_run_pipeline_function():
    """Bridge 应导入 run_pipeline_function.run_pipeline 并 zero-arg 调用 (lines 29-30)."""
    # Patch 真 run_pipeline 避免实际触发 pipeline (会读 config / setup logging
    # / 跑 stages). 这里只验证桥接契约.
    with patch('news_process.run_pipeline_function.run_pipeline') as mock_run:
        from news_process.papers._common.pipeline_runner import run_main_pipeline
        run_main_pipeline()
        mock_run.assert_called_once_with()


def test_run_main_pipeline_returns_none():
    """Public API 契约: 返回 None (Phase 9b bridge invariant)."""
    with patch('news_process.run_pipeline_function.run_pipeline',
               return_value=None):
        from news_process.papers._common.pipeline_runner import run_main_pipeline
        result = run_main_pipeline()
        assert result is None
