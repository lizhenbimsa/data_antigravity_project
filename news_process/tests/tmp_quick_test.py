"""防御机制验证"""
import pandas as pd, numpy as np

df = pd.DataFrame({
    'target_bank': ['工行','工行'],
    'year': [2023,2023],
    'llm_vote_score_full': [0.8, -0.2],
    # 无 herd_weight 和 is_forward_looking
})

agg_dict = {
    'avg_herd_weight': ('herd_weight', 'mean'),
    'min_herd_weight': ('herd_weight', 'min'),
    'avg_is_forward_looking': ('is_forward_looking', 'mean'),
    'n_articles': ('llm_vote_score_full', 'count'),
}

valid_agg = {}
missing = []
for out_col, (src_col, func) in agg_dict.items():
    if src_col in df.columns:
        valid_agg[out_col] = (src_col, func)
    else:
        missing.append(f'{out_col} <- {src_col}')

print(f'有效: {list(valid_agg.keys())}')
print(f'跳过: {missing}')
panel = df.groupby(['target_bank','year']).agg(**valid_agg).reset_index()
print(f'面板列: {list(panel.columns)}')
assert 'avg_herd_weight' not in panel.columns
assert 'n_articles' in panel.columns
print('防御机制有效 ✓')
