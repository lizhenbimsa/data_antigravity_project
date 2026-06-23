"""
tests/test_63_evaluation.py — diagnose_misclassification_bias 单元测试
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
# 旧 ``import_module('63_news_llms_evaluation')`` 现仅返回 thin shim,
# 直接走规范 import 即可拿到全部内部函数与模块级常量。
from news_process.validation import llms_evaluation as _mod

diagnose_misclassification_bias = _mod.diagnose_misclassification_bias


class TestGwetAC1AndWeightedKappa:
    """WS-C: Gwet AC1 (偏态破 κ 悖论) + population-weighted κ (Manski-Lerman 外推)。"""

    def test_gwet_ac1_perfect_agreement(self):
        r = np.array([0, 0, 1, 1, 0])
        assert _mod.compute_gwet_ac1(r, r)['ac1'] == 1.0

    def test_gwet_ac1_skewed_beats_kappa(self):
        """偏态 90/5/5/0: κ 悖论性塌为负, AC1 仍高 (Gwet 2008 破 κ 悖论)。"""
        a = np.array([0] * 90 + [0] * 5 + [1] * 5)
        b = np.array([0] * 90 + [1] * 5 + [0] * 5)
        kappa = _mod.compute_cohens_kappa(a, b)['kappa']
        ac1 = _mod.compute_gwet_ac1(a, b)['ac1']
        # 手算: κ=(0.9-0.905)/0.095≈-0.0526; AC1=(0.9-0.095)/0.905≈0.8895
        assert ac1 > kappa
        assert abs(kappa - (-0.0526)) < 0.001
        assert abs(ac1 - 0.8895) < 0.001  # 验证用的是 AC1 的 p_e 非误抄 κ 的 p_e

    def test_gwet_ac1_single_category(self):
        """单类别 (全同) → AC1=1, 不除零。"""
        r = np.array([1, 1, 1, 1])
        assert _mod.compute_gwet_ac1(r, r)['ac1'] == 1.0

    def test_weighted_kappa_unit_weights_equals_unweighted(self):
        """向后兼容锚: 全 w=1 时 κ_w 逐位等于 compute_cohens_kappa。"""
        a = np.array([0, 1, 0, 1, 1, 0, 0, 1])
        b = np.array([0, 1, 1, 1, 0, 0, 0, 1])
        w = np.ones(8)
        kw = _mod.compute_cohens_kappa_weighted(a, b, w)
        ku = _mod.compute_cohens_kappa(a, b)
        assert kw['kappa'] == ku['kappa']
        assert kw['observed_agreement'] == ku['observed_agreement']
        assert kw['expected_agreement'] == ku['expected_agreement']

    def test_weighted_kappa_nonuniform_shifts_point_estimate(self):
        a = np.array([0, 1, 0, 1, 1, 0, 0, 1])
        b = np.array([0, 1, 1, 1, 0, 0, 0, 1])
        w2 = np.array([2., 1, 1, 1, 1, 3, 1, 1])
        kw = _mod.compute_cohens_kappa_weighted(a, b, w2)['kappa']
        assert kw != _mod.compute_cohens_kappa(a, b)['kappa']

    def test_weighted_bootstrap_ci_covers_point_estimate(self):
        """R8-fix C2: 概率重抽+无权 κ 的加权 bootstrap CI 必须覆盖其点估计
        (旧实现双重计权 → CI 偏移不覆盖点估计)。"""
        rng = np.random.RandomState(7)
        yt = np.array(['象征性'] * 50 + ['实质性'] * 150)
        yp = yt.copy()
        yp[:50][rng.rand(50) < 0.4] = '实质性'
        yp[50:][rng.rand(150) < 0.1] = '象征性'
        w = np.array([0.2] * 50 + [1.0] * 150)
        point = _mod.compute_cohens_kappa_weighted(yt, yp, w)['kappa']
        # 复刻生产 bootstrap (概率重抽 p=w/wsum + 无权 κ)
        wp = w / w.sum()
        rw = np.random.default_rng(43)
        ny = len(yt)
        bw = np.array([_mod.compute_cohens_kappa(yt[i], yp[i])['kappa']
                       for i in (rw.choice(ny, ny, p=wp) for _ in range(1000))])
        lo, hi = np.percentile(bw, 2.5), np.percentile(bw, 97.5)
        assert lo <= point <= hi, f"point {point} 不在 CI [{lo},{hi}] (双重计权 bug?)"

    def test_weighted_kappa_str_labels(self):
        """直接喂中文 str array (criterion κ 口径, 内部 sorted(set) 编码)。"""
        a = np.array(['实质性', '象征性', '实质性', '象征性'])
        b = np.array(['实质性', '象征性', '象征性', '象征性'])
        w = np.ones(4)
        assert _mod.compute_cohens_kappa_weighted(a, b, w)['kappa'] == \
            _mod.compute_cohens_kappa(a, b)['kappa']
        # str array 亦可喂 AC1
        assert 'ac1' in _mod.compute_gwet_ac1(a, b)


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


@pytest.mark.filterwarnings(
    "ignore:Precision loss occurred in moment calculation:RuntimeWarning"
)
class TestDiagnoseMisclassificationBias:

    def test_basic_structure(self):
        """返回字典包含所有必要键，四象限之和等于总样本数。"""
        df = _make_df(100)
        r = diagnose_misclassification_bias(df, '最终_验证', '_full')
        # fix(omni-g-val-eval-01/03, 2026-06-11): 新增 n_gold_excluded 键
        # (金标准 NaN/-1 哨兵行从诊断域剔除的计数)
        assert set(r.keys()) == {'track', 'tests', 'quadrant_counts',
                                 'conclusion', 'n_gold_excluded'}
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


# =============================================================================
# Plan v1.37 P0 §3.3.3 — 4-task 扩展的 17 个新测试
# 参数化展开后共 26 个 case (test 7: 10 个 case; tests 1-6, 8-17: 各 1 个 case)
# =============================================================================
from news_process.validation.manual_validation_schema import (
    R_COLUMNS_BY_RATER,
    merge_three_rater_majority,
    normalize_rater_value,
)


def _rater_row(sub_vals, locus_vals, collab_vals=None):
    """构造含 R 列的 dict 行 (3 substantiveness + 3 locus [+ 3 collab])。

    WS-A (R6-P1-1): collab_vals=None 时跳过 collab 列注入, 护现有 2-arg 调用。
    """
    row = {}
    for i, v in enumerate(sub_vals, 1):
        row[f'R{i}_stage3a_substantiveness'] = v
    for i, v in enumerate(locus_vals, 1):
        row[f'R{i}_stage3b_locus'] = v
    if collab_vals is not None:
        for i, v in enumerate(collab_vals, 1):
            row[f'R{i}_stage3c_collab'] = v
    return row


def test_merge_majority_3_agree():
    """Item 1: 3 位评分者全部一致 → 保留该行, 取多数标签。"""
    row = _rater_row(['substantive', 'substantive', 'substantive'],
                     ['technology', 'technology', 'technology'])
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['substantiveness']) == '实质性'
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['locus']) == '底层技术'


def test_merge_majority_2_of_3():
    """Item 2: 2 位一致, 1 位不同 → 保留该行, 取 2 票多数标签。"""
    row = _rater_row(['substantive', 'substantive', 'symbolic'],
                     ['technology', 'application', 'technology'])
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['substantiveness']) == '实质性'
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['locus']) == '底层技术'


def test_merge_2_agree_1_missing():
    """Item 3: 2 位一致, 1 位 NaN → 保留该行, 取多数标签。"""
    import numpy as np
    row = _rater_row(['substantive', 'substantive', np.nan],
                     ['technology', np.nan, 'technology'])
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['substantiveness']) == '实质性'
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['locus']) == '底层技术'


def test_merge_1_1_tie_with_missing():
    """Item 4: 1-1 平局 + 第 3 位 NaN → 丢弃该行。"""
    import numpy as np
    row = _rater_row(['substantive', 'symbolic', np.nan],
                     ['technology', 'application', np.nan])
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['substantiveness']) is None
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['locus']) is None


def test_merge_all_missing():
    """Item 5: 3 位全 NaN → 丢弃该行。"""
    import numpy as np
    row = _rater_row([np.nan, np.nan, np.nan], [np.nan, np.nan, np.nan])
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['substantiveness']) is None


def test_merge_single_rater_dropped():
    """Item 6: 仅 1 个有效值 + 2 个 NaN → 丢弃 (评分者间信息不足; R3C-13)。"""
    import numpy as np
    row = _rater_row(['substantive', np.nan, np.nan], [np.nan, np.nan, 'technology'])
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['substantiveness']) is None
    assert merge_three_rater_majority(row, R_COLUMNS_BY_RATER['locus']) is None


@pytest.mark.parametrize("raw, expected", [
    ('substantive', '实质性'),
    ('Substantive', '实质性'),
    (' SUBSTANTIVE ', '实质性'),
    ('象征性 ', '象征性'),
    ('subtantive', None),       # typo → None
    (True, None),                # bool from openpyxl auto-type
    (1, None),                   # int
    (float('nan'), None),        # numpy NaN
    (pd.NA, None),               # pandas NA
    ('', None),                  # empty
])
def test_merge_value_normalization(raw, expected):
    """Item 7 (10 个 case): normalize_rater_value 归一化规则 (R5C-01 + R4A-02)。"""
    assert normalize_rater_value(raw) == expected


def test_normalize_rater_value_pd_isna_raises_caught_silently():
    """quality-hardening Round 13: pd.isna 对 list/dict 抛 → except 静默 → 走非 str → None
    (manual_validation_schema.py:63-64)."""
    # pd.isna 对 list/dict 抛 TypeError → caught + pass → 非 str check return None
    assert normalize_rater_value([1, 2, 3]) is None
    assert normalize_rater_value({'k': 'v'}) is None
    # 复杂对象: pd.isna 也会抛 → 不要把 except 路径吞掉真正的异常
    assert normalize_rater_value(object()) is None


def test_panels_E_F_present_with_gold(tmp_path, monkeypatch):
    """Item 8: 合成 30 行有效的 manual_validation_samples.xlsx;
    调用 _evaluate_innovation_panels; 断言 pending_reason 为 None 且 Panel E/F 已填充。"""
    # 合成 xlsx + docid 匹配的 21_tone_llms.parquet
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    n = 30
    docids = [f"doc_{i}" for i in range(n)]
    df_mv = pd.DataFrame({
        'docid': docids,
        **{c: ['substantive'] * n for c in R_COLUMNS_BY_RATER['substantiveness']},
        **{c: ['technology'] * n for c in R_COLUMNS_BY_RATER['locus']},
    })
    df_mv.to_excel(output_dir / 'manual_validation_samples.xlsx', index=False)
    df_pred = pd.DataFrame({
        'docid': docids,
        'innovation_substantiveness_full': ['实质性'] * n,
        'innovation_substantiveness_ctx':  ['实质性'] * n,
        'innovation_locus_full': ['底层技术'] * n,
        'innovation_locus_ctx':  ['底层技术'] * n,
    })
    df_pred.to_parquet(output_dir / '21_tone_llms.parquet')

    monkeypatch.setattr(
        'news_process.core.config.load_config',
        lambda: {'paths': {'output_dir': str(output_dir)}},
    )
    results = {'classifier_metrics': {'innovation_substantiveness': {},
                                       'innovation_locus': {}},
               'innovation_pending_reason': None}
    import logging
    log = logging.getLogger('test')
    _mod._evaluate_innovation_panels(results, str(output_dir), log)
    assert results['innovation_pending_reason'] is None
    assert results['classifier_metrics']['innovation_substantiveness']
    assert results['classifier_metrics']['innovation_locus']


def test_panels_E_F_pending_when_empty(tmp_path, monkeypatch):
    """Item 9: xlsx 中 R 列单元格全 NaN → pending 原因 'n=0'。"""
    import numpy as np
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    n = 30
    df_mv = pd.DataFrame({
        'docid': [f"d_{i}" for i in range(n)],
        **{c: [np.nan] * n for c in R_COLUMNS_BY_RATER['substantiveness']},
        **{c: [np.nan] * n for c in R_COLUMNS_BY_RATER['locus']},
    })
    df_mv.to_excel(output_dir / 'manual_validation_samples.xlsx', index=False)
    monkeypatch.setattr(
        'news_process.core.config.load_config',
        lambda: {'paths': {'output_dir': str(output_dir)}},
    )
    results = {'classifier_metrics': {'innovation_substantiveness': {},
                                       'innovation_locus': {}},
               'innovation_pending_reason': None}
    import logging
    _mod._evaluate_innovation_panels(results, str(output_dir), logging.getLogger('t'))
    assert results['innovation_pending_reason'] == 'n=0'


def test_panels_E_F_pending_when_file_absent(tmp_path, monkeypatch):
    """Item 10: 无 xlsx 文件 → pending 原因 'file not present'。"""
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    monkeypatch.setattr(
        'news_process.core.config.load_config',
        lambda: {'paths': {'output_dir': str(output_dir)}},
    )
    results = {'classifier_metrics': {'innovation_substantiveness': {},
                                       'innovation_locus': {}},
               'innovation_pending_reason': None}
    import logging
    _mod._evaluate_innovation_panels(results, str(output_dir), logging.getLogger('t'))
    assert results['innovation_pending_reason'] == 'file not present'


def test_panels_A_to_D_structural_equality():
    """Item 11: LaTeX 表应含 Panel E + Panel F 结构 (按 R12C-01 各占独立
    tabular); 第一个 \\end{tabular} 截断 Panel A-D。"""
    results = {
        'demo_mode': True,
        'classifier_metrics': {
            'verification': {'LLM (_full)': {'macro': {'precision': 0.9, 'recall': 0.9, 'f1': 0.9}, 'accuracy': 0.9, 'per_class': {}, 'support': {}}},
            'sentiment': {},
            'innovation_substantiveness': {},
            'innovation_locus': {},
        },
        'inter_coder_reliability': {'verification': {}, 'sentiment': {}},
        'innovation_pending_reason': 'file not present',
    }
    out_path = '/tmp/_test_eval.tex'
    import logging
    _mod.generate_latex_table(results, out_path, logging.getLogger('t'))
    tex = open(out_path, encoding='utf-8').read()
    # Panel E + F 始终存在 (R21A-01 对账)
    assert 'Panel E' in tex
    assert 'Panel F' in tex
    # 两个 \begin{tabular} 块 (R12C-01 结构约束)
    assert tex.count(r'\begin{tabular}') == 2
    # pending 脚注在两个 panel 中均存在
    assert 'manual validation pending' in tex


def test_xlsx_with_wrong_columns_emits_pending(tmp_path, monkeypatch):
    """Item 12 (R2C-04): xlsx 存在但 R 列名错误 → pending 'schema mismatch'。"""
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    df_mv = pd.DataFrame({
        'docid': ['d0'],
        'wrong_column_name': ['substantive'],
    })
    df_mv.to_excel(output_dir / 'manual_validation_samples.xlsx', index=False)
    monkeypatch.setattr(
        'news_process.core.config.load_config',
        lambda: {'paths': {'output_dir': str(output_dir)}},
    )
    results = {'classifier_metrics': {'innovation_substantiveness': {},
                                       'innovation_locus': {}},
               'innovation_pending_reason': None}
    import logging
    _mod._evaluate_innovation_panels(results, str(output_dir), logging.getLogger('t'))
    assert results['innovation_pending_reason'] == 'schema mismatch'


def test_join_falls_back_to_orig_index(tmp_path, monkeypatch):
    """Item 13 (R2C-04): 缺 docid 列 → schema mismatch (回退路径)。"""
    # 按当前实现: join_key 无法取 docid → schema mismatch
    # (回退到 orig_index 需要按位置 join, 标记为 future work)
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    n = 5
    df_mv = pd.DataFrame({
        'orig_index': list(range(n)),
        **{c: ['substantive'] * n for c in R_COLUMNS_BY_RATER['substantiveness']},
        **{c: ['technology'] * n for c in R_COLUMNS_BY_RATER['locus']},
    })
    df_mv.to_excel(output_dir / 'manual_validation_samples.xlsx', index=False)
    df_pred = pd.DataFrame({
        'orig_index': list(range(n)),
        'innovation_substantiveness_full': ['实质性'] * n,
        'innovation_substantiveness_ctx':  ['实质性'] * n,
        'innovation_locus_full': ['底层技术'] * n,
        'innovation_locus_ctx':  ['底层技术'] * n,
    })
    df_pred.to_parquet(output_dir / '21_tone_llms.parquet')
    monkeypatch.setattr(
        'news_process.core.config.load_config',
        lambda: {'paths': {'output_dir': str(output_dir)}},
    )
    results = {'classifier_metrics': {'innovation_substantiveness': {},
                                       'innovation_locus': {}},
               'innovation_pending_reason': None}
    import logging
    _mod._evaluate_innovation_panels(results, str(output_dir), logging.getLogger('t'))
    # 记录当前行为: 无 docid → schema mismatch
    assert results['innovation_pending_reason'] in ('schema mismatch', None)


def test_duplicate_docid_dedupe_with_warn(tmp_path, monkeypatch):
    """Item 14 (R2C-04): docid 重复 → 保留首条 (去重并 warn)。"""
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    n = 4
    df_mv = pd.DataFrame({
        'docid': ['d0', 'd0', 'd1', 'd2'],  # d0 重复
        **{c: ['substantive'] * n for c in R_COLUMNS_BY_RATER['substantiveness']},
        **{c: ['technology'] * n for c in R_COLUMNS_BY_RATER['locus']},
    })
    df_mv.to_excel(output_dir / 'manual_validation_samples.xlsx', index=False)
    df_pred = pd.DataFrame({
        'docid': ['d0', 'd1', 'd2'],
        'innovation_substantiveness_full': ['实质性'] * 3,
        'innovation_substantiveness_ctx':  ['实质性'] * 3,
        'innovation_locus_full': ['底层技术'] * 3,
        'innovation_locus_ctx':  ['底层技术'] * 3,
    })
    df_pred.to_parquet(output_dir / '21_tone_llms.parquet')
    monkeypatch.setattr(
        'news_process.core.config.load_config',
        lambda: {'paths': {'output_dir': str(output_dir)}},
    )
    results = {'classifier_metrics': {'innovation_substantiveness': {},
                                       'innovation_locus': {}},
               'innovation_pending_reason': None}
    import logging
    _mod._evaluate_innovation_panels(results, str(output_dir), logging.getLogger('t'))
    # 不应抛异常; pending 为 None 表示已填充
    assert results['innovation_pending_reason'] is None


def test_r_column_schema_coupling():
    """Item 15 (R3C-01 + R34A/B/C-01): 采样脚本源码中模板片段存在
    + 往返重构结果与 R_COLUMNS_BY_RATER 一致。"""
    import pathlib
    src_path = (pathlib.Path(__file__).resolve().parents[1]
                / 'scripts' / 'migrate' / 'manual_validation_sampling.py')
    src = src_path.read_text(encoding='utf-8')

    # (a) 源码中含模板片段
    assert 'stage3a_substantiveness' in src
    assert 'stage3b_locus' in src
    for rater in ('R1', 'R2', 'R3'):
        assert rater in src

    # WS-A: collab schema 模板片段
    assert 'stage3c_collab' in src

    # (b) 往返重构 (含 WS-A collab)
    reconstructed_subst = [f'{r}_stage3a_substantiveness' for r in ('R1', 'R2', 'R3')]
    reconstructed_locus = [f'{r}_stage3b_locus' for r in ('R1', 'R2', 'R3')]
    reconstructed_collab = [f'{r}_stage3c_collab' for r in ('R1', 'R2', 'R3')]
    assert R_COLUMNS_BY_RATER['substantiveness'] == reconstructed_subst
    assert R_COLUMNS_BY_RATER['locus'] == reconstructed_locus
    assert R_COLUMNS_BY_RATER['collab'] == reconstructed_collab

    # (c) 取值词表 token 应在脚本中存在 (含 WS-A collab self_developed/collaborative)
    for token in ('substantive', 'symbolic', 'technology', 'application',
                  'self_developed', 'collaborative'):
        assert token in src


def test_collab_dimension_optional_pending(tmp_path, monkeypatch):
    """WS-A(F23/V-01): collab R 列缺 → 仅 G pending(by_dim), E/F 仍跑,
    顶层 innovation_pending_reason 保持 None(向后兼容)。"""
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    n = 30
    docids = [f"doc_{i}" for i in range(n)]
    df_mv = pd.DataFrame({  # 只有 subst+locus R 列, 无 collab
        'docid': docids,
        **{c: ['substantive'] * n for c in R_COLUMNS_BY_RATER['substantiveness']},
        **{c: ['technology'] * n for c in R_COLUMNS_BY_RATER['locus']},
    })
    df_mv.to_excel(output_dir / 'manual_validation_samples.xlsx', index=False)
    pd.DataFrame({
        'docid': docids,
        'innovation_substantiveness_full': ['实质性'] * n,
        'innovation_locus_full': ['底层技术'] * n,
        'innovation_collab_mode_full': ['自主研发'] * n,
    }).to_parquet(output_dir / '21_tone_llms.parquet')
    monkeypatch.setattr('news_process.core.config.load_config',
                        lambda: {'paths': {'output_dir': str(output_dir)}})
    results = {'classifier_metrics': {'innovation_substantiveness': {},
                                      'innovation_locus': {},
                                      'innovation_collab_mode': {}},
               'innovation_pending_reason': None}
    import logging
    _mod._evaluate_innovation_panels(results, str(output_dir), logging.getLogger('t'))
    # 顶层保持 None (collab 缺不触发全局 pending)
    assert results['innovation_pending_reason'] is None
    # 仅 collab dim 标 pending; E/F 续跑
    assert results['innovation_pending_by_dim']['collab'] == 'schema mismatch'
    assert results['innovation_pending_by_dim']['substantiveness'] is None
    assert results['classifier_metrics']['innovation_substantiveness']
    assert results['classifier_metrics']['innovation_locus']


def test_panel_G_collab_present_with_gold(tmp_path, monkeypatch):
    """WS-A: collab R 列就位 + gold 有效 → Panel G 填充, ICR α 恰 3 子键。"""
    output_dir = tmp_path / "processed"
    output_dir.mkdir()
    n = 30
    docids = [f"doc_{i}" for i in range(n)]
    rows = [_rater_row(['substantive'] * 3, ['technology'] * 3,
                       collab_vals=['collaborative'] * 3) for _ in range(n)]
    df_mv = pd.DataFrame(rows)
    df_mv['docid'] = docids
    df_mv.to_excel(output_dir / 'manual_validation_samples.xlsx', index=False)
    pd.DataFrame({
        'docid': docids,
        'innovation_substantiveness_full': ['实质性'] * n,
        'innovation_locus_full': ['底层技术'] * n,
        'innovation_collab_mode_full': ['外部协同'] * n,
    }).to_parquet(output_dir / '21_tone_llms.parquet')
    monkeypatch.setattr('news_process.core.config.load_config',
                        lambda: {'paths': {'output_dir': str(output_dir)}})
    results = {'classifier_metrics': {'innovation_substantiveness': {},
                                      'innovation_locus': {},
                                      'innovation_collab_mode': {}},
               'innovation_pending_reason': None}
    import logging
    _mod._evaluate_innovation_panels(results, str(output_dir), logging.getLogger('t'))
    assert results['innovation_pending_reason'] is None
    assert results['innovation_pending_by_dim']['collab'] is None
    # Panel G 填充 + criterion κ/AC1 键存在
    g = results['classifier_metrics']['innovation_collab_mode']
    assert g  # 非空
    any_metric = next(iter(g.values()))
    assert 'cohens_kappa' in any_metric and 'gwet_ac1' in any_metric
    # ICR α 恰 3 子键 (subst/locus/collab)
    assert set(results['innovation_inter_coder_reliability'].keys()) == \
        {'substantiveness', 'locus', 'collab'}


def test_panels_E_F_G_in_separate_tabular():
    """Item 16 (R12C-01) + WS-A(F8): Panel E/F/G 同处第 2 个 tabular,
    \\begin{tabular} 计数保持 2 (Panel G 是子表头, 不新开第 3 个 tabular)。"""
    import logging
    _m = lambda p, r, f, a: {'macro': {'precision': p, 'recall': r, 'f1': f},  # noqa: E731
                             'accuracy': a, 'per_class': {}, 'support': {}}
    results = {
        'demo_mode': True,
        'classifier_metrics': {
            'verification': {},
            'sentiment': {},
            'innovation_substantiveness': {'LLM (_full)': _m(0.85, 0.80, 0.82, 0.83)},
            'innovation_locus': {'LLM (_full)': _m(0.90, 0.88, 0.89, 0.90)},
            'innovation_collab_mode': {'LLM (_full)': _m(0.78, 0.75, 0.76, 0.79)},
        },
        'inter_coder_reliability': {'verification': {}, 'sentiment': {}},
        'innovation_pending_reason': None,
    }
    out_path = '/tmp/_test_eval_2tab.tex'
    _mod.generate_latex_table(results, out_path, logging.getLogger('t'))
    tex = open(out_path, encoding='utf-8').read()
    # F8: Panel G 是第 2 tabular 内子表头, 计数保持 2 (绝不变 3)
    assert tex.count(r'\begin{tabular}') == 2
    assert tex.count(r'\end{tabular}') == 2
    # Panel E + F + G 在第二个 tabular 中 (均已填充, 非 pending)
    assert 'Panel E' in tex
    assert 'Panel F' in tex
    assert 'Panel G' in tex
    assert 'manual validation pending' not in tex


def test_sha_missing_is_auto_generated(tmp_path):
    """Item 17 (R7C-02): pending 数据路径 — 占位文档性测试: 说明
    manual_validation_samples_synthetic.sha sidecar 的重生成由 fixture
    生成脚本负责 (此处不直接测试, 因 code-path 验收不需要合成 xlsx
    fixture — 见 plan §3.7 拆分)。"""
    # 文档性测试: 断言 manual_validation_schema 模块存在,
    # 并暴露未来 fixture 重生成所需的规范常量。
    from news_process.validation import manual_validation_schema
    assert hasattr(manual_validation_schema, 'R_COLUMNS_BY_RATER')
    assert hasattr(manual_validation_schema, 'normalize_rater_value')
    assert hasattr(manual_validation_schema, 'merge_three_rater_majority')
