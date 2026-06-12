"""scripts/generate_bank_list_from_addresses.py — bank_list.yaml 从 bank_addresses.json
自动派生 (v3.7.0 user task 3, 2026-05-18).

设计原则
--------
- 单一可信源 = ``news_process/config/bank_addresses.json`` (1768 行, NFRA 官方银行清单)
- bank_list.yaml 为 derived artifact, 跑此脚本同步
- 派生规则 frozen 在本脚本中 (审计 trail)
- D-SIB list + 政策性银行 (3 家) 手动补充, 因 bank_addresses.json 不含

映射规则 (nfra_type → bank_type_id, implicit_guarantee_tier)
----------------------------------------------------------
| nfra_type        | bank_type_id | tier_default | is_soe_default |
|------------------|--------------|--------------|----------------|
| 国有大型商业银行  | 1            | 5            | true           |
| 股份制商业银行    | 2            | 3 (4 if DSIB)| false          |
| 城市商业银行      | 3            | 2 (3 if listed)| false        |
| 农村商业银行      | 4            | 1            | false          |
| 民营银行          | 5            | 1            | false          |
| 外资法人银行      | 6            | 1            | false          |
| (政策性, 手动补)  | 7            | 5            | true           |
| 直销银行 / 中央  | 8            | 5 (央行) / 1  | true (央行)/false |

Listed 判断
-----------
- bank_addresses.json 的 wind_code 是机构 code (F010/F020xxxx), 不是股票 ticker.
- 因此 listed 判断改为 hardcode LISTED_BANKS_2024_Q4 set
  (含 A 股 / H 股 / 美股已上市的 ~44 银行 frozen at 2024-Q4)

D-SIB list (银保监 2024-Q4 frozen)
---------------------------------
招商 / 兴业 / 上海浦东发展 / 中信 / 中国民生 (5 家股份制 tier 升级到 4)

政策性银行 (3 家, bank_addresses.json 无, 手动加)
----------------------------------------------
国家开发银行 / 中国进出口银行 / 中国农业发展银行

输出
----
news_process/config/bank_list.yaml (覆盖现有, 但保留 metadata + tier_definitions section)
"""
from __future__ import annotations

import json
from pathlib import Path

# D-SIB 2024-Q4 名单 (NFRA 公告; tier 4)
D_SIB_2024_Q4: set[str] = {
    '招商银行',
    '兴业银行',
    '上海浦东发展银行',  # = 浦发
    '中信银行',
    '中国民生银行',  # = 民生
}

# A/H/美股上市银行 frozen at 2024-Q4 (NFRA + 沪深 + 港交所 + 美股)
# bank_addresses.json 的 wind_code 是机构 code 非 ticker, 故 listed 必须 hardcode.
# 来源: 交易所披露 + Wind 银行库 cross-check (2024-Q4 list).
# 命名严格与 bank_addresses.json key 一致 (e.g., 浦发=上海浦东发展银行).
LISTED_BANKS_2024_Q4: set[str] = {
    # 6 国有大型 (全 A+H 上市)
    '中国工商银行', '中国农业银行', '中国银行', '中国建设银行',
    '交通银行', '中国邮政储蓄银行',
    # 9 股份制上市 (12 中: 广发/恒丰 非上市; 渤海仅 H 股)
    '招商银行', '兴业银行', '上海浦东发展银行', '中信银行',
    '中国民生银行', '中国光大银行', '华夏银行', '平安银行',
    '浙商银行', '渤海银行',  # 渤海 9668.HK
    # 18 上市城市商业银行 (A 股 + H 股)
    '北京银行', '上海银行', '江苏银行', '南京银行', '宁波银行',
    '杭州银行', '成都银行', '长沙银行', '贵阳银行', '郑州银行',
    '重庆银行', '齐鲁银行', '西安银行', '厦门银行', '苏州银行',
    '青岛银行', '兰州银行', '天津银行',  # 天津 1578.HK
    # 10 上市农村商业银行 (命名严格匹配 bank_addresses.json key)
    '重庆农村商业银行', '无锡农村商业银行',
    '江苏常熟农村商业银行', '江苏江阴农村商业银行',
    '江苏苏州农村商业银行', '江苏紫金农村商业银行',
    '青岛农村商业银行', '上海农村商业银行',
    '浙江绍兴瑞丰农村商业银行',
    '江苏张家港农村商业银行',
}

# 政策性银行 (bank_addresses.json 无, 手动补; 3 家)
POLICY_BANKS: list[dict] = [
    {
        'target_bank': '国家开发银行',
        'province': '北京', 'wind_code': None,
        'nfra_type': '政策性银行',
    },
    {
        'target_bank': '中国进出口银行',
        'province': '北京', 'wind_code': None,
        'nfra_type': '政策性银行',
    },
    {
        'target_bank': '中国农业发展银行',
        'province': '北京', 'wind_code': None,
        'nfra_type': '政策性银行',
    },
]

# nfra_type → (bank_type_id, default_tier, default_is_soe)
NFRA_TYPE_MAP: dict[str, tuple[int, int, bool]] = {
    '国有大型商业银行': (1, 5, True),
    '股份制商业银行':   (2, 3, False),  # D-SIB 则升 tier 4
    '城市商业银行':     (3, 2, False),  # 上市则升 tier 3
    '农村商业银行':     (4, 1, False),
    '民营银行':         (5, 1, False),
    '外资法人银行':     (6, 1, False),
    '政策性银行':       (7, 5, True),
    '直销银行':         (8, 1, False),
    '中央银行':         (8, 5, True),   # PBC, 不进 commercial panel
}


def is_listed_from_hardcode(name: str) -> bool:
    """A/H/U 股已上市判断 (基于 LISTED_BANKS_2024_Q4 frozen set).

    Note: bank_addresses.json::wind_code 是 NFRA 机构 code (F010xxxx),
    不是股票 ticker, 故不能用后缀判断, 必须 hardcode 上市清单.
    """
    return name in LISTED_BANKS_2024_Q4


def derive_bank_record(name: str, addr_info: dict) -> dict:
    """从 bank_addresses.json 一条 entry 派生 bank_list.yaml record.

    M3 修复 (audit V2): unknown nfra_type 不再 silent fallback,
    raise ValueError 强制开发者明确决定如何分类新类型.
    M6 修复 (audit V2): 央行加 is_commercial_bank=false 标记,
    防止下游 panel / Stata 模板误把央行纳入商业银行回归.
    (注: 修复当时所指的下游 stage 49 risk_taking_outcomes 已于 2026-06-12 整体移除,
    is_commercial_bank 标记本身仍为通用过滤依据, 保留有效。)
    """
    nfra_type = addr_info.get('nfra_type', '')
    wind_code = addr_info.get('wind_code') or None
    if wind_code == '':
        wind_code = None

    if nfra_type not in NFRA_TYPE_MAP:
        raise ValueError(
            f"Unknown nfra_type {nfra_type!r} for bank {name!r}. "
            f"Add to NFRA_TYPE_MAP at scripts/generate_bank_list_from_addresses.py. "
            f"Known types: {sorted(NFRA_TYPE_MAP.keys())}"
        )
    type_id, tier, is_soe = NFRA_TYPE_MAP[nfra_type]

    listed = is_listed_from_hardcode(name)

    # tier override: D-SIB 股份制 → tier 4
    if name in D_SIB_2024_Q4:
        tier = 4

    # tier override: 城商行上市 → tier 3
    if type_id == 3 and listed:
        tier = 3

    # M6 修复: 标记是否为商业银行 (下游 panel 过滤用)
    # 中国人民银行 = 央行, nfra_type='中央银行', bank_type_id=8
    is_commercial_bank = nfra_type != '中央银行'

    return {
        'target_bank': name,
        'is_soe': is_soe,
        'bank_type_id': type_id,
        'implicit_guarantee_tier': tier,
        'wind_code': wind_code,
        'listed': listed,
        'province': addr_info.get('province', ''),
        'nfra_type': nfra_type,
        'is_commercial_bank': is_commercial_bank,
    }


def render_yaml(banks: list[dict], n_total: int) -> str:
    """渲染 bank_list.yaml — 紧凑 flow style (1 行 per bank)."""
    header = f"""# news_process/config/bank_list.yaml
# ──────────────────────────────────────────────────────────────────────────
# Bank panel master list — derived from bank_addresses.json (NFRA 1768 银行)
# + 政策性银行 3 家手动补充 + D-SIB list 2024-Q4 frozen.
#
# v3.7.0 user task 3 (2026-05-18): 严格按照 bank_addresses.json 执行.
# 重新生成: python scripts/generate_bank_list_from_addresses.py
#
# 单一可信源:
#   bank_addresses.json (1768 行 NFRA 官方清单) → 自动派生 1768 行
#   POLICY_BANKS (脚本内 3 家政策性) → 手动加 3 行
#   总计: {n_total} 行
#
# Schema (per bank):
#   target_bank: 中文全称 (与 bank_addresses.json key 完全一致)
#   is_soe: bool (国务院 / 财政部 / 汇金 控股 ≥ 50%)
#   is_commercial_bank: bool (排除央行; 下游 panel 过滤依据)  # M6 audit V2 修复
#   bank_type_id: int 1-8 (国有/股份/城商/农商/民营/外资/政策/其他)
#   implicit_guarantee_tier: int 1-5 (Acharya 2016 RFS 框架, 5=TBTF / 1=无)
#   wind_code: NFRA 机构 code (F010/F020xxxx 格式; 非股票 ticker. M5 audit warning)
#   listed: bool (A/H/U 股任一; 基于 LISTED_BANKS_2024_Q4 hardcode set)
#   province: 总部省份
#   nfra_type: NFRA 官方分类 (8 个 + 政策性)
#
# Tier 派生规则 (frozen in generate_bank_list_from_addresses.py):
#   tier 5: 国有大型商业银行 + 政策性银行 (绝对 TBTF)
#   tier 4: 股份制 ∩ D-SIB 2024-Q4 (招商/兴业/上海浦东发展/中信/中国民生)
#   tier 3: 其他股份制 + 上市城市商业银行
#   tier 2: 非上市城市商业银行
#   tier 1: 农商 + 民营 + 外资 + 直销
#
# D-SIB 2024-Q4 (NFRA 公告):
#   招商银行 / 兴业银行 / 上海浦东发展银行 / 中信银行 / 中国民生银行

metadata:
  version: "2.0.0"
  source: "bank_addresses.json (1768 NFRA) + 3 policy banks (manual)"
  frozen_date: "2024-Q4"
  generated_by: "scripts/generate_bank_list_from_addresses.py"
  total_banks: {n_total}
  d_sib_2024_q4:
    - 招商银行
    - 兴业银行
    - 上海浦东发展银行
    - 中信银行
    - 中国民生银行

tier_definitions:
  5: "国有大型商业银行 + 政策性银行 (绝对 TBTF)"
  4: "D-SIB 股份制 (银保监 2024-Q4 list)"
  3: "其他股份制 + 上市城商行"
  2: "非上市城商行 (有地方政府背书)"
  1: "农商 + 民营 + 外资 + 直销"

bank_type_definitions:
  1: "国有大型商业银行"
  2: "股份制商业银行"
  3: "城市商业银行"
  4: "农村商业银行"
  5: "民营银行 / 互联网银行"
  6: "外资法人银行"
  7: "政策性银行"
  8: "其他 (直销 / 央行 / 未分类)"

# ─────────────────────────────────────────────────────────────────────────
# Bank entries (flow style for compactness; {n_total} 行)
# ─────────────────────────────────────────────────────────────────────────
banks:
"""
    lines = [header]
    for b in banks:
        # YAML flow style 单行, 中文字符串无需引号
        wind_str = f'"{b["wind_code"]}"' if b['wind_code'] else 'null'
        lines.append(
            f"  - {{target_bank: {b['target_bank']}, "
            f"is_soe: {str(b['is_soe']).lower()}, "
            f"is_commercial_bank: {str(b['is_commercial_bank']).lower()}, "
            f"bank_type_id: {b['bank_type_id']}, "
            f"implicit_guarantee_tier: {b['implicit_guarantee_tier']}, "
            f"wind_code: {wind_str}, "
            f"listed: {str(b['listed']).lower()}, "
            f"province: {b['province']}, "
            f"nfra_type: {b['nfra_type']}}}\n"
        )
    return ''.join(lines)


def main():
    project_root = Path(__file__).resolve().parents[2]
    addresses_path = project_root / 'news_process' / 'config' / 'bank_addresses.json'
    output_path = project_root / 'news_process' / 'config' / 'bank_list.yaml'

    with addresses_path.open('r', encoding='utf-8') as f:
        addresses = json.load(f)

    # 从 bank_addresses.json 派生 1768 条银行记录
    records: list[dict] = []
    for name, info in addresses.items():
        records.append(derive_bank_record(name, info))

    # 手动补充 3 家政策性银行 (bank_addresses.json 不含)
    for pb in POLICY_BANKS:
        records.append(derive_bank_record(pb['target_bank'], pb))

    # 排序: 国有大 → 政策性 → D-SIB 股份制 → 其他股份制 → 城商行 → 农商 → 民营 → 外资 → 直销 → 央行
    def _sort_priority(b: dict) -> tuple[int, str]:
        """v3.7.1 audit V2 m2 修复: lambda → def 提升可读性 + ruff PLW0108 合规."""
        type_to_priority = {
            1: 0,                                                # 国有大型
            7: 1,                                                # 政策性
            2: 2 if b['target_bank'] in D_SIB_2024_Q4 else 3,    # D-SIB / 普通股份
            3: 4 if b['listed'] else 5,                          # 上市城商 / 非上市城商
            4: 6,                                                # 农商
            5: 7,                                                # 民营
            6: 8,                                                # 外资
            8: 9,                                                # 直销 / 央行
        }
        return (type_to_priority.get(b['bank_type_id'], 10), b['target_bank'])

    records.sort(key=_sort_priority)

    yaml_text = render_yaml(records, len(records))
    output_path.write_text(yaml_text, encoding='utf-8')

    # 统计报告 (分类型/分 tier 计数)
    from collections import Counter
    type_counts = Counter(b['bank_type_id'] for b in records)
    tier_counts = Counter(b['implicit_guarantee_tier'] for b in records)
    listed_count = sum(1 for b in records if b['listed'])

    print(f"Generated: {output_path.relative_to(project_root)}")
    print(f"Total banks: {len(records)}")
    print(f"Listed: {listed_count}")
    print()
    print("Type distribution:")
    type_names = {1: '国有大型', 2: '股份制', 3: '城商', 4: '农商',
                  5: '民营', 6: '外资', 7: '政策性', 8: '其他/央行'}
    for tid, n in sorted(type_counts.items()):
        print(f"  type {tid} ({type_names[tid]}): {n}")
    print()
    print("Tier distribution:")
    for tier, n in sorted(tier_counts.items(), reverse=True):
        print(f"  tier {tier}: {n}")


if __name__ == '__main__':
    main()
