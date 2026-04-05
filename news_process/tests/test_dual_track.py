"""
双轨重构全面验证脚本
检验所有阶段输出的列完整性、数据质量和回退公理
"""
import pandas as pd
import os
import sys

OUTPUT_DIR = "data_processed"
ERRORS = []

def check(label, condition, detail=""):
    status = "OK" if condition else "FAIL"
    if not condition:
        ERRORS.append(f"{label}: {detail}")
    print(f"  [{status}] {label}" + (f" ({detail})" if detail else ""))

print("=" * 70)
print("  双轨输出列完整性验证 (Dual-Track Verification)")
print("=" * 70)

# ━━━ 1. 阶段 21: LLM 双轨输出 ━━━
print("\n━━━ 阶段 21: LLM 双轨输出 ━━━")
df21_path = os.path.join(OUTPUT_DIR, "21_tone_llms.parquet")
if os.path.exists(df21_path):
    df21 = pd.read_parquet(df21_path)
    print(f"行数: {len(df21)}, 列数: {len(df21.columns)}")
    
    core_21_cols = [
        'llm_verified_full', 'llm_verified_ctx',
        'llm_sentiment_full', 'llm_sentiment_ctx',
        'llm_agreement_rate_full', 'llm_agreement_rate_ctx',
        'fintech_category', 'category_confidence',
    ]
    for col in core_21_cols:
        exists = col in df21.columns
        nan_ct = int(df21[col].isna().sum()) if exists else -1
        check(col, exists, f"NaN={nan_ct}")
    
    # 检查逐模型双轨列
    model_shorts = []
    for c in df21.columns:
        if c.endswith('_verified_full'):
            sn = c.replace('_verified_full', '')
            if sn != 'llm':
                model_shorts.append(sn)
    print(f"  发现逐模型 short_names: {model_shorts}")
    for sn in model_shorts:
        for track in ['_full', '_ctx']:
            for sfx in ['_verified', '_sentiment', '_verification_confidence', '_sentiment_confidence']:
                col = f"{sn}{sfx}{track}"
                check(f"{sn}{sfx}{track}", col in df21.columns)
else:
    ERRORS.append("21_tone_llms.parquet not found")

# ━━━ 2. 阶段 22: 词典法双轨输出 ━━━
print("\n━━━ 阶段 22: 词典法双轨输出 ━━━")
df22_path = os.path.join(OUTPUT_DIR, "22_words_tone.parquet")
if os.path.exists(df22_path):
    df22 = pd.read_parquet(df22_path)
    print(f"行数: {len(df22)}, 列数: {len(df22.columns)}")
    
    dicts = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']
    for d in dicts:
        for track in ['_full', '_ctx']:
            for sfx in ['_score', '_label', '_zscore']:
                col = f"{d}{sfx}{track}"
                check(col, col in df22.columns)
    
    check("sentiment_details_full", "sentiment_details_full" in df22.columns)
    check("sentiment_details_ctx", "sentiment_details_ctx" in df22.columns)
    
    # Z-score 独立性检验
    for d in dicts:
        if f'{d}_zscore_full' in df22.columns and f'{d}_zscore_ctx' in df22.columns:
            mean_full = df22[f'{d}_zscore_full'].mean()
            mean_ctx = df22[f'{d}_zscore_ctx'].mean()
            msg = f"zscore_full_mean={mean_full:.6f}, zscore_ctx_mean={mean_ctx:.6f}"
            check(f"{d} Z-score独立标准化", abs(mean_full) < 0.01 and abs(mean_ctx) < 0.01, msg)
else:
    ERRORS.append("22_words_tone.parquet not found")

# ━━━ 3. 阶段 23: BERT 双轨输出 ━━━
print("\n━━━ 阶段 23: BERT 双轨输出 ━━━")
df23_path = os.path.join(OUTPUT_DIR, "23_bert_tone.parquet")
if os.path.exists(df23_path):
    df23 = pd.read_parquet(df23_path)
    print(f"行数: {len(df23)}, 列数: {len(df23.columns)}")
    
    full_cols = [c for c in df23.columns if c.endswith('_full')]
    ctx_cols = [c for c in df23.columns if c.endswith('_ctx')]
    print(f"  _full 列数: {len(full_cols)}")
    print(f"  _ctx 列数: {len(ctx_cols)}")
    
    check("bert_num_windows_full", "bert_num_windows_full" in df23.columns)
    check("bert_num_windows_ctx", "bert_num_windows_ctx" in df23.columns)
    
    # LLM 列继承检查
    check("llm_verified_full (继承)", "llm_verified_full" in df23.columns)
    check("llm_sentiment_ctx (继承)", "llm_sentiment_ctx" in df23.columns)
    
    # 词典列继承检查
    check("jiang_2021_score_full (继承)", "jiang_2021_score_full" in df23.columns)
    check("jiang_2021_score_ctx (继承)", "jiang_2021_score_ctx" in df23.columns)
else:
    ERRORS.append("23_bert_tone.parquet not found")

# ━━━ 4. 阶段 41-45: 面板数据双轨输出 ━━━
print("\n━━━ 阶段 41-45: 面板数据双轨输出 ━━━")
df40_path = os.path.join(OUTPUT_DIR, "40_panel_yearly.parquet")
if os.path.exists(df40_path):
    df40 = pd.read_parquet(df40_path)
    print(f"行数: {len(df40)}, 列数: {len(df40.columns)}")
    
    panel_key_cols = [
        'n_articles', 'target_bank', 'year',
        'llm_vote_tone_full', 'llm_vote_tone_ctx',
        'pos_frac_full', 'pos_frac_ctx',
        'neg_frac_full', 'neg_frac_ctx',
        'dict_avg_tone_full', 'dict_avg_tone_ctx',
        'bert_avg_pos_full', 'bert_avg_pos_ctx',
        'bert_avg_neg_full', 'bert_avg_neg_ctx',
        'llm_models_avg_tone_full', 'llm_models_avg_tone_ctx',
        'avg_agreement_rate_full', 'avg_agreement_rate_ctx',
    ]
    for col in panel_key_cols:
        check(col, col in df40.columns)
    
    full_panel_cols = [c for c in df40.columns if c.endswith('_full')]
    ctx_panel_cols = [c for c in df40.columns if c.endswith('_ctx')]
    print(f"  面板 _full 列数: {len(full_panel_cols)}")
    print(f"  面板 _ctx 列数: {len(ctx_panel_cols)}")
else:
    ERRORS.append("40_panel_yearly.parquet not found")

# ━━━ 5. 回退公理验证 (NaN 检查) ━━━
print("\n━━━ 回退公理验证 (NaN 检查) ━━━")
if os.path.exists(df23_path):
    for track in ['_full', '_ctx']:
        track_cols = [c for c in df23.columns if c.endswith(track)]
        total_nan = 0
        nan_cols = []
        for c in track_cols:
            n = df23[c].isna().sum()
            if n > 0:
                total_nan += n
                nan_cols.append(f"{c}({n})")
        detail = f"NaN总计={total_nan}"
        if nan_cols:
            detail += f", 含NaN的列: {', '.join(nan_cols[:5])}"
        check(f"{track} 轨道无 NaN", total_nan == 0, detail)

# ━━━ 6. 全量文件完整性 ━━━
print("\n━━━ 全量 LLM 输出验证 ━━━")
df21_full_path = os.path.join(OUTPUT_DIR, "21_tone_llms_full.parquet")
if os.path.exists(df21_full_path):
    df21_full = pd.read_parquet(df21_full_path)
    print(f"全量文件行数: {len(df21_full)}, 列数: {len(df21_full.columns)}")
    check("全量文件包含 llm_verified_full", "llm_verified_full" in df21_full.columns)
    check("全量文件包含 llm_verified_ctx", "llm_verified_ctx" in df21_full.columns)
    verified_full = df21_full['llm_verified_full'].sum()
    verified_ctx = df21_full['llm_verified_ctx'].sum()
    check("过滤文件行数一致", len(df21) == verified_full, f"filtered={len(df21)}, verified_full={verified_full}")
    print(f"  全量文件: verified_full={verified_full}, verified_ctx={verified_ctx}")

# ━━━ 汇总 ━━━
print("\n" + "=" * 70)
if ERRORS:
    print(f"  ✗ 发现 {len(ERRORS)} 个问题:")
    for e in ERRORS:
        print(f"    - {e}")
    sys.exit(1)
else:
    print("  ✓ 全部验证通过! 双轨重构完全正确!")
print("=" * 70)
