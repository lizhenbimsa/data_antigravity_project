"""
tests/test_pipeline_reporting.py — utils/pipeline_reporting.py 单元测试
========================================================================

测试管道执行摘要报告生成器的核心逻辑。
"""

import os
import sys
import logging
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.pipeline_reporting import generate_pipeline_summary
from utils.helpers import setup_logging


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
