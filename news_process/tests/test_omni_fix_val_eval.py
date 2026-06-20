"""
tests/test_omni_fix_val_eval.py — omni 审计修复组 g-val-eval 回归锁
====================================================================

锁定 validation/llms_evaluation.py 的 5 条修复行为 (fix(omni-*, 2026-06-11)):

  - g-val-eval-01/05: 情感评估域剔除 NaN/非法标签预测行 (不再 fillna('中性')
    伪造中性预测), coverage 单独报告; 逐模型同病同修。
  - g-val-eval-02: demo_mode 全部产物加 _DEMO 文件名后缀 + LaTeX caption
    [SYNTHETIC-DEMO] 前缀 + 表内警示行。
  - g-val-eval-03: 金标准提取排除待仲裁哨兵 (最终_验证=-1 / 最终_情感='待仲裁'),
    attrition 单独报告; stage 33 显式优先读取 *_merged.xlsx。
  - g-val-eval-04: import math 提升到模块级 (验证 ICR 缺失而情感 ICR 存在时
    G-10 报告段不再 UnboundLocalError)。
  - 组裁决补充: diagnose_misclassification_bias 的 gold fillna(0) 同理剔除。

全部用合成 DataFrame, 不依赖盘上大数据, 不调外部 API。

# 白话: 这是给"模型 vs 人工标注"评估打分器本身上锁: 模型没给出预测的行
# 不能偷偷填成"中性"再算成"答对了", 要剔除并单独报覆盖率; 人工还没仲裁完
# 的样本(-1/待仲裁)不算金标准; 演示模式跑出来的假数据, 所有文件名和表格
# 标题都要打上 DEMO 警示, 防止误引用。
"""

import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

_PROJECT_PARENT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.validation import llms_evaluation as _mod

LABELS_SEN = ['正面', '中性', '负面']


# ============================================================================
# 1. _demo_marked_path (omni-g-val-eval-02)
# ============================================================================

def test_demo_marked_path_suffix():
    p = os.path.join('a', 'b', 'classification_eval_table.tex')
    assert _mod._demo_marked_path(p, False) == p
    marked = _mod._demo_marked_path(p, True)
    assert marked.endswith('classification_eval_table_DEMO.tex')


def test_demo_marked_path_preserves_extension():
    assert _mod._demo_marked_path('x/cm_plot.png', True).endswith('cm_plot_DEMO.png')
    assert _mod._demo_marked_path('x/results.json', True).endswith('results_DEMO.json')


# ============================================================================
# 2. generate_latex_table demo 标记 (omni-g-val-eval-02)
# ============================================================================

def _minimal_results(demo: bool) -> dict:
    return {
        'demo_mode': demo,
        'classifier_metrics': {
            'verification': {
                'LLM (_full)': {'macro': {'precision': 0.9, 'recall': 0.9, 'f1': 0.9},
                                'accuracy': 0.9, 'per_class': {}},
            },
            'sentiment': {},
            'innovation_substantiveness': {},
            'innovation_locus': {},
        },
        'inter_coder_reliability': {'verification': {}, 'sentiment': {}},
        'innovation_pending_reason': 'file not present',
    }


def test_latex_table_demo_caption_and_warning_row(tmp_path):
    import logging
    out = tmp_path / 'eval_demo.tex'
    _mod.generate_latex_table(_minimal_results(True), str(out), logging.getLogger('t'))
    tex = out.read_text(encoding='utf-8')
    assert '[SYNTHETIC-DEMO]' in tex
    assert 'SYNTHETIC DEMO DATA' in tex
    assert 'do not cite' in tex


def test_latex_table_real_mode_unmarked(tmp_path):
    import logging
    out = tmp_path / 'eval_real.tex'
    _mod.generate_latex_table(_minimal_results(False), str(out), logging.getLogger('t'))
    tex = out.read_text(encoding='utf-8')
    assert '[SYNTHETIC-DEMO]' not in tex
    assert 'SYNTHETIC DEMO DATA' not in tex
    assert r'\caption{Validation and Sentiment Performance Evaluation}' in tex


# ============================================================================
# 3. _sentiment_eval_domain (omni-g-val-eval-01/05)
# ============================================================================

def test_sentiment_eval_domain_excludes_nan_and_invalid_labels():
    frame = pd.DataFrame({
        'gold': ['正面', '中性', '负面', '正面', '中性', '负面'],
        'pred': ['正面', '中性', np.nan, '无关', '中性 ', None],
    })
    y_gold, y_pred, cov, mask = _mod._sentiment_eval_domain(
        frame, 'pred', 'gold', LABELS_SEN)
    # NaN ×2 + 非法标签 '无关' ×1 剔除; '中性 ' (带尾空格) strip 后有效
    assert cov['n_gold'] == 6
    assert cov['n_valid_pred'] == 3
    assert cov['n_excluded_invalid_pred'] == 3
    assert cov['coverage'] == 0.5
    assert list(y_pred) == ['正面', '中性', '中性']
    assert list(y_gold) == ['正面', '中性', '中性']
    assert int(mask.sum()) == 3


def test_sentiment_eval_domain_no_neutral_fabrication():
    """旧实现把 NaN 行 fillna('中性') 后, gold='中性' 的 NaN 行会被伪判为'正确'。"""
    frame = pd.DataFrame({
        'gold': ['中性', '中性', '中性'],
        'pred': [np.nan, np.nan, '中性'],
    })
    y_gold, y_pred, cov, _ = _mod._sentiment_eval_domain(
        frame, 'pred', 'gold', LABELS_SEN)
    # 仅 1 行进入评估域 — 旧实现会得到 3 行全'正确' (伪 accuracy=1.0 且 n=3)
    assert cov['n_valid_pred'] == 1
    assert len(y_gold) == 1 and len(y_pred) == 1


def test_sentiment_eval_domain_empty_frame():
    frame = pd.DataFrame({'gold': pd.Series(dtype=object),
                          'pred': pd.Series(dtype=object)})
    y_gold, y_pred, cov, _ = _mod._sentiment_eval_domain(
        frame, 'pred', 'gold', LABELS_SEN)
    assert cov == {'n_gold': 0, 'n_valid_pred': 0,
                   'n_excluded_invalid_pred': 0, 'coverage': 0.0}
    assert len(y_gold) == 0


# ============================================================================
# 4. diagnose_misclassification_bias gold 域 (omni-g-val-eval-01/03 + 组裁决)
# ============================================================================

def test_diagnose_excludes_nan_and_sentinel_gold():
    """gold NaN / -1 (待仲裁哨兵) 不再 fillna(0) 伪造成 gold=0。"""
    df = pd.DataFrame({
        '最终_验证': [1, 1, 0, 0, np.nan, -1],
        'llm_verified_full': [True, True, False, True, True, True],
        'llm_sentiment_full': ['正面'] * 6,
        '内容': ['测试' * 50] * 6,
    })
    r = _mod.diagnose_misclassification_bias(df, '最终_验证', '_full')
    assert r['n_gold_excluded'] == 2
    qc = r['quadrant_counts']
    # 仅 4 条有效金标准进入四象限 (旧实现: NaN/-1 → gold=0, FP 虚增 2 条)
    assert qc['TP'] + qc['FP'] + qc['FN'] + qc['TN'] == 4
    assert qc == {'TP': 2, 'FP': 1, 'FN': 0, 'TN': 1}


def test_diagnose_clean_gold_zero_excluded():
    df = pd.DataFrame({
        '最终_验证': [1, 0, 1, 0],
        'llm_verified_full': [True, False, True, False],
        'llm_sentiment_full': ['中性'] * 4,
        '内容': ['测试' * 30] * 4,
    })
    r = _mod.diagnose_misclassification_bias(df, '最终_验证', '_full')
    assert r['n_gold_excluded'] == 0
    assert sum(r['quadrant_counts'].values()) == 4


def test_diagnose_demo_csv_suffix(tmp_path):
    df = pd.DataFrame({
        '最终_验证': [1, 0, 1, 0],
        'llm_verified_full': [True, False, False, True],
        'llm_sentiment_full': ['正面', '中性', '负面', '中性'],
        '内容': ['测试' * 30] * 4,
    })
    _mod.diagnose_misclassification_bias(
        df, '最终_验证', '_full', output_dir=str(tmp_path), demo_mode=True)
    assert (tmp_path / 'misclassification_bias_diag_full_DEMO.csv').exists()
    assert not (tmp_path / 'misclassification_bias_diag_full.csv').exists()


# ============================================================================
# 5. import math 模块级 (omni-g-val-eval-04)
# ============================================================================

def test_math_is_module_level():
    import types
    assert isinstance(getattr(_mod, 'math', None), types.ModuleType)


# ============================================================================
# 6. main() 端到端 (合成 xlsx, 全部修复联动)
# ============================================================================

def _patch_config(monkeypatch, out_dir: str, models=None):
    cfg = {
        'paths': {'output_dir': out_dir, 'log_dir': out_dir},
        'filenames': {'output_32_human_sample': '61_human_samples.xlsx'},
        'tone_llm_processing': {'models': models or []},
    }
    monkeypatch.setattr(_mod, 'CONFIG', cfg)
    # 模块内 load_config (diagnose/_generate_demo_data) + 内嵌 import
    # (_evaluate_innovation_panels) 双双打补丁, 保持测试封闭。
    monkeypatch.setattr(_mod, 'load_config', lambda: cfg)
    monkeypatch.setattr('news_process.core.config.load_config', lambda: cfg)
    return cfg


def _build_annotated_df() -> pd.DataFrame:
    """10 行合成标注: 含验证哨兵 -1 ×2 / 情感哨兵 '待仲裁' ×2 / 预测 NaN+非法。

    设计意图 (新旧行为可区分):
      - 验证: 8 行 gold∈{0,1} 且预测全对 → 修复后 accuracy=1.0
        (旧实现含 -1 行 → accuracy=0.8 且对 labels=[0,1] 虚假 FP)。
      - 情感: 8 行合法金标准中, 6 行预测正确, 1 行 NaN, 1 行 '无关'
        → 修复后 coverage=6/8=0.75, accuracy=1.0
        (旧实现 fillna('中性') → 10 行评估域, accuracy=7/10)。
      - 编码者A/B_验证 全空而 编码者A/B_情感 全有 → 复现 omni-04 的
        G-10 情感 κ CI 分支 (旧实现 UnboundLocalError: math)。
    """
    gold_ver = [1, 1, 1, 1, 0, 0, -1, -1, 1, 0]
    gold_sen = ['正面', '正面', '负面', '负面', '中性', '中性',
                '待仲裁', '待仲裁', '正面', '中性']
    pred_ver = [bool(v == 1) for v in [1, 1, 1, 1, 0, 0, 1, 1, 1, 0]]
    pred_sen = ['正面', '正面', '负面', '负面', '中性', '中性',
                None, None, None, '无关']
    coder_sen = ['正面', '正面', '负面', '负面', '中性', '中性',
                 '正面', '负面', '正面', '中性']
    return pd.DataFrame({
        '样本编号': range(1, 11),
        '标题': [f't{i}' for i in range(10)],
        '内容': ['测' * 100] * 10,
        'llm_verified_full': pred_ver,
        'llm_verified_ctx': pred_ver,
        'llm_sentiment_full': pred_sen,
        'llm_sentiment_ctx': pred_sen,
        '编码者A_验证': [None] * 10,
        '编码者B_验证': [None] * 10,
        '编码者A_情感': coder_sen,
        '编码者B_情感': coder_sen,
        '最终_验证': gold_ver,
        '最终_情感': gold_sen,
    })


@pytest.mark.integration
def test_main_real_annotations_sentinels_nan_pred_and_math(tmp_path, monkeypatch):
    out_dir = str(tmp_path)
    _patch_config(monkeypatch, out_dir)
    _build_annotated_df().to_excel(
        os.path.join(out_dir, '61_human_samples.xlsx'), index=False)

    _mod.main()  # 旧实现会在 G-10 情感 κ CI 处 UnboundLocalError (omni-04)

    json_path = os.path.join(out_dir, 'eval_reports',
                             'classification_eval_results.json')
    assert os.path.exists(json_path), '真实标注 → 非 demo, 文件名不带 _DEMO'
    with open(json_path, encoding='utf-8') as f:
        results = json.load(f)

    assert results['demo_mode'] is False
    # omni-03: 哨兵剔除 + attrition 报告
    assert results['n_gold_ver'] == 8
    assert results['gold_standard_attrition'] == {
        'verification_pending_arbitration': 2,
        'sentiment_pending_arbitration': 2,
    }
    # 验证任务: -1 哨兵剔除后预测全对 → accuracy=1.0 (旧实现 0.8)
    ver_m = results['classifier_metrics']['verification']['LLM 验证 (_full)']
    assert ver_m['accuracy'] == 1.0
    assert ver_m['total'] == 8

    # omni-01/05: 情感 NaN/非法预测剔除 → 评估域 6 行全对, coverage=0.75
    sen_m = results['classifier_metrics']['sentiment']['LLM 情感分析 (_full)']
    assert sen_m['accuracy'] == 1.0
    assert sen_m['total'] == 6
    assert sen_m['coverage'] == 0.75
    assert sen_m['n_excluded_invalid_pred'] == 2
    cov = results['sentiment_prediction_coverage']['LLM 情感分析 (_full)']
    assert cov['n_gold'] == 8 and cov['n_valid_pred'] == 6
    # 被剔除 2 行中 1 行是相关性筛选拒绝 (llm_verified=False) 行
    assert cov['n_excluded_unverified'] == 1

    # omni-04: 情感 κ CI 已写入标准化报告 CSV (math 模块级可用; 旧实现在
    # 验证 ICR 缺失而情感 ICR 存在时于此处 UnboundLocalError, 报告无法产出)
    std_df = pd.read_csv(
        os.path.join(out_dir, 'eval_reports', 'validation_standard_report.csv'),
        encoding='utf-8-sig')
    assert '情感任务_κ_95%CI' in std_df.columns

    # 真实模式产物不带 _DEMO 后缀
    assert os.path.exists(os.path.join(out_dir, 'eval_reports',
                                       'classification_eval_table.tex'))
    assert not os.path.exists(os.path.join(out_dir, 'eval_reports',
                                           'classification_eval_table_DEMO.tex'))


@pytest.mark.integration
def test_main_prefers_merged_xlsx(tmp_path, monkeypatch):
    """omni-03: 存在 *_merged.xlsx 时优先消费合并产物。"""
    out_dir = str(tmp_path)
    _patch_config(monkeypatch, out_dir)
    # 原始标注 10 行; 合并产物 12 行 (n_samples 可区分来源)
    _build_annotated_df().to_excel(
        os.path.join(out_dir, '61_human_samples.xlsx'), index=False)
    df_merged = pd.concat(
        [_build_annotated_df(), _build_annotated_df().head(2)],
        ignore_index=True)
    df_merged.to_excel(
        os.path.join(out_dir, '61_human_samples_merged.xlsx'), index=False)

    _mod.main()

    json_path = os.path.join(out_dir, 'eval_reports',
                             'classification_eval_results.json')
    with open(json_path, encoding='utf-8') as f:
        results = json.load(f)
    assert results['n_samples'] == 12, '应读 merged 产物 (12 行) 而非原始 (10 行)'


@pytest.mark.integration
def test_main_demo_mode_artifacts_all_marked(tmp_path, monkeypatch):
    """omni-02: 标注文件缺失 → demo_mode → 全部产物 _DEMO 后缀 + caption 警示。"""
    out_dir = str(tmp_path)
    _patch_config(monkeypatch, out_dir)
    # 不写 61_human_samples.xlsx → demo 分支

    _mod.main()

    reports = os.path.join(out_dir, 'eval_reports')
    assert os.path.exists(os.path.join(reports, 'classification_eval_results_DEMO.json'))
    assert not os.path.exists(os.path.join(reports, 'classification_eval_results.json'))
    tex_path = os.path.join(reports, 'classification_eval_table_DEMO.tex')
    assert os.path.exists(tex_path)
    assert not os.path.exists(os.path.join(reports, 'classification_eval_table.tex'))
    tex = open(tex_path, encoding='utf-8').read()
    assert '[SYNTHETIC-DEMO]' in tex
    assert 'SYNTHETIC DEMO DATA' in tex
    assert os.path.exists(os.path.join(reports, 'classification_eval_summary_DEMO.csv'))
    assert os.path.exists(os.path.join(reports, 'validation_standard_report_DEMO.csv'))
    assert os.path.exists(os.path.join(reports, 'misclassification_bias_diag_full_DEMO.csv'))

    with open(os.path.join(reports, 'classification_eval_results_DEMO.json'),
              encoding='utf-8') as f:
        results = json.load(f)
    assert results['demo_mode'] is True
