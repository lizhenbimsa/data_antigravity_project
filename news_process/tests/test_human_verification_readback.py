"""
tests/test_human_verification_readback.py — 人工标注回读比对回归锁 (2026-06-13)
================================================================================

锁定 validation/tone_validation.py 的 human-annot-readback 三项行为:

  1. evaluate_human_verification: 09_sentiment_verify{track}.xlsx 回读端 —
     全部方法标签列 (词典_*/BERT_*/LLM_*/多数投票标签) vs 人工判定_情感
     计算 accuracy/macro-P/R/F1 + Cohen's κ; 这是全项目唯一能为词典/BERT
     族产出人工验证指标的代码路径。
  2. 空表/缺文件优雅 pending, 且【不写任何指标文件】(防 2026-05-31
     demo 合成假产物被误引的覆辙)。
  3. 防覆盖守卫: 已填人工标注的工作台不得被 Step 7 重生覆盖
     (count_human_annotations + _run_validation_for_track 源码锁)。

# 白话: 以前考卷只管印不管批 — 这组测试锁住新补的"批改"环节: 填了表就出
# 真实成绩单, 没填就明说"待标注"绝不编分数, 而且填好的考卷不许被重印销毁。
"""

import inspect
import os

import pandas as pd
import pytest

from news_process.validation.tone_validation import (
    HUMAN_VERIFY_MIN_N,
    _run_validation_for_track,
    count_human_annotations,
    evaluate_human_verification,
)


class _SilentLogger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass


@pytest.fixture
def silent_logger():
    return _SilentLogger()


def _write_workbook(path, n=40, fill_human=True, perfect=True,
                    human_values=None, reason_values=None,
                    sheet_name='验证数据', with_method_cols=True,
                    with_stype=False):
    """构造合成 09_sentiment_verify 工作台 (sheet='验证数据')。

    perfect=True 时全部方法列与人工判定完全一致 → 期望 Acc/κ=1.0。
    human_values/reason_values 可显式覆盖人工列 (测非法词汇/只填理由)。
    """
    labels = ['正面', '中性', '负面']
    gold = [labels[i % 3] for i in range(n)]
    pred_ok = list(gold)
    # 非 perfect: 词典列整体错一类 (循环移位) → accuracy=0
    pred_bad = [labels[(i + 1) % 3] for i in range(n)]
    data = {'标题': [f't{i}' for i in range(n)]}
    if with_method_cols:
        data.update({
            '词典_jiang_2021': pred_ok if perfect else pred_bad,
            'BERT_finbert_cn': pred_ok,
            'LLM_llm': pred_ok,
            '多数投票标签': pred_ok,
        })
    if with_stype:
        data['样本类型'] = ['一致' if i % 2 == 0 else '分歧' for i in range(n)]
    data['人工判定_情感'] = (human_values if human_values is not None
                             else (gold if fill_human else [''] * n))
    data['人工判定_理由'] = (reason_values if reason_values is not None
                             else [''] * n)
    df = pd.DataFrame(data)
    with pd.ExcelWriter(path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return df


# ============================================================================
# 1. count_human_annotations — 守卫计数
# ============================================================================

class TestCountHumanAnnotations:
    def test_missing_file_returns_zero(self, tmp_path):
        assert count_human_annotations(str(tmp_path / 'nope.xlsx')) == 0

    def test_empty_workbook_returns_zero(self, tmp_path):
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=10, fill_human=False)
        assert count_human_annotations(p) == 0

    def test_filled_workbook_counts_valid_labels(self, tmp_path):
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=12, fill_human=True)
        assert count_human_annotations(p) == 12

    # ---- final-audit HV-P1-01/02 (fail-closed + 动过即保护) 回归锁 ----

    def test_invalid_vocabulary_still_protected(self, tmp_path):
        """标注员用错词汇 ('积极'/'1') 也是人工劳动, 必须计入守卫。"""
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=10,
                        human_values=['积极'] * 5 + ['1'] * 5)
        assert count_human_annotations(p) == 10

    def test_reason_only_still_protected(self, tmp_path):
        """只填了'人工判定_理由'未填情感列, 同样不许覆盖。"""
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=8, fill_human=False,
                        reason_values=['有疑问'] * 8)
        assert count_human_annotations(p) == 8

    def test_corrupt_file_fails_closed(self, tmp_path):
        """文件存在但损坏 → -1 (fail-closed), 绝不返回 0 放行重生。"""
        p = tmp_path / 'v.xlsx'
        p.write_bytes(b'PK\x03\x04' + b'\x00' * 64)
        assert count_human_annotations(str(p)) == -1

    def test_renamed_sheet_fails_closed(self, tmp_path):
        """sheet 被标注员改名 ('验证数据'→'Sheet1') → -1, 保护潜在标注。"""
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=10, fill_human=True, sheet_name='Sheet1')
        assert count_human_annotations(p) == -1

    def test_missing_human_headers_fails_closed(self, tmp_path):
        """人工判定两列表头全部丢失 → 结构异常 -1。"""
        p = str(tmp_path / 'v.xlsx')
        df = pd.DataFrame({'标题': ['a'], '词典_x': ['正面']})
        with pd.ExcelWriter(p, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='验证数据', index=False)
        assert count_human_annotations(p) == -1


# ============================================================================
# 2. evaluate_human_verification — 回读比对
# ============================================================================

class TestEvaluateHumanVerification:
    def test_missing_file_pending_no_output(self, tmp_path, silent_logger):
        out = str(tmp_path)
        res = evaluate_human_verification(
            str(tmp_path / 'nope.xlsx'), '_full', out, silent_logger)
        assert res['status'] == 'pending'
        assert not os.path.isfile(
            os.path.join(out, 'human_verify_metrics_full.csv'))

    def test_empty_annotations_pending_no_output(self, tmp_path, silent_logger):
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=20, fill_human=False)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        assert res['status'] == 'pending'
        assert res['n_annotated'] == 0
        # 红线: pending 时绝不落盘指标文件 (防空壳假产物)
        assert not os.path.isfile(
            os.path.join(str(tmp_path), 'human_verify_metrics_full.csv'))

    def test_filled_workbook_metrics_all_method_families(self, tmp_path,
                                                         silent_logger):
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=HUMAN_VERIFY_MIN_N + 9, fill_human=True,
                        perfect=True)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        assert res['status'] == 'ok'
        # 关键缺口锁: 词典/BERT 族必须在人工比对覆盖内 (stage 33 只评 LLM)
        for col in ['词典_jiang_2021', 'BERT_finbert_cn', 'LLM_llm',
                    '多数投票标签']:
            assert col in res['metrics'], f'{col} 未进入人工比对'
            assert res['metrics'][col]['accuracy'] == 1.0
            assert res['metrics'][col]['kappa_vs_human'] == 1.0
        csv_path = os.path.join(str(tmp_path), 'human_verify_metrics_full.csv')
        assert os.path.isfile(csv_path)
        out_df = pd.read_csv(csv_path, encoding='utf-8-sig')
        assert set(out_df['方法']) >= {'词典_jiang_2021', 'BERT_finbert_cn'}
        assert '口径说明' in out_df.columns

    def test_imperfect_prediction_detected(self, tmp_path, silent_logger):
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=HUMAN_VERIFY_MIN_N + 9, fill_human=True,
                        perfect=False)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        # 词典列被构造为全错 (循环移位), 其余列全对
        assert res['metrics']['词典_jiang_2021']['accuracy'] == 0.0
        assert res['metrics']['BERT_finbert_cn']['accuracy'] == 1.0

    def test_small_sample_flagged_insufficient(self, tmp_path, silent_logger):
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=HUMAN_VERIFY_MIN_N - 10, fill_human=True)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        assert res['status'] == 'insufficient'
        assert res['n_annotated'] == HUMAN_VERIFY_MIN_N - 10

    def test_track_note_distinguishes_ctx(self, tmp_path, silent_logger):
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=40, fill_human=True)
        res_ctx = evaluate_human_verification(p, '_ctx', str(tmp_path),
                                              silent_logger)
        res_full = evaluate_human_verification(p, '_full', str(tmp_path),
                                               silent_logger)
        assert '上下文窗口' in res_ctx['gold_construct_note']
        assert '混合下界' in res_ctx['gold_construct_note']
        assert res_full['gold_construct_note'] != res_ctx['gold_construct_note']


# ============================================================================
# 2b. final-audit 修复回归锁 (T4-01 / HV-P2-04/05 / HV-P2-02)
# ============================================================================

class TestFinalAuditFixes:
    def test_stale_csv_cleaned_on_pending(self, tmp_path, silent_logger):
        """T4-01: 工作台被清空后, 上一轮的指标 CSV 必须被清除 (防假产物)。"""
        p = str(tmp_path / 'v.xlsx')
        out = str(tmp_path)
        _write_workbook(p, n=40, fill_human=True)
        evaluate_human_verification(p, '_full', out, silent_logger)
        csv_path = os.path.join(out, 'human_verify_metrics_full.csv')
        assert os.path.isfile(csv_path)
        _write_workbook(p, n=40, fill_human=False)  # 清空标注
        res = evaluate_human_verification(p, '_full', out, silent_logger)
        assert res['status'] == 'pending'
        assert not os.path.isfile(csv_path), '陈旧指标 CSV 未被清除'

    def test_no_method_cols_is_error_no_csv(self, tmp_path, silent_logger):
        """HV-P2-05: 无任何方法列 → error 且不写退化空 CSV。"""
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=40, fill_human=True, with_method_cols=False)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        assert res['status'] == 'error'
        assert not os.path.isfile(
            os.path.join(str(tmp_path), 'human_verify_metrics_full.csv'))

    def test_invalid_values_reported_not_silenced(self, tmp_path,
                                                  silent_logger):
        """HV-P1-02 (评估端): 非法标注值计入 n_nonempty_invalid 告警字段。"""
        p = str(tmp_path / 'v.xlsx')
        labels = ['正面', '中性', '负面']
        n = 40
        vals = [labels[i % 3] for i in range(n)]
        vals[:6] = ['积极'] * 6  # 6 条非法
        _write_workbook(p, n=n, human_values=vals)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        assert res['n_nonempty_invalid'] == 6
        assert res['n_annotated'] == n - 6

    def test_method_level_status_by_n_valid(self, tmp_path, silent_logger):
        """HV-P2-04: 方法级 n_valid<30 时该行状态必须是'样本不足'。"""
        p = str(tmp_path / 'v.xlsx')
        n = 40
        labels = ['正面', '中性', '负面']
        gold = [labels[i % 3] for i in range(n)]
        df = pd.DataFrame({
            '标题': [f't{i}' for i in range(n)],
            '词典_jiang_2021': gold,                      # n_valid=40
            'BERT_finbert_cn': gold[:10] + [''] * (n - 10),  # n_valid=10
            '人工判定_情感': gold,
            '人工判定_理由': [''] * n,
        })
        with pd.ExcelWriter(p, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='验证数据', index=False)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        assert res['metrics']['词典_jiang_2021']['status'] == '正常'
        assert '样本不足' in res['metrics']['BERT_finbert_cn']['status']

    def test_stratified_accuracy_when_sample_type_present(self, tmp_path,
                                                          silent_logger):
        """HV-P2-02: 工作台含'样本类型'时输出一致/分歧分层 accuracy。"""
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=40, fill_human=True, with_stype=True)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        strat = res['metrics']['词典_jiang_2021']['accuracy_by_stratum']
        assert strat == {'一致': 1.0, '分歧': 1.0}
        out_df = pd.read_csv(
            os.path.join(str(tmp_path), 'human_verify_metrics_full.csv'),
            encoding='utf-8-sig')
        assert 'Accuracy_一致' in out_df.columns
        assert 'Accuracy_分歧' in out_df.columns

    def test_duplicate_mangled_columns_excluded(self, tmp_path,
                                                silent_logger):
        """HV-INFO-03: pandas 重复表头 mangle 出的 '列.1' 不计入方法。"""
        p = str(tmp_path / 'v.xlsx')
        n = 40
        labels = ['正面', '中性', '负面']
        gold = [labels[i % 3] for i in range(n)]
        df = pd.DataFrame({
            '标题': [f't{i}' for i in range(n)],
            '词典_jiang_2021': gold,
            '词典_jiang_2021.1': gold,  # 模拟 mangle 产物
            '人工判定_情感': gold,
            '人工判定_理由': [''] * n,
        })
        with pd.ExcelWriter(p, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='验证数据', index=False)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        assert '词典_jiang_2021' in res['metrics']
        assert '词典_jiang_2021.1' not in res['metrics']

    def test_sampling_disclosure_in_note(self, tmp_path, silent_logger):
        """HV-P2-02/F2: 口径说明必须披露选择性抽样与单编码者协议。"""
        p = str(tmp_path / 'v.xlsx')
        _write_workbook(p, n=40, fill_human=True)
        res = evaluate_human_verification(p, '_full', str(tmp_path),
                                          silent_logger)
        assert 'oversample' in res['gold_construct_note']
        assert '单编码者' in res['gold_construct_note']


# ============================================================================
# 3. 防覆盖守卫 — 源码锁 (行为锁见 TestCountHumanAnnotations fail-closed 组)
# ============================================================================

class TestOverwriteGuardWired:
    def test_step7_guards_and_evaluates(self):
        src = inspect.getsource(_run_validation_for_track)
        # 重生前必须先查人工痕迹; fail-closed 分支必须存在;
        # 无论生成与否都必须回读评估并入 results
        assert 'count_human_annotations' in src
        assert 'n_existing < 0' in src, 'fail-closed 分支被移除'
        assert "results['human_verification']" in src
        assert 'evaluate_human_verification' in src
        # 仅"确认空白"(==0) 才允许走重生分支 (else 在 <0 / >0 之后)
        assert 'generate_validation_sample' in src.split('n_existing < 0')[1]


# ============================================================================
# 4. llms_evaluation 构念披露 — HV-P1-03 死分支回归锁
# ============================================================================

class TestConstructDisclosure:
    def test_all_real_key_shapes_hit_ctx(self):
        """真实键形 ('LLM 情感分析 (_ctx)' 等) 必须命中 ctx 披露。"""
        from news_process.validation.llms_evaluation import (
            GOLD_CONSTRUCT_DISCLOSURE,
            construct_disclosure_for,
        )
        for key in ['LLM 情感分析 (_ctx)', 'gpt54nano_ctx (独立)',
                    'gpt54nano_ctx', 'llm_ctx']:
            assert construct_disclosure_for(key) == GOLD_CONSTRUCT_DISCLOSURE, key
        for key in ['LLM 情感分析 (_full)', 'gpt54nano_full (独立)',
                    'gpt54nano_full', '规则分类器']:
            out = construct_disclosure_for(key)
            assert out != GOLD_CONSTRUCT_DISCLOSURE, key
            assert out != '', 'full 轨口径说明不得为空串'

    def test_csv_sites_use_single_source(self):
        """三个 CSV 落盘点不得再各自手写 endswith 判断 (死分支防回归)。"""
        import news_process.validation.llms_evaluation as mod
        src = inspect.getsource(mod)
        assert src.count('construct_disclosure_for(') >= 3  # def + 2 调用
        # 不许出现作为代码的 endswith('_ctx') 判断 (docstring/注释里的
        # 历史记载以反引号/中文括号语境出现, 不以 'if ' 前缀)
        assert "if name.endswith('_ctx')" not in src
        assert "if model_name.endswith('_ctx')" not in src
