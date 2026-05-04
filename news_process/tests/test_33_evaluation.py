"""
tests/test_33_evaluation.py — diagnose_misclassification_bias 单元测试
====================================================================
"""

import os
import sys
import numpy as np
import pandas as pd
import pytest

# Phase 7b: 注入项目父目录, 让 ``news_process.*`` 在任意 cwd 解析
_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

# Phase 7b: body 已迁至 news_process.validation.llms_evaluation,
# 旧 ``import_module('33_news_llms_evaluation')`` 现仅返回 thin shim,
# 直接走规范 import 即可拿到全部内部函数与模块级常量。
from news_process.validation import llms_evaluation as _mod
diagnose_misclassification_bias = _mod.diagnose_misclassification_bias


def _make_df(n=100, fp_bias=None, seed=42):
    """构造测试 DataFrame。fp_bias='正面' 时 FP 样本全部为正面。"""
    rng = np.random.RandomState(seed)
    gold = rng.binomial(1, 0.7, n)
    pred = np.where(rng.binomial(1, 0.15, n), 1 - gold, gold).astype(bool)
    labels = ['正面', '中性', '负面']
    sentiment = np.array([rng.choice(labels) for _ in range(n)])
    if fp_bias:
        fp_mask = (gold == 0) & (pred == True)
        sentiment[fp_mask] = fp_bias
    return pd.DataFrame({
        '最终_验证': gold,
        'llm_verified_full': pred,
        'llm_verified_ctx': pred,
        'llm_sentiment_full': sentiment,
        'llm_sentiment_ctx': sentiment,
        '内容': ['测' * rng.randint(100, 2000) for _ in range(n)],
    })


class TestDiagnoseMisclassificationBias:

    def test_basic_structure(self):
        """返回字典包含所有必要键，四象限之和等于总样本数。"""
        df = _make_df(100)
        r = diagnose_misclassification_bias(df, '最终_验证', '_full')
        assert set(r.keys()) == {'track', 'tests', 'quadrant_counts', 'conclusion'}
        qc = r['quadrant_counts']
        assert set(qc.keys()) == {'TP', 'FP', 'FN', 'TN'}
        assert qc['TP'] + qc['FP'] + qc['FN'] + qc['TN'] == 100

    def test_fp_zero_skips_t1_t3(self):
        """gold 全为 1 → FP=0 → T1/T3 标记 skipped。"""
        df = pd.DataFrame({
            '最终_验证': [1] * 50,
            'llm_verified_full': [True] * 40 + [False] * 10,
            'llm_sentiment_full': ['正面'] * 50,
            '内容': ['测试'] * 50,
        })
        r = diagnose_misclassification_bias(df, '最终_验证', '_full')
        assert r['quadrant_counts']['FP'] == 0
        assert r['tests'][0]['skipped'] is True   # T1
        assert r['tests'][2]['skipped'] is True   # T3

    def test_fn_zero_skips_t2_t4(self):
        """gold 全为 0 → FN=0 → T2/T4 标记 skipped。"""
        df = pd.DataFrame({
            '最终_验证': [0] * 50,
            'llm_verified_full': [True] * 10 + [False] * 40,
            'llm_sentiment_full': ['中性'] * 50,
            '内容': ['测试'] * 50,
        })
        r = diagnose_misclassification_bias(df, '最终_验证', '_full')
        assert r['quadrant_counts']['FN'] == 0
        assert r['tests'][1]['skipped'] is True   # T2
        assert r['tests'][3]['skipped'] is True   # T4

    def test_known_bias_direction(self):
        """FP 全为正面时，T1 的 FP 均值应大于 TP 均值。"""
        df = _make_df(500, fp_bias='正面', seed=123)
        r = diagnose_misclassification_bias(df, '最终_验证', '_full')
        t1 = r['tests'][0]
        if not t1.get('skipped'):
            assert t1['mean_a'] is not None and t1['mean_b'] is not None
            assert t1['mean_a'] > t1['mean_b']

    def test_missing_column_graceful(self):
        """缺少 llm_verified 列时安全返回。"""
        df = pd.DataFrame({'最终_验证': [1, 0], '内容': ['a', 'b']})
        r = diagnose_misclassification_bias(df, '最终_验证', '_full')
        assert '缺少必要列' in r['conclusion']

    def test_csv_output(self, tmp_path):
        """CSV 文件成功写入，包含所有预期列。"""
        df = _make_df(100)
        diagnose_misclassification_bias(
            df, '最终_验证', '_full', output_dir=str(tmp_path))
        csv = tmp_path / 'misclassification_bias_diag_full.csv'
        assert csv.exists()
        csv_df = pd.read_csv(csv)
        assert len(csv_df) > 0
        for col in ['track', 'variable', 'test', 'statistic', 'p_value', 'significant']:
            assert col in csv_df.columns

    def test_ctx_track(self):
        """ctx 轨道正常运行。"""
        df = _make_df(100)
        r = diagnose_misclassification_bias(df, '最终_验证', '_ctx')
        assert r['track'] == '_ctx'
        assert len(r['tests']) >= 5
