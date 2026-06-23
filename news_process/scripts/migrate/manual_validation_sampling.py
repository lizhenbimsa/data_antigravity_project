"""人工验证研究 (n≥500) 分层抽样。

输出: news_process/data/processed/manual_validation_samples.xlsx
含 5 个分层 (strata) + 后置 weighting columns, 供 ≥3 名 rater 独立标注。

分层设计 (substantive×symbolic × application×technology 四格 + 拒判格 A;
原 docs/methodology/manual_validation_study_plan.md 已随 docs/ 目录整体删除, commit 1698bda5):
  A: is_bank_fintech_news = False  → 100 篇 (验证拒判正确性)
  B: substantive ∧ application      → 100 篇 (众数基线)
  C: symbolic    ∧ application      → 100 篇 (少数类过采样)
  D: substantive ∧ technology       → 100 篇 (少数类过采样)
  E: symbolic    ∧ technology       → 100 篇 (不足则取全部) — 双重少数类

Stratum E fallback: 若该层不足 100, 取全部 + 把缺额按比例补到 C/D。

运行方式: 从项目根目录运行
    "F:/Anaconda3/python.exe" news_process/scripts/migrate/manual_validation_sampling.py

白话: 从 LLM 已打标的文章里按"类别组合"分五组抽 500 篇, 给三位真人独立标注,
之后拿真人结果和 LLM 结果对账, 检验 LLM 打标可不可信。少见的类别故意多抽,
不然抽不到几篇没法检验。
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PARQUET = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / '21_tone_llms.parquet'
INPUT_FULL_PARQUET = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / '21_tone_llms_full.parquet'
OUTPUT_XLSX = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / 'manual_validation_samples.xlsx'
# 反锚定对账表 (R-0/F1): LLM 预测 (v7ref_*), 仅在编码完成+共识冻结后解锁
RECONCILIATION_XLSX = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / 'manual_validation_reconciliation.xlsx'

SEED = 42
TARGET_TOTAL = 500
PER_STRATUM = 100


def main():
    # 加载: 21_tone_llms_full.parquet 含全部 1,170 篇文章 (包括 verified=False)
    if INPUT_FULL_PARQUET.exists():
        df = pd.read_parquet(INPUT_FULL_PARQUET)
        print(f'Loaded full parquet: {len(df)} rows × {len(df.columns)} cols')
    else:
        df = pd.read_parquet(INPUT_PARQUET)
        print(f'Loaded verified-only parquet: {len(df)} rows × {len(df.columns)} cols')

    # WS-D F7 先决修复 (R6-P2-2): 分层列改读 _full 主轨 + loud 守卫。
    # 现盘 21_tone_llms*.parquet 只有 innovation_substantiveness_{full,ctx,ss}
    # (带后缀), 无裸名 innovation_substantiveness/_locus → 裸名直接 KeyError 崩。
    # 与 :53 已用的 llm_verified_full 主轨一致。
    def _resolve_col(df_, candidates, what):
        for c in candidates:
            if c in df_.columns:
                return c
        innov = [c for c in df_.columns if c.startswith('innovation_')]
        raise SystemExit(
            f'抽样阻塞: 缺 {what} 分层列 (尝试 {candidates}); '
            f'现有 innovation_* 列: {innov}'
        )

    SUBST_COL = _resolve_col(
        df, ['innovation_substantiveness_full', 'innovation_substantiveness'],
        'innovation_substantiveness')
    LOCUS_COL = _resolve_col(
        df, ['innovation_locus_full', 'innovation_locus'], 'innovation_locus')
    # collab 列仅用于 v7ref 参考 + stage3c_collab 标注, 不进分层 (8 格 T=2 枯竭)
    COLLAB_COL = next(
        (c for c in ['innovation_collab_mode_full', 'innovation_collab_mode']
         if c in df.columns), None)

    # 分层
    strata = {}

    # Stratum A: 非银行金融科技新闻 (验证拒判)
    pool_a = df[df.get('llm_verified_full', True) == False]
    strata['A_not_relevant'] = pool_a

    # Stratum B-E: verified=True, 按 innovation_* 维度分层
    verified = df[df.get('llm_verified_full', True) == True].copy()
    print(f'\nVerified subset: {len(verified)}')
    print(f'  {SUBST_COL} distribution:')
    print(verified[SUBST_COL].value_counts(dropna=False).to_string())
    print(f'  {LOCUS_COL} distribution:')
    print(verified[LOCUS_COL].value_counts(dropna=False).to_string())

    # B: 实质性 ∧ 应用场景 (众数格)
    strata['B_substantive_app'] = verified[
        (verified[SUBST_COL] == '实质性') &
        (verified[LOCUS_COL] == '应用场景')
    ]

    # C: 象征性 (symbolic, W&Z 1998 ASQ) ∧ 应用场景
    strata['C_symbolic_app'] = verified[
        (verified[SUBST_COL] == '象征性') &
        (verified[LOCUS_COL] == '应用场景')
    ]

    # D: 实质性 ∧ 底层技术
    strata['D_substantive_tech'] = verified[
        (verified[SUBST_COL] == '实质性') &
        (verified[LOCUS_COL] == '底层技术')
    ]

    # E: 象征性 ∧ 底层技术 (双重少数类)
    strata['E_symbolic_tech'] = verified[
        (verified[SUBST_COL] == '象征性') &
        (verified[LOCUS_COL] == '底层技术')
    ]

    # 抽样 (带不足额回退)
    print(f'\nStratum populations:')
    samples = {}
    backfill_needed = 0
    for name, pool in strata.items():
        avail = len(pool)
        target = PER_STRATUM
        n = min(avail, target)
        if avail < target:
            shortfall = target - avail
            backfill_needed += shortfall
            print(f'  {name}: {avail} avail, taking ALL {n} (shortfall {shortfall} → backfill)')
        else:
            print(f'  {name}: {avail} avail, sampling {n}')
        samples[name] = pool.sample(n=n, random_state=SEED).assign(stratum=name)

    # 若 E (或其他层) 不足额 — 缺额重新分配到 C/D (次稀有的两类)
    if backfill_needed > 0:
        print(f'\nBackfill needed: {backfill_needed} → distributing to C + D')
        # 优先补 C (E 之后最稀有), 再补 D
        for backfill_target in ['C_symbolic_app', 'D_substantive_tech']:
            if backfill_needed <= 0:
                break
            pool = strata[backfill_target]
            already_sampled_ids = set(samples[backfill_target].index)
            remaining = pool.loc[~pool.index.isin(already_sampled_ids)]
            add_n = min(backfill_needed, len(remaining))
            if add_n > 0:
                extra = remaining.sample(n=add_n, random_state=SEED + 1).assign(stratum=backfill_target + '_extra')
                samples[backfill_target] = pd.concat([samples[backfill_target], extra])
                print(f'  {backfill_target}: +{add_n} (now {len(samples[backfill_target])})')
                backfill_needed -= add_n

    # 合并各层样本
    out = pd.concat(samples.values(), ignore_index=False).reset_index(drop=False)
    out = out.rename(columns={'index': 'orig_index'})

    # 追加后置分层加权列
    # population_weight = (该层总体数) / (该层样本数)
    # 白话: 少数类被故意多抽了, 算总体指标时要用这个权重"还原"回真实占比。
    for name in samples.keys():
        clean_name = name.replace('_extra', '')
        pop_size = len(strata[clean_name])
        sample_size = sum(1 for s in out['stratum'] if s.startswith(clean_name))
        weight = pop_size / sample_size if sample_size > 0 else 0.0
        out.loc[out['stratum'].str.startswith(clean_name), 'population_weight'] = weight

    # 标注表单列 (初始为空, 留给 rater 填写)
    # WS-D: 新增 stage3c_collab (自研/协同, Chesbrough 2003 / L&S 2006);
    # 取值 self_developed / collaborative (与 _RATER_VALUE_TO_CANONICAL_LABEL_RAW 对齐)。
    for rater in ['R1', 'R2', 'R3']:
        for stage_col in [
            f'{rater}_stage1_relevant',         # yes / no
            f'{rater}_stage1_conf',              # low / med / high
            f'{rater}_stage2_sentiment',         # positive / neutral / negative
            f'{rater}_stage2_conf',
            f'{rater}_stage3a_substantiveness',  # substantive / symbolic
            f'{rater}_stage3a_conf',
            f'{rater}_stage3a_rationale',        # 自由文本
            f'{rater}_stage3b_locus',            # technology / application
            f'{rater}_stage3b_conf',
            f'{rater}_stage3b_rationale',
            f'{rater}_stage3c_collab',           # self_developed / collaborative
            f'{rater}_stage3c_conf',
            f'{rater}_stage3c_rationale',
            f'{rater}_total_time_sec',           # 用于注意力检查
        ]:
            out[stage_col] = ''

    # WS-D 纯随机层 (R4-P2-05): 10-20% 不按任何 LLM 标签随机抽,
    # 供无偏估计 LLM 漏判率 (分层抽样按 LLM 标签定义 frame 无法估漏判)。
    # ⚠ T=2/N≈400 下仅作 face-validity 哨兵, 漏判率点估计不附推断 CI,
    #   真值 deferred-T18 全样本。
    already = set(out['orig_index'])
    pure_pool = df.loc[~df.index.isin(already)]
    pure_n = min(len(pure_pool), max(1, round(0.15 * len(out))))
    if pure_n > 0:
        pure = (pure_pool.sample(n=pure_n, random_state=SEED + 2)
                .assign(stratum='F_pure_random')
                .reset_index().rename(columns={'index': 'orig_index'}))
        pure['population_weight'] = len(df) / pure_n if pure_n else 0.0
        # 给纯随机层补齐 rater 标注列 (空) 与其余 out 列
        for c in out.columns:
            if c not in pure.columns:
                pure[c] = '' if c.startswith(('R1_', 'R2_', 'R3_')) else pd.NA
        out = pd.concat([out, pure[out.columns]], ignore_index=True)

    # ── 反锚定双文件 (R-0/F1): 编码者盲表零 LLM 标签 + 对账表后解锁 ──
    rater_cols = [c for c in out.columns if c.startswith(('R1_', 'R2_', 'R3_'))]
    # 窗口文本列 (F13/R-P1-3): 供 deferred 窗口级金标准 (各轨独立窗口判标签)
    metadata_cols = ['orig_index', 'docid', 'target_bank', '标题', '内容',
                     'content_ctx', 'content_ss', 'stratum', 'population_weight']
    metadata_cols = [c for c in metadata_cols if c in out.columns]

    # v7ref LLM 预测 (含 collab): 仅进对账表, 绝不进编码者盲表 (anchoring)
    v7_ref_cols_orig = [c for c in ['llm_verified_full', 'llm_sentiment_full',
                                    SUBST_COL, LOCUS_COL, COLLAB_COL]
                        if c and c in out.columns]
    rename_map = {c: f'v7ref_{c}' for c in v7_ref_cols_orig}

    # D5 修复: random shuffle 避免 rater 在 stratum boundary anchoring bias
    out = out.sample(frac=1, random_state=43).reset_index(drop=True)

    # (a) coder-facing 盲表: 元数据 + 空白 rater 列, 零 LLM 输出
    coder_cols = [c for c in (metadata_cols + rater_cols) if c in out.columns]
    coder_df = out[coder_cols]
    # (b) reconciliation 对账表: orig_index 主键 + 全部 v7ref_ LLM 预测,
    #     编码完成+共识冻结后才解锁对账
    recon_df = out[['orig_index'] + v7_ref_cols_orig].rename(columns=rename_map)

    print(f'\nFinal sample size: {len(out)}')
    print('Stratum breakdown:')
    print(out['stratum'].value_counts().to_string())
    print(f'\n[盲表] coder-facing (零 LLM 标签) → {OUTPUT_XLSX}')
    coder_df.to_excel(OUTPUT_XLSX, index=False)
    print(f'[对账表] reconciliation (LLM 预测, 编码后解锁) → {RECONCILIATION_XLSX}')
    recon_df.to_excel(RECONCILIATION_XLSX, index=False)
    print('Done.')


if __name__ == '__main__':
    main()
