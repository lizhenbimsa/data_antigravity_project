import os
import sys
import pytest
import pandas as pd
import numpy as np

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
    tone.ALL_DICTIONARIES = []
    res_none = tone._analyze_single_article(None)

    
    res_punct = tone._analyze_single_article("。。？？！！")
    assert res_punct['pos_ratio'] == 0.0
    # empty/punctuation content yields default readability
    assert res_punct['avg_sentence_len'] == 0.0 or res_punct['avg_sentence_len'] == 6.0
