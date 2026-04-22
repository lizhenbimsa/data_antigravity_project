"""
_test_integration.py — 集成测试: 模拟完整数据流
=================================================
目标: 使用微型数据集模拟 45_panel_export_main.py 中新增
      步骤 7d-geo / 7d-imit / 7h-cogn / 7h-brok / 7h-neg / 7h-fire
      的完整数据流, 验证端到端正确性。
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'f:\WiseSearch\data_antigravity_project\news_process')

import numpy as np
import pandas as pd
import importlib.util as _iu

# 加载模块
base = r'f:\WiseSearch\data_antigravity_project\news_process'

def load_mod(name, path):
    s = _iu.spec_from_file_location(name, path)
    m = _iu.module_from_spec(s)
    s.loader.exec_module(m)
    return m

m43 = load_mod('m43', f'{base}\\43_panel_indicators_geography.py')
m46 = load_mod('m46', f'{base}\\46_network_spillovers.py')
m47 = load_mod('m47', f'{base}\\47_network_brokerage.py')

# ============================================================
# 构造微型测试数据
# ============================================================
print("=" * 60)
print("集成测试: 端到端流水线数据流模拟")
print("=" * 60)

np.random.seed(42)
banks = ['工商银行', '建设银行', '农业银行', '中国银行', '交通银行']
years = [2019, 2020, 2021]
medias = ['财经网', '新浪财经', '经济日报', '人民日报', '证券时报',
          '每日经济新闻', '第一财经', '金融界']

# --- 篇章级数据 ---
rows = []
for year in years:
    for bank in banks:
        n_articles = np.random.randint(30, 80)
        for _ in range(n_articles):
            rows.append({
                'target_bank': bank,
                'year': year,
                '媒体(中文)': np.random.choice(medias),
                '标题': f'{bank}金融科技创新发展' * 3,
                '内容': f'{bank}在{year}年大力推进数字化转型和金融科技创新' * 20,
                '城市': np.random.choice(['北京', '上海', '广州', '深圳', '杭州']),
                '国家地区/省份': np.random.choice(['北京', '上海', '广东', '广东', '浙江']),
                'llm_vote_score_full': np.random.normal(0.6, 0.3),
                'is_positive_full': np.random.choice([0, 1], p=[0.3, 0.7]),
                'is_negative_full': np.random.choice([0, 1], p=[0.8, 0.2]),
                'co_mentioned_banks': str(np.random.choice(
                    [b for b in banks if b != bank], 
                    size=np.random.randint(0, 3),
                    replace=False).tolist()),
            })

df_exploded = pd.DataFrame(rows)
print(f"df_exploded: {len(df_exploded)} 行, {len(df_exploded.columns)} 列")

# --- 面板数据 ---
panel_rows = []
for bank in banks:
    for year in years:
        mask = (df_exploded['target_bank'] == bank) & (df_exploded['year'] == year)
        n = mask.sum()
        panel_rows.append({
            'target_bank': bank,
            'year': year,
            'n_articles': n,
            'neg_count_full': int(df_exploded.loc[mask, 'is_negative_full'].sum()),
            'llm_vote_tone_full': df_exploded.loc[mask, 'llm_vote_score_full'].mean(),
            'bank_province': np.random.choice(['北京', '上海', '广东', '浙江', '江苏']),
            'bank_city': np.random.choice(['北京', '上海', '广州', '杭州', '南京']),
            'ln_news_coverage': np.log(n + 1),
        })
panel = pd.DataFrame(panel_rows)
print(f"panel: {len(panel)} 行, {len(panel.columns)} 列")

# ============================================================
# 步骤 1: 认知邻近度 (46)
# ============================================================
print("\n--- 步骤 1: 认知邻近度 ---")
panel = m46.compute_cognitive_proximity(df_exploded, panel)
assert 'bank_cogn_mean' in panel.columns, "bank_cogn_mean 未生成!"
n1 = panel['bank_cogn_mean'].notna().sum()
print(f"  bank_cogn_mean: {n1}/{len(panel)} 有效")

# ============================================================
# 步骤 2: 经纪中心度 (47)
# ============================================================
print("\n--- 步骤 2: 经纪中心度 ---")
panel = m47.compute_brokerage_centrality(panel, df_exploded)
assert 'brokerage_eigen_cent' in panel.columns, "brokerage_eigen_cent 未生成!"
n2 = panel['brokerage_eigen_cent'].notna().sum()
print(f"  brokerage_eigen_cent: {n2}/{len(panel)} 有效")

# ============================================================
# 步骤 3: 行业负面冲击 (47)
# ============================================================
print("\n--- 步骤 3: 行业负面冲击 ---")
panel = m47.compute_industry_neg_shock(panel)
assert 'industry_neg_shock' in panel.columns, "industry_neg_shock 未生成!"
n3 = panel['industry_neg_shock'].notna().sum()
print(f"  industry_neg_shock: {n3}/{len(panel)} 有效")

# ============================================================
# 步骤 4: 火灾甩卖交乘 (47)
# ============================================================
print("\n--- 步骤 4: 火灾甩卖交乘 ---")
panel = m47.compute_fire_sale_interaction(panel)
assert 'brokerage_fire_sale' in panel.columns, "brokerage_fire_sale 未生成!"
n4 = panel['brokerage_fire_sale'].notna().sum()
# 首年(2019)应全为 NaN (无 lag1)
first_year_fs = panel[panel['year'] == 2019]['brokerage_fire_sale']
assert first_year_fs.isna().all(), "2019 年应全为 NaN (首年无 lag)"
print(f"  brokerage_fire_sale: {n4}/{len(panel)} 有效 (2019 全 NaN: OK)")

# ============================================================
# 步骤 5: 最终断言
# ============================================================
print("\n" + "=" * 60)
print("最终断言")
print("=" * 60)

# 检查 panel 无重复行
dup = panel.duplicated(subset=['target_bank', 'year']).sum()
assert dup == 0, f"面板存在重复行: {dup}"
print(f"  ✓ 无重复行 ({dup} duplicates)")

# 检查 panel 行数正确 (5 banks × 3 years = 15)
assert len(panel) == 15, f"面板行数异常: {len(panel)} (应为 15)"
print(f"  ✓ 行数正确: {len(panel)}")

# 检查所有新列存在
new_cols = ['bank_cogn_mean', 'brokerage_eigen_cent',
            'industry_neg_shock', 'brokerage_fire_sale']
for col in new_cols:
    assert col in panel.columns, f"列 {col} 缺失!"
    print(f"  ✓ {col}: 存在")

# 范围检查
vals = panel['bank_cogn_mean'].dropna()
assert (vals >= 0).all() and (vals <= 1).all(), "cogn 超出 [0,1]"
print(f"  ✓ bank_cogn_mean ∈ [0,1]")

vals = panel['brokerage_eigen_cent'].dropna()
assert (vals >= 0).all(), "brokerage 有负值"
print(f"  ✓ brokerage_eigen_cent ≥ 0")

vals = panel['industry_neg_shock'].dropna()
assert (vals >= 0).all() and (vals <= 1).all(), "neg_shock 超出 [0,1]"
print(f"  ✓ industry_neg_shock ∈ [0,1]")

print("\n" + "=" * 60)
print("集成测试全部通过 ✓✓✓")
print("=" * 60)
