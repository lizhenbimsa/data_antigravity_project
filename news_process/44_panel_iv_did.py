"""
44_panel_iv_did.py — Bartik IV 与 DID 政策冲击
==========================================================

功能:
  - 银行分组映射加载 (load_bank_group_maps)
  - 通用 Bartik Shift-Share IV (compute_bartik_iv)
  - 文章属性维度 Bartik IV (compute_bartik_iv_fintech)
  - 经济圈 Leave-One-Out IV (compute_zone_leave1out)
  - DID 政策冲击变量合并 (merge_policy_shocks)

拆分自: 40_build_panel.py (L144-652)
学术依据:
  Goldsmith-Pinkham, Sorkin & Swift (2020, AER) — Bartik IV
  Callaway & Sant’Anna (2021, JoE) — Staggered DID
"""

import os
import json
import re
import importlib.util as _iu

import numpy as np
import pandas as pd

# --- 从 41 导入共享配置 ---
_p41 = os.path.join(os.path.dirname(__file__), '41_panel_encode_aggregate.py')
_s41 = _iu.spec_from_file_location('_41_mod', _p41)
_m41 = _iu.module_from_spec(_s41)
_s41.loader.exec_module(_m41)

logger = _m41.logger


# ============================================================================
# 2b. 银行分组映射加载 (Bartik IV 前置依赖)
# ============================================================================

def load_bank_group_maps() -> tuple:
    """从 bank_addresses.json 读取银行分组映射。

    Returns:
        type_map:  {银行名 → 'soe'/'joint'/'city'/'rural'/'private'/'foreign'/'other'}
        scale_map: {银行名 → 'L'/'M'/'S'/'XS'/'other'}
    """
    addr_path = os.path.join(os.path.dirname(__file__), 'config', 'bank_addresses.json')
    with open(addr_path, 'r', encoding='utf-8') as f:
        addresses = json.load(f)

    NFRA_TO_SHORT = {
        '国有大型商业银行': 'soe',
        '股份制商业银行':   'joint',
        '城市商业银行':     'city',
        '农村商业银行':     'rural',
        '民营银行':         'private',
        '外资法人银行':     'foreign',
    }
    SCALE_TO_SHORT = {
        'L(大型)': 'L', 'M(中型)': 'M', 'S(小型)': 'S', 'XS(微型)': 'XS',
    }

    type_map, scale_map = {}, {}
    for bank_name, info in addresses.items():
        type_map[bank_name] = NFRA_TO_SHORT.get(info.get('nfra_type', ''), 'other')
        scale_map[bank_name] = SCALE_TO_SHORT.get(info.get('enterprise_scale', ''), 'other')

    return type_map, scale_map


# ============================================================================
# 2c. 通用 Bartik Shift-Share IV 计算
#     学术依据:
#       [1] Goldsmith-Pinkham, Sorkin & Swift (2020, AER)
#           DOI: 10.1257/aer.20181047  — Share 视角: 基期份额外生性
#       [2] Borusyak, Hull & Jaravel (2022, RES)
#           DOI: 10.1093/restud/rdab030 — Shift 视角: 冲击准随机性
# ============================================================================

def compute_bartik_iv(panel: pd.DataFrame,
                      df_exploded: pd.DataFrame,
                      bank_group_map: dict,
                      group_prefix: str,
                      base_year: int = None) -> pd.DataFrame:
    """通用 Bartik Shift-Share IV 计算。

    参数:
        panel:          Bank-Year 面板
        df_exploded:    文章级数据 (含 target_bank, co_mentioned_banks)
        bank_group_map: {银行名 → 组别标签} (如 type_map 或 scale_map)
        group_prefix:   输出列名前缀 ('type' 或 'scale')
        base_year:      基期年份 (None = 面板最早年份)

    输出列:
        bartik_{prefix}_iv_full / _ctx         — Bartik IV 值
        bartik_{prefix}_share_{group}          — 基期份额
        bank_{prefix}                          — 银行分组标签

    索引安全: 全程 merge-based, 不依赖行序。
    """
    T0 = base_year if base_year is not None else panel['year'].min()
    groups = sorted(set(v for v in bank_group_map.values() if v != 'other'))
    logger.info(f"  Bartik IV [{group_prefix}]: 基期 T0={T0}, "
                f"组别={groups} ({len(groups)} 维)")

    # --- Step 1: 银行分组标签 ---
    panel[f'bank_{group_prefix}'] = (
        panel['target_bank'].map(bank_group_map).fillna('other')
    )

    # --- Step 2: 基期份额 (通过 co_mentioned_banks 计算跨组暴露) ---
    base = df_exploded[df_exploded['year'] == T0].copy()
    if len(base) == 0:
        logger.warning(f"  基期 T0={T0} 无数据, Bartik IV [{group_prefix}] 跳过")
        for track in ['_full', '_ctx']:
            panel[f'bartik_{group_prefix}_iv{track}'] = np.nan
        return panel

    def get_co_groups(co_banks_str):
        """从 co_mentioned_banks 提取涉及的组别。"""
        if not co_banks_str or str(co_banks_str).strip() in ('', 'nan'):
            return []
        banks = [b.strip() for b in str(co_banks_str).split(';') if b.strip()]
        return [bank_group_map.get(b, 'other') for b in banks]

    base['_co_groups'] = base['co_mentioned_banks'].apply(get_co_groups)

    # 计算每家银行在基期的跨组暴露份额
    all_banks = panel['target_bank'].unique()
    shares_data = []
    for bank in all_banks:
        bank_base = base[base['target_bank'] == bank]
        if len(bank_base) == 0:
            continue
        group_counts = {}
        for groups_list in bank_base['_co_groups']:
            for g in groups_list:
                if g != 'other':
                    group_counts[g] = group_counts.get(g, 0) + 1
        total = sum(group_counts.values())
        if total == 0:
            own_group = bank_group_map.get(bank, 'other')
            for g in groups:
                shares_data.append({
                    'target_bank': bank, 'group': g,
                    'share': 1.0 if g == own_group else 0.0
                })
        else:
            for g in groups:
                shares_data.append({
                    'target_bank': bank, 'group': g,
                    'share': group_counts.get(g, 0) / total
                })

    shares_df = pd.DataFrame(shares_data)

    for g in groups:
        g_shares = shares_df[shares_df['group'] == g][['target_bank', 'share']]
        col_name = f'bartik_{group_prefix}_share_{g}'
        g_shares = g_shares.rename(columns={'share': col_name})
        # 防止多次调用时重复列: 先删除已有列
        if col_name in panel.columns:
            panel = panel.drop(columns=[col_name])
        panel = panel.merge(g_shares, on='target_bank', how='left')
        panel[col_name] = panel[col_name].fillna(0)

    # --- Step 3: 组别×年份 shift (关键: 自身组=LOO, 其他组=FULL) ---
    df_with_group = df_exploded.copy()
    df_with_group['_group'] = df_with_group['target_bank'].map(bank_group_map).fillna('other')

    for track in ['_full', '_ctx']:
        score_col = f'llm_vote_score{track}'
        if score_col not in df_with_group.columns:
            panel[f'bartik_{group_prefix}_iv{track}'] = np.nan
            continue

        # Step 3a: 组×年份 的聚合统计 (文章级)
        group_year_stats = (df_with_group[df_with_group['_group'].isin(groups)]
                           .groupby(['_group', 'year'])[score_col]
                           .agg(['sum', 'count'])
                           .reset_index())

        # Step 3b: 银行×组×年份 的贡献量 (用于 LOO 减除)
        bank_group_contrib = (df_with_group[df_with_group['_group'].isin(groups)]
                             .groupby(['target_bank', '_group', 'year'])[score_col]
                             .agg(['sum', 'count'])
                             .reset_index()
                             .rename(columns={'sum': '_bi_sum', 'count': '_bi_cnt'}))

        # Step 3c: 为每个 (bank, year) 构建各组 shift
        all_banks_df = panel[['target_bank', 'year']].drop_duplicates()

        for g in groups:
            # 组 g 的年度聚合
            g_stats = group_year_stats[group_year_stats['_group'] == g][['year', 'sum', 'count']]
            g_stats = g_stats.rename(columns={'sum': f'_sum_{g}', 'count': f'_cnt_{g}'})
            all_banks_df = all_banks_df.merge(g_stats, on='year', how='left')

            # 银行 i 在组 g 中的贡献 (仅当 bank i ∈ g 时有值)
            bi_g = bank_group_contrib[bank_group_contrib['_group'] == g][
                ['target_bank', 'year', '_bi_sum', '_bi_cnt']]
            bi_g = bi_g.rename(columns={'_bi_sum': f'_bi_sum_{g}', '_bi_cnt': f'_bi_cnt_{g}'})
            all_banks_df = all_banks_df.merge(bi_g, on=['target_bank', 'year'], how='left')
            all_banks_df[f'_bi_sum_{g}'] = all_banks_df[f'_bi_sum_{g}'].fillna(0)
            all_banks_df[f'_bi_cnt_{g}'] = all_banks_df[f'_bi_cnt_{g}'].fillna(0)

            # LOO: (组总和 - 银行贡献) / (组计数 - 银行计数)
            remain_sum = all_banks_df[f'_sum_{g}'] - all_banks_df[f'_bi_sum_{g}']
            remain_cnt = all_banks_df[f'_cnt_{g}'] - all_banks_df[f'_bi_cnt_{g}']
            all_banks_df[f'shift_{g}'] = np.where(
                remain_cnt > 0,
                remain_sum / remain_cnt,
                np.nan  # 组内仅有自己 → 无法 LOO
            )

        # --- Step 4: BIV = Σ share × shift (merge-based) ---
        share_cols = [f'bartik_{group_prefix}_share_{g}' for g in groups]
        biv = panel[['target_bank', 'year'] + share_cols].copy()
        shift_cols_needed = [f'shift_{g}' for g in groups]
        biv = biv.merge(
            all_banks_df[['target_bank', 'year'] + shift_cols_needed],
            on=['target_bank', 'year'], how='left')

        biv_val = pd.Series(0.0, index=biv.index)
        for g in groups:
            share_col = f'bartik_{group_prefix}_share_{g}'
            shift_col = f'shift_{g}'
            if shift_col in biv.columns:
                # NaN shift → 0: 当某组在该年份无 LOO 可计算时
                # (组内仅剩自身银行), 视该维度暴露为零
                # 学术合理性: 等价于 exclusion restriction (该维度无外生冲击)
                biv_val += biv[share_col].fillna(0) * biv[shift_col].fillna(0)

        # 通过 target_bank+year 对齐回 panel，确保行序安全
        biv_result = biv[['target_bank', 'year']].copy()
        biv_result[f'bartik_{group_prefix}_iv{track}'] = biv_val.values
        # 先删除已有列(若存在)再 merge
        iv_col = f'bartik_{group_prefix}_iv{track}'
        if iv_col in panel.columns:
            panel = panel.drop(columns=[iv_col])
        panel = panel.merge(biv_result[['target_bank', 'year', iv_col]],
                            on=['target_bank', 'year'], how='left')

    # 诊断
    group_dist = panel.drop_duplicates('target_bank')[f'bank_{group_prefix}'].value_counts()
    logger.info(f"  分组分布: {dict(group_dist)}")

    return panel


# ============================================================================
# 2d. 文章属性维度 Bartik IV (基于文章自身分类列, 而非 co_mentioned_banks)
#     适用于 fintech_category, _media_type, _half_year 等维度
# ============================================================================

def compute_bartik_iv_fintech(panel: pd.DataFrame,
                              df_exploded: pd.DataFrame,
                              category_map: dict,
                              group_prefix: str,
                              base_year: int = None,
                              category_col: str = 'fintech_category') -> pd.DataFrame:
    """文章属性维度 Bartik IV (基于文章自身分类列, 而非 co_mentioned_banks)。

    通用接口: 可接受任意文章级分类列 (fintech_category, _media_type,
    _half_year, _doclen_type 等), 将文章按 category_col 分组后计算
    Bartik Shift-Share IV。

    share_{i,k,T0} = 银行 i 在基期文章中, category_col=k 的占比
    shift_{k,t}    = 类别 k 中其他银行的 leave-one-out 年度情感均值
    """
    T0 = base_year if base_year is not None else panel['year'].min()
    # 修正5: 排除兜底类别 'other', 与 compute_bartik_iv 保持一致
    groups = sorted(set(v for v in category_map.values() if v != 'other'))

    # Step 1: 基期份额 (直接从文章的分类列计算)
    base = df_exploded[df_exploded['year'] == T0].copy()
    base['_cat_short'] = base[category_col].map(category_map)

    shares = (base.groupby(['target_bank', '_cat_short']).size()
              .unstack(fill_value=0))
    total = shares.sum(axis=1).replace(0, np.nan)
    shares = shares.div(total, axis=0).fillna(0)

    for g in groups:
        col_name = f'bartik_{group_prefix}_share_{g}'
        if g in shares.columns:
            panel[col_name] = panel['target_bank'].map(shares[g]).fillna(0)
        else:
            panel[col_name] = 0.0

    # Step 2: shift (用 bank×category×year 的贡献做 LOO 减除)
    df_cat = df_exploded.copy()
    df_cat['_cat_short'] = df_cat[category_col].map(category_map)

    for track in ['_full', '_ctx']:
        score_col = f'llm_vote_score{track}'
        if score_col not in df_cat.columns:
            panel[f'bartik_{group_prefix}_iv{track}'] = np.nan
            continue

        # 类别×年份 聚合
        gys = (df_cat[df_cat['_cat_short'].isin(groups)]
               .groupby(['_cat_short', 'year'])[score_col]
               .agg(['sum', 'count']).reset_index())

        # 银行×类别×年份 的贡献量
        bgc = (df_cat[df_cat['_cat_short'].isin(groups)]
               .groupby(['target_bank', '_cat_short', 'year'])[score_col]
               .agg(['sum', 'count']).reset_index()
               .rename(columns={'sum': '_bi_sum', 'count': '_bi_cnt'}))

        abd = panel[['target_bank', 'year']].drop_duplicates()

        for g in groups:
            gs = gys[gys['_cat_short'] == g][['year', 'sum', 'count']]
            gs = gs.rename(columns={'sum': f'_sum_{g}', 'count': f'_cnt_{g}'})
            abd = abd.merge(gs, on='year', how='left')

            bi_g = bgc[bgc['_cat_short'] == g][['target_bank', 'year', '_bi_sum', '_bi_cnt']]
            bi_g = bi_g.rename(columns={'_bi_sum': f'_bi_sum_{g}', '_bi_cnt': f'_bi_cnt_{g}'})
            abd = abd.merge(bi_g, on=['target_bank', 'year'], how='left')
            abd[f'_bi_sum_{g}'] = abd[f'_bi_sum_{g}'].fillna(0)
            abd[f'_bi_cnt_{g}'] = abd[f'_bi_cnt_{g}'].fillna(0)

            remain_sum = abd[f'_sum_{g}'] - abd[f'_bi_sum_{g}']
            remain_cnt = abd[f'_cnt_{g}'] - abd[f'_bi_cnt_{g}']
            abd[f'shift_{g}'] = np.where(
                remain_cnt > 0,
                remain_sum / remain_cnt,
                np.nan
            )

        # BIV = Σ share × shift
        biv = panel[['target_bank', 'year']].copy()
        for g in groups:
            biv[f's_{g}'] = panel[f'bartik_{group_prefix}_share_{g}']
        biv = biv.merge(
            abd[['target_bank', 'year'] + [f'shift_{g}' for g in groups]],
            on=['target_bank', 'year'], how='left')
        biv_val = sum(biv[f's_{g}'].fillna(0) * biv[f'shift_{g}'].fillna(0) for g in groups)
        # 通过 target_bank+year 对齐回 panel，确保行序安全
        biv_result = biv[['target_bank', 'year']].copy()
        biv_result[f'bartik_{group_prefix}_iv{track}'] = biv_val.values
        iv_col = f'bartik_{group_prefix}_iv{track}'
        if iv_col in panel.columns:
            panel = panel.drop(columns=[iv_col])
        panel = panel.merge(biv_result[['target_bank', 'year', iv_col]],
                            on=['target_bank', 'year'], how='left')

    # 诊断日志
    for track in ['_full', '_ctx']:
        iv_col = f'bartik_{group_prefix}_iv{track}'
        if iv_col in panel.columns:
            n_valid = panel[iv_col].notna().sum()
            iv_mean = panel[iv_col].mean()
            iv_std = panel[iv_col].std()
            logger.info(f"  [{group_prefix}] {iv_col}: "
                        f"{n_valid}/{len(panel)} 有效, "
                        f"mean={iv_mean:.4f}, std={iv_std:.4f}")

    return panel

# ============================================================================
# 2e. 经济圈 Leave-One-Out IV
# ============================================================================

PROVINCE_TO_ZONE = {
    '北京': '京津冀', '天津': '京津冀', '河北': '京津冀',
    '上海': '长三角', '江苏': '长三角', '浙江': '长三角', '安徽': '长三角',
    '广东': '珠三角',
    '四川': '成渝', '重庆': '成渝',
    '辽宁': '东北', '吉林': '东北', '黑龙江': '东北',
    '湖北': '中部', '湖南': '中部', '江西': '中部', '山西': '中部', '河南': '中部',
    '陕西': '西北', '甘肃': '西北', '青海': '西北', '宁夏': '西北', '新疆': '西北',
    '云南': '西南', '贵州': '西南', '广西': '西南', '西藏': '西南',
    '福建': '东南', '海南': '东南',
    '山东': '环渤海', '内蒙古': '环渤海',
}


def compute_zone_leave1out(panel: pd.DataFrame,
                          df_exploded: pd.DataFrame,
                          min_group_size: int = 3) -> pd.DataFrame:
    """经济圈维度 Leave-One-Out 情感均值，作为省级 LOO 的补充 IV。

    与省级 LOO 的区别:
        - 省级 LOO: 同省内其他银行 → 粒度细，但省内银行数可能太少
        - 经济圈 LOO: 同经济圈(跨省)内其他银行 → 样本更充足，捕捉区域共同冲击

    输出列:
        zone_leave1out_tone_full / zone_leave1out_tone_ctx
        bank_zone (银行所属经济圈标签)
    """
    # Step 1: 为面板加上经济圈标签
    panel['bank_zone'] = panel['bank_province'].map(PROVINCE_TO_ZONE).fillna('other')

    # Step 2: 文章级数据也打上经济圈标签 (通过 target_bank merge)
    bank_zone_map = panel.drop_duplicates('target_bank').set_index('target_bank')['bank_zone']
    df_z = df_exploded.copy()
    df_z['_zone'] = df_z['target_bank'].map(bank_zone_map).fillna('other')

    for track in ['_full', '_ctx']:
        score_col = f'llm_vote_score{track}'
        out_col = f'zone_leave1out_tone{track}'
        if score_col not in df_z.columns:
            panel[out_col] = np.nan
            continue

        # 经济圈×年份 聚合
        zone_agg = (df_z.groupby(['_zone', 'year'])[score_col]
                    .agg(['sum', 'count']).reset_index())

        # 银行×经济圈×年份 的贡献量
        bank_agg = (df_z.groupby(['target_bank', '_zone', 'year'])[score_col]
                    .agg(['sum', 'count']).reset_index()
                    .rename(columns={'sum': '_bi_sum', 'count': '_bi_cnt'}))

        # merge: 面板 ← 经济圈聚合 ← 银行贡献
        tmp = panel[['target_bank', 'year', 'bank_zone']].drop_duplicates()
        tmp = tmp.merge(zone_agg, left_on=['bank_zone', 'year'],
                        right_on=['_zone', 'year'], how='left')
        tmp = tmp.merge(bank_agg[['target_bank', 'year', '_bi_sum', '_bi_cnt']],
                        on=['target_bank', 'year'], how='left')
        tmp['_bi_sum'] = tmp['_bi_sum'].fillna(0)
        tmp['_bi_cnt'] = tmp['_bi_cnt'].fillna(0)

        # LOO: (经济圈总和 - 自身贡献) / (经济圈计数 - 自身计数)
        remain_sum = tmp['sum'] - tmp['_bi_sum']
        remain_cnt = tmp['count'] - tmp['_bi_cnt']
        tmp[out_col] = np.where(
            remain_cnt >= min_group_size,  # 组内(排除自身后)至少3篇文章
            remain_sum / remain_cnt,
            np.nan
        )
        panel = panel.merge(tmp[['target_bank', 'year', out_col]],
                            on=['target_bank', 'year'], how='left')

    # 诊断
    zone_dist = panel.drop_duplicates('target_bank')['bank_zone'].value_counts()
    logger.info(f"  经济圈分布: {dict(zone_dist)}")
    for track in ['_full', '_ctx']:
        out_col = f'zone_leave1out_tone{track}'
        if out_col in panel.columns:
            n_valid = panel[out_col].notna().sum()
            logger.info(f"  {out_col}: {n_valid}/{len(panel)} 有效 ({n_valid/len(panel)*100:.1f}%)")

    return panel

# ============================================================================
# 2f. DID 政策冲击变量合并
#     学术依据: Callaway & Sant'Anna (2021, JoE)
#     DOI: 10.1016/j.jeconom.2020.12.001
# ============================================================================

def merge_policy_shocks(panel: pd.DataFrame) -> pd.DataFrame:
    """合并政策冲击 DID 变量（仅年份维度，不区分波次/月份）。

    设计思路:
        面板为 Bank-Year 年度频率，因此政策冲击只需定位到"年份"即可。
        同一年内若有多批次（如 DCEP 2022年3月第三批 + 12月第四批），
        统一视为该年处理。

    对每个政策(dcep / sandbox)生成 3 个变量:
        {prefix}_treated:    处理组哑变量 (0/1)
        {prefix}_post:       政策后哑变量 (0/1)
        {prefix}_treat_year: 首次被处理的年份 (0=控制组, 用于交错DID的 gvar)

    匹配规则（按优先级从高到低）:
        1. cities:         按 bank_city 精确匹配
        2. full_province:  按 bank_province 匹配整个省份的全部银行
        3. new_cities:     按 bank_city 匹配零散新增城市
        先入为主: 一旦银行已被某年份匹配, 后续年份不再覆盖。
    """
    shock_path = os.path.join(os.path.dirname(__file__), 'config', 'policy_shocks.json')
    if not os.path.exists(shock_path):
        logger.warning("  policy_shocks.json 不存在, 跳过 DID 变量")
        return panel

    with open(shock_path, 'r', encoding='utf-8') as f:
        shocks = json.load(f)

    # 城市名别名映射 (雄安新区行政上属保定市)
    CITY_ALIASES = {
        '雄安': ['雄安', '保定'],
    }

    for policy_name, cfg in shocks.items():
        if policy_name.startswith('_'):
            continue
        prefix = cfg['prefix']

        # 前置校验: bank_city 是 DID 匹配的必要列
        if 'bank_city' not in panel.columns:
            logger.warning(f"  bank_city 列不存在, 跳过 {policy_name} DID 匹配"
                           " (请确保 merge_bank_geography 已在前序步骤中执行)")
            continue

        panel[f'{prefix}_treat_year'] = 0
        panel_city = panel['bank_city'].fillna('').str.rstrip('市')

        for group in cfg['groups']:
            treat_year = group['year']

            # (a) 城市级匹配
            if 'cities' in group:
                for city in group['cities']:
                    city_clean = city.rstrip('市')
                    aliases = CITY_ALIASES.get(city_clean, [city_clean])
                    for alias in aliases:
                        mask = (panel_city == alias) & (panel[f'{prefix}_treat_year'] == 0)
                        panel.loc[mask, f'{prefix}_treat_year'] = treat_year

            # (b) 省级匹配
            if 'full_province' in group and 'bank_province' in panel.columns:
                provs = set(group['full_province'])
                mask = (panel['bank_province'].isin(provs)
                        & (panel[f'{prefix}_treat_year'] == 0))
                panel.loc[mask, f'{prefix}_treat_year'] = treat_year

            # (c) 零散新增城市
            if 'new_cities' in group:
                new_city_set = set(c.rstrip('市') for c in group['new_cities'])
                if '西双版纳' in new_city_set:
                    new_city_set.add('景洪')
                mask = (panel_city.isin(new_city_set)
                        & (panel[f'{prefix}_treat_year'] == 0))
                panel.loc[mask, f'{prefix}_treat_year'] = treat_year

        # 生成最终 DID 变量
        panel[f'{prefix}_treated'] = (panel[f'{prefix}_treat_year'] > 0).astype(int)
        panel[f'{prefix}_post'] = np.where(
            panel[f'{prefix}_treat_year'] > 0,
            (panel['year'] >= panel[f'{prefix}_treat_year']).astype(int),
            0
        )

        # 诊断日志
        n_treated = panel.loc[panel[f'{prefix}_treated'] == 1, 'target_bank'].nunique()
        n_control = panel.loc[panel[f'{prefix}_treated'] == 0, 'target_bank'].nunique()
        year_dist = (panel.drop_duplicates('target_bank')
                     .groupby(f'{prefix}_treat_year')['target_bank'].count()
                     .to_dict())
        logger.info(f"  {policy_name}: 处理组 {n_treated} 家, "
                    f"控制组 {n_control} 家, 年份分布 {year_dist}")

    return panel
