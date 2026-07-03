"""G-1/G-3 gate — 盲标双文件协议回归锁 (WP-A/B, 2026-07-03)。

锁定三件事:
  1. 盲表列白名单: 任何机器判定/抽样层/权重列出现在编码员盲表即红
     (锚定偏差防线; 协议=scripts/audit/HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md)。
  2. A/B 双副本行序一致 + reconciliation _row_uid 与盲表双射
     (⚠ docid 为 文章×银行 粒度非唯一, 禁作 join 键 — R4 实证)。
  3. 09 盲标回读: 双编码共识 → inter_coder κ/α 出键 + Manski-Lerman
     加权指标出键; 重复 docid 下无 join 行爆炸。
"""
import os
import re

import pandas as pd
import pytest

from news_process.validation import llms_human
from news_process.validation.tone_validation import (
    count_human_annotations,
    evaluate_human_verification,
    generate_validation_sample,
)

#: 盲表列黑名单模式 (出现任一即为盲标破坏)
FORBIDDEN = re.compile(
    r'(_tone|_verified|_sentiment|词典_|BERT_|LLM_|投票|样本类型|population_weight)')


class _SilentLogger:
    def info(self, *a, **k):
        pass

    def warning(self, *a, **k):
        pass


@pytest.fixture
def silent_logger():
    return _SilentLogger()


# ============================================================================
# 1. 61 侧 (llms_human) — 盲表/对账表拆分
# ============================================================================

def _sample_frame_61(n=12):
    return pd.DataFrame({
        '_row_uid': range(n),
        'docid': [i // 2 for i in range(n)],  # 刻意重复 — 模拟 article×bank 粒度
        '日期': ['2017-01-01'] * n,
        '媒体类型(中文)': ['报纸'] * n,
        '标题': [f't{i}' for i in range(n)],
        '内容': ['c'] * n,
        'target_bank': ['工商银行'] * n,
        'llm_verified_full': [True] * n,
        'gpt54nano_sentiment_full': ['正面'] * n,
        '编码者A_验证': [''] * n,
        '编码者B_验证': [''] * n,
        '编码者A_情感': [''] * n,
        '编码者B_情感': [''] * n,
    })


class TestBlind61:
    def test_blind_workbook_whitelist_and_per_coder_cols(self, tmp_path):
        sdf = _sample_frame_61()
        for coder, other in (('A', 'B'), ('B', 'A')):
            p = str(tmp_path / f'blind_{coder}.xlsx')
            llms_human._write_blind_workbook(sdf, coder, p)
            got = pd.read_excel(p, sheet_name='验证数据')
            bad = [c for c in got.columns if FORBIDDEN.search(str(c))]
            assert not bad, f'盲表{coder} 泄露机器/抽样列: {bad}'
            assert f'编码者{coder}_验证' in got.columns
            assert f'编码者{coder}_情感' in got.columns
            assert f'编码者{other}_验证' not in got.columns, '另一位编码员判定不得同表 (独立性)'
            assert '_row_uid' in got.columns and 'target_bank' in got.columns
            guide = pd.read_excel(p, sheet_name='编码指南')
            assert '独立性' in guide['项目'].values

    def test_reconciliation_keeps_machine_drops_annotation(self, tmp_path):
        sdf = _sample_frame_61()
        p = str(tmp_path / 'recon.xlsx')
        llms_human._write_reconciliation(sdf, p)
        got = pd.read_excel(p, sheet_name='验证数据')
        assert 'llm_verified_full' in got.columns
        assert '_row_uid' in got.columns and got['_row_uid'].is_unique
        assert sorted(got['_row_uid']) == sorted(sdf['_row_uid']), '_row_uid 须与盲表双射'
        assert not any(c in got.columns for c in llms_human._ANNOTATION_COLS)

    def test_derive_blind_paths_naming(self):
        p = llms_human.derive_blind_paths(os.path.join('x', '61_human_samples.xlsx'))
        assert p['blind_A'].endswith('61_human_samples_blind_A.xlsx')
        assert p['blind_B'].endswith('61_human_samples_blind_B.xlsx')
        assert p['reconciliation'].endswith('61_human_samples_reconciliation.xlsx')
        assert p['pending'].endswith('61_human_samples_pending_adjudication.xlsx')


# ============================================================================
# 2. 09 侧 (tone_validation 生成端) — 盲表/对账表拆分 + 权重落盘
# ============================================================================

def _inputs_09(n=40):
    half = n // 2
    df = pd.DataFrame({
        'docid': [i // 2 for i in range(n)],  # 刻意重复 docid
        '标题': [f'标题{i}' for i in range(n)],
        '内容': ['正文'] * n,
        '日期': ['2018-01-01'] * n,
        '媒体(中文)': ['报'] * n,
        'content_full': [f'标题{i}。正文' for i in range(n)],
    })
    labels = pd.DataFrame({
        '词典_x': ['正面'] * half + ['负面'] * (n - half),
        'BERT_y': ['正面'] * half + ['中性'] * (n - half),
    })
    vote = pd.Series(['正面'] * half + ['负面'] * (n - half))
    return df, labels, vote


class TestBlind09Generation:
    def _generate(self, tmp_path, silent_logger):
        df, labels, vote = _inputs_09()
        base = tmp_path / '09_sentiment_verify_full.xlsx'
        generate_validation_sample(
            df, labels, vote, str(base), silent_logger,
            n_agree=8, n_disagree=8, seed=42, track='_full')
        b, e = os.path.splitext(str(base))
        return base, f'{b}_blind_A{e}', f'{b}_blind_B{e}', f'{b}_reconciliation{e}'

    def test_split_whitelist_bijection_and_no_legacy(self, tmp_path, silent_logger):
        base, ba, bb, rp = self._generate(tmp_path, silent_logger)
        assert not base.is_file(), '旧单文件 (反盲标) 不应再产出'
        da = pd.read_excel(ba, sheet_name='验证数据')
        db = pd.read_excel(bb, sheet_name='验证数据')
        recon = pd.read_excel(rp, sheet_name='验证数据')
        bad = [c for c in da.columns if FORBIDDEN.search(str(c))]
        assert not bad, f'09 盲表泄露机器/抽样列: {bad}'
        pd.testing.assert_frame_equal(da, db)  # 双副本同内容同行序
        assert da['_row_uid'].is_unique
        assert set(recon['_row_uid']) == set(da['_row_uid']) and len(recon) == len(da)
        for c in ('样本类型', 'population_weight', '词典_x', 'BERT_y', '多数投票标签'):
            assert c in recon.columns, f'对账表缺 {c}'
        w = pd.to_numeric(recon['population_weight'], errors='coerce')
        assert w.notna().all() and (w > 0).all()

    def test_guide_has_no_sampling_leak_and_overview_has_population(
            self, tmp_path, silent_logger):
        _, ba, _, rp = self._generate(tmp_path, silent_logger)
        guide = pd.read_excel(ba, sheet_name='编码指南')
        assert '样本来源说明' not in guide['项目'].values, '一致/分歧抽样设计对编码员泄密'
        assert '独立性' in guide['项目'].values
        ov = pd.read_excel(rp, sheet_name='统计概览').set_index('统计项')
        for k in ('总体有效行数', '总体一致数', '总体分歧数', '总体预测负面数'):
            assert k in ov.index, f'统计概览缺总体层计数 {k} (层权不可恢复)'


# ============================================================================
# 3. 09 盲标回读 — 双编码共识 κ/α + 加权指标 + 无行爆炸
# ============================================================================

def _write_blind_trio(tmp_path, n=30, disagree_rows=(0, 1)):
    base = str(tmp_path / '09_sentiment_verify_full.xlsx')
    b, e = os.path.splitext(base)
    labels = ['正面', '中性', '负面']
    gold = [labels[i % 3] for i in range(n)]
    ctx = {'_row_uid': list(range(n)),
           'docid': [i // 2 for i in range(n)],  # 重复 docid — 回归锁: join 不得按 docid
           '标题': [f't{i}' for i in range(n)], '内容': ['c'] * n}
    a_vals = list(gold)
    b_vals = list(gold)
    for r in disagree_rows:
        b_vals[r] = labels[(labels.index(b_vals[r]) + 1) % 3]
    pd.DataFrame({**ctx, '人工判定_情感': a_vals, '人工判定_理由': [''] * n}).to_excel(
        f'{b}_blind_A{e}', sheet_name='验证数据', index=False)
    pd.DataFrame({**ctx, '人工判定_情感': b_vals, '人工判定_理由': [''] * n}).to_excel(
        f'{b}_blind_B{e}', sheet_name='验证数据', index=False)
    recon = pd.DataFrame({
        '_row_uid': list(range(n)),
        '样本类型': ['一致' if i % 2 == 0 else '分歧' for i in range(n)],
        'population_weight': [1.5 if i % 2 == 0 else 0.5 for i in range(n)],
        '词典_jiang_2021': gold, 'BERT_finbert_cn': gold,
        'LLM_llm': gold, '多数投票标签': gold,
    })
    with pd.ExcelWriter(f'{b}_reconciliation{e}', engine='openpyxl') as w:
        recon.to_excel(w, sheet_name='验证数据', index=False)
        pd.DataFrame({'统计项': ['生成时间'], '值': ['2026-07-03 00:00:00']}).to_excel(
            w, sheet_name='统计概览', index=False)
    return base


class TestBlind09Readback:
    def test_consensus_icr_and_weighted_keys(self, tmp_path, silent_logger):
        base = _write_blind_trio(tmp_path, n=30, disagree_rows=(0, 1))
        res = evaluate_human_verification(base, '_full', str(tmp_path), silent_logger)
        assert res['gold_source'] == 'two_coder_consensus_blind'
        icr = res['inter_coder']
        assert icr['n_both_valid'] == 30
        assert icr['n_disagree'] == 2
        assert icr['cohen_kappa'] is not None, 'G-3: 09 双编码 κ 必须出键'
        assert icr['krippendorff_alpha'] is not None, 'G-3: 09 双编码 α 必须出键'
        # 分歧 2 行不进评估域 → 28 条共识; 方法列=gold → 全对
        assert res['n_annotated'] == 28, '重复 docid 下不得 join 行爆炸/丢行'
        m = res['metrics']['词典_jiang_2021']
        assert m['accuracy'] == 1.0
        assert m['accuracy_weighted_corpus'] == 1.0, 'G-3: Manski-Lerman 加权口径必须出键'
        assert m['kappa_weighted_corpus'] is not None
        assert res['workbook_generated_at'] == '2026-07-03 00:00:00'

    def test_row_uid_mismatch_fails_loud(self, tmp_path, silent_logger):
        base = _write_blind_trio(tmp_path, n=10, disagree_rows=())
        b, e = os.path.splitext(base)
        db = pd.read_excel(f'{b}_blind_B{e}', sheet_name='验证数据')
        db = db.iloc[:-1]  # B 侧删一行 → 键漂移
        db.to_excel(f'{b}_blind_B{e}', sheet_name='验证数据', index=False)
        res = evaluate_human_verification(base, '_full', str(tmp_path), silent_logger)
        # 盲标三文件在但键不一致 → 不得静默用错配数据; 回退 legacy 又无单文件 → pending
        assert res['status'] in ('pending', 'error')
        assert res.get('gold_source') != 'two_coder_consensus_blind'

    def test_count_human_annotations_covers_blind_copies(self, tmp_path):
        base = _write_blind_trio(tmp_path, n=10, disagree_rows=())
        assert count_human_annotations(base) == 20  # A 10 + B 10 (防覆盖守卫盖住双盲表)
