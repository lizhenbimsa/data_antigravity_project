"""
tests/conftest.py — 共享 pytest fixtures
==========================================

提供所有测试共用的 mock 数据、临时文件和 fixture 工厂。
"""

import os
import sys
import json
import pytest
import tempfile
import pandas as pd
import numpy as np

# 确保 news_process 目录在 sys.path 中
NEWS_PROCESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if NEWS_PROCESS_DIR not in sys.path:
    sys.path.insert(0, NEWS_PROCESS_DIR)


# ============================================================================
# 基础 Fixtures
# ============================================================================

@pytest.fixture
def tmp_dir(tmp_path):
    """返回临时目录路径（pytest 内置 tmp_path 的别名）。"""
    return tmp_path


@pytest.fixture
def sample_df():
    """创建包含所有必需列的模拟新闻 DataFrame（20行）。"""
    np.random.seed(42)
    n = 20
    return pd.DataFrame({
        'docid': [f'DOC{i:04d}' for i in range(n)],
        'pubcode': [f'PUB{i:03d}' for i in range(n)],
        '媒体(中文)': np.random.choice(['新华社', '人民日报', '经济日报', '21世纪经济报道'], n),
        '媒体类型(中文)': np.random.choice(['报纸', '网页(W)', '期刊'], n),
        '内容': [
            '中国工商银行近日宣布推出人工智能驱动的智能风控系统，该系统利用大数据和机器学习技术，'
            '能够实时监测交易风险。工商银行金融科技部负责人表示，这一举措将大幅提升风控效率。'
            '工商银行计划在未来三年内将人工智能技术应用到更多业务领域。'
            * 3  # 重复使内容足够长
        ] * n,
        '日期': pd.date_range('2024-01-01', periods=n, freq='D').strftime('%Y-%m-%d').tolist(),
        '标题': [f'中国工商银行推出金融科技创新方案{i}' for i in range(n)],
        '版面': ['财经'] * n,
        '栏名': ['银行'] * n,
        '页号': ['A1'] * n,
        '作者': [f'记者{i}' for i in range(n)],
        '国家地区/省份': np.random.choice(['北京', '上海', '广东', '浙江'], n).tolist(),
        '城市': np.random.choice(['北京', '上海', '广州', '杭州'], n).tolist(),
    })


@pytest.fixture
def small_df():
    """极简 DataFrame（3行），用于快速逻辑测试。"""
    return pd.DataFrame({
        '标题': ['银行金融科技创新', '天气预报', '工行大数据风控'],
        '内容': [
            '中国建设银行近日推出区块链供应链金融平台，建设银行表示该平台已联合多家企业试点。'
            '建设银行科技部表示，区块链技术可有效提升供应链金融的透明度和效率。',
            '今天北京天气晴朗，最高温度25度，适合出行。',
            '工商银行旗下的大数据风控平台已正式上线，工行利用人工智能技术进行实时风险监控。'
            '工行金融科技负责人指出，大数据技术将全面赋能风控体系。工行计划在全国推广。',
        ],
        '媒体(中文)': ['新华社', '人民日报', '经济日报'],
        '日期': ['2024-01-01', '2024-01-02', '2024-01-03'],
    })


# ============================================================================
# Mock JSON 数据 Fixtures
# ============================================================================

@pytest.fixture
def mock_bank_names_json(tmp_dir):
    """创建 mock 银行名称 JSON 文件。"""
    data = [
        {
            'bank_name': '中国工商银行',
            'variants': ['中国工商银行', '工商银行', '工行', 'ICBC'],
        },
        {
            'bank_name': '中国建设银行',
            'variants': ['中国建设银行', '建设银行', '建行', 'CCB'],
        },
        {
            'bank_name': '中国银行',
            'variants': ['中国银行', '中行', 'BOC'],
        },
    ]
    path = tmp_dir / 'bank_names.json'
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return str(path)


@pytest.fixture
def mock_bank_name_exclusions_json(tmp_dir):
    """创建 mock 银行名称排除规则 JSON 文件。"""
    data = {
        'negation_patterns': ['务农行列', '交通行业', '中国银行业'],
        'short_name_context_exclusions': {
            'context_window': 5,
            'exclusions': {
                '工行': ['工行距离', '施工行为'],
                '中行': ['中行走', '中行列'],
            }
        }
    }
    path = tmp_dir / 'bank_name_exclusions.json'
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return str(path)


@pytest.fixture
def mock_fintech_dict_json(tmp_dir):
    """创建 mock 金融科技词典 JSON 文件。"""
    data = [
        '人工智能', '大数据', '云计算', '区块链', '物联网',
        '数字支付', '智能风控', '数字信贷', '机器学习', '深度学习',
        '金融科技', '数字化转型', '智能客服',
    ]
    path = tmp_dir / 'fintech_dict.json'
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return str(path)


@pytest.fixture
def mock_tone_dicts_json(tmp_dir):
    """创建 mock 情感词典 JSON 文件。"""
    data = {
        'jiang_2021': {
            'name': '姜富伟(2021)',
            'positive': ['增长', '创新', '突破', '提升', '良好'],
            'negative': ['下降', '风险', '亏损', '困难', '危机'],
        },
        'yao_2021': {
            'name': '姚加权(2021)',
            'positive': ['盈利', '发展', '优化'],
            'negative': ['损失', '违规', '处罚'],
        },
        'bian_2021': {'name': 'Bian(2021)', 'positive': [], 'negative': []},
        'du_2022': {
            'name': 'Du(2022)',
            'positive': ['合作', '升级'],
            'negative': ['违约', '欺诈'],
            'political_positive': ['改革', '开放'],
        },
        'you_2018': {'name': 'You(2018)', 'positive': [], 'negative': []},
    }
    path = tmp_dir / 'tone_dicts.json'
    path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
    return str(path)


@pytest.fixture
def mock_config(tmp_dir):
    """创建模拟配置字典。"""
    return {
        'paths': {
            'output_dir': str(tmp_dir / 'output'),
            'log_dir': str(tmp_dir / 'logs'),
            'raw_data_dir': str(tmp_dir / 'data_excel'),
            'bank_names_file': str(tmp_dir / 'bank_names.json'),
            'bank_keywords_file': str(tmp_dir / 'bank_keywords.json'),
            'fintech_dict_file': str(tmp_dir / 'fintech_dict.json'),
            'bank_name_exclusions_file': str(tmp_dir / 'bank_name_exclusions.json'),
            'tone_dicts_file': str(tmp_dir / 'tone_dicts.json'),
            'noise_patterns_file': str(tmp_dir / 'noise_patterns.json'),
            'media_weights_file': str(tmp_dir / 'media_weights.json'),
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
        'parallel': {'n_jobs': 1, 'batch_size': 5},
        'preprocessing': {
            'title_min_length': 2,
            'content_min_length': 100,
            'content_max_length': 10000,
        },
        'deduplication': {
            'jaccard_similarity_threshold': 0.85,
            'minhash_permutations': 16,
            'ngram_size': 3,
            'parallel_workers': 1,
        },
    }


# ============================================================================
# 日志隔离 — 防止测试运行污染生产日志文件
# ============================================================================

@pytest.fixture(autouse=True, scope='session')
def _isolate_loggers_from_production_files():
    """在 pytest session 开始时移除所有模块级 logger 中的文件 handler。

    问题根因:
      各 pipeline 脚本（如 51_falsification_test.py）在模块级别执行
      ``logger = setup_logging(STAGE_NAME, ...)``，当 pytest import 这些模块时，
      RotatingFileHandler 被注册到 logger 上，导致测试中每个函数调用的日志
      都写入生产 .log 文件，产生重复输出问题。

    本 fixture 在所有测试开始前，扫描已注册的 logger，将文件 handler 替换为
    NullHandler，确保测试只输出到控制台（stderr），不触碰生产日志文件。
    """
    import logging
    from logging.handlers import RotatingFileHandler

    patched = []
    for name, lg in logging.Logger.manager.loggerDict.items():
        if not isinstance(lg, logging.Logger):
            continue
        file_handlers = [
            h for h in lg.handlers
            if isinstance(h, (logging.FileHandler, RotatingFileHandler))
        ]
        for fh in file_handlers:
            lg.removeHandler(fh)
            patched.append((name, fh))

    yield  # 测试运行

    # 恢复（可选，session 结束后进程即退出，恢复非必须）
    for name, fh in patched:
        lg = logging.getLogger(name)
        if fh not in lg.handlers:
            lg.addHandler(fh)
