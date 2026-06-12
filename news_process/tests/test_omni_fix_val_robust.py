"""
tests/test_omni_fix_val_robust.py — omni 修复组 g-val-robust 回归锁
====================================================================

锁定 2026-06-11 omni 审计修复后的行为 (防静默 revert):

  - g-val-robust-01: dedup_threshold 敏感性输入优先预去重语料 (_cache),
    回退口径逐行标记 Mechanically_Censored (单侧截尾披露)
  - g-val-robust-02: dict_coverage 分析 3 死词/覆盖率措辞限定为
    "通过分类的文章中" (选择后样本口径), 撤回全语料清理建议
  - g-val-robust-03: radius_sensitivity 热力图相关矩阵复用零方差守卫
    (常量输入 → NaN, 不再裸调 pearsonr 渲染 'nan' 进附录图)
  - g-val-robust-04: decay_sensitivity 结论/论文用语限定为衰减权重族内
    (radius=2), 不再声称 "主结果对权重方案不敏感"
  - g-val-robust-05: media_diversity Pielou J' 在 S=1 时返回 NaN (不适用),
    不再硬编码 1.0 ("完全均匀") 与 HHI=1 自相矛盾
  - omni-extra-threshold-condb: threshold.py 银行模拟路径 B 用正文
    total (upper+lower) 对齐生产 analyze_bank_matches
  - omni-extra-dictcov-5b: dict_coverage 分析 5b 死分支移除 + 诚实披露

全部用合成 DataFrame, 不依赖盘上大数据, 不调外部 API。

# 白话: 这组测试锁的是几个稳健性检验模块的"诚实度"修复: 去重阈值敏感性要用
# 去重前的语料当输入, 用不了就标明结果被单侧截断; 词典覆盖率结论只能说"在
# 通过分类的文章里"而不能说"全部语料里"; 相关矩阵遇到常数输入时写 NaN 而不是
# 渲染 'nan' 进图; 衰减权重的结论不能夸大成"主结果不敏感"; 只有一家媒体时
# 均匀度指标本来就没定义, 该是 NaN 就 NaN, 不硬写 1.0。
"""

import json
import math
import os
import sys
import warnings

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)


class _RecLogger:
    """轻量日志记录器替身: 捕获各级日志文本供断言。"""

    def __init__(self):
        self.lines = []

    def _log(self, msg, *args):
        text = str(msg)
        if args:
            try:
                text = text % args
            except TypeError:
                pass
        self.lines.append(text)

    info = _log
    warning = _log
    error = _log
    debug = _log

    def joined(self) -> str:
        return "\n".join(self.lines)


# ============================================================================
# omni-extra-threshold-condb: 银行分类模拟路径 B 对齐生产正文口径
# ============================================================================

class TestThresholdCondB:
    """fix(omni-extra-threshold-condb, 2026-06-11)。"""

    @pytest.fixture(scope="class")
    def mod(self):
        from news_process.validation import threshold
        return threshold

    def test_title_only_no_body_rejected(self, mod):
        """标题-only 提及 (正文 0 次) 不得走 cond_b — 生产口径正文 total >= min_upper。"""
        matches = [
            {'bank_counts': {'工商银行': {'total': 3, 'upper': 0, 'lower': 0, 'title': 1}}}
        ]
        assert mod.simulate_bank_classification_from_precomputed(matches, 1, 1, 3) == 0

    def test_title_plus_body_passes(self, mod):
        """标题 + 正文达标走 cond_b (与生产 analyze_bank_matches 路径 B 一致)。"""
        matches = [
            {'bank_counts': {'工商银行': {'total': 3, 'upper': 2, 'lower': 0, 'title': 1}}}
        ]
        assert mod.simulate_bank_classification_from_precomputed(matches, 1, 1, 3) == 1

    def test_cond_a_unchanged(self, mod):
        """路径 A (上下半分布) 行为不受修复影响。"""
        matches = [
            {'bank_counts': {'工商银行': {'total': 5, 'upper': 3, 'lower': 2, 'title': 0}}}
        ]
        assert mod.simulate_bank_classification_from_precomputed(matches, 1, 1, 3) == 1

    def test_fintech_path_untouched(self, mod):
        """金融科技模拟 cond_b 本就与生产一致 (grand_total 正文口径), 不应被改动。"""
        matches = [
            {'distinct_count': 3, 'upper_total': 0, 'lower_total': 0,
             'grand_total': 2, 'any_in_title': True}
        ]
        assert mod.simulate_fintech_classification_vectorized(matches, 1, 1, 3) == 1


# ============================================================================
# g-val-robust-01: dedup_threshold 预去重输入 + 单侧截尾披露
# ============================================================================

class TestDedupThresholdInput:
    """fix(omni-g-val-robust-01, 2026-06-11)。"""

    @pytest.fixture(scope="class")
    def mod(self):
        from news_process.validation import dedup_threshold
        return dedup_threshold

    @staticmethod
    def _write_cache(cache_dir, name, n=3, extra_col=True):
        os.makedirs(cache_dir, exist_ok=True)
        df = pd.DataFrame({
            'docid': [f'{name}-{i}' for i in range(n)],
            '标题': [f'标题{i}' for i in range(n)],
            '内容': [f'内容内容内容{i}' for i in range(n)],
            '日期': ['2017-01-01'] * n,
            '媒体(中文)': ['新华社'] * n,
        })
        if extra_col:
            df['多余列'] = 1  # 验证只读必需 5 列
        df.to_parquet(os.path.join(cache_dir, f'{name}.parquet'))

    def test_load_pre_dedup_corpus_happy_path(self, mod, tmp_path):
        """缓存存在且列齐 → 拼接全部缓存文件, 仅读必需 5 列。"""
        out_dir = str(tmp_path)
        cache_dir = os.path.join(out_dir, '_cache')
        self._write_cache(cache_dir, 'a', n=3)
        self._write_cache(cache_dir, 'b', n=2)

        rec = _RecLogger()
        df = mod._load_pre_dedup_corpus(out_dir, rec)
        assert df is not None
        assert len(df) == 5
        assert list(df.columns) == mod.PRE_DEDUP_REQUIRED_COLS
        assert '多余列' not in df.columns

    def test_load_pre_dedup_corpus_missing_dir(self, mod, tmp_path):
        """缓存目录缺失 → None (调用方回退并披露)。"""
        rec = _RecLogger()
        assert mod._load_pre_dedup_corpus(str(tmp_path), rec) is None

    def test_load_pre_dedup_corpus_missing_column(self, mod, tmp_path):
        """任一缓存文件缺必需列 → 整体放弃缓存口径 (None)。"""
        out_dir = str(tmp_path)
        cache_dir = os.path.join(out_dir, '_cache')
        os.makedirs(cache_dir)
        pd.DataFrame({'docid': ['x'], '标题': ['t'], '内容': ['c']}).to_parquet(
            os.path.join(cache_dir, 'bad.parquet'))
        rec = _RecLogger()
        assert mod._load_pre_dedup_corpus(out_dir, rec) is None
        assert '缺少必需列' in rec.joined()

    def test_annotate_censoring_fallback(self, mod):
        """回退口径: Threshold >= 生产阈值的行标记机械截尾。"""
        res_df = pd.DataFrame({'Threshold': [0.75, 0.80, 0.85, 0.90],
                               'Retained': [90, 100, 100, 100]})
        out = mod._annotate_censoring(res_df, 'post_dedup_fallback', 0.80)
        assert (out['Input_Mode'] == 'post_dedup_fallback').all()
        assert out['Mechanically_Censored'].tolist() == [False, True, True, True]

    def test_annotate_censoring_pre_dedup(self, mod):
        """预去重口径: 双向均有信息, 全部 False。"""
        res_df = pd.DataFrame({'Threshold': [0.75, 0.80, 0.85, 0.90],
                               'Retained': [80, 90, 95, 99]})
        out = mod._annotate_censoring(res_df, 'pre_dedup_cache', 0.80)
        assert (out['Input_Mode'] == 'pre_dedup_cache').all()
        assert not out['Mechanically_Censored'].any()


# ============================================================================
# g-val-robust-02 + omni-extra-dictcov-5b: dict_coverage 口径措辞 / 5b 死分支
# ============================================================================

class TestDictCoverageScopeWording:
    """fix(omni-g-val-robust-02, 2026-06-11)。"""

    @pytest.fixture(scope="class")
    def mod(self):
        from news_process.validation import dict_coverage
        return dict_coverage

    def test_analysis_3_scoped_wording(self, mod, tmp_path, monkeypatch):
        """零命中措辞限定为'通过分类的文章', 不再声称'全部语料中从未出现'。"""
        dict_file = tmp_path / 'fintech_dict.json'
        dict_file.write_text(
            json.dumps(['区块链', '人工智能', '云计算']), encoding='utf-8')
        monkeypatch.setitem(mod.CONFIG['paths'], 'fintech_dict_file', str(dict_file))

        rec = _RecLogger()
        monkeypatch.setattr(mod, 'logger', rec)

        details = json.dumps([{'keyword': '区块链', 'total': 2},
                              {'keyword': '人工智能', 'total': 1}])
        df = pd.DataFrame({'fintech_keyword_details': [details, details]})

        freq_df, zero_hit_df = mod.analysis_3_keyword_concentration(df)
        text = rec.joined()

        # 行为: 云计算在通过样本中零命中
        assert set(zero_hit_df['keyword']) == {'云计算'}
        assert len(freq_df) == 2
        # 措辞: 限定通过样本口径
        assert '通过分类的金融科技文章' in text
        assert '全部语料中从未出现' not in text
        assert "'死词'" not in text or '非全语料' in text

    def test_log_summary_retracts_full_corpus_cleanup_advice(self, mod, monkeypatch):
        """综合结论低覆盖率时: 限定口径 + 撤回直接清理建议。"""
        rec = _RecLogger()
        monkeypatch.setattr(mod, 'logger', rec)
        mod.log_summary(marginal_rate=0.05, effect_size=0.0,
                        enk=100.0, coverage_rate=0.30)
        text = rec.joined()
        assert '通过分类的文章中命中' in text
        assert '选择后样本口径' in text
        assert '核查词典' in text
        # 旧的全语料直接清理建议必须消失
        assert "移除零命中的'死词'" not in text
        assert '从未在语料中出现过' not in text


class TestDictCoverage5bDeadBranchRemoved:
    """fix(omni-extra-dictcov-5b, 2026-06-11)。"""

    @pytest.fixture(scope="class")
    def mod(self):
        from news_process.validation import dict_coverage
        return dict_coverage

    def test_5b_discloses_never_implemented(self, mod, tmp_path, monkeypatch):
        """非空灰色地带 → 输出披露, 返回 None, 不写 FNR CSV。"""
        rec = _RecLogger()
        monkeypatch.setattr(mod, 'logger', rec)
        monkeypatch.setattr(mod, 'EVAL_DIR', str(tmp_path))

        grey = pd.DataFrame({'标题': ['t1', 't2'], '内容': ['c1', 'c2'],
                             'fintech_distinct_keywords': [1, 2]})
        result = mod.analysis_5b_llm_cross_validation(grey)
        text = rec.joined()

        assert result is None
        assert '从未实装' in text
        # 不再误导为可修复的环境问题
        assert '请确认 utils/llm_clients.py 存在' not in text
        # 死分支移除后不应产出任何 FNR 估计文件
        assert not os.path.exists(
            os.path.join(str(tmp_path), '37_false_negative_estimate.csv'))

    def test_5b_empty_grey_zone_skips(self, mod, monkeypatch):
        """空灰色地带 → 平静跳过 (原行为保留)。"""
        rec = _RecLogger()
        monkeypatch.setattr(mod, 'logger', rec)
        assert mod.analysis_5b_llm_cross_validation(pd.DataFrame()) is None
        assert '灰色地带为空' in rec.joined()


# ============================================================================
# g-val-robust-03: radius_sensitivity 热力图零方差守卫
# ============================================================================

class TestRadiusHeatmapZeroVarGuard:
    """fix(omni-g-val-robust-03, 2026-06-11)。"""

    @pytest.fixture(scope="class")
    def mod(self):
        from news_process.validation import radius_sensitivity
        return radius_sensitivity

    @staticmethod
    def _make_data(radii, score_fn):
        """构造 per_radius_data: {radius: [{'d1_score': v}, ...]}。"""
        return {r: [{'d1_score': score_fn(r, i)} for i in range(10)]
                for r in radii}

    def test_constant_scores_yield_nan_not_warning(self, mod):
        """常量得分 (词典零命中/空窗口退化) → 非对角 NaN, 无 ConstantInputWarning。"""
        radii = [0, 1]
        data = self._make_data(radii, lambda r, i: 0.0)  # 全常量
        with warnings.catch_warnings():
            warnings.simplefilter('error')  # 任何 warning 直接失败
            corr = mod._compute_pairwise_radius_corr(data, 'd1', radii)
        assert corr[0, 0] == 1.0 and corr[1, 1] == 1.0  # 对角惯例 1.0
        assert math.isnan(corr[0, 1]) and math.isnan(corr[1, 0])

    def test_varying_scores_yield_real_correlation(self, mod):
        """有方差得分 → 真实 Pearson r (完全共线 → ≈1.0)。"""
        radii = [0, 1]
        data = self._make_data(radii, lambda r, i: float(i) * (1.0 + r))
        corr = mod._compute_pairwise_radius_corr(data, 'd1', radii)
        assert corr[0, 1] == pytest.approx(1.0, abs=1e-9)
        assert corr[1, 0] == pytest.approx(1.0, abs=1e-9)

    def test_tiny_sample_yields_nan(self, mod):
        """n <= 2 样本不足 → NaN (与 cross_radius 守卫同语义)。"""
        radii = [0, 1]
        data = {r: [{'d1_score': float(i + r)} for i in range(2)] for r in radii}
        corr = mod._compute_pairwise_radius_corr(data, 'd1', radii)
        assert math.isnan(corr[0, 1])

    def test_one_constant_one_varying_yields_nan(self, mod):
        """任一侧零方差即 NaN (相关无定义)。"""
        radii = [0, 1]
        data = {0: [{'d1_score': 0.5} for _ in range(10)],
                1: [{'d1_score': float(i)} for i in range(10)]}
        corr = mod._compute_pairwise_radius_corr(data, 'd1', radii)
        assert math.isnan(corr[0, 1]) and math.isnan(corr[1, 0])


# ============================================================================
# g-val-robust-04: decay_sensitivity 锚定声称限定为衰减权重族内
# ============================================================================

class TestDecayScopedClaims:
    """fix(omni-g-val-robust-04, 2026-06-11)。"""

    @pytest.fixture(scope="class")
    def mod(self):
        from news_process.validation import decay_sensitivity
        return decay_sensitivity

    def test_report_uses_within_family_language(self, mod, monkeypatch):
        """高相关时结论/论文用语限定族内, 不再过度声称主结果不敏感。"""
        rec = _RecLogger()
        monkeypatch.setattr(mod, 'logger', rec)

        n = 30
        base = np.linspace(-1.0, 1.0, n)
        score_df = pd.DataFrame({
            'jiang_2021_uniform': base,
            'jiang_2021_inverse': base * 0.9,
            'jiang_2021_exponential': base * 0.8,
        })
        mod.log_correlation_report(score_df, ['jiang_2021'])
        text = rec.joined()

        # 新: 限定衰减权重族内 (radius=2)
        assert '衰减权重族内' in text
        assert 'within this family' in text
        assert 'not numerically anchored' in text
        # 旧过度声称必须消失
        assert '主结果对权重选择' not in text
        assert 'confirming that our main results' not in text
        assert 'insensitive to the weighting scheme' not in text

    def test_docstring_discloses_three_divergences(self, mod):
        """模块 docstring 披露与生产测度的三重口径差异。"""
        doc = mod.__doc__
        assert 'mean-of-ratios' in doc
        assert 'ratio-of-sums' in doc
        assert 'prepend_title' in doc or '标题' in doc
        assert '不是' in doc and '锚点' in doc


# ============================================================================
# g-val-robust-05: media_diversity Pielou S=1 返回 NaN
# ============================================================================

class TestPielouSingleCategoryNaN:
    """fix(omni-g-val-robust-05, 2026-06-11)。"""

    @pytest.fixture(scope="class")
    def mod(self):
        from news_process.validation import media_diversity
        return media_diversity

    def test_single_category_returns_nan(self, mod):
        """S=1 → J' = 0/0 未定义 → NaN (不再硬编码 1.0)。"""
        assert math.isnan(mod.compute_pielou_evenness(0.0, 1))

    def test_zero_categories_returns_nan(self, mod):
        assert math.isnan(mod.compute_pielou_evenness(0.0, 0))

    def test_uniform_distribution_is_one(self, mod):
        """S=4 完全均匀 (H=2, H_max=2) → J' = 1.0 (正常路径不受影响)。"""
        assert mod.compute_pielou_evenness(2.0, 4) == pytest.approx(1.0)

    def test_two_categories_normal(self, mod):
        assert mod.compute_pielou_evenness(1.0, 2) == pytest.approx(1.0)
        assert mod.compute_pielou_evenness(0.5, 2) == pytest.approx(0.5)

    def test_summary_displays_na_and_skips_evenness_gate(self, mod, monkeypatch):
        """综合结论: J'=NaN 显示 n/a, 不触发'分布不均'误报; HHI 门照常捕获垄断。"""
        rec = _RecLogger()
        monkeypatch.setattr(mod, 'logger', rec)

        final_metrics = {
            '唯一媒体数': 1, 'HHI': 1.0, '等效媒体数ENM': 1.0,
            'Pielou均匀度': float('nan'), 'Gini系数': 0.0,
            '已评级报道占比(%)': 50.0,
        }
        final_region = {
            '唯一地域数': 1, '地域HHI': 0.05,
            '地域Pielou均匀度': float('nan'), '省份覆盖率': 0.9,
        }
        mod.log_comprehensive_summary(final_metrics, final_region)
        text = rec.joined()

        assert 'n/a' in text and "J' 不适用" in text
        # NaN 不得触发均匀度误报
        assert '报道数在各媒体间分布不均' not in text
        # 单一媒体垄断仍由 HHI 门捕获 (自相矛盾消除后的承重判定)
        assert '来源过度集中于少数媒体' in text


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
