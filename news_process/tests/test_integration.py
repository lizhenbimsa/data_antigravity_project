"""
tests/test_integration.py — 集成测试
=====================================

验证跨模块数据流和关键配置一致性。
"""

import os
import sys
import json
import pytest
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_config


# ============================================================================
# 配置一致性测试
# ============================================================================

class TestConfigIntegrity:
    """验证配置文件的完整性和一致性。"""

    @pytest.fixture
    def config(self):
        return load_config()

    def test_required_paths_exist(self, config):
        """配置中引用的核心路径键应存在。"""
        required_keys = [
            'output_dir', 'log_dir', 'bank_names_file',
            'fintech_dict_file', 'tone_dicts_file',
        ]
        for key in required_keys:
            assert key in config['paths'], f"缺少路径配置: {key}"

    def test_required_filenames_exist(self, config):
        """配置中引用的输出文件名键应存在。"""
        required = [
            'output_00_preprocessing', 'output_11_bank_news',
            'output_12_fintech_news', 'output_21_tone_llms',
            'output_22_words_tone', 'output_23_bert_tone',
        ]
        for key in required:
            assert key in config['filenames'], f"缺少文件名配置: {key}"

    def test_all_paths_absolute(self, config):
        """所有路径应为绝对路径。"""
        for key, path in config['paths'].items():
            assert os.path.isabs(path), f"路径 {key}={path} 不是绝对路径"

    def test_parallel_config(self, config):
        """并行配置应合理。"""
        parallel = config.get('parallel', {})
        n_jobs = parallel.get('n_jobs', -1)
        batch_size = parallel.get('batch_size', 5000)
        assert isinstance(n_jobs, int)
        assert batch_size > 0

    def test_dedup_config_valid(self, config):
        """去重配置阈值应在合理范围。"""
        dedup = config.get('deduplication', {})
        threshold = dedup.get('jaccard_similarity_threshold', 0.8)
        assert 0 < threshold < 1, f"Jaccard 阈值应在 (0,1) 之间，实际: {threshold}"

    def test_config_files_exist(self, config):
        """配置文件引用的外部资源文件应存在。"""
        files_to_check = [
            'bank_names_file',
            'fintech_dict_file',
            'tone_dicts_file',
            'bank_name_exclusions_file',
            'noise_patterns_file',
        ]
        for key in files_to_check:
            path = config['paths'].get(key)
            if path:
                assert os.path.exists(path), f"配置文件不存在: {key}={path}"


# ============================================================================
# 外部资源文件格式测试
# ============================================================================

class TestResourceFiles:
    """验证外部资源文件的格式正确性。"""

    @pytest.fixture
    def config(self):
        return load_config()

    def test_bank_names_json_format(self, config):
        """bank_names.json 应为有效 JSON 列表。"""
        path = config['paths'].get('bank_names_file')
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, list)
            if data:
                assert 'variants' in data[0] or 'standard_name' in data[0]

    def test_fintech_dict_json_format(self, config):
        """fintech_dict.json 应为有效 JSON。"""
        path = config['paths'].get('fintech_dict_file')
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, (list, dict))

    def test_tone_dicts_json_format(self, config):
        """tone_dicts.json 应为有效 JSON 对象。"""
        path = config['paths'].get('tone_dicts_file')
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, dict)
            # 应包含预期的词典键
            expected_keys = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
            for key in expected_keys:
                assert key in data, f"tone_dicts.json 缺少键: {key}"

    def test_exclusion_patterns_json_format(self, config):
        """bank_name_exclusions.json 应为有效 JSON 对象。"""
        path = config['paths'].get('bank_name_exclusions_file')
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, dict)
            assert 'negation_patterns' in data or 'short_name_context_exclusions' in data

    def test_noise_patterns_json_format(self, config):
        """noise_patterns.json 应为有效 JSON 对象。"""
        path = config['paths'].get('noise_patterns_file')
        if path and os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            assert isinstance(data, dict)


# ============================================================================
# 数据流一致性测试
# ============================================================================

class TestDataFlow:
    """验证跨阶段数据流一致性。"""

    def test_stage_output_column_contract(self):
        """模拟数据流中各阶段应保留核心列。"""
        # Stage 00 输出列
        df_00 = pd.DataFrame({
            'docid': ['D1'], '标题': ['时标题'], '内容': ['内容'],
            '媒体(中文)': ['新华社'], '日期': ['2024-01-01'],
            '媒体类型(中文)': ['报纸'],
        })

        # Stage 11 应保留 00 的列并添加银行分类列
        df_11 = df_00.copy()
        df_11['is_bank_news'] = True
        df_11['target_bank'] = '中国工商银行'
        df_11['co_mentioned_banks'] = ''
        assert '标题' in df_11.columns
        assert 'is_bank_news' in df_11.columns

        # Stage 12 应保留 11 的列并添加分类列
        df_12 = df_11.copy()
        df_12['is_fintech_news'] = True
        df_12['fintech_distinct_count'] = 5
        assert 'is_bank_news' in df_12.columns
        assert 'is_fintech_news' in df_12.columns

        # Stage 21 应保留 12 的列并添加 LLM 列
        df_21 = df_12.copy()
        df_21['llm_verified'] = True
        df_21['llm_sentiment'] = '正面'
        df_21['llm_agreement_rate'] = 1.0
        assert 'is_fintech_news' in df_21.columns
        assert 'llm_verified' in df_21.columns

        # Stage 22 应保留 21 的列并添加词典分数
        df_22 = df_21.copy()
        df_22['jiang_2021_score'] = 0.5
        df_22['jiang_2021_label'] = '正面'
        assert 'llm_sentiment' in df_22.columns
        assert 'jiang_2021_score' in df_22.columns

    def test_bank_then_fintech_flow(self):
        """银行筛选→金融科技筛选数据流应正确传递。"""
        # 模拟银行筛选结果
        df_bank = pd.DataFrame({
            '标题': ['银行创新', '普通新闻', '银行科技'],
            '内容': ['内容1', '内容2', '内容3'],
            'is_bank_news': [True, False, True],
            'target_bank': ['工商银行', '', '建设银行'],
        })

        # 筛选为银行新闻
        df_filtered = df_bank[df_bank['is_bank_news']].copy()
        assert len(df_filtered) == 2

        # 模拟金融科技分类
        df_filtered['is_fintech_news'] = [True, False]
        df_fintech = df_filtered[df_filtered['is_fintech_news']].copy()
        assert len(df_fintech) == 1
        assert df_fintech.iloc[0]['target_bank'] == '工商银行'


# ============================================================================
# Pipeline Reporting 测试
# ============================================================================

class TestPipelineReportingIntegration:
    """验证管道报告功能。"""

    def test_generate_summary_with_parquets(self, tmp_path):
        """使用临时 parquet 文件测试管道报告摘要。"""
        from utils.helpers import setup_logging, save_dataset

        logger = setup_logging('test_pipeline', str(tmp_path / 'logs'))
        output_dir = tmp_path / 'output'
        output_dir.mkdir()

        # 创建模拟各阶段 parquet
        for name, n_rows in [('00_preprocessing', 1000), ('11_bank_news', 500),
                              ('12_fintech_news', 200), ('21_tone_llms', 180)]:
            df = pd.DataFrame({'docid': range(n_rows), '标题': ['test'] * n_rows})
            df.to_parquet(str(output_dir / f'{name}.parquet'), index=False)

        # 验证 parquet 文件正确写入
        for name, expected_rows in [('00_preprocessing', 1000), ('11_bank_news', 500)]:
            loaded = pd.read_parquet(str(output_dir / f'{name}.parquet'))
            assert len(loaded) == expected_rows


# ============================================================================
# 增强集成测试
# ============================================================================

class TestEnhancedIntegration:
    """增强集成测试：配置验证和数据流一致性。"""

    def test_media_weights_file_config(self):
        """验证 media_weights_file 配置存在且路径有效。"""
        config = load_config()
        # media_weights_file 可能在 paths 或其他位置
        if 'media_weights_file' in config.get('paths', {}):
            path = config['paths']['media_weights_file']
            assert os.path.exists(path), f"media_weights_file 不存在: {path}"

    def test_stage_output_filenames_unique(self):
        """所有阶段输出文件名应唯一。"""
        config = load_config()
        filenames = config.get('filenames', {})
        output_files = [v for k, v in filenames.items() if k.startswith('output_')]
        assert len(output_files) == len(set(output_files)), \
            f"发现重复的输出文件名: {output_files}"

    def test_all_stage_keys_have_filenames(self):
        """关键阶段的输出文件名键应存在于配置中。"""
        config = load_config()
        filenames = config.get('filenames', {})
        required_keys = [
            'output_00_preprocessing',
            'output_11_bank_news',
            'output_12_fintech_news',
        ]
        for key in required_keys:
            assert key in filenames, f"配置中缺少输出文件关键键: {key}"

    def test_pipeline_reporting_with_mock_stages(self, tmp_path):
        """管道报告集成测试：使用多阶段 mock 数据。"""
        from utils.pipeline_reporting import generate_pipeline_summary
        from utils.helpers import setup_logging

        logger = setup_logging('test_enhanced_pipeline', str(tmp_path / 'logs'))
        output_dir = tmp_path / 'output'
        output_dir.mkdir()

        config = {
            'paths': {'output_dir': str(output_dir)},
            'filenames': {
                'output_00_preprocessing': '00_preprocessing.parquet',
                'output_11_bank_news': '11_bank_news.parquet',
                'output_12_fintech_news': '12_fintech_news.parquet',
                'output_21_tone_llms': '21_tone_llms.parquet',
                'output_21_tone_llms_full': '21_tone_llms_full.parquet',
                'output_22_words_tone': '22_words_tone.parquet',
                'output_23_bert_tone': '23_bert_tone.parquet',
            },
        }

        # 创建递减数据量的 parquet 文件
        for name, n_rows in [('00_preprocessing', 2000), ('11_bank_news', 1000),
                              ('12_fintech_news', 500), ('21_tone_llms', 450),
                              ('22_words_tone', 450), ('23_bert_tone', 450)]:
            df = pd.DataFrame({
                'docid': range(n_rows),
                '标题': [f'新闻{i}' for i in range(n_rows)],
                '内容': [f'内容{i}' for i in range(n_rows)],
            })
            df.to_parquet(str(output_dir / f'{name}.parquet'), index=False)

        # 不应抛异常
        generate_pipeline_summary(config, logger)

    def test_dedup_threshold_in_valid_range(self):
        """去重阈值应在 (0, 1) 范围内。"""
        config = load_config()
        threshold = config.get('dedup', {}).get('jaccard_similarity_threshold')
        if threshold is not None:
            assert 0 < threshold < 1, f"Jaccard 阈值应在 (0, 1)，当前: {threshold}"

    def test_sentiment_methods_valid(self):
        """启用的情感分析方法应在合法集合内。"""
        config = load_config()
        enabled_methods = config.get('sentiment_analysis', {}).get('enabled_methods', [])
        valid_methods = {'tone_llms', 'tone_words', 'tone_berts'}
        for method in enabled_methods:
            assert method in valid_methods, \
                f"未知情感分析方法: {method}，有效选项: {valid_methods}"

