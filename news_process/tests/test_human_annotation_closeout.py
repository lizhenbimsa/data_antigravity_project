"""人工标注回收收口 (2026-10-10..12) 回归锁。

覆盖本轮新增/改动、此前零测试的代码路径 (全部 tmp_path 隔离, 不碰盘上冻结表):
  1. manual_validation_schema: needs_adjudication / adjudicated_gold 真值表;
  2. tone_validation: 三轨窗口情感仲裁表生成 + 盲标共识读入 C 裁决 + 已填 C 拒绝覆盖;
  3. stage13_reject_audit_sampling: adjudicate 子命令 + readback 剔除/仲裁双口径 + 防覆写守卫;
  4. manual_validation_sampling: 每人一份盲表零机器列 (无 stratum/population_weight) +
     merge 并入 C_ 列 + adjudicate 只列两人打平的维度;
  5. llms_human.main: 盲表已有人工标注 → 跳过重生正常返回 (不 SystemExit, 不写对账表);
  6. human_annotation_ci: κ / PABAK / 加权召回率 / 多数票 原语;
  7. verify_human_annotation_frozen: 原件/副本 sha256 校验与 override。
"""
import hashlib
import logging

import numpy as np
import pandas as pd
import pytest

from news_process.validation.manual_validation_schema import (
    ADJUDICATION_COLUMNS,
    R_COLUMNS_BY_RATER,
    adjudicated_gold,
    needs_adjudication,
)

LOG = logging.getLogger('test_human_annotation_closeout')


# ---------------------------------------------------------------- 1. schema
class TestAdjudicatedGold:
    cols = R_COLUMNS_BY_RATER['locus']
    adj = ADJUDICATION_COLUMNS['locus']

    def _row(self, r1, r2, r3, c=None):
        return pd.Series(dict(zip(self.cols, (r1, r2, r3)), **{self.adj: c}))

    def test_majority_wins_and_c_ignored(self):
        row = self._row('technology', 'technology', 'application', c='application')
        assert not needs_adjudication(row, self.cols)
        assert adjudicated_gold(row, self.cols, self.adj) == '底层技术'

    def test_two_coded_split_takes_c(self):
        row = self._row('technology', 'application', None, c='application')
        assert needs_adjudication(row, self.cols)
        assert adjudicated_gold(row, self.cols, self.adj) == '应用场景'

    def test_two_coded_split_without_c_is_none(self):
        row = self._row('technology', 'application', None)
        assert adjudicated_gold(row, self.cols, self.adj) is None

    def test_single_coder_not_adjudicated(self):
        """只有一人编码 (另两人判不相关) → 不仲裁, C 有值也不采用。"""
        row = self._row('technology', None, None, c='technology')
        assert not needs_adjudication(row, self.cols)
        assert adjudicated_gold(row, self.cols, self.adj) is None

    def test_missing_c_column_equals_majority(self):
        row = pd.Series(dict(zip(self.cols, ('symbolic', None, 'symbolic'))))
        assert adjudicated_gold(row, R_COLUMNS_BY_RATER['substantiveness'],
                                ADJUDICATION_COLUMNS['substantiveness']) is None  # 列名不匹配 → 无票


# ---------------------------------------------------------------- 2. tone_validation 三轨仲裁
@pytest.fixture
def window_blind(tmp_path):
    base = tmp_path / '09_sentiment_verify_full'
    uid = list(range(6))
    ctx = {'_row_uid': uid, 'docid': [str(i) for i in uid], '标题': ['t'] * 6,
           '内容': ['c'] * 6, '机器输入文本': ['m'] * 6, 'target_bank': ['b'] * 6}
    a = ['正面', '正面', '中性', '负面', '正面', '中性']
    b = ['正面', '中性', '中性', '正面', '正面', '负面']
    pd.DataFrame({'人工判定_情感': a, '人工判定_理由': ['r'] * 6, **ctx}).to_excel(
        f'{base}_blind_A.xlsx', sheet_name='验证数据', index=False)
    pd.DataFrame({'人工判定_情感': b, '人工判定_理由': ['r'] * 6, **ctx}).to_excel(
        f'{base}_blind_B.xlsx', sheet_name='验证数据', index=False)
    pd.DataFrame({'_row_uid': uid, 'docid': [str(i) for i in uid], 'LLM_投票': ['正面'] * 6}).to_excel(
        f'{base}_reconciliation.xlsx', sheet_name='验证数据', index=False)
    return str(base) + '.xlsx'


class TestWindowAdjudication:
    def test_generate_lists_only_disagreements_without_machine_cols(self, window_blind):
        from news_process.validation import tone_validation as tv
        assert tv.generate_adjudication_workbook(window_blind) == 3
        pend = pd.read_excel(window_blind.replace('.xlsx', '_pending_adjudication.xlsx'))
        assert set(pend['_row_uid']) == {1, 3, 5}
        assert {'编码者A_情感', '编码者B_情感', '编码者C_情感', '编码者C_理由'} <= set(pend.columns)
        assert not [c for c in pend.columns if c.startswith(('LLM_', '词典_', 'BERT_'))]

    def test_consensus_reads_c_and_strict_unchanged_without_c(self, window_blind):
        from news_process.validation import tone_validation as tv
        df, icr, _ = tv._load_blind_consensus(window_blind, LOG)
        assert icr['n_adjudicated'] == 0 and int((df['人工判定_情感'] != '').sum()) == 3
        tv.generate_adjudication_workbook(window_blind)
        p = window_blind.replace('.xlsx', '_pending_adjudication.xlsx')
        pend = pd.read_excel(p)
        pend['编码者C_情感'] = ['中性', '负面', '负面']
        pend.to_excel(p, sheet_name='验证数据', index=False)
        df, icr, _ = tv._load_blind_consensus(window_blind, LOG)
        gold = df.set_index('_row_uid')['人工判定_情感']
        assert icr['n_adjudicated'] == 3 and icr['n_agree'] == 3
        assert gold[1] == '中性' and gold[3] == '负面' and gold[0] == '正面'

    def test_refuses_to_overwrite_filled_c(self, window_blind):
        from news_process.validation import tone_validation as tv
        tv.generate_adjudication_workbook(window_blind)
        p = window_blind.replace('.xlsx', '_pending_adjudication.xlsx')
        pend = pd.read_excel(p)
        pend['编码者C_情感'] = pend['编码者C_情感'].astype(object)
        pend.loc[0, '编码者C_情感'] = '正面'
        pend.to_excel(p, sheet_name='验证数据', index=False)
        with pytest.raises(SystemExit):
            tv.generate_adjudication_workbook(window_blind)


# ---------------------------------------------------------------- 3. stage13 漏检审计
@pytest.fixture
def s13(tmp_path, monkeypatch):
    from news_process.scripts.migrate import stage13_reject_audit_sampling as m
    for name in ('BLIND_A', 'BLIND_B', 'RECON', 'PENDING', 'RESULT_CSV'):
        monkeypatch.setattr(m, name, tmp_path / getattr(m, name).name)
    uid = list(range(10))
    ctx = {'_row_uid': uid, 'docid': [str(i) for i in uid], '日期': ['2020-01-01'] * 10,
           '媒体类型(中文)': ['报纸'] * 10, '标题': ['t'] * 10, '内容': ['c'] * 10, 'target_bank': ['b'] * 10}
    a = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    b = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    pd.DataFrame({'编码者A_验证': a, **ctx}).to_excel(m.BLIND_A, sheet_name='验证数据', index=False)
    pd.DataFrame({'编码者B_验证': b, **ctx}).to_excel(m.BLIND_B, sheet_name='验证数据', index=False)
    pd.DataFrame({**ctx, 'population_weight': [1.0] * 10}).to_excel(m.RECON, sheet_name='验证数据', index=False)
    return m


class TestStage13:
    def test_adjudicate_then_readback_both_caliber(self, s13):
        s13.adjudicate()
        pend = pd.read_excel(s13.PENDING, sheet_name='验证数据')
        assert set(pend['_row_uid']) == {1, 2}
        assert not [c for c in pend.columns if c in ('population_weight', '_stratum')]
        s13.readback()
        res = pd.read_csv(s13.RESULT_CSV)
        assert list(res['指标']) == ['stage13_假阴性率_剔除口径']
        assert res.loc[0, '点估_未加权'] == pytest.approx(1 / 8)
        pend['编码者C_验证'] = [1, 0]
        pend.to_excel(s13.PENDING, sheet_name='验证数据', index=False)
        s13.readback()
        res = pd.read_csv(s13.RESULT_CSV).set_index('指标')
        assert res.loc['stage13_假阴性率_仲裁口径', '点估_未加权'] == pytest.approx(2 / 10)
        assert res.loc['stage13_假阴性率_剔除口径', '点估_未加权'] == pytest.approx(1 / 8)

    def test_sample_refuses_when_annotated(self, s13):
        with pytest.raises(SystemExit):
            s13.sample()


# ---------------------------------------------------------------- 4. 创新三维盲表 / 装配 / 仲裁
@pytest.fixture
def mvs(tmp_path, monkeypatch):
    from news_process.scripts.migrate import manual_validation_sampling as m
    out = tmp_path / 'manual_validation_samples.xlsx'
    monkeypatch.setattr(m, 'OUTPUT_XLSX', out)
    monkeypatch.setattr(m, 'RECONCILIATION_XLSX', tmp_path / 'manual_validation_reconciliation.xlsx')
    monkeypatch.setattr(m, 'BLIND_XLSX', {r: tmp_path / f'manual_validation_samples_blind_{r}.xlsx'
                                          for r in m.RATERS})
    monkeypatch.setattr(m, 'ADJ_XLSX', tmp_path / 'manual_validation_pending_adjudication.xlsx')
    base = pd.DataFrame({'orig_index': [10, 11, 12], 'docid': ['a', 'b', 'c'], 'target_bank': ['x'] * 3,
                         '标题': ['t'] * 3, '内容': ['c'] * 3})
    vals = {'R1': ['technology', 'technology', 'application'],
            'R2': ['application', 'technology', None],
            'R3': [None, 'application', None]}
    for r in m.RATERS:
        df = base.copy()
        df[f'{r}_stage3b_locus'] = vals[r]
        df[f'{r}_stage3a_substantiveness'] = None
        df[f'{r}_stage3c_collab'] = None
        m._write_rater_blind(df, r, m.BLIND_XLSX[r])
    pd.DataFrame({'orig_index': [10, 11, 12], 'stratum': ['B', 'C', 'A'],
                  'population_weight': [1.0, 2.0, 3.0]}).to_excel(m.RECONCILIATION_XLSX, index=False)
    return m


class TestInnovationWorkbooks:
    def test_rater_blind_has_no_machine_or_stratum(self, mvs):
        for r in mvs.RATERS:
            cols = pd.read_excel(mvs.BLIND_XLSX[r], sheet_name='验证数据').columns
            assert 'stratum' not in cols and 'population_weight' not in cols
            assert not [c for c in cols if c[:3] in {'R1_', 'R2_', 'R3_'} - {f'{r}_'}]

    def test_merge_then_adjudicate_then_merge_joins_c(self, mvs):
        mvs.merge()
        mv = pd.read_excel(mvs.OUTPUT_XLSX)
        assert {'stratum', 'population_weight', 'R3_stage3b_locus'} <= set(mv.columns)
        mvs.adjudicate()
        adj = pd.read_excel(mvs.ADJ_XLSX, sheet_name='验证数据')
        assert list(adj['orig_index']) == [10]  # 11 有多数票, 12 只一人编码
        assert adj.loc[0, '需裁_locus'] == '是'
        adj['C_stage3b_locus'] = ['application']
        adj.to_excel(mvs.ADJ_XLSX, sheet_name='验证数据', index=False)
        mvs.merge()
        mv = pd.read_excel(mvs.OUTPUT_XLSX).set_index('orig_index')
        assert mv.loc[10, 'C_stage3b_locus'] == 'application'
        g = adjudicated_gold(mv.loc[10], R_COLUMNS_BY_RATER['locus'], ADJUDICATION_COLUMNS['locus'])
        assert g == '应用场景'
        with pytest.raises(SystemExit):
            mvs.adjudicate()  # 已填 C → 拒绝覆盖


# ---------------------------------------------------------------- 5. stage 61 跳过重生
def test_stage61_skips_regeneration_when_annotated(tmp_path, monkeypatch):
    from news_process.validation import llms_human
    cfg = dict(llms_human.CONFIG)
    cfg['paths'] = {**llms_human.CONFIG['paths'], 'output_dir': str(tmp_path)}
    monkeypatch.setattr(llms_human, 'CONFIG', cfg)
    paths = llms_human.derive_blind_paths(str(tmp_path / '61_human_samples.xlsx'))
    for coder in ('A', 'B'):
        pd.DataFrame({'_row_uid': [0], f'编码者{coder}_验证': [1], f'编码者{coder}_情感': ['正面']}).to_excel(
            paths[f'blind_{coder}'], sheet_name='验证数据', index=False)
    before = {c: hashlib.sha256(open(paths[f'blind_{c}'], 'rb').read()).hexdigest() for c in 'AB'}
    assert llms_human.main() is None  # 不 SystemExit; 无抽样源 parquet 也不会走到 sys.exit(1)
    after = {c: hashlib.sha256(open(paths[f'blind_{c}'], 'rb').read()).hexdigest() for c in 'AB'}
    assert before == after
    assert not (tmp_path / '61_human_samples_reconciliation.xlsx').exists()


# ---------------------------------------------------------------- 6. CI 原语
class TestCIPrimitives:
    def test_kappa_pabak_recall_majority(self):
        from news_process.validation import human_annotation_ci as ci
        x = np.array([0, 0, 1, 1, 1, 1])
        y = np.array([0, 1, 1, 1, 1, 0])
        assert ci._acc(x, y, 2) == pytest.approx(4 / 6)
        assert ci._pabak(x, y, 2) == pytest.approx(2 * 4 / 6 - 1)
        po, pe = 4 / 6, (2 / 6) * (2 / 6) + (4 / 6) * (4 / 6)
        assert ci._kappa(x, y, 2) == pytest.approx((po - pe) / (1 - pe))
        w = np.array([1, 1, 1, 1, 1, 9.0])
        assert ci._recall(x, y, 2) == pytest.approx(3 / 4)
        assert ci._recall(x, y, 2, w) == pytest.approx(3 / 12)
        assert ci._miss(x, y, 2, w) == pytest.approx(9 / 12)
        assert ci._majority(['yes', 'yes', 'no']) == 'yes'
        assert ci._majority(['yes', None, 'no']) is None
        assert ci._majority(['yes', None, None]) is None

    def test_stratified_resample_keeps_stratum_sizes(self):
        from news_process.validation import human_annotation_ci as ci
        s = np.array(['A'] * 3 + ['B'] * 5)
        idx = ci._resample_idx(8, s, 20, np.random.default_rng(0))
        assert all((s[i] == 'A').sum() == 3 for i in idx)


# ---------------------------------------------------------------- 7. 冻结校验
def test_verify_frozen_detects_tamper(tmp_path, monkeypatch):
    from news_process.core import config as core_config
    from news_process.scripts.audit import verify_human_annotation_frozen as v
    (tmp_path / 'human_samples_blind' / 'T').mkdir(parents=True)
    (tmp_path / 'a.xlsx').write_bytes(b'orig')
    (tmp_path / 'human_samples_blind' / 'T' / 'a.xlsx').write_bytes(b'copy-edited')
    sha = lambda b: hashlib.sha256(b).hexdigest()  # noqa: E731
    frozen = {'files': {'a.xlsx': sha(b'orig')}, 'archive_dir': 'human_samples_blind',
              'archive_sha256_overrides': {'T/a.xlsx': sha(b'copy-edited')}}
    monkeypatch.setattr(core_config, 'load_config', lambda: {'human_annotation_frozen': frozen})
    assert v.verify(tmp_path) == 0
    (tmp_path / 'a.xlsx').write_bytes(b'tampered')
    assert v.verify(tmp_path) == 1


def test_gwet_ac1_matches_hand_formula():
    from news_process.validation import human_annotation_ci as ci
    x = np.array([0, 0, 1, 1, 1, 1])
    y = np.array([0, 1, 1, 1, 1, 0])
    pi1 = (4 + 4) / 12
    pe = 2 * pi1 * (1 - pi1)
    assert ci._ac1(x, y, 2) == pytest.approx((4 / 6 - pe) / (1 - pe))
