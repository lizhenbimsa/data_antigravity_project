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

识别设计披露 (metric-audit 2026-06-02, 论文须如实声明, 勿过度宣称):
  1. **shift 是内生 LOO 情感均值, 非准随机外生冲击**: compute_bartik_iv 的
     shift_g = 组 g 内其他银行的 leave-one-out 年度 llm_vote_score 均值
     (L210-218), 与被解释变量(本行情感/绩效)同源、存在 Manski(1993) 反射与共同
     冲击. 故识别**仅依赖 GPSS(2020) "基期 share 外生性"视角**, **不**满足
     Borusyak-Hull-Jaravel(2022) "shift 准随机"视角 — 论文勿主张双重识别;
     诊断走 Rotemberg(share)而非 shift 平衡性. (本模块各函数注释中对 BHJ 的引用
     仅作对比, 非声称满足其前提.)
  2. **diagnose_rotemberg_weights 是近似, 非 GPSS α_k**: 用 Cov(share,BIV)/
     Var(BIV) 的单变量 OLS 投影代替真正的两阶段 Rotemberg 分解; 其"负权重/HHI"
     仅作快速集中度提示, **正式论文的 Rotemberg 权重须走 Stata bartik_weight 包**
     (函数内已给命令), 不得以本近似冒充 GPSS §5 诊断.
  3. **T=2 面板结构退化**: 当前面板仅 2017-2018 (84 banks × 2y). Bartik share
     在 64%(112/176) bank-year 退化为 own-type one-hot (基期 co-mention 跨组为
     0 → L137-143 兜底 share=1.0), fintech 基期类别 96.7% app vs 3.3% tech →
     工具近共线于 bank-type FE、一阶段 F 弱; DiD(dcep/sandbox) 处理年份均 ≥2019
     (晚于面板末年 2018) 致 _post 恒 0、不可识别 (fix(ivdid-stata-01): 原文误写
     "≤2018", 归因方向倒置, 实为处理年份晚于样本期末). 论文须报告一阶段有效 N/F、
     披露退化并相应降权这些 spec.
"""

import json
import os

import numpy as np
import pandas as pd

# Phase 2a: 取代旧的 importlib.spec_from_file_location 反射,改为正规子包 import。
from news_process.pipeline.panel.encode import CONFIG, logger

# ============================================================================
# 2b. 银行分组映射加载 (Bartik IV 前置依赖)
# ============================================================================

def load_bank_group_maps() -> tuple:
    """从 bank_addresses.json 读取银行分组映射。

    Returns:
        type_map:  {银行名 → 'soe'/'joint'/'city'/'rural'/'private'/'foreign'/'other'}
        scale_map: {银行名 → 'L'/'M'/'S'/'XS'/'other'}
    """
    # Phase 1 重构: 优先读取 CONFIG['paths']['bank_addresses_file']。
    addr_path = CONFIG['paths'].get(
        'bank_addresses_file',
        os.path.join(os.path.dirname(__file__), 'config', 'bank_addresses.json'),
    )
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
    panel = panel.copy()

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
    df_with_group = pd.concat(
        [
            df_exploded.copy(),
            pd.DataFrame({
                '_group': df_exploded['target_bank'].map(bank_group_map).fillna('other')
            }, index=df_exploded.index),
        ],
        axis=1,
    ).copy()

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
            # v6/F2: groupby.sum() over nullable Int8 returns Int64 nullable → 转 float 再走 np.where
            remain_sum = (all_banks_df[f'_sum_{g}'] - all_banks_df[f'_bi_sum_{g}']).astype('float64')
            remain_cnt = (all_banks_df[f'_cnt_{g}'] - all_banks_df[f'_bi_cnt_{g}']).astype('float64')
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
#     适用于 innovation_locus, _media_type, _half_year 等维度
# ============================================================================

def compute_bartik_iv_fintech(panel: pd.DataFrame,
                              df_exploded: pd.DataFrame,
                              category_map: dict,
                              group_prefix: str,
                              base_year: int = None,
                              category_col: str = 'innovation_locus') -> pd.DataFrame:
    """文章属性维度 Bartik IV (基于文章自身分类列, 而非 co_mentioned_banks)。

    通用接口: 可接受任意文章级分类列 (innovation_locus, _media_type,
    _half_year, _doclen_type 等), 将文章按 category_col 分组后计算
    Bartik Shift-Share IV。

    share_{i,k,T0} = 银行 i 在基期文章中, category_col=k 的占比
    shift_{k,t}    = 类别 k 中其他银行的 leave-one-out 年度情感均值
    """
    T0 = base_year if base_year is not None else panel['year'].min()
    # 修正5: 排除兜底类别 'other', 与 compute_bartik_iv 保持一致
    groups = sorted(set(v for v in category_map.values() if v != 'other'))
    panel = panel.copy()

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
    df_cat = pd.concat(
        [
            df_exploded.copy(),
            pd.DataFrame({
                '_cat_short': df_exploded[category_col].map(category_map)
            }, index=df_exploded.index),
        ],
        axis=1,
    ).copy()

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

            # v6/F2: nullable Int8 → float 兼容 np.where
            remain_sum = (abd[f'_sum_{g}'] - abd[f'_bi_sum_{g}']).astype('float64')
            remain_cnt = (abd[f'_cnt_{g}'] - abd[f'_bi_cnt_{g}']).astype('float64')
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
    bank_zone = panel['bank_province'].map(PROVINCE_TO_ZONE).fillna('other')
    panel = pd.concat(
        [panel.copy(), pd.DataFrame({'bank_zone': bank_zone}, index=panel.index)],
        axis=1,
    ).copy()

    # Step 2: 文章级数据也打上经济圈标签 (通过 target_bank merge)
    bank_zone_map = panel.drop_duplicates('target_bank').set_index('target_bank')['bank_zone']
    df_z = pd.concat(
        [
            df_exploded.copy(),
            pd.DataFrame({
                '_zone': df_exploded['target_bank'].map(bank_zone_map).fillna('other')
            }, index=df_exploded.index),
        ],
        axis=1,
    ).copy()

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
        # v6/F2: nullable Int8 → float 兼容 np.where
        remain_sum = (tmp['sum'] - tmp['_bi_sum']).astype('float64')
        remain_cnt = (tmp['count'] - tmp['_bi_cnt']).astype('float64')
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
    # Phase 1 重构: 优先读取 CONFIG['paths']['policy_shocks_file']。
    shock_path = CONFIG['paths'].get(
        'policy_shocks_file',
        os.path.join(os.path.dirname(__file__), 'config', 'policy_shocks.json'),
    )
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

        # fix(ivdid-01): T=2 面板 + 处理年份均 ≥2019 (晚于面板末年) → _post 恒 0,
        # DiD/event-study 在当前 corpus 上结构性不可识别。fail-loud 披露, 提醒下游
        # 回归勿在 post≡0 spec 上估计 ATT (production T≥3 面板下自然恢复可识别)。
        if not (panel[f'{prefix}_post'] == 1).any():
            logger.warning(
                f"  [DiD 不可识别] {prefix}_post 全为 0 — 处理年份均晚于面板末年 "
                f"{int(panel['year'].max())}; 下游勿在此 spec 上估计 ATT")

        # ── G-01: Event Study 动态效应支持 ──
        # 学术依据: Callaway & Sant'Anna (2021, JoE), Sun & Abraham (2021, JoE)
        # relative_year = year - treat_year (控制组设为 NaN，Stata 中自动排除)
        # 用于:
        #   1. Event Study Plot: 逐期 ATT 估计
        #   2. 平行趋势检验: relative_year < 0 的系数应不显著
        #   3. 动态效应: relative_year >= 0 的系数变化趋势
        panel[f'{prefix}_rel_year'] = np.where(
            panel[f'{prefix}_treat_year'] > 0,
            panel['year'] - panel[f'{prefix}_treat_year'],
            np.nan  # 控制组: NaN, Stata 中作为 never-treated baseline
        )

        # 生成 Event Study lead/lag 虚拟变量 (k = -3 到 +3, 以 k=-1 为基期)
        # 设计: 覆盖 pre-treatment 3 期 + post-treatment 3 期
        #   Stata 用法:
        #     * 方法一 (csdid): csdid Y X, ivar(bank_id) time(year) gvar({prefix}_treat_year)
        #     * 方法二 (手动): reghdfe Y {prefix}_lead3 ... {prefix}_lag3 X, absorb(bank_id year)
        for k in range(-3, 4):
            if k == -1:
                continue  # k=-1 为基期 (omitted)
            col_name = f'{prefix}_lag{k}' if k >= 0 else f'{prefix}_lead{abs(k)}'
            panel[col_name] = np.where(
                panel[f'{prefix}_rel_year'] == k,
                1, 0
            ).astype(int)
            # 控制组的 lead/lag 全为 0 (因为 rel_year 是 NaN, == k 为 False)

        # Endpoint binning: k <= -4 合并为 lead4plus, k >= 4 合并为 lag4plus
        panel[f'{prefix}_lead4plus'] = np.where(
            panel[f'{prefix}_rel_year'].fillna(0) <= -4,
            (panel[f'{prefix}_treat_year'] > 0).astype(int),
            0
        ).astype(int)
        panel[f'{prefix}_lag4plus'] = np.where(
            panel[f'{prefix}_rel_year'].fillna(0) >= 4,
            (panel[f'{prefix}_treat_year'] > 0).astype(int),
            0
        ).astype(int)

        # 诊断日志
        n_treated = panel.loc[panel[f'{prefix}_treated'] == 1, 'target_bank'].nunique()
        n_control = panel.loc[panel[f'{prefix}_treated'] == 0, 'target_bank'].nunique()
        year_dist = (panel.drop_duplicates('target_bank')
                     .groupby(f'{prefix}_treat_year')['target_bank'].count()
                     .to_dict())
        logger.info(f"  {policy_name}: 处理组 {n_treated} 家, "
                    f"控制组 {n_control} 家, 年份分布 {year_dist}")

        # Event Study 诊断
        if panel[f'{prefix}_rel_year'].notna().any():
            rel_year_dist = panel.loc[
                panel[f'{prefix}_rel_year'].notna(),
                f'{prefix}_rel_year'
            ].value_counts().sort_index().to_dict()
            logger.info(f"  {policy_name} Event Study relative_year 分布: "
                        f"{rel_year_dist}")
            logger.info(f"  {policy_name} Stata Event Study 命令:")
            logger.info(f"    * csdid Y X, ivar(bank_id) time(year) "
                        f"gvar({prefix}_treat_year)")
            logger.info(f"    * estat event  // 绘制 Event Study Plot")
            logger.info(f"    * estat pretrend  // 平行趋势检验")

    # ── G-05: 多政策处理组正交性诊断 ──
    # 学术依据: Callaway & Sant'Anna (2021, JoE, §6.1):
    #   当面板中存在多个政策冲击时, 需检验处理组是否高度重叠 (overlapping treatments)。
    #   若重叠过高, DiD 估计量可能混淆多个政策效应, 导致因果识别失效。
    policy_prefixes = [cfg['prefix'] for name, cfg in shocks.items()
                       if not name.startswith('_')
                       and f"{cfg['prefix']}_treated" in panel.columns]
    if len(policy_prefixes) >= 2:
        logger.info("=" * 60)
        logger.info("G-05: 多政策处理组正交性诊断")
        logger.info("  对标: DID 标准假设 — 处理组交叉独立性")
        logger.info("=" * 60)

        from itertools import combinations
        for p1, p2 in combinations(policy_prefixes, 2):
            t1 = panel[f'{p1}_treated']
            t2 = panel[f'{p2}_treated']
            crosstab = pd.crosstab(t1, t2, margins=True)
            logger.info(f"  {p1} × {p2} 交叉表:")
            for idx in crosstab.index:
                logger.info(f"    {p1}={idx}: {dict(crosstab.loc[idx])}")

            # 计算 Cramér's V (关联强度)
            n_obs = t1.notna().sum()
            chi2 = 0
            for v1 in [0, 1]:
                for v2 in [0, 1]:
                    obs = ((t1 == v1) & (t2 == v2)).sum()
                    exp = ((t1 == v1).sum() * (t2 == v2).sum()) / max(n_obs, 1)
                    if exp > 0:
                        chi2 += (obs - exp) ** 2 / exp
            cramers_v = (chi2 / max(n_obs, 1)) ** 0.5
            logger.info(f"  Cramér's V = {cramers_v:.4f}"
                        f" {'✓ < 0.3 弱相关' if cramers_v < 0.3 else '≥ 0.3 中强相关'}")
            if cramers_v >= 0.3:
                logger.info(f"  → 建议: 在论文中讨论 {p1} 与 {p2} 的处理组重叠问题,")
                logger.info(f"    或在稳健性检验中单独估计各政策效应")

    return panel


# ============================================================================
# G-03: Rotemberg 权重诊断
# ============================================================================
# 学术依据:
#   Goldsmith-Pinkham, Sorkin & Swift (2020, AER, §5):
#     "The Rotemberg weights α_k decompose the just-identified Bartik
#      estimator into a weighted sum of group-specific estimators.
#      Negative weights indicate potential misspecification."
#   DOI: 10.1257/aer.20181047
#
#   Borusyak, Hull & Jaravel (2022, RES, §4.2):
#     "Under the shift-share interpretation, one should verify that
#      no single industry (share) dominates the variation."
#   DOI: 10.1093/restud/rdab030
# ============================================================================

def diagnose_rotemberg_weights(panel: pd.DataFrame,
                                group_prefix: str,
                                groups: list = None,
                                logger_inst=None) -> dict:
    """计算 Bartik IV 的 Rotemberg (1983) 权重分解。

    Rotemberg 权重 α_k 衡量每个 share 维度 k 对整体 Bartik IV 的贡献。
    诊断目标:
      1. 识别 α_k < 0 的"负权重"维度 (Goldsmith-Pinkham 2020 §5 核心检验)
      2. 识别贡献集中度 (HHI of α_k): HHI > 0.25 表示少数维度主导
      3. 报告前 5 大权重维度及其基期份额均值

    参数:
        panel:        Bank-Year 面板
        group_prefix: Bartik IV 系列前缀 (如 'type', 'scale', 'ft_cat')
        groups:       组别列表 (None 时从面板 share 列推断)
        logger_inst:  日志实例 (None 时使用模块级 logger)

    返回:
        dict: {
          'weights': {group_k: alpha_k, ...},
          'hhi': float,
          'n_negative': int,
          'top5': [(group, weight), ...],
          'share_means': {group_k: mean_share, ...},
        }
    """
    lg = logger_inst or logger

    lg.info("=" * 60)
    lg.info(f"G-03: Rotemberg 权重诊断 [{group_prefix}]")
    lg.info("  对标: Goldsmith-Pinkham et al. (2020, AER, §5, Table 3)")
    lg.info("=" * 60)

    # 推断组别列表
    if groups is None:
        share_cols = [c for c in panel.columns
                      if c.startswith(f'bartik_{group_prefix}_share_')]
        groups = [c.replace(f'bartik_{group_prefix}_share_', '')
                  for c in share_cols]
    if not groups:
        lg.warning(f"  未找到 bartik_{group_prefix}_share_* 列，跳过诊断")
        return {}

    # --- 计算近似 Rotemberg 权重 ---
    # α_k ≈ Cov(share_k, BIV) / Var(BIV)
    # 这是 Rotemberg (1983) 权重的 OLS 分解近似
    iv_col = f'bartik_{group_prefix}_iv_full'
    if iv_col not in panel.columns:
        lg.warning(f"  {iv_col} 不存在，跳过诊断")
        return {}

    biv = panel[iv_col].dropna()
    if biv.var() == 0 or len(biv) < 10:
        lg.warning(f"  {iv_col} 方差为 0 或样本太小，跳过诊断")
        return {}

    var_biv = biv.var()
    weights = {}
    share_means = {}
    for g in groups:
        share_col = f'bartik_{group_prefix}_share_{g}'
        if share_col not in panel.columns:
            continue
        valid = panel[[share_col, iv_col]].dropna()
        if len(valid) < 10:
            continue
        cov = valid[share_col].cov(valid[iv_col])
        alpha_k = cov / var_biv
        weights[g] = round(alpha_k, 6)
        share_means[g] = round(valid[share_col].mean(), 4)

    if not weights:
        lg.warning("  无法计算权重，跳过")
        return {}

    # --- 诊断指标 ---
    # (1) 负权重检查
    n_negative = sum(1 for v in weights.values() if v < 0)
    neg_groups = [g for g, v in weights.items() if v < 0]

    # (2) HHI 集中度 (α_k 归一化后的 Herfindahl)
    total_abs = sum(abs(v) for v in weights.values())
    if total_abs > 0:
        hhi = sum((abs(v) / total_abs) ** 2 for v in weights.values())
    else:
        hhi = 0.0

    # (3) Top-5 排序
    top5 = sorted(weights.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

    # --- 日志输出 ---
    lg.info(f"  ── Rotemberg 权重 α_k (共 {len(weights)} 个维度) ──")
    for g, alpha in sorted(weights.items(), key=lambda x: -abs(x[1])):
        flag = " NEGATIVE" if alpha < 0 else ""
        lg.info(f"    {g:>15s}: α = {alpha:+.6f}, "
                f"E[share] = {share_means.get(g, 0):.4f}{flag}")

    lg.info(f"  ── 诊断汇总 ──")
    lg.info(f"    负权重维度: {n_negative}/{len(weights)}"
            f"{' → ' + str(neg_groups) if neg_groups else ''}")
    if n_negative > 0:
        lg.info(f"    负权重提示可能的排他性约束违背 "
                f"(Goldsmith-Pinkham 2020, AER §5.2)")
        lg.info(f"    → 建议: 在论文稳健性检验中移除负权重维度后重新估计")
    lg.info(f"    HHI(|α|) = {hhi:.4f}"
            f" {'✓ < 0.25 分散' if hhi < 0.25 else '≥ 0.25 集中'}")
    lg.info(f"    Top-5 权重维度: "
            f"{[(g, f'{a:+.4f}') for g, a in top5]}")

    # Stata 命令建议
    lg.info(f"  ── Stata 验证命令 ──")
    lg.info(f"    * 使用 bartik_weight 包 (Goldsmith-Pinkham 2020 官方):")
    lg.info(f"      ssc install bartik_weight")
    lg.info(f"      bartik_weight Y bartik_{group_prefix}_iv_full "
            f"{' '.join(f'bartik_{group_prefix}_share_{g}' for g in groups[:5])}, "
            f"absorb(target_bank year)")

    result = {
        'weights': weights,
        'hhi': round(hhi, 6),
        'n_negative': n_negative,
        'negative_groups': neg_groups,
        'top5': top5,
        'share_means': share_means,
    }
    return result
