import os
import sys

import pandas as pd
import pytest

# Phase 7a-5: 注入项目父目录, 让 ``news_process.*`` 在任意 cwd 解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

# Phase 7a-5: body 已迁至 news_process.pipeline.sentiment.tone_words,
# 旧 ``spec_from_file_location('tone_words_22', '22_tone_words.py')`` 现仅
# 返回 thin shim, 直接走规范 import 即可拿到全部内部函数与模块级常量。
from news_process.pipeline.sentiment import tone_words as tone


@pytest.fixture
def mock_sentiment_dict():
    return {
        '上涨': 1.0,
        '好': 1.0,
        '下跌': -1.0,
        '差': -1.0
    }

def test_score_to_label():
    assert tone._score_to_label(0.15) == '正面'
    assert tone._score_to_label(-0.15) == '负面'
    assert tone._score_to_label(0.0) == '中性'
    assert tone._score_to_label(0.09) == '中性'

def test_compute_readability_empty():
    content = "   "
    tokens = [" ", " ", " "]
    res = tone._compute_readability(content, tokens)
    assert res['avg_sentence_len'] == 0.0
    assert res['type_token_ratio'] == 0.0
    assert res['char_per_word'] == 0.0

def test_compute_readability_normal():
    content = "中国工商银行上涨。这很好。"
    tokens = ["中国工商银行", "上涨", "。", "这", "很", "好", "。"]
    res = tone._compute_readability(content, tokens)
    assert res['avg_sentence_len'] > 0
    assert res['type_token_ratio'] <= 1.0
    assert res['char_per_word'] > 0

def test_compute_sentiment_with_rules(mock_sentiment_dict):
    # 将系统的规则模拟进去
    original_neg = tone.NEGATION_WORDS
    original_deg = tone.DEGREE_WORDS
    original_adv = tone.ADVERSATIVE_WORDS
    original_end = tone.SENTENCE_END_MARKERS
    # fix(audit ENG-2, 2026-06-13): 一并保存 WINDOW/BOOST — 旧版还原块遗漏这两个标量,
    # 形成 module-global 泄漏 (当前泄漏值==config 默认 2/1.5 故无害, 但属测试卫生缺陷)。
    original_window = tone.NEGATION_WINDOW
    original_boost = tone.ADVERSATIVE_BOOST

    tone.NEGATION_WORDS = frozenset(['不', '没'])
    tone.DEGREE_WORDS = {'非常': 2.0, '稍微': 0.5}
    tone.ADVERSATIVE_WORDS = frozenset(['但是', '然而'])
    tone.SENTENCE_END_MARKERS = frozenset(['。', '！', '？'])
    tone.NEGATION_WINDOW = 2
    tone.ADVERSATIVE_BOOST = 1.5

    # 1. 基础测试
    tokens_base = ["股票", "上涨", "。"]
    total_score, norm_score, p_cnt, n_cnt, matched = tone._compute_sentiment_with_rules(tokens_base, mock_sentiment_dict)
    assert p_cnt == 1
    assert n_cnt == 0
    assert total_score == 1.0
    
    # 2. 否定测试
    tokens_neg = ["股票", "不", "上涨", "。"]
    total_score_neg, norm_score_neg, p_cnt_neg, n_cnt_neg, _ = tone._compute_sentiment_with_rules(tokens_neg, mock_sentiment_dict)
    assert n_cnt_neg == 1
    assert p_cnt_neg == 0
    assert total_score_neg == -1.0
    
    # 3. 程度副词测试
    tokens_deg = ["业绩", "非常", "好", "。"]
    total_score_deg, _, p_cnt_deg, _, _ = tone._compute_sentiment_with_rules(tokens_deg, mock_sentiment_dict)
    assert p_cnt_deg == 1
    assert total_score_deg == 2.0
    
    # 4. 转折测试
    tokens_adv = ["虽然", "下跌", "但是", "业绩", "非常", "好", "。"]
    t_score_adv, _, p_c, n_c, matched_adv = tone._compute_sentiment_with_rules(tokens_adv, mock_sentiment_dict)
    assert t_score_adv == 2.0
    
    # 还原
    tone.NEGATION_WORDS = original_neg
    tone.DEGREE_WORDS = original_deg
    tone.ADVERSATIVE_WORDS = original_adv
    tone.SENTENCE_END_MARKERS = original_end
    tone.NEGATION_WINDOW = original_window      # fix(audit ENG-2): 补还原, 消除泄漏
    tone.ADVERSATIVE_BOOST = original_boost

def test_build_idf_weights():
    # 测试 IDF 生成
    df = pd.DataFrame({
        'id': [1, 2, 3],
        '内容': ["股票 大涨", "股票 大跌", "金融 市场"]
    })
    dicts = [
        ('test', {'大涨': 1.0, '大跌': -1.0, '金融': 1.0})
    ]
    idf_weights = tone.build_idf_weights(df, dicts, text_col='内容')
    assert 'test' in idf_weights
    assert '大涨' in idf_weights['test']
    assert '大跌' in idf_weights['test']
    assert '金融' in idf_weights['test']

def test_build_idf_empty():
    df = pd.DataFrame({'内容': []})
    dicts = [('test', {'大涨': 1.0})]
    idf_weights = tone.build_idf_weights(df, dicts, text_col='内容')
    assert idf_weights['test']['大涨'] == 1.0  # fallback

def test_analyze_empty_and_robustness():
    # 测试异常输入处理
    import math

    tone.ALL_DICTIONARIES = []
    res_none = tone._analyze_single_article(None)
    # fix(omni-g-tonewords empty-text contract, 2026-06-11): 空/无效文本 ratio → NaN
    # (缺失语义, 旧断言 == 0.0 为伪中性回填)
    assert math.isnan(res_none['pos_ratio'])

    res_punct = tone._analyze_single_article("。。？？！！")
    # fix(omni-g-tonewords-06, 2026-06-11): 纯标点文本 word-token 分母 = 0 → ratio NaN
    # (旧断言 == 0.0 锁的是含标点分母旧行为)
    assert math.isnan(res_punct['pos_ratio'])
    # 空文本/纯标点内容应产出默认可读性指标
    assert res_punct['avg_sentence_len'] == 0.0 or res_punct['avg_sentence_len'] == 6.0


@pytest.mark.fast
def test_score_to_label_config_wiring_anchor():
    """E-2 接线防回退锚 (2026-07-18 第六轮审计 RR1-L2-NIT-1): 两调用点必须显式传
    POS_THRESHOLD/NEG_THRESHOLD — 删去实参会静默回退到函数硬编码默认, 与 config
    (sentiment.yaml::tone_words.pos/neg_threshold) 分叉且全部既有测试仍绿。"""
    import inspect
    src = inspect.getsource(tone)
    assert src.count("_score_to_label(norm_score, POS_THRESHOLD, NEG_THRESHOLD)") == 1, \
        "主 label 调用点未显式传 config 阈值 (E-2 接线回退)"
    assert src.count("_score_to_label(idf_norm, POS_THRESHOLD, NEG_THRESHOLD)") == 1, \
        "idf label 调用点未显式传 config 阈值 (E-2 接线回退)"
    # 接线值与 config/默认恒等 (当前 yaml 0.1/-0.1; 若刻意改 yaml, 更新此锚)
    assert pytest.approx(0.1) == tone.POS_THRESHOLD
    assert pytest.approx(-0.1) == tone.NEG_THRESHOLD


# ══════════════════════════════════════════════════════════════════════════
# 进程并行后端 gate (perf 2026-07-25; 计划
# NINE_ENTRYPOINT_PRODUCTION_SCALE_RUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-25 §2-F3/F5)
# ══════════════════════════════════════════════════════════════════════════

def test_parallel_kwargs_workload_adaptive():
    """批数 < 阈值 → 线程臂 (免 spawn); ≥ 阈值 → 进程臂 (绕 GIL)。"""
    small = tone._parallel_kwargs(tone._PROC_PARALLEL_MIN_BATCHES - 1)
    big = tone._parallel_kwargs(tone._PROC_PARALLEL_MIN_BATCHES)
    assert small['prefer'] == 'threads', '小工况应留线程后端'
    assert big['prefer'] == 'processes', '大工况应切进程后端 (否则生产被 GIL 锁成单核)'


def test_proc_workers_capped_never_minus_one():
    """进程臂 worker 数必须有限且 ≤ CPU 核数 —— n_jobs=-1 已实弹 MemoryError。

    每个 loky worker 各持一份六部词典 + 注入 44,983 词的 jieba Trie (~0.6-2 GB),
    32 核机上以 -1 起 32 worker 会直接撑爆内存 (2026-07-25 实测)。"""
    kw = tone._parallel_kwargs(tone._PROC_PARALLEL_MIN_BATCHES)
    assert kw['n_jobs'] > 0, '进程臂严禁 n_jobs=-1 (worker 各持一份词典 → MemoryError)'
    assert kw['n_jobs'] <= (os.cpu_count() or 1)
    assert tone._proc_workers() >= 1


def test_proc_workers_config_override(monkeypatch):
    """config sentiment_analysis.tone_words.proc_workers 可覆盖; 畸值回落默认。"""
    monkeypatch.setitem(tone.SENTIMENT_PARAMS, 'proc_workers', 3)
    assert tone._proc_workers() == 3
    monkeypatch.setitem(tone.SENTIMENT_PARAMS, 'proc_workers', 'bogus')
    assert tone._proc_workers() == min(tone._PROC_PARALLEL_MAX_WORKERS, os.cpu_count() or 1)
    monkeypatch.setitem(tone.SENTIMENT_PARAMS, 'proc_workers', 0)
    assert tone._proc_workers() == 1, 'proc_workers=0 应 clamp 到 1 (不可为 0/负)'


def test_worker_helpers_are_module_level_picklable():
    """loky 进程后端要求 worker 为模块级 (pickle-by-ref)。"""
    import pickle
    for fn in (tone._classify_batch_worker, tone._idf_df_chunk_worker):
        assert fn.__module__ == tone.__name__
        assert pickle.loads(pickle.dumps(fn)) is fn


def test_silence_worker_logging_removes_handlers():
    """worker 必须彻底静音: setup_logging 的 delay+首开截断语义下, 子进程首条日志
    会把父进程 <stage>.log 从头截断 (2026-07-24 'worker 横幅毁日志头' 实弹先例)。"""
    import logging as _logging
    lg = tone.logger
    saved = list(lg.handlers)
    saved_disable = _logging.root.manager.disable
    try:
        lg.addHandler(_logging.NullHandler())
        tone._silence_worker_logging()
        assert lg.handlers == [], 'worker 静音后 logger 不得残留任何 handler'
        assert _logging.root.manager.disable >= _logging.CRITICAL
    finally:
        _logging.disable(saved_disable)
        lg.handlers = saved


# ══════════════════════════════════════════════════════════════════════════
# stage 24 herd_decay 进程并行 gate (F20, 2026-07-26; 与 stage22 同型范式)
# ══════════════════════════════════════════════════════════════════════════

def test_herd_parallel_kwargs_workload_adaptive():
    """银行数 < 阈值 → 串行 (免 spawn); ≥ 阈值 → 进程后端 (绕单线程瓶颈)。"""
    from news_process.pipeline.sentiment import herd_decay as H
    small = H._parallel_kwargs(H._PROC_PARALLEL_MIN_BANKS - 1)
    big = H._parallel_kwargs(H._PROC_PARALLEL_MIN_BANKS)
    assert small['n_jobs'] == 1, '小工况应串行'
    assert big['prefer'] == 'processes', (
        '大工况应切进程后端 —— 生产 991 家可算银行串行需 ≈5.8 小时并撞穿父端超时')
    assert big['n_jobs'] > 0, '严禁 n_jobs=-1 (每 worker 各持 TF-IDF 矩阵)'
    assert big['n_jobs'] <= (os.cpu_count() or 1)


def test_herd_proc_workers_config_override(monkeypatch):
    from news_process.pipeline.sentiment import herd_decay as H
    monkeypatch.setitem(H.HERD_CFG, 'proc_workers', 4)
    assert H._proc_workers() == 4
    monkeypatch.setitem(H.HERD_CFG, 'proc_workers', 'bogus')
    assert H._proc_workers() == min(H._PROC_PARALLEL_MAX_WORKERS, os.cpu_count() or 1)
    monkeypatch.setitem(H.HERD_CFG, 'proc_workers', 0)
    assert H._proc_workers() == 1, 'proc_workers=0 应 clamp 到 1'


def test_herd_worker_is_module_level_picklable():
    """loky 进程后端要求 worker 为模块级 (pickle-by-ref)。"""
    import pickle

    from news_process.pipeline.sentiment import herd_decay as H
    assert H._herd_bank_worker.__module__ == H.__name__
    assert pickle.loads(pickle.dumps(H._herd_bank_worker)) is H._herd_bank_worker


def test_herd_worker_silences_logging():
    """⚠ herd_decay 在**模块级**调 setup_logging → 子进程首条日志会截断父进程
    24_herd_decay_processor.log (2026-07-24 实弹先例)。worker 必须先静音。"""
    import logging as _logging

    from news_process.pipeline.sentiment import herd_decay as H
    lg = H.logger
    saved, saved_disable = list(lg.handlers), _logging.root.manager.disable
    try:
        lg.addHandler(_logging.NullHandler())
        H._silence_worker_logging()
        assert lg.handlers == [], 'worker 静音后不得残留 handler'
        assert _logging.root.manager.disable >= _logging.CRITICAL
    finally:
        _logging.disable(saved_disable)
        lg.handlers = saved
