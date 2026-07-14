"""
tests/conftest.py — 共享 pytest fixtures
==========================================

提供所有测试共用的 mock 数据、临时文件和 fixture 工厂。
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

# 确保 news_process 目录在 sys.path 中  (legacy: ``from utils.helpers import X`` 形式仍需此项)
NEWS_PROCESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if NEWS_PROCESS_DIR not in sys.path:
    sys.path.insert(0, NEWS_PROCESS_DIR)

# Phase 1: 同时把项目根的父目录 (data_antigravity_project/) 加入 sys.path,
# 这样 ``import news_process`` 才能解析到包根 (news_process/__init__.py)。
PROJECT_PARENT = os.path.dirname(NEWS_PROCESS_DIR)
if PROJECT_PARENT not in sys.path:
    sys.path.insert(0, PROJECT_PARENT)

# ============================================================================
# fix(M1-P2, 2026-07-14): v3.5.1 冻结 sidecar 写入全局隔离。
# M1 后 sidecar 为 git 跟踪文件且写路径经 config 绝对解析 (cwd 免疫) — 任何
# 经 apply_v3_5_1/aggregate_panel 的测试路径都会刷新真 sidecar 的
# stage21_last_run_timestamp → 每次全量 pytest 脏工作树 (推送后终审实证:
# 逐点给 4 个已知调用测试补 env 隔离后仍有漏网路径)。改为 conftest autouse
# 一点封死: 所有测试默认把 LLM_ARCHIVE_SIDECAR_PATH 指向各自 tmp; 刻意走真
# 解析路径的只读测试共三处 delenv 豁免 (test_prompt_v8_frozen 恒等 gate /
# test_v3_5_to_v3_5_1_migration 存在性 gate / test_omni_fix_tonellms 的
# g05 路径断言[既有, 只解析不读写]); 需自定 sidecar 的测试用 setenv 覆盖
# (monkeypatch 同栈后设优先, R4 活跑 206 例验证零脏写)。
# ============================================================================


@pytest.fixture(autouse=True)
def _isolate_v3_5_1_sidecar_writes(tmp_path, monkeypatch):
    monkeypatch.setenv(
        'LLM_ARCHIVE_SIDECAR_PATH', str(tmp_path / 'v3_5_1_constants.json'))


# ============================================================================
# 日志隔离【根因修复 R1】(2026-06-20 日志审计): 模块级 monkeypatch setup_logging,
# 防 pytest 收集/import 覆写真实生产日志 logs/<stage>.log。
# ============================================================================
# 根因: 多个 pipeline stage 模块在【模块顶层】调用 setup_logging() 并随即 emit 横幅
# (如 13/14/21 的 1-2 行 banner)。pytest 收集期 import 这些模块时, 该 emit 发生在
# *import 时刻* —— 早于任何 fixture (含下方 session 级 handler 扫描), 故会以
# file_mode='w' 首写截断覆写 logs/<stage>.log 里上一次【真实生产运行】的记录
# (即 12b/37/47/39c/39e/39f/21 等"现盘日志实为测试产物"的成因)。session/function
# 级 fixture 都无法阻止 import 期 emit —— 唯一可靠拦截点是在【收集开始前】(conftest
# 模块导入即执行) monkeypatch setup_logging: 凡写【生产 logs/ 目录】的调用一律强制
# console_only=True (不创建文件 handler); 写 tmp 目录的调用 (test_helpers /
# test_pipeline_reporting 等单测) 经路径判别豁免, 行为不变。
# 生产运行不导入 conftest, 故 setup_logging 在生产中行为完全不变 (零副作用)。
try:
    import news_process.core.logging as _np_logging

    try:
        from news_process.core.config import load_config as _np_load_config
        _PROD_LOG_DIR = os.path.normcase(os.path.realpath(
            str(_np_load_config()['paths']['log_dir'])))
    except Exception:  # 配置不可用时回退到包内 logs/
        _PROD_LOG_DIR = os.path.normcase(os.path.realpath(
            os.path.join(NEWS_PROCESS_DIR, 'logs')))

    _orig_setup_logging = _np_logging.setup_logging

    def _testing_setup_logging(stage_name, log_dir, *args, **kwargs):
        """测试期包装: 写生产 logs/ 的调用强制 console_only, 不触碰生产日志文件。"""
        try:
            _resolved = os.path.normcase(os.path.realpath(str(log_dir)))
        except Exception:
            _resolved = ''
        if _resolved == _PROD_LOG_DIR:
            kwargs['console_only'] = True
        return _orig_setup_logging(stage_name, log_dir, *args, **kwargs)

    if getattr(_np_logging.setup_logging, '__name__', '') != '_testing_setup_logging':
        _np_logging.setup_logging = _testing_setup_logging
except Exception:  # pragma: no cover — 极端环境下不阻断测试收集
    pass


# ============================================================================
# V4 T1.6: 自动为测试分层打 marker (fast | integration)
# ============================================================================
# 按文件路径自动分配, 免人工给 48 个测试文件逐一加 pytestmark.
# 单 test 需 override (如某 root-level 测试实际为 integration) 可用
# ``@pytest.mark.integration`` 装饰器, pytest 会保留两个 marker.

def pytest_collection_modifyitems(config, items):
    """按路径自动打 marker: tests/integration/ 下为 'integration', 其余为 'fast'。"""
    integration_marker = pytest.mark.integration
    fast_marker = pytest.mark.fast
    integration_segment = os.path.join("tests", "integration") + os.sep
    for item in items:
        path_str = str(item.fspath)
        if integration_segment in path_str:
            item.add_marker(integration_marker)
        else:
            item.add_marker(fast_marker)


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


@pytest.fixture
def three_track_article_df():
    """三轨 (full/ctx/ss) 文章级 fixture (2026-06-14).

    给参数化三轨测试 (['_full','_ctx','_ss']) 提供统一的最小输入: 物化后的
    content_full / content_ctx / content_ss 三条文本轨 + ctx_is_fallback /
    ss_is_fallback 两个回退标志。

    回退语义 (镜像 ctx 回退公理):
      - 第 0 行: 银行与金科同句共现 → content_ss 为真窗口, ss_is_fallback=False。
      - 第 1 行: **零共现** (银行句不提金科) → content_ss 退回全文 body
        (== content_full), ss_is_fallback=True (按 plan §7.4-M2 至少含 1 个零共现
        回退行)。
    """
    bodies = [
        '工商银行推出金融科技风控平台。这是一句无关补充。',  # 共现行: 银行∧金科同句
        '建设银行季报披露净利增长。某非提及内容句。',          # 零共现行 → ss 回退全文
    ]
    titles = ['工商银行金科创新', '建设银行季报']
    full = [f'{t}。{b}' for t, b in zip(titles, bodies)]
    ctx = full[:]  # ctx 真窗口 (本 fixture 取全文同形, 结构平价即可)
    # ss: 共现行取窗口, 零共现行镜像 ctx 回退公理退回全文 body (== content_full)
    ss = ['工商银行金科创新。工商银行推出金融科技风控平台。', full[1]]
    ss_is_fallback = [False, True]
    return pd.DataFrame({
        'target_bank': ['工商银行', '建设银行'],
        'year': [2024, 2024],
        '标题': titles,
        '内容': bodies,
        'content_full': full,
        'content_ctx': ctx,
        'content_ss': ss,
        'ctx_is_fallback': pd.Series([False, False], dtype='bool'),
        'ss_is_fallback': pd.Series(ss_is_fallback, dtype='bool'),
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
        # v3.10.0: 第 6 部主词典 (L&M 2011 中文译本) + 6 非极性子集。
        # 缺此块 → load_all_dictionaries().get('loughran_mcdonald_zh_2026') 取空 → 列数对不齐。
        'loughran_mcdonald_zh_2026': {
            'name': 'Loughran-McDonald(2026)',
            'positive': ['盈余', '增益'],
            'negative': ['诉讼', '违规'],
            'uncertainty': ['可能', '或许'],
            'litigious': ['诉讼', '仲裁'],
            'constraining': ['必须', '强制'],
            'strong_modal': ['一定', '必定'],
            'weak_modal': ['也许', '大概'],
            'complexity': ['复杂', '繁琐'],
        },
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
            'output_14_fintech_intensity': '15_fintech_intensity.parquet',
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
