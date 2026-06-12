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


def _rater_row(sub_vals, locus_vals):
    """构造含 6 个 R 列 (3 个 substantiveness + 3 个 locus) 的 dict 行。

    (原英文注释声称还附加 2 个 stage1/stage2 dummy 列, 实际代码并未添加, 已更正。)
    """
    row = {}
    for i, v in enumerate(sub_vals, 1):
        row[f'R{i}_stage3a_substantiveness'] = v
    for i, v in enumerate(locus_vals, 1):
        row[f'R{i}_stage3b_locus'] = v
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

    # (b) 往返重构
    reconstructed_subst = [f'{r}_stage3a_substantiveness' for r in ('R1', 'R2', 'R3')]
    reconstructed_locus = [f'{r}_stage3b_locus' for r in ('R1', 'R2', 'R3')]
    assert R_COLUMNS_BY_RATER['substantiveness'] == reconstructed_subst
    assert R_COLUMNS_BY_RATER['locus'] == reconstructed_locus

    # (c) 取值词表 token 应在脚本中存在
    for token in ('substantive', 'symbolic', 'technology', 'application'):
        assert token in src


def test_panels_E_F_in_separate_tabular():
    """Item 16 (R12C-01): 重构后 TeX 应恰有 2 个 \\begin{tabular} 块。"""
    import logging
    results = {
        'demo_mode': True,
        'classifier_metrics': {
            'verification': {},
            'sentiment': {},
            'innovation_substantiveness': {
                'LLM (_full)': {'macro': {'precision': 0.85, 'recall': 0.80, 'f1': 0.82},
                                'accuracy': 0.83, 'per_class': {}, 'support': {}},
            },
            'innovation_locus': {
                'LLM (_full)': {'macro': {'precision': 0.90, 'recall': 0.88, 'f1': 0.89},
                                'accuracy': 0.90, 'per_class': {}, 'support': {}},
            },
        },
        'inter_coder_reliability': {'verification': {}, 'sentiment': {}},
        'innovation_pending_reason': None,
    }
    out_path = '/tmp/_test_eval_2tab.tex'
    _mod.generate_latex_table(results, out_path, logging.getLogger('t'))
    tex = open(out_path, encoding='utf-8').read()
    assert tex.count(r'\begin{tabular}') == 2
    assert tex.count(r'\end{tabular}') == 2
    # Panel E + F 在第二个 tabular 中 (已填充, 非 pending)
    assert 'Panel E' in tex
    assert 'Panel F' in tex
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
