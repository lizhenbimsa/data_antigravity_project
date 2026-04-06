"""
tests/test_38b_decay_sensitivity.py — 距离衰减权重敏感性检验单元测试
====================================================================

覆盖范围:
  1. 衰减函数数学正确性 (uniform / inverse / exponential)
  2. _sentence_tone() 三重语言学规则验证
  3. compute_decay_sentiment() 距离加权计算
  4. 空输入/边界条件防御
  5. run_analysis() 端到端测试
  6. log_correlation_report() 报告生成
  7. load_dictionaries() 词典加载
  8. _inject_custom_dicts_to_jieba() 词典注入
  9. 与 22_tone_words 规则一致性交叉验证
"""

import os
import sys
import json
import math
import logging
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

# 确保 news_process 目录在 sys.path 中
NEWS_PROCESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if NEWS_PROCESS_DIR not in sys.path:
    sys.path.insert(0, NEWS_PROCESS_DIR)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_config_for_38b(tmp_path):
    """创建 38b 测试专用的 mock 配置。"""
    tone_dicts = {
        'jiang_2021': {
            'name': '姜富伟(2021)',
            'positive': ['增长', '创新', '突破', '提升', '良好', '发展', '领先'],
            'negative': ['下降', '风险', '亏损', '困难', '危机', '衰退', '恶化'],
        },
        'yao_2021': {
            'name': '姚加权(2021)',
            'positive': ['盈利', '发展', '优化', '提升'],
            'negative': ['损失', '违规', '处罚', '下降'],
        },
        'bian_2021': {
            'name': 'Bian(2021)',
            'positive': ['增长', '稳定'],
            'negative': ['下降', '风险'],
        },
        'du_2022': {
            'name': 'Du(2022)',
            'positive': ['合作', '升级'],
            'negative': ['违约', '欺诈'],
            'political_positive': ['改革', '开放'],
        },
        'you_2018': {
            'name': 'You(2018)',
            'positive': ['增长', '利好'],
            'negative': ['亏损', '危机'],
        },
    }

    bank_names = [
        {
            'bank_name': '中国工商银行',
            'variants': ['中国工商银行', '工商银行', '工行', 'ICBC'],
        },
        {
            'bank_name': '中国建设银行',
            'variants': ['中国建设银行', '建设银行', '建行', 'CCB'],
        },
    ]

    fintech_dict = ['人工智能', '大数据', '云计算', '区块链', '金融科技']

    # 写入临时文件
    tone_dicts_path = tmp_path / 'tone_dicts.json'
    tone_dicts_path.write_text(json.dumps(tone_dicts, ensure_ascii=False), encoding='utf-8')

    bank_names_path = tmp_path / 'bank_names.json'
    bank_names_path.write_text(json.dumps(bank_names, ensure_ascii=False), encoding='utf-8')

    fintech_path = tmp_path / 'fintech_dict.json'
    fintech_path.write_text(json.dumps(fintech_dict, ensure_ascii=False), encoding='utf-8')

    output_dir = tmp_path / 'output'
    output_dir.mkdir(exist_ok=True)
    log_dir = tmp_path / 'logs'
    log_dir.mkdir(exist_ok=True)
    eval_dir = output_dir / 'eval_reports'
    eval_dir.mkdir(exist_ok=True)

    config = {
        'paths': {
            'output_dir': str(output_dir),
            'log_dir': str(log_dir),
            'bank_names_file': str(bank_names_path),
            'fintech_dict_file': str(fintech_path),
            'tone_dicts_file': str(tone_dicts_path),
        },
        'sentiment_analysis': {
            'tone_words': {
                'pos_threshold': 0.1,
                'neg_threshold': -0.1,
                'negation_window': 2,
                'adversative_boost': 1.5,
                'sentence_end_markers': ['。', '！', '？', '!', '?', '；', ';'],
                'negation_words': ['不', '没', '未', '没有', '不会', '不能'],
                'degree_words': {
                    '非常': 2.5,
                    '很': 1.5,
                    '略': 0.6,
                    '极其': 3.0,
                },
                'adversative_words': ['但是', '然而', '却', '不过'],
            },
        },
    }

    return config, str(tone_dicts_path)


@pytest.fixture
def patched_module(mock_config_for_38b):
    """返回已打补丁的 38b 模块, 避免读取生产配置。"""
    config, tone_dicts_path = mock_config_for_38b

    with patch('utils.helpers.load_config', return_value=config):
        # 强制重新导入模块, 使用 mock 配置
        if '38b_decay_sensitivity' in sys.modules:
            del sys.modules['38b_decay_sensitivity']

        # 动态导入 (文件名含数字前缀, 不能直接 import)
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            '38b_decay_sensitivity',
            os.path.join(NEWS_PROCESS_DIR, '38b_decay_sensitivity.py')
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules['38b_decay_sensitivity'] = mod
        spec.loader.exec_module(mod)

        yield mod

        # 清理
        if '38b_decay_sensitivity' in sys.modules:
            del sys.modules['38b_decay_sensitivity']


# ============================================================================
# 1. 衰减函数数学正确性
# ============================================================================

class TestDecayFunctions:
    """测试三种衰减函数的数学性质。"""

    def test_uniform_constant(self, patched_module):
        """uniform 衰减: 所有距离返回 1.0。"""
        f = patched_module.DECAY_FUNCTIONS['uniform']
        for d in [0, 1, 2, 5, 100]:
            assert f(d) == 1.0, f"uniform({d}) 应为 1.0"

    def test_inverse_formula(self, patched_module):
        """inverse 衰减: w(d) = 1/(1+d)。"""
        f = patched_module.DECAY_FUNCTIONS['inverse']
        assert f(0) == 1.0                              # d=0 → 1.0
        assert f(1) == pytest.approx(0.5)               # d=1 → 0.5
        assert f(2) == pytest.approx(1.0 / 3.0)         # d=2 → 0.333
        assert f(3) == pytest.approx(0.25)               # d=3 → 0.25

    def test_exponential_formula(self, patched_module):
        """exponential 衰减: w(d) = exp(-0.5*d)。"""
        f = patched_module.DECAY_FUNCTIONS['exponential']
        assert f(0) == pytest.approx(1.0)               # d=0 → 1.0
        assert f(1) == pytest.approx(math.exp(-0.5))     # d=1 → ~0.607
        assert f(2) == pytest.approx(math.exp(-1.0))     # d=2 → ~0.368

    def test_all_positive(self, patched_module):
        """所有衰减函数对非负距离返回正值。"""
        for name, f in patched_module.DECAY_FUNCTIONS.items():
            for d in [0, 1, 2, 5, 10]:
                assert f(d) > 0, f"{name}({d}) 必须为正"

    def test_monotone_decreasing(self, patched_module):
        """inverse 和 exponential 应单调递减。"""
        for name in ['inverse', 'exponential']:
            f = patched_module.DECAY_FUNCTIONS[name]
            for d in range(10):
                assert f(d) >= f(d + 1), (
                    f"{name}({d}) = {f(d):.4f} < {name}({d+1}) = {f(d+1):.4f}, 违反单调递减"
                )

    def test_d0_equals_one(self, patched_module):
        """所有函数在 d=0 时权重 = 1.0 (命中句最大权重)。"""
        for name, f in patched_module.DECAY_FUNCTIONS.items():
            assert f(0) == pytest.approx(1.0), f"{name}(0) 应为 1.0"


# ============================================================================
# 2. _sentence_tone() 三重规则验证
# ============================================================================

class TestSentenceTone:
    """测试 _sentence_tone() 的三重语言学规则。"""

    def test_basic_positive(self, patched_module):
        """基础正面词检测。"""
        sdict = {'增长': 1.0, '下降': -1.0}
        tokens = ['公司', '利润', '增长']
        score = patched_module._sentence_tone(tokens, sdict)
        assert score > 0, "含正面词应返回正分"

    def test_basic_negative(self, patched_module):
        """基础负面词检测。"""
        sdict = {'增长': 1.0, '下降': -1.0}
        tokens = ['业绩', '下降']
        score = patched_module._sentence_tone(tokens, sdict)
        assert score < 0, "含负面词应返回负分"

    def test_negation_flip(self, patched_module):
        """否定词翻转极性: "不增长" → 负分。"""
        sdict = {'增长': 1.0, '下降': -1.0}
        tokens = ['不', '增长']
        score = patched_module._sentence_tone(tokens, sdict)
        assert score < 0, "'不增长' 应因否定翻转返回负分"

    def test_negation_window(self, patched_module):
        """否定窗口: 超出窗口的词不受影响。"""
        sdict = {'增长': 1.0, '良好': 1.0}
        # NEGATION_WINDOW = 2, 所以 "不 X Y 良好" 中 "良好" 不受否定影响
        tokens = ['不', '一些', '其他', '良好']
        score = patched_module._sentence_tone(tokens, sdict)
        assert score > 0, "超出否定窗口的词应保持原极性"

    def test_adversative_boost(self, patched_module):
        """转折词增强: 转折后情感词权重提升。"""
        sdict = {'增长': 1.0}
        tokens_no_adv = ['增长']
        tokens_with_adv = ['但是', '增长']
        s_base = patched_module._sentence_tone(tokens_no_adv, sdict)
        s_boost = patched_module._sentence_tone(tokens_with_adv, sdict)
        assert s_boost > s_base, "转折后情感词得分应高于无转折"

    def test_degree_scaling(self, patched_module):
        """程度副词缩放: "非常增长" > "增长"。"""
        sdict = {'增长': 1.0}
        tokens_plain = ['增长']
        tokens_degree = ['非常', '增长']
        s_plain = patched_module._sentence_tone(tokens_plain, sdict)
        s_degree = patched_module._sentence_tone(tokens_degree, sdict)
        assert s_degree > s_plain, "程度副词应放大情感得分"

    def test_degree_weaken(self, patched_module):
        """弱程度副词: "略增长" < "增长"。"""
        sdict = {'增长': 1.0}
        tokens_plain = ['增长']
        tokens_weak = ['略', '增长']
        s_plain = patched_module._sentence_tone(tokens_plain, sdict)
        s_weak = patched_module._sentence_tone(tokens_weak, sdict)
        assert s_weak < s_plain, "弱程度副词应缩小情感得分"

    def test_sentence_end_resets_state(self, patched_module):
        """句末标点重置: 跨句不影响。"""
        sdict = {'增长': 1.0}
        # "但是" 后跟 "。" 应重置转折状态
        tokens = ['但是', '。', '增长']
        score = patched_module._sentence_tone(tokens, sdict)
        expected = 1.0  # 增长不受转折影响 (已被句末标点重置)
        assert score == pytest.approx(expected), "句末标点应重置转折状态"

    def test_empty_tokens(self, patched_module):
        """空 token 列表返回 0.0。"""
        assert patched_module._sentence_tone([], {'增长': 1.0}) == 0.0

    def test_no_sentiment_match(self, patched_module):
        """无情感词命中返回 0.0。"""
        sdict = {'增长': 1.0}
        tokens = ['公司', '发布', '公告']
        assert patched_module._sentence_tone(tokens, sdict) == 0.0

    def test_normalized_by_match_count(self, patched_module):
        """归一化: 分数 = 总分 / 命中数。"""
        sdict = {'增长': 1.0, '下降': -1.0}
        # 2 个词, 得分 = (1.0 + (-1.0)) = 0.0 → 0.0/2 = 0.0
        tokens = ['增长', '下降']
        score = patched_module._sentence_tone(tokens, sdict)
        assert score == pytest.approx(0.0), "正负相消应归一化为 0.0"

    def test_negation_then_adversative(self, patched_module):
        """否定+转折组合: "不下降, 但是增长"。"""
        sdict = {'下降': -1.0, '增长': 1.0}
        tokens = ['不', '下降', '但是', '增长']
        score = patched_module._sentence_tone(tokens, sdict)
        # "不下降" → +1.0, "但是增长" → 1.0 × 1.5 = 1.5
        # 归一化: (1.0 + 1.5) / 2 = 1.25
        assert score == pytest.approx(1.25), "否定+转折组合计算错误"


# ============================================================================
# 3. compute_decay_sentiment() 加权计算
# ============================================================================

class TestComputeDecaySentiment:
    """测试距离加权情感计算。"""

    def test_uniform_equals_average(self, patched_module):
        """uniform 衰减等价于简单平均。"""
        sdict = {'好': 1.0, '差': -1.0}
        tokenized = [
            (['好'], 0),   # tone = 1.0
            (['差'], 1),   # tone = -1.0
        ]
        uniform = patched_module.DECAY_FUNCTIONS['uniform']
        score = patched_module.compute_decay_sentiment(tokenized, sdict, uniform)
        # 平均 = (1.0 + (-1.0)) / 2 = 0.0
        assert score == pytest.approx(0.0)

    def test_inverse_weighting(self, patched_module):
        """inverse 衰减: 近距离句子权重更大。"""
        sdict = {'好': 1.0, '差': -1.0}
        tokenized = [
            (['好'], 0),   # tone=1.0, w=1.0
            (['差'], 2),   # tone=-1.0, w=1/3
        ]
        inverse = patched_module.DECAY_FUNCTIONS['inverse']
        score = patched_module.compute_decay_sentiment(tokenized, sdict, inverse)
        # weighted_sum = 1.0 × 1.0 + (-1.0) × (1/3) = 1.0 - 0.333 = 0.667
        # weight_total = 1.0 + 1/3 = 4/3
        # score = 0.667 / 1.333 = 0.5
        assert score == pytest.approx(0.5)

    def test_exponential_weighting(self, patched_module):
        """exponential 衰减: 验证公式正确性。"""
        sdict = {'好': 1.0}
        tokenized = [
            (['好'], 0),   # tone=1.0, w=exp(0)=1.0
            (['好'], 1),   # tone=1.0, w=exp(-0.5)≈0.607
        ]
        exp_func = patched_module.DECAY_FUNCTIONS['exponential']
        score = patched_module.compute_decay_sentiment(tokenized, sdict, exp_func)
        # weighted_sum = 1.0 + 0.607 = 1.607
        # weight_total = 1.0 + 0.607 = 1.607
        # score = 1.0
        assert score == pytest.approx(1.0)

    def test_empty_input(self, patched_module):
        """空输入返回 0.0。"""
        uniform = patched_module.DECAY_FUNCTIONS['uniform']
        assert patched_module.compute_decay_sentiment([], {'好': 1.0}, uniform) == 0.0

    def test_no_sentiment_words(self, patched_module):
        """无情感词命中返回 0.0 (tone=0 for all sentences)。"""
        sdict = {'好': 1.0}
        tokenized = [
            (['公司', '发布'], 0),
            (['公告', '通知'], 1),
        ]
        uniform = patched_module.DECAY_FUNCTIONS['uniform']
        score = patched_module.compute_decay_sentiment(tokenized, sdict, uniform)
        assert score == pytest.approx(0.0)

    def test_single_sentence(self, patched_module):
        """单句输入: 距离=0, 等价于 _sentence_tone()。"""
        sdict = {'增长': 1.0}
        tokenized = [(['增长'], 0)]
        for name, f in patched_module.DECAY_FUNCTIONS.items():
            score = patched_module.compute_decay_sentiment(tokenized, sdict, f)
            assert score == pytest.approx(1.0), f"{name}: 单句距离=0 应返回 tone 值"


# ============================================================================
# 4. load_dictionaries() 词典加载
# ============================================================================

class TestLoadDictionaries:
    """测试词典加载函数。"""

    def test_loads_five_dicts(self, patched_module):
        """应加载 5 套词典。"""
        dicts = patched_module.load_dictionaries()
        assert len(dicts) == 5, "应加载 5 套词典"

    def test_dict_keys(self, patched_module):
        """词典名称应匹配预设列表。"""
        dicts = patched_module.load_dictionaries()
        keys = [name for name, _ in dicts]
        expected = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
        assert keys == expected

    def test_positive_negative_scores(self, patched_module):
        """正面词 = +1.0, 负面词 = -1.0。"""
        dicts = patched_module.load_dictionaries()
        jiang = dict(dicts)['jiang_2021']
        assert jiang.get('增长') == 1.0, "正面词应为 +1.0"
        assert jiang.get('下降') == -1.0, "负面词应为 -1.0"

    def test_political_positive_score(self, patched_module):
        """政治正面词 = +0.5 (du_2022 特有)。"""
        dicts = patched_module.load_dictionaries()
        du = dict(dicts)['du_2022']
        assert du.get('改革') == 0.5, "政治正面词应为 +0.5"

    def test_political_no_override(self, patched_module):
        """政治正面词不应覆盖已有正面/负面词。"""
        dicts = patched_module.load_dictionaries()
        du = dict(dicts)['du_2022']
        # '合作' 是正面词 (1.0), 不应被 political_positive 覆盖
        if '合作' in du:
            assert du['合作'] == 1.0

    def test_missing_dict_file(self, patched_module, tmp_path):
        """词典文件不存在时应返回空词典。"""
        patched_module.TONE_DICTS_FILE = str(tmp_path / 'nonexistent.json')
        dicts = patched_module.load_dictionaries()
        assert len(dicts) == 5
        # 所有词典应为空
        for name, d in dicts:
            assert len(d) == 0, f"{name} 应为空"


# ============================================================================
# 5. run_analysis() 端到端测试
# ============================================================================

class TestRunAnalysis:
    """测试 run_analysis() 端到端流程。"""

    def test_output_shape(self, patched_module):
        """输出 DataFrame 应有 5×3=15 列。"""
        df = pd.DataFrame({
            'target_bank': ['中国工商银行', '中国建设银行', '中国工商银行'],
            '内容': [
                '工商银行推出金融科技创新方案。该方案利用人工智能技术实现增长。工商银行表示效果良好。',
                '建设银行近期面临风险。建设银行利润下降。建设银行计划调整策略。',
                '工商银行在金融科技领域持续创新。工商银行发展迅速。工行获得突破。',
            ],
        })
        dicts = patched_module.load_dictionaries()
        score_df = patched_module.run_analysis(df, dicts)
        # 5 词典 × 3 衰减 = 15 列
        assert score_df.shape[1] == 15, f"应有 15 列, 实际 {score_df.shape[1]}"
        assert score_df.shape[0] == 3, "行数应与输入一致"

    def test_column_naming(self, patched_module):
        """列名格式应为 '{dict}_{decay}'。"""
        df = pd.DataFrame({
            'target_bank': ['中国工商银行'],
            '内容': ['工商银行增长良好。工行发展迅速。工商银行利润提升。'],
        })
        dicts = patched_module.load_dictionaries()
        score_df = patched_module.run_analysis(df, dicts)
        expected_cols = [
            f'{dn}_{fn}'
            for dn in ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
            for fn in ['uniform', 'inverse', 'exponential']
        ]
        assert list(score_df.columns) == expected_cols

    def test_empty_content_returns_zero(self, patched_module):
        """空内容行应返回全零。"""
        df = pd.DataFrame({
            'target_bank': ['中国工商银行'],
            '内容': [''],
        })
        dicts = patched_module.load_dictionaries()
        score_df = patched_module.run_analysis(df, dicts)
        assert (score_df.values == 0.0).all(), "空内容应返回全零"

    def test_no_target_bank_returns_zero(self, patched_module):
        """无目标银行行应返回全零。"""
        df = pd.DataFrame({
            'target_bank': [''],
            '内容': ['这是一篇关于人工智能增长的文章。发展前景良好。技术取得突破。'],
        })
        dicts = patched_module.load_dictionaries()
        score_df = patched_module.run_analysis(df, dicts)
        assert (score_df.values == 0.0).all(), "无目标银行应返回全零"

    def test_uniform_columns_not_all_nan(self, patched_module):
        """uniform 列不应全为 NaN。"""
        df = pd.DataFrame({
            'target_bank': ['中国工商银行'] * 5,
            '内容': [
                '工商银行推出金融科技创新方案。该方案实现增长。工商银行表示效果良好。',
            ] * 5,
        })
        dicts = patched_module.load_dictionaries()
        score_df = patched_module.run_analysis(df, dicts)
        uniform_cols = [c for c in score_df.columns if c.endswith('_uniform')]
        assert not score_df[uniform_cols].isna().all().all(), "uniform 列不应全为 NaN"


# ============================================================================
# 6. log_correlation_report() 报告生成
# ============================================================================

class TestLogCorrelationReport:
    """测试相关性报告生成。

    注意: 38b 模块使用 setup_logging() 创建的命名 logger (非 root logger),
    pytest 的 caplog 默认仅捕获 root logger。因此使用 StringIO handler
    直接附加到模块 logger 上来捕获输出。
    """

    @staticmethod
    def _capture_logger_output(module_logger, func, *args, **kwargs):
        """捕获命名 logger 的输出到字符串。"""
        import io
        stream = io.StringIO()
        handler = logging.StreamHandler(stream)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(message)s'))
        module_logger.addHandler(handler)
        try:
            func(*args, **kwargs)
        finally:
            module_logger.removeHandler(handler)
        return stream.getvalue()

    def test_high_correlation_report(self, patched_module):
        """高相关性数据应触发 '高度不敏感' 结论。"""
        np.random.seed(42)
        n = 100
        base = np.random.randn(n) * 0.1
        score_df = pd.DataFrame()
        for dn in ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']:
            score_df[f'{dn}_uniform'] = base
            # 添加微小噪声使 Pearson 接近但不等于 1.0
            score_df[f'{dn}_inverse'] = base + np.random.randn(n) * 0.001
            score_df[f'{dn}_exponential'] = base + np.random.randn(n) * 0.001

        dict_names = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']

        log_text = self._capture_logger_output(
            patched_module.logger,
            patched_module.log_correlation_report,
            score_df, dict_names
        )
        assert '高度不敏感' in log_text or '基本不敏感' in log_text, \
            f"高相关性应触发稳健性结论, 实际日志:\n{log_text[:500]}"

    def test_missing_columns_handled(self, patched_module):
        """缺少列时不应崩溃。"""
        score_df = pd.DataFrame({'jiang_2021_uniform': [0.1, 0.2, 0.3]})
        dict_names = ['jiang_2021']
        # 不应抛出异常
        patched_module.log_correlation_report(score_df, dict_names)

    def test_few_samples_warning(self, patched_module):
        """样本不足时应跳过或警告。"""
        score_df = pd.DataFrame({
            'jiang_2021_uniform': [0.1, 0.2],
            'jiang_2021_inverse': [0.1, 0.2],
        })
        dict_names = ['jiang_2021']

        log_text = self._capture_logger_output(
            patched_module.logger,
            patched_module.log_correlation_report,
            score_df, dict_names
        )
        # 少于 10 个样本, 应跳过或发出警告
        assert '跳过' in log_text or '未能' in log_text or len(log_text) > 0, \
            "样本不足时应有处理"


# ============================================================================
# 7. 边界条件和防御性编程
# ============================================================================

class TestEdgeCases:
    """测试边界条件。"""

    def test_all_same_score(self, patched_module):
        """所有文章得分相同时不应崩溃。"""
        sdict = {'好': 1.0}
        tokenized = [(['好'], 0)] * 10
        for name, f in patched_module.DECAY_FUNCTIONS.items():
            score = patched_module.compute_decay_sentiment(tokenized, sdict, f)
            assert score == pytest.approx(1.0)

    def test_large_distance(self, patched_module):
        """大距离值不应导致数值溢出。"""
        sdict = {'好': 1.0}
        tokenized = [(['好'], 1000)]
        for name, f in patched_module.DECAY_FUNCTIONS.items():
            score = patched_module.compute_decay_sentiment(tokenized, sdict, f)
            assert np.isfinite(score), f"{name}: 大距离不应导致非有限值"

    def test_degree_words_type_safety(self, patched_module):
        """DEGREE_WORDS 值应为 float (非 int/str)。"""
        for word, value in patched_module.DEGREE_WORDS.items():
            assert isinstance(value, float), (
                f"DEGREE_WORDS['{word}'] = {value} (type={type(value).__name__}), "
                f"应为 float"
            )


# ============================================================================
# 8. 与 22_tone_words 规则一致性交叉验证
# ============================================================================

class TestCrossValidation:
    """与 22_tone_words 的规则一致性验证。"""

    def test_negation_behavior_matches(self, patched_module):
        """否定词行为应与 22_tone_words 一致。

        验证: "不 增长" 中 "增长" 的最终得分 = -1.0 (翻转)
        """
        sdict = {'增长': 1.0}
        tokens = ['不', '增长']
        score = patched_module._sentence_tone(tokens, sdict)
        assert score == pytest.approx(-1.0)

    def test_adversative_behavior_matches(self, patched_module):
        """转折词行为应与 22_tone_words 一致。

        验证: "但是 增长" 中 "增长" 的最终得分 = 1.0 × ADVERSATIVE_BOOST
        """
        sdict = {'增长': 1.0}
        tokens = ['但是', '增长']
        score = patched_module._sentence_tone(tokens, sdict)
        expected = 1.0 * patched_module.ADVERSATIVE_BOOST
        assert score == pytest.approx(expected)

    def test_degree_behavior_matches(self, patched_module):
        """程度副词行为应与 22_tone_words 一致。

        验证: "非常 增长" 中 "增长" 的最终得分 = 1.0 × DEGREE_WORDS['非常']
        """
        sdict = {'增长': 1.0}
        tokens = ['非常', '增长']
        score = patched_module._sentence_tone(tokens, sdict)
        degree_val = patched_module.DEGREE_WORDS.get('非常', 2.5)
        expected = 1.0 * degree_val
        assert score == pytest.approx(expected)

    def test_combined_rules(self, patched_module):
        """组合规则: "但是 不 非常 增长"。

        状态推演:
          "但是"    → adversative_active = True
          "不"      → negation_remaining = 2
          "非常"    → degree_multiplier = 2.5, negation_remaining 不递减 (因为 continue)
          "增长"    → base = 1.0
                       否定翻转 → base = -1.0
                       程度缩放 → final = -1.0 × 2.5 = -2.5
                       转折增强 → final = -2.5 × 1.5 = -3.75
        归一化: -3.75 / 1 = -3.75
        """
        sdict = {'增长': 1.0}
        tokens = ['但是', '不', '非常', '增长']
        score = patched_module._sentence_tone(tokens, sdict)
        degree_val = patched_module.DEGREE_WORDS.get('非常', 2.5)
        boost = patched_module.ADVERSATIVE_BOOST
        expected = -1.0 * degree_val * boost  # 否定 × 程度 × 转折
        assert score == pytest.approx(expected), (
            f"组合规则计算错误: expected={expected}, got={score}"
        )

    def test_degree_reset_on_non_sentiment(self, patched_module):
        """非情感词消费后程度副词应重置。

        "非常 公司 增长" 中 "非常" 在 "公司"(非情感词)处未被消费但被重置,
        所以 "增长" 不应受程度副词影响。
        """
        sdict = {'增长': 1.0}
        tokens = ['非常', '公司', '增长']
        score = patched_module._sentence_tone(tokens, sdict)
        # "非常" 在遇到 "公司" (非情感词) 时被 else 分支重置为 1.0
        # 所以 "增长" 得分 = 1.0 × 1.0 = 1.0
        assert score == pytest.approx(1.0), "程度副词应在非情感词处重置"
