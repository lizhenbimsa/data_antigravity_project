"""measurement-validation-topjournal-audit (2026-06-13) 落地修复的定向回归测试。

覆盖四处 golden-safe (validation-output-only, 不触面板/golden) 的顶刊级修复:
  F1  McNemar: 小分歧样本 (b+c<25) 改用精确二项检验, 大样本沿用连续性校正卡方
       → compute_mcnemar_test
  F2  Krippendorff α: D_e 仅基于可配对单元 (m_u>=2), 与 D_o 同口径
       → compute_krippendorffs_alpha (定义性不变性: 单编码者单元对 α 零贡献)
  F3  Cohen κ 95% CI 截断至 [-1,1] (在 main() 标准化报告中, 此处不直接测)
  F4  compute_classification_metrics 新增 Wilson 'accuracy_ci'

这些函数此前无直接单测; 本文件补齐, 并断言修复在完整数据下与旧行为一致
(仅在小样本 / 缺标单元等边界给出更正确的统计量)。
"""
import numpy as np

from news_process.validation import llms_evaluation as _mod


# ---------------------------------------------------------------------------
# F1: McNemar 精确二项 vs 连续性校正卡方
# ---------------------------------------------------------------------------
class TestMcNemarExactSmallN:
    def test_small_discordant_uses_exact_binomial(self):
        # b=2, c=0 → n_discordant=2 < 25 → 精确二项; 两侧 p = 2*C(2,0)*0.5^2 = 0.5
        y_true = np.array([1, 1, 1, 1])
        y_pred_a = np.array([1, 1, 1, 1])  # 全对
        y_pred_b = np.array([0, 0, 1, 1])  # 前两条错 → b=2 (A对B错), c=0
        r = _mod.compute_mcnemar_test(y_true, y_pred_a, y_pred_b)
        assert r['test_type'] == 'exact_binomial'
        assert r['b_count'] == 2 and r['c_count'] == 0
        assert abs(r['p_value'] - 0.5) < 1e-6
        assert r['significant'] is False

    def test_large_discordant_uses_chi2(self):
        # 构造 b+c >= 25 → 连续性校正卡方路径
        n = 100
        y_true = np.ones(n, dtype=int)
        a = np.ones(n, dtype=int)
        b = np.ones(n, dtype=int)
        # 让 30 条 A 对 B 错, 5 条 A 错 B 对 (b=30, c=5, n_discordant=35)
        b[:30] = 0          # B 在前 30 条错
        a[30:35] = 0        # A 在 30-34 错 (这 5 条 B 仍为 1=对)
        r = _mod.compute_mcnemar_test(y_true, a, b)
        assert r['test_type'] == 'continuity_corrected_chi2'
        assert r['b_count'] == 30 and r['c_count'] == 5
        # 连续性校正卡方 = (|30-5|-1)^2 / 35 (返回值四舍五入到 4 位小数)
        assert abs(r['chi2_statistic'] - round(((abs(30 - 5) - 1) ** 2) / 35, 4)) < 1e-6
        assert r['significant'] is True  # 强不对称 → 显著

    def test_zero_discordant(self):
        y_true = np.array([1, 0, 1, 0])
        same = np.array([1, 0, 1, 0])
        r = _mod.compute_mcnemar_test(y_true, same, same)
        assert r['b_count'] == 0 and r['c_count'] == 0
        assert r['p_value'] == 1.0 and r['significant'] is False
        assert r['test_type'] == 'none(b+c=0)'


# ---------------------------------------------------------------------------
# F2: Krippendorff α — 单编码者单元零贡献 (D_e 与 D_o 同口径)
# ---------------------------------------------------------------------------
class TestKrippendorffSingletonInvariance:
    def test_singleton_unit_does_not_change_alpha(self):
        # 2 编码者, 3 个完整单元
        complete = np.array([
            [0, 1, 0],
            [0, 1, 1],
        ])
        alpha_complete = _mod.compute_krippendorffs_alpha(complete)

        # 追加 1 个仅 coder0 评过的单元 (coder1 缺标 = -1)
        with_singleton = np.array([
            [0, 1, 0, 1],
            [0, 1, 1, -1],
        ])
        alpha_with_singleton = _mod.compute_krippendorffs_alpha(with_singleton)

        # 定义性质: 单编码者单元对 α 无贡献 → 两者必须严格相等
        assert alpha_complete == alpha_with_singleton

    def test_alpha_in_valid_range_and_perfect_agreement(self):
        perfect = np.array([
            [0, 1, 2, 0, 1],
            [0, 1, 2, 0, 1],
        ])
        assert _mod.compute_krippendorffs_alpha(perfect) == 1.0
        mixed = np.array([
            [0, 1, 0, 1],
            [0, 0, 1, 1],
        ])
        a = _mod.compute_krippendorffs_alpha(mixed)
        assert -1.0 <= a <= 1.0


# ---------------------------------------------------------------------------
# F4: accuracy 的 Wilson 95% CI (additive 键)
# ---------------------------------------------------------------------------
class TestAccuracyWilsonCI:
    def test_accuracy_ci_present_and_brackets_point(self):
        y_true = np.array(['正面', '中性', '负面', '正面', '中性', '负面'])
        y_pred = np.array(['正面', '中性', '负面', '正面', '负面', '负面'])
        m = _mod.compute_classification_metrics(
            y_true, y_pred, labels=['正面', '中性', '负面'])
        assert 'accuracy_ci' in m
        lo, hi = m['accuracy_ci']
        assert 0.0 <= lo <= m['accuracy'] <= hi <= 1.0
        # 既有键未被破坏 (向后兼容)
        for k in ('accuracy', 'macro', 'weighted', 'per_class', 'confusion_matrix'):
            assert k in m

    def test_ci_narrows_with_n(self):
        # 同准确率下, n 越大 CI 越窄
        small = _mod.compute_classification_metrics(
            np.array([1, 1, 0, 0]), np.array([1, 1, 0, 0]), labels=[0, 1])
        big_true = np.array([1, 0] * 200)
        big = _mod.compute_classification_metrics(
            big_true, big_true, labels=[0, 1])
        small_w = small['accuracy_ci'][1] - small['accuracy_ci'][0]
        big_w = big['accuracy_ci'][1] - big['accuracy_ci'][0]
        assert big_w < small_w


# ---------------------------------------------------------------------------
# P1-2 (创新维度 3 编码者 Krippendorff α) + P1-3 (总体加权 accuracy)
# 经 _evaluate_innovation_panels 端到端验证: 合成带分歧 + 权重倾斜的工作簿
# ---------------------------------------------------------------------------
import pandas as pd  # noqa: E402

from news_process.validation.manual_validation_schema import (  # noqa: E402
    R_COLUMNS_BY_RATER,
)


class TestInnovationPercoderAlphaAndWeightedAccuracy:
    def _run(self, tmp_path, monkeypatch, weights=(1.0, 1.0, 1.0, 10.0)):
        import logging
        output_dir = tmp_path / "processed"
        output_dir.mkdir(parents=True, exist_ok=True)
        docids = ['d0', 'd1', 'd2', 'd3']
        # substantiveness: d0/d1 三人一致 substantive; d2 多数 symbolic(2:1, 含分歧);
        # d3 三人一致 symbolic → gold=[实质性,实质性,象征性,象征性]
        subst = {
            R_COLUMNS_BY_RATER['substantiveness'][0]: ['substantive', 'substantive', 'symbolic', 'symbolic'],
            R_COLUMNS_BY_RATER['substantiveness'][1]: ['substantive', 'substantive', 'symbolic', 'symbolic'],
            R_COLUMNS_BY_RATER['substantiveness'][2]: ['substantive', 'substantive', 'substantive', 'symbolic'],
        }
        locus = {c: ['technology'] * 4 for c in R_COLUMNS_BY_RATER['locus']}
        df_mv = pd.DataFrame({
            'docid': docids,
            # 权重倾斜: d3 权重远大于其余 → 加权 accuracy ≠ 未加权
            'population_weight': list(weights),
            **subst, **locus,
        })
        df_mv.to_excel(output_dir / 'manual_validation_samples.xlsx', index=False)
        # 预测: substantiveness_full 在 d3 故意错(预测实质性, gold 象征性) → 未加权 3/4
        df_pred = pd.DataFrame({
            'docid': docids,
            'innovation_substantiveness_full': ['实质性', '实质性', '象征性', '实质性'],
            'innovation_substantiveness_ctx':  ['实质性', '实质性', '象征性', '象征性'],
            'innovation_locus_full': ['底层技术'] * 4,
            'innovation_locus_ctx':  ['底层技术'] * 4,
        })
        df_pred.to_parquet(output_dir / '21_tone_llms.parquet')
        monkeypatch.setattr(
            'news_process.core.config.load_config',
            lambda: {'paths': {'output_dir': str(output_dir)}},
        )
        results = {'classifier_metrics': {'innovation_substantiveness': {},
                                          'innovation_locus': {}},
                   'innovation_pending_reason': None}
        _mod._evaluate_innovation_panels(results, str(output_dir), logging.getLogger('t'))
        return results

    def test_innovation_3coder_alpha_reported(self, tmp_path, monkeypatch):
        results = self._run(tmp_path, monkeypatch)
        icr = results.get('innovation_inter_coder_reliability')
        assert icr is not None
        # substantiveness 有 1 处编码者分歧 → α 应可算且 < 1
        a = icr['substantiveness']
        assert a['status'] == 'ok' and a['n_pairable_items'] == 4
        assert a['krippendorffs_alpha'] is not None
        assert -1.0 <= a['krippendorffs_alpha'] < 1.0
        # locus 三人全一致 → α = 1.0
        assert icr['locus']['krippendorffs_alpha'] == 1.0
        # 不得污染 inter_coder_reliability 的 2-键不变量(本函数不写该键)
        assert 'inter_coder_reliability' not in results

    def test_population_weighted_accuracy_differs_from_unweighted(self, tmp_path, monkeypatch):
        results = self._run(tmp_path, monkeypatch)
        m = results['classifier_metrics']['innovation_substantiveness']['LLM (_full)']
        # 未加权: d3 错 → 3/4 = 0.75
        assert abs(m['accuracy'] - 0.75) < 1e-9
        # 加权: d3(错)权重=10 → (1+1+1)/(1+1+1+10) = 3/13 ≈ 0.2308
        assert m['accuracy_weighted_corpus'] is not None
        assert abs(m['accuracy_weighted_corpus'] - round(3 / 13, 4)) < 1e-6
        assert 'accuracy_note' in m

    def test_weighted_accuracy_guarded_on_nan_weight(self, tmp_path, monkeypatch):
        # re-audit 防御: partial-NaN 权重 → accuracy_weighted_corpus=None, 不静默分叉
        results = self._run(tmp_path / 'nan', monkeypatch,
                            weights=[float('nan'), 1.0, 1.0, 10.0])
        m = results['classifier_metrics']['innovation_substantiveness']['LLM (_full)']
        assert abs(m['accuracy'] - 0.75) < 1e-9   # 未加权仍正常
        assert m['accuracy_weighted_corpus'] is None
        assert '不可计' in m['accuracy_note']

    def test_weighted_accuracy_guarded_on_negative_weight(self, tmp_path, monkeypatch):
        # re-audit 防御: 负权重会使 accuracy 越界 [0,1] → 置 None
        results = self._run(tmp_path / 'neg', monkeypatch,
                            weights=[-2.0, 1.0, 1.0, 5.0])
        m = results['classifier_metrics']['innovation_substantiveness']['LLM (_full)']
        assert m['accuracy_weighted_corpus'] is None
        assert '不可计' in m['accuracy_note']
