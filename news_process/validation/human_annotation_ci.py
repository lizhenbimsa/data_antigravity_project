"""人工验证指标的 bootstrap 置信区间 (κ / α / PABAK / accuracy / macro-F1 / 召回率)。

stage 63/64 只给 accuracy 附 Wilson CI; 编码者间信度 (Cohen κ / Krippendorff α) 与
人机比对的 macro-F1、κ 均无区间 (MEASUREMENT_VALIDATION_AUDIT_TOPTIER_2026-06-13 §5.4 DEFER)。
人机比对另报 Gwet AC1 (Gwet 2008) 与 PABAK。本模块对 4 个人工任务做非参数 bootstrap: 按条目 (文章) 有放回重抽 B 次, 取百分位区间;
带抽样权重的口径按抽样层分层重抽。

输出三类行 (列 `类别`):
  - 编码者间信度: 原始一致率 / Cohen κ (或 Krippendorff α) / PABAK。情感类标签约八成为
    正面, κ 受基率压低 (Feinstein & Cicchetti 1990 "high agreement but low kappa"),
    故并报原始一致率与患病率调整的 PABAK (Byrt, Bishop & Carlin 1993)。
  - 人机比对: accuracy / macro-F1 / Cohen κ; 同一比对按金标准口径并排 (仲裁口径 vs
    剔除口径或纯多数票口径), 带抽样权重时另报总体加权 accuracy (Manski & Lerman 1977)。
  - LLM 留篇召回: 任务四三位编码员的「是否相关」判断 (此前无消费代码) 作金标准,
    估计 LLM 留篇判断的总体加权召回率 / 漏判率 / 精确率; 另以纯随机层 F 单独估计作核对。

只读: 读冻结人工表 + 对账表 + 合并表 + 21 号预测, 只写一个 CSV
(eval_reports/human_annotation_bootstrap_ci.csv); 不进 DAG、不进面板, golden 无关, $0。
点估口径与 stage 63/64 一致 (同一评估域、同一金标准), 区间是新增信息。

用法 (repo 根): python -m news_process.validation.human_annotation_ci [--n-boot 2000]

白话: 一致性系数只算一个数不够, 还要知道它有多稳 —— 把样本反复重抽两千次,
看这个数在什么范围内晃动, 就得到 95% 置信区间。
"""
import argparse
import hashlib
import os
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')
_PROJECT_PARENT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.validation.llms_evaluation import compute_krippendorffs_alpha  # noqa: E402
from news_process.validation.manual_validation_schema import (  # noqa: E402
    ADJUDICATION_COLUMNS,
    R_COLUMNS_BY_RATER,
    adjudicated_gold,
    merge_three_rater_majority,
)

SEED = 42
SENT = ['正面', '中性', '负面']
TRACKS = ('_full', '_ctx', '_ss')
_EN_SENT = {'positive': '正面', 'neutral': '中性', 'negative': '负面'}


# ---------------------------------------------------------------- 统计量 (x=金标准/编码者1, y=预测/编码者2)
def _codes(a, b, labels, w=None, strata=None):
    m = {lab: i for i, lab in enumerate(labels)}
    x = pd.Series(a).reset_index(drop=True).map(m).to_numpy(dtype=float)
    y = pd.Series(b).reset_index(drop=True).map(m).to_numpy(dtype=float)
    ok = ~np.isnan(x) & ~np.isnan(y)
    w = None if w is None else np.asarray(w, dtype=float)[ok]
    s = None if strata is None else np.asarray(strata)[ok]
    return x[ok].astype(int), y[ok].astype(int), len(labels), w, s


def _kappa(x, y, k, w=None):
    n = len(x)
    if n == 0:
        return np.nan
    cm = np.bincount(x * k + y, minlength=k * k).reshape(k, k)
    po = np.trace(cm) / n
    pe = (cm.sum(1) * cm.sum(0)).sum() / n ** 2
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def _acc(x, y, k, w=None):
    if not len(x):
        return np.nan
    return float(np.mean(x == y)) if w is None else float(np.sum(w * (x == y)) / np.sum(w))


def _pabak(x, y, k, w=None):
    """患病率与偏差调整 κ: PABAK = (k·p_o − 1)/(k − 1) (Byrt, Bishop & Carlin 1993)。"""
    po = _acc(x, y, k)
    return (k * po - 1) / (k - 1) if po == po else np.nan


def _ac1(x, y, k, w=None):
    """Gwet AC1 (两评分者): p_e = Σ_c π_c(1−π_c)/(k−1), π_c = 两方边际均值 (Gwet 2008)。"""
    n = len(x)
    if n == 0:
        return np.nan
    po = np.mean(x == y)
    pi = (np.bincount(x, minlength=k) + np.bincount(y, minlength=k)) / (2 * n)
    pe = float(np.sum(pi * (1 - pi)) / (k - 1))
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def _macro_f1(gold, pred, k, w=None):
    # 与 sklearn precision_recall_fscore_support(average='macro', labels=全集, zero_division=0) 一致
    f1s = []
    for c in range(k):
        tp = np.sum((pred == c) & (gold == c))
        fp = np.sum((pred == c) & (gold != c))
        fn = np.sum((pred != c) & (gold == c))
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1s.append(2 * p * r / (p + r) if p + r else 0.0)
    return float(np.mean(f1s))


def _recall(gold, pred, k, w=None):
    """正类 (编码 1) 召回率: 人判相关的文章中 LLM 也判相关的 (加权) 比例。"""
    w = np.ones(len(gold)) if w is None else w
    den = np.sum(w * (gold == 1))
    return float(np.sum(w * (gold == 1) * (pred == 1)) / den) if den else np.nan


def _miss(gold, pred, k, w=None):
    r = _recall(gold, pred, k, w)
    return 1 - r if r == r else np.nan


def _precision(gold, pred, k, w=None):
    w = np.ones(len(gold)) if w is None else w
    den = np.sum(w * (pred == 1))
    return float(np.sum(w * (gold == 1) * (pred == 1)) / den) if den else np.nan


def _resample_idx(n, strata, n_boot, rng):
    if strata is None:
        return rng.integers(0, n, size=(n_boot, n))
    groups = [np.flatnonzero(strata == s) for s in pd.unique(strata)]
    return np.array([np.concatenate([g[rng.integers(0, len(g), len(g))] for g in groups])
                     for _ in range(n_boot)])


def _boot_pair(x, y, k, stat, n_boot, rng, w=None, strata=None):
    n = len(x)
    point = stat(x, y, k, w)
    if n < 2:
        return point, np.nan, np.nan, n
    idx = _resample_idx(n, strata, n_boot, rng)
    vals = np.array([stat(x[i], y[i], k, None if w is None else w[i]) for i in idx])
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return point, lo, hi, n


def _alpha(M):
    a = compute_krippendorffs_alpha(M)
    return a['alpha'] if isinstance(a, dict) else a


def _pairwise_agreement(M):
    """多编码者平均两两原始一致率 (只计双方都有编码的条目)。"""
    rates = []
    for i in range(M.shape[0]):
        for j in range(i + 1, M.shape[0]):
            ok = (M[i] >= 0) & (M[j] >= 0)
            if ok.any():
                rates.append(np.mean(M[i, ok] == M[j, ok]))
    return float(np.mean(rates)) if rates else np.nan


def _boot_matrix(M, stat, n_boot, rng):
    """M: (n_coders, n_items), -1 = 缺失。按条目重抽。"""
    n = M.shape[1]
    point = stat(M)
    idx = rng.integers(0, n, size=(n_boot, n))
    vals = np.array([stat(M[:, i]) for i in idx])
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    n_pair = int(((M >= 0).sum(0) >= 2).sum())
    return point, lo, hi, n_pair


def _majority(values):
    """≥2 票一致的多数标签, 否则 None。"""
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None
    top, cnt = Counter(vals).most_common(1)[0]
    return top if cnt >= 2 else None


def _clean_lower(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    s = str(v).strip().lower()
    return s or None


# ---------------------------------------------------------------- 主流程
def run(n_boot: int = 2000) -> pd.DataFrame:
    cfg = load_config()
    P = cfg['paths']['output_dir']
    E = os.path.join(P, 'eval_reports')
    rows = []

    def rng_for(*key):
        # 每项 (任务, 对象, 指标, 口径) 独立固定种子: 新增/删减指标不改变其他行的区间 (可复现)
        h = int(hashlib.sha256('|'.join(map(str, key)).encode('utf-8')).hexdigest()[:8], 16)
        return np.random.default_rng([SEED, h])

    def add(task, kind, item, metric, res, gold_note):
        point, lo, hi, n = res
        rows.append({'任务': task, '类别': kind, '对象': item, '指标': metric,
                     '点估': round(float(point), 6) if point == point else np.nan,
                     'CI95_下': round(float(lo), 6) if lo == lo else np.nan,
                     'CI95_上': round(float(hi), 6) if hi == hi else np.nan,
                     'n': n, '金标准口径': gold_note})

    def coder_metrics(task, item, a, b, labels):
        x, y, k, _, _ = _codes(a, b, labels)
        for name, f in (('原始一致率', _acc), ('Cohen_κ', _kappa), ('PABAK', _pabak)):
            add(task, '编码者间信度', item, name, _boot_pair(x, y, k, f, n_boot, rng_for(task, item, name)), '—')

    def pair_metrics(task, item, gold, pred, labels, note, w=None, strata=None):
        g, p, k, ww, ss = _codes(gold, pred, labels, w, strata)
        for name, f in (('accuracy', _acc), ('macro_F1', _macro_f1), ('Cohen_κ', _kappa),
                        ('Gwet_AC1', _ac1), ('PABAK', _pabak)):
            add(task, '人机比对', item, name, _boot_pair(g, p, k, f, n_boot, rng_for(task, item, name, note)), note)
        if ww is not None:
            add(task, '人机比对', item, 'accuracy_总体加权',
                _boot_pair(g, p, k, _acc, n_boot, rng_for(task, item, 'accuracy_总体加权', note), ww, ss), note)

    def rd(p):
        return pd.read_excel(p, sheet_name='验证数据')

    # ---- 任务一: 验证 + 全文情感 (A/B 双编码; 金标准并排: 仲裁口径 最终_* / 剔除口径 最终_*_strict)
    a, b = rd(os.path.join(P, '61_human_samples_blind_A.xlsx')), rd(os.path.join(P, '61_human_samples_blind_B.xlsx'))
    b = b.set_index('_row_uid').reindex(a['_row_uid']).reset_index()
    for col, labels in (('验证', [0, 1]), ('情感', SENT)):
        coder_metrics('任务一', f'{col} A-B', a[f'编码者A_{col}'], b[f'编码者B_{col}'], labels)
    m = pd.read_excel(os.path.join(P, '61_human_samples_merged.xlsx'))
    rc = rd(os.path.join(P, '61_human_samples_reconciliation.xlsx'))
    j = m[['_row_uid', '最终_验证', '最终_情感', '最终_验证_strict', '最终_情感_strict']].merge(
        rc, on='_row_uid', how='left')
    for suffix, note in (('', '仲裁口径'), ('_strict', '剔除口径')):
        gv = pd.to_numeric(j[f'最终_验证{suffix}'], errors='coerce').where(lambda s: s.isin([0, 1]))
        gs = j[f'最终_情感{suffix}'].where(j[f'最终_情感{suffix}'].isin(SENT))
        for t in TRACKS:
            ver = j[f'llm_verified{t}'].map({True: 1, False: 0, 'True': 1, 'False': 0})
            pair_metrics('任务一', f'LLM 验证 ({t})', gv, ver, [0, 1], note)
            pair_metrics('任务一', f'LLM 情感 ({t})', gs, j[f'llm_sentiment{t}'], SENT, note)

    # ---- 任务二: 三轨窗口情感 (A/B 共识; 金标准并排: 共识 + C 仲裁 / 共识剔除分歧)
    for t in TRACKS:
        base = os.path.join(E, f'09_sentiment_verify{t}')
        x_a, x_b = rd(base + '_blind_A.xlsx'), rd(base + '_blind_B.xlsx').set_index('_row_uid')
        x_b = x_b.reindex(x_a['_row_uid']).reset_index()
        coder_metrics('任务二', f'情感 A-B ({t})', x_a['人工判定_情感'], x_b['人工判定_情感'], SENT)
        rc2 = rd(base + '_reconciliation.xlsx')
        strict = x_a['人工判定_情感'].where(x_a['人工判定_情感'] == x_b['人工判定_情感'])
        golds = {'剔除口径 (分歧剔除)': strict}
        if os.path.isfile(base + '_pending_adjudication.xlsx'):  # 与 stage 64 同口径补入 C 裁决
            adj = rd(base + '_pending_adjudication.xlsx').set_index('_row_uid')['编码者C_情感']
            c_val = adj.reindex(x_a['_row_uid']).to_numpy()
            fill = strict.isna().to_numpy() & pd.Series(c_val).isin(SENT).to_numpy()
            if fill.any():
                golds = {'共识 + C 仲裁': strict.where(~fill, c_val), **golds}
        meth = [c for c in rc2.columns if c.startswith(('词典_', 'BERT_', 'LLM_')) or c == '多数投票标签']
        for note, gold in golds.items():
            jj = pd.DataFrame({'_row_uid': x_a['_row_uid'], 'gold': gold}).merge(rc2, on='_row_uid', how='left')
            w = jj.get('population_weight')
            st = jj.get('样本类型')
            for c in meth:
                pair_metrics('任务二', f'{c} ({t})', jj['gold'], jj[c], SENT, note, w, st)

    # ---- 任务三: 过滤器漏检 (A/B)
    a3, b3 = rd(os.path.join(E, 'stage13_reject_audit_blind_A.xlsx')), rd(os.path.join(E, 'stage13_reject_audit_blind_B.xlsx'))
    b3 = b3.set_index('_row_uid').reindex(a3['_row_uid']).reset_index()
    coder_metrics('任务三', '是否误拒 A-B', a3['编码者A_验证'], b3['编码者B_验证'], [0, 1])

    # ---- 任务四: 创新三维 (R1/R2/R3; α 按条目重抽)
    mv = pd.read_excel(os.path.join(P, 'manual_validation_samples.xlsx'))
    raters = ('R1', 'R2', 'R3')
    dims = {'stage1_relevant': ['no', 'yes'], 'stage2_sentiment': ['negative', 'neutral', 'positive'],
            'stage3a_substantiveness': ['symbolic', 'substantive'],
            'stage3b_locus': ['technology', 'application'],
            'stage3c_collab': ['self_developed', 'collaborative']}
    for d, labels in dims.items():
        M = np.array([[labels.index(v) if (v := _clean_lower(x)) in labels else -1
                       for x in mv[f'{r}_{d}']] for r in raters])
        add('任务四', '编码者间信度', d, 'Krippendorff_α', _boot_matrix(M, _alpha, n_boot, rng_for('任务四', d, 'α')), '—')
        add('任务四', '编码者间信度', d, '两两原始一致率', _boot_matrix(M, _pairwise_agreement, n_boot, rng_for('任务四', d, '两两')), '—')

    mv['docid'] = mv['docid'].astype(str)
    pcols = ([f'innovation_{d}{t}' for d in ('substantiveness', 'locus', 'collab_mode') for t in TRACKS]
             + [f'llm_verified{t}' for t in TRACKS] + [f'llm_sentiment{t}' for t in TRACKS])
    pred = pd.read_parquet(os.path.join(P, '21_tone_llms_full.parquet'), columns=['docid', 'target_bank'] + pcols)
    pred['docid'] = pred['docid'].astype(str)
    pred = pred.drop_duplicates(['docid', 'target_bank'])
    mvj = mv.drop_duplicates(['docid', 'target_bank']).merge(pred, on=['docid', 'target_bank'], how='left')
    w4 = pd.to_numeric(mvj['population_weight'], errors='coerce')
    s4 = mvj['stratum'].astype(str)
    for dim, pcol, labels in (('substantiveness', 'innovation_substantiveness', ['实质性', '象征性']),
                              ('locus', 'innovation_locus', ['底层技术', '应用场景']),
                              ('collab', 'innovation_collab_mode', ['自主研发', '外部协同'])):
        golds = {'三人多数票': mvj.apply(lambda r, dim=dim: merge_three_rater_majority(
            r, R_COLUMNS_BY_RATER[dim]), axis=1)}
        if ADJUDICATION_COLUMNS[dim] in mvj:
            golds = {'三人多数票 + C 仲裁': mvj.apply(lambda r, dim=dim: adjudicated_gold(
                r, R_COLUMNS_BY_RATER[dim], ADJUDICATION_COLUMNS[dim]), axis=1), **golds}
        for note, gold in golds.items():
            for t in TRACKS:
                pair_metrics('任务四', f'LLM {dim} ({t})', gold, mvj[f'{pcol}{t}'], labels, note, w4, s4)

    # ---- 任务四 (此前未用的两列): 三人「是否相关」→ LLM 留篇召回; 三人「情感」→ LLM 情感
    rel = mvj.apply(lambda r: _majority([_clean_lower(r[f'{x}_stage1_relevant']) for x in raters]), axis=1)
    rel_gold = rel.map({'yes': 1, 'no': 0})
    note = '三人多数票 (分层抽样, 层权还原总体)'
    for t in TRACKS:
        ver = mvj[f'llm_verified{t}'].map({True: 1, False: 0, 'True': 1, 'False': 0})
        g, p, k, ww, ss = _codes(rel_gold, ver, [0, 1], w4, s4)
        for name, f in (('召回率_总体加权', _recall), ('漏判率_总体加权', _miss),
                        ('精确率_总体加权', _precision), ('accuracy_总体加权', _acc)):
            add('任务四', 'LLM 留篇召回', f'LLM 留篇 ({t})', name,
                _boot_pair(g, p, k, f, n_boot, rng_for('留篇', t, name), ww, ss), note)
        f_only = (s4 == 'F_pure_random').to_numpy()
        g, p, k, _, _ = _codes(rel_gold[f_only], ver[f_only], [0, 1])
        for name, f in (('召回率_纯随机层', _recall), ('accuracy_纯随机层', _acc)):
            add('任务四', 'LLM 留篇召回', f'LLM 留篇 ({t})', name,
                _boot_pair(g, p, k, f, n_boot, rng_for('留篇F', t, name)), '三人多数票 (仅纯随机层 F, 无需加权)')
    sen = mvj.apply(lambda r: _majority([_EN_SENT.get(_clean_lower(r[f'{x}_stage2_sentiment']))
                                         for x in raters]), axis=1)
    for t in TRACKS:
        pair_metrics('任务四', f'LLM 情感 ({t})', sen, mvj[f'llm_sentiment{t}'], SENT,
                     '三人多数票 (人机均判相关的文章)', w4, s4)

    out = pd.DataFrame(rows)
    out['bootstrap'] = (f'B={n_boot}, 百分位法, 种子=({SEED}, sha256(行键)), 按条目有放回重抽 '
                        '(总体加权口径按抽样层分层重抽)')
    out['生成时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
    path = os.path.join(E, 'human_annotation_bootstrap_ci.csv')
    out.to_csv(path, index=False, encoding='utf-8-sig')
    print(f'{len(out)} 行 → {path}')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-boot', type=int, default=2000)
    run(ap.parse_args().n_boot)
