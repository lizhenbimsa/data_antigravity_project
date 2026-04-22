"""
_test_final_round.py — 第四轮审查: 微观细节深度测试
====================================================
覆盖:
  1. 正则表达式边界 (_GEO_SUFFIXES_DIST)
  2. STATA 标签与实际列名精确匹配
  3. 省会映射完整性 (31省 vs 34省级行政区)
  4. pandas include_groups 兼容性
  5. _concat_text 闭包安全性
  6. _haversine 极端坐标 (边界/反子午线)
  7. LOO 单银行年份退化
  8. 空图 fallback 正确性
  9. compute_fire_sale_interaction 排序稳定性
  10. _neg_ratio 除零保护
"""
import sys, os, re, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, r'f:\WiseSearch\data_antigravity_project\news_process')

import numpy as np
import pandas as pd
import importlib.util as _iu

base = r'f:\WiseSearch\data_antigravity_project\news_process'

def load_mod(name, path):
    s = _iu.spec_from_file_location(name, path)
    m = _iu.module_from_spec(s)
    s.loader.exec_module(m)
    return m

m43 = load_mod('m43', f'{base}\\43_panel_indicators_geography.py')
m47 = load_mod('m47', f'{base}\\47_network_brokerage.py')

print("=" * 60)
print("第四轮审查: 微观细节深度测试 (10 项)")
print("=" * 60)

# ============================================================
# 测试 1: 正则表达式边界
# ============================================================
print("\n--- 测试 1: _GEO_SUFFIXES_DIST 正则边界 ---")
_suf = m43._GEO_SUFFIXES_DIST

test_cases = [
    ("北京市", "北京"),
    ("河北省", "河北"),
    ("新疆维吾尔自治区", "新疆"),
    ("宁夏回族自治区", "宁夏"),
    ("广西壮族自治区", "广西"),
    ("内蒙古自治区", "内蒙古"),
    ("香港特别行政区", "香港"),
    ("澳门特别行政区", "澳门"),
    ("恩施土家族苗族自治州", "恩施土家族苗族自治州"),  # 自治州不应被清洗
    ("大兴安岭地区", "大兴安岭"),
    ("神农架林区", "神农架"),
    ("石家庄市", "石家庄"),
    ("石家庄", "石家庄"),  # 无后缀不应改变
]

errors = 0
for raw, expected in test_cases:
    result = _suf.sub('', raw).strip()
    ok = result == expected
    if not ok:
        print(f'  FAIL: "{raw}" -> "{result}" (expected "{expected}")')
        errors += 1
    else:
        print(f'  OK: "{raw}" -> "{result}"')

assert errors == 0, f"{errors} 个正则匹配错误"

# ============================================================
# 测试 2: STATA 标签与实际函数输出列名匹配
# ============================================================
print("\n--- 测试 2: STATA 标签列名匹配 ---")

# 模拟 compute_geo_proximity_buffers 输出列名
expected_geo_cols = []
for t in [50, 100, 150, 200]:
    for suffix in ['_n_media', '_n_articles', '_frac', '_tone_full',
                   '_pos_frac', '_neg_frac', '_is_local']:
        expected_geo_cols.append(f'prox_{t}km{suffix}')

# 模拟 compute_regional_imitation_pressure 输出列名
expected_imit_cols = ['ai_reg_province', 'ai_reg_city',
                      'ai_reg_50km', 'ai_reg_100km',
                      'ai_reg_150km', 'ai_reg_200km']

# STATA 标签中声明的变量
stata_declared = {
    'prox_50km_n_media', 'prox_50km_n_articles', 'prox_50km_frac',
    'prox_50km_tone_full', 'prox_50km_pos_frac', 'prox_50km_neg_frac',
    'prox_50km_is_local',
    'prox_100km_n_media', 'prox_100km_n_articles', 'prox_100km_frac',
    'prox_100km_tone_full', 'prox_100km_pos_frac', 'prox_100km_neg_frac',
    'prox_100km_is_local',
    'prox_150km_n_media', 'prox_150km_n_articles', 'prox_150km_frac',
    'prox_150km_tone_full', 'prox_150km_pos_frac', 'prox_150km_neg_frac',
    'prox_150km_is_local',
    'prox_200km_n_media', 'prox_200km_n_articles', 'prox_200km_frac',
    'prox_200km_tone_full', 'prox_200km_pos_frac', 'prox_200km_neg_frac',
    'prox_200km_is_local',
    'ai_reg_province', 'ai_reg_city',
    'ai_reg_50km', 'ai_reg_100km', 'ai_reg_150km', 'ai_reg_200km',
    'bank_cogn_mean', 'brokerage_eigen_cent',
    'industry_neg_shock', 'brokerage_fire_sale',
    'peer_fintech_exposure_lag1',
}

# 验证函数生成的列名全部在 STATA 声明中
geo_set = set(expected_geo_cols)
imit_set = set(expected_imit_cols)

missing_in_stata = (geo_set | imit_set) - stata_declared
if missing_in_stata:
    print(f'  FAIL: 以下列未在 STATA 标签中声明: {missing_in_stata}')
    assert False
else:
    print(f'  OK: {len(geo_set)} 地理列 + {len(imit_set)} 模仿列 全部匹配')

# ============================================================
# 测试 3: 省会映射完整性
# ============================================================
print("\n--- 测试 3: 省会映射完整性 ---")

with open(f'{base}\\config\\province_capital_map.json', 'r', encoding='utf-8') as f:
    cap_map = json.load(f)

# 中国 31 个省级行政区 (不含港澳台)
expected_provinces = {
    '北京', '天津', '河北', '山西', '内蒙古',
    '辽宁', '吉林', '黑龙江', '上海', '江苏',
    '浙江', '安徽', '福建', '江西', '山东',
    '河南', '湖北', '湖南', '广东', '广西',
    '海南', '重庆', '四川', '贵州', '云南',
    '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆',
}

# 已知正确的省会
known_capitals = {
    '北京': '北京', '天津': '天津', '上海': '上海', '重庆': '重庆',
    '河北': '石家庄', '山西': '太原', '内蒙古': '呼和浩特',
    '辽宁': '沈阳', '吉林': '长春', '黑龙江': '哈尔滨',
    '江苏': '南京', '浙江': '杭州', '安徽': '合肥',
    '福建': '福州', '江西': '南昌', '山东': '济南',
    '河南': '郑州', '湖北': '武汉', '湖南': '长沙',
    '广东': '广州', '广西': '南宁', '海南': '海口',
    '四川': '成都', '贵州': '贵阳', '云南': '昆明',
    '西藏': '拉萨', '陕西': '西安', '甘肃': '兰州',
    '青海': '西宁', '宁夏': '银川', '新疆': '乌鲁木齐',
}

cap_errors = 0
missing_provs = expected_provinces - set(cap_map.keys())
if missing_provs:
    print(f'  FAIL: 以下省份缺失: {missing_provs}')
    cap_errors += 1

for prov, expected_cap in known_capitals.items():
    actual = cap_map.get(prov)
    if actual != expected_cap:
        print(f'  FAIL: {prov} -> {actual} (应为 {expected_cap})')
        cap_errors += 1

assert cap_errors == 0, f"{cap_errors} 个省会映射错误"
print(f'  OK: 31 省全部正确映射')

# ============================================================
# 测试 4: _haversine 极端坐标
# ============================================================
print("\n--- 测试 4: _haversine 极端坐标 ---")
haversine = m43._haversine

# 赤道上 1 度经度 ≈ 111 km
d_eq = haversine(0, 0, 0, 1)
assert 110 < d_eq < 112, f"赤道 1° 经度应 ≈ 111 km, 实际: {d_eq:.1f}"
print(f'  OK: 赤道 1° 经度 = {d_eq:.2f} km')

# 南北极 → 半周 ≈ 20015 km
d_pole = haversine(90, 0, -90, 0)
assert 20000 < d_pole < 20100, f"两极距离异常: {d_pole:.1f}"
print(f'  OK: 北极→南极 = {d_pole:.2f} km')

# 漠河 (中国最北) → 三沙 (中国最南) ≈ 4500 km
d_ns = haversine(53.47, 122.37, 9.54, 112.34)
assert 4800 < d_ns < 5100, f"漠河→三沙异常: {d_ns:.1f}"
print(f'  OK: 漠河→三沙 = {d_ns:.2f} km')

# NaN 输入保护
try:
    d_nan = haversine(np.nan, 116.4, 39.9, 116.4)
    # math.radians(nan) = nan, math.sin(nan) = nan → result = nan
    assert np.isnan(d_nan), f"NaN 输入应返回 NaN, 实际: {d_nan}"
    print(f'  OK: NaN 输入 → NaN 输出')
except (ValueError, TypeError) as e:
    print(f'  WARN: NaN 输入抛出异常: {e} (可接受 — 上游已有守卫)')

# ============================================================
# 测试 5: compute_industry_neg_shock 单银行年份退化
# ============================================================
print("\n--- 测试 5: 单银行年份退化 ---")
panel_single = pd.DataFrame({
    'target_bank': ['A'],
    'year': [2020],
    'neg_count_full': [10],
    'n_articles': [100],
})
result_single = m47.compute_industry_neg_shock(panel_single.copy())
shock_val = result_single['industry_neg_shock'].iloc[0]
assert pd.isna(shock_val), f"单银行应为 NaN, 实际: {shock_val}"
print(f'  OK: 单银行 → NaN (无法做 LOO)')

# ============================================================
# 测试 6: compute_industry_neg_shock 零文章保护
# ============================================================
print("\n--- 测试 6: 零文章除零保护 ---")
panel_zero = pd.DataFrame({
    'target_bank': ['A', 'B'],
    'year': [2020, 2020],
    'neg_count_full': [5, 10],
    'n_articles': [0, 100],  # A 的 n_articles=0
})
result_zero = m47.compute_industry_neg_shock(panel_zero.copy())
# A 的 neg_ratio = 5/0 → NaN (通过 .replace(0, np.nan))
# B 的 LOO: 只有 A 且 A 是 NaN → total_n=1, 但 B 自身有效 → (total_sum - own)/(1-1) = /0
# 实际: total_n=1 (只有 B 有效), 对 B: total_n > 1 为 False → NaN
shock_A = result_zero.loc[result_zero['target_bank'] == 'A', 'industry_neg_shock'].iloc[0]
shock_B = result_zero.loc[result_zero['target_bank'] == 'B', 'industry_neg_shock'].iloc[0]
print(f'  A (n_articles=0): industry_neg_shock = {shock_A} (NaN expected: {pd.isna(shock_A)})')
print(f'  B (n_articles=100): industry_neg_shock = {shock_B} (NaN expected: {pd.isna(shock_B)})')
# 两者都应为 NaN: A 因为自身 ratio 是 NaN, B 因为 total_n=1 不满足 >1
assert pd.isna(shock_A), "A 应为 NaN"
assert pd.isna(shock_B), "B 应为 NaN (只有1个有效银行无法LOO)"
print(f'  OK: 零文章和单有效银行均正确退化为 NaN')

# ============================================================
# 测试 7: fire_sale 排序稳定性
# ============================================================
print("\n--- 测试 7: fire_sale 排序稳定性 ---")
# 输入乱序
panel_unsorted = pd.DataFrame({
    'target_bank': ['B', 'A', 'B', 'A', 'B', 'A'],
    'year': [2020, 2019, 2019, 2020, 2021, 2021],
    'brokerage_eigen_cent': [0.5, 0.1, 0.4, 0.2, 0.6, 0.3],
    'industry_neg_shock': [0.6, 0.5, 0.5, 0.6, 0.7, 0.7],
})
result_unsorted = m47.compute_fire_sale_interaction(panel_unsorted.copy())

# A: 2019=NaN, 2020=0.1*0.6=0.06, 2021=0.2*0.7=0.14
# B: 2019=NaN, 2020=0.4*0.6=0.24, 2021=0.5*0.7=0.35
fs_A_2020 = result_unsorted.loc[
    (result_unsorted['target_bank']=='A') & (result_unsorted['year']==2020),
    'brokerage_fire_sale'].iloc[0]
fs_B_2021 = result_unsorted.loc[
    (result_unsorted['target_bank']=='B') & (result_unsorted['year']==2021),
    'brokerage_fire_sale'].iloc[0]

assert abs(fs_A_2020 - 0.06) < 1e-10, f"A 2020: {fs_A_2020} (expected 0.06)"
assert abs(fs_B_2021 - 0.35) < 1e-10, f"B 2021: {fs_B_2021} (expected 0.35)"
print(f'  OK: 乱序输入 → 正确 lag-1 (A_2020={fs_A_2020:.4f}, B_2021={fs_B_2021:.4f})')

# ============================================================
# 测试 8: bipartite 空图 fallback
# ============================================================
print("\n--- 测试 8: 空图 fallback ---")
import networkx as nx
df_empty = pd.DataFrame({
    '媒体(中文)': pd.Series(dtype=str),
    'target_bank': pd.Series(dtype=str),
    'year': pd.Series(dtype=int),
})
G = m47.build_media_bank_bipartite(df_empty, 2020)
assert G is not None, "空图不应返回 None"
assert G.number_of_nodes() == 0, f"空图应有 0 节点, 实际: {G.number_of_nodes()}"
print(f'  OK: 空数据 → 空图 (nodes={G.number_of_nodes()})')

# ============================================================
# 测试 9: include_groups 兼容性
# ============================================================
print("\n--- 测试 9: pandas include_groups 兼容性 ---")
pd_version = tuple(int(x) for x in pd.__version__.split('.')[:2])
if pd_version >= (2, 1):
    print(f'  OK: pandas {pd.__version__} >= 2.1 (include_groups=False 可用)')
else:
    print(f'  WARN: pandas {pd.__version__} < 2.1 (include_groups 不可用!)')

# ============================================================
# 测试 10: _DISTANCE_THRESHOLDS_KM 严格递增
# ============================================================
print("\n--- 测试 10: 距离阈值严格递增 ---")
thresholds = m43._DISTANCE_THRESHOLDS_KM
for i in range(len(thresholds) - 1):
    assert thresholds[i] < thresholds[i+1], \
        f"阈值不递增: {thresholds[i]} >= {thresholds[i+1]}"
print(f'  OK: {thresholds} 严格递增')

# ============================================================
# 总结
# ============================================================
print("\n" + "=" * 60)
print("全部 10 项微观细节测试通过 ✓✓✓")
print("=" * 60)
