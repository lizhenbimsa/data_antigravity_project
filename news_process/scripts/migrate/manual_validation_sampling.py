"""Manual validation study (n≥500) stratified sampling.

Output: news_process/data/processed/manual_validation_samples.xlsx
含 5 strata + 后置 weighting columns, 供 ≥3 raters 独立标注。

Strata (per docs/methodology/manual_validation_study_plan.md §2.2):
  A: is_bank_fintech_news = False  → 100 articles (validate rejection)
  B: substantive ∧ application      → 100 articles (modal baseline)
  C: symbolic    ∧ application      → 100 articles (over-sample minority)
  D: substantive ∧ technology       → 100 articles (over-sample minority)
  E: symbolic    ∧ technology       → 100 (or all if fewer) — double minority

Stratum E fallback: 若该层不足 100, 取全部 + 把缺额按比例补到 C/D。

Execution: 从项目根目录运行
    "F:/Anaconda3/python.exe" news_process/scripts/migrate/manual_validation_sampling.py
"""
import sys
from pathlib import Path

import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PARQUET = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / '21_tone_llms.parquet'
INPUT_FULL_PARQUET = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / '21_tone_llms_full.parquet'
OUTPUT_XLSX = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / 'manual_validation_samples.xlsx'

SEED = 42
TARGET_TOTAL = 500
PER_STRATUM = 100


def main():
    # Load: 21_tone_llms_full.parquet contains all 1,170 articles incl. verified=False
    if INPUT_FULL_PARQUET.exists():
        df = pd.read_parquet(INPUT_FULL_PARQUET)
        print(f'Loaded full parquet: {len(df)} rows × {len(df.columns)} cols')
    else:
        df = pd.read_parquet(INPUT_PARQUET)
        print(f'Loaded verified-only parquet: {len(df)} rows × {len(df.columns)} cols')

    # Stratify
    strata = {}

    # Stratum A: not bank-fintech (validate rejection)
    pool_a = df[df.get('llm_verified_full', True) == False]
    strata['A_not_relevant'] = pool_a

    # Stratum B-E: verified=True, 按 innovation_* 维度分层
    verified = df[df.get('llm_verified_full', True) == True].copy()
    print(f'\nVerified subset: {len(verified)}')
    print(f'  innovation_substantiveness distribution:')
    print(verified['innovation_substantiveness'].value_counts(dropna=False).to_string())
    print(f'  innovation_locus distribution:')
    print(verified['innovation_locus'].value_counts(dropna=False).to_string())

    # B: 实质性 ∧ 应用场景 (modal)
    strata['B_substantive_app'] = verified[
        (verified['innovation_substantiveness'] == '实质性') &
        (verified['innovation_locus'] == '应用场景')
    ]

    # C: 描述性 (= symbolic post-translation) ∧ 应用场景
    strata['C_symbolic_app'] = verified[
        (verified['innovation_substantiveness'] == '象征性') &
        (verified['innovation_locus'] == '应用场景')
    ]

    # D: 实质性 ∧ 底层技术
    strata['D_substantive_tech'] = verified[
        (verified['innovation_substantiveness'] == '实质性') &
        (verified['innovation_locus'] == '底层技术')
    ]

    # E: 描述性 ∧ 底层技术 (double minority)
    strata['E_symbolic_tech'] = verified[
        (verified['innovation_substantiveness'] == '象征性') &
        (verified['innovation_locus'] == '底层技术')
    ]

    # Sample with fallback
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

    # Backfill if E (or others) short — redistribute to C/D (next most rare classes)
    if backfill_needed > 0:
        print(f'\nBackfill needed: {backfill_needed} → distributing to C + D')
        # 优先 C (singletons after E), then D
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

    # Combine
    out = pd.concat(samples.values(), ignore_index=False).reset_index(drop=False)
    out = out.rename(columns={'index': 'orig_index'})

    # Add post-stratification weighting columns
    # population_weight = (population count of stratum) / (sample count of stratum)
    for name in samples.keys():
        clean_name = name.replace('_extra', '')
        pop_size = len(strata[clean_name])
        sample_size = sum(1 for s in out['stratum'] if s.startswith(clean_name))
        weight = pop_size / sample_size if sample_size > 0 else 0.0
        out.loc[out['stratum'].str.startswith(clean_name), 'population_weight'] = weight

    # Annotation form columns (initially empty for raters to fill)
    for rater in ['R1', 'R2', 'R3']:
        for stage_col in [
            f'{rater}_stage1_relevant',         # yes / no
            f'{rater}_stage1_conf',              # low / med / high
            f'{rater}_stage2_sentiment',         # positive / neutral / negative
            f'{rater}_stage2_conf',
            f'{rater}_stage3a_substantiveness',  # substantive / symbolic
            f'{rater}_stage3a_conf',
            f'{rater}_stage3a_rationale',        # free text
            f'{rater}_stage3b_locus',            # technology / application
            f'{rater}_stage3b_conf',
            f'{rater}_stage3b_rationale',
            f'{rater}_total_time_sec',           # for attention check
        ]:
            out[stage_col] = ''

    # Reorder: metadata → rater forms → v7 reference (v7 cols renamed with v7_
    # prefix to make their "for reference only" status visually obvious to raters)
    rater_cols = [c for c in out.columns if c.startswith(('R1_', 'R2_', 'R3_'))]
    v7_ref_cols_orig = ['llm_verified_full', 'llm_sentiment_full',
                        'innovation_substantiveness', 'innovation_locus']
    metadata_cols = ['orig_index', 'docid', 'target_bank', '标题', '内容',
                     'stratum', 'population_weight']
    v7_ref_cols_orig = [c for c in v7_ref_cols_orig if c in out.columns]
    metadata_cols = [c for c in metadata_cols if c in out.columns]

    # 重命名 v7 cols 加 "v7ref_" 前缀, 提示这些列仅供参考 (不应锚定 rater 判断)
    rename_map = {c: f'v7ref_{c}' for c in v7_ref_cols_orig}
    out = out.rename(columns=rename_map)
    v7_ref_cols = [rename_map[c] for c in v7_ref_cols_orig]
    col_order = metadata_cols + rater_cols + v7_ref_cols
    col_order = [c for c in col_order if c in out.columns]
    out = out[col_order]

    # D5 修复 (审核): random shuffle 避免 rater 在 stratum boundary anchoring bias
    out = out.sample(frac=1, random_state=43).reset_index(drop=True)

    print(f'\nFinal sample size: {len(out)}')
    print(f'Stratum breakdown:')
    print(out['stratum'].value_counts().to_string())
    print(f'\nWriting to: {OUTPUT_XLSX}')
    out.to_excel(OUTPUT_XLSX, index=False)
    print(f'Done.')


if __name__ == '__main__':
    main()
