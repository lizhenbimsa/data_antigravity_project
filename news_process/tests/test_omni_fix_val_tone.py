"""
tests/test_omni_fix_val_tone.py — omni 审计修复回归锁 (组 g-val-tone, 2026-06-11)
================================================================================

锁定 validation/tone_validation.py + validation/llms_evaluation.py 的 4 项修复行为:

  g-val-tone-01 (P1): discover_sentiment_columns BERT 组排除 IDF 词典名
                      (words_idf), probs 收紧为情感类别白名单 (排除 zscore)。
  g-val-tone-02 (P2): LLM 聚合投票列 short_name=='llm' 从 Cronbach α /
                      一致率 / 方法均值剔除, 仅作对比基准单独记录。
  g-val-tone-03 (P2): ECE 伪 ground truth 从 leave-one-in (含被评模型自身票
                      的多数票) 改为 leave-one-out 共识; 人工金标准优先级保留。
  g-val-tone-04 (P3): 人工验证样本双轨独立文件 (09_sentiment_verify{track}.xlsx)
                      + 编码指南随 track 对齐 prepend_title 口径 + 附机器输入
                      文本列; llms_evaluation 全文构念披露。

直接 import 生产函数 (合成 DataFrame, 不依赖盘上大数据, 无外部 API)。

# 白话: 这组测试锁的是情感测度"自我评分"环节的公正性: 1) 自动发现情感列时
# 别把 IDF 词典名、zscore 这类非情感列误收进来; 2) LLM 三模型的"合议票"不能
# 既当选手又当裁判 — 算模型间一致性时要把它剔出去; 3) 没有人工标注时用来
# 当"标准答案"的多数票, 不能包含被打分模型自己的那一票; 4) 给人工标注员的
# 抽样文件和编码指南要跟机器实际读到的文本(含拼接的标题)一致。
"""

import inspect
import json
import logging
import os

import numpy as np
import pandas as pd
import pytest

from news_process.validation.tone_validation import (
    _run_validation_for_track,
    diagnose_confidence_calibration,
    discover_sentiment_columns,
    generate_validation_sample,
)


@pytest.fixture
def test_logger():
    lg = logging.getLogger("test_omni_fix_val_tone")
    if not lg.handlers:
        lg.addHandler(logging.NullHandler())
    lg.propagate = False
    return lg


# ============================================================================
# g-val-tone-01: BERT 组排除 IDF 词典 + probs 白名单
# ============================================================================

class TestBertGroupExcludesIdf:
    """fix(omni-g-val-tone-01): IDF 词典不得泄漏进 'BERT' 组。"""

    @staticmethod
    def _make_df():
        n = 4
        return pd.DataFrame({
            # 等权词典
            'jiang_2021_score_full': [0.5] * n,
            'jiang_2021_label_full': ['正面'] * n,
            # IDF 词典 (score+label+zscore 三件套, 旧代码会把 label 误判为 BERT)
            'jiang_2021_idf_score_full': [0.4] * n,
            'jiang_2021_idf_label_full': ['正面'] * n,
            'jiang_2021_idf_zscore_full': [1.2] * n,
            'yao_2021_idf_score_full': [0.3] * n,
            'yao_2021_idf_label_full': ['中性'] * n,
            'yao_2021_idf_zscore_full': [-0.1] * n,
            # 孤儿 IDF label (无 score 对 → 不进 words_idf, 靠 '_idf' 子串守卫)
            'bian_2021_idf_label_full': ['负面'] * n,
            # 真 BERT 模型
            'finbert_cn_label_full': ['正面'] * n,
            'finbert_cn_正面_full': [0.8] * n,
            'finbert_cn_中性_full': [0.1] * n,
            'finbert_cn_负面_full': [0.1] * n,
            'finbert_cn_zscore_full': [0.5] * n,  # 派生列, 不是概率
            # LLM
            'gpt54nano_sentiment_full': ['正面'] * n,
            'gpt54nano_sentiment_confidence_full': [0.9] * n,
            # 聚合投票列
            'llm_sentiment_full': ['正面'] * n,
        })

    def test_bert_group_contains_only_real_bert_models(self):
        result = discover_sentiment_columns(self._make_df(), track_suffix='_full')
        assert set(result['bert'].keys()) == {'finbert_cn'}, (
            f"BERT 组应只剩真 BERT 模型, 实际: {sorted(result['bert'])}"
        )

    def test_idf_dicts_stay_in_words_idf_group(self):
        result = discover_sentiment_columns(self._make_df(), track_suffix='_full')
        assert 'jiang_2021_idf' in result['words_idf']
        assert 'yao_2021_idf' in result['words_idf']
        # 等权词典不受影响
        assert 'jiang_2021' in result['words']

    def test_orphan_idf_label_without_score_not_in_bert(self):
        """'_idf' 子串守卫: IDF 列缺 score 对时也不得泄漏进 BERT。"""
        result = discover_sentiment_columns(self._make_df(), track_suffix='_full')
        assert 'bian_2021_idf' not in result['bert']

    def test_probs_whitelist_excludes_zscore(self):
        """probs 仅收情感类别概率列 (正面/中性/负面), zscore 等派生列排除。"""
        result = discover_sentiment_columns(self._make_df(), track_suffix='_full')
        probs = result['bert']['finbert_cn']['probs']
        assert set(probs.keys()) == {'正面', '中性', '负面'}
        assert 'zscore' not in probs


# ============================================================================
# g-val-tone-03: ECE leave-one-out 伪 GT
# ============================================================================

class TestEceLeaveOneOut:
    """fix(omni-g-val-tone-03): ECE 伪 GT 排除被评模型自身票。"""

    @staticmethod
    def _make_loo_df():
        """80 行: 前 60 行 m2==m3 一致 ('正面'), 后 20 行 m2/m3 分歧。

        m1 在一致行上前 30 行预测正确 ('正面')、后 30 行预测错误 ('负面'),
        置信度恒 0.95 → LOO ECE = |0.5 - 0.95| = 0.45。
        llm_sentiment_full 故意 == m1 预测 (旧 leave-one-in GT 下 m1 全
        "正确", ECE = 0.05) — 用于证明新代码不再使用该列。
        """
        n_unanimous, n_split = 60, 20
        m1 = ['正面'] * 30 + ['负面'] * 30 + ['正面'] * n_split
        m2 = ['正面'] * n_unanimous + ['正面'] * n_split
        m3 = ['正面'] * n_unanimous + ['负面'] * n_split
        return pd.DataFrame({
            'm1_sentiment_full': m1,
            'm1_sentiment_confidence_full': [0.95] * (n_unanimous + n_split),
            'm2_sentiment_full': m2,
            'm3_sentiment_full': m3,
            'llm_sentiment_full': m1,  # 旧伪 GT == 被评模型自身预测
        })

    @staticmethod
    def _llm_cols():
        return {
            'm1': {'sentiment': 'm1_sentiment_full',
                   'confidence': 'm1_sentiment_confidence_full'},
            'm2': {'sentiment': 'm2_sentiment_full', 'confidence': None},
            'm3': {'sentiment': 'm3_sentiment_full', 'confidence': None},
            'llm': {'sentiment': 'llm_sentiment_full', 'confidence': None},
        }

    def test_loo_consensus_excludes_own_vote(self, tmp_path, test_logger):
        df = self._make_loo_df()
        result = diagnose_confidence_calibration(
            df, self._llm_cols(), '_full', str(tmp_path), test_logger
        )
        assert 'ece' in result, "应基于 leave-one-out 共识计算出 ECE"
        # LOO: 仅 60 一致行进入评估, m1 acc=0.5, conf=0.95 → ECE=0.45
        assert result['ece']['m1'] == pytest.approx(0.45, abs=0.01)
        # 若仍为 leave-one-in (gt=llm_sentiment_full==m1 预测) 则 ECE=0.05
        assert result['ece']['m1'] > 0.4, (
            "ECE 过低 → 疑似回退到含被评模型自身票的 leave-one-in 伪 GT"
        )
        assert 'leave-one-out' in result['ground_truth_source']

    def test_disagreement_rows_dropped_from_gt(self, tmp_path, test_logger):
        """m2/m3 分歧行应被剔除 (不计入任何 bin)。"""
        df = self._make_loo_df()
        result = diagnose_confidence_calibration(
            df, self._llm_cols(), '_full', str(tmp_path), test_logger
        )
        n_in_bins = sum(b['n'] for b in result['reliability_data']['m1'])
        assert n_in_bins == 60, f"应仅 60 一致行进入 ECE, 实际 {n_in_bins}"

    def test_human_gold_path_has_priority(self, tmp_path, test_logger):
        """人工金标准存在 (>100 非空) 时优先于 LOO 共识。"""
        n = 130
        df = pd.DataFrame({
            'm1_sentiment_full': ['正面'] * n,
            'm1_sentiment_confidence_full': [0.9] * n,
            # 其余模型全程分歧 → LOO 共识为空; 若 ECE 仍算得出 = 人工路径生效
            'm2_sentiment_full': ['正面'] * n,
            'm3_sentiment_full': ['负面'] * n,
            'human_sentiment_full': ['正面'] * n,
        })
        result = diagnose_confidence_calibration(
            df, self._llm_cols(), '_full', str(tmp_path), test_logger
        )
        assert '人工金标准' in result['ground_truth_source']
        # gold 全 '正面', m1 全对, conf=0.9 → ECE = 0.1
        assert result['ece']['m1'] == pytest.approx(0.1, abs=0.01)

    def test_single_model_without_peers_skips_ece(self, tmp_path, test_logger):
        """仅 1 个独立模型且无人工 gold → 无 LOO 来源, 优雅跳过 ECE。"""
        n = 60
        df = pd.DataFrame({
            'm1_sentiment_full': ['正面'] * n,
            'm1_sentiment_confidence_full': [0.9] * n,
            'llm_sentiment_full': ['正面'] * n,
        })
        llm_cols = {
            'm1': {'sentiment': 'm1_sentiment_full',
                   'confidence': 'm1_sentiment_confidence_full'},
            'llm': {'sentiment': 'llm_sentiment_full', 'confidence': None},
        }
        result = diagnose_confidence_calibration(
            df, llm_cols, '_full', str(tmp_path), test_logger
        )
        assert result['mode'] == 'descriptive_only'
        assert 'ece' not in result


# ============================================================================
# g-val-tone-02 + 01 + 04a 集成: _run_validation_for_track
# ============================================================================

def _make_track_df(n=60, seed=0):
    """合成含 词典(等权+IDF)/BERT/LLM(独立+聚合) 全家族的双轨 DataFrame。"""
    rng = np.random.RandomState(seed)
    cats = np.array(['正面', '中性', '负面'])
    base = rng.choice(cats, size=n)

    def noisy(p_flip=0.1):
        flip = rng.rand(n) < p_flip
        out = base.copy()
        out[flip] = rng.choice(cats, size=int(flip.sum()))
        return out

    label_num = {'正面': 1.0, '中性': 0.0, '负面': -1.0}

    def to_score(labels):
        return np.array([label_num[v] for v in labels]) + rng.normal(0, 0.05, n)

    cols = {
        '标题': [f'标题{i}' for i in range(n)],
        '内容': ['正文' * 50 for _ in range(n)],
        'content_full': [f'标题{i}。' + '正文' * 50 for i in range(n)],
        'content_ctx': [f'标题{i}。' + '窗口' * 10 for i in range(n)],
        '日期': pd.to_datetime(['2017-06-01'] * n),
    }
    # 词典 (等权 ×2 + IDF ×1)
    for d in ['dictA', 'dictB']:
        lab = noisy()
        cols[f'{d}_score_full'] = to_score(lab)
        cols[f'{d}_label_full'] = lab
    idf_lab = noisy()
    cols['dictA_idf_score_full'] = to_score(idf_lab)
    cols['dictA_idf_label_full'] = idf_lab
    cols['dictA_idf_zscore_full'] = rng.normal(0, 1, n)
    # BERT ×2
    for b in ['bertX', 'bertY']:
        lab = noisy()
        pos = np.clip(0.5 + 0.4 * np.array([label_num[v] for v in lab]), 0, 1)
        neg = np.clip(0.5 - 0.4 * np.array([label_num[v] for v in lab]), 0, 1)
        cols[f'{b}_label_full'] = lab
        cols[f'{b}_正面_full'] = pos
        cols[f'{b}_负面_full'] = neg
        cols[f'{b}_中性_full'] = np.clip(1 - pos - neg, 0, 1)
    # LLM 独立 ×3 + 聚合投票列
    llm_labels = {}
    for m in ['m1', 'm2', 'm3']:
        lab = noisy()
        llm_labels[m] = lab
        cols[f'{m}_sentiment_full'] = lab
        cols[f'{m}_sentiment_confidence_full'] = rng.uniform(0.7, 1.0, n)
    vote = []
    for i in range(n):
        votes = [llm_labels[m][i] for m in ['m1', 'm2', 'm3']]
        vote.append(max(set(votes), key=votes.count))
    cols['llm_sentiment_full'] = vote
    return pd.DataFrame(cols)


class TestRunValidationForTrackAggregateExclusion:
    """fix(omni-g-val-tone-02): 聚合列剔除 + fix-01 BERT 纯净 + fix-04a 双轨文件。"""

    @pytest.fixture(scope='class')
    def track_run(self, tmp_path_factory):
        out_dir = tmp_path_factory.mktemp('eval_reports')
        df = _make_track_df()
        lg = logging.getLogger('test_omni_fix_val_tone_e2e')
        if not lg.handlers:
            lg.addHandler(logging.NullHandler())
        lg.propagate = False
        _run_validation_for_track(df, '_full', str(out_dir), lg, {})
        json_path = os.path.join(str(out_dir), 'sentiment_validation_results_full.json')
        assert os.path.isfile(json_path)
        with open(json_path, encoding='utf-8') as f:
            results = json.load(f)
        return str(out_dir), results

    def test_llm_methods_exclude_aggregate(self, track_run):
        _, results = track_run
        detected = results['methods_detected']
        assert detected['llm'] == ['m1', 'm2', 'm3']
        assert 'llm' not in detected['llm']
        assert detected['llm_aggregate_excluded'] == ['llm']

    def test_aggregate_reported_as_benchmark_only(self, track_run):
        _, results = track_run
        bench = results['llm_aggregate_benchmark']
        assert bench['column'] == 'llm_sentiment_full'
        assert '非独立测量' in bench['note']

    def test_label_agreement_n_methods_excludes_aggregate_and_idf(self, track_run):
        """n_methods = 2 词典 + 2 BERT + 3 LLM = 7 (无聚合列/无 IDF)。"""
        _, results = track_run
        agreement = results['cross_method']['label_agreement']
        assert agreement['n_methods'] == 7

    def test_bert_group_pure_in_e2e(self, track_run):
        _, results = track_run
        assert sorted(results['methods_detected']['bert']) == ['bertX', 'bertY']

    def test_cronbach_csv_n_models(self, track_run):
        out_dir, _ = track_run
        csv_path = os.path.join(out_dir, 'cronbachs_alpha_summary_full.csv')
        assert os.path.isfile(csv_path)
        alpha_df = pd.read_csv(csv_path).set_index('方法')
        assert int(alpha_df.loc['LLM', 'N Models']) == 3
        assert int(alpha_df.loc['BERT', 'N Models']) == 2

    def test_verify_xlsx_has_track_suffix(self, track_run):
        """fix(omni-g-val-tone-04a): 双轨各写独立文件, 不再互相覆盖。"""
        out_dir, _ = track_run
        assert os.path.isfile(os.path.join(out_dir, '09_sentiment_verify_full.xlsx'))
        assert not os.path.exists(os.path.join(out_dir, '09_sentiment_verify.xlsx'))


# ============================================================================
# g-val-tone-04b: 编码指南 + 机器输入文本随 track 对齐
# ============================================================================

class TestValidationSampleTrackAlignment:
    """fix(omni-g-val-tone-04b): 编码协议与 prepend_title 后的机器口径对齐。"""

    @staticmethod
    def _inputs(n=30):
        df = pd.DataFrame({
            '标题': [f'标题{i}' for i in range(n)],
            '内容': ['正文文本'] * n,
            'content_full': [f'标题{i}。正文文本' for i in range(n)],
            'content_ctx': [f'标题{i}。实体窗口' for i in range(n)],
        })
        labels = pd.DataFrame({
            'LLM_m1': ['正面'] * (n // 2) + ['负面'] * (n - n // 2),
            'LLM_m2': ['正面'] * (n // 2) + ['中性'] * (n - n // 2),
        })
        vote = pd.Series(['正面'] * (n // 2) + ['中性'] * (n - n // 2))
        return df, labels, vote

    def _run(self, tmp_path, test_logger, track):
        df, labels, vote = self._inputs()
        out = tmp_path / f'09_sentiment_verify{track}.xlsx'
        generate_validation_sample(
            df, labels, vote, str(out), test_logger,
            n_agree=5, n_disagree=5, seed=42, track=track,
        )
        assert out.is_file()
        guide = pd.read_excel(out, sheet_name='编码指南').set_index('项目')
        data = pd.read_excel(out, sheet_name='验证数据')
        return guide, data

    def test_ctx_guide_uses_window_instructions(self, tmp_path, test_logger):
        guide, data = self._run(tmp_path, test_logger, '_ctx')
        assert '验证轨道' in guide.index
        assert 'ctx' in guide.loc['验证轨道', '说明']
        note = guide.loc['注意事项', '说明']
        assert '不受标题影响' not in note, "旧指南指示剔除标题信息, 与 prepend 口径矛盾"
        assert '实体上下文窗口' in note
        assert '机器输入文本' in data.columns
        assert data['机器输入文本'].str.contains('实体窗口').all()

    def test_full_guide_includes_title_in_judgment(self, tmp_path, test_logger):
        guide, data = self._run(tmp_path, test_logger, '_full')
        note = guide.loc['注意事项', '说明']
        assert '不受标题影响' not in note
        assert '标题+正文' in note
        assert '机器输入文本' in data.columns
        assert data['机器输入文本'].str.contains('正文文本').all()

    def test_missing_ctx_text_col_degrades_gracefully(self, tmp_path, test_logger):
        """content_ctx 缺失时不崩溃, 仅无机器输入文本列 (警告披露)。"""
        df, labels, vote = self._inputs()
        df = df.drop(columns=['content_ctx'])
        out = tmp_path / 'verify_no_ctx.xlsx'
        generate_validation_sample(
            df, labels, vote, str(out), test_logger,
            n_agree=5, n_disagree=5, seed=42, track='_ctx',
        )
        data = pd.read_excel(out, sheet_name='验证数据')
        assert '机器输入文本' not in data.columns


# ============================================================================
# g-val-tone-04c: llms_evaluation 全文构念披露
# ============================================================================

class TestGoldConstructDisclosure:
    """fix(omni-g-val-tone-04c): 同一全文 gold 评双轨的构念混淆已在报告披露。"""

    def test_disclosure_constant_exists(self):
        from news_process.validation import llms_evaluation
        assert hasattr(llms_evaluation, 'GOLD_CONSTRUCT_DISCLOSURE')
        text = llms_evaluation.GOLD_CONSTRUCT_DISCLOSURE
        assert '全文构念' in text
        assert '_ctx' in text

    def test_disclosure_wired_into_main_results(self):
        """main() 须把披露写进 results['gold_construct_disclosure']。"""
        from news_process.validation import llms_evaluation
        src = inspect.getsource(llms_evaluation.main)
        assert "results['gold_construct_disclosure']" in src
        assert 'GOLD_CONSTRUCT_DISCLOSURE' in src
