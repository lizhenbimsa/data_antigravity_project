"""
tests/test_24_herd_decay.py — 24_herd_decay_processor.py 单元测试
=================================================================

对跟风/抄袭新闻检测与衰减加权的核心算法进行全面测试。

测试覆盖:
  1. 正常场景: 跟风检测的基本功能验证
  2. 时间窗口: 窗口内外的行为差异
  3. 边界条件: 缺失列、空数据、NaT 日期等
  4. 参数敏感性: 阈值变化对检测结果的影响
  5. 数据完整性: 列保留、公式正确性、输出格式
"""

import logging
import os
import sys

import numpy as np
import pandas as pd
import pytest

# Phase 7a-7: 注入项目父目录, 使 ``news_process.*`` 可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

# Phase 7a-7: body 已迁至 news_process.pipeline.sentiment.herd_decay,
# 旧 ``importlib.import_module('24_herd_decay_processor')`` 现仅返回 thin shim,
# 直接走规范 import 即可拿到全部内部函数与模块级常量。
from news_process.pipeline.sentiment import herd_decay as herd_module

compute_herd_weights = herd_module.compute_herd_weights


# ============================================================================
# 共享 Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def _patch_herd_logger(monkeypatch):
    """替换模块级 logger 为 NullHandler，防止污染生产日志。"""
    test_logger = logging.getLogger('test_24_herd_decay')
    test_logger.handlers.clear()
    test_logger.addHandler(logging.NullHandler())
    test_logger.setLevel(logging.DEBUG)
    monkeypatch.setattr(herd_module, 'logger', test_logger)


@pytest.fixture(autouse=True)
def _default_herd_params(monkeypatch):
    """确保每个测试使用一致的默认参数。

    注意:
      - MIN_DF=1: 小测试集需要更低的文档频率阈值
      - MAX_DF=1.0: 避免小测试集中因所有文档共享相同词汇导致 TF-IDF 词汇表为空
    """
    monkeypatch.setattr(herd_module, 'SIMILARITY_THRESHOLD', 0.35)
    monkeypatch.setattr(herd_module, 'TIME_WINDOW_DAYS', 7)
    monkeypatch.setattr(herd_module, 'MAX_FEATURES', 10000)
    monkeypatch.setattr(herd_module, 'MIN_DF', 1)
    monkeypatch.setattr(herd_module, 'MAX_DF', 1.0)


# ============================================================================
# 1. 正常场景测试
# ============================================================================

class TestComputeHerdWeightsNormal:
    """正常场景下的跟风检测测试。"""

    def test_single_article_per_bank(self):
        """每家银行仅 1 篇新闻 → 所有 herd_weight 为 1.0。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行', '建设银行'],
            '日期': ['2024-01-01', '2024-01-02'],
            '内容': [
                '工商银行推出智能风控系统利用人工智能技术进行风险管理',
                '建设银行发布区块链供应链金融平台为企业提供融资服务',
            ],
        })
        result = compute_herd_weights(df)
        assert (result['herd_weight'] == 1.0).all()
        assert (result['n_similar_articles'] == 0).all()

    def test_identical_articles_same_bank(self):
        """同一银行的高度相似文章应被标记为跟风。"""
        # 使用相似但非完全相同的文本（避免 max_df 过滤）
        base_text = '中国工商银行宣布推出人工智能风控系统，利用大数据和机器学习技术进行实时监测。'
        texts = [
            base_text * 10,
            base_text * 9 + '工商银行科技部表示将继续加大投入。' * 3,
            base_text * 8 + '该系统已在信用卡业务中成功部署。' * 5,
            base_text * 9 + '工行金融科技负责人分享了实施经验。' * 3,
            base_text * 8 + '风控系统的性能指标优异。' * 6,
        ]
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 5,
            '日期': pd.date_range('2024-01-01', periods=5, freq='D'),
            '内容': texts,
        })
        result = compute_herd_weights(df)

        # 第一篇(最早)应为原创
        assert result.iloc[0]['herd_weight'] == 1.0
        assert result.iloc[0]['n_similar_articles'] == 0

        # 至少有一些后续文章应被标记为跟风
        herd_detected = (result.iloc[1:]['herd_weight'] < 1.0).sum()
        assert herd_detected > 0, "应至少检测到 1 篇跟风新闻"

    def test_different_banks_same_text(self):
        """不同银行的相同文章不应互相影响（独立分组检测）。"""
        text = '某银行推出了创新的金融科技服务平台提供更好的客户体验和风控能力' * 10
        df = pd.DataFrame({
            'target_bank': ['工商银行', '建设银行'],
            '日期': ['2024-01-01', '2024-01-01'],
            '内容': [text, text],
        })
        result = compute_herd_weights(df)
        # 不同银行应独立处理，各自仅有 1 篇，herd_weight=1.0
        assert (result['herd_weight'] == 1.0).all()

    def test_dissimilar_articles_same_bank(self):
        """同一银行的完全不同文章不应被标记为跟风。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            '日期': pd.date_range('2024-01-01', periods=3, freq='D'),
            '内容': [
                '工商银行今日发布年度财务报告全年净利润增长百分之十五资产规模突破三十万亿' * 5,
                '北京天气晴朗最高温度二十五度空气质量优良适合户外运动和郊游活动赏花踏青' * 5,
                '中国足球超级联赛今日开幕北京国安对阵上海海港比赛精彩纷呈球迷热情高涨' * 5,
            ],
        })
        result = compute_herd_weights(df)
        # 内容差异极大，不应被标记
        assert (result['herd_weight'] == 1.0).all()

    def test_output_columns_exist(self):
        """验证输出 DataFrame 包含必需的新增列。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'],
            '日期': ['2024-01-01'],
            '内容': ['工商银行推出人工智能智能风控系统利用大数据分析' * 5],
        })
        result = compute_herd_weights(df)
        assert 'herd_weight' in result.columns
        assert 'n_similar_articles' in result.columns

    def test_herd_weight_formula(self):
        """验证衰减公式: weight = 1 / (1 + n_similar_predecessors)。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 4,
            '日期': pd.date_range('2024-01-01', periods=4, freq='D'),
            '内容': [
                '人工智能和大数据在金融领域应用的长篇详细新闻报道文章' * 20,
                '人工智能和大数据在金融领域应用的长篇详细新闻报道内容' * 20,
                '人工智能和大数据在金融领域应用的长篇详细新闻报道稿件' * 20,
                '人工智能和大数据在金融领域应用的长篇详细新闻报道消息' * 20,
            ],
        })
        result = compute_herd_weights(df)

        # 验证公式一致性：对于检测到 n 篇相似前驱的文章
        for _, row in result.iterrows():
            n_sim = row['n_similar_articles']
            expected_weight = 1.0 / (1.0 + n_sim)
            assert abs(row['herd_weight'] - expected_weight) < 1e-10, \
                f"n_similar={n_sim}, expected={expected_weight}, got={row['herd_weight']}"

    def test_herd_weight_range(self):
        """herd_weight 应始终在 (0, 1] 范围内。"""
        base = '工商银行推出人工智能大数据风控系统技术创新' * 15
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 10,
            '日期': pd.date_range('2024-01-01', periods=10, freq='D'),
            '内容': [base + f'版本{i}号更新内容' * 3 for i in range(10)],
        })
        result = compute_herd_weights(df)
        assert (result['herd_weight'] > 0).all(), "herd_weight 必须 > 0"
        assert (result['herd_weight'] <= 1.0).all(), "herd_weight 必须 ≤ 1.0"

    def test_n_similar_articles_non_negative(self):
        """n_similar_articles 应始终 ≥ 0。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 5,
            '日期': pd.date_range('2024-01-01', periods=5, freq='D'),
            '内容': [f'工商银行新闻报道第{i}篇内容金融科技' * 10 for i in range(5)],
        })
        result = compute_herd_weights(df)
        assert (result['n_similar_articles'] >= 0).all()


# ============================================================================
# 2. 时间窗口测试
# ============================================================================

class TestTimeWindow:
    """时间窗口相关的测试。"""

    def test_outside_time_window(self, monkeypatch):
        """超出时间窗口的相同文章不应被标记为跟风。"""
        monkeypatch.setattr(herd_module, 'TIME_WINDOW_DAYS', 3)
        text = '人工智能和大数据在金融领域的应用前景广阔银行科技创新' * 20
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 2,
            '日期': ['2024-01-01', '2024-01-15'],  # 间隔 14 天 > 3 天窗口
            '内容': [text, text + '微小差异'],
        })
        result = compute_herd_weights(df)
        assert (result['herd_weight'] == 1.0).all(), \
            "超出时间窗口的文章不应被标记为跟风"

    def test_within_time_window(self, monkeypatch):
        """窗口内的相似文章应被标记为跟风。"""
        monkeypatch.setattr(herd_module, 'TIME_WINDOW_DAYS', 30)
        text = '人工智能和大数据在金融领域的应用前景广阔银行科技创新' * 20
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 2,
            '日期': ['2024-01-01', '2024-01-15'],  # 间隔 14 天 < 30 天窗口
            '内容': [text, text + '微小差异'],
        })
        result = compute_herd_weights(df)
        # 第二篇应被标记（在窗口内且文本高度相似）
        assert result.iloc[1]['herd_weight'] < 1.0, \
            "窗口内的相似文章应被标记为跟风"

    def test_time_window_boundary(self, monkeypatch):
        """恰好在时间窗口边界上的文章应被检测。"""
        monkeypatch.setattr(herd_module, 'TIME_WINDOW_DAYS', 7)
        text = '人工智能和大数据在金融领域的应用前景广阔银行科技创新' * 20
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 2,
            '日期': ['2024-01-01', '2024-01-08'],  # 恰好间隔 7 天 = 窗口上限
            '内容': [text, text + '微小差异'],
        })
        result = compute_herd_weights(df)
        # 7天窗口应包含恰好7天的情况（delta_days <= TIME_WINDOW_DAYS）
        assert result.iloc[1]['herd_weight'] < 1.0, \
            "窗口边界上的文章应被检测"

    def test_time_window_just_outside(self, monkeypatch):
        """刚好超出时间窗口的文章不应被检测。"""
        monkeypatch.setattr(herd_module, 'TIME_WINDOW_DAYS', 7)
        text = '人工智能和大数据在金融领域的应用前景广阔银行科技创新' * 20
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 2,
            '日期': ['2024-01-01', '2024-01-09'],  # 间隔 8 天 > 7 天窗口
            '内容': [text, text + '微小差异'],
        })
        result = compute_herd_weights(df)
        assert (result['herd_weight'] == 1.0).all(), \
            "刚超出窗口的文章不应被标记"


# ============================================================================
# 3. 边界条件测试
# ============================================================================

class TestEdgeCases:
    """边界条件测试。"""

    def test_missing_text_column(self):
        """文本列缺失时应优雅降级。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'],
            '日期': ['2024-01-01'],
            # 没有 '内容'、'正文'、'content' 列
        })
        result = compute_herd_weights(df)
        assert (result['herd_weight'] == 1.0).all()
        assert (result['n_similar_articles'] == 0).all()

    def test_missing_target_bank_column(self):
        """缺少 target_bank 列时应优雅降级（不崩溃）。"""
        df = pd.DataFrame({
            '日期': ['2024-01-01'],
            '内容': ['工商银行推出人工智能风控系统'],
        })
        result = compute_herd_weights(df)
        assert (result['herd_weight'] == 1.0).all()
        assert (result['n_similar_articles'] == 0).all()

    def test_empty_text(self):
        """所有文本为空字符串时应不崩溃。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            '日期': pd.date_range('2024-01-01', periods=3, freq='D'),
            '内容': ['', '', ''],
        })
        result = compute_herd_weights(df)
        assert (result['herd_weight'] == 1.0).all()

    def test_none_text(self):
        """文本为 None/NaN 时应不崩溃。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            '日期': pd.date_range('2024-01-01', periods=3, freq='D'),
            '内容': [None, np.nan, ''],
        })
        result = compute_herd_weights(df)
        assert (result['herd_weight'] == 1.0).all()

    def test_nat_dates(self):
        """日期为 NaT 时应不崩溃。"""
        text = '这是一篇测试新闻报道用于验证日期处理功能和健壮性' * 20
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            '日期': [pd.NaT, '2024-01-01', pd.NaT],
            '内容': [text, text + '微小差异', text + '另外差异'],
        })
        result = compute_herd_weights(df)
        assert len(result) == 3
        assert result['herd_weight'].notna().all()

    def test_empty_dataframe(self):
        """空 DataFrame 应返回带必需列的空 DataFrame。"""
        df = pd.DataFrame({
            'target_bank': pd.Series([], dtype=str),
            '日期': pd.Series([], dtype=str),
            '内容': pd.Series([], dtype=str),
        })
        result = compute_herd_weights(df)
        assert 'herd_weight' in result.columns
        assert 'n_similar_articles' in result.columns
        assert len(result) == 0

    def test_alternative_text_column_zhengwen(self):
        """应支持 '正文' 作为备选文本列名。"""
        text = '这是一篇使用正文列名的测试新闻内容银行金融科技创新' * 20
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            '日期': pd.date_range('2024-01-01', periods=3, freq='D'),
            '正文': [text, text + '差异一', text + '差异二'],
        })
        result = compute_herd_weights(df)
        assert 'herd_weight' in result.columns

    def test_alternative_text_column_content(self):
        """应支持 'content' 作为备选文本列名。"""
        text = '这是一篇使用content列名的测试新闻银行金融科技创新内容' * 20
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            '日期': pd.date_range('2024-01-01', periods=3, freq='D'),
            'content': [text, text + '差异一', text + '差异二'],
        })
        result = compute_herd_weights(df)
        assert 'herd_weight' in result.columns

    def test_preserves_original_columns(self):
        """应保留原始 DataFrame 的所有列。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'],
            '日期': ['2024-01-01'],
            '内容': ['测试内容银行金融科技'],
            'custom_col': [42],
            'another_col': ['test'],
        })
        result = compute_herd_weights(df)
        assert 'custom_col' in result.columns
        assert result['custom_col'].iloc[0] == 42
        assert 'another_col' in result.columns
        assert result['another_col'].iloc[0] == 'test'

    def test_date_string_conversion(self):
        """日期为字符串格式时应自动转换为 datetime。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'],
            '日期': ['2024-01-01'],
            '内容': ['测试内容银行金融科技'],
        })
        result = compute_herd_weights(df)
        assert pd.api.types.is_datetime64_any_dtype(result['日期'])

    def test_two_articles_same_bank(self):
        """一家银行恰好 2 篇文章（最小可检测规模）。"""
        text = '工商银行推出人工智能大数据风控系统技术创新服务升级' * 15
        df = pd.DataFrame({
            'target_bank': ['工商银行', '工商银行'],
            '日期': ['2024-01-01', '2024-01-02'],
            '内容': [text, text + '微小差异'],
        })
        result = compute_herd_weights(df)
        # 不崩溃即可
        assert len(result) == 2
        assert result['herd_weight'].notna().all()

    def test_default_df_threshold_small_groups_no_warning(self, monkeypatch, caplog):
        """生产默认 df 阈值在小样本银行组上应自适应, 不应刷 warning。"""
        monkeypatch.setattr(herd_module, 'MIN_DF', 5)
        monkeypatch.setattr(herd_module, 'MAX_DF', 0.9)
        caplog.set_level(logging.WARNING, logger='test_24_herd_decay')

        text = '工商银行推出人工智能大数据风控系统技术创新服务升级' * 15
        df = pd.DataFrame({
            'target_bank': ['工商银行', '工商银行'],
            '日期': ['2024-01-01', '2024-01-02'],
            '内容': [text, text + '微小差异'],
        })

        # v3.6.0 在 df 没 content_ctx 时会发"内容 ctx 缺失"WARN — 该 WARN 与本测试无关
        # (本测试关注 df 阈值参数, 非轨道化). 加 content_ctx 列消除 v3.6.0 引入的噪音 WARN.
        # v3.9.0 三轨: 同理补 content_ss 列, 消除"content_ss 缺失"噪音 WARN。
        df['content_ctx'] = df['内容']
        df['content_ss'] = df['内容']

        result = compute_herd_weights(df)

        assert len(result) == 2
        assert result['herd_weight'].notna().all()
        assert not [r for r in caplog.records if r.levelno >= logging.WARNING]


# ============================================================================
# 4. 阈值参数化测试
# ============================================================================

class TestThresholdSensitivity:
    """阈值敏感性测试。"""

    def test_high_threshold_reduces_detection(self, monkeypatch):
        """高相似度阈值应减少跟风检测数量。"""
        monkeypatch.setattr(herd_module, 'SIMILARITY_THRESHOLD', 0.99)
        base = '人工智能和大数据在金融领域的应用前景广阔' * 15
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            '日期': pd.date_range('2024-01-01', periods=3, freq='D'),
            '内容': [
                base,
                base + '工商银行积极推动数字化转型' * 3,
                base + '银行业金融科技投入持续增加' * 3,
            ],
        })
        result_high = compute_herd_weights(df)
        n_herd_high = (result_high['herd_weight'] < 1.0).sum()

        # 低阈值
        monkeypatch.setattr(herd_module, 'SIMILARITY_THRESHOLD', 0.1)
        df2 = df.copy()
        df2['herd_weight'] = 1.0
        df2['n_similar_articles'] = 0
        result_low = compute_herd_weights(df2)
        n_herd_low = (result_low['herd_weight'] < 1.0).sum()

        # 低阈值应检测到更多（或相同数量）的跟风文章
        assert n_herd_low >= n_herd_high, \
            f"低阈值检测数({n_herd_low}) 应 >= 高阈值检测数({n_herd_high})"

    def test_zero_threshold_maximizes_detection(self, monkeypatch):
        """零阈值应最大化跟风检测（任何非零相似度都触发）。"""
        monkeypatch.setattr(herd_module, 'SIMILARITY_THRESHOLD', 0.0)
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            '日期': pd.date_range('2024-01-01', periods=3, freq='D'),
            '内容': [
                '工商银行大数据风控系统人工智能金融科技技术创新' * 10,
                '建设银行区块链供应链金融平台数字化转型服务升级' * 10,
                '中国银行云计算数字支付智能客服机器学习深度学习' * 10,
            ],
        })
        result = compute_herd_weights(df)
        # 阈值为 0 时，只要余弦相似度 >= 0（几乎总是），就标记为跟风
        # 至少应有 1 篇被标记
        n_herd = (result['herd_weight'] < 1.0).sum()
        assert n_herd > 0, "零阈值时至少应检测到 1 篇跟风"


# ============================================================================
# 5. 多银行混合场景测试
# ============================================================================

class TestMultiBankScenarios:
    """多银行混合场景测试。"""

    def test_mixed_banks_independent(self):
        """多家银行混合时，检测应在各银行内独立进行。"""
        text_a = '工商银行推出智能风控系统利用大数据进行实时监测' * 15
        text_b = '建设银行发布区块链供应链金融平台服务中小企业' * 15

        df = pd.DataFrame({
            'target_bank': ['工商银行', '建设银行', '工商银行', '建设银行'],
            '日期': ['2024-01-01', '2024-01-01', '2024-01-02', '2024-01-02'],
            '内容': [text_a, text_b, text_a + '微小差异', text_b + '微小差异'],
        })
        result = compute_herd_weights(df)

        # 工商银行和建设银行应独立处理
        icbc_results = result[result['target_bank'] == '工商银行']
        ccb_results = result[result['target_bank'] == '建设银行']

        # 各自的第一篇应为原创(按日期排序后, 即最早的那篇)
        for bank_df in [icbc_results, ccb_results]:
            sorted_bank = bank_df.sort_values('日期')
            assert sorted_bank.iloc[0]['herd_weight'] == 1.0

    def test_many_banks_no_crash(self):
        """大量银行（50家）时不应崩溃且在合理时间内完成。"""
        n_banks = 50
        n_articles_per_bank = 3
        rows = []
        for i in range(n_banks):
            bank_name = f'银行{i:03d}'
            for j in range(n_articles_per_bank):
                rows.append({
                    'target_bank': bank_name,
                    '日期': f'2024-01-{j+1:02d}',
                    '内容': f'{bank_name}推出金融科技创新服务产品方案数字化' * 10,
                })
        df = pd.DataFrame(rows)
        result = compute_herd_weights(df)
        assert len(result) == n_banks * n_articles_per_bank
        assert result['herd_weight'].notna().all()

    def test_temporal_ordering(self):
        """验证跟风检测严格遵循时间因果（只有更早的文章才能是原创）。"""
        text = '银行金融科技创新技术发展大数据人工智能应用' * 20
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            # 故意打乱输入顺序
            '日期': ['2024-01-03', '2024-01-01', '2024-01-02'],
            '内容': [text + '参考差异', text, text + '微小差异'],
        })
        result = compute_herd_weights(df)

        # 最早的文章(01-01)应为原创
        earliest = result[result['日期'] == pd.Timestamp('2024-01-01')]
        assert earliest.iloc[0]['herd_weight'] == 1.0
        assert earliest.iloc[0]['n_similar_articles'] == 0


# ============================================================================
# 6. 数据类型与格式测试
# ============================================================================

class TestDataTypesAndFormat:
    """数据类型和格式相关的测试。"""

    def test_herd_weight_dtype(self):
        """herd_weight 应为浮点型。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'],
            '日期': ['2024-01-01'],
            '内容': ['测试内容银行金融科技'],
        })
        result = compute_herd_weights(df)
        assert result['herd_weight'].dtype in [np.float64, float]

    def test_n_similar_articles_dtype(self):
        """n_similar_articles 应为整型或可转为整型。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 2,
            '日期': pd.date_range('2024-01-01', periods=2, freq='D'),
            '内容': ['测试内容银行金融科技' * 10] * 2,
        })
        result = compute_herd_weights(df)
        # 值应为整数
        for val in result['n_similar_articles']:
            assert val == int(val)

    def test_row_count_preserved(self):
        """输出行数应与输入行数完全一致。"""
        n = 15
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * n,
            '日期': pd.date_range('2024-01-01', periods=n, freq='D'),
            '内容': [f'新闻报道第{i}篇银行科技创新金融' * 8 for i in range(n)],
        })
        result = compute_herd_weights(df)
        assert len(result) == n

    def test_index_preserved(self):
        """原始 DataFrame 的索引应被完整保留。"""
        df = pd.DataFrame({
            'target_bank': ['工商银行'] * 3,
            '日期': pd.date_range('2024-01-01', periods=3, freq='D'),
            '内容': ['测试内容银行金融科技' * 10] * 3,
        }, index=[10, 20, 30])
        result = compute_herd_weights(df)
        assert list(result.index) == [10, 20, 30]
