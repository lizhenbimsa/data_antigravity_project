"""人工验证指标的 bootstrap 置信区间 (κ / α / accuracy / macro-F1)。

stage 63/64 只给 accuracy 附 Wilson CI; 编码者间信度 (Cohen κ / Krippendorff α) 与
人机比对的 macro-F1、κ 均无区间 (MEASUREMENT_VALIDATION_AUDIT_TOPTIER_2026-06-13 §5.4 DEFER)。
本模块对 4 个人工任务做非参数 bootstrap: 按条目 (文章) 有放回重抽 B 次, 取百分位区间。

只读: 读冻结人工表 + 对账表 + 合并表 + 21 号预测, 只写一个 CSV
(eval_reports/human_annotation_bootstrap_ci.csv); 不进 DAG、不进面板, golden 无关, $0。
点估口径与 stage 63/64 一致 (同一评估域、同一金标准), 区间是新增信息。

用法 (repo 根): python -m news_process.validation.human_annotation_ci [--n-boot 2000]

白话: 一致性系数只算一个数不够, 还要知道它有多稳 —— 把样本反复重抽两千次,
看这个数在什么范围内晃动, 就得到 95% 置信区间。
"""
import argparse
import os
import sys
import time

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
)

SEED = 42
SENT = ['正面', '中性', '负面']
TRACKS = ('_full', '_ctx', '_ss')


# ---------------------------------------------------------------- 统计量
def _codes(a, b, labels):
    m = {l: i for i, l in enumerate(labels)}
    x = pd.Series(a).map(m).to_numpy(dtype=float)
    y = pd.Series(b).map(m).to_numpy(dtype=float)
    ok = ~np.isnan(x) & ~np.isnan(y)
    return x[ok].astype(int), y[ok].astype(int), len(labels)


def _kappa(x, y, k):
    n = len(x)
    if n == 0:
        return np.nan
    cm = np.bincount(x * k + y, minlength=k * k).reshape(k, k)
    po = np.trace(cm) / n
    pe = (cm.sum(1) * cm.sum(0)).sum() / n ** 2
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def _acc(x, y, k):
    return np.mean(x == y) if len(x) else np.nan


def _macro_f1(gold, pred, k):
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


def _boot_pair(x, y, k, stat, n_boot, rng):
    n = len(x)
    point = stat(x, y, k)
    if n < 2:
        return point, np.nan, np.nan, n
    idx = rng.integers(0, n, size=(n_boot, n))
    vals = np.array([stat(x[i], y[i], k) for i in idx])
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    return point, lo, hi, n


def _alpha(M):
    a = compute_krippendorffs_alpha(M)
    return a['alpha'] if isinstance(a, dict) else a


def _boot_alpha(M, n_boot, rng):
    """M: (n_coders, n_items), -1 = 缺失。按条目重抽。"""
    n = M.shape[1]
    point = _alpha(M)
    idx = rng.integers(0, n, size=(n_boot, n))
    vals = np.array([_alpha(M[:, i]) for i in idx])
    lo, hi = np.nanpercentile(vals, [2.5, 97.5])
    n_pair = int(((M >= 0).sum(0) >= 2).sum())
    return point, lo, hi, n_pair


# ---------------------------------------------------------------- 主流程
def run(n_boot: int = 2000) -> pd.DataFrame:
    cfg = load_config()
    P = cfg['paths']['output_dir']
    E = os.path.join(P, 'eval_reports')
    rng = np.random.default_rng(SEED)
    rows = []

    def add(task, kind, item, metric, res, gold_note):
        point, lo, hi, n = res
        rows.append({'任务': task, '类别': kind, '对象': item, '指标': metric,
                     '点估': round(float(point), 4) if point == point else np.nan,
                     'CI95_下': round(float(lo), 4) if lo == lo else np.nan,
                     'CI95_上': round(float(hi), 4) if hi == hi else np.nan,
                     'n': n, '金标准口径': gold_note})

    def pair_metrics(task, item, gold, pred, labels, note):
        g, p, k = _codes(gold, pred, labels)
        for name, f in (('accuracy', _acc), ('macro_F1', _macro_f1), ('Cohen_κ', _kappa)):
            add(task, '人机比对', item, name, _boot_pair(g, p, k, f, n_boot, rng), note)

    def rd(p):
        return pd.read_excel(p, sheet_name='验证数据')

    # ---- 任务一: 验证 + 全文情感 (A/B 双编码; 金标准 = 仲裁后 最终_*)
    a, b = rd(os.path.join(P, '61_human_samples_blind_A.xlsx')), rd(os.path.join(P, '61_human_samples_blind_B.xlsx'))
    b = b.set_index('_row_uid').reindex(a['_row_uid']).reset_index()
    for col, labels in (('验证', [0, 1]), ('情感', SENT)):
        x, y, k = _codes(a[f'编码者A_{col}'], b[f'编码者B_{col}'], labels)
        add('任务一', '编码者间信度', f'{col} A-B', 'Cohen_κ', _boot_pair(x, y, k, _kappa, n_boot, rng), '—')
    m = pd.read_excel(os.path.join(P, '61_human_samples_merged.xlsx'))
    rc = rd(os.path.join(P, '61_human_samples_reconciliation.xlsx'))
    j = m[['_row_uid', '最终_验证', '最终_情感']].merge(rc, on='_row_uid', how='left')
    for t in TRACKS:
        ver = j[f'llm_verified{t}'].map({True: 1, False: 0, 'True': 1, 'False': 0})
        gv = pd.to_numeric(j['最终_验证'], errors='coerce').where(lambda s: s.isin([0, 1]))
        pair_metrics('任务一', f'LLM 验证 ({t})', gv, ver, [0, 1], '仲裁口径')
        pair_metrics('任务一', f'LLM 情感 ({t})', j['最终_情感'], j[f'llm_sentiment{t}'], SENT, '仲裁口径')

    # ---- 任务二: 三轨窗口情感 (A/B 共识, 分歧剔除 = stage 64 口径)
    for t in TRACKS:
        base = os.path.join(E, f'09_sentiment_verify{t}')
        x_a, x_b = rd(base + '_blind_A.xlsx'), rd(base + '_blind_B.xlsx').set_index('_row_uid')
        x_b = x_b.reindex(x_a['_row_uid']).reset_index()
        x, y, k = _codes(x_a['人工判定_情感'], x_b['人工判定_情感'], SENT)
        add('任务二', '编码者间信度', f'情感 A-B ({t})', 'Cohen_κ', _boot_pair(x, y, k, _kappa, n_boot, rng), '—')
        rc2 = rd(base + '_reconciliation.xlsx')
        gold = x_a['人工判定_情感'].where(x_a['人工判定_情感'] == x_b['人工判定_情感'])
        note = '共识口径 (分歧剔除)'
        if os.path.isfile(base + '_pending_adjudication.xlsx'):  # 与 stage 64 同口径补入 C 裁决
            adj = rd(base + '_pending_adjudication.xlsx').set_index('_row_uid')['编码者C_情感']
            c_val = adj.reindex(x_a['_row_uid']).to_numpy()
            fill = gold.isna().to_numpy() & pd.Series(c_val).isin(SENT).to_numpy()
            if fill.any():
                gold = gold.where(~fill, c_val)
                note = '共识 + C 仲裁'
        jj = pd.DataFrame({'_row_uid': x_a['_row_uid'], 'gold': gold}).merge(rc2, on='_row_uid', how='left')
        meth = [c for c in rc2.columns if c.startswith(('词典_', 'BERT_', 'LLM_')) or c == '多数投票标签']
        for c in meth:
            pair_metrics('任务二', f'{c} ({t})', jj['gold'], jj[c], SENT, note)

    # ---- 任务三: 过滤器漏检 (A/B)
    a3, b3 = rd(os.path.join(E, 'stage13_reject_audit_blind_A.xlsx')), rd(os.path.join(E, 'stage13_reject_audit_blind_B.xlsx'))
    b3 = b3.set_index('_row_uid').reindex(a3['_row_uid']).reset_index()
    x, y, k = _codes(a3['编码者A_验证'], b3['编码者B_验证'], [0, 1])
    add('任务三', '编码者间信度', '是否误拒 A-B', 'Cohen_κ', _boot_pair(x, y, k, _kappa, n_boot, rng), '—')

    # ---- 任务四: 创新三维 (R1/R2/R3; α 按条目重抽; 人机比对金标准 = 三人多数票)
    mv = pd.read_excel(os.path.join(P, 'manual_validation_samples.xlsx'))
    raters = ('R1', 'R2', 'R3')
    dims = {'stage1_relevant': ['no', 'yes'], 'stage2_sentiment': ['negative', 'neutral', 'positive'],
            'stage3a_substantiveness': ['symbolic', 'substantive'],
            'stage3b_locus': ['technology', 'application'],
            'stage3c_collab': ['self_developed', 'collaborative']}
    for d, labels in dims.items():
        M = np.array([[labels.index(str(v).strip().lower()) if str(v).strip().lower() in labels else -1
                       for v in mv[f'{r}_{d}']] for r in raters])
        add('任务四', '编码者间信度', d, 'Krippendorff_α', _boot_alpha(M, n_boot, rng), '—')
    pred = pd.read_parquet(os.path.join(P, '21_tone_llms.parquet'),
                           columns=['docid', 'target_bank'] + [f'innovation_{d}{t}' for d in
                                                               ('substantiveness', 'locus', 'collab_mode') for t in TRACKS])
    pred['docid'] = pred['docid'].astype(str)
    mv['docid'] = mv['docid'].astype(str)
    pred = pred.drop_duplicates(['docid', 'target_bank'])
    mvj = mv.drop_duplicates(['docid', 'target_bank']).merge(pred, on=['docid', 'target_bank'], how='left')
    for dim, pcol, labels in (('substantiveness', 'innovation_substantiveness', ['实质性', '象征性']),
                              ('locus', 'innovation_locus', ['底层技术', '应用场景']),
                              ('collab', 'innovation_collab_mode', ['自主研发', '外部协同'])):
        gold = mvj.apply(lambda r, dim=dim: adjudicated_gold(
            r, R_COLUMNS_BY_RATER[dim], ADJUDICATION_COLUMNS[dim]), axis=1)
        for t in TRACKS:
            pair_metrics('任务四', f'LLM {dim} ({t})', gold, mvj[f'{pcol}{t}'], labels,
                         '三人多数票 + C 仲裁' if ADJUDICATION_COLUMNS[dim] in mvj else '三人多数票')

    out = pd.DataFrame(rows)
    out['bootstrap'] = f'B={n_boot}, 百分位法, seed={SEED}, 按条目有放回重抽'
    out['生成时间'] = time.strftime('%Y-%m-%d %H:%M:%S')
    path = os.path.join(E, 'human_annotation_bootstrap_ci.csv')
    out.to_csv(path, index=False, encoding='utf-8-sig')
    print(f'{len(out)} 行 → {path}')
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--n-boot', type=int, default=2000)
    run(ap.parse_args().n_boot)
