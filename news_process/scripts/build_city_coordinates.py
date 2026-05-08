"""
build_city_coordinates.py — 城市地理坐标构建脚本
=================================================

管线位置:
  本脚本为离线预处理工具, 仅在配置变更时手动运行一次。
  其输出文件 (city_coordinates.json, province_capital_map.json)
  被 43_panel_indicators_geography.py 在运行时加载, 用于:
  - Haversine 距离计算 (28 种距离缓冲指标)
  - 区域 AI 模仿压力计算 (6 层 LOO 指标)
  - 省会退化策略 (媒体城市无坐标时使用省会坐标替代)

功能:
  从高德地图官方经纬度数据 (config/经纬度_全国各地区_高德地图.xlsx) 提取
  地级市/直辖市坐标, 与 bank_addresses.json 中的银行注册城市匹配,
  输出 config/city_coordinates.json 供距离计算使用。

匹配策略 (三级, 确保 100% 覆盖率):
  Level 1 精确匹配: 清洗后城市名 完全一致 (如 '石家庄' == '石家庄')
  Level 2 子串匹配: 处理自治州简称 (如 '恩施' ⊂ '恩施土家族苗族自治州')
  Level 3 手工映射: 特殊城市映射至最近地级市 (如 '北屯' → '阿勒泰')

输入:
  - config/经纬度_全国各地区_高德地图.xlsx (3445 行, 高德官方)
  - config/bank_addresses.json (1768 家银行, 329 个唯一城市)

输出:
  - config/city_coordinates.json
    格式: {"城市名": {"lat": float, "lon": float}, ...}
  - config/province_capital_map.json
    格式: {"省份名(清洗后)": "省会城市名(清洗后)", ...}
    用途: 43_panel_indicators_geography.py 中媒体城市无坐标时的退化策略

学术依据:
  Coval, J. D., & Moskowitz, T. J. (1999). Home bias at home: Local
  equity preference in domestic portfolios. The Journal of Finance,
  54(6), 2045-2073. DOI: 10.1111/0022-1082.00181
  → 多距离阈值方法论需要精确的城市级坐标

  Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype:
  Local media slant, local advertising, and firm value. The Journal
  of Finance, 67(2), 561-598. DOI: 10.1111/j.1540-6261.2012.01725.x
  → 本地媒体偏向的地理距离操作化基础

运行:
  python scripts/build_city_coordinates.py
"""

import os
import re
import sys
import json

sys.stdout.reconfigure(encoding='utf-8')

import pandas as pd

# ============================================================================
# 路径配置
# ============================================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(PROJECT_DIR, 'config')

EXCEL_PATH = os.path.join(CONFIG_DIR, '经纬度_全国各地区_高德地图.xlsx')
BANK_ADDR_PATH = os.path.join(CONFIG_DIR, 'bank_addresses.json')
OUTPUT_PATH = os.path.join(CONFIG_DIR, 'city_coordinates.json')
CAPITAL_MAP_PATH = os.path.join(CONFIG_DIR, 'province_capital_map.json')

# ============================================================================
# 地名后缀清洗 (复用 42_panel_attention_media.py L747-754 逻辑)
# ============================================================================

_GEO_SUFFIXES = re.compile(
    r'省|市|维吾尔自治区|回族自治区|壮族自治区|自治区|特别行政区|地区|林区'
)


def clean_geo(name: str) -> str:
    """移除行政区划后缀, 标准化城市/省份名称。

    示例:
      '北京市' → '北京'  | '河北省' → '河北'
      '新疆维吾尔自治区' → '新疆'  | '内蒙古自治区' → '内蒙古'
      '恩施土家族苗族自治州' → 不变 (正则不匹配自治州)

    复用自 pipeline/panel/geography.py 的 _GEO_SUFFIXES_DIST 逻辑
    (Phase 2a 起从 43_panel_indicators_geography.py 迁出).
    """
    return _GEO_SUFFIXES.sub('', str(name)).strip()


# ============================================================================
# 主逻辑
# ============================================================================

def main():
    print("=" * 60)
    print("城市地理坐标构建脚本")
    print("=" * 60)

    # 1. 读取高德 Excel
    if not os.path.exists(EXCEL_PATH):
        print(f"ERROR: {EXCEL_PATH} 不存在!")
        sys.exit(1)

    df = pd.read_excel(EXCEL_PATH)
    df['code_str'] = df['行政区划代码'].astype(str).str.zfill(6)
    print(f"高德数据: {len(df)} 行, 列: {df.columns.tolist()}")

    # 2. 提取多层级坐标

    # 2a. 省级 (直辖市): code 末4位=0000
    province_level = df[df['code_str'].str[-4:] == '0000'].copy()
    print(f"省级记录: {len(province_level)} (含 4 直辖市)")

    # 2b. 地级市: code 末2位=00, 末4位!=0000
    prefecture_level = df[
        (df['code_str'].str[-2:] == '00') &
        (df['code_str'].str[-4:] != '0000')
    ].copy()
    print(f"地级市记录: {len(prefecture_level)}")

    # 2c. 县级市 (省直辖): 直接从全表搜索特殊城市名
    # 仙桃、天门、潜江、神农架(湖北)、济源(河南)、北屯(新疆兵团)
    SPECIAL_CITIES = {'仙桃', '天门', '潜江', '神农架', '济源', '北屯'}

    # 3. 构建坐标字典 (清洗后城市名 → 坐标)
    coord_dict = {}  # {clean_name: (lat, lon, raw_name)}

    # 3a. 省级 (直辖市) — 同时作为省会
    for _, row in province_level.iterrows():
        name_clean = clean_geo(row['城市'])
        coord_dict[name_clean] = (row['纬度'], row['经度'], row['城市'])

    # 3b. 地级市
    for _, row in prefecture_level.iterrows():
        name_clean = clean_geo(row['城市'])
        if name_clean not in coord_dict:  # 不覆盖直辖市
            coord_dict[name_clean] = (row['纬度'], row['经度'], row['城市'])

    # 3c. 特殊城市 (从全表中精确查找)
    for _, row in df.iterrows():
        name_clean = clean_geo(row['城市'])
        if name_clean in SPECIAL_CITIES and name_clean not in coord_dict:
            coord_dict[name_clean] = (row['纬度'], row['经度'], row['城市'])

    print(f"坐标字典: {len(coord_dict)} 个条目")

    # 4. 加载 bank_addresses.json
    if not os.path.exists(BANK_ADDR_PATH):
        print(f"ERROR: {BANK_ADDR_PATH} 不存在!")
        sys.exit(1)

    with open(BANK_ADDR_PATH, 'r', encoding='utf-8') as f:
        bank_addr = json.load(f)

    bank_cities = set()
    for info in bank_addr.values():
        c = info.get('city', '').strip()
        if c:
            bank_cities.add(c)
    print(f"bank_addresses 唯一城市: {len(bank_cities)}")

    # 5. 匹配 (三级: 精确 → 子串 → 手工映射)

    # 手工映射表 (高德数据中不存在或名称差异较大的城市)
    MANUAL_MAP = {
        # 新疆兵团城市 — 使用最近地级市坐标 (兵团城市无独立行政代码)
        '北屯': '阿勒泰',  # 北屯市隶属新疆兵团第十师, 靠近阿勒泰市
        # 如未来新增银行的注册地在高德数据中不存在, 在此添加映射
    }

    output = {}
    matched_exact = 0
    matched_substr = 0
    matched_manual = 0
    unmatched = []

    for city in sorted(bank_cities):
        city_clean = clean_geo(city)

        # Level 1: 精确匹配
        if city_clean in coord_dict:
            lat, lon, _ = coord_dict[city_clean]
            output[city] = {'lat': float(lat), 'lon': float(lon)}
            matched_exact += 1
            continue

        # Level 2: 子串匹配 (处理自治州简称)
        found = False
        for pref_name, (lat, lon, _) in coord_dict.items():
            if city_clean in pref_name or pref_name in city_clean:
                output[city] = {'lat': float(lat), 'lon': float(lon)}
                matched_substr += 1
                found = True
                break
        if found:
            continue

        # Level 3: 手工映射
        if city_clean in MANUAL_MAP:
            target = MANUAL_MAP[city_clean]
            if target in coord_dict:
                lat, lon, _ = coord_dict[target]
                output[city] = {'lat': float(lat), 'lon': float(lon)}
                matched_manual += 1
                continue

        unmatched.append(city)

    # 6. 诊断
    total = len(bank_cities)
    print(f"\n匹配结果:")
    print(f"  精确匹配: {matched_exact}/{total}")
    print(f"  子串匹配: {matched_substr}/{total}")
    print(f"  手工映射: {matched_manual}/{total}")
    print(f"  总计匹配: {len(output)}/{total} "
          f"({len(output)/total:.1%})")

    if unmatched:
        print(f"\n未匹配 ({len(unmatched)}):")
        for c in unmatched:
            print(f"  {c}")

    # 7. 构建省→省会映射表 (用于媒体城市缺失时的退化策略)
    # 策略:
    #   - 直辖市 (省级条目中 省份==城市): 直接映射到自身
    #   - 普通省份: 从地级市条目中取第一条 (高德按行政代码排序, 首条即省会)
    #   注意: 高德 Excel 的省级条目中, 所有省份的"城市"列存储的是
    #   省名而非省会名 (如 河北省→河北, 不是→石家庄), 所以
    #   只有直辖市的省级条目才能直接使用。
    MUNICIPALITIES = {'北京', '天津', '上海', '重庆'}
    province_capital = {}
    seen_provinces = set()

    # 直辖市: 省份=城市=省会 (清洗后: 北京→北京)
    for _, row in province_level.iterrows():
        prov_clean = clean_geo(row['省份'])
        city_clean = clean_geo(row['城市'])
        if prov_clean in MUNICIPALITIES:
            province_capital[prov_clean] = city_clean
            seen_provinces.add(prov_clean)

    # 地级市: 每省第一个即省会 (高德数据按行政区划代码排序)
    for _, row in prefecture_level.iterrows():
        prov_clean = clean_geo(row['省份'])
        city_clean = clean_geo(row['城市'])
        if prov_clean not in seen_provinces:
            province_capital[prov_clean] = city_clean
            seen_provinces.add(prov_clean)

    print(f"\n省→省会映射: {len(province_capital)} 个省份")

    # 8. 保存
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\n已保存: {OUTPUT_PATH} ({len(output)} 条)")

    with open(CAPITAL_MAP_PATH, 'w', encoding='utf-8') as f:
        json.dump(province_capital, f, ensure_ascii=False, indent=2)
    print(f"已保存: {CAPITAL_MAP_PATH} ({len(province_capital)} 条)")

    # 9. 最终断言
    assert len(output) == total, \
        f"覆盖率不足: {len(output)}/{total}"
    print(f"\n✓ 覆盖率断言通过: {len(output)}/{total} = 100%")


if __name__ == '__main__':
    main()
