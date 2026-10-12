"""stage 13 共现过滤被拒行 (假阴性/漏检) 人工审计 — 抽样 + 回读 (WP-D, 2026-07-03)。

背景: 人工验证此前只覆盖 stage 13 过滤**之后**的宇宙 (61/09/manual_validation
Stratum A 均是), 过滤器丢掉的行从未被审计 → 假阴性率 (真银行金科新闻被误拒
的比例) 无法估计。本脚本从被拒宇宙分层抽样产盲表, 双编码回读后给出
假阴性率点估 + Wilson 95% CI + Manski-Lerman 总体外推。

⚠ 被拒宇宙 = 行级 anti-join (12 − 13, 键 = (docid, target_bank)):
   R4 实证 docid 集合差 (61) ≠ 真实被拒行数 (106) — 同一 docid 部分行被拒
   部分存活, docid 集合差集口径**禁用**。

落位 = scripts/migrate/ (镜像 manual_validation_sampling.py): 不建 root shim,
不动 16/16/35/OUTPUT_REGISTRY 计数不变量。全程 $0, 无 LLM/嵌入调用, golden 无关。

用法 (repo 根, python = 项目解释器):
    python news_process/scripts/migrate/stage13_reject_audit_sampling.py            # 抽样产盲表
    python news_process/scripts/migrate/stage13_reject_audit_sampling.py readback   # 标注后算假阴性率
    python news_process/scripts/migrate/stage13_reject_audit_sampling.py adjudicate # A≠B 分歧行产仲裁表 (C 填)

协议 = scripts/audit/HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md (任务 T4)。
"""
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

PROCESSED = PROJECT_ROOT / 'news_process' / 'data' / 'processed'
INPUT_12 = PROCESSED / '12_fintech_news.parquet'
INPUT_13 = PROCESSED / '13_cooccurrence_filtered.parquet'
OUT_DIR = PROCESSED / 'eval_reports'
BLIND_A = OUT_DIR / 'stage13_reject_audit_blind_A.xlsx'
BLIND_B = OUT_DIR / 'stage13_reject_audit_blind_B.xlsx'
RECON = OUT_DIR / 'stage13_reject_audit_reconciliation.xlsx'
RESULT_CSV = OUT_DIR / 'stage13_reject_audit.csv'
PENDING = OUT_DIR / 'stage13_reject_audit_pending_adjudication.xlsx'

SEED = 42
TARGET_N = 300
ROW_KEY = ['docid', 'target_bank']
BLIND_CONTEXT = ['_row_uid', 'docid', '日期', '媒体类型(中文)', '标题', '内容', 'target_bank']
VER_LABELS = (1, 0)


def _build_rejected_universe() -> pd.DataFrame:
    """被拒宇宙 = 12 − 13 行级 anti-join, 键 (docid, target_bank) 须双侧唯一。"""
    df12 = pd.read_parquet(INPUT_12)
    df13 = pd.read_parquet(INPUT_13)
    for name, d in (('12_fintech_news', df12), ('13_cooccurrence_filtered', df13)):
        missing = [k for k in ROW_KEY if k not in d.columns]
        if missing:
            raise SystemExit(f'[FATAL] {name} 缺行键列 {missing}')
        if d.duplicated(subset=ROW_KEY).any():
            n_dup = int(d.duplicated(subset=ROW_KEY).sum())
            raise SystemExit(
                f'[FATAL] {name} 的 (docid, target_bank) 非唯一 ({n_dup} 重复行) — '
                '行级 anti-join 键失效, 须改用带序次的复合键后重跑')
    merged = df12.merge(df13[ROW_KEY].assign(_kept=1), on=ROW_KEY, how='left')
    rejected = merged[merged['_kept'].isna()].drop(columns=['_kept']).copy()
    print(f'12 号 {len(df12)} 行 − 13 号 {len(df13)} 行 → 被拒宇宙 {len(rejected)} 行 '
          f'(行级 anti-join; docid 集合差口径禁用)')
    return rejected


def _stratum_labels(df: pd.DataFrame) -> pd.Series:
    year = pd.to_datetime(df.get('日期'), errors='coerce').dt.year.fillna(-1).astype(int)
    media = df.get('媒体类型(中文)', pd.Series('', index=df.index)).astype(str)
    return year.astype(str) + '×' + media


def _refuse_if_annotated() -> None:
    """人工标注防覆写: 任一盲表已有非空标注即拒绝重抽 (config/validation.yaml::
    human_annotation_frozen 冻结清单; 人工成果不可从代码重建, 无越权开关)。"""
    for coder, path in (('A', BLIND_A), ('B', BLIND_B)):
        if not path.exists():
            continue
        try:
            col = pd.read_excel(path, sheet_name='验证数据')[f'编码者{coder}_验证']
        except Exception as e:
            raise SystemExit(f'[FATAL] 读取既有盲表失败 ({e}), 为保护人工标注拒绝重抽: {path}')
        s = col.astype('object').where(col.notna(), '').astype(str).str.strip()
        if s.ne('').any():
            raise SystemExit(f'[FATAL] {path} 已有 {int(s.ne("").sum())} 条人工标注, 拒绝重抽 '
                             '(人工标注严禁修改/删除, 见 config/validation.yaml::human_annotation_frozen)')


def sample() -> None:
    _refuse_if_annotated()
    rejected = _build_rejected_universe()
    if rejected.empty:
        raise SystemExit('[FATAL] 被拒宇宙为空 — stage 13 未丢行或输入文件不齐')

    rejected = rejected.reset_index(drop=True)
    rejected['_stratum'] = _stratum_labels(rejected)
    n_pop = len(rejected)
    rng = np.random.RandomState(SEED)

    if n_pop <= TARGET_N:
        print(f'⚠ 被拒宇宙 {n_pop} ≤ 目标 {TARGET_N}: 全选 (早期试跑 T=2 属预期; '
              '生产 T=19 重抽才有效度意义)')
        sample_df = rejected.copy()
    else:
        # 年×媒体类型 分层比例配额 (largest remainder), 层内 SRS
        pop_counts = rejected['_stratum'].value_counts()
        quota_f = pop_counts / n_pop * TARGET_N
        quota = quota_f.astype(int)
        rem = TARGET_N - int(quota.sum())
        if rem > 0:
            frac_order = (quota_f - quota).sort_values(ascending=False)
            for s in frac_order.index[:rem]:
                quota[s] += 1
        picks = []
        for s, q in quota.items():
            pool = rejected.index[rejected['_stratum'] == s]
            q = min(int(q), len(pool))
            if q > 0:
                picks.append(rng.choice(pool, size=q, replace=False))
        sample_df = rejected.loc[np.concatenate(picks)].copy()

    # 层权 (Manski-Lerman poststratify) + shuffle + 合成行键
    n_smp = len(sample_df)
    pop_counts = rejected['_stratum'].value_counts()
    smp_counts = sample_df['_stratum'].value_counts()
    sample_df['population_weight'] = sample_df['_stratum'].map(
        lambda s: (pop_counts[s] / n_pop) / (smp_counts[s] / n_smp))
    sample_df = sample_df.sample(frac=1, random_state=SEED).reset_index(drop=True)
    sample_df['_row_uid'] = range(len(sample_df))
    for c in ('编码者A_验证', '编码者B_验证'):
        sample_df[c] = ''

    guide = pd.DataFrame(
        [('任务', '独立判定: 编码者X_验证 ∈ {1,0} — 1=该文确为目标银行 (target_bank 列) 的'
                  '金融科技相关新闻 (即被过滤器误拒), 0=不是 (过滤正确)。'),
         ('判断依据', '阅读"标题"+"内容"全文; 银行仅被列举且无金科关联细节=0; 文本异常=0。'),
         ('独立性', '禁止与另一位编码员交流; 按行序标注。'),
         ('完整协议', 'scripts/audit/HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md (任务 T4)')],
        columns=['项目', '说明'])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for coder, path in (('A', BLIND_A), ('B', BLIND_B)):
        ann = f'编码者{coder}_验证'
        cols = [ann] + [c for c in BLIND_CONTEXT if c in sample_df.columns]
        blind = sample_df[cols].copy()
        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            blind.to_excel(writer, sheet_name='验证数据', index=False)
            guide.to_excel(writer, sheet_name='编码指南', index=False)
            ci = list(blind.columns).index(ann)
            writer.sheets['验证数据'].data_validation(
                1, ci, len(blind), ci, {'validate': 'list', 'source': ['1', '0']})
        print(f'盲表{coder} = {path} ({len(blind)} 行, 零机器列, 验证列锁下拉)')

    recon = sample_df.drop(columns=['编码者A_验证', '编码者B_验证'])
    with pd.ExcelWriter(RECON, engine='xlsxwriter') as writer:
        recon.to_excel(writer, sheet_name='验证数据', index=False)
        pd.DataFrame({'统计项': ['样本行数', '被拒宇宙行数', '12号行数键', '13号行数键',
                                 '层数', '生成时间', '随机种子'],
                      '值': [n_smp, n_pop, str(INPUT_12), str(INPUT_13),
                             int(pop_counts.shape[0]),
                             time.strftime('%Y-%m-%d %H:%M:%S'), SEED]},
                     ).to_excel(writer, sheet_name='统计概览', index=False)
    print(f'对账表 = {RECON} (层/权重/全列; 不发编码员)')


def _load_coded():
    """读双盲表 + 对账表, 返回 (A 判定, B 判定, 对账表), 均以 _row_uid 为索引。"""
    for p in (BLIND_A, BLIND_B, RECON):
        if not p.exists():
            raise SystemExit(f'[FATAL] 缺文件: {p} — 先跑抽样')
    a = pd.read_excel(BLIND_A, sheet_name='验证数据')
    b = pd.read_excel(BLIND_B, sheet_name='验证数据')
    recon = pd.read_excel(RECON, sheet_name='验证数据')
    if (len(a) != len(b) or set(a['_row_uid']) != set(b['_row_uid'])
            or set(a['_row_uid']) != set(recon['_row_uid'])):
        raise SystemExit('[FATAL] _row_uid 三侧不一致, 拒绝回读')
    va = pd.to_numeric(a.set_index('_row_uid')['编码者A_验证'], errors='coerce')
    vb = pd.to_numeric(b.set_index('_row_uid')['编码者B_验证'], errors='coerce').reindex(va.index)
    return a.set_index('_row_uid'), va, vb, recon.set_index('_row_uid')


def adjudicate() -> None:
    """A≠B 的分歧行 → 仲裁工作台 (镜像 llms_human 任务一仲裁表: 文本 + A/B 判定, 零机器列)。

    第三编码员 C 只填 编码者C_验证; 填毕后 readback 自动并入, 与剔除口径并排报告。
    """
    a, va, vb, _ = _load_coded()
    dis = va.isin(VER_LABELS) & vb.isin(VER_LABELS) & (va != vb)
    if not dis.any():
        print('无分歧行, 不需仲裁')
        return
    if PENDING.exists():
        old = pd.read_excel(PENDING, sheet_name='验证数据')
        if '编码者C_验证' in old.columns and old['编码者C_验证'].notna().any():
            raise SystemExit(f'[FATAL] 既有仲裁表已含 C 判定, 拒绝覆盖: {PENDING}')
    ctx = [c for c in BLIND_CONTEXT if c != '_row_uid' and c in a.columns]
    pend = a.loc[dis, ctx].copy()
    pend.insert(0, '_row_uid', pend.index)
    pend['编码者A_验证'] = va[dis].astype(int)
    pend['编码者B_验证'] = vb[dis].astype(int)
    pend['编码者C_验证'] = ''
    with pd.ExcelWriter(PENDING, engine='xlsxwriter') as writer:
        pend.to_excel(writer, sheet_name='验证数据', index=False)
        ci = list(pend.columns).index('编码者C_验证')
        writer.sheets['验证数据'].data_validation(
            1, ci, len(pend), ci, {'validate': 'list', 'source': ['1', '0']})
    print(f'仲裁表 = {PENDING} ({len(pend)} 行, 仅 A≠B 分歧行, 零机器列)')


def readback() -> None:
    from news_process.validation.dict_coverage import wilson_ci

    _, va, vb, recon = _load_coded()
    both = va.isin(VER_LABELS) & vb.isin(VER_LABELS)
    agree = both & (va == vb)
    n_both, n_agree = int(both.sum()), int(agree.sum())
    if n_agree == 0:
        raise SystemExit(f'[pending] 双编码共识 0 条 (双合法 {n_both}) — 标注未完成或全分歧')

    # 仲裁口径: 分歧行由 C 裁决补入 (C 空 → 仍剔除); 剔除口径永远并排保留
    vc = pd.Series(np.nan, index=va.index)
    if PENDING.exists():
        adj = pd.read_excel(PENDING, sheet_name='验证数据')
        if '编码者C_验证' in adj.columns:
            vc = pd.to_numeric(adj.set_index('_row_uid')['编码者C_验证'],
                               errors='coerce').reindex(va.index)
    adj_mask = both & (va != vb) & vc.isin(VER_LABELS)
    gold_strict = va[agree]
    gold_adj = pd.concat([gold_strict, vc[adj_mask]])

    rows = []
    for name, gold, note in (
            ('stage13_假阴性率_剔除口径', gold_strict, '共识=1 占比; 分歧行剔除'),
            ('stage13_假阴性率_仲裁口径', gold_adj, '共识 + 分歧行 C 裁决; C 未裁决行剔除')):
        if name.endswith('仲裁口径') and not adj_mask.any():
            continue
        w = recon['population_weight'].reindex(gold.index).astype(float)
        fn_rate = float((gold == 1).mean())
        lo, hi = wilson_ci(fn_rate, len(gold))
        fn_rate_w = float(((gold == 1).astype(float) * w).sum() / w.sum()) if w.sum() > 0 else np.nan
        rows.append({
            '指标': name, '金标准n': len(gold), '双合法n': n_both,
            '分歧n': n_both - n_agree, 'C裁决n': int(adj_mask.sum()),
            '点估_未加权': round(fn_rate, 4),
            'Wilson95CI_下': round(lo, 4), 'Wilson95CI_上': round(hi, 4),
            '点估_ManskiLerman加权': round(fn_rate_w, 4) if not np.isnan(fn_rate_w) else '',
            '口径': note + '; 加权=总体后分层外推',
            '生成时间': time.strftime('%Y-%m-%d %H:%M:%S'),
        })
        print(f'{name} = {fn_rate:.4f} [{lo:.4f}, {hi:.4f}] (加权 {fn_rate_w:.4f}, n={len(gold)})')
    pd.DataFrame(rows).to_csv(RESULT_CSV, index=False, encoding='utf-8-sig')
    print(f'结果 → {RESULT_CSV}')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'readback':
        readback()
    elif len(sys.argv) > 1 and sys.argv[1] == 'adjudicate':
        adjudicate()
    else:
        sample()
