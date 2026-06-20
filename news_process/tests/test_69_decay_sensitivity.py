import math
import os
import sys

import pandas as pd
import pytest

# Phase 7b: 注入项目父目录, 让 ``news_process.*`` 在任意 cwd 解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

# Phase 7b: body 已迁至 news_process.validation.decay_sensitivity,
# 旧 ``spec_from_file_location('decay_sensitivity_38b', '69_decay_sensitivity.py')``
# 现仅返回 thin shim, 直接走规范 import 即可拿到全部内部函数与模块级常量。
from news_process.validation import decay_sensitivity as decay


@pytest.fixture
def mock_sentiment_dict():
    return {
        '增长': 1.0,
        '好': 1.0,
        '减少': -1.0,
        '差': -1.0
    }

def test_decay_functions():
    assert decay.DECAY_FUNCTIONS['uniform'](0) == 1.0
    assert decay.DECAY_FUNCTIONS['uniform'](5) == 1.0
    
    assert decay.DECAY_FUNCTIONS['inverse'](0) == 1.0
    assert decay.DECAY_FUNCTIONS['inverse'](1) == 0.5
    assert decay.DECAY_FUNCTIONS['inverse'](3) == 0.25
    
    assert math.isclose(decay.DECAY_FUNCTIONS['exponential'](0), 1.0)
    assert math.isclose(decay.DECAY_FUNCTIONS['exponential'](2), math.exp(-1.0))

def test_sentence_tone(mock_sentiment_dict):
    # 与 22_tone_words 的测试同思路
    tokens = ["银行业绩", "增长"]
    assert decay._sentence_tone(tokens, mock_sentiment_dict) == 1.0
    
    tokens_unmatched = ["今天", "天气"]
    assert decay._sentence_tone(tokens_unmatched, mock_sentiment_dict) == 0.0

def test_compute_decay_sentiment(mock_sentiment_dict):
    # 句距 0: "银行业绩好", tone = 1.0
    # 句距 1: "市场减少", tone = -1.0
    tokenized_swd = [
        (["银行", "业绩", "好"], 0),      # w=1.0,  tone=1.0  => sum=1.0
        (["市场", "表现", "减少"], 1)       # w=0.5,  tone=-1.0 => sum=-0.5
    ]
    
    # uniform
    score_unif = decay.compute_decay_sentiment(tokenized_swd, mock_sentiment_dict, decay.DECAY_FUNCTIONS['uniform'])
    # (1.0 * 1.0 + 1.0 * -1.0) / 2.0 = 0.0
    assert math.isclose(score_unif, 0.0)
    
    # inverse
    score_inv = decay.compute_decay_sentiment(tokenized_swd, mock_sentiment_dict, decay.DECAY_FUNCTIONS['inverse'])
    # (1.0 * 1.0 + 0.5 * -1.0) / 1.5 = 0.5 / 1.5 = 1/3
    assert math.isclose(score_inv, 1.0 / 3.0)

def test_run_analysis_empty_robustness():
    # 测试异常输入处理
    df = pd.DataFrame({'target_bank': ['建设银行'], '内容': ['  ']})
    res_df = decay.run_analysis(df, [('test_dict', {'好': 1.0})])
    assert 'test_dict_uniform' in res_df.columns
    assert res_df.iloc[0]['test_dict_uniform'] == 0.0
