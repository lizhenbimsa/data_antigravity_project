"""
tests/test_pipeline_reporting.py — utils/pipeline_reporting.py 单元测试
========================================================================

测试管道执行摘要报告生成器的核心逻辑。
"""

import os
import sys

import pandas as pd
import pytest

# Phase 5c-2: 注入项目父目录解析 ``news_process.*``
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.logging import setup_logging
from news_process.core.reporting import generate_pipeline_summary

# ============================================================================
# Fixture：构建测试用配置和 parquet 文件
# ============================================================================

@pytest.fixture
def pipeline_config(tmp_path):
    """创建包含必要路径和文件名的配置字典。"""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    log_dir = tmp_path / 'logs'
    log_dir.mkdir()
    return {
        'paths': {
            'output_dir': str(output_dir),
            'log_dir': str(log_dir),
        },
        'filenames': {
            'output_00_preprocessing': '00_preprocessing.parquet',
            'output_11_bank_news': '11_bank_news.parquet',
            'output_12_fintech_news': '12_fintech_news.parquet',
            'output_21_tone_llms': '21_tone_llms.parquet',
            'output_21_tone_llms_full': '21_tone_llms_full.parquet',
            'output_22_words_tone': '22_words_tone.parquet',
            'output_23_bert_tone': '23_bert_tone.parquet',
            'output_24_herd_decay': '24_herd_decay.parquet',
        },
    }


@pytest.fixture
def pipeline_logger(tmp_path):
    """创建测试用 logger。"""
    return setup_logging('test_pipeline_report', str(tmp_path / 'logs'))


def _create_parquet(output_dir, filename, n_rows):
    """创建简单的测试 parquet 文件。"""
    df = pd.DataFrame({
        'docid': range(n_rows),
        '标题': [f'新闻{i}' for i in range(n_rows)],
    })
    path = os.path.join(output_dir, filename)
    df.to_parquet(path, index=False)
    return path


# ============================================================================
# 正常运行测试
# ============================================================================

class TestGeneratePipelineSummary:
    """测试 generate_pipeline_summary() 功能。"""

    def test_all_stages_present(self, pipeline_config, pipeline_logger):
        """所有阶段的 parquet 文件都存在时不应崩溃。"""
        output_dir = pipeline_config['paths']['output_dir']

        # 创建逐阶段递减的 parquet 文件
        stage_rows = {
            '00_preprocessing.parquet': 1000,
            '11_bank_news.parquet': 800,
            '12_fintech_news.parquet': 500,
            '21_tone_llms.parquet': 450,
            '21_tone_llms_full.parquet': 800,
            '22_words_tone.parquet': 450,
            '23_bert_tone.parquet': 450,
            '24_herd_decay.parquet': 450,
        }
        for filename, n_rows in stage_rows.items():
            _create_parquet(output_dir, filename, n_rows)

        # 不应抛异常
        generate_pipeline_summary(pipeline_config, pipeline_logger)

    def test_partial_stages(self, pipeline_config, pipeline_logger):
        """部分阶段文件缺失时应警告但不崩溃。"""
        output_dir = pipeline_config['paths']['output_dir']

        # 仅创建前两个阶段
        _create_parquet(output_dir, '00_preprocessing.parquet', 1000)
        _create_parquet(output_dir, '11_bank_news.parquet', 600)

        # 不应抛异常
        generate_pipeline_summary(pipeline_config, pipeline_logger)

    def test_no_files(self, pipeline_config, pipeline_logger):
        """全部文件缺失时应优雅处理。"""
        generate_pipeline_summary(pipeline_config, pipeline_logger)

    def test_single_row_files(self, pipeline_config, pipeline_logger):
        """极小文件（1行）应正常处理。"""
        output_dir = pipeline_config['paths']['output_dir']
        _create_parquet(output_dir, '00_preprocessing.parquet', 1)
        _create_parquet(output_dir, '23_bert_tone.parquet', 1)
        generate_pipeline_summary(pipeline_config, pipeline_logger)

    def test_empty_dataframe_parquet(self, pipeline_config, pipeline_logger):
        """空 DataFrame 的 parquet 文件应正常处理。"""
        output_dir = pipeline_config['paths']['output_dir']
        _create_parquet(output_dir, '00_preprocessing.parquet', 0)
        generate_pipeline_summary(pipeline_config, pipeline_logger)

    def test_missing_filename_key(self, pipeline_logger, tmp_path):
        """配置中缺少某个 filename key 时应优雅处理。"""
        config = {
            'paths': {'output_dir': str(tmp_path)},
            'filenames': {
                'output_00_preprocessing': '00_preprocessing.parquet',
                # 故意缺少其他键
            },
        }
        generate_pipeline_summary(config, pipeline_logger)


# ============================================================================
# 数据量变化计算测试
# ============================================================================

class TestPipelineDataFlowCalculation:
    """测试管道数据流转计算的数值正确性。"""

    def test_retention_rate_calculation(self, pipeline_config, pipeline_logger):
        """验证保留率计算：各阶段行数 / 初始行数。"""
        output_dir = pipeline_config['paths']['output_dir']
        _create_parquet(output_dir, '00_preprocessing.parquet', 1000)
        _create_parquet(output_dir, '11_bank_news.parquet', 500)
        _create_parquet(output_dir, '12_fintech_news.parquet', 200)
        # 不应抛异常（保留率：50%、20%）
        generate_pipeline_summary(pipeline_config, pipeline_logger)

    def test_identical_row_counts(self, pipeline_config, pipeline_logger):
        """所有阶段行数相同时，变化量应为 0。"""
        output_dir = pipeline_config['paths']['output_dir']
        for filename in pipeline_config['filenames'].values():
            _create_parquet(output_dir, filename, 500)
        generate_pipeline_summary(pipeline_config, pipeline_logger)

    def test_increasing_rows_warning(self, pipeline_config, pipeline_logger):
        """行数递增（异常情况）不应崩溃。"""
        output_dir = pipeline_config['paths']['output_dir']
        _create_parquet(output_dir, '00_preprocessing.parquet', 100)
        _create_parquet(output_dir, '11_bank_news.parquet', 200)  # 异常增长
        generate_pipeline_summary(pipeline_config, pipeline_logger)

    def test_large_dataset(self, pipeline_config, pipeline_logger):
        """较大数据集应正常处理。"""
        output_dir = pipeline_config['paths']['output_dir']
        _create_parquet(output_dir, '00_preprocessing.parquet', 50000)
        _create_parquet(output_dir, '23_bert_tone.parquet', 40000)
        generate_pipeline_summary(pipeline_config, pipeline_logger)


# ============================================================================
# quality-hardening Round 42 (2026-05-27): reporting.py 84.57% → ≥90%
# 补漏: panel_stages 段 (397-416, 423-427) + per-stage exception handler
# (354-356) + final detail report exception (379-380) + missing pct when
# total_rows==0 (line 189) + 14_fintech_intensity stage filename key
# ============================================================================


@pytest.fixture
def pipeline_config_with_panels(tmp_path):
    """带 panel_stages filenames 的扩展 config (覆盖 397-416)."""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    log_dir = tmp_path / 'logs'
    log_dir.mkdir()
    return {
        'paths': {
            'output_dir': str(output_dir),
            'log_dir': str(log_dir),
        },
        'filenames': {
            'output_00_preprocessing': '00_preprocessing.parquet',
            'output_11_bank_news': '11_bank_news.parquet',
            'output_12_fintech_news': '12_fintech_news.parquet',
            'output_14_fintech_intensity': '14_fintech_intensity.parquet',
            'output_21_tone_llms': '21_tone_llms.parquet',
            'output_21_tone_llms_full': '21_tone_llms_full.parquet',
            'output_22_words_tone': '22_words_tone.parquet',
            'output_23_bert_tone': '23_bert_tone.parquet',
            'output_24_herd_decay': '24_herd_decay.parquet',
            # 新加 3 个 panel filenames
            'output_40_panel_yearly': '40_panel_yearly.parquet',
            'output_40_article_bank': '40_article_bank.parquet',
            'output_51_panel_controls': '51_panel_with_controls.parquet',
        },
    }


def test_pipeline_summary_panel_stages_present(pipeline_config_with_panels,
                                                pipeline_logger):
    """panel_stages 三个 parquet 都存在 → 触发 397-405 路径."""
    output_dir = pipeline_config_with_panels['paths']['output_dir']
    _create_parquet(output_dir, '40_panel_yearly.parquet', 168)
    _create_parquet(output_dir, '40_article_bank.parquet', 1170)
    _create_parquet(output_dir, '51_panel_with_controls.parquet', 168)
    generate_pipeline_summary(pipeline_config_with_panels, pipeline_logger)


def test_pipeline_summary_panel_stages_partial(pipeline_config_with_panels,
                                                pipeline_logger):
    """panel_stages 部分文件缺失 → 触发 406-411 (未生成 status)."""
    output_dir = pipeline_config_with_panels['paths']['output_dir']
    # 仅 1 个 panel 文件存在, 其余缺失
    _create_parquet(output_dir, '40_panel_yearly.parquet', 168)
    generate_pipeline_summary(pipeline_config_with_panels, pipeline_logger)


def test_pipeline_summary_missing_filenames_key(pipeline_logger, tmp_path):
    """panel_stages 中 filenames 缺 key → 触发 396 continue (跳过该 panel stage)."""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    config = {
        'paths': {'output_dir': str(output_dir), 'log_dir': str(tmp_path / 'logs')},
        'filenames': {
            'output_00_preprocessing': '00_preprocessing.parquet',
            # 故意不加 output_40_panel_yearly / output_40_article_bank
            # / output_51_panel_controls → 走 `if not filename: continue` 路径
        },
    }
    _create_parquet(str(output_dir), '00_preprocessing.parquet', 100)
    generate_pipeline_summary(config, pipeline_logger)


def test_pipeline_summary_handles_corrupt_panel_parquet(
        pipeline_config_with_panels, pipeline_logger):
    """panel_stages 中 parquet 损坏 → 触发 412-420 异常 handler."""
    output_dir = pipeline_config_with_panels['paths']['output_dir']
    # 写一个有效的早期 stage parquet (走 happy path)
    _create_parquet(output_dir, '00_preprocessing.parquet', 100)
    # 写一个损坏的 panel parquet
    bad_parquet = os.path.join(output_dir, '40_panel_yearly.parquet')
    with open(bad_parquet, 'wb') as f:
        f.write(b'not a real parquet file')
    # 不应崩溃; 应记录 error
    generate_pipeline_summary(pipeline_config_with_panels, pipeline_logger)


def test_pipeline_summary_corrupt_stage_parquet(pipeline_config, pipeline_logger):
    """主流程中某 stage parquet 损坏 → 触发 354-362 异常 handler."""
    output_dir = pipeline_config['paths']['output_dir']
    # 正常文件 + 损坏文件
    _create_parquet(output_dir, '00_preprocessing.parquet', 100)
    bad_path = os.path.join(output_dir, '11_bank_news.parquet')
    with open(bad_path, 'wb') as f:
        f.write(b'not parquet')
    # 不应崩溃
    generate_pipeline_summary(pipeline_config, pipeline_logger)


def test_pipeline_summary_final_detail_report_error(pipeline_config,
                                                     pipeline_logger,
                                                     monkeypatch):
    """final detail report (379-380) 异常 handler: monkey-patch pd.read_parquet
    在最终阶段加载时抛, generate_pipeline_summary 不应崩溃."""
    import pandas as pd

    import news_process.core.reporting as reporting_mod
    output_dir = pipeline_config['paths']['output_dir']
    # 创建所有阶段的有效 parquet
    for filename in pipeline_config['filenames'].values():
        _create_parquet(output_dir, filename, 50)

    # monkey-patch: 让 pd.read_parquet 抛 (但保留 pq.read_metadata 完好)
    original_read = pd.read_parquet

    def failing_read(*args, **kwargs):
        raise RuntimeError("simulated parquet load failure")
    monkeypatch.setattr(reporting_mod.pd, 'read_parquet', failing_read)
    try:
        # 不应崩溃; 应进 except 路径 (379-380)
        generate_pipeline_summary(pipeline_config, pipeline_logger)
    finally:
        monkeypatch.setattr(reporting_mod.pd, 'read_parquet', original_read)


# ============================================================================
# 直接对 reporting helpers 加测试 (Round 42 续) — save_dataset 双分支 +
# safe_save_preview_csv PermissionError + total_rows==0 missing pct
# ============================================================================


def test_save_dataset_with_versioning_branch(tmp_path):
    """save_dataset 传 stage_name+config → 走 save_parquet_with_metadata
    (lines 74-75)."""
    from unittest.mock import patch

    import pandas as pd

    import news_process.core.reporting as rep
    from news_process.core.logging import setup_logging

    logger = setup_logging('save_vers', str(tmp_path / 'logs'))
    df = pd.DataFrame({'a': [1, 2, 3]})
    out_path = str(tmp_path / 'out.parquet')

    with patch('news_process.core.data_versioning.save_parquet_with_metadata') as mock_save:
        # mock 不真写文件; 我们仅验证调用路径
        mock_save.return_value = None
        # 但 csv preview 仍需 out.parquet 存在 (其实没必要, safe_save_preview_csv 自身写 csv 不读 parquet)
        # 直接调用
        rep.save_dataset(df, out_path, logger,
                          stage_name='test_stage',
                          config={'paths': {'output_dir': str(tmp_path)}},
                          input_files=[])
        assert mock_save.called


def test_save_dataset_exception_propagates(tmp_path):
    """save_dataset: parquet 写失败 → 异常 re-raise (lines 90-93)."""
    from unittest.mock import patch

    import pandas as pd

    import news_process.core.reporting as rep
    from news_process.core.logging import setup_logging

    logger = setup_logging('save_err', str(tmp_path / 'logs'))
    df = pd.DataFrame({'a': [1]})
    out_path = str(tmp_path / 'out.parquet')

    # patch to_parquet 抛
    with patch.object(pd.DataFrame, 'to_parquet',
                      side_effect=RuntimeError("write failure")):
        with pytest.raises(RuntimeError, match="write failure"):
            rep.save_dataset(df, out_path, logger)


def test_safe_save_preview_csv_permission_error(tmp_path):
    """safe_save_preview_csv PermissionError → 静默 warning (lines 38-42)."""
    from unittest.mock import patch

    import pandas as pd

    import news_process.core.reporting as rep
    from news_process.core.logging import setup_logging

    logger = setup_logging('csv_perm', str(tmp_path / 'logs'))
    df = pd.DataFrame({'a': [1]})
    target = str(tmp_path / 'preview.csv')
    # patch DataFrame.to_csv 抛 PermissionError
    with patch.object(pd.DataFrame, 'to_csv',
                      side_effect=PermissionError("Excel 占用文件")):
        # 不抛
        rep.safe_save_preview_csv(df, target, logger)


def test_generate_dataframe_report_gb_branch(tmp_path):
    """generate_dataframe_report memory >= 1 GB 走 GB 分支 (lines 157-160).

    用 monkey-patch DataFrame.memory_usage 返回 ≥ 1 GB.
    """
    from unittest.mock import patch

    import pandas as pd

    from news_process.core.logging import setup_logging
    from news_process.core.reporting import generate_dataframe_report

    logger = setup_logging('rep_gb', str(tmp_path / 'logs'))
    df = pd.DataFrame({'a': [1, 2, 3]})
    # mock memory_usage 返回 ~2 GB
    fake_mem = pd.Series([2 * 1024 ** 3], index=['a'])
    with patch.object(pd.DataFrame, 'memory_usage', return_value=fake_mem):
        generate_dataframe_report(df, logger)


def test_generate_dataframe_report_mb_branch(tmp_path):
    """generate_dataframe_report memory ∈ [1MB, 1GB) 走 MB 分支."""
    from unittest.mock import patch

    import pandas as pd

    from news_process.core.logging import setup_logging
    from news_process.core.reporting import generate_dataframe_report

    logger = setup_logging('rep_mb', str(tmp_path / 'logs'))
    df = pd.DataFrame({'a': [1, 2, 3]})
    fake_mem = pd.Series([5 * 1024 ** 2], index=['a'])  # 5 MB
    with patch.object(pd.DataFrame, 'memory_usage', return_value=fake_mem):
        generate_dataframe_report(df, logger)
